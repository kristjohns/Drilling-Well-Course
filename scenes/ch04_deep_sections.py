"""Ch 4: Drilling the deep sections: the BHA, steering, the bit, drag and doglegs, surveys, the mud, ECD and MPD.

4.01 the drill string hangs from the hook: the BHA (bit, steering tool, sensors, collars) is named as it is spoken; the
     puzzle 'do we push from the rig?' is answered by a ghost string that buckles between the hole walls during the
     pause; then the axial-force diagram: tension from the hook down to a neutral point ~80 % up the BHA, compression
     (weight on bit) below it; only part of the BHA weight rests on the bit
4.02 WHY first (plan-view map: offset target, neighbour well; our vertical wildcat kept straight), then HOW (tilt or push
     the bit): one continuous rotate / slide / rotate path drilled by a bent-housing motor, a rotary steerable pushing
     pads while it turns, and finally the PDC bit: its face, one cutter shearing a layer off the rock (side view) and a
     lathe tool cutting a turning steel bar with the same raked-back geometry
4.03 the capstan (wrap angle grows, T2 grows as e^(mu theta)), the same law in a curved well, a push-in on the bend for
     dogleg severity (deg per 30 m) and fibre-stress reversal on every turn, MWD inclination / direction, a plan view of
     survey stations whose uncertainty ellipses grow along the path
4.04 the circulating mud in a cutaway: overbalance and filter cake on the sand, cuttings, cooling, mud-pulse signals;
     water- vs oil-based mud, barite raising the density (1.00 -> 1.62 sg), oily cuttings shipped to shore
4.05 pumps on / off in a cutaway with a live bottom-hole-pressure trace (636 -> 655 bar), ECD equation, a connection
4.06 the Ch 1 window chart zooms (procedurally) on the open hole below the 9 5/8 in shoe: pumps-off 1.62 sg (dashed amber)
     and a swab nudge while pulling pipe, pumps-on ECD 1.67 sg (solid amber), weakest point = fracture at the shoe
     (1.71 sg); a HYPOTHETICAL narrower window squeezes in and the mud-weight pair slides left (kick side turns red) and
     right (losses side turns red): no mud weight does both. Then MPD: rotating seal on the annulus around the turning
     pipe, returns through a choke (the knob); when the pumps stop the choke closes, back pressure rises 0 -> 20 bar
     (= the lost annular friction) and BHP stays at 655 bar (three lanes: pump rate, choke back pressure, BHP); finally
     the primary-barrier envelope (blue outline) takes in the sealed top and the choke

Colour notes (one meaning per colour): mechanical quantities are neutral (tension = white, compression / weight on bit
= gold WARN, 'slide' = gold, 'rotate' = white); mud and ECD are amber, pore pressure light blue, fracture orange.
Detail shots use a content-only camera (View, as in Ch 3) so the header, well strip and term cards stay put.
"""
from __future__ import annotations
import math
import random

import skia

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common.shapes import pill
from scenes.common.stage import Track, as_list, ease_inout
from scenes.common.look import wrap_to, col, hex_rgb, lighten, darken

TITLE = "Drilling the deep sections"

# ---------------------------------------------------------------- numbers (all from well_model or the narration)
MW = M.section_mud_weights()["9-5/8in intermediate"]           # 1.62 sg: mud for the 8 1/2 in open hole
SHOE = {s.name: s for s in M.programme()}["9-5/8in intermediate"].shoe   # 3,400 m: last casing shoe
SHOE13 = {s.name: s for s in M.programme()}["13-3/8in intermediate"].shoe  # 2,000 m
FG_SHOE = M.fg(SHOE)                                            # 1.71 sg: the weakest point of the open hole
ECD_ADD = 0.05                                                  # [SIM] annular friction as EMW, pumps on
ECD = MW + ECD_ADD                                              # 1.67 sg
TVD = 4000.0                                                    # bit depth for the 4.05 gauge (as in Ch 7)
P_STATIC = M.bar(TVD, MW)                                       # 636 bar
P_ECD = M.bar(TVD, ECD)                                         # 655 bar
P_PORE = M.bar(TVD, M.pp(TVD))                                  # 607 bar
BARITE_SG = 4.2

TENS = "#e8eef6"        # tension (neutral white)
COMP = P.WARN           # compression / weight on bit / sliding (gold highlight, not a fluid colour)
BARITE = "#d6dbe4"      # barite powder (drawing only)
CAKE = "#8a5a14"        # filter cake: dried mud solids (darker than the mud)
CUTTING = "#8c7a62"     # rock cuttings
RUBBER = "#272b35"


# ====================================================================================================== small helpers
def W(b, i, needle, frac=0.0):
    """Time `needle` is spoken in sentence i of beat b (fails loudly if the script changed)."""
    txt = b._sentences()[i]
    if needle.lower() not in txt.lower():
        raise KeyError(f"{b.id} sentence {i}: {needle!r} not in {txt!r}")
    return b.word(i, needle, frac)


def _sm(f):
    f = min(max(f, 0.0), 1.0)
    return f * f * (3 - 2 * f)


def _env(t, a, b, d=0.35):
    return max(0.0, min(1.0, (t - a) / d, (b - t) / d))


def _ramp(t, a, b):
    return _sm((t - a) / max(b - a, 1e-6))


def tag(st, x, y, text, fg=P.TEXT, size=0.19, align="l", bg=P.PANEL2, z=0.5):
    return pill(st, x, y, text, bg, fg, size, z, align=align)


def leader(st, x0, y0, x1, y1, color=P.MUTED, z=0.45):
    return [st.line([(x0, y0), (x1, y1)], color, 0.022, z, alpha=0.85), st.circle(x1, y1, 0.045, color, z + 0.01, role="solid")]


def num_badge(st, x, y, n, color=P.MUD, z=0.5):
    return [st.circle(x, y, 0.19, P.PANEL2, z, role="solid"), st.ring(x, y, 0.19, 0.03, color, z + 0.01),
            st.text(str(n), x, y, 0.18, color, z + 0.02, kind="bold")]


def _arc(cx, cy, r, a0, a1, n=48):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def _ell_pts(cx, cy, a, b, rot_deg, n=40):
    c, s = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    return [(cx + a * math.cos(2 * math.pi * i / n) * c - b * math.sin(2 * math.pi * i / n) * s,
             cy + a * math.cos(2 * math.pi * i / n) * s + b * math.sin(2 * math.pi * i / n) * c) for i in range(n)]


def _stroke(color, alpha, width, cap=True):
    return skia.Paint(Color=col(hex_rgb(color), alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width,
                      StrokeCap=skia.Paint.kRound_Cap if cap else skia.Paint.kButt_Cap, StrokeJoin=skia.Paint.kRound_Join)


def _fill(color, alpha):
    return skia.Paint(Color=col(hex_rgb(color), alpha), AntiAlias=True)


def _glow(look, color, alpha, width):
    return skia.Paint(Color=col(hex_rgb(color), 0.4 * alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width * 2.6,
                      StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join, MaskFilter=look._blur(max(3.0, width * look.k * 0.9)))


def _path(pts, close=False):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def _polyline_at(pts, s):
    """Point and unit tangent at arc length s along a polyline."""
    acc = 0.0
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        if acc + L >= s or (x1, y1) == pts[-1]:
            f = 0.0 if L == 0 else min(max((s - acc) / L, 0.0), 1.0)
            return (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f), ((x1 - x0) / max(L, 1e-9), (y1 - y0) / max(L, 1e-9))
        acc += L
    return pts[-1], (0.0, -1.0)


def _plen(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:]))


def _sub(pts, s0, s1, n=None):
    """Sub-polyline between arc lengths s0 and s1."""
    out = [_polyline_at(pts, s0)[0]]
    acc = 0.0
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        acc += math.hypot(x1 - x0, y1 - y0)
        if s0 < acc < s1:
            out.append((x1, y1))
    out.append(_polyline_at(pts, s1)[0])
    return out


# ====================================================================================================== content camera
class View:
    """A camera for the drawing only (copied from Ch 3). Objects and procedurals created inside `with view:` are drawn
    through a local transform screen = world * s + d (clipped to `clip`), so the chapter furniture is unaffected."""

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


# ====================================================================================================== 4.01 the BHA
SX = -4.6                 # string axis
HOLE_W = 0.88
Y_RIG, Y_ROCK = 2.75, 2.45
Y_PIPE_TOP = 3.24
Y_BRK = (0.9, 1.08)       # break in the drawing: kilometres of drill pipe
Y_X = -0.45               # crossover drill pipe -> drill collars
Y_C = -1.95               # bottom of the collars
Y_S = -2.3                # bottom of the sensor sub
Y_ST = -2.72              # bottom of the steering tool
Y_BIT = -3.02             # bit face
NP_FRAC = 0.8             # neutral point ~80 % of the way up the BHA
Y_NP = Y_BIT + NP_FRAC * (Y_X - Y_BIT)
GX = 2.3                  # ghost (pushed) string
XA, XS = -1.6, 0.12       # axial-force diagram: zero axis, world units per force unit
WP, WC, JUMP = 1.5, 4.0, 8.0


def _force(y):
    """Axial force (tension +) at height y of the drawing (schematic units)."""
    if y <= Y_X:
        return WC * (y - Y_NP)
    f = WC * (Y_X - Y_NP)
    if y <= Y_BRK[0]:
        return f + WP * (y - Y_X)
    f += WP * (Y_BRK[0] - Y_X) + JUMP
    return f + WP * (y - Y_BRK[0])


def beat_bha(st, tl):
    b = tl["4.01"]
    s = b.sent
    t_bha = W(b, 0, "bottom-hole assembly")
    t_bit, t_steer, t_sens, t_coll = W(b, 0, "the bit"), W(b, 0, "steering tool"), W(b, 0, "measurement sensors"), W(b, 0, "drill collars")
    t_ton = W(b, 1, "tonnes")
    t_push = W(b, 2, "push")
    t_buck0, t_buck1 = b.sent_end[2] + 0.1, b.sent_end[2] + 1.4
    t_no = s[3]
    t_hold = W(b, 4, "holds")
    t_tens = W(b, 5, "tension")
    t_part = W(b, 5, "only part")
    t_rests = W(b, 5, "rests on the bit")
    t_push2 = W(b, 6, "push down")
    t_buckle2 = W(b, 6, "buckle")
    t_keep = W(b, 6, "compression")
    view = View(st, b.start, b.end, z=0.2)
    with st.span(b.start, b.end):
        with view:
            # ---- the hole in rock, the rig floor and the hook
            rw = 0.62
            rock = [st.rect(SX - HOLE_W / 2 - rw / 2, (Y_ROCK + Y_BIT) / 2, rw, Y_ROCK - Y_BIT, P.ROCK, 0.0),
                    st.rect(SX + HOLE_W / 2 + rw / 2, (Y_ROCK + Y_BIT) / 2, rw, Y_ROCK - Y_BIT, P.ROCK, 0.0),
                    st.rect(SX, Y_BIT - 0.22, HOLE_W + 2 * rw, 0.44, P.ROCK, 0.0)]
            hole = st.rect(SX, (Y_ROCK + Y_BIT) / 2, HOLE_W, Y_ROCK - Y_BIT, P.BG, 0.01)
            floor = st.rect(SX, Y_RIG, 2.3, 0.1, P.STEEL_DK, 0.25)
            block = st.rect(SX, 3.42, 0.62, 0.34, P.STEEL_DK, 0.3, role="solid")
            cables = [st.line([(SX + dx, 3.59), (SX + dx, 3.9)], P.MUTED, 0.025, 0.29) for dx in (-0.18, 0.18)]
            hook_l = st.text("hook", SX - 0.45, 3.42, 0.17, P.MUTED, 0.3, align="r", kind="bold")
            st.fade_in(rock + [hole], b.start + 0.05, 0.5)
            st.fade_in([floor, block, hook_l] + cables, b.start + 0.2, 0.5)
            # ---- the string, top to bottom
            pipe_a = st.rect(SX, (Y_PIPE_TOP + Y_BRK[1]) / 2, 0.18, Y_PIPE_TOP - Y_BRK[1], P.STEEL, 0.2)
            pipe_b = st.rect(SX, (Y_BRK[0] + Y_X) / 2, 0.18, Y_BRK[0] - Y_X, P.STEEL, 0.2)
            coll = st.rect(SX, (Y_X + Y_C) / 2, 0.44, Y_X - Y_C, "#71839c", 0.21)
            sens = st.rect(SX, (Y_C + Y_S) / 2, 0.4, Y_C - Y_S, "#98a9bf", 0.21)
            sens_w = st.rect(SX, (Y_C + Y_S) / 2, 0.12, 0.12, P.PANEL2, 0.22, role="solid")
            sens_d = st.circle(SX, (Y_C + Y_S) / 2, 0.035, P.SAFE, 0.23)
            steer = st.rect(SX, (Y_S + Y_ST) / 2, 0.44, Y_S - Y_ST, "#56667d", 0.21)
            pads = [st.rect(SX + sx * 0.25, (Y_S + Y_ST) / 2, 0.07, 0.22, "#c9d4e1", 0.22) for sx in (-1, 1)]
            bitp = [(SX - 0.2, Y_ST), (SX + 0.2, Y_ST), (SX + 0.43, Y_ST - 0.1), (SX + 0.43, Y_BIT + 0.06), (SX + 0.37, Y_BIT),
                    (SX - 0.37, Y_BIT), (SX - 0.43, Y_BIT + 0.06), (SX - 0.43, Y_ST - 0.1)]
            bit = st.poly(bitp, P.STEEL_DK, 0.22)
            cutters = [st.circle(SX + dx, Y_BIT + 0.07, 0.045, "#1d2129", 0.23, role="solid") for dx in (-0.3, -0.15, 0.0, 0.15, 0.3)]
            string = [pipe_a, pipe_b, coll, sens, sens_w, sens_d, steer, bit] + pads + cutters
            st.fade_in([pipe_a], b.start + 0.4, 0.5)
            st.fade_in([pipe_b], b.start + 0.6, 0.5)
            st.fade_in([coll], b.start + 0.8, 0.5)
            st.fade_in([sens, sens_w, sens_d, steer, bit] + pads + cutters, b.start + 1.0, 0.5)
            # break: kilometres of pipe left out
            band = st.rect(SX, (Y_BRK[0] + Y_BRK[1]) / 2, 2.1, Y_BRK[1] - Y_BRK[0] - 0.02, P.BG, 0.36, role="flat")
            zz = [st.line([(SX - 0.9, y - 0.05), (SX + 0.9, y + 0.05)], P.MUTED, 0.03, 0.37) for y in Y_BRK]
            st.fade_in([band] + zz, b.start + 0.6, 0.4)
            km = st.text("kilometres of drill pipe", SX + 0.62, 1.55, 0.17, P.MUTED, 0.4, align="l")
            st.fade_in(km, b.start + 0.9, 0.5)
            st.fade_out(km, t_bha - 0.6, 0.4)

            # ---- s0: name the BHA, part by part, while the view pushes in
            bx = SX + 0.62
            brk = [st.line([(bx, Y_X), (bx, Y_BIT)], P.TEXT, 0.025, 0.4), st.line([(bx - 0.08, Y_X), (bx, Y_X)], P.TEXT, 0.025, 0.4),
                   st.line([(bx - 0.08, Y_BIT), (bx, Y_BIT)], P.TEXT, 0.025, 0.4)]
            ttl = st.text("BOTTOM-HOLE ASSEMBLY (BHA)", bx + 0.15, Y_X + 0.08, 0.2, P.TEXT, 0.4, align="l", kind="bold")
            st.fade_in(brk + [ttl], t_bha - 0.1, 0.4)
            parts = [("bit", (Y_ST + Y_BIT) / 2, t_bit), ("steering tool", (Y_S + Y_ST) / 2, t_steer),
                     ("measurement sensors", (Y_C + Y_S) / 2, t_sens), ("drill collars: heavy steel", (Y_X + Y_C) / 2, t_coll)]
            lab = []
            for name, y, t in parts:
                d = st.circle(bx, y, 0.04, P.TEXT, 0.41, role="solid")
                tx = st.text(name, bx + 0.15, y, 0.17, P.TEXT, 0.41, align="l", kind="bold")
                st.fade_in([d, tx], t - 0.1, 0.35)
                lab += [d, tx]
            view.camera(t_bha - 0.5, t_bha + 1.1, focus=(SX + 1.0, -1.72), at=(-3.0, -0.75), scale=1.5)
            st.fade_out(brk + [ttl] + lab, s[1] + 0.5, 0.4)
            view.home(s[1] + 0.4, s[1] + 1.6)

            # ---- s1: tonnes of force on the bit
            need = st.arrow(SX + 0.8, -1.95, SX + 0.8, Y_BIT + 0.02, COMP, 0.08, 0.26, 0.45)
            need_l = st.text("tonnes of force\non the bit", SX + 0.98, -2.45, 0.18, COMP, 0.45, align="l", kind="bold")
            st.fade_in(need + [need_l], t_ton - 0.2, 0.4)
            st.fade_out(need + [need_l], t_hold - 0.3, 0.4)

            # ---- s2 + pause: the ghost string pushed from the top buckles between the walls
            gw = 0.45
            gwalls = st.dashed((GX - gw, Y_ROCK), (GX - gw, Y_BIT), P.MUTED, 0.025, 0.14, 0.1, 0.1) + \
                st.dashed((GX + gw, Y_ROCK), (GX + gw, Y_BIT), P.MUTED, 0.025, 0.14, 0.1, 0.1)
            gfloor = st.rect(GX, Y_BIT - 0.14, 1.5, 0.28, P.ROCK, 0.05)
            grig = st.rect(GX, Y_RIG, 1.5, 0.08, P.STEEL_DK, 0.25)
            push = st.arrow(GX, 3.72, GX, Y_RIG + 0.08, COMP, 0.09, 0.28, 0.45)
            q = tag(st, GX - 0.32, 3.36, "push from the rig?", P.TEXT, 0.19, align="r")
            st.fade_in(gwalls + [gfloor, grig] + push + q, t_push - 0.2, 0.4)
            amp_max = gw - 0.1

            def ghost(c, t, look):
                a = _env(t, t_push - 0.1, b.end, 0.4)
                dim = 1.0 - 0.6 * _ramp(t, t_no + 0.4, t_no + 1.2) + 0.5 * _ramp(t, t_push2 - 0.3, t_push2 + 0.4) \
                    - 0.5 * _ramp(t, t_keep + 0.5, t_keep + 1.4)
                a *= max(0.25, min(1.0, dim))
                if a <= 0:
                    return
                A = _ramp(t, t_buck0, t_buck1)
                pts = []
                n = 60
                for i in range(n + 1):
                    f = i / n
                    y = Y_RIG - f * (Y_RIG - Y_BIT - 0.02)
                    x = 0.62 * A * math.sin(4.5 * math.pi * f) * math.sin(math.pi * f) ** 0.4
                    pts.append((GX + max(-amp_max, min(amp_max, x)), y))
                path = _path(pts)
                c.drawPath(path, _stroke("#5d6b80", a, 0.2))
                c.drawPath(path, _stroke(P.STEEL, a, 0.12))
                if A > 0.6:
                    for (x, y) in pts[::3]:
                        if abs(x - GX) >= amp_max - 1e-3:
                            c.drawCircle(x + (0.07 if x > GX else -0.07), y, 0.05, _fill(P.BAD, a * min(1.0, (A - 0.6) / 0.3)))
            st.procedural(t_push - 0.2, b.end, 0.3, ghost)
            bk = tag(st, GX + 0.62, 1.2, "BUCKLES", "#ffffff", 0.2, bg=P.BAD)
            st.pop_in(bk, t_buck1 - 0.2, 0.35)
            strike = st.line([(GX - 0.32 - st.measure("push from the rig?", 0.19, "bold") - 0.25, 3.36), (GX - 0.28, 3.36)], P.BAD, 0.05, 0.6)
            st.draw_on(strike, t_no, t_no + 0.35, "BEZIER")
            st.fade(push, t_no + 0.6, t_no + 1.2, 1.0, 0.35)
            st.fade_out(q + [strike], t_hold - 0.4, 0.4)
            st.fade(bk, t_no + 0.6, t_no + 1.2, 1.0, 0.35)
            st.fade(bk, t_buckle2 - 0.3, t_buckle2 + 0.2, 0.35, 1.0)
            st.fade(bk, t_keep + 0.5, t_keep + 1.2, 1.0, 0.35)

            # ---- s4: the rig holds the pipe back (hook load)
            ups = []
            for dx in (-0.18, 0.18):
                ups += st.arrow(SX + dx, 3.6, SX + dx, 3.9, TENS, 0.05, 0.14, 0.45)
            hold = tag(st, SX + 0.5, 3.42, "the rig holds the pipe back", P.TEXT, 0.18)
            st.fade_in(ups + hold, t_hold - 0.2, 0.4)

            # ---- s5: axial force: tension above the neutral point, compression below
            ys = [Y_RIG, Y_BRK[1], Y_BRK[0], Y_X, Y_NP, Y_BIT]
            axis = st.line([(XA, Y_RIG + 0.12), (XA, Y_BIT - 0.05)], P.MUTED, 0.022, 0.3)
            ax_t = st.text("tension →", XA + 0.1, Y_RIG + 0.22, 0.16, TENS, 0.3, align="l", kind="bold")
            ax_c = st.text("← compression", XA - 0.1, Y_RIG + 0.22, 0.16, COMP, 0.3, align="r", kind="bold")
            ax_n = st.text("axial force along the string", XA, Y_BIT - 0.32, 0.16, P.MUTED, 0.3)
            dx0, dx1 = XA - 0.15, XA + XS * _force(Y_RIG) + 0.2
            band2 = st.rect((dx0 + dx1) / 2, (Y_BRK[0] + Y_BRK[1]) / 2, dx1 - dx0, Y_BRK[1] - Y_BRK[0] - 0.02, P.BG, 0.36, role="flat")
            zz2 = [st.line([(dx0, y - 0.05), (dx1, y + 0.05)], P.MUTED, 0.03, 0.37) for y in Y_BRK]
            st.fade_in([axis, ax_t, ax_c, ax_n, band2] + zz2, t_tens - 0.6, 0.4)
            tp = [(XA + XS * _force(y), y) for y in ys[:5]]
            cp = [(XA + XS * _force(y), y) for y in ys[4:]]
            tcurve = st.line(tp, TENS, 0.045, 0.32)
            tfill = st.poly([(XA, Y_RIG)] + tp + [(XA, Y_NP)], TENS, 0.29, alpha=0.13, role="flat")
            ccurve = st.line(cp, COMP, 0.05, 0.32)
            cfill = st.poly([(XA, Y_NP)] + cp + [(XA, Y_BIT)], COMP, 0.29, alpha=0.22, role="flat")
            st.draw_on(tcurve, t_tens - 0.2, t_tens + 1.8, "BEZIER")
            st.fade_in(tfill, t_tens + 1.2, 0.6)
            hk = st.text("hook load", tp[0][0] + 0.12, Y_RIG, 0.17, TENS, 0.33, align="l", kind="bold")
            st.fade_in(hk, t_tens + 0.2, 0.4)
            # tint on the string itself
            ttint = st.line([(SX, Y_RIG - 0.05), (SX, Y_NP)], TENS, 0.05, 0.24, alpha=0.55)
            ctint = st.line([(SX, Y_NP), (SX, Y_ST + 0.05)], COMP, 0.06, 0.24)
            st.draw_on(ttint, t_tens - 0.2, t_tens + 1.8, "BEZIER")
            # on the string itself: stretched pipe (arrows pulling apart), squeezed collars (arrows pushing together)
            pairs_t, pairs_c = [], []
            for y in (2.0, 0.25):
                pairs_t += st.arrow(SX - 0.3, y + 0.04, SX - 0.3, y + 0.36, TENS, 0.035, 0.11, 0.45) + \
                    st.arrow(SX - 0.3, y - 0.04, SX - 0.3, y - 0.36, TENS, 0.035, 0.11, 0.45)
            yc = (Y_NP + Y_C) / 2
            pairs_c += st.arrow(SX - 0.33, yc + 0.4, SX - 0.33, yc + 0.06, COMP, 0.035, 0.11, 0.45) + \
                st.arrow(SX - 0.33, yc - 0.4, SX - 0.33, yc - 0.06, COMP, 0.035, 0.11, 0.45)
            st.fade_in(pairs_t, t_tens + 0.2, 0.4)
            st.fade_in(pairs_c, t_part + 0.3, 0.4)
            st.draw_on(ccurve, t_part - 0.1, t_part + 1.0, "BEZIER")
            st.draw_on(ctint, t_part - 0.1, t_part + 1.0, "BEZIER")
            st.fade_in(cfill, t_part + 0.6, 0.5)
            npl = st.dashed((SX - 0.55, Y_NP), (XA + 0.05, Y_NP), P.TEXT, 0.025, 0.12, 0.08, 0.42)
            npt = tag(st, XA + 0.18, Y_NP, "neutral point", P.TEXT, 0.18)
            npn = st.text("kept inside the collars", XA + 0.22, Y_NP - 0.42, 0.16, P.MUTED, 0.42, align="l")
            st.fade_in(npl + npt + [npn], t_part + 0.2, 0.4)
            wob = st.arrow(SX, Y_BIT - 0.42, SX, Y_BIT - 0.02, COMP, 0.08, 0.2, 0.45)
            wobl = st.text("weight\non bit", XA + XS * _force(Y_BIT) - 0.12, Y_BIT + 0.05, 0.16, COMP, 0.33, align="r", kind="bold")
            st.fade_in(wob, t_rests - 0.3, 0.3)
            st.fade_in(wobl, t_rests - 0.1, 0.4)
            st.ripple(SX, Y_BIT, t_rests - 0.2, t_rests + 1.0, COMP, period=0.6, r0=0.2, r1=0.8)

            # ---- WOB gauge: only part of the BHA weight rests on the bit
            gx0, gw_ = 3.55, 3.7
            gt = st.text("WEIGHT ON THE BIT", gx0, -0.15, 0.17, P.MUTED, 0.4, align="l", kind="bold")
            l1 = st.text("BHA weight (in mud)", gx0, -0.6, 0.17, P.TEXT, 0.4, align="l")
            tr1 = st.rect(gx0 + gw_ / 2, -0.92, gw_, 0.16, P.GRID, 0.4, role="pill")
            b1 = st.rect(gx0, -0.92, 0.0001, 0.16, "#98a9bf", 0.41, anchor="l", role="pill")
            l2 = st.text("resting on the bit", gx0, -1.35, 0.17, COMP, 0.4, align="l", kind="bold")
            tr2 = st.rect(gx0 + gw_ / 2, -1.67, gw_, 0.16, P.GRID, 0.4, role="pill")
            b2 = st.rect(gx0, -1.67, 0.0001, 0.16, COMP, 0.41, anchor="l", role="pill")
            st.fade_in([gt, l1, tr1, b1, l2, tr2, b2], t_part - 0.2, 0.4)
            st.scale_to(b1, t_part, t_part + 0.9, sx=gw_)
            st.scale_to(b2, t_part + 0.5, t_rests + 0.6, sx=gw_ * NP_FRAC)
            rest = st.text("the rest hangs from the hook", gx0, -2.05, 0.16, P.MUTED, 0.4, align="l")
            st.fade_in(rest, t_rests + 0.3, 0.4)

            # ---- s6: keep the compression in the collars
            st.ripple(GX + amp_max, -0.3, t_buckle2 - 0.1, t_buckle2 + 1.0, P.BAD, period=0.6, r0=0.15, r1=0.7)
            keep = tag(st, XA + 0.18, -2.15, "compression stays in\nthe heavy, stiff collars", COMP, 0.17)
            st.fade_in(keep, t_keep - 0.1, 0.4)
            glow = st.rect(SX, (Y_NP + Y_ST) / 2, 0.6, Y_NP - Y_ST, COMP, 0.18, role="flat")
            st.fade(glow, t_keep, t_keep + 0.5, 0.0, 0.28)
            st.fade(glow, t_keep + 0.5, t_keep + 1.4, 0.28, 0.12)


