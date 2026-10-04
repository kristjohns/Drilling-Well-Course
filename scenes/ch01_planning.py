"""Ch 1: Planning: casing from the bottom up.

Core animation: the mud-weight window vs depth, then the bottom-up stair-step that places each casing shoe
while the strings telescope down beside it. All numbers come from scenes/common/well_model.py.
"""
from __future__ import annotations
import math

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.shapes import WindowChart, CasingColumn, pill

TITLE = "Planning: casing from the bottom up"


# ----------------------------------------------------------------------------- helpers
def _y(z):            # full-height cross-section scale used in 1.01 / 1.06
    return 3.45 - z * 6.65 / 4200.0


def _window_static(st, t0, t1, fade=0.5):
    """Whole window chart (axes, curves, band, margins) appearing at t0 with a quick fade."""
    with st.span(t0, t1):
        wc = WindowChart(st)
        objs = wc.axes() + [wc.curves()["pp"], wc.objs["fg"], wc.objs["pp_lbl"], wc.objs["fg_lbl"], wc.band()] + wc.margins()
        st.fade_in(objs, t0 + 0.05, fade)
    return wc


# ----------------------------------------------------------------------------- 1.01 target
def beat_target(st, tl):
    b = tl["1.01"]
    s = b.sent
    with st.span(b.start, b.end):
        X0, X1 = -6.0, 7.6
        cx = (X0 + X1) / 2
        sea = st.rect(cx, (_y(0) + _y(300)) / 2, X1 - X0, _y(0) - _y(300), P.SEA, 0.0)
        surf = st.rect(cx, _y(0), X1 - X0, 0.04, P.PORE, 0.05)
        layers = [(300, 1000, P.ROCK), (1000, 2200, P.ROCK2), (2200, 3400, P.ROCK), (3400, 3950, P.SHALE), (3950, M.RES_BASE, P.SAND), (M.RES_BASE, 4200, P.ROCK)]
        strata = [st.rect(cx, (_y(a) + _y(c)) / 2, X1 - X0, _y(a) - _y(c), col, 0.0) for a, c, col in layers]
        ticks = []
        for zt in (0, 1000, 2000, 3000, 4000):
            ticks.append(st.text(f"{zt:,} m", X0 + 0.1, _y(zt) + 0.2, 0.2, P.TEXT, 0.2, align="l"))
            ticks.append(st.rect(cx, _y(zt), X1 - X0, 0.012, P.GRID, 0.06, alpha=0.7))
        st.text("sea level", X1 - 0.1, _y(0) + 0.2, 0.17, P.MUTED, 0.2, align="r")
        st.text("seabed", X1 - 0.1, _y(300) - 0.2, 0.17, P.TEXT, 0.2, align="r")
        st.fade_in([sea] + strata + ticks, b.start, 0.6)
        # target highlight
        hl = st.rect(cx, (_y(3950) + _y(M.RES_BASE)) / 2, X1 - X0, _y(3950) - _y(M.RES_BASE) + 0.14, P.WARN, 0.03)
        tag = st.text("TARGET: sandstone, 3,950 m TVD", 3.3, _y(3950) + 0.5, 0.3, P.WARN, 0.3, kind="bold")
        arr = st.arrow(3.3, _y(3950) + 0.3, 3.3, _y(3950) + 0.06, P.WARN, 0.05, 0.2, 0.3)
        st.fade_in([hl, tag] + arr, s[1], 0.5)
        # TVD vs measured depth
        xs = -2.6
        tvd = st.dashed((xs, _y(0)), (xs, _y(3950)), P.TEXT, 0.045, 0.22, 0.14, 0.3)
        tvd_lbl = pill(st, xs - 0.2, _y(2000), "TVD: straight down", P.PANEL2, P.TEXT, 0.24, 0.35, align="r")
        pts = [(xs + 0.9 * math.sin(i / 7 * math.pi * 1.4) * (i / 7), _y(3950 * i / 7)) for i in range(8)]
        pts[-1] = (xs, _y(3950))
        md = st.line(pts, P.PORE, 0.07, 0.31)
        md_lbl = pill(st, xs + 1.5, _y(1400), "measured depth:\nalong the hole", P.PANEL2, P.PORE, 0.22, 0.35, align="l")
        st.fade_in(tvd + tvd_lbl, s[2], 0.4)
        st.draw_on(md, s[2] + 0.4, s[2] + 2.6)
        st.fade_in(md_lbl, s[2] + 1.8, 0.4)
        goal = pill(st, 3.3, _y(3000), "reach it safely, and find out\nwhat is in it", P.PANEL2, P.TEXT, 0.26, 0.35)
        st.fade_in(goal, s[3], 0.5)


