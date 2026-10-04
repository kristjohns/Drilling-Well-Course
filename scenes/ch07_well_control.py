"""Ch 7: Well control and barriers. Includes THE KICK PROPAGATING UP THE ANNULUS (Boyle's law, derived)."""
from __future__ import annotations
import math

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common.shapes import Cutaway, WindowChart, BopStack, pill, loop_move

TITLE = "Well control and barriers"

# one consistent set of numbers for the kill-sheet beats (illustrative, derived from the well model)
MW_OLD = 1.50
TVD_KILL = 4000.0
P_PORE = M.bar(TVD_KILL, M.pp(TVD_KILL))
P_HYD = M.bar(TVD_KILL, MW_OLD)
SIDPP = P_PORE - P_HYD
KMW = MW_OLD + SIDPP / (M.G * TVD_KILL)


# ---------------------------------------------------------------- 7.01 the window lied
def beat_lied(st, tl):
    b = tl["7.01"]
    s = b.sent
    with st.span(b.start, b.end):
        wc = WindowChart(st, x=-5.3, y=-3.0, w=5.6, h=6.3)
        objs = wc.axes() + [wc.curves()["pp"], wc.objs["fg"], wc.objs["pp_lbl"], wc.objs["fg_lbl"], wc.band()]
        st.fade_in(objs, b.start, 0.5)
        c = wc.c
        mw = st.rect(c.X(1.45), (c.Y(2500) + c.Y(4100)) / 2, 0.08, c.Y(2500) - c.Y(4100), P.MUD, 0.5)
        mwl = pill(st, c.X(1.45) - 0.15, c.Y(4100) + 0.4, "mud weight", P.PANEL2, P.MUD, 0.2, 0.6, align="r")
        st.fade_in([mw] + mwl, s[0], 0.5)
        zs = [z for z in range(2400, 4201, 100)]
        actual = st.line([c.pt(M.pp(z) + (0.12 if z > 3000 else 0.12 * (z - 2400) / 600), z) for z in zs], P.BAD, 0.07, 0.55)
        al = pill(st, c.X(1.75), c.Y(3000), "actual pore pressure:\nhigher than forecast", P.BAD, "#ffffff", 0.2, 0.7, align="c")
        st.draw_on(actual, s[1], s[1] + 2.5)
        st.fade_in(al, s[1] + 1.5, 0.5)
        # syringe + influx
        bx = 4.2
        barrel = st.rect(bx, 1.4, 1.2, 0.5, P.PANEL2, 0.3)
        plunger = st.rect(bx + 1.0, 1.4, 1.4, 0.12, P.STEEL, 0.4)
        handle = st.rect(bx + 1.75, 1.4, 0.12, 0.7, P.STEEL, 0.4)
        liq = st.rect(bx - 0.2, 1.4, 0.8, 0.4, P.WATER, 0.35)
        sl = st.text("swab: pulling the pipe\nsucks fluid in, like a syringe", bx + 0.6, 2.3, 0.22, P.TEXT, 0.4, kind="bold")
        st.fade_in([barrel, plunger, handle, liq, sl], s[1] + 0.5, 0.5)
        st.move([plunger, handle], s[1] + 1.5, s[1] + 3.0, dx=0.6)
        # influx into the hole
        hole = st.rect(bx, -1.7, 1.0, 3.4, P.MUD, 0.2)
        walls = [st.rect(bx - 0.8, -1.7, 0.6, 3.4, P.ROCK, 0.15), st.rect(bx + 0.8, -1.7, 0.6, 3.4, P.ROCK, 0.15)]
        inf = []
        for y in (-2.9, -2.1, -1.3):
            inf += st.arrow(bx - 1.3, y, bx - 0.45, y, P.WATER, 0.08, 0.22, 0.4) + st.arrow(bx + 1.3, y, bx + 0.45, y, P.WATER, 0.08, 0.22, 0.4)
        st.fade_in([hole] + walls, s[2] - 0.2, 0.4)
        st.fade_in(inf, s[2], 0.5)
        il = st.text("formation fluid enters the well", bx, -3.5, 0.24, P.WATER, 0.4, kind="bold")
        st.fade_in(il, s[2], 0.5)
        kb = pill(st, bx, 3.4, "kick  →  blowout", P.BAD, "#ffffff", 0.3, 0.6)
        st.fade_in(kb, s[3], 0.5)


