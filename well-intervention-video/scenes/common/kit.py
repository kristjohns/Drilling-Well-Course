"""Drawing kit for the intervention film: labels, callouts, the compressed-depth well schematic, tables, gauges.

Everything returns lists of Stage objects (or a small namespace of named lists) so a chapter can fade, move and scale them with
the normal Stage calls. World units: canvas x -8..8, y -4.5..4.5. Keep content below y 3.9 and above y -3.7.
"""
from __future__ import annotations
import math

from . import palette as P
from . import model as M
from .shapes import pill
from .stage import as_list
from .look import wrap_to


class NS(dict):
    """dict with attribute access: parts.tubing, parts['tubing']."""
    __getattr__ = dict.__getitem__

    def all(self):
        out = []
        for v in self.values():
            out += as_list(v)
        return out


# ====================================================================================================== labels
def tag(st, x, y, text, color=P.PANEL2, fg=P.TEXT, size=0.2, z=1.0, align="c", alpha=1.0):
    """Label plate (pill). Returns [plate, text]."""
    return pill(st, x, y, text, bg=color, fg=fg, size=size, z=z, align=align, alpha=alpha)


def callout(st, text, x, y, tx, ty, color=P.PANEL2, fg=P.TEXT, size=0.2, z=1.0, align="l", dot=True, line=P.MUTED):
    """Pill at (x, y) with a thin leader to the target point (tx, ty). Returns all objects."""
    parts = pill(st, x, y, text, bg=color, fg=fg, size=size, z=z, align=align)
    w = st.measure(text, size, "bold") + 0.5
    if align == "l":
        ax = x + (0.0 if tx > x + w else -0.0)
        edge = x if tx < x else x + w
    elif align == "r":
        edge = x if tx > x else x - w
    else:
        edge = x - w / 2 if tx < x else x + w / 2
    parts.append(st.line([(edge, y), (tx, ty)], line, 0.022, z - 0.02, role="hair"))
    if dot:
        parts.append(st.circle(tx, ty, 0.05, P.TEXT, z + 0.01, role="disc"))
    return parts


def note(st, text, x, y, size=0.2, color=P.MUTED, align="l", z=1.0, wrap=None, kind="sans", valign="c"):
    return [st.text(text, x, y, size, color, z, align=align, kind=kind, wrap=wrap, valign=valign)]


def title(st, text, x, y, size=0.34, color=P.TEXT, align="l", z=1.0):
    return [st.text(text, x, y, size, color, z, align=align, kind="bold")]


def card(st, x, y, w, h, color=P.PANEL, z=0.3):
    return [st.rect(x, y, w, h, color, z, role="card")]


def ticker(st, parts, t, dt=0.18, d=0.35):
    """Fade a list of groups in one after the other starting at t."""
    for i, g in enumerate(parts):
        st.fade_in(g, t + i * dt, d)


def show(st, objs, t0, t1=None, d=0.35):
    """Fade in at t0, and (optionally) out at t1."""
    st.fade_in(objs, t0, d)
    if t1 is not None:
        st.fade_out(objs, t1, d)


def wiggle_arrow(st, x0, y0, x1, y1, color, t0, t1, z=0.8, width=0.06, head=0.24):
    """An arrow that fades in, and is gone at t1."""
    a = st.arrow(x0, y0, x1, y1, color, width, head, z)
    show(st, a, t0, t1)
    return a


def gauge_bar(st, x, y, w, h, t0, t1, v0, v1, vmax, color=P.PORE, label=None, fmt="{:.0f} bar", z=0.6, size=0.22):
    """Horizontal bar gauge that fills from v0 to v1 between t0 and t1, with a number counter. Returns objects."""
    back = st.rect(x + w / 2, y, w, h, P.PANEL, z - 0.02, role="card")
    f0, f1 = max(v0 / vmax, 0.001), max(v1 / vmax, 0.001)
    fill = st.rect(x + 0.04, y, w * f0 - 0.08, h - 0.1, color, z, anchor="l", role="flat")
    st.scale_to(fill, t0, t1, sx=max(w * f1 - 0.08, 0.001))
    st.counter(x + w / 2, y + h / 2 + 0.2, t0, t1, v0, v1, fmt, size, P.TEXT, z + 0.1)
    out = [back, fill]
    if label:
        out.append(st.text(label, x + w / 2, y - h / 2 - 0.2, 0.18, P.MUTED, z))
    return out


