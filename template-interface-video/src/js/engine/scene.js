// Scenes: a container shown in [t0, t1] with factories for text, cards, KaTeX equations, SVG and charts.
import katex from 'katex';
import { Actor, E, ease, W, H, COL, hexRGB, fmt } from './core.js';

const NS = 'http://www.w3.org/2000/svg';

export const MACROS = {
  '\\p': '\\htmlClass{p-#1}{#2}',
  '\\cm': '\\htmlClass{v-mom}{#1}',
  '\\cs': '\\htmlClass{v-str}{#1}',
  '\\cn': '\\htmlClass{v-cyc}{#1}',
  '\\cv': '\\htmlClass{v-slope}{#1}',
  '\\cg': '\\htmlClass{v-df}{#1}',
  '\\cy': '\\htmlClass{v-k}{#1}',
  '\\cb': '\\htmlClass{v-geo}{#1}',
  '\\DM': '\\htmlClass{v-mom}{\\Delta M}',
  '\\Ds': '\\htmlClass{v-str}{\\Delta\\sigma}',
  '\\abar': '\\bar{a}',
  '\\dd': '\\mathrm{d}',
  '\\lg': '\\log',
};

export function tex2html(tex, display = false) {
  return katex.renderToString(tex, { displayMode: display, throwOnError: false, trust: true, strict: 'ignore', macros: { ...MACROS } });
}

const layoutQueue = [];
export function later(fn) { layoutQueue.push(fn); }
export function runLayout() { for (const f of layoutQueue) f(); layoutQueue.length = 0; }

function stageRect(el) {
  const r = el.getBoundingClientRect();
  const s = E.stageScale || 1;
  const o = E.root.getBoundingClientRect();
  return { x: (r.left - o.left) / s, y: (r.top - o.top) / s, w: r.width / s, h: r.height / s };
}

export class Scene {
  constructor(t0, t1, { fade = 0.5, fadeOut = null, parent = null, z = 0 } = {}) {
    this.t0 = t0; this.t1 = t1;
    this.el = document.createElement('div');
    this.el.className = 'scene';
    if (z) this.el.style.zIndex = z;
    (parent || E.layer).appendChild(this.el);
    this.actor = new Actor(this.el, { o: 0 });
    this.actor.T('o').add(t0 - 0.001, fade, 1, ease.inOut);
    this.actor.T('o').add(t1 - (fadeOut ?? fade), fadeOut ?? fade, 0, ease.inOut);
    this.actors = [];
    this._svg = null;
    E.scenes.push(this);
  }
  apply(t) {
    // active window includes the fades
    if (t < this.t0 - 0.05 || t > this.t1 + 0.05) {
      if (this.el.style.visibility !== 'hidden') { this.el.style.visibility = 'hidden'; this.el.style.opacity = '0'; this.actor.last = {}; }
      return;
    }
    this.actor.apply(t);
    if (this.actor.last.o <= 0.001) return;
    for (const a of this.actors) a.apply(t);
  }
  track(a) { this.actors.push(a); return a; }

  // ----------------------------------------------------------------------------- generic html
  div(html, { x = 0, y = 0, w = null, h = null, cls = '', style = '', o = 0, anchor = null, parent = null } = {}) {
    const el = document.createElement('div');
    el.className = 'abs ' + cls;
    el.innerHTML = html;
    el.style.cssText += `left:${x}px;top:${y}px;` + (w ? `width:${w}px;` : '') + (h ? `height:${h}px;` : '') + style;
    (parent || this.el).appendChild(el);
    const a = this.track(new Actor(el, { o }));
    if (anchor) {
      // centre/right anchored text without a width: measure at its natural width (not squeezed by the stage edge), then fix it
      const free = !w && anchor[0] !== 'l' && !/(^|;)\s*width\s*:/.test(style);
      if (free) { el.style.left = '0px'; el.style.whiteSpace = 'nowrap'; }      // its width is fixed after layout
      later(() => { if (free) el.style.width = (el.offsetWidth + 1) + 'px'; const r = { w: el.offsetWidth, h: el.offsetHeight }; place(el, x, y, r, anchor); });
    }
    return a;
  }
  text(html, opts = {}) { return this.div(html, { cls: opts.cls || 'body', ...opts }); }
  card(html, opts = {}) { return this.div(html, { ...opts, cls: 'card ' + (opts.cls || '') }); }
  pill(html, opts = {}) { return this.div(html, { ...opts, cls: 'pill ' + (opts.cls || '') }); }
  label(html, opts = {}) { return this.div(html, { ...opts, cls: 'label ' + (opts.cls || '') }); }