# ---------------------------------------------------------------- 7.02 THE KICK PROPAGATING UP THE ANNULUS
def _bubble_r(f, r0=0.07):
    """Radius of a free-gas bubble at fractional height f (0 = bottom, 1 = surface); Boyle: V ~ 1/p, r ~ p^(-1/3)."""
    p_bot = 1.0 + M.bar(4000, 1.5)
    p = 1.0 + M.bar(4000 * (1 - f), 1.5)
    return r0 * (p_bot / p) ** (1.0 / 3.0)


def beat_kick(st, tl):
    b = tl["7.02"]
    s = b.sent
    with st.span(b.start, b.end):
        yt, yb = 3.2, -3.1
        H = yt - yb
        cols = {}
        for name, cx in (("free", -4.4), ("dissolved", -1.2)):
            cut = Cutaway(st, cx, yt, yb, hole_w=1.5, pipe_w=0.5, rock_w=0.9, wall=0.05)
            base = cut.draw(pipe_bottom=yb + 0.4)
            mud = [cut.static_gap("l", P.MUD, yt, yb, 0.03), cut.static_gap("r", P.MUD, yt, yb, 0.03), cut.static_bore(P.MUD, yt, yb + 0.4, 0.03)]
            hd = st.text("water-based mud:\ngas stays free" if name == "free" else "oil-based mud:\ngas dissolves, hides", cx, 3.85, 0.22, P.TEXT, 0.4, kind="bold")
            st.fade_in(base + mud + [hd], b.start, 0.5)
            cols[name] = cut
        # scale labels
        sl = [st.text("surface", -6.0, yt - 0.1, 0.18, P.MUTED, 0.3, align="l"), st.text("4 km", -6.0, yb + 0.2, 0.18, P.MUTED, 0.3, align="l")]
        st.fade_in(sl, b.start, 0.4)
        # ---- free gas: bubble rises and expands (Boyle). Keyframes at fractions of the trip.
        cutF = cols["free"]
        gx = (cutF.gap_r[0] + cutF.gap_r[1]) / 2
        T0, T1 = s[1] + 0.2, s[2] + 1.0
        bub = st.ellipse(gx, yb + 0.35, 0.07, 0.07, P.GAS, 0.5)
        fracs = [0.0, 0.3, 0.6, 0.8, 0.9, 0.95, 0.98, 1.0]
        # position: linear in time; radius follows Boyle's law at each fraction of the trip
        st.move(bub, T0, T1, to=(gx, yt - 0.15), interp="LINEAR")
        for f in fracs[1:]:
            t = T0 + f * (T1 - T0)
            r = _bubble_r(f)
            st.scale_to(bub, t - 0.0, t + 0.01, sx=min(r, 0.34), sy=r, interp="LINEAR")
        st.fade_in(bub, s[1] + 0.1, 0.3)
        lab1 = st.text("tiny at the bottom", cutF.hole[1] + 0.2, yb + 0.5, 0.2, P.GAS, 0.5, align="l", kind="bold")
        lab2 = st.text("enormous at the top", cutF.hole[1] + 0.2, yt - 0.9, 0.2, P.GAS, 0.5, align="l", kind="bold")
        st.fade_in(lab1, T0, 0.4)
        st.fade_in(lab2, T1 - 2.0, 0.4)
        # ---- dissolved gas in oil-based mud: faint until the flash point near the top
        cutD = cols["dissolved"]
        dx = (cutD.gap_r[0] + cutD.gap_r[1]) / 2
        T2, T3 = s[2] + 0.2, b.end - 1.0
        ghost = st.ellipse(dx, yb + 0.35, 0.07, 0.07, P.GAS, 0.5, alpha=0.18)
        st.fade_in(ghost, T2, 0.3)
        st.move(ghost, T2, T3, to=(dx, yt - 0.15), interp="LINEAR")
        flash = T2 + 0.93 * (T3 - T2)
        real = st.ellipse(dx, yt - 0.9, 0.05, 0.05, P.GAS, 0.55, alpha=0.0)
        st.fade_in(real, flash, 0.15)
        st.scale_to(real, flash, T3, sx=0.34, sy=0.9, interp="LINEAR")
        st.move(real, flash, T3, dy=0.6, interp="LINEAR")
        fl = pill(st, cutD.hole[1] + 1.2, yt - 1.4, "gas flashes out of\nsolution near the top", P.PANEL2, P.GAS, 0.2, 0.6, align="l")
        st.fade_in(fl, flash - 0.3, 0.4)
        # ---- pit-gain trace derived from the same formula
        c = Chart(st, 2.0, -2.5, 5.4, 4.6, (0, 1), (0, 1))
        fr = c.frame(xticks=[], yticks=[], xlabel="gas position (bottom → surface)", ylabel="pit gain", grid=False)
        xs = [i / 40 for i in range(41)]
        gain_free = [(_bubble_r(x) / _bubble_r(1.0)) ** 3 for x in xs]
        gain_diss = [0.0 if x < 0.93 else ((x - 0.93) / 0.07) ** 2 for x in xs]
        t1 = c.curve(xs, gain_free, P.GAS, 0.08, 0.4)
        t2 = c.curve(xs, gain_diss, P.WARN, 0.07, 0.45)
        c.label(0.55, 0.9, "free gas", 0.2, P.GAS, "l")
        c.label(0.55, 0.78, "dissolved gas", 0.2, P.WARN, "l")
        st.fade_in(fr, s[1], 0.4)
        st.draw_on(t1, T0, T1)
        st.draw_on(t2, T2, T3)
        note = st.text("detectable only at the very end:\nthe pit barely moves until the last stretch", 4.7, 3.2, 0.2, P.TEXT, 0.4, kind="bold")
        st.fade_in(note, T1 - 1.5, 0.5)


