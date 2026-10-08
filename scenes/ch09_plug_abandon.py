"""Ch 9: Plugging and abandonment.

One plug list (PLUGS) drives the well schematic, the 'well so far' strip and the as-abandoned drawing. Plug depths and
lengths are DRAWING values (the narration states no D-010 minimum lengths). Every plug is cement grey; it gets a green
outline only once it has been verified (9.06). Barrier envelopes: primary = blue outline, secondary = red outline.
"""
from __future__ import annotations
import math
from typing import NamedTuple

import skia

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.shapes import pill
from scenes.common.look import col, hex_rgb, lighten, darken, wrap_to
from scenes.common.stage import ease_inout

TITLE = "Plugging and abandonment"


# ====================================================================================== the ONE plug list
class Plug(NamedTuple):
    key: str
    top: float       # m
    base: float      # m
    hole: str        # "open" (against rock) or "cased" (inside the 9 5/8 in casing, on a bridge plug)
    role: str        # "primary" / "secondary" / "surface"
    source: str
    label: str


PLUGS = (
    Plug("res_p", 3750.0, 4110.0, "open", "primary", "reservoir", "reservoir: primary"),
    Plug("res_s", 3300.0, 3750.0, "open", "secondary", "reservoir", "reservoir: secondary, across the 9⅝ in shoe"),
    Plug("sa_p", 2880.0, 2980.0, "cased", "primary", "Sand A", "Sand A: primary, on a bridge plug"),
    Plug("sa_s", 2700.0, 2800.0, "cased", "secondary", "Sand A", "Sand A: secondary, on a bridge plug"),
    Plug("surf", 305.0, 450.0, "cased", "surface", "seabed", "surface plug, just below the seabed"),
)
PLUG = {p.key: p for p in PLUGS}
DEEP = ("res_p", "res_s", "sa_p", "sa_s")
BP_LEN = 12.0                       # bridge plug length (m, drawing)
CUT_Z = M.WATER_DEPTH + 5.0         # casing cut a few metres below the seabed (drawing; no figure is narrated)
SHOE_958 = M.programme()[-1].shoe   # 3,400 m
# top of cement behind each string (drawing values; the 9 5/8 in cement covers Sand A, ch. 6)
TOC = {"30in conductor": M.WATER_DEPTH, "20in surface casing": M.WATER_DEPTH, "13-3/8in intermediate": 800.0,
       "9-5/8in intermediate": 2600.0}
MUD_DIM = "#a8790a"                 # mud amber, dimmed for the overview drawing (same hue: still 'mud')
RUBBER = "#2f2f35"


def W(b, i, needle, frac=0.0):
    """Time `needle` is spoken in sentence i of beat b (fails loudly if the phrase is not in that sentence)."""
    txt = b._sentences()[i]
    assert needle.lower() in txt.lower(), (b.id, i, needle, txt)
    return b.word(i, needle, frac)


