"""Ch 5: Casing and tubular design.

5.01 tunnel lining -> casing, the grade tag (P110 = 110 ksi ≈ 758 MPa), sour service (hydrogen into a hard lattice, a crack)
5.02 three loads, three ways to fail: burst (net internal pressure, 0.875 · 2Yt/D), collapse (thin buckles, thick yields,
     D/t slider), tension (buoyed weight hanging from the hook, max at the top, the connection as the weak link)
5.03 the design basis: shut-in gas kick (burst), lost circulation with the level falling inside (collapse), running,
     shock and overpull (tension); a design-basis table fills in
5.04 von Mises ellipse centred on the origin vs the uniaxial rectangle; design factor; the puzzle and its answer
5.05 load vs depth: single-weight rating fails at both ends; tapered capacity steps fix it
5.06 API thread (spiral leak path + compound) vs premium (cone-on-cone seal + torque shoulder); make-up on a torque-turn plot
5.07 the last-set casing and its cement as a well barrier element; the conductor is structure, not barrier

Casing LOADS get chapter-local colours (they are neither fluids nor formation pressures): burst rose, collapse lavender,
tension mint. The von Mises ellipse is drawn in white; the design-factor ellipse in the safe teal.
"""
from __future__ import annotations
import math

import skia

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common.shapes import Cutaway, pill
from scenes.common.stage import Track
from scenes.common.look import col, hex_rgb, lighten, darken, wrap_to

TITLE = "Casing and tubular design"

L_BURST = "#ff9de2"      # burst load (net internal pressure)
L_COLL = "#a98bff"       # collapse load (net external pressure)
L_TENS = "#80ed99"       # tension load (axial pull)
DOPE = "#8f9bab"         # thread compound (a grey grease; not a fluid colour)
H_ATOM = "#f4f7fb"       # hydrogen atoms in the steel lattice
PIN_C, BOX_C = "#b4c2d4", "#5d6c82"


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
    """0..1 envelope: fades in from a, out before b."""
    if t < a or t > b:
        return 0.0
    return min(1.0, (t - a) / d, (b - t) / d)


def chip(st, x, y, text, fg=P.TEXT, size=0.2, align="c", bg=P.PANEL2, z=0.5):
    return pill(st, x, y, text, bg, fg, size, z, align=align)


def leader(st, x0, y0, x1, y1, color=P.MUTED, z=0.45):
    return [st.line([(x0, y0), (x1, y1)], color, 0.022, z, alpha=0.85), st.circle(x1, y1, 0.045, color, z + 0.01, role="disc")]


def _path(pts, close=False):
    p = skia.Path()
    p.moveTo(float(pts[0][0]), float(pts[0][1]))
    for q in pts[1:]:
        p.lineTo(float(q[0]), float(q[1]))
    if close:
        p.close()
    return p


def _fill(c, pts, color, a):
    if a > 0.003:
        c.drawPath(_path(pts, True), skia.Paint(Color=col(hex_rgb(color), a), AntiAlias=True))


