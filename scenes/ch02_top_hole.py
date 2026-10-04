"""Ch 2: Top hole: drilling with no safety net (riserless drilling, spud, conductor, surface casing, cement, wellhead)."""
from __future__ import annotations
import math
import random

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.shapes import Cutaway, pill, loop_move

TITLE = "Top hole: drilling with no safety net"
SEABED_Y = 0.6          # world y of the seabed in the cutaway scenes (sea above, rock below)


def _earth(st, x0=-6.0, x1=7.7, top=3.9, bottom=-3.5, seabed=SEABED_Y):
    cx, w = (x0 + x1) / 2, x1 - x0
    sea = st.rect(cx, (top + seabed) / 2, w, top - seabed, P.SEA, 0.0)
    rock = st.rect(cx, (seabed + bottom) / 2, w, seabed - bottom, P.ROCK, 0.0)
    line = st.rect(cx, seabed, w, 0.05, P.SEABED, 0.06)
    return [sea, rock, line]


_loop_move = loop_move   # shared helper in scenes/common/shapes.py


# ---------------------------------------------------------------- 2.01 riserless drilling
def beat_riserless(st, tl):
    b = tl["2.01"]
    s = b.sent
    rnd = random.Random(3)
    with st.span(b.start, b.end):
        earth = _earth(st)
        st.fade_in(earth, b.start, 0.5)
        hx = -2.0
        hole = st.rect(hx, (SEABED_Y - 1.7) / 2 + 0.0, 0.8, SEABED_Y + 1.7 - 0.0, P.BG, 0.05)
        hole.location[1] = (SEABED_Y + (-1.7)) / 2
        pipe = st.rect(hx, (3.9 + -1.45) / 2, 0.2, 3.9 + 1.45, P.STEEL, 0.2)
        bit = st.poly([(hx - 0.3, -1.45), (hx + 0.3, -1.45), (hx, -1.78)], P.WARN, 0.25)
        st.fade_in([hole, pipe, bit], s[0], 0.6)
        lab = st.text("drill string", hx - 0.35, 2.4, 0.26, P.TEXT, 0.3, align="r", kind="bold")
        st.fade_in(lab, s[0] + 0.3, 0.4)
        # seawater down the pipe (chevrons) and up the annulus
        down = [st.poly([(hx - 0.07, y + 0.09), (hx + 0.07, y + 0.09), (hx, y - 0.05)], P.PORE, 0.3) for y in (2.9, 1.9, 0.9)]
        st.fade_in(down, s[2], 0.3)
        _loop_move(st, down, s[2], b.end - 0.5, -1.0, cycles=6)
        up = [st.poly([(hx + 0.55 - 0.07, y - 0.09), (hx + 0.55 + 0.07, y - 0.09), (hx + 0.55, y + 0.05)], P.PORE, 0.3) for y in (-1.3, -0.5)] + \
             [st.poly([(hx - 0.55 - 0.07, y - 0.09), (hx - 0.55 + 0.07, y - 0.09), (hx - 0.55, y + 0.05)], P.PORE, 0.3) for y in (-1.3, -0.5)]
        st.fade_in(up, s[2] + 0.5, 0.3)
        _loop_move(st, up, s[2] + 0.5, b.end - 0.5, 1.0, cycles=5)
        sw = st.text("seawater pumped down the pipe", 1.0, 2.6, 0.26, P.PORE, 0.3, align="l", kind="bold")
        st.fade_in(sw, s[2], 0.4)
        # cuttings plume at the seabed
        plume = []
        for i in range(26):
            x = hx + rnd.uniform(-0.2, 0.2)
            c = st.circle(x, SEABED_Y + 0.05, rnd.uniform(0.07, 0.16), "#9aa0a8", 0.4, alpha=0.0)
            plume.append(c)
            t = s[3] + 0.2 * (i % 8)
            st.fade_in(c, t, 0.2)
            st.move(c, t, t + 3.0, dx=rnd.uniform(-2.2, 3.2), dy=rnd.uniform(0.4, 1.8))
            st.fade_out(c, t + 1.8, 1.2)
        pl = st.text("cuttings + seawater spill out at the seabed", 1.6, 1.45, 0.24, P.TEXT, 0.4, align="l", kind="bold")
        st.fade_in(pl, s[3], 0.4)
        # ghost BOP + riser, crossed out
        gh = st.dashed((4.8, 3.5), (4.8, -0.7), P.MUTED, 0.05, 0.2, 0.15, 0.3) + st.dashed((5.6, 3.5), (5.6, -0.7), P.MUTED, 0.05, 0.2, 0.15, 0.3)
        gb = st.dashed((4.5, -0.7), (5.9, -0.7), P.MUTED, 0.05, 0.2, 0.15, 0.3) + st.dashed((4.5, -0.2), (5.9, -0.2), P.MUTED, 0.05, 0.2, 0.15, 0.3)
        x1 = st.line([(4.35, 3.0), (6.05, -0.9)], P.BAD, 0.12, 0.5)
        x2 = st.line([(4.35, -0.9), (6.05, 3.0)], P.BAD, 0.12, 0.5)
        gl = st.text("no riser, no BOP", 5.2, 3.75, 0.28, P.BAD, 0.5, kind="bold")
        st.fade_in(gh + gb + [gl], s[1], 0.5)
        st.draw_on(x1, s[1] + 0.5, s[1] + 1.1)
        st.draw_on(x2, s[1] + 1.0, s[1] + 1.6)
        bp = st.text("BOP: a stack of valves\nthat can close the well", 5.2, -1.6, 0.22, P.MUTED, 0.3)
        st.fade_in(bp, s[1] + 0.8, 0.5)
        ns = st.text("nothing returns to the rig", 5.2, -2.5, 0.24, P.WARN, 0.3, kind="bold")
        st.fade_in(ns, s[4], 0.5)


