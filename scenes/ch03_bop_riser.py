"""Ch 3: BOP, riser, and the closed loop. Includes THE BOP CLOSING animation (annular -> pipe rams -> blind shear rams)."""
from __future__ import annotations
import math

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common.shapes import BopStack, WindowChart, pill, loop_move as _loop_move

TITLE = "BOP, riser, and the closed loop"


# ---------------------------------------------------------------- 3.01 BOP lowered on the riser, latches, loop closes
def beat_riser(st, tl):
    b = tl["3.01"]
    s = b.sent
    with st.span(b.start, b.end):
        seabed = -2.5
        cx = -0.5
        sea = st.rect(0.9, 0.7, 13.4, 6.4, P.SEA, -0.1)
        rock = st.rect(0.9, seabed - 0.9, 13.4, 1.8, P.ROCK, -0.1)
        sline = st.rect(0.9, seabed, 13.4, 0.05, P.SEABED, 0.0)
        wh = [st.rect(cx, seabed + 0.25, 1.9, 0.5, P.STEEL_DK, 0.2), st.rect(cx, seabed + 0.55, 1.5, 0.15, "#9aa8bb", 0.22)]
        hole = st.rect(cx, seabed - 0.6, 0.45, 1.2, P.BG, 0.1)
        st.fade_in([sea, rock, sline] + wh + [hole], b.start, 0.5)
        bop = BopStack(st, cx, seabed + 0.5 + 4.2, s=0.95, pipe_top=3.9)
        riser_h = 6.0
        riser = [st.rect(cx - 0.62, bop.y_top + riser_h / 2, 0.08, riser_h, P.STEEL, 0.3), st.rect(cx + 0.62, bop.y_top + riser_h / 2, 0.08, riser_h, P.STEEL, 0.3)]
        rl = st.text("marine riser", cx - 0.85, bop.y_top + 1.0, 0.26, P.TEXT, 0.4, align="r", kind="bold")
        st.fade_in(bop.all + riser, b.start, 0.3)
        st.fade_in(rl, s[1], 0.4)
        stack_group = bop.all + riser + [rl]
        t_land = s[1] + 6.0
        st.move(stack_group, s[1] + 0.8, t_land, dy=-4.2, interp="BEZIER")
        # clamp
        cl = [st.rect(cx - 1.25, seabed + 0.55, 0.3, 0.2, P.WARN, 0.5), st.rect(cx + 1.25, seabed + 0.55, 0.3, 0.2, P.WARN, 0.5)]
        st.fade_in(cl, t_land - 0.3, 0.2)
        st.move(cl[0], t_land, t_land + 0.5, dx=0.35)
        st.move(cl[1], t_land, t_land + 0.5, dx=-0.35)
        lt = st.text("latches onto the wellhead", cx + 2.6, seabed + 0.6, 0.26, P.WARN, 0.5, align="l", kind="bold")
        st.fade_in(lt, t_land, 0.4)
        # mud loop: down the pipe, up the riser
        down = [st.poly([(cx - 0.06, y + 0.1), (cx + 0.06, y + 0.1), (cx, y - 0.05)], P.MUD, 0.5) for y in (3.4, 2.2, 1.0, -0.2)]
        up = [st.poly([(cx + 0.45 - 0.06, y - 0.1), (cx + 0.45 + 0.06, y - 0.1), (cx + 0.45, y + 0.05)], P.MUD, 0.5) for y in (3.0, 1.8, 0.6, -0.6)] + \
             [st.poly([(cx - 0.45 - 0.06, y - 0.1), (cx - 0.45 + 0.06, y - 0.1), (cx - 0.45, y + 0.05)], P.MUD, 0.5) for y in (3.0, 1.8, 0.6, -0.6)]
        st.fade_in(down + up, s[2], 0.3)
        _loop_move(st, down, s[2], b.end - 0.3, -1.2, cycles=5)
        _loop_move(st, up, s[2], b.end - 0.3, 1.2, cycles=5)
        cs = st.text("closed system:\nmud returns up the riser,\nnot into the sea", cx + 3.2, 1.7, 0.3, P.MUD, 0.5, align="l", kind="bold")
        st.fade_in(cs, s[2], 0.5)


