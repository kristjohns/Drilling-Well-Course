#!/usr/bin/env python3
"""Engineering model behind every number in the video.

It implements the NORSOK U-001:2026 fatigue method for the conductor and the conductor/template interface
(Annex A.3.5 loads, Annex B.2.6 design format, Annex B.4 M-N capacity, Miner damage) and a simplified local
response model of the well (two concentric beam strings, contact areas A-H of Figure J.1, cement, soil and
template springs) that stands in for the 3D finite element model B.4.2.4 asks for.

    python3 model/fatigue_model.py          -> src/data/model.json (+ a printed report)

Units inside: N, m, Pa. Reported: kNm, kN, MPa, mm.

Everything marked ILLUSTRATIVE is a teaching value, not project data. NORSOK values are quoted from
NORSOK U-001:2026 (tables A.3, A.7, A.8, B.4, Table 4). The S-N parameters are the DNV-RP-C203 (2016 edition)
C1 curve for seawater with cathodic protection; NORSOK U-001:2026 refers to DNV-RP-C203:2024, whose seawater
curves were revised, so take design values from that edition.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "src", "data", "model.json")

E_STEEL = 207e9          # Pa
INCH = 0.0254

# ------------------------------------------------------------------------------------------------ NORSOK data
# Table A.7  annual WH single-load bending moment range dMo [kNm] (DF = 1)
TABLE_A7 = {
    "BOP on WH": {"80-250": 2124, "250-500": 1436, "500-1500": 1194},
    "BOP on XT": {"80-250": 2466, "250-500": 1766, "500-1500": 1452},
}
# Table A.8  annual general bending moment fatigue histogram at WH datum (normalised ranges, cycles)
A8_R = [round(0.1 * i, 1) for i in range(1, 30)]
A8_N = [3948892, 826087, 698721, 550639, 416070, 309974, 223998, 166948, 111824, 78218, 52813, 34385, 21874,
        13388, 8007, 4921, 2673, 1574, 847, 471, 230, 110, 55, 27, 13, 7, 3, 1, 1]
# Table A.3 standard design case: wellhead datum to centre lower flex joint (max) and XT height (max)
H_LFJ = 13.7
H_XT = 2.5
# Table B.4 S-N fatigue design factors
TABLE_B4 = {"permanent": {"service life": 10}, "temporary": {"service life": 3, "inspection interval": 10}}
# Table 4 indicative vertical load share factors (share carried by the structure)
TABLE_4 = [("Single caisson 1-slot", "50 %"), ("Template 1-slot", "40 %"), ("Template 2-slot", "45 %"),
           ("Template 4-slot", "35 %"), ("Template 6-slot", "30 % / 20 %")]
# Table A.4 / A.5 ULS & ALS WH design loads (context only)
TABLE_A4 = [("80-250", 9289, 678, -1472, 13382, 977, 3424), ("250-500", 7354, 537, -1472, 12217, 892, 3424),
            ("500+", 6862, 501, -1472, 11467, 837, 3424)]

# NORSOK N-001 design fatigue factor matrix (for the template; check the edition in your design basis)
N001_DFF = {"columns": ["No access or in the splash zone", "Accessible, below splash zone",
                        "Above splash zone or internal"],
            "rows": {"Substantial consequences": [10, 3, 2], "Without substantial consequences": [3, 2, 1]}}

# S-N curve C1, seawater with cathodic protection (DNV-RP-C203 2016 values; ILLUSTRATIVE for this video)
SN_C1_CP = {"name": "C1, seawater + CP", "m1": 3.0, "loga1": 12.049, "m2": 5.0, "loga2": 16.081,
            "Nknee": 1e6, "t_ref": 25.0, "k": 0.15}
SN_C1_AIR = {"name": "C1, in air", "m1": 3.0, "loga1": 12.449, "m2": 5.0, "loga2": 16.081, "Nknee": 1e7}
SN_C1_FC = {"name": "C1, free corrosion", "m1": 3.0, "loga1": 11.972}
SN_D_CP = {"name": "D, seawater + CP", "m1": 3.0, "loga1": 11.764, "m2": 5.0, "loga2": 15.606, "Nknee": 1e6}


# ------------------------------------------------------------------------------------------------ basics
def tube(D: float, t: float) -> dict:
    """Section properties of a circular tube (outside diameter D, wall t), derived in chapter 6."""
    d = D - 2 * t
    A = math.pi / 4 * (D ** 2 - d ** 2)
    I = math.pi / 64 * (D ** 4 - d ** 4)
    return {"D": D, "t": t, "d": d, "A": A, "I": I, "W": I / (D / 2)}


def sn_N(ds_mpa: float, sn: dict, t_mm: float | None = None) -> float:
    """Cycles to failure from a (bi)linear S-N curve with optional thickness correction."""
    if ds_mpa <= 0:
        return math.inf
    s = ds_mpa
    if t_mm is not None and "k" in sn and t_mm > sn["t_ref"]:
        s = ds_mpa * (t_mm / sn["t_ref"]) ** sn["k"]
    logN1 = sn["loga1"] - sn["m1"] * math.log10(s)
    if "m2" not in sn or logN1 <= math.log10(sn["Nknee"]):
        return 10 ** logN1
    return 10 ** (sn["loga2"] - sn["m2"] * math.log10(s))


def sn_knee_stress(sn: dict) -> float:
    return 10 ** ((sn["loga1"] - math.log10(sn["Nknee"])) / sn["m1"])


def histogram(dMo_kNm: float) -> list[dict]:
    """Annex A.3.5.1: multiply all ranges of Table A.8 by the single-load range of Table A.7."""
    return [{"r": r, "dM": round(r * dMo_kNm, 3), "n": n} for r, n in zip(A8_R, A8_N)]


def dM_eq(hist: list[dict], m: float) -> float:
    """Formula (B.14)."""
    n = sum(b["n"] for b in hist)
    return (sum(b["n"] * b["dM"] ** m for b in hist) / n) ** (1 / m)


def dMo_from_hist(hist: list[dict], m: float) -> float:
    """Formulas (B.13) and (B.12): the single-load range at 1e6 cycles that does the same damage."""
    n = sum(b["n"] for b in hist)
    loga = math.log10(n) + m * math.log10(dM_eq(hist, m))
    return 10 ** ((loga - 6) / m)


# ------------------------------------------------------------------------------------------------ M-N curves
class MN:
    """Linear (B.8/B.9) or bilinear (B.10/B.11) M-N curve, moments in kNm."""

    def __init__(self, loga1, m1, loga2=None, m2=None, name=""):
        self.loga1, self.m1, self.loga2, self.m2, self.name = loga1, m1, loga2, m2, name

    @property
    def bilinear(self):
        return self.loga2 is not None

    @property
    def logM12(self):
        """Formula (B.11)."""
        return (self.loga2 - self.loga1) / (self.m2 - self.m1) if self.bilinear else None

    def N(self, dM):
        if dM <= 0:
            return math.inf
        if not self.bilinear or math.log10(dM) >= self.logM12:
            return 10 ** (self.loga1 - self.m1 * math.log10(dM))
        return 10 ** (self.loga2 - self.m2 * math.log10(dM))

    def dM_at(self, N):
        """Inverse: moment range with N cycles to failure."""
        lg = math.log10(N)
        if self.bilinear:
            Nk = 10 ** (self.loga1 - self.m1 * self.logM12)
            if N > Nk:
                return 10 ** ((self.loga2 - lg) / self.m2)
        return 10 ** ((self.loga1 - lg) / self.m1)

    @property
    def dMc(self):
        """Single-load fatigue capacity at 1e6 cycles, DF = 1 (Tables B.11/B.12)."""
        return self.dM_at(1e6)

    def as_dict(self):
        d = {"name": self.name, "loga1": round(self.loga1, 4), "m1": self.m1, "dMc": round(self.dMc, 1)}
        if self.bilinear:
            d.update({"loga2": round(self.loga2, 4), "m2": self.m2, "dM12": round(10 ** self.logM12, 1)})
        return d


def miner(hist: list[dict], curve: MN) -> dict:
    rows, D = [], 0.0
    for b in hist:
        N = curve.N(b["dM"])
        d = b["n"] / N
        D += d
        rows.append({"r": b["r"], "dM": round(b["dM"], 1), "n": b["n"], "N": N, "d": d})
    return {"rows": rows, "D": D, "life_years": 1 / D if D > 0 else math.inf}


# ------------------------------------------------------------------------------------------------ local model
class WellModel:
    """Two concentric Euler-Bernoulli beam strings in one bending plane.

    inner string: WH housing -> WH extension -> 20 in surface casing
    outer string: conductor housing -> conductor extension -> 36 in conductor
    z is measured DOWN from the wellhead datum (z = 0). Contact areas follow NORSOK U-001 Figure J.1:
      A, B  WH housing <-> conductor housing (radial contact, springs between strings)
      C, D  conductor housing <-> template slot rings (springs to the template, with radial gap)
      E     top of cement in the conductor/surface casing annulus (strings bonded below E)
      H     conductor <-> soil/cement (Winkler springs below the mudline)
      F     WH connector: the riser moment Mw and shear Qw are applied at the datum on the inner string
    """

    def __init__(self, **kw):
        p = dict(
            z_mud=4.0,             # mudline below datum [m]                                   ILLUSTRATIVE
            z_A=1.0, z_B=2.8,      # WH / conductor housing contacts
            z_C=1.6, z_D=3.6,      # template slot rings (upper ring, bottom of structure)
            z_wh_end=2.5,          # WH housing -> WH extension weld
            z_ch_end=3.0,          # conductor housing -> conductor extension girth weld (hot spot)
            shortfall=5.0,         # cement shortfall below mudline [m] -> top of cement E
            z_end=64.0,            # 60 m conductor below mudline (Table A.1 example)
            k_soil=3.0e6,          # Winkler soil+cement modulus [N/m per m]                   ILLUSTRATIVE
            k_C=60e6, k_D=120e6,   # template ring lateral stiffness [N/m]                     ILLUSTRATIVE
            gap=0.0,               # radial clearance at C and D [m]
            k_AB=5e9, k_bond=5e9,  # contact / bonded-annulus penalty stiffness [N/m]
            template=True,
            H=H_LFJ,
            wh=tube(0.762, 0.143),              # 30 in OD x 18 3/4 in bore forging
            whx=tube(20 * INCH, 1.25 * INCH),   # WH extension
            sc=tube(20 * INCH, 1.0 * INCH),     # surface casing (Table A.1)
            ch=tube(0.9652, 0.0889),            # 38 in OD conductor housing forging
            cx=tube(36 * INCH, 2.0 * INCH),     # conductor extension and conductor (Table A.1)
        )
        p.update(kw)
        self.p = p
        self._mesh()

    # mesh: fine near the top, coarser deeper; all special depths are nodes
    def _mesh(self):
        p = self.p
        special = [0, p["z_A"], p["z_B"], p["z_C"], p["z_D"], p["z_mud"], p["z_wh_end"], p["z_ch_end"],
                   p["z_mud"] + p["shortfall"], 0.9, p["z_end"]]
        z = set(np.round(np.arange(0, 20.0001, 0.1), 4))
        z |= set(np.round(np.arange(20, p["z_end"] + 1e-6, 0.5), 4))
        z |= set(round(s, 4) for s in special)
        self.z = np.array(sorted(v for v in z if v <= p["z_end"] + 1e-9))
        self.n = len(self.z)

    def _sec_inner(self, zm):
        p = self.p
        if zm < p["z_wh_end"]:
            return p["wh"]
        if zm < p["z_mud"] + 0.5:
            return p["whx"]
        return p["sc"]

    def _sec_outer(self, zm):
        p = self.p
        return p["ch"] if zm < p["z_ch_end"] else p["cx"]

    def _outer_starts(self):
        return 0.9   # conductor housing top (no outer string above)

    def solve(self, Mw: float, Qw: float | None = None, iters: int = 60):
        """Static response to the riser moment Mw [Nm] (and shear Qw = Mw/H) at the datum."""
        p = self.p
        if Qw is None:
            Qw = Mw / p["H"]
        n = self.n
        ndof = 4 * n                       # inner (v, th) then outer (v, th) for every node
        iv = lambda i: 2 * i
        ov = lambda i: 2 * n + 2 * i
        K = np.zeros((ndof, ndof))
        z = self.z
        z_toc = p["z_mud"] + p["shortfall"]
        z0_out = self._outer_starts()
        for e in range(n - 1):
            L = z[e + 1] - z[e]
            zm = 0.5 * (z[e] + z[e + 1])
            for base, sec in ((iv, self._sec_inner(zm)), (ov, self._sec_outer(zm) if zm > z0_out else None)):
                if sec is None:
                    continue
                EI = E_STEEL * sec["I"]
                ke = EI / L ** 3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                                             [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
                idx = [base(e), base(e) + 1, base(e + 1), base(e + 1) + 1]
                K[np.ix_(idx, idx)] += ke
            if zm > p["z_mud"]:
                ks = p["k_soil"]
                kf = ks * L / 420 * np.array([[156, 22 * L, 54, -13 * L], [22 * L, 4 * L * L, 13 * L, -3 * L * L],
                                              [54, 13 * L, 156, -22 * L], [-13 * L, -3 * L * L, -22 * L, 4 * L * L]])
                idx = [ov(e), ov(e) + 1, ov(e + 1), ov(e + 1) + 1]
                K[np.ix_(idx, idx)] += kf
        # inactive outer dofs above the conductor housing top
        for i in range(n):
            if z[i] < z0_out - 1e-9:
                K[ov(i), ov(i)] += 1.0
                K[ov(i) + 1, ov(i) + 1] += 1.0

        def couple(i, k):
            a, b = iv(i), ov(i)
            K[a, a] += k; K[b, b] += k; K[a, b] -= k; K[b, a] -= k

        for zc in (p["z_A"], p["z_B"]):
            couple(self._node(zc), p["k_AB"])
        for i in range(n):
            if z[i] >= z_toc - 1e-9:
                couple(i, p["k_bond"])
        F = np.zeros(ndof)
        F[iv(0)] += Qw                     # shear at the datum (+v)
        F[iv(0) + 1] -= Mw                 # moment of the riser force about the datum, same sense as Qw
        # template springs with gaps: active-set iteration
        iC, iD = self._node(p["z_C"]), self._node(p["z_D"])
        springs = [(iC, p["k_C"]), (iD, p["k_D"])] if p["template"] else []
        state = {i: 0 for i, _ in springs}       # -1, 0, +1 contact side
        for _ in range(iters):
            Kt = K.copy()
            Ft = F.copy()
            for i, k in springs:
                s = state[i]
                if s != 0:
                    Kt[ov(i), ov(i)] += k
                    Ft[ov(i)] += k * p["gap"] * s     # spring force k*(v - s*gap)
            u = np.linalg.solve(Kt, Ft)
            new = {}
            for i, k in springs:
                v = u[ov(i)]
                new[i] = 1 if v > p["gap"] else (-1 if v < -p["gap"] else 0)
            if new == state:
                break
            state = new
        self.u, self.Mw, self.Qw = u, Mw, Qw
        res = {"z": z.tolist()}
        res["v_in"] = u[0:2 * n:2].tolist()
        res["v_out"] = u[2 * n::2].tolist()
        res["M_in"], res["M_out"] = self._moments(u, iv, inner=True), self._moments(u, ov, inner=False)
        fC = p["k_C"] * (u[ov(iC)] - p["gap"] * state.get(iC, 0)) if state.get(iC, 0) else 0.0
        fD = p["k_D"] * (u[ov(iD)] - p["gap"] * state.get(iD, 0)) if state.get(iD, 0) else 0.0
        res["F_C"], res["F_D"] = -fC, -fD          # reaction on the well (negative = resisting)
        res["template_moment"] = -(fC * (p["z_C"]) + fD * p["z_D"]) if springs else 0.0
        return res

    def _node(self, zc):
        return int(np.argmin(np.abs(self.z - zc)))

    def _moments(self, u, base, inner):
        """Nodal bending moment EI*v'' from the element curvatures, averaged at nodes (sign of the riser moment = -)."""
        z, n = self.z, self.n
        M = np.zeros(n)
        cnt = np.zeros(n)
        z0_out = self._outer_starts()
        for e in range(n - 1):
            L = z[e + 1] - z[e]
            zm = 0.5 * (z[e] + z[e + 1])
            sec = self._sec_inner(zm) if inner else (self._sec_outer(zm) if zm > z0_out else None)
            if sec is None:
                continue
            EI = E_STEEL * sec["I"]
            idx = [base(e), base(e) + 1, base(e + 1), base(e + 1) + 1]
            ue = u[idx]
            # curvature at both ends of a cubic Hermite element
            v1, t1, v2, t2 = ue
            k1 = (-6 * v1 - 4 * L * t1 + 6 * v2 - 2 * L * t2) / L ** 2
            k2 = (6 * v1 + 2 * L * t1 - 6 * v2 + 4 * L * t2) / L ** 2
            M[e] += EI * k1; cnt[e] += 1
            M[e + 1] += EI * k2; cnt[e + 1] += 1
        cnt[cnt == 0] = 1
        return (M / cnt).tolist()

    def moment_at(self, res, zc, inner=False):
        i = self._node(zc)
        return (res["M_in"] if inner else res["M_out"])[i]


# ------------------------------------------------------------------------------------------------ BEF (closed form)
def bef_moment(x, M0, P, EI, k):
    """Semi-infinite beam on a Winkler foundation, end moment M0 and end shear P acting in the same sense."""
    beta = (k / (4 * EI)) ** 0.25
    bx = beta * x
    A = math.exp(-bx) * (math.cos(bx) + math.sin(bx))
    B = math.exp(-bx) * math.sin(bx)
    return M0 * A + P / beta * B


def bef_max(M0, P, EI, k):
    beta = (k / (4 * EI)) ** 0.25
    bx = math.atan(P / (2 * beta * M0 + P))
    x = bx / beta
    return x, bef_moment(x, M0, P, EI, k), beta


# ------------------------------------------------------------------------------------------------ validation
def validate_bef(EI=None, k=3.0e6, L=80.0, M0=1.0e6, P=0.1e6):
    """Same element formulas as WellModel on a single semi-infinite beam: compare with the closed form."""
    EI = EI or E_STEEL * tube(36 * INCH, 2 * INCH)["I"]
    z = np.linspace(0, L, 801)
    n = len(z)
    K = np.zeros((2 * n, 2 * n))
    for e in range(n - 1):
        h = z[e + 1] - z[e]
        ke = EI / h ** 3 * np.array([[12, 6 * h, -12, 6 * h], [6 * h, 4 * h * h, -6 * h, 2 * h * h],
                                     [-12, -6 * h, 12, -6 * h], [6 * h, 2 * h * h, -6 * h, 4 * h * h]])
        kf = k * h / 420 * np.array([[156, 22 * h, 54, -13 * h], [22 * h, 4 * h * h, 13 * h, -3 * h * h],
                                     [54, 13 * h, 156, -22 * h], [-13 * h, -3 * h * h, -22 * h, 4 * h * h]])
        idx = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        K[np.ix_(idx, idx)] += ke + kf
    F = np.zeros(2 * n)
    F[0], F[1] = P, -M0
    u = np.linalg.solve(K, F)
    M = []
    for e in range(n - 1):
        h = z[e + 1] - z[e]
        v1, t1, v2, t2 = u[2 * e:2 * e + 4]
        M.append(EI * (-6 * v1 - 4 * h * t1 + 6 * v2 - 2 * h * t2) / h ** 2)
    M = np.array(M)
    exact = np.array([bef_moment(x, M0, P, EI, k) for x in z[:-1]])
    return float(np.max(np.abs(M - exact)) / M0)


# ------------------------------------------------------------------------------------------------ the example
LEVELS = [6000, 3000, 1500, 750, 375, 187.5]          # NORSOK B.4.2.4 Note 1 moment ranges [kNm]
BASE = dict(k_soil=5.0e6, k_C=200e6, k_D=400e6, gap=0.002, shortfall=5.0)                # ILLUSTRATIVE
HOT = dict(SCF_gw=1.10, t_gw=50.8,                          # conductor girth weld GW1           ILLUSTRATIVE
           slot_L=2.5, slot_W=2.0e-3, SCF_T=2.0)           # template slot weld TS1 beam model  ILLUSTRATIVE


def kappa_T(h=HOT):
    """Hot-spot stress per unit ring force [MPa per kN]: ring force F shared by two fixed-fixed beams
    loaded at mid span -> M = (F/2) L / 8 = F L / 16, sigma = SCF M / W."""
    return h["SCF_T"] * h["slot_L"] / (16 * h["slot_W"]) / 1e6 * 1e3


def lower_bound(points, key):
    """Bilinear M-N curve with the S-N slopes (m1 = 3, m2 = 5) placed on or below every point."""
    fin = [p for p in points if p[key] is not None and math.isfinite(p[key])]
    if not fin:
        return None
    b1 = [p for p in fin if p[key] <= 1e6] or fin
    b2 = [p for p in fin if p[key] > 1e6] or fin
    la1 = min(math.log10(p[key]) + 3 * math.log10(p["dM"]) for p in b1)
    la2 = min(math.log10(p[key]) + 5 * math.log10(p["dM"]) for p in b2)
    return MN(la1, 3.0, la2, 5.0)


def evaluate(params=None, hot=None, dMo=1436.0, keep_profiles=False):
    """NORSOK U-001 B.4.2.4 a)-f) with the simplified local model, then M-N fit and Miner damage."""
    params = BASE | (params or {})
    hot = HOT | (hot or {})
    mdl = WellModel(**params)
    W = mdl.p["cx"]["W"]
    z_gw = mdl.p["z_ch_end"]
    kT = kappa_T(hot)
    pts, prof = [], {}
    for dM in LEVELS:
        Ma = dM / 2 * 1e3                       # fully reversed: +Mw and -Mw, R = -1
        rp, rn = mdl.solve(+Ma), mdl.solve(-Ma)
        dMgw = abs(mdl.moment_at(rp, z_gw) - mdl.moment_at(rn, z_gw))
        s_gw = dMgw / W / 1e6 * hot["SCF_gw"]
        dF = abs(rp["F_C"] - rn["F_C"]) / 1e3
        s_T = dF * kT
        pts.append({"dM": dM, "dM_gw": dMgw / 1e3, "ds_gw": s_gw, "N_gw": sn_N(s_gw, SN_C1_CP, hot["t_gw"]),
                    "dF_C": dF, "ds_T": s_T, "N_T": sn_N(s_T, SN_D_CP) if s_T > 1e-9 else math.inf})
        if keep_profiles:
            prof[str(dM)] = {k: [round(v, 7) for v in rp[k]] for k in ("v_in", "v_out", "M_in", "M_out")} | {
                "F_C": rp["F_C"], "F_D": rp["F_D"]}
    hist = histogram(dMo)
    c_gw, c_T = lower_bound(pts, "N_gw"), lower_bound(pts, "N_T")
    r_gw = miner(hist, c_gw)
    r_T = miner(hist, c_T) if c_T else {"D": 0.0, "life_years": math.inf, "rows": []}
    out = {"points": pts, "mn_gw": c_gw, "mn_T": c_T, "miner_gw": r_gw, "miner_T": r_T, "dMo": dMo}
    if keep_profiles:
        out["profiles"] = prof
        out["z"] = mdl.z.tolist()
        out["p"] = {k: v for k, v in mdl.p.items() if not isinstance(v, dict)}
    return out


def _clean(x):
    if isinstance(x, float):
        return None if not math.isfinite(x) else x
    if isinstance(x, dict):
        return {k: _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    if isinstance(x, MN):
        return x.as_dict()
    return x


def build():
    out = {"meta": {"generated_by": "model/fatigue_model.py",
                    "note": "Illustrative teaching example. Not project data."}}
    out["validation"] = {"bef_max_rel_error": validate_bef()}
    # --- loads (main example: 350 m water depth, BOP on WH mode)
    band, mode = "250-500", "BOP on WH"
    dMo = TABLE_A7[mode][band]
    hist = histogram(dMo)
    out["loads"] = {"water_depth": 350, "band": band, "mode": mode, "dMo": dMo, "H_LFJ": H_LFJ, "H_XT": H_XT,
                    "tableA7": TABLE_A7, "tableA8": [{"r": r, "n": n} for r, n in zip(A8_R, A8_N)],
                    "n_total": sum(A8_N), "hist": hist, "tableA4": TABLE_A4,
                    "example1": {"dMo": 2124, "r": 0.1, "n": 3948892, "dM": 212.4},
                    "dMo_check": {str(m): dMo_from_hist(histogram(1.0), m) for m in (3, 4, 5)},
                    "dMeq": {str(m): dM_eq(hist, m) for m in (3, 4, 5)},
                    "dMo_back": {str(m): dMo_from_hist(hist, m) for m in (3, 4, 5)}}
    # --- sections and EI share
    secs = {"conductor": tube(36 * INCH, 2 * INCH), "surface_casing": tube(20 * INCH, 1 * INCH),
            "conductor_30": tube(30 * INCH, 1 * INCH)}
    out["sections"] = {k: {"D_mm": s["D"] * 1e3, "t_mm": s["t"] * 1e3, "d_mm": s["d"] * 1e3, "I_m4": s["I"],
                           "W_m3": s["W"], "A_m2": s["A"]} for k, s in secs.items()}
    EIc, EIs = E_STEEL * secs["conductor"]["I"], E_STEEL * secs["surface_casing"]["I"]
    out["share_EI"] = {"EI_c": EIc, "EI_s": EIs, "conductor": EIc / (EIc + EIs), "casing": EIs / (EIc + EIs)}
    # --- beam on elastic foundation, bare conductor, shear lever h = 4 m to the mudline
    h = BASE_Z_MUD = 4.0
    M0, P = 1.0 + h / H_LFJ, 1.0 / H_LFJ
    bef = {}
    for k in (1e6, 5e6, 20e6):
        x_max, M_max, beta = bef_max(M0, P, EIc, k)
        xs = np.linspace(0, 40, 161)
        bef[str(int(k / 1e6))] = {"k": k, "beta": beta, "L_char": 1 / beta, "x_max": x_max, "M_max": M_max,
                                  "x": xs.tolist(), "M": [bef_moment(x, M0, P, EIc, k) for x in xs],
                                  "k_theta_free": EIc * beta}
    out["bef"] = {"EI": EIc, "M0": M0, "P": P, "h": h, "cases": bef}
    # --- main example
    ex = evaluate(dMo=dMo, keep_profiles=True)
    DF, DFF = TABLE_B4["permanent"]["service life"], 10
    g, t = ex["miner_gw"], ex["miner_T"]
    out["example"] = {
        "inputs": BASE | HOT | {"kappa_T": kappa_T(), "z_gw": 3.0, "SN": SN_C1_CP, "SN_T": SN_D_CP,
                                "DF": DF, "DFF": DFF},
        "points": ex["points"], "mn_gw": ex["mn_gw"], "mn_T": ex["mn_T"], "z": ex["z"], "p": ex["p"],
        "profiles": ex["profiles"],
        "miner_gw": {"D": g["D"], "life": g["life_years"], "service": g["life_years"] / DF,
                     "days": 365.25 * g["life_years"] / DF, "rows": g["rows"]},
        "miner_T": {"D": t["D"], "life": t["life_years"], "service": t["life_years"] / DFF,
                    "days": 365.25 * t["life_years"] / DFF, "rows": t["rows"]},
        "screen_gw": {"dMc": ex["mn_gw"].dMc, "dMc_over_DF": ex["mn_gw"].dMc / DF ** (1 / 3), "dMo": dMo,
                      "life_linear_m3": (ex["mn_gw"].dMc / dMo) ** 3},
        "screen_T": {"dMc": ex["mn_T"].dMc, "dMc_over_DFF": ex["mn_T"].dMc / DFF ** (1 / 3), "dMo": dMo},
    }
    # linear-only (m = 3 everywhere) damage for comparison with the bilinear result
    lin = MN(ex["mn_gw"].loga1, 3.0)
    out["example"]["miner_gw_linear"] = miner(hist, lin)["life_years"]
    # --- what-if cases and sensitivities (fatigue life, DF = 1, years)
    def lives(params=None, hot=None, dMo_=dMo):
        e = evaluate(params, hot, dMo_)
        return {"gw": e["miner_gw"]["life_years"], "T": e["miner_T"]["life_years"],
                "dMc_gw": e["mn_gw"].dMc, "dMc_T": e["mn_T"].dMc if e["mn_T"] else None}
    sens = {
        "band": {b: lives(dMo_=TABLE_A7["BOP on WH"][b]) for b in ("80-250", "250-500", "500-1500")},
        "xt_mode": {b: lives(dMo_=TABLE_A7["BOP on XT"][b]) for b in ("80-250", "250-500", "500-1500")},
        "shortfall": [[s_, lives({"shortfall": s_})] for s_ in (0.0, 2.5, 5.0, 10.0, 15.0)],
        "k_soil": [[k_ / 1e6, lives({"k_soil": k_})] for k_ in (2e6, 5e6, 10e6, 20e6)],
        "gap": [[g_ * 1e3, lives({"gap": g_})] for g_ in (0.0, 0.001, 0.002, 0.004, 0.008)],
        "k_template": [[f_, lives({"k_C": 200e6 * f_, "k_D": 400e6 * f_})] for f_ in (0.5, 1, 2, 4)],
        "no_template": lives({"template": False}),
        "SCF": [[s_, lives(hot={"SCF_gw": s_})] for s_ in (1.0, 1.1, 1.2, 1.3)],
        "load_relief": [[f_, lives(dMo_=TABLE_A7["BOP on WH"]["80-250"] * f_)] for f_ in (1.0, 0.8, 0.6, 0.5)],
    }
    out["sensitivity"] = sens
    # moment profiles for the animation: no template / base / tight slot, and two cement shortfalls
    prof = {}
    for name, prm in {"no_template": {"template": False}, "base": {}, "tight": {"gap": 0.0},
                      "short0": {"shortfall": 0.0}, "short10": {"shortfall": 10.0}}.items():
        e = evaluate(prm, dMo=dMo, keep_profiles=True)
        prof[name] = {"z": e["z"], **e["profiles"]["3000"]}
    out["profiles"] = prof
    # transfer functions (stress range vs WH moment range) for the nonlinearity chart
    mdl = WellModel(**BASE)
    W = mdl.p["cx"]["W"]
    tr = []
    for dM in np.geomspace(100, 6000, 31):
        Ma = dM / 2 * 1e3
        rp, rn = mdl.solve(+Ma), mdl.solve(-Ma)
        dMgw = abs(mdl.moment_at(rp, 3.0) - mdl.moment_at(rn, 3.0))
        tr.append({"dM": float(dM), "ds_gw": dMgw / W / 1e6 * HOT["SCF_gw"],
                   "dF_C": abs(rp["F_C"] - rn["F_C"]) / 1e3, "ds_T": abs(rp["F_C"] - rn["F_C"]) / 1e3 * kappa_T()})
    out["transfer"] = tr
    out["norsok"] = {"tableB4": TABLE_B4, "table4": TABLE_4, "N001_DFF": N001_DFF,
                     "rel_disp_mm": 100, "girth_weld_class": "C1", "min_fatigue_service_life_years": 1}
    # thermal growth illustration (Annex E): free growth and fully restrained force for 20 in x 1 in casing
    alpha, dT, Lfree = 1.2e-5, 60.0, 120.0
    sc = secs["surface_casing"]
    out["thermal"] = {"alpha": alpha, "dT": dT, "L": Lfree, "growth_mm": alpha * dT * Lfree * 1e3,
                      "restrained_force_MN": E_STEEL * sc["A"] * alpha * dT / 1e6}
    out["sn"] = {"C1_CP": SN_C1_CP, "C1_air": SN_C1_AIR, "C1_FC": SN_C1_FC, "D_CP": SN_D_CP,
                 "knee_stress_C1_CP": sn_knee_stress(SN_C1_CP),
                 "thickness_factor_gw": (50.8 / SN_C1_CP["t_ref"]) ** SN_C1_CP["k"]}
    return out


def report(o):
    print("== validation, beam FE vs closed form, max error / M0:", f"{o['validation']['bef_max_rel_error']:.2e}")
    L = o["loads"]
    print("== loads: dMo", L["dMo"], "kNm, total cycles", L["n_total"])
    print("   dMo back-calculated (normalised histogram):", {k: round(v, 4) for k, v in L["dMo_check"].items()})
    print("   dMeq:", {k: round(v, 1) for k, v in L["dMeq"].items()})
    for k, s in o["sections"].items():
        print(f"== {k}: I = {s['I_m4']:.5e} m4, W = {s['W_m3']:.5e} m3, A = {s['A_m2']:.5e} m2")
    print("== EI share conductor/casing:", round(o["share_EI"]["conductor"], 3), round(o["share_EI"]["casing"], 3))
    for k, b in o["bef"]["cases"].items():
        print(f"== BEF k={k} MPa: beta = {b['beta']:.4f} 1/m, 1/beta = {b['L_char']:.2f} m, "
              f"max {b['M_max']:.3f} Mw at {b['x_max']:.2f} m below mudline, k_theta = {b['k_theta_free']/1e6:.0f} MNm/rad")
    ex = o["example"]
    print("== kappa_T =", round(ex["inputs"]["kappa_T"], 4), "MPa/kN")
    for p in ex["points"]:
        print(f"   dM {p['dM']:7.1f} kNm  dM_gw {p['dM_gw']:8.1f} kNm  ds_gw {p['ds_gw']:7.2f} MPa  N {p['N_gw']:.3e} | "
              f"dF_C {p['dF_C']:7.1f} kN  ds_T {p['ds_T']:6.2f} MPa  N {p['N_T']:.3e}")
    print("== M-N GW1:", ex["mn_gw"].as_dict())
    print("== M-N TS1:", ex["mn_T"].as_dict())
    g, t = ex["miner_gw"], ex["miner_T"]
    print(f"== Miner GW1: D/yr = {g['D']:.4e}, life = {g['life']:.2f} yr, service (DF 10) = {g['service']:.3f} yr "
          f"= {g['days']:.0f} days; linear m=3 life = {ex['miner_gw_linear']:.2f} yr")
    print(f"== Miner TS1: D/yr = {t['D']:.4e}, life = {t['life']:.2f} yr, service (DFF 10) = {t['service']:.3f} yr "
          f"= {t['days']:.0f} days")
    print("== screening GW1:", {k: round(v, 1) for k, v in ex["screen_gw"].items()})
    print("== screening TS1:", {k: round(v, 1) for k, v in ex["screen_T"].items()})
    for k, v in o["sensitivity"].items():
        print("== sens", k, json.dumps(_clean(v))[:400])
    print("== thermal:", o["thermal"])
    print("== thickness factor GW1:", round(o["sn"]["thickness_factor_gw"], 4), "knee stress", round(o["sn"]["knee_stress_C1_CP"], 1))


if __name__ == "__main__":
    o = build()
    report(o)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(_clean(o), f, indent=1)
    print("->", OUT, f"{os.path.getsize(OUT)/1e3:.0f} kB")