# ---------------------------------------------------------------- 2.02 why is it allowed?
def beat_why(st, tl):
    b = tl["2.02"]
    s = b.sent
    with st.span(b.start, b.end):
        title = st.text("a kilometre with nothing that can close the well. Why is that allowed?", 0.8, 3.7, 0.3, P.TEXT, 0.3, kind="bold")
        st.fade_in(title, s[0], 0.5)
        # left: shut-in attempt
        for (cx, name) in ((-2.9, "closed in"), (3.6, "left open")):
            sea = st.rect(cx, 2.0, 4.8, 1.2, P.SEA, 0.0)
            rock = st.rect(cx, -0.9, 4.8, 4.6, P.ROCK, 0.0)
            line = st.rect(cx, 1.4, 4.8, 0.05, P.SEABED, 0.06)
            hole = st.rect(cx, -0.5, 0.5, 3.8, P.BG, 0.05)
            st.fade_in([sea, rock, line, hole, st.text(name, cx, 2.75, 0.3, P.TEXT, 0.3, kind="bold")], s[1] - 0.5 if cx < 0 else s[2], 0.5)
        # shut-in: gauge climbs, crack to seabed
        gauge = st.rect(-5.0, -2.6, 0.3, 0.0001, P.FRAC, 0.2, anchor="b")
        gframe = st.rect(-5.0, -0.7, 0.34, 3.8, P.PANEL2, 0.15)
        glabel = st.text("pressure", -5.0, 1.45, 0.2, P.MUTED, 0.2)
        st.fade_in([gframe, glabel], s[1], 0.4)
        st.scale_to(gauge, s[2], s[2] + 4.0, sy=3.4, interp="LINEAR")
        crack = st.line([(-2.9, -2.0), (-2.5, -1.2), (-2.9, -0.3), (-2.4, 0.5), (-2.8, 1.4)], P.BAD, 0.1, 0.4)
        st.draw_on(crack, s[2] + 2.8, s[2] + 4.4)
        br = st.text("cracks the weak rock\nand breaks out beside the well", -2.9, -3.15, 0.22, P.BAD, 0.4, kind="bold")
        st.fade_in(br, s[2] + 3.6, 0.5)
        # open: tank of kill mud + pump arrow
        tank = st.rect(5.9, 0.4, 1.3, 1.1, P.KILL_MUD, 0.3)
        tl_ = st.text("kill mud\nready to pump", 5.9, 0.4, 0.2, "#0b1220", 0.4, kind="bold")
        pa = st.arrow(5.25, 0.4, 3.9, 0.4, P.KILL_MUD, 0.1, 0.3, 0.3)
        st.fade_in([tank, tl_] + pa, s[4], 0.5)
        ok = st.text("defences: a survey for gas first,\nand heavy mud ready to pump", 3.6, -3.15, 0.22, P.SAFE, 0.4, kind="bold")
        st.fade_in(ok, s[4] + 0.8, 0.5)
        weak = st.text("near the seabed the rock is weak:\nlittle weight above it except water", 0.8, 3.1, 0.22, P.WARN, 0.4)
        st.fade_in(weak, s[2] - 0.2, 0.5)