# ----------------------------------------------------------------------------- 1.02 hydrostatic + pore pressure
def beat_hydrostatic(st, tl):
    b = tl["1.02"]
    s = b.sent
    with st.span(b.start, b.end):
        # A: diver in a water column
        col = st.rect(-4.9, 0.1, 1.7, 5.4, P.SEA, 0.0)
        top, bot = 2.8, -2.6
        diver = [st.circle(-4.9, top - 0.3, 0.17, P.WARN, 0.3), st.rect(-4.9, top - 0.68, 0.22, 0.45, P.WARN, 0.3)]
        reads = [st.text(f"{n} bar", -3.8, top - 0.5 - 0.95 * n, 0.26, P.WARN, 0.3, align="l", kind="bold") for n in range(3)]
        st.fade_in([col] + diver + reads[:1], s[0], 0.5)
        st.move(diver, s[1], s[1] + 3.0, dy=-2.3)
        st.fade_in(reads[1], s[1] + 1.0, 0.3)
        st.fade_in(reads[2], s[1] + 2.0, 0.3)
        g1 = st.text("+1 bar per 10 m", -4.9, 2.95, 0.25, P.TEXT, 0.35, kind="bold")
        st.fade_in(g1, s[1] + 0.2, 0.4)
        # B: pressure-depth lines
        from scenes.common.chart import Chart
        c = Chart(st, -2.1, -2.3, 3.9, 4.6, (0, 700), (0, 4000), invert_y=True)
        fr = c.frame(xticks=[0, 200, 400, 600], yticks=[0, 2000, 4000], xlabel="pressure (bar)", ylabel="depth (m)", title=None)
        zs = [0, 4000]
        w1 = c.curve([M.bar(z, 1.0) for z in zs], zs, P.PORE, 0.07, 0.3)
        w2 = c.curve([M.bar(z, 1.62) for z in zs], zs, P.MUD, 0.07, 0.3)
        l1 = st.text("water, 1.0 sg", c.X(M.bar(3300, 1.0)) + 0.15, c.Y(3300) + 0.1, 0.2, P.PORE, 0.3, align="l")
        l2 = st.text("mud, 1.62 sg", c.X(M.bar(1700, 1.62)) + 0.15, c.Y(1700) - 0.05, 0.2, P.MUD, 0.3, align="l")
        eq = st.text("P = ρ g h", 0.0, 2.75, 0.34, P.TEXT, 0.3, kind="mono")
        sg = st.text("sg = density relative to fresh water", 0.0, 2.35, 0.2, P.MUTED, 0.3)
        st.fade_in(fr, s[2] - 0.2, 0.5)
        st.draw_on(w1, s[2], s[2] + 1.4)
        st.draw_on(w2, s[3], s[3] + 1.6)
        st.fade_in([l1], s[2] + 1.0, 0.3)
        st.fade_in([l2, eq, sg], s[3] + 1.0, 0.4)
        # C: rock with pores connected to the sea
        rock = st.rect(5.2, -1.4, 3.6, 3.2, P.ROCK, 0.0)
        sea2 = st.rect(5.2, 1.5, 3.6, 0.8, P.SEA, 0.0)
        tube = st.rect(5.2, 0.15, 0.12, 1.9, P.WATER, 0.1)
        pores = []
        for i, (px, py) in enumerate([(4.2, -0.7), (4.9, -1.2), (5.7, -0.8), (6.2, -1.5), (4.5, -1.9), (5.3, -2.0), (6.0, -2.2), (4.1, -1.3)]):
            pores.append(st.circle(px, py, 0.2, P.WATER, 0.2))
        txt = st.text("pore pressure:\nfluid in the pores", 5.2, 2.35, 0.24, P.WATER, 0.3, kind="bold")
        norm = st.text("connected up to the sea\n= a column of water = normal pressure", 5.2, -3.15, 0.2, P.TEXT, 0.3)
        st.fade_in([rock, sea2, tube, txt], s[4], 0.5)
        for i, p in enumerate(pores):
            st.fade_in(p, s[4] + 0.3 + 0.1 * i, 0.3)
        st.fade_in(norm, s[5], 0.5)


