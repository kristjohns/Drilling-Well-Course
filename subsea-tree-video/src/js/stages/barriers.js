// Scene 17 – The two-barrier principle (404 – 445 s) ---------------------------------------------
// A purpose-drawn well-barrier schematic (blue = primary, red = secondary, as in NORSOK D-010).
import { H, S } from '../lib/svg.js';
import { makeScene, iconSvg } from '../lib/scene.js';
import { icons } from '../art/icons.js';
import { installDefs } from '../art/defs.js';
import { GateValve } from '../art/valve.js';
import { callout } from '../lib/annot.js';

const BLUE = '#4A82FF', RED = '#FF4F6D', OR = '#FF9A3C', TEAL = '#34D8A8', GRN = '#3BDB86', YEL = '#FFC857';
const OUT = '#0B141C';

export function build(root, E) {
  const { T, tl, show, hide, fadeIn, sfx, animate } = E;
  installDefs();
  const w = (id, word, n = 0) => T.word('barriers.' + id, word, n);
  const bt = (id) => T.beat('barriers.' + id);
  const { el, svg } = makeScene(root, E, 'barriers', {});

  const X = 1230;           // centre line of the well
  const SEABED = 462;
  const defs = S('defs', {},
    S('linearGradient', { id: 'gBarSteel', x1: 0, y1: 0, x2: 1, y2: 1 }, S('stop', { offset: 0, 'stop-color': '#7A92A6' }), S('stop', { offset: 1, 'stop-color': '#475A69' })),
    S('linearGradient', { id: 'gBarWater', x1: 0, y1: 0, x2: 0, y2: 1 }, S('stop', { offset: 0, 'stop-color': '#3C86D6', 'stop-opacity': 0 }), S('stop', { offset: 1, 'stop-color': '#3C86D6', 'stop-opacity': 0.24 })));
  svg.append(defs);

  /* ---------- panel (left) ---------- */
  const kick = H('div', { class: 'kicker abs', style: { left: '96px', top: '150px', color: YEL }, text: 'Well integrity' });
  const h2 = H('div', { class: 'h2 abs', style: { left: '96px', top: '188px', width: '640px' }, html: 'The two-barrier<br>principle' });
  const body = H('div', { class: 'body abs', style: { left: '96px', top: '350px', width: '560px', fontSize: '28px' }, text: 'At all times: two independent, tested barriers between the reservoir and the environment.' });
  el.append(kick, h2, body);
  show(kick, bt('b1').start - 0.1, 0.6); show(h2, bt('b1').start, 0.7); show(body, w('b2', 'two') - 0.4, 0.7);

  /* ---------- the well (all static art, revealed with the whole group) ---------- */
  const art = S('g');
  svg.append(art);
  // sea water above the seabed, formation below
  art.append(S('rect', { x: X - 430, y: 60, width: 860, height: SEABED - 60, fill: 'url(#gBarWater)' }));
  art.append(S('rect', { x: X - 430, y: SEABED, width: 860, height: 530, fill: 'url(#pRock)', opacity: 0.55 }), S('path', { d: `M${X - 430} ${SEABED} H${X + 430}`, stroke: '#4A5F6E', 'stroke-width': 4 }));
  // reservoir
  art.append(S('path', { d: `M${X - 440} 960 C${X - 260} 930 ${X + 260} 930 ${X + 440} 960 L${X + 480} 1060 L${X - 480} 1060 Z`, fill: 'url(#pSand)', stroke: '#8A5A22', 'stroke-width': 3 }));
  // casing walls + cement
  art.append(S('rect', { x: X - 190, y: 474, width: 20, height: 530, fill: 'url(#pCement)' }), S('rect', { x: X - 170, y: 474, width: 18, height: 530, fill: '#7A93A8', stroke: OUT, 'stroke-width': 2 }),
    S('rect', { x: X + 170, y: 474, width: 20, height: 530, fill: 'url(#pCement)' }), S('rect', { x: X + 152, y: 474, width: 18, height: 530, fill: '#7A93A8', stroke: OUT, 'stroke-width': 2 }));
  // annulus fluid
  art.append(S('rect', { x: X - 152, y: 474, width: 118, height: 346, fill: TEAL, opacity: 0.22 }), S('rect', { x: X + 34, y: 474, width: 118, height: 346, fill: TEAL, opacity: 0.22 }));
  // tubing
  art.append(S('rect', { x: X - 34, y: 464, width: 12, height: 540, fill: '#B3C4D2', stroke: OUT, 'stroke-width': 2 }), S('rect', { x: X + 22, y: 464, width: 12, height: 540, fill: '#B3C4D2', stroke: OUT, 'stroke-width': 2 }), S('rect', { x: X - 22, y: 464, width: 44, height: 540, fill: '#050B11' }));
  // reservoir fluid in the tubing: below the DHSV, and (during the failure) above it
  art.append(S('rect', { x: X - 22, y: 700, width: 44, height: 304, fill: 'url(#gFluidHC)', opacity: 0.55 }), S('rect', { x: X - 22, y: 464, width: 44, height: 132, fill: 'url(#gFluidHC)', opacity: 0.55 }));
  // perforations
  for (let i = 0; i < 5; i++) [-1, 1].forEach((sg) => art.append(S('rect', { x: sg > 0 ? X + 190 : X - 226, y: 940 + i * 14, width: 36, height: 6, rx: 2, fill: '#FFB067' })));
  // packer
  [[X - 152, 118], [X + 34, 118]].forEach(([x, wd]) => art.append(
    S('rect', { x, y: 820, width: wd, height: 56, fill: '#1B232B', stroke: OUT, 'stroke-width': 3 }), S('rect', { x: x + 6, y: 830, width: wd - 12, height: 36, rx: 6, fill: '#2C3A46' }),
    S('rect', { x, y: 806, width: wd, height: 14, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 2 }), S('rect', { x, y: 876, width: wd, height: 14, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 2 })));
  // DHSV (flapper closed) + its hydraulic control line
  art.append(S('rect', { x: X - 66, y: 596, width: 132, height: 104, rx: 12, fill: '#A9BBCA', stroke: OUT, 'stroke-width': 3 }), S('rect', { x: X - 22, y: 590, width: 44, height: 116, fill: '#050B11' }),
    S('rect', { x: X - 22, y: 668, width: 44, height: 10, rx: 3, fill: 'url(#gGate)', stroke: OUT, 'stroke-width': 2 }), S('circle', { cx: X - 22, cy: 673, r: 6, fill: '#EAF1F6', stroke: OUT, 'stroke-width': 2 }),
    S('path', { d: `M${X + 66} 616 H${X + 92} V450`, fill: 'none', stroke: '#2ED0FF', 'stroke-width': 5, 'stroke-linejoin': 'round', opacity: 0.8 }));
  // wellhead + hanger
  art.append(S('rect', { x: X - 206, y: 392, width: 412, height: 82, rx: 14, fill: 'url(#gBarSteel)', stroke: OUT, 'stroke-width': 3 }), S('rect', { x: X - 156, y: 400, width: 312, height: 66, rx: 8, fill: '#33485A', stroke: OUT, 'stroke-width': 3 }), S('rect', { x: X - 22, y: 392, width: 44, height: 82, fill: '#050B11' }),
    S('rect', { x: X - 158, y: 420, width: 8, height: 12, fill: '#C9D6E0' }), S('rect', { x: X + 150, y: 420, width: 8, height: 12, fill: '#C9D6E0' }));
  // tree: block with the vertical bore, production wing, three hydraulic gate valves (all shut in)
  art.append(S('rect', { x: X - 212, y: 178, width: 424, height: 214, rx: 16, fill: 'url(#gBarSteel)', stroke: OUT, 'stroke-width': 3 }), S('rect', { x: X - 212, y: 178, width: 424, height: 214, rx: 16, fill: 'url(#pHatch)', opacity: 0.5 }),
    S('rect', { x: X - 34, y: 158, width: 68, height: 24, rx: 5, fill: '#5C7384', stroke: OUT, 'stroke-width': 3 }),
    S('rect', { x: X + 200, y: 258, width: 130, height: 68, fill: '#3F5363', stroke: OUT, 'stroke-width': 3 }), S('rect', { x: X + 322, y: 246, width: 16, height: 92, rx: 3, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 2 }),
    S('rect', { x: X - 20, y: 160, width: 40, height: 232, fill: '#050B11' }), S('rect', { x: X + 20, y: 276, width: 318, height: 32, fill: '#050B11' }));
  GateValve(art, { x: X, y: 232, bw: 40, act: 'fs', f0: 0 });
  GateValve(art, { x: X, y: 352, bw: 40, act: 'fs', f0: 0 });
  GateValve(art, { x: X + 135, y: 292, rot: 90, bw: 32, act: 'fs', f0: 0 });
  const vl = (x, y, text, anchor = 'end') => art.append(S('text', { x, y, 'text-anchor': anchor, fill: '#AFC0CE', 'font-size': 21, 'font-weight': 700, style: { fontFamily: 'var(--mono)' }, text }));
  vl(X - 238, 240, 'PSV'); vl(X - 238, 360, 'PMV'); vl(X + 135, 104, 'PWV', 'middle');
  vl(X + 366, 298, 'to flowline', 'start');
  fadeIn(art, bt('b1').start + 0.3, 1.0);

  /* ---------- barrier envelopes ---------- */
  const env = (rects, col, o = {}) => {
    const g = S('g', { opacity: 0 });
    rects.forEach(([x, y, wd, h, r]) => g.append(S('rect', { x, y, width: wd, height: h, rx: r ?? 10, fill: col, 'fill-opacity': o.fill ?? 0.22, stroke: col, 'stroke-width': o.sw ?? 7, 'stroke-linejoin': 'round' })));
    svg.append(g);
    return g;
  };
  const envPath = (d, col, o = {}) => {
    const g = S('g', { opacity: 0 }, S('path', { d, fill: col, 'fill-opacity': o.fill ?? 0.16, stroke: col, 'stroke-width': o.sw ?? 7, 'stroke-linejoin': 'round' }));
    svg.append(g);
    return g;
  };
  const eTub = env([[X - 42, 592, 84, 292, 6]], BLUE), ePack = env([[X - 158, 800, 130, 96, 8], [X + 28, 800, 130, 96, 8]], BLUE), eDhsv = env([[X - 72, 590, 144, 116, 14]], BLUE);
  const eCas = env([[X - 194, 470, 44, 424, 6], [X + 150, 470, 44, 424, 6]], RED, { fill: 0.35, sw: 6 });
  const eWell = env([[X - 214, 386, 428, 94, 18]], RED), eHang = env([[X - 162, 396, 324, 74, 10]], RED, { fill: 0.35, sw: 6 });
  const eTree = envPath(`M${X - 222} 168 H${X + 106} V118 H${X + 164} V168 H${X + 222} V250 H${X + 346} V334 H${X + 222} V402 H${X - 222} Z`, RED);

  /* ---------- labels with leaders ---------- */
  const lab = (target, at, text, col, t0, t1, anchor, sub) => {
    const c = callout(svg, { target, at, text, sub, color: col, anchor, size: 26 });
    show(c.g, t0, 0.45, { y: 10 });
    hide(c.g, t1, 0.4);
    return c;
  };

  /* ---------- b2: end-points ---------- */
  const tag2 = (x, y, text, col, t0, anchor) => {
    const c = callout(svg, { target: [x, y], at: [x + (anchor === 'l' ? 90 : -90), y], text, color: col, anchor, size: 26, mono: true });
    show(c.g, t0, 0.45, { y: 10 }); hide(c.g, bt('b3').start - 0.2, 0.4);
  };
  tag2(X + 250, 130, 'ENVIRONMENT', '#6FB6E0', w('b2', 'environment') - 0.4, 'l');
  tag2(X + 330, 1000, 'RESERVOIR', OR, w('b2', 'reservoir') - 0.4, 'r');
  // two shields at left
  const shW = H('div', { class: 'abs', style: { left: '96px', top: '560px', display: 'flex', gap: '34px', alignItems: 'flex-end' } });
  const shield = (c, txt) => H('div', { style: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' } }, iconSvg(icons.shield('#EEF4F9', c), 128), H('div', { style: { font: '700 22px var(--mono)', color: c }, text: txt }));
  const s1 = shield(BLUE, 'BARRIER 1'), s2 = shield(RED, 'BARRIER 2');
  shW.append(s1, s2);
  el.append(shW);
  tl.fromTo(s1, { autoAlpha: 0, scale: 0.6 }, { autoAlpha: 1, scale: 1, duration: 0.5, ease: 'back.out(2)', immediateRender: true }, w('b2', 'two') - 0.1);
  tl.fromTo(s2, { autoAlpha: 0, scale: 0.6 }, { autoAlpha: 1, scale: 1, duration: 0.5, ease: 'back.out(2)', immediateRender: true }, w('b2', 'two') + 0.3);
  const chk = (txt, y, at) => { const c = H('div', { class: 'abs', style: { left: '96px', top: y + 'px', padding: '8px 20px', borderRadius: '12px', background: 'rgba(5,16,26,.9)', border: `2px solid ${GRN}`, font: '700 26px var(--font)', color: '#EEF4F9' }, html: `<span style="color:${GRN}">✓</span>&nbsp; ${txt}` }); el.append(c); show(c, at, 0.45, { y: 10 }); hide(c, bt('b3').start - 0.2, 0.4); };
  chk('independent', 760, w('b2', 'independent') - 0.2); chk('tested', 820, w('b2', 'tested') - 0.2);
  hide(shW, bt('b3').start - 0.2, 0.4); hide(body, bt('b3').start - 0.3, 0.4);

  /* ---------- b3: primary barrier ---------- */
  const tEnd = bt('b6').start - 0.3;
  const bluePanel = H('div', { class: 'abs', style: { left: '96px', top: '430px', width: '520px', padding: '16px 22px', borderRadius: '16px', background: 'rgba(5,16,26,.9)', border: `2px solid ${BLUE}` } },
    H('div', { style: { font: '800 26px var(--mono)', color: BLUE, marginBottom: '6px' }, text: 'PRIMARY BARRIER' }), H('div', { style: { font: '500 24px/1.35 var(--font)', color: '#DCE6EE' }, text: 'Tubing · packer · downhole safety valve' }));
  el.append(bluePanel);
  show(bluePanel, w('b3', 'primary') - 0.2, 0.6, { x: -20, y: 0 }); hide(bluePanel, tEnd, 0.4);
  tl.fromTo(eTub, { opacity: 0 }, { opacity: 1, duration: 0.6, immediateRender: false }, w('b3', 'tubing') - 0.1);
  tl.fromTo(ePack, { opacity: 0 }, { opacity: 1, duration: 0.6, immediateRender: false }, w('b3', 'packer') - 0.1);
  tl.fromTo(eDhsv, { opacity: 0 }, { opacity: 1, duration: 0.6, immediateRender: false }, w('b3', 'downhole') - 0.1);
  const tL = bt('b5').start - 0.2;
  lab([X - 30, 770], [X - 330, 770], 'Tubing', BLUE, w('b3', 'tubing') - 0.1, tL, 'r');
  lab([X - 150, 850], [X - 330, 850], 'Packer', BLUE, w('b3', 'packer') - 0.1, tL, 'r');
  lab([X - 66, 648], [X - 330, 648], 'DHSV', BLUE, w('b3', 'downhole') - 0.1, tL, 'r');
  sfx(w('b3', 'tubing'), 'tick', 0.6);

  /* ---------- b4: secondary barrier ---------- */
  const redPanel = H('div', { class: 'abs', style: { left: '96px', top: '580px', width: '520px', padding: '16px 22px', borderRadius: '16px', background: 'rgba(5,16,26,.9)', border: `2px solid ${RED}` } },
    H('div', { style: { font: '800 26px var(--mono)', color: RED, marginBottom: '6px' }, text: 'SECONDARY BARRIER' }), H('div', { style: { font: '500 24px/1.35 var(--font)', color: '#DCE6EE' }, text: 'Casing and cement · wellhead · tubing hanger · tree with valves' }));
  el.append(redPanel);
  show(redPanel, w('b4', 'secondary') - 0.2, 0.6, { x: -20, y: 0 }); hide(redPanel, tEnd, 0.4);
  tl.fromTo(eCas, { opacity: 0 }, { opacity: 1, duration: 0.6, immediateRender: false }, w('b4', 'casing') - 0.1);
  tl.fromTo(eWell, { opacity: 0 }, { opacity: 1, duration: 0.6, immediateRender: false }, w('b4', 'wellhead') - 0.1);
  tl.fromTo(eHang, { opacity: 0 }, { opacity: 1, duration: 0.6, immediateRender: false }, w('b4', 'hanger') - 0.2);
  tl.fromTo(eTree, { opacity: 0 }, { opacity: 1, duration: 0.6, immediateRender: false }, w('b4', 'tree') - 0.1);
  lab([X + 194, 700], [X + 330, 700], 'Casing', RED, w('b4', 'casing') - 0.1, tL, 'l');
  lab([X + 180, 580], [X + 330, 580], 'Cement', RED, w('b4', 'cement') - 0.1, tL, 'l');
  lab([X + 214, 440], [X + 330, 440], 'Wellhead', RED, w('b4', 'wellhead') - 0.1, tL, 'l');
  lab([X - 150, 436], [X - 330, 436], 'Tubing hanger', RED, w('b4', 'hanger') - 0.2, tL, 'r');
  lab([X + 222, 200], [X + 330, 190], 'Tree + valves', RED, w('b4', 'tree') - 0.1, tL, 'l');
  sfx(w('b4', 'casing'), 'tick', 0.6);

  /* ---------- b5: barrier 1 fails, barrier 2 holds ---------- */
  const burst = S('g', { transform: `translate(${X} 648)` });
  const burstI = S('g');
  burst.append(burstI);
  burstI.append(S('circle', { r: 64, fill: 'url(#gGlowRed)' }), S('path', { d: 'M-24 -24 L24 24 M24 -24 L-24 24', stroke: '#fff', 'stroke-width': 10, 'stroke-linecap': 'round' }));
  svg.append(burst);
  tl.fromTo(burstI, { scale: 0, svgOrigin: '0 0' }, { scale: 1, duration: 0.5, ease: 'back.out(3)', immediateRender: true }, w('b5', 'fails') - 0.2);
  tl.to(burstI, { opacity: 0, duration: 0.5 }, bt('b6').start - 0.3);
  tl.to([eTub, ePack, eDhsv], { opacity: 0.3, duration: 0.6 }, w('b5', 'fails'));
  lab([X - 40, 628], [X - 330, 600], 'BARRIER 1 FAILS', '#FF3B5C', w('b5', 'fails') - 0.1, bt('b6').start - 0.3, 'r');
  // the leak rises through the tubing and stops at the closed master valve
  const leak = S('rect', { x: X - 22, y: 590, width: 44, height: 0, fill: 'url(#gFluidHC)', opacity: 0.85 });
  svg.append(leak);
  tl.fromTo(leak, { attr: { y: 596, height: 0 } }, { attr: { y: 360, height: 236 }, duration: 1.4, ease: 'power1.in', immediateRender: true }, w('b5', 'fails') + 0.1);
  tl.to(leak, { opacity: 0, duration: 0.6 }, bt('b6').start - 0.3);
  const hold = S('g', { transform: `translate(${X + 118} 352)` });
  const holdI = S('g');
  hold.append(holdI);
  holdI.append(S('circle', { r: 20, fill: GRN, stroke: OUT, 'stroke-width': 3 }), S('path', { d: 'M-9 0 l7 8 l12 -16', fill: 'none', stroke: OUT, 'stroke-width': 5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
  svg.append(hold);
  tl.fromTo(holdI, { scale: 0, svgOrigin: '0 0' }, { scale: 1, duration: 0.4, ease: 'back.out(3)', immediateRender: true }, w('b5', 'other') - 0.1);
  tl.to(holdI, { opacity: 0, duration: 0.4 }, bt('b6').start - 0.3);
  lab([X + 140, 352], [X + 330, 392], 'BARRIER 2 HOLDS', GRN, w('b5', 'other') - 0.1, bt('b6').start - 0.3, 'l');
  animate(w('b5', 'other'), bt('b6').start, (t) => { const o = 0.78 + 0.22 * Math.sin((t - w('b5', 'other')) * 6); [eCas, eWell, eHang, eTree].forEach((e) => (e.style.opacity = o.toFixed(2))); });
  const act = H('div', { class: 'abs', style: { left: '96px', top: '800px', padding: '12px 26px', borderRadius: '14px', background: 'rgba(5,16,26,.9)', border: `2px solid ${YEL}`, font: '800 34px var(--mono)', color: YEL }, text: 'TIME TO ACT' });
  el.append(act);
  show(act, w('b5', 'time') - 0.3, 0.5, { y: 14 }); hide(act, bt('b6').start - 0.3, 0.4);

  /* ---------- b6: tested regularly ---------- */
  tl.to([eTub, ePack, eDhsv], { opacity: 1, duration: 0.5 }, bt('b6').start - 0.2);
  const check = (x, y, at) => {
    const g = S('g', { transform: `translate(${x} ${y})` });
    const gi = S('g');
    g.append(gi);
    gi.append(S('circle', { r: 18, fill: GRN, stroke: OUT, 'stroke-width': 3 }), S('path', { d: 'M-8 0 l6 7 l11 -14', fill: 'none', stroke: OUT, 'stroke-width': 4.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
    svg.append(g);
    tl.fromTo(gi, { scale: 0, svgOrigin: '0 0' }, { scale: 1, duration: 0.4, ease: 'back.out(3)', immediateRender: true }, at);
    tl.to(gi, { opacity: 0, duration: 0.5 }, bt('b6').end + 0.2);
  };
  check(X + 96, 648, w('b6', 'barrier') + 0.1); check(X + 212, 850, w('b6', 'barrier') + 0.3);
  check(X + 96, 232, w('b6', 'tree') + 0.1); check(X + 96, 352, w('b6', 'tree') + 0.3); check(X + 232, 292, w('b6', 'valves') - 0.1);
  const tst = H('div', { class: 'abs', style: { left: '96px', top: '470px', width: '560px', padding: '16px 24px', borderRadius: '16px', background: 'rgba(5,16,26,.92)', border: `2px solid ${GRN}` } },
    H('div', { style: { font: '800 28px var(--mono)', color: GRN, marginBottom: '6px' }, text: 'TESTED REGULARLY' }), H('div', { style: { font: '500 24px/1.35 var(--font)', color: '#DCE6EE' }, text: 'Barrier elements, including the tree valves, are tested to prove they still work.' }));
  el.append(tst);
  show(tst, w('b6', 'tested') - 0.4, 0.6, { x: -20, y: 0 }); hide(tst, bt('b6').end + 0.2, 0.5);
  sfx(w('b6', 'tested'), 'chime', 0.6);
  [eTub, ePack, eDhsv, eCas, eWell, eHang, eTree].forEach((e) => tl.to(e, { opacity: 0, duration: 0.6 }, bt('b6').end + 0.25));
}
