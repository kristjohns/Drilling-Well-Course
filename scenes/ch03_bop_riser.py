"""Ch 3: BOP, riser, and the closed loop.

3.01 the BOP is lowered on the riser, latches, and the mud makes its first full circuit (st.flow, path by path)
3.02 THE BOP CLOSING ANIMATION: annular (rubber packer) -> pipe rams -> blind shear rams cut the pipe body and seal the
     empty bore; the accumulator stores the energy to do it without rig power
3.03 why the closed loop matters: weighted mud, flow in vs flow out + tank level, shut in at the seabed and circulate
     through the choke; then the informal two-barrier shield
3.04 tested before trusted: test plug in the wellhead, each element closed, pressured and held; shear rams on an empty bore
3.05 the leak-off test at the 20 in shoe: drill out, close in, pump slowly, the line bends, 37 bar + mud column = 1.50 sg

Detail shots use a content-only camera (View): the header, well strip and term cards stay put while the drawing
pushes in; labels live in screen space and follow the drawing (`View.follow`).
"""
from __future__ import annotations
import math

import skia

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common.shapes import pill
from scenes.common.stage import Track, as_list, ease_inout
from scenes.common.look import wrap_to, col, hex_rgb

TITLE = "BOP, riser, and the closed loop"

RUBBER = "#272b35"       # elastomer (annular packer, ram faces): dark on the steel body
RUBBER_HI = "#a8b3c6"    # bright edge of the rubber where it meets the pipe
HYD = "#c4b5fd"          # hydraulic control fluid (accumulator drawing only)
N2 = "#9fb0c8"           # nitrogen pre-charge (accumulator drawing only)
SKY = "#0e1628"

MW_NEXT = M.section_mud_weights()["20in surface casing"]          # 1.12 sg, mud for the section below the 20 in shoe
SHOE_20 = {s.name: s for s in M.programme()}["20in surface casing"].shoe   # 1,000 m
SHOE_13 = {s.name: s for s in M.programme()}["13-3/8in intermediate"].shoe  # 2,000 m
FG_SHOE = M.fg(SHOE_20)                                                     # 1.50 sg
P_LOT = (FG_SHOE - MW_NEXT) * M.G * SHOE_20                                 # ~37 bar at surface
P_COL = MW_NEXT * M.G * SHOE_20                                             # ~110 bar mud column


def _w(b, i, needle, frac=0.0):
    return b.word(i, needle, frac)


def _clamp(v, a, b):
    return max(a, min(b, v))


# ====================================================================================================== content camera
class View:
    """A camera for the drawing only. Objects and procedurals created inside `with view:` are drawn through a local
    transform screen = world * s + d (clipped to `clip`), so the chapter furniture is unaffected. s and d are
    interpolated linearly in the eased parameter, so a screen-space label moved with the same timing (follow())
    stays glued to its world point."""

    def __init__(self, st, t0, t1, z=0.2, clip=(-6.32, -4.5, 8.0, 3.93)):
        self.st, self.clip = st, clip
        self.ts, self.tx, self.ty = Track(), Track(), Track()
        self.cur = (1.0, 0.0, 0.0)
        self.objs, self.procs, self.follows, self.segs = [], [], [], []
        st.procedural(t0, t1, z, self._draw)

    def __enter__(self):
        self._n0, self._p0 = len(self.st.objs), len(self.st.procedurals)
        return self

    def __exit__(self, *a):
        st = self.st
        for o in st.objs[self._n0:]:
            if not o.hide_render:
                o.hide_render = True
                self.objs.append(o)
        self.procs += st.procedurals[self._p0:]
        del st.procedurals[self._p0:]

    def camera(self, t0, t1, focus, at=None, scale=1.0, interp="BEZIER"):
        """Show world point `focus` at screen point `at` (default: where it is now unzoomed) with zoom `scale`."""
        at = focus if at is None else at
        s1, dx1, dy1 = scale, at[0] - focus[0] * scale, at[1] - focus[1] * scale
        s0, dx0, dy0 = self.cur
        for tr, a, b in ((self.ts, s0, s1), (self.tx, dx0, dx1), (self.ty, dy0, dy1)):
            tr.set(t0, a, interp)
            tr.set(t1, b, interp)
        self.segs.append((t0, t1, interp, s1, dx1, dy1))
        self.cur = (s1, dx1, dy1)

    def home(self, t0, t1):
        self.camera(t0, t1, (0.0, 0.0), (0.0, 0.0), 1.0)

    def screen(self, x, y, state=None):
        s, dx, dy = state or self.cur
        return x * s + dx, y * s + dy

    def follow(self, objs, wx, wy):
        """Screen-space objects (made at their unzoomed position) that stay attached to world point (wx, wy)."""
        self.follows.append((as_list(objs), wx, wy))

    def finish(self):
        st = self.st
        for objs, wx, wy in self.follows:
            for o in objs:
                x, y, _ = st.state[o]["loc"]
                ox, oy = x - wx, y - wy
                for (t0, t1, interp, s1, dx1, dy1) in self.segs:
                    st.move(o, t0, t1, to=(wx * s1 + dx1 + ox, wy * s1 + dy1 + oy), interp=interp)

    def _draw(self, c, t, look):
        s = self.ts.eval(t) if self.ts else 1.0
        dx = self.tx.eval(t) if self.tx else 0.0
        dy = self.ty.eval(t) if self.ty else 0.0
        M0, k0 = look.M, look.k
        L = skia.Matrix()
        L.setAll(s, 0, dx, 0, s, dy, 0, 0, 1)
        M1 = skia.Matrix.Concat(M0, L)
        c.save()
        c.setMatrix(M0)
        x0, y0, x1, y1 = self.clip
        c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
        look.M, look.k = M1, k0 * s
        items = []
        for o in self.objs:
            if all(a <= t < b for a, b in o.windows):
                items.append((o.location[2], o.idx, o))
        for (a, b, z, fn) in self.procs:
            if a <= t < b:
                items.append((z, 1e12 + id(fn) % 100000, fn))
        items.sort(key=lambda it: (it[0], it[1]))
        try:
            for _, _, o in items:
                if callable(o):
                    c.save()
                    c.setMatrix(M1)
                    o(c, t, look)
                    c.restore()
                else:
                    look._draw(c, o, t)
        finally:
            look.M, look.k = M0, k0
            c.restore()


# ====================================================================================================== small helpers
def _dashed_rect(st, x0, y0, x1, y1, color=P.MUTED, z=0.6, width=0.035):
    out = []
    for p, q in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        out += st.dashed(p, q, color, width, 0.16, 0.1, z)
    return out


def _check(st, x, y, t, s=0.17, z=1.2, color=P.SAFE):
    """A check mark drawn on stroke by stroke, on a round plate."""
    plate = st.circle(x, y, s * 1.45, P.PANEL2, z - 0.01, role="disc")
    ln = st.line([(x - s * 0.62, y + 0.0), (x - s * 0.15, y - s * 0.48), (x + s * 0.7, y + s * 0.55)], color, 0.06, z)
    st.pop_in(plate, t - 0.05, 0.3)
    st.draw_on(ln, t + 0.05, t + 0.45, "BEZIER")
    return [plate, ln]


def _x_mark(st, x, y, r, t, z=1.5, width=0.08):
    a = st.line([(x - r, y + r), (x + r, y - r)], P.BAD, width, z)
    c = st.line([(x - r, y - r), (x + r, y + r)], P.BAD, width, z)
    st.draw_on(a, t, t + 0.3, "BEZIER")
    st.draw_on(c, t + 0.2, t + 0.5, "BEZIER")
    return [a, c]


def _orb(st, x, y, n, t, color=P.MUD, r=0.17, z=1.0, fg=P.BG):
    o = st.circle(x, y, r, color, z)
    tx = st.text(str(n), x, y - 0.005, 0.15, fg, z + 0.01, kind="bold")
    st.pop_in(o, t, 0.35)
    st.fade_in(tx, t + 0.1, 0.25)
    return [o, tx]


def _arc_pts(cx, cy, r, a0, a1, n=48):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def _dial(st, x, y, r, z=0.4, color=P.MUTED):
    """Semicircular gauge face. Returns objects."""
    face = st.poly([(x, y)] + _arc_pts(x, y, r, 0, 180), P.PANEL2, z)
    rim = st.line(_arc_pts(x, y, r, 0, 180), color, 0.03, z + 0.01, role="hair")
    return [face, rim]


def _needle(st, x, y, length, deg, color=P.TEXT, z=0.5, width=0.06):
    n = st.rect(x, y, length, width, color, z, anchor="l", rot=deg, role="shaft")
    hub = st.circle(x, y, width * 1.5, P.TEXT, z + 0.01, role="disc")
    return n, hub