  // ----------------------------------------------------------------------------- equations
  eq(tex, { x = W / 2, y = H / 2, size = 56, align = 'center', cls = '', o = 0, display = true, color = null, parent = null } = {}) {
    const el = document.createElement('div');
    el.className = 'eq ' + cls;
    el.style.fontSize = size + 'px';
    if (color) el.style.color = color;
    el.innerHTML = tex2html(tex, display);
    el.style.left = x + 'px'; el.style.top = y + 'px';
    (parent || this.el).appendChild(el);
    const a = this.track(new Eq(el, { o }, this));
    a.ax = x; a.ay = y; a.align = align;
    later(() => a.layout());
    return a;
  }

  // ----------------------------------------------------------------------------- svg
  get svg() {
    if (!this._svg) {
      this._svg = document.createElementNS(NS, 'svg');
      this._svg.setAttribute('class', 'svg');
      this._svg.setAttribute('width', W); this._svg.setAttribute('height', H);
      this._svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
      this.el.appendChild(this._svg);
      this._svg.appendChild(document.createElementNS(NS, 'defs'));      // per-scene defs (chart clip paths)
    }
    return this._svg;
  }
  svgEl(tag, attrs = {}, { parent = null, o = 0 } = {}) {
    const el = document.createElementNS(NS, tag);
    for (const k in attrs) el.setAttribute(k, attrs[k]);
    (parent || this.svg).appendChild(el);
    return this.track(new Actor(el, { o }));
  }
  g({ o = 0, parent = null } = {}) { return this.svgEl('g', {}, { parent, o }); }
  path(d, { stroke = COL.ink, width = 3, fill = 'none', dash = null, cap = 'round', o = 0, parent = null, cls = '', marker = null, opacity = 1 } = {}) {
    const a = this.svgEl('path', { d, stroke, 'stroke-width': width, fill, 'stroke-linecap': cap, 'stroke-linejoin': 'round', class: cls, 'stroke-opacity': opacity }, { parent, o });
    if (dash) a.el.setAttribute('stroke-dasharray', dash);
    if (marker) a.el.setAttribute('marker-end', `url(#${marker})`);
    return a;
  }
  line(x1, y1, x2, y2, opts = {}) { return this.path(`M${x1},${y1} L${x2},${y2}`, opts); }
  arrow(x1, y1, x2, y2, { color = COL.ink, width = 4, head = 16, o = 0, parent = null, dash = null } = {}) {
    const g = this.g({ o, parent });
    const ang = Math.atan2(y2 - y1, x2 - x1);
    const bx = x2 - Math.cos(ang) * head * 0.8, by = y2 - Math.sin(ang) * head * 0.8;
    const shaft = this.path(`M${x1},${y1} L${bx},${by}`, { stroke: color, width, parent: g.el, o: 1, dash });
    const hx = (a) => x2 - Math.cos(ang + a) * head, hy = (a) => y2 - Math.sin(ang + a) * head;
    const tip = this.path(`M${hx(0.45)},${hy(0.45)} L${x2},${y2} L${hx(-0.45)},${hy(-0.45)} Z`, { stroke: color, width: 1, fill: color, parent: g.el, o: 1 });
    g.shaft = shaft; g.tip = tip;
    return g;
  }
  circle(cx, cy, r, { fill = COL.ink, stroke = 'none', width = 2, o = 0, parent = null } = {}) {
    return this.svgEl('circle', { cx, cy, r, fill, stroke, 'stroke-width': width }, { parent, o });
  }
  rect(x, y, w, h, { fill = 'none', stroke = COL.ink, width = 2, rx = 0, o = 0, parent = null, opacity = 1 } = {}) {
    return this.svgEl('rect', { x, y, width: w, height: h, rx, fill, stroke, 'stroke-width': width, 'fill-opacity': opacity }, { parent, o });
  }
  svgText(str, x, y, { size = 20, fill = COL.dim, anchor = 'middle', weight = 600, o = 0, parent = null, family = null } = {}) {
    const a = this.svgEl('text', { x, y, fill, 'font-size': size, 'text-anchor': anchor, 'font-weight': weight, 'dominant-baseline': 'middle' }, { parent, o });
    if (family) a.el.setAttribute('font-family', family);
    a.el.textContent = str;
    return a;
  }
  // a pointer label: dot at (px, py), leader to (lx, ly), label text there
  callout(px, py, lx, ly, html, { t = 0, color = COL.ink, side = 'auto', cls = '', d = 0.6 } = {}) {
    const dot = this.circle(px, py, 6, { fill: color });
    const ring = this.circle(px, py, 12, { fill: 'none', stroke: color, width: 2 });
    const ln = this.path(`M${px},${py} L${lx},${ly}`, { stroke: color, width: 2, opacity: 0.8 });
    const right = side === 'auto' ? lx >= px : side === 'right';
    const lab = this.label(html, { x: lx, y: ly, cls, anchor: right ? 'lm' : 'rm' });
    lab.el.style.marginLeft = right ? '10px' : '-10px';
    if (t) {
      dot.in(t, 0.3, 'pop'); ring.in(t, 0.3, 'pop');
      ln.set(t, { draw: 0 }).to(t, d, { draw: 1 }, ease.out3).in(t, 0.01, 'none');
      lab.in(t + d * 0.6, 0.45, right ? 'left' : 'right');
    }
    return { dot, ring, ln, lab, all: [dot, ring, ln, lab], out(t1, dd = 0.4) { for (const a of this.all) a.out(t1, dd); } };
  }

