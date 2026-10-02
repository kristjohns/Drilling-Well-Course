// Fail-safe hydraulic gate valve (cut-away) ------------------------------
// Local frame: bore runs along +y through (0,0); the gate slides along x;
// the actuator is on the -x side.  Use rot/mirror to place it anywhere.
//   open fraction f: 0 = closed (spring extended, gate blocks the bore)
//                    1 = open   (hydraulic pressure compresses the spring)
import { S, G, coilD } from '../lib/svg.js';
import { tl, sfx } from '../engine.js';

const OPEN_C = '#3BDB86', CLOSED_C = '#FF3B5C', HYD = '#2ED0FF', SPRING = '#FFC857';

export function GateValve(parent, o = {}) {
  const {
    x = 0, y = 0, rot = 0, mirror = false, bw = 56, act = 'fs', f0 = 0, label = '',
    scale = 1, led = true, cavity = true, bonnetColor = '#33485A', ext = false,
  } = o;
  const b = bw / 2;
  const gt = Math.max(10, bw * 0.30);            // gate thickness
  const L = bw * 2.7;                              // gate length
  const uh = -L / 2 + bw * 0.7;                    // hole centre in plate coords
  const D = bw * 1.25;                             // stroke
  const xcOpen = -uh, xcClosed = -uh - D;          // plate centre positions
  const cavHalf = bw * 2.05;
  const bonnetW = bw * 0.34;
  const xb = -cavHalf - bonnetW;                   // outer face of bonnet
  const lenFree = D + bw * 0.95;                   // spring free length
  const xp0 = xb - lenFree;                        // piston face when closed
  const chamberMin = bw * 0.42;
  const wall = Math.max(3, bw * 0.08);
  const xIn = xp0 - chamberMin;                    // inner left end of the cylinder
  const cylH = bw * 1.28;

  const root = S('g', { transform: `translate(${x} ${y}) rotate(${rot}) scale(${mirror ? -scale : scale} ${scale})` });
  parent.append(root);

  // gate chamber ------------------------------------------------------
  const gCav = S('g');
  if (cavity) {
    gCav.append(
      S('rect', { x: -cavHalf, y: -gt / 2 - 3, width: cavHalf * 2, height: gt + 6, fill: '#070F16', stroke: '#1A2733', 'stroke-width': 2 }),
    );
  }
  // seats (fixed)
  const seatW = bw * 0.16, seatH = bw * 0.2;
  const seats = S('g', { fill: '#C4D2DD', stroke: '#1A2733', 'stroke-width': 1.5 },
    S('rect', { x: -b - seatW, y: -gt / 2 - seatH, width: seatW, height: seatH }),
    S('rect', { x: b, y: -gt / 2 - seatH, width: seatW, height: seatH }),
    S('rect', { x: -b - seatW, y: gt / 2, width: seatW, height: seatH }),
    S('rect', { x: b, y: gt / 2, width: seatW, height: seatH }));

  // gate (moves) ------------------------------------------------------
  const gate = S('g');
  const holeL = uh - b, holeR = uh + b;
  const gateFill = { fill: 'url(#gGate)', stroke: '#1A2733', 'stroke-width': 2 };
  gate.append(
    S('rect', { x: -L / 2, y: -gt / 2, width: holeL + L / 2, height: gt, ...gateFill }),
    S('rect', { x: holeR, y: -gt / 2, width: L / 2 - holeR, height: gt, ...gateFill }),
    S('rect', { x: holeR + 2, y: -gt / 2 + 2, width: L / 2 - holeR - 4, height: 3, fill: 'rgba(255,255,255,.55)' }),
  );

  // stem -------------------------------------------------------------
  const stem = S('rect', { x: 0, y: -bw * 0.085, width: 10, height: bw * 0.17, fill: '#D6E1EA', stroke: '#1A2733', 'stroke-width': 1.5 });

  // actuator ---------------------------------------------------------
  const actG = S('g');
  let piston, spring, fluid, ledEl, ledGlow, fluidFlow, ovr, handle;
  const bonnet = S('rect', { x: xb, y: -bw * 0.5, width: bonnetW, height: bw, fill: bonnetColor, stroke: '#1A2733', 'stroke-width': 2, rx: 3 });
  if (ext) {
    // exterior view: solid actuator shell, no internals
    if (act === 'fs') {
      const portX = xIn - wall;
      actG.append(
        S('rect', { x: xIn - wall, y: -cylH / 2 - wall, width: xb - xIn + wall, height: cylH + 2 * wall, rx: 7, fill: 'url(#gAct)', stroke: '#0E2236', 'stroke-width': 2.5 }),
        S('rect', { x: xIn + (xb - xIn) * 0.35, y: -cylH / 2 - wall, width: bw * 0.08, height: cylH + 2 * wall, fill: 'rgba(255,255,255,.35)' }),
        S('rect', { x: portX - bw * 0.34, y: -bw * 0.17, width: bw * 0.34, height: bw * 0.34, rx: 3, fill: '#2A3B49', stroke: '#0E2236', 'stroke-width': 2 }),
        S('path', { d: `M${portX - bw * 0.26} 0 l${bw * 0.05} ${-bw * 0.08} h${bw * 0.1} l${bw * 0.05} ${bw * 0.08} l${-bw * 0.05} ${bw * 0.08} h${-bw * 0.1} z`, fill: '#9FB2C2' }),
        S('rect', { x: portX + bw * 0.1, y: -cylH / 2 - wall - bw * 0.3, width: bw * 0.16, height: bw * 0.3 + wall, fill: '#1E3346', stroke: '#0E2236', 'stroke-width': 1.5 }));
    } else if (act === 'manual') {
      actG.append(
        S('rect', { x: xb - bw * 0.9, y: -bw * 0.09, width: bw * 0.9, height: bw * 0.18, fill: '#C9D6E0', stroke: '#1A2733', 'stroke-width': 1.2 }),
        S('rect', { x: xb - bw * 1.1, y: -bw * 0.26, width: bw * 0.2, height: bw * 0.52, rx: 3, fill: '#E8913A', stroke: '#6B3A0C', 'stroke-width': 1.5 }));
    }
    actG.append(bonnet);
    root.append(actG);
    const apiE = { g: root, cur: f0, set() {}, open() { return apiE; }, close() { return apiE; }, to() { return apiE; }, toWorld: () => [x, y], anchors: {} };
    return apiE;
  }
  if (act === 'fs') {
    const shell = S('g');
    shell.append(
      S('rect', { x: xIn - wall, y: -cylH / 2 - wall, width: xb - xIn + wall, height: cylH + 2 * wall, rx: 6, fill: 'url(#gAct)', stroke: '#0E2236', 'stroke-width': 2.5 }),
      S('rect', { x: xIn, y: -cylH / 2, width: xb - xIn, height: cylH, fill: '#06101A' }),
    );
    fluid = S('rect', { x: xIn, y: -cylH / 2, width: 10, height: cylH, fill: HYD, opacity: 0.55 });
    piston = S('g');
    piston.append(S('rect', { x: -bw * 0.12, y: -cylH / 2, width: bw * 0.12, height: cylH, fill: '#DCE6EE', stroke: '#1A2733', 'stroke-width': 1.5 }));
    spring = S('path', { d: '', fill: 'none', stroke: SPRING, 'stroke-width': Math.max(2.4, bw * 0.062), 'stroke-linejoin': 'round', 'stroke-linecap': 'round' });
    // hydraulic port + ROV override on the end cap
    const portX = xIn - wall;
    ovr = S('g', {},
      S('rect', { x: portX - bw * 0.34, y: -bw * 0.17, width: bw * 0.34, height: bw * 0.34, rx: 3, fill: '#2A3B49', stroke: '#0E2236', 'stroke-width': 2 }),
      S('path', { d: `M${portX - bw * 0.26} 0 l${bw * 0.05} ${-bw * 0.08} h${bw * 0.1} l${bw * 0.05} ${bw * 0.08} l${-bw * 0.05} ${bw * 0.08} h${-bw * 0.1} z`, fill: '#9FB2C2' }));
    const port = S('g', {},
      S('rect', { x: portX + bw * 0.1, y: -cylH / 2 - wall - bw * 0.3, width: bw * 0.16, height: bw * 0.3 + wall, fill: '#1E3346', stroke: '#0E2236', 'stroke-width': 1.5 }),
      S('circle', { cx: portX + bw * 0.18, cy: -cylH / 2 - wall - bw * 0.3, r: bw * 0.095, fill: HYD }));
    fluidFlow = port;
    actG.append(shell, fluid, spring, piston, ovr, port);
  } else if (act === 'manual') {
    handle = S('g');
    handle.append(
      S('rect', { x: -bw * 0.5, y: -bw * 0.26, width: bw * 0.2, height: bw * 0.52, rx: 3, fill: '#E8913A', stroke: '#6B3A0C', 'stroke-width': 1.5 }),
      S('rect', { x: -bw * 0.3, y: -bw * 0.09, width: bw * 0.3, height: bw * 0.18, fill: '#C9D6E0', stroke: '#1A2733', 'stroke-width': 1.2 }));
    actG.append(handle);
  }
  actG.append(bonnet);

  if (led && act === 'fs') {
    ledGlow = S('circle', { r: bw * 0.3, cx: xIn + bw * 0.1, cy: -cylH / 2 - wall - bw * 0.62, fill: 'url(#gGlowRed)', opacity: 0.9 });
    ledEl = S('circle', { r: bw * 0.115, cx: xIn + bw * 0.1, cy: -cylH / 2 - wall - bw * 0.62, fill: CLOSED_C, stroke: '#07101A', 'stroke-width': 1.5 });
    actG.append(ledGlow, ledEl);
  }

  root.append(gCav, seats, gate, stem, actG);

  // state --------------------------------------------------------------
  const api = {
    g: root, bw, D, cur: f0, parts: { gate, stem, spring, piston, fluid, led: ledEl },
    anchors: {
      center: [x, y],
      /** world position of the hydraulic port (for hose routing) */
      portLocal: [xIn - wall + bw * 0.18, -cylH / 2 - wall - bw * 0.3],
      actEndLocal: [xIn - wall - bw * 0.34, 0],
    },
    /** local -> world for point (px,py) */
    toWorld(px, py) {
      const s = scale, sx = mirror ? -s : s;
      const r = (rot * Math.PI) / 180, c = Math.cos(r), sn = Math.sin(r);
      const lx = px * sx, ly = py * s;
      return [x + lx * c - ly * sn, y + lx * sn + ly * c];
    },
    set(f) {
      const xc = xcClosed + (xcOpen - xcClosed) * f;
      gate.setAttribute('transform', `translate(${xc.toFixed(2)} 0)`);
      const gl = xc - L / 2;                     // gate left end
      if (act === 'fs') {
        const xp = xp0 + D * f;
        piston.setAttribute('transform', `translate(${xp.toFixed(2)} 0)`);
        spring.setAttribute('d', coilD(xp, 0, xb, 0, 8, cylH * 0.3));
        fluid.setAttribute('width', Math.max(1, xp - xIn).toFixed(2));
        fluid.setAttribute('opacity', (0.28 + 0.4 * f).toFixed(2));
        stem.setAttribute('x', xp.toFixed(2));
        stem.setAttribute('width', Math.max(1, gl - xp).toFixed(2));
        if (ledEl) {
          const on = f > 0.5;
          ledEl.setAttribute('fill', on ? OPEN_C : CLOSED_C);
          ledGlow.setAttribute('fill', on ? 'url(#gGlowGreen)' : 'url(#gGlowRed)');
        }
      } else if (act === 'manual') {
        const xh = gl - bw * 0.55 - cavHalf * 0.1;
        stem.setAttribute('x', (xh).toFixed(2));
        stem.setAttribute('width', Math.max(1, gl - xh).toFixed(2));
        handle.setAttribute('transform', `translate(${(xh).toFixed(2)} 0)`);
      } else {
        stem.setAttribute('width', 0);
      }
    },
    /** Timeline: open (hydraulic pressure applied) */
    open(t, d = 1.5, ease = 'power2.inOut') { return api.to(t, d, 1, ease); },
    /** Timeline: close (pressure vented, spring drives gate shut) */
    close(t, d = 0.6, ease = 'power3.in') { return api.to(t, d, 0, ease); },
    to(t, d, f, ease = 'power2.inOut') {
      const p = { f: api.cur };
      if (Math.abs(f - api.cur) > 0.3 && d >= 0.2 && !ext) sfx(t, f > api.cur ? 'valveOpen' : 'valveClose', 1, { d, auto: true });
      tl.fromTo(p, { f: api.cur }, { f, duration: Math.max(0.001, d), ease, onUpdate: () => api.set(p.f), immediateRender: false }, t);
      api.cur = f;
      return api;
    },
  };
  api.set(f0);
  return api;
}
