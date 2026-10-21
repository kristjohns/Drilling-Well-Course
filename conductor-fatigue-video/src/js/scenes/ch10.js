// Chapter 10 — the method on one page, then the outro: the cut closes, the camera pulls back up the riser to the rig at dawn.
import { E, ease, COL, clamp, smooth, ramp, lerp } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause, step } from '../engine/hud.js';
import { camSpline, DEF, THREE } from '../three/world.js';
import { updateSnow, updateSnowCam, glowBall } from '../three/models.js';
import { label3D } from './kit.js';

// shrink an equation to a maximum width (after layout)
function fit(e, maxW) {
  later(() => {
    const w = e.el.offsetWidth;
    if (w > maxW) { e.el.style.fontSize = (parseFloat(e.el.style.fontSize) * maxW / w).toFixed(1) + 'px'; e.layout(); }
  });
  return e;
}

export async function build(E, T, D) {
  const ch = T.ch(10);
  titleCard(ch, 'The whole method on one page');
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n), w = (id, word, k = 0) => T.w(id, word, k);
  const W3 = E.world, M = W3.M, md = W3.models;

  // ------------------------------------------------------------------ 10.1 the summary board
  {
    const B = b('10.1');
    const S = new Scene(B.start, B.end, { fade: 0.6 });
    clause('NORSOK U-001:2026 · 13.3.6 · A.3.5 · B.2.6 · B.4 · Annex J', B.start + 0.5, B.end);
    S.div('The method on one page', { x: 120, y: 112, cls: 'h2' }).in(B.start + 0.2, 0.7, 'write');
    const tiles = [
      { n: '01', title: 'Loads', ref: 'A.3.5 · TABLES A.7, A.8', eqs: ['\\cm{\\Delta M_i} = r_i\\,\\cm{\\Delta M_o}', '\\cm M(z) = \\cm{M_w}\\left(1+\\dfrac{z}{H}\\right)'], cap: 'annual histogram at the<br>wellhead datum' },
      { n: '02', title: 'Load share', ref: '13.3.6 · ANNEX J', eqs: ['F_i = \\dfrac{k_i}{\\sum k}\\,F', '\\cy{k_{\\theta,T}} = \\dfrac{k_C\\,k_D}{k_C+k_D}\\,h^2'], cap: 'stiffness attracts load,<br>gaps make it nonlinear' },
      { n: '03', title: 'Local model', ref: 'B.4.2.4 · BEAM ON SPRINGS', eqs: ['EI\\,\\dfrac{\\dd^4 y}{\\dd z^4} + k\\,y = 0', '\\beta = \\left(\\dfrac{k}{4EI}\\right)^{1/4}'], cap: 'peak moment just below<br>the mudline' },
      { n: '04', title: 'Hot-spot stress', ref: 'BEAM THEORY · SCF', eqs: ['\\cs\\sigma = \\dfrac{\\cm M}{W},\\;\\; I = \\dfrac{\\pi}{64}\\left(D^4-d^4\\right)', '\\mathrm{SCF} = 1+\\dfrac{3e}{t}'], cap: 'nominal stress × stress<br>concentration factor' },
      { n: '05', title: 'M–N curve', ref: 'B.4.4 · (B.8)–(B.11)', eqs: ['\\cn N = \\bar a_{\\Delta M}\\,\\DM^{-\\cv m}', '\\log\\DM_{1,2} = \\dfrac{\\log\\bar a_{2}-\\log\\bar a_{1}}{\\cv{m_2}-\\cv{m_1}}'], cap: 'lower bound of the<br>local model results' },
      { n: '06', title: 'Damage', ref: 'PALMGREN–MINER', eqs: ['D = \\sum_i \\dfrac{n_i}{\\cn{N_i}}', 'T_f = \\dfrac{1\\ \\text{yr}}{D_{\\text{year}}}'], cap: 'failure when D reaches 1,<br>life = 1 / annual damage' },
      { n: '07', title: 'Design check', ref: '(B.3) · TABLE B.4', eqs: ['\\dfrac{T_f}{\\cg{D_F}} \\;\\ge\\; T_{\\text{riser}}', '\\cg{D_F} = 10'], cap: 'at least one year of<br>riser-connected time' },
      { n: '08', title: 'Screen & mitigate', ref: '(B.12)–(B.14)', eqs: ['\\DM_{\\mathrm{eq}} = \\Big[\\tfrac{1}{n}\\textstyle\\sum_i n_i\\,\\DM_i^{\\cv m}\\Big]^{1/\\cv m}', '\\dfrac{\\DM_c}{\\cg{D_F}^{\\,1/\\cv m}} \\;\\ge\\; \\DM_o'], cap: 'fails? refine, stiffen,<br>limit riser days, monitor' },
    ];
    const cues = ['loads', 'share', 'soil', 'stress', 'mn', 'damage', 'check'].map((k) => c('10.1', k));
    cues.push(w('10.1', 'check'));
    const TW = 405, TH = 362, X0 = 120, Y0 = 192, GX = 20, GY = 20;
    tiles.forEach((tl, i) => {
      const x = X0 + (i % 4) * (TW + GX), y = Y0 + Math.floor(i / 4) * (TH + GY);
      const tc = cues[i], tn = i < 7 ? cues[i + 1] : B.end - 1.2;
      const card = S.card(`<div style="display:flex;align-items:baseline;gap:14px"><span class="num" style="font-size:24px;color:var(--cyan)">${tl.n}</span>` +
        `<span style="font-weight:750;font-size:31px;color:var(--ink)">${tl.title}</span></div>` +
        `<div class="mono" style="font-size:15px;color:var(--dim);letter-spacing:0.08em;margin-top:6px">${tl.ref}</div>`, { x, y, w: TW, h: TH, cls: 'glass' });
      card.el.style.padding = '22px 26px';
      card.set(0, { o: 0, y: 18 }).to(B.start + 0.5 + i * 0.07, 0.6, { o: 0.32, y: 0 }, ease.out3).to(tc - 0.1, 0.5, { o: 1 });
      const glow = S.div('', { x, y, w: TW, h: TH, style: `border:2px solid ${COL.amber};border-radius:20px;box-shadow:0 0 44px rgba(255,181,71,0.33), inset 0 0 30px rgba(255,181,71,0.08)` });
      glow.in(tc - 0.1, 0.5, 'none').out(tn - 0.2, 0.6);
      tl.eqs.forEach((tex, j) => {
        const e = fit(S.eq(tex, { x: x + TW / 2, y: y + 160 + j * 90, size: 30 }), TW - 44);
        e.in(tc + 0.15 + j * 0.45, 0.6, 'write');
      });
      const cap = S.div(tl.cap, { x: x + 26, y: y + TH - 26, cls: 'tiny', anchor: 'lb', style: `width:${TW - 52}px;letter-spacing:0.04em;line-height:1.3` });
      cap.in(tc + 0.9, 0.5, 'none');
      step(tc, i);
    });
    // everything lit: one sweep of light across the board
    const sweep = S.div('', { x: X0 - 200, y: Y0, w: 180, h: 2 * TH + GY, style: 'background:linear-gradient(90deg, rgba(79,209,255,0) 0%, rgba(79,209,255,0.16) 50%, rgba(79,209,255,0) 100%);border-radius:20px' });
    const tSw = cues[7] + 2.0;
    sweep.set(0, { o: 0 }).set(tSw, { o: 1 }).to(tSw, 1.6, { x: 4 * (TW + GX) + 220 }, ease.inOut).to(tSw + 1.45, 0.15, { o: 0 });
  }

  // ------------------------------------------------------------------ 10.2 outro
  {
    const B = b('10.2');
    step(B.start, -1, { show: false });
    const tEnd = T.duration;
    const tU0 = w('10.2', 'field') - 0.2, tU1 = tU0 + 2.6;        // the cut closes (plane z = 0 -> 14)
    const cam = camSpline([
      { t: B.start, p: [8.0, 3.2, 12.5], l: [0, 1.2, 0], fov: 36 },
      { t: tU0, p: [7.0, 2.8, 11.0], l: [0, 1.3, 0], fov: 36 },
      { t: tU1, p: [7.8, 3.6, 12.4], l: [0, 1.8, 0], fov: 36 },
      { t: tU1 + 3.6, p: [16, 10, 24], l: [0, 7, 0], fov: 40 },
      { t: tU1 + 6.4, p: [9, 34, 13], l: [0, 52, 0], fov: 46 },
      { t: tU1 + 9.6, p: [7, 170, 10], l: [0, 205, 0], fov: 48 },
      { t: tU1 + 12.4, p: [8, 326, 12], l: [0, 350, 0], fov: 46 },
      { t: tU1 + 14.4, p: [64, 359.6, 104], l: [-8, 370, 8], fov: 42 },
      { t: tU1 + 17.4, p: [110, 366, 170], l: [-30, 379, 20], fov: 38 },
      { t: tEnd, p: [185, 372, 280], l: [-52, 384, 35], fov: 36 },
    ]);
    const gGW = glowBall(M, '#ff6f61', 0.16), gTS = glowBall(M, '#ff6f61', 0.16);
    gGW.position.set(0.46, 1.0, 0.02); gTS.position.set(0.68, 2.39, 0.05);
    for (const [k, o] of [['glowGW10', gGW], ['glowTS10', gTS]]) { o.visible = false; W3.scene.add(o); md[k] = o; }
    // dawn: low sun behind and right of the rig, as seen from the final camera
    const fwd = new THREE.Vector3(-52 - 185, 0, 35 - 280).normalize(), right = new THREE.Vector3(-fwd.z, 0, fwd.x);      // camera right = fwd x up
    const sunDir = fwd.clone().multiplyScalar(Math.cos(0.36)).add(right.clone().multiplyScalar(Math.sin(0.36))).multiplyScalar(0.9975).setY(0.07).normalize();
    const C = (h) => new THREE.Color(h);
    const dawn = { key: C('#ffb877'), hemiSky: C('#f2b48a'), hemiGround: C('#1c2a3a'), fill: C('#7aa6d6'), top: C('#203f69'), hor: C('#ffb07a'), low: C('#2c3346'), sea: C('#f0a576'), sun: C('#ffd6a6'), haze: C('#c99a86') };
    const deep = C('#062a42'), mid = C('#0d4766'), shallow = C('#1a6b8e');
    const tmp = new THREE.Color();
    const show = ['sky', 'rig', 'sea', 'riser', 'bop', 'well', 'template', 'seabed', 'wellCut', 'templateCut', 'seabedCut', 'sliceFace', 'snow', 'snowHigh', 'snowCam', 'rays', 'glowGW10', 'glowTS10'];
    W3.shot(B.start, tEnd + 1, {
      show, fadeIn: 1.0, fadeOut: 0.01, cam,
      fog: (t) => { const y = cam(t).p[1]; const u = clamp((355.2 - y) / 1.5); return lerp(0.0019, 0.022 + 0.008 * clamp((300 - y) / 280), u); },
      update: (t) => {
        W3.update(t);
        const cp = cam(t).p, y = cp[1];
        const under = clamp((355.2 - y) / 1.5), above = 1 - under;
        // background / fog colour: deep water -> shallow water -> dawn haze
        tmp.copy(deep).lerp(mid, smooth(y, 40, 220)).lerp(shallow, smooth(y, 220, 350)).lerp(dawn.haze, above);
        W3.scene.background = tmp.clone(); W3.scene.fog.color.copy(tmp);
        // the cut closes: cut models until tU0, then full models clipped by a plane moving out to z = 14
        const u = ramp(t, tU0, tU1, ease.inOut);
        const cut = t < tU0, closing = t >= tU0 && u < 1;
        md.wellCut.visible = cut; md.templateCut.visible = cut; md.seabedCut.visible = cut;
        md.well.visible = !cut; md.template.visible = !cut; md.seabed.visible = !cut;
        md.sliceFace.visible = closing; md.sliceFace.position.z = lerp(0, 14, u) - 0.01;
        W3.clip.constant = closing ? lerp(0, 14, u) : 1e4;
        // hot spots glow while the narration names them
        const g = smooth(t, c('10.2', 'back') - 0.2, c('10.2', 'back') + 0.8) * (1 - smooth(t, tU0 - 0.6, tU0 + 0.4));
        const pulse = 0.75 + 0.25 * Math.sin(t * 4);
        gGW.visible = gTS.visible = g > 0.01; gGW.material.opacity = gTS.material.opacity = g * pulse;
        DEF.uAmp.value = 0; DEF.uStressMix.value = 0; DEF.uGlowY.value = 1.0; DEF.uGlow.value = 1.2 * g * pulse;
        // water column
        updateSnow(md.snow, t); updateSnow(md.snowHigh, t); updateSnowCam(md.snowCam, t, cp);
        md.snow.visible = y < 90; md.snowHigh.visible = y > 20 && y < 356; md.snowCam.visible = y > 12 && y < 352;
        for (const r of md.rays.children) r.material.opacity = (0.07 + 0.04 * Math.sin(t * 0.7 + r.userData.phase)) * under;
        md.rays.position.y = lerp(30, 300, smooth(y, 60, 260));
        md.rays.visible = under > 0.01;
        // surface: rig in the swell, sky only from above
        md.rig.position.y = 354 + 1.3 * Math.sin(0.55 * t);
        md.rig.rotation.z = 0.012 * Math.sin(0.55 * t + 0.6);
        md.sky.visible = above > 0.01;
        md.sea.visible = y > 250; md.rig.visible = y > 250;           // fully fogged out further down
        md.bop.visible = true;
        // dawn light (blended in as the camera breaks the surface)
        M.sun.dir.value.copy(sunDir); M.sun.col.value.copy(dawn.sun); M.sun.i.value = above; M.sun.sky.value.copy(dawn.sea);
        M.sky.top.value.copy(dawn.top); M.sky.hor.value.copy(dawn.hor); M.sky.low.value.copy(dawn.low); M.sky.disc.value = 1;
        const d0 = W3.lightDefaults;
        W3.key.color.copy(d0.keyCol).lerp(dawn.key, above); W3.key.intensity = lerp(d0.keyI, 2.6, above);
        W3.key.position.copy(d0.keyPos).lerp(sunDir.clone().multiplyScalar(120), above);
        W3.hemi.color.copy(d0.hemiSky).lerp(dawn.hemiSky, above); W3.hemi.groundColor.copy(d0.hemiGround).lerp(dawn.hemiGround, above);
        W3.hemi.intensity = lerp(d0.hemiI, 0.6, above);
        W3.scene.environmentIntensity = lerp(1, 0.3, above);
        W3.fill.color.copy(d0.fillCol).lerp(dawn.fill, above); W3.fill.intensity = lerp(d0.fillI, 0.45, above);
      },
    });

    // overlays
    const S = new Scene(B.start, tEnd + 1, { fade: 0.5, fadeOut: 0.01 });
    label3D(S, [0.47, 1.0, 0], '<b>Conductor</b><span class="sub">designed for the field life · never inspected</span>', { t0: c('10.2', 'back') + 0.3, t1: tU0, anchor: 'rm', dx: -150, dy: 120, color: COL.coral });
    label3D(S, [0.7, 2.4, 0], '<b>Template slot</b><span class="sub">designed for the field life · never inspected</span>', { t0: w('10.2', 'template') + 0.2, t1: tU0, anchor: 'rm', dx: -170, dy: -110, color: COL.coral });
    // three take-aways
    const take = [
      [w('10.2', 'number'), 'Put a number on the riser-connected time', COL.amber],
      [w('10.2', 'check'), 'Check the S-N data against the current DNV-RP-C203 edition', COL.cyan],
      [w('10.2', 'keep'), 'Keep monitoring the well (Annex J)', COL.green],
    ];
    const tOff = c('10.2', 'end') - 0.3;
    take.forEach(([t0, txt, col], i) => {
      const k = S.card(`<div style="display:flex;gap:18px;align-items:center"><span class="num" style="font-size:26px;color:${col}">${i + 1}</span><span style="font-size:30px;font-weight:650;color:var(--ink)">${txt}</span></div>`,
        { x: 120, y: 690 + i * 96, cls: 'glass' });
      k.el.style.padding = '16px 26px'; k.el.style.borderLeft = `4px solid ${col}`;
      k.in(t0, 0.6, 'left').out(tOff, 0.5);
    });
    // end card
    const tE = c('10.2', 'end');
    const shade = S.div('', { x: 0, y: 0, w: 1920, h: 1080, style: 'background:linear-gradient(90deg, rgba(4,12,20,0.86) 0%, rgba(4,12,20,0.66) 42%, rgba(4,12,20,0.0) 72%)' });
    shade.in(tE - 0.4, 1.2, 'none');
    S.div('Thanks for watching', { x: 120, y: 176, cls: 'h1' }).in(tE, 0.9, 'write');
    const bar = S.div('', { x: 124, y: 282, w: 520, h: 6, cls: 'bar' });
    bar.el.style.transformOrigin = '0 50%'; bar.set(0, { sx: 0, o: 0 }).set(tE + 0.2, { o: 1 }).to(tE + 0.2, 1.0, { sx: 1 }, ease.out3);
    S.div('SOURCES', { x: 124, y: 330, cls: 'kicker' }).in(tE + 1.0, 0.5, 'left');
    const src = [
      ['NORSOK U-001:2026', 'Subsea production systems · 13.3.6, Annex A (A.3.5), Annex B (B.2.6, B.4), Annex J'],
      ['DNV-RP-C203:2024', 'Fatigue design of offshore steel structures · S-N curves, SCFs, thickness effect'],
      ['NORSOK N-001', 'Integrity of offshore structures · design fatigue factors for the template'],
      ['DNV-RP-E104', 'Wellhead fatigue analysis · background to the local response method'],
    ];
    src.forEach(([a, d], i) => {
      S.div(`<div class="mono" style="font-size:21px;color:var(--cyan);font-weight:600">${a}</div><div class="small" style="font-size:21px;margin-top:2px">${d}</div>`, { x: 124, y: 378 + i * 88, w: 860 })
        .in(tE + 1.4 + i * 0.35, 0.5, 'left');
    });
    S.div('<span class="badge warn">The worked example uses illustrative teaching inputs, not project data</span>', { x: 124, y: 760 }).in(tE + 3.0, 0.5, 'pop');
    S.div('Every number in this video comes from the open model in this repository: model/fatigue_model.py', { x: 124, y: 834, w: 860, cls: 'tiny', style: 'letter-spacing:0.04em;text-transform:none;font-weight:550' }).in(tE + 3.4, 0.5);
    // fade to black at the very end
    const blk = S.div('', { x: 0, y: 0, w: 1920, h: 1080, style: 'background:#000' });
    blk.set(0, { o: 0 }).to(tEnd - 1.6, 1.4, { o: 1 }, ease.inOut);
  }
}
