"""2D vector graphics toolkit (pycairo) for overlays, diagrams and charts."""
import math

import cairo

import palette as P

W, H = 1920, 1080


# ------------------------------------------------------------------ colour / easing

def rgb(h, a=1.0):
    if isinstance(h, tuple):
        return h if len(h) == 4 else h + (a,)
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def mix(c0, c1, t):
    a, b = rgb(c0), rgb(c1)
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(4))


def with_alpha(c, a):
    c = rgb(c)
    return (c[0], c[1], c[2], c[3] * a)


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def ease_in_out(t):
    t = clamp(t)
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t * t * t


def ease_out_back(t, s=1.70158):
    t = clamp(t)
    return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2


def linear(t):
    return clamp(t)


def prog(t, t0, dur, ease=ease_in_out):
    if dur <= 0:
        return 1.0 if t >= t0 else 0.0
    return ease((t - t0) / dur)


def window(t, t0, t1, fade=0.4, ease=ease_in_out):
    """1 inside [t0, t1], fading in/out over `fade` seconds at each end."""
    return min(prog(t, t0, fade, ease), 1 - prog(t, t1 - fade, fade, ease))


# ------------------------------------------------------------------ canvas

class Canvas:
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.ctx = cairo.Context(self.surface)
        fo = cairo.FontOptions()
        fo.set_antialias(cairo.ANTIALIAS_GRAY)
        fo.set_hint_style(cairo.HINT_STYLE_NONE)
        fo.set_hint_metrics(cairo.HINT_METRICS_OFF)
        self.ctx.set_font_options(fo)
        self.ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    def clear(self):
        c = self.ctx
        c.save()
        c.set_operator(cairo.OPERATOR_CLEAR)
        c.paint()
        c.restore()


def set_color(ctx, col, alpha=1.0):
    r, g, b, a = rgb(col)
    ctx.set_source_rgba(r, g, b, a * alpha)


# ------------------------------------------------------------------ backgrounds

def bg_gradient(ctx, top=P.BG_TOP, bot=P.BG_BOT, w=W, h=H, vignette=0.10):
    g = cairo.LinearGradient(0, 0, 0, h)
    g.add_color_stop_rgba(0, *rgb(top))
    g.add_color_stop_rgba(1, *rgb(bot))
    ctx.set_source(g)
    ctx.paint()
    if vignette > 0:
        rg = cairo.RadialGradient(w / 2, h / 2, h * 0.35, w / 2, h / 2, h * 1.05)
        rg.add_color_stop_rgba(0, 0, 0, 0, 0)
        rg.add_color_stop_rgba(1, 0.05, 0.08, 0.12, vignette)
        ctx.set_source(rg)
        ctx.paint()


def bg_multi(ctx, stops, w=W, h=H, vignette=0.12):
    """Vertical gradient with [(pos, colour), ...] stops."""
    g = cairo.LinearGradient(0, 0, 0, h)
    for pos, col in stops:
        g.add_color_stop_rgba(pos, *rgb(col))
    ctx.set_source(g)
    ctx.paint()
    if vignette > 0:
        rg = cairo.RadialGradient(w / 2, h / 2, h * 0.35, w / 2, h / 2, h * 1.05)
        rg.add_color_stop_rgba(0, 0, 0, 0, 0)
        rg.add_color_stop_rgba(1, 0.02, 0.04, 0.08, vignette)
        ctx.set_source(rg)
        ctx.paint()


