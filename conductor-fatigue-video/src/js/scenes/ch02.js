// Chapter 2 — fatigue and the S-N curve: weld toe, stress cycle, residual stress, Paris law -> S-N, design curve, DNV curves.
import { E, ease, COL, clamp, smooth, lerp, fmt } from '../engine/core.js';
import { Scene, morph, later } from '../engine/scene.js';
import { titleCard, clause, step } from '../engine/hud.js';
import { quoteCard, derivation, table, tx, brace } from './kit.js';
import { weldToe } from './drawings.js';
import { snCurve, snN, snS, prng, gauss, logTicks, pow10 } from './fatigue.js';

export async function build(E, T, D) {
  const ch = T.ch(2);
  titleCard(ch, 'What fatigue is, and where the S-N curve comes from');
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  step(ch.title_card[1], -1);

  // ------------------------------------------------------------------ 2.1 what fatigue is
  {
    const B = b('2.1');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · 3.2.19 fatigue', B.start + 0.5, B.end);
    quoteCard(S, '3.2.19 · fatigue', 'process of progressive localized structural change occurring in a material/component subjected to conditions which produce <span class="q">fluctuating stresses</span> at some point or points and which can culminate in <span class="q">cracks or complete fracture</span> after a sufficient number of load cycles',
      { x: 1080, y: 230, w: 720, t: c('2.1', 'def'), size: 27 });
    const wt = weldToe(S, 520, 560, { s: 1.25 });
    wt.g.in(B.start + 0.4, 0.8, 'none');
    const lab1 = S.callout(657, 560, 760, 420, 'weld toe', { t: c('2.1', 'toe'), color: COL.coral });
    wt.toe.pulse(c('2.1', 'toe'), 0.6, 0.8);
    wt.grow(c('2.1', 'beach') - 0.5, B.end - 1.0);
    const lab2 = S.div('a fatigue crack grows a little every cycle', { x: 700, y: 790, cls: 'small' });
    lab2.in(c('2.1', 'beach') + 0.4, 0.5, 'left');
    S.div('plate', { x: 40, y: 640, cls: 'tiny' }).in(B.start + 1, 0.5);
    S.div('weld cap', { x: 470, y: 470, cls: 'tiny', anchor: 'cb' }).in(B.start + 1, 0.5);
  }

  // ------------------------------------------------------------------ 2.2 anatomy of a cycle (+ 2.3 why the range)
  {
    const B = b('2.2'), B3 = b('2.3');
    const S = new Scene(B.start, B.end);
    const ch1 = S.chart({ x: 220, y: 230, w: 1100, h: 560, xmin: 0, xmax: 4, ymin: -1.4, ymax: 2.4, xticks: [], yticks: [], grid: false, xlabel: 'time', ylabel: 'stress' });
    ch1.show(B.start + 0.3);
    const zero = S.line(ch1.X(0), ch1.Y(0), ch1.X(4), ch1.Y(0), { stroke: 'rgba(200,225,245,0.35)', width: 2, dash: '8 8' });
    zero.in(B.start + 0.5, 0.5, 'none');
    S.svgText('0', ch1.X(0) - 16, ch1.Y(0), { size: 20, anchor: 'end', o: 1 }).in(B.start + 0.5, 0.4, 'none');
    // the signal: mean drifts from 0.7 to 0 at the "reversed" cue
    const tRev = c('2.2', 'rev');
    const mean = (t) => lerp(0.7, 0, smooth(t, tRev, tRev + 1.4));
    const amp = 0.95;
    const sig = S.path('', { stroke: COL.coral, width: 5 });
    sig.in(B.start + 0.6, 0.3, 'none');
    const meanLine = S.path('', { stroke: COL.violet, width: 2.5, dash: '10 8' });
    meanLine.in(c('2.2', 'mean'), 0.4, 'none');
    E.anim(B.start, B.end, (t) => {
      const m = mean(t), draw = clamp((t - B.start - 0.6) / 2.2);
      let d = '';
      for (let i = 0; i <= 200 * draw; i++) { const x = 4 * i / 200; d += `${i ? 'L' : 'M'}${ch1.X(x).toFixed(1)},${ch1.Y(m + amp * Math.sin(2 * Math.PI * x / 1.6)).toFixed(1)}`; }
      sig.el.setAttribute('d', d);
      meanLine.el.setAttribute('d', `M${ch1.X(0)},${ch1.Y(m)} L${ch1.X(4)},${ch1.Y(m)}`);
    });
    // annotations (positioned for the first, non-zero-mean state)
    const xA = ch1.X(2.0), yMax = ch1.Y(0.7 + amp), yMin = ch1.Y(0.7 - amp);
    const rng = S.arrow(xA, yMin + 2, xA, yMax - 2, { color: COL.coral, width: 3 });
    const rng2 = S.arrow(xA, yMax - 2, xA, yMin + 2, { color: COL.coral, width: 3 });
    rng.in(c('2.2', 'range'), 0.4, 'none'); rng2.in(c('2.2', 'range'), 0.4, 'none');
    const eRange = S.eq('\\Ds = \\sigma_{\\max}-\\sigma_{\\min}', { x: 1380, y: 300, size: 46, align: 'left' });
    eRange.in(c('2.2', 'range'), 0.6, 'write');
    const eAmp = S.eq('\\sigma_a = \\tfrac{1}{2}\\Ds', { x: 1380, y: 400, size: 46, align: 'left' });
    eAmp.in(c('2.2', 'amp'), 0.6, 'write');
    const eMean = S.eq('\\sigma_m = \\tfrac{1}{2}(\\sigma_{\\max}+\\sigma_{\\min})', { x: 1380, y: 500, size: 46, align: 'left' });
    eMean.in(c('2.2', 'mean'), 0.6, 'write');
    const eR = S.eq('R = \\dfrac{\\sigma_{\\min}}{\\sigma_{\\max}}', { x: 1380, y: 620, size: 46, align: 'left' });
    eR.in(c('2.2', 'R'), 0.6, 'write');
    const eRev = S.eq('R=-1,\\;\\; \\sigma_m = 0', { x: 1380, y: 740, size: 46, align: 'left', color: COL.amber });
    eRev.in(tRev + 0.4, 0.6, 'write');
    for (const a of [rng, rng2]) a.out(tRev, 0.4);
    const rev = S.div('fully reversed · B.4.2.4 c)', { x: 1380, y: 800, cls: 'tiny' });
    rev.in(tRev + 0.8, 0.5);

    // 2.3: why only the range matters
    const S3 = new Scene(B3.start, B3.end);
    const cA = S3.chart({ x: 160, y: 300, w: 640, h: 460, xmin: 0, xmax: 3.2, ymin: -1.3, ymax: 2.6, xticks: [], yticks: [], grid: false, xlabel: 'nominal stress, two different means', title: 'NOMINAL' });
    const cB = S3.chart({ x: 1100, y: 300, w: 640, h: 460, xmin: 0, xmax: 3.2, ymin: -1.3, ymax: 2.6, xticks: [], yticks: [], grid: false, xlabel: 'local stress at the weld toe', title: 'AT THE TOE' });
    cA.show(B3.start + 0.2); cB.show(c('2.3', 'resid'));
    const curve = (chh, m, a, n = 160) => { let d = ''; for (let i = 0; i <= n; i++) { const x = 3.2 * i / n; d += `${i ? 'L' : 'M'}${chh.X(x).toFixed(1)},${chh.Y(m + a * Math.sin(2 * Math.PI * x / 1.6)).toFixed(1)}`; } return d; };
    const s1 = S3.path(curve(cA, 0.0, 0.8), { stroke: COL.cyan, width: 4 }); s1.set(0, { draw: 0 }).to(B3.start + 0.4, 1.4, { draw: 1 }).in(B3.start + 0.4, 0.01, 'none');
    const s2 = S3.path(curve(cA, 1.0, 0.8), { stroke: COL.amber, width: 4 }); s2.set(0, { draw: 0 }).to(B3.start + 0.9, 1.4, { draw: 1 }).in(B3.start + 0.9, 0.01, 'none');
    const yl = S3.line(cB.X(0), cB.Y(2.1), cB.X(3.2), cB.Y(2.1), { stroke: COL.red, width: 2.5, dash: '10 8' });
    yl.in(c('2.3', 'resid'), 0.5, 'none');
    S3.svgText('yield', cB.X(3.2) + 10, cB.Y(2.1), { anchor: 'start', fill: COL.red, size: 20, o: 0 }).in(c('2.3', 'resid'), 0.5, 'none');
    const loc = S3.path(curve(cB, 2.1 - 0.8, 0.8), { stroke: COL.coral, width: 5 }); loc.set(0, { draw: 0 }).to(c('2.3', 'resid') + 0.4, 1.4, { draw: 1 }).in(c('2.3', 'resid') + 0.4, 0.01, 'none');
    const arr = S3.arrow(830, 530, 1060, 530, { color: COL.ink2, width: 4 });
    arr.in(c('2.3', 'resid'), 0.5, 'none');
    S3.div('residual stress ≈ yield', { x: 945, y: 490, cls: 'tiny', anchor: 'cb' }).in(c('2.3', 'resid') + 0.2, 0.5);
    const same = S3.eq('\\text{same } \\Ds \\;\\Rightarrow\\; \\text{same damage}', { x: 960, y: 900, size: 48 });
    same.in(c('2.3', 'same'), 0.7, 'write');
    same.boxed(c('2.3', 'same') + 1.0);
  }

  // ------------------------------------------------------------------ 2.4 Paris law  +  2.5 integrate  (one board)
  {
    const B4 = b('2.4'), B5 = b('2.5');
    const S = new Scene(B4.start, B5.end);
    // crack sketch (left)
    const g = S.g(); g.in(B4.start + 0.3, 0.6, 'none');
    S.rect(170, 330, 460, 330, { fill: '#2c3f52', stroke: '#8fa7bb', width: 2, parent: g.el, o: 1 });
    // the crack ratchets deeper, a little every cycle, while the Paris law is introduced
    const crack = S.path('', { stroke: COL.coral, width: 5, parent: g.el, o: 1 });
    crack.el.setAttribute('filter', 'url(#glow)');
    const adim = S.path('', { stroke: COL.ink2, width: 2, parent: g.el, o: 1 });
    const alab = S.svgText('a', 462, 400, { size: 30, fill: COL.ink, parent: g.el, o: 1, family: 'KaTeX_Math' });
    E.anim(B4.start - 0.1, B5.start + 1, (t) => {
      const u = Math.floor(14 * smooth(t, B4.start + 0.8, c('2.4', 'dk') + 1.0)) / 14;
      const L = 36 + 118 * u, y = 330;
      crack.el.setAttribute('d', `M400,${y} L406,${(y + L * 0.35).toFixed(1)} L399,${(y + L * 0.7).toFixed(1)} L404,${(y + L).toFixed(1)}`);
      adim.el.setAttribute('d', `M440,${y} L440,${(y + L).toFixed(1)}`);
      alab.el.setAttribute('y', (y + L / 2).toFixed(1));
    });
    for (const x of [230, 330, 470, 570]) { S.arrow(x, 300, x, 230, { color: COL.coral, width: 3, parent: g.el, o: 1 }); S.arrow(x, 690, x, 760, { color: COL.coral, width: 3, parent: g.el, o: 1 }); }
    S.svgText('σ', 650, 255, { size: 30, fill: COL.coral, parent: g.el, o: 1 });
    g.out(B5.start + 0.3, 0.6);
    // equations
    const e1 = S.eq('\\frac{\\dd a}{\\dd \\cn{N}} = C\\,\\left(\\p{dK}{\\Delta K}\\right)^{\\cv m}', { x: 1240, y: 360, size: 64 });
    e1.in(c('2.4', 'paris'), 0.8, 'write');
    S.div('Paris law: growth per cycle', { x: 1240, y: 270, cls: 'tiny', anchor: 'cm' }).in(c('2.4', 'paris'), 0.5).out(B5.start, 0.4);
    const e2 = S.eq('\\p{dK}{\\Delta K} = Y\\,\\Ds\\,\\sqrt{\\pi a}', { x: 1240, y: 560, size: 60 });
    e2.in(c('2.4', 'dk'), 0.8, 'write');
    S.div('stress intensity range', { x: 1240, y: 480, cls: 'tiny', anchor: 'cm' }).in(c('2.4', 'dk'), 0.5).out(B5.start, 0.4);
    // 2.5: derivation steps move to centre
    e1.to(B5.start, 0.8, { x: -280, y: -160, s: 0.75 });
    e2.to(B5.start, 0.8, { x: 280, y: -360, s: 0.75 });
    const st = derivation(S, [
      { tex: '\\frac{\\dd a}{\\dd \\cn N} = C\\,\\left(Y\\,\\Ds\\sqrt{\\pi a}\\right)^{\\cv m}', t: B5.start + 0.6, note: 'substitute' },
      { tex: '\\dd \\cn N = \\frac{\\dd a}{C\\,Y^{\\cv m}\\,\\Ds^{\\cv m}\\,(\\pi a)^{\\cv m/2}}', t: c('2.5', 'sep'), note: 'separate' },
      { tex: '\\cn N = \\frac{1}{C\\,\\Ds^{\\cv m}}\\p{int}{\\int_{a_i}^{a_f}\\frac{\\dd a}{Y^{\\cv m}(\\pi a)^{\\cv m/2}}}', t: c('2.5', 'int'), note: 'integrate', gap: 170 },
    ], { x: 1060, y0: 360, gap: 150, size: 54 });
    st[2].hl('int', c('2.5', 'brace'), { color: COL.violet, pad: 10 });
    const br = S.div('depends only on geometry and flaw sizes → a constant', { x: 1240, y: 830, cls: 'small', anchor: 'cm', style: 'color:#b794f6' });
    br.in(c('2.5', 'brace') + 0.4, 0.6);
    const res = S.eq('\\cn N\\,\\Ds^{\\cv m} = \\bar a', { x: 960, y: 960, size: 72 });
    res.in(c('2.5', 'result'), 0.8, 'pop');
    res.boxed(c('2.5', 'abar'), { color: COL.amber });
  }

  // ------------------------------------------------------------------ 2.6 log-log line
  {
    const B = b('2.6');
    const S = new Scene(B.start, B.end);
    const eq = S.eq('\\log \\cn N = \\log \\bar a - \\cv m\\,\\log \\Ds', { x: 1380, y: 220, size: 54 });
    eq.in(c('2.6', 'log'), 0.8, 'write');
    const cc = S.chart({ x: 220, y: 200, w: 820, h: 640, xlog: true, ylog: true, xmin: 1e4, xmax: 1e9, ymin: 10, ymax: 1000,
      xticks: logTicks(1e4, 1e9), yticks: [10, 100, 1000], xfmt: pow10, yfmt: (v) => String(v), xlabel: 'cycles to failure, N', ylabel: 'stress range Δσ [MPa]' });
    cc.show(B.start + 0.4);
    const sn = { m1: 3, loga1: 12.449 };
    const pts = snCurve(sn, 1e4, 1e9);
    cc.curve(pts, { color: COL.amber, width: 5, t: c('2.6', 'line') });
    // slope triangle
    const N1 = 1e6, N2 = 1e7;
    const tri = S.path(`M${cc.X(N1)},${cc.Y(snS(N1, sn))} L${cc.X(N2)},${cc.Y(snS(N1, sn))} L${cc.X(N2)},${cc.Y(snS(N2, sn))}`, { stroke: COL.violet, width: 3, dash: '8 6' });
    tri.in(c('2.6', 'm3'), 0.5, 'none');
    S.div('×10 cycles', { x: (cc.X(N1) + cc.X(N2)) / 2, y: cc.Y(snS(N1, sn)) - 26, cls: 'tiny', anchor: 'cm', style: 'color:#b794f6' }).in(c('2.6', 'm3'), 0.5);
    S.div('÷10<sup>1/m</sup>', { x: cc.X(N2) + 16, y: (cc.Y(snS(N1, sn)) + cc.Y(snS(N2, sn))) / 2, cls: 'tiny', anchor: 'lm', style: 'color:#b794f6' }).in(c('2.6', 'm3'), 0.5);
    const mcard = S.card(`<div class="title">For welded steel</div><div class="eq" style="position:relative;font-size:46px">${tx('\\cv m \\approx 3')}</div>`, { x: 1180, y: 340, w: 400 });
    mcard.in(c('2.6', 'm3'), 0.6);
    // doubling the stress
    const s1 = 60, s2 = 120;
    const p1 = cc.dot(snN(s1, sn), s1, { color: COL.cyan, r: 10, t: c('2.6', 'eight') - 1.2 });
    const p2 = cc.dot(snN(s2, sn), s2, { color: COL.coral, r: 10, t: c('2.6', 'eight') - 0.8 });
    const eq8 = S.eq('2\\Ds \\;\\Rightarrow\\; \\cn N \\div 2^{\\cv 3} = \\cn N \\div 8', { x: 1380, y: 640, size: 50 });
    eq8.in(c('2.6', 'eight') - 0.9, 0.7, 'write');
    eq8.boxed(c('2.6', 'eight'), { color: COL.coral });
  }

  // ------------------------------------------------------------------ 2.7 design curve
  {
    const B = b('2.7');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · 3.2.43 S-N curve, note 1', B.start + 0.5, B.end);
    const cc = S.chart({ x: 220, y: 190, w: 1000, h: 680, xlog: true, ylog: true, xmin: 1e4, xmax: 1e9, ymin: 20, ymax: 600,
      xticks: logTicks(1e4, 1e9), yticks: [20, 50, 100, 200, 500], xfmt: pow10, yfmt: (v) => String(v), xlabel: 'cycles to failure, N', ylabel: 'Δσ [MPa]' });
    cc.show(B.start + 0.3);
    const mean = { m1: 3, loga1: 12.449 + 0.4 }, sd = 0.2;
    const r = prng(42);
    const dots = [];
    for (let i = 0; i < 46; i++) {
      const s = Math.pow(10, Math.log10(40) + r() * Math.log10(400 / 40));
      const lN = Math.log10(snN(s, mean)) + gauss(r) * sd;
      if (lN < 4.05 || lN > 8.95) continue;
      dots.push(cc.dot(Math.pow(10, lN), s, { color: COL.cyan, r: 6, t: c('2.7', 'scatter') + i * 0.025 }));
    }
    const mline = cc.curve(snCurve(mean, 1e4, 1e9), { color: COL.ink2, width: 3, dash: '10 8', t: c('2.7', 'scatter') + 1.0 });
    const dline = cc.curve(snCurve({ m1: 3, loga1: mean.loga1 - 2 * sd }, 1e4, 1e9), { color: COL.amber, width: 5, t: c('2.7', 'shift') });
    S.div('mean', { x: cc.X(2e8) + 6, y: cc.Y(snS(2e8, mean)) - 26, cls: 'tiny' }).in(c('2.7', 'scatter') + 1.4, 0.5);
    S.div('design = mean − 2 s', { x: cc.X(2e4), y: cc.Y(snS(2e4, { m1: 3, loga1: mean.loga1 - 0.4 })) + 40, cls: 'small', style: 'color:#ffb547' }).in(c('2.7', 'shift') + 0.6, 0.5);
    // sideways normal distribution at 100 MPa
    const sref = 100, lc = Math.log10(snN(sref, mean));
    let dd = '';
    for (let i = 0; i <= 80; i++) { const z = -3 + 6 * i / 80; const xx = cc.X(Math.pow(10, lc + z * sd)); const yy = cc.Y(sref) - 150 * Math.exp(-z * z / 2); dd += `${i ? 'L' : 'M'}${xx.toFixed(1)},${yy.toFixed(1)}`; }
    const bell = S.path(dd, { stroke: COL.violet, width: 3 }); bell.set(0, { draw: 0 }).to(c('2.7', 'shift') - 0.6, 1.0, { draw: 1 }).in(c('2.7', 'shift') - 0.6, 0.01, 'none');
    const x2 = cc.X(Math.pow(10, lc - 2 * sd));
    const cut = S.line(x2, cc.Y(sref) - 165, x2, cc.Y(sref) + 10, { stroke: COL.amber, width: 3 });
    cut.in(c('2.7', 'frac'), 0.4, 'none');
    const q = quoteCard(S, '3.2.43 note 1', 'The S-N curve is defined as the value below which <span class="q">2,3 %</span> of the values are expected to fall (mean minus two standard deviations), i.e. <span class="q">97,7 % probability of survival</span>', { x: 1280, y: 250, w: 520, t: c('2.7', 'frac'), size: 26 });
  }

  // ------------------------------------------------------------------ 2.8 DNV curves and environment
  {
    const B = b('2.8');
    const S = new Scene(B.start, B.end);
    clause('DNV-RP-C203 · S-N curves (referenced by B.4.1)', B.start + 0.5, B.end);
    const sn = D.sn;
    const cc = S.chart({ x: 200, y: 190, w: 960, h: 660, xlog: true, ylog: true, xmin: 1e4, xmax: 1e9, ymin: 20, ymax: 600,
      xticks: logTicks(1e4, 1e9), yticks: [20, 50, 100, 200, 500], xfmt: pow10, yfmt: String, xlabel: 'cycles to failure, N', ylabel: 'Δσ [MPa]', title: 'CLASS C1' });
    cc.show(B.start + 0.3);
    const air = cc.curve(snCurve(sn.C1_air, 1e4, 1e9), { color: COL.ink2, width: 4, t: c('2.8', 'air') });
    const cp = cc.curve(snCurve(sn.C1_CP, 1e4, 1e9), { color: COL.amber, width: 5, t: c('2.8', 'cp') });
    const fc = cc.curve(snCurve(sn.C1_FC, 1e4, 1e9), { color: COL.coral, width: 4, dash: '12 8', t: c('2.8', 'fc') });
    // while the reference is introduced: what the families are (gives way to the parameter table)
    S.card(`<div class="ref">DNV-RP-C203:2024 · referenced by U-001 B.4.1</div><div style="font-weight:750;font-size:30px;margin-bottom:10px">S-N curves come in families</div>` +
      `<div class="small">one curve per <b class="c-amber">detail class</b> (B1 … W3), for each <b class="c-amber">environment</b>: in air · seawater with cathodic protection · free corrosion</div>`,
      { x: 1240, y: 260, w: 560, cls: 'glass' }).in(c('2.8', 'dnv'), 0.6).out(c('2.8', 'c1') - 0.7, 0.5);
    const lab = (txt, N, curve, col, t, dy = -24) => S.div(txt, { x: cc.X(N), y: cc.Y(snS(N, curve)) + dy, cls: 'tiny', anchor: 'cm', style: `color:${col};letter-spacing:0.06em` }).in(t + 0.6, 0.5);
    lab('IN AIR', 4e8, sn.C1_air, COL.ink2, c('2.8', 'air'), -26);
    lab('SEAWATER + CP', 1.6e7, sn.C1_CP, COL.amber, c('2.8', 'cp'), 34);
    lab('FREE CORROSION', 3e5, sn.C1_FC, COL.coral, c('2.8', 'fc'), 40);
    const k1 = cc.dot(1e7, snS(1e7, sn.C1_air), { color: COL.ink2, r: 8, t: c('2.8', 'air') + 1.0 });
    const k2 = cc.dot(1e6, snS(1e6, sn.C1_CP), { color: COL.amber, r: 9, t: c('2.8', 'cp') + 1.0 });
    // parameter table
    const tb = table(S, ['', 'N ≤ 10⁶', 'N > 10⁶'], [
      [tx('\\cv{m}'), '3', '5'],
      [tx('\\log\\bar a'), '12.049', '16.081'],
      ['knee Δσ', '103.8 MPa', ''],
    ], { x: 1230, y: 260, w: 560, t: c('2.8', 'c1'), title: 'C1 · seawater + cathodic protection', colCls: ['l', '', ''] });
    const flag = S.card('<span class="badge warn">for teaching</span><div class="small" style="margin-top:12px">DNV-RP-C203 <b>2016</b> values. NORSOK U-001:2026 refers to <b>DNV-RP-C203:2024</b>, which revised the seawater curves: take design values from the edition in your design basis.</div>', { x: 1230, y: 600, w: 560 });
    flag.in(c('2.8', 'flag'), 0.6);
  }

  // ------------------------------------------------------------------ 2.9 thickness effect
  {
    const B = b('2.9');
    const S = new Scene(B.start, B.end);
    clause('DNV-RP-C203 · thickness effect', B.start + 0.5, B.end);
    // thin vs thick plate sketches with toe stress gradients
    const g = S.g(); g.in(c('2.9', 'thick'), 0.6, 'none');
    const plate = (x, y, t, lbl) => {
      S.rect(x, y, 360, t, { fill: '#2c3f52', stroke: '#8fa7bb', width: 2, parent: g.el, o: 1 });
      S.path(`M${x + 140},${y} C${x + 160},${y - 30} ${x + 200},${y - 30} ${x + 220},${y}`, { fill: '#4a6176', stroke: '#c7d6e2', width: 2, parent: g.el, o: 1 });
      let d = `M${x + 220},${y}`;
      for (let i = 0; i <= 30; i++) { const z = t * i / 30; d += ` L${x + 220 + 90 * Math.exp(-z / (t * 0.35))},${y + z}`; }
      S.path(d, { stroke: COL.coral, width: 3, parent: g.el, o: 1 });
      S.svgText(lbl, x + 180, y + t + 30, { size: 20, parent: g.el, o: 1 });
    };
    plate(200, 330, 90, 'thin');
    plate(200, 560, 200, 'thick');
    // the two reasons, as they are said (they make room for the formula)
    const why = [['decays', 'the toe stress decays more slowly through a thick wall'], ['volume', 'more stressed volume, so more room for flaws']];
    why.forEach(([wd, txt], i) => {
      S.div(`<div style="display:flex;gap:16px;align-items:center"><span style="width:12px;height:12px;border-radius:50%;background:#ff6f61;flex:none"></span><span class="body" style="color:var(--ink)">${txt}</span></div>`,
        { x: 760, y: 420 + i * 90, w: 1000 }).in(T.w('2.9', wd), 0.6, 'left').out(c('2.9', 'tf') - 0.5, 0.5);
    });
    const e = S.eq('\\log \\cn N = \\log\\bar a - \\cv m \\log\\!\\left[\\Ds \\p{tf}{\\left(\\frac{t}{t_{\\mathrm{ref}}}\\right)^{k}}\\right]', { x: 1230, y: 330, size: 50 });
    e.in(c('2.9', 'tf'), 0.8, 'write');
    e.hl('tf', c('2.9', 'tf') + 1.6, { color: COL.amber });
    S.div('t<sub>ref</sub> = 25 mm', { x: 1230, y: 430, cls: 'small', anchor: 'cm' }).in(c('2.9', 'tf') + 1.0, 0.5);
    const n = S.eq('\\left(\\frac{50.8}{25}\\right)^{0.15} = 1.11', { x: 1230, y: 640, size: 54 });
    n.in(c('2.9', 'num'), 0.8, 'write');
    S.div('2 in conductor wall, k = 0.15 (DNV-RP-C203 2016, C1)', { x: 1230, y: 730, cls: 'tiny', anchor: 'cm' }).in(c('2.9', 'num') + 0.4, 0.5);
  }

  // ------------------------------------------------------------------ 2.10 class C1 requirement
  {
    const B = b('2.10');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · 13.3.6.2 and B.10.4', B.start + 0.5, B.end);
    quoteCard(S, '13.3.6.2 · conductor', '<span class="q">Girth welds on the conductor</span> (e.g. conductor housing to conductor extension) <span class="q">shall meet S–N class C1</span> in accordance with DNV-RP-C203:2024.', { x: 120, y: 260, w: 760, t: B.start + 0.6, size: 32 });
    const cc = S.chart({ x: 1020, y: 230, w: 760, h: 560, xlog: true, ylog: true, xmin: 1e4, xmax: 1e9, ymin: 20, ymax: 600,
      xticks: logTicks(1e4, 1e9), yticks: [20, 50, 100, 200, 500], xfmt: pow10, yfmt: String, xlabel: 'N', ylabel: 'Δσ [MPa]', title: 'IN AIR' });
    cc.show(c('2.10', 'req') + 0.4);
    const C1 = { m1: 3, loga1: 12.449, m2: 5, loga2: 16.081, Nknee: 1e7 };
    const Dc = { m1: 3, loga1: 12.164, m2: 5, loga2: 15.606, Nknee: 1e7 };
    const Fc = { m1: 3, loga1: 11.855, m2: 5, loga2: 15.091, Nknee: 1e7 };
    cc.curve(snCurve(Fc), { color: COL.dim, width: 3, t: c('2.10', 'above') - 0.6 });
    cc.curve(snCurve(Dc), { color: COL.ink2, width: 3, t: c('2.10', 'above') - 0.3 });
    cc.curve(snCurve(C1), { color: COL.amber, width: 5, t: c('2.10', 'above') });
    const lab = (txt, curve, col, t) => S.div(txt, { x: cc.X(3e4), y: cc.Y(snS(3e4, curve)) - 18, cls: 'tiny', anchor: 'cm', style: `color:${col}` }).in(t, 0.5);
    lab('C1', C1, COL.amber, c('2.10', 'above') + 0.8);
    lab('D', Dc, COL.ink2, c('2.10', 'above') + 0.5);
    lab('F', Fc, COL.dim, c('2.10', 'above') + 0.2);
  }
}
