// Simple line icons, centred on (0,0), nominal size 160 ---------------------------
import { S } from '../lib/svg.js';

const st = (c, w = 7) => ({ fill: 'none', stroke: c, 'stroke-width': w, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });

export const icons = {
  /** subsea template with four wells */
  template(c = '#EEF4F9') {
    return S('g', {},
      S('path', { ...st(c), d: 'M-76 40 H76 M-64 40 V10 H64 V40' }),
      ...[-44, -15, 15, 44].map((x) => S('path', { ...st(c, 6), d: `M${x} 10 V-30 M${x - 11} -30 h22 M${x} -30 V-52` })),
      S('path', { ...st(c, 5), d: 'M-76 62 H76', opacity: 0.5 }));
  },
  /** gate valve symbol with actuator */
  valve(c = '#EEF4F9') {
    return S('g', {},
      S('path', { ...st(c), d: 'M-70 14 L0 40 L-70 66 Z M70 14 L0 40 L70 66 Z' }),
      S('path', { ...st(c), d: 'M0 40 V-18 M-26 -18 H26 M-18 -18 V-62 H18 V-18' }));
  },
  /** hydraulic piston + spring (fail-safe) */
  spring(c = '#EEF4F9', c2 = '#FFC857') {
    return S('g', {},
      S('rect', { ...st(c, 6), x: -76, y: -34, width: 152, height: 68, rx: 8 }),
      S('path', { ...st(c2, 6), d: 'M-6 0 l8 -22 l12 44 l12 -44 l12 44 l12 -44 l8 22' }),
      S('path', { ...st(c, 8), d: 'M-34 -34 V34' }),
      S('path', { ...st(c, 6), d: 'M-76 0 H-100' }));
  },
  /** primary (blue) and secondary (red) barrier shields */
  shields(c1 = '#4A82FF', c2 = '#FF4F6D') {
    const sh = (s) => `M0 ${-80 * s} L${62 * s} ${-54 * s} V${6 * s} C${62 * s} ${44 * s} ${34 * s} ${68 * s} 0 ${82 * s} C${-34 * s} ${68 * s} ${-62 * s} ${44 * s} ${-62 * s} ${6 * s} V${-54 * s} Z`;
    return S('g', {}, S('path', { ...st(c2, 7), d: sh(1) }), S('path', { ...st(c1, 7), d: sh(0.62), transform: 'translate(0 10)' }));
  },
  /** map pin */
  pin(c = '#EEF4F9') {
    return S('g', {},
      S('path', { ...st(c), d: 'M0 70 C-34 28 -50 4 -50 -22 A50 50 0 0 1 50 -22 C50 4 34 28 0 70 Z' }),
      S('circle', { ...st(c), cx: 0, cy: -22, r: 16 }));
  },
  /** control the flow */
  flow(c = '#EEF4F9', c2 = '#FF9A3C') {
    return S('g', {},
      S('path', { ...st(c), d: 'M-80 -26 H80 M-80 26 H80' }),
      S('path', { ...st(c), d: 'M0 -76 V-30 M-30 -76 H30' }),
      S('path', { ...st(c), d: 'M-16 -26 L16 -26 L8 8 L-8 8 Z', fill: c, 'fill-opacity': 0.25 }),
      S('path', { ...st(c2, 6), d: 'M-62 -4 l12 8 l-12 8 M-36 -4 l12 8 l-12 8 M30 -4 l12 8 l-12 8 M56 -4 l12 8 l-12 8' }));
  },
  /** isolate: shield + padlock */
  shield(c = '#EEF4F9', c2 = '#FF3B5C') {
    return S('g', {},
      S('path', { ...st(c), d: 'M0 -82 L64 -56 V6 C64 44 34 68 0 84 C-34 68 -64 44 -64 6 V-56 Z' }),
      S('rect', { ...st(c2, 6), x: -20, y: -8, width: 40, height: 34, rx: 6, fill: c2, 'fill-opacity': 0.25 }),
      S('path', { ...st(c2, 6), d: 'M-12 -8 V-20 a12 12 0 0 1 24 0 V-8' }));
  },
  /** inject + measure: drop and gauge */
  inject(c = '#EEF4F9', c2 = '#BC8FFF') {
    return S('g', {},
      S('path', { ...st(c2, 6), d: 'M-36 -64 C-36 -64 -62 -26 -62 -6 a26 26 0 0 0 52 0 C-10 -26 -36 -64 -36 -64 Z', fill: c2, 'fill-opacity': 0.25 }),
      S('circle', { ...st(c, 6), cx: 38, cy: 26, r: 40 }),
      S('path', { ...st(c, 5), d: 'M38 26 L58 8 M38 -6 v8 M6 26 h8 M70 26 h-8' }),
      S('circle', { cx: 38, cy: 26, r: 6, fill: c }));
  },
  /** access: wireline tool in the bore */
  tool(c = '#EEF4F9', c2 = '#FFC857') {
    return S('g', {},
      S('path', { ...st(c), d: 'M-30 -80 V80 M30 -80 V80' }),
      S('path', { ...st(c2, 4), d: 'M0 -80 V-24' }),
      S('rect', { ...st(c2, 6), x: -14, y: -24, width: 28, height: 62, rx: 8, fill: c2, 'fill-opacity': 0.25 }),
      S('path', { ...st(c, 6), d: 'M-10 56 l10 12 l10 -12' }));
  },
};
