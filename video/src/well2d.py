"""2D well cross-section diagrams (cairo), sharing depths/colours with the 3D models.

Depths here are metres below sea level (MSL); water depth is 350 m.
"""
import math
import os

import cairo

import gfx as G
import palette as P

WD = 350.0
# (name, top MSL, base MSL, colour, texture)
STRATA = [
    ('Soft clay', 350, 600, P.SOFT_CLAY, 'soft_clay'),
    ('Claystone', 600, 1250, P.CLAYSTONE, 'claystone'),
    ('Siltstone', 1250, 1850, P.SILTSTONE, 'siltstone'),
    ('Chalk', 1850, 2500, P.CHALK, 'chalk'),
    ('Claystone', 2500, 3150, '#A2957F', 'claystone2'),
    ('Cap rock', 3150, 3300, P.SHALE, 'shale'),
    ('Reservoir', 3300, 3450, P.RESERVOIR, 'reservoir'),
    ('Water zone', 3450, 3650, P.WATER_ZONE, 'water_zone'),
    ('Deeper rock', 3650, 4200, P.BASEMENT, 'basement'),
]
# label, OD (in), hole (in), shoe MSL (m), top MSL (m)
CASINGS = [
    ('30" conductor', 30.0, 36.0, 430, 350),
    ('20" surface casing', 20.0, 26.0, 1350, 350),
    ('13⅜" intermediate', 13.375, 17.5, 2350, 350),
    ('9⅝" production', 9.625, 12.25, 3230, 350),
    ('7" liner', 7.0, 8.5, 3430, 3130),
]

# pressure profiles as equivalent mud density (s.g.) vs depth MSL (m)
PORE = [(350, 1.03), (1200, 1.04), (1600, 1.12), (2000, 1.24), (2350, 1.33), (2700, 1.40),
        (3230, 1.42), (3300, 1.37), (3450, 1.35)]
FRAC = [(350, 1.12), (600, 1.25), (900, 1.36), (1350, 1.45), (1700, 1.55), (2350, 1.68),
        (2900, 1.76), (3450, 1.80)]
MUD_STEPS = [(350, 430, 1.03), (430, 1350, 1.05), (1350, 2350, 1.40), (2350, 3230, 1.50),
             (3230, 3430, 1.45)]


def interp(table, d):
    if d <= table[0][0]:
        return table[0][1]
    for (d0, v0), (d1, v1) in zip(table[:-1], table[1:]):
        if d0 <= d <= d1:
            return v0 + (v1 - v0) * (d - d0) / (d1 - d0)
    return table[-1][1]


def sample(table, d0, d1, n=80):
    return [(interp(table, d0 + (d1 - d0) * i / n), d0 + (d1 - d0) * i / n) for i in range(n + 1)]


_PATTERNS = {}


def pattern(texname, scale=0.5):
    key = (texname, scale)
    if key not in _PATTERNS:
        import textures
        paths = textures.build_all()
        img = cairo.ImageSurface.create_from_png(paths[texname])
        pat = cairo.SurfacePattern(img)
        pat.set_extend(cairo.EXTEND_REPEAT)
        m = cairo.Matrix()
        m.scale(1 / scale, 1 / scale)
        pat.set_matrix(m)
        pat.set_filter(cairo.FILTER_GOOD)
        _PATTERNS[key] = (pat, img)
    return _PATTERNS[key][0]


