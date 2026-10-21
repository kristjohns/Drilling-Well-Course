// Reusable building blocks for the chapters.
import { E, ease, W, H, COL, fmt, clamp, Actor } from '../engine/core.js';
import { Scene, later, tex2html } from '../engine/scene.js';

// a NORSOK quote card: clause reference + quote text (with <span class="q"> highlights)
export function quoteCard(S, ref, html, { x = 120, y = 200, w = 760, t = 0, size = 30, cls = '' } = {}) {
  const c = S.card(`<div class="ref">${ref}</div><div class="quote" style="font-size:${size}px">${html}</div>`, { x, y, w, cls: 'glass ' + cls });
  if (t) c.in(t, 0.6, 'rise');
  return c;
}

// stacked derivation: [{tex, t, size, note, how}] placed top-down from y0; returns the Eq actors
export function derivation(S, steps, { x = 960, y0 = 260, gap = 110, align = 'center', size = 50, noteAbove = false } = {}) {
  const out = [];
  let y = y0;
  for (const s of steps) {
    const e = S.eq(s.tex, { x: s.x ?? x, y: s.y ?? y, size: s.size || size, align: s.align || align });
    if (s.t !== undefined) e.in(s.t, s.d || 0.7, s.how || 'write');
    if (s.note) {
      const above = s.noteAbove ?? noteAbove;
      const n = above
        ? S.div(s.note, { x: s.x ?? x, y: (s.y ?? y) - (s.size || size) * 0.95, cls: 'tiny', anchor: (s.align || align) === 'left' ? 'lb' : 'cb', style: 'letter-spacing:0.12em;text-transform:uppercase;color:#7f97aa' })
        : S.div(s.note, { x: s.noteX ?? 150, y: (s.y ?? y), cls: 'tiny', anchor: 'lm', style: 'letter-spacing:0.12em;text-transform:uppercase;color:#7f97aa' });
      if (s.t !== undefined) n.in(s.t, 0.5, 'left');
      // a tall equation (fractions, integrals) reaches above the default note line: lift the note clear of it and its box
      if (above) later(() => {
        const top = e.ay - e.h / 2, nh = n.el.offsetHeight;
        if (top - 6 < parseFloat(n.el.style.top) + nh) n.el.style.top = (top - 18 - nh) + 'px';
      });
      e.note = n;
    }
    out.push(e);
    y += s.gap || gap;
  }
  return out;
}

// HTML table: rows = array of arrays, head = array; returns {card, rows: [Actor]}
export function table(S, head, rows, { x, y, w = null, t = 0, stagger = 0.08, cls = '', title = '', colCls = [] } = {}) {
  const th = head.map((h, i) => `<th class="${colCls[i] || ''}">${h}</th>`).join('');
  const tr = rows.map((r, k) => `<tr data-k="${k}">${r.map((c, i) => `<td class="${colCls[i] || ''}">${c}</td>`).join('')}</tr>`).join('');
  const card = S.card(`${title ? `<div class="title">${title}</div>` : ''}<table class="t ${cls}"><thead><tr>${th}</tr></thead><tbody>${tr}</tbody></table>`, { x, y, w });
  const trs = [...card.el.querySelectorAll('tbody tr')].map((el) => S.track(new Actor(el, { o: t ? 0 : 1 })));
  if (t) { card.in(t, 0.5, 'rise'); trs.forEach((a, i) => a.in(t + 0.3 + i * stagger, 0.35, 'none')); }
  return { card, rows: trs, el: card.el };
}

