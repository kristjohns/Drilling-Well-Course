// Vertical subsea tree – cut-away illustration -------------------------
// Local frame: x=0 is the production bore centre-line, ty=0 the top of the tree cap,
// the seabed is at ty=900.  The whole tree lives in a group translated by (0,-900),
// so WORLD y = ty - 900 (seabed = 0, up is negative).
import { S, G, pathD } from '../lib/svg.js';
import { tl, Flow, sfx } from '../engine.js';
import { GateValve } from './valve.js';

export const SEABED_TY = 900;
export const W = (tx, ty) => [tx, ty - SEABED_TY];       // tree-local -> world

export const COL = { hc: '#FF9A3C', ann: '#34D8A8', hyd: '#2ED0FF', chem: '#BC8FFF', open: '#3BDB86', closed: '#FF3B5C' };
const OUT = '#0B141C';                                    // outline colour
const BORE = '#050B11';

/** merged union of rects: outline layer first, fill layer on top */
function union(parent, rects, { fill = 'url(#gTreeBody)', outline = OUT, t = 3.5, bevel = true } = {}) {
  const g = S('g');
  rects.forEach((r) => g.append(S('rect', { ...r, fill: outline, stroke: outline, 'stroke-width': t * 2, 'stroke-linejoin': 'round' })));
  rects.forEach((r) => g.append(S('rect', { ...r, fill })));
  if (bevel) rects.forEach((r) => g.append(S('rect', { x: r.x + 4, y: r.y + 4, width: r.width - 8, height: r.height - 8, rx: Math.max(0, (r.rx || 0) - 3), fill: 'none', stroke: 'rgba(255,255,255,.13)', 'stroke-width': 2 })));
  parent.append(g);
  return g;
}

/** a pipe along an SVG path with bore + removable fluid fill */
function pipe(parent, d, { outer = 36, inner = 20, fill = '#4E6376' } = {}) {
  const g = S('g');
  const pOuter = S('path', { d, fill: 'none', stroke: OUT, 'stroke-width': outer + 7, 'stroke-linejoin': 'round' });
  const pBody = S('path', { d, fill: 'none', stroke: fill, 'stroke-width': outer, 'stroke-linejoin': 'round' });
  const pHi = S('path', { d, fill: 'none', stroke: 'rgba(255,255,255,.12)', 'stroke-width': outer - 8, 'stroke-linejoin': 'round' });
  const pBore = S('path', { d, fill: 'none', stroke: BORE, 'stroke-width': inner, 'stroke-linejoin': 'round' });
  const pFill = S('path', { d, fill: 'none', stroke: '#fff', 'stroke-width': inner, 'stroke-linejoin': 'round', opacity: 0 });
  g.append(pOuter, pBody, pHi, pBore, pFill);
  parent.append(g);
  return { g, fillEl: pFill };
}

