#!/usr/bin/env python3
"""Engineering model behind the acceptance-criteria video -> src/data/model.json

Every number shown on screen or spoken in the narration comes from this file.

    python3 model/acceptance_model.py

Contents
  1. Design strength (NORSOK U-001:2026 B.2.7.4, formulas B.5 / B.6) for an API 75K forging.
  2. True stress-strain curve after the ASME BPVC VIII model (VIII-2 Annex 3-D, VIII-3 KM-620) that B.3.6.2 asks for,
     the curve cut off at yield (limit load method) and at true ultimate (plastic collapse method), the engineering
     curve of the tensile test and the 0.2 % offset construction.
  3. The worked example: HP wellhead housing neck just below the connector hub (all wellhead datum load passes
     through it), Table A.4 loads (250-500 m, BOP on WH) moved 0.6 m down with the shear force (A.3.3), rated
     working pressure end load on the gasket sealing diameter (B.7).
  4. Elastic route (B.3.5): an ILLUSTRATIVE stress field along a stress classification line (SCL) at the neck fillet
     (beam stresses + Lame pressure stresses + a fillet peak), linearised per ASME VIII-2 Annex 5-A, checked against
     Table B.7 with the design factor.
  5. Elastic-plastic route (B.3.6): a section (fibre) model of the neck as a teaching stand-in for the 3D FE model:
     limit load (curve cut off at yield) and plastic collapse (curve cut off at true ultimate, geometric softening
     represented by the engineering stress), factored by MAX[1.2; su/sy]; combined tension-bending interaction.
  6. Capacity check with formula (B.7) and the Table B.3 design factors.
  7. Local failure: the triaxiality-dependent strain limit of ASME VIII-3 KD-232 (shape of the curve only).
"""
import json
import math
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'src', 'data', 'model.json')


def r(x, d=4):
    return float(round(float(x), d))


# --------------------------------------------------------------------------------------------- 1. design strength
E_MOD = 207000.0          # MPa
NU = 0.3
SMYS, SMTS = 517.0, 655.0  # API 75K: 75 ksi / 95 ksi
ELONG_MIN, RA_MIN = 17.0, 35.0
Yy, Yu = 1.0, 1.0          # metal temperature below 40 degC: no de-rating (B.2.7.4)
SY = min(Yy * SMYS, 0.90 * Yu * SMTS)        # (B.5)
SU = Yu * SMTS                                # (B.6)
RATIO = SU / SY
FACTOR = max(1.2, RATIO)                      # B.3.6.3.2.3
EPS_Y = SY / E_MOD


# --------------------------------------------------------------------------------------------- 2. stress-strain
def km620_strain(st, sys_=SY, suts=SU, E=E_MOD, eps_p=2.0e-5, m2=None):
    """total true strain for a true stress st (MPa); ASME VIII-2 3-D.3 / VIII-3 KM-620, ferritic steel"""
    R = sys_ / suts
    if m2 is None:
        m2 = 0.60 * (1.00 - R)
    eys = 0.002
    K = 1.5 * R ** 1.5 - 0.5 * R ** 2.5 - R ** 3.5
    m1 = (math.log(R) + (eps_p - eys)) / math.log(math.log(1 + eps_p) / math.log(1 + eys))
    A1 = sys_ * (1 + eys) / (math.log(1 + eys)) ** m1
    A2 = suts * math.exp(m2) / m2 ** m2
    H = 2 * (st - (sys_ + K * (suts - sys_))) / (K * (suts - sys_))
    e1 = (st / A1) ** (1 / m1)
    e2 = (st / A2) ** (1 / m2)
    g1 = e1 / 2 * (1 - math.tanh(H))
    g2 = e2 / 2 * (1 + math.tanh(H))
    return st / E + g1 + g2


