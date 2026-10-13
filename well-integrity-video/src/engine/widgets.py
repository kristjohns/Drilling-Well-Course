"""Reusable visual components: icons, cards, lists, plots, gauges, waffles."""
from __future__ import annotations

import math

import numpy as np
import skia

from .core import (C, W, H, arrow, chip, clamp, draw_panel, draw_paragraph, draw_text, ease_in_out, ease_out,
                   ease_out_back, font, glow_path, lerp, mix, paint, poly, prog, rrect, trim_path, with_alpha, rgb,
                   wrap_lines)


# =============================================================== icons
# All icons are drawn centred on (x, y) inside a box of size s.
def _sp(color, a, s, w=None):
    return paint(color, a, stroke=(w if w is not None else max(2.0, s * 0.06)))


def icon(c, name, x, y, s=64, color=C.text, a=1.0, accent=None):
    if a <= 0.01:
        return
    accent = accent if accent is not None else C.primary
    f = ICONS.get(name)
    if f is None:
        c.drawCircle(x, y, s * 0.3, _sp(color, a, s))
        return
    c.save()
    c.translate(x, y)
    f(c, s, color, a, accent)
    c.restore()


def _i_valve(c, s, col, a, acc):
    h = s * 0.5
    bt = poly([(-h, -h * 0.55), (0, 0), (-h, h * 0.55)], close=True)
    bt2 = poly([(h, -h * 0.55), (0, 0), (h, h * 0.55)], close=True)
    c.drawPath(bt, _sp(col, a, s))
    c.drawPath(bt2, _sp(col, a, s))
    c.drawLine(0, 0, 0, -h * 0.9, _sp(col, a, s))
    c.drawLine(-h * 0.45, -h * 0.9, h * 0.45, -h * 0.9, _sp(acc, a, s))


def _i_gauge(c, s, col, a, acc):
    r = s * 0.42
    arc = skia.Path()
    arc.addArc(skia.Rect(-r, -r, r, r), 150, 240)
    c.drawPath(arc, _sp(col, a, s))
    ang = math.radians(-35)
    c.drawLine(0, 0, r * 0.75 * math.cos(ang), r * 0.75 * math.sin(ang), _sp(acc, a, s))
    c.drawCircle(0, 0, s * 0.05, paint(acc, a))


def _i_people(c, s, col, a, acc):
    for dx, sc, cc in ((-s * 0.2, 0.8, col), (s * 0.2, 0.8, col), (0, 1.0, acc)):
        c.drawCircle(dx, -s * 0.16 * sc, s * 0.11 * sc, _sp(cc, a, s))
        arc = skia.Path()
        arc.addArc(skia.Rect(dx - s * 0.2 * sc, s * 0.02, dx + s * 0.2 * sc, s * 0.42 * sc + s * 0.02), 180, 180)
        c.drawPath(arc, _sp(cc, a, s))


def _i_doc(c, s, col, a, acc):
    w, h = s * 0.62, s * 0.8
    p = poly([(-w / 2, -h / 2), (w / 2 - s * 0.16, -h / 2), (w / 2, -h / 2 + s * 0.16), (w / 2, h / 2), (-w / 2, h / 2)], close=True)
    c.drawPath(p, _sp(col, a, s))
    for k in range(3):
        yy = -h / 2 + s * 0.28 + k * s * 0.15
        c.drawLine(-w / 2 + s * 0.12, yy, w / 2 - s * 0.12, yy, _sp(acc if k == 0 else col, a, s, max(1.5, s * 0.04)))


def _i_check(c, s, col, a, acc):
    c.drawCircle(0, 0, s * 0.42, _sp(acc, a, s))
    c.drawPath(poly([(-s * 0.18, 0), (-s * 0.04, s * 0.14), (s * 0.2, -s * 0.14)]), _sp(acc, a, s, s * 0.08))


