// Chapter 4 — the elastic-plastic route: analysis requirements, the limit load (3D yielded zone + load-rotation curve,
// non-convergence), the factored plastic collapse load, Figure B.6, the capacity chart.
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause } from '../engine/hud.js';
import { camSpline } from '../three/world.js';
import { FEU, feSetPlastic } from '../three/models.js';
import { stamp } from './kit.js';
import { peLegend, probe3D, note, capChart } from './fx.js';

export async function build(E, T, D) {
  const ch = T.ch(4);
  titleCard(ch, 'The capacity is a load: limit load, plastic collapse, and the capacity chart');
  const W3 = E.world, md = W3.models;
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const ep = D.ep, mat = D.material;
  const Mp = ep.M_limit;
  const rot = ep.rot_mrad, My = ep.M_y, Mu = ep.M_u;
  // neck curvature (1/m) for a bending moment on the cut-off-at-yield curve
  const kappaOf = (M) => {
    if (M <= 0) return 0;
    for (let i = 0; i < My.length - 1; i++) if (M <= My[i + 1]) return (rot[i] + (rot[i + 1] - rot[i]) * (M - My[i]) / (My[i + 1] - My[i])) / 1000 / ep.L_rot;
    return rot[rot.length - 1] / 1000 / ep.L_rot;
  };

  // ------------------------------------------------------------------ 4.1 the analysis
  {
    const B = b('4.1');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.3.6.2 · B.3.6.5 · Table B.8', B.start + 0.3, B.end);
    S.div('The FE model shall include', { x: 110, y: 150, cls: 'h2' }).in(B.start + 0.3, 0.6, 'write');
    const items = [['list', 'von Mises yield function, associated flow rule'], ['large', 'Large deformations (geometric non-linearity)'], ['large', 'Large strains'],
      ['iso', 'Strain hardening: <span class="c-amber">isotropic</span> for static capacities'], ['kin', '<span class="c-amber">kinematic</span> if yielding reverses (e.g. cyclic pressure from above and below)']];
    items.forEach(([cue, txt], i) => {
      const a = S.div(`<span style="color:#46d39a;font-weight:800;margin-right:16px">✓</span>${txt}`, { x: 130, y: 260 + i * 70, cls: 'small', style: 'font-size:29px;color:#e9f2f9' });
      a.in(c('4.1', cue) + (i === 2 ? 1.2 : 0), 0.5, 'left');
    });
    // load sequence strip
    const seq = [['Preload', 'minimum preload'], ['Pressure', 'held constant'], ['Tension', 'held constant'], ['Bending ↑', 'to instability']];
    seq.forEach(([a, sub], i) => {
      const x = 130 + i * 430;
      const card = S.card(`<div style="font-weight:750;font-size:32px">${a}</div><div class="small" style="font-size:22px">${sub}</div>`, { x, y: 720, w: 340, cls: 'glass', style: i === 3 ? 'border-color:rgba(255,181,71,0.7)' : '' });
      card.in(c('4.1', i === 3 ? 'ramp' : 'seq') + (i < 3 ? i * 0.6 : 0), 0.6, 'rise');
      if (i < 3) { const ar = S.arrow(x + 352, 780, x + 418, 780, { color: COL.dim, width: 4 }); ar.in(c('4.1', 'seq') + i * 0.6 + 0.4, 0.4, 'none'); }
    });
    S.div('Table B.8, load case 1: bending moment increased to overall structural instability (maximum load); pressure and tension zero', { x: 130, y: 880, w: 1600, cls: 'small' }).in(c('4.1', 'ramp') + 0.8, 0.6);
  }

  // ------------------------------------------------------------------ 4.2 the limit load: 3D yielded zone + load-rotation curve
  {
    const B = b('4.2');
    const t0 = c('4.2', 'first'), tnc = c('4.2', 'nc');
    const inc = ep.increments;                       // [frac, M, rot]
    // increments timed to the narration: the elastic steps go quickly, the surface yields (about 0.89 Mp) on 'yield0',
    // the last steps crawl while the yielded zone spreads and the hinge forms
    const ty = c('4.2', 'yield0'), tsp = c('4.2', 'spread'), thg = c('4.2', 'hinge');
    const tInc = [t0 + 0.6, t0 + 1.2, t0 + 1.8, t0 + 2.3, ty + 0.4, ty + 2.0, tsp + 0.4, tsp + 3.6, thg - 0.6, thg + 1.0];
    const Mof = (t) => {
      if (t <= t0) return 0;
      if (t <= tInc[0]) return inc[0][1] * ease.inOut(clamp((t - t0) / (tInc[0] - t0)));
      for (let i = 0; i < inc.length - 1; i++) if (t <= tInc[i + 1]) return lerp(inc[i][1], inc[i + 1][1], ease.inOut(clamp((t - tInc[i]) / (tInc[i + 1] - tInc[i]))));
      return inc[inc.length - 1][1];
    };
    const panel = { x: 40, y: 150, w: 700, h: 820 };
    const cam = camSpline([
      { t: B.start, p: [0.2, 3.42, 2.05], l: [0.0, 3.28, 0], fov: 34 },
      { t: B.end, p: [0.3, 3.45, 1.9], l: [0.02, 3.28, 0], fov: 34 },
    ]);
    W3.shot(B.start, B.end, {
      show: ['feHousing'], fadeIn: 0.7, fadeOut: 0.5, cam, fog: 0, bg: '#0b1824', panel,
      update: (t) => {
        const M = Mof(t);
        feSetPlastic(M, kappaOf(M), { E: mat.E, sy: mat.sy });
        FEU.uFE.value = 1;
        md.feHousing.userData.lines.material.opacity = 0.35;
      },
      key: (t) => Mof(t).toFixed(4),
    });
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.3.6.3.2.2 limit load method', B.start + 0.3, B.end);
    const kk = S.div('LIMIT LOAD METHOD · CURVE CUT OFF AT <span style="text-transform:none">σ<sub>y</sub></span>', { x: 70, y: 110, cls: 'kicker' });
    kk.in(B.start + 0.3, 0.5, 'left');
    peLegend(S, { x: 758, y: 690, t0: B.start + 0.8 });
    const ts = S.div('tension side', { x: 0, y: 0, cls: 'tiny', style: 'color:#fff' }), cs = S.div('compression side', { x: 0, y: 0, cls: 'tiny', style: 'color:#fff' });
    ts.in(B.start + 1.0, 0.5); cs.in(B.start + 1.0, 0.5);
    E.anim(B.start, B.end, (t) => {
      const a = W3.project([0.34, 3.12, 0], t), q = W3.project([-0.34, 3.12, 0], t);
      ts.el.style.left = (a.x - 60) + 'px'; ts.el.style.top = (a.y + 20) + 'px';
      cs.el.style.left = (q.x - 80) + 'px'; cs.el.style.top = (q.y + 20) + 'px';
    });
    // the chart
    const chm = S.chart({ x: 1090, y: 200, w: 760, h: 600, xmin: 0, xmax: 70, ymin: 0, ymax: 24, xticks: [0, 10, 20, 30, 40, 50, 60, 70], yticks: [0, 4, 8, 12, 16, 20, 24],
      xlabel: 'End rotation · mrad', ylabel: 'Bending moment M · MNm', title: 'LOAD-ROTATION CURVE · LOAD CASE 1' });
    chm.show(B.start + 0.4);
    const curveY = rot.map((r, i) => [r, My[i]]).filter(([r]) => r <= 70);
    const path = S.path('M0,0', { stroke: '#ff8a3d', width: 5, parent: chm.plot, o: 1 });
    E.anim(t0, B.end, (t) => {
      const M = Mof(t);
      const pts = [];
      for (const p of curveY) { if (p[1] <= M + 1e-9) pts.push(p); else break; }
      const r1 = kappaOf(M) * 1000 * ep.L_rot;
      pts.push([Math.min(r1, 70), M]);
      path.el.setAttribute('d', chm.pathD(pts));
    });
    inc.forEach(([f, M, r], i) => chm.dot(Math.min(r, 70), M, { color: '#ffffff', r: 7, t: tInc[i] }));
    const sy0 = S.callout(chm.X(ep.rot_surf_yield), chm.Y(ep.M_surf_yield), chm.X(ep.rot_surf_yield) + 70, chm.Y(ep.M_surf_yield) + 120,
      `0.2 % plastic strain at the surface · <span class="num">${Math.round(ep.surf_yield_frac * 100)}</span> %`, { t: c('4.2', 'yield0') + 1.8, color: COL.cyan });
    sy0.out(c('4.2', 'cap'));
    // non-convergence: the next increment
    const nx = S.div('✗', { x: chm.X(64), y: chm.Y(Mp * 1.003), cls: 'h2', anchor: 'cm', style: 'color:#ff4d5e;font-size:56px' });
    nx.in(tnc, 0.4, 'pop');
    const na = S.path(`M${chm.X(inc[inc.length - 1][2]) + 12},${chm.Y(Mp * 1.003)} L${chm.X(60)},${chm.Y(Mp * 1.003)}`, { stroke: '#ff4d5e', width: 3, dash: '8 7' });
    na.in(tnc - 0.2, 0.4, 'none');
    const nt = S.div('next step: no equilibrium · not converged', { x: chm.X(64), y: chm.Y(Mp) - 70, cls: 'small', anchor: 'rm', style: 'color:#ff4d5e' });
    nt.in(tnc + 0.3, 0.5);
    const lim = S.path(`M${chm.X(0)},${chm.Y(Mp)} L${chm.X(70)},${chm.Y(Mp)}`, { stroke: '#ffffff', width: 2, dash: '4 6' });
    lim.in(c('4.2', 'cap'), 0.5, 'none');
    const ll = S.card(`<div class="tiny">LIMIT LOAD = YIELDING CAPACITY (F<sub>d</sub> = 1.0)</div><div class="num" style="font-size:54px;color:#ffb547">${Mp.toFixed(1)} <span class="small">MNm</span></div>`, { x: 1260, y: 905, w: 560, cls: 'glass' });
    ll.in(c('4.2', 'mc'), 0.6, 'rise');
    const hg = S.div('plastic hinge', { x: 0, y: 0, cls: 'label' });
    hg.in(c('4.2', 'hinge'), 0.5, 'pop');
    E.anim(c('4.2', 'hinge') - 0.1, B.end, (t) => { const p = W3.project([0, 3.28, 0], t); hg.el.style.left = (p.x - 70) + 'px'; hg.el.style.top = (p.y - 20) + 'px'; });
    note(S, 'Teaching stand-in: section model of the neck', { t0: B.start + 1, t1: B.end - 0.4 });
  }

  // ------------------------------------------------------------------ 4.3 the factored plastic collapse load
  {
    const B = b('4.3');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.3.6.3.2.3 factored plastic collapse method', B.start + 0.3, B.end);
    const chc = S.chart({ x: 980, y: 200, w: 840, h: 600, xmin: 0, xmax: 600, ymin: 0, ymax: 28, xticks: [0, 100, 200, 300, 400, 500, 600], yticks: [0, 4, 8, 12, 16, 20, 24, 28],
      xlabel: 'End rotation · mrad', ylabel: 'Bending moment M · MNm', title: 'LOAD-ROTATION CURVES' });
    chc.show(B.start + 0.2);
    chc.curve(rot.map((r, i) => [r, My[i]]).filter(([r]) => r <= 600), { color: '#ff8a3d', width: 4, t: B.start + 0.4, d: 1.0 });
    const l1 = S.div('cut-off at σ<sub>y</sub> → limit load', { x: chc.X(330), y: chc.Y(Mp) - 44, cls: 'small', style: 'color:#ff8a3d' });
    l1.in(B.start + 1.0, 0.5);
    const hard = rot.map((r, i) => [r, Mu[i]]).filter(([r]) => r <= 600);
    chc.curve(hard, { color: COL.cyan, width: 5, t: c('4.3', 'hard'), d: 3.6 });
    const l2 = S.div('hardening to the true ultimate', { x: chc.X(150), y: chc.Y(26.2), cls: 'small c-cyan' });
    l2.in(c('4.3', 'hard') + 1.6, 0.5);
    chc.dot(ep.rot_collapse, ep.M_collapse, { color: '#ffffff', r: 10, t: c('4.3', 'peak') });
    const pl = S.div(`plastic collapse · <span class="num">${ep.M_collapse.toFixed(1)}</span> MNm`, { x: chc.X(ep.rot_collapse), y: chc.Y(ep.M_collapse) - 40, cls: 'label', anchor: 'cm' });
    pl.in(c('4.3', 'peak') + 0.3, 0.5, 'pop');
    const fl = S.path(`M${chc.X(0)},${chc.Y(ep.M_fact)} L${chc.X(600)},${chc.Y(ep.M_fact)}`, { stroke: COL.green, width: 3, dash: '10 7' });
    fl.in(c('4.3', 'res'), 0.6, 'none');
    const fll = S.div(`factored · <span class="num">${ep.M_fact.toFixed(1)}</span>`, { x: chc.X(590), y: chc.Y(ep.M_fact) + 30, cls: 'small c-green', anchor: 'rm' });
    fll.in(c('4.3', 'res') + 0.3, 0.5);
    const eq = S.eq('\\text{capacity} = \\frac{M_{\\text{collapse}}}{\\max\\!\\left[\\,1.2\\,;\\ \\sigma_u/\\sigma_y\\,\\right]}', { x: 120, y: 290, size: 46, align: 'left' });
    eq.in(c('4.3', 'div'), 0.9, 'write');
    const e2 = S.eq(`\\frac{\\sigma_u}{\\sigma_y} = \\frac{${mat.su}}{${mat.sy}} = ${mat.ratio.toFixed(2)} \\;>\\; 1.2`, { x: 120, y: 430, size: 42, align: 'left' });
    e2.in(c('4.3', 'r127'), 0.8, 'write');
    const e3 = S.eq(`\\frac{${ep.M_collapse.toFixed(1)}}{${mat.factor.toFixed(2)}} = \\cg{${ep.M_fact.toFixed(1)}\\ \\mathrm{MNm}}`, { x: 120, y: 550, size: 46, align: 'left' });
    e3.in(c('4.3', 'res'), 0.8, 'write');
    const why = S.card(`<div class="ref">WHY 1.2? · NOTE 2</div><div class="small" style="font-size:24px">ASME VIII-3: margin <span class="num c-amber">1.8</span> on plastic collapse<br>ISO 13628-7: margin <span class="num c-amber">1.5</span> on yielding (limit load)<br>1.8 / 1.5 = <span class="num c-amber">1.2</span></div>`, { x: 110, y: 660, w: 640, cls: 'glass' });
    why.in(c('4.3', 'why'), 0.6, 'rise');
    const ag = S.div(`limit load <span class="num">${Mp.toFixed(1)}</span> · factored collapse <span class="num">${ep.M_fact.toFixed(1)}</span> → within <span class="num">${Math.round((1 - ep.M_fact / Mp) * 100)}</span> %`, { x: 1400, y: 900, cls: 'h3', anchor: 'cm', style: 'font-size:30px' });
    ag.in(c('4.3', 'agree'), 0.6, 'rise');
  }

  // ------------------------------------------------------------------ 4.4 more than one limit on the curve (Figure B.6)
  {
    const B = b('4.4');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · Figure B.6 · B.3.1', B.start + 0.3, B.end);
    const cf = S.chart({ x: 300, y: 180, w: 900, h: 640, xmin: 0, xmax: 1, ymin: 0, ymax: 1.12, xticks: [], yticks: [], xlabel: 'End rotation', ylabel: 'Bending moment', grid: false });
    cf.show(B.start + 0.2);
    const sch = [];
    for (let i = 0; i <= 80; i++) { const x = i / 80; const y = x < 0.18 ? x / 0.18 * 0.62 : 0.62 + 0.38 * (1 - Math.exp(-(x - 0.18) * 5.5)) * (1 - 0.55 * Math.max(0, x - 0.62) ** 2 * 6); sch.push([x, y]); }
    const peak = sch.reduce((a, p) => (p[1] > a[1] ? p : a));
    cf.curve(sch, { color: '#e9f2f9', width: 5, t: B.start + 0.4, d: 1.4 });
    const lv = [['Preload exceedance after 80 % of structural capacity', 0.6, '#7f97aa'], ['Preload exceedance', 0.66, '#9fb2c2'], ['Seal leak tightness', 0.73, COL.green],
      ['Mechanical disengagement', 0.8, COL.violet], ['Limit load', 0.86, COL.amber], ['Plastic collapse', peak[1], COL.cyan]];
    lv.forEach(([name, y, col], i) => {
      const t = c('4.4', 'levels') + i * 0.9;
      const ln = S.path(`M${cf.X(0)},${cf.Y(y)} L${cf.X(0.98)},${cf.Y(y)}`, { stroke: col, width: 2.5, dash: '9 7' });
      ln.in(t, 0.4, 'none');
      const lab = S.div(name, { x: cf.X(1) + 20, y: cf.Y(y), cls: 'small', anchor: 'lm', style: `color:${col};font-size:24px` });
      lab.in(t + 0.1, 0.4, 'left');
    });
    const hi = S.div('', { x: cf.X(0) - 8, y: cf.Y(0.6) - 16, w: 1580, h: 32, cls: 'hl' });
    hi.in(c('4.4', 'lowest'), 0.5, 'pop');
    const ct = S.div('Static capacity = the lowest relevant level (B.3.1)', { x: 960, y: 960, cls: 'h3 c-amber', anchor: 'cm' });
    ct.in(c('4.4', 'lowest') + 0.4, 0.6, 'rise');
    const pt = S.div('Always plot load against rotation or displacement', { x: 960, y: 1010, cls: 'small', anchor: 'cm' });
    pt.in(c('4.4', 'plot'), 0.6);
    S.div('schematic, after NORSOK U-001 Figure B.6', { x: 300, y: 140, cls: 'tiny' }).in(B.start + 0.5, 0.5);
  }

  // ------------------------------------------------------------------ 4.5 the capacity chart
  {
    const B = b('4.5');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.3.6.6 · formula (B.7) · Table B.9', B.start + 0.3, B.end);
    const eq = S.eq('\\left(\\frac{T_w}{T_c} + \\frac{|M|}{M_c}\\right)\\frac{1}{\\cg{F_d}} \\le 1.0', { x: 450, y: 300, size: 52 });
    eq.in(c('4.5', 'b7'), 0.9, 'write');
    S.div('T<sub>w</sub> true wall tension · T<sub>c</sub>, M<sub>c</sub> single load capacities', { x: 450, y: 390, cls: 'small', anchor: 'ct' }).in(c('4.5', 'b7') + 0.8, 0.5);
    capChart(S, D, { t: c('4.5', 'b7') + 1.5, cues: { 0.67: c('4.5', 'n'), 0.8: c('4.5', 'x'), 0.9: c('4.5', 'a'), exact: c('4.5', 'b7') + 3.0 } });
    const nl = S.card(`<div class="ref">NONLINEAR CAPACITIES · B.3.6.5.3 · TABLE B.9</div><div class="small" style="font-size:24px">When pressure or tension changes the bending capacity: analyse with the pressure and tension divided by F<sub>d</sub>, increase the moment to instability, and multiply all loads back by F<sub>d</sub>.</div>`, { x: 110, y: 520, w: 700, cls: 'glass' });
    nl.in(c('4.5', 'nonlin'), 0.6, 'rise');
  }
}
