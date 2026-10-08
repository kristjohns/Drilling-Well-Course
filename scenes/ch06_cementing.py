"""Ch 6: Cementing.

6.01 three jobs of casing cement on a cutaway (holds, seals, shields); the seal makes it a well barrier ELEMENT.
6.02 the U-tube job, driven by ONE pumped-volume parameter V(t). Order down the string (bottom up): mud ahead | spacer |
     bottom plug | cement | top plug | displacement mud. The bottom plug's diaphragm bursts on the float collar, cement
     turns the corner at the shoe and rises in the annulus (front height = volume past the shoe / annulus area), the top
     plug bumps at the calculated volume, the shoe track stays full of cement. The pump-pressure trace is computed from
     the fluid columns (heavy cement falling down the pipe, then lifted in the annulus, then the bump).
6.03 THE DISPLACEMENT ANIMATION: a vertical slice of an eccentric annulus + its plan view. Front speed ~ gap^2 with a mud
     yield threshold (invented ratios, [SIM]): the wide side races, the narrow side stalls, a mud channel is left. Replay
     with bow-spring centralisers: steady, nearly level fronts, a clean sheath.
6.04 the 9 5/8 in job inside the window (well_model numbers): column and column + friction between pore and fracture;
     lead / tail; top of cement above Sand A. Lab: thickening time, strength, silica above about 110 C.
6.05 gel strength: the pressure the cement passes down falls below the gas-zone pressure before it is gas-tight.
6.06 how we know: job record, cement bond log (free pipe rings, bonded is damped), ultrasonic map, microannulus,
     weigh it all together with the shoe test.

Detail shots use a content-only camera (View, as in ch03): header, well strip and term cards stay put.
"""
from __future__ import annotations
import math

import skia

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common.shapes import Cutaway, pill
from scenes.common.stage import Track, as_list
from scenes.common.look import col, hex_rgb, lighten, darken, wrap_to, measure

TITLE = "Cementing"

RUBBER = "#2f2f35"           # wiper-plug rubber (not a fluid colour)
FIN = "#55555f"
LEAD = "#cbc5ba"             # lead slurry: a slightly lighter tint of cement grey (still cement, never spacer white)
SHOE_958 = [s.shoe for s in M.programme() if s.name.startswith("9-5/8")][0]      # 3,400 m
SHOE_1338 = [s.shoe for s in M.programme() if s.name.startswith("13-3/8")][0]    # 2,000 m
MW_1214 = M.section_mud_weights()["13-3/8in intermediate"]                       # 1.49 sg: mud in the 12 1/4 in hole
TOC_958 = 2600.0             # top of cement behind the 9 5/8 in (drawing value; same as ch09)
TAIL_TOP = 3100.0            # top of the tail slurry (drawing value)
RHO_LEAD, RHO_TAIL = 1.55, 1.90       # slurry densities (drawing values, never printed)
FRICTION = 0.06              # annular friction while pumping, as equivalent density (drawing value)


# ====================================================================================================== small helpers
def W(b, i, needle, frac=0.0):
    """Time `needle` is spoken in sentence i of beat b (fails loudly if the script changed)."""
    txt = b._sentences()[i]
    if needle.lower() not in txt.lower():
        raise KeyError(f"{b.id} sentence {i}: {needle!r} not in {txt!r}")
    return b.word(i, needle, frac)


