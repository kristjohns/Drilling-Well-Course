"""Parametric well schematic renderer.

Geometry is in metres (depth, vertical well) and inches (diameters). The depth
axis is piecewise linear ("not to scale") so the interesting deep section gets
more room. Radial dimensions are exaggerated, as in any well schematic.

Illustrative architecture (northern North Sea style):
  30"   conductor            0 - 180 m   cemented to seabed
  20"   surface casing       0 - 700 m   cemented to seabed
  13 3/8" intermediate       0 - 1800 m  TOC 1200 m
  9 5/8" production casing   0 - 2950 m  TOC 2350 m (shoe in Draupne cap rock)
  7"    production liner  2850 - 3330 m cemented to liner top
  4 1/2" tubing, production packer at 2800 m, DHSV at 450 m
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import skia

from .core import (C, clamp, ease_in_out, ease_out, lerp, mix, noise_image, paint, poly, rgb, speckle_image,
                   with_alpha, image_shader, draw_text, glow_path, trim_path)


# --------------------------------------------------------------- lithology
@dataclass
class Layer:
    top: float
    base: float
    lith: str
    name: str = ""
    group: str = ""


STRATIGRAPHY = [
    Layer(0, 700, "clay", "Clays and sands", "Nordland Gp"),
    Layer(700, 1650, "claystone", "Claystone", "Hordaland Gp"),
    Layer(1650, 2050, "shale", "Shale and tuff", "Rogaland Gp"),
    Layer(2050, 2550, "chalk", "Chalk and limestone", "Shetland Gp"),
    Layer(2550, 2700, "marl", "Marl", "Cromer Knoll Gp"),
    Layer(2700, 3000, "caprock", "Draupne shale (cap rock)", "Viking Gp"),
    Layer(3000, 3250, "reservoir", "Reservoir sandstone", "Brent Gp"),
    Layer(3250, 3600, "shale", "Shale and siltstone", "Dunlin Gp"),
]

LITH_COLORS = {
    "clay": rgb("#5F5A4C"),
    "claystone": rgb("#4F5552"),
    "shale": rgb("#3F4A4B"),
    "chalk": rgb("#A7A291"),
    "marl": rgb("#77766A"),
    "caprock": rgb("#2E3437"),
    "reservoir": rgb("#8D6431"),
    "sand": rgb("#A88B57"),
    "water_sand": rgb("#6F7E80"),
}

_TEX = {}


def lith_texture(lith: str) -> skia.Image:
    if lith in _TEX:
        return _TEX[lith]
    base = LITH_COLORS[lith]
    w, h = 1024, 512
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    c.clear(base)
    tile = skia.ISize(w, h)

    def noise_layer(fx, fy, oct_, seed, alpha, mode=skia.BlendMode.kOverlay, turb=False):
        mk = skia.PerlinNoiseShader.MakeTurbulence if turb else skia.PerlinNoiseShader.MakeFractalNoise
        sh = mk(fx, fy, oct_, seed, tile)
        p = skia.Paint(Shader=sh)
        p.setColorFilter(skia.ColorFilters.Matrix([
            0.5, 0.5, 0, 0, 0, 0.5, 0.5, 0, 0, 0, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, alpha]))
        p.setBlendMode(mode)
        c.drawRect(skia.Rect(0, 0, w, h), p)

    rnd = np.random.default_rng(abs(hash(lith)) % 2**32)
    if lith in ("shale", "caprock", "claystone"):
        noise_layer(0.0025, 0.09, 3, 3, 0.55)
        noise_layer(0.01, 0.01, 2, 5, 0.25)
        # fine laminae
        for _ in range(55):
            y = rnd.uniform(0, h)
            c.drawLine(0, y, w, y + rnd.uniform(-3, 3), paint(C.black if rnd.random() < .6 else C.white,
                                                              rnd.uniform(0.04, 0.10), stroke=rnd.uniform(0.6, 1.6)))
    elif lith in ("chalk", "marl"):
        noise_layer(0.006, 0.012, 4, 7, 0.45)
        for _ in range(900):
            c.drawCircle(rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(0.5, 1.6), paint(C.black, rnd.uniform(0.05, 0.18)))
    elif lith in ("reservoir", "sand", "water_sand"):
        noise_layer(0.012, 0.03, 3, 11, 0.40)
        cols = [mix(base, C.white, 0.35), mix(base, C.black, 0.35), mix(base, rgb("#E8C27A"), 0.5)]
        for _ in range(14000):
            c.drawCircle(rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(0.6, 2.0),
                         paint(cols[rnd.integers(0, 3)], rnd.uniform(0.25, 0.7)))
    else:  # clay
        noise_layer(0.004, 0.02, 4, 13, 0.5)
        for _ in range(2500):
            c.drawCircle(rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(0.5, 1.8), paint(mix(base, C.white, 0.3), rnd.uniform(0.15, 0.45)))
    img = surf.makeImageSnapshot()
    _TEX[lith] = img
    return img


_CEMENT = None


def cement_texture() -> skia.Image:
    global _CEMENT
    if _CEMENT is None:
        w, h = 512, 512
        surf = skia.Surface(w, h)
        c = surf.getCanvas()
        c.clear(C.cement)
        sh = skia.PerlinNoiseShader.MakeFractalNoise(0.03, 0.03, 3, 21, skia.ISize(w, h))
        p = skia.Paint(Shader=sh, BlendMode=skia.BlendMode.kOverlay)
        p.setColorFilter(skia.ColorFilters.Matrix([0.5, .5, 0, 0, 0, .5, .5, 0, 0, 0, .5, .5, 0, 0, 0, 0, 0, 0, 0, .45]))
        c.drawRect(skia.Rect(0, 0, w, h), p)
        rnd = np.random.default_rng(5)
        for _ in range(4000):
            col = C.white if rnd.random() < 0.5 else rgb("#6E6A60")
            c.drawCircle(rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(0.5, 1.5), paint(col, rnd.uniform(0.25, 0.7)))
        _CEMENT = surf.makeImageSnapshot()
    return _CEMENT


# --------------------------------------------------------------- tubulars
@dataclass
class Casing:
    key: str
    name: str
    od: float
    id: float
    top: float
    shoe: float
    toc: float | None
    hole: float          # open hole diameter drilled for this string
    label: str = ""


DEFAULT_STRINGS = [
    Casing("cond", "30\" conductor", 30.0, 28.0, 0, 180, 0, 36.0, "30 in"),
    Casing("surf", "20\" surface casing", 20.0, 18.73, 0, 700, 0, 26.0, "20 in"),
    Casing("int", "13 3/8\" intermediate casing", 13.375, 12.415, 0, 1800, 1200, 17.5, "13⅜ in"),
    Casing("prod", "9 5/8\" production casing", 9.625, 8.535, 0, 2950, 2350, 12.25, "9⅝ in"),
    Casing("liner", "7\" production liner", 7.0, 6.184, 2850, 3330, 2850, 8.5, "7 in"),
]


@dataclass
class WellState:
    """Everything that can vary from frame to frame."""
    strings: list = field(default_factory=lambda: list(DEFAULT_STRINGS))
    td: float = 3330.0
    hole_td: float = 3330.0               # deepest drilled depth
    show_strings: dict = field(default_factory=dict)   # key -> alpha (default 1)
    string_extent: dict = field(default_factory=dict)  # key -> fraction of run (0..1)
    cement_fill: dict = field(default_factory=dict)    # key -> 0..1 fraction of cement placed
    bore_fluid: int = C.mud
    bore_fluid_alpha: float = 0.85
    annulus_fluid: int = C.mud                          # fluid above TOC in annuli
    fluid_level: float = 0.0                            # depth of fluid top inside bore
    a_annulus_fluid: int | None = None                  # packer fluid when completed
    tubing_fluid: int = C.oil
    # completion
    completion: float = 0.0       # 0 = none, 1 = fully installed (slides in)
    packer_depth: float = 2800.0
    dhsv_depth: float = 450.0
    tubing_tail: float = 2820.0
    tubing_od: float = 4.5
    tubing_id: float = 3.958
    dhsv_open: float = 1.0
    perforations: float = 0.0
    perf_top: float = 3040.0
    perf_base: float = 3200.0
    # drilling
    drillstring: float = 0.0
    bit_depth: float = 3150.0
    rotation: float = 0.0
    # surface
    surface: str = "tree"          # 'tree' | 'bop' | 'none' | 'cap'
    surface_alpha: float = 1.0
    bop_close: float = 0.0
    tree_valves_closed: dict = field(default_factory=dict)
    # plugs: list of dicts(top, base, kind, alpha, fill)
    plugs: list = field(default_factory=list)
    # highlights: list of (element_key, color, alpha)
    highlights: list = field(default_factory=list)
    # fluid overlays drawn over the bore fluid: dict(kind='bore'|'dp', d0, d1, color, alpha)
    overlays: list = field(default_factory=list)


class WellView:
    """Maps world (depth m, radius in) to screen pixels."""

    def __init__(self, axis_x: float, y_top: float, y_bot: float, sx: float = 7.0,
                 knots_d=(0, 700, 1800, 2700, 3400), knots_f=(0, 0.16, 0.36, 0.58, 1.0),
                 x_left: float | None = None, x_right: float | None = None):
        self.ax = axis_x
        self.y_top = y_top
        self.y_bot = y_bot
        self.sx = sx
        self.kd = np.array(knots_d, float)
        self.kf = np.array(knots_f, float)
        self.x_left = x_left if x_left is not None else axis_x - 520
        self.x_right = x_right if x_right is not None else axis_x + 520
        self.regions = {}

    def y(self, d: float) -> float:
        f = float(np.interp(d, self.kd, self.kf, left=None, right=None))
        if d > self.kd[-1]:
            f = self.kf[-1] + (d - self.kd[-1]) * (self.kf[-1] - self.kf[-2]) / (self.kd[-1] - self.kd[-2])
        return self.y_top + f * (self.y_bot - self.y_top)

    def d_of_y(self, y: float) -> float:
        f = (y - self.y_top) / (self.y_bot - self.y_top)
        return float(np.interp(f, self.kf, self.kd))

    def r(self, diameter_in: float) -> float:
        """half width in px for a diameter in inches."""
        return diameter_in * 0.5 * self.sx

    def xl(self, diameter_in):
        return self.ax - self.r(diameter_in)

    def xr(self, diameter_in):
        return self.ax + self.r(diameter_in)

    # register a highlightable region (list of rects or path)
    def reg(self, key, path: skia.Path):
        if key in self.regions:
            self.regions[key].addPath(path)
        else:
            self.regions[key] = skia.Path(path)


def rect_path(x0, y0, x1, y1) -> skia.Path:
    p = skia.Path()
    p.addRect(skia.Rect(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
    return p


def steel_paint(x0, x1, alpha=1.0, tint=None):
    base_dk, base_mid, base_hi = C.steel_dk, C.steel, C.steel_hi
    if tint is not None:
        base_dk, base_mid, base_hi = mix(tint, C.black, .55), tint, mix(tint, C.white, .42)
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear(
        [skia.Point(x0, 0), skia.Point(x1, 0)],
        [with_alpha(base_dk, alpha), with_alpha(base_hi, alpha), with_alpha(base_mid, alpha), with_alpha(base_dk, alpha)],
        [0.0, 0.35, 0.6, 1.0]))
    return p


# --------------------------------------------------------------- drawing
def draw_formation(c: skia.Canvas, v: WellView, layers=STRATIGRAPHY, alpha=1.0, labels=False, label_alpha=1.0,
                   x_label=None, depth_max=None, tex_scale=0.6, reservoir_glow=0.0, t=0.0):
    depth_max = depth_max if depth_max is not None else v.kd[-1]
    for L in layers:
        if L.top >= depth_max:
            continue
        y0, y1 = v.y(L.top), v.y(min(L.base, depth_max))
        r = skia.Rect(v.x_left, y0, v.x_right, y1)
        p = skia.Paint(AntiAlias=False, Shader=image_shader(lith_texture(L.lith), tex_scale, 0, y0 * 0.37))
        p.setAlphaf(alpha)
        c.drawRect(r, p)
        if L.lith == "reservoir" and reservoir_glow > 0:
            gp = skia.Paint()
            gp.setShader(skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)],
                                                        [with_alpha(C.amber, 0.0), with_alpha(C.amber, 0.28 * reservoir_glow),
                                                         with_alpha(C.amber, 0.0)]))
            c.drawRect(r, gp)
        # subtle boundary line
        c.drawLine(v.x_left, y0, v.x_right, y0, paint(C.black, 0.35 * alpha, stroke=1.2))
    if labels:
        for L in layers:
            if L.top >= depth_max:
                continue
            ym = (v.y(L.top) + v.y(min(L.base, depth_max))) / 2
            xl = x_label if x_label is not None else v.x_left + 18
            draw_text(c, L.group, xl, ym - 4, 19, C.text, 600, 0.85 * label_alpha * alpha, shadow=True)
            draw_text(c, L.name, xl, ym + 19, 16, C.muted, 400, 0.85 * label_alpha * alpha, shadow=True)


def _outer_boundary(st: WellState, idx: int, d: float) -> float:
    """Diameter of the outer boundary of the annulus outside string idx at depth d."""
    s = st.strings[idx]
    for j in range(idx - 1, -1, -1):
        o = st.strings[j]
        if _alpha(st, o.key) > 0.5 and o.top <= d <= o.shoe:
            return o.id
    return s.hole


def _alpha(st: WellState, key: str) -> float:
    return st.show_strings.get(key, 1.0)


def draw_well(c: skia.Canvas, v: WellView, st: WellState, t: float = 0.0, alpha: float = 1.0):
    """Draw holes, cement, casings, fluids, completion, plugs. Registers regions on v."""
    v.regions = {}
    strings = st.strings

    # 1) open hole + fluid for each section (outer to inner)
    prev_shoe = 0.0
    for i, s in enumerate(strings):
        a = _alpha(st, s.key)
        hole_top = 0.0 if i == 0 else strings[i - 1].shoe
        hole_bot = min(s.shoe if a > 0.5 else st.hole_td, st.hole_td)
        if i == len(strings) - 1 or _alpha(st, strings[i].key) < 0.5:
            hole_bot = st.hole_td
        if hole_bot > hole_top:
            x0, x1 = v.xl(s.hole), v.xr(s.hole)
            c.drawRect(skia.Rect(x0, v.y(hole_top), x1, v.y(hole_bot)), paint(rgb("#1E1A16"), alpha))
        prev_shoe = s.shoe

    # deepest open hole below the last string that is present
    present = [s for s in strings if _alpha(st, s.key) > 0.01]
    last = present[-1] if present else None
    if last is not None and st.hole_td > last.shoe:
        nxt = strings[strings.index(last) + 1] if strings.index(last) + 1 < len(strings) else None
        hd = nxt.hole if nxt is not None else last.hole * 0.75
        c.drawRect(skia.Rect(v.xl(hd), v.y(last.shoe), v.xr(hd), v.y(st.hole_td)), paint(rgb("#1E1A16"), alpha))
        v.reg("openhole", rect_path(v.xl(hd), v.y(last.shoe), v.xr(hd), v.y(st.hole_td)))
        v.reg("formation_below_" + last.key, rect_path(v.xl(hd) - 26, v.y(last.shoe), v.xr(hd) + 26, v.y(last.shoe) + 30))

    # 2) annulus fluids and cement
    cem_img = cement_texture()
    for i, s in enumerate(strings):
        a = _alpha(st, s.key) * alpha
        if a <= 0.01:
            continue
        ext = st.string_extent.get(s.key, 1.0)
        bot = s.top + (s.shoe - s.top) * ext
        # annulus outside this string from top to TOC: fluid ; TOC to shoe: cement
        segs = _annulus_segments(st, i, s.top, bot)
        cf = st.cement_fill.get(s.key, 1.0)
        toc_eff = s.shoe - (s.shoe - (s.toc if s.toc is not None else s.shoe)) * cf
        for (d0, d1, outer) in segs:
            xo_l, xo_r = v.xl(outer), v.xr(outer)
            xi_l, xi_r = v.xl(s.od), v.xr(s.od)
            # fluid part
            f0, f1 = d0, min(d1, toc_eff)
            if f1 > f0:
                fl = st.annulus_fluid if not (s.key == "prod" and st.a_annulus_fluid is not None and False) else st.annulus_fluid
                for (xa, xb) in ((xo_l, xi_l), (xi_r, xo_r)):
                    c.drawRect(skia.Rect(xa, v.y(f0), xb, v.y(f1)), paint(fl, 0.75 * a))
            # cement part
            c0, c1 = max(d0, toc_eff), d1
            if c1 > c0 and cf > 0:
                cp = skia.Paint(AntiAlias=False, Shader=image_shader(cem_img, 0.5))
                cp.setAlphaf(a)
                for (xa, xb) in ((xo_l, xi_l), (xi_r, xo_r)):
                    c.drawRect(skia.Rect(xa, v.y(c0), xb, v.y(c1)), cp)
                    v.reg(f"cement_{s.key}", rect_path(xa, v.y(c0), xb, v.y(c1)))

    # 3) bore fluid inside innermost present string + open hole
    inner = present[-1] if present else None
    if inner is not None:
        top_fluid = max(0.0, st.fluid_level)
        # inside each string from its top to shoe (only the innermost at that depth)
        for d0, d1, dia in _bore_segments(st):
            y0, y1 = v.y(max(d0, top_fluid)), v.y(d1)
            if y1 > y0:
                c.drawRect(skia.Rect(v.xl(dia), y0, v.xr(dia), y1), paint(st.bore_fluid, st.bore_fluid_alpha * alpha))
                _cyl_shade(c, v.xl(dia), y0, v.xr(dia), y1, alpha)
                v.reg("bore_fluid", rect_path(v.xl(dia), y0, v.xr(dia), y1))

    # 3b) fluid overlays (kill mud fronts, influx etc.)
    for ov in st.overlays:
        if ov["d1"] <= ov["d0"]:
            continue
        if ov["kind"] == "dp":
            dia = 4.67
            c.drawRect(skia.Rect(v.xl(dia), v.y(ov["d0"]), v.xr(dia), v.y(ov["d1"])), paint(ov["color"], ov.get("alpha", 0.95) * alpha))
        else:
            for d0, d1, dia in _bore_segments(st):
                a0, a1 = max(d0, ov["d0"]), min(d1, ov["d1"])
                if a1 > a0:
                    c.drawRect(skia.Rect(v.xl(dia), v.y(a0), v.xr(dia), v.y(a1)), paint(ov["color"], ov.get("alpha", 0.95) * alpha))
                    if ov.get("keep_dp") is not None:
                        c.drawRect(skia.Rect(v.xl(4.67), v.y(a0), v.xr(4.67), v.y(a1)), paint(ov["keep_dp"], 0.95 * alpha))

    # 4) casing walls
    for i, s in enumerate(strings):
        a = _alpha(st, s.key) * alpha
        if a <= 0.01:
            continue
        ext = st.string_extent.get(s.key, 1.0)
        top = s.top
        bot = s.top + (s.shoe - s.top) * ext
        wall = max(2.6, (s.od - s.id) * 0.5 * v.sx)
        for side in (-1, 1):
            xo = v.ax + side * v.r(s.od)
            xi = xo - side * wall
            x0, x1 = min(xo, xi), max(xo, xi)
            pth = rect_path(x0, v.y(top), x1, v.y(bot))
            c.drawRect(skia.Rect(x0, v.y(top), x1, v.y(bot)), steel_paint(x0, x1, a))
            v.reg(f"casing_{s.key}", pth)
            # shoe triangle
            if ext >= 0.999:
                ys = v.y(bot)
                tri = poly([(xo, ys - 9), (xo + side * 9, ys), (xo, ys)], close=True)
                c.drawPath(tri, paint(C.steel_hi, a))
        if s.key == "liner" and st.completion >= 0 and a > 0.01:
            # liner hanger / liner top packer
            yl = v.y(s.top)
            outer_id = next((o.id for o in strings if o.key == "prod"), 8.535)
            for side in (-1, 1):
                xa = v.ax + side * v.r(s.od)
                xb = v.ax + side * v.r(outer_id)
                r = skia.Rect(min(xa, xb), yl - 3, max(xa, xb), yl + 9)
                c.drawRect(r, paint(rgb("#2C2C30"), a))
                c.drawRect(skia.Rect(r.left(), r.top(), r.right(), r.top() + 3), paint(C.steel_hi, a))
                v.reg("liner_top_packer", rect_path(r.left(), r.top(), r.right(), r.bottom()))

    # 5) perforations
    if st.perforations > 0:
        liner = next((s for s in strings if s.key == "liner"), None)
        dia_in = liner.od if liner else 9.625
        hole = 8.5
        n = 9
        for k in range(n):
            d = st.perf_top + (st.perf_base - st.perf_top) * (k + 0.5) / n
            y = v.y(d)
            ln = v.r(hole) - v.r(dia_in) + 26
            for side in (-1, 1):
                x0 = v.ax + side * (v.r(dia_in) - 3)
                pa = clamp(st.perforations * 1.5 - k * 0.05)
                tunnel = poly([(x0, y - 2.5), (x0 + side * ln * pa, y - 0.8), (x0 + side * ln * pa, y + 0.8), (x0, y + 2.5)], close=True)
                c.drawPath(tunnel, paint(rgb("#120E0A"), alpha))
                c.drawPath(tunnel, paint(C.amber, 0.35 * alpha * pa, stroke=1))

    # 6) completion: tubing, packer, DHSV
    if st.completion > 0:
        draw_completion(c, v, st, t, alpha)

    # 7) drill string
    if st.drillstring > 0:
        draw_drillstring(c, v, st, t, alpha * st.drillstring)

    # 8) plugs
    for pl in st.plugs:
        draw_plug(c, v, st, pl, alpha)


def _annulus_segments(st: WellState, idx: int, d0: float, d1: float):
    """Split [d0,d1] outside string idx into pieces with constant outer diameter."""
    cuts = {d0, d1}
    for j in range(idx):
        o = st.strings[j]
        if _alpha(st, o.key) > 0.5:
            for d in (o.top, o.shoe):
                if d0 < d < d1:
                    cuts.add(d)
    cuts = sorted(cuts)
    out = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        m = (a + b) / 2
        out.append((a, b, _outer_boundary(st, idx, m)))
    return out


def _bore_segments(st: WellState):
    """Inner bore: for each depth range, the innermost present string's ID, or open hole."""
    present = [s for s in st.strings if _alpha(st, s.key) > 0.5]
    cuts = {0.0, st.hole_td}
    for s in present:
        cuts.update([s.top, s.shoe])
    cuts = sorted(c for c in cuts if c <= st.hole_td)
    out = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        m = (a + b) / 2
        dia = None
        for s in present:
            ext = st.string_extent.get(s.key, 1.0)
            if s.top <= m <= s.top + (s.shoe - s.top) * ext:
                dia = s.id if dia is None else min(dia, s.id)
        if dia is None:
            # open hole: the hole drilled for the string whose section contains this depth
            dia = None
            prev = 0.0
            for s in st.strings:
                if prev <= m <= s.shoe:
                    dia = s.hole
                    break
                prev = s.shoe
            if dia is None:
                dia = st.strings[-1].hole * 0.75
        out.append((a, b, dia))
    return out