class Well2D:
    """Depth->pixel mapping plus drawing primitives for a vertical well section."""

    def __init__(self, cx, knots, x0, x1, k=2.0, strata=STRATA, casings=CASINGS, pat_scale=0.45):
        """knots: [(depth_m, y_px), ...] piecewise-linear depth mapping."""
        self.cx = cx
        self.knots = knots
        self.x0, self.x1 = x0, x1
        self.k = k          # px per inch of diameter (half-width = k * inches / 2)
        self.strata = strata
        self.casings = casings
        self.pat_scale = pat_scale
        self._static = None

    def y(self, d):
        return interp([(a, b) for a, b in self.knots], d)

    def hw(self, inches):
        return self.k * inches / 2

    def hole_hw(self, d):
        prev = WD
        for (_, od, hole, shoe, top) in self.casings:
            if prev <= d <= shoe:
                return self.hw(hole)
            prev = shoe
        return self.hw(self.casings[-1][2])

    # ------------------------------------------------------------ static layers
    def draw_earth(self, ctx, d_top=None, d_bot=None, sea=True, sky=False, labels=False,
                   alpha=1.0):
        y_sea = self.y(0)
        y_bed = self.y(WD)
        top = self.knots[0][1]
        bot = self.knots[-1][1]
        if sea:
            g = cairo.LinearGradient(0, y_sea, 0, y_bed)
            g.add_color_stop_rgba(0, *G.rgb('#5DB2E6', alpha))
            g.add_color_stop_rgba(1, *G.rgb('#1F6FA8', alpha))
            ctx.rectangle(self.x0, max(top, y_sea), self.x1 - self.x0, y_bed - max(top, y_sea))
            ctx.set_source(g)
            ctx.fill()
        for (name, dt, db, col, tex) in self.strata:
            yt, yb = self.y(dt), self.y(db)
            if yb <= top or yt >= bot:
                continue
            yt, yb = max(yt, top), min(yb, bot)
            ctx.rectangle(self.x0, yt, self.x1 - self.x0, yb - yt)
            ctx.set_source(pattern(tex, self.pat_scale))
            ctx.paint_with_alpha(alpha) if False else None
            ctx.save()
            ctx.clip()
            ctx.paint_with_alpha(alpha)
            ctx.restore()
            G.line(ctx, [(self.x0, yt), (self.x1, yt)], (0, 0, 0, 0.18), 1.5, alpha)
            if labels:
                G.text(ctx, name, self.x1 - 16, (yt + yb) / 2, 20, 'SemiBold',
                       '#FFFFFF' if name in ('Cap rock',) else P.INK_SOFT, 'right', 'middle',
                       alpha=alpha * 0.9)
        # seabed line
        if top <= y_bed <= bot:
            G.line(ctx, [(self.x0, y_bed), (self.x1, y_bed)], '#8A7A5A', 3, alpha)

    def fill_bore(self, ctx, d_top, d_bot, col, alpha=1.0, hw=None, extra=0):
        """Fill the open bore between depths with a fluid colour (stepped hole width)."""
        if d_bot <= d_top:
            return
        pts_l, pts_r = [], []
        steps = [d_top] + [c[3] for c in self.casings if d_top < c[3] < d_bot] + [d_bot]
        for a, b in zip(steps[:-1], steps[1:]):
            w = (hw if hw is not None else self.hole_hw((a + b) / 2)) + extra
            pts_l += [(self.cx - w, self.y(a)), (self.cx - w, self.y(b))]
            pts_r += [(self.cx + w, self.y(a)), (self.cx + w, self.y(b))]
        G.poly(ctx, pts_l + pts_r[::-1], fill=col, alpha=alpha)

    def casing(self, ctx, i, p=1.0, alpha=1.0, col=P.STEEL_DARK, lw=None, shoe=True,
               top_override=None):
        """Draw casing string i as two vertical walls, run in to fraction p of its length."""
        if p <= 0:
            return
        _, od, hole, shoe_d, top_d = self.casings[i]
        top_d = top_override if top_override is not None else top_d
        L = shoe_d - top_d
        bot = top_d + L * p
        # during running, the whole string slides down from above: draw from bot-L..bot
        t_d = bot - L
        w = self.hw(od)
        th = lw or max(4.0, self.k * 0.9)
        for s in (-1, 1):
            x = self.cx + s * (w - th / 2)
            G.line(ctx, [(x, self.y(max(t_d, self.knots[0][0]))), (x, self.y(bot))], col, th,
                   alpha)
        if shoe and p > 0.98:
            for s in (-1, 1):
                x = self.cx + s * w
                yb = self.y(shoe_d)
                G.poly(ctx, [(x, yb), (x + s * 12, yb), (x, yb - 16)], fill=col, alpha=alpha)

    def cement(self, ctx, i, p=1.0, alpha=1.0, top_d=None, col=None):
        """Cement in the annulus of casing i, rising from the shoe to fraction p."""
        if p <= 0:
            return
        _, od, hole, shoe_d, ctop = self.casings[i]
        ctop = top_d if top_d is not None else (ctop if i < 2 else self.casings[i - 1][3] - 250)
        cur_top = shoe_d - (shoe_d - ctop) * p
        w_in = self.hw(od)
        prev_shoe = self.casings[i - 1][3] if i > 0 else WD
        segs = []
        # open-hole part
        a = max(cur_top, prev_shoe)
        if a < shoe_d:
            segs.append((a, shoe_d, self.hw(hole)))
        # overlap inside previous casing
        if i > 0 and cur_top < prev_shoe:
            pw = self.hw(self.casings[i - 1][1]) - max(4.0, self.k * 0.9)
            segs.append((cur_top, prev_shoe, pw))
        for (a, b, wo) in segs:
            for s in (-1, 1):
                x0, x1 = self.cx + s * w_in, self.cx + s * wo
                ctx.rectangle(min(x0, x1), self.y(a), abs(x1 - x0), self.y(b) - self.y(a))
                ctx.save()
                ctx.clip()
                if col:
                    G.set_color(ctx, col, alpha)
                    ctx.paint()
                else:
                    ctx.set_source(pattern('cement', 0.35))
                    ctx.paint_with_alpha(alpha)
                ctx.restore()


