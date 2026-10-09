"""Large close-up drawings of the completion fittings, reused by several chapters.

Each function draws at centre (cx, cy) with scale s (world units per half bore width / 0.6) and returns an NS of named object
lists so a chapter can animate parts (a sleeve that slides, a valve that is pulled, keys that engage).
All geometry is a vertical tubing section: bore half-width B = 0.6 s, wall thickness T = 0.18 s.
"""
from __future__ import annotations
import math

from . import palette as P
from .kit import NS


def _r(st, x0, x1, y0, y1, color, z, **kw):
    """Rect from corner coordinates."""
    return st.rect((x0 + x1) / 2, (y0 + y1) / 2, abs(x1 - x0), abs(y1 - y0), color, z, **kw)


def tubing_section(st, cx, cy, s, h, z=0.2, bore=P.BG, color=P.STEEL):
    """Plain tubing wall pair + bore. Returns NS(walls, bore)."""
    B, T = 0.6 * s, 0.18 * s
    walls = [_r(st, cx - B - T, cx - B, cy - h / 2, cy + h / 2, color, z), _r(st, cx + B, cx + B + T, cy - h / 2, cy + h / 2, color, z)]
    bo = [_r(st, cx - B, cx + B, cy - h / 2, cy + h / 2, bore, z - 0.05)]
    return NS(walls=walls, bore=bo)


def nipple_inset(st, cx, cy, s=2.0, h=None, z=0.2, y_top=None, y_bot=None):
    """Landing nipple: the tubing wall thickens into a polished seal bore above and below a machined locking groove.
    The groove is centred on cy (half height 0.2 s); the lower seal bore is 1.1 s long, the upper 0.4 s.
    Returns NS(walls, bore, body, groove_y, seal_y, B, T, groove, cx, top, bot)."""
    B, T = 0.6 * s, 0.18 * s
    if y_top is None:
        h = h or 3.4 * s
        y_top, y_bot = cy + h / 2, cy - h / 2
    sec_h = y_top - y_bot
    walls = [_r(st, cx - B - T, cx - B, y_bot, y_top, P.STEEL, z), _r(st, cx + B, cx + B + T, y_bot, y_top, P.STEEL, z)]
    bore = [_r(st, cx - B, cx + B, y_bot, y_top, P.BG, z - 0.05)]
    yt, yg0, yg1, yb = cy + 0.6 * s, cy + 0.2 * s, cy - 0.2 * s, cy - 1.3 * s
    body = []
    for sd in (-1, 1):
        def X(a, b):
            return (cx + sd * a, cx + sd * b)
        x0, x1 = X(B * 0.78, B)
        body.append(_r(st, x0, x1, yg0, yt, P.STEEL, z + 0.02))
        x0, x1 = X(B * 1.12, B)
        body.append(_r(st, x0, x1, yg1, yg0, P.BG, z + 0.03))
        x0, x1 = X(B * 0.78, B)
        body.append(_r(st, x0, x1, yb, yg1, P.STEEL, z + 0.02))
    return NS(walls=walls, bore=bore, body=body, groove_y=cy, seal_y=((yt + yg0) / 2, (yg1 + yb) / 2), top=y_top, bot=y_bot, B=B, T=T, groove=(yg1, yg0), cx=cx,
              seal_bore_low=(yb, yg1), seal_bore_up=(yg0, yt))


def mandrel_inset(st, cx, cy, s=2.0, valve=True, z=0.2, open_top=False):
    """Side-pocket mandrel: main bore on the left, an off-centre pocket on the right holding a gas-lift valve. Annulus gas enters
    the pocket through lower ports, passes the valve and leaves into the bore through an upper port.
    Returns NS(body, bore, pocket, valve, ports, gas_path, ...)."""
    B, T = 0.6 * s, 0.18 * s
    h = 4.0 * s
    top, bot = cy + h / 2, cy - h / 2
    pk_x0, pk_x1 = cx + B + 0.1 * s, cx + B + 0.1 * s + 0.62 * s     # pocket chamber (inside the bulge)
    out_x = pk_x1 + T
    body = [_r(st, cx - B - T, cx - B, bot, top, P.STEEL, z),                       # left wall of the bore
            _r(st, cx + B, cx + B + 0.1 * s, bot, top, P.STEEL, z),                  # wall between bore and pocket
            _r(st, pk_x1, out_x, bot, top, P.STEEL, z)]                              # outer wall of the bulge (right)
    # the bulge is wider than the plain tubing between y_b0 and y_b1
    bore = [_r(st, cx - B, cx + B, bot, top, P.BG, z - 0.05)]
    pocket = [_r(st, pk_x0, pk_x1, cy - 1.45 * s, cy + 1.6 * s, P.BG, z - 0.04)]
    # ports: lower port through the outer wall (annulus -> pocket); upper port through the inner wall (pocket -> bore)
    y_lo, y_hi = cy - 1.2 * s, cy + 1.25 * s
    ports = [_r(st, pk_x1, out_x, y_lo - 0.1 * s, y_lo + 0.1 * s, P.BG, z + 0.03),
             _r(st, cx + B, cx + B + 0.1 * s, y_hi - 0.1 * s, y_hi + 0.1 * s, P.BG, z + 0.03)]
    # pocket ends (steel cap top and bottom)
    caps = [_r(st, pk_x0, pk_x1, cy - 1.6 * s, cy - 1.45 * s, P.STEEL, z)] + ([] if open_top else [_r(st, pk_x0, pk_x1, cy + 1.6 * s, cy + 1.75 * s, P.STEEL, z)])
    vx = (pk_x0 + pk_x1) / 2
    vparts = []
    if valve:
        vparts = gl_valve(st, vx, cy, s, z + 0.05)
    # gas path: annulus (right) -> lower port -> up the pocket past the valve -> upper port -> bore
    gas = [(out_x + 0.35 * s, y_lo), (vx, y_lo), (vx, y_hi), (cx + B + 0.05 * s, y_hi), (cx + 0.05 * s, y_hi)]
    return NS(body=body + caps, bore=bore, pocket=pocket, valve=vparts, ports=ports, gas_path=gas, cx=cx, cy=cy, vx=vx, pk=(pk_x0, pk_x1),
              y_lo=y_lo, y_hi=y_hi, B=B, s=s)