# ---------------------------------------------------------------- 2.03 spud, guide base, conductor
def beat_conductor(st, tl):
    b = tl["2.03"]
    s = b.sent
    with st.span(b.start, b.end):
        earth = _earth(st, -6.0, 1.2, 3.9, -3.5)
        st.fade_in(earth, b.start, 0.5)
        # guide base lands
        gb = [st.rect(-2.6, SEABED_Y + 0.08, 2.4, 0.16, P.STEEL_DK, 0.3), st.rect(-3.7, SEABED_Y + 0.22, 0.12, 0.3, P.STEEL_DK, 0.3), st.rect(-1.5, SEABED_Y + 0.22, 0.12, 0.3, P.STEEL_DK, 0.3)]
        for o in gb:
            st.move(o, s[1], s[1] + 1.4, dy=0.0)
        st.fade_in(gb, s[1], 0.6)
        gl = st.text("guide base", -2.6, SEABED_Y + 0.7, 0.24, P.TEXT, 0.4, kind="bold")
        st.fade_in(gl, s[1] + 0.4, 0.4)
        # conductor lowered
        cond = st.rect(-2.6, 3.9, 0.5, 4.7, P.STEEL, 0.25, anchor="t")
        st.fade_in(cond, s[2] - 0.3, 0.3)
        st.move(cond, s[2], s[2] + 3.0, dy=-3.1)
        jets = [st.arrow(-2.6 + dx, -1.2, -2.6 + dx * 1.7, -1.7, P.PORE, 0.05, 0.16, 0.4) for dx in (-0.2, 0.2)]
        st.fade_in([j for jj in jets for j in jj], s[2] + 2.8, 0.4)
        cl = st.text("30 in conductor:\njetted in, or drilled and cemented", -2.6, 2.4, 0.24, P.TEXT, 0.4, kind="bold")
        st.fade_in(cl, s[2], 0.5)
        # free-body: the conductor as a pile
        rx = 4.3
        soil = st.rect(rx, -1.5, 4.0, 4.0, P.SEABED, 0.0)
        sea = st.rect(rx, 2.4, 4.0, 2.8, P.SEA, 0.0)
        pile = st.rect(rx, 0.0, 0.42, 4.2, P.STEEL, 0.2)
        stack = st.rect(rx, 2.3, 1.5, 1.0, P.PANEL2, 0.3)
        stl = st.text("wellhead + BOP\nhundreds of tonnes", rx, 2.3, 0.2, P.TEXT, 0.4, kind="bold")
        wt = st.arrow(rx, 3.9, rx, 2.85, P.WARN, 0.1, 0.3, 0.4)
        fr = []
        for y in (0.0, -0.7, -1.4, -2.1):
            fr += st.arrow(rx - 0.55, y - 0.35, rx - 0.55, y + 0.1, P.SAFE, 0.05, 0.16, 0.3) + st.arrow(rx + 0.55, y - 0.35, rx + 0.55, y + 0.1, P.SAFE, 0.05, 0.16, 0.3)
        sp = []
        for y in (-0.3, -1.0, -1.7):
            sp += [st.line([(rx - 1.1, y), (rx - 0.9, y + 0.07), (rx - 0.75, y - 0.07), (rx - 0.6, y)], P.WARN, 0.04, 0.3),
                   st.line([(rx + 1.1, y), (rx + 0.9, y + 0.07), (rx + 0.75, y - 0.07), (rx + 0.6, y)], P.WARN, 0.04, 0.3)]
        wave = st.arrow(rx - 1.9, 2.3, rx - 0.85, 2.3, P.PORE, 0.1, 0.3, 0.4)
        wl = st.text("riser pulls sideways\nwith every wave", rx - 1.5, 3.0, 0.2, P.PORE, 0.4, kind="bold")
        fl = st.text("soil friction carries the weight\nsoil springs resist the bending", rx, -3.2, 0.2, P.SAFE, 0.4, kind="bold")
        st.fade_in([soil, sea, pile, stack, stl] + wt, s[3] + 0.3, 0.6)
        st.fade_in(fr + sp + wave + [wl, fl], s[3] + 2.0, 0.6)
        pl = st.text("a pile in mud", rx, 3.75, 0.3, P.TEXT, 0.4, kind="bold")
        st.fade_in(pl, s[3] + 1.0, 0.4)