# ---------------------------------------------------------------- 3.02 THE BOP CLOSING ANIMATION
def beat_bop(st, tl):
    b = tl["3.02"]
    s = b.sent
    with st.span(b.start, b.end):
        cx = -1.6
        bop = BopStack(st, cx, -3.3, s=1.05, pipe_top=3.9, label=True)
        st.fade_in(bop.all, b.start, 0.6)
        steps = st.text("1  annular  →  2  pipe rams  →  3  blind shear rams", 3.2, 3.4, 0.27, P.MUTED, 0.5, kind="bold")
        st.fade_in(steps, s[0] + 0.5, 0.5)
        # 1: annular squeezes the pipe
        h1 = st.rect(3.2, 2.5, 5.2, 0.55, P.PANEL2, 0.45)
        t1 = st.text("annular: rubber element squeezes around anything in the hole", 3.2, 2.5, 0.22, P.TEXT, 0.5, kind="bold")
        st.fade_in([h1, t1], s[1], 0.4)
        bop.close_annular(s[1] + 0.8, s[1] + 2.8)
        st.fade_out([h1, t1], s[2] - 0.2, 0.3)
        # 2: pipe rams
        h2 = st.rect(3.2, 2.5, 5.2, 0.55, P.PANEL2, 0.45)
        t2 = st.text("pipe rams: steel blocks close around the pipe", 3.2, 2.5, 0.22, P.TEXT, 0.5, kind="bold")
        st.fade_in([h2, t2], s[2], 0.4)
        bop.close_pipe_rams(s[2] + 0.6, s[2] + 2.2)
        st.fade_out([h2, t2], s[3] - 0.2, 0.3)
        # 3: blind shear rams cut the pipe
        h3 = st.rect(3.2, 2.5, 5.2, 0.55, P.PANEL2, 0.45)
        t3 = st.text("blind shear rams: cut the pipe, seal the bore", 3.2, 2.5, 0.22, P.TEXT, 0.5, kind="bold")
        st.fade_in([h3, t3], s[3], 0.4)
        bop.shear(s[3] + 1.4, s[3] + 3.0, t_fall=s[3] + 3.0)
        sealed = st.text("SEALED", cx, bop.y_bsr + 0.0, 0.4, "#0b1220", 0.9, kind="bold")
        st.fade_in(sealed, s[3] + 3.2, 0.4)
        # accumulator
        ax, ay = 4.3, -1.3
        bottle = st.rect(ax, ay, 1.0, 2.0, P.PANEL2, 0.4)
        gas = st.rect(ax, ay + 0.55, 1.0, 0.9, P.PORE, 0.42, alpha=0.8)
        liq = st.rect(ax, ay - 0.55, 1.0, 0.9, P.MUD, 0.42)
        gl = st.text("N₂ gas", ax, ay + 0.55, 0.2, "#0b1220", 0.5, kind="bold")
        ll = st.text("hydraulic\nfluid", ax, ay - 0.55, 0.2, "#0b1220", 0.5, kind="bold")
        line = st.line([(ax - 0.5, ay - 0.9), (cx + 1.5, ay - 0.9), (cx + 1.5, bop.y_ram1)], P.MUD, 0.07, 0.4)
        cap = st.text("accumulator: stored hydraulic energy\ncloses the BOP even without power", ax, ay - 1.7, 0.22, P.MUD, 0.5, kind="bold")
        st.fade_in([bottle, gas, liq, gl, ll, cap], s[4], 0.5)
        st.draw_on(line, s[4] + 0.4, s[4] + 1.6)


# ---------------------------------------------------------------- 3.03 tested before trusted
def beat_test(st, tl):
    b = tl["3.03"]
    s = b.sent
    with st.span(b.start, b.end):
        cx = -3.0
        bop = BopStack(st, cx, -3.2, s=0.9, pipe_top=1.0, label=False)
        st.fade_in(bop.all, b.start, 0.4)
        bop.close_annular(b.start + 0.05, b.start + 0.1)
        bop.close_pipe_rams(b.start + 0.05, b.start + 0.1)
        # pressure gauge dial + trace
        gx, gy = 2.4, 1.3
        dial = st.circle(gx, gy, 1.1, P.PANEL2, 0.3)
        rim = st.ring(gx, gy, 1.1, 0.06, P.MUTED, 0.35)
        needle = st.rect(gx, gy, 0.95, 0.07, P.WARN, 0.5, anchor="l", rot=200)
        hub = st.circle(gx, gy, 0.09, P.TEXT, 0.55)
        lab = st.text("test pressure", gx, gy - 1.5, 0.26, P.TEXT, 0.4, kind="bold")
        st.fade_in([dial, rim, needle, hub, lab], b.start, 0.5)
        st.rotate(needle, b.start + 0.8, b.start + 4.0, -20, interp="LINEAR")
        hold = st.text("HOLD", gx + 2.3, gy, 0.4, P.SAFE, 0.5, kind="bold")
        st.fade_in(hold, b.start + 4.2, 0.4)
        # ticks on each element
        ticks = []
        for name, yy in (("annular", bop.y_ann), ("pipe rams", (bop.y_ram1 + bop.y_ram2) / 2), ("blind shear rams", bop.y_bsr)):
            ticks.append(st.text("✓ " + name, cx + 1.7, yy, 0.3, P.SAFE, 0.6, align="l", kind="mono"))
        st.fade_in(ticks[2:3], b.start + 4.8, 0.3)
        st.fade_in(ticks[1:2], b.start + 5.3, 0.3)
        st.fade_in(ticks[0:1], b.start + 5.8, 0.3)
        note = st.text("an untested barrier is a hope, not a barrier", 2.4, -2.0, 0.28, P.WARN, 0.5, kind="bold")
        st.fade_in(note, s[1], 0.5)


