// Scene 1 – Cold open (0 – 31 s) ---------------------------------------------
import { H, S, rng } from '../lib/svg.js';
import { installDefs } from '../art/defs.js';
import { buildTreeExterior } from '../art/treeExt.js';
import { marineSnow, beam } from '../lib/fx.js';
import { tag, leader, ring } from '../lib/annot.js';

export function build(root, E) {
  const { T, A, tl, show, hide, fadeIn, fadeOut, window_, tweenNumber, Cam, proj, sfx, animate, gsap } = E;
  installDefs();
  const sc = T.scene('intro');
  const el = H('div', { class: 'scene' });
  root.append(el);
  window_(el, 0, sc.end, { fi: 1.4, fo: 0.9 });
  const svg = S('svg', { viewBox: '0 0 1920 1080' });
  el.append(svg);

  /* ---- water column: surface -> deep ------------------------------------ */
  const defs = S('defs', {},
    S('linearGradient', { id: 'gIntroSurf', x1: 0, y1: 0, x2: 0, y2: 1 },
      S('stop', { offset: 0, 'stop-color': '#9ADCF5' }), S('stop', { offset: 0.35, 'stop-color': '#2A86B8' }), S('stop', { offset: 1, 'stop-color': '#08405F' })),
    S('linearGradient', { id: 'gIntroDeep', x1: 0, y1: 0, x2: 0, y2: 1 },
      S('stop', { offset: 0, 'stop-color': '#04141F' }), S('stop', { offset: 0.6, 'stop-color': '#020B12' }), S('stop', { offset: 1, 'stop-color': '#010508' })));
  svg.append(defs);
  svg.append(S('rect', { width: 1920, height: 1080, fill: 'url(#gIntroDeep)' }));
  const surf = S('rect', { width: 1920, height: 1080, fill: 'url(#gIntroSurf)' });
  svg.append(surf);
  tl.to(surf, { opacity: 0, duration: 4.2, ease: 'power1.inOut' }, 0.9);
  // sun glow + shafts
  const sun = S('ellipse', { cx: 960, cy: -40, rx: 900, ry: 520, fill: 'url(#gGlowWarm)', opacity: 0.35, style: { mixBlendMode: 'screen' } });
  const shafts = S('g', { style: { mixBlendMode: 'screen' }, fill: '#DDF6FF' });
  [[260, 90, -260], [620, 70, -180], [980, 120, -100], [1340, 80, -20], [1640, 100, 80]].forEach(([x, w, sk], i) =>
    shafts.append(S('path', { d: `M${x} 0 h${w} L${x + w + sk} 1100 h${-w * 1.6} Z`, opacity: 0.06 + (i % 2) * 0.03 })));
  svg.append(sun, shafts);
  tl.to([sun, shafts], { opacity: 0, duration: 3.6, ease: 'power1.in' }, 1.2);

  /* ---- world: seabed + exterior tree ----------------------------------- */
  const world = S('g');
  svg.append(world);
  const cam = new Cam(world, { wx: 0, wy: -330, sx: 960, sy: 1560, k: 0.44 });
  const r = rng(11);
  world.append(
    S('rect', { x: -3000, y: 0, width: 6000, height: 2400, fill: 'url(#gSeabed)' }),
    S('path', { d: 'M-3000 0 H3000', stroke: '#31434F', 'stroke-width': 4 }));
  for (let i = 0; i < 46; i++) {
    const x = -1800 + r() * 3600, dy = 12 + r() * 200, rr = 6 + r() * 20;
    world.append(S('ellipse', { cx: x, cy: dy, rx: rr * 2.2, ry: rr * 0.7, fill: '#1B2830', opacity: 0.6 }));
  }
  world.append(S('ellipse', { cx: 0, cy: 12, rx: 760, ry: 40, fill: 'url(#gShadowE)' }));
  const tree = buildTreeExterior(world);

  /* ---- marine snow + beams ---------------------------------------------- */
  const snow = marineSnow(svg, { n: 170, seed: 5, ambient: 9, op: 0.55 });
  const beamA = beam(svg, 'bmA', { x: 120, y: -90, angle: 50, length: 1500, spread: 10, op: 0.5 });
  const beamB = beam(svg, 'bmB', { x: 1800, y: -90, angle: 131, length: 1500, spread: 9, op: 0.42 });
  gsap.set([beamA, beamB], { autoAlpha: 0 });
  const bt = T.start('intro.b1') + 5.6;
  tl.fromTo(beamA, { autoAlpha: 0 }, { autoAlpha: 1, duration: 1.6, ease: 'power2.out', immediateRender: false }, bt);
  tl.fromTo(beamB, { autoAlpha: 0 }, { autoAlpha: 1, duration: 1.6, ease: 'power2.out', immediateRender: false }, bt + 0.6);

  // darkness: vignette that is opened up by the lights
  const dark = H('div', { class: 'abs', style: { inset: 0, background: 'radial-gradient(ellipse 58% 62% at 50% 56%, rgba(1,5,9,0) 0%, rgba(1,5,9,.55) 55%, rgba(1,5,9,.94) 100%)', opacity: 0 } });
  el.append(dark);
  tl.to(dark, { opacity: 1, duration: 3.0, ease: 'power1.inOut' }, 2.0);
  tl.to(dark, { opacity: 0.5, duration: 2.2, ease: 'power1.inOut' }, T.start('intro.b5') - 0.2);

  /* ---- descent -------------------------------------------------------- */
  E.tweenNumber(0.6, 6.4, 0, 2600, (v) => (snow.state.d = v), 'power2.out');
  const depth = H('div', { class: 'abs', style: { left: '96px', top: '470px' } },
    H('div', { class: 'kicker', text: 'DEPTH', style: { marginBottom: '6px' } }),
    H('div', { style: { display: 'flex', alignItems: 'baseline', gap: '10px' } },
      H('span', { class: 'mono', style: { font: '700 112px/1 var(--mono)', color: '#EEF4F9', letterSpacing: '-0.04em' }, text: '0' }),
      H('span', { style: { font: '600 40px var(--font)', color: '#AFC0CE' }, text: 'm' })));
  el.append(depth);
  const dnum = depth.querySelector('.mono');
  fadeIn(depth, 0.6, 0.8);
  E.tweenNumber(0.8, 4.2, 0, 300, (v) => (dnum.textContent = String(Math.round(v))), 'power2.inOut');
  fadeOut(depth, T.start('intro.b2') - 0.6, 0.6);

  /* ---- seabed rises, tree emerges --------------------------------------- */
  const S0 = cam.go(T.start('intro.b1') + 4.6, 4.2, { sy: 700 }, 'power3.out');        // seabed + tree rise into view
  const S1 = cam.go(T.start('intro.b2') - 0.3, 3.0, { wy: -430, sy: 560, k: 0.64, sx: 800 }, 'power2.inOut');     // tree left, pressure card right
  const S1b = cam.go(T.start('intro.b3') - 0.35, 1.3, { sx: 1190 }, 'power2.inOut');                                // tree right, icons left
  const S1c = cam.go(T.start('intro.b4') - 0.45, 1.3, { sx: 960 }, 'power2.inOut');                                 // centred for the four chips
  const S2 = cam.go(T.start('intro.b5') - 0.5, 2.0, { sx: 1350, k: 0.62 }, 'power3.inOut');

  /* ---- b2: pressure comparison ------------------------------------------- */
  const pc = S('g', { transform: 'translate(1380 250)' });
  const pcIn = S('g');
  pc.append(pcIn);
  svg.append(pc);
  pcIn.append(
    S('rect', { width: 420, height: 470, rx: 22, fill: 'rgba(8,26,42,.84)', stroke: 'rgba(170,200,225,.28)', 'stroke-width': 1.6 }),
    S('text', { x: 30, y: 50, fill: '#AFC0CE', 'font-size': 20, 'font-weight': 700, 'letter-spacing': '0.2em', text: 'PRESSURE' }));
  const baseY = 410;
  const seaBar = S('rect', { x: 62, y: baseY, width: 96, height: 0, rx: 6, fill: '#3C86D6' });
  const resBar = S('rect', { x: 250, y: baseY, width: 96, height: 0, rx: 6, fill: 'url(#gOrange)' });
  const zig = S('path', { d: 'M250 150 l12 -14 l12 14 l12 -14 l12 14 l12 -14 l12 14 l12 -14 Z', fill: '#FFB067', opacity: 0 });
  const sLab = S('text', { x: 110, y: 442, 'text-anchor': 'middle', fill: '#DCE6EE', 'font-size': 21, 'font-weight': 600, text: 'Seawater' });
  const sLab2 = S('text', { x: 110, y: 462, 'text-anchor': 'middle', fill: '#AFC0CE', 'font-size': 18, text: 'at 300 m' });
  const rLab = S('text', { x: 298, y: 442, 'text-anchor': 'middle', fill: '#DCE6EE', 'font-size': 21, 'font-weight': 600, text: 'Reservoir' });
  const sVal = S('text', { x: 110, y: 370, 'text-anchor': 'middle', fill: '#9FD0FF', 'font-size': 28, 'font-weight': 700, style: { fontFamily: 'var(--mono)' }, text: '≈ 30 bar', opacity: 0 });
  const rVal = S('text', { x: 298, y: 88, 'text-anchor': 'middle', fill: '#FFC27A', 'font-size': 27, 'font-weight': 700, style: { fontFamily: 'var(--mono)' }, text: 'hundreds', opacity: 0 });
  const rVal2 = S('text', { x: 298, y: 118, 'text-anchor': 'middle', fill: '#FFC27A', 'font-size': 27, 'font-weight': 700, style: { fontFamily: 'var(--mono)' }, text: 'of bar', opacity: 0 });
  pcIn.append(seaBar, resBar, zig, sLab, sLab2, rLab, sVal, rVal, rVal2);
  const b2 = 'intro.b2';
  show(pcIn, T.start(b2) - 0.1, 0.7, { x: 30, y: 0 });
  tl.fromTo(seaBar, { attr: { y: baseY, height: 0 } }, { attr: { y: baseY - 30, height: 30 }, duration: 0.7, ease: 'power3.out', immediateRender: true }, T.start(b2) + 0.2);
  tl.to(sVal, { opacity: 1, duration: 0.4 }, T.start(b2) + 0.7);
  tl.fromTo(resBar, { attr: { y: baseY, height: 0 } }, { attr: { y: baseY - 258, height: 258 }, duration: 1.5, ease: 'power3.in', immediateRender: true }, T.word(b2, 'hundreds') - 0.9);
  tl.to([rVal, rVal2, zig], { opacity: 1, duration: 0.35 }, T.word(b2, 'hundreds') + 0.5);
  hide(pcIn, T.start('intro.b3') + 0.3, 0.6);

  /* ---- b3: no people, no wheel, no lever --------------------------------- */
  const b3 = 'intro.b3';
  const icons = S('g');
  svg.append(icons);
  const icon = (cx, cy, drawFn) => {
    const wrap = S('g', { transform: `translate(${cx} ${cy})` });
    const g = S('g');
    wrap.append(g);
    const st = { fill: 'none', stroke: '#EEF4F9', 'stroke-width': 7, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' };
    g.append(S('circle', { r: 76, fill: 'rgba(8,26,42,.78)', stroke: 'rgba(170,200,225,.28)', 'stroke-width': 2 }));
    drawFn(g, st);
    const slash = S('g', { opacity: 0 }, S('circle', { r: 76, fill: 'none', stroke: '#FF3B5C', 'stroke-width': 8 }), S('line', { x1: -54, y1: -54, x2: 54, y2: 54, stroke: '#FF3B5C', 'stroke-width': 8, 'stroke-linecap': 'round' }));
    g.append(slash);
    icons.append(wrap);
    return { g, slash };
  };
  const person = icon(180, 400, (g, st) => g.append(S('circle', { ...st, cx: 0, cy: -30, r: 20 }), S('path', { ...st, d: 'M-42 44 Q-42 0 0 0 Q42 0 42 44' })));
  const wheel = icon(370, 400, (g, st) => g.append(S('circle', { ...st, r: 46 }), S('circle', { ...st, r: 9, fill: '#EEF4F9' }),
    ...[0, 45, 90, 135].map((a) => S('line', { ...st, x1: 0, y1: 0, x2: 0, y2: -46, transform: `rotate(${a}) ` })), ...[0, 45, 90, 135].map((a) => S('line', { ...st, x1: 0, y1: 0, x2: 0, y2: 46, transform: `rotate(${a})` }))));
  const lever = icon(560, 400, (g, st) => g.append(S('circle', { ...st, cx: -20, cy: 42, r: 13 }), S('line', { ...st, x1: -20, y1: 42, x2: 28, y2: -42 }), S('circle', { ...st, cx: 28, cy: -42, r: 14, fill: '#EEF4F9' })));
  const cap3 = H('div', { class: 'abs h3', style: { left: '96px', top: '520px', width: '640px', color: '#EEF4F9', fontSize: '40px' }, html: 'No hands. <span style="color:var(--ink2)">No wheels.</span> No levers.' });
  el.append(cap3);
  [[person, 'nobody'], [wheel, 'wheel'], [lever, 'lever']].forEach(([ic, w]) => {
    const tw = T.word(b3, w);
    show(ic.g, tw - 0.15, 0.5, { y: 24 });
    tl.fromTo(ic.slash, { opacity: 0, scale: 0.7, svgOrigin: '0 0' }, { opacity: 1, scale: 1, duration: 0.35, ease: 'back.out(2)', immediateRender: true }, tw + 0.55);
  });
  show(cap3, T.word(b3, 'nobody') + 0.4, 0.6);
  [person.g, wheel.g, lever.g, cap3].forEach((x) => hide(x, T.end(b3) + 0.55, 0.6));

  /* ---- b4: four capabilities --------------------------------------------- */
  const b4 = 'intro.b4';
  const lay = S('g');
  svg.append(lay);
  const P = (wx, wy) => proj(S1c, wx, wy);
  const chips = [
    { w: 'opens', text: 'OPENS & CLOSES', target: P(-230, -580), at: [520, 300], anchor: 'r', col: '#2ED0FF', ringAt: P(-230, -580) },
    { w: 'measures', text: 'MEASURES', target: P(357, -254), at: [1500, 760], anchor: 'l', col: '#FFC857', ringAt: P(357, -254) },
    { w: 'injects', text: 'INJECTS CHEMICALS', target: P(-640, -470), at: [520, 720], anchor: 'r', col: '#BC8FFF', ringAt: P(-640, -470) },
    { w: 'shuts', text: 'SHUTS THE WELL IN', target: P(0, -400), at: [1500, 300], anchor: 'l', col: '#FF3B5C', ringAt: P(0, -400) },
  ];
  chips.forEach((c, i) => {
    const g = S('g');
    lay.append(g);
    const ld = leader(g, c.target, c.at, { color: c.col, elbow: [c.at[0] + (c.anchor === 'l' ? -60 : 60), c.at[1]] });
    const tg = tag(g, { x: c.at[0], y: c.at[1], text: c.text, accent: c.col, anchor: c.anchor, size: 28, mono: true });
    const rg = ring(g, c.ringAt[0], c.ringAt[1], { r: 38, color: c.col, t0: T.word(b4, c.w), t1: T.end(b4) + 1 });
    const t0 = T.word(b4, c.w) - 0.1;
    show(g, t0, 0.5, { y: 14 });
    tl.fromTo(rg, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: true }, t0);
    hide(g, T.end(b4) + 0.15, 0.5);
    sfx(t0, 'tick', 0.6);
  });

  /* ---- b5/b6: title ------------------------------------------------------- */
  const title = H('div', { class: 'abs', style: { left: '96px', top: '300px', width: '760px' } },
    H('div', { class: 'kicker', style: { color: '#FFC857', marginBottom: '22px' }, text: 'Drilling & Well · Subsea' }),
    H('div', { class: 'h1', style: { fontSize: '100px', lineHeight: '1.0' }, html: 'The Subsea<br>Christmas Tree' }),
    H('div', { class: 'lead', style: { marginTop: '34px', fontSize: '38px', color: '#DCE6EE' }, text: 'How it works' }),
    H('div', { class: 'body', style: { marginTop: '14px', fontSize: '26px', color: '#7F97AA', width: '620px', lineHeight: '1.35' }, text: 'Valves, barriers and control on the Norwegian Continental Shelf' }));
  el.append(title);
  show(title, T.start('intro.b5') - 0.1, 1.0, { x: -40, y: 0, ease: 'power3.out' });
  sfx(T.start('intro.b5') - 0.1, 'whoosh', 0.8);
  hide(title, sc.end - 1.4, 0.9, { x: -30 });
  tl.to(dark, { opacity: 1, duration: 1.4, ease: 'power1.in' }, sc.end - 1.4);
  sfx(0.9, 'ping', 0.5);
  sfx(T.start('intro.b1') + 5.4, 'thud', 0.6);
}
