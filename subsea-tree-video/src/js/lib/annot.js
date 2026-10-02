// Annotation helpers (screen-space labels, leaders, rings) -------------------------
import { S, H } from './svg.js';
import { animate, tl } from '../engine.js';

const BG = 'rgba(5,16,26,.86)', BORDER = 'rgba(170,200,225,.34)';

/** Pill label. (x,y) = the anchor point; `anchor` says which side of the pill touches it. */
export function tag(parent, { x, y, text, sub, color = '#EEF4F9', accent = '#FFC857', anchor = 'l', size = 26, mono = false, minW = 0 }) {
  const outer = S('g', { transform: `translate(${x} ${y})` });
  const el = S('g');
  outer.append(el);
  parent.append(outer);
  const pad = 15;
  const t1 = S('text', { x: pad + 6, y: 0, fill: color, 'font-size': size, 'font-weight': mono ? 700 : 650, style: { fontFamily: mono ? 'var(--mono)' : 'var(--font)' }, 'letter-spacing': mono ? '0.03em' : '0' });
  t1.textContent = text;
  el.append(t1);
  let t2 = null;
  if (sub) {
    t2 = S('text', { x: pad + 6, y: 0, fill: '#AFC0CE', 'font-size': Math.round(size * 0.78), 'font-weight': 500 });
    t2.textContent = sub;
    el.append(t2);
  }
  const w1 = t1.getComputedTextLength();
  const w2 = t2 ? t2.getComputedTextLength() : 0;
  const w = Math.max(minW, Math.max(w1, w2) + pad * 2 + 8);
  const h = sub ? size * 2.15 + pad : size * 1.25 + pad;
  t1.setAttribute('y', (pad * 0.55 + size * 0.88).toFixed(1));
  if (t2) t2.setAttribute('y', (pad * 0.55 + size * 0.88 + size * 0.98).toFixed(1));
  const bg = S('rect', { x: 0, y: 0, width: w, height: h, rx: 11, fill: BG, stroke: BORDER, 'stroke-width': 1.6 });
  const bar = S('rect', { x: 0, y: 0, width: 5, height: h, rx: 2.5, fill: accent });
  el.prepend(bg);
  el.append(bar);
  // position so that the anchor touches the pill
  let ox = 0, oy = 0;
  if (anchor === 'l') { ox = 0; oy = -h / 2; }
  else if (anchor === 'r') { ox = -w; oy = -h / 2; }
  else if (anchor === 't') { ox = -w / 2; oy = 0; }
  else if (anchor === 'b') { ox = -w / 2; oy = -h; }
  else if (anchor === 'c') { ox = -w / 2; oy = -h / 2; }
  outer.setAttribute('transform', `translate(${x + ox} ${y + oy})`);
  return { el, w, h, x: x + ox, y: y + oy, outer };
}

/** Leader line from `from` (target, gets a dot) to `to` (label side). Optional elbow. */
export function leader(parent, from, to, { color = '#FFC857', dot = true, width = 2.4, elbow = null } = {}) {
  const pts = elbow ? [from, elbow, to] : [from, to];
  const d = pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' ');
  const g = S('g');
  g.append(S('path', { d, fill: 'none', stroke: color, 'stroke-width': width, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
  if (dot) g.append(S('circle', { cx: from[0], cy: from[1], r: 6.5, fill: '#06121C', stroke: color, 'stroke-width': 2.6 }), S('circle', { cx: from[0], cy: from[1], r: 2.6, fill: color }));
  parent.append(g);
  return g;
}

/** Label + leader in one: returns a group you can show/hide. */
export function callout(parent, { target, at, text, sub, color = '#FFC857', anchor = 'l', size = 26, mono = false, elbow = null }) {
  const g = S('g');
  parent.append(g);
  const ld = leader(g, target, at, { color, elbow });
  const tg = tag(g, { x: at[0], y: at[1], text, sub, accent: color, anchor, size, mono });
  return { g, tag: tg };
}

/** A pulsing ring around a screen point (animated by time, so deterministic). */
export function ring(parent, x, y, { r = 46, color = '#FFC857', w = 4, t0 = 0, t1 = 1e9, period = 1.2 } = {}) {
  const g = S('g', { opacity: 0 });
  const c1 = S('circle', { cx: x, cy: y, r, fill: 'none', stroke: color, 'stroke-width': w });
  const c2 = S('circle', { cx: x, cy: y, r, fill: 'none', stroke: color, 'stroke-width': 2, opacity: 0.5 });
  g.append(c1, c2);
  parent.append(g);
  animate(t0, t1, (t) => {
    const p = ((t - t0) / period) % 1;
    c2.setAttribute('r', (r + p * r * 0.9).toFixed(1));
    c2.setAttribute('opacity', (0.55 * (1 - p)).toFixed(2));
    c1.setAttribute('r', (r + Math.sin(p * Math.PI * 2) * 2).toFixed(1));
  });
  return g;
}

/** Rounded translucent panel (SVG) */
export function panel(parent, x, y, w, h, { r = 20, fill = 'rgba(8,26,42,.82)', stroke = 'rgba(170,200,225,.28)' } = {}) {
  const g = S('g', { transform: `translate(${x} ${y})` });
  const inner = S('g');
  inner.append(S('rect', { width: w, height: h, rx: r, fill, stroke, 'stroke-width': 1.6 }));
  g.append(inner);
  parent.append(g);
  return { outer: g, el: inner };
}
