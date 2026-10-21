// Chapter 3 — from waves to the wellhead moment: the chain, the lever arm, the moment below the datum, Tables A.7 and A.8.
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt } from '../engine/core.js';
import { Scene } from '../engine/scene.js';
import { titleCard, clause, step } from '../engine/hud.js';
import { quoteCard, derivation, table, tx, counter } from './kit.js';
import { ground } from './drawings.js';
import { logTicks, pow10 } from './fatigue.js';

export async function build(E, T, D) {
  const ch = T.ch(3);
  titleCard(ch, 'Step 1 · the fatigue load at the wellhead datum (Annex A)');
  step(ch.title_card[1], 0);
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const L = D.loads;

  // ------------------------------------------------------------------ 3.1 the chain (animated schematic)
  {
    const B = b('3.1');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · Annex A.3 · Annex J.4.2.1 (metocean, vessel RAO)', B.start + 0.4, B.end);
    // geometry (px): sea surface y 230, seabed y 900, wellhead datum y 800, flex joint y 610
    const xs = 560, ySea = 230, yBed = 900, yWH = 812, yFJ = 612;
    const off = (t) => 70 * Math.sin(2 * Math.PI * (t - B.start) / 7.5) * smooth(t, c('3.1', 'vessel') - 0.5, c('3.1', 'vessel') + 1);
    const tilt = (t) => 0.06 * Math.sin(2 * Math.PI * (t - B.start - 0.6) / 7.5) * smooth(t, c('3.1', 'stack') - 0.6, c('3.1', 'stack') + 1);
    const sea = S.path('', { stroke: '#5aa9ff', width: 4 }); sea.in(B.start + 0.2, 0.5, 'none');
    const water = S.path('', { fill: 'rgba(40,110,170,0.10)', stroke: 'none', width: 0 }); water.in(B.start + 0.2, 0.5, 'none');
    const gr = ground(S, 160, 980, yBed); gr.in(B.start + 0.3, 0.5, 'none');
    S.div('≈ 350 m', { x: 975, y: (ySea + yBed) / 2, cls: 'small', anchor: 'rm' }).in(B.start + 0.6, 0.5);
    const dim = S.path(`M995,${ySea} L995,${yBed}`, { stroke: COL.dim, width: 2, dash: '6 6' }); dim.in(B.start + 0.6, 0.5, 'none');
    const rig = S.g(); rig.in(B.start + 0.3, 0.5, 'none');
    const rr = (x, y, w, h, f) => S.rect(x, y, w, h, { fill: f, stroke: 'none', parent: rig.el, o: 1 });
    rr(-120, -10, 240, 26, '#c7cfd6'); rr(-100, 16, 40, 40, '#c7cfd6'); rr(60, 16, 40, 40, '#c7cfd6'); rr(-130, 52, 260, 18, '#b0322a');
    S.path('M-30,-10 L-10,-110 L10,-110 L30,-10', { stroke: '#e9eef2', width: 4, parent: rig.el, o: 1 });
    const riser = S.path('', { stroke: COL.steel, width: 7 }); riser.in(B.start + 0.4, 0.5, 'none');
    const stack = S.g(); stack.in(B.start + 0.4, 0.5, 'none');
    S.rect(-46, -175, 92, 175, { fill: '#5d6b78', stroke: '#e7ae1c', width: 4, parent: stack.el, o: 1 });
    S.rect(-30, -150, 60, 30, { fill: '#e7ae1c', parent: stack.el, o: 1 }); S.rect(-30, -100, 60, 30, { fill: '#e7ae1c', parent: stack.el, o: 1 }); S.rect(-30, -50, 60, 30, { fill: '#c0392b', parent: stack.el, o: 1 });
    S.circle(0, -200, 14, { fill: '#3d4853', stroke: COL.ink, width: 3, parent: stack.el, o: 1 });
    S.rect(-14, -186, 28, 12, { fill: '#3d4853', parent: stack.el, o: 1 });
    const wh = S.rect(xs - 22, yWH, 44, yBed - yWH + 10, { fill: '#8d9cab', stroke: 'none' }); wh.in(B.start + 0.4, 0.5, 'none');
    E.anim(B.start, B.end, (t) => {
      const o = off(t), a = tilt(t);
      let d = '', dw = '';
      for (let x = 160; x <= 980; x += 10) { const yy = ySea + 7 * Math.sin(x * 0.035 + t * 2.1) + 4 * Math.sin(x * 0.07 - t * 1.4); d += `${x === 160 ? 'M' : 'L'}${x},${yy.toFixed(1)}`; }
      sea.el.setAttribute('d', d);
      water.el.setAttribute('d', d + ` L980,${yBed} L160,${yBed} Z`);
      rig.baseTf = `translate(${xs + o} ${ySea - 40 + 6 * Math.sin(t * 1.3)})`;
      // stack pivots about the wellhead datum
      const fjx = xs + Math.sin(a) * (yWH - yFJ), fjy = yWH - Math.cos(a) * (yWH - yFJ);
      stack.baseTf = `translate(${xs} ${yWH}) rotate(${(a * 180 / Math.PI).toFixed(3)})`;
      // riser: from rig (xs+o, ySea+20) to flex joint (fjx, fjy-14), a gentle catenary-ish curve
      const x0 = xs + o, y0 = ySea + 30;
      riser.el.setAttribute('d', `M${x0},${y0} C${x0},${y0 + 200} ${fjx},${fjy - 200} ${fjx},${fjy - 14}`);
    });
    // the chain, one numbered link per cue
    [['waves', 'waves move the rig'], ['vessel', 'the rig drags the riser top'], ['fj', 'the riser rotates in the lower flex joint'], ['stack', 'the stack sways like an inverted pendulum']]
      .forEach(([k, txt], i) => {
        const y = 260 + i * 100, t = c('3.1', k);
        S.div(`<div style="display:flex;align-items:center;gap:18px"><span class="num" style="width:44px;height:44px;border-radius:50%;border:2px solid #ffb547;color:#ffb547;font-size:22px;display:flex;align-items:center;justify-content:center">${i + 1}</span><span class="small" style="color:var(--ink)">${txt}</span></div>`,
          { x: 1120, y, anchor: 'lm' }).in(t, 0.5, 'left');
        if (i) S.path(`M1142,${y - 72} L1142,${y - 28}`, { stroke: 'rgba(255,181,71,0.55)', width: 2, dash: '4 5' }).in(t - 0.2, 0.4, 'none');
      });
    const mres = S.eq('\\Rightarrow\\; \\cm{M_w},\\;Q_w \\text{ at the wellhead datum}', { x: 1120, y: 690, size: 44, align: 'left' });
    mres.in(c('3.1', 'moment'), 0.7, 'write');
    const curl = S.path(`M${xs - 60},${yWH + 20} A60,40 0 1,0 ${xs + 60},${yWH + 20}`, { stroke: COL.amber, width: 4 });
    curl.in(c('3.1', 'moment'), 0.4, 'none');
  }

  // ------------------------------------------------------------------ 3.2 lever arm + 3.3 moment below the datum
  {
    const B2 = b('3.2'), B3 = b('3.3');
    const S = new Scene(B2.start, B3.end);
    clause('NORSOK U-001:2026 · Tables A.3, A.4, A.5 (footnotes)', B2.start + 0.4, B3.end);
    // FBD: datum at y 640, flex joint at y 230 (H), well continues below to y 900 (z)
    const x0 = 520, yD = 620, yF = 230, k = (yD - yF) / 13.7;
    const yMud = yD + 4 * k, yEnd = yMud + 140;
    const body = S.g(); body.in(B2.start + 0.3, 0.6, 'none');
    S.rect(x0 - 50, yF + 30, 100, yD - yF - 30, { fill: '#2c3f52', stroke: '#e7ae1c', width: 3, parent: body.el, o: 1 });
    S.circle(x0, yF + 14, 16, { fill: '#3d4853', stroke: COL.ink, width: 3, parent: body.el, o: 1 });
    S.svgText('lower flex joint', x0 + 34, yF + 14, { anchor: 'start', size: 22, fill: COL.ink2, parent: body.el, o: 1 });
    S.svgText('BOP stack', x0, (yF + yD) / 2, { size: 24, fill: COL.ink2, parent: body.el, o: 1 });
    const datum = S.line(x0 - 260, yD, x0 + 260, yD, { stroke: COL.amber, width: 2, dash: '10 8' }); datum.in(B2.start + 0.5, 0.5, 'none');
    S.svgText('wellhead datum', x0 - 270, yD - 18, { anchor: 'start', size: 20, fill: COL.amber, o: 0 }).in(B2.start + 0.5, 0.5, 'none');
    const Q = S.arrow(x0 - 200, yF + 14, x0 - 22, yF + 14, { color: COL.amber, width: 5, head: 20 }); Q.in(c('3.2', 'hinge'), 0.5, 'none');
    S.svgText('Q', x0 - 220, yF + 14, { size: 34, fill: COL.amber, anchor: 'end', o: 0, family: 'KaTeX_Math' }).in(c('3.2', 'hinge'), 0.5, 'none');
    const Hd = S.path(`M${x0 + 150},${yF + 14} L${x0 + 150},${yD}`, { stroke: COL.ink2, width: 2 }); Hd.in(c('3.2', 'hinge') + 0.4, 0.5, 'none');
    const Hlab = S.eq('H', { x: x0 + 180, y: (yF + yD) / 2, size: 40, align: 'left' }); Hlab.in(c('3.2', 'hinge') + 0.4, 0.5, 'none');
    const derv = derivation(S, [
      { tex: '\\textstyle\\sum M_{\\text{datum}} = 0:\\quad \\cm{M_w} = Q\\,H', t: c('3.2', 'eq'), x: 1000, align: 'left' },
      { tex: 'Q_w = \\dfrac{\\cm{M_w}}{H_{\\mathrm{LFJ}}}', t: c('3.2', 'eq') + 2.0, x: 1000, align: 'left', size: 58 },
    ], { y0: 300, gap: 130, size: 48 });
    derv[1].boxed(c('3.2', 'eq') + 4.2, { out: B3.start });
    const tA3 = table(S, ['Table A.3', 'standard design case'], [['H<sub>LFJ</sub> (datum → LFJ)', '≤ 13.7 m'], ['H<sub>XT</sub> (datum → re-entry hub)', '≤ 2.5 m']], { x: 1000, y: 560, w: 700, t: c('3.2', 'h137'), colCls: ['l', ''] });
    const xt = S.eq('\\text{BOP on XT: } Q_w = \\dfrac{\\cm{M_w}}{H_{\\mathrm{LFJ}}+H_{\\mathrm{XT}}}', { x: 1000, y: 800, size: 44, align: 'left' });
    xt.in(c('3.2', 'xt'), 0.7, 'write');
    // 3.3: below the datum
    for (const a of [...derv, tA3.card, xt]) a.out(B3.start, 0.5);
    const well = S.rect(x0 - 26, yD, 52, yEnd - yD, { fill: '#8d9cab', stroke: 'none' }); well.in(B2.start + 0.3, 0.6, 'none');
    const gr = ground(S, x0 - 260, x0 + 260, yMud); gr.in(B2.start + 0.3, 0.6, 'none');
    const cut = S.line(x0 - 90, yMud, x0 + 90, yMud, { stroke: COL.coral, width: 3, dash: '8 6' }); cut.in(c('3.3', 'mz') - 1.5, 0.5, 'none');
    S.svgText('z', x0 + 110, (yD + yMud) / 2, { size: 34, fill: COL.ink, family: 'KaTeX_Math', o: 0 }).in(c('3.3', 'mz') - 1.5, 0.5, 'none');
    const zd = S.path(`M${x0 + 90},${yD} L${x0 + 90},${yMud}`, { stroke: COL.ink2, width: 2 }); zd.in(c('3.3', 'mz') - 1.5, 0.5, 'none');
    // moment diagram growing linearly from the flex joint
    const md = S.path(`M${x0 - 60},${yF + 14} L${x0 - 60 - 0.0},${yF + 14} L${x0 - 60 - 230 * (13.7 + 4) / 13.7 * 0.75},${yMud} L${x0 - 60},${yMud} Z`, { fill: 'rgba(255,181,71,0.18)', stroke: COL.amber, width: 3 });
    md.in(c('3.3', 'mz') - 0.4, 0.8, 'none');
    md.el.setAttribute('d', `M${x0 - 60},${yF + 14} L${x0 - 60 - 172 * (yMud - yF - 14) / (yD - yF - 14)},${yMud} L${x0 - 60},${yMud} Z`);
    const e1 = S.eq('\\cm{M}(z) = Q\\,(H+z) = \\cm{M_w}\\left(1+\\dfrac{z}{H}\\right)', { x: 1000, y: 360, size: 50, align: 'left' });
    e1.in(c('3.3', 'mz'), 0.8, 'write');
    e1.boxed(c('3.3', 'mz') + 2.6);
    const e2 = S.eq('z = 4\\text{ m}:\\quad \\cm{M} = \\cm{M_w}\\left(1+\\tfrac{4}{13.7}\\right) = 1.29\\,\\cm{M_w}', { x: 1000, y: 560, size: 46, align: 'left' });
    e2.in(c('3.3', 'mud'), 0.8, 'write');
    S.div('mudline', { x: x0 + 270, y: yMud, cls: 'tiny', anchor: 'lm' }).in(c('3.3', 'mud'), 0.5);
  }

  // ------------------------------------------------------------------ 3.4 static vs fatigue
  {
    const B = b('3.4');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · A.3.1, A.3.3', B.start + 0.3, B.end);
    const t4 = table(S, ['Water depth [m]', 'ULS M<sub>W</sub> [kNm]', 'Q<sub>W</sub> [kN]', 'ALS M<sub>W</sub> [kNm]'],
      L.tableA4.map((r) => [r[0], fmt(r[1]), fmt(r[2]), fmt(r[4])]), { x: 120, y: 250, w: 780, t: B.start + 0.3, title: 'Table A.4 · ULS / ALS wellhead loads, BOP on WH', colCls: ['l', '', '', ''] });
    const tag = S.div('<span class="badge">static design</span>', { x: 160, y: 560 }); tag.in(c('3.4', 'static'), 0.5, 'pop');
    t4.card.to(c('3.4', 'fat'), 0.6, { o: 0.35 });
    quoteCard(S, 'A.3.1', 'For the purpose of fatigue design, fatigue loads are specified in terms of a <span class="q">single-load bending moment range</span> and a <span class="q">general bending moment fatigue histogram</span>.', { x: 1000, y: 300, w: 800, t: c('3.4', 'fat'), size: 32 });
  }

  // ------------------------------------------------------------------ 3.5 Table A.7
  {
    const B = b('3.5');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · Table A.7', B.start + 0.3, B.end);
    S.div('Annual WH single-load bending moment range ΔM<sub>o</sub> · DF = 1', { x: 960, y: 170, cls: 'h3', anchor: 'ct' }).in(c('3.5', 'a7'), 0.6, 'write');
    const bands = ['80 – 250 m', '250 – 500 m', '500 – 1500 m'];
    const keys = ['80-250', '250-500', '500-1500'];
    const x0 = 520, w1 = 0.42;   // px per kNm
    keys.forEach((k, i) => {
      const y = 300 + i * 200;
      S.div(bands[i], { x: x0 - 40, y: y + 30, cls: 'h3', anchor: 'rm' }).in(c('3.5', 'a7') + 0.3 + i * 0.25, 0.5, 'left');
      for (const [j, mode, col] of [[0, 'BOP on WH', COL.amber], [1, 'BOP on XT', COL.coral]]) {
        const v = L.tableA7[mode][k];
        const yy = y + j * 64;
        const bar = S.div('', { x: x0, y: yy, w: v * w1, h: 48, style: `background:linear-gradient(90deg, ${col}cc, ${col}66);border-radius:8px` });
        bar.el.style.transformOrigin = '0 50%';
        const tb = j === 0 ? c('3.5', 'a7') + 0.6 + i * 0.25 : c('3.5', 'xtmode') - 0.2 + i * 0.2;
        bar.set(0, { sx: 0 }).to(tb, 0.9, { sx: 1 }, ease.out3).in(tb, 0.2, 'none');
        S.div(`<span class="num" style="font-size:30px">${fmt(v)}</span> <span class="tiny">kNm · ${mode}</span>`, { x: x0 + v * w1 + 18, y: yy + 24, anchor: 'lm' }).in(tb + 0.6, 0.5);
      }
    });
    const hl = S.div('', { x: 140, y: 284, w: 1660, h: 160, cls: 'hl' }); hl.in(c('3.5', 'shallow'), 0.5, 'pop');
    S.div('shallow water: short, stiff riser → largest moments', { x: 1790, y: 270, cls: 'small', anchor: 'rb', style: 'color:#ffb547' }).in(c('3.5', 'shallow') + 0.3, 0.5);
  }

  // ------------------------------------------------------------------ 3.6 Table A.8  +  3.7 scaling
  {
    const B6 = b('3.6'), B7 = b('3.7');
    const S = new Scene(B6.start, B7.end);
    clause('NORSOK U-001:2026 · Table A.8 · A.3.5.1', B6.start + 0.3, B7.end);
    const cc = S.chart({ x: 230, y: 190, w: 1000, h: 620, ylog: true, xmin: 0, xmax: 3.0, ymin: 0.5, ymax: 1e7,
      xticks: [0.5, 1.0, 1.5, 2.0, 2.5, 3.0], yticks: logTicks(1, 1e7), xfmt: (v) => v.toFixed(1), yfmt: pow10, ylabel: 'cycles per year' });
    cc.show(c('3.6', 'a8'));
    const xl = S.div('normalised bending moment range  r', { x: 730, y: 870, cls: 'small', anchor: 'cm' }); xl.in(c('3.6', 'a8'), 0.5); xl.out(c('3.7', 'mult') + 0.6, 0.4);
    const xl2 = S.div('bending moment range at the WH datum  ΔM = r · ΔM<sub>o</sub>  [kNm]', { x: 730, y: 870, cls: 'small', anchor: 'cm', style: 'color:#ffb547' }); xl2.in(c('3.7', 'mult') + 0.8, 0.5);
    const bw = 1000 / 3.0 * 0.1 * 0.78;
    L.tableA8.forEach((r, i) => {
      const x = cc.X(r.r) - bw / 2, y = cc.Y(r.n), h = cc.Y(0.5) - y;
      const bar = S.rect(x, y, bw, h, { fill: i === 0 ? COL.cyan : 'rgba(79,209,255,0.55)', stroke: 'none', rx: 3, parent: cc.plot });
      bar.el.style.transformOrigin = `${x}px ${cc.Y(0.5)}px`; bar.el.style.transformBox = 'view-box';
      bar.set(0, { sy: 0 }).to(c('3.6', 'a8') + 0.8 + i * 0.06, 0.6, { sy: 1 }, ease.out3).in(c('3.6', 'a8') + 0.8 + i * 0.06, 0.2, 'none');
    });
    // x-axis kNm labels for the scaled histogram (overlay the normalised tick labels)
    const ticks2 = S.g(); ticks2.in(c('3.7', 'mult') + 0.8, 0.5, 'none');
    const blank = S.rect(cc.x - 20, cc.y + cc.h + 8, cc.w + 40, 34, { fill: '#08182a', stroke: 'none', parent: ticks2.el, o: 1 });
    for (const v of [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]) S.svgText(fmt(v * 1436), cc.X(v), cc.y + cc.h + 26, { size: 20, fill: COL.amber, parent: ticks2.el, o: 1 });
    S.div('3 948 892 cycles at r = 0.1', { x: cc.X(0.1) + 20, y: cc.Y(3948892) - 10, cls: 'small', anchor: 'lb', style: 'color:#4fd1ff' }).in(c('3.6', 'small'), 0.5, 'left');
    S.div('1 cycle at 2.8 and 2.9', { x: cc.X(2.85), y: cc.Y(1) - 70, cls: 'small', anchor: 'cb' }).in(c('3.6', 'big'), 0.5);
    const tot = counter(S, { x: 1520, y: 330, a: 0, b: L.n_total, t0: c('3.6', 'total'), t1: c('3.6', 'total') + 2.2, size: 64, color: COL.cyan });
    tot.in(c('3.6', 'total') - 0.1, 0.4);
    S.div('cycles per year in total · one every ≈ 4.2 s', { x: 1520, y: 395, cls: 'small', anchor: 'cm' }).in(c('3.6', 'total') + 0.6, 0.5);
    tot.out(B7.start, 0.4);
    // 3.7 equations
    const e1 = S.eq('\\cm{\\Delta M_i} = r_i \\times \\cm{\\Delta M_o}', { x: 1520, y: 300, size: 56 });
    e1.in(c('3.7', 'mult'), 0.7, 'write');
    const e2 = S.eq('0.1 \\times 2124 = 212.4\\ \\text{kNm}', { x: 1520, y: 450, size: 46 });
    e2.in(c('3.7', 'ex1'), 0.7, 'write');
    S.div('Example 1, A.3.5.1 · 80–250 m · 3 948 892 cycles', { x: 1520, y: 510, cls: 'tiny', anchor: 'cm' }).in(c('3.7', 'ex1') + 0.4, 0.5);
    const e3 = S.card(`<div class="ref">OUR EXAMPLE WELL</div><div style="font-size:28px;font-weight:650;line-height:1.5">350 m · BOP on WH<br><span class="c-amber num" style="font-size:40px">ΔM<sub>o</sub> = 1 436 kNm</span><br><span class="small">bins from 143.6 to 4 164 kNm</span></div>`, { x: 1290, y: 600, w: 470 });
    e3.in(c('3.7', 'ours'), 0.6);
  }

  // ------------------------------------------------------------------ 3.8 fatigue service life
  {
    const B = b('3.8');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · A.3.5.1 note 1 · A.3.5.2 · A.3.5.3', B.start + 0.3, B.end);
    const e = S.eq('\\text{fatigue service life} = \\dfrac{\\text{fatigue life}}{\\cg{D_F}}', { x: 960, y: 270, size: 60 });
    e.in(c('3.8', 'svc'), 0.8, 'write');
    const n = S.div('≡ permissible operational days with a BOP and marine drilling riser connected to the wellhead or XT', { x: 960, y: 380, w: 1300, cls: 'body', anchor: 'ct', style: 'text-align:center;color:#e9f2f9' });
    n.in(c('3.8', 'svc') + 1.8, 0.6);
    const card = (x, ref, title, body, t) => { const a = S.card(`<div class="ref">${ref}</div><div style="font-weight:750;font-size:30px;margin-bottom:8px">${title}</div><div class="small">${body}</div>`, { x, y: 560, w: 520 }); a.in(t, 0.6); return a; };
    card(120, 'A.3.5.2 · templates', 'Minimum 1 year', 'in the area of riser load transfer between the wellhead system and the template well slot · DFF per NORSOK N-001', c('3.8', 'min'));
    card(700, 'A.3.5.3 · wellhead systems', 'Minimum 1 year', 'pressure-containing and primary structural components in the riser load path · DF per Annex B', c('3.8', 'min') + 0.4);
    card(1280, 'A.3.5.1', 'VIV not included', 'fatigue damage from vortex induced vibration shall be added when applicable (API STD 2RD, DNV-RP-F204)', c('3.8', 'viv'));
  }
}