R_YT = SY / SU
M2 = 0.60 * (1.00 - R_YT)
ST_U = SU * math.exp(M2)                          # true ultimate (cut-off) stress
# tabulate the true curve on a stress grid, then invert for strain -> stress
_st = np.linspace(1.0, ST_U, 4000)
_et = np.array([km620_strain(s) for s in _st])
assert np.all(np.diff(_et) > 0)
EPS_TU = float(_et[-1])                           # true strain at the true ultimate stress
# strain at which the curve reaches the yield strength (cut-off point of the limit-load curve)
EPS_TY = float(np.interp(SY, _st, _et))


def sigma_true(eps, cut='u'):
    """true stress for a true strain (magnitude), cut-off at yield ('y') or true ultimate ('u')"""
    e = abs(eps)
    if cut == 'y':
        if e >= EPS_TY:
            return SY
        return float(np.interp(e, _et, _st))
    if e >= EPS_TU:
        return ST_U
    return float(np.interp(e, _et, _st))


def sigma_eng_of_true_strain(eps):
    """engineering stress for a true strain (force per original area, uniform deformation)"""
    return sigma_true(eps, 'u') * math.exp(-abs(eps))


# chart data (strain in %, stress in MPa)
curves = {}
grid = np.concatenate([np.linspace(0, 0.006, 61), np.linspace(0.006, 0.05, 89)[1:], np.linspace(0.05, 0.26, 85)[1:]])
curves['true_u'] = [[r(e * 100, 4), r(sigma_true(e, 'u'), 2)] for e in grid]
curves['true_y'] = [[r(e * 100, 4), r(sigma_true(e, 'y'), 2)] for e in grid]
curves['linear'] = [[0, 0], [r(700 / E_MOD * 100, 4), 700.0]]
# stabilising slope allowed with the cut-off at yield: at most +5 % at 20 % plastic strain (B.3.6.2)
curves['y_stab'] = [[r(EPS_TY * 100, 4), r(SY, 2)], [r((EPS_TY + 0.20) * 100, 4), r(SY * 1.05, 2)]]
# engineering curve of the tensile test: from the true curve up to the maximum (uniform elongation), then a
# schematic necking branch to fracture at 22 % elongation (above the 17 % minimum)
eng = []
for e in np.concatenate([np.linspace(0, 0.006, 61), np.linspace(0.006, EPS_TU, 120)[1:]]):
    ee = math.exp(e) - 1
    eng.append([ee, sigma_true(e, 'u') / (1 + ee)])
e_u = eng[-1][0]
s_u = eng[-1][1]
FRACT = 0.22
for k in range(1, 41):
    u = k / 40
    ee = e_u + (FRACT - e_u) * u
    eng.append([ee, s_u * (1 - 0.16 * u ** 2.2)])
curves['eng'] = [[r(a * 100, 4), r(b, 2)] for a, b in eng]
UNIFORM_ELONG = e_u
# 0.2 % offset construction: line through (0.2 %, 0) with slope E meets the engineering curve at the yield strength
off_x = 0.002 + SY / E_MOD
curves['offset'] = [[0.2, 0.0], [r(off_x * 100, 4), r(SY, 2)]]
curves['true_vs_eng'] = [[r(a * 100, 3), r(b, 2), r((math.log(1 + a)) * 100, 3), r(b * (1 + a), 2)] for a, b in eng if a <= e_u + 1e-9][::4]

# --------------------------------------------------------------------------------------------- 3. the worked example
D_O, D_I = 0.700, 0.476                 # neck outside / bore (18 3/4 in) diameter, m
R_O, R_I = D_O / 2, D_I / 2
T_W = R_O - R_I
A_SEC = math.pi / 4 * (D_O ** 2 - D_I ** 2)
I_SEC = math.pi / 64 * (D_O ** 4 - D_I ** 4)
Z_EL = I_SEC / R_O
Z_PL = (D_O ** 3 - D_I ** 3) / 6
M_Y = SY * Z_EL                         # first yield at the outside fibre, MNm (MPa x m3)
M_P = SY * Z_PL                         # fully plastic moment
T_C = SY * A_SEC                        # MN

