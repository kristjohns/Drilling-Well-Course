"""Ch 1: Planning: casing from the bottom up.

1.01 the target and TVD vs MD  ->  1.02 hydrostatic and normal pore pressure  ->  1.03 Terzaghi's piston (overpressure)
->  1.04 stress around a borehole: collapse, fracture, leak-off test  ->  1.05 the mud-weight window chart
->  1.06 bottom-up design of the deepest shoe (chart)  ->  1.07 shallow hazards and the site survey
->  1.08 the staircase (same chart, same place)  ->  1.09 the telescope of sizes, wildcat and contingency.

Every number on screen comes from scenes/common/well_model.py (or is spoken in the narration). Animations are keyed to
the words as they are spoken (Beat.word). Colours keep one meaning (palette.py)."""
from __future__ import annotations
import math

import skia

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common.shapes import pill, STRING_COLORS
from scenes.common.look import col, hex_rgb, wrap_to, lighten
from scenes.common.stage import ease_inout

TITLE = "Planning: casing from the bottom up"

PROG = {s.name: s for s in M.programme()}
DESIGN = M.design_bottom_up()            # deepest first: 1.62 sg -> 3,370 m, 1.49 sg -> 1,960 m, 1.12 sg -> 660 m (-> 1,000 m)
N9, N13, N20, N30 = "9-5/8in intermediate", "13-3/8in intermediate", "20in surface casing", "30in conductor"
SIZE = {N30: '30"', N20: '20"', N13: '13⅜"', N9: '9⅝"'}
HOLE = {N30: '36"', N20: '26"', N13: '17½"', N9: '12¼"'}


# ============================================================================================ small helpers
def W(b, i, phrase, frac=0.0):
    """Time at which `phrase` is spoken in sentence i of beat b (asserts the phrase is really in that sentence)."""
    txt = b._sentences()[i]
    assert phrase.lower() in txt.lower(), f"{b.id} s{i}: {phrase!r} not in {txt!r}"
    return b.word(i, phrase, frac)


