"""Synthetic (illustrative) petrophysics for the composite well: logs, Archie saturation, net pay, pressure gradients.

Nothing here is real data. All curves are generated from layer definitions + a fixed random seed, then the SAME
equations the narration quotes (Archie, gradient intersection) are applied to them, so every number on screen is computed.
"""
from __future__ import annotations
import random
from dataclasses import dataclass

from . import well_model as M

Z0, Z1 = 3930.0, 4130.0          # logged interval, m TVD
STEP = 0.5
RW, A_ARCHIE, M_ARCHIE, N_ARCHIE = 0.05, 1.0, 2.0, 2.0     # ohm.m at reservoir temperature, a, m, n
GR_SAND, GR_SHALE = 35.0, 110.0
CUT_VSH, CUT_PHI, CUT_SW = 0.40, 0.12, 0.60                 # [SIM] illustrative cutoffs

# pressure gradients, bar/m (reservoir conditions, illustrative)
G_GAS, G_OIL, G_WATER = 0.025, 0.076, 0.106

STREAKS = [(3985.0, 3988.0), (4012.0, 4016.0), (4075.0, 4077.0)]    # thin shale stringers inside the sand


def fluid_at(z: float) -> str:
    if z < M.RES_TOP or z >= M.RES_BASE:
        return "none"
    if z < M.GOC:
        return "gas"
    if z < M.OWC:
        return "oil"
    return "water"


def is_sand(z: float) -> bool:
    return M.RES_TOP <= z < M.RES_BASE and not any(a <= z < b for a, b in STREAKS)


@dataclass
class Logs:
    z: list
    gr: list
    rt: list
    dphi: list
    nphi: list
    phi: list          # "interpreted" porosity
    vsh: list
    sw: list           # from Archie
    fluid: list
    net_sand: list
    net_res: list
    net_pay: list


def generate(seed: int = 4) -> Logs:
    rnd = random.Random(seed)
    zs, gr, rt, dphi, nphi, phi, vsh, sw, fl = [], [], [], [], [], [], [], [], []
    z = Z0
    while z <= Z1 + 1e-9:
        sand = is_sand(z)
        f = fluid_at(z)
        if sand:
            g = GR_SAND + rnd.gauss(0, 4)
            true_phi = (0.23 if z < 4088 else 0.17) + rnd.gauss(0, 0.008)
            true_sw = {"gas": 0.20, "oil": 0.28, "water": 1.0}[f] + (rnd.gauss(0, 0.015) if f != "water" else 0.0)
            true_sw = min(max(true_sw, 0.05), 1.0)
            r = RW / (A_ARCHIE * true_phi ** M_ARCHIE * true_sw ** N_ARCHIE)
            d = true_phi + (0.045 if f == "gas" else 0.0) + rnd.gauss(0, 0.004)
            n = true_phi - (0.075 if f == "gas" else -0.01) + rnd.gauss(0, 0.004)
        else:
            g = GR_SHALE + rnd.gauss(0, 5)
            r = 2.0 + rnd.gauss(0, 0.15)
            d, n = 0.10 + rnd.gauss(0, 0.01), 0.34 + rnd.gauss(0, 0.012)
            true_phi, true_sw = 0.05, 1.0
        zs.append(z)
        gr.append(g)
        rt.append(max(r, 0.2))
        dphi.append(d)
        nphi.append(n)
        fl.append(f if sand else "none")
        # interpretation from the curves only (what an analyst would do)
        v = min(max((g - GR_SAND) / (GR_SHALE - GR_SAND), 0.0), 1.0)
        vsh.append(v)
        p = max((d + n) / 2 if f != "gas" else (d * 0.5 + n * 0.5 + 0.0), 0.01) if sand else 0.05
        phi.append(p)
        s_ = (RW / (A_ARCHIE * max(p, 0.02) ** M_ARCHIE * rt[-1])) ** (1.0 / N_ARCHIE)
        sw.append(min(max(s_, 0.0), 1.0))
        z += STEP
    ns = [v < CUT_VSH and M.RES_TOP <= zz < M.RES_BASE for v, zz in zip(vsh, zs)]
    nr = [a and p > CUT_PHI for a, p in zip(ns, phi)]
    npay = [a and s < CUT_SW for a, s in zip(nr, sw)]
    return Logs(zs, gr, rt, dphi, nphi, phi, vsh, sw, fl, ns, nr, npay)