  // ----------------------------------------------------------------------------- charts
  chart(opts) { return new Chart(this, opts); }
}

// anchor codes: l/c/r + t/m/b (e.g. 'cm' = centre-middle)
function place(el, x, y, r, anchor) {
  const ax = anchor[0], ay = anchor[1] || 't';
  const left = ax === 'l' ? x : ax === 'c' ? x - r.w / 2 : x - r.w;
  const top = ay === 't' ? y : ay === 'm' ? y - r.h / 2 : y - r.h;
  el.style.left = left + 'px'; el.style.top = top + 'px';
}

export class Eq extends Actor {
  constructor(el, init, scene) { super(el, init); this.scene = scene; this.partActors = {}; }
  layout() {
    const w = this.el.offsetWidth, h = this.el.offsetHeight;
    this.w = w; this.h = h;
    const left = this.align === 'left' ? this.ax : this.align === 'right' ? this.ax - w : this.ax - w / 2;
    this.el.style.left = left + 'px';
    this.el.style.top = (this.ay - h / 2) + 'px';
    this.el.style.transformOrigin = this.align === 'left' ? '0 50%' : this.align === 'right' ? '100% 50%' : '50% 50%';
  }
  parts(name) { return [...this.el.querySelectorAll('.p-' + name)]; }
  // an Actor for a tagged sub-expression (its own opacity / colour / transform)
  P(name, init = {}) {
    if (this.partActors[name]) return this.partActors[name];
    const els = this.parts(name);
    if (!els.length) { console.warn('missing eq part', name); const d = document.createElement('span'); return new Actor(d); }
    els.forEach((e) => { e.style.display = 'inline-block'; });
    const a = new Actor(els[0], init);
    // apply to all elements with that class
    if (els.length > 1) {
      const extra = els.slice(1).map((e) => new Actor(e, init));
      const ap = a.apply.bind(a);
      a.apply = (t) => { ap(t); for (const x of extra) { x.tr = a.tr; x.apply(t); } };
    }
    this.scene.track(a);
    this.partActors[name] = a;
    return a;
  }
  // rect of a part relative to the stage, valid after layout (call inside later())
  rect(name) {
    const els = name ? this.parts(name) : [this.el];
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (const e of els) { const r = stageRect(e); x0 = Math.min(x0, r.x); y0 = Math.min(y0, r.y); x1 = Math.max(x1, r.x + r.w); y1 = Math.max(y1, r.y + r.h); }
    return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
  }
  // reveal tagged parts one after another
  build(names, t0, step = 0.5, d = 0.45, how = 'fade') {
    names.forEach((n, i) => {
      const p = this.P(n, { o: 0 });
      p.in(t0 + i * step, d, how === 'fade' ? 'none' : how);
    });
    return this;
  }
  // highlight box behind a part (created after layout)
  hl(name, t0, { d = 0.4, hold = null, color = COL.amber, pad = 8 } = {}) {
    later(() => {
      const r = this.rect(name);
      const box = this.scene.div('', { x: r.x - pad, y: r.y - pad, w: r.w + 2 * pad, h: r.h + 2 * pad, cls: 'hl' });
      box.el.style.borderColor = color;
      box.el.style.background = color + '26';
      box.in(t0, d, 'pop');
      if (hold !== null) box.out(t0 + hold, 0.4);
      this._hls = (this._hls || []).concat(box);
    });
    return this;
  }
  boxed(t0, { color = COL.amber, pad = 18, out = null } = {}) {
    later(() => {
      const r = this.rect();
      const b = this.scene.div('', { x: r.x - pad, y: r.y - pad * 0.7, w: r.w + 2 * pad, h: r.h + 1.4 * pad, cls: 'eqbox' });
      b.el.style.borderColor = color;
      b.el.style.boxShadow = `0 0 34px ${color}48`;
      b.in(t0, 0.5, 'zoom');
      if (out !== null) b.out(out, 0.4);
    });
    return this;
  }
}

