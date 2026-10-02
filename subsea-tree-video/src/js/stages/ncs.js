// Scene 20 – Trees on the Norwegian shelf (554 – 590 s) -------------------------------------
// A vector map of the shelf; the camera hops between four fields. Facility layouts are schematic.
import { H, S } from '../lib/svg.js';
import { makeScene } from '../lib/scene.js';
import { installDefs } from '../art/defs.js';
import { MAP } from '../art/mapdata.js';
import { tag } from '../lib/annot.js';

const CY = '#2ED0FF', OR = '#FF9A3C', YEL = '#FFC857', GRN = '#3BDB86', PUR = '#BC8FFF';
const OUT = '#0B141C';

/** small subsea-tree glyph (for template icons / well grids) */
export function treeGlyph(g, cx, cy, s = 1, col = CY, fill = 'rgba(46,208,255,.18)') {
  const o = S('g', { transform: `translate(${cx} ${cy}) scale(${s})`, fill, stroke: col, 'stroke-width': 2.4, 'stroke-linejoin': 'round' });
  o.append(S('rect', { x: -15, y: 12, width: 30, height: 6, rx: 1.5 }), S('rect', { x: -9, y: -6, width: 18, height: 18, rx: 2 }), S('rect', { x: -5, y: -14, width: 10, height: 8, rx: 1.5 }),
    S('path', { d: 'M9 2 H21 V8 H9', fill: 'none' }), S('path', { d: 'M-3 -14 V-20 H3 V-14', fill: 'none' }));
  g.append(o);
  return o;
}