TABLE_A4 = [
    {'range': '80–250', 'uls': [9289, 678, -1472], 'als': [13382, 977, 3424]},
    {'range': '250–500', 'uls': [7354, 537, -1472], 'als': [12217, 892, 3424]},
    {'range': '500 and deeper', 'uls': [6862, 501, -1472], 'als': [11467, 837, 3424]},
]
CASE = TABLE_A4[1]
Z_SEC = 0.60                            # section (fillet root) below the wellhead datum, m
P_I = 69.0                              # rated working pressure, MPa (690 bar)
P_E = 0.0                               # external pressure ignored (conservative for the end load)
D_S = 0.50                              # gasket sealing diameter (illustrative), m
END_LOAD = math.pi / 4 * D_S ** 2 * (P_I - P_E)     # MN
FD = {'single_internal': 0.60, 'single_external': 0.60, 'fat': 0.90, 'make_break': 0.90,
      'normal': 0.67, 'extreme': 0.80, 'accidental_above': 1.00, 'accidental_below': 0.90}

loads = {}
for key, fd in (('uls', FD['extreme']), ('als', FD['accidental_below'])):
    Mw, Qw, Te = CASE[key]
    M = (Mw + Qw * Z_SEC) / 1000.0      # MNm
    Tw = Te / 1000.0 + END_LOAD         # MN
    loads[key] = {'Mw_kNm': Mw, 'Qw_kN': Qw, 'Te_kN': Te, 'M_MNm': r(M, 4), 'Tw_MN': r(Tw, 4), 'Fd': fd}


# --------------------------------------------------------------------------------------------- 4. elastic route (SCL)
KT, DELTA = 1.50, 0.012                 # fillet stress concentration and its decay depth (illustrative)


def lame(rr, p=P_I, ri=R_I, ro=R_O):
    a = p * ri ** 2 / (ro ** 2 - ri ** 2)
    return a * (1 + ro ** 2 / rr ** 2), a * (1 - ro ** 2 / rr ** 2)     # hoop, radial


def scl_profile(M, Tw, n=81, peak=True):
    xs = np.linspace(0.0, T_W, n)        # 0 = bore, t = outside surface
    rr = R_I + xs
    sa_nom = Tw / A_SEC + M * rr / I_SEC
    sa = sa_nom + ((KT - 1) * (Tw / A_SEC + M * R_O / I_SEC) * np.exp(-(R_O - rr) / DELTA) if peak else 0.0)
    sh, sr = lame(rr)
    return xs, sa, sh, sr


def linearise(xs, s):
    t = xs[-1] - xs[0]
    m = np.trapezoid(s, xs) / t
    b_in = 6 / t ** 2 * np.trapezoid(s * (t / 2 - (xs - xs[0])), xs)      # bending stress at the inside surface
    return m, b_in


def vm(a, h, rr, sh=0.0):
    return math.sqrt(0.5 * ((a - h) ** 2 + (h - rr) ** 2 + (rr - a) ** 2) + 3 * sh ** 2)


def elastic_check(key):
    L = loads[key]
    xs, sa, sh, sr = scl_profile(L['M_MNm'], L['Tw_MN'])
    comp = {}
    for name, s in (('a', sa), ('h', sh), ('r', sr)):
        m, b = linearise(xs, s)
        comp[name] = (m, b)
    mem = vm(comp['a'][0], comp['h'][0], comp['r'][0])
    mb_in = vm(*(comp[k][0] + comp[k][1] for k in 'ahr'))
    mb_out = vm(*(comp[k][0] - comp[k][1] for k in 'ahr'))
    tot_out = vm(sa[-1], sh[-1], sr[-1])
    tot_in = vm(sa[0], sh[0], sr[0])
    fd = L['Fd']
    out = {
        'x_mm': [r(x * 1000, 2) for x in xs],
        'sa': [r(v, 2) for v in sa], 'sh': [r(v, 2) for v in sh], 'sr': [r(v, 2) for v in sr],
        'sa_nom': [r(v, 2) for v in scl_profile(L['M_MNm'], L['Tw_MN'], peak=False)[1]],
        'vm_total': [r(vm(a, h, q), 2) for a, h, q in zip(sa, sh, sr)],
        'lin': {k: [r(comp[k][0], 2), r(comp[k][1], 2)] for k in comp},
        'mem_vm': r(mem, 2), 'mb_vm_in': r(mb_in, 2), 'mb_vm_out': r(mb_out, 2), 'mb_vm': r(max(mb_in, mb_out), 2),
        'total_vm_out': r(tot_out, 2), 'total_vm_in': r(tot_in, 2),
        'peak_vm_out': r(tot_out - mb_out, 2),
        'allow_PL': r(fd * SY, 2), 'allow_PLPb': r(1.5 * fd * SY, 2),
        'uf_PL': r(mem / (fd * SY), 4), 'uf_PLPb': r(max(mb_in, mb_out) / (1.5 * fd * SY), 4),
        'tri_sum_out': r(sa[-1] + sh[-1] + sr[-1], 2), 'tri_limit': r(2.5 * SMYS, 1),
    }
    return out


