"""Reusable assemblies built from Stage primitives: pill labels, the mud-weight-window chart, nested casing column."""
from __future__ import annotations

from . import palette as P
from . import well_model as M
from .chart import Chart
from .stage import TEXT_SCALE, MIN_TEXT


def pill(st, x, y, text, bg=P.PANEL2, fg=P.TEXT, size=0.2, z=0.5, pad=0.22, kind="bold", align="c"):
    """Label on a rounded-ish rectangular plate. Returns [plate, text]."""
    ts = max(size * TEXT_SCALE, MIN_TEXT)
    w = ts * 0.58 * max(len(l) for l in text.split("\n")) + pad * 2
    h = ts * 1.25 * (text.count("\n") + 1) + pad
    cx = x if align == "c" else (x + w / 2 if align == "l" else x - w / 2)
    return [st.rect(cx, y, w, h, bg, z), st.text(text, cx, y, size, fg, z + 0.01, kind=kind)]


def cross_arrow(st, x0, y0, x1, y1, color, label=None, size=0.2, z=0.4):
    parts = st.arrow(x0, y0, x1, y1, color, 0.05, 0.22, z)
    if label:
        parts.append(st.text(label, (x0 + x1) / 2, (y0 + y1) / 2 + 0.2, size, color, z))
    return parts


class WindowChart:
    """The recurring protagonist: pore pressure and fracture limit vs depth, as equivalent mud weight (sg)."""

    def __init__(self, st, x=-5.3, y=-3.0, w=7.2, h=6.35, ymax=4200.0, xr=(0.9, 2.0)):
        self.st = st
        self.c = Chart(st, x, y, w, h, xr, (0.0, ymax), invert_y=True)
        self.objs: dict = {}

    def axes(self, collapse_label=False):
        c = self.c
        fr = c.frame(xticks=[1.0, 1.2, 1.4, 1.6, 1.8, 2.0], yticks=[0, 1000, 2000, 3000, 4000],
                     xlabel="equivalent mud weight (sg)", ylabel="depth below sea level (m)", fx="{:.1f}")
        st = self.st
        sb = st.rect(c.X(c.xr[0]) + c.w / 2, c.Y(M.WATER_DEPTH), c.w, 0.035, P.SEABED, 0.12)
        sbl = st.text("seabed, 300 m", c.X(c.xr[0]) + 0.1, c.Y(M.WATER_DEPTH) - 0.2, 0.18, P.TEXT, 0.12, align="l")
        sea = st.rect(c.x + c.w / 2, (c.Y(0) + c.Y(M.WATER_DEPTH)) / 2, c.w, c.Y(0) - c.Y(M.WATER_DEPTH), P.SEA, 0.01, alpha=0.5)
        self.objs["axes"] = fr + [sb, sbl, sea]
        return self.objs["axes"]

    def _depths(self, z0=M.WATER_DEPTH, z1=M.TD, step=50.0):
        z, out = z0, []
        while z < z1 + 1e-6:
            out.append(z)
            z += step
        if out[-1] < z1:
            out.append(z1)
        return out

    def curves(self, collapse=False):
        c, st = self.c, self.st
        zs = self._depths()
        self.objs["pp"] = c.curve([M.pp(z) for z in zs], zs, P.PORE, 0.07, 0.3)
        self.objs["fg"] = c.curve([M.fg(z) for z in zs], zs, P.FRAC, 0.07, 0.3)
        self.objs["pp_lbl"] = st.text("pore pressure", c.X(1.06) - 0.45, c.Y(1500), 0.22, P.PORE, 0.3, align="r")
        self.objs["fg_lbl"] = st.text("fracture", c.X(1.84) + 0.1, c.Y(1500), 0.22, P.FRAC, 0.3, align="l")
        if collapse:
            self.objs["co"] = c.curve([M.collapse(z) for z in zs], zs, P.COLLAPSE, 0.05, 0.3)
            self.objs["co_lbl"] = st.text("collapse", c.X(1.05), c.Y(3500), 0.2, P.COLLAPSE, 0.3, align="r")
        return self.objs

    def band(self, alpha=0.38):
        zs = self._depths()
        left = [(M.pp(z), z) for z in zs]   # [SIM] lower limit drawn as pore pressure only
        right = [(M.fg(z), z) for z in zs]
        self.objs["band"] = self.c.band(left, right, P.SAFE, 0.1, alpha)
        return self.objs["band"]

    def margins(self):
        zs = self._depths()
        c, st = self.c, self.st
        a = [st.line([c.pt(M.pp(z) + M.TRIP_ECD_MARGIN, z) for z in zs], P.PORE, 0.025, 0.25, 0.6)]
        b = [st.line([c.pt(M.fg(z) - M.FRAC_MARGIN, z) for z in zs], P.FRAC, 0.025, 0.25, 0.6)]
        self.objs["margins"] = a + b
        return a + b

    def limit_curve(self, mw, z0=M.WATER_DEPTH, color=P.WARN, alpha=0.9):
        """'Fracture, less margins' for a section drilled with mud weight mw (the curve the bottom-up design compares to)."""
        c, st = self.c, self.st
        pts = []
        for z in self._depths(z0, M.TD, 25.0):
            v = M.fg(z) - (M.required_shoe_emw(z, mw) - mw)
            if v >= c.xr[0]:
                pts.append(c.pt(v, z))
        return st.line(pts, color, 0.035, 0.28, alpha)

    def mw_line(self, mw, z_from, z_to, color=P.MUD, width=0.08):
        """Vertical mud-weight line from depth z_from to z_to (z_to < z_from means upward). Anchored at z_from."""
        c, st = self.c, self.st
        ya, yb = c.Y(z_from), c.Y(z_to)
        o = st.rect(c.X(mw), ya, width, 0.0001, color, 0.35, anchor="b" if yb > ya else "t")
        return o, abs(yb - ya)

    def crack_wedge(self, mw, z_top, z_bot, alpha=0.45):
        """Red wedge between the 'fracture less margins' curve and the mud-weight line where the open hole would crack."""
        c = self.c
        left, right = [], []
        z = z_top
        while z <= z_bot + 1e-6:
            v = max(M.fg(z) - (M.required_shoe_emw(z, mw) - mw), c.xr[0])
            left.append((v, z))
            right.append((mw, z))
            z += 25.0
        return self.st.poly([c.pt(*p) for p in left] + [c.pt(*p) for p in reversed(right)], P.BAD, 0.2, alpha)