def _i_cross(c, s, col, a, acc):
    c.drawCircle(0, 0, s * 0.42, _sp(acc, a, s))
    d = s * 0.15
    c.drawLine(-d, -d, d, d, _sp(acc, a, s, s * 0.08))
    c.drawLine(-d, d, d, -d, _sp(acc, a, s, s * 0.08))


def _i_warning(c, s, col, a, acc):
    p = poly([(0, -s * 0.42), (s * 0.46, s * 0.36), (-s * 0.46, s * 0.36)], close=True)
    c.drawPath(p, _sp(acc, a, s))
    c.drawLine(0, -s * 0.12, 0, s * 0.1, _sp(acc, a, s, s * 0.07))
    c.drawCircle(0, s * 0.22, s * 0.04, paint(acc, a))


def _i_shield(c, s, col, a, acc):
    p = skia.Path()
    p.moveTo(0, -s * 0.44)
    p.lineTo(s * 0.36, -s * 0.3)
    p.quadTo(s * 0.36, s * 0.2, 0, s * 0.46)
    p.quadTo(-s * 0.36, s * 0.2, -s * 0.36, -s * 0.3)
    p.close()
    c.drawPath(p, _sp(col, a, s))
    c.drawPath(poly([(-s * 0.14, 0), (-s * 0.03, s * 0.12), (s * 0.16, -s * 0.12)]), _sp(acc, a, s, s * 0.07))


def _i_gear(c, s, col, a, acc):
    r1, r2 = s * 0.3, s * 0.42
    p = skia.Path()
    n = 8
    for k in range(n * 2):
        ang = k * math.pi / n
        r = r2 if k % 2 == 0 else r1
        x, y = r * math.cos(ang), r * math.sin(ang)
        (p.moveTo if k == 0 else p.lineTo)(x, y)
    p.close()
    c.drawPath(p, _sp(col, a, s))
    c.drawCircle(0, 0, s * 0.12, _sp(acc, a, s))


def _i_drop(c, s, col, a, acc):
    p = skia.Path()
    p.moveTo(0, -s * 0.42)
    p.cubicTo(s * 0.12, -s * 0.2, s * 0.32, -s * 0.02, s * 0.32, s * 0.14)
    p.cubicTo(s * 0.32, s * 0.34, s * 0.16, s * 0.44, 0, s * 0.44)
    p.cubicTo(-s * 0.16, s * 0.44, -s * 0.32, s * 0.34, -s * 0.32, s * 0.14)
    p.cubicTo(-s * 0.32, -s * 0.02, -s * 0.12, -s * 0.2, 0, -s * 0.42)
    c.drawPath(p, paint(acc, 0.25 * a))
    c.drawPath(p, _sp(acc, a, s))


def _i_cloud(c, s, col, a, acc):
    p = skia.Path()
    for (dx, dy, r) in ((-s * 0.18, s * 0.05, s * 0.18), (s * 0.02, -s * 0.08, s * 0.24), (s * 0.22, s * 0.06, s * 0.16)):
        p.addCircle(dx, dy, r)
    p.addRect(skia.Rect(-s * 0.36, s * 0.05, s * 0.38, s * 0.22))
    p2 = skia.Path()
    ok = skia.Op(p, p2, skia.PathOp.kUnion_PathOp) if False else None
    c.drawPath(p, paint(acc, 0.25 * a))
    c.drawPath(p, _sp(acc, a, s, s * 0.04))


def _i_clock(c, s, col, a, acc):
    c.drawCircle(0, 0, s * 0.42, _sp(col, a, s))
    c.drawLine(0, 0, 0, -s * 0.26, _sp(acc, a, s))
    c.drawLine(0, 0, s * 0.18, s * 0.08, _sp(acc, a, s))