# ====================================================================================================== 4.02 why steer, how, the bit
def _platform(st, x, y, color=P.STEEL_DK, z=0.4, r=0.17):
    return [st.rect(x, y, r * 2, r * 2, color, z, role="solid"), st.ring(x, y, r * 0.55, 0.03, P.TEXT, z + 0.01)]


def _bez(p0, c, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * t * (1 - t) * c[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * t * (1 - t) * c[1] + t * t * p2[1])
            for t in (i / n for i in range(n + 1))]


# motor panel geometry: one continuous path (rotate -> slide -> rotate)
MP_X0, MP_Y0, MP_YK, MP_R, MP_TH, MP_L3 = -4.6, 2.7, 1.0, 2.6, 40.0, 2.0


def _motor_path():
    seg1 = [(MP_X0, MP_Y0), (MP_X0, MP_YK)]
    arc = [(MP_X0 + MP_R - MP_R * math.cos(math.radians(a)), MP_YK - MP_R * math.sin(math.radians(a)))
           for a in [MP_TH * i / 40 for i in range(41)]]
    d = (math.sin(math.radians(MP_TH)), -math.cos(math.radians(MP_TH)))
    e = arc[-1]
    seg3 = [e, (e[0] + d[0] * MP_L3, e[1] + d[1] * MP_L3)]
    return seg1, arc, seg3


