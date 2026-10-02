// Well section below the tree (world coords: seabed y=0, +y down) -------------------
// Compressed depth (not to scale): conductor shoe 300, surface shoe 800, DHSV ~560,
// break 900-1000, packer 1250, perforations 1600-1700, reservoir 1500-1900.
import { S, coilD } from '../lib/svg.js';
import { tl, Flow, sfx } from '../engine.js';

const OUT = '#0B141C';
export const WELL = { dhsvY: 560, packerY: 1250, perfY: 1650, resTop: 1500, resBot: 1950, breakY: 900 };

export function buildWell(parent) {
  const root = S('g');
  parent.append(root);
  const R = { root, fills: {}, flows: {} };

  /* formation */
  root.append(
    S('rect', { x: -1100, y: 12, width: 2200, height: 2100, fill: 'url(#pRock)' }),
    S('rect', { x: -1100, y: 12, width: 2200, height: 2100, fill: 'url(#gSeabed)', opacity: 0.55 }));
  // reservoir lens
  const res = S('g');
  res.append(
    S('path', { d: 'M-1100 1560 C-700 1480 -300 1500 0 1490 C300 1500 700 1480 1100 1560 L1100 1960 C700 2010 300 1990 0 2000 C-300 1990 -700 2010 -1100 1960 Z', fill: 'url(#pSand)', stroke: '#8A5A22', 'stroke-width': 3 }),
    S('path', { d: 'M-1100 1560 C-700 1480 -300 1500 0 1490 C300 1500 700 1480 1100 1560', fill: 'none', stroke: '#E5A04C', 'stroke-width': 4, opacity: 0.7 }));
  root.append(res);
  R.reservoir = res;
  // cap rock band above the reservoir
  root.append(S('rect', { x: -1100, y: 1380, width: 2200, height: 90, fill: 'rgba(10,18,26,.35)' }));

  /* casings & cement */
  const walls = S('g');
  const wall = (xL, xR, w, y0, y1, col = '#6F879A') => {
    [[-xR, -xL], [xL, xR]].forEach(([a, b]) => {
      walls.append(S('rect', { x: a, y: y0, width: b - a, height: y1 - y0, fill: col, stroke: OUT, 'stroke-width': 2 }));
    });
  };
  const cement = (xL, xR, y0, y1) => [[-xR, -xL], [xL, xR]].forEach(([a, b]) => walls.append(S('rect', { x: a, y: y0, width: b - a, height: y1 - y0, fill: 'url(#pCement)' })));
  cement(232, 248, 12, 330); wall(218, 232, 14, 12, 320, '#5F7587');
  cement(208, 220, 320, 880); wall(196, 208, 12, 12, 880, '#68809A');
  cement(184, 196, 880, 1700); wall(172, 184, 12, 12, 1700, '#7A93A8');
  // casing shoes
  [[225, 320], [202, 880], [178, 1700]].forEach(([x, y]) => [-1, 1].forEach((sg) =>
    walls.append(S('path', { d: `M${sg * (x - 13)} ${y} h${sg * 26} l${-sg * 4} 14 h${-sg * 18} z`, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 1.5 }))));
  root.append(walls);
  R.walls = walls;

  /* annulus (tubing x production casing) */
  const ann = S('g');
  const annL = S('rect', { x: -172, y: -94, width: 132, height: WELL.packerY + 94, fill: '#34D8A8', opacity: 0.16 });
  const annR = S('rect', { x: 40, y: -94, width: 132, height: WELL.packerY + 94, fill: '#34D8A8', opacity: 0.16 });
  ann.append(annL, annR);
  root.append(ann);
  R.fills.annulus = { els: [annL, annR] };
  // casing-head cavity under the hanger
  root.append(S('rect', { x: -172, y: -94, width: 344, height: 106, fill: '#071019', opacity: 0.0 }));

  /* tubing */
  const tub = S('g');
  tub.append(
    S('rect', { x: -40, y: -94, width: 14, height: 1840, fill: '#B3C4D2', stroke: OUT, 'stroke-width': 2 }),
    S('rect', { x: 26, y: -94, width: 14, height: 1840, fill: '#B3C4D2', stroke: OUT, 'stroke-width': 2 }),
    S('rect', { x: -26, y: -94, width: 52, height: 1840, fill: '#050B11' }));
  root.append(tub);
  const tubFill = S('rect', { x: -26, y: -94, width: 52, height: 1840, fill: 'url(#gFluidHC)', opacity: 0 });
  root.append(tubFill);
  R.fills.tubing = { el: tubFill, to(t, d = 0.6, op = 0.5) { tl.to(tubFill, { opacity: op, duration: d, ease: 'power1.out' }, t); } };

  /* packer */
  const packer = S('g');
  [[-172, -40], [40, 172]].forEach(([a, b]) => packer.append(
    S('rect', { x: a, y: WELL.packerY, width: b - a, height: 56, fill: '#1B232B', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: a + 6, y: WELL.packerY + 10, width: b - a - 12, height: 36, rx: 6, fill: '#2C3A46' }),
    S('rect', { x: a, y: WELL.packerY - 16, width: b - a, height: 16, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 2 }),
    S('rect', { x: a, y: WELL.packerY + 56, width: b - a, height: 16, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 2 })));
  root.append(packer);
  R.packer = packer;

  /* perforations + reservoir fluid below packer */
  const perfs = S('g', { fill: '#FFB067' });
  for (let i = 0; i < 6; i++) [-1, 1].forEach((sg) => perfs.append(S('rect', { x: sg > 0 ? 172 : -208, y: 1600 + i * 24, width: 36, height: 8, rx: 3 })));
  root.append(perfs);
  const resFluid = S('g', { opacity: 0.22, fill: '#FF9A3C' },
    S('rect', { x: -172, y: WELL.packerY + 72, width: 132, height: 700 }), S('rect', { x: 40, y: WELL.packerY + 72, width: 132, height: 700 }));
  root.append(resFluid);
  R.resFluid = resFluid;

  /* break symbol (compressed depth) */
  const brk = S('g');
  const band = S('path', { d: 'M-1100 920 ' + Array.from({ length: 74 }, (_, i) => `l30 ${i % 2 ? 18 : -18}`).join(' ') + ' L1100 1010 ' + Array.from({ length: 74 }, (_, i) => `l-30 ${i % 2 ? 18 : -18}`).join(' ') + ' Z', fill: '#071019', stroke: '#6F879A', 'stroke-width': 3, opacity: 0.96 });
  brk.append(band);
  const brkLab = S('text', { x: 0, y: 972, 'text-anchor': 'middle', fill: '#8FA6B8', 'font-size': 26, 'font-weight': 600, 'letter-spacing': '0.18em', text: 'NOT TO SCALE' });
  brk.append(brkLab);
  // re-draw the tubing + casings across the break so the strings read as continuous
  const cont = S('g');
  cont.append(
    S('rect', { x: -40, y: 925, width: 14, height: 80, fill: '#B3C4D2', stroke: OUT, 'stroke-width': 2 }),
    S('rect', { x: 26, y: 925, width: 14, height: 80, fill: '#B3C4D2', stroke: OUT, 'stroke-width': 2 }));
  root.append(brk, cont);
  R.break = brk;

  /* control line from hanger to DHSV */
  const cl = S('g');
  const clPath = `M88 -94 V${WELL.dhsvY - 64} H44`;
  cl.append(
    S('path', { d: clPath, fill: 'none', stroke: OUT, 'stroke-width': 11, 'stroke-linejoin': 'round' }),
    S('path', { d: clPath, fill: 'none', stroke: '#2ED0FF', 'stroke-width': 5, 'stroke-linejoin': 'round', opacity: 0.9 }));
  root.append(cl);
  R.ctrlLine = { g: cl, path: clPath };

  /* DHSV */
  R.dhsv = buildDHSV(root, { x: 0, y: WELL.dhsvY });

  /* flows */
  R.flows.tubLow = Flow(root, `M0 1720 V${WELL.dhsvY + 80}`, { color: '#FF9A3C', w: 8 });
  R.flows.tubHigh = Flow(root, `M0 ${WELL.dhsvY - 120} V-60`, { color: '#FF9A3C', w: 8 });
  R.flows.inL = Flow(root, 'M-520 1680 C-380 1680 -250 1700 -30 1706', { color: '#FF9A3C', w: 7 });
  R.flows.inR = Flow(root, 'M520 1680 C380 1680 250 1700 30 1706', { color: '#FF9A3C', w: 7 });
  R.flows.ctrl = Flow(root, clPath, { color: '#2ED0FF', w: 5, gap: 18 });
  return R;
}

