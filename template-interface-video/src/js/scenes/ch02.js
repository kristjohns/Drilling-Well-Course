// Chapter 2 — the template steel, the elastic check: partial factors (N-001, N-004), the yield strength the Eurocode
// way (ReH or Rp0.2), the von Mises check of EN 1993-1-1 6.2.1(5) on the slot ring: 416 MPa against 300 MPa.
import { E, ease, COL, clamp, smooth, lerp, fmt, Actor } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause } from '../engine/hud.js';
import { camSpline } from '../three/world.js';
import { RING_D } from '../three/models.js';
import { table, stamp, quoteCard } from './kit.js';
import { probe3D, note } from './fx.js';
import { ringState, ringPoint, stressLegend, RINGU } from './ringfx.js';

export async function build(E, T, D) {
  const ch = T.ch(2);
  titleCard(ch, 'Partial factors, the yield strength in Eurocode 3, and the von Mises check');
  const W3 = E.world, md = W3.models;
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const I = D.inputs, EL = D.elastic;

  // ------------------------------------------------------------------ 2.1 partial factors
  {
    const B = b('2.1');
    const S = new Scene(B.start, B.end);
    clause('NORSOK N-001 · NORSOK N-004 · U-001 Table A.2', B.start + 0.3, B.end);
    S.div('LOAD AND RESISTANCE FACTOR DESIGN', { x: 110, y: 150, cls: 'kicker' }).in(c('2.1', 'lrfd') - 0.3, 0.6, 'left');
    const eq = S.eq('\\p{sd}{S_d = \\gamma_f\\,S_k} \\;\\p{le}{\\le}\\; \\p{rd}{R_d = \\dfrac{R_k}{\\gamma_M}}', { x: 960, y: 300, size: 64, o: 1 });
    eq.build(['sd', 'le', 'rd'], c('2.1', 'lrfd'), 0.9, 0.6);
    eq.hl('sd', c('2.1', 'load'), { hold: 6, color: COL.coral });
    eq.hl('rd', c('2.1', 'res'), { hold: 6, color: COL.green });
    const tb = table(S, ['Limit state', 'Riser loads × γ<sub>f</sub>', 'Material factor γ<sub>M</sub>'],
      [['ULS · Table A.2 case K (extreme)', '1.3', '1.15'], ['ALS · Table A.2 case L (accidental)', '1.0', '1.0'], ['SLS · relative displacement', '1.0', '—']],
      { x: 430, y: 470, w: 1060, t: c('2.1', 'load') + 0.4, stagger: 1.2, colCls: ['l', '', ''] });
    tb.el.style.fontSize = '27px';
    later(() => {
      // the material factor column is hidden until 'res'
      const cells = [...tb.el.querySelectorAll('tbody tr td:nth-child(3), thead th:nth-child(3)')];
      for (const el of cells) { const a = S.track(new Actor(el, { o: 0 })); a.in(c('2.1', 'gm'), 0.5, 'none'); }
    });
    const n1 = S.div('load factors per NORSOK N-001, as listed in U-001 Table A.2', { x: 960, y: 760, cls: 'small', anchor: 'ct' });
    n1.in(c('2.1', 'load') + 3, 0.5);
    const n2 = S.div('material factors: NORSOK N-004 (ULS) and N-001 (ALS)', { x: 960, y: 805, cls: 'small c-green', anchor: 'ct' });
    n2.in(c('2.1', 'gm') + 0.8, 0.5);
    note(S, 'Factors as used in Norwegian offshore practice; confirm them in the editions of your design basis', { t0: c('2.1', 'gm') + 1.5, t1: B.end - 0.4 });
  }

  // ------------------------------------------------------------------ 2.2 the yield strength, the Eurocode way
  {
    const B = b('2.2');
    const S = new Scene(B.start, B.end);
    clause('EN 1993-1-1 3.2.1 · EN 10025-2 · S355', B.start + 0.3, B.end);
    const chs = S.chart({ x: 900, y: 180, w: 900, h: 620, xmin: 0, xmax: 1.2, ymin: 0, ymax: 450, xticks: [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2], yticks: [0, 100, 200, 300, 400],
      xfmt: (v) => v.toFixed(1), xlabel: 'Strain · %', ylabel: 'Stress · MPa', title: 'S355 PLATE · TENSILE TEST (SCHEMATIC)' });
    chs.show(c('2.2', 's355') - 0.4);
    const Es = 210000;
    const plateau = [[0, 0], [362 / Es * 100, 362], [0.19, 347], [0.24, 345], [1.2, 346]];
    chs.curve(plateau, { color: COL.amber, width: 5, t: c('2.2', 's355'), d: 1.4 });
    const ln = S.path(`M${chs.X(0)},${chs.Y(345)} L${chs.X(1.2)},${chs.Y(345)}`, { stroke: '#ffffff', width: 2, dash: '5 7' });
    ln.in(c('2.2', 'reh') - 0.2, 0.5, 'none');
    const r1 = S.div('upper yield strength R<sub>eH</sub> ≥ f<sub>y</sub> = <span class="num">345</span> MPa', { x: chs.X(0.30), y: chs.Y(345) - 46, cls: 'label' });
    r1.in(c('2.2', 'reh'), 0.5, 'left');
    // a steel without a distinct yield point: rounded curve, 0.2 % offset line
    const ro = [];
    for (let s = 0; s <= 430; s += 5) ro.push([(s / Es + 0.002 * Math.pow(s / 345, 14)) * 100, s]);
    chs.curve(ro.filter(([x]) => x <= 1.2), { color: '#9fb2c2', width: 3.5, dash: '8 6', t: c('2.2', 'rp'), d: 0.8 });
    const off = S.path(`M${chs.X(0.2)},${chs.Y(0)} L${chs.X(0.2 + 400 / Es * 100)},${chs.Y(400)}`, { stroke: COL.cyan, width: 3 });
    off.set(0, { draw: 0 }).to(c('2.2', 'rp') + 0.6, 0.8, { draw: 1 }).in(c('2.2', 'rp') + 0.6, 0.01, 'none');
    const r2 = S.div('no distinct yield point → R<sub>p0.2</sub> at the 0.2 % offset', { x: chs.X(0.45), y: chs.Y(200), cls: 'label c-cyan' });
    r2.in(c('2.2', 'rp') + 1.2, 0.5, 'left');
    chs.dot(0.2 + 345 / Es * 100, 345, { color: COL.cyan, r: 9, t: c('2.2', 'rp') + 1.3 });
    const ey = 345 / Es * 100;
    const eyl = S.path(`M${chs.X(ey)},${chs.Y(0)} L${chs.X(ey)},${chs.Y(345)}`, { stroke: COL.green, width: 2.5, dash: '4 5' });
    eyl.in(c('2.2', 'ey'), 0.4, 'none');
    const eyt = S.div(`ε<sub>y</sub> = f<sub>y</sub>/E = <span class="num">${ey.toFixed(2)}</span> %`, { x: chs.X(ey) + 12, y: chs.Y(60), cls: 'label c-green', anchor: 'lm' });
    eyt.in(c('2.2', 'ey') + 0.2, 0.5, 'left');
    // left: the nominal values
    const tb = table(S, ['S355 · thickness t', 'f<sub>y</sub> · MPa'], [['t ≤ 16 mm', '355'], ['16 < t ≤ 40 mm', '345'], ['40 < t ≤ 63 mm', '335']],
      { x: 110, y: 200, w: 600, t: c('2.2', 's355') + 0.4, stagger: 0.25, colCls: ['l', ''], title: 'Nominal yield strength · EN 10025-2' });
    later(() => { tb.rows[1].el.classList.add('hi'); });
    quoteCard(S, 'EN 1993-1-1 · 3.2.1', 'f<sub>y</sub> = R<sub>eH</sub> and f<sub>u</sub> = R<sub>m</sub>, taken directly from the <span class="q">product standard</span>',
      { x: 110, y: 520, w: 600, t: c('2.2', 'reh') + 0.6, size: 27 });
    const same = S.card('<div style="font-weight:750;font-size:28px">The same idea as the <span class="c-amber">0.2 % offset</span></div><div class="small" style="font-size:22px">yielding starts at a strain of about 0.16 %</div>',
      { x: 110, y: 760, w: 600, cls: 'glass' });
    same.in(c('2.2', 'same'), 0.6, 'rise');
  }

  // ------------------------------------------------------------------ 2.3 the elastic check on the slot ring
  {
    const B = b('2.3');
    const panel = { x: 820, y: 130, w: 1060, h: 800 };
    const tR = c('2.3', 'ring'), tC = c('2.3', 'contour');
    const cam = camSpline([
      { t: tR - 0.8, p: [1.45, 2.35, 2.75], l: [0.3, 0.32, 0.0], fov: 32 },
      { t: c('2.3', 'peak') + 0.6, p: [1.2, 1.8, 2.05], l: [0.42, 0.36, 0.12], fov: 32 },
      { t: B.end, p: [1.15, 1.75, 2.0], l: [0.42, 0.36, 0.12], fov: 32 },
    ]);
    const alpha = (t) => smooth(t, tR + 1.5, tC + 1.0);
    const DEFS = 60;                                                     // displacement exaggeration
    let fNow = null;
    W3.shot(tR - 0.8, B.end, {
      show: ['feRing'], panel, fadeIn: 0.8, fadeOut: 0.6, cam, fog: 0, bg: '#0b1824',
      update: (t) => {
        fNow = ringState(D, 'el', alpha(t), DEFS);
        RINGU.uRMode.value = 0; RINGU.uRVmax.value = 450; RINGU.uRBands.value = 9;
        RINGU.uRF.value = smooth(t, tC - 0.6, tC + 0.6);
        md.feRing.userData.lines.material.opacity = 0.35;
      },
      key: (t) => (t < tC + 1.2 ? t.toFixed(3) : 'k'),
    });
    const S = new Scene(B.start, B.end);
    clause('EN 1993-1-1 · 6.2.1(5) · formula (6.1)', B.start + 0.3, B.end);
    S.div('THE ELASTIC CHECK · EN 1993-1-1', { x: 100, y: 150, cls: 'kicker' }).in(B.start + 0.3, 0.6, 'left');
    const e1 = S.eq('\\left(\\tfrac{\\sigma_{x,Ed}}{f_y/\\gamma_{M0}}\\right)^{2}+\\left(\\tfrac{\\sigma_{z,Ed}}{f_y/\\gamma_{M0}}\\right)^{2}-\\left(\\tfrac{\\sigma_{x,Ed}}{f_y/\\gamma_{M0}}\\right)\\!\\left(\\tfrac{\\sigma_{z,Ed}}{f_y/\\gamma_{M0}}\\right)+3\\left(\\tfrac{\\tau_{Ed}}{f_y/\\gamma_{M0}}\\right)^{2}\\le 1',
      { x: 100, y: 250, size: 25, align: 'left' });
    e1.in(c('2.3', 'vm'), 0.9, 'write');
    const e2 = S.eq('\\sigma_{vM,Ed} \\;\\le\\; \\frac{f_y}{\\gamma_{M0}} = \\frac{345}{1.15} = \\cg{300\\ \\mathrm{MPa}}', { x: 100, y: 360, size: 40, align: 'left' });
    e2.in(c('2.3', 'vm') + 3.0, 0.8, 'write');
    S.div('von Mises at the critical point · elastic analysis', { x: 100, y: 430, cls: 'small' }).in(c('2.3', 'vm') + 3.5, 0.5);
    const inp = S.card(`<div class="ref">SLOT RING D · TEACHING MODEL</div><div class="small" style="font-size:21px;line-height:1.5">S355 · 40 mm plate · inner radius ${Math.round(I.ri * 1000)} mm · width ${Math.round(I.w * 1000)} mm<br>4 struts, pinned · contact ±${I.spread_deg}° between two struts<br>design contact force <span class="c-amber num">${I.PD}</span> MN (ULS, load factor included)</div>`,
      { x: 100, y: 500, w: 680, cls: 'glass' });
    inp.in(tR + 0.3, 0.6, 'rise');
    stressLegend(S, { x: 1620, y: 190, t0: tC + 0.2, t1: B.end - 0.4 });
    const thc = EL.crit.theta_deg;
    probe3D(S, () => ringPoint(thc, I.ro, RING_D.y1, fNow, DEFS), `<span style="font-size:40px;font-weight:800;color:#ff5a4a" class="num">${Math.round(EL.sigma_d)} MPa</span><span class="sub">outer edge behind the contact</span>`,
      { t0: c('2.3', 'peak'), t1: B.end, dx: 130, dy: 150, color: '#ff5a4a' });
    const u = S.eq(`\\frac{${Math.round(EL.sigma_d)}}{300} = ${EL.util.toFixed(2)}`, { x: 100, y: 740, size: 52, align: 'left' });
    u.in(c('2.3', 'util'), 0.7, 'write');
    stamp(S, 'fails', { x: 580, y: 740, t: c('2.3', 'fail'), kind: 'fail', size: 30 });
    const but = S.div('…but it stops at the <span class="c-amber">first point that yields</span>', { x: 100, y: 850, cls: 'h3', style: 'font-size:30px' });
    but.in(c('2.3', 'but'), 0.6, 'rise');
    note(S, `Ring analysed with a fibre beam model (linear elastic here); displacements ×${DEFS}`, { t0: tC + 1, t1: B.end - 0.4 });
  }
}