def gauge(ctx, cx, cy, r, value, vmax, label=None, col=P.INK, needle=P.KICK, alpha=1.0,
          unit=''):
    """Round pressure gauge with a needle (value in 0..vmax)."""
    if alpha <= 0:
        return
    G.circle(ctx, cx, cy, r + 6, fill='#2A3440', alpha=alpha)
    G.circle(ctx, cx, cy, r, fill='#FFFFFF', alpha=alpha)
    a0, a1 = math.radians(135), math.radians(405)
    for i in range(11):
        a = a0 + (a1 - a0) * i / 10
        L = 14 if i % 5 == 0 else 8
        G.line(ctx, [(cx + (r - 6) * math.cos(a), cy + (r - 6) * math.sin(a)),
                     (cx + (r - 6 - L) * math.cos(a), cy + (r - 6 - L) * math.sin(a))],
               '#2A3440', 3 if i % 5 == 0 else 2, alpha)
    # red zone
    ctx.new_path()
    ctx.arc(cx, cy, r - 10, a0 + (a1 - a0) * 0.8, a1)
    G.set_color(ctx, P.KICK, alpha * 0.7)
    ctx.set_line_width(6)
    ctx.stroke()
    v = max(0, min(1, value / vmax))
    a = a0 + (a1 - a0) * v
    G.line(ctx, [(cx - 12 * math.cos(a), cy - 12 * math.sin(a)),
                 (cx + (r - 18) * math.cos(a), cy + (r - 18) * math.sin(a))], needle, 5, alpha)
    G.circle(ctx, cx, cy, 8, fill='#2A3440', alpha=alpha)
    if label:
        G.text(ctx, label, cx, cy + r * 0.55, max(14, r * 0.2), 'Bold', '#2A3440', 'center',
               'middle', alpha=alpha)


# ------------------------------------------------------------------ equipment icons (2D)

