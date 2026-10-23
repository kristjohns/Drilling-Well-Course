// Helpers shared by the chapters: well sway, FE legend, probes and load arrows that follow the 3D camera.
import { E, ease, COL, clamp, fmt } from '../engine/core.js';
import { later } from '../engine/scene.js';
import { DEF, DEF_N } from '../three/world.js';

// lateral deflection shape of the well under a riser load (unit at the datum): straight above the datum (the stack
// leans with it), bending between datum and mudline, a decaying wave in the soil. Fills DEF.uDefl once.
export function setSwayShape() {
  const y0 = DEF.uY0.value, y1 = DEF.uY1.value;
  for (let i = 0; i < DEF_N; i++) {
    const y = y0 + (y1 - y0) * i / (DEF_N - 1);
    let v;
    if (y >= 4.0) v = 1 + 0.42 * (y - 4.0);
    else if (y >= 0) { const u = y / 4.0; v = 0.32 + 0.68 * (u * u * (1.6 - 0.6 * u)); }
    else { const b = 0.22; v = 0.32 * Math.exp(b * y) * Math.cos(b * y); }
    DEF.uDefl.value[i] = v * 0.06;
    DEF.uStress.value[i] = 0;
  }
}

// banded legend of the FE contour (von Mises, MPa) with the yield strength marked
export function vmLegend(S, { x = 1630, y = 230, vmax = 800, bands = 9, sy = 517, t0, t1, title = 'von Mises stress · MPa' } = {}) {
  const h = 46 * bands;
  const jet = (u) => {
    const c = (v) => Math.round(255 * clamp(v));
    return `rgb(${c(1.5 - Math.abs(4 * u - 3))},${c(1.5 - Math.abs(4 * u - 2))},${c(1.5 - Math.abs(4 * u - 1))})`;
  };
  let sw = '';
  for (let k = bands - 1; k >= 0; k--) sw += `<div style="height:46px;background:${jet((k + 0.5) / bands)}"></div>`;
  let lab = '';
  for (let k = 0; k <= bands; k++) lab += `<div style="position:absolute;left:58px;top:${h - k * 46 - 13}px" class="num">${fmt(vmax * k / bands)}</div>`;
  const ys = h - sy / vmax * h;
  lab += `<div style="position:absolute;left:-14px;top:${ys - 1.5}px;width:58px;height:3px;background:#fff"></div>`;
  lab += `<div style="position:absolute;left:-150px;top:${ys - 15}px;font-weight:700;font-size:21px;color:#fff;white-space:nowrap">σ<sub>y</sub> ${sy}</div>`;
  const c = S.card(`<div class="tiny" style="margin-bottom:14px;letter-spacing:0.12em;text-transform:uppercase">${title}</div>
    <div style="position:relative;width:150px;height:${h}px"><div style="width:44px;border-radius:6px;overflow:hidden;border:1px solid rgba(255,255,255,0.25)">${sw}</div>${lab}</div>`,
  { x, y, cls: 'glass', style: 'padding:22px 26px 26px 26px;width:230px' });
  if (t0 !== undefined) c.in(t0, 0.6, 'left');
  if (t1 !== undefined) c.out(t1, 0.5);
  return c;
}

// legend of the equivalent plastic strain contour
export function peLegend(S, { x = 1600, y = 260, t0, t1 } = {}) {
  const row = (col, txt, border = '') => `<div style="display:flex;align-items:center;gap:14px;margin:7px 0"><div style="width:44px;height:30px;border-radius:5px;background:${col};${border}"></div><div class="small" style="font-size:22px">${txt}</div></div>`;
  const c = S.card(`<div class="tiny" style="margin-bottom:12px;letter-spacing:0.12em;text-transform:uppercase">Equivalent plastic strain</div>
    ${row('rgb(255,90,40)', '≥ 1 %')}${row('rgb(255,200,40)', '0.5 %')}${row('rgb(150,255,90)', '0.2 % · yielded')}
    <div style="height:3px;background:#fff;margin:4px 0 4px 0;border-radius:2px"></div>
    ${row('linear-gradient(90deg,#1a8cf2,#33e6f2)', '0 – 0.2 %')}${row('rgb(41,77,158)', 'elastic')}`, { x, y, cls: 'glass', style: 'padding:22px 26px' });
  if (t0 !== undefined) c.in(t0, 0.6, 'left');
  if (t1 !== undefined) c.out(t1, 0.5);
  return c;
}