def draw_completion(c, v: WellView, st: WellState, t, alpha):
    comp = ease_in_out(st.completion)
    # tubing slides in from surface
    tail = st.tubing_tail * comp
    od, idd = st.tubing_od, st.tubing_id
    wall = max(2.4, (od - idd) * 0.5 * v.sx)
    # A-annulus packer fluid (between tubing and prod casing above packer)
    if st.a_annulus_fluid is not None and comp > 0.98:
        prod = next(s for s in st.strings if s.key == "prod")
        for side in (-1, 1):
            xa = v.ax + side * v.r(od)
            xb = v.ax + side * v.r(prod.id)
            c.drawRect(skia.Rect(min(xa, xb), v.y(0), max(xa, xb), v.y(st.packer_depth)), paint(st.a_annulus_fluid, 0.9 * alpha))
            v.reg("a_annulus", rect_path(min(xa, xb), v.y(0), max(xa, xb), v.y(st.packer_depth)))
    # tubing content
    c.drawRect(skia.Rect(v.xl(idd), v.y(0), v.xr(idd), v.y(tail)), paint(st.tubing_fluid, 0.9 * alpha))
    for side in (-1, 1):
        xo = v.ax + side * v.r(od)
        xi = xo - side * wall
        x0, x1 = min(xo, xi), max(xo, xi)
        c.drawRect(skia.Rect(x0, v.y(0), x1, v.y(tail)), steel_paint(x0, x1, alpha))
        v.reg("tubing", rect_path(x0, v.y(0), x1, v.y(tail)))
    # packer
    yp = v.y(st.packer_depth * comp + (1 - comp) * 0)
    if comp > 0.98:
        prod = next(s for s in st.strings if s.key == "prod")
        ph = 22
        for side in (-1, 1):
            xa = v.ax + side * v.r(od)
            xb = v.ax + side * v.r(prod.id)
            x0, x1 = min(xa, xb), max(xa, xb)
            body = skia.Rect(x0, yp - ph / 2, x1, yp + ph / 2)
            c.drawRect(body, paint(rgb("#25252A"), alpha))
            # rubber element
            c.drawRect(skia.Rect(x0, yp - 5, x1, yp + 5), paint(rgb("#111114"), alpha))
            # slips
            for k in range(3):
                yy = yp - ph / 2 + 2 + k * 3
                c.drawLine(x0, yy, x1, yy, paint(C.steel_hi, 0.5 * alpha, stroke=1))
            v.reg("packer", rect_path(x0, yp - ph / 2, x1, yp + ph / 2))
    # DHSV
    if comp > 0.15:
        yd = v.y(st.dhsv_depth)
        hh = 26
        bw = v.r(od) + 7
        body = skia.Rect(v.ax - bw, yd - hh / 2, v.ax + bw, yd + hh / 2)
        c.drawRoundRect(body, 5, 5, paint(rgb("#3A4352"), alpha))
        c.drawRoundRect(body, 5, 5, paint(C.steel_hi, 0.5 * alpha, stroke=1.2))
        # flapper: open = vertical along wall, closed = horizontal across bore
        ang = (1 - st.dhsv_open) * 90
        pivot_x, pivot_y = v.ax - v.r(idd) + 1, yd + hh / 2 - 3
        L = 2 * v.r(idd) - 2
        a = math.radians(-90 + ang)
        fx, fy = pivot_x + L * math.cos(a), pivot_y + L * math.sin(a)
        c.drawLine(pivot_x, pivot_y, fx, fy, paint(C.amber if st.dhsv_open < 0.5 else C.steel_hi, alpha, stroke=4))
        v.reg("dhsv", rect_path(body.left(), body.top(), body.right(), body.bottom()))