# ====================================================================================================== the BOP stack
class Stack:
    """Subsea BOP stack cutaway, bottom to top: wellhead connector, two pipe rams, blind shear rams, LMRP connector,
    annular preventer, riser adapter. Ram blocks slide in their cavities, the annular's rubber packer is squeezed in by
    its piston, the blind shear blades overlap and cut the pipe body."""
    H = (("con", 0.55), ("pr1", 0.72), ("pr2", 0.72), ("bsr", 0.80), ("lmrp", 0.22), ("ann", 1.25), ("top", 0.32))

    def __init__(self, st, cx, y0, S=1.0, z=0.3, pipe=None, joint=None, outlet=False):
        self.st, self.cx, self.y0, self.S, self.z = st, cx, y0, S, z
        BW, BON, BR, PW = 2.0 * S, 0.72 * S, 0.8 * S, 0.26 * S
        self.BW, self.BON, self.BR, self.PW = BW, BON, BR, PW
        self.half = BW / 2 + BON                      # half-width over the bonnets
        y = y0
        self.y, self.h = {}, {}
        body = []
        widths = {"con": BW * 0.9, "lmrp": BW * 0.78, "ann": BW * 0.96, "top": BW * 0.48}
        for key, h in self.H:
            hh = h * S
            colr = P.STEEL if key == "lmrp" else P.STEEL_DK
            body.append(st.rect(cx, y + hh / 2, widths.get(key, BW), hh, colr, z))
            self.y[key], self.h[key] = y + hh / 2, hh
            y += hh
        self.y_top = y
        self.y_pr = (self.y["pr1"] + self.y["pr2"]) / 2
        # flanges between the bodies
        yy = y0
        for key, h in self.H[:-1]:
            yy += h * S
            body.append(st.rect(cx, yy, BW * (0.86 if key in ("bsr", "lmrp") else 1.04), 0.07 * S, P.STEEL, z + 0.005))
        # ram bonnets + cavities
        self.cav = {}
        for key in ("pr1", "pr2", "bsr"):
            yc = self.y[key]
            bh = (0.5 if key != "bsr" else 0.58) * S
            for sd in (-1, 1):
                body.append(st.rect(cx + sd * (BW / 2 + BON / 2 - 0.02 * S), yc, BON, bh, P.STEEL_DK, z - 0.01))
                body.append(st.rect(cx + sd * (BW / 2 + BON - 0.03 * S), yc, 0.09 * S, bh + 0.1 * S, P.STEEL, z - 0.005))
            rh = (0.3 if key != "bsr" else 0.36) * S
            body.append(st.rect(cx, yc, 2 * (BW / 2 + BON - 0.1 * S), rh + 0.04 * S, P.BG, z + 0.01))
            self.cav[key] = rh
        ya = self.y["ann"]
        # the bore
        self.bore = st.rect(cx, (y0 + self.y_top) / 2, BR, self.y_top - y0 - 0.02 * S, P.BG, z + 0.02)
        body.append(self.bore)
        if outlet:      # choke outlet on the right, between the two pipe rams (below the upper one)
            yo = self.y["pr1"] + 0.25 * S
            body.append(st.rect(cx + BW / 2 + 0.25 * S, yo, 0.5 * S, 0.13 * S, P.STEEL, z - 0.02))
            self.y_outlet = yo
        self.body = body
        # --- pipe rams: block + rubber face + rod + piston, per side
        self.rams = {}
        for key in ("pr1", "pr2"):
            yc, rh = self.y[key], self.cav[key]
            sides = []
            for sd in (-1, 1):
                RB = 0.62 * S
                face = cx + sd * (BR / 2 + 0.03 * S)
                blk = st.rect(face + sd * RB / 2, yc, RB, rh * 0.92, P.STEEL, z + 0.06)
                rub = st.rect(face + sd * 0.035 * S, yc, 0.07 * S, rh * 0.92, RUBBER, z + 0.065, role="solid")
                rod_x0, rod_x1 = face + sd * RB, cx + sd * (BW / 2 + BON - 0.2 * S)
                rod = st.rect((rod_x0 + rod_x1) / 2, yc, abs(rod_x1 - rod_x0), 0.08 * S, P.STEEL_DK, z + 0.055)
                pis = st.rect(rod_x1, yc, 0.1 * S, rh * 1.25, P.STEEL, z + 0.056)
                sides.append([blk, rub, rod, pis])
            self.rams[key] = sides
        # --- blind shear rams: body + blade (left blade on the upper half, right blade on the lower half)
        yc, rh = self.y["bsr"], self.cav["bsr"]
        BL, RB = 0.34 * S, 0.6 * S
        self.BL = BL
        self.shear_blocks = []
        for sd in (-1, 1):
            face = cx + sd * (BR / 2 + 0.03 * S + BL)
            blk = st.rect(face + sd * RB / 2, yc, RB, rh * 0.94, P.STEEL, z + 0.06)
            if sd < 0:
                pts = [(face, yc), (face + BL, yc), (face + BL - 0.1 * S, yc + rh * 0.47), (face, yc + rh * 0.47)]
            else:
                pts = [(face, yc), (face - BL, yc), (face - BL + 0.1 * S, yc - rh * 0.47), (face, yc - rh * 0.47)]
            blade = st.poly(pts, "#e6ecf3", z + 0.062)
            rod_x0, rod_x1 = face + sd * RB, cx + sd * (BW / 2 + BON - 0.2 * S)
            rod = st.rect((rod_x0 + rod_x1) / 2, yc, abs(rod_x1 - rod_x0), 0.08 * S, P.STEEL_DK, z + 0.055)
            pis = st.rect(rod_x1, yc, 0.1 * S, rh * 1.2, P.STEEL, z + 0.056)
            self.shear_blocks.append([blk, blade, rod, pis])
        # --- annular: rubber packer halves (anchored at the outer wall, squeezed inward) + piston
        self.pk_open = 0.83 * S - BR / 2 - 0.02 * S
        self.pk_closed = 0.83 * S - PW / 2
        self.pk_full = 0.83 * S - 0.005 * S
        ypk = ya + 0.14 * S
        self.packer = [st.rect(cx - 0.83 * S, ypk, self.pk_open, 0.56 * S, RUBBER, z + 0.06, anchor="l", role="flat"),
                       st.rect(cx + 0.83 * S, ypk, self.pk_open, 0.56 * S, RUBBER, z + 0.06, anchor="r", role="flat")]
        ex = cx - 0.83 * S + self.pk_open
        self.packer_edge = [st.rect(ex - 0.025 * S, ypk, 0.05 * S, 0.5 * S, RUBBER_HI, z + 0.065, role="solid"),
                            st.rect(2 * cx - ex + 0.025 * S, ypk, 0.05 * S, 0.5 * S, RUBBER_HI, z + 0.065, role="solid")]
        # steel inserts in the packer (they ride with the rubber)
        self.packer_edge += [st.rect(ex - 0.1 * S, ypk + sy * 0.2 * S, 0.12 * S, 0.06 * S, P.STEEL, z + 0.066, role="solid") for sy in (-1, 1)]
        self.packer_edge += [st.rect(2 * cx - ex + 0.1 * S, ypk + sy * 0.2 * S, 0.12 * S, 0.06 * S, P.STEEL, z + 0.066, role="solid") for sy in (-1, 1)]
        self.piston = [st.rect(cx - 0.58 * S, ya - 0.24 * S, 0.5 * S, 0.14 * S, P.STEEL, z + 0.058),
                       st.rect(cx + 0.58 * S, ya - 0.24 * S, 0.5 * S, 0.14 * S, P.STEEL, z + 0.058)]
        # --- connector latch dogs
        yl = self.y["con"] - 0.12 * S
        self.dogs = [st.rect(cx - BR / 2 - 0.12 * S, yl, 0.16 * S, 0.14 * S, P.STEEL, z + 0.07),
                     st.rect(cx + BR / 2 + 0.12 * S, yl, 0.16 * S, 0.14 * S, P.STEEL, z + 0.07)]
        self.parts = (self.body + [o for k in self.rams.values() for sd in k for o in sd] +
                      [o for sd in self.shear_blocks for o in sd] + self.packer + self.packer_edge + self.piston + self.dogs)
        # --- drill pipe (cut into three pieces at the shear rams) and a tool joint
        self.pipe = []
        if pipe is not None:
            yb_, yt_ = pipe
            lo, hi = yc - rh * 0.5, yc + rh * 0.5
            self.p_low = st.rect(cx, (yb_ + lo) / 2, PW, lo - yb_, P.STEEL, z + 0.04)
            self.p_mid = st.rect(cx, yc, PW, hi - lo, P.STEEL, z + 0.04)
            self.p_up = st.rect(cx, (hi + yt_) / 2, PW, yt_ - hi, P.STEEL, z + 0.04)
            self.pipe = [self.p_low, self.p_mid, self.p_up]
            self.joint = None
            if joint is not None:
                self.joint = st.rect(cx, joint, 0.44 * S, 0.3 * S, P.STEEL, z + 0.045)
                self.pipe.append(self.joint)
        self.all = self.parts + self.pipe

    # --- actions ---------------------------------------------------------------------------------------------
    def _ram_dx(self):
        return self.BR / 2 + 0.03 * self.S - self.PW / 2

    def close_rams(self, t0, t1, keys=("pr1", "pr2"), sign=1):
        d = self._ram_dx() * sign
        for key in keys:
            for sd, objs in zip((-1, 1), self.rams[key]):
                self.st.move(objs, t0, t1, dx=-sd * d)

    def open_rams(self, t0, t1, keys=("pr1", "pr2")):
        self.close_rams(t0, t1, keys, sign=-1)

    def close_annular(self, t0, t1, empty=False, sign=1):
        st, S = self.st, self.S
        w1 = (self.pk_full if empty else self.pk_closed)
        w0 = self.pk_open
        if sign < 0:
            w0, w1 = w1, w0
        st.scale_to(self.packer, t0, t1, sx=w1)
        st.move(self.packer_edge[0::2][:1] + self.packer_edge[2:4], t0, t1, dx=w1 - w0)
        st.move(self.packer_edge[1:2] + self.packer_edge[4:6], t0, t1, dx=-(w1 - w0))
        st.move(self.piston, t0, t1, dy=sign * 0.09 * S)
        self._ann_w = w1

    def open_annular(self, t0, t1, empty=False):
        self.close_annular(t0, t1, empty, sign=-1)

    def _bsr_dx(self):
        return self.BR / 2 + 0.03 * self.S + self.BL / 2

    def close_bsr(self, t0, t1, sign=1):
        d = self._bsr_dx() * sign
        for sd, objs in zip((-1, 1), self.shear_blocks):
            self.st.move(objs, t0, t1, dx=-sd * d)

    def open_bsr(self, t0, t1):
        self.close_bsr(t0, t1, sign=-1)

    def shear(self, t0, t1, lift=0.6, t_lift=None):
        """Blades close; where they meet the pipe its body is crushed and cut; the upper string is then picked up."""
        st = self.st
        self.close_bsr(t0, t1)
        f_contact = (self.BR / 2 + 0.03 * self.S - self.PW / 2) / self._bsr_dx()
        tc = t0 + (t1 - t0) * (0.35 + 0.4 * f_contact)
        st.scale_to(self.p_mid, tc, t1, sx=0.0001)
        st.ripple(self.cx, self.y["bsr"], t1 - 0.05, t1 + 0.6, P.WARN, period=0.5, r0=0.1, r1=0.9 * self.S, width=0.05, z=self.z + 0.3)
        tl_ = t1 + 0.35 if t_lift is None else t_lift
        up = [self.p_up] + ([self.joint] if self.joint is not None else [])
        st.move(up, tl_, tl_ + 1.1, dy=lift * self.S)
        return tc

    def latch(self, t0, t1):
        st, S = self.st, self.S
        st.move(self.dogs[0], t0, t1, dx=0.1 * S)
        st.move(self.dogs[1], t0, t1, dx=-0.1 * S)

    def right(self, key):
        """World point just right of the bonnets at element `key`."""
        return self.cx + self.half, self.y[key] if key != "pr" else self.y_pr


# ====================================================================================================== 3.01 riser, latch, circuit
CX1 = -2.4
WIN1 = (-6.2, -3.62, 1.55, 3.82)        # scene window (x0, y0, x1, y1)
SS1, DECK1, SB1, SHOE1, BIT1 = 2.0, 2.5, -1.15, -3.05, -2.68
S1 = 0.42