def beat_steering(st, tl):
    b = tl["4.02"]
    s = b.sent
    t_tgt, t_clear, t_wild, t_str = W(b, 1, "target"), W(b, 1, "other wells"), W(b, 1, "vertical wildcat"), W(b, 1, "keep the hole straight")
    t_dd = s[2]
    t_tilt, t_pushs = W(b, 3, "tilt"), W(b, 3, "push it sideways")
    t_motor, t_flow, t_bend = s[4], W(b, 4, "driven by the mud"), W(b, 4, "slight bend")
    t_slide, t_curve = W(b, 4, "stop turning"), W(b, 4, "curves", 1.0) + 0.15
    t_rss, t_pads, t_turns = s[5], W(b, 5, "pushes pads"), W(b, 5, "whole string turns")
    t_pdc, t_poly, t_shear, t_lathe = s[6], W(b, 6, "polycrystalline"), W(b, 6, "shears rock"), W(b, 6, "lathe")
    with st.span(b.start, b.end):
        # ================================================================ WHY: the map, then our vertical wildcat
        endA = t_tilt - 0.6
        with st.span(b.start, endA + 0.5):
            head = st.text("Why steer?", -5.85, 3.62, 0.34, P.TEXT, 0.5, align="l", kind="bold")
            st.fade_in(head, s[0] - 0.1, 0.4)
            card1 = st.rect(-3.05, 0.2, 5.7, 6.1, P.PANEL, 0.0)
            pv = tag(st, -5.72, 2.86, "PLAN VIEW · from above", P.MUTED, 0.15)
            nx, ny = -0.62, 2.6
            north = st.arrow(nx, ny - 0.25, nx, ny + 0.3, P.TEXT, 0.035, 0.15, 0.4) + [st.text("N", nx, ny - 0.45, 0.16, P.TEXT, 0.4, kind="bold")]
            rig = (-4.6, 1.9)
            tgt = (-1.5, -1.9)
            rg = _platform(st, *rig)
            rgl = st.text("our rig", rig[0], rig[1] + 0.42, 0.17, P.TEXT, 0.4, kind="bold")
            st.fade_in([card1, rgl] + pv + north + rg, s[0] + 0.1, 0.5)
            # an offset target
            tg = [st.ring(tgt[0], tgt[1], 0.26, 0.04, P.WARN, 0.4), st.ring(tgt[0], tgt[1], 0.13, 0.035, P.WARN, 0.4),
                  st.circle(tgt[0], tgt[1], 0.045, P.WARN, 0.41)]
            tgl = st.text("target", tgt[0] - 0.4, tgt[1] - 0.05, 0.17, P.WARN, 0.4, align="r", kind="bold")
            st.pop_in(tg, t_tgt - 0.1, 0.4)
            st.fade_in(tgl, t_tgt, 0.4)
            path = st.line(_bez(rig, (-1.0, 1.4), tgt), P.WARN, 0.07, 0.35)
            st.draw_on(path, t_tgt + 0.4, t_tgt + 2.4, "BEZIER")
            # a neighbour well with its keep-out zone; the straight line would hit it
            nb0, nb1 = (-3.95, 0.6), (-2.55, -0.8)
            nb = _platform(st, *nb0, color="#56667d")
            nbp = st.line([nb0, nb1], P.MUTED, 0.06, 0.3)
            zone = st.line([nb0, nb1], P.BAD, 0.62, 0.25, alpha=0.18, role="flat")
            nbl = st.text("other well:\nkeep clear", -4.05, -0.95, 0.16, P.MUTED, 0.4, kind="bold")
            st.fade_in(nb + [nbp, zone, nbl], t_clear - 0.2, 0.4)
            straight = st.dashed(rig, tgt, P.MUTED, 0.03, 0.14, 0.1, 0.32)
            st.fade_in(straight, t_clear + 0.4, 0.3)
            hit = [st.line([(-3.2, 0.12), (-2.9, -0.18)], P.BAD, 0.06, 0.45), st.line([(-3.2, -0.18), (-2.9, 0.12)], P.BAD, 0.06, 0.45)]
            st.draw_on(hit, t_clear + 0.7, t_clear + 1.0, "BEZIER")
            st.ripple(-3.05, -0.03, t_clear + 0.7, t_clear + 1.6, P.BAD, period=0.7, r0=0.1, r1=0.6)
            # our vertical wildcat: kept straight
            card2 = st.rect(1.5, 0.2, 2.9, 6.1, P.PANEL, 0.0)
            sv = tag(st, 0.2, 2.86, "OUR WELL · side view", P.MUTED, 0.15)
            sb = st.rect(1.5, 2.1, 2.6, 0.05, P.SEABED, 0.1)
            rk = st.rect(1.5, -0.3, 2.6, 4.75, P.ROCK, 0.05)
            rg2 = _platform(st, 1.5, 2.45)
            wander = st.line(_bez((1.5, 2.1), (1.5, 0.0), (2.55, -2.3)), P.MUTED, 0.035, 0.3)
            wl = st.text("left alone,\nthe bit\nwanders", 1.35, -0.6, 0.15, P.MUTED, 0.35, align="r")
            vert = st.line([(1.5, 2.1), (1.5, -2.55)], P.WARN, 0.07, 0.35)
            st.fade_in([card2, sb, rk] + sv + rg2, t_wild - 0.4, 0.4)
            st.draw_on(wander, t_wild + 0.1, t_wild + 1.5, "BEZIER")
            st.fade_in(wl, t_wild + 0.8, 0.4)
            st.draw_on(vert, t_str - 0.3, t_str + 1.3, "BEZIER")
            kl = tag(st, 1.5, -2.45, "kept straight", P.WARN, 0.16, align="c")
            st.fade_in(kl, t_str + 0.9, 0.4)
            dd = tag(st, -1.4, -3.3, "DIRECTIONAL DRILLING: steering the hole", P.TEXT, 0.2, align="c")
            st.fade_in(dd, t_dd - 0.1, 0.4)
            st.fade_out([head, card1, rgl, path, nbp, zone, nbl, card2, sb, rk, wander, wl, vert] + pv + north + rg + tg + [tgl] + nb +
                        straight + hit + sv + rg2 + kl + dd, endA, 0.45)

        # ================================================================ HOW: tilt the bit or push it
        endB = t_motor + 0.4
        with st.span(endA, endB + 0.5):
            icons = []
            for k, (cx, cap, t) in enumerate(((-3.3, "TILT the bit", t_tilt), (0.7, "PUSH the bit sideways", t_pushs))):
                walls = [st.rect(cx - 0.62, 0.55, 0.3, 3.3, P.ROCK, 0.05), st.rect(cx + 0.62, 0.55, 0.3, 3.3, P.ROCK, 0.05)]
                hole = st.rect(cx, 0.55, 0.94, 3.3, P.BG, 0.06)
                up = st.rect(cx, 1.45, 0.34, 1.5, "#71839c", 0.2)
                objs = walls + [hole, up]
                if k == 0:
                    lo = st.rect(cx + 0.06, 0.25, 0.34, 0.9, "#56667d", 0.21, rot=8)
                    bt = st.rect(cx + 0.14, -0.27, 0.44, 0.2, P.STEEL_DK, 0.21, rot=8)
                    ang = st.line(_arc(cx, 0.7, 0.55, -90, -82, 8), COMP, 0.04, 0.3)
                    ar = st.arrow(cx + 0.18, -0.5, cx + 0.42, -1.25, COMP, 0.06, 0.2, 0.3)
                    objs += [lo, bt, ang] + ar
                else:
                    lo = st.rect(cx, 0.2, 0.34, 1.0, "#56667d", 0.21)
                    pad = st.rect(cx - 0.3, 0.4, 0.26, 0.36, "#c9d4e1", 0.22)
                    bt = st.rect(cx, -0.38, 0.44, 0.2, P.STEEL_DK, 0.21)
                    pa = st.arrow(cx - 0.05, 0.4, cx - 0.38, 0.4, P.TEXT, 0.05, 0.14, 0.3)
                    ar = st.arrow(cx + 0.1, -0.6, cx + 0.42, -1.25, COMP, 0.06, 0.2, 0.3)
                    objs += [lo, pad, bt] + pa + ar
                cp = st.text(cap, cx, -1.75, 0.24, COMP if k == 0 else P.TEXT, 0.4, kind="bold")
                st.fade_in(objs + [cp], t - 0.25, 0.45)
                icons += objs + [cp]
            st.fade_out(icons, endB, 0.45)

        # ================================================================ the mud motor: one continuous path
        endC = t_pdc - 0.35
        seg1, arc, seg3 = _motor_path()
        full = seg1 + arc[1:] + seg3[1:]
        L1, L2, L3 = _plen(seg1), _plen(arc), _plen(seg3)
        ta0, ta1 = endB + 0.4, t_slide
        tb1 = max(t_curve, t_slide + 2.5)
        tc1 = tb1 + 2.2

        def s_at(t):
            if t <= ta0:
                return 0.0
            if t <= ta1:
                return L1 * (t - ta0) / (ta1 - ta0)
            if t <= tb1:
                return L1 + L2 * (t - ta1) / (tb1 - ta1)
            return L1 + L2 + L3 * min(1.0, (t - tb1) / (tc1 - tb1))

        def sliding(t):
            return ta1 <= t < tb1

        with st.span(endB, endC + 0.5):
            card = st.rect(-1.55, 0.0, 8.9, 6.8, P.PANEL, 0.0)
            ttl = tag(st, -5.8, 3.0, "MUD MOTOR · tilt the bit", COMP, 0.18)
            rock = st.rect(-3.55, -0.22, 4.4, 5.86, P.ROCK, 0.05)
            st.fade_in([card, rock] + ttl, endB + 0.35, 0.5)
            holes, tracks = [], []
            for pts, a, c_, colr in ((seg1, ta0, ta1, TENS), (arc, ta1, tb1, COMP), (seg3, tb1, tc1, TENS)):
                h = st.line(pts, P.BG, 0.36, 0.1, role="flat")
                tr = st.line(pts, colr, 0.06, 0.12, alpha=0.9)
                st.draw_on([h, tr], a, c_, "LINEAR")
                holes.append(h)
                tracks.append(tr)

            def tool(c, t, look):
                a = _env(t, endB + 0.3, endC + 0.4, 0.4)
                if a <= 0:
                    return
                sv = s_at(t)
                c.save()
                c.clipRect(skia.Rect.MakeLTRB(-5.75, -3.15, -1.35, 2.71))
                (px, py), (dx, dy) = _polyline_at(full, sv)
                nx_, ny_ = -dy, dx
                sl = sliding(t)
                delta = math.radians(9.0) * (1.0 if sl else math.cos(9.0 * t))
                ex, ey = math.cos(delta) * dx + math.sin(delta) * nx_, math.cos(delta) * dy + math.sin(delta) * ny_
                bx_, by_ = px - 0.5 * ex, py - 0.5 * ey
                ux, uy = bx_ - 0.8 * dx, by_ - 0.8 * dy
                # mud particles running down the pipe behind the tool
                if sv > 0.2:
                    for k in range(int(sv / 0.28) + 1):
                        q = (k * 0.28 + 0.9 * t) % max(sv, 0.01)
                        (qx, qy), _ = _polyline_at(full, q)
                        c.drawCircle(qx, qy, 0.035, _fill(P.MUD, 0.85 * a))
                c.drawLine(ux, uy, bx_, by_, _stroke("#71839c", a, 0.24, cap=False))
                c.drawLine(bx_, by_, px - 0.08 * ex, py - 0.08 * ey, _stroke("#56667d", a, 0.24, cap=False))
                c.drawLine(px - 0.1 * ex, py - 0.1 * ey, px + 0.02 * ex, py + 0.02 * ey, _stroke(P.STEEL_DK, a, 0.34, cap=False))
                if sl:
                    tx, ty = bx_ + 0.15 * nx_, by_ + 0.15 * ny_
                    c.drawLine(tx, ty, tx + 0.45 * nx_, ty + 0.45 * ny_, _glow(look, COMP, a, 0.05))
                    c.drawLine(tx, ty, tx + 0.45 * nx_, ty + 0.45 * ny_, _stroke(COMP, a, 0.05))
                    hx, hy = tx + 0.55 * nx_, ty + 0.55 * ny_
                    c.drawPath(_path([(hx, hy), (hx - 0.14 * nx_ + 0.09 * dx, hy - 0.14 * ny_ + 0.09 * dy),
                                      (hx - 0.14 * nx_ - 0.09 * dx, hy - 0.14 * ny_ - 0.09 * dy)], True), _fill(COMP, a))
                elif t > ta0:
                    mx, my = (ux + bx_) / 2, (uy + by_) / 2
                    ph = (t * 2.2) % 1.0
                    for k in range(3):
                        f = (ph + k / 3) % 1.0
                        w = 0.2 * math.cos(2 * math.pi * f)
                        if math.sin(2 * math.pi * f) > 0:
                            c.drawCircle(mx + w * nx_ + (k - 1) * 0.18 * dx, my + w * ny_ + (k - 1) * 0.18 * dy, 0.03, _fill(TENS, 0.9 * a))
                c.restore()
            st.procedural(endB, endC + 0.5, 0.3, tool)
            lab1 = tag(st, -4.2, 2.1, "ROTATE: straight", TENS, 0.17)
            lab2 = tag(st, -3.75, 1.3, "SLIDE: the bend is held\nat one toolface", COMP, 0.17)
            lab3 = tag(st, -2.45, -1.55, "ROTATE: straight on the new heading", TENS, 0.17)
            st.fade_in(lab1, ta0 + 0.8, 0.4)
            st.fade_in(lab2, ta1 + 0.3, 0.4)
            st.fade_in(lab3, tb1 + 0.4, 0.4)
            # motor anatomy inset (right of the rock)
            ix, iy = 0.0, 1.55
            sub = st.text("inside the motor", 0.95, 3.0, 0.16, P.MUTED, 0.3, kind="bold")
            ins = [st.rect(ix, 2.7, 0.2, 0.5, P.STEEL, 0.2), st.rect(ix, 1.85, 0.5, 1.3, "#71839c", 0.2),
                   st.rect(ix + 0.075, 0.82, 0.48, 0.8, "#56667d", 0.2, rot=8), st.rect(ix + 0.135, 0.33, 0.6, 0.22, P.STEEL_DK, 0.2, rot=8)]
            bore = st.rect(ix, 1.85, 0.3, 1.2, P.BG, 0.21, role="hole")
            st.fade_in([sub, bore] + ins, t_motor + 0.2, 0.5)

            def rotor(c, t, look):
                a = _env(t, t_motor + 0.3, endC + 0.4, 0.4)
                if a <= 0:
                    return
                pts = [(ix + 0.09 * math.sin(2 * math.pi * (yy / 0.45) - 5.0 * t), 2.4 - yy) for yy in [i * 0.02 for i in range(56)]]
                c.drawPath(_path(pts), _stroke(P.STEEL, a, 0.07))
                for k in range(7):
                    f = ((t * 0.8) + k / 7) % 1.0
                    c.drawCircle(ix - 0.11 + 0.22 * (k % 2), 2.42 - f * 1.15, 0.03, _fill(P.MUD, a * 0.9))
                if t > t_flow:
                    for k in range(3):
                        f = ((t * 0.7) + k / 3) % 1.0
                        c.drawCircle(ix + 0.33 + f * 0.25, 0.2 + f * 0.55, 0.03, _fill(P.MUD, a * (1 - f)))
            st.procedural(t_motor + 0.2, endC + 0.5, 0.25, rotor)
            l_m = st.text("mud flow turns\nthe rotor and bit", ix + 0.45, 2.05, 0.15, P.MUD, 0.3, align="l", kind="bold")
            st.fade_in(l_m, t_flow, 0.4)
            bend_arc = st.line(_arc(ix, 1.22, 0.75, -90, -82, 6), COMP, 0.035, 0.3)
            bend_ref = st.dashed((ix, 1.22), (ix, 0.4), P.MUTED, 0.02, 0.08, 0.06, 0.25)
            l_b = st.text("slight bend in\nthe housing\n(drawn exaggerated)", ix + 0.55, 1.0, 0.15, COMP, 0.3, align="l", kind="bold")
            st.fade_in([bend_arc, l_b] + bend_ref, t_bend - 0.1, 0.4)
            st.ripple(ix + 0.02, 1.22, t_bend, t_bend + 1.0, COMP, period=0.6, r0=0.12, r1=0.5)
            mode_r = tag(st, 0.95, -0.55, "PIPE ROTATING", TENS, 0.17, align="c")
            mode_s = tag(st, 0.95, -0.55, "PIPE STILL: SLIDING", COMP, 0.17, align="c")
            st.fade_in(mode_r, ta0 + 0.2, 0.3)
            st.fade_out(mode_r, ta1 - 0.15, 0.25)
            st.fade_in(mode_s, ta1, 0.3)
            st.fade_out(mode_s, tb1 - 0.15, 0.25)
            mode_r2 = tag(st, 0.95, -0.55, "PIPE ROTATING", TENS, 0.17, align="c")
            st.fade_in(mode_r2, tb1, 0.3)
            st.fade_out([card, rock, sub, bore, l_m, bend_arc, l_b] + holes + tracks + ttl + lab1 + lab2 + lab3 + ins + bend_ref +
                        mode_r2, endC, 0.45)

        # ================================================================ the rotary steerable: pads push while it turns
        with st.span(t_rss - 0.6, endC + 0.5):
            rcx, rcy = 5.58, -0.35
            card = st.rect(5.58, -0.55, 4.3, 5.7, P.PANEL, 0.0)
            ttl = tag(st, 3.6, 1.95, "ROTARY STEERABLE · push the bit", P.TEXT, 0.16)
            rockd = st.circle(rcx, rcy, 1.6, P.ROCK, 0.05)
            holed = st.circle(rcx, rcy, 1.15, P.BG, 0.06, role="hole")
            body = st.circle(rcx, rcy, 0.6, "#71839c", 0.2)
            tv = st.text("TOP VIEW", 3.62, 1.45, 0.14, P.MUTED, 0.3, align="l", kind="bold")
            st.fade_in([card, rockd, holed, body, tv] + ttl, t_rss - 0.5, 0.5)
            t_p0 = t_pads - 0.2

            def rss(c, t, look):
                a = _env(t, t_rss - 0.4, endC + 0.4, 0.4)
                if a <= 0:
                    return
                om = 2.4 * t
                on = _ramp(t, t_p0, t_p0 + 0.6)
                for k in range(3):
                    ph = om + k * 2 * math.pi / 3
                    ext = on * 0.42 * max(0.0, math.cos(ph - math.pi)) ** 3
                    r0, r1 = 0.58, 0.72 + ext
                    ca, sa = math.cos(ph), math.sin(ph)
                    c.drawLine(rcx + r0 * ca, rcy + r0 * sa, rcx + r1 * ca, rcy + r1 * sa, _stroke("#c9d4e1", a, 0.26, cap=False))
                    if ext > 0.38:
                        c.drawCircle(rcx + 1.15 * ca, rcy + 1.15 * sa, 0.08, _fill(COMP, a * min(1.0, (ext - 0.38) / 0.04)))
                mk = om
                c.drawLine(rcx, rcy, rcx + 0.45 * math.cos(mk), rcy + 0.45 * math.sin(mk), _stroke(P.STEEL, a, 0.06))
                arcp = [(rcx + 0.85 * math.cos(math.radians(d)), rcy + 0.85 * math.sin(math.radians(d))) for d in range(20, 140, 6)]
                c.drawPath(_path(arcp), _stroke(TENS, 0.8 * a, 0.035))
                hx, hy = arcp[-1]
                c.drawPath(_path([(hx - 0.02, hy + 0.11), (hx - 0.08, hy - 0.09), (hx + 0.1, hy - 0.04)], True), _fill(TENS, 0.8 * a))
            st.procedural(t_rss - 0.6, endC + 0.5, 0.3, rss)
            sf = st.arrow(rcx + 0.1, rcy, rcx + 1.05, rcy, COMP, 0.08, 0.24, 0.45)
            sfl = st.text("side force\non the bit", 7.65, rcy - 1.55, 0.15, COMP, 0.45, align="r", kind="bold")
            pl = st.text("pad pushes\non the wall", 3.6, rcy - 1.55, 0.15, P.TEXT, 0.45, align="l", kind="bold")
            st.fade_in(sf + [sfl, pl], t_pads + 0.4, 0.4)
            stx = tag(st, rcx, -2.85, "steers while the whole string turns", P.TEXT, 0.16, align="c")
            st.fade_in(stx, t_turns - 0.2, 0.4)
            st.fade_out([card, rockd, holed, body, tv, sfl, pl] + stx + ttl + sf, endC, 0.45)

        # ================================================================ the PDC bit: shearing like a lathe tool
        # grid: bit face (left) | one cutter, side view (centre, full height) | a lathe tool on steel (right, below the cards)
        with st.span(endC, b.end):
            bfx, bfy, bfr = -4.45, 1.85, 1.15

            def bitface(c, t, look):
                a = _env(t, endC + 0.2, b.end + 1.0, 0.4)
                if a <= 0:
                    return
                rot = -0.9 * t
                c.drawCircle(bfx, bfy, bfr, _fill("#3a4456", a))
                c.drawCircle(bfx, bfy, bfr, _stroke("#98a9bf", a, 0.03))
                for k in range(5):
                    ang = rot + k * 2 * math.pi / 5
                    ca, sa = math.cos(ang), math.sin(ang)
                    nxx, nyy = -sa, ca
                    blade = [(bfx + 0.16 * ca - 0.14 * nxx, bfy + 0.16 * sa - 0.14 * nyy), (bfx + (bfr - 0.05) * ca - 0.17 * nxx, bfy + (bfr - 0.05) * sa - 0.17 * nyy),
                             (bfx + (bfr - 0.05) * ca + 0.17 * nxx, bfy + (bfr - 0.05) * sa + 0.17 * nyy), (bfx + 0.16 * ca + 0.14 * nxx, bfy + 0.16 * sa + 0.14 * nyy)]
                    c.drawPath(_path(blade, True), _fill("#71839c", a))
                    for j in range(4):
                        rr = 0.36 + j * 0.24
                        x, y = bfx + rr * ca + 0.08 * nxx, bfy + rr * sa + 0.08 * nyy
                        c.drawCircle(x, y, 0.085, _fill("#1d2129", a))
                        c.drawCircle(x, y, 0.085, _stroke("#c9d4e1", a, 0.02))
                    nz = ang + math.pi / 5
                    c.drawCircle(bfx + 0.6 * math.cos(nz), bfy + 0.6 * math.sin(nz), 0.06, _fill(P.BG, a))
                c.drawCircle(bfx, bfy, 0.17, _fill("#56667d", a))
                # the cutter shown in close-up is highlighted on the face
                if t > t_pdc + 0.6:
                    ang = rot
                    x, y = bfx + 1.08 * math.cos(ang) + 0.08 * -math.sin(ang), bfy + 1.08 * math.sin(ang) + 0.08 * math.cos(ang)
                    c.drawCircle(x, y, 0.15, _stroke(P.WARN, a * _ramp(t, t_pdc + 0.6, t_pdc + 1.0), 0.035))
            st.procedural(endC, b.end, 0.2, bitface)
            bl = st.text("PDC bit, seen from below", bfx, bfy - bfr - 0.32, 0.18, P.TEXT, 0.4, kind="bold")
            bl2 = st.text("diamond cutters on steel blades", bfx, bfy - bfr - 0.66, 0.15, P.MUTED, 0.4)
            st.fade_in([bl, bl2], t_pdc + 0.1, 0.4)
            cl = pill(st, bfx, -1.3, "PDC: polycrystalline\ndiamond compact", P.PANEL2, P.TEXT, 0.17)
            st.fade_in(cl, t_poly - 0.2, 0.4)

            # one cutter, side view: it moves along the rock and shears a layer off
            cbx0, cbx1 = -2.65, 3.08
            card = st.rect((cbx0 + cbx1) / 2, -0.2, cbx1 - cbx0, 6.2, P.PANEL, 0.0)
            ctl = tag(st, cbx0 + 0.18, 2.55, "ONE CUTTER · side view", P.MUTED, 0.15)
            y0, doc = -1.05, 0.3
            rockb = st.rect((cbx0 + cbx1) / 2, (y0 - 3.15) / 2, cbx1 - cbx0 - 0.2, y0 + 3.15, P.ROCK, 0.05)
            xr = cbx1 - 0.1
            x_a, x_b = -1.7, 2.05
            ta, tb = t_pdc + 0.4, b.end - 0.2
            layer = st.rect(xr, y0 + doc / 2, xr - x_a, doc, P.ROCK2, 0.06, anchor="r")
            st.fade_in([card, rockb, layer] + ctl, endC + 0.1, 0.5)
            st.scale_to(layer, ta, tb, sx=xr - x_b, interp="LINEAR")

            def cutter(c, t, look):
                a = _env(t, endC + 0.2, b.end + 1.0, 0.4)
                if a <= 0:
                    return
                f = min(max((t - ta) / (tb - ta), 0.0), 1.0)
                xc = x_a + (x_b - x_a) * f
                _shear_tool(c, t, a, (xc, y0 + 0.01), 1.25, ("#56667d", "#c4d0de", "#1d2129"), "#b49b7b", t > ta, 2.55)
                c.drawLine(cbx0 + 0.2, y0 + 0.004, xc - 0.02, y0 + 0.004, _stroke("#c9d4e1", 0.35 * a, 0.02))
            st.procedural(endC, b.end, 0.3, cutter)
            dl = st.text("depth of cut", xr - 0.12, y0 + doc + 0.25, 0.15, P.MUTED, 0.3, align="r")
            dbr = [st.line([(xr + 0.06, y0), (xr + 0.06, y0 + doc)], P.MUTED, 0.022, 0.3)]
            dt = tag(st, cbx0 + 0.18, 2.0, "diamond table, raked back", P.TEXT, 0.15)
            st.fade_in([dl] + dt + dbr, t_poly + 0.6, 0.4)
            sh = st.text("shears a layer off the rock", (cbx0 + cbx1) / 2, -2.75, 0.2, P.TEXT, 0.4, kind="bold")
            st.fade_in(sh, t_shear - 0.1, 0.4)

            # like a lathe tool: a turning steel workpiece, the same geometry
            lcx0, lcx1, lcy0, lcy1 = 3.4, 7.65, -3.3, 0.85
            lcard = st.rect((lcx0 + lcx1) / 2, (lcy0 + lcy1) / 2, lcx1 - lcx0, lcy1 - lcy0, P.PANEL, 0.0)
            ltl = tag(st, lcx0 + 0.18, lcy1 - 0.35, "LATHE TOOL · on steel", P.MUTED, 0.15)
            wx, wy, wr = 5.1, -2.05, 1.0
            st.fade_in([lcard] + ltl, t_shear + 0.3, 0.45)

            def lathe(c, t, look):
                a = _env(t, t_shear + 0.35, b.end + 1.0, 0.4)
                if a <= 0:
                    return
                c.save()
                c.clipRect(skia.Rect.MakeLTRB(lcx0 + 0.05, lcy0 + 0.05, lcx1 - 0.05, lcy1 - 0.05))
                om = 1.3 * t                                    # turning anticlockwise: the top surface runs into the tool
                rim = [(wx + (wr + 0.18) * math.cos(math.radians(d)), wy + (wr + 0.18) * math.sin(math.radians(d))) for d in range(-250, 89, 6)]
                rim += [(wx + (wr - 0.02) * math.cos(math.radians(d)), wy + (wr - 0.02) * math.sin(math.radians(d))) for d in range(88, -251, -6)]
                c.drawPath(_path(rim, True), _fill("#8c96a6", a))                 # the layer still to be cut
                c.drawCircle(wx, wy, wr, _fill("#b5c0cf", a))
                for k in range(6):
                    q = om + k * math.pi / 3
                    c.drawLine(wx + 0.25 * math.cos(q), wy + 0.25 * math.sin(q), wx + (wr - 0.08) * math.cos(q), wy + (wr - 0.08) * math.sin(q),
                               _stroke("#8c96a6", 0.8 * a, 0.03))
                c.drawCircle(wx, wy, 0.2, _fill("#56667d", a))
                _shear_tool(c, t, a, (wx, wy + wr + 0.01), 0.75, ("#56667d", "#98a9bf", "#3a4456"), "#d6dde8", True, lcy1 - 0.1)
                c.restore()
            st.procedural(t_shear + 0.3, b.end, 0.3, lathe)
            same = tag(st, lcx1 - 0.2, -0.55, "the same cut", P.TEXT, 0.17, align="r")
            st.fade_in(same, t_lathe - 0.2, 0.4)
            st.ripple(wx, wy + wr, t_lathe - 0.2, t_lathe + 0.4, P.WARN, period=0.6, r0=0.12, r1=0.6)