# ----------------------------------------------------------------------------- 1.03 Terzaghi overpressure
def _cyl(st, cx, blocked):
    parts = {}
    parts["wall"] = [st.rect(cx - 0.8, -0.25, 0.08, 4.0, P.STEEL_DK, 0.1), st.rect(cx + 0.8, -0.25, 0.08, 4.0, P.STEEL_DK, 0.1),
                     st.rect(cx, -2.25, 1.68, 0.08, P.STEEL_DK, 0.1)]
    parts["water"] = st.rect(cx, -2.2, 1.5, 3.2, P.WATER, 0.05, anchor="b", alpha=0.85)
    coils = [st.rect(cx, -2.05 + i * 0.32, 1.0, 0.07, P.STEEL, 0.2) for i in range(10)]   # spring spans the cylinder
    parts["coils"] = coils
    left = st.rect(cx - 0.45, 1.05, 0.55, 0.2, P.STEEL, 0.25)
    right = st.rect(cx + 0.45, 1.05, 0.55, 0.2, P.STEEL, 0.25)
    plug = st.rect(cx, 1.05, 0.34, 0.2, P.BAD if blocked else P.BG, 0.26)
    parts["piston"] = [left, right, plug]
    parts["arrow"] = st.arrow(cx, 2.35, cx, 1.35, P.WARN, 0.12, 0.35, 0.3)
    parts["load"] = st.text("load", cx + 0.55, 1.95, 0.24, P.WARN, 0.3, align="l", kind="bold")
    return parts


def beat_terzaghi(st, tl):
    b = tl["1.03"]
    s = b.sent
    with st.span(b.start, b.end):
        title = st.text("Terzaghi's piston and spring", -0.4, 3.75, 0.3, P.TEXT, 0.3, kind="bold")
        st.fade_in(title, s[1], 0.4)
        out = {}
        for key, cx, blocked in (("A", -3.4, False), ("B", 1.9, True)):
            p = _cyl(st, cx, blocked)
            out[key] = (cx, p)
            body = p["wall"] + [p["water"]] + p["coils"] + p["piston"]
            st.fade_in(body, s[1], 0.5)
            lab = st.text("hole open" if not blocked else "hole blocked", cx, -2.75, 0.26, P.TEXT, 0.3, kind="bold")
            st.fade_in(lab, s[1] + 0.2, 0.4)
            # gauges: water pressure + spring stress (anchored at bottom)
            gx = cx + 1.35
            gf1 = st.rect(gx, -2.2, 0.28, 3.0, P.PANEL2, 0.1, anchor="b")
            gf2 = st.rect(gx + 0.45, -2.2, 0.28, 3.0, P.PANEL2, 0.1, anchor="b")
            wbar = st.rect(gx, -2.2, 0.28, 0.0001, P.PORE, 0.2, anchor="b")
            sbar = st.rect(gx + 0.45, -2.2, 0.28, 0.0001, P.STEEL, 0.2, anchor="b")
            t1 = st.text("water p", gx, 1.0, 0.16, P.PORE, 0.3, kind="bold")
            t2 = st.text("grains σ′", gx + 0.45, 1.25, 0.16, P.STEEL, 0.3, kind="bold")
            st.fade_in([gf1, gf2, t1, t2], s[1] + 0.4, 0.4)
            out[key] = (cx, p, wbar, sbar)
        # A: load -> water carries -> leaks -> spring takes over
        cx, p, wbar, sbar = out["A"]
        t_load, t_end = s[2] + 0.4, s[2] + 7.0
        st.scale_to(wbar, t_load - 0.4, t_load + 0.3, sy=2.8)
        st.scale_to(sbar, t_load - 0.4, t_load, sy=0.08)
        st.scale_to(wbar, t_load + 0.3, t_end, sy=0.25)
        st.scale_to(sbar, t_load + 0.3, t_end, sy=2.55)
        st.move(p["piston"] + [p["arrow"][0], p["arrow"][1], p["load"]], t_load + 0.3, t_end, dy=-0.55)
        st.scale_to(p["water"], t_load + 0.3, t_end, sy=2.65)
        for i, cl in enumerate(p["coils"]):            # spring compresses: top coil follows the piston, bottom coil stays put
            st.move(cl, t_load + 0.3, t_end, dy=-0.55 * i / (len(p["coils"]) - 1))
        # B: blocked: water keeps carrying
        cx2, p2, wbar2, sbar2 = out["B"]
        t_load2 = s[3] + 0.3
        st.scale_to(wbar2, t_load2 - 0.4, t_load2 + 0.3, sy=2.8)
        st.scale_to(sbar2, t_load2 - 0.4, t_load2, sy=0.08)
        st.scale_to(sbar2, t_load2 + 0.3, t_load2 + 5.0, sy=0.2)
        ov = st.text("overpressure", cx2, -0.8, 0.3, P.WARN, 0.4, kind="bold")
        st.fade_in(ov, s[3] + 3.0, 0.5)
        # equation
        eq = st.text("σ′ = σ − p", -0.4, 2.85, 0.48, P.TEXT, 0.4, kind="bold")
        sub = st.text("effective stress = total stress − pore pressure", -0.4, 2.3, 0.2, P.MUTED, 0.4)
        bg = st.rect(-0.4, 2.55, 4.6, 1.15, P.PANEL2, 0.35)
        st.fade_in([bg, eq, sub], s[4], 0.6)