// a label with a leader line to a 3D point; pos may be a function of t
export function probe3D(S, pos, html, { t0, t1, dx = 120, dy = -80, color = COL.ink, cls = '' } = {}) {
  const lab = S.label(html, { x: 0, y: 0, cls });
  const dot = S.circle(0, 0, 7, { fill: color, stroke: '#06121c', width: 2 });
  const ring = S.circle(0, 0, 15, { fill: 'none', stroke: color, width: 2.5 });
  const ln = S.path('M0,0 L0,0', { stroke: color, width: 2, opacity: 0.85 });
  for (const a of [lab, dot, ring, ln]) { a.in(t0, 0.45, 'none'); if (t1 !== undefined) a.out(t1 - 0.4, 0.4); }
  let wh = null;
  E.anim(t0 - 0.1, (t1 ?? t0 + 3600) + 0.1, (t) => {
    const p = E.world.project(typeof pos === 'function' ? pos(t) : pos, t);
    if (!wh) wh = [lab.el.offsetWidth, lab.el.offsetHeight];
    const lx = p.x + dx, ly = p.y + dy;
    const left = dx >= 0 ? lx : lx - wh[0];
    lab.el.style.left = left.toFixed(1) + 'px'; lab.el.style.top = (ly - wh[1] / 2).toFixed(1) + 'px';
    for (const c of [dot, ring]) { c.el.setAttribute('cx', p.x.toFixed(1)); c.el.setAttribute('cy', p.y.toFixed(1)); }
    ln.el.setAttribute('d', `M${p.x.toFixed(1)},${p.y.toFixed(1)} L${lx.toFixed(1)},${ly.toFixed(1)}`);
  });
  return { lab, dot, ring, ln };
}

// load arrows at a 3D point (the wellhead datum): tension up, shear sideways, bending as a curved arrow
export function datumLoads(S, pos, { t0, t1, scale = 1, labels = {}, color = COL.amber, show = ['T', 'Q', 'M'] } = {}) {
  const g = S.g();
  const mk = (name) => S.path('M0,0', { stroke: color, width: 6, parent: g.el, o: 1 });
  const parts = {};
  for (const k of show) { parts[k] = mk(k); parts[k + 'h'] = S.path('M0,0', { stroke: color, width: 1, fill: color, parent: g.el, o: 1 }); }
  const labs = {};
  for (const k of show) {
    labs[k] = S.label(labels[k] || k, { x: 0, y: 0, cls: 'c-amber' });
    labs[k].el.style.color = color;
    labs[k].in(t0 + 0.3, 0.5, 'none');
    if (t1 !== undefined) labs[k].out(t1 - 0.4, 0.4);
  }
  g.in(t0, 0.5, 'none'); if (t1 !== undefined) g.out(t1 - 0.4, 0.4);
  const head = (x2, y2, ang, s = 18) => {
    const hx = (a) => x2 - Math.cos(ang + a) * s, hy = (a) => y2 - Math.sin(ang + a) * s;
    return `M${hx(0.45).toFixed(1)},${hy(0.45).toFixed(1)} L${x2.toFixed(1)},${y2.toFixed(1)} L${hx(-0.45).toFixed(1)},${hy(-0.45).toFixed(1)} Z`;
  };
  let wh = {};
  E.anim(t0 - 0.1, (t1 ?? t0 + 3600) + 0.1, (t) => {
    const p = E.world.project(typeof pos === 'function' ? pos(t) : pos, t);
    const s = scale;
    if (parts.T) {
      const x = p.x, y0 = p.y - 30 * s, y1 = p.y - 150 * s;
      parts.T.el.setAttribute('d', `M${x},${y0} L${x},${y1 + 14}`);
      parts.Th.el.setAttribute('d', head(x, y1, -Math.PI / 2));
      place(labs.T, x + 16, y1 - 6, 'l');
    }
    if (parts.Q) {
      const y = p.y + 4, x0 = p.x - 200 * s, x1 = p.x - 50 * s;
      parts.Q.el.setAttribute('d', `M${x0},${y} L${x1 - 14},${y}`);
      parts.Qh.el.setAttribute('d', head(x1, y, 0));
      place(labs.Q, x0 - 12, y, 'r');
    }
    if (parts.M) {
      const R = 95 * s, cx = p.x, cy = p.y - 10 * s;
      const a0 = Math.PI * 1.15, a1 = Math.PI * 1.85;
      const x0 = cx + R * Math.cos(a0), y0 = cy + R * Math.sin(a0), x1 = cx + R * Math.cos(a1), y1 = cy + R * Math.sin(a1);
      parts.M.el.setAttribute('d', `M${x0.toFixed(1)},${y0.toFixed(1)} A${R},${R} 0 0 1 ${x1.toFixed(1)},${y1.toFixed(1)}`);
      parts.Mh.el.setAttribute('d', head(x1, y1, a1 + Math.PI / 2 - 0.15));
      place(labs.M, x1 + 20, y1 - 10, 'l');
    }
  });
  function place(lab, x, y, side) {
    const k = lab.el;
    const w = k.offsetWidth, h = k.offsetHeight;
    k.style.left = (side === 'l' ? x : x - w).toFixed(1) + 'px'; k.style.top = (y - h / 2).toFixed(1) + 'px';
  }
  return { g, labs };
}