def _cl(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def _sm(f):
    f = _cl(f)
    return f * f * (3 - 2 * f)


def _env(t, a, b, d=0.35):
    """Fade envelope for procedurals: 0 before a, 1 inside, 0 after b."""
    return max(0.0, min(1.0, (t - a) / d, (b - t) / d))


def _pw(t, knots):
    """Piecewise-linear function of time through (t, value) knots (constant outside)."""
    if t <= knots[0][0]:
        return knots[0][1]
    for (t0, v0), (t1, v1) in zip(knots[:-1], knots[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * (t - t0) / max(t1 - t0, 1e-9)
    return knots[-1][1]


def tag(st, x, y, text, fg=P.TEXT, size=0.2, align="l", bg=P.PANEL2, z=0.6):
    return pill(st, x, y, text, bg, fg, size, z, align=align)


def leader(st, x0, y0, x1, y1, color=P.MUTED, z=0.55):
    return [st.line([(x0, y0), (x1, y1)], color, 0.022, z, alpha=0.85), st.circle(x1, y1, 0.05, color, z + 0.01, role="disc")]


def _check(st, x, y, t, s=0.17, z=0.8, color=P.SAFE):
    """A check mark drawn on, on a round plate."""
    plate = st.circle(x, y, s * 1.45, P.PANEL2, z - 0.01, role="disc")
    ln = st.line([(x - s * 0.62, y + 0.0), (x - s * 0.15, y - s * 0.48), (x + s * 0.7, y + s * 0.55)], color, 0.06, z)
    st.pop_in(plate, t - 0.05, 0.3)
    st.draw_on(ln, t + 0.05, t + 0.45, "BEZIER")
    return [plate, ln]


def _x_mark(st, x, y, r, t, z=0.8, width=0.08):
    a = st.line([(x - r, y + r), (x + r, y - r)], P.BAD, width, z)
    c = st.line([(x - r, y - r), (x + r, y + r)], P.BAD, width, z)
    st.draw_on(a, t, t + 0.3, "BEZIER")
    st.draw_on(c, t + 0.2, t + 0.5, "BEZIER")
    return [a, c]


# ---------------------------------------------------------------------------------------------- skia helpers (procedurals)
def _paint(color, alpha, stroke=None):
    p = skia.Paint(Color=col(hex_rgb(color), _cl(alpha)), AntiAlias=True)
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def _R(x0, y0, x1, y1):
    return skia.Rect.MakeLTRB(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def _fluid(c, look, x0, y0, x1, y1, color, alpha):
    """A fluid-filled box with the engine's soft cylindrical sheen (cement gets its grain)."""
    if abs(x1 - x0) < 1e-4 or abs(y1 - y0) < 1e-4 or alpha <= 0:
        return
    rgb = hex_rgb(color)
    r = _R(x0, y0, x1, y1)
    a = _cl(alpha)
    g = skia.GradientShader.MakeLinear([skia.Point(r.left(), 0), skia.Point(r.right(), 0)],
                                       [col(darken(rgb, 0.16), a), col(lighten(rgb, 0.10), a), col(rgb, a), col(darken(rgb, 0.16), a)],
                                       [0.0, 0.35, 0.6, 1.0])
    c.drawRect(r, skia.Paint(Shader=g, AntiAlias=True))
    if color in (P.CEMENT, LEAD):
        c.drawRect(r, look._texture_paint("cement", a, 1.2, 0.0, 0.0))


def _steel(c, x0, y0, x1, y1, alpha, color=P.STEEL):
    rgb = hex_rgb(color)
    r = _R(x0, y0, x1, y1)
    g = skia.GradientShader.MakeLinear([skia.Point(r.left(), 0), skia.Point(r.right(), 0)],
                                       [col(darken(rgb, 0.35), alpha), col(lighten(rgb, 0.25), alpha), col(rgb, alpha), col(darken(rgb, 0.4), alpha)],
                                       [0.0, 0.3, 0.6, 1.0])
    c.drawRect(r, skia.Paint(Shader=g, AntiAlias=True))


def _trace(c, look, pts, color, alpha, width=0.06, dash=None, glow=True):
    if len(pts) < 2 or alpha <= 0:
        return
    rgb = hex_rgb(color)
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    if glow:
        c.drawPath(path, skia.Paint(Color=col(rgb, 0.35 * alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width * 2.4,
                                    StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join,
                                    MaskFilter=look._blur(max(3.0, width * look.k * 0.8))))
    p = skia.Paint(Color=col(rgb, alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width,
                   StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(list(dash), 0.0))
        p.setStrokeCap(skia.Paint.kButt_Cap)
    c.drawPath(path, p)


def _ppill(c, look, x, y, text, fg, alpha, size=0.18, align="l", bg=P.PANEL2):
    """Procedural pill label; returns (x_left, x_right)."""
    if alpha <= 0:
        return x, x
    pad = 0.17
    w = measure(text, size, "bold") + 2 * pad
    h = max(size * 1.18, 0.2) * 1.22 + 0.16
    x0 = x if align == "l" else (x - w / 2 if align == "c" else x - w)
    rr = _R(x0, y - h / 2, x0 + w, y + h / 2)
    c.drawRoundRect(rr, h / 2, h / 2, skia.Paint(Color=col((0, 0, 0), 0.35 * alpha), AntiAlias=True, MaskFilter=look._blur(6 * look.w / 1920)))
    c.drawRoundRect(rr, h / 2, h / 2, _paint(bg, 0.96 * alpha))
    c.drawRoundRect(rr, h / 2, h / 2, _paint(fg, 0.3 * alpha, stroke=0.012))
    look.draw_text(c, text, x0 + w / 2, y, size, fg, alpha, "c", "bold")
    return x0, x0 + w


def _plug(c, look, cx, yc, w, kind, alpha, burst=0.0, rot=0.0):
    """Rubber wiper plug centred at (cx, yc), bore width w. kind 'bottom': hollow core closed by a thin diaphragm (bursts);
    kind 'top': solid, outlined. rot in degrees (90 for a pipeline pig travelling sideways)."""
    if alpha <= 0:
        return
    HP = 0.34
    c.save()
    c.translate(cx, yc)
    if rot:
        c.rotate(rot)
    body = _R(-w * 0.36, -HP / 2, w * 0.36, HP / 2)
    c.drawRoundRect(body, 0.05, 0.05, _paint(RUBBER, alpha))
    for k in range(3):
        fy = HP / 2 - 0.045 - k * 0.115
        fin = _R(-w / 2 + 0.01, fy - 0.03, w / 2 - 0.01, fy + 0.03)
        c.drawRoundRect(fin, 0.03, 0.03, _paint(FIN, alpha))
    if kind == "top":
        c.drawRoundRect(_R(-w * 0.36, -HP / 2, w * 0.36, HP / 2), 0.05, 0.05, _paint(P.TEXT, 0.9 * alpha, stroke=0.022))
        c.drawRoundRect(_R(-w / 2 + 0.01, HP / 2 - 0.075, w / 2 - 0.01, HP / 2 - 0.015), 0.03, 0.03, _paint(P.TEXT, 0.9 * alpha, stroke=0.018))
    else:
        c.drawRect(_R(-w * 0.1, -HP / 2, w * 0.1, HP / 2), _paint(P.BG, 0.9 * alpha))
        d = 1.0 - _cl(burst)
        if d > 0:
            c.drawRect(_R(-w * 0.14, HP / 2 - 0.03, w * 0.14, HP / 2 + 0.005), _paint(P.TEXT, alpha * d))
    c.restore()


# ====================================================================================================== content camera
class View:
    """A camera for the drawing only (copied from ch03). Objects and procedurals created inside `with view:` are drawn
    through a local transform screen = world * s + d, clipped to `clip`, so the chapter furniture is unaffected."""

    def __init__(self, st, t0, t1, z=0.2, clip=(-6.32, -4.5, 8.0, 3.93)):
        self.st, self.clip = st, clip
        self.ts, self.tx, self.ty = Track(), Track(), Track()
        self.cur = (1.0, 0.0, 0.0)
        self.objs, self.procs = [], []
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
        """Show world point `focus` at screen point `at` with zoom `scale`."""
        at = focus if at is None else at
        s1, dx1, dy1 = scale, at[0] - focus[0] * scale, at[1] - focus[1] * scale
        s0, dx0, dy0 = self.cur
        for tr, a, b in ((self.ts, s0, s1), (self.tx, dx0, dx1), (self.ty, dy0, dy1)):
            tr.set(t0, a, interp)
            tr.set(t1, b, interp)
        self.cur = (s1, dx1, dy1)

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


# ====================================================================================================== 6.01 three jobs
def beat_jobs(st, tl):
    b = tl["6.01"]
    s = b.sent
    CX, YT, YB, TOC = -3.45, 3.55, -3.35, 1.55
    SY0, SY1 = -2.35, -1.35                     # a water-bearing sand in the rock
    with st.span(b.start, b.end):
        cut = Cutaway(st, CX, YT, YB, hole_w=2.5, pipe_w=1.25, wall=0.13, rock_w=1.2)
        base = cut.draw()
        hx0, hx1 = cut.hole
        sands = []
        for xc in (hx0 - 0.6, hx1 + 0.6):
            sands += [st.rect(xc, (SY0 + SY1) / 2, 1.2, SY1 - SY0, P.SAND, 0.02),
                      st.rect(xc, (SY0 + SY1) / 2, 1.2, SY1 - SY0, P.WATER, 0.03, alpha=0.38, role="flat")]
        sl = st.text("water sand", hx0 - 0.6, SY0 - 0.2, 0.15, P.WATER, 0.1, kind="bold")
        bore = cut.static_bore(P.MUD, YT, YB, 0.05, alpha=0.8)
        mud = [cut.static_gap(sd, P.MUD, YT, YB, 0.04, alpha=0.85) for sd in "lr"]
        st.fade_in(base + sands + [sl, bore] + mud, b.start, 0.5)
        # the cement sheath rises in the annulus as the beat opens
        t_c0 = s[0] - 0.1
        cem = [cut.fill_gap(sd, P.CEMENT, YB, TOC, t_c0, t_c0 + 1.8, 0.06) for sd in "lr"]
        st.fade_in(cem, t_c0, 0.15)
        gxs = [(g[0] + g[1]) / 2 for g in (cut.gap_l, cut.gap_r)]
        for gx in gxs:
            st.flow([(gx, YB + 0.1), (gx, TOC - 0.15)], t_c0, t_c0 + 1.9, P.CEMENT, n=6, speed=2.8, r=0.035, z=0.3)
        tocl = st.text("top of cement", hx0 - 0.62, TOC + 0.22, 0.14, P.MUTED, 0.1, kind="bold")
        st.fade_in(tocl, t_c0 + 1.6, 0.4)

        # ---- three rows (right)
        RX = 0.45
        kick = st.text("CEMENT HAS THREE JOBS", RX, 3.55, 0.2, P.MUTED, 0.5, align="l", kind="bold")
        st.fade_in(kick, s[0] + 0.1, 0.4)
        st.fade_out(kick, s[4] - 0.3, 0.4)
        rows = [(2.6, "01", "HOLDS", "the pipe in place: no buckling, no moving", W(b, 1, "holds")),
                (0.75, "02", "SEALS", "the gap: nothing flows along the outside", W(b, 2, "seals")),
                (-1.1, "03", "SHIELDS", "the steel from corrosive fluids", W(b, 3, "shields"))]
        row_objs = []
        for (y, n, head, sub, t) in rows:
            num = st.text(n, RX, y + 0.17, 0.24, P.MUTED, 0.5, align="l", kind="mono")
            hd = st.text(head, RX + 0.72, y + 0.17, 0.44, P.TEXT, 0.5, align="l", kind="bold")
            sb = st.text(sub, RX + 0.74, y - 0.4, 0.21, P.MUTED, 0.5, align="l")
            st.fade_in([num, hd, sb], t - 0.15, 0.45)
            row_objs.append([num, hd, sb])
        for i in (0, 1):
            st.recolor(row_objs[i][1], rows[i + 1][4] - 0.15, rows[i + 1][4] + 0.35, P.MUTED)
        # the seal is the point: rows 1 and 3 leave, row 2 rises to the top and lights up again
        st.fade_out(row_objs[0] + row_objs[2], s[4] - 0.3, 0.4)
        st.move(row_objs[1], s[4] - 0.1, s[4] + 0.7, dy=rows[0][0] - rows[1][0])
        st.recolor(row_objs[1][1], s[4] - 0.1, s[4] + 0.5, P.TEXT)

        # ---- 1: holds. Restraint arrows (cement on steel), then the ghost of a free pipe buckling, straightened
        t_hold = W(b, 1, "in place")
        rest = []
        for y in (0.9, -0.6, -2.1):
            rest += st.arrow(hx0 + 0.08, y, cut.pipe[0] - 0.03, y, P.TEXT, 0.045, 0.16, 0.3)
            rest += st.arrow(hx1 - 0.08, y, cut.pipe[1] + 0.03, y, P.TEXT, 0.045, 0.16, 0.3)
        st.fade_in(rest, t_hold - 0.1, 0.35)
        st.fade_out(rest, rows[1][4] - 0.4, 0.4)
        t_bk = W(b, 1, "buckling")

        def draw_buckle(c, t, look):
            a = _env(t, t_bk - 0.1, t_bk + 2.7, 0.35)
            if a <= 0:
                return
            amp = 0.32 * _sm((t - t_bk + 0.1) / 0.6) * (1.0 - _sm((t - t_bk - 1.4) / 1.0))
            for xw in cut.pipe:
                pts = [(xw + amp * math.sin(2 * math.pi * (YB + (YT - YB) * i / 60 - YB) / (YT - YB) * 1.0), YB + (YT - YB) * i / 60)
                       for i in range(61)]
                _trace(c, look, pts, P.BAD, 0.95 * a, 0.035, dash=(0.12, 0.08), glow=False)
            _ppill(c, look, RX + 0.74, 1.62, "without cement: free pipe buckles", P.BAD, a, 0.18)
        st.procedural(t_bk - 0.1, t_bk + 2.8, 0.45, draw_buckle)

        # ---- 2: seals. Formation water pushes in from the sand and stops at the cement; nothing runs up the annulus
        t_seal = rows[1][4]
        for sx, wall in ((-1, hx0), (1, hx1)):
            for y in (SY0 + 0.3, SY1 - 0.3):
                st.flow([(wall + sx * 1.15, y), (wall + sx * 0.03, y)], t_seal - 0.1, s[4] - 0.2, P.WATER, n=4, speed=0.55, r=0.04, z=0.3)
        gx = gxs[1]
        up = st.dashed((gx, SY1 - 0.1), (gx, 0.85), P.WATER, 0.05, 0.16, 0.1, 0.35)
        head = st.poly([(gx, 1.12), (gx - 0.13, 0.86), (gx + 0.13, 0.86)], P.WATER, 0.35, role="head")
        t_nf = W(b, 2, "nothing flows")
        st.fade_in(up + [head], t_nf - 0.5, 0.4)
        xm = _x_mark(st, gx, 0.05, 0.2, t_nf + 0.2, z=0.4)
        st.fade_out(up + [head] + xm, s[4] - 0.3, 0.4)

        # ---- 3: shields. The steel surface lights up where cement covers it
        t_sh = rows[2][4]
        shine = [st.line([(xw, YB + 0.05), (xw, TOC - 0.05)], P.TEXT, 0.045, 0.32, role="glow") for xw in cut.pipe]
        st.fade_in(shine, t_sh, 0.2)
        st.draw_on(shine, t_sh, t_sh + 1.2, "BEZIER")
        st.fade_out(shine, s[4] - 0.3, 0.4)

        # ---- the seal is the point: long enough + verified -> a well barrier element
        pt = tag(st, RX + 3.35, rows[0][0] + 0.17, "the point", P.WARN, 0.2)
        st.fade_in(pt, W(b, 4, "the point") - 0.1, 0.4)
        t_long = W(b, 4, "long enough")
        bx = hx1 + 0.2
        br = st.line([(bx + 0.12, YB + 0.08), (bx, YB + 0.08), (bx, TOC - 0.02), (bx + 0.12, TOC - 0.02)], P.SAFE, 0.04, 0.5)
        st.draw_on(br, t_long - 0.2, t_long + 0.6, "BEZIER")
        c1 = _check(st, RX + 0.2, 1.3, t_long) + [st.text("long enough", RX + 0.6, 1.3, 0.26, P.TEXT, 0.5, align="l", kind="bold")]
        st.fade_in(c1[-1], t_long, 0.35)
        t_ver = W(b, 4, "verified")
        c2 = _check(st, RX + 0.2, 0.6, t_ver) + [st.text("verified", RX + 0.6, 0.6, 0.26, P.TEXT, 0.5, align="l", kind="bold")]
        st.fade_in(c2[-1], t_ver, 0.35)
        t_be = W(b, 4, "barrier element")
        outl = []
        for g in (cut.gap_l, cut.gap_r):
            outl.append(st.line([(g[0], YB + 0.04), (g[0], TOC), (g[1], TOC), (g[1], YB + 0.04)], P.SAFE, 0.05, 0.4))
        st.draw_on(outl, t_be - 1.0, t_be + 0.2, "BEZIER")
        bep = pill(st, RX, -0.45, "casing cement = a well barrier element", P.SAFE, "#06201c", 0.26, 0.6, align="l")
        st.fade_in(bep, t_be - 0.1, 0.45)
        note = st.text("one element of a barrier envelope, with the casing above it", RX + 0.05, -1.15, 0.18, P.MUTED, 0.5, align="l")
        st.fade_in(note, t_be + 0.8, 0.45)


# ====================================================================================================== 6.02 the U-tube job
def beat_utube(st, tl):
    b = tl["6.02"]
    s = b.sent
    CX = -4.1
    YT, YFC, YS, YH = 3.55, -1.45, -2.35, -3.25
    HOLE_W, PIPE_W, WALL = 2.3, 1.1, 0.12
    HP = 0.34                                   # plug height
    U_TURN = 0.45                               # path length of the turn below the shoe
    LX = -1.95                                  # label column (screen space)

    T_circ = s[0] + 0.2
    T_sp = W(b, 1, "Spacer")
    T_bp = W(b, 2, "rubber plugs")
    T_tp = W(b, 3, "a top plug")
    T_land = W(b, 5, "pressure jumps") - 0.25
    Lfc, Ls = YT - YFC, YT - YS
    q = (Lfc - HP) / (T_land - T_tp)
    Vsp, Vc = q * (T_bp - T_sp), q * (T_tp - T_bp)
    Vfin = Vsp + Vc + Lfc - HP
    T_burst = T_bp + Lfc / q

    view = View(st, b.start, b.end, z=0.2, clip=(-6.32, -3.62, 8.0, 3.93))
    with st.span(b.start, b.end):
        with view:
            cut = Cutaway(st, CX, YT, YH, hole_w=HOLE_W, pipe_w=PIPE_W, wall=WALL, rock_w=0.85)
            base = cut.draw(pipe_bottom=YS)
            bx0, bx1 = cut.bore
            gl, gr = cut.gap_l, cut.gap_r
            hx0, hx1 = cut.hole
            r = ((gl[1] - gl[0]) + (gr[1] - gr[0])) / (bx1 - bx0)
            Umax = Ls + U_TURN + r * (YT - YS)
            mud = [cut.static_bore(P.MUD, YT, YS, 0.04, alpha=0.85), cut.static_gap("l", P.MUD, YT, YS, 0.04, alpha=0.85),
                   cut.static_gap("r", P.MUD, YT, YS, 0.04, alpha=0.85),
                   st.rect(CX, (YS + YH) / 2, HOLE_W, YS - YH, P.MUD, 0.04, alpha=0.85)]
            # float collar (thicker sub with a seat) and guide shoe (rounded nose)
            fc = [st.rect(cut.pipe[0] + WALL / 2 - 0.02, YFC - 0.12, WALL + 0.1, 0.42, P.STEEL_DK, 0.22),
                  st.rect(cut.pipe[1] - WALL / 2 + 0.02, YFC - 0.12, WALL + 0.1, 0.42, P.STEEL_DK, 0.22),
                  st.rect(bx0 + 0.07, YFC - 0.02, 0.14, 0.06, P.STEEL_DK, 0.23), st.rect(bx1 - 0.07, YFC - 0.02, 0.14, 0.06, P.STEEL_DK, 0.23)]
            shoe = [st.rect(cut.pipe[0] + WALL / 2, YS - 0.06, WALL + 0.12, 0.22, P.STEEL_DK, 0.22),
                    st.rect(cut.pipe[1] - WALL / 2, YS - 0.06, WALL + 0.12, 0.22, P.STEEL_DK, 0.22)]
            st.fade_in(base + mud + fc + shoe, b.start, 0.5)

            def V(t):
                return _cl((t - T_sp) * q, 0.0, Vfin)

            def D(t):
                return max(0.0, min(t, T_land) - T_circ) * q

            def segs(v):
                cuts = [(v - Vsp - Vc, v - Vsp, "cement"), (v - Vsp, v, "spacer")]
                return [(max(a, 0.0), bb, f) for a, bb, f in cuts if bb > max(a, 0.0)]

            def fluid_at(u, v):
                for a, bb, f in segs(v):
                    if a <= u < bb:
                        return f
                return "mud"

            FCOL = {"mud": P.MUD, "spacer": P.SPACER, "cement": P.CEMENT}

            def draw_fluids(c, t, look):
                v = V(t)
                for u0, u1, f in segs(v):
                    colr = FCOL[f]
                    a, bb = max(u0, 0.0), min(u1, Ls)
                    if bb > a:
                        _fluid(c, look, bx0, YT - bb, bx1, YT - a, colr, 1.0)
                    um = Ls + U_TURN * 0.5
                    if u0 <= um < u1:
                        _fluid(c, look, hx0, YS - 0.32, hx1, YS, colr, 1.0)
                    a, bb = max(u0, Ls + U_TURN), min(u1, Umax)
                    if bb > a:
                        h0, h1 = (a - Ls - U_TURN) / r, (bb - Ls - U_TURN) / r
                        for g in (gl, gr):
                            _fluid(c, look, g[0], YS + h0, g[1], min(YS + h1, YT), colr, 1.0)
            st.procedural(b.start, b.end, 0.1, draw_fluids)

            # particles move with the fluid, coloured by the fluid they are in
            NP = 30
            gxs = [(gl[0] + gl[1]) / 2, (gr[0] + gr[1]) / 2]

            def ppos(u, k):
                jit = ((k * 37) % 7 - 3) * 0.06
                if u <= Ls:
                    return CX + jit, YT - u
                if u <= Ls + U_TURN:
                    f = (u - Ls) / U_TURN
                    gx = gxs[k % 2]
                    return CX + jit * (1 - f) + (gx - CX) * f, YS - 0.2 * math.sin(math.pi * f)
                return gxs[k % 2] + jit * 0.4, YS + (u - Ls - U_TURN) / r

            def draw_particles(c, t, look):
                a = _env(t, T_circ, T_land + 1.2, 0.5)
                if a <= 0:
                    return
                v, d = V(t), D(t)
                groups = {}
                for k in range(NP):
                    u = (k * Umax / NP + d) % Umax
                    if u < 0.25 or u > Umax - 0.4:
                        continue
                    groups.setdefault(fluid_at(u, v), []).append(ppos(u, k))
                for f, pos in groups.items():
                    look.draw_particles(c, pos, FCOL[f], 0.045, 0.85 * a, glow=False)
            st.procedural(T_circ - 0.1, T_land + 1.4, 0.15, draw_particles)

            # plugs and the float valve poppet
            def plug_pos(t):
                v = V(t)
                ub = _cl(v - Vsp, 0.0, Lfc)
                ut = _cl(v - Vsp - Vc, 0.0, Lfc - HP)
                return YT - ub + HP / 2, YT - ut + HP / 2

            def draw_plugs(c, t, look):
                yb, yt = plug_pos(t)
                bw = bx1 - bx0
                if t >= T_bp:
                    _plug(c, look, CX, yb, bw, "bottom", _cl((t - T_bp) / 0.3), burst=_cl((t - T_burst) / 0.25))
                if t >= T_tp:
                    _plug(c, look, CX, yt, bw, "top", _cl((t - T_tp) / 0.3))
                # one-way poppet just below the float-collar seat: open (down) while fluid is pumped down, closed after
                op = 1.0 - _sm((t - T_land - 0.2) / 0.5)
                py = YFC - 0.2 - 0.12 * op
                c.drawCircle(CX, py, 0.13, _paint(P.STEEL, 1.0))
                c.drawCircle(CX, py, 0.13, _paint(P.STEEL_DK, 1.0, stroke=0.025))
                c.drawRect(_R(CX - 0.025, py - 0.3, CX + 0.025, py - 0.1), _paint(P.STEEL_DK, 1.0))
            st.procedural(b.start, b.end, 0.3, draw_plugs)
            st.ripple(CX, YFC + 0.1, T_burst, T_burst + 0.2, P.TEXT, period=0.6, r0=0.1, r1=0.6, z=0.35)
            st.ripple(CX, YFC + 0.4, T_land, T_land + 1.0, P.WARN, period=0.8, r0=0.15, r1=0.9, z=0.35)
            st.ripple(CX, YFC - 0.3, W(b, 4, "float valve") - 0.1, W(b, 4, "float valve") + 1.2, P.TEXT, period=0.7, r0=0.1, r1=0.55, z=0.35)

        # ---------------- s0: the U-tube, labelled
        t_u = W(b, 0, "U-tube")
        l_in = tag(st, LX, 2.75, "↓ down the inside", P.TEXT, 0.19)
        k_in = leader(st, LX - 0.02, 2.75, CX + 0.15, 2.75)
        l_out = tag(st, LX, 1.75, "↑ up the outside", P.TEXT, 0.19)
        k_out = leader(st, LX - 0.02, 1.75, gxs[1], 1.75)
        l_u = tag(st, LX, 0.75, "= a U-tube", P.WARN, 0.24)
        st.fade_in(l_in + k_in, W(b, 0, "down the inside") - 0.2, 0.4)
        st.fade_in(l_out + k_out, W(b, 0, "up the outside") - 0.2, 0.4)
        st.fade_in(l_u, t_u - 0.2, 0.4)
        st.fade_out(l_in + k_in + l_out + k_out + l_u, T_sp + 0.2, 0.4)

        # ---------------- fluid legend (bottom of the label column)
        leg = []
        for i, (nm, colr) in enumerate((("mud", P.MUD), ("spacer", P.SPACER), ("cement", P.CEMENT))):
            x = LX + 0.12 + i * 1.0
            leg += [st.circle(x, -3.3, 0.09, colr, 0.5, role="disc"), st.text(nm, x + 0.15, -3.3, 0.15, P.MUTED, 0.5, align="l", kind="bold")]
        st.fade_in(leg, T_sp - 0.3, 0.4)

        # ---------------- moving labels for fluids and plugs (screen space; they follow until the zoom)
        t_zoom = s[6] - 0.15

        def draw_labels(c, t, look):
            v = V(t)
            yb, yt = plug_pos(t)
            items = []
            a = _env(t, T_sp + 0.5, T_bp + 3.5)
            if a > 0 and v < Ls:
                u0, u1 = max(v - Vsp, 0.0), min(v, Ls)
                items.append([YT - (u0 + u1) / 2, "spacer", P.SPACER, a])
            a = _env(t, T_bp + 1.2, T_tp + 3.0)
            if a > 0:
                u0, u1 = max(v - Vsp - Vc, 0.0), min(v - Vsp, Lfc)
                if u1 > u0 + 0.3:
                    items.append([YT - (u0 + u1) / 2, "cement", P.CEMENT, a])
            a = _env(t, T_bp + 0.2, t_zoom)
            if a > 0:
                items.append([yb, "bottom plug (burst)" if t > T_burst + 0.2 else "bottom plug", P.TEXT, a])
            a = _env(t, T_tp + 0.2, t_zoom)
            if a > 0:
                items.append([yt, "top plug", P.TEXT, a])
            a = _env(t, W(b, 5, "float collar") - 0.2, t_zoom)
            if a > 0:
                items.append([YFC - 0.05, "float collar", P.WARN, a])
            items.sort(key=lambda it: -it[0])
            y_prev = 9.0
            for it in items:
                ty = min(it[0], y_prev - 0.47)
                y_prev = ty
                _trace(c, look, [(LX - 0.02, ty), (bx1 - 0.06, it[0])], P.MUTED, 0.85 * it[3], 0.022, glow=False)
                c.drawCircle(bx1 - 0.06, it[0], 0.05, _paint(P.MUTED, it[3]))
                _ppill(c, look, LX, ty, it[1], it[2], it[3], 0.17)
        st.procedural(T_sp, t_zoom + 0.4, 0.62, draw_labels)

        # ---------------- inset: the pipeline pig (s2-s3), then the float valve (s4)
        IX, IY, IW, IH = 1.95, 2.1, 2.4, 3.2
        t_pig = W(b, 2, "pipeline engineers") - 0.3
        t_v = s[4] - 0.1
        card1 = st.rect(IX, IY, IW, IH, P.PANEL, 0.3)
        tt1 = st.text("a pipeline pig", IX, IY + 1.3, 0.19, P.TEXT, 0.32, kind="bold")
        cap1 = st.text("pig = wiper plug", IX, IY - 1.25, 0.18, P.WARN, 0.32, kind="bold")
        st.fade_in([card1, tt1], t_pig, 0.4)
        st.fade_in(cap1, W(b, 2, "they are pigs") - 0.1, 0.4)
        st.fade_out([card1, tt1, cap1], t_v - 0.5, 0.4)

        def draw_pig(c, t, look):
            a = _env(t, t_pig, t_v - 0.1, 0.4)
            if a <= 0:
                return
            x0, x1, yc, hh = IX - 1.05, IX + 1.05, IY + 0.1, 0.34
            xp = x0 + 0.45 + 1.15 * _sm((t - t_pig - 0.3) / 4.5)
            _fluid(c, look, x0, yc - hh, xp, yc + hh, P.WATER, 0.9 * a)
            _fluid(c, look, xp, yc - hh, x1, yc + hh, P.OIL, 0.9 * a)
            _steel(c, x0, yc + hh, x1, yc + hh + 0.07, a)
            _steel(c, x0, yc - hh - 0.07, x1, yc - hh, a)
            _plug(c, look, xp, yc, 2 * hh, "top", a, rot=90)
            look.draw_text(c, "water", x0 + 0.05, yc - hh - 0.3, 0.16, P.WATER, a, "l", "bold")
            look.draw_text(c, "oil", x1 - 0.05, yc - hh - 0.3, 0.16, P.OIL, a, "r", "bold")
        st.procedural(t_pig, t_v, 0.34, draw_pig)

        card2 = st.rect(IX, IY, IW, IH, P.PANEL, 0.3)
        tt2 = st.text("float valve: one way", IX, IY + 1.3, 0.19, P.TEXT, 0.32, kind="bold")
        cap2 = st.text("heavier cement can't U-tube back", IX, IY - 1.3, 0.15, P.MUTED, 0.32, kind="bold")
        t_vend = W(b, 5, "float collar") + 0.6
        st.fade_in([card2, tt2], t_v, 0.4)
        st.fade_in(cap2, W(b, 4, "heavier") - 0.2, 0.4)
        st.fade_out([card2, tt2, cap2], t_vend, 0.4)
        t_back = W(b, 4, "U-tubing") - 0.4

        def draw_valve(c, t, look):
            a = _env(t, t_v, t_vend + 0.4, 0.4)
            if a <= 0:
                return
            xc, y0, y1, hw, wl = IX, IY - 0.95, IY + 0.85, 0.4, 0.08
            seat = IY + 0.1
            for sx in (-1, 1):          # annulus cement outside the casing, then the casing wall
                _fluid(c, look, xc + sx * (hw + wl), y0, xc + sx * (hw + wl + 0.36), y1, P.CEMENT, a)
                _steel(c, xc + sx * hw, y0, xc + sx * (hw + wl), y1, a)
            _fluid(c, look, xc - hw, y0, xc + hw, y1, P.CEMENT, a)
            c.drawRect(_R(xc - hw, seat - 0.03, xc - 0.16, seat + 0.03), _paint(P.STEEL_DK, a))
            c.drawRect(_R(xc + 0.16, seat - 0.03, xc + hw, seat + 0.03), _paint(P.STEEL_DK, a))
            close = _sm((t - t_back - 0.4) / 0.5)
            py = seat - 0.17 - 0.2 * (1 - close)
            c.drawCircle(xc, py, 0.15, _paint(P.STEEL, a))
            c.drawCircle(xc, py, 0.15, _paint(P.STEEL_DK, a, stroke=0.02))
            c.drawRect(_R(xc - 0.02, py - 0.35, xc + 0.02, py - 0.15), _paint(P.STEEL_DK, a))

            def arrow(x, ya, yb, alpha):
                _trace(c, look, [(x, ya), (x, yb)], P.TEXT, alpha, 0.04, glow=False)
                d = 1 if yb > ya else -1
                pth = skia.Path()
                pth.moveTo(x, yb + d * 0.1)
                pth.lineTo(x - 0.08, yb - d * 0.02)
                pth.lineTo(x + 0.08, yb - d * 0.02)
                pth.close()
                c.drawPath(pth, _paint(P.TEXT, alpha))
            if t < t_back:          # pumping: cement goes down the pipe, through the open valve
                pos = []
                for k in range(8):
                    f = ((t - t_v) * 0.45 + k / 8) % 1.0
                    pos.append((xc + (0.25 if k % 2 else -0.25) * math.sin(math.pi * _cl((f - 0.25) / 0.5)), y1 - 0.05 - f * (y1 - y0 - 0.1)))
                look.draw_particles(c, pos, P.TEXT, 0.035, 0.9 * a, glow=False)
                look.draw_text(c, "open", xc, y1 + 0.18, 0.15, P.TEXT, a, "c", "bold")
            else:                   # pumping stops: the heavier annulus cement falls and pushes back up inside
                g = _sm((t - t_back) / 0.6)
                for sx in (-1, 1):
                    arrow(xc + sx * (hw + wl + 0.18), y1 - 0.1, y1 - 0.1 - 0.75 * g, a * g)
                arrow(xc, y0 + 0.02, y0 + 0.02 + 0.2 * g, a * g)
                x = _cl((t - t_back - 1.0) / 0.3)
                if x > 0:
                    _trace(c, look, [(xc - 0.11, seat + 0.27), (xc + 0.11, seat + 0.05)], P.BAD, a * x, 0.05, glow=False)
                    _trace(c, look, [(xc - 0.11, seat + 0.05), (xc + 0.11, seat + 0.27)], P.BAD, a * x, 0.05, glow=False)
                    look.draw_text(c, "closed", xc, y1 + 0.18, 0.15, P.BAD, a * x, "c", "bold")
        st.procedural(t_v, t_vend + 0.5, 0.34, draw_valve)

        # ---------------- the pump-pressure trace: computed from the fluid columns
        RHO = {"spacer": 0.12, "cement": 0.85}

        def p_surf(v):
            bore = ann = 0.0
            for a, bb, f in segs(v):
                rho = RHO[f]
                bore += rho * max(0.0, min(bb, Ls) - max(a, 0.0))
                ann += rho * max(0.0, min(bb, Umax) - max(a, Ls + U_TURN)) / r
            return max(0.06, 0.24 + 0.085 * (ann - bore))

        ch = Chart(st, 2.45, -2.6, 4.7, 2.45, (0.0, Vfin * 1.12), (0.0, 1.0))
        fr = ch.frame(xticks=[], yticks=[], xlabel="volume pumped", ylabel="pump pressure", grid=False)
        t_ch = T_sp - 0.2
        st.fade_in(fr, t_ch, 0.5)
        p_end = p_surf(Vfin)

        def draw_trace(c, t, look):
            a = _env(t, t_ch + 0.2, t_zoom + 0.4, 0.5)
            if a <= 0:
                return
            v = V(t)
            n = max(2, int(80 * v / Vfin) + 2)
            pts = [ch.pt(v * i / (n - 1), p_surf(v * i / (n - 1))) for i in range(n)]
            if t > T_land:
                g = _sm((t - T_land) / 0.45)
                pts.append(ch.pt(Vfin, p_end + (0.92 - p_end) * g))
            _trace(c, look, pts, P.TEXT, a, 0.05)
            x, y = pts[-1]
            c.drawCircle(x, y, 0.07, _paint(P.TEXT, a))
        st.procedural(t_ch, b.end, 0.4, draw_trace)
        t_cv = W(b, 5, "calculated volume")
        cv = st.dashed(ch.pt(Vfin, 0.0), ch.pt(Vfin, 1.0), P.WARN, 0.03, 0.12, 0.08, 0.3)
        cvl = st.text("calculated volume", ch.X(Vfin) - 0.1, ch.Y(1.0) + 0.02, 0.15, P.WARN, 0.35, align="r", kind="bold")
        st.fade_in(cv + [cvl], t_cv - 0.2, 0.4)
        bump = tag(st, ch.X(Vfin) - 0.25, ch.Y(0.62), "plug bump: pressure jumps", P.WARN, 0.17, align="r")
        st.fade_in(bump, T_land + 0.35, 0.4)
        st.ripple(ch.X(Vfin), ch.Y(0.92), T_land + 0.4, T_land + 1.6, P.WARN, period=0.8, r0=0.08, r1=0.5)

        # ---------------- s6: push in on the shoe track (the chart and legend make room)
        st.fade_out(fr + cv + [cvl] + bump + leg, t_zoom - 0.1, 0.5)
        FOC, AT, S = (CX, -1.825), (-1.9, -0.75), 2.3
        view.camera(t_zoom, t_zoom + 1.7, FOC, AT, S)

        def scr(wx, wy):
            return AT[0] + (wx - FOC[0]) * S, AT[1] + (wy - FOC[1]) * S

        t_l = t_zoom + 1.4
        ZX = 3.0
        for wy, txt, colr, t in ((YFC + HP * 1.5, "top plug, landed", P.TEXT, t_l),
                                 (YFC, "float collar + one-way valve", P.WARN, t_l + 0.2),
                                 ((YFC + YS) / 2, "shoe track: stays full of cement", P.CEMENT, max(W(b, 6, "shoe track") - 0.1, t_l + 0.4)),
                                 (YS - 0.05, "shoe", P.MUTED, t_l + 0.6)):
            sx, sy = scr(bx1 - 0.05, wy)
            ps = tag(st, ZX, sy, txt, colr, 0.2)
            ld = leader(st, ZX - 0.02, sy, sx, sy)
            st.fade_in(ps + ld, t, 0.4)
        sx0, sy0 = scr(bx0 + 0.08, YFC - 0.03)
        sx1, sy1 = scr(bx0 + 0.08, YS + 0.03)
        brk = st.line([(sx0 + 0.15, sy0), (sx0, sy0), (sx1, sy1), (sx1 + 0.15, sy1)], P.TEXT, 0.045, 0.6)
        t_st = max(W(b, 6, "shoe track") - 0.2, t_l + 0.2)
        st.draw_on(brk, t_st, t_st + 0.6, "BEZIER")


# ====================================================================================================== stubs (filled below)
R_PIPE, D_ECC, D_CEN, G_CRIT = 0.52, 0.30, 0.05, 0.16      # pipe radius, offsets (hole radius = 1), mud yield gap [SIM]


def _gap(th, d):
    """Annular gap at azimuth th (0 = +x) for a pipe offset d towards +x (hole radius 1)."""
    return 1.0 - (d * math.cos(th) + math.sqrt(max(R_PIPE ** 2 - (d * math.sin(th)) ** 2, 0.0)))


def _vel(th, d):
    """Front speed relative to the wide side: ~ gap^2 (slot flow), zero below the gap where the mud's yield stress wins."""
    g, gw = _gap(th, d), _gap(math.pi, d)
    return max(0.0, g * g - G_CRIT ** 2) / (gw * gw - G_CRIT ** 2)


def beat_displacement(st, tl):
    b = tl["6.03"]
    s = b.sent
    SX, K = -3.75, 1.3                # slice centre, world units per hole radius
    YB, YT = -3.1, 3.35
    H = YT - YB
    RCX, RCY, KR = 1.0, 0.55, 1.12    # plan view
    h0 = RCY - YB                     # the plan view is cut at the slice height y = RCY
    WALL = 0.11
    RX = 3.5                          # caption column

    t_e0 = W(b, 1, "off-centre") + 0.3
    t_e1 = b.sent_end[1] + 0.2
    T_rw0 = s[3] - 0.05
    T_rw1 = T_rw0 + 0.9
    T_c0 = T_rw1 + 1.0
    T_c1 = min(W(b, 4, "moving the pipe"), b.end - 3.2)
    TAU_E = H * 1.12

    def tau_e(t):
        if t < T_rw0:
            f = _cl((t - t_e0) / (t_e1 - t_e0))
            return TAU_E * (0.25 * f + 0.75 * f * f)          # the front accelerates as the wide side takes the flow
        return TAU_E * (1.0 - _sm((t - T_rw0) / (T_rw1 - T_rw0)))

    def tau_c(t):
        return H * 1.12 * _cl((t - T_c0) / (T_c1 - T_c0))

    def dpos(t):
        return D_ECC + (D_CEN - D_ECC) * _sm((t - T_rw1) / 1.0)

    def fronts(th, t):
        d = dpos(t)
        v = _vel(th, d)
        if t < T_rw1:
            tau = tau_e(t)
            return v * tau, v * (tau + 0.9)
        tau = tau_c(t)
        if tau <= 0:
            return 0.0, 0.0
        hc = max(0.0, tau - 0.45 * (1.0 - v))
        return hc, hc + 0.75 * _cl(tau / 0.75)

    def fluid_h(th, y, t):
        hc, hs = fronts(th, t)
        return P.CEMENT if y < hc else (P.SPACER if y < hs else P.MUD)

    with st.span(b.start, b.end):
        # ---------------- the side-view slice
        rock = [st.rect(SX - K - 0.3, (YT + YB) / 2, 0.6, H, P.ROCK, 0.0), st.rect(SX + K + 0.3, (YT + YB) / 2, 0.6, H, P.ROCK, 0.0)]
        st.fade_in(rock, b.start, 0.5)

        def draw_slice(c, t, look):
            a = _env(t, b.start, b.end + 1, 0.5)
            d = dpos(t)
            pl, pr = SX + K * (d - R_PIPE), SX + K * (d + R_PIPE)
            for th, x0, x1 in ((math.pi, SX - K, pl), (0.0, pr, SX + K)):
                hc, hs = fronts(th, t)
                hc, hs = min(hc, H), min(hs, H)
                _fluid(c, look, x0, YB + hs, x1, YT, P.MUD, a)
                if hs > hc:
                    _fluid(c, look, x0, YB + hc, x1, YB + hs, P.SPACER, a)
                if hc > 0:
                    _fluid(c, look, x0, YB, x1, YB + hc, P.CEMENT, a)
            _fluid(c, look, pl + WALL, YB, pr - WALL, YT, P.MUD, 0.5 * a)
            _steel(c, pl, YB, pl + WALL, YT, a)
            _steel(c, pr - WALL, YB, pr, YT, a)
        st.procedural(b.start, b.end, 0.1, draw_slice)

        # particles ride with the fluid in each gap (fast on the wide side, nearly still on the narrow side)
        NPP = 9

        def draw_slice_particles(c, t, look):
            a = _env(t, t_e0 - 0.6, b.end, 0.5)
            if a <= 0:
                return
            d = dpos(t)
            pl, pr = SX + K * (d - R_PIPE), SX + K * (d + R_PIPE)
            groups = {}
            for th, x0, x1 in ((math.pi, SX - K, pl), (0.0, pr, SX + K)):
                v = _vel(th, d)
                adv = v * tau_e(t) if t < T_rw1 else tau_c(t) * (0.8 + 0.2 * v)
                for k in range(NPP):
                    y = ((k + 0.5) / NPP * H + adv * 1.0) % H
                    fx = 0.3 + 0.4 * ((k * 5) % NPP) / NPP
                    groups.setdefault(fluid_h(th, y, t), []).append((x0 + (x1 - x0) * fx, YB + y))
            for colr, pos in groups.items():
                look.draw_particles(c, pos, colr, 0.05, 0.9 * a, glow=False)
        st.procedural(b.start, b.end, 0.15, draw_slice_particles)

        # cut line and connector to the plan view
        cutl = st.dashed((SX - K, RCY), (SX + K, RCY), P.TEXT, 0.025, 0.12, 0.09, 0.3, alpha=0.6)
        conn = st.dashed((SX + K + 0.65, RCY), (RCX - KR - 0.32, RCY), P.MUTED, 0.025, 0.12, 0.09, 0.3)
        cap_s = st.text("side view", SX, YT + 0.27, 0.17, P.MUTED, 0.3, kind="bold")
        cap_p = st.text("plan view at the dashed line", RCX, RCY + KR + 0.5, 0.17, P.MUTED, 0.3, kind="bold")
        fromshoe = st.text("↑ cement comes up from the shoe", SX + 0.55, YB - 0.28, 0.15, P.MUTED, 0.3)
        st.fade_in(cutl + conn + [cap_s, cap_p, fromshoe], b.start + 0.3, 0.5)

        # ---------------- the plan view (top-down ring), cut at y = RCY
        def draw_ring(c, t, look):
            a = _env(t, b.start, b.end + 1, 0.5)
            d = dpos(t)
            c.drawCircle(RCX, RCY, KR + 0.13, _paint(P.ROCK, a, stroke=0.26))
            N = 144
            for i in range(N):
                th0, th1 = 2 * math.pi * i / N, 2 * math.pi * (i + 1.04) / N
                thm = (th0 + th1) / 2
                colr = fluid_h(thm, h0, t)
                pth = skia.Path()
                for th in (th0, th1):
                    pth.lineTo(RCX + KR * math.cos(th), RCY + KR * math.sin(th)) if th != th0 else pth.moveTo(RCX + KR * math.cos(th), RCY + KR * math.sin(th))
                for th in (th1, th0):
                    rr = (1.0 - _gap(th, d)) * KR
                    pth.lineTo(RCX + rr * math.cos(th), RCY + rr * math.sin(th))
                pth.close()
                c.drawPath(pth, skia.Paint(Color=col(hex_rgb(colr), a), AntiAlias=False))
            px = RCX + KR * d
            c.drawCircle(px, RCY, KR * R_PIPE - WALL * 0.5, _paint(P.MUD, 0.5 * a))
            c.drawCircle(px, RCY, KR * R_PIPE - WALL * 0.5, _paint(P.STEEL, a, stroke=WALL))
            c.drawCircle(RCX, RCY, KR, _paint(darken(hex_rgb(P.ROCK), 0.3), a, stroke=0.02))
        st.procedural(b.start, b.end, 0.1, draw_ring)

        # wide / narrow labels
        wl = st.text("wide", RCX - KR * 0.62, RCY, 0.16, P.BG, 0.3, kind="bold")
        nx = RCX + KR * (1.0 + D_ECC + R_PIPE) / 2
        nl = st.text("narrow", RCX + KR + 0.45, RCY - 0.75, 0.16, P.TEXT, 0.3, align="l", kind="bold")
        nld = leader(st, RCX + KR + 0.42, RCY - 0.72, nx, RCY - 0.05, P.MUTED, 0.3)
        sw = st.text("wide", SX + K * (-1 + D_ECC - R_PIPE) / 2, YT + 0.0 - 0.25, 0.16, P.BG, 0.3, kind="bold")
        t_w = W(b, 1, "narrow side") - 0.3
        st.fade_in([wl, nl, sw] + nld, t_w, 0.4)
        st.fade_out([wl, nl, sw] + nld, T_rw0, 0.4)

        # standoff bar
        BX0, BX1, BY = RCX - KR - 0.1, RCX + KR + 0.1, RCY - KR - 0.85
        sbl = st.text("standoff", BX0, BY + 0.3, 0.17, P.MUTED, 0.3, align="l", kind="bold")
        st.fade_in(sbl, s[0] + 0.5, 0.4)

        def draw_standoff(c, t, look):
            a = _env(t, s[0] + 0.5, b.end + 1)
            d = dpos(t)
            f = (1.0 - R_PIPE - d) / (1.0 - R_PIPE)
            c.drawRoundRect(_R(BX0, BY - 0.07, BX1, BY + 0.07), 0.07, 0.07, _paint(P.GRID, a))
            cc = tuple(x + (y - x) * _cl((f - 0.4) / 0.5) for x, y in zip(hex_rgb(P.WARN), hex_rgb(P.SAFE)))
            c.drawRoundRect(_R(BX0, BY - 0.07, BX0 + (BX1 - BX0) * f, BY + 0.07), 0.07, 0.07, skia.Paint(Color=col(cc, a), AntiAlias=True))
            look.draw_text(c, "low: pipe off-centre" if f < 0.6 else "high: close to the middle", BX1, BY - 0.3, 0.16, P.TEXT, a, "r", "bold")
        st.procedural(s[0] + 0.3, b.end, 0.3, draw_standoff)

        # ---------------- the channel (s2): outlines in slice and plan view, formation fluid finds the path
        t_ch = W(b, 2, "channel")
        th_c = 0.0
        lo, hi = 0.0, math.pi                      # azimuth where the cement front at the cut level stops
        for _ in range(40):
            m = (lo + hi) / 2
            if _vel(m, D_ECC) * TAU_E < h0:
                lo = m
            else:
                hi = m
        th_c = lo
        hn = _vel(0.0, D_ECC) * TAU_E

        def draw_channel(c, t, look):
            a = _env(t, t_ch - 0.2, T_rw0 + 0.2, 0.4)
            if a <= 0:
                return
            x0, x1 = SX + K * (D_ECC + R_PIPE), SX + K
            pts = [(x0, YT - 0.02), (x0, YB + hn), (x1, YB + hn), (x1, YT - 0.02)]
            _trace(c, look, pts + [pts[0]], P.BAD, a, 0.045)
            arc = [(RCX + KR * math.cos(-th_c + 2 * th_c * i / 30), RCY + KR * math.sin(-th_c + 2 * th_c * i / 30)) for i in range(31)]
            inner = []
            for i in range(31):
                th = th_c - 2 * th_c * i / 30
                rr = (1.0 - _gap(th, D_ECC)) * KR
                inner.append((RCX + rr * math.cos(th), RCY + rr * math.sin(th)))
            _trace(c, look, arc + inner + [arc[0]], P.BAD, a, 0.045)
        st.procedural(t_ch - 0.3, T_rw0 + 0.3, 0.4, draw_channel)
        st.ripple(RCX + KR * (1.0 + D_ECC + R_PIPE) / 2, RCY, t_ch, t_ch + 1.2, P.BAD, period=0.8, r0=0.1, r1=0.7)
        xn = SX + K * (1.0 + D_ECC + R_PIPE) / 2
        st.flow([(xn, YB + 0.3), (xn, YT - 0.1)], W(b, 2, "path for fluid") - 0.2, T_rw0, P.WATER, n=7, speed=0.9, r=0.035, z=0.35)

        # ---------------- the replay: rewind, the pipe slides back towards the middle on bow-spring centralisers
        def draw_bows(c, t, look):
            a = _env(t, T_rw1 - 0.3, b.end + 1, 0.4)
            if a <= 0:
                return
            d = dpos(t)
            pl, pr = SX + K * (d - R_PIPE), SX + K * (d + R_PIPE)
            for yb in (2.0, -1.55):
                for xw, xh in ((pl, SX - K), (pr, SX + K)):
                    pts = [(xw + (xh - xw) * math.sin(math.pi * u / 20), yb - 0.55 + 1.1 * u / 20) for u in range(21)]
                    _trace(c, look, pts, P.TEXT, a, 0.045, glow=False)
                for yy in (yb - 0.58, yb + 0.58):
                    for xw in (pl, pr - WALL):
                        c.drawRoundRect(_R(xw - 0.04, yy - 0.07, xw + WALL + 0.04, yy + 0.07), 0.03, 0.03, _paint(P.STEEL_DK, a))
            px = RCX + KR * d
            for k in range(6):
                th = math.pi / 6 + k * math.pi / 3
                rr = (1.0 - _gap(th, d)) * KR
                p0 = (RCX + rr * math.cos(th), RCY + rr * math.sin(th))
                p1 = (RCX + KR * math.cos(th), RCY + KR * math.sin(th))
                _trace(c, look, [p0, p1], P.TEXT, a, 0.05, glow=False)
            c.drawCircle(px, RCY, KR * R_PIPE + 0.02, _paint(P.STEEL_DK, a, stroke=0.04))
        st.procedural(T_rw1 - 0.4, b.end, 0.2, draw_bows)
        rw = tag(st, SX, YT - 0.45, "⟲  replay with centralisers", P.TEXT, 0.18, align="c", z=0.7)
        st.fade_in(rw, T_rw0, 0.3)
        st.fade_out(rw, T_c0 + 0.6, 0.4)

        # ---------------- captions (right column; below the term cards from s2 on)
        h1 = st.text("MUD REMOVAL", RX, 3.15, 0.4, P.TEXT, 0.5, align="l", kind="bold")
        h2 = st.text(wrap_to("get every bit of mud out of the annulus", 0.21, 4.2), RX, 2.45, 0.21, P.MUTED, 0.5, align="l")
        st.fade_in(h1, s[0] + 0.1, 0.45)
        st.fade_in(h2, W(b, 0, "getting every") - 0.1, 0.45)
        t_card = min(F.spoken_at(b, tt["term"]) for tt in b.terms) - 0.3
        st.fade_out([h1, h2], t_card - 0.45, 0.4)
        c1 = tag(st, RX, 0.35, "pipe off-centre", P.WARN, 0.2)
        c2 = tag(st, RX, -0.27, "narrow side: mud barely moves", P.MUD, 0.2)
        c3 = tag(st, RX, -0.89, "wide side: cement races up", P.CEMENT, 0.2)
        c4 = tag(st, RX, -1.51, "a mud channel: a hidden path", "#ffffff", 0.2, bg=P.BAD)
        st.fade_in(c1, W(b, 1, "off-centre") - 0.2, 0.4)
        st.fade_in(c2, W(b, 1, "narrow side") - 0.1, 0.4)
        st.fade_in(c3, W(b, 1, "races") - 0.2, 0.4)
        st.fade_in(c4, W(b, 2, "path for fluid") - 0.3, 0.4)
        st.fade_out(c1 + c2 + c3 + c4, T_rw0, 0.4)
        d1 = tag(st, RX, 0.35, "centralisers re-centre the pipe", P.TEXT, 0.2)
        st.fade_in(d1, W(b, 3, "push the pipe") - 0.2, 0.4)
        chips = [("condition the mud", W(b, 4, "Conditioning")), ("a well-designed spacer", W(b, 4, "well-designed")),
                 ("a high pump rate", W(b, 4, "high pump rate")), ("land wells, liners: move the pipe", W(b, 4, "moving the pipe"))]
        for i, (txt, t) in enumerate(chips):
            ch_ = tag(st, RX, -0.27 - 0.62 * i, ("+ " if i < 3 else "") + txt, P.TEXT if i < 3 else P.MUTED, 0.19)
            st.fade_in(ch_, t - 0.15, 0.4)
        done = tag(st, RX, -2.95, "clean sheath, no channel", "#06201c", 0.22, bg=P.SAFE)
        st.fade_in(done, T_c1 + 0.3, 0.45)


def _col_emw(z, friction=0.0):
    """Equivalent density (sg) of the 9 5/8 in annulus column at depth z: mud to the top of cement, lead, tail."""
    segs = [(0.0, TOC_958, MW_1214), (TOC_958, TAIL_TOP, RHO_LEAD), (TAIL_TOP, SHOE_958, RHO_TAIL), (SHOE_958, 9e9, RHO_TAIL)]
    p = sum(rho * max(0.0, min(z, bb) - a) for a, bb, rho in segs)
    return p / z + friction


def beat_slurry(st, tl):
    b = tl["6.04"]
    s = b.sent
    t_B = s[3] - 0.1                     # part B (the lab) starts with sentence 3
    with st.span(b.start, b.end):
        # ================= part A: the column inside the window, 12 1/4 in hole, 9 5/8 in casing
        Z0, Z1 = 1800.0, 3500.0
        ch = Chart(st, -4.55, -2.6, 3.9, 5.9, (1.0, 1.8), (Z0, Z1), invert_y=True)
        fr = ch.frame(xticks=[1.0, 1.2, 1.4, 1.6, 1.8], yticks=[2000, 2500, 3000, 3500], xlabel="equivalent density (sg)",
                      ylabel="depth (m)", fx="{:.1f}", grid=False)
        zs = [Z0 + 25 * i for i in range(int((Z1 - Z0) / 25) + 1)]
        band = ch.band([(M.pp(z), z) for z in zs], [(M.fg(z), z) for z in zs], P.SAFE, 0.1, 0.3)
        ppc = ch.curve([M.pp(z) for z in zs], zs, P.PORE, 0.06, 0.3)
        fgc = ch.curve([M.fg(z) for z in zs], zs, P.FRAC, 0.06, 0.3)
        ppl = ch.label(M.pp(3300) - 0.03, 3300, "pore pressure", 0.17, P.PORE, "r", "bold")
        fgl = ch.label(M.fg(2500) + 0.015, 2500, "fracture", 0.17, P.FRAC, "l", "bold")
        partA = fr + [band, ppc, fgc, ppl, fgl]
        st.fade_in(fr + [band], b.start + 0.1, 0.5)
        st.draw_on([ppc, fgc], s[0] + 0.2, s[0] + 1.6, "BEZIER")
        st.fade_in([ppl, fgl], s[0] + 1.0, 0.4)
        # the column, static (dashed) and with friction while pumping (solid), over the open hole
        zc = [SHOE_1338 + 10 * i for i in range(int((SHOE_958 - SHOE_1338) / 10) + 1)]
        stat = st.line([ch.pt(_col_emw(z), z) for z in zc], P.CEMENT, 0.045, 0.35, alpha=0.9)
        dyn = st.line([ch.pt(_col_emw(z, FRICTION), z) for z in zc], P.CEMENT, 0.065, 0.36, role="glow")
        t_col, t_fr = W(b, 1, "its column"), W(b, 1, "plus friction")
        st.draw_on(stat, t_col - 0.2, t_col + 1.2, "BEZIER")
        st.draw_on(dyn, t_fr - 0.1, t_fr + 1.3, "BEZIER")
        lg = [[st.line([(ch.X(1.06), ch.Y(1880)), (ch.X(1.13), ch.Y(1880))], P.CEMENT, 0.045, 0.4, alpha=0.9)],
              st.text("column", ch.X(1.15), ch.Y(1880), 0.16, P.TEXT, 0.4, align="l", kind="bold")]
        lg2 = [st.line([(ch.X(1.06), ch.Y(1975)), (ch.X(1.13), ch.Y(1975))], P.CEMENT, 0.06, 0.4),
               st.text("column + friction", ch.X(1.15), ch.Y(1975), 0.16, P.TEXT, 0.4, align="l", kind="bold")]
        st.fade_in(lg[0] + [lg[1]], t_col, 0.4)
        st.fade_in(lg2, t_fr, 0.4)
        partA += [stat, dyn] + lg[0] + [lg[1]] + lg2
        # margins at the shoe: below fracture, above pore
        zm = SHOE_958 - 40
        t_m1, t_m2 = W(b, 1, "below the fracture"), W(b, 1, "above pore")
        m1 = st.line([ch.pt(_col_emw(zm, FRICTION) + 0.01, zm), ch.pt(M.fg(zm) - 0.01, zm)], P.FRAC, 0.04, 0.45)
        m2 = st.line([ch.pt(M.pp(zm) + 0.01, zm), ch.pt(_col_emw(zm) - 0.01, zm)], P.PORE, 0.04, 0.45)
        st.draw_on(m1, t_m1, t_m1 + 0.5, "BEZIER")
        st.draw_on(m2, t_m2, t_m2 + 0.5, "BEZIER")
        st.ripple(ch.X(M.fg(zm)), ch.Y(zm), t_m1, t_m1 + 0.6, P.FRAC, period=0.7, r0=0.06, r1=0.4)
        st.ripple(ch.X(M.pp(zm)), ch.Y(zm), t_m2, t_m2 + 0.6, P.PORE, period=0.7, r0=0.06, r1=0.4)
        partA += [m1, m2]

        # depth-aligned annulus strip: bore | 9 5/8 in casing | annulus | rock (13 3/8 in casing above 2,000 m)
        Y = ch.Y
        XB0, XB1, XA1, XR1 = 0.15, 0.55, 1.15, 1.6
        WL = 0.1
        ybot = Y(3460)
        strip = [st.rect((XB0 + XR1) / 2, (Y(Z0) + ybot) / 2, XR1 - XB0 + 0.2, Y(Z0) - ybot + 0.1, P.PANEL, 0.0),
                 st.rect((XA1 + XR1) / 2, (Y(Z0) + ybot) / 2, XR1 - XA1, Y(Z0) - ybot, P.ROCK, 0.02),
                 st.rect((XB0 + XA1) / 2, (Y(SHOE_958) + ybot) / 2, XA1 - XB0, Y(SHOE_958) - ybot, P.MUD, 0.03, alpha=0.85),
                 st.rect((XB0 + XB1) / 2, (Y(Z0) + Y(SHOE_958)) / 2, XB1 - XB0, Y(Z0) - Y(SHOE_958), P.MUD, 0.03, alpha=0.55),
                 st.rect((XB1 + WL + XA1) / 2, (Y(Z0) + Y(SHOE_958)) / 2, XA1 - XB1 - WL, Y(Z0) - Y(SHOE_958), P.MUD, 0.03, alpha=0.85),
                 st.rect(XB1 + WL / 2, (Y(Z0) + Y(SHOE_958)) / 2, WL, Y(Z0) - Y(SHOE_958), P.STEEL, 0.2),
                 st.rect(XA1 + WL / 2, (Y(Z0) + Y(SHOE_1338)) / 2, WL, Y(Z0) - Y(SHOE_1338), P.STEEL_DK, 0.2),
                 st.rect((XA1 + XR1) / 2, Y(sum(M.SAND_A) / 2), XR1 - XA1, max(Y(M.SAND_A[0]) - Y(M.SAND_A[1]), 0.09), P.SAND, 0.05)]
        st.fade_in(strip, s[0] + 0.3, 0.5)
        partA += strip
        LXS = 1.95
        lbl = []

        def lab(z, txt, colr, t):
            o = tag(st, LXS, Y(z), txt, colr, 0.18)
            ld = leader(st, LXS - 0.02, Y(z), XA1 - 0.05 if z < SHOE_958 else XB1, Y(z))
            st.fade_in(o + ld, t, 0.4)
            lbl.extend(o + ld)
        lab(SHOE_1338, f"13⅜ in shoe · {SHOE_1338:,.0f} m", P.MUTED, s[0] + 0.6)
        lab(SHOE_958, f"9⅝ in shoe · {SHOE_958:,.0f} m", P.MUTED, s[0] + 0.8)
        t_lead, t_tail = W(b, 2, "lighter lead"), W(b, 2, "dense, strong tail")
        lead = st.rect((XB1 + WL + XA1) / 2, Y(TAIL_TOP), XA1 - XB1 - WL, 0.0001, LEAD, 0.06, anchor="b")
        tail = st.rect((XB1 + WL + XA1) / 2, Y(SHOE_958), XA1 - XB1 - WL, 0.0001, P.CEMENT, 0.06, anchor="b")
        st.fade_in(lead, t_lead - 0.1, 0.1)
        st.scale_to(lead, t_lead - 0.1, t_lead + 1.2, sy=Y(TOC_958) - Y(TAIL_TOP))
        st.fade_in(tail, t_tail - 0.1, 0.1)
        st.scale_to(tail, t_tail - 0.1, t_tail + 1.0, sy=Y(TAIL_TOP) - Y(SHOE_958))
        partA += [lead, tail]
        lab(2300, "mud", P.MUD, t_lead - 0.3)
        lab((TOC_958 + TAIL_TOP) / 2 - 60, "lead: lighter", LEAD, t_lead + 0.2)
        lab((TAIL_TOP + SHOE_958) / 2 - 30, "tail: dense, strong", P.CEMENT, t_tail + 0.2)
        st.ripple(ch.X(_col_emw(TAIL_TOP + 150, FRICTION)), Y(TAIL_TOP + 150), t_tail, t_tail + 0.5, P.CEMENT, period=0.8, r0=0.06, r1=0.45)
        t_toc, t_sa = W(b, 2, "top of cement"), W(b, 2, "thin overpressured sand")
        tocm = st.line([(XB1 + WL, Y(TOC_958)), (XA1 + 0.25, Y(TOC_958))], P.TEXT, 0.035, 0.4)
        st.draw_on(tocm, t_toc - 0.1, t_toc + 0.4, "BEZIER")
        partA.append(tocm)
        lab(TOC_958 - 40, "top of cement", P.TEXT, t_toc)
        lab(sum(M.SAND_A) / 2 + 25, f"Sand A · {M.SAND_A[0]:,.0f}–{M.SAND_A[1]:,.0f} m", P.SAND, t_sa - 0.1)
        st.ripple((XA1 + XR1) / 2, Y(sum(M.SAND_A) / 2), t_sa - 0.1, t_sa + 1.2, P.SAND, period=0.8, r0=0.08, r1=0.55)
        sab = st.rect(ch.x + ch.w / 2, Y(sum(M.SAND_A) / 2), ch.w, max(Y(M.SAND_A[0]) - Y(M.SAND_A[1]), 0.07), P.SAND, 0.12, alpha=0.75, role="flat")
        st.fade_in(sab, t_sa, 0.4)
        partA.append(sab)
        ok = tag(st, 4.95, (Y(TOC_958) + Y(sum(M.SAND_A) / 2)) / 2, "✓ above every zone", P.SAFE, 0.18)
        brk = st.line([(4.7, Y(TOC_958) - 0.02), (4.8, Y(TOC_958) - 0.02), (4.8, Y(M.SAND_A[1]) + 0.02), (4.7, Y(M.SAND_A[1]) + 0.02)], P.SAFE, 0.035, 0.4)
        t_ok = W(b, 2, "above every zone")
        st.fade_in(ok, t_ok - 0.1, 0.4)
        st.draw_on(brk, t_ok - 0.3, t_ok + 0.3, "BEZIER")
        partA += lbl + ok + [brk]
        st.fade_out(partA, t_B - 0.5, 0.45)

        # ================= part B: the lab
        hdr = st.text("LAB TESTS AT DOWNHOLE TEMPERATURE AND PRESSURE", -5.95, 3.4, 0.24, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(hdr, t_B + 0.1, 0.45)
        c1 = Chart(st, -4.75, -2.55, 4.3, 3.35, (0, 10), (0, 10))
        f1 = c1.frame(xticks=[], yticks=[], xlabel="time", ylabel="consistency", grid=False)
        f1.append(st.text("how long it stays pumpable", c1.x + c1.w / 2 - 0.5, c1.y + c1.h + 0.7, 0.22, P.TEXT, 0.4, kind="bold"))
        st.fade_in(f1, t_B + 0.2, 0.45)
        tt = c1.curve([0, 2, 4, 5.5, 6.5, 7.1, 7.5, 7.85], [1.0, 1.1, 1.25, 1.5, 2.2, 3.8, 6.4, 9.6], P.TEXT, 0.07, 0.4)
        t_hl = W(b, 3, "how long")
        st.draw_on(tt, t_hl - 0.2, t_hl + 2.0, "BEZIER")
        lim = st.dashed(c1.pt(0, 7.0), c1.pt(10, 7.0), P.MUTED, 0.03, 0.12, 0.08, 0.35)
        liml = c1.label(0.2, 7.55, "limit of pumpability", 0.16, P.MUTED, "l", "bold")
        st.fade_in(lim + [liml], W(b, 3, "pumpable") - 0.2, 0.4)
        t_tt = W(b, 3, "thickening time")
        x_tt = 7.55
        drop = st.dashed(c1.pt(x_tt, 7.0), c1.pt(x_tt, 0.0), P.WARN, 0.035, 0.1, 0.07, 0.45)
        arr = st.arrow(c1.X(0.15), c1.Y(4.6), c1.X(x_tt) - 0.03, c1.Y(4.6), P.WARN, 0.045, 0.18, 0.45)
        ttl = c1.label(x_tt / 2, 5.3, "thickening time", 0.19, P.WARN, "c", "bold")
        st.fade_in(drop + arr + [ttl], t_tt - 0.2, 0.45)
        c2 = Chart(st, 1.85, -2.55, 5.0, 3.35, (0, 10), (0, 10))
        f2 = c2.frame(xticks=[], yticks=[], xlabel="time", ylabel="strength", grid=False)
        f2.append(st.text("how fast it gains strength", c2.x + c2.w / 2 - 0.5, c2.y + c2.h + 0.7, 0.22, P.TEXT, 0.4, kind="bold"))
        t_gs = W(b, 3, "how fast")
        st.fade_in(f2, t_gs - 0.6, 0.45)
        cs = c2.curve([0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0], [0.0, 0.3, 1.6, 3.6, 5.3, 6.3, 6.8], P.TEXT, 0.07, 0.4)
        st.draw_on(cs, t_gs - 0.2, t_gs + 1.8, "BEZIER")
        # temperature: above about 110 C strength fades without silica
        TX0, TX1, TY = -4.2, 2.6, 2.55
        t110 = W(b, 4, "a hundred and ten")
        tlab = st.text("temperature", -5.95, TY, 0.18, P.MUTED, 0.5, align="l", kind="bold")
        tbar = st.rect((TX0 + TX1) / 2, TY, TX1 - TX0, 0.14, P.GRID, 0.4, role="pill")
        hot = st.rect(TX0 + (TX1 - TX0) * 0.62, TY, (TX1 - TX0) * 0.38, 0.14, P.WARN, 0.41, anchor="l", role="pill", alpha=0.85)
        tick = st.rect(TX0 + (TX1 - TX0) * 0.62, TY, 0.05, 0.42, P.TEXT, 0.42)
        tkl = st.text("110 °C", TX0 + (TX1 - TX0) * 0.62, TY + 0.36, 0.2, P.TEXT, 0.42, kind="bold")
        st.fade_in([tlab, tbar], s[4] - 0.1, 0.4)
        st.fade_in([hot, tick, tkl], t110 - 0.2, 0.4)
        t_dp = W(b, 4, "deepest sections")
        dpl = st.text("our deepest sections", TX0 + (TX1 - TX0) * 0.86, TY - 0.36, 0.16, P.WARN, 0.42, kind="bold")
        st.fade_in(dpl, t_dp - 0.2, 0.4)
        fade_c = c2.curve([6.0, 7.0, 8.0, 9.0, 10.0], [6.8, 6.3, 5.0, 3.9, 3.1], P.BAD, 0.06, 0.41)
        fade_l = c2.label(9.8, 2.2, "no silica: strength fades", 0.16, P.BAD, "r", "bold")
        st.draw_on(fade_c, t_dp + 0.1, t_dp + 1.5, "BEZIER")
        st.fade_in(fade_l, t_dp + 0.8, 0.4)
        t_si = W(b, 4, "silica")
        sil_c = c2.curve([6.0, 7.0, 8.0, 9.0, 10.0], [6.8, 7.1, 7.3, 7.45, 7.55], P.SAFE, 0.07, 0.42)
        sil_l = c2.label(9.8, 8.4, "+ silica: strength holds", 0.17, P.SAFE, "r", "bold")
        st.draw_on(sil_c, t_si, t_si + 1.4, "BEZIER")
        st.fade_in(sil_l, t_si + 0.7, 0.4)


def _p_slow(x):
    """Pressure the setting cement passes down to the gas zone (arbitrary units) vs time after placement (0-10)."""
    return 8.2 - 5.6 * _sm((x - 3.0) / 3.5)


def _p_fast(x):
    return 8.2 - 5.6 * _sm((x - 3.0) / 1.6)


def beat_danger(st, tl):
    b = tl["6.05"]
    s = b.sent
    PG = 5.0                                   # gas-zone pressure (same units)
    X_GT, X_GT_F = 6.8, 3.7                    # gas-tight times: slow and fast-setting slurry
    lo, hi = 3.0, 7.0
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if _p_slow(m) > PG else (lo, m)
    X_C = lo                                   # the slow slurry's pressure crosses the gas-zone pressure
    t_a = s[1] + 0.1
    t_b = W(b, 1, "hold itself up")
    t_c = W(b, 3, "drops below") + 0.2
    t_d = W(b, 3, "leave a path", 1.0) + 0.2
    t_e = s[4]
    knots = [(t_a, 0.0), (t_b, 3.0), (t_c, X_C), (t_d, X_GT), (t_e, 7.6), (b.end, 8.4)]

    def xnow(t):
        return _pw(t, knots)

    with st.span(b.start, b.end):
        hd = st.text("A DANGEROUS PERIOD", -5.9, 3.35, 0.36, P.TEXT, 0.5, align="l", kind="bold")
        sb = st.text("minutes to hours long", -5.9, 2.8, 0.22, P.MUTED, 0.5, align="l")
        st.fade_in(hd, s[0] + 0.05, 0.45)
        st.fade_in(sb, W(b, 0, "minutes") - 0.1, 0.45)
        ch = Chart(st, -4.6, -2.3, 5.4, 4.1, (0, 10), (0, 10))
        fr = ch.frame(xticks=[], yticks=[], xlabel="time after the cement is in place", ylabel="pressure on the gas zone", grid=False)
        zones = []
        for x0, x1, a, nm in ((0, 3.0, 0.05, "liquid"), (3.0, X_GT, 0.13, "gel"), (X_GT, 10, 0.26, "set")):
            zones.append(st.rect(ch.X((x0 + x1) / 2), ch.Y(5), ch.X(x1) - ch.X(x0), ch.Y(10) - ch.Y(0), P.CEMENT, 0.06, alpha=a, role="flat"))
            zones.append(st.text(nm, ch.X((x0 + x1) / 2), ch.Y(9.4), 0.19, P.TEXT, 0.2, kind="bold"))
        st.fade_in(fr, s[0] + 0.2, 0.5)
        st.fade_in(zones[0:2], s[0] + 0.5, 0.4)
        st.fade_in(zones[2:4], t_b - 0.3, 0.4)
        st.fade_in(zones[4:6], t_d - 0.6, 0.4)
        t_gas = W(b, 2, "holding gas back")
        gline = st.dashed(ch.pt(0, PG), ch.pt(10, PG), P.PORE, 0.04, 0.16, 0.09, 0.3)
        glab = ch.label(9.85, PG + 0.45, "gas-zone pressure", 0.17, P.PORE, "r", "bold")
        st.fade_in(gline + [glab], t_gas - 0.6, 0.4)

        def draw_curve(c, t, look):
            a = _env(t, t_a - 0.3, b.end + 1)
            xn = xnow(t)
            n = max(2, int(xn * 12) + 2)
            pts = [ch.pt(xn * i / (n - 1), _p_slow(xn * i / (n - 1))) for i in range(n)]
            _trace(c, look, pts, P.CEMENT, a, 0.065)
            x, y = pts[-1]
            c.drawCircle(x, y, 0.09, _paint(P.TEXT, a))
            if t < t_c + 2.0:
                look.draw_text(c, "weight of the column", ch.X(0.25), ch.Y(_p_slow(0) + 0.55), 0.16, P.CEMENT, a * _env(t, t_a, t_c + 1.5), "l", "bold")
        st.procedural(t_a - 0.3, b.end, 0.4, draw_curve)
        # the danger window: below the gas-zone pressure, not yet gas-tight
        win = st.rect(ch.X(X_C), ch.Y(5), 0.0001, ch.Y(10) - ch.Y(0), P.BAD, 0.08, anchor="l", alpha=0.32, role="flat")
        st.fade_in(win, t_c - 0.1, 0.2)
        st.scale_to(win, t_c, t_d, sx=ch.X(X_GT) - ch.X(X_C), interp="LINEAR")
        wl = tag(st, ch.X((X_C + X_GT) / 2), ch.Y(7.75), "gas can get in", "#ffffff", 0.18, align="c", bg=P.BAD)
        st.fade_in(wl, W(b, 3, "gas can slip") - 0.2, 0.4)
        st.ripple(ch.X(X_C), ch.Y(PG), t_c - 0.2, t_c + 1.0, P.BAD, period=0.7, r0=0.08, r1=0.55)
        gt = st.dashed(ch.pt(X_GT, 0), ch.pt(X_GT, 8.9), P.TEXT, 0.03, 0.1, 0.07, 0.3)
        gtl = ch.label(X_GT + 0.12, 8.65, "gas-tight", 0.16, P.TEXT, "l", "bold")
        st.fade_in(gt + [gtl], t_d - 0.4, 0.4)
        # a good slurry: sets fast through the gap, gas-tight before the pressure is lost
        t_f = W(b, 4, "good slurries")
        fc = ch.curve([i * 0.1 for i in range(101)], [_p_fast(i * 0.1) for i in range(101)], P.SAFE, 0.065, 0.42)
        st.draw_on(fc, t_f - 0.5, t_f + 1.3, "BEZIER")
        fgt = st.dashed(ch.pt(X_GT_F, 0), ch.pt(X_GT_F, 8.6), P.SAFE, 0.03, 0.1, 0.07, 0.42)
        st.fade_in(fgt, t_f + 0.2, 0.3)
        fl = tag(st, ch.X(X_GT_F) + 0.15, ch.Y(1.1), "fast set: gas-tight first", P.SAFE, 0.17)
        st.fade_in(fl, t_f + 0.5, 0.4)

        # ---------------- the annulus beside it: cement gels, its weight stops pressing down, gas gets in
        CXc = 4.75
        view = View(st, b.start, b.end, z=0.2, clip=(2.38, -3.31, 7.12, 3.46))
        view.__enter__()
        cut = Cutaway(st, CXc, 3.45, -3.3, hole_w=2.3, pipe_w=1.0, wall=0.11, rock_w=1.15)
        base = cut.draw()
        GY0, GY1 = -2.35, -1.35
        gas = []
        for xc in (cut.hole[0] - 0.575, cut.hole[1] + 0.575):
            gas += [st.rect(xc, (GY0 + GY1) / 2, 1.15, GY1 - GY0, P.SAND, 0.02),
                    st.rect(xc, (GY0 + GY1) / 2, 1.15, GY1 - GY0, P.GAS, 0.03, alpha=0.22, role="flat")]
        gzl = st.text("gas zone", cut.hole[1] + 0.47, GY0 - 0.2, 0.15, P.GAS, 0.1, kind="bold")
        cem = [cut.static_gap(sd, P.CEMENT, 3.45, -3.3, 0.05) for sd in "lr"]
        bore = cut.static_bore(P.MUD, 3.45, -3.3, 0.05, alpha=0.6)
        st.fade_in(base + gas + [gzl] + cem + [bore], s[0] + 0.3, 0.5)
        gxs = [(g[0] + g[1]) / 2 for g in (cut.gap_l, cut.gap_r)]

        def draw_annulus(c, t, look):
            a = _env(t, s[0] + 0.4, b.end + 1)
            xn = xnow(t)
            gel = _sm((xn - 3.0) / (X_GT - 3.0))
            if gel > 0:              # a gel network forms: the cement starts to hold itself up
                for g in (cut.gap_l, cut.gap_r):
                    c.save()
                    c.clipRect(_R(g[0], -3.3, g[1], 3.45))
                    for k in range(-6, 30):
                        y0 = -3.3 + k * 0.28
                        _trace(c, look, [(g[0], y0), (g[1], y0 + 0.4)], P.STEEL_DK, 0.55 * gel * a, 0.018, glow=False)
                        _trace(c, look, [(g[0], y0 + 0.4), (g[1], y0)], P.STEEL_DK, 0.55 * gel * a, 0.018, glow=False)
                    c.restore()
            f = (_p_slow(xn) - 2.6) / 5.6            # share of the weight still pressing down
            if t > t_a - 0.2:
                for gx in gxs:
                    for y in (2.4, 0.9, -0.6):
                        L = 0.9 * f
                        if L > 0.05:
                            _trace(c, look, [(gx, y + 0.45), (gx, y + 0.45 - L)], P.TEXT, a * 0.9, 0.05, glow=False)
                            pth = skia.Path()
                            pth.moveTo(gx, y + 0.45 - L - 0.14)
                            pth.lineTo(gx - 0.1, y + 0.45 - L + 0.02)
                            pth.lineTo(gx + 0.1, y + 0.45 - L + 0.02)
                            pth.close()
                            c.drawPath(pth, _paint(P.TEXT, a * 0.9))
            # at the gas zone (right wall): cement pressure pushes out, gas pressure pushes in
            if t > t_gas - 0.6:
                ag = a * _cl((t - t_gas + 0.6) / 0.4) * (1.0 - _cl((t - t_off) / 0.4))
                yw = (GY0 + GY1) / 2
                xw = cut.hole[1]
                Lc = 0.95 * _p_slow(xn) / 8.2
                Lg = 0.95 * PG / 8.2
                _trace(c, look, [(xw - 0.05, yw + 0.18), (xw - 0.05 + Lc, yw + 0.18)], P.CEMENT, ag, 0.06, glow=False)
                pth = skia.Path()
                pth.moveTo(xw - 0.05 + Lc + 0.15, yw + 0.18)
                pth.lineTo(xw - 0.05 + Lc, yw + 0.28)
                pth.lineTo(xw - 0.05 + Lc, yw + 0.08)
                pth.close()
                c.drawPath(pth, _paint(P.CEMENT, ag))
                _trace(c, look, [(xw + 1.05, yw - 0.18), (xw + 1.05 - Lg, yw - 0.18)], P.PORE, ag, 0.06)
                pth = skia.Path()
                pth.moveTo(xw + 1.05 - Lg - 0.15, yw - 0.18)
                pth.lineTo(xw + 1.05 - Lg, yw - 0.08)
                pth.lineTo(xw + 1.05 - Lg, yw - 0.28)
                pth.close()
                c.drawPath(pth, _paint(P.PORE, ag))
        st.procedural(s[0] + 0.3, b.end, 0.3, draw_annulus)
        view.__exit__()
        hold = tag(st, CXc, 2.95, "gels: holds itself up", P.TEXT, 0.17, align="c", z=0.7)
        st.fade_in(hold, t_b - 0.2, 0.4)
        st.fade_out(hold, t_c - 0.5, 0.4)

        # gas slips in after the crossing and leaves a path up through the gelled cement
        gx = gxs[1]
        t_in = W(b, 3, "gas can slip") - 0.2
        t_p0, t_p1 = W(b, 3, "leave a path") - 0.4, t_e - 0.3
        t_off = t_f + 0.8

        def draw_gas(c, t, look):
            a = _env(t, t_in, t_off + 0.6, 0.4)
            if a <= 0:
                return
            yw = (GY0 + GY1) / 2
            top = yw + (3.2 - yw) * _sm((t - t_p0) / (t_p1 - t_p0))
            if top > yw + 0.05:
                _trace(c, look, [(gx, yw), (gx + 0.03, (yw + top) / 2), (gx - 0.02, top)], P.GAS, a * 0.9, 0.035)
            pos = []
            for k in range(7):
                tb = t_in + 0.55 * k
                if t < tb:
                    continue
                u = (t - tb) / 3.2
                if u < 0.25:
                    x = cut.hole[1] + 0.55 - (cut.hole[1] + 0.55 - gx) * (u / 0.25)
                    y = yw + 0.05 * math.sin(k)
                else:
                    x = gx + 0.04 * math.sin(6 * u + k)
                    y = yw + (u - 0.25) * 4.0
                if y < 3.3:
                    pos.append((x, y))
            look.draw_particles(c, pos, P.GAS, 0.065, a, glow=True)
        view.__enter__()
        st.procedural(t_in, t_off + 1.0, 0.35, draw_gas)
        view.__exit__()
        # push in on the gas zone as the pressure crosses, back out as the path climbs
        FZ = (cut.hole[1] - 0.1, (GY0 + GY1) / 2 + 0.3)
        view.camera(t_c - 0.9, t_c + 0.5, FZ, FZ, 1.5)
        view.camera(t_p0 + 0.2, t_p0 + 1.6, FZ, FZ, 1.0)
        gl = tag(st, CXc, -2.9, "gas leaves a path", P.GAS, 0.18, align="c", z=0.7)
        st.fade_in(gl, W(b, 3, "leave a path") - 0.1, 0.4)
        st.fade_out(gl, t_off, 0.4)
        ok = tag(st, CXc, -2.9, "fast set: gas stays out", P.SAFE, 0.18, align="c", z=0.7)
        st.fade_in(ok, t_off + 0.4, 0.4)


def _wave_pts(x0, y, length, amp, decay, onset=0.12, n=110, cycles=7.0):
    """Receiver waveform: quiet until the casing arrival, then a damped ring."""
    out = []
    for i in range(n):
        u = i / (n - 1)
        if u < onset:
            out.append((x0 + length * u, y))
        else:
            v = (u - onset) / (1 - onset)
            out.append((x0 + length * u, y + amp * math.exp(-decay * v) * math.sin(2 * math.pi * cycles * v)))
    return out


def beat_logs(st, tl):
    b = tl["6.06"]
    s = b.sent
    with st.span(b.start, b.end):
        # ---------------- s0: the question
        q = st.text("How do we know it worked?", -1.2, 0.4, 0.5, P.TEXT, 0.5, kind="bold")
        st.fade_in(q, s[0] - 0.05, 0.45)
        st.fade_out(q, s[1] - 0.35, 0.35)

        # ---------------- s1: the job record (first evidence)
        JX0, JX1, JY0, JY1 = -6.05, 2.95, -2.75, 2.95
        card = st.rect((JX0 + JX1) / 2, (JY0 + JY1) / 2, JX1 - JX0, JY1 - JY0, P.PANEL, 0.2)
        jt = st.text("THE JOB RECORD", JX0 + 0.35, JY1 - 0.45, 0.3, P.TEXT, 0.3, align="l", kind="bold")
        st.fade_in([card, jt], s[1] - 0.2, 0.45)
        job = [card, jt]
        rows = [(1.25, "full returns", "no mud lost to the rock", W(b, 1, "full returns")),
                (-0.2, "the right volumes", "pumped as planned", W(b, 1, "right volumes")),
                (-1.65, "a plug bump on time", "at the calculated volume", W(b, 1, "plug bump"))]
        for y, h, sub, t in rows:
            ck = _check(st, JX0 + 0.6, y, t + 0.3, z=0.5)
            ht = st.text(h, JX0 + 1.05, y + 0.17, 0.27, P.TEXT, 0.4, align="l", kind="bold")
            sb = st.text(sub, JX0 + 1.05, y - 0.27, 0.18, P.MUTED, 0.4, align="l")
            st.fade_in([ht, sb], t - 0.15, 0.4)
            job += ck + [ht, sb]
        # mini visuals (right side of the card)
        MX0, MX1 = 0.1, 2.6
        y = rows[0][0]
        ut = st.line([(MX0 + 0.3, y + 0.45), (MX0 + 0.3, y - 0.4), (MX1 - 0.3, y - 0.4), (MX1 - 0.3, y + 0.45)], P.GRID, 0.12, 0.35)
        st.fade_in(ut, rows[0][3] - 0.2, 0.4)
        st.flow([(MX0 + 0.3, y + 0.45), (MX0 + 0.3, y - 0.4), (MX1 - 0.3, y - 0.4), (MX1 - 0.3, y + 0.45)], rows[0][3] - 0.1, s[2] - 0.2,
                P.MUD, n=12, speed=1.0, r=0.045, z=0.4)
        io = [st.text("in", MX0 + 0.05, y + 0.3, 0.16, P.MUTED, 0.4, align="r", kind="bold"),
              st.text("out = in", MX1 - 0.1, y + 0.3, 0.16, P.MUD, 0.4, align="l", kind="bold")]
        st.fade_in(io, rows[0][3], 0.4)
        job += [ut] + io
        y = rows[1][0]
        gbar = st.rect((MX0 + MX1) / 2, y, MX1 - MX0, 0.18, P.GRID, 0.35, role="pill")
        gfill = st.rect(MX0, y, 0.0001, 0.18, P.CEMENT, 0.36, anchor="l", role="pill")
        plan = st.rect(MX0 + 0.85 * (MX1 - MX0), y, 0.04, 0.42, P.WARN, 0.37)
        pl_t = st.text("planned", MX0 + 0.85 * (MX1 - MX0), y + 0.36, 0.15, P.WARN, 0.37, kind="bold")
        st.fade_in([gbar, plan, pl_t, gfill], rows[1][3] - 0.2, 0.4)
        st.scale_to(gfill, rows[1][3], rows[1][3] + 1.2, sx=0.85 * (MX1 - MX0))
        job += [gbar, gfill, plan, pl_t]
        y = rows[2][0]
        xs = [0.0, 0.2, 0.45, 0.7, 0.85, 0.85]
        ys = [0.15, 0.1, 0.05, 0.3, 0.35, 0.95]
        tr = st.line([(MX0 + x * (MX1 - MX0 - 0.2), y - 0.42 + v * 0.85) for x, v in zip(xs, ys)], P.TEXT, 0.05, 0.4)
        cl = st.dashed((MX0 + 0.85 * (MX1 - MX0 - 0.2), y - 0.45), (MX0 + 0.85 * (MX1 - MX0 - 0.2), y + 0.45), P.WARN, 0.03, 0.1, 0.07, 0.38)
        st.fade_in(cl, rows[2][3] - 0.2, 0.3)
        st.draw_on(tr, rows[2][3] - 0.1, rows[2][3] + 1.0, "BEZIER")
        job += [tr] + cl
        st.fade_out(job, s[2] - 0.35, 0.4)

        # ---------------- s2-s3: logs, where it matters. The cement bond log
        lh = st.text("LOGS, WHERE IT MATTERS", -5.95, 3.4, 0.28, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(lh, s[2] - 0.05, 0.4)
        CXl, YT, YB, YM = -4.5, 2.95, -3.25, -0.2           # cutaway; above YM: free pipe (mud), below: bonded cement
        cut = Cutaway(st, CXl, YT, YB, hole_w=2.3, pipe_w=1.35, wall=0.1, rock_w=0.55)
        base = cut.draw()
        fills = [cut.static_gap(sd, P.MUD, YT, YM, 0.05, alpha=0.85) for sd in "lr"] + \
                [cut.static_gap(sd, P.CEMENT, YM, YB, 0.05) for sd in "lr"] + [cut.static_bore(P.MUD, YT, YB, 0.04, alpha=0.45)]
        zl = pill(st, CXl, YT - 0.35, "free pipe", P.PANEL2, P.MUD, 0.15, 0.3) + \
            pill(st, CXl, YM - 0.35, "cemented", P.PANEL2, P.CEMENT, 0.15, 0.3)
        st.fade_in(base + fills + zl, s[2] + 0.1, 0.45)
        t_cbl = W(b, 3, "listens")
        t_damp = W(b, 3, "good cement damps")
        t_us = s[4]

        def ytool(t):
            return _pw(t, [(t_damp - 0.9, 1.35), (t_damp - 0.1, -1.75)])

        bw0, bw1 = cut.pipe[0] + cut.wall, cut.pipe[1] - cut.wall

        def draw_tool(c, t, look):
            a = _env(t, s[2] + 0.3, s[5] + 0.2)
            if a <= 0:
                return
            yc = ytool(t)
            c.drawRoundRect(_R(CXl - 0.13, yc - 1.05, CXl + 0.13, yc + 1.05), 0.12, 0.12, _paint(P.STEEL_DK, a))
            c.drawRect(_R(CXl - 0.02, yc + 1.05, CXl + 0.02, YT + 0.1), _paint(P.MUTED, a * 0.8))
            yt_, yr_ = yc + 0.75, yc - 0.75
            for yy, lab in ((yt_, "T"), (yr_, "R")):
                c.drawCircle(CXl, yy, 0.12, _paint(P.WARN, a))
                look.draw_text(c, lab, CXl, yy, 0.13, P.BG, a, "c", "bold")
            if t > t_cbl - 0.3 and t < t_us:
                # a pulse: T -> casing wall -> along the steel -> R; bright over free pipe, damped where bonded
                for k in range(2):
                    ph = ((t - t_cbl) / 1.1 + k * 0.5) % 1.0
                    for sx, xw in ((-1, bw0), (1, bw1)):
                        if ph < 0.2:
                            f = ph / 0.2
                            x, y = CXl + (xw - CXl) * f, yt_
                        elif ph < 0.8:
                            f = (ph - 0.2) / 0.6
                            x, y = xw, yt_ + (yr_ - yt_) * f
                        else:
                            f = (ph - 0.8) / 0.2
                            x, y = xw + (CXl - xw) * f, yr_
                        damp = 0.25 if y < YM else 1.0
                        look.draw_particles(c, [(x, y)], P.WARN, 0.06, a * damp, glow=True)
            if t > t_us - 0.2:          # ultrasonic: a rotating transducer looks all round the pipe
                ang = (t - t_us) * 5.0
                x = CXl + 0.5 * math.cos(ang)
                _trace(c, look, [(CXl, yc - 0.95), (x, yc - 0.95 + 0.1 * math.sin(ang))], P.WARN, a * _cl((t - t_us + 0.2) / 0.3), 0.045)
        st.procedural(s[2] + 0.2, s[5] + 0.6, 0.4, draw_tool)

        # waveform panel
        WX0, WX1, WY0, WY1 = -2.45, 2.95, 0.15, 2.95
        wcard = st.rect((WX0 + WX1) / 2, (WY0 + WY1) / 2, WX1 - WX0, WY1 - WY0, P.PANEL, 0.2)
        wct = st.text("what the receiver hears", WX0 + 0.25, WY1 - 0.3, 0.19, P.MUTED, 0.3, align="l", kind="bold")
        st.fade_in([wcard, wct], t_cbl - 0.3, 0.4)
        w_free = st.line(_wave_pts(WX0 + 0.25, 1.85, 3.3, 0.42, 1.0), P.WARN, 0.045, 0.35)
        w_bond = st.line(_wave_pts(WX0 + 0.25, 0.7, 3.3, 0.1, 3.5), P.WARN, 0.045, 0.35)
        l_free = st.text("free pipe:\nrings", WX1 - 1.4, 1.85, 0.17, P.TEXT, 0.35, align="l", kind="bold")
        l_bond = st.text("bonded:\ndamped", WX1 - 1.4, 0.7, 0.17, P.TEXT, 0.35, align="l", kind="bold")
        st.draw_on(w_free, t_cbl + 0.3, t_cbl + 1.6)
        st.fade_in(l_free, t_cbl + 0.8, 0.4)
        st.draw_on(w_bond, t_damp, t_damp + 1.2)
        st.fade_in(l_bond, t_damp + 0.4, 0.4)

        # ultrasonic map (all round the pipe), below the waveforms
        UX0, UX1, UY0, UY1 = -2.0, 2.75, -2.95, -0.75
        NA, ND = 24, 9
        cw, chh = (UX1 - UX0) / NA, (UY1 - UY0) / ND
        cells = []
        for i in range(NA):
            for j in range(ND):
                chan = i in (13, 14) and j <= 6
                cells.append(st.rect(UX0 + (i + 0.5) * cw, UY0 + (j + 0.5) * chh, cw * 0.92, chh * 0.9, P.MUD if chan else P.CEMENT, 0.3,
                                     alpha=0.95, role="flat"))
        ul = [st.text("0°", UX0, UY0 - 0.2, 0.15, P.MUTED, 0.3, kind="bold"), st.text("360°", UX1, UY0 - 0.2, 0.15, P.MUTED, 0.3, kind="bold"),
              st.text("around the pipe", (UX0 + UX1) / 2, UY0 - 0.22, 0.15, P.MUTED, 0.3, kind="bold"),
              st.text("depth", UX0 - 0.2, (UY0 + UY1) / 2, 0.15, P.MUTED, 0.3, align="r", kind="bold"),
              st.text("ultrasonic map", UX0, UY1 + 0.25, 0.17, P.TEXT, 0.3, align="l", kind="bold")]
        st.fade_in(ul, t_us - 0.2, 0.4)
        for k, o in enumerate(cells):
            st.fade_in(o, t_us + 0.05 * (k // ND), 0.25)
        chl = tag(st, UX0 + 14 * cw, UY1 + 0.25, "mud channel", P.MUD, 0.16, align="c", z=0.5)
        st.fade_in(chl, t_us + 1.4, 0.4)

        # ---------------- s5: contact, not seal
        t_cn = s[5]
        cn = st.text(wrap_to("A LOG MEASURES CONTACT, NOT SEAL", 0.3, 4.3, "bold"), 3.45, 0.35, 0.3, P.WARN, 0.5, align="l", kind="bold")
        st.fade_in(cn, t_cn - 0.05, 0.45)

        # ---------------- s6: a microannulus makes good cement look bad; a narrow channel slips past
        t_ma = W(b, 6, "microannulus")
        MX, MY0, MY1 = 3.45, -3.2, -0.65
        mcard = st.rect(5.6, (MY0 + MY1) / 2, 4.35, MY1 - MY0, P.PANEL, 0.2)
        mt = st.text("zoom: steel | gap | cement", MX + 0.2, MY1 - 0.25, 0.16, P.MUTED, 0.3, align="l", kind="bold")
        strips = [st.rect(MX + 0.55, (MY0 + MY1) / 2 - 0.15, 0.5, MY1 - MY0 - 0.75, P.STEEL, 0.3),
                  st.rect(MX + 0.85, (MY0 + MY1) / 2 - 0.15, 0.06, MY1 - MY0 - 0.75, P.BG, 0.31, role="hole"),
                  st.rect(MX + 1.3, (MY0 + MY1) / 2 - 0.15, 0.85, MY1 - MY0 - 0.75, P.CEMENT, 0.3)]
        gl = tag(st, MX + 0.88, MY0 + 0.3, "microannulus", P.BAD, 0.15, align="c", z=0.5)
        st.fade_in([mcard, mt] + strips, t_ma - 0.4, 0.4)
        st.fade_in(gl, t_ma, 0.4)
        w_ma = st.line(_wave_pts(MX + 2.0, -1.45, 2.0, 0.38, 1.1, cycles=5.0), P.WARN, 0.045, 0.35)
        st.draw_on(w_ma, W(b, 6, "look bad") - 0.6, W(b, 6, "look bad") + 0.6)
        wl = st.text("rings like free pipe:\ngood cement looks bad", MX + 3.0, -2.45, 0.15, P.TEXT, 0.35, kind="bold")
        st.fade_in(wl, W(b, 6, "look bad") - 0.2, 0.4)
        t_nc = W(b, 6, "narrow channel")
        xh = UX0 + 19.5 * cw
        hair = st.line([(xh, UY0 + 0.05), (xh + 0.02, UY1 - 0.05)], P.MUD, 0.025, 0.45)
        st.draw_on(hair, t_nc - 0.2, t_nc + 0.6, "BEZIER")
        hl = tag(st, xh, UY1 + 0.25, "too narrow to see", P.TEXT, 0.15, align="c", z=0.5)
        hld = leader(st, xh, UY1 + 0.08, xh, UY1 - 0.4, P.TEXT, 0.5)
        st.fade_in(hl + hld, t_nc + 0.3, 0.4)
        st.fade_out(chl, t_nc - 0.2, 0.3)

        # ---------------- s7: weigh it all together
        t_w = s[7]
        clear = [lh] + base + fills + zl + [wcard, wct, w_free, w_bond, l_free, l_bond] + cells + ul + chl + [cn, mcard, mt] + strips + gl + \
            [w_ma, wl, hair] + hl + hld
        st.fade_out(clear, t_w - 0.4, 0.4)
        FX = -2.7
        ft = st.text("WEIGH IT ALL TOGETHER", FX - 0.25, 2.75, 0.36, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(ft, t_w, 0.45)
        items = [("full returns", "no losses during the job"), ("the right volumes", "pumped as planned"),
                 ("a plug bump on time", "at the calculated volume"), ("logs, where it matters", "contact, not proof of a seal"),
                 ("the pressure test at the shoe", "after drilling out")]
        for i, (h, sub) in enumerate(items):
            y = 1.75 - 0.95 * i
            t = t_w + 0.35 + 0.3 * i if i < 4 else W(b, 7, "pressure test") - 0.1
            ck = _check(st, FX, y, t, z=0.6)
            ht = st.text(h, FX + 0.5, y + 0.13, 0.26, P.TEXT, 0.6, align="l", kind="bold")
            sb = st.text(sub, FX + 0.5, y - 0.27, 0.17, P.MUTED, 0.6, align="l")
            st.fade_in([ht, sb], t - 0.1, 0.4)


def build(st, tl):
    F.header(st, tl)
    F.well_strip(st, 0.0, tl.dur, strings=["30in conductor", "20in surface casing", "13-3/8in intermediate", "9-5/8in intermediate"], marker=M.TD)
    beat_jobs(st, tl)
    beat_utube(st, tl)
    beat_displacement(st, tl)
    beat_slurry(st, tl)
    beat_danger(st, tl)
    beat_logs(st, tl)
