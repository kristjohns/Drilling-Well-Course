// Chapter 5 — where strain is the criterion: studs/segments in bending (0.2 % through the section), local failure
// (triaxiality-dependent strain limit, ASME VIII-3 KD-232), the ductility exemption, the remaining failure modes.
import { E, ease, COL, clamp, smooth, ramp, lerp, fmt } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause } from '../engine/hud.js';
import { quoteCard, stamp } from './kit.js';

export async function build(E, T, D) {
  const ch = T.ch(5);
  titleCard(ch, 'The yielding capacity is a load. Strain enters in exactly two places');
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);
  const mat = D.material, EL = D.elastic.als, lf = D.local;

  // ------------------------------------------------------------------ 5.1 so, is it a strain limit?
  {
    const B = b('5.1');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.3.6.3.2 · 3.2.54 yielding capacity', B.start + 0.3, B.end);
    const st = S.card(`<div class="ref">YIELDING CAPACITY</div><div style="font-weight:800;font-size:56px;line-height:1.1">a <span class="c-amber">LOAD</span>, not a strain</div>
      <div class="small" style="margin-top:10px">limit load, or factored plastic collapse load · read off the load–rotation curve</div>`, { x: 960, y: 190, w: 1200, cls: 'glass', anchor: 'ct', style: 'text-align:center' });
    st.in(c('5.1', 'no') - 0.2, 0.7, 'rise');
    const ex = (x, n, title, body) => {
      const a = S.card(`<div style="display:flex;gap:18px;align-items:center;margin-bottom:12px"><div style="width:58px;height:58px;border-radius:16px;background:#46d39a;color:#06121c;font-weight:800;font-size:32px;display:flex;align-items:center;justify-content:center">${n}</div>
        <div style="font-weight:750;font-size:32px">${title}</div></div><div class="small">${body}</div>`, { x, y: 560, w: 760, cls: 'glass' });
      a.in(c('5.1', 'two') + (n - 1) * 0.8, 0.6, 'rise');
    };
    S.div('Strain becomes the criterion in exactly two places', { x: 960, y: 490, cls: 'h3', anchor: 'ct', style: 'color:#46d39a' }).in(c('5.1', 'two') - 0.3, 0.5);
    ex(160, 1, 'Studs and segments in bending', '0.2 % equivalent plastic strain through the whole root cross section (B.3.6.3.2.2, Figure B.7)');
    ex(1000, 2, 'Local failure', 'accumulated plastic strain against a limit that falls with triaxiality (B.3.6.3.3, ASME VIII-3 KD-232)');
  }

  // ------------------------------------------------------------------ 5.2 studs in bending
  {
    const B = b('5.2');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.3.6.3.2.2/3 · Figure B.7 · 3.2.54 note 2', B.start + 0.3, B.end);
    // flange pair in section with two studs, bending moment
    const g = S.g(); g.in(c('5.2', 'studs') - 0.2, 0.6, 'none');
    const P = (d, o) => S.path(d, { parent: g.el, o: 1, ...o });
    const cx = 520, cy = 560;
    P(`M${cx - 70},${cy - 330} L${cx - 70},${cy - 40} L${cx + 70},${cy - 40} L${cx + 70},${cy - 330}`, { stroke: '#d7e3ec', width: 3, fill: 'rgba(127,147,166,0.45)' });           // upper pipe
    P(`M${cx - 70},${cy + 330} L${cx - 70},${cy + 40} L${cx + 70},${cy + 40} L${cx + 70},${cy + 330}`, { stroke: '#d7e3ec', width: 3, fill: 'rgba(127,147,166,0.45)' });           // lower pipe
    P(`M${cx - 300},${cy - 80} L${cx + 300},${cy - 80} L${cx + 300},${cy - 2} L${cx - 300},${cy - 2} Z`, { stroke: '#d7e3ec', width: 3, fill: '#5f7486' });                          // upper flange
    P(`M${cx - 300},${cy + 2} L${cx + 300},${cy + 2} L${cx + 300},${cy + 80} L${cx - 300},${cy + 80} Z`, { stroke: '#d7e3ec', width: 3, fill: '#5f7486' });                          // lower flange
    const stud = (x, hot) => {
      P(`M${x - 16},${cy - 140} L${x + 16},${cy - 140} L${x + 16},${cy + 140} L${x - 16},${cy + 140} Z`, { stroke: '#e9f2f9', width: 2, fill: hot ? '#c0503c' : '#9fb2c2' });
      P(`M${x - 34},${cy - 140} L${x + 34},${cy - 140} L${x + 34},${cy - 100} L${x - 34},${cy - 100} Z`, { stroke: '#e9f2f9', width: 2, fill: '#3d4853' });
      P(`M${x - 34},${cy + 100} L${x + 34},${cy + 100} L${x + 34},${cy + 140} L${x - 34},${cy + 140} Z`, { stroke: '#e9f2f9', width: 2, fill: '#3d4853' });
    };
    stud(cx - 220, false); stud(cx + 220, true);
    const mArc = S.path(`M${cx - 140},${cy - 380} A150,150 0 0 1 ${cx + 140},${cy - 380}`, { stroke: COL.amber, width: 6 });
    const mTip = S.path(`M${cx + 122},${cy - 400} L${cx + 146},${cy - 372} L${cx + 112},${cy - 366} Z`, { stroke: COL.amber, width: 1, fill: COL.amber });
    mArc.in(c('5.2', 'studs') + 0.4, 0.5, 'none'); mTip.in(c('5.2', 'studs') + 0.4, 0.5, 'none');
    S.div('bending moment', { x: cx + 170, y: cy - 415, cls: 'small c-amber', anchor: 'lm' }).in(c('5.2', 'studs') + 0.6, 0.5);
    S.div('most loaded stud', { x: cx + 260, y: cy + 170, cls: 'small', style: 'color:#ff8a6a' }).in(c('5.2', 'studs') + 1.0, 0.5);
    // root cross section of the stud: the zone above 0.2 % equivalent plastic strain sweeps across it
    const ox = 1380, oy = 520, R = 190;
    const cid = 'stud' + Math.random().toString(36).slice(2, 7);
    const cp = document.createElementNS('http://www.w3.org/2000/svg', 'clipPath'); cp.setAttribute('id', cid);
    const cc = document.createElementNS('http://www.w3.org/2000/svg', 'circle'); cc.setAttribute('cx', ox); cc.setAttribute('cy', oy); cc.setAttribute('r', R);
    cp.appendChild(cc); S.svg.querySelector('defs').appendChild(cp);
    const g2 = S.g(); g2.in(c('5.2', 'why') - 0.5, 0.6, 'none');
    S.circle(ox, oy, R, { fill: '#2a4d8f', stroke: 'none', parent: g2.el, o: 1 });
    const inner = document.createElementNS('http://www.w3.org/2000/svg', 'g'); inner.setAttribute('clip-path', `url(#${cid})`); g2.el.appendChild(inner);
    const zone = S.path('M0,0', { stroke: 'none', fill: '#ff8a3d', parent: inner, o: 1 });
    const edge = S.path('M0,0', { stroke: '#ffffff', width: 4, parent: inner, o: 1 });
    S.circle(ox, oy, R, { fill: 'none', stroke: '#e9f2f9', width: 4, parent: g2.el, o: 1 });
    const t0 = c('5.2', 'why') + 0.6, t1 = c('5.2', 'through') + 3.5;
    E.anim(B.start, B.end, (t) => {
      const u = ease.inOut(clamp((t - t0) / (t1 - t0)));
      const xe = ox + R + 4 - u * (2 * R + 8);                 // the 0.2 % front moves from the tension edge across the section
      const bow = 40 * Math.sin(Math.PI * u);
      zone.el.setAttribute('d', `M${ox + R + 10},${oy - R - 10} L${xe},${oy - R - 10} Q${xe - bow},${oy} ${xe},${oy + R + 10} L${ox + R + 10},${oy + R + 10} Z`);
      edge.el.setAttribute('d', u > 0.001 && u < 0.999 ? `M${xe},${oy - R - 10} Q${xe - bow},${oy} ${xe},${oy + R + 10}` : 'M0,0');
    });
    S.div('stud root cross section', { x: ox, y: oy + R + 30, cls: 'small', anchor: 'ct' }).in(c('5.2', 'why'), 0.5);
    const k1 = S.div('<span style="color:#ff8a3d">■</span> ≥ 0.2 % equivalent plastic strain', { x: ox, y: oy + R + 72, cls: 'small', anchor: 'ct' });
    k1.in(c('5.2', 'why') + 0.4, 0.5);
    const cap = S.card(`<div class="ref">YIELDING CAPACITY OF THE STUD</div><div style="font-weight:700;font-size:28px">the load at which the <span class="c-amber">whole root section</span> has reached 0.2 % equivalent plastic strain</div>`, { x: ox, y: 110, w: 760, cls: 'glass', anchor: 'ct' });
    cap.in(c('5.2', 'through'), 0.6, 'rise');
    const sl = S.card(`<div class="small" style="font-size:25px">yielded right through → permanently stretched → <span class="c-red">preload lost</span></div>`, { x: ox, y: 900, w: 760, cls: 'glass', anchor: 'ct', style: 'text-align:center' });
    sl.in(c('5.2', 'stretch'), 0.6, 'rise');
    const ex = S.div('also: segments in clamps, connector locking segments', { x: cx, y: 940, cls: 'small', anchor: 'ct' });
    ex.in(c('5.2', 'studs') + 2.6, 0.5);
  }

  // ------------------------------------------------------------------ 5.3 local failure
  {
    const B = b('5.3');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · 3.2.27 · B.3.6.3.3 · ASME BPVC VIII-3 KD-232', B.start + 0.3, B.end);
    // microvoids at a notch: nucleate, grow, coalesce
    const mx = 400, my = 360, MR = 230;
    const cid = 'void' + Math.random().toString(36).slice(2, 7);
    const cp = document.createElementNS('http://www.w3.org/2000/svg', 'clipPath'); cp.setAttribute('id', cid);
    const cc = document.createElementNS('http://www.w3.org/2000/svg', 'circle'); cc.setAttribute('cx', mx); cc.setAttribute('cy', my); cc.setAttribute('r', MR);
    cp.appendChild(cc); S.svg.querySelector('defs').appendChild(cp);
    const g = S.g(); g.in(c('5.3', 'def') - 0.4, 0.6, 'none');
    S.circle(mx, my, MR, { fill: '#7f93a6', stroke: 'none', parent: g.el, o: 1 });
    const inner = document.createElementNS('http://www.w3.org/2000/svg', 'g'); inner.setAttribute('clip-path', `url(#${cid})`); g.el.appendChild(inner);
    S.path(`M${mx - MR},${my - 40} L${mx + 30},${my - 6} Q${mx + 46},${my} ${mx + 30},${my + 6} L${mx - MR},${my + 40} Z`, { stroke: '#e9f2f9', width: 3, fill: '#0b1824', parent: inner, o: 1 });    // notch
    const voids = [];
    const rr = (k) => ((Math.sin(k * 12.9898) * 43758.5453) % 1 + 1) % 1;
    for (let k = 0; k < 16; k++) {
      const vx = mx + 52 + rr(k) * 120, vy = my + (rr(k + 40) - 0.5) * 120;
      voids.push([vx, vy, S.circle(vx, vy, 1, { fill: '#0b1824', stroke: 'none', parent: inner, o: 1 }), rr(k + 80)]);
    }
    const crack = S.path(`M${mx + 38},${my} L${mx + 70},${my - 4} L${mx + 102},${my + 5} L${mx + 134},${my - 3} L${mx + 170},${my + 4}`, { stroke: '#0b1824', width: 9, parent: inner, o: 1 });
    crack.set(0, { draw: 0 });
    S.circle(mx, my, MR, { fill: 'none', stroke: '#e9f2f9', width: 4, parent: g.el, o: 1 });
    const tv = c('5.3', 'def');
    E.anim(tv, B.end, (t) => {
      for (const [vx, vy, v, ph] of voids) {
        const u = clamp((t - tv - 1.0 - ph * 2.0) / 4.0);
        v.el.setAttribute('r', (u <= 0 ? 0 : 2 + 9 * ease.out(u)).toFixed(2));
      }
    });
    crack.to(tv + 6.0, 2.5, { draw: 1 }, ease.inOut);
    const vl = S.div('voids form → grow → join into a ductile crack', { x: mx, y: my + MR + 24, cls: 'small', anchor: 'ct' });
    vl.in(tv + 1.0, 0.5);
    // triaxiality
    const tri = S.eq('T = \\frac{\\sigma_m}{\\sigma_e} = \\frac{(\\sigma_1+\\sigma_2+\\sigma_3)/3}{\\sigma_e}', { x: 120, y: 760, size: 44, align: 'left' });
    tri.in(c('5.3', 'tri'), 0.9, 'write');
    const t13 = S.div('tensile test: T = ⅓ &nbsp;·&nbsp; constrained notch: T &gt; 1', { x: 124, y: 840, cls: 'small' });
    t13.in(c('5.3', 'notch'), 0.6);
    // strain limit
    const lim = S.eq('\\varepsilon_L = \\varepsilon_{Lu}\\,\\exp\\!\\left[-\\frac{\\alpha_{sl}}{1+m_2}\\left(T-\\tfrac{1}{3}\\right)\\right]', { x: 1400, y: 170, size: 44 });
    lim.in(c('5.3', 'limit'), 1.0, 'write');
    const chl = S.chart({ x: 1020, y: 300, w: 780, h: 440, xmin: 0, xmax: 2, ymin: 0, ymax: 2, xticks: [0, 0.5, 1, 1.5, 2], yticks: [0, 0.5, 1, 1.5, 2],
      xfmt: (v) => v.toFixed(1), yfmt: (v) => v.toFixed(1), xlabel: 'Triaxiality T', ylabel: 'ε<sub>L</sub> / ε<sub>Lu</sub>' });
    chl.show(c('5.3', 'limit') + 0.6);
    chl.curve(lf.curve, { color: COL.coral, width: 5, t: c('5.3', 'limit') + 1.0, d: 1.6 });
    chl.dot(1 / 3, 1, { color: '#ffffff', r: 9, t: c('5.3', 'limit') + 2.4 });
    const p1 = S.div('tensile test', { x: chl.X(1 / 3) + 16, y: chl.Y(1) - 34, cls: 'small' });
    p1.in(c('5.3', 'limit') + 2.6, 0.5);
    chl.dot(lf.notch_T, lf.notch_ratio, { color: COL.amber, r: 10, t: c('5.3', 'drop') });
    const p2 = S.div(`T = ${lf.notch_T} → only <span class="num c-amber">${Math.round(lf.notch_ratio * 100)} %</span> of the ductility`, { x: chl.X(lf.notch_T) - 10, y: chl.Y(lf.notch_ratio) - 60, cls: 'small', anchor: 'rm' });
    p2.in(c('5.3', 'drop') + 0.3, 0.5);
    const cf = S.div(`shape for ferritic steel: α<sub>sl</sub> = ${lf.alpha_sl}, m<sub>2</sub> = 0.6(1 − σ<sub>y</sub>/σ<sub>u</sub>) = ${lf.m2.toFixed(3)} · coefficients from Table KM-620`, { x: 1020, y: 818, w: 800, cls: 'tiny', style: 'font-size:17px' });
    cf.in(c('5.3', 'limit') + 3.0, 0.5);
    // damage over the load history
    const dm = S.eq('D_\\varepsilon = \\sum_k \\frac{\\Delta\\varepsilon_{peq,k}}{\\varepsilon_{L,k}} \\le 1.0', { x: 1400, y: 915, size: 40 });
    dm.in(c('5.3', 'damage'), 0.9, 'write');
    const hist = S.div('load history: preload → hydrostatic pressure test → yielding capacity', { x: 1400, y: 975, cls: 'small', anchor: 'ct' });
    hist.in(c('5.3', 'damage') + 1.2, 0.5);
    const lfac = S.div('ASME load factor for the local criterion (Table KD-230.4) set to <span class="c-amber">1.0</span>', { x: 1400, y: 1018, cls: 'small', anchor: 'ct' });
    lfac.in(c('5.3', 'factor'), 0.6);
    quoteCard(S, '3.2.27 · local failure', 'initiation of a ductile crack at a point of <span class="q">elevated triaxial stress</span>, through microvoid nucleation, growth and coalescence', { x: 1020, y: 320, w: 780, t: c('5.3', 'def') + 0.5, size: 28 }).out(c('5.3', 'limit') - 0.4, 0.4);
  }

  // ------------------------------------------------------------------ 5.4 the ductility exemption
  {
    const B = b('5.4');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.3.6.3.3 a) b) · B.3.5.3 · D.7.2', B.start + 0.3, B.end);
    S.div('The shortcut: ductile enough → no local failure check', { x: 110, y: 140, cls: 'h2' }).in(c('5.4', 'duct') - 0.3, 0.6, 'write');
    const tb = S.card(`<div class="ref">CARBON AND LOW-ALLOY STEELS (INCL. BOLTING)</div>
      <table class="t" style="margin-top:10px;font-size:26px"><thead><tr><th class="l">SMYS</th><th>Elongation in 50 mm, min.</th><th>Reduction of area, min.</th></tr></thead>
      <tbody><tr><td class="l">≤ 655 MPa</td><td>17 %</td><td>35 %</td></tr><tr><td class="l">655 – 830 MPa</td><td>16 %</td><td>45 %</td></tr></tbody></table>`, { x: 110, y: 250, w: 980, cls: 'glass' });
    tb.in(c('5.4', 'el') - 0.2, 0.6, 'rise');
    const bo = S.card(`<div class="ref">D.7.2</div><div style="font-weight:700;font-size:28px">Low-alloy studs and nuts made to D.7.2: no local failure check</div>`, { x: 110, y: 560, w: 980, cls: 'glass' });
    bo.in(c('5.4', 'bolts'), 0.6, 'rise');
    const us = S.card(`<div class="ref">OUR HOUSING · API 75K</div><div style="font-weight:750;font-size:34px">min. elongation <span class="num">${mat.elong_min}</span> % · min. reduction of area <span class="num">${mat.ra_min}</span> %</div>`, { x: 1160, y: 250, w: 650, cls: 'glass' });
    us.in(c('5.4', 'us'), 0.6, 'rise');
    stamp(S, 'meets B.3.6.3.3 · exempt', { x: 1485, y: 490, t: c('5.4', 'us') + 0.8, kind: 'pass', size: 26 });
    const el = S.eq('\\sigma_1+\\sigma_2+\\sigma_3 \\;\\le\\; 2.5\\cdot\\mathrm{SMYS}', { x: 960, y: 830, size: 50 });
    el.in(c('5.4', 'el2'), 0.9, 'write');
    S.div(`elastic route (B.3.5.3) · at our fillet: <span class="num">${fmt(EL.tri_sum_out)}</span> ≤ <span class="num">${fmt(EL.tri_limit)}</span> MPa`, { x: 960, y: 910, cls: 'small', anchor: 'ct' }).in(c('5.4', 'el2') + 1.2, 0.5);
  }

  // ------------------------------------------------------------------ 5.5 the other failure modes
  {
    const B = b('5.5');
    const S = new Scene(B.start, B.end);
    clause('NORSOK U-001:2026 · B.3.6.3.4–B.3.6.3.6 · B.3.6.4', B.start + 0.3, B.end);
    S.div('The remaining modes: load-based again', { x: 960, y: 140, cls: 'h2', anchor: 'ct' }).in(B.start + 0.3, 0.6, 'write');
    const card = (x, y, ref, title, body, t, color) => {
      const a = S.card(`<div class="ref" style="color:${color}">${ref}</div><div style="font-weight:750;font-size:34px;margin-bottom:8px">${title}</div><div class="small">${body}</div>`, { x, y, w: 820, cls: 'glass' });
      a.in(t - 0.2, 0.6, 'rise');
    };
    card(110, 260, 'B.3.6.3.6', 'Buckling = max load / 1.10', 'global, local (wrinkling) and hoop buckling; include imperfections; check all mode shapes', c('5.5', 'buck'), COL.cyan);
    card(990, 260, 'B.3.6.3.5', 'Disengagement = load / 1.1', 'load at disengagement of the first load shoulder or thread', c('5.5', 'dis'), COL.violet);
    card(110, 560, 'B.3.6.3.4 · KD-234', 'Ratcheting: only above 180 °C', 'design temperatures up to and including 180 °C are exempt', c('5.5', 'ratch'), COL.amber);
    card(990, 560, 'B.3.6.4 · TABLE B.3', 'Functional capacities: F<sub>d</sub> = 1.0', 'hub face separation, leak tightness, galling, loss of function · manufacturer criteria, validated by testing', c('5.5', 'funct'), COL.green);
  }
}
