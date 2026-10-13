"""Core drawing utilities for the well integrity film (skia-python)."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import skia

W, H = 1920, 1080
FPS = 30


# ----------------------------------------------------------------- colours
def rgb(h: str, a: float = 1.0) -> int:
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.Color(r, g, b, int(max(0, min(1, a)) * 255))


def with_alpha(color: int, a: float) -> int:
    return skia.ColorSetA(color, int(max(0.0, min(1.0, a)) * skia.ColorGetA(color)))


def mix(c1: int, c2: int, t: float) -> int:
    t = max(0.0, min(1.0, t))
    return skia.Color(
        int(skia.ColorGetR(c1) + (skia.ColorGetR(c2) - skia.ColorGetR(c1)) * t),
        int(skia.ColorGetG(c1) + (skia.ColorGetG(c2) - skia.ColorGetG(c1)) * t),
        int(skia.ColorGetB(c1) + (skia.ColorGetB(c2) - skia.ColorGetB(c1)) * t),
        int(skia.ColorGetA(c1) + (skia.ColorGetA(c2) - skia.ColorGetA(c1)) * t),
    )


class C:
    """Palette."""
    bg0 = rgb("#060C17")
    bg1 = rgb("#0B1628")
    bg2 = rgb("#11213A")
    panel = rgb("#0F1E35")
    panel_hi = rgb("#16294A")
    line = rgb("#2A4166")
    grid = rgb("#1A2C48")
    text = rgb("#EAF0F8")
    muted = rgb("#93A6C2")
    dim = rgb("#5E7394")
    primary = rgb("#3EA6FF")      # primary well barrier (blue)
    primary_hi = rgb("#9FD3FF")
    secondary = rgb("#FF4D5E")    # secondary well barrier (red)
    secondary_hi = rgb("#FFB0B8")
    common = rgb("#C77DFF")
    teal = rgb("#2DD4BF")
    amber = rgb("#F5B942")
    gas = rgb("#FFD27A")
    oil = rgb("#B7792B")
    water = rgb("#3E8FC7")
    brine = rgb("#6F8E99")
    mud = rgb("#8A6A48")
    kill_mud = rgb("#5E4630")
    cement = rgb("#B9B4A8")
    steel = rgb("#9AA9BA")
    steel_dk = rgb("#55657A")
    steel_hi = rgb("#E3EAF2")
    green = rgb("#34D399")
    yellow = rgb("#FACC15")
    orange = rgb("#FB923C")
    red = rgb("#F43F5E")
    white = rgb("#FFFFFF")
    black = rgb("#000000")
    co2 = rgb("#9AE6B4")


# ----------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def ease_in_out(t):  # cubic
    t = clamp(t)
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out(t):  # cubic
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t * t * t


def ease_out_back(t, s=1.4):
    t = clamp(t)
    c3 = s + 1
    return 1 + c3 * (t - 1) ** 3 + s * (t - 1) ** 2


def ease_out_quint(t):
    t = clamp(t)
    return 1 - (1 - t) ** 5


def smoothstep(a, b, x):
    t = clamp((x - a) / (b - a)) if b != a else (1.0 if x >= b else 0.0)
    return t * t * (3 - 2 * t)


def prog(t, start, dur, ease=ease_in_out):
    if dur <= 0:
        return 1.0 if t >= start else 0.0
    return ease(clamp((t - start) / dur))


def window(t, a, b, fade_in=0.5, fade_out=0.5):
    """Opacity for something visible during [a, b] with fades."""
    if t < a or t > b + fade_out:
        return 0.0
    fi = 1.0 if fade_in <= 0 else ease_in_out(clamp((t - a) / fade_in))
    fo = 1.0 if t <= b else (1.0 - ease_in_out(clamp((t - b) / fade_out)))
    return fi * fo


# ----------------------------------------------------------------- fonts
FONT_FAMILY = "Inter"
DISPLAY_FAMILY = "Inter Display"


@lru_cache(maxsize=None)
def typeface(weight: int = 400, display: bool = False, italic: bool = False) -> skia.Typeface:
    fam = DISPLAY_FAMILY if display else FONT_FAMILY
    slant = skia.FontStyle.kItalic_Slant if italic else skia.FontStyle.kUpright_Slant
    return skia.Typeface(fam, skia.FontStyle(weight, skia.FontStyle.kNormal_Width, slant))


@lru_cache(maxsize=None)
def font(size: float, weight: int = 400, display: bool = False, italic: bool = False) -> skia.Font:
    f = skia.Font(typeface(weight, display, italic), size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
    f.setHinting(skia.FontHinting.kNone)
    f.setLinearMetrics(True)
    return f


def text_width(s: str, f: skia.Font, tracking: float = 0.0) -> float:
    return f.measureText(s) + tracking * max(0, len(s) - 1)


def paint(color, alpha=1.0, stroke=None, aa=True, blur=None, blend=None, cap=None, join=None) -> skia.Paint:
    p = skia.Paint(AntiAlias=aa)
    p.setColor(with_alpha(color, alpha) if alpha < 1.0 else color)
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(cap if cap is not None else skia.Paint.kRound_Cap)
        p.setStrokeJoin(join if join is not None else skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend is not None:
        p.setBlendMode(blend)
    return p


def draw_text(c: skia.Canvas, s: str, x: float, y: float, size: float = 30, color=C.text,
              weight: int = 400, alpha: float = 1.0, align: str = "left", display: bool = False,
              tracking: float = 0.0, italic: bool = False, shadow: bool = False) -> float:
    """Draw single-line text with baseline at y. Returns width."""
    if alpha <= 0.002 or not s:
        return 0.0
    f = font(size, weight, display, italic)
    w = text_width(s, f, tracking)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    p = paint(color, alpha)
    if shadow:
        sp = paint(C.black, 0.55 * alpha, blur=size * 0.12)
        _draw_str(c, s, x + 1, y + 2, f, sp, tracking)
    _draw_str(c, s, x, y, f, p, tracking)
    return w


def _draw_str(c, s, x, y, f, p, tracking):
    if tracking == 0.0:
        c.drawString(s, x, y, f, p)
    else:
        cx = x
        for ch in s:
            c.drawString(ch, cx, y, f, p)
            cx += f.measureText(ch) + tracking


def wrap_lines(s: str, f: skia.Font, max_w: float) -> list[str]:
    out = []
    for para in s.split("\n"):
        words = para.split(" ")
        line = ""
        for w in words:
            cand = (line + " " + w).strip()
            if f.measureText(cand) <= max_w or not line:
                line = cand
            else:
                out.append(line)
                line = w
        out.append(line)
    return out


def draw_paragraph(c, s, x, y, max_w, size=30, color=C.text, weight=400, alpha=1.0, leading=1.38,
                   align="left", display=False, reveal: float | None = None, italic=False) -> float:
    """Wrapped text. y is the first baseline. reveal in [0,1] fades lines/words in.
    Returns total height."""
    f = font(size, weight, display, italic)
    lines = wrap_lines(s, f, max_w)
    lh = size * leading
    nwords = sum(len(l.split()) for l in lines)
    wi = 0
    for i, l in enumerate(lines):
        if reveal is None:
            draw_text(c, l, x if align == "left" else (x + max_w / 2 if align == "center" else x + max_w),
                      y + i * lh, size, color, weight, alpha, align, display, italic=italic)
        else:
            # word-by-word reveal
            words = l.split()
            lw = f.measureText(l)
            if align == "center":
                cx = x + (max_w - lw) / 2
            elif align == "right":
                cx = x + max_w - lw
            else:
                cx = x
            for w in words:
                k = clamp(reveal * (nwords + 4) - wi)
                a = ease_out(k)
                if a > 0:
                    c.save()
                    c.translate(0, (1 - a) * size * 0.35)
                    draw_text(c, w, cx, y + i * lh, size, color, weight, alpha * a, "left", display, italic=italic)
                    c.restore()
                cx += f.measureText(w + " ")
                wi += 1
    return len(lines) * lh


def rrect(x, y, w, h, r) -> skia.RRect:
    return skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)


def draw_panel(c, x, y, w, h, alpha=1.0, r=18, fill=None, border=None, glow=None):
    if alpha <= 0:
        return
    fill = C.panel if fill is None else fill
    if glow is not None:
        c.drawRRect(rrect(x, y, w, h, r), paint(glow, 0.35 * alpha, blur=24))
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear(
        [skia.Point(x, y), skia.Point(x, y + h)],
        [with_alpha(mix(fill, C.white, 0.04), 0.92 * alpha), with_alpha(fill, 0.92 * alpha)]))
    c.drawRRect(rrect(x, y, w, h, r), p)
    c.drawRRect(rrect(x + 0.5, y + 0.5, w - 1, h - 1, r), paint(border if border is not None else C.line, 0.8 * alpha, stroke=1.2))


def glow_path(c, path: skia.Path, color, width=4, alpha=1.0, glow=14, core_color=None):
    if alpha <= 0:
        return
    c.drawPath(path, paint(color, 0.55 * alpha, stroke=width * 2.6, blur=glow))
    c.drawPath(path, paint(color, alpha, stroke=width))
    if core_color is not None:
        c.drawPath(path, paint(core_color, 0.9 * alpha, stroke=max(1.0, width * 0.35)))


def trim_path(path: skia.Path, t0: float, t1: float) -> skia.Path:
    """Sub-path from fraction t0 to t1 of total length (all contours)."""
    t0, t1 = clamp(t0), clamp(t1)
    out = skia.Path()
    if t1 <= t0:
        return out
    pm = skia.PathMeasure(path, False)
    lengths = []
    while True:
        lengths.append(pm.getLength())
        if not pm.nextContour():
            break
    total = sum(lengths)
    if total <= 0:
        return out
    a, b = t0 * total, t1 * total
    pm = skia.PathMeasure(path, False)
    acc = 0.0
    for L in lengths:
        s_, e_ = max(a - acc, 0), min(b - acc, L)
        if e_ > s_:
            pm.getSegment(s_, e_, out, True)
        acc += L
        if not pm.nextContour():
            break
    return out


def path_length(path: skia.Path) -> float:
    pm = skia.PathMeasure(path, False)
    total = 0.0
    while True:
        total += pm.getLength()
        if not pm.nextContour():
            break
    return total


def path_point(path: skia.Path, t: float):
    pm = skia.PathMeasure(path, False)
    L = pm.getLength()
    pos, tan = pm.getPosTan(clamp(t) * L)
    return (pos.x(), pos.y()), (tan.x(), tan.y())


def poly(points, close=False) -> skia.Path:
    p = skia.Path()
    for i, (x, y) in enumerate(points):
        if i == 0:
            p.moveTo(x, y)
        else:
            p.lineTo(x, y)
    if close:
        p.close()
    return p


def arrow(c, x0, y0, x1, y1, color, width=3, alpha=1.0, head=14, glow=False):
    if alpha <= 0:
        return
    ang = math.atan2(y1 - y0, x1 - x0)
    bx, by = x1 - head * 0.8 * math.cos(ang), y1 - head * 0.8 * math.sin(ang)
    p = poly([(x0, y0), (bx, by)])
    if glow:
        c.drawPath(p, paint(color, 0.45 * alpha, stroke=width * 3, blur=8))
    c.drawPath(p, paint(color, alpha, stroke=width))
    hp = poly([(x1, y1),
               (x1 - head * math.cos(ang - 0.42), y1 - head * math.sin(ang - 0.42)),
               (x1 - head * math.cos(ang + 0.42), y1 - head * math.sin(ang + 0.42))], close=True)
    c.drawPath(hp, paint(color, alpha))


def dashed(c, path, color, width=2, on=8, off=8, phase=0.0, alpha=1.0):
    p = paint(color, alpha, stroke=width, cap=skia.Paint.kButt_Cap)
    p.setPathEffect(skia.DashPathEffect.Make([on, off], phase))
    c.drawPath(path, p)


def leader_label(c, x0, y0, x1, y1, text, color=C.text, size=24, alpha=1.0, align="left", weight=500,
                 line_color=None, dot=True, sub=None):
    """A label with a leader line from (x0,y0) (target) to (x1,y1) (label anchor)."""
    if alpha <= 0:
        return
    lc = line_color if line_color is not None else with_alpha(C.muted, 0.9)
    c.drawPath(poly([(x0, y0), (x1, y1)]), paint(lc, alpha, stroke=1.6))
    if dot:
        c.drawCircle(x0, y0, 4.5, paint(lc, alpha))
    tx = x1 + (10 if align == "left" else -10)
    draw_text(c, text, tx, y1 + size * 0.35, size, color, weight, alpha, align)
    if sub:
        draw_text(c, sub, tx, y1 + size * 0.35 + size * 1.05, size * 0.78, C.muted, 400, alpha, align)


def chip(c, x, y, text, color, alpha=1.0, size=22, filled=True, weight=600, pad=14, align="left"):
    f = font(size, weight)
    w = f.measureText(text) + pad * 2
    h = size * 1.6
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    if filled:
        c.drawRRect(rrect(x, y, w, h, h / 2), paint(color, 0.22 * alpha))
    c.drawRRect(rrect(x + 0.75, y + 0.75, w - 1.5, h - 1.5, h / 2), paint(color, 0.9 * alpha, stroke=1.5))
    draw_text(c, text, x + pad, y + h / 2 + size * 0.36, size, mix(color, C.white, 0.55), weight, alpha)
    return w


# ----------------------------------------------------------------- textures
def noise_image(w: int, h: int, fx: float, fy: float, octaves: int, seed: int, base: int, contrast: float = 0.5,
                turbulence: bool = False, tint: int | None = None) -> skia.Image:
    """Bake a coloured noise texture into an image (cheap to draw later)."""
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    c.clear(base)
    sh = (skia.PerlinNoiseShader.MakeTurbulence if turbulence else skia.PerlinNoiseShader.MakeFractalNoise)(
        fx, fy, octaves, seed)
    p = skia.Paint(Shader=sh)
    # convert noise to luminance-ish overlay
    p.setColorFilter(skia.ColorFilters.Matrix([
        0.33, 0.33, 0.33, 0, 0,
        0.33, 0.33, 0.33, 0, 0,
        0.33, 0.33, 0.33, 0, 0,
        0, 0, 0, 0, contrast,
    ]))
    p.setBlendMode(skia.BlendMode.kOverlay)
    c.drawRect(skia.Rect(0, 0, w, h), p)
    if tint is not None:
        c.drawRect(skia.Rect(0, 0, w, h), paint(tint, 0.15, blend=skia.BlendMode.kSoftLight))
    return surf.makeImageSnapshot()


def speckle_image(w, h, base, speck_colors, density=0.004, seed=1, size=(0.6, 1.8)) -> skia.Image:
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    c.clear(base)
    rnd = random.Random(seed)
    n = int(w * h * density)
    for _ in range(n):
        col = rnd.choice(speck_colors)
        c.drawCircle(rnd.random() * w, rnd.random() * h, rnd.uniform(*size), paint(col, rnd.uniform(0.35, 0.9)))
    return surf.makeImageSnapshot()


def image_shader(img: skia.Image, scale=1.0, dx=0.0, dy=0.0):
    m = skia.Matrix()
    m.setScaleTranslate(scale, scale, dx, dy)
    return img.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat,
                          skia.SamplingOptions(skia.FilterMode.kLinear), m)


# ----------------------------------------------------------------- background
_BG_CACHE = {}


def background(kind: str = "default") -> skia.Image:
    if kind in _BG_CACHE:
        return _BG_CACHE[kind]
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    p = skia.Paint()
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [C.bg1, C.bg0]))
    c.drawRect(skia.Rect(0, 0, W, H), p)
    # soft radial glows
    for (gx, gy, r, col, a) in [(W * 0.18, H * 0.1, 900, rgb("#1B3A66"), 0.55), (W * 0.9, H * 0.95, 800, rgb("#0F3B4A"), 0.4)]:
        rp = skia.Paint()
        rp.setShader(skia.GradientShader.MakeRadial(skia.Point(gx, gy), r, [with_alpha(col, a), with_alpha(col, 0)]))
        c.drawRect(skia.Rect(0, 0, W, H), rp)
    if kind == "grid":
        gp = paint(C.grid, 0.55, stroke=1)
        for x in range(0, W + 1, 60):
            c.drawLine(x, 0, x, H, gp)
        for y in range(0, H + 1, 60):
            c.drawLine(0, y, W, y, gp)
    if kind == "dots":
        dp = paint(C.grid, 0.9)
        for x in range(30, W, 40):
            for y in range(30, H, 40):
                c.drawCircle(x, y, 1.2, dp)
    # vignette
    vp = skia.Paint()
    vp.setShader(skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), W * 0.75,
                                                [with_alpha(C.black, 0), with_alpha(C.black, 0.55)], [0.55, 1.0]))
    c.drawRect(skia.Rect(0, 0, W, H), vp)
    img = surf.makeImageSnapshot()
    _BG_CACHE[kind] = img
    return img


# ----------------------------------------------------------------- particles
@dataclass
class Particle:
    x: float
    y: float
    r: float
    phase: float
    speed: float


def make_particles(n, x0, y0, x1, y1, rmin=1, rmax=3, seed=0, smin=0.2, smax=1.0):
    rnd = random.Random(seed)
    return [Particle(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(rmin, rmax), rnd.random() * 6.283,
                     rnd.uniform(smin, smax)) for _ in range(n)]


def seeded(seed):
    return random.Random(seed)