// HTML label that follows a 3D world point during [t0, t1]
export function label3D(S, pos, html, { t0, t1, dx = 0, dy = 0, anchor = 'lm', cls = '', d = 0.5, line = true, color = COL.ink } = {}) {
  const lab = S.label(html, { x: 0, y: 0, cls });
  lab.in(t0, d, 'none'); lab.out(t1 - 0.4, 0.4);
  let dot = null, ln = null;
  if (line) {
    dot = S.circle(0, 0, 5, { fill: color }); dot.in(t0, d, 'none'); dot.out(t1 - 0.4, 0.4);
    ln = S.path('M0,0 L0,0', { stroke: color, width: 1.6, opacity: 0.75 }); ln.in(t0, d, 'none'); ln.out(t1 - 0.4, 0.4);
  }
  let wh = null;
  E.anim(t0 - 0.1, t1 + 0.1, (t) => {
    const p = E.world.project(typeof pos === 'function' ? pos(t) : pos, t);
    if (!wh) wh = [lab.el.offsetWidth, lab.el.offsetHeight];
    const lx = p.x + dx, ly = p.y + dy;
    const left = anchor[0] === 'l' ? lx + 12 : anchor[0] === 'r' ? lx - wh[0] - 12 : lx - wh[0] / 2;
    lab.el.style.left = left.toFixed(1) + 'px'; lab.el.style.top = (ly - wh[1] / 2).toFixed(1) + 'px';
    if (dot) { dot.el.setAttribute('cx', p.x.toFixed(1)); dot.el.setAttribute('cy', p.y.toFixed(1)); }
    if (ln) ln.el.setAttribute('d', `M${p.x.toFixed(1)},${p.y.toFixed(1)} L${(anchor[0] === 'l' ? lx + 12 : anchor[0] === 'r' ? lx - 12 : lx).toFixed(1)},${ly.toFixed(1)}`);
  });
  return lab;
}

// letter badge (contact areas) following a 3D point
export function letter3D(S, pos, ch, { t0, t1, color = COL.amber } = {}) {
  const b = S.div(ch, { x: 0, y: 0, cls: 'letter' });
  b.el.style.background = color;
  b.in(t0, 0.4, 'pop'); b.out(t1 - 0.3, 0.3);
  E.anim(t0 - 0.1, t1 + 0.1, (t) => { const p = E.world.project(pos, t); b.el.style.left = p.x.toFixed(1) + 'px'; b.el.style.top = p.y.toFixed(1) + 'px'; });
  return b;
}

// counter text that counts from a to b during [t0, t1]
export function counter(S, { x, y, a = 0, b, t0, t1, d = 0, fmtf = (v) => fmt(v, d), cls = 'num', size = 64, prefix = '', suffix = '', anchor = 'cm', color = COL.ink } = {}) {
  // laid out with the final value (so the anchored box fits it), then counts up inside that box
  const align = anchor[0] === 'l' ? 'left' : anchor[0] === 'r' ? 'right' : 'center';
  const el = S.div(prefix + fmtf(b) + suffix, { x, y, cls, anchor, style: `font-size:${size}px;color:${color};white-space:nowrap;text-align:${align}` });
  let last = null;
  E.anim(t0 - 3, t1 + 3600, (t) => {
    const u = ease.out3(clamp((t - t0) / (t1 - t0)));
    const v = a + (b - a) * u;
    const s = prefix + fmtf(v) + suffix;
    if (s !== last) { el.el.innerHTML = s; last = s; }
  });
  return el;
}

// big "PASS / FAIL" stamp
export function stamp(S, text, { x, y, t, kind = 'pass', size = 34 } = {}) {
  const b = S.div(text, { x, y, cls: 'badge ' + kind, anchor: 'cm', style: `font-size:${size}px;padding:12px 26px` });
  b.in(t, 0.45, 'pop');
  return b;
}

// tex inline in html strings
export const tx = (s) => tex2html(s, false);

// a simple bracket/brace under a horizontal span (svg)
export function brace(S, x0, x1, y, { color = COL.dim, h = 14, t = 0 } = {}) {
  const m = (x0 + x1) / 2;
  const p = S.path(`M${x0},${y} q0,${h} ${h},${h} L${m - h},${y + h} q${h},0 ${h},${h} q0,-${h} ${h},-${h} L${x1 - h},${y + h} q${h},0 ${h},-${h}`, { stroke: color, width: 2.5 });
  if (t) p.set(0, { draw: 0 }).to(t, 0.6, { draw: 1 }).in(t, 0.01, 'none');
  return p;
}