def _shear_tool(c, t, a, tip, sc, cols, chip_col, live, top):
    """A cutting tool raked back 20 degrees, its tip at `tip`, cutting towards +x (the work runs into it from the right):
    holder, substrate and cutting table, plus the chip curling up the rake face when `live`."""
    holder, substrate, table = cols
    rake = math.radians(20)
    fu = (-math.sin(rake), math.cos(rake))          # up the rake face
    fb = (-math.cos(rake), -math.sin(rake))         # back into the tool
    Lf, T, Td = 0.8 * sc, 0.44 * sc, 0.08 * sc
    p0 = tip
    p1 = (tip[0] + fu[0] * Lf, tip[1] + fu[1] * Lf)
    q0 = (p0[0] + fb[0] * T, p0[1] + fb[1] * T)
    q1 = (p1[0] + fb[0] * T, p1[1] + fb[1] * T)
    d0 = (p0[0] + fb[0] * Td, p0[1] + fb[1] * Td)
    d1 = (p1[0] + fb[0] * Td, p1[1] + fb[1] * Td)
    hold = [q0, (q0[0] - 0.36 * sc, q0[1] + 0.1 * sc), (q1[0] - 0.44 * sc, top), (p1[0] + 0.08 * sc, top), p1]
    c.drawPath(_path(hold, True), _fill(holder, a))
    c.drawPath(_path(hold, True), _stroke("#98a9bf", a, 0.025))
    c.drawPath(_path([d0, q0, q1, d1], True), _fill(substrate, a))
    c.drawPath(_path([p0, d0, d1, p1], True), _fill(table, a))
    c.drawLine(p0[0], p0[1], p1[0], p1[1], _stroke("#e8eef6", 0.8 * a, 0.02))
    if not live:
        return
    fn = (math.cos(rake), math.sin(rake))
    pts = []
    for k in range(26):
        u = k / 25
        if u < 0.45:
            d_ = Lf * 0.75 * u / 0.45
            pts.append((tip[0] + fu[0] * d_ + fn[0] * 0.07 * sc, tip[1] + 0.03 * sc + fu[1] * d_ + fn[1] * 0.07 * sc))
        else:
            v = (u - 0.45) / 0.55
            top_ = (tip[0] + fu[0] * Lf * 0.75 + fn[0] * 0.07 * sc, tip[1] + 0.03 * sc + fu[1] * Lf * 0.75 + fn[1] * 0.07 * sc)
            cc = (top_[0] + fn[0] * 0.2 * sc, top_[1] + fn[1] * 0.2 * sc)
            r_ = 0.2 * sc * (1 - 0.35 * v)
            th = math.atan2(top_[1] - cc[1], top_[0] - cc[0]) - 1.9 * math.pi * v
            pts.append((cc[0] + r_ * math.cos(th), cc[1] + r_ * math.sin(th)))
    c.drawPath(_path(pts), _stroke(chip_col, 0.35 * a, 0.05 * sc))
    for k in range(9):
        u = ((t * 0.9) + k / 9) % 1.0
        (qx, qy), _ = _polyline_at(pts, u * _plen(pts))
        rr = (0.06 - 0.025 * u) * sc
        rot_ = 3.0 * u + k
        frag = [(qx + rr * math.cos(rot_ + j * 2.1), qy + rr * 0.8 * math.sin(rot_ + j * 2.1)) for j in range(3)]
        c.drawPath(_path(frag, True), _fill(chip_col, a * (1 - 0.5 * u)))


# ====================================================================================================== 4.03 drag, dogleg, surveys
MU = 0.3                                     # [SIM] illustrative friction factor (badge: SIMPLIFIED)
ROPE = "#d8c7a0"
DCX, DCY, DR = -3.0, 0.55, 0.95              # capstan drum
KX, KS, KY, KR, KTH, KL3 = 1.2, 2.3, 1.0, 2.3, 50.0, 2.4   # well: x, rock top, kickoff, radius, total turn, tangent


def _eq_exp(st, x, y, base, sup, size, color, z=0.5, align="l"):
    """'base' with a superscript 'sup' (e.g. e^(mu theta)); returns (objects, width)."""
    wb = st.measure(base, size, "bold")
    ws = st.measure(sup, size * 0.66, "bold")
    x0 = x if align == "l" else x - (wb + ws + 0.03) / 2
    a = st.text(base, x0, y, size, color, z, align="l", kind="bold")
    b_ = st.text(sup, x0 + wb + 0.03, y + size * 0.48, size * 0.66, color, z, align="l", kind="bold")
    return [a, b_], wb + ws + 0.03


def _well_pts():
    seg1 = [(KX, KS), (KX, KY)]
    arc = [(KX + KR - KR * math.cos(math.radians(a)), KY - KR * math.sin(math.radians(a))) for a in [KTH * i / 40 for i in range(41)]]
    d = (math.sin(math.radians(KTH)), -math.cos(math.radians(KTH)))
    e = arc[-1]
    return seg1 + arc[1:] + [(e[0] + d[0] * KL3, e[1] + d[1] * KL3)]


def _arc_pt(a, r=KR):
    return (KX + KR - r * math.cos(math.radians(a)), KY - r * math.sin(math.radians(a)))


def beat_drag(st, tl):
    b = tl["4.03"]
    s = b.sent
    t_pull, t_cap, t_mult, t_emu, t_tot = W(b, 1, "Pulling pipe"), W(b, 1, "capstan"), W(b, 1, "multiplies"), W(b, 1, "e to the mu"), W(b, 1, "total angle")
    t_sharp, t_deg, t_dls = s[2], W(b, 2, "degrees per thirty"), W(b, 2, "dogleg severity")
    t_rot, t_flex, t_fat, t_lim = s[3], W(b, 3, "flexed"), W(b, 3, "fatigue"), W(b, 3, "limit")
    t_mwd, t_inc, t_dir, t_comp = s[4], W(b, 4, "inclination"), W(b, 4, "direction"), W(b, 4, "compute")
    t_err, t_ell, t_far = s[5], W(b, 5, "an ellipse"), W(b, 5, "farther")
    path = _well_pts()
    Lp = _plen(path)
    view = View(st, b.start, b.end, z=0.2)
    with st.span(b.start, b.end):
        # ================================================================ the curved well (in the content camera)
        with view:
            rock = st.rect(2.7, (KS - 2.9) / 2, 5.0, KS + 2.9, P.ROCK, 0.0)
            floor = st.rect(KX, KS + 0.42, 1.3, 0.08, P.STEEL_DK, 0.25)
            hole = st.line(path, P.BG, 0.36, 0.05, role="flat")
            st.fade_in([rock, floor], b.start + 0.05, 0.5)
            st.draw_on(hole, b.start + 0.3, s[0] + 1.6, "BEZIER")
            # the pipe, pulled against the inside of the bend while it is pulled out
            pp = [(KX, KS + 0.4), (KX, KY)]
            for i in range(1, 41):
                a = KTH * i / 40
                off = 0.1 * min(1.0, a / 8.0, (KTH - a) / 8.0)
                pp.append(_arc_pt(a, KR - off))
            pp.append(path[-1])
            pipe = st.line(pp, P.STEEL, 0.11, 0.1, role="flat")
            st.draw_on(pipe, s[0] + 0.6, s[0] + 2.0, "BEZIER")
            st.flow(list(reversed(pp)), t_pull, t_rot - 0.3, P.STEEL, n=16, speed=0.55, r=0.045, z=0.12, glow=False)
            drags = []
            for a in (10, 22, 34, 46):
                (x, y) = _arc_pt(a, KR - 0.05)
                d = (math.sin(math.radians(a)), -math.cos(math.radians(a)))
                nrm = (math.cos(math.radians(a)), math.sin(math.radians(a)))       # toward the arc centre
                x, y = x + nrm[0] * 0.2, y + nrm[1] * 0.2
                drags += st.arrow(x - d[0] * 0.2, y - d[1] * 0.2, x + d[0] * 0.25, y + d[1] * 0.25, P.BAD, 0.05, 0.15, 0.3)
            dl = tag(st, _arc_pt(28, KR - 0.6)[0] + 0.1, _arc_pt(28, KR - 0.6)[1] + 0.05, "drag", P.BAD, 0.16)
            st.fade_in(drags + dl, t_pull + 0.8, 0.4)
            t2 = st.arrow(KX, KS + 0.5, KX, KS + 1.15, TENS, 0.07, 0.2, 0.3)
            t2l = st.text("T₂ at the hook", KX + 0.2, KS + 0.85, 0.17, TENS, 0.3, align="l", kind="bold")
            dd = (math.sin(math.radians(KTH)), -math.cos(math.radians(KTH)))
            e = _arc_pt(KTH)
            t1 = st.arrow(e[0] + dd[0] * 0.15, e[1] + dd[1] * 0.15, e[0] + dd[0] * 0.75, e[1] + dd[1] * 0.75, TENS, 0.05, 0.16, 0.3)
            t1l = st.text("T₁", e[0] + dd[0] * 0.5 + 0.22, e[1] + dd[1] * 0.5 + 0.2, 0.17, TENS, 0.3, align="l", kind="bold")
            st.fade_in(t2 + [t2l] + t1 + [t1l], t_pull + 0.4, 0.4)
            # theta: the total turn, between the tangent before and after the bend
            ix_, iy_ = KX, KY - (KX - e[0]) / dd[0] * dd[1] * -1.0
            iy_ = e[1] + (KX - e[0]) / dd[0] * dd[1]
            ext1 = st.dashed((KX, KY), (KX, iy_ - 0.6), P.MUTED, 0.025, 0.1, 0.07, 0.3)
            ext2 = st.dashed(e, (KX - dd[0] * 0.5, iy_ - dd[1] * 0.5), P.MUTED, 0.025, 0.1, 0.07, 0.3)
            tha = st.line(_arc(KX, iy_, 0.7, 270, 270 + KTH, 20), P.WARN, 0.05, 0.31)
            thl = st.text("θ: total turn", KX - 0.2, iy_ - 0.55, 0.17, P.WARN, 0.31, align="r", kind="bold")
            st.fade_in(ext1 + ext2, t_tot - 0.3, 0.3)
            st.draw_on(tha, t_tot - 0.1, t_tot + 0.6, "BEZIER")
            st.fade_in(thl, t_tot + 0.2, 0.4)
            st.fade_out(ext1 + ext2 + [tha, thl] + drags + dl + t2 + [t2l] + t1 + [t1l], t_sharp - 0.4, 0.4)

            # ---- dogleg severity: change of direction over a 30 m course
            a1, a2 = 12.0, 38.0
            ticks = []
            dirs = []
            for a in (a1, a2):
                (x, y) = _arc_pt(a)
                ticks.append(st.circle(x, y, 0.06, P.WARN, 0.33))
                d = (math.sin(math.radians(a)), -math.cos(math.radians(a)))           # direction of the hole here
                o = _arc_pt(a, KR + 0.5)                                              # drawn just outside the bend
                dirs.append((o, d))
                ticks += [st.line([(x, y), o], P.WARN, 0.018, 0.32, alpha=0.6)]
                ticks += st.arrow(o[0], o[1], o[0] + d[0] * 0.75, o[1] + d[1] * 0.75, P.WARN, 0.035, 0.12, 0.33)
            (o2, d2), (o1, d1) = dirs[1], dirs[0]
            ghost = st.dashed(o2, (o2[0] + d1[0] * 0.75, o2[1] + d1[1] * 0.75), P.MUTED, 0.025, 0.08, 0.06, 0.32)
            ang = st.line(_arc(o2[0], o2[1], 0.5, math.degrees(math.atan2(d1[1], d1[0])), math.degrees(math.atan2(d2[1], d2[0])), 12),
                          P.WARN, 0.03, 0.33)
            angl = st.text("change of\ndirection", o2[0] - 0.12, o2[1] - 0.5, 0.1, P.WARN, 0.33, align="r", kind="bold")
            ticks += ghost + [ang, angl]
            br = st.line([_arc_pt(a, KR - 0.3) for a in [a1 + (a2 - a1) * i / 16 for i in range(17)]], P.TEXT, 0.025, 0.32)
            brl = st.text("30 m", _arc_pt((a1 + a2) / 2, KR - 0.6)[0], _arc_pt((a1 + a2) / 2, KR - 0.6)[1], 0.17, P.TEXT, 0.32, kind="bold")
            st.fade_in(ticks, t_sharp + 0.6, 0.4)
            st.fade_in([br, brl], t_deg, 0.4)
            # ---- rotating pipe in the bend: one fibre swings from stretched to squeezed on every turn
            t_f0 = t_rot

            def fibre(c, t, look):
                a_ = _env(t, t_f0, t_mwd - 0.3, 0.4)
                if a_ <= 0:
                    return
                v = math.cos(2 * math.pi * 0.9 * (t - t_f0))
                pts = []
                for i in range(41):
                    aa = 4 + (KTH - 8) * i / 40
                    pts.append(_arc_pt(aa, KR - 0.05 * v))
                colr = TENS if v > 0 else COMP
                c.drawPath(_path(pts), _glow(look, colr, a_ * abs(v), 0.035))
                c.drawPath(_path(pts), _stroke(colr, a_ * (0.35 + 0.65 * abs(v)), 0.035))
            st.procedural(t_f0, t_mwd, 0.4, fibre)
            crack = st.line([(_arc_pt(26, KR + 0.06)[0] + dx_, _arc_pt(26, KR + 0.06)[1] + dy_) for dx_, dy_ in
                             ((0.0, 0.0), (-0.07, -0.03), (-0.04, -0.09), (-0.11, -0.13))], P.BAD, 0.035, 0.45)
            st.draw_on(crack, t_fat, t_fat + 0.4, "BEZIER")
            st.fade_out(ticks + [br, brl, crack], t_mwd - 0.6, 0.4)

            # ---- MWD: inclination at the tool, survey stations along the path
            mt = (e[0] + dd[0] * 1.6, e[1] + dd[1] * 1.6)
            mwd = st.line([(mt[0] - dd[0] * 0.3, mt[1] - dd[1] * 0.3), (mt[0] + dd[0] * 0.3, mt[1] + dd[1] * 0.3)], "#98a9bf", 0.2, 0.15, role="flat")
            mdot = st.circle(mt[0], mt[1], 0.055, P.SAFE, 0.16)
            ml = tag(st, mt[0] + 0.35, mt[1] + 0.35, "MWD sensors", P.TEXT, 0.16)
            st.fade_in([mwd, mdot] + ml, t_mwd + 0.6, 0.4)
            vref = st.dashed(mt, (mt[0], mt[1] - 1.0), P.MUTED, 0.025, 0.1, 0.07, 0.3)
            inc = st.line(_arc(mt[0], mt[1], 0.6, 270, 270 + KTH, 20), P.WARN, 0.045, 0.31)
            incl = st.text("inclination", mt[0] + 0.32, mt[1] - 0.95, 0.16, P.WARN, 0.31, align="l", kind="bold")
            st.fade_in(vref, t_inc - 0.3, 0.3)
            st.draw_on(inc, t_inc - 0.1, t_inc + 0.5, "BEZIER")
            st.fade_in(incl, t_inc + 0.1, 0.4)
            stations = [i * 0.5 for i in range(1, int((Lp - 0.1) / 0.5) + 1)]
            st_t = [t_comp + (t_err - 0.2 - t_comp) * k / len(stations) for k in range(len(stations))]
            for sv, tt in zip(stations, st_t):
                (x, y), _ = _polyline_at(path, sv)
                o = st.circle(x, y, 0.055, P.WARN, 0.34)
                st.pop_in(o, tt, 0.3)

        # ---- view: push in on the bend for the dogleg, back out for the survey
        mid = _arc_pt(KTH / 2)
        view.camera(t_sharp - 0.3, t_sharp + 1.3, focus=mid, at=(0.8, 0.15), scale=1.9)
        view.home(t_mwd - 0.5, t_mwd + 0.8)

        # ================================================================ the capstan (screen space, left)
        tc0 = t_cap - 0.4
        endcap = t_sharp - 0.4
        with st.span(tc0, endcap + 0.5):
            drum = st.circle(DCX, DCY, DR, "#71839c", 0.2)
            hub = st.ring(DCX, DCY, 0.25, 0.05, P.STEEL, 0.21)
            cap_t = st.text("a rope round a capstan", -5.9, 3.35, 0.22, P.TEXT, 0.3, align="l", kind="bold")
            st.fade_in([drum, hub, cap_t], tc0, 0.4)
            th0, th1 = t_cap + 0.6, t_emu + 0.6

            def theta(t):                     # wrap angle grows from a quarter turn to two-thirds of a turn
                return math.radians(90 + 150 * _ramp(t, th0, th1))

            def rope(c, t, look):
                a = _env(t, tc0, endcap + 0.4, 0.4)
                if a <= 0:
                    return
                th = theta(t)
                r = DR + 0.045
                y_top = DCY + 0.75
                pts = [(DCX - r, y_top), (DCX - r, DCY)]
                n = 40
                for i in range(1, n + 1):      # the rope arrives down the left side and wraps on round the drum
                    ang = math.pi + th * i / n
                    pts.append((DCX + r * math.cos(ang), DCY + r * math.sin(ang)))
                al = math.pi + th
                dvec = (-math.sin(al), math.cos(al))
                tail = (pts[-1][0] + dvec[0] * 0.8, pts[-1][1] + dvec[1] * 0.8)
                pts.append(tail)
                c.drawPath(_path(pts), _stroke("#7a6a4a", a, 0.12))
                c.drawPath(_path(pts), _stroke(ROPE, a, 0.08))
                ratio = math.exp(MU * th)
                L2 = 0.35 * ratio
                # T2 (hauling end, left) and T1 (holding end): arrows point away from the drum, lengths ~ tension
                for (x0, y0, ux, uy, L, lab) in ((DCX - r, y_top, 0.0, 1.0, L2, "T₂"), (tail[0], tail[1], dvec[0], dvec[1], 0.35, "T₁")):
                    x1, y1 = x0 + ux * L, y0 + uy * L
                    c.drawLine(x0, y0, x1 - ux * 0.12, y1 - uy * 0.12, _glow(look, TENS, a, 0.06))
                    c.drawLine(x0, y0, x1 - ux * 0.12, y1 - uy * 0.12, _stroke(TENS, a, 0.06))
                    c.drawPath(_path([(x1, y1), (x1 - ux * 0.2 - uy * 0.11, y1 - uy * 0.2 + ux * 0.11),
                                      (x1 - ux * 0.2 + uy * 0.11, y1 - uy * 0.2 - ux * 0.11)], True), _fill(TENS, a))
                    if lab == "T₂":
                        look.draw_text(c, "T₂: pulling", x1 - 0.2, y1 - 0.1, 0.19, TENS, a, "r", "bold")
                    else:
                        mx_, my_ = (pts[-2][0] + tail[0]) / 2 + math.cos(al) * 0.45, (pts[-2][1] + tail[1]) / 2 + math.sin(al) * 0.45
                        look.draw_text(c, "T₁: holding", mx_, my_, 0.19, TENS, a, "c", "bold")
                deg = math.degrees(th)
                look.draw_text(c, f"θ = {deg:3.0f}°", DCX - 0.15, DCY - DR - 0.75, 0.22, P.WARN, a, "r", "mono")
                look.draw_text(c, f"T₂ = {ratio:3.1f} × T₁", DCX + 0.15, DCY - DR - 0.75, 0.22, TENS, a, "l", "mono")
            st.procedural(tc0, endcap + 0.5, 0.3, rope)
            eq, w_ = _eq_exp(st, DCX, -1.85, "T₂ = T₁ · e", "μθ", 0.36, P.TEXT, 0.5, align="c")
            leg = st.text("μ: friction factor (0.3 here)   θ: total angle turned", DCX, -2.45, 0.15, P.MUTED, 0.5)
            st.fade_in(eq, t_emu - 0.1, 0.4)
            st.fade_in(leg, t_emu + 0.6, 0.4)
            st.fade_out([drum, hub, cap_t, leg] + eq, endcap, 0.45)

        # ================================================================ dogleg + fatigue (screen space, left)
        with st.span(t_sharp, t_mwd + 0.2):
            dls = [st.text("DOGLEG SEVERITY", -5.95, 3.35, 0.24, P.TEXT, 0.5, align="l", kind="bold"),
                   st.text("how sharply the hole bends:", -5.95, 2.92, 0.17, P.MUTED, 0.5, align="l")]
            unit = st.text("° per 30 m", -5.95, 2.35, 0.42, P.WARN, 0.5, align="l", kind="bold")
            st.fade_in(dls, t_sharp + 0.5, 0.4)
            st.fade_in(unit, t_deg, 0.4)
            # cross-section of the rotating pipe + the stress on one fibre
            cx_, cy_ = -4.6, -0.45
            ring = st.ring(cx_, cy_, 0.42, 0.13, "#98a9bf", 0.4)
            o_l = st.text("outside of the bend", cx_, cy_ + 0.68, 0.14, TENS, 0.4, kind="bold")
            i_l = st.text("inside", cx_, cy_ - 0.68, 0.14, COMP, 0.4, kind="bold")
            ax = [st.line([(-3.9, cy_), (-2.0, cy_)], P.MUTED, 0.02, 0.4)]
            sl = [st.text("stretched", -2.95, cy_ + 0.62, 0.14, TENS, 0.4), st.text("squeezed", -2.95, cy_ - 0.62, 0.14, COMP, 0.4)]
            cap2 = st.text("every turn: one full load cycle", -3.75, cy_ - 1.2, 0.16, P.TEXT, 0.4, kind="bold")
            st.fade_in([ring, o_l, i_l] + ax, t_rot + 0.1, 0.4)
            st.fade_in(cap2, t_flex + 0.4, 0.4)
            T0 = t_rot + 0.2

            def trace(c, t, look):
                a = _env(t, t_rot + 0.1, t_mwd - 0.3, 0.4)
                if a <= 0:
                    return
                ph = 2 * math.pi * 0.9 * (t - t_f0)
                fx, fy = cx_ + 0.36 * math.cos(ph), cy_ + 0.36 * math.sin(ph)
                v = math.sin(ph)
                c.drawCircle(fx, fy, 0.08, _fill(TENS if v > 0 else COMP, a))
                span_t = 3.2
                x0, x1 = -3.85, -2.05
                pts = []
                for i in range(0, 81):
                    tt = t - span_t + span_t * i / 80
                    if tt < T0:
                        continue
                    vv = math.sin(2 * math.pi * 0.9 * (tt - t_f0))
                    pts.append((x0 + (x1 - x0) * i / 80, cy_ + 0.4 * vv, vv))
                for (xa, ya, va), (xb, yb, vb) in zip(pts[:-1], pts[1:]):
                    colr = TENS if (va + vb) > 0 else COMP
                    c.drawLine(xa, ya, xb, yb, _stroke(colr, a, 0.04))
                if pts:
                    c.drawCircle(pts[-1][0], pts[-1][1], 0.05, _fill(TENS if pts[-1][2] > 0 else COMP, a))
            st.procedural(t_rot, t_mwd, 0.45, trace)
            sl_on = sl
            st.fade_in(sl_on, t_flex, 0.4)
            fat = tag(st, -5.95, -2.45, "fatigue cracks", "#ffffff", 0.18, bg=P.BAD)
            st.fade_in(fat, t_fat, 0.35)
            lim = tag(st, -3.9, -2.45, "so: limit the dogleg severity", P.WARN, 0.18)
            st.fade_in(lim, t_lim - 0.1, 0.4)
            st.fade_out(dls + [unit, ring, o_l, i_l, cap2] + ax + sl + fat + lim, t_mwd - 0.6, 0.4)

        # ================================================================ plan view: direction and the growing uncertainty
        with st.span(t_mwd, b.end):
            pcx, pcy = -3.5, -0.75
            card = st.rect(pcx, pcy, 4.9, 4.7, P.PANEL, 0.0)
            pv = tag(st, -5.8, 1.27, "PLAN VIEW · from above", P.MUTED, 0.15)
            nxp, nyp = -1.45, 0.8
            north = st.arrow(nxp, nyp - 0.25, nxp, nyp + 0.3, P.TEXT, 0.035, 0.15, 0.4) + [st.text("N", nxp, nyp - 0.45, 0.16, P.TEXT, 0.4, kind="bold")]
            st.fade_in([card] + pv + north, t_mwd + 0.8, 0.45)
            w0 = (-5.0, 0.55)
            az = math.radians(120)
            dvec = (math.sin(az), math.cos(az))
            wh = _platform(st, *w0, r=0.12)
            st.fade_in(wh, t_mwd + 1.1, 0.4)
            nref = st.dashed(w0, (w0[0], w0[1] + 0.8), P.MUTED, 0.025, 0.1, 0.07, 0.3)
            azl = st.line(_arc(w0[0], w0[1], 0.55, 90, 90 - 120, 24), P.WARN, 0.045, 0.31)
            azt = st.text("direction", w0[0] + 0.62, w0[1] + 0.35, 0.16, P.WARN, 0.31, align="l", kind="bold")
            st.fade_in(nref, t_dir - 0.2, 0.3)
            st.draw_on(azl, t_dir, t_dir + 0.6, "BEZIER")
            st.fade_in(azt, t_dir + 0.2, 0.4)
            ppts = []
            for sv in stations:
                (x, y), _ = _polyline_at(path, sv)
                hd = (x - KX) * 1.15
                ppts.append((w0[0] + dvec[0] * hd, w0[1] + dvec[1] * hd, sv))
            pl = st.line([w0] + [(p[0], p[1]) for p in ppts], P.WARN, 0.05, 0.32)
            st.draw_on(pl, st_t[0], st_t[-1] + 0.3, "LINEAR")
            for (x, y, sv), tt in zip(ppts, st_t):
                o = st.circle(x, y, 0.05, P.WARN, 0.34)
                st.pop_in(o, tt, 0.3)
            rot = math.degrees(math.atan2(dvec[1], dvec[0])) + 90

            def ellipses(c, t, look):
                a = _env(t, t_err, b.end + 1.0, 0.5)
                if a <= 0:
                    return
                g = 0.25 + 0.75 * _ramp(t, t_err + 0.2, t_ell + 1.5)
                for (x, y, sv), tt in zip(ppts, st_t):
                    big = (0.05 + 0.1 * sv) * g
                    pts = _ell_pts(x, y, big, big * 0.55, rot)
                    c.drawPath(_path(pts, True), _fill(P.WARN, 0.07 * a))
                    c.drawPath(_path(pts, True), _stroke(P.WARN, 0.75 * a, 0.022))
            st.procedural(t_err, b.end, 0.3, ellipses)
            far = tag(st, pcx, -2.75, "uncertainty grows with distance drilled", P.WARN, 0.17, align="c")
            st.fade_in(far, t_far - 0.3, 0.4)
            surv = st.text("survey stations: angles → path", pcx, -2.2, 0.15, P.MUTED, 0.4)
            st.fade_in(surv, t_comp + 0.3, 0.4)