STRING_COLORS = {"30in conductor": "#56667d", "20in surface casing": "#71839c", "13-3/8in intermediate": "#98a9bf",
                 "9-5/8in intermediate": "#c9d4e1"}
STRING_W = {"30in conductor": 1.5, "20in surface casing": 1.2, "13-3/8in intermediate": 0.9, "9-5/8in intermediate": 0.6}
STRING_LABEL = {"30in conductor": '30"', "20in surface casing": '20"', "13-3/8in intermediate": '13⅜"', "9-5/8in intermediate": '9⅝"'}


class CasingColumn:
    """Nested telescoping casing strings drawn beside a chart, depth-aligned to chart.Y()."""

    def __init__(self, st, chart: Chart, cx=4.6):
        self.st, self.c, self.cx = st, chart, cx
        self.bars: dict = {}
        self.labels: dict = {}

    def backdrop(self):
        c, st = self.c, self.st
        zt, zb = c.Y(0), c.Y(M.TD)
        back = [st.rect(self.cx, (zt + zb) / 2, 2.2, zt - zb, P.PANEL, 0.0),
                st.rect(self.cx, (c.Y(0) + c.Y(M.WATER_DEPTH)) / 2, 2.2, c.Y(0) - c.Y(M.WATER_DEPTH), P.SEA, 0.02, alpha=0.5),
                st.rect(self.cx, (c.Y(M.WATER_DEPTH) + zb) / 2, 2.2, c.Y(M.WATER_DEPTH) - zb, P.ROCK, 0.02, alpha=0.5)]
        back.append(st.text("casing strings", self.cx, c.Y(0) + 0.3, 0.2, P.MUTED, 0.1, kind="bold"))
        return back

    def string(self, name, shoe, t0, t1):
        """Add one string; it grows downward from the seabed between t0 and t1. Returns its objects."""
        st, c = self.st, self.c
        w = STRING_W[name]
        top = c.Y(M.WATER_DEPTH)
        z = 0.1 + 0.2 * (1.5 - w)   # inner (narrower) strings sit in front
        bar = st.rect(self.cx, top, w, 0.0001, STRING_COLORS[name], z, anchor="t")
        length = top - c.Y(shoe)
        st.scale_to(bar, t0, t1, sy=length)
        shoe_mark = st.poly([(self.cx - w / 2 - 0.12, c.Y(shoe)), (self.cx - w / 2, c.Y(shoe)), (self.cx - w / 2, c.Y(shoe) + 0.14)], P.WARN, 0.5)
        shoe_mark2 = st.poly([(self.cx + w / 2 + 0.12, c.Y(shoe)), (self.cx + w / 2, c.Y(shoe)), (self.cx + w / 2, c.Y(shoe) + 0.14)], P.WARN, 0.5)
        lab = st.text(f"{STRING_LABEL[name]} shoe {shoe:,.0f} m", self.cx + 1.15, c.Y(shoe), 0.19, P.TEXT, 0.5, align="l")
        st.fade_in([shoe_mark, shoe_mark2, lab], t1 - 0.1, 0.3)
        self.bars[name] = bar
        return [bar, shoe_mark, shoe_mark2, lab]


