import { H, S } from '../lib/svg.js';
import { installDefs } from '../art/defs.js';
import { buildTree } from '../art/tree.js';
import { buildWell } from '../art/well.js';
export function build(root, E) {
  installDefs();
  const el = H('div', { class: 'scene', style: { background: 'linear-gradient(#08192A,#040C14)' } });
  root.append(el);
  const svg = S('svg', { viewBox: '0 0 1920 1080' });
  el.append(svg);
  const world = S('g');
  svg.append(world);
  const cam = new E.Cam(world, { wx: 0, wy: 300, sx: 960, sy: 540, k: 0.34 });
  const tree = buildTree(world);
  const well = buildWell(world);
  well.reservoir && 0;
  cam.cut(10, { wx: 0, wy: 150, sx: 960, sy: 540, k: 1.0 });
  cam.cut(20, { wx: 0, wy: 560, sx: 960, sy: 540, k: 3.0 });
  well.dhsv.open(21, 1.6);
  well.dhsv.close(25, 0.6);
  ['p_low','p_mid','p_tee','p_up','p_br1','p_br2','p_out1','p_out2'].forEach(n => tree.fills[n].to(0.2, 0.1, 0.5));
  Object.values(tree.flows).filter(f=>f.g).forEach(f => f.show(0.2, 0.2, 70));
  Object.values(well.flows).forEach(f => f.show(0.2, 0.2, 70));
  well.fills.tubing.to(0.2, 0.1, 0.5);
}
