// Scene 19 – Vertical or horizontal? (495 – 554 s) -------------------------------------------------
// Side-by-side cut-away comparison, installation sequences, workover, then the standard tree.
import { H, S } from '../lib/svg.js';
import { makeScene } from '../lib/scene.js';
import { installDefs } from '../art/defs.js';
import { GateValve } from '../art/valve.js';
import { callout, tag } from '../lib/annot.js';

const CY = '#2ED0FF', OR = '#FF9A3C', YEL = '#FFC857', GRN = '#3BDB86', RED = '#FF3B5C', PUR = '#BC8FFF', BLU = '#4FA3FF';
const OUT = '#0B141C';

export function build(root, E) {
  const { T, tl, gsap, show, hide, fadeIn, fadeOut, sfx, animate, Flow, tweenNumber } = E;
  installDefs();
  const w = (id, word, n = 0) => T.word('types.' + id, word, n);
  const bt = (id) => T.beat('types.' + id);
  const { el, svg, sc } = makeScene(root, E, 'types', {});
  const t1s = sc.end;

  /* ------------------------------------------------------------------ geometry ---- */
  const SB = 800, SC = 0.9, CXV = 600, CXH = 1330;                 // seabed y, column scale, column centres
  const sx = (cx, x) => cx + x * SC, sy = (y) => SB + y * SC;         // column-local -> screen (before the b5 move)

  const steel = (g, x, y, wd, h, r = 6, op = 0.45, fill = 'url(#gSteelCut)') => g.append(
    S('rect', { x, y, width: wd, height: h, rx: r, fill, stroke: OUT, 'stroke-width': 3 }), S('rect', { x, y, width: wd, height: h, rx: r, fill: 'url(#pHatch)', opacity: op }));
  const dark = (g, x, y, wd, h) => g.append(S('rect', { x, y, width: wd, height: h, fill: '#050B11' }));
  const tubing = (g, y0) => g.append(S('rect', { x: -22, y: y0, width: 44, height: 242 - y0, fill: '#B3C4D2', stroke: OUT, 'stroke-width': 2.5 }), S('rect', { x: -13, y: y0, width: 26, height: 242 - y0, fill: '#050B11' }));

  const mkWellhead = (parent) => {
    const g = S('g');
    parent.append(g);
    g.append(S('rect', { x: -340, y: 0, width: 680, height: 244, fill: 'url(#gSeabed)' }), S('path', { d: 'M-340 0 H340', stroke: '#3A4F5E', 'stroke-width': 4 }),
      S('rect', { x: -66, y: 0, width: 14, height: 244, fill: '#7A93A8', stroke: OUT, 'stroke-width': 2 }), S('rect', { x: 52, y: 0, width: 14, height: 244, fill: '#7A93A8', stroke: OUT, 'stroke-width': 2 }));
    steel(g, -100, -150, 200, 150, 8);
    dark(g, -52, -150, 104, 150);
    g.append(S('rect', { x: -52, y: -62, width: 16, height: 10, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 2 }), S('rect', { x: 36, y: -62, width: 16, height: 10, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 2 }),
      S('rect', { x: -116, y: -166, width: 64, height: 18, rx: 4, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 3 }), S('rect', { x: 52, y: -166, width: 64, height: 18, rx: 4, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 3 }));
    return g;
  };
  const collar = (g) => { steel(g, -120, -198, 240, 34, 6, 0.3); g.append(S('rect', { x: -130, y: -190, width: 14, height: 18, rx: 3, fill: '#EAF1F6', stroke: OUT, 'stroke-width': 2 }), S('rect', { x: 116, y: -190, width: 14, height: 18, rx: 3, fill: '#EAF1F6', stroke: OUT, 'stroke-width': 2 })); };

  // columns (positioned with GSAP so the vertical tree can move / scale later)
  const colV = S('g'), colH = S('g');
  svg.append(colV, colH);
  gsap.set(colV, { x: CXV, y: SB, scale: SC }); gsap.set(colH, { x: CXH, y: SB, scale: SC });

  /* ---- vertical tree ---- */
  const whV = mkWellhead(colV);
  const hangV = S('g'), treeV = S('g');
  colV.append(hangV, treeV);
  tubing(hangV, -58);
  steel(hangV, -50, -112, 100, 56, 5, 0.25, '#A9BBCA');
  dark(hangV, -13, -112, 26, 56);
  hangV.append(S('rect', { x: -54, y: -100, width: 8, height: 12, fill: '#EAF1F6', stroke: OUT, 'stroke-width': 1.5 }), S('rect', { x: 46, y: -100, width: 8, height: 12, fill: '#EAF1F6', stroke: OUT, 'stroke-width': 1.5 }));
  collar(treeV);
  steel(treeV, -92, -432, 184, 234, 8);
  dark(treeV, -18, -440, 36, 276);
  steel(treeV, 92, -358, 160, 48, 4, 0.35);
  dark(treeV, 18, -347, 232, 26);
  treeV.append(S('rect', { x: 250, y: -372, width: 14, height: 76, rx: 3, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 2.5 }), S('rect', { x: -36, y: -456, width: 72, height: 26, rx: 5, fill: '#5C7384', stroke: OUT, 'stroke-width': 3 }));
  const vPMV = GateValve(treeV, { x: 0, y: -250, bw: 36, act: 'fs', f0: 1 });
  const vPSV = GateValve(treeV, { x: 0, y: -396, bw: 36, act: 'fs', f0: 0 });
  const vPWV = GateValve(treeV, { x: 176, y: -334, rot: 90, bw: 26, act: 'fs', f0: 1 });

  /* ---- horizontal tree ---- */
  const whH = mkWellhead(colH);
  const treeH = S('g'), hangH = S('g'), capH = S('g');
  colH.append(treeH, hangH, capH);
  collar(treeH);
  steel(treeH, -114, -404, 228, 208, 8);
  dark(treeH, -68, -404, 136, 208); dark(treeH, -52, -200, 104, 40);
  steel(treeH, 114, -312, 218, 44, 4, 0.35);
  dark(treeH, 68, -303, 262, 26);
  treeH.append(S('rect', { x: 330, y: -326, width: 14, height: 72, rx: 3, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 2.5 }));
  const hPMV = GateValve(treeH, { x: 158, y: -290, rot: 90, bw: 26, act: 'fs', f0: 1 });
  const hPWV = GateValve(treeH, { x: 268, y: -290, rot: 90, bw: 26, act: 'fs', f0: 1 });
  tubing(hangH, -248);
  steel(hangH, -62, -340, 124, 94, 6, 0.25, '#A9BBCA');
  dark(hangH, -13, -304, 26, 58); dark(hangH, 13, -297, 56, 14);
  hangH.append(S('rect', { x: -66, y: -322, width: 8, height: 14, fill: '#EAF1F6', stroke: OUT, 'stroke-width': 1.5 }), S('rect', { x: 58, y: -322, width: 8, height: 14, fill: '#EAF1F6', stroke: OUT, 'stroke-width': 1.5 }));
  steel(capH, -76, -430, 152, 28, 5, 0.3, '#7E94A6');
  capH.append(S('rect', { x: -14, y: -444, width: 28, height: 16, rx: 3, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 2 }));

  // production flow (orange dots) – inside the column groups
  const flV = Flow(colV, 'M0 236 V-334 H258', { color: OR, w: 8, gap: 22 });
  const flH = Flow(colH, 'M0 236 V-290 H336', { color: OR, w: 8, gap: 22 });

  /* ---------------------------------------------------------- headers + labels ---- */
  const headers = [];
  const header = (cx, text, sub, col, at) => {
    const g = S('g'); svg.append(g);
    const t = tag(g, { x: cx, y: 142, text, sub, accent: col, anchor: 'c', size: 28, mono: true });
    show(t.el, at, 0.6, { y: -14 });
    headers.push(t.el);
    return t;
  };
  const pillAt = (x, y, text, col, at, until, anchor = 'c', size = 24, mono = true, sub) => {
    const t = tag(svg, { x, y, text, sub, accent: col, anchor, size, mono });
    show(t.el, at, 0.45, { y: 10 });
    if (until !== undefined) hide(t.el, until, 0.4);
    return t;
  };
  const lab = (target, at, text, col, t0, t1, anchor) => {
    const c = callout(svg, { target, at, text, color: col, anchor, size: 26 });
    show(c.g, t0, 0.45, { y: 10 });
    if (t1 !== undefined) hide(c.g, t1, 0.4);
    return c;
  };

  /* ------------------------------------------------------------ install helpers ---- */
  const drop = (g, t, d, bottom, snd = true) => {            // bottom = lowest local y of the part
    const FALL = (-30 - SB) / SC - bottom;
    tl.fromTo(g, { y: FALL }, { y: 0, duration: d, ease: 'power2.in', immediateRender: true }, t);
    tl.to(g, { y: -7, duration: 0.09, ease: 'power1.out' }, t + d);
    tl.to(g, { y: 0, duration: 0.2, ease: 'bounce.out' }, t + d + 0.09);
    if (snd) sfx(t + d, 'clunk', 0.8);
  };

  /* ================================================================== b1 ==== */
  const b1 = bt('b1');
  fadeIn(whV, b1.start + 0.1, 0.8); fadeIn(whH, b1.start + 0.3, 0.8);
  // headers appear when each design is introduced
  header(CXV, 'VERTICAL TREE', 'VXT', BLU, w('b2', 'vertical') - 0.3);
  header(CXH, 'HORIZONTAL TREE', 'HXT', PUR, w('b3', 'horizontal') - 0.3);
  const divider = S('path', { d: 'M965 230 V930', stroke: 'rgba(170,200,225,.18)', 'stroke-width': 2, 'stroke-dasharray': '8 10' });
  svg.append(divider); fadeIn(divider, b1.start + 0.4, 0.6);
  const vs = H('div', { class: 'abs', style: { left: '890px', top: '470px', width: '140px', height: '140px', borderRadius: '50%', display: 'grid', placeItems: 'center', font: '800 54px var(--font)', color: '#06121C', background: YEL, boxShadow: '0 0 60px rgba(255,200,87,.45)' }, text: 'VS' });
  el.append(vs);
  show(vs, w('b1', 'two') - 0.2, 0.6, { scale: 0.5 }); hide(vs, bt('b2').start + 0.3, 0.5);
  sfx(w('b1', 'two') - 0.2, 'chime', 0.5);

  /* ================================================================== b2: vertical ==== */
  {
    const tH = w('b2', 'tubing') - 0.1, dH = 1.45;
    drop(hangV, tH, dH, 242);
    const tT = w('b2', 'tree', 1) - 0.6, dT = 1.7;
    drop(treeV, tT, dT, -164);
    // the collar clamps close once the tree has landed
    const tLand = tT + dT + 0.3;
    sfx(tLand, 'tick', 0.7);
    const tl_ = bt('b3').start - 0.2;
    lab([sx(CXV, -50), sy(-86)], [370, sy(-110)], 'Tubing hanger', BLU, w('b2', 'hanger'), tl_, 'r');
    lab([sx(CXV, -100), sy(-40)], [370, sy(-20)], 'Wellhead', '#93A8B8', w('b2', 'wellhead') - 0.2, tl_, 'r');
    lab([sx(CXV, -92), sy(-300)], [370, sy(-330)], 'Tree', BLU, w('b2', 'tree', 1) + 1.0, tl_, 'r');
    flV.show(tLand + 0.4, 0.5); flV.speed(tLand + 0.4, 70, 1.6);
  }

  /* ================================================================== b3: horizontal ==== */
  {
    const tT = w('b3', 'tree', 1) - 0.9, dT = 1.7;
    drop(treeH, tT, dT, -164);
    const tH = w('b3', 'tubing') - 0.2, dH = 1.5;
    drop(hangH, tH, dH, 242);
    drop(capH, tH + dH + 0.15, 0.55, -402, false);
    sfx(tH + dH + 0.7, 'tick', 0.7);
    const tl_ = bt('b4').start - 0.2;
    lab([sx(CXH, -114), sy(-340)], [1170, sy(-380)], 'Tree', PUR, w('b3', 'tree', 1) + 0.9, tl_, 'r');
    lab([sx(CXH, -62), sy(-290)], [1170, sy(-250)], 'Tubing hanger', PUR, w('b3', 'hanger'), tl_, 'r');
    // production leaves sideways
    flH.show(w('b3', 'production') - 0.2, 0.5); flH.speed(w('b3', 'production') - 0.2, 70, 1.6);
    const side = pillAt(sx(CXH, 356), sy(-290), 'OUT SIDEWAYS', OR, w('b3', 'sideways') - 0.1, bt('b4').start + 0.3, 'l', 24);
    // arrow pulse along the horizontal outlet
    const ar = S('path', { d: `M${sx(CXH, 120)} ${sy(-290)} H${sx(CXH, 330)}`, stroke: OR, 'stroke-width': 7, 'stroke-linecap': 'round', fill: 'none', opacity: 0 });
    svg.append(ar);
    tl.fromTo(ar, { opacity: 0 }, { opacity: 0.35, duration: 0.3, immediateRender: false }, w('b3', 'sideways') - 0.1);
    tl.to(ar, { opacity: 0, duration: 0.5 }, bt('b4').start + 0.3);
  }

  /* ================================================================== b4: the workover ==== */
  {
    const tc = w('b4', 'completion');
    const tp = w('b4', 'pulled');
    const tl_ = bt('b5').start - 0.3;
    // the completion is the hanger + tubing: highlight it in both designs
    const tubV = S('rect', { x: sx(CXV, -26), y: sy(-116), width: 52 * SC, height: 360 * SC, rx: 4, fill: 'none', stroke: OR, 'stroke-width': 4, opacity: 0 });
    const tubH = S('rect', { x: sx(CXH, -26), y: sy(-250), width: 52 * SC, height: 500 * SC, rx: 4, fill: 'none', stroke: OR, 'stroke-width': 4, opacity: 0 });
    svg.append(tubV, tubH);
    [tubV, tubH].forEach((r) => { tl.fromTo(r, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: false }, tc - 0.1); tl.to(r, { opacity: 0, duration: 0.4 }, tp + 0.2); });
    lab([sx(CXH, -22), sy(40)], [1170, sy(-10)], 'The completion', OR, tc - 0.1, tp + 0.3, 'r');
    lab([sx(CXV, -22), sy(40)], [370, sy(-10)], 'The completion', OR, tc - 0.1, tp + 0.3, 'r');
    flV.hide(tc - 0.3, 0.5); flH.hide(tc - 0.3, 0.5);
    flV.speed(tc - 0.3, 0, 0.5); flH.speed(tc - 0.3, 0, 0.5);
    // horizontal: the completion comes straight out; the tree stays
    const LIFT = -220;
    tl.to(capH, { y: -190, duration: 0.9, ease: 'power2.inOut' }, tp - 0.4);
    tl.to(hangH, { y: LIFT, duration: 1.7, ease: 'power2.inOut' }, tp + 0.3);
    sfx(tp, 'slide', 0.5);
    pillAt(CXH - 80, 850, '1 · PULL THE COMPLETION', GRN, tp + 0.2, tl_, 'r', 24);
    pillAt(CXH - 80, 905, 'TREE STAYS IN PLACE', GRN, w('b4', 'tree') - 0.1, tl_, 'r', 24);
    // vertical: the tree has to come off first
    const tv = w('b4', 'lifting') - 0.2;
    tl.to(treeV, { y: -210, duration: 1.6, ease: 'power2.inOut' }, tv);
    sfx(tv, 'slide', 0.5);
    pillAt(CXV - 80, 850, '1 · LIFT THE TREE OFF', RED, tv + 0.2, tl_, 'r', 24);
    const tv2 = tv + 2.0;
    tl.to(hangV, { y: LIFT, duration: 1.7, ease: 'power2.inOut' }, tv2);
    sfx(tv2, 'slide', 0.5);
    pillAt(CXV - 80, 905, '2 · PULL THE COMPLETION', OR, tv2 + 0.2, tl_, 'r', 24);
    // Norne
    const tn = w('b4', 'Norne') - 0.1;
    const nb = H('div', { class: 'abs', style: { left: '800px', top: '430px', width: '330px', padding: '12px 18px', borderRadius: '16px', background: 'rgba(5,16,26,.92)', border: `2px solid ${PUR}`, textAlign: 'center' } },
      H('div', { style: { font: '800 30px var(--mono)', color: PUR }, text: 'NORNE · 1997' }), H('div', { style: { font: '500 21px var(--font)', color: '#DCE6EE', marginTop: '4px' }, text: 'first horizontal trees on the Norwegian shelf' }));
    el.append(nb);
    show(nb, tn, 0.6, { y: 14 }); hide(nb, tl_, 0.5);
    sfx(tn, 'chime', 0.5);
  }

  /* ================================================================== b5: the standard tree ==== */
  const CXV2 = 470, SC2 = 1.15;
  const sx2 = (x) => CXV2 + x * SC2, sy2 = (y) => SB + y * SC2;
  {
    const t0 = bt('b5').start;
    // the horizontal column leaves, the vertical one re-installs and moves to the left
    fadeOut(colH, t0 - 0.3, 0.7);
    headers.forEach((h_) => hide(h_, t0 - 0.3, 0.5));
    tl.to(hangV, { y: 0, duration: 1.3, ease: 'power2.in' }, t0 - 0.2);
    tl.to(treeV, { y: 0, duration: 1.5, ease: 'power2.inOut' }, t0 + 0.8);
    sfx(t0 + 1.1, 'clunk', 0.8); sfx(t0 + 2.3, 'tick', 0.7);
    tl.to(colV, { x: CXV2, scale: SC2, duration: 1.8, ease: 'power3.inOut' }, t0 + 0.2);
    fadeOut(divider, t0 - 0.2, 0.5);
    // spec card (right)
    const card = H('div', { class: 'abs', style: { left: '940px', top: '230px', width: '884px', padding: '30px 36px', borderRadius: '24px', background: 'linear-gradient(160deg,rgba(18,44,66,.9),rgba(8,24,38,.92))', border: '1.5px solid rgba(170,200,225,.22)', boxShadow: '0 22px 60px rgba(0,0,0,.4)' } },
      H('div', { class: 'kicker', style: { color: GRN, marginBottom: '14px', fontSize: '24px' }, text: 'Standard tree' }),
      H('div', { class: 'h3', style: { fontSize: '64px' }, html: 'Vertical tree · <span style="color:#FFC857">VXT</span>' }),
      H('div', { style: { font: '500 36px var(--font)', color: '#AFC0CE', marginTop: '14px' }, text: 'Developed with Aker Solutions' }));
    el.append(card);
    show(card, w('b5', 'Equinor') - 0.3, 0.7, { x: 30, y: 0 });
    hide(card, w('b6', 'seven-by-five') - 0.7, 0.5, { x: 30 });
    const tl_ = bt('b6').start - 0.2;
    // standard-tree badge on the drawing
    const tg = tag(svg, { x: sx2(0), y: 150, text: 'EQUINOR STANDARD VXT', accent: GRN, anchor: 'c', size: 28, mono: true });
    show(tg.el, w('b5', 'standard') - 0.2, 0.6, { y: -12 });
    hide(tg.el, w('b6', 'module') - 0.6, 0.4);
    // flows back on
    flV.show(t0 + 2.6, 0.5); flV.speed(t0 + 2.6, 70, 1.4);
  }

  /* ================================================================== b6: sizes + flow module ==== */
  {
    const t0 = bt('b6').start;
    // bore-size chips
    const mkSize = (txt, a, b, left) => {
      const c = H('div', { class: 'abs', style: { left: left + 'px', top: '230px', width: '430px', padding: '28px 32px', borderRadius: '24px', background: 'linear-gradient(160deg,rgba(18,44,66,.9),rgba(8,24,38,.92))', border: `1.5px solid rgba(170,200,225,.22)` } });
      const svgI = S('svg', { viewBox: '0 0 330 130', width: 330, height: 130, style: { display: 'block', overflow: 'visible', flex: 'none' } });
      svgI.append(S('circle', { cx: 70, cy: 65, r: a * 8, fill: 'rgba(46,208,255,.12)', stroke: CY, 'stroke-width': 5 }), S('circle', { cx: 232, cy: 65, r: b * 8, fill: 'rgba(255,200,87,.12)', stroke: YEL, 'stroke-width': 5 }),
        S('text', { x: 70, y: 74, 'text-anchor': 'middle', fill: CY, 'font-size': 28, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: a + '"' }), S('text', { x: 232, y: 74, 'text-anchor': 'middle', fill: YEL, 'font-size': 28, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: b + '"' }));
      c.append(H('div', { style: { font: '800 84px var(--mono)', color: '#EEF4F9', marginBottom: '18px' }, text: txt }), svgI);
      el.append(c);
      return c;
    };
    const s75 = mkSize('7 × 5', 7, 5, 940), s77 = mkSize('7 × 7', 7, 7, 1394);
    show(s75, w('b6', 'seven-by-five') - 0.3, 0.6, { y: 24 });
    show(s77, w('b6', 'seven-by-seven') - 0.3, 0.6, { y: 24 });
    const cap = H('div', { class: 'abs', style: { left: '940px', top: '560px', font: '500 32px var(--font)', color: '#AFC0CE' }, text: 'Named after their bore sizes (inches)' });
    el.append(cap);
    show(cap, w('b6', 'named') - 0.2, 0.5, { y: 10 });
    [s75, s77, cap].forEach((e_) => hide(e_, w('b6', 'flow') - 0.5, 0.5));
    // flow module on the drawing: dashed box around the wing
    const mod = S('g', { opacity: 0 });
    mod.append(S('rect', { x: 100, y: -520, width: 190, height: 262, rx: 14, fill: 'rgba(188,143,255,.12)', stroke: PUR, 'stroke-width': 4, 'stroke-dasharray': '14 9' }));
    colV.append(mod);
    fadeIn(mod, w('b6', 'module') - 0.3, 0.6);
    const mt = tag(svg, { x: sx2(96), y: sy2(-536), text: 'FLOW MODULE', accent: PUR, anchor: 'r', size: 26, mono: true });
    show(mt.el, w('b6', 'module') - 0.2, 0.5, { y: -10 }); hide(mt.el, bt('b6').end + 0.0, 0.4);
    flV.hide(w('b6', 'flow') - 0.2, 0.4); flV.speed(w('b6', 'flow') - 0.2, 0, 0.3);
    // three duties
    const duties = [
      { key: 'producer', name: 'PRODUCER', sub: 'oil / gas out of the well', col: OR, dir: 1, ic: 'M-18 10 V-12 M-28 -2 L-18 -14 L-8 -2' },
      { key: 'gas', name: 'GAS INJECTOR', sub: 'gas into the reservoir', col: YEL, dir: -1, ic: 'M-18 -12 V10 M-28 0 L-18 12 L-8 0' },
      { key: 'water', name: 'WATER INJECTOR', sub: 'water into the reservoir', col: CY, dir: -1, ic: 'M-18 -12 V10 M-28 0 L-18 12 L-8 0' },
    ];
    const dutyCards = duties.map((d, i) => {
      const c = H('div', { class: 'abs', style: { left: (940 + i * 300) + 'px', top: '230px', width: '284px', padding: '26px 24px', borderRadius: '22px', background: 'linear-gradient(160deg,rgba(18,44,66,.9),rgba(8,24,38,.92))', border: `2px solid rgba(170,200,225,.22)`, boxSizing: 'border-box' } });
      const ic = S('svg', { viewBox: '-40 -30 80 60', width: 130, height: 98, style: { display: 'block', overflow: 'visible' } }, S('path', { d: d.ic, fill: 'none', stroke: d.col, 'stroke-width': 6, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }), S('circle', { cx: 18, cy: 0, r: 12, fill: 'none', stroke: d.col, 'stroke-width': 4, opacity: 0.6 }));
      c.append(ic, H('div', { style: { font: '800 25px var(--mono)', color: d.col, marginTop: '14px', whiteSpace: 'nowrap' }, text: d.name }), H('div', { style: { font: '500 24px/1.3 var(--font)', color: '#AFC0CE', marginTop: '10px' }, text: d.sub }));
      el.append(c);
      return c;
    });
    // each duty: card + flow direction through the module
    const mf = [];
    const WP = 'M110 -334 H262';
    duties.forEach((d, i) => {
      const t = w('b6', d.key === 'producer' ? 'producer' : d.key === 'gas' ? 'gas' : 'water');
      const next = i < 2 ? w('b6', i === 0 ? 'gas' : 'water') : bt('b7').start - 0.2;
      show(dutyCards[i], t - 0.3, 0.55, { y: 24 });
      tl.to(dutyCards[i], { borderColor: d.col, duration: 0.3 }, t);
      if (i < 2) tl.to(dutyCards[i], { borderColor: 'rgba(170,200,225,.22)', duration: 0.3 }, next);
      const f = Flow(colV, d.dir > 0 ? WP : 'M262 -334 H110', { color: d.col, w: 8, gap: 22 });
      f.show(t, 0.4); f.speed(t, 70, 0.8);
      f.hide(next - 0.1, 0.35);
      mf.push(f);
      sfx(t, 'tick', 0.5);
    });
    dutyCards.forEach((c) => hide(c, bt('b6').end + 0.0, 0.4));
    // module label stays until b7 starts
    tl.to(mod, { opacity: 0, duration: 0.5 }, bt('b6').end + 0.0);
  }

  /* ================================================================== b7: weight + vessels ==== */
  {
    const P0 = { x: 940, y: 190 };
    const panel = S('g', { opacity: 0 });
    svg.append(panel);
    panel.append(S('rect', { x: P0.x, y: P0.y, width: 884, height: 700, rx: 24, fill: 'rgba(5,16,26,.9)', stroke: 'rgba(170,200,225,.3)', 'stroke-width': 1.8 }),
      S('text', { x: P0.x + 34, y: P0.y + 52, fill: '#AFC0CE', 'font-size': 22, 'font-weight': 800, 'letter-spacing': '0.16em', text: 'TREE WEIGHT' }));
    // bars
    const bx1 = P0.x + 90, bx2 = P0.x + 330, base = P0.y + 330, H100 = 240, BW = 180;
    const barOld = S('rect', { x: bx1, y: base - H100, width: BW, height: H100, rx: 8, fill: '#6F879A', stroke: OUT, 'stroke-width': 3, opacity: 0.9 });
    const barNew = S('rect', { x: bx2, y: base - H100, width: BW, height: H100, rx: 8, fill: GRN, stroke: OUT, 'stroke-width': 3 });
    const bl = (x, l1, l2, col) => [S('text', { x, y: base + 38, 'text-anchor': 'middle', fill: col, 'font-size': 25, 'font-weight': 800, text: l1 }), S('text', { x, y: base + 68, 'text-anchor': 'middle', fill: col, 'font-size': 25, 'font-weight': 800, text: l2 })];
    panel.append(barOld, barNew, S('path', { d: `M${bx1 - 30} ${base} H${bx2 + BW + 30}`, stroke: '#AFC0CE', 'stroke-width': 3 }), ...bl(bx1 + BW / 2, 'EARLIER', 'TREES', '#AFC0CE'), ...bl(bx2 + BW / 2, 'NEW STANDARD', 'TREE', GRN));
    const half = S('text', { x: bx2 + BW / 2, y: base - 42, 'text-anchor': 'middle', fill: '#06121C', 'font-size': 72, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: '≈ ½', opacity: 0 });
    const dashed = S('path', { d: `M${bx2 - 14} ${base - H100} H${bx2 + BW + 14}`, stroke: '#AFC0CE', 'stroke-width': 2.5, 'stroke-dasharray': '9 8', opacity: 0 });
    const claim = S('g', { opacity: 0 }, S('text', { x: P0.x + 590, y: P0.y + 190, fill: '#EEF4F9', 'font-size': 44, 'font-weight': 800, text: 'Roughly half' }), S('text', { x: P0.x + 590, y: P0.y + 238, fill: '#EEF4F9', 'font-size': 44, 'font-weight': 800, text: 'the weight' }), S('text', { x: P0.x + 590, y: P0.y + 284, fill: '#AFC0CE', 'font-size': 27, 'font-weight': 500, text: 'of earlier trees' }));
    panel.append(half, dashed, claim, S('text', { x: P0.x + 850, y: P0.y + 52, 'text-anchor': 'end', fill: '#7F96A8', 'font-size': 19, 'font-weight': 500, text: 'according to Aker Solutions' }));
    fadeIn(panel, w('b7', 'Aker') + 0.05, 0.7);
    fadeOut(panel, T.scene('types').end - 0.3, 0.5);
    const tHalf = w('b7', 'roughly') - 0.1;
    const pb = { h: H100 };
    tl.fromTo(pb, { h: H100 }, { h: H100 / 2, duration: 1.1, ease: 'power3.inOut', onUpdate: () => { barNew.setAttribute('y', (base - pb.h).toFixed(1)); barNew.setAttribute('height', pb.h.toFixed(1)); }, immediateRender: false }, tHalf);
    [dashed, half, claim].forEach((e_) => tl.fromTo(e_, { opacity: 0 }, { opacity: e_ === dashed ? 0.9 : 1, duration: 0.4, immediateRender: false }, tHalf + 0.8));
    sfx(tHalf + 0.9, 'chime', 0.5);
    // vessels (outer wrapper carries the slide, inner group the static placement)
    const vess = (s_, col, strokeW = 3) => {
      const g = S('g', { transform: `scale(${s_})`, fill: 'none', stroke: col, 'stroke-width': strokeW, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' });
      g.append(S('path', { d: 'M-120 0 H110 L88 30 H-96 Z' }), S('path', { d: 'M20 0 V-34 H64 V0 M30 -34 V-52 H54 V-34' }), S('path', { d: 'M-70 0 V-60 L-30 -96 M-70 -60 H-24' }), S('path', { d: 'M-130 40 q22 -10 44 0 t44 0 t44 0 t44 0 t44 0 t44 0', opacity: 0.5 }));
      return g;
    };
    const mkV = (x, y, s_, col, sw) => { const wrap = S('g', { opacity: 0 }); const place = S('g', { transform: `translate(${x} ${y})` }); place.append(vess(s_, col, sw)); wrap.append(place); panel.append(wrap); return wrap; };
    const vBig = mkV(P0.x + 250, P0.y + 560, 1.15, '#6F879A', 3), vSmall = mkV(P0.x + 650, P0.y + 560, 0.78, GRN, 4);
    const tv = w('b7', 'smaller') - 0.4;
    tl.fromTo(vBig, { opacity: 0 }, { opacity: 0.85, duration: 0.5, immediateRender: false }, tv - 0.8);
    tl.fromTo(vSmall, { opacity: 0, x: 60 }, { opacity: 1, x: 0, duration: 0.7, ease: 'power3.out', immediateRender: false }, tv);
    const vl = S('g', { opacity: 0 }, S('text', { x: P0.x + 650, y: P0.y + 618, 'text-anchor': 'middle', fill: GRN, 'font-size': 27, 'font-weight': 800, text: 'smaller vessels' }), S('text', { x: P0.x + 250, y: P0.y + 618, 'text-anchor': 'middle', fill: '#7F96A8', 'font-size': 27, 'font-weight': 700, text: 'larger vessel' }));
    panel.append(vl);
    tl.fromTo(vl, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: false }, tv + 0.5);
    // Barents Sea chip
    const bs = tag(svg, { x: P0.x + 442, y: P0.y + 664, text: 'BARENTS SEA', accent: YEL, anchor: 'c', size: 28, mono: true });
    show(bs.el, w('b7', 'Barents') - 0.2, 0.6, { y: 12 }); hide(bs.el, T.scene('types').end - 0.3, 0.4);
  }
}
