"""Ch 8: Formation evaluation: discovery or dry hole?

8.01 the question flips; the ladder of measurements ranked by cost and certainty (time-to-result jumps around)
8.02 mud log: circulation brings cuttings to the shaker, a UV tray where oil glows, a chromatogram C1-C5, the lag clock
8.03 LWD: a bit + sensor collar drills down the depth column, the logs draw on at the sensor depth (a few metres behind
     the bit); gamma ray, resistivity, density-neutron with the gas crossover; mud-pulse telemetry vs memory
8.04 Archie: a brine-filled pore network conducts; oil blocks paths and the ammeter drops; the equation, the worked
     example from the model (Rw 0.05, phi 0.23, Rt 23.6 -> Sw 0.20); shaly sands need extended models
8.05 THE PRESSURE-GRADIENT PLOT: a wireline formation tester sets at ten stations; gas / oil / water lines (0.025 /
     0.076 / 0.106 bar/m); GOC 3,990 m and FWL 4,052 m from the crossings; the well crossed the FWL; a ghost example
     where the water line is borrowed from a neighbouring well
8.06 samples (optical analysis + bottle), two sands on offset lines vs one line, FWL (pressure) vs OWC (logs) 6 m higher
8.07 coring with a hollow bit vs cuttings vs sidewall plugs; lab: porosity, permeability plug test, triaxial cell,
     stress-strain, Mohr circles centred on the sigma axis with a tangent envelope; weeks vs months
8.08 DST in a liner cemented across the reservoir (hung in the 9-5/8 in casing): packer, tester valve, separator, burner;
     rate + build-up + log-log derivative; Norway emissions; the test string fades: our well = logs, pressures, samples
8.09 cutoffs in three passes, net reservoir / gross = 151 / 160 = 0.94, net pay 89 m (37 gas + 52 oil)
8.10 decision tree: present? movable? -> DISCOVERY (technical); Sodir definition; will it pay?; dry hole = still data

Every curve, saturation, pressure, contact and thickness is computed in scenes/common/logs.py (synthetic data).
"""
from __future__ import annotations
import bisect
import math
import random

import skia

from scenes.common import palette as P, well_model as M, furniture as F, logs as L
from scenes.common.chart import Chart
from scenes.common.shapes import pill
from scenes.common.stage import Track, as_list
from scenes.common.look import col, hex_rgb

TITLE = "Formation evaluation: discovery or dry hole?"
LG = L.generate()
SUM = L.summary(LG)
FIT = L.fitted_contacts()

# neutral, non-palette colours used only on this chapter's instrument drawings (no fluid / limit meaning)
CURVE = "#e8eef6"        # generic log curve (white, as on a log print)
NEUTRON = "#a5b4fc"      # neutron porosity curve (lavender) next to the white density curve
CUTTING = "#5a4632"      # a rock chip in the mud
UV_BG = "#1d1240"        # UV light box
GLOW = "#fff4b0"         # oil fluorescence (yellow-white)
ELEC = "#ffffff"         # electric current particles
LABGAS = "#cfd8e6"       # lab nitrogen / brine in the permeability rig
FLAME = "#ffd27a"        # burner flame
RUBBER = "#30343f"       # packer element
CLAY = "#8a9a8c"         # clay flakes


# ====================================================================================================== small helpers
def _w(b, i, needle, frac=0.0):
    return b.word(i, needle, frac)


def _clamp(v, a, b):
    return max(a, min(b, v))


def _env(t, t0, t1, fin=0.35, fout=0.35):
    a = 1.0
    if fin > 0:
        a = min(a, (t - t0) / fin)
    if fout > 0:
        a = min(a, (t1 - t) / fout)
    return _clamp(a, 0.0, 1.0)


def _path(pts, closed=False):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if closed:
        p.close()
    return p


def _stroke(c, look, pts, color, width, alpha, glow=False, dash=None):
    if len(pts) < 2 or alpha <= 0.003:
        return
    path = _path(pts)
    rgb = hex_rgb(color)
    if glow:
        g = skia.Paint(Color=col(rgb, 0.35 * alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width * 2.4,
                       StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join,
                       MaskFilter=look._blur(max(3.0, width * look.k * 0.8)))
        c.drawPath(path, g)
    p = skia.Paint(Color=col(rgb, alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width,
                   StrokeCap=skia.Paint.kRound_Cap if not dash else skia.Paint.kButt_Cap, StrokeJoin=skia.Paint.kRound_Join)
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(list(dash), 0.0))
    c.drawPath(path, p)


def _fill(c, pts, color, alpha):
    if len(pts) < 3 or alpha <= 0.003:
        return
    c.drawPath(_path(pts, True), skia.Paint(Color=col(hex_rgb(color), alpha), AntiAlias=True))


def _tip(c, look, x, y, color, r, alpha):
    rgb = hex_rgb(color)
    c.drawCircle(x, y, r * 2.6, skia.Paint(Color=col(rgb, 0.5 * alpha), AntiAlias=True, MaskFilter=look._blur(max(4.0, r * look.k))))
    c.drawCircle(x, y, r, skia.Paint(Color=col((1, 1, 1), alpha), AntiAlias=True))


def _alpha_track(keys):
    """keys [(t, a)] -> callable alpha(t) (linear)."""
    tr = Track()
    for t, a in keys:
        tr.set(t, a, "LINEAR")
    return tr.eval


def _lbl(st, x, y, text, fg=P.TEXT, size=0.19, align="c", z=0.7, bg=P.PANEL2, kind="bold"):
    return pill(st, x, y, text, bg, fg, size, z, pad=0.16, kind=kind, align=align)


def _check(st, x, y, t, s=0.16, z=1.2, color=P.SAFE):
    plate = st.circle(x, y, s * 1.45, P.PANEL2, z - 0.01, role="disc")
    ln = st.line([(x - s * 0.62, y + 0.0), (x - s * 0.15, y - s * 0.48), (x + s * 0.7, y + s * 0.55)], color, 0.06, z)
    st.pop_in(plate, t - 0.05, 0.3)
    st.draw_on(ln, t + 0.05, t + 0.45, "BEZIER")
    return [plate, ln]


def _arc(cx, cy, r, a0, a1, n=48):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
            for k in range(n + 1)]


def _zoom_link(st, t0, t1, z_top, z_bot, y_top, y_bot, x_to=-6.22):
    """Highlight the logged interval on the well strip and draw zoom lines to the log tracks (fixes the two-scale
    confusion between the 0-4,200 m strip and the 200 m log window)."""
    ya, yb = F.depth_y(z_top), F.depth_y(z_bot)
    xr = F.STRIP_CX + 0.62
    band = st.rect(F.STRIP_CX, (ya + yb) / 2, 1.24, ya - yb + 0.02, P.WARN, 0.35, alpha=0.55, role="flat")
    l1 = st.line([(xr, ya), (x_to, y_top)], P.WARN, 0.018, 0.3, alpha=0.45, role="hair")
    l2 = st.line([(xr, yb), (x_to, y_bot)], P.WARN, 0.018, 0.3, alpha=0.45, role="hair")
    st.fade_in(band, t0, 0.4)
    st.draw_on([l1, l2], t0 + 0.2, t0 + 0.9, "BEZIER")
    return [band, l1, l2]


# ------------------------------------------------------------------------------------------- log display geometry
LZ0, LZ1 = 3925.0, 4135.0       # displayed depth window (logs cover 3,930-4,130 m)
LY0, LY1 = 2.95, -3.25          # world y of LZ0 / LZ1


def Yd(z):
    return LY0 + (z - LZ0) * (LY1 - LY0) / (LZ1 - LZ0)


def _xmap(x0, w, lo, hi, logscale=False):
    if logscale:
        lo, hi = math.log10(lo), math.log10(hi)

    def f(v):
        if logscale:
            v = math.log10(max(v, 1e-6))
        return x0 + _clamp((v - lo) / (hi - lo), 0.0, 1.0) * w
    return f


def _track_frame(st, x0, w, title, color=CURVE, ticks=(), unit=None, z=0.05):
    """A log track: card, vertical grid, depth grid, title + unit, tick labels. Returns objects."""
    out = [st.rect(x0 + w / 2, (LY0 + LY1) / 2, w + 0.12, LY0 - LY1 + 0.12, P.PANEL, z - 0.02)]
    for zz in (3950, 4000, 4050, 4100):
        out.append(st.rect(x0 + w / 2, Yd(zz), w, 0.012, P.GRID, z))
    for (xv, txt) in ticks:
        out.append(st.rect(xv, (LY0 + LY1) / 2, 0.012, LY0 - LY1, P.GRID, z))
        out.append(st.text(txt, xv, LY1 - 0.2, 0.13, P.MUTED, z + 0.01))
    out.append(st.text(title, x0 + w / 2, LY0 + 0.42, 0.17, color, z + 0.01, kind="bold"))
    if unit:
        out.append(st.text(unit, x0 + w / 2, LY0 + 0.18, 0.13, P.MUTED, z + 0.01))
    return out


def _depth_labels(st, x=-5.62, z=0.1):
    out = [st.text(f"{zz:,}", x, Yd(zz), 0.15, P.MUTED, z, align="r", kind="mono") for zz in (3950, 4000, 4050, 4100)]
    out.append(st.text("m", x - 0.25, LY0 + 0.18, 0.13, P.MUTED, z, align="r"))
    return out


def _log_curve(st, xs, zs, X, color, width, t0, t1, zfront=None, alpha_fn=None, z=0.3, glow=True):
    """A log curve revealed down to depth zfront(t) (the sensor), with a bright tip while it is being drawn."""
    pts = [(X(v), Yd(zz)) for v, zz in zip(xs, zs)]

    def draw(c, t, look):
        a = _env(t, t0, t1, 0.3, 0.3) * (alpha_fn(t) if alpha_fn else 1.0)
        if a <= 0.003:
            return
        n = len(pts) if zfront is None else bisect.bisect_right(zs, zfront(t))
        if n < 2:
            return
        _stroke(c, look, pts[:n], color, width, a, glow=glow)
        if n < len(pts):
            _tip(c, look, pts[n - 1][0], pts[n - 1][1], color, width * 1.4, a)
    st.procedural(t0, t1, z, draw)


# ====================================================================================================== 8.01 the ladder
def beat_ladder(st, tl):
    b = tl["8.01"]
    s = b.sent
    with st.span(b.start, b.end):
        # the question flips
        old = st.text("How do we get there safely?", 0.6, 0.55, 0.5, P.TEXT, 0.5, kind="bold")
        st.fade_in(old, s[0] - 0.1, 0.5)
        t_flip = _w(b, 1, "now it is")
        st.recolor(old, t_flip - 0.4, t_flip, P.MUTED)
        st.move(old, t_flip - 0.4, t_flip + 0.4, dy=0.55)
        st.fade(old, t_flip, t_flip + 0.5, 1.0, 0.45)
        new = st.text("What did we find?", 0.6, -0.35, 0.72, P.WARN, 0.5, kind="bold")
        st.pop_in(new, t_flip, 0.45)
        st.fade_in(new, t_flip, 0.25)
        t_lad = s[2] - 0.35
        st.fade_out(old, t_lad - 0.5, 0.4)
        st.fade_out(new, t_lad - 0.3, 0.4)

        # the ladder: rails + rungs, one row per measurement
        rows = [("mud log", "~1 h (lag)", 0.15, 0.04),
                ("logging while drilling", "minutes", 0.32, 0.10),
                ("wireline logs", "days", 0.48, 0.20),
                ("pressures + samples", "days", 0.64, 0.33),
                ("core", "weeks", 0.80, 0.55),
                ("well test", "weeks", 0.95, 1.00)]
        y0, dy = 2.35, 0.98
        ys = [y0 - dy * i for i in range(len(rows))]
        RX = -5.75
        rails = [st.rect(RX - 0.22, (ys[0] + ys[-1]) / 2, 0.06, ys[0] - ys[-1] + 0.9, P.STEEL_DK, 0.2, role="steel"),
                 st.rect(RX + 0.22, (ys[0] + ys[-1]) / 2, 0.06, ys[0] - ys[-1] + 0.9, P.STEEL_DK, 0.2, role="steel")]
        st.fade_in(rails, t_lad, 0.5)
        hx = {"time": 0.55, "cert": 2.85, "cost": 5.75}
        heads = [st.text("time to result", hx["time"], 3.3, 0.17, P.MUTED, 0.4, kind="bold"),
                 st.text("certainty", hx["cert"], 3.3, 0.17, P.SAFE, 0.4, kind="bold"),
                 st.text("cost", hx["cost"], 3.3, 0.17, P.WARN, 0.4, kind="bold")]
        st.fade_in(heads, t_lad + 0.2, 0.5)
        t_row0 = s[2] + 0.4
        t_rowN = _w(b, 2, "slow") - 0.2
        step = (t_rowN - t_row0) / (len(rows) - 1)
        time_tags = []
        for i, (name, ttr, cert, cost) in enumerate(rows):
            y = ys[i]
            t = t_row0 + step * i
            rung = st.rect(RX, y, 0.5, 0.07, P.STEEL, 0.25, role="steel")
            num = st.text(f"{i + 1}", RX, y + 0.27, 0.14, P.MUTED, 0.3, kind="mono")
            lab = st.text(name, -5.25, y, 0.25, P.TEXT, 0.4, align="l", kind="bold")
            tag = _lbl(st, hx["time"], y, ttr, P.TEXT, 0.18, z=0.45)
            time_tags.append(tag)
            tr_c = st.rect(hx["cert"] - 1.0, y, 2.0, 0.22, P.PANEL2, 0.3, anchor="l", role="pill")
            tr_k = st.rect(hx["cost"] - 1.6, y, 3.2, 0.22, P.PANEL2, 0.3, anchor="l", role="pill")
            bc = st.rect(hx["cert"] - 1.0, y, 0.0001, 0.22, P.SAFE, 0.32, anchor="l", role="pill")
            bk = st.rect(hx["cost"] - 1.6, y, 0.0001, 0.22, P.WARN, 0.32, anchor="l", role="pill")
            st.fade_in([rung, num, lab, tr_c, tr_k] + tag, t, 0.35)
            st.scale_to(bc, t + 0.15, t + 0.85, sx=2.0 * cert)
            st.scale_to(bk, t + 0.25, t + 0.95, sx=3.2 * cost)
        # the two ends of the ladder
        t_fast = _w(b, 2, "fast")
        top = _lbl(st, 3.8, ys[0] + 0.62, "fast · cheap · uncertain", P.PORE, 0.17, z=0.6)
        bot = _lbl(st, 3.8, ys[-1] - 0.6, "slow · costly · definitive", P.WARN, 0.17, z=0.6)
        st.fade_in(top, max(t_fast, t_row0 + 0.3), 0.4)
        st.fade_in(bot, _w(b, 2, "slow"), 0.4)
        # ranked by price, not by time: the time column lights up out of order
        t_price = _w(b, 3, "price")
        t_time = _w(b, 3, "not by time")
        frame = st.rect(hx["time"], (ys[0] + ys[-1]) / 2, 1.85, ys[0] - ys[-1] + 0.75, P.WARN, 0.2, alpha=0.08, role="flat")
        st.fade_in(frame, t_time - 0.2, 0.4)
        for i in (1, 0, 2, 3):    # minutes, ~1 h, days ... : not the ladder order
            st.recolor(time_tags[i][1], t_time + 0.15 * i, t_time + 0.15 * i + 0.3, P.WARN)
        note = _lbl(st, 0.55, -3.35, "ranked by cost and certainty, not by time", P.WARN, 0.2, z=0.6)
        st.fade_in(note, t_price - 0.2, 0.45)