def dot_grid(ctx, spacing=48, r=1.3, col='#9FB3C8', alpha=0.35, w=W, h=H):
    set_color(ctx, col, alpha)
    for y in range(spacing // 2, h, spacing):
        for x in range(spacing // 2, w, spacing):
            ctx.arc(x, y, r, 0, math.tau)
            ctx.fill()


# ------------------------------------------------------------------ shapes

def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def shadow_rrect(ctx, x, y, w, h, r, alpha=0.18, spread=10, dy=6):
    for i in range(spacing := 5):
        k = (i + 1) / spacing
        rrect(ctx, x - spread * k * 0.5, y - spread * k * 0.5 + dy, w + spread * k, h + spread * k,
              r + spread * k * 0.5)
        ctx.set_source_rgba(0.05, 0.08, 0.12, alpha / spacing * (1 - k * 0.6))
        ctx.fill()


def circle(ctx, x, y, r, fill=None, stroke=None, lw=2, alpha=1.0):
    ctx.new_path()
    ctx.arc(x, y, r, 0, math.tau)
    if fill:
        set_color(ctx, fill, alpha)
        ctx.fill_preserve() if stroke else ctx.fill()
    if stroke:
        set_color(ctx, stroke, alpha)
        ctx.set_line_width(lw)
        ctx.stroke()


def poly(ctx, pts, fill=None, stroke=None, lw=2, alpha=1.0, close=True):
    ctx.new_path()
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()
    if fill:
        set_color(ctx, fill, alpha)
        if stroke:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if stroke:
        set_color(ctx, stroke, alpha)
        ctx.set_line_width(lw)
        ctx.stroke()


def rect(ctx, x, y, w, h, fill=None, stroke=None, lw=2, alpha=1.0):
    poly(ctx, [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], fill, stroke, lw, alpha)


def path_length(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def partial(pts, p):
    """Leading portion of a polyline covering fraction p of its length."""
    if p <= 0:
        return pts[:1]
    if p >= 1:
        return list(pts)
    total = path_length(pts)
    target = total * p
    out = [pts[0]]
    acc = 0
    for i in range(len(pts) - 1):
        d = math.dist(pts[i], pts[i + 1])
        if acc + d >= target:
            k = (target - acc) / d if d else 0
            out.append((lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k)))
            return out
        acc += d
        out.append(pts[i + 1])
    return out


def point_at(pts, p):
    return partial(pts, p)[-1]


def line(ctx, pts, col=P.INK, lw=3, alpha=1.0, p=1.0, dash=None):
    pts = partial(pts, p)
    if len(pts) < 2:
        return
    ctx.new_path()
    ctx.move_to(*pts[0])
    for q in pts[1:]:
        ctx.line_to(*q)
    set_color(ctx, col, alpha)
    ctx.set_line_width(lw)
    if dash:
        ctx.set_dash(dash)
    ctx.stroke()
    ctx.set_dash([])


def arrow(ctx, x0, y0, x1, y1, col=P.INK, lw=5, head=18, p=1.0, alpha=1.0, both=False):
    if p <= 0:
        return
    x1p, y1p = lerp(x0, x1, p), lerp(y0, y1, p)
    ang = math.atan2(y1p - y0, x1p - x0)
    L = math.hypot(x1p - x0, y1p - y0)
    hd = min(head, L * 0.6)
    bx, by = x1p - hd * 0.8 * math.cos(ang), y1p - hd * 0.8 * math.sin(ang)
    sx, sy = x0, y0
    if both:
        sx, sy = x0 + hd * 0.8 * math.cos(ang), y0 + hd * 0.8 * math.sin(ang)
    line(ctx, [(sx, sy), (bx, by)], col, lw, alpha)
    _head(ctx, x1p, y1p, ang, hd, col, alpha)
    if both:
        _head(ctx, x0, y0, ang + math.pi, hd, col, alpha)


def _head(ctx, x, y, ang, hd, col, alpha):
    a1, a2 = ang + math.radians(152), ang - math.radians(152)
    poly(ctx, [(x, y), (x + hd * math.cos(a1), y + hd * math.sin(a1)),
               (x + hd * math.cos(a2), y + hd * math.sin(a2))], fill=col, alpha=alpha)


def arrow_path(ctx, pts, col=P.INK, lw=5, head=18, p=1.0, alpha=1.0):
    pts = partial(pts, p)
    if len(pts) < 2:
        return
    x1, y1 = pts[-1]
    x0, y0 = pts[-2]
    ang = math.atan2(y1 - y0, x1 - x0)
    trimmed = pts[:-1] + [(x1 - head * 0.7 * math.cos(ang), y1 - head * 0.7 * math.sin(ang))]
    line(ctx, trimmed, col, lw, alpha)
    _head(ctx, x1, y1, ang, head, col, alpha)


# ------------------------------------------------------------------ text

FONT = 'Montserrat'
WEIGHTS = {'Light': 'Montserrat Light', 'Regular': 'Montserrat', 'Medium': 'Montserrat Medium',
           'SemiBold': 'Montserrat SemiBold', 'Bold': 'Montserrat', 'ExtraBold': 'Montserrat ExtraBold'}


def font(ctx, size, weight='SemiBold', italic=False, family=None):
    fam = family or WEIGHTS.get(weight, FONT)
    w = cairo.FONT_WEIGHT_BOLD if weight == 'Bold' else cairo.FONT_WEIGHT_NORMAL
    s = cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL
    ctx.select_font_face(fam, s, w)
    ctx.set_font_size(size)


def text_w(ctx, s, size, weight='SemiBold', family=None, italic=False):
    font(ctx, size, weight, italic, family)
    return ctx.text_extents(s).x_advance


def text(ctx, s, x, y, size=36, weight='SemiBold', col=P.INK, align='left', valign='baseline',
         alpha=1.0, family=None, italic=False, tracking=0.0, shadow=None):
    """Draw a single line. Returns (width, height) of the text box."""
    if alpha <= 0.001 or not s:
        return 0, 0
    font(ctx, size, weight, italic, family)
    fe = ctx.font_extents()
    if tracking:
        widths = [ctx.text_extents(ch).x_advance for ch in s]
        tw = sum(widths) + tracking * size * (len(s) - 1)
    else:
        tw = ctx.text_extents(s).x_advance
    if align == 'center':
        x -= tw / 2
    elif align == 'right':
        x -= tw
    asc = size * 0.72  # cap height approx for Montserrat
    if valign == 'middle':
        y += asc / 2
    elif valign == 'top':
        y += asc
    if shadow:
        set_color(ctx, shadow[0], alpha * shadow[1])
        _show(ctx, s, x + shadow[2], y + shadow[2], tracking, size)
    set_color(ctx, col, alpha)
    _show(ctx, s, x, y, tracking, size)
    return tw, fe[0]


def _show(ctx, s, x, y, tracking, size):
    if not tracking:
        ctx.move_to(x, y)
        ctx.show_text(s)
        return
    cx = x
    for ch in s:
        ctx.move_to(cx, y)
        ctx.show_text(ch)
        cx += ctx.text_extents(ch).x_advance + tracking * size


def wrap(ctx, s, maxw, size, weight='SemiBold'):
    font(ctx, size, weight)
    words = s.split()
    lines, cur = [], ''
    for wd in words:
        trial = (cur + ' ' + wd).strip()
        if ctx.text_extents(trial).x_advance > maxw and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def paragraph(ctx, s, x, y, maxw, size=34, weight='Medium', col=P.INK, lh=1.3, align='left',
              alpha=1.0):
    lines = wrap(ctx, s, maxw, size, weight)
    for i, ln in enumerate(lines):
        text(ctx, ln, x, y + i * size * lh, size, weight, col, align, alpha=alpha)
    return len(lines) * size * lh


def rich(ctx, parts, x, y, size=48, col=P.INK, align='left', alpha=1.0):
    """Draw a line made of (string, style) parts; style: 'math', 'mathup', 'bold', 'normal'."""
    fams = {'math': ('Noto Serif', True, 'Regular'), 'mathup': ('Noto Serif', False, 'Regular'),
            'bold': (None, False, 'Bold'), 'normal': (None, False, 'SemiBold'),
            'light': (None, False, 'Medium'), 'sub': (None, False, 'SemiBold'),
            'xbold': (None, False, 'ExtraBold')}
    widths = []
    for part in parts:
        s, st = part[0], part[1]
        fam, it, wt = fams.get(st, fams['normal'])
        sz = size * 0.55 if st == 'sub' else size
        widths.append(text_w(ctx, s, sz, wt, fam, it))
    total = sum(widths)
    if align == 'center':
        x -= total / 2
    elif align == 'right':
        x -= total
    cx = x
    for part, wd in zip(parts, widths):
        s, st = part[0], part[1]
        c = part[2] if len(part) > 2 else col
        fam, it, wt = fams.get(st, fams['normal'])
        sz = size * 0.55 if st == 'sub' else size
        yy = y + size * 0.18 if st == 'sub' else y
        text(ctx, s, cx, yy, sz, wt, c, alpha=alpha, family=fam, italic=it)
        cx += wd
    return total


def pore_inset(ctx, cx, cy, r, fluid=P.PRIMARY, grain='#E6C98E', t=0.0, alpha=1.0,
               arrows=True, seed=11, oil=False):
    """Magnified view of sand grains with fluid in the pore space."""
    import random
    if alpha <= 0:
        return
    rnd = random.Random(seed)
    ctx.save()
    ctx.new_path()
    ctx.arc(cx, cy, r, 0, math.tau)
    ctx.clip()
    set_color(ctx, fluid, alpha)
    ctx.paint()
    # grains
    placed = []
    tries = 0
    while len(placed) < 60 and tries < 3000:
        tries += 1
        gr = rnd.uniform(r * 0.14, r * 0.24)
        gx, gy = cx + rnd.uniform(-r, r), cy + rnd.uniform(-r, r)
        if all(math.hypot(gx - px, gy - py) > (gr + pr) * 0.93 for px, py, pr in placed):
            placed.append((gx, gy, gr))
    for gx, gy, gr in placed:
        shade = rnd.uniform(0.92, 1.05)
        c = rgb(grain)
        col = (min(1, c[0] * shade), min(1, c[1] * shade), min(1, c[2] * shade), 1)
        ctx.new_path()
        n = 9
        for i in range(n):
            a = math.tau * i / n
            rr = gr * rnd.uniform(0.86, 1.0)
            ctx.line_to(gx + rr * math.cos(a), gy + rr * math.sin(a))
        ctx.close_path()
        set_color(ctx, col, alpha)
        ctx.fill_preserve()
        set_color(ctx, '#8C6A3A', alpha * 0.6)
        ctx.set_line_width(2)
        ctx.stroke()
    ctx.restore()
    circle(ctx, cx, cy, r, stroke=P.WHITE, lw=10, alpha=alpha)
    circle(ctx, cx, cy, r + 5, stroke=P.INK, lw=2, alpha=alpha * 0.4)


# ------------------------------------------------------------------ callouts

def label(ctx, ax, ay, tx, ty, s, p, col=P.INK, bg=P.WHITE, size=28, weight='SemiBold',
          dot_col=None, line_col=None, sub=None, sub_col=P.INK_SOFT, align=None, out=0.0,
          elbow=True):
    """Animated callout: anchor dot -> leader line -> text pill.

    p: 0..1 build-in progress; out: 0..1 fade-out progress.
    (ax, ay) anchor point; (tx, ty) where the pill's attach side sits.
    """
    if p <= 0 or out >= 1:
        return
    a = 1 - ease_in_out(out)
    dot_col = dot_col or P.WHITE
    line_col = line_col or P.WHITE
    pd = ease_out_back(clamp(p / 0.3))
    pl = ease_in_out(clamp((p - 0.15) / 0.45))
    pt = ease_out(clamp((p - 0.45) / 0.55))
    # leader line (optionally horizontal elbow)
    if align is None:
        align = 'left' if tx >= ax else 'right'
    pts = [(ax, ay), (tx, ty)]
    if elbow:
        ex = tx - (30 if align == 'left' else -30)
        pts = [(ax, ay), (ex, ty), (tx, ty)]
    if pl > 0:
        line(ctx, pts, (0.05, 0.08, 0.12, 0.35), 5, a, pl)
        line(ctx, pts, line_col, 2.4, a, pl)
    # anchor dot
    circle(ctx, ax, ay, 9 * pd, fill=(0.05, 0.08, 0.12, 0.25), alpha=a)
    circle(ctx, ax, ay, 7 * pd, fill=dot_col, alpha=a)
    circle(ctx, ax, ay, 3.2 * pd, fill=P.INK, alpha=a)
    if pt <= 0:
        return
    tw = text_w(ctx, s, size, weight)
    sw = text_w(ctx, sub, size * 0.72, 'Medium') if sub else 0
    padx, pady = size * 0.55, size * 0.42
    bw = max(tw, sw) + 2 * padx
    bh = size * 0.78 + 2 * pady + (size * 0.95 if sub else 0)
    bx = tx if align == 'left' else tx - bw
    by = ty - bh / 2
    slide = (1 - pt) * 14 * (1 if align == 'left' else -1)
    bx -= slide
    shadow_rrect(ctx, bx, by, bw, bh, bh / 2 if not sub else 14, alpha=0.22 * a * pt)
    rrect(ctx, bx, by, bw, bh, min(bh / 2, 16) if sub else bh / 2)
    set_color(ctx, bg, a * pt * 0.96)
    ctx.fill()
    text(ctx, s, bx + padx, by + pady + size * 0.74, size, weight, col, alpha=a * pt)
    if sub:
        text(ctx, sub, bx + padx, by + pady + size * 0.74 + size * 0.95, size * 0.72, 'Medium',
             sub_col, alpha=a * pt)


def tag(ctx, s, x, y, p=1.0, col=P.WHITE, bg=P.INK, size=26, weight='Bold', align='left',
        alpha=1.0, tracking=0.08, padx=None):
    """Solid pill with text (for headings/badges)."""
    if p <= 0:
        return 0
    pe = ease_out(p)
    tw = text_w(ctx, s, size, weight) + tracking * size * (len(s) - 1)
    padx = size * 0.7 if padx is None else padx
    bw, bh = tw + 2 * padx, size * 1.7
    if align == 'center':
        x -= bw / 2
    elif align == 'right':
        x -= bw
    rrect(ctx, x, y - bh / 2, bw * (0.6 + 0.4 * pe), bh, bh / 2)
    set_color(ctx, bg, alpha * pe)
    ctx.fill()
    text(ctx, s, x + padx, y, size, weight, col, valign='middle', alpha=alpha * pe,
         tracking=tracking)
    return bw


def panel(ctx, x, y, w, h, p=1.0, col=P.WHITE, alpha=0.92, r=22, shadow=True):
    if p <= 0:
        return
    pe = ease_out(p)
    yy = y + (1 - pe) * 20
    if shadow:
        shadow_rrect(ctx, x, yy, w, h, r, alpha=0.25 * pe)
    rrect(ctx, x, yy, w, h, r)
    set_color(ctx, col, alpha * pe)
    ctx.fill()


# ------------------------------------------------------------------ titles

def chapter_title(ctx, num, title, t, t_in, t_out, sub=None, accent=P.ACCENT, dark=False,
                  backdrop=False):
    """Big chapter card: number badge + title + accent underline."""
    pin = prog(t, t_in, 0.9, ease_out)
    pout = prog(t, t_out, 0.6, ease_in)
    if pin <= 0 or pout >= 1:
        return
    a = 1 - pout
    col = P.WHITE if dark else P.INK
    cx, cy = W / 2, H / 2
    if backdrop:
        shadow_rrect(ctx, cx - 520, cy - 230, 1040, 420, 40, alpha=0.3 * a * pin)
        rrect(ctx, cx - 520, cy - 230, 1040, 420, 40)
        set_color(ctx, '#F4F7FA', 0.93 * a * pin)
        ctx.fill()
    # number badge
    r = 54 * ease_out_back(pin)
    circle(ctx, cx, cy - 120, r, fill=accent, alpha=a)
    text(ctx, str(num), cx, cy - 120, 58, 'ExtraBold', P.WHITE, 'center', 'middle', alpha=a * pin)
    text(ctx, title.upper(), cx, cy + 20 + (1 - pin) * 30, 96, 'ExtraBold', col, 'center',
         alpha=a * pin, tracking=0.06)
    bw = 260 * ease_in_out(prog(t, t_in + 0.3, 0.8))
    rrect(ctx, cx - bw / 2, cy + 58, bw, 8, 4)
    set_color(ctx, accent, a)
    ctx.fill()
    if sub:
        text(ctx, sub, cx, cy + 130, 38, 'Medium', P.INK_SOFT if not dark else '#D6E4F0', 'center',
             alpha=a * prog(t, t_in + 0.5, 0.8))


PHASES = ['Design', 'Drilling', 'Completion', 'P&A']


def phase_tracker(ctx, active, t, t_in=0.0, dark=False, x=48, y=52):
    """Small persistent top-left progress indicator of the four phases."""
    a = prog(t, t_in, 0.6)
    if a <= 0:
        return
    cx = x
    for i, ph in enumerate(PHASES):
        on = (i == active)
        done = i < active
        s = f'{i + 1}  {ph.upper()}'
        size = 19
        tw = text_w(ctx, s, size, 'Bold') + 0.08 * size * (len(s) - 1)
        bw, bh = tw + 28, 36
        rrect(ctx, cx, y - bh / 2, bw, bh, bh / 2)
        if on:
            set_color(ctx, P.ACCENT, 0.95 * a)
            ctx.fill()
            tc = P.WHITE
        else:
            set_color(ctx, P.WHITE if not dark else '#0E2A44', (0.55 if not dark else 0.55) * a)
            ctx.fill()
            tc = P.INK_SOFT if not dark else '#B8CDE0'
            if done:
                tc = P.INK if not dark else '#E3EEF7'
        text(ctx, s, cx + 14, y, size, 'Bold', tc, valign='middle', alpha=a, tracking=0.08)
        cx += bw + 10


def subtitle_bar(ctx, s, alpha=1.0):
    if not s or alpha <= 0:
        return
    lines = wrap(ctx, s, 1500, 30, 'Medium')
    y0 = H - 70 - (len(lines) - 1) * 40
    for i, ln in enumerate(lines):
        tw = text_w(ctx, ln, 30, 'Medium')
        rrect(ctx, W / 2 - tw / 2 - 14, y0 + i * 40 - 30, tw + 28, 42, 8)
        ctx.set_source_rgba(0, 0, 0, 0.55 * alpha)
        ctx.fill()
        text(ctx, ln, W / 2, y0 + i * 40, 30, 'Medium', P.WHITE, 'center', alpha=alpha)


# ------------------------------------------------------------------ chart

class Chart:
    """Simple 2D chart mapping data coordinates into a pixel rectangle."""

    def __init__(self, x, y, w, h, xr, yr, y_down=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.xr, self.yr = xr, yr
        self.y_down = y_down

    def px(self, dx, dy):
        u = (dx - self.xr[0]) / (self.xr[1] - self.xr[0])
        v = (dy - self.yr[0]) / (self.yr[1] - self.yr[0])
        X = self.x + u * self.w
        Y = self.y + v * self.h if self.y_down else self.y + self.h - v * self.h
        return X, Y

    def pts(self, data):
        return [self.px(a, b) for a, b in data]

    def axes(self, ctx, p=1.0, col=P.INK, xlabel=None, ylabel=None, xticks=(), yticks=(),
             alpha=1.0, grid=True, tick_fmt=str, size=24):
        if p <= 0:
            return
        o = self.px(self.xr[0], self.yr[0])
        xe = self.px(self.xr[1], self.yr[0])
        ye = self.px(self.xr[0], self.yr[1])
        if grid:
            for v in yticks:
                a0 = self.px(self.xr[0], v)
                a1 = self.px(self.xr[1], v)
                line(ctx, [a0, a1], '#9DB0C3', 1.2, alpha * 0.5 * p)
            for v in xticks:
                a0 = self.px(v, self.yr[0])
                a1 = self.px(v, self.yr[1])
                line(ctx, [a0, a1], '#9DB0C3', 1.2, alpha * 0.5 * p)
        arrow(ctx, o[0], o[1], xe[0] + 24, xe[1], col, 3.5, 16, p, alpha)
        arrow(ctx, o[0], o[1], ye[0], ye[1] + (24 if self.y_down else -24), col, 3.5, 16, p, alpha)
        ta = alpha * prog(p, 0.5, 0.5, linear)
        for v in xticks:
            X, Y = self.px(v, self.yr[0])
            ty = Y - 14 if self.y_down else Y + 34
            text(ctx, tick_fmt(v), X, ty, size, 'Medium', P.INK_SOFT, 'center', alpha=ta)
        for v in yticks:
            X, Y = self.px(self.xr[0], v)
            text(ctx, tick_fmt(v), X - 14, Y, size, 'Medium', P.INK_SOFT, 'right', 'middle',
                 alpha=ta)
        if xlabel:
            X, Y = self.px((self.xr[0] + self.xr[1]) / 2, self.yr[0])
            ty = Y - 52 if self.y_down else Y + 78
            text(ctx, xlabel, X, ty, size + 4, 'SemiBold', col, 'center', alpha=ta)
        if ylabel:
            X, Y = self.px(self.xr[0], (self.yr[0] + self.yr[1]) / 2)
            ctx.save()
            ctx.translate(X - 90, Y)
            ctx.rotate(-math.pi / 2)
            text(ctx, ylabel, 0, 0, size + 4, 'SemiBold', col, 'center', alpha=ta)
            ctx.restore()

    def curve(self, ctx, data, col, lw=6, p=1.0, alpha=1.0, dash=None, glow=True):
        pts = self.pts(data)
        if glow:
            line(ctx, pts, col, lw * 2.6, alpha * 0.18, p, dash)
        line(ctx, pts, col, lw, alpha, p, dash)
        return point_at(pts, p) if p > 0 else None

    def band(self, ctx, lo, hi, col, alpha=0.3, p=1.0):
        """Fill between two curves sharing the same y samples (depth-down charts)."""
        if p <= 0:
            return
        n = max(2, int(len(lo) * p))
        a = self.pts(lo[:n])
        b = self.pts(hi[:n])
        poly(ctx, a + b[::-1], fill=col, alpha=alpha)