# ----------------------------------------------------------------------------- 1.04 fracture + collapse + LOT teaser
def _hole_panel(st, cx, cy, size=3.4):
    plate = st.rect(cx, cy, size, size, P.ROCK, 0.0)
    hole = st.circle(cx, cy, 0.55, P.BG, 0.1)
    return plate, hole


def beat_fracture(st, tl):
    b = tl["1.04"]
    s = b.sent
    with st.span(b.start, b.end):
        cL, cM, cR, cy = -4.0, 0.2, 4.4, 0.4
        plateL, holeL = _hole_panel(st, cL, cy)
        plateM, holeM = _hole_panel(st, cM, cy)
        titles = [st.text("pressure too high", cL, cy + 2.15, 0.26, P.FRAC, 0.3, kind="bold"),
                  st.text("pressure too low", cM, cy + 2.15, 0.26, P.COLLAPSE, 0.3, kind="bold"),
                  st.text("leak-off test", cR, cy + 2.15, 0.26, P.TEXT, 0.3, kind="bold")]
        st.fade_in([plateL, holeL, plateM, holeM], b.start, 0.5)
        # s1: stress concentration rings around the hole + far-field arrows
        rings = [st.ring(cL, cy, 0.9, 0.35, P.WARN, 0.05, 0.40), st.ring(cL, cy, 1.25, 0.35, P.WARN, 0.04, 0.22), st.ring(cL, cy, 1.6, 0.35, P.WARN, 0.03, 0.12)]
        far = [st.arrow(cL - 1.95, cy, cL - 1.45, cy, P.MUTED, 0.06, 0.2, 0.3), st.arrow(cL + 1.95, cy, cL + 1.45, cy, P.MUTED, 0.06, 0.2, 0.3)]
        conc = st.text("2–3× the far-field stress\nat the wall of the hole", cL, cy - 1.95, 0.22, P.WARN, 0.3)
        st.fade_in(far, s[1] - 0.2, 0.4)
        st.fade_in(rings + [conc], s[1] + 0.3, 0.6)
        # s2: internal pressure pushes back
        push = []
        for i in range(8):
            a = i * math.pi / 4
            push += st.arrow(cL + 0.62 * math.cos(a), cy + 0.62 * math.sin(a), cL + 1.0 * math.cos(a), cy + 1.0 * math.sin(a), P.MUD, 0.07, 0.22, 0.35)
        st.fade_in(push, s[2], 0.4)
        # s3: crack
        crack = st.line([(cL + 0.55, cy + 0.05), (cL + 0.9, cy + 0.3), (cL + 1.2, cy + 0.2), (cL + 1.6, cy + 0.55), (cL + 1.7, cy + 0.6)], P.BAD, 0.09, 0.4)
        st.fade_in(titles[0], s[3] - 0.2, 0.3)
        st.draw_on(crack, s[3], s[3] + 1.5)
        ck = st.text("rock splits: fracture gradient", cL, cy - 2.75, 0.24, P.BAD, 0.4, kind="bold")
        st.fade_in(ck, s[3] + 1.0, 0.4)
        # s4: collapse (chips fall inward)
        st.fade_in(titles[1], s[4] - 0.2, 0.3)
        chips = []
        for i, a in enumerate([0.4, 1.4, 2.5, 3.6, 4.6, 5.6]):
            px, py = cM + 0.62 * math.cos(a), cy + 0.62 * math.sin(a)
            c = st.poly([(px - 0.1, py - 0.08), (px + 0.1, py - 0.06), (px, py + 0.12)], P.COLLAPSE, 0.3)
            chips.append(c)
            st.fade_in(c, s[4], 0.3)
            st.move(c, s[4] + 0.3, s[4] + 1.5, to=(cM + 0.18 * math.cos(a), cy + 0.18 * math.sin(a)))
        col = st.text("wall shears: collapse", cM, cy - 1.95, 0.24, P.COLLAPSE, 0.4, kind="bold")
        st.fade_in(col, s[4] + 1.0, 0.4)
        # s5: LOT curve
        from scenes.common.chart import Chart
        c = Chart(st, cR - 1.4, cy - 1.45, 2.9, 2.9, (0, 6), (0, 8))
        fr = c.frame(xticks=[], yticks=[], xlabel="volume pumped", ylabel="pressure", grid=False)
        xs = [0, 1, 2, 3, 3.6, 4.3, 5.2, 6]
        ys = [0, 2, 4, 6, 6.9, 7.3, 7.5, 7.6]
        ln = c.curve(xs, ys, P.PORE, 0.07, 0.4)
        dot = c.dot(3.4, 6.6, 0.1, P.WARN, 0.5)
        lp = c.label(3.55, 6.0, "leak-off\npoint", 0.2, P.WARN, "l", dx=0.1, dy=-0.4)
        st.fade_in(titles[2], s[5] - 0.2, 0.3)
        st.fade_in(fr, s[5], 0.4)
        st.draw_on(ln, s[5] + 0.3, s[5] + 2.2)
        st.fade_in([dot, lp], s[5] + 1.8, 0.4)