# ---------------------------------------------------------------- 7.03 detection dashboard
def beat_detect(st, tl):
    b = tl["7.03"]
    s = b.sent
    with st.span(b.start, b.end):
        pos = [(-2.9, 1.5), (3.0, 1.5), (-2.9, -2.0), (3.0, -2.0)]
        titles = ["flow out > flow in", "rising pit level", "flow check: pumps off,\nwell still flowing", "drilling break"]
        starts = [s[1], s[2], s[3], s[4]]
        cards, frames = [], []
        for (x, y), t, ts in zip(pos, titles, starts):
            card = st.rect(x, y, 5.6, 3.1, P.PANEL, 0.0)
            tt = st.text(t, x, y + 1.15, 0.25, P.TEXT, 0.3, kind="bold")
            st.fade_in([card, tt], ts, 0.4)
            frames.append(card)
        # 1 flow in/out bars
        x, y = pos[0]
        fin = st.rect(x - 0.8, y - 1.2, 0.8, 1.2, P.PORE, 0.2, anchor="b")
        fout = st.rect(x + 0.8, y - 1.2, 0.8, 1.2, P.PORE, 0.2, anchor="b")
        li = st.text("in", x - 0.8, y - 1.45, 0.2, P.TEXT, 0.3)
        lo = st.text("out", x + 0.8, y - 1.45, 0.2, P.TEXT, 0.3)
        st.fade_in([fin, fout, li, lo], s[1] + 0.3, 0.4)
        st.scale_to(fout, s[1] + 1.5, s[1] + 2.5, sy=1.9)
        st.recolor(fout, s[1] + 1.5, s[1] + 2.5, P.BAD)
        # 2 pit trace
        x, y = pos[1]
        c = Chart(st, x - 2.2, y - 1.15, 4.4, 1.9, (0, 10), (0, 10))
        fr = c.frame(xticks=[], yticks=[], grid=False, panel=False)
        tr = c.curve([0, 3, 6, 6.5, 8, 10], [3, 3.1, 3, 3.5, 6.2, 9.0], P.WARN, 0.08, 0.4)
        st.fade_in(fr, s[2] + 0.3, 0.4)
        st.draw_on(tr, s[2] + 0.5, s[2] + 2.5)
        # 3 flow check
        x, y = pos[2]
        pmp = st.rect(x - 1.5, y - 0.5, 1.0, 0.8, P.PANEL2, 0.3)
        pt = st.text("pumps\nOFF", x - 1.5, y - 0.5, 0.2, P.BAD, 0.4, kind="bold")
        fa = st.arrow(x + 0.2, y - 1.1, x + 0.2, y + 0.5, P.WATER, 0.12, 0.35, 0.4)
        ft = st.text("still flowing:\na kick", x + 1.5, y - 0.3, 0.22, P.BAD, 0.4, align="l", kind="bold")
        st.fade_in([pmp, pt], s[3] + 0.3, 0.4)
        st.fade_in(fa + [ft], s[3] + 1.2, 0.4)
        # 4 ROP trace
        x, y = pos[3]
        c4 = Chart(st, x - 2.2, y - 1.15, 4.4, 1.9, (0, 10), (0, 10))
        f4 = c4.frame(xticks=[], yticks=[], grid=False, panel=False)
        tr4 = c4.curve([0, 2, 4, 4.4, 4.9, 5.4, 7, 10], [3, 3.2, 2.9, 7.8, 8.4, 4.6, 4.4, 4.5], P.PORE, 0.08, 0.4)
        c4.label(4.9, 9.2, "faster drilling", 0.2, P.PORE, "c")
        st.fade_in(f4, s[4] + 0.3, 0.4)
        st.draw_on(tr4, s[4] + 0.5, s[4] + 2.5)
        st.fade_in(st.text("catch it while it is still small", 0.4, -3.9, 0.3, P.SAFE, 0.5, kind="bold"), s[5], 0.5)