def thickness(flags) -> float:
    return sum(flags) * STEP


def summary(lg: Logs | None = None) -> dict:
    lg = lg or generate()
    gross = M.RES_BASE - M.RES_TOP
    ns, nr, npay = thickness(lg.net_sand), thickness(lg.net_res), thickness(lg.net_pay)
    return dict(gross=gross, net_sand=ns, net_reservoir=nr, net_pay=npay, ntg=nr / gross, pay_to_gross=npay / gross)


# ---- pressure points + gradient fit ----------------------------------------------------------------------
# Water-leg reference pressure at 4,000 m, chosen so the gas crest at the reservoir top reads exactly the forecast pore
# pressure: the window charts of chapters 1, 4 and 7 and the measured pressures of chapter 8 then agree at the crest.
P_REF = (M.bar(M.RES_TOP, M.pp(M.RES_TOP))
         - (G_WATER * (M.FWL - 4000.0) - G_OIL * (M.FWL - M.GOC) - G_GAS * (M.GOC - M.RES_TOP)))


def p_water(z):
    return P_REF + G_WATER * (z - 4000.0)


def p_oil(z):
    return p_water(M.FWL) - G_OIL * (M.FWL - z)


def p_gas(z):
    return p_oil(M.GOC) - G_GAS * (M.GOC - z)


def pressure_points(seed: int = 9):
    rnd = random.Random(seed)
    pts = []
    for fluid, depths, fn in (("gas", (3955, 3972, 3984), p_gas), ("oil", (3996, 4014, 4030, 4042), p_oil), ("water", (4068, 4090, 4108), p_water)):
        for z in depths:
            pts.append((fluid, float(z), fn(z) + rnd.gauss(0, 0.05)))
    return pts


def fit_line(points):
    """Least-squares P = a + g z through (z, p) pairs -> (a, g)."""
    n = len(points)
    sz = sum(z for z, _ in points)
    sp = sum(p for _, p in points)
    szz = sum(z * z for z, _ in points)
    szp = sum(z * p for z, p in points)
    g = (n * szp - sz * sp) / (n * szz - sz * sz)
    a = (sp - g * sz) / n
    return a, g


def fitted_contacts():
    pts = pressure_points()
    lines = {}
    for fl in ("gas", "oil", "water"):
        lines[fl] = fit_line([(z, p) for f, z, p in pts if f == fl])
    (ao, go), (aw, gw), (ag, gg) = lines["oil"], lines["water"], lines["gas"]
    z_fwl = (ao - aw) / (gw - go)
    z_goc = (ag - ao) / (go - gg)
    return dict(points=pts, lines=lines, fwl=z_fwl, goc=z_goc)


def archie_example():
    """Worked example shown on screen: gas-zone numbers."""
    phi, rt = 0.23, RW / (A_ARCHIE * 0.23 ** M_ARCHIE * 0.20 ** N_ARCHIE)
    sw = (RW / (A_ARCHIE * phi ** M_ARCHIE * rt)) ** (1.0 / N_ARCHIE)
    return dict(rw=RW, phi=phi, rt=rt, sw=sw)


if __name__ == "__main__":
    lg = generate()
    print("summary", {k: round(v, 2) for k, v in summary(lg).items()})
    c = fitted_contacts()
    print("fitted gradients (bar/m):", {k: round(v[1], 4) for k, v in c["lines"].items()})
    print("FWL from intersection: %.1f m (model %.0f)   GOC: %.1f m (model %.0f)" % (c["fwl"], M.FWL, c["goc"], M.GOC))
    print("archie example", {k: round(v, 3) for k, v in archie_example().items()})