def draw_drillstring(c, v: WellView, st: WellState, t, alpha):
    bit = st.bit_depth
    dp_od, dp_id = 5.5, 4.67
    dc_od = 6.75
    bha_top = bit - 180
    # drill pipe
    for (d0, d1, od) in ((0, bha_top, dp_od), (bha_top, bit - 8, dc_od)):
        wall = max(2.2, 0.55 * v.sx)
        for side in (-1, 1):
            xo = v.ax + side * v.r(od)
            xi = xo - side * wall
            x0, x1 = min(xo, xi), max(xo, xi)
            c.drawRect(skia.Rect(x0, v.y(d0), x1, v.y(d1)), steel_paint(x0, x1, alpha))
            v.reg("drillstring", rect_path(x0, v.y(d0), x1, v.y(d1)))
        # tool joints: small upsets on the pipe OD every joint (subtle motion with rotation)
        y0, y1 = v.y(d0), v.y(d1)
        step = 34.0
        off = (st.rotation * 6) % step
        yy = y0 + off
        while yy < y1 - 6:
            for side in (-1, 1):
                xo = v.ax + side * v.r(od)
                c.drawRect(skia.Rect(min(xo, xo + side * 2.5), yy, max(xo, xo + side * 2.5), yy + 7), paint(C.steel_hi, 0.75 * alpha))
            yy += step
    # bit
    yb = v.y(bit)
    bw = v.r(8.5) - 1
    bitp = poly([(v.ax - bw, yb - 14), (v.ax + bw, yb - 14), (v.ax + bw * 0.8, yb - 2), (v.ax, yb + 2), (v.ax - bw * 0.8, yb - 2)], close=True)
    c.drawPath(bitp, paint(rgb("#B9BEC6"), alpha))
    c.drawPath(bitp, paint(rgb("#2B2F36"), alpha, stroke=1.2))
    v.reg("bit", bitp)


