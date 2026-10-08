"""Ch 2: Top hole: drilling with no safety net (riserless drilling, why it is allowed, spud, guide base, conductor as a
pile, surface casing + high-pressure housing, the cement U-tube, the wellhead as nested seats, wellhead fatigue).

Every animation is keyed to the word being spoken (b.word). Numbers come from well_model (water depth, shoes, sizes,
pore / fracture gradient). Fluids: pumped seawater = pale sea-blue particles, gel sweeps = mud amber, cuttings = rock
brown, cement = P.CEMENT grey everywhere, shallow gas = crimson, kill mud = kill-mud amber; forces are white arrows.
No camera moves: the header, well strip and term cards live in world space, so detail is shown by re-staging instead."""
from __future__ import annotations
import math
import random

import numpy as np
import skia

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common.look import col, hex_rgb, lighten, darken, wrap_to
from scenes.common.shapes import pill
from scenes.common.stage import ease_inout

TITLE = "Top hole: drilling with no safety net"

# chapter-local colours (each keeps one meaning in this chapter)
SEAWATER = "#a9cdf2"      # pumped seawater (not formation water): pale sea-blue particles
CUTTINGS = "#9b7a55"      # rock chips
SILT = "#8f8170"          # fine cloud of the cuttings plume
SEABED_LINE = "#8b7a5e"
RUBBER = "#2b303b"        # cement plug, seal element before it is set
ROV_BODY = "#d7dde6"
C_COND, C_SURF, C_INT = "#56667d", "#71839c", "#98a9bf"   # 30 in, 20 in, 13-3/8 in (as in shapes.STRING_COLORS)

PROG = {s.name: s for s in M.programme()}
WD = M.WATER_DEPTH                                   # 300 m
COND_SHOE = PROG["30in conductor"].shoe              # 390 m
SURF_SHOE = PROG["20in surface casing"].shoe         # 1,000 m
COND_LEN = COND_SHOE - WD                            # 90 m below the seabed
BELOW_SB = SURF_SHOE - WD                            # 700 m below the seabed


# ====================================================================================================== helpers
def _w(b, i, needle, frac=0.0):
    """Time `needle` is spoken in sentence i of beat b (fails loudly if the script changed)."""
    txt = b._sentences()[i]
    if needle.lower() not in txt.lower():
        raise KeyError(f"{b.id} sentence {i}: {needle!r} not in {txt!r}")
    return b.word(i, needle, frac)


def _clamp(v, a, b):
    return a if v < a else (b if v > b else v)


def _ramp(t, a, b):
    return _clamp((t - a) / max(b - a, 1e-6), 0.0, 1.0)


def _piecewise(keys):
    """keys [(t, value, 'BEZIER'|'LINEAR'), ...] -> f(t) (constant outside, easing of a segment = its left key)."""
    def f(t):
        if t <= keys[0][0]:
            return keys[0][1]
        for (ta, va, e), (tb, vb, _) in zip(keys[:-1], keys[1:]):
            if t <= tb:
                u = (t - ta) / max(tb - ta, 1e-9)
                return va + (vb - va) * (ease_inout(u) if e == "BEZIER" else u)
        return keys[-1][1]
    return f


def _drive(st, obj, t0, t1, fn, fps=20):
    """Key an object densely from fn(t) -> {'loc': (x, y), 'scale': (sx, sy)} so several objects stay exactly in sync."""
    n = max(2, int(math.ceil((t1 - t0) * fps)) + 1)
    for i in range(n):
        t = t0 + (t1 - t0) * i / (n - 1)
        d = fn(t)
        if "loc" in d:
            obj.track("loc").set(t, tuple(d["loc"]), "LINEAR")
        if "scale" in d:
            obj.track("scale").set(t, tuple(d["scale"]), "LINEAR")


def _seascape(st, x0, x1, y_top, y_sb, y_bot, clay=0.0, z=0.0):
    """Sea over seabed over (soft clay over) rock, as one cutaway block."""
    cx, w = (x0 + x1) / 2, x1 - x0
    out = [st.rect(cx, (y_top + y_sb) / 2, w, y_top - y_sb, P.SEA, z)]
    if clay > 0:
        out.append(st.rect(cx, y_sb - clay / 2, w, clay, P.SEABED, z))
        out.append(st.rect(cx, (y_sb - clay + y_bot) / 2, w, y_sb - clay - y_bot, P.ROCK, z))
    else:
        out.append(st.rect(cx, (y_sb + y_bot) / 2, w, y_sb - y_bot, P.ROCK, z))
    out.append(st.rect(cx, y_sb, w, 0.05, SEABED_LINE, z + 0.02))
    return out


def _callout(st, x, y, text, t, target=None, fg=P.TEXT, bg=P.PANEL2, size=0.2, align="l", z=2.0, t_out=None, d=0.4):
    """Pill label at (x, y) (align: which side x is) with an optional hairline leader + dot to `target`."""
    parts = pill(st, x, y, text, bg, fg, size, z, align=align)
    plate = parts[0]
    w, h = plate.scale[0], plate.scale[1]
    px = plate.location[0]
    if target is not None:
        tx, ty = target
        sx = _clamp(tx, px - w / 2, px + w / 2)
        sy = _clamp(ty, y - h / 2, y + h / 2)
        parts.append(st.line([(sx, sy), (tx, ty)], P.TEXT, 0.022, z - 0.02, alpha=0.7))
        parts.append(st.circle(tx, ty, 0.045, P.TEXT, z - 0.01))
    st.fade_in(parts, t, d)
    if t_out is not None:
        st.fade_out(parts, t_out, 0.4)
    return parts


def _x_mark(st, x, y, r, t, z=1.5, width=0.09):
    """A red cross drawn on stroke by stroke."""
    a = st.line([(x - r, y + r), (x + r, y - r)], P.BAD, width, z)
    c = st.line([(x - r, y - r), (x + r, y + r)], P.BAD, width, z)
    st.draw_on(a, t, t + 0.3, "BEZIER")
    st.draw_on(c, t + 0.22, t + 0.52, "BEZIER")
    return [a, c]


def _dashed_rect(st, x0, y0, x1, y1, color=P.MUTED, z=0.6, width=0.035):
    out = []
    for p, q in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        out += st.dashed(p, q, color, width, 0.16, 0.1, z)
    return out


def _check(st, x, y, t, s=0.22, z=1.2):
    ln = st.line([(x - s, y), (x - s * 0.35, y - s * 0.62), (x + s, y + s * 0.7)], P.SAFE, 0.07, z)
    st.draw_on(ln, t, t + 0.45, "BEZIER")
    return [ln]


def _rig(st, x, y, z=0.4, w=1.6):
    """Small semi-submersible silhouette: pontoon at the waterline y, columns, deck, derrick (all in steel)."""
    out = [st.rect(x, y - 0.12, w, 0.14, P.STEEL_DK, z),
           st.rect(x - w * 0.35, y + 0.05, 0.16, 0.3, P.STEEL_DK, z),
           st.rect(x + w * 0.35, y + 0.05, 0.16, 0.3, P.STEEL_DK, z),
           st.rect(x, y + 0.26, w * 0.95, 0.13, P.STEEL, z + 0.01),
           st.poly([(x - 0.18, y + 0.32), (x + 0.18, y + 0.32), (x + 0.04, y + 0.62), (x - 0.04, y + 0.62)], P.STEEL_DK, z + 0.02)]
    return out


# ---------------------------------------------------------------- particles
def _polyline(pts):
    P_ = np.array(pts, dtype=float)
    seg = np.hypot(*(P_[1:] - P_[:-1]).T)
    cum = np.concatenate([[0.0], np.cumsum(seg)])

    def at(s):
        i = min(max(int(np.searchsorted(cum, s, side="right")) - 1, 0), len(seg) - 1)
        f = (s - cum[i]) / max(seg[i], 1e-9)
        p = P_[i] + (P_[i + 1] - P_[i]) * f
        d = (P_[i + 1] - P_[i]) / max(seg[i], 1e-9)
        return p, d
    return at, float(cum[-1])


def _stream(st, pts, t0, t1, color=SEAWATER, rate=7.0, speed=1.0, r=0.045, z=0.5, jitter=0.0, alpha=0.9, glow=True,
            color_fn=None, t_stop=None, fade=0.4, seed=1, tail_fade=0.0):
    """Particles emitted at pts[0] (rate per s) that travel along the polyline at `speed`: the stream has a visible
    FRONT, so a fluid can be shown arriving where the narration says it does. color_fn(t_emit, k) -> (color, r)."""
    at, L = _polyline(pts)
    t_stop = t1 if t_stop is None else t_stop
    life = L / speed
    rng = random.Random(seed)
    side = [(rng.random() - 0.5) * 2 * jitter for _ in range(997)]

    def draw(c, t, look):
        env = min(1.0, (t1 - t) / fade) if fade > 0 else 1.0
        if env <= 0:
            return
        kmax = int(math.floor((min(t, t_stop) - t0) * rate))
        kmin = max(0, int(math.ceil((t - t0 - life) * rate)))
        groups = {}
        for k in range(kmin, kmax + 1):
            te = t0 + k / rate
            s = speed * (t - te)
            if s < 0 or s > L:
                continue
            p, d = at(s)
            if jitter:
                p = p + np.array([-d[1], d[0]]) * side[k % 997]
            colr, rr = (color, r) if color_fn is None else color_fn(te, k)
            if colr is None:
                continue
            a = 1.0
            if tail_fade > 0 and s > L - tail_fade:
                a = (L - s) / tail_fade
            groups.setdefault((colr, rr, round(a, 1)), []).append(p)
        for (colr, rr, a), pos in groups.items():
            look.draw_particles(c, pos, colr, rr, alpha * env * a, glow)
    st.procedural(t0, t1, z, draw)


def _spill(st, x0, y0, t0, t1, gap, chip=CUTTINGS, cloud=SILT, rate=9.0, life=2.4, reach=1.5, height=0.65, drift=0.22,
           z=0.55, seed=5, cloud_alpha=0.26):
    """Returns leaving the hole mouth at (x0 +- gap, y0): chips arc out and land on the seabed, a fine cloud billows up and
    drifts with the current. Continuous emitter between t0 and t1."""
    rng = random.Random(seed)
    params = [(rng.choice((-1, 1)), rng.uniform(0.25, 1.0), rng.uniform(0.4, 1.0), rng.uniform(0.5, 1.3), rng.uniform(0.6, 1.4))
              for _ in range(997)]

    def draw(c, t, look):
        env = min(1.0, (t - t0) / 0.4, (t1 - t) / 0.4)
        if env <= 0:
            return
        kmax = int(math.floor((t - t0) * rate))
        kmin = max(0, int(math.ceil((t - t0 - life * 1.8) * rate)))
        chips = []
        blur = skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(2.0, 0.09 * look.k), False)
        for k in range(kmin, kmax + 1):
            side, fr, fh, fc, fz = params[k % 997]
            age = t - (t0 + k / rate)
            xs = x0 + side * (gap - 0.06)
            u = age / life
            if 0 <= u <= 1:
                x = xs + side * reach * fr * (1 - (1 - u) ** 2) + drift * age * 0.4
                y = y0 + 0.03 + height * fh * 4 * u * (1 - u)
                a = 1.0 if u < 0.85 else (1 - u) / 0.15
                chips.append((x, y, a))
            uc = age / (life * 1.8)
            if 0 <= uc <= 1:
                x = xs + side * reach * 0.55 * fr * (1 - (1 - uc) ** 2) + drift * age * fz
                y = y0 + 0.08 + height * 1.5 * fc * uc ** 0.7
                rr = 0.07 + 0.28 * uc
                p = skia.Paint(Color=col(hex_rgb(cloud), cloud_alpha * env * (1 - uc) ** 1.2), AntiAlias=True, MaskFilter=blur)
                c.drawCircle(x, y, rr, p)
        for a in (1.0, 0.6, 0.3):
            pos = [(x, y) for x, y, aa in chips if abs(aa - a) < 0.2 or (a == 0.3 and aa < 0.4)]
            if pos:
                look.draw_particles(c, pos, chip, 0.042, env * a, glow=False)
    st.procedural(t0, t1, z, draw)


def _mound(st, x0, y0, t0, t1, color=CUTTINGS, hmax=0.3, width=1.5, gap=0.5, z=0.52, t_end=None):
    """A pile building up on the seabed around the hole mouth (both sides), from t0 (empty) to t1 (full)."""
    t_end = t_end if t_end is not None else t1

    def draw(c, t, look):
        f = _ramp(t, t0, t1)
        h = hmax * (1 - (1 - f) ** 2)
        if h < 0.004:
            return
        rgb = hex_rgb(color)
        for side in (-1, 1):
            path = skia.Path()
            path.moveTo(x0 + side * gap, y0)
            for i in range(25):
                u = i / 24
                bump = math.sin(math.pi / 2 * min(u * 5, 1.0)) * (1 - u) ** 1.7
                path.lineTo(x0 + side * (gap + width * u), y0 + h * bump)
            path.close()
            g = skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y0 + hmax)],
                                               [col(darken(rgb, 0.25), 1.0), col(lighten(rgb, 0.08), 1.0)])
            c.drawPath(path, skia.Paint(Shader=g, AntiAlias=True))
    st.procedural(t0, t_end, z, draw)


def _bubbles(st, x0, y0, t0, t1, color=P.GAS, rate=6.0, rise=0.8, life=3.0, spread=0.12, r=0.045, z=0.6, wobble=0.06,
             seed=3, y_max=None, drift=0.0, grow=0.6, alpha=0.95):
    """Gas bubbles released at (x0 +- spread, y0) rising (and growing: gas expands as it rises) with a wobble."""
    rng = random.Random(seed)
    params = [(rng.uniform(-1, 1), rng.uniform(0.75, 1.25), rng.uniform(0, 6.28), rng.uniform(0.7, 1.3)) for _ in range(997)]

    def draw(c, t, look):
        env = min(1.0, (t - t0) / 0.3, (t1 - t) / 0.5)
        if env <= 0:
            return
        kmax = int(math.floor((t - t0) * rate))
        kmin = max(0, int(math.ceil((t - t0 - life) * rate)))
        groups = {}
        for k in range(kmin, kmax + 1):
            dx, fv, ph, fr = params[k % 997]
            age = t - (t0 + k / rate)
            if age < 0 or age > life:
                continue
            y = y0 + rise * fv * age
            if y_max is not None and y > y_max:
                continue
            x = x0 + dx * spread + wobble * math.sin(3.0 * age + ph) + drift * age
            u = age / life
            a = min(1.0, (1 - u) / 0.3)
            if y_max is not None:
                a = min(a, (y_max - y) / 0.3)
            rr = round(r * fr * (1 + grow * u), 3)
            groups.setdefault((rr, round(a, 1)), []).append((x, y))
        for (rr, a), pos in groups.items():
            look.draw_particles(c, pos, color, rr, alpha * env * a, True)
    st.procedural(t0, t1, z, draw)


# ---------------------------------------------------------------- procedural steel / the bending well column
def _steel_paint(x0, x1, rgb, alpha):
    g = skia.GradientShader.MakeLinear([skia.Point(x0, 0), skia.Point(x1, 0)],
                                       [col(darken(rgb, 0.38), alpha), col(lighten(rgb, 0.30), alpha), col(rgb, alpha),
                                        col(darken(rgb, 0.10), alpha), col(darken(rgb, 0.42), alpha)], [0.0, 0.26, 0.5, 0.78, 1.0])
    return skia.Paint(Shader=g, AntiAlias=True)


def _tube(c, dx, cx, ya, yb, hw, color, alpha, n=16, flat=False):
    """A straight part of the column (half-width hw) between ya < yb, laterally deflected by dx(y)."""
    if alpha <= 0.003 or yb <= ya:
        return
    ys = [ya + (yb - ya) * i / n for i in range(n + 1)]
    path = skia.Path()
    path.moveTo(cx + dx(ys[0]) - hw, ys[0])
    for y in ys[1:]:
        path.lineTo(cx + dx(y) - hw, y)
    for y in reversed(ys):
        path.lineTo(cx + dx(y) + hw, y)
    path.close()
    rgb = hex_rgb(color)
    xm = cx + dx((ya + yb) / 2)
    if flat:
        c.drawPath(path, skia.Paint(Color=col(rgb, alpha), AntiAlias=True))
    else:
        c.drawPath(path, _steel_paint(xm - hw, xm + hw, rgb, alpha))