# ----------------------------------------------------------------------------- 1.05 the window chart
def beat_window(st, tl):
    b = tl["1.05"]
    s = b.sent
    with st.span(b.start, b.end):
        wc = WindowChart(st)
        ax = wc.axes()
        st.fade_in(ax, b.start + 0.2, 0.5)
        cu = wc.curves()
        st.draw_on(cu["pp"], s[1], s[1] + 1.8)
        st.fade_in(cu["pp_lbl"], s[1] + 1.4, 0.3)
        st.draw_on(cu["fg"], s[1] + 2.0, s[1] + 3.8)
        st.fade_in(cu["fg_lbl"], s[1] + 3.4, 0.3)
        band = wc.band()
        st.fade_in(band, s[2], 0.7)
        mg = wc.margins()
        st.fade_in(mg, s[2] + 0.4, 0.5)
        c = wc.c
        mud = st.circle(c.X(1.27), c.Y(2200), 0.13, P.MUD, 0.4)
        mudl = pill(st, c.X(1.27) + 0.3, c.Y(2200), "mud weight", P.PANEL2, P.MUD, 0.2, 0.45, align="l")
        st.fade_in([mud] + mudl, s[2] + 0.8, 0.4)
        st.move([mud] + mudl, s[2] + 1.4, s[2] + 2.4, dx=0.5)
        st.move([mud] + mudl, s[2] + 2.4, s[2] + 3.4, dx=-0.9)
        # s3: window narrows
        brs = []
        for z in (1500, 3900):
            xa, xb = c.X(M.pp(z)), c.X(M.fg(z))
            y = c.Y(z)
            brs += st.arrow((xa + xb) / 2, y, xb, y, P.TEXT, 0.045, 0.16, 0.5) + st.arrow((xa + xb) / 2, y, xa, y, P.TEXT, 0.045, 0.16, 0.5)
            brs.append(st.text(f"{M.fg(z) - M.pp(z):.2f} sg", (xa + xb) / 2, y + 0.22, 0.21, P.TEXT, 0.5, kind="bold"))
        st.fade_in(brs, s[3] + 0.4, 0.5)
        # right-hand explainer text
        eq = st.text("EMW = P / (0.0981 × depth)", 4.2, 2.6, 0.26, P.TEXT, 0.4, kind="mono", align="c")
        e1 = st.text("equivalent mud weight:\nthe mud weight that would\ngive the same pressure", 4.2, 1.6, 0.22, P.MUTED, 0.4)
        e2 = st.text("the mud must stay inside the\ngreen window, with a margin\neach side", 4.2, -0.2, 0.24, P.SAFE, 0.4, kind="bold")
        e3 = st.text("pore pressure climbs faster than the\nrock's resistance to fracture,\nso the window narrows with depth", 4.2, -1.9, 0.22, P.WARN, 0.4)
        e4 = st.text("[simplified] lower limit drawn as pore pressure only", 4.2, -3.05, 0.17, P.SIM_BADGE, 0.4)
        st.fade_in([eq, e1], s[0] + 1.5, 0.5)
        st.fade_in(e2, s[2] + 0.2, 0.5)
        st.fade_in(e3, s[3] + 0.5, 0.5)
        st.fade_in(e4, s[4], 0.5)


