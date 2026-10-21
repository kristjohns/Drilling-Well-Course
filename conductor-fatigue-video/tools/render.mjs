// Deterministic frame renderer: Playwright (Chromium, SwiftShader WebGL) -> ffmpeg, in parallel chunks.
//   node tools/render.mjs                         full video, 3 workers, 1920x1080 @ 30 fps
//   node tools/render.mjs --from 100 --to 110     only a time range (for tests)
//   node tools/render.mjs --workers 3 --chunk 450 --crf 14 --format jpeg --quality 95
// Output: build/render/seg_XXXXXX.mp4 (+ .done markers, so an interrupted render resumes) and
//         build/render/video.mp4 (silent, concatenated). Timing per chunk goes to build/render/log.txt.
import fs from 'node:fs';
import path from 'node:path';
import { spawn, execFileSync } from 'node:child_process';
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { startServer } from './server.mjs';

const args = process.argv.slice(2);
const opt = { workers: 3, fps: 30, chunk: 450, crf: 14, preset: 'veryfast', format: 'jpeg', quality: 95, from: 0, to: 0, out: 'build/render' };
for (let i = 0; i < args.length; i++) {
  if (!args[i].startsWith('--')) continue;
  const k = args[i].slice(2), v = args[i + 1];
  opt[k] = isNaN(Number(v)) ? v : Number(v); i++;
}
fs.mkdirSync(opt.out, { recursive: true });
const LAUNCH = { args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text'] };
const log = (s) => { console.log(s); fs.appendFileSync(path.join(opt.out, 'log.txt'), s + '\n'); };

const { srv, url } = await startServer(0);
const page0 = `${url}/src/index.html?render=1`;
const tl = JSON.parse(fs.readFileSync('src/data/timeline.json', 'utf8'));
const dur = tl.duration;
const t0 = opt.from, t1 = opt.to || dur;
const f0 = Math.round(t0 * opt.fps), f1 = Math.min(Math.round(dur * opt.fps), Math.round(t1 * opt.fps));
const chunks = [];
for (let s = f0; s < f1; s += opt.chunk) chunks.push([s, Math.min(f1, s + opt.chunk)]);
log(`duration ${dur.toFixed(3)} s | frames ${f0}..${f1} (${f1 - f0}) | ${chunks.length} chunks | ${opt.workers} workers | ${opt.format}`);

let next = 0, done = 0, framesDone = 0;
const tStart = Date.now();
const segPath = (i) => path.join(opt.out, `seg_${String(chunks[i][0]).padStart(6, '0')}.mp4`);

async function worker(id) {
  const browser = await chromium.launch(LAUNCH);
  const page = await (await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 })).newPage();
  page.on('pageerror', (e) => log(`[w${id}] pageerror ${e.message}`));
  await page.goto(page0);
  await page.waitForFunction('window.__ready === true || window.__error', null, { timeout: 300000 });
  const err = await page.evaluate('window.__error');
  if (err) throw new Error('BOOT ERROR ' + err);
  const cdp = await page.context().newCDPSession(page);
  for (;;) {
    const ci = next++;
    if (ci >= chunks.length) break;
    const [a, b] = chunks[ci];
    const out = segPath(ci);
    if (fs.existsSync(out + '.done')) { done++; framesDone += b - a; continue; }
    const tc = Date.now();
    const ff = spawn('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(opt.fps), '-vcodec', opt.format === 'png' ? 'png' : 'mjpeg', '-i', 'pipe:0',
      '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-preset', opt.preset, '-crf', String(opt.crf), '-r', String(opt.fps),
      '-g', '60', '-x264-params', 'keyint=60:min-keyint=60:scenecut=0', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', out],
      { stdio: ['pipe', 'inherit', 'inherit'] });
    const exited = new Promise((res) => ff.on('close', res));
    // the first frame of a chunk is seeked twice: some per-shot state is set lazily on the first visit
    await page.evaluate((t) => window.__seek(t), a / opt.fps);
    let img = null, reused = 0;
    const tm = { seek: 0, shot: 0, write: 0 };
    for (let f = a; f < b; f++) {
      let q = Date.now();
      const changed = await page.evaluate((t) => window.__seek(t), f / opt.fps);
      tm.seek += Date.now() - q; q = Date.now();
      if (changed || !img || opt.noreuse) {
        const shot = await cdp.send('Page.captureScreenshot', opt.format === 'png' ? { format: 'png', optimizeForSpeed: true } : { format: 'jpeg', quality: opt.quality, optimizeForSpeed: true });
        img = Buffer.from(shot.data, 'base64');
      } else reused++;
      tm.shot += Date.now() - q; q = Date.now();
      if (!ff.stdin.write(img)) await new Promise((r) => ff.stdin.once('drain', r));
      tm.write += Date.now() - q;
    }
    if (opt.prof) log(`[w${id}] seek ${(tm.seek / 1000).toFixed(1)} s, shot ${(tm.shot / 1000).toFixed(1)} s, write ${(tm.write / 1000).toFixed(1)} s`);
    ff.stdin.end();
    const code = await exited;
    if (code !== 0) throw new Error(`ffmpeg failed for chunk ${ci}`);
    fs.writeFileSync(out + '.done', '');
    done++; framesDone += b - a;
    const el = (Date.now() - tStart) / 1000, sec = (Date.now() - tc) / 1000;
    log(`[w${id}] chunk ${ci + 1}/${chunks.length} t=${(a / opt.fps).toFixed(1)}-${(b / opt.fps).toFixed(1)} s in ${sec.toFixed(0)} s (${((b - a) / sec).toFixed(1)} fps, ${reused} reused) | ${done}/${chunks.length} | elapsed ${(el / 60).toFixed(1)} min`);
  }
  await browser.close();
}

await Promise.all(Array.from({ length: opt.workers }, (_, i) => worker(i)));
srv.close();

const list = chunks.map((_, i) => `file '${path.resolve(segPath(i))}'`).join('\n');
fs.writeFileSync(path.join(opt.out, 'list.txt'), list + '\n');
const name = opt.from || opt.to ? `video_${t0}-${t1}.mp4` : 'video.mp4';
execFileSync('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(opt.out, 'list.txt'), '-c', 'copy', path.join(opt.out, name)], { stdio: 'inherit' });
log(`done in ${((Date.now() - tStart) / 60000).toFixed(1)} min -> ${path.join(opt.out, name)}`);
