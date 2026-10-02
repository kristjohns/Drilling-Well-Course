// QA: find on-screen text that is covered by, or collides with, something else, over the whole timeline.
//   node tools/overlap-scan.mjs                         every 0.25 s, 4 browsers -> build/qa/overlaps.json + summary
//   node tools/overlap-scan.mjs --from 350 --to 410 --step 0.5
// At every sample time the page is seeked and each visible piece of text is probed on a grid of points with
// document.elementsFromPoint(): anything painted *above* the text (another label, a line, a ring, a flow dot ...) at
// those points is reported ("occluded"). In addition, pairs of text boxes that overlap are reported ("text-text").
import fs from 'node:fs';
import os from 'node:os';
import { chromium } from 'playwright';
import { startServer } from './server.mjs';

const args = process.argv.slice(2);
const opt = { step: 0.25, from: 0, to: 0, minpts: 3, minop: 0.5, workers: Math.min(4, os.cpus().length), out: 'build/qa/overlaps.json' };
for (let i = 0; i < args.length; i += 2) opt[args[i].replace(/^--/, '')] = isNaN(Number(args[i + 1])) ? args[i + 1] : Number(args[i + 1]);

const SCAN = ({ minop, cols, rows }) => {
  const SKIP = 'defs, mask, clipPath, pattern, symbol, script, style, title';
  const effOpacity = (el) => {
    let op = 1;
    for (let e = el; e && e !== document.body; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none') return 0;
      if (e === el && cs.visibility === 'hidden') return 0;
      op *= parseFloat(cs.opacity);
      if (op < 0.02) return 0;
    }
    return op;
  };
  const alphaOf = (c) => {
    if (!c || c === 'none') return 0;
    if (c.startsWith('url(')) return 0.6;
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return 1;
    const p = m[1].split(/[ ,\/]+/).filter(Boolean);
    return p.length > 3 ? parseFloat(p[3]) : 1;
  };
  const paintAlpha = (el) => {
    const cs = getComputedStyle(el);
    if (el.tagName.toLowerCase() === 'text' || el.tagName.toLowerCase() === 'tspan') return Math.max(alphaOf(cs.fill) * parseFloat(cs.fillOpacity || 1), 0);
    const f = alphaOf(cs.fill) * parseFloat(cs.fillOpacity || 1);
    const sw = parseFloat(cs.strokeWidth || 0);
    const s = sw > 0.4 ? alphaOf(cs.stroke) * parseFloat(cs.strokeOpacity || 1) : 0;
    return Math.max(f, s);
  };
  const desc = (el) => {
    const parts = [];
    for (let e = el, i = 0; e && e !== document.body && i < 3; e = e.parentElement, i++) {
      parts.push(e.tagName.toLowerCase() + (e.getAttribute('class') ? '.' + e.getAttribute('class').split(' ')[0] : '') + (e.id ? '#' + e.id : ''));
    }
    const r = el.getBoundingClientRect();
    const own = (el.textContent || '').trim().slice(0, 24);
    return `${parts.join('<')}@${Math.round(r.left)},${Math.round(r.top)} ${Math.round(r.width)}x${Math.round(r.height)}${own ? ' "' + own + '"' : ''}`;
  };

  const out = [];
  const texts = [];
  const walker = document.createTreeWalker(document.getElementById('stage'), NodeFilter.SHOW_TEXT);
  const range = document.createRange();
  let n;
  while ((n = walker.nextNode())) {
    const txt = n.nodeValue.replace(/\s+/g, ' ').trim();
    const el = n.parentElement;
    if (!txt || !el || el.closest(SKIP)) continue;
    const op = effOpacity(el);
    if (op < minop) continue;
    range.selectNode(n);
    const r = range.getBoundingClientRect();
    if (r.width < 2 || r.height < 2 || r.right < 0 || r.bottom < 0 || r.left > 1920 || r.top > 1080) continue;
    texts.push({ n, el, txt, r });
  }
  for (const T of texts) {
    // --- occlusion probe
    const { r, el } = T;
    const svgText = el.closest('text');
    const isSelf = (e) => (svgText ? e.closest('text') === svgText : e === el || el.contains(e) || e.contains(el));
    let hitPts = 0;
    const occ = new Map();
    for (let i = 0; i < cols; i++) {
      for (let j = 0; j < rows; j++) {
        const x = r.left + 1 + ((i + 0.5) / cols) * (r.width - 2);
        const y = r.top + r.height * (0.3 + 0.4 * ((j + 0.5) / rows));
        if (x < 0 || x > 1919 || y < 0 || y > 1079) continue;
        const stack = document.elementsFromPoint(x, y);
        let above = [];
        let found = false;
        for (const e of stack) { if (isSelf(e)) { found = true; break; } above.push(e); }
        if (!found) continue;
        let bad = null;
        for (const e of above) {
          if (e.closest(SKIP) || e.id === 'vignette' || e.id === 'grain' || e.id === 'stage' || e.id === 'scenes') continue;
          const tn = e.tagName.toLowerCase();
          if (tn === 'svg' || tn === 'g') continue;
          let pa;
          if (e instanceof SVGElement) pa = paintAlpha(e);
          else { const bg = getComputedStyle(e).backgroundColor; pa = alphaOf(bg); if (pa < 0.4) continue; }
          const o = effOpacity(e) * pa;
          if (o >= 0.4) { bad = e; break; }
        }
        if (bad) { hitPts++; const k = desc(bad); occ.set(k, (occ.get(k) || 0) + 1); }
      }
    }
    if (hitPts >= 1) out.push({ kind: 'occluded', t: T.txt, pts: hitPts, by: [...occ.entries()].sort((a, b) => b[1] - a[1]).slice(0, 2).map((x) => x[0]), box: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)] });
  }
  // --- text/text boxes
  for (let a = 0; a < texts.length; a++) {
    for (let b = a + 1; b < texts.length; b++) {
      const A = texts[a].r, B = texts[b].r;
      const w = Math.min(A.right, B.right) - Math.max(A.left, B.left), h = Math.min(A.bottom, B.bottom) - Math.max(A.top, B.top);
      if (w <= 1.5 || h <= 1.5) continue;
      const frac = (w * h) / Math.min(A.width * A.height, B.width * B.height);
      if (frac >= 0.12) out.push({ kind: 'text-text', t: texts[a].txt, t2: texts[b].txt, frac: +frac.toFixed(2), box: [Math.round(Math.max(A.left, B.left)), Math.round(Math.max(A.top, B.top))] });
    }
  }
  return out;
};

