"""Reusable assemblies built from Stage primitives: pill labels, cross arrows, a rock/hole/pipe cutaway."""
from __future__ import annotations

from . import palette as P
from .stage import TEXT_SCALE, MIN_TEXT


def pill(st, x, y, text, bg=P.PANEL2, fg=P.TEXT, size=0.2, z=0.5, pad=0.22, kind="bold", align="c", alpha=1.0):
    """Label on a rounded-ish rectangular plate. Returns [plate, text]."""
    ts = max(size * TEXT_SCALE, MIN_TEXT)
    w = st.measure(text, size, kind) + pad * 2 + 0.06
    h = ts * 1.22 * (text.count("\n") + 1) + pad
    cx = x if align == "c" else (x + w / 2 if align == "l" else x - w / 2)
    return [st.rect(cx, y, w, h, bg, z, alpha=alpha, role="pill"), st.text(text, cx, y, size, fg, z + 0.01, kind=kind)]


def cross_arrow(st, x0, y0, x1, y1, color, label=None, size=0.2, z=0.4):
    parts = st.arrow(x0, y0, x1, y1, color, 0.05, 0.22, z)
    if label:
        parts.append(st.text(label, (x0 + x1) / 2, (y0 + y1) / 2 + 0.2, size, color, z))
    return parts


# ======================================================================================================
class Cutaway:
    """Vertical well cutaway: rock | annulus | pipe | annulus | rock, in a world-space rectangle.

    `eccentric` shifts the pipe sideways (positive = right) to make one gap wide and the other narrow."""

    def __init__(self, st, cx, y_top, y_bot, hole_w=2.4, pipe_w=0.9, wall=0.11, eccentric=0.0, z=0.0, rock=P.ROCK, rock_w=1.6):
        self.st, self.cx, self.y_top, self.y_bot, self.z = st, cx, y_top, y_bot, z
        self.hole = (cx - hole_w / 2, cx + hole_w / 2)
        pc = cx + eccentric
        self.pipe = (pc - pipe_w / 2, pc + pipe_w / 2)
        self.wall = wall
        self.bore = (self.pipe[0] + wall, self.pipe[1] - wall)
        self.gap_l = (self.hole[0], self.pipe[0])
        self.gap_r = (self.pipe[1], self.hole[1])
        self.rock_w, self.rock_color = rock_w, rock

    def draw(self, pipe_color=P.STEEL, hole_bg=P.BG, pipe_bottom=None):
        st, z = self.st, self.z
        h = self.y_top - self.y_bot
        cy = (self.y_top + self.y_bot) / 2
        out = [st.rect(self.hole[0] - self.rock_w / 2, cy, self.rock_w, h, self.rock_color, z),
               st.rect(self.hole[1] + self.rock_w / 2, cy, self.rock_w, h, self.rock_color, z),
               st.rect(self.cx, cy, self.hole[1] - self.hole[0], h, hole_bg, z + 0.01)]
        pb = self.y_bot if pipe_bottom is None else pipe_bottom
        ph = self.y_top - pb
        out += [st.rect(self.pipe[0] + self.wall / 2, (self.y_top + pb) / 2, self.wall, ph, pipe_color, z + 0.2),
                st.rect(self.pipe[1] - self.wall / 2, (self.y_top + pb) / 2, self.wall, ph, pipe_color, z + 0.2)]
        return out

    def _fill(self, x0, x1, color, ya, yb, t0, t1, z, alpha=1.0, interp="BEZIER"):
        st = self.st
        o = st.rect((x0 + x1) / 2, ya, x1 - x0, 0.0001, color, z, anchor="b" if yb > ya else "t", alpha=alpha)
        st.scale_to(o, t0, t1, sy=abs(yb - ya), interp=interp)
        return o

    def fill_gap(self, side, color, ya, yb, t0, t1, z=0.1, alpha=1.0, interp="BEZIER"):
        g = self.gap_l if side == "l" else self.gap_r
        return self._fill(g[0], g[1], color, ya, yb, t0, t1, self.z + z, alpha, interp)

    def fill_bore(self, color, ya, yb, t0, t1, z=0.1, alpha=1.0, interp="BEZIER"):
        return self._fill(self.bore[0], self.bore[1], color, ya, yb, t0, t1, self.z + z, alpha, interp)

    def static_gap(self, side, color, ya, yb, z=0.1, alpha=1.0):
        g = self.gap_l if side == "l" else self.gap_r
        return self.st.rect((g[0] + g[1]) / 2, (ya + yb) / 2, g[1] - g[0], abs(yb - ya), color, self.z + z, alpha=alpha)

    def static_bore(self, color, ya, yb, z=0.1, alpha=1.0):
        return self.st.rect((self.bore[0] + self.bore[1]) / 2, (ya + yb) / 2, self.bore[1] - self.bore[0], abs(yb - ya), color, self.z + z, alpha=alpha)


def loop_move(st, objs, t0, t1, dy, cycles=3, dx=0.0):
    """Repeating drift for flow arrows: move by (dx, dy) over one cycle, snap back, repeat `cycles` times in [t0, t1]."""
    from .stage import as_list
    objs = as_list(objs)
    d = (t1 - t0) / cycles
    for o in objs:
        x, y, z = st.state[o]["loc"]
        for i in range(cycles):
            a = t0 + i * d
            st.move(o, a, a + d * 0.92, to=(x + dx, y + dy), interp="LINEAR")
            st.move(o, a + d * 0.92, a + d, to=(x, y), interp="CONSTANT")
