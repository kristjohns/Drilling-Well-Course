// Chapter 1 — who owns the interface: the contacts of Figure J.1 and load path 3, the two rule books (Annex B for the
// wellhead side, N-001 -> N-004 -> Eurocode 3 for the template side), the interface as a mechanism (end stops, SLS).
import { E, ease, COL, clamp, smooth, lerp } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause } from '../engine/hud.js';
import { camSpline, DEF } from '../three/world.js';
import { updateSnow } from '../three/models.js';
import { label3D, letter3D, quoteCard } from './kit.js';
import { note } from './fx.js';

export async function build(E, T, D) {
  const ch = T.ch(1);
  titleCard(ch, 'The contacts, the load share, and which rule book applies to each side');
  const W3 = E.world, md = W3.models, M = W3.M;
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);

  // ------------------------------------------------------------------ 1.1 the contacts and load path 3
  {
    const B = b('1.1');
    const cam = camSpline([
      { t: B.start, p: [-0.6, 3.4, 14.2], l: [-0.6, 1.3, 0], fov: 38 },
      { t: c('1.1', 'C') + 0.6, p: [1.7, 2.75, 5.6], l: [0.25, 1.85, 0], fov: 36 },
      { t: c('1.1', 'D') + 1.0, p: [1.6, 1.55, 5.2], l: [0.25, 1.05, 0], fov: 36 },
      { t: c('1.1', 'path') + 1.6, p: [0.4, 3.0, 9.6], l: [0.0, 1.9, 0], fov: 38 },
      { t: c('1.1', 'G') + 0.4, p: [-0.4, 3.5, 14.6], l: [-0.6, 1.4, 0], fov: 38 },
      { t: B.end, p: [-0.5, 3.6, 15.0], l: [-0.6, 1.4, 0], fov: 38 },
    ]);
    W3.shot(B.start, B.end, {
      show: ['wellCut', 'templateCut', 'seabedCut', 'connCut', 'snow'],
      fadeIn: 0.8, fadeOut: 0.8, cam, fog: 0.012, bg: '#082b42',
      update: (t) => { W3.update(t); updateSnow(md.snow, t); DEF.uAmp.value = 0; },
    });
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · Figure J.1 · 3.1.12 · Table 4', B.start + 0.3, B.end);
    S.div('FIGURE J.1 · CONTACTS AND LOAD PATHS', { x: 110, y: 130, cls: 'kicker' }).in(B.start + 0.4, 0.6, 'left');
    const P = { F: [0, 4.0, 0.05], A: [0.42, 3.05, 0.05], C: [0.68, 2.40, 0.05], D: [0.56, 0.40, 0.05], G: [-8.2, 0.05, 0.05] };
    letter3D(S, P.C, 'C', { t0: c('1.1', 'C'), t1: B.end });
    letter3D(S, P.D, 'D', { t0: c('1.1', 'D'), t1: B.end });
    letter3D(S, P.F, 'F', { t0: c('1.1', 'path'), t1: B.end, color: COL.cyan });
    letter3D(S, P.A, 'A', { t0: c('1.1', 'path') + 0.3, t1: B.end, color: COL.cyan });
    letter3D(S, P.G, 'G', { t0: c('1.1', 'G'), t1: B.end, color: COL.cyan });
    label3D(S, P.C, 'C · template structure / conductor housing', { t0: c('1.1', 'C') + 0.4, t1: c('1.1', 'path'), anchor: 'lm', dx: 70, dy: -40, color: COL.amber });
    label3D(S, P.D, 'D · bottom of structure / conductor housing', { t0: c('1.1', 'D') + 0.4, t1: c('1.1', 'path'), anchor: 'lm', dx: 70, dy: 40, color: COL.amber });
    // load path 3: F -> A -> C -> D -> G drawn on progressively
    const lp = S.path('M0,0', { stroke: '#ffb547', width: 7, opacity: 0.9 });
    lp.el.setAttribute('filter', 'url(#glow)');
    lp.in(c('1.1', 'path'), 0.4, 'none');
    const t0 = c('1.1', 'path') + 0.2, t1 = c('1.1', 'G') + 1.2;
    E.anim(t0 - 0.1, B.end, (t) => {
      const pts = ['F', 'A', 'C', 'D', 'G'].map((k) => W3.project(P[k], t));
      const seg = []; let L = 0;
      for (let i = 0; i < pts.length - 1; i++) { const l = Math.hypot(pts[i + 1].x - pts[i].x, pts[i + 1].y - pts[i].y); seg.push(l); L += l; }
      let rem = L * smooth(t, t0, t1);
      let d = `M${pts[0].x.toFixed(1)},${pts[0].y.toFixed(1)}`;
      for (let i = 0; i < seg.length && rem > 0; i++) {
        const u = Math.min(1, rem / seg[i]);
        d += ` L${lerp(pts[i].x, pts[i + 1].x, u).toFixed(1)},${lerp(pts[i].y, pts[i + 1].y, u).toFixed(1)}`;
        rem -= seg[i];
      }
      lp.el.setAttribute('d', d);
    });
    const lab = S.div('Load path 3 · WH → conductor → guide structure → seabed', { x: 110, y: 172, cls: 'small c-amber' });
    lab.in(c('1.1', 'path') + 0.6, 0.6, 'left');
    const q = quoteCard(S, 'NORSOK U-001:2026 · 3.1.12 load share', '<span class="q">distribution of applied loads</span> between the well (including conductor, casing and soil) and the template structure and its foundation',
      { x: 1170, y: 180, w: 660, t: c('1.1', 'share'), size: 27 });
    const t4 = S.card(`<div class="ref">TABLE 4 · INDICATIVE VERTICAL LOAD SHARE FACTORS</div>
      <table class="t"><tbody>${[['Single caisson 1-slot', '50 %'], ['Template 1-slot', '40 %'], ['Template 2-slot', '45 %'], ['Template 4-slot', '35 %'], ['Template 6-slot', '30 % / 20 %']].map(([a, v]) => `<tr><td class="l">${a}</td><td>${v}</td></tr>`).join('')}</tbody></table>
      <div class="small" style="font-size:21px;margin-top:10px">Figure J.1: load sharing depends on <span class="c-amber">tolerances</span> and the <span class="c-amber">relative stiffness</span> of well, template and soil</div>`,
    { x: 1170, y: 470, w: 660, cls: 'glass' });
    t4.in(c('1.1', 'stiff') - 0.4, 0.6, 'rise');
  }

  // ------------------------------------------------------------------ 1.2 two sides, two rule books
  {
    const B = b('1.2');
    const panel = { x: 690, y: 170, w: 540, h: 640 };
    const cam = camSpline([
      { t: B.start, p: [2.3, 2.4, 4.6], l: [0.15, 1.45, 0], fov: 38 },
      { t: B.end, p: [2.0, 2.2, 4.3], l: [0.15, 1.45, 0], fov: 38 },
    ]);
    const cyan = [0.12, 0.42, 0.62], yel = [0.45, 0.32, 0.02];
    const glow = (mat, col, h) => mat.emissive.setRGB(col[0] * h, col[1] * h, col[2] * h);
    W3.shot(B.start, B.end, {
      show: ['wellCut', 'templateCut', 'seabedCut', 'connCut'], panel, fadeIn: 0.7, fadeOut: 0.6, cam, fog: 0.01, bg: '#0b2236',
      update: (t) => {
        W3.update(t); DEF.uAmp.value = 0;
        const hw = smooth(t, c('1.2', 'wh') - 0.3, c('1.2', 'wh') + 0.6) * (1 - 0.6 * smooth(t, c('1.2', 'tm') - 0.3, c('1.2', 'tm') + 0.5));
        const ht = smooth(t, c('1.2', 'tm') - 0.3, c('1.2', 'tm') + 0.6);
        glow(M.lp, cyan, hw); glow(M.cond, cyan, hw); glow(M.steel, cyan, 0.5 * hw);
        glow(M.yellow, yel, ht); glow(M.yellowDark, yel, ht);
      },
      key: (t) => t.toFixed(2),
    });
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · 13.3.6.1 · Annex B · B.9 · normative references', B.start + 0.3, B.end);
    const L = S.card(`<div class="tiny" style="color:#4fd1ff;letter-spacing:0.16em">WELLHEAD SIDE</div>
      <div class="small" style="margin:4px 0 16px 0">conductor housing · conductor</div>
      <div style="font-weight:750;font-size:34px;line-height:1.2">NORSOK U-001<br>Annex B</div>
      <div class="small" style="margin-top:6px">clause B.9: pipe formulas for the conductor</div>
      <div style="height:1px;background:rgba(190,220,245,0.18);margin:18px 0"></div>
      <div class="small" style="font-size:23px;line-height:1.6">σ<sub>y</sub> at <span class="c-amber">0.2 %</span> plastic strain<br>load ≤ F<sub>d</sub> × capacity<br>capacities found as <span class="c-amber">loads</span></div>
      <div class="tiny" style="margin-top:14px">→ the first video</div>`,
    { x: 90, y: 200, w: 560, cls: 'glass', style: 'border-color:rgba(79,209,255,0.55)' });
    L.in(c('1.2', 'wh') - 0.3, 0.6, 'left');
    const R = S.card(`<div class="tiny" style="color:#f2c14e;letter-spacing:0.16em">TEMPLATE SIDE</div>
      <div class="small" style="margin:4px 0 0 0">slot rings · struts · girders</div>`,
    { x: 1270, y: 200, w: 560, cls: 'glass', style: 'border-color:rgba(242,193,78,0.55)' });
    R.in(c('1.2', 'tm') - 0.3, 0.6, 'right');
    const chain = [['clause', 'U-001 · 13.3.6.1', 'structural design shall follow'], ['clause', 'ISO 13628-15 · clause 5.4<br>+ NORSOK N-001', ''], ['n004', 'NORSOK N-004:2022', 'steel design'], ['ec3', 'Eurocode 3 · NS-EN 1993', '+ National Annex']];
    chain.forEach(([cue, a, sub], i) => {
      const y = 330 + i * 150;
      const box = S.card(`<div style="font-weight:720;font-size:27px;line-height:1.2">${a}</div>${sub ? `<div class="small" style="font-size:20px">${sub}</div>` : ''}`, { x: 1300, y, w: 500, cls: 'glass', style: 'padding:14px 20px' });
      box.in(c('1.2', cue) + (i === 1 ? 1.8 : 0), 0.5, 'rise');
      if (i) { const ar = S.arrow(1550, y - 36, 1550, y - 6, { color: COL.yellow, width: 4, head: 14 }); ar.in(c('1.2', cue) + (i === 1 ? 1.6 : -0.2), 0.4, 'none'); }
    });
    const tag = S.div('U-001 has <span class="c-amber">no failure criterion of its own</span> for the template steel', { x: 960, y: 930, cls: 'h3', anchor: 'cm', style: 'font-size:32px' });
    tag.in(c('1.2', 'none'), 0.6, 'rise');
    S.div('wellhead side', { x: panel.x + 24, y: panel.y + 20, cls: 'tiny', style: 'color:#4fd1ff' }).in(c('1.2', 'wh'), 0.5);
    S.div('template side', { x: panel.x + panel.w - 24, y: panel.y + 20, cls: 'tiny', anchor: 'rt', style: 'color:#f2c14e' }).in(c('1.2', 'tm'), 0.5);
  }

  // ------------------------------------------------------------------ 1.3 the interface as a mechanism
  {
    const B = b('1.3');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · 13.3.6.2 · Table A.2 note d · 13.3.6.4', B.start + 0.3, B.end);
    S.div('THE INTERFACE AS A MECHANISM · SCHEMATIC', { x: 110, y: 130, cls: 'kicker' }).in(B.start + 0.3, 0.6, 'left');
    // schematic section of the slot: template (yellow) with a lower end stop (landing) and an upper end stop, housing (grey)
    const g = S.g({ o: 0 }); g.in(B.start + 0.4, 0.6, 'none');
    const sc = 1.0, X0 = 520, Y0 = 560;
    const tmpl = S.g({ parent: g.el, o: 1 }), hous = S.g({ parent: g.el, o: 1 });
    const R = (gg, x, y, w, h, fill, stroke = 'none') => S.rect(x, y, w, h, { fill, stroke, width: 2, parent: gg.el, o: 1, rx: 3 });
    for (const s of [-1, 1]) {
      R(tmpl, X0 + s * 190 - (s < 0 ? 60 : 0), Y0 - 260, 60, 520, '#c9961c');                      // slot walls
      R(tmpl, X0 + s * 120 - (s < 0 ? 70 : 0), Y0 + 40, 70, 34, '#e7ae1c');                          // lower end stop (landing ring)
      R(tmpl, X0 + s * 120 - (s < 0 ? 70 : 0), Y0 - 140, 70, 30, '#e7ae1c');                         // upper end stop
    }
    R(hous, X0 - 80, Y0 - 300, 160, 640, '#8d9cab');                                                   // conductor housing
    for (const s of [-1, 1]) R(hous, X0 + s * 80 - (s < 0 ? 38 : 0), Y0 - 40, 38, 60, '#a9b8c6');    // shoulder
    const lbl = (txt, x, y, col = COL.dim, a = 'lm') => { const d = S.div(txt, { x, y, cls: 'small', anchor: a, style: `color:${col};font-size:22px` }); d.in(B.start + 0.8, 0.5); return d; };
    lbl('template slot', X0 + 260, Y0 - 230, COL.yellow);
    lbl('conductor housing', X0, Y0 + 370, COL.steel, 'ct');
    lbl('upper end stop', X0 - 270, Y0 - 125, COL.yellow, 'rm');
    lbl('lower end stop', X0 - 270, Y0 + 57, COL.yellow, 'rm');
    // motion: the well grows up, the template settles; the relative displacement closes the upper gap at 'preload'
    const tg = c('1.3', 'grow'), tpre = c('1.3', 'preload');
    const rel = (t) => 40 * smooth(t, tg, tg + 4.0) + 30 * smooth(t, tpre - 1.6, tpre);    // px of relative displacement
    let gap1 = null, gap2 = null;
    E.anim(B.start, B.end, (t) => {
      const r = rel(t);
      hous.baseTf = `translate(0 ${(-0.62 * r).toFixed(2)})`; tmpl.baseTf = `translate(0 ${(0.38 * r).toFixed(2)})`;
      // the highlighted gaps follow the parts: upper gap between shoulder top and upper stop, lower gap below the shoulder
      const shTop = Y0 - 40 - 0.62 * r, shBot = Y0 + 20 - 0.62 * r, stUp = Y0 - 110 + 0.38 * r, stLo = Y0 + 40 + 0.38 * r;
      if (gap1) { gap1.el.style.top = (stUp - 2).toFixed(1) + 'px'; gap1.el.style.height = Math.max(4, shTop - stUp + 4).toFixed(1) + 'px'; }
      if (gap2) { gap2.el.style.top = (shBot - 2).toFixed(1) + 'px'; gap2.el.style.height = Math.max(4, stLo - shBot + 4).toFixed(1) + 'px'; }
    });
    hous.T('x'); tmpl.T('x');
    const up = S.arrow(X0, Y0 - 330, X0, Y0 - 400, { color: COL.coral, width: 5 }); up.in(tg, 0.5, 'none');
    const upl = S.div('thermal growth of the well', { x: X0 + 18, y: Y0 - 390, cls: 'small c-coral', anchor: 'lm', style: 'font-size:22px' }); upl.in(tg + 0.2, 0.5);
    const dn = S.arrow(X0 - 250, Y0 + 300, X0 - 250, Y0 + 360, { color: COL.cyan, width: 5 }); dn.in(tg + 1.2, 0.5, 'none');
    const dnl = S.div('template settlement', { x: X0 - 270, y: Y0 + 330, cls: 'small c-cyan', anchor: 'rm', style: 'font-size:22px' }); dnl.in(tg + 1.4, 0.5);
    // gaps (highlighted at 'stops') and the contact at 'preload'
    gap1 = S.div('', { x: X0 + 84, y: Y0 - 112, w: 36, h: 74, cls: 'hl' }); gap1.in(c('1.3', 'stops'), 0.4, 'none'); gap1.out(tpre - 0.3, 0.3);
    gap2 = S.div('', { x: X0 + 84, y: Y0 + 20, w: 36, h: 22, cls: 'hl' }); gap2.in(c('1.3', 'stops') + 0.5, 0.4, 'none'); gap2.out(tpre - 0.3, 0.3);
    const gl1 = S.div('margin to the upper end stop', { x: X0 + 270, y: Y0 - 80, cls: 'tiny', anchor: 'lm', style: 'color:#ffb547' }); gl1.in(c('1.3', 'stops') + 0.2, 0.4); gl1.out(tpre - 0.3, 0.3);
    const gl2 = S.div('margin to the lower end stop', { x: X0 + 270, y: Y0 + 10, cls: 'tiny', anchor: 'lm', style: 'color:#ffb547' }); gl2.in(c('1.3', 'stops') + 0.7, 0.4); gl2.out(tpre - 0.3, 0.3);
    const yc = Y0 - 40 - 0.62 * 70;                                   // shoulder top = upper stop bottom when the gap has closed
    for (const xh of [X0 + 70, X0 - 210]) {
      const hit = S.div('', { x: xh, y: yc - 30, w: 140, h: 60, style: 'border-radius:14px;background:rgba(255,77,94,0.25);border:3px solid #ff4d5e' });
      hit.in(tpre, 0.3, 'pop');
    }
    const hitl = S.card('<div style="font-weight:750;font-size:26px;color:#ff4d5e">end stop reached</div><div class="small" style="font-size:21px">→ template preload forces<br>→ separate ULS load cases</div>', { x: 790, y: 430, w: 320, cls: 'glass' });
    hitl.in(tpre + 0.4, 0.5, 'rise');
    quoteCard(S, 'U-001 · 13.3.6.2', 'A relative vertical displacement of <span class="q">100 mm</span> between the template and the conductor or wellhead, including thermal upward growth and template settlement, shall be accounted for in the template design unless otherwise specified.',
      { x: 1140, y: 170, w: 700, t: c('1.3', 'mm'), size: 24 });
    quoteCard(S, 'U-001 · Table A.2, note d', 'The relative displacement between conductor and template is analysed (<span class="q">SLS check, load factor 1,0</span>), and the margins to upper and lower end stops are checked. If end stops are reached resulting in template preload forces, this should be accounted for in ULS separate load cases.',
      { x: 1140, y: 450, w: 700, t: c('1.3', 'sls'), size: 24 });
    quoteCard(S, 'U-001 · 13.3.6.4', 'The final inclination of the installed template shall not exceed <span class="q">0,3 degrees</span> unless it is documented that the … tolerance loop design allows for it.',
      { x: 1140, y: 800, w: 700, t: c('1.3', 'tilt'), size: 24 });
  }
}