# ---------------------------------------------------------------- 2.04 surface casing + wellhead housing
def beat_surface_casing(st, tl):
    b = tl["2.04"]
    s = b.sent
    with st.span(b.start, b.end):
        earth = _earth(st, -6.0, 7.7, 3.9, -3.6)
        st.fade_in(earth, b.start, 0.5)
        cx = 0.0
        # conductor (short) with its housing
        cw = 1.0
        cond = [st.rect(cx - cw / 2, SEABED_Y - 0.35, 0.08, 1.2, P.STEEL_DK, 0.2), st.rect(cx + cw / 2, SEABED_Y - 0.35, 0.08, 1.2, P.STEEL_DK, 0.2),
                st.rect(cx, SEABED_Y + 0.15, cw + 0.55, 0.3, P.STEEL_DK, 0.25)]
        st.fade_in(cond, b.start + 0.3, 0.4)
        # 26 in hole drilled down to 1,000 m
        hole = st.rect(cx, SEABED_Y - 0.2, 0.84, 0.0001, P.BG, 0.1, anchor="t")
        st.scale_to(hole, s[0], s[0] + 3.0, sy=3.9, interp="LINEAR")
        hl = st.text("26 in hole to about 1,000 m", 3.3, -1.5, 0.26, P.TEXT, 0.3, kind="bold")
        st.fade_in(hl, s[0] + 0.5, 0.4)
        scale = st.text("(not to scale)", 3.3, -2.0, 0.18, P.MUTED, 0.3)
        st.fade_in(scale, s[0] + 0.5, 0.4)
        # 20 in casing + high-pressure wellhead housing lowered in
        w = 0.7
        c20 = [st.rect(cx - w / 2, 4.9, 0.08, 6.5, P.STEEL, 0.3), st.rect(cx + w / 2, 4.9, 0.08, 6.5, P.STEEL, 0.3)]
        hh = st.rect(cx, 4.55, 0.95, 0.5, P.STEEL, 0.4)
        parts = c20 + [hh]
        st.fade_in(parts, s[1] - 0.2, 0.3)
        # lowered so that the housing lands in the conductor housing at seabed
        st.move(parts, s[1], s[1] + 3.5, dy=-(4.55 - (SEABED_Y + 0.15)) )
        l20 = st.text("20 in surface casing", 3.3, 1.9, 0.26, P.TEXT, 0.4, kind="bold")
        lh = st.text("high-pressure wellhead housing:\nthe first hardware that can contain pressure", 3.3, 0.9, 0.22, P.WARN, 0.4, kind="bold")
        st.fade_in(l20, s[1] + 0.5, 0.4)
        st.fade_in(lh, s[2] + 0.4, 0.5)
        ar = st.arrow(2.4, 0.9, 0.6, SEABED_Y + 0.15, P.WARN, 0.05, 0.2, 0.4)
        st.fade_in(ar, s[2] + 0.6, 0.4)