def _i_thermo(c, s, col, a, acc):
    c.drawRoundRect(skia.Rect(-s * 0.08, -s * 0.42, s * 0.08, s * 0.18), s * 0.08, s * 0.08, _sp(col, a, s))
    c.drawCircle(0, s * 0.26, s * 0.15, paint(acc, a))
    c.drawLine(0, s * 0.2, 0, -s * 0.2, _sp(acc, a, s, s * 0.07))


def _i_network(c, s, col, a, acc):
    pts = [(-s * 0.32, -s * 0.2), (s * 0.3, -s * 0.28), (s * 0.05, s * 0.05), (-s * 0.25, s * 0.32), (s * 0.32, s * 0.3)]
    for i, j in ((0, 2), (1, 2), (2, 3), (2, 4), (0, 1)):
        c.drawLine(*pts[i], *pts[j], _sp(col, a, s, s * 0.04))
    for k, (x, y) in enumerate(pts):
        c.drawCircle(x, y, s * 0.08, paint(acc if k == 2 else col, a))


def _i_rig(c, s, col, a, acc):
    # semi-submersible
    c.drawRect(skia.Rect(-s * 0.42, s * 0.22, s * 0.42, s * 0.32), _sp(col, a, s))
    c.drawLine(-s * 0.3, s * 0.22, -s * 0.3, -s * 0.02, _sp(col, a, s))
    c.drawLine(s * 0.3, s * 0.22, s * 0.3, -s * 0.02, _sp(col, a, s))
    c.drawRect(skia.Rect(-s * 0.4, -s * 0.08, s * 0.4, s * 0.0), _sp(col, a, s))
    c.drawPath(poly([(-s * 0.1, -s * 0.08), (0, -s * 0.46), (s * 0.1, -s * 0.08)]), _sp(acc, a, s))


def _i_platform(c, s, col, a, acc):
    c.drawPath(poly([(-s * 0.3, s * 0.44), (-s * 0.18, -s * 0.02), (s * 0.18, -s * 0.02), (s * 0.3, s * 0.44)]), _sp(col, a, s))
    c.drawLine(-s * 0.24, s * 0.2, s * 0.24, s * 0.2, _sp(col, a, s, s * 0.035))
    c.drawRect(skia.Rect(-s * 0.36, -s * 0.16, s * 0.36, -s * 0.02), _sp(col, a, s))
    c.drawPath(poly([(s * 0.1, -s * 0.16), (s * 0.18, -s * 0.44), (s * 0.26, -s * 0.16)]), _sp(acc, a, s))


def _i_heli(c, s, col, a, acc):
    c.drawOval(skia.Rect(-s * 0.26, -s * 0.06, s * 0.14, s * 0.2), _sp(col, a, s))
    c.drawLine(s * 0.12, s * 0.06, s * 0.42, s * 0.02, _sp(col, a, s))
    c.drawLine(-s * 0.44, -s * 0.18, s * 0.36, -s * 0.18, _sp(acc, a, s))
    c.drawLine(-s * 0.06, -s * 0.18, -s * 0.06, -s * 0.06, _sp(col, a, s))
    c.drawLine(-s * 0.24, s * 0.3, s * 0.1, s * 0.3, _sp(col, a, s))


def _i_magnifier(c, s, col, a, acc):
    c.drawCircle(-s * 0.06, -s * 0.06, s * 0.28, _sp(col, a, s))
    c.drawLine(s * 0.14, s * 0.14, s * 0.4, s * 0.4, _sp(acc, a, s, s * 0.09))


def _i_chart(c, s, col, a, acc):
    c.drawPath(poly([(-s * 0.4, -s * 0.4), (-s * 0.4, s * 0.4), (s * 0.42, s * 0.4)]), _sp(col, a, s))
    c.drawPath(poly([(-s * 0.3, s * 0.2), (-s * 0.1, 0), (s * 0.08, s * 0.1), (s * 0.34, -s * 0.28)]), _sp(acc, a, s))