def dial(st, x, y, r, t0, t1, a0, a1, color=P.PORE, label=None, z=0.6):
    """Round gauge: face, ticks, a needle that swings from angle a0 to a1 (degrees, 0 = right, 90 = up, 180 = left)."""
    face = st.circle(x, y, r, P.PANEL2, z, role="disc")
    rim = st.ring(x, y, r, 0.04, P.MUTED, z + 0.01)
    ticks = []
    for k in range(9):
        a = math.radians(210 - k * 30)
        ticks.append(st.line([(x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78), (x + math.cos(a) * r * 0.92, y + math.sin(a) * r * 0.92)],
                             P.MUTED, 0.02, z + 0.02, role="hair"))
    needle = st.rect(x, y, r * 0.8, 0.045, color, z + 0.05, anchor="l", rot=a0, role="shaft")
    st.rotate(needle, t0, t1, a1)
    hub = st.circle(x, y, 0.07, P.TEXT, z + 0.06, role="disc")
    out = [face, rim, needle, hub] + ticks
    if label:
        out.append(st.text(label, x, y - r - 0.22, 0.18, P.MUTED, z))
    return out


# ====================================================================================================== tables
def matrix(st, x0, y0, col_w, row_h, rows, cols, z=0.5, head_size=0.17, row_size=0.2, row_label_w=2.4, head_h=0.7):
    """A grid of cells. Returns NS(cells={(r, c): [objs]}, rowlabels=[...], heads=[...], frame=[...]). Cell content is drawn
    later with `mark()` so a chapter can light cells up in sync with the voice. (x0, y0) = top-left of the first cell."""
    cells, heads, rls, frame = {}, [], [], []
    for c, name in enumerate(cols):
        cx = x0 + row_label_w + c * col_w + col_w / 2
        heads.append(st.text(name, cx, y0 + head_h / 2, head_size, P.MUTED, z, kind="bold", wrap=12, valign="c"))
    for r, name in enumerate(rows):
        cy = y0 - r * row_h - row_h / 2
        rls.append(st.text(name, x0 + row_label_w - 0.15, cy, row_size, P.TEXT, z, align="r", kind="bold"))
        frame.append(st.rect(x0 + row_label_w + len(cols) * col_w / 2, cy - row_h / 2, len(cols) * col_w, 0.012, P.GRID, z - 0.1))
        for c in range(len(cols)):
            cells[(r, c)] = (x0 + row_label_w + c * col_w + col_w / 2, cy)
    frame.append(st.rect(x0 + row_label_w + len(cols) * col_w / 2, y0, len(cols) * col_w, 0.012, P.GRID, z - 0.1))
    frame.append(st.rect(x0 + row_label_w + len(cols) * col_w / 2, y0 - len(rows) * row_h, len(cols) * col_w, 0.012, P.GRID, z - 0.1))
    return NS(cells=cells, heads=heads, rowlabels=rls, frame=frame)


def mark(st, pos, kind, t, size=0.17, z=0.8):
    """A tick (full), half-disc (partial) or cross (none) at pos, drawn on stroke by stroke starting at t."""
    x, y = pos
    if kind == "full":
        ln = st.line([(x - size * 0.7, y - 0.0), (x - size * 0.15, y - size * 0.55), (x + size * 0.8, y + size * 0.6)], P.SAFE, 0.07, z)
        st.draw_on(ln, t, t + 0.35, "BEZIER")
        return [ln]
    if kind == "part":
        d = st.circle(x, y, size * 0.6, P.WARN, z, role="disc")
        st.pop_in(d, t, 0.3)
        return [d]
    a = st.line([(x - size * 0.5, y + size * 0.5), (x + size * 0.5, y - size * 0.5)], P.BAD, 0.06, z)
    b = st.line([(x - size * 0.5, y - size * 0.5), (x + size * 0.5, y + size * 0.5)], P.BAD, 0.06, z)
    st.draw_on(a, t, t + 0.25, "BEZIER")
    st.draw_on(b, t + 0.15, t + 0.4, "BEZIER")
    return [a, b]


# ====================================================================================================== tube and wire helpers
def pipe_v(st, cx, y_top, y_bot, od, wall, color=P.STEEL, z=0.2, bore=None, bore_alpha=1.0):
    """Vertical pipe cutaway: two walls (+ optional bore fill). Returns NS(walls=[l, r], bore=[...])."""
    h = y_top - y_bot
    cy = (y_top + y_bot) / 2
    walls = [st.rect(cx - od / 2 + wall / 2, cy, wall, h, color, z), st.rect(cx + od / 2 - wall / 2, cy, wall, h, color, z)]
    b = []
    if bore:
        b = [st.rect(cx, cy, od - 2 * wall, h, bore, z - 0.02, alpha=bore_alpha)]
    return NS(walls=walls, bore=b)


def pipe_h(st, cy, x0, x1, od, wall, color=P.STEEL, z=0.2, bore=None, bore_alpha=1.0):
    w = x1 - x0
    cx = (x0 + x1) / 2
    walls = [st.rect(cx, cy + od / 2 - wall / 2, w, wall, color, z), st.rect(cx, cy - od / 2 + wall / 2, w, wall, color, z)]
    b = []
    if bore:
        b = [st.rect(cx, cy, w, od - 2 * wall, bore, z - 0.02, alpha=bore_alpha)]
    return NS(walls=walls, bore=b)


