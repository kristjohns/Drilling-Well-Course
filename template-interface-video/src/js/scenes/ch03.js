// Chapter 3 — non-linear FE to EN 1993-1-5 Annex C: the annex, material models (C.6), load multiplier (C.7), the limit
// state criteria (C.8, the 5 %), the ring analysis (curves + 3D strain contour), the margin alpha_u >= alpha_1 alpha_2 (C.9).
import { E, ease, COL, clamp, smooth, lerp, fmt, Actor } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause } from '../engine/hud.js';
import { camSpline } from '../three/world.js';
import { RING_D } from '../three/models.js';
import { stamp, quoteCard, counter } from './kit.js';
import { probe3D, note } from './fx.js';
import { ringState, ringPoint, strainLegend, RINGU } from './ringfx.js';

export async function build(E, T, D) {
  const ch = T.ch(3);
  titleCard(ch, 'Material models, load multiplier, limit state criteria and the margin');
  const W3 = E.world, md = W3.models;
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const I = D.inputs, MK = D.marks, CK = D.check;
  const Ca = D.curves.a, Cc = D.curves.c;

  // ------------------------------------------------------------------ 3.1 Annex C
  {
    const B = b('3.1');
    const S = new Scene(B.start, B.end);
    clause('EN 1993-1-5:2006 · Annex C (informative) · Table C.1', B.start + 0.3, B.end);
    const hd = S.card(`<div class="ref">EUROCODE 3 · PART 1-5 · PLATED STRUCTURAL ELEMENTS</div>
      <div style="font-weight:800;font-size:56px;letter-spacing:-0.02em;line-height:1.05">Annex C</div>
      <div style="font-weight:600;font-size:34px;color:#b9cad8;margin-top:6px">Finite element methods of analysis (FEM)</div>`, { x: 110, y: 170, w: 900, cls: 'glass' });
    hd.in(c('3.1', 'annex') - 0.3, 0.7, 'rise');
    const inf = S.div('<span class="badge warn" style="font-size:22px">informative</span>', { x: 1060, y: 205 });
    inf.in(c('3.1', 'inf'), 0.5, 'pop');
    const inft = S.div('the National Annex and the design basis decide whether, and how, it is used', { x: 1060, y: 265, w: 760, cls: 'small' });
    inft.in(c('3.1', 'inf') + 0.4, 0.6);
    const rows = [['mna', 'Material non-linear · geometry linear · no imperfections', 'plastic resistance (ULS)', 'stocky parts that cannot buckle — like the slot ring'],
      ['gmnia', 'Material and geometry non-linear · with imperfections', 'elastic-plastic resistance with buckling (ULS)', 'plates and shells that can buckle']];
    rows.forEach(([cue, a, r, ex], i) => {
      const y = 470 + i * 200;
      const cd = S.card(`<div style="display:flex;gap:26px;align-items:center"><div style="flex:1"><div style="font-weight:720;font-size:29px">${a}</div><div class="small" style="font-size:22px;margin-top:4px">${ex}</div></div><div class="c-amber" style="font-weight:700;font-size:26px;width:380px;text-align:right">→ ${r}</div></div>`,
        { x: 110, y, w: 1700, cls: 'glass' });
      cd.in(c('3.1', cue) - 0.2, 0.6, 'left');
    });
    S.div('after EN 1993-1-5 Table C.1 (two of its rows)', { x: 110, y: 880, cls: 'tiny' }).in(c('3.1', 'mna'), 0.5);
  }

  // ------------------------------------------------------------------ 3.2 material models (C.6) and the load multiplier (C.7)
  {
    const B = b('3.2');
    const S = new Scene(B.start, B.end);
    clause('EN 1993-1-5 · C.6 material properties · C.7 loads', B.start + 0.3, B.end);
    const ch2 = S.chart({ x: 200, y: 200, w: 800, h: 560, xmin: 0, xmax: 5, ymin: 0, ymax: 1.6, xticks: [0, 1, 2, 3, 4, 5], yticks: [0, 0.4, 0.8, 1.2, 1.6],
      yfmt: (v) => v.toFixed(1), xlabel: 'Strain · %', ylabel: 'σ / f<sub>y</sub>', title: 'MATERIAL MODELS OF C.6 (SCHEMATIC)' });
    ch2.show(B.start + 0.4);
    const ey = 345 / 210000 * 100;
    const mods = [
      ['a', '(a) without strain hardening', COL.cyan, [[0, 0], [ey, 1], [5, 1]]],
      ['b', '(b) nominal plateau slope', '#9fb2c2', [[0, 0], [ey, 1], [5, 1.05]]],
      ['c', '(c) linear strain hardening', COL.amber, [[0, 0], [ey, 1], [5, 1 + (5 - ey) / 100 * 210000 / 100 / 345]]],
      ['d', '(d) true stress-strain curve from tests', COL.coral, [[0, 0], [ey, 1], [1.4, 1.0], ...Array.from({ length: 20 }, (_, k) => { const x = 1.4 + 3.6 * (k + 1) / 20; return [x, 1.0 + 0.48 * (1 - Math.exp(-(x - 1.4) / 1.6))]; })]],
    ];
    mods.forEach(([cue, name, col, pts], i) => {
      ch2.curve(pts, { color: col, width: 4, t: c('3.2', cue), d: 0.7 });
      const lb = S.div(name, { x: 1040, y: 260 + i * 56, cls: 'small', style: `color:${col};font-size:25px;font-weight:650` });
      lb.in(c('3.2', cue), 0.4, 'left');
    });
    const chv = S.card('<div style="font-weight:750;font-size:27px">Characteristic values</div><div class="small" style="font-size:23px">f<sub>y</sub> itself — not f<sub>y</sub>/γ<sub>M</sub></div>', { x: 1040, y: 520, w: 640, cls: 'glass' });
    chv.in(c('3.2', 'char'), 0.6, 'rise');
    const eq = S.eq('F = \\alpha \\cdot F_{Ed}', { x: 1040, y: 760, size: 54, align: 'left' });
    eq.in(c('3.2', 'load'), 0.8, 'write');
    S.div('all factored design loads × one load multiplier α', { x: 1040, y: 820, cls: 'small' }).in(c('3.2', 'load') + 0.5, 0.5);
    counter(S, { x: 1500, y: 760, a: 0, b: 1.8, t0: c('3.2', 'ramp'), t1: c('3.2', 'ramp') + 4.0, d: 2, prefix: 'α = ', size: 48, anchor: 'lm', color: COL.amber });
  }

  // ------------------------------------------------------------------ 3.3 the limit state criteria (C.8)
  {
    const B = b('3.3');
    const S = new Scene(B.start, B.end);
    clause('EN 1993-1-5 · C.8 limit state criteria', B.start + 0.3, B.end);
    const card = S.card(`<div class="ref">EN 1993-1-5 · C.8 (1) · WORDING ABRIDGED</div>
      <div class="quote" style="font-size:28px">The ultimate limit state criteria:</div>
      <div class="quote p1" style="font-size:28px;margin-top:10px">1. structures susceptible to buckling: attainment of the <span class="q">maximum load</span></div>
      <div class="quote p2" style="font-size:28px;margin-top:10px">2. regions subjected to tensile stresses: attainment of a limiting value of the <span class="q">principal membrane strain</span></div>
      <div class="small p3" style="font-size:24px;margin-top:18px;color:#e9f2f9">NOTE 1 · The National Annex may specify the limiting value of a principal strain. <span class="c-amber" style="font-weight:750">A value of 5 % is recommended.</span></div>
      <div class="small p4" style="font-size:24px;margin-top:12px;color:#e9f2f9">NOTE 2 · Other criteria may be used, e.g. attainment of the yielding criterion or limitation of the yielding zone.</div>`,
    { x: 110, y: 170, w: 1060, cls: 'glass' });
    card.in(B.start + 0.4, 0.6, 'rise');
    later(() => {
      const parts = [['p1', 'buck'], ['p2', 'tens'], ['p3', 'five'], ['p4', 'other']];
      for (const [cl, cue] of parts) { const el = card.el.querySelector('.' + cl); const a = S.track(new Actor(el, { o: 0 })); a.in(c('3.3', cue) - 0.2, 0.5, 'none'); }
    });
    const five = S.div('5 %', { x: 1480, y: 330, cls: 'num', anchor: 'cm', style: 'font-size:150px;color:#ffb547;font-weight:700' });
    five.in(c('3.3', 'rec'), 0.6, 'pop');
    S.div('recommended · nationally determined', { x: 1480, y: 430, cls: 'small', anchor: 'cm' }).in(c('3.3', 'rec') + 0.4, 0.5);
    // membrane versus surface strain through a shell thickness
    const sx = 1260, sy = 560, sw = 440, sh = 120;
    const g = S.g(); g.in(c('3.3', 'membrane') - 0.3, 0.6, 'none');
    S.rect(sx, sy, sw, sh, { fill: 'rgba(154,168,181,0.35)', stroke: '#9aa8b5', width: 2, parent: g.el, o: 1 });
    S.line(sx, sy + sh / 2, sx + sw, sy + sh / 2, { stroke: '#ffffff', width: 2, dash: '6 6', parent: g.el, o: 1 });
    // strain distribution: membrane 2 % + bending ±1.5 % -> drawn as a linear profile to the right
    const px = sx + sw + 40, k = 26;
    S.line(px, sy - 10, px, sy + sh + 10, { stroke: 'rgba(200,225,245,0.55)', width: 2, parent: g.el, o: 1 });
    S.path(`M${px},${sy} L${px + 3.5 * k},${sy} L${px + 0.5 * k},${sy + sh} L${px},${sy + sh}`, { stroke: COL.coral, width: 3, fill: 'rgba(255,111,97,0.18)', parent: g.el, o: 1 });
    S.line(px, sy + sh / 2, px + 2 * k, sy + sh / 2, { stroke: COL.amber, width: 5, parent: g.el, o: 1 });
    const l1 = S.div('membrane = mid-thickness', { x: sx, y: sy + sh + 40, cls: 'small c-amber', style: 'font-size:24px;font-weight:700' });
    l1.in(c('3.3', 'membrane') + 0.3, 0.5);
    const l2 = S.div('surface = membrane + plate bending', { x: sx, y: sy + sh + 80, cls: 'small c-coral', style: 'font-size:24px' });
    l2.in(c('3.3', 'membrane') + 0.9, 0.5);
    S.div('shell section', { x: sx, y: sy - 34, cls: 'tiny' }).in(c('3.3', 'membrane'), 0.5);
  }

  // ------------------------------------------------------------------ 3.4 running the ring
  const aU = CK.alpha_u, aPl = MK.a.plateau;
  {
    const B = b('3.4');
    const panel = { x: 40, y: 140, w: 900, h: 800 };
    const K = { lin: c('3.4', 'lin'), y: c('3.4', 'y'), p02: c('3.4', 'p02'), spread: c('3.4', 'spread'), flat: c('3.4', 'flat'), hard: c('3.4', 'hard'), five: c('3.4', 'five') };
    const sched = [[B.start, 0], [K.lin, 0], [K.y, MK.c.first_yield.alpha], [K.p02, MK.c.p02.alpha], [K.spread + 1.5, 1.45], [K.flat, aPl], [K.hard, 1.62], [K.five, aU], [B.end, aU + 0.03]];
    const alpha = (t) => {
      if (t <= sched[0][0]) return 0;
      for (let i = 0; i < sched.length - 1; i++) if (t <= sched[i + 1][0]) return lerp(sched[i][1], sched[i + 1][1], ease.inOut(clamp((t - sched[i][0]) / (sched[i + 1][0] - sched[i][0]))));
      return sched[sched.length - 1][1];
    };
    const DEFS = 12;
    let fNow = null;
    const cam = camSpline([
      { t: B.start, p: [1.35, 2.1, 2.45], l: [0.1, 0.3, 0.12], fov: 33 },
      { t: K.five, p: [1.05, 1.8, 1.95], l: [0.15, 0.33, 0.18], fov: 33 },
      { t: B.end, p: [1.0, 1.78, 1.9], l: [0.15, 0.33, 0.18], fov: 33 },
    ]);
    W3.shot(B.start, B.end, {
      show: ['feRing'], panel, fadeIn: 0.7, fadeOut: 0.6, cam, fog: 0, bg: '#0b1824',
      update: (t) => {
        fNow = ringState(D, 'c', alpha(t), DEFS);
        RINGU.uRMode.value = 1; RINGU.uRF.value = 1;
        md.feRing.userData.lines.material.opacity = 0.3;
      },
    });
    const S = new Scene(B.start, B.end);
    clause('EN 1993-1-5 · C.6 (a), (c) · C.7 · C.8 — slot ring D', B.start + 0.3, B.end);
    const chc = S.chart({ x: 1060, y: 190, w: 780, h: 520, xmin: 0, xmax: 12, ymin: 0, ymax: 2.0, xticks: [0, 2, 4, 6, 8, 10, 12], yticks: [0, 0.5, 1.0, 1.5, 2.0],
      yfmt: (v) => v.toFixed(1), xlabel: 'Radial displacement at the contact · mm', ylabel: 'Load multiplier α', title: 'MATERIALLY NON-LINEAR ANALYSIS · LOAD-DISPLACEMENT' });
    chc.show(B.start + 0.3);
    const one = S.path(`M${chc.X(0)},${chc.Y(1)} L${chc.X(12)},${chc.Y(1)}`, { stroke: '#ffffff', width: 2, dash: '5 7' });
    one.in(B.start + 0.8, 0.5, 'none');
    S.div('design load (α = 1)', { x: chc.X(11.8), y: chc.Y(1) + 22, cls: 'tiny', anchor: 'rm', style: 'color:#fff' }).in(B.start + 1.0, 0.5);
    const dOf = (C, a) => { for (let i = 0; i < C.length - 1; i++) if (a <= C[i + 1][1]) return lerp(C[i][0], C[i + 1][0], (a - C[i][1]) / (C[i + 1][1] - C[i][1])); return C[C.length - 1][0]; };
    const pc = S.path('M0,0', { stroke: COL.amber, width: 5, parent: chc.plot, o: 1 });
    E.anim(K.lin - 0.2, B.end, (t) => {
      const a = alpha(t);
      const pts = [[0, 0]];
      for (const p of Cc) { if (p[1] <= a) pts.push([p[0], p[1]]); else break; }
      pts.push([dOf(Cc, a), a]);
      pc.el.setAttribute('d', chc.pathD(pts.filter(([x]) => x <= 12.5)));
    });
    chc.curve(Ca.filter(([x]) => x <= 12).map(([x, y]) => [x, y]), { color: COL.cyan, width: 4, t: K.flat - 1.0, d: 1.6 });
    const la = S.div('(a) no hardening', { x: chc.X(4.2), y: chc.Y(aPl) + 34, cls: 'small c-cyan', style: 'font-size:22px' });
    la.in(K.flat + 0.4, 0.5);
    const lc = S.div('(c) linear hardening', { x: chc.X(8.6), y: chc.Y(1.93), cls: 'small c-amber', style: 'font-size:22px' });
    lc.in(K.hard, 0.5);
    const mk = (a, C, col, t, txt, dx, dy) => {
      const x = dOf(C, a);
      chc.dot(x, a, { color: col, r: 9, t });
      const l = S.div(txt, { x: chc.X(x) + dx, y: chc.Y(a) + dy, cls: 'label', anchor: dx >= 0 ? 'lm' : 'rm', style: `font-size:21px;color:${col}` });
      l.in(t + 0.2, 0.5);
      return l;
    };
    mk(MK.c.first_yield.alpha, Cc, '#ffffff', K.y, `first yield · α <span class="num">${MK.c.first_yield.alpha.toFixed(2)}</span>`, 22, 18);
    mk(MK.c.p02.alpha, Cc, COL.green, K.p02, `0.2 % plastic strain · <span class="num">${MK.c.p02.alpha.toFixed(2)}</span>`, 22, 24);
    const pl = S.path(`M${chc.X(0)},${chc.Y(aPl)} L${chc.X(12)},${chc.Y(aPl)}`, { stroke: COL.cyan, width: 2, dash: '3 6' });
    pl.in(K.mech, 0.5, 'none');
    const plt = S.div(`mechanism · α <span class="num">${aPl.toFixed(2)}</span>`, { x: chc.X(11.8), y: chc.Y(aPl) + 22, cls: 'tiny', anchor: 'rm', style: 'color:#4fd1ff;font-size:20px' });
    plt.in(K.mech + 0.2, 0.5);
    mk(aU, Cc, '#ff4d5e', K.five, `5 % strain · α<sub>u</sub> = <span class="num">${aU.toFixed(2)}</span>`, -22, -26);
    // a horizontal legend under the chart
    const lg = S.card(`<div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap;font-size:19px">
      <span class="tiny" style="letter-spacing:0.1em">STRAIN</span>
      ${[['linear-gradient(90deg,#08146b,#0f42a6)', 'elastic'], ['rgb(0,143,178)', 'yielded'], ['rgb(22,156,43)', '0.2 %–1 %'], ['rgb(200,170,4)', '1–2 %'], ['rgb(217,87,0)', '2–5 %'], ['rgb(200,8,8)', '≥ 5 %']].map(([col, t]) => `<span style="display:flex;align-items:center;gap:6px"><span style="width:26px;height:16px;border-radius:3px;background:${col}"></span>${t}</span>`).join('')}
      <span style="display:flex;align-items:center;gap:6px"><span style="width:26px;height:3px;background:#fff"></span>5 % line</span></div>`,
    { x: 1060, y: 820, w: 780, cls: 'glass', style: 'padding:12px 18px' });
    lg.in(B.start + 1.0, 0.6, 'rise');
    const al = S.div('', { x: 70, y: 170, cls: 'num', style: 'font-size:40px;color:#ffb547' });
    let last = '';
    E.anim(B.start, B.end, (t) => { const s = `α = ${alpha(t).toFixed(2)}`; if (s !== last) { al.el.textContent = s; last = s; } });
    al.in(K.lin, 0.5);
    probe3D(S, () => ringPoint(44, I.ro, RING_D.y1, fNow, DEFS), 'tension · behind the contact', { t0: K.y + 0.6, t1: K.spread + 4, dx: 110, dy: 140, color: '#ffffff' });
    probe3D(S, () => ringPoint(2, I.ri, RING_D.y1, fNow, DEFS), 'at the strut', { t0: K.spread + 0.4, t1: K.five, dx: -60, dy: -160, color: '#ffffff' });
    note(S, `Fibre beam model of the ring (C.6 (c): hardening E/100; (a): nominal slope E/10 000); 3D shows model (c), displacements ×${DEFS}`, { t0: B.start + 1.2, t1: B.end - 0.4 });
  }

  // ------------------------------------------------------------------ 3.5 the margin (C.9)
  {
    const B = b('3.5');
    const S = new Scene(B.start, B.end);
    clause('EN 1993-1-5 · C.9 partial factors', B.start + 0.3, B.end);
    const eq = S.eq('\\alpha_u \\;\\ge\\; \\alpha_1\\,\\alpha_2', { x: 960, y: 230, size: 84 });
    eq.in(c('3.5', 'au'), 0.9, 'write');
    const d1 = S.card('<div style="font-weight:750;font-size:29px"><span class="c-amber">α<sub>1</sub></span> · model uncertainty of the FE modelling</div><div class="small" style="font-size:22px">from evaluations of test calibrations (EN 1990, Annex D)</div>', { x: 160, y: 360, w: 760, cls: 'glass' });
    d1.in(c('3.5', 'a1') - 0.2, 0.6, 'left');
    const d2 = S.card('<div style="font-weight:750;font-size:29px"><span class="c-amber">α<sub>2</sub></span> · scatter of loading and resistance</div><div class="small" style="font-size:22px">γ<sub>M1</sub> if instability governs · γ<sub>M2</sub> if fracture governs</div>', { x: 1000, y: 360, w: 760, cls: 'glass' });
    d2.in(c('3.5', 'a2') - 0.2, 0.6, 'right');
    const e1 = S.eq('\\alpha_1 = 1.0\\ \\text{(benchmarked model)}, \\quad \\alpha_2 \\le 1.3', { x: 960, y: 560, size: 40 });
    e1.in(c('3.5', 'ex'), 0.8, 'write');
    const e2 = S.eq(`\\text{(c) hardening:}\\quad \\alpha_u = ${aU.toFixed(2)} \\;\\ge\\; 1.0\\times1.3 = 1.30`, { x: 960, y: 650, size: 42 });
    e2.in(c('3.5', 'pass'), 0.8, 'write');
    stamp(S, 'pass', { x: 1640, y: 650, t: c('3.5', 'pass') + 0.8, kind: 'pass', size: 26 });
    const e3 = S.eq(`\\text{(a) no hardening:}\\quad \\alpha_u = ${MK.a.e5.alpha.toFixed(2)} \\;\\ge\\; 1.30`, { x: 960, y: 730, size: 42 });
    e3.in(c('3.5', 'passa'), 0.8, 'write');
    stamp(S, 'pass', { x: 1640, y: 730, t: c('3.5', 'passa') + 0.8, kind: 'pass', size: 26 });
    const v1 = S.card(`<div class="tiny">ELASTIC CHECK · 6.2.1(5)</div><div style="font-weight:750;font-size:30px">utilisation <span class="num c-red">${D.elastic.util.toFixed(2)}</span> → fails</div>`, { x: 300, y: 830, w: 600, cls: 'glass', style: 'border-color:rgba(255,77,94,0.6)' });
    v1.in(c('3.5', 'verdict'), 0.6, 'rise');
    const v2 = S.card(`<div class="tiny">NON-LINEAR · ANNEX C</div><div style="font-weight:750;font-size:30px">α<sub>u</sub> <span class="num c-green">${aU.toFixed(2)}</span> ≥ 1.30 → accepted</div>`, { x: 1020, y: 830, w: 600, cls: 'glass', style: 'border-color:rgba(70,211,154,0.6)' });
    v2.in(c('3.5', 'verdict') + 0.6, 0.6, 'rise');
    note(S, 'α₁ = 1.0 is an assumption for the example; take α₂ (γM1, γM2) from the governing code and National Annex', { t0: c('3.5', 'ex') + 1, t1: B.end - 0.4 });
  }
}
