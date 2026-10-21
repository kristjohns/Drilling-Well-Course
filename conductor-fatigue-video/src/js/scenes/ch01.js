// Chapter 1 — the system and the rules: exploded cutaway of the wellhead system, definitions, the map of the standard, the recipe.
import { E, ease, COL, clamp, smooth, ramp, lerp } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause, step, STEPS } from '../engine/hud.js';
import { camPath, camSpline, DEF, THREE } from '../three/world.js';
import { updateSnow, revolve } from '../three/models.js';
import { quoteCard, label3D } from './kit.js';

export async function build(E, T, D) {
  const ch = T.ch(1);
  titleCard(ch, 'The hardware, the loads it sees, and where NORSOK U-001 puts the rules');
  const W3 = E.world, md = W3.models, M = W3.M;
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const B1 = b('1.1'), B2 = b('1.2');

  // ------------------------------------------------------------------ 1.1 + 1.2 exploded cutaway (one 3D shot)
  const tE0 = c('1.1', 'wh') + 0.2, tE1 = c('1.1', 'cond') + 1.6;      // explode while naming parts, re-assemble later
  const tR0 = c('1.1', 'slot') - 0.2, tR1 = tR0 + 2.0;
  const ex = (t) => ramp(t, tE0, tE0 + 2.2, ease.inOut3) * (1 - ramp(t, tR0, tR1, ease.inOut3));
  const cam = camSpline([
    { t: B1.start, p: [7.5, 6.2, 11.0], l: [0, 3.6, 0], fov: 34 },
    { t: c('1.1', 'wh'), p: [7.2, 5.8, 11.4], l: [0, 3.6, 0], fov: 35 },
    { t: tE0 + 2.4, p: [8.6, 5.4, 13.8], l: [0, 4.2, 0], fov: 38 },          // whole exploded stack in view
    { t: c('1.1', 'datum') + 1.0, p: [7.8, 4.8, 12.4], l: [0, 3.6, 0], fov: 38 },
    { t: c('1.1', 'whx'), p: [5.6, 4.6, 9.4], l: [0, 2.8, 0], fov: 36 },
    { t: c('1.1', 'cond'), p: [4.2, 3.0, 9.6], l: [0, 1.6, 0], fov: 38 },
    { t: c('1.1', 'slot'), p: [7.6, 4.6, 10.6], l: [-0.6, 1.4, 0], fov: 38 },
    { t: c('1.1', 'cement') + 0.4, p: [2.5, -1.9, 4.4], l: [0.2, -3.4, 0], fov: 36 },      // close on the cement annuli
    { t: c('1.2', 'def'), p: [5.6, 1.0, 11.2], l: [0.4, 0.7, 0], fov: 38 },
    { t: B2.end, p: [5.2, 1.6, 10.8], l: [0, 1.2, 0], fov: 38 },
  ]);
  const P = md.wellCut.userData.parts;
  const offs = { hp: 2.2, whx: 2.2, sc: 2.2, whxWeld: 2.2, lp: 0.9 };
  const conn = md.connCut;      // stand-alone wellhead connector (cut), sits on the datum
  W3.shot(B1.start, B2.end, {
    show: ['wellCut', 'templateCut', 'seabedCut', 'snow', 'connCut'],
    fadeIn: 0.8, fadeOut: 0.8, cam, fog: 0.012, bg: '#082b42',
    update: (t) => {
      W3.update(t); updateSnow(md.snow, t);
      const e = ex(t);
      for (const k in P) P[k].position.y = (offs[k] || 0) * e;
      conn.position.y = 3.6 * e;
      md.templateCut.visible = t > c('1.1', 'slot') - 0.6;
      md.seabedCut.visible = t > c('1.1', 'slot') - 0.6;
      DEF.uAmp.value = 0; DEF.uGlow.value = 0;
      // highlight the conductor during the definitions
      const h = smooth(t, c('1.2', 'def') - 0.3, c('1.2', 'def') + 0.8);
      M.cond.emissive.setRGB(0.55 * h, 0.32 * h, 0.05 * h);
      DEF.uStressMix.value = 0;
    },
  });
  const S = new Scene(B1.start, B1.end);
  const L = (t0, pos, html, o = {}) => label3D(S, pos, html, { t0, t1: o.t1 || (tR0 + 0.2), anchor: o.anchor || 'lm', dx: o.dx ?? 90, dy: o.dy ?? 0, cls: o.cls || '' });
  L(c('1.1', 'conn'), (t) => [0.85, 4.4 + 3.6 * ex(t), 0], 'Wellhead connector <span class="sub">on the BOP</span>', { dx: 120 });
  L(c('1.1', 'wh'), (t) => [0.41, 3.5 + 2.2 * ex(t), 0], 'High-pressure wellhead housing <span class="sub">18¾ in bore</span>', { dx: 140, dy: -20 });
  L(c('1.1', 'whx'), (t) => [0.26, 0.4 + 2.2 * ex(t), 0], 'Wellhead extension', { anchor: 'rm', dx: -130 });
  L(c('1.1', 'sc'), (t) => [0.26, -1.8 + 2.2 * ex(t), 0], 'Surface casing <span class="sub">20 in</span>', { anchor: 'rm', dx: -130 });
  L(c('1.1', 'ch'), (t) => [0.49, 2.0 + 0.9 * ex(t), 0], 'Conductor housing <span class="sub">low pressure</span>', { dx: 150 });
  L(c('1.1', 'cx'), [0.46, 0.4, 0], 'Conductor extension', { dx: 150 });
  L(c('1.1', 'cond'), [0.46, -1.6, 0], 'Conductor <span class="sub">36 in × 2 in</span>', { dx: 150 });
  // datum plane label
  const dl = S.div('WELLHEAD DATUM', { x: 0, y: 0, cls: 'tiny', style: 'color:#ffb547;letter-spacing:0.16em' });
  dl.in(c('1.1', 'datum'), 0.5, 'none'); dl.out(c('1.1', 'whx') + 1.5, 0.4);
  E.anim(c('1.1', 'datum') - 0.1, c('1.1', 'whx') + 2, (t) => {
    const p = W3.project([-1.6, 4.0 + 2.2 * ex(t), 0], t);
    dl.el.style.left = (p.x - 200).toFixed(1) + 'px'; dl.el.style.top = (p.y - 12).toFixed(1) + 'px';
  });
  const dline = S.path('M0,0', { stroke: COL.amber, width: 2, dash: '10 8' });
  dline.in(c('1.1', 'datum'), 0.5, 'none'); dline.out(c('1.1', 'whx') + 1.5, 0.4);
  E.anim(c('1.1', 'datum') - 0.1, c('1.1', 'whx') + 2, (t) => {
    const a = W3.project([-1.4, 4.0 + 2.2 * ex(t), 0], t), q = W3.project([1.4, 4.0 + 2.2 * ex(t), 0], t);
    dline.el.setAttribute('d', `M${a.x.toFixed(1)},${a.y.toFixed(1)} L${q.x.toFixed(1)},${q.y.toFixed(1)}`);
  });
  L(c('1.1', 'slot'), [-0.75, 2.45, 0], 'Template well slot', { anchor: 'rm', dx: -110, dy: -50, t1: B1.end });
  L(c('1.1', 'cement') + 0.5, [0.51, -2.9, 0], 'Cement · conductor to soil', { dx: 150, dy: -40, t1: B1.end });
  L(c('1.1', 'cement') + 1.1, [0.33, -3.7, 0], 'Cement inside the conductor', { anchor: 'rm', dx: -150, dy: 40, t1: B1.end });

  // 1.2 definitions over the 3D
  {
    const S2 = new Scene(B2.start, B2.end);
    clause('NORSOK U-001:2026 · 3.1.7 conductor', B2.start + 0.3, B2.end);
    const shade = S2.div('', { x: 0, y: 0, w: 1920, h: 1080, style: 'background:linear-gradient(90deg, rgba(4,12,20,0.9) 0%, rgba(4,12,20,0.6) 50%, rgba(4,12,20,0) 75%)' });
    shade.in(B2.start, 0.8, 'none');
    quoteCard(S2, '3.1.7 · conductor', 'tubulars installed and cemented in a well construction, providing support for, and <span class="q">load sharing</span> with the surface casing', { x: 120, y: 250, w: 800, t: c('1.2', 'def'), size: 36 });
    const n1 = S2.div('Note 1: the conductor design may also include a weld on the upper part: a low-pressure pipe extension and a conductor housing.', { x: 150, y: 560, w: 740, cls: 'small' });
    n1.in(c('1.2', 'def') + 1.4, 0.6);
    const sh = S2.div('Who carries what?', { x: 150, y: 720, cls: 'h2', style: 'color:#ffb547' });
    sh.in(c('1.2', 'share') + 0.6, 0.7, 'write');
  }

  // ------------------------------------------------------------------ 1.3 where the rules are
  {
    const B = b('1.3');
    const S3 = new Scene(B.start, B.end);
    S3.div('NORSOK U-001:2026 · Subsea production systems', { x: 960, y: 150, cls: 'kicker', anchor: 'ct' }).in(B.start + 0.2, 0.5);
    const card = (x, y, w, ref, title, body, t, col = COL.cyan) => {
      const a = S3.card(`<div class="ref" style="color:${col}">${ref}</div><div style="font-weight:750;font-size:30px;margin-bottom:8px">${title}</div><div class="small">${body}</div>`, { x, y, w });
      a.in(t, 0.6, 'rise');
      a.T('s').init = 1;
      return a;
    };
    // clause 8.1 is read out at length: its card starts large in the centre and settles into the grid before 13.3.6
    const c81 = S3.card(`<div class="ref" style="color:${COL.cyan}">Clause 8.1</div><div style="font-weight:750;font-size:30px;margin-bottom:8px">Riser forces</div><div class="small">Annex A riser loads act on the WH housing, WH extension, conductor housing and conductor extension. <span style="color:var(--amber)">Load share WH system ↔ template shall be determined.</span></div>`, { x: 120, y: 220, w: 540 });
    later(() => {
      const w = c81.el.offsetWidth, h = c81.el.offsetHeight, t81 = c('1.3', 'c81');
      const dx = 960 - (120 + w / 2), dy = 560 - (220 + h / 2);
      c81.T('o').init = 0; c81.T('o').add(t81, 0.6, 1, ease.out3);
      c81.T('x').init = dx; c81.T('y').init = dy + 24; c81.T('y').add(t81, 0.6, dy, ease.out3);
      c81.T('s').init = 1.6;
      c81.to(c('1.3', 'c1336') - 1.1, 1.0, { x: 0, y: 0, s: 1 }, ease.inOut3);
    });
    card(690, 220, 540, 'Clause 13.3.6', 'Structural design', 'Template, conductor and well system; load share; conductor girth welds class C1; 100 mm relative displacement.', c('1.3', 'c1336'));
    card(1260, 220, 540, 'Annex A · A.3.5', 'Fatigue loads', 'Annual single-load moment range ΔM<sub>o</sub> and the bending moment histogram at the WH datum.', c('1.3', 'annA'), COL.amber);
    card(120, 520, 540, 'Annex B · B.2.6, B.4', 'Design format and capacity', 'Service life ≤ fatigue life / D<sub>F</sub>; M-N curves from the S-N method; Miner damage.', c('1.3', 'annB'), COL.amber);
    card(690, 520, 540, 'Annex J', 'Load paths', 'Contact areas A–H, three load paths, critical factors, monitoring.', c('1.3', 'annJ'), COL.amber);
    const ext1 = card(1260, 520, 540, 'DNV-RP-C203:2024', 'S-N curves', 'Fatigue strength of welds and base material, environment, thickness, connectors (section 5.7).', c('1.3', 'dnv'), COL.violet);
    const ext2 = card(1260, 790, 540, 'NORSOK N-001', 'Template design fatigue factors', 'DFF by access for inspection and consequence of failure.', c('1.3', 'n001'), COL.violet);
    S3.div('referenced documents', { x: 1260, y: 486, cls: 'tiny', style: 'color:#b794f6' }).in(c('1.3', 'dnv'), 0.5);
  }

  // ------------------------------------------------------------------ 1.4 the recipe
  {
    const B = b('1.4');
    const S4 = new Scene(B.start, B.end);
    S4.div('The method in eight steps', { x: 960, y: 150, cls: 'h2', anchor: 'ct' }).in(B.start + 0.2, 0.6, 'write');
    const sub = ['Annex A', 'Annex J · 13.3.6', 'B.4.2', 'B.4.3 · DNV-RP-C203', 'B.4.4', 'Palmgren–Miner', 'B.2.6 · N-001', 'A.3.5.1 · Annex J'];
    const cues = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8'];
    STEPS.forEach((s, i) => {
      const col = i < 4 ? 0 : 1, row = i % 4;
      const x = 260 + col * 720, y = 270 + row * 165;
      const [n, ...rest] = s.split(' ');
      const a = S4.div(`<div style="display:flex;align-items:center;gap:24px"><div style="width:76px;height:76px;border-radius:20px;background:linear-gradient(140deg,#ffb547,#ff8a3d);color:#06121c;font-weight:800;font-size:40px;display:flex;align-items:center;justify-content:center">${n}</div><div><div style="font-weight:750;font-size:36px">${rest.join(' ')}</div><div class="tiny" style="color:#4fd1ff;margin-top:4px">${sub[i]}</div></div></div>`, { x, y });
      a.in(c('1.4', cues[i]), 0.5, 'left');
    });
    step(c('1.4', 's8') + 2.0, -1);
  }
}