def wire_down(st, x, y_top, y_bot, t0=None, t1=None, y_bot0=None, width=0.03, color=P.WIRE, z=0.9):
    """A vertical line hanging from y_top; its lower end moves from y_bot0 to y_bot between t0 and t1 (matches st.move of the tool)."""
    y0 = y_bot0 if y_bot0 is not None else y_bot
    o = st.rect(x, y_top, width, max(y_top - y0, 0.001), color, z, anchor="t", role="steel")
    if t0 is not None:
        st.scale_to(o, t0, t1, sy=max(y_top - y_bot, 0.001))
    return o


def move_group(st, objs, t0, t1, dx=0.0, dy=0.0, interp="BEZIER"):
    st.move(objs, t0, t1, dx=dx, dy=dy, interp=interp)


# ====================================================================================================== the compressed-depth well
# (md, y offset below the seabed, world units): piecewise-linear depth map, with more room around the completion fittings
DEPTH_MAP = [(0.0, 0.0), (450.0, 0.85), (1200.0, 2.0), (2100.0, 3.1), (3000.0, 4.1), (3550.0, 4.75), (3650.0, 5.05),
             (3720.0, 5.3), (3800.0, 5.55), (3900.0, 5.9), (4100.0, 6.4), (4200.0, 6.65)]


