"""Ch 9: Plugging and abandonment. Includes THE PLUG PLACEMENT animation (mechanical base, balanced cement plug, pull out).

Plug lengths in this chapter are DRAWING values only (the narration states no D-010 minimum lengths: unverified)."""
from __future__ import annotations
import math

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common.shapes import Cutaway, CasingColumn, pill, loop_move

TITLE = "Plugging and abandonment"


def _well(st, t0, cx=-1.4):
    """Depth-aligned well schematic (all four strings, reservoir band). Returns (chart for Y mapping, objects)."""
    ch = Chart(st, cx - 1.6, -3.1, 3.2, 6.5, (0, 1), (0, 4300), invert_y=True)
    col = CasingColumn(st, ch, cx=cx)
    objs = col.backdrop()
    res = st.rect(cx, (ch.Y(M.RES_TOP) + ch.Y(M.RES_BASE)) / 2, 2.2, ch.Y(M.RES_TOP) - ch.Y(M.RES_BASE), P.SAND, 0.03)
    sa = st.rect(cx, (ch.Y(M.SAND_A[0]) + ch.Y(M.SAND_A[1])) / 2, 2.2, max(ch.Y(M.SAND_A[0]) - ch.Y(M.SAND_A[1]), 0.06), P.SAND, 0.03)
    objs += [res, sa]
    for i, p in enumerate(M.programme()):
        objs += col.string(p.name, p.shoe, t0 + 0.1 * i, t0 + 0.2 * i + 0.4)
    hole = st.rect(cx, (ch.Y(M.programme()[-1].shoe) + ch.Y(M.TD)) / 2, 0.14, ch.Y(M.programme()[-1].shoe) - ch.Y(M.TD), P.BG, 0.6)
    objs.append(hole)
    return ch, col, objs


# ---------------------------------------------------------------- 9.01 sealed for geological time
def beat_why(st, tl):
    b = tl["9.01"]
    s = b.sent
    with st.span(b.start, b.end):
        ch, col, objs = _well(st, b.start)
        st.fade_in(objs, b.start, 0.5)
        cx = col.cx
        gauge = pill(st, cx + 2.2, ch.Y(4030), f"reservoir: ~{M.bar(4000, M.pp(4000)):.0f} bar", P.PANEL2, P.WATER, 0.26, 0.5, align="l")
        st.fade_in(gauge, s[3], 0.5)
        flow = st.arrow(cx + 1.05, ch.Y(3950), cx + 1.05, ch.Y(420), P.WATER, 0.1, 0.35, 0.6)
        fl = st.text("a flow path to the seabed", cx + 1.3, ch.Y(2000), 0.26, P.WATER, 0.6, align="l", kind="bold")
        sea = st.text("the sea", cx + 1.3, ch.Y(150), 0.24, P.TEXT, 0.6, align="l", kind="bold")
        st.fade_in(flow + [fl, sea], s[3] + 0.8, 0.6)
        # geological time + the P&A plan
        gt = st.text("must stay sealed for\ngeological time", 4.4, 1.2, 0.4, P.WARN, 0.5, kind="bold")
        st.fade_in(gt, s[3] + 2.0, 0.6)
        doc = st.rect(4.4, -1.4, 2.2, 1.5, P.PANEL2, 0.4)
        dl = st.text("P&A plan:\nwritten before spud", 4.4, -1.4, 0.26, P.TEXT, 0.5, kind="bold")
        st.fade_in([doc, dl], s[5], 0.6)
        pa = st.text("plugging and abandonment", 4.4, 3.4, 0.34, P.PORE, 0.5, kind="bold")
        st.fade_in(pa, s[4], 0.5)


