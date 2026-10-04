"""Recurring on-screen furniture: chapter header, 'well so far' strip, term cards, scope badges.

Layout (world units, canvas 16 x 9, centre 0,0):
  header      x -7.85.., y 4.15            (chapter label, small, top-left)
  well strip  x -7.85 .. -6.55             (persistent depth ruler + casing so far)
  content     x -6.3 .. 7.8,  y -3.5 .. 3.9
  term card   top-right,  x 3.4 .. 7.85, y 3.0 .. 4.4
  badges      right edge, y -3.3           (above the burned-in subtitle band at y < -3.7)
"""
from __future__ import annotations

from . import palette as P
from . import well_model as M

STRIP_CX = -7.15
STRIP_Y_TOP, STRIP_Y_BOT = 3.55, -3.4


def depth_y(z: float) -> float:
    return STRIP_Y_TOP - z * (STRIP_Y_TOP - STRIP_Y_BOT) / M.TD


def header(st, tl, t0=0.0, t1=None):
    t1 = tl.dur if t1 is None else t1
    with st.span(t0, t1):
        a = st.text(f"CH {tl.num}", -7.85, 4.18, 0.26, P.PORE, 0.5, align="l", kind="bold")
        b = st.text(tl.title.upper(), -7.2, 4.18, 0.26, P.MUTED, 0.5, align="l", kind="bold")
        st.fade_in([a, b], t0 + 0.2, 0.4)


# string label -> (od width in strip units, colour)
_STRIP_WIDTH = {"30in conductor": 0.56, "20in surface casing": 0.44, "13-3/8in intermediate": 0.34, "9-5/8in intermediate": 0.24}


def well_strip(st, t0, t1, strings=(), marker=None, td=False, plugs=(), cut_below_seabed=False, show_reservoir=True):
    """Persistent mini-schematic of the well so far. strings: names from well_model.programme() to draw."""
    with st.span(t0, t1):
        objs = []
        objs.append(st.rect(STRIP_CX, (STRIP_Y_TOP + STRIP_Y_BOT) / 2, 1.3, STRIP_Y_TOP - STRIP_Y_BOT + 0.15, P.PANEL, 0.0))
        # sea + rock
        ys, yb = depth_y(0), depth_y(M.WATER_DEPTH)
        objs.append(st.rect(STRIP_CX, (ys + yb) / 2, 1.2, ys - yb, P.SEA, 0.05))
        objs.append(st.rect(STRIP_CX, (yb + depth_y(M.TD)) / 2, 1.2, yb - depth_y(M.TD), P.ROCK, 0.05))
        if show_reservoir:
            objs.append(st.rect(STRIP_CX, (depth_y(M.RES_TOP) + depth_y(M.RES_BASE)) / 2, 1.2, depth_y(M.RES_TOP) - depth_y(M.RES_BASE), P.SAND, 0.06))
        for zt in (0, 1000, 2000, 3000, 4000):
            objs.append(st.text(f"{zt:,}", STRIP_CX - 0.58, depth_y(zt) + 0.12, 0.15, P.TEXT, 0.2, align="l"))
            objs.append(st.rect(STRIP_CX, depth_y(zt), 1.2, 0.01, P.GRID, 0.07))
        objs.append(st.text("depth (m)", STRIP_CX, depth_y(0) + 0.2, 0.13, P.MUTED, 0.2))
        by_name = {s.name: s for s in M.programme()}
        for name in strings:
            s = by_name[name]
            wd = _STRIP_WIDTH[name]
            top = depth_y(M.WATER_DEPTH)
            bot = depth_y(s.shoe)
            for sx in (-1, 1):
                objs.append(st.rect(STRIP_CX + sx * wd / 2, (top + bot) / 2, 0.04, top - bot, P.STEEL, 0.1))
            objs.append(st.poly([(STRIP_CX - wd / 2 - 0.07, bot), (STRIP_CX - wd / 2 + 0.03, bot), (STRIP_CX - wd / 2 + 0.03, bot + 0.1)], P.STEEL, 0.11))
            objs.append(st.poly([(STRIP_CX + wd / 2 + 0.07, bot), (STRIP_CX + wd / 2 - 0.03, bot), (STRIP_CX + wd / 2 - 0.03, bot + 0.1)], P.STEEL, 0.11))
        if marker is not None:
            y = depth_y(marker)
            objs.append(st.poly([(STRIP_CX + 0.66, y), (STRIP_CX + 0.9, y + 0.1), (STRIP_CX + 0.9, y - 0.1)], P.WARN, 0.3))
            objs.append(st.text(f"{marker:,.0f} m", STRIP_CX + 0.95, y, 0.17, P.WARN, 0.3, align="l"))
        for (z0, z1) in plugs:
            objs.append(st.rect(STRIP_CX, (depth_y(z0) + depth_y(z1)) / 2, 0.16, abs(depth_y(z0) - depth_y(z1)), P.SAFE, 0.2))
        objs.append(st.text("WELL SO FAR", STRIP_CX, STRIP_Y_BOT - 0.2, 0.15, P.MUTED, 0.2, kind="bold"))
        return objs


def term_card(st, t0, d, term, definition, slot=0):
    """Top-right card shown when a term is first defined in the narration."""
    y = 3.62 - slot * 1.0
    with st.span(t0, t0 + d):
        parts = [
            st.rect(5.6, y, 4.5, 0.9, P.PANEL2, 0.6),
            st.rect(3.37, y, 0.07, 0.9, P.PORE, 0.61),
            st.text("NEW TERM", 3.55, y + 0.31, 0.14, P.PORE, 0.62, align="l", kind="bold"),
            st.text(term.upper(), 3.55, y + 0.1, 0.24, P.TEXT, 0.62, align="l", kind="bold"),
            st.text(definition, 3.55, y - 0.14, 0.15, P.MUTED, 0.62, align="l", valign="t", wrap=60),
        ]
        st.fade_in(parts, t0, 0.3)
        st.fade_out(parts, t0 + d - 0.35, 0.3)


def badge(st, t0, t1, label, color, y, x=7.85):
    with st.span(t0, t1):
        w = 0.17 * len(label) * 0.62 + 0.4
        parts = [st.rect(x - w / 2, y, w, 0.34, color, 0.7), st.text(label, x - w / 2, y, 0.17, "#0b1220", 0.71, kind="bold")]
        st.fade_in(parts, t0, 0.25)
        return parts


def auto_overlays(st, tl):
    """Term cards + scope badges for every beat, straight from the script (so they can never drift)."""
    for b in tl.beats:
        slot = 0
        for t in b.terms[:2]:
            term_card(st, b.start + 0.5, min(max(b.dur - 1.0, 3.0), 9.0), t["term"], t["def"], slot)
            slot += 1
        y = -3.28
        if "NO" in b.scope:
            badge(st, b.start + 0.3, b.end - 0.2, "NORWAY / NORSOK-SPECIFIC", P.NO_BADGE, y)
            y += 0.42
        if b.sim:
            badge(st, b.start + 0.3, b.end - 0.2, "SIMPLIFIED", P.SIM_BADGE, y)