class Well:
    """The composite well as a vertical cutaway. `y(md)` maps measured depth to world y (compressed). Parts are created on demand
    so a chapter can reveal them one by one.

        w = Well(st, cx=-3.2, y_top=2.7)           # y_top = seabed level
        w.rock(); w.casing(); w.tubing(); w.packer(); ...
    """
    CAS_OD, CAS_WALL = 1.08, 0.06
    HOLE_W = 1.34
    TUB_OD, TUB_WALL = 0.46, 0.05

    def __init__(self, st, cx=-3.2, y_top=2.7, scale=1.0, rock_w=2.4, depth_map=None):
        self.st, self.cx, self.y_top, self.k = st, cx, y_top, scale
        self.rock_w = rock_w
        self.map = depth_map or DEPTH_MAP
        self.parts = NS()
        self.grow = None      # (t0, t1): columns created while set grow downward from their top edge over that time

    # ------------------------------------------------------------------ geometry
    def y(self, md):
        pts = self.map
        if md <= pts[0][0]:
            return self.y_top - pts[0][1] * self.k
        for (m0, o0), (m1, o1) in zip(pts[:-1], pts[1:]):
            if md <= m1:
                f = (md - m0) / (m1 - m0)
                return self.y_top - (o0 + (o1 - o0) * f) * self.k
        return self.y_top - pts[-1][1] * self.k

    @property
    def y_bot(self):
        return self.y(M.TD_MD)

    @property
    def tub_x(self):
        return self.cx

    def _col(self, x_off, y0, y1, w, color, z, **kw):
        if self.grow and "alpha" not in kw:
            g0, g1 = self.grow
            o = self.st.rect(self.cx + x_off, max(y0, y1), w, 0.0001, color, z, anchor="t", **kw)
            self.st.scale_to(o, g0, g1, sy=abs(y0 - y1))
            return o
        return self.st.rect(self.cx + x_off, (y0 + y1) / 2, w, abs(y0 - y1), color, z, **kw)

    # ------------------------------------------------------------------ rock, cement, casing
    def rock(self, z=0.0):
        st, cx = self.st, self.cx
        yb = self.y_bot - 0.25
        h = self.y_top - yb
        half = self.HOLE_W / 2
        L = st.rect(cx - half - self.rock_w / 2, (self.y_top + yb) / 2, self.rock_w, h, P.ROCK, z)
        R = st.rect(cx + half + self.rock_w / 2, (self.y_top + yb) / 2, self.rock_w, h, P.ROCK, z)
        self.parts["rock"] = [L, R]
        return [L, R]

    def reservoir(self, md0=3820.0, md1=4200.0, z=0.02):
        """Sand band across the rock at the producing interval."""
        y0, y1 = self.y(md0) , self.y(md1) - 0.25
        half = self.HOLE_W / 2
        out = [self.st.rect(self.cx - half - self.rock_w / 2, (y0 + y1) / 2, self.rock_w, y0 - y1, P.SAND, z),
               self.st.rect(self.cx + half + self.rock_w / 2, (y0 + y1) / 2, self.rock_w, y0 - y1, P.SAND, z)]
        self.parts["reservoir"] = out
        return out

    def cement(self, md0=0.0, md1=4200.0, z=0.05):
        a = self.HOLE_W / 2 - (self.HOLE_W - self.CAS_OD) / 4
        w = (self.HOLE_W - self.CAS_OD) / 2
        y0, y1 = self.y(md0), self.y(md1)
        out = [self._col(-a, y0, y1, w, P.CEMENT, z), self._col(a, y0, y1, w, P.CEMENT, z)]
        self.parts["cement"] = out
        return out

    def casing(self, md0=0.0, md1=4200.0, z=0.1):
        a = self.CAS_OD / 2 - self.CAS_WALL / 2
        y0, y1 = self.y(md0), self.y(md1)
        out = [self._col(-a, y0, y1, self.CAS_WALL, P.STEEL_DK, z), self._col(a, y0, y1, self.CAS_WALL, P.STEEL_DK, z)]
        # the open bore of the casing (annulus space): dark
        inner = self._col(0, y0, y1, self.CAS_OD - 2 * self.CAS_WALL, P.BG, z - 0.04)
        out.append(inner)
        self.parts["casing"] = out
        return out

    def tubing(self, md0=0.0, md1=3800.0, z=0.2, bore=P.OIL, bore_alpha=0.0):
        a = self.TUB_OD / 2 - self.TUB_WALL / 2
        y0, y1 = self.y(md0), self.y(md1)
        out = [self._col(-a, y0, y1, self.TUB_WALL, P.STEEL, z), self._col(a, y0, y1, self.TUB_WALL, P.STEEL, z)]
        self.parts["tubing"] = out
        bore_o = self._col(0, y0, y1, self.TUB_OD - 2 * self.TUB_WALL, bore, z - 0.02, alpha=max(bore_alpha, 0.001))
        self.parts["bore"] = [bore_o]
        return out

    def fill(self, region, color, md0, md1, z=0.15, alpha=1.0):
        """Fill the 'annulus' (both sides, between tubing and casing) or the 'bore' with a colour."""
        if region == "bore":
            return [self._col(0, self.y(md0), self.y(md1), self.TUB_OD - 2 * self.TUB_WALL, color, z, alpha=alpha)]
        a = (self.CAS_OD / 2 - self.CAS_WALL + self.TUB_OD / 2) / 2
        w = (self.CAS_OD / 2 - self.CAS_WALL) - self.TUB_OD / 2
        return [self._col(-a, self.y(md0), self.y(md1), w, color, z, alpha=alpha), self._col(a, self.y(md0), self.y(md1), w, color, z, alpha=alpha)]

    # ------------------------------------------------------------------ completion fittings
    def packer(self, md=M.PACKER_MD, z=0.3):
        st, y = self.st, self.y(md)
        h = 0.34
        ann_in = self.TUB_OD / 2
        ann_out = self.CAS_OD / 2 - self.CAS_WALL
        w = ann_out - ann_in
        out = []
        for sd in (-1, 1):
            xc = sd * (ann_in + ann_out) / 2
            out.append(self._col(xc, y + h / 2, y - h / 2, w, "#5a6b8c", z, role="solid"))
            out.append(self._col(xc, y + h / 2 + 0.07, y + h / 2, w, P.STEEL, z + 0.01))
            out.append(self._col(xc, y - h / 2, y - h / 2 - 0.07, w, P.STEEL, z + 0.01))
        self.parts["packer"] = out
        return out

    def dhsv(self, md=M.DHSV_MD, z=0.3, open_=True):
        """Downhole safety valve: a thicker body with a flapper line. Returns NS(body, flapper)."""
        st, y = self.st, self.y(md)
        body = [self._col(0, y + 0.22, y - 0.22, self.TUB_OD + 0.16, P.STEEL_DK, z)]
        bore = self._col(0, y + 0.22, y - 0.22, self.TUB_OD - 2 * self.TUB_WALL, P.BG, z + 0.01)
        fl = st.rect(self.cx - 0.1, y, 0.22, 0.045, P.WARN, z + 0.03, anchor="l", rot=(80 if open_ else 0), role="shaft")
        ctl = st.line([(self.cx + 0.3, y + 0.0), (self.cx + 0.42, y), (self.cx + 0.42, self.y_top - 0.2)], P.PORE, 0.02, z - 0.04, role="hair")
        self.parts["dhsv"] = NS(body=body + [bore], flapper=[fl], ctrl=[ctl])
        return self.parts["dhsv"]

    def mandrel(self, md, z=0.3, valve=True):
        """Side-pocket mandrel: a bulge on the tubing's right side with a pocket (and a small valve). Returns NS(body, valve)."""
        st, y = self.st, self.y(md)
        body = [self._col(0.17, y + 0.3, y - 0.3, 0.5, P.STEEL_DK, z)]
        pocket = [self._col(0.30, y + 0.2, y - 0.2, 0.16, P.BG, z + 0.01)]
        vlv = [self._col(0.30, y + 0.12, y - 0.12, 0.1, P.GAS, z + 0.02, role="flat")] if valve else []
        # tubing bore is still clear; make the main bore visible through the body
        bore = [self._col(-0.02, y + 0.3, y - 0.3, self.TUB_OD - 2 * self.TUB_WALL - 0.04, P.BG, z + 0.005)]
        out = NS(body=body + bore + pocket, valve=vlv)
        self.parts.setdefault("mandrels", []).append(out)
        return out

    def sleeve(self, md=M.SLEEVE_MD, z=0.3, open_=False):
        st, y = self.st, self.y(md)
        body = [self._col(0, y + 0.24, y - 0.24, self.TUB_OD + 0.14, P.STEEL_DK, z)]
        bore = [self._col(0, y + 0.24, y - 0.24, self.TUB_OD - 2 * self.TUB_WALL, P.BG, z + 0.01)]
        port_l = self._col(-(self.TUB_OD / 2 + 0.02), y + 0.07, y - 0.07, 0.09, P.BG, z + 0.02)
        port_r = self._col((self.TUB_OD / 2 + 0.02), y + 0.07, y - 0.07, 0.09, P.BG, z + 0.02)
        inner = self._col(0, y + 0.12, y - 0.12, self.TUB_OD - 2 * self.TUB_WALL + 0.0, P.PRIMARY_B, z + 0.015, role="flat")
        self.parts["sleeve"] = NS(body=body + bore, ports=[port_l, port_r], inner=[inner])
        return self.parts["sleeve"]

    def nipple(self, md=M.NIPPLE_MD, z=0.3):
        st, y = self.st, self.y(md)
        body = [self._col(0, y + 0.13, y - 0.13, self.TUB_OD + 0.1, P.STEEL_DK, z)]
        bore = [self._col(0, y + 0.13, y - 0.13, self.TUB_OD - 2 * self.TUB_WALL - 0.02, P.BG, z + 0.01)]
        groove = [self._col(0, y + 0.03, y - 0.03, self.TUB_OD - 2 * self.TUB_WALL + 0.07, P.BG, z + 0.012)]
        self.parts["nipple"] = body + bore + groove
        return self.parts["nipple"]

    def perfs(self, md0=M.PERFS_MD[0], md1=M.PERFS_MD[1], n=6, z=0.2, color=P.OIL):
        """Perforation tunnels through casing and cement into the sand. Returns NS(tunnels, glow)."""
        st = self.st
        out = []
        for i in range(n):
            md = md0 + (md1 - md0) * (i + 0.5) / n
            y = self.y(md)
            for sd in (-1, 1):
                x0 = sd * (self.CAS_OD / 2 - 0.02)
                L = 0.62
                out.append(st.rect(self.cx + x0 + sd * L / 2, y, L, 0.06, P.BG, z, role="hole"))
        self.parts["perfs"] = out
        return out

    # ------------------------------------------------------------------ tree
    def tree(self, z=0.35, label=False):
        """A simple subsea-tree block on the seabed at the top of the well. Returns objects."""
        st, cx, y = self.st, self.cx, self.y_top
        out = [st.rect(cx, y + 0.18, 1.2, 0.36, P.STEEL_DK, z),
               st.rect(cx, y + 0.5, 0.62, 0.34, P.STEEL, z),
               st.rect(cx, y + 0.8, 0.5, 0.28, P.STEEL_DK, z),
               st.rect(cx, y + 1.0, 0.7, 0.1, P.STEEL, z),
               st.rect(cx + 0.62, y + 0.55, 0.65, 0.16, P.STEEL, z - 0.01)]
        for dy in (0.5, 0.8):
            out.append(st.circle(cx - 0.0, y + dy, 0.07, P.BG, z + 0.02, role="hole"))
        self.parts["tree"] = out
        return out

    def seabed(self, z=0.04, width=6.4):
        st = self.st
        sb = st.rect(self.cx, self.y_top - 0.02, width, 0.05, P.SEABED, z + 0.2)
        self.parts["seabed"] = [sb]
        return [sb]

    def depth_ticks(self, mds=(0, 1000, 2000, 3000, 4000), x=None, z=0.9):
        """Measured-depth ruler beside the well."""
        st = self.st
        x = self.cx - self.HOLE_W / 2 - self.rock_w - 0.15 if x is None else x
        out = []
        for md in mds:
            y = self.y(md)
            out.append(st.text(f"{md:,} m", x, y, 0.17, P.MUTED, z, align="r"))
            out.append(st.rect(x + 0.08, y, 0.12, 0.012, P.GRID, z))
        return out