def _stroke(c, pts, color, a, w=0.04, close=False, look=None, glow=False):
    if a <= 0.003:
        return
    rgb = hex_rgb(color)
    path = _path(pts, close)
    if glow and look is not None:
        c.drawPath(path, skia.Paint(Color=col(rgb, 0.4 * a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w * 2.6,
                                    StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join,
                                    MaskFilter=look._blur(max(3.0, w * look.k * 0.8))))
    c.drawPath(path, skia.Paint(Color=col(rgb, a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w,
                                StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join))


def _arrow(c, x0, y0, x1, y1, color, a, w=0.06, head=0.2, look=None, glow=True):
    """Procedural arrow (round shaft + head), for arrows that follow moving geometry."""
    L = math.hypot(x1 - x0, y1 - y0)
    if a <= 0.003 or L < 1e-3:
        return
    head = min(head, L * 0.6)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    bx, by = x1 - ux * head, y1 - uy * head
    nx, ny = -uy, ux
    hw = head * 0.55
    tri = [(x1, y1), (bx + nx * hw, by + ny * hw), (bx - nx * hw, by - ny * hw)]
    rgb = hex_rgb(color)
    if glow and look is not None:
        g = skia.Paint(Color=col(rgb, 0.35 * a), AntiAlias=True, MaskFilter=look._blur(max(3.0, w * look.k * 0.9)))
        c.drawPath(_path([(x0, y0), (bx, by)]), skia.Paint(Color=col(rgb, 0.35 * a), AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                                         StrokeWidth=w * 2.2, StrokeCap=skia.Paint.kRound_Cap,
                                                         MaskFilter=look._blur(max(3.0, w * look.k * 0.9))))
        c.drawPath(_path(tri, True), g)
    c.drawPath(_path([(x0, y0), (bx + ux * 0.02, by + uy * 0.02)]),
               skia.Paint(Color=col(rgb, a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, StrokeCap=skia.Paint.kRound_Cap))
    c.drawPath(_path(tri, True), skia.Paint(Color=col(rgb, a), AntiAlias=True))


def counter(st, x, y, t0, t1, v0, v1, fmt, t_out, size=0.3, color=P.TEXT, align="l", kind="mono", z=0.6):
    """A number that counts v0 -> v1 over [t0, t1] and fades out at t_out (Stage.counter cannot fade out)."""
    def draw(c, t, look):
        a = min(1.0, (t - t0 + 0.3) / 0.3, (t_out + 0.35 - t) / 0.35)
        if a <= 0:
            return
        v = v0 + (v1 - v0) * _sm((t - t0) / max(t1 - t0, 1e-6))
        look.draw_text(c, fmt.format(v), x, y, size, color, a, align, kind)
    st.procedural(max(t0 - 0.3, 0.0), t_out + 0.4, z, draw)


def rip(st, x, y, t0, t1, color, end, period=1.2, **kw):
    """st.ripple that is guaranteed to be gone by `end` (the last ring finishes before it; drawing is clipped at it)."""
    t1 = min(t1, end - period * 1.6)
    if t1 <= t0:
        return
    st.ripple(x, y, t0, t1, color, period=period, **kw)
    a, b, z, fn = st.procedurals[-1]
    st.procedurals[-1] = (a, min(b, end), z, fn)


def _ptag(c, look, x, y, text, color, a=1.0, size=0.15, align="c", bg=P.PANEL2):
    """Procedural label on a rounded plate (for labels that ride on moving geometry)."""
    if a <= 0.003:
        return
    from scenes.common.look import measure
    from scenes.common.stage import TEXT_SCALE, MIN_TEXT
    w = measure(text, size, "bold") + 0.22
    h = max(size * TEXT_SCALE, MIN_TEXT) * 1.22 + 0.1
    cx = x if align == "c" else (x + w / 2 if align == "l" else x - w / 2)
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(cx - w / 2, y - h / 2, cx + w / 2, y + h / 2), h / 2, h / 2)
    c.drawRRect(rr, skia.Paint(Color=col(hex_rgb(bg), 0.92 * a), AntiAlias=True))
    look.draw_text(c, text, cx, y, size, color, a, "c", "bold")


def _mixc(c1, c2, f):
    a, b = hex_rgb(c1), hex_rgb(c2)
    return "#%02x%02x%02x" % tuple(int(round((x + (y - x) * f) * 255)) for x, y in zip(a, b))


def _ring_pts(cx, cy, rfun, n=144, th0=0.0, th1=2 * math.pi):
    out = []
    for i in range(n + 1):
        th = th0 + (th1 - th0) * i / n
        r = rfun(th)
        out.append((cx + r * math.cos(th), cy + r * math.sin(th)))
    return out


def _draw_ring(c, cx, cy, ro, ri, color, a, gap_at=None, gap=0.0, look=None, hot=0.0):
    """Annulus between radius functions ro(th) > ri(th); optional split of angular width `gap` (rad) at angle gap_at."""
    if a <= 0.003:
        return
    if gap_at is not None and gap > 1e-3:
        th0, th1 = gap_at + gap / 2, gap_at + 2 * math.pi - gap / 2
        pts = _ring_pts(cx, cy, ro, 160, th0, th1) + list(reversed(_ring_pts(cx, cy, ri, 160, th0, th1)))
        _fill(c, pts, color, a)
    else:
        path = _path(_ring_pts(cx, cy, ro), True)
        path.addPath(_path(_ring_pts(cx, cy, ri), True))
        path.setFillType(skia.PathFillType.kEvenOdd)
        c.drawPath(path, skia.Paint(Color=col(hex_rgb(color), a), AntiAlias=True))
    # edge highlights: light outer rim, darker inner rim
    _stroke(c, _ring_pts(cx, cy, ro), "#e9eff7", 0.55 * a, 0.018)
    _stroke(c, _ring_pts(cx, cy, ri), "#3b4658", 0.6 * a, 0.018)
    if hot > 0.01 and look is not None:
        path = _path(_ring_pts(cx, cy, ro), True)
        c.drawPath(path, skia.Paint(Color=col(hex_rgb(P.BAD), 0.3 * hot * a), AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                    StrokeWidth=0.09, MaskFilter=look._blur(8 * look.w / 1920)))


# ====================================================================================================== 5.01 lining, grade, sour service
def beat_lining(st, tl):
    b = tl["5.01"]
    s = b.sent
    CX, CY = -3.0, 0.35
    RC, RS, RI = 2.0, 1.72, 1.42              # hole wall (cement outer), steel outer, steel inner
    t_morph = s[1] - 0.35
    with st.span(b.start, s[2] + 0.2):
        rock = st.rect(CX, CY, 6.0, 5.6, P.ROCK, 0.0)
        hole = st.circle(CX, CY, RC, P.BG, 0.02, role="hole")
        st.fade_in([rock, hole], b.start + 0.05, 0.5)
        # a tunnel: segmented lining, a track bed
        segs = []
        n = 9
        for k in range(n):
            a0, a1 = 2 * math.pi * k / n + 0.035, 2 * math.pi * (k + 1) / n - 0.035
            pts = [(CX + 1.62 * math.cos(a0 + (a1 - a0) * i / 12), CY + 1.62 * math.sin(a0 + (a1 - a0) * i / 12)) for i in range(13)]
            pts += [(CX + RC * math.cos(a1 - (a1 - a0) * i / 12), CY + RC * math.sin(a1 - (a1 - a0) * i / 12)) for i in range(13)]
            segs.append(st.poly(pts, "#7d8696", 0.05))
        bed = [st.rect(CX, CY - 1.12, 2.3, 0.16, "#59626f", 0.04),
               st.rect(CX - 0.45, CY - 0.98, 0.1, 0.1, P.STEEL_DK, 0.045), st.rect(CX + 0.45, CY - 0.98, 0.1, 0.1, P.STEEL_DK, 0.045)]
        tun = chip(st, CX, CY + RC + 0.42, "a tunnel lining", P.TEXT, 0.22)
        st.fade_in(segs + bed, b.start + 0.25, 0.5)
        st.fade_in(tun, s[0] + 0.3, 0.4)
        st.fade_out(segs + bed + tun, t_morph, 0.55)
        # ... becomes the casing: cement sheath, steel, mud in the bore
        cem = st.ring(CX, CY, RC, RC - RS, P.CEMENT, 0.05)
        steel = st.ring(CX, CY, RS, RS - RI, P.STEEL, 0.06)
        rim = st.ring(CX, CY, RS + 0.012, 0.03, "#e9eff7", 0.065, alpha=0.6)
        mud = st.circle(CX, CY, RI, P.MUD, 0.04, alpha=0.35, role="disc")
        st.fade_in([cem, mud], t_morph + 0.1, 0.5)
        st.pop_in([steel, rim], t_morph + 0.15, 0.5)
        st.fade_in([steel, rim], t_morph + 0.15, 0.3)
        cs = chip(st, CX, CY + RC + 0.42, "casing: a steel lining", P.TEXT, 0.22)
        st.fade_in(cs, t_morph + 0.35, 0.4)
        # the three jobs, each as it is spoken
        t_open, t_pr, t_iso = W(b, 1, "holds the hole open"), W(b, 1, "contains pressure"), W(b, 1, "isolates formations")
        sq = []
        for k in range(8):
            th = math.pi / 8 + k * math.pi / 4
            sq += st.arrow(CX + 2.75 * math.cos(th), CY + 2.75 * math.sin(th), CX + 2.06 * math.cos(th), CY + 2.06 * math.sin(th),
                           P.TEXT, 0.06, 0.2, 0.3, alpha=0.85)
        st.fade_in(sq, t_open - 0.1, 0.35)
        pa = []
        for k in range(8):
            th = k * math.pi / 4
            pa += st.arrow(CX + 0.45 * math.cos(th), CY + 0.45 * math.sin(th), CX + 1.34 * math.cos(th), CY + 1.34 * math.sin(th),
                           P.MUD, 0.06, 0.2, 0.3)
        st.fade_in(pa, t_pr - 0.1, 0.35)
        jobs = [chip(st, 0.55, 2.0, "holds the hole open", P.TEXT, 0.22, "l"),
                chip(st, 0.55, 1.05, "contains pressure", P.MUD, 0.22, "l"),
                chip(st, 0.55, 0.1, "isolates formations, with its cement", P.CEMENT, 0.22, "l")]
        for j, t in zip(jobs, (t_open, t_pr, t_iso)):
            st.fade_in(j, t, 0.4)
        st.fade(sq, t_pr - 0.1, t_pr + 0.4, 1.0, 0.35)
        st.fade(pa, t_iso - 0.1, t_iso + 0.4, 1.0, 0.35)
        rip(st, CX, CY, t_iso - 0.1, t_iso + 2.6, P.CEMENT, period=0.5, r0=RC - 0.1, r1=RC + 0.7, width=0.05, z=0.3, end=s[2] - 0.45)
        st.fade_out([rock, hole, cem, steel, rim, mud] + cs + sq + pa + jobs[0] + jobs[1] + jobs[2], s[2] - 0.45, 0.45)
    _grade(st, b)
    _sour(st, b)


def _grade(st, b):
    s = b.sent
    t0, t1 = s[2] - 0.05, s[3] + 0.9
    with st.span(t0, t1 + 0.5):
        cut = Cutaway(st, -4.25, 3.3, -3.2, hole_w=1.9, pipe_w=1.15, wall=0.12, rock_w=0.95)
        base = cut.draw()
        cem = [cut.static_gap(sd, P.CEMENT, 3.3, -3.2, 0.05) for sd in "lr"]
        bore = cut.static_bore(P.MUD, 3.3, -3.2, 0.05, alpha=0.4)
        cl = st.text("casing in the hole", -4.25, -3.45, 0.17, P.MUTED, 0.3, kind="bold")
        st.fade_in(base + cem + [bore, cl], t0, 0.5)
        # the stencil on the pipe
        x_w = cut.pipe[1]
        tag0 = chip(st, -4.25, 1.4, "P110", P.WARN, 0.2, z=0.55)
        st.fade_in(tag0, t0 + 0.4, 0.4)
        # big decode
        big = "P110"
        w = st.measure(big, 1.0, "bold")
        xc = 1.45
        x0 = xc - w / 2
        wp = st.measure("P", 1.0, "bold")
        xP, xN = x0 + wp / 2, x0 + wp + (w - wp) / 2
        g = st.text(big, xc, 1.55, 1.0, P.TEXT, 0.4, kind="bold")
        ld = leader(st, xc - w / 2 - 0.15, 1.55, -4.25 + 0.42, 1.4)
        st.fade_in([g] + ld, s[2] + 0.1, 0.5)
        t_let, t_num = W(b, 2, "a letter"), W(b, 2, "a number")
        brP = st.line([(xP - 0.3, 0.82), (xP - 0.3, 0.72), (xP + 0.3, 0.72), (xP + 0.3, 0.82)], P.WARN, 0.035, 0.4)
        brN = st.line([(xN - 0.85, 0.82), (xN - 0.85, 0.72), (xN + 0.85, 0.72), (xN + 0.85, 0.82)], P.WARN, 0.035, 0.4)
        lP = st.text("grade letter", xP, 0.42, 0.19, P.WARN, 0.4, kind="bold")
        lN = st.text("minimum yield, ksi", xN + 0.25, -0.05, 0.19, P.WARN, 0.4, kind="bold")
        lNl = st.line([(xN, 0.72), (xN, 0.12)], P.WARN, 0.022, 0.4, alpha=0.7)
        st.draw_on(brP, t_let - 0.1, t_let + 0.35)
        st.fade_in(lP, t_let + 0.1, 0.35)
        st.draw_on(brN, t_num - 0.1, t_num + 0.35)
        st.fade_in([lN, lNl], t_num + 0.1, 0.35)
        # the number, counted
        t_psi = W(b, 2, "one hundred and ten thousand")
        t_mpa = W(b, 2, "about")
        counter(st, -0.6, -1.15, t_psi, W(b, 2, "psi", 1.0), 0, 110000, "{:,.0f} psi", t1 - 0.4, 0.36, P.TEXT)
        t_tag = W(b, 2, "megapascals") - 0.5
        counter(st, 2.85, -1.15, t_mpa, t_tag - 0.15, 0, 758, "≈ {:.0f} MPa", t1 - 0.4, 0.36, P.WARN)
        eq = st.text("= 110 ksi", -0.6, -1.75, 0.2, P.MUTED, 0.4, align="l", kind="mono")
        st.fade_in(eq, W(b, 2, "psi", 1.0) - 0.2, 0.4)
        # the pipe tag (once both numbers have landed)
        tag = chip(st, -0.6, -2.55, "P110: 110 ksi ≈ 758 MPa", P.WARN, 0.26, "l", z=0.55)
        tl_ = leader(st, -0.6, -2.55, x_w + 0.02, -2.0, P.WARN)
        st.fade_in(tag + tl_, t_tag, 0.45)
        rip(st, x_w + 0.02, -2.0, t_tag + 0.2, t_tag + 1.0, P.WARN, period=0.8, r0=0.15, r1=0.6, z=0.6, end=t1 - 0.4)
        st.fade_out(base + cem + [bore, cl, g, brP, brN, lP, lN, lNl, eq] + tag0 + ld + tag + tl_, t1 - 0.4, 0.45)


def _sour(st, b):
    s = b.sent
    t0 = s[3] + 0.5
    X0, X1, YS, YB = -5.85, -1.0, 1.25, -3.1          # steel lattice box; YS = the steel surface (sour fluid above)
    with st.span(t0, b.end):
        card = st.rect((X0 + X1) / 2, (YB + 2.45) / 2, X1 - X0 + 0.3, 2.45 - YB + 0.3, P.PANEL, 0.0)
        fluid = st.rect((X0 + X1) / 2, (YS + 2.35) / 2, X1 - X0, 2.35 - YS, P.SEA, 0.02, alpha=0.55)
        surf = st.rect((X0 + X1) / 2, YS, X1 - X0, 0.03, P.TEXT, 0.1, alpha=0.6)
        fl = st.text("sour fluid", X0 + 0.1, 2.12, 0.17, P.MUTED, 0.2, align="l", kind="bold")
        sl = st.text("hard steel", X0 + 0.1, YB + 0.12, 0.17, P.TEXT, 0.35, align="l", kind="bold")
        atoms = []
        xs = [X0 + 0.25 + 0.4 * i for i in range(12)]
        ys = [YS - 0.25 - 0.4 * j for j in range(11)]
        for x in xs:
            for y in ys:
                if x < X1 - 0.1 and y > YB + 0.3:
                    atoms.append(st.circle(x, y, 0.115, P.STEEL_DK, 0.05, role="disc"))
        mol = []
        for (mx, my) in ((-5.0, 1.75), (-3.6, 1.95), (-2.2, 1.7)):
            mol.append(st.text("H₂S", mx, my, 0.2, P.WARN, 0.2, kind="bold"))
        st.fade_in([card, fluid, surf, fl, sl] + atoms, t0, 0.5)
        st.fade_in(mol, t0 + 0.4, 0.4)
        # hydrogen diffusing in, between the iron atoms
        t_h = W(b, 3, "drives hydrogen")
        for k, xg in enumerate((-5.25, -4.45, -3.65, -2.85, -2.05, -1.45)):
            pts = [(xg + 0.2, 1.75), (xg + 0.2, YS + 0.05)]
            y, x = YS, xg + 0.2
            for j in range(6):
                y -= 0.4
                x += 0.4 if (j + k) % 2 else -0.4
                x = min(max(x, X0 + 0.45), X1 - 0.3)
                pts.append((x, y))
            st.flow(pts, t_h - 0.2 + 0.12 * k, b.end, H_ATOM, n=5, speed=0.55, r=0.045, z=0.3, alpha=0.95)
        hl = chip(st, X1 - 0.15, -0.55, "hydrogen atoms", H_ATOM, 0.17, "r", z=0.55)
        st.fade_in(hl, t_h + 0.8, 0.4)
        # the crack
        t_cr = W(b, 3, "cracks it")
        cpts = [(-3.25, YS + 0.01), (-3.45, YS - 0.4), (-3.25, YS - 0.8), (-3.45, YS - 1.2), (-3.3, YS - 1.6), (-3.55, YS - 2.05),
                (-3.4, YS - 2.5)]
        crack = st.line(cpts, P.BG, 0.12, 0.4)
        crack2 = st.line(cpts, P.BAD, 0.03, 0.41, alpha=0.8)
        st.draw_on([crack, crack2], t_cr - 0.1, t_cr + 1.5, "BEZIER")
        rip(st, -3.4, YS - 2.5, t_cr + 1.3, t_cr + 3.0, P.BAD, period=0.8, r0=0.1, r1=0.7, z=0.6, end=b.end)
        cl = chip(st, -3.0, YS - 2.95, "cracking", P.BAD, 0.18, "l", z=0.55)
        st.fade_in(cl, t_cr + 1.0, 0.4)
        # hardness gauge: sour grades below the cap, P110 above it
        GX, G0, G1, YC = 0.9, -2.9, 1.7, -0.5
        track = st.rect(GX, (G0 + G1) / 2, 0.24, G1 - G0, P.GRID, 0.2, role="pill")
        gt = st.text("STEEL HARDNESS", GX, G1 + 0.4, 0.18, P.MUTED, 0.3, kind="bold")
        hi = st.text("harder", GX - 0.3, G1 - 0.1, 0.16, P.MUTED, 0.3, align="r")
        lo = st.text("softer", GX - 0.3, G0 + 0.1, 0.16, P.MUTED, 0.3, align="r")
        st.fade_in([track, gt, hi, lo], s[3] + 0.6, 0.5)
        t_cap = W(b, 3, "cap hardness")
        ok = st.rect(GX, (G0 + YC) / 2, 0.24, YC - G0, P.SAFE, 0.22, alpha=0.75, role="pill")
        bad = st.rect(GX, (YC + G1) / 2, 0.24, G1 - YC, P.BAD, 0.22, alpha=0.45, role="pill")
        cap = st.rect(GX + 0.15, YC, 0.9, 0.05, P.TEXT, 0.3)
        capl = st.text("sour grades: hardness capped", GX + 0.75, YC, 0.2, P.TEXT, 0.35, align="l", kind="bold")
        st.fade_in([ok, bad], t_cap - 0.3, 0.4)
        st.fade_in([cap, capl], t_cap, 0.4)
        t_sg = W(b, 3, "sour-service grades")
        d1 = st.circle(GX, -1.75, 0.13, P.SAFE, 0.4)
        l1 = chip(st, GX + 0.45, -1.75, "sour-service grades  ✓", P.SAFE, 0.19, "l")
        st.pop_in(d1, t_sg, 0.4)
        st.fade_in(l1, t_sg + 0.1, 0.4)
        t_p = W(b, 3, "P one-ten")
        d2 = st.circle(GX, 0.75, 0.13, P.BAD, 0.4)
        l2 = chip(st, GX + 0.45, 0.75, "P110: too hard for most sour wells", P.BAD, 0.19, "l")
        st.pop_in(d2, t_p, 0.4)
        st.fade_in(l2, t_p + 0.1, 0.4)
        rip(st, GX, 0.75, t_p + 0.2, t_p + 2.4, P.BAD, period=0.8, r0=0.15, r1=0.7, end=b.end)


# ====================================================================================================== 5.02 three loads
RING = (-2.7, 0.15)


def _ring_proc(st, a, b, z, cx, cy, state):
    """A pipe cross-section that deforms. state(t) -> dict(R, w, eps, a, hot, gap, gap_at, fill, arrows=[(kind, len, color, alpha)])."""
    def draw(c, t, look):
        S = state(t)
        A = S.get("a", 1.0)
        if A <= 0.003:
            return
        R, w, eps = S["R"], S["w"], S.get("eps", 0.0)
        ro = lambda th: R * (1 + eps * math.cos(2 * th)) + w / 2
        ri = lambda th: R * (1 + eps * math.cos(2 * th)) - w / 2
        if S.get("fill"):
            fc, fa = S["fill"]
            _fill(c, _ring_pts(cx, cy, ri), fc, fa * A)
        for kind, ln, colr, aa, n in S.get("arrows", []):
            if aa * A <= 0.003 or ln <= 0.01:
                continue
            for k in range(n):
                th = 2 * math.pi * (k + 0.5) / n
                ux, uy = math.cos(th), math.sin(th)
                if kind == "in":           # outside pressure: from outside onto the outer surface
                    r1 = ro(th) + 0.03
                    r0 = r1 + ln
                else:                      # inside pressure: from the centre region onto the inner surface
                    r1 = ri(th) - 0.03
                    r0 = max(r1 - ln, 0.05)
                _arrow(c, cx + r0 * ux, cy + r0 * uy, cx + r1 * ux, cy + r1 * uy, colr, aa * A, 0.05, 0.17, look)
        colr = _mixc(P.STEEL, "#ffb4a2", 0.45 * S.get("hot", 0.0))
        _draw_ring(c, cx, cy, ro, ri, colr, A, S.get("gap_at"), S.get("gap", 0.0), look, S.get("hot", 0.0))
    st.procedural(a, b, z, draw)


def beat_modes(st, tl):
    b = tl["5.02"]
    s = b.sent
    with st.span(b.start, b.end):
        # mode chips: three ways to fail (big in the middle, then a tab row at the top)
        names = [("BURST", L_BURST), ("COLLAPSE", L_COLL), ("TENSION", L_TENS)]
        big = []
        for i, (nm, cc) in enumerate(names):
            big.append(chip(st, -3.6 + 3.4 * i, 0.2, nm, cc, 0.4))
        for i, o in enumerate(big):
            st.fade_in(o, s[0] + 0.25 + 0.35 * i, 0.4)
            st.fade_out(o, s[1] - 0.45, 0.35)
        tabs = []
        x = -5.9
        for nm, cc in names:
            o = chip(st, x, 3.45, nm, cc, 0.2, "l")
            tabs.append(o)
            x += st.measure(nm, 0.2, "bold") + 0.75
        st.fade_in(tabs, s[1] - 0.2, 0.4)
        st.fade(tabs[1] + tabs[2], s[1] + 0.3, s[1] + 0.7, 1.0, 0.3)
        st.fade(tabs[1], s[3] - 0.3, s[3] + 0.1, 0.3, 1.0)
        st.fade(tabs[0], s[3] - 0.3, s[3] + 0.1, 1.0, 0.3)
        st.fade(tabs[2], s[6] - 0.3, s[6] + 0.1, 0.3, 1.0)
        st.fade(tabs[1], s[6] - 0.3, s[6] + 0.1, 1.0, 0.3)
    _burst(st, b)
    _collapse(st, b)
    _tension(st, b)


def _burst(st, b):
    s = b.sent
    cx, cy = RING
    t0, t1 = s[1] - 0.2, s[3] - 0.35
    t_in, t_out = W(b, 1, "pressure inside"), W(b, 1, "exceeds pressure outside")
    t_y = W(b, 1, "wall yields")
    t_split = t_y + 1.5
    R0, W0 = 1.45, 0.3

    def state(t):
        sw = 0.075 * _sm((t - t_y) / 1.3)
        return dict(R=R0 * (1 + sw), w=W0 / (1 + sw) ** 2, a=_env(t, t0, t1, 0.4), hot=_sm((t - t_y) / 1.0),
                    gap_at=math.radians(38), gap=math.radians(7) * _sm((t - t_split) / 0.5),
                    fill=(P.MUD, 0.28),
                    arrows=[("out", 0.85 * _sm((t - t_in) / 0.6), L_BURST, 1.0, 12),
                            ("in", 0.32 * _sm((t - t_out) / 0.6), L_BURST, 0.5, 12)])
    with st.span(t0, t1 + 0.1):
        _ring_proc(st, t0, t1 + 0.1, 0.3, cx, cy, state)
        th = math.radians(38)
        r = R0 * 1.075
        st.flow([(cx + (r - 0.3) * math.cos(th), cy + (r - 0.3) * math.sin(th)), (cx + (r + 0.9) * math.cos(th), cy + (r + 0.9) * math.sin(th))],
                t_split + 0.1, t1, P.MUD, n=8, speed=1.6, r=0.05, z=0.35, jitter=0.12)
        pin = chip(st, cx, cy, "inside", L_BURST, 0.17)
        pout = chip(st, cx + 2.35, cy - 1.9, "outside", L_BURST, 0.17)
        st.fade_in(pin, t_in + 0.4, 0.3)
        st.fade_in(pout, t_out + 0.3, 0.3)
        net = st.text("net load = inside − outside pressure", 0.55, 2.35, 0.24, P.TEXT, 0.4, align="l", kind="bold")
        st.fade_in(net, t_out + 0.2, 0.4)
        yl = chip(st, 0.55, 1.6, "the wall stretches, then yields", P.BAD, 0.2, "l")
        st.fade_in(yl, t_y + 0.1, 0.4)
        pl = st.text("like an over-pressured pipeline", 0.55, 0.95, 0.19, P.MUTED, 0.4, align="l")
        st.fade_in(pl, W(b, 1, "pipeline") - 0.3, 0.4)
        # the rating, on a wall 12.5 % thinner than nominal
        t_r = W(b, 2, "rating")
        f1 = st.text("P", 0.55, 0.0, 0.42, L_BURST, 0.4, align="l", kind="bold")
        f1s = st.text("burst", 0.85, -0.14, 0.17, L_BURST, 0.4, align="l", kind="bold")
        f2 = st.text("= 0.875 × 2 Y t / D", 1.62, 0.0, 0.42, P.TEXT, 0.4, align="l", kind="bold")
        leg = st.text("Y minimum yield   ·   t nominal wall   ·   D outside diameter", 0.55, -0.62, 0.16, P.MUTED, 0.4, align="l")
        st.fade_in([f1, f1s, f2], t_r, 0.45)
        st.fade_in(leg, t_r + 0.5, 0.45)
        # D and t on the ring
        dD = st.arrow(cx - R0 - W0 / 2, cy - 2.05, cx + R0 + W0 / 2, cy - 2.05, P.MUTED, 0.03, 0.14, 0.4) + \
            st.arrow(cx + R0 + W0 / 2, cy - 2.05, cx - R0 - W0 / 2, cy - 2.05, P.MUTED, 0.03, 0.14, 0.4)
        dDl = st.text("D", cx, cy - 2.32, 0.2, P.TEXT, 0.4, kind="bold")
        tick = [st.rect(cx - R0 - W0 / 2, cy - 1.0, 0.02, 1.9, P.MUTED, 0.39, alpha=0.6), st.rect(cx + R0 + W0 / 2, cy - 1.0, 0.02, 1.9, P.MUTED, 0.39, alpha=0.6)]
        st.fade_in(dD + tick + [dDl], t_r + 0.3, 0.4)
        # wall-tolerance bars
        t_tol = W(b, 2, "twelve and a half")
        BX, BY, BL = 0.55, -1.55, 4.4
        bar1 = st.rect(BX, BY, BL, 0.3, P.STEEL, 0.3, anchor="l")
        b1l = st.text("nominal wall  t", BX + BL + 0.15, BY, 0.18, P.TEXT, 0.4, align="l", kind="bold")
        bar2 = st.rect(BX, BY - 0.62, BL * 0.875, 0.3, P.STEEL, 0.3, anchor="l")
        miss = st.dashed((BX + BL * 0.875, BY - 0.62 + 0.15), (BX + BL, BY - 0.62 + 0.15), P.BAD, 0.03, 0.08, 0.06, 0.32) + \
            st.dashed((BX + BL * 0.875, BY - 0.62 - 0.15), (BX + BL, BY - 0.62 - 0.15), P.BAD, 0.03, 0.08, 0.06, 0.32) + \
            [st.line([(BX + BL, BY - 0.77), (BX + BL, BY - 0.47)], P.BAD, 0.03, 0.32)]
        b2l = st.text("0.875 t", BX + BL + 0.15, BY - 0.62, 0.18, P.TEXT, 0.4, align="l", kind="bold")
        b3l = chip(st, BX + BL * 0.9375, BY - 1.22, "−12.5 %: mill tolerance", P.BAD, 0.18)
        st.fade_in([bar1, b1l], t_tol - 0.5, 0.4)
        st.fade_in(bar2, t_tol - 0.1, 0.3)
        st.scale_to(bar2, t_tol - 0.1, t_tol + 0.9, sx=BL * 0.875)
        st.fade_in(miss + [b2l], t_tol + 0.6, 0.35)
        st.fade_in(b3l, W(b, 2, "mill tolerance") - 0.2, 0.4)
        objs = pin + pout + [net] + yl + [pl, f1, f1s, f2, leg] + dD + tick + [dDl, bar1, b1l, bar2, b2l] + miss + b3l
        st.fade_out(objs, t1 - 0.35, 0.4)


def _collapse(st, b):
    s = b.sent
    t0, t1 = s[3] - 0.3, s[6] + 0.15
    t_one_end = s[4] - 0.1
    cx, cy = RING
    t_gv = W(b, 3, "gives way")

    def single(t):
        wob = 0.06 * _sm((t - t_gv) / 0.7)
        return dict(R=1.3, w=0.24, eps=wob, a=_env(t, t0, t_one_end + 0.3, 0.4),
                    arrows=[("in", 0.6 * _sm((t - s[3] - 0.2) / 0.6), L_COLL, 1.0, 12)])
    TX, TY, KX = -3.85, 1.35, -0.15                # thin ring, thick ring centres
    t_bk, t_yl = W(b, 4, "buckles"), W(b, 4, "thick pipe yields")

    def thin(t):
        e = 0.17 * _sm((t - t_bk) / 1.4)
        return dict(R=0.95, w=0.075, eps=e, a=_env(t, t_one_end, t1, 0.4),
                    arrows=[("in", 0.42, L_COLL, 1.0, 10)])

    def thick(t):
        sh = 0.05 * _sm((t - t_yl) / 1.0)
        return dict(R=0.95 * (1 - sh), w=0.36, a=_env(t, t_one_end, t1, 0.4), hot=_sm((t - t_yl) / 0.8),
                    arrows=[("in", 0.42, L_COLL, 1.0, 10)])
    with st.span(t0, t1 + 0.1):
        _ring_proc(st, t0, t_one_end + 0.35, 0.3, cx, cy, single)
        _ring_proc(st, t_one_end, t1 + 0.1, 0.3, TX, TY, thin)
        _ring_proc(st, t_one_end, t1 + 0.1, 0.3, KX, TY, thick)
        net = st.text("net load = outside − inside pressure", 0.55, 2.35, 0.24, P.TEXT, 0.4, align="l", kind="bold")
        st.fade_in(net, s[3] + 0.3, 0.4)
        st.fade_out(net, t_one_end, 0.35)
        l1 = chip(st, TX, TY - 1.75, "thin wall: buckles", L_COLL, 0.2)
        l1b = st.text("like a crushed can (elastic)", TX, TY - 2.25, 0.17, P.MUTED, 0.4)
        l2 = chip(st, KX, TY - 1.75, "thick wall: yields first", P.BAD, 0.2)
        l2b = st.text("the steel itself gives", KX, TY - 2.25, 0.17, P.MUTED, 0.4)
        st.fade_in(l1, t_bk - 0.1, 0.35)
        st.fade_in(l1b, t_bk + 0.4, 0.35)
        st.fade_in(l2, t_yl - 0.1, 0.35)
        st.fade_in(l2b, t_yl + 0.4, 0.35)
        # D/t: high for the thin ring, low for the thick one
        t_dt = W(b, 5, "diameter-to-thickness")
        dts = [chip(st, TX, TY, "high D/t", P.TEXT, 0.17), chip(st, KX, TY, "low D/t", P.TEXT, 0.17)]
        st.fade_in(dts, t_dt + 0.3, 0.4)
        # slider: D/t from low (yield) to high (elastic buckling); a ring icon below it shows D and t
        SX0, SX1, SY = -5.0, 3.0, -2.05
        bands = [(SX0, -2.6, "yield", P.BAD), (-2.6, 0.8, "in between: most casing", P.TEXT), (0.8, SX1, "elastic buckling", L_COLL)]
        bobj = []
        for i, (a, c2, nm, cc) in enumerate(bands):
            bobj.append(st.rect((a + c2) / 2, SY, c2 - a - 0.06, 0.16, cc, 0.3, alpha=0.55, role="pill"))
            bobj.append(st.text(nm, (a + c2) / 2, SY - 0.68, 0.17, cc, 0.35, kind="bold"))
        sl = st.text("D/t", SX0 - 0.12, SY, 0.2, P.TEXT, 0.35, align="r", kind="bold")
        ends = [st.text("thick wall", SX0 + 0.05, SY + 0.66, 0.16, P.MUTED, 0.35, align="l"),
                st.text("thin wall", SX1 - 0.05, SY + 0.66, 0.16, P.MUTED, 0.35, align="r")]
        st.fade_in(bobj + [sl] + ends, t_dt - 0.2, 0.45)
        t_ib = W(b, 5, "in between")
        k0, k1, k2 = -4.3, 2.5, -0.9

        def knob(c, t, look):
            """The knob IS a pipe cross-section: its wall thins as the knob slides from thick-walled to thin-walled."""
            a = _env(t, t_dt, t1, 0.35)
            if a <= 0:
                return
            f = _sm((t - t_dt - 0.2) / 1.6)
            x = k0 + (k1 - k0) * f
            g = _sm((t - t_ib + 0.3) / 0.9)
            x = x + (k2 - x) * g
            u = (x - SX0) / (SX1 - SX0)
            R, wv = 0.3, 0.26 * (1 - u) + 0.035
            c.drawCircle(x, SY, R + wv / 2 + 0.05, skia.Paint(Color=col(hex_rgb(P.BG), 0.9 * a), AntiAlias=True))
            _draw_ring(c, x, SY, lambda th: R + wv / 2, lambda th: R - wv / 2, P.STEEL, a)
        st.procedural(t_dt, t1 + 0.1, 0.5, knob)
        st.fade(bobj[2:4], t_ib + 0.3, t_ib + 0.8, 1.0, 1.8)
        objs = l1 + l2 + [l1b, l2b] + dts[0] + dts[1] + bobj + [sl] + ends
        st.fade_out(objs, t1 - 0.35, 0.4)


def _tension(st, b):
    s = b.sent
    t0 = s[6] + 0.1
    t_w, t_pull = W(b, 6, "weight"), W(b, 6, "any pull")
    t_body, t_conn = W(b, 6, "pipe body"), W(b, 6, "weaker connection")
    SX, YT, YB = -3.9, 2.2, -2.9
    with st.span(t0, b.end):
        mud = st.rect(SX, (YT - 0.3 + YB - 0.3) / 2, 2.2, YT - YB, P.MUD, 0.02, alpha=0.22, role="flat")
        ml = st.text("mud", SX - 0.85, YB + 0.0, 0.17, P.MUD, 0.1, kind="bold")
        block = [st.rect(SX, YT + 0.62, 0.9, 0.36, P.STEEL_DK, 0.3), st.rect(SX, YT + 0.32, 0.14, 0.3, P.STEEL_DK, 0.3),
                 st.rect(SX, YT + 0.12, 0.64, 0.14, P.STEEL_DK, 0.31)]
        bl = st.text("hook", SX - 0.65, YT + 0.62, 0.17, P.MUTED, 0.3, align="r", kind="bold")
        pipe = st.rect(SX, YT, 0.42, YT - YB, P.STEEL, 0.2, anchor="t")
        cpl_y = [YT - 0.45, YT - 2.25, YT - 4.05]
        cpls = [st.rect(SX, y, 0.62, 0.3, P.STEEL, 0.25) for y in cpl_y]
        st.fade_in([mud, ml, pipe, bl] + block + cpls, t0, 0.5)
        # stretch: the string lengthens a little under its own weight (shown exaggerated)
        st.scale_to(pipe, t_w, t_w + 1.4, sy=(YT - YB) * 1.035)
        for k, o in enumerate(cpls):
            st.move(o, t_w, t_w + 1.4, dy=-(YT - cpl_y[k]) * 0.035)
        ref = st.rect(SX + 0.6, YB, 0.5, 0.025, P.MUTED, 0.3)
        refl = st.text("stretch", SX + 0.9, YB - 0.08, 0.15, P.MUTED, 0.3, align="l")
        st.fade_in([ref, refl], t_w + 0.6, 0.4)
        # tension along the string: a mint glow, strongest at the top
        def tglow(c, t, look):
            a = _env(t, t_w, b.end + 1, 0.5)
            if a <= 0:
                return
            n = 30
            op = 0.25 * _sm((t - t_pull) / 0.8)
            for i in range(n):
                y0 = YT - (YT - YB) * i / n
                y1 = YT - (YT - YB) * (i + 1) / n
                f = (1 - (i + 0.5) / n + op) / (1 + op)
                _fill(c, [(SX - 0.21, y0), (SX + 0.21, y0), (SX + 0.21, y1), (SX - 0.21, y1)], L_TENS, a * 0.75 * f)
        st.procedural(t_w, b.end, 0.22, tglow)
        # distributed weight: small down arrows; hook reaction up
        wts = []
        for y in (1.6, 0.6, -0.4, -1.4, -2.3):
            wts += st.arrow(SX - 0.55, y + 0.3, SX - 0.55, y - 0.2, P.TEXT, 0.035, 0.13, 0.3, alpha=0.8)
        wl = st.text("weight in mud\n(buoyed)", SX - 0.75, -0.9, 0.15, P.TEXT, 0.3, align="r")
        st.fade_in(wts + [wl], t_w + 0.2, 0.4)
        # T(z) diagram
        DX, DW = -1.2, 2.3

        def tri(c, t, look):
            a = _env(t, t_w + 0.3, b.end + 1, 0.5)
            if a <= 0:
                return
            op = 0.5 * _sm((t - t_pull) / 0.8)
            _stroke(c, [(DX, YT + 0.1), (DX, YB - 0.1)], P.MUTED, a, 0.025)
            pts = [(DX, YT), (DX + DW * 0.72 + op, YT), (DX + op, YB), (DX, YB)]
            _fill(c, pts, L_TENS, 0.28 * a)
            _stroke(c, [(DX + DW * 0.72 + op, YT), (DX + op, YB)], L_TENS, a, 0.045, look=look, glow=True)
            if op > 0.01:
                _fill(c, [(DX, YT), (DX + op, YT), (DX + op, YB), (DX, YB)], L_TENS, 0.42 * a)
            look.draw_text(c, "tension", DX + 0.05, YT + 0.32, 0.18, L_TENS, a, "l", "bold")
            look.draw_text(c, "max at the top", DX + DW * 0.72 + op + 0.12, YT - 0.05, 0.16, P.TEXT, a, "l", "bold")
            look.draw_text(c, "zero at the free end", DX + 0.12, YB + 0.05, 0.15, P.MUTED, a * (1 - op / 0.5), "l")
            if op > 0.01:
                look.draw_text(c, "a pull adds tension all the way down", DX + 0.12 + op, YB + 0.05, 0.15, L_TENS, a * op / 0.5, "l")
        st.procedural(t_w + 0.3, b.end, 0.4, tri)
        # the pull at the hook
        def hook(c, t, look):
            a = _env(t, t_w + 0.2, b.end + 1, 0.4)
            ln = 0.55 + 0.45 * _sm((t - t_pull) / 0.6)
            _arrow(c, SX + 0.75, YT - 0.2, SX + 0.75, YT - 0.2 + ln, L_TENS, a, 0.07, 0.22, look)
            if t > t_pull:
                look.draw_text(c, "+ any pull", SX + 0.95, YT + 0.15, 0.16, L_TENS, min(1.0, (t - t_pull) / 0.4) * a, "l", "bold")
        st.procedural(t_w + 0.2, b.end, 0.45, hook)
        # limits: pipe body, then (often) the weaker connection
        body = chip(st, 2.0, -0.7, "limit: the pipe body ...", P.TEXT, 0.2, "l")
        st.fade_in(body, t_body - 0.1, 0.35)
        st.recolor(cpls[0], t_conn, t_conn + 0.5, P.BAD)
        conn = chip(st, 2.0, -1.4, "... or, often, the weaker connection", P.BAD, 0.2, "l")
        cn2 = chip(st, -2.35, cpl_y[0], "connection", P.BAD, 0.15)
        st.fade_in(conn + cn2, t_conn, 0.4)
        rip(st, SX, cpl_y[0], t_conn + 0.1, t_conn + 2.5, P.BAD, period=0.8, r0=0.3, r1=0.9, end=b.end)


# ====================================================================================================== 5.03 design basis
PX = (-4.75, -1.65, 1.45)
PSEA, PSHOE, PBOT = 1.95, -1.4, -3.0


def _panel(st, x, title, color, t):
    card = st.rect(x, -0.12, 2.9, 6.5, P.PANEL, 0.0)
    rock = st.rect(x, (PSEA + PBOT - 0.1) / 2, 2.5, PSEA - PBOT + 0.1, P.ROCK, 0.01)
    sea = st.rect(x, PSEA + 0.22, 2.5, 0.44, P.SEA, 0.01)
    hole = st.rect(x, (PSEA + PSHOE) / 2, 1.24, PSEA - PSHOE, P.BG, 0.02)
    oh = st.rect(x, (PSHOE + PBOT) / 2, 0.84, PSHOE - PBOT, P.BG, 0.02)
    hd = chip(st, x, 2.82, title, color, 0.22)
    st.fade_in([card, rock, sea, hole, oh] + hd, t, 0.45)
    return [card, rock, sea, hole, oh] + hd


def beat_loads(st, tl):
    b = tl["5.03"]
    s = b.sent
    with st.span(b.start, b.end):
        ttl = st.text("for each load: the worst credible case", -1.65, 3.55, 0.22, P.MUTED, 0.4, kind="bold")
        st.fade_in(ttl, s[0] + 0.2, 0.4)
        # design-basis table (fills in, row by row)
        TX = 3.5
        th = st.text("DESIGN BASIS", TX, 1.95, 0.2, P.TEXT, 0.4, align="l", kind="bold")
        tr = st.rect(TX + 2.1, 1.7, 4.2, 0.025, P.GRID, 0.4)
        st.fade_in([th, tr], s[0] + 0.6, 0.4)
        rows = [("BURST", L_BURST, "gas kick, shut in;\nor the casing pressure test", s[1]),
                ("COLLAPSE", L_COLL, "lost circulation: level inside falls,\nfull mud column outside", s[2]),
                ("TENSION", L_TENS, "running in, shock from sudden stops,\noverpull if it sticks", s[3])]
        for i, (nm, cc, txt, t) in enumerate(rows):
            y = 1.15 - 1.45 * i
            c1 = chip(st, TX, y, nm, cc, 0.18, "l")
            tx = st.text(txt, TX, y - 0.62, 0.17, P.TEXT, 0.4, align="l")
            st.fade_in(c1, t + 0.1, 0.4)
            st.fade_in(tx, t + 0.6, 0.4)
    _case_burst(st, b)
    _case_collapse(st, b)
    _case_tension(st, b)


def _case_burst(st, b):
    s = b.sent
    x = PX[0]
    t0 = s[1] - 0.3
    tp = s[0] + 0.5
    with st.span(tp, b.end):
        base = _panel(st, x, "BURST", L_BURST, tp)
        cem = [st.rect(x + sd * 0.49, PSHOE + 0.55, 0.26, 1.1, P.CEMENT, 0.05) for sd in (-1, 1)]
        ann = [st.rect(x + sd * 0.49, (PSEA + PSHOE + 1.1) / 2, 0.26, PSEA - PSHOE - 1.1, P.MUD, 0.05, alpha=0.5) for sd in (-1, 1)]
        walls = [st.rect(x + sd * 0.36, (PSEA + PSHOE) / 2, 0.07, PSEA - PSHOE, P.STEEL, 0.2) for sd in (-1, 1)]
        mud_in = st.rect(x, (PSEA + PBOT) / 2, 0.64, PSEA - PBOT, P.MUD, 0.06, alpha=0.6)
        oh = st.rect(x, (PSHOE + PBOT) / 2, 0.84, PSHOE - PBOT, P.MUD, 0.055, alpha=0.6)
        bop = st.rect(x, PSEA + 0.2, 1.0, 0.34, P.STEEL_DK, 0.25)
        rams = [st.rect(x - 0.38, PSEA + 0.2, 0.22, 0.16, P.PANEL2, 0.27, role="solid"), st.rect(x + 0.38, PSEA + 0.2, 0.22, 0.16, P.PANEL2, 0.27, role="solid")]
        st.fade_in(cem + ann + walls + [mud_in, oh, bop] + rams, tp + 0.1, 0.4)
        # gas kick: bubbles rise, a gas column builds at the top
        t_k = W(b, 1, "gas kick")
        st.flow([(x + 0.05, PBOT + 0.15), (x - 0.05, PSHOE), (x + 0.05, PSEA - 0.2)], t_k - 0.2, t_k + 3.2, P.GAS, n=9, speed=1.5, r=0.05, z=0.3)
        gas = st.rect(x, PSEA - 0.02, 0.64, 0.0001, P.GAS, 0.08, anchor="t")
        st.fade_in(gas, t_k, 0.2)
        st.scale_to(gas, t_k + 0.3, t_k + 2.8, sy=1.5)
        gl = st.text("gas", x, PSEA - 0.6, 0.17, P.TEXT, 0.3, kind="bold")
        st.fade_in(gl, t_k + 1.6, 0.4)
        # shut in: the rams close
        t_sh = W(b, 1, "shut in")
        st.move(rams[0], t_sh - 0.1, t_sh + 0.5, to=(x - 0.11, PSEA + 0.2))
        st.move(rams[1], t_sh - 0.1, t_sh + 0.5, to=(x + 0.11, PSEA + 0.2))
        sl = st.text("shut in", x + 0.62, PSEA + 0.2, 0.15, P.TEXT, 0.3, align="l", kind="bold")
        st.fade_in(sl, t_sh + 0.3, 0.3)
        arr = []
        for y, ln in ((1.55, 0.55), (1.0, 0.47), (0.45, 0.38), (-0.1, 0.3), (-0.65, 0.22)):
            for sd in (-1, 1):
                arr += st.arrow(x + sd * 0.12, y, x + sd * (0.4 + ln), y, L_BURST, 0.05, 0.15, 0.32)
        st.fade_in(arr, t_sh + 0.45, 0.4)
        cap = st.text("highest at the top", x, PBOT - 0.2, 0.15, P.MUTED, 0.3)
        st.fade_in(cap, t_sh + 0.9, 0.4)
        t_pt = W(b, 1, "pressure test")
        rip(st, x, PSEA - 0.4, t_pt, t_pt + 2.0, L_BURST, period=0.7, r0=0.1, r1=0.6, end=b.end)


def _case_collapse(st, b):
    s = b.sent
    x = PX[1]
    t0 = s[2] - 0.3
    tp = s[0] + 0.8
    with st.span(tp, b.end):
        base = _panel(st, x, "COLLAPSE", L_COLL, tp)
        cem = [st.rect(x + sd * 0.49, PSHOE + 0.55, 0.26, 1.1, P.CEMENT, 0.05) for sd in (-1, 1)]
        ann = [st.rect(x + sd * 0.49, (PSEA + PSHOE + 1.1) / 2, 0.26, PSEA - PSHOE - 1.1, P.MUD, 0.05, alpha=0.85) for sd in (-1, 1)]
        walls = [st.rect(x + sd * 0.36, (PSEA + PSHOE) / 2, 0.07, PSEA - PSHOE, P.STEEL, 0.2) for sd in (-1, 1)]
        mud_in = st.rect(x, PSHOE, 0.64, PSEA - PSHOE, P.MUD, 0.06, anchor="b", alpha=0.85)
        YF = -2.2                                  # loss zone (fracture) in the open hole
        oh_lo = st.rect(x, PBOT, 0.84, PSHOE - PBOT, P.MUD, 0.055, anchor="b", alpha=0.85)
        st.fade_in(cem + ann + walls + [mud_in, oh_lo], tp + 0.1, 0.4)
        al = st.text("full mud column outside", x, PBOT - 0.2, 0.15, P.MUD, 0.3, kind="bold")
        st.fade_in(al, t0 + 0.6, 0.4)
        t_lc = W(b, 2, "lost circulation")
        wall = x - 0.42
        wedge = st.poly([(wall, YF + 0.22), (wall - 0.78, YF + 0.05), (wall, YF - 0.22)], P.MUD, 0.07)
        edge = st.line([(wall, YF + 0.22), (wall - 0.4, YF + 0.16), (wall - 0.78, YF + 0.05), (wall - 0.4, YF - 0.1), (wall, YF - 0.22)], P.FRAC, 0.04, 0.08)
        st.pop_in(wedge, t_lc, 0.5)
        st.draw_on(edge, t_lc, t_lc + 0.6)
        fl = chip(st, x - 0.5, YF - 0.55, "cracked rock", P.FRAC, 0.14, z=0.45)
        st.fade_in(fl, t_lc + 0.4, 0.4)
        t_dr = W(b, 2, "drains away")
        st.flow([(x, PSHOE - 0.1), (x, YF + 0.05), (wall - 0.6, YF + 0.05)], t_dr - 0.2, W(b, 2, "completely") + 1.6, P.MUD, n=5, speed=0.9, r=0.045, z=0.3)
        st.flow([(x, YF + 0.05), (wall - 0.6, YF + 0.05)], W(b, 2, "completely") + 1.0, b.end, P.MUD, n=3, speed=0.5, r=0.04, z=0.3)
        # the level inside falls: partly, then completely
        t_lv, t_part, t_all = W(b, 2, "level inside"), W(b, 2, "partly"), W(b, 2, "completely") + 0.5
        H = PSEA - PSHOE
        st.scale_to(mud_in, t_lv - 0.2, t_part + 0.3, sy=H * 0.5)
        st.scale_to(mud_in, t_all - 0.2, t_all + 1.0, sy=0.0001)
        st.scale_to(oh_lo, t_all - 0.2, t_all + 1.0, sy=(YF + 0.2) - PBOT)
        lvl = st.text("level\nfalls", x, PSHOE + H * 0.75, 0.15, P.TEXT, 0.3, kind="bold")
        st.fade_in(lvl, t_lv + 0.3, 0.3)
        st.fade_out(lvl, t_all - 0.3, 0.3)
        part = chip(st, x, PSEA - 0.3, "partly", P.TEXT, 0.15, z=0.4)
        st.fade_in(part, t_part, 0.3)
        st.fade_out(part, t_all - 0.2, 0.3)
        allc = chip(st, x, PSEA - 0.3, "empty", P.TEXT, 0.15, z=0.4)
        st.fade_in(allc, t_all + 0.4, 0.3)
        # inward arrows appear where the inside is empty, longest at depth
        t_out = W(b, 2, "pushes in")
        ys = (1.5, 0.95, 0.4, -0.15, -0.7)
        for k, y in enumerate(ys):
            ln = 0.18 + 0.07 * k
            arr = st.arrow(x - 0.42 - ln, y, x - 0.41, y, L_COLL, 0.05, 0.15, 0.32) + st.arrow(x + 0.42 + ln, y, x + 0.41, y, L_COLL, 0.05, 0.15, 0.32)
            frac = (PSEA - y) / H
            ta = (t_lv + 0.2 + (t_part + 0.3 - t_lv) * min(frac / 0.5, 1.0)) if frac <= 0.5 else (t_all - 0.2 + 1.2 * (frac - 0.5) / 0.5)
            st.fade_in(arr, min(ta, t_out), 0.3)


def _case_tension(st, b):
    s = b.sent
    x = PX[2]
    t0 = s[3] - 0.3
    t_lw, t_sh, t_op = W(b, 3, "lowered in"), W(b, 3, "sudden stops"), W(b, 3, "overpull")
    t_st = W(b, 3, "sticks")
    YTOP, Y_B0, drop = PSEA + 0.4, -0.75, 1.3          # string top (runs on up to the rig), bottom before / after running
    tp = s[0] + 1.1
    with st.span(tp, b.end):
        base = _panel(st, x, "TENSION", L_TENS, tp)
        mud = st.rect(x, (PSEA + PBOT) / 2, 1.24, PSEA - PBOT, P.MUD, 0.05, alpha=0.3)
        st.fade_in(mud, tp + 0.1, 0.4)

        def ybot(t):
            f = min(max((t - t_lw + 0.3) / (t_sh - t_lw + 0.3), 0.0), 1.0)    # constant running speed, then a sudden stop
            return Y_B0 - drop * f

        def string(c, t, look):
            a = _env(t, t0 + 0.1, b.end + 1, 0.4)
            if a <= 0:
                return
            yb = ybot(t)
            _fill(c, [(x - 0.19, yb), (x + 0.19, yb), (x + 0.19, YTOP), (x - 0.19, YTOP)], P.STEEL, a)
            _stroke(c, [(x - 0.19, yb), (x - 0.19, YTOP)], "#e9eff7", 0.7 * a, 0.02)
            _stroke(c, [(x + 0.19, yb), (x + 0.19, YTOP)], "#5d6c82", 0.8 * a, 0.02)
            y = yb + 0.35
            while y < YTOP - 0.1:
                _fill(c, [(x - 0.27, y - 0.1), (x + 0.27, y - 0.1), (x + 0.27, y + 0.1), (x - 0.27, y + 0.1)], "#98a9bf", a)
                y += 1.05
        st.procedural(t0, b.end, 0.2, string)
        # stuck at the bottom
        yb = Y_B0 - drop
        stk = [st.poly([(x - 0.62, yb + 0.3), (x - 0.2, yb + 0.12), (x - 0.62, yb - 0.08)], P.ROCK2, 0.25),
               st.poly([(x + 0.62, yb + 0.3), (x + 0.2, yb + 0.12), (x + 0.62, yb - 0.08)], P.ROCK2, 0.25)]
        stl = chip(st, x, yb - 0.45, "stuck", P.BAD, 0.14, z=0.45)
        st.fade_in(stk + stl, t_st - 0.4, 0.3)
        # forces: buoyed weight DOWN at mid-string, hook load / overpull UP at the top
        def forces(c, t, look):
            a = _env(t, t_lw - 0.3, b.end + 1, 0.4)
            if a <= 0:
                return
            ym = (ybot(t) + YTOP) / 2
            _arrow(c, x - 0.72, ym + 0.4, x - 0.72, ym - 0.45, P.TEXT, a, 0.05, 0.16, look, glow=False)
            look.draw_text(c, "buoyed\nweight", x - 0.8, ym - 0.8, 0.13, P.TEXT, a, "c", "bold")
            spike = math.exp(-max(t - t_sh, 0.0) / 0.25) * (1.0 if t >= t_sh else 0.0)
            op = _sm((t - t_op) / 0.6)
            ln = 0.45 + 0.5 * spike + 0.6 * op
            ya = YTOP - 1.1
            _arrow(c, x + 0.68, ya, x + 0.68, ya + ln, L_TENS, a, 0.06, 0.18, look)
            lab = "overpull" if t > t_op else "hook load"
            look.draw_text(c, lab, x + 0.82, ya - 0.22, 0.13, L_TENS, a, "c", "bold")
        st.procedural(t_lw - 0.3, b.end, 0.45, forces)
        sk = chip(st, x, YTOP - 0.25, "shock", P.WARN, 0.15, z=0.5)
        st.fade_in(sk, t_sh, 0.2)
        st.fade_out(sk, t_sh + 1.3, 0.3)
        rip(st, x, Y_B0 - drop, t_sh, t_sh + 1.0, P.WARN, period=0.5, r0=0.15, r1=0.7, end=t_sh + 2.0)


# ====================================================================================================== 5.04 von Mises ellipse
OX, OY, K = -2.2, 0.1, 1.95


def _X(v):
    return OX + K * v


def _Y(v):
    return OY + K * v


def vme_radius(theta, scale=1.0):
    """Radius of x^2 - xy + y^2 = scale^2 in direction theta (x: pressure / yield, y: axial / yield)."""
    c, s = math.cos(theta), math.sin(theta)
    return scale / math.sqrt(c * c - c * s + s * s)


def vme_pts(scale=1.0, th0=0.0, th1=2 * math.pi, n=180):
    out = []
    for i in range(n + 1):
        th = th0 + (th1 - th0) * i / n
        r = vme_radius(th, scale)
        out.append((r * math.cos(th), r * math.sin(th)))
    return out


def x_collapse(y):
    """Collapse-side (negative pressure) edge of the ellipse at axial load y."""
    return (y - math.sqrt(max(4 - 3 * y * y, 0.0))) / 2


def beat_vme(st, tl):
    b = tl["5.04"]
    s = b.sent
    W_ = lambda pts: [(_X(px), _Y(py)) for px, py in pts]
    with st.span(b.start, b.end):
        panel = st.rect(OX, OY - 0.15, 6.0, 6.25, P.PANEL, 0.0)
        axh = st.line([(_X(-1.4), OY), (_X(1.4), OY)], P.MUTED, 0.03, 0.2)
        axv = st.line([(OX, _Y(-1.35)), (OX, _Y(1.35))], P.MUTED, 0.03, 0.2)
        lt = st.text("tension", OX, _Y(1.35) + 0.22, 0.19, L_TENS, 0.3, kind="bold")
        lc = st.text("compression", OX, _Y(-1.35) - 0.22, 0.17, P.MUTED, 0.3, kind="bold")
        lb = st.text("burst", _X(1.4) + 0.08, OY, 0.19, L_BURST, 0.3, align="l", kind="bold")
        lco = st.text("collapse", _X(-1.4) - 0.08, OY, 0.19, L_COLL, 0.3, align="r", kind="bold")
        cap = st.text("across: pressure difference (inside − outside)   ·   up: axial force", OX, -3.25, 0.15, P.MUTED, 0.3)
        st.fade_in([panel, axh, axv, lt, lc, lb, lco, cap], b.start + 0.1, 0.5)
        # s0: the uniaxial ratings, one at a time -> a rectangle
        t_one = W(b, 0, "one load at a time")
        sides = [([(1, -1), (1, 1)], "burst rating", (_X(1) + 0.12, _Y(-0.45)), "l"),
                 ([(-1, -1), (-1, 1)], "collapse rating", (_X(-1) - 0.12, _Y(0.5)), "r"),
                 ([(-1, 1), (1, 1)], "tension yield", (_X(1) + 0.3, _Y(1)), "l"),
                 ([(-1, -1), (1, -1)], "compression yield", (_X(1) + 0.12, _Y(-1)), "l")]
        rect = []
        for k, (pts, nm, (lx, ly), al) in enumerate(sides):
            ln = st.line(W_(pts), P.TEXT, 0.035, 0.25, alpha=0.75)
            st.draw_on(ln, t_one - 0.6 + 0.35 * k, t_one - 0.2 + 0.35 * k)
            tx = st.text(nm, lx, ly, 0.15, P.MUTED, 0.3, align=al, kind="bold")
            st.fade_in(tx, t_one - 0.4 + 0.35 * k, 0.3)
            rect += [ln, tx]
        rl = chip(st, _X(-0.56), _Y(1) + 0.42, "single-load ratings", P.TEXT, 0.16)
        st.fade_in(rl, t_one + 0.6, 0.4)
        st.fade_out(rl, s[3] - 0.4, 0.4)
        # s1: pulled, squeezed and pressurised at once (a pipe element)
        _element(st, b)
        # s2: the von Mises ellipse, then the design factor
        t_vm, t_df = W(b, 2, "von Mises"), W(b, 2, "design factor")
        ell = st.line(W_(vme_pts(1.0)), P.TEXT, 0.055, 0.4)
        st.draw_on(ell, t_vm - 0.1, t_vm + 2.0, "BEZIER")
        ef = st.poly(W_(vme_pts(1.0, n=90)[:-1]), P.TEXT, 0.12, alpha=0.06)
        st.fade_in(ef, t_vm + 1.6, 0.6)
        el = st.text("von Mises\nellipse", _X(-1.2) - 0.05, _Y(-0.95), 0.17, P.TEXT, 0.5, align="r", kind="bold")
        st.fade_in(el, t_vm + 1.2, 0.4)
        eq = [st.text("σ", 2.0, -0.35, 0.42, P.TEXT, 0.4, align="l", kind="bold"),
              st.text("VME", 2.33, -0.5, 0.15, P.TEXT, 0.4, align="l", kind="bold"),
              st.text("≤  yield ÷ design factor", 2.9, -0.35, 0.3, P.TEXT, 0.4, align="l", kind="bold")]
        st.fade_in(eq, W(b, 2, "against yield") - 0.2, 0.4)
        dfe = st.line(W_(vme_pts(0.8)), P.SAFE, 0.04, 0.42)
        dff = st.poly(W_(vme_pts(0.8, n=90)[:-1]), P.SAFE, 0.11, alpha=0.16)
        st.draw_on(dfe, t_df - 0.1, t_df + 1.3, "BEZIER")
        st.fade_in(dff, t_df + 0.6, 0.5)
        p_df = (0.8 * vme_radius(-math.pi / 4) * math.cos(-math.pi / 4), 0.8 * vme_radius(-math.pi / 4) * math.sin(-math.pi / 4))
        dfl = chip(st, 2.0, -1.35, "design factor (operator-specific)", P.SAFE, 0.18, "l")
        dfld = leader(st, 2.0, -1.35, _X(p_df[0]), _Y(p_df[1]), P.SAFE)
        st.fade_in(dfl + dfld, t_df + 0.5, 0.4)
        # s3: where the ellipse differs from the rectangle (tension side), the red dot
        t_pl = W(b, 3, "Plotted")
        more = [st.poly(W_(vme_pts(1.0, 0.0, math.pi / 4, 60)), P.SAFE, 0.13, alpha=0.55),
                st.poly(W_(vme_pts(1.0, math.pi / 4, math.pi / 2, 60)), P.SAFE, 0.13, alpha=0.55)]
        q2 = [(-1.0, 0.0), (-1.0, 1.0), (0.0, 1.0)] + vme_pts(1.0, math.pi / 2, math.pi, 90)[1:-1]
        less = st.poly(W_(q2), P.BAD, 0.13, alpha=0.42)
        st.fade_in(more, t_pl + 0.3, 0.5)
        st.fade_in(less, t_pl + 0.9, 0.5)
        ml = st.text("allows more", _X(1.16) + 0.12, _Y(0.6), 0.15, P.SAFE, 0.3, align="l", kind="bold")
        ll = st.text("allows less", _X(-0.62), _Y(0.88), 0.15, P.TEXT, 0.3, kind="bold")
        st.fade_in(ll, t_pl + 1.2, 0.4)
        st.fade_out(ll, W(b, 3, "ellipse") + 0.6, 0.3)
        st.fade_in(ml, t_pl + 0.6, 0.4)
        dot = st.circle(_X(-0.72), _Y(0.72), 0.12, P.BAD, 0.6)
        t_dot = W(b, 3, "ellipse") + 0.8
        st.pop_in(dot, t_dot, 0.4)
        dl = chip(st, _X(-0.6), _Y(1.27), "passes the box, fails von Mises", P.BAD, 0.16, "c", z=0.55)
        st.fade_in(dl, t_dot + 0.2, 0.4)
        rip(st, _X(-0.72), _Y(0.72), t_dot + 0.2, t_dot + 2.2, P.BAD, period=0.8, r0=0.15, r1=0.6, end=s[5] - 0.3)
        st.fade_out(eq + dfl + dfld + [ml], s[4] - 0.4, 0.4)
        st.fade_out(dl, s[5] - 0.3, 0.4)
        # s4 + pause: the puzzle on screen; then the answer
        qx = 4.85
        q = st.text(wrap_to("Does pulling on a pipe make it easier or harder to crush?", 0.34, 4.6, "bold"), qx, 0.05, 0.34, P.TEXT, 0.5, kind="bold")
        st.fade_in(q, s[4] - 0.1, 0.5)
        t_ans = s[5]
        rip(st, _X(x_collapse(0.45)), _Y(0.45), b.sent_end[4], t_ans - 0.2, L_COLL, period=0.9, r0=0.1, r1=0.7, end=t_ans)
        st.recolor(q, t_ans - 0.2, t_ans + 0.3, P.MUTED)
        ans = st.text("Easier.", qx, -1.25, 0.62, P.WARN, 0.5, kind="bold")
        st.pop_in(ans, t_ans - 0.05, 0.4)
        st.fade_in(ans, t_ans - 0.05, 0.2)
        # s6: tension shrinks the collapse side; the rating is corrected
        t_a0 = s[6] + 0.2
        t_a1 = W(b, 6, "squeezed", 1.0)

        def answer(c, t, look):
            a = _env(t, t_a0, b.end + 1, 0.4)
            if a <= 0:
                return
            y = 0.72 * _sm((t - t_a0) / (t_a1 - t_a0))
            xc = x_collapse(y)
            _stroke(c, [(_X(0), _Y(0)), (_X(-1), _Y(0))], L_COLL, 0.35 * a, 0.09)
            _arrow(c, _X(0) + 0.0, _Y(0), _X(0), _Y(y) + 0.02, L_TENS, a, 0.07, 0.2, look)
            _stroke(c, [(_X(0), _Y(y)), (_X(xc), _Y(y))], L_COLL, a, 0.09, look=look, glow=True)
            c.drawCircle(_X(xc), _Y(y), 0.1, skia.Paint(Color=col(hex_rgb(L_COLL), a), AntiAlias=True))
            _ptag(c, look, _X(0) + 0.14, _Y(y * 0.5), "pull", L_TENS, a, 0.15, "l")
            _ptag(c, look, _X(xc) - 0.05, _Y(y) + 0.3, "collapse resistance left", L_COLL, a, 0.15, "l")
            _ptag(c, look, _X(-0.5), _Y(0) - 0.25, "with no pull", L_COLL, 0.8 * a, 0.14, "c")
        st.procedural(t_a0, b.end, 0.62, answer)
        st.fade(less, t_a0, t_a0 + 0.5, 1.0, 0.45)
        corr = chip(st, qx, -2.35, "collapse rating: corrected for tension", L_COLL, 0.19)
        st.fade_in(corr, W(b, 6, "corrected") - 0.2, 0.45)
        note = st.text("collapse itself: the API / ISO formula, derated for tension", qx, -2.95, 0.14, P.MUTED, 0.5)
        st.fade_in(note, W(b, 6, "corrected") + 0.6, 0.45)


def _element(st, b):
    """A short pipe element: pulled (axial), squeezed (outside pressure), pressurised (inside pressure)."""
    t_p, t_s, t_r = W(b, 1, "pulled"), W(b, 1, "squeezed"), W(b, 1, "pressurised")
    t_end = W(b, 2, "von Mises") + 0.6
    EX, EY = 4.9, 1.05
    with st.span(t_p - 0.4, t_end + 0.5):
        tube = [st.rect(EX, EY + 0.42, 2.2, 0.16, P.STEEL, 0.3), st.rect(EX, EY - 0.42, 2.2, 0.16, P.STEEL, 0.3)]
        bore = st.rect(EX, EY, 2.2, 0.68, P.BG, 0.29)
        st.fade_in(tube + [bore], t_p - 0.4, 0.35)
        pull = st.arrow(EX + 1.15, EY, EX + 2.0, EY, L_TENS, 0.08, 0.22, 0.32) + st.arrow(EX - 1.15, EY, EX - 2.0, EY, L_TENS, 0.08, 0.22, 0.32)
        sq = []
        for dx in (-0.6, 0.0, 0.6):
            sq += st.arrow(EX + dx, EY + 1.0, EX + dx, EY + 0.53, L_COLL, 0.05, 0.15, 0.32)
            sq += st.arrow(EX + dx, EY - 1.0, EX + dx, EY - 0.53, L_COLL, 0.05, 0.15, 0.32)
        pr = []
        for dx in (-0.3, 0.3):
            pr += st.arrow(EX + dx, EY + 0.05, EX + dx, EY + 0.3, L_BURST, 0.04, 0.12, 0.32)
            pr += st.arrow(EX + dx, EY - 0.05, EX + dx, EY - 0.3, L_BURST, 0.04, 0.12, 0.32)
        labs = [st.text("pulled", EX - 1.1, EY - 1.45, 0.17, L_TENS, 0.35, kind="bold"),
                st.text("squeezed", EX, EY - 1.45, 0.17, L_COLL, 0.35, kind="bold"),
                st.text("pressurised", EX + 1.25, EY - 1.45, 0.17, L_BURST, 0.35, kind="bold")]
        st.fade_in(pull + [labs[0]], t_p, 0.3)
        st.fade_in(sq + [labs[1]], t_s, 0.3)
        st.fade_in(pr + [labs[2]], t_r, 0.3)
        st.fade_out(tube + [bore] + pull + sq + pr + labs, t_end, 0.4)


# ====================================================================================================== 5.05 tapered string
Z0, Z1 = 300.0, 3400.0


def T_load(z):
    return 0.05 + 1.2 * (Z1 - z) / (Z1 - Z0)


def B_load(z):
    return 1.12 - 0.77 * (z - Z0) / (Z1 - Z0)


def C_load(z):
    return 1.2 * ((z - Z0) / (Z1 - Z0)) ** 1.1


STEPS = [(Z0, 1000.0, 1.45), (1000.0, 2600.0, 1.0), (2600.0, Z1, 1.4)]


def cap_step(z):
    for a, c, v in STEPS:
        if a <= z <= c:
            return v
    return 1.0


def beat_taper(st, tl):
    b = tl["5.05"]
    s = b.sent
    with st.span(b.start, b.end):
        c = Chart(st, -4.9, -2.6, 5.4, 4.9, (0.0, 1.6), (Z0, Z1), invert_y=True)
        fr = c.frame(xticks=[0, 0.5, 1.0, 1.5], yticks=[300, 1000, 2000, 3000], xlabel="load ÷ rating of the lighter pipe",
                     ylabel="depth (m)", fx="{:g}", tick_size=0.17)
        ttl = st.text("the 9⅝ in string, seabed to shoe", -4.9, 3.05, 0.22, P.TEXT, 0.4, align="l", kind="bold")
        st.fade_in(fr + [ttl], b.start + 0.1, 0.5)
        zs = [Z0 + (Z1 - Z0) * i / 60 for i in range(61)]
        tcv = c.curve([T_load(z) for z in zs], zs, L_TENS, 0.06, 0.3)
        bcv = c.curve([B_load(z) for z in zs], zs, L_BURST, 0.06, 0.3)
        ccv = c.curve([C_load(z) for z in zs], zs, L_COLL, 0.06, 0.3)
        t_t, t_b, t_c = W(b, 1, "Tension"), W(b, 1, "often burst"), W(b, 2, "Collapse")
        st.draw_on(tcv, t_t - 0.2, t_t + 1.4, "BEZIER")
        st.draw_on(bcv, t_b - 0.2, t_b + 1.4, "BEZIER")
        st.draw_on(ccv, t_c - 0.2, t_c + 1.4, "BEZIER")
        tl_ = c.label(T_load(2000) - 0.04, 2000, "tension", 0.17, L_TENS, "r", "bold")
        bl_ = c.label(B_load(2500) + 0.05, 2500, "burst", 0.17, L_BURST, "l", "bold")
        cl_ = c.label(C_load(1150) + 0.05, 1150, "collapse", 0.17, L_COLL, "l", "bold")
        st.fade_in(tl_, t_t + 0.8, 0.3)
        st.fade_in(bl_, t_b + 0.8, 0.3)
        st.fade_in(cl_, t_c + 0.8, 0.3)
        # capacity: one weight for the whole string, then tapered steps (procedural morph)
        t_cap = s[0] + 0.2
        t_eat = W(b, 1, "eats into")
        t_tap = W(b, 3, "tapered")

        def capacity(cv, t, look):
            a = _env(t, t_cap, b.end + 1, 0.4)
            if a <= 0:
                return
            f = _sm((t - t_tap) / 1.4)
            pts, pc = [], []
            for i in range(121):
                z = Z0 + (Z1 - Z0) * i / 120
                v = 1.0 + f * (cap_step(z + (1e-6 if i < 120 else -1e-6)) - 1.0)
                pts.append(c.pt(v, z))
                pc.append(c.pt(v * (1 - 0.3 * T_load(z) / 1.3), z))
            _stroke(cv, pts, P.TEXT, a, 0.05, look=look, glow=False)
            ea = _env(t, t_eat, b.end + 1, 0.4) * a
            if ea > 0:
                for k in range(0, len(pc) - 1, 2):
                    _stroke(cv, [pc[k], pc[k + 1]], L_COLL, 0.85 * ea, 0.03)
            look.draw_text(cv, "rating" if f < 0.5 else "tapered rating", c.X(1.0 + f * 0.45), c.Y(Z0) + 0.22, 0.15, P.TEXT, a, "c", "bold")
        st.procedural(t_cap, b.end, 0.35, capacity)
        eat = st.text("collapse rating,\ncut by tension", c.X(0.66), c.Y(520), 0.14, L_COLL, 0.4, align="r", kind="bold")
        st.fade_in(eat, t_eat + 0.4, 0.4)
        st.fade_out(eat, t_tap - 0.2, 0.4)
        # where the single weight fails: top (tension, burst) and bottom (collapse)
        top_bad = st.rect(c.X(0.8), (c.Y(Z0) + c.Y(950)) / 2, c.X(1.6) - c.X(0.0) - 0.05, c.Y(Z0) - c.Y(950), P.BAD, 0.15, alpha=0.18, role="flat")
        bot_bad = st.rect(c.X(0.8), (c.Y(2950) + c.Y(Z1)) / 2, c.X(1.6) - c.X(0.0) - 0.05, c.Y(2950) - c.Y(Z1), P.BAD, 0.15, alpha=0.18, role="flat")
        tb = chip(st, c.X(1.42), c.Y(780), "✗ fails", P.BAD, 0.16, z=0.5)
        bb = chip(st, c.X(0.55), c.Y(3180), "✗ fails", P.BAD, 0.16, z=0.5)
        t_top = W(b, 1, "worst at the top")
        st.fade_in([top_bad] + tb, t_top, 0.4)
        t_bot = W(b, 2, "worst at the bottom")
        st.fade_in([bot_bad] + bb, t_bot, 0.4)
        st.fade_out([top_bad, bot_bad] + tb + bb, t_tap + 0.4, 0.6)
        ok = chip(st, 4.7, -0.9, "✓ every load under its rating", P.SAFE, 0.2, z=0.5)
        st.fade_in(ok, t_tap + 1.6, 0.4)
        # the string beside it: constant OD; stronger steel at the top, thicker wall at the bottom
        SX, R = 1.6, 0.34
        secs = [(Z0, 1000.0, 0.09, "#c9d4e1", "stronger steel"), (1000.0, 2600.0, 0.09, "#71839c", "lighter wall"),
                (2600.0, Z1, 0.19, "#71839c", "thicker wall")]
        groups = []
        for z0, z1, wv, cc, nm in secs:
            ya, yb_ = c.Y(z0), c.Y(z1)
            g = [st.rect(SX + sd * (R - wv / 2), (ya + yb_) / 2, wv, ya - yb_ - 0.04, cc, 0.3) for sd in (-1, 1)]
            g.append(st.rect(SX, (ya + yb_) / 2, 2 * (R - wv) - 0.01, ya - yb_ - 0.04, P.BG, 0.29))
            g.append(st.text(nm, SX + R + 0.2, (ya + yb_) / 2, 0.18, P.TEXT, 0.35, align="l", kind="bold"))
            groups.append(g)
        sl = st.text("same outside diameter", SX, c.Y(Z1) - 0.3, 0.14, P.MUTED, 0.35)
        t_tw, t_ss = W(b, 3, "thicker wall"), W(b, 3, "stronger steel")
        st.fade_in(groups[1], t_tap + 0.2, 0.4)
        st.fade_in(groups[2], t_tw - 0.1, 0.4)
        st.fade_in(groups[0], t_ss - 0.1, 0.4)
        st.fade_in(sl, W(b, 3, "stronger steel"), 0.4)
        rip(st, SX, (c.Y(Z0) + c.Y(1000)) / 2, W(b, 3, "stronger steel"), W(b, 3, "stronger steel") + 1.2, P.TEXT, period=0.6, r0=0.2, r1=0.7, end=b.end)


# ====================================================================================================== 5.06 connections
class View:
    """A camera for the drawing only (copied from ch06/ch03). Objects and procedurals created inside `with view:` are drawn
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


AY, PID, POD, COD = 0.05, 0.62, 1.7, 2.75         # axis, pipe ID, pipe OD, coupling OD (half-section, upper wall)
XF, XS, XN, XM, XE = -4.0, -0.35, 0.55, 1.4, 2.45  # coupling face, end of threads, pin nose, coupling centre, cut edge
PITCH, TH = 0.45, 0.2
NT, NB = (XN + 0.06, 0.84), (XN - 0.06, PID)       # pin nose: top (end of the seal cone) and bottom of the shoulder face
CS = (XS + 0.1, 0.975)                             # start of the seal cone


def _pitch_y(x):
    return 1.42 + (x - XF) * (1.08 - 1.42) / (XS - XF)


def _thread(x0, x1, kind, n_per=10, lift=0.0):
    """Thread profile from x0 to x1 (pin crests up). 'api': rounded V; 'prem': buttress-like (square flanks)."""
    pts = []
    n = max(int(abs(x1 - x0) / PITCH * n_per), 2)
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        ph = ((x - XF) / PITCH) % 1.0
        if kind == "api":
            tw = 1 - 2 * abs(ph - 0.5)
            tw = 0.5 - 0.5 * math.cos(math.pi * tw)
        else:
            tw = 1.0 if 0.18 < ph < 0.62 else (ph / 0.18 if ph <= 0.18 else max(0.0, 1 - (ph - 0.62) / 0.05))
        pts.append((x, _pitch_y(x) - TH / 2 + TH * tw + lift))
    return pts


def _pin_pts(kind, d=0.0):
    """Pin (pipe end) outline; d = how far the pin still has to travel (its nose features sit d to the left). The thread
    profile does not move in the section plane while the pin screws in: only the nose advances."""
    if kind == "api":
        xn = XN - d
        return [(-9.5, PID), (xn, PID), (xn, _pitch_y(xn) - TH / 2)] + _thread(xn, XF - 0.05, "api") + [(XF - 0.05, POD), (-9.5, POD)]
    return [(-9.5, PID), (NB[0] - d, PID), (NT[0] - d, NT[1]), (CS[0] - d, CS[1])] + _thread(XS - d, XF - 0.05, "prem") + \
        [(XF - 0.05, POD), (-9.5, POD)]


def _box_pts(kind):
    if kind == "api":
        return [(XF, POD + 0.02)] + _thread(XF, XE, "api", lift=0.035) + [(XE, COD), (XF, COD)]
    return [(XF, POD + 0.02)] + _thread(XF, XS, "prem") + [CS, NT, NB, (XE, PID), (XE, COD), (XF, COD)]


def _pin_proc(st, a, b, kind, dfun, z=0.2):
    def draw(c, t, look):
        al = dfun(t)
        d, alpha = al
        if alpha <= 0.003:
            return
        pts = _pin_pts(kind, d)
        _fill(c, pts, PIN_C, alpha)
        _stroke(c, pts, "#46536a", alpha, 0.018, close=True)
    st.procedural(a, b, z, draw)


def beat_connections(st, tl):
    b = tl["5.06"]
    s = b.sent
    with st.span(b.start, b.end):
        _conn_intro(st, b)
        t0, t1 = s[1] - 0.35, s[4] - 0.1
        view = View(st, t0, t1, z=0.2)
        with view:
            with st.span(t0, t1):
                bore = st.rect((-9.5 + XE) / 2, (AY + PID) / 2, XE + 9.5, PID - AY, P.BG, 0.02)
                cl = st.dashed((-9.5, AY), (XE + 0.2, AY), P.MUTED, 0.025, 0.4, 0.15, 0.05)
                al = st.text("pipe axis", -5.6, AY - 0.2, 0.14, P.MUTED, 0.3, align="l")
                brk = st.line([(XE, COD + 0.1), (XE - 0.08, (COD + PID) / 2 + 0.3), (XE + 0.08, (COD + PID) / 2 - 0.3), (XE, PID - 0.05)],
                              P.MUTED, 0.025, 0.4)
                st.fade_in([bore, brk, al] + cl, t0, 0.4)
                st.fade_out([bore, brk, al] + cl, t1 - 0.4, 0.4)
            _conn_api(st, b)
            ctx = _conn_premium(st, b)
        _conn_labels(st, b, view, ctx)
        _conn_end(st, b)


def _conn_intro(st, b):
    """Two pipe joints and a coupling at true-ish proportions: the right joint's threaded pin end screws into the coupling."""
    s = b.sent
    t0, t1 = b.start, s[1] - 0.1
    Y, H, CH, CW = 0.35, 1.0, 1.36, 1.9          # axis height, pipe OD, coupling OD, coupling length
    with st.span(t0, t1 + 0.5):
        lp = st.rect(-3.3, Y, 6.6, H, P.STEEL, 0.2)                       # left joint: -6.6 .. 0 (its pin sits in the coupling)
        cp = st.rect(0.0, Y, CW, CH, P.STEEL_DK, 0.25)
        L0, L1 = 2.3, 0.0                                                  # right joint's pin end: before / after make-up
        rp = st.rect(L0 + 3.0, Y, 6.0, H, P.STEEL, 0.2)
        thr = [st.rect(L0 + 0.12 + 0.15 * k, Y, 0.05, H - 0.04, "#71839c", 0.21) for k in range(6)]
        st.fade_in([lp, cp, rp] + thr, t0 + 0.2, 0.5)
        t_j = W(b, 0, "threaded joints")
        st.move([rp] + thr, t_j - 0.5, t_j + 1.2, dx=L1 - L0)
        l1 = chip(st, -3.3, Y - 0.95, "pipe joint", P.TEXT, 0.2)
        l2 = chip(st, 0.0, Y - 1.15, "coupling: threaded at both ends", P.TEXT, 0.2)
        l3 = chip(st, L0 + 0.5, Y + 1.0, "threaded pin end", P.TEXT, 0.18)
        st.fade_in(l1 + l2, t_j - 0.2, 0.4)
        st.fade_in(l3, b.start + 0.6, 0.4)
        st.move(l3, t_j - 0.5, t_j + 1.2, dx=L1 - L0 + 1.0)
        st.fade_out(l3, t_j + 1.6, 0.4)
        st.fade_out([lp, cp, rp] + thr + l1 + l2, t1 - 0.2, 0.5)


def _conn_api(st, b):
    s = b.sent
    t0, t1 = s[1] - 0.3, s[2] + 0.2
    with st.span(t0, t1 + 0.5):
        box = st.poly(_box_pts("api"), BOX_C, 0.22)
        bo = st.line(_box_pts("api") + [_box_pts("api")[0]], "#46536a", 0.018, 0.221)
        st.fade_in([box, bo], t0, 0.45)
        _pin_proc(st, t0, t1 + 0.5, "api", lambda t: (0.0, _env(t, t0, t1 + 0.45, 0.45)))
        pl = st.text("pin (pipe end)", -5.3, (PID + POD) / 2, 0.17, P.BG, 0.3, kind="bold")
        bl = st.text("box (coupling)", -0.6, COD - 0.32, 0.17, P.BG, 0.3, kind="bold")
        st.fade_in([pl, bl], t0 + 0.4, 0.4)
        # the helical gap between pin and box threads: a spiral leak path from the bore to the outside
        gap = [(XN + 0.1, (PID + 0.98) / 2)] + [(x, y + 0.017) for x, y in _thread(XN, XF, "api")] + [(XF - 0.3, POD + 0.3)]
        t_c = W(b, 1, "thread compound")
        st.flow(gap, t0 + 0.4, t_c + 0.3, P.GAS, n=16, speed=2.4, r=0.04, z=0.4)
        dots = []
        pts = _thread(XN, XF, "api", n_per=3)
        for k, (x, y) in enumerate(pts):
            d = st.circle(x, y + 0.017, 0.032, DOPE, 0.41, role="disc")
            st.fade_in(d, t_c - 0.2 + 0.7 * k / len(pts), 0.15)
            dots.append(d)
        st.fade_out([box, bo, pl, bl] + dots, t1, 0.45)


def _conn_premium(st, b):
    s = b.sent
    t0 = s[2] - 0.1
    t_end = s[4] - 0.1
    t_mu = W(b, 3, "make-up")
    t_mu1 = W(b, 3, "torque-turn", 1.0) + 0.3
    N_S = 0.9                                     # fraction of the make-up at which the pin nose meets the shoulder
    t_c0 = t_mu + 0.3
    t_sh = t_c0 + N_S * (t_mu1 - t_c0)

    def dfun(t):
        a = _env(t, t0, t_end, 0.45)
        if t < t_mu - 0.6:
            return 0.0, a
        if t < t_mu - 0.1:
            return PITCH * _sm((t - t_mu + 0.6) / 0.5), a
        if t < t_c0:
            return PITCH, a
        return PITCH * max(0.0, 1 - (t - t_c0) / (t_sh - t_c0)), a
    with st.span(t0, t_end):
        box = st.poly(_box_pts("prem"), BOX_C, 0.22)
        bo = st.line(_box_pts("prem") + [_box_pts("prem")[0]], "#46536a", 0.018, 0.221)
        st.fade_in([box, bo], t0 + 0.15, 0.45)
        _pin_proc(st, t0, t_end, "prem", dfun)
        pl = st.text("pin (pipe end)", -5.3, (PID + POD) / 2, 0.17, P.BG, 0.3, kind="bold")
        bl = st.text("box (coupling)", -0.6, COD - 0.32, 0.17, P.BG, 0.3, kind="bold")
        st.fade_in([pl, bl], t0 + 0.5, 0.4)
        seal = st.line([CS, NT], P.TEXT, 0.035, 0.4, role="glow")
        shld = st.line([NT, NB], P.WARN, 0.04, 0.4)
        t_ms, t_ts = W(b, 2, "metal-to-metal"), W(b, 2, "torque shoulder")
        st.draw_on(seal, t_ms - 0.1, t_ms + 0.5)
        st.draw_on(shld, t_ts - 0.1, t_ts + 0.4)
        t_gt = W(b, 2, "gas-tight")
        st.flow([(XE - 0.3, 0.3), (XN + 0.3, 0.42), (NB[0] + 0.08, 0.5)], t_gt - 0.7, t_gt + 1.8, P.GAS, n=8, speed=0.9, r=0.03, z=0.35)
        rip(st, (CS[0] + NT[0]) / 2, (CS[1] + NT[1]) / 2, t_gt, t_gt + 1.6, P.SAFE, period=0.6, r0=0.05, r1=0.3, width=0.02, end=t_end - 0.4)
        # make-up: the seal and shoulder highlights hide while the pin is backed off, return at shoulder contact
        st.fade([seal, shld], t_mu - 0.6, t_mu - 0.3, 1.0, 0.0)
        st.fade([seal, shld], t_sh, t_sh + 0.3, 0.0, 1.0)
        rip(st, (NT[0] + NB[0]) / 2, (NT[1] + NB[1]) / 2, t_sh, t_sh + 1.4, P.WARN, period=0.6, r0=0.05, r1=0.45, end=t_end - 0.4)
        st.fade_out([box, bo, pl, bl, seal, shld], t_end - 0.45, 0.4)
    return dict(t0=t0, t_end=t_end, t_mu=t_mu, t_mu1=t_mu1, t_sh=t_sh, t_c0=t_c0, N_S=N_S, t_gt=t_gt, t_ms=t_ms, t_ts=t_ts,
                t_zoom=t_ms - 1.1, t_out=s[3] - 0.1)


ZF, ZA, ZK = (0.15, 0.9), (-1.2, -0.3), 2.0     # zoom: world focus, screen point, scale
V1F, V1A, V1K = (-2.0, 1.4), (0.6, 0.35), 1.3   # opening view of the half-section (fills the frame)


def _zs(p):
    return (ZA[0] + (p[0] - ZF[0]) * ZK, ZA[1] + (p[1] - ZF[1]) * ZK)


def _conn_labels(st, b, view, ctx):
    s = b.sent
    t_zoom, t_out = ctx["t_zoom"], ctx["t_out"]
    view.camera(s[1] - 0.4, s[1] - 0.35, V1F, V1A, V1K)
    view.camera(t_zoom, t_zoom + 1.1, ZF, ZA, ZK)
    view.camera(t_out, t_out + 1.1, (0.0, 0.0), (0.0, 0.0), 1.0)
    with st.span(b.start, b.end):
        hdr1 = chip(st, -6.2, 3.45, "basic API coupling (half-section)", P.TEXT, 0.2, "l")
        st.fade_in(hdr1, s[1] - 0.1, 0.4)
        st.fade_out(hdr1, s[2] - 0.2, 0.35)
        lk = chip(st, 0.0, 3.05, "spiral gap along the threads: a leak path", P.GAS, 0.18)
        t_c = W(b, 1, "thread compound")
        st.fade_in(lk, s[1] + 0.4, 0.4)
        st.fade_out(lk, t_c, 0.3)
        dl = chip(st, 0.0, 3.05, "thread compound fills the gap", DOPE, 0.18)
        st.fade_in(dl, t_c + 0.2, 0.4)
        st.fade_out(dl, s[2] - 0.2, 0.35)
        hdr2 = chip(st, -6.2, 3.45, "premium connection (half-section)", P.TEXT, 0.2, "l")
        st.fade_in(hdr2, s[2], 0.4)
        st.fade_out(hdr2, ctx["t_end"] - 0.4, 0.35)
        # zoomed labels (screen space, computed through the zoom)
        p_seal = _zs(((CS[0] + NT[0]) / 2, (CS[1] + NT[1]) / 2))
        p_sh = _zs(((NT[0] + NB[0]) / 2, (NT[1] + NB[1]) / 2))
        sll = chip(st, -3.4, -2.55, "metal-to-metal seal: cone on cone", P.TEXT, 0.2)
        sld = leader(st, -2.2, -2.33, p_seal[0], p_seal[1], P.TEXT)
        tsl = chip(st, 1.7, -2.55, "torque shoulder", P.WARN, 0.2)
        tsd = leader(st, 1.0, -2.33, p_sh[0], p_sh[1], P.WARN)
        st.fade_in(sll + sld, ctx["t_ms"] + 0.2, 0.4)
        st.fade_in(tsl + tsd, ctx["t_ts"] + 0.2, 0.4)
        gt = chip(st, -0.9, -3.25, "✓ gas-tight", P.SAFE, 0.22)
        st.fade_in(gt, ctx["t_gt"] + 0.1, 0.35)
        st.fade_out(sll + sld + tsl + tsd + gt, t_out - 0.4, 0.35)
        # qualified by test (while the view pulls back), then make-up on the torque-turn plot
        t_iso = W(b, 3, "ISO")
        iso = chip(st, -1.9, -1.75, "qualified by testing to ISO 13679", P.TEXT, 0.24)
        st.fade_in(iso, t_iso - 0.2, 0.4)
        st.fade_out(iso, ctx["t_mu"] - 0.5, 0.35)
        mu = chip(st, 4.9, 0.9, "make-up: screwing the joint together", P.TEXT, 0.18)
        st.fade_in(mu, ctx["t_mu"] - 0.2, 0.4)
        st.fade_out(mu, ctx["t_end"] - 0.4, 0.35)
        _torque_turn(st, b, ctx)


def _tq(n, n_s=0.9):
    if n <= n_s:
        return 0.22 * n + 0.32 * n * n + (1.6 * (n - 0.72) ** 2 if n > 0.72 else 0.0)
    return _tq(n_s, n_s) + 11.0 * (n - n_s)


def _torque_turn(st, b, ctx):
    t_mu, t_mu1, n_s, t_c0 = ctx["t_mu"], ctx["t_mu1"], ctx["N_S"], ctx["t_c0"]
    c = Chart(st, -4.9, -2.85, 6.6, 2.0, (0.0, 1.0), (0.0, 1.45))
    n_f = n_s + 0.055
    t_end = ctx["t_end"]
    with st.span(t_mu - 0.3, t_end):
        pan = st.rect(c.x + c.w / 2 - 0.25, c.y + c.h / 2 - 0.15, c.w + 1.2, c.h + 1.0, P.PANEL, 0.0)
        fr = c.frame(xticks=[], yticks=[], xlabel="turns", ylabel="", grid=False, panel=False)
        yl = st.text("torque", c.x - 0.15, c.y + c.h - 0.1, 0.17, P.MUTED, 0.1, align="r")
        tmin, tmax = 1.0, 1.32
        win = st.rect(c.X(n_s + 0.055), (c.Y(tmin) + c.Y(tmax)) / 2, c.X(0.1) - c.X(0.0), c.Y(tmax) - c.Y(tmin), P.SAFE, 0.12, alpha=0.3, role="flat")
        dmin = st.dashed((c.X(0.6), c.Y(tmin)), (c.X(1.0), c.Y(tmin)), P.SAFE, 0.025, 0.12, 0.08, 0.13)
        dmax = st.dashed((c.X(0.6), c.Y(tmax)), (c.X(1.0), c.Y(tmax)), P.SAFE, 0.025, 0.12, 0.08, 0.13)
        wl = st.text("acceptance window", c.X(0.6) - 0.12, (c.Y(tmin) + c.Y(tmax)) / 2, 0.16, P.SAFE, 0.2, align="r", kind="bold")
        st.fade_in([pan, yl] + fr, t_mu - 0.3, 0.45)
        st.fade_in([win, wl] + dmin + dmax, t_mu + 0.6, 0.45)

        def curve(cv, t, look):
            if t < t_c0:
                return
            f = min((t - t_c0) / (t_mu1 - t_c0), 1.0)
            n_now = f * n_f
            pts = [c.pt(n_now * i / 120, _tq(n_now * i / 120, n_s)) for i in range(121)]
            _stroke(cv, pts, P.TEXT, 1.0, 0.05)
            x, y = pts[-1]
            cv.drawCircle(x, y, 0.07, skia.Paint(Color=col(hex_rgb(P.WARN), 1.0), AntiAlias=True))
            if n_now >= n_s:
                xs, ys = c.pt(n_s, _tq(n_s, n_s))
                a = min(1.0, (n_now - n_s) / 0.01)
                look.draw_text(cv, "shoulder", xs - 0.15, ys + 0.1, 0.16, P.WARN, a, "r", "bold")
            if f >= 1.0:
                a = min(1.0, (t - t_mu1) / 0.3)
                look.draw_text(cv, "✓", x + 0.3, y, 0.28, P.SAFE, a, "l", "bold")
        st.procedural(t_c0, t_end, 0.4, curve)
        st.fade_out([pan, yl, win, wl] + fr + dmin + dmax, t_end - 0.4, 0.35)


def _conn_end(st, b):
    s = b.sent
    t0 = s[4] - 0.25
    with st.span(t0, b.end):
        Y = 0.5
        objs = []
        xs = [-5.6, -2.3, 1.0]
        for k, x in enumerate(xs):
            objs.append(st.rect(x + 1.6, Y, 3.1, 0.7, P.STEEL, 0.2))
        cps = [st.rect(x, Y, 0.6, 0.95, P.STEEL_DK, 0.25) for x in xs[1:] + [4.3]]
        st.fade_in(objs + cps, t0, 0.45)
        t_f = W(b, 4, "may be fine")
        oks = []
        for x in xs:
            oks += chip(st, x + 1.6, Y + 0.85, "✓ pipe body", P.SAFE, 0.15)
        st.fade_in(oks, t_f - 0.2, 0.4)
        t_l = W(b, 4, "where most leaks")
        for x in xs[1:] + [4.3]:
            rip(st, x, Y, t_l - 0.2, b.end, P.BAD, period=1.0, r0=0.35, r1=1.0, end=b.end)
        st.flow([(-2.3, Y + 0.5), (-2.35, Y + 1.3), (-2.2, Y + 2.0)], t_l, b.end, P.GAS, n=6, speed=0.8, r=0.045, z=0.4, jitter=0.1)
        cap = chip(st, -0.6, -1.0, "connections: where most leaks start", P.BAD, 0.26)
        st.fade_in(cap, t_l, 0.45)


# ====================================================================================================== 5.07 the casing as a barrier element
def beat_barrier_element(st, tl):
    b = tl["5.07"]
    s = b.sent
    CX = -2.6
    Yz = lambda z: 3.3 - z * 6.4 / M.TD
    prog = {p.name: p for p in M.programme()}
    sh30, sh20, sh13, sh9 = (prog[n].shoe for n in ("30in conductor", "20in surface casing", "13-3/8in intermediate", "9-5/8in intermediate"))
    TOC9 = 2600.0           # top of cement behind the 9 5/8 in (same drawing value as ch06 / ch09)
    TOC13 = 1500.0          # drawing value
    r = dict(h36=1.25, c30=1.05, h26=0.95, c20=0.78, h17=0.64, c13=0.52, h12=0.44, c9=0.34, oh=0.28)
    ysb = Yz(M.WATER_DEPTH)
    with st.span(b.start, b.end):
        objs = [st.rect(CX, (ysb + 3.55) / 2, 3.7, 3.55 - ysb, P.SEA, 0.0),
                st.rect(CX, (ysb + Yz(M.TD) - 0.15) / 2, 3.7, ysb - Yz(M.TD) + 0.15, P.ROCK, 0.0)]

        def col_rect(rr, z0, z1, color, z, alpha=1.0):
            return st.rect(CX, (Yz(z0) + Yz(z1)) / 2, 2 * rr, Yz(z0) - Yz(z1), color, z, alpha=alpha)
        objs += [col_rect(r["h36"], M.WATER_DEPTH, sh30, P.CEMENT, 0.02), col_rect(r["h26"], M.WATER_DEPTH, sh20, P.CEMENT, 0.03),
                 col_rect(r["c20"], M.WATER_DEPTH, sh20, P.BG, 0.04), col_rect(r["c20"], M.WATER_DEPTH, sh20, P.MUD, 0.041, 0.3),
                 col_rect(r["h17"], sh20, sh13, P.BG, 0.04), col_rect(r["h17"], sh20, sh13, P.MUD, 0.041, 0.3),
                 col_rect(r["h17"], TOC13, sh13, P.CEMENT, 0.045),
                 col_rect(r["c13"], M.WATER_DEPTH, sh13, P.BG, 0.05), col_rect(r["c13"], M.WATER_DEPTH, sh13, P.MUD, 0.051, 0.3),
                 col_rect(r["h12"], sh13, sh9, P.BG, 0.05), col_rect(r["h12"], sh13, sh9, P.MUD, 0.051, 0.3),
                 col_rect(r["h12"], TOC9, sh9, P.CEMENT, 0.055),
                 col_rect(r["c9"], M.WATER_DEPTH, sh9, P.BG, 0.06), col_rect(r["c9"], M.WATER_DEPTH, sh9, P.MUD, 0.061, 0.45),
                 col_rect(r["oh"], sh9, M.TD, P.BG, 0.06), col_rect(r["oh"], sh9, M.TD, P.MUD, 0.061, 0.45)]
        walls = {}
        st.fade_in(objs[:2], b.start + 0.05, 0.4)
        for k, (key, nm, shoe, cc) in enumerate((("c30", "30in conductor", sh30, "#56667d"), ("c20", "20in surface casing", sh20, "#71839c"),
                                                 ("c13", "13-3/8in intermediate", sh13, "#98a9bf"), ("c9", "9-5/8in intermediate", sh9, P.STEEL))):
            walls[key] = [st.rect(CX + sd * (r[key] - 0.03), ysb, 0.06, 0.0001, cc, 0.2, anchor="t") for sd in (-1, 1)]
            ta = b.start + 0.25 + 0.45 * k
            st.fade_in(walls[key], ta, 0.15)
            st.scale_to(walls[key], ta, ta + 0.5 + 0.25 * k, sy=ysb - Yz(shoe))
            st.fade_in([objs[2:3], objs[3:6], objs[6:11], objs[11:]][k], ta + 0.05, 0.4)
        wh = st.rect(CX, ysb + 0.1, 1.0, 0.2, P.STEEL_DK, 0.25)
        st.fade_in(wh, b.start + 0.1, 0.4)
        ch7 = chip(st, 0.0, 1.0, "the barrier language of chapter 7", P.MUTED, 0.2, "l")
        st.fade_in(ch7, s[0] + 0.3, 0.4)
        st.fade_out(ch7, W(b, 0, "the casing that seals") - 0.2, 0.4)
        labs = []
        for key, txt, z in (("c30", "30 in", sh30), ("c20", "20 in", sh20), ("c13", "13⅜ in", sh13), ("c9", "9⅝ in", sh9)):
            labs.append(st.text(txt, CX - 1.95, Yz(z), 0.15, P.MUTED, 0.3, align="r", kind="bold"))
        st.fade_in(labs, b.start + 0.4, 0.4)
        # the last-set casing and its cement light up (outline; cement stays cement grey)
        t_c = W(b, 0, "the casing that seals")
        hl = []
        for sd in (-1, 1):
            pts = [(CX + sd * (r["c9"] - 0.09), ysb - 0.02), (CX + sd * (r["c9"] - 0.09), Yz(sh9) - 0.03), (CX + sd * (r["h12"] + 0.05), Yz(sh9) - 0.03),
                   (CX + sd * (r["h12"] + 0.05), Yz(TOC9) + 0.03), (CX + sd * (r["c9"] + 0.05), Yz(TOC9) + 0.03), (CX + sd * (r["c9"] + 0.05), ysb - 0.02)]
            hl.append(st.line(pts, P.TEXT, 0.035, 0.5, role="glow"))
        st.draw_on(hl, t_c, t_c + 1.5, "BEZIER")
        ccl = st.text("the last-set casing, 9⅝ in, + its cement", 0.0, -0.05, 0.19, P.TEXT, 0.4, align="l", kind="bold")
        st.fade_in(ccl, t_c + 0.4, 0.4)
        t_e = W(b, 0, "well barrier element")
        wbe = chip(st, 0.0, -0.75, "a well barrier element", P.TEXT, 0.26, "l")
        wld = leader(st, 0.0, -0.75, CX + r["h12"] + 0.05, Yz(3000), P.TEXT)
        st.fade_in(wbe + wld, t_e - 0.1, 0.45)
        rip(st, CX + r["h12"] + 0.05, Yz(3000), t_e, t_e + 1.6, P.TEXT, period=0.8, r0=0.1, r1=0.6, end=b.end)
        t_o = W(b, 0, "one object")
        oo = st.text("one object that helps stop flow", 0.0, -1.38, 0.19, P.MUTED, 0.4, align="l")
        st.fade_in(oo, t_o, 0.4)
        # accepted on a documented design and a pressure test
        t_d, t_p = W(b, 0, "documented design"), W(b, 0, "pressure test")
        doc = [st.rect(0.25, -2.35, 0.42, 0.55, P.TEXT, 0.4, alpha=0.9, role="flat")] + \
              [st.rect(0.25, -2.2 - 0.12 * k, 0.26, 0.03, P.BG, 0.41) for k in range(3)]
        dd = st.text("documented design", 0.6, -2.35, 0.2, P.TEXT, 0.4, align="l", kind="bold")
        st.fade_in(doc + [dd], t_d - 0.1, 0.4)
        pt = chip(st, 3.45, -2.35, "✓ pressure test", P.SAFE, 0.2, "l")
        st.fade_in(pt, t_p, 0.4)
        parr = []
        for z in (900, 1700, 2500):
            for sd in (-1, 1):
                parr += st.arrow(CX + sd * 0.05, Yz(z), CX + sd * (r["c9"] - 0.07), Yz(z), L_BURST, 0.045, 0.13, 0.45)
        st.fade_in(parr, t_p - 0.3, 0.3)
        st.fade_out(parr, t_p + 2.0, 0.5)
        # the conductor: structure, not barrier
        t_cd = W(b, 1, "conductor")
        st.recolor(walls["c30"], t_cd, t_cd + 0.4, "#4a5466")
        cdl = chip(st, 0.0, 2.05, "30 in conductor: structure, not barrier", P.MUTED, 0.2, "l")
        cdd = leader(st, 0.0, 2.05, CX + r["c30"], (ysb + Yz(sh30)) / 2, P.MUTED)
        st.fade_in(cdl + cdd, max(t_cd - 0.1, tl["5.07"].sent_end[0] + 0.7), 0.4)


def build(st, tl):
    F.header(st, tl)
    F.well_strip(st, 0.0, tl.dur, strings=[p.name for p in M.programme()], marker=M.TD)
    beat_lining(st, tl)
    beat_modes(st, tl)
    beat_loads(st, tl)
    beat_vme(st, tl)
    beat_taper(st, tl)
    beat_connections(st, tl)
    beat_barrier_element(st, tl)
