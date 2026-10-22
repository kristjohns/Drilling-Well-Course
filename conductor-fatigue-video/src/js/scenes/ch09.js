// Chapter 9 — the worked example (illustrative inputs).
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause, step } from '../engine/hud.js';
import { quoteCard, derivation, table, tx, counter, stamp } from './kit.js';
import { logTicks, pow10 } from './fatigue.js';

const sciS = (x) => { if (!x) return '∞'; const e = Math.floor(Math.log10(x)); return `${(x / 10 ** e).toFixed(2)}×10<sup>${e}</sup>`; };

export async function build(E, T, D) {
  const ch = T.ch(9);
  titleCard(ch, 'All eight steps on one illustrative well');
  step(ch.title_card[1], 6);
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const ex = D.example, inp = ex.inputs, L = D.loads, S9 = D.sensitivity;
  const g = ex.miner_gw, ts = ex.miner_T;

  // ------------------------------------------------------------------ 9.1 the example well
  {
    const B = b('9.1');
    const S = new Scene(B.start, B.end);
    const il = '<span style="color:#7f97aa">illustrative</span>';
    const rows = [
      ['Water depth · mode', '350 m · BOP on WH', 'Table A.7'], ['ΔM<sub>o</sub> · H<sub>LFJ</sub>', '1 436 kNm · 13.7 m', 'Tables A.7, A.3'],
      ['Conductor · surface casing', '36 in × 2 in · 20 in × 1 in', 'Table A.1'], ['WH datum above mudline', '4.0 m', il],
      ['Template rings C, D', '1.6 m and 3.6 m below datum · 200 / 400 MN/m · 2 mm gap', il], ['Soil · cement shortfall', 'k = 5 MPa (Winkler) · 5 m', il],
      ['GW1', '3.0 m below datum · C1 seawater + CP · SCF 1.10 · t = 50.8 mm', '13.3.6.2 · SCF ' + il], ['TS1', 'class D seawater + CP · 0.156 MPa per kN', il],
      ['Design factors', 'D<sub>F</sub> = 10 (permanent) · DFF = 10 (N-001)', 'Table B.4 · N-001'],
    ];
    const tb = table(S, ['Input', 'Value', 'Source'], rows, { x: 120, y: 230, t: c('9.1', 'inputs'), stagger: 0.18, colCls: ['l', 'l', 'l'] });
    tb.el.querySelectorAll('th, td').forEach((e) => { e.style.paddingLeft = '22px'; e.style.paddingRight = '22px'; });
    later(() => { tb.el.style.left = (960 - tb.el.offsetWidth / 2) + 'px'; });
    const fl = S.div('<span class="badge warn">illustrative teaching inputs · not project data</span>', { x: 960, y: 960, anchor: 'cm' });
    fl.in(c('9.1', 'flag'), 0.5, 'pop');
  }

  // ------------------------------------------------------------------ 9.2 + 9.3 histogram and screening
  {
    const B2 = b('9.2'), B3 = b('9.3');
    const S = new Scene(B2.start, B3.end);
    step(B2.start, 0);
    const cc = S.chart({ x: 160, y: 200, w: 760, h: 520, ylog: true, xmin: 0, xmax: 4400, ymin: 0.5, ymax: 1e7, xticks: [0, 1000, 2000, 3000, 4000], yticks: logTicks(1, 1e7), xfmt: (v) => fmt(v), yfmt: pow10, xlabel: 'ΔM<sub>i</sub> = r<sub>i</sub> × 1 436 kNm', ylabel: 'cycles per year', title: 'STEP 1 · THE ANNUAL HISTOGRAM' });
    cc.show(c('9.2', 'hist'));
    const bw = cc.w / 4400 * 143.6 * 0.8;
    L.hist.forEach((h, i) => {
      const x = cc.X(h.dM) - bw / 2, y = cc.Y(h.n);
      const r = S.rect(x, y, bw, cc.Y(0.5) - y, { fill: 'rgba(255,181,71,0.7)', stroke: 'none', rx: 2, parent: cc.plot });
      r.el.style.transformOrigin = `${x}px ${cc.Y(0.5)}px`; r.el.style.transformBox = 'view-box';
      r.set(0, { sy: 0 }).to(c('9.2', 'hist') + 0.3 + i * 0.04, 0.5, { sy: 1 }, ease.out3).in(c('9.2', 'hist') + 0.3 + i * 0.04, 0.1, 'none');
    });
    // screening
    step(B3.start, 7);
    const sc = ex.screen_gw;
    const st = derivation(S, [
      { tex: '\\DM_c = ' + fmt(sc.dMc) + '\\ \\text{kNm}', t: c('9.3', 'screen'), x: 1080, align: 'left' },
      { tex: '\\dfrac{\\DM_c}{\\cg{10}^{1/3}} = ' + fmt(sc.dMc_over_DF) + ' \\;<\\; ' + fmt(sc.dMo) + ' = \\DM_o', t: c('9.3', 'screen') + 2.6, x: 1080, align: 'left', size: 46 },
      { tex: 'T_f = \\left(\\tfrac{' + fmt(sc.dMc) + '}{' + fmt(sc.dMo) + '}\\right)^{3} = ' + sc.life_linear_m3.toFixed(1) + '\\ \\text{yr} \\;\\Rightarrow\\; \\tfrac{T_f}{\\cg{D_F}} = ' + (sc.life_linear_m3 / 10).toFixed(2) + '\\ \\text{yr}', t: c('9.3', 'fail') + 1.6, x: 1080, align: 'left', size: 40 },
    ], { y0: 280, gap: 150, size: 48 });
    stamp(S, 'SCREENING FAILS', { x: 1430, y: 760, t: c('9.3', 'fail'), kind: 'fail' });
    const np = S.div('…but the screening uses slope 3 for every cycle. Most cycles live on the flatter slope 5.', { x: 1080, y: 850, w: 740, cls: 'small' });
    np.in(c('9.3', 'nopanic'), 0.6);
  }

  // ------------------------------------------------------------------ 9.4 the Miner sum for GW1
  {
    const B = b('9.4');
    const S = new Scene(B.start, B.end);
    step(B.start, 5);
    const rows = g.rows;
    const tot = rows.reduce((s, r) => s + r.d, 0);
    // damage density chart (left) and a compact table of the top bins (right)
    const cc = S.chart({ x: 160, y: 200, w: 900, h: 540, xmin: 0, xmax: 4400, ymin: 0, ymax: 14, xticks: [0, 1000, 2000, 3000, 4000], yticks: [0, 5, 10], xfmt: (v) => fmt(v), yfmt: (v) => v + ' %', xlabel: 'ΔM<sub>i</sub> [kNm]', ylabel: 'share of the damage', title: 'WHERE THE DAMAGE COMES FROM · GW1' });
    cc.show(c('9.4', 'table'));
    const bw = cc.w / 4400 * 143.6 * 0.8;
    rows.forEach((r, i) => {
      const v = 100 * r.d / tot, x = cc.X(r.dM) - bw / 2, y = cc.Y(v);
      const mid = r.dM >= 1000 && r.dM <= 2300;
      const rr = S.rect(x, y, bw, cc.Y(0) - y, { fill: mid ? COL.coral : 'rgba(255,111,97,0.45)', stroke: 'none', rx: 2, parent: cc.plot });
      rr.el.style.transformOrigin = `${x}px ${cc.Y(0)}px`; rr.el.style.transformBox = 'view-box';
      rr.set(0, { sy: 0 }).to(c('9.4', 'table') + 0.6 + i * 0.07, 0.5, { sy: 1 }, ease.out3).in(c('9.4', 'table') + 0.6 + i * 0.07, 0.1, 'none');
    });
    const band = S.rect(cc.X(1000), cc.y, cc.X(2300) - cc.X(1000), cc.h, { fill: 'rgba(255,111,97,0.08)', stroke: 'rgba(255,111,97,0.5)', width: 2, rx: 6 });
    band.in(c('9.4', 'mid'), 0.5, 'none');
    S.div('← 1 000 – 2 300 kNm do most of the work', { x: cc.X(2330), y: cc.Y(9.5), cls: 'small', anchor: 'lm', style: 'color:#ff6f61' }).in(c('9.4', 'mid') + 0.3, 0.5);
    const lx = cc.X(143.6), ly = cc.Y(0) + 96;
    S.path(`M${lx},${cc.Y(0) + 6} L${lx},${ly - 14}`, { stroke: COL.dim, width: 1.5 }).in(c('9.4', 'where'), 0.5, 'none');
    S.div('3.9 million cycles at 144 kNm do almost nothing', { x: lx - 8, y: ly, cls: 'tiny', anchor: 'lm' }).in(c('9.4', 'where'), 0.5);
    const top = [...rows].sort((a, b2) => b2.d - a.d).slice(0, 6).sort((a, b2) => a.dM - b2.dM);
    const tb = table(S, ['ΔM<sub>i</sub>', 'n<sub>i</sub>', 'N<sub>i</sub>', 'n<sub>i</sub>/N<sub>i</sub>'], top.map((r) => [fmt(r.dM), fmt(r.n), sciS(r.N), r.d.toFixed(4)]), { x: 1150, y: 170, w: 650, t: c('9.4', 'table') + 1.0, title: 'largest contributions (of 29 bins)' });
    const e1 = S.eq('D_{\\text{year}} = \\sum_{i=1}^{29}\\dfrac{n_i}{\\cn{N_i}} = ' + g.D.toFixed(4), { x: 1150, y: 730, size: 40, align: 'left' });
    e1.in(c('9.4', 'total'), 0.7, 'write');
    const e2 = S.eq('T_f = \\dfrac{1}{' + g.D.toFixed(4) + '} = ' + g.life.toFixed(1) + '\\ \\text{yr}', { x: 1150, y: 856, size: 40, align: 'left' });
    e2.in(c('9.4', 'life'), 0.7, 'write');
    const e3 = S.eq('\\dfrac{T_f}{\\cg{D_F}} = ' + g.service.toFixed(2) + '\\ \\text{yr} \\approx ' + fmt(g.days) + '\\ \\text{days}', { x: 1150, y: 972, size: 44, align: 'left' });
    e3.in(c('9.4', 'svc'), 0.7, 'write');
    stamp(S, 'GW1 PASSES · ≥ 1 YEAR', { x: 600, y: 900, t: c('9.4', 'pass'), kind: 'pass' });
  }

  // ------------------------------------------------------------------ 9.5 linear vs bilinear + 9.6 TS1
  {
    const B5 = b('9.5'), B6 = b('9.6');
    const S = new Scene(B5.start, B6.end);
    const vals = [['screening, single slope at 10⁶', ex.screen_gw.life_linear_m3, COL.red], ['full sum, single slope 3', ex.miner_gw_linear, COL.amber], ['full sum, bilinear curve', g.life, COL.green]];
    const x0 = 560, wmax = 1100, vmax = 16;
    vals.forEach(([lab, v, col], i) => {
      const y = 280 + i * 130;
      S.div(lab, { x: x0 - 30, y: y + 32, cls: 'body', anchor: 'rm', style: 'color:#e9f2f9' }).in(c('9.5', 'three') + i * 0.5, 0.5, 'left');
      const bar = S.div('', { x: x0, y, w: wmax * v / vmax, h: 64, style: `background:${col};border-radius:10px` });
      bar.el.style.transformOrigin = '0 50%';
      bar.set(0, { sx: 0 }).to(c('9.5', 'three') + i * 0.5, 0.8, { sx: 1 }, ease.out3).in(c('9.5', 'three') + i * 0.5, 0.1, 'none');
      S.div(`<span class="num" style="font-size:34px">${v.toFixed(1)} yr</span>`, { x: x0 + wmax * v / vmax + 20, y: y + 32, anchor: 'lm' }).in(c('9.5', 'three') + i * 0.5 + 0.6, 0.4);
    });
    S.div('fatigue life of GW1 (D<sub>F</sub> = 1) · each step removes a layer of conservatism', { x: x0, y: 690, cls: 'small' }).in(c('9.5', 'lesson'), 0.6);
    // 9.6 TS1
    const card = S.card(`<div class="ref">TS1 · template slot weld · DFF = 10 (N-001)</div>
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-top:6px;padding-right:30px">
      <div><div class="tiny">damage per year</div><div class="num" style="font-size:44px">${ts.D.toFixed(4)}</div></div>
      <div><div class="tiny">fatigue life</div><div class="num" style="font-size:44px">${ts.life.toFixed(1)} yr</div></div>
      <div><div class="tiny">service life</div><div class="num c-green" style="font-size:44px">${ts.service.toFixed(2)} yr</div></div></div>`, { x: 560, y: 780, w: 900 });
    card.in(c('9.6', 'ts'), 0.6);
    stamp(S, 'TS1 PASSES', { x: 1720, y: 860, t: c('9.6', 'pass'), kind: 'pass' });
  }

  // ------------------------------------------------------------------ 9.7 the load-share trade-off
  {
    const B = b('9.7');
    const S = new Scene(B.start, B.end);
    step(B.start, 7);
    clause('NORSOK U-001:2026 · 8.1 (load share for fatigue performance)', B.start + 0.3, B.end);
    const gp = S9.gap;   // [gap mm, {gw, T}]
    const cc = S.chart({ x: 220, y: 200, w: 900, h: 640, ylog: true, xmin: 0, xmax: 8, ymin: 0.1, ymax: 20, xticks: [0, 1, 2, 4, 8], yticks: [0.1, 0.3, 1, 3, 10], xfmt: (v) => v + ' mm', yfmt: String, xlabel: 'radial gap in the template slot', ylabel: 'fatigue service life [years]', title: 'MOVE THE GAP' });
    cc.show(B.start + 0.3);
    const one = S.line(cc.X(0), cc.Y(1), cc.X(8), cc.Y(1), { stroke: COL.green, width: 3, dash: '10 8' }); one.in(B.start + 0.6, 0.5, 'none');
    S.div('1 year minimum', { x: cc.X(8) - 10, y: cc.Y(1) + 12, cls: 'small', anchor: 'rt', style: 'color:#46d39a' }).in(B.start + 0.8, 0.5);
    const gwPts = gp.map(([x, v]) => [x, v.gw / 10]), tsPts = gp.map(([x, v]) => [x, v.T / 10]);
    cc.curve(gwPts, { color: COL.amber, width: 5, t: c('9.7', 'gap') });
    cc.curve(tsPts, { color: COL.lemon, width: 5, t: c('9.7', 'gap') + 0.4 });
    gwPts.forEach((p) => cc.dot(p[0], p[1], { color: COL.amber, r: 7, t: c('9.7', 'gap') + 0.8 }));
    tsPts.forEach((p) => cc.dot(p[0], p[1], { color: COL.lemon, r: 7, t: c('9.7', 'gap') + 1.0, stroke: '#3b2a00' }));
    S.div('GW1 conductor', { x: cc.X(0.2), y: cc.Y(gwPts[0][1]) - 18, cls: 'small', anchor: 'lb', style: 'color:#ffb547' }).in(c('9.7', 'gw'), 0.5);
    S.div('TS1 template', { x: cc.X(0.25), y: cc.Y(tsPts[0][1]) + 16, cls: 'small', anchor: 'lt', style: `color:${COL.lemon}` }).in(c('9.7', 'tsfail'), 0.5);
    const nt = S9.no_template;
    const card = S.card(`<div class="ref">no template contact at all</div><div class="num" style="font-size:40px">GW1 · <span class="c-red">${(nt.gw / 10).toFixed(2)} yr</span></div>`, { x: 1220, y: 300, w: 560 });
    card.in(c('9.7', 'none'), 0.6);
    const ls = S.div('Load share moves damage around.<br>It never deletes it.', { x: 1220, y: 560, cls: 'h2', style: 'color:#ffb547' });
    ls.in(c('9.7', 'lesson'), 0.8, 'write');
  }

  // ------------------------------------------------------------------ 9.8 sensitivities (tornado)
  {
    const B = b('9.8');
    const S = new Scene(B.start, B.end);
    const base = g.service;
    // [row, longer-life case, its value, shorter-life case, its value, cue]
    const ent = [
      ['SCF at GW1', 'SCF 1.0', S9.SCF.find((r) => r[0] === 1.0)[1].gw / 10, 'SCF 1.2', S9.SCF.find((r) => r[0] === 1.2)[1].gw / 10, 'scf'],
      ['water depth', '500–1500 m', S9.band['500-1500'].gw / 10, '80–250 m', S9.band['80-250'].gw / 10, 'depth'],
      ['BOP mode (250–500 m)', '', base, 'BOP on XT', S9.xt_mode['250-500'].gw / 10, 'xt'],
      ['soil stiffness', 'k = 2 MPa', S9.k_soil.find((r) => r[0] === 2)[1].gw / 10, 'k = 20 MPa', S9.k_soil.find((r) => r[0] === 20)[1].gw / 10, 'soil'],
      ['cement shortfall', '0 m', S9.shortfall.find((r) => r[0] === 0)[1].gw / 10, '15 m', S9.shortfall.find((r) => r[0] === 15)[1].gw / 10, 'soil'],
    ];
    const X = (v) => 960 + 560 * Math.log10(v / base);        // log scale: equal factors, equal lengths
    S.div('GW1 fatigue service life [years] · base case · log scale', { x: 960, y: 150, cls: 'small', anchor: 'cm' }).in(c('9.8', 'tornado'), 0.5);
    const axis = S.line(X(base), 220, X(base), 900, { stroke: COL.ink2, width: 3 }); axis.in(c('9.8', 'tornado'), 0.5, 'none');
    S.div(base.toFixed(2), { x: X(base), y: 920, cls: 'num', anchor: 'ct', style: 'font-size:28px' }).in(c('9.8', 'tornado'), 0.5);
    const one = S.line(X(1), 220, X(1), 900, { stroke: COL.green, width: 2, dash: '8 6' }); one.in(c('9.8', 'tornado'), 0.5, 'none');
    S.div('1 yr', { x: X(1), y: 205, cls: 'tiny', anchor: 'cb', style: 'color:#46d39a' }).in(c('9.8', 'tornado'), 0.5);
    ent.forEach(([lab, hiCase, hi, loCase, lo, cue], i) => {
      const y = 260 + i * 125, t = c('9.8', cue) - 0.3 + (cue === 'soil' && i === 4 ? 0.6 : 0);
      S.div(lab, { x: 120, y: y + 30, cls: 'small', anchor: 'lm', style: 'color:#e9f2f9' }).in(t, 0.5, 'left');
      // each bar end carries its value and the case that gives it
      const seg = (v, cs, col) => {
        if (Math.abs(v - base) < 0.005) return;
        const x0 = Math.min(X(base), X(v)), w = Math.abs(X(v) - X(base)), right = v > base;
        S.div('', { x: x0, y, w: Math.max(w, 2), h: 60, style: `background:${col};border-radius:6px;opacity:0.9` }).in(t, 0.5, 'none');
        S.div(`<div class="num" style="font-size:24px">${v.toFixed(2)}</div><div class="tiny" style="color:#9fb3c4;margin-top:2px">${cs}</div>`,
          { x: X(v) + (right ? 12 : -12), y: y + 30, anchor: right ? 'lm' : 'rm', style: `text-align:${right ? 'left' : 'right'};line-height:1.15;background:rgba(10,21,32,0.9);box-shadow:0 0 10px 6px rgba(10,21,32,0.9);border-radius:6px` }).in(t + 0.3, 0.4);
      };
      seg(hi, hiCase, 'rgba(70,211,154,0.75)'); seg(lo, loCase, 'rgba(255,77,94,0.8)');
    });
  }

  // ------------------------------------------------------------------ 9.9 mitigation
  {
    const B = b('9.9');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · 13.2 · Table J.1 · J.4.3 · NORSOK U-009', B.start + 0.3, B.end);
    const sh = S9.band['80-250'], lr = S9.load_relief.find((r) => r[0] === 0.6)[1];
    const c1 = S.card(`<div class="ref">shallow water · 80–250 m</div><div style="font-size:28px;line-height:1.6">GW1 <span class="num c-red">${(sh.gw / 10).toFixed(2)} yr</span> · TS1 <span class="num c-red">${(sh.T / 10).toFixed(2)} yr</span><br>with 40 % load relief: GW1 <span class="num c-green">${(lr.gw / 10).toFixed(2)} yr</span> · TS1 <span class="num c-green">${(lr.T / 10).toFixed(2)} yr</span></div>`, { x: 120, y: 220, w: 820 });
    c1.in(c('9.9', 'relief'), 0.6);
    const c2 = S.card('<div class="ref">13.2</div><div style="font-weight:750;font-size:30px">Lateral BOP support</div><div class="small">the template may be prepared for, or equipped with, a system for lateral BOP support to extend wellhead fatigue life (OMAE2023-104891)</div>', { x: 980, y: 220, w: 820 });
    c2.in(c('9.9', 'relief') + 0.8, 0.6);
    const c3 = S.card('<div class="ref">Table J.1 · operational levers</div><div class="small" style="line-height:1.6;display:grid;grid-template-columns:1fr 1fr;column-gap:36px;margin-top:4px"><div class="hang">• less LMRP overpull</div><div class="hang">• lower drill pipe tension</div><div class="hang">• softer lower flex joint</div><div class="hang">• lighter stack</div><div class="hang">• avoid beam seas (DP rigs)</div><div></div><div class="hang" style="grid-column:1 / span 2">• riser tally: no buoyancy near the top in shallow water</div></div>', { x: 120, y: 520, w: 820 });
    c3.in(c('9.9', 'j1'), 0.6);
    const c4 = S.card('<div class="ref">J.4.3 · J.4.4.3 · NORSOK U-009</div><div style="font-weight:750;font-size:30px">Monitor, update, extend</div><div class="small">measure wellhead motion or bending; replace the design histogram with measured loads; update fatigue life calculations and extend life</div>', { x: 980, y: 520, w: 820 });
    c4.in(c('9.9', 'monitor'), 0.6);
  }
}
