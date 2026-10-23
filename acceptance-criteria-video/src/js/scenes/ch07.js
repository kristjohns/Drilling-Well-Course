// Chapter 7 — summary: the three answers on one page, the design format, sources and outro.
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause } from '../engine/hud.js';
import { camSpline, DEF } from '../three/world.js';
import { updateSnow } from '../three/models.js';

export async function build(E, T, D) {
  const ch = T.ch(7);
  titleCard(ch, 'The three questions, answered');
  const W3 = E.world, md = W3.models;
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);

  // ------------------------------------------------------------------ 7.1 the answers
  {
    const B = b('7.1');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · Annex B', B.start + 0.3, B.end);
    const col = (x, n, q, a, bullets, tq, tb, color) => {
      const head = S.div(`<div class="num" style="font-size:30px;color:${color}">${n}</div><div style="font-weight:750;font-size:33px;line-height:1.15;margin-top:4px">${q}</div>`, { x, y: 140, w: 540 });
      head.in(tq - 0.3, 0.6, 'rise');
      const ans = S.div(a, { x, y: 270, w: 540, cls: 'h3', style: `color:${color};font-size:31px;line-height:1.2` });
      ans.in(tq + 0.8, 0.6, 'rise');
      bullets.forEach((bl, i) => {
        const r = S.div(`<span style="color:${color};margin-right:10px">●</span>${bl}`, { x, y: 400 + i * 104, w: 540, cls: 'small', style: 'font-size:24px;color:#e9f2f9;line-height:1.35' });
        r.in(tb + i * 0.9, 0.5, 'left');
      });
    };
    col(110, '1', 'Is the criterion the yield strength?', 'The anchor of every check, never compared with a peak',
      ['σ<sub>y</sub> = min[Y<sub>y</sub>·SMYS; 0.9·Y<sub>u</sub>·SMTS], 0.2 % offset (B.5)', 'Elastic: linearised P<sub>m</sub>, P<sub>L</sub>, P<sub>b</sub> against σ<sub>y</sub>, 1.5 σ<sub>y</sub> … (Table B.7)',
        'Elastic-plastic: shapes the material curve that produces the capacity', 'Pipe formulas use σ<sub>y</sub> directly (B.9)'], c('7.1', 'q1'), c('7.1', 'q1b'), COL.amber);
    col(690, '2', 'Is it a strain limit?', 'Not for yielding',
      ['Yielding capacity = limit load, or plastic collapse / max[1.2; σ<sub>u</sub>/σ<sub>y</sub>]', 'Studs and segments in bending: 0.2 % plastic strain through the root section',
        'Local failure: strain limit falling with triaxiality (KD-232), unless the steel is ductile enough'], c('7.1', 'q2'), c('7.1', 'q2b'), COL.green);
    col(1270, '3', 'What do we take out of the FE model?', 'Linearised stresses, or a load–rotation curve',
      ['Elastic: membrane, bending and peak along stress classification lines', 'Elastic-plastic: load against rotation up to instability', 'Plastic strain and triaxiality at critical points; contact pressure for seals and hub faces'],
      c('7.1', 'q3'), c('7.1', 'q3') + 2.0, COL.cyan);
    const eq = S.eq('\\text{Load} \\;\\le\\; \\cg{F_d} \\times \\text{Capacity}', { x: 960, y: 935, size: 66 });
    eq.in(c('7.1', 'last') + 1.0, 1.0, 'write');
    eq.boxed(c('7.1', 'last') + 2.0, { color: COL.amber });
  }

  // ------------------------------------------------------------------ 7.2 outro
  {
    const B = b('7.2');
    const cam = camSpline([
      { t: B.start, p: [9, 6.5, 14], l: [0, 5.2, 0], fov: 38 },
      { t: B.end, p: [13, 7.5, 9.5], l: [0, 5.6, 0], fov: 38 },
    ]);
    W3.shot(B.start, B.end + 0.5, {
      show: ['bop', 'well', 'template', 'seabed', 'snow', 'rays', 'riser'],
      fadeIn: 1.2, fadeOut: 2.0, cam, fog: 0.018, bg: '#0a3550',
      update: (t) => {
        W3.update(t); updateSnow(md.snow, t); DEF.uAmp.value = 0;
        for (const r of md.rays.children) r.material.opacity = 0.06 + 0.04 * Math.sin(t * 0.7 + r.userData.phase);
        md.rays.position.y = 40;
      },
    });
    const S = new Scene(B.start, B.end + 0.5, { fade: 0.8, fadeOut: 1.6 });
    const dim = S.div('', { x: 0, y: 0, w: 1920, h: 1080, style: 'background:linear-gradient(90deg, rgba(4,12,20,0.9) 0%, rgba(4,12,20,0.6) 50%, rgba(4,12,20,0) 80%)' });
    dim.in(B.start, 1.0, 'none');
    S.div('SOURCES', { x: 120, y: 200, cls: 'kicker' }).in(c('7.2', 'src'), 0.6, 'left');
    const src = [
      'NORSOK U-001:2026 · Annex B: B.2.5, B.2.7.4, B.3.3–B.3.6, B.9, Table B.7 · definitions 3.1, 3.2 · Annex A, Table A.4',
      'ASME BPVC VIII-2 Annex 5-A · stress classification and linearisation',
      'ASME BPVC VIII-3 KM-620 material model · KD-232 local strain limit · KD-234 ratcheting',
      'NS-EN ISO 13628-7 · completion/workover riser systems',
    ];
    src.forEach((s, i) => S.div(s, { x: 120, y: 250 + i * 66, w: 1450, cls: 'small' }).in(c('7.2', 'src') + 0.4 + i * 0.35, 0.5, 'left'));
    const disc = S.card(`<div class="ref" style="color:#ffb547">WORKED EXAMPLE</div><div class="small">Illustrative inputs: 75K housing neck OD 0.70 m, bore 0.476 m; Table A.4 loads 250–500 m; 690 bar on D<sub>s</sub> 0.50 m. The stress field and the load–rotation curves come from teaching stand-ins (beam, Lamé and fillet-peak stresses; a section model of the neck), not from a 3D FE analysis. Take design values from your project and the code editions in your design basis.</div>`,
      { x: 120, y: 540, w: 1000, cls: 'glass' });
    disc.in(c('7.2', 'disc'), 0.7, 'rise');
    const end = S.div('Acceptance criteria for structural analysis · NORSOK U-001:2026', { x: 120, y: 900, cls: 'small', style: 'color:#7f97aa' });
    end.in(c('7.2', 'disc') + 2.5, 0.8);
  }
}