# ====================================================================================================== 4.04 the mud's jobs
MCX, MHW = -3.9, 0.75                       # cutaway: hole centre, half width
M_TOP, M_BOT = 3.55, -2.95                  # top of the drawing, bottom of the hole
SAND4 = (1.3, -0.3)                         # permeable sand in the wall
M_BHA, M_BIT = -1.6, -2.6


def beat_mud(st, tl):
    b = tl["4.04"]
    s = b.sent
    t_hold, t_prop, t_cake = W(b, 1, "holds back"), W(b, 1, "props up"), W(b, 1, "filter cake")
    t_cut, t_cool, t_sig = W(b, 2, "cuttings"), W(b, 2, "cools"), W(b, 2, "signals")
    t_wbm, t_obm, t_bar, t_four = W(b, 3, "water-based"), W(b, 3, "oil-based"), W(b, 3, "barite"), W(b, 3, "four times")
    t_nor, t_dump, t_ship, t_inj = s[4], W(b, 4, "may not be dumped"), W(b, 4, "shipped to shore"), W(b, 4, "injected")
    view = View(st, b.start, b.end, z=0.2, clip=(-6.05, -3.5, -1.7, 3.55))
    with st.span(b.start, b.end):
        win = st.rect(-3.875, 0.025, 4.45, 7.15, P.PANEL, 0.0)
        st.fade_in(win, b.start + 0.05, 0.4)
        with view:
            L, Rr = MCX - MHW, MCX + MHW
            rocks = []
            for x0, x1 in ((-6.1, L), (Rr, -1.6)):
                cxr, wr = (x0 + x1) / 2, x1 - x0
                rocks += [st.rect(cxr, (M_TOP + SAND4[0]) / 2, wr, M_TOP - SAND4[0], P.SHALE, 0.0),
                          st.rect(cxr, (SAND4[0] + SAND4[1]) / 2, wr, SAND4[0] - SAND4[1], P.SAND, 0.0),
                          st.rect(cxr, (SAND4[1] - 3.6) / 2, wr, SAND4[1] + 3.6, P.ROCK, 0.0)]
            rocks.append(st.rect(MCX, (M_BOT - 3.6) / 2, 2 * MHW, M_BOT + 3.6, P.ROCK, 0.0))
            hole = st.rect(MCX, (M_TOP + M_BOT) / 2, 2 * MHW, M_TOP - M_BOT, P.BG, 0.01)
            mud = st.rect(MCX, (M_TOP + M_BOT) / 2, 2 * MHW, M_TOP - M_BOT, P.MUD, 0.02, alpha=0.28, role="flat")
            pw = 0.5
            pipe = [st.rect(MCX - pw / 2 + 0.04, (M_TOP + M_BHA) / 2, 0.08, M_TOP - M_BHA, P.STEEL, 0.2),
                    st.rect(MCX + pw / 2 - 0.04, (M_TOP + M_BHA) / 2, 0.08, M_TOP - M_BHA, P.STEEL, 0.2),
                    st.rect(MCX, (M_BHA + M_BIT) / 2, 0.72, M_BHA - M_BIT, "#71839c", 0.2)]
            bit = st.poly([(MCX - 0.36, M_BIT), (MCX + 0.36, M_BIT), (MCX + MHW - 0.03, M_BIT - 0.12), (MCX + MHW - 0.03, M_BOT + 0.05),
                           (MCX - MHW + 0.03, M_BOT + 0.05), (MCX - MHW + 0.03, M_BIT - 0.12)], P.STEEL_DK, 0.21)
            st.fade_in(rocks + [hole, mud, bit] + pipe, b.start + 0.05, 0.5)
            labs = [st.text("sand", -5.95, 0.5, 0.15, P.BG, 0.3, align="l", kind="bold"),
                    st.text("shale", -5.95, 2.6, 0.15, P.MUTED, 0.3, align="l", kind="bold")]
            st.fade_in(labs, b.start + 0.6, 0.4)
            # circulation: down the pipe, out of the bit, up the annulus
            st.flow([(MCX, M_TOP + 0.1), (MCX, M_BIT + 0.05)], b.start + 0.3, b.end, P.MUD, n=16, speed=1.1, r=0.045, z=0.25)
            for sx in (-1, 1):
                ax_ = MCX + sx * (MHW - 0.2)
                st.flow([(MCX + sx * 0.12, M_BIT - 0.2), (MCX + sx * (MHW - 0.15), M_BOT + 0.12), (ax_, M_BIT + 0.1), (ax_, M_TOP + 0.1)],
                        b.start + 0.5, b.end, P.MUD, n=22, speed=1.0, r=0.04, z=0.25)
            for sx in (-1, 1):
                ax_ = MCX + sx * (MHW - 0.2)
                st.flow([(MCX + sx * 0.3, M_BOT + 0.1), (ax_, M_BIT + 0.1), (ax_, M_TOP + 0.1)], t_cut - 0.3, b.end, CUTTING,
                        n=18, speed=0.7, r=0.055, z=0.26, glow=False, jitter=0.08)

            # ---- holds back the formation fluids; props up the wall; filter cake on the sand
            pore = []
            for y in (1.0, 0.5, 0.0):
                pore += st.arrow(L - 0.75, y, L - 0.06, y, P.PORE, 0.045, 0.13, 0.3)
            mudp = []
            for y in (0.75, 0.25):
                mudp += st.arrow(MCX - 0.33, y, L + 0.04, y, P.MUD, 0.065, 0.16, 0.31)
            st.fade_in(pore, t_hold - 0.2, 0.4)
            st.fade_in(mudp, t_hold + 0.5, 0.4)
            wallp = []
            for y in (2.1, -1.0):
                wallp += st.arrow(MCX - 0.33, y, L + 0.04, y, P.MUD, 0.065, 0.16, 0.31)
            st.fade_in(wallp, t_prop - 0.1, 0.4)
            cake = st.rect(L, (SAND4[0] + SAND4[1]) / 2, 0.0001, SAND4[0] - SAND4[1], CAKE, 0.22, anchor="l", role="flat")
            cake_r = st.rect(Rr, (SAND4[0] + SAND4[1]) / 2, 0.0001, SAND4[0] - SAND4[1], CAKE, 0.22, anchor="r", role="flat")
            st.fade_in([cake, cake_r], t_cake - 0.6, 0.2)
            st.scale_to([cake, cake_r], t_cake - 0.5, t_cake + 1.2, sx=0.09)
            st.flow([(L + 0.2, 0.9), (L - 0.6, 0.85)], t_hold + 0.8, t_cake + 0.9, P.MUD, n=5, speed=0.35, r=0.03, z=0.3, alpha=0.7)
            st.flow([(L + 0.2, 0.2), (L - 0.6, 0.1)], t_hold + 1.0, t_cake + 0.9, P.MUD, n=5, speed=0.35, r=0.03, z=0.3, alpha=0.7)
            st.fade_out(pore + mudp + wallp, t_cut - 0.5, 0.4)

            # ---- cools the bit; mud-pulse signals travel up the pipe
            st.ripple(MCX, M_BOT + 0.15, t_cool - 0.1, t_cool + 1.2, TENS, period=0.6, r0=0.2, r1=0.9)

            def pulses(c, t, look):
                a = _env(t, t_sig - 0.2, b.end + 1.0, 0.3)
                if a <= 0:
                    return
                code = [1, 0, 1, 1, 0, 1, 0, 0]
                span_ = M_TOP - M_BHA
                for k, bit_ in enumerate(code * 3):
                    if not bit_:
                        continue
                    y = M_BHA + ((t - t_sig) * 1.6 - k * 0.45) % (len(code) * 3 * 0.45)
                    if M_BHA < y < M_TOP:
                        c.drawRect(skia.Rect.MakeLTRB(MCX - pw / 2 + 0.08, y - 0.06, MCX + pw / 2 - 0.08, y + 0.06), _fill("#fff1c2", 0.9 * a))
            st.procedural(t_sig - 0.2, b.end, 0.27, pulses)

        # ---- camera: push in on the sand wall, back out for the circulation
        view.camera(t_hold - 0.8, t_hold + 0.4, focus=(L, 0.55), at=(-4.35, 0.35), scale=2.1)
        view.home(t_cut - 0.7, t_cut + 0.5)

        # ---- the job list (right of the cutaway)
        endL = s[3] - 0.3
        with st.span(b.start, endL + 0.5):
            hd = st.text("What the mud does", -1.25, 3.55, 0.28, P.TEXT, 0.5, align="l", kind="bold")
            st.fade_in(hd, s[0] + 0.2, 0.4)
            rows = [("holds back the formation fluids", "mud pressure beats pore pressure", t_hold),
                    ("props up the wall", None, t_prop),
                    ("seals the sand: filter cake", "a thin skin of mud solids", t_cake),
                    ("carries cuttings up", None, t_cut),
                    ("cools the bit", None, t_cool),
                    ("carries signals to the surface", "pressure pulses in the mud", t_sig)]
            objs = [hd]
            for i, (txt, sub, t) in enumerate(rows):
                y = 2.85 - i * 0.72
                o = num_badge(st, -1.0, y, i + 1, P.MUD) + [st.text(txt, -0.65, y, 0.2, P.TEXT, 0.5, align="l", kind="bold")]
                if sub:
                    o.append(st.text(sub, -0.65, y - 0.3, 0.15, P.MUTED, 0.5, align="l"))
                st.fade_in(o, t - 0.15, 0.4)
                objs += o
            # a pulse train: the data the MWD sends up
            wave = [(-0.65, -1.55)]
            x = -0.65
            for bit_ in [1, 0, 1, 1, 0, 1, 0]:
                y = -1.35 if bit_ else -1.55
                wave += [(x, y), (x + 0.38, y)]
                x += 0.38
            wv = st.line(wave + [(x, -1.55)], P.MUD, 0.035, 0.5)
            st.draw_on(wv, t_sig + 0.2, t_sig + 1.4)
            objs.append(wv)
            st.fade_out(objs, endL, 0.45)

        # ---- water- or oil-based; barite makes it heavy
        endM = t_nor - 0.3
        with st.span(endL, endM + 0.5):
            disc = []
            for (x, lab, t, drops) in ((-0.45, "water-based", t_wbm, False), (1.7, "oil-based (deep)", t_obm, True)):
                d = st.circle(x, 2.75, 0.5, P.MUD, 0.3, role="flat", alpha=0.85)
                rim = st.ring(x, 2.75, 0.5, 0.03, P.TEXT, 0.31, alpha=0.5)
                o = [d, rim, st.text(lab, x, 2.0, 0.18, P.TEXT, 0.3, kind="bold")]
                rnd = random.Random(3 if drops else 4)
                for k in range(9):
                    rr = rnd.uniform(0.0, 0.36)
                    an = rnd.uniform(0, 2 * math.pi)
                    if drops:
                        o.append(st.ring(x + rr * math.cos(an), 2.75 + rr * math.sin(an), 0.06, 0.022, P.TEXT, 0.32, alpha=0.8))
                    else:
                        o.append(st.rect(x + rr * math.cos(an), 2.75 + rr * math.sin(an), 0.14, 0.03, CAKE, 0.32, rot=rnd.uniform(0, 180)))
                st.fade_in(o, t - 0.2, 0.4)
                disc += o
            n1 = st.text("water with clay", -0.45, 1.68, 0.14, P.MUTED, 0.3)
            n2 = st.text("brine droplets in oil", 1.7, 1.68, 0.14, P.MUTED, 0.3)
            st.fade_in(n1, t_wbm + 0.4, 0.4)
            st.fade_in(n2, t_obm + 0.6, 0.4)
            # beaker + density gauge
            bxc, byc, bw, bh = 0.2, -1.8, 1.5, 1.8
            ytop, ybot = byc + bh / 2, byc - bh / 2
            glass = [st.line([(bxc - bw / 2, ytop + 0.15), (bxc - bw / 2, ybot), (bxc + bw / 2, ybot), (bxc + bw / 2, ytop + 0.15)], P.MUTED, 0.035, 0.45)]
            liquid = st.rect(bxc, ybot + (bh - 0.2) / 2, bw - 0.06, bh - 0.2, "#e9dcae", 0.35, alpha=0.8, role="flat")
            g_x = 1.55
            track = st.rect(g_x, byc, 0.18, bh, P.GRID, 0.4, role="pill")
            fill = st.rect(g_x, ybot, 0.14, 0.0001, P.MUD, 0.41, anchor="b", role="pill")

            def gy(sg):
                return ybot + (sg - 1.0) / 1.0 * bh
            tk = []
            for v in (1.0, 1.5, 2.0):
                tk += [st.rect(g_x + 0.14, gy(v), 0.1, 0.02, P.MUTED, 0.4), st.text(f"{v:.1f}", g_x + 0.24, gy(v), 0.13, P.MUTED, 0.4, align="l")]
            gl = st.text("density (sg)", g_x, ytop + 0.28, 0.14, P.MUTED, 0.4, kind="bold")
            st.fade_in(glass + [liquid, track, fill, gl] + tk, t_bar - 1.4, 0.4)
            st.scale_to(fill, t_bar - 1.2, t_bar - 0.6, sy=gy(1.0) - ybot + 0.001)
            st.scale_to(fill, t_bar + 0.3, t_four + 1.0, sy=gy(MW) - ybot)
            st.recolor(liquid, t_bar + 0.3, t_four + 1.0, P.MUD)
            st.counter(g_x + 0.62, gy(MW) + 0.32, t_bar + 0.3, t_four + 1.0, 1.0, MW, fmt="{:.2f} sg", size=0.22, color=P.MUD, align="l", hold=endM + 0.5)
            ml = st.text("our deep-section mud", g_x + 0.62, gy(MW) + 0.0, 0.13, P.MUTED, 0.4, align="l")
            st.fade_in(ml, t_four + 0.6, 0.4)
            # barite pours in and stays suspended (it does not dissolve)
            scoop = st.poly([(bxc - 0.55, ytop + 0.72), (bxc + 0.15, ytop + 0.72), (bxc + 0.02, ytop + 0.45), (bxc - 0.42, ytop + 0.45)], "#98a9bf", 0.45)
            st.fade_in(scoop, t_bar - 0.3, 0.3)
            rnd = random.Random(9)
            grains = [(rnd.uniform(-0.6, 0.6), rnd.uniform(0.05, bh - 0.3), rnd.uniform(0, 1.2)) for _ in range(70)]

            def barite(c, t, look):
                a = _env(t, t_bar, endM + 0.4, 0.3)
                if a <= 0:
                    return
                for gx_, gyy, dly in grains:
                    t0 = t_bar + 0.2 + dly * 2.0
                    if t < t0:
                        continue
                    f = min(1.0, (t - t0) / 0.9)
                    yy = ytop + 0.42 - f * (ytop + 0.42 - (ybot + gyy))
                    xx = bxc - 0.2 + (gx_ + 0.2) * f
                    xx += 0.02 * math.sin(1.3 * t + gyy * 7)
                    c.drawCircle(xx, yy, 0.028, _fill(BARITE, 0.95 * a))
            st.procedural(t_bar, endM + 0.5, 0.42, barite)
            bl = tag(st, -1.25, 0.95, "barite ≈ 4.2 sg", P.TEXT, 0.18)
            bl2 = st.text("a mineral powder, about\nfour times as dense as water", -1.2, 0.42, 0.14, P.MUTED, 0.45, align="l")
            st.fade_in(bl, t_bar, 0.4)
            st.fade_in(bl2, t_four - 0.3, 0.4)
            st.fade_out(disc + glass + [n1, n2, liquid, track, fill, gl, ml, scoop, bl2] + tk + bl, endM, 0.45)

        # ---- Norway: oily cuttings are shipped to shore (or injected), not dumped at sea
        with st.span(endM, b.end):
            sea_y, sb_y = -0.35, -2.55
            sea = st.rect(3.15, (sea_y + sb_y) / 2, 9.2, sea_y - sb_y, P.SEA, 0.0)
            ground = st.rect(3.15, (sb_y - 3.45) / 2, 9.2, sb_y + 3.45, P.SEABED, 0.0)
            legs = [st.rect(x, (0.95 + sb_y) / 2, 0.14, 0.95 - sb_y, P.STEEL_DK, 0.1) for x in (-0.8, 1.5)]
            deck = st.rect(0.35, 1.0, 3.0, 0.2, P.STEEL_DK, 0.2)
            derrick = st.poly([(-0.25, 1.1), (0.45, 1.1), (0.2, 2.75), (0.0, 2.75)], P.STEEL, 0.15)
            shaker = st.rect(-0.7, 1.3, 0.55, 0.38, "#56667d", 0.22, role="solid")
            shl = st.text("shakers", -0.7, 1.72, 0.13, P.MUTED, 0.3, kind="bold")
            st.fade_in([sea, ground, deck, derrick, shaker, shl] + legs, endM + 0.05, 0.5)
            skl = tag(st, 1.0, 3.3, "skip of oil-coated cuttings", P.TEXT, 0.15, align="c") + \
                [st.line([(1.35, 3.1), (1.35, 1.62)], P.MUTED, 0.02, 0.3, alpha=0.8)]
            st.fade_in(skl, t_nor + 0.2, 0.4)
            chute = st.dashed((1.85, 0.95), (2.6, sea_y + 0.05), P.MUTED, 0.03, 0.12, 0.08, 0.3)
            st.fade_in(chute, t_dump - 0.6, 0.3)
            xm = [st.line([(2.05, 0.15), (2.45, 0.55)], P.BAD, 0.07, 0.5), st.line([(2.05, 0.55), (2.45, 0.15)], P.BAD, 0.07, 0.5)]
            st.draw_on(xm, t_dump - 0.1, t_dump + 0.3, "BEZIER")
            nod = tag(st, 2.75, 0.35, "no dumping at sea", "#ffffff", 0.16, bg=P.BAD)
            st.fade_in(nod, t_dump + 0.1, 0.35)
            bt = st.text("supply boat", 6.0, sea_y - 0.3, 0.14, P.TEXT, 0.35, kind="bold")
            st.fade_in(bt, t_dump + 0.4, 0.4)
            mast = st.rect(1.95, 1.85, 0.12, 1.5, P.STEEL_DK, 0.25)
            st.fade_in(mast, endM + 0.2, 0.4)
            t_lift = t_ship - 1.6
            t_l1, t_s1, t_d1, t_go = t_lift + 0.7, t_lift + 2.0, t_lift + 2.7, t_lift + 2.9
            px_, py_, Lb, ty_ = 1.95, 2.6, 3.7, 2.95
            bx0 = 5.65

            def logistics(c, t, look):
                a = _env(t, endM + 0.1, b.end + 2.0, 0.4)
                if a <= 0:
                    return
                if t < t_dump + 0.4:
                    ab = 0.0
                else:
                    ab = a * min(1.0, (t - t_dump - 0.4) / 0.4)
                boat_dx = 1.8 * _ramp(t, t_go, t_go + 2.2)
                # boat
                if ab > 0:
                    hull = [(4.9 + boat_dx, sea_y + 0.02), (7.3 + boat_dx, sea_y + 0.02), (7.7 + boat_dx, sea_y + 0.42), (4.7 + boat_dx, sea_y + 0.42)]
                    c.drawPath(_path(hull, True), _fill("#c9d4e1", ab))
                    c.drawRect(skia.Rect.MakeLTRB(6.75 + boat_dx, sea_y + 0.42, 7.3 + boat_dx, sea_y + 0.95), _fill("#98a9bf", ab))
                # crane: slews (seen side-on, the boom tip swings from over the deck to over the boat)
                ph = math.radians(99.5) * (1 - _ramp(t, t_l1, t_s1))
                tipx = px_ + Lb * math.cos(ph)
                c.drawLine(px_, py_, tipx, ty_, _stroke(P.STEEL_DK, a, 0.08))
                # skip position
                if t < t_lift:
                    sx_, sy_ = 1.35, 1.32
                elif t < t_l1:
                    sx_, sy_ = 1.35, 1.32 + 0.75 * _ramp(t, t_lift, t_l1)
                elif t < t_d1:
                    sx_, sy_ = tipx, 2.07 - (2.07 - (sea_y + 0.63)) * _ramp(t, t_s1, t_d1)
                else:
                    sx_, sy_ = bx0 + boat_dx, sea_y + 0.63
                if t_lift <= t < t_d1 + 0.2:
                    c.drawLine(tipx, ty_, sx_, sy_ + 0.21, _stroke(P.MUTED, a, 0.025))
                c.drawRect(skia.Rect.MakeLTRB(sx_ - 0.31, sy_ - 0.21, sx_ + 0.31, sy_ + 0.21), _fill("#71839c", a))
                c.drawRect(skia.Rect.MakeLTRB(sx_ - 0.26, sy_ + 0.1, sx_ + 0.26, sy_ + 0.22), _fill(CUTTING, a))
                c.drawRect(skia.Rect.MakeLTRB(sx_ - 0.26, sy_ + 0.2, sx_ + 0.26, sy_ + 0.24), _fill(P.MUD, a))
            st.procedural(endM, b.end, 0.3, logistics)
            st.fade_out(skl, t_lift, 0.3)
            st.move(bt, t_go, t_go + 2.2, dx=1.8)
            shore = tag(st, 7.6, 1.6, "to shore →", P.TEXT, 0.18, align="r")
            st.fade_in(shore, t_ship + 0.3, 0.4)
            inj = st.line([(-0.2, 0.92), (-0.2, sb_y), (-0.2, -3.3)], P.MUTED, 0.05, 0.12)
            st.fade_in(inj, t_inj - 0.4, 0.3)
            st.flow([(-0.2, 0.9), (-0.2, -3.3)], t_inj - 0.2, b.end, CUTTING, n=8, speed=1.0, r=0.05, z=0.13, glow=False)
            injl = tag(st, -0.05, -3.1, "or injected deep underground", P.TEXT, 0.15)
            st.fade_in(injl, t_inj, 0.4)