def draw_plug(c, v: WellView, st: WellState, pl: dict, alpha):
    a = pl.get("alpha", 1.0) * alpha
    if a <= 0.01:
        return
    top, base = pl["top"], pl["base"]
    fill = pl.get("fill", 1.0)
    kind = pl.get("kind", "cement")
    dia = pl.get("dia")
    if dia is None:
        # innermost present string at mid-depth
        segs = _bore_segments(st)
        m = (top + base) / 2
        dia = next((dd for (a0, b0, dd) in segs if a0 <= m <= b0), 8.5)
    cur_top = base - (base - top) * fill
    x0, x1 = v.xl(dia), v.xr(dia)
    if kind == "cement":
        cp = skia.Paint(AntiAlias=False, Shader=image_shader(cement_texture(), 0.5))
        cp.setAlphaf(a)
        c.drawRect(skia.Rect(x0, v.y(cur_top), x1, v.y(base)), cp)
        if pl.get("glow"):
            c.drawRect(skia.Rect(x0, v.y(cur_top), x1, v.y(base)), paint(pl["glow"], 0.25 * a))
    elif kind == "mechanical":
        r = skia.Rect(x0, v.y(top), x1, v.y(base))
        c.drawRect(r, paint(rgb("#2A2D33"), a))
        for k in range(4):
            yy = r.top() + (k + 0.5) * r.height() / 4
            c.drawLine(x0, yy, x1, yy, paint(C.steel_hi, 0.4 * a, stroke=1))
    elif kind == "bismuth":
        c.drawRect(skia.Rect(x0, v.y(cur_top), x1, v.y(base)), paint(rgb("#B7B9C8"), a))
    if pl.get("key"):
        v.reg(pl["key"], rect_path(x0, v.y(cur_top), x1, v.y(base)))


