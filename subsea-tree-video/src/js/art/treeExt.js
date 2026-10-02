// Vertical subsea tree – EXTERIOR view (same geometry as the cut-away) ---------------
// Used for the cold open; cross-faded / wiped into the cut-away for "let's open one up".
import { S } from '../lib/svg.js';
import { GateValve } from './valve.js';
import { SEABED_TY } from './tree.js';

const OUT = '#08111A';

function tube(parent, d, w, base = '#4A5F70', hi = 'rgba(190,215,235,.45)') {
  parent.append(
    S('path', { d, fill: 'none', stroke: OUT, 'stroke-width': w + 7, 'stroke-linejoin': 'round', 'stroke-linecap': 'butt' }),
    S('path', { d, fill: 'none', stroke: base, 'stroke-width': w, 'stroke-linejoin': 'round', 'stroke-linecap': 'butt' }),
    S('path', { d, fill: 'none', stroke: hi, 'stroke-width': Math.max(2, w * 0.28), 'stroke-linejoin': 'round', 'stroke-linecap': 'butt', transform: 'translate(0 -1)' }));
}
function block(parent, rects, fill) {
  rects.forEach((r) => parent.append(S('rect', { ...r, fill: OUT, stroke: OUT, 'stroke-width': 7, 'stroke-linejoin': 'round' })));
  rects.forEach((r) => parent.append(S('rect', { ...r, fill })));
}