# ====================================================================================================== 4.05 ECD
E_CX, E_HW = -4.2, 0.85                 # cutaway hole centre, half width
E_TOP, E_BOT = 1.6, -2.95               # cutaway top, hole bottom
E_BHA, E_BIT = -1.55, -2.6


def beat_ecd(st, tl):
    b = tl["4.05"]
    s = b.sent
    t_on, t_gap = W(b, 1, "pumps on"), W(b, 1, "narrow gap")
    t_fric = s[2]
    t_hi = W(b, 3, "higher")
    t_emw, t_ecd = W(b, 4, "equivalent mud weight"), W(b, 4, "equivalent circulating density")
    t_off, t_stand, t_conn, t_drop = W(b, 5, "stop the pumps"), W(b, 5, "stand of pipe"), W(b, 5, "connection"), W(b, 5, "drops")
    t_on1, t_off1 = t_on + 0.2, t_off + 0.3

    def bhp(t):
        return P_STATIC + (P_ECD - P_STATIC) * (_ramp(t, t_on1, t_on1 + 1.8) - _ramp(t, t_off1, t_off1 + 1.0))

    with st.span(b.start, b.end):
        # ================================================================ rig floor (top) + hole cutaway (below a break)
        L, Rr = E_CX - E_HW, E_CX + E_HW
        floor = st.rect(E_CX, 2.35, 2.6, 0.09, P.STEEL_DK, 0.25)
        TD0, TD_UP = 2.92, 0.6                     # top drive on the string; it lifts one stand length at the connection
        t_lift0, t_lift1 = t_stand - 0.6, t_stand + 0.2
        td = st.rect(E_CX, TD0, 0.62, 0.34, P.STEEL_DK, 0.3, role="solid")
        tdl = st.text("top drive", E_CX + 0.42, TD0, 0.14, P.MUTED, 0.3, align="l", kind="bold")
        upipe = st.rect(E_CX, 2.375, 0.2, 0.75, P.STEEL, 0.2)
        pump = st.circle(-5.6, 3.05, 0.27, P.STEEL_DK, 0.3, role="solid")
        pl = st.text("pump", -5.6, 2.62, 0.14, P.MUTED, 0.3, kind="bold")
        spipe = st.line([(-5.33, 3.05), (-4.95, 3.05), (-4.95, 3.82), (E_CX, 3.82)], P.MUD, 0.06, 0.28, role="flat")

        def hose(c, t, look):                      # the hose follows the top drive up and down
            a = _env(t, b.start + 0.05, b.end + 1.0, 0.4)
            ytop = TD0 + TD_UP * _ramp(t, t_lift0, t_lift1) + 0.17
            c.drawLine(E_CX, 3.82, E_CX, ytop, _stroke(P.MUD, a, 0.06))
        st.procedural(b.start, b.end, 0.28, hose)
        zz = [st.line([(L - 0.6, y - 0.05), (Rr + 0.6, y + 0.05)], P.MUTED, 0.03, 0.3) for y in (1.82, 1.97)]
        kml = st.text("kilometres of hole", Rr + 0.7, 1.9, 0.14, P.MUTED, 0.3, align="l")
        rocks = [st.rect(L - 0.3, (E_TOP + E_BOT) / 2, 0.6, E_TOP - E_BOT, P.ROCK, 0.0), st.rect(Rr + 0.3, (E_TOP + E_BOT) / 2, 0.6, E_TOP - E_BOT, P.ROCK, 0.0),
                 st.rect(E_CX, E_BOT - 0.22, 2 * E_HW + 1.2, 0.44, P.ROCK, 0.0)]
        hole = st.rect(E_CX, (E_TOP + E_BOT) / 2, 2 * E_HW, E_TOP - E_BOT, P.BG, 0.01)
        mud = st.rect(E_CX, (E_TOP + E_BOT) / 2, 2 * E_HW, E_TOP - E_BOT, P.MUD, 0.02, alpha=0.3, role="flat")
        pw = 0.62
        pipe = [st.rect(E_CX - pw / 2 + 0.045, (E_TOP + E_BHA) / 2, 0.09, E_TOP - E_BHA, P.STEEL, 0.2),
                st.rect(E_CX + pw / 2 - 0.045, (E_TOP + E_BHA) / 2, 0.09, E_TOP - E_BHA, P.STEEL, 0.2),
                st.rect(E_CX, (E_BHA + E_BIT) / 2, 1.0, E_BHA - E_BIT, "#71839c", 0.2)]
        bit = st.poly([(E_CX - 0.5, E_BIT), (E_CX + 0.5, E_BIT), (Rr - 0.03, E_BIT - 0.12), (Rr - 0.03, E_BOT + 0.05),
                       (L + 0.03, E_BOT + 0.05), (L + 0.03, E_BIT - 0.12)], P.STEEL_DK, 0.21)
        base = [floor, td, tdl, upipe, pump, pl, spipe, kml, hole, mud, bit] + zz + rocks + pipe
        st.fade_in(base, b.start + 0.05, 0.5)
        stat_on = tag(st, -5.3, 2.1, "PUMPS ON", P.MUD, 0.16, align="c")
        stat_off = tag(st, -5.3, 2.1, "PUMPS OFF", P.MUTED, 0.16, align="c")
        stat_off2 = tag(st, -5.3, 2.1, "PUMPS OFF", P.MUTED, 0.16, align="c")
        st.fade_in(stat_off, b.start + 0.4, 0.3)
        st.fade_out(stat_off, t_on1 - 0.15, 0.2)
        st.fade_in(stat_on, t_on1, 0.25)
        st.fade_out(stat_on, t_off1 - 0.15, 0.2)
        st.fade_in(stat_off2, t_off1, 0.25)

        def impeller(c, t, look):
            a = _env(t, b.start + 0.1, b.end + 1.0, 0.4)
            ang = 7.0 * (min(t, t_off1 + 0.6) - t_on1) if t > t_on1 else 0.0
            for k in range(3):
                q = ang + k * 2 * math.pi / 3
                c.drawLine(-5.6, 3.05, -5.6 + 0.2 * math.cos(q), 3.05 + 0.2 * math.sin(q), _stroke(P.TEXT, 0.8 * a, 0.04))
        st.procedural(b.start, b.end, 0.31, impeller)
        # circulation (pumps on only)
        st.flow([(-5.33, 3.05), (-4.95, 3.05), (-4.95, 3.82), (E_CX, 3.82), (E_CX, 2.3)], t_on1, t_off1, P.MUD, n=8, speed=1.0, r=0.04, z=0.32)
        st.flow([(E_CX, E_TOP + 0.05), (E_CX, E_BIT + 0.05)], t_on1, t_off1, P.MUD, n=14, speed=1.1, r=0.045, z=0.25)
        for sx in (-1, 1):
            xa = E_CX + sx * (E_HW - 0.13)
            xb = E_CX + sx * (pw / 2 + (E_HW - pw / 2) / 2)
            st.flow([(E_CX + sx * 0.15, E_BIT - 0.2), (xa, E_BOT + 0.12), (xa, E_BHA), (xb, E_BHA + 0.15), (xb, E_TOP + 0.05)],
                    t_on1 + 0.2, t_off1, P.MUD, n=18, speed=1.0, r=0.04, z=0.25)
        # the narrow gap
        gx_ = E_CX + pw / 2 + (E_HW - pw / 2) / 2
        gap = leader(st, -2.55, 0.65, gx_, 0.4, P.TEXT)
        gapl = st.text("narrow gap", -2.5, 0.65, 0.16, P.TEXT, 0.45, align="l", kind="bold")
        st.fade_in(gap + [gapl], t_gap - 0.2, 0.4)
        # friction: short marks against the upward flow, along both walls of the annulus
        fr = []
        for y in (1.1, 0.25, -0.6, -1.35, -2.2):
            for sx in (-1, 1):
                xw = E_CX + sx * (E_HW - 0.07)
                xp = E_CX + sx * ((pw / 2 + 0.07) if y > E_BHA else 0.57)
                for x in (xw, xp):
                    fr.append(st.line([(x - 0.06, y + 0.05), (x, y - 0.03), (x + 0.06, y + 0.05)], TENS, 0.03, 0.27, alpha=0.85))
        frl = st.text("friction", -2.5, -0.35, 0.16, TENS, 0.45, align="l", kind="bold")
        frl2 = st.text("resists the flow", -2.5, -0.65, 0.14, P.MUTED, 0.45, align="l")
        st.fade_in(fr, t_fric - 0.1, 0.3)
        st.fade_in([frl, frl2], t_fric + 0.1, 0.4)
        st.fade_out(fr, t_off1, 0.4)
        st.fade_out([frl, frl2], t_off1, 0.3)
        # bottom-hole pressure read-out
        dot = st.circle(E_CX, E_BOT + 0.02, 0.06, P.TEXT, 0.4, role="solid")
        lead = st.line([(E_CX + 0.06, E_BOT + 0.02), (-2.55, E_BOT + 0.02)], P.MUTED, 0.022, 0.39)
        cap = st.text("BOTTOM-HOLE PRESSURE", -2.45, E_BOT + 0.62, 0.13, P.MUTED, 0.45, align="l", kind="bold")
        st.fade_in([dot, lead, cap], b.start + 0.6, 0.4)

        def readout(c, t, look):
            a = _env(t, b.start + 0.6, b.end + 1.0, 0.4)
            v = bhp(t)
            colr = P.MUD
            look.draw_text(c, f"{v:3.0f} bar", -2.45, E_BOT + 0.18, 0.3, colr, a, "l", "mono")
        st.procedural(b.start, b.end, 0.5, readout)

        # ================================================================ BHP vs time
        T0, T1 = s[1] - 1.0, b.end + 0.2
        c = Chart(st, 0.45, -1.9, 6.7, 3.7, (T0, T1), (595.0, 665.0))
        frm = c.frame(xticks=[], yticks=[600, 620, 640, 660], xlabel="time →", ylabel="bottom-hole pressure (bar)", fy="{:.0f}")
        st.fade_in(frm, b.start + 0.3, 0.5)
        porel = c.hline(P_PORE, P.PORE, 0.03, 0.15)
        porel_t = c.label(T0, P_PORE, f"pore pressure  {P_PORE:.0f} bar", 0.15, P.PORE, "l", "bold", dx=0.12, dy=-0.22)
        st.fade_in([porel, porel_t], b.start + 0.6, 0.4)
        stat = st.dashed(c.pt(T0, P_STATIC), c.pt(T1, P_STATIC), P.MUD, 0.035, 0.16, 0.1, 0.18)
        st.fade_in(stat, b.start + 0.7, 0.4)
        stat_t = c.label(T1, P_STATIC, f"pumps off: mud weight alone, {P_STATIC:.0f} bar", 0.15, P.MUD, "r", "bold", dx=-0.12, dy=-0.24)
        st.fade_in(stat_t, t_hi + 0.4, 0.4)

        def trace(cv, t, look):
            a = _env(t, b.start + 0.6, b.end + 1.0, 0.4)
            if a <= 0:
                return
            te = min(t, T1)
            n = max(2, int((te - T0) / 0.08))
            pts = [c.pt(T0 + (te - T0) * i / n, bhp(T0 + (te - T0) * i / n)) for i in range(n + 1)]
            pa = _path(pts)
            cv.drawPath(pa, _glow(look, P.MUD, a, 0.06))
            cv.drawPath(pa, _stroke(P.MUD, a, 0.06))
            cv.drawCircle(pts[-1][0], pts[-1][1], 0.08, _fill("#fff1c2", a))
        st.procedural(b.start + 0.4, b.end, 0.3, trace)
        # friction bracket, ECD labels
        xb_ = (t_fric + t_hi) / 2
        brk = [st.line([c.pt(xb_, P_STATIC), c.pt(xb_, P_ECD)], TENS, 0.03, 0.4)] + \
              [st.line([(c.X(xb_) - 0.08, c.Y(v)), (c.X(xb_) + 0.08, c.Y(v))], TENS, 0.03, 0.4) for v in (P_STATIC, P_ECD)]
        brl = st.text(f"+ friction ≈ {P_ECD - P_STATIC:.0f} bar", c.X(xb_) + 0.15, c.Y((P_STATIC + P_ECD) / 2), 0.15, TENS, 0.4, align="l", kind="bold")
        st.fade_in(brk + [brl], t_fric + 0.3, 0.4)
        pon = c.label(T0 + 0.5, P_ECD, "pumping", 0.16, P.MUD, "l", "bold", dx=0.0, dy=0.3)
        st.fade_in(pon, t_hi - 0.1, 0.4)
        ecd_l = tag(st, c.X(t_emw) + 0.1, c.Y(P_ECD) + 0.55, f"ECD ≈ {ECD:.2f} sg", P.MUD, 0.17)
        mw_l = st.text(f"= {MW:.2f} sg", c.X(T1) - 0.12, c.Y(P_STATIC) - 0.52, 0.15, P.MUD, 0.4, align="r", kind="bold")
        st.fade_in(mw_l, t_emw, 0.4)
        st.fade_in(ecd_l, t_ecd - 0.2, 0.4)
        eq = tag(st, 3.3, -3.32, "ECD = MW + annular friction ΔP / (g · TVD)", P.TEXT, 0.2, align="c")
        st.fade_in(eq, t_ecd + 0.6, 0.5)
        # the connection: pumps stop, a stand is added, the pressure drops
        # the top drive breaks out and lifts, a new stand swings in on top of the string, the top drive makes it up
        stand = st.rect(-2.6, TD0 + 0.13, 0.2, 0.6, P.STEEL, 0.3)
        st.fade_out(tdl, t_lift0 - 0.4, 0.3)
        st.move(td, t_lift0, t_lift1, dy=TD_UP)
        st.fade_in(stand, t_lift1 - 0.3, 0.3)
        st.move(stand, t_lift1 - 0.2, t_lift1 + 0.9, dx=E_CX + 2.6)
        st.ripple(E_CX, TD0 - 0.17, t_lift1 + 0.9, t_lift1 + 1.8, P.TEXT, period=0.6, r0=0.1, r1=0.5)
        sl_ = tag(st, E_CX + 0.4, TD0 + 0.13, "+1 stand ≈ 28 m", P.TEXT, 0.15)
        st.fade_in(sl_, t_lift1 + 0.9, 0.4)
        conn = c.label(t_off1 + 2.2, P_STATIC, "connection", 0.16, P.TEXT, "l", "bold", dy=0.3)
        st.fade_in(conn, t_conn - 0.2, 0.4)
        st.ripple(c.X(t_off1 + 0.5), c.Y(P_STATIC), t_drop - 0.4, t_drop + 0.1, P.MUD, period=0.6, r0=0.1, r1=0.6)


