// Scene 4 – Four jobs (103 – 130 s) -----------------------------------------------
import { H, S, rng } from '../lib/svg.js';
import { makeScene } from '../lib/scene.js';
import { installDefs } from '../art/defs.js';
import { buildTreeExterior } from '../art/treeExt.js';
import { marineSnow } from '../lib/fx.js';

export function build(root, E) {
  const { T, A, tl, show, hide, fadeIn, fadeOut, Cam, Flow, animate, sfx, gsap } = E;
  installDefs();
  const sc = T.scene('jobs');
  const tTree = T.start('jobs.b6') - 0.4;

  /* ================= part A: the four cards ================= */
  const { el, svg } = makeScene(root, E, 'jobs', { t0: sc.start, t1: tTree + 0.7, pad: 0.3 });
  const kick = H('div', { class: 'kicker abs', style: { left: '96px', top: '150px', color: '#FFC857' }, text: 'What a subsea tree does' });
  const h2 = H('div', { class: 'h2 abs', style: { left: '96px', top: '188px' }, text: 'Four jobs' });
  el.append(kick, h2);
  show(kick, T.start('jobs.b1') - 0.1, 0.6); show(h2, T.start('jobs.b1'), 0.7);

  const cw = 405, ch = 560, gap = 24, x0 = 114, y0 = 300;
  const defs = [
    { title: 'Control the flow', sub: ['The choke sets how much', 'comes out, or goes in'], col: '#FF9A3C', beat: 'b2' },
    { title: 'Isolate the well', sub: ['A pressure-containing', 'safety barrier'], col: '#FF4F6D', beat: 'b3' },
    { title: 'Inject & monitor', sub: ['Chemicals in; pressure and', 'temperature out'], col: '#BC8FFF', beat: 'b4' },
    { title: 'Give access', sub: ['For maintenance and', 'well intervention'], col: '#2ED0FF', beat: 'b5' },
  ];
  const cards = defs.map((d, i) => {
    const wrap = S('g', { transform: `translate(${x0 + i * (cw + gap)} ${y0})` });
    const g = S('g');
    wrap.append(g);
    svg.append(wrap);
    g.append(
      S('rect', { width: cw, height: ch, rx: 26, fill: 'rgba(8,26,42,.86)', stroke: 'rgba(170,200,225,.26)', 'stroke-width': 1.8 }),
      S('rect', { x: 0, y: 0, width: cw, height: 8, rx: 4, fill: d.col, opacity: 0.0 }));
    const edge = S('rect', { width: cw, height: ch, rx: 26, fill: 'none', stroke: d.col, 'stroke-width': 3.5, opacity: 0 });
    g.append(edge);
    g.append(
      S('circle', { cx: 50, cy: 52, r: 28, fill: d.col }),
      S('text', { x: 50, y: 62, 'text-anchor': 'middle', fill: '#06121C', 'font-size': 30, 'font-weight': 700, style: { fontFamily: 'var(--mono)' }, text: String(i + 1) }),
      S('text', { x: cw / 2, y: 410, 'text-anchor': 'middle', fill: '#EEF4F9', 'font-size': 40, 'font-weight': 700, text: d.title }),
      S('text', { x: cw / 2, y: 462, 'text-anchor': 'middle', fill: '#AFC0CE', 'font-size': 26, 'font-weight': 500, text: d.sub[0] }),
      S('text', { x: cw / 2, y: 496, 'text-anchor': 'middle', fill: '#AFC0CE', 'font-size': 26, 'font-weight': 500, text: d.sub[1] }));
    const ia = S('g', { transform: `translate(${cw / 2} 215)` });
    g.append(ia);
    const tb = T.start('jobs.' + d.beat);
    tl.fromTo(g, { autoAlpha: 0, y: 50 }, { autoAlpha: 0.45, y: 0, duration: 0.6, ease: 'power3.out', immediateRender: true }, T.start('jobs.b1') + 0.9 + i * 0.12);
    tl.to(g, { autoAlpha: 1, duration: 0.35 }, tb - 0.05);
    tl.to(edge, { opacity: 1, duration: 0.3 }, tb);
    const tn = i < 3 ? T.start('jobs.' + defs[i + 1].beat) : T.end('jobs.b5') + 0.5;
    tl.to(edge, { opacity: 0, duration: 0.4 }, tn);
    tl.to(g, { autoAlpha: 0.7, duration: 0.5 }, tn);
    tl.to(wrap, { opacity: 0, duration: 0.01 }, tTree + 0.5);
    sfx(tb, 'tick', 0.6);
    return { g, ia, tb, d };
  });
  const T0 = sc.start, T1 = tTree + 1;

  // (1) choke + flow ----------------------------------------------------------
  {
    const ia = cards[0].ia;
    ia.append(
      S('rect', { x: -150, y: -34, width: 300, height: 68, fill: '#050B11', stroke: '#51677A', 'stroke-width': 5 }),
      S('rect', { x: -150, y: -42, width: 300, height: 8, fill: '#51677A' }), S('rect', { x: -150, y: 34, width: 300, height: 8, fill: '#51677A' }),
      S('rect', { x: -52, y: -108, width: 104, height: 74, rx: 8, fill: 'url(#gAct)', stroke: '#0E2236', 'stroke-width': 3 }),
      S('rect', { x: -52, y: 34, width: 104, height: 26, rx: 4, fill: '#51677A' }));
    const f = Flow(ia, 'M-146 0 H146', { color: '#FF9A3C', w: 9, gap: 26 });
    f.show(cards[0].tb - 0.2, 0.5, 70);
    const needle = S('g');
    needle.append(S('rect', { x: -9, y: -70, width: 18, height: 70, fill: 'url(#gGate)', stroke: '#0B141C', 'stroke-width': 2 }), S('path', { d: 'M-9 0 H9 L3 22 H-3 Z', fill: '#E5ECF2', stroke: '#0B141C', 'stroke-width': 2 }));
    ia.append(needle);
    animate(cards[0].tb - 0.5, T1, (t) => needle.setAttribute('transform', `translate(0 ${(-4 + 24 * Math.sin((t - cards[0].tb) * 1.6)).toFixed(2)})`));
  }
  // (2) shield + lock ------------------------------------------------------------
  {
    const ia = cards[1].ia, c = '#EEF4F9', col = '#FF4F6D';
    const shield = S('path', { d: 'M0 -100 L84 -66 V8 C84 56 44 86 0 108 C-44 86 -84 56 -84 8 V-66 Z', fill: 'rgba(255,79,109,.10)', stroke: c, 'stroke-width': 8, 'stroke-linejoin': 'round' });
    const lockBody = S('rect', { x: -32, y: -6, width: 64, height: 52, rx: 9, fill: col, stroke: '#06121C', 'stroke-width': 3 });
    const shackle = S('path', { d: 'M-18 -6 V-26 a18 18 0 0 1 36 0 V-6', fill: 'none', stroke: c, 'stroke-width': 9, 'stroke-linecap': 'round' });
    const keyhole = S('circle', { cx: 0, cy: 18, r: 7, fill: '#06121C' });
    ia.append(shield, shackle, lockBody, keyhole);
    tl.fromTo(shackle, { y: -16 }, { y: 0, duration: 0.45, ease: 'bounce.out', immediateRender: true }, cards[1].tb + 0.5);
    tl.fromTo(shield, { scale: 1, svgOrigin: '0 0' }, { scale: 1.07, duration: 0.3, yoyo: true, repeat: 1, ease: 'power2.out', immediateRender: false }, cards[1].tb + 0.8);
    sfx(cards[1].tb + 0.9, 'clunk', 0.8);
  }
  // (3) inject + gauge ----------------------------------------------------------------
  {
    const ia = cards[2].ia;
    ia.append(
      S('rect', { x: -150, y: 14, width: 190, height: 52, fill: '#050B11', stroke: '#51677A', 'stroke-width': 5 }),
      S('rect', { x: -26, y: -64, width: 52, height: 78, fill: '#050B11', stroke: '#51677A', 'stroke-width': 5, transform: 'translate(-60 0)' }));
    const f = Flow(ia, 'M-146 40 H36', { color: '#FF9A3C', w: 8, gap: 24 });
    f.show(cards[2].tb - 0.1, 0.5, 60);
    const drops = [0, 1, 2].map(() => { const d = S('path', { d: 'M0 -12 C0 -12 -9 0 -9 5 a9 9 0 0 0 18 0 C9 0 0 -12 0 -12 Z', fill: '#BC8FFF' }); ia.append(d); return d; });
    animate(cards[2].tb - 0.2, T1, (t) => drops.forEach((d, i) => { const p = (((t - cards[2].tb) * 0.9 + i / 3) % 1 + 1) % 1; d.setAttribute('transform', `translate(-86 ${(-110 + p * 130).toFixed(1)}) scale(${(0.7 + 0.3 * (1 - p)).toFixed(2)})`); d.setAttribute('opacity', p > 0.92 ? ((1 - p) / 0.08).toFixed(2) : 1); }));
    // gauge
    const gg = S('g', { transform: 'translate(96 -22)' });
    gg.append(S('circle', { r: 56, fill: '#0B1823', stroke: '#EEF4F9', 'stroke-width': 6 }),
      ...Array.from({ length: 9 }, (_, i) => { const a = (-210 + i * 30) * Math.PI / 180; return S('line', { x1: Math.cos(a) * 44, y1: Math.sin(a) * 44, x2: Math.cos(a) * 52, y2: Math.sin(a) * 52, stroke: '#6F879A', 'stroke-width': 3 }); }));
    const needle = S('line', { x1: 0, y1: 0, x2: 0, y2: -44, stroke: '#FFC857', 'stroke-width': 5, 'stroke-linecap': 'round' });
    gg.append(needle, S('circle', { r: 7, fill: '#FFC857' }));
    ia.append(gg);
    animate(cards[2].tb - 0.2, T1, (t) => needle.setAttribute('transform', `rotate(${(-20 + 70 * Math.sin((t - cards[2].tb) * 1.3) + 8 * Math.sin((t - cards[2].tb) * 4.1)).toFixed(1)})`));
  }
  // (4) wireline tool descending the bore -------------------------------------------------
  {
    const ia = cards[3].ia;
    ia.append(S('rect', { x: -38, y: -120, width: 76, height: 240, fill: '#050B11', stroke: '#51677A', 'stroke-width': 6 }));
    const tool = S('g');
    tool.append(S('line', { x1: 0, y1: -400, x2: 0, y2: -22, stroke: '#FFC857', 'stroke-width': 4 }),
      S('rect', { x: -15, y: -22, width: 30, height: 64, rx: 7, fill: '#FFC857', stroke: '#06121C', 'stroke-width': 3 }),
      S('rect', { x: -8, y: 42, width: 16, height: 16, rx: 3, fill: '#EEF4F9' }));
    const clip = S('clipPath', { id: 'clipBoreJobs' }, S('rect', { x: -38, y: -120, width: 76, height: 240 }));
    ia.append(clip);
    const toolWrap = S('g', { 'clip-path': 'url(#clipBoreJobs)' });
    toolWrap.append(tool);
    ia.append(toolWrap);
    animate(cards[3].tb - 0.2, T1, (t) => { const p = (((t - cards[3].tb) / 3.2) % 1 + 1) % 1; const e = p < 0.8 ? 1 - Math.pow(1 - p / 0.8, 2) : 1; tool.setAttribute('transform', `translate(0 ${(-80 + e * 120 + 30 * (p > 0.8 ? (p - 0.8) / 0.2 * 6 : 0)).toFixed(1)})`); });
    // chevrons
    ia.append(S('path', { d: 'M-110 -40 l20 20 l-20 20 M-110 20 l20 20 l-20 20', fill: 'none', stroke: '#2ED0FF', 'stroke-width': 8, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', opacity: 0.8, transform: 'rotate(90 -100 0)' }));
  }

  /* ================= part B: why "Christmas tree"? ================= */
  const B = makeScene(root, E, 'jobs', { t0: tTree, t1: sc.end, pad: 0.35, bg: 'radial-gradient(900px 700px at 62% 50%, #12385A 0%, #07182A 60%, #040C14 100%)' });
  const svgB = B.svg;
  const snow = marineSnow(svgB, { n: 90, seed: 9, ambient: 8, op: 0.5 });
  const world = S('g');
  svgB.append(world);
  const cam = new Cam(world, { wx: 0, wy: -520, sx: 1100, sy: 560, k: 0.62 });
  world.append(S('rect', { x: -3000, y: 0, width: 6000, height: 1200, fill: 'url(#gSeabed)' }), S('path', { d: 'M-3000 0 H3000', stroke: '#31434F', 'stroke-width': 4 }));
  const tree = buildTreeExterior(world);
  const ttl = H('div', { class: 'abs', style: { left: '96px', top: '380px', width: '640px' } },
    H('div', { class: 'kicker', style: { color: '#FFC857', marginBottom: '16px' }, text: 'Why “Christmas tree”?' }),
    H('div', { class: 'h2', style: { fontSize: '58px' }, html: 'A stack of <span style="color:var(--hyd)">valves</span> and <span style="color:var(--hc)">branches</span>' }));
  B.el.append(ttl);
  show(ttl, T.word('jobs.b6', 'name') - 0.1, 0.7);
  // fir outline (right half mirrored)
  const half = [[0, -1090], [340, -860], [190, -860], [520, -620], [360, -620], [730, -260], [730, -60]];
  const full = [...half, [-730, -60], ...[...half].slice(1, -1).reverse().map(([x, y]) => [-x, y]), [0, -1090]];
  const dd = full.map((p, i) => (i ? 'L' : 'M') + p[0] + ' ' + p[1]).join(' ');
  const fir = S('path', { d: dd, pathLength: 1, fill: 'none', stroke: '#3BDB86', 'stroke-width': 9, 'stroke-linejoin': 'round', 'stroke-dasharray': 1, 'stroke-dashoffset': 1, opacity: 0.95 });
  const firGlow = S('path', { d: dd, pathLength: 1, fill: 'none', stroke: '#3BDB86', 'stroke-width': 24, 'stroke-linejoin': 'round', 'stroke-dasharray': 1, 'stroke-dashoffset': 1, opacity: 0.18 });
  world.append(firGlow, fir);
  const tChr = T.word('jobs.b6', 'Christmas') - 0.3;
  tl.fromTo([fir, firGlow], { attr: { 'stroke-dashoffset': 1 } }, { attr: { 'stroke-dashoffset': 0 }, duration: 1.5, ease: 'power2.inOut', immediateRender: true }, tChr);
  // star
  const star = S('g', { transform: 'translate(0 -1120)' });
  const starIn = S('g');
  star.append(starIn);
  starIn.append(S('circle', { r: 70, fill: 'url(#gGlowWarm)' }), S('path', { d: 'M0 -42 L12 -14 L42 -12 L19 8 L26 38 L0 22 L-26 38 L-19 8 L-42 -12 L-12 -14 Z', fill: '#FFC857', stroke: '#FF9A3C', 'stroke-width': 4, 'stroke-linejoin': 'round' }));
  world.append(star);
  tl.fromTo(starIn, { scale: 0, opacity: 0, svgOrigin: '0 0' }, { scale: 1, opacity: 1, duration: 0.6, ease: 'back.out(3)', immediateRender: true }, tChr + 1.3);
  sfx(tChr + 1.3, 'chime', 0.8);
  // baubles on actuator positions (tree-local -> world y-900)
  const baub = [[-230, 270, '#FF4F6D'], [0, 430, '#2ED0FF'], [150, 430, '#FFC857'], [400, 270, '#BC8FFF'], [-400, 60, '#3BDB86'], [300, 70, '#FF9A3C'], [-560, 320, '#2ED0FF'], [540, 320, '#FF4F6D']];
  baub.forEach(([x, y, col], i) => {
    const b = S('g', { transform: `translate(${x} ${y - 900})` });
    const bi = S('g');
    b.append(bi);
    bi.append(S('circle', { r: 34, fill: col, stroke: '#06121C', 'stroke-width': 4 }), S('circle', { cx: -10, cy: -10, r: 9, fill: 'rgba(255,255,255,.55)' }));
    world.append(b);
    tl.fromTo(bi, { scale: 0, svgOrigin: '0 0' }, { scale: 1, duration: 0.5, ease: 'back.out(3)', immediateRender: true }, T.word('jobs.b6', 'valves') + 0.15 * i);
  });
  // slow push-in
  cam.go(tTree, 2.0, { wy: -520, k: 0.62 }, 'power2.out');
  fadeOut(fir, sc.end - 0.9, 0.8);
}
