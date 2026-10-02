// Host facilities + subsea template glyphs (flat style) ------------------------------
import { S } from '../lib/svg.js';
import { animate } from '../engine.js';

const OUT = '#0B141C';

/** Semi-submersible platform. Origin = waterline centre. ~520w x 330h (above water). */
export function platform(parent, { scale = 1, flame = true, t0 = 0 } = {}) {
  const g = S('g', { transform: `scale(${scale})` });
  // submerged hull + columns
  g.append(
    S('rect', { x: -215, y: 70, width: 430, height: 42, rx: 21, fill: '#2B4254', stroke: OUT, 'stroke-width': 3 }),
    ...[-170, -56, 58, 160].map((x) => S('rect', { x, y: 0, width: 40, height: 74, fill: '#3B566B', stroke: OUT, 'stroke-width': 3 })),
    ...[-170, -56, 58, 160].map((x) => S('rect', { x, y: -64, width: 40, height: 66, fill: '#DCE6EE', stroke: OUT, 'stroke-width': 3 })),
    ...[-170, -56, 58, 160].map((x) => S('rect', { x, y: -40, width: 40, height: 12, fill: '#F2994A' })),
    // decks
    S('rect', { x: -240, y: -112, width: 480, height: 50, rx: 4, fill: '#C9D6E0', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: -240, y: -112, width: 480, height: 10, fill: '#F2994A' }),
    S('rect', { x: -212, y: -160, width: 112, height: 48, fill: '#E6EEF4', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: -66, y: -150, width: 130, height: 38, fill: '#E6EEF4', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: 112, y: -196, width: 104, height: 84, fill: '#F4F8FB', stroke: OUT, 'stroke-width': 3 }),
    ...[0, 1, 2, 3].flatMap((i) => [0, 1].map((j) => S('rect', { x: 124 + i * 22, y: -184 + j * 28, width: 14, height: 14, fill: '#2B4254' }))),
    // derrick
    S('path', { d: 'M-40 -150 L-14 -330 L12 -150 Z', fill: 'none', stroke: '#EEF4F9', 'stroke-width': 5, 'stroke-linejoin': 'round' }),
    S('path', { d: 'M-34 -190 H8 M-29 -230 H3 M-24 -270 H-2 M-40 -150 L8 -190 M12 -150 L-34 -190 M-34 -190 L3 -230 M8 -190 L-29 -230', fill: 'none', stroke: '#EEF4F9', 'stroke-width': 3 }),
    // flare boom
    S('path', { d: 'M-190 -160 L-262 -270', stroke: '#C9D6E0', 'stroke-width': 7, 'stroke-linecap': 'round' }),
    // crane
    S('path', { d: 'M196 -196 V-250 L120 -300', fill: 'none', stroke: '#F2994A', 'stroke-width': 8, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
  if (flame) {
    const fl = S('path', { d: 'M-262 -270 c-14 -10 -16 -30 0 -52 c4 14 22 22 14 52 z', fill: '#FF9A3C', stroke: 'none', style: { mixBlendMode: 'screen' } });
    const fl2 = S('path', { d: 'M-262 -272 c-7 -6 -8 -17 0 -28 c3 8 11 12 7 28 z', fill: '#FFE08A' });
    g.append(fl, fl2);
    animate(t0, 1e9, (t) => { const s = 0.85 + 0.2 * Math.sin(t * 9) + 0.1 * Math.sin(t * 17); fl.setAttribute('transform', `translate(-262 -270) scale(${s.toFixed(3)} ${(s * 1.1).toFixed(3)}) translate(262 270)`); fl2.setAttribute('transform', `translate(-262 -272) scale(${(s * 0.95).toFixed(3)}) translate(262 272)`); });
  }
  parent.append(g);
  return g;
}

/** FPSO. Origin = waterline, centred. ~660w x 330h. */
export function fpso(parent, { scale = 1, flame = true, t0 = 0 } = {}) {
  const g = S('g', { transform: `scale(${scale})` });
  g.append(
    // hull
    S('path', { d: 'M-320 -62 H270 L338 -18 L296 78 H-320 Z', fill: '#2B4254', stroke: OUT, 'stroke-width': 3 }),
    S('path', { d: 'M-320 -62 H270 L338 -18 L330 0 H-320 Z', fill: '#C0392B', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: -320, y: -62, width: 600, height: 12, fill: '#E5E9EC' }),
    // accommodation (stern)
    S('rect', { x: -310, y: -176, width: 104, height: 114, fill: '#F4F8FB', stroke: OUT, 'stroke-width': 3 }),
    ...[0, 1, 2, 3].flatMap((i) => [0, 1, 2].map((j) => S('rect', { x: -298 + i * 22, y: -164 + j * 28, width: 14, height: 14, fill: '#2B4254' }))),
    // process modules
    S('rect', { x: -190, y: -110, width: 110, height: 48, fill: '#C9D6E0', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: -66, y: -126, width: 90, height: 64, fill: '#E6EEF4', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: 40, y: -104, width: 120, height: 42, fill: '#C9D6E0', stroke: OUT, 'stroke-width': 3 }),
    ...[-150, -110, 80, 120].map((x) => S('rect', { x, y: -150, width: 18, height: 40, rx: 3, fill: '#9FB2C2', stroke: OUT, 'stroke-width': 2 })),
    S('path', { d: 'M-180 -62 V-132 M-120 -62 V-146', stroke: '#C9D6E0', 'stroke-width': 6 }),
    // flare tower at bow
    S('path', { d: 'M236 -62 L256 -300 L276 -62 Z', fill: 'none', stroke: '#EEF4F9', 'stroke-width': 5, 'stroke-linejoin': 'round' }),
    S('path', { d: 'M242 -130 H270 M247 -200 H265', stroke: '#EEF4F9', 'stroke-width': 3 }),
    // turret under bow + mooring lines
    S('rect', { x: 200, y: -62, width: 56, height: 142, fill: '#455C70', stroke: OUT, 'stroke-width': 3 }),
    S('path', { d: 'M228 80 L420 300 M228 80 L40 300', stroke: '#6F879A', 'stroke-width': 3, fill: 'none', 'stroke-dasharray': '10 8' }));
  if (flame) {
    const fl = S('path', { d: 'M256 -300 c-14 -10 -16 -30 0 -52 c4 14 22 22 14 52 z', fill: '#FF9A3C', style: { mixBlendMode: 'screen' } });
    g.append(fl);
    animate(t0, 1e9, (t) => { const s = 0.85 + 0.2 * Math.sin(t * 8.3) + 0.1 * Math.sin(t * 15); fl.setAttribute('transform', `translate(256 -300) scale(${s.toFixed(3)} ${(s * 1.1).toFixed(3)}) translate(-256 300)`); });
  }
  parent.append(g);
  return g;
}

/** Onshore gas plant. Origin = ground level, centred. ~560w x 330h. */
export function plant(parent, { scale = 1, flame = true, t0 = 0 } = {}) {
  const g = S('g', { transform: `scale(${scale})` });
  g.append(
    S('rect', { x: -300, y: 0, width: 600, height: 26, fill: '#3E5262' }),
    // tanks
    ...[-230, -140, -50].map((x) => S('g', {},
      S('rect', { x: x - 38, y: -110, width: 76, height: 110, fill: '#DCE6EE', stroke: OUT, 'stroke-width': 3 }),
      S('ellipse', { cx: x, cy: -110, rx: 38, ry: 12, fill: '#F4F8FB', stroke: OUT, 'stroke-width': 3 }))),
    // towers
    S('rect', { x: 20, y: -250, width: 30, height: 250, fill: '#C9D6E0', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: 78, y: -190, width: 24, height: 190, fill: '#DCE6EE', stroke: OUT, 'stroke-width': 3 }),
    ...[-210, -160, -110, -60].map((y) => S('rect', { x: 17, y, width: 36, height: 8, fill: '#8DA2B3' })),
    // buildings
    S('rect', { x: 130, y: -70, width: 110, height: 70, fill: '#E6EEF4', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: 150, y: -48, width: 20, height: 20, fill: '#2B4254' }), S('rect', { x: 196, y: -48, width: 20, height: 20, fill: '#2B4254' }),
    // pipe rack
    S('path', { d: 'M-280 -24 H260 M-280 -14 H260', stroke: '#8DA2B3', 'stroke-width': 5 }),
    // flare stack
    S('path', { d: 'M270 0 V-280', stroke: '#EEF4F9', 'stroke-width': 6 }));
  if (flame) {
    const fl = S('path', { d: 'M270 -280 c-14 -10 -16 -30 0 -52 c4 14 22 22 14 52 z', fill: '#FF9A3C', style: { mixBlendMode: 'screen' } });
    g.append(fl);
    animate(t0, 1e9, (t) => { const s = 0.85 + 0.2 * Math.sin(t * 7.7) + 0.1 * Math.sin(t * 13); fl.setAttribute('transform', `translate(270 -280) scale(${s.toFixed(3)} ${(s * 1.1).toFixed(3)}) translate(-270 280)`); });
  }
  parent.append(g);
  return g;
}

/** Mini tree glyph (for template views). Origin = base centre on the seabed. ~60w x 110h. */
export function miniTree(parent, { scale = 1 } = {}) {
  const g = S('g', { transform: `scale(${scale})` });
  g.append(
    S('rect', { x: -22, y: -26, width: 44, height: 26, rx: 5, fill: '#51677A', stroke: OUT, 'stroke-width': 2.5 }),
    S('rect', { x: -15, y: -88, width: 30, height: 64, rx: 5, fill: '#7F98AC', stroke: OUT, 'stroke-width': 2.5 }),
    S('rect', { x: -9, y: -100, width: 18, height: 14, rx: 5, fill: '#93A8B8', stroke: OUT, 'stroke-width': 2 }),
    S('rect', { x: -48, y: -72, width: 34, height: 11, rx: 3, fill: '#3F86C4', stroke: OUT, 'stroke-width': 2 }),
    S('rect', { x: 14, y: -52, width: 30, height: 10, rx: 3, fill: '#3F86C4', stroke: OUT, 'stroke-width': 2 }),
    S('path', { d: 'M15 -66 H58', stroke: '#6B8296', 'stroke-width': 7, 'stroke-linecap': 'round' }),
    S('path', { d: 'M-8 -104 q0 -14 8 -14 q8 0 8 14', fill: 'none', stroke: '#E5701A', 'stroke-width': 3.5 }));
  parent.append(g);
  return g;
}

/** Subsea template frame with n slots (trees added by caller). Origin = base centre on the seabed. */
export function templateFrame(parent, { w = 360, h = 150 } = {}) {
  const g = S('g');
  g.append(
    S('rect', { x: -w / 2, y: -10, width: w, height: 14, rx: 4, fill: '#33485A', stroke: OUT, 'stroke-width': 2.5 }),
    S('path', { d: `M${-w / 2 + 6} -8 V${-h} M${w / 2 - 6} -8 V${-h} M${-w / 2 + 6} ${-h} H${w / 2 - 6}`, fill: 'none', stroke: '#2E4152', 'stroke-width': 8, 'stroke-linecap': 'round' }),
    S('path', { d: `M${-w / 2 + 6} ${-h} L${-w / 2 + 6 + w * 0.22} -8 M${w / 2 - 6} ${-h} L${w / 2 - 6 - w * 0.22} -8`, fill: 'none', stroke: '#2E4152', 'stroke-width': 5 }));
  parent.append(g);
  return g;
}
