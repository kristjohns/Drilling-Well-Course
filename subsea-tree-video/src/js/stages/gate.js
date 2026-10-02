// Scene 6 – The fail-safe valve (180 – 230 s) ---------------------------------------------
import { H, S } from '../lib/svg.js';
import { tag, leader } from '../lib/annot.js';
import { gauge, banner } from '../lib/ui.js';

export const SHOT2 = {
  pmv: { wx: -90, wy: -400, sx: 1110, sy: 560, k: 2.6 },
};

export function build(ctx) {
  const { E, cam, tree, T, COL, annot, html } = ctx;
  const { tl, gsap, show, hide, fadeIn, fadeOut, sfx, animate, Flow } = E;
  const V = tree.valves.PMV;
  const SH = SHOT2.pmv;
  const P = (tx, ty) => ctx.P(SH, tx, ty);
  const tG = T.scene('gate').start;
  const b = (id) => T.beat('gate.' + id);

  /* ---- flow helpers: everything downstream of the PMV ------------------------------------ */
  const downFlows = [tree.flows.p_mid, tree.flows.p_out1, tree.flows.p_out2];
  const downFills = ['p_mid', 'p_tee', 'p_br1', 'p_br2', 'p_out1', 'p_out2'];
  let flowing = true;
  const flowOn = (t) => {
    if (flowing) return; flowing = true;
    tree.flows.p_low.speed(t, 70, 0.5);
    downFlows.forEach((f, i) => f.show(t + 0.1 * i, 0.4, 70));
    downFills.forEach((n) => tree.fills[n].to(t, 0.5, 0.5));
  };
  const flowOff = (t) => {
    if (!flowing) return; flowing = false;
    tree.flows.p_low.speed(t, 0, 0.35);
    downFlows.forEach((f, i) => f.hide(t + 0.05 + 0.15 * i, 0.5));
    downFills.forEach((n) => tree.fills[n].to(t + 0.1, 0.6, 0.28));
  };
  // PMV states as a list so the LED tag can follow it
  const states = [{ t: tG - 1, open: true }];
  const op = (t, open, d, ease) => {
    if (open) V.open(t, d, ease); else V.close(t, d, ease);
    states.push({ t: t + (open ? d * 0.55 : d * 0.5), open });
    if (open) flowOn(t + d * 0.7); else flowOff(t + d * 0.3);
  };

  /* ---- b1: dive into the valve ------------------------------------------------------------ */
  cam.go(tG - 0.1, 2.5, SH, 'power3.inOut');
  const p1 = ctx.panel({ at: b('b1').start + 1.2, until: b('b2').start - 0.1, kicker: 'Inside a tree valve', title: 'Hydraulic<br>gate valve', body: 'Used for the master, wing and swab valves', top: 190, width: 460 });

  /* ---- b2: gate, hole, seats ------------------------------------------------------------ */
  const t2 = b('b2').start;
  op(t2 + 0.1, false, 0.7, 'power2.inOut');                 // show the gate in the closed position
  ctx.note({ shot: SH, at: T.word('gate.b2', 'gate') + 0.1, until: b('b3').start - 0.2, tx: 0, ty: 500, dx: 130, dy: -215, label: 'Gate', sub: 'flat steel plate', color: '#EEF4F9', size: 30 });
  ctx.note({ shot: SH, at: T.word('gate.b2', 'hole') - 0.2, until: b('b3').start - 0.2, tx: -65, ty: 500, dx: -110, dy: 190, label: 'Hole', color: '#2ED0FF', size: 30 });
  ctx.note({ shot: SH, at: T.word('gate.b2', 'seats') - 0.2, until: b('b3').start - 0.2, tx: 30, ty: 513, dx: 190, dy: 200, label: 'Metal seats', color: '#FFC857', size: 30 });
  ctx.ringAt({ shot: SH, tx: -30, ty: 487, r: 28, color: '#FFC857', at: T.word('gate.b2', 'seats') - 0.1, until: b('b3').start - 0.2 });
  ctx.ringAt({ shot: SH, tx: 30, ty: 513, r: 28, color: '#FFC857', at: T.word('gate.b2', 'seats') - 0.1, until: b('b3').start - 0.2 });

  /* ---- b3: align the hole -> flow ----------------------------------------------------------- */
  const t3 = b('b3').start;
  op(t3 + 0.2, true, 2.0, 'power2.inOut');
  sfx(t3 + 0.3, 'slide', 0.6);

  /* ---- b4: slide across -> blocked ------------------------------------------------------------- */
  const t4 = b('b4').start;
  op(T.word('gate.b4', 'across') - 0.1, false, 1.2, 'power2.inOut');
  sfx(T.word('gate.b4', 'across') - 0.1, 'slide', 0.6);
  ctx.note({ shot: SH, at: T.word('gate.b4', 'solid') - 0.1, until: b('b5').start - 0.1, tx: 0, ty: 500, dx: 130, dy: -215, label: 'Solid steel blocks the flow', color: '#FF3B5C', size: 28 });

  /* ---- b5: hydraulic actuator ----------------------------------------------------------------- */
  const t5 = b('b5').start;
  const portTL = [-255.3, 446.9];
  const hoseD = `M-398 425 H-255 V450`;
  const hose = S('g');
  hose.append(S('path', { d: hoseD, fill: 'none', stroke: '#0B141C', 'stroke-width': 11, 'stroke-linejoin': 'round' }), S('path', { d: hoseD, fill: 'none', stroke: '#1C6E8C', 'stroke-width': 6, 'stroke-linejoin': 'round' }));
  tree.root.append(hose);
  tl.fromTo(hose, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: true }, T.word('gate.b5', 'hydraulic') - 0.2);
  const hf = Flow(tree.root, hoseD, { color: '#2ED0FF', w: 5, gap: 16 });
  hf.show(T.word('gate.b5', 'Fluid') - 0.2, 0.4, 0);
  hf.speed(T.word('gate.b5', 'Fluid') - 0.2, 0, 0.01);
  // supply gauge on the left, connected to the hose
  const gg = gauge(annot, { x: 250, y: 400, r: 70, max: 250, label: 'ACTUATOR PRESSURE', color: '#2ED0FF' });
  show(gg.g, T.word('gate.b5', 'hydraulic') - 0.3, 0.6, { x: -20, y: 0 });
  const gLink = S('path', { d: `M${320} ${P(-398, 425)[1]} H${P(-398, 425)[0]}`, stroke: '#1C6E8C', 'stroke-width': 8, fill: 'none', 'stroke-linecap': 'round' });
  annot.append(gLink);
  tl.fromTo(gLink, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: true }, T.word('gate.b5', 'hydraulic') - 0.2);
  gg.to(T.word('gate.b5', 'Fluid') - 0.1, 1.4, 207, 'power2.out');
  hf.speed(T.word('gate.b5', 'Fluid') - 0.1, 90, 0.8);
  ctx.note({ shot: SH, at: T.word('gate.b5', 'actuator') - 0.3, until: T.word('gate.b5', 'Fluid') - 0.1, tx: -200, ty: 462, dx: -60, dy: -230, label: 'Hydraulic actuator', color: '#2ED0FF', size: 30 });
  op(T.word('gate.b5', 'Fluid') + 0.1, true, 2.6, 'power2.inOut');
  ctx.note({ shot: SH, at: T.word('gate.b5', 'piston') - 0.2, until: T.word('gate.b5', 'spring') + 1.0, tx: -174, ty: 470, dx: -90, dy: -190, label: 'Piston', color: '#EEF4F9', size: 28 });
  ctx.note({ shot: SH, at: T.word('gate.b5', 'spring') - 0.3, until: T.word('gate.b5', 'spring') + 1.0, tx: -150, ty: 520, dx: -40, dy: 190, label: 'Spring', sub: 'compressed', color: '#FFC857', size: 28 });
  ctx.note({ shot: SH, at: T.word('gate.b5', 'Fluid') + 0.3, until: T.word('gate.b5', 'spring') + 1.0, tx: portTL[0], ty: portTL[1] - 10, dx: -110, dy: -70, label: 'Hydraulic port', color: '#2ED0FF', size: 26 });
  sfx(T.word('gate.b5', 'Fluid') + 0.1, 'hiss', 0.7);

  /* ---- b6: pressure holds it open ... take it away ---------------------------------------------- */
  const t6 = b('b6').start;
  const bn1 = banner(html, { text: 'PRESSURE <span style="color:#2ED0FF">ON</span> = VALVE <span style="color:#3BDB86">OPEN</span>', color: '#EEF4F9', top: 118, size: 50 });
  const bn2 = banner(html, { text: 'PRESSURE <span style="color:#FF3B5C">OFF</span> = VALVE <span style="color:#FF3B5C">CLOSED</span>', color: '#FF3B5C', top: 118, size: 50 });
  show(bn1, T.word('gate.b6', 'Hydraulic') - 0.2, 0.5, { y: -20 });
  hide(bn1, T.word('gate.b6', 'Take') - 0.1, 0.35);
  show(bn2, T.word('gate.b6', 'pressure', 1) - 0.2, 0.5, { y: -20 });
  hide(bn2, b('b7').start - 0.1, 0.4);
  const tDrop = T.word('gate.b6', 'Take');
  gg.to(tDrop + 0.1, 2.5, 0, 'power1.in');
  hf.speed(tDrop + 0.2, 0, 1.6);
  tl.to(hf.g, { opacity: 0, duration: 0.5 }, tDrop + 2.6);
  ctx.ringAt({ shot: SH, tx: -150, ty: 500, r: 70, color: '#FFC857', at: T.word('gate.b6', 'spring') - 0.1, until: T.word('gate.b6', 'shut') + 0.8 });
  op(T.word('gate.b6', 'spring') + 0.15, false, 0.95, 'power3.in');
  sfx(T.word('gate.b6', 'gate') - 0.1, 'clunk', 0.9);

  /* ---- b7: fail-safe closed ---------------------------------------------------------------------- */
  const bn3 = banner(html, { text: '<span style="color:#FFC857">FAIL-SAFE</span> CLOSED', color: '#FFC857', top: 118, size: 64 });
  show(bn3, T.word('gate.b7', 'fail-safe') - 0.2, 0.5, { y: -20, scale: 0.9 });
  hide(bn3, b('b8').start - 0.1, 0.4);
  sfx(T.word('gate.b7', 'fail-safe') - 0.1, 'chime', 0.7);

  /* ---- b8: lose the signal / supply / everything ---------------------------------------------------- */
  const icoSig = '<svg viewBox="-40 -40 80 80" width="54" height="54"><g fill="none" stroke="#EEF4F9" stroke-width="6" stroke-linecap="round"><path d="M-26 -8 A36 36 0 0 1 26 -8"/><path d="M-15 6 A20 20 0 0 1 15 6"/><circle cx="0" cy="22" r="4" fill="#EEF4F9"/></g></svg>';
  const icoHose = '<svg viewBox="-40 -40 80 80" width="54" height="54"><g fill="none" stroke="#2ED0FF" stroke-width="7" stroke-linecap="round"><path d="M-34 14 C-14 14 -14 -14 6 -14 H34"/><path d="M-34 4 V24 M34 -24 V-4"/></g></svg>';
  const icoAll = '<svg viewBox="-40 -40 80 80" width="54" height="54"><g fill="none" stroke="#FFC857" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 -34 L-16 4 H0 L-6 34 L18 -8 H2 Z"/></g></svg>';
  const tiles = [
    { ico: icoSig, text: 'Signal lost', w: 'signal', wClosed: 0, x: 420 },
    { ico: icoHose, text: 'Hydraulic supply lost', w: 'hydraulic', wClosed: 1, x: 780 },
    { ico: icoAll, text: 'Everything lost', w: 'everything', wClosed: 2, x: 1310 },
  ];
  const B8 = b('b8');
  const closedTimes = [T.word('gate.b8', 'Closed', 0), T.word('gate.b8', 'Closed', 1), T.word('gate.b8', 'closed', 2)];
  // NOTE: "Closed."(1) "Closed."(2) "closed."(Still closed)
  tiles.forEach((tl_, i) => {
    const wrap = H('div', { class: 'abs', style: { left: tl_.x + 'px', top: '110px', display: 'flex', alignItems: 'center', gap: '16px', padding: '14px 26px 14px 20px', borderRadius: '16px', background: 'rgba(5,16,26,.9)', border: '2px solid rgba(170,200,225,.35)', font: '700 30px var(--font)', color: '#EEF4F9' } },
      H('span', { html: tl_.ico, style: { display: 'block', lineHeight: 0 } }), tl_.text);
    const x = H('div', { class: 'abs', style: { left: tl_.x + 'px', top: '110px', width: '100%', height: '0' } });
    html.append(wrap);
    const startT = T.word('gate.b8', tl_.w) - 0.35;
    show(wrap, startT, 0.45, { y: -16 });
    const cT = closedTimes[i];
    tl.to(wrap, { borderColor: '#FF3B5C', boxShadow: '0 0 30px rgba(255,59,92,.45)', duration: 0.2 }, cT);
    // reopen before each phrase, slam shut on "Closed"
    const reopenT = Math.max(i === 0 ? B8.start - 0.25 : closedTimes[i - 1] + 0.7, cT - 1.45);
    const dOpen = Math.min(1.2, cT - reopenT - 0.15);
    gg.to(reopenT, dOpen * 0.8, 207, 'power2.out');
    hf.show(reopenT, 0.3, 90);
    op(reopenT, true, dOpen, 'power2.inOut');
    gg.to(cT - 0.04, 0.45, 0, 'power3.in');
    hf.speed(cT - 0.02, 0, 0.3);
    hf.hide(cT + 0.4, 0.4);
    op(cT - 0.02, false, 0.45, 'power3.in');
    sfx(cT - 0.02, 'clunk', 0.85);
    hide(wrap, b('b9').start - 0.1, 0.4);
    if (i === 2) tl.set(wrap, { autoAlpha: 0 }, b('b9').end + 1);
  });

  /* ---- b9: safe by default ------------------------------------------------------------------------------ */
  const bn9 = banner(html, { text: 'Default state = <span style="color:#3BDB86">SAFE</span>', color: '#3BDB86', top: 118, size: 58 });
  show(bn9, b('b9').start - 0.05, 0.5, { y: -20 });
  hide(bn9, b('b9').end + 0.2, 0.5);
  sfx(b('b9').start + 0.2, 'chime', 0.6);

  // LED status tag for the PMV follows the valve states
  // (rebuilt here so it can use the full list of state changes)
  ctx.status({ name: 'PMV', shot: SH, tx: 0, ty: 500, dx: 0, dy: -300, at: t2 + 0.2, until: b('b9').end + 0.4, states: [{ t: 0, open: false }, ...states.filter((s_) => s_.t > t2 + 0.3)] });
  // clean up the demonstration hardware at the end of the scene
  const tOut = b('b9').end + 0.2;
  hide(gg.g, tOut, 0.5);
  tl.to(gLink, { opacity: 0, duration: 0.4 }, tOut);
  tl.to(hose, { opacity: 0, duration: 0.4 }, tOut);
  hf.hide(tOut, 0.4);
  ctx.gateStates = states;
  ctx.pmvOps = { op, flowOn, flowOff };
}
