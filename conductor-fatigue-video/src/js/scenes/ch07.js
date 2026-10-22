// Chapter 7 — building the M-N curve (B.4.2 and B.4.4).
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt } from '../engine/core.js';
import { Scene } from '../engine/scene.js';
import { titleCard, clause, step } from '../engine/hud.js';
import { quoteCard, derivation, table, tx } from './kit.js';
import { springPath, ground } from './drawings.js';
import { snCurve, mnCurve, mnN, logTicks, pow10 } from './fatigue.js';

const sciS = (x) => { const e = Math.floor(Math.log10(x)); return `${(x / 10 ** e).toFixed(2)}×10<sup>${e}</sup>`; };

export async function build(E, T, D) {
  const ch = T.ch(7);
  titleCard(ch, 'Step 3 and step 5 · from a local response model to M-N curves (B.4.2, B.4.4)');
  step(ch.title_card[1], 4);
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const ex = D.example, pts = ex.points, gw = ex.mn_gw, ts = ex.mn_T;

  // ------------------------------------------------------------------ 7.1 why M-N
  {
    const B = b('7.1');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.4.2.1', B.start + 0.3, B.end);
    const mk = (x, ttl, yl, col, t, curve) => {
      const cc = S.chart({ x, y: 280, w: 620, h: 460, xlog: true, ylog: true, xmin: 1e4, xmax: 1e9, ymin: curve.ymin, ymax: curve.ymax, xticks: logTicks(1e4, 1e9), yticks: curve.yt, xfmt: pow10, yfmt: (v) => fmt(v), xlabel: 'cycles to failure N', ylabel: yl, ylabelDx: curve.dx || 76, title: ttl });
      cc.show(t); cc.curve(curve.pts, { color: col, width: 5, t: t + 0.4 }); return cc;
    };
    mk(220, 'S-N · STRESS AT THE HOT SPOT', 'Δσ [MPa]', COL.coral, B.start + 0.3, { pts: snCurve(D.sn.C1_CP), ymin: 10, ymax: 1000, yt: [10, 100, 1000] });
    mk(1180, 'M-N · MOMENT AT THE WH DATUM', 'ΔM [kNm]', COL.amber, c('7.1', 'mn'), { pts: mnCurve(gw), ymin: 100, ymax: 10000, yt: [100, 1000, 10000], dx: 104 });
    const ar = S.arrow(880, 510, 1040, 510, { color: COL.ink2, width: 5 }); ar.in(c('7.1', 'mn'), 0.5, 'none');
    S.div('same datum as the load histogram', { x: 1490, y: 880, cls: 'h3', anchor: 'ct', style: 'color:#ffb547' }).in(c('7.1', 'why'), 0.7, 'write');
  }

  // ------------------------------------------------------------------ 7.2 linear transfer derivation
  {
    const B = b('7.2');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · formulas (B.8) and (B.9)', B.start + 0.3, B.end);
    const st = derivation(S, [
      { tex: '\\Ds = \\kappa\\,\\DM', t: c('7.2', 'lin'), note: 'if stress ∝ moment' },
      { tex: '\\cn N = \\bar a_{\\sigma}\\,\\left(\\kappa\\,\\DM\\right)^{-\\cv m}', t: c('7.2', 'lin') + 2.4, note: 'S-N curve' },
      { tex: '\\cn N = \\underbrace{\\left(\\bar a_{\\sigma}\\,\\kappa^{-\\cv m}\\right)}_{\\bar a_{\\Delta M}}\\,\\DM^{-\\cv m}', t: c('7.2', 'group'), note: 'group constants', size: 54 },
      { tex: '\\cn N = \\bar a_{\\Delta M}\\,\\DM^{-\\cv m} \\qquad \\log \\cn N = \\log\\bar a_{\\Delta M} - \\cv m \\log \\DM', t: c('7.2', 'b8'), note: '(B.8), (B.9)', size: 48 },
    ], { y0: 260, gap: 170, size: 52 });
    st[3].boxed(c('7.2', 'b8') + 1.8);
    const n = S.div('same slope m · only the intercept moves: log ā<sub>ΔM</sub> = log ā<sub>σ</sub> − m log κ', { x: 960, y: 960, cls: 'body', anchor: 'cm', style: 'color:#e9f2f9' });
    n.in(c('7.2', 'b8') + 2.6, 0.6);
  }

  // ------------------------------------------------------------------ 7.3 nonlinear transfer functions
  {
    const B = b('7.3');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.4.1 (nonlinear relation, FEA)', B.start + 0.3, B.end);
    const tr = D.transfer;
    // zoomed on the low moments where the contacts change state: the gap closes at ~160 kNm
    const cc = S.chart({ x: 220, y: 200, w: 1000, h: 640, xmin: 0, xmax: 2000, ymin: 0, ymax: 80, xticks: [0, 500, 1000, 1500, 2000], yticks: [0, 20, 40, 60, 80], xfmt: (v) => fmt(v), yfmt: String,
      xlabel: 'WH moment range ΔM<sub>w</sub> [kNm]', ylabel: 'hot-spot stress range [MPa]' });
    cc.show(B.start + 0.3);
    const k0 = tr[0].ds_gw / tr[0].dM;
    cc.curve([[0, 0], [2000, k0 * 2000]], { color: COL.dim, width: 2, dash: '8 8', t: c('7.3', 'nonlin') });
    S.div('proportional', { x: cc.X(900) - 4, y: cc.Y(k0 * 900) - 10, cls: 'tiny', anchor: 'rb' }).in(c('7.3', 'nonlin') + 0.6, 0.5);
    cc.curve([[0, 0], ...tr.map((p) => [p.dM, p.ds_gw])], { color: COL.amber, width: 5, t: c('7.3', 'gwcurve') });
    cc.curve([[0, 0], ...tr.map((p) => [p.dM, p.ds_T])], { color: COL.lemon, width: 5, t: c('7.3', 'tscurve') });
    // legend in the empty lower right
    [['GW1 · conductor girth weld', COL.amber, 19, 'gwcurve'], ['TS1 · template slot weld', COL.lemon, 11, 'tscurve']].forEach(([txt, col, yv, cue]) => {
      S.path(`M${cc.X(1170)},${cc.Y(yv)} L${cc.X(1270)},${cc.Y(yv)}`, { stroke: col, width: 5 }).in(c('7.3', cue) + 0.8, 0.5, 'none');
      S.div(txt, { x: cc.X(1270) + 14, y: cc.Y(yv), cls: 'small', anchor: 'lm', style: `color:${col}` }).in(c('7.3', cue) + 0.8, 0.5);
    });
    const gap0 = 161;
    const gapz = S.rect(cc.X(0), cc.y, cc.X(gap0) - cc.X(0), cc.h, { fill: 'rgba(255,230,109,0.10)', stroke: 'none' }); gapz.in(c('7.3', 'tscurve') + 0.5, 0.5, 'none');
    S.div('← gap open: TS1 carries nothing', { x: cc.X(gap0) + 12, y: cc.Y(70), cls: 'tiny', anchor: 'lm', style: `color:${COL.lemon}` }).in(c('7.3', 'tscurve') + 0.6, 0.5);
    quoteCard(S, 'B.4.1', 'For connectors and wellheads there may be a <span class="q">nonlinear relation between load and stress</span>, finite element analysis shall be used to determine fatigue stress ranges at fatigue critical region(s).', { x: 1300, y: 260, w: 500, t: c('7.3', 'nonlin'), size: 25 });
  }

  // ------------------------------------------------------------------ 7.4 the procedure a)-f)
  {
    const B = b('7.4');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.4.2.4 a) – f)', B.start + 0.3, B.end);
    const items = [
      ['a', '3D elastic model: contacts, boundary conditions, fine mesh, shoulder preload, cement shortfall, down weights, friction, tolerances, radial clearances'],
      ['b', 'apply M<sub>w,i</sub> and Q<sub>w,i</sub> = M<sub>w,i</sub> / H<sub>LFJ</sub> at the wellhead datum'],
      ['c', 'fully reversed, R = −1: apply +M then −M; ΔM = 2M, ΔQ = 2M / H<sub>LFJ</sub>; stress range at each hot spot; iterate to convergence'],
      ['d', 'cycles to failure N<sub>i</sub> from the S-N curve for the environment'],
      ['e', 'report N<sub>i</sub> versus ΔM<sub>w,i</sub> for each hot spot'],
      ['f', 'repeat until 10<sup>4</sup> – 10<sup>8</sup> cycles are covered · e.g. 6000, 3000, 1500, 750, 375, 187.5 kNm'],
    ];
    items.forEach(([k, txt], i) => {
      const a = S.div(`<div style="display:flex;gap:22px;align-items:flex-start"><div style="flex:none;width:52px;height:52px;border-radius:14px;background:#4fd1ff;color:#06121c;font-weight:800;font-size:28px;display:flex;align-items:center;justify-content:center">${k}</div><div class="small" style="color:#e9f2f9;font-size:27px;padding-top:6px">${txt}</div></div>`, { x: 840, y: 200 + i * 128, w: 960 });
      a.in(c('7.4', k), 0.5, 'left');
    });
    // a small animated well beam: +M / -M
    const x0 = 420, yT = 260, yG = 640, yB = 960;
    const ph = (t) => Math.sin(2 * Math.PI * (t - c('7.4', 'c')) / 2.4) * smooth(t, c('7.4', 'c') - 0.2, c('7.4', 'c') + 0.6);
    const gr = ground(S, 200, 640, yG); gr.in(B.start + 0.3, 0.5, 'none');
    const beam = S.path('', { stroke: '#c7d6e2', width: 20, cap: 'butt' }); beam.in(B.start + 0.3, 0.5, 'none');
    const mArc = S.path('', { stroke: COL.amber, width: 5 }); mArc.in(c('7.4', 'b'), 0.5, 'none');
    const mLab = S.div('', { x: 0, y: 0, cls: 'h3', style: 'color:#ffb547' }); mLab.in(c('7.4', 'b'), 0.5, 'none');
    E.anim(B.start, B.end, (t) => {
      const a = 60 * (ph(t) || 0);
      let d = '';
      for (let i = 0; i <= 40; i++) { const u = i / 40, y = yT + (yB - yT) * u; const z = (y - yT) / (yB - yT); const shape = Math.exp(-4 * z) * Math.cos(5 * z); d += `${i ? 'L' : 'M'}${(x0 + a * shape).toFixed(1)},${y.toFixed(1)}`; }
      beam.el.setAttribute('d', d);
      const sgn = (ph(t) || 0) >= 0 ? 1 : -1;
      mArc.el.setAttribute('d', `M${x0 - 70},${yT - 10} A70,40 0 1,${sgn > 0 ? 1 : 0} ${x0 + 70},${yT - 10}`);
      mLab.el.innerHTML = Math.abs(ph(t)) < 0.05 ? 'M' : (sgn > 0 ? '+M' : '−M');
      mLab.el.style.left = (x0 + 90) + 'px'; mLab.el.style.top = (yT - 80) + 'px';
    });
  }

  // ------------------------------------------------------------------ 7.5 our local model
  {
    const B = b('7.5');
    const S = new Scene(B.start, B.end);
    clause('simplified local response model (teaching stand-in for the 3D FE model)', B.start + 0.3, B.end);
    const pr = D.profiles.base, z = pr.z;
    const zmax = 24, y0 = 190, y1 = 1000, X0 = 520, sc = (y1 - y0) / zmax;
    const Y = (zz) => y0 + zz * sc;
    const amp = (t) => 2600 * smooth(t, c('7.5', 'springs') + 0.5, c('7.5', 'springs') + 2.0) * Math.cos(2 * Math.PI * (t - c('7.5', 'springs')) / 5);
    const inner = S.path('', { stroke: COL.blue, width: 6 }), outer = S.path('', { stroke: COL.amber, width: 8 });
    inner.in(c('7.5', 'beams'), 0.5, 'none'); outer.in(c('7.5', 'beams') + 0.4, 0.5, 'none');
    const gr = ground(S, X0 - 240, X0 + 240, Y(4.0)); gr.in(c('7.5', 'beams'), 0.5, 'none');
    const sprC = S.path('', { stroke: COL.yellow, width: 3 }), sprD = S.path('', { stroke: COL.yellow, width: 3 });
    sprC.in(c('7.5', 'springs'), 0.5, 'none'); sprD.in(c('7.5', 'springs'), 0.5, 'none');
    const soil = []; for (let k = 0; k < 8; k++) { const s = S.path('', { stroke: COL.soil, width: 2.5 }); s.in(c('7.5', 'springs') + 0.4, 0.5, 'none'); soil.push(s); }
    const cem = S.rect(X0 - 40, Y(9), 80, Y(zmax) - Y(9), { fill: 'url(#cementpat)', stroke: 'none', opacity: 0.6 }); cem.in(c('7.5', 'springs') + 0.6, 0.5, 'none');
    const lbl = (txt, zz, col, t, dx = 260) => S.div(txt, { x: X0 + dx, y: Y(zz), cls: 'small', anchor: 'lm', style: `color:${col}` }).in(t, 0.5);
    lbl('WH + surface casing (inner)', 0.5, COL.blue, c('7.5', 'beams'), 120);
    lbl('conductor housing + conductor (outer)', 6, COL.amber, c('7.5', 'beams') + 0.4, 120);
    lbl('template rings C, D · 2 mm gap', 2.6, COL.yellow, c('7.5', 'springs'), 120);
    lbl('bonded below top of cement E', 11, COL.cement, c('7.5', 'springs') + 0.6, 120);
    lbl('soil springs H', 17, COL.soil, c('7.5', 'springs') + 0.4, 120);
    E.anim(B.start, B.end, (t) => {
      const a = amp(t);
      const path = (v, z0) => { let d = '', f = true; for (let i = 0; i < z.length; i++) { if (z[i] > zmax || z[i] < z0) continue; d += `${f ? 'M' : 'L'}${(X0 + a * v[i]).toFixed(1)},${Y(z[i]).toFixed(1)}`; f = false; } return d; };
      inner.el.setAttribute('d', path(pr.v_in, 0)); outer.el.setAttribute('d', path(pr.v_out, 0.9));
      const vAt = (zz) => { let i = 0; while (i < z.length - 1 && z[i] < zz) i++; return pr.v_out[i]; };
      sprC.el.setAttribute('d', springH(X0 - 220, Y(1.6), X0 + a * vAt(1.6) - 14, Y(1.6)));
      sprD.el.setAttribute('d', springH(X0 - 220, Y(3.6), X0 + a * vAt(3.6) - 14, Y(3.6)));
      soil.forEach((s, k) => { const zz = 5 + k * 2.4; s.el.setAttribute('d', springH(X0 - 200, Y(zz), X0 + a * vAt(zz) - 14, Y(zz))); });
    });
    S.div('deflection exaggerated', { x: 160, y: 990, cls: 'tiny' }).in(c('7.5', 'springs') + 1, 0.5);
    const hn = S.card('<div class="small">Same steps as B.4.2.4: apply ±M with Q = M/H<sub>LFJ</sub>, solve the contacts, read the hot-spot stress ranges.</div>', { x: 1230, y: 820, w: 580 });
    hn.in(c('7.5', 'honest'), 0.6);
  }

  // ------------------------------------------------------------------ 7.6 six points
  {
    const B = b('7.6');
    const S = new Scene(B.start, B.end);
    const rows = pts.map((p) => [fmt(p.dM, p.dM % 1 ? 1 : 0), p.ds_gw.toFixed(1), sciS(p.N_gw), fmt(p.dF_C), p.ds_T.toFixed(1), p.N_T ? sciS(p.N_T) : '∞']);
    const tb = table(S, ['ΔM<sub>w</sub> [kNm]', 'Δσ GW1', 'N GW1', 'ΔF<sub>C</sub> [kN]', 'Δσ TS1', 'N TS1'], rows, { x: 100, y: 210, w: 900, t: c('7.6', 'six'), stagger: 0.25 });
    const cc = S.chart({ x: 1150, y: 220, w: 680, h: 600, xlog: true, ylog: true, xmin: 1e4, xmax: 1e16, ymin: 100, ymax: 10000, xticks: [1e4, 1e6, 1e8, 1e10, 1e12, 1e14, 1e16], yticks: [100, 1000, 10000], xfmt: pow10, yfmt: (v) => fmt(v),
      xlabel: 'cycles to failure N', ylabel: 'ΔM<sub>w</sub> [kNm]', title: 'M-N POINTS' });
    cc.show(c('7.6', 'six') + 0.2);
    pts.forEach((p, i) => {
      cc.dot(p.N_gw, p.dM, { color: COL.amber, r: 10, t: c('7.6', 'six') + 0.5 + i * 0.25 });
      if (p.N_T) cc.dot(p.N_T, p.dM, { color: COL.lemon, r: 8, t: c('7.6', 'tsp') + i * 0.2, stroke: '#3b2a00' });
    });
    S.div(`<span style="color:#ffb547">● GW1</span> &nbsp; <span style="color:${COL.lemon}">● TS1</span>`, { x: 1180, y: 880, cls: 'small' }).in(c('7.6', 'tsp'), 0.5);
    S.div('S-N: DNV-RP-C203 (2016) C1 / D, seawater + CP · thickness factor 1.11 for GW1 · teaching values', { x: 100, y: 990, cls: 'tiny' }).in(c('7.6', 'six') + 1.5, 0.5);
  }

  // ------------------------------------------------------------------ 7.7 bilinear and the knee
  {
    const B = b('7.7');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · formulas (B.10) and (B.11)', B.start + 0.3, B.end);
    const e1 = S.eq('\\log \\cn N = \\begin{cases} \\log\\bar a_{\\Delta M,1} - \\cv{m_1}\\log\\DM, & \\DM \\ge \\DM_{1,2}\\\\[4pt] \\log\\bar a_{\\Delta M,2} - \\cv{m_2}\\log\\DM, & \\DM < \\DM_{1,2} \\end{cases}', { x: 960, y: 330, size: 46 });
    e1.in(c('7.7', 'bil'), 0.9, 'write');
    const st = derivation(S, [
      { tex: '\\log\\bar a_{\\Delta M,1} - \\cv{m_1}\\log\\DM_{1,2} = \\log\\bar a_{\\Delta M,2} - \\cv{m_2}\\log\\DM_{1,2}', t: c('7.7', 'set'), size: 44 },
      { tex: '\\log \\DM_{1,2} = \\dfrac{\\log\\bar a_{\\Delta M,2} - \\log\\bar a_{\\Delta M,1}}{\\cv{m_2} - \\cv{m_1}}', t: c('7.7', 'knee'), size: 54 },
    ], { y0: 600, gap: 190 });
    st[1].boxed(c('7.7', 'knee') + 1.6);
  }

  // ------------------------------------------------------------------ 7.8 lower-bound fit
  {
    const B = b('7.8');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.4.4 (lower bound for all hot spots)', B.start + 0.3, B.end);
    const cc = S.chart({ x: 220, y: 200, w: 900, h: 660, xlog: true, ylog: true, xmin: 1e4, xmax: 1e13, ymin: 100, ymax: 10000, xticks: [1e4, 1e6, 1e8, 1e10, 1e12], yticks: [100, 1000, 10000], xfmt: pow10, yfmt: (v) => fmt(v),
      xlabel: 'cycles to failure N', ylabel: 'ΔM<sub>w</sub> [kNm]', title: 'GW1 · LOWER-BOUND BILINEAR M-N CURVE' });
    cc.show(B.start + 0.2);
    pts.forEach((p, i) => cc.dot(p.N_gw, p.dM, { color: COL.amber, r: 10, t: B.start + 0.4 + i * 0.1 }));
    // two branches sliding down to touch the controlling points
    const slide = (t, t0) => 1.2 * (1 - smooth(t, t0, t0 + 2.2));
    const br1 = S.path('', { stroke: COL.coral, width: 5, }), br2 = S.path('', { stroke: COL.violet, width: 5 });
    br1.el.setAttribute('clip-path', cc.plot.getAttribute('clip-path')); br2.el.setAttribute('clip-path', cc.plot.getAttribute('clip-path'));
    br1.in(c('7.8', 'slide'), 0.4, 'none'); br2.in(c('7.8', 'slide') + 0.6, 0.4, 'none');
    E.anim(B.start, B.end, (t) => {
      const d1 = slide(t, c('7.8', 'slide')), d2 = slide(t, c('7.8', 'slide') + 0.6);
      const la1 = gw.loga1 + d1, la2 = gw.loga2 + d2;
      const seg = (la, m, M0, M1) => { let d = ''; for (let i = 0; i <= 40; i++) { const lm = Math.log10(M0) + (Math.log10(M1) - Math.log10(M0)) * i / 40; const N = Math.pow(10, la - m * lm); d += `${i ? 'L' : 'M'}${cc.X(N).toFixed(1)},${cc.Y(Math.pow(10, lm)).toFixed(1)}`; } return d; };
      br1.el.setAttribute('d', seg(la1, 3, 900, 10000));
      br2.el.setAttribute('d', seg(la2, 5, 100, 3000));
    });
    const knee = cc.dot(mnN(gw.dM12, gw), gw.dM12, { color: COL.ink, r: 9, t: c('7.8', 'gwres') + 1.0 });
    const tb = table(S, ['GW1', 'value'], [[tx('\\log\\bar a_{\\Delta M,1}\\ (m_1{=}3)'), gw.loga1.toFixed(2)], [tx('\\log\\bar a_{\\Delta M,2}\\ (m_2{=}5)'), gw.loga2.toFixed(2)], [tx('\\Delta M_{1,2}'), fmt(gw.dM12) + ' kNm']],
      { x: 1200, y: 240, w: 600, t: c('7.8', 'gwres'), colCls: ['l', ''] });
    const eqf = S.eq('\\log\\bar a = \\min_i\\left(\\log \\cn{N_i} + \\cv m\\log\\DM_i\\right)', { x: 1500, y: 640, size: 40 });
    eqf.in(c('7.8', 'slide') + 2.0, 0.7, 'write');
    const nt = S.div('the flat branch is set by the smallest moment, where the gap is open', { x: 1200, y: 760, w: 600, cls: 'small', style: 'color:#b794f6' });
    nt.in(c('7.8', 'note'), 0.6);
  }

  // ------------------------------------------------------------------ 7.9 RF and ΔMc
  {
    const B = b('7.9');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.4.4 · Tables B.11 / B.12', B.start + 0.3, B.end);
    const e1 = S.eq('\\cn{N_{\\mathrm{design}}} = \\dfrac{\\cn N}{\\mathrm{RF}} \\;\\Rightarrow\\; \\log\\bar a \\to \\log\\bar a - \\log \\mathrm{RF}', { x: 960, y: 260, size: 46 });
    e1.in(c('7.9', 'rf'), 0.8, 'write');
    S.div('RF from DNV-RP-C203:2024 section 5.7 · RF = 1 in this example · life ∝ 1 / RF', { x: 960, y: 340, cls: 'small', anchor: 'cm' }).in(c('7.9', 'rf') + 1.2, 0.5);
    const q = quoteCard(S, 'B.4.4', 'Linear and bi-linear M-N curves <span class="q">shall include a fatigue life reduction factor (RF)</span> in accordance with DNV-RP-C203:2024 Section 5.7.', { x: 460, y: 470, w: 1000, t: c('7.9', 'rf') + 2.2, size: 30 });
    q.out(c('7.9', 'dmc') - 0.7, 0.5);
    const tb = table(S, ['Hot spot', 'log ā<sub>ΔM,1</sub>', 'm<sub>1</sub>', 'log ā<sub>ΔM,2</sub>', 'm<sub>2</sub>', 'ΔM<sub>c</sub> [kNm]', 'ΔM<sub>1,2</sub> [kNm]', 'Environment'], [
      ['GW1 conductor girth weld', gw.loga1.toFixed(2), '3', gw.loga2.toFixed(2), '5', fmt(gw.dMc), fmt(gw.dM12), 'seawater + CP'],
      ['TS1 template slot weld', ts.loga1.toFixed(2), '3', ts.loga2.toFixed(2), '5', fmt(ts.dMc), fmt(ts.dM12), 'seawater + CP'],
    ], { x: 110, y: 440, w: 1700, t: c('7.9', 'dmc'), title: 'Table B.12 · fatigue capacity, bilinear M-N curve · bending moment at the WH datum · D<sub>F</sub> = 1', colCls: ['l', '', '', '', '', '', '', 'l'], stagger: 0.4 });
    const dm = S.div(`ΔM<sub>c</sub> = single-load fatigue capacity at 10<sup>6</sup> cycles`, { x: 960, y: 760, cls: 'h3', anchor: 'ct', style: 'color:#ffb547' });
    dm.in(c('7.9', 'dmc') + 1.2, 0.6, 'write');
  }
}

function springH(x0, y, x1, y1) {
  const n = 10, L = x1 - x0;
  let d = `M${x0},${y} L${x0 + L * 0.15},${y}`;
  for (let i = 0; i <= n; i++) { const xx = x0 + L * 0.15 + L * 0.7 * i / n; const yy = y + (i === 0 || i === n ? 0 : (i % 2 ? 8 : -8)); d += ` L${xx.toFixed(1)},${yy.toFixed(1)}`; }
  return d + ` L${x1},${y}`;
}
