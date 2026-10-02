// Shared gradients / filters (document-global ids) ------------------------
import { S, linGrad, radGrad } from '../lib/svg.js';

let done = false;
export function installDefs() {
  if (done) return;
  done = true;
  const svg = S('svg', { width: 0, height: 0, style: { position: 'absolute' }, 'aria-hidden': 'true' });
  const defs = S('defs');
  svg.append(defs);
  document.body.append(svg);

  // Steel – cut sections (vertical light falloff) and cylinders (horizontal roundness)
  linGrad(defs, 'gSteelV', [[0, '#7088A0'], [0.5, '#53687A'], [1, '#3A4B5A']], { x1: 0, y1: 0, x2: 0, y2: 1 });
  linGrad(defs, 'gSteelCut', [[0, '#5F7587'], [1, '#43566A']], { x1: 0, y1: 0, x2: 1, y2: 1 });
  linGrad(defs, 'gSteelDark', [[0, '#3C4E5D'], [1, '#26343F']], { x1: 0, y1: 0, x2: 0, y2: 1 });
  linGrad(defs, 'gCylH', [[0, '#27394A'], [0.28, '#6F8AA2'], [0.5, '#A9C0D3'], [0.72, '#6A859D'], [1, '#243545']], { x1: 0, y1: 0, x2: 0, y2: 1 });
  linGrad(defs, 'gCylV', [[0, '#27394A'], [0.28, '#6F8AA2'], [0.5, '#A9C0D3'], [0.72, '#6A859D'], [1, '#243545']], { x1: 0, y1: 0, x2: 1, y2: 0 });
  linGrad(defs, 'gAct', [[0, '#173B5C'], [0.3, '#3F86C4'], [0.5, '#7DBDF2'], [0.72, '#3A7DB8'], [1, '#14354F']], { x1: 0, y1: 0, x2: 0, y2: 1 });
  linGrad(defs, 'gGate', [[0, '#E4ECF2'], [0.5, '#B3C4D2'], [1, '#8497A8']], { x1: 0, y1: 0, x2: 0, y2: 1 });
  linGrad(defs, 'gOrange', [[0, '#FFB067'], [1, '#E5701A']], { x1: 0, y1: 0, x2: 0, y2: 1 });
  linGrad(defs, 'gSeabed', [[0, '#1C2A33'], [1, '#0A1218']], { x1: 0, y1: 0, x2: 0, y2: 1 });
  linGrad(defs, 'gWater', [[0, '#0E3A57'], [0.55, '#082A41'], [1, '#04121D']], { x1: 0, y1: 0, x2: 0, y2: 1 });
  linGrad(defs, 'gBore', [[0, '#04090E'], [1, '#0A1620']], { x1: 0, y1: 0, x2: 1, y2: 0 });
  radGrad(defs, 'gSpot', [[0, '#BFE9FF', 0.55], [1, '#BFE9FF', 0]]);
  radGrad(defs, 'gGlowWarm', [[0, '#FFC857', 0.8], [1, '#FFC857', 0]]);
  radGrad(defs, 'gGlowRed', [[0, '#FF3B5C', 0.85], [1, '#FF3B5C', 0]]);
  radGrad(defs, 'gGlowGreen', [[0, '#3BDB86', 0.8], [1, '#3BDB86', 0]]);
  radGrad(defs, 'gGlowCyan', [[0, '#2ED0FF', 0.8], [1, '#2ED0FF', 0]]);
  radGrad(defs, 'gGlowOr', [[0, '#FF9A3C', 0.8], [1, '#FF9A3C', 0]]);
  radGrad(defs, 'gGlowYel', [[0, '#FFC857', 0.8], [1, '#FFC857', 0]]);

  // Filters
  defs.append(
    S('filter', { id: 'fGlow', x: '-60%', y: '-60%', width: '220%', height: '220%' },
      S('feGaussianBlur', { stdDeviation: 7, result: 'b' }),
      S('feMerge', {}, S('feMergeNode', { in: 'b' }), S('feMergeNode', { in: 'SourceGraphic' }))),
    S('filter', { id: 'fBlur4', x: '-50%', y: '-50%', width: '200%', height: '200%' }, S('feGaussianBlur', { stdDeviation: 4 })),
    S('filter', { id: 'fBlur10', x: '-50%', y: '-50%', width: '200%', height: '200%' }, S('feGaussianBlur', { stdDeviation: 10 })),
    S('filter', { id: 'fShadow', x: '-20%', y: '-20%', width: '150%', height: '160%' },
      S('feDropShadow', { dx: 0, dy: 10, stdDeviation: 12, 'flood-color': '#000', 'flood-opacity': 0.55 }))
  );

  // Diagonal hatch for cut surfaces
  defs.append(
    S('pattern', { id: 'pHatch', width: 12, height: 12, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)' },
      S('rect', { width: 12, height: 12, fill: 'transparent' }),
      S('line', { x1: 0, y1: 0, x2: 0, y2: 12, stroke: 'rgba(255,255,255,.10)', 'stroke-width': 3 })),
    S('pattern', { id: 'pCement', width: 14, height: 14, patternUnits: 'userSpaceOnUse' },
      S('rect', { width: 14, height: 14, fill: '#55606A' }),
      S('circle', { cx: 3, cy: 4, r: 1.4, fill: '#7B8791' }), S('circle', { cx: 10, cy: 9, r: 1.6, fill: '#3F4952' }), S('circle', { cx: 11, cy: 2, r: 1, fill: '#8A96A0' })),
    S('pattern', { id: 'pRock', width: 40, height: 40, patternUnits: 'userSpaceOnUse' },
      S('rect', { width: 40, height: 40, fill: '#3A332D' }),
      S('circle', { cx: 8, cy: 10, r: 3.5, fill: '#4A4037' }), S('circle', { cx: 28, cy: 6, r: 2.5, fill: '#2E2824' }),
      S('circle', { cx: 18, cy: 28, r: 4, fill: '#463C34' }), S('circle', { cx: 34, cy: 32, r: 2.5, fill: '#2B2521' })),
    S('pattern', { id: 'pSand', width: 26, height: 26, patternUnits: 'userSpaceOnUse' },
      S('rect', { width: 26, height: 26, fill: '#6B4A25' }),
      S('circle', { cx: 6, cy: 7, r: 2.6, fill: '#FF9A3C', opacity: 0.8 }), S('circle', { cx: 18, cy: 5, r: 1.8, fill: '#FF9A3C', opacity: 0.6 }),
      S('circle', { cx: 12, cy: 19, r: 2.2, fill: '#FF9A3C', opacity: 0.7 }), S('circle', { cx: 23, cy: 21, r: 1.6, fill: '#FF9A3C', opacity: 0.5 }))
  );
  return defs;
}
