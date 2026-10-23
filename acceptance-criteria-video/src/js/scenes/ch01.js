// Chapter 1 — load against capacity: scope of Annex B on the 3D wellhead, failure modes, design format (B.2), three ways to a capacity.
import { E, ease, COL, clamp, smooth, ramp, lerp } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause } from '../engine/hud.js';
import { camSpline, DEF } from '../three/world.js';
import { updateSnow } from '../three/models.js';
import { label3D } from './kit.js';

export async function build(E, T, D) {
  const ch = T.ch(1);
  titleCard(ch, 'Which rules apply, the failure modes, and the design format of Annex B');
  const W3 = E.world, md = W3.models, M = W3.M;
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);

  // ------------------------------------------------------------------ 1.1 scope on the 3D wellhead
  {
    const B = b('1.1');
    const cam = camSpline([
      { t: B.start, p: [7.4, 5.6, 11.4], l: [-0.3, 2.3, 0], fov: 36 },
      { t: c('1.1', 'wh'), p: [5.2, 4.6, 8.4], l: [0, 2.7, 0], fov: 34 },
      { t: c('1.1', 'conn') + 1.0, p: [4.8, 4.9, 8.0], l: [0, 2.9, 0], fov: 34 },
      { t: c('1.1', 'pipe') + 0.8, p: [6.0, 1.6, 10.2], l: [0, -0.8, 0], fov: 38 },
      { t: c('1.1', 'tmpl') + 0.8, p: [9.8, 6.8, 13.6], l: [-1.6, 1.3, -1.2], fov: 40 },
      { t: B.end, p: [10.2, 7.0, 14.0], l: [-1.6, 1.3, -1.2], fov: 40 },
    ]);
    const cyan = [0.12, 0.42, 0.62], amber = [0.62, 0.36, 0.04], yel = [0.42, 0.3, 0.02];
    const glow = (mat, col, h) => mat.emissive.setRGB(col[0] * h, col[1] * h, col[2] * h);
    W3.shot(B.start, B.end, {
      show: ['wellCut', 'templateCut', 'seabedCut', 'connCut', 'snow'],
      fadeIn: 0.8, fadeOut: 0.8, cam, fog: 0.012, bg: '#082b42',
      update: (t) => {
        W3.update(t); updateSnow(md.snow, t);
        DEF.uAmp.value = 0;
        const hw = smooth(t, c('1.1', 'wh') - 0.2, c('1.1', 'wh') + 0.6), hc = smooth(t, c('1.1', 'ch') - 0.2, c('1.1', 'ch') + 0.6);
        const hn = smooth(t, c('1.1', 'conn') - 0.2, c('1.1', 'conn') + 0.6), hp = smooth(t, c('1.1', 'pipe') - 0.2, c('1.1', 'pipe') + 0.6);
        const ht = smooth(t, c('1.1', 'tmpl') - 0.2, c('1.1', 'tmpl') + 0.6);
        glow(M.steel, cyan, hw); glow(M.whx, cyan, hw); glow(M.lp, cyan, hc); glow(M.connDark, cyan, 1.3 * hn);
        glow(M.cond, amber, hp); glow(M.yellow, yel, ht); glow(M.yellowDark, yel, ht);
      },
    });
    const S = new Scene(B.start, B.end);
    const card = S.card(`<div class="ref">NORSOK U-001:2026 · Annex B (normative) · Table B.1</div>
      <div style="font-weight:750;font-size:30px;line-height:1.25;margin-bottom:12px">Pressure-containing and primary structural components in the <span class="c-cyan">riser load path</span></div>
      <div class="small">Wellhead and conductor housings and their extensions · connectors · tree · completion and workover riser equipment</div>`,
    { x: 110, y: 170, w: 640, cls: 'glass' });
    card.in(c('1.1', 'annexB') - 0.2, 0.6, 'left');
    const key = (y, col, txt, t) => {
      const a = S.div(`<span style="display:inline-block;width:18px;height:18px;border-radius:4px;background:${col};margin-right:12px;vertical-align:-2px"></span>${txt}`, { x: 120, y, cls: 'small' });
      a.in(t, 0.5, 'left');
    };
    key(585, COL.cyan, 'Annex B · capacity by analysis', c('1.1', 'wh'));
    key(630, COL.amber, 'Clause B.9 · pipe capacity formulas', c('1.1', 'pipe'));
    key(675, COL.yellow, 'NORSOK N-001 · template structure', c('1.1', 'tmpl'));
    const t1 = c('1.1', 'pipe') - 0.3;
    label3D(S, [0.42, 3.62, 0], 'HP wellhead housing', { t0: c('1.1', 'wh') + 0.2, t1, anchor: 'lm', dx: 110, dy: -40 });
    label3D(S, [0.26, 0.45, 0], 'Wellhead extension', { t0: c('1.1', 'wh') + 0.9, t1, anchor: 'lm', dx: 150, dy: -20 });
    label3D(S, [0.5, 1.9, 0], 'Conductor housing', { t0: c('1.1', 'ch') + 0.2, t1, anchor: 'lm', dx: 140, dy: 20 });
    label3D(S, [0.84, 4.7, 0], 'Wellhead connector', { t0: c('1.1', 'conn') + 0.2, t1, anchor: 'lm', dx: 110, dy: -30 });
    label3D(S, [0.46, -2.4, 0], 'Conductor pipe <span class="sub">clause B.9 · 13.3.6.2</span>', { t0: c('1.1', 'pipe') + 0.6, t1: c('1.1', 'tmpl') + 0.2, anchor: 'lm', dx: 140, dy: 0, color: COL.amber });
    label3D(S, [-4.4, 2.95, -0.2], 'Template <span class="sub">13.3.6 → NORSOK N-001</span>', { t0: c('1.1', 'tmpl') + 0.6, t1: B.end, anchor: 'lm', dx: 60, dy: -110, color: COL.yellow });
  }

  // ------------------------------------------------------------------ 1.2 failure modes (Table B.2)
  {
    const B = b('1.2');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · Table B.2 · B.2.2 · B.3.1', B.start + 0.3, B.end);
    S.div('Design against failure modes', { x: 960, y: 140, cls: 'h2', anchor: 'ct' }).in(c('1.2', 'modes') - 0.3, 0.6, 'write');
    const col = (x, title, color, items, t, step = 0.55) => {
      const card = S.card(`<div class="ref" style="color:${color}">${title}</div>`, { x, y: 250, w: 520, h: 520, cls: 'glass' });
      card.in(t - 0.2, 0.5, 'rise');
      const rows = items.map((it, i) => {
        const r = S.div(`<span style="color:${color};margin-right:12px">●</span>${it}`, { x: x + 34, y: 312 + i * 64, cls: 'small', style: 'font-size:27px;color:#e9f2f9' });
        r.in(t + i * step, 0.45, 'left');
        return r;
      });
      return { card, rows };
    };
    const st = col(120, 'STRUCTURAL', COL.cyan, ['Brittle fracture', 'Yielding', 'Local failure', 'Buckling', 'Mechanical disengagement'], c('1.2', 'struct'), 0.9);
    const fu = col(700, 'FUNCTIONAL', COL.green, ['Hub face separation', 'Seal / gasket leak tightness', 'Galling', 'Loss of functionality'], c('1.2', 'func'), 0.8);
    const en = col(1280, 'ENVIRONMENTAL', COL.violet, ['Corrosion', 'Environmental assisted cracking'], c('1.2', 'func') + 3.2, 0.6);
    // brittle fracture and EAC are handled by the material requirements
    const tm = c('1.2', 'mat');
    for (const [r, x, y] of [[st.rows[0], 120, 312], [en.rows[1], 1280, 376]]) {
      r.to(tm, 0.6, { o: 0.4 });
      const tag = S.div('prevented by material requirements · B.10', { x: x + 34, y: y + 40, cls: 'tiny', style: 'color:#ffb547;letter-spacing:0.04em;font-size:18px' });
      tag.in(tm + 0.3, 0.5, 'left');
    }
    const eq = S.eq('\\text{Static capacity} \\;=\\; \\min\\big(\\,\\text{structural},\\ \\text{functional}\\,\\big)', { x: 960, y: 880, size: 46 });
    eq.in(c('1.2', 'min'), 0.8, 'write');
    S.div('B.3.1 · the lowest capacity over all remaining failure modes', { x: 960, y: 950, cls: 'small', anchor: 'ct' }).in(c('1.2', 'min') + 0.8, 0.6);
  }

  // ------------------------------------------------------------------ 1.3 design format (B.2) and Table B.3
  {
    const B = b('1.3');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.2.5 · formula (B.2) · Table B.3', B.start + 0.3, B.end);
    const eq = S.eq('\\p{load}{\\text{Load or load effect}} \\;\\le\\; \\p{fd}{\\cg{F_d}} \\times \\p{cap}{\\text{Static capacity}}', { x: 960, y: 230, size: 64 });
    eq.in(c('1.3', 'b2') - 0.2, 0.9, 'write');
    S.div('formula (B.2)', { x: 1640, y: 230, cls: 'tiny', anchor: 'lm' }).in(c('1.3', 'b2') + 0.6, 0.5);
    // Table B.3 as rows
    const rows = [
      ['h', 'Single load design', '', ''],
      ['press', 'Internal pressure · external pressure', '0.60', '1.00'],
      ['', 'Hydrostatic body pressure test (FAT) · make and break', '0.90', '1.00'],
      ['h', 'Combined load design', '', ''],
      ['normal', 'Normal conditions', '0.67', '1.00'],
      ['extreme', 'Extreme conditions', '0.80', '1.00'],
      ['acc', 'Accidental · above barrier elements', '1.00', '1.00'],
      ['acc2', 'Accidental · below and including barrier elements', '0.90', '1.00'],
    ];
    const x0 = 330, y0 = 360, w = 1260;
    const head = S.div(`<div style="display:flex;font-weight:700;font-size:20px;color:#7f97aa;letter-spacing:0.06em"><div style="width:${w - 420}px">TABLE B.3 · LOAD AND LOAD CONDITION</div><div style="width:210px;text-align:right">STRUCTURAL F<sub>d</sub></div><div style="width:210px;text-align:right">FUNCTIONAL F<sub>d</sub></div></div>`, { x: x0, y: y0 - 50 });
    head.in(c('1.3', 'table') - 0.2, 0.5);
    const R = {}, ALL = [];
    rows.forEach(([k, a, s1, s2], i) => {
      const y = y0 + i * 62;
      const isH = k === 'h';
      const r = S.div(`<div style="display:flex;align-items:center;height:54px;padding:0 18px;border-radius:12px;${isH ? '' : 'background:rgba(16,36,54,0.82);border:1px solid rgba(190,220,245,0.12)'}">
        <div style="width:${w - 456}px;font-weight:${isH ? 750 : 550};font-size:${isH ? 22 : 27}px;color:${isH ? '#4fd1ff' : '#e9f2f9'};${isH ? 'letter-spacing:0.08em;text-transform:uppercase' : ''}">${a}</div>
        <div class="num" style="width:210px;text-align:right;font-size:32px;color:#46d39a">${s1}</div><div class="num" style="width:210px;text-align:right;font-size:32px;color:#b9cad8">${s2}</div></div>`, { x: x0, y, w });
      r.in(c('1.3', 'table') + 0.15 * i, 0.4, 'left');
      R[k] = r; ALL.push(r);
    });
    const hiRow = (k, t, d = 3.2) => {
      const i = rows.findIndex((r) => r[0] === k);
      const box = S.div('', { x: x0 - 8, y: y0 + i * 62 - 6, w: w + 16, h: 66, cls: 'hl' });
      box.in(t, 0.35, 'pop'); box.out(t + d, 0.4);
    };
    hiRow('normal', c('1.3', 'normal'), 3.3); hiRow('extreme', c('1.3', 'extreme'), 2.2);
    hiRow('acc', c('1.3', 'acc'), 4.4); hiRow('acc2', c('1.3', 'acc'), 4.4); hiRow('press', c('1.3', 'press'), 3.6);
    // functional column
    const fbox = S.div('', { x: x0 + w - 230, y: y0 - 8, w: 236, h: rows.length * 62 + 4, cls: 'hl' });
    fbox.el.style.borderColor = '#46d39a'; fbox.el.style.background = 'rgba(70,211,154,0.12)';
    fbox.in(c('1.3', 'func'), 0.4, 'pop'); fbox.out(c('1.3', 'only') - 0.2, 0.4);
    S.div('F<sub>d</sub> applies to the yielding failure mode (Tables B.5, B.6, note a)', { x: x0, y: y0 + rows.length * 62 + 14, cls: 'tiny', style: 'font-size:19px' }).in(c('1.3', 'table') + 1.6, 0.5).out(c('1.3', 'only') - 0.1, 0.5);
    // both sides are loads
    const tOnly = c('1.3', 'only');
    for (const r of ALL) r.out(tOnly - 0.1, 0.5);
    head.out(tOnly - 0.1, 0.5);
    eq.to(tOnly, 1.0, { y: 200, s: 1.12 }, ease.inOut3);
    later(() => {
      const mk = (name, txt, color, dy) => {
        const r = eq.rect(name);
        const sc = 1.12, cx = 960, cy = 230;
        const X = cx + (r.x - cx) * sc, Y = cy + 200 + (r.y - cy) * sc, Wd = r.w * sc, Hd = r.h * sc;
        const box = S.div('', { x: X - 14, y: Y - 12, w: Wd + 28, h: Hd + 24, cls: 'eqbox' });
        box.el.style.borderColor = color; box.el.style.boxShadow = `0 0 34px ${color}55`;
        box.in(c('1.3', 'both'), 0.5, 'zoom');
        const tag = S.div(txt, { x: X + Wd / 2, y: Y + Hd + 40 + dy, cls: 'h3', anchor: 'ct', style: `color:${color};letter-spacing:0.12em` });
        tag.in(c('1.3', 'both') + 0.3, 0.5, 'rise');
      };
      mk('load', 'A LOAD', COL.amber, 0);
      mk('cap', 'A LOAD', COL.cyan, 0);
    });
    const big = S.div('Not a stress. Not a strain.<br><span class="c-amber">A load, compared with a capacity.</span>', { x: 960, y: 650, cls: 'h2', anchor: 'ct', style: 'text-align:center' });
    big.in(c('1.3', 'notstress'), 0.8, 'rise');
  }

  // ------------------------------------------------------------------ 1.4 three ways to a capacity (B.3.3)
  {
    const B = b('1.4');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.3.3 capacity methods · B.9 pipe design', B.start + 0.3, B.end);
    S.div('How do we find the capacity?', { x: 960, y: 140, cls: 'h2', anchor: 'ct' }).in(B.start + 0.4, 0.6, 'write');
    const card = (x, n, title, body, t, color) => {
      const a = S.card(`<div style="display:flex;align-items:center;gap:18px;margin-bottom:16px"><div style="width:64px;height:64px;border-radius:18px;background:${color};color:#06121c;font-weight:800;font-size:34px;display:flex;align-items:center;justify-content:center">${n}</div>
        <div style="font-weight:750;font-size:33px;line-height:1.1">${title}</div></div><div class="small">${body}</div>`, { x, y: 250, w: 540, h: 400, cls: 'glass' });
      a.in(t - 0.2, 0.6, 'rise');
      return a;
    };
    card(110, 1, 'By formulas', 'Simple shapes only: pipes (clause B.9), spheres, bolted flanges (Annex C). Also used to check FE results by hand.', c('1.4', 'formulas'), COL.amber);
    card(690, 2, 'Elastic FE analysis', 'Linearised stresses against allowables in σ<sub>y</sub> (Table B.7). <span class="c-amber">Preliminary design only.</span> Not for functional capacities.', c('1.4', 'elastic'), COL.cyan);
    card(1270, 3, 'Elastic-plastic FE analysis', 'A direct assessment of the failure modes: limit load, or factored plastic collapse load. The method for design.', c('1.4', 'ep'), COL.green);
    const pn = S.card(`<div class="tiny" style="color:#ffb547;margin-bottom:8px">PIPE FORMULAS USE σ<sub>y</sub> DIRECTLY</div>
      <div class="small" style="font-size:23px">Seamless riser pipe (B.9.3): fully plastic section, M<sub>p</sub><br>Conductor, casing (B.9.5): first yield at the outer fibre, M<sub>y</sub></div>`, { x: 110, y: 690, w: 540, cls: 'glass', style: 'padding:20px 28px' });
    pn.in(c('1.4', 'pipes'), 0.6, 'rise');
    const strip = S.div('<span class="c-amber">σ<sub>y</sub></span> enters all three &nbsp;·&nbsp; <span class="c-green">strain</span> only appears in elastic-plastic analysis', { x: 960, y: 960, cls: 'h3', anchor: 'ct' });
    strip.in(c('1.4', 'where'), 0.7, 'rise');
  }
}