# ---------------------------------------------------------------- 3.04 why the closed loop matters
def beat_closed_loop(st, tl):
    b = tl["3.04"]
    s = b.sent
    with st.span(b.start, b.end):
        xs = (-3.9, 0.9, 5.7)
        titles = ["change the mud weight", "compare flow in vs flow out", "shut the well"]
        for i, x in enumerate(xs):
            card = st.rect(x, 0.2, 4.2, 5.4, P.PANEL, 0.0)
            t = st.text(f"{i + 1}  " + titles[i], x, 2.5, 0.27, P.TEXT, 0.3, kind="bold")
            st.fade_in([card, t], s[i + 1] if i + 1 < len(s) else s[-1], 0.5)
        # 1 mud weight dial -> bottom-hole pressure bar
        trk = st.rect(-4.6, 0.0, 0.1, 3.0, P.GRID, 0.2)
        kn = st.circle(-4.6, -1.0, 0.2, P.MUD, 0.3)
        bar = st.rect(-3.2, -1.5, 0.6, 0.0001, P.MUD, 0.2, anchor="b")
        bf = st.rect(-3.2, 0.0, 0.64, 3.0, P.PANEL2, 0.15)
        l1 = st.text("mud weight", -4.6, 1.8, 0.2, P.MUD, 0.3, kind="bold")
        l2 = st.text("bottom-hole\npressure", -3.2, 1.8, 0.2, P.TEXT, 0.3, kind="bold")
        st.fade_in([trk, kn, bf, l1, l2], s[1] + 0.3, 0.4)
        st.scale_to(bar, s[1] + 0.6, s[1] + 1.2, sy=1.0)
        st.move(kn, s[1] + 1.5, s[1] + 3.2, dy=1.6)
        st.scale_to(bar, s[1] + 1.5, s[1] + 3.2, sy=2.4)
        # 2 flow meters
        fin = st.rect(0.0, -1.5, 0.6, 1.8, P.PORE, 0.2, anchor="b")
        fout = st.rect(1.8, -1.5, 0.6, 1.8, P.PORE, 0.2, anchor="b")
        f1 = st.text("flow in", 0.0, -1.85, 0.2, P.TEXT, 0.3, kind="bold")
        f2 = st.text("flow out", 1.8, -1.85, 0.2, P.TEXT, 0.3, kind="bold")
        st.fade_in([fin, fout, f1, f2], s[2] + 0.3, 0.4)
        st.scale_to(fout, s[2] + 2.5, s[2] + 4.0, sy=2.6)
        dd = st.text("more out than in\n= a kick", 0.9, 1.6, 0.24, P.BAD, 0.4, kind="bold")
        st.fade_in(dd, s[2] + 3.6, 0.4)
        # 3 shut: two blocks close on a pipe
        pipe = st.rect(5.7, -0.4, 0.3, 3.4, P.STEEL, 0.2)
        bl = [st.rect(4.4, -0.4, 0.9, 0.5, P.WARN, 0.3), st.rect(7.0, -0.4, 0.9, 0.5, P.WARN, 0.3)]
        st.fade_in([pipe] + bl, s[3] + 0.2, 0.4)
        st.move(bl[0], s[3] + 1.2, s[3] + 2.4, dx=0.55)
        st.move(bl[1], s[3] + 1.2, s[3] + 2.4, dx=-0.55)