# ---------------------------------------------------------------- 9.02 every source of inflow
def beat_sources(st, tl):
    b = tl["9.02"]
    s = b.sent
    with st.span(b.start, b.end):
        ch, col, objs = _well(st, b.start)
        st.fade_in(objs, b.start, 0.4)
        cx = col.cx
        arr1 = st.arrow(cx + 1.0, ch.Y(4050), cx + 1.0, ch.Y(3500), P.WATER, 0.09, 0.3, 0.7)
        l1 = st.text("reservoir", cx + 1.3, ch.Y(4030), 0.26, P.SAND, 0.7, align="l", kind="bold")
        st.fade_in(arr1 + [l1], s[0] + 0.8, 0.5)
        arr2 = st.arrow(cx + 1.0, ch.Y(2990), cx + 1.0, ch.Y(2500), P.WATER, 0.09, 0.3, 0.7)
        l2 = pill(st, cx + 1.4, ch.Y(2990), "thin overpressured sand\n(~3,000 m): flow potential", P.PANEL2, P.WATER, 0.24, 0.7, align="l")
        st.fade_in(l1, s[1], 0.3)
        st.fade_in(arr2 + l2, s[2], 0.5)
        # barrier brackets (drawing only): two for the reservoir, one for the sand
        def bar(z0, z1, label, col_):
            r = st.rect(cx, (ch.Y(z0) + ch.Y(z1)) / 2, 1.9, abs(ch.Y(z0) - ch.Y(z1)), P.SAFE, 0.8)
            t = st.text(label, cx - 1.3, (ch.Y(z0) + ch.Y(z1)) / 2, 0.22, col_, 0.9, align="r", kind="bold")
            return [r, t]
        b1 = bar(3820, 3880, "primary", P.SAFE)
        b2 = bar(3640, 3700, "secondary", P.SAFE)
        b3 = bar(2900, 2955, "one barrier", P.SAFE)
        st.fade_in(b1, s[3], 0.5)
        st.fade_in(b2, s[3] + 1.0, 0.5)
        st.fade_in(b3, s[3] + 2.0, 0.5)
        tw = st.text("two for a flowing\nhydrocarbon reservoir", cx + 1.4, ch.Y(3760), 0.24, P.SAFE, 0.9, align="l", kind="bold")
        st.fade_in(tw, s[3] + 1.2, 0.5)
        dr = st.text("[bar lengths are drawing values]", 4.4, -3.4, 0.2, P.SIM_BADGE, 0.9)
        st.fade_in(dr, s[3] + 2.0, 0.4)


# ---------------------------------------------------------------- 9.03 rock to rock
def beat_rock(st, tl):
    b = tl["9.03"]
    s = b.sent
    with st.span(b.start, b.end):
        yt, yb = 2.6, -2.6
        # LEFT: plug inside casing only; leak path behind it
        cxL, cxR = -4.2, 4.2
        L = Cutaway(st, cxL, yt, yb, hole_w=2.4, pipe_w=1.0, rock_w=1.2)
        R = Cutaway(st, cxR, yt, yb, hole_w=2.4, pipe_w=1.0, rock_w=1.2)
        baseL, baseR = L.draw(), R.draw()
        annL = [L.static_gap("l", P.CEMENT, yt, yb, 0.03), L.static_gap("r", P.MUD, yt, yb, 0.03)]
        annR = [R.static_gap("l", P.CEMENT, yt, yb, 0.03), R.static_gap("r", P.CEMENT, yt, yb, 0.03)]
        boreL, boreR = L.static_bore(P.MUD, yt, yb, 0.03), R.static_bore(P.MUD, yt, yb, 0.03)
        st.fade_in(baseL + baseR + annL + annR + [boreL, boreR], b.start, 0.5)
        # tunnel analogy (middle)
        tx = 0.0
        cor = st.rect(tx, 0.0, 3.6, 1.7, P.PANEL, 0.0)
        door = st.rect(tx, 0.0, 0.3, 1.5, P.STEEL, 0.3)
        pip = [st.rect(tx, 0.62, 3.4, 0.12, P.WATER, 0.3), st.rect(tx, -0.62, 3.4, 0.12, P.WATER, 0.3)]
        arrw = st.arrow(tx - 1.6, 0.62, tx + 1.6, 0.62, P.BAD, 0.06, 0.2, 0.5)
        tl_ = st.text("a door in the corridor is\nno use if pipes run along the wall", tx, 1.75, 0.22, P.TEXT, 0.4, kind="bold")
        st.fade_in([cor, door] + pip, s[1], 0.5)
        st.fade_in(arrw + [tl_], s[2], 0.5)
        # failing plug (left): inside the casing only, with the leak path around it
        plugL = st.rect((L.bore[0] + L.bore[1]) / 2, -0.2, L.bore[1] - L.bore[0], 0.8, P.SAFE, 0.4)
        leak = st.arrow(L.gap_r[0] + 0.15, -2.2, L.gap_r[0] + 0.15, 2.0, P.BAD, 0.07, 0.25, 0.5)
        fl = pill(st, cxL, -3.15, "plug in the casing only:\nfluid runs behind it", P.BAD, "#ffffff", 0.24, 0.7)
        st.fade_in([plugL] + leak, s[3], 0.5)
        st.fade_in(fl, s[3] + 0.5, 0.5)
        # holding plug (right): across casing + annulus, bonded to rock on both sides
        plugR = st.rect(cxR, -0.2, R.hole[1] - R.hole[0], 0.8, P.SAFE, 0.4)
        bonds = st.arrow(R.hole[0] - 1.0, -0.2, R.hole[0] + 0.05, -0.2, P.TEXT, 0.06, 0.2, 0.5) + st.arrow(R.hole[1] + 1.0, -0.2, R.hole[1] - 0.05, -0.2, P.TEXT, 0.06, 0.2, 0.5)
        hl = pill(st, cxR, -3.15, "ROCK TO ROCK: seals the whole\ncross-section, every annulus", P.SAFE, "#06201c", 0.24, 0.7)
        st.fade_in([plugR] + bonds, s[0] + 3.0, 0.5)
        st.fade_in(hl, s[0] + 3.5, 0.5)


