// Scene 16 – How the valves are controlled (356 – 404 s) -----------------------------------
import { H, S, rng } from '../lib/svg.js';
import { makeScene, BLUEPRINT } from '../lib/scene.js';
import { installDefs } from '../art/defs.js';
import { GateValve } from '../art/valve.js';
import { miniTree } from '../art/system.js';
import { rov } from '../art/rov.js';
import { tag, leader, ring } from '../lib/annot.js';
import { gauge } from '../lib/ui.js';

const YEL = '#FFC857', CY = '#2ED0FF', WH = '#EEF4F9', VI = '#BC8FFF', OR = '#FF9A3C';

export function build(root, E) {
  const { T, tl, gsap, show, hide, fadeIn, fadeOut, sfx, animate, Flow } = E;
  installDefs();
  const sc = T.scene('control');
  const w = (id, word, n = 0) => T.word('control.' + id, word, n);
  const bt = (id) => T.beat('control.' + id);
  const tB = bt('b3').start;

  /* ------------------------------------------------------------------ Part A: overview */
  const A_ = makeScene(root, E, 'control', { t0: sc.start, t1: tB, pad: 0.3 });
  const { el: elA, svg: svgA } = A_;
  const kick = H('div', { class: 'kicker abs', style: { left: '96px', top: '150px', color: YEL }, text: 'Control system' });
  const q = H('div', { class: 'h2 abs', style: { left: '96px', top: '188px' }, html: 'How do the valves <span style="color:var(--warn)">know</span> what to do?' });
  elA.append(kick, q);
  show(kick, bt('b1').start - 0.1, 0.6); show(q, bt('b1').start, 0.7);

  // host panel (left)
  const hostW = S('g', { transform: 'translate(96 392)' });
  const hostG = S('g');
  hostW.append(hostG);
  svgA.append(hostW);
  hostG.append(
    S('rect', { width: 470, height: 360, rx: 24, fill: 'rgba(8,26,42,.86)', stroke: 'rgba(170,200,225,.3)', 'stroke-width': 1.8 }),
    S('text', { x: 28, y: 46, fill: YEL, 'font-size': 20, 'font-weight': 800, 'letter-spacing': '0.16em', text: 'HOST  /  ONSHORE' }),
    S('rect', { x: 28, y: 70, width: 290, height: 190, rx: 12, fill: '#06101A', stroke: '#51677A', 'stroke-width': 3 }),
    S('text', { x: 173, y: 296, 'text-anchor': 'middle', fill: WH, 'font-size': 20, 'font-weight': 700, 'letter-spacing': '0.08em', text: 'MASTER CONTROL STATION' }));
  // monitor content (waveform + valve lines)
  const mon = S('g');
  [0, 1, 2, 3].forEach((i) => mon.append(S('rect', { x: 48, y: 92 + i * 38, width: 120 + (i % 2) * 40, height: 10, rx: 5, fill: i === 1 ? '#3BDB86' : '#2B4660' })));
  mon.append(S('path', { d: 'M190 230 l20 -34 l22 22 l24 -52 l20 40 l20 -16', fill: 'none', stroke: '#3BDB86', 'stroke-width': 4, 'stroke-linejoin': 'round' }));
  hostG.append(mon);
  hostG.append(
    S('rect', { x: 340, y: 70, width: 100, height: 82, rx: 10, fill: '#13263A', stroke: CY, 'stroke-width': 3 }), S('text', { x: 390, y: 118, 'text-anchor': 'middle', fill: CY, 'font-size': 26, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: 'HPU' }),
    S('rect', { x: 340, y: 178, width: 100, height: 82, rx: 10, fill: '#2A2410', stroke: YEL, 'stroke-width': 3 }), S('text', { x: 390, y: 226, 'text-anchor': 'middle', fill: YEL, 'font-size': 26, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: 'EPU' }),
    S('text', { x: 390, y: 172, 'text-anchor': 'middle', fill: '#9FB4C6', 'font-size': 13, 'font-weight': 600, text: 'hydraulic power' }), S('text', { x: 390, y: 280, 'text-anchor': 'middle', fill: '#9FB4C6', 'font-size': 13, 'font-weight': 600, text: 'electric power' }));
  show(hostG, bt('b2').start - 0.2, 0.8, { x: -40, y: 0 });

  // tree + SCM (right)
  const trW = S('g', { transform: 'translate(1500 840)' });
  const trG = S('g');
  trW.append(trG);
  svgA.append(trW);
  // cross-section: control room on land (left) -> shoreline -> sea -> seabed (right)
  const seabedA = S('g');
  const LAND = 'M0 770 H560 C650 770 690 846 790 846 H1920 V1080 H0 Z';
  seabedA.append(
    S('g', { mask: 'url(#mSeaA)' }, S('rect', { x: 560, y: 300, width: 1360, height: 550, fill: 'url(#gSeaA)' }),
    S('path', { d: 'M560 300 q30 -12 60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0', fill: 'none', stroke: 'rgba(111,182,224,.55)', 'stroke-width': 3 })),
    S('path', { d: LAND, fill: 'url(#gSeabed)' }), S('path', { d: LAND.replace(/ V1080 H0 Z$/, ''), fill: 'none', stroke: '#4A5A66', 'stroke-width': 3 }));
  svgA.insertBefore(S('defs', {}, S('linearGradient', { id: 'gSeaA', x1: 0, y1: 0, x2: 0, y2: 1 }, S('stop', { offset: 0, 'stop-color': '#3C86D6', 'stop-opacity': 0.05 }), S('stop', { offset: 1, 'stop-color': '#0E3A57', 'stop-opacity': 0.42 })),
    S('linearGradient', { id: 'gFadeXA', x1: 0, y1: 0, x2: 1, y2: 0 }, S('stop', { offset: 0, 'stop-color': '#000' }), S('stop', { offset: 0.2, 'stop-color': '#fff' }), S('stop', { offset: 1, 'stop-color': '#fff' })),
    S('mask', { id: 'mSeaA', maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: 1920, height: 1080 }, S('rect', { x: 560, y: 280, width: 1360, height: 580, fill: 'url(#gFadeXA)' }))), svgA.firstChild.nextSibling);
  svgA.insertBefore(seabedA, svgA.firstChild.nextSibling.nextSibling);
  const TS = 3.3;
  const mt = S('g', { transform: `scale(${TS})` });
  trG.append(mt);
  miniTree(mt, { scale: 1 });
  const scm = S('g', { transform: 'translate(-300 -200)' });
  const scmI = S('g');
  scm.append(scmI);
  scmI.append(S('rect', { width: 150, height: 96, rx: 10, fill: '#1C2B37', stroke: '#0B141C', 'stroke-width': 4 }), S('rect', { width: 150, height: 22, rx: 8, fill: '#E5A22A' }),
    S('text', { x: 75, y: 62, 'text-anchor': 'middle', fill: WH, 'font-size': 26, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: 'SCM' }),
    S('text', { x: 75, y: 84, 'text-anchor': 'middle', fill: '#9FB4C6', 'font-size': 13, 'font-weight': 600, text: 'control module' }));
  trG.append(scm);
  show(trG, bt('b1').start + 0.4, 0.8, { y: 40 });
  // "?" bubbles over the actuators
  const qs = S('g');
  [[-92, -190], [-8, -168], [54, -150]].forEach(([x, y], i) => {
    const g = S('g', { transform: `translate(${x * TS} ${y * TS * 0.92})` });
    const gi = S('g');
    g.append(gi);
    gi.append(S('circle', { r: 26, fill: '#FFC857', stroke: '#0B141C', 'stroke-width': 3 }), S('text', { x: 0, y: 12, 'text-anchor': 'middle', fill: '#0B141C', 'font-size': 38, 'font-weight': 800, text: '?' }));
    trG.append(g);
    tl.fromTo(gi, { scale: 0, svgOrigin: '0 0' }, { scale: 1, duration: 0.45, ease: 'back.out(3)', immediateRender: true }, w('b1', 'valves') + i * 0.12);
    tl.to(gi, { scale: 0, duration: 0.3, svgOrigin: '0 0' }, w('b2', 'tree') - 0.2);
  });
  // no brain
  const brain = S('g', { transform: 'translate(1180 470)' });
  const brainI = S('g');
  brain.append(brainI);
  brainI.append(S('circle', { cx: -26, cy: 0, r: 30, fill: '#EEB6C8', stroke: '#0B141C', 'stroke-width': 4 }), S('circle', { cx: 26, cy: 0, r: 30, fill: '#EEB6C8', stroke: '#0B141C', 'stroke-width': 4 }), S('circle', { cx: 0, cy: -24, r: 26, fill: '#F4C6D6', stroke: '#0B141C', 'stroke-width': 4 }),
    S('path', { d: 'M0 -44 V30 M-26 -16 q10 10 0 22 M26 -16 q-10 10 0 22', fill: 'none', stroke: '#B0647E', 'stroke-width': 4, 'stroke-linecap': 'round' }),
    S('circle', { r: 66, fill: 'none', stroke: '#FF3B5C', 'stroke-width': 9 }), S('line', { x1: -46, y1: -46, x2: 46, y2: 46, stroke: '#FF3B5C', 'stroke-width': 9, 'stroke-linecap': 'round' }));
  svgA.append(brain);
  show(brainI, w('b2', 'brain') - 0.3, 0.5, { y: 20 });
  hide(brainI, w('b2', 'Commands') - 0.2, 0.4);
  ctxTag(svgA, 1180, 580, 'No brain of its own', '#FF3B5C', w('b2', 'brain') - 0.2, w('b2', 'Commands') - 0.2);

  // umbilical + packets
  const umbD = 'M566 600 C 640 600 660 770 760 812 C 840 836 960 828 1060 826 C 1150 824 1180 780 1198 700';
  const cores = [[YEL, -9, 'power'], [WH, -3, 'signals'], [CY, 3, 'hydraulics'], [VI, 9, 'chemicals']];
  const umbG = S('g');
  svgA.insertBefore(umbG, hostW);
  umbG.append(S('path', { d: umbD, fill: 'none', stroke: '#07131C', 'stroke-width': 34, 'stroke-linecap': 'round' }), S('path', { d: umbD, fill: 'none', stroke: '#3A4B59', 'stroke-width': 28, 'stroke-linecap': 'round' }));
  tl.set(umbG, { opacity: 0 }, 0);
  tl.fromTo(umbG, { opacity: 0 }, { opacity: 1, duration: 0.8, immediateRender: false }, w('b2', 'umbilical') - 0.5);
  const flows = cores.map(([c, dy], i) => {
    const g = S('g', { transform: `translate(0 ${dy})` });
    svgA.append(g);
    const f = Flow(g, umbD, { color: c, w: 4, gap: 30 + i * 4, glow: false });
    f.show(w('b2', 'umbilical') - 0.2, 0.4, 70 + i * 8);
    return f;
  });
  // command packets (big dots) from host -> tree
  const pk = S('g');
  svgA.append(pk);
  const pkG = S('g', { transform: 'translate(0 0)' });
  pk.append(pkG);
  const pf = Flow(pkG, umbD, { color: '#FFFFFF', w: 15, gap: 260, glowW: 2.4, glowOp: 0.35 });
  pf.show(w('b2', 'Commands') - 0.2, 0.4, 230);
  // labels
  const lMcs = tag(svgA, { x: 640, y: 420, text: 'Master control station', sub: 'on the host or onshore', anchor: 'l', size: 28, accent: YEL });
  const lMcsL = leader(svgA, [330, 480], [640, 420], { color: YEL, elbow: [560, 420] });
  show(lMcs.el, w('b2', 'master') - 0.2, 0.5); show(lMcsL, w('b2', 'master') - 0.2, 0.5);
  hide(lMcs.el, w('b2', 'umbilical') - 0.4, 0.4); hide(lMcsL, w('b2', 'umbilical') - 0.4, 0.4);
  const lU = tag(svgA, { x: 900, y: 716, text: 'Umbilical', sub: 'power · signals · hydraulics · chemicals', anchor: 't', size: 28, accent: '#C9A227' });
  show(lU.el, w('b2', 'umbilical') - 0.1, 0.5);
  const lT = tag(svgA, { x: 1560, y: 400, text: 'Subsea tree', anchor: 'c', size: 28, accent: WH });
  show(lT.el, bt('b1').start + 1.0, 0.5, { y: 10 });

  function ctxTag(parent, x, y, text, col, at, until) {
    const t = tag(parent, { x, y, text, accent: col, anchor: 'c', size: 28 });
    show(t.el, at, 0.5, { y: 12 });
    hide(t.el, until, 0.4);
    return t;
  }

  /* ------------------------------------------------------------------ Part B: inside the SCM */
  const B_ = makeScene(root, E, 'control', { t0: tB, t1: sc.end, pad: 0.35 });
  const { el: elB, svg } = B_;
  const defs = S('defs', {}, S('linearGradient', { id: 'gBlockB', x1: 0, y1: 0, x2: 1, y2: 1 }, S('stop', { offset: 0, 'stop-color': '#6C8499' }), S('stop', { offset: 1, 'stop-color': '#3F5363' })));
  svg.append(defs);
  const kickB = H('div', { class: 'kicker abs', style: { left: '96px', top: '150px', color: YEL }, text: 'From command to motion' });
  elB.append(kickB);
  show(kickB, tB - 0.1, 0.6);

  /* MCS display (top-left) */
  const mcs = S('g', { transform: 'translate(96 196)' });
  const mcsI = S('g');
  mcs.append(mcsI);
  svg.append(mcs);
  mcsI.append(S('rect', { width: 560, height: 118, rx: 14, fill: '#06101A', stroke: '#51677A', 'stroke-width': 3 }),
    S('text', { x: 20, y: 30, fill: YEL, 'font-size': 15, 'font-weight': 800, 'letter-spacing': '0.16em', text: 'MASTER CONTROL STATION' }));
  const mcsCmd = S('text', { x: 20, y: 68, fill: '#3BDB86', 'font-size': 26, 'font-weight': 700, style: { fontFamily: 'var(--mono)' }, text: '> OPEN PMV' });
  const mcsL1 = S('text', { x: 20, y: 100, fill: WH, 'font-size': 22, 'font-weight': 600, style: { fontFamily: 'var(--mono)' }, text: '' });
  const mcsL2 = S('text', { x: 300, y: 68, fill: WH, 'font-size': 22, 'font-weight': 600, style: { fontFamily: 'var(--mono)' }, text: '' });
  const mcsL3 = S('text', { x: 300, y: 100, fill: WH, 'font-size': 22, 'font-weight': 600, style: { fontFamily: 'var(--mono)' }, text: '' });
  mcsI.append(mcsCmd, mcsL1, mcsL2, mcsL3);
  gsap.set(mcsCmd, { opacity: 0 });
  show(mcsI, tB - 0.1, 0.7, { y: -20 });
  tl.fromTo(mcsCmd, { opacity: 0 }, { opacity: 1, duration: 0.3, immediateRender: false }, tB + 0.6);
  tl.to(mcsCmd, { opacity: 0, duration: 0.3 }, w('b5', 'Sensors') - 0.2);
  const txtAt = (el, entries) => animate(0, 1e9, (t) => { let cur = ''; for (const [tt, s_] of entries) if (t >= tt) cur = s_; el.textContent = cur; });
  txtAt(mcsL1, [[w('b5', 'pressure'), 'PT  215 bar']]);
  txtAt(mcsL2, [[w('b5', 'temperature'), 'TT  62 °C']]);
  txtAt(mcsL3, [[w('b5', 'state'), 'PMV  OPEN'], [w('b6', 'power') + 0.3, 'PMV  CLOSED'], [w('b7', 'operate') + 1.8, 'PMV  OPEN']]);

  /* SCM box */
  const scmB = S('g');
  svg.append(scmB);
  const scmFrame = S('rect', { x: 330, y: 340, width: 640, height: 520, rx: 22, fill: 'rgba(14,34,52,.92)', stroke: 'rgba(170,200,225,.4)', 'stroke-width': 3 });
  scmB.append(scmFrame, S('text', { x: 360, y: 384, fill: '#AFC0CE', 'font-size': 18, 'font-weight': 800, 'letter-spacing': '0.16em', text: 'SUBSEA CONTROL MODULE (SCM)' }));
  const scmGlow = S('rect', { x: 330, y: 340, width: 640, height: 520, rx: 22, fill: 'none', stroke: YEL, 'stroke-width': 5, opacity: 0 });
  scmB.append(scmGlow);
  // SEM
  const sem = S('g');
  sem.append(S('rect', { x: 380, y: 420, width: 210, height: 120, rx: 12, fill: '#0E2A18', stroke: '#3BDB86', 'stroke-width': 3 }),
    S('rect', { x: 430, y: 450, width: 110, height: 60, rx: 6, fill: '#06140C', stroke: '#3BDB86', 'stroke-width': 2.5 }),
    ...[0, 1, 2, 3].flatMap((i) => [S('line', { x1: 450 + i * 25, y1: 450, x2: 450 + i * 25, y2: 440, stroke: '#3BDB86', 'stroke-width': 3 }), S('line', { x1: 450 + i * 25, y1: 510, x2: 450 + i * 25, y2: 520, stroke: '#3BDB86', 'stroke-width': 3 })]),
    S('text', { x: 485, y: 576, 'text-anchor': 'middle', fill: '#9FE6B5', 'font-size': 20, 'font-weight': 700, text: 'Electronics' }));
  const semGlow = S('rect', { x: 380, y: 420, width: 210, height: 120, rx: 12, fill: '#3BDB86', opacity: 0 });
  scmB.append(semGlow, sem);
  // solenoid pilot valve
  const sol = S('g');
  const solBody = S('rect', { x: 650, y: 430, width: 150, height: 96, rx: 12, fill: '#2A2410', stroke: YEL, 'stroke-width': 3 });
  const solGlow = S('rect', { x: 650, y: 430, width: 150, height: 96, rx: 12, fill: YEL, opacity: 0 });
  sol.append(solBody, S('path', { d: 'M668 478 q10 -26 20 0 t20 0 t20 0 t20 0 t20 0 t20 0', fill: 'none', stroke: YEL, 'stroke-width': 5, 'stroke-linecap': 'round' }),
    S('text', { x: 744, y: 562, 'text-anchor': 'start', fill: '#FFE08A', 'font-size': 20, 'font-weight': 700, text: 'Solenoid pilot valve' }));
  scmB.append(solGlow, sol);
  // directional control valve: in (left) / out (right) / vent (bottom); two internal states
  const dcvX = 610, dcvY = 620;
  const dcvBox = S('g');
  dcvBox.append(S('rect', { x: dcvX, y: dcvY, width: 180, height: 80, rx: 8, fill: '#08121B', stroke: '#51677A', 'stroke-width': 3 }));
  const dcvVent = S('path', { d: `M${dcvX + 180} ${dcvY + 40} H${dcvX + 90} V${dcvY + 80}`, fill: 'none', stroke: CY, 'stroke-width': 6, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
  const dcvSup = S('path', { d: `M${dcvX} ${dcvY + 40} H${dcvX + 180}`, fill: 'none', stroke: CY, 'stroke-width': 6, 'stroke-linecap': 'round', opacity: 0 });
  const spool = S('g');
  spool.append(S('rect', { x: dcvX + 62, y: dcvY + 12, width: 56, height: 56, rx: 6, fill: '#1E3A52', stroke: '#9FD8F0', 'stroke-width': 2.5 }),
    S('path', { d: `M${dcvX + 80} ${dcvY + 40} h20 l-8 -8 m8 8 l-8 8`, fill: 'none', stroke: '#9FD8F0', 'stroke-width': 3, 'stroke-linecap': 'round' }));
  dcvBox.append(dcvVent, dcvSup, spool);
  const dcvBody = { vent: dcvVent, sup: dcvSup, spool };
  scmB.append(dcvBox, S('text', { x: 712, y: dcvY - 14, 'text-anchor': 'end', fill: '#9FD8F0', 'font-size': 19, 'font-weight': 700, text: 'Directional control valve' }),
    S('text', { x: dcvX + 8, y: dcvY + 100, fill: '#6FA9C2', 'font-size': 14, 'font-weight': 700, text: 'IN' }), S('text', { x: dcvX + 150, y: dcvY + 100, fill: '#6FA9C2', 'font-size': 14, 'font-weight': 700, text: 'OUT' }));
  const dcvSet = (t, energized, d = 0.4) => {
    tl.to(dcvSup, { opacity: energized ? 1 : 0, duration: d }, t);
    tl.to(dcvVent, { opacity: energized ? 0 : 1, duration: d }, t);
    tl.to(spool, { x: energized ? 40 : 0, duration: d, ease: 'power3.out' }, t);
  };
  // lines inside SCM (signals): pilot line sol->DCV
  const line = (d, col, wd = 5, op = 0.9) => { const g = S('g'); g.append(S('path', { d, fill: 'none', stroke: '#07131C', 'stroke-width': wd + 5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }), S('path', { d, fill: 'none', stroke: col, 'stroke-width': wd, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', opacity: op })); svg.append(g); return g; };
  const sigD = 'M236 314 V470 H380', pwrD = 'M180 314 V500 H380', hydD = 'M292 314 V660 H610', semSolD = 'M590 478 H650', pilotD = 'M725 526 V620', outD = 'M790 660 H1060 V540 H1150 V516', ventD = 'M700 700 V790';
  // umbilical stub from the MCS (power/signal/hydraulic)
  const lines = {
    pwr: line(pwrD, '#7A6420'), sig: line(sigD, '#7C8A97'), hyd: line(hydD, '#1C6E8C', 6), pilot: line(pilotD, '#6E5C16', 4), semSol: line(semSolD, '#6E5C16', 4), out: line(outD, '#1C6E8C', 6),
  };
  [['pwr', 'POWER', YEL, 180], ['sig', 'SIGNALS', WH, 236], ['hyd', 'HYDRAULIC', CY, 292]].forEach(([k, txt, col, x]) => {
    svg.append(S('text', { transform: `translate(${x + 13} 324) rotate(90)`, fill: col, 'font-size': 14, 'font-weight': 800, 'letter-spacing': '0.08em', text: txt }));
  });
  // dots flowing in the lines
  const fl = {
    sig: Flow(svg, sigD, { color: WH, w: 6, gap: 22 }), pwr: Flow(svg, pwrD, { color: YEL, w: 6, gap: 22 }),
    semSol: Flow(svg, semSolD, { color: YEL, w: 6, gap: 18 }), pilot: Flow(svg, pilotD, { color: YEL, w: 6, gap: 18 }),
    hyd: Flow(svg, 'M292 314 V660 H610', { color: CY, w: 7, gap: 22 }), hydIn: Flow(svg, 'M610 660 H790', { color: CY, w: 7, gap: 18 }),
    out: Flow(svg, outD, { color: CY, w: 7, gap: 20 }),
  };

  /* valve + block (right) */
  const VX = 1560, VY = 660, VS = 1.5;
  const blk = S('g');
  blk.append(S('rect', { x: VX - 175, y: 340, width: 350, height: 640, rx: 20, fill: 'url(#gBlockB)', stroke: '#0B141C', 'stroke-width': 4 }), S('rect', { x: VX - 175, y: 340, width: 350, height: 640, rx: 20, fill: 'url(#pHatch)', opacity: 0.55 }),
    S('rect', { x: VX - 39, y: 340, width: 78, height: 640, fill: '#050B11' }));
  svg.append(blk);
  const bFill = S('rect', { x: VX - 39, y: 340, width: 78, height: 640, fill: 'url(#gFluidHC)', opacity: 0.0 });
  svg.append(bFill);
  const V = GateValve(svg, { x: VX, y: VY, bw: 52, act: 'fs', f0: 0, scale: VS });
  const fBore = [Flow(svg, `M${VX} 980 V${VY + 42}`, { color: OR, w: 10, gap: 28 }), Flow(svg, `M${VX} ${VY - 42} V340`, { color: OR, w: 10, gap: 28 })];
  tl.fromTo(bFill, { opacity: 0 }, { opacity: 0.5, duration: 0.6, immediateRender: false }, w('b4', 'valve') - 0.3);
  fBore[0].show(w('b4', 'opens') - 1.0, 0.4, 0);
  // gauge at actuator
  const ag = gauge(svg, { x: 1100, y: 922, r: 62, max: 250, label: 'ACTUATOR PRESSURE', color: CY, v0: 0 });
  show(ag.g, w('b3', 'hydraulic') - 0.2, 0.5, { y: 20 });
  // sensors
  const sens = S('g');
  const mkS = (x, y, lab) => sens.append(S('line', { x1: VX + 39, y1: y, x2: x, y2: y, stroke: '#0B141C', 'stroke-width': 12 }), S('line', { x1: VX + 39, y1: y, x2: x, y2: y, stroke: '#51677A', 'stroke-width': 7 }), S('circle', { cx: x + 22, cy: y, r: 26, fill: '#E5A22A', stroke: '#0B141C', 'stroke-width': 4 }), S('text', { x: x + 22, y: y + 8, 'text-anchor': 'middle', fill: '#0B141C', 'font-size': 20, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: lab }));
  mkS(VX + 112, 470, 'PT'); mkS(VX + 112, 840, 'TT');
  svg.append(sens);
  const sensRet = 'M1694 443 V300 H1000 V400 H470 V420';
  tl.set(sens, { opacity: 0 }, 0);
  tl.fromTo(sens, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: false }, w('b5', 'Sensors') - 0.2);
  const retG = S('g');
  retG.append(S('path', { d: sensRet, fill: 'none', stroke: '#07131C', 'stroke-width': 9, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }), S('path', { d: sensRet, fill: 'none', stroke: '#55697A', 'stroke-width': 4, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
  svg.append(retG);
  tl.set(retG, { opacity: 0 }, 0);
  tl.fromTo(retG, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: false }, w('b5', 'Sensors'));
  const retFlow = Flow(svg, sensRet, { color: '#9FE6B5', w: 6, gap: 26 });
  retFlow.show(w('b5', 'report') - 0.1, 0.4, 150);
  const retUp = Flow(svg, 'M380 470 H236 V314', { color: '#9FE6B5', w: 6, gap: 22 });
  retUp.show(w('b5', 'pressure') - 0.4, 0.4, 100);

  /* ---- hose label etc. */
  const hose = S('g');
  svg.append(hose);

  /* ---- sequence ---------------------------------------------------------------------- */
  // b3: command arrives
  const t3 = tB;
  const lMod = tag(svg, { x: 850, y: 290, text: 'Subsea control module', sub: 'mounted on the tree', anchor: 'c', size: 28, accent: YEL });
  show(lMod.el, w('b3', 'subsea') - 0.3, 0.5); hide(lMod.el, w('b3', 'electronics') - 0.4, 0.4);
  tl.fromTo(scmGlow, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: false }, w('b3', 'subsea') - 0.1);
  tl.to(scmGlow, { opacity: 0, duration: 0.5 }, w('b3', 'electronics') - 0.3);
  // command pulses travel in the signal/power lines
  fl.sig.show(tB + 0.8, 0.4, 130); fl.pwr.show(tB + 0.8, 0.4, 100);
  const tEl = w('b3', 'electronics');
  tl.fromTo(semGlow, { opacity: 0 }, { opacity: 0.35, duration: 0.5, ease: 'power2.out', immediateRender: false }, tEl);
  const lElec = tag(svg, { x: 485, y: 818, text: 'Electronics receive the command', anchor: 'c', size: 24, accent: '#3BDB86' });
  show(lElec.el, tEl - 0.1, 0.5); hide(lElec.el, w('b3', 'energise') - 0.3, 0.4);
  const tEn = w('b3', 'energise');
  fl.semSol.show(tEn - 0.3, 0.4, 90);
  tl.fromTo(solGlow, { opacity: 0 }, { opacity: 0.35, duration: 0.4, immediateRender: false }, tEn);
  fl.pilot.show(tEn + 0.5, 0.4, 90);
  const lSol = tag(svg, { x: 818, y: 478, text: 'Energised', anchor: 'l', size: 24, accent: YEL });
  show(lSol.el, tEn - 0.1, 0.5); hide(lSol.el, w('b3', 'hydraulic') - 0.2, 0.4);
  // DCV shifts to supply position
  const tDcv = w('b3', 'valve,');
  dcvSet(tDcv - 0.2, true, 0.5);
  const tHy = w('b3', 'hydraulic');
  fl.hyd.show(tB + 1.2, 0.4, 70);
  fl.hydIn.show(tHy - 0.3, 0.4, 100);
  fl.out.show(tHy + 0.5, 0.4, 110);
  ag.to(w('b4', 'builds') - 0.1, 1.6, 207, 'power2.out');
  // one specific actuator
  const tAct = w('b3', 'specific');
  ring_(svg, 1100, 660, 120, YEL, tAct - 0.2, bt('b4').start + 0.2);
  const lAct = tag(svg, { x: 1160, y: 420, text: 'One specific actuator', anchor: 'l', size: 28, accent: YEL });
  show(lAct.el, tAct - 0.2, 0.5); hide(lAct.el, bt('b4').start + 0.3, 0.4);
  // b4: pressure builds -> spring compresses -> valve opens
  V.open(w('b4', 'spring') - 0.4, 2.2, 'power2.inOut');
  const lPr = tag(svg, { x: 1008, y: 922, text: 'Pressure builds', anchor: 'r', size: 26, accent: CY });
  show(lPr.el, w('b4', 'Pressure') - 0.1, 0.5); hide(lPr.el, w('b4', 'valve') - 0.1, 0.4);
  fBore[0].speed(w('b4', 'opens') - 0.7, 80, 0.8);
  fBore[1].show(w('b4', 'opens') - 0.3, 0.4, 80);
  const stLed = tag(svg, { x: VX + 140, y: 255, text: 'OPEN', anchor: 'l', size: 26, accent: '#3BDB86', mono: true });
  show(stLed.el, w('b4', 'opens') - 0.1, 0.5);
  hide(stLed.el, w('b5', 'Sensors') - 0.2, 0.4);

  // b6: cut the power / vent the hydraulics / springs take over
  const t6a = w('b6', 'pressure'), tPow = w('b6', 'power');
  const banner6 = H('div', { class: 'abs', style: { left: '0', top: '128px', width: '1920px', textAlign: 'center' } },
    H('div', { style: { display: 'inline-block', padding: '12px 32px 14px', borderRadius: '16px', background: 'rgba(5,16,26,.9)', border: '2px solid #2ED0FF', font: '800 48px var(--font)', color: WH }, html: 'PRESSURE <span style="color:#2ED0FF">ON</span> = OPEN' }));
  elB.append(banner6);
  show(banner6, t6a - 0.2, 0.5, { y: -20 }); hide(banner6, tPow - 0.4, 0.4);
  const cut = S('g', { stroke: '#FF3B5C', 'stroke-width': 9, 'stroke-linecap': 'round' }, S('path', { d: 'M168 390 l24 24 M192 390 l-24 24' }));
  svg.append(cut);
  tl.set(cut, { opacity: 0 }, 0);
  tl.fromTo(cut, { opacity: 0 }, { opacity: 1, duration: 0.25, immediateRender: false }, tPow);
  tl.to(cut, { opacity: 0, duration: 0.4 }, bt('b7').start - 0.2);
  const lCut = tag(svg, { x: 230, y: 450, text: 'POWER LOST', anchor: 'c', size: 24, accent: '#FF3B5C', mono: true });
  show(lCut.el, tPow - 0.1, 0.4); hide(lCut.el, bt('b7').start - 0.2, 0.4);
  fl.pwr.speed(tPow, 0, 0.3); fl.sig.speed(tPow + 0.05, 0, 0.3); fl.semSol.speed(tPow + 0.05, 0, 0.3); fl.pilot.speed(tPow + 0.05, 0, 0.3);
  fl.pwr.hide(tPow + 0.5, 0.4); fl.sig.hide(tPow + 0.5, 0.4); fl.semSol.hide(tPow + 0.5, 0.4); fl.pilot.hide(tPow + 0.5, 0.4);
  tl.to(solGlow, { opacity: 0, duration: 0.3 }, tPow + 0.1);
  tl.to(semGlow, { opacity: 0, duration: 0.3 }, tPow + 0.1);
  dcvSet(tPow + 0.5, false, 0.4);
  const tVent = w('b6', 'vent');
  fl.out.speed(tVent - 0.1, 0, 0.3); fl.hydIn.speed(tVent - 0.1, 0, 0.3);
  fl.out.hide(tVent + 0.8, 0.4); fl.hydIn.hide(tVent + 0.8, 0.4);
  const ventFlow = Flow(svg, ventD, { color: CY, w: 7, gap: 16 });
  ventFlow.show(tVent, 0.3, 90); ventFlow.hide(tVent + 1.6, 0.4);
  const lVent = tag(svg, { x: 730, y: 770, text: 'Vented to sea', anchor: 'l', size: 26, accent: CY });
  show(lVent.el, tVent, 0.4); hide(lVent.el, bt('b7').start - 0.2, 0.4);
  ag.to(tVent, 1.2, 0, 'power2.in');
  V.close(w('b6', 'springs') - 0.15, 0.8, 'power3.in');
  fBore[1].hide(w('b6', 'springs') + 0.3, 0.5); fBore[0].speed(w('b6', 'springs') + 0.2, 0, 0.4);
  tl.to(bFill, { opacity: 0.25, duration: 0.6 }, w('b6', 'springs') + 0.3);
  const lSpr = tag(svg, { x: 1285, y: 744, text: 'Springs take over', anchor: 't', size: 26, accent: YEL });
  show(lSpr.el, w('b6', 'springs') - 0.2, 0.4); hide(lSpr.el, bt('b7').start - 0.2, 0.4);
  sfx(w('b6', 'springs') - 0.1, 'clunk', 0.9);

  // b7: control lost -> ROV override
  const tL = w('b7', 'control');
  [scmB, mcs, retG, sens, ...Object.values(lines)].forEach((x) => tl.to(x, { opacity: 0.18, duration: 0.7 }, tL));
  Object.values(fl).forEach((f) => f.hide(tL - 0.05, 0.3));
  retFlow.hide(tL - 0.05, 0.3); retUp.hide(tL - 0.05, 0.3);
  const lost = tag(svg, { x: 1000, y: 226, text: 'CONTROL SYSTEM LOST', anchor: 'c', size: 34, accent: '#FF3B5C', mono: true });
  show(lost.el, tL - 0.1, 0.5); hide(lost.el, w('b7', 'ROV') + 1.5, 0.4);
  const rovWrap = S('g');
  svg.append(rovWrap);
  const rv = S('g', { transform: 'scale(1.15)' });
  rovWrap.append(rv);
  rov(rv, { scale: 1 });
  const ovr = [VX - 264.7 * VS + 4, VY];            // override hex position (screen)
  gsap.set(rovWrap, { x: -300, y: 1150 });
  const rovPos = [ovr[0] - 154 * 1.15 - 6, ovr[1] - 36 * 1.15 + 10];
  tl.to(rovWrap, { x: rovPos[0], y: rovPos[1], duration: 2.2, ease: 'power2.out' }, w('b7', 'ROV') - 0.6);
  const hex = S('g', { transform: `translate(${ovr[0] - 12} ${ovr[1]})` });
  const hexI = S('g');
  hex.append(hexI);
  hexI.append(S('path', { d: 'M-22 0 l11 -19 h22 l11 19 l-11 19 h-22 z', fill: '#9FB2C2', stroke: '#0B141C', 'stroke-width': 3 }), S('line', { x1: -14, y1: 0, x2: 14, y2: 0, stroke: '#0B141C', 'stroke-width': 4 }));
  svg.append(hex);
  tl.set(hex, { opacity: 0 }, 0);
  tl.fromTo(hex, { opacity: 0 }, { opacity: 1, duration: 0.3, immediateRender: false }, w('b7', 'connect'));
  const tOp = w('b7', 'operate');
  animate(tOp, tOp + 1.9, (t) => hexI.setAttribute('transform', `rotate(${(((t - tOp) / 1.9) * 540).toFixed(1)})`));
  V.open(tOp + 0.2, 1.9, 'power2.inOut');
  fBore[0].speed(tOp + 1.4, 80, 0.5); fBore[1].show(tOp + 1.6, 0.4, 80);
  tl.to(bFill, { opacity: 0.5, duration: 0.6 }, tOp + 1.6);
  const lOvr = tag(svg, { x: ovr[0] - 40, y: ovr[1] - 200, text: 'ROV mechanical override', sub: 'no control system needed', anchor: 'r', size: 28, accent: '#E5A22A' });
  show(lOvr.el, w('b7', 'connect') - 0.1, 0.5);
  hide(rovWrap, sc.end - 0.2, 0.4);

  function ring_(parent, x, y, r, col, at, until) {
    const g = ring(parent, x, y, { r, color: col, t0: at, t1: until });
    tl.fromTo(g, { opacity: 0 }, { opacity: 1, duration: 0.3, immediateRender: true }, at);
    tl.to(g, { opacity: 0, duration: 0.3 }, until);
    return g;
  }
}
