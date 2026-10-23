// Helpers for the slot-ring shots: legends, field access, points on the (deformed) ring.
import { E, COL, clamp, fmt } from '../engine/core.js';
import { RING_D, RINGU, ringFieldAt, ringSetField, ringDeform } from '../three/models.js';

export const RING_Y = RING_D.y1;                     // top face of the ring

// a world point on the ring at angle thDeg (degrees, from +x towards +z), radius r, height y, with the displacement
// field f applied at the exaggeration s (the field arrays are per degree)
export function ringPoint(thDeg, r, y = RING_Y, f = null, s = 0) {
  const th = thDeg * Math.PI / 180;
  let dr = 0, dt = 0;
  if (f && s) { const i = Math.round(((thDeg % 360) + 360) % 360) % 360; dr = s * f[2][i]; dt = s * f[3][i]; }
  return [(r + dr) * Math.cos(th) - dt * Math.sin(th), y, (r + dr) * Math.sin(th) + dt * Math.cos(th)];
}

// put the field of load multiplier alpha on the ring: 'el' = elastic solution scaled, 'c' = non-linear model (c)
export function ringState(D, mode, alpha, defScale) {
  let f;
  if (mode === 'el') f = D.elastic.field.map((arr) => arr.map((v) => v * alpha));
  else f = ringFieldAt(D.fields, alpha);
  ringSetField(f);
  ringDeform(E.world.models.feRing, f, defScale, D.inputs.load_deg);
  return f;
}

// banded stress legend (MPa) with fy/gamma_M0 and fy marked
export function stressLegend(S, { x = 1620, y = 230, vmax = 450, bands = 9, fyd = 300, fy = 345, t0, t1 } = {}) {
  const h = 46 * bands;
  const jet = (u) => {
    const c = (v) => Math.round(255 * clamp(v));
    return `rgb(${c(1.5 - Math.abs(4 * u - 3))},${c(1.5 - Math.abs(4 * u - 2))},${c(1.5 - Math.abs(4 * u - 1))})`;
  };
  let sw = '';
  for (let k = bands - 1; k >= 0; k--) sw += `<div style="height:46px;background:${jet((k + 0.5) / bands)}"></div>`;
  let lab = '';
  for (let k = 0; k <= bands; k++) lab += `<div style="position:absolute;left:58px;top:${h - k * 46 - 13}px" class="num">${fmt(vmax * k / bands)}</div>`;
  for (const [v, txt, col] of [[fyd, `f<sub>y</sub>/γ<sub>M0</sub> ${fyd}`, '#ffffff'], [fy, `f<sub>y</sub> ${fy}`, '#9fb2c2']]) {
    const ys = h - v / vmax * h;
    lab += `<div style="position:absolute;left:-14px;top:${ys - 1.5}px;width:58px;height:3px;background:${col}"></div>`;
    lab += `<div style="position:absolute;left:-170px;top:${ys - 15}px;font-weight:700;font-size:20px;color:${col};white-space:nowrap;width:150px;text-align:right">${txt}</div>`;
  }
  const c = S.card(`<div class="tiny" style="margin-bottom:14px;letter-spacing:0.12em;text-transform:uppercase">von Mises stress · MPa</div>
    <div style="position:relative;width:150px;height:${h}px"><div style="width:44px;border-radius:6px;overflow:hidden;border:1px solid rgba(255,255,255,0.25)">${sw}</div>${lab}</div>`,
  { x, y, cls: 'glass', style: 'padding:22px 26px 26px 26px;width:230px' });
  if (t0 !== undefined) c.in(t0, 0.6, 'left');
  if (t1 !== undefined) c.out(t1, 0.5);
  return c;
}

// legend of the strain contour (largest principal membrane strain magnitude)
export function strainLegend(S, { x = 1560, y = 250, t0, t1 } = {}) {
  const row = (col, txt) => `<div style="display:flex;align-items:center;gap:14px;margin:6px 0"><div style="width:44px;height:28px;border-radius:5px;background:${col}"></div><div class="small" style="font-size:21px">${txt}</div></div>`;
  const c = S.card(`<div class="tiny" style="margin-bottom:12px;letter-spacing:0.12em;text-transform:uppercase">Strain · membrane</div>
    ${row('rgb(200,8,8)', '≥ 5 %')}
    <div style="display:flex;align-items:center;gap:14px;margin:2px 0 6px 0"><div style="width:44px;height:4px;border-radius:2px;background:#fff"></div><div class="small" style="font-size:21px;color:#fff;font-weight:700">5 % line</div></div>
    ${row('rgb(217,87,0)', '2 – 5 %')}${row('rgb(200,170,4)', '1 – 2 %')}${row('rgb(22,156,43)', '0.2 % plastic – 1 %')}
    ${row('rgb(0,143,178)', 'yielded, &lt; 0.2 % plastic')}${row('linear-gradient(90deg,#08146b,#0f42a6)', 'elastic')}`, { x, y, cls: 'glass', style: 'padding:20px 24px' });
  if (t0 !== undefined) c.in(t0, 0.6, 'left');
  if (t1 !== undefined) c.out(t1, 0.5);
  return c;
}

export { RINGU };
