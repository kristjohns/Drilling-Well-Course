"""Data-driven 2-D chart built from Stage primitives (so charts live in the same Blender scene as everything else)."""
from __future__ import annotations

from . import palette as P


class Chart:
    """A plot area with its lower-left corner at world (x, y), size (w, h), data ranges xr, yr.

    invert_y=True puts yr[0] at the TOP (depth increasing downward)."""

    def __init__(self, st, x, y, w, h, xr, yr, invert_y=False, z=0.05):
        self.st, self.x, self.y, self.w, self.h = st, x, y, w, h
        self.xr, self.yr, self.inv, self.z = xr, yr, invert_y, z
        self.furniture: list = []

    # data -> world
    def X(self, v):
        return self.x + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, v):
        f = (v - self.yr[0]) / (self.yr[1] - self.yr[0])
        return self.y + (self.h - f * self.h if self.inv else f * self.h)

    def pt(self, vx, vy):
        return (self.X(vx), self.Y(vy))

    def frame(self, xticks=(), yticks=(), xlabel="", ylabel="", fx="{:g}", fy="{:,.0f}", grid=True, title=None, panel=True,
              tick_size=0.2):
        st, z = self.st, self.z
        out = []
        if panel:
            out.append(st.rect(self.x + (self.w - 1.0) / 2, self.y + (self.h - 0.55) / 2, self.w + 1.5, self.h + 1.3, P.PANEL, z - 0.04))
        for v in xticks:
            xv = self.X(v)
            if grid:
                out.append(st.rect(xv, self.y + self.h / 2, 0.012, self.h, P.GRID, z - 0.02))
            out.append(st.text(fx.format(v), xv, self.y - 0.24, tick_size, P.MUTED, z))
        for v in yticks:
            yv = self.Y(v)
            if grid:
                out.append(st.rect(self.x + self.w / 2, yv, self.w, 0.012, P.GRID, z - 0.02))
            out.append(st.text(fy.format(v), self.x - 0.12, yv, tick_size, P.MUTED, z, align="r"))
        out.append(st.rect(self.x + self.w / 2, self.y, self.w, 0.03, P.MUTED, z))               # x axis
        out.append(st.rect(self.x, self.y + self.h / 2, 0.03, self.h, P.MUTED, z))               # y axis
        if xlabel:
            out.append(st.text(xlabel, self.x + self.w / 2, self.y - 0.62, 0.24, P.MUTED, z))
        if ylabel:
            t = st.text(ylabel, self.x - 0.95, self.y + self.h / 2, 0.24, P.MUTED, z)
            t.rotation_euler[2] = 1.5707963
            out.append(t)
        if title:
            out.append(st.text(title, self.x + self.w / 2, self.y + self.h + 0.28, 0.3, P.TEXT, z, kind="bold"))
        self.furniture += out
        return out

    def curve(self, xs, ys, color, width=0.07, z=0.2):
        return self.st.line([self.pt(a, b) for a, b in zip(xs, ys)], color, width, z)

    def band(self, left_pts, right_pts, color, z=0.1, alpha=0.5):
        """Filled region between two data polylines (each a list of (vx, vy))."""
        pts = [self.pt(*p) for p in left_pts] + [self.pt(*p) for p in reversed(right_pts)]
        return self.st.poly(pts, color, z, alpha)

    def dot(self, vx, vy, r=0.1, color=P.TEXT, z=0.3):
        return self.st.circle(self.X(vx), self.Y(vy), r, color, z)

    def hline(self, vy, color, width=0.04, z=0.15, x0=None, x1=None):
        a = self.X(self.xr[0] if x0 is None else x0)
        b = self.X(self.xr[1] if x1 is None else x1)
        return self.st.rect((a + b) / 2, self.Y(vy), b - a, width, color, z)

    def vline(self, vx, color, width=0.04, z=0.15, y0=None, y1=None):
        a = self.Y(self.yr[0] if y0 is None else y0)
        b = self.Y(self.yr[1] if y1 is None else y1)
        return self.st.rect(self.X(vx), (a + b) / 2, width, abs(b - a), color, z)

    def label(self, vx, vy, s, size=0.24, color=P.TEXT, align="l", kind="sans", z=0.3, dx=0.0, dy=0.0):
        return self.st.text(s, self.X(vx) + dx, self.Y(vy) + dy, size, color, z, align=align, kind=kind)
