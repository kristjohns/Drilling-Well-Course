"""Ch 0: Cold open.

0.01 a well whose rate has fallen from 1,000 to 600 m3/d; the fault is inside a pipe 14 cm wide and 4 km long that nobody can
     look into, full of oil at 200 bar: all we can do is lower something into it and work blind
0.02 the definition of well intervention, the two questions (WHY? HOW?), and the film title
"""
from __future__ import annotations
import numpy as np

from scenes.common import palette as P, model as M
from scenes.common.chart import Chart
from scenes.common import kit as K

TITLE = "Cold open"


def _rate_curve():
    ts = np.linspace(0, 11, 111)
    pts = [(0, 0), (0.35, 650), (1.0, 1120), (3.0, 1200), (6.0, 1160), (9.0, 1000), (10.0, 800), (11.0, 600)]
    xs, ys = zip(*pts)
    y = np.interp(ts, xs, ys)
    k = 5
    ypad = np.concatenate([np.full(k, y[0]), y, np.full(k, y[-1])])
    ys_s = np.convolve(ypad, np.ones(2 * k + 1) / (2 * k + 1), mode="valid")
    ys_s[0] = 0
    ys_s[-1] = 600
    return ts, ys_s


def b001(st, tl):
    b = tl["0.01"]
    s = b.sent
    with st.span(b.start, b.end):
        # ---- left: the decline curve
        ch = Chart(st, -6.2, -2.2, 5.4, 4.3, (0, 11), (0, 1300))
        fr = ch.frame(xticks=[0, 2, 4, 6, 8, 10], yticks=[0, 400, 800, 1200], xlabel="years on production", ylabel="oil rate (m³/d)",
                      fx="{:.0f}", fy="{:,.0f}", tick_size=0.18)
        st.fade_in(fr, b.start + 0.2, 0.5)
        ts, ys = _rate_curve()
        curve = ch.curve(ts, ys, P.OIL, 0.075, 0.4)
        st.draw_on(curve, s[0], s[1] + 1.0, "LINEAR")
        # 2 years ago / today markers
        y9, y11 = ch.pt(9, 1000), ch.pt(11, 600)
        d9 = st.circle(y9[0], y9[1], 0.11, P.TEXT, 0.5)
        d11 = st.circle(y11[0], y11[1], 0.11, P.BAD, 0.5)
        st.fade_in(d9, s[1] + 0.3, 0.3)
        st.fade_in(d11, s[2] + 0.2, 0.3)
        l9 = st.text("2 years ago", y9[0] - 0.12, y9[1] + 0.38, 0.2, P.TEXT, 0.5, align="r")
        c9 = st.counter(y9[0] - 0.12, y9[1] + 0.72, s[1] + 0.3, s[1] + 1.2, 0, 1000, "{:,.0f} m³/d", 0.24, P.TEXT, 0.5, align="r")
        l11 = st.text("today", y11[0] - 0.18, y11[1] - 0.38, 0.2, P.BAD, 0.5, align="r")
        c11 = st.counter(y11[0] - 0.18, y11[1] - 0.72, s[2] + 0.2, s[2] + 1.1, 1000, 600, "{:,.0f} m³/d", 0.24, P.BAD, 0.5, align="r")
        st.fade_in(l9, s[1] + 0.3, 0.3)
        st.fade_in(l11, s[2] + 0.2, 0.3)

        # ---- right: the well as a black box
        w = K.Well(st, cx=4.3, y_top=2.55, scale=0.88, rock_w=1.7)
        rock = w.rock()
        res = w.reservoir(3820, 4200)
        cem = w.cement()
        cas = w.casing()
        tub = w.tubing(bore_alpha=0.9)
        tree = w.tree()
        sea = w.seabed()
        well_objs = rock + res + cem + cas + tub + tree + sea + w.parts["bore"]
        st.fade_in(well_objs, s[3] - 0.2, 0.9)
        st.flow([(w.cx, w.y(3800)), (w.cx, w.y(0) + 0.1)], s[3] + 0.4, b.end - 0.5, P.OIL, n=10, speed=0.7, r=0.04)
        # the question mark in the middle of the well
        q = st.text("?", w.cx, w.y(2100), 1.1, P.WARN, 0.9, kind="bold")
        st.fade_in(q, s[3] + 0.5, 0.6)
        st.ripple(w.cx, w.y(2100), s[3] + 0.6, s[6], P.WARN, period=1.3, r0=0.2, r1=1.1)
        # callouts
        c1 = K.callout(st, "14 cm wide", 6.0, w.y(900), w.cx + 0.2, w.y(900), size=0.2, align="l")
        c2 = K.callout(st, "4 km long", 6.0, w.y(3000), w.cx + 0.2, w.y(3000), size=0.2, align="l")
        c3 = K.callout(st, "200 bar", 6.0, w.y(1700), w.cx + 0.2, w.y(1700), size=0.2, color=P.BAD, align="l")
        st.fade_in(c1, b.word(3, "fourteen centimetres", 1.0), 0.4)
        st.fade_in(c2, b.word(3, "four kilometres", 1.0), 0.4)
        st.fade_in(c3, b.word(6, "two hundred bar"), 0.4)
        # a person who cannot go in
        hx, hy = 1.3, 2.9
        person = [st.circle(hx, hy, 0.17, P.TEXT, 0.8, role="disc"),
                  st.rect(hx, hy - 0.45, 0.42, 0.55, P.TEXT, 0.8, role="flat")]
        st.fade_in(person, s[5], 0.4)
        x = K.xmark(st, hx, hy - 0.15, 0.42, s[5] + 0.7)
        lab = st.text("cannot go in", hx, hy - 1.1, 0.19, P.MUTED, 0.8)
        st.fade_in(lab, s[5] + 0.5, 0.3)
        # the thin line that goes in
        wire = st.rect(w.cx, w.y_top + 0.9, 0.035, 0.001, P.WIRE, 1.0, anchor="t", role="steel")
        st.fade_in(wire, s[7], 0.2)
        st.scale_to(wire, s[7] + 0.3, s[7] + 3.5, sy=w.y_top + 0.9 - w.y(1700))
        tip = st.circle(w.cx, w.y(1700), 0.09, P.WARN, 1.0)
        st.fade_in(tip, s[7] + 3.4, 0.3)
        st.move(tip, s[7] + 0.0, s[7] + 0.01, to=(w.cx, w.y_top + 0.9))
        st.move(tip, s[7] + 0.3, s[7] + 3.5, to=(w.cx, w.y(1700)))
        blind = st.text("working blind", w.cx - 1.35, w.y(1700) - 0.55, 0.22, P.MUTED, 1.0, align="r")
        st.fade_in(blind, b.word(7, "work blind"), 0.4)


