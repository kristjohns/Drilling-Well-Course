"""Styled drawing primitives for procedural callbacks (fn(canvas, t, look) registered with Stage.procedural).

The canvas is already in world coordinates (y up), so everything here takes world units. The look matches the role-based
styling of ordinary Stage objects: brushed steel gradients, soft flat fills with a hairline edge, rubber, glows.
Use these for mechanisms whose parts move along computed paths (linkages, valves, tools), where keyframing every part
would be clumsy.
"""
from __future__ import annotations
import math

import skia

from . import palette as P
from .look import col, lighten, darken
from .stage import hex_rgb


def _rgb(c):
    return hex_rgb(c) if isinstance(c, str) else c


def _paint(color, a=1.0, stroke=None, cap=None):
    p = skia.Paint(Color=col(_rgb(color), a), AntiAlias=True)
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeJoin(skia.Paint.kRound_Join)
        p.setStrokeCap(cap or skia.Paint.kRound_Cap)
    return p


def _path(pts, closed=True):
    path = skia.Path()
    path.moveTo(*pts[0])
    for q in pts[1:]:
        path.lineTo(*q)
    if closed:
        path.close()
    return path


# ---------------------------------------------------------------------------------------------- fills
def steel(c, x0, y0, x1, y1, color=P.STEEL, a=1.0, axis=None):
    """Brushed-steel rectangle; the gradient runs across the short axis (or axis='x' / 'y')."""
    if a <= 0.003:
        return
    xa, xb, ya, yb = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    if xb - xa <= 0 or yb - ya <= 0:
        return
    rgb = _rgb(color)
    axis = axis or ("x" if (xb - xa) < (yb - ya) else "y")
    pts = [skia.Point(xa, 0), skia.Point(xb, 0)] if axis == "x" else [skia.Point(0, ya), skia.Point(0, yb)]
    g = skia.GradientShader.MakeLinear(pts, [col(darken(rgb, 0.38), a), col(lighten(rgb, 0.30), a), col(rgb, a),
                                             col(darken(rgb, 0.10), a), col(darken(rgb, 0.42), a)], [0.0, 0.26, 0.5, 0.78, 1.0])
    c.drawRect(skia.Rect(xa, ya, xb, yb), skia.Paint(Shader=g, AntiAlias=True))


def steel_poly(c, pts, color=P.STEEL, a=1.0, axis="x"):
    """Polygon with the steel gradient across its bounding box (axis 'x' = left to right)."""
    if a <= 0.003:
        return
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    rgb = _rgb(color)
    if axis == "x":
        g_pts = [skia.Point(min(xs), 0), skia.Point(max(xs), 0)]
    else:
        g_pts = [skia.Point(0, min(ys)), skia.Point(0, max(ys))]
    g = skia.GradientShader.MakeLinear(g_pts, [col(darken(rgb, 0.38), a), col(lighten(rgb, 0.30), a), col(rgb, a),
                                               col(darken(rgb, 0.10), a), col(darken(rgb, 0.42), a)], [0.0, 0.26, 0.5, 0.78, 1.0])
    c.drawPath(_path(pts), skia.Paint(Shader=g, AntiAlias=True))


def flat(c, x0, y0, x1, y1, color, a=1.0, r=0.0, edge=True, px=0.004):
    """Soft top-lit fill with a hairline edge (the 'flat' role)."""
    if a <= 0.003:
        return
    xa, xb, ya, yb = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    if xb - xa <= 0 or yb - ya <= 0:
        return
    rgb = _rgb(color)
    rect = skia.Rect(xa, ya, xb, yb)
    g = skia.GradientShader.MakeLinear([skia.Point(0, ya), skia.Point(0, yb)], [col(darken(rgb, 0.10), a), col(lighten(rgb, 0.08), a)])
    rr = skia.RRect.MakeRectXY(rect, r, r)
    c.drawRRect(rr, skia.Paint(Shader=g, AntiAlias=True))
    if edge:
        c.drawRRect(rr, _paint(darken(rgb, 0.45), 0.55 * a, stroke=px))


def fill(c, x0, y0, x1, y1, color, a=1.0):
    if a <= 0.003:
        return
    c.drawRect(skia.Rect(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)), _paint(color, a))


def poly(c, pts, color, a=1.0):
    if a <= 0.003:
        return
    c.drawPath(_path(pts), _paint(color, a))


def gradient_rect_v(c, x0, y0, x1, y1, color_bottom, color_top, a=1.0):
    """Vertical colour ramp (fluids, gas columns)."""
    if a <= 0.003:
        return
    ya, yb = min(y0, y1), max(y0, y1)
    g = skia.GradientShader.MakeLinear([skia.Point(0, ya), skia.Point(0, yb)], [col(_rgb(color_bottom), a), col(_rgb(color_top), a)])
    c.drawRect(skia.Rect(min(x0, x1), ya, max(x0, x1), yb), skia.Paint(Shader=g, AntiAlias=True))


