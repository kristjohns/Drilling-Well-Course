// Scenes 7–15 – Meet the valves (230 – 356 s) --------------------------------------------------
import { H, S, rng } from '../lib/svg.js';
import { tag, leader } from '../lib/annot.js';
import { gauge } from '../lib/ui.js';
import { rov } from '../art/rov.js';
import { miniTree, plant } from '../art/system.js';
import { SHOT } from './anatomy.js';

export const VSH = {
  full: SHOT.full,
  pmv: { wx: -30, wy: -400, sx: 1260, sy: 560, k: 2.0 },
  pwv: { wx: -250, wy: -580, sx: 1250, sy: 540, k: 1.75 },
  choke: { wx: -390, wy: -640, sx: 1190, sy: 560, k: 1.9 },
  psv: { wx: 0, wy: -790, sx: 1260, sy: 640, k: 2.1 },
  ann: { wx: 200, wy: -580, sx: 1200, sy: 540, k: 1.45 },
  xov: { wx: -5, wy: -740, sx: 1250, sy: 540, k: 1.1 },
  civ: { wx: -330, wy: -470, sx: 1240, sy: 540, k: 1.45 },
  dhsvWide: { wx: 40, wy: 300, sx: 1250, sy: 540, k: 1.2 },
  dhsv: { wx: 0, wy: 540, sx: 1250, sy: 560, k: 2.6 },
};