def ramp(t, a, b):
    """Eased 0..1 between a and b."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return ease_inout(min(1.0, max(0.0, (t - a) / (b - a))))


def env(t, a, b, fi=0.35, fo=0.35):
    """Alpha envelope: 0 outside [a, b], fades in over fi and out over fo."""
    if t <= a or t >= b:
        return 0.0
    e = 1.0
    if fi > 0:
        e = min(e, (t - a) / fi)
    if fo > 0:
        e = min(e, (b - t) / fo)
    return max(0.0, min(1.0, e))


def _path(pts, closed=False):
    p = skia.Path()
    p.moveTo(float(pts[0][0]), float(pts[0][1]))
    for q in pts[1:]:
        p.lineTo(float(q[0]), float(q[1]))
    if closed:
        p.close()
    return p


def stroke(c, look, pts, color, alpha, width, dash=None, glow=True, frac=1.0, tip=False, cap="round"):
    """Draw a polyline in world coordinates (inside a procedural). frac < 1 reveals it from its first point."""
    if alpha <= 0.003 or len(pts) < 2 or frac <= 0.0005:
        return None
    path = _path(pts)
    end = None
    if frac < 0.999:
        meas = skia.PathMeasure(path, False)
        L = meas.getLength()
        seg = skia.Path()
        meas.getSegment(0, L * frac, seg, True)
        pos = meas.getPosTan(L * frac)
        end = pos[0] if isinstance(pos, tuple) else None
        path = seg
    rgb = hex_rgb(color)
    if glow:
        c.drawPath(path, skia.Paint(Color=col(rgb, 0.32 * alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                    StrokeWidth=width * 2.4, StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join,
                                    MaskFilter=look._blur(max(3.0, width * look.k * 0.8))))
    p = skia.Paint(Color=col(rgb, alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width,
                   StrokeCap=skia.Paint.kRound_Cap if cap == "round" else skia.Paint.kButt_Cap, StrokeJoin=skia.Paint.kRound_Join)
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(list(dash), 0.0))
    c.drawPath(path, p)
    if tip and end is not None:
        r = width * 1.4
        c.drawCircle(end.x(), end.y(), r * 2.6, skia.Paint(Color=col(lighten(rgb, 0.4), 0.5 * alpha), AntiAlias=True,
                                                         MaskFilter=look._blur(max(4.0, r * look.k))))
        c.drawCircle(end.x(), end.y(), r, skia.Paint(Color=col(lighten(rgb, 0.6), alpha), AntiAlias=True))
    return end


def fill(c, pts, color, alpha):
    if alpha > 0.003:
        c.drawPath(_path(pts, True), skia.Paint(Color=col(hex_rgb(color), alpha), AntiAlias=True))


def text(c, look, s, x, y, size, color, alpha, align="c", kind="bold"):
    if alpha > 0.003:
        look.draw_text(c, s, x, y, size, color, alpha, align, kind)


def plate(c, look, x, y, w, h, color, alpha, r=None):
    """Rounded plate (pill look) drawn procedurally."""
    if alpha <= 0.003:
        return
    rr = min(w, h) / 2 if r is None else r
    rect = skia.Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
    c.drawRRect(skia.RRect.MakeRectXY(rect, rr, rr), skia.Paint(Color=col(hex_rgb(color), alpha), AntiAlias=True))


def leader(st, p0, p1, color=P.MUTED, z=0.45, alpha=0.8):
    return st.line([p0, p1], color, 0.022, z, alpha=alpha)


# ============================================================================================ 1.01 target, TVD vs MD
SEA_Y01, U01 = 3.2, 6.3 / 4200.0     # sea level (world y) and true scale (world units per metre, both axes) in 1.01


def y01(z):
    return SEA_Y01 - z * U01


def _jwell(md):
    """J-profile for the TVD/MD comparison: vertical to a 1,500 m kick-off, build 3 deg/30 m to 30 deg, hold.
    Returns (tvd, horizontal offset), metres. Real geometry: MD at the 3,950 m target comes out ~4,300 m."""
    KOP, R, inc = 1500.0, 30.0 / math.radians(3.0), math.radians(30.0)
    if md <= KOP:
        return md, 0.0
    sb = R * inc
    if md <= KOP + sb:
        a = (md - KOP) / R
        return KOP + R * math.sin(a), R * (1 - math.cos(a))
    tv0, h0 = KOP + R * math.sin(inc), R * (1 - math.cos(inc))
    return tv0 + (md - KOP - sb) * math.cos(inc), h0 + (md - KOP - sb) * math.sin(inc)


def _jwell_md_at(tvd_target):
    lo, hi = 0.0, 8000.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if _jwell(mid)[0] < tvd_target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def beat_target(st, tl):
    b = tl["1.01"]
    s = b.sent
    X0, X1 = -6.95, 7.85
    cx = (X0 + X1) / 2
    XT = 3.0                                      # target x
    md_t = _jwell_md_at(M.RES_TOP)
    off_t = _jwell(md_t)[1]
    XR = XT - off_t * U01                          # rig x (true lateral scale)
    with st.span(b.start, b.end):
        # --- the section: sea, seabed, distinct strata, the target sand
        sea = st.rect(cx, (y01(0) + y01(M.WATER_DEPTH)) / 2, X1 - X0, y01(0) - y01(M.WATER_DEPTH), P.SEA, 0.0)
        surf = st.line([(X0, y01(0)), (X1, y01(0))], P.PORE, 0.03, 0.05, alpha=0.75)
        layers = [(300, 1000, P.ROCK2), (1000, 2200, P.ROCK), (2200, 3000, P.SHALE), (3000, 3400, P.ROCK2), (3400, M.RES_TOP, P.SHALE),
                  (M.RES_TOP, M.RES_BASE, P.SAND), (M.RES_BASE, 4300, P.ROCK)]
        strata = [st.rect(cx, (y01(a) + y01(c_)) / 2, X1 - X0, y01(a) - y01(c_), colr, 0.0) for a, c_, colr in layers]
        seams = [st.rect(cx, y01(a), X1 - X0, 0.012, "#000000", 0.02, alpha=0.35) for a, _, _ in layers[1:]]
        seabed = st.rect(cx, y01(M.WATER_DEPTH), X1 - X0, 0.04, P.SEABED, 0.03)
        st.fade_in([sea, surf], b.start + 0.1, 0.5)
        st.fade_in(seabed, b.start + 0.35, 0.4)
        for i, o in enumerate(strata):
            st.fade_in([o] + ([seams[i - 1]] if i else []), s[0] + 0.15 + 0.22 * i, 0.5)
        # --- depth ruler (left gutter): metres below sea level
        rul = [st.text("depth below sea level (m)", X0, y01(0) + 0.33, 0.16, P.MUTED, 0.3, align="l", kind="bold")]
        for zt in (0, 1000, 2000, 3000, 4000):
            rul.append(st.text(f"{zt:,}", X0 - 0.12, y01(zt), 0.18, P.TEXT, 0.3, align="r", kind="mono"))
            rul.append(st.rect(X0 + 0.09, y01(zt), 0.18, 0.02, P.TEXT, 0.3, alpha=0.8))
        sbl = st.text("seabed · 300 m", X0 + 0.3, y01(M.WATER_DEPTH) - 0.2, 0.18, P.TEXT, 0.3, align="l", kind="bold")
        st.fade_in(rul + [sbl], s[0] + 0.3, 0.5)
        # --- the target (s1)
        t_tg = W(b, 1, "target")
        glow = st.rect(cx, (y01(M.RES_TOP) + y01(M.RES_BASE)) / 2, X1 - X0, y01(M.RES_TOP) - y01(M.RES_BASE), P.WARN, 0.04, alpha=0.35, role="flat")
        st.fade_in(glow, t_tg, 0.4)
        st.fade(glow, t_tg + 0.4, t_tg + 1.4, 1.0, 0.45)
        bull = [st.ring(XT, y01(M.RES_TOP) - 0.02, 0.2, 0.05, P.WARN, 0.4), st.circle(XT, y01(M.RES_TOP) - 0.02, 0.07, P.WARN, 0.41)]
        st.pop_in(bull, t_tg + 0.1, 0.4)
        st.ripple(XT, y01(M.RES_TOP), t_tg + 0.1, t_tg + 2.5, P.WARN, period=0.9, r0=0.15, r1=0.9)
        tgt = pill(st, 5.55, y01(M.RES_TOP) - 0.12, "TARGET · sandstone · 3,950 m", P.PANEL2, P.WARN, 0.22, 0.5)
        st.fade_in(tgt, W(b, 1, "sandstone"), 0.4)
        # --- TVD: a dashed plumb line from sea level to the target, with its counter (s2)
        t_tvd0, t_tvd1 = W(b, 2, "true vertical depth"), W(b, 2, "straight down", 1.0)
        y_t = y01(M.RES_TOP)

        def draw_tvd(c, t, look):
            f = ramp(t, t_tvd0, t_tvd1)
            a = env(t, t_tvd0 - 0.05, b.end, 0.2, 0.3)
            y = SEA_Y01 + (y_t - SEA_Y01) * f
            stroke(c, look, [(XT, SEA_Y01), (XT, y)], P.TEXT, 0.95 * a, 0.045, dash=(0.16, 0.1), glow=False)
            z = (SEA_Y01 - y) / U01
            text(c, look, f"TVD {z:,.0f} m", XT + 0.2, min(y + 0.28, 2.1), 0.22, P.TEXT, a, "l", "mono")
        st.procedural(t_tvd0 - 0.05, b.end, 0.45, draw_tvd)
        tvd_l = pill(st, XT + 0.2, 0.15, "TVD: straight down", P.PANEL2, P.TEXT, 0.22, 0.5, align="l")
        st.fade_in(tvd_l, W(b, 2, "straight down"), 0.4)
        # --- MD: a J-shaped well from a rig offset to the left, tip counter in measured metres (s2 end)
        t_md0 = W(b, 2, "along the hole") - 0.3
        t_md1 = max(t_md0 + 2.6, s[3] - 0.2)
        mds = [i * 25.0 for i in range(int(md_t / 25) + 1)] + [md_t]
        pts = [(XR + _jwell(m)[1] * U01, y01(_jwell(m)[0])) for m in mds]

        def draw_md(c, t, look):
            f = ramp(t, t_md0, t_md1)
            a = env(t, t_md0 - 0.05, b.end, 0.2, 0.3)
            stroke(c, look, pts, P.STEEL, a, 0.07, glow=True, frac=f, tip=f < 0.999)
            if f > 0.002:
                k = min(int(f * (len(pts) - 1)), len(pts) - 1)
                x, y = pts[k]
                text(c, look, f"MD {mds[k]:,.0f} m", x - 0.22, y + 0.05, 0.22, P.STEEL, a, "r", "mono")
        st.procedural(t_md0 - 0.05, b.end, 0.46, draw_md)
        md_l = pill(st, -0.75, 0.15, "measured depth: along the hole", P.PANEL2, P.STEEL, 0.22, 0.5, align="r")
        st.fade_in(md_l, t_md0 + 0.6, 0.4)
        # --- datums (s3): the rig on the surface; sea level is our zero, real plans use the rig floor
        t_rig = s[3] - 0.1
        rig = [st.rect(XR, SEA_Y01 + 0.1, 0.9, 0.12, P.STEEL_DK, 0.6, role="solid"),
               st.rect(XR - 0.32, SEA_Y01 - 0.02, 0.12, 0.2, P.STEEL_DK, 0.6, role="solid"),
               st.rect(XR + 0.32, SEA_Y01 - 0.02, 0.12, 0.2, P.STEEL_DK, 0.6, role="solid"),
               st.poly([(XR - 0.18, SEA_Y01 + 0.16), (XR + 0.18, SEA_Y01 + 0.16), (XR + 0.04, SEA_Y01 + 0.62), (XR - 0.04, SEA_Y01 + 0.62)], P.STEEL, 0.6)]
        st.fade_in(rig, t_md0 - 0.3, 0.4)
        floor = st.line([(XR - 1.0, SEA_Y01 + 0.16), (XR + 0.5, SEA_Y01 + 0.16)], P.WARN, 0.03, 0.62)
        rf = pill(st, XR - 1.15, SEA_Y01 + 0.3, "real well plans: zero at the rig floor", P.PANEL2, P.WARN, 0.19, 0.62, align="r")
        sl = pill(st, XR - 1.15, SEA_Y01 - 0.3, "this film: zero at sea level", P.PANEL2, P.PORE, 0.19, 0.62, align="r")
        st.fade_in([floor] + rf, W(b, 3, "rig floor") - 0.2, 0.4)
        st.fade_in(sl, t_rig + 0.4, 0.4)
        note = st.text("our example well is drilled near-vertical, so its MD ≈ TVD", X0 + 0.05, -3.45, 0.17, P.MUTED, 0.5, align="l")
        st.fade_in(note, W(b, 3, "instead"), 0.5)
        # --- the job (s4): reach it safely, find out what is in it
        st.fade_out(md_l + tvd_l, s[4] - 0.4, 0.4)
        t_safe = W(b, 4, "reach the target safely")
        job = pill(st, 5.55, -1.1, "reach it safely", P.PANEL2, P.SAFE, 0.24, 0.6)
        st.fade_in(job, t_safe, 0.4)
        t_what = W(b, 4, "find out what is in it")
        what = pill(st, 5.55, -1.8, "gas?   oil?   water?", P.PANEL2, P.TEXT, 0.24, 0.6)
        st.fade_in(what, t_what, 0.4)
        w = st.measure("gas?   oil?   water?", 0.24, "bold")
        for i, (word, colr) in enumerate((("gas?", P.GAS), ("oil?", P.OIL), ("water?", P.WATER))):
            pass
        dots = [st.circle(5.55 - w / 2 - 0.05 + i * 0.0, -1.8, 0.0, P.GAS, 0.0) for i in range(0)]
        orbs = []
        for i, colr in enumerate((P.GAS, P.OIL, P.WATER)):
            o = st.circle(XT - 0.25 + 0.25 * i, y01((M.RES_TOP + M.RES_BASE) / 2), 0.075, colr, 0.42)
            orbs.append(o)
            st.pop_in(o, t_what + 0.3 + 0.25 * i, 0.35)
        st.ripple(XT, y01(M.RES_TOP), t_what, b.end, P.WARN, period=1.3, r0=0.2, r1=1.0)


# ============================================================================================ 1.02 hydrostatics, normal pressure
def beat_hydrostatic(st, tl):
    b = tl["1.02"]
    s = b.sent
    c = Chart(st, -1.3, -2.7, 4.0, 5.2, (0, 700), (0, 4000), invert_y=True)
    AX, AW = -4.45, 2.3                  # left panel (diver -> two columns -> rock) centre / width
    top, bot = c.Y(0), c.Y(4000)
    with st.span(b.start, b.end):
        # ---------------- A1: the diver (s0-s2)
        t_a1_out = s[3] - 0.1
        with st.span(b.start, t_a1_out + 0.5):
            Ytop, Ybot = 2.5, -2.7
            ym = lambda zm: Ytop - zm * (Ytop - Ybot) / 14.0        # 0..14 m
            col_ = st.rect(AX, (Ytop + Ybot) / 2, AW, Ytop - Ybot, P.SEA, 0.0)
            surf = st.line([(AX - AW / 2, Ytop), (AX + AW / 2, Ytop)], P.PORE, 0.03, 0.05, alpha=0.8)
            ticks = []
            for zm in (0, 5, 10):
                ticks.append(st.rect(AX - AW / 2 + 0.12, ym(zm), 0.24, 0.02, P.TEXT, 0.1, alpha=0.6))
                ticks.append(st.text(f"{zm} m", AX - AW / 2 + 0.3, ym(zm), 0.17, P.TEXT, 0.1, align="l", kind="mono", alpha=0.8))
            st.fade_in([col_, surf] + ticks, b.start + 0.15, 0.5)
            t_dive0, t_dive1 = W(b, 1, "Dive"), W(b, 1, "ten metres", 1.0) + 0.4
            DX = AX + 0.35

            def draw_diver(c_, t, look):
                a = env(t, b.start + 0.3, t_a1_out + 0.45, 0.4, 0.4)
                f = ramp(t, t_dive0, t_dive1)
                zm = 10.0 * f
                y = ym(zm) - 0.35
                rgb = hex_rgb(P.WARN)
                # a simple diver: head, body, fins, bubbles
                c_.drawCircle(DX, y + 0.22, 0.13, skia.Paint(Color=col(rgb, a), AntiAlias=True))
                c_.drawRRect(skia.RRect.MakeRectXY(skia.Rect(DX - 0.1, y - 0.28, DX + 0.1, y + 0.08), 0.08, 0.08),
                             skia.Paint(Color=col(rgb, a), AntiAlias=True))
                fill(c_, [(DX - 0.1, y - 0.28), (DX + 0.1, y - 0.28), (DX + 0.2, y - 0.5), (DX - 0.2, y - 0.5)], P.STEEL_DK, a)
                for k in range(4):
                    ph = (t * 0.9 + k * 0.25) % 1.0
                    by = y + 0.4 + ph * (Ytop - y - 0.45)
                    if by < Ytop - 0.05:
                        c_.drawCircle(DX + 0.05 * math.sin(6 * ph + k), by, 0.035 + 0.02 * ph,
                                      skia.Paint(Color=col((0.85, 0.93, 1.0), 0.5 * a * (1 - ph)), AntiAlias=True))
                # gauge read-out beside the diver: pressure above the surface value
                bar_ = M.bar(zm, 1.03)
                text(c_, look, f"+{bar_:.1f} bar", DX - 0.32, y - 0.02, 0.26, P.TEXT, a, "r", "mono")
            st.procedural(b.start + 0.3, t_a1_out + 0.5, 0.4, draw_diver)
            note = st.text("above the pressure\nat the surface", AX, ym(10) - 1.15, 0.16, P.MUTED, 0.4)
            st.fade_in(note, t_dive1 - 0.3, 0.4)
            g1 = pill(st, AX, Ybot + 0.35, "+1 bar per 10 m of water", P.PANEL2, P.TEXT, 0.19, 0.4)
            st.fade_in(g1, W(b, 1, "one more bar"), 0.4)
            st.fade_out([col_, surf, note] + ticks + g1, t_a1_out, 0.4)
        # ---------------- B: the chart (from s2)
        fr = c.frame(xticks=[0, 200, 400, 600], yticks=[0, 1000, 2000, 3000, 4000], xlabel="pressure (bar)", ylabel="depth (m)")
        st.fade_in(fr, s[2] - 0.1, 0.5)
        eq = st.text("P = ρ · g · h", 5.45, 0.25, 0.46, P.TEXT, 0.4, kind="bold")
        eq_s = st.text("density × gravity × depth", 5.45, -0.3, 0.19, P.MUTED, 0.4)
        st.fade_in(eq, W(b, 2, "density"), 0.4)
        st.fade_in(eq_s, W(b, 2, "depth"), 0.4)
        # ---------------- A2: two 4 km columns, sea water and mud, aligned to the chart (s3)
        t_cols = s[3] - 0.05
        t_a2_out = s[4] - 0.1
        zs = [0.0, 4000.0]
        with st.span(t_cols, t_a2_out + 0.5):
            xs_, xm_ = AX - 0.55, AX + 0.55
            cw = 0.8
            frames = [st.rect(xs_, (top + bot) / 2, cw + 0.08, top - bot, P.PANEL2, 0.0, role="flat"),
                      st.rect(xm_, (top + bot) / 2, cw + 0.08, top - bot, P.PANEL2, 0.0, role="flat")]
            sw = st.rect(xs_, top, cw, 0.0001, P.SEA, 0.05, anchor="t")
            mw = st.rect(xm_, top, cw, 0.0001, P.MUD, 0.05, anchor="t")
            st.fade_in(frames, t_cols, 0.4)
            t_sw0 = t_cols + 0.1
            t_mw0 = W(b, 3, "heavier liquid") - 0.2
            st.fade_in(sw, t_sw0, 0.1)
            st.scale_to(sw, t_sw0, t_sw0 + 1.6, sy=top - bot)
            st.fade_in(mw, t_mw0, 0.1)
            st.scale_to(mw, t_mw0, t_mw0 + 1.6, sy=top - bot)
            lab = [st.text("sea\nwater", xs_, top + 0.38, 0.17, P.PORE, 0.2, kind="bold"),
                   st.text("mud", xm_, top + 0.3, 0.17, P.MUD, 0.2, kind="bold")]
            st.fade_in(lab[0], t_sw0, 0.3)
            st.fade_in(lab[1], t_mw0, 0.3)
            st.counter(xs_, bot - 0.32, t_sw0, t_sw0 + 1.6, 0, M.bar(4000, 1.03), fmt="{:.0f} bar", size=0.2, color=P.PORE, hold=t_a2_out + 0.4)
            st.counter(xm_, bot - 0.32, t_mw0, t_mw0 + 1.6, 0, M.bar(4000, 1.62), fmt="{:.0f} bar", size=0.2, color=P.MUD, hold=t_a2_out + 0.4)
            st.fade_out(frames + [sw, mw] + lab, t_a2_out, 0.4)
        w1 = c.curve([M.bar(z, 1.03) for z in zs], zs, P.PORE, 0.07, 0.3)
        w2 = c.curve([M.bar(z, 1.62) for z in zs], zs, P.MUD, 0.07, 0.3)
        st.draw_on(w1, t_sw0, t_sw0 + 1.6)
        st.draw_on(w2, t_mw0, t_mw0 + 1.6)
        l1 = st.text("sea water\n1.03 sg", c.X(M.bar(3000, 1.03)) - 0.2, c.Y(3000) + 0.15, 0.19, P.PORE, 0.3, align="r", kind="bold")
        l2 = st.text("mud, 1.62 sg", c.X(M.bar(1800, 1.62)) + 0.2, c.Y(1800), 0.19, P.MUD, 0.3, align="l", kind="bold")
        st.fade_in(l1, t_sw0 + 1.0, 0.4)
        st.fade_in(l2, t_mw0 + 1.2, 0.4)
        sg = st.text("sg = density ÷ density of fresh water", 5.45, -1.2, 0.19, P.TEXT, 0.4)
        sg2 = st.text("fresh water 1.00  ·  sea water 1.03", 5.45, -1.65, 0.19, P.MUTED, 0.4)
        st.fade_in(sg, W(b, 3, "specific gravity"), 0.4)
        st.fade_in(sg2, W(b, 3, "fresh water is one"), 0.4)
        # ---------------- A3: rock with pores, connected up to the sea (s4, s5)
        t_rock = s[4] - 0.05
        with st.span(t_rock, b.end):
            sea = st.rect(AX, (top + c.Y(M.WATER_DEPTH)) / 2, AW, top - c.Y(M.WATER_DEPTH), P.SEA, 0.0)
            rock = st.rect(AX, (c.Y(M.WATER_DEPTH) + bot) / 2, AW, c.Y(M.WATER_DEPTH) - bot, P.ROCK, 0.0)
            sbd = st.rect(AX, c.Y(M.WATER_DEPTH), AW, 0.035, P.SEABED, 0.02)
            st.fade_in([sea, rock, sbd], t_rock, 0.5)
            # magnified pore inset at 2,000 m: grains with water between them
            ZG = 2000.0
            ix, iy, ir = AX, c.Y(ZG), 0.72
            ring = st.ring(ix, iy, ir + 0.05, 0.05, P.TEXT, 0.3, alpha=0.85)
            water = st.circle(ix, iy, ir, P.WATER, 0.2, role="flat")
            grains = []
            for k, (gx, gy, gr) in enumerate([(-0.38, 0.33, 0.25), (0.15, 0.42, 0.22), (0.45, 0.05, 0.2), (-0.05, 0.0, 0.24), (-0.45, -0.2, 0.21),
                                              (0.2, -0.38, 0.24), (-0.25, -0.5, 0.17), (0.5, -0.42, 0.14), (0.48, 0.45, 0.12), (-0.6, 0.12, 0.1)]):
                if math.hypot(gx, gy) + gr <= ir + 0.02:
                    grains.append(st.circle(ix + gx, iy + gy, gr, "#a08c6e", 0.25, role="flat"))
            mag = st.text("pores, magnified", ix, iy - ir - 0.25, 0.16, P.MUTED, 0.3)
            st.fade_in([water, ring, mag] + grains, W(b, 4, "pores") - 0.1, 0.5)
            st.counter(ix, iy + ir + 0.3, W(b, 4, "pore pressure"), W(b, 4, "pore pressure") + 1.2, 0, M.bar(ZG, 1.03),
                       fmt="{:.0f} bar", size=0.22, color=P.PORE)
            # the connected path up to the seabed (draws on at "connect all the way up")
            t_con = W(b, 5, "connect all the way up")
            chan = [(ix + 0.1, iy + ir), (ix + 0.3, iy + ir + 0.4), (ix - 0.2, iy + 1.0), (ix + 0.25, iy + 1.5), (ix - 0.15, iy + 2.0),
                    (ix + 0.1, c.Y(M.WATER_DEPTH))]

            def draw_chan(cv, t, look):
                a = env(t, t_con - 0.05, b.end, 0.2, 0.3)
                f = ramp(t, t_con, t_con + 1.6)
                stroke(cv, look, chan, P.WATER, a, 0.07, glow=True, frac=f, tip=f < 0.999)
            st.procedural(t_con - 0.05, b.end, 0.31, draw_chan)
            st.flow(chan, t_con + 1.6, b.end, P.PORE, n=8, speed=0.5, r=0.035, z=0.32)
            dot = c.dot(M.bar(ZG, 1.03), ZG, 0.1, P.PORE, 0.5)
            st.pop_in(dot, W(b, 4, "pore pressure") + 1.2, 0.4)
            gl = leader(st, (ix + ir + 0.05, iy), (c.X(M.bar(ZG, 1.03)) - 0.12, c.Y(ZG)), P.PORE, 0.29, 0.6)
            st.fade_in(gl, W(b, 4, "pore pressure") + 1.2, 0.4)
            t_norm = W(b, 5, "normal pressure")
            st.ripple(c.X(M.bar(ZG, 1.03)), c.Y(ZG), t_norm - 0.2, b.end, P.PORE, period=1.1, r0=0.1, r1=0.6)
            nl = pill(st, 5.45, -2.55, "normal pore pressure = a sea-water column", P.PANEL2, P.PORE, 0.2, 0.5)
            st.fade_in(nl, W(b, 5, "salty water"), 0.4)
            st.recolor(l1, t_norm, t_norm + 0.4, P.TEXT)
            st.recolor(l1, t_norm + 0.6, t_norm + 1.0, P.PORE)


# ============================================================================================ 1.03 Terzaghi's piston and spring
YB3, YP3, HW3 = -2.3, 0.55, 0.7            # cylinder floor, piston rest height (bottom face), inner half-width


def _cylinder_draw(cx, hole, d_fn, sig_fn, p_fn, load_kind, t_load, t_end, leak_fn, z_label=None):
    """Procedural cylinder internals: water, zig-zag spring, piston with a hole, the load, escaping water.
    d_fn(t): piston travel down; sig_fn/p_fn: total load and water pressure (0..1); leak_fn(t): escape rate 0..1."""
    rnd = [((k * 0.61803) % 1.0, (k * 0.3819 + 0.2) % 1.0) for k in range(24)]

    def draw(c, t, look):
        a = env(t, t_load[0], t_end, 0.4, 0.4)
        if a <= 0:
            return
        d = d_fn(t)
        yp = YP3 - d
        # water below the piston
        fill(c, [(cx - HW3, YB3), (cx + HW3, YB3), (cx + HW3, yp), (cx - HW3, yp)], P.WATER, 0.78 * a)
        # zig-zag spring from the floor to the piston (it really shortens)
        n = 9
        pts = [(cx, YB3 + 0.02)]
        h = yp - 0.04 - (YB3 + 0.06)
        for k in range(1, 2 * n):
            pts.append((cx + (0.48 if k % 2 else -0.48), YB3 + 0.06 + h * k / (2 * n)))
        pts.append((cx, yp - 0.04))
        stroke(c, look, pts, P.STEEL, a, 0.07, glow=False)
        # piston (two halves, a hole between them)
        pr = skia.Paint(Color=col(hex_rgb(P.STEEL_DK), a), AntiAlias=True)
        c.drawRect(skia.Rect(cx - HW3, yp, cx - hole / 2, yp + 0.22), pr)
        c.drawRect(skia.Rect(cx + hole / 2, yp, cx + HW3, yp + 0.22), pr)
        c.drawRect(skia.Rect(cx - HW3, yp + 0.17, cx - hole / 2, yp + 0.22), skia.Paint(Color=col(hex_rgb(P.STEEL), a), AntiAlias=True))
        c.drawRect(skia.Rect(cx + hole / 2, yp + 0.17, cx + HW3, yp + 0.22), skia.Paint(Color=col(hex_rgb(P.STEEL), a), AntiAlias=True))
        # escaped water pooling on top of the piston (volume = piston travel)
        pool = min(d * 0.55, 0.3)
        if pool > 0.004:
            fill(c, [(cx - HW3, yp + 0.22), (cx - 0.42, yp + 0.22), (cx - 0.42, yp + 0.22 + pool), (cx - HW3, yp + 0.22 + pool)], P.WATER, 0.7 * a)
            fill(c, [(cx + 0.42, yp + 0.22), (cx + HW3, yp + 0.22), (cx + HW3, yp + 0.22 + pool), (cx + 0.42, yp + 0.22 + pool)], P.WATER, 0.7 * a)
        # the load on the piston
        sg = sig_fn(t)
        if load_kind == "weight":
            if t >= t_load[0]:
                drop = 1.0 - ramp(t, t_load[0], t_load[1])
                yb = yp + 0.22 + drop * 1.6
                g = skia.GradientShader.MakeLinear([skia.Point(cx - 0.4, 0), skia.Point(cx + 0.4, 0)],
                                                   [col(hex_rgb("#3c4659"), a), col(hex_rgb("#6b7891"), a), col(hex_rgb("#3c4659"), a)])
                c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(cx - 0.4, yb, cx + 0.4, yb + 0.62), 0.05, 0.05), skia.Paint(Shader=g, AntiAlias=True))
                text(c, look, "LOAD", cx, yb + 0.31, 0.17, P.TEXT, a * min(1.0, sg + 0.3), "c", "bold")
        else:
            # sediment layers piling up on the piston as load is added
            nl = int(round(sg * 5))
            y0 = yp + 0.22
            for k in range(nl):
                colr = ("#8a7558", "#6e5d4b", "#7d6a52", "#5b4d3f", "#93805f")[k]
                y1 = y0 + 0.16
                c.drawRect(skia.Rect(cx - HW3 + 0.02, y0, cx + HW3 - 0.02, y1), skia.Paint(Color=col(hex_rgb(colr), a), AntiAlias=True))
                y0 = y1
        # water squirting up through the hole while the spring takes over
        lk = leak_fn(t)
        if lk > 0.01:
            pos = []
            for k, (u, v) in enumerate(rnd):
                ph = (t * 1.6 + u) % 1.0
                if v > lk + 0.05:
                    continue
                side = -1 if k % 2 else 1
                x = cx + side * (0.04 + 0.32 * ph ** 1.5)
                y = yp + 0.1 + 0.55 * math.sin(math.pi * min(ph, 1.0)) * (1.0 - 0.3 * ph) + 0.05
                pos.append((x, y))
            look.draw_particles(c, pos, P.WATER, 0.035, a, glow=True)
    return draw


def _gauge_draw(gx, sig_fn, p_fn, t0, t1, H=2.6):
    """Two bars: water pressure p (pore blue) and grain stress σ′ = σ − p (steel); a dashed line marks the load σ."""
    def draw(c, t, look):
        a = env(t, t0, t1, 0.4, 0.4)
        if a <= 0:
            return
        sg, p = sig_fn(t), p_fn(t)
        sp = max(sg - p, 0.0)
        for k, (v, colr) in enumerate(((p, P.PORE), (sp, P.STEEL))):
            x = gx + k * 0.42
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x - 0.14, YB3, x + 0.14, YB3 + H), 0.06, 0.06),
                        skia.Paint(Color=col(hex_rgb(P.PANEL2), a), AntiAlias=True))
            if v > 0.003:
                c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x - 0.12, YB3 + 0.02, x + 0.12, YB3 + 0.02 + (H - 0.04) * v), 0.05, 0.05),
                            skia.Paint(Color=col(hex_rgb(colr), a), AntiAlias=True))
        text(c, look, "p", gx, YB3 + H + 0.22, 0.2, P.PORE, a, "c", "bold")
        text(c, look, "σ′", gx + 0.42, YB3 + H + 0.22, 0.2, P.STEEL, a, "c", "bold")
        if sg > 0.01:
            yl = YB3 + 0.02 + (H - 0.04) * sg
            stroke(c, look, [(gx - 0.24, yl), (gx + 0.66, yl)], P.TEXT, a, 0.025, dash=(0.07, 0.05), glow=False, cap="butt")
            text(c, look, "σ", gx + 0.78, yl, 0.2, P.TEXT, a, "l", "bold")
    return draw


def beat_terzaghi(st, tl):
    b = tl["1.03"]
    s = b.sent
    AX, BX = -3.55, 1.0
    with st.span(b.start, b.end):
        # ---------- cylinder A appears on "Picture a spring"
        t_a = W(b, 1, "Picture") - 0.1
        walls = lambda cx: [st.rect(cx - HW3 - 0.05, (YB3 + 1.75) / 2 - 0.03, 0.1, 1.75 - YB3 + 0.06, P.STEEL_DK, 0.3),
                            st.rect(cx + HW3 + 0.05, (YB3 + 1.75) / 2 - 0.03, 0.1, 1.75 - YB3 + 0.06, P.STEEL_DK, 0.3),
                            st.rect(cx, YB3 - 0.05, 2 * HW3 + 0.2, 0.1, P.STEEL_DK, 0.3)]
        wa = walls(AX)
        st.fade_in(wa, t_a, 0.5)
        tL0 = W(b, 2, "Load it") - 0.15
        tL1 = tL0 + 0.45
        t_leak = W(b, 2, "leaks away")
        tau = 1.1
        sigA = lambda t: ramp(t, tL0, tL1)
        pA = lambda t: sigA(t) if t < t_leak else math.exp(-(t - t_leak) / tau)
        dA = lambda t: 0.8 * max(sigA(t) - pA(t), 0.0)
        leakA = lambda t: pA(t) if t >= t_leak else 0.0
        st.procedural(t_a, b.end, 0.25, _cylinder_draw(AX, 0.09, dA, sigA, pA, "weight", (tL0, tL1), b.end + 1, leakA))
        st.procedural(t_a, b.end, 0.28, _gauge_draw(AX + 1.25, sigA, pA, t_a, b.end + 1))
        # mapping tags, keyed to the words
        tags = [("spring = rock grains", P.STEEL, W(b, 1, "rock grains"), -1.55),
                ("water = pore fluid", P.WATER, W(b, 1, "pore fluid"), -2.25)]
        for txt, colr, t, y in tags:
            p_ = pill(st, AX - 1.2, y, txt, P.PANEL2, colr, 0.19, 0.5, align="r")
            st.fade_in(p_, t - 0.1, 0.4)
        hole_tag = pill(st, AX - 1.2, 0.95, "tiny hole", P.PANEL2, P.TEXT, 0.19, 0.5, align="r")
        hl = leader(st, (AX - 1.2, 0.95), (AX - 0.06, YP3 + 0.12), P.MUTED, 0.49)
        st.fade_in(hole_tag + [hl], W(b, 1, "tiny hole") - 0.1, 0.4)
        st.fade_out([hl], tL0, 0.3)
        ta = st.text("drains freely", AX, YB3 - 0.42, 0.22, P.TEXT, 0.3, kind="bold")
        st.fade_in(ta, t_a + 0.3, 0.4)
        # narration-synced captions for A
        cap1 = pill(st, AX + 0.3, 2.5, "first the water carries the load", P.PANEL2, P.PORE, 0.19, 0.5)
        cap2 = pill(st, AX + 0.3, 2.5, "water leaks out: the spring takes over", P.PANEL2, P.STEEL, 0.19, 0.5)
        st.fade_in(cap1, W(b, 2, "water takes the load"), 0.3)
        st.fade_out(cap1, t_leak - 0.1, 0.3)
        st.fade_in(cap2, t_leak + 0.2, 0.3)
        st.fade_out(cap2, s[3] - 0.3, 0.3)
        # ---------- cylinder B: tight shale, load added as sediment piles up (s3)
        t_b = s[3] - 0.15
        wb = walls(BX)
        st.fade_in(wb, t_b, 0.5)
        tB0, tB1 = W(b, 3, "Bury sediment fast"), W(b, 3, "as load is added", 1.0)
        sigB = lambda t: ramp(t, tB0, tB1)
        pB = lambda t: 0.93 * sigB(t)
        dB = lambda t: 0.8 * max(sigB(t) - pB(t), 0.0)
        leakB = lambda t: 0.12 * sigB(t) if t > tB0 else 0.0
        st.procedural(t_b, b.end, 0.25, _cylinder_draw(BX, 0.025, dB, sigB, pB, "sediment", (t_b, t_b + 0.2), b.end + 1, leakB))
        st.procedural(t_b, b.end, 0.28, _gauge_draw(BX + 1.25, sigB, pB, t_b, b.end + 1))
        tb = st.text("tight shale", BX, YB3 - 0.42, 0.22, P.TEXT, 0.3, kind="bold")
        st.fade_in(tb, t_b + 0.3, 0.4)
        sh = pill(st, BX, 2.5, "tiny hole = tight shale: water can't keep up", P.PANEL2, P.TEXT, 0.19, 0.5)
        st.fade_in(sh, W(b, 3, "tight shale"), 0.4)
        st.fade_out(sh, s[4] - 0.3, 0.3)
        # ---------- "That is overpressure."
        t_ov = W(b, 4, "overpressure")
        ov = pill(st, BX + 0.2, 2.5, "OVERPRESSURE", P.BAD, "#ffffff", 0.28, 0.6)
        st.fade_in(ov, t_ov - 0.15, 0.3)
        st.ripple(BX + 1.25, YB3 + 2.4, t_ov - 0.1, t_ov + 2.5, P.PORE, period=0.8, r0=0.15, r1=0.8)
        # ---------- effective stress (s5): σ′ = σ − p, σ labelled overburden
        EX, EY = 5.55, -1.05
        card = st.rect(EX, EY, 4.0, 2.75, P.PANEL, 0.35)
        eq = st.text("σ′ = σ − p", EX, EY + 0.85, 0.5, P.TEXT, 0.4, kind="bold")
        st.fade_in([card, eq], s[5] - 0.1, 0.5)
        rows = [("σ′", "effective stress: carried by the grains", P.STEEL, W(b, 5, "effective stress")),
                ("σ", "overburden: weight of everything above", P.TEXT, W(b, 5, "weight of everything above")),
                ("p", "pore pressure", P.PORE, W(b, 5, "pore pressure"))]
        for k, (sym, txt, colr, t) in enumerate(rows):
            y = EY + 0.12 - k * 0.48
            o = [st.text(sym, EX - 1.75, y, 0.24, colr, 0.4, align="l", kind="bold"),
                 st.text(txt, EX - 1.35, y, 0.17, P.TEXT if k < 2 else P.PORE, 0.4, align="l")]
            st.fade_in(o, t - 0.1, 0.4)


# ============================================================================================ 1.04 stress around a borehole
def _kirsch_picture(cx, cy, a, R, sH=1.0, sh=0.5):
    """Hoop stress around a hole in a plate loaded by sH (horizontal) and sh (vertical) (Kirsch), as a warm colour field:
    hot where the hoop stress concentrates (top and bottom of the hole for a horizontal sH), none where it is lowest."""
    rec = skia.PictureRecorder()
    cv = rec.beginRecording(skia.Rect(cx - R - 1, cy - R - 1, cx + R + 1, cy + R + 1))
    rgb = hex_rgb(P.WARN)
    nr, nt = 16, 120
    for i in range(nr):
        r0 = a + (R - a) * (i / nr) ** 1.4
        r1 = a + (R - a) * ((i + 1) / nr) ** 1.4
        rm = (r0 + r1) / 2
        for j in range(nt):
            t0, t1 = 2 * math.pi * j / nt, 2 * math.pi * (j + 1) / nt
            tm = (t0 + t1) / 2
            sth = (sH + sh) / 2 * (1 + a * a / (rm * rm)) - (sH - sh) / 2 * (1 + 3 * a ** 4 / rm ** 4) * math.cos(2 * tm)
            v = max(0.0, min(1.0, (sth - 1.0) / 1.5))
            if v <= 0.01:
                continue
            pts = [(cx + r0 * math.cos(t0), cy + r0 * math.sin(t0)), (cx + r1 * math.cos(t0), cy + r1 * math.sin(t0)),
                   (cx + r1 * math.cos(t1), cy + r1 * math.sin(t1)), (cx + r0 * math.cos(t1), cy + r0 * math.sin(t1))]
            cv.drawPath(_path(pts, True), skia.Paint(Color=col(rgb, 0.85 * v ** 1.1), AntiAlias=True))
    return rec.finishRecordingAsPicture()


def beat_fracture(st, tl):
    b = tl["1.04"]
    s = b.sent
    PX, PY, PS, HR = -3.55, 0.45, 4.1, 0.5         # plate centre, size, hole radius
    GX, GY0, GY1 = 0.35, -1.45, 2.35                # mud-pressure gauge
    with st.span(b.start, b.end):
        # ---------- s0: the window gauge, upper wall highlighted
        zones = [(GY0, GY0 + 0.75, P.COLLAPSE, "collapse"), (GY0 + 0.75, GY1 - 0.95, P.SAFE, "window"), (GY1 - 0.95, GY1, P.FRAC, "fracture")]
        gz = []
        for y0, y1, colr, name in zones:
            gz.append(st.rect(GX, (y0 + y1) / 2, 0.36, y1 - y0 - 0.03, colr, 0.2, alpha=0.75, role="flat"))
            gz.append(st.text(name, GX + 0.35, (y0 + y1) / 2, 0.19, colr, 0.3, align="l", kind="bold"))
        gt = st.text("mud pressure", GX, GY1 + 0.32, 0.19, P.MUD, 0.3, kind="bold")
        st.fade_in(gz + [gt], s[0] - 0.1, 0.5)
        up = st.ring(GX, GY1 - 0.475, 0.62, 0.04, P.FRAC, 0.25, alpha=0.9)
        st.pop_in(up, W(b, 0, "upper wall"), 0.4)
        st.fade_out(up, s[1] + 1.5, 0.5)
        needle = [st.rect(GX, (GY0 + GY1) / 2, 0.62, 0.075, P.MUD, 0.4, role="shaft"),
                  st.poly([(GX - 0.42, (GY0 + GY1) / 2 + 0.13), (GX - 0.42, (GY0 + GY1) / 2 - 0.13), (GX - 0.24, (GY0 + GY1) / 2)], P.MUD, 0.41)]
        # ---------- s1: plate, far-field stress, concentration at the wall
        rock = st.rect(PX, PY, PS, PS, P.ROCK, 0.0)
        frame = st.rect(PX, PY, PS + 0.06, PS + 0.06, P.PANEL2, -0.01, role="flat")
        hole = st.circle(PX, PY, HR, P.BG, 0.15, role="hole")
        st.fade_in([frame, rock, hole], s[1] - 0.2, 0.5)
        far = []
        for sgn in (-1, 1):
            far += st.arrow(PX + sgn * (PS / 2 + 0.75), PY, PX + sgn * (PS / 2 + 0.08), PY, P.TEXT, 0.11, 0.3, 0.3)
            far += st.arrow(PX, PY + sgn * (PS / 2 + 0.45), PX, PY + sgn * (PS / 2 + 0.08), P.TEXT, 0.07, 0.22, 0.3)
        st.fade_in(far, W(b, 1, "concentrates stress") - 0.3, 0.4)
        fl = st.text("rock stress", PX - PS / 2 - 0.45, PY + 0.35, 0.16, P.MUTED, 0.3)
        st.fade_in(fl, W(b, 1, "concentrates stress"), 0.4)
        pic = _kirsch_picture(PX, PY, HR, 1.85)
        t_k0 = W(b, 1, "two to three") - 0.5

        def draw_field(c, t, look):
            a = env(t, t_k0, b.end, 0.8, 0.4) * (1.0 - 0.45 * ramp(t, s[3] - 0.3, s[3] + 0.4) * (1 - ramp(t, s[4] - 0.4, s[4])))
            if a <= 0.003:
                return
            c.saveLayerAlpha(skia.Rect(PX - 2.2, PY - 2.2, PX + 2.2, PY + 2.2), int(255 * a))
            c.drawPicture(pic)
            c.restore()
        st.procedural(t_k0, b.end, 0.05, draw_field)
        k23 = pill(st, PX, PY + HR + 0.95, "2–3× at the wall", P.PANEL2, P.WARN, 0.2, 0.5)
        st.fade_in(k23, W(b, 1, "two to three"), 0.4)
        st.fade_out(k23, s[2] + 0.2, 0.3)
        bh = st.text("borehole", PX, PY, 0.17, P.MUTED, 0.3)
        st.fade_in(bh, W(b, 1, "borehole") - 0.1, 0.4)
        st.fade_out(bh, s[2] - 0.2, 0.3)
        # ---------- s2: mud pressure pushes back (amber mud, white pressure arrows)
        mud = st.circle(PX, PY, HR, P.MUD, 0.16, role="flat")
        st.fade_in(mud, s[2] - 0.1, 0.4)
        push = []
        for i in range(8):
            ang = i * math.pi / 4 + math.pi / 8
            push += st.arrow(PX + 0.12 * math.cos(ang), PY + 0.12 * math.sin(ang), PX + (HR - 0.04) * math.cos(ang), PY + (HR - 0.04) * math.sin(ang),
                             P.TEXT, 0.045, 0.13, 0.35)
        st.fade_in(push, s[2] + 0.1, 0.35)
        st.fade_in(needle, s[2] - 0.1, 0.4)
        mp = pill(st, PX, PY - HR - 0.95, "mud pressure pushes back", P.PANEL2, P.MUD, 0.2, 0.5)
        st.fade_in(mp, s[2] + 0.2, 0.3)
        st.fade_out(mp, s[3] - 0.1, 0.3)
        # ---------- s3: too little -> breakouts top and bottom (where the hoop stress peaks), flakes fall in
        t_lo = W(b, 3, "Too little")
        st.move(needle, t_lo, t_lo + 0.9, dy=(GY0 + 0.37) - (GY0 + GY1) / 2)
        st.fade(push, t_lo, t_lo + 0.8, 1.0, 0.25)
        t_cr = W(b, 3, "crushes")
        ears = []
        for sgn in (1, -1):
            ear = st.poly([(PX - 0.36, PY + sgn * 0.35), (PX - 0.2, PY + sgn * 0.72), (PX, PY + sgn * 0.86), (PX + 0.2, PY + sgn * 0.72),
                           (PX + 0.36, PY + sgn * 0.35)], P.MUD, 0.155)
            ears.append(ear)
        st.pop_in(ears, t_cr, 0.6)
        eo = []
        for sgn in (1, -1):
            eo.append(st.line([(PX - 0.36, PY + sgn * 0.35), (PX - 0.2, PY + sgn * 0.72), (PX, PY + sgn * 0.86), (PX + 0.2, PY + sgn * 0.72),
                               (PX + 0.36, PY + sgn * 0.35)], P.COLLAPSE, 0.05, 0.3))
        st.draw_on(eo, t_cr, t_cr + 0.6)
        flakes = []
        for k, (fx, sgn) in enumerate([(-0.15, 1), (0.12, 1), (0.0, -1), (-0.1, -1), (0.18, -1), (0.05, 1)]):
            fy = PY + sgn * 0.62
            f_ = st.poly([(PX + fx - 0.07, fy - 0.05), (PX + fx + 0.07, fy - 0.03), (PX + fx, fy + 0.07)], "#8a7558", 0.36, role="flat")
            flakes.append(f_)
            st.fade_in(f_, t_cr + 0.2 + 0.08 * k, 0.2)
            st.move(f_, t_cr + 0.3 + 0.08 * k, t_cr + 1.4 + 0.08 * k, dy=-sgn * (0.42 + 0.05 * k), dx=0.05 * (k - 2.5))
        cl = pill(st, PX, PY - HR - 0.95, "too little: the wall crumbles in, collapse", P.PANEL2, P.COLLAPSE, 0.2, 0.5)
        st.fade_in(cl, W(b, 3, "collapse") - 0.2, 0.3)
        # ---------- s4: too much -> two fracture wings along the far-field stress
        t_hi = W(b, 4, "Too much")
        st.fade_out(ears + eo + flakes + cl, t_hi - 0.1, 0.4)
        st.move(needle, t_hi, t_hi + 1.0, dy=(GY1 - 0.4) - (GY0 + 0.37))
        st.fade(push, t_hi, t_hi + 0.8, 0.25, 1.0)
        for o in push:
            pass
        t_sp = W(b, 4, "splits")
        wings = []
        for sgn in (1, -1):
            wing_pts = [(PX + sgn * (HR - 0.02), PY + 0.07), (PX + sgn * 1.15, PY + 0.035), (PX + sgn * 1.75, PY), (PX + sgn * 1.15, PY - 0.035),
                        (PX + sgn * (HR - 0.02), PY - 0.07)]
            w_ = st.poly(wing_pts, P.MUD, 0.17, role="flat")
            st.pop_in(w_, t_sp, 0.5)
            wings.append(w_)
            e_ = st.line([(PX + sgn * (HR - 0.02), PY + 0.07), (PX + sgn * 1.15, PY + 0.035), (PX + sgn * 1.75, PY), (PX + sgn * 1.15, PY - 0.035),
                          (PX + sgn * (HR - 0.02), PY - 0.07)], P.FRAC, 0.04, 0.2)
            st.draw_on(e_, t_sp - 0.05, t_sp + 0.6)
            wings.append(e_)
        st.ripple(PX, PY, t_sp, t_sp + 1.6, P.FRAC, period=0.6, r0=0.5, r1=1.6)
        fgp = pill(st, PX, PY - HR - 0.95, "too much: the wall splits, fracture", P.PANEL2, P.FRAC, 0.2, 0.5)
        st.fade_in(fgp, t_sp + 0.1, 0.3)
        fg2 = pill(st, GX + 1.6, GY1 - 0.95, "this pressure, as a mud weight:\nthe fracture gradient", P.PANEL2, P.FRAC, 0.18, 0.5, align="l")
        fgl = leader(st, (GX + 0.2, GY1 - 0.4), (GX + 1.6, GY1 - 0.95), P.FRAC, 0.49, 0.7)
        st.fade_in(fg2 + [fgl], W(b, 4, "as a mud weight"), 0.4)
        # ---------- s5: for planning it is predicted
        pr = pill(st, GX + 1.6, GY1 - 1.75, "for planning: predicted", P.PANEL2, P.MUTED, 0.18, 0.5, align="l")
        st.fade_in(pr, s[5], 0.4)
        # ---------- s6: leak-off test, one depth, after casing is set
        t_lot = W(b, 6, "leak-off test")
        lc = Chart(st, 3.75, -2.75, 3.4, 2.5, (0, 6), (0, 8))
        fr = lc.frame(xticks=[], yticks=[], xlabel="volume pumped", ylabel="pressure", grid=False)
        st.fade_in(fr, t_lot - 0.3, 0.4)
        lt = pill(st, 5.45, 0.25, "leak-off test: one depth, after casing is set", P.PANEL2, P.TEXT, 0.18, 0.5)
        st.fade_in(lt, t_lot, 0.4)
        xs = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.3, 3.6, 4.0, 4.5, 5.0, 5.5]
        ys = [0, 0.9, 1.8, 2.7, 3.6, 4.5, 5.4, 5.93, 6.35, 6.7, 6.95, 7.1, 7.18]
        ln = lc.curve(xs, ys, P.MUD, 0.06, 0.4)
        t_pump = W(b, 6, "pumping")
        st.draw_on(ln, t_pump, W(b, 6, "takes fluid", 1.0) + 0.3)
        ext = st.dashed(lc.pt(3.0, 5.4), lc.pt(4.1, 7.38), P.TEXT, 0.025, 0.08, 0.06, 0.39, alpha=0.7)
        st.fade_in(ext, W(b, 6, "takes fluid"), 0.4)
        dot = lc.dot(3.2, 5.76, 0.09, P.FRAC, 0.45)
        st.pop_in(dot, W(b, 6, "takes fluid"), 0.4)
        lpl = st.text("leak-off: the rock\nstarts taking fluid", lc.X(3.2) + 0.25, lc.Y(5.76) - 0.62, 0.16, P.FRAC, 0.45, align="l", kind="bold")
        st.fade_in(lpl, W(b, 6, "takes fluid") + 0.2, 0.4)


# ============================================================================================ the window chart (1.05, 1.06, 1.08)
CH_X, CH_Y, CH_W, CH_H = -5.0, -2.75, 6.2, 6.2
XR = (0.9, 2.0)
ZS = [M.WATER_DEPTH + 25.0 * i for i in range(int((M.TD - M.WATER_DEPTH) / 25) + 1)]
COL_X, KIN = 2.45, 0.04          # casing column centre; world units per inch of OD


def _chart(st):
    return Chart(st, CH_X, CH_Y, CH_W, CH_H, XR, (0.0, M.TD), invert_y=True)


def _req(z, mw):
    """'Fracture, less margin and kick allowance' for a section drilled with mud weight mw (sg)."""
    return M.fg(z) - (M.required_shoe_emw(z, mw) - mw)


def _chart_frame(st, c):
    fr = c.frame(xticks=[1.0, 1.2, 1.4, 1.6, 1.8, 2.0], yticks=[0, 1000, 2000, 3000, 4000],
                 xlabel="equivalent mud weight (sg)", ylabel="depth below sea level (m)", fx="{:.1f}")
    sea = st.rect(c.x + c.w / 2, (c.Y(0) + c.Y(M.WATER_DEPTH)) / 2, c.w, c.Y(0) - c.Y(M.WATER_DEPTH), P.SEA, 0.01, alpha=0.55)
    sb = st.rect(c.x + c.w / 2, c.Y(M.WATER_DEPTH), c.w, 0.03, P.SEABED, 0.12)
    sbl = st.text("seabed · 300 m", c.X(2.0) - 0.1, (c.Y(0) + c.Y(M.WATER_DEPTH)) / 2, 0.17, P.TEXT, 0.12, align="r")
    return fr + [sea, sb, sbl]


def _chart_curves(st, c):
    pp = c.curve([M.pp(z) for z in ZS], ZS, P.PORE, 0.07, 0.3)
    fg = c.curve([M.fg(z) for z in ZS], ZS, P.FRAC, 0.07, 0.3)
    zl = 2800.0
    ppl = st.text("pore\npressure", c.X(M.pp(zl)) - 0.15, c.Y(zl) + 0.05, 0.2, P.PORE, 0.3, align="r", kind="bold")
    zf = 3800.0
    fgl = st.text("fracture", c.X(M.fg(zf)) + 0.15, c.Y(zf), 0.2, P.FRAC, 0.3, align="l", kind="bold")
    return pp, fg, ppl, fgl


def _chart_band(st, c):
    band = c.band([(M.pp(z), z) for z in ZS], [(M.fg(z), z) for z in ZS], P.SAFE, 0.1, 0.3)
    mL = c.band([(M.pp(z), z) for z in ZS], [(M.pp(z) + M.TRIP_MARGIN, z) for z in ZS], P.PORE, 0.11, 0.22)
    mR = c.band([(M.fg(z) - M.FRAC_MARGIN, z) for z in ZS], [(M.fg(z), z) for z in ZS], P.FRAC, 0.11, 0.26)
    return band, mL, mR


def _margin_lines(st, c, t0, t1, t_in, t_draw=None):
    """Thin dashed offsets: pore + trip margin, fracture − margin (procedural, real dashes)."""
    ptsL = [c.pt(M.pp(z) + M.TRIP_MARGIN, z) for z in ZS]
    ptsR = [c.pt(M.fg(z) - M.FRAC_MARGIN, z) for z in ZS]

    def draw(cv, t, look):
        a = env(t, t_in, t1 + 10, 0.3, 0.0) if t < t1 else 0.0
        f = 1.0 if t_draw is None else ramp(t, t_draw[0], t_draw[1])
        stroke(cv, look, ptsL, P.PORE, 0.85 * a, 0.022, dash=(0.09, 0.06), glow=False, frac=f, cap="butt")
        stroke(cv, look, ptsR, P.FRAC, 0.85 * a, 0.022, dash=(0.09, 0.06), glow=False, frac=f, cap="butt")
    st.procedural(t0, t1, 0.26, draw)


def _chart_static(st, c, t0, t1):
    """The finished window chart, visible for the whole span (used by 1.06 and 1.08: same place for continuity)."""
    objs = _chart_frame(st, c)
    pp, fg, ppl, fgl = _chart_curves(st, c)
    band, mL, mR = _chart_band(st, c)
    _margin_lines(st, c, t0, t1, t0 - 1.0)
    return objs + [pp, fg, ppl, fgl, band, mL, mR]


def _bracket(st, c, z, t, label_side="r"):
    xa, xb, y = c.X(M.pp(z)), c.X(M.fg(z)), c.Y(z)
    o = st.arrow((xa + xb) / 2, y, xb - 0.02, y, P.TEXT, 0.035, 0.13, 0.5) + st.arrow((xa + xb) / 2, y, xa + 0.02, y, P.TEXT, 0.035, 0.13, 0.5)
    lab = f"{M.fg(z) - M.pp(z):.2f} sg"
    if label_side == "r":
        p_ = pill(st, xb + 0.2, y, lab, P.PANEL2, P.SAFE, 0.2, 0.55, align="l")
    else:
        p_ = pill(st, (xa + xb) / 2, y + 0.3, lab, P.PANEL2, P.SAFE, 0.2, 0.55)
    st.fade_in(o, t, 0.3)
    st.fade_in(p_, t + 0.15, 0.3)
    return o + p_


def beat_window(st, tl):
    b = tl["1.05"]
    s = b.sent
    c = _chart(st)
    with st.span(b.start, b.end):
        fr = _chart_frame(st, c)
        st.fade_in(fr, b.start + 0.15, 0.5)
        pp, fg, ppl, fgl = _chart_curves(st, c)
        band, mL, mR = _chart_band(st, c)
        # s0: EMW explained on the right
        e0 = st.text("EMW = P ÷ (0.0981 × depth)", 4.7, 1.55, 0.24, P.TEXT, 0.4, kind="mono")
        e1 = st.text("the mud weight that would\ngive that pressure", 4.7, 0.85, 0.2, P.MUTED, 0.4)
        st.fade_in(e0, W(b, 0, "equivalent mud weight"), 0.4)
        st.fade_in(e1, W(b, 0, "the mud weight that"), 0.4)
        st.fade_out([e0, e1], s[2] - 0.2, 0.4)
        # s1: pore pressure on the left, fracture on the right (draw from the seabed down)
        t_pp, t_fg = W(b, 1, "Pore pressure"), W(b, 1, "fracture")
        st.draw_on(pp, t_pp - 0.1, t_pp + 1.6, "BEZIER")
        st.fade_in(ppl, t_pp + 1.0, 0.3)
        st.draw_on(fg, t_fg - 0.1, t_fg + 1.6, "BEZIER")
        st.fade_in(fgl, t_fg + 1.0, 0.3)
        # s2: the mud stays between them, with a margin each side
        t_bw = W(b, 2, "between them")
        st.fade_in(band, t_bw - 0.3, 0.6)
        t_mg = W(b, 2, "margin")
        st.fade_in([mL, mR], t_mg, 0.5)
        _margin_lines(st, c, t_mg, b.end, t_mg, (t_mg, t_mg + 1.0))
        z_m = 1500.0
        mpl = pill(st, c.X(M.pp(z_m) + M.TRIP_MARGIN / 2) + 0.05, c.Y(z_m) + 0.55, f"+{M.TRIP_MARGIN:.2f} sg margin", P.PANEL2, P.PORE, 0.18, 0.5, align="l")
        mpr = pill(st, c.X(M.fg(z_m)) + 0.25, c.Y(z_m) + 0.55, f"−{M.FRAC_MARGIN:.2f} sg margin", P.PANEL2, P.FRAC, 0.18, 0.5, align="l")
        lL = leader(st, (c.X(M.pp(z_m) + M.TRIP_MARGIN / 2), c.Y(z_m)), (c.X(M.pp(z_m) + M.TRIP_MARGIN / 2) + 0.1, c.Y(z_m) + 0.38), P.PORE, 0.49)
        lR = leader(st, (c.X(M.fg(z_m) - M.FRAC_MARGIN / 2), c.Y(z_m)), (c.X(M.fg(z_m)) + 0.3, c.Y(z_m) + 0.38), P.FRAC, 0.49)
        st.fade_in(mpl + [lL], t_mg + 0.4, 0.4)
        st.fade_in(mpr + [lR], t_mg + 0.6, 0.4)
        st.fade_out(mpl + mpr + [lL, lR], s[3] - 0.2, 0.4)
        # a mud-weight marker that lives inside the window
        zmud = 2000.0
        ymud = c.Y(zmud)
        mud = st.circle(c.X(1.35), ymud, 0.12, P.MUD, 0.45)
        st.pop_in(mud, t_bw, 0.4)
        st.move(mud, t_bw + 0.3, t_bw + 1.3, to=(c.X(M.pp(zmud) + M.TRIP_MARGIN) + 0.12, ymud))
        st.move(mud, t_bw + 1.3, t_bw + 2.6, to=(c.X(M.fg(zmud) - M.FRAC_MARGIN) - 0.12, ymud))
        st.move(mud, t_bw + 2.6, t_bw + 3.6, to=(c.X(1.35), ymud))
        ml = st.text("mud", c.X(1.35), ymud + 0.3, 0.18, P.MUD, 0.45, kind="bold")
        st.fade_in(ml, t_bw + 0.1, 0.3)
        st.move(ml, t_bw + 0.3, t_bw + 1.3, to=(c.X(M.pp(zmud) + M.TRIP_MARGIN) + 0.12, ymud + 0.3))
        st.move(ml, t_bw + 1.3, t_bw + 2.6, to=(c.X(M.fg(zmud) - M.FRAC_MARGIN) - 0.12, ymud + 0.3))
        st.move(ml, t_bw + 2.6, t_bw + 3.6, to=(c.X(1.35), ymud + 0.3))
        st.fade_out([mud, ml], s[3] - 0.2, 0.4)
        # s3: three brackets keyed to the words
        _bracket(st, c, 310.0, W(b, 3, "tight near the seabed"), "r")
        _bracket(st, c, 2400.0, W(b, 3, "widest"), "c")
        _bracket(st, c, 3900.0, W(b, 3, "pinches in"), "r")
        # ... because pore pressure climbs faster than the stress needed to open a fracture (2,400 -> 3,900 m)
        t_cl = W(b, 3, "climbs faster")
        za, zb = 2400.0, 3900.0
        seg_pp = st.line([c.pt(M.pp(z), z) for z in ZS if za <= z <= zb], P.PORE, 0.14, 0.31, alpha=0.6)
        seg_fg = st.line([c.pt(M.fg(z), z) for z in ZS if za <= z <= zb], P.FRAC, 0.14, 0.31, alpha=0.6)
        st.draw_on(seg_pp, t_cl - 0.3, t_cl + 1.0)
        st.draw_on(seg_fg, W(b, 3, "stress needed"), W(b, 3, "stress needed") + 1.0)
        rx = 4.7
        hdr = st.text("from 2,400 m to 3,900 m", rx, -0.35, 0.2, P.MUTED, 0.4, kind="bold")
        st.fade_in(hdr, t_cl - 0.4, 0.4)
        st.counter(rx - 0.95, -0.95, t_cl, t_cl + 1.2, 0.0, M.pp(zb) - M.pp(za), fmt="+{:.2f} sg", size=0.3, color=P.PORE, kind="mono")
        st.counter(rx + 0.95, -0.95, W(b, 3, "stress needed"), W(b, 3, "stress needed") + 1.2, 0.0, M.fg(zb) - M.fg(za),
                   fmt="+{:.2f} sg", size=0.3, color=P.FRAC, kind="mono")
        cl1 = st.text("pore pressure", rx - 0.95, -1.4, 0.18, P.PORE, 0.4, kind="bold")
        cl2 = st.text("fracture", rx + 0.95, -1.4, 0.18, P.FRAC, 0.4, kind="bold")
        st.fade_in(cl1, t_cl, 0.4)
        st.fade_in(cl2, W(b, 3, "stress needed"), 0.4)
        # s4: simplification
        sim = pill(st, 4.7, -2.55, "simplified: lower limit drawn as pore pressure only", P.PANEL2, P.SIM_BADGE, 0.19, 0.5)
        st.fade_in(sim, s[4] - 0.1, 0.4)


# ---------------------------------------------------------------------------------------------- casing column (1.06, 1.08)
def _column_back(st, c):
    w = 1.5
    zt, zs, zb = c.Y(0), c.Y(M.WATER_DEPTH), c.Y(M.TD)
    return [st.rect(COL_X, (zt + zs) / 2, w, zt - zs, P.SEA, 0.02, alpha=0.8),
            st.rect(COL_X, (zs + zb) / 2, w, zs - zb, P.ROCK, 0.02),
            st.rect(COL_X, zs, w, 0.03, P.SEABED, 0.03),
            st.text("casing strings", COL_X, zt + 0.28, 0.17, P.MUTED, 0.1, kind="bold")]


def _string(st, c, name, t0=None, t1=None):
    """A casing string (width ∝ OD) hanging from the seabed to its shoe; grows down between t0 and t1 if given."""
    s_ = PROG[name]
    w = s_.od_in * KIN
    top = c.Y(M.WATER_DEPTH)
    L = top - c.Y(s_.shoe)
    z = 0.1 + 0.02 * (30 - s_.od_in)
    bar = st.rect(COL_X, top, w, L if t0 is None else 0.0001, STRING_COLORS[name], z, anchor="t")
    ys = c.Y(s_.shoe)
    shoe = [st.poly([(COL_X - w / 2 - 0.1, ys), (COL_X - w / 2, ys), (COL_X - w / 2, ys + 0.13)], P.TEXT, z + 0.05, role="flat"),
            st.poly([(COL_X + w / 2 + 0.1, ys), (COL_X + w / 2, ys), (COL_X + w / 2, ys + 0.13)], P.TEXT, z + 0.05, role="flat")]
    if t0 is not None:
        st.fade_in(bar, t0, 0.15)
        st.scale_to(bar, t0, t1, sy=L)
        st.fade_in(shoe, t1 - 0.1, 0.25)
    return [bar] + shoe


def _shoe_label(st, c, name, t=None, extra=""):
    s_ = PROG[name]
    o = st.text(f"{SIZE[name]} · {s_.shoe:,.0f} m{extra}", COL_X + 0.85, c.Y(s_.shoe), 0.18, P.TEXT, 0.5, align="l", kind="bold")
    if t is not None:
        st.fade_in(o, t, 0.35)
    return o


def _req_curve(st, c, t0, t1, mw_fn, draw=None, alpha_fn=None, zmin=2350.0):
    """Yellow dashed 'fracture, less margin and kick allowance' curve; mw_fn(t) lets it morph when the mud changes.
    Drawn from TD upward (draw=(ta, tb) reveals it)."""
    def draw_fn(cv, t, look):
        a = alpha_fn(t) if alpha_fn else 1.0
        if a <= 0.003:
            return
        mw = mw_fn(t)
        zs = [z for z in reversed(ZS) if z >= zmin(mw) if callable(zmin)] if callable(zmin) else [z for z in reversed(ZS) if z >= zmin]
        pts = [c.pt(_req(z, mw), z) for z in zs if _req(z, mw) >= XR[0]]
        f = 1.0 if draw is None else ramp(t, draw[0], draw[1])
        stroke(cv, look, pts, P.WARN, a, 0.045, dash=(0.12, 0.07), glow=True, frac=f, tip=f < 0.999, cap="butt")
    st.procedural(t0, t1, 0.33, draw_fn)


def beat_bottom_up(st, tl):
    """1.06: the deepest shoe, designed from the bottom up."""
    b = tl["1.06"]
    s = b.sent
    c = _chart(st)
    d1 = DESIGN[0]
    mw1, z1 = d1["mw"], d1["shoe_calc"]          # 1.62 sg, 3,370 m
    z_pp = max(range(int(M.WATER_DEPTH), int(M.TD) + 1, 10), key=lambda z: M.pp(z))   # 3,900 m
    pp_max = M.pp(z_pp)                          # 1.55 sg
    z_nk = M.WATER_DEPTH
    for z in range(int(M.TD), int(M.WATER_DEPTH), -1):        # where plain fracture − margin would meet the 1.62 line
        if M.fg(z) - M.FRAC_MARGIN < mw1:
            z_nk = z + 1
            break
    with st.span(b.start, b.end):
        _chart_static(st, c, b.start, b.end)
        # ---------- s0: the question again; a slice sweeps down the window (cold-open callback)
        q = st.text(wrap_to("How do you stay inside the window for four kilometres?", 0.36, 4.5, "bold"), 4.9, 1.5, 0.36, P.TEXT, 0.5, kind="bold")
        st.fade_in(q, s[0] + 0.2, 0.5)
        t_sl0, t_sl1 = s[0] + 0.5, s[1] - 0.2

        def draw_slice(cv, t, look):
            a = env(t, t_sl0, t_sl1 + 0.3, 0.3, 0.3)
            if a <= 0:
                return
            z = M.WATER_DEPTH + 40 + (M.TD - 60 - M.WATER_DEPTH) * ramp(t, t_sl0, t_sl1)
            x0, x1, y = c.X(M.pp(z)), c.X(M.fg(z)), c.Y(z)
            stroke(cv, look, [(x0, y), (x1, y)], P.SAFE, a, 0.09, glow=True)
            look.draw_ring(cv, x0, y, 0.07, 0.03, P.PORE, a)
            look.draw_ring(cv, x1, y, 0.07, 0.03, P.FRAC, a)
            text(cv, look, f"{z:,.0f} m", x0 - 0.18, y, 0.18, P.TEXT, a, "r", "mono")
        st.procedural(t_sl0, t_sl1 + 0.3, 0.5, draw_slice)
        # ---------- s1: "You don't, not all at once": one mud weight top to bottom cracks the shallow rock
        t_no = W(b, 1, "You don't")
        one = st.line([c.pt(mw1, M.WATER_DEPTH), c.pt(mw1, M.TD)], P.MUD, 0.07, 0.4)
        st.draw_on(one, t_no - 0.2, t_no + 0.6, "BEZIER")
        z_c = 2000.0                                 # fg = 1.62 sg here: above it, 1.62 sg mud is past fracture
        bad = st.line([c.pt(mw1, M.WATER_DEPTH), c.pt(mw1, z_c)], P.BAD, 0.08, 0.41)
        st.fade_in(bad, t_no + 0.5, 0.3)
        st.ripple(c.X(mw1), c.Y(1100), t_no + 0.5, s[2], P.BAD, period=0.6, r0=0.1, r1=0.7)
        ans = st.text("You don't. Not all at once.", 4.9, 0.2, 0.3, P.WARN, 0.5, kind="bold")
        st.fade_in(ans, t_no, 0.4)
        st.fade_out([q, ans, one, bad], s[2] - 0.1, 0.4)
        # ---------- s2: one section at a time, each locked behind casing, cemented in place (a mini demo in the column)
        back = _column_back(st, c)
        st.fade_in(back, s[2], 0.5)
        ts = W(b, 2, "one section at a time")
        hw, cw = PROG[N20].hole_in * KIN, PROG[N20].od_in * KIN
        ztop, zsh = c.Y(M.WATER_DEPTH), c.Y(PROG[N20].shoe)
        with st.span(s[2], s[3] + 0.6):
            holeo = st.rect(COL_X, ztop, hw, 0.0001, P.BG, 0.08, anchor="t")
            st.fade_in(holeo, ts - 0.2, 0.1)
            st.scale_to(holeo, ts - 0.2, ts + 1.3, sy=ztop - zsh)
            tp = W(b, 2, "steel pipe") - 0.2
            wl = st.rect(COL_X - cw / 2 + 0.03, ztop, 0.06, 0.0001, P.STEEL, 0.2, anchor="t")
            wr = st.rect(COL_X + cw / 2 - 0.03, ztop, 0.06, 0.0001, P.STEEL, 0.2, anchor="t")
            st.fade_in([wl, wr], tp, 0.1)
            st.scale_to([wl, wr], tp, tp + 1.2, sy=ztop - zsh + 0.02)
            tcm = W(b, 2, "cemented") - 0.1
            gap = (hw - cw) / 2
            cem = [st.rect(COL_X - cw / 2 - gap / 2, zsh, gap, 0.0001, P.CEMENT, 0.15, anchor="b"),
                   st.rect(COL_X + cw / 2 + gap / 2, zsh, gap, 0.0001, P.CEMENT, 0.15, anchor="b")]
            st.fade_in(cem, tcm + 0.3, 0.1)
            st.scale_to(cem, tcm + 0.3, tcm + 1.8, sy=zsh - ztop)
            # cement pumped down the inside of the casing, out of the shoe, up the annulus
            st.flow([(COL_X, ztop - 0.05), (COL_X, zsh + 0.06), (COL_X - cw / 2 - gap / 2, zsh + 0.06), (COL_X - cw / 2 - gap / 2, ztop - 0.05)],
                    tcm, tcm + 2.0, P.CEMENT, n=12, speed=1.6, r=0.035, z=0.3, glow=False)
            st.flow([(COL_X, ztop - 0.05), (COL_X, zsh + 0.06), (COL_X + cw / 2 + gap / 2, zsh + 0.06), (COL_X + cw / 2 + gap / 2, ztop - 0.05)],
                    tcm, tcm + 2.0, P.CEMENT, n=12, speed=1.6, r=0.035, z=0.3, glow=False)
            p1 = pill(st, COL_X + 1.05, 1.7, "one section", P.PANEL2, P.TEXT, 0.18, 0.5, align="l")
            p2 = pill(st, COL_X + 1.05, 1.15, "casing: steel pipe", P.PANEL2, P.STEEL, 0.18, 0.5, align="l")
            p3 = pill(st, COL_X + 1.05, 0.6, "cement", P.PANEL2, P.CEMENT, 0.18, 0.5, align="l")
            st.fade_in(p1, ts, 0.3)
            st.fade_in(p2, tp + 0.4, 0.3)
            st.fade_in(p3, tcm + 0.4, 0.3)
            st.fade_out([holeo, wl, wr] + cem + p1 + p2 + p3, s[3] - 0.1, 0.5)
        # ---------- s3: we design from the bottom up
        t_bu = W(b, 3, "bottom up")
        bu = st.arrow(COL_X + 1.0, c.Y(4150), COL_X + 1.0, c.Y(2700), P.TEXT, 0.07, 0.26, 0.5)
        bul = st.text("design:\nbottom up", COL_X + 1.2, c.Y(3700), 0.22, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(bu + [bul], t_bu - 0.4, 0.4)
        st.fade_out(bu + [bul], s[6] - 0.2, 0.4)
        # ---------- s4: the deepest section needs 1.62 sg = 1.55 sg pore + margin
        t_162 = W(b, 4, "one point six two")
        td = st.circle(c.X(mw1), c.Y(M.TD), 0.13, P.MUD, 0.5)
        st.pop_in(td, t_162 - 0.1, 0.4)
        tdl = st.text(f"{mw1:.2f} sg", c.X(mw1) + 0.2, c.Y(M.TD) + 0.22, 0.2, P.MUD, 0.5, align="l", kind="bold")
        st.fade_in(tdl, t_162, 0.3)
        t_hp = W(b, 4, "highest pore pressure")
        ring = st.ring(c.X(pp_max), c.Y(z_pp), 0.16, 0.04, P.PORE, 0.5)
        st.pop_in(ring, t_hp, 0.4)
        ppv = st.text(f"{pp_max:.2f}", c.X(pp_max) - 0.22, c.Y(z_pp) + 0.2, 0.18, P.PORE, 0.5, align="r", kind="bold")
        st.fade_in(ppv, W(b, 4, "one point five five"), 0.3)
        t_mg = W(b, 4, "plus a margin")
        mar = st.arrow(c.X(pp_max) + 0.1, c.Y(z_pp), c.X(mw1) - 0.04, c.Y(z_pp), P.TEXT, 0.035, 0.12, 0.5)
        st.fade_in(mar, t_mg - 0.1, 0.3)
        dp = pill(st, -3.25, c.Y(3950), "deepest section:\n1.55 sg pore + margin", P.PANEL2, P.MUD, 0.19, 0.5)
        dl = leader(st, (-2.05, c.Y(3950) - 0.05), (c.X(mw1) - 0.14, c.Y(M.TD) + 0.06), P.MUD, 0.49, 0.6)
        st.fade_in(dp + [dl], t_mg + 0.3, 0.4)
        # ---------- s5: draw that line up until it meets fracture, less a margin and room for a gas kick
        t_up0 = W(b, 5, "Draw that line up")
        t_meet = W(b, 5, "meets", 1.0)
        t_up1 = max(t_meet + 0.5, t_up0 + 2.8)
        rise = st.line([c.pt(mw1, M.TD), c.pt(mw1, z1)], P.MUD, 0.08, 0.45)
        st.draw_on(rise, t_up0, t_up1, "BEZIER")
        t_y0 = W(b, 5, "fracture curve") - 0.2
        _req_curve(st, c, t_y0, b.end, lambda t: mw1, draw=(t_y0, t_y0 + 2.2), alpha_fn=lambda t: env(t, t_y0, b.end + 1, 0.1, 0))
        t_gk = W(b, 5, "gas kick")
        yl = pill(st, c.X(1.30), c.Y(2120), "fracture, less margin\nand kick allowance", P.PANEL2, P.WARN, 0.19, 0.5)
        yll = leader(st, (c.X(1.30) + 0.6, c.Y(2120) - 0.32), (c.X(_req(2380, mw1)) - 0.04, c.Y(2380) + 0.04), P.WARN, 0.49, 0.7)
        st.fade_in(yl + [yll], t_gk - 0.5, 0.4)
        meet = st.ring(c.X(mw1), c.Y(z1), 0.15, 0.045, P.TEXT, 0.55)
        st.pop_in(meet, t_up1 - 0.1, 0.4)
        # ---------- s6: above that point no safe shut-in of a kick -> casing must end below it
        t_ab = W(b, 6, "Above that point")
        red = st.rect(c.X(mw1), c.Y(z1), 0.2, 0.0001, P.BAD, 0.36, alpha=0.5, anchor="b", role="flat")
        st.fade_in(red, t_ab, 0.1)
        st.scale_to(red, t_ab, t_ab + 1.2, sy=c.Y(M.WATER_DEPTH) - c.Y(z1))
        rp = pill(st, c.X(mw1), c.Y(720), "shoe too weak for\na kick above here", P.BAD, "#ffffff", 0.19, 0.55)
        st.fade_in(rp, W(b, 6, "could not safely shut in") - 0.2, 0.4)
        tick = st.rect(c.X(mw1), c.Y(z_nk), 0.42, 0.03, P.TEXT, 0.4, alpha=0.6)
        tkl = st.text("fracture − margin\nalone would allow this", c.X(1.96), c.Y(z_nk) - 0.02, 0.15, P.MUTED, 0.4, align="r")
        tkd = leader(st, (c.X(mw1) + 0.22, c.Y(z_nk)), (c.X(1.96) - st.measure("alone would allow this", 0.15) - 0.05, c.Y(z_nk) - 0.02), P.MUTED, 0.39, 0.6)
        st.fade_in([tick, tkl, tkd], W(b, 6, "closing the well") - 0.2, 0.5)
        t_cs = W(b, 6, "casing must end")
        shl = st.dashed(c.pt(XR[0], z1), c.pt(mw1 - 0.03, z1), P.TEXT, 0.025, 0.08, 0.06, 0.4, alpha=0.8)
        st.fade_in(shl, t_cs - 0.2, 0.3)
        sp_ = pill(st, -3.25, c.Y(z1) + 0.32, f"shoe ≥ {z1:,.0f} m", P.PANEL2, P.TEXT, 0.19, 0.55)
        st.fade_in(sp_, t_cs, 0.4)
        s9 = _string(st, c, N9, t_cs, t_cs + 1.8)
        lab9 = st.text(f"{SIZE[N9]} casing", COL_X + 0.85, 0.75, 0.2, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(lab9, t_cs + 1.0, 0.4)
        # ---------- s7: its bottom end is the casing shoe
        t_sh = W(b, 7, "casing shoe")
        st.ripple(COL_X, c.Y(PROG[N9].shoe), t_sh - 0.3, b.end, P.TEXT, period=1.0, r0=0.15, r1=0.9)
        shp = pill(st, COL_X + 0.85, c.Y(PROG[N9].shoe), f"shoe · {PROG[N9].shoe:,.0f} m", P.PANEL2, P.TEXT, 0.19, 0.55, align="l")
        st.fade_in(shp, t_sh - 0.3, 0.4)
        nt = st.text("set a little deeper\nthan the 3,370 m minimum", COL_X + 0.9, c.Y(PROG[N9].shoe) - 0.6, 0.15, P.MUTED, 0.55, align="l")
        st.fade_in(nt, t_sh, 0.4)
    return t_cs + 1.8


# ============================================================================================ 1.07 shallow hazards + site survey
SB7, SURF7 = 1.15, 2.95


def beat_hazards(st, tl):
    b = tl["1.07"]
    s = b.sent
    X0, X1 = -6.3, 7.85
    cx = (X0 + X1) / 2
    GXC, GYC = -1.55, -0.85               # gas pocket crest
    with st.span(b.start, b.end):
        sea = st.rect(cx, (SB7 + SURF7) / 2, X1 - X0, SURF7 - SB7, P.SEA, 0.0)
        surf = st.line([(X0, SURF7), (X1, SURF7)], P.PORE, 0.03, 0.05, alpha=0.75)
        till = st.rect(cx, (SB7 + 0.25) / 2, X1 - X0, SB7 - 0.25, P.ROCK2, 0.0)
        rock = st.rect(cx, (0.25 - 3.45) / 2, X1 - X0, 0.25 + 3.45, P.ROCK, 0.0)
        # domed shale cap with the gas lens pressed up beneath it
        cap_top = [(x, GYC + 0.62 - 0.55 * ((x - GXC) / 2.6) ** 2) for x in [GXC - 2.6 + 0.26 * i for i in range(21)]]
        cap = st.poly(cap_top + [(x, y - 0.28) for x, y in reversed(cap_top)], P.SHALE, 0.02)
        gas_top = [(x, GYC + 0.34 - 0.55 * ((x - GXC) / 2.6) ** 2) for x in [GXC - 1.15 + 0.115 * i for i in range(21)]]
        gas_pts = gas_top + [(GXC + 1.15, gas_top[-1][1]), (GXC - 1.15, gas_top[0][1])]
        gas = st.poly(gas_top + [(GXC + 1.05, GYC - 0.05), (GXC, GYC - 0.12), (GXC - 1.05, GYC - 0.05)], P.GAS, 0.03, alpha=0.9)
        seabed = st.rect(cx, SB7, X1 - X0, 0.04, P.SEABED, 0.05)
        st.fade_in([sea, surf, till, rock, cap, seabed], b.start + 0.1, 0.5)
        lt = st.text("till: left by glaciers", X1 - 0.15, 0.45, 0.16, P.MUTED, 0.06, align="r")
        st.fade_in(lt, s[2], 0.4)
        h0 = pill(st, -3.2, 3.45, "near the top: pressure is not the only enemy", P.PANEL2, P.TEXT, 0.2, 0.5)
        st.fade_in(h0, s[0] + 0.2, 0.4)
        st.fade_out(h0, s[1] - 0.2, 0.3)
        # ---------- s1: shallow gas, a few hundred metres below the seabed, reached before any BOP
        t_g = W(b, 1, "Shallow gas")
        st.pop_in(gas, t_g, 0.5)
        gl = pill(st, GXC + 2.0, GYC - 0.75, "shallow gas", P.PANEL2, P.GAS, 0.22, 0.5, align="l")
        st.fade_in(gl, t_g + 0.2, 0.4)
        t_fh = W(b, 1, "a few hundred metres")
        bx = -4.6
        br = st.arrow(bx, SB7 - 0.05, bx, GYC + 0.4, P.TEXT, 0.035, 0.14, 0.5) + st.arrow(bx, GYC + 0.4, bx, SB7 - 0.05, P.TEXT, 0.035, 0.14, 0.5)
        brl = st.text("a few hundred m\nbelow the seabed", bx - 0.12, (SB7 + GYC + 0.4) / 2, 0.16, P.TEXT, 0.5, align="r", kind="bold")
        st.fade_in(br + [brl], t_fh, 0.4)
        # the top-hole well: drilled from the seabed with no BOP on it yet
        t_dr = W(b, 1, "reached before")
        crest_y = GYC + 0.34
        hole = st.rect(GXC, SB7, 0.22, 0.0001, P.BG, 0.1, anchor="t", role="hole")
        st.fade_in(hole, t_dr - 0.3, 0.1)
        st.scale_to(hole, t_dr - 0.3, t_dr + 1.2, sy=SB7 - crest_y)
        whd = [st.rect(GXC, SB7 + 0.1, 0.5, 0.2, P.STEEL_DK, 0.3), st.rect(GXC, SB7 + 0.25, 0.3, 0.12, P.STEEL, 0.3)]
        st.fade_in(whd, t_dr - 0.4, 0.3)
        t_bop = W(b, 1, "blowout preventer")
        ghost = []
        gx0, gx1, gy0, gy1 = GXC - 0.45, GXC + 0.45, SB7 + 0.32, SB7 + 1.25
        for p0, p1 in (((gx0, gy0), (gx1, gy0)), ((gx1, gy0), (gx1, gy1)), ((gx1, gy1), (gx0, gy1)), ((gx0, gy1), (gx0, gy0))):
            ghost += st.dashed(p0, p1, P.MUTED, 0.03, 0.1, 0.07, 0.3, alpha=0.9)
        nb = pill(st, GXC + 0.65, SB7 + 0.8, "no BOP yet", P.PANEL2, P.MUTED, 0.19, 0.5, align="l")
        st.fade_in(ghost + nb, t_bop, 0.4)
        t_flow = W(b, 1, "so a gas flow")
        st.flow([(GXC, crest_y + 0.02), (GXC, SB7 + 0.2)], t_flow - 0.2, s[2] + 0.4, P.GAS, n=10, speed=1.2, r=0.04, z=0.35)
        st.flow([(GXC, SB7 + 0.3), (GXC + 0.15, SB7 + 0.9), (GXC - 0.1, SB7 + 1.4), (GXC + 0.05, SURF7 - 0.05)], t_flow, s[2] + 0.4,
                P.GAS, n=10, speed=0.9, r=0.05, z=0.35, jitter=0.12)
        ns = pill(st, GXC + 0.65, SB7 + 1.3, "cannot simply be shut in", P.PANEL2, P.GAS, 0.19, 0.5, align="l")
        st.fade_in(ns, W(b, 1, "cannot simply be shut in") - 0.2, 0.4)
        st.fade_out([nb[0], nb[1], ns[0], ns[1]] + ghost, s[2] + 0.2, 0.4)
        # ---------- s2: boulders left by glaciers (in the till)
        t_bd = W(b, 2, "Boulders")
        bould = []
        for (x, y, r, colr) in ((1.6, 0.85, 0.22, "#9aa3ad"), (2.15, 0.6, 0.3, "#aab2bb"), (2.75, 0.85, 0.2, "#8f98a3"), (3.3, 0.55, 0.25, "#a0a8b2")):
            o = st.circle(x, y, r, colr, 0.08, role="flat")
            bould.append(o)
            st.pop_in(o, t_bd - 0.1 + 0.08 * len(bould), 0.35)
        bl = pill(st, 2.45, 2.0, "boulders", P.PANEL2, P.TEXT, 0.22, 0.5)
        bll = leader(st, (2.45, 1.78), (2.3, 0.95), P.MUTED, 0.49)
        st.fade_in(bl + [bll], t_bd, 0.4)
        # ---------- s3: soft, uneven seabed (a pockmark, filled with sea water)
        t_pm = W(b, 3, "Soft")
        PMX = 5.6
        pm_pts = [(PMX - 0.9, SB7 + 0.02)] + [(PMX + 0.9 * math.cos(math.pi * (1 - k / 12)), SB7 - 0.32 * math.sin(math.pi * k / 12)) for k in range(13)]
        pm = st.poly(pm_pts, P.SEA, 0.07)
        pml = st.line([(PMX + 0.9 * math.cos(math.pi * (1 - k / 12)), SB7 - 0.32 * math.sin(math.pi * k / 12)) for k in range(13)], P.SEABED, 0.04, 0.08)
        st.fade_in([pm, pml], t_pm - 0.1, 0.4)
        sl = pill(st, PMX, 2.0, "soft, uneven seabed", P.PANEL2, P.TEXT, 0.22, 0.5)
        sll = leader(st, (PMX, 1.78), (PMX, SB7 + 0.05), P.MUTED, 0.49)
        st.fade_in(sl + [sll], t_pm, 0.4)
        # ---------- s4: the site survey: a vessel with a multibeam fan (seabed) and a towed seismic source (below it)
        t_sv0 = s[4] - 0.1
        t_sv1 = b.end - 0.45
        xa, xb = -7.2, 7.3

        def ship_x(t):
            return xa + (xb - xa) * min(1.0, max(0.0, (t - t_sv0) / (t_sv1 - t_sv0)))
        t_over = lambda x: t_sv0 + (x - xa) / (xb - xa) * (t_sv1 - t_sv0)
        src_off = 1.0
        hz = {"gas": (GXC, t_over(GXC + src_off) + 0.45), "bould": (2.4, t_over(2.4)), "pm": (PMX, t_over(PMX))}

        def draw_survey(cv, t, look):
            a = env(t, t_sv0, b.end, 0.3, 0.3)
            if a <= 0:
                return
            x = ship_x(t)
            # wavefronts from the towed source, expanding into the ground
            sx = x - src_off
            for k in range(12):
                te = t_sv0 + 0.2 + 0.45 * k
                age = t - te
                if age < 0 or age > 1.8:
                    continue
                xe = ship_x(te) - src_off
                r = 0.3 + 2.6 * age
                al = 0.55 * a * (1 - age / 1.8)
                p = skia.Paint(Color=col(hex_rgb(P.TEXT), al), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.025)
                cv.save()
                cv.clipRect(skia.Rect(X0, -3.5, X1, SURF7 - 0.02))
                cv.drawArc(skia.Rect(xe - r, SURF7 - 0.05 - r, xe + r, SURF7 - 0.05 + r), 200, 140, False, p)
                cv.restore()
            # multibeam fan to the seabed
            fill(cv, [(x, SURF7 - 0.05), (x - 0.95, SB7 + 0.03), (x + 0.95, SB7 + 0.03)], P.TEXT, 0.13 * a)
            stroke(cv, look, [(x - 0.95, SB7 + 0.03), (x, SURF7 - 0.05), (x + 0.95, SB7 + 0.03)], P.TEXT, 0.45 * a, 0.018, glow=False)
            stroke(cv, look, [(x - 0.95, SB7 + 0.04), (x + 0.95, SB7 + 0.04)], P.TEXT, 0.9 * a, 0.035, glow=True)
            # streamer + source behind the vessel
            stroke(cv, look, [(x - 0.4, SURF7 + 0.02), (sx, SURF7 - 0.04), (sx - 2.4, SURF7 - 0.07)], P.MUTED, a, 0.02, glow=False)
            for k in range(8):
                cv.drawCircle(sx - 0.3 * k, SURF7 - 0.045 - 0.004 * k, 0.03, skia.Paint(Color=col(hex_rgb(P.WARN), 0.9 * a), AntiAlias=True))
            # the vessel
            hull = [(x - 0.55, SURF7 + 0.18), (x + 0.6, SURF7 + 0.18), (x + 0.4, SURF7 - 0.06), (x - 0.5, SURF7 - 0.06)]
            fill(cv, hull, P.STEEL, a)
            fill(cv, [(x - 0.3, SURF7 + 0.18), (x + 0.15, SURF7 + 0.18), (x + 0.15, SURF7 + 0.42), (x - 0.3, SURF7 + 0.42)], P.STEEL_DK, a)
            stroke(cv, look, [(x - 0.05, SURF7 + 0.42), (x - 0.05, SURF7 + 0.7)], P.STEEL, a, 0.03, glow=False)
            text(cv, look, "seabed mapping", x + 1.05, SB7 + 0.32, 0.15, P.TEXT, 0.9 * a, "l", "bold")
            text(cv, look, "shallow seismic", sx - 0.2, SURF7 - 0.42, 0.15, P.TEXT, 0.9 * a * env(t, t_sv0, t_sv1 - 2.0, 0.3, 0.5), "r", "bold")
        st.procedural(t_sv0, b.end, 0.6, draw_survey)
        # hazards light up as the survey finds them
        st.ripple(GXC, GYC + 0.1, hz["gas"][1], hz["gas"][1] + 2.0, P.GAS, period=0.55, r0=0.4, r1=1.6)
        bright = st.poly(gas_top + [(GXC + 1.05, GYC - 0.05), (GXC, GYC - 0.12), (GXC - 1.05, GYC - 0.05)], "#ff9fb5", 0.04, alpha=0.8, role="flat")
        st.fade_in(bright, hz["gas"][1], 0.2)
        st.fade_out(bright, hz["gas"][1] + 0.5, 1.2)
        bs = pill(st, GXC + 2.0, GYC - 0.75, "bright spot: gas found", P.PANEL2, P.GAS, 0.2, 0.5, align="l")
        st.fade_out(gl, hz["gas"][1] - 0.1, 0.2)
        st.fade_in(bs, hz["gas"][1], 0.3)
        st.ripple(2.4, 0.75, hz["bould"][1], hz["bould"][1] + 1.6, P.TEXT, period=0.6, r0=0.3, r1=1.3)
        st.ripple(PMX, SB7 - 0.1, hz["pm"][1], hz["pm"][1] + 1.6, P.TEXT, period=0.6, r0=0.3, r1=1.3)
        sv = pill(st, 0.9, -2.95, "site survey: seabed mapping + high-resolution shallow seismic, before the rig arrives", P.PANEL2, P.SAFE, 0.19, 0.5)
        st.fade_in(sv, W(b, 4, "site survey"), 0.4)


# ============================================================================================ 1.08 the staircase
def beat_staircase(st, tl):
    b = tl["1.08"]
    s = b.sent
    c = _chart(st)
    d1, d2, d3 = DESIGN
    mw1, mw2, mw3 = d1["mw"], d2["mw"], d3["mw"]
    sh9, sh13, sh20 = PROG[N9].shoe, PROG[N13].shoe, PROG[N20].shoe
    times = {}
    with st.span(b.start, b.end):
        _chart_static(st, c, b.start, b.end)
        back = _column_back(st, c)
        s9 = _string(st, c, N9)
        l9 = _shoe_label(st, c, N9)
        # carried over from 1.06: the deepest riser and its meeting point
        rise1 = st.line([c.pt(mw1, M.TD), c.pt(mw1, d1["shoe_calc"])], P.MUD, 0.08, 0.45)
        td = st.circle(c.X(mw1), c.Y(M.TD), 0.13, P.MUD, 0.5)
        lab1 = st.text(f"{mw1:.2f} sg", c.X(mw1) + 0.2, c.Y(M.TD) + 0.22, 0.2, P.MUD, 0.5, align="l", kind="bold")
        # the requirement curve morphs as the section mud weight changes
        t_m2 = W(b, 2, "one point four nine") - 0.2
        t_m3 = W(b, 3, "one point one two") - 0.2

        def mw_t(t):
            if t < t_m3:
                return mw1 + (mw2 - mw1) * ramp(t, t_m2, t_m2 + 1.0)
            return mw2 + (mw3 - mw2) * ramp(t, t_m3, t_m3 + 1.0)
        t_ystop = W(b, 4, "Shallow hazards") + 0.4

        def zmin_fn(mw):
            return 2350.0 if mw > 1.55 else (1300.0 if mw > 1.3 else 450.0)
        _req_curve(st, c, b.start, b.end, mw_t, zmin=zmin_fn, alpha_fn=lambda t: 1.0 - 0.6 * ramp(t, t_ystop, t_ystop + 0.8))
        ylab = st.text("fracture, less margin\nand kick allowance", c.X(1.95), c.Y(2900), 0.16, P.WARN, 0.4, align="r", kind="bold")
        st.fade_out(ylab, s[2] - 0.2, 0.4)
        # ---------- s1: the deepest string ends at about 3,400 m
        t1 = W(b, 1, "three thousand four hundred")
        st.ripple(COL_X, c.Y(sh9), t1 - 0.2, t1 + 2.0, P.TEXT, period=0.8, r0=0.15, r1=0.9)
        sl9 = st.dashed(c.pt(XR[0], sh9), c.pt(mw1, sh9), P.TEXT, 0.025, 0.08, 0.06, 0.4, alpha=0.8)
        st.fade_in(sl9, t1, 0.3)
        p9 = pill(st, -3.25, c.Y(sh9) + 0.32, f"shoe {sh9:,.0f} m", P.PANEL2, P.TEXT, 0.19, 0.55)
        st.fade_in(p9, t1, 0.4)
        # ---------- s2: lighter mud above that shoe: 1.49 sg, meets the curve near 2,000 m
        t_l = W(b, 2, "lighter")
        tr1 = st.line([c.pt(mw1, sh9), c.pt(mw2, sh9)], P.MUD, 0.08, 0.45)
        st.draw_on(tr1, t_l - 0.1, t_l + 0.7, "BEZIER")
        p2 = pill(st, c.X(mw2) - 0.15, c.Y(2700), f"{mw2:.2f} sg", P.PANEL2, P.MUD, 0.2, 0.55, align="r")
        st.fade_in(p2, t_m2 + 0.2, 0.3)
        t_r2 = W(b, 2, "its line meets") - 0.2
        t_r2e = W(b, 2, "near two thousand") + 0.2
        r2 = st.line([c.pt(mw2, sh9), c.pt(mw2, d2["shoe_calc"])], P.MUD, 0.08, 0.45)
        st.draw_on(r2, t_r2, t_r2e, "BEZIER")
        m2 = st.ring(c.X(mw2), c.Y(d2["shoe_calc"]), 0.15, 0.045, P.TEXT, 0.55)
        st.pop_in(m2, t_r2e - 0.1, 0.4)
        p2s = pill(st, c.X(1.98), c.Y(d2["shoe_calc"]), f"shoe ≥ {d2['shoe_calc']:,.0f} m", P.PANEL2, P.TEXT, 0.18, 0.55, align="r")
        st.fade_in(p2s, t_r2e, 0.4)
        t_ns = W(b, 2, "the next shoe") - 0.2
        s13 = _string(st, c, N13, t_ns, t_ns + 1.5)
        l13 = _shoe_label(st, c, N13, t_ns + 1.4)
        times["13"] = t_ns + 1.5
        # ---------- s3: above that, 1.12 sg: so light that pressure no longer decides
        st.fade_out(p2s, s[3] - 0.3, 0.3)
        tr2 = st.line([c.pt(mw2, sh13), c.pt(mw3, sh13)], P.MUD, 0.08, 0.45)
        st.draw_on(tr2, t_m3 - 0.2, t_m3 + 0.6, "BEZIER")
        p3 = pill(st, c.X(mw3) + 0.15, c.Y(1500), f"{mw3:.2f} sg", P.PANEL2, P.MUD, 0.2, 0.55, align="l")
        st.fade_in(p3, t_m3 + 0.3, 0.3)
        t_r3 = t_m3 + 1.0
        r3 = st.line([c.pt(mw3, sh13), c.pt(mw3, sh20)], P.MUD, 0.08, 0.45)
        st.draw_on(r3, t_r3, t_r3 + 1.3, "BEZIER")
        ghost3 = st.dashed(c.pt(mw3, sh20), c.pt(mw3, d3["shoe_calc"]), P.MUD, 0.05, 0.1, 0.07, 0.44, alpha=0.8)
        t_g3 = t_r3 + 1.3
        for k, o in enumerate(ghost3):
            st.fade_in(o, t_g3 + 0.05 * k, 0.15)
        m3 = st.ring(c.X(mw3), c.Y(d3["shoe_calc"]), 0.15, 0.045, P.TEXT, 0.55)
        st.pop_in(m3, t_g3 + 0.4, 0.35)
        p3c = pill(st, -0.95, c.Y(d3["shoe_calc"]) - 0.05, f"pressure alone: {d3['shoe_calc']:,.0f} m", P.PANEL2, P.MUTED, 0.18, 0.55, align="l")
        l3c = leader(st, (c.X(mw3) + 0.16, c.Y(d3["shoe_calc"])), (-0.95, c.Y(d3["shoe_calc"]) - 0.05), P.MUTED, 0.54)
        st.fade_in(p3c + [l3c], W(b, 3, "no longer decides") - 0.2, 0.4)
        # ---------- s4: shallow hazards and the anchor for wellhead + BOP decide: not shallower than 1,000 m
        t_hz = W(b, 4, "Shallow hazards")
        fl = st.dashed(c.pt(XR[0], sh20), c.pt(XR[1], sh20), P.WARN, 0.03, 0.12, 0.08, 0.42, alpha=0.9)
        st.fade_in(fl, t_hz - 0.2, 0.4)
        fp = pill(st, c.X(1.98), c.Y(1350), "shallow hazards +\nwellhead/BOP anchor:\nnot shallower than 1,000 m", P.PANEL2, P.WARN, 0.18, 0.55, align="r")
        st.fade_in(fp, W(b, 4, "strong anchor") - 0.3, 0.4)
        st.fade_out(p3c + [l3c], W(b, 4, "strong anchor") - 0.3, 0.3)
        # ---------- s5: about a thousand metres -> the shoe snaps down to 1,000 m, surface casing goes in
        t_k = W(b, 5, "thousand")
        st.move(m3, t_k - 0.3, t_k + 0.5, to=(c.X(mw3), c.Y(sh20)))
        st.fade_out(ghost3, t_k + 0.2, 0.5)
        st.ripple(c.X(mw3), c.Y(sh20), t_k + 0.4, t_k + 2.0, P.WARN, period=0.7, r0=0.12, r1=0.7)
        s20 = _string(st, c, N20, t_k - 0.2, t_k + 1.1)
        l20 = _shoe_label(st, c, N20, t_k + 1.0)
        times["20"] = t_k + 1.1
        # ---------- s6: the result is a staircase (plus the soil-driven conductor)
        t_st = W(b, 6, "staircase") - 0.6
        stair = [c.pt(mw1, M.TD), c.pt(mw1, sh9), c.pt(mw2, sh9), c.pt(mw2, sh13), c.pt(mw3, sh13), c.pt(mw3, sh20)]
        sg_ = st.line(stair, "#fff1c2", 0.05, 0.47)
        st.draw_on(sg_, t_st, t_st + 1.6, "BEZIER")
        st.fade_out(sg_, t_st + 1.7, 0.6)
        stl = st.text("a staircase", -3.3, c.Y(3850), 0.32, P.MUD, 0.5, kind="bold")
        st.fade_in(stl, t_st + 0.4, 0.4)
        s30 = _string(st, c, N30, s[5] + 0.6, s[5] + 1.3)
        l30 = _shoe_label(st, c, N30, s[5] + 1.2, extra="  conductor: set by the soil")
        times["30"] = s[5] + 1.3
    return times


# ============================================================================================ 1.09 telescope, wildcat, contingency
def beat_telescope(st, tl):
    b = tl["1.09"]
    s = b.sent
    prog = M.programme()
    SX, KW = -5.0, 0.045                       # side view centre x; world units per inch (width only, to scale)
    ytop, ybot = 3.25, -3.15
    ys = lambda z: ytop - (z - M.WATER_DEPTH) * (ytop - ybot) / (M.TD - M.WATER_DEPTH)
    RX, RY, KR = 2.1, -0.35, 0.085             # ring view centre; world units per inch of diameter
    with st.span(b.start, b.end):
        # ---------- the side view (to scale in width): rock, drilled hole sections, casing strings
        back = st.rect(SX, (ytop + ybot) / 2, 2.3, ytop - ybot, P.ROCK, 0.0)
        sea = st.rect(SX, ytop + 0.18, 2.3, 0.36, P.SEA, 0.0)
        sbd = st.rect(SX, ytop, 2.3, 0.03, P.SEABED, 0.02)
        st.fade_in([back, sea, sbd], b.start + 0.1, 0.5)
        sections = [(M.WATER_DEPTH, prog[0].shoe, prog[0].hole_in), (prog[0].shoe, prog[1].shoe, prog[1].hole_in),
                    (prog[1].shoe, prog[2].shoe, prog[2].hole_in), (prog[2].shoe, prog[3].shoe, prog[3].hole_in), (prog[3].shoe, M.TD, M.HOLE_TD_IN)]
        t_tel = [s[0] + 0.1 + 0.55 * i for i in range(5)]
        holes = []
        for i, (za, zb, hin) in enumerate(sections):
            h = st.rect(SX, ys(za), hin * KW, 0.0001, P.BG, 0.05, anchor="t", role="hole")
            st.fade_in(h, t_tel[i], 0.1)
            st.scale_to(h, t_tel[i], t_tel[i] + 0.6, sy=ys(za) - ys(zb) + (0.0 if i == 4 else 0.01))
            holes.append(h)
        walls = []
        for i, p in enumerate(prog):
            w = p.od_in * KW
            for sg in (-1, 1):
                o = st.rect(SX + sg * (w / 2 - 0.025), ytop, 0.05, 0.0001, P.STEEL, 0.2 + 0.01 * i, anchor="t")
                st.fade_in(o, t_tel[i] + 0.2, 0.1)
                st.scale_to(o, t_tel[i] + 0.2, t_tel[i] + 0.8, sy=ytop - ys(p.shoe))
                walls.append(o)
        # size labels, keyed to the sizes as they are spoken
        say = [W(b, 1, "thirty inch"), W(b, 1, "twenty"), W(b, 1, "thirteen and three eighths"), W(b, 1, "nine and five eighths")]
        t_hole = W(b, 1, "each set in a bigger drilled hole")
        t_oh = W(b, 1, "eight and a half inch open hole")
        LX = SX + 1.35
        for i, p in enumerate(prog):
            y = ys(p.shoe) + (0.0 if i else -0.1)
            a = st.text(f"{SIZE[p.name]} casing", LX, y + 0.13, 0.19, P.TEXT, 0.4, align="l", kind="bold")
            bb = st.text(f"in {HOLE[p.name]} hole · {p.shoe:,.0f} m", LX, y - 0.15, 0.16, P.MUTED, 0.4, align="l")
            st.fade_in(a, say[i] - 0.1, 0.3)
            st.fade_in(bb, t_hole + 0.25 * i, 0.3)
            st.recolor(bb, t_hole + 0.25 * i, t_hole + 0.25 * i + 0.3, P.TEXT)
        ohl = st.text('8½" open hole', LX, ys(3950) + 0.13, 0.19, P.TEXT, 0.4, align="l", kind="bold")
        ohl2 = st.text(f"to {M.TD:,.0f} m", LX, ys(3950) - 0.15, 0.16, P.TEXT, 0.4, align="l")
        st.fade_in([ohl, ohl2], t_oh, 0.3)
        # ---------- the ring view: looking down the well, to scale (solid steel = casing, thin = drilled hole)
        rv_t = st.text("looking down the well, to scale", RX, RY + 36 * KR / 2 + 0.35, 0.18, P.MUTED, 0.3, kind="bold")
        st.fade_in(rv_t, s[1] - 0.2, 0.4)
        holes_in = [36, 26, 17.5, 12.25, 8.5]
        for i, hin in enumerate(holes_in):
            r = hin * KR / 2
            o = st.ring(RX, RY, r, 0.022, P.MUTED, 0.2 + 0.02 * i, alpha=0.9)
            t = say[i] - 0.15 if i < 4 else t_oh
            st.pop_in(o, t, 0.35)
        rings = []
        for i, p in enumerate(prog):
            r = p.od_in * KR / 2
            o = st.ring(RX, RY, r, 0.07, P.STEEL, 0.21 + 0.02 * i)
            st.pop_in(o, say[i], 0.4)
            rings.append(o)
        bore = st.circle(RX, RY, M.HOLE_TD_IN * KR / 2 - 0.022, P.BG, 0.2, role="hole")
        st.fade_in(bore, t_oh, 0.3)
        # labels to the right, horizontal leaders (they never cross)
        lab_x = RX + 36 * KR / 2 + 0.3
        rows = [(30.0, 1.15, '30"', say[0]), (20.0, 0.78, '20"', say[1]), (13.375, 0.42, '13⅜"', say[2]), (9.625, 0.08, '9⅝"', say[3]),
                (8.5, -0.25, '8½" hole', t_oh)]
        for od, dy, name, t in rows:
            r = od * KR / 2
            px = RX + math.sqrt(max(r * r - dy * dy, 0.0))
            ln = leader(st, (px, RY + dy), (lab_x - 0.06, RY + dy), P.MUTED, 0.3, 0.7)
            tx = st.text(name, lab_x, RY + dy, 0.19, P.TEXT, 0.3, align="l", kind="bold")
            st.fade_in([ln, tx], t + 0.1, 0.3)
        leg = st.text("thick ring: casing    thin ring: drilled hole", RX, RY - 36 * KR / 2 - 0.3, 0.15, P.MUTED, 0.3)
        st.fade_in(leg, t_hole, 0.4)
        # ---------- s2: every string costs diameter
        t_cd = W(b, 2, "costs diameter")
        cd = pill(st, RX, RY - 36 * KR / 2 - 0.85, "every string costs diameter: 36\" at the top, 8½\" at the bottom", P.PANEL2, P.WARN, 0.18, 0.5)
        st.fade_in(cd, t_cd - 0.3, 0.4)
        st.fade_out(cd, s[3] - 0.2, 0.3)
        for o in rings:
            pass
        st.ripple(RX, RY, t_cd - 0.2, t_cd + 1.6, P.WARN, period=0.7, r0=1.55, r1=0.35)
        # ---------- s3: wildcat
        t_wc = W(b, 3, "wildcat")
        wc = pill(st, RX, RY - 36 * KR / 2 - 0.85, "wildcat: first well on an untested prospect", P.PANEL2, P.TEXT, 0.2, 0.5)
        st.fade_in(wc, t_wc, 0.4)
        # ---------- s4: nearby wells help, but may sit in a different pressure compartment: the forecast is uncertain
        fx0, fy0 = 4.6, -3.05
        fc = Chart(st, fx0, fy0, 2.6, 2.2, (1.0, 1.8), (2000.0, M.TD), invert_y=True)
        ffr = fc.frame(xticks=[], yticks=[], xlabel="", ylabel="", grid=False)
        t_nw = W(b, 4, "Nearby wells")
        zf = [2000.0 + 50 * i for i in range(int((M.TD - 2000) / 50) + 1)]
        unc = lambda z: 0.02 + 0.10 * max(0.0, (z - 2400) / 1800)
        band = fc.band([(M.pp(z) - unc(z), z) for z in zf], [(M.pp(z) + unc(z), z) for z in zf], P.PORE, 0.1, 0.25)
        fcur = fc.curve([M.pp(z) for z in zf], zf, P.PORE, 0.05, 0.2)
        nb = st.line([fc.pt(M.pp(z) - (0.0 if z < 2900 else 0.09 * min(1.0, (z - 2900) / 400)), z) for z in zf], P.MUTED, 0.035, 0.19)
        ft = st.text("pore pressure forecast", fx0 + 1.3, fy0 + 2.45, 0.17, P.PORE, 0.3, kind="bold")
        st.fade_in(ffr + [ft, fcur], t_nw - 0.3, 0.4)
        st.draw_on(nb, t_nw, t_nw + 1.2)
        nbl = st.text("nearby well", fc.X(1.12), fc.Y(3700), 0.15, P.MUTED, 0.3, align="c")
        st.fade_in(nbl, t_nw + 0.6, 0.3)
        t_cp = W(b, 4, "different pressure compartment")
        st.fade_in(band, W(b, 4, "uncertain") - 0.3, 0.5)
        unl = st.text("uncertain", fc.X(1.7), fc.Y(3300), 0.16, P.PORE, 0.3, align="c", kind="bold")
        st.fade_in(unl, W(b, 4, "uncertain"), 0.4)
        # ---------- s5: a spare, contingency string (7 in) in reserve; it only fits if everything above is bigger
        t_cs = W(b, 5, "contingency string")
        zl0, zl1 = PROG[N9].shoe - 100.0, 3800.0      # ghost liner: lapped ~100 m inside the 9⅝" shoe, set where trouble starts
        w7 = 7.0 * KW
        ghost = []
        for sg in (-1, 1):
            ghost += st.dashed((SX + sg * (w7 / 2 - 0.02), ys(zl0)), (SX + sg * (w7 / 2 - 0.02), ys(zl1)), P.WARN, 0.035, 0.1, 0.07, 0.5)
        g6 = []
        for sg in (-1, 1):
            g6 += st.dashed((SX + sg * 6.0 * KW / 2, ys(zl1)), (SX + sg * 6.0 * KW / 2, ys(M.TD)), P.MUTED, 0.02, 0.07, 0.06, 0.5)
        st.fade_in(ghost, t_cs - 0.2, 0.4)
        st.fade_in(g6, t_cs + 0.6, 0.4)
        cl = pill(st, LX + 1.85, ys(3700), 'contingency string (7 in)\nin reserve', P.PANEL2, P.WARN, 0.17, 0.55, align="l")
        cll = leader(st, (SX + w7 / 2 + 0.05, ys(3650)), (LX + 1.85, ys(3700)), P.WARN, 0.54, 0.7)
        st.fade_in(cl + [cll], t_cs, 0.4)
        r7 = st.ring(RX, RY, 7.0 * KR / 2, 0.045, P.WARN, 0.3, alpha=0.9)
        st.pop_in(r7, t_cs + 0.2, 0.4)
        t_fit = W(b, 5, "only fits")
        st.ripple(RX, RY, t_fit, t_fit + 2.5, P.WARN, period=0.8, r0=0.3, r1=1.5)
        fit = pill(st, RX, RY - 36 * KR / 2 - 0.85, "it only fits if every size above is bigger from the start", P.PANEL2, P.WARN, 0.18, 0.5)
        st.fade_out(wc, t_fit - 0.3, 0.3)
        st.fade_in(fit, t_fit, 0.4)


# ============================================================================================ build
def build(st, tl):
    F.header(st, tl)
    beat_target(st, tl)
    beat_hydrostatic(st, tl)
    beat_terzaghi(st, tl)
    beat_fracture(st, tl)
    beat_window(st, tl)
    T1 = beat_bottom_up(st, tl)
    beat_hazards(st, tl)
    tm = beat_staircase(st, tl)
    beat_telescope(st, tl)
    # 'well so far' strip: hidden in 1.01 (the section itself is the depth ruler there); then the design, string by string
    t0 = tl["1.02"].start
    F.well_strip(st, t0, T1)
    F.well_strip(st, T1, tm["13"], strings=[N9])
    F.well_strip(st, tm["13"], tm["20"], strings=[N9, N13])
    F.well_strip(st, tm["20"], tm["30"], strings=[N9, N13, N20])
    F.well_strip(st, tm["30"], tl.dur, strings=[N30, N20, N13, N9])
