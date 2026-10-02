// Deterministic animation engine --------------------------------------
// Everything on screen is a pure function of the global time t (seconds):
//   * GSAP timeline  -> tweens (paused; we seek it)
//   * animators      -> per-frame functions of t (flows, particles, pulses)
// so frames can be rendered in any order, on any number of workers.
import { gsap } from '/node_modules/gsap/index.js';
import { S, G, clamp } from './lib/svg.js';

gsap.defaults({ ease: 'power2.inOut' });
gsap.ticker.lagSmoothing(0);

export { gsap };
export const tl = gsap.timeline({ paused: true });

/* ---------- narration timings -------------------------------------- */
export const T = {
  data: null,
  dur: 0,
  sc: {},
  load(d) {
    this.data = d;
    this.dur = d.meta.duration;
    this.sc = {};
    d.scenes.forEach((s) => (this.sc[s.id] = s));
  },
  scene(id) {
    const s = this.sc[id];
    if (!s) throw new Error('Unknown scene ' + id);
    return s;
  },
  beat(path) {
    const [s, b] = path.split('.');
    const bt = this.scene(s).beats[b];
    if (!bt) throw new Error('Unknown beat ' + path);
    return bt;
  },
  start: (p) => T.beat(p).start,
  end: (p) => T.beat(p).end,
  /** time at fraction f (0..1) of a beat */
  frac: (p, f) => T.beat(p).start + T.beat(p).dur * f,
  /** start time of the nth word of a beat matching text `w` (case-insensitive substring) */
  word(path, w, n = 0) {
    const b = T.beat(path);
    const q = w.toLowerCase();
    const hits = b.words.filter((x) => x.w.toLowerCase().includes(q));
    if (hits.length <= n) throw new Error(`Word "${w}"#${n} not found in ${path}: ${b.text}`);
    return b.start + hits[n].s;
  },
  /** end time of a matching word */
  wordEnd(path, w, n = 0) {
    const b = T.beat(path);
    const q = w.toLowerCase();
    const hits = b.words.filter((x) => x.w.toLowerCase().includes(q));
    if (hits.length <= n) throw new Error(`Word "${w}"#${n} not found in ${path}: ${b.text}`);
    return b.start + hits[n].e;
  },
};

/* ---------- timeline sugar ----------------------------------------- */
export const A = {
  to: (t, target, vars) => tl.to(target, vars, t),
  fromTo: (t, target, from, to) => tl.fromTo(target, from, to, t),
  set: (t, target, vars) => tl.set(target, vars, t),
  call: (t, fn) => tl.call(fn, [], t),
};

const animators = [];
/** Run fn(t) every frame while t0 <= t <= t1. */
export function animate(t0, t1, fn) {
  animators.push({ t0, t1, fn });
}
export function renderAt(t) {
  tl.time(t, false);
  for (const a of animators) if (t >= a.t0 - 1e-3 && t <= a.t1 + 1e-3) a.fn(t);
}

/* ---------- sound-effect cue list (exported for the audio mixer) -------- */
export const SFX = [];
export function sfx(t, name, gain = 1, extra = {}) { SFX.push({ t: +t.toFixed(3), name, gain, ...extra }); }

/* ---------- reveal helpers ----------------------------------------- */
/** Fade/slide an element in. */
export function show(el, t, d = 0.5, o = {}) {
  tl.fromTo(
    el,
    { autoAlpha: 0, x: o.x ?? 0, y: o.y ?? 18, scale: o.scale ?? 1, ...(o.svgOrigin ? { svgOrigin: o.svgOrigin } : {}) },
    { autoAlpha: o.opacity ?? 1, x: 0, y: 0, scale: 1, duration: d, ease: o.ease || 'power3.out', immediateRender: true },
    t
  );
}
export function hide(el, t, d = 0.4, o = {}) {
  tl.to(el, { autoAlpha: 0, x: o.x ?? 0, y: o.y ?? 0, duration: d, ease: o.ease || 'power2.in' }, t);
}
/** Opacity-only reveal (safe for elements that carry a static transform attribute). */
export function fadeIn(el, t, d = 0.5, op = 1) {
  tl.fromTo(el, { autoAlpha: 0 }, { autoAlpha: op, duration: d, ease: 'power2.out', immediateRender: true }, t);
}
export function fadeOut(el, t, d = 0.4) {
  tl.to(el, { autoAlpha: 0, duration: d, ease: 'power2.in' }, t);
}
/** Make `el` visible during [t0,t1] with cross-fades. */
export function window_(el, t0, t1, { fi = 0.5, fo = 0.5 } = {}) {
  gsap.set(el, { autoAlpha: 0 });
  tl.fromTo(el, { autoAlpha: 0 }, { autoAlpha: 1, duration: fi, ease: 'power1.out', immediateRender: false }, t0);
  tl.to(el, { autoAlpha: 0, duration: fo, ease: 'power1.in' }, t1 - fo);
}
/** Stagger children appearing one after another. */
export function stagger(els, t, step = 0.12, d = 0.45, o = {}) {
  els.forEach((el, i) => show(el, t + i * step, d, o));
}
/** Count a numeric proxy from a to b and call fmt(v). */
export function tweenNumber(t, d, a, b, fn, ease = 'power2.out') {
  const o = { v: a };
  tl.fromTo(o, { v: a }, { v: b, duration: d, ease, onUpdate: () => fn(o.v), immediateRender: false }, t);
}

