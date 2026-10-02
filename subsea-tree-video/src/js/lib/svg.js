// Tiny SVG/DOM helpers -------------------------------------------------
export const NS = 'http://www.w3.org/2000/svg';

/** Create an SVG element: S('rect', {x:1,y:2}, child, child…). */
export function S(tag, attrs = {}, ...kids) {
  const el = document.createElementNS(NS, tag);
  for (const k in attrs) {
    const v = attrs[k];
    if (v === undefined || v === null || v === false) continue;
    if (k === 'style' && typeof v === 'object') Object.assign(el.style, v);
    else if (k === 'text') el.textContent = v;
    else el.setAttribute(k, v === true ? '' : String(v));
  }
  for (const c of kids.flat()) if (c) el.append(c);
  return el;
}

/** Create an HTML element: H('div', {class:'card', style:{…}}, 'text' | node …). */
export function H(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const k in attrs) {
    const v = attrs[k];
    if (v === undefined || v === null || v === false) continue;
    if (k === 'style' && typeof v === 'object') {
      for (const sk in v) {
        if (sk.startsWith('--')) el.style.setProperty(sk, v[sk]);
        else el.style[sk] = v[sk];
      }
    } else if (k === 'html') el.innerHTML = v;
    else if (k === 'text') el.textContent = v;
    else el.setAttribute(k, v === true ? '' : String(v));
  }
  for (const c of kids.flat()) if (c !== null && c !== undefined && c !== false) el.append(c);
  return el;
}

export const G = (attrs, ...kids) => S('g', attrs, ...kids);

/** Rounded polygon / path helpers */
export const pathD = (pts, close = false) =>
  pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(2) + ' ' + p[1].toFixed(2)).join(' ') + (close ? ' Z' : '');

/** Zig-zag/coil polyline between (x0,y0) and (x1,y1) – used for springs. */
export function coilD(x0, y0, x1, y1, turns, amp) {
  const pts = [[x0, y0]];
  const n = turns * 2;
  const dx = (x1 - x0) / (n + 1), dy = (y1 - y0) / (n + 1);
  const len = Math.hypot(x1 - x0, y1 - y0) || 1;
  const nx = -(y1 - y0) / len, ny = (x1 - x0) / len;
  for (let i = 1; i <= n; i++) {
    const s = i % 2 ? 1 : -1;
    pts.push([x0 + dx * i + nx * amp * s, y0 + dy * i + ny * amp * s]);
  }
  pts.push([x1, y1]);
  return pathD(pts);
}

/** Linear gradient helper → returns the id. */
export function linGrad(defs, id, stops, { x1 = 0, y1 = 0, x2 = 1, y2 = 0 } = {}) {
  if (defs.querySelector('#' + id)) return id;
  defs.append(
    S('linearGradient', { id, x1, y1, x2, y2 },
      stops.map(([o, c, a]) => S('stop', { offset: o, 'stop-color': c, 'stop-opacity': a ?? 1 })))
  );
  return id;
}
export function radGrad(defs, id, stops, { cx = 0.5, cy = 0.5, r = 0.5, fx, fy } = {}) {
  if (defs.querySelector('#' + id)) return id;
  defs.append(
    S('radialGradient', { id, cx, cy, r, fx, fy },
      stops.map(([o, c, a]) => S('stop', { offset: o, 'stop-color': c, 'stop-opacity': a ?? 1 })))
  );
  return id;
}

/** Deterministic PRNG (mulberry32) so particle fields look the same on every render. */
export function rng(seed = 1) {
  let a = seed >>> 0;
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const lerp = (a, b, t) => a + (b - a) * t;
export const smooth = (t) => t * t * (3 - 2 * t);