// thin banner at the top centre ("teaching stand-in" style notes)
export function note(S, html, { x = 1872, y = 1058, t0, t1, anchor = 'rm', w = null } = {}) {
  const n = S.div(html, { x, y, anchor, cls: 'tiny', w, style: 'color:#7f97aa;letter-spacing:0.08em;text-transform:none;font-size:19px' });
  if (t0 !== undefined) n.in(t0, 0.5, 'none');
  if (t1 !== undefined) n.out(t1, 0.4);
  return n;
}

export const sleep = () => later(() => {});
export { ease };

// capacity chart in the (M, Tw) plane: formula (B.7) lines for the design factors, optional exact plastic interaction
export function capChart(S, D, { x = 980, y = 200, w = 820, h = 640, t, fds = [0.67, 0.8, 0.9], exact = true, labels = true, cues = {} } = {}) {
  const Tc = D.section.Tc, Mc = D.ep.M_limit;
  const chart = S.chart({ x, y, w, h, xmin: 0, xmax: 22, ymin: 0, ymax: 112, xticks: [0, 4, 8, 12, 16, 20], yticks: [0, 20, 40, 60, 80, 100],
    xlabel: 'Bending moment M · MNm', ylabel: 'True wall tension T<sub>w</sub> · MN', title: 'COMBINED LOAD CAPACITY · FORMULA (B.7)' });
  chart.show(t);
  const colors = { 0.67: COL.cyan, 0.8: COL.amber, 0.9: COL.coral, 1: '#e9f2f9' };
  const names = { 0.67: 'normal · F<sub>d</sub> 0.67', 0.8: 'extreme · F<sub>d</sub> 0.8', 0.9: 'accidental · F<sub>d</sub> 0.9', 1: 'capacity · F<sub>d</sub> 1.0' };
  const out = { chart, lines: {} };
  const cap1 = chart.curve([[0, Tc], [Mc, 0]], { color: '#e9f2f9', width: 2.5, dash: '6 6', t: t + 0.4, d: 0.6 });
  out.cap1 = cap1;
  if (exact) {
    const ex = chart.curve(D.ep.interaction.map(([m, n]) => [m, n]), { color: '#7f97aa', width: 2.5, dash: '3 7', t: (cues.exact ?? t + 1.0), d: 0.8 });
    const el = S.div('exact plastic interaction<br>(section model)', { x: chart.X(19.4), y: chart.Y(40), cls: 'tiny', style: 'color:#9fb2c2;font-size:17px' });
    el.in((cues.exact ?? t + 1.0) + 0.5, 0.5);
    out.ex = ex; out.el = el;
  }
  const rows = [];
  fds.forEach((fd, i) => {
    const tt = cues[fd] ?? t + 1.2 + i * 0.5;
    out.lines[fd] = chart.curve([[0, fd * Tc], [fd * Mc, 0]], { color: colors[fd], width: 4, t: tt, d: 0.7 });
    rows.push([fd, tt]);
  });
  if (labels) {
    const leg = S.card(`<div class="tiny" style="margin-bottom:6px">ENVELOPES</div>` +
      rows.map(([fd]) => `<div class="lg" style="display:flex;align-items:center;gap:12px;font-size:20px;margin:4px 0"><span style="width:28px;height:5px;background:${colors[fd]};flex:none"></span><span>${names[fd]}</span></div>`).join('') +
      `<div style="display:flex;align-items:center;gap:12px;font-size:20px;margin:4px 0"><span style="width:28px;height:0;border-top:3px dashed #e9f2f9;flex:none"></span><span>F<sub>d</sub> 1.0: M<sub>c</sub> ${Mc.toFixed(1)} MNm · T<sub>c</sub> ${Tc.toFixed(0)} MN</span></div>`,
    { x: x + w - 400, y: y + 14, w: 390, cls: 'glass', style: 'padding:14px 18px' });
    leg.in(t + 0.6, 0.5);
    out.leg = leg;
  }
  out.point = (M, Tw, { tt, color = '#ffffff', label = '', dx = 16, dy = -24 }) => {
    chart.dot(M, Tw, { color, r: 11, t: tt });
    if (label) { const a = S.div(label, { x: chart.X(M) + dx, y: chart.Y(Tw) + dy, cls: 'label', anchor: 'lm' }); a.in(tt + 0.2, 0.5, 'left'); return a; }
    return null;
  };
  return out;
}
