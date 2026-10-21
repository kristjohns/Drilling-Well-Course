// Deterministic animation core: every visible property is a pure function of time t.
// Actors wrap DOM/SVG elements; their properties are keyframe tracks; E.seek(t) evaluates and writes them.

export const W = 1920, H = 1080;

// ------------------------------------------------------------------------------------------- easing
const c1 = 1.70158, c3 = c1 + 1;
export const ease = {
  linear: (x) => x,
  in: (x) => x * x,
  out: (x) => 1 - (1 - x) * (1 - x),
  inOut: (x) => (x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2),
  out3: (x) => 1 - Math.pow(1 - x, 3),
  inOut3: (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  out4: (x) => 1 - Math.pow(1 - x, 4),
  expo: (x) => (x === 1 ? 1 : 1 - Math.pow(2, -10 * x)),
  back: (x) => 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2),
  sine: (x) => -(Math.cos(Math.PI * x) - 1) / 2,
  elastic: (x) => (x === 0 || x === 1 ? x : Math.pow(2, -10 * x) * Math.sin((x * 10 - 0.75) * ((2 * Math.PI) / 3)) + 1),
};
export const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const lerp = (a, b, u) => a + (b - a) * u;
export const ramp = (t, t0, t1, e = ease.inOut) => (t <= t0 ? 0 : t >= t1 ? 1 : e((t - t0) / (t1 - t0)));
export const smooth = (t, t0, t1) => ramp(t, t0, t1, ease.inOut3);

// ------------------------------------------------------------------------------------------- tracks
// A track holds segments {t0, t1, v1, e}; the value before the first segment is `init`.
// A segment starts from whatever value the track has at its t0 (later segments take over).
export class Track {
  constructor(init) { this.init = init; this.segs = []; this.ready = false; }
  add(t0, d, v1, e = ease.inOut) { this.segs.push({ t0, t1: t0 + Math.max(d, 1e-6), v1, e }); this.ready = false; return this; }
  set(t0, v) { return this.add(t0, 1e-6, v, ease.linear); }
  prep() {
    this.segs.sort((a, b) => a.t0 - b.t0);
    let v = this.init;
    for (let i = 0; i < this.segs.length; i++) {
      const s = this.segs[i];
      // value at s.t0 given previous segment (which may still be running)
      const p = this.segs[i - 1];
      if (p) v = p.t1 <= s.t0 ? p.v1 : mix(p.v0, p.v1, p.e((s.t0 - p.t0) / (p.t1 - p.t0)));
      s.v0 = v;
    }
    this.ready = true;
  }
  at(t) {
    if (!this.ready) this.prep();
    const s = this.segs;
    if (!s.length || t < s[0].t0) return this.init;
    let lo = 0, hi = s.length - 1;
    while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (s[mid].t0 <= t) lo = mid; else hi = mid - 1; }
    const g = s[lo];
    if (t >= g.t1) return g.v1;
    return mix(g.v0, g.v1, g.e((t - g.t0) / (g.t1 - g.t0)));
  }
}
function mix(a, b, u) {
  if (typeof a === 'number') return a + (b - a) * u;
  if (Array.isArray(a)) return a.map((x, i) => x + (b[i] - x) * u);
  return u < 0.5 ? a : b;
}

