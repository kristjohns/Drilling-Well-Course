// Fatigue math in JS (mirrors model/fatigue_model.py) for plotting.
export function snN(ds, sn) {
  if (ds <= 0) return Infinity;
  const l1 = sn.loga1 - sn.m1 * Math.log10(ds);
  if (!sn.m2 || l1 <= Math.log10(sn.Nknee)) return Math.pow(10, l1);
  return Math.pow(10, sn.loga2 - sn.m2 * Math.log10(ds));
}
export function snS(N, sn) {           // stress range at N cycles
  const lg = Math.log10(N);
  if (sn.m2 && N > sn.Nknee) return Math.pow(10, (sn.loga2 - lg) / sn.m2);
  return Math.pow(10, (sn.loga1 - lg) / sn.m1);
}
export function snCurve(sn, N0 = 1e4, N1 = 1e9, n = 60) {
  const pts = [];
  for (let i = 0; i <= n; i++) { const N = N0 * Math.pow(N1 / N0, i / n); pts.push([N, snS(N, sn)]); }
  if (sn.m2) { pts.push([sn.Nknee, snS(sn.Nknee, sn)]); pts.sort((a, b) => a[0] - b[0]); }
  return pts;
}
export function mnN(dM, c) {
  if (dM <= 0) return Infinity;
  if (!c.loga2 || Math.log10(dM) >= Math.log10(c.dM12)) return Math.pow(10, c.loga1 - c.m1 * Math.log10(dM));
  return Math.pow(10, c.loga2 - c.m2 * Math.log10(dM));
}
export function mnM(N, c) {
  const lg = Math.log10(N);
  if (c.loga2) {
    const Nk = Math.pow(10, c.loga1 - c.m1 * Math.log10(c.dM12));
    if (N > Nk) return Math.pow(10, (c.loga2 - lg) / c.m2);
  }
  return Math.pow(10, (c.loga1 - lg) / c.m1);
}
export function mnCurve(c, N0 = 1e4, N1 = 1e9, n = 60) {
  const pts = [];
  for (let i = 0; i <= n; i++) { const N = N0 * Math.pow(N1 / N0, i / n); pts.push([N, mnM(N, c)]); }
  if (c.loga2) { const Nk = Math.pow(10, c.loga1 - c.m1 * Math.log10(c.dM12)); if (Nk > N0 && Nk < N1) pts.push([Nk, c.dM12]); pts.sort((a, b) => a[0] - b[0]); }
  return pts;
}
// deterministic pseudo-random + normal
export function prng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
export function gauss(r) { const u = Math.max(r(), 1e-9), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
export const logTicks = (a, b) => { const out = []; for (let e = Math.ceil(Math.log10(a)); e <= Math.floor(Math.log10(b)); e++) out.push(Math.pow(10, e)); return out; };
export const pow10 = (v) => { const e = Math.round(Math.log10(v)); return e === 0 ? '1' : e === 1 ? '10' : `10${sup(e)}`; };
const SUP = { '-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' };
export const sup = (n) => String(n).split('').map((c) => SUP[c]).join('');