/* ---------- camera -------------------------------------------------- */
/** World->screen camera: world point (wx,wy) is drawn at screen (sx,sy) with scale k. */
export class Cam {
  constructor(el, s0 = {}) {
    this.el = el;
    this.s = { wx: 0, wy: 0, sx: 960, sy: 540, k: 1, ...s0 };
    this.cur = { ...this.s };
    this.apply();
  }
  apply() {
    const { wx, wy, sx, sy, k } = this.s;
    this.el.setAttribute('transform', `translate(${sx.toFixed(2)} ${sy.toFixed(2)}) scale(${k.toFixed(5)}) translate(${(-wx).toFixed(2)} ${(-wy).toFixed(2)})`);
  }
  /** Animate to a (partial) shot over d seconds starting at t. Returns the full target shot. */
  go(t, d, shot, ease = 'power3.inOut') {
    const from = { ...this.cur };
    const to = { ...this.cur, ...shot };
    tl.fromTo(this.s, from, { ...to, duration: Math.max(d, 0.001), ease, onUpdate: () => this.apply(), immediateRender: false }, t);
    this.cur = to;
    return to;
  }
  /** Snap to a shot at time t (no move). */
  cut(t, shot) {
    return this.go(t, 0.001, shot, 'none');
  }
}
/** Project a world point to screen for a given shot (final camera state). */
export const proj = (shot, wx, wy) => [shot.sx + (wx - shot.wx) * shot.k, shot.sy + (wy - shot.wy) * shot.k];

/* ---------- flow dots ----------------------------------------------- */
/** Marching dots along path `d` with glow. Speed can be ramped over time (integrated analytically). */
export function Flow(parent, d, o = {}) {
  const { color = '#FF9A3C', w = 7, gap = 24, glow = true, dir = 1, glowOp = 0.22, glowW = 2.6, blend } = o;
  const g = S('g', { opacity: 0, style: blend ? { mixBlendMode: blend } : {} });
  if (glow) g.append(S('path', { d, fill: 'none', stroke: color, 'stroke-width': w * glowW, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', opacity: glowOp }));
  const dots = S('path', { d, fill: 'none', stroke: color, 'stroke-width': w, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-dasharray': `0.01 ${gap}` });
  g.append(dots);
  parent.append(g);
  const knots = [[0, 0]];
  let tShow = Infinity, lastAction = 'none', lastEnd = 0;
  const period = gap + 0.01;
  const api = {
    g,
    /** ramp speed (px/s) to v, starting at t */
    speed(t, v, ramp = 0.45) {
      const last = knots[knots.length - 1];
      if (t > last[0]) knots.push([t, last[1]]);
      knots.push([t + ramp, v]);
      return api;
    },
    show(t, d = 0.4, v) {
      tl.fromTo(g, { opacity: 0 }, { opacity: 1, duration: d, ease: 'power1.out', immediateRender: false }, t);
      tShow = Math.min(tShow, t);
      lastAction = 'show';
      lastEnd = t + d;
      if (v !== undefined) api.speed(t, v, d);
      return api;
    },
    hide(t, d = 0.4) {
      tl.to(g, { opacity: 0, duration: d, ease: 'power1.in' }, t);
      lastAction = 'hide';
      lastEnd = t + d;
      return api;
    },
    pos(t) {
      let s = 0;
      for (let i = 0; i < knots.length - 1; i++) {
        const [t0, v0] = knots[i], [t1, v1] = knots[i + 1];
        if (t <= t0) break;
        const tt = Math.min(t, t1);
        const vt = v0 + (v1 - v0) * ((tt - t0) / (t1 - t0 || 1));
        s += ((v0 + vt) / 2) * (tt - t0);
        if (t < t1) return s;
      }
      const last = knots[knots.length - 1];
      if (t > last[0]) s += last[1] * (t - last[0]);
      return s;
    },
    update(t) {
      dots.setAttribute('stroke-dashoffset', (-(api.pos(t) * dir) % period).toFixed(2));
    },
  };
  animate(0, 1e9, (t) => {
    if (t >= tShow - 0.05 && (lastAction === 'show' || t <= lastEnd + 0.05)) api.update(t);
  });
  return api;
}

/* ---------- misc ----------------------------------------------------- */
/** Pulse value 0..1 – smooth periodic function */
export const pulse = (t, period = 1.4, phase = 0) => 0.5 + 0.5 * Math.sin(((t + phase) / period) * Math.PI * 2);
export { S, G, clamp };