# ====================================================================================================== 8.02 mud log
def beat_mudlog(st, tl):
    b = tl["8.02"]
    s = b.sent
    rnd = random.Random(2)
    CX, HW, PW = -4.6, 0.62, 0.2          # hole centre, half-widths of hole and pipe
    YT, YB = 2.55, -2.95                  # surface outlet and hole bottom
    with st.span(b.start, b.end):
        t_in = b.start + 0.1
        # rock column with a sand layer at the bit
        rock = [st.rect(CX, (YT + 0.0) / 2 + 0.2, 2.9, YT - 0.0 + 0.4, P.ROCK2, 0.0),
                st.rect(CX, (0.0 - 1.7) / 2, 2.9, 1.7, P.SHALE, 0.0),
                st.rect(CX, (-1.7 - 3.35) / 2, 2.9, 1.65, P.SAND, 0.0)]
        hole = st.rect(CX, (YT + YB) / 2, 2 * HW, YT - YB, P.BG, 0.02)
        ann = st.rect(CX, (YT + YB) / 2, 2 * HW, YT - YB, P.MUD, 0.03, alpha=0.28, role="flat")
        pipe = [st.rect(CX - PW, (YT + 0.3 + YB + 0.3) / 2, 0.06, YT + 0.3 - (YB + 0.3), P.STEEL, 0.2),
                st.rect(CX + PW, (YT + 0.3 + YB + 0.3) / 2, 0.06, YT + 0.3 - (YB + 0.3), P.STEEL, 0.2)]
        bit = st.poly([(CX - HW + 0.05, YB + 0.32), (CX + HW - 0.05, YB + 0.32), (CX + HW - 0.18, YB + 0.02), (CX - HW + 0.18, YB + 0.02)],
                      P.STEEL_DK, 0.25)
        # shaker at the surface
        SX, SY = -2.55, 3.05
        flowline = st.rect((CX + HW + SX - 0.7) / 2, YT + 0.05, SX - 0.7 - (CX + HW), 0.1, P.STEEL_DK, 0.15)
        riser_out = st.rect(CX + HW - 0.05, YT + 0.0, 0.1, 0.3, P.STEEL_DK, 0.15)
        screen = st.line([(SX - 0.75, SY + 0.12), (SX + 0.75, SY - 0.2)], P.STEEL, 0.06, 0.3)
        shaker_box = st.rect(SX, SY - 0.38, 1.3, 0.35, P.PANEL2, 0.25, role="card")
        shl = st.text("shaker", SX, SY - 0.38, 0.15, P.MUTED, 0.3, kind="bold")
        base = rock + [hole, ann, bit, flowline, riser_out, screen, shaker_box, shl] + pipe
        st.fade_in(base, t_in, 0.5)
        # circulation: down the pipe, up both annuli, out to the shaker
        down = [(CX, YT + 0.3), (CX, YB + 0.35)]
        up_l = [(CX - HW + 0.1, YB + 0.25), (CX - HW + 0.1, YT - 0.05)]
        up_r = [(CX + HW - 0.1, YB + 0.25), (CX + HW - 0.1, YT), (SX - 0.7, YT + 0.05), (SX - 0.6, SY + 0.1)]
        st.flow(down, t_in + 0.3, b.end, P.MUD, n=12, speed=1.1, r=0.04, z=0.4)
        st.flow(up_l, t_in + 0.3, b.end, P.MUD, n=10, speed=0.7, r=0.035, z=0.4, alpha=0.7)
        st.flow(up_r, t_in + 0.3, b.end, P.MUD, n=16, speed=0.7, r=0.035, z=0.4, alpha=0.7)
        # cuttings come up with the mud
        t_cut = _w(b, 1, "cuttings")
        st.flow(up_r, t_cut - 0.3, b.end, CUTTING, n=14, speed=0.7, r=0.06, z=0.45, glow=False, alpha=1.0, jitter=0.12)
        st.flow(up_l, t_cut - 0.3, b.end, CUTTING, n=8, speed=0.7, r=0.06, z=0.45, glow=False, alpha=1.0, jitter=0.12)
        cl = _lbl(st, CX + HW + 0.15, 0.6, "cuttings up with the mud", P.TEXT, 0.17, align="l")
        st.fade_in(cl, t_cut, 0.4)
        st.fade_out(cl, s[3] - 0.4, 0.3)

        # UV tray (middle column, top)
        TX, TY, TW, TH = 0.15, 2.05, 4.4, 2.0
        tray = st.rect(TX, TY, TW, TH, UV_BG, 0.1, role="card")
        uv_lab = st.text("UV light box", TX - TW / 2 + 0.2, TY + TH / 2 - 0.22, 0.13, "#b9a6ff", 0.2, align="l", kind="bold")
        chips = []
        glowing = []
        for i in range(16):
            x = TX - 1.8 + (i % 8) * 0.5 + rnd.uniform(-0.12, 0.12)
            y = TY - 0.35 + (i // 8) * 0.7 + rnd.uniform(-0.12, 0.12)
            r = rnd.uniform(0.09, 0.14)
            pts = [(x + r * math.cos(a) * rnd.uniform(0.7, 1.2), y + r * math.sin(a) * rnd.uniform(0.7, 1.2)) for a in
                   [k * 2 * math.pi / 6 for k in range(6)]]
            if i in (2, 5, 9, 12, 14):
                glowing.append((x, y, r))
            chips.append(st.poly(pts, "#3b3430", 0.15, role="flat"))
        t_uv = _w(b, 1, "ultraviolet")
        st.fade_in([tray, uv_lab] + chips, t_uv - 0.3, 0.5)
        t_glow = _w(b, 1, "oil glows")

        def draw_glow(c, t, look):
            a = _clamp((t - t_glow) / 0.8, 0.0, 1.0) * _env(t, t_glow, b.end, 0.0, 0.3)
            if a <= 0:
                return
            fl = 0.85 + 0.15 * math.sin(t * 5.0)
            look.draw_particles(c, [(x, y) for x, y, r in glowing], GLOW, 0.12, a * fl, True)
        st.procedural(t_glow, b.end, 0.3, draw_glow)
        gl = _lbl(st, TX, TY - TH / 2 - 0.32, "under UV light, oil glows", GLOW, 0.18)
        st.fade_in(gl, t_glow, 0.4)

        # gas chromatograph (right, under the term cards)
        c = Chart(st, 3.75, -2.75, 3.75, 2.55, (0.0, 6.0), (0.0, 1.1))
        fr = c.frame(xticks=[], yticks=[], xlabel="retention time  →", grid=False, panel=True)
        ttl = st.text("gas chromatograph", c.X(3.0), 0.38, 0.2, P.GAS, 0.3, kind="bold")
        heights = (1.0, 0.46, 0.27, 0.14, 0.07)
        xs = [i * 0.02 for i in range(301)]
        ys = [0.02 + sum(h * math.exp(-((x - (k + 1.0)) / 0.09) ** 2) for k, h in enumerate(heights)) for x in xs]
        trace = c.curve(xs, ys, P.GAS, 0.04, 0.3)
        t_gc = s[2]
        st.fade_in(fr + [ttl], t_gc - 0.2, 0.4)
        st.draw_on(trace, t_gc + 0.2, t_gc + 2.4)
        for k, h in enumerate(heights):
            pk = st.text(f"C{k + 1}", c.X(k + 1.0), c.Y(h + 0.02) + 0.2, 0.15, P.TEXT, 0.35, kind="bold")
            st.fade_in(pk, t_gc + 0.5 + 0.38 * k, 0.3)
        gm = st.text("methane … pentane", c.X(3.0), c.Y(0.75), 0.14, P.MUTED, 0.35)
        st.fade_in(gm, t_gc + 2.3, 0.4)

        # lag: one tagged cutting rides from the bit to the shaker while the clock runs
        t_a = _w(b, 3, "delay")
        t_b = s[3] + (b.sent_end[3] - s[3]) * 0.93
        lag_path = [(CX + HW - 0.12, YB + 0.3), (CX + HW - 0.12, YT), (SX - 0.7, YT + 0.05), (SX - 0.3, SY + 0.0)]
        seg = [math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(lag_path[:-1], lag_path[1:])]
        Ltot = sum(seg)

        def at(f):
            d = f * Ltot
            for (p, q), L_ in zip(zip(lag_path[:-1], lag_path[1:]), seg):
                if d <= L_:
                    u = d / L_
                    return p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u
                d -= L_
            return lag_path[-1]

        def draw_tag(c, t, look):
            f = _clamp((t - t_a) / (t_b - t_a), 0.0, 1.0)
            x, y = at(f)
            a = _env(t, t_a - 0.3, b.end, 0.3, 0.3)
            look.draw_ring(c, x, y, 0.14, 0.035, P.TEXT, a)
            c.drawCircle(x, y, 0.09, skia.Paint(Color=col(hex_rgb(P.SAND), a), AntiAlias=True))
        st.procedural(t_a - 0.3, b.end, 0.6, draw_tag)
        LX, LY = 0.15, -1.25
        ring = st.ring(LX - 1.45, LY, 0.42, 0.05, P.MUTED, 0.3)
        hand = st.rect(LX - 1.45, LY, 0.05, 0.36, P.TEXT, 0.32, anchor="b")
        st.fade_in([ring, hand], t_a, 0.3)
        st.rotate(hand, t_a, t_b, -360.0, interp="LINEAR")
        cap = st.text("LAG", LX - 0.85, LY + 0.25, 0.14, P.MUTED, 0.35, align="l", kind="bold")
        st.fade_in(cap, t_a, 0.3)
        st.counter(LX - 0.85, LY - 0.12, t_a, t_b, 0, 60, fmt="{:.0f} min", size=0.36, color=P.TEXT, align="l")
        illu = st.text("at 4 km: about an hour (illustrative)", LX - 0.85, LY - 0.55, 0.13, P.MUTED, 0.35, align="l")
        st.fade_in(illu, t_b - 0.6, 0.4)
        t_form = _w(b, 3, "annulus volume")
        form = _lbl(st, LX, -0.18, "lag time = annulus volume ÷ flow rate", P.TEXT, 0.18, kind="mono")
        st.fade_in(form, t_form - 0.2, 0.4)
        t_old = _w(b, 3, "old news")
        old = _lbl(st, LX, -2.65, "cuttings are old news when they arrive", P.WARN, 0.18)
        st.fade_in(old, t_old - 0.1, 0.4)
        st.ripple(SX - 0.3, SY, t_b - 0.1, t_b + 0.5, P.WARN, period=0.6, r0=0.12, r1=0.6)


# ====================================================================================================== 8.03 LWD
def beat_lwd(st, tl):
    b = tl["8.03"]
    s = b.sent
    k = (LY0 - LY1) / (LZ1 - LZ0)            # world units per metre
    OFF = 10.0                               # sensor-to-bit offset shown, m ("a few metres")
    BX = -4.95                               # BHA column
    GX, GW = -4.5, 1.9                       # gamma ray track
    RX, RW = -2.4, 1.9                       # resistivity track
    NX, NW = -0.3, 2.1                       # density-neutron track
    with st.span(b.start, b.end):
        t0 = b.start + 0.1
        t_d0 = s[0] + 2.2
        t_d1 = s[3] + 3.8

        def zs_at(t):
            f = _clamp((t - t_d0) / (t_d1 - t_d0), 0.0, 1.0)
            return LZ0 + (L.Z1 - LZ0) * f

        dl = _depth_labels(st)
        zl = _zoom_link(st, t0, b.end, LZ0, LZ1, LY0, LY1)
        f_gr = _track_frame(st, GX, GW, "gamma ray", CURVE, [(GX, "0"), (GX + GW / 2, "75"), (GX + GW, "150")], "API")
        dec = [0.2, 2, 20, 200]
        Xr = _xmap(RX, RW, 0.2, 200, True)
        f_rt = _track_frame(st, RX, RW, "resistivity", CURVE, [(Xr(v), f"{v:g}") for v in dec], "Ω·m, log scale")
        Xn = _xmap(NX, NW, 0.45, -0.15)
        f_dn = _track_frame(st, NX, NW, "density · neutron", CURVE, [(Xn(v), f"{v:g}") for v in (0.45, 0.15, -0.15)], "porosity")
        leg = [st.rect(NX + 0.35, LY0 + 0.18, 0.3, 0.04, CURVE, 0.1), st.rect(NX + NW - 0.35, LY0 + 0.18, 0.3, 0.04, NEUTRON, 0.1)]
        f_dn[-1].data["s"] = "density      neutron"
        st.fade_in(dl + f_gr + f_rt + f_dn + leg, t0, 0.5)

        # BHA column: the hole grows with the bit; pipe, sensor collar and bit move down together (linear)
        y_s0, y_s1 = Yd(LZ0), Yd(L.Z1)
        hole = st.rect(BX, LY0 + 0.05, 0.5, (LY0 + 0.05) - (y_s0 - OFF * k - 0.12), P.BG, 0.1, anchor="t")
        pipe = st.rect(BX, LY0 + 0.05, 0.13, (LY0 + 0.05) - (y_s0 + 0.25), P.STEEL, 0.2, anchor="t")
        collar = st.rect(BX, y_s0 - OFF * k / 2 + 0.05, 0.26, OFF * k + 0.45, P.STEEL_DK, 0.21)
        sensor = st.rect(BX, y_s0, 0.36, 0.07, P.WARN, 0.23, role="flat")
        bitp = st.poly([(BX - 0.2, y_s0 - OFF * k), (BX + 0.2, y_s0 - OFF * k), (BX + 0.1, y_s0 - OFF * k - 0.14), (BX - 0.1, y_s0 - OFF * k - 0.14)],
                       P.STEEL, 0.22)
        bha = [hole, pipe, collar, sensor, bitp]
        st.fade_in(bha, t0, 0.5)
        dz = y_s1 - y_s0
        st.move([collar, sensor, bitp], t_d0, t_d1, dy=dz, interp="LINEAR")
        st.scale_to(hole, t_d0, t_d1, sy=(LY0 + 0.05) - (y_s1 - OFF * k - 0.12), interp="LINEAR")
        st.scale_to(pipe, t_d0, t_d1, sy=(LY0 + 0.05) - (y_s1 + 0.25), interp="LINEAR")
        # a hairline at the sensor depth across the tracks (the "reading front")
        def draw_front(c, t, look):
            if t < t_d0 or t > t_d1 + 0.6:
                return
            y = Yd(zs_at(t))
            a = 0.55 * _env(t, t_d0, t_d1 + 0.6, 0.3, 0.6)
            _stroke(c, look, [(BX + 0.2, y), (NX + NW, y)], P.WARN, 0.015, a, dash=(0.06, 0.06))
        st.procedural(t_d0, t_d1 + 0.6, 0.5, draw_front)

        # emphasis: each track is bright while it is discussed, dim otherwise (after the first pass)
        t_gr, t_rt, t_dn = s[1], s[2], s[3]
        a_gr = _alpha_track([(t_gr - 0.3, 1.0), (t_rt - 0.2, 1.0), (t_rt + 0.3, 0.35), (s[4] - 0.3, 0.35), (s[4] + 0.3, 1.0)])
        a_rt = _alpha_track([(t_gr - 0.3, 1.0), (t_gr + 0.2, 0.35), (t_rt - 0.2, 0.35), (t_rt + 0.3, 1.0), (t_dn - 0.2, 1.0),
                             (t_dn + 0.3, 0.35), (s[4] - 0.3, 0.35), (s[4] + 0.3, 1.0)])
        a_dn = _alpha_track([(t_gr - 0.3, 1.0), (t_gr + 0.2, 0.35), (t_dn - 0.2, 0.35), (t_dn + 0.3, 1.0)])
        Xg = _xmap(GX, GW, 0, 150)
        _log_curve(st, LG.gr, LG.z, Xg, CURVE, 0.035, t0, b.end, zs_at, a_gr)
        _log_curve(st, LG.rt, LG.z, Xr, CURVE, 0.035, t0, b.end, zs_at, a_rt)
        _log_curve(st, LG.dphi, LG.z, Xn, CURVE, 0.035, t0, b.end, zs_at, a_dn)
        _log_curve(st, LG.nphi, LG.z, Xn, NEUTRON, 0.035, t0, b.end, zs_at, a_dn)

        # sensors a few metres behind the bit
        t_sens = _w(b, 0, "sensors")
        br = st.line([(BX + 0.42, y_s0 - 0.02), (BX + 0.52, y_s0 - 0.02), (BX + 0.52, y_s0 - OFF * k - 0.12), (BX + 0.42, y_s0 - OFF * k - 0.12)],
                     P.WARN, 0.025, 0.4, role="hair")

        # BHA detail on the right
        DX = 3.0
        det = [st.rect(DX, 0.78, 0.2, 0.5, P.STEEL, 0.2),
               st.rect(DX, 0.27, 0.42, 0.55, P.STEEL_DK, 0.21),
               st.rect(DX, -1.22, 0.42, 2.45, P.STEEL, 0.2),
               st.poly([(DX - 0.24, -2.45), (DX + 0.24, -2.45), (DX + 0.13, -2.85), (DX - 0.13, -2.85)], P.STEEL_DK, 0.22)]
        bands = {"rt": [st.rect(DX, -0.35, 0.5, 0.06, CURVE, 0.25, role="flat"), st.rect(DX, -0.6, 0.5, 0.06, CURVE, 0.25, role="flat")],
                 "gr": [st.rect(DX, -1.15, 0.5, 0.1, CURVE, 0.25, role="flat")],
                 "dn": [st.rect(DX, -1.85, 0.5, 0.1, CURVE, 0.25, role="flat")]}
        labs = {"rt": st.text("resistivity", DX + 0.45, -0.47, 0.17, P.MUTED, 0.3, align="l", kind="bold"),
                "gr": st.text("gamma ray", DX + 0.45, -1.15, 0.17, P.MUTED, 0.3, align="l", kind="bold"),
                "dn": st.text("density · neutron", DX + 0.45, -1.85, 0.17, P.MUTED, 0.3, align="l", kind="bold")}
        dbr = st.line([(DX + 0.32, -1.95), (DX + 0.42, -1.95), (DX + 0.42, -2.85), (DX + 0.32, -2.85)], P.WARN, 0.025, 0.4, role="hair")
        dbl = st.text("a few metres", DX + 0.55, -2.4, 0.16, P.WARN, 0.4, align="l", kind="bold")
        cap = st.text("LWD TOOL", DX, 1.25, 0.14, P.MUTED, 0.3, kind="bold")
        st.fade_in(det + bands["rt"] + bands["gr"] + bands["dn"] + list(labs.values()) + [cap], t0 + 0.3, 0.5)
        st.fade_in([dbr, dbl, br], t_sens, 0.4)
        sens_l = _lbl(st, DX + 0.1, -3.3, "sensors read the rock minutes after it is cut", P.TEXT, 0.16)
        st.fade_in(sens_l, _w(b, 0, "reading"), 0.4)
        st.fade_out(sens_l, s[1] - 0.3, 0.3)
        for key, tt, te in (("gr", t_gr, t_rt), ("rt", t_rt, t_dn), ("dn", t_dn, s[4])):
            st.recolor(bands[key], tt - 0.1, tt + 0.3, P.WARN)
            st.recolor(labs[key], tt - 0.1, tt + 0.3, P.TEXT)
            st.recolor(bands[key], te - 0.2, te + 0.2, CURVE)
            st.recolor(labs[key], te - 0.2, te + 0.2, P.MUTED)

        # gamma ray: shale vs sand
        sand_runs, run = [], None
        for zz in LG.z:
            sd = L.is_sand(zz)
            if sd and run is None:
                run = zz
            if not sd and run is not None:
                sand_runs.append((run, zz))
                run = None
        if run is not None:
            sand_runs.append((run, LG.z[-1]))
        shade = [st.rect(GX + GW / 2, (Yd(a) + Yd(c_)) / 2, GW, abs(Yd(a) - Yd(c_)), P.SAND, 0.08, alpha=0.2, role="flat")
                 for a, c_ in sand_runs]
        st.fade_in(shade, _w(b, 1, "separates") - 0.2, 0.5)
        sh_l = _lbl(st, GX + 0.5, Yd(3938), "shale", P.MUTED, 0.16)
        sd_l = _lbl(st, GX + GW - 0.5, Yd(4030), "sand", P.SAND, 0.16)
        st.fade_in(sh_l, _w(b, 1, "shale"), 0.3)
        st.fade_in(sd_l, _w(b, 1, "sand"), 0.3)
        st.fade(sh_l + sd_l, t_rt + 0.3, t_rt + 0.6, 1.0, 0.45)
        # resistivity: hydrocarbons high, water low
        hc = _lbl(st, RX + 0.52, Yd(4005), "oil or gas", P.TEXT, 0.16)
        wl = _lbl(st, RX + RW - 0.48, Yd(4085), "water", P.WATER, 0.16)
        st.fade_in(hc, _w(b, 2, "high resistivity"), 0.35)
        st.fade_in(wl, _w(b, 2, "high resistivity") + 0.5, 0.35)
        st.fade(hc + wl, t_dn + 0.3, t_dn + 0.6, 1.0, 0.45)
        # density-neutron: porosity, then the gas crossover
        gas_pts = [(zz, d, n) for zz, d, n in zip(LG.z, LG.dphi, LG.nphi) if M.RES_TOP <= zz < M.GOC and L.is_sand(zz)]
        poly = [(Xn(d), Yd(zz)) for zz, d, n in gas_pts] + [(Xn(n), Yd(zz)) for zz, d, n in reversed(gas_pts)]
        t_x = _w(b, 3, "cross over")

        def draw_cross(c, t, look):
            a = _clamp((t - t_x) / 0.6, 0.0, 1.0) * _env(t, t_x, b.end, 0.0, 0.3)
            _fill(c, poly, P.GAS, 0.55 * a)
        st.procedural(t_x, b.end, 0.28, draw_cross)
        phl = _lbl(st, NX + NW - 0.55, Yd(4025), "φ ≈ 0.23", P.TEXT, 0.16)
        st.fade_in(phl, _w(b, 3, "pore space") - 0.3, 0.35)
        gl = _lbl(st, NX + NW - 0.45, Yd(3968), "gas", P.GAS, 0.18)
        st.fade_in(gl, _w(b, 3, "signature"), 0.35)
        st.ripple(NX + 0.5, Yd(3968), _w(b, 3, "signature"), _w(b, 3, "signature") + 1.2, P.GAS, period=0.6, r0=0.1, r1=0.6)

        # telemetry: pulses climb the pipe; at surface a thin stream; the full log stays in memory
        t_tel = s[4]

        def draw_pulses(c, t, look):
            a = _env(t, t_tel, b.end, 0.4, 0.3)
            if a <= 0:
                return
            ys_ = Yd(L.Z1) + 0.2
            for kk in range(8):
                yy = ys_ + ((t - t_tel) * 1.6 + kk * 0.8) % (LY0 - ys_)
                look.draw_particles(c, [(BX, yy)], P.MUD, 0.05, a, True)
            for kk in range(3):
                yy = 0.55 + ((t - t_tel) * 0.9 + kk * 0.33) % 0.5
                look.draw_particles(c, [(DX, yy)], P.MUD, 0.05, a, True)
        st.procedural(t_tel, b.end, 0.45, draw_pulses)
        pl = st.text("MWD pulser", DX + 0.45, 0.27, 0.17, P.MUD, 0.3, align="l", kind="bold")
        st.fade_in(pl, t_tel, 0.4)
        card = st.rect(5.5, 2.55, 4.25, 2.3, P.PANEL, 0.3)
        ttl = st.text("AT SURFACE: pressure pulses in the mud", 3.6, 3.43, 0.13, P.MUTED, 0.35, align="l", kind="bold")
        st.fade_in([card, ttl], t_tel + 0.2, 0.4)
        bits = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1]
        TX0, TX1, TYL, TYH = 3.7, 7.35, 2.0, 2.9

        def draw_trace(c, t, look):
            a = _env(t, t_tel + 0.3, b.end, 0.4, 0.3)
            if a <= 0:
                return
            bw = 0.36
            off = (t - t_tel) * 0.72          # 2 bits per second scroll
            pts = []
            x = TX0
            while x <= TX1:
                idx = int((x - TX0 + off) / bw)
                v = bits[idx % len(bits)]
                y = TYH if v else TYL
                if pts and pts[-1][1] != y:
                    pts.append((x, pts[-1][1]))
                pts.append((x, y))
                x += 0.02
            _stroke(c, look, pts, P.MUD, 0.035, a, glow=True)
        st.procedural(t_tel + 0.3, b.end, 0.4, draw_trace)
        rate = _lbl(st, 5.5, 1.67, "a few bits per second", P.MUD, 0.17, z=0.45)
        st.fade_in(rate, _w(b, 4, "a few bits"), 0.4)
        t_mem = _w(b, 4, "memory")
        chip = [st.rect(DX + 0.75, -3.25, 0.36, 0.3, P.PANEL2, 0.4, role="card")]
        for kk in range(3):
            chip += [st.rect(DX + 0.65 + 0.1 * kk, -3.07, 0.03, 0.08, P.STEEL, 0.41), st.rect(DX + 0.65 + 0.1 * kk, -3.43, 0.03, 0.08, P.STEEL, 0.41)]
        chip_l = st.text("full log waits in the tool's memory", DX + 1.05, -3.25, 0.16, P.TEXT, 0.4, align="l", kind="bold")
        st.fade_in(chip + [chip_l], t_mem - 0.3, 0.4)


