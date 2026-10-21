// Chapter 5 — the conductor in the soil: beam on an elastic (Winkler) foundation, solution, boundary conditions, max moment.
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt } from '../engine/core.js';
import { Scene } from '../engine/scene.js';
import { titleCard, clause, step } from '../engine/hud.js';
import { camPath, DEF, setProfile, THREE } from '../three/world.js';
import { updateSnow } from '../three/models.js';
import { quoteCard, derivation, table, tx, label3D } from './kit.js';
import { springPath, ground } from './drawings.js';

export async function build(E, T, D) {
  const ch = T.ch(5);
  titleCard(ch, 'Below the mudline the conductor is a beam on springs');
  step(ch.title_card[1], 2);
  const W3 = E.world, md = W3.models, M = W3.M;
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const bef = D.bef, k5 = bef.cases['5'];

  // ------------------------------------------------------------------ 5.1 Winkler foundation and the ODE
  {
    const B = b('5.1');
    const S = new Scene(B.start, B.end);
    clause('Beam on an elastic foundation (Winkler, Hetényi)', B.start + 0.3, B.end);
    const x0 = 360, yM = 260, yB = 960, beta = 0.147, Lpx = (yB - yM) / 30;   // 30 m shown
    const defl = (zm) => { const bx = beta * zm; return Math.exp(-bx) * (Math.cos(bx) - 0.35 * Math.sin(bx)); };
    const amp = (t) => 70 * smooth(t, c('5.1', 'bed') + 0.4, c('5.1', 'bed') + 2.2);
    const gr = ground(S, 120, 640, yM); gr.in(B.start + 0.2, 0.5, 'none');
    S.rect(120, yM, 520, yB - yM, { fill: 'url(#soilpat)', stroke: 'none', opacity: 0.55 }).in(B.start + 0.2, 0.5, 'none');
    const beam = S.path('', { stroke: '#c7d6e2', width: 22, cap: 'butt' }); beam.in(B.start + 0.3, 0.5, 'none');
    const springsL = [], springsR = [];
    for (let i = 0; i < 9; i++) { const sL = S.path('', { stroke: COL.soil, width: 3 }), sR = S.path('', { stroke: COL.soil, width: 3 }); sL.in(c('5.1', 'bed'), 0.5, 'none'); sR.in(c('5.1', 'bed'), 0.5, 'none'); springsL.push(sL); springsR.push(sR); }
    const P = S.arrow(x0 - 200, yM - 40, x0 - 20, yM - 40, { color: COL.amber, width: 5 }); P.in(c('5.1', 'bed') + 0.2, 0.4, 'none');
    S.eq('P,\\;\\cm{M_0}', { x: x0 - 220, y: yM - 40, size: 36, align: 'right' }).in(c('5.1', 'bed') + 0.2, 0.4, 'none');
    E.anim(B.start, B.end, (t) => {
      const a = amp(t);
      let d = '';
      for (let i = 0; i <= 60; i++) { const zm = 30 * i / 60; d += `${i ? 'L' : 'M'}${(x0 + a * defl(zm)).toFixed(1)},${(yM - 40 + (yB - yM + 40) * i / 60).toFixed(1)}`; }
      beam.el.setAttribute('d', d);
      for (let i = 0; i < 9; i++) {
        const zm = 1.5 + i * 2.6, y = yM + zm * Lpx, xb = x0 + a * defl(zm);
        springsL[i].el.setAttribute('d', rotSpring(140, y, xb - 14, y));
        springsR[i].el.setAttribute('d', rotSpring(xb + 14, y, 620, y));
      }
    });
    // slice free body
    const sl = S.card('', { x: 760, y: 560, w: 300, h: 360 }); sl.in(c('5.1', 'shear') - 0.4, 0.5);
    const sg = S.g(); sg.in(c('5.1', 'shear') - 0.3, 0.5, 'none');
    S.rect(880, 640, 60, 200, { fill: '#8fa3b5', stroke: COL.ink2, width: 2, parent: sg.el, o: 1 });
    S.arrow(990, 640, 945, 640, { color: COL.cyan, width: 3, parent: sg.el, o: 1 }); S.arrow(830, 840, 875, 840, { color: COL.cyan, width: 3, parent: sg.el, o: 1 });
    S.svgText('V', 1000, 620, { size: 26, fill: COL.cyan, parent: sg.el, o: 1, family: 'KaTeX_Math' });
    S.svgText('V + dV', 810, 870, { size: 22, fill: COL.cyan, parent: sg.el, o: 1 });
    for (let k = 0; k < 5; k++) S.arrow(800, 670 + k * 36, 870, 670 + k * 36, { color: COL.soil, width: 2.5, parent: sg.el, o: 1 });
    S.svgText('k y dz', 790, 600, { size: 22, fill: COL.soil, parent: sg.el, o: 1 });
    const st = derivation(S, [
      { tex: '\\dfrac{\\dd V}{\\dd z} = -k\\,y', t: c('5.1', 'shear'), note: 'slice equilibrium', x: 1180, align: 'left' },
      { tex: '\\dfrac{\\dd \\cm M}{\\dd z} = V', t: c('5.1', 'mom'), note: 'moment balance', x: 1180, align: 'left' },
      { tex: '\\cm M = -EI\\,\\dfrac{\\dd^2 y}{\\dd z^2}', t: c('5.1', 'ei'), note: 'beam bending', x: 1180, align: 'left' },
      { tex: 'EI\\,\\dfrac{\\dd^4 y}{\\dd z^4} + k\\,y = 0', t: c('5.1', 'ode'), x: 1180, align: 'left', size: 58 },
    ], { y0: 260, gap: 165, size: 46, noteAbove: true });
    st[3].boxed(c('5.1', 'ode') + 1.6);
  }

  // ------------------------------------------------------------------ 5.2 solving the equation
  {
    const B = b('5.2');
    const S = new Scene(B.start, B.end);
    const st = derivation(S, [
      { tex: 'y = e^{\\lambda z}\\;\\Rightarrow\\; EI\\,\\lambda^4 + k = 0', t: c('5.2', 'char'), x: 120, align: 'left' },
      { tex: '\\beta = \\left(\\dfrac{k}{4EI}\\right)^{1/4},\\qquad \\lambda^4 = -4\\beta^4', t: c('5.2', 'beta'), x: 120, align: 'left' },
      { tex: '\\lambda = \\beta\\,(\\pm 1 \\pm i)', t: c('5.2', 'beta') + 2.5, x: 120, align: 'left' },
      { tex: 'y = e^{-\\beta z}\\left(C_1\\cos\\beta z + C_2 \\sin\\beta z\\right)', t: c('5.2', 'decay'), x: 120, align: 'left', size: 52 },
    ], { y0: 260, gap: 150, size: 48 });
    st[3].boxed(c('5.2', 'len') - 0.4);
    // complex plane with four roots
    const cx = 1500, cy = 520, R = 150;
    const ax = S.g(); ax.in(c('5.2', 'beta') + 2.0, 0.5, 'none');
    S.arrow(cx - 260, cy, cx + 260, cy, { color: COL.dim, width: 2, parent: ax.el, o: 1 }); S.arrow(cx, cy + 260, cx, cy - 260, { color: COL.dim, width: 2, parent: ax.el, o: 1 });
    S.svgText('Re', cx + 270, cy + 24, { size: 20, parent: ax.el, o: 1 }); S.svgText('Im', cx + 26, cy - 262, { size: 20, parent: ax.el, o: 1 });
    const roots = [[-1, 1], [-1, -1], [1, 1], [1, -1]];
    roots.forEach(([re, im], i) => {
      const keep = re < 0;
      const d = S.circle(cx + re * R, cy - im * R, 14, { fill: keep ? COL.green : COL.red, stroke: '#06121c', width: 2 });
      d.in(c('5.2', 'beta') + 2.6 + i * 0.2, 0.4, 'pop');
      if (!keep) { const x = S.path(`M${cx + re * R - 20},${cy - im * R - 20} L${cx + re * R + 20},${cy - im * R + 20} M${cx + re * R + 20},${cy - im * R - 20} L${cx + re * R - 20},${cy - im * R + 20}`, { stroke: COL.red, width: 4 }); x.in(c('5.2', 'decay'), 0.4, 'none'); }
    });
    S.div('decaying: keep', { x: cx - R, y: cy + 210, cls: 'small', anchor: 'ct', style: 'color:#46d39a' }).in(c('5.2', 'decay'), 0.5);
    S.div('growing: drop', { x: cx + R, y: cy + 210, cls: 'small', anchor: 'ct', style: 'color:#ff4d5e' }).in(c('5.2', 'decay'), 0.5);
    S.div('1/β = the length over which the conductor “feels” the soil', { x: 120, y: 900, cls: 'body', w: 1200 }).in(c('5.2', 'len'), 0.6);
  }

  // ------------------------------------------------------------------ 5.3 boundary conditions
  {
    const B = b('5.3');
    const S = new Scene(B.start, B.end);
    clause('stick-up hands over M₀ = M_w (1 + h/H) and P = Q_w at the mudline', B.start + 0.3, B.end);
    const st = derivation(S, [
      { tex: '\\cm M(0) = -EI\\,y\\,\\!\'\'(0) = \\cm{M_0} \\;\\Rightarrow\\; C_2 = \\dfrac{\\cm{M_0}}{2EI\\beta^2}', t: c('5.3', 'm0'), x: 140, align: 'left' },
      { tex: 'V(0) = -EI\\,y\\,\\!\'\'\'(0) = P \\;\\Rightarrow\\; C_1 = -\\dfrac{P}{2EI\\beta^3} - C_2', t: c('5.3', 'm0') + 3.5, x: 140, align: 'left' },
      { tex: '\\cm M(x) = \\cm{M_0}\\,e^{-\\beta x}\\left(\\cos\\beta x+\\sin\\beta x\\right) + \\dfrac{P}{\\beta}\\,e^{-\\beta x}\\sin\\beta x', t: c('5.3', 'result'), x: 140, align: 'left', size: 50 },
    ], { y0: 300, gap: 170, size: 46 });
    st[2].boxed(c('5.3', 'result') + 2.4);
    const mo = S.eq('\\cm{M_0} = \\cm{M_w}\\left(1+\\dfrac{4}{13.7}\\right) = 1.29\\,\\cm{M_w},\\qquad P = \\dfrac{\\cm{M_w}}{13.7\\text{ m}}', { x: 960, y: 880, size: 40 });
    mo.in(c('5.3', 'm0') + 1.0, 0.7, 'write');
  }

  // ------------------------------------------------------------------ 5.4 maximum moment + chart
  {
    const B = b('5.4');
    const S = new Scene(B.start, B.end);
    const e1 = S.eq('\\dfrac{\\dd \\cm M}{\\dd x} = 0 \\;\\Rightarrow\\; \\tan\\beta x_{\\max} = \\dfrac{P}{2\\beta \\cm{M_0} + P}', { x: 1340, y: 230, size: 44 });
    e1.in(c('5.4', 'tan'), 0.8, 'write');
    const cc = S.chart({ x: 200, y: 190, w: 640, h: 760, xmin: 0, xmax: 1.5, ymin: 40, ymax: 0, xticks: [0, 0.5, 1.0, 1.5], yticks: [0, 10, 20, 30, 40], xfmt: (v) => v.toFixed(1), yfmt: (v) => v + ' m', xlabel: 'M(x) / M<sub>w</sub>', title: 'DEPTH BELOW MUDLINE' });
    cc.show(B.start + 0.3);
    const cols = { 1: COL.violet, 5: COL.amber, 20: COL.cyan };
    for (const k of ['1', '5', '20']) {
      const cs = bef.cases[k];
      const pts = cs.x.map((x, i) => [Math.abs(cs.M[i]), x]);
      cc.curve(pts, { color: cols[k], width: k === '5' ? 6 : 3.5, t: k === '5' ? c('5.4', 'tan') + 0.6 : c('5.4', 'soft') + (k === '1' ? 0 : 0.4) });
      const xl = S.div(`k = ${k} MPa`, { x: cc.X(Math.abs(cs.M[20])) + 14, y: cc.Y(cs.x[20]), cls: 'tiny', anchor: 'lm', style: `color:${cols[k]}` });
      xl.in(k === '5' ? c('5.4', 'num') : c('5.4', 'soft') + 0.4, 0.5);
    }
    const mx = cc.dot(k5.M_max, k5.x_max, { color: COL.coral, r: 11, t: c('5.4', 'num') });
    const tb = table(S, ['k = 5 MPa', ''], [
      ['β', `${k5.beta.toFixed(3)} 1/m`], ['1/β', `${k5.L_char.toFixed(1)} m`],
      ['M<sub>max</sub>', `${k5.M_max.toFixed(2)} M<sub>w</sub>`], ['at depth', `${k5.x_max.toFixed(1)} m`],
    ], { x: 1000, y: 360, w: 520, t: c('5.4', 'num'), colCls: ['l', ''] });
    const kt = S.eq('\\cy{k_{\\theta,W}} = EI\\,\\beta \\approx ' + fmt(k5.k_theta_free / 1e6) + '\\ \\tfrac{\\text{MNm}}{\\text{rad}}', { x: 1000, y: 760, size: 46, align: 'left' });
    kt.in(c('5.4', 'ktheta'), 0.8, 'write');
    const cmp = S.div(`vs template ≈ 533 MNm/rad → template would take ≈ ${(100 * 533 / (533 + k5.k_theta_free / 1e6)).toFixed(0)} % without a gap`, { x: 1000, y: 850, w: 820, cls: 'small' });
    cmp.in(c('5.4', 'compare'), 0.6);
  }

  // ------------------------------------------------------------------ 5.5 reality check: nonlinear p-y curves
  {
    const B = b('5.5');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · J.2.2 · B.4.2.4', B.start + 0.3, B.end);
    const tp = c('5.5', 'py');
    const cc = S.chart({ x: 200, y: 230, w: 680, h: 560, xmin: 0, xmax: 50, ymin: 0, ymax: 500, xticks: [0, 10, 20, 30, 40, 50], yticks: [0, 100, 200, 300, 400, 500],
      xlabel: 'lateral displacement y [mm]', ylabel: 'soil resistance p [kN/m]', title: 'ILLUSTRATIVE p–y CURVES' });
    cc.show(tp - 0.2);
    // p = pu tanh(k y / pu): capacity and initial stiffness grow with depth; cycling lowers the capacity
    const pyc = (pu, k) => { const pts = []; for (let i = 0; i <= 60; i++) { const y = 50 * i / 60; pts.push([y, pu * Math.tanh(k * y / pu)]); } return pts; };
    const set = [[2, 150, 20, '#7fc8ff'], [6, 300, 40, COL.cyan], [12, 450, 60, '#2f9fd8']];
    set.forEach(([z, pu, k, col], i) => {
      cc.curve(pyc(pu, k), { color: col, width: 4, t: tp + 0.4 + i * 0.5, d: 1.0 });
      S.div(`z = ${z} m`, { x: cc.X(50) + 12, y: cc.Y(pu * Math.tanh(k * 50 / pu)), cls: 'small', anchor: 'lm', style: `color:${col}` }).in(tp + 1.2 + i * 0.5, 0.4);
    });
    const tcy = T.w('5.5', 'cycling');
    cc.curve(pyc(0.72 * 300, 40), { color: COL.coral, width: 4, dash: '10 8', t: tcy - 0.2, d: 1.0 });
    S.div('z = 6 m after cycling', { x: cc.X(49), y: cc.Y(0.72 * 300) + 26, cls: 'small', anchor: 'rm', style: 'color:#ff6f61' }).in(tcy + 0.5, 0.4);
    S.div('↑ stiffer and stronger with depth', { x: cc.X(24), y: cc.Y(378), cls: 'tiny', anchor: 'lm', style: 'color:#4fd1ff' }).in(tp + 2.6, 0.5);
    const card = (y, title, body, col, t) => { const a = S.card(`<div style="font-weight:750;font-size:30px;color:${col}">${title}</div><div class="small">${body}</div>`, { x: 1120, y, w: 700 }); a.in(t, 0.6, 'left'); return a; };
    card(220, 'Driven', 'best contact between the soil and the conductor', COL.green, c('5.5', 'driven'));
    card(360, 'Drilled and driven', 'still a very good interface', COL.amber, c('5.5', 'driven') + 0.8);
    card(500, 'Drilled hole, cemented', 'least predictable interface, poorest horizontal support', COL.red, c('5.5', 'cemented'));
    const py = S.div('<b>Real soil:</b> nonlinear p–y curves, stiffer with depth, softer under cycling', { x: 1120, y: 680, w: 700, cls: 'body' });
    py.in(c('5.5', 'py'), 0.6);
    const fe = S.card('<div class="ref">B.4.2.4</div><div class="small">Local response model · fatigue capacity for a <b class="c-amber">range of parameters</b> (cement shortfall, hang-off weights, friction, tolerances, radial clearances).</div>', { x: 1120, y: 820, w: 700 });
    fe.in(c('5.5', 'fe'), 0.6);
  }
}

// horizontal spring between two points
function rotSpring(x0, y, x1, y1) {
  const n = 10, L = x1 - x0;
  let d = `M${x0},${y} L${x0 + L * 0.15},${y}`;
  for (let i = 0; i <= n; i++) { const xx = x0 + L * 0.15 + L * 0.7 * i / n; const yy = y + (i === 0 || i === n ? 0 : (i % 2 ? 9 : -9)); d += ` L${xx.toFixed(1)},${yy.toFixed(1)}`; }
  return d + ` L${x1},${y}`;
}