# ====================================================================================================== vessel and sea
def sea_block(st, x0, x1, y_top, y_bot, z=0.0):
    return [st.rect((x0 + x1) / 2, (y_top + y_bot) / 2, x1 - x0, y_top - y_bot, P.SEA, z, alpha=0.6)]


def vessel(st, cx, y_water, scale=1.0, z=0.6, moonpool=True):
    """A side-on service vessel: hull, deckhouse, crane, derrick over a moonpool. y_water = waterline. Returns NS."""
    s = scale
    hull = st.poly([(cx - 2.2 * s, y_water + 0.5 * s), (cx + 2.4 * s, y_water + 0.5 * s), (cx + 2.0 * s, y_water - 0.35 * s),
                    (cx - 1.9 * s, y_water - 0.35 * s)], "#2b3b57", z, role="solid")
    deck = st.rect(cx - 0.4 * s, y_water + 0.56 * s, 4.4 * s, 0.1 * s, P.STEEL_DK, z + 0.01)
    house = st.rect(cx + 1.7 * s, y_water + 1.05 * s, 0.9 * s, 0.9 * s, "#d8dee9", z + 0.01, role="solid")
    win = st.rect(cx + 1.7 * s, y_water + 1.25 * s, 0.7 * s, 0.18 * s, "#294a7a", z + 0.02, role="solid")
    mp = []
    if moonpool:
        mp = [st.rect(cx - 0.4 * s, y_water + 0.15 * s, 0.7 * s, 0.9 * s, P.SEA, z + 0.02, alpha=0.9)]
    derrick = [st.line([(cx - 0.75 * s, y_water + 0.6 * s), (cx - 0.55 * s, y_water + 2.0 * s), (cx - 0.25 * s, y_water + 2.0 * s),
                        (cx - 0.05 * s, y_water + 0.6 * s)], P.STEEL, 0.04, z + 0.02, role="hair")]
    crane = [st.line([(cx - 1.4 * s, y_water + 0.6 * s), (cx - 1.4 * s, y_water + 1.4 * s), (cx - 2.0 * s, y_water + 1.9 * s)], P.STEEL, 0.05, z + 0.02, role="hair")]
    return NS(hull=[hull, deck, house, win], moonpool=mp, derrick=derrick, crane=crane)