# ======================================================================================================
class Cutaway:
    """Vertical well cutaway: rock | annulus | pipe | annulus | rock, in a world-space rectangle.

    `eccentric` shifts the pipe sideways (positive = right) to make one gap wide and the other narrow."""

    def __init__(self, st, cx, y_top, y_bot, hole_w=2.4, pipe_w=0.9, wall=0.07, eccentric=0.0, z=0.0, rock=P.ROCK, rock_w=1.6):
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


class BopStack:
    """Subsea BOP stack cutaway with a drill pipe through the bore. Rams / annular / shear rams really close."""
    BORE = 0.8

    def __init__(self, st, cx, cy, s=1.0, z=0.3, pipe_top=None, label=False):
        self.st, self.cx, self.cy, self.s, self.z = st, cx, cy, s, z
        S = s
        W = 2.7 * S
        self.W = W
        y = cy
        parts = {}

        def body(h, color=P.PANEL2):
            nonlocal y
            o = st.rect(cx, y + h * S / 2, W, h * S, color, z)
            c = y + h * S / 2
            y += h * S
            return o, c
        o, _ = body(0.45, P.STEEL_DK)
        parts["connector"] = o
        self.y_connector = cy + 0.225 * S
        o, c = body(0.6); parts["bsr_body"] = o; self.y_bsr = c
        o, c = body(0.6); parts["ram1_body"] = o; self.y_ram1 = c
        o, c = body(0.6); parts["ram2_body"] = o; self.y_ram2 = c
        o, c = body(0.9); parts["ann_body"] = o; self.y_ann = c
        o, c = body(0.4, P.STEEL_DK); parts["flex"] = o; self.y_flex = c
        self.y_top = y
        bore = st.rect(cx, (cy + 0.45 * S + y) / 2, self.BORE * S, y - cy - 0.45 * S, P.BG, z + 0.02)
        parts["bore"] = bore
        # drill pipe (two pieces so the shear ram can cut it)
        pt = (self.y_top + 1.4 * S) if pipe_top is None else pipe_top
        pw = 0.3 * S
        self.pipe_w = pw
        self.pipe_top = st.rect(cx, self.y_bsr, pw, pt - self.y_bsr, P.STEEL, z + 0.05, anchor="b")
        self.pipe_bot = st.rect(cx, cy - 0.4 * S, pw, self.y_bsr - (cy - 0.4 * S), P.STEEL, z + 0.05, anchor="b")
        # ram blocks (retracted), annular packers (retracted)
        k = 0.45 * S
        self.bsr = [st.rect(cx - 1.0 * S, self.y_bsr, 0.9 * S, 0.36 * S, P.BAD, z + 0.08, anchor="c"),
                    st.rect(cx + 1.0 * S, self.y_bsr, 0.9 * S, 0.36 * S, P.BAD, z + 0.08, anchor="c")]
        self.pr = []
        for yy in (self.y_ram1, self.y_ram2):
            self.pr.append([st.rect(cx - 1.0 * S, yy, 0.9 * S, 0.36 * S, P.WARN, z + 0.08), st.rect(cx + 1.0 * S, yy, 0.9 * S, 0.36 * S, P.WARN, z + 0.08)])
        self.ann = [st.rect(cx - 0.68 * S, self.y_ann, 0.5 * S, 0.62 * S, "#2f2f35", z + 0.08), st.rect(cx + 0.68 * S, self.y_ann, 0.5 * S, 0.62 * S, "#2f2f35", z + 0.08)]
        self.parts = parts
        self.all = list(parts.values()) + [self.pipe_top, self.pipe_bot] + self.bsr + [b for pr in self.pr for b in pr] + self.ann
        if label:
            self.labels = self._labels()
            self.all += self.labels

    def _labels(self):
        st, cx, S = self.st, self.cx, self.s
        L = []
        for name, yy, col in (("annular preventer", self.y_ann, P.TEXT), ("pipe rams", (self.y_ram1 + self.y_ram2) / 2, P.WARN),
                              ("blind shear rams", self.y_bsr, P.BAD), ("wellhead connector", self.y_connector, P.MUTED)):
            L.append(st.text(name, cx + 1.55 * S, yy, 0.22 * S + 0.04, col, self.z + 0.1, align="l", kind="bold"))
        return L

    # --- closing actions ---------------------------------------------------------------------------
    def close_annular(self, t0, t1):
        S, st, cx = self.s, self.st, self.cx
        st.move(self.ann[0], t0, t1, to=(cx - (self.pipe_w / 2 + 0.25 * S), self.y_ann))
        st.move(self.ann[1], t0, t1, to=(cx + (self.pipe_w / 2 + 0.25 * S), self.y_ann))

    def close_pipe_rams(self, t0, t1):
        S, st, cx = self.s, self.st, self.cx
        for pr in self.pr:
            st.move(pr[0], t0, t1, to=(cx - (self.pipe_w / 2 + 0.45 * S), pr[0].location[1]))
            st.move(pr[1], t0, t1, to=(cx + (self.pipe_w / 2 + 0.45 * S), pr[1].location[1]))

    def shear(self, t0, t1, t_fall=None):
        S, st, cx = self.s, self.st, self.cx
        st.move(self.bsr[0], t0, t1, to=(cx - 0.45 * S, self.y_bsr))
        st.move(self.bsr[1], t0, t1, to=(cx + 0.45 * S, self.y_bsr))
        tf = t1 if t_fall is None else t_fall
        st.move(self.pipe_top, tf, tf + 1.0, dy=-0.9 * S)

    def open_all(self, t0, t1):
        S, st, cx = self.s, self.st, self.cx
        st.move(self.ann[0], t0, t1, to=(cx - 0.68 * S, self.y_ann))
        st.move(self.ann[1], t0, t1, to=(cx + 0.68 * S, self.y_ann))
        for pr in self.pr:
            st.move(pr[0], t0, t1, to=(cx - 1.0 * S, pr[0].location[1]))
            st.move(pr[1], t0, t1, to=(cx + 1.0 * S, pr[1].location[1]))


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