// ------------------------------------------------------------------------------------------- actors
const DEF = { o: 1, x: 0, y: 0, s: 1, sx: 1, sy: 1, r: 0, clip: 1, clipY: 1, blur: 0 };
export class Actor {
  constructor(el, init = {}) {
    this.el = el; this.tr = {}; this.init = { ...DEF, ...init }; this.last = {};
    this.isSvg = el instanceof SVGElement;
    this.custom = [];
  }
  T(k) { if (!this.tr[k]) this.tr[k] = new Track(this.init[k] ?? DEF[k] ?? 0); return this.tr[k]; }
  // keyframe helpers ------------------------------------------------------------------------
  to(t0, d, props, e = ease.inOut) { for (const k in props) this.T(k).add(t0, d, props[k], e); return this; }
  set(t0, props) { for (const k in props) this.T(k).set(t0, props[k]); return this; }
  in(t0, d = 0.6, how = 'rise', e = ease.out3) {
    const o = this.T('o');
    if (!o.segs.length) o.init = 0;
    o.add(t0, d, 1, e);
    const from = (k, off) => {           // offset entrance, only if the track has no earlier keys
      const tr = this.T(k), base = this.init[k] ?? DEF[k];
      if (!tr.segs.length) tr.init = base + off;
      tr.add(t0, d, base, e);
    };
    if (how === 'rise') from('y', 26);
    else if (how === 'drop') from('y', -26);
    else if (how === 'left') from('x', -40);
    else if (how === 'right') from('x', 40);
    else if (how === 'pop') { const tr = this.T('s'); if (!tr.segs.length) tr.init = 0.6; tr.add(t0, d, 1, ease.back); }
    else if (how === 'zoom') { const tr = this.T('s'); if (!tr.segs.length) tr.init = 1.12; tr.add(t0, d, 1, e); }
    else if (how === 'write') { const tr = this.T('clip'); if (!tr.segs.length) tr.init = 0; tr.add(t0, d * 1.6, 1, ease.inOut); }
    else if (how === 'wipe') { const tr = this.T('clipY'); if (!tr.segs.length) tr.init = 0; tr.add(t0, d * 1.4, 1, ease.inOut); }
    return this;
  }
  out(t0, d = 0.45, e = ease.inOut) { this.T('o').add(t0, d, 0, e); return this; }
  // pulse a scale accent (e.g. when a value is mentioned)
  pulse(t0, amt = 0.08, d = 0.5) { const s = this.T('s'); s.add(t0, d * 0.4, 1 + amt, ease.out); s.add(t0 + d * 0.4, d * 0.6, 1, ease.inOut); return this; }
  // called every frame -----------------------------------------------------------------------
  apply(t) {
    const v = {};
    for (const k in this.tr) v[k] = this.tr[k].at(t);
    const o = v.o ?? this.init.o;
    const st = this.el.style;
    if (o !== this.last.o) {
      st.opacity = o.toFixed(4);
      st.visibility = o <= 0.001 ? 'hidden' : 'visible';
      this.last.o = o;
    }
    if (o <= 0.001) return;
    const x = v.x ?? this.init.x, y = v.y ?? this.init.y, s = v.s ?? this.init.s, r = v.r ?? this.init.r;
    const sx = (v.sx ?? this.init.sx) * s, sy = (v.sy ?? this.init.sy) * s;
    const key = `${x.toFixed(2)},${y.toFixed(2)},${sx.toFixed(4)},${sy.toFixed(4)},${r.toFixed(3)}|${this.baseTf || ''}`;
    if (key !== this.last.tf) {
      if (this.isSvg) this.el.setAttribute('transform', `${this.baseTf || ''} translate(${x} ${y}) rotate(${r}) scale(${sx} ${sy})`);
      else st.transform = `translate(${x}px, ${y}px) rotate(${r}deg) scale(${sx}, ${sy})`;
      this.last.tf = key;
    }
    if ('clip' in v || 'clipY' in v) {
      const c = v.clip ?? 1, cy = v.clipY ?? 1;
      const ck = c.toFixed(4) + cy.toFixed(4);
      if (ck !== this.last.clip) {
        st.clipPath = c >= 0.9999 && cy >= 0.9999 ? 'none' : `inset(${((1 - cy) * 100).toFixed(2)}% ${((1 - c) * 100).toFixed(2)}% 0 -2%)`;
        this.last.clip = ck;
      }
    }
    if ('blur' in v) {
      const b = v.blur;
      if (b !== this.last.blur) { st.filter = b > 0.01 ? `blur(${b.toFixed(2)}px)` : 'none'; this.last.blur = b; }
    }
    if ('draw' in v) {           // SVG stroke draw-on, 0..1
      const L = this.len ?? (this.len = this.el.getTotalLength ? this.el.getTotalLength() : 1000);
      const d = v.draw;
      if (d !== this.last.draw) {
        this.el.style.strokeDasharray = `${L} ${L}`;
        this.el.style.strokeDashoffset = `${(1 - d) * L}`;
        this.last.draw = d;
      }
    }
    if ('color' in v) {
      const c = v.color;
      const ck = c.join(',');
      if (ck !== this.last.color) { st.color = `rgb(${c[0] | 0},${c[1] | 0},${c[2] | 0})`; this.last.color = ck; }
    }
    if ('fill' in v) {
      const c = v.fill; const ck = c.join(',');
      if (ck !== this.last.fill) { this.el.setAttribute('fill', `rgb(${c[0] | 0},${c[1] | 0},${c[2] | 0})`); this.last.fill = ck; }
    }
    if ('stroke' in v) {
      const c = v.stroke; const ck = c.join(',');
      if (ck !== this.last.stroke) { this.el.setAttribute('stroke', `rgb(${c[0] | 0},${c[1] | 0},${c[2] | 0})`); this.last.stroke = ck; }
    }
    for (const f of this.custom) f(t, v);
  }
}

// ------------------------------------------------------------------------------------------- engine
export const E = {
  t: 0, scenes: [], animators: [], world: null, data: {}, T: null,
  root: null, layer: null, hud: null,
  seek(t) {
    this.t = t;
    // animators first: they may set inputs (e.g. baseTf) that the actors write out in the same frame
    for (const a of this.animators) if (t >= a.t0 - 1e-9 && t <= a.t1 + 1e-9) a.fn(t);
    for (const sc of this.scenes) sc.apply(t);
    if (this.world) this.world.render(t);
  },
  anim(t0, t1, fn) { this.animators.push({ t0, t1, fn }); },
};

export function hexRGB(h) {
  h = h.replace('#', '');
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}
export const COL = {
  ink: '#e9f2f9', ink2: '#b9cad8', dim: '#7f97aa', amber: '#ffb547', coral: '#ff6f61', cyan: '#4fd1ff', violet: '#b794f6',
  green: '#46d39a', red: '#ff4d5e', yellow: '#f2c14e', lemon: '#ffe66d', steel: '#b8c7d4', soil: '#c9a46c', cement: '#a7b1b9', blue: '#5aa9ff',
  line: 'rgba(190,220,245,0.16)',
};

// number formatting: 7472771 -> "7 472 771" (thin spaces), decimals with "."
export function fmt(x, d = 0) {
  if (x === null || x === undefined || !isFinite(x)) return '∞';
  const s = Math.abs(x).toFixed(d);
  const [i, f] = s.split('.');
  const g = i.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  return (x < 0 ? '−' : '') + g + (f ? '.' + f : '');
}
export function sci(x, d = 2) {
  if (!isFinite(x)) return '∞';
  const e = Math.floor(Math.log10(Math.abs(x)));
  const m = x / Math.pow(10, e);
  return `${m.toFixed(d)}×10<sup>${e}</sup>`;
}
export function sciTex(x, d = 2) {
  if (!isFinite(x)) return '\\infty';
  const e = Math.floor(Math.log10(Math.abs(x)));
  const m = x / Math.pow(10, e);
  return `${m.toFixed(d)}\\times10^{${e}}`;
}