# ====================================================================================================== small icons
def drum(st, x, y, r, z=0.5, turns=5, color=P.WIRE):
    """A wireline drum / reel seen side-on: flanges, core and wound turns. Returns NS(body, turns)."""
    flange = [st.circle(x, y, r, "#34425f", z, role="solid")]
    wound = []
    for i in range(turns):
        wound.append(st.ring(x, y, r * (0.95 - i * 0.12), 0.025, color, z + 0.01 + i * 0.001))
    hub = st.circle(x, y, r * 0.22, P.STEEL_DK, z + 0.1, role="solid")
    spokes = [st.rect(x, y, r * 1.6, 0.04, P.STEEL_DK, z + 0.02, rot=a, role="solid") for a in (0, 60, 120)]
    return NS(body=flange + [hub] + spokes, turns=wound)


def spin(st, objs, t0, t1, deg, around):
    """Rotate objects about a pivot (x, y) by `deg` between t0 and t1 by moving their positions along an arc and spinning them."""
    ax, ay = around
    n = max(int((t1 - t0) * 24), 2)
    for o in as_list(objs):
        x, y, _ = st.state[o]["loc"]
        r0 = math.atan2(y - ay, x - ax)
        rad = math.hypot(x - ax, y - ay)
        a0 = math.degrees(st.state[o]["rot"]) if False else st.state[o]["rot"]
        for i in range(1, n + 1):
            f = i / n
            ang = r0 + math.radians(deg) * f
            st.move(o, t0 + (t1 - t0) * (i - 1) / n, t0 + (t1 - t0) * i / n, to=(ax + rad * math.cos(ang), ay + rad * math.sin(ang)),
                    interp="LINEAR")
            st.rotate(o, t0 + (t1 - t0) * (i - 1) / n, t0 + (t1 - t0) * i / n, a0 + deg * f, interp="LINEAR")