def _down_arrow(c, x, y0, y1, alpha, width=0.07, head=0.22, color=P.TEXT):
    rgb = hex_rgb(color)
    p = skia.Paint(Color=col(rgb, alpha), AntiAlias=True, StrokeWidth=width, Style=skia.Paint.kStroke_Style,
                   StrokeCap=skia.Paint.kRound_Cap)
    c.drawLine(x, y0, x, y1 + head * 0.8, p)
    path = skia.Path()
    path.moveTo(x, y1)
    path.lineTo(x - head * 0.55, y1 + head)
    path.lineTo(x + head * 0.55, y1 + head)
    path.close()
    c.drawPath(path, skia.Paint(Color=col(rgb, alpha), AntiAlias=True))


class Column:
    """The well as a structure: conductor pile in the soil, wellhead, BOP, riser up to the rig. Drawn procedurally so
    the whole column can bend as a cantilever fixed a little below the mudline (rig and riser motion)."""

    def __init__(self, st, t0, t1, cx, y_sb, y_shoe, y_rig, z=0.3, t_inner=None, t_wh=None, t_bop=None, t_riser=None,
                 amp=None, weights=False, fade=0.45, bop_h=1.3, wh_h=0.6):
        self.cx, self.y_sb, self.y_shoe, self.y_rig = cx, y_sb, y_shoe, y_rig
        self.y_fix = y_sb - 0.55
        self.y_wh = y_sb + wh_h
        self.y_bop = self.y_wh + bop_h
        self.amp = amp or (lambda t: 0.0)
        big = 1e9
        t_inner = big if t_inner is None else t_inner
        t_wh = big if t_wh is None else t_wh
        t_bop = big if t_bop is None else t_bop
        t_riser = big if t_riser is None else t_riser
        self.t_bop = t_bop

        def draw(c, t, look):
            a0 = _ramp(t, t0, t0 + fade) * min(1.0, (t1 - t) / 0.3)
            A = self.amp(t)
            span = self.y_rig - self.y_fix

            def dx(y):
                if y <= self.y_fix:
                    return 0.0
                u = (y - self.y_fix) / span
                return A * u * u
            # conductor pile (30 in) + optional cemented 20 in inside it
            ai = a0 * _ramp(t, t_inner, t_inner + 0.6)
            if ai > 0:
                _tube(c, dx, cx, y_shoe - 0.25, y_sb + 0.05, 0.25, P.CEMENT, ai, flat=False)
                _tube(c, dx, cx, y_shoe - 0.25, y_sb + 0.05, 0.17, C_SURF, ai)
                _tube(c, dx, cx, y_shoe - 0.25, y_sb + 0.05, 0.12, P.SEA, ai, flat=True)
            for s in (-1, 1):
                _tube(c, lambda y: dx(y) + s * 0.27, cx, y_shoe, y_sb + 0.08, 0.05, C_COND, a0)
            # wellhead: low-pressure housing on the conductor, high-pressure housing on top
            aw = a0 * _ramp(t, t_wh, t_wh + 0.5)
            if aw > 0:
                _tube(c, dx, cx, y_sb - 0.05, y_sb + wh_h * 0.55, 0.42, C_COND, aw)
                _tube(c, dx, cx, y_sb + wh_h * 0.55, self.y_wh, 0.33, C_SURF, aw)
            # BOP stack drops on from above (ease-out), with ram bonnets so it reads as a BOP
            ab = a0 * _ramp(t, t_bop, t_bop + 0.4)
            if ab > 0:
                drop = 1.4 * (1 - _ramp(t, t_bop, t_bop + 1.0)) ** 3
                ya, yb = self.y_wh + drop, self.y_bop + drop
                d2 = lambda y: dx(y - drop) if drop else dx(y)
                _tube(c, d2, cx, ya, yb, 0.5, P.STEEL_DK, ab)
                for k in range(3):
                    yy = ya + (yb - ya) * (0.18 + 0.25 * k)
                    _tube(c, d2, cx, yy - 0.09, yy + 0.09, 0.7, P.STEEL, ab)
                _tube(c, d2, cx, yb - 0.05, yb + 0.12, 0.3, P.STEEL, ab)
                if weights:
                    xm = cx + d2((ya + yb) / 2)
                    _down_arrow(c, xm + 0.95, yb - 0.05, ya + 0.25, ab * _ramp(t, t_bop + 0.9, t_bop + 1.3), 0.09, 0.28)
            # riser to the rig, and the rig (rig moves with the top of the riser)
            ar = a0 * _ramp(t, t_riser, t_riser + 0.5)
            if ar > 0:
                _tube(c, dx, cx, self.y_bop + 0.12, y_rig - 0.05, 0.13, P.STEEL, ar)
                xr = cx + dx(y_rig)
                rgb = hex_rgb(P.STEEL_DK)
                for (x, y, w, h, colr) in ((xr, y_rig - 0.05, 1.9, 0.16, P.STEEL_DK), (xr - 0.65, y_rig + 0.12, 0.16, 0.3, P.STEEL_DK),
                                           (xr + 0.65, y_rig + 0.12, 0.16, 0.3, P.STEEL_DK), (xr, y_rig + 0.32, 1.8, 0.13, P.STEEL)):
                    rr = skia.Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
                    g = skia.GradientShader.MakeLinear([skia.Point(0, rr.bottom()), skia.Point(0, rr.top())],
                                                       [col(darken(hex_rgb(colr), 0.38), ar), col(lighten(hex_rgb(colr), 0.25), ar),
                                                        col(darken(hex_rgb(colr), 0.4), ar)], [0.0, 0.4, 1.0])
                    c.drawRect(rr, skia.Paint(Shader=g, AntiAlias=True))
                path = skia.Path()
                path.moveTo(xr - 0.18, y_rig + 0.38)
                path.lineTo(xr + 0.18, y_rig + 0.38)
                path.lineTo(xr + 0.04, y_rig + 0.62)
                path.lineTo(xr - 0.04, y_rig + 0.62)
                path.close()
                c.drawPath(path, skia.Paint(Color=col(rgb, ar), AntiAlias=True))
        st.procedural(t0, t1, z, draw)

    def dx(self, t, y):
        A = self.amp(t)
        if y <= self.y_fix:
            return 0.0
        u = (y - self.y_fix) / (self.y_rig - self.y_fix)
        return A * u * u


