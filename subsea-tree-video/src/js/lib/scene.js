// Scene container helper ------------------------------------------------------------
import { H, S } from './svg.js';

export const BLUEPRINT =
  'repeating-linear-gradient(0deg, rgba(120,170,210,.045) 0 1px, transparent 1px 90px),' +
  'repeating-linear-gradient(90deg, rgba(120,170,210,.045) 0 1px, transparent 1px 90px),' +
  'radial-gradient(1400px 800px at 68% 28%, #0F3454 0%, #08192A 52%, #040C14 100%)';

/** A full-screen scene container visible during [t0-pad, t1+pad] with cross-fades. */
export function makeScene(root, E, id, { t0, t1, fi = 0.6, fo = 0.6, pad = 0.35, bg = BLUEPRINT, svg = true } = {}) {
  const sc = E.T.scene(id);
  const a = (t0 ?? sc.start) - pad, b = (t1 ?? sc.end) + pad;
  const el = H('div', { class: 'scene', id: 'scene-' + id, style: bg ? { background: bg } : {} });
  root.append(el);
  E.window_(el, Math.max(0, a), b, { fi, fo });
  const s = svg ? S('svg', { viewBox: '0 0 1920 1080' }) : null;
  if (s) el.append(s);
  return { el, svg: s, sc };
}

/** Small inline SVG icon for HTML cards. */
export function iconSvg(group, size = 64, vb = 90) {
  const s = S('svg', { viewBox: `${-vb} ${-vb} ${vb * 2} ${vb * 2}`, width: size, height: size, style: { display: 'block', overflow: 'visible' } });
  s.append(group);
  return s;
}
