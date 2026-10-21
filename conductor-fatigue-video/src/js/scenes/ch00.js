// Chapter 0 — cold open: rig in the swell, down the riser, the swaying stack, slice into the seabed, hot spots, title.
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt } from '../engine/core.js';
import { Scene } from '../engine/scene.js';
import { camPath, camSpline, DEF, setProfile, THREE } from '../three/world.js';
import { updateSnow, updateSnowCam, glowBall } from '../three/models.js';
import { label3D, counter } from './kit.js';
import { weldToe } from './drawings.js';

export async function build(E, T, D) {
  const W3 = E.world, M = W3.M, md = W3.models;
  const b1 = T.b('0.1'), b2 = T.b('0.2'), b3 = T.b('0.3');
  const c = (id, n) => T.c(id, n);

  // deflection shape for the sway: the local model at +-1500 kNm (inner string), unit amplitude
  const pr = D.profiles.base;
  const sway = (t, t0, A = 22) => {
    // two half swings keyed to the narration, then a steady wave-period rocking
    const u = Math.max(0, t - t0);
    return A * Math.sin(2 * Math.PI * u / 6.0) * smooth(t, t0 - 0.2, t0 + 1.2);
  };

  // --------------------------------------------------------------------------------- shot A: surface -> seabed
  const tA0 = b1.start, tA1 = b1.end;
  const tR = c('0.1', 'riser'), tBop = c('0.1', 'bop'), tBend = c('0.1', 'bend');
  // one continuous move: the rig in the swell, skim the surface, dive and plunge down the riser to the BOP
  const camA = camSpline([
    { t: tA0, p: [190, 410, 280], l: [0, 381, 0], fov: 38 },
    { t: tR - 2.6, p: [96, 378, 142], l: [0, 369, 0], fov: 38 },
    { t: tR - 0.7, p: [30, 358.4, 7], l: [0, 345, 0], fov: 42 },
    { t: tR + 0.2, p: [9, 336, 5], l: [0, 300, 0], fov: 46 },
    { t: tBop + 1.3, p: [8, 52, 12], l: [0, 18, 0], fov: 46 },
    { t: tBop + 2.7, p: [16, 20, 24], l: [0, 10, 0], fov: 40 },
    { t: tBend, p: [15, 13, 22], l: [0, 8.5, 0], fov: 38 },
    { t: tA1, p: [19, 9.5, 27], l: [0, 6.5, 0], fov: 36 },
  ]);
  const under = (y) => clamp((355.2 - y) / 1.5);
  // daylight: sun high on the right of the opening view, sky reflected in the swell
  const f0 = new THREE.Vector3(-190, 0, -280).normalize(), r0 = new THREE.Vector3(-f0.z, 0, f0.x);
  const sunA = r0.clone().multiplyScalar(0.8).add(f0.clone().multiplyScalar(-0.25)).normalize().multiplyScalar(Math.cos(0.55)).setY(Math.sin(0.55)).normalize();
  const C = (h) => new THREE.Color(h);
  const day = { top: C('#1f5a94'), hor: C('#bcd3e4'), low: C('#2f4a60'), sea: C('#a9c4d8'), sun: C('#fff3df'), haze: C('#a7c0d4'), key: C('#fff1dc') };
  const deep = C('#062a42'), mid = C('#0d4766'), shallow = C('#1a6b8e'), bgc = new THREE.Color();
  W3.shot(tA0, tA1, {
    show: ['sky', 'rig', 'sea', 'riser', 'bop', 'well', 'template', 'seabed', 'snowHigh', 'snow', 'snowCam', 'rays'],
    fadeIn: 1.2, fadeOut: 0.01,
    cam: camA,
    fog: (t) => { const y = camA(t).p[1]; return lerp(0.0011, 0.022 + 0.01 * clamp((300 - y) / 280), under(y)); },
    update: (t) => {
      const cp = camA(t).p, y = cp[1];
      const u = under(y), above = 1 - u;
      bgc.copy(deep).lerp(mid, smooth(y, 40, 220)).lerp(shallow, smooth(y, 220, 350)).lerp(day.haze, above);
      W3.scene.background = bgc.clone(); W3.scene.fog.color.copy(bgc);
      W3.update(t);
      md.rig.position.y = 354 + 1.3 * Math.sin(0.55 * t);
      md.rig.rotation.z = 0.012 * Math.sin(0.55 * t + 0.6);
      md.sea.visible = y > 250; md.rig.visible = y > 250; md.sky.visible = above > 0.01;     // fully fogged out below 250 m
      M.sun.dir.value.copy(sunA); M.sun.col.value.copy(day.sun); M.sun.i.value = 0.7 * above; M.sun.sky.value.copy(day.sea);
      M.sky.top.value.copy(day.top); M.sky.hor.value.copy(day.hor); M.sky.low.value.copy(day.low); M.sky.disc.value = 0.8;
      const d0 = W3.lightDefaults;
      W3.key.color.copy(d0.keyCol).lerp(day.key, above); W3.key.intensity = lerp(2.4, 2.8, above);
      W3.key.position.copy(d0.keyPos).lerp(sunA.clone().multiplyScalar(120), above);
      W3.scene.environmentIntensity = lerp(1, 0.55, above);
      updateSnow(md.snowHigh, t); updateSnow(md.snow, t); updateSnowCam(md.snowCam, t, cp);
      md.snowCam.visible = y > 12 && y < 352;
      for (const r of md.rays.children) r.material.opacity = (0.07 + 0.04 * Math.sin(t * 0.7 + r.userData.phase)) * u;
      md.rays.position.y = lerp(30, 300, smooth(y, 60, 260));
      setProfile(pr.z, pr.v_in, pr.M_in);
      DEF.uAmp.value = sway(t, c('0.1', 'bend'));
      DEF.uStressMix.value = 0; DEF.uGlow.value = 0;
    },
  });

  // overlay: count of cycles
  const S1 = new Scene(b1.start, b1.end + 0.4, { fade: 0.4 });
  const cnt = counter(S1, { x: 1500, y: 880, a: 0, b: 7472771, t0: c('0.1', 'count'), t1: c('0.1', 'count') + 2.6, size: 72, anchor: 'cm', color: COL.amber });
  cnt.in(c('0.1', 'count') - 0.2, 0.5);
  const cntl = S1.div('cycles per year at the wellhead', { x: 1500, y: 945, cls: 'small', anchor: 'cm' });
  cntl.in(c('0.1', 'count') + 0.3, 0.5);
  const lbB = label3D(S1, [1.9, 13, 0], 'Blowout preventer stack', { t0: c('0.1', 'bop') + 1.7, t1: c('0.1', 'count') - 0.3, anchor: 'lm', dx: 70, dy: -40 });
  const lbW = label3D(S1, [0.4, 3.6, 0], 'Wellhead', { t0: c('0.1', 'bend') + 0.3, t1: c('0.1', 'count') - 0.3, anchor: 'lm', dx: 60, dy: 30 });

  // --------------------------------------------------------------------------------- shot B: slice + hot spots + title
  const tB0 = b2.start, tB1 = b3.end;
  const tSlice0 = b2.start + 0.8, tSlice1 = b2.start + 3.4;
  const camB = camPath([
    { t: tB0, p: [16, 7.5, 21], l: [0, 2.5, 0], fov: 36 },
    { t: tSlice1, p: [9.5, 2.5, 13.5], l: [0, 0.3, 0], fov: 36 },
    { t: c('0.2', 'gw'), p: [5.0, 1.6, 7.6], l: [0.2, 1.2, 0], fov: 34 },
    { t: c('0.2', 'q'), p: [6.5, 2.4, 9.8], l: [0, 1.0, 0], fov: 36 },
    { t: tB1, p: [8.0, 3.2, 12.5], l: [0, 1.2, 0], fov: 36 },
  ]);
  const glowGW = glowBall(M, '#ff6f61', 0.16), glowTS = glowBall(M, '#ff6f61', 0.16);
  glowGW.position.set(0.46, 1.0, 0.02); glowTS.position.set(0.68, 2.39, 0.05);
  W3.scene.add(glowGW); W3.scene.add(glowTS);
  md.glowGW = glowGW; md.glowTS = glowTS;
  W3.shot(tB0, tB1, {
    show: ['bop', 'template', 'seabed', 'snow', 'rays', 'well', 'wellCut', 'templateCut', 'seabedCut', 'sliceFace', 'glowGW', 'glowTS'],
    fadeIn: 0.01, fadeOut: 0.8,
    cam: camB, fog: 0.016,
    update: (t) => {
      W3.update(t);
      W3.scene.background = new THREE.Color('#07304a'); W3.scene.fog.color.set('#07304a');
      updateSnow(md.snow, t);
      const u = ramp(t, tSlice0, tSlice1, ease.inOut);         // slice plane sweeps from z = 14 to z = 0
      const zc = lerp(14, 0, u);
      const cutDone = u >= 1;
      W3.clip.constant = u <= 0 || cutDone ? 1e4 : zc;
      md.well.visible = !cutDone; md.wellCut.visible = cutDone;
      md.template.visible = !cutDone; md.templateCut.visible = cutDone;
      md.seabed.visible = !cutDone; md.seabedCut.visible = cutDone;
      md.sliceFace.visible = u > 0 && !cutDone; md.sliceFace.position.z = zc - 0.01;
      md.bop.visible = true;
      setProfile(pr.z, pr.v_in, pr.M_in);
      DEF.uAmp.value = sway(t, tB0 - 30) * (1 - smooth(t, tB0, tSlice0));
      const g1 = smooth(t, c('0.2', 'gw') - 0.3, c('0.2', 'gw') + 0.6), g2 = smooth(t, c('0.2', 'ts') - 0.3, c('0.2', 'ts') + 0.6);
      const pulse = 0.75 + 0.25 * Math.sin(t * 4);
      glowGW.visible = g1 > 0.01; glowGW.material.opacity = g1 * pulse;
      glowTS.visible = g2 > 0.01; glowTS.material.opacity = g2 * pulse;
      DEF.uGlowY.value = 1.0; DEF.uGlow.value = 1.2 * g1 * pulse;
      DEF.uStressMix.value = 0;
    },
    key: (t) => t.toFixed(3),
  });
  W3.models.glowGW = glowGW; W3.models.glowTS = glowTS;

  const S2 = new Scene(b2.start, b2.end, { fade: 0.4 });
  const ins = S2.card('<div class="tiny" style="margin-bottom:8px">WELD TOE · CROSS-SECTION</div>', { x: 1330, y: 520, w: 470, h: 300, cls: 'glass' });      // created before the svg layer so the drawing sits on top
  label3D(S2, [0.47, 1.0, 0], '<b>GW1</b> · conductor girth weld<span class="sub">conductor housing → conductor extension</span>', { t0: c('0.2', 'gw') + 0.2, t1: b2.end, anchor: 'rm', dx: -150, dy: 120, color: COL.coral });
  label3D(S2, [0.7, 2.4, 0], '<b>TS1</b> · template slot weld<span class="sub">slot ring → support beam</span>', { t0: c('0.2', 'ts') + 0.2, t1: b2.end, anchor: 'rm', dx: -170, dy: -110, color: COL.coral });
  // crack inset
  ins.in(c('0.2', 'gw') + 1.2, 0.6);
  const wt = weldToe(S2, 1545, 660, { s: 0.5 });
  wt.g.in(c('0.2', 'gw') + 1.4, 0.6, 'none');
  wt.grow(c('0.2', 'gw') + 2.0, c('0.2', 'q') - 0.2);
  const q = S2.card('<div class="h2" style="font-size:46px;text-align:center">How many days can we keep a riser connected?</div>', { x: 960, y: 1010, anchor: 'cb', cls: 'glass', style: 'padding:22px 40px' });
  q.in(c('0.2', 'q'), 0.8, 'write');

  // promise / title
  const S3 = new Scene(b3.start, b3.end, { fade: 0.6 });
  const dim = S3.div('', { x: 0, y: 0, w: 1920, h: 1080, style: 'background:linear-gradient(90deg, rgba(4,12,20,0.88) 0%, rgba(4,12,20,0.55) 55%, rgba(4,12,20,0.15) 100%)' });
  dim.in(b3.start, 1.0, 'none');
  S3.div('NORSOK U-001:2026 · ANNEX A, B &amp; J', { x: 140, y: 300, cls: 'kicker' }).in(b3.start + 0.3, 0.6, 'left');
  S3.div('Fatigue of the conductor<br>and the conductor–template interface', { x: 136, y: 350, cls: 'h1', w: 1500 }).in(c('0.3', 'std') - 0.4, 0.9, 'write');
  S3.div('The NORSOK method, every equation derived, step by step', { x: 140, y: 540, cls: 'body', w: 1200 }).in(c('0.3', 'derive'), 0.7, 'rise');
  const bar = S3.div('', { x: 140, y: 620, w: 640, h: 6, cls: 'bar' });
  bar.el.style.transformOrigin = '0 50%'; bar.set(0, { sx: 0 }).to(c('0.3', 'derive') + 0.3, 1.0, { sx: 1 }, ease.out3);
  const ex = S3.div('<span class="badge warn">Worked example included</span>', { x: 140, y: 670 });
  ex.in(c('0.3', 'example'), 0.5, 'pop');
}
