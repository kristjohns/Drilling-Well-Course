// Chapter 0 — cold open: the well in its template slot, the riser load pushes the conductor on the lower slot ring,
// three questions (0.2 % yield? 5 %? 2 %?), title.
import { E, ease, COL, clamp, smooth } from '../engine/core.js';
import { Scene } from '../engine/scene.js';
import { camSpline, DEF } from '../three/world.js';
import { updateSnow, glowBall, RING_D } from '../three/models.js';
import { label3D } from './kit.js';
import { setSwayShape, note } from './fx.js';
import { ringState, RINGU } from './ringfx.js';

export async function build(E, T, D) {
  const W3 = E.world, M = W3.M, md = W3.models;
  const b1 = T.b('0.1'), b2 = T.b('0.2'), b3 = T.b('0.3');
  const c = (id, n) => T.c(id, n);
  const th45 = Math.PI / 4;
  // a glow at the contact of conductor and ring D (registered so that other shots hide it)
  const glow = glowBall(M, '#ffb547', 0.1);
  glow.position.set((RING_D.ri + 0.01) * Math.cos(th45), RING_D.y1 + 0.01, (RING_D.ri + 0.01) * Math.sin(th45));
  glow.visible = false; W3.scene.add(glow); md.glowD = glow;

  // --------------------------------------------------------------------------------- shot A: the slot, the push
  const tA0 = b1.start, tA1 = b1.end + 0.3;
  const tPush = c('0.1', 'push');
  const camA = camSpline([
    { t: tA0, p: [10.5, 7.2, 13.5], l: [-2.2, 1.4, -2.2], fov: 38 },
    { t: c('0.1', 'slot') + 1.2, p: [3.5, 2.25, 8.4], l: [0, 1.5, 0], fov: 36 },
    { t: c('0.1', 'ring') + 1.6, p: [2.3, 1.35, 4.9], l: [0.05, 0.6, 0.05], fov: 36 },
    { t: tA1, p: [2.1, 1.4, 4.3], l: [0.12, 0.55, 0.12], fov: 36 },
  ]);
  const amp = (t) => 1.6 * smooth(t, tPush - 0.2, tPush + 2.2);
  W3.shot(tA0, tA1, {
    show: ['bop', 'well', 'template', 'seabed', 'snow', 'rays', 'glowD'],
    fadeIn: 1.4, fadeOut: 0.6, cam: camA, fog: 0.016, bg: '#0a3550',
    update: (t) => {
      W3.update(t); updateSnow(md.snow, t);
      for (const r of md.rays.children) r.material.opacity = 0.06 + 0.04 * Math.sin(t * 0.7 + r.userData.phase);
      md.rays.position.y = 40;
      setSwayShape();
      DEF.uDir.value.set(Math.cos(th45), Math.sin(th45));
      DEF.uAmp.value = amp(t);
      DEF.uStressMix.value = 0; DEF.uGlow.value = 0;
      const g = smooth(t, tPush + 0.4, tPush + 1.6);
      glow.material.opacity = 0.95 * g * (0.8 + 0.2 * Math.sin(t * 5));
      glow.scale.setScalar(0.6 * (0.6 + 0.4 * g));
    },
  });
  const S1 = new Scene(b1.start, tA1, { fade: 0.4 });
  S1.div('NORSOK U-001:2026 · FIGURE J.1', { x: 120, y: 120, cls: 'kicker' }).in(c('0.1', 'tmpl') + 0.6, 0.6, 'left');
  S1.div('Subsea wellhead in a template slot', { x: 120, y: 160, cls: 'small' }).in(c('0.1', 'tmpl') + 1.0, 0.6, 'left');
  label3D(S1, [0.82, 2.46, 0.0], 'Slot ring C <span class="sub">conductor housing lands here</span>', { t0: c('0.1', 'slot') + 1.0, t1: c('0.1', 'ring') + 1.0, anchor: 'lm', dx: 150, dy: -60, color: COL.yellow });
  label3D(S1, [-0.62, RING_D.y1, 0.1], 'Slot ring D <span class="sub">guides the conductor</span>', { t0: c('0.1', 'ring') + 1.6, t1: tA1, anchor: 'rm', dx: -150, dy: -40, color: COL.yellow });
  // the push of the conductor on the ring
  const push = S1.arrow(0, 0, 0, 0, { color: COL.amber, width: 6, head: 20 });
  push.in(tPush + 0.8, 0.5, 'none');
  const ps = S1.label('contact force on ring D', { x: 0, y: 0, cls: 'c-amber' }); ps.in(tPush + 1.2, 0.5, 'none');
  const setArrow = (g, a, b) => {
    const ang = Math.atan2(b.y - a.y, b.x - a.x), hd = 20;
    const bx = b.x - Math.cos(ang) * hd * 0.8, by = b.y - Math.sin(ang) * hd * 0.8;
    g.shaft.el.setAttribute('d', `M${a.x.toFixed(1)},${a.y.toFixed(1)} L${bx.toFixed(1)},${by.toFixed(1)}`);
    const hx = (k) => b.x - Math.cos(ang + k) * hd, hy = (k) => b.y - Math.sin(ang + k) * hd;
    g.tip.el.setAttribute('d', `M${hx(0.45).toFixed(1)},${hy(0.45).toFixed(1)} L${b.x.toFixed(1)},${b.y.toFixed(1)} L${hx(-0.45).toFixed(1)},${hy(-0.45).toFixed(1)} Z`);
  };
  E.anim(tPush - 0.2, tA1, (t) => {
    const p0 = W3.project([0.12 * Math.cos(th45), RING_D.y1 + 0.02, 0.12 * Math.sin(th45)], t), p1 = W3.project([(RING_D.ri + 0.02) * Math.cos(th45), RING_D.y1 + 0.02, (RING_D.ri + 0.02) * Math.sin(th45)], t);
    setArrow(push, p0, p1);
    ps.el.style.left = (p1.x + 24) + 'px'; ps.el.style.top = (p1.y + 6) + 'px';
  });

  // --------------------------------------------------------------------------------- shot B: the ring, questions, title
  const tB0 = b2.start - 0.3, tB1 = b3.end;
  const camB = camSpline([
    { t: tB0, p: [1.55, 2.25, 2.85], l: [-0.5, 0.3, 0.28], fov: 34 },
    { t: b3.start, p: [1.35, 2.1, 2.55], l: [-0.52, 0.32, 0.3], fov: 34 },
    { t: tB1, p: [1.25, 2.0, 2.4], l: [-0.55, 0.32, 0.3], fov: 34 },
  ]);
  W3.shot(tB0, tB1, {
    show: ['feRing'], fadeIn: 0.9, fadeOut: 0.8, cam: camB, fog: 0.0, bg: '#0b1824',
    update: () => { ringState(D, 'el', 0, 0); RINGU.uRF.value = 0; md.feRing.userData.lines.material.opacity = 0.18; },
    key: () => 'k',
  });
  const S2 = new Scene(tB0, b2.end, { fade: 0.5 });
  S2.div('When has it failed?', { x: 120, y: 190, cls: 'h1' }).in(b2.start + 0.3, 0.7, 'write');
  const qs = [['q1', '<span class="c-amber">0.2 %</span> plastic strain — the yield strength?'],
    ['q2', 'A strain limit of <span class="c-amber">5 %</span>?'],
    ['q3', 'Or <span class="c-amber">2 %</span> — from Eurocode 3, Part 1-5?']];
  qs.forEach(([cue, txt], i) => {
    const q = S2.card(`<div style="display:flex;gap:22px;align-items:flex-start"><div class="num" style="font-size:40px;color:#4fd1ff;line-height:1">${i + 1}</div><div style="font-weight:650;font-size:34px;line-height:1.25">${txt}</div></div>`,
      { x: 120, y: 330 + i * 170, w: 760, cls: 'glass' });
    q.in(c('0.2', cue) - 0.2, 0.6, 'left');
  });
  label3D(S2, [0.659 * Math.cos(th45), RING_D.y1, 0.659 * Math.sin(th45)], 'contact force', { t0: b2.start + 1.2, t1: b2.end, anchor: 'lm', dx: 120, dy: 60, color: COL.amber });
  label3D(S2, [1.2, RING_D.y, 0], 'strut', { t0: b2.start + 1.6, t1: b2.end, anchor: 'lm', dx: 70, dy: -40 });

  // title
  const S3 = new Scene(b3.start, b3.end, { fade: 0.7 });
  const dim = S3.div('', { x: 0, y: 0, w: 1920, h: 1080, style: 'background:linear-gradient(90deg, rgba(4,12,20,0.94) 0%, rgba(4,12,20,0.80) 55%, rgba(4,12,20,0.40) 100%)' });
  dim.in(b3.start, 1.0, 'none');
  S3.div('NORSOK U-001:2026 → N-001 → N-004 → EUROCODE 3', { x: 140, y: 290, cls: 'kicker' }).in(b3.start + 0.3, 0.6, 'left');
  S3.div('The template interface', { x: 136, y: 340, cls: 'h1', w: 1500, style: 'font-size:96px' }).in(b3.start + 0.5, 0.9, 'write');
  S3.div('When has it failed?', { x: 140, y: 470, cls: 'h2', w: 1300, style: 'color:#ffb547' }).in(b3.start + 1.2, 0.7, 'rise');
  const bar = S3.div('', { x: 140, y: 560, w: 640, h: 6, cls: 'bar' });
  bar.el.style.transformOrigin = '0 50%'; bar.set(0, { sx: 0 }).to(b3.start + 1.4, 1.0, { sx: 1 }, ease.out3);
  const pills = [['who', '1 · Who owns the interface'], ['what', '2 · Failure on each side'], ['ec', '3 · What Eurocode 3 says'], ['check', '4 · The slot ring, checked both ways']];
  pills.forEach(([cue, txt], i) => {
    const p = S3.div(`<span class="badge" style="font-size:20px;letter-spacing:0.08em">${txt}</span>`, { x: 140, y: 620 + i * 62 });
    p.in(c('0.3', cue), 0.5, 'left');
  });
  note(S3, 'A follow-up to “Acceptance criteria for structural analysis — NORSOK U-001:2026, Annex B”', { t0: b3.start + 1.5, t1: b3.end - 0.4 });
}