# ====================================================================================================== 8.04 Archie
def beat_archie(st, tl):
    b = tl["8.04"]
    s = b.sent
    ex = L.archie_example()
    SX0, SX1, SY0, SY1 = -5.85, -0.75, -2.15, 1.95
    with st.span(b.start, b.end):
        t0 = s[1] - 0.2
        brine = st.rect((SX0 + SX1) / 2, (SY0 + SY1) / 2, SX1 - SX0, SY1 - SY0, P.WATER, 0.05, alpha=0.8)
        grains = []
        rows, dy_ = 5, (SY1 - SY0) / 5
        chan_y = []
        for j in range(rows):
            y = SY0 + dy_ * (j + 0.5)
            off = 0.0 if j % 2 == 0 else 0.37
            x = SX0 + 0.37 + off
            while x < SX1 - 0.2:
                grains.append(st.circle(x, y, 0.33, P.SAND, 0.1, role="disc"))
                x += 0.74
            if j < rows - 1:
                chan_y.append(y + dy_ / 2)
        el_l = st.rect(SX0 - 0.1, (SY0 + SY1) / 2, 0.14, SY1 - SY0 + 0.2, P.STEEL, 0.2)
        el_r = st.rect(SX1 + 0.1, (SY0 + SY1) / 2, 0.14, SY1 - SY0 + 0.2, P.STEEL, 0.2)
        AX, AY = (SX0 + SX1) / 2, -3.0
        wires = [st.line([(SX0 - 0.1, SY0 - 0.1), (SX0 - 0.1, AY), (AX - 0.45, AY)], P.STEEL_DK, 0.03, 0.15, role="hair"),
                 st.line([(SX1 + 0.1, SY0 - 0.1), (SX1 + 0.1, AY), (AX + 0.45, AY)], P.STEEL_DK, 0.03, 0.15, role="hair")]
        meter = [st.circle(AX, AY, 0.45, P.PANEL2, 0.2, role="disc"), st.ring(AX, AY, 0.45, 0.04, P.MUTED, 0.21)]
        needle = st.rect(AX, AY, 0.36, 0.04, P.TEXT, 0.25, anchor="l", rot=170)
        a_l = st.text("A", AX, AY - 0.22, 0.14, P.MUTED, 0.25, kind="bold")
        cap = _lbl(st, (SX0 + SX1) / 2, 2.5, "rock ≈ a sponge soaked in salty water", P.TEXT, 0.19)
        st.fade_in([brine] + grains, t0, 0.6)
        st.fade_in(cap, s[1] + 0.2, 0.4)
        st.fade_in([el_l, el_r] + wires + meter + [needle, a_l], s[2] - 0.4, 0.4)
        # current through the brine channels
        t_cur = s[2]
        t_oil = _w(b, 3, "oil")
        blocked = (0, 2)
        for i, y in enumerate(chan_y):
            pts = [(SX0, y), (SX1, y)]
            if i in blocked:
                st.flow(pts, t_cur, t_oil + 0.6, ELEC, n=8, speed=1.3, r=0.04, z=0.4)
            else:
                st.flow(pts, t_cur, b.end, ELEC, n=8, speed=1.3, r=0.04, z=0.4)
        st.rotate(needle, t_cur + 0.2, t_cur + 1.0, 40)
        cl = _lbl(st, (SX0 + SX1) / 2, SY0 - 0.32, "current flows through the salt water", P.TEXT, 0.17)
        st.fade_in(cl, t_cur + 0.3, 0.4)
        st.fade_out(cl, t_oil - 0.2, 0.3)
        # oil replaces some water and blocks paths
        oils = []
        for i in blocked:
            y = chan_y[i]
            for x in (SX0 + 1.1, SX0 + 2.6, SX0 + 4.0):
                oils.append(st.ellipse(x, y, 0.42, 0.2, P.OIL, 0.3))
        for x, y in ((SX0 + 1.85, chan_y[1] + 0.02), (SX0 + 3.3, chan_y[3] - 0.02)):
            oils.append(st.ellipse(x, y, 0.2, 0.12, P.OIL, 0.3))
        for i, o in enumerate(oils):
            st.pop_in(o, t_oil + 0.1 * i, 0.4)
        st.rotate(needle, t_oil + 0.6, t_oil + 1.6, 125)
        ol = _lbl(st, (SX0 + SX1) / 2, SY0 - 0.32, "oil is an insulator: fewer paths, less current", P.OIL, 0.17)
        st.fade_in(ol, _w(b, 3, "less current") - 0.2, 0.4)
        st.fade_out(ol, s[5] - 0.3, 0.3)

        # equation card
        CXc, CYc, CWc, CHc = 3.95, -0.5, 7.3, 5.55
        card = st.rect(CXc, CYc, CWc, CHc, P.PANEL, 0.1)
        kick = st.text("ARCHIE'S EQUATION", CXc - CWc / 2 + 0.3, CYc + CHc / 2 - 0.3, 0.14, P.MUTED, 0.2, align="l", kind="bold")
        t_eq = s[4]
        st.fade_in([card, kick], t_eq - 0.3, 0.4)
        FY = 1.15
        sw = st.text("Sw", 1.25, FY, 0.42, P.WATER, 0.3, kind="bold")
        eq = st.text("=", 1.95, FY, 0.4, P.TEXT, 0.3)
        lp = st.text("(", 2.4, FY, 0.95, P.MUTED, 0.3)
        num = st.text("a · Rw", 3.55, FY + 0.38, 0.32, P.TEXT, 0.3, kind="mono")
        rule = st.rect(3.55, FY, 2.0, 0.035, P.TEXT, 0.3)
        den = st.text("φ  · Rt", 3.55, FY - 0.4, 0.32, P.TEXT, 0.3, kind="mono")
        sup = st.text("m", 3.05, FY - 0.24, 0.17, P.TEXT, 0.31, kind="mono")
        rp = st.text(")", 4.7, FY, 0.95, P.MUTED, 0.3)
        ex_ = st.text("1/n", 5.15, FY + 0.5, 0.2, P.TEXT, 0.3, kind="mono")
        st.fade_in([sw, eq, lp, num, rule, den, sup, rp, ex_], t_eq, 0.5)
        legend = [("Sw", "water saturation", P.WATER, _w(b, 4, "water saturation")),
                  ("φ", "porosity", P.TEXT, _w(b, 4, "porosity")),
                  ("Rt", "measured resistivity", P.TEXT, _w(b, 4, "measured resistivity")),
                  ("Rw", "the salt water's own resistivity", P.TEXT, _w(b, 4, "salt water"))]
        for i, (sym, txt, colr, t) in enumerate(legend):
            y = 0.05 - 0.42 * i
            a = st.text(sym, 1.0, y, 0.2, colr, 0.3, align="l", kind="mono")
            bb = st.text(txt, 1.75, y, 0.18, P.MUTED if i else P.TEXT, 0.3, align="l", kind="bold")
            st.fade_in([a, bb], t - 0.15, 0.35)
        # worked example from the model (gas leg of our well)
        t_ex = b.sent_end[4] - 1.2
        exl = st.text(f"our gas leg:   Rw {ex['rw']:.2f} Ω·m   φ {ex['phi']:.2f}   Rt {ex['rt']:.1f} Ω·m", 0.6, -1.85, 0.16, P.TEXT, 0.3,
                      align="l", kind="mono")
        exa = st.text("a = 1,  m = n = 2", 0.6, -2.25, 0.14, P.MUTED, 0.3, align="l", kind="mono")
        st.fade_in([exl, exa], t_ex, 0.4)
        res_l = st.text("Sw ≈", 0.6, -2.85, 0.3, P.WATER, 0.3, align="l", kind="bold")
        st.fade_in(res_l, t_ex + 0.6, 0.3)
        st.counter(1.55, -2.85, t_ex + 0.6, t_ex + 1.8, 1.0, ex["sw"], fmt="{:.2f}", size=0.3, color=P.WATER, align="l")
        gas_l = st.text(f"→  {100 * (1 - ex['sw']):.0f} % of the pores hold gas", 2.75, -2.85, 0.2, P.GAS, 0.3, align="l", kind="bold")
        st.fade_in(gas_l, t_ex + 1.9, 0.4)
        # shaly sands: clay conducts too
        t_sh = s[5]
        rnd = random.Random(5)
        clays = []
        for _ in range(9):
            x = rnd.uniform(SX0 + 0.4, SX1 - 0.4)
            y = rnd.choice(chan_y) + rnd.choice((-0.13, 0.13))
            clays.append(st.rect(x, y, 0.32, 0.06, CLAY, 0.32, rot=rnd.uniform(-12, 12), role="flat"))
        st.fade_in(clays, _w(b, 5, "clays"), 0.5)
        for i in blocked:
            st.flow([(SX0, chan_y[i] + 0.13), (SX1, chan_y[i] + 0.13)], _w(b, 5, "conduct"), b.end, CLAY, n=6, speed=0.7, r=0.03, z=0.41)
        sh = _lbl(st, (SX0 + SX1) / 2, SY0 - 0.32, "clays conduct too: shaly sands need extended models", P.WARN, 0.16)
        st.fade_in(sh, _w(b, 5, "shaly") - 0.2, 0.4)