def _springs(st, col_, t0, t1, depths, reach=0.85, z=0.32, half=0.32):
    """Lateral soil springs from a fixed soil anchor to the pile wall (they follow the pile's deflection)."""
    def draw(c, t, look):
        a = _ramp(t, t0, t0 + 0.5) * min(1.0, (t1 - t) / 0.3)
        if a <= 0:
            return
        p = skia.Paint(Color=col(hex_rgb(P.MUTED), a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.035,
                       StrokeJoin=skia.Paint.kRound_Join, StrokeCap=skia.Paint.kRound_Cap)
        for y in depths:
            for s in (-1, 1):
                xw = col_.cx + col_.dx(t, y) + s * half
                xa = col_.cx + s * (half + reach)
                path = skia.Path()
                path.moveTo(xa, y)
                n = 7
                for i in range(1, n):
                    f = i / n
                    path.lineTo(xa + (xw - xa) * f, y + (0.09 if i % 2 else -0.09))
                path.lineTo(xw, y)
                c.drawPath(path, p)
                c.drawLine(xa, y - 0.16, xa, y + 0.16, p)
                for k in range(3):
                    yy = y - 0.12 + 0.12 * k
                    c.drawLine(xa, yy, xa + s * 0.12, yy - 0.1, p)
    st.procedural(t0, t1, z, draw)


def _moment_arc(st, x, y, t0, t1, r=0.75, z=0.9, color=P.TEXT):
    """Double-headed curved arrow (bending moment, back and forth) around (x, y)."""
    def draw(c, t, look):
        a = _ramp(t, t0, t0 + 0.5) * min(1.0, (t1 - t) / 0.3)
        if a <= 0:
            return
        rgb = hex_rgb(color)
        p = skia.Paint(Color=col(rgb, a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.06,
                       StrokeCap=skia.Paint.kRound_Cap)
        a0, a1 = 25.0, 155.0
        path = skia.Path()
        path.addArc(skia.Rect(x - r, y - r * 0.55, x + r, y + r * 0.55), a0, a1 - a0)
        c.drawPath(path, p)
        for ang, sgn in ((a0, -1), (a1, 1)):
            th = math.radians(ang)
            px, py = x + r * math.cos(th), y + r * 0.55 * math.sin(th)
            tx, ty = -math.sin(th) * r * sgn, math.cos(th) * r * 0.55 * sgn
            L = math.hypot(tx, ty)
            tx, ty = tx / L, ty / L
            nx, ny = -ty, tx
            hp = skia.Path()
            hp.moveTo(px - tx * 0.02, py - ty * 0.02)
            hp.lineTo(px + tx * 0.2 + nx * 0.1, py + ty * 0.2 + ny * 0.1)
            hp.lineTo(px + tx * 0.2 - nx * 0.1, py + ty * 0.2 - ny * 0.1)
            hp.close()
            c.drawPath(hp, skia.Paint(Color=col(rgb, a), AntiAlias=True))
    st.procedural(t0, t1, z, draw)


# ====================================================================================================== 2.01
def beat_riserless(st, tl):
    b = tl["2.01"]
    s = b.sent
    TOP, SB, BOT = 3.85, 0.2, -3.6
    WX, HW, HB = -1.5, 1.0, -3.0          # well x, hole width, final hole bottom
    BIT_H, COL_H, PIPE_W, COL_W = 0.26, 1.15, 0.13, 0.3
    t_a = b.start + 0.2
    t_b = _w(b, 0, "drill") + 0.6           # bit tags the seabed as "drill" is said
    t_c = _w(b, 2, "drill string")          # first metres drilled while the strange first section is announced
    ybit = _piecewise([(t_a, SB + 1.4, "BEZIER"), (t_b, SB, "LINEAR"), (t_c, HB, "LINEAR")])
    with st.span(b.start, b.end):
        scene = _seascape(st, -6.2, 3.1, TOP, SB, BOT, clay=0.7)
        hole = st.rect(WX, SB, HW, 0.0001, P.BG, 0.1, anchor="t")
        pipe = st.rect(WX, TOP, PIPE_W, 1.0, P.STEEL, 0.3, anchor="t")
        collar = st.rect(WX, 0, COL_W, COL_H, P.STEEL_DK, 0.31)
        bit = st.rect(WX, 0, HW * 0.86, BIT_H * 0.7, P.STEEL_DK, 0.32)
        teeth = st.poly([(WX - HW * 0.43, 0), (WX + HW * 0.43, 0), (WX + HW * 0.25, -BIT_H * 0.3), (WX - HW * 0.25, -BIT_H * 0.3)],
                        "#4b5566", 0.32)
        t_off = teeth.location[1]
        _drive(st, hole, b.start, t_c + 0.05, lambda t: {"scale": (HW, max(SB - ybit(t), 0.0001))})
        _drive(st, pipe, b.start, t_c + 0.05, lambda t: {"scale": (PIPE_W, TOP - (ybit(t) + BIT_H + COL_H))})
        _drive(st, collar, b.start, t_c + 0.05, lambda t: {"loc": (WX, ybit(t) + BIT_H + COL_H / 2)})
        _drive(st, bit, b.start, t_c + 0.05, lambda t: {"loc": (WX, ybit(t) + BIT_H * 0.65)})
        _drive(st, teeth, b.start, t_c + 0.05, lambda t: {"loc": (WX, ybit(t) + BIT_H * 0.3 + t_off)})

        # the string turns: stripes sweep across the collar
        def spin(c, t, look):
            yc = ybit(t) + BIT_H + COL_H / 2
            for k in range(3):
                ph = 2 * math.pi * (1.6 * (t - t_a) + k / 3)
                if math.cos(ph) <= 0:
                    continue
                x = WX + COL_W * 0.42 * math.sin(ph)
                p = skia.Paint(Color=col((0.1, 0.12, 0.16), 0.45 * math.cos(ph)), AntiAlias=True)
                c.drawRect(skia.Rect(x - 0.022, yc - COL_H / 2 + 0.05, x + 0.022, yc + COL_H / 2 - 0.05), p)
        st.procedural(t_a, b.end, 0.33, spin)

        # drill string: the pipe that turns the bit, hanging in open sea
        _callout(st, WX + 0.95, 2.95, "drill string", _w(b, 2, "drill string"), target=(WX + PIPE_W / 2, 2.95))
        t_turn = _w(b, 2, "turns the bit")
        ybot = HB + BIT_H + COL_H / 2

        def turn_arrow(c, t, look):
            a = _ramp(t, t_turn, t_turn + 0.4) * (1 - _ramp(t, t_turn + 3.4, t_turn + 3.9))
            if a <= 0:
                return
            p = skia.Paint(Color=col(hex_rgb(P.TEXT), a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.05,
                           StrokeCap=skia.Paint.kRound_Cap)
            r = skia.Rect(WX - 0.42, ybot - 0.13, WX + 0.42, ybot + 0.13)
            path = skia.Path()
            path.addArc(r, 200, 140)
            c.drawPath(path, p)
            hp = skia.Path()
            hx, hy = WX + 0.42 * math.cos(math.radians(340)), ybot + 0.13 * math.sin(math.radians(340))
            hp.moveTo(hx + 0.12, hy + 0.05)
            hp.lineTo(hx - 0.05, hy + 0.1)
            hp.lineTo(hx - 0.02, hy - 0.09)
            hp.close()
            c.drawPath(hp, skia.Paint(Color=col(hex_rgb(P.TEXT), a), AntiAlias=True))
        st.procedural(t_turn, t_turn + 4.0, 0.9, turn_arrow)
        tb = _callout(st, WX - 0.75, ybot, "turns the bit", t_turn + 0.2, target=(WX - 0.45, ybot), align="r", t_out=t_turn + 3.5)

        # 300 m of open sea
        t_sea = _w(b, 2, "open sea")
        dimx = WX - 1.15
        dim = [st.line([(dimx, TOP - 0.06), (dimx, SB + 0.06)], P.TEXT, 0.025, 0.8, alpha=0.8),
               st.rect(dimx, TOP - 0.06, 0.24, 0.025, P.TEXT, 0.8), st.rect(dimx, SB + 0.06, 0.24, 0.025, P.TEXT, 0.8)]
        st.draw_on(dim[0], t_sea, t_sea + 0.6, "BEZIER")
        st.fade_in(dim[1:], t_sea, 0.3)
        dl = pill(st, dimx - 0.2, (TOP + SB) / 2, f"{WD:.0f} m of open sea", P.PANEL2, P.TEXT, 0.2, 2.0, align="r")
        st.fade_in(dl, t_sea + 0.3, 0.4)
        st.fade_out(dim + dl, s[3] + 0.2, 0.5)

        # ghost riser (with the mud it would bring back), then a ghost BOP on the seabed: both crossed out
        t_r = _w(b, 2, "no riser")
        t_carry = _w(b, 2, "carry the mud")
        t_rx = _w(b, 2, "to the rig", 1.0)
        t_bop = _w(b, 2, "no blowout preventer")
        BOP_T = SB + 1.15
        ghost_r = st.dashed((WX - 0.45, BOP_T), (WX - 0.45, TOP - 0.02), P.MUTED, 0.04, 0.18, 0.12, 0.6) + \
            st.dashed((WX + 0.45, BOP_T), (WX + 0.45, TOP - 0.02), P.MUTED, 0.04, 0.18, 0.12, 0.6)
        st.fade_in(ghost_r, t_r, 0.5)
        for xx in (WX - 0.3, WX + 0.3):
            _stream(st, [(xx, BOP_T + 0.05), (xx, TOP - 0.05)], t_carry, t_bop + 0.6, P.MUD, rate=3.0, speed=1.4, r=0.04,
                    z=0.58, alpha=0.55, seed=11 if xx < WX else 12)
        xr = _x_mark(st, WX, (BOP_T + TOP) / 2 + 0.2, 0.55, t_rx - 0.2)
        nr = _callout(st, WX + 0.95, 2.1, "no riser", t_rx - 0.1, fg=P.BAD)
        ghost_b = _dashed_rect(st, WX - 0.8, SB + 0.04, WX + 0.8, BOP_T)
        st.fade_in(ghost_b, t_bop, 0.4)
        xb = _x_mark(st, WX, (SB + BOP_T) / 2, 0.45, t_bop + 0.35)
        nb = _callout(st, WX + 0.95, (SB + BOP_T) / 2, "no blowout preventer", t_bop + 0.4, fg=P.BAD)
        ghosts = ghost_r + ghost_b + xr + xb
        st.fade_out(ghosts, s[3] + 0.1, 0.6)
        st.fade_out(nr + nb, s[3] + 0.1, 0.5)
        title = st.text("RISERLESS DRILLING", -5.95, 3.42, 0.32, P.TEXT, 2.0, align="l", kind="bold")
        st.fade_in(title, _w(b, 3, "riserless"), 0.5)

        # circulation: seawater (+ gel sweeps) down the pipe, out of the bit, up the annulus, onto the seabed
        t_dn = _w(b, 4, "Seawater")
        t_gel = _w(b, 4, "slugs of thick gel")
        t_bitout = _w(b, 4, "out of the bit")
        t_spill = _w(b, 4, "spilling")
        t_cut = _w(b, 4, "the cuttings")
        down = [(WX, TOP - 0.02), (WX, HB + 0.08)]
        v_dn = (TOP - HB) / max(t_bitout - t_dn, 1.0)

        def gel_fn(te, k):
            if te >= t_gel - 0.3 and ((te - t_gel + 0.3) % 3.2) < 0.9:
                return P.MUD, 0.055
            return SEAWATER, 0.042
        _stream(st, down, t_dn, b.end, SEAWATER, rate=7.0, speed=v_dn, z=0.45, color_fn=gel_fn, seed=2)
        st.ripple(WX, HB + 0.12, t_bitout - 0.15, t_bitout + 1.2, SEAWATER, period=0.6, r0=0.12, r1=0.65, z=0.6)
        up_len = (SB - HB) + 0.6
        v_up = up_len / max(t_spill - t_bitout + 0.2, 1.0)
        for sd in (-1, 1):
            path = [(WX + sd * 0.05, HB + 0.04), (WX + sd * 0.47, HB + 0.07), (WX + sd * 0.47, HB + BIT_H + 0.05),
                    (WX + sd * 0.31, HB + BIT_H + 0.3), (WX + sd * 0.31, SB - 0.01)]

            def up_fn(te, k):
                return (CUTTINGS, 0.05) if k % 3 == 0 else (SEAWATER, 0.038)
            _stream(st, path, t_bitout - 0.2, b.end, rate=6.0, speed=v_up, z=0.46, color_fn=up_fn, seed=4 + sd, jitter=0.05)
        _spill(st, WX, SB, t_spill - 0.1, b.end, HW / 2, rate=10.0, reach=1.6, height=0.6, drift=0.25)
        _mound(st, WX, SB + 0.02, t_spill, b.end, CUTTINGS, hmax=0.28, width=1.6, gap=HW / 2 + 0.02)
        _callout(st, WX - 0.35, 1.55, "seawater + gel sweeps, pumped down", t_dn + 0.2, target=(WX - 0.07, 1.55), align="r")
        _callout(st, WX - HW / 2 - 0.3, -1.45, "returns + cuttings, up around the pipe", _w(b, 4, "back up around"),
                 target=(WX - 0.31, -1.45), align="r")
        _callout(st, WX + 1.05, SB + 0.85, "cuttings pile up on the seabed", t_cut, target=(WX + 0.95, SB + 0.12))

        # what flows: a small legend card (bottom-right, clear of the term cards)
        lx0, ly = 3.45, -1.2
        card = st.rect(lx0 + 2.05, ly - 1.05, 4.1, 2.1, P.PANEL, 0.2)
        head = st.text("WHAT FLOWS", lx0 + 0.25, ly - 0.3, 0.15, P.MUTED, 0.3, align="l", kind="bold")
        st.fade_in([card, head], t_dn, 0.4)
        rows = [(SEAWATER, "seawater, pumped down", t_dn + 0.1), (P.MUD, "gel sweep: a thick slug", t_gel),
                (CUTTINGS, "cuttings: chips of rock", t_cut)]
        for i, (cc, txt, tt) in enumerate(rows):
            yy = ly - 0.75 - i * 0.45
            dot = st.circle(lx0 + 0.42, yy, 0.09, cc, 0.3, role="orb" if cc != CUTTINGS else "disc")
            tx = st.text(txt, lx0 + 0.72, yy, 0.18, P.TEXT, 0.3, align="l")
            st.fade_in([dot, tx], tt, 0.4)

        # usually nothing returns to the rig
        t_no = _w(b, 5, "nothing returns")
        up = st.arrow(WX + 0.42, 2.75, WX + 0.42, 3.7, P.MUTED, 0.05, 0.2, 1.0)
        st.fade_in(up, t_no - 0.2, 0.3)
        _x_mark(st, WX + 0.42, 3.2, 0.2, t_no + 0.1, width=0.06)
        _callout(st, -5.95, 2.85, "usually nothing returns to the rig", t_no, fg=P.WARN, align="l")


# ====================================================================================================== 2.02
def _gas_panel(st, x0, x1, title, tcol, t_in, SBY=0.8, TOPY=3.45, BOTY=-3.4, z=0.0):
    """One side of the comparison: rig at the surface, 300 m of water, a conductor and an open hole into a shallow
    gas sand. Returns a dict of geometry and the objects."""
    cx = (x0 + x1) / 2
    wx = cx + 0.55
    objs = _seascape(st, x0, x1, TOPY, SBY, BOTY, clay=0.6, z=z)
    sand = st.rect(cx, -2.35, x1 - x0, 0.55, P.SAND, z + 0.01)
    shoe = SBY - 0.95
    hole = st.rect(wx, (shoe + (-2.85)) / 2, 0.46, shoe + 2.85, P.BG, z + 0.05)
    cond = [st.rect(wx - 0.28, (SBY + 0.12 + shoe) / 2, 0.07, SBY + 0.12 - shoe, C_COND, z + 0.1),
            st.rect(wx + 0.28, (SBY + 0.12 + shoe) / 2, 0.07, SBY + 0.12 - shoe, C_COND, z + 0.1)]
    bore = st.rect(wx, (SBY + shoe) / 2, 0.49, SBY - shoe, P.BG, z + 0.05)
    hous = st.rect(wx, SBY + 0.12, 0.85, 0.24, C_COND, z + 0.12)
    pipe = st.rect(wx, (TOPY - 0.1 + (-2.6)) / 2, 0.08, TOPY - 0.1 + 2.6, P.STEEL, z + 0.2)
    bit = st.rect(wx, -2.66, 0.36, 0.14, P.STEEL_DK, z + 0.21)
    rig = _rig(st, wx, TOPY, z + 0.3, 1.5)
    gl = st.text("shallow gas", x0 + 0.2, -2.35, 0.17, P.GAS, z + 0.4, align="l", kind="bold")
    hd = pill(st, x0 + 0.18, TOPY - 0.42, title, P.PANEL2, tcol, 0.22, z + 0.5, align="l")
    objs += [sand, hole, bore] + cond + [hous, pipe, bit] + rig + [gl] + hd
    st.fade_in(objs, t_in, 0.5)
    pockets = []
    rnd = random.Random(int(x0 * 10) + 7)
    for i in range(16):
        px = x0 + 0.3 + (x1 - x0 - 0.6) * (i + rnd.random() * 0.6) / 16
        if abs(px - wx) < 0.35 or px < x0 + 1.55:
            continue
        pockets.append(st.circle(px, -2.35 + rnd.uniform(-0.17, 0.17), rnd.uniform(0.035, 0.06), P.GAS, z + 0.3))
    st.fade_in(pockets, t_in + 0.3, 0.5)
    return dict(cx=cx, wx=wx, sb=SBY, shoe=shoe, top=TOPY, objs=objs + pockets)


def beat_why(st, tl):
    b = tl["2.02"]
    s = b.sent
    with st.span(b.start, b.end):
        # ---- A: the question (700 m with nothing that can close the well), held through the 2 s pause
        kick = st.text("PAUSE AND THINK", -5.95, 3.4, 0.2, P.MUTED, 1.0, align="l", kind="bold")
        st.fade_in(kick, s[0], 0.4)
        k = 6.0 / SURF_SHOE
        cx0, ytop = -4.55, 2.75
        Y = lambda z: ytop - z * k
        col_ = [st.rect(cx0, (Y(0) + Y(WD)) / 2, 1.5, Y(0) - Y(WD), P.SEA, 0.1),
                st.rect(cx0, (Y(WD) + Y(SURF_SHOE)) / 2, 1.5, Y(WD) - Y(SURF_SHOE), P.ROCK, 0.1),
                st.rect(cx0, Y(WD), 1.5, 0.04, SEABED_LINE, 0.12)]
        t_700 = _w(b, 1, "seven hundred")
        t_700e = _w(b, 1, "below the seabed", 1.0)
        hole = st.rect(cx0, Y(WD), 0.26, 0.0001, P.BG, 0.15, anchor="t")
        st.fade_in(col_ + [hole], s[1] - 0.3, 0.5)
        st.scale_to(hole, t_700, t_700e, sy=Y(WD) - Y(SURF_SHOE))
        tk = []
        for z, txt in ((0, "sea level"), (WD, f"seabed {WD:.0f} m"), (SURF_SHOE, f"{SURF_SHOE:,.0f} m")):
            tk.append(st.rect(cx0 + 0.95, Y(z), 0.18, 0.025, P.MUTED, 0.2))
            tk.append(st.text(txt, cx0 + 1.12, Y(z), 0.16, P.MUTED, 0.2, align="l"))
        st.fade_in(tk[:4], s[1] - 0.1, 0.4)
        st.fade_in(tk[4:], t_700e - 0.3, 0.4)
        brk = st.line([(cx0 - 0.95, Y(WD)), (cx0 - 1.1, Y(WD)), (cx0 - 1.1, Y(SURF_SHOE)), (cx0 - 0.95, Y(SURF_SHOE))], P.TEXT, 0.03, 0.3)
        st.draw_on(brk, t_700, t_700e, "BEZIER")
        hx = -2.0
        st.counter(hx, 2.25, t_700, t_700e, 0, BELOW_SB, fmt="{:,.0f} m", size=0.85, color=P.TEXT, align="l", kind="bold",
                   hold=s[3] - 0.3)
        l2 = st.text("below the seabed", hx, 1.35, 0.36, P.TEXT, 1.0, align="l", kind="bold")
        st.fade_in(l2, t_700e - 0.4, 0.4)
        t_noth = _w(b, 1, "nothing that can close")
        l3 = st.text("with nothing that can close the well", hx, 0.65, 0.3, P.BAD, 1.0, align="l", kind="bold")
        st.fade_in(l3, t_noth, 0.4)
        nob = _dashed_rect(st, cx0 - 0.42, Y(WD) + 0.02, cx0 + 0.42, Y(WD) + 0.5, P.MUTED, 0.3)
        st.fade_in(nob, t_noth, 0.3)
        nox = _x_mark(st, cx0, Y(WD) + 0.26, 0.24, t_noth + 0.3, z=0.4, width=0.06)
        q = st.text("Why is that allowed?", hx, -1.0, 0.5, P.WARN, 1.0, align="l", kind="bold")
        st.fade_in(q, s[2], 0.45)
        bar = st.line([(hx, -1.75), (hx + 6.6, -1.75)], P.WARN, 0.04, 1.0, alpha=0.7)
        st.draw_on(bar, b.sent_end[2], s[3] - 0.1)
        A = col_ + [hole, brk, kick, l2, l3, q, bar] + tk + nob + nox
        st.fade_out(A, s[3] - 0.35, 0.4)

        # ---- B: shallow rock is weak: thin cover, grains barely squeezed, splits at low pressure
        t_b = s[3]
        x0, x1, y0, y1 = -6.1, -0.7, -3.3, 2.35
        card = st.rect((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, P.PANEL, 0.1)
        sea = st.rect((x0 + x1) / 2, 2.15, x1 - x0 - 0.3, 0.3, P.SEA, 0.12)
        cover = st.rect((x0 + x1) / 2, 1.78, x1 - x0 - 0.3, 0.44, P.SEABED, 0.12)
        st.fade_in([card, sea, cover], t_b, 0.5)
        t_thin = _w(b, 3, "thin layer")
        wts = []
        for xx in (-4.9, -3.4, -1.9):
            wts += st.arrow(xx, 2.05, xx, 1.6, P.TEXT, 0.05, 0.16, 0.4)
        st.fade_in(wts, t_thin, 0.4)
        thin = _callout(st, (x0 + x1) / 2, 2.85, "only a thin layer of sediment above", t_thin, align="c")
        rnd = random.Random(9)
        t_sq = _w(b, 3, "barely squeezed")
        t_split = _w(b, 3, "splits")
        crack_x = lambda y: -3.35 + 0.25 * math.sin(2.3 * y)
        grains = []
        for j in range(8):
            for i in range(9):
                gx = x0 + 0.5 + i * 0.57 + (0.28 if j % 2 else 0) + rnd.uniform(-0.05, 0.05)
                gy = 1.2 - j * 0.48 + rnd.uniform(-0.04, 0.04)
                if gx > x1 - 0.35 or gy < -2.15:
                    continue
                g = st.circle(gx, gy, 0.2 + rnd.uniform(-0.02, 0.02), P.SAND, 0.2)
                grains.append(g)
                st.move(g, t_split, t_split + 0.8, dx=0.09 if gx > crack_x(gy) else -0.09)
        st.fade_in(grains, t_b + 0.3, 0.6)
        cap1 = st.text("grains barely squeezed", (x0 + x1) / 2, -2.55, 0.22, P.TEXT, 0.4, kind="bold")
        st.fade_in(cap1, t_sq, 0.4)
        crack = st.line([(crack_x(y), y) for y in np.linspace(-2.1, 1.45, 24)], P.FRAC, 0.06, 0.45)
        st.draw_on(crack, t_split, t_split + 0.8, "BEZIER")
        cap2 = st.text("→ the rock splits at low pressure", (x0 + x1) / 2, -3.0, 0.22, P.FRAC, 0.4, kind="bold")
        st.fade_in(cap2, t_split + 0.2, 0.4)
        # inset: the shallow fracture limit from the window chart
        c = Chart(st, 1.4, -2.55, 5.1, 5.1, (1.0, 1.6), (0.0, SURF_SHOE), invert_y=True, z=0.2)
        fr = c.frame(xticks=[1.0, 1.2, 1.4, 1.6], yticks=[0, 500, 1000], xlabel="equivalent mud weight (sg)",
                     ylabel="depth (m)", fx="{:.1f}", tick_size=0.17)
        sea_c = st.rect(c.x + c.w / 2, (c.Y(0) + c.Y(WD)) / 2, c.w, c.Y(0) - c.Y(WD), P.SEA, 0.18, alpha=0.5)
        sbl = st.text("seabed", c.x + c.w - 0.08, c.Y(WD) + 0.17, 0.15, P.MUTED, 0.3, align="r")
        zs = list(range(int(WD), int(SURF_SHOE) + 1, 25))
        band = c.band([(M.pp(z), z) for z in zs], [(M.fg(z), z) for z in zs], P.SAFE, 0.21, 0.25)
        ppc = c.curve([M.pp(z) for z in zs], zs, P.PORE, 0.06, 0.3)
        fgc = c.curve([M.fg(z) for z in zs], zs, P.FRAC, 0.06, 0.3)
        t_c = _w(b, 3, "so the grains")
        st.fade_in(fr + [sea_c, sbl, band], t_c, 0.5)
        st.draw_on([ppc, fgc], t_c + 0.4, t_c + 1.8, "BEZIER")
        ppl = c.label(M.pp(900) + 0.02, 900, "pore pressure", 0.17, P.PORE, "l", "bold")
        fgl = c.label(M.fg(800) + 0.02, 800, "fracture", 0.17, P.FRAC, "l", "bold")
        st.fade_in([ppl, fgl], t_c + 1.4, 0.4)
        t_low = _w(b, 3, "low pressure")
        ring = st.ring(c.X(M.fg(WD)), c.Y(WD), 0.17, 0.035, P.FRAC, 0.5)
        st.pop_in(ring, t_low - 0.4, 0.4)
        st.ripple(c.X(M.fg(WD)), c.Y(WD), t_low - 0.4, t_low + 2.5, P.FRAC, period=1.0, r0=0.15, r1=0.55, z=0.55)
        lowl = st.text(f"splits at only {M.fg(WD):.2f} sg", c.X(M.fg(WD)) + 0.3, c.Y(WD) - 0.42, 0.19, P.FRAC, 0.5, align="l", kind="bold")
        st.fade_in(lowl, t_low - 0.2, 0.4)
        B = [card, sea, cover, cap1, crack, cap2, sea_c, sbl, band, ppc, fgc, ppl, fgl, ring, lowl] + wts + thin + grains + fr
        st.fade_out(B, s[4] - 0.35, 0.4)

        # ---- C: shut in -> fracture at the shoe -> broach;  left open -> it bubbles out at the seabed
        L = _gas_panel(st, -6.1, -0.35, "IF WE SHUT IT IN", P.BAD, s[4] - 0.1)
        wx, sb, shoe = L["wx"], L["sb"], L["shoe"]
        t_shut = _w(b, 4, "Shut in")
        valve = [st.rect(wx, sb + 0.42, 0.95, 0.32, P.STEEL_DK, 0.6),
                 st.poly([(wx - 0.3, sb + 0.3), (wx, sb + 0.42), (wx - 0.3, sb + 0.54)], P.TEXT, 0.62),
                 st.poly([(wx + 0.3, sb + 0.3), (wx, sb + 0.42), (wx + 0.3, sb + 0.54)], P.TEXT, 0.62)]
        st.pop_in(valve, t_shut, 0.4)
        shut_c = _callout(st, wx + 0.62, sb + 0.42, "shut", t_shut + 0.2, fg=P.BAD, size=0.18)
        tC1 = s[6] - 0.1                                  # section C ends (its particles stop with it)
        t_gas = _w(b, 4, "gas flow")
        for sd in (-1, 1):
            _stream(st, [(wx + sd * 1.1, -2.35), (wx + sd * 0.16, -2.3), (wx + sd * 0.12, sb + 0.1)], t_gas, tC1, P.GAS,
                    rate=4.0, speed=1.3, r=0.045, z=0.5, seed=20 + sd, tail_fade=0.4)
        cap = st.rect(wx, sb + 0.2, 0.42, 0.0001, P.GAS, 0.48, anchor="t", alpha=0.55)
        t_crack = _w(b, 4, "crack the rock")
        st.fade_in(cap, t_gas + 1.5, 0.3)
        st.scale_to(cap, t_gas + 1.5, t_crack, sy=1.6)
        # well-pressure dial with the fracture limit marked
        gx, gy, gr = L["cx"] - 1.55, 1.95, 0.55
        t_p = _w(b, 4, "trapped pressure")
        dial = [st.circle(gx, gy, gr, P.PANEL2, 0.5, role="solid"), st.ring(gx, gy, gr, 0.04, P.MUTED, 0.51)]
        for kk in range(7):
            th = math.radians(210 - 240 * kk / 6)
            dial.append(st.rect(gx + (gr - 0.1) * math.cos(th), gy + (gr - 0.1) * math.sin(th), 0.1, 0.025, P.MUTED, 0.52,
                                rot=math.degrees(th)))
        th_f = 25.0
        dial.append(st.rect(gx + (gr - 0.1) * math.cos(math.radians(th_f)), gy + (gr - 0.1) * math.sin(math.radians(th_f)),
                            0.22, 0.07, P.FRAC, 0.53, rot=th_f))
        needle = st.rect(gx, gy, gr - 0.12, 0.045, P.TEXT, 0.55, anchor="l", rot=205)
        hub = st.circle(gx, gy, 0.06, P.TEXT, 0.56)
        dl = st.text("well pressure", gx, gy - gr - 0.22, 0.16, P.TEXT, 0.5, kind="bold")
        fl = st.text("fracture limit at the shoe", gx + 0.05, gy + gr + 0.2, 0.15, P.FRAC, 0.5, kind="bold")
        st.fade_in(dial + [needle, hub, dl], t_shut - 0.2, 0.4)
        st.fade_in(fl, t_p, 0.4)
        st.rotate(needle, t_p, t_crack, th_f + 2, interp="BEZIER")
        st.rotate(needle, t_crack, t_crack + 0.6, 0.0)
        # fracture from just below the conductor shoe, up outside the conductor, to the seabed (broach)
        fpts = [(wx - 0.23, shoe - 0.2), (wx - 0.45, shoe - 0.05), (wx - 0.55, shoe + 0.25), (wx - 0.5, shoe + 0.55),
                (wx - 0.62, shoe + 0.8), (wx - 0.6, sb)]
        frl = st.line(fpts, P.FRAC, 0.06, 0.45)
        st.draw_on(frl, t_crack, t_crack + 0.9, "BEZIER")
        t_out = _w(b, 4, "outside the well")
        _stream(st, [(wx - 0.18, shoe - 0.2)] + fpts[1:], t_out - 0.6, tC1, P.GAS, rate=4.5, speed=1.1, r=0.045, z=0.5, seed=31)
        crater = st.ellipse(wx - 0.6, sb + 0.01, 0.22, 0.07, P.BG, 0.3, role="hole")
        st.fade_in(crater, t_out, 0.3)
        _bubbles(st, wx - 0.6, sb + 0.05, t_out, tC1, P.GAS, rate=7.0, rise=0.75, life=3.4, spread=0.15, seed=33,
                 y_max=L["top"] - 0.15, r=0.04)
        t_stop = _w(b, 4, "nothing can stop it")
        st.ripple(wx - 0.6, sb + 0.05, t_stop - 0.2, t_stop + 2.5, P.BAD, period=0.9, r0=0.15, r1=0.8, z=0.7)
        brl = _callout(st, L["cx"], -3.0, "broach: gas escapes outside the well", t_stop, fg="#ffffff", bg=P.BAD, align="c")

        R = _gas_panel(st, 0.25, 6.0, "LEFT OPEN", P.SAFE, s[5] - 0.3)
        rwx, rsb = R["wx"], R["sb"]
        t_bub = _w(b, 5, "bubble out")
        _stream(st, [(rwx + 1.2, -2.35), (rwx + 0.16, -2.3), (rwx + 0.12, rsb - 0.02)], t_bub - 2.2, tC1, P.GAS, rate=4.0,
                speed=1.5, r=0.045, z=0.5, seed=41)
        _stream(st, [(rwx - 1.2, -2.35), (rwx - 0.16, -2.3), (rwx - 0.12, rsb - 0.02)], t_bub - 2.0, tC1, P.GAS, rate=4.0,
                speed=1.5, r=0.045, z=0.5, seed=42)
        _bubbles(st, rwx, rsb + 0.28, t_bub, tC1, P.GAS, rate=8.0, rise=0.7, life=3.2, spread=0.2, seed=43, y_max=2.3,
                 drift=0.08, r=0.04)
        t_far = _w(b, 5, "far below the rig")
        dimx = R["cx"] - 1.95
        dim = [st.line([(dimx, R["top"] - 0.25), (dimx, rsb + 0.05)], P.TEXT, 0.025, 0.8, alpha=0.8),
               st.rect(dimx, R["top"] - 0.25, 0.22, 0.025, P.TEXT, 0.8), st.rect(dimx, rsb + 0.05, 0.22, 0.025, P.TEXT, 0.8)]
        st.draw_on(dim[0], t_far - 0.2, t_far + 0.4, "BEZIER")
        st.fade_in(dim[1:], t_far - 0.2, 0.3)
        dlab = pill(st, dimx + 0.2, (R["top"] + rsb) / 2 - 0.15, f"{WD:.0f} m", P.PANEL2, P.TEXT, 0.2, 2.0, align="l")
        st.fade_in(dlab, t_far, 0.4)
        okl = _callout(st, R["cx"], -3.0, "it vents at the seabed, far below the rig", t_bub + 0.3, fg=P.SAFE, align="c")
        C = L["objs"] + R["objs"] + valve + [cap, needle, hub, dl, fl, frl, crater] + dial + brl + dim + dlab + okl + shut_c
        st.fade_out(C, s[6] - 0.3, 0.4)

        # ---- D: the defences come first (four tiles, each on its words)
        hd = st.text("THE DEFENCES COME FIRST", -5.95, 3.35, 0.3, P.TEXT, 1.0, align="l", kind="bold")
        st.fade_in(hd, s[6], 0.45)
        tiles = [(-2.75, 1.0, "SURVEY FOR GAS", "a seismic site survey maps shallow gas before the spud", _w(b, 6, "survey for gas")),
                 (4.25, 1.0, "PILOT HOLE", "where in doubt, a narrow hole first: a smaller flow, easier to kill", _w(b, 6, "pilot hole")),
                 (-2.75, -1.95, "ROV WATCHING", "a camera on the seabed: the only eyes on the hole", _w(b, 6, "remotely operated")),
                 (4.25, -1.95, "HEAVY MUD READY", "pumped hard down the pipe to kill a flow", _w(b, 6, "heavy mud"))]
        for i, (tx, ty, ttl, sub, tt) in enumerate(tiles):
            w, h = 6.7, 2.55
            plate = st.rect(tx, ty, w, h, P.PANEL2, 0.3)
            num = st.text(f"0{i + 1}", tx - 0.8, ty + 0.95, 0.15, P.MUTED, 0.4, align="l", kind="mono")
            ttl_o = st.text(ttl, tx - 0.8, ty + 0.5, 0.25, P.TEXT, 0.4, align="l", kind="bold")
            sub_o = st.text(wrap_to(sub, 0.17, 3.7), tx - 0.8, ty + 0.05, 0.17, P.MUTED, 0.4, align="l", valign="t")
            st.fade_in([plate, num], tt - 0.25, 0.4)
            st.fade_in([ttl_o, sub_o], tt, 0.4)
            _check(st, tx + w / 2 - 0.4, ty + h / 2 - 0.4, tt + 0.6)
            _defence_icon(st, i, tx - 2.05, ty, tt - 0.1, b.end)


def _defence_icon(st, i, x, y, t, t_end):
    if i == 0:      # seismic section with a bright spot (gas)
        traces = []
        for j in range(9):
            xx = x - 1.0 + j * 0.25
            pts = [(xx + 0.07 * math.sin(7.0 * yy + j * 1.3) * (2.2 if abs(yy - y + 0.2) < 0.15 and 2 <= j <= 6 else 1.0), yy)
                   for yy in np.linspace(y + 0.95, y - 0.95, 40)]
            traces.append(st.line(pts, P.MUTED, 0.022, 0.45))
        st.fade_in(traces, t, 0.2)
        st.draw_on(traces, t, t + 0.8)
        spot = st.ellipse(x, y - 0.2, 0.55, 0.12, P.GAS, 0.5, alpha=0.85)
        st.fade_in(spot, t + 0.7, 0.4)
        lbl = st.text("gas?", x + 0.62, y - 0.2, 0.15, P.GAS, 0.5, align="l", kind="bold")
        st.fade_in(lbl, t + 0.9, 0.3)
    elif i == 1:    # narrow pilot hole beside the full-size hole outline
        blk = [st.rect(x, y - 0.15, 2.0, 1.6, P.ROCK, 0.4), st.rect(x, y + 0.65, 2.0, 0.04, SEABED_LINE, 0.41),
               st.rect(x, y + 0.82, 2.0, 0.3, P.SEA, 0.4)]
        st.fade_in(blk, t, 0.3)
        ph = st.rect(x - 0.35, y + 0.65, 0.14, 0.0001, P.BG, 0.45, anchor="t")
        st.fade_in(ph, t + 0.1, 0.1)
        st.scale_to(ph, t + 0.2, t + 1.2, sy=1.4)
        full = _dashed_rect(st, x + 0.12, y - 0.75, x + 0.72, y + 0.65, P.MUTED, 0.46)
        st.fade_in(full, t + 0.9, 0.4)
        l1 = st.text("pilot", x - 0.35, y - 0.95, 0.14, P.TEXT, 0.5, kind="bold")
        l2 = st.text("full size", x + 0.42, y - 0.95, 0.14, P.MUTED, 0.5)
        st.fade_in([l1, l2], t + 1.0, 0.3)
    elif i == 2:    # ROV with its camera on the wellhead, watching for bubbles
        bg = [st.rect(x, y, 2.1, 2.0, P.SEA, 0.4), st.rect(x, y - 0.75, 2.1, 0.5, P.SEABED, 0.41)]
        wh = st.rect(x - 0.45, y - 0.42, 0.42, 0.18, C_COND, 0.43)
        st.fade_in(bg + [wh], t, 0.3)
        rov = [st.rect(x + 0.55, y + 0.25, 0.7, 0.36, ROV_BODY, 0.46), st.rect(x + 0.55, y + 0.47, 0.6, 0.08, P.STEEL_DK, 0.47),
               st.circle(x + 0.22, y + 0.18, 0.07, P.TEXT, 0.48)]
        teth = st.line([(x + 0.6, y + 0.51), (x + 0.75, y + 0.99)], P.MUTED, 0.02, 0.45)
        cone = st.poly([(x + 0.2, y + 0.18), (x - 0.75, y - 0.4), (x - 0.15, y - 0.55)], "#ffffff", 0.44, 0.16)
        st.fade_in(rov + [teth, cone], t + 0.2, 0.4)
        st.move(rov + [teth], t + 0.2, t + 1.2, dx=0.0, dy=0.0)
        _bubbles(st, x - 0.45, y - 0.3, t + 0.8, t_end, P.GAS, rate=3.0, rise=0.35, life=2.6, spread=0.06, r=0.03, seed=51,
                 y_max=y + 0.95, z=0.47)
    else:           # heavy (kill) mud ready to pump down the pipe
        tank = [st.rect(x - 0.35, y + 0.2, 1.1, 1.2, P.STEEL_DK, 0.42), st.rect(x - 0.35, y + 0.08, 0.94, 0.0001, P.KILL_MUD, 0.43, anchor="b")]
        tank[1].location[1] = y - 0.36
        st.fade_in(tank, t, 0.3)
        st.scale_to(tank[1], t + 0.1, t + 0.9, sy=0.95)
        pipe = st.rect(x + 0.6, y - 0.25, 0.1, 1.3, P.STEEL, 0.42)
        st.fade_in(pipe, t + 0.2, 0.3)
        _stream(st, [(x + 0.2, y + 0.45), (x + 0.6, y + 0.45), (x + 0.6, y - 0.9)], t + 0.9, t_end, P.KILL_MUD, rate=5.0,
                speed=1.2, r=0.04, z=0.5, seed=61)
        lbl = st.text("kill mud", x - 0.35, y - 0.6, 0.15, P.KILL_MUD, 0.5, kind="bold")
        st.fade_in(lbl, t + 0.5, 0.3)


# ====================================================================================================== 2.03
def beat_conductor(st, tl):
    b = tl["2.03"]
    s = b.sent
    with st.span(b.start, b.end):
        # ---- A: spud, guide base, conductor run in (x < 3.1: the term cards stack down the right side here)
        TOP, SB, BOT = 3.85, 1.0, -3.6
        WX, HW = -1.5, 1.44                 # 36 in hole
        HB = -2.65
        tA1 = s[3] - 0.2
        scene = _seascape(st, -6.2, 3.1, TOP, SB, BOT, clay=1.6)
        st.fade_out(scene, tA1, 0.5)
        t_spud = _w(b, 0, "spud")
        t_g = _w(b, 1, "guide base")
        t_out = s[2] + 0.1
        ybit = _piecewise([(b.start, SB + 1.6, "BEZIER"), (t_spud, SB, "LINEAR"), (_w(b, 0, "first metres", 1.0), SB - 0.55, "LINEAR"),
                           (t_g + 0.9, SB - 0.55, "LINEAR"), (t_out - 0.4, HB, "BEZIER"), (t_out + 1.2, SB + 2.6, "LINEAR")])
        BIT_H, COL_H = 0.3, 0.9
        hole = st.rect(WX, SB, HW, 0.0001, P.SEA, 0.1, anchor="t")
        pipe = st.rect(WX, TOP, 0.13, 1.0, P.STEEL, 0.3, anchor="t")
        collar = st.rect(WX, 0, 0.32, COL_H, P.STEEL_DK, 0.31)
        bit = st.rect(WX, 0, HW * 0.92, BIT_H, P.STEEL_DK, 0.32)
        deepest = {"y": SB}

        def hole_fn(t):
            return {"scale": (HW, max(SB - min(ybit(tt) for tt in np.linspace(b.start, t, 12)), 0.0001))}
        _drive(st, hole, b.start, t_out, hole_fn, fps=12)
        _drive(st, pipe, b.start, t_out + 1.2, lambda t: {"scale": (0.13, max(TOP - (ybit(t) + BIT_H + COL_H), 0.0001))})
        _drive(st, collar, b.start, t_out + 1.2, lambda t: {"loc": (WX, ybit(t) + BIT_H + COL_H / 2)})
        _drive(st, bit, b.start, t_out + 1.2, lambda t: {"loc": (WX, ybit(t) + BIT_H / 2)})
        st.fade_out([pipe, collar, bit], t_out + 0.6, 0.5)
        st.fade_out(hole, tA1, 0.5)
        _spill(st, WX, SB, t_spud - 0.1, t_spud + 1.6, HW / 2, chip=SILT, cloud=SILT, rate=14, life=1.4, reach=1.0, height=0.4,
               cloud_alpha=0.3, seed=71)
        _callout(st, WX + 1.05, SB + 0.6, "spud: the first metres", t_spud + 0.2, target=(WX + 0.75, SB - 0.25), t_out=tA1)
        # guide base slides down the pipe and lands on the seabed
        gb = [st.rect(WX - 1.15, SB + 0.07, 0.9, 0.14, P.STEEL_DK, 0.4), st.rect(WX + 1.15, SB + 0.07, 0.9, 0.14, P.STEEL_DK, 0.4),
              st.poly([(WX - 0.7, SB + 0.14), (WX - 0.95, SB + 0.4), (WX - 0.85, SB + 0.4), (WX - 0.62, SB + 0.14)], P.STEEL_DK, 0.41),
              st.poly([(WX + 0.7, SB + 0.14), (WX + 0.95, SB + 0.4), (WX + 0.85, SB + 0.4), (WX + 0.62, SB + 0.14)], P.STEEL_DK, 0.41),
              st.rect(WX - 1.45, SB + 0.6, 0.06, 0.95, P.STEEL, 0.4), st.rect(WX + 1.45, SB + 0.6, 0.06, 0.95, P.STEEL, 0.4),
              st.poly([(WX - 1.52, SB + 1.07), (WX - 1.38, SB + 1.07), (WX - 1.45, SB + 1.3)], P.STEEL, 0.41),
              st.poly([(WX + 1.52, SB + 1.07), (WX + 1.38, SB + 1.07), (WX + 1.45, SB + 1.3)], P.STEEL, 0.41)]
        for o in gb:
            st.move(o, b.start, t_g, dy=1.6)
        st.fade_in(gb, t_g - 0.1, 0.3)
        st.move(gb, t_g, t_g + 1.4, dy=-1.6)
        _spill(st, WX, SB, t_g + 1.3, t_g + 2.6, 1.6, chip=SILT, cloud=SILT, rate=10, life=1.2, reach=0.6, height=0.25,
               cloud_alpha=0.25, seed=73)
        _callout(st, WX - 1.75, SB + 1.45, "guide base (often)", t_g + 0.6, target=(WX - 1.45, SB + 0.9), align="r", t_out=tA1)
        t_al = _w(b, 1, "aligned")
        axis = st.dashed((WX, SB + 1.9), (WX, HB - 0.05), P.TEXT, 0.03, 0.14, 0.1, 0.6, alpha=0.7)
        st.fade_in(axis, t_al - 0.4, 0.3)
        st.fade_out(axis, t_al + 2.0, 0.5)
        # the conductor (30 in) with its low-pressure housing is lowered through the guide base into the 36 in hole
        t_c0 = t_out + 0.7
        t_c1 = _w(b, 2, "thirty inch") + 1.0
        CW = 1.2
        c_top = SB + 0.42
        c_shoe = HB + 0.15
        drop = TOP - 0.1 - c_top - 0.05
        cond = [st.rect(WX - CW / 2 + 0.05, (c_top + c_shoe) / 2, 0.1, c_top - c_shoe, C_COND, 0.5),
                st.rect(WX + CW / 2 - 0.05, (c_top + c_shoe) / 2, 0.1, c_top - c_shoe, C_COND, 0.5),
                st.rect(WX, c_top - 0.12, CW + 0.36, 0.24, C_COND, 0.52)]
        for o in cond:
            st.move(o, b.start, t_c0, dy=drop)
        st.fade_in(cond, t_c0 - 0.2, 0.3)
        st.move(cond, t_c0, t_c1, dy=-drop)
        st.fade_out(cond + gb, tA1, 0.5)
        _callout(st, WX - 1.9, SB - 1.2, "30 in conductor", _w(b, 2, "thirty inch"), target=(WX - CW / 2, SB - 1.2), align="r", t_out=tA1)
        _callout(st, WX - 1.9, SB - 1.85, "the well's foundation", _w(b, 2, "foundation"), fg=P.WARN, align="r", t_out=tA1)

        # ---- B: two ways in: (a) jetted, (b) drilled + cemented (our well)
        tB0, tB1 = s[3], s[4] - 0.15
        SBp, BOTp, TOPp = 1.5, -3.4, 3.2
        pa = _seascape(st, -6.1, -1.85, TOPp, SBp, BOTp, clay=SBp - BOTp - 0.01, z=0.0)
        pb = _seascape(st, -1.55, 2.95, TOPp, SBp, BOTp, clay=1.6, z=0.0)
        ta = st.text("(a) JETTED", -3.975, 3.55, 0.24, P.TEXT, 0.6, kind="bold")
        tb = st.text("(b) DRILLED + CEMENTED", 0.7, 3.55, 0.24, P.TEXT, 0.6, kind="bold")
        st.fade_in(pa + pb + [ta, tb], tB0, 0.5)
        # (a) jetting: the conductor sinks under its own weight while jets at its tip wash the clay away
        ax = -3.975
        a_top_f, a_shoe_f = SBp + 0.4, -2.75
        shift = 1.35
        t_j0, t_j1 = _w(b, 3, "jetted"), _w(b, 3, "soft clay", 1.0)
        shoe_a = _piecewise([(t_j0, a_shoe_f + shift, "BEZIER"), (t_j1, a_shoe_f, "LINEAR")])
        CWa = 0.95
        ca = [st.rect(ax - CWa / 2 + 0.045, 0, 0.09, a_top_f - a_shoe_f, C_COND, 0.5),
              st.rect(ax + CWa / 2 - 0.045, 0, 0.09, a_top_f - a_shoe_f, C_COND, 0.5),
              st.rect(ax, 0, CWa + 0.3, 0.22, C_COND, 0.52)]
        js = st.rect(ax, TOPp, 0.09, 1.0, P.STEEL, 0.45, anchor="t")
        jb = st.rect(ax, 0, 0.42, 0.14, P.STEEL_DK, 0.46)
        bore_a = st.rect(ax, 0, CWa - 0.18, 1.0, P.SEA, 0.44)
        L_a = a_top_f - a_shoe_f
        _drive(st, ca[0], tB0, tB1, lambda t: {"loc": (ax - CWa / 2 + 0.045, shoe_a(t) + L_a / 2)})
        _drive(st, ca[1], tB0, tB1, lambda t: {"loc": (ax + CWa / 2 - 0.045, shoe_a(t) + L_a / 2)})
        _drive(st, ca[2], tB0, tB1, lambda t: {"loc": (ax, shoe_a(t) + L_a - 0.11)})
        _drive(st, bore_a, tB0, tB1, lambda t: {"loc": (ax, shoe_a(t) + (L_a - 0.1) / 2), "scale": (CWa - 0.18, L_a - 0.1)})
        _drive(st, js, tB0, tB1, lambda t: {"scale": (0.09, TOPp - shoe_a(t) - 0.12)})
        _drive(st, jb, tB0, tB1, lambda t: {"loc": (ax, shoe_a(t) + 0.12)})
        st.fade_in(ca + [js, jb, bore_a], tB0, 0.5)

        def jets(c, t, look):
            a = _ramp(t, t_j0 + 0.8, t_j0 + 1.2) * min(1.0, (tB1 - t) / 0.3)
            if a <= 0:
                return
            y = shoe_a(t)
            pos_w, pos_s = [], []
            for k in range(14):
                ph = (t * 2.2 + k / 14) % 1.0
                sd = -1 if k % 2 else 1
                ang = math.radians(-60 - 25 * ((k * 7) % 5) / 4)
                pos_w.append((ax + sd * 0.12 + sd * math.cos(ang) * -0.45 * ph * -1, y - 0.02 + math.sin(ang) * 0.5 * ph))
            for k in range(12):
                ph = (t * 0.55 + k / 12) % 1.0
                sd = -1 if k % 2 else 1
                yy = y + 0.1 + (L_a - 0.05) * ph
                pos_s.append((ax + sd * (0.28 + 0.04 * math.sin(9 * ph + k)), yy))
            look.draw_particles(c, pos_w, SEAWATER, 0.04, 0.9 * a, True)
            look.draw_particles(c, pos_s, SILT, 0.05, 0.9 * a, False)
        st.procedural(tB0, tB1, 0.6, jets)
        top_a = lambda t: shoe_a(t) + L_a
        _spill(st, ax, a_top_f + 0.05, t_j0 + 2.0, tB1, CWa / 2 + 0.05, chip=SILT, cloud=SILT, rate=8, life=1.6, reach=0.7,
               height=0.5, cloud_alpha=0.28, seed=75)
        wt = st.arrow(ax + 1.15, a_top_f + 1.05 + shift, ax + 1.15, a_top_f + 0.25 + shift, P.TEXT, 0.07, 0.24, 0.7)
        st.move(wt, tB0, t_j0, dy=0.0)
        st.move(wt, t_j0, t_j1, dy=-shift)
        wl = st.text("own weight", ax + 1.15, a_top_f + 1.3 + shift, 0.17, P.TEXT, 0.7, kind="bold")
        st.move(wl, t_j0, t_j1, dy=-shift)
        t_wt = _w(b, 3, "its own weight")
        st.fade_in(wt + [wl], t_wt - 0.2, 0.4)
        _callout(st, ax - 0.65, -3.0, "water jets at the tip", _w(b, 3, "water jets"), target=(ax - 0.2, a_shoe_f - 0.1), align="c", t_out=tB1 - 0.05)
        # (b) our well: drill a 36 in hole, run the conductor, cement it to the seabed
        bx = 0.7
        HWb, CWb = 1.2, 0.95
        b_shoe = -2.6
        t_our = _w(b, 3, "as in our well")
        ow = _callout(st, bx, 2.75, "OUR WELL", t_our, fg=P.BG, bg=P.WARN, align="c", size=0.18)
        t_d0, t_d1 = _w(b, 3, "drilled"), _w(b, 3, "inch hole", 1.0)
        hb = st.rect(bx, SBp, HWb, 0.0001, P.SEA, 0.1, anchor="t")
        st.scale_to(hb, t_d0, t_d1, sy=SBp - b_shoe + 0.15, interp="LINEAR")
        bitb = st.rect(bx, SBp + 0.12, HWb * 0.9, 0.22, P.STEEL_DK, 0.32)
        pipeb = st.rect(bx, TOPp, 0.09, TOPp - SBp - 0.23, P.STEEL, 0.31, anchor="t")
        st.fade_in([bitb, pipeb], t_d0 - 0.4, 0.3)
        st.move(bitb, t_d0, t_d1, dy=-(SBp - b_shoe + 0.15), interp="LINEAR")
        st.scale_to(pipeb, t_d0, t_d1, sy=TOPp - b_shoe + 0.15 - 0.23, interp="LINEAR")
        st.fade_out([bitb, pipeb], t_d1 + 0.05, 0.3)
        hl = st.text("36 in hole", bx + HWb / 2 + 0.12, SBp - 0.55, 0.16, P.TEXT, 0.6, align="l", kind="bold")
        st.fade_in(hl, t_d0 + 0.6, 0.3)
        t_r0 = t_d1 + 0.2
        t_cem = _w(b, 3, "and cemented")
        t_r1 = max(t_r0 + 0.6, t_cem - 0.1)
        b_top = SBp + 0.4
        Lb = b_top - b_shoe
        cb = [st.rect(bx - CWb / 2 + 0.045, (b_top + b_shoe) / 2 + 1.0, 0.09, Lb, C_COND, 0.5),
              st.rect(bx + CWb / 2 - 0.045, (b_top + b_shoe) / 2 + 1.0, 0.09, Lb, C_COND, 0.5),
              st.rect(bx, b_top - 0.11 + 1.0, CWb + 0.3, 0.22, C_COND, 0.52)]
        st.fade_in(cb, t_r0 - 0.15, 0.2)
        st.move(cb, t_r0, t_r1, dy=-1.0)
        cem = []
        for sd in (-1, 1):
            g0, g1 = bx + sd * CWb / 2, bx + sd * HWb / 2
            o = st.rect((g0 + g1) / 2, b_shoe, abs(g1 - g0), 0.0001, P.CEMENT, 0.4, anchor="b")
            st.fade_in(o, t_cem, 0.1)
            st.scale_to(o, t_cem, t_cem + 1.6, sy=SBp - b_shoe)
            cem.append(o)
        plug = st.rect(bx, b_shoe + 0.12, CWb - 0.18, 0.24, P.CEMENT, 0.41)
        st.fade_in(plug, t_cem + 0.2, 0.4)
        cml = st.text("cement", bx + HWb / 2 + 0.12, -1.6, 0.16, P.CEMENT, 0.6, align="l", kind="bold")
        st.fade_in(cml, t_cem + 0.5, 0.3)
        t_90 = _w(b, 3, "ninety metres")
        dimx = bx + HWb / 2 + 0.95
        dim = [st.line([(dimx, SBp), (dimx, b_shoe)], P.TEXT, 0.025, 0.7, alpha=0.85), st.rect(dimx, SBp, 0.22, 0.025, P.TEXT, 0.7),
               st.rect(dimx, b_shoe, 0.22, 0.025, P.TEXT, 0.7)]
        st.draw_on(dim[0], t_90 - 0.2, t_90 + 0.4, "BEZIER")
        st.fade_in(dim[1:], t_90 - 0.2, 0.3)
        nl = _callout(st, dimx + 0.25, (SBp + b_shoe) / 2, f"≈ {COND_LEN:.0f} m below seabed\nshoe at {COND_SHOE:.0f} m",
                      t_90, align="l", size=0.19)
        B = pa + pb + [ta, tb, js, jb, bore_a, hb, hl, plug, cml] + ca + wt + [wl] + ow + cb + cem + dim + nl
        st.fade_out(B, tB1, 0.4)
        for o in st.objs[-60:]:
            pass

        # ---- C: think of it as a pile: friction, cemented casing inside, wellhead, BOP, and the rig + riser bending it
        tC = s[4] - 0.1
        cx, Y_SB, Y_SH, Y_RIG = -2.3, -0.2, -3.3, 3.3
        seaC = st.rect(-2.0, (3.85 + Y_SB) / 2, 8.4, 3.85 - Y_SB, P.SEA, 0.0)
        soilC = st.rect(-2.0, (Y_SB - 3.6) / 2, 8.4, Y_SB + 3.6, P.SEABED, 0.0)
        lineC = st.rect(-2.0, Y_SB, 8.4, 0.05, SEABED_LINE, 0.02)
        st.fade_in([seaC, soilC, lineC], tC, 0.5)
        ttl = st.text("A PILE IN THE SOIL", -5.75, 3.4, 0.28, P.TEXT, 1.0, align="l", kind="bold")
        st.fade_in(ttl, _w(b, 4, "pile"), 0.4)
        t_fric = _w(b, 5, "Soil friction")
        t_in = _w(b, 5, "cemented casing")
        t_wh = _w(b, 5, "carries the wellhead")
        t_bop = _w(b, 5, "blowout preventer")
        t_rig = _w(b, 5, "moving rig")
        t_bend = _w(b, 5, "bend it")
        amp = lambda t: 0.5 * _ramp(t, t_rig + 0.3, t_bend + 0.5) * math.sin(2 * math.pi * (t - t_rig) / 3.0) if t > t_rig else 0.0
        colm = Column(st, tC, b.end, cx, Y_SB, Y_SH, Y_RIG, z=0.3, t_inner=t_in, t_wh=t_wh, t_bop=t_bop, t_riser=t_rig - 0.2,
                      amp=amp, weights=True)
        fr_ = []
        for y in (-1.95, -2.45, -2.95):
            for sd in (-1, 1):
                fr_ += st.arrow(cx + sd * 0.45, y - 0.22, cx + sd * 0.45, y + 0.25, P.TEXT, 0.05, 0.16, 0.6)
        st.fade_in(fr_, t_fric, 0.4)
        _callout(st, 0.15, -2.45, "soil friction holds it up", t_fric + 0.2, target=(cx + 0.55, -2.45))
        _callout(st, 0.15, -1.45, "later: the cemented 20 in inside shares the load", t_in, target=(cx + 0.14, -1.45), size=0.18)
        _callout(st, cx - 0.75, Y_SB + 0.35, "wellhead", t_wh + 0.3, target=(cx - 0.42, Y_SB + 0.35), align="r")
        _callout(st, cx - 1.05, colm.y_wh + 0.65, "BOP: hundreds of tonnes", t_bop + 0.9, target=(cx - 0.72, colm.y_wh + 0.65), align="r")
        _springs(st, colm, t_rig + 0.3, b.end, (-0.55, -0.95, -1.35), reach=0.8)
        _moment_arc(st, cx, Y_SB + 0.35, t_bend - 0.4, b.end, r=0.85)
        _callout(st, 0.15, Y_SB + 0.35, "rig + riser bend it at the top", t_bend - 0.2, target=(cx + 0.88, Y_SB + 0.35))
        sp = st.text("soil springs", cx - 1.25, -0.95, 0.16, P.MUTED, 0.6, align="r", kind="bold")
        st.fade_in(sp, t_rig + 0.6, 0.4)
        mv = st.arrow(cx + 1.2, Y_RIG + 0.2, cx + 2.0, Y_RIG + 0.2, P.TEXT, 0.05, 0.18, 0.9) + \
            st.arrow(cx + 1.2, Y_RIG + 0.2, cx + 0.45, Y_RIG + 0.2, P.TEXT, 0.05, 0.18, 0.9)
        st.fade_in(mv, t_rig + 0.2, 0.4)


# ====================================================================================================== 2.04
def beat_surface_casing(st, tl):
    b = tl["2.04"]
    s = b.sent
    TOP, SB, TD_Y, BOT = 3.85, 1.7, -3.3, -3.6
    k = (SB - TD_Y) / BELOW_SB
    Y = lambda z: SB - (z - WD) * k
    WX = -2.0
    u = 0.045                                   # world units per inch
    with st.span(b.start, b.end):
        scene = _seascape(st, -6.2, 2.7, TOP, SB, BOT, clay=0.9)
        y_cs = Y(COND_SHOE)
        h36 = st.rect(WX, (SB + y_cs) / 2, 36 * u, SB - y_cs, P.CEMENT, 0.08)
        cond = [st.rect(WX - 15 * u + 0.04, (SB + 0.05 + y_cs) / 2, 0.08, SB + 0.05 - y_cs, C_COND, 0.3),
                st.rect(WX + 15 * u - 0.04, (SB + 0.05 + y_cs) / 2, 0.08, SB + 0.05 - y_cs, C_COND, 0.3)]
        bore = st.rect(WX, (SB + y_cs) / 2, 30 * u - 0.16, SB - y_cs, P.SEA, 0.09)
        LPT = SB + 0.38
        lp = [st.rect(WX - 0.76, SB + 0.17, 0.3, 0.42, C_COND, 0.35), st.rect(WX + 0.76, SB + 0.17, 0.3, 0.42, C_COND, 0.35)]
        gb = [st.rect(WX - 1.25, SB + 0.06, 0.8, 0.12, P.STEEL_DK, 0.34), st.rect(WX + 1.25, SB + 0.06, 0.8, 0.12, P.STEEL_DK, 0.34)]
        st.fade_in([h36, bore] + cond + lp + gb, b.start, 0.4)
        # depth ruler (below sea level) at the right edge of the cutaway
        rx = 2.95
        ticks = []
        for z, txt, tt in ((WD, f"{WD:.0f} m  seabed", b.start + 0.4), (COND_SHOE, f"{COND_SHOE:.0f} m  conductor shoe", b.start + 0.6),
                           (SURF_SHOE, f"{SURF_SHOE:,.0f} m", _w(b, 0, "thousand metres"))):
            o = [st.rect(rx, Y(z), 0.22, 0.025, P.MUTED, 0.3), st.text(txt, rx + 0.2, Y(z), 0.17, P.TEXT, 0.3, align="l")]
            st.fade_in(o, tt, 0.4)
            ticks += o
        rl = st.text("depth below sea level", rx - 0.05, Y(WD) + 0.42, 0.15, P.MUTED, 0.3, align="l", kind="bold")
        st.fade_in(rl, b.start + 0.4, 0.4)
        # the 26 in bit goes down THROUGH the conductor, then drills to 1,000 m
        t_th = _w(b, 0, "through the conductor")
        t_d0 = _w(b, 0, "twenty-six inch")
        t_d1 = _w(b, 0, "thousand metres", 1.0)
        t_po = s[1]
        BIT_H, COL_H = 0.24, 0.95
        ybit = _piecewise([(b.start, SB + 1.3, "BEZIER"), (t_th, SB + 1.3, "BEZIER"), (t_d0, y_cs, "LINEAR"), (t_d1, TD_Y, "LINEAR"),
                           (t_po, TD_Y, "BEZIER"), (t_po + 1.1, TD_Y + 3.0, "LINEAR")])
        hole = st.rect(WX, y_cs, 26 * u, 0.0001, P.SEA, 0.08, anchor="t")
        _drive(st, hole, b.start, t_d1 + 0.05, lambda t: {"scale": (26 * u, max(y_cs - ybit(t), 0.0001))})
        pipe = st.rect(WX, TOP, 0.13, 1.0, P.STEEL, 0.4, anchor="t")
        collar = st.rect(WX, 0, 0.3, COL_H, P.STEEL_DK, 0.41)
        bit = st.rect(WX, 0, 24 * u, BIT_H, P.STEEL_DK, 0.42)
        tend = t_po + 1.1
        _drive(st, pipe, b.start, tend, lambda t: {"scale": (0.13, max(TOP - (ybit(t) + BIT_H + COL_H), 0.0001))})
        _drive(st, collar, b.start, tend, lambda t: {"loc": (WX, ybit(t) + BIT_H + COL_H / 2)})
        _drive(st, bit, b.start, tend, lambda t: {"loc": (WX, ybit(t) + BIT_H / 2)})
        st.fade_in([pipe, collar, bit], b.start, 0.4)
        st.fade_out([pipe, collar, bit], t_po + 0.6, 0.5)

        def depth_tag(c, t, look):
            a = _ramp(t, t_d0 - 0.3, t_d0) * (1 - _ramp(t, t_po, t_po + 0.4))
            if a <= 0:
                return
            y = ybit(t)
            z = WD + (SB - y) / k
            look.draw_text(c, f"{z:,.0f} m", WX - 0.75, y + 0.12, 0.22, P.TEXT, a, "r", "mono")
        st.procedural(t_d0 - 0.3, t_po + 0.5, 1.0, depth_tag)
        hl = _callout(st, WX - 0.95, Y(700), "26 in hole", t_d0 + 0.4, target=(WX - 13 * u, Y(700)), align="r")
        t_7 = _w(b, 0, "seven hundred")
        bx = WX + 1.0
        brk = st.line([(bx - 0.12, SB), (bx, SB), (bx, TD_Y), (bx - 0.12, TD_Y)], P.TEXT, 0.03, 0.6)
        st.draw_on(brk, t_7 - 0.2, t_7 + 0.6, "BEZIER")
        bl = pill(st, bx + 0.2, (SB + TD_Y) / 2, f"{BELOW_SB:.0f} m below the seabed", P.PANEL2, P.TEXT, 0.2, 2.0, align="l")
        st.fade_in(bl, t_7, 0.4)
        st.fade_out([brk] + bl, s[2], 0.4)
        # the 20 in surface casing with the high-pressure housing on top, run on a slim landing string, lands in the LP housing
        t_r0 = t_po + 0.5
        t_land = min(_w(b, 1, "at its top", 1.0) - 0.3, s[2] - 0.2)
        HP_B = SB - 0.02                       # landed: housing bottom
        HP_H = 0.78
        shoe_y = TD_Y + 0.12
        Lc = HP_B - shoe_y
        dy0 = 3.0 - HP_B
        cas = [st.rect(WX - 10 * u + 0.035, HP_B - Lc / 2 + dy0, 0.07, Lc, C_SURF, 0.5),
               st.rect(WX + 10 * u - 0.035, HP_B - Lc / 2 + dy0, 0.07, Lc, C_SURF, 0.5),
               st.poly([(WX - 10 * u, shoe_y + dy0), (WX + 10 * u, shoe_y + dy0), (WX + 0.25, shoe_y - 0.14 + dy0), (WX - 0.25, shoe_y - 0.14 + dy0)],
                       C_SURF, 0.5),
               st.rect(WX - 0.5, HP_B + HP_H / 2 + dy0, 0.2, HP_H, C_SURF, 0.55), st.rect(WX + 0.5, HP_B + HP_H / 2 + dy0, 0.2, HP_H, C_SURF, 0.55),
               st.rect(WX - 0.68, LPT + 0.06 + dy0, 0.16, 0.12, C_SURF, 0.56), st.rect(WX + 0.68, LPT + 0.06 + dy0, 0.16, 0.12, C_SURF, 0.56)]
        tool = st.rect(WX, HP_B + HP_H + 0.08 + dy0, 0.62, 0.16, P.STEEL_DK, 0.57)
        rs = st.rect(WX, TOP, 0.12, 0.1, P.STEEL, 0.5, anchor="t")
        st.fade_in(cas + [tool, rs], t_r0, 0.35)
        st.move(cas + [tool], t_r0 + 0.1, t_land, dy=-dy0)
        st.scale_to(rs, t_r0 + 0.1, t_land, sy=TOP - (HP_B + HP_H + 0.16))
        t_rel = s[2] + 0.2
        st.move(tool, t_rel, t_rel + 1.0, dy=1.6)
        st.scale_to(rs, t_rel, t_rel + 1.0, sy=TOP - (HP_B + HP_H + 0.16) - 1.6)
        st.fade_out([tool, rs], t_rel + 0.5, 0.5)
        st.ripple(WX, LPT + 0.06, t_land, t_land + 1.2, P.TEXT, period=0.6, r0=0.3, r1=1.2, z=0.8)
        _callout(st, WX - 1.0, -1.5, "20 in surface casing", _w(b, 1, "surface casing"), target=(WX - 10 * u, -1.5), align="r")
        t_hp = max(_w(b, 1, "high-pressure"), t_land - 0.3)
        hp1 = _callout(st, WX + 1.0, HP_B + 0.45, "high-pressure\nwellhead housing", t_hp, target=(WX + 0.6, HP_B + 0.45), align="l",
                       t_out=s[2] + 0.4)
        hp2 = _callout(st, WX + 1.0, HP_B + 0.45, "the first hardware that\ncan contain pressure", s[2] + 0.6, fg=P.WARN,
                       target=(WX + 0.6, HP_B + 0.45), align="l")
        st.ripple(WX, HP_B + 0.4, s[2] + 0.5, s[2] + 3.0, P.WARN, period=0.9, r0=0.45, r1=1.1, z=0.8)
        # everything else will hang from it: ghost BOP above, ghost later strings inside
        t_hang = _w(b, 2, "hang from it")
        gbop = _dashed_rect(st, WX - 0.75, HP_B + HP_H + 0.02, WX + 0.75, HP_B + HP_H + 1.25, P.MUTED, 0.6)
        g1 = st.dashed((WX - 0.3, HP_B + 0.1), (WX - 0.3, BOT + 0.05), P.MUTED, 0.03, 0.16, 0.1, 0.6) + \
            st.dashed((WX + 0.3, HP_B + 0.1), (WX + 0.3, BOT + 0.05), P.MUTED, 0.03, 0.16, 0.1, 0.6)
        g2 = st.dashed((WX - 0.2, HP_B + 0.1), (WX - 0.2, BOT + 0.05), P.MUTED, 0.03, 0.16, 0.1, 0.6) + \
            st.dashed((WX + 0.2, HP_B + 0.1), (WX + 0.2, BOT + 0.05), P.MUTED, 0.03, 0.16, 0.1, 0.6)
        st.fade_in(gbop, t_hang - 0.5, 0.4)
        st.fade_in(g1, t_hang - 0.1, 0.4)
        st.fade_in(g2, t_hang + 0.3, 0.4)
        gl1 = st.text("BOP (chapter 3)", WX + 0.95, HP_B + HP_H + 0.65, 0.17, P.MUTED, 0.6, align="l", kind="bold")
        gl2 = st.text("later casing strings", WX + 0.55, -2.6, 0.17, P.MUTED, 0.6, align="l", kind="bold")
        st.fade_in(gl1, t_hang - 0.3, 0.4)
        st.fade_in(gl2, t_hang + 0.3, 0.4)
        st.state["ch2_land20"] = t_land
        st.state["ch2_td"] = t_d1


# ====================================================================================================== 2.05
def beat_cement(st, tl):
    b = tl["2.05"]
    s = b.sent
    TOP, SB, Y_SH, BOT = 3.85, 1.6, -3.0, -3.6
    k = (SB - Y_SH) / BELOW_SB
    Y = lambda z: SB - (z - WD) * k
    WX = -1.9
    r_co, wall = 0.8, 0.09                 # 20 in OD half-width, wall
    r_bore = r_co - wall
    r_h = r_co * 26 / 20                  # 26 in hole
    r_ci = r_co * 28 / 20                 # conductor ID
    r_cd = r_co * 30 / 20                 # conductor OD
    r_36 = r_co * 36 / 20
    Y_CS = Y(COND_SHOE)
    RAT = 0.2
    Y_HB = Y_SH - RAT
    SHOE_TRACK_M = 56.0
    Y_FC = Y_SH + SHOE_TRACK_M * k
    with st.span(b.start, b.end):
        scene = _seascape(st, -6.2, 3.0, TOP, SB, BOT, clay=0.9)
        sand = st.rect(-1.6, -0.75, 9.2, 0.45, P.SAND, 0.02)
        st.fade_in(scene + [sand], b.start, 0.3)
        base = [st.rect(WX, (SB + Y_CS) / 2, 2 * r_36, SB - Y_CS, P.CEMENT, 0.08),           # conductor cement (2.03)
                st.rect(WX, (SB + Y_CS) / 2, 2 * r_ci, SB - Y_CS, P.SEA, 0.09),             # seawater inside the conductor
                st.rect(WX, (Y_CS + Y_HB) / 2, 2 * r_h, Y_CS - Y_HB, P.SEA, 0.09)]           # seawater in the 26 in hole
        cond = [st.rect(WX - (r_ci + r_cd) / 2, (SB + 0.05 + Y_CS) / 2, r_cd - r_ci, SB + 0.05 - Y_CS, C_COND, 0.3),
                st.rect(WX + (r_ci + r_cd) / 2, (SB + 0.05 + Y_CS) / 2, r_cd - r_ci, SB + 0.05 - Y_CS, C_COND, 0.3)]
        cas = [st.rect(WX - r_co + wall / 2, (SB + Y_SH) / 2, wall, SB - Y_SH, C_SURF, 0.3),
               st.rect(WX + r_co - wall / 2, (SB + Y_SH) / 2, wall, SB - Y_SH, C_SURF, 0.3),
               st.rect(WX, Y_FC, 2 * r_bore, 0.05, P.STEEL_DK, 0.31)]
        shoe = [st.rect(WX - r_co + 0.09, Y_SH + 0.06, 0.18, 0.12, P.STEEL_DK, 0.31), st.rect(WX + r_co - 0.09, Y_SH + 0.06, 0.18, 0.12, P.STEEL_DK, 0.31)]
        HPT = SB + 0.7
        lp = [st.rect(WX - r_cd - 0.05, SB + 0.17, 0.5, 0.34, C_COND, 0.35), st.rect(WX + r_cd + 0.05, SB + 0.17, 0.5, 0.34, C_COND, 0.35)]
        hp = [st.rect(WX - r_co - 0.1, SB + 0.33, 0.36, 0.74, C_SURF, 0.36), st.rect(WX + r_co + 0.1, SB + 0.33, 0.36, 0.74, C_SURF, 0.36)]
        hp_bore = st.rect(WX, SB + 0.33, 2 * r_bore, 0.74, P.SEA, 0.09)
        tool = st.rect(WX, HPT + 0.1, 0.8, 0.2, P.STEEL_DK, 0.37)
        rs = st.rect(WX, (TOP + HPT + 0.2) / 2, 0.2, TOP - HPT - 0.2, P.STEEL, 0.36)
        st.fade_in(base + cond + cas + shoe + lp + hp + [hp_bore, tool, rs], b.start, 0.3)

        # ---- the cement job, with volumes from real cross-sections (in^2 x m) so the U-tube moves consistently
        A_b = 18.73 ** 2
        A_oh, A_cd, A_rh = 26 ** 2 - 20 ** 2, 28 ** 2 - 20 ** 2, 26 ** 2
        L_b = BELOW_SB
        L_rh = RAT / k
        L_oh, L_cd = SURF_SHOE - COND_SHOE, COND_LEN
        V1 = A_b * L_b
        V2 = V1 + A_rh * L_rh
        V3 = V2 + A_oh * L_oh
        V4 = V3 + A_cd * L_cd                              # cement front at the seabed
        V_c = A_b * SHOE_TRACK_M + (V4 - V1) * 1.04        # cement volume: annulus + rathole + shoe track + 4 % excess
        V_end = V_c + A_b * (L_b - SHOE_TRACK_M)           # plug bumps on the float collar
        t_p0 = _w(b, 0, "cement it")
        t_sb = _w(b, 0, "appears at the seabed") + 0.2
        rate = V4 / (t_sb - t_p0)
        t_end = t_p0 + V_end / rate
        Q = lambda t: rate * _clamp(t - t_p0, 0.0, t_end - t_p0)

        def where(v):
            """Volume pumped behind a parcel -> ('bore', y) / ('rat', f) / ('ann', y) / ('out', excess)."""
            if v <= V1:
                return "bore", SB - (v / A_b) * k
            if v <= V2:
                return "rat", (v - V1) / (V2 - V1)
            if v <= V3:
                return "ann", Y_SH + ((v - V2) / A_oh) * k
            if v <= V4:
                return "ann", Y_CS + ((v - V3) / A_cd) * k
            return "out", v - V4

        bore_c = st.rect(WX, SB, 2 * r_bore, 0.0001, P.CEMENT, 0.2)
        rat_c = st.rect(WX, Y_SH, 2 * r_h, 0.0001, P.CEMENT, 0.2, anchor="t")
        ann = {}
        for sd in (-1, 1):
            ann[(sd, "oh")] = st.rect(WX + sd * (r_co + r_h) / 2, Y_SH, r_h - r_co, 0.0001, P.CEMENT, 0.2, anchor="b")
            ann[(sd, "cd")] = st.rect(WX + sd * (r_co + r_ci) / 2, Y_CS, r_ci - r_co, 0.0001, P.CEMENT, 0.2, anchor="b")
        plug = st.rect(WX, SB, 2 * r_bore - 0.04, 0.14, RUBBER, 0.25)
        cem_objs = [bore_c, rat_c, plug] + list(ann.values())
        st.fade_in([bore_c, rat_c] + list(ann.values()), t_p0, 0.05)

        def bore_fn(t):
            q = Q(t)
            front, tail = q, max(q - V_c, 0.0)
            yf = where(front)[1] if front <= V1 else Y_SH
            yt = where(tail)[1] if tail <= V1 else Y_SH
            yt = min(yt, SB)
            if front <= 0:
                return {"loc": (WX, SB), "scale": (2 * r_bore, 0.0001)}
            return {"loc": (WX, (yf + yt) / 2), "scale": (2 * r_bore, max(yt - yf, 0.0001))}
        _drive(st, bore_c, t_p0, t_end + 0.05, bore_fn, fps=15)
        _drive(st, rat_c, t_p0, t_end + 0.05, lambda t: {"scale": (2 * r_h, RAT * _clamp((Q(t) - V1) / (V2 - V1), 0, 1) + 0.0001)}, fps=15)
        for sd in (-1, 1):
            _drive(st, ann[(sd, "oh")], t_p0, t_end + 0.05,
                   lambda t: {"scale": (r_h - r_co, max(min(Q(t), V3) - V2, 0) / A_oh * k + 0.0001)}, fps=15)
            _drive(st, ann[(sd, "cd")], t_p0, t_end + 0.05,
                   lambda t: {"scale": (r_ci - r_co, max(min(Q(t), V4) - V3, 0) / A_cd * k + 0.0001)}, fps=15)
        t_plug = t_p0 + V_c / rate
        _drive(st, plug, t_p0, t_end + 0.05, lambda t: {"loc": (WX, min(where(max(Q(t) - V_c, 0.0))[1], SB) + 0.07)}, fps=15)
        st.fade_in(plug, t_plug - 0.1, 0.2)

        # material parcels: dots inside the cement and the seawater behind it, carried by the U-tube flow
        rnd = random.Random(81)
        parcels = [(rnd.uniform(0, V_c), rnd.uniform(-1, 1), rnd.choice((-1, 1))) for _ in range(70)]
        parcels += [(V_c + rnd.uniform(0, V_end - V_c), rnd.uniform(-1, 1), 0) for _ in range(26)]

        def flow_dots(c, t, look):
            if t < t_p0:
                return
            q = Q(t)
            a = min(1.0, (t - t_p0) / 0.3) * (1 - _ramp(t, t_end + 0.3, t_end + 1.0))
            if a <= 0:
                return
            cpos, wpos = [], []
            for v0, lat, sd in parcels:
                d = q - v0
                if d < 0:
                    continue
                kind, val = where(d)
                if kind == "bore":
                    p = (WX + lat * (r_bore - 0.12), val)
                elif kind == "rat":
                    p = (WX + (sd or 1) * val * (r_co + 0.1), Y_SH - RAT * 0.5)
                elif kind == "ann":
                    sd2 = sd or 1
                    r_out = r_h if val < Y_CS else r_ci
                    p = (WX + sd2 * (r_co + r_out) / 2 + lat * 0.05, val)
                else:
                    continue
                (cpos if v0 < V_c else wpos).append(p)
            look.draw_particles(c, cpos, "#ffffff", 0.03, 0.55 * a, False)
            look.draw_particles(c, wpos, SEAWATER, 0.035, 0.8 * a, True)
        st.procedural(t_p0, t_end + 1.0, 0.27, flow_dots)

        # in the landing string: cement first, then seawater behind the plug
        def rs_fn(te, kk):
            return (P.CEMENT, 0.05) if te < t_plug - 0.4 else (SEAWATER, 0.04)
        _stream(st, [(WX, TOP - 0.02), (WX, HPT + 0.2)], t_p0 - 0.8, t_end, rate=6.0, speed=3.0, z=0.45, color_fn=rs_fn, glow=False, seed=83)

        # labels for the U-tube
        _callout(st, WX - r_36 - 0.3, 0.2, "cement down the inside", _w(b, 0, "down the inside"), target=(WX - 0.35, 0.2), align="r",
                 t_out=s[1] - 0.2)
        _callout(st, WX + r_36 + 0.35, -1.9, "… and up the outside", _w(b, 0, "up the outside"), target=(WX + (r_co + r_h) / 2, -1.9),
                 t_out=s[1] - 0.2)
        _callout(st, WX + r_36 + 0.35, -0.2, "a plug, then seawater, push it", t_plug + 0.1, target=(WX + 0.3, Y(WD + 60)),
                 t_out=s[1] - 0.2, size=0.18)
        _callout(st, WX + r_36 + 0.35, Y_SH + 0.15, "only a short shoe track stays inside", t_end + 0.2,
                 target=(WX + 0.3, (Y_FC + Y_SH) / 2), size=0.18, t_out=s[2])
        # returns at the seabed, the ROV spots them
        rx0 = WX + r_cd + 0.3
        _spill(st, WX, SB + 0.02, t_sb - 0.1, b.end, r_cd + 0.3, chip=P.CEMENT, cloud=P.CEMENT, rate=9, life=2.4, reach=0.8,
               height=0.5, drift=0.18, cloud_alpha=0.32, seed=85)
        _mound(st, WX, SB + 0.02, t_sb, b.end, P.CEMENT, hmax=0.2, width=1.0, gap=r_cd + 0.3)
        t_rov = _w(b, 0, "spotted") - 0.6
        ry = 2.75
        rov = [st.rect(1.05, ry, 1.05, 0.5, ROV_BODY, 0.6), st.rect(1.05, ry + 0.31, 0.95, 0.12, P.STEEL_DK, 0.61),
               st.rect(1.62, ry - 0.05, 0.12, 0.34, P.STEEL_DK, 0.61), st.circle(0.6, ry - 0.1, 0.09, P.TEXT, 0.62),
               st.text("ROV", 1.12, ry - 0.02, 0.15, P.BG, 0.63, kind="bold")]
        teth = st.line([(1.05, ry + 0.37), (1.3, TOP - 0.02)], P.MUTED, 0.025, 0.59)
        grp = rov + [teth]
        for o in grp:
            st.move(o, b.start, t_rov, dx=2.0)
        st.fade_in(grp, t_rov - 0.1, 0.3)
        st.move(grp, t_rov, t_rov + 1.3, dx=-2.0)
        cone = st.poly([(0.55, ry - 0.1), (WX + r_cd + 0.2, SB + 0.1), (WX + r_cd + 1.1, SB + 0.35)], "#ffffff", 0.58, 0.14)
        st.fade_in(cone, t_rov + 1.2, 0.4)
        # ROV camera view (right column, below the cement term card)
        t_cam = _w(b, 0, "camera")
        vx0, vx1, vy0, vy1 = 3.5, 7.55, -3.25, 0.7
        frame = st.rect((vx0 + vx1) / 2, (vy0 + vy1) / 2, vx1 - vx0, vy1 - vy0, P.PANEL, 0.6)
        scr = st.rect((vx0 + vx1) / 2, (vy0 + vy1) / 2 + 0.12, vx1 - vx0 - 0.3, vy1 - vy0 - 0.55, P.SEA, 0.61)
        sx0, sx1, sy0, sy1 = vx0 + 0.15, vx1 - 0.15, vy0 + 0.39, vy1 - 0.15
        scx = (sx0 + sx1) / 2
        floor = st.rect(scx, sy0 + 0.35, sx1 - sx0, 0.7, P.SEABED, 0.62)
        whv = [st.rect(scx, sy0 + 0.95, 1.5, 0.5, C_COND, 0.63), st.rect(scx, sy0 + 1.45, 1.0, 0.55, C_SURF, 0.63)]
        cam_l = st.text("ROV CAM 2", sx0 + 0.15, sy1 - 0.22, 0.14, P.TEXT, 0.66, align="l", kind="mono")
        rec = st.circle(sx1 - 0.25, sy1 - 0.22, 0.06, P.BAD, 0.66)
        brk = []
        for (xx, yy, ddx, ddy) in ((sx0 + 0.08, sy1 - 0.08, 1, -1), (sx1 - 0.08, sy1 - 0.08, -1, -1), (sx0 + 0.08, sy0 + 0.08, 1, 1),
                                   (sx1 - 0.08, sy0 + 0.08, -1, 1)):
            brk.append(st.line([(xx + ddx * 0.3, yy), (xx, yy), (xx, yy + ddy * 0.3)], P.TEXT, 0.025, 0.66, alpha=0.8))
        cap = st.text("ROV camera view", (vx0 + vx1) / 2, vy0 + 0.2, 0.15, P.MUTED, 0.66, kind="bold")
        view = [frame, scr, floor, cam_l, rec, cap] + whv + brk
        st.fade_in(view, t_cam - 0.3, 0.4)
        t_view_out = s[1] + 0.8
        for kk in range(12):                                  # REC blinks until the view closes
            if t_cam + kk * 1.0 + 1.0 > t_view_out:
                break
            st.fade(rec, t_cam + kk * 1.0, t_cam + kk * 1.0 + 0.5, 1.0, 0.15)
            st.fade(rec, t_cam + kk * 1.0 + 0.5, t_cam + kk * 1.0 + 1.0, 0.15, 1.0)

        def cam_cloud(c, t, look):
            a = _ramp(t, t_cam, t_cam + 0.6) * (1 - _ramp(t, t_view_out, t_view_out + 0.4))
            if a <= 0:
                return
            c.save()
            c.clipRect(skia.Rect(sx0, sy0, sx1, sy1))
            rng = random.Random(5)
            blur = skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(2.0, 0.12 * look.k), False)
            for j in range(26):
                ph = (t * 0.22 + j / 26) % 1.0
                sd = -1 if j % 2 else 1
                x = scx + sd * (0.75 + 1.3 * ph * rng.uniform(0.5, 1.0)) + 0.3 * ph
                y = sy0 + 0.75 + 1.1 * ph * rng.uniform(0.4, 1.0)
                rr = 0.15 + 0.4 * ph
                c.drawCircle(x, y, rr, skia.Paint(Color=col(hex_rgb(P.CEMENT), 0.55 * a * (1 - ph)), AntiAlias=True, MaskFilter=blur))
            c.restore()
        st.procedural(t_cam, t_view_out + 0.5, 0.64, cam_cloud)
        ok = pill(st, scx, sy0 + 2.35, "grey cement at the seabed", P.CEMENT, P.BG, 0.19, 0.67)
        st.fade_in(ok, t_cam + 0.6, 0.4)
        chk = _check(st, scx + st.measure("grey cement at the seabed", 0.19, "bold") / 2 + 0.45, sy0 + 2.35, t_cam + 0.9, s=0.16, z=0.68)
        st.fade_out(view + ok + chk, t_view_out, 0.4)

        # the annulus, named: between casing and rock, and up inside the conductor
        t_ann = _w(b, 1, "annulus")
        outl = []
        for sd in (-1, 1):
            xa, xb = WX + sd * r_co, WX + sd * r_h
            outl.append(st.line([(xa, Y_SH), (xb, Y_SH), (xb, Y_CS), (WX + sd * r_ci, Y_CS), (WX + sd * r_ci, SB), (xa, SB), (xa, Y_SH)],
                                P.WARN, 0.035, 0.5, closed=True))
        st.fade_in(outl, t_ann - 0.1, 0.3)
        for kk in range(3):
            st.fade(outl, t_ann + 0.3 + kk * 1.2, t_ann + 0.9 + kk * 1.2, 1.0, 0.35)
            st.fade(outl, t_ann + 0.9 + kk * 1.2, t_ann + 1.5 + kk * 1.2, 0.35, 1.0)
        st.fade_out(outl, s[2], 0.5)
        _callout(st, WX - r_36 - 0.3, -1.9, "between the casing and the rock", _w(b, 1, "between the casing"),
                 target=(WX - (r_co + r_h) / 2, -1.9), align="r", t_out=s[3])
        _callout(st, WX - r_36 - 0.3, (SB + Y_CS) / 2 + 0.05, "up inside the conductor", _w(b, 1, "up inside the conductor"),
                 target=(WX - (r_co + r_ci) / 2, (SB + Y_CS) / 2 + 0.05), align="r", t_out=s[3])
        # its jobs: supports the wellhead, seals off shallow zones
        t_sup = _w(b, 2, "supports the wellhead")
        sup = []
        for sd in (-1, 1):
            sup += st.arrow(WX + sd * (r_co + r_ci) / 2, Y_CS - 0.15, WX + sd * (r_co + r_ci) / 2, SB - 0.05, P.TEXT, 0.06, 0.2, 0.7)
        st.fade_in(sup, t_sup, 0.4)
        st.ripple(WX, SB + 0.35, t_sup + 0.2, t_sup + 2.5, P.TEXT, period=0.9, r0=0.6, r1=1.6, z=0.75)
        _callout(st, WX + r_36 + 0.35, SB - 0.25, "supports the wellhead", t_sup + 0.1, target=(WX + r_cd + 0.1, SB + 0.2))
        t_seal = _w(b, 2, "seals off")
        blk = []
        for sd in (-1, 1):
            for yy in (-0.65, -0.85):
                x_far = WX + sd * (r_h + 1.1)
                x_near = WX + sd * (r_h + 0.12)
                blk += st.arrow(x_far, yy, x_near, yy, P.WATER, 0.05, 0.16, 0.6)
            blk.append(st.rect(WX + sd * (r_h + 0.04), -0.75, 0.05, 0.5, P.TEXT, 0.62))
        st.fade_in(blk, t_seal - 0.1, 0.4)
        _callout(st, WX + r_36 + 0.35, -1.35, "shallow zones sealed off", t_seal + 0.2, target=(WX + r_h + 1.15, -0.75), fg=P.SAFE)
        _callout(st, 3.5, -2.9, "how cement behaves: chapter 6 →", _w(b, 3, "chapter six") - 0.3, fg=P.MUTED, align="l")


# ====================================================================================================== 2.06
def beat_wellhead(st, tl):
    b = tl["2.06"]
    s = b.sent
    CX, SBW, BOT = -1.6, -0.2, -3.5
    tA1 = s[3] - 0.25
    with st.span(b.start, b.end):
        # ---- A: nested seats, drawn as a big section through the wellhead
        sea = st.rect(-1.6, (3.85 + SBW) / 2, 9.2, 3.85 - SBW, P.SEA, 0.0)
        soil = st.rect(-1.6, (SBW + BOT) / 2, 9.2, SBW - BOT, P.SEABED, 0.0)
        sbl = st.rect(-1.6, SBW, 9.2, 0.05, SEABED_LINE, 0.02)
        cem36 = st.rect(CX, (SBW + BOT) / 2, 2 * 1.9, SBW - BOT, P.CEMENT, 0.05)
        cond = [st.rect(CX + sd * 1.595, (BOT - 0.6) / 2, 0.11, -0.6 - BOT, C_COND, 0.2) for sd in (-1, 1)]
        inside = st.rect(CX, (1.65 + BOT) / 2, 2 * 1.54, 1.65 - BOT, P.SEA, 0.04)
        lp = [st.rect(CX + sd * 1.765, 0.05, 0.53, 1.3, C_COND, 0.25) for sd in (-1, 1)]
        A0 = [sea, soil, sbl, cem36, inside] + cond + lp
        st.fade_in(A0, b.start, 0.3)
        st.fade_out(A0, tA1, 0.5)
        # stacked bowls: the analogy, as three cups dropping into each other
        bowls = []
        bx, by = -4.85, 2.35
        for i, (r, cc) in enumerate(((0.95, C_COND), (0.72, C_SURF), (0.5, C_INT))):
            pts = [(bx + r * math.cos(th), by + 0.15 * i + 0.75 * r * math.sin(th)) for th in np.linspace(math.pi, 2 * math.pi, 22)]
            o = st.line(pts, cc, 0.11, 0.6 + 0.01 * i)
            st.move(o, b.start, s[0], dy=0.9)
            st.fade_in(o, s[0] + 0.5 * i, 0.3)
            st.move(o, s[0] + 0.5 * i, s[0] + 0.5 * i + 0.7, dy=-0.9)
            bowls.append(o)
        bl = st.text("nested seats, like stacked bowls", bx, by - 1.15, 0.17, P.MUTED, 0.6, kind="bold")
        st.fade_in(bl, _w(b, 0, "stacked bowls"), 0.4)
        st.fade_out(bowls + [bl], tA1, 0.5)
        # the HP housing on the 20 in casing lands inside the LP housing
        t_hp = _w(b, 1, "high-pressure housing")
        t_land = _w(b, 1, "lands", 1.0) + 0.3
        D = 2.15
        hp = []
        for sd in (-1, 1):
            hp += [st.rect(CX + sd * 1.245, 0.625, 0.43, 2.05, C_SURF, 0.3), st.rect(CX + sd * 1.195, -0.7, 0.53, 0.6, C_SURF, 0.3),
                   st.rect(CX + sd * 1.56, 0.79, 0.2, 0.18, C_SURF, 0.31), st.rect(CX + sd * 1.04, (BOT - 1.0) / 2, 0.12, -1.0 - BOT, C_SURF, 0.3)]
        bore = st.rect(CX, (1.65 + BOT) / 2, 2 * 0.93, 1.65 - BOT, P.SEA, 0.29)
        hp.append(bore)
        for o in hp:
            st.move(o, b.start, t_hp, dy=D)
        st.fade_in(hp, t_hp - 0.3, 0.3)
        st.move(hp, t_hp, t_land, dy=-D)
        for sd in (-1, 1):
            st.ripple(CX + sd * 1.56, 0.7, t_land, t_land + 1.0, P.TEXT, period=0.5, r0=0.1, r1=0.45, z=0.8)
        cem20 = [st.rect(CX + sd * 1.32, (BOT - 0.62) / 2, 0.44, -0.62 - BOT, P.CEMENT, 0.06) for sd in (-1, 1)]
        st.fade_in(cem20, t_land + 0.6, 0.6)
        lx = 0.95
        hp_l = pill(st, lx, 1.35 + D, "high-pressure housing\n(on the 20 in casing)", P.PANEL2, P.TEXT, 0.19, 2.0, align="l")
        ld = st.line([(lx, 1.35 + D), (CX + 1.46, 1.35 + D)], P.TEXT, 0.022, 1.98, alpha=0.7)
        st.move(hp_l + [ld], b.start, t_hp, dy=0.0)
        st.fade_in(hp_l + [ld], t_hp, 0.4)
        st.move(hp_l + [ld], t_hp, t_land, dy=-D)
        _callout(st, lx, 0.15, "low-pressure housing\n(on the 30 in conductor)", _w(b, 1, "low-pressure"), target=(CX + 2.03, 0.15), t_out=tA1)
        # each later string hangs on a casing hanger; a seal closes the gap behind it
        t_h0 = _w(b, 2, "hang inside")
        t_h1 = _w(b, 2, "casing hanger", 1.0) + 0.2
        D2 = 2.4
        hg = []
        for sd in (-1, 1):
            hg += [st.rect(CX + sd * 0.74, 0.005, 0.24, 0.69, C_INT, 0.4), st.rect(CX + sd * 0.81, -0.40, 0.38, 0.12, C_INT, 0.4),
                   st.rect(CX + sd * 0.76, -0.78, 0.28, 0.64, C_INT, 0.4), st.rect(CX + sd * 0.6775, (BOT - 1.1) / 2, 0.115, -1.1 - BOT, C_INT, 0.4)]
        for o in hg:
            st.move(o, b.start, t_h0, dy=D2)
        st.fade_in(hg, t_h0 - 0.3, 0.3)
        st.move(hg, t_h0, t_h1, dy=-D2)
        for sd in (-1, 1):
            st.ripple(CX + sd * 0.96, -0.42, t_h1, t_h1 + 1.0, P.TEXT, period=0.5, r0=0.08, r1=0.4, z=0.8)
        hg_l = pill(st, lx, -1.05 + D2, "casing hanger\n(next string hangs here)", P.PANEL2, P.TEXT, 0.19, 2.0, align="l")
        hg_d = st.line([(lx, -1.05 + D2), (CX + 0.9, -0.85 + D2)], P.TEXT, 0.022, 1.98, alpha=0.7)
        st.move(hg_l + [hg_d], b.start, t_h0, dy=0.0)
        st.fade_in(hg_l + [hg_d], _w(b, 2, "casing hanger") - 0.2, 0.4)
        st.move(hg_l + [hg_d], t_h0, t_h1, dy=-D2)
        t_seal = _w(b, 2, "with a seal")
        t_close = _w(b, 2, "closes the gap")
        seal = [st.rect(CX + sd * 0.945, -0.1 + 1.6, 0.16, 0.4, RUBBER, 0.42) for sd in (-1, 1)]
        st.fade_in(seal, t_seal - 0.2, 0.3)
        st.move(seal, t_seal, t_close - 0.1, dy=-1.6)
        st.recolor(seal, t_close, t_close + 0.4, P.SAFE)
        for sd in (-1, 1):
            st.ripple(CX + sd * 0.945, -0.1, t_close, t_close + 1.6, P.SAFE, period=0.7, r0=0.1, r1=0.5, z=0.8)
        _callout(st, lx, -1.85, "seal assembly: closes the gap\nbehind the hanger", t_seal + 0.2, target=(CX + 0.945, -0.1), t_out=tA1)
        iso = [st.rect(CX + sd * 0.86, (BOT - 0.55) / 2 - 0.0, 0.2, -0.55 - BOT, P.SAFE, 0.39, alpha=0.3) for sd in (-1, 1)]
        st.fade_in(iso, t_close + 0.2, 0.5)
        ghost = _dashed_rect(st, CX - 1.0, 0.4, CX - 0.62, 1.0, P.MUTED, 0.5) + _dashed_rect(st, CX + 0.62, 0.4, CX + 1.0, 1.0, P.MUTED, 0.5)
        t_g = b.sent_end[2] - 1.2
        st.fade_in(ghost, t_g, 0.4)
        gl = st.text("the next hanger stacks on top", CX, 1.95, 0.17, P.MUTED, 0.6, kind="bold")
        st.fade_in(gl, t_g + 0.2, 0.4)
        A = hp + cem20 + hp_l + [ld] + hg + hg_l + [hg_d] + seal + iso + ghost + [gl]
        st.fade_out(A, tA1, 0.5)
        for o in st.objs:
            pass

        # ---- B: once BOP + riser are on: a tall slender column bent by rig motion and currents -> fatigue
        tB = s[3] - 0.1
        cx, Y_SB, Y_SH, Y_RIG = -2.6, -1.25, -3.4, 3.3
        seaB = st.rect(-2.2, (3.85 + Y_SB) / 2, 8.0, 3.85 - Y_SB, P.SEA, 0.0)
        soilB = st.rect(-2.2, (Y_SB - 3.6) / 2, 8.0, Y_SB + 3.6, P.SEABED, 0.0)
        lineB = st.rect(-2.2, Y_SB, 8.0, 0.05, SEABED_LINE, 0.02)
        st.fade_in([seaB, soilB, lineB], tB, 0.5)
        t_bop = _w(b, 3, "preventer")
        t_ris = _w(b, 3, "riser")
        t_bent = _w(b, 3, "bent back and forth")
        t_rig = _w(b, 3, "rig motion")
        t_cur = _w(b, 3, "currents")
        t_fat = _w(b, 3, "fatigue")
        amp = lambda t: 0.45 * _ramp(t, t_bent - 0.3, t_bent + 1.2) * math.sin(2 * math.pi * (t - t_bent) / 3.2) if t > t_bent - 0.3 else 0.0
        colm = Column(st, tB, b.end, cx, Y_SB, Y_SH, Y_RIG, z=0.3, t_inner=tB, t_wh=tB, t_bop=t_bop - 0.3, t_riser=t_ris - 0.2,
                      amp=amp, bop_h=1.25, wh_h=0.55)
        _callout(st, cx - 1.0, colm.y_wh + 0.65, "BOP", t_bop + 0.6, target=(cx - 0.72, colm.y_wh + 0.65), align="r")
        _callout(st, cx - 0.55, 2.3, "riser", t_ris + 0.3, target=(cx - 0.15, 2.3), align="r")
        _callout(st, cx - 0.75, Y_SB + 0.3, "wellhead", tB + 0.4, target=(cx - 0.42, Y_SB + 0.3), align="r")
        mv = st.arrow(cx + 1.25, Y_RIG + 0.2, cx + 2.05, Y_RIG + 0.2, P.TEXT, 0.05, 0.18, 0.9) + \
            st.arrow(cx + 1.25, Y_RIG + 0.2, cx + 0.45 - 0.0, Y_RIG + 0.2, P.TEXT, 0.05, 0.18, 0.9)
        st.fade_in(mv, t_rig, 0.4)
        rml = st.text("rig motion", cx + 2.2, Y_RIG + 0.2, 0.17, P.TEXT, 0.9, align="l", kind="bold")
        st.fade_in(rml, t_rig + 0.1, 0.4)
        for i, yy in enumerate((0.55, 1.45, 2.35)):
            _stream(st, [(-6.1, yy), (cx - 0.35, yy)], t_cur - 0.2, b.end, SEAWATER, rate=2.5, speed=1.4, r=0.035, z=0.25,
                    alpha=0.6, seed=90 + i, tail_fade=0.6)
        cul = st.text("current", -5.95, 2.75, 0.17, SEAWATER, 0.6, align="l", kind="bold")
        st.fade_in(cul, t_cur, 0.4)
        _springs(st, colm, tB, b.end, (Y_SB - 0.45, Y_SB - 0.95), reach=0.75)
        hs = st.circle(cx, Y_SB - 0.15, 0.14, P.WARN, 0.9)
        st.fade_in(hs, t_fat - 0.2, 0.3)
        st.ripple(cx, Y_SB - 0.15, t_fat - 0.2, b.end, P.WARN, period=0.9, r0=0.15, r1=0.75, z=0.95)
        _callout(st, cx - 0.9, Y_SB - 0.75, "fatigue hot spot", t_fat, target=(cx - 0.18, Y_SB - 0.2), fg=P.WARN, align="r")
        # stress at the hot spot (live trace) and the fatigue damage adding up
        gx0, gx1, gy0, gy1 = 1.2, 7.5, -2.9, 1.1
        card = st.rect((gx0 + gx1) / 2, (gy0 + gy1) / 2, gx1 - gx0, gy1 - gy0, P.PANEL, 0.4)
        ttl = st.text("STRESS AT THE HOT SPOT", gx0 + 0.3, gy1 - 0.32, 0.16, P.MUTED, 0.5, align="l", kind="bold")
        axis = st.rect((gx0 + gx1) / 2, -0.35, gx1 - gx0 - 0.6, 0.02, P.GRID, 0.45)
        st.fade_in([card, ttl, axis], t_bent - 0.4, 0.4)
        tx0, tx1, tyc = gx0 + 0.3, gx1 - 0.3, -0.35
        win = 9.0

        def trace(c, t, look):
            a = _ramp(t, t_bent - 0.4, t_bent)
            if a <= 0:
                return
            path = skia.Path()
            n = 120
            first = True
            for i in range(n + 1):
                tt = t - win + win * i / n
                if tt < t_bent - 0.4:
                    continue
                v = amp(tt) / 0.45
                x = tx0 + (tx1 - tx0) * i / n
                y = tyc + 1.0 * v
                if first:
                    path.moveTo(x, y)
                    first = False
                else:
                    path.lineTo(x, y)
            p = skia.Paint(Color=col(hex_rgb(P.TEXT), 0.9 * a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.045,
                           StrokeJoin=skia.Paint.kRound_Join, StrokeCap=skia.Paint.kRound_Cap)
            c.drawPath(path, p)
            look.draw_particles(c, [(tx1, tyc + amp(t) / 0.45)], P.WARN, 0.06, a, True)
        st.procedural(t_bent - 0.4, b.end, 0.5, trace)
        rng_l = st.text("stress range, every cycle", tx1, gy1 - 0.32, 0.16, P.TEXT, 0.5, align="r")
        st.fade_in(rng_l, t_bent + 1.0, 0.4)
        dmg_bg = st.rect((tx0 + tx1) / 2, -2.25, tx1 - tx0, 0.22, P.GRID, 0.45, role="pill")
        dmg = st.rect(tx0, -2.25, 0.0001, 0.22, P.WARN, 0.46, anchor="l", role="pill")
        dml = st.text("fatigue damage adds up", tx0, -1.8, 0.17, P.WARN, 0.5, align="l", kind="bold")
        st.fade_in([dmg_bg, dmg, dml], t_fat - 0.1, 0.4)
        st.scale_to(dmg, t_fat, b.end - 0.6, sx=(tx1 - tx0) * 0.62, interp="LINEAR")
        dd = _callout(st, (gx0 + gx1) / 2, -3.35, "a real design driver for wellhead + conductor", _w(b, 3, "design driver") - 0.3,
                      fg=P.TEXT, align="c", size=0.18)


# ====================================================================================================== build
def build(st, tl):
    F.header(st, tl)
    beat_riserless(st, tl)
    beat_why(st, tl)
    beat_conductor(st, tl)
    beat_surface_casing(st, tl)
    beat_cement(st, tl)
    beat_wellhead(st, tl)
    b3 = tl["2.03"]
    t_cond = _w(b3, 3, "ninety metres")                    # the conductor is in: show it in the strip
    t_td = st.state.get("ch2_td", tl["2.04"].start + 7.0)  # bit at 1,000 m
    t_20 = st.state.get("ch2_land20", tl["2.04"].start + 13.0)
    F.well_strip(st, 0.0, t_cond, strings=[], marker=WD)
    F.well_strip(st, t_cond, t_td, strings=["30in conductor"], marker=COND_SHOE)
    F.well_strip(st, t_td, t_20, strings=["30in conductor"], marker=SURF_SHOE)
    F.well_strip(st, t_20, tl.dur, strings=["30in conductor", "20in surface casing"], marker=SURF_SHOE)
