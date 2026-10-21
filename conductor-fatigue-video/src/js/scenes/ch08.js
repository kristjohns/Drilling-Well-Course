// Chapter 8 — damage, life and the design check: Miner, B.3/B.4, Table B.4, N-001 DFF, B.14, B.13/B.12, the screening check.
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt } from '../engine/core.js';
import { Scene } from '../engine/scene.js';
import { titleCard, clause, step } from '../engine/hud.js';
import { quoteCard, derivation, table, tx, counter } from './kit.js';
import { mnCurve, logTicks, pow10 } from './fatigue.js';

export async function build(E, T, D) {
  const ch = T.ch(8);
  titleCard(ch, 'Steps 6 and 7 · Palmgren–Miner, design factors and the formulas of B.4.4');
  step(ch.title_card[1], 5);
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const ex = D.example, gw = ex.mn_gw, L = D.loads;

  // ------------------------------------------------------------------ 8.1 Palmgren-Miner
  {
    const B = b('8.1');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · 3.2.21 fatigue failure: Miner’s sum = 1.0', B.start + 0.3, B.end);
    const st = derivation(S, [
      { tex: '\\text{one cycle:}\\;\\; \\dfrac{1}{\\cn{N_i}}', t: c('8.1', 'one'), x: 260, align: 'left', size: 50 },
      { tex: 'n_i \\text{ cycles:}\\;\\; \\dfrac{n_i}{\\cn{N_i}}', t: c('8.1', 'ni'), x: 760, align: 'left', size: 50 },
      { tex: 'D = \\sum_{i=1}^{k} \\dfrac{n_i}{\\cn{N_i}}, \\qquad \\text{failure at } D = 1', t: c('8.1', 'sum'), size: 62 },
    ], { y0: 280, gap: 0, size: 50 });
    st[1].ay = 280; st[2].ay = 560;
    st[2].boxed(c('8.1', 'fail'));
    // life bar
    const x0 = 260, w = 1400, y = 780;
    S.rect(x0, y, w, 64, { fill: 'rgba(255,255,255,0.04)', stroke: COL.line, width: 2, rx: 12 }).in(c('8.1', 'sum'), 0.5, 'none');
    const rows = ex.miner_gw.rows, Dtot = ex.miner_gw.D;
    let acc = 0;
    const segs = rows.map((r, i) => { const s0 = acc; acc += r.d / Dtot; return { s0, s1: acc, i }; });
    segs.forEach((sg, k) => {
      const hue = 30 + 170 * (k / segs.length);
      const rr = S.rect(x0 + w * sg.s0, y + 4, Math.max(1, w * (sg.s1 - sg.s0)), 56, { fill: `hsl(${hue},80%,60%)`, stroke: 'none', rx: 2 });
      rr.in(c('8.1', 'sum') + 0.4 + k * 0.08, 0.3, 'none');
    });
    S.div('D = 1 · the whole life is used up', { x: x0 + w, y: y + 90, cls: 'small', anchor: 'rt' }).in(c('8.1', 'fail'), 0.5);
    S.div('each colour = one moment range bin · order does not matter', { x: x0, y: y + 90, cls: 'tiny' }).in(c('8.1', 'sum') + 1.5, 0.5);
  }

  // ------------------------------------------------------------------ 8.2 damage -> life, design format, Table B.4
  {
    const B = b('8.2');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.2.6 · formulas (B.3), (B.4) · Table B.4', B.start + 0.3, B.end);
    const e1 = S.eq('T_f = \\dfrac{1\\ \\text{year}}{D_{\\text{year}}}', { x: 480, y: 290, size: 58 });
    e1.in(c('8.2', 'inv'), 0.7, 'write');
    const e2 = S.eq('\\text{Service life} \\le \\dfrac{\\text{Fatigue life}}{\\cg{D_F}}\\quad\\text{(B.3)}', { x: 1300, y: 290, size: 48 });
    e2.in(c('8.2', 'b3'), 0.8, 'write');
    const e3 = S.eq('\\text{Inspection interval} \\le \\dfrac{\\text{Fatigue life}}{\\cg{D_F}}\\quad\\text{(B.4)}', { x: 1300, y: 430, size: 44 });
    e3.in(c('8.2', 'b4'), 0.8, 'write');
    const tb = table(S, ['Permanent equipment', 'Temporary equipment', ''], [['Service life', 'Service life', 'Inspection interval'], ['<span class="c-green" style="font-size:40px">10</span>', '<span class="c-green" style="font-size:40px">3</span>', '<span class="c-green" style="font-size:40px">10</span>']],
      { x: 420, y: 560, w: 1080, t: c('8.2', 'table'), title: 'Table B.4 · S-N method fatigue design factor D<sub>F</sub>', colCls: ['', '', ''] });
    S.div('a: it is assumed that inspection of all permanent equipment is not performed', { x: 440, y: 880, cls: 'tiny' }).in(c('8.2', 'table') + 0.8, 0.5);
  }

  // ------------------------------------------------------------------ 8.3 template DFF (N-001)
  {
    const B = b('8.3');
    const S = new Scene(B.start, B.end);
    clause('NORSOK N-001 · design fatigue factors (check the edition in your design basis)', B.start + 0.3, B.end);
    const m = D.norsok.N001_DFF;
    const x0 = 520, y0 = 300, cw = 380, rh = 150;
    S.div('Access for inspection and repair →', { x: x0 + 1.5 * cw, y: y0 - 90, cls: 'small', anchor: 'cm', style: 'color:#4fd1ff' }).in(c('8.3', 'n001'), 0.5);
    m.columns.forEach((col, j) => S.div(col, { x: x0 + j * cw + cw / 2, y: y0 - 30, w: cw - 20, cls: 'small', anchor: 'cm', style: 'text-align:center;color:#e9f2f9;font-weight:650' }).in(c('8.3', 'n001') + 0.2 * j, 0.5));
    Object.entries(m.rows).forEach(([row, vals], i) => {
      S.div(row, { x: x0 - 30, y: y0 + 60 + i * rh, w: 360, cls: 'small', anchor: 'rm', style: 'text-align:right;color:#e9f2f9;font-weight:650' }).in(c('8.3', 'n001') + 0.6 + 0.2 * i, 0.5);
      vals.forEach((v, j) => {
        const cell = S.div(`<span class="num" style="font-size:54px">${v}</span>`, { x: x0 + j * cw + 10, y: y0 + i * rh, w: cw - 20, h: rh - 20, style: 'display:flex;align-items:center;justify-content:center;border-radius:16px;background:rgba(255,255,255,0.05);border:1px solid rgba(190,220,245,0.16)' });
        cell.in(c('8.3', 'n001') + 0.8 + 0.1 * (i * 3 + j), 0.4, 'pop');
        if (i === 0 && j === 0) { cell.el.style.transition = 'none'; const h = S.div('', { x: x0 + 4, y: y0 - 6, w: cw - 8, h: rh - 8, cls: 'hl' }); h.el.style.borderColor = '#46d39a'; h.el.style.background = 'rgba(70,211,154,0.18)'; h.in(c('8.3', 'ten'), 0.5, 'pop'); }
      });
    });
    S.div('TS1: hidden behind the conductor housing (no access) · losing it removes support from the well (substantial) → <b class="c-green">DFF = 10</b>', { x: 520, y: 650, w: 1180, cls: 'body' }).in(c('8.3', 'ts'), 0.6);
  }

  // ------------------------------------------------------------------ 8.4 equivalent moment range (B.14)
  {
    const B = b('8.4');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · formula (B.14)', B.start + 0.3, B.end);
    const st = derivation(S, [
      { tex: 'D = \\sum_i \\dfrac{n_i}{\\bar a\\,\\DM_i^{-\\cv m}} = \\dfrac{1}{\\bar a}\\sum_i n_i\\,\\DM_i^{\\cv m}', t: c('8.4', 'd'), note: 'linear M-N curve' },
      { tex: '\\dfrac{n\\,\\DM_{\\mathrm{eq}}^{\\cv m}}{\\bar a} = \\dfrac{1}{\\bar a}\\sum_i n_i\\,\\DM_i^{\\cv m}, \\qquad n = \\sum_i n_i', t: c('8.4', 'neq'), note: 'same damage' },
      { tex: '\\DM_{\\mathrm{eq}} = \\left[\\dfrac{1}{n}\\sum_{i=1}^{k} n_i\\,\\DM_i^{\\cv m}\\right]^{1/\\cv m}\\quad\\text{(B.14)}', t: c('8.4', 'meq'), size: 56 },
    ], { y0: 270, gap: 190, size: 50 });
    st[2].boxed(c('8.4', 'meq') + 2.0);
    const n = S.eq('n = 7\\,472\\,771,\\;\\; \\cv m = 3:\\quad \\DM_{\\mathrm{eq}} = ' + fmt(L.dMeq['3']) + '\\ \\text{kNm}', { x: 960, y: 920, size: 44 });
    n.in(c('8.4', 'num'), 0.8, 'write');
  }

  // ------------------------------------------------------------------ 8.5 the single-load moment range (B.13, B.12)
  {
    const B = b('8.5');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · formulas (B.13) and (B.12)', B.start + 0.3, B.end);
    const cc = S.chart({ x: 200, y: 210, w: 820, h: 640, xlog: true, ylog: true, xmin: 1e4, xmax: 1e9, ymin: 100, ymax: 10000, xticks: logTicks(1e4, 1e9), yticks: [100, 1000, 10000], xfmt: pow10, yfmt: (v) => fmt(v), xlabel: 'cycles N', ylabel: 'ΔM [kNm]', title: 'DEMAND CURVE THROUGH (n, ΔM<sub>eq</sub>)' });
    cc.show(B.start + 0.3);
    const n = L.n_total, meq = L.dMeq['3'], la = Math.log10(n) + 3 * Math.log10(meq);
    const dem = [1e4, 1e9].map((N) => [N, Math.pow(10, (la - Math.log10(N)) / 3)]);
    const pt = cc.dot(n, meq, { color: COL.cyan, r: 11, t: c('8.5', 'through') - 0.4 });
    cc.curve(dem, { color: COL.cyan, width: 4, t: c('8.5', 'through') });
    const mo = Math.pow(10, (la - 6) / 3);
    const p6 = cc.dot(1e6, mo, { color: COL.amber, r: 12, t: c('8.5', 'at6') + 0.4 });
    S.line(cc.X(1e6), cc.Y(100), cc.X(1e6), cc.Y(mo), { stroke: COL.amber, width: 2, dash: '8 6' }).in(c('8.5', 'at6') + 0.4, 0.5, 'none');
    S.line(cc.X(1e4), cc.Y(mo), cc.X(1e6), cc.Y(mo), { stroke: COL.amber, width: 2, dash: '8 6' }).in(c('8.5', 'at6') + 0.4, 0.5, 'none');
    S.div('ΔM<sub>o</sub>', { x: cc.X(1e6) + 16, y: cc.Y(mo) - 22, cls: 'small', anchor: 'lb', style: 'color:#ffb547' }).in(c('8.5', 'at6') + 0.6, 0.5);
    S.div('(n, ΔM<sub>eq</sub>)', { x: cc.X(n) + 16, y: cc.Y(meq) + 16, cls: 'small', anchor: 'lt', style: 'color:#4fd1ff' }).in(c('8.5', 'through'), 0.5);
    const st = derivation(S, [
      { tex: '\\log\\bar a = \\log n + \\cv m\\,\\log\\DM_{\\mathrm{eq}}\\quad\\text{(B.13)}', t: c('8.5', 'through'), x: 1100, align: 'left', size: 42 },
      { tex: '\\log\\DM_o = \\dfrac{1}{\\cv m}\\left(\\log\\bar a - \\log 10^6\\right)\\quad\\text{(B.12)}', t: c('8.5', 'at6'), x: 1100, align: 'left', size: 42 },
      { tex: '\\DM_o = ' + fmt(L.dMo_back['3']) + '\\ \\text{kNm}\\;\\; \\text{vs}\\;\\; 1436 \\;\\;(0.93)', t: c('8.5', 'num'), x: 1100, align: 'left', size: 42 },
    ], { y0: 300, gap: 160, size: 42 });
    const cons = S.div('Table A.7 is slightly conservative', { x: 1100, y: 790, cls: 'h3', style: 'color:#46d39a' });
    cons.in(c('8.5', 'cons'), 0.7, 'write');
  }

  // ------------------------------------------------------------------ 8.6 the screening check
  {
    const B = b('8.6');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · A.3.5.1 example 2 · B.4.4 example', B.start + 0.3, B.end);
    const st = derivation(S, [
      { tex: 'D_{\\text{year}} = \\dfrac{10^6\\,\\DM_o^{\\cv m}}{10^6\\,\\DM_c^{\\cv m}} = \\left(\\dfrac{\\DM_o}{\\DM_c}\\right)^{\\cv m}', t: c('8.6', 'ratio'), note: 'demand / capacity at 10⁶' },
      { tex: 'T_f = 1\\ \\text{yr}\\left(\\dfrac{\\DM_c}{\\DM_o}\\right)^{\\cv m} \\;\\ge\\; \\cg{D_F}\\cdot 1\\ \\text{yr}', t: c('8.6', 'req'), note: 'require' },
      { tex: '\\dfrac{\\DM_c}{\\cg{D_F}^{\\,1/\\cv m}} \\;\\ge\\; \\DM_o', t: c('8.6', 'screen'), size: 64, note: 'screening check' },
    ], { y0: 230, gap: 180, size: 50 });
    st[2].boxed(c('8.6', 'screen') + 1.2, { color: COL.green });
    const d1 = S.eq('\\cg{D_F}=10,\\;\\cv m=3:\\;\\; 10^{1/3} = 2.15', { x: 960, y: 790, size: 42 });
    d1.in(c('8.6', 'dfm'), 0.7, 'write');
    const sens = table(S, ['+10 % moment', 'm = 3', 'm = 5'], [['life ×', (1 / 1.1 ** 3).toFixed(2), (1 / 1.1 ** 5).toFixed(2)]], { x: 700, y: 860, w: 520, t: c('8.6', 'sens'), colCls: ['l', '', ''] });
  }
}
