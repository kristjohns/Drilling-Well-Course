// Chapter 4 — five percent, and the two: Annex C has one strain value; what a 2 % limit would change on the ring;
// the strain at a point depends on the mesh (no hardening) but the load hardly does; EN 1993-1-14.
import { E, ease, COL, clamp, smooth, lerp, fmt } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause } from '../engine/hud.js';
import { note } from './fx.js';

export async function build(E, T, D) {
  const ch = T.ch(4);
  titleCard(ch, 'Where the 2 % is not, and why a strain value needs its model and mesh');
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const MK = D.marks;

  // ------------------------------------------------------------------ 4.1 where is the 2 %?
  {
    const B = b('4.1');
    const S = new Scene(B.start, B.end);
    clause('EN 1993-1-5 · Annex C · C.8 NOTE 1', B.start + 0.3, B.end);
    const one = S.card(`<div class="ref">EN 1993-1-5 · ANNEX C</div><div style="font-weight:750;font-size:34px;line-height:1.25">One strain value: <span class="c-amber">5 %</span></div><div class="small" style="font-size:23px">recommended limiting principal membrane strain · the National Annex may specify another value</div>`,
      { x: 110, y: 180, w: 760, cls: 'glass' });
    one.in(c('4.1', 'one') - 0.2, 0.6, 'left');
    const no = S.card(`<div style="display:flex;gap:20px;align-items:center"><div style="font-size:64px;color:#ff4d5e;font-weight:800;line-height:1">✗</div><div><div style="font-weight:750;font-size:34px">2 %</div><div class="small" style="font-size:23px">no such criterion found in EN 1993-1-5</div></div></div>`,
      { x: 110, y: 420, w: 760, cls: 'glass', style: 'border-color:rgba(255,77,94,0.5)' });
    no.in(c('4.1', 'none') - 0.2, 0.6, 'left');
    const ask = S.card(`<div class="tiny" style="margin-bottom:8px">IF SOMEONE QUOTES A STRAIN LIMIT, ASK</div><div class="small" style="font-size:24px;line-height:1.55;color:#e9f2f9">which document and clause?<br>which strain: membrane, surface, equivalent plastic?<br>which material model and mesh?</div>`,
      { x: 110, y: 640, w: 760, cls: 'glass' });
    ask.in(c('4.1', 'ask') - 0.2, 0.6, 'left');
    // bars: alpha at 2 % and at 5 % for both material models
    const X0 = 1040, Y0 = 820, Hs = 300, bw = 120;
    const yv = (a) => Y0 - (a - 1.0) / (1.9 - 1.0) * Hs * 1.6;
    const axis = S.path(`M${X0 - 30},${Y0} L${X0 + 760},${Y0}`, { stroke: 'rgba(200,225,245,0.55)', width: 2 });
    axis.in(c('4.1', 'cmp'), 0.5, 'none');
    S.div('load multiplier α at the strain limit', { x: X0 - 30, y: 220, cls: 'tiny' }).in(c('4.1', 'cmp'), 0.5);
    const grp = [['c', 'linear hardening (c)', MK.c.e2.alpha, MK.c.e5.alpha, COL.amber], ['a', 'nominal plateau (b)', MK.b.e2.alpha, MK.b.e5.alpha, COL.cyan]];
    grp.forEach(([cue, name, a2, a5, col], i) => {
      const x = X0 + i * 380, t = c('4.1', cue);
      for (const [k, a, op, lab] of [[0, a2, 0.55, '2 %'], [1, a5, 1, '5 %']]) {
        const bx = x + k * (bw + 24), top = yv(a);
        const r = S.rect(bx, top, bw, Y0 - top, { fill: col, stroke: 'none', rx: 6, opacity: op });
        r.in(t + k * 0.5, 0.5, 'none');
        S.div(`<span class="num">${a.toFixed(2)}</span>`, { x: bx + bw / 2, y: top - 26, cls: 'small', anchor: 'cm', style: `color:${col};font-size:26px;font-weight:700` }).in(t + k * 0.5 + 0.2, 0.4);
        S.div(lab, { x: bx + bw / 2, y: Y0 + 26, cls: 'small', anchor: 'cm', style: 'font-size:22px' }).in(t + k * 0.5, 0.4);
      }
      S.div(name, { x: x + bw + 12, y: Y0 + 70, cls: 'small', anchor: 'ct', style: `color:${col};font-size:23px;font-weight:650` }).in(t, 0.4);
      const dlt = Math.round((a2 / a5 - 1) * 100);
      S.div(`${dlt} %`, { x: x + bw + 12, y: yv(a5) - 90, cls: 'h3', anchor: 'cm', style: `color:${col}` }).in(t + 1.0, 0.5, 'pop');
    });
    note(S, 'Slot ring D, fibre beam model, elements of 1.25°', { t0: c('4.1', 'cmp') + 1, t1: B.end - 0.4 });
  }

  // ------------------------------------------------------------------ 4.2 strain depends on the mesh
  {
    const B = b('4.2');
    const S = new Scene(B.start, B.end);
    clause('EN 1993-1-5 · C.8 · EN 1993-1-14:2025', B.start + 0.3, B.end);
    const cols = ['#5b6f80', '#7fa6c4', '#4fd1ff', '#e9f2f9'];
    const mkChart = (x, m, ymin, ymax, title, t) => {
      const chm = S.chart({ x, y: 200, w: 760, h: 470, xmin: 0, xmax: 6, ymin, ymax, xticks: [0, 1, 2, 3, 4, 5, 6], yticks: [ymin, (ymin + ymax) / 2, ymax].map((v) => +v.toFixed(2)),
        yfmt: (v) => v.toFixed(2), xlabel: 'Largest strain in the ring · %', ylabel: 'Load multiplier α', title });
      chm.show(t);
      D.mesh[m].forEach((ms, i) => chm.curve(ms.curve.map(([a, e]) => [e, a]).filter(([e]) => e <= 6.2), { color: cols[i], width: 3.5, t: t + 0.4 + i * 0.5, d: 1.0 }));
      return chm;
    };
    const ca = mkChart(140, 'b', 1.2, 1.6, '(b) NOMINAL PLATEAU · FOUR ELEMENT SIZES', c('4.2', 'mesh') - 1.0);
    const cc = mkChart(1020, 'c', 1.2, 1.8, '(c) LINEAR HARDENING · FOUR ELEMENT SIZES', c('4.2', 'harden') - 0.4);
    const lg = S.div(D.mesh.b.map((ms, i) => `<span style="display:inline-flex;align-items:center;gap:8px;margin-right:22px"><span style="width:26px;height:4px;background:${cols[i]}"></span>${ms.deg.toFixed(ms.deg < 1 ? 3 : ms.deg < 2 ? 2 : 1).replace(/0+$/, '').replace(/\.$/, '')}° · ${Math.round(ms.L_mm)} mm</span>`).join(''),
      { x: 960, y: 92, cls: 'small', anchor: 'ct', style: 'font-size:21px' });
    lg.in(c('4.2', 'mesh') - 0.6, 0.5);
    // alpha = 1.50 marker with the strains of the four meshes
    const yl = S.path(`M${ca.X(0)},${ca.Y(1.5)} L${ca.X(6)},${ca.Y(1.5)}`, { stroke: '#ffffff', width: 2, dash: '5 6' });
    yl.in(c('4.2', 'mesh') + 2.5, 0.5, 'none');
    D.mesh.b.forEach((ms, i) => { if (ms.eps_at_150 !== null) ca.dot(ms.eps_at_150, 1.5, { color: cols[i], r: 8, t: c('4.2', 'mesh') + 3.0 + i * 0.3 }); });
    const e0 = D.mesh.b[0].eps_at_150, e3 = D.mesh.b[3].eps_at_150;
    const ml = S.div(`same load α 1.50: <span class="num">${e0.toFixed(1)}</span> % coarse … <span class="num">${e3.toFixed(1)}</span> % fine`, { x: ca.X(0.2), y: ca.Y(1.5) + 70, cls: 'label', style: 'font-size:23px' });
    ml.in(c('4.2', 'mesh') + 4.2, 0.5, 'rise');
    const a5 = D.mesh.b.map((ms) => ms.e5.alpha);
    const ll = S.div(`α at 5 %: <span class="num">${Math.max(...a5).toFixed(2)}</span> … <span class="num">${Math.min(...a5).toFixed(2)}</span> — the load hardly moves`, { x: ca.X(0.2), y: ca.Y(1.5) + 115, cls: 'label c-amber', style: 'font-size:23px' });
    ll.in(c('4.2', 'load'), 0.5, 'rise');
    const hl = S.div('the four curves lie on top of each other', { x: cc.X(0.3), y: cc.Y(1.3), cls: 'label c-green', style: 'font-size:23px' });
    hl.in(c('4.2', 'harden') + 1.8, 0.5, 'rise');
    const ls = S.card('<div style="font-weight:750;font-size:30px">A strain limit = a number + a material model + a mesh + a definition of the strain</div>', { x: 140, y: 790, w: 1080, cls: 'glass' });
    ls.in(c('4.2', 'lesson'), 0.6, 'rise');
    const ec = S.card('<div class="ref">SECOND GENERATION EUROCODE 3</div><div style="font-weight:750;font-size:28px">EN 1993-1-14:2025</div><div class="small" style="font-size:21px">Design assisted by finite element analysis</div>', { x: 1300, y: 770, w: 480, cls: 'glass' });
    ec.in(c('4.2', 'ec14'), 0.6, 'rise');
    const ed = S.div('check the edition your design basis calls for', { x: 1540, y: 960, cls: 'small c-amber', anchor: 'ct', style: 'font-size:22px' });
    ed.in(c('4.2', 'edition'), 0.5);
  }
}