def fluid(c, x0, y0, x1, y1, color, a=1.0):
    """A liquid fill with a soft vertical sheen (the 'fluid' role, for narrow columns)."""
    if a <= 0.003:
        return
    rgb = _rgb(color)
    xa, xb = min(x0, x1), max(x0, x1)
    g = skia.GradientShader.MakeLinear([skia.Point(xa, 0), skia.Point(xb, 0)],
                                       [col(darken(rgb, 0.16), a), col(lighten(rgb, 0.10), a), col(rgb, a), col(darken(rgb, 0.16), a)],
                                       [0.0, 0.35, 0.6, 1.0])
    c.drawRect(skia.Rect(xa, min(y0, y1), xb, max(y0, y1)), skia.Paint(Shader=g, AntiAlias=True))


# ---------------------------------------------------------------------------------------------- strokes and dots
def stroke(c, pts, color, w, a=1.0, closed=False, butt=False):
    if a <= 0.003 or len(pts) < 2:
        return
    c.drawPath(_path(pts, closed), _paint(color, a, stroke=w, cap=skia.Paint.kButt_Cap if butt else None))


def dashed(c, p0, p1, color, w, a=1.0, dash=0.12, gap=0.09):
    if a <= 0.003:
        return
    x0, y0 = p0
    x1, y1 = p1
    L = math.hypot(x1 - x0, y1 - y0)
    if L <= 0:
        return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    s = 0.0
    while s < L:
        e = min(s + dash, L)
        stroke(c, [(x0 + ux * s, y0 + uy * s), (x0 + ux * e, y0 + uy * e)], color, w, a, butt=True)
        s = e + gap


def disc(c, x, y, r, color, a=1.0):
    if a <= 0.003:
        return
    c.drawCircle(x, y, r, _paint(color, a))


def ring(c, x, y, r, w, color, a=1.0):
    if a <= 0.003:
        return
    c.drawCircle(x, y, r, _paint(color, a, stroke=w))


def glow(c, look, x, y, r, color, a=1.0):
    """Soft blurred halo (an impact, a highlight)."""
    if a <= 0.003:
        return
    p = _paint(color, a)
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(r * look.k * 0.6, 1.0), False))
    c.drawCircle(x, y, r, p)


def flash(c, look, x, y, r, color, f):
    """Impact flash for a 0..1 phase f: a bright core and an expanding ring that fade out."""
    if f <= 0.0 or f >= 1.0:
        return
    a = (1.0 - f) ** 1.5
    glow(c, look, x, y, r * (0.6 + 0.6 * f), color, 0.8 * a)
    ring(c, x, y, r * (0.4 + 1.6 * f), r * 0.12 * (1.0 - f) + 0.01, color, a)
    disc(c, x, y, r * 0.22 * (1.0 - f), "#ffffff", a)


def text(c, look, s, x, y, size, color=P.TEXT, a=1.0, align="c", kind="sans"):
    if a <= 0.003:
        return
    look.draw_text(c, s, x, y, size, color, a, align=align, kind=kind)


def pill(c, look, s, x, y, size, bg, fg=P.BG, a=1.0, align="c", kind="bold"):
    """A label plate drawn procedurally (matches kit.tag)."""
    if a <= 0.003:
        return
    from .look import measure
    w = measure(s, size, kind) + 0.36
    h = size * 1.75
    x0 = {"c": x - w / 2, "l": x, "r": x - w}[align]
    rect = skia.Rect(x0, y - h / 2, x0 + w, y + h / 2)
    rgb = _rgb(bg)
    g = skia.GradientShader.MakeLinear([skia.Point(0, y - h / 2), skia.Point(0, y + h / 2)], [col(darken(rgb, 0.05), a), col(lighten(rgb, 0.08), a)])
    c.drawRRect(skia.RRect.MakeRectXY(rect, h / 2, h / 2), skia.Paint(Shader=g, AntiAlias=True))
    text(c, look, s, x0 + w / 2, y, size, fg, a, "c", kind)


# ---------------------------------------------------------------------------------------------- mechanical details
def rubber_stack(c, x0, x1, y0, y1, n=3, a=1.0):
    """A packing (chevron) stack: dark elastomer rings with light chevron edges, between x0..x1, y0..y1."""
    if a <= 0.003:
        return
    xa, xb, ya, yb = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    fill(c, xa, ya, xb, yb, P.RUBBER, a)
    h = (yb - ya) / n
    w = xb - xa
    for i in range(n):
        yy = ya + h * (i + 0.5)
        stroke(c, [(xa + 0.08 * w, yy - 0.28 * h), (xa + 0.5 * w, yy + 0.22 * h), (xb - 0.08 * w, yy - 0.28 * h)], P.RUBBER_HI, max(0.12 * h, 0.006), 0.8 * a)


