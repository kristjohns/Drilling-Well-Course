// Chapter 3 — the elastic route: FE model and von Mises contour, why the peak is not the criterion, the SCL, linearisation,
// stress categories, Table B.7 (with the shape factor 1.5), the check with Fd and the fine print (B.3.3, B.3.5.1).
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt, Actor } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause } from '../engine/hud.js';
import { camSpline } from '../three/world.js';
import { FEU, feSetElastic, NECK } from '../three/models.js';
import { quoteCard, stamp, table } from './kit.js';
import { vmLegend, probe3D, datumLoads, note } from './fx.js';

export async function build(E, T, D) {
  const ch = T.ch(3);
  titleCard(ch, 'From six stress components to linearised stresses, and what Table B.7 does with them');
  const W3 = E.world, md = W3.models, M = W3.M;
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const L = D.loads.als, EL = D.elastic.als, mat = D.material, sec = D.section;
  const setFE = () => feSetElastic({ Mw: L.Mw_kNm / 1000, Qw: L.Qw_kN / 1000, Tw: L.Tw_MN, p: D.loads.p_i });
  const lines = md.feHousing.userData.lines;

  // ------------------------------------------------------------------ 3.1 the FE model
  {
    const B = b('3.1');
    const cam = camSpline([
      { t: B.start, p: [2.4, 3.55, 6.5], l: [0.1, 2.98, 0], fov: 32 },
      { t: c('3.1', 'contour'), p: [2.1, 3.6, 5.6], l: [0.1, 3.02, 0], fov: 32 },
      { t: B.end, p: [1.95, 3.62, 5.2], l: [0.1, 3.05, 0], fov: 32 },
    ]);
    W3.shot(B.start, B.end, {
      show: ['feHousing'], fadeIn: 0.8, fadeOut: 0.6, cam, fog: 0, bg: '#0b1824',
      update: (t) => {
        setFE();
        lines.material.opacity = 0.5 * smooth(t, c('3.1', 'mesh') - 0.3, c('3.1', 'mesh') + 0.8);
        FEU.uFE.value = smooth(t, c('3.1', 'contour') - 0.2, c('3.1', 'contour') + 1.4);
      },
    });
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.3.4 analysis model · B.3.5 elastic analysis', B.start + 0.3, B.end);
    const k = S.div('HP WELLHEAD HOUSING · CUT IN HALF', { x: 120, y: 400, cls: 'kicker' });
    k.in(B.start + 0.4, 0.6, 'left');
    const mk = S.div('Mesh refined at the fillet, where stresses change fast (B.3.4)', { x: 120, y: 445, w: 560, cls: 'small' });
    mk.in(c('3.1', 'mesh') + 0.6, 0.6, 'left');
    datumLoads(S, [0, 4.0, 0], { t0: c('3.1', 'loads'), t1: B.end, scale: 0.85,
      labels: { M: `M<sub>w</sub> <span class="num">${fmt(L.Mw_kNm)}</span> kNm`, Q: `Q<sub>w</sub> <span class="num">${fmt(L.Qw_kN)}</span> kN`, T: `T<sub>e</sub> <span class="num">${fmt(L.Te_kN)}</span> kN` } });
    const al = S.div('Table A.4 · accidental (ALS) · 250–500 m', { x: 120, y: 540, cls: 'small c-amber' });
    al.in(c('3.1', 'loads') + 0.4, 0.6, 'left');
    probe3D(S, [0.0, 2.55, -0.16], `p = <span class="num">${D.loads.p_i}</span> MPa <span class="sub">rated working pressure, in the bore</span>`, { t0: c('3.1', 'press'), t1: B.end, dx: 320, dy: 210, color: COL.cyan });
    const six = S.card(`<div class="tiny" style="margin-bottom:8px">AT EVERY POINT</div><div class="eqrow" style="font-size:30px">σ<sub>xx</sub> σ<sub>yy</sub> σ<sub>zz</sub> τ<sub>xy</sub> τ<sub>yz</sub> τ<sub>zx</sub></div>
      <div class="small" style="margin-top:10px">→ one number for the plot: the von Mises equivalent stress σ<sub>e</sub></div>`, { x: 120, y: 700, w: 560, cls: 'glass' });
    six.in(c('3.1', 'contour'), 0.6, 'rise');
    vmLegend(S, { x: 1630, y: 250, t0: c('3.1', 'vm'), t1: B.end });
    note(S, 'Illustrative stress field (teaching stand-in, not an FE result)', { t0: c('3.1', 'contour') + 1, t1: B.end - 0.4 });
  }

  // ------------------------------------------------------------------ 3.2 von Mises
  {
    const B = b('3.2');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.3.5.1 · von Mises or Tresca', B.start + 0.3, B.end);
    const eq = S.eq('\\sigma_e = \\sqrt{\\tfrac{1}{2}\\Big[(\\sigma_1-\\sigma_2)^2 + (\\sigma_2-\\sigma_3)^2 + (\\sigma_3-\\sigma_1)^2\\Big]}', { x: 960, y: 210, size: 58 });
    eq.in(B.start + 0.4, 1.0, 'write');
    // two elements: equal stresses (no distortion) and unequal stresses (distortion)
    const box = (cx, cy, tag, sx, sy, t0, txt) => {
      const g = S.g();
      g.in(t0, 0.6, 'none');
      const sq = S.path('M0,0', { stroke: '#d7e3ec', width: 3, fill: 'rgba(143,163,181,0.35)', parent: g.el, o: 1 });
      const ghost = S.path(`M${cx - 110},${cy - 110} L${cx + 110},${cy - 110} L${cx + 110},${cy + 110} L${cx - 110},${cy + 110} Z`, { stroke: 'rgba(215,227,236,0.35)', width: 2, dash: '8 8', parent: g.el, o: 1 });
      const arr = [];
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) arr.push(S.arrow(0, 0, 0, 0, { color: dx ? COL.coral : COL.cyan, width: 5, parent: g.el, o: 1 }));
      const lab = S.div(tag, { x: cx, y: cy + 210, cls: 'h3', anchor: 'ct' });
      lab.in(t0 + 0.3, 0.5);
      const res = S.div(txt, { x: cx, y: cy + 262, cls: 'small', anchor: 'ct' });
      res.in(t0 + 1.4, 0.5);
      E.anim(t0, B.end, (t) => {
        const u = ease.inOut(clamp((t - t0 - 0.4) / 1.6));
        const hx = 110 * (1 + sx * 0.28 * u), hy = 110 * (1 + sy * 0.28 * u);
        sq.el.setAttribute('d', `M${cx - hx},${cy - hy} L${cx + hx},${cy - hy} L${cx + hx},${cy + hy} L${cx - hx},${cy + hy} Z`);
        const set = (a, x1, y1, x2, y2) => {
          const ang = Math.atan2(y2 - y1, x2 - x1), bx = x2 - Math.cos(ang) * 13, by = y2 - Math.sin(ang) * 13;
          a.shaft.el.setAttribute('d', `M${x1.toFixed(1)},${y1.toFixed(1)} L${bx.toFixed(1)},${by.toFixed(1)}`);
          const h = (q) => [x2 - Math.cos(ang + q) * 16, y2 - Math.sin(ang + q) * 16];
          a.tip.el.setAttribute('d', `M${h(0.45).join(',')} L${x2},${y2} L${h(-0.45).join(',')} Z`);
        };
        const out = (s) => (s > 0 ? 1 : -1);
        set(arr[0], cx + hx + (sx > 0 ? 8 : 78), cy, cx + hx + (sx > 0 ? 78 : 8), cy);
        set(arr[1], cx - hx - (sx > 0 ? 8 : 78), cy, cx - hx - (sx > 0 ? 78 : 8), cy);
        set(arr[2], cx, cy + hy + (sy > 0 ? 8 : 78), cx, cy + hy + (sy > 0 ? 78 : 8));
        set(arr[3], cx, cy - hy - (sy > 0 ? 8 : 78), cx, cy - hy - (sy > 0 ? 78 : 8));
        void out;
      });
    };
    box(620, 560, 'Equal stresses (pressure)', -0.6, -0.6, c('3.2', 'dist') - 0.6, 'squeezed, not distorted → σ<sub>e</sub> = 0');
    box(1300, 560, 'Unequal stresses', 1.0, -0.7, c('3.2', 'dist') + 1.6, 'distorted → σ<sub>e</sub> &gt; 0');
    const yl = S.div('σ<sub>e</sub> = σ<sub>y</sub> &nbsp;→&nbsp; yielding starts', { x: 960, y: 905, cls: 'h3 c-amber', anchor: 'cm' });
    yl.in(c('3.2', 'equal'), 0.6, 'rise');
    const tr = S.div('NORSOK: von Mises (distortion energy) or Tresca (maximum shear)', { x: 960, y: 960, cls: 'small', anchor: 'cm' });
    tr.in(c('3.2', 'crit'), 0.6);
  }

  // ------------------------------------------------------------------ 3.3 the peak is not the criterion
  {
    const B = b('3.3');
    const cam = camSpline([
      { t: B.start, p: [1.05, 3.56, 2.0], l: [0.35, 3.36, 0], fov: 30 },
      { t: c('3.3', 'peak') + 1.0, p: [0.78, 3.47, 1.0], l: [0.55, 3.41, 0], fov: 30 },
      { t: B.end, p: [0.8, 3.48, 1.05], l: [0.55, 3.41, 0], fov: 30 },
    ]);
    W3.shot(B.start, B.end, {
      show: ['feHousing'], fadeIn: 0.7, fadeOut: 0.5, cam, fog: 0, bg: '#0b1824',
      update: () => { setFE(); lines.material.opacity = 0.5; FEU.uFE.value = 1; },
    });
    const S = new Scene(B.start, B.end);
    clause('Peak stress · local, self-limiting · fatigue', B.start + 0.3, B.end);
    probe3D(S, [0.352, 3.416, 0.0], `<span style="font-size:36px;font-weight:800;color:#ff5a4a" class="num">793 MPa</span><span class="sub">peak, neck fillet</span>`, { t0: c('3.3', 'peak'), t1: B.end, dx: -250, dy: 200, color: '#ff5a4a' });
    // magnifier: the wall near the fillet in section, red skin about 10 mm deep
    const cx = 1420, cy = 520, R = 300;
    const mg = S.g();
    mg.in(c('3.3', 'peak') + 0.8, 0.7, 'none');
    const clipId = 'mag' + Math.random().toString(36).slice(2, 7);
    const cp = document.createElementNS('http://www.w3.org/2000/svg', 'clipPath'); cp.setAttribute('id', clipId);
    const cc = document.createElementNS('http://www.w3.org/2000/svg', 'circle'); cc.setAttribute('cx', cx); cc.setAttribute('cy', cy); cc.setAttribute('r', R);
    cp.appendChild(cc); S.svg.querySelector('defs').appendChild(cp);
    S.circle(cx, cy, R, { fill: '#0d1d2b', stroke: 'none', parent: mg.el, o: 1 });
    const inner = document.createElementNS('http://www.w3.org/2000/svg', 'g'); inner.setAttribute('clip-path', `url(#${clipId})`); mg.el.appendChild(inner);
    // scale: 1 mm = 5 px; wall from the bore (left) to the outside surface (x = cx + 130), fillet arc to the hub above
    const ox = cx + 130, oy = cy + 40;                    // fillet root on the outside surface
    const P = (d, o) => S.path(d, { parent: inner, o: 1, ...o });
    P(`M${cx - 420},${cy + 400} L${cx - 420},${cy - 400} L${ox + 175},${cy - 400} L${ox + 175},${oy - 175} A175,175 0 0 0 ${ox},${oy} L${ox},${cy + 400} Z`, { fill: '#e8c547', stroke: 'none' });
    P(`M${ox - 60},${cy + 400} L${ox - 60},${oy} A235,235 0 0 1 ${ox + 175},${oy - 235} L${ox + 175},${oy - 175} A175,175 0 0 0 ${ox},${oy} L${ox},${cy + 400} Z`, { fill: '#f39a2e', stroke: 'none' });
    const skin = P(`M${ox - 22},${cy + 220} L${ox - 22},${oy} A197,197 0 0 1 ${ox + 70},${oy - 160} L${ox + 60},${oy - 140} A175,175 0 0 0 ${ox},${oy} L${ox},${cy + 220} Z`, { fill: '#e8352a', stroke: 'none' });
    P(`M${ox},${cy + 400} L${ox},${oy} A175,175 0 0 1 ${ox + 175},${oy - 175}`, { stroke: '#ffffff', width: 3 });
    S.circle(cx, cy, R, { fill: 'none', stroke: '#d7e3ec', width: 4, parent: mg.el, o: 1 });
    const sb = S.path(`M${ox - 110},${cy + 200} L${ox - 60},${cy + 200}`, { stroke: '#fff', width: 4, parent: mg.el, o: 1 });
    const sbl = S.div('10 mm', { x: ox - 85, y: cy + 212, cls: 'tiny', anchor: 'ct', style: 'color:#06121c;font-weight:800' });
    sbl.in(c('3.3', 'peak') + 1.4, 0.4);
    const ml = S.div('the peak lives in a skin ≈ 1 cm deep', { x: cx, y: cy + R + 30, cls: 'small', anchor: 'ct' });
    ml.in(c('3.3', 'peak') + 1.6, 0.5);
    // the skin yields, the load moves inwards
    const tl = c('3.3', 'local');
    skin.set(tl + 0.4, {}).to(tl + 0.4, 0.8, { o: 0.35 });
    const hat = P(`M${ox - 22},${cy + 220} L${ox - 22},${oy} A197,197 0 0 1 ${ox + 70},${oy - 160} L${ox + 60},${oy - 140} A175,175 0 0 0 ${ox},${oy} L${ox},${cy + 220} Z`, { fill: 'url(#hatch)', stroke: 'none' });
    hat.T('o').init = 0; hat.in(tl + 0.5, 0.6, 'none');
    for (let i = 0; i < 3; i++) {
      const a = S.arrow(ox - 40, cy + 120 - i * 70, ox - 170, cy + 120 - i * 70, { color: '#ffffff', width: 4, parent: mg.el });
      a.in(tl + 1.0 + i * 0.25, 0.4, 'none');
    }
    const rl = S.div('it yields → the load moves to the material next to it', { x: cx, y: cy + R + 70, cls: 'small c-amber', anchor: 'ct' });
    rl.in(tl + 1.2, 0.5);
    const ft = S.card(`<div class="ref" style="color:#ff6f61">PEAK STRESS (F)</div><div style="font-weight:700;font-size:30px">→ fatigue: where cracks start</div>`, { x: 120, y: 160, w: 560, cls: 'glass' });
    ft.in(c('3.3', 'fatigue'), 0.6, 'left');
    const st = S.card(`<div class="ref">STATIC STRENGTH</div><div style="font-weight:700;font-size:30px">peak vs σ<sub>y</sub> &nbsp;<span class="c-red">✗ the wrong question</span></div>`, { x: 120, y: 330, w: 560, cls: 'glass' });
    st.in(c('3.3', 'static'), 0.6, 'left');
    void sb;
  }

  // ------------------------------------------------------------------ 3.4 the stress classification line
  const xs = EL.x_mm;
  const ptsOf = (arr) => xs.map((x, i) => [x, arr[i]]);
  {
    const B = b('3.4');
    const panel = { x: 60, y: 150, w: 800, h: 800 };
    const cam = camSpline([
      { t: B.start, p: [0.55, 3.45, 0.95], l: [0.33, 3.405, 0], fov: 34 },
      { t: c('3.4', 'scl') + 1.0, p: [0.42, 3.43, 0.6], l: [0.295, 3.405, 0], fov: 34 },
      { t: B.end, p: [0.41, 3.43, 0.58], l: [0.295, 3.405, 0], fov: 34 },
    ]);
    W3.shot(B.start, B.end, {
      show: ['feHousing'], fadeIn: 0.6, fadeOut: 0.4, cam, fog: 0, bg: '#0b1824', panel,
      update: (t) => {
        setFE(); lines.material.opacity = 0.5; FEU.uFE.value = 1;
        const sc = md.feHousing.userData.scl;
        sc.visible = t > c('3.4', 'scl') - 0.1;
        md.feHousing.userData.sclMat.opacity = smooth(t, c('3.4', 'scl') - 0.1, c('3.4', 'scl') + 0.5);
      },
    });
    const S = new Scene(B.start, B.end);
    clause('ASME BPVC VIII-2 Annex 5-A · stress classification line', B.start + 0.3, B.end);
    probe3D(S, [(NECK.ri + NECK.ro) / 2, NECK.y1, 0.0], 'SCL <span class="sub">bore → outside · t = 112 mm</span>', { t0: c('3.4', 'scl') + 0.3, t1: B.end, dx: -160, dy: 230, color: '#ffffff' });
    const bo = S.div('bore', { x: 0, y: 0, cls: 'tiny', style: 'color:#fff' }), ou = S.div('outside', { x: 0, y: 0, cls: 'tiny', style: 'color:#fff' });
    bo.in(c('3.4', 'scl') + 0.6, 0.4); ou.in(c('3.4', 'scl') + 0.6, 0.4);
    E.anim(c('3.4', 'scl'), B.end, (t) => {
      const a = W3.project([NECK.ri, NECK.y1, 0], t), q = W3.project([NECK.ro, NECK.y1, 0], t);
      bo.el.style.left = (a.x - 40) + 'px'; bo.el.style.top = (a.y - 46) + 'px';
      ou.el.style.left = (q.x - 30) + 'px'; ou.el.style.top = (q.y - 46) + 'px';
    });
    const chp = S.chart({ x: 1010, y: 220, w: 800, h: 600, xmin: 0, xmax: 112, ymin: -100, ymax: 900, xticks: [0, 28, 56, 84, 112], yticks: [-100, 100, 300, 500, 700, 900],
      xlabel: 'Distance along the SCL from the bore · mm', ylabel: 'Stress · MPa', title: 'STRESS COMPONENTS ALONG THE SCL' });
    chp.show(c('3.4', 'path'));
    chp.curve(ptsOf(EL.sa), { color: COL.coral, width: 5, t: c('3.4', 'axial'), d: 1.2 });
    chp.curve(ptsOf(EL.sh), { color: COL.cyan, width: 4, t: c('3.4', 'hoop'), d: 1.0 });
    chp.curve(ptsOf(EL.sr), { color: COL.violet, width: 4, t: c('3.4', 'hoop') + 0.6, d: 1.0 });
    const lg = (t, y, col, txt) => { const a = S.div(`<span style="display:inline-block;width:28px;height:5px;background:${col};vertical-align:middle;margin-right:10px"></span>${txt}`, { x: 1040, y, cls: 'small' }); a.in(t, 0.5, 'left'); };
    lg(c('3.4', 'axial') + 0.4, 260, COL.coral, 'axial · bending + tension');
    lg(c('3.4', 'hoop') + 0.4, 300, COL.cyan, 'hoop · pressure');
    lg(c('3.4', 'hoop') + 0.9, 340, COL.violet, 'radial · pressure');
  }

  // ------------------------------------------------------------------ 3.5 linearisation
  {
    const B = b('3.5');
    const S = new Scene(B.start, B.end);
    clause('ASME BPVC VIII-2 Annex 5-A · linearisation', B.start + 0.3, B.end);
    const chl = S.chart({ x: 980, y: 200, w: 820, h: 600, xmin: 0, xmax: 112, ymin: 200, ymax: 900, xticks: [0, 28, 56, 84, 112], yticks: [200, 300, 400, 500, 600, 700, 800, 900],
      xlabel: 'Distance along the SCL from the bore · mm', ylabel: 'Axial stress · MPa', title: 'AXIAL STRESS ALONG THE SCL' });
    chl.show(B.start + 0.2);
    const tot = ptsOf(EL.sa);
    chl.curve(tot, { color: COL.coral, width: 5, t: B.start + 0.4, d: 1.0 });
    const [mA, bA] = EL.lin.a;
    const linAt = (x) => mA + bA * (1 - 2 * x / 112);
    chl.curve([[0, mA], [112, mA]], { color: '#ffffff', width: 4, t: c('3.5', 'mem'), d: 0.8 });
    const ml = S.div(`membrane <span class="num">${fmt(mA)}</span>`, { x: chl.X(6), y: chl.Y(mA) - 34, cls: 'small', style: 'color:#fff' });
    ml.in(c('3.5', 'mem') + 0.5, 0.5);
    chl.curve([[0, linAt(0)], [112, linAt(112)]], { color: COL.amber, width: 4, t: c('3.5', 'bend'), d: 0.8 });
    const bl = S.div(`membrane + bending <span class="num">${fmt(linAt(112))}</span>`, { x: chl.X(54), y: chl.Y(linAt(112)) - 6, cls: 'small c-amber', anchor: 'cb' });
    bl.in(c('3.5', 'bend') + 0.5, 0.5);
    // peak = what is left: shaded between the total and the linear line
    const pk = tot.map(([x, y]) => [x, y]);
    const pd = chl.pathD(pk) + ' ' + [...tot].reverse().map(([x]) => `L${chl.X(x).toFixed(1)},${chl.Y(linAt(x)).toFixed(1)}`).join(' ') + ' Z';
    const ph = S.path(pd, { stroke: 'none', fill: 'rgba(255,111,97,0.32)', parent: chl.plot });
    ph.T('o').init = 0; ph.in(c('3.5', 'pk'), 0.6, 'none');
    const pl = S.div('peak', { x: chl.X(101), y: chl.Y(780), cls: 'small c-coral', anchor: 'rm' });
    pl.in(c('3.5', 'pk') + 0.3, 0.5);
    const f1 = S.eq('\\sigma_m = \\frac{1}{t}\\int_0^t \\sigma\\,dx', { x: 120, y: 290, size: 46, align: 'left' });
    f1.in(c('3.5', 'mem'), 0.8, 'write');
    S.div('membrane = the average over the wall', { x: 124, y: 360, cls: 'small' }).in(c('3.5', 'mem') + 0.6, 0.5);
    const f2 = S.eq('\\sigma_b = \\frac{6}{t^2}\\int_0^t \\sigma\\left(\\tfrac{t}{2}-x\\right)dx', { x: 120, y: 470, size: 46, align: 'left' });
    f2.in(c('3.5', 'bend'), 0.8, 'write');
    S.div('bending = the linear part with the same moment', { x: 124, y: 545, cls: 'small' }).in(c('3.5', 'bend') + 0.6, 0.5);
    S.div('peak = total − membrane − bending', { x: 124, y: 610, cls: 'small c-coral' }).in(c('3.5', 'pk'), 0.5);
    // FE post-processor style output
    const rows = [['Membrane', fmt(EL.mem_vm), 'm482'], ['Membrane + bending', fmt(EL.mb_vm), 'mb613'], ['Peak (total − M+B)', fmt(EL.peak_vm_out), 'p180'], ['Total', fmt(EL.total_vm_out), 'p180']];
    const tb = S.card(`<div class="tiny" style="margin-bottom:10px">LINEARISED STRESS · VON MISES (MPa) · OUTSIDE SURFACE</div>` +
      rows.map(([a, v], i) => `<div class="lr" data-i="${i}" style="display:flex;justify-content:space-between;font-size:27px;padding:5px 0;border-top:1px solid rgba(190,220,245,0.1)"><span>${a}</span><span class="num">${v}</span></div>`).join(''),
    { x: 120, y: 700, w: 620, cls: 'glass' });
    tb.in(c('3.5', 'table'), 0.6, 'rise');
    const rws = [...tb.el.querySelectorAll('.lr')].map((el) => S.track(new Actor(el, { o: 0 })));
    rws[0].in(c('3.5', 'm482'), 0.4, 'none'); rws[1].in(c('3.5', 'mb613'), 0.4, 'none'); rws[2].in(c('3.5', 'p180'), 0.4, 'none'); rws[3].in(c('3.5', 'p180') + 0.8, 0.4, 'none');
  }

  // ------------------------------------------------------------------ 3.6 stress categories
  {
    const B = b('3.6');
    const S = new Scene(B.start, B.end);
    clause('ASME BPVC VIII-2 5.2.2 · NORSOK U-001 B.3.5.1', B.start + 0.3, B.end);
    S.div('Every part gets a category', { x: 960, y: 140, cls: 'h2', anchor: 'ct' }).in(B.start + 0.3, 0.6, 'write');
    // mini through-wall profiles
    const mini = (x, y, kind, color) => {
      const g = S.g();
      const w = 150, h = 90;
      S.rect(x, y, w, h, { fill: 'rgba(143,163,181,0.12)', stroke: 'rgba(190,220,245,0.25)', width: 1.5, parent: g.el, o: 1 });
      const P = (d) => S.path(d, { stroke: color, width: 4, parent: g.el, o: 1 });
      const z = y + h * 0.75;
      S.line(x, z, x + w, z, { stroke: 'rgba(190,220,245,0.4)', width: 1.5, parent: g.el, o: 1 });
      if (kind === 'm') P(`M${x},${y + 25} L${x + w},${y + 25}`);
      if (kind === 'b') P(`M${x},${y + 8} L${x + w},${z + 12}`);
      if (kind === 'q') P(`M${x},${z + 10} L${x + w},${y + 10}`);
      if (kind === 'f') P(`M${x},${y + 45} L${x + w - 40},${y + 45} C${x + w - 15},${y + 45} ${x + w - 6},${y + 20} ${x + w},${y + 2}`);
      return g;
    };
    const card = (x, w, ref, color, title, body, t) => {
      const a = S.card(`<div class="ref" style="color:${color}">${ref}</div><div style="font-weight:750;font-size:32px;margin-bottom:10px">${title}</div><div class="small">${body}</div>`, { x, y: 240, w, h: 330, cls: 'glass' });
      a.in(t - 0.2, 0.6, 'rise');
      return a;
    };
    card(110, 860, 'PRIMARY · P', COL.amber, 'Carries the load', 'equilibrium with the applied loads · not self-limiting', c('3.6', 'prim'));
    card(1010, 380, 'SECONDARY · Q', COL.cyan, 'From constraint', 'thermal, preload · self-limiting', c('3.6', 'sec'));
    card(1430, 380, 'PEAK · F', COL.coral, 'Local', 'notches, fillets · fatigue only', c('3.6', 'pk'));
    const sub = (x, t, name, txt, kind) => {
      const g = mini(x, 455, kind, COL.amber); g.in(t, 0.5, 'none');
      const l = S.div(`<span class="num" style="font-size:30px;color:#ffb547">${name}</span><div class="tiny" style="margin-top:4px">${txt}</div>`, { x, y: 590, w: 260 });
      l.in(t + 0.2, 0.5, 'rise');
    };
    sub(150, c('3.6', 'pm'), 'P<sub>m</sub>', 'general membrane', 'm');
    sub(430, c('3.6', 'pl'), 'P<sub>L</sub>', 'local membrane, near a discontinuity', 'm');
    sub(710, c('3.6', 'pb'), 'P<sub>b</sub>', 'bending', 'b');
    const gq = mini(1050, 455, 'q', COL.cyan); gq.in(c('3.6', 'sec') + 0.4, 0.5, 'none');
    const gf = mini(1470, 455, 'f', COL.coral); gf.in(c('3.6', 'pk') + 0.3, 0.5, 'none');
    S.div('stress across the wall', { x: 960, y: 700, cls: 'tiny', anchor: 'ct' }).in(c('3.6', 'pm') + 0.5, 0.5);
    const pre = S.card(`<div class="ref">B.3.5.1 · PRELOADED EQUIPMENT</div><div style="font-weight:650;font-size:29px">If primary and secondary stresses cannot be separated, treat the total as primary.</div>`, { x: 960, y: 790, w: 1100, cls: 'glass', anchor: 'ct' });
    pre.in(c('3.6', 'preload'), 0.6, 'rise');
  }

  // ------------------------------------------------------------------ 3.7 Table B.7 and the shape factor
  {
    const B = b('3.7');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.3.5.2 · Table B.7', B.start + 0.3, B.end);
    const rows = [
      ['pm', 'General / local primary membrane, P<sub>m</sub>, P<sub>L</sub>', '(σ<sub>eq</sub>) ≤ σ<sub>y</sub>'],
      ['pb', 'Primary membrane + primary bending, P<sub>m/L</sub> + P<sub>b</sub>', '(σ<sub>eq</sub>) ≤ 1.5 σ<sub>y</sub>'],
      ['pq', 'Primary + secondary stress range, P + Q', '(σ<sub>eq</sub>) ≤ 2.0 σ<sub>y</sub>'],
      ['sh', 'Primary average shear, P<sub>sh</sub>', 'τ ≤ 0.57 σ<sub>y</sub>'],
      ['sh2', 'Average bearing stress, P<sub>br</sub>', 'σ<sub>br</sub> ≤ σ<sub>y</sub>'],
    ];
    S.div('TABLE B.7 · LINEARISED EQUIVALENT VON MISES STRESS · ALLOWABLE AT YIELDING CAPACITY', { x: 110, y: 150, cls: 'tiny', style: 'color:#4fd1ff' }).in(B.start + 0.3, 0.5);
    rows.forEach(([k, a, v], i) => {
      const r = S.div(`<div style="display:flex;align-items:center;height:70px;padding:0 22px;border-radius:12px;background:rgba(16,36,54,0.82);border:1px solid rgba(190,220,245,0.12)">
        <div style="width:560px;font-size:25px;font-weight:550">${a}</div><div style="width:250px;text-align:right;font-weight:750;font-size:30px;color:#ffb547">${v}</div></div>`, { x: 110, y: 200 + i * 84, w: 860 });
      r.in(c('3.7', k === 'sh2' ? 'sh' : k) + (k === 'sh2' ? 1.4 : 0), 0.5, 'left');
    });
    // shape factor: rectangular wall section, stress block from triangle (first yield) to rectangle (fully plastic)
    const x0 = 1190, y0 = 230, h = 280, bw = 70;
    const g = S.g(); g.in(c('3.7', 'why'), 0.6, 'none');
    S.rect(x0, y0, bw, h, { fill: '#7f93a6', stroke: '#d7e3ec', width: 2, parent: g.el, o: 1 });
    S.div('wall', { x: x0 + bw / 2, y: y0 + h + 14, cls: 'tiny', anchor: 'ct' }).in(c('3.7', 'why'), 0.5);
    const ax = x0 + bw + 120;
    S.line(ax, y0 - 20, ax, y0 + h + 20, { stroke: 'rgba(200,225,245,0.6)', width: 2, parent: g.el, o: 1 });
    const blk = S.path('M0,0', { stroke: COL.amber, width: 3, fill: 'rgba(255,181,71,0.35)', parent: g.el, o: 1 });
    const sy = 150;
    const tf = c('3.7', 'first'), tp = c('3.7', 'full');
    E.anim(B.start, B.end, (t) => {
      const u = ease.inOut(clamp((t - tp - 0.4) / 3.0));              // 0: triangle (first yield), 1: rectangle (plastic)
      const ye = (h / 2) * (1 - u);                                       // half depth of the elastic core
      const ym = y0 + h / 2;
      const pts = [[ax, y0], [ax + sy, y0], [ax + sy, ym - ye], [ax, ym], [ax - sy, ym + ye], [ax - sy, y0 + h], [ax, y0 + h]];
      if (ye < 1e-3) { pts[2] = [ax + sy, ym]; pts[4] = [ax - sy, ym]; }
      blk.el.setAttribute('d', `M${ax},${y0} L${ax + sy},${y0} L${ax + sy},${ym - ye} L${ax},${ym} L${ax - sy},${ym + ye} L${ax - sy},${y0 + h} L${ax},${y0 + h} Z`);
    });
    const sl = S.div('σ<sub>y</sub>', { x: ax + sy + 10, y: y0 - 6, cls: 'small c-amber' }); sl.in(tf, 0.5);
    const e1 = S.eq('M_y = \\sigma_y\\,\\frac{b\\,h^2}{6}', { x: 1290, y: 640, size: 42 });
    e1.in(tf + 0.6, 0.8, 'write');
    S.div('first yield at the surface', { x: 1290, y: 700, cls: 'small', anchor: 'ct' }).in(tf + 1.0, 0.5);
    const e2 = S.eq('M_p = \\sigma_y\\,\\frac{b\\,h^2}{4}', { x: 1660, y: 640, size: 42 });
    e2.in(tp + 2.6, 0.8, 'write');
    S.div('whole thickness yielded', { x: 1660, y: 700, cls: 'small', anchor: 'ct' }).in(tp + 3.0, 0.5);
    const r = S.eq('\\frac{M_p}{M_y} = 1.5', { x: 1475, y: 840, size: 52 });
    r.in(c('3.7', 'ratio'), 0.8, 'write');
    r.boxed(c('3.7', 'ratio') + 0.6, { color: COL.amber });
    const shr = S.div('0.57 ≈ 1/√3 &nbsp;·&nbsp; von Mises shear yield τ<sub>y</sub> = σ<sub>y</sub>/√3', { x: 540, y: 680, cls: 'h3', anchor: 'ct', style: 'font-size:30px' });
    shr.in(c('3.7', 'shear'), 0.6, 'rise');
  }

  // ------------------------------------------------------------------ 3.8 with the design factor, and the fine print
  {
    const B = b('3.8');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.2.5 · B.3.3 · B.3.5.1', B.start + 0.3, B.end);
    S.div('Accidental case · F<sub>d</sub> = 0.9', { x: 110, y: 140, cls: 'h2' }).in(B.start + 0.3, 0.6, 'write');
    const bar = (y, label, val, allow, allowTxt, t, uf) => {
      const W0 = 900, x0 = 560;
      const S2 = S;
      const lab = S2.div(label, { x: 110, y, cls: 'h3', style: 'font-size:30px' }); lab.in(t, 0.5, 'left');
      const full = S2.rect(x0, y + 4, W0, 40, { fill: 'rgba(190,220,245,0.06)', stroke: 'rgba(190,220,245,0.2)', width: 1, rx: 8 }); full.in(t, 0.4, 'none');
      const vmax = Math.max(val, allow) * 1.15;
      const fill = S2.rect(0, y + 4, W0 * val / vmax, 40, { fill: uf > 1 ? COL.red : COL.green, stroke: 'none', rx: 8, opacity: 0.85 });
      fill.baseTf = `translate(${x0} 0)`;
      fill.set(0, { sx: 0 }).to(t + 0.2, 1.0, { sx: 1 }, ease.out3); fill.in(t, 0.2, 'none');
      const ax = x0 + W0 * allow / vmax;
      const lim = S2.line(ax, y - 14, ax, y + 62, { stroke: '#ffffff', width: 4 }); lim.in(t + 0.6, 0.4, 'none');
      const lt = S2.div(allowTxt, { x: ax, y: y + 70, cls: 'small', anchor: 'ct', style: 'color:#fff' }); lt.in(t + 0.8, 0.5);
      const vt = S2.div(`<span class="num">${fmt(val)}</span> MPa`, { x: x0 + W0 * val / vmax + 16, y: y + 24, cls: 'h3', anchor: 'lm', style: `color:${uf > 1 ? '#ff4d5e' : '#46d39a'};font-size:30px` }); vt.in(t + 1.0, 0.5);
      return { lab, full, fill, lim, lt, vt };
    };
    const b1 = bar(270, 'P<sub>L</sub> · membrane', EL.mem_vm, EL.allow_PL, `0.9 × ${mat.sy} = ${fmt(EL.allow_PL)}`, c('3.8', 'pl'), EL.uf_PL);
    stamp(S, `${EL.uf_PL.toFixed(2)} · FAIL`, { x: 1660, y: 300, t: c('3.8', 'fail'), kind: 'fail' });
    const b2 = bar(430, 'P<sub>L</sub> + P<sub>b</sub>', EL.mb_vm, EL.allow_PLPb, `1.5 × 0.9 × ${mat.sy} = ${fmt(EL.allow_PLPb)}`, c('3.8', 'plpb'), EL.uf_PLPb);
    stamp(S, `${EL.uf_PLPb.toFixed(2)} · pass`, { x: 1660, y: 460, t: c('3.8', 'plpb') + 1.2, kind: 'pass' });
    const fp = S.div('The fine print', { x: 110, y: 610, cls: 'h3 c-amber' });
    fp.in(c('3.8', 'but'), 0.5, 'left');
    const fc = (x, ref, txt, t) => { const a = S.card(`<div class="ref">${ref}</div><div style="font-weight:650;font-size:28px;line-height:1.3">${txt}</div>`, { x, y: 670, w: 540, cls: 'glass' }); a.in(t, 0.6, 'rise'); return a; };
    fc(110, 'B.3.3', 'Elastic analysis is limited to <span class="c-amber">preliminary design</span>', c('3.8', 'prelim'));
    fc(690, 'B.3.5.1', 'Pressure-containing parts only with <span class="c-amber">D/t &gt; 10</span>', c('3.8', 'dt'));
    const nk = S.card(`<div class="ref">OUR NECK</div><div style="font-weight:750;font-size:30px">D/t = <span class="num">${sec.D.toFixed(2)}</span> / <span class="num">${sec.t.toFixed(3)}</span> = <span class="num c-red">${sec.Dt.toFixed(2)}</span></div>`, { x: 1270, y: 670, w: 540, cls: 'glass' });
    nk.in(c('3.8', 'neck'), 0.6, 'rise');
    stamp(S, 'not permitted for acceptance', { x: 1540, y: 890, t: c('3.8', 'notallowed'), kind: 'fail', size: 26 });
    const go = S.div('→ we need the direct method', { x: 110, y: 960, cls: 'h3', style: 'color:#46d39a' });
    go.in(c('3.8', 'notallowed') + 1.6, 0.6, 'left');
    void b1; void b2;
  }
}
