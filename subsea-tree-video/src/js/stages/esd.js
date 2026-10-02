// Scene 18 – Start-up and emergency shutdown (445 – 495 s) --------------------------------------
// The tree stage is re-used (hidden during control + barriers, reset while hidden).
// Left column: sequence lists with live valve-status pills; bottom-left: DHSV inset.
import { H, S, rng } from '../lib/svg.js';
import { buildDHSV } from '../art/well.js';

export const ESHOT = { wx: -20, wy: -470, sx: 1230, sy: 540, k: 0.86 };
const GRN = '#3BDB86', RED = '#FF3B5C', CY = '#2ED0FF', YEL = '#FFC857', OR = '#FF9A3C';
const STC = { closed: RED, open: GRN, opening: YEL, closing: YEL };

export function build(ctx) {
  const { E, cam, tree, well, T, annot, html, world } = ctx;
  const { tl, gsap, show, hide, fadeOut, sfx, animate, Flow } = E;
  const w = (id, word, n = 0) => T.word('esd.' + id, word, n);
  const bt = (id) => T.beat('esd.' + id);
  const V = tree.valves;
  const SH = ESHOT;
  const P = (tx, ty) => ctx.P(SH, tx, ty);
  const t0 = T.scene('esd').start;

  /* ---------------- reset the tree stage while it is hidden (barriers scene is on screen) ---------------- */
  const tR = t0 - 0.9;
  cam.cut(tR, SH);
  fadeOut(well.root, tR, 0.05);
  fadeOut(tree.overlays.scm.g, tR, 0.05); fadeOut(tree.overlays.dhsvLine.g, tR, 0.05);
  V.PMV.close(tR, 0.05, 'none'); V.PWV.close(tR, 0.05, 'none');
  tree.choke.to(tR, 0.05, 0.0);
  ['p_low', 'p_mid', 'p_tee', 'p_br1', 'p_br2', 'p_out1', 'p_out2'].forEach((n) => tree.fills[n].to(tR, 0.05, 0.0));
  tree.fills.a_low.to(tR, 0.05, 0.0); tree.fills.a_mid.to(tR, 0.05, 0.0);
  [tree.flows.p_low, tree.flows.p_mid, tree.flows.p_out1, tree.flows.p_out2].forEach((f) => { f.speed(tR, 0, 0.05); f.hide(tR, 0.05); });
  tree.flows.a_low.hide(tR, 0.05); tree.flows.a_mid.hide(tR, 0.05);

  /* ---------------- helpers ---------------- */
  /** a glowing dot that flies along a curve from a to b (position = pure function of t) */
  const fly = (a, b, t, d = 0.8, col = '#FFFFFF', bend = 0.18) => {
    const g = S('g', { opacity: 0 }, S('circle', { r: 17, fill: col, opacity: 0.25 }), S('circle', { r: 7.5, fill: col }));
    annot.append(g);
    const mx = (a[0] + b[0]) / 2 + (b[1] - a[1]) * bend, my = (a[1] + b[1]) / 2 - (b[0] - a[0]) * bend;
    tl.fromTo(g, { opacity: 0 }, { opacity: 1, duration: 0.12, immediateRender: false }, t);
    tl.to(g, { opacity: 0, duration: 0.15 }, t + d - 0.12);
    animate(t - 0.05, t + d + 0.05, (tt) => {
      const u = Math.min(1, Math.max(0, (tt - t) / d)), e = u * u * (3 - 2 * u), v = 1 - e;
      g.setAttribute('transform', `translate(${(v * v * a[0] + 2 * v * e * mx + e * e * b[0]).toFixed(1)} ${(v * v * a[1] + 2 * v * e * my + e * e * b[1]).toFixed(1)})`);
    });
  };

  /** list row with badge, name, sub-text and a live status pill */
  const mkRow = ({ n, name, sub, col, top, st0, badgeQ = false, showSub = true }) => {
    const bQ = H('div', { style: { position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', opacity: badgeQ ? 1 : 0 }, text: '?' });
    const bN = H('div', { style: { position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', opacity: badgeQ ? 0 : 1 }, text: String(n) });
    const badge = H('div', { style: { position: 'relative', width: '44px', height: '44px', borderRadius: '50%', background: badgeQ ? YEL : col, flex: 'none', color: '#06121C', font: '800 24px var(--mono)' } }, bQ, bN);
    const dot = H('div', { style: { position: 'absolute', left: '0', top: '8px', width: '14px', height: '14px', borderRadius: '50%', background: STC[st0], boxShadow: `0 0 10px ${STC[st0]}` } });
    const lab = (txt, c, on) => H('div', { style: { position: 'absolute', left: '26px', top: '2px', font: '700 20px/26px var(--mono)', color: c, opacity: on ? 1 : 0, whiteSpace: 'nowrap' }, text: txt });
    const sts = { closed: lab('CLOSED', RED, st0 === 'closed'), open: lab('OPEN', GRN, st0 === 'open'), opening: lab('OPENING', YEL, false), closing: lab('CLOSING', YEL, false) };
    const pill = H('div', { style: { position: 'relative', width: '126px', height: '30px', flex: 'none', marginLeft: 'auto' } }, dot, ...Object.values(sts));
    const subEl = H('div', { style: { font: '500 19px var(--font)', color: '#AFC0CE', opacity: showSub ? 1 : 0, whiteSpace: 'nowrap' }, text: sub });
    const row = H('div', { style: { position: 'absolute', left: '0', top: top + 'px', width: '470px', height: '80px', display: 'flex', alignItems: 'center', gap: '14px', padding: '0 16px', borderRadius: '16px', background: 'rgba(8,26,42,.9)', border: '2px solid rgba(170,200,225,.24)', boxSizing: 'border-box' } },
      badge, H('div', { style: { display: 'flex', flexDirection: 'column', gap: '2px', minWidth: '0' } }, H('div', { style: { font: '700 25px var(--mono)', color: '#EEF4F9' }, text: name }), subEl), pill);
    const api = {
      el: row, y: top,
      state(t, st) {
        const c = STC[st];
        tl.to(dot, { backgroundColor: c, boxShadow: `0 0 10px ${c}`, duration: 0.15 }, t);
        Object.entries(sts).forEach(([k, e]) => tl.to(e, { opacity: st === k ? 1 : 0, duration: 0.12 }, t));
      },
      light(t, c) { tl.to(row, { borderColor: c, autoAlpha: 1, duration: 0.3 }, t); },
      reveal(t, c, txt) {
        tl.to(bQ, { opacity: 0, duration: 0.15 }, t); tl.to(bN, { opacity: 1, duration: 0.15 }, t);
        tl.to(badge, { backgroundColor: c, duration: 0.2 }, t);
        if (txt) tl.to(subEl, { opacity: 1, duration: 0.3 }, t);
      },
      moveTo(t, d, ytop) { tl.to(row, { y: ytop - top, duration: d, ease: 'power3.inOut' }, t); },
    };
    return api;
  };
  /** list container with a kicker header (several kicker texts can cross-fade) */
  const mkList = ({ kickers, rows, at, until, top = 168 }) => {
    const wrap = H('div', { class: 'abs', style: { left: '96px', top: top + 'px', width: '470px', height: '460px' } });
    const ks = kickers.map((k, i) => H('div', { class: 'kicker', style: { position: 'absolute', left: '0', top: '0', color: k.col, opacity: i ? 0 : 1, whiteSpace: 'nowrap' }, text: k.text }));
    const body = H('div', { style: { position: 'absolute', left: '0', top: '58px', width: '470px' } });
    wrap.append(...ks, body);
    rows.forEach((r) => body.append(r.el));
    html.append(wrap);
    show(wrap, at, 0.6, { x: -26, y: 0 });
    hide(wrap, until, 0.5, { x: -20 });
    return { wrap, kick: (t, i) => ks.forEach((k, j) => tl.to(k, { opacity: i === j ? 1 : 0, duration: 0.25 }, t)) };
  };
  const ROW_P = 92;

  /* ---------------- b1: agenda chips ---------------- */
  const chipsW = H('div', { class: 'abs', style: { left: '96px', top: '200px', width: '470px' } });
  const mkChip = (n, txt, col) => H('div', { style: { display: 'flex', alignItems: 'center', gap: '14px', padding: '14px 18px', marginBottom: '14px', borderRadius: '16px', background: 'rgba(8,26,42,.9)', border: `2px solid ${col}` } },
    H('div', { style: { width: '44px', height: '44px', borderRadius: '50%', display: 'grid', placeItems: 'center', background: col, color: '#06121C', font: '800 24px var(--mono)', flex: 'none' }, text: n }),
    H('div', { style: { font: '700 28px var(--font)', color: '#EEF4F9' }, text: txt }));
  const ch1 = mkChip('1', 'Start-up', CY), ch2 = mkChip('2', 'Emergency shutdown', RED);
  chipsW.append(ch1, ch2);
  html.append(chipsW);
  show(ch1, w('b1', 'start') - 0.2, 0.5, { x: -24, y: 0 });
  show(ch2, w('b1', 'emergency') - 0.2, 0.5, { x: -24, y: 0 });
  hide(chipsW, bt('b2').start - 0.1, 0.4, { x: -20 });

  /* ---------------- DHSV inset (bottom-left) ---------------- */
  const insW = S('g', { transform: 'translate(96 636)' });
  const ins = S('g');
  insW.append(ins);
  annot.append(insW);
  ins.append(S('rect', { width: 430, height: 304, rx: 20, fill: 'rgba(5,16,26,.92)', stroke: 'rgba(170,200,225,.32)', 'stroke-width': 1.8 }),
    S('text', { x: 22, y: 38, fill: '#FF9AAB', 'font-size': 17, 'font-weight': 800, 'letter-spacing': '0.12em', text: 'DOWNHOLE SAFETY VALVE' }));
  const dG = S('g', { transform: 'translate(140 192) scale(0.74)' });
  ins.append(dG);
  const dh = buildDHSV(dG, { x: 0, y: 0 });
  const fLow = Flow(dG, 'M0 150 V80', { color: OR, w: 9, gap: 24 });
  const fHigh = Flow(dG, 'M0 66 V-146', { color: OR, w: 9, gap: 24 });
  // big state read-out (right)
  const mono = { fontFamily: 'var(--mono)' };
  const dLedG = S('circle', { cx: 262, cy: 132, r: 11, fill: RED });
  const dTxtC = S('text', { x: 284, y: 141, fill: RED, 'font-size': 28, 'font-weight': 800, style: mono, text: 'CLOSED' });
  const dTxtO = S('text', { x: 284, y: 141, fill: GRN, 'font-size': 28, 'font-weight': 800, style: mono, text: 'OPEN', opacity: 0 });
  const mkSub = (l1, l2, op) => S('g', { opacity: op, fill: '#AFC0CE', 'font-size': 17, 'font-weight': 500 }, S('text', { x: 250, y: 176, text: l1 }), S('text', { x: 250, y: 198, text: l2 }));
  const dSubC = mkSub('closed by', 'its spring', 1), dSubO = mkSub('held open by', 'hydraulic pressure', 0);
  ins.append(dLedG, dTxtC, dTxtO, dSubC, dSubO);
  dh.set(0);
  const dState = (t, open) => {
    tl.to(dLedG, { attr: { fill: open ? GRN : RED }, duration: 0.1 }, t);
    tl.to(dTxtO, { opacity: open ? 1 : 0, duration: 0.1 }, t); tl.to(dTxtC, { opacity: open ? 0 : 1, duration: 0.1 }, t);
    tl.to(dSubO, { opacity: open ? 1 : 0, duration: 0.1 }, t); tl.to(dSubC, { opacity: open ? 0 : 1, duration: 0.1 }, t);
  };
  show(ins, w('b2', 'downhole') - 0.6, 0.7, { y: 40 });

  /* ---------------- start-up (b2 / b3) ---------------- */
  const upRows = [
    mkRow({ n: 1, name: 'DHSV', sub: 'open first', col: CY, top: 0 * ROW_P, st0: 'closed' }),
    mkRow({ n: 2, name: 'PMV', sub: 'master valve', col: CY, top: 1 * ROW_P, st0: 'closed' }),
    mkRow({ n: 3, name: 'PWV', sub: 'wing valve', col: CY, top: 2 * ROW_P, st0: 'closed' }),
    mkRow({ n: 4, name: 'CHOKE', sub: 'open gradually', col: CY, top: 3 * ROW_P, st0: 'closed' }),
  ];
  upRows.forEach((r) => gsap.set(r.el, { autoAlpha: 0.38 }));
  const upList = mkList({ kickers: [{ text: 'Start-up sequence', col: CY }, { text: '● Well flowing', col: GRN }], rows: upRows, at: bt('b2').start - 0.05, until: bt('b4').start + 0.2 });
  const rowR = (i) => [96 + 470, 168 + 58 + i * ROW_P + 40];
  const flowsArr = [tree.flows.p_low, tree.flows.p_mid, tree.flows.p_out1, tree.flows.p_out2];
  const pMV = P(0, 500), pWV = P(-230, 320), pCK = P(-400, 320);
  const vtag = (p, text, at, until, dx = 0, dy = 100) => ctx.tagAt({ x: p[0] + dx, y: p[1] + dy, text, color: CY, mono: true, size: 24, anchor: 'c', at, until });
  const tUpEnd = bt('b4').start + 0.2;

  // 1 DHSV
  const tD = w('b2', 'downhole');
  upRows[0].light(tD - 0.1, CY); fly(rowR(0), [526, 770], tD - 0.1, 0.8, CY);
  upRows[0].state(tD + 0.55, 'opening'); upRows[0].state(tD + 2.0, 'open');
  dh.open(tD + 0.6, 1.5); dState(tD + 1.5, true); sfx(tD + 0.7, 'slide', 0.5);
  fLow.show(tD + 1.3, 0.3, 0);
  tree.fills.p_low.to(tD + 1.0, 0.6, 0.5);
  // 2 PMV
  const tM = w('b2', 'master');
  upRows[1].light(tM - 0.1, CY); fly(rowR(1), [P(-70, 500)[0], pMV[1]], tM - 0.1, 0.8, CY);
  upRows[1].state(tM + 0.65, 'opening'); upRows[1].state(tM + 1.9, 'open');
  V.PMV.open(tM + 0.6, 1.2, 'power2.inOut'); sfx(tM + 0.6, 'slide', 0.5);
  ['p_mid', 'p_tee', 'p_br1'].forEach((n, i) => tree.fills[n].to(tM + 1.4 + i * 0.1, 0.6, 0.5));
  ctx.ringAt({ shot: SH, tx: -60, ty: 500, r: 70, color: CY, at: tM + 0.3, until: tM + 2.2 });
  vtag(pMV, 'PMV', tM + 0.3, tM + 2.0, -52, 100);
  // 3 PWV
  const tW = w('b2', 'wing');
  upRows[2].light(tW - 0.1, CY); fly(rowR(2), pWV, tW - 0.1, 0.8, CY);
  upRows[2].state(tW + 0.65, 'opening'); upRows[2].state(tW + 1.9, 'open');
  V.PWV.open(tW + 0.6, 1.2, 'power2.inOut'); sfx(tW + 0.6, 'slide', 0.5);
  ['p_br2', 'p_out1'].forEach((n, i) => tree.fills[n].to(tW + 1.4 + i * 0.1, 0.6, 0.5));
  ctx.ringAt({ shot: SH, tx: -230, ty: 320, r: 66, color: CY, at: tW + 0.3, until: tW + 2.2 });
  vtag(pWV, 'PWV', tW + 0.3, tW + 2.0, 0, 115);
  // 4 choke, gradually
  const tCh = w('b3', 'choke');
  upRows[3].light(tCh - 0.1, CY); fly(rowR(3), pCK, tCh - 0.1, 0.8, CY);
  upRows[3].state(tCh + 0.5, 'opening'); upRows[3].state(tCh + 3.3, 'open');
  tree.choke.to(tCh + 0.6, 2.6, 0.55, 'power1.inOut');
  ctx.ringAt({ shot: SH, tx: -400, ty: 320, r: 66, color: CY, at: tCh + 0.3, until: tCh + 3.2 });
  vtag(pCK, 'CHOKE', tCh + 0.3, tCh + 3.4, 0, 115);
  tree.fills.p_out2.to(tCh + 1.4, 0.6, 0.5);
  const tF = tCh + 1.5;                       // flow starts as the choke opens
  [[tree.flows.p_low, 0], [tree.flows.p_mid, 0.1], [tree.flows.p_out1, 0.2], [tree.flows.p_out2, 0.3]].forEach(([f, dl]) => { f.show(tF + dl, 0.5); f.speed(tF + dl, 72, 2.2); });
  fLow.speed(tF, 72, 2.2); fHigh.show(tF + 0.2, 0.4); fHigh.speed(tF + 0.2, 72, 2.2);
  upList.kick(w('b3', 'flow') - 0.1, 1);
  sfx(w('b3', 'flow'), 'chime', 0.6);

  /* ---------------- ESD trigger (b4) ---------------- */
  const tW4 = w('b4', 'wrong');
  const vign = H('div', { class: 'abs', style: { inset: '0', background: 'radial-gradient(ellipse at 50% 50%, rgba(255,40,70,0) 45%, rgba(255,40,70,.42) 100%)', opacity: 0, pointerEvents: 'none' } });
  html.append(vign);
  tl.fromTo(vign, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: true }, tW4);
  animate(tW4 + 0.4, bt('b6').start + 3, (t) => { vign.style.opacity = (0.55 + 0.45 * Math.sin((t - tW4) * 7)).toFixed(2); });
  tl.to(vign, { opacity: 0, duration: 0.8 }, w('b7', 'master') + 1.0);
  // host card (left column) + ESD banner (top)
  const tri = S('svg', { viewBox: '-30 -30 60 60', width: 56, height: 56, style: { flex: 'none', overflow: 'visible' } },
    S('path', { d: 'M0 -24 L24 20 H-24 Z', fill: RED, stroke: '#2A0610', 'stroke-width': 3, 'stroke-linejoin': 'round' }), S('rect', { x: -2.8, y: -8, width: 5.6, height: 16, rx: 2.5, fill: '#fff' }), S('circle', { cx: 0, cy: 13.5, r: 3.2, fill: '#fff' }));
  const hostCard = H('div', { class: 'abs', style: { left: '96px', top: '232px', width: '470px', padding: '18px 20px', display: 'flex', alignItems: 'center', gap: '18px', borderRadius: '18px', background: 'rgba(40,6,12,.92)', border: `3px solid ${RED}`, boxShadow: '0 0 40px rgba(255,59,92,.35)' } }, tri,
    H('div', { style: { display: 'flex', flexDirection: 'column', gap: '4px' } }, H('div', { style: { font: '800 26px var(--mono)', color: '#fff' }, text: 'HOST: GAS LEAK' }), H('div', { style: { font: '500 20px var(--font)', color: '#FFB3C0' }, text: 'detected on the platform' })));
  html.append(hostCard);
  show(hostCard, w('b4', 'gas') - 0.3, 0.5, { x: -24, y: 0 });
  animate(w('b4', 'gas'), bt('b5').start, (t) => { hostCard.style.borderColor = (Math.sin((t - w('b4', 'gas')) * 8) > 0 ? RED : '#7A1A2A'); });
  hide(hostCard, bt('b5').start - 0.1, 0.4, { x: -20 });
  const bn = H('div', { class: 'abs', style: { left: '0', top: '112px', width: '1920px', boxSizing: 'border-box', paddingLeft: '130px', textAlign: 'center' } },
    H('div', { style: { display: 'inline-block', padding: '12px 36px 14px', borderRadius: '16px', background: 'rgba(40,6,12,.94)', border: `3px solid ${RED}`, font: '800 50px var(--font)', color: '#fff', letterSpacing: '0.02em', boxShadow: '0 0 50px rgba(255,59,92,.5)' }, html: `EMERGENCY SHUTDOWN <span style="color:${RED}">· ESD</span>` }));
  html.append(bn);
  show(bn, w('b4', 'emergency') - 0.2, 0.5, { y: -20 });
  hide(bn, bt('b8').start - 0.3, 0.5);
  sfx(w('b4', 'emergency') - 0.2, 'alarm', 0.8);
  // the ESD signal runs from the host to the tree
  const esdD = `M566 262 C 800 150 1000 130 ${P(0, 20)[0] - 10} ${P(0, 20)[1] - 6}`;
  const esdSig = Flow(annot, esdD, { color: RED, w: 14, gap: 200, glowW: 2.4 });
  esdSig.show(w('b4', 'shutdown') - 0.4, 0.3, 300); esdSig.hide(w('b4', 'shutdown') + 1.5, 0.3);

  /* ---------------- the question (b5) ---------------- */
  const tQ = bt('b5').start, tA = bt('b6').start;
  // rows in the "wrong" order for the question: deepest first, the answer swaps them into place
  const dnRows = [
    mkRow({ n: 3, name: 'DHSV', sub: 'closes last', col: RED, top: 0 * ROW_P, st0: 'open', badgeQ: true, showSub: false }),
    mkRow({ n: 2, name: 'PMV', sub: 'closes next', col: RED, top: 1 * ROW_P, st0: 'open', badgeQ: true, showSub: false }),
    mkRow({ n: 1, name: 'PWV', sub: 'closes first, against the flow', col: RED, top: 2 * ROW_P, st0: 'open', badgeQ: true, showSub: false }),
  ];
  const [rDH, rPM, rPW] = dnRows;
  const dnList = mkList({ kickers: [{ text: 'Which valve closes first?', col: YEL }, { text: 'Shutdown sequence', col: RED }], rows: dnRows, at: w('b5', 'Which') - 0.25, until: bt('b8').end + 0.6, top: 188 });
  // countdown ring beside the list
  const cd = H('div', { class: 'abs', style: { left: '590px', top: '286px', width: '100px', height: '100px', borderRadius: '50%', border: `5px solid ${YEL}`, display: 'grid', placeItems: 'center', font: '800 56px var(--mono)', color: YEL, background: 'rgba(5,16,26,.92)' }, text: '3' });
  html.append(cd);
  const tCd0 = bt('b5').end + 0.15;
  show(cd, bt('b5').end - 0.4, 0.4, { scale: 0.7 });
  animate(tCd0 - 0.05, tA, (t) => { cd.textContent = String(Math.max(1, 3 - Math.floor(Math.max(0, t - tCd0)))); });
  hide(cd, tA - 0.15, 0.3);
  const think = ctx.tagAt({ x: 640, y: 424, text: 'Think about it …', color: YEL, anchor: 'c', size: 24, at: bt('b5').end - 0.3, until: tA - 0.15 });
  // candidate rows take turns lighting up while we wait
  animate(w('b5', 'Which'), tA - 0.05, (t) => dnRows.forEach((r, i) => { const ph = (t * 0.9 - i * 0.33) % 1; r.el.style.borderColor = (t < tA - 0.2 && ph >= 0 && ph < 0.3) ? YEL : 'rgba(170,200,225,.24)'; }));

  /* ---------------- answer + shutdown sequence (b6 / b7 / b8) ---------------- */
  dnList.kick(tA - 0.2, 1);
  // PWV first: it jumps to the top, the DHSV drops to the bottom (z-order: PWV above)
  rPW.el.style.zIndex = 3;
  const tClosePW = w('b6', 'wing') - 0.05;
  rPW.moveTo(tClosePW - 0.2, 0.9, 0 * ROW_P); rDH.moveTo(tClosePW - 0.2, 0.9, 2 * ROW_P);
  rPW.reveal(tClosePW, RED, true); rPW.light(tClosePW, RED);
  rPW.state(tClosePW + 0.1, 'closing'); rPW.state(tClosePW + 0.7, 'closed');
  V.PWV.close(tClosePW, 0.6, 'power3.in'); sfx(tClosePW + 0.3, 'clunk', 0.9);
  fly([96 + 470, 188 + 58 + 40], pWV, tClosePW - 0.1, 0.8, RED);
  ctx.ringAt({ shot: SH, tx: -230, ty: 320, r: 66, color: RED, at: tClosePW + 0.3, until: tClosePW + 2.4 });
  tree.flows.p_out1.hide(tClosePW + 0.25, 0.4); tree.flows.p_out2.hide(tClosePW + 0.4, 0.4);
  tree.flows.p_mid.speed(tClosePW + 0.25, 0, 0.3); tree.flows.p_low.speed(tClosePW + 0.25, 0, 0.3);
  ['p_out1', 'p_out2'].forEach((n) => tree.fills[n].to(tClosePW + 0.3, 0.6, 0.15));
  ['p_mid', 'p_tee', 'p_br1', 'p_br2'].forEach((n) => tree.fills[n].to(tClosePW + 0.3, 0.8, 0.8));
  ctx.tagAt({ x: pWV[0], y: pWV[1] + 130, text: 'Closes against the flow', color: RED, anchor: 'c', size: 24, at: w('b6', 'designed') - 0.3, until: bt('b7').start + 0.2 });
  // PMV next
  const tClosePM = w('b7', 'master') - 0.05;
  rPM.reveal(tClosePM, RED, true); rPM.light(tClosePM, RED);
  rPM.state(tClosePM + 0.1, 'closing'); rPM.state(tClosePM + 0.7, 'closed');
  V.PMV.close(tClosePM, 0.6, 'power3.in'); sfx(tClosePM + 0.3, 'clunk', 0.9);
  fly([96 + 470, 188 + 58 + ROW_P + 40], [P(-70, 500)[0], pMV[1]], tClosePM - 0.1, 0.8, RED);
  ctx.ringAt({ shot: SH, tx: -60, ty: 500, r: 70, color: RED, at: tClosePM + 0.3, until: tClosePM + 2.2 });
  tree.flows.p_low.hide(tClosePM + 0.3, 0.4);
  ['p_mid', 'p_tee', 'p_br1', 'p_br2'].forEach((n) => tree.fills[n].to(tClosePM + 0.4, 0.8, 0.3));
  // only once the flow has stopped: DHSV, the last line of defence
  ctx.tagAt({ x: 1690, y: 690, text: 'FLOW STOPPED', color: GRN, mono: true, size: 28, anchor: 'c', at: w('b7', 'stopped') - 0.3, until: bt('b8').start });
  fLow.speed(w('b7', 'stopped') - 0.1, 0, 0.5); fHigh.speed(w('b7', 'stopped') - 0.1, 0, 0.5);
  const tCloseDH = w('b7', 'downhole');
  rDH.reveal(tCloseDH, RED, true); rDH.light(tCloseDH, RED);
  rDH.state(tCloseDH + 0.1, 'closing'); rDH.state(tCloseDH + 0.6, 'closed');
  fly([96 + 470, 188 + 58 + 2 * ROW_P + 40], [526, 770], tCloseDH - 0.1, 0.8, RED);
  dh.close(tCloseDH + 0.5, 0.55); dState(tCloseDH + 0.8, false);
  fHigh.hide(tCloseDH + 0.8, 0.4);
  sfx(tCloseDH + 0.7, 'clunk', 1.0);
  const dhRing = S('rect', { x: 8, y: 8, width: 414, height: 288, rx: 16, fill: 'none', stroke: RED, 'stroke-width': 5, opacity: 0 });
  ins.append(dhRing);
  tl.fromTo(dhRing, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: false }, w('b7', 'last') - 0.3);
  tl.to(dhRing, { opacity: 0, duration: 0.5 }, bt('b7').end + 0.6);
  ctx.tagAt({ x: 311, y: 598, text: 'LAST LINE OF DEFENCE', color: RED, mono: true, size: 24, anchor: 'c', at: w('b7', 'last') - 0.3, until: bt('b8').start + 0.3 });

  /* ---------------- b8: hydraulics vented, springs do the rest ---------------- */
  const tVent = w('b8', 'hydraulics');
  const r_ = rng(7);
  const bubbles = S('g', { fill: CY });
  const bb = [];
  [V.PMV, V.PWV].forEach((v) => { const [px, py] = v.toWorld(...v.anchors.portLocal); const [wx, wy] = ctx.w(px, py); for (let i = 0; i < 7; i++) { const c = S('circle', { r: 4 + r_() * 3 }); bubbles.append(c); bb.push({ c, wx, wy, ph: r_(), dx: (r_() - 0.5) * 30 }); } });
  world.append(bubbles);
  tl.set(bubbles, { opacity: 0 }, 0);
  tl.fromTo(bubbles, { opacity: 0 }, { opacity: 1, duration: 0.3, immediateRender: false }, tVent - 0.2);
  tl.to(bubbles, { opacity: 0, duration: 0.5 }, tVent + 2.4);
  animate(tVent - 0.25, tVent + 3.1, (t) => bb.forEach((b_) => { const p = (((t - tVent) * 0.7 + b_.ph) % 1 + 1) % 1; b_.c.setAttribute('cx', (b_.wx + b_.dx * p).toFixed(1)); b_.c.setAttribute('cy', (b_.wy - 110 * p).toFixed(1)); b_.c.setAttribute('opacity', (1 - p).toFixed(2)); }));
  const pPort = V.PMV.toWorld(...V.PMV.anchors.portLocal), pp = ctx.Pw(SH, ...ctx.w(...pPort));
  ctx.tagAt({ x: pp[0] - 30, y: pp[1] + 82, text: 'Hydraulic pressure vented', color: CY, anchor: 'r', size: 24, at: tVent - 0.2, until: w('b8', 'springs') + 0.2 });
  const tSp = w('b8', 'springs');
  [V.PMV, V.PWV].forEach((v) => { const [sx_, sy_] = v.toWorld(-3.49 * v.bw, 0); ctx.ringAt({ shot: SH, tx: sx_, ty: sy_, r: 52, color: YEL, at: tSp - 0.2, until: T.scene('esd').end - 0.15 }); });
  ctx.tagAt({ x: 1700, y: 840, text: 'No manual action', color: GRN, mono: true, size: 26, anchor: 'c', at: w('b8', 'operator') - 0.3, until: tVent - 0.3 });
  ctx.tagAt({ x: 1690, y: 840, text: 'Springs close the valves', color: YEL, anchor: 'c', size: 26, at: tSp - 0.2, until: T.scene('esd').end - 0.15 });
}