def zigzag(c, x0, x1, y0, y1, n, color, w, a=1.0):
    """Zig-zag between x0 and x1 going from y0 to y1 with n teeth (springs, bellows convolutions)."""
    if a <= 0.003 or n < 1:
        return
    pts = [(x0 if i % 2 == 0 else x1, y0 + (y1 - y0) * i / (2 * n)) for i in range(2 * n + 1)]
    stroke(c, pts, color, w, a)


def bellows(c, xc, y0, y1, w, n, color=P.STEEL, a=1.0):
    """Convoluted metal bellows centred on xc from y0 to y1 (both walls zig-zag)."""
    if a <= 0.003:
        return
    ya, yb = min(y0, y1), max(y0, y1)
    pitch = (yb - ya) / max(n, 1)
    lw = max(pitch * 0.18, 0.006)
    left = [(xc - w / 2 + (0.0 if i % 2 == 0 else w * 0.12), ya + pitch * i / 2) for i in range(2 * n + 1)]
    right = [(xc + w / 2 - (0.0 if i % 2 == 0 else w * 0.12), ya + pitch * i / 2) for i in range(2 * n + 1)]
    body = left + right[::-1]
    poly(c, body, darken(_rgb(color), 0.25), 0.55 * a)
    stroke(c, left, lighten(_rgb(color), 0.2), lw, a)
    stroke(c, right, lighten(_rgb(color), 0.2), lw, a)
    for i in range(0, 2 * n + 1, 2):
        stroke(c, [left[i], right[i]], color, lw * 0.7, 0.6 * a)


def hatch(c, x0, y0, x1, y1, color, a=1.0, spacing=0.07, w=0.012):
    """Diagonal hatching clipped to a rectangle (cut steel, shared barrier elements)."""
    if a <= 0.003:
        return
    xa, xb, ya, yb = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    c.save()
    c.clipRect(skia.Rect(xa, ya, xb, yb))
    k = xa - (yb - ya)
    while k < xb:
        stroke(c, [(k, ya), (k + (yb - ya), yb)], color, w, a, butt=True)
        k += spacing
    c.restore()


def arrow(c, x0, y0, x1, y1, color, w=0.05, head=0.18, a=1.0):
    if a <= 0.003:
        return
    L = math.hypot(x1 - x0, y1 - y0)
    if L <= 1e-6:
        return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    bx, by = x1 - ux * head, y1 - uy * head
    stroke(c, [(x0, y0), (bx, by)], color, w, a, butt=True)
    nx, ny = -uy, ux
    poly(c, [(x1, y1), (bx + nx * head * 0.55, by + ny * head * 0.55), (bx - nx * head * 0.55, by - ny * head * 0.55)], color, a)


# ---------------------------------------------------------------------------------------------- timing helpers
def ramp(t, t0, t1):
    """0 before t0, 1 after t1, smooth (ease in-out) between."""
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    f = min(max((t - t0) / (t1 - t0), 0.0), 1.0)
    return f * f * (3 - 2 * f)


def lin(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return min(max((t - t0) / (t1 - t0), 0.0), 1.0)


def vis(t, t_in, t_out=None, d=0.4):
    """Opacity for something that fades in at t_in and (optionally) out at t_out."""
    a = lin(t, t_in, t_in + d)
    if t_out is not None:
        a *= 1.0 - lin(t, t_out, t_out + d)
    return a


def keys(t, pts):
    """Piecewise smooth interpolation through [(t, value), ...] (values may be numbers or tuples)."""
    if t <= pts[0][0]:
        return pts[0][1]
    for (ta, va), (tb, vb) in zip(pts[:-1], pts[1:]):
        if t <= tb:
            f = ramp(t, ta, tb)
            if isinstance(va, tuple):
                return tuple(a + (b - a) * f for a, b in zip(va, vb))
            return va + (vb - va) * f
    return pts[-1][1]


def keys_lin(t, pts):
    """Like keys() but linear between the points (constant-speed motion)."""
    if t <= pts[0][0]:
        return pts[0][1]
    for (ta, va), (tb, vb) in zip(pts[:-1], pts[1:]):
        if t <= tb:
            f = lin(t, ta, tb)
            if isinstance(va, tuple):
                return tuple(a + (b - a) * f for a, b in zip(va, vb))
            return va + (vb - va) * f
    return pts[-1][1]
