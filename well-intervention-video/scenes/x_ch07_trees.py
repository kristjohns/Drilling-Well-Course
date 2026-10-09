"""Ch 7, beat 7.02: vertical and horizontal subsea trees, and why it matters for intervention.

Both drawn procedurally as cutaways.
  Vertical tree: the tubing hanger sits in the wellhead; the tree stacks on top with the master valves, the swab valve and the
  tree cap in line with the bore, and the wing valve on the side branch. Tools go straight down. The tree lifts off alone.
  Horizontal tree: the hanger lands inside the tree body; its side port lines up with the tree's side outlet, where the master
  and wing valves sit, horizontally. The vertical bore is closed by crown plugs, which must be pulled through the equipment
  on top before a tool can go down. The tree cannot be lifted without pulling the hanger and the tubing with it.
"""
from __future__ import annotations
import math

from scenes.common import palette as P
from scenes.common import kit as K
from scenes.common import pdraw as D
from scenes.common.look import darken, lighten
from scenes.common.stage import hex_rgb


def _gate(c, look, x, y, a, open_=1.0, horizontal=False, s=1.0, color=P.STEEL_DK, hl=0.0):
    """Gate valve on a bore at (x, y). Vertical bore: the gate slides sideways; horizontal bore: the gate slides up/down."""
    bore_dark = darken(hex_rgb(P.BG), 0.3)
    if not horizontal:
        D.steel(c, x - 0.42 * s, y - 0.17 * s, x + 0.42 * s, y + 0.17 * s, color, a)
        D.fill(c, x - 0.17 * s, y - 0.17 * s, x + 0.17 * s, y + 0.17 * s, bore_dark, a)
        g_off = 0.36 * s * open_
        D.flat(c, x - 0.17 * s - g_off, y - 0.1 * s, x + 0.17 * s - g_off, y + 0.1 * s, P.WARN if open_ > 0.5 else P.STEEL, a, r=0.02)
        D.steel(c, x - 0.75 * s, y - 0.05 * s, x - 0.42 * s, y + 0.05 * s, P.STEEL, a)
        D.flat(c, x - 0.82 * s, y - 0.12 * s, x - 0.75 * s, y + 0.12 * s, P.STEEL_DK, a)
    else:
        D.steel(c, x - 0.17 * s, y - 0.42 * s, x + 0.17 * s, y + 0.42 * s, color, a)
        D.fill(c, x - 0.17 * s, y - 0.17 * s, x + 0.17 * s, y + 0.17 * s, bore_dark, a)
        g_off = 0.36 * s * open_
        D.flat(c, x - 0.1 * s, y - 0.17 * s + g_off, x + 0.1 * s, y + 0.17 * s + g_off, P.WARN if open_ > 0.5 else P.STEEL, a, r=0.02)
        D.steel(c, x - 0.05 * s, y + 0.42 * s, x + 0.05 * s, y + 0.75 * s, P.STEEL, a)
        D.flat(c, x - 0.12 * s, y + 0.75 * s, x + 0.12 * s, y + 0.82 * s, P.STEEL_DK, a)
    if hl > 0:
        D.glow(c, look, x, y, 0.5 * s, P.WARN, 0.35 * hl * a)


