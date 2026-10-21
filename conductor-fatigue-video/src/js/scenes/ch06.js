// Chapter 6 — from moment to hot-spot stress: bending stress, I of a tube, nominal stress at GW1, SCF, the slot hot spot.
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt } from '../engine/core.js';
import { Scene } from '../engine/scene.js';
import { titleCard, clause, step } from '../engine/hud.js';
import { camPath, DEF, THREE } from '../three/world.js';
import { updateSnow, glowBall } from '../three/models.js';
import { quoteCard, derivation, table, tx, label3D } from './kit.js';
import { tubeSection } from './drawings.js';

export async function build(E, T, D) {
  const ch = T.ch(6);
  titleCard(ch, 'Step 4 · beam theory, section properties and stress concentrations');
  step(ch.title_card[1], 3);
  const W3 = E.world, md = W3.models, M = W3.M;
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const ex = D.example, p3000 = ex.points.find((p) => p.dM === 3000);

  // ------------------------------------------------------------------ 6.1 bending stress
  {
    const B = b('6.1');
    const S = new Scene(B.start, B.end);
    const x0 = 150, y0 = 300, Hs = 420, Wb = 340;
    // beam segment bending, strain and stress profiles
    const seg = S.path(`M${x0},${y0} Q${x0 + Wb / 2},${y0 + 40} ${x0 + Wb},${y0} L${x0 + Wb},${y0 + Hs} Q${x0 + Wb / 2},${y0 + Hs + 40} ${x0},${y0 + Hs} Z`, { fill: '#2c3f52', stroke: COL.ink2, width: 2 });
    seg.in(B.start + 0.3, 0.5, 'none');
    const na = S.line(x0 - 30, y0 + Hs / 2 + 20, x0 + Wb + 30, y0 + Hs / 2 + 20, { stroke: COL.dim, width: 2, dash: '8 6' }); na.in(c('6.1', 'plane'), 0.5, 'none');
    S.div('neutral axis', { x: x0 + Wb + 40, y: y0 + Hs / 2 + 20, cls: 'tiny', anchor: 'lm' }).in(c('6.1', 'plane'), 0.5);
    const sx = x0 + Wb + 220;
    const strain = S.path(`M${sx},${y0} L${sx - 90},${y0} L${sx + 90},${y0 + Hs} L${sx},${y0 + Hs} Z`, { fill: 'rgba(79,209,255,0.18)', stroke: COL.cyan, width: 3 });
    strain.in(c('6.1', 'plane') + 0.4, 0.6, 'none');
    S.div('strain ε = κ y', { x: sx, y: y0 - 30, cls: 'small', anchor: 'cb', style: 'color:#4fd1ff' }).in(c('6.1', 'plane') + 0.4, 0.5);
    const sx2 = sx + 230;
    const stress = S.path(`M${sx2},${y0} L${sx2 - 90},${y0} L${sx2 + 90},${y0 + Hs} L${sx2},${y0 + Hs} Z`, { fill: 'rgba(255,111,97,0.18)', stroke: COL.coral, width: 3 });
    stress.in(c('6.1', 'hooke'), 0.6, 'none');
    S.div('stress σ = E κ y', { x: sx2, y: y0 - 30, cls: 'small', anchor: 'cb', style: 'color:#ff6f61' }).in(c('6.1', 'hooke'), 0.5);
    const st = derivation(S, [
      { tex: '\\varepsilon = \\kappa\\,y', t: c('6.1', 'plane'), x: 1120, align: 'left', note: 'plane sections' },
      { tex: '\\cs\\sigma = E\\,\\kappa\\,y', t: c('6.1', 'hooke'), x: 1120, align: 'left', note: 'Hooke' },
      { tex: '\\cm M = \\int_A \\cs\\sigma\\,y\\,\\dd A = E\\kappa\\int_A y^2\\,\\dd A = E I \\kappa', t: c('6.1', 'eq'), x: 1120, align: 'left', note: 'equilibrium', size: 40 },
      { tex: '\\cs\\sigma = \\dfrac{\\cm M\\,y}{I},\\qquad \\cs{\\sigma_{\\max}} = \\dfrac{\\cm M}{W},\\;\\; W = \\dfrac{2I}{D}', t: c('6.1', 'sigma'), x: 1120, align: 'left', size: 42 },
    ], { y0: 290, gap: 165, size: 50, noteAbove: true });
    st[3].boxed(c('6.1', 'sigma') + 2.0);
  }

  // ------------------------------------------------------------------ 6.2 second moment of a tube
  {
    const B = b('6.2');
    const S = new Scene(B.start, B.end);
    const cx = 470, cy = 560, R = 300, t = 300 * 50.8 / 457.2;
    const tube = tubeSection(S, cx, cy, R, t, { fill: '#5b7085' }); tube.in(B.start + 0.3, 0.5, 'none');
    const rr = (tt) => R - t + t * clamp((tt - c('6.2', 'polar')) / 2.5);
    const ringEl = S.circle(cx, cy, R - t / 2, { fill: 'none', stroke: COL.amber, width: 8 });
    ringEl.in(c('6.2', 'polar'), 0.4, 'none');
    E.anim(B.start, B.end, (tt) => { ringEl.el.setAttribute('r', (rr(tt) - 4).toFixed(1)); });
    S.arrow(cx, cy, cx + (R - t / 2) * 0.7, cy - (R - t / 2) * 0.7, { color: COL.ink2, width: 2 }).in(c('6.2', 'polar'), 0.4, 'none');
    S.eq('r', { x: cx + 90, y: cy - 130, size: 36, align: 'left' }).in(c('6.2', 'polar'), 0.4, 'none');
    S.div('ring of radius r, width dr: dA = 2πr dr', { x: cx, y: cy + R + 50, cls: 'small', anchor: 'ct', style: 'color:#ffb547' }).in(c('6.2', 'polar') + 0.4, 0.5);
    const st = derivation(S, [
      { tex: 'J = \\int r^2\\,\\dd A = \\int_{r_i}^{r_o} r^2\\, 2\\pi r\\,\\dd r = \\dfrac{\\pi}{2}\\left(r_o^4 - r_i^4\\right)', t: c('6.2', 'polar'), x: 900, align: 'left', size: 44, note: 'polar moment' },
      { tex: 'I = \\dfrac{J}{2} = \\dfrac{\\pi}{64}\\left(D^4 - d^4\\right)', t: c('6.2', 'sym'), x: 900, align: 'left', size: 54, note: 'symmetry: <span style="text-transform:none;letter-spacing:0.04em">J = I<sub>x</sub> + I<sub>y</sub></span>' },
      { tex: 'I = \\dfrac{\\pi}{64}\\left(914.4^4 - 812.8^4\\right) = 1.289\\times10^{10}\\ \\text{mm}^4', t: c('6.2', 'num'), x: 900, align: 'left', size: 40 },
      { tex: 'W = \\dfrac{I}{D/2} = 2.820\\times10^{7}\\ \\text{mm}^3', t: c('6.2', 'num') + 2.6, x: 900, align: 'left', size: 44 },
    ], { y0: 280, gap: 170, size: 48, noteAbove: true });
    st[1].boxed(c('6.2', 'i'));
  }

  // ------------------------------------------------------------------ 6.3 nominal stress at GW1 (moment diagram from the local model)
  {
    const B = b('6.3');
    const S = new Scene(B.start, B.end);
    clause('simplified local model · ΔM<sub>w</sub> = 3000 kNm (±1500)', B.start + 0.3, B.end);
    const pr = D.profiles.base;
    const cc = S.chart({ x: 220, y: 190, w: 620, h: 720, xmin: 0, xmax: 4500, ymin: 16, ymax: -0.5, xticks: [0, 1500, 3000, 4500], yticks: [0, 4, 8, 12, 16], xfmt: (v) => fmt(v), yfmt: (v) => v + ' m',
      xlabel: 'moment range at depth z [kNm]', title: 'DEPTH BELOW THE WELLHEAD DATUM' });
    cc.show(B.start + 0.3);
    const sel = pr.z.map((z, i) => [z, i]).filter(([z]) => z <= 16);
    const outer = sel.map(([z, i]) => [Math.abs(2 * pr.M_out[i]) / 1e3, z]).filter((p, j) => pr.z[sel[j][1]] >= 0.9);
    const inner = sel.map(([z, i]) => [Math.abs(2 * pr.M_in[i]) / 1e3, z]);
    const free = [[3000, 0], [3000 * (1 + 16 / 13.7), 16]];
    cc.curve(free, { color: COL.dim, width: 2, dash: '8 8', t: c('6.3', 'gw1') - 0.8 });
    S.div('no load share: M<sub>w</sub>(1 + z/H)', { x: cc.X(3000 * (1 + 10 / 13.7)) + 8, y: cc.Y(10), cls: 'tiny', anchor: 'lm' }).in(c('6.3', 'gw1') - 0.4, 0.5);
    cc.curve(inner, { color: COL.blue, width: 4, t: c('6.3', 'gw1') - 0.4 });
    cc.curve(outer, { color: COL.amber, width: 5, t: c('6.3', 'gw1') });
    S.div('conductor string', { x: cc.X(3200), y: cc.Y(6.5), cls: 'tiny', anchor: 'lm', style: 'color:#ffb547' }).in(c('6.3', 'gw1') + 1.0, 0.5);
    S.div('WH / surface casing string', { x: cc.X(600), y: cc.Y(14.5), cls: 'tiny', anchor: 'lm', style: 'color:#5aa9ff' }).in(c('6.3', 'gw1') + 1.0, 0.5);
    const dot = cc.dot(p3000.dM_gw, 3.0, { color: COL.coral, r: 11, t: c('6.3', 'm') });
    S.line(cc.X(0), cc.Y(3.0), cc.X(4500), cc.Y(3.0), { stroke: 'rgba(255,111,97,0.5)', width: 2, dash: '6 6' }).in(c('6.3', 'gw1'), 0.5, 'none');
    S.div('GW1 · 3.0 m', { x: cc.X(4400), y: cc.Y(3.0) - 16, cls: 'tiny', anchor: 'rb', style: 'color:#ff6f61' }).in(c('6.3', 'gw1'), 0.5);
    const e1 = S.eq('\\cm{\\Delta M_{GW1}} = ' + fmt(p3000.dM_gw) + '\\ \\text{kNm}', { x: 960, y: 380, size: 52, align: 'left' });
    e1.in(c('6.3', 'm'), 0.7, 'write');
    const e2 = S.eq('\\cs{\\Delta\\sigma_{\\mathrm{nom}}} = \\dfrac{' + fmt(p3000.dM_gw) + '\\times10^{6}}{2.820\\times10^{7}} = ' + (p3000.ds_gw / ex.inputs.SCF_gw).toFixed(1) + '\\ \\text{MPa}', { x: 960, y: 560, size: 46, align: 'left' });
    e2.in(c('6.3', 'nom'), 0.8, 'write');
    e2.boxed(c('6.3', 'nom') + 2.0);
  }

  // ------------------------------------------------------------------ 6.4 stress concentration from misalignment
  {
    const B = b('6.4');
    const S = new Scene(B.start, B.end);
    clause('DNV-RP-C203 · SCF for misalignment of butt welds (principle)', B.start + 0.3, B.end);
    const y0 = 420, tpx = 90, e = 30;
    const g = S.g(); g.in(B.start + 0.3, 0.5, 'none');
    S.rect(160, y0, 360, tpx, { fill: '#3a5168', stroke: COL.ink2, width: 2, parent: g.el, o: 1 });
    S.rect(520, y0 + e, 360, tpx, { fill: '#3a5168', stroke: COL.ink2, width: 2, parent: g.el, o: 1 });
    S.path(`M500,${y0} L540,${y0 + e} L540,${y0 + e + tpx} L500,${y0 + tpx} Z`, { fill: '#5b7085', stroke: COL.ink2, width: 2, parent: g.el, o: 1 });
    const N1 = S.arrow(150, y0 + tpx / 2, 40, y0 + tpx / 2, { color: COL.amber, width: 5 }), N2 = S.arrow(890, y0 + e + tpx / 2, 1000, y0 + e + tpx / 2, { color: COL.amber, width: 5 });
    N1.in(c('6.4', 'mis'), 0.4, 'none'); N2.in(c('6.4', 'mis'), 0.4, 'none');
    S.eq('N', { x: 30, y: y0 + tpx / 2 - 40, size: 36, align: 'left' }).in(c('6.4', 'mis'), 0.4, 'none');
    S.eq('N', { x: 980, y: y0 + e + tpx / 2 - 40, size: 36, align: 'left' }).in(c('6.4', 'mis'), 0.4, 'none');
    const ed = S.path(`M560,${y0 + tpx / 2} L560,${y0 + e + tpx / 2}`, { stroke: COL.coral, width: 3 }); ed.in(c('6.4', 'mis') + 0.6, 0.4, 'none');
    S.eq('e', { x: 575, y: y0 + tpx / 2 + e / 2, size: 34, align: 'left', color: COL.coral }).in(c('6.4', 'mis') + 0.6, 0.4, 'none');
    const lof = S.path(`M60,${y0 + tpx / 2} L510,${y0 + tpx / 2} L530,${y0 + e + tpx / 2} L980,${y0 + e + tpx / 2}`, { stroke: COL.amber, width: 2.5, dash: '10 8' }); lof.in(c('6.4', 'moment'), 0.5, 'none');
    S.div('line of force jogs → local bending at the weld', { x: 520, y: y0 + 170, cls: 'small', anchor: 'ct' }).in(c('6.4', 'moment'), 0.5);
    const st = derivation(S, [
      { tex: '\\cm{M_e} = N e,\\qquad \\text{each side } \\tfrac{1}{2}N e', t: c('6.4', 'moment'), x: 1080, align: 'left' },
      { tex: '\\cs{\\sigma_b} = \\dfrac{6\\,(N e/2)}{t^2} = \\dfrac{3 N e}{t^2},\\qquad \\cs{\\sigma_m} = \\dfrac{N}{t}', t: c('6.4', 'moment') + 2.6, x: 1080, align: 'left' },
      { tex: '\\mathrm{SCF} = 1 + \\dfrac{\\cs{\\sigma_b}}{\\cs{\\sigma_m}} = 1 + \\dfrac{3e}{t}', t: c('6.4', 'scf'), x: 1080, align: 'left', size: 54 },
    ], { y0: 270, gap: 150, size: 44 });
    st[2].boxed(c('6.4', 'scf') + 1.4);
    S.div('tubes restrain the offset better; DNV-RP-C203 gives the tubular formula, and part of the misalignment is already inside the S-N class', { x: 1080, y: 720, w: 740, cls: 'small' }).in(c('6.4', 'tube'), 0.6);
    const hs = S.eq('\\cs{\\Delta\\sigma_{hs}} = 1.10 \\times ' + (p3000.ds_gw / 1.1).toFixed(1) + ' = ' + p3000.ds_gw.toFixed(1) + '\\ \\text{MPa}', { x: 1080, y: 900, size: 46, align: 'left' });
    hs.in(c('6.4', 'hs'), 0.8, 'write');
  }

  // ------------------------------------------------------------------ 6.5 template slot hot spot
  {
    const B = b('6.5');
    const S = new Scene(B.start, B.end);
    clause('TS1 · illustrative beam model of the slot supports', B.start + 0.3, B.end);
    // plan view: ring between two beams
    const g = S.g(); g.in(B.start + 0.3, 0.5, 'none');
    S.rect(160, 300, 720, 46, { fill: '#e7ae1c', stroke: 'none', rx: 4, parent: g.el, o: 1 });
    S.rect(160, 560, 720, 46, { fill: '#e7ae1c', stroke: 'none', rx: 4, parent: g.el, o: 1 });
    S.circle(520, 453, 90, { fill: 'none', stroke: '#e7ae1c', width: 26, parent: g.el, o: 1 });
    S.circle(520, 453, 62, { fill: '#8d9cab', stroke: 'none', parent: g.el, o: 1 });
    S.path('M520,363 L520,346 M520,543 L520,560', { stroke: '#e7ae1c', width: 20, parent: g.el, o: 1 });
    for (const y of [300, 560]) { S.rect(130, y - 10, 30, 66, { fill: 'url(#hatch)', stroke: COL.ink2, width: 1, parent: g.el, o: 1 }); S.rect(880, y - 10, 30, 66, { fill: 'url(#hatch)', stroke: COL.ink2, width: 1, parent: g.el, o: 1 }); }
    const F = S.arrow(520, 453, 700, 453, { color: COL.amber, width: 6, head: 22 }); F.in(c('6.5', 'ts1'), 0.4, 'none');
    S.eq('F', { x: 720, y: 453, size: 40, align: 'left' }).in(c('6.5', 'ts1'), 0.4, 'none');
    const hs = S.circle(520, 346, 12, { fill: COL.coral }); hs.in(c('6.5', 'ts1') + 0.4, 0.4, 'pop');
    S.div('TS1 hot spot', { x: 545, y: 330, cls: 'small', anchor: 'lb', style: 'color:#ff6f61' }).in(c('6.5', 'ts1') + 0.4, 0.4);
    // fixed-fixed beam moment diagram
    const bm = S.g(); bm.in(c('6.5', 'beam'), 0.5, 'none');
    S.line(160, 800, 880, 800, { stroke: COL.ink2, width: 6, parent: bm.el, o: 1 });
    S.path('M160,800 L340,800 L520,740 L700,800 L880,800', { stroke: 'none', parent: bm.el, o: 1 });
    S.path('M160,800 L160,860 L340,800 L520,740 L700,800 L880,860 L880,800', { stroke: COL.violet, width: 3, fill: 'rgba(183,148,246,0.15)', parent: bm.el, o: 1 });
    S.arrow(520, 690, 520, 790, { color: COL.amber, width: 4, parent: bm.el, o: 1 });
    S.svgText('F/2', 545, 700, { size: 24, fill: COL.amber, anchor: 'start', parent: bm.el, o: 1 });
    S.svgText('PL/8', 520, 720, { size: 22, fill: COL.violet, parent: bm.el, o: 1 });
    const st = derivation(S, [
      { tex: '\\cm{M_{\\mathrm{mid}}} = \\dfrac{(F/2)\\,L}{8} = \\dfrac{F L}{16}', t: c('6.5', 'beam'), x: 1060, align: 'left' },
      { tex: '\\cs{\\sigma_{hs}} = \\mathrm{SCF}\\,\\dfrac{F L}{16\\,W} \\;\\Rightarrow\\; \\dfrac{2.0\\times2.5}{16\\times0.002} = 0.156\\ \\tfrac{\\text{MPa}}{\\text{kN}}', t: c('6.5', 'kappa'), x: 1060, align: 'left', size: 40 },
      { tex: '\\Delta F_C = ' + fmt(p3000.dF_C) + '\\ \\text{kN} \\;\\Rightarrow\\; \\cs{\\Delta\\sigma_{hs}} = ' + p3000.ds_T.toFixed(1) + '\\ \\text{MPa}', t: c('6.5', 'num'), x: 1060, align: 'left', size: 44 },
    ], { y0: 300, gap: 170, size: 46 });
    st[2].boxed(c('6.5', 'num') + 2.2);
    S.div('at ΔM<sub>w</sub> = 3000 kNm (local model, 2 mm gap)', { x: 1060, y: 720, cls: 'tiny' }).in(c('6.5', 'num') + 0.5, 0.5);
  }

  // ------------------------------------------------------------------ 6.6 where the hot spots are (3D)
  {
    const B = b('6.6');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.2.3 e) · Table B.11 note a', B.start + 0.3, B.end);
    const spots = [[0.27, 1.1, 0.03, 'WH housing → extension weld'], [0.26, -5.0, 0.03, 'surface casing at top of cement'], [0.46, 1.0, 0.03, 'GW1 · conductor girth weld'], [0.47, -11.5, 0.03, 'conductor connector (outside U-001 scope)'], [0.7, 2.4, 0.05, 'TS1 · template slot weld']];
    const glows = spots.map(([x, y, z]) => { const s = glowBall(M, '#ff6f61', 0.13); s.position.set(x, y, z); W3.scene.add(s); return s; });
    glows.forEach((g, i) => { md['hs' + i] = g; });
    const cam = camPath([{ t: B.start, p: [10.4, -1.4, 24.6], l: [1.2, -4.3, 0], fov: 44 }, { t: B.end, p: [9.6, -1.8, 23.4], l: [1.2, -4.5, 0], fov: 44 }]);
    W3.shot(B.start, B.end, {
      show: ['wellCut', 'templateCut', 'seabedCut', 'connCut', ...glows.map((_, i) => 'hs' + i)],
      fadeIn: 0.8, fadeOut: 0.6, cam, fog: 0.008, bg: '#082b42',
      update: (t) => {
        W3.update(t); DEF.uAmp.value = 0; DEF.uStressMix.value = 0; DEF.uGlow.value = 0;
        glows.forEach((g, i) => { const on = smooth(t, c('6.6', 'list') + i * 0.6, c('6.6', 'list') + i * 0.6 + 0.4); g.material.opacity = on * (0.8 + 0.2 * Math.sin(t * 4 + i)); g.visible = on > 0.01; });
      },
    });
    const lo = [['rm', -150, -36], ['rm', -140, 0], ['lm', 150, 44], ['rm', -140, 0], ['lm', 150, -40]];     // label side and offsets per spot
    spots.forEach(([x, y, z, name], i) => label3D(S, [x, y, z], name, { t0: c('6.6', 'list') + i * 0.6, t1: B.end, anchor: lo[i][0], dx: lo[i][1], dy: lo[i][2], color: COL.coral }));
    const n = S.card('<div class="small">“Four to six fatigue hotspots with the lowest capacity, i.e. critical regions, are typically sufficient.”</div><div class="tiny" style="margin-top:8px">Table B.11, note a</div>', { x: 1300, y: 800, w: 520 });
    n.in(c('6.6', 'fea'), 0.6);
  }
}