# ====================================================================================================== 4.06 squeezed window + MPD
WX0, WX1, WY0, WY1 = -4.45, 0.75, -3.0, 3.05          # window-chart plot area (world)
W_FULL = ((0.9, 2.0), (0.0, 4200.0))                   # the Ch 1 window chart ...
W_ZOOM = ((1.30, 1.95), (3150.0, 4200.0))              # ... zoomed on the open hole below the 9 5/8 in shoe
SWAB = 0.035                                           # [SIM] drawn only (no number): pulling pipe lowers BHP
HYP_PP, HYP_FG = 0.07, 0.06                            # [SIM] hypothetical narrower window: pore up, fracture down
P_BP = P_ECD - P_STATIC                                # MPD back pressure that replaces the lost friction (~20 bar)
HC, HHW, PHW = -3.55, 0.78, 0.22                       # MPD cutaway: hole centre, hole half width, pipe half width
Y_GL, Y_SP, Y_RCD, Y_HB = 0.3, 0.62, 1.27, -3.2        # ground, flow spool, rotating seal, hole bottom
CHK = (0.35, Y_SP)                                     # the choke on the return line


def _dash_stroke(color, alpha, width, on=0.12, off=0.08):
    p = _stroke(color, alpha, width, cap=False)
    p.setPathEffect(skia.DashPathEffect.Make([on, off], 0.0))
    return p