# ---------------------------------------------------------------- 7.04 the barrier schematic (outline-only panel style)
def _outline(st, x0, y0, x1, y1, color, w=0.07, z=0.6, dashed=False):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return [st.rect(cx, y0, x1 - x0, w, color, z), st.rect(cx, y1, x1 - x0, w, color, z),
            st.rect(x0, cy, w, y1 - y0, color, z), st.rect(x1, cy, w, y1 - y0, color, z)]


def beat_barriers(st, tl):
    b = tl["7.04"]
    s = b.sent
    with st.span(b.start, b.end):
        cx = -3.3
        # schematic: wellhead + BOP on top, casing + cement, open hole below, source at the bottom
        rock = [st.rect(cx - 1.55, -0.4, 0.9, 6.6, P.ROCK, 0.0), st.rect(cx + 1.55, -0.4, 0.9, 6.6, P.ROCK, 0.0)]
        sand = st.rect(cx, -3.45, 3.6, 0.5, P.SAND, 0.0)
        mud = st.rect(cx, -0.2, 1.1, 5.2, P.MUD, 0.1, alpha=0.55)
        csg = [st.rect(cx - 0.62, 0.9, 0.08, 3.6, P.STEEL, 0.2), st.rect(cx + 0.62, 0.9, 0.08, 3.6, P.STEEL, 0.2)]
        cem = [st.rect(cx - 0.8, 0.0, 0.2, 1.8, P.CEMENT, 0.15), st.rect(cx + 0.8, 0.0, 0.2, 1.8, P.CEMENT, 0.15)]
        wh = st.rect(cx, 2.8, 1.7, 0.4, P.STEEL_DK, 0.3)
        bop = st.rect(cx, 3.3, 1.7, 0.7, P.PANEL2, 0.3)
        bopl = st.text("BOP", cx, 3.3, 0.25, P.TEXT, 0.4, kind="bold")
        src = st.arrow(cx, -3.5, cx, -2.8, P.WATER, 0.12, 0.35, 0.4)
        srl = st.text("pressurised formation", cx + 1.2, -3.45, 0.2, P.WATER, 0.4, align="l", kind="bold")
        st.fade_in(rock + [sand, mud] + csg + cem + [wh, bop, bopl] + src + [srl], b.start, 0.5)
        # primary envelope (blue outline): the mud column
        pe = _outline(st, cx - 0.5, -2.9, cx + 0.5, 2.55, P.PRIMARY_B, 0.08, 0.7)
        pl = pill(st, cx + 2.1, 0.3, "PRIMARY: mud column", P.PANEL2, P.PRIMARY_B, 0.24, 0.5, align="l")
        # secondary envelope (red outline): casing + cement + wellhead + BOP
        se = _outline(st, cx - 0.98, -0.95, cx + 0.98, 3.7, P.SECOND_B, 0.08, 0.65)
        sl = pill(st, cx + 2.1, 2.5, "SECONDARY: casing + cement\n+ wellhead + BOP", P.PANEL2, P.SECOND_B, 0.24, 0.5, align="l")
        st.fade_in(se + sl, s[2] + 0.2, 0.5)
        st.fade_in(pe + pl, s[2] + 2.0, 0.5)
        # s0/s1 captions
        t0 = st.text("two independent well barriers, at all times", 3.3, 3.6, 0.3, P.TEXT, 0.5, kind="bold")
        t1 = st.text("each: a well barrier envelope\n= elements that together stop flow", 3.3, 2.6, 0.24, P.MUTED, 0.5)
        st.fade_in(t0, s[0], 0.5)
        st.fade_in(t1, s[1], 0.5)
        # airlock cartoon (right)
        ax = 4.3
        corridor = st.rect(ax, -0.2, 5.0, 1.3, P.PANEL, 0.0)
        d1 = st.rect(ax - 1.4, -0.2, 0.2, 1.3, P.SAFE, 0.3)
        d2 = st.rect(ax + 1.4, -0.2, 0.2, 1.3, P.SAFE, 0.3)
        al = st.text("two airlock doors, never both open", ax, -1.3, 0.24, P.TEXT, 0.4, kind="bold")
        st.fade_in([corridor, d1, d2, al], s[3], 0.5)
        st.move(d1, s[3] + 1.2, s[3] + 2.0, dy=1.0)
        st.move(d1, s[3] + 2.4, s[3] + 3.2, dy=-1.0)
        st.move(d2, s[3] + 3.4, s[3] + 4.2, dy=1.0)
        # s4 barrier lost banner
        ban = pill(st, ax, -2.8, "barrier lost → stop work, restore it", P.BAD, "#ffffff", 0.26, 0.7)
        st.fade_in(ban, s[4], 0.5)
        st.recolor(se[:2], s[4] + 1.5, s[4] + 2.2, P.MUTED)