def beat_riser(st, tl):
    b = tl["3.01"]
    s = b.sent
    t_low = _w(b, 1, "lowered")
    t_lat = _w(b, 1, "latches")
    t_land = t_lat + 0.35
    t_dp, t_an = _w(b, 2, "down the drill pipe"), _w(b, 2, "up the annulus")
    t_ri, t_tk = _w(b, 2, "the riser"), _w(b, 2, "back to the rig")
    t_sb = _w(b, 2, "instead of")
    x0, y0, x1, y1 = WIN1
    with st.span(b.start, b.end):
        view = View(st, b.start, b.end, z=0.2, clip=WIN1)
        with view:
            # ---- sky, sea, rock
            st.rect((x0 + x1) / 2, (SS1 + y1 + 1) / 2, x1 - x0 + 2, y1 + 1 - SS1, SKY, 0.0, role="flat")
            st.rect((x0 + x1) / 2, (SS1 + SB1) / 2, x1 - x0 + 2, SS1 - SB1, P.SEA, 0.0)
            st.rect((x0 + x1) / 2, SS1, x1 - x0 + 2, 0.03, P.PORE, 0.01, alpha=0.6)
            st.rect((x0 + x1) / 2, (SB1 + y0 - 1) / 2, x1 - x0 + 2, SB1 - y0 + 1, P.ROCK2, 0.0)
            st.rect((x0 + x1) / 2, SB1, x1 - x0 + 2, 0.06, "#8b7a5e", 0.02)
            # ---- the hole: 30 in conductor, 26 in hole, cemented 20 in casing, shoe track
            Z = 0.1
            st.rect(CX1, (SB1 + SHOE1 - 0.05) / 2, 0.84, SB1 - SHOE1 + 0.05, P.CEMENT, Z)
            for sd in (-1, 1):
                st.rect(CX1 + sd * 0.45, SB1 - 0.42, 0.06, 0.84, P.STEEL_DK, Z + 0.02)
                st.rect(CX1 + sd * 0.27, (SB1 + 0.3 + SHOE1) / 2, 0.05, SB1 + 0.3 - SHOE1, P.STEEL, Z + 0.03)
                st.poly([(CX1 + sd * 0.3, SHOE1), (CX1 + sd * 0.42, SHOE1), (CX1 + sd * 0.3, SHOE1 + 0.12)], P.WARN, Z + 0.04)
            casing_in = st.rect(CX1, (SB1 + 0.3 + SHOE1) / 2, 0.49, SB1 + 0.3 - SHOE1, P.BG, Z + 0.02)
            st.rect(CX1, SHOE1 + 0.16, 0.49, 0.32, P.CEMENT, Z + 0.025)
            st.rect(CX1, SB1 + 0.1, 0.72, 0.4, P.STEEL_DK, Z + 0.05)          # low-pressure housing
            st.rect(CX1, SB1 + 0.25, 0.56, 0.3, P.STEEL, Z + 0.06)            # high-pressure housing (hub)
            st.rect(CX1, SB1 + 0.25, 0.4, 0.3, P.BG, Z + 0.065)
            # ---- the rig: pontoons, columns, deck, derrick, mud tanks, pump
            for xx in (CX1 - 1.55, CX1 + 2.2):
                st.rect(xx, SS1 - 0.3, 1.0, 0.3, P.STEEL_DK, 0.3)
                st.rect(xx, (SS1 - 0.2 + DECK1) / 2, 0.42, DECK1 - SS1 + 0.2, P.STEEL_DK, 0.3)
            st.rect(CX1 + 0.35, DECK1 - 0.08, 4.6, 0.18, P.STEEL_DK, 0.31)
            for sd in (-1, 1):
                st.line([(CX1 + sd * 0.55, DECK1), (CX1 + sd * 0.16, 3.72)], P.STEEL_DK, 0.05, 0.3)
            for yy in (2.85, 3.2, 3.52):
                f = (yy - DECK1) / (3.72 - DECK1)
                hw = 0.55 + (0.16 - 0.55) * f
                st.line([(CX1 - hw, yy), (CX1 + hw, yy)], P.STEEL_DK, 0.03, 0.3)
            st.rect(CX1, 3.72, 0.5, 0.08, P.STEEL_DK, 0.31)
            st.rect(CX1, 3.42, 0.32, 0.16, P.STEEL, 0.32)                     # top drive
            tank_x = CX1 + 1.55
            st.rect(tank_x, DECK1 + 0.24, 0.95, 0.46, P.STEEL_DK, 0.31)
            tank_mud = st.rect(tank_x, DECK1 + 0.06, 0.83, 0.3, P.MUD, 0.32, anchor="b")
            pump_x = CX1 + 2.55
            st.rect(pump_x, DECK1 + 0.17, 0.4, 0.3, P.STEEL, 0.31)
            pipe_rt = [(tank_x + 0.47, DECK1 + 0.15), (pump_x - 0.2, DECK1 + 0.15)]
            st.line(pipe_rt, P.STEEL_DK, 0.05, 0.305)
            standpipe = [(pump_x, DECK1 + 0.32), (pump_x, 3.42), (CX1 + 0.16, 3.42)]
            st.line(standpipe, P.STEEL_DK, 0.05, 0.305)
            flowline = [(CX1 + 0.3, 2.92), (tank_x - 0.3, 2.92), (tank_x - 0.3, DECK1 + 0.5)]
            st.line(flowline, P.STEEL_DK, 0.06, 0.305)
            st.rect(CX1, 2.82, 0.62, 0.24, P.STEEL_DK, 0.33)                  # bell nipple on the rig floor
            st.rect(CX1, 2.82, 0.48, 0.24, P.BG, 0.335)
            # ---- ghost of the riserless set-up (Ch 2): dashed BOP and riser where they will be
            stk_tmp = None
            y_land = SB1 + 0.12
            hstack = sum(h for _, h in Stack.H) * S1
            gw = (2.0 / 2 + 0.72) * S1
            ghost = _dashed_rect(st, CX1 - gw, y_land, CX1 + gw, y_land + hstack, P.MUTED, 0.25)
            ghost += st.dashed((CX1 - 0.3, y_land + hstack), (CX1 - 0.3, DECK1 - 0.2), P.MUTED, 0.03, 0.16, 0.1, 0.25)
            ghost += st.dashed((CX1 + 0.3, y_land + hstack), (CX1 + 0.3, DECK1 - 0.2), P.MUTED, 0.03, 0.16, 0.1, 0.25)
            st.fade_in(ghost, b.start + 0.4, 0.6)
            st.fade_out(ghost, t_land - 0.2, 0.6)
            # ---- the stack, lowered on the riser
            y_start = DECK1 - 0.12 - hstack
            stk = Stack(st, CX1, y_start, S=S1, z=0.4)
            D = y_start - y_land
            riser_top = DECK1 + 0.1
            h0 = riser_top - stk.y_top
            riser = st.rect(CX1, riser_top, 0.62, h0, P.STEEL, 0.38, anchor="t")
            riser_in = st.rect(CX1, riser_top, 0.48, h0, P.BG, 0.385, anchor="t")
            st.fade_in(stk.all + [riser, riser_in], s[1] - 0.3, 0.5)
            t_a, t_b = t_low - 0.1, t_lat
            st.move(stk.all, t_a, t_b, dy=-D)
            st.scale_to([riser, riser_in], t_a, t_b, sy=h0 + D)
            stk.latch(t_land - 0.15, t_land + 0.35)
            st.ripple(CX1, SB1 + 0.25, t_land, t_land + 1.2, P.TEXT, period=0.6, r0=0.2, r1=1.0, width=0.03, z=0.9)
            # ---- drill pipe run in after the latch, bit stops above the shoe track
            t_p0, t_p1 = t_land + 0.6, min(t_land + 2.6, t_dp - 0.3)
            dp = st.rect(CX1, 3.34, 0.13, 0.0001, P.STEEL, 0.45, anchor="t")
            bit = st.poly([(CX1 - 0.15, 3.34), (CX1 + 0.15, 3.34), (CX1 + 0.09, 3.2), (CX1 - 0.09, 3.2)], P.STEEL_DK, 0.46)
            st.fade_in([dp, bit], t_p0 - 0.1, 0.2)
            st.scale_to(dp, t_p0, t_p1, sy=3.34 - BIT1)
            st.move(bit, t_p0, t_p1, dy=BIT1 - 3.34)
            # ---- mud fills the riser, bore and casing; then the circuit, path by path, as it is spoken
            fills = [st.rect(CX1, riser_top, 0.48, riser_top - (y_land + hstack), P.MUD, 0.386, anchor="t", alpha=0.22),
                     st.rect(CX1, (y_land + y_land + hstack) / 2, stk.BR, hstack, P.MUD, 0.43, alpha=0.22),
                     st.rect(CX1, (SB1 + 0.3 + SHOE1 + 0.32) / 2, 0.49, SB1 + 0.3 - SHOE1 - 0.32, P.MUD, Z + 0.03, alpha=0.22)]
            st.fade_in(fills, t_p1 - 0.2, 0.8)
            ax = 0.13
            down = [(tank_x + 0.3, DECK1 + 0.15), (pump_x, DECK1 + 0.15), (pump_x, 3.42), (CX1, 3.42), (CX1, BIT1 - 0.05)]
            st.flow(down, t_dp - 0.1, b.end, P.MUD, n=34, speed=1.0, r=0.03, z=0.6)
            for sd in (-1, 1):
                ann = [(CX1 + sd * 0.05, BIT1 - 0.1), (CX1 + sd * ax, BIT1 + 0.05), (CX1 + sd * ax, y_land)]
                st.flow(ann, t_an - 0.1, b.end, P.MUD, n=11, speed=0.8, r=0.03, z=0.6)
                up = [(CX1 + sd * ax, y_land), (CX1 + sd * ax, 2.85)]
                st.flow(up, t_ri - 0.1, b.end, P.MUD, n=14, speed=0.8, r=0.03, z=0.6)
            back = [(CX1 + ax, 2.85), (CX1 + 0.3, 2.92), (tank_x - 0.3, 2.92), (tank_x - 0.3, DECK1 + 0.4)]
            st.flow(back, t_tk - 0.1, b.end, P.MUD, n=6, speed=0.8, r=0.03, z=0.6)
            st.scale_to(tank_mud, t_tk, t_tk + 0.01, sy=0.3)
            # ---- the old way, crossed out: returns onto the seabed
            plume = [st.ellipse(CX1 + 0.75 + 0.32 * i, SB1 + 0.03, 0.28 - 0.04 * i, 0.09 - 0.012 * i, "#9b7a55", 0.7, alpha=0.75, role="solid")
                     for i in range(4)]
            plume += [st.ellipse(CX1 + 0.95, SB1 + 0.3, 0.45, 0.22, "#8f8170", 0.69, alpha=0.3, role="solid")]
            st.fade_in(plume, t_sb - 0.2, 0.3)
            xm = _x_mark(st, CX1 + 1.0, SB1 + 0.22, 0.2, t_sb + 0.2, z=0.75, width=0.06)
            # circuit numbers on the drawing
            orbs = (_orb(st, pump_x + 0.32, 3.05, 1, t_dp, r=0.14) + _orb(st, CX1 + 0.62, -2.05, 2, t_an, r=0.14) +
                    _orb(st, CX1 + 0.6, 1.75, 3, t_ri, r=0.14) + _orb(st, tank_x, 3.12, 4, t_tk, r=0.14))
        # ---- labels in screen space that follow the drawing
        lab_r = pill(st, CX1 - 0.55, 1.2, "marine riser", P.PANEL2, P.TEXT, 0.19, 1.0, align="r")
        st.fade_in(lab_r, s[2] - 0.2, 0.4)
        view.follow(lab_r, CX1 - 0.55, 1.2)
        lab_b = pill(st, CX1 - 0.55, y_start + hstack * 0.55, "blowout preventer (BOP)", P.PANEL2, P.TEXT, 0.19, 1.0, align="r")
        st.fade_in(lab_b, s[1] - 0.1, 0.4)
        st.move(lab_b, t_a, t_b, dy=-D)
        view.follow(lab_b, CX1 - 0.55, y_land + hstack * 0.55)
        lab_w = pill(st, CX1 - 0.55, SB1 + 0.05, "wellhead", P.PANEL2, P.TEXT, 0.19, 1.0, align="r")
        st.fade_in(lab_w, b.start + 0.6, 0.4)
        view.follow(lab_w, CX1 - 0.55, SB1 + 0.05)
        lab_s = pill(st, CX1 - 0.55, SHOE1 + 0.05, f"20 in shoe · {SHOE_20:,.0f} m", P.PANEL2, P.MUTED, 0.17, 1.0, align="r")
        lab_sb = pill(st, CX1 - 0.55, SB1 - 0.45, f"seabed · {M.WATER_DEPTH:.0f} m", P.PANEL2, P.MUTED, 0.17, 1.0, align="r")
        st.fade_in(lab_s + lab_sb, b.start + 0.8, 0.4)
        view.follow(lab_s, CX1 - 0.55, SHOE1 + 0.05)
        view.follow(lab_sb, CX1 - 0.55, SB1 - 0.45)
        st.fade(lab_s + lab_sb, t_lat - 1.4, t_lat - 1.0, 1.0, 0.0)          # out of frame during the push-in
        st.fade(lab_s + lab_sb, s[2] + 0.2, s[2] + 0.6, 0.0, 1.0)
        lab_g = st.text("Ch 2: no BOP, no riser", CX1 + 0.85, -0.1, 0.16, P.MUTED, 1.0, align="l", kind="bold")
        st.fade_in(lab_g, b.start + 0.6, 0.5)
        st.fade_out(lab_g, t_low, 0.4)
        # ---- camera: push in on the latch, back out for the full circuit
        view.camera(t_lat - 1.3, t_land + 0.1, focus=(CX1, SB1 + 0.3), at=(CX1 + 0.6, -0.2), scale=1.7)
        view.home(s[2] - 0.6, s[2] + 0.8)
        view.finish()
        # ---- right column: depth read-out while lowering, then the circuit list
        RX = 2.2
        hud = [st.text("LOWERING THE BOP", RX, 2.6, 0.17, P.MUTED, 0.6, align="l", kind="bold"),
               st.text("water depth", RX, 0.95, 0.17, P.MUTED, 0.6, align="l")]
        st.fade_in(hud, s[1] - 0.2, 0.4)
        st.counter(RX, 1.75, t_a, t_b, 0.0, M.WATER_DEPTH, fmt="{:.0f} m", size=0.62, color=P.PORE, align="l", hold=s[2] - 0.5)
        lat = pill(st, RX, 0.2, "latched onto the wellhead", P.PANEL2, P.SAFE, 0.21, 0.6, align="l")
        st.fade_in(lat, t_land, 0.4)
        st.fade_out(hud + lat, s[2] - 0.8, 0.4)
        head = st.text("THE MUD CIRCUIT", RX, 2.75, 0.17, P.MUTED, 0.6, align="l", kind="bold")
        st.fade_in(head, s[2], 0.4)
        rows = [("down the drill pipe", t_dp), ("up the annulus", t_an), ("up the riser", t_ri), ("back to the rig's tanks", t_tk)]
        prev = None
        for i, (txt, t) in enumerate(rows):
            yy = 2.05 - i * 0.72
            o = _orb(st, RX + 0.17, yy, i + 1, t - 0.1, r=0.17)
            tx = st.text(txt, RX + 0.52, yy, 0.25, P.TEXT, 0.6, align="l", kind="bold")
            st.fade_in(tx, t - 0.1, 0.4)
            if prev is not None:
                st.recolor(prev, t - 0.1, t + 0.3, P.MUTED)
            prev = tx
        sub = st.text("annulus: the gap between pipe and casing", RX + 0.52, 2.05 - 0.72 - 0.34, 0.16, P.MUTED, 0.6, align="l")
        st.fade_in(sub, t_an + 0.2, 0.4)
        st.recolor(prev, t_sb - 0.1, t_sb + 0.3, P.MUTED)
        no = st.text("not onto the seabed", RX + 0.52, -0.95, 0.25, P.MUTED, 0.6, align="l", kind="bold")
        nx = _x_mark(st, RX + 0.17, -0.95, 0.12, t_sb, z=0.7, width=0.05)
        st.fade_in(no, t_sb - 0.1, 0.4)
        strike = st.line([(RX + 0.48, -0.95), (RX + 0.52 + st.measure("not onto the seabed", 0.25, "bold") + 0.05, -0.95)], P.BAD, 0.035, 0.62)
        st.draw_on(strike, t_sb + 0.3, t_sb + 0.8)
        foot = st.text(wrap_to("The riser is open to the air at the rig: it brings the mud back, it does not hold pressure.", 0.16, 5.2),
                       RX, -2.25, 0.16, P.MUTED, 0.6, align="l")
        st.fade_in(foot, t_sb + 1.0, 0.5)


# ====================================================================================================== 3.02 THE BOP CLOSING ANIMATION
CX2, Y02 = -3.45, -2.95