# ---------------------------------------------------------------- 2.05 cementing the surface casing
def beat_cement(st, tl):
    b = tl["2.05"]
    s = b.sent
    with st.span(b.start, b.end):
        y_top, y_bot, y_sb = 3.7, -3.4, 1.6          # screen y of top of pipe, bottom of hole, seabed
        cx = -1.8
        sea = st.rect(-0.2, (y_top + y_sb) / 2, 11.0, y_top - y_sb, P.SEA, -0.05)
        cut = Cutaway(st, cx, y_sb, y_bot, hole_w=2.2, pipe_w=1.0, rock_w=3.0)
        base = cut.draw(pipe_bottom=y_bot + 0.45)
        pipe_up = st.rect(cx, (y_top + y_sb) / 2, 1.0, y_top - y_sb, P.SEA, 0.01)
        pw = [st.rect(cx - 0.465, (y_top + y_sb) / 2, 0.07, y_top - y_sb, P.STEEL, 0.22), st.rect(cx + 0.465, (y_top + y_sb) / 2, 0.07, y_top - y_sb, P.STEEL, 0.22)]
        st.fade_in([sea] + base + [pipe_up] + pw, b.start, 0.5)
        mud_b = cut.static_bore(P.MUD, y_sb, y_bot + 0.45, 0.02)
        mud_l = cut.static_gap("l", P.MUD, y_sb, y_bot + 0.45, 0.02)
        mud_r = cut.static_gap("r", P.MUD, y_sb, y_bot + 0.45, 0.02)
        shoe = st.poly([(cx - 0.55, y_bot + 0.45), (cx + 0.55, y_bot + 0.45), (cx + 0.4, y_bot + 0.3), (cx - 0.4, y_bot + 0.3)], P.STEEL_DK, 0.3)
        st.fade_in([mud_b, mud_l, mud_r, shoe], b.start, 0.5)
        # cement goes down the inside, around the shoe, up the outside
        t_down0, t_down1 = s[0] + 0.5, s[0] + 3.5
        c_in = st.rect(cx, y_top, 0.86, 0.0001, P.CEMENT, 0.12, anchor="t")
        st.scale_to(c_in, t_down0, t_down1, sy=y_top - (y_bot + 0.45), interp="LINEAR")
        cl = cut.fill_gap("l", P.CEMENT, y_bot + 0.45, y_sb, t_down1, t_down1 + 3.0, 0.12, interp="LINEAR")
        cr = cut.fill_gap("r", P.CEMENT, y_bot + 0.45, y_sb, t_down1, t_down1 + 3.0, 0.12, interp="LINEAR")
        lab_in = st.text("down the inside…", cx + 1.9, 2.4, 0.26, P.CEMENT, 0.3, align="l", kind="bold")
        lab_out = st.text("…and up the outside", cx + 1.9, -0.8, 0.26, P.CEMENT, 0.3, align="l", kind="bold")
        st.fade_in(lab_in, t_down0, 0.4)
        st.fade_in(lab_out, t_down1 + 0.5, 0.4)
        # returns at the seabed + ROV
        puff = []
        for i in range(10):
            c = st.circle(cx + (-0.7 + 0.14 * i), y_sb + 0.1, 0.1, P.CEMENT, 0.4, alpha=0.0)
            puff.append(c)
            t = t_down1 + 3.0 + 0.08 * i
            st.fade_in(c, t, 0.15)
            st.move(c, t, t + 1.4, dx=-0.5 + 0.1 * i, dy=0.7 + 0.05 * i)
            st.fade_out(c, t + 0.8, 0.6)
        rov = [st.rect(3.6, 2.6, 1.3, 0.6, P.WARN, 0.4), st.circle(3.0, 2.6, 0.2, P.TEXT, 0.45), st.text("ROV", 3.7, 2.6, 0.22, "#0b1220", 0.45, kind="bold")]
        cone = st.poly([(3.0, 2.6), (cx + 0.2, y_sb + 0.1), (cx + 1.0, y_sb + 0.45)], P.TEXT, 0.35, 0.18)
        rl = st.text("returns at the seabed:\nthe ROV camera sees grey cement", 4.3, 0.9, 0.24, P.TEXT, 0.4, align="c", kind="bold")
        st.fade_in(rov + [cone, rl], t_down1 + 2.6, 0.5)
        an = st.text("annulus", cx - 1.6, -1.8, 0.24, P.TEXT, 0.4, align="r", kind="bold")
        ar = st.arrow(cx - 1.55, -1.8, cx - 0.95, -1.8, P.TEXT, 0.04, 0.16, 0.4)
        st.fade_in([an] + ar, s[2], 0.4)
        jobs = st.text("supports the wellhead + seals shallow zones", 4.3, -2.6, 0.24, P.SAFE, 0.4, kind="bold")
        st.fade_in(jobs, s[3], 0.5)


