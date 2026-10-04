"""Ch 5: Casing and tubular design: burst / collapse / tension, load cases, von Mises ellipse, taper, connections."""
from __future__ import annotations
import math

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common.shapes import CasingColumn, pill

TITLE = "Casing and tubular design"


def vme_radius(theta):
    """Radius of the plane-stress von Mises ellipse x^2 - xy + y^2 = 1 in direction theta."""
    c, s = math.cos(theta), math.sin(theta)
    return 1.0 / math.sqrt(c * c - c * s + s * s)


def vme_points(scale=1.0, n=90):
    return [(scale * vme_radius(2 * math.pi * i / n) * math.cos(2 * math.pi * i / n),
             scale * vme_radius(2 * math.pi * i / n) * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]


# ---------------------------------------------------------------- 5.01 tunnel lining, grade
def beat_lining(st, tl):
    b = tl["5.01"]
    s = b.sent
    with st.span(b.start, b.end):
        # tunnel lining ring -> casing ring
        cx, cy = -3.6, 0.6
        rock = st.circle(cx, cy, 2.2, P.ROCK, 0.0)
        ring = st.ring(cx, cy, 1.55, 0.22, P.STEEL, 0.2)
        hole = st.circle(cx, cy, 1.33, P.BG, 0.1)
        st.fade_in([rock, ring, hole], b.start, 0.5)
        cap = st.text("a tunnel lining…", cx, 3.2, 0.3, P.TEXT, 0.3, kind="bold")
        st.fade_in(cap, s[0], 0.5)
        cap2 = st.text("…that is the casing", cx, 3.2, 0.3, P.PORE, 0.31, kind="bold")
        bg2 = st.rect(cx, 3.2, 4.2, 0.5, P.BG, 0.305)
        st.fade_in([bg2, cap2], s[1] - 0.2, 0.5)
        jobs = []
        for i, (t, col) in enumerate((("holds the hole open", P.TEXT), ("contains pressure", P.MUD), ("isolates formations", P.CEMENT))):
            jobs.append(pill(st, cx, -2.0 - 0.6 * i, t, P.PANEL2, col, 0.24, 0.4))
        for i, j in enumerate(jobs):
            st.fade_in(j, s[1] + 0.8 * i, 0.4)
        # grade tag
        card = st.rect(3.1, 1.6, 4.8, 2.1, P.PANEL, 0.0)
        g = st.text("P110", 1.5, 2.1, 0.8, P.WARN, 0.3, kind="bold")
        gl = st.text("= 110 ksi minimum yield\n= 758 MPa", 3.7, 1.9, 0.3, P.TEXT, 0.3, align="l", kind="bold")
        st.fade_in([card, g, gl], s[2], 0.5)
        # sour service sketch
        c = Chart(st, 1.2, -2.7, 3.6, 2.5, (0, 10), (0, 10))
        fr = c.frame(xticks=[], yticks=[], xlabel="steel hardness", ylabel="cracking risk (H₂S)", grid=False)
        crv = c.curve([0, 2, 4, 6, 7.5, 9, 10], [0.4, 0.7, 1.2, 2.2, 4.0, 7.0, 9.4], P.BAD, 0.08, 0.4)
        lim = c.vline(6.5, P.WARN, 0.04, 0.35)
        ll = c.label(6.7, 8.5, "sour service:\nhardness limit", 0.2, P.WARN, "l")
        st.fade_in(fr, s[3], 0.4)
        st.draw_on(crv, s[3] + 0.3, s[3] + 2.5)
        st.fade_in([lim, ll], s[3] + 2.0, 0.4)


# ---------------------------------------------------------------- 5.02 three loads, three mechanisms
def beat_modes(st, tl):
    b = tl["5.02"]
    s = b.sent
    with st.span(b.start, b.end):
        xs = (-4.0, 0.9, 5.7)
        for x in xs:
            st.fade_in(st.rect(x, 0.2, 4.4, 6.9, P.PANEL, 0.0), s[0], 0.4)
        # burst
        t1 = st.text("BURST: internal pressure", xs[0], 3.35, 0.24, P.FRAC, 0.3, kind="bold")
        r1 = st.ring(xs[0], 1.0, 1.1, 0.16, P.STEEL, 0.2)
        a1 = []
        for i in range(10):
            a = i * math.pi / 5
            a1 += st.arrow(xs[0] + 0.55 * math.cos(a), 1.0 + 0.55 * math.sin(a), xs[0] + 0.95 * math.cos(a), 1.0 + 0.95 * math.sin(a), P.MUD, 0.05, 0.16, 0.3)
        st.fade_in([t1, r1] + a1, s[1], 0.5)
        st.scale_to(r1, s[1] + 1.0, s[1] + 3.0, sx=1.12, sy=1.12)
        fb = st.text("P_burst = 0.875 · 2·Y·t / D", xs[0], -0.9, 0.24, P.TEXT, 0.4, kind="mono")
        fb2 = st.text("API rating includes the\n12.5 % wall tolerance", xs[0], -1.9, 0.22, P.MUTED, 0.4)
        st.fade_in([fb, fb2], s[1] + 2.5, 0.5)
        # collapse
        t2 = st.text("COLLAPSE: external pressure", xs[1], 3.35, 0.24, P.COLLAPSE, 0.3, kind="bold")
        r2 = st.ring(xs[1], 1.0, 1.1, 0.12, P.STEEL, 0.2)
        a2 = []
        for i in range(10):
            a = i * math.pi / 5
            a2 += st.arrow(xs[1] + 1.55 * math.cos(a), 1.0 + 1.55 * math.sin(a), xs[1] + 1.2 * math.cos(a), 1.0 + 1.2 * math.sin(a), P.WATER, 0.05, 0.16, 0.3)
        st.fade_in([t2, r2] + a2, s[2], 0.5)
        st.scale_to(r2, s[2] + 1.5, s[2] + 4.0, sx=1.25, sy=0.7)
        dt = st.text("set by D/t: a buckling problem,\nlike crushing a can from outside", xs[1], -0.9, 0.22, P.TEXT, 0.4, kind="bold")
        dd = st.arrow(xs[1] - 1.1, -1.9, xs[1] + 1.1, -1.9, P.MUTED, 0.04, 0.16, 0.4) + st.arrow(xs[1] + 1.1, -1.9, xs[1] - 1.1, -1.9, P.MUTED, 0.04, 0.16, 0.4)
        dl = st.text("D", xs[1], -2.25, 0.24, P.MUTED, 0.4, kind="bold")
        st.fade_in([dt, dl] + dd, s[2] + 2.0, 0.5)
        # tension
        t3 = st.text("TENSION: own weight", xs[2], 3.35, 0.24, P.PORE, 0.3, kind="bold")
        rod = st.rect(xs[2], 2.7, 0.5, 4.2, P.STEEL, 0.2, anchor="t")
        cpl = [st.rect(xs[2], 0.2, 0.7, 0.35, P.WARN, 0.3), st.rect(xs[2], -1.4, 0.7, 0.35, P.WARN, 0.3)]
        arr = st.arrow(xs[2] + 0.9, -2.2, xs[2] + 0.9, -3.0, P.PORE, 0.12, 0.35, 0.3)
        st.fade_in([t3, rod] + cpl + arr, s[3], 0.5)
        st.scale_to(rod, s[3] + 1.0, s[3] + 3.0, sy=4.5)
        cn = st.text("limited by the pipe body\nand, usually, the connection", xs[2], -3.2, 0.2, P.TEXT, 0.4, kind="bold")
        st.fade_in(cn, s[3] + 2.0, 0.5)
        st.recolor(cpl, s[3] + 2.0, s[3] + 3.0, P.BAD)


# ---------------------------------------------------------------- 5.03 load cases
def beat_loads(st, tl):
    b = tl["5.03"]
    s = b.sent
    with st.span(b.start, b.end):
        ttl = st.text("the design basis: worst credible cases", 0.8, 3.7, 0.3, P.TEXT, 0.3, kind="bold")
        st.fade_in(ttl, s[0], 0.5)
        xs = (-4.0, 0.9, 5.7)
        names = ["BURST", "COLLAPSE", "TENSION"]
        subs = ["gas kick, shut in at surface", "emptied by lost circulation,\nheavy mud outside", "running in the hole:\noverpull and shock"]
        for i, x in enumerate(xs):
            t = s[1 + i]
            card = st.rect(x, -0.1, 4.4, 6.0, P.PANEL, 0.0)
            tt = st.text(names[i], x, 2.5, 0.28, (P.FRAC, P.COLLAPSE, P.PORE)[i], 0.3, kind="bold")
            ss = st.text(subs[i], x, -2.4, 0.22, P.TEXT, 0.3, kind="bold")
            st.fade_in([card, tt, ss], t, 0.5)
        # burst: casing full of gas, surface pressure arrow
        x = xs[0]
        pipe = [st.rect(x - 0.5, 0.0, 0.08, 3.6, P.STEEL, 0.2), st.rect(x + 0.5, 0.0, 0.08, 3.6, P.STEEL, 0.2)]
        gas = st.rect(x, 0.0, 0.92, 3.6, P.GAS, 0.1, alpha=0.6)
        sp = st.arrow(x, 3.1, x, 2.0, P.FRAC, 0.1, 0.3, 0.4)
        spl = st.text("surface\npressure", x + 0.9, 2.5, 0.2, P.FRAC, 0.4, align="l", kind="bold")
        st.fade_in(pipe + [gas, spl] + sp, s[1] + 0.5, 0.4)
        # collapse: empty casing, mud outside
        x = xs[1]
        mud = [st.rect(x - 0.95, 0.0, 0.8, 3.6, P.MUD, 0.1, alpha=0.8), st.rect(x + 0.95, 0.0, 0.8, 3.6, P.MUD, 0.1, alpha=0.8)]
        pipe2 = [st.rect(x - 0.5, 0.0, 0.08, 3.6, P.STEEL, 0.2), st.rect(x + 0.5, 0.0, 0.08, 3.6, P.STEEL, 0.2)]
        ar = st.arrow(x - 1.35, 0.8, x - 0.62, 0.8, P.COLLAPSE, 0.08, 0.2, 0.4) + st.arrow(x + 1.35, 0.8, x + 0.62, 0.8, P.COLLAPSE, 0.08, 0.2, 0.4)
        em = st.text("empty", x, 0.0, 0.26, P.MUTED, 0.4, kind="bold")
        st.fade_in(mud + pipe2 + [em] + ar, s[2] + 0.5, 0.4)
        # tension: string being run with overpull
        x = xs[2]
        rod = st.rect(x, 2.0, 0.4, 3.6, P.STEEL, 0.2, anchor="t")
        hook = st.arrow(x, 3.4, x, 2.2, P.PORE, 0.12, 0.32, 0.4)
        ov = st.text("overpull + shock", x + 0.5, 2.8, 0.2, P.PORE, 0.4, align="l", kind="bold")
        st.fade_in([rod, ov] + hook, s[3] + 0.5, 0.4)
        st.move(rod, s[3] + 1.5, s[3] + 2.0, dy=0.12)
        st.move(rod, s[3] + 2.0, s[3] + 2.5, dy=-0.12)


# ---------------------------------------------------------------- 5.04 von Mises ellipse
def beat_vme(st, tl):
    b = tl["5.04"]
    s = b.sent
    with st.span(b.start, b.end):
        c = Chart(st, -3.6, -3.0, 5.8, 5.8, (-1.45, 1.45), (-1.45, 1.45))
        fr = c.frame(xticks=[], yticks=[], xlabel="axial load  (tension →)", ylabel="pressure:  collapse ↓   burst ↑", grid=False)
        axh = c.hline(0, P.GRID, 0.02, 0.1)
        axv = c.vline(0, P.GRID, 0.02, 0.1)
        st.fade_in(fr + [axh, axv], b.start, 0.5)
        # s0: uniaxial ratings = a box
        box = [st.rect(c.X(0), c.Y(1), c.X(1) - c.X(-1), 0.05, P.MUTED, 0.2), st.rect(c.X(0), c.Y(-1), c.X(1) - c.X(-1), 0.05, P.MUTED, 0.2),
               st.rect(c.X(1), c.Y(0), 0.05, c.Y(1) - c.Y(-1), P.MUTED, 0.2), st.rect(c.X(-1), c.Y(0), 0.05, c.Y(1) - c.Y(-1), P.MUTED, 0.2)]
        bl = st.text("uniaxial ratings:\neach limit on its own", c.X(-0.55), c.Y(1.25), 0.22, P.MUTED, 0.3, kind="bold")
        st.fade_in(box + [bl], s[0], 0.5)
        # s1/s2: von Mises ellipse
        ell = st.line(vme_points(1.0), P.PORE, 0.08, 0.4, closed=True)
        st.draw_on(ell, s[2], s[2] + 2.5)
        el = pill(st, c.X(-0.6), c.Y(-1.28), "von Mises: all stresses at once", P.PANEL2, P.PORE, 0.22, 0.5)
        st.fade_in(el, s[2] + 1.0, 0.4)
        # design factor ellipse
        df = st.line(vme_points(0.8), P.WARN, 0.05, 0.4, closed=True)
        dfl = st.text("design factor", c.X(0.52), c.Y(0.67), 0.2, P.WARN, 0.5, kind="bold")
        st.fade_in([df, dfl], s[2] + 2.5, 0.5)
        # s3: tension reduces collapse resistance
        x0, x05 = 0.0, 0.5
        y_c0 = (x0 - math.sqrt(4 - 3 * x0 * x0)) / 2
        y_c5 = (x05 - math.sqrt(4 - 3 * x05 * x05)) / 2
        d0 = st.arrow(c.X(0), c.Y(0), c.X(0), c.Y(y_c0), P.COLLAPSE, 0.05, 0.16, 0.5)
        d5 = st.arrow(c.X(x05), c.Y(0), c.X(x05), c.Y(y_c5), P.BAD, 0.05, 0.16, 0.5)
        pt = st.circle(c.X(0.75), c.Y(-0.75), 0.13, P.BAD, 0.6)
        ptl = pill(st, c.X(0.55), c.Y(-1.25), "passes every uniaxial check,\nfails von Mises", P.BAD, "#ffffff", 0.2, 0.7, align="l")
        st.fade_in(d0 + d5, s[3], 0.5)
        st.fade_in([pt] + ptl, s[3] + 1.5, 0.5)
        # right: equations
        e1 = st.text("σ_vme = √ ½ [ (σ_a−σ_θ)² + (σ_θ−σ_r)² + (σ_r−σ_a)² ]", 4.6, 2.2, 0.24, P.TEXT, 0.4, kind="mono", align="c")
        e2 = st.text("design factor = yield / σ_vme", 4.6, 1.4, 0.26, P.WARN, 0.4, kind="mono")
        e3 = st.text("tension reduces\ncollapse resistance", 4.6, -0.8, 0.34, P.BAD, 0.4, kind="bold")
        e4 = st.text("[plane stress, no bending or\nthermal load: simplified]", 4.6, -2.4, 0.18, P.SIM_BADGE, 0.4)
        st.fade_in([e1], s[2], 0.5)
        st.fade_in(e2, s[2] + 2.5, 0.5)
        st.fade_in(e3, s[3] + 0.8, 0.5)
        st.fade_in(e4, s[3] + 2.0, 0.5)


# ---------------------------------------------------------------- 5.05 tapered string
def beat_taper(st, tl):
    b = tl["5.05"]
    s = b.sent
    with st.span(b.start, b.end):
        c = Chart(st, -1.4, -3.0, 5.0, 6.2, (0, 1.3), (0, 3400), invert_y=True)
        fr = c.frame(xticks=[0, 0.5, 1.0], yticks=[0, 1000, 2000, 3000], xlabel="load / capacity", ylabel="depth (m)", fx="{:.1f}")
        zs = list(range(0, 3401, 100))
        ten = c.curve([1.05 - 0.9 * z / 3400 for z in zs], zs, P.PORE, 0.08, 0.4)
        col = c.curve([0.15 + 1.0 * (z / 3400) ** 1.3 for z in zs], zs, P.COLLAPSE, 0.08, 0.4)
        lim = c.vline(1.0, P.BAD, 0.04, 0.3)
        tl_ = c.label(0.98, 400, "tension load", 0.22, P.PORE, "r")
        cl_ = c.label(0.98, 3100, "collapse load", 0.22, P.COLLAPSE, "r")
        ll = c.label(1.02, 1700, "capacity", 0.2, P.BAD, "l")
        st.fade_in(fr + [lim, ll], s[1] - 0.5, 0.5)
        st.draw_on(ten, s[1], s[1] + 2.2)
        st.fade_in(tl_, s[1] + 1.8, 0.3)
        st.draw_on(col, s[1] + 2.2, s[1] + 4.5)
        st.fade_in(cl_, s[1] + 4.0, 0.3)
        tr = st.text("the top: most tension, which cuts collapse capacity", -1.0, 3.8, 0.24, P.WARN, 0.4, kind="bold")
        st.fade_in(tr, s[1] + 0.5, 0.5)
        # the string, colour-coded by wall thickness
        sx = 5.5
        segs = [(0, 900, "#5f7089", "heavy wall"), (900, 2500, "#a9b8cb", "lighter wall"), (2500, 3400, "#5f7089", "heavy wall")]
        yz = lambda z: c.Y(z)
        bars, labs = [], []
        for z0, z1, col_, name in segs:
            w = 0.8 if "heavy" in name else 0.5
            bars.append(st.rect(sx, (yz(z0) + yz(z1)) / 2, w, yz(z0) - yz(z1), col_, 0.3))
            labs.append(st.text(name, sx + 0.7, (yz(z0) + yz(z1)) / 2, 0.22, P.TEXT, 0.4, align="l", kind="bold"))
        st.fade_in(bars + labs, s[2], 0.6)
        tp = st.text("tapered string", sx, 3.7, 0.3, P.TEXT, 0.4, kind="bold")
        st.fade_in(tp, s[2], 0.5)


# ---------------------------------------------------------------- 5.06 connections
def beat_connections(st, tl):
    b = tl["5.06"]
    s = b.sent
    with st.span(b.start, b.end):
        def joint(cx, cy, premium):
            parts = []
            parts.append(st.rect(cx - 1.4, cy, 1.4, 0.9, P.STEEL, 0.2))
            parts.append(st.rect(cx + 1.4, cy, 1.4, 0.9, P.STEEL, 0.2))
            parts.append(st.rect(cx, cy + 0.55, 2.4, 0.3, "#8fa1b8", 0.25))
            parts.append(st.rect(cx, cy - 0.55, 2.4, 0.3, "#8fa1b8", 0.25))
            for i in range(7):
                for sy in (1, -1):
                    parts.append(st.poly([(cx - 1.1 + 0.34 * i, cy + sy * 0.4), (cx - 0.93 + 0.34 * i, cy + sy * 0.28), (cx - 0.76 + 0.34 * i, cy + sy * 0.4)], P.WARN if not premium else "#c9d4e1", 0.3))
            return parts
        card1 = st.rect(-3.9, 1.3, 4.9, 3.3, P.PANEL, 0.0)
        card2 = st.rect(1.9, 1.3, 4.9, 3.3, P.PANEL, 0.0)
        st.fade_in([card1], s[1] - 0.2, 0.4)
        j1 = joint(-3.9, 1.3, False)
        t1 = st.text("threaded coupling", -3.9, 2.75, 0.26, P.TEXT, 0.4, kind="bold")
        st.fade_in(j1 + [t1], s[1], 0.4)
        compound = [st.circle(-3.9 + 0.34 * i - 1.0, 1.3 + (0.4 if i % 2 else -0.4), 0.06, P.OIL, 0.5) for i in range(7)]
        cl = st.text("thread compound seals the spiral gap", -3.9, 0.15, 0.2, P.OIL, 0.4, kind="bold")
        st.fade_in(compound + [cl], s[1] + 1.0, 0.4)
        # premium connection
        st.fade_in([card2], s[2] - 0.2, 0.4)
        j2 = joint(1.9, 1.3, True)
        t2 = st.text("premium connection", 1.9, 2.75, 0.26, P.TEXT, 0.4, kind="bold")
        st.fade_in(j2 + [t2], s[2], 0.4)
        seal = st.ring(1.9, 1.3, 0.28, 0.07, P.SAFE, 0.5)
        sh = st.rect(1.9 + 1.12, 1.3, 0.14, 0.9, P.WARN, 0.5)
        sl = st.text("metal-to-metal seal", 1.9, 0.5, 0.2, P.SAFE, 0.5, kind="bold")
        shl = st.text("torque shoulder", 3.3, 0.5, 0.2, P.WARN, 0.5, kind="bold")
        st.fade_in([seal, sh, sl, shl], s[2] + 1.0, 0.4)
        # torque-turn plot
        c = Chart(st, -3.6, -3.0, 4.4, 2.4, (0, 4), (0, 2))
        fr = c.frame(xticks=[], yticks=[], xlabel="turns", ylabel="torque", grid=False)
        xs = [0, 1, 2, 3, 3.3, 3.6, 3.9]
        ys = [0, 0.25, 0.5, 0.75, 1.15, 1.6, 1.9]
        win = st.rect(c.X(3.6), c.Y(1.65), c.X(3.9) - c.X(3.3), c.Y(1.4) - c.Y(1.9), P.SAFE, 0.2, alpha=0.4)
        crv = c.curve(xs, ys, P.PORE, 0.08, 0.4)
        shl2 = c.label(3.05, 0.95, "shoulder", 0.2, P.WARN, "r")
        wl = c.label(2.1, 1.9, "acceptance window", 0.2, P.SAFE, "r")
        st.fade_in(fr + [win, wl], s[2] + 1.5, 0.4)
        st.draw_on(crv, s[2] + 1.8, s[2] + 5.0)
        st.fade_in(shl2, s[2] + 4.2, 0.4)
        end = st.text("the pipe may be fine.\nthe connection is where leaks start.", 3.9, -1.8, 0.3, P.BAD, 0.5, kind="bold")
        st.fade_in(end, s[3], 0.6)


# ---------------------------------------------------------------- 5.07 each string is a barrier element
def beat_barrier_element(st, tl):
    b = tl["5.07"]
    s = b.sent
    with st.span(b.start, b.end):
        ch = Chart(st, -3.0, -3.0, 3.0, 6.3, (0, 1), (0, 4200), invert_y=True)
        col = CasingColumn(st, ch, cx=0.0)
        bk = col.backdrop()
        st.fade_in(bk, b.start, 0.4)
        prog = M.programme()
        objs = []
        for i, p in enumerate(prog):
            objs += col.string(p.name, p.shoe, b.start + 0.6 + 0.5 * i, b.start + 1.8 + 0.5 * i)
        ticks = []
        for i, p in enumerate(prog):
            ticks.append(st.text("✓ tested", 4.2, ch.Y(p.shoe), 0.24, P.SAFE, 0.6, align="l", kind="mono"))
        for i, t in enumerate(ticks):
            st.fade_in(t, s[0] + 2.0 + 0.5 * i, 0.3)
        wb = pill(st, 4.6, 2.4, "well barrier element:\na single object that\nhelps stop flow", P.PANEL2, P.PORE, 0.26, 0.5)
        st.fade_in(wb, s[0] + 0.5, 0.5)
        dd = st.text("documented design\n+ a pressure test to prove it", 4.6, -2.7, 0.24, P.TEXT, 0.5, kind="bold")
        st.fade_in(dd, s[0] + 3.5, 0.5)


def build(st, tl):
    F.header(st, tl)
    F.well_strip(st, 0.0, tl.dur, strings=[p.name for p in M.programme()], marker=M.TD)
    beat_lining(st, tl)
    beat_modes(st, tl)
    beat_loads(st, tl)
    beat_vme(st, tl)
    beat_taper(st, tl)
    beat_connections(st, tl)
    beat_barrier_element(st, tl)