# ---------------------------------------------------------------- 7.05 shut-in + U-tube
def beat_shutin(st, tl):
    b = tl["7.05"]
    s = b.sent
    with st.span(b.start, b.end):
        # steps
        steps = ["1  stop drilling", "2  flow check", "3  close the preventer"]
        sp = [st.text(t, -5.9, 3.5 - 0.5 * i, 0.26, P.TEXT, 0.4, align="l", kind="bold") for i, t in enumerate(steps)]
        for i, t in enumerate(sp):
            st.fade_in(t, s[0] + 0.4 * i + 0.5, 0.4)
        # closing BOP block (simplified)
        bx, by = -3.6, 0.8
        bop = BopStack(st, bx, by - 2.0, s=0.55, pipe_top=by + 2.1)
        st.fade_in(bop.all, s[0] + 1.0, 0.4)
        bop.close_annular(s[0] + 2.5, s[0] + 3.5)
        # U-tube
        ux = 1.2
        pipe = st.rect(ux - 1.0, 0.2, 0.7, 5.4, P.PANEL2, 0.2)
        ann = st.rect(ux + 1.0, 0.2, 0.7, 5.4, P.PANEL2, 0.2)
        btm = st.rect(ux, -2.5, 2.7, 0.7, P.PANEL2, 0.2)
        mp = st.rect(ux - 1.0, 0.2 - 0.0, 0.6, 5.3, P.MUD, 0.25)
        ma = st.rect(ux + 1.0, 0.45, 0.6, 4.8, P.MUD, 0.25)
        mb = st.rect(ux, -2.5, 2.6, 0.55, P.MUD, 0.25)
        kick = st.rect(ux + 1.0, -1.9, 0.6, 0.6, P.WATER, 0.3)
        lp = st.text("drill pipe", ux - 1.0, 3.2, 0.22, P.TEXT, 0.4, kind="bold")
        la = st.text("annulus", ux + 1.0, 3.2, 0.22, P.TEXT, 0.4, kind="bold")
        st.fade_in([pipe, ann, btm, mp, ma, mb, kick, lp, la], s[2], 0.5)
        ut = st.text("a U-tube", ux, 3.85, 0.3, P.PORE, 0.5, kind="bold")
        st.fade_in(ut, s[2], 0.4)
        # gauges
        g1 = st.text(f"SIDPP\n{SIDPP:.0f} bar", ux - 1.0, 2.15, 0.3, P.WARN, 0.5, kind="bold")
        g2 = st.text("SICP", ux + 1.0, 2.15, 0.3, P.MUTED, 0.5, kind="bold")
        st.fade_in([g1, g2], s[1] + 0.6, 0.5)
        # equation card
        card = st.rect(5.6, 0.2, 3.7, 4.2, P.PANEL, 0.0)
        e1 = st.text("pressure at the bottom", 5.6, 2.0, 0.22, P.TEXT, 0.3, kind="bold")
        e2 = st.text(f"mud in the pipe\n{P_HYD:.0f} bar", 5.6, 1.0, 0.26, P.MUD, 0.3, kind="bold")
        e3 = st.text(f"+ SIDPP\n{SIDPP:.0f} bar", 5.6, -0.2, 0.26, P.WARN, 0.3, kind="bold")
        e4 = st.text(f"= pore pressure\n{P_PORE:.0f} bar", 5.6, -1.5, 0.28, P.WATER, 0.3, kind="bold")
        st.fade_in([card, e1], s[3] - 0.4, 0.4)
        st.fade_in(e2, s[3] + 0.5, 0.4)
        st.fade_in(e3, s[3] + 1.5, 0.4)
        st.fade_in(e4, s[4] + 0.2, 0.5)
        eq = st.text("P_pore = P_hyd(pipe) + SIDPP", 5.6, -3.0, 0.2, P.TEXT, 0.4, kind="mono")
        st.fade_in(eq, s[4], 0.5)


