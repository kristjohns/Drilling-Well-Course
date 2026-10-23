"""Numbers for the template-interface tutorial: the lower slot ring of the template (contact D of NORSOK U-001
Figure J.1) loaded by the conductor, checked the Eurocode way (NORSOK N-001 -> N-004 -> EN 1993).

Teaching inputs, not project data:
  ring cut from 40 mm S355 plate, inner radius 0.459 m (36 in conductor + clearance), radial width 0.200 m,
  pinned at four struts (0, 90, 180, 270 deg), contact pressure from the conductor over +-20 deg centred at 45 deg
  (between two struts), ULS design contact force 1.6 MN (load factor 1.3 included, from a load-share analysis).

Checks:
  1. elastic: von Mises at the critical point <= fy / gamma_M0          (EN 1993-1-1 6.2.1(5))
  2. non-linear FE (EN 1993-1-5 Annex C): material models of C.6 (a) no hardening, (c) linear hardening;
     load multiplier alpha on the design load (C.7); limit states of C.8: maximum load (buckling) or 5 % principal
     membrane strain (tension); C.9: alpha_u >= alpha_1 * alpha_2.
  3. what a 2 % strain limit would change, and how the strain at a point depends on the mesh.
Writes src/data/model.json.
"""
import json, math, os, time
import numpy as np
from ring_fe import Ring, GP

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'src', 'data', 'model.json')

E = 210000.0                 # MPa, EN 1993-1-1 3.2.6
FY = 345.0                   # MPa, S355 with 16 < t <= 40 mm (EN 10025-2)
FU = 470.0                   # MPa, S355 minimum tensile strength (EN 10025-2)
GM0 = 1.15                   # material factor, NORSOK N-004 (ULS)
A2_HI = 1.30                 # upper value used for alpha_1 * alpha_2 in the example (alpha_1 = 1.0, alpha_2 <= 1.3)
RI, WR, TR = 0.459, 0.200, 0.040
R = RI + WR / 2
LOAD_DEG, SPREAD = 45.0, 20.0
PD = 1.6                     # MN, ULS design contact force
N_FINE = 288
N_VIEW = 360                 # samples around the ring for the 3D contour (1 degree)
EPS_Y = FY / E

MODELS = {'a': E / 10000, 'c': E / 100}       # (a) "no hardening" with a nominal slope for the solver, (c) E/100


def steps(dmax):
    return np.r_[np.linspace(0, 0.002, 41)[1:], np.geomspace(0.002, dmax, 150)[1:]]


def run(n, Et, eps_stop=0.12, dmax=0.05, keep_fields=False):
    r = Ring(R, WR, TR, n, E, FY, Et, load_deg=LOAD_DEG, spread_deg=SPREAD)
    rows, fields = [], []
    prev = 0.0
    for tgt in steps(dmax):
        _, eps = r.step(tgt - prev); prev = tgt
        rows.append([tgt * 1000, r.lam / PD, eps.max() * 100, -eps.min() * 100])
        if keep_fields:
            fields.append(view_fields(r))
        if eps.max() > eps_stop: break
    return np.array(rows), fields, r


def view_fields(r):
    """membrane strain a, curvature b, radial / tangential displacement at N_VIEW angles (a and b interpolated
    from the Gauss points, so the peaks of the contour match the strains in the curves)"""
    e0, kap = r.section_strains(r.u)
    dth = 2 * math.pi / r.n
    th_g = (r.th[:, None] + GP[None, :] * dth).ravel()   # Gauss point angles (chord parameter ~ angle)
    tv = 2 * math.pi * np.arange(N_VIEW) / N_VIEW
    per = lambda x, y: np.interp(tv, np.r_[x - 2 * math.pi, x, x + 2 * math.pi], np.r_[y, y, y])
    a = per(th_g, np.repeat(e0, 3)); b = per(th_g, kap.ravel())
    ux, uy = r.u[0::3], r.u[1::3]
    ur = ux * np.cos(r.th) + uy * np.sin(r.th); ut = -ux * np.sin(r.th) + uy * np.cos(r.th)
    return [np.round(a, 7).tolist(), np.round(b, 6).tolist(), np.round(per(r.th, ur), 7).tolist(), np.round(per(r.th, ut), 7).tolist()]


def at(rows, col, val):
    """alpha (and delta) where column col first reaches val, by linear interpolation"""
    x = rows[:, col]
    j = int(np.argmax(x >= val))
    if x[j] < val: return None
    if j == 0: return {'alpha': float(rows[0, 1]), 'delta': float(rows[0, 0])}
    f = (val - x[j - 1]) / (x[j] - x[j - 1])
    return {'alpha': float(rows[j - 1, 1] + f * (rows[j, 1] - rows[j - 1, 1])), 'delta': float(rows[j - 1, 0] + f * (rows[j, 0] - rows[j - 1, 0]))}