def _cyl_shade(c, x0, y0, x1, y1, alpha=1.0):
    p = skia.Paint()
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(x0, 0), skia.Point(x1, 0)],
                                               [with_alpha(C.black, 0.45 * alpha), with_alpha(C.black, 0.0),
                                                with_alpha(C.white, 0.06 * alpha), with_alpha(C.black, 0.0),
                                                with_alpha(C.black, 0.45 * alpha)], [0, 0.25, 0.45, 0.7, 1]))
    c.drawRect(skia.Rect(x0, y0, x1, y1), p)


# --------------------------------------------------------------- depth-ranged regions
def string_by_key(st: WellState, key: str) -> Casing:
    return next(s for s in st.strings if s.key == key)


def region_casing(v: WellView, st: WellState, key: str, d0: float, d1: float) -> skia.Path:
    s = string_by_key(st, key)
    d0, d1 = max(d0, s.top), min(d1, s.shoe)
    wall = max(2.6, (s.od - s.id) * 0.5 * v.sx)
    p = skia.Path()
    for side in (-1, 1):
        xo = v.ax + side * v.r(s.od)
        xi = xo - side * wall
        p.addRect(skia.Rect(min(xo, xi), v.y(d0), max(xo, xi), v.y(d1)))
    return p


def region_cement(v: WellView, st: WellState, key: str, d0: float, d1: float) -> skia.Path:
    idx = next(i for i, s in enumerate(st.strings) if s.key == key)
    s = st.strings[idx]
    toc = s.toc if s.toc is not None else s.shoe
    d0, d1 = max(d0, toc), min(d1, s.shoe)
    p = skia.Path()
    if d1 <= d0:
        return p
    for (a, b, outer) in _annulus_segments(st, idx, d0, d1):
        for (xa, xb) in ((v.xl(outer), v.xl(s.od)), (v.xr(s.od), v.xr(outer))):
            p.addRect(skia.Rect(xa, v.y(a), xb, v.y(b)))
    return p


