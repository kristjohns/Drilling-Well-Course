// Scene 22 – Recap + closing + sources (640 – 677 s) ----------------------------------------------
import { H, S } from '../lib/svg.js';
import { makeScene } from '../lib/scene.js';
import { installDefs } from '../art/defs.js';
import { icons } from '../art/icons.js';
import { GateValve } from '../art/valve.js';
import { treeGlyph } from './ncs.js';

const CY = '#2ED0FF', OR = '#FF9A3C', YEL = '#FFC857', GRN = '#3BDB86', RED = '#FF3B5C', PUR = '#BC8FFF', BLU = '#4A82FF', ROSE = '#FF4F6D';

export function build(root, E) {
  const { T, tl, gsap, show, hide, fadeIn, fadeOut, sfx, animate, Flow } = E;
  installDefs();
  const w = (id, word, n = 0) => T.word('recap.' + id, word, n);
  const bt = (id) => T.beat('recap.' + id);
  const { el, svg, sc } = makeScene(root, E, 'recap', {});

  /* ---------------------------------------------------------------- heading ---- */
  const h2 = H('div', { class: 'h2 abs', style: { left: '96px', top: '140px', fontSize: '58px' }, text: 'Recap' });
  el.append(h2);
  show(h2, bt('b1').start, 0.6);
  hide(h2, bt('b6').start - 0.35, 0.4);
  const tCards = bt('b6').start - 0.35;

  /* ------------------------------------------------------------------- cards ---- */
  const CW = 840, CH = 340, X0 = 96, Y0 = 230, GX = 48, GY = 30;
  let cardIdx = 0;
  const mkCard = (col, row, title, color, tIn, tOut) => {
    const idx = cardIdx++;
    const wrap = S('g', { transform: `translate(${X0 + col * (CW + GX)} ${Y0 + row * (CH + GY)})` });
    const g = S('g');
    wrap.append(g);
    svg.append(wrap);
    const edge = S('rect', { width: CW, height: CH, rx: 26, fill: 'none', stroke: color, 'stroke-width': 3.5, opacity: 0 });
    g.append(S('rect', { width: CW, height: CH, rx: 26, fill: 'rgba(8,26,42,.88)', stroke: 'rgba(170,200,225,.26)', 'stroke-width': 1.8 }), edge,
      S('text', { x: 36, y: 56, fill: color, 'font-size': 24, 'font-weight': 800, 'letter-spacing': '0.16em', text: title }));
    tl.fromTo(g, { autoAlpha: 0, y: 40 }, { autoAlpha: 0.4, y: 0, duration: 0.6, ease: 'power3.out', immediateRender: true }, bt('b1').start + 0.5 + idx * 0.14);
    tl.to(g, { autoAlpha: 1, duration: 0.35 }, tIn - 0.15);
    tl.to(edge, { opacity: 1, duration: 0.3 }, tIn);
    tl.to(edge, { opacity: 0, duration: 0.5 }, tOut);
    tl.to(g, { autoAlpha: 0.7, duration: 0.6 }, tOut);
    tl.to(wrap, { opacity: 0, duration: 0.5 }, tCards);
    const content = S('g');                     // everything but the frame appears at the card's beat
    g.append(content);
    fadeIn(content, tIn - 0.1, 0.45);
    return { g: content, edge };
  };

  /* --- 1. four jobs (b2) --- */
  {
    const c = mkCard(0, 0, 'FOUR JOBS', OR, bt('b2').start, bt('b3').start - 0.2);
    const jobs = [
      { ic: icons.flow, col: OR, l: ['Control', 'the flow'], t: w('b2', 'controls') },
      { ic: icons.shield, col: ROSE, l: ['Isolate', 'the well'], t: w('b2', 'isolates') },
      { ic: icons.inject, col: PUR, l: ['Inject &', 'monitor'], t: w('b2', 'injects') },
      { ic: icons.tool, col: CY, l: ['Give', 'access'], t: w('b2', 'gives') },
    ];
    jobs.forEach((j, i) => {
      const gi = S('g', { opacity: 0 });
      const place = S('g', { transform: `translate(${105 + i * 210} 156) scale(1.0)` });
      place.append(j.ic('#EEF4F9', j.col));
      gi.append(place, S('text', { x: 105 + i * 210, y: 275, 'text-anchor': 'middle', fill: '#EEF4F9', 'font-size': 31, 'font-weight': 700, text: j.l[0] }), S('text', { x: 105 + i * 210, y: 311, 'text-anchor': 'middle', fill: '#AFC0CE', 'font-size': 28, 'font-weight': 500, text: j.l[1] }));
      c.g.append(gi);
      tl.fromTo(gi, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: true }, j.t - 0.15);
      sfx(j.t, 'tick', 0.5);
    });
  }

  /* --- 2. fail-safe (b3) --- */
  {
    const c = mkCard(1, 0, 'FAIL-SAFE', YEL, bt('b3').start, bt('b4').start - 0.2);
    const vx = 600, vy = 190, vsc = 1.45, bwv = 34;
    c.g.append(S('path', { d: `M${vx} ${vy - 120} V${vy + 125}`, stroke: '#93A8B8', 'stroke-width': bwv * vsc + 14, fill: 'none' }), S('path', { d: `M${vx} ${vy - 120} V${vy + 125}`, stroke: '#050B11', 'stroke-width': bwv * vsc, fill: 'none' }));
    const valve = GateValve(c.g, { x: vx, y: vy, bw: bwv, act: 'fs', f0: 0, scale: vsc });
    const f = Flow(c.g, `M${vx} ${vy - 120} V${vy + 125}`, { color: OR, w: 9, gap: 24 });
    const tOpen = w('b3', 'held') - 0.2, tClose = w('b3', 'closed');
    valve.open(tOpen, 1.2);
    f.show(tOpen + 0.9, 0.4); f.speed(tOpen + 0.9, 60, 0.8);
    const lab = (x, y, text, col, anchor = 'start') => S('text', { x, y, 'text-anchor': anchor, fill: col, 'font-size': 26, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text });
    const lPress = S('g', { opacity: 0 }, lab(36, 120, 'HYDRAULIC', CY), lab(36, 152, 'PRESSURE', CY), S('path', { d: 'M36 178 h150 l-14 -12 m14 12 l-14 12', fill: 'none', stroke: CY, 'stroke-width': 4, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
    const lSpring = S('g', { opacity: 0 }, lab(36, 120, 'SPRING', YEL), lab(36, 152, 'PUSHES SHUT', YEL));
    c.g.append(lPress, lSpring);
    tl.fromTo(lPress, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: true }, w('b3', 'hydraulic') - 0.2);
    tl.to(lPress, { opacity: 0, duration: 0.3 }, tClose - 0.2);
    tl.fromTo(lSpring, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: false }, tClose - 0.1);
    valve.close(tClose + 0.2, 0.7, 'power3.in');
    f.speed(tClose + 0.2, 0, 0.5); f.hide(tClose + 0.8, 0.4);
    sfx(tClose + 0.8, 'clunk', 0.7);
    const safe = S('g', { opacity: 0 }, S('rect', { x: 36, y: 262, width: 250, height: 52, rx: 14, fill: 'rgba(14,70,40,.9)', stroke: GRN, 'stroke-width': 3 }), S('text', { x: 56, y: 297, fill: GRN, 'font-size': 29, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: '✓ FAILS SAFE' }));
    c.g.append(safe);
    tl.fromTo(safe, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: false }, w('b3', 'fails') - 0.1);
    sfx(w('b3', 'fails'), 'chime', 0.6);
  }

  /* --- 3. shutdown order (b4) --- */
  {
    const c = mkCard(0, 1, 'IN AN EMERGENCY', RED, bt('b4').start, bt('b5').start - 0.2);
    const chips = [
      { n: 1, name: 'PWV', sub: ['wing', 'valve'], t: w('b4', 'wing') },
      { n: 2, name: 'PMV', sub: ['master', 'valve'], t: w('b4', 'master') },
      { n: 3, name: 'DHSV', sub: ['downhole', 'safety valve'], t: w('b4', 'downhole') },
    ];
    chips.forEach((ch, i) => {
      const x = 30 + i * 270;
      const gi = S('g', { opacity: 0 });
      gi.append(S('rect', { x, y: 104, width: 246, height: 190, rx: 20, fill: i === 2 ? 'rgba(60,10,22,.9)' : 'rgba(12,30,46,.9)', stroke: i === 2 ? RED : 'rgba(170,200,225,.3)', 'stroke-width': i === 2 ? 3.5 : 2 }),
        S('circle', { cx: x + 50, cy: 160, r: 32, fill: i === 2 ? RED : '#FF8A9B' }), S('text', { x: x + 50, y: 172, 'text-anchor': 'middle', fill: '#06121C', 'font-size': 36, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: String(ch.n) }),
        S('text', { x: x + 94, y: 174, fill: '#EEF4F9', 'font-size': 42, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: ch.name }),
        S('text', { x: x + 26, y: 232, fill: '#AFC0CE', 'font-size': 28, 'font-weight': 500, text: ch.sub[0] }), S('text', { x: x + 26, y: 266, fill: '#AFC0CE', 'font-size': 28, 'font-weight': 500, text: ch.sub[1] }));
      c.g.append(gi);
      tl.fromTo(gi, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: true }, ch.t - 0.2);
      sfx(ch.t, 'tick', 0.5);
      if (i < 2) { const ar = S('text', { x: x + 258, y: 212, 'text-anchor': 'middle', fill: '#6F879A', 'font-size': 48, 'font-weight': 800, text: '›', opacity: 0 }); c.g.append(ar); tl.fromTo(ar, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: true }, ch.t + 0.3); }
    });
    const lastT = S('g', { opacity: 0 }, S('rect', { x: 30 + 2 * 270 + 130, y: 86, width: 108, height: 36, rx: 10, fill: RED }), S('text', { x: 30 + 2 * 270 + 184, y: 112, 'text-anchor': 'middle', fill: '#fff', 'font-size': 22, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: 'LAST' }));
    c.g.append(lastT);
    tl.fromTo(lastT, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: true }, w('b4', 'last') - 0.1);
  }

  /* --- 4. second barrier (b5) --- */
  {
    const c = mkCard(1, 1, 'THE SECOND BARRIER', BLU, bt('b5').start, bt('b6').start - 0.5);
    const y = 130;
    // reservoir · barrier 1 · barrier 2 (with the tree) · environment
    const res = S('g', { opacity: 0 }, S('path', { d: `M40 ${y + 96} C70 ${y + 54} 150 ${y + 54} 180 ${y + 96} L196 ${y + 136} H24 Z`, fill: 'url(#pSand)', stroke: '#8A5A22', 'stroke-width': 3 }), S('text', { x: 110, y: y + 172, 'text-anchor': 'middle', fill: OR, 'font-size': 22, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: 'RESERVOIR' }));
    const sh = (cx, col, label, op) => {
      const gg = S('g', { opacity: op });
      const p = S('g', { transform: `translate(${cx} ${y + 76}) scale(0.95)` });
      p.append(icons.shield('#EEF4F9', col));
      gg.append(p, S('text', { x: cx, y: y + 172, 'text-anchor': 'middle', fill: col, 'font-size': 22, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: label }));
      return gg;
    };
    const s1 = sh(330, BLU, 'BARRIER 1', 0), s2 = sh(520, ROSE, 'BARRIER 2', 0);
    const env = S('g', { opacity: 0 }, S('path', { d: `M650 ${y + 64} q18 -14 36 0 t36 0 t36 0`, fill: 'none', stroke: '#6FB6E0', 'stroke-width': 5, 'stroke-linecap': 'round' }), S('path', { d: `M650 ${y + 98} q18 -14 36 0 t36 0 t36 0`, fill: 'none', stroke: '#6FB6E0', 'stroke-width': 5, 'stroke-linecap': 'round', opacity: 0.6 }), S('text', { x: 722, y: y + 172, 'text-anchor': 'middle', fill: '#6FB6E0', 'font-size': 22, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: 'ENVIRONMENT' }));
    c.g.append(res, s1, s2, env);
    const arrows = [[210, 300], [360, 490], [550, 650]].map(([a, b], i) => { const p = S('path', { d: `M${a} ${y + 80} H${b}`, stroke: OR, 'stroke-width': 5, 'stroke-dasharray': '3 11', 'stroke-linecap': 'round', fill: 'none', opacity: 0 }); c.g.append(p); return p; });
    const tree = S('g', { opacity: 0 });
    treeGlyph(tree, 520, y + 86, 1.15, '#EEF4F9', 'rgba(255,79,109,.35)');
    c.g.append(tree);
    const cap = S('text', { x: 36, y: 90, fill: '#DCE6EE', 'font-size': 27, 'font-weight': 600, text: 'Casing + wellhead + tree' });
    c.g.append(cap); cap.setAttribute('opacity', 0);
    tl.fromTo(res, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: true }, w('b5', 'reservoir') - 0.1);
    tl.fromTo(s1, { opacity: 0 }, { opacity: 0.55, duration: 0.5, immediateRender: true }, w('b5', 'second') - 0.6);
    tl.fromTo(s2, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: true }, w('b5', 'second') - 0.1);
    tl.fromTo(cap, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: true }, w('b5', 'casing') - 0.1);
    tl.fromTo(tree, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: true }, w('b5', 'tree') - 0.1);
    tl.fromTo(env, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: true }, w('b5', 'barriers') - 0.1);
    arrows.forEach((a, i) => tl.fromTo(a, { opacity: 0 }, { opacity: 0.9, duration: 0.4, immediateRender: true }, w('b5', 'keep') + i * 0.12));
    sfx(w('b5', 'second'), 'chime', 0.5);
  }

  /* ---------------------------------------------------------- closing + sources ---- */
  const tEnd = bt('b6').start;
  const thanks = H('div', { class: 'abs', style: { left: '96px', top: '230px', width: '1500px' } },
    H('div', { class: 'kicker', style: { color: YEL, marginBottom: '16px' }, text: 'The Subsea Christmas Tree: How It Works' }),
    H('div', { class: 'h1', text: 'Thank you for watching' }));
  el.append(thanks);
  show(thanks, tEnd - 0.1, 0.9, { y: 30 });
  const srcT = tEnd + 2.0;
  const src = H('div', { class: 'abs', style: { left: '96px', top: '450px', width: '1728px' } },
    H('div', { class: 'kicker', style: { color: '#AFC0CE', marginBottom: '20px' }, text: 'Sources and further reading' }));
  const items = [
    ['Equinor', 'Åsgard subsea gas compression · Aasta Hansteen · Troll Phase 3 · Norne'],
    ['Aker Solutions', 'Subsea tree and Johan Castberg / Åsgard project material'],
    ['Norwegian Offshore Directorate', 'Field fact pages: Troll, Johan Castberg'],
    ['SPE Journal of Petroleum Technology', 'Johan Castberg first oil · Aasta Hansteen start-up'],
    ['World Oil · Offshore Magazine · Offshore Engineer', 'Subsea trees and the path to standardization · horizontal and vertical trees'],
    ['NORSOK D-010 · Offshore Norge', 'Well integrity and the two-barrier principle'],
  ];
  const grid = H('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', columnGap: '48px', rowGap: '20px' } });
  items.forEach(([a, b]) => grid.append(H('div', { style: { font: '500 27px/1.32 var(--font)', color: '#AFC0CE' } }, H('b', { style: { color: '#EEF4F9', fontWeight: 700 }, text: a + ' — ' }), b)));
  src.append(grid, H('div', { style: { font: '500 24px/1.4 var(--font)', color: '#7F96A8', marginTop: '30px' }, text: 'Illustrations are schematic; facility layouts and field positions are simplified. Check details against current company requirements and standards before use in training.' }));
  el.append(src);
  show(src, srcT, 0.9, { y: 24 });
  sfx(tEnd, 'chime', 0.5);
}
