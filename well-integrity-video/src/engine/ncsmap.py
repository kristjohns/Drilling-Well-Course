"""Schematic map of the North Sea / Norwegian Continental Shelf (approximate coastline)."""
from __future__ import annotations

import math

import skia

from .core import C, draw_text, paint, poly, rgb, with_alpha, mix

NORWAY = [
    (11.15, 59.0), (10.95, 59.2), (10.6, 59.35), (10.25, 59.05), (10.0, 59.03), (9.4, 58.85), (8.77, 58.46),
    (8.0, 58.15), (7.45, 58.02), (7.05, 57.98), (6.6, 58.12), (6.3, 58.3), (5.95, 58.45), (5.55, 58.75),
    (5.6, 58.97), (5.85, 59.2), (5.25, 59.2), (5.2, 59.4), (5.15, 59.75), (5.0, 60.05), (4.95, 60.35),
    (4.75, 60.78), (4.95, 61.05), (5.0, 61.6), (5.1, 62.0), (5.15, 62.2), (5.9, 62.4), (6.1, 62.47),
    (6.9, 62.85), (7.7, 63.1), (8.4, 63.4), (8.6, 63.6), (9.6, 63.75), (10.2, 64.1), (10.7, 64.5),
    (11.2, 64.86), (12.2, 65.47), (12.6, 66.0), (13.0, 66.5), (13.6, 67.0), (14.4, 67.28), (15.0, 67.8),
    (16.0, 68.4), (17.5, 69.0), (18.95, 69.65), (20.5, 70.1), (22.0, 70.4), (23.68, 70.66), (25.78, 71.17),
    (27.5, 71.0), (29.0, 70.7), (31.1, 70.37), (30.05, 69.73), (28.5, 69.0), (25.0, 68.6), (20.0, 68.5),
    (18.0, 68.0), (16.0, 67.0), (14.5, 66.0), (13.5, 65.0), (12.5, 63.5), (12.2, 62.0), (12.3, 60.5), (11.8, 59.4),
]
SWEDEN = [(11.15, 59.0), (11.8, 59.4), (12.3, 60.5), (12.2, 62.0), (14.0, 62.0), (16.0, 59.0), (13.0, 56.0),
          (12.6, 56.2), (12.4, 57.1), (11.9, 57.7), (11.6, 58.3)]
DENMARK = [(10.6, 57.75), (9.95, 57.6), (8.6, 57.12), (8.1, 56.6), (8.15, 56.0), (8.1, 55.5), (8.6, 54.9),
           (9.8, 54.9), (10.4, 55.6), (10.6, 56.4), (10.3, 56.9)]
UK = [(-1.8, 57.5), (-2.1, 57.15), (-2.5, 56.6), (-3.0, 56.0), (-1.7, 55.6), (-1.4, 54.9), (-0.3, 54.2),
      (0.3, 53.4), (1.7, 52.7), (1.5, 52.0), (-3.0, 52.0), (-6.0, 56.0), (-5.0, 58.6), (-3.0, 58.65), (-3.1, 58.0),
      (-1.8, 57.6)]
SHETLAND = [(-1.75, 59.9), (-1.05, 60.1), (-0.85, 60.55), (-1.0, 60.8), (-1.4, 60.7), (-1.6, 60.4)]
ORKNEY = [(-3.4, 58.9), (-2.8, 58.85), (-2.6, 59.2), (-3.1, 59.3)]

FIELDS = {
    "Ekofisk": (3.2, 56.55), "Valhall": (3.39, 56.28), "Sleipner": (1.9, 58.37), "Johan Sverdrup": (2.6, 58.85),
    "Oseberg": (2.83, 60.5), "Troll": (3.65, 60.7), "Gullfaks": (2.27, 61.2), "Statfjord": (1.85, 61.25),
    "Snorre": (2.15, 61.45), "Heidrun": (7.32, 65.32), "Norne": (8.08, 66.0), "Aasta Hansteen": (7.0, 67.1),
    "Snøhvit": (21.0, 71.6), "Johan Castberg": (20.2, 72.5), "Aurora": (3.45, 60.42), "Øygarden": (4.85, 60.55),
}


LABEL_LEFT = {"Statfjord": True, "Sleipner": True, "Oseberg": True, "Valhall": False, "Aurora": True}
LABEL_DY = {"Snorre": -6, "Gullfaks": 22, "Statfjord": 7, "Troll": 0, "Oseberg": 8, "Aurora": 8, "Valhall": 18, "Ekofisk": -4}