def outline(st, x0, y0, x1, y1, color, z, width=0.035, alpha=1.0):
    return st.line([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color, width, z, alpha=alpha, closed=True)


def leader(st, x0, y0, x1, y1, z=0.45, color=P.MUTED):
    return [st.line([(x0, y0), (x1, y1)], color, 0.018, z, alpha=0.8), st.circle(x1, y1, 0.045, P.TEXT, z + 0.01, role="disc")]


def tag(st, x, y, text, fg=P.TEXT, size=0.18, z=0.5, align="l", bg=P.PANEL2):
    return pill(st, x, y, text, bg, fg, size, z, pad=0.16, align=align)


# ====================================================================================== the overview schematic
SX = -3.6                                            # well axis
ROCK_HW = 1.7                                        # rock half-width
KN = [(220, 3.62), (300, 3.3), (500, 2.85), (1000, 2.35), (2000, 1.55), (2600, 1.05), (3050, -0.45), (3300, -0.85),
      (3900, -1.85), (4200, -3.4)]                   # depth -> y (stretched at the zones of interest; ticks are labelled)
INCH = 0.05
WALL = 0.04
OH = M.HOLE_TD_IN * INCH / 2                         # 8 1/2 in open hole half-width


def zy(z):
    for (z0, y0), (z1, y1) in zip(KN[:-1], KN[1:]):
        if z <= z1:
            return y0 + (y1 - y0) * (z - z0) / (z1 - z0)
    (z0, y0), (z1, y1) = KN[-2], KN[-1]
    return y0 + (y1 - y0) * (z - z0) / (z1 - z0)


def _strings():
    return [(s.name, s.od_in * INCH / 2, s.hole_in * INCH / 2, s.shoe) for s in M.programme()]


def plug_hw(p):
    return OH if p.hole == "open" else _strings()[-1][1] - WALL


def _vrect(st, x0, x1, za, zb, color, z, alpha=1.0, role=None):
    """Rect between x0..x1 and depths za..zb (schematic scale)."""
    ya, yb = zy(za), zy(zb)
    return st.rect((x0 + x1) / 2, (ya + yb) / 2, x1 - x0, ya - yb, color, z, alpha=alpha, role=role)


def schematic(st, t_in, cut=False, grow=None, fluids=False):
    """Depth-stretched P&A schematic: rock, strings with walls, annulus cement / mud, bore mud. Returns dict of groups."""
    g = {"rock": [], "well": [], "axis": [], "fluids": []}
    top = CUT_Z if cut else M.WATER_DEPTH
    g["rock"].append(st.rect(SX, (3.62 + 3.3) / 2, 2 * ROCK_HW, 0.32, P.SEA, 0.0))
    g["rock"].append(_vrect(st, SX - ROCK_HW, SX + ROCK_HW, M.WATER_DEPTH, M.TD, P.ROCK, 0.0))
    for za, zb, c in ((3800, M.RES_TOP, P.SHALE), (M.SAND_A[0], M.SAND_A[1], P.SAND), (M.RES_TOP, M.RES_BASE, P.SAND),
                      (M.RES_BASE, M.TD, P.ROCK2)):
        g["rock"].append(_vrect(st, SX - ROCK_HW, SX + ROCK_HW, za, zb, c, 0.01))
    g["rock"].append(st.rect(SX, 3.3, 2 * ROCK_HW, 0.04, P.SEABED, 0.02))
    strs = _strings()
    # open hole of each section (dark), then annulus fills, then bore
    prev_shoe = M.WATER_DEPTH
    for name, od, hole, shoe in strs:
        g["well"].append(_vrect(st, SX - hole, SX + hole, max(prev_shoe, top), shoe, P.BG, 0.03))
        prev_shoe = shoe
    g["well"].append(_vrect(st, SX - OH, SX + OH, strs[-1][3], M.TD, P.BG, 0.03))
    prev = None
    for i, (name, od, hole, shoe) in enumerate(strs):
        segs = []
        if prev is None:
            segs.append((M.WATER_DEPTH, shoe, hole))
        else:
            segs.append((M.WATER_DEPTH, prev[3], prev[1] - WALL))
            segs.append((prev[3], shoe, hole))
        for za, zb, outer in segs:
            for a, b_, c in ((za, min(zb, TOC[name]), MUD_DIM), (max(za, TOC[name]), zb, P.CEMENT)):
                a = max(a, top)
                if b_ - a < 1:
                    continue
                for sgn in (-1, 1):
                    x0, x1 = sorted((SX + sgn * od, SX + sgn * outer))
                    g["well"].append(_vrect(st, x0, x1, a, b_, c, 0.05 + 0.01 * i, alpha=1.0 if c == P.CEMENT else 0.75))
        prev = (name, od, hole, shoe)
    idh = strs[-1][1] - WALL
    g["well"].append(_vrect(st, SX - idh, SX + idh, top, strs[-1][3], MUD_DIM, 0.09, alpha=0.8))
    g["well"].append(_vrect(st, SX - OH, SX + OH, strs[-1][3], M.TD, MUD_DIM, 0.09, alpha=0.8))
    # casing walls (inner strings in front) and shoes
    walls = []
    for i, (name, od, hole, shoe) in enumerate(strs):
        for sgn in (-1, 1):
            x = SX + sgn * (od - WALL / 2)
            if grow:
                w = st.rect(x, zy(top), WALL, 0.0001, P.STEEL, 0.12 + 0.01 * i, anchor="t")
                st.scale_to(w, grow + 0.15 * i, grow + 0.15 * i + 1.1, sy=zy(top) - zy(shoe))
            else:
                w = _vrect(st, x - WALL / 2, x + WALL / 2, top, shoe, P.STEEL, 0.12 + 0.01 * i)
            walls.append(w)
            ys = zy(shoe)
            walls.append(st.poly([(SX + sgn * od, ys), (SX + sgn * (od + 0.09), ys), (SX + sgn * od, ys + 0.1)], P.STEEL, 0.17))
    g["well"] += walls
    if not cut:
        g["well"] += [st.rect(SX, 3.36, 2.0, 0.07, P.STEEL_DK, 0.2), st.rect(SX, 3.45, 0.62, 0.22, P.STEEL_DK, 0.21)]
    # depth axis
    for zt in (300, 1000, 2000, 3000, 4000):
        lab = "seabed 300 m" if zt == 300 else f"{zt:,} m"
        g["axis"].append(st.text(lab, SX - ROCK_HW - 0.1, zy(zt), 0.14, P.MUTED, 0.3, align="r"))
        g["axis"].append(st.rect(SX - ROCK_HW - 0.02, zy(zt), 0.06, 0.015, P.MUTED, 0.3))
    g["axis"].append(st.text("depth scale stretched", SX, -3.58, 0.13, P.MUTED, 0.3))
    if fluids:
        g["fluids"] = reservoir_fluids(st)
    allo = g["rock"] + g["well"] + g["axis"] + g["fluids"]
    st.fade_in(allo, t_in, 0.6)
    g["all"] = allo
    return g


def reservoir_fluids(st):
    """Gas over oil over water in the reservoir sand (contacts from well_model)."""
    out = []
    for za, zb, c, lab in ((M.RES_TOP, M.GOC, P.GAS, "gas"), (M.GOC, M.OWC, P.OIL, "oil"), (M.OWC, M.RES_BASE, P.WATER, "water")):
        out.append(_vrect(st, SX - ROCK_HW, SX + ROCK_HW, za, zb, c, 0.015, alpha=0.5, role="flat"))
        out.append(st.text(lab, SX - 1.05, (zy(za) + zy(zb)) / 2, 0.14, P.TEXT, 0.3, kind="bold"))
    return out


def plug_objs(st, p, z=0.1):
    """A plug (cement grey) in the schematic, with its bridge plug for cased-hole plugs."""
    hw = plug_hw(p)
    if p.hole == "open" and p.top < SHOE_958 < p.base:        # runs up inside the 9 5/8 in shoe: casing ID above it
        idw = _strings()[-1][1] - WALL
        return [_vrect(st, SX - idw, SX + idw, p.top, SHOE_958, P.CEMENT, z), _vrect(st, SX - hw, SX + hw, SHOE_958, p.base, P.CEMENT, z)]
    out = [_vrect(st, SX - hw, SX + hw, p.top, p.base, P.CEMENT, z)]
    if p.role == "surface":       # rock to rock: the inner annuli are cemented across the surface plug too (under the casing walls)
        hw20 = _strings()[1][1] - WALL
        out.append(_vrect(st, SX - hw20, SX + hw20, p.top, p.base, P.CEMENT, min(z, 0.11)))
    if p.hole == "cased":
        out.append(_vrect(st, SX - hw, SX + hw, p.base, p.base + max(BP_LEN, 25), P.STEEL_DK, z + 0.005))
    return out


def plug_verified(st, p, z=0.3):
    hw = plug_hw(p) + 0.05
    return outline(st, SX - hw, zy(p.top) + 0.02, SX + hw, zy(p.base) - 0.02, P.SAFE, z, 0.03)


def envelope(st, p, z=0.3):
    c = P.PRIMARY_B if p.role == "primary" else P.SECOND_B
    hw = 0.5
    return outline(st, SX - hw, zy(p.top), SX + hw, zy(p.base), c, z, 0.035)


# ====================================================================================== 'well so far' strip plugs (cement grey)
def strip_plugs(st, t0, t1, keys, t_ver=None):
    with st.span(t0, t1):
        objs, ver = [], []
        for k in keys:
            p = PLUG[k]
            ya, yb = F.depth_y(p.top), F.depth_y(p.base)
            objs.append(st.rect(F.STRIP_CX, (ya + yb) / 2, 0.18, max(ya - yb, 0.05), P.CEMENT, 0.25))
            if t_ver is not None:
                o = outline(st, F.STRIP_CX - 0.11, ya + 0.01, F.STRIP_CX + 0.11, yb - 0.01, P.SAFE, 0.26, 0.022)
                ver.append(o)
        st.fade_in(objs, t0, 0.5)
        if ver:
            st.fade_in(ver, t_ver, 0.4)


# ====================================================================================== 9.01 why seal a discovery?
def beat_why(st, tl):
    b = tl["9.01"]
    s = b.sent
    with st.span(b.start, b.end):
        sch = schematic(st, b.start + 0.05, grow=b.start + 0.3)
        # discovery: gas over oil
        t_oil = W(b, 1, "found oil")
        fl = reservoir_fluids(st)
        st.fade_in(fl, t_oil - 0.3, 0.6)
        st.ripple(SX + 0.9, zy(4010), t_oil, t_oil + 2.4, P.OIL, period=0.8, r0=0.2, r1=1.1)
        ya = zy(4000)
        disc = tag(st, -1.6, ya, "DISCOVERY: gas over oil", P.OIL, 0.2)
        dl = leader(st, -1.65, ya, SX + 0.6, ya)
        st.fade_in(disc + dl, t_oil + 0.2, 0.4)
        k1 = st.text("FOUND OIL", -0.6, 1.9, 0.46, P.OIL, 0.5, align="l", kind="bold")
        t_seal = W(b, 1, "seal this well")
        k2 = st.text("→ SEAL IT FOR EVER", -0.6, 1.15, 0.46, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(k1, t_oil, 0.4)
        st.fade_in(k2, t_seal, 0.4)
        why = st.text("WHY?", -0.6, -0.4, 1.3, P.WARN, 0.5, align="l", kind="bold")
        st.pop_in(why, s[2] - 0.1, 0.4)
        st.fade_in(why, s[2] - 0.1, 0.2)
        st.fade_out([k1, k2, why], s[3] - 0.1, 0.4)
        # a measuring instrument, not a producer; new wells for a field
        t_meas = W(b, 3, "measuring instrument")
        cA = st.rect(1.3, 0.2, 4.0, 4.3, P.PANEL, 0.2)
        aT = st.text("THIS WELL", 1.3, 1.95, 0.26, P.TEXT, 0.3, kind="bold")
        aS = st.text("a measuring instrument", 1.3, 1.55, 0.2, P.PORE, 0.3)
        logs = []
        import random
        rnd = random.Random(4)
        for j, (x0, amp, colr) in enumerate(((0.0, 0.32, P.TEXT), (1.25, 0.28, P.MUTED), (2.5, 0.3, P.TEXT))):
            pts, v = [], 0.0
            for k in range(40):
                yv = 1.15 - k * 0.058
                v = 0.6 * v + rnd.uniform(-1, 1)
                if -0.45 > yv > -0.9:
                    v = 1.6
                pts.append((-0.3 + x0 + amp + amp * 0.6 * max(-1.4, min(1.4, v)), yv))
            ln = st.line(pts, colr, 0.03, 0.3)
            logs.append(ln)
            logs.append(st.rect(-0.3 + x0 + amp, (1.15 - 39 * 0.058 + 1.15) / 2, 0.012, 39 * 0.058, P.GRID, 0.25))
        st.fade_in([cA, aT, aS] + logs[1::2], t_meas - 0.4, 0.4)
        for j, ln in enumerate(logs[0::2]):
            st.draw_on(ln, t_meas + 0.1 * j, t_meas + 2.4 + 0.1 * j)
        npd = st.text("✕  not a producer", 1.3, -1.6, 0.22, P.BAD, 0.3, kind="bold")
        st.fade_in(npd, W(b, 3, "not a producer"), 0.4)
        t_new = W(b, 3, "new wells")
        cB = st.rect(5.55, 0.2, 4.0, 4.3, P.PANEL, 0.2)
        bT = st.text("IF A FIELD IS BUILT", 5.55, 1.95, 0.26, P.TEXT, 0.3, kind="bold")
        bS = st.text("new wells, built for the job", 5.55, 1.55, 0.2, P.PORE, 0.3)
        sb = st.rect(5.55, 0.75, 3.4, 0.03, P.SEABED, 0.3)
        plat = [st.rect(5.55, 1.05, 0.9, 0.12, P.STEEL_DK, 0.3), st.rect(5.25, 0.9, 0.06, 0.25, P.STEEL_DK, 0.3),
                st.rect(5.85, 0.9, 0.06, 0.25, P.STEEL_DK, 0.3)]
        paths = []
        for dx in (-1.3, -0.4, 0.5, 1.4):
            pts = [(5.55 + dx * 0.08 * (1 - (k / 12)) + dx * (k / 12) ** 2, 0.75 - k * 0.16) for k in range(13)]
            paths.append(st.line(pts, P.STEEL, 0.035, 0.3))
        st.fade_in([cB, bT, bS, sb] + plat, t_new - 0.3, 0.4)
        for j, ln in enumerate(paths):
            st.draw_on(ln, t_new + 0.15 * j, t_new + 1.8 + 0.15 * j, "BEZIER")
        prod = st.text("producers", 5.55, -1.6, 0.22, P.OIL, 0.3, kind="bold")
        st.fade_in(prod, t_new + 1.4, 0.4)
        cards = [cA, aT, aS, npd, cB, bT, bS, sb, prod] + plat + paths + logs
        st.fade_out(cards, s[4] - 0.2, 0.4)
        # P&A: the well as a tube from a pressurised reservoir to the sea, then sealed
        t4 = s[4]
        st.fade(sch["well"], t4, t4 + 0.8, 1.0, 0.3)
        st.fade_out(disc + dl, t4, 0.3)
        hw = 0.22
        tube = [st.line([(SX - hw, zy(4110)), (SX - hw, 3.3)], P.TEXT, 0.03, 0.4), st.line([(SX + hw, zy(4110)), (SX + hw, 3.3)], P.TEXT, 0.03, 0.4)]
        for ln in tube:
            st.draw_on(ln, t4 + 0.2, t4 + 1.4, "BEZIER")
        t_sealed = W(b, 4, "sealed from")
        st.flow([(SX - 0.07, zy(4040)), (SX - 0.07, 3.3), (SX - 0.3, 3.58)], t4 + 0.8, t_sealed + 0.3, P.OIL, n=16, speed=1.6, r=0.04, z=0.45)
        st.flow([(SX + 0.07, zy(3970)), (SX + 0.07, 3.3), (SX + 0.3, 3.58)], t4 + 0.9, t_sealed + 0.3, P.GAS, n=12, speed=1.9, r=0.04, z=0.45)
        gy = zy(4030)
        gp = tag(st, -1.6, gy, "reservoir", P.TEXT, 0.18)
        gl = leader(st, -1.65, gy, SX + 0.3, gy)
        st.fade_in(gp + gl, t4 + 0.5, 0.4)
        # big readout: a pipe from a pressurised reservoir to the open sea
        rd = [st.text("A PIPE FROM", -0.6, 2.75, 0.24, P.MUTED, 0.5, align="l", kind="bold"),
              st.text("reservoir pressure", -0.6, 1.25, 0.2, P.MUTED, 0.5, align="l"),
              st.text("TO THE OPEN SEA", -0.6, 0.55, 0.34, P.TEXT, 0.5, align="l", kind="bold")]
        st.fade_in(rd[:2], t4 + 0.5, 0.4)
        st.fade_in(rd[2], t4 + 1.4, 0.4)
        st.counter(-0.6, 1.95, t4 + 0.6, t4 + 2.2, 0, M.bar(4000, M.pp(4000)), fmt="≈ {:.0f} bar", size=0.56, color=P.PORE, z=0.52,
                   align="l", hold=W(b, 4, "geological") - 0.35)
        st.fade_out(rd, W(b, 4, "geological") - 0.6, 0.4)
        op = tag(st, -1.6, 3.3, "open to the sea", P.TEXT, 0.18)
        ol = leader(st, -1.65, 3.3, SX + 0.3, 3.3)
        st.fade_in(op + ol, t4 + 1.0, 0.4)
        # sealed: the plug list, bottom to top
        plugs = {k: plug_objs(st, PLUG[k], 0.42) for k in PLUG}
        t_res, t_sb = W(b, 4, "reservoir"), W(b, 4, "to seabed")
        for i, k in enumerate(("res_p", "res_s", "sa_p", "sa_s", "surf")):
            st.fade_in(plugs[k], t_sealed + (t_sb - t_sealed) * i / 4, 0.35)
        sealed = st.text(wrap_to("SEALED FOR GEOLOGICAL TIME", 0.44, 6.6, "bold"), -0.6, -0.4, 0.44, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(sealed, W(b, 4, "geological"), 0.5)
        allp = [o for v in plugs.values() for o in v]
        st.fade_out(gp + gl + op + ol + tube + [sealed] + allp, s[5] - 0.2, 0.5)
        st.fade(sch["well"], s[5], s[5] + 0.8, 0.3, 1.0)
        # designed in from the start: outline plan before spud -> detailed programme after logging
        ty = -0.5
        arr = st.arrow(-1.2, ty, 7.3, ty, P.MUTED, 0.04, 0.2, 0.4)
        st.fade_in(arr, s[5] + 0.2, 0.4)
        ms = [(-0.4, "spud", W(b, 5, "before the first")), (3.0, "TD + logs", W(b, 5, "detailed")), (6.3, "P&A", W(b, 5, "what we found"))]
        for x, lab, t in ms:
            d = st.circle(x, ty, 0.1, P.TEXT, 0.45, role="disc")
            tx = st.text(lab, x, ty - 0.4, 0.2, P.TEXT, 0.45, kind="bold")
            st.fade_in([d, tx], min(t, s[5] + 0.6), 0.4)

        def doc(x, y, title, sub, colr, t):
            o = [st.rect(x, y, 0.8, 1.0, P.PANEL2, 0.45)] + [st.rect(x, y + 0.28 - 0.18 * k, 0.48, 0.03, P.MUTED, 0.46) for k in range(4)]
            o += [st.text(title, x, y + 0.85, 0.22, colr, 0.46, kind="bold"), st.text(sub, x, ty - 0.8, 0.17, P.MUTED, 0.46)]
            st.fade_in(o, t, 0.45)
            return o
        doc(-0.4, 0.55, "outline P&A plan", "before the first metre", P.WARN, W(b, 5, "outline plan"))
        doc(3.0, 0.55, "detailed P&A programme", "once the logs are in", P.WARN, W(b, 5, "detailed programme"))
        dot = st.circle(-0.4, ty, 0.07, P.WARN, 0.5)
        st.fade_in(dot, W(b, 5, "outline plan"), 0.3)
        st.move(dot, W(b, 5, "outline plan") + 0.3, W(b, 5, "detailed programme"), to=(3.0, ty))
        st.move(dot, W(b, 5, "logs tell"), b.end - 0.6, to=(6.3, ty))


# ====================================================================================== 9.02 every source of inflow
def beat_sources(st, tl):
    b = tl["9.02"]
    s = b.sent
    with st.span(b.start, b.end):
        schematic(st, b.start, fluids=True)
        kick = st.text("FIND EVERY SOURCE OF INFLOW", -1.6, 3.45, 0.3, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(kick, s[0], 0.5)
        st.fade_out(kick, s[3] - 0.3, 0.4)
        # the reservoir
        t_res = W(b, 1, "reservoir")
        ry = zy(4030)
        rc = tag(st, -1.6, ry, "RESERVOIR: gas and oil", P.OIL, 0.2)
        rl = leader(st, -1.65, ry, SX + 0.45, ry)
        st.fade_in(rc + rl, t_res, 0.4)
        t_hc = W(b, 3, "a hydrocarbon zone")
        st.flow([(SX - 0.07, zy(4040)), (SX - 0.07, 3.3), (SX - 0.3, 3.58)], t_res + 0.2, t_hc + 0.4, P.OIL, n=16, speed=1.5, r=0.04, z=0.45)
        st.flow([(SX + 0.07, zy(3975)), (SX + 0.07, 3.3), (SX + 0.3, 3.58)], t_res + 0.3, t_hc + 0.4, P.GAS, n=12, speed=1.8, r=0.04, z=0.45)
        # any permeable layer with pressure: a scan down the section
        t_any = W(b, 1, "any permeable")
        t_sc1 = s[2] - 0.1

        def scan(c, t, look):
            f = min(1.0, max(0.0, (t - t_any) / (t_sc1 - t_any)))
            y = 3.3 + (zy(M.TD) - 3.3) * ease_inout(f)
            a = min(1.0, (t - t_any) / 0.3) * min(1.0, (t_sc1 + 0.4 - t) / 0.4)
            if a <= 0:
                return
            p = skia.Paint(Color=col(hex_rgb(P.TEXT), 0.55 * a), AntiAlias=True, StrokeWidth=0.02, Style=skia.Paint.kStroke_Style)
            c.drawLine(SX - ROCK_HW, y, SX + ROCK_HW, y, p)
        st.procedural(t_any, t_sc1 + 0.4, 0.5, scan)
        # Sand A
        t_sa = W(b, 2, "thin overpressured sand")
        sy_ = zy(sum(M.SAND_A) / 2)
        hl = _vrect(st, SX - ROCK_HW, SX + ROCK_HW, M.SAND_A[0] - 8, M.SAND_A[1] + 8, P.SAND, 0.4, alpha=0.9, role="flat")
        st.fade_in(hl, t_sa, 0.3)
        st.ripple(SX + 1.0, sy_, t_sa, t_sa + 2.2, P.SAND, period=0.8, r0=0.15, r1=0.9)
        sc = tag(st, -1.6, sy_, "SAND A: 2,980–3,000 m, overpressured", P.SAND, 0.2)
        sl = leader(st, -1.65, sy_, SX + 1.2, sy_)
        st.fade_in(sc + sl, t_sa + 0.2, 0.4)
        t_push = W(b, 2, "push fluid")
        t_op = W(b, 3, "overpressured zone")
        # flow potential: from the sand into the well and up the wellbore to the seabed
        for sgn in (-1, 1):
            st.flow([(SX + sgn * 1.1, sy_), (SX + sgn * 0.12, sy_), (SX + sgn * 0.12, 3.3), (SX + sgn * 0.35, 3.58)],
                    t_push - 0.2, t_op + 0.4, P.WATER, n=12, speed=1.5, r=0.035, z=0.46)
        pp_ = tag(st, -1.6, sy_ + 1.0, "could flow up the well to the seabed", P.WATER, 0.17)
        pl = leader(st, -1.65, sy_ + 1.0, SX + 0.15, sy_ + 1.0)
        st.fade_in(pp_ + pl, t_push + 0.3, 0.4)
        st.fade_out(pp_ + pl, t_op - 0.2, 0.3)
        # two permanent barriers for each source
        envs = {k: envelope(st, PLUG[k]) for k in DEEP}
        st.pop_in(envs["res_p"], t_hc, 0.4)
        st.pop_in(envs["res_s"], t_hc + 0.5, 0.4)
        st.pop_in(envs["sa_p"], t_op, 0.4)
        st.pop_in(envs["sa_s"], t_op + 0.5, 0.4)
        for k in DEEP:
            st.fade_in(envs[k], (t_hc if k.startswith("res") else t_op) + (0.5 if k.endswith("s") else 0.0), 0.2)
        x2r = tag(st, -1.6 + st.measure("RESERVOIR: gas and oil", 0.2, "bold") + 0.65, ry, "× 2", P.TEXT, 0.22)
        x2s = tag(st, -1.6 + st.measure("SAND A: 2,980–3,000 m, overpressured", 0.2, "bold") + 0.65, sy_, "× 2", P.TEXT, 0.22)
        st.fade_in(x2r, t_hc + 0.8, 0.3)
        st.fade_in(x2s, t_op + 0.8, 0.3)
        lg = [outline(st, -1.55, 2.95, -1.0, 2.65, P.PRIMARY_B, 0.5), st.text("primary barrier", -0.85, 2.8, 0.2, P.PRIMARY_B, 0.5, align="l", kind="bold"),
              outline(st, -1.55, 2.4, -1.0, 2.1, P.SECOND_B, 0.5), st.text("secondary barrier", -0.85, 2.25, 0.2, P.SECOND_B, 0.5, align="l", kind="bold")]
        st.fade_in(lg, t_hc + 0.2, 0.4)
        stmt = st.text(wrap_to("Hydrocarbons, or overpressure that can flow to the seabed: TWO permanent barriers", 0.28, 4.3, "bold"),
                       5.25, -1.3, 0.28, P.TEXT, 0.5, kind="bold")
        st.fade_in(stmt, W(b, 3, "two permanent"), 0.5)


# ====================================================================================== 9.03 rock to rock (two cutaways + tunnel)
def cutaway(st, cx, cemented, t_in, z=0.0, yt=3.1, yb=-2.9):
    """Section through a cased well: rock | annulus | casing | bore | casing | annulus | rock; a plug inside the casing."""
    o = {}
    RW, HH, OD, WL = 1.45, 0.8, 0.52, 0.08
    lay = [(yt, 1.7, P.ROCK2), (1.7, -1.0, P.SHALE), (-1.0, yb, P.SAND)]
    o["rock"] = [st.rect(cx, (a + c) / 2, 2 * RW, a - c, colr, z) for a, c, colr in lay]
    o["hole"] = [st.rect(cx, (yt + yb) / 2, 2 * HH, yt - yb, P.BG, z + 0.02)]
    ann = P.CEMENT if cemented else P.MUD
    o["ann"] = [st.rect(cx + sg * (OD + HH) / 2, (yt + yb) / 2, HH - OD, yt - yb, ann, z + 0.03, alpha=1.0 if cemented else 0.75) for sg in (-1, 1)]
    o["bore"] = [st.rect(cx, (yt + yb) / 2, 2 * (OD - WL), yt - yb, P.MUD, z + 0.03, alpha=0.6)]
    o["plug"] = [st.rect(cx, 0.3, 2 * (OD - WL), 1.8, P.CEMENT, z + 0.05)]
    o["casing"] = [st.rect(cx + sg * (OD - WL / 2), (yt + yb) / 2, WL, yt - yb, P.STEEL, z + 0.08) for sg in (-1, 1)]
    o["dims"] = (RW, HH, OD, WL, yt, yb)
    o["all"] = o["rock"] + o["hole"] + o["ann"] + o["bore"] + o["plug"] + o["casing"]
    st.fade_in(o["all"], t_in, 0.5)
    return o


def beat_rock(st, tl):
    b = tl["9.03"]
    s = b.sent
    with st.span(b.start, b.end):
        HX, FX = -0.6, -4.0
        H = cutaway(st, HX, True, b.start + 0.1)
        RW, HH, OD, WL, yt, yb = H["dims"]
        # plan view: the whole cross-section, seen from above
        t_cs = W(b, 0, "whole cross-section")
        px, py = FX, 1.05
        disc = [st.circle(px, py, 1.25, P.ROCK, 0.1, role="earth"), st.circle(px, py, 0.8, P.CEMENT, 0.12, role="disc"),
                st.ring(px, py, 0.52, 0.08, P.STEEL, 0.14), st.circle(px, py, 0.44, P.CEMENT, 0.13, role="disc")]
        st.fade_in(disc, t_cs - 0.2, 0.5)
        dl = st.text("seen from above", px, py + 1.5, 0.17, P.MUTED, 0.3)
        dlab = [st.text("plug", px, py, 0.17, P.BG, 0.3, kind="bold")]
        st.fade_in([dl] + dlab, t_cs, 0.4)
        t_ann = W(b, 0, "every annulus")
        ring_hl = st.ring(px, py, 0.8, 0.28, P.SAFE, 0.2, alpha=0.0)
        st.ripple(px, py, t_ann, t_ann + 1.6, P.TEXT, period=0.8, r0=0.85, r1=1.4)
        al = st.text("+ the annulus cement", px, py - 1.55, 0.18, P.TEXT, 0.3, kind="bold")
        st.fade_in(al, t_ann, 0.4)
        # labels on the holding cutaway
        lx = 1.05
        labs = []

        def lab(y, txt, tx, ty, t, colr=P.TEXT):
            o = tag(st, lx, y, txt, colr, 0.17) + leader(st, lx - 0.05, y, tx, ty)
            st.fade_in(o, t, 0.4)
            labs.extend(o)
        lab(2.55, "casing", HX + OD - WL / 2, 2.55, t_cs - 0.1)
        lab(0.45, "plug inside the casing", HX + 0.1, 0.45, t_cs + 0.3)
        lab(-0.4, "annulus cement", HX + (OD + HH) / 2, -0.4, t_ann)
        t_tight = W(b, 0, "tight rock")
        lab(1.3, "tight caprock", HX + HH + 0.4, 1.3, t_tight)
        t_crack = W(b, 0, "pressure below")
        arrs = []
        for x in (HX - HH - 0.35, HX, HX + HH + 0.35):
            arrs += st.arrow(x, -2.3, x, -1.15 if abs(x - HX) > 0.1 else -0.75, P.PORE, 0.06, 0.2, 0.4)
        st.fade_in(arrs, t_crack - 0.2, 0.4)
        lab(-2.0, "pressure below", HX + HH + 0.35, -2.0, t_crack, P.PORE)
        t_rr = W(b, 0, "rock to rock")
        ok = outline(st, HX - HH - 0.12, 1.2, HX + HH + 0.12, -0.6, P.SAFE, 0.3, 0.035)
        st.draw_on(ok, t_rr - 0.2, t_rr + 0.7)
        hp = pill(st, HX, -3.3, "✓ HOLDS: rock to rock", P.SAFE, "#06201c", 0.2, 0.5)
        st.fade_in(hp, t_rr + 0.3, 0.4)
        st.fade_out(labs + arrs, s[1] - 0.2, 0.4)
        # the tunnel analogy
        tx0, tx1 = 1.6, 7.35
        tcx = (tx0 + tx1) / 2
        card = st.rect(tcx, -1.05, tx1 - tx0, 3.9, P.PANEL, 0.1)
        ttl = st.text("A TUNNEL", tx0 + 0.25, 0.62, 0.18, P.MUTED, 0.3, align="l", kind="bold")
        rk = [st.rect(tcx, 0.17, tx1 - tx0 - 0.3, 0.36, P.ROCK, 0.15), st.rect(tcx, -2.47, tx1 - tx0 - 0.3, 0.36, P.ROCK, 0.15)]
        lin = [st.rect(tcx, -0.21, tx1 - tx0 - 0.3, 0.12, P.STEEL, 0.2), st.rect(tcx, -2.23, tx1 - tx0 - 0.3, 0.12, P.STEEL, 0.2)]
        inside = st.rect(tcx, -1.22, tx1 - tx0 - 0.3, 1.9, P.BG, 0.16)
        lt = st.text("lining", tx1 - 0.3, -0.45, 0.15, P.MUTED, 0.3, align="r")
        st.fade_in([card, ttl] + rk + lin + [inside, lt], s[1], 0.5)
        t_door = W(b, 2, "door")
        door = st.rect(tcx, -1.22, 0.22, 1.9, P.CEMENT, 0.25)
        st.pop_in(door, t_door, 0.4)
        st.fade_in(door, t_door, 0.2)
        dlb = st.text("door", tcx, -2.47, 0.17, P.TEXT, 0.3, kind="bold")
        st.fade_in(dlb, t_door + 0.2, 0.3)
        t_gap = W(b, 2, "gap behind")
        gap = st.rect(tcx, -0.075, tx1 - tx0 - 0.3, 0.15, P.BG, 0.21)
        cracks = [st.rect(tcx - 1.3, -0.21, 0.16, 0.13, P.BG, 0.22), st.rect(tcx + 1.3, -0.21, 0.16, 0.13, P.BG, 0.22)]
        st.fade_in([gap] + cracks, t_gap - 0.1, 0.4)
        gl = tag(st, tcx, 0.17, "gap behind the lining", P.BAD, 0.16, align="c")
        st.fade_in(gl, t_gap + 0.2, 0.3)
        path = [(tx0 + 0.3, -1.25), (tcx - 1.3, -1.0), (tcx - 1.3, -0.08), (tcx + 1.3, -0.08), (tcx + 1.3, -1.0), (tx1 - 0.3, -1.25)]
        st.flow(path, t_gap + 0.1, b.end, P.BAD, n=22, speed=1.3, r=0.04, z=0.4)
        # the failing well: plug in the casing, uncemented annulus
        t_f = s[3]
        st.fade_out(disc + [dl, al, ring_hl] + dlab, t_f - 0.5, 0.4)
        Fc = cutaway(st, FX, False, t_f - 0.2)
        leak = []
        for sg in (-1, 1):
            xa = FX + sg * (OD + HH) / 2
            leak.append([(FX + sg * (HH + 0.45), -2.75), (xa, -2.2), (xa, 2.9)])     # from the sand, up the open annulus
        for pth in leak:
            st.flow(pth, W(b, 3, "run behind") - 0.6, b.end, P.BAD, n=12, speed=1.3, r=0.04, z=0.4)
        fp = pill(st, FX, -3.3, "✕ FAILS: leaks behind it", P.BAD, "#ffffff", 0.18, 0.5)
        st.fade_in(fp, W(b, 3, "no use") , 0.4)
        ua = tag(st, FX, 2.65, "uncemented annulus", P.MUD, 0.16, align="c", z=0.55)
        st.fade_in(ua, W(b, 3, "run behind"), 0.3)
        st.fade_out(dlb, t_f, 0.3)
        m1 = tag(st, tcx - 1.45, -2.47, "door ≈ plug", P.TEXT, 0.16, align="c")
        m2 = tag(st, tcx + 1.35, -2.47, "gap ≈ uncemented annulus", P.TEXT, 0.16, align="c")
        st.fade_in(m1, W(b, 3, "plug inside"), 0.3)
        st.fade_in(m2, W(b, 3, "run behind"), 0.3)


# ====================================================================================== zoomed cased-hole cutaway (9.04 - 9.06)
class Zoom:
    """Large section of the 9 5/8 in casing around Sand A, on its own depth scale."""

    def __init__(self, st, cx, z_top, z_bot, y_top, y_bot, hh=1.25, od=0.95, wl=0.1, rw=1.95):
        self.st, self.cx = st, cx
        self.zt, self.zb, self.yt, self.yb = z_top, z_bot, y_top, y_bot
        self.hh, self.od, self.wl, self.rw = hh, od, wl, rw
        self.id = od - wl

    def Y(self, z):
        return self.yt + (z - self.zt) * (self.yb - self.yt) / (self.zb - self.zt)

    def base(self, t_in, ann=P.CEMENT, toc=None, ticks=True, sand=True, z=0.0):
        st, cx = self.st, self.cx
        yt, yb = self.yt, self.yb
        out = [st.rect(cx, (yt + yb) / 2, 2 * self.rw, yt - yb, P.SHALE, z)]
        if sand:
            ya, yb2 = self.Y(M.SAND_A[0]), self.Y(M.SAND_A[1])
            out.append(st.rect(cx, (ya + yb2) / 2, 2 * self.rw, ya - yb2, P.SAND, z + 0.01))
        out.append(st.rect(cx, (yt + yb) / 2, 2 * self.hh, yt - yb, P.BG, z + 0.02))
        self.ann = []
        for sg in (-1, 1):
            xm = cx + sg * (self.od + self.hh) / 2
            if toc is not None and toc > self.zt:
                y0 = self.Y(toc)
                self.ann.append(st.rect(xm, (yt + y0) / 2, self.hh - self.od, yt - y0, P.MUD, z + 0.03, alpha=0.75))
                self.ann.append(st.rect(xm, (y0 + yb) / 2, self.hh - self.od, y0 - yb, P.CEMENT, z + 0.03))
            else:
                self.ann.append(st.rect(xm, (yt + yb) / 2, self.hh - self.od, yt - yb, ann, z + 0.03, alpha=1.0 if ann == P.CEMENT else 0.75))
        self.bore = st.rect(cx, (yt + yb) / 2, 2 * self.id, yt - yb, P.MUD, z + 0.04, alpha=0.7)
        self.walls = [st.rect(cx + sg * (self.od - self.wl / 2), (yt + yb) / 2, self.wl, yt - yb, P.STEEL, z + 0.3) for sg in (-1, 1)]
        out += self.ann + [self.bore] + self.walls
        if ticks:
            for zt in range(int(math.ceil(self.zt / 100.0) * 100), int(self.zb) + 1, 100):
                y = self.Y(zt)
                out.append(st.text(f"{zt:,} m", cx - self.rw - 0.12, y, 0.15, P.MUTED, z + 0.3, align="r"))
                out.append(st.rect(cx - self.rw - 0.03, y, 0.07, 0.015, P.MUTED, z + 0.3))
        st.fade_in(out, t_in, 0.5)
        self.objs = out
        return out

    def bridge_plug(self, z_top, t_run=None, t_set=None, z=0.35, run_from=None):
        """Bridge plug: steel mandrel, steel slips above and below a rubber element. Optionally run in and set."""
        st, cx = self.st, self.cx
        y0, y1 = self.Y(z_top), self.Y(z_top + BP_LEN)
        h = y0 - y1
        yc = (y0 + y1) / 2
        body = st.rect(cx, yc, 0.42, h, P.STEEL_DK, z)
        rub = st.rect(cx, yc, 0.42, h * 0.34, RUBBER, z + 0.01, role="solid")
        slips = []
        for sg in (-1, 1):
            for yy, d in ((y0 - h * 0.17, -1), (y1 + h * 0.17, 1)):
                slips.append(st.poly([(cx + sg * 0.21, yy + d * h * 0.14), (cx + sg * 0.21, yy - d * h * 0.14), (cx + sg * 0.36, yy + d * h * 0.14)],
                                     P.STEEL, z + 0.02))
        parts = [body, rub] + slips
        if t_set is not None:
            st.scale_to(rub, t_set, t_set + 0.6, sx=2 * self.id)
            for sl in slips:
                sx = st.state[sl]["loc"][0]
                st.move(sl, t_set, t_set + 0.6, dx=(self.id - 0.36) * (1 if sx > cx else -1))
        else:
            st.state[rub]["scale"] = (2 * self.id, h * 0.34, 1.0)
            rub.scale = [2 * self.id, h * 0.34, 1.0]
            for sl in slips:
                sx = st.state[sl]["loc"][0]
                st.move(sl, self.st._span[0], self.st._span[0] + 0.01, dx=(self.id - 0.36) * (1 if sx > cx else -1))
        if t_run is not None:
            dy = (run_from if run_from is not None else self.yt - 0.3) - yc
            for o in parts:
                st.move(o, t_run[0] - 0.01, t_run[0], dy=dy, interp="CONSTANT")
                st.move(o, t_run[0], t_run[1], dy=-dy)
        return parts


def method_list(st, x, y, items, times, t_in, dy=0.95):
    """Right-column list; the active item is lit, earlier ones dim."""
    head = st.text("BEHIND CASING: THREE WAYS", x, y + 0.6, 0.2, P.MUTED, 0.5, align="l", kind="bold")
    st.fade_in(head, t_in, 0.4)
    rows = []
    for i, (txt, t) in enumerate(zip(items, times)):
        yy = y - i * dy
        hl = st.rect(x + 2.2, yy, 4.6, 0.75, P.PANEL2, 0.45, alpha=0.0)
        n = st.text(str(i + 1), x + 0.2, yy, 0.3, P.WARN, 0.5, kind="bold")
        tx = st.text(wrap_to(txt, 0.2, 3.7, "bold"), x + 0.55, yy, 0.2, P.MUTED, 0.5, align="l", kind="bold")
        st.fade_in([n, tx], t_in + 0.15 * i, 0.4)
        st.fade(hl, t - 0.2, t + 0.2, 0.0, 1.0)
        st.recolor(tx, t - 0.2, t + 0.2, P.TEXT)
        if i + 1 < len(times):
            st.fade(hl, times[i + 1] - 0.2, times[i + 1] + 0.2, 1.0, 0.0)
            st.recolor(tx, times[i + 1] - 0.2, times[i + 1] + 0.2, P.MUTED)
        rows.append((hl, n, tx))
    return rows


# ====================================================================================== 9.04 open hole, then three ways behind casing
def beat_ways(st, tl):
    b = tl["9.04"]
    s = b.sent
    with st.span(b.start, b.end):
        # open hole: the plug already sits against the rock
        ox = -4.9
        card = st.rect(ox, 0.0, 2.5, 6.8, P.PANEL, 0.0)
        ttl = st.text("OPEN HOLE", ox, 3.05, 0.22, P.TEXT, 0.1, kind="bold")
        rock = [st.rect(ox, 0.0, 2.1, 5.2, P.SHALE, 0.05), st.rect(ox, 0.0, 0.8, 5.2, P.BG, 0.06),
                st.rect(ox, 0.0, 0.8, 5.2, P.MUD, 0.07, alpha=0.6)]
        oplug = st.rect(ox, 0.0, 0.8, 1.8, P.CEMENT, 0.08)
        st.fade_in([card, ttl] + rock, b.start + 0.1, 0.5)
        st.pop_in(oplug, s[0] + 0.3, 0.4)
        st.fade_in(oplug, s[0] + 0.3, 0.2)
        ar = st.arrow(ox - 1.0, 0.0, ox - 0.45, 0.0, P.TEXT, 0.04, 0.14, 0.2) + st.arrow(ox + 1.0, 0.0, ox + 0.45, 0.0, P.TEXT, 0.04, 0.14, 0.2)
        rl = st.text(wrap_to("cement meets the rock", 0.17, 2.2), ox, -2.95, 0.17, P.TEXT, 0.1)
        st.fade_in(ar + [rl], W(b, 0, "against the rock"), 0.4)
        st.fade(rock + [oplug, ttl, rl] + ar, s[1] - 0.2, s[1] + 0.4, 1.0, 0.55)
        # method list (right column, below the term-card zone)
        items = ["logged, good cement behind the casing", "section milling", "perforate, wash, cement"]
        times = [s[2], s[3], s[4]]
        method_list(st, 3.3, -0.3, items, times, s[1], dy=0.85)
        # (a) logged good cement behind the casing: Sand A, our well
        Z = Zoom(st, -1.75, 2480.0, 3060.0, 2.9, -2.9, hh=0.95, od=0.62, wl=0.08, rw=1.6)
        za = Z.base(s[1], toc=TOC["9-5/8in intermediate"], ticks=False)
        csg = tag(st, Z.cx, 3.25, "9⅝ in casing at Sand A", P.TEXT, 0.17, align="c")
        st.fade_in(csg, s[1] + 0.3, 0.4)
        ytoc = Z.Y(TOC["9-5/8in intermediate"])
        t_good = W(b, 2, "cement behind the casing is good")
        for sg in (-1, 1):
            st.ripple(Z.cx + sg * (Z.od + Z.hh) / 2, (ytoc + Z.yb) / 2, t_good, t_good + 1.6, P.TEXT, period=0.8, r0=0.1, r1=0.5)
        t_log = W(b, 2, "proven by a log")
        trk_x0, trk_x1 = 0.15, 1.15
        trk = [st.rect((trk_x0 + trk_x1) / 2, 0.0, trk_x1 - trk_x0, 5.8, P.PANEL, 0.1),
               st.text("BOND LOG", (trk_x0 + trk_x1) / 2, 3.12, 0.15, P.MUTED, 0.2, kind="bold")]
        st.fade_in(trk, t_log - 0.5, 0.4)
        pts = []
        import random
        rnd = random.Random(11)
        for k in range(59):
            y = 2.85 - k * 0.0975
            a = 0.98 + rnd.uniform(-0.03, 0.03) if y > ytoc else 0.33 + rnd.uniform(-0.05, 0.05)
            pts.append((a, y))
        curve = st.line(pts, P.TEXT, 0.03, 0.3)
        t_l0, t_l1 = t_log, t_log + 3.0
        st.draw_on(curve, t_l0, t_l1)
        tool = [st.rect(Z.cx, 2.6, 0.22, 0.6, P.STEEL_DK, 0.36)]
        wire = st.rect(Z.cx, 2.9, 0.025, 0.0001, P.MUTED, 0.35, anchor="t")
        st.fade_in(tool + [wire], t_l0 - 0.3, 0.3)
        st.move(tool, t_l0, t_l1, dy=-5.2, interp="LINEAR")
        st.scale_to(wire, t_l0, t_l1, sy=5.2, interp="LINEAR")
        st.fade_out(tool + [wire], t_l1 + 0.2, 0.4)
        fp = st.text("free pipe", 0.88, ytoc + 0.35, 0.12, P.MUTED, 0.35, align="r")
        gb = st.text("bonded", 0.5, ytoc - 0.6, 0.13, P.TEXT, 0.35, align="l", kind="bold")
        st.fade_in(fp, t_l0 + 0.6, 0.4)
        st.fade_in(gb, t_l0 + 1.4, 0.4)
        t_rec = W(b, 2, "job record")
        rec = tag(st, trk_x1 + 0.15, 1.0, "+ cement job record", P.TEXT, 0.15)
        st.fade_in(rec, t_rec, 0.4)
        t_len = W(b, 2, "enough length")
        pa, pb_ = Z.Y(PLUG["sa_p"].top), Z.Y(M.SAND_A[0])
        brk = st.line([(trk_x1 + 0.12, pa), (trk_x1 + 0.22, pa), (trk_x1 + 0.22, pb_), (trk_x1 + 0.12, pb_)], P.TEXT, 0.03, 0.35)
        st.draw_on(brk, t_len - 0.2, t_len + 0.6)
        lnt = st.text(wrap_to("enough length", 0.15, 1.0), trk_x1 + 0.35, (pa + pb_) / 2, 0.15, P.TEXT, 0.35, align="l")
        st.fade_in(lnt, t_len + 0.2, 0.4)
        # ... it can form part of the barrier: a plug on a bridge plug across the logged interval
        t_pl = W(b, 2, "form part")
        bp = Z.bridge_plug(PLUG["sa_p"].base, z=0.2)
        st.fade_in(bp, t_pl - 0.4, 0.3)
        y_top, y_bp = Z.Y(PLUG["sa_p"].top), Z.Y(PLUG["sa_p"].base)
        pl = st.rect(Z.cx, y_bp, 2 * Z.id, 0.0001, P.CEMENT, 0.15, anchor="b")
        st.fade_in(pl, t_pl, 0.1)
        st.scale_to(pl, t_pl, t_pl + 1.2, sy=y_top - y_bp)
        env = outline(st, Z.cx - Z.hh - 0.12, y_top + 0.04, Z.cx + Z.hh + 0.12, y_bp - 0.04, P.PRIMARY_B, 0.4)
        st.draw_on(env, t_pl + 0.9, t_pl + 1.7)
        envt = tag(st, Z.cx, -3.3, "plug + logged cement behind it = barrier", P.PRIMARY_B, 0.16, align="c")
        st.fade_in(envt, t_pl + 1.3, 0.4)
        # our overpressured sand is covered by the cement from chapter six
        t_sand = W(b, 2, "our overpressured")
        ysa = Z.Y(sum(M.SAND_A) / 2)
        sat = tag(st, trk_x1 + 0.15, ysa, "Sand A", P.SAND, 0.16)
        st.fade_in(sat, t_sand, 0.4)
        st.ripple(Z.cx + Z.hh + 0.3, ysa, t_sand, t_sand + 1.6, P.SAND, period=0.8, r0=0.1, r1=0.6)
        t_cov = W(b, 2, "covered by")
        tocl = st.dashed((Z.cx - Z.rw, ytoc), (trk_x1, ytoc), P.TEXT, 0.025, 0.12, 0.08, 0.32)
        toct = tag(st, trk_x1 + 0.15, ytoc, "top of cement (ch. 6)", P.TEXT, 0.15)
        st.fade_in(tocl, t_l0 + 0.5, 0.4)
        st.fade_in(toct, t_cov, 0.4)
        st.ripple(Z.cx + (Z.od + Z.hh) / 2, ytoc, t_cov, t_cov + 1.6, P.TEXT, period=0.8, r0=0.1, r1=0.5)
        a_objs = za + [csg] + trk + [curve, gb, fp] + tocl + toct + rec + [brk, lnt] + sat + bp + [pl, env] + envt
        st.fade_out(a_objs, s[3] - 0.5, 0.4)
        # (b) section milling: poor cement behind casing -> mill a window -> plug against the rock
        t_b = s[3] - 0.2
        Zb = Zoom(st, -1.75, 2560.0, 3060.0, 2.9, -2.9, hh=0.95, od=0.62, wl=0.08, rw=1.6)
        zb = Zb.base(t_b, ann=P.MUD, ticks=False, sand=False)
        poor = tag(st, Zb.cx, 3.25, "poor or no cement behind the casing", P.TEXT, 0.16, align="c")
        st.fade_in(poor, t_b + 0.2, 0.4)
        w0, w1 = 0.7, -1.2
        cut_parts = []
        t_m0, t_m1 = W(b, 3, "mill a window"), W(b, 3, "section milling", 1.0)
        for sg in (-1, 1):
            for x, wd, colr, alp, zz in ((Zb.cx + sg * (Zb.od - Zb.wl / 2), Zb.wl, P.STEEL, 1.0, 0.32),
                                         (Zb.cx + sg * (Zb.od + Zb.hh) / 2, Zb.hh - Zb.od, P.MUD, 0.75, 0.05)):
                cover = st.rect(x, (w0 + w1) / 2, wd + 0.01, w0 - w1, P.BG, zz - 0.005)
                seg = st.rect(x, w1, wd, w0 - w1, colr, zz, anchor="b", alpha=alp)
                st.fade_in([cover, seg], t_b, 0.5)
                st.scale_to(seg, t_m0, t_m1, sy=0.0001, interp="LINEAR")
                cut_parts += [cover, seg]
        pipe = st.rect(Zb.cx, 2.9, 0.26, 0.0001, P.STEEL, 0.4, anchor="t")
        mill = [st.rect(Zb.cx, w0 + 2.0, 0.5, 0.3, P.STEEL_DK, 0.41), st.rect(Zb.cx, w0 + 2.0, 1.3, 0.1, P.WARN, 0.42)]
        st.fade_in(mill + [pipe], t_b + 0.3, 0.3)
        st.scale_to(pipe, t_b + 0.3, t_m0, sy=2.9 - w0 - 0.15)
        st.move(mill, t_b + 0.3, t_m0, dy=-2.0)
        st.scale_to(pipe, t_m0, t_m1, sy=2.9 - w1 - 0.15, interp="LINEAR")
        st.move(mill, t_m0, t_m1, dy=-(w0 - w1), interp="LINEAR")
        st.flow([(Zb.cx + 0.3, w1), (Zb.cx + 0.35, 2.85)], t_m0, t_m1 + 0.3, P.STEEL, n=14, speed=2.2, r=0.035, z=0.43)
        t_pa = W(b, 3, "plug against")
        st.fade_out(mill + [pipe], t_pa - 0.6, 0.3)
        bpb = st.rect(Zb.cx, w1 - 0.52, 2 * Zb.id, 0.12, P.STEEL_DK, 0.2)
        st.fade_in(bpb, t_pa - 0.4, 0.3)
        plw = st.rect(Zb.cx, w1, 2 * Zb.hh, 0.0001, P.CEMENT, 0.15, anchor="b")
        plb = st.rect(Zb.cx, w1 - 0.46, 2 * Zb.id, 0.0001, P.CEMENT, 0.15, anchor="b")
        plt = st.rect(Zb.cx, w0, 2 * Zb.id, 0.0001, P.CEMENT, 0.15, anchor="b")
        st.fade_in([plw, plb, plt], t_pa, 0.1)
        st.scale_to(plb, t_pa, t_pa + 0.4, sy=0.46)
        st.scale_to(plw, t_pa + 0.4, t_pa + 1.4, sy=w0 - w1)
        st.scale_to(plt, t_pa + 1.4, t_pa + 1.8, sy=0.45)
        bt = tag(st, Zb.cx, -3.3, "window milled: plug against the rock", P.TEXT, 0.16, align="c")
        st.fade_in(bt, t_pa + 0.6, 0.4)
        b_objs = zb + [poor[0], poor[1]] + cut_parts + [bpb, plw, plb, plt] + bt
        st.fade_out(b_objs, s[4] - 0.5, 0.4)
        # (c) perforate, wash, cement
        t_c = s[4] - 0.2
        Zc = Zoom(st, -1.75, 2560.0, 3060.0, 2.9, -2.9, hh=0.95, od=0.62, wl=0.08, rw=1.6)
        zc = Zc.base(t_c, ann=P.MUD, ticks=False, sand=False)
        poor2 = tag(st, Zc.cx, 3.25, "poor or no cement behind the casing", P.TEXT, 0.16, align="c")
        st.fade_in(poor2, t_c + 0.2, 0.4)
        t_perf = W(b, 4, "perforate the casing")
        gun = st.rect(Zc.cx, (w0 + w1) / 2, 0.3, w0 - w1 + 0.2, P.STEEL_DK, 0.4)
        st.fade_in(gun, t_c + 0.3, 0.3)
        holes, shots = [], []
        for k in range(5):
            yy = w0 - 0.15 - k * (w0 - w1 - 0.3) / 4
            tk = t_perf + 0.12 * k
            for sg in (-1, 1):
                h = st.rect(Zc.cx + sg * (Zc.od - Zc.wl / 2), yy, Zc.wl + 0.02, 0.1, P.BG, 0.33)
                st.fade_in(h, tk, 0.1)
                holes.append(h)
                sh = st.arrow(Zc.cx + sg * 0.15, yy, Zc.cx + sg * (Zc.hh + 0.25), yy, P.WARN, 0.05, 0.14, 0.45)
                st.fade_in(sh, tk, 0.08)
                st.fade_out(sh, tk + 0.35, 0.25)
                shots += sh
        st.fade_out(gun, W(b, 4, "wash") - 0.3, 0.3)
        t_wash = W(b, 4, "wash the annulus")
        washers = []
        for sg in (-1, 1):
            o = st.rect(Zc.cx + sg * (Zc.od + Zc.hh) / 2, (w0 + w1) / 2, Zc.hh - Zc.od, w0 - w1, P.MUD, 0.08, alpha=0.75)
            st.fade_in(o, t_c, 0.5)
            st.recolor(o, t_wash + 0.2, t_wash + 1.6, P.SPACER)
            washers.append(o)
        wt = [st.rect(Zc.cx, w0 + 0.2, 0.3, 0.4, P.STEEL_DK, 0.4)]
        st.fade_in(wt, t_wash - 0.2, 0.3)
        st.move(wt, t_wash, t_wash + 1.6, dy=-(w0 - w1), interp="LINEAR")
        for sg in (-1, 1):       # jets out through the lower holes, up the annulus, back in through the upper holes, up the bore
            xa = Zc.cx + sg * (Zc.od + Zc.hh) / 2
            st.flow([(Zc.cx + sg * 0.15, w1 + 0.25), (xa, w1 + 0.25), (xa, w0 - 0.2), (Zc.cx + sg * 0.3, w0 - 0.2), (Zc.cx + sg * 0.3, 2.85)],
                    t_wash, t_wash + 2.2, P.SPACER, n=16, speed=1.8, r=0.035, z=0.45)
        t_cem = W(b, 4, "pump cement")
        st.fade_out(wt, t_cem - 0.4, 0.3)
        bpc = st.rect(Zc.cx, w1 - 0.52, 2 * Zc.id, 0.12, P.STEEL_DK, 0.2)
        st.fade_in(bpc, t_cem - 0.4, 0.3)
        cem = []
        for sg in (-1, 1):
            o = st.rect(Zc.cx + sg * (Zc.od + Zc.hh) / 2, w1, Zc.hh - Zc.od, 0.0001, P.CEMENT, 0.09, anchor="b")
            cem.append(o)
            st.scale_to(o, t_cem, t_cem + 1.4, sy=w0 - w1)
        cb = st.rect(Zc.cx, w1 - 0.46, 2 * Zc.id, 0.0001, P.CEMENT, 0.15, anchor="b")
        st.scale_to(cb, t_cem, t_cem + 1.6, sy=w0 - w1 + 0.46 + 0.3)
        st.fade_in(cem + [cb], t_cem, 0.1)
        ct = tag(st, Zc.cx, -3.3, "annulus and bore cemented across the interval", P.TEXT, 0.16, align="c")
        st.fade_in(ct, t_cem + 0.8, 0.4)


# ====================================================================================== 9.05 THE PLUG PLACEMENT ANIMATION
PCX = -2.75


def beat_place(st, tl):
    b = tl["9.05"]
    s = b.sent
    with st.span(b.start, b.end):
        Z = Zoom(st, PCX, 2780.0, 3011.0, 3.5, -3.3)
        zo = Z.base(b.start + 0.05)
        pz = PLUG["sa_p"]
        y_ct, y_bp = Z.Y(pz.top), Z.Y(pz.base)           # plug top (= balanced cement top) and bridge-plug top
        y_st = Z.Y(pz.top - 12.0)                         # spacer top
        y_pb = Z.Y(pz.base - 10.0)                        # pipe end while pumping, just above the bridge plug
        y_out = Z.Y(pz.top - 30.0)                        # pipe end after pulling out, just above the spacer
        # labels (middle column)
        lx = -0.55

        def lab(y, txt, tx, ty, t0, t1=None, colr=P.TEXT):
            o = tag(st, lx, y, txt, colr, 0.16) + leader(st, lx - 0.05, y, tx, ty)
            st.fade_in(o, t0, 0.35)
            if t1:
                st.fade_out(o, t1, 0.35)
            return o
        lab(3.1, "9⅝ in casing", PCX + Z.od - 0.05, 3.1, b.start + 0.4)
        lab(2.5, "annulus cement (logged)", PCX + (Z.od + Z.hh) / 2, 2.5, b.start + 0.6)
        lab(-2.85, "Sand A, 2,980–3,000 m", PCX + Z.hh + 0.5, Z.Y(2990), b.start + 0.8, colr=P.SAND)
        # 1. the bridge plug runs in on wireline and sets
        t_mb = W(b, 0, "mechanical base")
        t_set = W(b, 0, "seals the casing")
        bp = Z.bridge_plug(pz.base, t_run=(t_mb - 0.6, t_set - 0.8), t_set=t_set - 0.6, z=0.35, run_from=2.6)
        st.fade_in(bp, t_mb - 0.6, 0.3)
        wire = st.rect(PCX, 3.5, 0.025, 3.5 - 2.6 - 0.15, P.MUTED, 0.34, anchor="t")
        st.fade_in(wire, t_mb - 0.6, 0.3)
        st.scale_to(wire, t_mb - 0.6, t_set - 0.8, sy=3.5 - Z.Y(pz.base + 6) - 0.2)
        st.scale_to(wire, t_set + 0.2, t_set + 1.4, sy=0.0001)
        st.ripple(PCX, Z.Y(pz.base + 6), t_set, t_set + 1.2, P.TEXT, period=0.6, r0=0.3, r1=1.0)
        bpl = lab(-1.75, "bridge plug: steel slips, rubber seal", PCX + 0.3, Z.Y(pz.base + 6), W(b, 0, "steel-and-rubber"), s[3])
        hold = lab(-1.15, "holds the cement up", PCX, y_bp + 0.05, W(b, 0, "holds the cement"), s[2])
        # right column: the steps
        rx = 3.4
        steps = [("bridge plug: the mechanical base", t_mb), ("pump spacer, cement, spacer", s[2]),
                 ("balance: same level in and out", W(b, 2, "weigh the same")), ("pull the pipe out slowly", s[3]),
                 ("circulate the excess out", W(b, 3, "excess"))]
        for i, (txt, t) in enumerate(steps):
            yy = 1.2 - i * 0.48
            n = st.text(str(i + 1), rx + 0.12, yy, 0.22, P.WARN, 0.5, kind="bold")
            tx = st.text(txt, rx + 0.42, yy, 0.18, P.TEXT, 0.5, align="l", kind="bold")
            st.fade_in([n, tx], t, 0.4)
            if i + 1 < len(steps):
                st.recolor(tx, steps[i + 1][1], steps[i + 1][1] + 0.4, P.MUTED)
        # 2. open hole: a viscous pill is the base (inset)
        t_oh = s[1]
        ix, iy = 5.65, -2.15
        inset = [st.rect(ix, iy, 3.8, 2.45, P.PANEL, 0.2), st.text("OPEN HOLE", ix - 1.7, iy + 0.98, 0.15, P.MUTED, 0.3, align="l", kind="bold"),
                 st.rect(ix - 0.6, iy - 0.1, 0.9, 1.9, P.SHALE, 0.25), st.rect(ix + 0.6, iy - 0.1, 0.9, 1.9, P.SHALE, 0.25),
                 st.rect(ix, iy - 0.1, 0.3, 1.9, P.MUD, 0.26, alpha=0.6)]
        visc = st.rect(ix, iy - 0.75, 0.3, 0.4, P.MUD, 0.27)
        hatch = [st.line([(ix - 0.15, iy - 0.95 + 0.1 * k), (ix + 0.15, iy - 0.75 + 0.1 * k)], RUBBER, 0.02, 0.28) for k in range(3)]
        ocem = st.rect(ix, iy - 0.55, 0.3, 0.0001, P.CEMENT, 0.27, anchor="b")
        st.fade_in(inset, t_oh - 0.3, 0.4)
        st.fade_in([visc] + hatch, W(b, 1, "viscous pill"), 0.4)
        st.fade_in(ocem, W(b, 1, "does that job") - 0.3, 0.1)
        st.scale_to(ocem, W(b, 1, "does that job") - 0.3, W(b, 1, "does that job") + 0.8, sy=0.95)
        il = [st.text("viscous pill", ix + 1.12, iy - 0.75, 0.15, P.MUD, 0.3, align="l", kind="bold"),
              st.text("cement", ix + 1.12, iy - 0.05, 0.15, P.TEXT, 0.3, align="l", kind="bold")]
        st.fade_in(il[0], W(b, 1, "viscous pill") + 0.2, 0.3)
        st.fade_in(il[1], W(b, 1, "does that job"), 0.3)
        st.fade_out(inset + [visc, ocem] + hatch + il, W(b, 2, "U-tube") - 0.9, 0.4)
        # 3. open-ended drill pipe runs in to just above the bridge plug (during the inset)
        t_run0, t_run1 = s[1] + 0.2, s[2] - 0.2
        PO, PW = 0.27, 0.06
        pwalls = [st.rect(PCX + sg * (PO - PW / 2), 3.5, PW, 0.0001, P.STEEL, 0.38, anchor="t") for sg in (-1, 1)]
        st.fade_in(pwalls, t_run0, 0.2)
        st.scale_to(pwalls, t_run0, t_run1, sy=3.5 - y_pb)
        lab(1.9, "open-ended drill pipe", PCX + PO, 1.9, t_run0 + 0.5, s[3] - 0.3)
        # 4. pump spacer / cement / spacer; columns balance (procedural, volume-correct U-tube)
        A_p, A_a, A_b = 2 * (PO - PW), 2 * (Z.id - PO), 2 * Z.id
        Lp, g = 3.5 - y_pb, y_pb - y_bp
        h_ci, h_sp = y_ct - y_pb, y_st - y_ct
        Lc = (A_p * h_ci + A_b * g + A_a * h_ci) / A_p
        Ls1 = A_a * h_sp / A_p
        s3f = Lp - h_ci
        s2f, s4f = s3f + Lc, s3f - h_sp
        s1f = s2f + Ls1
        t_p0, t_p1 = s[2] + 0.2, W(b, 2, "weigh the same")
        t_u0, t_u1 = s[3] + 0.1, W(b, 3, "out of the cement", 1.0) + 0.3       # pull out
        t_r0, t_r1 = W(b, 3, "excess") - 0.3, s[4] - 0.1                        # reverse-circulate the excess

        def fill(c, look, x0, x1, ya, yb, color, a=1.0):
            if yb - ya < 1e-4 or x1 - x0 < 1e-4 or a <= 0.01:
                return
            rgb = hex_rgb(color)
            r = skia.Rect.MakeLTRB(x0, ya, x1, yb)
            gsh = skia.GradientShader.MakeLinear([skia.Point(x0, 0), skia.Point(x1, 0)],
                                                 [col(darken(rgb, 0.16), a), col(lighten(rgb, 0.10), a), col(rgb, a), col(darken(rgb, 0.16), a)],
                                                 [0.0, 0.35, 0.6, 1.0])
            c.drawRect(r, skia.Paint(Shader=gsh, AntiAlias=True))
            if color == P.CEMENT:
                c.drawRect(r, look._texture_paint("cement", a, 1.2, 0.0, 0.0))

        def out_y(V):
            if V <= A_b * g:
                return y_bp + V / A_b
            return y_pb + (V - A_b * g) / A_a

        def draw_cols(c, t, look):
            if t < t_p0:
                return
            if t < t_p1 + 1e-3:
                f = ease_inout(min(1.0, (t - t_p0) / (t_p1 - t_p0)))
                sh = -(1.0 - f) * s1f
                segs = [(s2f + sh, s1f + sh, P.SPACER), (s3f + sh, s2f + sh, P.CEMENT), (s4f + sh, s3f + sh, P.SPACER)]
                for sa, sb, colr in segs:
                    ia, ib = max(sa, 0.0), min(sb, Lp)
                    if ib > ia:
                        fill(c, look, PCX - (PO - PW), PCX + (PO - PW), 3.5 - ib, 3.5 - ia, colr)
                    if sb > Lp:
                        va, vb = max(sa - Lp, 0.0) * A_p, (sb - Lp) * A_p
                        ya, yb = out_y(va), out_y(vb)
                        ga, gb = min(ya, y_pb), min(yb, y_pb)
                        fill(c, look, PCX - Z.id, PCX + Z.id, ga, gb, colr)
                        aa, ab = max(ya, y_pb), max(yb, y_pb)
                        for sg in (-1, 1):
                            x0, x1 = sorted((PCX + sg * PO, PCX + sg * Z.id))
                            fill(c, look, x0, x1, aa, ab, colr)
                return
            # balanced, then pulled out and circulated: full-bore columns (the pipe slides through them)
            fa = 1.0 if t < t_r0 else max(0.0, 1.0 - (t - t_r0) / (t_r1 - t_r0))
            fill(c, look, PCX - Z.id, PCX + Z.id, y_bp, y_ct, P.CEMENT)
            fill(c, look, PCX - Z.id, PCX + Z.id, y_ct, y_st, P.SPACER, fa)
        st.procedural(t_p0, b.end, 0.2, draw_cols)
        st.flow([(PCX, 3.45), (PCX, y_pb + 0.1)], t_p0, t_p1 - 0.3, P.SPACER, n=10, speed=2.2, r=0.03, z=0.39)
        sp = lab(1.3, "spacer", PCX + PO + 0.3, (y_ct + y_st) / 2, t_p1 - 0.4, s[3])
        cm = lab(-0.45, "cement", PCX + PO + 0.3, -0.45, t_p1 - 0.2, s[3])
        t_eq = W(b, 2, "inside and outside")
        eq = st.dashed((PCX - Z.id, y_ct), (PCX + Z.id + 0.2, y_ct), P.WARN, 0.03, 0.12, 0.07, 0.45)
        st.fade_in(eq, t_eq - 0.2, 0.3)
        st.fade_out(eq, s[3], 0.3)
        eql = lab(0.55, "same level inside and outside", PCX + Z.id + 0.2, y_ct, t_eq, s[3], colr=P.WARN)
        # mini U-tube (we met it in ch. 5)
        t_u = W(b, 2, "U-tube")
        ux, uy = 5.65, -2.35
        ut = [st.rect(ux, -2.15, 3.8, 2.45, P.PANEL, 0.2), st.text("U-TUBE (ch. 6)", ux - 1.7, -1.17, 0.15, P.MUTED, 0.3, align="l", kind="bold")]
        ux0 = ux - 0.6
        UW, UH = 0.22, 1.1                                   # U-tube: two legs joined at the bottom, cement grey at equal levels
        for sg in (-1, 1):
            ut.append(st.rect(ux0 + sg * 0.55, uy - 0.05, UW, UH, P.CEMENT, 0.3))
            ut.append(st.rect(ux0 + sg * 0.55, uy + 0.5 + 0.15, UW, 0.3, P.SPACER, 0.3))
        ut.append(st.rect(ux0, uy - 0.6 - UW / 2 + 0.11, 1.1 + UW, UW, P.CEMENT, 0.3))
        ut.append(st.line([(ux0 - 0.55 - UW / 2 - 0.03, uy + 0.95), (ux0 - 0.55 - UW / 2 - 0.03, uy - 0.75), (ux0 + 0.55 + UW / 2 + 0.03, uy - 0.75),
                           (ux0 + 0.55 + UW / 2 + 0.03, uy + 0.95)], P.TEXT, 0.03, 0.32))
        ut.append(st.line([(ux0 - 0.55 + UW / 2 + 0.03, uy + 0.95), (ux0 - 0.55 + UW / 2 + 0.03, uy - 0.47), (ux0 + 0.55 - UW / 2 - 0.03, uy - 0.47),
                           (ux0 + 0.55 - UW / 2 - 0.03, uy + 0.95)], P.TEXT, 0.03, 0.32))
        ut += st.dashed((ux0 - 0.85, uy + 0.5), (ux0 + 0.85, uy + 0.5), P.WARN, 0.025, 0.1, 0.06, 0.33)
        ut.append(st.text(wrap_to("equal weight both sides: nothing moves", 0.15, 1.6), ux0 + 1.8, uy + 0.0, 0.15, P.TEXT, 0.33))
        st.fade_in(ut, t_u - 0.4, 0.4)
        st.fade_out(ut, s[3] + 0.4, 0.4)
        # 5. pull out slowly; 6. reverse-circulate the excess
        st.scale_to(pwalls, t_u0, t_u1, sy=3.5 - y_out)
        for sg in (-1, 1):
            xa = PCX + sg * (PO + Z.id) / 2
            st.flow([(xa, 3.45), (xa, y_out - 0.1), (PCX, y_out - 0.15), (PCX, 3.45)], t_r0, t_r1, P.MUD, n=12, speed=1.6, r=0.035, z=0.39)
        rc = lab(1.9, "reverse circulation: excess out up the pipe", PCX + 0.1, 2.4, t_r0, s[4] + 0.6, colr=P.MUD)
        # 7. the plug: ~100 m, drawing value
        t_dim = W(b, 4, "hundred metres")
        dx = PCX + Z.rw + 0.15
        dim = st.line([(dx - 0.08, y_ct), (dx, y_ct), (dx, y_bp), (dx - 0.08, y_bp)], P.TEXT, 0.03, 0.45)
        st.draw_on(dim, s[4], s[4] + 0.6)
        dt = [st.text("≈ 100 m", dx + 0.15, (y_ct + y_bp) / 2 + 0.15, 0.24, P.TEXT, 0.46, align="l", kind="bold"),
              st.text("drawing only", dx + 0.15, (y_ct + y_bp) / 2 - 0.2, 0.15, P.MUTED, 0.46, align="l")]
        st.fade_in(dt, t_dim - 0.3, 0.4)


# ====================================================================================== 9.06 verification
def beat_verify(st, tl):
    b = tl["9.06"]
    s = b.sent
    with st.span(b.start, b.end):
        Z = Zoom(st, PCX, 2780.0, 3011.0, 3.5, -3.3)
        zo = Z.base(b.start + 0.05)
        pz = PLUG["sa_p"]
        y_ct, y_bp = Z.Y(pz.top), Z.Y(pz.base)
        rx = 3.4
        steps = [("LOG the cement behind the casing", s[1]), ("TAG: set down weight", W(b, 2, "tag it")),
                 ("PRESSURE TEST from above", W(b, 3, "pressure test")), ("INFLOW TEST from below", W(b, 3, "inflow test")),
                 ("VERIFIED", W(b, 5, "verified"))]
        for i, (txt, t) in enumerate(steps):
            yy = 1.2 - i * 0.48
            n = st.text(str(i + 1) if i < 4 else "✓", rx + 0.12, yy, 0.22, P.WARN if i < 4 else P.SAFE, 0.5, kind="bold")
            tx = st.text(txt, rx + 0.42, yy, 0.18, P.TEXT if i < 4 else P.SAFE, 0.5, align="l", kind="bold")
            st.fade_in([n, tx], t, 0.4)
            if i + 1 < len(steps) - 1:
                st.recolor(tx, steps[i + 1][1], steps[i + 1][1] + 0.4, P.MUTED)
        kick = st.text("PROVE IT", -0.55, 3.2, 0.34, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(kick, s[0], 0.4)
        st.fade_out(kick, s[1] + 0.5, 0.3)
        # 1. log before the plug goes in
        t_l0, t_l1 = s[1] + 0.2, s[2] - 0.5
        tool = [st.rect(PCX, 3.2, 0.3, 0.6, P.STEEL_DK, 0.36)]
        wire = st.rect(PCX, 3.5, 0.025, 0.0001, P.MUTED, 0.35, anchor="t")
        st.fade_in(tool + [wire], t_l0 - 0.3, 0.3)
        st.move(tool, t_l0, t_l1, dy=-6.0, interp="LINEAR")
        st.scale_to(wire, t_l0, t_l1, sy=6.0, interp="LINEAR")
        st.fade_out(tool + [wire], t_l1, 0.3)
        tx0, tx1 = -0.5, 0.7
        trk = [st.rect((tx0 + tx1) / 2, 0.1, tx1 - tx0, 6.8, P.PANEL, 0.1), st.text("BOND LOG", (tx0 + tx1) / 2, -3.45 + 0.05, 0.14, P.MUTED, 0.2, kind="bold")]
        import random
        rnd = random.Random(5)
        pts = [(tx0 + 0.25 + rnd.uniform(-0.05, 0.05), 3.4 - k * 0.1) for k in range(66)]
        curve = st.line(pts, P.TEXT, 0.03, 0.3)
        st.fade_in(trk, t_l0 - 0.3, 0.3)
        st.draw_on(curve, t_l0 + 0.05, t_l1)
        lb = tag(st, tx1 + 0.15, 2.4, "logged before the plug: bond good", P.TEXT, 0.16)
        st.fade_in(lb, t_l0 + 1.0, 0.4)
        st.fade_out(trk + [curve] + lb, s[2] + 0.2, 0.4)
        # 2. after it sets: the plug; tag it
        bp = Z.bridge_plug(pz.base, z=0.35)
        plug = st.rect(PCX, (y_ct + y_bp) / 2, 2 * Z.id, y_ct - y_bp, P.CEMENT, 0.3)
        st.fade_in(bp + [plug], s[2] - 0.2, 0.5)
        sets = tag(st, -0.55, -0.6, "plug set and hardened", P.TEXT, 0.16)
        st.fade_in(sets, s[2] + 0.1, 0.4)
        st.fade_out(sets, W(b, 2, "rests on") , 0.3)
        PO, PW = 0.27, 0.06
        t_d0, t_d1 = W(b, 2, "lower the pipe") - 0.2, W(b, 2, "rests on the plug", 1.0)
        pw = [st.rect(PCX + sg * (PO - PW / 2), 3.5, PW, 0.0001, P.STEEL, 0.38, anchor="t") for sg in (-1, 1)]
        pin = st.rect(PCX, 3.5, 2 * (PO - PW), 0.0001, P.MUD, 0.37, anchor="t", alpha=0.7)
        st.fade_in(pw + [pin], t_d0, 0.2)
        st.scale_to(pw + [pin], t_d0, t_d1, sy=3.5 - y_ct)
        st.ripple(PCX, y_ct, t_d1, t_d1 + 1.2, P.TEXT, period=0.6, r0=0.2, r1=0.9)
        t_wt = W(b, 2, "load it with weight")
        wa = st.arrow(PCX + 0.75, 3.3, PCX + 0.75, 2.4, P.WARN, 0.08, 0.25, 0.45) + st.arrow(PCX - 0.75, 3.3, PCX - 0.75, 2.4, P.WARN, 0.08, 0.25, 0.45)
        st.fade_in(wa, t_wt, 0.3)
        tg = tag(st, -0.55, y_ct + 0.05, "tagged on top of the plug", P.TEXT, 0.16) + leader(st, -0.6, y_ct + 0.05, PCX + 0.3, y_ct)
        st.fade_in(tg, t_d1, 0.4)
        # weight indicator (instrument slot)
        ix, iy = 5.65, -2.15
        inst = [st.rect(ix, iy, 3.8, 2.45, P.PANEL, 0.2), st.text("WEIGHT ON THE PLUG", ix, iy + 0.98, 0.15, P.MUTED, 0.3, kind="bold")]
        dial = [st.circle(ix - 0.8, iy - 0.25, 0.75, P.PANEL2, 0.3, role="disc"), st.ring(ix - 0.8, iy - 0.25, 0.75, 0.05, P.MUTED, 0.31)]
        for k in range(7):
            a = math.radians(210 - k * 40)
            dial.append(st.rect(ix - 0.8 + 0.62 * math.cos(a), iy - 0.25 + 0.62 * math.sin(a), 0.12, 0.025, P.MUTED, 0.31, rot=math.degrees(a)))
        nd = st.rect(ix - 0.8, iy - 0.25, 0.6, 0.05, P.WARN, 0.33, anchor="l", rot=210)
        hub = st.circle(ix - 0.8, iy - 0.25, 0.07, P.TEXT, 0.34, role="disc")
        st.fade_in(inst + dial + [nd, hub], t_wt - 0.6, 0.4)
        st.rotate(nd, t_wt, t_wt + 1.6, 110)
        wtx = st.text(wrap_to("pipe stops on the plug and stays put", 0.15, 1.6), ix + 0.95, iy - 0.25, 0.15, P.TEXT, 0.33)
        st.fade_in(wtx, t_wt + 1.0, 0.4)
        inst_a = inst + dial + [nd, hub, wtx]
        st.fade_out(inst_a + wa + tg, s[3] - 0.3, 0.4)
        # 3. pressure test from above (pipe pulled clear), 4. inflow test from below
        st.scale_to(pw + [pin], s[3] - 0.4, s[3] + 0.6, sy=3.5 - (y_ct + 1.9))
        t_pt = W(b, 3, "from above")
        pa = []
        for x in (PCX - 0.55, PCX + 0.55):
            pa += st.arrow(x, y_ct + 1.2, x, y_ct + 0.12, P.WARN, 0.07, 0.22, 0.45)
        st.fade_in(pa, t_pt - 0.5, 0.3)
        st.ripple(PCX, y_ct + 0.05, t_pt - 0.3, t_pt + 2.5, P.WARN, period=0.9, r0=0.2, r1=1.0)
        ch = [st.rect(ix, iy, 3.8, 2.45, P.PANEL, 0.2), st.text("PRESSURE TEST", ix, iy + 0.98, 0.15, P.MUTED, 0.3, kind="bold")]
        x0, x1, y0, y1 = ix - 1.55, ix + 1.6, iy - 0.95, iy + 0.6
        ax = [st.rect((x0 + x1) / 2, y0, x1 - x0, 0.02, P.MUTED, 0.31), st.rect(x0, (y0 + y1) / 2, 0.02, y1 - y0, P.MUTED, 0.31),
              st.text("time", x1, y0 - 0.17, 0.13, P.MUTED, 0.31, align="r"), st.text("pressure", x0 + 0.08, y1 + 0.02, 0.13, P.MUTED, 0.31, align="l")]
        tr = st.line([(x0, y0 + 0.02), (x0 + 0.9, y1 - 0.25), (x1 - 0.1, y1 - 0.25)], P.WARN, 0.04, 0.33)
        st.fade_in(ch + ax, s[3] - 0.3, 0.4)
        st.draw_on(tr, t_pt - 0.2, t_pt + 3.0)
        hf = st.text("holds flat", (x0 + 0.9 + x1) / 2, y1 - 0.05, 0.16, P.TEXT, 0.34, kind="bold")
        st.fade_in(hf, t_pt + 2.6, 0.4)
        t_in = W(b, 3, "inflow test")
        ia = st.arrow(PCX, y_bp - 1.0, PCX, y_bp - 0.42, P.PORE, 0.07, 0.22, 0.45)
        st.fade_in(ia, t_in - 0.2, 0.3)
        il = tag(st, -0.55, y_bp - 0.75, "inflow test: pressure from below", P.PORE, 0.16) + leader(st, -0.6, y_bp - 0.75, PCX + 0.1, y_bp - 0.75)
        st.fade_in(il, t_in, 0.4)
        # 5. open hole: proven by the tag (the instrument slot shows an open-hole plug being tagged)
        t_oh = s[4]
        st.fade_out(ch + ax + [tr, hf], t_oh - 0.3, 0.4)
        oh = [st.rect(ix, iy, 3.8, 2.45, P.PANEL, 0.2), st.text("OPEN-HOLE PLUG", ix - 1.7, iy + 0.98, 0.15, P.MUTED, 0.3, align="l", kind="bold")]
        ox = ix - 0.8
        oh += [st.rect(ox - 0.5, iy - 0.15, 0.65, 1.85, P.SHALE, 0.25), st.rect(ox + 0.5, iy - 0.15, 0.65, 1.85, P.SHALE, 0.25),
               st.rect(ox, iy - 0.15, 0.36, 1.85, P.MUD, 0.26, alpha=0.6), st.rect(ox, iy - 0.6, 0.36, 0.95, P.CEMENT, 0.27)]
        st.fade_in(oh, t_oh - 0.2, 0.4)
        opw = [st.rect(ox + sg * 0.11, iy + 0.8, 0.05, 0.0001, P.STEEL, 0.3, anchor="t") for sg in (-1, 1)]
        st.fade_in(opw, t_oh + 0.2, 0.2)
        st.scale_to(opw, t_oh + 0.2, t_oh + 1.2, sy=iy + 0.8 - (iy - 0.13))
        st.ripple(ox, iy - 0.13, t_oh + 1.2, t_oh + 2.2, P.TEXT, period=0.5, r0=0.1, r1=0.5)
        oht = st.text(wrap_to("proven by the tag", 0.18, 2.1), ix + 0.85, iy - 0.15, 0.18, P.TEXT, 0.3)
        st.fade_in(oht, t_oh + 1.0, 0.4)
        # 6. verified: the green outline lands on the plug
        t_v = W(b, 5, "verified")
        vo = outline(st, PCX - Z.id - 0.06, y_ct + 0.05, PCX + Z.id + 0.06, y_bp - 0.05, P.SAFE, 0.45, 0.045)
        st.draw_on(vo, t_v - 0.6, t_v + 0.3)
        vp = pill(st, PCX, y_ct + 0.45, "✓ VERIFIED", P.SAFE, "#06201c", 0.2, 0.5)
        st.fade_in(vp, t_v, 0.3)
        st.ripple(PCX, (y_ct + y_bp) / 2, t_v, t_v + 1.6, P.SAFE, period=0.8, r0=0.6, r1=1.8)
        st.fade_out(pa + il + [ia], s[5] - 0.3, 0.3)


# ====================================================================================== 9.07 cut and pull, seabed survey, temporary abandonment
def beat_cut(st, tl):
    b = tl["9.07"]
    s = b.sent
    with st.span(b.start, b.end):
        cx, sb = -2.2, 0.9
        ycut = sb - 1.25                                     # zoom: ~4 m per unit
        K = 0.08
        strs = [(n, od * K / 2, hole * K / 2) for n, od, hole, _ in [(x.name, x.od_in, x.hole_in, x.shoe) for x in M.programme()]]
        X0, X1 = -6.1, 7.6
        sea = st.rect((X0 + X1) / 2, (sb + 3.85) / 2, X1 - X0, 3.85 - sb, P.SEA, 0.0)
        rock = st.rect((X0 + X1) / 2, (sb - 3.45) / 2, X1 - X0, sb + 3.45, P.SEABED, 0.0)
        line = st.rect((X0 + X1) / 2, sb, X1 - X0, 0.05, "#8b7a5e", 0.02)
        mound = st.poly([(cx - 3.2, sb), (cx - 1.6, sb + 0.16), (cx + 1.6, sb + 0.18), (cx + 3.4, sb)], "#8b7a5e", 0.03)
        st.fade_in([sea, rock, line, mound], b.start, 0.5)
        lower, upper = [], []
        hole = strs[0][2]
        lower.append(st.rect(cx, (ycut - 3.45) / 2, 2 * hole, ycut + 3.45, P.BG, 0.05))
        upper.append(st.rect(cx, (sb + ycut) / 2, 2 * hole, sb - ycut, P.BG, 0.05))
        # annuli: conductor + 20 in cemented to the seabed; the inner annuli are cemented across the surface plug (rock to rock)
        ann_col = [P.CEMENT, P.CEMENT, P.CEMENT, P.CEMENT]
        bounds = [hole] + [od - 0.07 for _, od, _ in strs[:-1]]
        for i, (n, od, hl) in enumerate(strs):
            outer = bounds[i]
            for sg in (-1, 1):
                x0, x1 = sorted((cx + sg * od, cx + sg * outer))
                a = 1.0 if ann_col[i] == P.CEMENT else 0.8
                lower.append(st.rect((x0 + x1) / 2, (ycut - 3.45) / 2, x1 - x0, ycut + 3.45, ann_col[i], 0.06 + 0.01 * i, alpha=a))
                upper.append(st.rect((x0 + x1) / 2, (sb + ycut) / 2, x1 - x0, sb - ycut, ann_col[i], 0.06 + 0.01 * i, alpha=a))
        idh = strs[-1][1] - 0.07
        y_pt = ycut - 0.08
        lower.append(st.rect(cx, (y_pt - 3.45) / 2, 2 * idh, y_pt + 3.45, P.CEMENT, 0.1))
        lower.append(st.rect(cx, (ycut + y_pt) / 2, 2 * idh, ycut - y_pt, MUD_DIM, 0.1, alpha=0.8))
        upper.append(st.rect(cx, (sb + ycut) / 2, 2 * idh, sb - ycut, MUD_DIM, 0.1, alpha=0.8))
        for i, (n, od, hl) in enumerate(strs):
            for sg in (-1, 1):
                x = cx + sg * (od - 0.035)
                lower.append(st.rect(x, (ycut - 3.45) / 2, 0.07, ycut + 3.45, P.STEEL, 0.15 + 0.01 * i))
                upper.append(st.rect(x, (sb + 0.25 + ycut) / 2, 0.07, sb + 0.25 - ycut, P.STEEL, 0.15 + 0.01 * i))
        wh = [st.rect(cx, sb + 0.85, 1.7, 1.2, P.STEEL_DK, 0.3), st.rect(cx, sb + 1.55, 1.0, 0.25, P.STEEL, 0.31),
              st.rect(cx, sb + 0.12, 4.0, 0.16, P.STEEL_DK, 0.29)] + [st.rect(cx + sg * 1.8, sb + 0.6, 0.08, 0.95, P.STEEL, 0.29) for sg in (-1, 1)]
        upper += wh
        st.fade_in(lower + upper, b.start + 0.1, 0.5)
        whl = tag(st, cx + 2.2, sb + 1.3, "wellhead + guide base", P.TEXT, 0.17)
        st.fade_in(whl, b.start + 0.6, 0.4)
        stays = tag(st, cx + 2.0, -1.6, "casing, cement and plugs stay in the ground", P.TEXT, 0.17)
        spl = tag(st, cx + 2.0, -2.5, "surface plug", P.TEXT, 0.17) + leader(st, cx + 1.95, -2.5, cx + 0.2, -2.5)
        st.fade_in(spl, b.start + 0.8, 0.4)
        # the cut: a cutter inside the casing cuts every string below the seabed
        t_cut = W(b, 1, "cut the casing")
        pipe = st.rect(cx, 3.85, 0.22, 0.0001, P.STEEL, 0.5, anchor="t")
        cutter = [st.rect(cx, ycut + 2.0, 0.34, 0.35, P.STEEL_DK, 0.51)]
        blades = [st.rect(cx, ycut + 2.0, 0.34, 0.08, P.WARN, 0.52)]
        st.fade_in([pipe] + cutter + blades, t_cut - 1.0, 0.3)
        st.scale_to(pipe, t_cut - 1.0, t_cut - 0.2, sy=3.85 - ycut - 0.15)
        st.move(cutter + blades, t_cut - 1.0, t_cut - 0.2, dy=-2.0)
        st.scale_to(blades, t_cut - 0.1, t_cut + 0.4, sx=2 * idh)
        t_cond = W(b, 1, "conductor", 1.0)
        cl = st.line([(cx - 0.05, ycut), (cx - hole - 0.1, ycut)], P.WARN, 0.04, 0.55), st.line([(cx + 0.05, ycut), (cx + hole + 0.1, ycut)], P.WARN, 0.04, 0.55)
        for o in cl:
            st.draw_on(o, t_cut, t_cond)
        st.ripple(cx, ycut, t_cut, t_cond, P.WARN, period=0.5, r0=0.2, r1=1.3)
        ctag = tag(st, cx + 2.0, ycut, "cut below the seabed", P.WARN, 0.17)
        st.fade_in(ctag, t_cut + 0.3, 0.4)
        # lift out the wellhead with the cut stubs
        t_lift = W(b, 1, "lift out")
        pull = upper + cutter + blades + list(cl)
        st.move(pull, t_lift, t_lift + 2.0, dy=1.25)                       # lifted (and out of the frame, below the header)
        st.scale_to(pipe, t_lift, t_lift + 2.0, sy=3.85 - ycut - 0.15 - 1.25)
        st.fade_out(pull + [pipe] + whl, t_lift + 0.9, 1.0)
        fillsed = st.rect(cx, (sb - 0.03 - 3.45) / 2, 2 * hole + 0.02, sb - 0.03 + 3.45, P.SEABED, 0.04)      # same extent as the seabed: seamless
        st.fade_in(fillsed, t_lift + 2.2, 0.8)
        st.fade_in(stays, t_lift + 1.6, 0.4)
        st.fade_out(ctag, s[2], 0.3)
        # ROV survey: a clean seabed (only the old cuttings mound)
        t_rov = s[2]
        r0 = -5.2
        rv = [st.rect(r0, 2.35, 1.25, 0.55, P.PANEL2, 0.6, role="solid"), st.rect(r0, 2.6, 1.25, 0.1, P.WARN, 0.61),
              st.circle(r0 + 0.53, 2.3, 0.08, P.WARN, 0.62), st.text("ROV", r0 - 0.1, 2.3, 0.15, P.TEXT, 0.62, kind="bold")]
        beam = st.poly([(r0 + 0.5, 2.1), (r0 - 0.4, sb + 0.04), (r0 + 1.6, sb + 0.04)], P.TEXT, 0.58, alpha=0.12)
        st.fade_in(rv + [beam], t_rov - 0.2, 0.3)
        st.move(rv + [beam], t_rov, b.word(2, "catch", 1.0) + 0.3, dx=11.0, interp="LINEAR")
        st.fade_out(rv + [beam], b.word(2, "catch", 1.0) + 0.1, 0.3)
        cut_l = tag(st, cx + 3.6, sb + 0.45, "old cuttings", P.MUTED, 0.15, align="c")
        st.fade_in(cut_l, t_rov + 1.2, 0.4)
        t_tr = W(b, 2, "fishing trawl")
        # a bottom trawl towed to the right: cod end trailing, mouth ahead, warps up to the (off-screen) vessel
        m = -3.9
        net = [st.line([(m, sb + 0.08), (m, sb + 0.95), (m - 1.7, sb + 0.6), (m - 2.0, sb + 0.42), (m - 1.7, sb + 0.25)], P.MUTED, 0.03, 0.57, closed=True)]
        net += [st.line([(m - 0.45 * k, sb + 0.08 + 0.05 * k), (m - 0.45 * k, sb + 0.95 - 0.1 * k)], P.MUTED, 0.015, 0.57) for k in (1, 2, 3)]
        net += [st.line([(m, sb + 0.95), (m + 2.2, 3.8)], P.MUTED, 0.02, 0.57), st.line([(m, sb + 0.08), (m + 2.6, 3.8)], P.MUTED, 0.02, 0.57)]
        st.fade_in(net, t_tr - 0.2, 0.3)
        st.move(net, t_tr - 0.2, s[3] - 0.2, dx=8.0, interp="LINEAR")
        st.fade_out(net, s[3] - 0.5, 0.3)
        cs = pill(st, 2.6, 2.45, "clear seabed: nothing for a trawl to catch", P.SAFE, "#06201c", 0.18, 0.6)
        st.fade_in(cs, t_tr + 0.6, 0.4)
        st.fade_out(cs, s[3] + 0.2, 0.4)
        # temporary abandonment: wellhead left, plugged, time-limited
        t_ta = W(b, 3, "temporary abandonment")
        st.fade_out(stays + spl, t_ta - 0.6, 0.3)
        cxp = 2.3
        card = st.rect(4.45, -1.75, 5.9, 3.1, P.PANEL, 0.7)
        ttl = st.text("TEMPORARY ABANDONMENT", 1.75, -0.45, 0.18, P.WARN, 0.72, align="l", kind="bold")
        mini_sb = st.rect(cxp, -1.05, 1.6, 0.04, "#8b7a5e", 0.72)
        mini = [st.rect(cxp - 0.18, -2.05, 0.05, 2.0, P.STEEL, 0.73), st.rect(cxp + 0.18, -2.05, 0.05, 2.0, P.STEEL, 0.73),
                st.rect(cxp, -1.65, 0.31, 0.3, P.CEMENT, 0.73), st.rect(cxp, -2.6, 0.31, 0.4, P.CEMENT, 0.73)]
        mwh = st.rect(cxp, -0.85, 0.5, 0.4, P.STEEL_DK, 0.74)
        st.fade_in([card, ttl, mini_sb] + mini, t_ta - 0.3, 0.4)
        st.fade_in(mwh, W(b, 3, "wellhead left"), 0.4)
        st.ripple(cxp, -0.85, W(b, 3, "wellhead left"), W(b, 3, "wellhead left") + 1.4, P.TEXT, period=0.7, r0=0.2, r1=0.6)
        wl = st.text("wellhead left on", cxp + 0.45, -0.85, 0.17, P.TEXT, 0.74, align="l", kind="bold")
        st.fade_in(wl, W(b, 3, "wellhead left") + 0.2, 0.3)
        t_back = W(b, 3, "come back")
        ret = st.text("so we can come back", cxp + 0.45, -1.2, 0.15, P.MUTED, 0.74, align="l")
        st.fade_in(ret, t_back - 0.1, 0.4)
        # calendar + limit
        kx, ky = 5.85, -1.75
        cal = [st.rect(kx, ky, 1.5, 1.4, P.PANEL2, 0.73), st.rect(kx, ky + 0.55, 1.5, 0.3, P.MUTED, 0.74)]
        for r_ in range(3):
            for c_ in range(5):
                cal.append(st.rect(kx - 0.52 + c_ * 0.26, ky + 0.15 - r_ * 0.28, 0.14, 0.14, P.MUTED, 0.74, alpha=0.6))
        t_lim = W(b, 3, "time-limited")
        st.fade_in(cal, t_lim - 0.8, 0.4)
        lim = pill(st, kx, ky - 1.05, "time-limited", P.BAD, "#ffffff", 0.18, 0.76)
        st.pop_in(lim, t_lim, 0.4)
        st.fade_in(lim, t_lim, 0.2)


# ====================================================================================== 9.08 the as-abandoned drawing
def beat_filed(st, tl):
    b = tl["9.08"]
    s = b.sent
    with st.span(b.start, b.end):
        sch = schematic(st, b.start, cut=True)
        deep = []
        for k in DEEP:
            deep += plug_objs(st, PLUG[k], 0.1) + [plug_verified(st, PLUG[k])]
        st.fade_in(deep, b.start + 0.1, 0.4)
        # the last plug, just below the seabed
        t_last = W(b, 0, "last plug")
        sp = plug_objs(st, PLUG["surf"], 0.1)
        st.fade_in(sp, t_last - 0.1, 0.5)
        spv = plug_verified(st, PLUG["surf"])
        st.draw_on(spv, t_last + 0.6, t_last + 1.3)
        st.ripple(SX, zy(380), t_last, t_last + 1.6, P.SAFE, period=0.8, r0=0.2, r1=0.8)
        # labels from the plug list
        lx = -1.55
        rows = [("surf", 3.05), ("sa_s", zy(2750) + 0.12), ("sa_p", zy(2930) - 0.12), ("res_s", zy(3525)), ("res_p", zy(3930))]
        labs = []
        for k, y in rows:
            p = PLUG[k]
            yp = (zy(p.top) + zy(p.base)) / 2
            o = tag(st, lx, y, "✓ " + p.label, P.TEXT, 0.15) + leader(st, lx - 0.05, y, SX + plug_hw(p) + 0.05, yp)
            labs += o
        st.fade_in(labs[:4], t_last + 0.4, 0.4)
        st.fade_in(labs[4:], b.start + 0.6, 0.4)
        # zoom inset: the top of the well (casing stubs cut below the seabed, surface plug inside, seabed clear)
        ix, iy, iw, ih = 4.6, 2.2, 5.6, 3.0
        ins = [st.rect(ix, iy, iw, ih, P.PANEL, 0.3),
               st.text("TOP OF THE WELL, ZOOMED IN", ix - iw / 2 + 0.25, iy + ih / 2 - 0.25, 0.15, P.MUTED, 0.31, align="l", kind="bold")]
        gx, gw = ix - 0.9, 3.4                              # drawing window inside the card
        ysb = iy + 0.35
        sea_ = st.rect(gx, (ysb + iy + 1.0) / 2, gw, iy + 1.0 - ysb, P.SEA, 0.31)
        mud_ = st.rect(gx, (ysb + iy - 1.3) / 2, gw, ysb - (iy - 1.3), P.SEABED, 0.31)
        ycut = ysb - 0.35
        stubs = []
        for i, hw in enumerate((1.1, 0.8, 0.56, 0.4)):
            for sg in (-1, 1):
                stubs.append(st.rect(gx + sg * hw, (ycut + iy - 1.3) / 2, 0.06, ycut - (iy - 1.3), P.STEEL, 0.33))
        cemi = st.rect(gx, (ycut - 0.06 + iy - 1.3) / 2, 2.2, ycut - 0.06 - (iy - 1.3), P.CEMENT, 0.32)      # bore + annuli
        ver = outline(st, gx - 1.18, ycut - 0.04, gx + 1.18, iy - 1.28, P.SAFE, 0.34, 0.03)
        cutl = st.dashed((gx - 1.45, ycut), (gx + 1.45, ycut), P.WARN, 0.025, 0.1, 0.07, 0.34)
        lx2 = gx + gw / 2 + 0.15
        il = [st.text("seabed: clear", lx2, ysb + 0.2, 0.16, P.TEXT, 0.34, align="l", kind="bold"),
              st.text(wrap_to("strings cut below the seabed", 0.16, 1.9), lx2, ycut - 0.25, 0.16, P.WARN, 0.34, align="l", kind="bold"),
              st.text("surface plug", lx2, iy - 0.95, 0.16, P.TEXT, 0.34, align="l", kind="bold")]
        il += leader(st, lx2 - 0.05, iy - 0.95, gx + 0.95, iy - 0.95, z=0.35)
        st.fade_in(ins + [sea_, mud_] + stubs + [cemi] + cutl + il, t_last + 0.6, 0.5)
        st.fade_in(ver, t_last + 1.3, 0.3)
        # the drawing is stamped and filed
        t_draw = W(b, 0, "as-abandoned drawing")
        sx_, sy_ = 4.75, -1.05
        sheet = [st.rect(sx_, sy_, 1.5, 1.95, P.TEXT, 0.5, role="flat")]
        for k in range(5):
            sheet.append(st.rect(sx_ + 0.15, sy_ + 0.55 - 0.25 * k, 0.8, 0.03, P.MUTED, 0.51))
        sheet.append(st.rect(sx_ - 0.45, sy_ - 0.1, 0.12, 1.4, P.STEEL_DK, 0.51))
        for k in range(3):
            sheet.append(st.rect(sx_ - 0.45, sy_ + 0.3 - 0.4 * k, 0.24, 0.16, P.CEMENT, 0.52))
        st.fade_in(sheet, t_draw - 0.4, 0.4)
        stamp = pill(st, sx_, sy_ - 0.35, "AS-ABANDONED", P.SAFE, "#06201c", 0.16, 0.53)
        st.pop_in(stamp, t_draw + 0.4, 0.4)
        st.fade_in(stamp, t_draw + 0.4, 0.2)
        box = [st.rect(sx_, -3.05, 2.2, 0.7, P.PANEL2, 0.6), st.text("WELL ARCHIVE", sx_, -3.05, 0.16, P.MUTED, 0.61, kind="bold")]
        t_fil = W(b, 0, "filed")
        st.fade_in(box, t_fil - 0.6, 0.4)
        st.move(sheet + stamp, t_fil + 0.2, t_fil + 1.4, dy=-1.6)
        st.fade_out(sheet + stamp, t_fil + 1.0, 0.4)
        lt = st.text(wrap_to("the last page in the well's life", 0.3, 3.0, "bold"), 4.7, -0.65, 0.3, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(lt, W(b, 1, "last page"), 0.5)
        lt2 = st.text("right for\nthe long term", 4.7, -1.85, 0.26, P.WARN, 0.5, align="l", kind="bold")
        st.fade_in(lt2, W(b, 1, "long term"), 0.5)


def build(st, tl):
    F.header(st, tl)
    names = [p.name for p in M.programme()]
    F.well_strip(st, 0.0, tl.dur, strings=names, marker=M.TD)
    b5, b6, b8 = tl["9.05"], tl["9.06"], tl["9.08"]
    t_placed = W(b5, 3, "excess")
    t_ver = W(b6, 5, "verified")
    strip_plugs(st, t_placed, b6.start + 0.01, DEEP)
    strip_plugs(st, b6.start, tl.dur, DEEP, t_ver=t_ver)
    t_last = W(b8, 0, "last plug")
    strip_plugs(st, t_last, tl.dur, ("surf",), t_ver=t_last + 0.6)
    beat_why(st, tl)
    beat_sources(st, tl)
    beat_rock(st, tl)
    beat_ways(st, tl)
    beat_place(st, tl)
    beat_verify(st, tl)
    beat_cut(st, tl)
    beat_filed(st, tl)