def beat_bop(st, tl):
    b = tl["3.02"]
    s = b.sent
    t_ann = _w(b, 1, "squeezes")
    t_pr = _w(b, 2, "close")
    t_bsr = _w(b, 3, "blind shear")
    t_cut = _w(b, 3, "cut through")
    t_tj = _w(b, 3, "thick joints")
    t_seal = _w(b, 3, "seal the hole")
    t_acc = s[4]
    t_pow = _w(b, 4, "loses power")
    t_fast = _w(b, 4, "close fast")
    with st.span(b.start, b.end):
        view = View(st, b.start, b.end, z=0.2)
        with view:
            stk = Stack(st, CX2, Y02, S=1.0, z=0.3, pipe=(-4.6, 3.9), joint=1.8)
            # wellhead below, riser above (stubs)
            st.rect(CX2, Y02 - 0.3, 1.5, 0.75, P.STEEL_DK, 0.25)
            st.rect(CX2, Y02 - 0.3, stk.BR, 0.75, P.BG, 0.26)
            st.rect(CX2, Y02 - 1.2, 1.1, 1.2, P.STEEL, 0.24)
            st.rect(CX2, Y02 - 1.2, stk.BR, 1.2, P.BG, 0.245)
            ry0 = stk.y_top
            riser = [st.rect(CX2, (ry0 + 4.3) / 2, 1.1, 4.3 - ry0, P.STEEL, 0.24), st.rect(CX2, (ry0 + 4.3) / 2, 0.86, 4.3 - ry0, P.BG, 0.245)]
            # build the stack bottom-up on "stack of valves"
            t_b0 = _w(b, 0, "stack") - 0.4
            groups = [stk.body, ]
            st.fade_in(riser + stk.body, b.start + 0.2, 0.6)
            st.fade_in([o for o in stk.all if o not in stk.body], b.start + 0.5, 0.6)
            # 1: the annular squeezes its rubber around the pipe
            stk.close_annular(t_ann - 0.1, t_ann + 1.5)
            st.ripple(CX2, stk.y["ann"] + 0.14, t_ann + 1.2, t_ann + 2.4, P.TEXT, period=0.6, r0=0.2, r1=0.9, width=0.03, z=0.9)
            # 2: pipe rams slide in and grip
            stk.close_rams(t_pr - 0.1, t_pr + 0.8)
            st.ripple(CX2, stk.y_pr, t_pr + 0.7, t_pr + 1.8, P.TEXT, period=0.6, r0=0.2, r1=0.9, width=0.03, z=0.9)
            # 3: blind shear rams cut the pipe body; upper string picked up; the bore is sealed
            stk.shear(t_cut - 0.2, t_cut + 0.9, lift=0.55, t_lift=t_cut + 1.2)
            seal = st.rect(CX2, stk.y["bsr"], stk.BR + 0.06, 0.05, P.SAFE, 0.5, role="shaft")
            st.fade_in(seal, t_seal, 0.4)
            # well pressure held below the closed shear rams
            arrs = []
            for dx_ in (-0.2, 0.2):
                arrs += st.arrow(CX2 + dx_, stk.y["bsr"] - 1.05, CX2 + dx_, stk.y["bsr"] - 0.3, P.TEXT, 0.05, 0.16, 0.55)
            st.fade_in(arrs, t_seal + 0.3, 0.4)
            # the tool joint: too thick to shear
            tj_ring = st.ring(CX2, 1.8 + 0.55, 0.42, 0.04, P.WARN, 0.6)
            st.fade_in(tj_ring, t_tj - 0.2, 0.3)
            st.fade_out(tj_ring, t_tj + 2.2, 0.4)
        # ---- labels (screen space, follow the stack)
        lx = CX2 + stk.half + 0.32
        specs = [("ann", 1, "annular preventer", "rubber squeezes around\nanything in the hole", t_ann - 0.3),
                 ("pr", 2, "pipe rams", "steel blocks close\naround the drill pipe", t_pr - 0.3),
                 ("bsr", 3, "blind shear rams", "cut the pipe body,\nseal the empty bore", t_bsr - 0.2),
                 ("con", None, "wellhead connector", "", None)]
        t_list = _w(b, 0, "each with a job") - 0.2
        labs = {}
        for key, n, name, sub, t_on in specs:
            yy = stk.y_pr if key == "pr" else stk.y[key]
            objs = []
            if n:
                plate = st.circle(lx + 0.2, yy + 0.16, 0.17, P.GRID, 0.6)
                num = st.text(str(n), lx + 0.2, yy + 0.155, 0.15, P.TEXT, 0.61, kind="bold")
                objs += [plate, num]
            ttl = st.text(name, lx + (0.5 if n else 0.0), yy + 0.16, 0.25, P.MUTED, 0.6, align="l", kind="bold")
            objs.append(ttl)
            st.fade_in(objs, t_list + (0 if n else 0.3) + 0.15 * (n or 3), 0.4)
            view.follow(objs, lx, yy)
            if t_on is not None:
                st.recolor(ttl, t_on, t_on + 0.3, P.TEXT)
                st.recolor(plate, t_on, t_on + 0.3, P.MUD)
                st.recolor(num, t_on, t_on + 0.3, P.BG)
                sb = st.text(sub, lx + 0.5, yy - 0.3, 0.17, P.MUTED, 0.6, align="l", valign="t")
                st.fade_in(sb, t_on + 0.3, 0.4)
                view.follow(sb, lx, yy)
                objs.append(sb)
            labs[key] = objs
        # pipe body vs tool joint
        pj = pill(st, CX2 + 0.75, 2.35, "tool joint: too thick to cut", P.PANEL2, P.WARN, 0.18, 0.6, align="l")
        st.fade_in(pj, t_tj - 0.1, 0.4)
        st.fade_out(pj, t_acc - 0.5, 0.4)
        view.follow(pj, CX2 + 0.75, 2.35)
        sealp = pill(st, CX2 - stk.half - 0.15, stk.y["bsr"], "sealed", P.PANEL2, P.SAFE, 0.2, 0.6, align="r")
        st.fade_in(sealp, t_seal + 0.2, 0.4)
        view.follow(sealp, CX2 - stk.half - 0.15, stk.y["bsr"])
        held = pill(st, CX2 - stk.half - 0.15, stk.y["pr1"] - 0.05, "pipe hung\noff below", P.PANEL2, P.MUTED, 0.16, 0.6, align="r")
        st.fade_in(held, t_seal + 0.8, 0.4)
        view.follow(held, CX2 - stk.half - 0.15, stk.y["pr1"] - 0.05)
        # ---- camera: a gentle push-in that follows the action, then back out
        view.camera(s[1] - 0.2, s[1] + 1.3, focus=(CX2, stk.y["ann"]), scale=1.2)
        view.camera(s[2] - 0.3, s[2] + 0.7, focus=(CX2, stk.y_pr), scale=1.2)
        view.camera(t_bsr - 0.4, t_bsr + 0.8, focus=(CX2, stk.y["bsr"]), scale=1.28)
        view.home(b.sent_end[3] - 0.6, t_acc + 0.6)
        view.finish()
        allabs = [o for v in labs.values() for o in v]
        st.fade_out(allabs + held, t_acc - 0.2, 0.4)
        # ---- accumulator: nitrogen pre-charge pushes hydraulic fluid to the stack, no rig power needed
        _accumulator(st, b, stk, t_acc, t_pow, t_fast)


def _accumulator(st, b, stk, t_acc, t_pow, t_fast):
    ax, ay, aw, ah = 2.3, -1.1, 1.5, 2.9
    top, bot = ay + ah / 2, ay - ah / 2
    shell = st.rect(ax, ay, aw, ah, P.STEEL_DK, 0.5)
    inner = st.rect(ax, ay, aw - 0.16, ah - 0.16, P.BG, 0.51)
    caps = [st.ellipse(ax, top, aw / 2, 0.22, P.STEEL_DK, 0.49, role="solid"), st.ellipse(ax, bot, aw / 2, 0.22, P.STEEL_DK, 0.49, role="solid")]
    y_sep0 = ay - 0.1
    gas = st.rect(ax, top - 0.08, aw - 0.16, top - 0.08 - y_sep0, N2, 0.52, anchor="t", alpha=0.55, role="flat")
    liq = st.rect(ax, bot + 0.08, aw - 0.16, y_sep0 - bot - 0.08, HYD, 0.52, anchor="b", role="flat")
    sep = st.rect(ax, y_sep0, aw - 0.16, 0.05, P.TEXT, 0.53, role="solid")
    gl = st.text("nitrogen", ax, ay + 0.8, 0.17, P.BG, 0.55, kind="bold")
    ll = st.text("hydraulic\nfluid", ax, ay - 0.8, 0.17, P.BG, 0.55, kind="bold")
    # pre-charge gauge beside the top of the bottle
    gx, gy = ax + 1.55, top - 0.55
    dial = _dial(st, gx, gy, 0.5, 0.5)
    nd, hub = _needle(st, gx, gy, 0.42, 40, P.TEXT, 0.52, 0.045)
    gtl = st.text("N₂ pre-charge", gx, gy - 0.27, 0.16, P.MUTED, 0.52)
    stem = st.rect((ax + aw / 2 + gx - 0.5) / 2, gy + 0.05, gx - 0.5 - ax - aw / 2, 0.04, P.STEEL_DK, 0.48)
    title = st.text("ACCUMULATOR", ax - 0.75, top + 1.0, 0.24, P.TEXT, 0.55, align="l", kind="bold")
    tsub = st.text("a gas-charged bottle of stored hydraulic energy", ax - 0.75, top + 0.62, 0.17, P.MUTED, 0.55, align="l")
    parts = [shell, inner, *caps, gas, liq, sep, gl, ll, *dial, nd, hub, gtl, stem, title, tsub]
    st.fade_in(parts, t_acc, 0.5)
    # control line to the stack bonnets (screen = world: the view is home by now)
    xs = stk.cx + stk.half - 0.05
    yl = stk.y["pr1"]
    line_pts = [(ax - aw / 2 + 0.05, bot + 0.35), (ax - 1.25, bot + 0.35), (ax - 1.25, yl), (xs, yl)]
    cl = st.line(line_pts, HYD, 0.06, 0.45, role="solid")
    st.draw_on(cl, t_acc + 0.4, t_acc + 1.4, "BEZIER")
    # rig power: the pumps that recharge the bottle
    px, py = 6.2, 0.2
    pw_pl = pill(st, px, py, "rig power", P.PANEL2, P.SAFE, 0.21, 0.55)
    pdot = st.circle(px - 0.75, py, 0.07, P.SAFE, 0.57)
    st.fade_in(pw_pl + [pdot], t_acc + 0.5, 0.4)
    rch = [(px + 0.85, py - 0.25), (px + 0.85, ay - 1.3), (ax + aw / 2 + 0.05, ay - 1.3)]
    rl = st.line(rch, P.STEEL_DK, 0.05, 0.47)
    st.fade_in(rl, t_acc + 0.5, 0.4)
    # the rig's pumps charge the bottle: fluid in, nitrogen squeezed, gauge up
    t_ch0, t_ch1 = t_acc + 0.9, _w(b, 4, "store") + 2.2
    st.flow(rch, t_acc + 0.7, t_pow, HYD, n=6, speed=0.9, r=0.035, z=0.6)
    up = 0.35
    st.move(sep, t_ch0, t_ch1, dy=up)
    st.scale_to(gas, t_ch0, t_ch1, sy=top - 0.08 - (y_sep0 + up))
    st.scale_to(liq, t_ch0, t_ch1, sy=y_sep0 + up - bot - 0.08)
    st.move(gl, t_ch0, t_ch1, dy=up / 2)
    st.move(ll, t_ch0, t_ch1, dy=up / 2)
    st.rotate(nd, t_ch0, t_ch1, 22)
    # the gas expands and pushes the fluid out, fast, into the stack ...
    t_go = t_fast - 0.15
    dy = -0.95
    st.move(sep, t_go, t_go + 1.5, dy=dy)
    st.scale_to(gas, t_go, t_go + 1.5, sy=top - 0.08 - (y_sep0 + up + dy))
    st.scale_to(liq, t_go, t_go + 1.5, sy=y_sep0 + up + dy - bot - 0.08)
    st.move(gl, t_go, t_go + 1.5, dy=dy / 2)
    st.move(ll, t_go, t_go + 1.5, dy=dy / 2)
    st.rotate(nd, t_go, t_go + 1.5, 70)
    st.flow(line_pts, t_go, b.end, HYD, n=18, speed=2.6, r=0.04, z=0.62)
    st.ripple(stk.cx, stk.y_pr, t_go + 0.6, b.end, HYD, period=0.9, r0=0.3, r1=1.5, width=0.03, z=0.62)
    # ... and keeps doing it with the rig's power gone
    st.recolor([pw_pl[1], pdot], t_pow, t_pow + 0.3, P.BAD)
    xo = _x_mark(st, px - 0.75, py, 0.13, t_pow + 0.1, z=0.7, width=0.05)
    lost = st.text("power lost", px, py - 0.5, 0.19, P.BAD, 0.6, kind="bold")
    st.fade_in(lost, t_pow + 0.3, 0.3)
    fast = pill(st, ax - 0.75, bot - 0.6, "the preventers still close, fast", P.PANEL2, P.TEXT, 0.21, 0.6, align="l")
    st.fade_in(fast, t_pow + 0.2, 0.4)