export function build(root, E) {
  const { T, tl, show, hide, fadeIn, fadeOut, sfx, animate, Cam, proj, Flow, tweenNumber } = E;
  installDefs();
  const w = (id, word, n = 0) => T.word('ncs.' + id, word, n);
  const bt = (id) => T.beat('ncs.' + id);
  const { el, svg, sc } = makeScene(root, E, 'ncs', {});
  const t0s = sc.start, t1s = sc.end;

  /* ---------------------------------------------------------------- map ---- */
  const SH = {
    over: { wx: 930, wy: 1230, sx: 1250, sy: 570, k: 0.56 },
    troll: { wx: 588, wy: 1664, sx: 1230, sy: 560, k: 4.2 },
    asgard: { wx: 762, wy: 1335, sx: 1230, sy: 560, k: 4.2 },
    aasta: { wx: 805, wy: 1170, sx: 1000, sy: 570, k: 4.0 },
    castberg: { wx: 1192, wy: 752, sx: 1000, sy: 570, k: 3.4 },
  };
  const mapG = S('g');
  svg.append(mapG);
  const cam = new Cam(mapG, SH.over);
  const ns = { 'vector-effect': 'non-scaling-stroke' };
  mapG.append(S('path', { d: MAP.grat, fill: 'none', stroke: 'rgba(140,190,230,.13)', 'stroke-width': 1, ...ns }));
  MAP.land.forEach((l) => mapG.append(S('path', { d: l.d, fill: l.name === 'Norway' ? '#17405F' : '#0E2940', stroke: l.name === 'Norway' ? '#6FA6D2' : '#3F6E96', 'stroke-width': 1.3, 'stroke-linejoin': 'round', ...ns })));
  mapG.append(S('path', { d: MAP.borders, fill: 'none', stroke: 'rgba(190,220,245,.2)', 'stroke-width': 1, ...ns }));

  // markers keep a constant on-screen size: counter-scale by the camera zoom every frame
  const scalers = [];
  const marker = (x, y, g) => { const outer = S('g'); outer.append(g); mapG.append(outer); scalers.push({ outer, x, y }); return outer; };
  animate(t0s - 0.6, t1s + 0.6, () => { const s = 1 / cam.s.k; scalers.forEach((m) => m.outer.setAttribute('transform', `translate(${m.x} ${m.y}) scale(${s.toFixed(5)})`)); });

  // sea names
  const seaTxt = (key, text) => { const g = S('g', { opacity: 0 }, S('text', { 'text-anchor': 'middle', fill: 'rgba(150,200,240,.6)', 'font-size': 22, 'font-weight': 700, 'letter-spacing': '0.34em', text })); marker(...MAP.seaPos[key], g); return g; };
  const seas = [seaTxt('north', 'NORTH SEA'), seaTxt('norwegian', 'NORWEGIAN SEA'), seaTxt('barents', 'BARENTS SEA')];

  // decorative field dots (selection of producing fields, approximate)
  const dots = MAP.dots.map(([x, y], i) => {
    const g = S('g', { opacity: 0 }, S('circle', { r: 11, fill: 'url(#gGlowOr)', opacity: 0.55 }), S('circle', { r: 4.2, fill: OR, stroke: '#2B1500', 'stroke-width': 1 }));
    marker(x, y, g);
    return g;
  });
  // pins
  const pinG = {};
  const mkPin = (key, name, sub) => {
    const [x, y] = MAP.pins[key];
    const g = S('g', { opacity: 0 });
    const pulse = S('circle', { r: 12, fill: 'none', stroke: YEL, 'stroke-width': 2 });
    g.append(pulse, S('circle', { r: 15, fill: 'url(#gGlowYel)', opacity: 0.7 }), S('circle', { r: 6.5, fill: YEL, stroke: '#2B1D00', 'stroke-width': 2 }));
    marker(x, y, g);                                   // attach first: tag() measures its text
    const lab = tag(g, { x: 22, y: 0, text: name, sub, accent: YEL, anchor: 'l', size: 26 });
    pinG[key] = { g, lab: lab.el, pulse };
    animate(t0s, t1s, (t) => { const p = (t * 0.8) % 1; pulse.setAttribute('r', (10 + p * 18).toFixed(1)); pulse.setAttribute('opacity', (0.8 * (1 - p)).toFixed(2)); });
    return pinG[key];
  };
  // map-unit helpers (overlays live in the map group and scale with the camera)
  const ov = (t_in, t_out) => { const g = S('g', { opacity: 0 }); mapG.append(g); fadeIn(g, t_in, 0.6); fadeOut(g, t_out, 0.5); return g; };
  const ringMap = (parent, x, y, r, col, at, until) => {
    const g = S('g', { opacity: 0 });
    const c1 = S('circle', { cx: x, cy: y, r, fill: 'none', stroke: col, 'stroke-width': 3, ...ns }), c2 = S('circle', { cx: x, cy: y, r, fill: 'none', stroke: col, 'stroke-width': 1.5, ...ns });
    g.append(c1, c2); parent.append(g);
    tl.fromTo(g, { opacity: 0 }, { opacity: 1, duration: 0.35, immediateRender: true }, at);
    if (until) tl.to(g, { opacity: 0, duration: 0.35 }, until);
    animate(at, until ?? t1s, (t) => { const p = ((t - at) / 1.2) % 1; c2.setAttribute('r', (r * (1 + p * 0.9)).toFixed(2)); c2.setAttribute('opacity', (0.55 * (1 - p)).toFixed(2)); });
  };
  const platform = (parent, x, y, label, sz = 1) => {
    const g = S('g', { transform: `translate(${x} ${y}) scale(${sz})` });
    g.append(S('rect', { x: -3.4, y: 0.4, width: 1.1, height: 2.6, fill: '#6F879A', stroke: OUT, 'stroke-width': 0.25 }), S('rect', { x: 2.3, y: 0.4, width: 1.1, height: 2.6, fill: '#6F879A', stroke: OUT, 'stroke-width': 0.25 }),
      S('rect', { x: -4.2, y: -1.5, width: 8.4, height: 2, rx: 0.3, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 0.28 }), S('rect', { x: -2.6, y: -3, width: 3, height: 1.5, fill: '#93A8B8', stroke: OUT, 'stroke-width': 0.22 }),
      S('rect', { x: 2.2, y: -4.6, width: 0.45, height: 3.1, fill: '#C4D2DD' }), S('path', { d: 'M2.42 -4.6 q-0.9 -0.9 0 -1.9 q0.9 0.9 0 1.9', fill: OR }),
      );
    parent.append(g);
    return g;
  };
  const fpso = (parent, x, y, label, sz = 1) => {
    const g = S('g', { transform: `translate(${x} ${y}) scale(${sz})` });
    g.append(S('path', { d: 'M-6 -0.2 H6.6 L5.2 2.6 H-5.4 Z', fill: '#93A8B8', stroke: OUT, 'stroke-width': 0.28 }), S('rect', { x: -2.4, y: -1.6, width: 3.6, height: 1.5, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 0.22 }),
      S('circle', { cx: 3.2, cy: -0.2, r: 0.9, fill: '#DCE6EE', stroke: OUT, 'stroke-width': 0.22 }), S('rect', { x: -5, y: -3.4, width: 0.4, height: 3.2, fill: '#C4D2DD' }), S('path', { d: 'M-4.8 -3.4 q-0.8 -0.8 0 -1.7 q0.8 0.8 0 1.7', fill: OR }));
    parent.append(g);
    return g;
  };
  const template = (parent, x, y, col = CY, at = 0, sz = 2.2) => {
    const g = S('g', { opacity: 0 });
    const ig = S('g', { transform: `translate(${x} ${y}) scale(${sz}) translate(${-x} ${-y})` });
    ig.append(S('rect', { x: x - 2.2, y: y - 1.5, width: 4.4, height: 3, rx: 0.5, fill: '#33485A', stroke: col, 'stroke-width': 0.35 }), S('rect', { x: x - 1.2, y: y - 0.9, width: 0.9, height: 1.8, fill: col, opacity: 0.8 }), S('rect', { x: x + 0.3, y: y - 0.9, width: 0.9, height: 1.8, fill: col, opacity: 0.8 }));
    g.append(ig);
    parent.append(g);
    tl.fromTo(g, { opacity: 0, scale: 0.4, svgOrigin: `${x} ${y}` }, { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(2.4)', immediateRender: true }, at);
    return g;
  };
  const line = (parent, d, col, at, v = 12, wdt = 0.9) => { const f = Flow(parent, d, { color: col, w: wdt, gap: 4.4, glowW: 2.2 }); f.show(at, 0.4, v); return f; };

  /* ------------------------------------------------------- left cards ---- */
  const card = (id, kick, title, lines, tIn, tOut, col = YEL) => {
    const p = H('div', { class: 'abs', style: { left: '96px', top: '190px', width: '560px' } },
      H('div', { class: 'kicker', style: { color: col, marginBottom: '14px' }, text: kick }),
      H('div', { class: 'h2', style: { fontSize: '62px', marginBottom: '22px' }, text: title }),
      ...lines.map((l) => H('div', { style: { display: 'flex', gap: '14px', alignItems: 'flex-start', marginBottom: '14px' } },
        H('div', { style: { width: '12px', height: '12px', borderRadius: '50%', background: col, marginTop: '15px', flex: 'none' } }),
        H('div', { style: { font: '500 30px/1.3 var(--font)', color: '#DCE6EE' }, html: l }))));
    el.append(p);
    show(p, tIn, 0.6, { x: -26, y: 0 });
    hide(p, tOut, 0.5, { x: -18 });
    return p;
  };

  /* ================================================================== b1 ==== */
  const b1 = bt('b1');
  const c1 = card('b1', 'Norwegian Continental Shelf', 'Subsea trees are everywhere', ['North Sea', 'Norwegian Sea', 'Barents Sea'], b1.start - 0.1, bt('b2').start - 0.5);
  seas.forEach((s_, i) => fadeIn(s_, w('b1', 'everywhere') - 0.2 + i * 0.25, 0.8));
  dots.forEach((d, i) => fadeIn(d, w('b1', 'trees') + 0.1 + ((i * 7) % dots.length) * 0.045, 0.5));
  sfx(w('b1', 'everywhere'), 'chime', 0.4);
  const legend = H('div', { class: 'abs', style: { left: '96px', top: '830px', display: 'flex', alignItems: 'center', gap: '12px', font: '500 22px var(--font)', color: '#AFC0CE' } },
    H('div', { style: { width: '14px', height: '14px', borderRadius: '50%', background: OR, boxShadow: `0 0 12px ${OR}` } }), 'Selected fields with subsea wells');
  el.append(legend);
  show(legend, w('b1', 'trees') + 0.6, 0.6, { y: 10 }); hide(legend, bt('b2').start - 0.4, 0.4);

  // camera hops between fields: zoom out, then in
  const hop = (t, d, to) => {
    const from = cam.cur;
    const mid = { wx: (from.wx + to.wx) / 2, wy: (from.wy + to.wy) / 2, sx: 1230, sy: 560, k: Math.max(0.5, Math.min(from.k, to.k) * 0.22) };
    cam.go(t, d * 0.5, mid, 'power2.in');
    cam.go(t + d * 0.5, d * 0.5, to, 'power2.out');
  };
  const fade = (g, at, until) => { fadeIn(g, at, 0.45); if (until) fadeOut(g, until, 0.4); };

  /* ================================================================== b2: Troll ==== */
  {
    const tIn = bt('b2').start;
    hop(tIn - 1.5, 2.2, SH.troll);
    seas.forEach((s_) => fadeOut(s_, tIn - 1.2, 0.5));
    dots.forEach((d) => tl.to(d, { opacity: 0.3, duration: 0.6 }, tIn - 1.2));
    const tOut = bt('b3').start - 0.7;
    card('b2', 'North Sea', 'Troll', ['Subsea templates feed <b style="color:#fff">Troll B</b> and <b style="color:#fff">Troll C</b>', 'Since <b style="color:#FFC857">2021</b>: Phase 3 feeds gas to <b style="color:#fff">Troll A</b>'], tIn - 0.2, tOut);
    const pin = mkPin('troll', 'Troll', 'North Sea');
    fade(pin.g, tIn - 0.8, w('b2', 'templates') - 0.1);
    const g = ov(tIn + 0.5, tOut);
    const A = [600, 1680], B = [586, 1664], C = [592, 1646];          // schematic layout
    const tb = [[566, 1640], [560, 1662], [568, 1684]];
    const tw = w('b2', 'templates');
    tb.forEach(([x, y], i) => template(g, x, y, CY, tw + i * 0.18));
    const pB = platform(g, B[0], B[1], 'B', 1.9), pC = platform(g, C[0], C[1], 'C', 1.9), pA = platform(g, A[0], A[1], 'A', 1.9);
    [pB, pC, pA].forEach((p_) => gsapHide(p_));
    fadeIn(pB, w('b2', 'Troll', 1) - 0.1, 0.5); fadeIn(pC, w('b2', 'Troll', 2) - 0.1, 0.5);
    // gas export to shore (decorative, unlabelled)
    const exp = S('path', { d: `M${A[0] + 4} ${A[1] + 2} Q640 1676 676 1668`, fill: 'none', stroke: 'rgba(190,220,245,.35)', 'stroke-width': 1.4, 'stroke-dasharray': '6 5', ...ns, opacity: 0 });
    g.append(exp); fadeIn(exp, w('b2', 'Phase') + 0.5, 0.6, 0.8);
    line(g, `M${tb[0][0]} ${tb[0][1]} L${C[0] - 5} ${C[1] + 1}`, OR, w('b2', 'feed'));
    line(g, `M${tb[1][0]} ${tb[1][1]} L${B[0] - 5} ${B[1] + 1.2}`, OR, w('b2', 'feed') + 0.15);
    line(g, `M${tb[2][0]} ${tb[2][1]} Q574 1672 ${B[0] - 3.4} ${B[1] + 3}`, OR, w('b2', 'feed') + 0.3);
    ringMap(g, B[0], B[1] - 1.5, 9.5, CY, w('b2', 'Troll', 1) - 0.1, w('b2', 'since') - 0.2);
    ringMap(g, C[0], C[1] - 1.5, 9.5, CY, w('b2', 'Troll', 2) - 0.1, w('b2', 'since') - 0.2);
    // phase 3 → Troll A
    const p3 = [[576, 1708], [592, 1718]];
    p3.forEach(([x, y], i) => template(g, x, y, YEL, w('b2', 'Phase') + i * 0.2));
    fadeIn(pA, w('b2', 'Phase') + 0.3, 0.5);
    line(g, `M${p3[0][0]} ${p3[0][1]} Q586 1698 ${A[0] - 4} ${A[1] + 4}`, YEL, w('b2', 'gas') - 0.3, 13);
    line(g, `M${p3[1][0]} ${p3[1][1]} Q598 1700 ${A[0]} ${A[1] + 4.6}`, YEL, w('b2', 'gas') - 0.1, 13);
    ringMap(g, A[0], A[1] - 1.5, 9.5, YEL, w('b2', 'Troll', 3) - 0.1, tOut - 0.3);
    // labels in screen space
    const pr = (x, y) => proj(SH.troll, x, y);
    const pill = (p, dx, dy, text, col, anchor, at, until) => { const t = tag(svg, { x: p[0] + dx, y: p[1] + dy, text, accent: col, anchor, size: 24, mono: true }); show(t.el, at, 0.45, { y: 10 }); hide(t.el, until, 0.4); };
    pill(pr(...B), -150, 0, 'TROLL B', CY, 'r', w('b2', 'Troll', 1) - 0.1, tOut - 0.2);
    pill(pr(...C), 74, -4, 'TROLL C', CY, 'l', w('b2', 'Troll', 2) - 0.1, tOut - 0.2);
    pill(pr(...A), 74, 6, 'TROLL A', YEL, 'l', w('b2', 'Troll', 3) - 0.1, tOut - 0.2);
    pill(pr(563, 1662), -52, -118, 'SUBSEA TEMPLATES', CY, 'c', tw - 0.1, w('b2', 'since') - 0.1);
    pill(pr(584, 1713), 4, 62, 'PHASE 3 · 2021', YEL, 'c', w('b2', '2021') - 0.1, tOut - 0.2);
    sfx(tw, 'tick', 0.5);
  }

  /* ================================================================== b3: Åsgard ==== */
  {
    const tIn = bt('b3').start, tOut = bt('b4').start - 0.7;
    hop(bt('b3').start - 0.8, 2.2, SH.asgard);
    card('b3', 'Norwegian Sea', 'Åsgard', ["The world's first <b style=\"color:#fff\">subsea gas compression</b> plant", 'Started up in <b style="color:#FFC857">2015</b>'], tIn - 0.2, tOut);
    const pin = mkPin('asgard', 'Åsgard', 'Norwegian Sea');
    fade(pin.g, tIn - 0.8, tIn + 0.9);
    const g = ov(tIn + 0.3, tOut);
    const F = MAP.pins.asgard, Cmp = [746, 1348];
    const fp = fpso(g, F[0] + 1, F[1] - 0.5, 'FPSO', 2.1);
    gsapHide(fp); fadeIn(fp, tIn + 0.2, 0.5);
    const tps = [[740, 1324], [758, 1358], [730, 1340]];
    tps.forEach(([x, y], i) => template(g, x, y, CY, tIn + 0.5 + i * 0.15));
    // wells feed the compression station slowly; after it, gas flows faster to the FPSO
    line(g, `M${tps[0][0]} ${tps[0][1]} Q741 1336 ${Cmp[0] - 1} ${Cmp[1] - 3}`, OR, tIn + 0.8, 5);
    line(g, `M${tps[2][0]} ${tps[2][1]} L${Cmp[0] - 3.6} ${Cmp[1]}`, OR, tIn + 0.9, 5);
    line(g, `M${tps[1][0]} ${tps[1][1]} L${Cmp[0] + 1.4} ${Cmp[1] + 3}`, OR, tIn + 1.0, 5);
    const tc = w('b3', 'compression');
    const stn = S('g', { opacity: 0 });
    stn.append(S('g', { transform: `translate(${Cmp[0]} ${Cmp[1]}) scale(2.1) translate(${-Cmp[0]} ${-Cmp[1]})` },
      S('rect', { x: Cmp[0] - 3.4, y: Cmp[1] - 2.6, width: 6.8, height: 5.2, rx: 0.9, fill: '#1B2F42', stroke: PUR, 'stroke-width': 0.45 }), S('circle', { cx: Cmp[0], cy: Cmp[1], r: 1.7, fill: 'none', stroke: PUR, 'stroke-width': 0.4 }),
      S('path', { d: `M${Cmp[0]} ${Cmp[1] - 1.5} L${Cmp[0] + 1.3} ${Cmp[1] + 0.8} L${Cmp[0] - 1.3} ${Cmp[1] + 0.8} Z`, fill: PUR, opacity: 0.85 })));
    g.append(stn); fadeIn(stn, tc - 0.3, 0.6);
    line(g, `M${Cmp[0] + 3.4} ${Cmp[1] - 3} Q758 1338 ${F[0] - 3} ${F[1] + 3.4}`, YEL, tc + 0.2, 16, 1.2);
    ringMap(g, Cmp[0], Cmp[1], 9.5, PUR, tc - 0.2, tOut - 0.3);
    const pr = (x, y) => proj(SH.asgard, x, y);
    const t1 = tag(svg, { x: pr(Cmp[0], Cmp[1])[0], y: pr(Cmp[0], Cmp[1])[1] + 96, text: 'SUBSEA GAS COMPRESSION', accent: PUR, anchor: 'c', size: 24, mono: true });
    show(t1.el, tc, 0.5, { y: 10 }); hide(t1.el, tOut - 0.2, 0.4);
    const t2 = tag(svg, { x: pr(F[0], F[1])[0] + 30, y: pr(F[0], F[1])[1] - 110, text: 'FIRST IN THE WORLD · 2015', accent: YEL, anchor: 'c', size: 24, mono: true });
    show(t2.el, w('b3', 'first') - 0.1, 0.5, { y: 10 }); hide(t2.el, tOut - 0.2, 0.4);
    const t3 = tag(svg, { x: pr(F[0], F[1])[0] + 70, y: pr(F[0], F[1])[1] + 38, text: 'FPSO', accent: '#93A8B8', anchor: 'l', size: 22, mono: true });
    show(t3.el, tIn + 0.5, 0.5, { y: 10 }); hide(t3.el, tOut - 0.2, 0.4);
    sfx(tc, 'chime', 0.5);
  }

  /* ================================================================== b4: Aasta Hansteen ==== */
  {
    const tIn = bt('b4').start, tOut = bt('b5').start - 0.7;
    hop(bt('b4').start - 0.8, 2.2, SH.aasta);
    card('b4', 'Norwegian Sea', 'Aasta Hansteen', ['Trees stand in <b style="color:#FFC857">1,300 metres</b> of water', 'The <b style="color:#fff">deepest</b> on the shelf'], tIn - 0.2, tOut);
    const pin = mkPin('aasta', 'Aasta Hansteen', 'Norwegian Sea');
    fade(pin.g, tIn - 0.8, w('b4', 'Aasta') + 0.9);
    // depth cross-section (screen space)
    const P0 = { x: 1424, y: 190 };
    const dp = S('g', { opacity: 0 });
    svg.append(dp);
    dp.append(S('rect', { x: P0.x, y: P0.y, width: 400, height: 700, rx: 22, fill: 'rgba(5,16,26,.9)', stroke: 'rgba(170,200,225,.3)', 'stroke-width': 1.8 }),
      S('text', { x: P0.x + 26, y: P0.y + 42, fill: '#AFC0CE', 'font-size': 18, 'font-weight': 800, 'letter-spacing': '0.16em', text: 'WATER DEPTH' }));
    const sy0 = P0.y + 100, k = 0.36;                      // px per metre
    const colX = P0.x + 190, colW = 120;
    const seabed = sy0 + 1300 * k;
    dp.append(S('defs', {}, S('linearGradient', { id: 'gDepthW', x1: 0, y1: 0, x2: 0, y2: 1 }, S('stop', { offset: 0, 'stop-color': '#3C86D6', 'stop-opacity': 0.55 }), S('stop', { offset: 1, 'stop-color': '#0A2540', 'stop-opacity': 0.95 }))));
    dp.append(S('rect', { x: colX, y: sy0, width: colW, height: 1300 * k, fill: 'url(#gDepthW)' }), S('path', { d: `M${colX - 12} ${seabed} H${colX + colW + 84}`, stroke: '#7A6A52', 'stroke-width': 6 }),
      S('rect', { x: colX - 12, y: seabed, width: colW + 96, height: 18, fill: '#3A3226' }));
    [0, 500, 1000, 1300].forEach((m) => { const y = sy0 + m * k; dp.append(S('path', { d: `M${colX - 14} ${y} H${colX}`, stroke: '#AFC0CE', 'stroke-width': 2 }), S('text', { x: colX - 22, y: y + 6, 'text-anchor': 'end', fill: '#AFC0CE', 'font-size': 18, 'font-weight': 600, style: { fontFamily: 'var(--mono)' }, text: m + ' m' })); });
    // spar platform at the surface + tree at the seabed
    dp.append(S('path', { d: `M${colX + 30} ${sy0 - 6} h60 v-34 h-60 z`, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 2 }), S('rect', { x: colX + 50, y: sy0 - 6, width: 20, height: 74, fill: '#93A8B8', stroke: OUT, 'stroke-width': 2 }),
      S('path', { d: `M${colX + 36} ${sy0 - 40} v-18`, stroke: '#C4D2DD', 'stroke-width': 3 }), S('path', { d: `M${colX + 36} ${sy0 - 58} q-8 -9 0 -19 q8 9 0 19`, fill: OR }));
    treeGlyph(dp, colX + colW / 2, seabed - 22, 0.9, CY);
    dp.append(S('path', { d: `M${colX + colW / 2 + 4} ${seabed - 44} V${sy0 + 62}`, stroke: OR, 'stroke-width': 3, 'stroke-dasharray': '6 6', opacity: 0.8 }));
    // eiffel tower for scale (330 m)
    const ex = colX + colW + 78, eh = 330 * k;
    dp.append(S('path', { d: `M${ex - 30} ${seabed} L${ex - 5} ${seabed - eh * 0.45} L${ex - 2} ${seabed - eh} L${ex + 2} ${seabed - eh} L${ex + 5} ${seabed - eh * 0.45} L${ex + 30} ${seabed} M${ex - 20} ${seabed - eh * 0.2} H${ex + 20} M${ex - 8} ${seabed - eh * 0.6} H${ex + 8}`, fill: 'none', stroke: '#8FA6B8', 'stroke-width': 2.4, 'stroke-linejoin': 'round' }),
      S('text', { x: ex, y: seabed - eh - 12, 'text-anchor': 'middle', fill: '#8FA6B8', 'font-size': 16, 'font-weight': 600, text: '330 m' }));
    // big number
    const num = S('text', { x: P0.x + 26, y: P0.y + 650, fill: YEL, 'font-size': 64, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: '0 m' });
    dp.append(num, S('text', { x: P0.x + 26, y: P0.y + 684, fill: '#AFC0CE', 'font-size': 18, 'font-weight': 600, text: '≈ four Eiffel Towers on top of each other' }));
    fadeIn(dp, tIn + 0.6, 0.7);
    fadeOut(dp, tOut, 0.5);
    const t = w('b4', '1,300') - 0.3;
    tweenNumber(t, 1.9, 0, 1300, (v) => { num.textContent = (Math.round(v / 10) * 10).toLocaleString('en-US') + ' m'; }, 'power2.out');
    // depth marker sweeping down the column
    const arrow = S('path', { d: `M${colX + colW + 10} ${sy0} l14 -9 v18 z`, fill: YEL, opacity: 0 });
    dp.append(arrow);
    tl.fromTo(arrow, { opacity: 0, attr: { transform: 'translate(0 0)' } }, { opacity: 1, duration: 0.2, immediateRender: false }, t);
    const pa = { y: 0 };
    tl.fromTo(pa, { y: 0 }, { y: 1300 * k, duration: 1.9, ease: 'power2.out', onUpdate: () => arrow.setAttribute('transform', `translate(0 ${pa.y.toFixed(1)})`), immediateRender: false }, t);
    // spar on the map
    const g = ov(tIn + 0.2, tOut);
    const Pn = MAP.pins.aasta;
    const spar = S('g', { transform: `translate(${Pn[0] + 2} ${Pn[1] - 1.4}) scale(1.9)`, opacity: 0 });
    spar.append(S('rect', { x: -1.1, y: -0.4, width: 2.2, height: 6.5, rx: 0.5, fill: '#6F879A', stroke: OUT, 'stroke-width': 0.25 }), S('rect', { x: -3.4, y: -2, width: 6.8, height: 1.8, rx: 0.3, fill: '#C4D2DD', stroke: OUT, 'stroke-width': 0.28 }), S('rect', { x: -2.4, y: -3.4, width: 2.6, height: 1.4, fill: '#93A8B8', stroke: OUT, 'stroke-width': 0.22 }),
      S('rect', { x: 2, y: -4.8, width: 0.4, height: 2.9, fill: '#C4D2DD' }), S('path', { d: 'M2.2 -4.8 q-0.8 -0.8 0 -1.7 q0.8 0.8 0 1.7', fill: OR }));
    g.append(spar); fadeIn(spar, w('b4', 'Aasta') + 0.2, 0.6);
    ringMap(g, Pn[0] + 2, Pn[1] - 1.4, 9.5, YEL, w('b4', 'trees') - 0.1, tOut - 0.3);
  }

  /* ================================================================== b5: Johan Castberg ==== */
  {
    const tIn = bt('b5').start, tOut = t1s - 0.3;
    hop(bt('b5').start - 0.8, 2.4, SH.castberg);
    seas[2].setAttribute('opacity', 0); fadeIn(seas[2], tIn - 0.3, 0.8, 0.8);
    card('b5', 'Barents Sea', 'Johan Castberg', ['First oil: <b style="color:#FFC857">March 2025</b>', '<b style="color:#fff">30 subsea wells</b>', 'All on the new <b style="color:#fff">standard tree</b>'], tIn - 0.2, tOut);
    const pin = mkPin('castberg', 'Johan Castberg', 'Barents Sea');
    fade(pin.g, tIn - 0.8, tOut);
    const g = ov(tIn + 0.2, tOut);
    const Pn = MAP.pins.castberg;
    const fp = fpso(g, Pn[0] + 0.5, Pn[1] - 0.8, 'FPSO', 1.5);
    ringMap(g, Pn[0], Pn[1] - 1, 7, YEL, w('b5', 'Johan') - 0.1, tOut - 0.3);
    // 30-well grid (screen space)
    const P0 = { x: 1360, y: 200 };
    const gp = S('g', { opacity: 0 });
    svg.append(gp);
    gp.append(S('rect', { x: P0.x, y: P0.y, width: 464, height: 660, rx: 22, fill: 'rgba(5,16,26,.9)', stroke: 'rgba(170,200,225,.3)', 'stroke-width': 1.8 }),
      S('text', { x: P0.x + 26, y: P0.y + 42, fill: '#AFC0CE', 'font-size': 18, 'font-weight': 800, 'letter-spacing': '0.16em', text: 'SUBSEA WELLS' }));
    const cells = [];
    for (let r = 0; r < 5; r++) for (let c = 0; c < 6; c++) {
      const cg = S('g', { opacity: 0.18 });
      treeGlyph(cg, P0.x + 52 + c * 72, P0.y + 120 + r * 92, 1.15, CY, 'rgba(46,208,255,.28)');
      gp.append(cg); cells.push(cg);
    }
    const cnt = S('text', { x: P0.x + 26, y: P0.y + 608, fill: YEL, 'font-size': 62, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: '0' });
    gp.append(cnt, S('text', { x: P0.x + 130, y: P0.y + 608, fill: '#AFC0CE', 'font-size': 24, 'font-weight': 600, text: 'subsea wells' }));
    fadeIn(gp, tIn + 0.7, 0.7); fadeOut(gp, tOut, 0.5);
    const tw30 = w('b5', 'thirty');
    cells.forEach((cg, i) => tl.to(cg, { opacity: 1, duration: 0.25 }, tw30 + i * 0.04));
    tweenNumber(tw30, 30 * 0.04 + 0.2, 0, 30, (v) => (cnt.textContent = String(Math.round(v))), 'none');
    const sd = tag(svg, { x: P0.x + 232, y: P0.y + 700, text: 'NEW STANDARD TREE', accent: GRN, anchor: 'c', size: 26, mono: true });
    show(sd.el, w('b5', 'standard') - 0.2, 0.5, { y: 10 }); hide(sd.el, tOut, 0.4);
    cells.forEach((cg) => tl.to(cg.firstChild, { stroke: GRN, duration: 0.4 }, w('b5', 'standard')));
    sfx(tw30, 'chime', 0.5);
  }
}

/** initial hidden state for elements that are revealed with fadeIn (opacity-only) */
function gsapHide(el) { el.setAttribute('opacity', 0); }