# ---------------------------------------------------------------- 7.06 kill the well
def beat_kill(st, tl):
    b = tl["7.06"]
    s = b.sent
    with st.span(b.start, b.end):
        cx, yt, yb = -3.4, 3.4, -3.0
        cut = Cutaway(st, cx, yt, yb, hole_w=2.2, pipe_w=0.9, rock_w=1.5)
        base = cut.draw(pipe_bottom=yb + 0.5)
        mb = cut.static_bore(P.MUD, yt, yb + 0.5, 0.03)
        ml = cut.static_gap("l", P.MUD, yt, yb, 0.03)
        mr = cut.static_gap("r", P.MUD, yt, yb, 0.03)
        inf_l = cut.static_gap("l", P.WATER, yb, yb + 1.3, 0.05)
        inf_r = cut.static_gap("r", P.WATER, yb, yb + 1.3, 0.05)
        st.fade_in(base + [mb, ml, mr, inf_l, inf_r], b.start, 0.5)
        # equation
        eq1 = st.text("kill mud weight = old weight + SIDPP / (g · depth)", 2.2, 3.5, 0.24, P.TEXT, 0.4, kind="mono", align="c")
        eq2 = st.text(f"{MW_OLD:.2f} + {SIDPP:.1f} / (0.0981 × {TVD_KILL:,.0f}) = {KMW:.2f} sg", 2.2, 2.9, 0.3, P.KILL_MUD, 0.4, kind="mono", align="c")
        st.fade_in([eq1], s[0], 0.5)
        st.fade_in([eq2], s[0] + 2.5, 0.5)
        # kill mud down the pipe, up the annulus (driller's method second circulation)
        t0, t1, t2 = s[1] + 0.3, s[1] + 3.5, s[1] + 7.0
        kb = cut.fill_bore(P.KILL_MUD, yt, yb + 0.5, t0, t1, 0.12, interp="LINEAR")
        kl = cut.fill_gap("l", P.KILL_MUD, yb, yt, t1, t2, 0.12, interp="LINEAR")
        kr = cut.fill_gap("r", P.KILL_MUD, yb, yt, t1, t2, 0.12, interp="LINEAR")
        # choke + constant BHP
        chk = st.poly([(cx + 2.0, 3.1), (cx + 2.6, 3.1), (cx + 2.3, 2.6)], P.WARN, 0.5)
        cl = st.text("choke holds bottom-hole\npressure just above pore pressure", 2.2, 1.6, 0.24, P.WARN, 0.5, kind="bold")
        bar = st.rect(5.6, -2.2, 0.6, 2.4, P.MUD, 0.3, anchor="b")
        bf = st.rect(5.6, -1.0, 0.64, 2.8, P.PANEL2, 0.2)
        bl = st.text("bottom-hole\npressure", 5.6, 0.7, 0.2, P.TEXT, 0.4, kind="bold")
        st.fade_in([chk, cl, bf, bar, bl], s[1] + 0.5, 0.5)
        dm = st.text("driller's method:\ncirculates twice", 2.2, -0.2, 0.26, P.TEXT, 0.5, kind="bold")
        st.fade_in(dm, s[2], 0.5)
        # subsea choke-line friction
        line = st.line([(cut.hole[1] + 0.3, 3.0), (3.6, 3.0), (3.6, -0.8)], P.MUTED, 0.06, 0.4)
        fr = st.arrow(3.9, 0.4, 3.9, -0.8, P.BAD, 0.07, 0.22, 0.5)
        ft = st.text("friction in the long choke\nline adds pressure:\npump slowly, correct for it", 4.15, -1.6, 0.22, P.BAD, 0.5, align="l", kind="bold")
        st.fade_in([line] + fr + [ft], s[3], 0.5)


