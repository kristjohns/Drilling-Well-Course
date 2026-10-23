// Chapter 2 — the stress-strain diagram: tensile test, 0.2 % offset, design values (B.5, B.6), true curve, the three FE curves.
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause } from '../engine/hud.js';
import { quoteCard } from './kit.js';

// strain axis stretched over 0..1 %: the elastic line and the knee stay visible next to 24 % of elongation
const fx = (e) => e / 24;
const XT = [0, 4, 8, 12, 16, 20, 24];
const xlab = (e) => String(e);

function interp(pts, x) {
  if (x <= pts[0][0]) return pts[0][1];
  for (let i = 0; i < pts.length - 1; i++) if (x <= pts[i + 1][0]) return pts[i][1] + (pts[i + 1][1] - pts[i][1]) * (x - pts[i][0]) / (pts[i + 1][0] - pts[i][0]);
  return pts[pts.length - 1][1];
}
function upTo(pts, x) {
  const out = [];
  for (const p of pts) { if (p[0] <= x) out.push(p); else break; }
  out.push([x, interp(pts, x)]);
  return out;
}

export async function build(E, T, D) {
  const ch = T.ch(2);
  titleCard(ch, 'From the tensile test to the material curves of the FE model');
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const mat = D.material, cv = D.curves;
  const eng = cv.eng;
  const eU = mat.uniform_elong * 100, eF = mat.fracture_elong * 100;

  // ------------------------------------------------------------------ 2.1 tensile test
  {
    const B = b('2.1');
    const S = new Scene(B.start, B.end + 0.01, { fadeOut: 0.01 });
    clause('Tensile test · engineering stress and strain', B.start + 0.3, B.end);
    const ch1 = S.chart({ x: 1080, y: 200, w: 740, h: 620, xmin: 0, xmax: 1, ymin: 0, ymax: 700, xticks: XT.map(fx), yticks: [0, 100, 200, 300, 400, 500, 600, 700],
      xfmt: (v) => xlab(XT[XT.map(fx).indexOf(v)]), xlabel: 'Strain ε = ΔL / L<sub>0</sub> · %', ylabel: 'Stress σ = F / A<sub>0</sub> · MPa' });
    ch1.show(B.start + 0.5);
    const tP = c('2.1', 'pull'), tS = c('2.1', 'strain'), tE = c('2.1', 'elastic'), tY = c('2.1', 'yield'), tH = c('2.1', 'hard'), tU = c('2.1', 'uts'), tN = c('2.1', 'neck');
    const tFr = Math.min(B.end - 0.8, tN + 3.4);
    const keys = [[tP, 0], [tS, 0.12], [tE + 3.0, 0.25], [tE + 5.6, 0.0], [tE + 8.0, 0.25], [tY + 1.4, 0.7], [tH + 0.9, 6], [tU + 1.6, eU], [tFr, eF]];
    const strain = (t) => {
      if (t <= keys[0][0]) return 0;
      for (let i = 0; i < keys.length - 1; i++) if (t <= keys[i + 1][0]) return lerp(keys[i][1], keys[i + 1][1], ease.inOut(clamp((t - keys[i][0]) / (keys[i + 1][0] - keys[i][0]))));
      return eF;
    };
    const elasticOnly = (t) => t > tE + 3.0 && t < tE + 8.0;          // unloading and reloading run along the elastic line
    const path = S.path('M0,0', { stroke: COL.amber, width: 5, parent: ch1.plot, o: 1 });
    const dot = S.circle(0, 0, 9, { fill: COL.amber, stroke: '#06121c', width: 2, parent: ch1.plot, o: 0 });
    dot.in(tP, 0.3, 'none');
    let maxE = 0;
    E.anim(B.start, B.end + 0.02, (t) => {
      const e = strain(t);
      if (!elasticOnly(t)) maxE = Math.max(maxE, e); else maxE = Math.max(maxE, 0.25);
      if (t < tE + 3.0) maxE = e;
      const pts = upTo(eng, Math.max(maxE, 1e-4)).map(([x, y]) => [fx(x), y]);
      path.el.setAttribute('d', ch1.pathD(pts));
      const s = elasticOnly(t) ? e / 100 * mat.E : interp(eng, e);
      dot.el.setAttribute('cx', ch1.X(fx(e)).toFixed(1)); dot.el.setAttribute('cy', ch1.Y(s).toFixed(1));
    });
    // labels on the curve
    const lab = (t, xv, yv, html, dx, dy, t1 = B.end) => {
      const p = S.callout(ch1.X(fx(xv)), ch1.Y(yv), ch1.X(fx(xv)) + dx, ch1.Y(yv) + dy, html, { t, color: COL.ink });
      p.out(t1 - 0.3);
      return p;
    };
    lab(tE + 0.5, 0.13, 0.13 / 100 * mat.E, 'Elastic · slope E <span class="sub">Young’s modulus, 207 GPa</span>', 150, 170);
    lab(tY + 0.6, 0.62, interp(eng, 0.62), 'Yielding starts', 90, 100);
    lab(tU + 0.4, eU, mat.su, `Tensile strength · <span class="num">${fmt(mat.su)}</span> MPa`, -40, -80);
    lab(tN + 0.6, 18.5, interp(eng, 18.5), 'Necking', 10, 90);
    const fr = S.div('Fracture', { x: ch1.X(fx(eF)) - 10, y: ch1.Y(interp(eng, eF)) + 70, cls: 'label', anchor: 'cm' });
    fr.in(tFr + 0.1, 0.4, 'pop');
    // the specimen: grips, shoulders and a gauge section that stretches (x 2.2), necks and breaks
    const g = S.g();
    g.in(B.start + 0.6, 0.6, 'none');
    const body = S.path('M0,0', { stroke: '#d7e3ec', width: 2.5, fill: '#7f93a6', parent: g.el, o: 1 });
    const body2 = S.path('M0,0', { stroke: '#d7e3ec', width: 2.5, fill: '#7f93a6', parent: g.el, o: 1 });
    const gl = S.path('M0,0', { stroke: '#ffb547', width: 2, parent: g.el, o: 1, dash: '6 6' });
    const fL = S.arrow(0, 0, 0, 0, { color: COL.amber, o: 0 }), fR = S.arrow(0, 0, 0, 0, { color: COL.amber, o: 0 });
    const fLab = S.div('F', { x: 0, y: 0, cls: 'h3 c-amber' }), fLab2 = S.div('F', { x: 0, y: 0, cls: 'h3 c-amber' });
    for (const a of [fL, fR, fLab, fLab2]) a.in(tP, 0.4, 'none');
    const l0 = S.div('L<sub>0</sub>', { x: 470, y: 470, cls: 'small c-amber', anchor: 'cb' });
    l0.in(tS, 0.4, 'none'); l0.out(tE, 0.4);
    const cx = 470, cy = 560, w0 = 30, wg = 64, gL0 = 320;
    E.anim(B.start, B.end + 0.02, (t) => {
      const e = strain(t) / 100;
      const L = gL0 * (1 + 1.8 * e);
      const xl = cx - L / 2, xr = cx + L / 2;
      const nk = e * 100 > eU ? 0.5 * Math.pow(clamp((e * 100 - eU) / (eF - eU)), 1.4) : 0;
      const broken = t >= tFr;
      const gap = broken ? 26 * ease.out3(clamp((t - tFr) / 0.5)) : 0;
      const half = (x) => {      // half width at x
        if (x < xl - 34) return 62;
        if (x < xl) return wg / 2 + (62 - wg / 2) * Math.pow((xl - x) / 34, 1.6);
        if (x > xr + 34) return 62;
        if (x > xr) return wg / 2 + (62 - wg / 2) * Math.pow((x - xr) / 34, 1.6);
        return wg / 2 * (1 - nk * Math.exp(-(((x - cx) / 30) ** 2)));
      };
      const outline = (xa, xb, shift) => {
        const n = 80, top = [], bot = [];
        for (let i = 0; i <= n; i++) { const x = xa + (xb - xa) * i / n; top.push([x + shift, cy - half(x)]); bot.push([x + shift, cy + half(x)]); }
        return 'M' + top.map((p) => p.map((v) => v.toFixed(1)).join(',')).join(' L') + ' L' + bot.reverse().map((p) => p.map((v) => v.toFixed(1)).join(',')).join(' L') + ' Z';
      };
      const a0 = xl - 34 - 110, b1 = xr + 34 + 110;
      if (!broken) { body.el.setAttribute('d', outline(a0, b1, 0)); body2.el.setAttribute('d', 'M0,0'); }
      else { body.el.setAttribute('d', outline(a0, cx - 1, -gap / 2)); body2.el.setAttribute('d', outline(cx + 1, b1, gap / 2)); }
      gl.el.setAttribute('d', `M${xl.toFixed(1)},${cy - 92} L${xl.toFixed(1)},${cy + 92} M${xr.toFixed(1)},${cy - 92} L${xr.toFixed(1)},${cy + 92}`);
      const ya = cy;
      const set = (arw, x1, x2) => { arw.shaft.el.setAttribute('d', `M${x1},${ya} L${x2 + (x2 > x1 ? -13 : 13)},${ya}`); const s = x2 > x1 ? 1 : -1; arw.tip.el.setAttribute('d', `M${x2 - s * 16},${ya - 7} L${x2},${ya} L${x2 - s * 16},${ya + 7} Z`); };
      set(fL, a0 - 10 - gap / 2, a0 - 90 - gap / 2); set(fR, b1 + 10 + gap / 2, b1 + 90 + gap / 2);
      fLab.el.style.left = (a0 - 80 - gap / 2) + 'px'; fLab.el.style.top = (ya - 64) + 'px';
      fLab2.el.style.left = (b1 + 60 + gap / 2) + 'px'; fLab2.el.style.top = (ya - 64) + 'px';
    });
    const cap = S.div('Specimen: gauge length L<sub>0</sub>, area A<sub>0</sub> <span class="tiny">(elongation drawn ×1.8)</span>', { x: 470, y: 700, cls: 'small', anchor: 'ct' });
    cap.in(tP + 0.5, 0.5);
  }

  // ------------------------------------------------------------------ 2.2 the 0.2 % offset
  {
    const B = b('2.2');
    const S = new Scene(B.start, B.end, { fade: 0.01 });
    clause('NORSOK U-001:2026 · 3.1.22 yielding · 3.1.23 yield strength', B.start + 0.3, B.end);
    const ch2 = S.chart({ x: 1010, y: 200, w: 800, h: 620, xmin: 0, xmax: 1, ymin: 0, ymax: 700, xticks: [0, 0.2, 0.4, 0.6, 0.8, 1], yticks: [0, 100, 200, 300, 400, 500, 600, 700],
      xfmt: (v) => v.toFixed(1), xlabel: 'Strain ε · %', ylabel: 'Stress σ · MPa', o: 1 });
    ch2.xl.in(B.start, 0.01); ch2.yl.in(B.start, 0.01);
    const knee = eng.filter(([x]) => x <= 1.0);
    ch2.curve(knee, { color: COL.amber, width: 5, o: 1 });
    const off = cv.offset;
    const oline = ch2.curve([[0.2, 0], [0.2 + 700 / mat.E * 100, 700]], { color: COL.cyan, width: 3, dash: '10 8', t: c('2.2', 'offset'), d: 0.6 });
    const zl = S.div('0.2 %', { x: ch2.X(0.2), y: ch2.Y(0) + 40, cls: 'small c-cyan', anchor: 'ct' });
    zl.in(c('2.2', 'offset'), 0.5);
    const yx = off[1][0], yy = off[1][1];
    ch2.dot(yx, yy, { color: '#ffffff', r: 10, t: c('2.2', 'cross') });
    const hl = S.path(`M${ch2.X(0)},${ch2.Y(yy)} L${ch2.X(yx)},${ch2.Y(yy)}`, { stroke: '#ffffff', width: 2, dash: '6 6' });
    hl.in(c('2.2', 'cross') + 0.2, 0.5, 'none');
    const yl = S.div(`Yield strength <span class="num">${fmt(mat.sy)}</span> MPa`, { x: ch2.X(0) + 24, y: ch2.Y(yy) - 34, cls: 'label' });
    yl.in(c('2.2', 'cross') + 0.4, 0.5, 'left');
    // unload: back down a line parallel to the elastic line, to 0.2 % permanent strain
    const ud = S.circle(ch2.X(yx), ch2.Y(yy), 9, { fill: COL.coral, stroke: '#06121c', width: 2, o: 0 });
    ud.in(c('2.2', 'unload'), 0.3, 'none');
    const tu = c('2.2', 'unload');
    E.anim(tu, B.end, (t) => {
      const u = ease.inOut(clamp((t - tu - 0.3) / 2.2));
      ud.el.setAttribute('cx', ch2.X(lerp(yx, 0.2, u)).toFixed(1)); ud.el.setAttribute('cy', ch2.Y(lerp(yy, 0, u)).toFixed(1));
    });
    const pl = S.div('0.2 % permanent strain after unloading', { x: ch2.X(0.2) + 20, y: ch2.Y(0) - 60, cls: 'small c-coral' });
    pl.in(tu + 2.4, 0.5, 'left');
    quoteCard(S, '3.1.23 · yield strength', 'stress at which a material exhibits a specified deviation from the proportionality of stress to strain — <span class="q">offset method, a strain of 0.20 %</span> (or total extension under load, usually 0.50 %)', { x: 110, y: 200, w: 800, t: c('2.2', 'def'), size: 29 });
    quoteCard(S, '3.1.22 · yielding', 'theoretical static structural failure mode that occurs when the <span class="q">elastic limit (0.2 % plastic strain)</span> of metallic materials has been exceeded', { x: 110, y: 560, w: 800, t: c('2.2', 'yielding'), size: 29 });
  }

  // ------------------------------------------------------------------ 2.3 design values (B.5, B.6)
  {
    const B = b('2.3');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.2.7.4 design material properties · (B.5) (B.6)', B.start + 0.3, B.end);
    S.div('Design values, not a test result', { x: 960, y: 140, cls: 'h2', anchor: 'ct' }).in(B.start + 0.3, 0.6, 'write');
    const e5 = S.eq('\\sigma_y = \\min\\big[\\,\\p{yy}{Y_y}\\cdot\\mathrm{SMYS}\\,;\\ \\p{cap}{0.90\\cdot Y_u\\cdot\\mathrm{SMTS}}\\,\\big]', { x: 960, y: 290, size: 58 });
    e5.in(c('2.3', 'b5') - 0.2, 0.9, 'write');
    S.div('(B.5)', { x: 1640, y: 290, cls: 'tiny', anchor: 'lm' }).in(c('2.3', 'b5') + 0.5, 0.5);
    e5.hl('cap', c('2.3', 'cap'), { hold: 3.6 });
    const e6 = S.eq('\\sigma_u = Y_u\\cdot\\mathrm{SMTS}', { x: 960, y: 400, size: 58 });
    e6.in(c('2.3', 'b6') - 0.2, 0.8, 'write');
    S.div('(B.6)', { x: 1640, y: 400, cls: 'tiny', anchor: 'lm' }).in(c('2.3', 'b6') + 0.5, 0.5);
    const dr = S.div('Y<sub>y</sub>, Y<sub>u</sub> · temperature de-rating factors, needed above <span class="c-amber">40 °C</span> (ASME II-D, API TR 6MET, hot tensile tests)', { x: 960, y: 480, cls: 'small', anchor: 'ct' });
    dr.in(c('2.3', 'derate'), 0.6);
    const ex = S.card(`<div class="ref">EXAMPLE · WELLHEAD HOUSING · API 75K FORGING</div>
      <div style="display:flex;gap:60px;margin-top:10px">
        <div><div class="tiny">SMYS</div><div class="num" style="font-size:52px">${fmt(mat.SMYS)}<span class="small"> MPa</span></div></div>
        <div><div class="tiny">SMTS</div><div class="num" style="font-size:52px">${fmt(mat.SMTS)}<span class="small"> MPa</span></div></div>
        <div><div class="tiny">METAL TEMPERATURE</div><div class="num" style="font-size:52px">&lt; 40<span class="small"> °C</span></div></div></div>`,
    { x: 960, y: 560, cls: 'glass', anchor: 'ct', style: 'width:1100px' });
    ex.in(c('2.3', 'ex'), 0.6, 'rise');
    const r1 = S.eq(`\\sigma_y = \\min\\big[\\,1.0\\cdot ${mat.SMYS}\\,;\\ 0.90\\cdot1.0\\cdot ${mat.SMTS} = ${mat.cap_09smts}\\,\\big] = \\cs{${mat.sy}\\ \\mathrm{MPa}}`, { x: 960, y: 860, size: 44 });
    r1.in(c('2.3', 'result') - 0.3, 0.9, 'write');
    const r2 = S.eq(`\\sigma_u = ${mat.su}\\ \\mathrm{MPa}`, { x: 960, y: 950, size: 44 });
    r2.in(c('2.3', 'result') + 1.6, 0.7, 'write');
  }

  // ------------------------------------------------------------------ 2.4 true stress and strain
  {
    const B = b('2.4');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.3.6.2 · ASME BPVC VIII-3 KM-620', B.start + 0.3, B.end);
    const chT = S.chart({ x: 900, y: 200, w: 900, h: 620, xmin: 0, xmax: 24, ymin: 0, ymax: 800, xticks: [0, 4, 8, 12, 16, 20, 24], yticks: [0, 200, 400, 600, 800],
      xlabel: 'Strain · %', ylabel: 'Stress · MPa' });
    chT.show(B.start + 0.3);
    const engUp = eng.filter(([x]) => x <= eU + 1e-6);
    chT.curve(eng, { color: COL.amber, width: 4, t: B.start + 0.6, d: 1.4 });
    const lE = S.div('engineering: F / A<sub>0</sub>', { x: chT.X(16), y: chT.Y(interp(eng, 16)) + 40, cls: 'small c-amber' });
    lE.in(B.start + 1.6, 0.5);
    const trueU = cv.true_u.filter(([x]) => x <= 24);
    chT.curve(trueU, { color: COL.cyan, width: 5, t: c('2.4', 'true') + 1.0, d: 2.2 });
    const lT = S.div('true: F / A', { x: chT.X(17), y: chT.Y(mat.st_u) - 50, cls: 'small c-cyan' });
    lT.in(c('2.4', 'rise'), 0.5);
    const eqs = S.eq('\\sigma_t = \\sigma\\,(1+\\varepsilon) \\qquad \\varepsilon_t = \\ln(1+\\varepsilon)', { x: 120, y: 300, size: 46, align: 'left' });
    eqs.in(c('2.4', 'true'), 0.9, 'write');
    S.div('valid up to the start of necking (uniform strain)', { x: 124, y: 360, cls: 'small' }).in(c('2.4', 'true') + 1.6, 0.5);
    chT.dot(mat.eps_tu * 100, mat.st_u, { color: '#ffffff', r: 10, t: c('2.4', 'tu') });
    const tl = S.div(`True ultimate · <span class="num">${fmt(mat.st_u)}</span> MPa at <span class="num">${(mat.eps_tu * 100).toFixed(0)}</span> %`, { x: chT.X(mat.eps_tu * 100) - 30, y: chT.Y(mat.st_u) - 70, cls: 'label', anchor: 'rm' });
    tl.in(c('2.4', 'tu') + 0.3, 0.5, 'right');
    const fe = S.card(`<div class="ref">FE with large strains</div><div class="small">needs the <span class="c-cyan">true</span> curve: true stress against true (logarithmic) strain</div>`, { x: 110, y: 450, w: 700, cls: 'glass' });
    fe.in(c('2.4', 'fe'), 0.6, 'rise');
    const km = S.card(`<div class="ref">No test curve available?</div><div class="small">Use the material model of <span class="c-amber">ASME BPVC VIII-3, KM-620</span> (B.3.6.2): built from σ<sub>y</sub>, σ<sub>u</sub> and E, with the yield strength at 0.2 % plastic strain</div>`, { x: 110, y: 640, w: 700, cls: 'glass' });
    km.in(c('2.4', 'km'), 0.6, 'rise');
  }

  // ------------------------------------------------------------------ 2.5 the three FE curves (Figure B.5)
  {
    const B = b('2.5');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.3.6.2 · Figure B.5', B.start + 0.3, B.end);
    S.div('Three material curves for the FE model', { x: 110, y: 140, cls: 'h2' }).in(B.start + 0.3, 0.6, 'write');
    const ch5 = S.chart({ x: 300, y: 250, w: 1080, h: 640, xmin: 0, xmax: 1, ymin: 0, ymax: 800, xticks: XT.map(fx), yticks: [0, 200, 400, 600, 800],
      xfmt: (v) => xlab(XT[XT.map(fx).indexOf(v)]), xlabel: 'True strain · %', ylabel: 'True stress · MPa' });
    ch5.show(B.start + 0.4);
    const tx = (pts) => pts.filter(([x]) => x <= 24).map(([x, y]) => [fx(x), y]);
    ch5.curve(tx([[0, 0], [800 / mat.E * 100, 800]]), { color: '#b9cad8', width: 4, t: c('2.5', 'lin'), d: 0.8 });
    ch5.curve(tx(cv.true_y), { color: '#ff8a3d', width: 5, t: c('2.5', 'cuty'), d: 1.6 });
    ch5.curve(tx(cv.y_stab), { color: '#ff8a3d', width: 3, dash: '8 7', t: c('2.5', 'stab'), d: 0.8 });
    ch5.curve(tx(cv.true_u), { color: COL.cyan, width: 5, t: c('2.5', 'cutu'), d: 1.8 });
    const tag = (t, y, color, title, sub) => {
      const a = S.div(`<div style="font-weight:750;font-size:27px;color:${color}">${title}</div><div class="small" style="font-size:22px">${sub}</div>`, { x: 1420, y, w: 440 });
      a.in(t + 0.4, 0.6, 'left');
      return a;
    };
    tag(c('2.5', 'lin'), 250, '#b9cad8', 'Linear elastic', 'elastic analysis · B.3.5');
    tag(c('2.5', 'cuty'), 520, '#ff8a3d', 'Cut-off at σ<sub>y</sub> · no hardening', 'limit load method');
    const st = S.div('≤ +5 % at 20 % plastic strain to help the solver', { x: ch5.X(fx(16)), y: ch5.Y(565) - 6, cls: 'small', anchor: 'cb', style: 'color:#ff8a3d;font-size:21px' });
    st.in(c('2.5', 'stab') + 0.5, 0.5);
    tag(c('2.5', 'cutu'), 340, COL.cyan, 'Cut-off at the true ultimate', 'plastic collapse method · local failure check');
    const yl = S.div(`σ<sub>y</sub> = ${mat.sy} MPa`, { x: ch5.X(fx(2)), y: ch5.Y(mat.sy) + 30, cls: 'small', style: 'color:#ff8a3d;font-size:22px' });
    yl.in(c('2.5', 'cuty') + 0.8, 0.5);
    const kp = S.div('Each curve belongs to a different acceptance check', { x: 960, y: 1000, cls: 'h3', anchor: 'cm', style: 'color:#ffb547' });
    kp.in(c('2.5', 'keep'), 0.7, 'rise');
  }
}