def _i_layers(c, s, col, a, acc):
    for k in range(3):
        y = -s * 0.22 + k * s * 0.2
        p = poly([(-s * 0.4, y), (0, y - s * 0.14), (s * 0.4, y), (0, y + s * 0.14)], close=True)
        c.drawPath(p, _sp(acc if k == 0 else col, a, s, s * 0.045))


def _i_flame(c, s, col, a, acc):
    p = skia.Path()
    p.moveTo(0, -s * 0.44)
    p.cubicTo(s * 0.3, -s * 0.1, s * 0.34, s * 0.2, 0, s * 0.42)
    p.cubicTo(-s * 0.34, s * 0.2, -s * 0.22, -s * 0.06, -s * 0.06, -s * 0.12)
    p.cubicTo(-s * 0.04, -s * 0.24, 0, -s * 0.34, 0, -s * 0.44)
    c.drawPath(p, paint(acc, 0.3 * a))
    c.drawPath(p, _sp(acc, a, s))


def _i_infinity(c, s, col, a, acc):
    p = skia.Path()
    r = s * 0.2
    p.moveTo(0, 0)
    p.cubicTo(s * 0.12, -r * 1.3, s * 0.46, -r * 1.3, s * 0.46, 0)
    p.cubicTo(s * 0.46, r * 1.3, s * 0.12, r * 1.3, 0, 0)
    p.cubicTo(-s * 0.12, -r * 1.3, -s * 0.46, -r * 1.3, -s * 0.46, 0)
    p.cubicTo(-s * 0.46, r * 1.3, -s * 0.12, r * 1.3, 0, 0)
    c.drawPath(p, _sp(acc, a, s))


def _i_book(c, s, col, a, acc):
    c.drawPath(poly([(0, -s * 0.3), (-s * 0.42, -s * 0.36), (-s * 0.42, s * 0.34), (0, s * 0.4), (s * 0.42, s * 0.34),
                     (s * 0.42, -s * 0.36)], close=True), _sp(col, a, s))
    c.drawLine(0, -s * 0.3, 0, s * 0.4, _sp(acc, a, s))


def _i_wave(c, s, col, a, acc):
    p = skia.Path()
    p.moveTo(-s * 0.44, 0)
    for k in range(4):
        x0 = -s * 0.44 + k * s * 0.22
        p.quadTo(x0 + s * 0.055, -s * 0.18 if k % 2 == 0 else s * 0.18, x0 + s * 0.11, 0)
        p.quadTo(x0 + s * 0.165, s * 0.18 if k % 2 == 0 else -s * 0.18, x0 + s * 0.22, 0)
    c.drawPath(p, _sp(acc, a, s))


def _i_ship(c, s, col, a, acc):
    c.drawPath(poly([(-s * 0.44, s * 0.04), (s * 0.44, s * 0.04), (s * 0.32, s * 0.28), (-s * 0.38, s * 0.28)], close=True), _sp(col, a, s))
    for k in range(3):
        c.drawCircle(-s * 0.2 + k * s * 0.2, -s * 0.08, s * 0.1, _sp(acc, a, s))


def _i_cpu(c, s, col, a, acc):
    c.drawRoundRect(skia.Rect(-s * 0.28, -s * 0.28, s * 0.28, s * 0.28), s * 0.06, s * 0.06, _sp(col, a, s))
    c.drawRect(skia.Rect(-s * 0.12, -s * 0.12, s * 0.12, s * 0.12), paint(acc, a))
    for k in range(-1, 2):
        for (x0, y0, x1, y1) in ((k * s * 0.14, -s * 0.28, k * s * 0.14, -s * 0.42), (k * s * 0.14, s * 0.28, k * s * 0.14, s * 0.42),
                                 (-s * 0.28, k * s * 0.14, -s * 0.42, k * s * 0.14), (s * 0.28, k * s * 0.14, s * 0.42, k * s * 0.14)):
            c.drawLine(x0, y0, x1, y1, _sp(col, a, s, s * 0.04))


