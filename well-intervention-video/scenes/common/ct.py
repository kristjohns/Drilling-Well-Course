"""Coiled-tubing drawings: the injector head with moving gripper chains, the stripper, the quad BOP with closing rams, tube paths.

All geometry is in world units. The injector chains are drawn by a procedural callback, so the chain blocks and the tube tick marks
really move (speed is a signed function of time: positive = tube driven down into the well).
"""
from __future__ import annotations
import math

import skia

from . import palette as P
from .kit import NS
from .look import col, lighten, darken
from .stage import hex_rgb


def arc_pts(cx, cy, r, a0, a1, n=40):
    """Points on a circle arc from angle a0 to a1 (degrees, counter-clockwise from +x)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def path_len(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:]))


def injector(st, cx, cy, h=2.6, gap=0.5, rho=0.42, t0=0.0, t1=1.0, speed=lambda t: 0.8, z=0.5, tube_h=None):
    """Injector head cutaway: two endless gripper chains either side of the tube (x = cx), squeezing cylinders and a frame.
    The chain blocks and tube tick marks are animated by a procedural from t0 to t1 with signed speed(t) (world units / s).
    Returns NS(frame, tube, procs, cyl (squeezing arrows), left_x, right_x, inner_l, inner_r)."""
    L = h - 2 * rho
    xl, xr = cx - gap / 2 - rho - 0.12, cx + gap / 2 + rho + 0.12
    frame = [st.rect(cx, cy, xr - xl + 1.5, h + 0.3, P.PANEL2, z - 0.2, role="card")]
    tube_h = tube_h if tube_h is not None else h + 2.6
    tube = st.rect(cx, cy, gap * 0.78, tube_h, P.STEEL, z + 0.05, role="steel")
    in_l, in_r = xl + rho, xr - rho
    N = 16

    def loop_pos(s_, side):
        """Position and tangent angle (deg) on a racetrack. side=-1: left chain (inner edge on its right), +1: right chain.
        Both chains move down along the inner run when the speed is positive (the tube is driven into the well)."""
        xc = xl if side < 0 else xr
        Lt_ = 2 * L + 2 * math.pi * rho
        s_ %= Lt_
        xin, xout = (xc + rho, xc - rho) if side < 0 else (xc - rho, xc + rho)
        if s_ < L:
            return xin, cy + L / 2 - s_, 270.0
        s_ -= L
        if s_ < math.pi * rho:
            a = s_ / rho
            if side < 0:
                th = -a
                ang = math.degrees(th) - 90
            else:
                th = math.pi + a
                ang = math.degrees(th) + 90
            return xc + rho * math.cos(th), cy - L / 2 + rho * math.sin(th), ang
        s_ -= math.pi * rho
        if s_ < L:
            return xout, cy - L / 2 + s_, 90.0
        s_ -= L
        a = s_ / rho
        if side < 0:
            th = math.pi - a
            ang = math.degrees(th) - 90
        else:
            th = a
            ang = math.degrees(th) + 90
        return xc + rho * math.cos(th), cy + L / 2 + rho * math.sin(th), ang

    Lt = 2 * L + 2 * math.pi * rho
    spacing = Lt / N

    def phase(t):
        n = max(int((t - t0) / 0.05), 0)
        ph = sum(speed(t0 + (k + 0.5) * 0.05) for k in range(n)) * 0.05
        return ph + speed(t0 + n * 0.05) * ((t - t0) - n * 0.05)

    def draw(c, t, look):
        ph = phase(t)
        body = skia.Paint(Color=col(hex_rgb(P.STEEL_DK), 1.0), AntiAlias=True)
        grip = skia.Paint(Color=col(hex_rgb(P.WARN), 1.0), AntiAlias=True)
        belt = skia.Paint(Color=col(hex_rgb("#3a4666"), 1.0), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.07)
        for side, xc in ((-1, xl), (1, xr)):
            path = skia.Path()
            path.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(xc - rho, cy - h / 2, xc + rho, cy + h / 2), rho, rho))
            c.drawPath(path, belt)
            for k in range(N):
                s_ = k * spacing + ph
                x, y, ang = loop_pos(s_, side)
                inner_run = (s_ % Lt) < L
                c.save()
                c.translate(x, y)
                c.rotate(ang)
                c.drawRect(skia.Rect.MakeLTRB(-0.17, -0.12, 0.17, 0.12), grip if inner_run else body)
                c.restore()
        tick = skia.Paint(Color=col(hex_rgb(P.STEEL_DK), 0.9), AntiAlias=True)
        sp = 0.45
        y_lo, y_hi = cy - h / 2, cy + h / 2
        yy = y_lo - sp + (ph % sp)
        while yy < y_hi:
            if y_lo <= yy <= y_hi:
                c.drawRect(skia.Rect.MakeLTRB(cx - gap * 0.39, yy, cx + gap * 0.39, yy + 0.05), tick)
            yy += sp

    st.procedural(t0, t1, z + 0.1, draw)
    sprocket = []
    for xc in (xl, xr):
        for yy in (cy + L / 2, cy - L / 2):
            sprocket.append(st.circle(xc, yy, rho * 0.55, P.STEEL, z + 0.02, role="solid"))
    return NS(frame=frame, tube=[tube], sprockets=sprocket, left_x=xl, right_x=xr, inner_l=in_l, inner_r=in_r, h=h, cx=cx, cy=cy)


def stripper(st, cx, y, w=1.5, h=0.7, z=0.5, tube_w=0.4):
    """Stripper (packoff): a housing with rubber elements squeezed by a hydraulic piston around the tube. Returns NS(parts, rubber, pistons)."""
    housing = [st.rect(cx - w / 2, y, 0.2, h, P.STEEL_DK, z, role="steel"), st.rect(cx + w / 2, y, 0.2, h, P.STEEL_DK, z, role="steel"),
               st.rect(cx, y + h / 2, w + 0.2, 0.14, P.STEEL, z, role="steel"), st.rect(cx, y - h / 2, w + 0.2, 0.14, P.STEEL, z, role="steel")]
    rubber = [st.rect(cx - tube_w / 2 - 0.3, y, 0.55, h * 0.8, P.RUBBER, z + 0.02, role="solid"), st.rect(cx + tube_w / 2 + 0.3, y, 0.55, h * 0.8, P.RUBBER, z + 0.02, role="solid")]
    pist = [st.rect(cx - w / 2 + 0.2, y, 0.14, h * 0.6, P.STEEL, z + 0.03, role="steel"), st.rect(cx + w / 2 - 0.2, y, 0.14, h * 0.6, P.STEEL, z + 0.03, role="steel")]
    return NS(parts=housing + rubber + pist, rubber=rubber, pistons=pist, housing=housing, y=y, h=h, w=w)


def bop_quad(st, cx, y_top, sec_h=0.95, w=2.8, z=0.4, tube_w=0.4):
    """Quad coiled-tubing BOP, top to bottom: blind, shear, slip, pipe rams. Each section has two ram blocks (retracted); closing moves them
    to the tube. Returns NS(body, sections={name: dict(y, left, right, label)}, close(name, t0, t1)) and helper positions."""
    names = ["blind rams", "shear rams", "slip rams", "pipe rams"]
    colors = {"blind rams": P.BAD, "shear rams": "#ff8a5c", "slip rams": P.WARN, "pipe rams": P.PRIMARY_B}
    secs, body = {}, []
    for i, nm in enumerate(names):
        yc = y_top - sec_h * (i + 0.5)
        body.append(st.rect(cx, yc, w, sec_h - 0.04, P.STEEL_DK, z, role="steel"))
        body.append(st.rect(cx, yc, tube_w + 0.12, sec_h - 0.04, P.BG, z + 0.02, role="hole"))
        left = st.rect(cx - w / 2 + 0.45, yc, 0.8, 0.5, colors[nm], z + 0.05, role="solid")
        right = st.rect(cx + w / 2 - 0.45, yc, 0.8, 0.5, colors[nm], z + 0.05, role="solid")
        body += [st.rect(cx - w / 2 - 0.25, yc, 0.5, 0.34, P.STEEL, z - 0.02, role="steel"), st.rect(cx + w / 2 + 0.25, yc, 0.5, 0.34, P.STEEL, z - 0.02, role="steel")]
        secs[nm] = dict(y=yc, left=left, right=right, color=colors[nm])
    return NS(body=body, sections=secs, names=names, cx=cx, w=w, y_top=y_top, sec_h=sec_h, y_bot=y_top - sec_h * 4, tube_w=tube_w)


def close_ram(st, stack, name, t0, t1):
    """Slide the two blocks of a ram section to the tube (blind/shear: to a gap of ~0)."""
    sec = stack.sections[name]
    cx, tw = stack.cx, stack.tube_w
    if name in ("blind rams", "shear rams"):
        xl, xr = cx - 0.4 + (0.0 if name == "blind rams" else 0.0), cx + 0.4
    else:
        xl, xr = cx - tw / 2 - 0.4, cx + tw / 2 + 0.4
    st.move(sec["left"], t0, t1, to=(xl, sec["y"]))
    st.move(sec["right"], t0, t1, to=(xr, sec["y"]))