def gl_valve(st, vx, cy, s, z=0.25, color=P.PANEL2):
    """The gas-lift valve in its pocket: a latch at the top (fishing neck), a body with packing seals and a check at the bottom."""
    w = 0.38 * s
    neck = _r(st, vx - 0.07 * s, vx + 0.07 * s, cy + 1.25 * s, cy + 1.55 * s, P.STEEL, z)
    head = _r(st, vx - 0.17 * s, vx + 0.17 * s, cy + 1.0 * s, cy + 1.25 * s, P.STEEL, z)
    body = _r(st, vx - w / 2, vx + w / 2, cy - 1.3 * s, cy + 1.0 * s, P.GAS, z, role="flat")
    seals = [_r(st, vx - w / 2 - 0.03 * s, vx + w / 2 + 0.03 * s, cy + 0.65 * s, cy + 0.72 * s, P.RUBBER, z + 0.01, role="solid"),
             _r(st, vx - w / 2 - 0.03 * s, vx + w / 2 + 0.03 * s, cy - 0.45 * s, cy - 0.38 * s, P.RUBBER, z + 0.01, role="solid")]
    check = _r(st, vx - w / 4, vx + w / 4, cy - 1.3 * s, cy - 1.15 * s, P.STEEL, z + 0.01)
    return [neck, head, body] + seals + [check]


def sleeve_inset(st, cx, cy, s=2.0, z=0.2, open_=False):
    """Sliding sleeve: outer housing with two ports; an inner sleeve that slides down to open them. Returns NS(walls, bore, ports,
    inner (the moving sleeve), y_closed, y_open)."""
    B, T = 0.6 * s, 0.18 * s
    h = 3.4 * s
    top, bot = cy + h / 2, cy - h / 2
    py0, py1 = cy - 0.25 * s, cy + 0.25 * s
    walls = []
    for sd in (-1, 1):
        a, b = sorted((cx + sd * B, cx + sd * (B + T)))
        walls.append(_r(st, a, b, py1, top, P.STEEL, z))
        walls.append(_r(st, a, b, bot, py0, P.STEEL, z))
    bore = [_r(st, cx - B, cx + B, bot, top, P.BG, z - 0.05)]
    ports = []
    for sd in (-1, 1):
        a, b = sorted((cx + sd * B, cx + sd * (B + T)))
        ports.append(_r(st, a, b, py0, py1, P.BG, z + 0.01))
    # the inner sleeve (a thin shell lining the bore), 1.0 s tall; closed: covers the ports; open: slid down below them
    y_closed = cy
    y_open = cy - 0.95 * s
    sl = []
    for sd in (-1, 1):
        a, b = sorted((cx + sd * B * 0.9, cx + sd * B))
        sl.append(st.rect((a + b) / 2, y_open if open_ else y_closed, abs(b - a), 0.95 * s, P.PRIMARY_B, z + 0.03, role="flat"))
    return NS(walls=walls, bore=bore, ports=ports, inner=sl, y_closed=y_closed, y_open=y_open, B=B, T=T, py=(py0, py1), cx=cx)


def perf_inset(st, cx, cy, s=2.0, z=0.1, n=3):
    """Perforations in section: casing wall on the left (vertical), cement, then sand on the right; tunnels from the sand
    through cement and casing into the well. Returns NS(rock, cement, casing, tunnels, paths (flow polylines))."""
    H = 3.6 * s
    top, bot = cy + H / 2, cy - H / 2
    x_cas0, x_cas1 = cx - 0.55 * s, cx - 0.4 * s         # casing wall
    x_cem1 = cx - 0.05 * s                               # cement outer edge
    x_end = cx + 2.4 * s
    sand = _r(st, x_cem1, x_end, bot, top, P.SAND, z)
    cement = _r(st, x_cas1, x_cem1, bot, top, P.CEMENT, z + 0.01)
    casing = _r(st, x_cas0, x_cas1, bot, top, P.STEEL_DK, z + 0.02)
    bore = _r(st, cx - 2.4 * s, x_cas0, bot, top, P.BG, z - 0.02)
    tunnels, paths = [], []
    ys = [cy + (i - (n - 1) / 2) * 0.95 * s for i in range(n)]
    for y in ys:
        L = 1.55 * s
        pts = [(x_cas0 - 0.02 * s, y - 0.09 * s), (x_cas0 - 0.02 * s, y + 0.09 * s), (x_cem1 + L, y + 0.04 * s), (x_cem1 + L, y - 0.04 * s)]
        # tunnel drawn from the casing inside edge to the tip; reversed x because it extends to the right
        tunnels.append(st.poly([(x_cas0 - 0.02 * s, y - 0.1 * s), (x_cas0 - 0.02 * s, y + 0.1 * s), (x_cem1 + L, y + 0.035 * s),
                                (x_cem1 + L, y - 0.035 * s)], P.BG, z + 0.05, role="flat"))
        paths.append([(x_cem1 + L * 0.95, y), (x_cas0 - 0.4 * s, y)])
    return NS(rock=[sand], cement=[cement], casing=[casing], bore=[bore], tunnels=tunnels, paths=paths, ys=ys, x_cas=(x_cas0, x_cas1),
              x_cem=x_cem1, x_end=x_end, sand=[sand])