# ---------------------------------------------------------------- 7.07 kick tolerance at the shoe
def beat_tolerance(st, tl):
    b = tl["7.07"]
    s = b.sent
    with st.span(b.start, b.end):
        cx, yt, yb = -3.6, 3.4, -3.0
        shoe_y = 0.9
        cut = Cutaway(st, cx, yt, yb, hole_w=2.2, pipe_w=0.8, rock_w=1.4)
        base = cut.draw(pipe_bottom=yb + 0.4)
        mud = [cut.static_gap("l", P.MUD, yt, yb, 0.03), cut.static_gap("r", P.MUD, yt, yb, 0.03), cut.static_bore(P.MUD, yt, yb + 0.4, 0.03)]
        csg = [st.rect(cut.hole[0] + 0.07, (yt + shoe_y) / 2, 0.12, yt - shoe_y, P.CEMENT, 0.08), st.rect(cut.hole[1] - 0.07, (yt + shoe_y) / 2, 0.12, yt - shoe_y, P.CEMENT, 0.08)]
        shoe = [st.poly([(cut.hole[0], shoe_y), (cut.hole[0] + 0.25, shoe_y), (cut.hole[0] + 0.25, shoe_y + 0.2)], P.WARN, 0.5),
                st.poly([(cut.hole[1], shoe_y), (cut.hole[1] - 0.25, shoe_y), (cut.hole[1] - 0.25, shoe_y + 0.2)], P.WARN, 0.5)]
        sl = st.text("casing shoe:\nthe weak point", cut.hole[1] + 0.2, shoe_y - 0.45, 0.24, P.WARN, 0.5, align="l", kind="bold")
        st.fade_in(base + mud + csg + shoe + [sl], b.start, 0.5)
        # gas slug rising: its top reaches the shoe, then passes it
        gx = (cut.gap_r[0] + cut.gap_r[1]) / 2
        slug = st.rect(gx, yb + 0.2, (cut.gap_r[1] - cut.gap_r[0]) * 0.8, 1.2, P.GAS, 0.4, anchor="b")
        st.fade_in(slug, s[1] - 0.5, 0.4)
        t_a, t_b = s[1], s[2] + 3.0
        st.move(slug, t_a, t_b, dy=(yt - 0.6 - (yb + 0.2)), interp="LINEAR")
        # pressure at the shoe: rises to a peak when the slug top reaches the shoe
        c = Chart(st, 1.4, -2.6, 5.8, 5.0, (0, 10), (0, 10))
        fr = c.frame(xticks=[], yticks=[], xlabel="gas position", ylabel="pressure at the shoe", grid=False)
        xs = [i / 4 for i in range(41)]
        ok = [3.0 + 3.5 * math.exp(-((x - 5.0) / 1.6) ** 2) for x in xs]
        big = [3.0 + 6.5 * math.exp(-((x - 5.0) / 1.6) ** 2) for x in xs]
        fline = c.hline(8.0, P.FRAC, 0.05, 0.3)
        fll = c.label(0.2, 8.5, "fracture pressure at the shoe", 0.22, P.FRAC, "l")
        st.fade_in(fr + [fline, fll], s[0], 0.4)
        l1 = c.curve(xs, ok, P.SAFE, 0.08, 0.4)
        st.draw_on(l1, t_a, t_b)
        st.fade_in(c.label(5.0, 6.9, "peaks as the gas top\nreaches the shoe", 0.2, P.SAFE, "c", dy=0.0), s[1] + 1.8, 0.5)
        l2 = c.curve(xs, big, P.BAD, 0.08, 0.45)
        st.draw_on(l2, s[2], s[2] + 3.0)
        st.fade_in(c.label(5.0, 9.7, "too big a kick: the rock cracks", 0.2, P.BAD, "c"), s[2] + 2.0, 0.5)
        kt = pill(st, 4.4, -3.4, "kick tolerance = the biggest kick that\nstays under the fracture line", P.PANEL2, P.TEXT, 0.22, 0.6)
        st.fade_in(kt, s[3], 0.6)