# ====================================================================================================== 8.05 gradients
class View:
    """A camera for the drawing only (copied from ch03): objects / procedurals made inside `with view:` are drawn through
    screen = world * s + d, clipped, so the header, strip and term cards stay put while the drawing pushes in."""

    def __init__(self, st, t0, t1, z=0.2, clip=(-6.32, -3.7, 8.0, 3.93)):
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
        at = focus if at is None else at
        s1, dx1, dy1 = scale, at[0] - focus[0] * scale, at[1] - focus[1] * scale
        s0, dx0, dy0 = self.cur
        for tr, a, b in ((self.ts, s0, s1), (self.tx, dx0, dx1), (self.ty, dy0, dy1)):
            tr.set(t0, a, interp)
            tr.set(t1, b, interp)
        self.cur = (s1, dx1, dy1)

    def home(self, t0, t1):
        self.camera(t0, t1, (0.0, 0.0), (0.0, 0.0), 1.0)

    def _draw(self, c, t, look):
        s = self.ts.eval(t) if self.ts else 1.0
        dx = self.tx.eval(t) if self.tx else 0.0
        dy = self.ty.eval(t) if self.ty else 0.0
        M0, k0 = look.M, look.k
        Lm = skia.Matrix()
        Lm.setAll(s, 0, dx, 0, s, dy, 0, 0, 1)
        M1 = skia.Matrix.Concat(M0, Lm)
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


def beat_gradients(st, tl):
    b = tl["8.05"]
    s = b.sent
    pts = FIT["points"]
    colors = {"gas": P.GAS, "oil": P.OIL, "water": P.WATER}
    fn = {"gas": L.p_gas, "oil": L.p_oil, "water": L.p_water}
    with st.span(b.start, b.end):
        view = View(st, b.start, b.end, z=0.2, clip=(-6.32, -3.7, 3.85, 3.93))
        with view:
            c = Chart(st, -2.2, -2.9, 5.4, 6.1, (598.0, 614.0), (3935.0, 4120.0), invert_y=True)
            fr = c.frame(xticks=[600, 604, 608, 612], yticks=[3950, 4000, 4050, 4100], xlabel="formation pressure (bar)",
                         ylabel="depth (m)", fx="{:g}", panel=False, tick_size=0.17)
            # borehole cutaway on the left, on the same depth scale
            HX0, HX1 = -5.2, -4.45
            Yc = c.Y
            ytop, ybot = 3.75, Yc(4120)
            rock = [st.rect(-5.7, (ytop + Yc(M.RES_TOP)) / 2, 1.0, ytop - Yc(M.RES_TOP), P.SHALE, 0.0),
                    st.rect(-3.95, (ytop + Yc(M.RES_TOP)) / 2, 1.0, ytop - Yc(M.RES_TOP), P.SHALE, 0.0),
                    st.rect(-5.7, (Yc(M.RES_TOP) + Yc(M.RES_BASE)) / 2, 1.0, Yc(M.RES_TOP) - Yc(M.RES_BASE), P.SAND, 0.0),
                    st.rect(-3.95, (Yc(M.RES_TOP) + Yc(M.RES_BASE)) / 2, 1.0, Yc(M.RES_TOP) - Yc(M.RES_BASE), P.SAND, 0.0),
                    st.rect(-5.7, (Yc(M.RES_BASE) + ybot) / 2, 1.0, Yc(M.RES_BASE) - ybot, P.SHALE, 0.0),
                    st.rect(-3.95, (Yc(M.RES_BASE) + ybot) / 2, 1.0, Yc(M.RES_BASE) - ybot, P.SHALE, 0.0)]
            hole = st.rect((HX0 + HX1) / 2, (ytop + ybot) / 2, HX1 - HX0, ytop - ybot, P.BG, 0.02)
            mudf = st.rect((HX0 + HX1) / 2, (ytop + ybot) / 2, HX1 - HX0, ytop - ybot, P.MUD, 0.03, alpha=0.18, role="flat")
            res_l = st.text("reservoir", -3.95, Yc(4030), 0.14, "#5b4a2a", 0.05, kind="bold")
            st.fade_in(rock + [hole, mudf, res_l], b.start + 0.1, 0.5)
            # the wireline tool: cable + body + probe pad + back-up arm
            TXc = (HX0 + HX1) / 2
            z_park = 3925.0
            cable = st.rect(TXc, ytop, 0.025, ytop - (Yc(z_park) + 0.45), P.STEEL, 0.3, anchor="t")
            body = st.rect(TXc, Yc(z_park), 0.3, 0.9, P.STEEL, 0.32)
            pad = st.rect(TXc + 0.15, Yc(z_park), 0.06, 0.24, P.WARN, 0.33, anchor="l")
            arm = st.rect(TXc - 0.15, Yc(z_park) - 0.2, 0.05, 0.05, P.STEEL_DK, 0.31, anchor="r")
            tool = [body, pad, arm]
            st.fade_in([cable] + tool, s[0], 0.4)

            def tool_to(z, t0_, t1_):
                st.move(tool, t0_, t1_, dy=Yc(z) - st.state[body]["loc"][1])
                st.scale_to(cable, t0_, t1_, sy=ytop - (Yc(z) + 0.45))
            # log run on the cable: down through the reservoir and back up to the first station
            t_dn0, t_dn1 = s[0] + 0.8, s[1] - 0.2
            tool_to(4112, t_dn0, t_dn1)
            st.ripple(TXc, Yc(4112), t_dn1 - 0.1, t_dn1 + 0.5, P.TEXT, period=0.5, r0=0.1, r1=0.5)

            st.fade_in(fr, s[1] - 0.2, 0.5)
            # pressure stations
            t_st0 = _w(b, 2, "presses") - 0.15
            t_wat = _w(b, 3, "water,")
            dt = (t_wat - 0.5 - t_st0) / (len(pts) - 1)
            dots = {"gas": [], "oil": [], "water": []}
            prev_t = t_st0 - 1.2
            tool_to(pts[0][1], prev_t, t_st0 - 0.1)
            for i, (fl, z, p) in enumerate(pts):
                t = t_st0 + dt * i
                if i:
                    tool_to(z, t - dt + 0.75, t - 0.1)
                st.scale_to(pad, t, t + 0.2, sx=HX1 - (TXc + 0.15) - 0.06)
                st.scale_to(arm, t, t + 0.2, sx=(TXc - 0.15) - HX0)
                st.scale_to(pad, t + 0.65, t + 0.8, sx=0.06)
                st.scale_to(arm, t + 0.65, t + 0.8, sx=0.05)
                d = st.circle(c.X(p), c.Y(z), 0.09, colors[fl], 0.5)
                st.pop_in(d, t + 0.3, 0.3)
                dots[fl].append(d)
                guide = st.dashed((HX1 + 0.05, c.Y(z)), (c.X(p) - 0.12, c.Y(z)), P.MUTED, 0.018, 0.08, 0.07, 0.15)
                st.fade_in(guide, t + 0.2, 0.15)
                st.fade_out(guide, t + 0.9, 0.3)
            tl_ = _lbl(st, -0.85, Yc(3943) - 0.02, "probe pressed on the rock", P.WARN, 0.15)
            st.fade_in(tl_, t_st0 + 0.2, 0.3)
            st.fade_out(tl_, t_st0 + 2.6, 0.3)
            # fitted lines (model gradients), solid over their data
            legs = {"gas": (3955, 3984), "oil": (3996, 4042), "water": (4068, 4108)}
            lines = {}
            for fl in ("gas", "oil", "water"):
                z0, z1 = legs[fl]
                ln = st.line([c.pt(fn[fl](z0 - 4), z0 - 4), c.pt(fn[fl](z1 + 4), z1 + 4)], colors[fl], 0.055, 0.4)
                t = _w(b, 3, fl + ",") - 0.1
                st.draw_on(ln, t, t + 0.8, "BEZIER")
                lines[fl] = ln
            # extrapolations to the crossings: GOC (gas/oil) and FWL (oil/water)
            t_gx = s[4] + 0.6
            gx = [st.line([c.pt(L.p_gas(3988), 3988), c.pt(L.p_gas(3998), 3998)], P.GAS, 0.03, 0.38, role="dash"),
                  st.line([c.pt(L.p_oil(3992), 3992), c.pt(L.p_oil(3982), 3982)], P.OIL, 0.03, 0.38, role="dash")]
            st.draw_on(gx, t_gx, t_gx + 0.6)
            gpt = (c.X(L.p_oil(M.GOC)), c.Y(M.GOC))
            gring = st.ring(gpt[0], gpt[1], 0.13, 0.035, P.TEXT, 0.5)
            st.pop_in(gring, t_gx + 0.5, 0.3)
            goc = _lbl(st, gpt[0] + 0.3, gpt[1] + 0.02, f"gas-oil contact  {M.GOC:,.0f} m", P.TEXT, 0.16, align="l")
            st.fade_in(goc, t_gx + 0.6, 0.35)
            t_meet = _w(b, 5, "meets")
            ox = st.line([c.pt(L.p_oil(4042), 4042), c.pt(L.p_oil(4064), 4064)], P.OIL, 0.035, 0.38)
            wx = st.line([c.pt(L.p_water(4068), 4068), c.pt(L.p_water(4040), 4040)], P.WATER, 0.035, 0.38)
            ox.data["_role"] = "dash"
            wx.data["_role"] = "dash"
            st.draw_on([ox, wx], t_meet - 0.3, t_meet + 0.6)
            fpt = (c.X(L.p_water(M.FWL)), c.Y(M.FWL))
            fring = st.ring(fpt[0], fpt[1], 0.16, 0.04, P.TEXT, 0.5)
            st.pop_in(fring, t_meet + 0.5, 0.3)
            fwl_line = st.dashed((HX0 - 0.95, fpt[1]), (fpt[0] - 0.2, fpt[1]), P.TEXT, 0.022, 0.12, 0.08, 0.36)
            st.fade_in(fwl_line, t_meet + 0.7, 0.4)
            fwl = _lbl(st, fpt[0] - 0.25, fpt[1] - 0.38, f"free-water level  {FIT['fwl']:,.0f} m", P.TEXT, 0.18, align="r", bg=P.PANEL2)
            st.fade_in(fwl, t_meet + 0.8, 0.4)
            alone = st.text("from pressures alone", fpt[0] - 0.25, fpt[1] - 0.8, 0.14, P.MUTED, 0.5, align="r")
            st.fade_in(alone, _w(b, 5, "pressures alone") - 0.2, 0.4)
            st.ripple(fpt[0], fpt[1], t_meet + 0.5, t_meet + 2.0, P.TEXT, period=0.7, r0=0.15, r1=0.7)

            # the well crossed it: water stations pulse; then the ghost example
            t_cr = _w(b, 6, "crossed")
            for d in dots["water"]:
                x, y, _ = st.state[d]["loc"]
                st.ripple(x, y, t_cr, t_cr + 1.0, P.WATER, period=0.5, r0=0.08, r1=0.4)
            crl = _lbl(st, TXc, Yc(4090), "our well:\nwater below", P.WATER, 0.14, z=0.6)
            st.fade_in(crl, t_cr, 0.3)
            t_gh = _w(b, 6, "never reached") - 0.2
            st.fade_out(crl, t_gh - 0.2, 0.3)
            st.fade(dots["water"] + [lines["water"], wx], t_gh, t_gh + 0.6, 1.0, 0.18)
            # a well that stops in the oil: hole below 4,046 m greyed out
            plug = st.rect((HX0 + HX1) / 2, (Yc(4046) + ybot) / 2, HX1 - HX0 + 0.02, Yc(4046) - ybot, P.SHALE, 0.35, alpha=0.92)
            st.fade_in(plug, t_gh, 0.5)
            stop = _lbl(st, TXc, Yc(4085), "another well:\nstops in oil", P.MUTED, 0.14, z=0.6)
            st.fade_in(stop, t_gh + 0.2, 0.4)
            t_nb = _w(b, 6, "neighbouring")
            nb_z = (4074, 4092, 4110)
            nbs = [st.ring(c.X(L.p_water(z)), c.Y(z), 0.1, 0.035, P.WATER, 0.5) for z in nb_z]
            for i, o in enumerate(nbs):
                st.pop_in(o, t_nb - 1.2 + 0.25 * i, 0.3)
            nbl = st.line([c.pt(L.p_water(4115), 4115), c.pt(L.p_water(4044), 4044)], P.WATER, 0.035, 0.4)
            nbl.data["_role"] = "dash"
            st.draw_on(nbl, t_nb - 0.4, t_nb + 0.6)
            nbt = _lbl(st, c.X(L.p_water(4100)) - 0.35, c.Y(4100), "water line from a neighbouring well", P.WATER, 0.15, align="r")
            st.fade_in(nbt, t_nb, 0.4)
            st.ripple(fpt[0], fpt[1], t_nb + 0.6, b.end, P.TEXT, period=0.9, r0=0.15, r1=0.7)
        # push in on the crossing while the FWL is explained, back out for the last sentence
        view.camera(t_meet - 0.6, t_meet + 1.2, focus=fpt, at=(fpt[0] + 0.2, fpt[1] + 0.3), scale=1.28)
        view.camera(s[6] - 0.4, s[6] + 0.8, focus=fpt, at=fpt, scale=1.0)

        # gradient legend (right, below the term cards)
        gtxt = {"gas": "gas     ≈ 0.25 bar per 10 m", "oil": "oil     ≈ 0.75 bar per 10 m", "water": "water  ≈ 1.0 bar per 10 m"}
        gsub = {"gas": L.G_GAS, "oil": L.G_OIL, "water": L.G_WATER}
        for i, fl in enumerate(("gas", "oil", "water")):
            y = 0.35 - 0.95 * i
            g = _lbl(st, 4.05, y, gtxt[fl], colors[fl], 0.18, align="l", z=0.6)
            sub = st.text(f"{gsub[fl]:.3f} bar/m", 4.25, y - 0.38, 0.14, P.MUTED, 0.6, align="l", kind="mono")
            t = _w(b, 3, fl + ",") - 0.2
            st.fade_in(g + [sub], t, 0.35)
        sd = _lbl(st, 5.8, -2.55, "slope = weight of the fluid", P.TEXT, 0.17, z=0.6)
        st.fade_in(sd, _w(b, 4, "slopes differ") - 0.2, 0.4)