elastic = {k: elastic_check(k) for k in loads}


# --------------------------------------------------------------------------------------------- 5. elastic-plastic route
NR, NTH = 28, 240
_rc = R_I + (np.arange(NR) + 0.5) * T_W / NR
_th = (np.arange(NTH) + 0.5) * 2 * math.pi / NTH
RR, TH = np.meshgrid(_rc, _th)
XX = (RR * np.cos(TH)).ravel()
DA = (RR * (T_W / NR) * (2 * math.pi / NTH)).ravel()
assert abs(DA.sum() - A_SEC) / A_SEC < 1e-3

# vectorised material laws on a strain grid (true strain magnitude -> stress)
_eg = np.concatenate([np.linspace(0, 0.01, 400), np.linspace(0.01, 0.6, 1200)[1:]])
LAW = {
    'y': np.array([sigma_true(e, 'y') for e in _eg]),                       # limit load: cut-off at yield
    'u_eng': np.array([sigma_eng_of_true_strain(e) for e in _eg]),          # collapse: true curve + area change
}


def stress_of(eps, law):
    return np.sign(eps) * np.interp(np.abs(eps), _eg, LAW[law])


def section(kappa, N, law):
    """moment (MNm) at curvature kappa (1/m) with axial force N (MN) held, solving for the axial strain"""
    lo, hi = -0.2, 0.2
    for _ in range(80):
        e0 = 0.5 * (lo + hi)
        f = float(np.dot(stress_of(e0 + kappa * XX, law), DA)) - N
        if f > 0:
            hi = e0
        else:
            lo = e0
    e0 = 0.5 * (lo + hi)
    s = stress_of(e0 + kappa * XX, law)
    return float(np.dot(s * XX, DA)), e0


L_ROT = 1.0                               # end rotation of a 1 m neck segment = curvature x 1 m
kap = np.concatenate([np.linspace(0, 0.02, 41), np.linspace(0.02, 0.2, 61)[1:], np.linspace(0.2, 1.4, 61)[1:]])
mk_y = [section(k, 0.0, 'y')[0] for k in kap]
mk_u = [section(k, 0.0, 'u_eng')[0] for k in kap]
i_max = int(np.argmax(mk_u))
M_COLLAPSE = mk_u[i_max]
KAPPA_COLLAPSE = float(kap[i_max])
M_LIMIT = M_P                             # the cut-off-at-yield curve approaches M_P; non-convergence there
M_FACT = M_COLLAPSE / FACTOR

# load-controlled increments of the limit-load analysis: the step to M_P never converges
inc = []
for frac in (0.2, 0.4, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99, 0.995):
    target = frac * M_P
    lo, hi = 0.0, 5.0
    for _ in range(70):
        mid = 0.5 * (lo + hi)
        if section(mid, 0.0, 'y')[0] < target:
            lo = mid
        else:
            hi = mid
    inc.append([r(frac, 4), r(target, 4), r(0.5 * (lo + hi) * L_ROT * 1000, 3)])

