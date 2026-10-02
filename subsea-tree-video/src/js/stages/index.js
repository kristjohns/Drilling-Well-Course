// Stage registry – built strictly in chronological order (valve/camera cursors depend on it).
import { build as intro } from './intro.js';
import { build as goals } from './goals.js';
import { build as system } from './system.js';
import { build as jobs } from './jobs.js';
import { createTreeStage } from './treeStage.js';
import { build as anatomy } from './anatomy.js';
import { build as gate } from './gate.js';
import { build as valves } from './valves.js';
import { build as control } from './control.js';
import { build as barriers } from './barriers.js';
import { build as esd } from './esd.js';
import { build as types } from './types.js';
import { build as ncs } from './ncs.js';
import { build as quiz } from './quiz.js';
import { build as recap } from './recap.js';
import { build as test } from './test.js';

export function buildStages(root, hud, E) {
  const only = new URLSearchParams(location.search).get('only');
  if (only === 'test') return test(root, E);
  const T = E.T;
  intro(root, E);
  goals(root, E);
  system(root, E);
  jobs(root, E);
  // continuous tree stage: anatomy .. dhsv, then again for esd (control + barriers are standalone scenes between)
  const ctx = createTreeStage(root, E, [[T.scene('anatomy').start - 0.3, T.scene('dhsv').end + 0.3], [T.scene('esd').start - 0.3, T.scene('esd').end + 0.3]]);
  anatomy(ctx);
  gate(ctx);
  valves(ctx);
  control(root, E);
  barriers(root, E);
  esd(ctx);
  types(root, E);
  ncs(root, E);
  quiz(root, E);
  recap(root, E);
}
