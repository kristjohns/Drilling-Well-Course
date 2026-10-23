// Render stills for review.
//   node tools/frame.mjs 12.5 40 61.2            -> build/frames/t_000012.50.png ...
//   node tools/frame.mjs --beat 2.5 --n 4        -> 4 stills spread over beat 2.5
//   node tools/frame.mjs --chapter 3 --sheet     -> contact sheet of a chapter (2 stills per beat)
//   --ch 2,3 only builds those chapters (faster); --scale 0.5 for small output
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { startServer } from './server.mjs';

const args = process.argv.slice(2);
const opt = { times: [], n: 2, sheet: false, out: 'build/frames', scale: 1 };
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === '--beat') opt.beat = args[++i];
  else if (a === '--chapter') opt.chapter = Number(args[++i]);
  else if (a === '--n') opt.n = Number(args[++i]);
  else if (a === '--sheet') opt.sheet = true;
  else if (a === '--ch') opt.ch = args[++i];
  else if (a === '--out') opt.out = args[++i];
  else if (a === '--scale') opt.scale = Number(args[++i]);
  else opt.times.push(Number(a));
}
fs.mkdirSync(opt.out, { recursive: true });
const tl = JSON.parse(fs.readFileSync('src/data/timeline.json', 'utf8'));
const beats = tl.chapters.flatMap((c) => c.beats.map((b) => ({ ...b, ch: c.no })));
if (opt.beat) { const b = beats.find((x) => x.id === opt.beat); for (let k = 0; k < opt.n; k++) opt.times.push(b.start + (b.end - b.start) * (k + 0.5) / opt.n); }
if (opt.chapter !== undefined) {
  const c = tl.chapters.find((x) => x.no === opt.chapter);
  if (c.title_card) opt.times.push(c.title_card[0] + 1.6);
  for (const b of c.beats) for (let k = 0; k < opt.n; k++) opt.times.push(b.start + (b.end - b.start) * (k + 0.6) / opt.n);
  if (!opt.ch) opt.ch = String(opt.chapter);
}
const { srv, url } = await startServer(0);
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--force-color-profile=srgb', '--font-render-hinting=none'] });
const page = await (await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: opt.scale })).newPage();
const errs = [];
page.on('console', (m) => { if (['error', 'warning'].includes(m.type())) errs.push(m.text()); });
page.on('pageerror', (e) => errs.push('PAGEERROR ' + e.message));
await page.goto(`${url}/src/index.html?render=1${opt.ch ? '&ch=' + opt.ch : ''}`);
await page.waitForFunction('window.__ready === true || window.__error', null, { timeout: 300000 });
const err = await page.evaluate('window.__error');
if (err) { console.error('BOOT ERROR\n' + err); process.exit(1); }
const files = [];
for (const t of opt.times) {
  await page.evaluate((tt) => window.__seek(tt), t);
  const f = path.join(opt.out, `t_${t.toFixed(2).padStart(9, '0')}.png`);
  await page.screenshot({ path: f });
  files.push([t, f]);
}
await browser.close();
srv.close();
for (const e of [...new Set(errs)].slice(0, 30)) console.log('console:', e.slice(0, 300));
if (opt.sheet && files.length) {
  // contact sheet with ffmpeg (tile), 4 columns at 480 px
  const list = files.map(([, f]) => f);
  const cols = 4, rows = Math.ceil(list.length / cols);
  const { execFileSync } = await import('node:child_process');
  const sheet = path.join(opt.out, `sheet_ch${opt.chapter ?? 'x'}.jpg`);
  const inputs = list.flatMap((f) => ['-i', f]);
  const filt = list.map((_, i) => `[${i}:v]scale=480:-1[v${i}]`).join(';') + ';' + list.map((_, i) => `[v${i}]`).join('') + `xstack=inputs=${list.length}:layout=` +
    list.map((_, i) => `${(i % cols) * 480}_${Math.floor(i / cols) * 270}`).join('|') + ':fill=black[out]';
  if (list.length > 1) execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...inputs, '-filter_complex', filt, '-map', '[out]', '-q:v', '3', sheet]);
  console.log('sheet', sheet, `(${rows} rows)`);
}
console.log(files.map(([t, f]) => `${t.toFixed(2)} ${f}`).join('\n'));
