"""Ch 10: Outro. Mirrors the Ch 0 seabed: the well is gone, the window gauge dissolves, camera rises, end card."""
from __future__ import annotations
import random

from scenes.common import palette as P, furniture as F

TITLE = "Outro: the empty seabed"


def beat_seabed(st, tl):
    b = tl["10.01"]
    s = b.sent
    rnd = random.Random(7)
    with st.span(b.start, b.end):
        top, bottom = 3.2, -12.0
        sea = st.rect(0, (top + bottom) / 2, 18, top - bottom, P.SEA, -0.2)
        rock = st.rect(0, bottom - 3.5, 18, 7.0, P.ROCK, -0.1)
        seabed = st.rect(0, bottom, 18, 0.07, P.SEABED, 0.0)
        surf = st.rect(0, top, 18, 0.06, P.PORE, 0.0)
        sky = st.rect(0, top + 3.0, 18, 6.0, P.BG, -0.15)
        for _ in range(60):
            x, y = rnd.uniform(-8, 8), rnd.uniform(bottom + 0.5, top - 0.5)
            c = st.circle(x, y, rnd.uniform(0.03, 0.08), "#a8c7ea", 0.1, alpha=rnd.uniform(0.15, 0.45))
            st.move(c, 0, b.end, dx=rnd.uniform(-0.3, 0.3), dy=rnd.uniform(0.2, 0.9), interp="LINEAR")
        # camera begins on the empty seabed (mirror of the opening shot) and slowly rises
        st.camera(0, 0.01, cy=bottom + 0.4, width=16)
        st.camera(b.end - 4.0, b.end - 0.5, cy=bottom + 5.0)
        # the window gauge from the opening dissolves into the seabed
        gx, gy = 0.0, bottom + 1.6
        kick = st.rect(gx, gy - 1.0, 0.9, 0.9, P.WATER, 0.3, alpha=0.9)
        green = st.rect(gx, gy, 0.9, 0.2, P.SAFE, 0.3, alpha=0.9)
        crack = st.rect(gx, gy + 1.0, 0.9, 0.9, P.FRAC, 0.3, alpha=0.9)
        gauge = [kick, green, crack]
        st.fade_in(gauge, b.start + 0.3, 0.5)
        st.fade_out(gauge, s[1] + 1.0, 2.0)
        st.fade_in(st.text("300 m", 5.6, bottom + 0.55, 0.4, P.TEXT, 0.2, kind="bold"), b.start + 0.2, 0.5)


def beat_endcard(st, tl):
    b = tl["10.02"]
    with st.span(b.start, b.end):
        st.camera(b.start - 0.02, b.start, cy=0.0, interp="CONSTANT")
        bg = st.rect(0, 0, 18, 10, P.BG, 0.0)
        t = st.text("THE HOLE THAT FIGHTS BACK", 0, 0.9, 0.7, P.TEXT, 0.3, kind="bold")
        l1 = st.text("Illustrative composite well: invented numbers, real physics.", 0, -0.4, 0.28, P.MUTED, 0.3)
        l2 = st.text("Norway-specific material is flagged [NO]. Verify any requirement against", 0, -0.95, 0.24, P.MUTED, 0.3)
        l3 = st.text("NORSOK D-010 and the current regulations before relying on it.", 0, -1.35, 0.24, P.MUTED, 0.3)
        st.fade_in([t, l1, l2, l3], b.start, 0.5)


def build(st, tl):
    beat_seabed(st, tl)
    beat_endcard(st, tl)