def gate_valve(st, x, y, s=1.0, z=0.4, open_=True, horizontal=False):
    """Gate valve cutaway. Vertical flow path: body 0.62 s wide, 0.5 s tall, the gate slides sideways across the bore.
    Horizontal flow path: the gate slides up and down. Returns NS(body, gate, stem, pos_open, pos_closed) - move the gate between
    the two positions to open and close the valve."""
    if not horizontal:
        body = [st.rect(x, y, 0.62 * s, 0.5 * s, P.STEEL_DK, z), st.rect(x, y, 0.2 * s, 0.5 * s, P.BG, z + 0.01),
                st.rect(x + 0.4 * s, y, 0.18 * s, 0.3 * s, P.STEEL_DK, z)]                  # bonnet on the right
        po, pc = (x + 0.3 * s, y), (x, y)
        gate = [st.rect(*(po if open_ else pc), 0.3 * s, 0.1 * s, P.WARN, z + 0.03, role="solid")]
        stem = [st.rect(x + 0.56 * s, y, 0.3 * s, 0.05 * s, P.STEEL, z), st.rect(x + 0.72 * s, y, 0.06 * s, 0.34 * s, P.STEEL, z + 0.01)]
    else:
        body = [st.rect(x, y, 0.5 * s, 0.62 * s, P.STEEL_DK, z), st.rect(x, y, 0.5 * s, 0.2 * s, P.BG, z + 0.01),
                st.rect(x, y + 0.4 * s, 0.3 * s, 0.18 * s, P.STEEL_DK, z)]
        po, pc = (x, y + 0.3 * s), (x, y)
        gate = [st.rect(*(po if open_ else pc), 0.1 * s, 0.3 * s, P.WARN, z + 0.03, role="solid")]
        stem = [st.rect(x, y + 0.56 * s, 0.05 * s, 0.3 * s, P.STEEL, z), st.rect(x, y + 0.72 * s, 0.34 * s, 0.06 * s, P.STEEL, z + 0.01)]
    return NS(body=body, gate=gate, stem=stem, pos_open=po, pos_closed=pc)


def valve_to(st, v, t0, t1, open_):
    """Slide a gate_valve's gate to its open or closed position."""
    st.move(v.gate, t0, t1, to=v.pos_open if open_ else v.pos_closed)


def dry_tree(st, cx, y0, s=1.0, z=0.4, open_=True):
    """Dry (platform) Christmas tree on a wellhead. y0 = top of the wellhead spool. From the bottom: lower master, upper master, a
    flow cross with the wing valve to the right, the swab valve, and a cap. Returns NS(parts, lmv, umv, wing, swab, cap, top, bore)."""
    spool = [st.rect(cx, y0 - 0.15 * s, 0.95 * s, 0.3 * s, P.STEEL_DK, z), st.rect(cx, y0 - 0.15 * s, 0.2 * s, 0.3 * s, P.BG, z + 0.01)]
    lmv = gate_valve(st, cx, y0 + 0.25 * s, s, z, open_)
    umv = gate_valve(st, cx, y0 + 0.8 * s, s, z, open_)
    yx = y0 + 1.3 * s
    cross = [st.rect(cx, yx, 0.62 * s, 0.4 * s, P.STEEL_DK, z), st.rect(cx, yx, 0.2 * s, 0.4 * s, P.BG, z + 0.01),
             st.rect(cx + 0.65 * s, yx, 0.7 * s, 0.26 * s, P.STEEL_DK, z), st.rect(cx + 0.65 * s, yx, 0.7 * s, 0.1 * s, P.BG, z + 0.01)]
    wing = gate_valve(st, cx + 0.88 * s, yx, s, z, open_, horizontal=True)
    swab = gate_valve(st, cx, y0 + 1.8 * s, s, z, open_)
    cap = [st.rect(cx, y0 + 2.12 * s, 0.5 * s, 0.14 * s, P.STEEL, z), st.rect(cx, y0 + 2.12 * s, 0.2 * s, 0.14 * s, P.BG, z + 0.01)]
    parts = spool + lmv.body + lmv.stem + umv.body + umv.stem + cross + wing.body + wing.stem + swab.body + swab.stem + cap
    gates = lmv.gate + umv.gate + wing.gate + swab.gate
    return NS(parts=parts, gates=gates, lmv=lmv, umv=umv, wing=wing, swab=swab, cap=cap, y_swab=y0 + 1.8 * s, y_umv=y0 + 0.8 * s, y_lmv=y0 + 0.25 * s,
              y_wing=yx, top=y0 + 2.2 * s, cx=cx, s=s, y0=y0)