def region_formation(v: WellView, st: WellState, key: str, d0: float, d1: float, width: float = 34) -> skia.Path:
    """Strip of formation immediately outside the hole of string `key` between d0 and d1."""
    s = string_by_key(st, key)
    p = skia.Path()
    hw = v.r(s.hole)
    for side in (-1, 1):
        xa = v.ax + side * hw
        xb = xa + side * width
        p.addRect(skia.Rect(min(xa, xb), v.y(d0), max(xa, xb), v.y(d1)))
    return p


def region_bore(v: WellView, st: WellState, d0: float, d1: float, dia: float) -> skia.Path:
    return rect_path(v.xl(dia), v.y(d0), v.xr(dia), v.y(d1))


def highlight_path(c, pth: skia.Path, color, alpha=1.0, glow=True, fill=0.55):
    if alpha <= 0.01 or pth is None or pth.isEmpty():
        return
    if glow:
        c.drawPath(pth, paint(color, 0.45 * alpha, blur=10))
    c.drawPath(pth, paint(color, fill * alpha))
    c.drawPath(pth, paint(mix(color, C.white, 0.5), 0.9 * alpha, stroke=1.4))


# --------------------------------------------------------------- surface equipment
def draw_wellhead(c, v: WellView, alpha=1.0, y=None):
    """Wellhead housing at depth 0. Returns top y."""
    y = v.y(0) if y is None else y
    w = v.r(30) + 16
    h = 46
    body = skia.Rect(v.ax - w, y - h, v.ax + w, y + 6)
    p = steel_paint(body.left(), body.right(), alpha)
    c.drawRoundRect(body, 6, 6, p)
    c.drawRoundRect(body, 6, 6, paint(C.black, 0.4 * alpha, stroke=1.2))
    # flange lines
    for k in range(3):
        yy = y - h + 8 + k * 14
        c.drawLine(body.left() + 4, yy, body.right() - 4, yy, paint(C.black, 0.25 * alpha, stroke=1))
    v.reg("wellhead", rect_path(body.left(), body.top(), body.right(), body.bottom()))
    # annulus access valve (side outlet) on the right
    ox = body.right()
    oy = y - 20
    c.drawRect(skia.Rect(ox, oy - 7, ox + 52, oy + 7), steel_paint(ox, ox + 52, alpha))
    vb = skia.Rect(ox + 52, oy - 15, ox + 82, oy + 15)
    c.drawRoundRect(vb, 4, 4, paint(rgb("#3D4656"), alpha))
    c.drawRoundRect(vb, 4, 4, paint(C.steel_hi, 0.5 * alpha, stroke=1))
    c.drawLine(ox + 67, oy - 15, ox + 67, oy - 30, paint(C.steel_hi, alpha, stroke=3))
    c.drawCircle(ox + 67, oy - 32, 8, paint(C.steel_hi, alpha, stroke=2.5))
    v.reg("annulus_valve", rect_path(ox, oy - 34, ox + 82, oy + 15))
    # tubing hanger region (inside housing)
    th = skia.Rect(v.ax - v.r(9.6), y - h + 8, v.ax + v.r(9.6), y - 4)
    v.reg("tubing_hanger", rect_path(th.left(), th.top(), th.right(), th.bottom()))
    return y - h


def draw_tubing_hanger(c, v, alpha=1.0, y=None):
    y = v.y(0) if y is None else y
    th = skia.Rect(v.ax - v.r(9.4), y - 36, v.ax + v.r(9.4), y - 8)
    c.drawRect(th, paint(rgb("#2B3340"), alpha))
    c.drawRect(th, paint(C.steel_hi, 0.6 * alpha, stroke=1.2))


