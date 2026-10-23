// Chapter 6 — worked example: Table A.4 loads at the datum moved to the neck, the pressure end load, the (B.7) check
// on the capacity chart, the remaining failure modes, and the verdict on the red spot.
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause } from '../engine/hud.js';
import { camSpline, DEF } from '../three/world.js';
import { updateSnow, FEU, feSetElastic } from '../three/models.js';
import { stamp } from './kit.js';
import { datumLoads, probe3D, capChart, vmLegend } from './fx.js';

const tn = (x) => fmt(x).replace(/\s/g, '\\,');

export async function build(E, T, D) {
  const ch = T.ch(6);
  titleCard(ch, 'Table A.4 loads, the pressure end load, formula (B.7) and the verdict');
  const W3 = E.world, md = W3.models, M = W3.M;
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const Ld = D.loads, A = Ld.als, U = Ld.uls, sec = D.section, ck = D.check.limit;

  // ------------------------------------------------------------------ 6.1 the case
  {
    const B = b('6.1');
    const cam = camSpline([
      { t: B.start, p: [8.0, 10.5, 19], l: [-4.0, 6.5, 0], fov: 36 },
      { t: c('6.1', 'a4'), p: [3.4, 5.8, 9.4], l: [-2.0, 4.1, 0], fov: 30 },
      { t: c('6.1', 'shear'), p: [2.7, 4.9, 7.2], l: [-1.55, 3.8, 0], fov: 30 },
      { t: B.end, p: [2.6, 4.85, 7.0], l: [-1.5, 3.78, 0], fov: 30 },
    ]);
    W3.shot(B.start, B.end, {
      show: ['bop', 'well', 'template', 'seabed', 'snow'],
      fadeIn: 0.8, fadeOut: 0.6, cam, fog: 0.016, bg: '#0a3550',
      update: (t) => {
        W3.update(t); updateSnow(md.snow, t);
        DEF.uAmp.value = 0;
        const h = smooth(t, c('6.1', 'shear') - 0.2, c('6.1', 'shear') + 0.6) * (0.75 + 0.25 * Math.sin(t * 3));
        M.steel.emissive.setRGB(0.55 * h, 0.32 * h, 0.04 * h);
      },
    });
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · Table A.4 · A.3.3 · A.3.4', B.start + 0.3, B.end);
    const k = S.div('WORKED EXAMPLE · 350 m · BOP ON THE WELLHEAD', { x: 110, y: 120, cls: 'kicker' });
    k.in(c('6.1', 'depth'), 0.6, 'left');
    const tb = S.card(`<div class="ref">TABLE A.4 · BOP ON WH · DESIGN LOADS AT THE WELLHEAD DATUM</div>
      <table class="t" style="font-size:24px;margin-top:6px"><thead><tr><th class="l">Water depth</th><th></th><th>M<sub>w</sub> kNm</th><th>Q<sub>w</sub> kN</th><th>T kN</th></tr></thead><tbody>
      ${Ld.table_a4.map((r) => `<tr class="${r.range === '250–500' ? 'hi' : 'dim'}"><td class="l">${r.range} m</td><td class="l">ULS</td><td>${fmt(r.uls[0])}</td><td>${fmt(r.uls[1])}</td><td>${fmt(r.uls[2])}</td></tr>
      <tr class="${r.range === '250–500' ? 'hi als' : 'dim'}"><td class="l"></td><td class="l">ALS</td><td>${fmt(r.als[0])}</td><td>${fmt(r.als[1])}</td><td>${fmt(r.als[2])}</td></tr>`).join('')}</tbody></table>
      <div class="tiny" style="margin-top:8px">ULS → extreme design loads · ALS → accidental design loads (A.3.4)</div>`, { x: 90, y: 180, w: 780, cls: 'glass' });
    tb.in(c('6.1', 'a4'), 0.6, 'rise');
    later(() => {
      const rows = [...tb.el.querySelectorAll('tr.als')];
      if (!rows.length) return;
      const r = rows[0].getBoundingClientRect(), o = E.root.getBoundingClientRect(), s = E.stageScale || 1;
      const box = S.div('', { x: (r.left - o.left) / s - 6, y: (r.top - o.top) / s - 2, w: r.width / s + 12, h: r.height / s + 4, cls: 'hl' });
      box.in(c('6.1', 'als'), 0.4, 'pop');
    });
    datumLoads(S, [0, 4.0, 0], { t0: c('6.1', 'als') + 0.5, t1: B.end, scale: 0.85,
      labels: { M: `<span class="num">${fmt(A.Mw_kNm)}</span> kNm`, Q: `<span class="num">${fmt(A.Qw_kN)}</span> kN`, T: `<span class="num">${fmt(A.Te_kN)}</span> kN` } });
    // datum and neck levels
    const dl = S.path('M0,0', { stroke: COL.amber, width: 2, dash: '10 8' }), nl = S.path('M0,0', { stroke: '#ffffff', width: 2, dash: '10 8' });
    const dim = S.path('M0,0', { stroke: '#ffffff', width: 2.5 });
    const dt = S.div('wellhead datum', { x: 0, y: 0, cls: 'tiny', style: 'color:#ffb547' }), nt = S.div('neck · critical section', { x: 0, y: 0, cls: 'tiny', style: 'color:#fff' });
    const dd = S.div('0.6 m', { x: 0, y: 0, cls: 'label' });
    for (const a of [dl, dt]) a.in(c('6.1', 'a4') + 0.5, 0.5, 'none');
    for (const a of [nl, nt, dim, dd]) a.in(c('6.1', 'shear'), 0.5, 'none');
    E.anim(B.start, B.end, (t) => {
      const p0 = W3.project([0.95, 4.0, 0.9], t), p1 = W3.project([0.95, 3.4, 0.9], t), a0 = W3.project([-0.95, 4.0, 0.9], t), a1 = W3.project([-0.95, 3.4, 0.9], t);
      dl.el.setAttribute('d', `M${a0.x.toFixed(1)},${a0.y.toFixed(1)} L${p0.x.toFixed(1)},${p0.y.toFixed(1)}`);
      nl.el.setAttribute('d', `M${a1.x.toFixed(1)},${a1.y.toFixed(1)} L${p1.x.toFixed(1)},${p1.y.toFixed(1)}`);
      dim.el.setAttribute('d', `M${(p0.x + 24).toFixed(1)},${p0.y.toFixed(1)} L${(p1.x + 24).toFixed(1)},${p1.y.toFixed(1)}`);
      dt.el.style.left = (p0.x + 40) + 'px'; dt.el.style.top = (p0.y - 26) + 'px';
      nt.el.style.left = (p1.x + 40) + 'px'; nt.el.style.top = (p1.y + 4) + 'px';
      dd.el.style.left = (p0.x + 40) + 'px'; dd.el.style.top = ((p0.y + p1.y) / 2 - 18) + 'px';
    });
    const eqc = S.card('', { x: 90, y: 690, w: 900, h: 150, cls: 'glass' });
    eqc.in(c('6.1', 'shear') + 0.4, 0.5, 'rise');
    S.div('MOMENT AT THE NECK · A.3.3', { x: 120, y: 708, cls: 'tiny', style: 'color:#4fd1ff' }).in(c('6.1', 'shear') + 0.5, 0.5);
    const eq = S.eq(`M = M_w + Q_w\\cdot 0.6 = ${tn(A.Mw_kNm)} + ${tn(A.Qw_kN)}\\cdot 0.6 = \\cm{${(A.M_MNm).toFixed(2)}\\ \\mathrm{MNm}}`, { x: 120, y: 785, size: 31, align: 'left' });
    eq.in(c('6.1', 'shear') + 0.6, 1.0, 'write');
    eq.hl('', c('6.1', 'm'), { color: COL.amber });
  }

  // ------------------------------------------------------------------ 6.2 the pressure end load
  {
    const B = b('6.2');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · formula (B.7) · B.3.6.6.1', B.start + 0.3, B.end);
    S.div('The well pressure pulls on the housing too', { x: 110, y: 140, cls: 'h2' }).in(B.start + 0.3, 0.6, 'write');
    const e1 = S.eq('T_w = T_e + \\frac{\\pi}{4}\\,D_s^2\\,(p_i - p_e)', { x: 960, y: 330, size: 60 });
    e1.in(c('6.2', 'tw'), 0.9, 'write');
    S.div('true wall tension = applied tension + pressure end load on the gasket sealing diameter', { x: 960, y: 420, cls: 'small', anchor: 'ct' }).in(c('6.2', 'tw') + 0.8, 0.5);
    const e2 = S.eq(`\\frac{\\pi}{4}\\cdot ${Ld.D_s.toFixed(2)}^2\\cdot ${Ld.p_i} = ${Ld.end_load.toFixed(2)}\\ \\mathrm{MN}`, { x: 960, y: 560, size: 50 });
    e2.in(c('6.2', 'num'), 0.9, 'write');
    const e3 = S.eq(`T_w = ${(A.Te_kN / 1000).toFixed(2)} + ${Ld.end_load.toFixed(2)} = \\cm{${A.Tw_MN.toFixed(2)}\\ \\mathrm{MN}}`, { x: 960, y: 690, size: 54 });
    e3.in(c('6.2', 'res'), 0.9, 'write');
    const n = S.div(`p<sub>i</sub> = 690 bar (rated working pressure, B.3.6.6.1) · D<sub>s</sub> = ${Ld.D_s} m (illustrative) · external pressure ignored (conservative)`, { x: 960, y: 830, cls: 'small', anchor: 'ct' });
    n.in(c('6.2', 'num') + 1.2, 0.5);
  }

  // ------------------------------------------------------------------ 6.3 the check
  {
    const B = b('6.3');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · formula (B.7) · Table B.3', B.start + 0.3, B.end);
    const cc = capChart(S, D, { t: B.start + 0.4, fds: [0.67, 0.8, 0.9], exact: false });
    const cap = S.card(`<div class="ref">CAPACITIES · LIMIT LOAD METHOD</div><div style="font-size:28px;font-weight:650">M<sub>c</sub> = <span class="num c-amber">${D.ep.M_limit.toFixed(1)}</span> MNm &nbsp; T<sub>c</sub> = σ<sub>y</sub>·A = <span class="num c-amber">${sec.Tc.toFixed(0)}</span> MN</div>`, { x: 110, y: 170, w: 760, cls: 'glass' });
    cap.in(c('6.3', 'cap'), 0.6, 'rise');
    const eA = S.eq(`\\text{ALS:}\\ \\left(\\frac{${A.Tw_MN.toFixed(1)}}{${sec.Tc.toFixed(0)}} + \\frac{${A.M_MNm.toFixed(2)}}{${D.ep.M_limit.toFixed(1)}}\\right)\\frac{1}{0.9} = \\cg{${ck.als.uf.toFixed(2)}}`, { x: 110, y: 430, size: 42, align: 'left' });
    eA.in(c('6.3', 'als'), 1.0, 'write');
    cc.point(A.M_MNm, A.Tw_MN, { tt: c('6.3', 'als') + 0.6, color: COL.coral, label: 'ALS', dx: 18, dy: -26 });
    stamp(S, `${ck.als.uf.toFixed(2)} ≤ 1 · PASS`, { x: 470, y: 530, t: c('6.3', 'uf'), kind: 'pass' });
    const eU = S.eq(`\\text{ULS:}\\ \\left(\\frac{${U.Tw_MN.toFixed(1)}}{${sec.Tc.toFixed(0)}} + \\frac{${U.M_MNm.toFixed(2)}}{${D.ep.M_limit.toFixed(1)}}\\right)\\frac{1}{0.8} = \\cg{${ck.uls.uf.toFixed(2)}}`, { x: 110, y: 660, size: 42, align: 'left' });
    eU.in(c('6.3', 'uls'), 1.0, 'write');
    cc.point(U.M_MNm, U.Tw_MN, { tt: c('6.3', 'uls') + 0.5, color: COL.amber, label: 'ULS', dx: 18, dy: -26 });
    stamp(S, `${ck.uls.uf.toFixed(2)} ≤ 1 · PASS`, { x: 470, y: 760, t: c('6.3', 'uls') + 1.6, kind: 'pass' });
    const cmp = S.card(`<div class="ref">SAME NECK, SAME LOADS</div><div style="font-size:27px;font-weight:650">elastic route <span class="num c-red">${D.elastic.als.uf_PL.toFixed(2)}</span> (first yield through the wall) &nbsp;·&nbsp; elastic-plastic <span class="num c-green">${ck.als.uf.toFixed(2)}</span> (full section)</div>`, { x: 110, y: 880, w: 800, cls: 'glass', style: 'padding:16px 28px' });
    cmp.in(c('6.3', 'compare'), 0.6, 'rise');
  }

  // ------------------------------------------------------------------ 6.4 the other checks and the verdict
  {
    const B = b('6.4');
    const tV = c('6.4', 'verdict');
    const S = new Scene(B.start, tV + 0.2);
    clause('NORSOK U-001:2026 · B.3.6.3 · B.3.6.4 · B.2.3 b) · B.7.6', B.start + 0.3, B.end);
    S.div('The other failure modes', { x: 110, y: 140, cls: 'h2' }).in(B.start + 0.3, 0.6, 'write');
    const row = (y, t, ok, title, body) => {
      const a = S.card(`<div style="display:flex;gap:22px;align-items:flex-start"><div style="font-size:40px;font-weight:800;color:${ok ? '#46d39a' : '#ffb547'};line-height:1">${ok ? '✓' : '→'}</div>
        <div><div style="font-weight:750;font-size:32px">${title}</div><div class="small">${body}</div></div></div>`, { x: 110, y, w: 1500, cls: 'glass' });
      a.in(t, 0.6, 'left');
    };
    row(250, c('6.4', 'local'), true, 'Local failure: exempt', '75K forging meets the ductility requirements of B.3.6.3.3 (elongation ≥ 17 %, reduction of area ≥ 35 %)');
    row(420, c('6.4', 'buck'), true, 'Buckling: not an issue', `thick wall, D/t = ${sec.Dt.toFixed(2)}`);
    row(590, c('6.4', 'func'), false, 'Functional capacities of the connector', 'hub face separation, gasket leak tightness at minimum preload: supplier data; connector capacities from FE validated by a full-scale test (B.2.3 b, B.7.6)');
    // verdict on the red spot
    const cam = camSpline([
      { t: tV - 0.8, p: [1.1, 3.58, 2.3], l: [0.12, 3.33, 0], fov: 30 },
      { t: B.end, p: [0.95, 3.55, 2.0], l: [0.14, 3.34, 0], fov: 30 },
    ]);
    W3.shot(tV - 0.8, B.end, {
      show: ['feHousing'], fadeIn: 0.8, fadeOut: 0.6, cam, fog: 0, bg: '#0b1824',
      update: () => { feSetElastic({ Mw: A.Mw_kNm / 1000, Qw: A.Qw_kN / 1000, Tw: A.Tw_MN, p: Ld.p_i }); FEU.uFE.value = 1; md.feHousing.userData.lines.material.opacity = 0.5; },
    });
    const S2 = new Scene(tV - 0.6, B.end);
    probe3D(S2, [0.352, 3.416, 0.0], `<span style="font-size:36px;font-weight:800;color:#ff5a4a" class="num">793 MPa</span><span class="sub">peak, neck fillet</span>`, { t0: tV, t1: B.end, dx: -420, dy: 160, color: '#ff5a4a' });
    vmLegend(S2, { x: 1630, y: 250, t0: tV, t1: B.end });
    const v = S2.card(`<div class="ref" style="color:#46d39a">VERDICT</div><div style="font-weight:800;font-size:46px">acceptable</div><div class="small">utilisation <span class="num">${ck.als.uf.toFixed(2)}</span> at the accidental load · F<sub>d</sub> = 0.9</div>`, { x: 110, y: 160, w: 560, cls: 'glass', style: 'border-color:rgba(70,211,154,0.6)' });
    v.in(tV + 0.8, 0.7, 'pop');
  }
}