// morph eq A into eq B (like "transform matching tex"): tagged parts present in both fly from A's layout to B's,
// A's other glyphs fade out, B's other glyphs fade in, then A is swapped for B. B must not be faded in by hand.
const isTagged = (el) => [...el.classList].some((c) => c.startsWith('p-'));
function untaggedLeaves(eq) {
  const out = [];
  const visit = (el) => {
    for (const c of el.children) {
      if (isTagged(c)) continue;
      if ([...c.querySelectorAll('*')].some(isTagged)) visit(c); else out.push(c);
    }
  };
  visit(eq.el.querySelector('.katex-html') || eq.el);
  return out;
}
function tagNames(eq) {
  const s = new Set();
  for (const e of eq.el.querySelectorAll('*')) for (const c of e.classList) if (c.startsWith('p-')) s.add(c.slice(2));
  return [...s];
}
export function morph(A, B, t0, d = 1.0, names = null) {
  later(() => {
    const keys = (names || tagNames(A)).filter((k) => B.parts(k).length && A.parts(k).length);
    const pa = {}, pb = {};
    for (const k of keys) { pa[k] = A.P(k); pb[k] = B.P(k); }
    const ra = {}, rb = {};
    for (const k of keys) { ra[k] = A.rect(k); rb[k] = B.rect(k); }
    // B: root visible from t0; its tagged parts appear when A's arrive; its other glyphs fade in late
    B.T('o').init = 0; B.T('o').set(t0, 1);
    for (const k of keys) { pb[k].T('o').init = 0; pb[k].T('o').set(t0 + d, 1); }
    for (const el of untaggedLeaves(B)) { const a = A.scene.track(new Actor(el, { o: 0 })); a.T('o').add(t0 + d * 0.45, d * 0.55, 1, ease.inOut); }
    for (const k of tagNames(B).filter((k) => !keys.includes(k))) { const p = B.P(k); p.T('o').init = 0; p.T('o').add(t0 + d * 0.45, d * 0.55, 1, ease.inOut); }
    // A: glyphs that do not travel fade out early; travelling parts move and scale; A disappears at the end
    for (const el of untaggedLeaves(A)) { const a = A.scene.track(new Actor(el)); a.T('o').add(t0, d * 0.4, 0, ease.out); }
    for (const k of tagNames(A).filter((k) => !keys.includes(k))) A.P(k).T('o').add(t0, d * 0.4, 0, ease.out);
    for (const k of keys) {
      const sc = rb[k].h / Math.max(ra[k].h, 1);
      pa[k].el.style.transformOrigin = '0 0';
      pa[k].to(t0, d, { x: rb[k].x - ra[k].x, y: rb[k].y - ra[k].y, s: sc }, ease.inOut3);
    }
    A.T('o').set(t0 + d, 0);
  });
}

