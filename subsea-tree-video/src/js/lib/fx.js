// Atmosphere helpers: marine snow, light beams ---------------------------------
import { S, rng } from './svg.js';
import { animate } from '../engine.js';

/** Drifting particles. `state.d` (cumulative vertical displacement, px) can be tweened by the timeline. */
export function marineSnow(parent, { n = 140, w = 1920, h = 1080, seed = 7, ambient = 10, drift = 14, rMin = 0.8, rMax = 3.0, op = 0.5, t0 = 0, t1 = 1e9, color = '#CDEBFF' } = {}) {
  const r = rng(seed);
  const g = S('g', { fill: color });
  parent.append(g);
  const items = [];
  for (let i = 0; i < n; i++) {
    const rr = rMin + r() * (rMax - rMin);
    const c = S('circle', { r: rr.toFixed(2), opacity: (0.12 + r() * op).toFixed(2), cx: 0, cy: 0 });
    g.append(c);
    items.push({ c, x: r() * w, y: r() * h, s: 0.35 + r() * 0.95, ph: r() * 6.28 });
  }
  const state = { d: 0 };
  animate(t0, t1, (t) => {
    for (const it of items) {
      const y = (((it.y - (state.d + ambient * t) * it.s) % h) + h) % h;
      const x = it.x + Math.sin(t * 0.45 * it.s + it.ph) * drift;
      it.c.setAttribute('cx', x.toFixed(1));
      it.c.setAttribute('cy', y.toFixed(1));
    }
  });
  return { g, state };
}

/** Soft light cone (screen-blended). Returns the group. */
export function beam(parent, id, { x, y, angle = 90, length = 900, spread = 16, color = '#BFE9FF', op = 0.55 } = {}) {
  const a0 = ((angle - spread) * Math.PI) / 180, a1 = ((angle + spread) * Math.PI) / 180;
  const p1 = [x + Math.cos(a0) * length, y + Math.sin(a0) * length];
  const p2 = [x + Math.cos(a1) * length, y + Math.sin(a1) * length];
  const am = (angle * Math.PI) / 180;
  const defs = S('defs', {},
    S('linearGradient', { id, gradientUnits: 'userSpaceOnUse', x1: x, y1: y, x2: x + Math.cos(am) * length, y2: y + Math.sin(am) * length },
      S('stop', { offset: 0, 'stop-color': color, 'stop-opacity': op }), S('stop', { offset: 0.6, 'stop-color': color, 'stop-opacity': op * 0.25 }), S('stop', { offset: 1, 'stop-color': color, 'stop-opacity': 0 })));
  const g = S('g', { style: { mixBlendMode: 'screen' } }, defs,
    S('path', { d: `M${x} ${y} L${p1[0]} ${p1[1]} L${p2[0]} ${p2[1]} Z`, fill: `url(#${id})` }));
  parent.append(g);
  return g;
}
