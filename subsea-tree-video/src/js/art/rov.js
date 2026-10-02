// Simple work-class ROV (side view). Origin = body centre, facing right. ~240w x 130h.
import { S } from '../lib/svg.js';
const OUT = '#0B141C';
export function rov(parent, { scale = 1, lights = true } = {}) {
  const g = S('g', { transform: `scale(${scale})` });
  g.append(
    // skids
    S('path', { d: 'M-96 52 H92 M-70 52 V30 M60 52 V30', stroke: '#C9D6E0', 'stroke-width': 7, 'stroke-linecap': 'round', fill: 'none' }),
    // floatation (top)
    S('rect', { x: -88, y: -62, width: 176, height: 40, rx: 14, fill: '#F2994A', stroke: OUT, 'stroke-width': 3.5 }),
    S('rect', { x: -88, y: -62, width: 176, height: 10, rx: 5, fill: 'rgba(255,255,255,.35)' }),
    // frame/body
    S('rect', { x: -78, y: -24, width: 156, height: 62, rx: 10, fill: '#2E4152', stroke: OUT, 'stroke-width': 3.5 }),
    S('rect', { x: -60, y: -12, width: 56, height: 38, rx: 6, fill: '#0F1B25', stroke: '#51677A', 'stroke-width': 2 }),
    S('circle', { cx: 30, cy: 6, r: 14, fill: '#0F1B25', stroke: '#6F879A', 'stroke-width': 3 }),
    S('circle', { cx: 30, cy: 6, r: 5, fill: '#2ED0FF' }),
    // thrusters
    S('circle', { cx: -62, cy: -42, r: 15, fill: '#455C70', stroke: OUT, 'stroke-width': 3 }), S('circle', { cx: 62, cy: -42, r: 15, fill: '#455C70', stroke: OUT, 'stroke-width': 3 }),
    // manipulator arm
    S('path', { d: 'M78 18 L118 4 L142 30', stroke: OUT, 'stroke-width': 13, fill: 'none', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }),
    S('path', { d: 'M78 18 L118 4 L142 30', stroke: '#E5A22A', 'stroke-width': 8, fill: 'none', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }),
    S('path', { d: 'M142 30 l12 8 M142 30 l-2 14', stroke: '#C9D6E0', 'stroke-width': 5, 'stroke-linecap': 'round' }));
  if (lights) g.append(S('circle', { cx: 86, cy: -8, r: 9, fill: '#FFF6C9', stroke: OUT, 'stroke-width': 2 }));
  parent.append(g);
  return g;
}