def b702(st, tl):
    b = tl["7.02"]
    s = b.sent
    with st.span(b.start, b.end):
        vx, hx = -4.3, 1.75
        sea_top = 3.35
        y_sb = -1.95                                       # seabed
        T0 = b.start + 0.2
        # timings
        t_vlift0, t_vlift1 = s[5] + 0.6, s[5] + 2.4
        t_hlift0, t_hlift1 = s[6] + 0.8, s[6] + 2.8
        t_plugs0 = b.word(4, "must be pulled") - 0.2
        t_plug1 = (t_plugs0 + 0.4, t_plugs0 + 2.0)
        t_plug2 = (t_plugs0 + 1.4, t_plugs0 + 3.0)
        t_tool_h = (t_plugs0 + 3.0, s[5] - 0.2)

        def draw(c, t, look):
            a = D.vis(t, T0, None, 0.5)
            if a <= 0:
                return
            bore_dark = darken(hex_rgb(P.BG), 0.3)
            # sea and seabed
            D.gradient_rect_v(c, -7.9, y_sb, 7.9, sea_top, darken(hex_rgb(P.SEA), 0.35), darken(hex_rgb(P.SEA), 0.1), 0.45 * a)
            D.fill(c, -7.9, -3.6, 7.9, y_sb, P.ROCK, 0.5 * a)
            D.fill(c, -7.9, y_sb - 0.05, 7.9, y_sb + 0.04, P.SEABED, 0.9 * a)
            # ================================================================== vertical tree
            av = a * D.vis(t, T0, None, 0.5)
            lift = 0.95 * D.ramp(t, t_vlift0, t_vlift1)
            # conductor / wellhead housing below the seabed
            D.steel(c, vx - 0.95, -3.6, vx + 0.95, y_sb + 0.25, P.STEEL_DK, av)
            D.fill(c, vx - 0.36, -3.6, vx + 0.36, y_sb + 0.25, bore_dark, av)
            # tubing (stays) and hanger in the wellhead
            D.fluid(c, vx - 0.17, -3.6, vx + 0.17, y_sb + 0.1, P.OIL, 0.35 * av)
            for sd in (-1, 1):
                D.steel(c, vx + sd * 0.17, -3.6, vx + sd * 0.25, y_sb - 0.25, P.STEEL, av)
                D.flat(c, vx + sd * 0.17, y_sb - 0.25, vx + sd * 0.36, y_sb + 0.1, P.PRIMARY_B, av, r=0.02)
            # the tree (lifts at s5)
            yb = y_sb + 0.25 + lift
            D.steel(c, vx - 0.75, yb, vx + 0.75, yb + 0.3, P.STEEL, av)                 # connector
            D.steel(c, vx - 0.4, yb + 0.3, vx + 0.4, yb + 3.25, P.STEEL_DK, av)          # block
            D.fill(c, vx - 0.17, yb, vx + 0.17, yb + 3.25, bore_dark, av)
            # wing branch
            yw = yb + 1.75
            D.steel(c, vx + 0.4, yw - 0.13, vx + 2.1, yw + 0.13, P.STEEL_DK, av)
            D.fill(c, vx + 0.17, yw - 0.06, vx + 2.1, yw + 0.06, bore_dark, av)
            hl = lambda w: D.vis(t, b.word(1, w) - 0.1, b.word(1, w) + 1.6, 0.2) if w else 0.0
            _gate(c, look, vx, yb + 0.75, av, open_=1.0, hl=hl("master valves"))
            _gate(c, look, vx, yb + 1.3, av, open_=1.0, hl=hl("master valves"))
            _gate(c, look, vx + 1.35, yw, av, open_=1.0, horizontal=True)
            _gate(c, look, vx, yb + 2.35, av, open_=1.0)
            D.steel(c, vx - 0.36, yb + 2.85, vx + 0.36, yb + 3.25, P.STEEL, av)          # tree cap
            # tool path straight down
            if s[2] - 0.2 < t < s[3] + 0.5:
                f = D.lin(t, s[2], s[2] + 1.6)
                y_tip = yb + 3.6 - f * (3.6 + (yb - (-3.3)))
                D.arrow(c, vx, yb + 3.6, vx, y_tip, P.SAFE, 0.07, 0.24, av * D.vis(t, s[2] - 0.2, s[3] + 0.2, 0.3))
            # ================================================================== horizontal tree
            ah = a * D.vis(t, s[3] - 0.4, None, 0.5)
            if ah > 0:
                hlift = 0.95 * D.ramp(t, t_hlift0, t_hlift1)
                D.steel(c, hx - 0.95, -3.6, hx + 0.95, y_sb + 0.25, P.STEEL_DK, ah)
                D.fill(c, hx - 0.36, -3.6, hx + 0.36, y_sb + 0.25, bore_dark, ah)
                # tubing (comes up with the tree at s6)
                D.fluid(c, hx - 0.17, -3.6, hx + 0.17, y_sb + 0.5 + hlift, P.OIL, 0.35 * ah)
                for sd in (-1, 1):
                    D.steel(c, hx + sd * 0.17, -3.6 + hlift, hx + sd * 0.25, y_sb + 0.75 + hlift, P.STEEL, ah)
                ybh = y_sb + 0.25 + hlift
                # tree body (spool) with a side outlet
                D.steel(c, hx - 0.95, ybh, hx + 0.95, ybh + 2.7, P.STEEL_DK, ah)
                D.fill(c, hx - 0.36, ybh, hx + 0.36, ybh + 2.7, bore_dark, ah)
                yo = ybh + 0.95
                D.steel(c, hx + 0.95, yo - 0.16, hx + 3.15, yo + 0.16, P.STEEL_DK, ah)
                D.fill(c, hx + 0.36, yo - 0.07, hx + 3.15, yo + 0.07, bore_dark, ah)
                # the hanger inside the tree: side port lined up with the outlet
                D.flat(c, hx - 0.36, ybh + 0.5, hx - 0.17, ybh + 1.35, P.PRIMARY_B, ah, r=0.02)
                D.flat(c, hx + 0.17, ybh + 0.5, hx + 0.36, yo - 0.07, P.PRIMARY_B, ah, r=0.02)
                D.flat(c, hx + 0.17, yo + 0.07, hx + 0.36, ybh + 1.35, P.PRIMARY_B, ah, r=0.02)
                D.fill(c, hx - 0.17, ybh + 0.5, hx + 0.17, ybh + 1.35, P.OIL, 0.35 * ah)
                # valves on the side outlet (master and wing), horizontal bore
                _gate(c, look, hx + 1.55, yo, ah, open_=1.0, horizontal=True, hl=D.vis(t, b.word(4, "side outlet") - 0.1, b.word(4, "side outlet") + 1.6, 0.2))
                _gate(c, look, hx + 2.45, yo, ah, open_=1.0, horizontal=True, hl=D.vis(t, b.word(4, "side outlet") - 0.1, b.word(4, "side outlet") + 1.6, 0.2))
                # crown plugs (pulled at s4) and the equipment on top
                for (y_p, (p0, p1)) in ((ybh + 1.55, t_plug1), (ybh + 2.3, t_plug2)):
                    up = D.ramp(t, p0, p1) * 5.5
                    pa = ah * (1.0 - D.lin(t, p1 - 0.3, p1))
                    if pa > 0:
                        D.steel(c, hx - 0.33, y_p - 0.16 + up, hx + 0.33, y_p + 0.16 + up, P.STEEL, pa)
                        D.fill(c, hx - 0.33, y_p - 0.05 + up, hx + 0.33, y_p + 0.05 + up, P.RUBBER, pa)
                # intervention stack on top (from s4 until the tree is lifted)
                sa = ah * D.vis(t, t_plugs0 - 0.6, t_hlift0 - 0.4, 0.4)
                if sa > 0:
                    yt = ybh + 2.7
                    D.steel(c, hx - 0.75, yt, hx + 0.75, yt + 0.8, P.STEEL_DK, sa)
                    D.fill(c, hx - 0.2, yt, hx + 0.2, yt + 0.8, bore_dark, sa)
                    for sd in (-1, 1):
                        D.flat(c, hx + sd * 0.2, yt + 0.3, hx + sd * 0.72, yt + 0.5, P.BAD, sa, r=0.02)
                    D.steel(c, hx - 0.2, yt + 0.8, hx + 0.2, 3.05, P.STEEL, sa)
                # tool path once the plugs are out
                if t_tool_h[0] < t < t_tool_h[1] + 0.4:
                    f = D.lin(t, t_tool_h[0], t_tool_h[0] + 1.6)
                    y0_ = ybh + 3.6
                    D.arrow(c, hx, y0_, hx, y0_ - f * (y0_ + 3.3), P.SAFE, 0.07, 0.24, ah * D.vis(t, t_tool_h[0], t_tool_h[1], 0.3))
                # flow leaves by the side
                if s[4] < t < t_plugs0:
                    pass

        st.procedural(b.start, b.end, 0.4, draw)
        # oil leaving through the outlets
        st.flow([(vx, -3.4), (vx, y_sb + 0.25 + 1.75), (vx + 2.1, y_sb + 0.25 + 1.75)], b.start + 0.6, s[2] - 0.3, P.OIL, n=8, speed=0.6, r=0.04, z=0.45)
        st.flow([(hx, -3.4), (hx, y_sb + 0.25 + 0.95), (hx + 3.15, y_sb + 0.25 + 0.95)], s[4] - 0.2, b.word(4, "must be pulled") - 0.4, P.OIL, n=8, speed=0.6, r=0.04, z=0.45)

        # ------------------------------------------------------------------ titles and labels
        K.show(st, [st.text("VERTICAL TREE", vx + 0.5, 3.5, 0.26, P.TEXT, 0.8, kind="bold")], s[1] - 0.3, None, 0.4)
        K.show(st, [st.text("HORIZONTAL TREE", hx + 1.0, 3.5, 0.26, P.TEXT, 0.8, kind="bold")], s[3] - 0.3, None, 0.4)
        yb0 = y_sb + 0.25
        lv = [("tubing hanger in the wellhead", vx + 1.15, y_sb - 0.45, vx + 0.36, y_sb - 0.1, b.word(1, "tubing hanger"), s[3]),
              ("master valves", vx - 1.1, yb0 + 1.02, vx - 0.82, yb0 + 1.02, b.word(1, "master valves"), s[3]),
              ("swab valve", vx - 1.1, yb0 + 2.35, vx - 0.82, yb0 + 2.35, b.word(1, "master valves") + 0.8, s[3]),
              ("wing valve", vx + 2.25, yb0 + 2.35, vx + 1.35, yb0 + 1.75 + 0.82, b.word(1, "master valves") + 1.2, s[3])]
        for text, x, y, tx, ty, t0, t1 in lv:
            K.show(st, K.callout(st, text, x, y, tx, ty, size=0.17, align="r" if x < vx else "l", z=1.1), t0, t1, 0.35)
        K.show(st, K.note(st, "tools go straight down", vx + 0.3, 2.55, 0.19, P.SAFE, align="l"), s[2], s[3] + 0.3, 0.35)
        lh = [("hanger inside the tree", hx - 1.1, yb0 + 0.9, hx - 0.36, yb0 + 0.9, b.word(4, "tubing hanger sits"), s[5]),
              ("valves on the side outlet", hx + 3.3, yb0 + 0.95 + 0.6, hx + 2.45, yb0 + 0.95 + 0.82, b.word(4, "side outlet"), s[5]),
              ("crown plugs close the bore", hx - 1.1, yb0 + 1.95, hx - 0.33, yb0 + 1.95, b.word(4, "closed by plugs"), s[5])]
        for text, x, y, tx, ty, t0, t1 in lh:
            K.show(st, K.callout(st, text, x, y, tx, ty, size=0.17, align="r" if x < hx else "l", z=1.1), t0, t1, 0.35)
        K.show(st, K.tag(st, hx + 0.9, yb0 + 3.25, "plugs pulled through the stack", color=P.WARN, fg=P.BG, size=0.17, z=1.1, align="l"),
               t_plugs0 + 0.3, s[5], 0.35)
        K.show(st, K.tag(st, vx - 1.1, 2.6, "lifts off alone: the completion stays", color=P.SAFE, fg=P.BG, size=0.18, z=1.1, align="l"), s[5] + 0.4, None, 0.35)
        K.show(st, K.tag(st, hx + 0.6, -2.6, "the hanger and tubing come with it", color=P.BAD, fg=P.BG, size=0.18, z=1.1, align="l"), s[6] + 0.6, None, 0.35)