export function buildTree(parent) {
  const gdefs = S('defs');
  gdefs.append(
    S('linearGradient', { id: 'gTreeBody', gradientUnits: 'userSpaceOnUse', x1: -260, y1: 40, x2: 300, y2: 700 },
      S('stop', { offset: 0, 'stop-color': '#7F98AC' }), S('stop', { offset: 0.5, 'stop-color': '#5B7184' }), S('stop', { offset: 1, 'stop-color': '#40525F' })),
    S('linearGradient', { id: 'gHanger', gradientUnits: 'userSpaceOnUse', x1: -170, y1: 0, x2: 170, y2: 0 },
      S('stop', { offset: 0, 'stop-color': '#27353F' }), S('stop', { offset: 0.5, 'stop-color': '#42576A' }), S('stop', { offset: 1, 'stop-color': '#27353F' })),
    S('linearGradient', { id: 'gWellhead', gradientUnits: 'userSpaceOnUse', x1: -230, y1: 0, x2: 230, y2: 0 },
      S('stop', { offset: 0, 'stop-color': '#3A4B59' }), S('stop', { offset: 0.5, 'stop-color': '#6C8598' }), S('stop', { offset: 1, 'stop-color': '#33434E' })),
    S('linearGradient', { id: 'gFluidHC', x1: 0, y1: 0, x2: 1, y2: 0 },
      S('stop', { offset: 0, 'stop-color': '#FF8A24' }), S('stop', { offset: 0.5, 'stop-color': '#FFB25E' }), S('stop', { offset: 1, 'stop-color': '#FF8A24' })),
    S('radialGradient', { id: 'gShadowE', cx: 0.5, cy: 0.5, r: 0.5 }, S('stop', { offset: 0, 'stop-color': '#000', 'stop-opacity': 0.6 }), S('stop', { offset: 1, 'stop-color': '#000', 'stop-opacity': 0 })),
  );
  const root = S('g', { transform: `translate(0 ${-SEABED_TY})` });
  root.append(gdefs);
  parent.append(root);
  const R = { root, valves: {}, fills: {}, flows: {}, groups: {}, overlays: {}, anchors: {} };

  /* ---------------- seabed + shadow (behind everything) ---------------- */
  const seabed = S('g');
  seabed.append(
    S('rect', { x: -1500, y: SEABED_TY, width: 3000, height: 1200, fill: 'url(#gSeabed)' }),
    S('ellipse', { cx: 0, cy: SEABED_TY + 6, rx: 420, ry: 34, fill: 'url(#gShadowE)' }),
    S('path', { d: `M-1500 ${SEABED_TY} H1500`, stroke: '#566873', 'stroke-width': 3 }),
    S('path', { d: `M-1500 ${SEABED_TY + 28} H1500`, stroke: 'rgba(120,150,170,.10)', 'stroke-width': 2 }),
  );
  // a few pebbles for texture
  [[-640, 30, 9], [-520, 44, 6], [-330, 22, 7], [330, 36, 8], [470, 26, 6], [640, 48, 10], [-820, 40, 8], [820, 24, 6]].forEach(([x, dy, r]) =>
    seabed.append(S('ellipse', { cx: x, cy: SEABED_TY + dy, rx: r * 1.5, ry: r * 0.7, fill: '#2B3A44', stroke: '#3C4E5A', 'stroke-width': 1.5 })));
  root.append(seabed);
  R.groups.seabed = seabed;

  /* ---------------- structure ---------------- */
  const struct = S('g');
  root.append(struct);
  union(struct, [{ x: -215, y: 712, width: 430, height: 200, rx: 22 }], { fill: 'url(#gWellhead)' });
  union(struct, [{ x: -232, y: 636, width: 464, height: 84, rx: 16 }], { fill: 'url(#gWellhead)' });
  union(struct, [
    { x: -130, y: 48, width: 335, height: 600, rx: 18 },
    { x: -62, y: 10, width: 124, height: 50, rx: 24 },
    { x: 130, y: 30, width: 40, height: 26, rx: 8 },
  ]);
  // flange bands + hatch texture on the block (section-cut feel)
  struct.append(
    S('rect', { x: -130, y: 48, width: 335, height: 600, rx: 18, fill: 'url(#pHatch)', opacity: 0.55 }),
    S('rect', { x: -130, y: 196, width: 335, height: 9, fill: 'rgba(255,255,255,.10)' }),
    S('rect', { x: -130, y: 598, width: 335, height: 9, fill: 'rgba(255,255,255,.10)' }),
    // lifting eye on the cap
    S('path', { d: 'M-20 14 q0 -34 20 -34 q20 0 20 34', fill: 'none', stroke: OUT, 'stroke-width': 11, 'stroke-linecap': 'round' }),
    S('path', { d: 'M-20 14 q0 -34 20 -34 q20 0 20 34', fill: 'none', stroke: '#E5701A', 'stroke-width': 6, 'stroke-linecap': 'round' }),
  );
  union(struct, [
    { x: -566, y: 282, width: 450, height: 76, rx: 10 },
    { x: 190, y: 296, width: 360, height: 48, rx: 8 },
  ]);
  R.groups.struct = struct;

  /* ---------------- hanger ---------------- */
  const hanger = S('g');
  hanger.append(
    S('rect', { x: -172, y: 722, width: 344, height: 84, rx: 6, fill: 'url(#gHanger)', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: -176, y: 738, width: 8, height: 10, fill: '#C9D6E0' }), S('rect', { x: 168, y: 738, width: 8, height: 10, fill: '#C9D6E0' }),
    S('rect', { x: -176, y: 770, width: 8, height: 10, fill: '#C9D6E0' }), S('rect', { x: 168, y: 770, width: 8, height: 10, fill: '#C9D6E0' }),
    S('text', { x: 0, y: 797, 'text-anchor': 'middle', fill: 'rgba(255,255,255,0)', text: '' }),
  );
  root.append(hanger);
  R.groups.hanger = hanger;
  // casing-head cavity under the hanger, with the tubing running through it
  root.append(
    S('rect', { x: -172, y: 806, width: 344, height: 106, fill: '#06101A' }),
    S('rect', { x: -40, y: 806, width: 14, height: 106, fill: '#B3C4D2', stroke: OUT, 'stroke-width': 2 }),
    S('rect', { x: 26, y: 806, width: 14, height: 106, fill: '#B3C4D2', stroke: OUT, 'stroke-width': 2 }));

  /* ---------------- bores (dark channels) ---------------- */
  const bores = S('g', { fill: BORE });
  const bore = (x, y, w, h) => bores.append(S('rect', { x, y, width: w, height: h }));
  bore(-26, 52, 52, 860);                 // production bore (down into tubing)
  bore(135, 48, 30, 758);                 // annulus bore (ends in the hanger)
  bore(-566, 301, 456, 38);               // production outlet bore (to hub)
  bore(-130, 301, 106, 38);
  bore(165, 309, 380, 22);                // annulus outlet bore
  root.append(bores);
  R.groups.bores = bores;

  /* ---------------- fluid fills (segments) ---------------- */
  const fills = S('g');
  root.append(fills);
  const fill = (name, x, y, w, h, color, grad) => {
    const r = S('rect', { x, y, width: w, height: h, fill: grad || color, opacity: 0 });
    fills.append(r);
    R.fills[name] = { el: r, color, to(t, d = 0.6, op = 0.5) { tl.to(r, { opacity: op, duration: d, ease: 'power1.out' }, t); return R.fills[name]; } };
    return R.fills[name];
  };
  const HCg = 'url(#gFluidHC)';
  fill('p_low', -26, 536, 52, 376, COL.hc, HCg);
  fill('p_mid', -26, 340, 52, 150, COL.hc, HCg);
  fill('p_tee', -26, 301, 52, 40, COL.hc, HCg);
  fill('p_up', -26, 138, 52, 163, COL.hc, HCg);
  fill('p_top', -26, 52, 52, 50, COL.hc, HCg);
  fill('p_br1', -108, 301, 82, 38, COL.hc);
  fill('p_br2', -190, 301, 82, 38, COL.hc);
  fill('p_out1', -566, 301, 296, 38, COL.hc);
  fill('a_low', 135, 520, 30, 286, COL.ann);
  fill('a_mid', 135, 330, 30, 160, COL.ann);
  fill('a_up', 135, 138, 30, 192, COL.ann);
  fill('a_out', 165, 309, 380, 22, COL.ann);

  /* ---------------- valves ---------------- */
  const V = R.valves;
  V.PMV = GateValve(root, { x: 0, y: 500, bw: 52, act: 'fs', f0: 1 });
  V.PSV = GateValve(root, { x: 0, y: 110, bw: 52, act: 'manual', f0: 0 });
  V.AMV = GateValve(root, { x: 150, y: 500, bw: 30, act: 'fs', mirror: true, f0: 1 });
  V.ASV = GateValve(root, { x: 150, y: 110, bw: 30, act: 'manual', mirror: true, f0: 0 });
  union(root, [{ x: -280, y: 236, width: 100, height: 168, rx: 10 }]);
  union(root, [{ x: 372, y: 264, width: 56, height: 112, rx: 8 }]);
  root.append(S('rect', { x: -280, y: 301, width: 100, height: 38, fill: BORE }), S('rect', { x: 372, y: 309, width: 56, height: 22, fill: BORE }));
  V.PWV = GateValve(root, { x: -230, y: 320, bw: 38, rot: 90, act: 'fs', f0: 1 });
  V.AWV = GateValve(root, { x: 400, y: 320, bw: 22, rot: 90, act: 'fs', f0: 0 });

  /* ---------------- choke ---------------- */
  const chokeG = S('g');
  union(chokeG, [{ x: -452, y: 262, width: 104, height: 116, rx: 10 }, { x: -430, y: 196, width: 60, height: 74, rx: 8 }]);
  chokeG.append(
    S('rect', { x: -452, y: 301, width: 104, height: 38, fill: BORE }),
    S('rect', { x: -420, y: 214, width: 40, height: 100, fill: '#07131C' }),
  );
  const cage = S('g', { fill: '#C4D2DD', stroke: OUT, 'stroke-width': 2 },
    S('rect', { x: -422, y: 290, width: 8, height: 62 }), S('rect', { x: -386, y: 290, width: 8, height: 62 }));
  const plug = S('g');
  plug.append(
    S('rect', { x: -412, y: 200, width: 24, height: 80, fill: 'url(#gGate)', stroke: OUT, 'stroke-width': 2 }),
    S('path', { d: 'M-412 280 h24 l-5 26 h-14 z', fill: '#E5ECF2', stroke: OUT, 'stroke-width': 2 }),
  );
  const chokeAct = S('g');
  chokeAct.append(
    S('rect', { x: -436, y: 128, width: 72, height: 78, rx: 8, fill: 'url(#gAct)', stroke: '#0E2236', 'stroke-width': 2.5 }),
    S('rect', { x: -424, y: 108, width: 48, height: 24, rx: 6, fill: '#2A3B49', stroke: '#0E2236', 'stroke-width': 2 }),
    S('path', { d: 'M-408 120 l5 -8 h10 l5 8 l-5 8 h-10 z', fill: '#9FB2C2' }),
  );
  const insert = S('g');
  insert.append(plug, chokeAct);
  chokeG.append(cage, insert);
  root.append(chokeG);
  const choke = {
    g: chokeG, insert, cage, cur: 0.5,
    set(f) { plug.setAttribute('transform', `translate(0 ${(-62 * f).toFixed(2)})`); },
    to(t, d, f, ease = 'power2.inOut') {
      const p = { f: choke.cur };
      if (Math.abs(f - choke.cur) > 0.05 && d > 0.3) sfx(t, 'chokeAdjust', 1, { d, auto: true });
      tl.fromTo(p, { f: choke.cur }, { f, duration: Math.max(0.001, d), ease, onUpdate: () => choke.set(p.f), immediateRender: false }, t);
      choke.cur = f;
      return choke;
    },
  };
  choke.set(0.5);
  R.choke = choke;

  /* ---------------- hubs / connectors ---------------- */
  const hubs = S('g');
  hubs.append(
    S('rect', { x: -588, y: 262, width: 26, height: 116, rx: 5, fill: 'url(#gCylV)', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: -604, y: 282, width: 18, height: 76, rx: 4, fill: '#8DA2B3', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: 546, y: 274, width: 22, height: 92, rx: 5, fill: 'url(#gCylV)', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: 566, y: 290, width: 16, height: 60, rx: 4, fill: '#8DA2B3', stroke: OUT, 'stroke-width': 3 }),
  );
  root.append(hubs);
  root.append(
    S('rect', { x: -700, y: 296, width: 96, height: 48, fill: '#3F5363', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: -700, y: 308, width: 96, height: 24, fill: BORE }),
    S('rect', { x: 580, y: 304, width: 90, height: 32, fill: '#3F5363', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: 580, y: 312, width: 90, height: 16, fill: BORE }));
  fill('p_out2', -700, 308, 115, 24, COL.hc);
  fill('a_out2', 560, 312, 110, 16, COL.ann);

  /* ---------------- tubing hanger aux passages (control line, cable) ---------------- */
  const aux = S('g');
  aux.append(
    S('rect', { x: 84, y: 722, width: 8, height: 84, fill: '#06202C' }),
    S('rect', { x: -96, y: 722, width: 8, height: 84, fill: '#2B2406' }));
  root.append(aux);
  const bolts = S('g', { fill: '#C9D6E0', stroke: OUT, 'stroke-width': 1.5 });
  for (let i = 0; i < 7; i++) {
    bolts.append(S('circle', { cx: -200 + i * 66.7, cy: 655, r: 7 }));
    bolts.append(S('circle', { cx: -200 + i * 66.7, cy: 700, r: 7 }));
  }
  root.append(bolts);

  /* ================= OVERLAYS (hidden until a scene reveals them) ================= */
  const hidden = (g) => { g.setAttribute('opacity', 0); g.style.visibility = 'hidden'; return g; };

  // --- crossover loop: production wing branch  ->  over the top  ->  annulus branch, XOV on right leg
  const xoPath = 'M-314 320 V-10 Q-314 -40 -284 -40 H270 Q300 -40 300 -10 V320';
  const xo = hidden(S('g'));
  const xoPipe = pipe(xo, xoPath, { outer: 36, inner: 20 });
  root.append(xo);
  R.overlays.xover = { g: xo, fillEl: xoPipe.fillEl, path: xoPath };
  V.XOV = GateValve(root, { x: 300, y: 130, bw: 22, rot: 0, mirror: true, act: 'fs', f0: 0 });
  hidden(V.XOV.g);
  R.flows.xo = Flow(root, 'M300 330 V-10 Q300 -40 270 -40 H-284 Q-314 -40 -314 -10 V312', { color: COL.ann, w: 6, gap: 20 });

  // --- chemical injection line: hub (left) -> CIV -> production bore between PMV and PWV
  const ci = hidden(S('g'));
  const ciPipe = pipe(ci, 'M-790 430 H-30', { outer: 26, inner: 12 });
  ci.append(
    S('rect', { x: -690, y: 408, width: 24, height: 44, rx: 5, fill: 'url(#gCylV)', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: -706, y: 418, width: 18, height: 24, rx: 4, fill: '#8DA2B3', stroke: OUT, 'stroke-width': 3 }));
  root.append(ci);
  R.overlays.ci = { g: ci, fillEl: ciPipe.fillEl };
  V.CIV = GateValve(root, { x: -390, y: 430, bw: 14, rot: 90, mirror: true, act: 'fs', f0: 0 });
  hidden(V.CIV.g);
  R.flows.ci = Flow(root, 'M-780 430 H-30 Q0 430 0 400', { color: COL.chem, w: 5, gap: 18 });

  // --- subsea control module + hydraulic hoses frame (SCM sits on the tree frame, right)
  const scm = hidden(S('g'));
  scm.append(
    S('rect', { x: 262, y: 586, width: 190, height: 120, rx: 10, fill: '#1C2B37', stroke: OUT, 'stroke-width': 4 }),
    S('rect', { x: 262, y: 586, width: 190, height: 26, rx: 8, fill: '#E5A22A', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: 276, y: 628, width: 60, height: 62, rx: 6, fill: '#0F1B25', stroke: '#3F5363', 'stroke-width': 2 }),
    S('circle', { cx: 372, cy: 660, r: 18, fill: '#0F1B25', stroke: '#6F879A', 'stroke-width': 3 }),
    S('circle', { cx: 372, cy: 660, r: 7, fill: '#2ED0FF' }),
    S('circle', { cx: 420, cy: 660, r: 12, fill: '#0F1B25', stroke: '#6F879A', 'stroke-width': 3 }),
    S('rect', { x: 452, y: 632, width: 22, height: 56, rx: 4, fill: 'url(#gCylV)', stroke: OUT, 'stroke-width': 2.5 }));
  root.append(scm);
  R.overlays.scm = { g: scm };

  // --- control line: SCM -> hanger passage (feeds the downhole safety valve)
  const dl = hidden(S('g'));
  const dlD = 'M262 652 H88 V806';
  dl.append(S('path', { d: dlD, fill: 'none', stroke: OUT, 'stroke-width': 11, 'stroke-linejoin': 'round' }), S('path', { d: dlD, fill: 'none', stroke: '#2ED0FF', 'stroke-width': 5, 'stroke-linejoin': 'round', opacity: 0.9 }));
  root.append(dl);
  R.overlays.dhsvLine = { g: dl, path: dlD };
  R.flows.dhsvTop = Flow(root, dlD, { color: '#2ED0FF', w: 5, gap: 18 });

  // --- pressure / temperature sensors
  const sens = hidden(S('g'));
  const sensor = (x, y, dx, name) => {
    const g = S('g', {},
      S('rect', { x: Math.min(x, x + dx) - 2, y: y - 5, width: Math.abs(dx) + 4, height: 10, fill: '#3F5363', stroke: OUT, 'stroke-width': 2 }),
      S('circle', { cx: x + dx, cy: y, r: 17, fill: '#E5A22A', stroke: OUT, 'stroke-width': 3 }),
      S('circle', { cx: x + dx, cy: y, r: 7, fill: '#2B2406' }));
    return g;
  };
  sens.append(sensor(26, 380, 50, 'ptp'), sensor(165, 410, 52, 'pta'), sensor(-346, 320, -0, 'ptd'));
  sens.lastChild.remove();                       // (third sensor omitted – keep it clean)
  root.append(sens);
  R.overlays.sensors = { g: sens };

  /* ---------------- flows ---------------- */
  const F = R.flows;
  const fl = (name, d, o) => (F[name] = Flow(root, d, { w: 8, ...o }));
  fl('p_low', 'M0 905 V530', { color: COL.hc });
  fl('p_mid', 'M0 470 V345 Q0 320 -25 320 H-186', { color: COL.hc });
  fl('p_out1', 'M-274 320 H-346', { color: COL.hc });
  fl('p_out2', 'M-454 320 H-690', { color: COL.hc });
  fl('a_low', 'M150 800 V530', { color: COL.ann, w: 5, gap: 20 });
  fl('a_mid', 'M150 470 V340', { color: COL.ann, w: 5, gap: 20 });

  R.anchors = {
    pmv: W(0, 500), psv: W(0, 110), pwv: W(-230, 320), choke: W(-400, 320), amv: W(150, 500), asv: W(150, 110), awv: W(400, 320),
    xov: W(300, 130), civ: W(-390, 430), scm: W(357, 646), hanger: W(0, 764), connector: W(0, 678), wellhead: W(0, 800),
    cap: W(0, 30), prodBore: W(0, 230), annBore: W(150, 230), outlet: W(-300, 320), hubP: W(-575, 320), hubA: W(560, 320), tree: W(0, 400),
  };
  return R;
}