def b002(st, tl):
    b = tl["0.02"]
    s = b.sent
    with st.span(b.start, b.end):
        # ---- the well with the line descending
        w = K.Well(st, cx=-4.6, y_top=2.55, scale=0.88, rock_w=1.6)
        base = w.rock() + w.reservoir(3820, 4200) + w.cement() + w.casing() + w.tubing(bore_alpha=0.9) + w.tree() + w.seabed() + w.parts["bore"]
        perf = w.perfs(n=5)
        base = base + perf
        wire = st.rect(w.cx, w.y_top + 0.9, 0.035, w.y_top + 0.9 - w.y(3500), P.WIRE, 1.0, anchor="t", role="steel")
        st.scale_to(wire, s[0] + 0.3, s[0] + 6.0, sy=w.y_top + 0.9 - w.y(3990))
        tip = st.circle(w.cx, w.y(3500), 0.09, P.WARN, 1.0)
        st.move(tip, s[0] + 0.3, s[0] + 6.0, to=(w.cx, w.y(3990)))
        glow = st.circle(w.cx + 0.55, w.y(4000), 0.2, P.OIL, 0.9)
        st.fade_in(glow, s[0] + 6.0, 0.5)
        part_glow = [glow]
        # ---- WHY? / HOW?
        why = st.text("WHY?", -0.4, 1.7, 1.05, P.PORE, 1.0, kind="bold")
        how = st.text("HOW?", -0.4, -0.2, 1.05, P.WARN, 1.0, kind="bold")
        st.fade_in(why, s[3], 0.5)
        st.fade_in(how, s[4], 0.5)
        # three icons under HOW: a wire on a drum, a reel of tube, a derrick
        ix = [-1.6, -0.2, 1.2]
        iy = -1.55
        drum_ = K.drum(st, ix[0], iy, 0.42, turns=3)
        reel = K.drum(st, ix[1], iy, 0.42, turns=5, color=P.STEEL)
        derr = [st.line([(ix[2] - 0.4, iy - 0.45), (ix[2], iy + 0.5), (ix[2] + 0.4, iy - 0.45)], P.STEEL, 0.05, 1.0, role="hair"),
                st.line([(ix[2] - 0.26, iy - 0.1), (ix[2] + 0.26, iy - 0.1)], P.STEEL, 0.03, 1.0, role="hair"),
                st.line([(ix[2] - 0.15, iy + 0.22), (ix[2] + 0.15, iy + 0.22)], P.STEEL, 0.03, 1.0, role="hair")]
        labs = [st.text("wire", ix[0], iy - 0.75, 0.19, P.MUTED, 1.0), st.text("coiled tube", ix[1], iy - 0.75, 0.19, P.MUTED, 1.0),
                st.text("rig", ix[2], iy - 0.75, 0.19, P.MUTED, 1.0)]
        t_icons = [b.word(4, "on a wire"), b.word(4, "coiled steel tube"), b.word(4, "a rig")]
        for t_, g in zip(t_icons, [drum_.all(), reel.all(), derr]):
            st.fade_in(g, t_, 0.4)
        for t_, l in zip(t_icons, labs):
            st.fade_in(l, t_, 0.4)
        # ---- title card over everything for the last sentence
        T = s[5] + 0.3
        shade = st.rect(0, 0, 16.5, 9.5, P.BG, 30.0, role="backdrop")
        st.fade_in(shade, T, 1.0)
        big = st.text("INTO THE LIVE WELL", 0, 0.35, 0.95, P.TEXT, 31.0, kind="bold")
        sub = st.text("why and how we intervene in producing wells", 0, -0.55, 0.3, P.MUTED, 31.0)
        rule = st.line([(-3.2, -0.12), (3.2, -0.12)], P.PORE, 0.05, 31.0)
        st.fade_in(big, T + 0.6, 0.8)
        st.fade_in(sub, T + 1.4, 0.8)
        st.draw_on(rule, T + 0.8, T + 1.8, "BEZIER")


def build(st, tl):
    b001(st, tl)
    b002(st, tl)