class MapView:
    def __init__(self, x, y, w, h, lon0, lon1, lat0, lat1):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.lon0, self.lon1, self.lat0, self.lat1 = lon0, lon1, lat0, lat1
        self.kx = math.cos(math.radians((lat0 + lat1) / 2))

    def p(self, lon, lat):
        sx = self.w / ((self.lon1 - self.lon0) * self.kx)
        sy = self.h / (self.lat1 - self.lat0)
        s = min(sx, sy)
        cx = self.x + self.w / 2 + ((lon - (self.lon0 + self.lon1) / 2) * self.kx) * s
        cy = self.y + self.h / 2 - (lat - (self.lat0 + self.lat1) / 2) * s
        return cx, cy


def draw_map(c, mv: MapView, a=1.0, fields=(), hot=(), t=0.0, labels=True, grid=True):
    if a <= 0:
        return
    c.save()
    c.clipRect(skia.Rect(mv.x, mv.y, mv.x + mv.w, mv.y + mv.h))
    sea = skia.Paint()
    sea.setShader(skia.GradientShader.MakeLinear([skia.Point(mv.x, mv.y), skia.Point(mv.x, mv.y + mv.h)],
                                                 [with_alpha(rgb("#0D2238"), a), with_alpha(rgb("#08182A"), a)]))
    c.drawRect(skia.Rect(mv.x, mv.y, mv.x + mv.w, mv.y + mv.h), sea)
    if grid:
        gp = paint(C.grid, 0.8 * a, stroke=1)
        for lon in range(-6, 32, 2):
            x0, y0 = mv.p(lon, mv.lat0 - 2)
            x1, y1 = mv.p(lon, mv.lat1 + 2)
            c.drawLine(x0, y0, x1, y1, gp)
        for lat in range(50, 76, 1):
            x0, y0 = mv.p(mv.lon0 - 5, lat)
            x1, y1 = mv.p(mv.lon1 + 5, lat)
            c.drawLine(x0, y0, x1, y1, gp)
            if labels and lat % 2 == 0:
                draw_text(c, f"{lat}°N", mv.x + 8, y0 - 6, 14, C.dim, 500, a)
    for shape, col in ((NORWAY, rgb("#2B3A4E")), (SWEDEN, rgb("#232F3F")), (DENMARK, rgb("#232F3F")), (UK, rgb("#232F3F")),
                       (SHETLAND, rgb("#232F3F")), (ORKNEY, rgb("#232F3F"))):
        pth = poly([mv.p(lo, la) for lo, la in shape], close=True)
        c.drawPath(pth, paint(col, a))
        c.drawPath(pth, paint(rgb("#4B6382"), 0.9 * a, stroke=1.4))
    if labels:
        nx, ny = mv.p(8.6, 61.2)
        draw_text(c, "NORWAY", nx, ny, 26, C.muted, 700, 0.7 * a, "center", tracking=6)
        ux, uy = mv.p(-1.5, 57.0)
        draw_text(c, "UK", ux, uy, 20, C.dim, 700, 0.7 * a, "center", tracking=4)
        dx, dy = mv.p(9.2, 56.3)
        draw_text(c, "DENMARK", dx, dy, 18, C.dim, 700, 0.7 * a, "center", tracking=4)
    for name in fields:
        lon, lat = FIELDS[name]
        x, y = mv.p(lon, lat)
        h = 1.0 if name in hot else 0.0
        col = mix(C.primary, C.amber, h)
        if h:
            pr = (t * 0.8) % 1.0
            c.drawCircle(x, y, 10 + 30 * pr, paint(col, a * (1 - pr), stroke=2))
        c.drawCircle(x, y, 7 + 3 * h, paint(col, a))
        c.drawCircle(x, y, 16, paint(col, 0.3 * a, blur=6))
        al = LABEL_LEFT.get(name, False)
        dy = LABEL_DY.get(name, 7)
        draw_text(c, name, x + (-14 if al else 14), y + dy, 20 + 4 * h, C.text if h else C.muted, 600 if h else 500, a,
                  "right" if al else "left", shadow=True)
    c.restore()
    c.drawRect(skia.Rect(mv.x, mv.y, mv.x + mv.w, mv.y + mv.h), paint(C.line, a, stroke=1.5))
    draw_text(c, "schematic map", mv.x + mv.w - 10, mv.y + mv.h - 10, 14, C.dim, 500, a, "right", italic=True)