# ---------------------------------------------------------------- 9.04 three ways
def beat_ways(st, tl):
    b = tl["9.04"]
    s = b.sent
    yt, yb = 2.4, -2.4
    xs = (-4.4, 0.9, 6.2)
    with st.span(b.start, b.end):
        st.fade_in(st.text("three ways to get rock to rock", 0.8, 3.7, 0.32, P.TEXT, 0.4, kind="bold"), s[0], 0.5)
        names = ["1  logged, good cement behind the casing", "2  section milling", "3  perforate, wash, cement"]
        for i, x in enumerate(xs):
            card = st.rect(x, -0.2, 4.7, 6.0, P.PANEL, 0.0)
            cut = Cutaway(st, x, yt, yb, hole_w=2.0, pipe_w=0.8, rock_w=1.0)
            base = cut.draw()
            tt = st.text(names[i], x, 3.0, 0.2, P.TEXT, 0.4, kind="bold")
            t = (s[1], s[2], s[3])[i]
            st.fade_in([card, tt] + base, t, 0.5)
            if i == 0:
                g = [cut.static_gap("l", P.CEMENT, yt, yb, 0.03), cut.static_gap("r", P.CEMENT, yt, yb, 0.03)]
                bore = cut.static_bore(P.MUD, yt, yb, 0.03)
                ok = st.rect(cut.hole[1] + 0.8, 0.2, 0.25, 2.2, P.SAFE, 0.5)
                okl = st.text("bond log:\ngood", cut.hole[1] + 1.55, 0.2, 0.2, P.SAFE, 0.5, kind="bold")
                plug = st.rect(x, 0.2, cut.hole[1] - cut.hole[0], 1.0, P.SAFE, 0.4)
                st.fade_in(g + [bore, ok, okl], t + 0.3, 0.4)
                st.fade_in(plug, t + 1.5, 0.5)
            elif i == 1:
                g = [cut.static_gap("l", P.CEMENT, yt, yb, 0.03), cut.static_gap("r", P.CEMENT, yt, yb, 0.03)]
                bore = cut.static_bore(P.MUD, yt, yb, 0.03)
                st.fade_in(g + [bore], t + 0.3, 0.4)
                # the milled window: casing removed -> open hole against the rock
                win = st.rect(x, 0.2, cut.hole[1] - cut.hole[0], 1.6, P.BG, 0.45)
                mill = st.rect(x, 0.2, 0.9, 0.35, P.WARN, 0.5)
                st.fade_in(mill, t + 0.6, 0.3)
                st.move(mill, t + 0.9, t + 2.0, dy=0.5)
                st.move(mill, t + 2.0, t + 3.0, dy=-0.5)
                st.fade_in(win, t + 1.2, 1.2)
                plug = st.rect(x, 0.2, cut.hole[1] - cut.hole[0], 1.4, P.SAFE, 0.5)
                st.fade_in(plug, t + 3.2, 0.5)
                st.fade_out(mill, t + 3.0, 0.3)
            else:
                g = [cut.static_gap("l", P.MUD, yt, yb, 0.03), cut.static_gap("r", P.MUD, yt, yb, 0.03)]
                bore = cut.static_bore(P.MUD, yt, yb, 0.03)
                st.fade_in(g + [bore], t + 0.3, 0.4)
                guns = [st.arrow(x - 0.1, 0.4, cut.pipe[0] - 0.3, 0.4, P.WARN, 0.06, 0.18, 0.5), st.arrow(x + 0.1, 0.4, cut.pipe[1] + 0.3, 0.4, P.WARN, 0.06, 0.18, 0.5)]
                gl = st.text("perforate", x, -1.0, 0.2, P.WARN, 0.5, kind="bold")
                st.fade_in([a for gg in guns for a in gg] + [gl], t + 0.8, 0.4)
                wl = st.text("wash the annulus clean", x, -1.5, 0.2, P.PORE, 0.5, kind="bold")
                st.fade_in(wl, t + 1.8, 0.4)
                st.recolor(g, t + 2.0, t + 2.8, P.PORE)
                cl = st.text("cement it", x, -2.0, 0.2, P.CEMENT, 0.5, kind="bold")
                st.fade_in(cl, t + 3.0, 0.4)
                st.recolor(g, t + 3.0, t + 3.8, P.SAFE)