export function buildTreeExterior(parent) {
  const defs = S('defs');
  defs.append(
    S('linearGradient', { id: 'gExtBlock', gradientUnits: 'userSpaceOnUse', x1: -130, y1: 0, x2: 205, y2: 0 },
      S('stop', { offset: 0, 'stop-color': '#17232E' }), S('stop', { offset: 0.3, 'stop-color': '#5A7286' }), S('stop', { offset: 0.5, 'stop-color': '#8CA5B8' }), S('stop', { offset: 0.75, 'stop-color': '#4A6074' }), S('stop', { offset: 1, 'stop-color': '#131E28' })),
    S('linearGradient', { id: 'gExtWell', gradientUnits: 'userSpaceOnUse', x1: -232, y1: 0, x2: 232, y2: 0 },
      S('stop', { offset: 0, 'stop-color': '#15212B' }), S('stop', { offset: 0.35, 'stop-color': '#4F687B' }), S('stop', { offset: 0.55, 'stop-color': '#7E98AC' }), S('stop', { offset: 1, 'stop-color': '#121C25' })),
    S('linearGradient', { id: 'gExtFrame', x1: 0, y1: 0, x2: 1, y2: 0 },
      S('stop', { offset: 0, 'stop-color': '#20303D' }), S('stop', { offset: 0.5, 'stop-color': '#4E6679' }), S('stop', { offset: 1, 'stop-color': '#1B2833' })),
  );
  const root = S('g', { transform: `translate(0 ${-SEABED_TY})` });
  root.append(defs);
  parent.append(root);
  const R = { root, valves: {} };

  // guide frame / mudmat ------------------------------------------------
  const frame = S('g');
  const rail = (x1, y1, x2, y2, w = 13) => frame.append(
    S('line', { x1, y1, x2, y2, stroke: OUT, 'stroke-width': w + 6, 'stroke-linecap': 'round' }),
    S('line', { x1, y1, x2, y2, stroke: '#2E4152', 'stroke-width': w, 'stroke-linecap': 'round' }),
    S('line', { x1, y1, x2, y2, stroke: 'rgba(170,200,225,.30)', 'stroke-width': w * 0.3, 'stroke-linecap': 'round' }));
  frame.append(S('rect', { x: -640, y: 884, width: 1280, height: 26, rx: 6, fill: '#1B2A36', stroke: OUT, 'stroke-width': 4 }));
  rail(-600, 884, -600, 120); rail(600, 884, 600, 120);
  rail(-600, 120, 600, 120); rail(-600, 884, -300, 884); rail(300, 884, 600, 884);
  rail(-600, 520, -250, 884, 9); rail(600, 520, 250, 884, 9); rail(-600, 120, -420, 520, 9); rail(600, 120, 420, 520, 9);
  // padeyes on the frame
  [-600, 600].forEach((x) => frame.append(S('circle', { cx: x, cy: 112, r: 15, fill: 'none', stroke: '#E5701A', 'stroke-width': 7 })));
  root.append(frame);

  // wellhead + connector -----------------------------------------------
  block(root, [{ x: -215, y: 712, width: 430, height: 200, rx: 22 }], 'url(#gExtWell)');
  block(root, [{ x: -232, y: 636, width: 464, height: 84, rx: 16 }], 'url(#gExtWell)');
  const bolts = S('g', { fill: '#B9C8D4', stroke: OUT, 'stroke-width': 2 });
  for (let i = 0; i < 7; i++) { bolts.append(S('circle', { cx: -200 + i * 66.7, cy: 655, r: 8 })); bolts.append(S('circle', { cx: -200 + i * 66.7, cy: 700, r: 8 })); }
  root.append(bolts);

  // pipes: production outlet (left), annulus outlet (right), crossover arch, chemical line --------
  tube(root, 'M-120 320 H-560', 62, '#43586A');
  tube(root, 'M190 320 H540', 36, '#43586A');
  tube(root, 'M-314 320 V-10 Q-314 -40 -284 -40 H270 Q300 -40 300 -10 V320', 34, '#4A5F70');
  tube(root, 'M-690 430 H-130', 24, '#3E5264');
  // hubs
  root.append(
    S('rect', { x: -588, y: 262, width: 26, height: 116, rx: 5, fill: 'url(#gCylV)', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: -604, y: 282, width: 18, height: 76, rx: 4, fill: '#8DA2B3', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: 546, y: 274, width: 22, height: 92, rx: 5, fill: 'url(#gCylV)', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: 566, y: 290, width: 16, height: 60, rx: 4, fill: '#8DA2B3', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: -700, y: 296, width: 96, height: 48, fill: '#3F5363', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: 580, y: 304, width: 90, height: 32, fill: '#3F5363', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: -690, y: 408, width: 24, height: 44, rx: 5, fill: 'url(#gCylV)', stroke: OUT, 'stroke-width': 3 }));

  // valve blocks on the branches + main block ---------------------------
  block(root, [{ x: -280, y: 236, width: 100, height: 168, rx: 10 }], 'url(#gExtBlock)');
  block(root, [{ x: 372, y: 264, width: 56, height: 112, rx: 8 }], 'url(#gExtBlock)');
  block(root, [{ x: -452, y: 262, width: 104, height: 116, rx: 10 }, { x: -430, y: 196, width: 60, height: 74, rx: 8 }], 'url(#gExtBlock)');
  block(root, [{ x: -130, y: 48, width: 335, height: 600, rx: 18 }, { x: -62, y: 10, width: 124, height: 50, rx: 24 }, { x: 130, y: 30, width: 40, height: 26, rx: 8 }], 'url(#gExtBlock)');
  root.append(
    S('rect', { x: -130, y: 196, width: 335, height: 9, fill: 'rgba(0,0,0,.28)' }), S('rect', { x: -130, y: 598, width: 335, height: 9, fill: 'rgba(0,0,0,.28)' }),
    S('rect', { x: -130, y: 420, width: 335, height: 6, fill: 'rgba(0,0,0,.22)' }),
    // flange rings with bolts
    ...[[190, 24], [410, 22], [592, 24]].flatMap(([y, h]) => [
      S('rect', { x: -146, y, width: 367, height: h, rx: 5, fill: '#33485A', stroke: OUT, 'stroke-width': 3 }),
      S('rect', { x: -146, y, width: 367, height: 4, rx: 2, fill: 'rgba(210,230,245,.40)' }),
      ...Array.from({ length: 9 }, (_, i) => S('circle', { cx: -122 + i * 40.5, cy: y + h / 2 + 1, r: 4.2, fill: '#B9C8D4', stroke: OUT, 'stroke-width': 1.2 })),
    ]),
    // vertical block seams
    S('rect', { x: -52, y: 205, width: 4, height: 215, fill: 'rgba(0,0,0,.30)' }), S('rect', { x: 92, y: 205, width: 4, height: 215, fill: 'rgba(0,0,0,.30)' }),
    S('rect', { x: -52, y: 426, width: 4, height: 166, fill: 'rgba(0,0,0,.30)' }), S('rect', { x: 92, y: 426, width: 4, height: 166, fill: 'rgba(0,0,0,.30)' }),
    // ROV torque-tool buckets
    ...[[-92, 300], [150, 260], [-92, 540], [158, 380]].flatMap(([x, y]) => [
      S('circle', { cx: x, cy: y, r: 19, fill: '#0C1620', stroke: '#E5A22A', 'stroke-width': 4 }),
      S('path', { d: `M${x - 7} ${y} l3.5 -6 h7 l3.5 6 l-3.5 6 h-7 z`, fill: '#8FA5B6' })]),
    S('path', { d: 'M-20 14 q0 -34 20 -34 q20 0 20 34', fill: 'none', stroke: OUT, 'stroke-width': 11, 'stroke-linecap': 'round' }),
    S('path', { d: 'M-20 14 q0 -34 20 -34 q20 0 20 34', fill: 'none', stroke: '#E5701A', 'stroke-width': 6, 'stroke-linecap': 'round' }),
    // choke actuator
    S('rect', { x: -436, y: 128, width: 72, height: 78, rx: 8, fill: 'url(#gAct)', stroke: '#0E2236', 'stroke-width': 2.5 }),
    S('rect', { x: -424, y: 108, width: 48, height: 24, rx: 6, fill: '#2A3B49', stroke: '#0E2236', 'stroke-width': 2 }));

  // actuators --------------------------------------------------------------
  const V = R.valves;
  const mk = (o) => GateValve(root, { ext: true, ...o });
  V.PMV = mk({ x: 0, y: 500, bw: 52, act: 'fs' });
  V.PSV = mk({ x: 0, y: 110, bw: 52, act: 'manual' });
  V.AMV = mk({ x: 150, y: 500, bw: 30, act: 'fs', mirror: true });
  V.ASV = mk({ x: 150, y: 110, bw: 30, act: 'manual', mirror: true });
  V.PWV = mk({ x: -230, y: 320, bw: 38, rot: 90, act: 'fs' });
  V.AWV = mk({ x: 400, y: 320, bw: 22, rot: 90, act: 'fs' });
  V.XOV = mk({ x: 300, y: 130, bw: 22, mirror: true, act: 'fs' });
  V.CIV = mk({ x: -390, y: 430, bw: 14, rot: 90, mirror: true, act: 'fs' });

  // subsea control module + hydraulic bundle -------------------------------
  root.append(
    S('rect', { x: 262, y: 586, width: 190, height: 120, rx: 10, fill: '#1C2B37', stroke: OUT, 'stroke-width': 4 }),
    S('rect', { x: 262, y: 586, width: 190, height: 26, rx: 8, fill: '#E5A22A', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: 276, y: 628, width: 60, height: 62, rx: 6, fill: '#0F1B25', stroke: '#3F5363', 'stroke-width': 2 }),
    S('circle', { cx: 372, cy: 660, r: 18, fill: '#0F1B25', stroke: '#6F879A', 'stroke-width': 3 }),
    S('rect', { x: 452, y: 632, width: 22, height: 56, rx: 4, fill: 'url(#gCylV)', stroke: OUT, 'stroke-width': 2.5 }));
  const hoses = [
    'M262 640 C 120 640 60 620 10 560', 'M262 650 C 80 700 -140 640 -260 540', 'M262 630 C 200 560 230 520 290 500',
    'M262 660 C 40 760 -300 700 -390 470', 'M262 620 C 120 420 -60 300 -226 270',
  ];
  hoses.forEach((d) => root.append(S('path', { d, fill: 'none', stroke: OUT, 'stroke-width': 7, 'stroke-linecap': 'round' }), S('path', { d, fill: 'none', stroke: '#2ED0FF', 'stroke-width': 3, 'stroke-linecap': 'round', opacity: 0.8 })));
  return R;
}