# ---------------------------------------------------------------- 2.06 wellhead = nested seats
def beat_wellhead(st, tl):
    b = tl["2.06"]
    s = b.sent
    with st.span(b.start, b.end):
        cx = -1.0
        # outer conductor housing, inner 20 in housing, casing hanger, seal
        outer = [st.rect(cx - 1.35, 0.4, 0.4, 2.4, P.STEEL_DK, 0.2), st.rect(cx + 1.35, 0.4, 0.4, 2.4, P.STEEL_DK, 0.2),
                 st.rect(cx - 1.45, 1.8, 0.6, 0.3, P.STEEL_DK, 0.25), st.rect(cx + 1.45, 1.8, 0.6, 0.3, P.STEEL_DK, 0.25)]
        inner_pos = [st.rect(cx - 0.95, 0.9, 0.35, 2.0, "#9aa8bb", 0.3), st.rect(cx + 0.95, 0.9, 0.35, 2.0, "#9aa8bb", 0.3)]
        inner = [st.rect(cx - 0.45, 3.4, 0.3, 2.0, "#9aa8bb", 0.3), st.rect(cx + 0.45, 3.4, 0.3, 2.0, "#9aa8bb", 0.3)]
        st.fade_in(outer, b.start, 0.5)
        l1 = st.text("conductor housing", cx + 2.1, 1.8, 0.22, P.TEXT, 0.4, align="l", kind="bold")
        l2 = st.text("20 in housing lands inside it", cx + 2.1, 0.9, 0.22, P.TEXT, 0.4, align="l", kind="bold")
        st.fade_in([l1], b.start + 0.3, 0.4)
        # inner housing drops into the outer one
        ih = [st.rect(cx - 0.85, 4.2, 0.4, 1.8, "#9aa8bb", 0.3), st.rect(cx + 0.85, 4.2, 0.4, 1.8, "#9aa8bb", 0.3), st.rect(cx, 3.35, 2.1, 0.3, "#9aa8bb", 0.3)]
        st.fade_in(ih, s[0], 0.4)
        st.move(ih, s[0] + 0.3, s[0] + 2.0, dy=-2.4)
        st.fade_in(l2, s[0] + 1.5, 0.4)
        # casing hanger with seal
        hg = [st.rect(cx - 0.55, 4.2, 0.35, 0.5, "#c4d0de", 0.4), st.rect(cx + 0.55, 4.2, 0.35, 0.5, "#c4d0de", 0.4)]
        sl = [st.rect(cx - 0.35, 4.2, 0.1, 0.4, P.WARN, 0.45), st.rect(cx + 0.35, 4.2, 0.1, 0.4, P.WARN, 0.45)]
        st.fade_in(hg + sl, s[1] - 0.2, 0.3)
        st.move(hg + sl, s[1], s[1] + 1.6, dy=-3.0)
        hl = st.text("casing hanger + seal\ncloses the gap behind each string", cx + 2.1, -0.3, 0.22, P.WARN, 0.4, align="l", kind="bold")
        st.fade_in(hl, s[1] + 1.2, 0.4)
        # sway for fatigue
        t0 = s[2]
        everything = outer + ih + hg + sl + [l1, l2]
        for i in range(6):
            st.move(everything, t0 + i * 1.6, t0 + i * 1.6 + 0.8, dx=0.12, interp="BEZIER")
            st.move(everything, t0 + i * 1.6 + 0.8, t0 + i * 1.6 + 1.6, dx=-0.12, interp="BEZIER")
        ft = st.text("waves load this stack every few seconds:\nfatigue of wellhead and conductor drives the design", cx, -2.6, 0.26, P.PORE, 0.4, kind="bold")
        st.fade_in(ft, s[2] + 0.5, 0.5)


def build(st, tl):
    F.header(st, tl)
    F.well_strip(st, 0.0, tl["2.03"].start + 4.0, strings=[], marker=M.WATER_DEPTH + 1)
    F.well_strip(st, tl["2.03"].start + 4.0, tl["2.04"].start + 3.5, strings=["30in conductor"], marker=M.WATER_DEPTH + 90)
    F.well_strip(st, tl["2.04"].start + 3.5, tl.dur, strings=["30in conductor", "20in surface casing"], marker=1000)
    beat_riserless(st, tl)
    beat_why(st, tl)
    beat_conductor(st, tl)
    beat_surface_casing(st, tl)
    beat_cement(st, tl)
    beat_wellhead(st, tl)