# the outside surface reaches 0.2 % plastic strain (yielding, definition 3.1.22) at this moment
KAPPA_SURF = EPS_TY / R_O
M_SURF = section(KAPPA_SURF, 0.0, 'y')[0]

# elastic core of the neck under pure bending (cut-off-at-yield law): fibres with |kappa x| < eps_y stay elastic
core = []
for row in inc:
    k = row[2] / 1000 / L_ROT
    core.append([row[0], r(min(1.0, EPS_TY / max(k * R_O, 1e-12)), 4)])

# tension capacity: limit load and factored plastic collapse (uniform strain, engineering stress maximum)
T_COLLAPSE = SU * A_SEC
T_FACT = T_COLLAPSE / FACTOR

# exact plastic interaction (axial force held, bending to the maximum) for the capacity chart
inter = []
for nf in np.linspace(0, 0.96, 13):
    N = nf * T_C
    best = 0.0
    for k in (0.05, 0.1, 0.2, 0.4, 0.8, 1.6):
        best = max(best, section(k, N, 'y')[0])
    inter.append([r(best, 4), r(N, 4)])
inter.append([0.0, r(T_C, 4)])


def b7(key, Tc, Mc):
    L = loads[key]
    s = L['Tw_MN'] / Tc + abs(L['M_MNm']) / Mc
    return {'sum': r(s, 4), 'uf': r(s / L['Fd'], 4), 'tw_term': r(L['Tw_MN'] / Tc, 4), 'm_term': r(L['M_MNm'] / Mc, 4)}


check = {
    'limit': {k: b7(k, T_C, M_LIMIT) for k in loads},
    'factored': {k: b7(k, T_FACT, M_FACT) for k in loads},
}

# --------------------------------------------------------------------------------------------- 7. local failure
ALPHA_SL = 2.2
coef = ALPHA_SL / (1 + M2)
tri = [[r(T, 3), r(math.exp(-coef * (T - 1 / 3)), 4)] for T in np.linspace(0, 2.0, 81)]

