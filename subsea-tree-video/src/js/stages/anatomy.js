// Scene 5 – Anatomy of a vertical tree (130 – 180 s) ----------------------------------
import { H, S } from '../lib/svg.js';

export const SHOT = {
  full: { wx: -20, wy: -470, sx: 1220, sy: 545, k: 0.9 },
  fullC: { wx: -20, wy: -470, sx: 960, sy: 545, k: 0.9 },
  conn: { wx: 0, wy: -222, sx: 1180, sy: 560, k: 1.7 },
  hanger: { wx: 0, wy: -150, sx: 1180, sy: 540, k: 1.85 },
  annulus: { wx: 40, wy: -300, sx: 1180, sy: 540, k: 0.95 },
  choke: { wx: -250, wy: -580, sx: 1120, sy: 540, k: 1.25 },
};

export function build(ctx) {
  const { E, cam, tree, well, ext, T, COL, annot, html } = ctx;
  const { tl, gsap, show, hide, fadeIn, fadeOut, sfx, animate } = E;
  const bt = (b) => T.beat('anatomy.' + b);
  const S1 = SHOT.full;

  /* b1 – open it up: x-ray wipe + dolly into the full shot ------------------------------ */
  cam.go(T.start('anatomy.b1') - 0.2, 1.9, S1, 'power2.inOut');
  ctx.wipe(T.start('anatomy.b1') + 0.1, 1.5);
  sfx(T.start('anatomy.b1') + 0.1, 'scan', 0.8);

  /* b2 – vertical tree, Equinor standard ------------------------------------------------- */
  const p2 = ctx.panel({ at: T.start('anatomy.b2') - 0.1, until: T.start('anatomy.b3') - 0.2, kicker: 'Tree type', title: 'Vertical tree<br><span style="color:var(--warn)">(VXT)</span>', body: 'Valves stacked above the tubing hanger', top: 190 });
  const chip = (txt, col, at, y, icon = '') => {
    const c = H('div', { class: 'abs', style: { left: '96px', top: y + 'px', display: 'flex', alignItems: 'center', gap: '14px', padding: '12px 22px 12px 16px', borderRadius: '14px', background: 'rgba(8,26,42,.88)', border: `1.5px solid ${col}`, font: '700 28px var(--font)', color: '#EEF4F9' } },
      H('span', { style: { width: '14px', height: '14px', borderRadius: '50%', background: col, boxShadow: `0 0 12px ${col}` } }), txt);
    html.append(c);
    show(c, at, 0.5, { x: -20, y: 0 });
    hide(c, T.start('anatomy.b3') - 0.2, 0.4, { x: -16 });
    return c;
  };
  chip('Equinor standard design', '#FFC857', T.word('anatomy.b2', 'standard') - 0.3, 580);
  chip('Johan Castberg', '#2ED0FF', T.word('anatomy.b2', 'Castberg') - 0.3, 654);
  chip('Troll Phase 3', '#34D8A8', T.word('anatomy.b2', 'Troll') - 0.3, 728);
  sfx(T.word('anatomy.b2', 'standard') - 0.3, 'tick', 0.5);

  /* b3 – hydraulic connector ---------------------------------------------------------------- */
  const t3 = T.start('anatomy.b3');
  const S3 = SHOT.conn;
  cam.go(t3 - 0.3, 1.4, S3, 'power3.inOut');
  ctx.ringAt({ shot: S3, tx: -200, ty: 678, r: 60, color: '#FFC857', at: t3 + 0.5, until: T.end('anatomy.b3') + 0.2 });
  ctx.ringAt({ shot: S3, tx: 200, ty: 678, r: 60, color: '#FFC857', at: t3 + 0.5, until: T.end('anatomy.b3') + 0.2 });
  ctx.note({ shot: S3, at: t3 + 0.4, until: T.end('anatomy.b3') + 0.3, tx: -232, ty: 650, dx: -250, dy: -150, label: 'Wellhead connector', sub: 'hydraulic – locks the tree onto the wellhead', color: '#FFC857', size: 28 });
  // clamp arrows (animated, point inward)
  const clamp = S('g', { fill: 'none', stroke: '#FFC857', 'stroke-width': 9, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
  const aL = S('path', { d: 'M0 -26 L26 0 L0 26' }), aR = S('path', { d: 'M0 -26 L-26 0 L0 26' });
  const pL = ctx.P(S3, -232, 678), pR = ctx.P(S3, 232, 678);
  const gL = S('g', { transform: `translate(${pL[0] - 70} ${pL[1]})` }), gR = S('g', { transform: `translate(${pR[0] + 70} ${pR[1]})` });
  const gLi = S('g'), gRi = S('g');
  gL.append(gLi); gR.append(gRi); gLi.append(aL); gRi.append(aR); clamp.append(gL, gR); annot.append(clamp);
  tl.set(clamp, { opacity: 0 }, 0);
  tl.fromTo(clamp, { opacity: 0 }, { opacity: 1, duration: 0.3, immediateRender: false }, t3 + 0.6);
  tl.to(clamp, { opacity: 0, duration: 0.3 }, T.end('anatomy.b3') + 0.1);
  animate(t3 + 0.5, T.end('anatomy.b3') + 0.5, (t) => { const o = 22 * (0.5 + 0.5 * Math.sin((t - t3) * 6)); gLi.setAttribute('transform', `translate(${o.toFixed(1)} 0)`); gRi.setAttribute('transform', `translate(${(-o).toFixed(1)} 0)`); });
  sfx(t3 + 1.3, 'clunk', 0.7);

  /* b4 – tubing hanger ------------------------------------------------------------------------ */
  const t4 = T.start('anatomy.b4');
  const S4 = SHOT.hanger;
  fadeIn(well.root, t4 - 0.4, 0.8);
  cam.go(t4 - 0.3, 1.5, S4, 'power3.inOut');
  ctx.ringAt({ shot: S4, tx: 0, ty: 764, r: 70, color: '#2ED0FF', at: T.word('anatomy.b4', 'hanger') - 0.1, until: T.end('anatomy.b4') + 0.2 });
  ctx.note({ shot: S4, at: T.word('anatomy.b4', 'hanger') - 0.1, until: T.end('anatomy.b4') + 0.3, tx: -172, ty: 764, dx: -260, dy: -120, label: 'Tubing hanger', color: '#2ED0FF', size: 30 });
  // weight arrow along the tubing
  const wp = ctx.P(S4, 0, 880);
  const wArrow = S('g', { fill: 'none', stroke: '#FFC857', 'stroke-width': 10, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
  wArrow.append(S('path', { d: `M${wp[0] + 74} ${wp[1] - 40} V${wp[1] + 160}` }), S('path', { d: `M${wp[0] + 50} ${wp[1] + 126} L${wp[0] + 74} ${wp[1] + 162} L${wp[0] + 98} ${wp[1] + 126}` }));
  annot.append(wArrow);
  tl.set(wArrow, { opacity: 0 }, 0);
  tl.fromTo(wArrow, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: false }, T.word('anatomy.b4', 'weight') - 0.3);
  tl.to(wArrow, { opacity: 0, duration: 0.3 }, T.word('anatomy.b4', 'seals') - 0.2);
  ctx.note({ shot: S4, at: T.word('anatomy.b4', 'weight') - 0.3, until: T.word('anatomy.b4', 'seals') - 0.2, tx: 40, ty: 880, dx: 240, dy: 70, label: 'Carries the weight', sub: 'of the production tubing', color: '#FFC857', size: 26 });
  ctx.ringAt({ shot: S4, tx: -172, ty: 745, r: 26, color: '#FF4F6D', at: T.word('anatomy.b4', 'seals') - 0.1, until: T.end('anatomy.b4') + 0.2 });
  ctx.ringAt({ shot: S4, tx: 172, ty: 745, r: 26, color: '#FF4F6D', at: T.word('anatomy.b4', 'seals') - 0.1, until: T.end('anatomy.b4') + 0.2 });
  ctx.ringAt({ shot: S4, tx: -172, ty: 776, r: 26, color: '#FF4F6D', at: T.word('anatomy.b4', 'seals') - 0.1, until: T.end('anatomy.b4') + 0.2 });
  ctx.ringAt({ shot: S4, tx: 172, ty: 776, r: 26, color: '#FF4F6D', at: T.word('anatomy.b4', 'seals') - 0.1, until: T.end('anatomy.b4') + 0.2 });
  ctx.note({ shot: S4, at: T.word('anatomy.b4', 'seals') - 0.1, until: T.end('anatomy.b4') + 0.3, tx: 172, ty: 776, dx: 150, dy: 110, label: 'Seals the annulus', color: '#FF4F6D', size: 26 });

  /* b5 – two channels ------------------------------------------------------------------------------ */
  const t5 = T.start('anatomy.b5');
  cam.go(t5 - 0.3, 1.5, S1, 'power3.inOut');
  const hl = (x, w, y0, y1, col) => { const r = S('rect', { x: x - w / 2 - 5, y: y0 - 900, width: w + 10, height: y1 - y0, rx: 6, fill: 'none', stroke: col, 'stroke-width': 4, opacity: 0 }); ctx.world.append(r); return r; };
  const hP = hl(0, 52, 52, 806, '#FF9A3C'), hA = hl(150, 30, 48, 806, '#34D8A8');
  tl.fromTo(hP, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: false }, T.word('anatomy.b5', 'channels') - 0.4);
  tl.fromTo(hA, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: false }, T.word('anatomy.b5', 'channels') - 0.1);
  animate(t5, T.end('anatomy.b6') + 1, (t) => { const o = 0.55 + 0.45 * Math.sin(t * 5); hP.style.strokeOpacity = o.toFixed(2); hA.style.strokeOpacity = o.toFixed(2); });
  tl.to(hA, { opacity: 0, duration: 0.5 }, T.start('anatomy.b6') + 0.5);

  /* b6 – production bore ------------------------------------------------------------------------------ */
  const t6 = T.start('anatomy.b6');
  ['p_low', 'p_mid', 'p_tee'].forEach((n, i) => tree.fills[n].to(t6 + 0.1 + i * 0.25, 0.7, 0.5));
  tree.fills.p_br1.to(t6 + 0.5, 0.6, 0.5);
  tree.flows.p_low.show(t6 + 0.2, 0.5, 70);
  tree.flows.p_mid.show(t6 + 0.9, 0.5, 70);
  ctx.note({ shot: S1, at: t6 + 0.3, until: T.end('anatomy.b6') + 0.4, tx: 0, ty: 600, dx: -330, dy: 20, label: 'Production bore', sub: 'well fluids', color: '#FF9A3C', size: 28 });
  tl.to(hP, { opacity: 0, duration: 0.5 }, T.end('anatomy.b6') + 0.2);

  /* b7 – annulus bore --------------------------------------------------------------------------------------- */
  const t7 = T.start('anatomy.b7');
  const S7 = SHOT.annulus;
  cam.go(t7 - 0.3, 1.6, S7, 'power3.inOut');
  tl.to(well.fills.annulus.els, { opacity: 0.42, duration: 0.8 }, t7 + 0.2);
  ['a_mid', 'a_low'].forEach((n, i) => tree.fills[n].to(t7 + 0.2 + i * 0.2, 0.7, 0.45));
  tree.flows.a_low.show(t7 + 0.5, 0.5, 40); tree.flows.a_mid.show(t7 + 0.5, 0.5, 40);
  ctx.note({ shot: S7, at: t7 + 0.1, until: T.end('anatomy.b7') + 0.4, tx: 150, ty: 420, dx: 220, dy: -40, label: 'Annulus bore', color: '#34D8A8', size: 28 });
  ctx.note({ shot: S7, at: T.word('anatomy.b7', 'space') - 0.2, until: T.end('anatomy.b7') + 0.4, wx: 105, wy: 60, dx: 330, dy: 70, label: 'Annulus', sub: 'between tubing and casing', color: '#34D8A8', size: 28 });
  ctx.note({ shot: S7, at: T.word('anatomy.b7', 'tubing') - 0.2, until: T.end('anatomy.b7') + 0.4, wx: -33, wy: 90, dx: -260, dy: 60, label: 'Tubing', color: '#B3C4D2', size: 26 });
  ctx.note({ shot: S7, at: T.word('anatomy.b7', 'casing') - 0.2, until: T.end('anatomy.b7') + 0.4, wx: 178, wy: 110, dx: 230, dy: -120, label: 'Production casing', color: '#B3C4D2', size: 26 });

  /* b8 – valves on each bore ------------------------------------------------------------------------------------ */
  const t8 = T.start('anatomy.b8');
  cam.go(t8 - 0.3, 1.6, S1, 'power3.inOut');
  tl.to(well.fills.annulus.els, { opacity: 0.16, duration: 0.6 }, t8);
  const grp = [
    { w: 'master', col: '#FFC857', label: 'Master valves', pts: [[0, 500], [150, 500]], note: { tx: 0, ty: 500, dx: -420, dy: 120 } },
    { w: 'wing', col: '#2ED0FF', label: 'Wing valves', pts: [[-230, 320], [400, 320]], note: { tx: 400, ty: 320, dx: 70, dy: -150 } },
    { w: 'swab', col: '#BC8FFF', label: 'Swab valves', pts: [[0, 110], [150, 110]], note: { tx: 0, ty: 110, dx: -440, dy: -20 } },
  ];
  grp.forEach((g) => {
    const ta = T.word('anatomy.b8', g.w) - 0.2;
    g.pts.forEach(([tx, ty]) => ctx.ringAt({ shot: S1, tx, ty, r: 50, color: g.col, at: ta, until: T.end('anatomy.b8') + 0.3 }));
    ctx.note({ shot: S1, at: ta, until: T.end('anatomy.b8') + 0.4, label: g.label, color: g.col, size: 28, ...g.note });
    sfx(ta, 'tick', 0.6);
  });

  /* b9 – wing leads through the choke ---------------------------------------------------------------------------------- */
  const t9 = T.start('anatomy.b9');
  const S9 = SHOT.choke;
  cam.go(t9 - 0.3, 1.4, S9, 'power3.inOut');
  tree.fills.p_out1.to(t9 + 0.1, 0.6, 0.5); tree.fills.p_out2.to(t9 + 0.3, 0.6, 0.5); tree.fills.p_br2.to(t9, 0.5, 0.5);
  tree.flows.p_out1.show(t9 + 0.3, 0.5, 80); tree.flows.p_out2.show(t9 + 0.9, 0.5, 80);
  ctx.note({ shot: S9, at: T.word('anatomy.b9', 'choke') - 0.2, until: T.end('anatomy.b9') + 0.5, tx: -400, ty: 200, dx: 40, dy: -150, label: 'Choke', color: '#FFC857', size: 30, anchor: 'b' });
  ctx.note({ shot: S9, at: T.word('anatomy.b9', 'flowline') - 0.2, until: T.end('anatomy.b9') + 0.5, tx: -580, ty: 320, dx: 40, dy: 130, label: 'Flowline connector', sub: 'to the manifold', color: '#FF9A3C', size: 26 });
}
