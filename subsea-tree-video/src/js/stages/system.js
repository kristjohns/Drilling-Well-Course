// Scene 3 – The big picture (57 – 103 s) --------------------------------------------
import { H, S, rng } from '../lib/svg.js';
import { makeScene } from '../lib/scene.js';
import { installDefs } from '../art/defs.js';
import { platform, fpso, plant, miniTree, templateFrame } from '../art/system.js';
import { tag, leader, callout, ring } from '../lib/annot.js';

export function build(root, E) {
  const { T, A, tl, show, hide, fadeIn, fadeOut, Cam, proj, Flow, animate, sfx, gsap } = E;
  installDefs();
  const sc = T.scene('system');
  const tB = T.start('system.b3');

  /* ======================= PART A – hosts (hub & spoke) ======================= */
  const A_ = makeScene(root, E, 'system', { t0: sc.start, t1: tB, pad: 0.3 });
  const { el: elA, svg: svgA } = A_;
  const kick = H('div', { class: 'kicker abs', style: { left: '96px', top: '150px', color: '#FFC857' }, text: 'Subsea production system' });
  const h2 = H('div', { class: 'h2 abs', style: { left: '96px', top: '188px', width: '1300px' }, html: 'Subsea wells are <span style="color:var(--hc)">tied back</span> to a host' });
  elA.append(kick, h2);
  show(kick, T.start('system.b1') - 0.1, 0.6);
  show(h2, T.start('system.b1'), 0.7);

  const hosts = [
    { cx: 360, draw: (g) => platform(g, { scale: 0.56, flame: true, t0: sc.start }), dy: 130, label: 'Platform', sub: 'fixed or floating', word: 'platform' },
    { cx: 960, draw: (g) => fpso(g, { scale: 0.5, flame: true, t0: sc.start }), dy: 130, label: 'Floating production vessel', sub: 'FPSO', word: 'floating' },
    { cx: 1560, draw: (g) => plant(g, { scale: 0.5, flame: true, t0: sc.start }), dy: 130, label: 'Onshore plant', sub: 'e.g. Snøhvit · 143 km away', word: 'onshore' },
  ];
  const cardY = 290, cardW = 520, cardH = 400;
  // seabed strip + template at the bottom
  const strip = S('g');
  svgA.append(strip);
  strip.append(S('rect', { x: 0, y: 900, width: 1920, height: 180, fill: 'url(#gSeabed)' }), S('path', { d: 'M0 900 H1920', stroke: '#4A5A66', 'stroke-width': 3 }));
  const tmpl = S('g', { transform: 'translate(960 900)' });
  const tmplIn = S('g');
  tmpl.append(tmplIn);
  svgA.append(tmpl);
  templateFrame(tmplIn, { w: 340, h: 150 });
  [-110, -37, 37, 110].forEach((x) => { const g = S('g', { transform: `translate(${x} -4)` }); miniTree(g, { scale: 0.95 }); tmplIn.append(g); });
  const tLab = tag(svgA, { x: 960, y: 960, text: 'Subsea wells', sub: 'wellheads, trees and a template on the seabed', anchor: 't', size: 26, accent: '#2ED0FF' });
  show(tmplIn, T.start('system.b1') + 0.6, 0.8, { y: 40 });
  show(tLab.el, T.start('system.b1') + 1.1, 0.6);

  hosts.forEach((h, i) => {
    const wrap = S('g', { transform: `translate(${h.cx} ${cardY})` });
    const g = S('g');
    wrap.append(g);
    svgA.append(wrap);
    g.append(S('rect', { x: -cardW / 2, y: 0, width: cardW, height: cardH, rx: 24, fill: 'rgba(8,26,42,.80)', stroke: 'rgba(170,200,225,.28)', 'stroke-width': 1.6 }));
    const art = S('g', { transform: `translate(0 ${h.dy + 150})` });
    g.append(art);
    h.draw(art);
    g.append(S('path', { d: `M${-cardW / 2} ${cardH - 90} h${cardW} v${90 - 24} a24 24 0 0 1 -24 24 h${-(cardW - 48)} a24 24 0 0 1 -24 -24 Z`, fill: 'rgba(0,0,0,.22)' }));
    g.append(S('text', { x: 0, y: cardH - 48, 'text-anchor': 'middle', fill: '#EEF4F9', 'font-size': 29, 'font-weight': 700, text: h.label }));
    g.append(S('text', { x: 0, y: cardH - 18, 'text-anchor': 'middle', fill: '#9FB4C6', 'font-size': 22, 'font-weight': 500, text: h.sub }));
    const t0 = T.word('system.b2', h.word) - 0.25;
    show(g, t0, 0.7, { y: 40 });
    sfx(t0, 'pop', 0.7);
    // connection line + flow
    const d = `M960 ${900 - 170} C 960 780 ${h.cx} 780 ${h.cx} ${cardY + cardH + 4}`;
    const line = S('path', { d, fill: 'none', stroke: '#33485A', 'stroke-width': 9, 'stroke-linecap': 'round', opacity: 0 });
    svgA.insertBefore(line, svgA.firstChild.nextSibling);
    tl.fromTo(line, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: true }, t0 + 0.2);
    const f = Flow(svgA, d, { color: '#FF9A3C', w: 7 });
    f.show(t0 + 0.4, 0.5, 90);
  });
  // 143 km dimension on the onshore card
  const dim = tag(svgA, { x: 1560, y: 248, text: '143 km', sub: 'subsea to shore', anchor: 'c', size: 30, accent: '#FFC857', mono: true });
  show(dim.el, T.word('system.b2', 'kilometres') - 0.6, 0.6);

  /* ======================= PART B – cross-section ======================= */
  const B_ = makeScene(root, E, 'system', { t0: tB, t1: sc.end, pad: 0.35, bg: '#04121C' });
  const { el: elB, svg: svgB } = B_;
  const defs = S('defs', {},
    S('linearGradient', { id: 'gSysSky', x1: 0, y1: 0, x2: 0, y2: 1 }, S('stop', { offset: 0, 'stop-color': '#0A2540' }), S('stop', { offset: 1, 'stop-color': '#3B7FA8' })),
    S('linearGradient', { id: 'gSysSea', gradientUnits: 'userSpaceOnUse', x1: 0, y1: 250, x2: 0, y2: 800 }, S('stop', { offset: 0, 'stop-color': '#1F6B96' }), S('stop', { offset: 0.5, 'stop-color': '#0C3C5B' }), S('stop', { offset: 1, 'stop-color': '#051B2A' })));
  svgB.append(defs);
  const world = S('g');
  svgB.append(world);
  const cam = new Cam(world, { wx: 960, wy: 540, sx: 960, sy: 540, k: 1 });
  // sky, sea, seabed
  const SEA_Y = 250, SEAB = 800;
  world.append(
    S('rect', { x: -1200, y: -600, width: 4400, height: SEA_Y + 600, fill: 'url(#gSysSky)' }),
    S('rect', { x: -1200, y: SEA_Y, width: 4400, height: SEAB - SEA_Y + 4, fill: 'url(#gSysSea)' }),
    S('rect', { x: -1200, y: SEAB, width: 4400, height: 1400, fill: 'url(#pRock)' }),
    S('rect', { x: -1200, y: SEAB, width: 4400, height: 1400, fill: 'url(#gSeabed)', opacity: 0.6 }),
    S('path', { d: `M-1200 ${SEAB} H3200`, stroke: '#6B7F8C', 'stroke-width': 4 }));
  // light shafts in the water
  const shafts = S('g', { style: { mixBlendMode: 'screen' }, fill: '#CFEFFF' });
  [[200, 90, -160], [620, 70, -120], [1100, 100, -60], [1500, 80, 0]].forEach(([x, w, sk], i) => shafts.append(S('path', { d: `M${x} ${SEA_Y} h${w} L${x + w + sk} ${SEAB} h${-w * 1.5} Z`, opacity: 0.045 + (i % 2) * 0.02 })));
  world.append(shafts);
  // reservoir
  const resG = S('g');
  resG.append(
    S('path', { d: 'M900 1000 C1100 960 1500 950 1900 1000 L1950 1100 C1500 1130 1100 1120 860 1100 Z', fill: 'url(#pSand)', stroke: '#8A5A22', 'stroke-width': 3 }),
    S('path', { d: 'M900 1000 C1100 960 1500 950 1900 1000', fill: 'none', stroke: '#E5A04C', 'stroke-width': 4, opacity: 0.8 }));
  world.append(resG);
  // sea surface waves (animated)
  const waves = S('path', { d: '', fill: 'rgba(160,215,240,.28)', stroke: 'rgba(210,240,255,.6)', 'stroke-width': 3 });
  world.append(waves);
  animate(0, 1e9, (t) => {
    let d = `M-300 ${SEA_Y + 60}`;
    const pts = [];
    for (let x = -300; x <= 2300; x += 40) pts.push(`L${x} ${(SEA_Y + 5 * Math.sin(x / 70 + t * 1.6) + 2.5 * Math.sin(x / 31 - t * 2.3)).toFixed(1)}`);
    waves.setAttribute('d', `M-300 ${SEA_Y + 60} ${pts.join(' ')} L2300 ${SEA_Y + 60} Z`);
  });
  const PX = 540;
  // platform (bobs gently)
  const platWrap = S('g', { transform: `translate(${PX} ${SEA_Y})` });
  const platBob = S('g');
  platWrap.append(platBob);
  world.append(platWrap);
  platform(platBob, { scale: 0.66, flame: true, t0: tB });
  animate(0, 1e9, (t) => platBob.setAttribute('transform', `translate(0 ${(2.5 * Math.sin(t * 0.9)).toFixed(2)}) rotate(${(0.35 * Math.sin(t * 0.7)).toFixed(3)})`));

  // pipework along the seabed
  const RB = [900, 798];                                    // riser base
  const TX = 1520;                                          // template centre
  const riserD = `M${PX} ${SEA_Y + 70} C ${PX} 560 ${PX + 230} 650 ${RB[0]} ${RB[1] - 2}`;
  const flD = `M${RB[0]} ${SEAB - 6} H${TX - 150}`;
  const umbD = `M${PX + 42} ${SEA_Y + 60} C ${PX + 110} 560 ${PX + 430} 640 ${PX + 570} ${SEAB + 6} H${TX - 150}`;
  const pipeStyle = { fill: 'none', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' };
  const pipeG = S('g');
  world.append(pipeG);
  const pipe = (d, w, col) => { const g = S('g'); g.append(S('path', { ...pipeStyle, d, stroke: '#07131C', 'stroke-width': w + 6 }), S('path', { ...pipeStyle, d, stroke: col, 'stroke-width': w })); pipeG.append(g); return g; };
  const riserG = pipe(riserD, 12, '#51677A');
  const flG = pipe(flD, 12, '#51677A');
  // template + wells + trees
  const tmplW = S('g', { transform: `translate(${TX} ${SEAB})` });
  world.append(tmplW);
  const trees = [-120, -40, 40, 120];
  const wellsG = S('g');
  world.append(wellsG);
  trees.forEach((x, i) => {
    const wx = TX + x;
    wellsG.append(
      S('path', { d: `M${wx} ${SEAB} C ${wx} 880 ${wx + (i - 1.5) * 28} 920 ${wx + (i - 1.5) * 70} 1010`, ...pipeStyle, stroke: '#07131C', 'stroke-width': 13 }),
      S('path', { d: `M${wx} ${SEAB} C ${wx} 880 ${wx + (i - 1.5) * 28} 920 ${wx + (i - 1.5) * 70} 1010`, ...pipeStyle, stroke: '#7F98AC', 'stroke-width': 7 }));
  });
  templateFrame(tmplW, { w: 360, h: 150 });
  const treeGs = trees.map((x) => { const g = S('g', { transform: `translate(${x} -2)` }); miniTree(g, { scale: 1.0 }); tmplW.append(g); return g; });
  const umbBundle = pipe(umbD, 7, '#C9A227');

  /* shots */
  const SH0 = { wx: 960, wy: 540, sx: 960, sy: 540, k: 1 };
  const SH1 = { wx: TX, wy: SEAB - 60, sx: 1060, sy: 660, k: 2.0 };    // template close-up
  const SH2 = { wx: 1010, wy: 560, sx: 960, sy: 590, k: 0.9 };       // whole system with flow
  const SH3 = { wx: 1010, wy: 560, sx: 960, sy: 590, k: 0.9 };
  const SH4 = { wx: TX - 40, wy: 770, sx: 960, sy: 620, k: 3.2 };     // one tree
  // initial: the platform and sea in view
  cam.cut(0, { ...SH0 });
  cam.go(T.start('system.b3') - 0.2, 2.2, SH1, 'power3.inOut');
  cam.go(T.start('system.b4') - 0.4, 2.2, SH2, 'power3.inOut');
  cam.go(T.start('system.b6') - 0.3, 2.4, SH4, 'power3.inOut');
  const P = (shot, wx, wy) => proj(shot, wx, wy);

  const annB = S('g');
  svgB.append(annB);
  // b3 labels (template close-up)
  const lt = tag(annB, { x: P(SH1, TX, SEAB - 175)[0], y: P(SH1, TX, SEAB - 175)[1], text: 'Template', sub: 'a steel frame that groups the wells', anchor: 'b', size: 28, accent: '#2ED0FF' });
  const lw = callout(annB, { target: P(SH1, TX - 40, SEAB - 20), at: [P(SH1, TX - 40, SEAB)[0] - 380, 840], text: 'Wellhead', sub: 'the top of each well', color: '#34D8A8', anchor: 'r', size: 26 });
  const lx = callout(annB, { target: P(SH1, TX + 40, SEAB - 80), at: [P(SH1, TX + 40, SEAB)[0] + 300, 330], text: 'Tree', sub: 'one on every wellhead', color: '#FFC857', anchor: 'l', size: 28 });
  show(lt.el, T.word('system.b3', 'templates') - 0.3, 0.6);
  show(lw.g, T.word('system.b3', 'wellhead') - 0.2, 0.6);
  show(lx.g, T.word('system.b3', 'tree') - 0.3, 0.6);
  [lt.el, lw.g, lx.g].forEach((x) => hide(x, T.end('system.b3') + 0.3, 0.5));

  // b4: hydrocarbons flow from reservoir to host
  const orange = '#FF9A3C';
  const fl = {};
  fl.wells = trees.map((x, i) => { const wx = TX + x; return Flow(world, `M${wx + (i - 1.5) * 70} 1010 C ${wx + (i - 1.5) * 28} 920 ${wx} 880 ${wx} ${SEAB - 6}`, { color: orange, w: 7, gap: 22 }); });
  fl.trees = trees.map((x) => Flow(world, `M${TX + x} ${SEAB - 6} V${SEAB - 70} Q${TX + x} ${SEAB - 80} ${TX + x - 10} ${SEAB - 80}`, { color: orange, w: 6, gap: 18 }));
  fl.fl = Flow(world, `M${TX - 150} ${SEAB - 6} H${RB[0]}`, { color: orange, w: 7, gap: 22 });
  fl.riser = Flow(world, `M${RB[0]} ${RB[1] - 2} C ${PX + 230} 650 ${PX} 560 ${PX} ${SEA_Y + 70}`, { color: orange, w: 7, gap: 22 });
  const b4 = 'system.b4';
  fl.wells.forEach((f, i) => f.show(T.word(b4, 'reservoir') + i * 0.05, 0.4, 70));
  fl.trees.forEach((f, i) => f.show(T.word(b4, 'tree') - 0.2 + i * 0.05, 0.4, 70));
  fl.fl.show(T.word(b4, 'flowline') - 0.2, 0.4, 90);
  fl.riser.show(T.word(b4, 'host') - 0.8, 0.4, 90);
  const rl = tag(annB, { x: 960, y: 1040, text: 'Reservoir', anchor: 'b', size: 28, accent: '#FF9A3C' });
  const fll = callout(annB, { target: [P(SH2, 1050, SEAB - 6)[0], P(SH2, 1050, SEAB - 6)[1]], at: [P(SH2, 1050, SEAB)[0], 905], text: 'Flowline', anchor: 't', size: 26, color: '#FF9A3C' });
  show(rl.el, T.word(b4, 'reservoir') - 0.2, 0.5);
  show(fll.g, T.word(b4, 'flowline') - 0.1, 0.5);
  const hostL = tag(annB, { x: 760, y: 190, text: 'Host', sub: 'platform · FPSO · onshore', anchor: 'l', size: 28, accent: '#EEF4F9' });
  show(hostL.el, T.word(b4, 'host') - 0.5, 0.5);
  [rl.el, fll.g].forEach((x) => hide(x, T.end(b4) + 0.3, 0.5));
  hide(hostL.el, T.end(b4) + 0.3, 0.5);

  // b5: umbilical
  const b5 = 'system.b5';
  gsap.set(umbBundle, { opacity: 0 });
  tl.fromTo(umbBundle, { opacity: 0 }, { opacity: 1, duration: 0.8, immediateRender: false }, T.word(b5, 'umbilical') - 0.2);
  const uf = [
    ['electrical', '#FFC857', 'POWER'], ['communication', '#EEF4F9', 'SIGNALS'], ['hydraulic', '#2ED0FF', 'HYDRAULICS'], ['chemicals', '#BC8FFF', 'CHEMICALS'],
  ];
  const umbPath = umbBundle.querySelectorAll('path')[1];
  const uLen = umbPath.getTotalLength();
  uf.forEach(([w, col, lab], i) => {
    const f = Flow(world, umbD, { color: col, w: 5, gap: 34 });
    f.speed(0, 0);
    f.show(T.word(b5, w) - 0.1, 0.4, 70 + i * 6);
    const pt = umbPath.getPointAtLength(uLen * (0.30 + i * 0.1));
    const sp = P(SH3, pt.x, pt.y);
    const tg = tag(annB, { x: 1130, y: 280 + i * 78, text: lab, anchor: 'l', size: 26, accent: col, mono: true });
    const lead = leader(annB, sp, [1130, 280 + i * 78], { color: col, elbow: [1090, 280 + i * 78] });
    show(tg.el, T.word(b5, w) - 0.15, 0.5);
    show(lead, T.word(b5, w) - 0.15, 0.5);
    [tg.el, lead].forEach((x) => hide(x, T.end(b5) + 0.4, 0.5));
  });
  const ul = tag(annB, { x: 640, y: 560, text: 'Umbilical', sub: 'from the host to the tree', anchor: 'r', size: 28, accent: '#C9A227' });
  show(ul.el, T.word(b5, 'umbilical') - 0.1, 0.5);
  hide(ul.el, T.end(b5) + 0.4, 0.5);

  // b6: gateway
  const b6 = 'system.b6';
  const treeTop = P(SH4, TX - 40, SEAB - 112), treeBot = P(SH4, TX - 40, SEAB + 30);
  const gate = tag(annB, { x: 960, y: 150, text: 'THE GATEWAY', anchor: 'c', size: 44, accent: '#FFC857', mono: true });
  show(gate.el, T.word(b6, 'gateway') - 0.5, 0.6);
  const arr = (x, y0, y1, col) => {
    const dir = y1 < y0 ? -1 : 1;
    const g = S('g', { fill: 'none', stroke: col, 'stroke-width': 9, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
    g.append(S('path', { d: `M${x} ${y0} V${y1}` }), S('path', { d: `M${x - 26} ${y1 - dir * 34} L${x} ${y1} L${x + 26} ${y1 - dir * 34}` }));
    annB.append(g);
    return g;
  };
  const arrUp = arr(960, treeTop[1] - 24, 262, '#2ED0FF');
  const arrDn = arr(960, treeBot[1] + 10, 900, '#FF9A3C');
  const upL = tag(annB, { x: 1010, y: 290, text: 'PRODUCTION SYSTEM', sub: 'flowline · host', anchor: 'l', size: 28, accent: '#2ED0FF', mono: true });
  const dnL = tag(annB, { x: 1010, y: 880, text: 'WELL', sub: 'tubing · reservoir', anchor: 'l', size: 28, accent: '#FF9A3C', mono: true });
  show(upL.el, T.word(b6, 'above') - 0.2, 0.5); show(arrUp, T.word(b6, 'above') - 0.4, 0.5);
  show(dnL.el, T.word(b6, 'below') - 0.2, 0.5); show(arrDn, T.word(b6, 'below') - 0.4, 0.5);
}