# --------------------------------------------------------------------------------------------- output
model = {
    'material': {
        'name': 'API 75K forging (wellhead housing)', 'E': E_MOD, 'nu': NU, 'SMYS': SMYS, 'SMTS': SMTS, 'Yy': Yy, 'Yu': Yu,
        'sy': r(SY, 2), 'su': r(SU, 2), 'cap_09smts': r(0.9 * Yu * SMTS, 2), 'ratio': r(RATIO, 4), 'factor': r(FACTOR, 4),
        'eps_y': r(EPS_Y, 6), 'R': r(R_YT, 4), 'm2': r(M2, 4), 'st_u': r(ST_U, 2), 'eps_tu': r(EPS_TU, 5), 'eps_ty': r(EPS_TY, 6),
        'uniform_elong': r(UNIFORM_ELONG, 5), 'fracture_elong': FRACT, 'elong_min': ELONG_MIN, 'ra_min': RA_MIN,
    },
    'curves': curves,
    'section': {
        'D': D_O, 'd': D_I, 't': r(T_W, 4), 'Dt': r(D_O / T_W, 3), 'A': r(A_SEC, 6), 'I': r(I_SEC, 7), 'Z': r(Z_EL, 6), 'Zp': r(Z_PL, 6),
        'My': r(M_Y, 4), 'Mp': r(M_P, 4), 'shape': r(Z_PL / Z_EL, 4), 'Tc': r(T_C, 4), 'z_below_datum': Z_SEC,
        'y_world': 4.0 - Z_SEC, 'ro': R_O, 'ri': R_I,
    },
    'loads': {'table_a4': TABLE_A4, 'case': '250–500', 'p_i': P_I, 'p_e': P_E, 'D_s': D_S, 'end_load': r(END_LOAD, 4), **loads},
    'Fd': FD,
    'elastic': elastic, 'kt': KT, 'delta_mm': DELTA * 1000,
    'ep': {
        'L_rot': L_ROT, 'rot_mrad': [r(k * L_ROT * 1000, 3) for k in kap],
        'M_y': [r(v, 4) for v in mk_y], 'M_u': [r(v, 4) for v in mk_u],
        'M_limit': r(M_LIMIT, 4), 'M_collapse': r(M_COLLAPSE, 4), 'rot_collapse': r(KAPPA_COLLAPSE * L_ROT * 1000, 3),
        'M_fact': r(M_FACT, 4), 'collapse_over_limit': r(M_COLLAPSE / M_LIMIT, 4),
        'T_collapse': r(T_COLLAPSE, 4), 'T_fact': r(T_FACT, 4),
        'increments': inc, 'core': core, 'interaction': inter,
        'M_surf_yield': r(M_SURF, 4), 'surf_yield_frac': r(M_SURF / M_P, 4), 'rot_surf_yield': r(KAPPA_SURF * L_ROT * 1000, 3),
    },
    'check': check,
    'local': {'alpha_sl': ALPHA_SL, 'm2': r(M2, 4), 'coef': r(coef, 4), 'curve': tri,
              'notch_T': 1.2, 'notch_ratio': r(math.exp(-coef * (1.2 - 1 / 3)), 4)},
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w') as f:
    json.dump(model, f, indent=1, ensure_ascii=False)

# ------------------------------------------------------------------------------------------- report
print(f"design strength: sy = min({Yy}x{SMYS}; 0.9x{Yu}x{SMTS} = {0.9 * Yu * SMTS:.1f}) = {SY:.1f} MPa, su = {SU:.1f} MPa, "
      f"su/sy = {RATIO:.3f}, factor = {FACTOR:.3f}")
print(f"true curve: R = {R_YT:.3f}, m2 = {M2:.4f}, true ultimate {ST_U:.1f} MPa at true strain {EPS_TU * 100:.2f} %, "
      f"sy reached at {EPS_TY * 100:.3f} %, uniform elongation {UNIFORM_ELONG * 100:.2f} %")
print(f"neck: D {D_O} d {D_I} t {T_W * 1000:.0f} mm D/t {D_O / T_W:.2f}, A {A_SEC:.5f} m2, I {I_SEC:.6f} m4, Z {Z_EL:.5f}, "
      f"Zp {Z_PL:.5f} m3, shape {Z_PL / Z_EL:.3f}")
print(f"  My {M_Y:.2f} MNm, Mp {M_P:.2f} MNm, Tc {T_C:.2f} MN")
print(f"end load {END_LOAD:.3f} MN (Ds {D_S} m, p {P_I} MPa)")
for k, L in loads.items():
    print(f"  {k}: M {L['M_MNm']:.3f} MNm, Tw {L['Tw_MN']:.3f} MN, Fd {L['Fd']}")
for k, e in elastic.items():
    print(f"elastic {k}: PL {e['mem_vm']:.1f} vs {e['allow_PL']:.1f} (uf {e['uf_PL']:.3f}); PL+Pb {e['mb_vm']:.1f} vs "
          f"{e['allow_PLPb']:.1f} (uf {e['uf_PLPb']:.3f}); total out {e['total_vm_out']:.1f}, peak {e['peak_vm_out']:.1f}; "
          f"lin a {e['lin']['a']} h {e['lin']['h']} r {e['lin']['r']}")
print(f"EP: limit {M_LIMIT:.3f} MNm (fibre model at kappa 1.4: {mk_y[-1]:.3f}), collapse {M_COLLAPSE:.3f} at {KAPPA_COLLAPSE * 1000:.0f} mrad "
      f"(x{M_COLLAPSE / M_LIMIT:.3f}), factored {M_FACT:.3f} MNm; T collapse {T_COLLAPSE:.2f} factored {T_FACT:.2f}")
print('increments', inc)
print('core', core)
for k in loads:
    print(f"B.7 {k}: limit {check['limit'][k]}  factored {check['factored'][k]}")
print('interaction', inter[:4], '...')
print(f"local: coef {coef:.3f}; eps_L/eps_Lu at T=1.2: {math.exp(-coef * (1.2 - 1 / 3)):.3f}")