def _valve(c, x, y, w, h, alpha, closed=0.0, actuator=False, color=None):
    body = skia.Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
    c.drawRoundRect(body, 5, 5, steel_paint(body.left(), body.right(), alpha, tint=color))
    c.drawRoundRect(body, 5, 5, paint(C.black, 0.45 * alpha, stroke=1.2))
    # gate indicator
    gc = mix(C.green, C.red, closed)
    c.drawCircle(x, y, 5, paint(gc, alpha))
    return body


def draw_tree(c, v: WellView, st: WellState, alpha=1.0, y_base=None):
    """Vertical dry Christmas tree on top of the wellhead."""
    y = (v.y(0) - 46) if y_base is None else y_base
    bw = v.r(9.0) + 18
    # main block
    blocks = [("lmv", "Lower master valve", 0), ("umv", "Upper master valve", 1), ("cross", "", 2), ("swab", "Swab valve", 3)]
    hh = 42
    for k, (key, name, idx) in enumerate(blocks):
        yc = y - hh / 2 - idx * (hh + 6)
        if key == "cross":
            body = skia.Rect(v.ax - bw, yc - hh / 2, v.ax + bw, yc + hh / 2)
            c.drawRect(body, steel_paint(body.left(), body.right(), alpha))
            # wing valve to the left (production)
            wx = v.ax - bw - 70
            c.drawRect(skia.Rect(wx, yc - 8, v.ax - bw, yc + 8), steel_paint(wx, v.ax - bw, alpha))
            b = _valve(c, wx + 8, yc, 34, 36, alpha, st.tree_valves_closed.get("pwv", 0.0))
            v.reg("pwv", rect_path(b.left(), b.top(), b.right(), b.bottom()))
            # flowline
            c.drawRect(skia.Rect(wx - 160, yc - 7, wx - 9, yc + 7), steel_paint(wx - 160, wx, alpha))
            # kill wing to the right
            kx = v.ax + bw
            c.drawRect(skia.Rect(kx, yc - 7, kx + 50, yc + 7), steel_paint(kx, kx + 50, alpha))
            b2 = _valve(c, kx + 50, yc, 30, 32, alpha, st.tree_valves_closed.get("kwv", 1.0))
            v.reg("kwv", rect_path(b2.left(), b2.top(), b2.right(), b2.bottom()))
            v.reg("tree", rect_path(body.left(), body.top(), body.right(), body.bottom()))
        else:
            b = _valve(c, v.ax, yc, 2 * bw, hh, alpha, st.tree_valves_closed.get(key, 0.0))
            v.reg(key, rect_path(b.left(), b.top(), b.right(), b.bottom()))
            v.reg("tree", rect_path(b.left(), b.top(), b.right(), b.bottom()))
            # handwheel / actuator
            if key == "umv":
                c.drawRoundRect(skia.Rect(v.ax + bw, yc - 14, v.ax + bw + 40, yc + 14), 6, 6, paint(rgb("#B23A3A"), alpha))
            else:
                c.drawLine(v.ax + bw, yc, v.ax + bw + 22, yc, paint(C.steel_hi, alpha, stroke=3))
                c.drawCircle(v.ax + bw + 28, yc, 9, paint(C.steel_hi, alpha, stroke=2.5))
    top = y - 4 * (hh + 6)
    # tree cap
    c.drawRoundRect(skia.Rect(v.ax - bw * 0.7, top - 18, v.ax + bw * 0.7, top + 4), 5, 5, steel_paint(v.ax - bw, v.ax + bw, alpha))
    return top - 18


def draw_bop(c, v: WellView, st: WellState, alpha=1.0, y_base=None):
    """BOP stack: annular on top, blind/shear ram, two pipe rams."""
    y = (v.y(0) - 46) if y_base is None else y_base
    bw = v.r(18.75) + 24
    rams = [("pipe_ram_lower", "Pipe ram", 1.0), ("pipe_ram_upper", "Pipe ram", 1.0), ("shear_ram", "Blind/shear ram", 0.0)]
    hh = 44
    close = ease_in_out(st.bop_close)
    yc = y
    pipe_r = v.r(5.5)
    for k, (key, name, pipe) in enumerate(rams):
        yc = y - hh / 2 - k * (hh + 4)
        body = skia.Rect(v.ax - bw, yc - hh / 2, v.ax + bw, yc + hh / 2)
        c.drawRect(body, steel_paint(body.left(), body.right(), alpha, tint=rgb("#B3262E")))
        c.drawRect(body, paint(C.black, 0.4 * alpha, stroke=1.2))
        # ram bonnets left/right
        for side in (-1, 1):
            bx = v.ax + side * bw
            c.drawRect(skia.Rect(min(bx, bx + side * 46), yc - hh / 2 + 6, max(bx, bx + side * 46), yc + hh / 2 - 6),
                       steel_paint(min(bx, bx + side * 46), max(bx, bx + side * 46), alpha, tint=rgb("#B3262E")))
        # ram blocks inside (closing toward pipe)
        if key.startswith("pipe") and k == 0:
            gap = lerp(bw - 8, pipe_r + 1, close)
            for side in (-1, 1):
                x_in = v.ax + side * gap
                x_out = v.ax + side * (bw - 4)
                c.drawRect(skia.Rect(min(x_in, x_out), yc - 10, max(x_in, x_out), yc + 10), paint(rgb("#1A1A1E"), alpha))
        v.reg(key, rect_path(body.left(), body.top(), body.right(), body.bottom()))
        v.reg("bop", rect_path(body.left(), body.top(), body.right(), body.bottom()))
    # annular preventer on top
    ya = yc - hh / 2 - 4 - 34
    ann = skia.Path()
    ann.moveTo(v.ax - bw, ya + 34)
    ann.lineTo(v.ax - bw, ya + 12)
    ann.quadTo(v.ax - bw, ya - 8, v.ax - bw * 0.5, ya - 10)
    ann.lineTo(v.ax + bw * 0.5, ya - 10)
    ann.quadTo(v.ax + bw, ya - 8, v.ax + bw, ya + 12)
    ann.lineTo(v.ax + bw, ya + 34)
    ann.close()
    p = steel_paint(v.ax - bw, v.ax + bw, alpha, tint=rgb("#B3262E"))
    c.drawPath(ann, p)
    c.drawPath(ann, paint(C.black, 0.4 * alpha, stroke=1.2))
    v.reg("annular", ann)
    v.reg("bop", ann)
    # choke & kill lines
    for side, name in ((-1, "choke"), (1, "kill")):
        x0 = v.ax + side * (bw + 46)
        yy = y - hh * 1.5
        c.drawRect(skia.Rect(min(x0, x0 + side * 70), yy - 5, max(x0, x0 + side * 70), yy + 5), steel_paint(x0, x0 + side * 70, alpha))
    return ya - 10