# ====================================================================================================== 8.06 samples, compartments, contacts
def beat_samples(st, tl):
    b = tl["8.06"]
    s = b.sent
    with st.span(b.start, b.end):
        t0 = b.start + 0.1
        kick = [st.text("SAMPLES", -4.35, 3.5, 0.15, P.MUTED, 0.3, kind="bold"),
                st.text("COMPARTMENTS", 0.05, 3.5, 0.15, P.MUTED, 0.3, kind="bold"),
                st.text("CONTACTS", 5.2, 3.5, 0.15, P.MUTED, 0.3, kind="bold")]
        # ---- A: sampling tool
        TX = -5.0
        sand = st.rect(-5.95, 0.0, 0.5, 6.4, P.SAND, 0.0)
        oilt = st.rect(-5.95, 0.0, 0.5, 6.4, P.OIL, 0.01, alpha=0.25, role="flat")
        body = st.rect(TX, 0.05, 0.8, 6.3, P.STEEL, 0.1)
        probe = st.rect(-5.5, 1.6, 0.22, 0.34, P.STEEL_DK, 0.15)
        bore = st.rect(TX + 0.05, -0.05, 0.08, 3.3, P.BG, 0.12)
        opt = st.rect(TX + 0.05, 0.75, 0.42, 0.42, P.PANEL2, 0.14, role="card")
        win = st.rect(TX + 0.05, 0.75, 0.2, 0.2, "#7fd1ff", 0.15, alpha=0.6, role="flat")
        bottle = st.rect(TX + 0.05, -2.2, 0.5, 1.5, P.PANEL2, 0.13, role="card")
        fill = st.rect(TX + 0.05, -2.9, 0.4, 0.0001, P.OIL, 0.14, anchor="b")
        st.fade_in(kick[:1] + [sand, oilt, body, probe, bore, opt, win, bottle], t0, 0.5)
        st.fade_in(kick[1:], t0, 0.5)
        t_pump = _w(b, 0, "pumps")
        st.fade_in(fill, t_pump, 0.2)
        st.scale_to(fill, t_pump + 0.4, s[1], sy=1.3)
        st.flow([(-5.95, 1.6), (TX + 0.05, 1.6), (TX + 0.05, -1.45)], t_pump - 0.2, s[1] + 0.6, P.OIL, n=12, speed=1.2, r=0.04, z=0.3)
        # optical dial
        DX, DY = -3.45, 1.05
        dial = [st.circle(DX, DY, 0.62, P.PANEL2, 0.2, role="disc")]
        for a0, a1, colr in ((180, 120, P.WATER), (120, 60, P.OIL), (60, 0, P.GAS)):
            dial.append(st.line(_arc(DX, DY, 0.5, a0, a1, 16), colr, 0.07, 0.22))
        ndl = st.rect(DX, DY, 0.44, 0.04, P.TEXT, 0.25, anchor="l", rot=170)
        lead = st.line([(TX + 0.3, 0.75), (DX - 0.65, DY - 0.1)], P.MUTED, 0.02, 0.18, role="hair")
        dlab = st.text("optical analysis\ndownhole", DX, DY - 0.95, 0.15, P.TEXT, 0.25, kind="bold")
        st.fade_in(dial + [ndl, lead, dlab], _w(b, 0, "analysed") - 0.3, 0.4)
        st.rotate(ndl, _w(b, 0, "analysed"), _w(b, 0, "analysed") + 1.2, 90)
        blab = st.text("sample bottle\n→ the lab", -3.45, -2.2, 0.15, P.TEXT, 0.25, kind="bold")
        barr = st.arrow(TX + 0.4, -2.2, -4.15, -2.2, P.MUTED, 0.03, 0.12, 0.2)
        st.fade_in([blab] + barr, _w(b, 0, "lab") - 0.3, 0.4)
        groupA = [sand, oilt, body, probe, bore, opt, win, bottle, fill] + dial + [ndl, lead, dlab, blab] + barr + kick[:1]

        # ---- B: two sands, two lines (offset) ; then one line
        def mini(y0, t, offset, label, lab_col):
            x0, w, h = -1.6, 3.5, 2.55
            ax = [st.rect(x0 + w / 2, y0, w, 0.025, P.MUTED, 0.2), st.rect(x0, y0 + h / 2, 0.025, h, P.MUTED, 0.2),
                  st.text("pressure →", x0 + w - 0.05, y0 - 0.2, 0.13, P.MUTED, 0.2, align="r"),
                  st.text("depth ↓", x0 - 0.1, y0 + h - 0.12, 0.13, P.MUTED, 0.2, align="r")]
            bands, objs = [], []
            for (za, zb) in ((0.15, 0.4), (0.62, 0.88)):
                ya, yb = y0 + h * (1 - za), y0 + h * (1 - zb)
                bands.append(st.rect(x0 + w / 2, (ya + yb) / 2, w, ya - yb, P.SAND, 0.15, alpha=0.18, role="flat"))
            sl = 1.15                          # x per unit of y down (same water gradient in both sands)

            def P_(yf, off):
                return x0 + 0.35 + sl * (yf * h) + off
            l1 = st.line([(P_(0.12, 0), y0 + h * 0.88), (P_(0.43, 0), y0 + h * 0.57)], P.WATER, 0.045, 0.3)
            l2 = st.line([(P_(0.59, offset), y0 + h * 0.41), (P_(0.9, offset), y0 + h * 0.1)], P.WATER, 0.045, 0.3)
            for yf in (0.2, 0.28, 0.36):
                objs.append(st.circle(P_(yf, 0), y0 + h * (1 - yf), 0.07, P.WATER, 0.35))
            for yf in (0.67, 0.75, 0.83):
                objs.append(st.circle(P_(yf, offset), y0 + h * (1 - yf), 0.07, P.WATER, 0.35))
            st.fade_in(ax + bands, t, 0.4)
            st.fade_in(objs[:3], t + 0.3, 0.3)
            st.draw_on(l1, t + 0.5, t + 1.1)
            st.fade_in(objs[3:], t + 0.9, 0.3)
            st.draw_on(l2, t + 1.1, t + 1.7)
            out = ax + bands + objs + [l1, l2]
            if offset:
                ext = st.line([(P_(0.43, 0), y0 + h * 0.57), (P_(0.92, 0), y0 + h * 0.08)], P.WATER, 0.025, 0.28, alpha=0.6)
                ext.data["_role"] = "dash"
                st.draw_on(ext, t + 1.8, t + 2.4)
                ym = y0 + h * (1 - 0.75)
                dp = st.arrow(P_(0.75, 0) + 0.05, ym, P_(0.75, offset) - 0.1, ym, P.TEXT, 0.025, 0.1, 0.4) + \
                    st.arrow(P_(0.75, offset) - 0.1, ym, P_(0.75, 0) + 0.05, ym, P.TEXT, 0.025, 0.1, 0.4)
                st.fade_in(dp, t + 2.3, 0.3)
                out += [ext] + dp
            lb = _lbl(st, x0 + w / 2, y0 + h + 0.3, label, lab_col, 0.16, z=0.5)
            st.fade_in(lb, t + 2.0 if offset else t + 1.6, 0.4)
            return out + lb
        t_b1 = s[1] - 0.2
        st.fade(groupA, t_b1, t_b1 + 0.5, 1.0, 0.35)
        gB1 = mini(0.15, t_b1, 1.0, "different lines: not in pressure contact", P.WARN)
        t_b2 = _w(b, 1, "sharing") - 0.3
        gB2 = mini(-3.25, t_b2, 0.0, "one line: suggests a connection, not proof", P.TEXT)

        # ---- C: the contact, zoomed: FWL (pressure) and OWC (logs) 6 m above, transition zone above that
        zc0, zc1 = 4026.0, 4058.0
        cy0, cy1 = 3.0, -3.0

        def Yc(z):
            return cy0 + (z - zc0) * (cy1 - cy0) / (zc1 - zc0)
        CX0, CX1 = 2.75, 3.6
        z_tz = M.OWC - 10.0                      # top of the illustrative transition zone

        def sw_at(z):
            if z >= M.OWC:
                return 1.0
            h = M.OWC - z
            return 0.28 + 0.72 * math.exp(-h / 3.0)
        t_c = s[2] - 0.2
        st.fade(gB1 + gB2, t_c, t_c + 0.5, 1.0, 0.35)
        sand_c = st.rect((CX0 + CX1) / 2, 0.0, CX1 - CX0, 6.0, P.SAND, 0.1)
        st.fade_in(sand_c, t_c, 0.4)
        # fluid fill by saturation: green (oil) -> blue (water)
        oil_rgb, wat_rgb = hex_rgb(P.OIL), hex_rgb(P.WATER)
        strips = []
        nz = 64
        for i in range(nz):
            za = zc0 + (zc1 - zc0) * i / nz
            zb = zc0 + (zc1 - zc0) * (i + 1) / nz
            f = (sw_at((za + zb) / 2) - 0.28) / 0.72
            rgb = tuple(o + (w_ - o) * f for o, w_ in zip(oil_rgb, wat_rgb))
            hexc = "#%02x%02x%02x" % tuple(int(255 * v) for v in rgb)
            strips.append(st.rect((CX0 + CX1) / 2, (Yc(za) + Yc(zb)) / 2, CX1 - CX0, abs(Yc(za) - Yc(zb)) + 0.01, hexc, 0.12, alpha=0.75,
                                  role="flat"))
        t_fwl = _w(b, 2, "free-water level")
        t_owc = _w(b, 2, "oil-water contact")
        t_cap = _w(b, 2, "capillary")
        st.fade_in(strips, t_c + 0.2, 0.6)
        # Sw vs depth chart
        SWX0, SWX1 = 4.35, 5.75

        def Xs(v):
            return SWX0 + v * (SWX1 - SWX0)
        sw_ax = [st.rect((SWX0 + SWX1) / 2, cy1, SWX1 - SWX0, 0.025, P.MUTED, 0.2),
                 st.rect(SWX0, 0.0, 0.025, 6.0, P.MUTED, 0.2),
                 st.text("0", SWX0, cy1 - 0.2, 0.13, P.MUTED, 0.2), st.text("1", SWX1, cy1 - 0.2, 0.13, P.MUTED, 0.2),
                 st.text("Sw", (SWX0 + SWX1) / 2, cy1 - 0.24, 0.15, P.WATER, 0.2, kind="bold")]
        zz = [zc0 + 0.25 * i for i in range(int((zc1 - zc0) / 0.25) + 1)]
        swc = st.line([(Xs(sw_at(z)), Yc(z)) for z in zz], P.WATER, 0.045, 0.3)
        st.fade_in(sw_ax, t_c + 0.3, 0.4)
        st.draw_on(swc, t_cap - 0.4, t_cap + 1.2, "BEZIER")
        # FWL first (pressure), then OWC (logs)
        fw = st.dashed((CX0 - 0.1, Yc(M.FWL)), (SWX1 + 0.1, Yc(M.FWL)), P.TEXT, 0.03, 0.14, 0.08, 0.4)
        st.fade_in(fw, t_fwl - 0.2, 0.4)
        fwl_l = _lbl(st, 5.95, Yc(M.FWL), f"FWL {M.FWL:,.0f} m\npressure", P.TEXT, 0.15, align="l")
        st.fade_in(fwl_l, t_fwl, 0.4)
        ow = st.rect((CX0 + SWX1) / 2, Yc(M.OWC), SWX1 - CX0 + 0.2, 0.035, P.TEXT, 0.4)
        st.fade_in(ow, t_owc - 0.2, 0.4)
        owc_l = _lbl(st, 5.95, Yc(M.OWC) + 0.05, f"OWC {M.OWC:,.0f} m\nlogs", P.TEXT, 0.15, align="l")
        st.fade_in(owc_l, t_owc, 0.4)
        st.move(owc_l, t_owc, t_owc + 0.01, dy=0.32)
        brk = st.line([(CX0 - 0.18, Yc(M.OWC)), (CX0 - 0.28, Yc(M.OWC)), (CX0 - 0.28, Yc(M.FWL)), (CX0 - 0.18, Yc(M.FWL))], P.WARN, 0.025, 0.4,
                      role="hair")
        brl = st.text(f"{M.FWL - M.OWC:.0f} m", CX0 - 0.36, (Yc(M.OWC) + Yc(M.FWL)) / 2, 0.16, P.WARN, 0.4, align="r", kind="bold")
        st.fade_in([brk, brl], _w(b, 2, "a little higher"), 0.4)
        tz = _lbl(st, 5.95, (Yc(M.OWC) + Yc(z_tz)) / 2 + 0.2, "transition zone", P.TEXT, 0.15, align="l")
        wo = st.text("water only", (CX0 + CX1) / 2, (Yc(M.OWC) + Yc(M.FWL)) / 2, 0.13, P.TEXT, 0.4, kind="bold")
        oil_t = st.text("oil", (CX0 + CX1) / 2, Yc(4030), 0.15, P.TEXT, 0.4, kind="bold")
        wat_t = st.text("water", (CX0 + CX1) / 2, Yc(4055), 0.15, P.TEXT, 0.4, kind="bold")
        st.fade_in([oil_t, wat_t], t_c + 0.6, 0.4)
        st.fade_in(tz + [wo], t_cap, 0.4)
        cap = _lbl(st, 4.25, -3.4, "capillary forces hold water above the FWL", P.TEXT, 0.15)
        st.fade_in(cap, t_cap + 0.4, 0.4)