/** Tubing-retrievable surface-controlled safety valve (flapper type), cut-away.
 *  f=0 closed (spring up, flapper shut)  ..  f=1 open (hydraulic pressure holds flow tube down). */
export function buildDHSV(parent, { x = 0, y = 0 } = {}) {
  const root = S('g', { transform: `translate(${x} ${y})` });
  parent.append(root);
  const H0 = -150, H1 = 110;                               // housing y range (local)
  const body = S('g');
  body.append(
    S('rect', { x: -70, y: H0, width: 140, height: H1 - H0, rx: 8, fill: '#A9BBCA', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: -70, y: H0, width: 140, height: H1 - H0, rx: 8, fill: 'url(#pHatch)', opacity: 0.6 }),
    S('rect', { x: -26, y: H0 - 2, width: 52, height: H1 - H0 + 4, fill: '#050B11' }));   // bore
  // hydraulic chamber (right side) & spring chamber
  const chamber = S('rect', { x: 34, y: H0 + 22, width: 28, height: 150, fill: '#06101A', stroke: OUT, 'stroke-width': 2 });
  body.append(chamber);
  // port from outside
  body.append(S('rect', { x: 62, y: H0 + 30, width: 24, height: 14, fill: '#06202C', stroke: OUT, 'stroke-width': 2 }));
  root.append(body);
  const fluid = S('rect', { x: 36, y: H0 + 24, width: 24, height: 10, fill: '#2ED0FF', opacity: 0.6 });
  const spring = S('path', { d: '', fill: 'none', stroke: '#FFC857', 'stroke-width': 3.2, 'stroke-linejoin': 'round' });
  const piston = S('rect', { x: 34, y: H0 + 24, width: 28, height: 9, fill: '#EAF1F6', stroke: OUT, 'stroke-width': 1.6 });
  // flow tube (two thin walls) – moves down when open
  const ft = S('g');
  ft.append(
    S('rect', { x: -33, y: 0, width: 9, height: 82, fill: '#D6E1EA', stroke: OUT, 'stroke-width': 1.8 }),
    S('rect', { x: 24, y: 0, width: 9, height: 82, fill: '#D6E1EA', stroke: OUT, 'stroke-width': 1.8 }),
    S('rect', { x: 24, y: -4, width: 38, height: 8, fill: '#D6E1EA', stroke: OUT, 'stroke-width': 1.6 }));       // arm to piston
  // flapper + hinge + seat
  const flap = S('g', { transform: 'translate(-26 70)' });
  const plate = S('rect', { x: 0, y: -5, width: 54, height: 10, rx: 3, fill: 'url(#gGate)', stroke: OUT, 'stroke-width': 2 });
  flap.append(plate);
  const seat = S('g', { fill: '#C4D2DD', stroke: OUT, 'stroke-width': 1.5 }, S('rect', { x: -30, y: 76, width: 12, height: 8 }), S('rect', { x: 18, y: 76, width: 12, height: 8 }));
  const hinge = S('circle', { cx: -26, cy: 70, r: 6, fill: '#EAF1F6', stroke: OUT, 'stroke-width': 2 });
  const fillBelow = S('rect', { x: -26, y: 76, width: 52, height: 40, fill: 'url(#gFluidHC)', opacity: 0.5 });
  const fillAbove = S('rect', { x: -26, y: H0, width: 52, height: 220, fill: 'url(#gFluidHC)', opacity: 0 });
  root.append(fillBelow, fillAbove, spring, fluid, piston, ft, seat, flap, hinge);

  const api = {
    g: root, cur: 0, fluidAbove: fillAbove,
    // port position in world coordinates (where the control line arrives)
    portWorld: [x + 86, y + H0 + 37],
    set(f) {
      const dz = 92 * f;
      const py = H0 + 24 + dz;
      piston.setAttribute('y', py.toFixed(2));
      fluid.setAttribute('height', Math.max(4, py - (H0 + 24) + 6).toFixed(2));
      ft.setAttribute('transform', `translate(0 ${(H0 + 28 + dz).toFixed(2)})`);
      spring.setAttribute('d', coilD(48, py + 9, 48, H0 + 172, 6, 9));
      const open = Math.min(1, Math.max(0, (f - 0.55) / 0.45));
      flap.setAttribute('transform', `translate(-26 70) rotate(${(open * 92).toFixed(2)})`);
      fillAbove.setAttribute('opacity', (0.5 * open).toFixed(3));
    },
    to(t, d, f, ease = 'power2.inOut') {
      const p = { f: api.cur };
      if (Math.abs(f - api.cur) > 0.3 && d >= 0.2) sfx(t, f > api.cur ? 'valveOpen' : 'valveClose', 1, { d, auto: true, deep: true });
      tl.fromTo(p, { f: api.cur }, { f, duration: Math.max(0.001, d), ease, onUpdate: () => api.set(p.f), immediateRender: false }, t);
      api.cur = f;
      return api;
    },
    open(t, d = 1.6) { return api.to(t, d, 1, 'power2.inOut'); },
    close(t, d = 0.55) { return api.to(t, d, 0, 'power3.in'); },
  };
  api.set(0);
  return api;
}