def draw_bop(ctx, cx, y_base, s=1.0, closed=0.0, shear=0.0, alpha=1.0, pipe=True, cut=False):
    """2D BOP stack standing on y_base (seabed/wellhead top). Height ~ 190*s px."""
    body = '#6F7C8A'
    yel = P.BOP
    bore = 16 * s
    def R(x, y, w, h, col, r=4):
        G.rrect(ctx, cx + x * s, y_base - (y + h) * s, w * s, h * s, r * s)
        G.set_color(ctx, col, alpha)
        ctx.fill()
    # frame
    G.rect(ctx, cx - 70 * s, y_base - 175 * s, 140 * s, 175 * s, stroke=yel, lw=5 * s, alpha=alpha)
    R(-42, 0, 84, 26, '#4A5663')                       # connector
    for k, y in enumerate((30, 62, 94)):               # ram bodies
        R(-40, y, 80, 28, body)
        R(-66, y + 4, 24, 20, yel, 6)
        R(42, y + 4, 24, 20, yel, 6)
    R(-46, 126, 92, 38, '#3F4A55', 16)                 # annular
    R(-22, 164, 44, 16, '#5E6B78')                     # flex / riser adapter
    # bore
    G.rect(ctx, cx - bore / 2, y_base - 180 * s, bore, 180 * s, fill='#DDE6EE', alpha=alpha)
    if pipe:
        G.rect(ctx, cx - 5 * s, y_base - 180 * s, 10 * s, 180 * s, fill=P.PIPE, alpha=alpha)
    # rams closing (pipe rams at k=0,1; shear at k=2)
    for k, y in enumerate((30, 62)):
        w = (bore / 2 - (5 * s if pipe else 0)) * closed
        for sg in (-1, 1):
            x0 = cx + sg * bore / 2
            G.rect(ctx, min(x0, x0 - sg * w), y_base - (y + 22) * s, w, 16 * s, fill='#C9D2DB',
                   alpha=alpha)
    if shear > 0:
        w = bore / 2 * shear
        for sg in (-1, 1):
            x0 = cx + sg * bore / 2
            G.rect(ctx, min(x0, x0 - sg * (w + 2 * s)), y_base - (94 + 22) * s, w + 2 * s, 16 * s,
                   fill='#E8EDF2', alpha=alpha)


def draw_xt(ctx, cx, y_base, s=1.0, alpha=1.0):
    """2D subsea christmas tree icon standing on y_base."""
    xt, dark = P.XT, P.XT_DARK
    G.rect(ctx, cx - 60 * s, y_base - 120 * s, 120 * s, 120 * s, stroke=xt, lw=5 * s, alpha=alpha)
    G.rrect(ctx, cx - 34 * s, y_base - 24 * s, 68 * s, 24 * s, 4 * s)
    G.set_color(ctx, '#4A5663', alpha)
    ctx.fill()
    G.rect(ctx, cx - 22 * s, y_base - 104 * s, 44 * s, 80 * s, fill='#8795A3', alpha=alpha)
    G.rect(ctx, cx + 22 * s, y_base - 74 * s, 60 * s, 14 * s, fill='#8795A3', alpha=alpha)
    for x in (32, 56):
        G.rect(ctx, cx + x * s, y_base - 82 * s, 14 * s, 30 * s, fill=dark, alpha=alpha)
    for y in (40, 70):
        G.rect(ctx, cx - 28 * s, y_base - (y + 12) * s, 56 * s, 12 * s, fill=dark, alpha=alpha)
    G.rrect(ctx, cx - 26 * s, y_base - 122 * s, 52 * s, 18 * s, 6 * s)
    G.set_color(ctx, dark, alpha)
    ctx.fill()


def draw_wellhead(ctx, cx, y_seabed, s=1.0, alpha=1.0):
    G.rect(ctx, cx - 26 * s, y_seabed - 18 * s, 52 * s, 30 * s, fill='#5E6B78', alpha=alpha)
    G.rect(ctx, cx - 20 * s, y_seabed - 34 * s, 40 * s, 18 * s, fill='#7E8B98', alpha=alpha)


def envelope(ctx, pts, col, p=1.0, alpha=1.0, lw=7):
    """Barrier envelope: bold line with a soft halo, drawn progressively."""
    G.line(ctx, pts, col, lw * 2.8, alpha * 0.18, p)
    G.line(ctx, pts, col, lw, alpha, p)