const { srv, url } = await startServer(0);
async function openPage() {
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--font-render-hinting=none'] });
  const page = await (await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 })).newPage();
  await page.goto(`${url}/src/index.html?render=1`);
  await page.waitForFunction('window.__ready === true || window.__error', null, { timeout: 180000 });
  const err = await page.evaluate('window.__error');
  if (err) throw new Error(err);
  return { browser, page };
}

const probe = await openPage();
const dur = await probe.page.evaluate('window.__duration');
await probe.browser.close();
const t0 = opt.from, t1 = opt.to || dur;
const times = [];
for (let t = t0; t <= t1 + 1e-9; t += opt.step) times.push(+t.toFixed(3));
console.log(`scanning ${times.length} samples (${t0}..${t1} s, step ${opt.step}) with ${opt.workers} browsers`);

const hits = [];
async function work(id) {
  const { browser, page } = await openPage();
  for (let i = id; i < times.length; i += opt.workers) {
    const t = times[i];
    await page.evaluate((x) => window.__seek(x), t);
    const res = await page.evaluate(SCAN, { minop: opt.minop, cols: 14, rows: 3 });
    for (const h of res) hits.push({ time: t, ...h });
  }
  await browser.close();
}
await Promise.all(Array.from({ length: opt.workers }, (_, i) => work(i)));
srv.close();

hits.sort((p, q) => p.time - q.time);
fs.mkdirSync('build/qa', { recursive: true });
fs.writeFileSync(opt.out, JSON.stringify(hits));

const groups = new Map();
for (const h of hits) {
  if (h.kind === 'occluded' && h.pts < opt.minpts) continue;
  const k = h.kind === 'occluded' ? `OCCLUDED "${h.t}"  by  ${h.by[0]}` : `TEXT-TEXT "${h.t}" ⟷ "${h.t2}"`;
  const g = groups.get(k) || { k, ranges: [], max: 0, box: h.box };
  const last = g.ranges[g.ranges.length - 1];
  if (last && h.time - last[1] <= opt.step * 1.51) last[1] = h.time; else g.ranges.push([h.time, h.time]);
  g.max = Math.max(g.max, h.pts || h.frac * 100);
  groups.set(k, g);
}
for (const g of groups.values()) g.ranges = g.ranges.filter(([a, b]) => b - a >= opt.step * 2 - 1e-6 || g.max >= 12);
const list = [...groups.values()].filter((g) => g.ranges.length).sort((p, q) => p.ranges[0][0] - q.ranges[0][0]);
console.log(`${hits.length} raw hits; ${list.length} distinct findings (occluded needs >= ${opt.minpts} probe points)`);
for (const g of list) {
  const r = g.ranges.map(([a, b]) => (a === b ? `${a.toFixed(2)}` : `${a.toFixed(2)}–${b.toFixed(2)}`)).join(', ');
  console.log(`${r}\n    ${g.k}  [max ${g.max.toFixed(0)}] box ${g.box}`);
}