def pce_stack(st, cx, y0, s=1.0, z=0.45, tube_h=1.5):
    """Wireline pressure control equipment on top of the tree (y0 = top of the tree cap): wireline BOP (two retractable rams),
    lubricator tube, and the stuffing box on top. Returns NS(parts, rams (left, right), tube_walls, bore (the inside), y_bop, y_tube0,
    y_tube1, y_box, top)."""
    bop_h = 0.55 * s
    y_bop = y0 + bop_h / 2
    bop = [st.rect(cx, y_bop, 0.62 * s, bop_h, P.STEEL_DK, z), st.rect(cx, y_bop, 0.2 * s, bop_h, P.BG, z + 0.01),
           st.rect(cx - 0.42 * s, y_bop, 0.24 * s, 0.3 * s, P.STEEL_DK, z), st.rect(cx + 0.42 * s, y_bop, 0.24 * s, 0.3 * s, P.STEEL_DK, z)]
    rl = st.rect(cx - 0.3 * s, y_bop, 0.2 * s, 0.14 * s, P.BAD, z + 0.03, role="solid")
    rr = st.rect(cx + 0.3 * s, y_bop, 0.2 * s, 0.14 * s, P.BAD, z + 0.03, role="solid")
    y_t0 = y0 + bop_h
    y_t1 = y_t0 + tube_h * s
    tube = [st.rect(cx - 0.15 * s, (y_t0 + y_t1) / 2, 0.08 * s, y_t1 - y_t0, P.STEEL, z, role="steel"),
            st.rect(cx + 0.15 * s, (y_t0 + y_t1) / 2, 0.08 * s, y_t1 - y_t0, P.STEEL, z, role="steel")]
    flange = [st.rect(cx, y_t0 + 0.04 * s, 0.5 * s, 0.08 * s, P.STEEL, z + 0.01), st.rect(cx, y_t1 - 0.04 * s, 0.5 * s, 0.08 * s, P.STEEL, z + 0.01)]
    bore = st.rect(cx, (y_t0 + y_t1) / 2, 0.22 * s, y_t1 - y_t0, P.BG, z - 0.02)
    box_h = 0.5 * s
    y_box = y_t1 + box_h / 2
    box = [st.rect(cx, y_box, 0.46 * s, box_h, P.STEEL_DK, z), st.rect(cx, y_box, 0.04 * s, box_h, P.BG, z + 0.01),
           st.rect(cx, y_t1 + box_h + 0.06 * s, 0.34 * s, 0.12 * s, P.STEEL, z)]
    parts = bop + tube + flange + [bore] + box
    return NS(parts=parts, rams=[rl, rr], tube=tube, bore=bore, y_bop=y_bop, y_t0=y_t0, y_t1=y_t1, y_box=y_box, top=y_t1 + box_h + 0.12 * s, cx=cx, s=s,
              ram_in=(cx - 0.1 * s, cx + 0.1 * s), ram_out=(cx - 0.3 * s, cx + 0.3 * s))


def toolstring_simple(st, cx, y_top, s=1.0, z=0.7, n=4):
    """A generic toolstring (rope socket, bars, jar, tool) drawn as stacked rounded bars. Returns NS(parts, h, bottom)."""
    segs = [(0.1, 0.2, P.STEEL_DK), (0.12, 0.55, P.STEEL), (0.14, 0.25, P.STEEL_DK), (0.12, 0.35, P.WARN)][:n]
    parts, y = [], y_top
    for w_, h_, c_ in segs:
        parts.append(st.rect(cx, y - h_ * s / 2, w_ * s, h_ * s, c_, z, role="steel" if c_ != P.WARN else "solid"))
        y -= h_ * s
    return NS(parts=parts, h=y_top - y, bottom=y)


def xmark(st, x, y, r, t, z=1.5, width=0.08):
    a = st.line([(x - r, y + r), (x + r, y - r)], P.BAD, width, z)
    b = st.line([(x - r, y - r), (x + r, y + r)], P.BAD, width, z)
    st.draw_on(a, t, t + 0.3, "BEZIER")
    st.draw_on(b, t + 0.2, t + 0.5, "BEZIER")
    return [a, b]


def check(st, x, y, t, s=0.17, z=1.2, color=P.SAFE):
    plate = st.circle(x, y, s * 1.45, P.PANEL2, z - 0.01, role="disc")
    ln = st.line([(x - s * 0.62, y), (x - s * 0.15, y - s * 0.48), (x + s * 0.7, y + s * 0.55)], color, 0.06, z)
    st.pop_in(plate, t - 0.05, 0.3)
    st.draw_on(ln, t + 0.05, t + 0.45, "BEZIER")
    return [plate, ln]


def orb_num(st, x, y, n, t, color=P.PORE, r=0.17, z=1.0, fg=P.BG):
    o = st.circle(x, y, r, color, z)
    tx = st.text(str(n), x, y - 0.005, 0.15, fg, z + 0.01, kind="bold")
    st.pop_in(o, t, 0.35)
    st.fade_in(tx, t + 0.1, 0.25)
    return [o, tx]


def S(b, i):
    """Start of sentence i of beat b (chapter-relative)."""
    return b.sent[i]


def steps_list(st, x, y_top, items, times, size=0.21, dy=0.55, z=0.9, color=P.PORE, t_out=None):
    """A numbered step list: each step (orb + text) fades in at its time. x = centre of the number orb; text follows to its right."""
    out = []
    for i, (txt, t) in enumerate(zip(items, times)):
        y = y_top - i * dy
        g = orb_num(st, x, y, i + 1, t, color=color, r=0.16, z=z)
        tx = st.text(txt, x + 0.3, y, size, P.TEXT, z, align="l")
        st.fade_in(tx, t + 0.1, 0.35)
        out += g + [tx]
    if t_out is not None:
        st.fade_out(out, t_out, 0.5)
    return out
