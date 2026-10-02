// Shared "tree stage": one continuous cut-away world used by anatomy, gate, valves, barriers, esd.
import { H, S } from '../lib/svg.js';
import { BLUEPRINT } from '../lib/scene.js';
import { installDefs } from '../art/defs.js';
import { buildTree, W, COL } from '../art/tree.js';
import { buildTreeExterior } from '../art/treeExt.js';
import { buildWell, WELL } from '../art/well.js';
import { tag, leader, callout, ring } from '../lib/annot.js';

export function createTreeStage(root, E, ranges) {
  const { T, tl, gsap, Cam, proj, show, hide, fadeIn, fadeOut, sfx, animate, Flow } = E;
  installDefs();

  const el = H('div', { class: 'scene', id: 'scene-tree', style: { background: BLUEPRINT } });
  root.append(el);
  // visible only during the given [a,b] ranges (cross-fades)
  gsap.set(el, { autoAlpha: 0 });
  ranges.forEach(([a, b], i) => {
    tl.fromTo(el, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.6, ease: 'power1.out', immediateRender: false }, a);
    tl.to(el, { autoAlpha: 0, duration: 0.6, ease: 'power1.in' }, b - 0.6);
  });

  const svg = S('svg', { viewBox: '0 0 1920 1080' });
  el.append(svg);
  const world = S('g');
  svg.append(world);
  const annot = S('g');
  svg.append(annot);
  const html = H('div', { class: 'html' });
  el.append(html);

  // starts on the exterior framing of the 'jobs' scene, then dollies into the full cut-away shot
  const cam = new Cam(world, { wx: 0, wy: -520, sx: 1100, sy: 560, k: 0.62 });
  world.append(S('rect', { x: -3000, y: 0, width: 6000, height: 1400, fill: 'url(#gSeabed)' }), S('path', { d: 'M-3000 0 H3000', stroke: '#31434F', 'stroke-width': 4 }));
  const tree = buildTree(world);
  const well = buildWell(world);
  const ext = buildTreeExterior(world);
  // the well sits below the seabed; hidden until needed
  gsap.set(well.root, { autoAlpha: 0 });
  // x-ray wipe: section visible left of the scan line, exterior right of it
  const defsW = S('defs', {},
    S('clipPath', { id: 'clipSec', clipPathUnits: 'userSpaceOnUse' }, S('rect', { id: 'clipSecR', x: -1400, y: -600, width: 0, height: 2200 })),
    S('clipPath', { id: 'clipExt', clipPathUnits: 'userSpaceOnUse' }, S('rect', { id: 'clipExtR', x: -1400, y: -600, width: 2800, height: 2200 })));
  svg.append(defsW);
  tree.root.setAttribute('clip-path', 'url(#clipSec)');
  ext.root.setAttribute('clip-path', 'url(#clipExt)');
  const scan = S('g', { opacity: 0 }, S('rect', { x: -5, y: -1250, width: 10, height: 1500, fill: '#9FE6FF' }), S('rect', { x: -40, y: -1250, width: 80, height: 1500, fill: 'url(#gScanGlow)', opacity: 0.55 }));
  defsW.append(S('linearGradient', { id: 'gScanGlow', x1: 0, y1: 0, x2: 1, y2: 0 }, S('stop', { offset: 0, 'stop-color': '#2ED0FF', 'stop-opacity': 0 }), S('stop', { offset: 0.5, 'stop-color': '#2ED0FF', 'stop-opacity': 0.9 }), S('stop', { offset: 1, 'stop-color': '#2ED0FF', 'stop-opacity': 0 })));
  world.append(scan);
  /** run the x-ray wipe from t0 over d seconds */
  const wipe = (t0, d) => {
    const p = { v: 0 };
    const X0 = -820, X1 = 860;
    const apply = () => {
      const x = X0 + (X1 - X0) * p.v;
      document.getElementById('clipSecR').setAttribute('width', (x + 1400).toFixed(1));
      document.getElementById('clipExtR').setAttribute('x', x.toFixed(1));
      document.getElementById('clipExtR').setAttribute('width', (2800 - (x + 1400)).toFixed(1));
      scan.setAttribute('transform', `translate(${x.toFixed(1)} 0)`);
    };
    tl.fromTo(p, { v: 0 }, { v: 1, duration: d, ease: 'power2.inOut', onUpdate: apply, immediateRender: false }, t0);
    tl.fromTo(scan, { opacity: 0 }, { opacity: 1, duration: 0.2, immediateRender: false }, t0);
    tl.to(scan, { opacity: 0, duration: 0.25 }, t0 + d - 0.1);
    tl.set(ext.root, { autoAlpha: 0 }, t0 + d + 0.05);
  };
  gsap.set(tree.root, { autoAlpha: 1 });
  document.getElementById('clipSecR').setAttribute('width', 0);

  const ctx = { E, el, svg, world, annot, html, cam, tree, well, ext, W, COL, WELL, T, wipe };

  /* ---- projection helpers -------------------------------------------------- */
  /** world position of tree-local (tx,ty) */
  ctx.w = (tx, ty) => W(tx, ty);
  ctx.P = (shot, tx, ty) => { const [wx, wy] = W(tx, ty); return proj(shot, wx, wy); };
  ctx.Pw = (shot, wx, wy) => proj(shot, wx, wy);

  /* ---- annotation primitives --------------------------------------------------- */
  /** callout with target in tree-local coords; label offset (dx,dy) in screen px. */
  ctx.note = ({ shot, at, until, tx, ty, wx, wy, dx = 160, dy = -90, label, sub, color = '#FFC857', size = 26, mono = false, anchor, fade = 0.45 }) => {
    const target = wx !== undefined ? proj(shot, wx, wy) : ctx.P(shot, tx, ty);
    const to = [target[0] + dx, target[1] + dy];
    const a = anchor || (dx >= 0 ? 'l' : 'r');
    const c = callout(annot, { target, at: to, text: label, sub, color, anchor: a, size, mono, elbow: Math.abs(dx) > 60 && Math.abs(dy) > 20 ? [to[0] - Math.sign(dx) * 40, to[1]] : null });
    show(c.g, at, fade, { y: 10 });
    if (until !== undefined) hide(c.g, until, 0.4);
    return c;
  };
  /** pulsing ring at a screen position */
  ctx.ringAt = ({ shot, tx, ty, wx, wy, r = 42, color = '#FFC857', at, until, w = 4, period = 1.2 }) => {
    const p = wx !== undefined ? proj(shot, wx, wy) : ctx.P(shot, tx, ty);
    const g = ring(annot, p[0], p[1], { r, color, w, t0: at, t1: until ?? 1e9, period });
    tl.fromTo(g, { opacity: 0 }, { opacity: 1, duration: 0.35, immediateRender: true }, at);
    if (until !== undefined) tl.to(g, { opacity: 0, duration: 0.35 }, until);
    return g;
  };
  /** free tag at screen coords */
  ctx.tagAt = ({ x, y, text, sub, color = '#FFC857', anchor = 'l', size = 26, mono = false, at, until, fade = 0.45 }) => {
    const t = tag(annot, { x, y, text, sub, accent: color, anchor, size, mono });
    show(t.el, at, fade, { y: 10 });
    if (until !== undefined) hide(t.el, until, 0.4);
    return t;
  };
  /** dashed outline box around a tree-local region (screen-space rect) */
  ctx.boxAt = ({ shot, tx0, ty0, tx1, ty1, color = '#FFC857', at, until, pad = 10 }) => {
    const a = ctx.P(shot, tx0, ty0), b = ctx.P(shot, tx1, ty1);
    const g = S('g');
    g.append(S('rect', { x: Math.min(a[0], b[0]) - pad, y: Math.min(a[1], b[1]) - pad, width: Math.abs(b[0] - a[0]) + pad * 2, height: Math.abs(b[1] - a[1]) + pad * 2, rx: 14, fill: 'none', stroke: color, 'stroke-width': 3.5, 'stroke-dasharray': '14 10' }));
    annot.append(g);
    tl.fromTo(g, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: true }, at);
    if (until !== undefined) tl.to(g, { opacity: 0, duration: 0.4 }, until);
    return g;
  };

  /* ---- valve status tags (LED + OPEN / CLOSED, switching over time) ------------------- */
  ctx.status = ({ name, shot, tx, ty, wx, wy, dx = 0, dy = -70, at, until, states, color = '#EEF4F9', anchor = 'c' }) => {
    const p = wx !== undefined ? proj(shot, wx, wy) : ctx.P(shot, tx, ty);
    const x = p[0] + dx, y = p[1] + dy;
    const g = S('g');
    annot.append(g);
    const outer = S('g', { transform: `translate(${x} ${y})` });
    const inner = S('g');
    outer.append(inner);
    g.append(outer);
    const w = 232, h = 50;
    inner.append(S('rect', { x: -w / 2, y: -h / 2, width: w, height: h, rx: 12, fill: 'rgba(5,16,26,.9)', stroke: 'rgba(170,200,225,.38)', 'stroke-width': 1.6 }));
    const led = S('circle', { cx: -w / 2 + 28, cy: 0, r: 10, fill: states[0].open ? COL.open : COL.closed });
    const glow = S('circle', { cx: -w / 2 + 28, cy: 0, r: 20, fill: states[0].open ? 'url(#gGlowGreen)' : 'url(#gGlowRed)', opacity: 0.8 });
    const nm = S('text', { x: -w / 2 + 52, y: 8.5, fill: color, 'font-size': 25, 'font-weight': 700, style: { fontFamily: 'var(--mono)' }, text: name });
    const tOpen = S('text', { x: w / 2 - 18, y: 8.5, 'text-anchor': 'end', fill: COL.open, 'font-size': 22, 'font-weight': 700, style: { fontFamily: 'var(--mono)' }, text: 'OPEN', opacity: states[0].open ? 1 : 0 });
    const tClosed = S('text', { x: w / 2 - 18, y: 8.5, 'text-anchor': 'end', fill: COL.closed, 'font-size': 22, 'font-weight': 700, style: { fontFamily: 'var(--mono)' }, text: 'CLOSED', opacity: states[0].open ? 0 : 1 });
    inner.append(glow, led, nm, tOpen, tClosed);
    show(inner, at, 0.45, { y: 10 });
    states.slice(1).forEach((s_) => {
      tl.to(led, { attr: { fill: s_.open ? COL.open : COL.closed }, duration: 0.12 }, s_.t);
      tl.to(glow, { attr: { fill: s_.open ? 'url(#gGlowGreen)' : 'url(#gGlowRed)' }, duration: 0.12 }, s_.t);
      tl.to(tOpen, { opacity: s_.open ? 1 : 0, duration: 0.1 }, s_.t);
      tl.to(tClosed, { opacity: s_.open ? 0 : 1, duration: 0.1 }, s_.t);
    });
    if (until !== undefined) hide(inner, until, 0.4);
    return { g: inner };
  };

  /* ---- left panel (HTML) ---------------------------------------------------------- */
  ctx.panel = ({ at, until, kicker, title, body, color = '#FFC857', left = 96, top = 170, width = 440 }) => {
    const p = H('div', { class: 'abs', style: { left: left + 'px', top: top + 'px', width: width + 'px' } },
      kicker ? H('div', { class: 'kicker', style: { color, marginBottom: '14px' }, text: kicker }) : null,
      title ? H('div', { class: 'h2', style: { fontSize: '50px', lineHeight: '1.08' }, html: title }) : null,
      body ? H('div', { class: 'body', style: { marginTop: '16px', fontSize: '28px', lineHeight: '1.38' }, html: body }) : null);
    html.append(p);
    show(p, at, 0.6, { x: -26, y: 0 });
    if (until !== undefined) hide(p, until, 0.45, { x: -16 });
    return p;
  };

  ctx.ex = { dim: (t, d = 0.5, op = 0.15) => tl.to(tree.root, { opacity: op, duration: d }, t) };
  return ctx;
}
