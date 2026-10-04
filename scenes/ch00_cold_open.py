"""Ch 0: Cold open. Seabed descent -> the mud-weight slider (kick vs crack) -> the narrowing window -> the question."""
from __future__ import annotations
import math
import random

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.shapes import pill

TITLE = "Cold open: the window"


# ---------------------------------------------------------------- 0.01 seabed descent
def beat_descent(st, tl):
    b = tl["0.01"]
    s = b.sent
    rnd = random.Random(7)
    with st.span(b.start, b.end):
        top, bottom = 3.2, -12.0                   # sea surface y, seabed y (world units; 300 m shown compressed)
        sea = st.rect(0, (top + bottom) / 2, 18, top - bottom, P.SEA, -0.2)
        rock = st.rect(0, bottom - 3.5, 18, 7.0, P.ROCK, -0.1)
        seabed = st.rect(0, bottom, 18, 0.07, P.SEABED, 0.0)
        surf = st.rect(0, top, 18, 0.06, P.PORE, 0.0)
        sky = st.rect(0, top + 3.0, 18, 6.0, P.BG, -0.15)
        # depth ticks along the way
        ticks = []
        for i in range(0, 6):
            y = top - i * (top - bottom) / 5
            ticks.append(st.rect(-7.3, y, 0.5, 0.025, P.MUTED, 0.1))
            ticks.append(st.text(f"{i * 60} m", -6.9, y, 0.22, P.MUTED, 0.1, align="l"))
        # drifting particles (marine snow)
        parts = []
        for _ in range(70):
            x, y = rnd.uniform(-8, 8), rnd.uniform(bottom + 0.5, top - 0.5)
            c = st.circle(x, y, rnd.uniform(0.03, 0.08), "#a8c7ea", 0.1, alpha=rnd.uniform(0.15, 0.45))
            parts.append(c)
            st.move(c, 0, b.end, dx=rnd.uniform(-0.3, 0.3), dy=rnd.uniform(0.2, 0.9), interp="LINEAR")
        st.camera(0, 0.01, cy=0.4, width=16)
        st.camera(1.0, b.start + 9.5, cy=bottom + 0.4)
        # seabed label + title at the bottom
        sl = st.text("300 m", 5.6, bottom + 0.55, 0.4, P.TEXT, 0.2, kind="bold")
        title = st.text("THE HOLE THAT FIGHTS BACK", 0, bottom + 2.6, 0.7, P.TEXT, 0.3, kind="bold")
        sub = st.text("how an offshore exploration well is drilled, judged, and erased", 0, bottom + 1.85, 0.27, P.MUTED, 0.3)
        st.fade_in([sl], b.start + 9.0, 0.6)
        st.fade_in([title, sub], s[1] + 0.2, 0.9)
        st.fade_out([title, sub], b.end - 2.0, 1.2)
        # the camera lingers on the empty seabed; chapter 10 mirrors this shot.
        # Hard cut back to the origin for every later beat (CONSTANT: jumps at the second key).
        st.camera(b.end - 0.02, b.end, cy=0.0, interp="CONSTANT")


# ---------------------------------------------------------------- 0.02 / 0.03 slider scene
def beat_slider(st, tl):
    b2, b3 = tl["0.02"], tl["0.03"]
    s2, s3 = b2.sent, b3.sent
    t0, t1 = b2.start, b3.end
    with st.span(t0, t1):
        # strata + hole (cutaway)
        layers = [(3.0, 1.6, P.ROCK2), (1.6, 0.4, P.ROCK), (0.4, -0.9, P.SHALE), (-0.9, -2.0, P.SAND), (-2.0, -3.4, P.ROCK)]
        rock = [st.rect(-2.2, (a + c) / 2, 6.2, a - c, col, 0.0) for a, c, col in layers]
        hole_x, hole_w = -2.2, 1.0
        hole_bg = st.rect(hole_x, -0.2, hole_w, 6.4, P.BG, 0.05)
        mud = st.rect(hole_x, -3.4, hole_w, 6.4, P.MUD, 0.1, anchor="b")
        st.fade_in(rock + [hole_bg, mud], t0, 0.6)
        badge = pill(st, -5.1, 3.65, "ILLUSTRATIVE WELL", P.PANEL2, P.WARN, 0.2, 0.5, align="l")
        st.fade_in(badge, s2[1] + 0.5, 0.5)
        # slider
        track = st.rect(3.2, 0.0, 0.14, 5.2, P.GRID, 0.2)
        knob = st.circle(3.2, 0.0, 0.26, P.TEXT, 0.3)
        lt = st.text("light", 3.9, -2.4, 0.25, P.PORE, 0.2, align="l", kind="bold")
        hv = st.text("heavy", 3.9, 2.4, 0.25, P.FRAC, 0.2, align="l", kind="bold")
        cap = st.text("weight of the mud", 3.2, 3.2, 0.28, P.TEXT, 0.2, kind="bold")
        st.fade_in([track, knob, lt, hv, cap], s2[1], 0.6)
        # idle wiggle on "we choose how heavy"
        st.move(knob, s2[2], s2[2] + 1.2, dy=0.8)
        st.move(knob, s2[2] + 1.2, s2[2] + 2.4, dy=-0.8)
        # 0.03: rock pressure arrows
        arrows = []
        for y in (-1.6, -0.9, -0.1, 0.8, -2.5):
            arrows += st.arrow(-4.3, y, -3.55, y, P.WATER, 0.07, 0.24, 0.35)
            arrows += st.arrow(-0.1, y, -0.85, y, P.WATER, 0.07, 0.24, 0.35)
        st.fade_in(arrows, s3[0], 0.5)
        press = st.text("rock pressure", -5.1, 1.9, 0.26, P.WATER, 0.3, align="l", kind="bold")
        st.fade_in(press, s3[0], 0.5)
        # too light: knob down, mud turns pale, arrows push in, KICK
        st.move(knob, s3[1], s3[1] + 1.5, dy=-1.6)
        st.recolor(mud, s3[1], s3[1] + 1.5, "#ffe9a6")
        for a in arrows:
            pass
        st.move(arrows, s3[1] + 1.0, s3[1] + 2.4, dx=0.0)   # arrows pulse in place; the kick label does the talking
        kick = st.text("KICK", hole_x, 0.2, 0.9, P.BAD, 0.6, kind="bold")
        st.fade_in(kick, s3[1] + 0.8, 0.3)
        st.fade_out(kick, s3[1] + 2.6, 0.5)
        # too heavy: knob up, mud darkens, cracks open, level drops
        st.move(knob, s3[2], s3[2] + 2.0, dy=3.2)
        st.recolor(mud, s3[2], s3[2] + 2.0, P.KILL_MUD)
        cracks = []
        for (x0, y0, sgn) in ((-2.75, 0.8, -1), (-2.75, -0.9, -1), (-1.65, 0.4, 1), (-1.65, -1.6, 1)):
            cr = st.line([(x0, y0), (x0 + sgn * 0.5, y0 + 0.25), (x0 + sgn * 0.9, y0 + 0.1), (x0 + sgn * 1.4, y0 + 0.4)], P.BAD, 0.08, 0.4)
            cracks.append(cr)
            st.draw_on(cr, s3[2] + 1.2, s3[2] + 2.6)
        st.scale_to(mud, s3[2] + 3.4, s3[2] + 6.0, sy=2.2)         # level drops as fluid drains into the cracks
        lvl = st.text("level drops", hole_x + 1.0, 0.6, 0.24, P.BAD, 0.5, align="l", kind="bold")
        st.fade_in(lvl, s3[2] + 3.6, 0.4)
        st.move(knob, s3[2] + 6.0, s3[2] + 7.0, dy=-3.0)
        again = st.text("too light again", hole_x, 1.4, 0.4, P.BAD, 0.6, kind="bold")
        st.fade_in(again, s3[2] + 6.2, 0.4)