def draw_rcd(c, v: WellView, y_base: float, alpha=1.0):
    """Rotating control device on top of the BOP (MPD)."""
    bw = v.r(18.75) + 4
    body = skia.Rect(v.ax - bw, y_base - 40, v.ax + bw, y_base)
    c.drawRoundRect(body, 6, 6, steel_paint(body.left(), body.right(), alpha, tint=rgb("#2F6F8F")))
    c.drawRoundRect(body, 6, 6, paint(C.black, 0.4 * alpha, stroke=1.2))
    # flow spool to choke manifold
    c.drawRect(skia.Rect(v.ax + bw, y_base - 26, v.ax + bw + 120, y_base - 14), steel_paint(v.ax + bw, v.ax + bw + 120, alpha))
    v.reg("rcd", rect_path(body.left(), body.top(), body.right(), body.bottom()))
    return y_base - 40


def draw_pce(c, v: WellView, y_base: float, alpha=1.0, tool_depth: float | None = None):
    """Wireline pressure control equipment on top of the tree."""
    bw = v.r(6.0) + 6
    # wireline BOP
    bop = skia.Rect(v.ax - bw - 10, y_base - 46, v.ax + bw + 10, y_base)
    c.drawRect(bop, steel_paint(bop.left(), bop.right(), alpha, tint=rgb("#B3262E")))
    c.drawRect(bop, paint(C.black, 0.4 * alpha, stroke=1.2))
    v.reg("wl_bop", rect_path(bop.left(), bop.top(), bop.right(), bop.bottom()))
    # lubricator
    lub = skia.Rect(v.ax - bw * 0.7, y_base - 46 - 150, v.ax + bw * 0.7, y_base - 46)
    c.drawRect(lub, steel_paint(lub.left(), lub.right(), alpha))
    v.reg("lubricator", rect_path(lub.left(), lub.top(), lub.right(), lub.bottom()))
    # stuffing box / grease head
    sb = skia.Rect(v.ax - bw * 0.55, lub.top() - 26, v.ax + bw * 0.55, lub.top())
    c.drawRoundRect(sb, 5, 5, steel_paint(sb.left(), sb.right(), alpha, tint=rgb("#B8860B")))
    v.reg("stuffing_box", rect_path(sb.left(), sb.top(), sb.right(), sb.bottom()))
    # sheave and wire
    c.drawCircle(v.ax + 14, sb.top() - 22, 16, paint(C.steel_hi, alpha, stroke=3))
    c.drawLine(v.ax + 30, sb.top() - 22, v.ax + 160, sb.top() + 40, paint(C.steel_hi, 0.8 * alpha, stroke=1.4))
    if tool_depth is not None:
        y_tool = v.y(tool_depth)
        c.drawLine(v.ax, sb.top() - 6, v.ax, y_tool - 30, paint(C.steel_hi, 0.9 * alpha, stroke=1.4))
        c.drawRoundRect(skia.Rect(v.ax - 6, y_tool - 30, v.ax + 6, y_tool + 30), 3, 3, paint(rgb("#C9A227"), alpha))
    return sb.top() - 40


def draw_surface(c, v: WellView, st: WellState, alpha=1.0):
    if st.surface == "none":
        return v.y(0)
    top = draw_wellhead(c, v, alpha * st.surface_alpha)
    if st.completion > 0.98:
        draw_tubing_hanger(c, v, alpha * st.surface_alpha)
    if st.surface == "tree":
        return draw_tree(c, v, st, alpha * st.surface_alpha)
    if st.surface == "bop":
        # drill pipe through the stack
        if st.drillstring > 0:
            y1 = v.y(0)
            for side in (-1, 1):
                xo = v.ax + side * v.r(5.5)
                xi = xo - side * 2.4
                c.drawRect(skia.Rect(min(xo, xi), y1 - 260, max(xo, xi), y1), steel_paint(min(xo, xi), max(xo, xi), alpha))
        return draw_bop(c, v, st, alpha * st.surface_alpha)
    return top


# --------------------------------------------------------------- highlights
def highlight(c, v: WellView, key: str, color, alpha=1.0, glow=True, fill=0.55):
    if alpha <= 0.01 or key not in v.regions:
        return
    pth = v.regions[key]
    if glow:
        c.drawPath(pth, paint(color, 0.45 * alpha, blur=10))
    c.drawPath(pth, paint(color, fill * alpha))
    c.drawPath(pth, paint(mix(color, C.white, 0.5), 0.9 * alpha, stroke=1.4))


def depth_scale(c, v: WellView, x, depths=(0, 500, 1000, 1500, 2000, 2500, 3000), alpha=1.0, label="Depth (m)"):
    if alpha <= 0:
        return
    c.drawLine(x, v.y(depths[0]), x, v.y(depths[-1]), paint(C.muted, 0.6 * alpha, stroke=1.2))
    for d in depths:
        y = v.y(d)
        c.drawLine(x - 6, y, x, y, paint(C.muted, 0.8 * alpha, stroke=1.2))
        draw_text(c, f"{d:,}".replace(",", " "), x - 10, y + 6, 16, C.muted, 500, alpha, "right")
    draw_text(c, label, x - 10, v.y(depths[0]) - 18, 15, C.dim, 600, alpha, "right")
    draw_text(c, "not to scale", x - 10, v.y(depths[-1]) + 26, 13, C.dim, 400, alpha, "right", italic=True)
