// Reusable UI pieces: pressure gauge, banners -------------------------------------------
import { S, H } from './svg.js';
import { tl } from '../engine.js';

/** Round gauge in an SVG layer. value range [0,max]. Returns {g, to(t,d,value), show/hide via the engine}. */
export function gauge(parent, { x, y, r = 78, max = 250, label = 'HYDRAULIC SUPPLY', unit = 'bar', color = '#2ED0FF', v0 = 0, numeric = true, labelBg = false }) {
  const outer = S('g', { transform: `translate(${x} ${y})` });
  const g = S('g');
  outer.append(g);
  parent.append(outer);
  g.append(
    S('circle', { r: r + 14, fill: 'rgba(5,16,26,.9)', stroke: 'rgba(170,200,225,.35)', 'stroke-width': 2 }),
    S('circle', { r: r, fill: '#09151F', stroke: color, 'stroke-width': 3 }));
  const ang = (v) => -125 + 250 * (v / max);
  for (let i = 0; i <= 10; i++) {
    const a = ((-125 + 25 * i - 90) * Math.PI) / 180;
    g.append(S('line', { x1: Math.cos(a) * (r - 4), y1: Math.sin(a) * (r - 4), x2: Math.cos(a) * (r - (i % 5 === 0 ? 17 : 11)), y2: Math.sin(a) * (r - (i % 5 === 0 ? 17 : 11)), stroke: '#6F879A', 'stroke-width': i % 5 === 0 ? 3.5 : 2 }));
  }
  const arc = S('path', { d: '', fill: 'none', stroke: color, 'stroke-width': 7, 'stroke-linecap': 'round', opacity: 0.9 });
  const needle = S('g');
  needle.append(S('line', { x1: 0, y1: 8, x2: 0, y2: -(r - 20), stroke: '#EEF4F9', 'stroke-width': 4.5, 'stroke-linecap': 'round' }));
  const hub = S('circle', { r: 8, fill: '#EEF4F9' });
  const val = S('text', { x: 0, y: r * 0.55, 'text-anchor': 'middle', fill: '#EEF4F9', 'font-size': 26, 'font-weight': 700, style: { fontFamily: 'var(--mono)' }, text: '0' });
  const un = S('text', { x: 0, y: r * 0.55 + 22, 'text-anchor': 'middle', fill: '#9FB4C6', 'font-size': 16, 'font-weight': 600, text: unit });
  const lab = S('text', { x: 0, y: -r - 30, 'text-anchor': 'middle', fill: '#AFC0CE', 'font-size': 18, 'font-weight': 700, 'letter-spacing': '0.14em', text: label });
  g.append(arc, needle, hub, lab);
  if (labelBg) {   // dark pill behind the label, for gauges that sit on busy artwork
    const lw = lab.getComputedTextLength();
    g.insertBefore(S('rect', { x: -lw / 2 - 12, y: -r - 30 - 19, width: lw + 24, height: 30, rx: 9, fill: 'rgba(5,16,26,.88)' }), lab);
  }
  if (numeric) g.append(val, un);
  const api = {
    g, cur: v0,
    set(v) {
      needle.setAttribute('transform', `rotate(${ang(v).toFixed(2)})`);
      val.textContent = Math.round(v);
      const a0 = ((-125 - 90) * Math.PI) / 180, a1 = ((ang(v) - 90) * Math.PI) / 180;
      const rr = r - 1;
      const large = ang(v) + 125 > 180 ? 1 : 0;
      arc.setAttribute('d', v <= 0.5 ? '' : `M${Math.cos(a0) * rr} ${Math.sin(a0) * rr} A${rr} ${rr} 0 ${large} 1 ${Math.cos(a1) * rr} ${Math.sin(a1) * rr}`);
    },
    to(t, d, v, ease = 'power2.inOut') {
      const p = { v: api.cur };
      tl.fromTo(p, { v: api.cur }, { v, duration: Math.max(0.001, d), ease, onUpdate: () => api.set(p.v), immediateRender: false }, t);
      api.cur = v;
      return api;
    },
  };
  api.set(v0);
  return api;
}

/** Big banner text (HTML) */
export function banner(html, { text, color = '#EEF4F9', sub, top = 120, size = 54, left = 0, width = 1920, align = 'center', bg = true } = {}) {
  const el = H('div', { class: 'abs', style: { left: left + 'px', top: top + 'px', width: width + 'px', textAlign: align } },
    H('div', { style: { display: 'inline-block', padding: bg ? '14px 34px 16px' : '0', borderRadius: '18px', background: bg ? 'rgba(5,16,26,.88)' : 'transparent', border: bg ? `2px solid ${color}` : 'none', boxShadow: bg ? `0 0 40px ${color}33` : 'none', font: `800 ${size}px var(--font)`, color, letterSpacing: '-0.01em' }, html: text }),
    sub ? H('div', { style: { marginTop: '10px', font: '600 28px var(--font)', color: '#AFC0CE' }, text: sub }) : null);
  html.append(el);
  return el;
}