# ---------------------------------------------------------------- 3.05 leak-off test
def beat_lot(st, tl):
    b = tl["3.05"]
    s = b.sent
    with st.span(b.start, b.end):
        # left: shoe + open-hole stub
        cx = -4.6
        rock = st.rect(cx, -0.6, 2.6, 5.2, P.ROCK, 0.0)
        cem = [st.rect(cx - 0.62, 0.7, 0.2, 2.4, P.CEMENT, 0.1), st.rect(cx + 0.62, 0.7, 0.2, 2.4, P.CEMENT, 0.1)]
        csg = [st.rect(cx - 0.45, 0.7, 0.07, 2.4, P.STEEL, 0.2), st.rect(cx + 0.45, 0.7, 0.07, 2.4, P.STEEL, 0.2)]
        bore = st.rect(cx, 0.7, 0.83, 2.4, P.MUD, 0.05)
        stub = st.rect(cx, -1.45, 0.83, 1.6, P.MUD, 0.05)
        shoe = st.poly([(cx - 0.52, -0.5), (cx - 0.38, -0.5), (cx - 0.38, -0.35)], P.WARN, 0.3)
        shoe2 = st.poly([(cx + 0.52, -0.5), (cx + 0.38, -0.5), (cx + 0.38, -0.35)], P.WARN, 0.3)
        st.fade_in([rock, bore, stub] + cem + csg + [shoe, shoe2], b.start, 0.5)
        l_stub = st.text("rock below the\n20 in shoe", cx, -2.7, 0.24, P.TEXT, 0.3, kind="bold")
        st.fade_in(l_stub, s[0] + 1.0, 0.4)
        # closed well + slow pump
        pump = st.arrow(cx, 3.5, cx, 2.0, P.MUD, 0.12, 0.35, 0.3)
        pl = st.text("close the well,\npump slowly", cx + 0.2, 3.5, 0.22, P.MUD, 0.3, align="l", kind="bold")
        st.fade_in(pump + [pl], s[1], 0.5)
        # middle: pressure vs volume
        c = Chart(st, -2.4, -2.5, 3.6, 4.4, (0, 6), (0, 8))
        fr = c.frame(xticks=[], yticks=[], xlabel="volume pumped", ylabel="pressure", grid=False)
        xs = [0, 1, 2, 3, 3.6, 4.3, 5.2, 6]
        ys = [0, 2, 4, 6, 6.9, 7.3, 7.5, 7.6]
        ln = c.curve(xs, ys, P.PORE, 0.07, 0.4)
        dot = c.dot(3.4, 6.6, 0.12, P.WARN, 0.5)
        ll = c.label(3.5, 5.7, "leak-off\npoint", 0.22, P.WARN, "l", dx=0.1)
        el = c.label(0.4, 2.0, "elastic: straight line", 0.2, P.PORE, "l", dx=0.0, dy=0.0)
        st.fade_in(fr, s[1], 0.5)
        st.draw_on(ln, s[2], s[2] + 3.5)
        st.fade_in(el, s[2] + 0.8, 0.4)
        st.fade_in([dot, ll], s[2] + 2.8, 0.4)
        ssc = st.text("like a stress-strain curve", c.X(3.0), c.Y(0.3), 0.2, P.MUTED, 0.5)
        st.fade_in(ssc, s[4], 0.5)
        # right: window chart; the leak-off dot lands on the fracture curve at 1,000 m
        wc = WindowChart(st, x=4.0, y=-3.0, w=3.2, h=6.2)
        ax = wc.axes()
        cu = wc.curves(labels=False)
        st.fade_in(ax + [cu["pp"], cu["fg"]], s[3], 0.5)
        mark = st.circle(c.X(3.4), c.Y(6.6), 0.12, P.WARN, 0.9)
        st.fade_in(mark, s[3] + 0.2, 0.2)
        st.move(mark, s[3] + 1.0, s[3] + 3.0, to=(wc.c.X(M.fg(1000)), wc.c.Y(1000)))
        lab = st.text("measured: the model\nfracture line was right", wc.c.X(M.fg(1000)) - 0.2, wc.c.Y(1000) + 0.6, 0.18, P.WARN, 0.9, align="r", kind="bold")
        st.fade_in(lab, s[4] + 0.5, 0.5)


def build(st, tl):
    F.header(st, tl)
    F.well_strip(st, 0.0, tl.dur, strings=["30in conductor", "20in surface casing"], marker=1000)
    beat_riser(st, tl)
    beat_bop(st, tl)
    beat_test(st, tl)
    beat_closed_loop(st, tl)
    beat_lot(st, tl)