# ----------------------------------------------------------------------------- 1.06 shallow hazards
def beat_hazards(st, tl):
    b = tl["1.06"]
    s = b.sent
    with st.span(b.start, b.end):
        sea = st.rect(0.8, 2.6, 14.0, 2.0, P.SEA, 0.0)
        rock = st.rect(0.8, -1.2, 14.0, 4.6, P.ROCK, 0.0)
        till = st.rect(0.8, 0.0, 14.0, 1.0, P.ROCK2, 0.02)
        seabed = st.rect(0.8, 1.05, 14.0, 0.05, P.SEABED, 0.1)
        st.fade_in([sea, rock, till, seabed], b.start, 0.5)
        lab = st.text("near-seabed hazards", -5.8, 3.5, 0.3, P.TEXT, 0.3, align="l", kind="bold")
        st.fade_in(lab, b.start + 0.3, 0.4)
        # gas pocket
        cap = st.rect(-2.3, -0.75, 1.9, 0.16, P.SHALE, 0.15)
        gas = st.circle(-2.3, -1.25, 0.5, P.GAS, 0.15)
        gl = pill(st, -2.3, -2.4, "shallow gas", P.PANEL2, P.GAS, 0.24, 0.4)
        gnote = st.text("pocket a few hundred\nmetres down, can arrive fast", -2.3, -3.0, 0.18, P.MUTED, 0.3)
        st.fade_in([cap, gas] + gl + [gnote], s[1], 0.5)
        # boulders
        bl = [st.circle(2.0, -0.1, 0.3, "#9aa3ad", 0.2), st.circle(2.7, -0.3, 0.38, "#aab2bb", 0.2), st.circle(3.3, 0.05, 0.25, "#8f98a3", 0.2)]
        bll = pill(st, 2.7, -1.2, "boulders", P.PANEL2, P.TEXT, 0.24, 0.4)
        bln = st.text("left by glaciers", 2.7, -1.75, 0.18, P.MUTED, 0.3)
        st.fade_in(bl + bll + [bln], s[2], 0.5)
        # soft / uneven seabed (pockmark)
        pm = st.poly([(5.0, 1.07), (5.55, 0.6), (6.1, 1.07)], P.BG, 0.12)
        pml = pill(st, 5.55, -0.6, "soft, uneven seabed", P.PANEL2, P.TEXT, 0.22, 0.4)
        st.fade_in([pm] + pml, s[3], 0.5)
        # survey ship and sonar fan
        hull = st.poly([(-6.4, 3.0), (-4.8, 3.0), (-5.1, 2.6), (-6.1, 2.6)], P.STEEL, 0.5)
        fan = st.poly([(-5.6, 2.6), (-7.0, 1.1), (-4.2, 1.1)], P.PORE, 0.3, 0.22)
        st.fade_in([hull, fan], s[4], 0.4)
        st.move([hull, fan], s[4] + 0.4, s[4] + 6.0, dx=11.0, interp="LINEAR")
        sv = st.text("a seabed survey maps them\nbefore the rig arrives", 0.8, -3.2, 0.24, P.SAFE, 0.4, kind="bold")
        st.fade_in(sv, s[4] + 1.0, 0.5)