def _i_lock(c, s, col, a, acc):
    c.drawRoundRect(skia.Rect(-s * 0.3, -s * 0.04, s * 0.3, s * 0.4), s * 0.06, s * 0.06, _sp(col, a, s))
    arc = skia.Path()
    arc.addArc(skia.Rect(-s * 0.2, -s * 0.38, s * 0.2, s * 0.06), 180, 180)
    c.drawPath(arc, _sp(acc, a, s))
    c.drawLine(-s * 0.2, -s * 0.16, -s * 0.2, -s * 0.04, _sp(acc, a, s))
    c.drawLine(s * 0.2, -s * 0.16, s * 0.2, -s * 0.04, _sp(acc, a, s))


ICONS = dict(valve=_i_valve, gauge=_i_gauge, people=_i_people, doc=_i_doc, check=_i_check, cross=_i_cross,
             warning=_i_warning, shield=_i_shield, gear=_i_gear, drop=_i_drop, cloud=_i_cloud, clock=_i_clock,
             thermo=_i_thermo, network=_i_network, rig=_i_rig, platform=_i_platform, heli=_i_heli,
             magnifier=_i_magnifier, chart=_i_chart, layers=_i_layers, flame=_i_flame, infinity=_i_infinity,
             book=_i_book, wave=_i_wave, ship=_i_ship, cpu=_i_cpu, lock=_i_lock)


# =============================================================== cards and lists
def icon_card(c, x, y, w, h, title, body, icon_name, t_in, t, accent=C.primary, size_title=34, size_body=24,
              alpha=1.0):
    k = ease_out(clamp((t - t_in) / 0.8))
    a = k * alpha
    if a <= 0.01:
        return
    c.save()
    c.translate(0, (1 - k) * 40)
    draw_panel(c, x, y, w, h, a, glow=accent if k > 0.5 else None)
    c.drawRect(skia.Rect(x, y + 18, x + 4, y + h - 18), paint(accent, a))
    icon(c, icon_name, x + 64, y + 70, 70, C.text, a, accent)
    draw_text(c, title, x + 120, y + 62, size_title, C.text, 600, a, display=True)
    draw_paragraph(c, body, x + 120, y + 104, w - 150, size_body, C.muted, 400, a, leading=1.35)
    c.restore()


def bullets(c, items, x, y, t, times, size=30, color=C.text, gap=1.65, max_w=760, accent=C.primary, alpha=1.0,
            bullet="dot", dim_after=None):
    """items: list of str; times: appear time per item."""
    yy = y
    for i, (it, ti) in enumerate(zip(items, times)):
        k = ease_out(clamp((t - ti) / 0.7))
        a = k * alpha
        if dim_after is not None and i < len(items) - 1 and t > times[min(i + 1, len(times) - 1)] + 0.5:
            a *= dim_after
        if a > 0.01:
            c.save()
            c.translate((1 - k) * 30, 0)
            if bullet == "dot":
                c.drawCircle(x + 8, yy - size * 0.33, 6, paint(accent, a))
            elif bullet == "num":
                draw_text(c, f"{i + 1}", x + 8, yy, size * 0.8, accent, 700, a, "center")
            h = draw_paragraph(c, it, x + 34, yy, max_w, size, color, 400, a, leading=1.32)
            c.restore()
        else:
            f = font(size, 400)
            h = len(wrap_lines(it, f, max_w)) * size * 1.32
        yy += max(h, size * 1.32) + size * (gap - 1.32)
    return yy