export function build(ctx) {
  const { E, cam, tree, well, T, COL, annot, html, world } = ctx;
  const { tl, gsap, show, hide, fadeIn, fadeOut, sfx, animate, Flow, tweenNumber, proj } = E;
  const V = tree.valves;
  const bt = (id) => T.beat(id);
  const w = (id, word, n = 0) => T.word(id, word, n);
  const P = (sh, tx, ty) => ctx.P(sh, tx, ty);

  /* ============================== valve index list (left) ============================== */
  const items = [
    { key: 'pmv', tag: 'PMV', name: 'Production master', col: '#FFC857', t0: bt('pmv.b1').start, t1: bt('pmv.b2').end },
    { key: 'pwv', tag: 'PWV', name: 'Production wing', col: '#2ED0FF', t0: bt('pwv.b1').start, t1: bt('pwv.b2').end },
    { key: 'choke', tag: 'CHOKE', name: 'Production choke', col: '#FF9A3C', t0: bt('choke.b1').start, t1: bt('choke.b2').end },
    { key: 'psv', tag: 'PSV', name: 'Production swab', col: '#BC8FFF', t0: bt('psv.b1').start, t1: bt('psv.b1').end },
    { key: 'ann', tag: 'AMV · AWV · ASV', name: 'Annulus valves', col: '#34D8A8', t0: bt('annulus.b1').start, t1: bt('annulus.b2').end },
    { key: 'xov', tag: 'XOV', name: 'Crossover', col: '#34D8A8', t0: bt('xov.b1').start, t1: bt('xov.b2').end },
    { key: 'civ', tag: 'CIV', name: 'Chemical injection', col: '#BC8FFF', t0: bt('civ.b1').start, t1: bt('civ.b2').end },
    { key: 'dhsv', tag: 'DHSV', name: 'Downhole safety', col: '#FF4F6D', t0: bt('dhsv.b1').start, t1: bt('dhsv.b3').end },
  ];
  const tList = bt('valves.b1').start;
  // opaque-ish backing so tree art behind the dim rows does not clutter the list
  const listBack = H('div', { class: 'abs', style: { left: '70px', top: '148px', width: '452px', height: '694px', borderRadius: '26px', background: 'rgba(4,12,20,.97)', border: '1.5px solid rgba(170,200,225,.14)', boxShadow: '0 20px 60px rgba(0,0,0,.4)' } });
  html.append(listBack);
  show(listBack, tList, 0.6, { x: -20, y: 0 });
  hide(listBack, bt('dhsv.b3').end + 0.1, 0.5, { x: -30 });
  const listKick = H('div', { class: 'kicker abs', style: { left: '96px', top: '168px', color: '#FFC857' }, text: 'Valves on this tree' });
  html.append(listKick);
  show(listKick, tList, 0.6);
  const rows = items.map((it, i) => {
    const row = H('div', { class: 'abs', style: { left: '96px', top: 214 + i * 74 + 'px', width: '400px', height: '62px', display: 'flex', alignItems: 'center', gap: '14px', padding: '0 18px', borderRadius: '14px', background: 'rgba(8,26,42,.78)', border: '1.5px solid rgba(170,200,225,.22)' } });
    const dot = H('div', { style: { width: '10px', height: '34px', borderRadius: '5px', background: it.col, flex: 'none', opacity: 0.35 } });
    const col = H('div', { style: { display: 'flex', flexDirection: 'column', gap: '2px' } },
      H('div', { style: { font: '700 22px var(--mono)', color: '#EEF4F9', letterSpacing: '0.02em' }, text: it.tag }),
      H('div', { style: { font: '500 19px var(--font)', color: '#AFC0CE' }, text: it.name }));
    row.append(dot, col);
    html.append(row);
    tl.fromTo(row, { autoAlpha: 0, x: -30 }, { autoAlpha: 0.38, x: 0, duration: 0.5, ease: 'power3.out', immediateRender: true }, tList + 0.7 + i * 0.1);
    tl.to(row, { autoAlpha: 1, duration: 0.3 }, it.t0 - 0.1);
    tl.to(row, { borderColor: it.col, duration: 0.3 }, it.t0 - 0.1);
    tl.to(dot, { opacity: 1, duration: 0.3 }, it.t0 - 0.1);
    tl.to(row, { autoAlpha: 0.62, borderColor: 'rgba(170,200,225,.22)', duration: 0.4 }, it.t1 + 0.1);
    tl.to(dot, { opacity: 0.6, duration: 0.4 }, it.t1 + 0.1);
    return row;
  });
  rows.forEach((r) => hide(r, bt('dhsv.b3').end + 0.1, 0.5, { x: -30 }));
  hide(listKick, bt('dhsv.b3').end + 0.1, 0.5);

  /* ============================== helpers ============================== */
  const down = (t, f) => f; // placeholder for readability
  const noIcon = (c, size = 44) => `<svg viewBox="-30 -30 60 60" width="${size}" height="${size}"><g fill="none" stroke="${c}" stroke-width="5" stroke-linecap="round"><circle r="22"/><path d="M-16 -16 L16 16"/></g></svg>`;
  const badge = ({ at, until, x, y, html: h, color = '#FFC857', size = 28 }) => {
    const el = H('div', { class: 'abs', style: { left: x + 'px', top: y + 'px', display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 20px', borderRadius: '14px', background: 'rgba(5,16,26,.9)', border: `2px solid ${color}`, font: `700 ${size}px var(--font)`, color: '#EEF4F9' }, html: h });
    html.append(el);
    show(el, at, 0.45, { y: 12 });
    if (until !== undefined) hide(el, until, 0.4);
    return el;
  };

  /* ====================================================================================== */
  /* valves.b1 – pull back, production resumes                                              */
  /* ====================================================================================== */
  const tV = bt('valves.b1').start;
  cam.go(tV - 0.2, 2.6, VSH.full, 'power3.inOut');
  ctx.pmvOps.op(tV + 0.3, true, 1.6, 'power2.inOut');
  sfx(tV + 0.3, 'slide', 0.5);

  /* ====================================================================================== */
  /* PMV                                                                                    */
  /* ====================================================================================== */
  {
    const S1 = VSH.pmv;
    const t = bt('pmv.b1').start, t2 = bt('pmv.b2').start;
    cam.go(t - 0.7, 1.8, S1, 'power3.inOut');
    ctx.note({ shot: S1, at: w('pmv.b1', 'master') - 0.3, until: t2 - 0.1, tx: 0, ty: 500, dx: 110, dy: -215, label: 'Production master valve', sub: 'PMV · the main door to the well', color: '#FFC857', size: 30 });
    ctx.status({ name: 'PMV', shot: S1, tx: -130, ty: 500, dx: 0, dy: 190, at: t + 0.4, until: bt('pmv.b2').end + 0.3, states: [{ t: 0, open: true }] });
    // door between "well" and "system"
    const b1 = P(S1, 0, 650), b2 = P(S1, 0, 360);
    ctx.tagAt({ x: b1[0] + 60, y: b1[1], text: 'WELL', color: '#FF9A3C', mono: true, size: 26, at: w('pmv.b1', 'well') - 0.2, until: t2 - 0.1 });
    ctx.tagAt({ x: b2[0] + 60, y: b2[1], text: 'REST OF THE SYSTEM', color: '#2ED0FF', mono: true, size: 26, at: w('pmv.b1', 'system') - 0.3, until: t2 - 0.1 });
    // b2
    ctx.note({ shot: S1, at: w('pmv.b2', 'stays') - 0.2, until: w('pmv.b2', 'avoid') - 0.2, tx: 0, ty: 500, dx: 110, dy: -215, label: 'Normally OPEN', color: '#3BDB86', size: 30 });
    const pa = P(S1, -90, 500);
    badge({ at: w('pmv.b2', 'avoid') - 0.2, until: w('pmv.b2', 'protect') - 0.3, x: pa[0] - 330, y: pa[1] + 230, html: noIcon('#FF3B5C') + 'Not operated while flowing', color: '#FF3B5C', size: 26 });
    ctx.ringAt({ shot: S1, tx: -30, ty: 487, r: 26, color: '#3BDB86', at: w('pmv.b2', 'protect') - 0.2, until: w('pmv.b2', 'many') - 0.2 });
    ctx.ringAt({ shot: S1, tx: 30, ty: 513, r: 26, color: '#3BDB86', at: w('pmv.b2', 'protect') - 0.2, until: w('pmv.b2', 'many') - 0.2 });
    ctx.tagAt({ x: P(S1, 30, 513)[0] + 150, y: P(S1, 30, 513)[1] + 90, text: 'Seals protected', color: '#3BDB86', size: 26, at: w('pmv.b2', 'protect') - 0.1, until: w('pmv.b2', 'many') - 0.2 });
    // ghost second master valve
    const gp0 = P(S1, -110, 394), gp1 = P(S1, 110, 426);
    const ghost = S('g');
    ghost.append(
      S('rect', { x: gp0[0], y: gp0[1], width: gp1[0] - gp0[0], height: gp1[1] - gp0[1], rx: 10, fill: 'rgba(255,200,87,.10)', stroke: '#FFC857', 'stroke-width': 3.5, 'stroke-dasharray': '12 9' }),
      S('path', { d: `M${(gp0[0] + gp1[0]) / 2 - 22} ${gp0[1] + 10} l22 12 l22 -12 M${(gp0[0] + gp1[0]) / 2 - 22} ${gp1[1] - 10} l22 -12 l22 12`, fill: 'none', stroke: '#FFC857', 'stroke-width': 4, 'stroke-linecap': 'round' }));
    annot.append(ghost);
    tl.fromTo(ghost, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: true }, w('pmv.b2', 'two') - 0.3);
    tl.to(ghost, { opacity: 0, duration: 0.4 }, bt('pmv.b2').end + 0.2);
    ctx.tagAt({ x: gp1[0] + 40, y: (gp0[1] + gp1[1]) / 2 - 60, text: 'Second master valve', sub: 'in series – extra security', color: '#FFC857', anchor: 'l', size: 26, at: w('pmv.b2', 'two') - 0.2, until: bt('pmv.b2').end + 0.2 });
  }

  /* ====================================================================================== */
  /* PWV                                                                                    */
  /* ====================================================================================== */
  const wingFlows = [tree.flows.p_out1, tree.flows.p_out2];
  const wingShut = (t) => {
    V.PWV.close(t, 0.6, 'power3.in');
    tree.flows.p_mid.speed(t + 0.2, 0, 0.5); tree.flows.p_low.speed(t + 0.2, 0, 0.5);
    wingFlows.forEach((f, i) => f.hide(t + 0.25 + 0.2 * i, 0.5));
    ['p_out1', 'p_out2'].forEach((n) => tree.fills[n].to(t + 0.3, 0.6, 0.18));
    ['p_mid', 'p_tee', 'p_br1', 'p_br2'].forEach((n) => tree.fills[n].to(t + 0.3, 0.8, 0.8));
  };
  const wingOpen = (t) => {
    V.PWV.open(t, 1.2, 'power2.inOut');
    tree.flows.p_mid.speed(t + 0.7, 70, 0.5); tree.flows.p_low.speed(t + 0.7, 70, 0.5);
    wingFlows.forEach((f, i) => f.show(t + 0.8 + 0.15 * i, 0.5, 75));
    ['p_out1', 'p_out2'].forEach((n) => tree.fills[n].to(t + 0.8, 0.6, 0.5));
    ['p_mid', 'p_tee', 'p_br1', 'p_br2'].forEach((n) => tree.fills[n].to(t + 0.8, 0.8, 0.5));
  };
  {
    const S1 = VSH.pwv;
    const t = bt('pwv.b1').start, t2 = bt('pwv.b2').start;
    cam.go(t - 0.5, 1.8, S1, 'power3.inOut');
    ctx.note({ shot: S1, at: w('pwv.b1', 'wing') - 0.3, until: t2 - 0.1, tx: -230, ty: 320, dx: 180, dy: -230, label: 'Production wing valve', sub: 'PWV', color: '#2ED0FF', size: 30 });
    ctx.status({ name: 'PWV', shot: S1, tx: -230, ty: 320, dx: 190, dy: -150, at: t + 0.5, until: bt('pwv.b2').end + 0.3, states: [{ t: 0, open: true }, { t: w('pwv.b2', 'shut') + 0.3, open: false }, { t: bt('pwv.b2').end - 0.25 + 0.6, open: true }] });
    ctx.tagAt({ x: P(S1, -230, 320)[0] - 40, y: P(S1, -230, 320)[1] + 175, text: 'THE WORKING VALVE', color: '#2ED0FF', mono: true, size: 26, anchor: 'r', at: w('pwv.b1', 'working') - 0.2, until: t2 - 0.1 });
    // b2: shut in
    wingShut(w('pwv.b2', 'shut') - 0.05);
    sfx(w('pwv.b2', 'shut') + 0.4, 'clunk', 0.8);
    ctx.tagAt({ x: P(S1, -330, 320)[0], y: P(S1, -330, 320)[1] - 190, text: 'WELL SHUT IN', color: '#FF3B5C', mono: true, size: 28, anchor: 'c', at: w('pwv.b2', 'shut') + 0.5, until: w('pwv.b2', 'master') - 0.3 });
    const pg = gauge(annot, { x: 1700, y: 860, r: 62, max: 250, label: 'TREE PRESSURE', numeric: false, color: '#FF9A3C', v0: 120, labelBg: true });
    show(pg.g, w('pwv.b2', 'shut') + 0.2, 0.5, { y: 20 });
    pg.to(w('pwv.b2', 'shut') + 0.4, 1.8, 190, 'power2.out');
    hide(pg.g, bt('pwv.b2').end - 0.4, 0.4);
    const pm = P(S1, 0, 500);
    ctx.ringAt({ shot: S1, tx: 0, ty: 500, r: 56, color: '#3BDB86', at: w('pwv.b2', 'master') - 0.2, until: bt('pwv.b2').end - 0.2 });
    ctx.tagAt({ x: pm[0] - 80, y: pm[1] + 100, text: 'Master valve untouched', sub: 'seals stay in perfect condition', color: '#3BDB86', anchor: 'r', size: 26, at: w('pwv.b2', 'master') - 0.2, until: bt('pwv.b2').end - 0.2 });
    wingOpen(bt('pwv.b2').end - 0.25);
  }

  /* ====================================================================================== */
  /* CHOKE                                                                                  */
  /* ====================================================================================== */
  const chokeSpeed = (t, f, d) => {
    const v = 30 + 110 * f;
    tree.flows.p_out1.speed(t, v, d); tree.flows.p_out2.speed(t, v, d); tree.flows.p_mid.speed(t, v * 0.8, d); tree.flows.p_low.speed(t, v * 0.8, d);
  };
  {
    const S1 = VSH.choke;
    const t = bt('choke.b1').start, t2 = bt('choke.b2').start;
    cam.go(t - 0.5, 1.8, S1, 'power3.inOut');
    ctx.note({ shot: S1, at: w('choke.b1', 'choke') - 0.2, until: t2 - 0.2, tx: -450, ty: 330, dx: -60, dy: -210, label: 'Production choke', color: '#FF9A3C', size: 30 });
    ctx.status({ name: 'CHOKE', shot: S1, tx: -400, ty: 320, dx: 20, dy: 200, at: t + 0.6, until: bt('choke.b2').end + 0.3, states: [{ t: 0, open: true }] });
    const na = P(S1, -440, 300);
    badge({ at: w('choke.b1', 'shut-off') - 0.2, until: w('choke.b1', 'throttle') - 0.3, x: na[0] - 530, y: na[1] + 220, html: noIcon('#FF3B5C') + 'Not a shut-off valve', color: '#FF3B5C', size: 26 });
    // throttle: wiggle the plug (steps are strictly chronological)
    const tt = w('choke.b1', 'throttle');
    let tcur = tt - 0.15;
    const cp = { f: 0.5 };
    let mFlow = null, mPress = null;
    const step = (t0, d, f) => {
      const ts = Math.max(t0, tcur);
      tree.choke.to(ts, d, f); chokeSpeed(ts, f, d);
      const from = cp.f;
      tl.fromTo(cp, { f: from }, { f, duration: d, ease: 'power2.inOut', onUpdate: () => { if (mFlow) { mFlow.set(0.12 + 0.82 * cp.f); mPress.set(0.9 - 0.7 * cp.f); } }, immediateRender: false }, ts);
      cp.f = f; tcur = ts + d;
    };
    step(tt - 0.15, 0.45, 0.15);
    step(tt + 0.35, 0.5, 0.85);
    step(tt + 0.95, 0.45, 0.5);
    ctx.tagAt({ x: P(S1, -400, 320)[0] + 80, y: P(S1, -400, 320)[1] - 250, text: 'THE THROTTLE', color: '#FF9A3C', mono: true, size: 28, anchor: 'c', at: tt - 0.2, until: t2 - 0.2 });
    // b2: meters
    const mx = 1560, my = 760;
    const meter = (x, label, col, v0) => {
      const g = S('g', { transform: `translate(${x} ${my})` });
      const gi = S('g');
      g.append(gi);
      const bar = S('rect', { x: 8, y: -200 * v0, width: 54, height: 200 * v0, rx: 6, fill: col });
      gi.append(S('rect', { x: -20, y: -260, width: 108, height: 330, rx: 16, fill: 'rgba(5,16,26,.9)', stroke: 'rgba(170,200,225,.3)', 'stroke-width': 1.6 }),
        S('rect', { x: 8, y: -200, width: 54, height: 200, rx: 6, fill: 'rgba(255,255,255,.08)' }), bar,
        S('text', { x: 34, y: 38, 'text-anchor': 'middle', fill: '#AFC0CE', 'font-size': 15, 'font-weight': 700, 'letter-spacing': '0.08em', text: label }));
      annot.append(g);
      return { g: gi, bar, set(v) { bar.setAttribute('y', (-200 * v).toFixed(1)); bar.setAttribute('height', (200 * v).toFixed(1)); } };
    };
    mFlow = meter(mx, 'FLOW', '#FF9A3C', 0.5); mPress = meter(mx + 150, 'PRESS.', '#FF3B5C', 0.5);
    const ta = w('choke.b2', 'adjusting');
    show(mFlow.g, ta - 0.2, 0.5, { y: 20 }); show(mPress.g, ta - 0.2, 0.5, { y: 20 });
    step(ta + 0.5, 1.0, 0.85);
    step(w('choke.b2', 'pressure') - 0.1, 1.1, 0.25);
    step(w('choke.b2', 'fast') - 0.3, 0.9, 0.55);
    ctx.tagAt({ x: mx - 40, y: my - 330, text: 'More open: more flow, less pressure', color: '#FF9A3C', anchor: 'r', size: 22, at: ta + 0.3, until: w('choke.b2', 'pressure') - 0.2 });
    ctx.tagAt({ x: mx - 40, y: my - 330, text: 'More closed: less flow, more pressure', color: '#FF3B5C', anchor: 'r', size: 22, at: w('choke.b2', 'pressure') - 0.05, until: w('choke.b2', 'fast') - 0.3 });
    hide(mFlow.g, w('choke.b2', 'tungsten') - 0.5, 0.4); hide(mPress.g, w('choke.b2', 'tungsten') - 0.5, 0.4);
    // abrasive flow sparks across the orifice
    const spark = S('g', { fill: '#FFF2C4' });
    const r = rng(5);
    const sp = Array.from({ length: 16 }, () => ({ el: S('circle', { r: 2.6 }), y: r() * 36 - 18, v: 120 + r() * 220, ph: r() }));
    sp.forEach((s_) => spark.append(s_.el));
    tree.root.append(spark);
    tl.set(spark, { opacity: 0 }, 0);
    tl.fromTo(spark, { opacity: 0 }, { opacity: 1, duration: 0.3, immediateRender: false }, w('choke.b2', 'fast') - 0.1);
    tl.to(spark, { opacity: 0, duration: 0.3 }, w('choke.b2', 'tungsten') + 0.3);
    animate(w('choke.b2', 'fast') - 0.2, w('choke.b2', 'tungsten') + 0.8, (tm) => sp.forEach((s_) => { const p = ((tm * s_.v / 120 + s_.ph * 6) % 1 + 1) % 1; s_.el.setAttribute('cx', (-440 + p * 110).toFixed(1)); s_.el.setAttribute('cy', (320 + s_.y * (0.4 + 0.6 * Math.sin(p * Math.PI))).toFixed(1)); }));
    ctx.note({ shot: S1, at: w('choke.b2', 'abrasive') - 0.2, until: w('choke.b2', 'tungsten') - 0.3, tx: -420, ty: 322, dx: -40, dy: 230, label: 'Fast, abrasive flow', color: '#FFC857', size: 26 });
    ctx.ringAt({ shot: S1, tx: -418, ty: 322, r: 46, color: '#FFC857', at: w('choke.b2', 'tungsten') - 0.2, until: w('choke.b2', 'insert') - 0.3 });
    ctx.ringAt({ shot: S1, tx: -382, ty: 322, r: 46, color: '#FFC857', at: w('choke.b2', 'tungsten') - 0.2, until: w('choke.b2', 'insert') - 0.3 });
    ctx.note({ shot: S1, at: w('choke.b2', 'tungsten') - 0.2, until: w('choke.b2', 'insert') - 0.3, tx: -382, ty: 340, dx: 150, dy: 170, label: 'Tungsten carbide trim', color: '#FFC857', size: 26 });
    // ROV lifts the insert
    const tr = w('choke.b2', 'insert');
    const rovWrap = S('g');
    annot.append(rovWrap);
    const rv = S('g', { transform: 'scale(-0.95 0.95)' });   // faces left
    rovWrap.append(rv);
    rov(rv, { scale: 1 });
    gsap.set(rovWrap, { x: 2250, y: 120 });
    const top = P(S1, -400, 108);
    tl.to(rovWrap, { x: top[0] + 130, y: top[1] - 40, duration: 1.6, ease: 'power2.inOut' }, tr - 0.5);
    tl.to(tree.choke.insert, { y: -120, duration: 1.2, ease: 'power2.inOut' }, tr + 1.3);
    tl.to(rovWrap, { y: top[1] - 40 - 120 * S1.k, duration: 1.2, ease: 'power2.inOut' }, tr + 1.3);
    ctx.tagAt({ x: top[0] - 120, y: top[1] - 150, text: 'ROV-retrievable insert', color: '#FFC857', anchor: 'r', size: 28, at: tr + 0.1, until: bt('choke.b2').end + 0.3 });
    const tEnd = bt('choke.b2').end + 0.1;
    tl.to(tree.choke.insert, { y: 0, duration: 1.0, ease: 'power2.inOut' }, tEnd);
    tl.to(rovWrap, { y: top[1] - 40, duration: 1.0, ease: 'power2.inOut' }, tEnd);
    tl.to(rovWrap, { x: 2300, duration: 1.4, ease: 'power2.in' }, tEnd + 1.0);
  }

  /* ====================================================================================== */
  /* PSV                                                                                    */
  /* ====================================================================================== */
  {
    const S1 = VSH.psv;
    const t = bt('psv.b1').start;
    cam.go(t - 1.2, 2.0, S1, 'power3.inOut');
    ctx.note({ shot: S1, at: w('psv.b1', 'swab') - 0.3, until: w('psv.b1', 'straight') - 0.2, tx: -70, ty: 110, dx: -190, dy: -150, label: 'Production swab valve', sub: 'PSV', color: '#BC8FFF', size: 30 });
    const stTags = ctx.status({ name: 'PSV', shot: S1, tx: 90, ty: 110, dx: 230, dy: 10, at: t + 1.6, until: bt('psv.b1').end + 0.3, states: [{ t: 0, open: false }, { t: w('psv.b1', 'wireline') + 0.75, open: true }, { t: w('psv.b1', 'stays') + 1.3, open: false }] });
    // straight vertical access
    const top = P(S1, 0, 40), bottom = P(S1, 0, 330);
    const arrow = S('g', { fill: 'none', stroke: '#2ED0FF', 'stroke-width': 7, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-dasharray': '16 12' });
    arrow.append(S('path', { d: `M${top[0] - 80} ${top[1] - 160} V${bottom[1] + 20}` }));
    annot.append(arrow);
    tl.set(arrow, { opacity: 0 }, 0);
    tl.fromTo(arrow, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: false }, w('psv.b1', 'straight') - 0.2);
    tl.to(arrow, { opacity: 0, duration: 0.4 }, w('psv.b1', 'wireline') - 0.4);
    ctx.tagAt({ x: top[0] - 120, y: top[1] - 40, text: 'Straight down the bore', color: '#2ED0FF', anchor: 'r', size: 26, at: w('psv.b1', 'straight') - 0.1, until: w('psv.b1', 'wireline') - 0.4 });
    // wireline tool
    const tool = S('g');
    tool.append(
      S('line', { x1: 0, y1: -700, x2: 0, y2: -34, stroke: '#FFC857', 'stroke-width': 3.5 }),
      S('rect', { x: -12, y: -34, width: 24, height: 58, rx: 6, fill: '#FFC857', stroke: '#0B141C', 'stroke-width': 2.5 }),
      S('rect', { x: -6, y: 24, width: 12, height: 12, rx: 3, fill: '#EEF4F9' }));
    tree.root.append(tool);
    gsap.set(tool, { y: -20, opacity: 0 });
    const tw = w('psv.b1', 'wireline');
    tl.to(tool, { opacity: 1, duration: 0.3 }, tw - 0.1);
    V.PSV.open(tw + 0.1, 1.0, 'power2.inOut');
    tl.to(tool, { y: 380, duration: 2.0, ease: 'power2.inOut' }, tw + 0.8);
    tl.to(tool, { y: -20, duration: 1.2, ease: 'power2.inOut' }, w('psv.b1', 'stays') - 0.4);
    tl.to(tool, { opacity: 0, duration: 0.3 }, w('psv.b1', 'stays') + 0.8);
    V.PSV.close(w('psv.b1', 'stays') + 0.8, 0.9, 'power2.inOut');
    ctx.tagAt({ x: top[0] + 180, y: top[1] + 60, text: 'Wireline tool', sub: 'lowered into the well', color: '#FFC857', size: 26, at: tw + 0.6, until: w('psv.b1', 'stays') - 0.4 });
    ctx.tagAt({ x: top[0] + 200, y: top[1] + 228, text: 'CLOSED during production', color: '#FF3B5C', mono: true, size: 24, at: w('psv.b1', 'stays') + 0.5, until: bt('psv.b1').end + 0.3 });
  }

  /* ====================================================================================== */
  /* ANNULUS                                                                                */
  /* ====================================================================================== */
  let annG = null;
  {
    const S1 = VSH.ann;
    const t = bt('annulus.b1').start, t2 = bt('annulus.b2').start;
    cam.go(t - 0.8, 1.9, S1, 'power3.inOut');
    ctx.ringAt({ shot: S1, tx: 150, ty: 300, r: 48, color: '#34D8A8', at: w('annulus.b1', 'annulus') - 0.2, until: w('annulus.b1', 'master') - 0.2 });
    ctx.note({ shot: S1, at: w('annulus.b1', 'annulus') - 0.2, until: w('annulus.b1', 'master') - 0.2, tx: 150, ty: 300, dx: -200, dy: -120, label: 'Annulus bore', color: '#34D8A8', size: 28 });
    const rings = [
      { w: 'master', tx: 150, ty: 500, label: 'AMV', sub: 'annulus master', dx: -170, dy: 120 },
      { w: 'wing', tx: 400, ty: 320, label: 'AWV', sub: 'annulus wing', dx: 40, dy: 190 },
      { w: 'swab', tx: 150, ty: 110, label: 'ASV', sub: 'annulus swab', dx: -190, dy: -100 },
    ];
    rings.forEach((r) => {
      const ta = w('annulus.b1', r.w) - 0.2;
      ctx.ringAt({ shot: S1, tx: r.tx, ty: r.ty, r: 46, color: '#34D8A8', at: ta, until: t2 + 0.2 });
      ctx.note({ shot: S1, at: ta, until: t2 + 0.2, tx: r.tx, ty: r.ty, dx: r.dx, dy: r.dy, label: r.label, sub: r.sub, color: '#34D8A8', size: 28, mono: true, anchor: r.dx < 0 ? 'r' : 'c' });
    });
    // b2 status + pressure rise
    ctx.status({ name: 'AMV', shot: S1, tx: 150, ty: 500, dx: -80, dy: 130, at: t2 + 0.2, until: bt('xov.b2').end + 0.3, states: [{ t: 0, open: true }], anchor: 'c' });
    ctx.status({ name: 'AWV', shot: S1, tx: 400, ty: 320, dx: 0, dy: 140, at: t2 + 0.2, until: bt('xov.b2').end + 0.3, states: [{ t: 0, open: false }] });
    ctx.status({ name: 'ASV', shot: S1, tx: 150, ty: 110, dx: -150, dy: -90, at: t2 + 0.2, until: bt('annulus.b2').end + 0.3, states: [{ t: 0, open: false }] });
    fadeIn(tree.overlays.sensors.g, w('annulus.b2', 'monitor') - 0.3, 0.6);
    ctx.note({ shot: S1, at: w('annulus.b2', 'monitor') - 0.2, until: w('annulus.b2', 'heats') - 0.3, tx: 217, ty: 410, dx: 190, dy: -50, label: 'Pressure sensor', color: '#FFC857', size: 26 });
    annG = gauge(annot, { x: 1745, y: 800, r: 70, max: 250, label: 'ANNULUS PRESSURE', color: '#34D8A8', v0: 40, numeric: true });
    show(annG.g, w('annulus.b2', 'monitor') - 0.2, 0.5, { y: 20 });
    // thermometer
    const th = S('g', { transform: 'translate(1770 250)' });
    const thi = S('g');
    th.append(thi);
    const merc = S('rect', { x: -6, y: 60, width: 12, height: 0, fill: '#FF3B5C' });
    thi.append(S('rect', { x: -14, y: -70, width: 28, height: 150, rx: 14, fill: '#0B1823', stroke: '#EEF4F9', 'stroke-width': 4 }), S('circle', { cx: 0, cy: 82, r: 24, fill: '#FF3B5C', stroke: '#EEF4F9', 'stroke-width': 4 }), merc,
      S('text', { x: 0, y: 140, 'text-anchor': 'middle', fill: '#FF9A9A', 'font-size': 20, 'font-weight': 700, 'letter-spacing': '0.12em', text: 'WELL HEATS UP' }));
    annot.append(th);
    show(thi, w('annulus.b2', 'heats') - 0.2, 0.5, { y: 20 });
    tl.fromTo(merc, { attr: { y: 60, height: 0 } }, { attr: { y: -50, height: 120 }, duration: 2.8, ease: 'power1.inOut', immediateRender: true }, w('annulus.b2', 'heats'));
    hide(thi, bt('annulus.b2').end + 0.1, 0.4);
    annG.to(w('annulus.b2', 'heats'), 3.6, 160, 'power1.in');
    tl.to(well.fills.annulus.els, { opacity: 0.55, duration: 2.0 }, w('annulus.b2', 'trapped'));
    tree.fills.a_mid.to(w('annulus.b2', 'trapped'), 1.0, 0.8);
    ctx.tagAt({ x: 1745, y: 944, text: 'Trapped fluid expands', color: '#FF9A9A', anchor: 'c', size: 24, at: w('annulus.b2', 'trapped') - 0.2, until: bt('annulus.b2').end + 0.2 });
  }

  /* ====================================================================================== */
  /* XOV                                                                                    */
  /* ====================================================================================== */
  {
    const S1 = VSH.xov;
    const t = bt('xov.b1').start, t2 = bt('xov.b2').start;
    cam.go(t - 0.5, 1.9, S1, 'power3.inOut');
    fadeIn(tree.overlays.xover.g, w('xov.b1', 'crossover') - 0.4, 0.9);
    fadeIn(V.XOV.g, w('xov.b1', 'crossover') - 0.2, 0.8);
    tree.overlays.xover.fillEl.setAttribute('stroke', '#34D8A8');
    ctx.note({ shot: S1, at: w('xov.b1', 'crossover') - 0.2, until: t2 + 0.2, tx: 300, ty: 130, dx: -10, dy: -200, label: 'Crossover valve', sub: 'XOV · links the two sides', color: '#34D8A8', size: 30, anchor: 'b' });
    ctx.status({ name: 'XOV', shot: S1, tx: 300, ty: 130, dx: 170, dy: 40, at: w('xov.b1', 'normally') - 0.3, until: bt('xov.b2').end + 0.3, states: [{ t: 0, open: false }, { t: w('xov.b2', 'Open') + 0.9, open: true }, { t: bt('xov.b2').end + 0.5, open: false }] });
    // b2: open + bleed
    const to = w('xov.b2', 'Open');
    V.XOV.open(to, 1.2, 'power2.inOut');
    const xo0 = Flow(tree.root, 'M150 470 V340 Q150 320 175 320 H300', { color: COL.ann, w: 6, gap: 20 });
    xo0.show(to + 1.0, 0.4, 90);
    tree.flows.xo.show(to + 1.5, 0.4, 90);
    annG.to(to + 0.9, 2.2, 45, 'power2.out');
    tl.to(tree.overlays.xover.fillEl, { opacity: 0.4, duration: 0.5 }, to + 1.2);
    ctx.tagAt({ x: 1480, y: 140, text: 'Annulus pressure bled into the flowline', color: '#34D8A8', anchor: 'c', size: 26, at: w('xov.b2', 'annulus') - 0.3, until: bt('xov.b2').end + 0.2 });
    const tc = bt('xov.b2').end + 0.1;
    V.XOV.close(tc, 0.5, 'power3.in');
    xo0.hide(tc + 0.3, 0.4); tree.flows.xo.hide(tc + 0.3, 0.4);
    tl.to(tree.overlays.xover.fillEl, { opacity: 0, duration: 0.5 }, tc + 0.3);
    tl.to(well.fills.annulus.els, { opacity: 0.16, duration: 1.0 }, to + 1.0);
    tree.fills.a_mid.to(to + 1.0, 1.0, 0.45);
    hide(annG.g, tc + 0.2, 0.5);
  }

  /* ====================================================================================== */
  /* CIV                                                                                    */
  /* ====================================================================================== */
  {
    const S1 = VSH.civ;
    const t = bt('civ.b1').start, t2 = bt('civ.b2').start;
    cam.go(t - 0.6, 1.9, S1, 'power3.inOut');
    fadeIn(tree.overlays.ci.g, w('civ.b1', 'chemical') - 0.2, 0.9);
    fadeIn(V.CIV.g, w('civ.b1', 'chemical') - 0.1, 0.8);
    tree.overlays.ci.fillEl.setAttribute('stroke', '#BC8FFF');
    ctx.note({ shot: S1, at: w('civ.b1', 'injection') - 0.3, until: t2 + 0.3, tx: -390, ty: 430, dx: 20, dy: -190, label: 'Chemical injection valve', sub: 'CIV', color: '#BC8FFF', size: 30, anchor: 'b' });
    ctx.status({ name: 'CIV', shot: S1, tx: -390, ty: 430, dx: 20, dy: 150, at: w('civ.b1', 'injection') + 0.2, until: bt('civ.b2').end + 0.3, states: [{ t: 0, open: false }, { t: w('civ.b1', 'chemicals') + 0.5, open: true }] });
    ctx.note({ shot: S1, at: w('civ.b1', 'umbilical') - 0.2, until: t2 + 0.3, tx: -700, ty: 430, dx: 60, dy: -150, label: 'Umbilical', sub: 'chemicals from the host', color: '#C9A227', size: 26, anchor: 'l' });
    const tc = w('civ.b1', 'chemicals');
    V.CIV.open(tc - 0.2, 0.8, 'power2.inOut');
    tl.to(tree.overlays.ci.fillEl, { opacity: 0.4, duration: 0.6 }, tc + 0.4);
    tree.flows.ci.show(tc + 0.4, 0.5, 80);
    // Snøhvit inset
    const ix = 1200, iy = 120, iw = 660, ih = 330;
    const ins = S('g', { transform: `translate(${ix} ${iy})` });
    const insI = S('g');
    ins.append(insI);
    annot.append(ins);
    insI.append(S('rect', { width: iw, height: ih, rx: 20, fill: 'rgba(5,16,26,.94)', stroke: 'rgba(170,200,225,.32)', 'stroke-width': 1.8 }),
      S('text', { x: 28, y: 44, fill: '#FFC857', 'font-size': 22, 'font-weight': 800, 'letter-spacing': '0.16em', text: 'SNØHVIT' }));
    const tree0 = S('g', { transform: 'translate(70 250)' });
    miniTree(tree0, { scale: 1.1 });
    const pl = S('g', { transform: `translate(${iw - 90} 246)` });
    plant(pl, { scale: 0.34, flame: false });
    insI.append(tree0, pl);
    const lineD = `M130 210 H${iw - 170}`;
    insI.append(S('path', { d: lineD, stroke: '#07131C', 'stroke-width': 18, 'stroke-linecap': 'round', fill: 'none' }), S('path', { d: lineD, stroke: '#51677A', 'stroke-width': 12, 'stroke-linecap': 'round', fill: 'none' }));
    insI.append(S('text', { x: (130 + iw - 170) / 2, y: 175, 'text-anchor': 'middle', fill: '#EEF4F9', 'font-size': 30, 'font-weight': 700, style: { fontFamily: 'var(--mono)' }, text: '143 km' }));
    // hydrate crystals
    const crystals = S('g');
    const rr = rng(21);
    const cry = Array.from({ length: 9 }, (_, i) => { const x = 170 + i * 48 + rr() * 14; const c = S('path', { d: 'M0 -12 l10 6 v12 l-10 6 l-10 -6 v-12 z', fill: '#EAF6FF', stroke: '#9FD0FF', 'stroke-width': 2, transform: `translate(${x.toFixed(1)} ${(210 + (rr() * 6 - 3)).toFixed(1)})` }); crystals.append(c); return c; });
    insI.append(crystals);
    tl.set(crystals, { opacity: 0 }, 0);
    const megFlow = Flow(insI, lineD, { color: '#BC8FFF', w: 7, gap: 22 });
    const tH = w('civ.b2', 'hydrates');
    show(insI, w('civ.b2', 'Snøhvit') - 0.2, 0.6, { y: -20 });
    ctx.tagAt({ x: ix + iw / 2, y: iy + ih + 36, text: 'MEG = monoethylene glycol', sub: 'prevents hydrate crystals', color: '#BC8FFF', anchor: 'c', size: 26, at: w('civ.b2', 'MEG') - 0.2, until: bt('civ.b2').end + 0.3 });
    megFlow.show(w('civ.b2', 'injected') - 0.2, 0.4, 80);
    // crystals form (no MEG) then vanish when MEG arrives -> we show them flash then X
    tl.fromTo(crystals, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: false }, tH - 0.4);
    const blockX = S('g', { opacity: 0, stroke: '#FF3B5C', 'stroke-width': 8, 'stroke-linecap': 'round' }, S('path', { d: `M${(130 + iw - 170) / 2 - 36} 245 L${(130 + iw - 170) / 2 + 36} 285 M${(130 + iw - 170) / 2 + 36} 245 L${(130 + iw - 170) / 2 - 36} 285` }));
    insI.append(blockX);
    tl.to(crystals, { opacity: 0, duration: 0.6 }, w('civ.b2', 'cannot') + 0.2);
    tl.fromTo(blockX, { opacity: 0 }, { opacity: 1, duration: 0.3, immediateRender: false }, w('civ.b2', 'cannot'));
    tl.to(blockX, { opacity: 0, duration: 0.4 }, w('civ.b2', 'cannot') + 1.1);
    hide(insI, bt('civ.b2').end + 0.1, 0.5);
  }

  /* ====================================================================================== */
  /* DHSV                                                                                   */
  /* ====================================================================================== */
  {
    const t = bt('dhsv.b1').start;
    well.dhsv.cur = 1; well.dhsv.set(1);
    // production state in the well: flows below / above the DHSV
    well.fills.tubing.to(t - 1, 0.5, 0.5);
    well.flows.tubLow.show(t - 0.5, 0.4, 70); well.flows.tubHigh.show(t - 0.5, 0.4, 70);
    well.flows.inL.show(t - 0.5, 0.4, 70); well.flows.inR.show(t - 0.5, 0.4, 70);
    const W1 = VSH.dhsvWide, W2 = VSH.dhsv;
    cam.go(t - 0.3, 3.2, W1, 'power2.inOut');
    ctx.ringAt({ wx: 0, wy: well.dhsv.g ? 560 : 560, shot: W1, r: 80, color: '#FF4F6D', at: w('dhsv.b1', 'downhole') - 0.3, until: bt('dhsv.b2').start + 0.1 });
    const dp = proj(W1, 0, 560);
    ctx.tagAt({ x: dp[0] + 120, y: dp[1] - 30, text: 'Downhole safety valve', sub: 'DHSV · deep in the well', color: '#FF4F6D', size: 30, at: w('dhsv.b1', 'downhole') - 0.3, until: bt('dhsv.b2').start + 0.3 });
    ctx.tagAt({ x: dp[0] - 120, y: dp[1] - 220, text: 'Tubing', color: '#B3C4D2', anchor: 'r', size: 24, at: w('dhsv.b1', 'deep') - 0.2, until: bt('dhsv.b2').start - 0.2 });
    // b2: control line
    const t2 = bt('dhsv.b2').start;
    fadeIn(tree.overlays.scm.g, t2 - 1.0, 0.8);
    fadeIn(tree.overlays.dhsvLine.g, t2 - 0.6, 0.8);
    well.flows.ctrl.show(w('dhsv.b2', 'control') + 0.2, 0.4, 100);
    tree.flows.dhsvTop.show(w('dhsv.b2', 'control') + 0.2, 0.4, 100);
    const lp = proj(W1, 88, 200);
    ctx.note({ shot: W1, at: w('dhsv.b2', 'hydraulic') - 0.2, until: w('dhsv.b2', 'tree') - 0.2, wx: 88, wy: 220, dx: 200, dy: 0, label: 'Hydraulic control line', color: '#2ED0FF', size: 28 });
    const hp = proj(W1, 88, -140);
    ctx.note({ shot: W1, at: w('dhsv.b2', 'tree') - 0.2, until: w('dhsv.b2', 'down') - 0.3, wx: 88, wy: -140, dx: 220, dy: 20, label: 'Through the tubing hanger', color: '#2ED0FF', size: 26 });
    ctx.ringAt({ shot: W1, wx: 88, wy: -140, r: 34, color: '#2ED0FF', at: w('dhsv.b2', 'hanger') - 0.2, until: w('dhsv.b2', 'down') + 0.2 });
    ctx.ringAt({ shot: W1, wx: 44, wy: 496, r: 34, color: '#2ED0FF', at: w('dhsv.b2', 'valve') - 0.3, until: bt('dhsv.b2').end + 0.4 });
    // b3: close-up on the flapper valve
    const t3 = bt('dhsv.b3').start;
    cam.go(t3 - 0.5, 1.9, W2, 'power3.inOut');
    const cg = gauge(annot, { x: 1700, y: 820, r: 66, max: 700, label: 'CONTROL LINE', color: '#2ED0FF', v0: 600, numeric: false });
    show(cg.g, t3 + 0.3, 0.5, { y: 20 });
    ctx.note({ shot: W2, at: w('dhsv.b3', 'flapper') - 0.3, until: w('dhsv.b3', 'spring') - 0.3, wx: -26, wy: 630, dx: -230, dy: 100, label: 'Flapper', color: '#EEF4F9', size: 30 });
    ctx.note({ shot: W2, at: w('dhsv.b3', 'hydraulic') - 0.3, until: w('dhsv.b3', 'flapper') - 0.3, wx: 48, wy: 430, dx: 240, dy: -60, label: 'Piston', sub: 'pushed down by pressure', color: '#2ED0FF', size: 26 });
    ctx.note({ shot: W2, at: w('dhsv.b3', 'spring') - 0.3, until: w('dhsv.b3', 'Lose') - 0.2, wx: 48, wy: 500, dx: 250, dy: 40, label: 'Spring', sub: 'pushes the piston up', color: '#FFC857', size: 28 });
    ctx.status({ name: 'DHSV', shot: W2, tx: 0, ty: 0, wx: 0, wy: 372, dx: 0, dy: 0, at: t3 + 0.2, until: bt('dhsv.b3').end + 0.3, states: [{ t: 0, open: true }, { t: w('dhsv.b3', 'snaps') + 0.3, open: false }] });
    const tClose = w('dhsv.b3', 'Lose');
    cg.to(tClose, 1.3, 0, 'power2.in');
    well.flows.ctrl.speed(tClose + 0.1, 0, 0.8); tree.flows.dhsvTop.speed(tClose + 0.1, 0, 0.8);
    well.dhsv.close(w('dhsv.b3', 'snaps') - 0.15, 0.5);
    well.flows.tubHigh.hide(w('dhsv.b3', 'snaps') + 0.3, 0.5);
    well.flows.ctrl.hide(w('dhsv.b3', 'snaps') + 0.8, 0.4); tree.flows.dhsvTop.hide(w('dhsv.b3', 'snaps') + 0.8, 0.4);
    sfx(w('dhsv.b3', 'snaps') - 0.05, 'clunk', 1.0);
    ctx.ringAt({ shot: W2, wx: 0, wy: 630, r: 60, color: '#FF3B5C', at: w('dhsv.b3', 'sealing') - 0.2, until: bt('dhsv.b3').end + 0.3 });
    ctx.tagAt({ x: 1700, y: 650, text: 'TUBING SEALED', color: '#FF3B5C', mono: true, size: 28, anchor: 'c', at: w('dhsv.b3', 'sealing') - 0.2, until: bt('dhsv.b3').end + 0.3 });
    hide(cg.g, bt('dhsv.b3').end + 0.2, 0.4);
  }
}