# ====================================================================================================== 3.03 why the closed loop matters
def beat_closed_loop(st, tl):
    b = tl["3.03"]
    s = b.sent
    with st.span(b.start, b.end):
        # left column: the three reasons
        hd = st.text("WHY THE CLOSED LOOP MATTERS", -6.05, 1.4, 0.17, P.MUTED, 0.5, align="l", kind="bold")
        st.fade_in(hd, s[0], 0.4)
        chips = []
        names = ["a real, weighted mud", "flow in vs flow out", "shut in at the seabed"]
        for i, nm in enumerate(names):
            y = 0.7 - i * 0.95
            card = st.rect(-4.45, y, 3.3, 0.72, P.PANEL2, 0.4)
            orb = st.circle(-5.75, y, 0.18, P.GRID, 0.45)
            num = st.text(str(i + 1), -5.75, y - 0.005, 0.15, P.TEXT, 0.46, kind="bold")
            tx = st.text(nm, -5.42, y, 0.21, P.MUTED, 0.46, align="l", kind="bold")
            st.fade_in([card, orb, num, tx], s[1] + 0.15 * i, 0.4)
            t_on = s[2 + i]
            st.recolor(orb, t_on - 0.2, t_on + 0.2, P.MUD)
            st.recolor(num, t_on - 0.2, t_on + 0.2, P.BG)
            st.recolor(tx, t_on - 0.2, t_on + 0.2, P.TEXT)
            if i < 2:
                st.recolor(tx, s[3 + i] - 0.2, s[3 + i] + 0.2, P.MUTED)
                st.recolor(orb, s[3 + i] - 0.2, s[3 + i] + 0.2, P.SAFE)
            chips += [card, orb, num, tx]
        st.fade_out(chips + [hd], s[5] - 0.3, 0.5)
        _reason_mud(st, b, s[2], s[3] - 0.35)
        _reason_flow(st, b, s[3], s[4] - 0.35)
        _reason_shut(st, b, s[4], s[5] - 0.35)
        _shield(st, b, s[5])


def _reason_mud(st, b, t0, t1):
    with st.span(t0 - 0.1, t1 + 0.4):
        objs = []
        ttl = []
        # mud-weight dial, 1.00 - 1.20 sg
        dx, dy, r = 0.3, -0.75, 1.75
        ang = lambda sg: 180.0 - (sg - 1.0) / 0.2 * 180.0
        face = _dial(st, dx, dy, r, 0.4)
        ticks = []
        for v in (1.0, 1.05, 1.10, 1.15, 1.20):
            a = math.radians(ang(v))
            ticks.append(st.line([(dx + (r - 0.18) * math.cos(a), dy + (r - 0.18) * math.sin(a)), (dx + r * math.cos(a), dy + r * math.sin(a))],
                                 P.MUTED, 0.03, 0.45, role="hair"))
            ticks.append(st.text(f"{v:.2f}", dx + (r + 0.3) * math.cos(a), dy + (r + 0.22) * math.sin(a), 0.16, P.MUTED, 0.45))
        nd, hub = _needle(st, dx, dy, r - 0.25, ang(M.pp(M.WATER_DEPTH)), P.MUD, 0.5, 0.07)
        cap = st.text("mud weight", dx, dy - 0.45, 0.19, P.MUTED, 0.5)
        st.fade_in(face + ticks + [nd, hub, cap], t0 + 0.2, 0.5)
        sw = st.text("from seawater to a weighted mud", dx, dy - 1.45, 0.17, P.MUTED, 0.5)
        st.fade_in(sw, _w(b, 2, "weighted") - 0.2, 0.4)
        t_w = _w(b, 2, "weighted")
        st.rotate(nd, t_w - 0.2, t_w + 1.4, ang(MW_NEXT))
        st.counter(dx, dy - 0.95, t_w - 0.2, t_w + 1.4, M.pp(M.WATER_DEPTH), MW_NEXT, fmt="{:.2f} sg", size=0.36, color=P.MUD, hold=t1 + 0.4)
        # pressure at the bottom of the next section vs pore pressure there
        z = SHOE_13
        p_sw, p_mw = M.bar(z, M.pp(M.WATER_DEPTH)), M.bar(z, MW_NEXT)
        p_pore = M.bar(z, max(M.pp(zz) for zz in range(int(SHOE_20), int(SHOE_13) + 1, 10)))
        bx, by0, by1 = 4.7, -2.7, 1.25
        lo, hi = 180.0, 240.0
        Y = lambda p: by0 + (p - lo) / (hi - lo) * (by1 - by0)
        frame = st.rect(bx, (by0 + by1) / 2, 0.8, by1 - by0, P.PANEL2, 0.4, role="flat")
        bar = st.rect(bx, by0, 0.56, Y(p_sw) - by0, P.MUD, 0.45, anchor="b")
        pore = st.rect(bx, Y(p_pore), 1.1, 0.05, P.PORE, 0.5, role="shaft")
        pl = st.text(f"pore pressure\n{p_pore:.0f} bar", bx + 0.7, Y(p_pore), 0.17, P.PORE, 0.5, align="l", kind="bold")
        cap2 = st.text(f"pressure at {z:,.0f} m", bx, by1 + 0.32, 0.19, P.MUTED, 0.5)
        brk = st.text("≈", bx, by0 - 0.22, 0.2, P.MUTED, 0.5)
        st.fade_in([frame, bar, pore, pl, cap2, brk], t0 + 0.6, 0.5)
        st.scale_to(bar, t_w - 0.2, t_w + 1.4, sy=Y(p_mw) - by0)
        st.counter(bx - 0.5, Y(p_mw) + 0.0, t_w - 0.2, t_w + 1.4, p_sw, p_mw, fmt="{:.0f} bar", size=0.2, color=P.MUD, align="r", hold=t1 + 0.4)
        t_c = _w(b, 2, "control pressure")
        ok = pill(st, bx + 0.55, Y(p_mw) + 0.1, "above pore pressure", P.PANEL2, P.SAFE, 0.16, 0.55, align="l")
        st.fade_in(ok, t_c - 0.2, 0.4)
        objs += ttl + face + ticks + [nd, hub, cap, sw, frame, bar, pore, pl, cap2, brk] + ok
        st.fade_out(objs, t1, 0.4)


def _reason_flow(st, b, t0, t1):
    with st.span(t0 - 0.1, t1 + 0.4):
        ttl = []
        t_back = _w(b, 3, "coming back")
        t_tank = _w(b, 3, "tank level")
        t_warn = _w(b, 3, "earliest warning")
        x0, x1 = -1.9, 2.3
        rows = []
        bars = {}
        for i, (nm, y) in enumerate((("flow in (pumps)", 1.25), ("flow out (returns)", 0.0))):
            lab = st.text(nm, x0, y + 0.42, 0.19, P.TEXT, 0.5, align="l", kind="bold")
            tube = st.rect((x0 + x1) / 2, y, x1 - x0, 0.32, P.PANEL2, 0.4, role="flat")
            gauge = st.rect(x1 + 1.35, y, 2.2, 0.32, P.PANEL2, 0.4, role="flat")
            g0 = x1 + 0.35
            fill = st.rect(g0, y, 1.5, 0.2, P.MUD, 0.45, anchor="l", role="flat")
            st.fade_in([lab, tube, gauge, fill], t0 + 0.2 + 0.2 * i, 0.4)
            pts = [(x0 + 0.1, y), (x1 - 0.1, y)] if i == 0 else [(x1 - 0.1, y), (x0 + 0.1, y)]
            st.flow(pts, t0 + 0.4, t1 + 0.4, P.MUD, n=14, speed=1.3, r=0.05, z=0.5)
            bars[i] = fill
            rows += [lab, tube, gauge, fill]
        # flow out creeps up: a few per cent more than goes in
        st.scale_to(bars[1], t_back + 0.4, t_back + 2.4, sx=1.7)
        rate = st.text("rate", x1 + 1.35, 1.25 + 0.42, 0.16, P.MUTED, 0.5)
        st.fade_in(rate, t0 + 0.4, 0.4)
        rows.append(rate)
        st.flow([(x1 - 0.1, 0.0), (x0 + 0.1, 0.0)], t_back + 1.0, t1 + 0.4, P.MUD, n=4, speed=1.6, r=0.05, z=0.5)
        # difference needle (centre zero)
        dx, dy, r = 6.55, 0.25, 0.8
        face = _dial(st, dx, dy, r, 0.4)
        zero = st.rect(dx, dy + r - 0.1, 0.03, 0.2, P.MUTED, 0.45)
        nd, hub = _needle(st, dx, dy, r - 0.12, 90, P.TEXT, 0.5, 0.05)
        dl = st.text("out − in", dx, dy - 0.3, 0.18, P.MUTED, 0.5)
        st.fade_in(face + [zero, nd, hub, dl], t0 + 0.6, 0.4)
        st.rotate(nd, t_back + 0.4, t_back + 2.4, 38)
        # tank level rises
        tx, ty, tw, th = 0.4, -2.3, 3.0, 1.15
        tank = st.rect(tx, ty, tw, th, P.STEEL_DK, 0.4)
        tin = st.rect(tx, ty, tw - 0.14, th - 0.14, P.BG, 0.41)
        lvl = st.rect(tx, ty - th / 2 + 0.07, tw - 0.14, 0.42, P.MUD, 0.42, anchor="b", alpha=0.85)
        mark = st.rect(tx, ty - th / 2 + 0.07 + 0.42, tw + 0.3, 0.025, P.MUTED, 0.43, role="hair")
        tl_ = st.text("tank level", tx - tw / 2 - 0.15, ty, 0.19, P.TEXT, 0.45, align="r", kind="bold")
        st.fade_in([tank, tin, lvl, mark, tl_], t_tank - 0.6, 0.4)
        st.scale_to(lvl, t_tank, t_tank + 2.0, sy=0.78)
        up = st.arrow(tx + tw / 2 + 0.3, ty - 0.2, tx + tw / 2 + 0.3, ty + 0.35, P.TEXT, 0.05, 0.16, 0.45)
        st.fade_in(up, t_tank + 0.4, 0.3)
        warn = pill(st, 5.6, -2.35, "possible kick:\nstop and flow-check", P.PANEL2, P.BAD, 0.21, 0.55)
        st.fade_in(warn, t_warn - 0.1, 0.4)
        st.ripple(5.6, -2.35, t_warn, t1, P.BAD, period=1.0, r0=0.5, r1=1.4, width=0.03, z=0.5)
        st.fade_out(ttl + rows + face + [zero, nd, hub, dl, tank, tin, lvl, mark, tl_] + up + warn, t1, 0.4)