def quote_block(c, text, x, y, w, t, t0, t1, size=40, color=C.text, highlights=(), alpha=1.0, src=None):
    """Word-by-word reveal over [t0, t1]; highlighted words get accent colour."""
    f = font(size, 500, True)
    lines = wrap_lines(text, f, w)
    total = sum(len(l.split()) for l in lines)
    r = clamp((t - t0) / max(0.1, t1 - t0))
    wi = 0
    lh = size * 1.3
    for i, l in enumerate(lines):
        cx = x
        for wd in l.split():
            k = ease_out(clamp(r * (total + 3) - wi))
            a = k * alpha
            core = wd.strip(",.;:").lower()
            col = color
            for hl, hc in highlights:
                if core in hl:
                    col = mix(color, hc, k)
            if a > 0.01:
                draw_text(c, wd, cx, y + i * lh + (1 - k) * 8, size, col, 500, a, display=True)
            cx += f.measureText(wd + " ")
            wi += 1
    if src:
        draw_text(c, src, x, y + len(lines) * lh + 24, 22, C.muted, 500, alpha * ease_out(clamp(r * 1.5)))
    return len(lines) * lh


# =============================================================== plots
class Plot:
    def __init__(self, x, y, w, h, xr, yr, invert_y=False, xlabel="", ylabel="", xticks=None, yticks=None,
                 xfmt="{:g}", yfmt="{:g}"):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.xr, self.yr = xr, yr
        self.inv = invert_y
        self.xlabel, self.ylabel = xlabel, ylabel
        self.xticks, self.yticks = xticks, yticks
        self.xfmt, self.yfmt = xfmt, yfmt

    def px(self, xv):
        return self.x + (xv - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def py(self, yv):
        f = (yv - self.yr[0]) / (self.yr[1] - self.yr[0])
        return self.y + (f * self.h if self.inv else (1 - f) * self.h)

    def axes(self, c, a=1.0, grid=True, label_size=20, tick_size=16):
        if a <= 0:
            return
        if grid:
            gp = paint(C.grid, 0.9 * a, stroke=1)
            for xv in (self.xticks or []):
                c.drawLine(self.px(xv), self.y, self.px(xv), self.y + self.h, gp)
            for yv in (self.yticks or []):
                c.drawLine(self.x, self.py(yv), self.x + self.w, self.py(yv), gp)
        ap = paint(C.muted, 0.8 * a, stroke=1.6)
        c.drawLine(self.x, self.y, self.x, self.y + self.h, ap)
        if self.inv:
            c.drawLine(self.x, self.y, self.x + self.w, self.y, ap)
        else:
            c.drawLine(self.x, self.y + self.h, self.x + self.w, self.y + self.h, ap)
        for xv in (self.xticks or []):
            ty = (self.y - 10) if self.inv else (self.y + self.h + 24)
            draw_text(c, self.xfmt.format(xv), self.px(xv), ty, tick_size, C.muted, 500, a, "center")
        for yv in (self.yticks or []):
            draw_text(c, self.yfmt.format(yv), self.x - 10, self.py(yv) + 5, tick_size, C.muted, 500, a, "right")
        if self.xlabel:
            ly = (self.y - 40) if self.inv else (self.y + self.h + 56)
            draw_text(c, self.xlabel, self.x + self.w / 2, ly, label_size, C.text, 600, a, "center")
        if self.ylabel:
            c.save()
            c.translate(self.x - 70, self.y + self.h / 2)
            c.rotate(-90)
            draw_text(c, self.ylabel, 0, 0, label_size, C.text, 600, a, "center")
            c.restore()

    def path(self, xs, ys) -> skia.Path:
        return poly([(self.px(a), self.py(b)) for a, b in zip(xs, ys)])

    def line(self, c, xs, ys, color, width=3.5, a=1.0, reveal=1.0, glow=True, dash=None):
        if a <= 0 or reveal <= 0:
            return
        p = self.path(xs, ys)
        if reveal < 1.0:
            p = trim_path(p, 0, reveal)
        if dash:
            pp = paint(color, a, stroke=width, cap=skia.Paint.kButt_Cap)
            pp.setPathEffect(skia.DashPathEffect.Make(dash, 0))
            c.drawPath(p, pp)
        elif glow:
            glow_path(c, p, color, width, a, glow=10)
        else:
            c.drawPath(p, paint(color, a, stroke=width))

    def clip(self, c):
        c.clipRect(skia.Rect(self.x, self.y - 2, self.x + self.w, self.y + self.h + 2))


# =============================================================== gauges
def gauge(c, x, y, r, value, vmin, vmax, label="", unit="bar", a=1.0, zones=None, color=C.primary, fmt="{:.0f}"):
    if a <= 0:
        return
    start, sweep = 135, 270
    c.drawCircle(x, y, r + 10, paint(C.panel, 0.95 * a))
    c.drawCircle(x, y, r + 10, paint(C.line, a, stroke=2))
    rect = skia.Rect(x - r, y - r, x + r, y + r)
    track = skia.Path()
    track.addArc(rect, start, sweep)
    c.drawPath(track, paint(C.grid, a, stroke=8, cap=skia.Paint.kButt_Cap))
    if zones:
        for (z0, z1, zc) in zones:
            zp = skia.Path()
            zp.addArc(rect, start + sweep * (z0 - vmin) / (vmax - vmin), sweep * (z1 - z0) / (vmax - vmin))
            c.drawPath(zp, paint(zc, 0.85 * a, stroke=8, cap=skia.Paint.kButt_Cap))
    f = clamp((value - vmin) / (vmax - vmin))
    val = skia.Path()
    val.addArc(skia.Rect(x - r + 14, y - r + 14, x + r - 14, y + r - 14), start, sweep * f)
    c.drawPath(val, paint(color, 0.9 * a, stroke=5))
    ang = math.radians(start + sweep * f)
    c.drawLine(x, y, x + (r - 18) * math.cos(ang), y + (r - 18) * math.sin(ang), paint(C.text, a, stroke=3))
    c.drawCircle(x, y, 6, paint(C.text, a))
    draw_text(c, fmt.format(value), x, y + r * 0.55, r * 0.34, C.text, 700, a, "center")
    draw_text(c, unit, x, y + r * 0.55 + r * 0.24, r * 0.16, C.muted, 500, a, "center")
    if label:
        draw_text(c, label, x, y + r + 40, 20, C.text, 600, a, "center")


# =============================================================== waffle
def waffle(c, x, y, n, cols, cell, gap, colors, reveal=1.0, a=1.0, round_=True):
    """colors: list of colour per cell index (len >= n)."""
    shown = int(n * clamp(reveal))
    for i in range(n):
        r, k = divmod(i, cols)
        cx = x + k * (cell + gap)
        cy = y + r * (cell + gap)
        if i < shown:
            col = colors[i]
            if round_:
                c.drawCircle(cx + cell / 2, cy + cell / 2, cell / 2, paint(col, a))
            else:
                c.drawRect(skia.Rect(cx, cy, cx + cell, cy + cell), paint(col, a))
        else:
            c.drawCircle(cx + cell / 2, cy + cell / 2, cell / 2, paint(C.grid, 0.6 * a))


def counter(c, value, x, y, size, color=C.text, a=1.0, fmt="{:,.0f}", align="center", weight=700, suffix=""):
    s = fmt.format(value).replace(",", " ") + suffix
    draw_text(c, s, x, y, size, color, weight, a, align, display=True)


def stamp(c, x, y, text, color, k, size=36):
    """A stamped label that pops in (k in 0..1)."""
    if k <= 0:
        return
    s = ease_out_back(k)
    c.save()
    c.translate(x, y)
    c.rotate(-8)
    c.scale(0.6 + 0.4 * s, 0.6 + 0.4 * s)
    f = font(size, 800)
    w = f.measureText(text) + 40
    h = size * 1.6
    c.drawRoundRect(skia.Rect(-w / 2, -h / 2, w / 2, h / 2), 10, 10, paint(color, k, stroke=4))
    draw_text(c, text, 0, size * 0.36, size, color, 800, k, "center", tracking=3)
    c.restore()
