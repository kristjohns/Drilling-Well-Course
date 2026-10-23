// Chapter 0 — cold open: a drive-off bends the wellhead, the FE model shows a red spot above yield, three questions, title.
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt } from '../engine/core.js';
import { Scene } from '../engine/scene.js';
import { camSpline, DEF, THREE } from '../three/world.js';
import { updateSnow, FEU, feSetElastic } from '../three/models.js';
import { label3D, counter } from './kit.js';
import { setSwayShape, vmLegend, probe3D, datumLoads, note } from './fx.js';

export async function build(E, T, D) {
  const W3 = E.world, M = W3.M, md = W3.models;
  const b1 = T.b('0.1'), b2 = T.b('0.2'), b3 = T.b('0.3');
  const c = (id, n) => T.c(id, n);
  const L = D.loads.als;

  // --------------------------------------------------------------------------------- shot A: the drive-off
  const tA0 = b1.start, tA1 = c('0.1', 'fe') + 0.2;
  const tPull = c('0.1', 'pull'), tMom = c('0.1', 'moment');
  const camA = camSpline([
    { t: tA0, p: [13, 26, 24], l: [0, 52, 0], fov: 40 },
    { t: tPull + 0.5, p: [15, 17, 25], l: [0, 12, 0], fov: 40 },
    { t: tMom + 0.6, p: [12, 10.5, 19], l: [0.3, 6.5, 0], fov: 38 },
    { t: tA1, p: [6.0, 6.0, 9.6], l: [0.4, 4.6, 0], fov: 36 },
  ]);
  const lean = (t) => 0.035 * smooth(t, tPull, tPull + 4.0);
  const bend = (t) => 4.2 * smooth(t, tPull + 0.8, tMom + 1.5);
  W3.shot(tA0, tA1, {
    show: ['riser', 'bop', 'well', 'template', 'seabed', 'snow', 'snowHigh', 'rays'],
    fadeIn: 1.4, fadeOut: 0.6, cam: camA, fog: 0.017, bg: '#0a3550',
    update: (t) => {
      W3.update(t); updateSnow(md.snow, t); updateSnow(md.snowHigh, t);
      for (const r of md.rays.children) r.material.opacity = 0.06 + 0.04 * Math.sin(t * 0.7 + r.userData.phase);
      md.rays.position.y = 40;
      setSwayShape();
      DEF.uAmp.value = bend(t);
      const th = lean(t);
      md.riser.rotation.z = -th;
      md.riser.position.set(18.5 * Math.sin(th) + DEF.uAmp.value * 0.06 * (1 + 0.42 * 14.5), 18.5 * (1 - Math.cos(th)), 0);
      DEF.uStressMix.value = 0; DEF.uGlow.value = 0;
    },
  });
  const S1 = new Scene(b1.start, tA1, { fade: 0.4 });
  const k = S1.div('ACCIDENTAL LOAD CASE · DRIVE-OFF', { x: 120, y: 120, cls: 'kicker' });
  k.in(c('0.1', 'rig') + 0.4, 0.6, 'left');
  const sub = S1.div('350 m water depth · BOP on the wellhead', { x: 120, y: 160, cls: 'small' });
  sub.in(c('0.1', 'rig') + 0.9, 0.6, 'left');
  datumLoads(S1, [0, 4.0, 0], { t0: tMom, t1: tA1, scale: 1.05, show: ['M'], labels: { M: `<span class="num">${fmt(L.Mw_kNm)}</span> kNm` } });
  label3D(S1, (t) => [0.5 + DEF.uAmp.value * 0.06, 4.6, 0.6], 'Wellhead', { t0: tMom + 1.6, t1: tA1, anchor: 'lm', dx: 120, dy: 70 });

  // --------------------------------------------------------------------------------- shot B: the FE model
  const tB0 = c('0.1', 'fe') - 0.3, tB1 = b3.end;
  const tRed = c('0.1', 'red');
  const camB = camSpline([
    { t: tB0, p: [2.6, 3.35, 6.2], l: [0.05, 2.7, 0], fov: 30 },
    { t: tRed - 1.2, p: [1.2, 3.55, 2.9], l: [0.2, 3.3, 0], fov: 30 },
    { t: tRed + 0.6, p: [0.62, 3.47, 0.95], l: [0.33, 3.4, 0], fov: 30 },
    { t: c('0.1', 'above') + 1.5, p: [0.66, 3.49, 1.05], l: [0.31, 3.39, 0], fov: 30 },
    { t: b2.start + 2.0, p: [0.35, 3.62, 2.75], l: [-0.42, 3.3, 0], fov: 30 },
    { t: b3.start, p: [0.25, 3.66, 2.9], l: [-0.5, 3.3, 0], fov: 30 },
    { t: tB1, p: [0.1, 3.7, 3.1], l: [-0.6, 3.25, 0], fov: 30 },
  ]);
  W3.shot(tB0, tB1, {
    show: ['feHousing'], fadeIn: 0.9, fadeOut: 0.8, cam: camB, fog: 0.0, bg: '#0b1824',
    update: (t) => {
      feSetElastic({ Mw: L.Mw_kNm / 1000, Qw: L.Qw_kN / 1000, Tw: L.Tw_MN, p: D.loads.p_i });
      FEU.uFE.value = smooth(t, tRed - 1.0, tRed + 0.3);
    },
    key: (t) => (t < tRed + 0.5 ? t.toFixed(3) : 'k'),
  });
  const S2 = new Scene(tB0, b2.end, { fade: 0.5 });
  const m1 = S2.div('FE MODEL · HP WELLHEAD HOUSING<br><span style="color:#b9cad8">ACCIDENTAL LOADS + RATED PRESSURE</span>', { x: 120, y: 110, cls: 'kicker', style: 'line-height:1.7' });
  m1.in(c('0.1', 'fe') + 0.6, 0.6, 'left'); m1.out(tRed - 0.6, 0.4);
  vmLegend(S2, { x: 1610, y: 250, t0: tRed + 0.2, t1: b2.end - 0.6 });
  const pk = probe3D(S2, [0.352, 3.416, 0.0], `<span style="font-size:40px;font-weight:800;color:#ff5a4a" class="num">793 MPa</span><span class="sub">peak von Mises, neck fillet</span>`,
    { t0: tRed + 0.1, t1: b2.end, dx: -360, dy: 150, color: '#ff5a4a' });
  const ab = S2.div(`<span class="num" style="color:#ffb547">+53 %</span> above σ<sub>y</sub> = <span class="num">${D.material.sy}</span> MPa`, { x: 120, y: 900, cls: 'h3' });
  ab.in(c('0.1', 'above'), 0.6, 'pop'); ab.out(b2.start + 0.4, 0.4);
  note(S2, 'Illustrative stress field (teaching stand-in, not an FE result)', { t0: tRed + 0.5, t1: b2.end - 0.5 });
  // questions
  const qs = [['q1', 'Is the acceptance criterion the <span class="c-amber">yield strength</span>?'],
    ['q2', 'Or a <span class="c-amber">strain limit</span> from an elastic-plastic analysis?'],
    ['q3', 'What do we <span class="c-amber">take out of the FE model</span> — and compare with what?']];
  const hd = S2.div('Has it failed?', { x: 120, y: 200, cls: 'h1' });
  hd.in(b2.start + 0.3, 0.7, 'write');
  qs.forEach(([cue, txt], i) => {
    const q = S2.card(`<div style="display:flex;gap:22px;align-items:flex-start"><div class="num" style="font-size:40px;color:#4fd1ff;line-height:1">${i + 1}</div><div style="font-weight:650;font-size:34px;line-height:1.25">${txt}</div></div>`,
      { x: 120, y: 340 + i * 190, w: 760, cls: 'glass' });
    q.in(c('0.2', cue) - 0.2, 0.6, 'left');
  });

  // --------------------------------------------------------------------------------- title
  const S3 = new Scene(b3.start, b3.end, { fade: 0.7 });
  const dim = S3.div('', { x: 0, y: 0, w: 1920, h: 1080, style: 'background:linear-gradient(90deg, rgba(4,12,20,0.94) 0%, rgba(4,12,20,0.78) 55%, rgba(4,12,20,0.35) 100%)' });
  dim.in(b3.start, 1.0, 'none');
  S3.div('NORSOK U-001:2026 · ANNEX B', { x: 140, y: 290, cls: 'kicker' }).in(b3.start + 0.3, 0.6, 'left');
  S3.div('Acceptance criteria<br>for structural analysis', { x: 136, y: 340, cls: 'h1', w: 1500, style: 'font-size:92px' }).in(c('0.3', 'std') - 0.6, 0.9, 'write');
  S3.div('Yield strength, strain limits, and how to read an FE model', { x: 140, y: 560, cls: 'body', w: 1300 }).in(c('0.3', 'std') + 0.8, 0.7, 'rise');
  const bar = S3.div('', { x: 140, y: 630, w: 640, h: 6, cls: 'bar' });
  bar.el.style.transformOrigin = '0 50%'; bar.set(0, { sx: 0 }).to(c('0.3', 'std') + 1.0, 1.0, { sx: 1 }, ease.out3);
  const pills = [['curve', '1 · The stress–strain diagram'], ['extract', '2 · Extracting stress from FE'], ['ep', '3 · The elastic–plastic check'], ['verdict', '4 · A verdict on the red spot']];
  pills.forEach(([cue, txt], i) => {
    const p = S3.div(`<span class="badge" style="font-size:20px;letter-spacing:0.08em">${txt}</span>`, { x: 140, y: 690 + i * 62 });
    p.in(c('0.3', cue), 0.5, 'left');
  });
}