# ---------------------------------------------------------------- 7.08 Macondo (restrained, factual)
def beat_macondo(st, tl):
    b = tl["7.08"]
    s = b.sent
    with st.span(b.start, b.end):
        head = st.text("Macondo, 2010", 0.8, 3.6, 0.5, P.TEXT, 0.3, kind="bold")
        st.fade_in(head, s[0], 0.6)
        rows = [("cement + shoe track:  did not isolate the reservoir", s[1]),
                ("negative pressure test:  misread", s[2]),
                ("blowout preventer:  did not seal", s[3])]
        bars = []
        for i, (txt, t) in enumerate(rows):
            y = 1.7 - 1.25 * i
            bar = st.rect(0.8, y, 10.5, 0.95, P.SAFE, 0.2)
            label = st.text(f"{i + 1}   " + txt, -4.2, y, 0.36, "#06201c", 0.3, align="l", kind="bold")
            st.fade_in([bar, label], s[0] + 0.6 + 0.3 * i, 0.5)
            st.recolor(bar, t, t + 0.8, P.STEEL_DK)
            st.recolor(label, t, t + 0.8, P.TEXT)
            bars.append(bar)
        loss = st.text("11 lives lost", 0.8, -2.5, 0.6, P.TEXT, 0.3, kind="bold")
        st.fade_in(loss, s[4], 0.8)
        lesson = st.text("barriers do not fail one at a time.\nthey fail when we stop checking.", 0.8, -3.5, 0.3, P.WARN, 0.3, kind="bold")
        st.fade_in(lesson, s[5], 0.8)


def build(st, tl):
    F.header(st, tl)
    F.well_strip(st, 0.0, tl.dur, strings=[p.name for p in M.programme()], marker=M.TD)
    beat_lied(st, tl)
    beat_kick(st, tl)
    beat_detect(st, tl)
    beat_barriers(st, tl)
    beat_shutin(st, tl)
    beat_kill(st, tl)
    beat_tolerance(st, tl)
    beat_macondo(st, tl)
