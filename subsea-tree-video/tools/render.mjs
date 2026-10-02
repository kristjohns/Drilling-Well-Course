// Deterministic frame renderer: Playwright (Chromium) -> ffmpeg, in parallel chunks.
//   node tools/render.mjs                       full video, 4 workers, 1920x1080 @ 30 fps
//   node tools/render.mjs --from 100 --to 110   only a time range (for tests)
//   node tools/render.mjs --workers 3 --chunk 600 --crf 14 --format png
// Output: build/render/seg_XXXX.mp4 (+ list.txt) and build/render/video.mp4 (silent, concatenated)
import fs from 'node:fs';
import path from 'node:path';
import { spawn, execFileSync } from 'node:child_process';
import os from 'node:os';
import { chromium } from 'playwright';
import { startServer } from './server.mjs';

const args = process.argv.slice(2);
const opt = { workers: Math.max(1, Math.min(4, os.cpus().length)), fps: 30, chunk: 600, crf: 14, preset: 'veryfast', format: 'png', from: 0, to: 0, out: 'build/render', quality: 92, keep: false };
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (!a.startsWith('--')) continue;
  const k = a.slice(2);
  if (k === 'keep') opt.keep = true;
  else opt[k] = isNaN(Number(args[i + 1])) ? args[i + 1] : Number(args[i + 1]), i++;
}
fs.mkdirSync(opt.out, { recursive: true });

const { srv, url } = await startServer(0);
const probe = await chromium.launch();
const pp = await (await probe.newContext({ viewport: { width: 1920, height: 1080 } })).newPage();
await pp.goto(`${url}/src/index.html?render=1`);
await pp.waitForFunction('window.__ready === true || window.__error', null, { timeout: 180000 });
if (await pp.evaluate('window.__error')) { console.error('BOOT ERROR', await pp.evaluate('window.__error')); process.exit(1); }
const dur = await pp.evaluate('window.__duration');
await probe.close();

const t0 = opt.from, t1 = opt.to || dur;
const f0 = Math.round(t0 * opt.fps), f1 = Math.min(Math.round(dur * opt.fps), Math.round(t1 * opt.fps));
const chunks = [];
for (let s = f0; s < f1; s += opt.chunk) chunks.push([s, Math.min(f1, s + opt.chunk)]);
console.log(`duration ${dur.toFixed(3)} s | frames ${f0}..${f1} (${f1 - f0}) | ${chunks.length} chunks | ${opt.workers} workers | ${opt.format}`);

let next = 0, done = 0;
const tStart = Date.now();
const segPath = (i) => path.join(opt.out, `seg_${String(chunks[i][0]).padStart(6, '0')}.mp4`);

async function worker(id) {
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text'] });
  const page = await (await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 })).newPage();
  page.on('pageerror', (e) => console.log(`[w${id}] pageerror`, e.message));
  await page.goto(`${url}/src/index.html?render=1`);
  await page.waitForFunction('window.__ready === true || window.__error', null, { timeout: 180000 });
  const cdp = await page.context().newCDPSession(page);
  for (;;) {
    const ci = next++;
    if (ci >= chunks.length) break;
    const [a, b] = chunks[ci];
    const out = segPath(ci);
    if (fs.existsSync(out + '.done')) { done++; continue; }
    const ff = spawn('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(opt.fps), '-vcodec', opt.format === 'png' ? 'png' : 'mjpeg', '-i', 'pipe:0',
      '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-preset', opt.preset, '-crf', String(opt.crf), '-r', String(opt.fps), '-g', '60', '-x264-params', 'keyint=60:min-keyint=60:scenecut=0', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const exited = new Promise((res) => ff.on('close', res));
    for (let f = a; f < b; f++) {
      await page.evaluate((t) => window.__seek(t), f / opt.fps);
      const shot = await cdp.send('Page.captureScreenshot', opt.format === 'png' ? { format: 'png', optimizeForSpeed: true } : { format: 'jpeg', quality: opt.quality, optimizeForSpeed: true });
      if (!ff.stdin.write(Buffer.from(shot.data, 'base64'))) await new Promise((r) => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
    const code = await exited;
    if (code !== 0) throw new Error(`ffmpeg failed for chunk ${ci}`);
    fs.writeFileSync(out + '.done', '');
    done++;
    const el = (Date.now() - tStart) / 1000;
    const framesDone = chunks.slice(0, 0).length; // eslint-disable-line
    console.log(`[w${id}] chunk ${ci + 1}/${chunks.length} (${a}-${b}) done | ${done}/${chunks.length} | elapsed ${(el / 60).toFixed(1)} min`);
  }
  await browser.close();
}

await Promise.all(Array.from({ length: opt.workers }, (_, i) => worker(i)));
srv.close();

// concatenate the segments
const list = chunks.map((_, i) => `file '${path.resolve(segPath(i))}'`).join('\n');
fs.writeFileSync(path.join(opt.out, 'list.txt'), list + '\n');
execFileSync('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(opt.out, 'list.txt'), '-c', 'copy', path.join(opt.out, 'video.mp4')], { stdio: 'inherit' });
console.log(`done in ${((Date.now() - tStart) / 60000).toFixed(1)} min -> ${path.join(opt.out, 'video.mp4')}`);