# ---------------------------------------------------------------- 0.04 the narrowing window
def beat_window(st, tl):
    b = tl["0.04"]
    s = b.sent
    with st.span(b.start, b.end):
        gx, gy0, gy1, gw = -1.2, -3.0, 3.2, 1.2
        kick_z = st.rect(gx, gy0, gw, 0.0001, P.WATER, 0.1, anchor="b")
        crack_z = st.rect(gx, gy1, gw, 0.0001, P.FRAC, 0.1, anchor="t")
        green = st.rect(gx, 0.1, gw, 2.4, P.SAFE, 0.12)
        st.scale_to(kick_z, s[0], s[0] + 1.0, sy=2.8)
        st.scale_to(crack_z, s[0], s[0] + 1.0, sy=2.8)
        st.fade_in(green, s[0], 0.5)
        kl = st.text("KICK", gx + 1.4, -2.3, 0.4, P.WATER, 0.3, align="l", kind="bold")
        cl = st.text("CRACK", gx + 1.4, 2.5, 0.4, P.FRAC, 0.3, align="l", kind="bold")
        st.fade_in([kl, cl], s[0] + 0.5, 0.5)
        # the window narrows
        st.scale_to(green, s[1], s[1] + 3.0, sy=0.9)
        st.move(green, s[1], s[1] + 3.0, dy=0.0)
        a = st.text("our well, at the bottom:\n0.22 sg of 1.62 sg ≈ 1/7", gx - 1.5, 0.1, 0.3, P.SAFE, 0.3, align="r", kind="bold")
        st.fade_in(a, s[1] + 0.5, 0.5)
        h = st.text("hottest, highest-pressure wells:\na few hundredths", gx - 1.5, -1.6, 0.26, P.WARN, 0.3, align="r")
        st.fade_in(h, s[2] + 0.3, 0.5)
        st.scale_to(green, s[2], s[2] + 2.5, sy=0.18)
        q = st.text("how do you stay inside it?", gx + 3.8, 0.1, 0.42, P.TEXT, 0.3, kind="bold")
        st.fade_in(q, s[3], 0.6)


# ---------------------------------------------------------------- 0.05 the question
def beat_question(st, tl):
    b = tl["0.05"]
    s = b.sent
    with st.span(b.start, b.end):
        l1 = st.text("How do you drill four kilometres below the seabed,", 0.8, 1.2, 0.46, P.TEXT, 0.3, kind="bold")
        l2 = st.text("through rock that wants to collapse or blow out,", 0.8, 0.5, 0.46, P.TEXT, 0.3, kind="bold")
        l3 = st.text("then leave the hole so safe nobody ever has to think about it again?", 0.8, -0.3, 0.38, P.PORE, 0.3, kind="bold")
        st.fade_in(l1, s[0], 0.6)
        st.fade_in(l2, s[0] + 2.2, 0.6)
        st.fade_in(l3, s[0] + 4.4, 0.6)
        st.fade_in(st.text("First, a plan.", 0.8, -1.5, 0.5, P.WARN, 0.3, kind="bold"), s[1], 0.6)
    strip = F.well_strip(st, b.start, tl.dur, strings=[])
    st.fade_in(strip, b.start + 0.4, 0.8)


def build(st, tl):
    beat_descent(st, tl)
    beat_slider(st, tl)
    beat_window(st, tl)
    beat_question(st, tl)
