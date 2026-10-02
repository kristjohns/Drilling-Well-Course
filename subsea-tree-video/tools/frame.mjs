// Render still frames for inspection.
//   node tools/frame.mjs 12.5 30 45.2            -> build/frames/f_12.50.png ...
//   node tools/frame.mjs --sheet 10,20,30,40     -> contact sheet build/frames/sheet.png
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { chromium } from 'playwright';
import { startServer } from './server.mjs';

const args = process.argv.slice(2);
let sheet = false, times = [], outDir = 'build/frames', scale = 1, query = '', cols = 3, every = 0, from = 0, to = 0, tw = 640, per = 0;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--sheet') sheet = true;
  else if (args[i] === '--out') outDir = args[++i];
  else if (args[i] === '--scale') scale = Number(args[++i]);
  else if (args[i] === '--q') query = '&' + args[++i];
  else if (args[i] === '--cols') cols = Number(args[++i]);
  else if (args[i] === '--every') every = Number(args[++i]);
  else if (args[i] === '--from') from = Number(args[++i]);
  else if (args[i] === '--to') to = Number(args[++i]);
  else if (args[i] === '--tw') tw = Number(args[++i]);
  else if (args[i] === '--per') per = Number(args[++i]);   // several sheets, `per` frames each: sheet_001.png ...
  else times.push(...args[i].split(',').filter(Boolean).map(Number));
}
fs.mkdirSync(outDir, { recursive: true });
const { srv, url } = await startServer(0);
const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--font-render-hinting=none'] });
const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: scale });
const page = await ctx.newPage();
page.on('console', (m) => { if (['error', 'warning'].includes(m.type())) console.log('[page]', m.type(), m.text()); });
page.on('pageerror', (e) => console.log('[pageerror]', e.message));
await page.goto(`${url}/src/index.html?render=1${query}`);
await page.waitForFunction('window.__ready === true || window.__error', null, { timeout: 120000 });
const err = await page.evaluate('window.__error');
if (err) { console.error('BOOT ERROR:', err); await browser.close(); srv.close(); process.exit(1); }
const dur = await page.evaluate('window.__duration');
console.log('duration', dur);
if (every > 0) { for (let t = from; t <= (to || dur); t += every) times.push(+t.toFixed(2)); }
const files = [];
for (const t of times) {
  const tt = Math.min(Math.max(0, t), dur);
  await page.evaluate((x) => window.__seek(x), tt);
  const f = path.join(outDir, `f_${tt.toFixed(2).padStart(7, '0')}.png`);
  await page.screenshot({ path: f });
  files.push(f);
  console.log('wrote', f);
}
await browser.close(); srv.close();
if (sheet && files.length) {
  const groups = per > 0 ? Array.from({ length: Math.ceil(files.length / per) }, (_, i) => files.slice(i * per, (i + 1) * per)) : [files];
  groups.forEach((g, i) => {
    const cc = Math.min(cols, g.length);
    const out = path.join(outDir, per > 0 ? `sheet_${String(i + 1).padStart(3, '0')}.png` : 'sheet.png');
    // label every tile with its time
    execFileSync('montage', ['-label', '%t', ...g, '-tile', `${cc}x`, '-geometry', `${tw}x${Math.round(tw * 9 / 16)}+4+4`, '-background', '#111', '-fill', '#ddd', '-pointsize', '18', out]);
    console.log('wrote', out);
  });
}