# ====================================================================================================== 8.07 core + lab
def beat_core(st, tl):
    b = tl["8.07"]
    s = b.sent
    rnd = random.Random(7)
    with st.span(b.start, b.end):
        t0 = b.start + 0.1
        # ---- phase 1: coring with a hollow bit
        CX = -4.1
        Y_TOP = 0.9                      # top of the sand / start of the core run
        rock = [st.rect(CX, (3.8 + Y_TOP) / 2, 3.6, 3.8 - Y_TOP, P.ROCK2, 0.0), st.rect(CX, (Y_TOP - 3.4) / 2, 3.6, Y_TOP + 3.4, P.SAND, 0.0)]
        hole = st.rect(CX, (3.8 + Y_TOP) / 2, 1.5, 3.8 - Y_TOP, P.BG, 0.02)
        RO, RI = 0.68, 0.36              # outer / inner radius of the crown (kerf between them)
        y_c0 = Y_TOP
        cut_len = 3.4
        t_cut0 = _w(b, 0, "cut by a hollow bit") - 0.2
        t_cut1 = _w(b, 0, "unlike") - 0.4
        kerf = [st.rect(CX - (RO + RI) / 2, y_c0, RO - RI, 0.0001, P.BG, 0.03, anchor="t"),
                st.rect(CX + (RO + RI) / 2, y_c0, RO - RI, 0.0001, P.BG, 0.03, anchor="t")]
        walls = [st.rect(CX - (RO + RI) / 2, 3.8, RO - RI - 0.04, 3.8 - y_c0 - 0.12, P.STEEL, 0.2, anchor="t"),
                 st.rect(CX + (RO + RI) / 2, 3.8, RO - RI - 0.04, 3.8 - y_c0 - 0.12, P.STEEL, 0.2, anchor="t")]
        crown = [st.rect(CX - (RO + RI) / 2, y_c0 - 0.06, RO - RI + 0.04, 0.14, P.STEEL_DK, 0.22),
                 st.rect(CX + (RO + RI) / 2, y_c0 - 0.06, RO - RI + 0.04, 0.14, P.STEEL_DK, 0.22)]
        cutters = []
        for sx in (-1, 1):
            for kx in range(3):
                x = CX + sx * (RI + 0.05 + kx * 0.1)
                cutters.append(st.poly([(x - 0.04, y_c0 - 0.13), (x + 0.04, y_c0 - 0.13), (x, y_c0 - 0.2)], P.TEXT, 0.23))
        core_l = st.text("core", CX, Y_TOP - 1.6, 0.17, "#5b4a2a", 0.05, kind="bold")
        st.fade_in(rock + [hole] + kerf + walls + crown + cutters, t0, 0.5)
        st.scale_to(kerf, t_cut0, t_cut1, sy=cut_len, interp="LINEAR")
        st.scale_to(walls, t_cut0, t_cut1, sy=3.8 - (y_c0 - cut_len) - 0.12, interp="LINEAR")
        st.move(crown + cutters, t_cut0, t_cut1, dy=-cut_len, interp="LINEAR")
        st.fade_in(core_l, t_cut0 + 1.2, 0.4)
        lab1 = _lbl(st, CX, 3.35, "hollow bit: the core rises inside", P.TEXT, 0.16)
        st.fade_in(lab1, t_cut0 + 0.2, 0.4)
        lab2 = _lbl(st, CX, -3.35, "cut while drilling the reservoir", P.WARN, 0.16)
        st.fade_in(lab2, _w(b, 0, "while the reservoir"), 0.4)
        # comparison: cuttings, sidewall plug, core (side by side, to scale-ish)
        t_cmp = _w(b, 0, "unlike")
        RY = -0.9
        chips = []
        for i in range(14):
            x = -0.85 + rnd.uniform(-0.45, 0.45)
            y = RY - 0.3 + rnd.uniform(-0.12, 0.18)
            r = rnd.uniform(0.04, 0.08)
            chips.append(st.poly([(x + r * math.cos(a) * rnd.uniform(0.6, 1.3), y + r * math.sin(a) * rnd.uniform(0.6, 1.3))
                                  for a in [k_ * 2 * math.pi / 5 for k_ in range(5)]], "#9c8457", 0.3, role="flat"))
        c_l = st.text("crushed cuttings", -0.85, RY - 0.85, 0.16, P.MUTED, 0.3, kind="bold")
        plug = [st.rect(1.35, RY - 0.25, 0.42, 0.28, P.SAND, 0.3), st.ellipse(1.56, RY - 0.25, 0.06, 0.14, "#d9bf86", 0.31, role="flat")]
        p_l = st.text("sidewall plug\n(thumb-sized)", 1.35, RY - 0.95, 0.16, P.MUTED, 0.3, kind="bold")
        core = [st.rect(4.9, RY - 0.2, 4.6, 0.62, P.SAND, 0.3)] + [st.rect(2.6 + 1.15 * k_, RY - 0.2, 0.025, 0.62, "#8f774d", 0.31) for k_ in range(1, 4)]
        core.append(st.ellipse(7.2, RY - 0.2, 0.1, 0.31, "#d9bf86", 0.31, role="flat"))
        k_l = st.text("core: a metres-long intact cylinder", 4.9, RY - 0.85, 0.16, P.TEXT, 0.3, kind="bold")
        st.fade_in(chips + [c_l], _w(b, 0, "crushed") - 0.2, 0.4)
        st.fade_in(plug + [p_l], _w(b, 0, "sidewall") - 0.3, 0.4)
        st.fade_in(core + [k_l], t_cmp - 0.6, 0.5)
        only = _lbl(st, 4.9, RY + 0.55, "the only large, intact sample", P.SAFE, 0.19)
        st.fade_in(only, t_cmp - 0.3, 0.4)
        ph1 = rock + [hole] + kerf + walls + crown + cutters + [core_l] + lab1 + lab2 + chips + [c_l] + plug + [p_l] + core + [k_l] + only
        t_lab = s[1] - 0.25
        st.fade_out(ph1, t_lab, 0.45)

        # ---- phase 2: the lab
        t_por = _w(b, 1, "porosity")
        t_perm = _w(b, 1, "permeability")
        t_flow = _w(b, 1, "how easily")
        t_tri = _w(b, 1, "triaxial")
        t_col = _w(b, 1, "collapse")
        t_lot = _w(b, 1, "leak-off")
        # permeability rig (top row)
        PX, PY = -2.0, 1.95
        sleeve = st.rect(PX, PY, 3.0, 1.0, P.STEEL_DK, 0.2, role="steel")
        plg = st.rect(PX, PY, 2.6, 0.72, P.SAND, 0.22)
        pores = [st.circle(PX - 1.1 + 0.32 * i + rnd.uniform(-0.05, 0.05), PY + rnd.choice((-0.2, 0.0, 0.2)), 0.05, P.BG, 0.23, role="disc")
                 for i in range(8)]
        inl = st.rect(PX - 2.05, PY, 1.1, 0.16, P.STEEL, 0.19)
        outl = st.rect(PX + 2.05, PY, 1.1, 0.16, P.STEEL, 0.19)
        g1 = [st.circle(PX - 2.2, PY + 0.55, 0.26, P.PANEL2, 0.25, role="disc"), st.ring(PX - 2.2, PY + 0.55, 0.26, 0.03, P.MUTED, 0.26),
              st.text("p1", PX - 2.2, PY + 0.55, 0.13, P.TEXT, 0.27, kind="bold")]
        g2 = [st.circle(PX + 2.2, PY + 0.55, 0.26, P.PANEL2, 0.25, role="disc"), st.ring(PX + 2.2, PY + 0.55, 0.26, 0.03, P.MUTED, 0.26),
              st.text("p2", PX + 2.2, PY + 0.55, 0.13, P.TEXT, 0.27, kind="bold")]
        rig = [sleeve, plg, inl, outl] + g1 + g2
        st.fade_in([sleeve, plg], t_lab + 0.3, 0.4)
        st.fade_in(pores, t_por - 0.2, 0.4)
        por_l = _lbl(st, PX - 0.6, PY - 0.82, "porosity: how much pore space", P.TEXT, 0.16)
        st.fade_in(por_l, t_por, 0.35)
        st.fade_in([inl, outl] + g1 + g2, t_perm - 0.3, 0.4)
        for dyy in (-0.18, 0.0, 0.18):
            st.flow([(PX - 2.6, PY + dyy * 0.3), (PX - 1.3, PY + dyy), (PX + 1.3, PY + dyy), (PX + 2.6, PY + dyy * 0.3)], t_perm, b.end,
                    LABGAS, n=9, speed=0.9, r=0.035, z=0.3, jitter=0.03)
        perm_l = _lbl(st, PX + 0.9, PY - 0.82, "permeability: flow rate ÷ pressure drop", P.TEXT, 0.16)
        st.fade(por_l, t_flow - 0.3, t_flow, 1.0, 0.0)
        st.fade_in(perm_l, t_flow, 0.35)
        # triaxial cell (bottom-left)
        TX, TY = -4.9, -1.55
        cell = st.rect(TX, TY, 1.55, 2.6, P.PANEL2, 0.2, role="card")
        spec = st.rect(TX, TY, 0.62, 1.5, P.SAND, 0.22)
        platens = [st.rect(TX, TY + 0.85, 0.72, 0.18, P.STEEL, 0.23), st.rect(TX, TY - 0.85, 0.72, 0.18, P.STEEL, 0.23)]
        s1a = st.arrow(TX, TY + 1.65, TX, TY + 0.98, P.TEXT, 0.05, 0.18, 0.3) + st.arrow(TX, TY - 1.65, TX, TY - 0.98, P.TEXT, 0.05, 0.18, 0.3)
        s3a = []
        for yy in (TY + 0.4, TY - 0.4):
            s3a += st.arrow(TX - 0.72, yy, TX - 0.36, yy, P.MUTED, 0.035, 0.12, 0.3) + st.arrow(TX + 0.72, yy, TX + 0.36, yy, P.MUTED, 0.035, 0.12, 0.3)
        s1l = st.text("σ1", TX + 0.22, TY + 1.4, 0.16, P.TEXT, 0.3, align="l", kind="bold")
        s3l = st.text("σ3", TX - 0.5, TY + 0.02, 0.15, P.MUTED, 0.3, kind="bold")
        tri_t = st.text("triaxial test", TX, TY + 1.95, 0.18, P.TEXT, 0.3, kind="bold")
        tri = [cell, spec] + platens + s1a + s3a + [s1l, s3l, tri_t]
        st.fade_in(tri, t_tri - 0.3, 0.45)
        # stress-strain
        cs = Chart(st, -3.3, -2.95, 2.4, 2.35, (0, 10), (0, 10))
        fr = cs.frame(xticks=[], yticks=[], xlabel="axial strain", grid=False, panel=False)
        ylab = st.text("stress", -3.45, -0.75, 0.14, P.MUTED, 0.2, align="r")
        ssx = [0, 1, 2, 3, 4, 5, 5.8, 6.5, 7.5, 8.5, 10]
        ssy = [0, 2.3, 4.5, 6.3, 7.7, 8.6, 8.9, 8.7, 7.4, 6.6, 6.2]
        ss = cs.curve(ssx, ssy, CURVE, 0.04, 0.3)
        pk = st.circle(cs.X(5.8), cs.Y(8.9), 0.07, P.WARN, 0.35)
        pkl = st.text("peak strength", cs.X(5.8), cs.Y(8.9) + 0.25, 0.14, P.WARN, 0.35, kind="bold")
        st.fade_in(fr + [ylab], t_tri, 0.4)
        st.draw_on(ss, t_tri + 0.3, t_tri + 2.0)
        st.move(platens[0], t_tri + 0.3, t_tri + 2.0, dy=-0.06)
        st.move(platens[1], t_tri + 0.3, t_tri + 2.0, dy=0.06)
        st.scale_to(spec, t_tri + 0.3, t_tri + 2.0, sy=1.38, sx=0.66)
        st.pop_in(pk, t_tri + 1.3, 0.3)
        st.fade_in(pkl, t_tri + 1.4, 0.3)
        # Mohr circles: centred on the sigma axis, envelope tangent (tau = c + sigma tan phi)
        sinp = 15.0 / 35.0
        phi = math.asin(sinp)
        cosp = math.cos(phi)
        coh = (25.0 - 35.0 * sinp) / cosp
        cm = Chart(st, 0.75, -2.95, 6.6, 6.6 * 62.0 / 140.0, (0.0, 140.0), (0.0, 62.0))
        mfr = [st.rect(cm.X(70), cm.Y(0), cm.w, 0.025, P.MUTED, 0.2), st.rect(cm.X(0), cm.Y(31), 0.025, cm.h, P.MUTED, 0.2),
               st.text("normal stress σ", cm.X(140), cm.Y(0) - 0.22, 0.14, P.MUTED, 0.2, align="r"),
               st.text("shear τ", cm.X(0) - 0.1, cm.Y(62) - 0.05, 0.14, P.MUTED, 0.2, align="r")]
        t_m = t_tri + 1.6
        st.fade_in(mfr, t_m, 0.4)
        circles = []
        for i, (s3, s1) in enumerate(((10.0, 60.0), (30.0, 110.0))):
            cc, R = (s1 + s3) / 2, (s1 - s3) / 2
            arc = st.line([cm.pt(cc + R * math.cos(math.radians(a)), R * math.sin(math.radians(a))) for a in range(0, 181, 4)], CURVE, 0.035, 0.3)
            st.draw_on(arc, t_m + 0.3 + 0.6 * i, t_m + 1.0 + 0.6 * i, "BEZIER")
            ticks = [st.rect(cm.X(s3), cm.Y(0), 0.025, 0.14, P.MUTED, 0.31), st.rect(cm.X(s1), cm.Y(0), 0.025, 0.14, P.MUTED, 0.31)]
            st.fade_in(ticks, t_m + 0.3 + 0.6 * i, 0.3)
            st_pt = (cc - R * sinp, R * cosp)
            dot = st.circle(cm.X(st_pt[0]), cm.Y(st_pt[1]), 0.06, P.COLLAPSE, 0.4)
            st.pop_in(dot, t_m + 1.6 + 0.2 * i, 0.3)
            circles += [arc, dot] + ticks
        s_end = (62.0 - coh) / math.tan(phi)
        env = st.line([cm.pt(0, coh), cm.pt(s_end, 62.0)], P.COLLAPSE, 0.045, 0.35)
        st.draw_on(env, t_m + 1.3, t_m + 2.0, "BEZIER")
        envl = st.text("failure envelope", cm.X(s_end) - 0.15, cm.Y(62.0) - 0.05, 0.15, P.COLLAPSE, 0.35, align="r", kind="bold")
        cohl = st.text("c", cm.X(0) + 0.12, cm.Y(coh) + 0.12, 0.14, P.COLLAPSE, 0.35, align="l", kind="bold")
        st.fade_in([envl, cohl], t_m + 1.8, 0.35)
        mohr_t = st.text("Mohr circles", cm.X(70), cm.Y(0) - 0.22, 0.14, P.MUTED, 0.2)
        mohr_t.data["s"] = ""
        # what the results calibrate
        colp = _lbl(st, 5.35, 2.25, "→ collapse and rock-strength models", P.COLLAPSE, 0.17)
        st.fade_in(colp, t_col - 0.2, 0.4)
        lotp = _lbl(st, 5.35, 1.45, "fracture limit: still from leak-off tests", P.FRAC, 0.17)
        st.fade_in(lotp, t_lot - 0.2, 0.4)
        # weeks / months
        t_wk = _w(b, 2, "weeks")
        t_mo = _w(b, 2, "months")
        wk = _lbl(st, 4.05, 3.15, "routine: weeks", P.TEXT, 0.19)
        mo = _lbl(st, 6.4, 3.15, "special: months", P.WARN, 0.19)
        st.fade_in(wk, t_wk - 0.3, 0.35)
        st.fade_in(mo, t_mo - 0.3, 0.35)