// ------------------------------------------------------------------------------------------- charts
export class Chart {
  constructor(S, { x, y, w, h, xlog = false, ylog = false, xmin, xmax, ymin, ymax, xticks = [], yticks = [], xfmt = null, yfmt = null,
    xlabel = '', ylabel = '', ylabelDx = 76, grid = true, o = 0, title = '' }) {
    Object.assign(this, { S, x, y, w, h, xlog, ylog, xmin, xmax, ymin, ymax });
    this.g = S.g({ o });
    this.xticks = xticks; this.yticks = yticks;
    const cid = 'clip' + Math.random().toString(36).slice(2, 9);
    const cp = document.createElementNS(NS, 'clipPath'); cp.setAttribute('id', cid);
    const cr = document.createElementNS(NS, 'rect'); cr.setAttribute('x', x); cr.setAttribute('y', y - 2); cr.setAttribute('width', w + 2); cr.setAttribute('height', h + 2);
    cp.appendChild(cr); S.svg.querySelector('defs').appendChild(cp);
    this.plot = document.createElementNS(NS, 'g'); this.plot.setAttribute('clip-path', `url(#${cid})`);
    const X = (v) => this.X(v), Y = (v) => this.Y(v);
    // grid + axes
    this.axisParts = [];
    if (grid) {
      for (const tv of xticks) this.axisParts.push(S.line(X(tv), y, X(tv), y + h, { stroke: 'rgba(190,220,245,0.09)', width: 1, parent: this.g.el, o: 1 }));
      for (const tv of yticks) this.axisParts.push(S.line(x, Y(tv), x + w, Y(tv), { stroke: 'rgba(190,220,245,0.09)', width: 1, parent: this.g.el, o: 1 }));
    }
    this.ax = S.path(`M${x},${y} L${x},${y + h} L${x + w},${y + h}`, { stroke: 'rgba(200,225,245,0.55)', width: 2, parent: this.g.el, o: 1 });
    this.g.el.appendChild(this.plot);
    for (const tv of xticks) this.axisParts.push(S.svgText(xfmt ? xfmt(tv) : String(tv), X(tv), y + h + 26, { size: 18, parent: this.g.el, o: 1 }));
    for (const tv of yticks) this.axisParts.push(S.svgText(yfmt ? yfmt(tv) : String(tv), x - 14, Y(tv), { size: 18, anchor: 'end', parent: this.g.el, o: 1 }));
    if (xlabel) this.xl = S.div(xlabel, { x: x + w / 2, y: y + h + 50, cls: 'small', anchor: 'ct', o: 0 });
    if (ylabel) {
      this.yl = S.div(ylabel, { x: x - ylabelDx, y: y + h / 2, cls: 'small', anchor: 'cm', o: 0 });
      this.yl.init.r = -90;
    }
    if (title) this.tl = S.div(title, { x, y: y - 46, cls: 'small', style: 'font-weight:700;color:#b9cad8;letter-spacing:0.04em', o: 0 });
  }
  X(v) { const { x, w, xmin, xmax } = this; return this.xlog ? x + w * (Math.log10(v) - Math.log10(xmin)) / (Math.log10(xmax) - Math.log10(xmin)) : x + w * (v - xmin) / (xmax - xmin); }
  Y(v) { const { y, h, ymin, ymax } = this; return this.ylog ? y + h - h * (Math.log10(v) - Math.log10(ymin)) / (Math.log10(ymax) - Math.log10(ymin)) : y + h - h * (v - ymin) / (ymax - ymin); }
  show(t, d = 0.8) {
    this.g.in(t, d, 'none');
    this.ax.set(t, { draw: 0 }).to(t, d, { draw: 1 }, ease.out3);
    if (this.xl) this.xl.in(t + 0.2, 0.5);
    if (this.yl) this.yl.in(t + 0.2, 0.5);
    if (this.tl) this.tl.in(t, 0.5);
    return this;
  }
  hide(t, d = 0.5) { this.g.out(t, d); for (const a of [this.xl, this.yl, this.tl]) if (a) a.out(t, d); return this; }
  pathD(pts) { return pts.map(([a, b], i) => `${i ? 'L' : 'M'}${this.X(a).toFixed(2)},${this.Y(b).toFixed(2)}`).join(' '); }
  curve(pts, { color = COL.amber, width = 4, dash = null, t = null, d = 1.2, o = 1 } = {}) {
    const p = this.S.path(this.pathD(pts), { stroke: color, width, dash, parent: this.plot, o });
    // draw-on uses the dash array, so a dashed curve fades in instead
    if (t !== null) { if (dash) { p.T('o').init = 0; p.in(t, d, 'none'); } else { p.set(0, { draw: 0 }); p.to(t, d, { draw: 1 }, ease.inOut); } }
    return p;
  }
  dot(xv, yv, { color = COL.amber, r = 8, t = null, stroke = '#06121c' } = {}) {
    const c = this.S.circle(this.X(xv), this.Y(yv), r, { fill: color, stroke, width: 2, parent: this.plot, o: 0 });
    c.el.style.transformOrigin = `${this.X(xv)}px ${this.Y(yv)}px`;
    c.el.style.transformBox = 'view-box';
    if (t !== null) c.in(t, 0.35, 'none');
    return c;
  }
}

// Shared patterns and filters live in one always-visible svg at the start of the stage: a pattern defined inside a
// hidden scene would render its tiles hidden wherever it is referenced.
export function installGlobalDefs(root) {
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('width', '0'); svg.setAttribute('height', '0');
  svg.style.cssText = 'position:absolute;left:0;top:0;width:0;height:0;overflow:hidden';
  svg.innerHTML = `<defs>${MARKERS}</defs>`;
  root.insertBefore(svg, root.firstChild);
}

const MARKERS = `
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="10" stroke="rgba(220,235,250,0.35)" stroke-width="2"/></pattern>
<pattern id="soilpat" width="14" height="14" patternUnits="userSpaceOnUse"><rect width="14" height="14" fill="#6b5536"/><circle cx="3" cy="4" r="1.3" fill="#8a7048"/><circle cx="10" cy="10" r="1.1" fill="#7b6240"/></pattern>
<pattern id="cementpat" width="12" height="12" patternUnits="userSpaceOnUse"><rect width="12" height="12" fill="#7d878f"/><circle cx="4" cy="3" r="1" fill="#9aa4ab"/><circle cx="9" cy="8" r="1.2" fill="#6c757c"/></pattern>
`;
