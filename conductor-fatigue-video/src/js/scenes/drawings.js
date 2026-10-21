// 2D engineering drawings (SVG) shared by several chapters.
import { E, ease, COL, clamp, lerp, Actor } from '../engine/core.js';

// Weld toe close-up: two plates with a butt weld cap; a crack grows from the toe with beach marks.
// (x, y) = toe position; s = scale. Returns {g, crack(t0, t1)}
export function weldToe(S, x, y, { s = 1, t = 0 } = {}) {
  const g = S.g();
  g.baseTf = `translate(${x} ${y}) scale(${s})`;
  const P = (d, o) => S.path(d, { parent: g.el, o: 1, ...o });
  // plate (thickness 120 px) and weld cap
  P('M-420,0 L420,0 L420,140 L-420,140 Z', { fill: '#33475a', stroke: '#8fa7bb', width: 2 });
  P('M-110,0 C-70,-46 70,-46 110,0 Z', { fill: '#4a6176', stroke: '#c7d6e2', width: 2 });
  // fusion lines
  P('M-110,0 L-40,140', { stroke: 'rgba(200,220,240,0.35)', width: 2, dash: '6 6' });
  P('M110,0 L40,140', { stroke: 'rgba(200,220,240,0.35)', width: 2, dash: '6 6' });
  // toe marker
  const toe = S.circle(110, 0, 7, { fill: COL.coral, parent: g.el, o: 1 });
  // crack: grows down from the toe at (110, 0); beach marks as arcs
  const crack = S.path('M110,0 L114,30 L108,62 L116,96 L111,128', { stroke: COL.coral, width: 7, parent: g.el, o: 1 });
  crack.el.setAttribute('filter', 'url(#glow)');
  crack.set(0, { draw: 0 });
  const marks = [];
  for (let k = 1; k <= 5; k++) {
    const r = 24 * k;
    marks.push(S.path(`M${110 - r * 0.9},0 A${r},${r * 1.05} 0 0 0 ${110 + r * 0.9},0`, { stroke: 'rgba(255,140,120,0.7)', width: 2.5, parent: g.el, o: 0 }));
  }
  return {
    g, toe, crack, marks,
    grow(t0, t1) {
      crack.to(t0, t1 - t0, { draw: 1 }, ease.inOut);
      marks.forEach((m, i) => m.in(t0 + (t1 - t0) * (i + 1) / 6, 0.4, 'none'));
    },
  };
}

// helical spring between (x, y0) and (x, y1) — vertical
export function springPath(x, y0, y1, { coils = 7, w = 26 } = {}) {
  const n = coils * 2;
  const L = y1 - y0;
  let d = `M${x},${y0} L${x},${y0 + L * 0.12}`;
  for (let i = 0; i <= n; i++) {
    const yy = y0 + L * 0.12 + (L * 0.76) * i / n;
    const xx = x + (i === 0 || i === n ? 0 : (i % 2 ? w : -w));
    d += ` L${xx},${yy}`;
  }
  d += ` L${x},${y1}`;
  return d;
}

// ground hatch along a line
export function ground(S, x0, x1, y, { parent = null, o = 1 } = {}) {
  const g = S.g({ parent, o });
  S.line(x0, y, x1, y, { stroke: COL.ink2, width: 3, parent: g.el, o: 1 });
  for (let x = x0; x < x1; x += 18) S.line(x, y, x - 14, y + 16, { stroke: 'rgba(185,202,216,0.6)', width: 2, parent: g.el, o: 1 });
  return g;
}

// cross-section of a tube (ring) at (cx, cy) with outer radius R and wall t (px)
export function tubeSection(S, cx, cy, R, t, { fill = '#8fa3b5', stroke = '#d7e3ec', o = 0, parent = null } = {}) {
  const g = S.g({ o, parent });
  const d = `M${cx - R},${cy} a${R},${R} 0 1,0 ${2 * R},0 a${R},${R} 0 1,0 ${-2 * R},0 Z M${cx - R + t},${cy} a${R - t},${R - t} 0 1,1 ${2 * (R - t)},0 a${R - t},${R - t} 0 1,1 ${-2 * (R - t)},0 Z`;
  S.path(d, { fill, stroke, width: 2, parent: g.el, o: 1 }).el.setAttribute('fill-rule', 'evenodd');
  return g;
}