# ====================================================================================================== 8.08 DST
def beat_dst(st, tl):
    b = tl["8.08"]
    s = b.sent
    WX = -4.6
    Y_SURF, Y_SB, Y_SHOE, Y_HANG = 3.3, 2.55, -0.45, -0.1
    Y_RT, Y_RB, Y_BOT = -1.55, -2.85, -3.25
    with st.span(b.start, b.end):
        t0 = b.start + 0.1
        # earth, seabed, sea
        sea = st.rect(WX, (3.85 + Y_SB) / 2, 3.2, 3.85 - Y_SB, P.SEA, 0.0)
        earth = [st.rect(WX, (Y_SB + Y_RT) / 2, 3.2, Y_SB - Y_RT, P.ROCK2, 0.0),
                 st.rect(WX, (Y_RT + Y_RB) / 2, 3.2, Y_RT - Y_RB, P.SAND, 0.0),
                 st.rect(WX, (Y_RB + Y_BOT - 0.15) / 2, 3.2, Y_RB - Y_BOT + 0.15, P.SHALE, 0.0)]
        hole_up = st.rect(WX, (Y_SB + Y_SHOE) / 2, 1.5, Y_SB - Y_SHOE, P.BG, 0.02)
        hole_dn = st.rect(WX, (Y_SHOE + Y_BOT) / 2, 1.12, Y_SHOE - Y_BOT, P.BG, 0.02)
        csg = [st.rect(WX - 0.6, (Y_SB + Y_SHOE) / 2, 0.08, Y_SB - Y_SHOE, P.STEEL, 0.1),
               st.rect(WX + 0.6, (Y_SB + Y_SHOE) / 2, 0.08, Y_SB - Y_SHOE, P.STEEL, 0.1)]
        cem9 = [st.rect(WX - 0.7, (0.6 + Y_SHOE) / 2, 0.11, 0.6 - Y_SHOE, P.CEMENT, 0.05), st.rect(WX + 0.7, (0.6 + Y_SHOE) / 2, 0.11, 0.6 - Y_SHOE, P.CEMENT, 0.05)]
        shoe_l = st.text("9⅝ in shoe", WX + 1.75, Y_SHOE, 0.14, P.MUTED, 0.3, align="r")
        sb_l = st.text("seabed", WX - 1.55, Y_SB + 0.15, 0.13, P.MUTED, 0.3, align="l")
        res_l = st.text("reservoir", WX - 1.55, Y_RT - 0.2, 0.13, "#5b4a2a", 0.3, align="l", kind="bold")
        base = [sea] + earth + [hole_up, hole_dn] + csg + cem9 + [shoe_l, sb_l, res_l]
        st.fade_in(base, t0, 0.5)
        # liner hung inside the 9-5/8 in casing, cemented across the reservoir
        t_lin = _w(b, 1, "liner")
        lin = [st.rect(WX - 0.4, (Y_HANG + Y_BOT) / 2, 0.06, Y_HANG - Y_BOT, P.STEEL, 0.12),
               st.rect(WX + 0.4, (Y_HANG + Y_BOT) / 2, 0.06, Y_HANG - Y_BOT, P.STEEL, 0.12)]
        hang = [st.rect(WX - 0.5, Y_HANG, 0.16, 0.12, P.STEEL_DK, 0.13), st.rect(WX + 0.5, Y_HANG, 0.16, 0.12, P.STEEL_DK, 0.13)]
        cem = [st.rect(WX - 0.5, Y_SHOE, 0.13, 0.0001, P.CEMENT, 0.06, anchor="t"), st.rect(WX + 0.5, Y_SHOE, 0.13, 0.0001, P.CEMENT, 0.06, anchor="t")]
        st.fade_in(lin + hang, t_lin - 0.2, 0.4)
        st.fade_in(cem, t_lin, 0.1)
        st.scale_to(cem, t_lin + 0.1, t_lin + 1.3, sy=Y_SHOE - Y_BOT)
        lin_l = _lbl(st, WX + 1.05, -1.0, "liner, cemented", P.TEXT, 0.14, align="l")
        st.fade_in(lin_l, t_lin + 0.4, 0.3)
        # perforations through liner and cement into the sand
        t_pipe = _w(b, 1, "temporary pipe")
        perfs = []
        for yy in (-1.8, -2.15, -2.5):
            for sx in (-1, 1):
                perfs.append(st.rect(WX + sx * 0.6, yy, 0.42, 0.06, P.BG, 0.14))
        st.fade_in(perfs, t_pipe - 0.6, 0.3)
        # test string, packer, tester valve
        tub = [st.rect(WX - 0.14, (Y_SURF + (-1.4)) / 2, 0.05, Y_SURF + 1.4, P.STEEL, 0.15),
               st.rect(WX + 0.14, (Y_SURF + (-1.4)) / 2, 0.05, Y_SURF + 1.4, P.STEEL, 0.15)]
        t_pk = _w(b, 1, "packer")
        t_vl = _w(b, 1, "valves")
        pk = [st.rect(WX - 0.27, -1.15, 0.2, 0.3, RUBBER, 0.16, role="flat"), st.rect(WX + 0.27, -1.15, 0.2, 0.3, RUBBER, 0.16, role="flat")]
        valve = st.circle(WX, -0.55, 0.13, P.STEEL_DK, 0.17, role="disc")
        vbore = st.rect(WX, -0.55, 0.055, 0.24, P.BG, 0.18)
        head = st.rect(WX, Y_SURF + 0.12, 0.5, 0.26, P.STEEL_DK, 0.2)
        st.fade_in(tub + [head], t_pipe - 0.2, 0.4)
        st.fade_in(pk, t_pk - 0.2, 0.3)
        st.fade_in([valve, vbore], t_vl - 0.2, 0.3)
        pk_l = _lbl(st, WX - 1.0, -1.15, "packer", P.TEXT, 0.14, align="r")
        vl_l = _lbl(st, WX - 1.0, -0.55, "valve", P.TEXT, 0.14, align="r")
        st.fade_in(pk_l, t_pk, 0.3)
        st.fade_in(vl_l, t_vl, 0.3)
        # surface: separator and burner
        SEPX, BURX, SY = -1.75, 1.6, 3.3
        fl1 = st.rect((WX + 0.25 + SEPX - 0.65) / 2, SY + 0.12, SEPX - 0.65 - (WX + 0.25), 0.07, P.STEEL_DK, 0.2)
        sep = st.rect(SEPX, SY + 0.12, 1.3, 0.5, P.PANEL2, 0.21, role="pill")
        sep_l = st.text("separator", SEPX, SY + 0.12, 0.14, P.TEXT, 0.22, kind="bold")
        fl2 = st.rect((SEPX + 0.65 + BURX) / 2, SY + 0.12, BURX - (SEPX + 0.65), 0.05, P.STEEL_DK, 0.2)
        boom = st.rect(BURX, SY + 0.12, 0.2, 0.18, P.STEEL_DK, 0.21)
        bur_l = st.text("burner", BURX, SY - 0.25, 0.14, P.MUTED, 0.22, kind="bold")
        t_surf = _w(b, 1, "flow to surface")
        st.fade_in([fl1, sep, sep_l, fl2, boom, bur_l], t_surf - 0.8, 0.4)
        t_shut = _w(b, 2, "shut it in")
        # flow: sand -> perforations -> liner -> tubing -> separator -> burner (gas + oil burned)
        for yy in (-1.8, -2.15, -2.5):
            for sx in (-1, 1):
                st.flow([(WX + sx * 1.3, yy), (WX + sx * 0.2, yy), (WX, -1.45)], t_surf - 0.3, t_shut + 0.2, P.OIL, n=4, speed=0.9, r=0.035, z=0.3)
        st.flow([(WX, -1.4), (WX, Y_SURF + 0.12), (SEPX - 0.6, SY + 0.12)], t_surf - 0.2, t_shut + 0.2, P.OIL, n=22, speed=2.0, r=0.035, z=0.3)
        st.flow([(SEPX + 0.6, SY + 0.12), (BURX, SY + 0.12)], t_surf + 0.4, t_shut + 0.6, P.GAS, n=6, speed=1.2, r=0.035, z=0.3)
        t_flame0 = t_surf + 0.6
        t_cost = _w(b, 3, "burns")
        t_fade = s[4]

        def draw_flame(c, t, look):
            if t < t_flame0:
                return
            on = _clamp((t - t_flame0) / 0.5, 0, 1) * (1.0 - _clamp((t - (t_shut + 0.6)) / 0.8, 0, 1))
            boost = 1.0 + 0.6 * _clamp((t - t_cost) / 0.6, 0, 1) * (1 - _clamp((t - t_fade) / 0.6, 0, 1))
            if t > t_cost - 0.3:      # relight for the 'burns hydrocarbons' line (illustrative)
                on = max(on, _clamp((t - (t_cost - 0.3)) / 0.5, 0, 1) * (1 - _clamp((t - t_fade) / 0.6, 0, 1)))
            if on <= 0.01:
                return
            for k_ in range(14):
                ph = (t * 1.7 + k_ / 14.0) % 1.0
                x = BURX + 0.25 + 0.55 * ph * boost + 0.05 * math.sin(t * 9 + k_)
                y = SY + 0.18 + 0.25 * ph * boost + 0.04 * math.sin(t * 7 + k_ * 2)
                r = (0.12 - 0.08 * ph) * boost
                look.draw_particles(c, [(x, y)], FLAME if ph < 0.6 else "#ff9b54", r, on * (1 - ph) * 0.9, True)
        st.procedural(t_flame0, b.end, 0.4, draw_flame)
        # shut-in: valve turns
        st.rotate(vbore, t_shut - 0.1, t_shut + 0.4, 90)
        st.recolor(valve, t_shut - 0.1, t_shut + 0.3, P.WARN)
        si = _lbl(st, WX - 1.0, -0.55, "valve shut", P.WARN, 0.14, align="r")
        st.fade_out(vl_l, t_shut - 0.1, 0.2)
        st.fade_in(si, t_shut + 0.1, 0.3)
        st.ripple(WX, -0.55, t_shut, t_shut + 1.2, P.WARN, period=0.6, r0=0.12, r1=0.6)
        # rate + pressure vs time (middle column)
        t_pl = t_surf - 0.3
        cr = Chart(st, -1.55, 0.55, 4.4, 1.15, (0.0, 10.0), (0.0, 1.2))
        crf = [st.rect(cr.X(5), cr.Y(0), cr.w, 0.025, P.MUTED, 0.2), st.rect(cr.X(0), cr.Y(0.6), 0.025, cr.h, P.MUTED, 0.2),
               st.text("rate", cr.X(0) - 0.1, cr.Y(0.6), 0.14, P.MUTED, 0.2, align="r")]
        cp = Chart(st, -1.55, -2.85, 4.4, 2.9, (0.0, 10.0), (0.0, 10.0))
        cpf = [st.rect(cp.X(5), cp.Y(0), cp.w, 0.025, P.MUTED, 0.2), st.rect(cp.X(0), cp.Y(5), 0.025, cp.h, P.MUTED, 0.2),
               st.text("pressure", cp.X(0) - 0.1, cp.Y(5), 0.14, P.MUTED, 0.2, align="r"),
               st.text("time →", cp.X(10), cp.Y(0) - 0.22, 0.14, P.MUTED, 0.2, align="r")]
        st.fade_in(crf + cpf, t_pl, 0.4)
        T_SI = 4.0
        rate = cr.curve([0, 0.6, 0.6, T_SI, T_SI, 10], [0, 0, 1.0, 1.0, 0, 0], P.OIL, 0.04, 0.3)
        qx = [0.0, 0.6] + [0.6 + i * (T_SI - 0.6) / 30 for i in range(1, 31)]
        qy = [9.0, 9.0] + [9.0 - 4.2 * (1 - math.exp(-(x - 0.6) / 0.35)) - 0.25 * math.log(1 + (x - 0.6)) for x in qx[2:]]
        p_si = qy[-1]
        bx = [T_SI + i * (10 - T_SI) / 40 for i in range(1, 41)]
        by = [p_si + (8.85 - p_si) * (1 - math.exp(-(x - T_SI) / 0.55)) - 0.15 * math.exp(-(x - T_SI) / 3.0) for x in bx]
        dd = cp.curve(qx, qy, P.PORE, 0.045, 0.3)
        bu = cp.curve([T_SI] + bx, [p_si] + by, P.PORE, 0.045, 0.3)
        st.draw_on(rate, t_pl + 0.2, t_shut + 0.3)
        st.draw_on(dd, t_pl + 0.3, t_shut)
        st.draw_on(bu, t_shut + 0.1, t_shut + 3.2)
        flw = st.text("flow", cp.X(2.3), cp.Y(3.3), 0.15, P.TEXT, 0.35, kind="bold")
        bul = st.text("build-up", cp.X(7.2), cp.Y(6.6), 0.15, P.TEXT, 0.35, kind="bold")
        st.fade_in(flw, t_pl + 1.0, 0.3)
        st.fade_in(bul, t_shut + 1.0, 0.3)
        si_line = st.rect(cp.X(T_SI), (cp.Y(0) + cr.Y(1.2)) / 2, 0.02, cr.Y(1.2) - cp.Y(0), P.WARN, 0.25, alpha=0.6)
        sil = st.text("shut in", cp.X(T_SI) + 0.08, cr.Y(1.2) - 0.05, 0.13, P.WARN, 0.3, align="l", kind="bold")
        st.fade_in([si_line, sil], t_shut, 0.3)
        t_prod = _w(b, 2, "productivity")
        prl = _lbl(st, cr.X(7.4), cr.Y(0.62), "productivity", P.TEXT, 0.14)
        st.fade_in(prl, t_prod - 0.1, 0.3)
        # log-log derivative (right, below the term cards)
        cd = Chart(st, 4.05, -2.9, 3.4, 2.15, (-2.0, 2.0), (-1.0, 1.4))
        cdf = [st.rect(cd.X(0), cd.Y(-1), cd.w, 0.025, P.MUTED, 0.2), st.rect(cd.X(-2), cd.Y(0.2), 0.025, cd.h, P.MUTED, 0.2),
               st.text("log Δt", cd.X(2), cd.Y(-1) - 0.2, 0.13, P.MUTED, 0.2, align="r"),
               st.text("log Δp, derivative", cd.X(-2) + 0.08, cd.Y(1.4) + 0.12, 0.13, P.MUTED, 0.2, align="l")]
        lx = [-2.0 + i * 0.05 for i in range(81)]
        dpy = [min(0.15 + 0.95 * (x + 2.0), 0.55 + 0.32 * (x + 0.5) + (0.2 * (x - 1.0) if x > 1.0 else 0.0)) for x in lx]
        dvy = [(-0.55 + 1.0 * (x + 2.0)) if x < -1.35 else
               (0.1 + 0.5 * math.exp(-((x + 1.0) / 0.42) ** 2) + (0.42 * (x - 0.9) if x > 0.9 else 0.0)) for x in lx]
        for i in range(1, len(dvy)):          # smooth the joints
            dvy[i] = 0.6 * dvy[i] + 0.4 * dvy[i - 1]
        t_der = _w(b, 2, "permeability") - 1.2
        st.fade_in(cdf, t_der - 0.4, 0.4)
        dpc = cd.curve(lx, dpy, P.PORE, 0.035, 0.3)
        dvc = cd.curve(lx, dvy, P.WARN, 0.04, 0.31)
        st.draw_on([dpc, dvc], t_der, t_der + 1.6)
        lb = [(_w(b, 2, "permeability"), cd.X(0.15), cd.Y(0.1) - 0.24, "flat: permeability"),
              (_w(b, 2, "near-well damage"), cd.X(-1.0), cd.Y(0.6) + 0.22, "hump: near-well damage"),
              (_w(b, 2, "boundaries"), cd.X(1.55), cd.Y(0.42) + 0.0, "boundary")]
        for t, x, y, txt in lb:
            o = st.text(txt, x, y, 0.13, P.WARN, 0.35, kind="bold")
            st.fade_in(o, t - 0.1, 0.3)
        # the cost: Norway
        cst = _lbl(st, 5.6, 2.55, "costly  ·  burns hydrocarbons", P.WARN, 0.18)
        st.fade_in(cst, _w(b, 3, "costly") - 0.1, 0.35)
        no = _lbl(st, 5.6, 1.75, "NORWAY: emissions controlled and taxed", "#ffffff", 0.16, bg=P.NO_BADGE)
        st.fade_in(no, _w(b, 3, "Norway") - 0.1, 0.35)
        # our well: logs, pressures, samples (the test string fades)
        test_parts = lin + hang + cem + perfs + tub + pk + [valve, vbore, head, fl1, sep, sep_l, fl2, boom, bur_l, lin_l, pk_l, si]
        st.fade(test_parts, t_fade - 0.2, t_fade + 0.8, 1.0, 0.12)
        plots = crf + cpf + [rate, dd, bu, flw, bul, si_line, sil] + prl + cdf + [dpc, dvc]
        st.fade(plots, t_fade - 0.2, t_fade + 0.6, 1.0, 0.25)
        oh = _lbl(st, WX + 1.05, -2.2, "our well: open hole", P.TEXT, 0.14, align="l")
        st.fade_in(oh, _w(b, 4, "our example well") - 0.2, 0.4)
        items = [("logs", _w(b, 4, "logs")), ("pressures", _w(b, 4, "pressures")), ("samples", _w(b, 4, "samples"))]
        for i, (txt, t) in enumerate(items):
            x = -0.4 + 2.15 * i
            p_ = _lbl(st, x, -0.1, txt, P.TEXT, 0.24, z=0.8)
            st.fade_in(p_, t - 0.1, 0.35)
            _check(st, x + 0.75, 0.3, t + 0.15, s=0.13)
        ow = st.text("our well: logs, pressures, samples", 1.75, 0.8, 0.26, P.SAFE, 0.8, kind="bold")
        st.fade_in(ow, _w(b, 4, "exactly") - 0.3, 0.4)