# ---------------------------------------------------------------- 9.05 THE PLUG PLACEMENT ANIMATION
def beat_place(st, tl):
    b = tl["9.05"]
    s = b.sent
    with st.span(b.start, b.end):
        yt, yb = 3.5, -3.1
        cx = -3.4
        cut = Cutaway(st, cx, yt, yb, hole_w=2.0, pipe_w=0.1, rock=P.STEEL_DK, rock_w=0.45, wall=0.02)
        base = cut.draw()
        mud = st.rect(cx, (yt + yb) / 2, 1.96, yt - yb, P.MUD, 0.03)
        csl = st.text("9⅝ in casing", cx - 1.75, 3.3, 0.22, P.TEXT, 0.4, align="r", kind="bold")
        st.fade_in(base + [mud, csl], b.start, 0.5)
        base_y = -2.3
        # 1. mechanical base (bridge plug) set
        plug0 = st.rect(cx, base_y, 1.96, 0.3, P.WARN, 0.35)
        slips = [st.poly([(cx - 0.98, base_y + 0.15), (cx - 0.7, base_y + 0.15), (cx - 0.98, base_y - 0.15)], P.TEXT, 0.4), st.poly([(cx + 0.98, base_y + 0.15), (cx + 0.7, base_y + 0.15), (cx + 0.98, base_y - 0.15)], P.TEXT, 0.4)]
        st.fade_in([plug0] + slips, s[0] + 0.8, 0.5)
        pb = st.text("mechanical base", cx + 1.2, base_y, 0.22, P.WARN, 0.5, align="l", kind="bold")
        st.fade_in(pb, s[0] + 1.2, 0.4)
        # 2. open-ended drill pipe lowered to just above the base
        pipe = st.rect(cx, yt, 0.34, 0.0001, P.STEEL, 0.5, anchor="t")
        pend = base_y + 0.55
        t_down0, t_down1 = s[1], s[1] + 3.0
        st.scale_to(pipe, t_down0, t_down1, sy=yt - pend)
        pl = st.text("open-ended drill pipe", cx + 1.2, 2.4, 0.22, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(pl, t_down0 + 0.5, 0.4)
        # cement column around the pipe end: spacer, cement, spacer
        sp1 = st.rect(cx, base_y + 0.15, 1.9, 0.0001, P.SPACER, 0.45, anchor="b")
        cem = st.rect(cx, base_y + 0.15, 1.9, 0.0001, P.CEMENT, 0.42, anchor="b")
        h_cem = 1.6
        t_c0, t_c1 = t_down1 + 0.3, t_down1 + 3.8
        st.scale_to(sp1, t_c0, t_c1, sy=h_cem + 0.35)
        st.scale_to(cem, t_c0 + 0.4, t_c1, sy=h_cem)
        sp2 = st.rect(cx, base_y + 0.15 + h_cem, 1.9, 0.0001, P.SPACER, 0.45, anchor="b")
        st.scale_to(sp2, t_c1, t_c1 + 0.4, sy=0.25)
        bl = st.text("balanced: levels inside and\noutside the pipe match", cx + 1.2, 0.2, 0.22, P.PORE, 0.5, align="l", kind="bold")
        st.fade_in(bl, t_c0 + 1.0, 0.5)
        # 3. pull out slowly through the cement; the cement stays
        t_p0, t_p1 = s[2], s[2] + 4.5
        st.scale_to(pipe, t_p0, t_p1, sy=yt - (pend + 2.6))
        pu = st.text("pull out slowly", cx + 1.2, 1.2, 0.22, P.SAFE, 0.5, align="l", kind="bold")
        st.fade_in(pu, t_p0 + 0.3, 0.4)
        # clear excess above the plug (reverse circulation)
        rc = [st.arrow(cx + 0.3, base_y + 2.0, cx + 0.3, base_y + 3.3, P.PORE, 0.05, 0.16, 0.5)]
        st.fade_in([a for r in rc for a in r], t_p1 - 1.0, 0.4)
        # the plug: dimension + drawing-only caption
        dim = st.arrow(cx - 1.25, base_y + 0.15 + h_cem / 2, cx - 1.25, base_y + 0.15 + h_cem, P.TEXT, 0.04, 0.16, 0.6) + st.arrow(cx - 1.25, base_y + 0.15 + h_cem / 2, cx - 1.25, base_y + 0.15, P.TEXT, 0.04, 0.16, 0.6)
        dt = st.text("≈100 m\n(drawing value)", cx - 1.45, base_y + 0.15 + h_cem / 2, 0.22, P.TEXT, 0.6, align="r", kind="bold")
        st.fade_in(dim + [dt], s[3], 0.5)
        # right: step list
        steps = ["1  set a mechanical base", "2  pump spacer, cement, spacer\n    through open-ended pipe", "3  pull out slowly", "4  circulate the excess out"]
        times = [s[0] + 1.0, s[1] + 1.0, s[2] + 0.5, t_p1 - 1.0]
        card = st.rect(3.9, 0.3, 6.4, 5.4, P.PANEL, 0.0)
        st.fade_in(card, b.start + 0.5, 0.5)
        for i, (t, tt) in enumerate(zip(steps, times)):
            st.fade_in(st.text(t, 1.0, 2.2 - 1.15 * i, 0.26, P.TEXT, 0.3, align="l", kind="bold"), tt, 0.5)
        sim = st.text("[drawing only: lengths come from the standard]", 3.9, -2.8, 0.2, P.SIM_BADGE, 0.3)
        st.fade_in(sim, s[3], 0.5)


# ---------------------------------------------------------------- 9.06 verification
def beat_verify(st, tl):
    b = tl["9.06"]
    s = b.sent
    with st.span(b.start, b.end):
        xs = (-4.4, 0.9, 6.0)
        names = ["TAG: set down weight", "PRESSURE TEST", "LOG THE CEMENT"]
        starts = [s[1], s[2], s[3]]
        for x, nm, t in zip(xs, names, starts):
            card = st.rect(x, 0.0, 4.5, 5.6, P.PANEL, 0.0)
            tt = st.text(nm, x, 2.4, 0.26, P.PORE, 0.3, kind="bold")
            st.fade_in([card, tt], t, 0.4)
        # 1: tag
        x = xs[0]
        w1 = [st.rect(x - 0.8, -0.3, 0.12, 3.6, P.STEEL_DK, 0.2), st.rect(x + 0.8, -0.3, 0.12, 3.6, P.STEEL_DK, 0.2)]
        plug = st.rect(x, -1.6, 1.6, 0.8, P.SAFE, 0.3)
        pipe = st.rect(x, 1.8, 0.3, 2.4, P.STEEL, 0.4, anchor="t")
        wt = st.arrow(x, 2.1, x, 1.3, P.WARN, 0.12, 0.3, 0.5)
        wl = st.text("load it with weight", x, -2.5, 0.22, P.WARN, 0.4, kind="bold")
        st.fade_in(w1 + [plug, pipe] + wt, s[1] + 0.3, 0.4)
        st.move(pipe, s[1] + 1.0, s[1] + 2.5, dy=-0.9)
        st.fade_in(wl, s[1] + 2.0, 0.4)
        # 2: pressure test
        x = xs[1]
        dial = st.circle(x, 0.4, 1.0, P.PANEL2, 0.3)
        rim = st.ring(x, 0.4, 1.0, 0.06, P.MUTED, 0.35)
        nd = st.rect(x, 0.4, 0.85, 0.07, P.WARN, 0.5, anchor="l", rot=200)
        hub = st.circle(x, 0.4, 0.08, P.TEXT, 0.55)
        st.fade_in([dial, rim, nd, hub], s[2] + 0.3, 0.4)
        st.rotate(nd, s[2] + 0.8, s[2] + 2.5, -15, interp="LINEAR")
        hd = st.text("HOLDS", x, -1.5, 0.4, P.SAFE, 0.4, kind="bold")
        dr = st.text("in the direction it has to hold,\nwhere possible", x, -2.4, 0.2, P.MUTED, 0.4)
        st.fade_in([hd, dr], s[2] + 2.6, 0.4)
        # 3: log
        x = xs[2]
        w3 = [st.rect(x - 0.7, -0.3, 0.1, 3.6, P.STEEL, 0.2), st.rect(x + 0.7, -0.3, 0.1, 3.6, P.STEEL, 0.2)]
        cem = [st.rect(x - 1.0, -0.3, 0.45, 3.6, P.CEMENT, 0.1), st.rect(x + 1.0, -0.3, 0.45, 3.6, P.CEMENT, 0.1)]
        tool = st.rect(x, 1.5, 0.7, 0.9, P.WARN, 0.4)
        st.fade_in(w3 + cem + [tool], s[3] + 0.3, 0.4)
        st.move(tool, s[3] + 0.8, s[3] + 3.0, dy=-2.4)
        tk = st.text("✓ bond good", x, -2.5, 0.28, P.SAFE, 0.5, kind="mono")
        st.fade_in(tk, s[3] + 3.0, 0.4)
        # stamp
        stamp = pill(st, 0.9, -3.6, "A BARRIER THAT HAS NOT BEEN VERIFIED IS NOT A BARRIER", P.SAFE, "#06201c", 0.3, 0.7)
        st.fade_in(stamp, s[4], 0.6)


# ---------------------------------------------------------------- 9.07 cut and pull + seabed clearance
def beat_cut(st, tl):
    b = tl["9.07"]
    s = b.sent
    with st.span(b.start, b.end):
        sb = 0.0
        sea = st.rect(0.8, 2.2, 14.0, 4.4, P.SEA, 0.0)
        rock = st.rect(0.8, -2.2, 14.0, 4.4, P.ROCK, 0.0)
        line = st.rect(0.8, sb, 14.0, 0.05, P.SEABED, 0.06)
        st.fade_in([sea, rock, line], b.start, 0.5)
        cx = -2.4
        strings = [(1.0, "#56667d"), (0.74, "#71839c"), (0.5, "#98a9bf"), (0.3, "#c9d4e1")]
        walls = []
        for w, col in strings:
            walls += [st.rect(cx - w / 2, -1.0, 0.06, 2.4, col, 0.2), st.rect(cx + w / 2, -1.0, 0.06, 2.4, col, 0.2)]
        wellhead = [st.rect(cx, sb + 0.35, 1.3, 0.7, P.STEEL_DK, 0.3), st.rect(cx, sb + 0.1, 2.4, 0.2, P.STEEL_DK, 0.3)]
        st.fade_in(walls + wellhead, b.start, 0.5)
        st.fade_in(st.text("last, the steel: cut and pull", 0.8, 3.6, 0.3, P.TEXT, 0.5, kind="bold"), s[0], 0.5)
        # cutter flashes below the seabed
        cutr = st.rect(cx, -0.8, 1.2, 0.12, P.BAD, 0.6, alpha=0.0)
        cl = st.text("cut below the seabed", cx + 1.4, -0.8, 0.24, P.BAD, 0.6, align="l", kind="bold")
        st.fade_in([cutr], s[1] + 0.3, 0.2)
        st.fade_in(cl, s[1] + 0.3, 0.4)
        st.fade_out(cutr, s[1] + 1.4, 0.3)
        # pull: casing above the cut, wellhead and guide base lift away
        upper = [w for w in walls]
        pull = wellhead + upper
        st.move(pull, s[1] + 2.0, s[1] + 5.5, dy=5.0)
        st.fade_out(pull, s[1] + 4.2, 1.2)
        # clean seabed + ROV sweep
        rov = [st.rect(-5.2, 1.4, 1.2, 0.5, P.WARN, 0.5), st.text("ROV", -5.2, 1.4, 0.2, "#0b1220", 0.6, kind="bold")]
        cone = st.poly([(-5.2, 1.2), (-6.0, sb + 0.05), (-4.4, sb + 0.05)], P.TEXT, 0.4, 0.2)
        st.fade_in(rov + [cone], s[2], 0.5)
        st.move(rov + [cone], s[2] + 0.5, s[2] + 6.0, dx=10.0, interp="LINEAR")
        cs = st.text("clean seabed: nothing for a trawl to catch", 2.2, -3.2, 0.26, P.SAFE, 0.5, kind="bold")
        st.fade_in(cs, s[2] + 3.0, 0.5)
        # temporary abandonment limit
        cal = st.rect(5.8, 1.6, 1.8, 1.4, P.PANEL2, 0.5)
        cg = [st.rect(5.8, 2.0, 1.8, 0.3, P.NO_BADGE, 0.55)] + [st.circle(5.2 + 0.4 * i, 1.5 + 0.0 - 0.0, 0.07, P.TEXT, 0.55) for i in range(4)]
        lm = pill(st, 5.8, 0.3, "temporary abandonment:\na limited lifetime", P.PANEL2, P.WARN, 0.22, 0.6)
        st.fade_in([cal] + cg + lm, s[3], 0.5)


# ---------------------------------------------------------------- 9.08 the as-abandoned drawing
def beat_filed(st, tl):
    b = tl["9.08"]
    s = b.sent
    with st.span(b.start, b.end):
        ch, col, objs = _well(st, b.start, cx=-2.2)
        st.fade_in(objs, b.start, 0.4)
        cx = col.cx
        plugs = [(3820, 3880), (3640, 3700), (2900, 2955), (1180, 1260), (330, 400)]
        pg = []
        for z0, z1 in plugs:
            pg.append(st.rect(cx, (ch.Y(z0) + ch.Y(z1)) / 2, 1.9, max(abs(ch.Y(z0) - ch.Y(z1)), 0.1), P.SAFE, 0.9))
        st.fade_in(pg, s[0], 0.8)
        st.fade_in(st.text("plugs in solid green\n[drawing values]", cx + 2.4, ch.Y(3000), 0.22, P.SAFE, 0.9, align="l", kind="bold"), s[0] + 0.5, 0.5)
        sbl = st.text("cut below the seabed:\nseabed clean", cx + 2.4, ch.Y(320), 0.22, P.TEXT, 0.9, align="l", kind="bold")
        st.fade_in(sbl, s[0] + 0.5, 0.5)
        stamp = pill(st, 4.4, 1.0, "AS-ABANDONED", P.SAFE, "#06201c", 0.5, 0.8)
        st.fade_in(stamp, s[1], 0.6)
        arch = st.rect(4.4, -1.6, 2.6, 1.8, P.PANEL2, 0.4)
        al = st.text("archive", 4.4, -1.6, 0.3, P.TEXT, 0.5, kind="bold")
        sheet = st.rect(4.4, 0.4, 1.4, 1.1, P.TEXT, 0.45)
        st.fade_in([arch, al, sheet], s[1] + 1.0, 0.5)
        st.move(sheet, s[1] + 2.0, s[1] + 3.2, dy=-1.2)
        rt = st.text("right for the long term", 4.4, -3.2, 0.3, P.WARN, 0.5, kind="bold")
        st.fade_in(rt, s[1] + 2.5, 0.6)


def build(st, tl):
    F.header(st, tl)
    F.well_strip(st, 0.0, tl["9.05"].start, strings=[p.name for p in M.programme()], marker=M.TD)
    F.well_strip(st, tl["9.05"].start, tl["9.08"].start, strings=[p.name for p in M.programme()], marker=M.TD, plugs=[(3640, 3880), (2900, 2955)])
    F.well_strip(st, tl["9.08"].start, tl.dur, strings=[p.name for p in M.programme()], plugs=[(3640, 3880), (2900, 2955), (1180, 1260)])
    beat_why(st, tl)
    beat_sources(st, tl)
    beat_rock(st, tl)
    beat_ways(st, tl)
    beat_place(st, tl)
    beat_verify(st, tl)
    beat_cut(st, tl)
    beat_filed(st, tl)