def _reason_shut(st, b, t0, t1):
    t_kick = _w(b, 4, "goes wrong")
    t_shut = _w(b, 4, "shut the well")
    t_circ = _w(b, 4, "circulate")
    t_choke = _w(b, 4, "through the choke")
    t_adj = _w(b, 4, "adjustable")
    t_line = _w(b, 4, "a line back")
    t_nr = _w(b, 4, "not up the riser")
    with st.span(t0 - 0.1, t1 + 0.4):
        ttl = []
        cx, SBy, S = 0.2, -1.35, 0.46
        sea = st.rect(cx + 1.0, (SBy + 1.85) / 2, 7.4, 1.85 - SBy, P.SEA, 0.3, alpha=0.85)
        rock = st.rect(cx + 1.0, (SBy - 3.55) / 2, 7.4, SBy + 3.55, P.ROCK2, 0.3)
        deck = st.rect(cx + 1.2, 1.95, 4.2, 0.16, P.STEEL_DK, 0.45)
        stk = Stack(st, cx, SBy + 0.05, S=S, z=0.5, outlet=True)
        riser = [st.rect(cx, (stk.y_top + 1.9) / 2, 0.42, 1.9 - stk.y_top, P.STEEL, 0.46), st.rect(cx, (stk.y_top + 1.9) / 2, 0.32, 1.9 - stk.y_top, P.BG, 0.465)]
        hole = [st.rect(cx, (SBy - 3.4) / 2, 0.5, SBy + 3.4, P.BG, 0.35), st.rect(cx, (SBy - 3.4) / 2, 0.32, SBy + 3.4, P.MUD, 0.36, alpha=0.3)]
        dp = st.rect(cx, (2.25 - 3.2) / 2, 0.1, 2.25 + 3.2, P.STEEL, 0.6)
        whd = st.rect(cx, SBy + 0.02, 0.6, 0.2, P.STEEL, 0.48)
        xo = stk.cx + stk.BW / 2 + 0.5 * S
        cl_pts = [(xo, stk.y_outlet), (cx + 1.7, stk.y_outlet), (cx + 1.7, 2.3), (cx + 2.35, 2.3)]
        cline = st.line(cl_pts, P.STEEL_DK, 0.07, 0.44)
        vx, vy = cx + 2.7, 2.3
        valve = [st.poly([(vx - 0.34, vy + 0.22), (vx, vy), (vx - 0.34, vy - 0.22)], P.STEEL, 0.5),
                 st.poly([(vx + 0.34, vy + 0.22), (vx, vy), (vx + 0.34, vy - 0.22)], P.STEEL, 0.5)]
        adj = st.arrow(vx - 0.36, vy - 0.32, vx + 0.38, vy + 0.36, P.TEXT, 0.04, 0.14, 0.52)
        out = st.line([(vx + 0.34, vy), (vx + 1.0, vy)], P.STEEL_DK, 0.07, 0.44)
        scene = [sea, rock, deck] + stk.all + riser + hole + [dp, whd, cline] + valve + adj + [out]
        st.fade_in(scene, t0 + 0.1, 0.5)
        sbl = st.text("seabed", cx - 2.4, SBy + 0.15, 0.16, P.MUTED, 0.5, align="l")
        rgl = st.text("rig", cx - 1.25, 2.2, 0.18, P.MUTED, 0.5, align="l", kind="bold")
        st.fade_in([sbl, rgl], t0 + 0.4, 0.4)
        # normal circulation, then the kick
        st.flow([(cx, 2.2), (cx, -3.15)], t0 + 0.3, t_shut + 0.4, P.MUD, n=16, speed=1.1, r=0.03, z=0.7)
        for sd in (-1, 1):
            st.flow([(cx + sd * 0.11, -3.2), (cx + sd * 0.11, 1.85)], t0 + 0.3, t_shut + 0.3, P.MUD, n=16, speed=1.1, r=0.03, z=0.7)
        for sd in (-1, 1):
            st.flow([(cx + sd * 0.11, -3.3), (cx + sd * 0.11, stk.y["pr2"] - 0.25)], t_kick, t_shut + 0.6, P.GAS, n=6, speed=0.9, r=0.045, z=0.71)
        kl = pill(st, cx - 0.5, -2.8, "kick (gas)", P.PANEL2, P.GAS, 0.18, 0.6, align="r")
        st.fade_in(kl, t_kick + 0.2, 0.3)
        st.ripple(cx, -3.0, t_kick, t_kick + 1.6, P.BAD, period=0.8, r0=0.2, r1=0.9, width=0.03, z=0.6)
        # shut in at the seabed
        stk.close_rams(t_shut - 0.1, t_shut + 0.6, keys=("pr2",))
        st.ripple(cx, stk.y["pr2"], t_shut + 0.5, t_shut + 1.6, P.TEXT, period=0.6, r0=0.15, r1=0.8, width=0.03, z=0.7)
        sh = pill(st, cx + 1.95, stk.y["pr2"] + 0.12, "shut in at the seabed", P.PANEL2, P.TEXT, 0.18, 0.6, align="l")
        st.fade_in(sh, t_shut + 0.4, 0.3)
        # circulate the kick out through the choke line
        st.flow([(cx, 2.2), (cx, -3.15)], t_circ, t1 + 0.4, P.MUD, n=16, speed=0.8, r=0.03, z=0.7)
        st.flow([(cx + 0.11, -3.2), (cx + 0.11, stk.y_outlet - 0.05), (xo, stk.y_outlet)], t_circ, t1 + 0.4, P.MUD, n=12, speed=0.8, r=0.03, z=0.7)
        st.flow([(cx - 0.11, -3.2), (cx - 0.11, stk.y_outlet - 0.05), (cx + 0.11, stk.y_outlet - 0.02), (xo, stk.y_outlet)], t_circ + 0.3, t1 + 0.4, P.GAS, n=8, speed=0.8, r=0.04, z=0.71)
        st.flow(cl_pts + [(vx + 0.85, vy)], t_circ + 0.4, t1 + 0.4, P.GAS, n=12, speed=1.0, r=0.04, z=0.71)
        cglow = st.line(cl_pts, P.WARN, 0.03, 0.445)
        st.draw_on(cglow, t_line - 0.1, t_line + 1.2, "BEZIER")
        cll = st.text("choke line", cx + 1.85, 0.6, 0.17, P.MUTED, 0.5, align="l", kind="bold")
        st.fade_in(cll, t_line, 0.4)
        vl = pill(st, vx + 0.2, vy - 0.62, "choke: adjustable valve", P.PANEL2, P.WARN, 0.18, 0.6, align="l")
        st.fade_in(vl, t_choke - 0.1, 0.3)
        st.rotate(adj, t_adj, t_adj + 0.7, 20)
        st.rotate(adj, t_adj + 0.7, t_adj + 1.4, -10)
        st.ripple(vx, vy, t_choke, t_choke + 1.5, P.WARN, period=0.7, r0=0.15, r1=0.6, width=0.03, z=0.6)
        # not up the riser
        xm = _x_mark(st, cx, 1.25, 0.22, t_nr, z=0.75, width=0.06)
        nr = pill(st, cx - 0.45, 1.25, "not up the riser", P.PANEL2, P.BAD, 0.18, 0.6, align="r")
        st.fade_in(nr, t_nr + 0.1, 0.3)
        st.fade_out(ttl + scene + [sbl, rgl] + kl + sh + [cglow, cll] + vl + xm + nr, t1, 0.4)


def _shield(st, b, t0):
    t_two = _w(b, 5, "two barriers")
    t_def = _w(b, 5, "things that can")
    t_mud = _w(b, 5, "the mud")
    t_steel = _w(b, 5, "steel")
    cx, cy = 0.9, -3.45
    sea = st.rect(cx, 1.55, 11.6, 1.5, P.SEA, 0.1)
    rock = st.rect(cx, (cy + 0.8) / 2, 11.6, 0.8 - cy, P.ROCK, 0.1)
    res = st.poly(_arc_pts(cx, cy, 1.25, 0, 180), P.SAND, 0.2)
    r1a, r1b, r2a, r2b = 1.6, 2.25, 2.6, 3.4
    inner = st.poly(_arc_pts(cx, cy, r1b, 0, 180) + list(reversed(_arc_pts(cx, cy, r1a, 0, 180))), P.MUD, 0.21, alpha=0.75)
    outer = st.poly(_arc_pts(cx, cy, r2b, 0, 180) + list(reversed(_arc_pts(cx, cy, r2a, 0, 180))), P.CEMENT, 0.21, alpha=0.8)
    ol1 = st.line(_arc_pts(cx, cy, r1b + 0.03, 0, 180), P.PRIMARY_B, 0.05, 0.25)
    ol2 = st.line(_arc_pts(cx, cy, r2b + 0.03, 0, 180), P.SECOND_B, 0.05, 0.25)
    sl = st.text("sea", cx, 1.55, 0.26, P.TEXT, 0.3, kind="bold")
    rl = st.text("reservoir", cx, cy + 0.55, 0.22, P.BG, 0.3, kind="bold")
    st.fade_in([sea, rock, res, sl, rl], t0 - 0.1, 0.5)
    st.fade_in(outer, t_two - 0.1, 0.5)
    st.fade_in(inner, t_two + 0.3, 0.5)
    st.draw_on(ol2, t_steel - 0.2, t_steel + 1.0, "BEZIER")
    st.draw_on(ol1, t_mud - 0.2, t_mud + 0.9, "BEZIER")
    # reservoir pressure pushes outward, stopped at the first barrier
    arrs = []
    for a in (35, 70, 110, 145):
        ra = math.radians(a)
        arrs += st.arrow(cx + 1.3 * math.cos(ra), cy + 1.3 * math.sin(ra), cx + 1.57 * math.cos(ra), cy + 1.57 * math.sin(ra), P.PORE, 0.05, 0.14, 0.3)
    st.fade_in(arrs, t_two + 0.6, 0.4)
    l1 = pill(st, cx, cy + (r1a + r1b) / 2, "1   mud", P.PANEL2, P.MUD, 0.22, 0.4)
    l2 = pill(st, cx, cy + (r2a + r2b) / 2, "2   steel · cement · BOP", P.PANEL2, P.TEXT, 0.22, 0.4)
    st.fade_in(l1, t_mud - 0.1, 0.4)
    st.fade_in(l2, t_steel - 0.1, 0.4)
    dfn = pill(st, -5.9, 2.6, "barrier: anything that can stop flow on its own", P.PANEL2, P.TEXT, 0.2, 0.4, align="l")
    st.fade_in(dfn, t_def - 0.1, 0.4)