# ====================================================================================================== 8.09 net pay
def beat_netpay(st, tl):
    b = tl["8.09"]
    s = b.sent
    VX, PX, SX, TW = -5.35, -3.85, -2.35, 1.3
    with st.span(b.start, b.end):
        t0 = b.start + 0.1
        dl = _depth_labels(st)
        zl = _zoom_link(st, t0, b.end, LZ0, LZ1, LY0, LY1)
        Xv = _xmap(VX, TW, 0.0, 1.0)
        Xp = _xmap(PX, TW, 0.0, 0.35)
        Xs = _xmap(SX, TW, 0.0, 1.0)
        fv = _track_frame(st, VX, TW, "shale volume", P.MUTED, [(VX, "0"), (VX + TW, "1")])
        fp = _track_frame(st, PX, TW, "porosity", CURVE, [(PX, "0"), (PX + TW, "0.35")])
        fs = _track_frame(st, SX, TW, "water sat.", P.WATER, [(SX, "0"), (SX + TW, "1")])
        st.fade_in(dl + fv + fp + fs, t0, 0.5)
        _log_curve(st, LG.vsh, LG.z, Xv, P.MUTED, 0.03, t0, b.end, lambda t: L.Z0 + (L.Z1 - L.Z0) * _clamp((t - t0 - 0.3) / 2.0, 0, 1), glow=False)
        _log_curve(st, LG.phi, LG.z, Xp, CURVE, 0.03, t0, b.end, lambda t: L.Z0 + (L.Z1 - L.Z0) * _clamp((t - t0 - 0.3) / 2.0, 0, 1), glow=False)
        _log_curve(st, LG.sw, LG.z, Xs, P.WATER, 0.03, t0, b.end, lambda t: L.Z0 + (L.Z1 - L.Z0) * _clamp((t - t0 - 0.3) / 2.0, 0, 1), glow=False)
        # contacts across the tracks
        for zc, name in ((M.GOC, "GOC"), (M.OWC, "OWC")):
            ln = st.dashed((VX, Yd(zc)), (0.75, Yd(zc)), P.TEXT, 0.015, 0.08, 0.06, 0.2, alpha=0.5)
            tx = st.text(name, 0.85, Yd(zc), 0.13, P.MUTED, 0.3, align="l", kind="bold")
            st.fade_in(ln + [tx], t0 + 1.5, 0.5)
        # cutoffs and flag columns, three passes
        flags = [("net\nsand", LG.net_sand, -0.75, lambda f: P.SAND, VX, Xv(L.CUT_VSH), f"Vsh < {L.CUT_VSH:g}", _w(b, 1, "shale")),
                 ("net\nreservoir", LG.net_res, -0.15, lambda f: "#e0a458", PX, Xp(L.CUT_PHI), f"φ > {L.CUT_PHI:g}", _w(b, 1, "porosity")),
                 ("net\npay", LG.net_pay, 0.45, lambda f: {"gas": P.GAS, "oil": P.OIL}.get(f, P.WATER), SX, Xs(L.CUT_SW), f"Sw < {L.CUT_SW:g}",
                  _w(b, 1, "water"))]
        for name, fl, x, cfn, tx0, xc, ctxt, t in flags:
            cl = st.rect(xc, (LY0 + LY1) / 2, 0.035, LY0 - LY1, P.WARN, 0.3, alpha=0.9)
            ct = _lbl(st, tx0 + TW / 2, LY1 - 0.45, ctxt, P.WARN, 0.14, z=0.5)
            st.fade_in([cl] + ct, t - 0.3, 0.35)
            parts, run, run_start = [], None, None
            for zz, f_, flu in zip(LG.z + [LG.z[-1] + L.STEP], fl + [False], LG.fluid + ["none"]):
                key = cfn(flu) if f_ else None
                if key != run:
                    if run is not None:
                        parts.append(st.rect(x, (Yd(run_start) + Yd(zz)) / 2, 0.42, abs(Yd(run_start) - Yd(zz)), run, 0.3, role="flat"))
                    run, run_start = key, zz
            hd = st.text(name, x, LY0 + 0.3, 0.13, P.TEXT, 0.3, kind="bold")
            frame = st.rect(x, (LY0 + LY1) / 2, 0.46, LY0 - LY1 + 0.04, P.PANEL, 0.25)
            st.fade_in([frame, hd], t - 0.3, 0.3)
            for i, p_ in enumerate(parts):
                st.fade_in(p_, t + 0.15 + 0.02 * i, 0.25)
        # thickness bars (right, below the term cards)
        BX0, BW = 3.2, 4.3
        k = BW / SUM["gross"]
        t_nr = _w(b, 2, "Net reservoir")
        t_gr = _w(b, 2, "gross thickness")
        t_ntg = _w(b, 2, "net-to-gross")
        t_094 = _w(b, 2, "nought point")
        t_np = s[3]
        t_89 = _w(b, 3, "eighty-nine")
        g_pay = sum(1 for f_, p_ in zip(LG.fluid, LG.net_pay) if p_ and f_ == "gas") * L.STEP
        o_pay = sum(1 for f_, p_ in zip(LG.fluid, LG.net_pay) if p_ and f_ == "oil") * L.STEP
        rows = [("gross", SUM["gross"], P.MUTED, t_gr, 0.25), ("net reservoir", SUM["net_reservoir"], "#e0a458", t_nr, -0.6)]
        for name, v, colr, t, y in rows:
            lab = st.text(name, 1.35, y, 0.18, P.TEXT, 0.4, align="l", kind="bold")
            bar = st.rect(BX0, y, 0.0001, 0.32, colr, 0.4, anchor="l", role="pill")
            st.fade_in([lab, bar], t - 0.2, 0.3)
            st.scale_to(bar, t, t + 0.9, sx=k * v)
            st.counter(BX0 + k * v + 0.12, y, t, t + 0.9, 0, v, fmt="{:.0f} m", size=0.17, color=P.TEXT, align="l")
        y = -1.45
        lab = st.text("net pay", 1.35, y, 0.18, P.TEXT, 0.4, align="l", kind="bold")
        bg_ = st.rect(BX0, y, 0.0001, 0.32, P.GAS, 0.4, anchor="l", role="pill")
        bo_ = st.rect(BX0 + k * g_pay, y, 0.0001, 0.32, P.OIL, 0.4, anchor="l", role="pill")
        st.fade_in([lab, bg_, bo_], t_np - 0.1, 0.3)
        st.scale_to(bg_, t_np, t_np + 0.7, sx=k * g_pay)
        st.scale_to(bo_, t_np + 0.6, t_np + 1.3, sx=k * o_pay)
        st.counter(BX0 + k * SUM["net_pay"] + 0.12, y, t_np, t_89 + 0.3, 0, SUM["net_pay"], fmt="{:.0f} m", size=0.17, color=P.TEXT, align="l")
        sub = st.text(f"{g_pay:.0f} m gas + {o_pay:.0f} m oil", BX0, y - 0.36, 0.14, P.MUTED, 0.4, align="l")
        st.fade_in(sub, t_89 + 0.3, 0.4)
        # N/G computed live
        ntg_txt = f"N/G = net reservoir / gross = {SUM['net_reservoir']:.0f} / {SUM['gross']:.0f} ="
        nw = st.measure(ntg_txt, 0.18, "mono")
        plate = st.rect(1.35 + (nw + 0.9) / 2 - 0.15, -2.45, nw + 0.95, 0.5, P.PANEL2, 0.45, role="pill")
        ntg = st.text(ntg_txt, 1.35, -2.45, 0.18, P.TEXT, 0.5, align="l", kind="mono")
        st.fade_in([plate, ntg], t_ntg - 0.2, 0.4)
        st.counter(1.35 + nw + 0.12, -2.45, t_094 - 0.4, t_094 + 0.6, 0.0, SUM["ntg"], fmt="{:.2f}", size=0.2, color=P.WARN, align="l", kind="mono")
        sim = _lbl(st, 4.5, -3.25, "cutoffs illustrative: real ones depend on the field", P.SIM_BADGE, 0.15)
        st.fade_in(sim, s[4] - 0.1, 0.4)


# ====================================================================================================== 8.10 the verdict
def beat_verdict(st, tl):
    b = tl["8.10"]
    s = b.sent
    with st.span(b.start, b.end):
        t0 = b.start + 0.1
        q = st.text("Is ours a discovery?", -6.0, 3.05, 0.42, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(q, s[0] - 0.1, 0.45)
        NY = 1.55
        nodes = [("hydrocarbons present?", -3.85, s[1]), ("movable?", 0.35, s[2])]
        boxes = []
        for txt, x, t in nodes:
            p_ = _lbl(st, x, NY, txt, P.TEXT, 0.22, z=0.6)
            st.fade_in(p_, t - 0.3, 0.35)
            boxes.append(p_)
        # connectors (grey, then lit teal)
        c0 = st.line([(-5.85, 2.75), (-5.85, NY), (-3.85 - 1.55, NY)], P.MUTED, 0.03, 0.4, alpha=0.6)
        c1 = st.line([(-3.85 + 1.55, NY), (0.35 - 0.75, NY)], P.MUTED, 0.03, 0.4, alpha=0.6)
        c2 = st.line([(0.35 + 0.75, NY), (3.15, NY)], P.MUTED, 0.03, 0.4, alpha=0.6)
        st.draw_on(c0, s[1] - 0.6, s[1] - 0.2)
        # evidence 1: the columns from the model contacts
        t_g = _w(b, 1, "forty")
        t_o = _w(b, 1, "fifty-five")
        EX, EY = -3.85, 0.05
        k_ = 0.016
        gas_c = st.rect(EX - 1.0, EY + 0.45, 0.42, 0.0001, P.GAS, 0.5, anchor="t")
        oil_c = st.rect(EX - 1.0, EY + 0.45 - k_ * (M.GOC - M.RES_TOP), 0.42, 0.0001, P.OIL, 0.5, anchor="t")
        st.fade_in(gas_c, t_g - 0.4, 0.1)
        st.scale_to(gas_c, t_g - 0.4, t_g + 0.3, sy=k_ * (M.GOC - M.RES_TOP))
        st.fade_in(oil_c, t_o - 0.5, 0.1)
        st.scale_to(oil_c, t_o - 0.5, t_o + 0.3, sy=k_ * (M.OWC - M.GOC))
        gl = st.text(f"gas ≈ {M.GOC - M.RES_TOP:.0f} m", EX - 0.6, EY + 0.45 - k_ * (M.GOC - M.RES_TOP) / 2, 0.18, P.GAS, 0.5, align="l", kind="bold")
        ol = st.text(f"oil ≈ {M.OWC - M.GOC:.0f} m", EX - 0.6, EY + 0.45 - k_ * (M.GOC - M.RES_TOP) - k_ * (M.OWC - M.GOC) / 2, 0.18, P.OIL, 0.5,
                     align="l", kind="bold")
        st.fade_in(gl, t_g, 0.3)
        st.fade_in(ol, t_o, 0.3)
        ck1 = _check(st, -3.85 + 1.75, NY + 0.42, b.sent_end[1] - 0.4)
        st.draw_on(c1, b.sent_end[1] - 0.3, s[2] - 0.2)
        st.recolor(c0, b.sent_end[1] - 0.4, b.sent_end[1], P.SAFE)
        # evidence 2: the sample bottle
        BXb, BYb = 0.35, -0.15
        bottle = [st.rect(BXb - 0.6, BYb, 0.42, 1.0, P.PANEL2, 0.5, role="card"), st.rect(BXb - 0.6, BYb + 0.6, 0.18, 0.2, P.STEEL, 0.5)]
        bfill = st.rect(BXb - 0.6, BYb - 0.44, 0.32, 0.0001, P.OIL, 0.51, anchor="b")
        bl = st.text("the tester\npumped them out", BXb - 0.25, BYb, 0.16, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(bottle + [bl], s[2] + 0.1, 0.35)
        st.fade_in(bfill, s[2] + 0.2, 0.1)
        st.scale_to(bfill, s[2] + 0.3, s[2] + 1.6, sy=0.8)
        ck2 = _check(st, 0.35 + 1.0, NY + 0.42, b.sent_end[2] - 0.3)
        st.recolor(c1, b.sent_end[2] - 0.3, b.sent_end[2], P.SAFE)
        # Sodir definition card
        t_def = s[3]
        CY = -1.95
        card = st.rect(1.0, CY, 13.0, 1.45, P.PANEL2, 0.45)
        bar = st.rect(-5.38, CY, 0.06, 1.1, P.SAFE, 0.46, role="shaft")
        qt = st.text("“A discovery: a petroleum deposit in which testing, sampling or logging has shown the probability of mobile petroleum.”",
                     -5.15, CY + 0.25, 0.18, P.TEXT, 0.47, align="l", kind="bold")
        src = st.text("Norwegian Offshore Directorate (Sodir) — covers both technical and commercial discoveries", -5.15, CY - 0.3, 0.14, P.MUTED,
                      0.47, align="l")
        st.fade_in([card, bar, qt, src], t_def - 0.1, 0.45)
        # the outcome
        t_dis = _w(b, 3, "a discovery")
        st.draw_on(c2, t_dis - 0.6, t_dis - 0.1)
        st.recolor(c2, t_dis - 0.2, t_dis + 0.1, P.SAFE)
        dis = _lbl(st, 5.3, NY, "DISCOVERY (technical)", "#06201c", 0.24, bg=P.SAFE, z=0.65)
        st.pop_in(dis[0], t_dis, 0.4)
        st.fade_in(dis[1], t_dis + 0.1, 0.3)
        st.ripple(5.3, NY, t_dis, t_dis + 1.6, P.SAFE, period=0.8, r0=0.4, r1=2.0)
        # will it pay? (not answered by this bar)
        t_pay = _w(b, 4, "will pay")
        c3 = st.dashed((5.3, NY - 0.35), (5.3, 0.2), P.MUTED, 0.03, 0.1, 0.08, 0.4)
        pay = _lbl(st, 5.3, -0.1, "will it pay?  not yet known", P.MUTED, 0.18, z=0.6)
        st.fade_in(c3, _w(b, 4, "technical") - 0.1, 0.3)
        st.fade_in(pay, t_pay - 0.6, 0.35)
        # dry hole: still data (greyed branch)
        t_dry = _w(b, 5, "dry hole")
        c4 = st.dashed((-5.85, NY - 0.05), (-5.85, -3.05), P.MUTED, 0.03, 0.1, 0.08, 0.4, alpha=0.7)
        nol = st.text("no", -5.7, 0.4, 0.14, P.MUTED, 0.4, align="l", kind="bold")
        dry = _lbl(st, -5.85, -3.3, "DRY HOLE: still data about the basin", P.MUTED, 0.18, align="l", z=0.6)
        st.fade_in(c4 + [nol], t_dry - 0.5, 0.35)
        st.fade_in(dry, t_dry - 0.2, 0.4)


def build(st, tl):
    F.header(st, tl)
    F.well_strip(st, 0.0, tl.dur, strings=[p.name for p in M.programme()], marker=M.TD)
    beat_ladder(st, tl)
    beat_mudlog(st, tl)
    beat_lwd(st, tl)
    beat_archie(st, tl)
    beat_gradients(st, tl)
    beat_samples(st, tl)
    beat_core(st, tl)
    beat_dst(st, tl)
    beat_netpay(st, tl)
    beat_verdict(st, tl)