# ----------------------------------------------------------------------------- 1.07 / 1.08 bottom-up stair-step
def beat_bottom_up(st, tl):
    b7, b8 = tl["1.07"], tl["1.08"]
    s7, s8 = b7.sent, b8.sent
    t0, t1 = b7.start, b8.end
    prog = M.programme()
    shoes = {p.name: p.shoe for p in prog}
    design = M.design_bottom_up()            # deepest first
    with st.span(t0, t1):
        wc = WindowChart(st)
        objs = wc.axes() + [wc.curves()["pp"], wc.objs["fg"], wc.objs["pp_lbl"], wc.objs["fg_lbl"], wc.band()] + wc.margins()
        st.fade_in(objs, t0 + 0.05, 0.6)
        col = CasingColumn(st, wc.c, cx=4.5)
        st.fade_in(col.backdrop(), t0 + 0.05, 0.6)
        c = wc.c
        # --- step 1: TD -> shoe at ~3,400
        d1 = design[0]
        arrow = st.arrow(c.X(1.62) + 1.0, c.Y(4150), c.X(1.62) + 1.0, c.Y(3600), P.TEXT, 0.06, 0.26, 0.5)
        bu = st.text("from the bottom up", c.X(1.62) + 1.12, c.Y(3880), 0.22, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(arrow + [bu], s7[1], 0.5)
        td_dot = st.circle(c.X(1.62), c.Y(M.TD), 0.13, P.MUD, 0.45)
        td_lbl = pill(st, c.X(1.0), c.Y(3900), "total depth 4,200 m:\nneeds about 1.62 sg", P.PANEL2, P.MUD, 0.22, 0.6, align="c")
        td_ld = st.line([(c.X(1.0) + 1.3, c.Y(3900)), (c.X(1.62) - 0.12, c.Y(M.TD) + 0.02)], P.MUD, 0.025, 0.55)
        st.fade_in([td_dot, td_ld] + td_lbl, s7[2], 0.5)
        lim1 = wc.limit_curve(1.62)
        wedge1 = wc.crack_wedge(1.62, M.WATER_DEPTH + 10, d1["shoe"])
        line1, L1 = wc.mw_line(1.62, M.TD, d1["shoe"])
        st.fade_in(lim1, s7[3] - 0.2, 0.4)
        st.scale_to(line1, s7[3], s7[3] + 2.2, sy=L1)
        st.fade_in(wedge1, s7[3] + 2.0, 0.6)
        wl = pill(st, c.X(1.2), c.Y(1300), "would crack\nabove here", P.BAD, "#ffffff", 0.24, 0.6)
        st.fade_in(wl, s7[3] + 2.4, 0.5)
        st.fade_in(pill(st, c.X(1.5) - 0.1, c.Y(2500), "fracture,\nless margins", P.PANEL2, P.WARN, 0.2, 0.6, align="r"), s7[3], 0.4)
        s1 = col.string("9-5/8in intermediate", shoes["9-5/8in intermediate"], s7[4], s7[4] + 1.8)
        st.fade_in(s1[1:], s7[5] - 0.3, 0.4)
        # --- step 2: MW 1.49 -> shoe 2,000
        d2 = design[1]
        st.fade_out([lim1, wedge1, wl], s8[1] - 0.2, 0.4)
        lim2 = wc.limit_curve(1.49)
        wedge2 = wc.crack_wedge(1.49, M.WATER_DEPTH + 10, d2["shoe"])
        line2, L2 = wc.mw_line(1.49, shoes["9-5/8in intermediate"], d2["shoe"])
        lab2 = pill(st, c.X(1.49) - 0.2, c.Y(3300), "1.49 sg", P.PANEL2, P.MUD, 0.2, 0.6, align="r")
        st.fade_in([lim2] + lab2, s8[1] - 0.1, 0.4)
        st.scale_to(line2, s8[1] + 0.3, s8[1] + 2.0, sy=L2)
        st.fade_in(wedge2, s8[1] + 1.8, 0.5)
        s2 = col.string("13-3/8in intermediate", shoes["13-3/8in intermediate"], s8[1] + 2.0, s8[1] + 3.6)
        # --- step 3: MW 1.12 -> calc 660 m but constrained to 1,000
        d3 = design[2]
        st.fade_out([lim2, wedge2] + lab2, s8[2] - 0.2, 0.4)
        lim3 = wc.limit_curve(1.12)
        line3, L3 = wc.mw_line(1.12, shoes["13-3/8in intermediate"], shoes["20in surface casing"])
        lab3 = pill(st, c.X(1.12) + 0.2, c.Y(1500), "1.12 sg", P.PANEL2, P.MUD, 0.2, 0.6, align="l")
        st.fade_in([lim3] + lab3, s8[2] - 0.1, 0.4)
        st.scale_to(line3, s8[2] + 0.3, s8[2] + 1.6, sy=L3)
        calc = st.dashed((c.X(1.0), c.Y(d3["shoe_calc"])), (c.X(1.5), c.Y(d3["shoe_calc"])), P.BAD, 0.035, 0.12, 0.1, 0.5)
        calc_l = pill(st, c.X(0.93), c.Y(d3["shoe_calc"]) - 0.32, f"calculated: {d3['shoe_calc']:,.0f} m", P.PANEL2, P.BAD, 0.2, 0.6, align="l")
        st.fade_in(calc + calc_l, s8[2] + 1.6, 0.4)
        floor = pill(st, c.X(1.77), c.Y(1000), "not shallower\nthan 1,000 m:\nhazards + BOP anchor", P.PANEL2, P.WARN, 0.2, 0.6)
        st.fade_in(floor, s8[3] - 0.3, 0.5)
        s3 = col.string("20in surface casing", shoes["20in surface casing"], s8[3], s8[3] + 1.4)
        # conductor is soil-driven
        s4 = col.string("30in conductor", shoes["30in conductor"], s8[4] - 0.2, s8[4] + 1.0)
        cnote = st.text("conductor: soil-driven", col.cx + 1.15, c.Y(390) - 0.28, 0.16, P.MUTED, 0.5, align="l")
        st.fade_in(cnote, s8[4] + 0.8, 0.4)
        stair = st.text("a staircase", c.X(1.85), c.Y(2700), 0.3, P.TEXT, 0.5, kind="bold")
        st.fade_in(stair, s8[4] + 0.6, 0.5)
    return t0, t1


# ----------------------------------------------------------------------------- 1.09 telescoping + contingency
def beat_telescope(st, tl):
    b = tl["1.09"]
    s = b.sent
    prog = M.programme()
    with st.span(b.start, b.end):
        # cross-section rings (left)
        cx, cy, k = -3.3, 0.35, 0.075       # 1 inch = 0.075 units
        rings = [(1.55, P.ROCK, "rock"), (36 / 2 * k, P.CEMENT, ""), (30 / 2 * k, P.STEEL, '30" conductor'), (28.6 / 2 * k, P.CEMENT, ""),
                 (20 / 2 * k, P.STEEL, '20" surface'), (19 / 2 * k, P.CEMENT, ""), (13.375 / 2 * k, P.STEEL, '13⅜"'), (12.4 / 2 * k, P.CEMENT, ""),
                 (9.625 / 2 * k, P.STEEL, '9⅝"'), (8.9 / 2 * k, P.CEMENT, ""), (8.5 / 2 * k, P.BG, '8½" hole to TD')]
        circles = []
        for i, (r, col, _) in enumerate(rings):
            circles.append(st.circle(cx, cy, r, col, 0.05 + 0.01 * i))
        st.fade_in(circles, b.start + 0.2, 0.6)
        labs = []
        for j, (r, name) in enumerate([(30 / 2 * k, '30"'), (20 / 2 * k, '20"'), (13.375 / 2 * k, '13⅜"'), (9.625 / 2 * k, '9⅝"'), (8.5 / 2 * k, '8½" hole')]):
            ang = math.radians(25 + j * 28)
            px, py = cx + r * math.cos(ang), cy + r * math.sin(ang)
            lx, ly = cx + 1.75, cy + 1.45 - j * 0.5
            ln = st.line([(px, py), (lx - 0.05, ly)], P.MUTED, 0.02, 0.4)
            tx = st.text(name, lx, ly, 0.24, P.TEXT, 0.4, align="l", kind="bold")
            labs += [ln, tx]
        st.fade_in(labs, s[1], 0.5)
        # telescoping side view (right)
        from scenes.common.shapes import STRING_COLORS, STRING_W, STRING_LABEL
        x0, ytop, ybot = 4.0, 3.0, -2.6
        yz = lambda z: ytop - (z - 300) * (ytop - ybot) / (M.TD - 300)
        back = st.rect(x0, (ytop + yz(M.TD)) / 2, 2.8, ytop - yz(M.TD), P.ROCK, 0.0)
        sizes = [st.text(f"{STRING_LABEL[p.name]}  {p.shoe:,.0f} m", x0 + 0.95, yz(p.shoe), 0.22, P.TEXT, 0.5, align="l", kind="bold") for p in prog]
        st.fade_in([back] + sizes, s[0] + 0.5, 0.5)
        side = []
        for p in prog:
            w = STRING_W[p.name] * 1.0
            bar = st.rect(x0, ytop, w, ytop - yz(p.shoe), STRING_COLORS[p.name], 0.1 + 0.2 * (1.5 - w), anchor="t")
            side.append(bar)
        open_hole = st.rect(x0, yz(prog[-1].shoe), 0.12, yz(prog[-1].shoe) - yz(M.TD), P.BG, 0.4, anchor="t")
        st.fade_in(side + [open_hole], s[0] + 0.5, 0.5)
        nest = st.text("each string must pass through the one above", x0, 3.55, 0.22, P.TEXT, 0.4, kind="bold")
        st.fade_in(nest, s[0] + 1.0, 0.5)
        costs = st.text("every extra string costs diameter", x0, -3.05, 0.22, P.WARN, 0.4, kind="bold")
        st.fade_in(costs, s[2], 0.5)
        # wildcat + contingency strings
        dash_l = st.dashed((x0 - 0.17, yz(3300)), (x0 - 0.17, yz(M.TD)), P.WARN, 0.04, 0.16, 0.1, 0.55)
        dash_r = st.dashed((x0 + 0.17, yz(3300)), (x0 + 0.17, yz(M.TD)), P.WARN, 0.04, 0.16, 0.1, 0.55)
        cl = pill(st, x0 + 1.1, yz(3800), "contingency\nliner (7 in)", P.PANEL2, P.WARN, 0.2, 0.6, align="l")
        wl = pill(st, -3.3, -2.65, "wildcat: no offset wells\nto learn from", P.PANEL2, P.TEXT, 0.22, 0.5)
        st.fade_in(wl, s[3] + 0.2, 0.5)
        st.fade_in(dash_l + dash_r + cl, s[3] + 2.2, 0.6)


# ----------------------------------------------------------------------------- build
def build(st, tl):
    F.header(st, tl)
    b7, b8, b9 = tl["1.07"], tl["1.08"], tl["1.09"]
    s8 = b8.sent
    # well strip progression (persistent "well so far")
    T1 = b7.sent[4] + 1.8
    T2 = s8[1] + 3.6
    T3 = s8[3] + 1.4
    T4 = s8[4] + 1.0
    F.well_strip(st, 0.0, T1)
    F.well_strip(st, T1, T2, strings=["9-5/8in intermediate"])
    F.well_strip(st, T2, T3, strings=["9-5/8in intermediate", "13-3/8in intermediate"])
    F.well_strip(st, T3, T4, strings=["9-5/8in intermediate", "13-3/8in intermediate", "20in surface casing"])
    F.well_strip(st, T4, tl.dur, strings=[p.name for p in M.programme()])
    beat_target(st, tl)
    beat_hydrostatic(st, tl)
    beat_terzaghi(st, tl)
    beat_fracture(st, tl)
    beat_window(st, tl)
    beat_hazards(st, tl)
    beat_bottom_up(st, tl)
    beat_telescope(st, tl)