# ====================================================================================================== 3.04 tested before trusted
def beat_test(st, tl):
    b = tl["3.04"]
    s = b.sent
    t_rock = _w(b, 2, "the rock")
    with st.span(b.start, b.end):
        cx, y0, S = -3.6, -2.25, 0.75
        view = View(st, b.start, b.end, z=0.2)
        with view:
            stk = Stack(st, cx, y0, S=S, z=0.3, pipe=(y0 - 0.32, 4.2))
            ry0 = stk.y_top
            riser = [st.rect(cx, (ry0 + 4.3) / 2, 0.8, 4.3 - ry0, P.STEEL, 0.24), st.rect(cx, (ry0 + 4.3) / 2, 0.62, 4.3 - ry0, P.BG, 0.245)]
            wh = [st.rect(cx, y0 - 0.38, 1.2, 0.8, P.STEEL_DK, 0.25), st.rect(cx, y0 - 0.38, stk.BR, 0.8, P.BG, 0.26),
                  st.rect(cx, y0 - 1.15, 0.9, 0.8, P.STEEL, 0.24), st.rect(cx, y0 - 1.15, stk.BR * 0.9, 0.8, P.BG, 0.245)]
            yp = y0 - 0.45
            plug = [st.rect(cx, yp, stk.BR + 0.04, 0.3, P.STEEL, 0.36),
                    st.rect(cx, yp + 0.1, stk.BR + 0.08, 0.06, RUBBER, 0.37, role="solid")]
            mud = st.rect(cx, (yp + 0.15 + stk.y_top) / 2, stk.BR, stk.y_top - yp - 0.15, P.MUD, 0.33, alpha=0.18)
        st.fade_in(riser + wh + stk.all + plug + [mud], b.start + 0.1, 0.5)
        lx = cx + stk.half + 0.25
        pl = pill(st, lx, yp, "test plug in the wellhead", P.PANEL2, P.MUTED, 0.17, 0.5, align="l")
        lead = st.line([(cx + stk.BR / 2 + 0.06, yp), (lx, yp)], P.TEXT, 0.022, 0.45, alpha=0.7)
        st.fade_in(pl + [lead], b.start + 0.5, 0.4)
        # chart: pressure vs time with a dashed test line
        c = Chart(st, 2.0, -0.85, 5.1, 3.0, (0.0, 1.0), (0.0, 1.0))
        fr = c.frame(xlabel="time", ylabel="pressure", grid=False)
        tline = st.dashed(c.pt(0.0, 0.8), c.pt(1.0, 0.8), P.MUTED, 0.03, 0.14, 0.09, 0.2)
        tll = st.text("test pressure", c.X(1.0), c.Y(0.8) + 0.22, 0.17, P.MUTED, 0.25, align="r")
        st.fade_in(fr + tline + [tll], b.start + 0.3, 0.5)
        # three tests: annular, pipe rams, then the shear rams on an empty bore
        tA = b.start + 0.7
        tests = [("ann", "annular", tA), ("pr2", "pipe rams", tA + 3.6), ("bsr", "blind shear rams", s[2] - 0.1)]
        T0, T1 = tests[0][2], tests[2][2] + 3.2
        X = lambda t: (t - T0) / (T1 - T0)
        segs = []
        for key, nm, t in tests:
            ta, tb, tc, td = t + 0.7, t + 1.4, t + 2.6, t + 3.0     # closed, at pressure, hold done, bled off
            segs.append((t, ta, tb, tc, td))
        trace_keys = [(T0, 0.0)]
        for (t, ta, tb, tc, td) in segs:
            trace_keys += [(ta, 0.0), (tb, 0.8), (tc, 0.79), (td, 0.0)]

        def P_at(tt):
            for (a, pa), (bb, pb) in zip(trace_keys[:-1], trace_keys[1:]):
                if a <= tt <= bb:
                    return pa + (pb - pa) * (tt - a) / max(bb - a, 1e-6)
            return 0.0

        def draw_trace(cv, t, look):
            if t < T0:
                return
            te = min(t, T1)
            pts = []
            n = int(80 * (te - T0) / (T1 - T0)) + 2
            for i in range(n):
                tt = T0 + (te - T0) * i / (n - 1)
                pts.append(c.pt(X(tt), P_at(tt)))
            path = skia.Path()
            path.moveTo(*pts[0])
            for p in pts[1:]:
                path.lineTo(*p)
            rgb = hex_rgb(P.MUD)
            glow = skia.Paint(Color=col(rgb, 0.35), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.15,
                              StrokeJoin=skia.Paint.kRound_Join, StrokeCap=skia.Paint.kRound_Cap,
                              MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 4.0, False))
            cv.drawPath(path, glow)
            cv.drawPath(path, skia.Paint(Color=col(rgb, 1.0), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.06,
                                         StrokeJoin=skia.Paint.kRound_Join, StrokeCap=skia.Paint.kRound_Cap))
            # hold timers: a ring that fills while the pressure is held
            for (t_, ta, tb, tc, td) in segs:
                if tb <= t:
                    f = _clamp((t - tb) / (tc - tb), 0.0, 1.0)
                    a = _clamp((td + 0.6 - t) / 0.4, 0.0, 1.0)
                    if a <= 0:
                        continue
                    hx, hy = c.X(X((tb + tc) / 2)), c.Y(0.8) - 0.6
                    r = 0.2
                    cv.drawCircle(hx, hy, r, skia.Paint(Color=col(hex_rgb(P.GRID), a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.05))
                    arc = skia.Path()
                    arc.addArc(skia.Rect(hx - r, hy - r, hx + r, hy + r), 90, -360 * f)
                    cv.drawPath(arc, skia.Paint(Color=col(hex_rgb(P.SAFE), a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.06,
                                                StrokeCap=skia.Paint.kRound_Cap))
                    look.draw_text(cv, "HOLD", hx, hy - 0.36, 0.13, P.MUTED, a, "c", "bold")
        st.procedural(T0, b.end, 0.4, draw_trace)
        # the elements close / open in turn; the volume below the closed element is pressured
        (t, ta, tb, tc, td) = segs[0]
        stk.close_annular(t, ta)
        stk.open_annular(td + 0.1, td + 0.6)
        (t, ta, tb, tc, td) = segs[1]
        stk.close_rams(t, ta, keys=("pr2",))
        stk.open_rams(td + 0.1, td + 0.5, keys=("pr2",))
        # pull the test string out of the stack before the shear-ram test (the plug stays in the wellhead)
        tp0 = td + 0.2
        st.move(stk.pipe, tp0, min(tp0 + 1.4, segs[2][0] - 0.1), dy=4.6)
        (t, ta, tb, tc, td) = segs[2]
        stk.close_bsr(t, ta)
        for i, (key, nm, _) in enumerate(tests):
            (t, ta, tb, tc, td) = segs[i]
            yk = stk.y[key]
            with view:
                prs = st.rect(cx, (yp + 0.15 + yk) / 2, stk.BR, yk - yp - 0.15, P.MUD, 0.335, alpha=0.6)
            st.fade_in(prs, ta, tb - ta)
            st.fade_out(prs, tc, td - tc)
            ck = _check(st, lx + 0.15, yk + (0.0 if key != "pr2" else -0.18), tc, s=0.15, z=0.6)
            lab = st.text(nm, lx + 0.45, yk + (0.0 if key != "pr2" else -0.18), 0.21, P.TEXT, 0.6, align="l", kind="bold")
            st.fade_in(lab, t - 0.1, 0.3)
            if key == "bsr":
                eb = st.text("on an empty bore: pipe pulled", lx + 0.45, yk - 0.3, 0.16, P.MUTED, 0.6, align="l")
                st.fade_in(eb, t + 0.1, 0.3)
        # the line that matters
        q = st.text("A barrier you have not tested\nis a hope, not a barrier.", 4.2, -2.75, 0.3, P.WARN, 0.5, kind="bold")
        st.fade_in(q, s[1], 0.5)
        st.fade_out(q, s[2] + 1.5, 0.4)
        nxt = pill(st, 4.2, -2.75, "next: test the rock below the 20 in shoe", P.PANEL2, P.TEXT, 0.21, 0.5)
        st.fade_in(nxt, t_rock, 0.4)


# ====================================================================================================== 3.05 leak-off test
def beat_lot(st, tl):
    b = tl["3.05"]
    s = b.sent
    t_drill = _w(b, 0, "drill out")
    t_rock = _w(b, 0, "fresh rock")
    t_test = _w(b, 0, "test it")
    t_r2 = _w(b, 0, "the rock,")
    t_seal = _w(b, 0, "cement seal")
    t_close = _w(b, 1, "close")
    t_pump = _w(b, 1, "pump slowly")
    t_lin = _w(b, 2, "straight line")
    t_sq = _w(b, 2, "squeezing")
    t_bend = _w(b, 2, "line bends")
    t_leak = _w(b, 2, "leak into")
    t_lop = _w(b, 3, "leak-off point")
    t_sr = _w(b, 4, "surface reading")
    t_col = _w(b, 4, "weight of the mud column")
    t_conv = _w(b, 4, "converts")
    t_chk = _w(b, 5, "checks")
    t_cap = _w(b, 5, "caps")
    t_out = t_sr - 0.6                     # the cutaway has done its job: the charts take the frame
    with st.span(b.start, b.end):
        # ================================================================ the shoe cutaway (its own camera)
        view = View(st, b.start, b.end, z=0.2)
        cx = -4.45
        y_csg_top, y_shoe, y_oh = 2.0, -0.3, -1.75
        with view:
            rock = st.rect(cx, (3.9 + -3.62) / 2, 3.8, 3.9 + 3.62, P.ROCK2, 0.0)
            cem = [st.rect(cx + sd * 0.62, (y_csg_top + y_shoe) / 2, 0.3, y_csg_top - y_shoe, P.CEMENT, 0.1) for sd in (-1, 1)]
            csg = [st.rect(cx + sd * 0.42, (y_csg_top + y_shoe) / 2, 0.1, y_csg_top - y_shoe, P.STEEL, 0.15) for sd in (-1, 1)]
            shoe = [st.poly([(cx + sd * 0.37, y_shoe), (cx + sd * 0.56, y_shoe), (cx + sd * 0.37, y_shoe + 0.2)], P.WARN, 0.2) for sd in (-1, 1)]
            bore = st.rect(cx, (y_csg_top + y_shoe) / 2, 0.74, y_csg_top - y_shoe, P.MUD, 0.05, alpha=0.55)
            track = st.rect(cx, y_shoe, 0.74, 0.85, P.CEMENT, 0.12, anchor="b")
            fc = st.rect(cx, y_shoe + 0.85, 0.74, 0.06, P.STEEL_DK, 0.13)
            # depth break above: the casing runs on up to the wellhead
            brk = []
            for dy in (0.0, 0.14):
                brk.append(st.line([(cx - 1.9, y_csg_top + 0.12 + dy), (cx - 0.6, y_csg_top + 0.2 + dy), (cx + 0.6, y_csg_top + 0.04 + dy),
                                    (cx + 1.9, y_csg_top + 0.12 + dy)], P.BG, 0.05, 0.3, role="solid"))
            above = [st.rect(cx + sd * 0.42, (y_csg_top + 0.35 + 3.95) / 2, 0.1, 3.95 - y_csg_top - 0.35, P.STEEL, 0.15) for sd in (-1, 1)]
            above.append(st.rect(cx, (y_csg_top + 0.35 + 3.95) / 2, 0.74, 3.95 - y_csg_top - 0.35, P.MUD, 0.05, alpha=0.55))
            oh = st.rect(cx, y_shoe, 0.6, 0.0001, P.MUD, 0.06, anchor="t", alpha=0.6)
            # drill string
            dp = st.rect(cx, 3.95, 0.18, 3.95 - (y_shoe + 0.95), P.STEEL, 0.3, anchor="t")
            bit = st.poly([(cx - 0.3, y_shoe + 0.95), (cx + 0.3, y_shoe + 0.95), (cx + 0.2, y_shoe + 0.75), (cx - 0.2, y_shoe + 0.75)], P.STEEL_DK, 0.31)
            cut_all = [rock, bore, track, fc, dp, bit, oh] + cem + csg + shoe + brk + above
            st.fade_in(cut_all, b.start + 0.1, 0.5)
            # drill out: through the float collar and the shoe track, then a few metres of new (narrower) hole
            ta, tb = t_drill - 0.2, t_rock - 0.3
            st.scale_to(dp, ta, tb, sy=3.95 - (y_shoe + 0.95) + 1.05, interp="LINEAR")
            st.move(bit, ta, tb, dy=-1.05, interp="LINEAR")
            st.scale_to(track, ta + 0.15, tb, sy=0.0001, interp="LINEAR")
            st.fade_out(fc, ta + 0.1, 0.3)
            tc_ = t_rock + 1.4
            st.scale_to(dp, tb, tc_, sy=3.95 - (y_shoe + 0.95) + 1.05 + (y_shoe - y_oh) - 0.1, interp="LINEAR")
            st.move(bit, tb, tc_, dy=-(y_shoe - y_oh) + 0.1, interp="LINEAR")
            st.scale_to(oh, tb, tc_, sy=y_shoe - y_oh, interp="LINEAR")
            # circulation while drilling: down the pipe, out at the bit, up the annulus (never ahead of the bit)
            st.flow([(cx, 3.9), (cx, y_shoe + 0.8)], ta, tc_, P.MUD, n=10, speed=1.4, r=0.035, z=0.35)
            st.flow([(cx, 3.9), (cx, y_oh + 0.35)], tc_ - 0.2, t_close - 0.6, P.MUD, n=12, speed=1.4, r=0.035, z=0.35)
            for sd in (-1, 1):
                st.flow([(cx + sd * 0.25, y_shoe + 0.8), (cx + sd * 0.25, 3.9)], ta, tc_, P.MUD, n=8, speed=1.4, r=0.035, z=0.35)
                st.flow([(cx + sd * 0.2, y_oh + 0.3), (cx + sd * 0.25, y_shoe), (cx + sd * 0.25, 3.9)], tc_ - 0.2, t_close - 0.6, P.MUD, n=11,
                        speed=1.4, r=0.035, z=0.35)
            # pull back into the casing, close the well, pump slowly
            y_bit_in = y_shoe + 0.6
            st.scale_to(dp, t_close - 0.6, t_close + 0.3, sy=3.95 - (y_bit_in + 0.2))
            st.move(bit, t_close - 0.6, t_close + 0.3, dy=(y_bit_in - 0.2) - (y_oh + 0.1 - 0.2))
            st.flow([(cx, 3.9), (cx, y_bit_in), (cx + 0.12, y_shoe - 0.3), (cx + 0.08, y_oh + 0.15)], t_pump, t_out + 0.5, P.MUD, n=12, speed=0.35, r=0.035, z=0.35)
            # fluid starts to leak into the rock below the shoe
            fy = y_oh + 0.45
            fr_ = []
            for sd in (-1, 1):
                w = st.poly([(cx + sd * 0.3, fy + 0.08), (cx + sd * 1.15, fy + 0.02), (cx + sd * 0.3, fy - 0.06)], P.MUD, 0.08)
                e = st.line([(cx + sd * 0.3, fy + 0.08), (cx + sd * 1.15, fy + 0.02), (cx + sd * 0.3, fy - 0.06)], P.FRAC, 0.03, 0.09)
                st.pop_in(w, t_leak, 0.6)
                st.draw_on(e, t_leak - 0.1, t_leak + 0.6)
                fr_ += [w, e]
                st.flow([(cx + sd * 0.3, fy + 0.01), (cx + sd * 1.05, fy + 0.02)], t_leak + 0.2, t_out + 0.5, P.MUD, n=4, speed=0.4, r=0.03, z=0.1)
        st.fade_out(cut_all + fr_, t_out, 0.6)
        # labels (screen space) for the cutaway
        lx = cx + 0.95
        l_tr = pill(st, lx, y_shoe + 0.5, "shoe-track cement", P.PANEL2, P.CEMENT, 0.17, 0.6, align="l")
        st.fade_in(l_tr, b.start + 0.6, 0.4)
        st.fade_out(l_tr, t_rock - 0.6, 0.4)
        view.follow(l_tr, lx, y_shoe + 0.5)
        l_nr = pill(st, lx, (y_shoe + y_oh) / 2 - 0.1, "a few metres\nof new rock", P.PANEL2, P.TEXT, 0.17, 0.6, align="l")
        st.fade_in(l_nr, t_rock, 0.4)
        st.fade_out(l_nr, t_test + 0.2, 0.3)
        view.follow(l_nr, lx, (y_shoe + y_oh) / 2 - 0.1)
        l_rk = pill(st, lx, y_oh + 0.2, "the rock", P.PANEL2, P.FRAC, 0.19, 0.6, align="l")
        l_cs = pill(st, lx, y_shoe + 0.2, "cement seal at the shoe", P.PANEL2, P.CEMENT, 0.17, 0.6, align="l")
        st.fade_in(l_rk, t_r2 - 0.2, 0.3)
        st.fade_in(l_cs, t_seal - 0.1, 0.3)
        view.follow(l_rk, lx, y_oh + 0.2)
        view.follow(l_cs, lx, y_shoe + 0.2)
        st.fade_out(l_rk + l_cs, t_close - 0.6, 0.3)
        sh = pill(st, lx - 0.1, y_shoe - 0.05, f"{SHOE_20:,.0f} m", P.PANEL2, P.MUTED, 0.16, 0.6, align="l")
        st.fade_in(sh, t_close + 0.2, 0.4)
        st.fade_out(sh, t_out, 0.4)
        view.follow(sh, lx - 0.1, y_shoe - 0.05)
        # camera: close on the shoe during the drill-out, then back
        view.camera(b.start + 0.2, t_drill + 0.6, focus=(cx, y_shoe - 0.3), at=(-1.7, -0.3), scale=1.55)
        view.home(s[1] - 0.8, s[1] + 0.6)
        view.finish()
        # the procedure, step by step as it is spoken (right column while the cutaway is big)
        RX = 3.65
        hd = st.text("THE LEAK-OFF TEST", RX, 2.35, 0.17, P.MUTED, 0.6, align="l", kind="bold")
        st.fade_in(hd, t_drill - 0.3, 0.4)
        steps = [("drill out the shoe track", t_drill - 0.2), ("a few metres of new rock", t_rock - 0.1),
                 ("test the rock + cement seal", t_test - 0.1), ("close the well, pump slowly", t_close - 0.1)]
        rows = [hd]
        prev = None
        for i, (txt, t) in enumerate(steps):
            yy = 1.6 - i * 0.72
            o = _orb(st, RX + 0.17, yy, i + 1, t, color=P.TEXT, r=0.16)
            tx = st.text(txt, RX + 0.48, yy, 0.21, P.TEXT, 0.6, align="l", kind="bold")
            st.fade_in(tx, t, 0.4)
            if prev is not None:
                st.recolor(prev, t, t + 0.3, P.MUTED)
            prev = tx
            rows += o + [tx]
        st.fade_out(rows, s[1] + 0.9, 0.5)
        # the well is closed at the top and pumped slowly
        bop_ic = pill(st, cx, 3.45, "BOP closed", P.PANEL2, P.TEXT, 0.18, 0.6)
        st.fade_in(bop_ic, t_close, 0.3)
        pump = pill(st, cx, 2.85, "pump slowly ↓", P.PANEL2, P.MUD, 0.18, 0.6)
        st.fade_in(pump, t_pump, 0.3)
        st.fade_out(bop_ic + pump, t_out, 0.4)
        # ================================================================ pressure vs volume pumped (its own camera: it moves left later)
        v2 = View(st, b.start, b.end, z=0.3)
        SHIFT = -3.4
        v_lo = 0.62
        k = P_LOT / v_lo

        def curve(v):
            if v <= v_lo:
                return k * v
            u = v - v_lo
            return P_LOT + k * u * 0.25 - k * 0.5 * u * u
        v_end = 0.8
        T_a, T_b = t_lin - 0.3, t_bend + 0.6        # straight line, then the bend
        T_c = t_lop + 0.2                           # pumps stopped just after leak-off
        T_d = T_c + 1.4                             # shut-in: pressure bleeds back a little

        def v_at(t):
            if t <= T_a:
                return 0.0
            if t <= T_b:
                return v_lo * (t - T_a) / (T_b - T_a) * 0.985
            return min(v_end, v_lo * 0.985 + (v_end - v_lo * 0.985) * (t - T_b) / (T_c - T_b))

        def p_shut(t):
            f = _clamp((t - T_c) / (T_d - T_c), 0.0, 1.0)
            return curve(v_end) - 5.0 * (1 - math.exp(-3 * f))
        with v2:
            c = Chart(st, -0.7, -1.75, 3.9, 3.75, (0.0, 1.0), (0.0, 50.0))
            fr = c.frame(yticks=[0, 10, 20, 30, 40, 50], xlabel="volume pumped", ylabel="surface pressure (bar)", grid=True, fy="{:.0f}")

            def draw_pv(cv, t, look):
                v = v_at(t)
                if v <= 0:
                    return
                n = max(2, int(120 * v))
                pts = [c.pt(v * i / (n - 1), curve(v * i / (n - 1))) for i in range(n)]
                if t > T_c:
                    pe = curve(v_end)
                    for j in range(1, 13):
                        tt = T_c + (min(t, T_d) - T_c) * j / 12
                        pts.append(c.pt(v_end + 0.02 * (tt - T_c) / (T_d - T_c), p_shut(tt)))
                path = skia.Path()
                path.moveTo(*pts[0])
                for p in pts[1:]:
                    path.lineTo(*p)
                rgb = hex_rgb(P.MUD)
                cv.drawPath(path, skia.Paint(Color=col(rgb, 0.35), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.16,
                                             StrokeJoin=skia.Paint.kRound_Join, StrokeCap=skia.Paint.kRound_Cap,
                                             MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 4.0, False)))
                cv.drawPath(path, skia.Paint(Color=col(rgb, 1.0), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.065,
                                             StrokeJoin=skia.Paint.kRound_Join, StrokeCap=skia.Paint.kRound_Cap))
                if t < T_c:
                    x, y = pts[-1]
                    cv.drawCircle(x, y, 0.07, skia.Paint(Color=col((1, 0.95, 0.8), 1.0), AntiAlias=True))
                pv = curve(v) if t <= T_c else p_shut(t)
                a = _clamp((T_c + 0.8 - t) / 0.4, 0.0, 1.0)       # the read-out bows out once the leak-off point is marked
                if a > 0:
                    look.draw_text(cv, f"{pv:4.1f} bar", c.X(0.03), c.Y(46.5), 0.24, P.MUD, a, "l", "mono")
                    look.draw_text(cv, "surface gauge", c.X(0.03), c.Y(41.5), 0.14, P.MUTED, a, "l", "sans")
            st.procedural(T_a, b.end, 0.4, draw_pv)
            ext = st.dashed(c.pt(v_lo, P_LOT), c.pt(0.8, k * 0.8), P.MUTED, 0.03, 0.12, 0.08, 0.35)
            lin = st.text("compressing the mud", c.X(0.3) + 0.1, c.Y(k * 0.3) - 0.3, 0.18, P.MUD, 0.45, align="l", kind="bold")
            dot = st.circle(c.X(v_lo), c.Y(P_LOT), 0.12, P.FRAC, 0.6)
            st.ripple(c.X(v_lo), c.Y(P_LOT), t_lop, t_lop + 1.6, P.FRAC, period=0.8, r0=0.15, r1=0.7, width=0.03, z=0.6)
            lop = pill(st, c.X(v_lo) + 0.25, c.Y(P_LOT) - 0.55, f"leak-off point · {P_LOT:.0f} bar at surface", P.PANEL2, P.FRAC, 0.17, 0.6, align="l")
        st.fade_in(fr, t_close + 0.1, 0.5)
        st.fade_in(ext, t_lop - 0.2, 0.4)
        st.fade_in(lin, t_sq - 0.2, 0.4)
        st.pop_in(dot, t_lop - 0.15, 0.4)
        st.fade_in(lop, t_lop + 0.1, 0.4)
        v2.camera(t_out, t_out + 1.2, focus=(0.0, 0.0), at=(SHIFT, 0.0), scale=1.0)
        v2.finish()
        # ================================================================ equation card (top)
        ey, ex0 = 3.15, -5.9
        parts = [(f"{P_LOT:.0f} bar", P.FRAC, 0.25, "surface reading", t_sr - 0.1),
                 (f"+  mud column ({MW_NEXT:.2f} sg × {SHOE_20:,.0f} m)", P.MUD, 0.21, f"= {P_COL:.0f} bar", t_col - 0.2),
                 (f"=  {FG_SHOE:.2f} sg at the shoe", P.TEXT, 0.25, f"{P_LOT + P_COL:.0f} bar at {SHOE_20:,.0f} m", t_conv)]
        x = ex0 + 0.3
        objs, ends = [], []
        for txt, colr, size, sub, t in parts:
            o = st.text(txt, x, ey + 0.12, size, colr, 0.55, align="l", kind="bold")
            sx = x + (st.measure(txt[:3], size, "bold") if txt.startswith(("+", "=")) else 0.0)
            so = st.text(sub, sx, ey - 0.27, 0.15, P.MUTED, 0.55, align="l")
            st.fade_in([o, so], t, 0.4)
            objs += [o, so]
            x = max(x + st.measure(txt, size, "bold"), sx + st.measure(sub, 0.15, "sans")) + 0.3
            ends.append(x)
        card = st.rect(ex0, ey, ends[1] - ex0, 0.95, P.PANEL2, 0.5, anchor="l")      # grows when the result arrives
        st.fade_in(card, t_sr - 0.35, 0.4)
        st.scale_to(card, t_conv - 0.35, t_conv + 0.05, sx=ends[2] - ex0)
        # ================================================================ the window chart: the point lands on the forecast at 1,000 m
        wc = Chart(st, 1.6, -2.55, 5.0, 4.4, (1.0, 2.0), (0.0, 2200.0), invert_y=True)
        wfr = wc.frame(xticks=[1.0, 1.2, 1.4, 1.6, 1.8, 2.0], yticks=[0, 1000, 2000], xlabel="equivalent mud weight (sg)", ylabel="depth (m)",
                       fx="{:.1f}", tick_size=0.17)
        zs = [M.WATER_DEPTH + 25 * i for i in range(int((2200 - M.WATER_DEPTH) / 25) + 1)]
        band = wc.band([(M.pp(z), z) for z in zs], [(M.fg(z), z) for z in zs], P.SAFE, 0.08, 0.28)
        ppc = wc.curve([M.pp(z) for z in zs], zs, P.PORE, 0.05, 0.15)
        fgc = wc.curve([M.fg(z) for z in zs], zs, P.FRAC, 0.05, 0.15)
        sea = st.rect(wc.X(1.5), (wc.Y(0) + wc.Y(M.WATER_DEPTH)) / 2, wc.w, wc.Y(0) - wc.Y(M.WATER_DEPTH), P.SEA, 0.06, alpha=0.5)
        leg = []
        lxx = wc.X(1.0) + 0.05
        for nm, colr in (("pore pressure", P.PORE), ("fracture", P.FRAC), ("mud weight", P.MUD)):
            leg.append(st.rect(lxx + 0.15, wc.y + wc.h + 0.22, 0.3, 0.05, colr, 0.2, role="shaft"))
            leg.append(st.text(nm, lxx + 0.38, wc.y + wc.h + 0.22, 0.15, colr, 0.2, align="l", kind="bold"))
            lxx += 0.38 + st.measure(nm, 0.15, "bold") + 0.35
        t_w0 = t_out + 1.2
        st.fade_in(wfr + [band, sea] + leg, t_w0, 0.5)
        st.draw_on([ppc, fgc], t_w0 + 0.1, t_w0 + 1.2, "BEZIER")
        x_lo, y_lo = c.X(v_lo) + SHIFT, c.Y(P_LOT)
        mark = st.circle(x_lo, y_lo, 0.13, P.FRAC, 0.9)
        st.fade_in(mark, t_chk - 1.0, 0.1)
        st.move(mark, t_chk - 0.9, t_chk + 0.6, to=(wc.X(FG_SHOE), wc.Y(SHOE_20)))
        st.ripple(wc.X(FG_SHOE), wc.Y(SHOE_20), t_chk + 0.6, t_chk + 2.2, P.FRAC, period=0.8, r0=0.15, r1=0.6, width=0.03, z=0.95)
        ml = pill(st, wc.X(FG_SHOE) + 0.25, wc.Y(SHOE_20), f"measured {FG_SHOE:.2f} sg = forecast", P.PANEL2, P.FRAC, 0.16, 0.9, align="l")
        st.fade_in(ml, t_chk + 0.7, 0.4)
        # caps the next section: its mud weight, plus any kick, must stay below the shoe strength
        mwl = st.rect(wc.X(MW_NEXT), wc.Y(SHOE_20), 0.06, 0.0001, P.MUD, 0.3, anchor="t")
        st.fade_in(mwl, t_cap - 0.2, 0.2)
        st.scale_to(mwl, t_cap - 0.2, t_cap + 0.9, sy=wc.Y(SHOE_20) - wc.Y(SHOE_13))
        mwt = st.text(f"{MW_NEXT:.2f} sg", wc.X(MW_NEXT) + 0.1, wc.Y(1900), 0.16, P.MUD, 0.9, align="l", kind="bold")
        st.fade_in(mwt, t_cap + 0.6, 0.4)
        room = st.line([(wc.X(MW_NEXT), wc.Y(SHOE_20)), (wc.X(FG_SHOE), wc.Y(SHOE_20))], P.TEXT, 0.03, 0.3, role="hair")
        st.draw_on(room, t_cap + 0.3, t_cap + 0.9)
        rl = pill(st, wc.X((MW_NEXT + FG_SHOE) / 2), wc.Y(1300), "room for\nmud + kick", P.PANEL2, P.TEXT, 0.15, 0.9)
        st.fade_in(rl, t_cap + 0.8, 0.4)
        nxt = st.text("next section", wc.X(MW_NEXT) + 0.1, wc.Y(1720), 0.15, P.MUTED, 0.9, align="l")
        st.fade_in(nxt, t_cap + 0.6, 0.4)


def build(st, tl):
    F.header(st, tl)
    F.well_strip(st, 0.0, tl.dur, strings=["30in conductor", "20in surface casing"], marker=SHOE_20)
    beat_riser(st, tl)
    beat_bop(st, tl)
    beat_closed_loop(st, tl)
    beat_test(st, tl)
    beat_lot(st, tl)
