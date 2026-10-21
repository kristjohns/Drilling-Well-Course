// Chapter 4 — load paths and load share: contact areas A-H, three paths, springs in parallel, Table 4, bonded strings,
// the template as a rotational spring (with a gap), and the 100 mm relative vertical displacement.
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt } from '../engine/core.js';
import { Scene } from '../engine/scene.js';
import { titleCard, clause, step } from '../engine/hud.js';
import { camPath, camSpline, DEF, THREE } from '../three/world.js';
import { updateSnow } from '../three/models.js';
import { quoteCard, derivation, table, tx, letter3D, label3D } from './kit.js';
import { springPath, ground, tubeSection } from './drawings.js';

export async function build(E, T, D) {
  const ch = T.ch(4);
  titleCard(ch, 'Step 2 · where the moment goes (Annex J, clauses 8.1 and 13.3.6)');
  step(ch.title_card[1], 1);
  const W3 = E.world, md = W3.models, M = W3.M;
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);

  // ------------------------------------------------------------------ 4.1 + 4.2 contact areas and load paths (3D)
  const B1 = b('4.1'), B2 = b('4.2');
  // the well sits left of centre so the list panel on the right does not cover it
  const cam = camSpline([
    { t: B1.start, p: [7.6, 2.6, 13.0], l: [1.6, 1.4, -0.7], fov: 40 },
    { t: c('4.1', 'D'), p: [8.0, 2.2, 13.6], l: [1.8, 0.9, -0.8], fov: 40 },
    { t: c('4.1', 'E'), p: [8.7, 1.9, 14.6], l: [2.0, 0.0, -0.9], fov: 41 },
    { t: B2.end, p: [8.4, 1.6, 14.2], l: [2.0, -0.2, -0.9], fov: 41 },
  ]);
  W3.shot(B1.start, B2.end, {
    show: ['wellCut', 'templateCut', 'seabedCut', 'snow', 'connCut'],
    fadeIn: 0.8, fadeOut: 0.8, cam, fog: 0.01, bg: '#082b42',
    update: (t) => {
      W3.update(t); updateSnow(md.snow, t);
      for (const k in md.wellCut.userData.parts) md.wellCut.userData.parts[k].position.y = 0;
      md.connCut.position.y = 0;
      DEF.uAmp.value = 0; DEF.uGlow.value = 0; DEF.uStressMix.value = 0; M.cond.emissive.setRGB(0, 0, 0);
    },
  });
  const S1 = new Scene(B1.start, B2.end);
  clause('NORSOK U-001:2026 · Figure J.1 · J.2.1', B1.start + 0.3, B2.end);
  const P = { F: [0.0, 4.25, 0], A: [0.41, 3.05, 0], B: [0.39, 1.22, 0], C: [0.6, 2.42, 0], D: [0.5, 0.40, 0], G: [2.9, 0.05, 0], E: [0.33, -5.0, 0], H: [0.52, -2.6, 0] };
  const desc = { F: 'WH / WH connector', A: 'top of WH / conductor housing', B: 'bottom of WH / conductor housing', C: 'template / conductor housing',
    D: 'bottom of structure / conductor housing', G: 'structure / seabed', E: 'top of cement, conductor / surface casing', H: 'conductor / soil and cement' };
  const order = ['F', 'A', 'B', 'C', 'D', 'G', 'E', 'H'];
  const panel = S1.card('<div class="tiny" style="letter-spacing:0.14em">CONTACT AREAS · FIGURE J.1</div>', { x: 1250, y: 150, w: 630, h: 610, cls: 'glass' });
  panel.in(c('4.1', 'F') - 0.4, 0.5, 'none').out(B2.start + 0.2, 0.5);
  order.forEach((k, i) => {
    const t0 = c('4.1', k);
    letter3D(S1, P[k], k, { t0, t1: B2.end });
    const row = S1.div(`<span style="display:inline-block;width:34px;height:34px;border-radius:50%;background:#ffb547;color:#06121c;font-weight:800;text-align:center;line-height:34px;margin-right:14px">${k}</span>${desc[k]}`, { x: 1282, y: 238 + i * 63, cls: 'small', style: 'color:#e9f2f9' });
    row.in(t0, 0.45, 'left');
    row.out(B2.start + 0.2, 0.5);
  });
  const ppanel = S1.card('<div class="tiny" style="letter-spacing:0.14em">THREE LOAD PATHS · FIGURE J.1</div>', { x: 1250, y: 150, w: 630, h: 480, cls: 'glass' });
  ppanel.in(c('4.2', 'p1') - 0.5, 0.5, 'none');
  // three load paths as glowing projected polylines with travelling dots
  const paths = [
    { k: 'p1', col: COL.blue, name: 'Path 1 · WH → surface casing → cement → soil', pts: [[0.3, 4.1, 0.03], [0.3, 1.2, 0.03], [0.24, 1.0, 0.03], [0.24, -5.0, 0.03], [0.3, -6.5, 0.03], [0.62, -7.5, 0.03]] },
    { k: 'p2', col: COL.amber, name: 'Path 2 · WH → A, B → conductor housing → conductor → soil', pts: [[0.36, 4.1, 0.03], [0.41, 3.05, 0.03], [0.44, 2.6, 0.03], [0.44, 1.22, 0.03], [0.44, -1.0, 0.03], [0.62, -2.6, 0.03]] },
    { k: 'p3', col: COL.green, name: 'Path 3 · WH → conductor housing → C, D → template → seabed', pts: [[0.38, 4.1, 0.03], [0.41, 3.05, 0.03], [0.58, 2.42, 0.03], [1.6, 2.42, 0.03], [2.6, 2.42, 0.03], [2.85, 1.4, 0.03], [2.9, 0.1, 0.03]] },
  ];
  paths.forEach((p, i) => {
    const t0 = c('4.2', p.k);
    const glow = S1.path('', { stroke: p.col, width: 12, opacity: 0.25 });
    const line = S1.path('', { stroke: p.col, width: 4 });
    line.el.setAttribute('stroke-dasharray', '14 10');
    glow.in(t0, 0.5, 'none'); line.in(t0, 0.5, 'none');
    const dots = [0, 1, 2].map(() => { const d = S1.circle(0, 0, 7, { fill: p.col }); d.in(t0, 0.5, 'none'); return d; });
    const [pn, ...pr] = p.name.split(' · ');
    const lab = S1.div(`<div style="color:${p.col};font-weight:750;font-size:28px">${pn}</div><div class="small" style="color:var(--ink);margin-top:4px">${pr.join(' · ')}</div>`, { x: 1282, y: 236 + i * 128, w: 570 });
    lab.in(t0, 0.5, 'left');
    E.anim(t0 - 0.1, B2.end + 0.1, (t) => {
      const q = p.pts.map((v) => W3.project(v, t));
      const d = q.map((v, j) => `${j ? 'L' : 'M'}${v.x.toFixed(1)},${v.y.toFixed(1)}`).join(' ');
      glow.el.setAttribute('d', d); line.el.setAttribute('d', d);
      line.el.style.strokeDashoffset = String(-(t - t0) * 60);
      // dots travel along the polyline
      const seg = []; let Ltot = 0;
      for (let j = 1; j < q.length; j++) { const l = Math.hypot(q[j].x - q[j - 1].x, q[j].y - q[j - 1].y); seg.push(l); Ltot += l; }
      dots.forEach((dd, m) => {
        let s = ((t - t0) * 0.32 + m / 3) % 1 * Ltot;
        let j = 0; while (j < seg.length - 1 && s > seg[j]) { s -= seg[j]; j++; }
        const u = seg[j] ? s / seg[j] : 0;
        dd.el.setAttribute('cx', (q[j].x + (q[j + 1].x - q[j].x) * u).toFixed(1));
        dd.el.setAttribute('cy', (q[j].y + (q[j + 1].y - q[j].y) * u).toFixed(1));
      });
    });
  });
  const qt = S1.card('<div class="ref">J.2.1</div><div class="quote" style="font-size:26px">“The load sharing is dependent upon <span class="q">tolerances</span> and <span class="q">relative stiffness</span> of the different elements including soil properties.”</div>', { x: 1250, y: 660, w: 630 });
  qt.in(c('4.2', 'quote'), 0.6);

  // ------------------------------------------------------------------ 4.3 springs in parallel
  {
    const B = b('4.3');
    const S = new Scene(B.start, B.end);
    const yb0 = 330, yg = 760;
    const dl = (t) => 46 * smooth(t, c('4.3', 'same') - 0.6, c('4.3', 'same') + 0.8);
    const g = ground(S, 180, 860, yg); g.in(B.start + 0.2, 0.5, 'none');
    const s1 = S.path('', { stroke: COL.cyan, width: 4 }), s2 = S.path('', { stroke: COL.violet, width: 4 });
    s1.in(B.start + 0.3, 0.5, 'none'); s2.in(B.start + 0.3, 0.5, 'none');
    const bar = S.rect(220, 0, 600, 34, { fill: '#5d6b78', stroke: COL.ink2, width: 2, rx: 6 }); bar.in(B.start + 0.3, 0.5, 'none');
    const F = S.arrow(520, 120, 520, 300, { color: COL.amber, width: 6, head: 22 }); F.in(B.start + 0.6, 0.5, 'none');
    const Fl = S.eq('F', { x: 560, y: 160, size: 44, align: 'left' }); Fl.in(B.start + 0.6, 0.5, 'none');
    const k1 = S.eq('k_1', { x: 300, y: 560, size: 40, align: 'right' }), k2 = S.eq('k_2', { x: 760, y: 560, size: 40, align: 'left' });
    k1.in(B.start + 0.4, 0.5, 'none'); k2.in(B.start + 0.4, 0.5, 'none');
    const dlt = S.eq('\\delta', { x: 870, y: 360, size: 40, align: 'left', color: COL.amber }); dlt.in(c('4.3', 'same'), 0.5, 'none');
    E.anim(B.start, B.end, (t) => {
      const d = dl(t), yb = yb0 + d;
      bar.el.setAttribute('y', yb); F.baseTf = `translate(0 ${d})`; Fl.el.style.marginTop = d + 'px';
      s1.el.setAttribute('d', springPath(340, yb + 34, yg, { coils: 6, w: 30 }));
      s2.el.setAttribute('d', springPath(700, yb + 34, yg, { coils: 9, w: 22 }));
    });
    derivation(S, [
      { tex: '\\delta_1 = \\delta_2 = \\delta', t: c('4.3', 'same'), note: 'compatibility', x: 1050, align: 'left' },
      { tex: 'F_1 = k_1\\,\\delta,\\qquad F_2 = k_2\\,\\delta', t: c('4.3', 'each'), note: 'material law', x: 1050, align: 'left' },
      { tex: 'F_1 + F_2 = F', t: c('4.3', 'sum'), note: 'equilibrium', x: 1050, align: 'left' },
      { tex: '\\delta = \\dfrac{F}{k_1+k_2}\\;\\;\\Rightarrow\\;\\; F_i = \\dfrac{k_i}{\\sum k}\\,F', t: c('4.3', 'solve'), note: 'solve', x: 1050, align: 'left', size: 54 },
    ], { y0: 300, gap: 150, size: 48, noteAbove: true }).forEach((e, i) => { if (i === 3) e.boxed(c('4.3', 'attract')); });
    const sl = S.div('stiffness attracts load', { x: 1050, y: 890, cls: 'h3', style: 'color:#ffb547' });
    sl.in(c('4.3', 'attract'), 0.6, 'write');
  }

  // ------------------------------------------------------------------ 4.4 vertical load share
  {
    const B = b('4.4');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · Table 4 · 13.3.6.4 · 13.3.7.2', B.start + 0.3, B.end);
    const t4 = table(S, ['Concept', 'Load share factor'], D.norsok.table4.map((r) => [r[0], r[1]]), { x: 120, y: 240, w: 720, t: c('4.4', 't4'), title: 'Table 4 · indicative structure vertical load share', colCls: ['l', ''] });
    S.div('a: based on wells with 30 in conductors; may conservatively be used for 36 in · b: corner slot / centre slot', { x: 140, y: 640, w: 700, cls: 'tiny' }).in(c('4.4', 't4') + 1, 0.5);
    const card = S.card(`<div class="ref">13.3.6.4 a) · 13.3.7.2</div><div style="font-weight:750;font-size:32px;margin-bottom:12px">Fully supporting conductor methodology</div><div class="small" style="line-height:1.6">• conductor designed for <b class="c-amber">all</b> vertical hang-off loads<br>• template designed for its <b class="c-amber">stiffness-based share</b> (Table 4, confirm with a spring model)</div>`, { x: 980, y: 260, w: 820 });
    card.in(c('4.4', 'fully'), 0.6);
    const lesson = S.div('Each element is designed for the share that is worst for it.', { x: 980, y: 640, w: 820, cls: 'h3', style: 'color:#ffb547;line-height:1.3' });
    lesson.in(c('4.4', 'both'), 0.7, 'write');
  }

  // ------------------------------------------------------------------ 4.5 bending share between bonded strings
  {
    const B = b('4.5');
    const S = new Scene(B.start, B.end);
    clause('Below the top of cement E: same curvature', B.start + 0.3, B.end);
    const cx = 430, cy = 470, sc = 0.38;   // px per mm
    const o = tubeSection(S, cx, cy, 457.2 * sc, 50.8 * sc, { fill: '#8fa3b5' });
    const cem = S.path(`M${cx - 406.4 * sc},${cy} a${406.4 * sc},${406.4 * sc} 0 1,0 ${2 * 406.4 * sc},0 a${406.4 * sc},${406.4 * sc} 0 1,0 ${-2 * 406.4 * sc},0 Z M${cx - 254 * sc},${cy} a${254 * sc},${254 * sc} 0 1,1 ${2 * 254 * sc},0 a${254 * sc},${254 * sc} 0 1,1 ${-2 * 254 * sc},0 Z`, { fill: 'url(#cementpat)', stroke: 'none' });
    cem.el.setAttribute('fill-rule', 'evenodd');
    const i = tubeSection(S, cx, cy, 254 * sc, 25.4 * sc, { fill: '#6f8396' });
    o.in(B.start + 0.3, 0.6, 'none'); cem.in(B.start + 0.5, 0.6, 'none'); i.in(B.start + 0.6, 0.6, 'none');
    S.div('36 in × 2 in conductor', { x: cx, y: cy - 200, cls: 'small', anchor: 'cb' }).in(B.start + 0.6, 0.5);
    for (const [r, ang, txt, dy] of [[125, -0.785, 'cement', -150], [92, 0.785, '20 in × 1 in surface casing', 150]]) {
      const px = cx + r * Math.cos(ang), py = cy + r * Math.sin(ang);
      S.path(`M${px},${py} L${cx + 205},${cy + dy}`, { stroke: COL.ink2, width: 1.5, opacity: 0.7 }).in(B.start + 0.8, 0.5, 'none');
      S.circle(px, py, 4, { fill: COL.ink }).in(B.start + 0.8, 0.5, 'none');
      S.div(txt, { x: cx + 213, y: cy + dy, cls: 'small', anchor: 'lm' }).in(B.start + 0.9, 0.5, 'left');
    }
    derivation(S, [
      { tex: '\\kappa_c = \\kappa_s = \\kappa', t: c('4.5', 'kappa'), x: 930, align: 'left' },
      { tex: '\\cm{M_i} = E_i I_i\\,\\kappa,\\qquad \\textstyle\\sum \\cm{M_i} = \\cm M', t: c('4.5', 'kappa') + 2.0, x: 930, align: 'left' },
      { tex: '\\cm{M_i} = \\dfrac{E_i I_i}{\\sum E I}\\,\\cm M', t: c('4.5', 'emi'), x: 930, align: 'left', size: 56 },
    ], { y0: 250, gap: 140, size: 46 })[2].boxed(c('4.5', 'emi') + 1.5);
    const sh = D.share_EI;
    const bw = 820;
    const b1 = S.div(`conductor ${(100 * sh.conductor).toFixed(0)} %`, { x: 930, y: 700, w: bw * sh.conductor, h: 56, style: 'background:linear-gradient(90deg,#ffb547,#ff8a3d);border-radius:10px 0 0 10px;color:#06121c;font-weight:800;font-size:26px;display:flex;align-items:center;padding-left:18px' });
    const b2 = S.div('', { x: 930 + bw * sh.conductor, y: 700, w: bw * sh.casing, h: 56, style: 'background:#5aa9ff;border-radius:0 10px 10px 0' });
    S.div(`casing ${(100 * sh.casing).toFixed(0)} %`, { x: 930 + bw + 16, y: 728, cls: 'small', anchor: 'lm', style: 'color:#5aa9ff' }).in(c('4.5', 'num') + 0.6, 0.5);
    b1.el.style.transformOrigin = '0 50%'; b2.el.style.transformOrigin = '0 50%';
    b1.set(0, { sx: 0 }).to(c('4.5', 'num'), 0.9, { sx: 1 }, ease.out3).in(c('4.5', 'num'), 0.1, 'none');
    b2.in(c('4.5', 'num') + 0.8, 0.4, 'none');
    S.div('I = 0.01289 m⁴ vs 0.00112 m⁴', { x: 930, y: 790, cls: 'tiny' }).in(c('4.5', 'num') + 0.6, 0.5);
    const warn = S.card('<div class="ref">J.2.1 · cement shortfall</div><div class="small">Above the top of cement the strings are <b class="c-amber">not bonded</b>: the surface casing carries its share alone, through the contacts. “One of the main factors influencing the fatigue life assessments.”</div>', { x: 930, y: 850, w: 860 });
    warn.in(c('4.5', 'short'), 0.6);
  }

  // ------------------------------------------------------------------ 4.6 template as a rotational spring (+ gap)
  {
    const B = b('4.6');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · Figure J.1 contacts C and D', B.start + 0.3, B.end);
    // housing tilting in the rings; h = 2 m drawn as 360 px
    const cx = 450, yc = 520, hh = 360;
    const th = (t) => 0.10 * smooth(t, c('4.6', 'defl') - 0.4, c('4.6', 'defl') + 1.0);
    const ringC = S.g(), ringD = S.g();
    for (const [gg, y] of [[ringC, yc - hh / 2], [ringD, yc + hh / 2]]) {
      S.rect(cx - 180, y - 14, 92, 28, { fill: '#e7ae1c', stroke: 'none', rx: 4, parent: gg.el, o: 1 });
      S.rect(cx + 88, y - 14, 92, 28, { fill: '#e7ae1c', stroke: 'none', rx: 4, parent: gg.el, o: 1 });
      gg.in(B.start + 0.3, 0.5, 'none');
    }
    const hous = S.g(); hous.in(B.start + 0.3, 0.5, 'none');
    S.rect(-80, -300, 160, 600, { fill: '#8d9cab', stroke: COL.ink2, width: 2, rx: 6, parent: hous.el, o: 1 });
    S.line(0, -330, 0, 330, { stroke: COL.dim, width: 2, dash: '8 6', parent: hous.el, o: 1 });
    const kC = S.eq('k_C', { x: cx - 210, y: yc - hh / 2, size: 40, align: 'right' }), kD = S.eq('k_D', { x: cx - 210, y: yc + hh / 2, size: 40, align: 'right' });
    kC.in(c('4.6', 'rings'), 0.5, 'none'); kD.in(c('4.6', 'rings'), 0.5, 'none');
    const hd = S.path(`M${cx + 240},${yc - hh / 2} L${cx + 240},${yc + hh / 2}`, { stroke: COL.ink2, width: 2 }); hd.in(c('4.6', 'rings'), 0.5, 'none');
    S.eq('h', { x: cx + 262, y: yc, size: 40, align: 'left' }).in(c('4.6', 'rings'), 0.5, 'none');
    const fC = S.arrow(cx + 220, yc - hh / 2, cx + 110, yc - hh / 2, { color: COL.amber, width: 5 }), fD = S.arrow(cx - 220, yc + hh / 2, cx - 110, yc + hh / 2, { color: COL.amber, width: 5 });
    fC.in(c('4.6', 'couple'), 0.4, 'none'); fD.in(c('4.6', 'couple'), 0.4, 'none');
    E.anim(B.start, B.end, (t) => { hous.baseTf = `translate(${cx} ${yc}) rotate(${(th(t) * 180 / Math.PI).toFixed(3)})`; });
    const tg = S.eq('\\theta', { x: cx + 40, y: yc - 330, size: 40, align: 'left', color: COL.amber }); tg.in(c('4.6', 'defl'), 0.5, 'none');
    const st = derivation(S, [
      { tex: 'u_C = +\\theta\\tfrac{h}{2},\\quad u_D = -\\theta\\tfrac{h}{2}', t: c('4.6', 'defl'), x: 960, align: 'left' },
      { tex: '\\cm{M_T} = \\left(k\\,\\theta\\tfrac{h}{2}\\right) h \\;\\Rightarrow\\; \\cy{k_{\\theta,T}} = \\tfrac{1}{2}k\\,h^2', t: c('4.6', 'couple'), x: 960, align: 'left' },
      { tex: '\\cy{k_{\\theta,T}} = \\dfrac{k_C\\,k_D}{k_C+k_D}\\,h^2 = \\dfrac{200\\cdot 400}{600}\\,2^2 \\approx 533\\ \\tfrac{\\text{MNm}}{\\text{rad}}', t: c('4.6', 'gen'), x: 960, align: 'left', size: 42 },
      { tex: '\\dfrac{\\cm{M_T}}{\\cm M} = \\dfrac{\\cy{k_{\\theta,T}}}{\\cy{k_{\\theta,T}}+\\cy{k_{\\theta,W}}}', t: c('4.6', 'parallel'), x: 960, align: 'left' },
    ], { y0: 230, gap: 140, size: 46 });
    st[2].note = null;
    // gap spring characteristic
    const tGap = c('4.6', 'gap');
    const gp = S.chart({ x: 1000, y: 770, w: 440, h: 220, xmin: -3, xmax: 3, ymin: -2.4, ymax: 2.4, xticks: [], yticks: [], grid: false });
    gp.ax.el.style.display = 'none';          // axes through the origin instead
    gp.show(tGap);
    const band = S.rect(gp.X(-1), gp.y, gp.X(1) - gp.X(-1), gp.h, { fill: 'rgba(255,111,97,0.10)', stroke: 'none' }); band.in(tGap + 0.2, 0.5, 'none');
    S.arrow(gp.X(-3), gp.Y(0), gp.X(3) + 18, gp.Y(0), { color: 'rgba(200,225,245,0.6)', width: 2, head: 12 }).in(tGap, 0.5, 'none');
    S.arrow(gp.X(0), gp.Y(-2.4), gp.X(0), gp.Y(2.4) - 14, { color: 'rgba(200,225,245,0.6)', width: 2, head: 12 }).in(tGap, 0.5, 'none');
    S.eq('u', { x: gp.X(3) + 40, y: gp.Y(0), size: 32 }).in(tGap + 0.2, 0.4, 'none');
    S.eq('F', { x: gp.X(0) + 30, y: gp.Y(2.4) - 4, size: 32 }).in(tGap + 0.2, 0.4, 'none');
    S.div('gap', { x: gp.X(0), y: gp.Y(-2.4) + 8, cls: 'tiny', anchor: 'ct', style: 'color:#ff6f61' }).in(tGap + 0.3, 0.4);
    const gl = gp.curve([[-3, -2], [-1, 0], [1, 0], [3, 2]], { color: COL.coral, width: 5, t: tGap + 0.3 });
    S.div('ring force vs deflection: zero until the radial gap closes', { x: 1545, y: 880, w: 320, cls: 'small', anchor: 'lm' }).in(tGap + 0.6, 0.5);
    for (const e of st) e.out(c('4.6', 'gap') - 0.2, 0.4);
    const nl = S.div('→ the share depends on the size of the cycle: <b class="c-coral">nonlinear</b>', { x: 960, y: 640, cls: 'body', w: 880 });
    nl.in(c('4.6', 'gap') + 1.6, 0.6);
    const recap = S.eq('\\cm{M_T} = 0 \\;\\;\\text{while}\\;\\; |u| < \\text{gap}', { x: 960, y: 450, size: 50, align: 'left' });
    recap.in(c('4.6', 'gap') + 0.2, 0.7, 'write');
  }

  // ------------------------------------------------------------------ 4.7 relative vertical displacement
  {
    const B = b('4.7');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · 13.3.6.2 · Annex E', B.start + 0.3, B.end);
    const cx = 420, yc = 560;
    const up = (t) => 70 * smooth(t, c('4.7', 'grow') - 0.3, c('4.7', 'grow') + 2.0);
    for (const y of [yc - 180, yc + 180]) {
      S.rect(cx - 180, y - 14, 92, 28, { fill: '#e7ae1c', stroke: 'none', rx: 4, o: 0 }).in(B.start + 0.3, 0.5, 'none');
      S.rect(cx + 88, y - 14, 92, 28, { fill: '#e7ae1c', stroke: 'none', rx: 4, o: 0 }).in(B.start + 0.3, 0.5, 'none');
    }
    const h = S.g(); h.in(B.start + 0.3, 0.5, 'none');
    S.rect(-80, -320, 160, 640, { fill: '#8d9cab', stroke: COL.ink2, width: 2, rx: 6, parent: h.el, o: 1 });
    const arr = S.arrow(cx + 240, yc + 60, cx + 240, yc - 60, { color: COL.coral, width: 6, head: 20 }); arr.in(c('4.7', 'grow'), 0.5, 'none');
    S.div('thermal growth + settlement', { x: cx + 270, y: yc, cls: 'small', anchor: 'lm', style: 'color:#ff6f61' }).in(c('4.7', 'grow') + 0.3, 0.5);
    E.anim(B.start, B.end, (t) => { h.baseTf = `translate(${cx} ${yc - up(t)})`; });
    const th = D.thermal;
    derivation(S, [
      { tex: '\\delta = \\alpha\\,\\Delta T\\,L', t: c('4.7', 'grow') + 1.2, x: 980, align: 'left', size: 56 },
      { tex: '= 12\\!\\times\\!10^{-6}\\cdot 60 \\cdot 120\\ \\text{m} \\approx ' + th.growth_mm.toFixed(0) + '\\ \\text{mm}', t: c('4.7', 'num'), x: 980, align: 'left' },
      { tex: 'F = E A\\,\\alpha\\,\\Delta T \\approx ' + th.restrained_force_MN.toFixed(1) + '\\ \\text{MN}', t: c('4.7', 'restrain'), x: 980, align: 'left' },
    ], { y0: 250, gap: 130, size: 48 });
    S.div('if the 20 in casing were fully restrained', { x: 980, y: 580, cls: 'tiny' }).in(c('4.7', 'restrain') + 0.5, 0.5);
    quoteCard(S, '13.3.6.2', 'A relative vertical displacement of <span class="q">100 mm</span> between the template and the conductor or wellhead, including thermal upward growth and template settlement, shall be accounted for in the template design unless otherwise specified.', { x: 980, y: 650, w: 820, t: c('4.7', 'req'), size: 26 });
  }
}