def main():
    t0 = time.time()
    # ------------------------------------------------------------------ elastic
    r = Ring(R, WR, TR, N_FINE, E, FY, MODELS['c'], load_deg=LOAD_DEG, spread_deg=SPREAD)
    u, eps = r.linear()
    sig_unit = float(np.abs(E * eps).max())               # MPa per MN
    i, g, k = np.unravel_index(np.argmax(np.abs(eps)), eps.shape)
    crit = {'theta_deg': float(math.degrees(r.th[i] + math.pi / r.n)), 'edge': 'outer' if r.y[k] < 0 else 'inner'}
    sig_d = sig_unit * PD
    P_y = FY / sig_unit
    r.u = u * PD
    elastic_field = view_fields(r)
    ur_load = float((u[3 * r.load_node] * math.cos(r.th[r.load_node]) + u[3 * r.load_node + 1] * math.sin(r.th[r.load_node])) * 1000)
    # reactions at the struts for the design load (radial, tangential), MN
    F, _, _ = r.assemble(u * PD)
    reac = []
    for nd in r.sup_nodes:
        fx, fy_ = F[3 * nd], F[3 * nd + 1]; th = r.th[nd]
        reac.append({'deg': round(math.degrees(th)), 'radial': float(fx * math.cos(th) + fy_ * math.sin(th)), 'tang': float(-fx * math.sin(th) + fy_ * math.cos(th))})
    elastic = {
        'sigma_per_MN': sig_unit, 'sigma_d': sig_d, 'f_yd': FY / GM0, 'util': sig_d / (FY / GM0),
        'P_y': P_y, 'alpha_y': P_y / PD, 'alpha_yd': P_y / GM0 / PD, 'crit': crit, 'ur_per_MN_mm': ur_load,
        'field': elastic_field, 'reactions': reac,
    }
    # ------------------------------------------------------------------ non-linear, fine mesh
    curves, marks = {}, {}
    fields = None
    for m, Et in MODELS.items():
        rows, flds, rr = run(N_FINE, Et, keep_fields=(m == 'c'))
        if m == 'c':
            # keep the contour fields up to a bit beyond 5 %
            keep = [j for j in range(len(rows)) if rows[j, 2] <= 6.5]
            fields = {'alpha': [float(rows[j, 1]) for j in keep], 'delta': [float(rows[j, 0]) for j in keep],
                      'eps': [float(rows[j, 2]) for j in keep], 'f': [flds[j] for j in keep]}
        curves[m] = np.round(rows, 5).tolist()
        marks[m] = {
            'first_yield': at(rows, 2, EPS_Y * 100 * 1.0000001),
            'p02': at(rows, 2, (EPS_Y + 0.002) * 100),
            'e2': at(rows, 2, 2.0), 'e5': at(rows, 2, 5.0), 'e10': at(rows, 2, 10.0),
            'last': {'alpha': float(rows[-1, 1]), 'delta': float(rows[-1, 0]), 'eps': float(rows[-1, 2])},
        }
        print(f'model {m}: ' + ', '.join(f'{k} {v["alpha"]:.3f}' for k, v in marks[m].items() if v))
    marks['a']['plateau'] = marks['a']['last']['alpha']
    # ------------------------------------------------------------------ mesh study
    mesh = {}
    for m, Et in MODELS.items():
        mesh[m] = []
        for n in (72, 144, 288, 576):
            rows, _, _ = run(n, Et, eps_stop=0.105)
            ent = {'n': n, 'deg': 360 / n, 'L_mm': 2 * R * math.sin(math.pi / n) * 1000,
                   'e2': at(rows, 2, 2.0), 'e5': at(rows, 2, 5.0), 'curve': np.round(rows[:, [1, 2]], 5).tolist()}
            # strain at a fixed load level (alpha 1.50) to show the mesh dependence of a point strain
            j = int(np.argmax(rows[:, 1] >= 1.50))
            ent['eps_at_150'] = float(rows[j, 2]) if rows[j, 1] >= 1.50 else None
            mesh[m].append(ent)
            print(f'mesh {m} n={n}: alpha(2%) {ent["e2"]["alpha"]:.3f} alpha(5%) {ent["e5"]["alpha"]:.3f} eps@1.50 {ent["eps_at_150"]}')
    # ------------------------------------------------------------------ the checks
    a_u = marks['c']['e5']['alpha']
    D = {
        'inputs': {'E': E, 'fy': FY, 'fu': FU, 'gM0': GM0, 'a12_hi': A2_HI, 'ri': RI, 'w': WR, 't': TR, 'R': R, 'ro': RI + WR,
                   'load_deg': LOAD_DEG, 'spread_deg': SPREAD, 'PD': PD, 'struts_deg': [0, 90, 180, 270], 'n_fine': N_FINE,
                   'n_view': N_VIEW, 'eps_y': EPS_Y, 'models': {'a': 'E/10000', 'c': 'E/100'}},
        'elastic': elastic, 'curves': curves, 'marks': marks, 'mesh': mesh, 'fields': fields,
        'check': {'alpha_u': a_u, 'alpha_1': 1.0, 'alpha_2_hi': A2_HI, 'ok': a_u >= A2_HI,
                  'e2_vs_e5_c': marks['c']['e2']['alpha'] / a_u - 1, 'e2_vs_e5_a': marks['a']['e2']['alpha'] / marks['a']['e5']['alpha'] - 1,
                  'pl_over_y': marks['a']['plateau'] / elastic['alpha_y']},
    }
    with open(OUT, 'w') as f:
        json.dump(D, f, separators=(',', ':'))
    print(f'elastic: sigma {sig_unit:.1f} MPa/MN, sigma_d {sig_d:.0f} MPa vs fyd {FY / GM0:.0f} -> util {sig_d / (FY / GM0):.2f}; '
          f'P_y {P_y:.3f} MN (alpha {P_y / PD:.3f}); crit {crit}')
    print(f'alpha_u (c, 5 %) {a_u:.3f} vs alpha1*alpha2 <= {A2_HI}; plateau (a) {marks["a"]["plateau"]:.3f}')
    print(f'wrote {OUT} ({os.path.getsize(OUT) / 1024:.0f} kB) in {time.time() - t0:.0f} s')


if __name__ == '__main__':
    main()