def beat_mpd(st, tl):
    b = tl["4.06"]
    s = b.sent
    t_sq = W(b, 0, "squeezed")
    t_off, t_pull, t_pore = W(b, 1, "pumps off"), W(b, 1, "pulling pipe"), W(b, 1, "pore pressure")
    t_on, t_frac, t_weak, t_shoe = W(b, 2, "pumps on"), W(b, 2, "fracture limit"), W(b, 2, "weakest point"), W(b, 2, "casing shoe")
    t_narrow, t_none = W(b, 3, "narrow window"), W(b, 3, "no mud weight")
    t_mpd, t_knob = s[4], W(b, 4, "knob")
    t_seal, t_turn, t_ret = W(b, 5, "rotating seal"), W(b, 5, "turning pipe"), W(b, 5, "returns")
    t_choke, t_stop, t_bp, t_hold = W(b, 5, "a choke"), W(b, 5, "pumps stop"), W(b, 5, "back pressure"), W(b, 5, "holding")
    t_alone = W(b, 6, "mud alone")
    tz0, tz1 = b.start + 0.7, t_sq + 1.0                 # zoom on the open hole
    end_w = t_mpd - 0.35                                  # the window part ends as MPD is named
    th0, th1 = t_narrow - 0.35, t_narrow + 0.75           # the hypothetical narrower window squeezes in

    def offset(t):                                       # the mud-weight pair slides left, then right: nothing fits
        return -0.05 * (_ramp(t, t_none - 0.25, t_none + 0.45) - _ramp(t, t_none + 0.75, t_none + 1.35)) \
            + 0.035 * (_ramp(t, t_none + 0.75, t_none + 1.35) - _ramp(t, t_none + 1.6, t_none + 2.0))

    def rng(t):
        f = _ramp(t, tz0, tz1)
        (xa0, xa1), (za0, za1) = W_FULL
        (xb0, xb1), (zb0, zb1) = W_ZOOM
        return (xa0 + (xb0 - xa0) * f, xa1 + (xb1 - xa1) * f), (za0 + (zb0 - za0) * f, za1 + (zb1 - za1) * f), f

    XZ = lambda v: WX0 + (v - W_ZOOM[0][0]) / (W_ZOOM[0][1] - W_ZOOM[0][0]) * (WX1 - WX0)     # zoomed mapping (static objs)
    YZ = lambda z: WY1 - (z - W_ZOOM[1][0]) / (W_ZOOM[1][1] - W_ZOOM[1][0]) * (WY1 - WY0)

    with st.span(b.start, b.end):
        # ================================================================ the window chart, zooming on the open hole
        with st.span(b.start, end_w + 0.5):
            card = st.rect((WX0 - 0.7 + WX1 + 0.12) / 2, -0.02, WX1 + 0.12 - (WX0 - 0.7), 7.25, P.PANEL, 0.0)
            ytl = st.text("depth (m)", WX0 - 0.1, WY1 + 0.3, 0.15, P.MUTED, 0.3, align="l", kind="bold")
            xtl = st.text("equivalent mud weight (sg)", (WX0 + WX1) / 2, WY0 - 0.5, 0.15, P.MUTED, 0.3, kind="bold")
            st.fade_in([card, ytl, xtl], b.start + 0.05, 0.45)

            def chart(c, t, look):
                a = _env(t, b.start + 0.1, end_w + 0.4, 0.4)
                if a <= 0:
                    return
                (x0, x1), (z0, z1), f = rng(t)
                X = lambda v: WX0 + (v - x0) / (x1 - x0) * (WX1 - WX0)
                Y = lambda z: WY1 - (z - z0) / (z1 - z0) * (WY1 - WY0)
                # grid + tick labels: the full-chart set cross-fades into the zoomed set
                for xs_, zs_, k in (((1.0, 1.2, 1.4, 1.6, 1.8, 2.0), (0, 1000, 2000, 3000, 4000), 1.0 - _ramp(f, 0.0, 0.35)),
                                    ((1.4, 1.5, 1.6, 1.7, 1.8, 1.9), (3200, 3400, 3600, 3800, 4000, 4200), _ramp(f, 0.65, 1.0))):
                    if k <= 0.01:
                        continue
                    for v in xs_:
                        if x0 - 1e-6 <= v <= x1 + 1e-6:
                            c.drawLine(X(v), WY0, X(v), WY1, _stroke(P.GRID, 0.8 * a * k, 0.012, cap=False))
                            look.draw_text(c, f"{v:.1f}", X(v), WY0 - 0.2, 0.14, P.MUTED, a * k, "c", "sans")
                    for z in zs_:
                        if z0 - 1e-6 <= z <= z1 + 1e-6:
                            c.drawLine(WX0, Y(z), WX1, Y(z), _stroke(P.GRID, 0.8 * a * k, 0.012, cap=False))
                            look.draw_text(c, f"{z:,.0f}", WX0 - 0.1, Y(z), 0.14, P.MUTED, a * k, "r", "sans")
                c.drawLine(WX0, WY0, WX1, WY0, _stroke(P.MUTED, a, 0.03, cap=False))
                c.drawLine(WX0, WY0, WX0, WY1, _stroke(P.MUTED, a, 0.03, cap=False))
                c.save()
                c.clipRect(skia.Rect.MakeLTRB(WX0, WY0, WX1, WY1))
                h = _ramp(t, th0, th1)
                dp, df = HYP_PP * h, HYP_FG * h
                zt = max(z0, M.WATER_DEPTH)
                zs = [zt + (z1 - zt) * i / 140 for i in range(141)]
                band = [(X(M.pp(z) + dp), Y(z)) for z in zs] + [(X(M.fg(z) - df), Y(z)) for z in reversed(zs)]
                c.drawPath(_path(band, True), _fill(P.SAFE, 0.32 * a))
                if h > 0:
                    for fn, colr in ((M.pp, P.PORE), (M.fg, P.FRAC)):
                        c.drawPath(_path([(X(fn(z)), Y(z)) for z in zs]), _dash_stroke(colr, 0.45 * a * h, 0.03, 0.08, 0.07))
                for fn, sh, colr in ((M.pp, dp, P.PORE), (M.fg, -df, P.FRAC)):
                    pth = _path([(X(fn(z) + sh), Y(z)) for z in zs])
                    c.drawPath(pth, _glow(look, colr, a, 0.05))
                    c.drawPath(pth, _stroke(colr, a, 0.05))
                # cased hole above the shoe (zoomed view only)
                if f > 0.01:
                    c.drawRect(skia.Rect.MakeLTRB(WX0, Y(SHOE), WX1, WY1), _fill(P.BG, 0.45 * a * f))
                    c.drawLine(WX0, Y(SHOE), WX1, Y(SHOE), _dash_stroke(P.TEXT, 0.75 * a * f, 0.025, 0.1, 0.07))
                # the two mud-weight markers: pumps off (dashed) and pumps on / ECD (solid), both amber
                o = offset(t)
                for mw, t_in, dashed in ((MW, t_off, True), (ECD, t_on, False)):
                    g = _ramp(t, t_in - 0.15, t_in + 0.9)
                    if g <= 0:
                        continue
                    xm, ya, yb = X(mw + o), Y(SHOE), Y(SHOE + g * (M.TD - SHOE))
                    pnt = _dash_stroke(P.MUD, a, 0.065, 0.16, 0.09) if dashed else _stroke(P.MUD, a, 0.065, cap=False)
                    c.drawLine(xm, ya, xm, yb, _glow(look, P.MUD, 0.7 * a, 0.05))
                    c.drawLine(xm, ya, xm, yb, pnt)
                # swab: pulling pipe out pulls the pumps-off pressure lower still
                sw = _ramp(t, t_pull - 0.1, t_pull + 0.6) * (1 - _ramp(t, t_pore + 0.4, t_pore + 1.2))
                if sw > 0:
                    xs = X(MW - SWAB * sw)
                    c.drawLine(xs, Y(SHOE), xs, Y(M.TD), _dash_stroke(P.MUD, 0.55 * a * sw, 0.04, 0.1, 0.08))
                    for zz in (3650, 3950):
                        c.drawLine(X(MW) - 0.06, Y(zz), xs + 0.07, Y(zz), _stroke(P.TEXT, 0.9 * a * sw, 0.03))
                        c.drawPath(_path([(xs, Y(zz)), (xs + 0.12, Y(zz) + 0.07), (xs + 0.12, Y(zz) - 0.07)], True), _fill(P.TEXT, a * sw))
                # where a marker breaks a limit: red (kick side: below pore; losses side: above fracture)
                if h > 0.05:
                    for z_a, z_b in ((SHOE, M.TD),):
                        bad_l, bad_r = [], []
                        for z in [z_a + (z_b - z_a) * i / 80 for i in range(81)]:
                            lo, hi = M.pp(z) + dp, M.fg(z) - df
                            bad_l.append((z, MW + o, lo) if MW + o < lo else None)
                            bad_r.append((z, ECD + o, hi) if ECD + o > hi else None)
                        for seq in (bad_l, bad_r):
                            run = []
                            for item in seq + [None]:
                                if item is None:
                                    if len(run) > 1:
                                        poly = [(X(m), Y(z)) for z, m, _ in run] + [(X(lim), Y(z)) for z, _, lim in reversed(run)]
                                        c.drawPath(_path(poly, True), _fill(P.BAD, 0.75 * a))
                                    run = []
                                else:
                                    run.append(item)
                # weakest point: the fracture limit at the last casing shoe
                gw = _ramp(t, t_weak - 0.2, t_weak + 0.4)
                if gw > 0:
                    px, py = X(M.fg(SHOE) - df), Y(SHOE)
                    c.drawCircle(px, py, 0.11, _fill(P.FRAC, a * gw))
                    c.drawCircle(px, py, 0.2, _stroke(P.FRAC, a * gw, 0.03))
                c.restore()
            st.procedural(b.start, end_w + 0.5, 0.2, chart)

            # labels in the zoomed chart
            cased = st.text("inside the 9⅝ in casing", (XZ(M.pp(3220)) + XZ(M.fg(3220))) / 2, YZ(3220), 0.15, P.MUTED, 0.3)
            shl = st.text(f"9⅝ in shoe · {SHOE:,.0f} m", XZ(M.fg(SHOE)) - 0.3, YZ(SHOE) + 0.2, 0.15, P.TEXT, 0.3, align="r", kind="bold")
            ohl = tag(st, WX0 + 0.1, YZ(4130), "OPEN HOLE", P.TEXT, 0.15)
            st.fade_in([cased, shl] + ohl, tz1 - 0.3, 0.4)
            st.fade_out(ohl, t_off - 0.2, 0.3)
            zq = 3820
            sq = st.arrow(WX0 + 0.25, YZ(zq), XZ(M.pp(zq)) - 0.15, YZ(zq), P.PORE, 0.07, 0.22, 0.4) + \
                st.arrow(WX1 - 0.1, YZ(zq), XZ(M.fg(zq)) + 0.14, YZ(zq), P.FRAC, 0.07, 0.22, 0.4)
            st.fade_in(sq, tz1 - 0.25, 0.35)
            st.fade_out(sq, t_off - 0.4, 0.35)
            st.ripple(XZ(M.fg(SHOE)), YZ(SHOE), t_weak - 0.1, t_shoe + 1.2, P.FRAC, period=0.8, r0=0.15, r1=0.75)
            hyp = tag(st, WX1, WY1 + 0.3, "HYPOTHETICAL: a narrower window", P.WARN, 0.15, align="r")
            st.fade_in(hyp, th0, 0.35)

            # the rules, one row per sentence (right column)
            rx = 1.15
            rows = []

            def row(y, swatch, title, sub, t_in, colr):
                objs = swatch + [st.text(title, rx + 0.75, y, 0.22, colr, 0.4, align="l", kind="bold"),
                                 st.text(sub, rx + 0.75, y - 0.38, 0.16, P.MUTED, 0.4, align="l")]
                st.fade_in(objs, t_in - 0.1, 0.4)
                rows.extend(objs)
                return objs
            ra = row(2.15, st.dashed((rx, 2.15), (rx + 0.5, 2.15), P.MUD, 0.065, 0.16, 0.09, 0.4),
                     f"pumps off: {MW:.2f} sg", "must still beat the pore pressure", t_off, P.MUD)
            ra2 = st.text("pulling pipe out lowers it further", rx + 0.75, 2.15 - 0.7, 0.16, P.TEXT, 0.4, align="l")
            st.fade_in(ra2, t_pull + 0.1, 0.4)
            rows.append(ra2)
            row(0.55, [st.line([(rx, 0.55), (rx + 0.5, 0.55)], P.MUD, 0.065, 0.4)],
                f"pumps on (ECD): ≈ {ECD:.2f} sg", "must stay under the fracture limit", t_on, P.MUD)
            row(-0.95, [st.circle(rx + 0.25, -0.95, 0.11, P.FRAC, 0.4), st.ring(rx + 0.25, -0.95, 0.2, 0.03, P.FRAC, 0.4)],
                "weakest point: the last casing shoe", f"{SHOE:,.0f} m · fracture ≈ {FG_SHOE:.2f} sg", t_weak, P.TEXT)
            st.fade(rows, th0, th0 + 0.5, 1.0, 0.3)
            none = pill(st, rx + 2.9, -2.35, "a narrow window: no mud weight does both", P.BAD, "#ffffff", 0.19, 0.5)
            st.pop_in(none, t_none - 0.1, 0.35)
            st.fade_out([cased, shl, hyp[0], hyp[1], card, ytl, xtl] + rows + none, end_w, 0.45)

        # ================================================================ MPD: sealed top, choke on the returns
        t0m = end_w + 0.25
        with st.span(t0m, b.end):
            ttl = st.text("MPD adds a knob", -5.85, 3.45, 0.3, P.TEXT, 0.4, align="l", kind="bold")
            st.fade_in(ttl, t_mpd, 0.4)
            L, R = HC - HHW, HC + HHW
            rock = [st.rect(L - 0.5, (Y_GL + Y_HB - 0.35) / 2, 1.0, Y_GL - Y_HB + 0.35, P.ROCK, 0.0),
                    st.rect(R + 0.5, (Y_GL + Y_HB - 0.35) / 2, 1.0, Y_GL - Y_HB + 0.35, P.ROCK, 0.0),
                    st.rect(HC, Y_HB - 0.18, 2 * HHW, 0.36, P.ROCK, 0.0)]
            hole = st.rect(HC, (Y_SP + 0.3 + Y_HB) / 2, 2 * HHW, Y_SP + 0.3 - Y_HB, P.BG, 0.01)
            mud = st.rect(HC, (Y_SP + 0.3 + Y_HB) / 2, 2 * HHW, Y_SP + 0.3 - Y_HB, P.MUD, 0.02, alpha=0.3, role="flat")
            spool = [st.rect(L - 0.17, Y_SP, 0.34, 0.62, P.STEEL_DK, 0.15), st.rect(R + 0.17, Y_SP, 0.34, 0.62, P.STEEL_DK, 0.15)]
            brk = [st.line([(L - 1.1, y - 0.05), (R + 1.1, y + 0.05)], P.MUTED, 0.03, 0.3) for y in (-0.55, -0.4)]
            brb = st.rect(HC, -0.475, 2 * HHW + 2.3, 0.13, P.BG, 0.29, role="flat")
            kml = st.text("kilometres of hole", R + 1.2, -0.475, 0.14, P.MUTED, 0.3, align="l")
            pipe = [st.rect(HC - PHW + 0.04, (3.05 + Y_HB + 0.45) / 2, 0.08, 3.05 - Y_HB - 0.45, P.STEEL, 0.2),
                    st.rect(HC + PHW - 0.04, (3.05 + Y_HB + 0.45) / 2, 0.08, 3.05 - Y_HB - 0.45, P.STEEL, 0.2)]
            bit = st.poly([(HC - 0.3, Y_HB + 0.45), (HC + 0.3, Y_HB + 0.45), (R - 0.03, Y_HB + 0.3), (R - 0.03, Y_HB + 0.04),
                           (L + 0.03, Y_HB + 0.04), (L + 0.03, Y_HB + 0.3)], P.STEEL_DK, 0.21)
            inlet = st.line([(-5.85, 3.05), (HC, 3.05)], P.STEEL, 0.14, 0.19)
            inl = st.text("mud in", -5.85, 2.75, 0.15, P.MUD, 0.3, align="l", kind="bold")
            base = rock + [hole, mud, bit, inlet, inl, brb, kml] + spool + brk + pipe
            st.fade_in(base, t0m, 0.5)
            # the rotating seal on top of the annulus, around the turning pipe
            rcd = [st.rect(HC, Y_RCD, 2 * HHW + 0.68, 0.66, P.STEEL_DK, 0.3, role="solid"),
                   st.rect(HC - PHW - 0.16, Y_RCD, 0.3, 0.5, RUBBER, 0.32, role="solid"),
                   st.rect(HC + PHW + 0.16, Y_RCD, 0.3, 0.5, RUBBER, 0.32, role="solid")]
            rcl = tag(st, HC + HHW + 0.55, Y_RCD + 0.1, "rotating seal", P.TEXT, 0.18)
            st.pop_in(rcd, t_seal - 0.15, 0.35)
            st.fade_in(rcl, t_seal + 0.1, 0.4)
            st.ripple(HC, Y_RCD, t_seal, t_seal + 1.2, P.TEXT, period=0.6, r0=0.3, r1=1.1)
            # the return line and its choke (the knob)
            rl = st.line([(R + 0.34, Y_SP), (CHK[0] - 0.3, Y_SP)], P.STEEL_DK, 0.2, 0.17)
            rl2 = st.line([(CHK[0] + 0.3, Y_SP), (1.55, Y_SP)], P.STEEL_DK, 0.2, 0.17)
            sh = st.text("to the shakers", 1.55, Y_SP - 0.35, 0.14, P.MUTED, 0.3, align="r")
            st.fade_in([rl, rl2, sh], t_mpd + 0.4, 0.4)

            def choke(c, t, look):
                a = _env(t, t_mpd + 0.3, b.end + 1.0, 0.35)
                if a <= 0:
                    return
                cx, cy = CHK
                close = _ramp(t, t_stop - 0.1, t_bp + 0.8)
                for sx in (-1, 1):
                    c.drawPath(_path([(cx, cy), (cx + sx * 0.3, cy + 0.22), (cx + sx * 0.3, cy - 0.22)], True), _fill(P.WARN, a))
                c.drawLine(cx - 0.32, cy - 0.3, cx + 0.3, cy + 0.32, _stroke(P.TEXT, a, 0.035))
                c.drawPath(_path([(cx + 0.36, cy + 0.38), (cx + 0.14, cy + 0.32), (cx + 0.3, cy + 0.16)], True), _fill(P.TEXT, a))
                # the knob above it turns as the choke closes
                kx, ky = cx, cy + 0.75
                c.drawLine(cx, cy + 0.05, kx, ky - 0.2, _stroke(P.MUTED, a, 0.04))
                c.drawCircle(kx, ky, 0.2, _fill("#3a4456", a))
                c.drawCircle(kx, ky, 0.2, _stroke(P.WARN, a, 0.035))
                ang = math.radians(135 - 200 * close)
                c.drawLine(kx, ky, kx + 0.16 * math.cos(ang), ky + 0.16 * math.sin(ang), _stroke(P.WARN, a, 0.045))
            st.procedural(t_mpd + 0.3, b.end, 0.35, choke)
            chl = tag(st, CHK[0] + 0.32, CHK[1] + 0.78, "choke", P.WARN, 0.18, align="l")
            st.fade_in(chl, t_choke, 0.4)
            st.ripple(CHK[0], CHK[1], t_knob - 0.2, t_knob + 1.0, P.WARN, period=0.6, r0=0.15, r1=0.7)

            # pumps on: down the pipe, up the annulus, out through the choke; the pipe turns
            t_pe = t_stop + 0.5
            st.flow([(-5.85, 3.05), (HC, 3.05), (HC, Y_HB + 0.5)], t0m + 0.3, t_pe, P.MUD, n=22, speed=1.1, r=0.045, z=0.25)
            st.flow([(HC + 0.48, Y_HB + 0.15), (HC + 0.48, Y_SP), (1.55, Y_SP)], t0m + 0.4, t_pe, P.MUD, n=24, speed=1.0, r=0.04, z=0.25)
            st.flow([(HC - 0.48, Y_HB + 0.15), (HC - 0.48, Y_SP + 0.1)], t0m + 0.4, t_pe, P.MUD, n=12, speed=1.0, r=0.04, z=0.25)

            def spin(c, t, look):
                a = _env(t, t0m + 0.2, b.end + 1.0, 0.35)
                if a <= 0:
                    return
                tt = min(t, t_stop + 0.6)
                c.save()
                c.clipRect(skia.Rect.MakeLTRB(HC - PHW + 0.01, Y_RCD + 0.34, HC + PHW - 0.01, 2.98))
                for k in range(4):
                    u = ((tt * 0.9) + k / 4) % 1.0
                    x = HC - PHW + 2 * PHW * u
                    c.drawLine(x, Y_RCD + 0.34, x - 0.08, 2.98, _stroke("#8a97ab", a * math.sin(math.pi * u), 0.035, cap=False))
                c.restore()
            st.procedural(t0m, b.end, 0.22, spin)
            trn = st.text("turning", HC - PHW - 0.12, 2.2, 0.15, P.MUTED, 0.3, align="r")
            st.fade_in(trn, t_turn - 0.1, 0.4)
            st.fade_out(trn, t_stop + 0.3, 0.3)

            # read-outs: back pressure at the choke, bottom-hole pressure
            bpl = st.text("BACK PRESSURE", CHK[0] - 0.75, 2.45, 0.13, P.MUTED, 0.4, align="l", kind="bold")
            st.fade_in(bpl, t_choke + 0.2, 0.4)

            def bp_read(c, t, look):
                a = _env(t, t_choke + 0.2, b.end + 1.0, 0.35)
                if a <= 0:
                    return
                v = P_BP * _ramp(t, t_stop - 0.1, t_bp + 0.8)
                look.draw_text(c, f"{v:3.0f} bar", CHK[0] - 0.75, 2.12, 0.24, P.WARN, a, "l", "mono")
            st.procedural(t_choke, b.end, 0.45, bp_read)
            dot = st.circle(HC, Y_HB + 0.04, 0.06, P.TEXT, 0.4, role="solid")
            lead = st.line([(HC + 0.06, Y_HB + 0.04), (-1.75, Y_HB + 0.04)], P.MUTED, 0.022, 0.39)
            bhl = st.text("BOTTOM-HOLE PRESSURE", -1.65, Y_HB + 0.62, 0.13, P.MUTED, 0.45, align="l", kind="bold")
            st.fade_in([dot, lead, bhl], t0m + 0.4, 0.4)
            st.counter(-1.65, Y_HB + 0.22, t0m + 0.4, t0m + 0.5, P_ECD, P_ECD, fmt="{:.0f} bar", size=0.28, color=P.MUD,
                       align="l", hold=b.end + 1.0)
            stdy = tag(st, -1.65, Y_HB - 0.3, "steady", P.MUD, 0.15)
            st.fade_in(stdy, t_hold, 0.4)

            # three lanes: pump rate falls, choke back pressure rises, bottom-hole pressure stays flat
            lx0, lx1 = 2.55, 7.45
            lanes = [(1.75, "pump rate", "#b8c4d6"), (0.05, "choke back pressure", P.WARN), (-1.65, "bottom-hole pressure", P.MUD)]
            tA, tB = t_ret - 0.4, b.end - 0.2
            lobjs = []
            for y, name, colr in lanes:
                lobjs += [st.rect((lx0 + lx1) / 2, y - 0.62, lx1 - lx0, 0.02, P.GRID, 0.3),
                          st.text(name, lx0, y + 0.18, 0.17, colr, 0.3, align="l", kind="bold")]
            tax = st.text("time →", lx1, -2.62, 0.14, P.MUTED, 0.3, align="r")
            st.fade_in(lobjs + [tax], tA - 0.3, 0.4)
            stop_x = lx0 + (lx1 - lx0) * (t_stop - tA) / (tB - tA)
            conn = [st.rect((stop_x + lx1) / 2, -0.25, lx1 - stop_x, 4.3, P.PANEL2, 0.25, alpha=0.55, role="flat"),
                    st.text("pumps stopped", stop_x + 0.08, -2.62, 0.14, P.TEXT, 0.3, align="l", kind="bold")]
            st.fade_in(conn, t_stop, 0.4)

            def lanes_draw(c, t, look):
                a = _env(t, tA - 0.3, b.end + 1.0, 0.35)
                if a <= 0 or t < tA:
                    return
                te = min(t, tB)
                n = max(2, int((te - tA) / 0.06))
                for y, name, colr in lanes:
                    pts = []
                    for i in range(n + 1):
                        tt = tA + (te - tA) * i / n
                        q = _ramp(tt, t_stop - 0.1, t_stop + 1.0)
                        g = _ramp(tt, t_stop - 0.1, t_bp + 0.8)
                        if name == "pump rate":
                            v = 0.85 * (1 - q)
                        elif name == "choke back pressure":
                            v = 0.85 * g
                        else:
                            v = 0.55
                        pts.append((lx0 + (lx1 - lx0) * (tt - tA) / (tB - tA), y - 0.55 + v * 0.5))
                    pa = _path(pts)
                    c.drawPath(pa, _glow(look, colr, a, 0.05))
                    c.drawPath(pa, _stroke(colr, a, 0.05))
                    c.drawCircle(pts[-1][0], pts[-1][1], 0.07, _fill("#ffffff", a))
            st.procedural(tA - 0.3, b.end, 0.35, lanes_draw)
            ebp = st.text(f"+{P_BP:.0f} bar", lx1, 0.05 + 0.25, 0.16, P.WARN, 0.4, align="r", kind="bold")
            st.fade_in(ebp, t_bp + 0.8, 0.4)
            ebh = st.text(f"{P_ECD:.0f} bar throughout", lx1, -1.65 + 0.18, 0.16, P.MUD, 0.4, align="r", kind="bold")
            st.fade_in(ebh, t_hold + 0.2, 0.4)

            # the mud alone is no longer the whole barrier: the envelope now takes in the sealed top and the choke
            env = [(L - 0.06, Y_HB - 0.05), (L - 0.06, 0.95), (HC - 1.18, 0.95), (HC - 1.18, Y_RCD + 0.4), (HC + 1.18, Y_RCD + 0.4),
                   (HC + 1.18, Y_SP + 0.16), (CHK[0] + 0.36, Y_SP + 0.16), (CHK[0] + 0.36, Y_SP - 0.16), (R + 0.06, Y_SP - 0.16),
                   (R + 0.06, Y_HB - 0.05), (L - 0.06, Y_HB - 0.05)]
            envl = st.line(env, P.PRIMARY_B, 0.05, 0.5, role="glow")
            st.draw_on(envl, t_alone - 0.2, t_alone + 1.6, "BEZIER")
            bl = tag(st, -1.6, -1.25, "primary barrier: mud\n+ sealed top + choke", P.PRIMARY_B, 0.16)
            st.fade_in(bl, t_alone + 0.8, 0.4)


def build(st, tl):
    F.header(st, tl)
    strings3 = ["30in conductor", "20in surface casing", "13-3/8in intermediate"]
    marks = {"4.01": SHOE13, "4.02": 2400.0, "4.03": 2800.0, "4.04": 3100.0, "4.05": SHOE}
    for bid, z in marks.items():
        bb = tl[bid]
        F.well_strip(st, 0.0 if bid == "4.01" else bb.start, bb.end, strings=strings3, marker=z)
    F.well_strip(st, tl["4.06"].start, tl.dur, strings=strings3 + ["9-5/8in intermediate"], marker=TVD)
    beat_bha(st, tl)
    beat_steering(st, tl)
    beat_drag(st, tl)
    beat_mud(st, tl)
    beat_ecd(st, tl)
    beat_mpd(st, tl)
