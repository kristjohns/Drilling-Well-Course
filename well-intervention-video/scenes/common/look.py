"""The visual style: how each primitive is drawn, by role.

Roles are inferred from the primitive and its colour (one meaning per colour, see palette.py), or given explicitly:
  card   rounded panel with a soft shadow, a faint top-lit gradient and a hairline border (PANEL / PANEL2 rects)
  pill   fully rounded label plate
  steel  casing / pipe: a cylindrical metallic gradient across the short axis
  earth  rock / seabed / shale with a world-anchored grain + strata texture;  sand: a speckled grain texture
  sea    a vertical gradient with faint caustics
  fluid  mud / cement / spacer / formation fluids: a soft cylindrical sheen (cement gets a fine grain)
  hair   thin rules (grid lines, axes, ticks)
  shaft / head  arrows: round-capped shaft, softened head, glow when the colour is an accent
  curve  polylines: round caps/joins; accent curves glow and show a bright tip while being drawn on
  orb    accent dots / bubbles: radial gradient + glow
  text   Inter (sans/bold), JetBrains Mono (mono), with a soft drop shadow for legibility over artwork
  solid / flat / hole  plain fills (machinery bodies, generic blocks, the open borehole)
"""
from __future__ import annotations
import math

import numpy as np
import skia

from . import palette as P
from .stage import hex_rgb, ease_out, W as WORLD_W

FONT_FILES = {
    "sans": "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    "bold": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
    "display": "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf",
    "mono": "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf",
    "fallback": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "fallback_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}


def _h(c):
    return c.lower() if isinstance(c, str) else c


ACCENTS = {_h(c) for c in (P.PORE, P.FRAC, P.MUD, P.WARN, P.BAD, P.OIL, P.GAS, P.SAFE, P.WATER, P.COLLAPSE,
                           P.PRIMARY_B, P.SECOND_B, P.KILL_MUD, P.NO_BADGE, P.ACID, P.N2, P.GREASE)}
CARDS = {_h(P.PANEL), _h(P.PANEL2)}
STEELS = {_h(P.STEEL), _h(P.STEEL_DK), _h(P.WIRE), _h(P.COPPER), "#56667d", "#71839c", "#98a9bf", "#c9d4e1"}
EARTH = {_h(P.ROCK), _h(P.ROCK2), _h(P.SEABED), _h(P.SHALE)}
FLUIDS = {_h(P.MUD), _h(P.KILL_MUD), _h(P.CEMENT), _h(P.SPACER), _h(P.WATER), _h(P.OIL), _h(P.GAS), _h(P.ACID), _h(P.N2),
          _h(P.GREASE), _h(P.SCALE), _h(P.WAX), _h(P.HYDRATE)}


def _hexof(rgb):
    return "#%02x%02x%02x" % tuple(int(round(max(0, min(1, c)) * 255)) for c in rgb[:3])


def _mix(rgb, target, f):
    return tuple(a + (b - a) * f for a, b in zip(rgb, target))


def lighten(rgb, f):
    return _mix(rgb, (1.0, 1.0, 1.0), f)


def darken(rgb, f):
    return _mix(rgb, (0.0, 0.0, 0.0), f)


def col(rgb, a=1.0):
    r, g, b = rgb[:3]
    return skia.Color4f(float(r), float(g), float(b), float(max(0.0, min(1.0, a)))).toColor()


# ---------------------------------------------------------------------------------------------- textures
def _value_noise(n, cells, seed):
    """Tileable value noise in [0,1], n x n, `cells` lattice cells per side."""
    rng = np.random.default_rng(seed)
    lat = rng.random((cells, cells))
    x = np.arange(n) * cells / n
    i0 = np.floor(x).astype(int) % cells
    i1 = (i0 + 1) % cells
    f = x - np.floor(x)
    f = f * f * (3 - 2 * f)
    a = lat[i0][:, i0] * (1 - f)[None, :] + lat[i0][:, i1] * f[None, :]
    b = lat[i1][:, i0] * (1 - f)[None, :] + lat[i1][:, i1] * f[None, :]
    return a * (1 - f)[:, None] + b * f[:, None]


def _fbm(n, seed, octaves=(4, 8, 16, 32, 64), gain=0.55):
    out = np.zeros((n, n))
    amp, tot = 1.0, 0.0
    for k, c in enumerate(octaves):
        out += amp * _value_noise(n, c, seed + k)
        tot += amp
        amp *= gain
    return out / tot


def _rgba_image(arr):
    arr = np.ascontiguousarray(arr.astype(np.uint8))
    return skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType)


def make_textures(n=256):
    tex = {}
    # earth: low-frequency mottling + thin sedimentary strata (dark, alpha-coded) and a few light flecks
    m = _fbm(n, 11)
    yy = np.arange(n)[:, None] / n
    strata = 0.5 + 0.5 * np.sin((yy * 9 + 0.35 * _fbm(n, 21, (4, 8))) * 2 * np.pi)
    dark = np.clip((m - 0.45) * 0.9 + 0.18 * strata ** 6, 0, 1)
    a = np.zeros((n, n, 4))
    a[..., 3] = dark * 120
    rng = np.random.default_rng(5)
    fl = rng.random((n, n)) > 0.996
    light = np.zeros((n, n, 4))
    light[..., :3] = 255
    light[..., 3] = fl * 60
    tex["earth_dark"] = _rgba_image(a)
    tex["earth_light"] = _rgba_image(light)
    # sand: dense speckles
    g = rng.random((n, n))
    sp = np.zeros((n, n, 4))
    sp[..., 3] = np.where(g > 0.93, 70, 0) + np.where(g < 0.05, 0, 0)
    tex["sand_dark"] = _rgba_image(sp)
    lt = np.zeros((n, n, 4))
    lt[..., :3] = 255
    lt[..., 3] = np.where(g < 0.035, 80, 0)
    tex["sand_light"] = _rgba_image(lt)
    # cement: fine low-contrast grain
    c = _fbm(n, 31, (32, 64, 128))
    cg = np.zeros((n, n, 4))
    cg[..., 3] = np.clip((c - 0.5) * 2.2, 0, 1) * 55
    tex["cement"] = _rgba_image(cg)
    # sea: soft caustic veins
    s = _fbm(n, 41, (6, 12, 24))
    ca = np.zeros((n, n, 4))
    ca[..., :3] = 255
    ca[..., 3] = np.clip(1 - np.abs(s - 0.5) * 9, 0, 1) * 22
    tex["sea"] = _rgba_image(ca)
    return tex


# ---------------------------------------------------------------------------------------------- the look
class Look:
    _cache: dict = {}

    @classmethod
    def get(cls, res):
        if res not in cls._cache:
            cls._cache[res] = Look(res)
        return cls._cache[res]

    def __init__(self, res):
        self.w, self.h = res
        self.k0 = self.w / WORLD_W                     # px per world unit at the default zoom
        self.buf = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        self.surface = skia.Surface(self.buf, colorType=skia.kRGBA_8888_ColorType)
        self.tf = {k: skia.Typeface.MakeFromFile(v) for k, v in FONT_FILES.items()}
        self.tex = make_textures()
        self.background = self._make_background()
        self._glyph_ok: dict = {}

    # ------------------------------------------------------------------ background
    def _make_background(self):
        w, h = self.w, self.h
        surf = skia.Surface(w, h)
        c = surf.getCanvas()
        bg = hex_rgb(P.BG)
        centre = lighten(bg, 0.055)
        edge = darken(bg, 0.35)
        paint = skia.Paint(Shader=skia.GradientShader.MakeRadial(
            skia.Point(w * 0.5, h * 0.42), max(w, h) * 0.75, [col(centre), col(bg), col(edge)], [0.0, 0.55, 1.0]))
        c.drawRect(skia.Rect(0, 0, w, h), paint)
        # faint engineering dot grid every half world unit
        step = self.k0 * 0.5
        dot = skia.Paint(Color=col((1, 1, 1), 0.035), AntiAlias=True)
        y = (h / 2) % step
        while y < h:
            x = (w / 2) % step
            while x < w:
                c.drawCircle(x, y, max(1.0, w / 1920 * 1.1), dot)
                x += step
            y += step
        img = surf.makeImageSnapshot()
        arr = img.toarray(colorType=skia.kRGBA_8888_ColorType).astype(np.int16)
        rng = np.random.default_rng(3)
        grain = rng.normal(0, 1.6, (h, w, 1)).astype(np.int16)
        arr[..., :3] = np.clip(arr[..., :3] + grain, 0, 255)
        arr[..., 3] = 255
        return _rgba_image(arr)

    # ------------------------------------------------------------------ role inference
    def role_of(self, o):
        r = o.data.get("_role") if isinstance(o.data, dict) else None
        if r:
            return r
        base = o.data.get("_base") or _hexof(o.color[:3])
        kind = o.kind
        if o.role:
            r = o.role
        elif kind == "text":
            r = "text"
        elif kind == "line":
            r = "curve" if o.data["width"] >= 0.03 else "hair"
        elif kind == "ring":
            r = "ring"
        elif kind == "ellipse":
            r = "orb" if base in ACCENTS else ("earth" if base in EARTH else "disc")
        elif kind == "poly":
            if base in EARTH:
                r = "earth"
            elif base == _h(P.SAND):
                r = "sand"
            elif base == _h(P.SEA):
                r = "sea"
            else:
                r = "flat"
        elif kind == "rect":
            sx, sy = abs(o.scale[0]), abs(o.scale[1])
            thin = min(sx, sy)
            if base in CARDS and thin > 0.2:
                r = "card"
            elif thin < 0.035 and max(sx, sy) > 0.0:
                r = "hair"
            elif base in STEELS:
                r = "steel"
            elif base in EARTH:
                r = "earth"
            elif base == _h(P.SAND):
                r = "sand"
            elif base == _h(P.SEA):
                r = "sea"
            elif base == _h(P.BG):
                r = "hole"
            elif base in FLUIDS:
                r = "fluid"
            else:
                r = "flat"
        else:
            r = "flat"
        o.data["_role"] = r
        return r

    # ------------------------------------------------------------------ frame
    def render(self, st, t):
        c = self.surface.getCanvas()
        c.resetMatrix()
        c.drawImage(self.background, 0, 0)
        cx, cy, cw = st.cam_at(t)
        k = self.w / cw
        self.k = k
        self.zoom = cw / WORLD_W
        M = skia.Matrix()
        M.setAll(k, 0, self.w / 2 - cx * k, 0, -k, self.h / 2 + cy * k, 0, 0, 1)
        self.M = M
        items = []
        for o in st.objs:
            if not o.visible(t):
                continue
            items.append((o.location[2], o.idx, o))
        for (a, b, z, fn) in st.procedurals:
            if a <= t < b:
                items.append((z, 1e12 + id(fn) % 1000, fn))
        items.sort(key=lambda it: (it[0], it[1]))
        for z, _, o in items:
            if callable(o):
                c.save()
                c.setMatrix(M)
                o(c, t, self)
                c.restore()
                continue
            self._draw(c, o, t)
        return self.buf.copy()

    # ------------------------------------------------------------------ dispatch
    def _draw(self, c, o, t):
        alpha = o.ev("alpha", t, o.color[3])
        if alpha <= 0.003:
            return
        rgb = o.ev("rgb", t, tuple(o.color[:3]))
        loc = o.ev("loc", t, (o.location[0], o.location[1]))
        sc = o.ev("scale", t, (o.scale[0], o.scale[1]))
        if abs(sc[0]) < 1e-6 and abs(sc[1]) < 1e-6 and o.kind not in ("line",):
            return
        rot = o.ev("rot", t, o.rotation_euler[2])
        role = self.role_of(o)
        x, y = loc
        if o.entrance and role in ("text", "card", "pill") and o.entrance[0] <= t < o.entrance[1]:
            a, b = o.entrance
            p = ease_out((t - a) / (b - a))
            y -= (1 - p) * 0.07
        if o.kind == "text":
            self._text(c, o, x, y, sc, rot, rgb, alpha)
            return
        c.save()
        c.setMatrix(self.M)
        c.translate(x, y)
        if rot:
            c.rotate(math.degrees(rot))
        try:
            if o.kind == "rect":
                self._rect(c, o, sc, rgb, alpha, role, x, y, rot)
            elif o.kind == "ellipse":
                self._ellipse(c, o, sc, rgb, alpha, role)
            elif o.kind == "ring":
                c.scale(sc[0], sc[1])
                self._ring(c, o, rgb, alpha)
            elif o.kind == "poly":
                c.scale(sc[0], sc[1])
                self._poly(c, o, rgb, alpha, role, x, y)
            elif o.kind == "line":
                c.translate(-x, -y)
                self._line(c, o, t, x, y, sc, rgb, alpha, role)
        finally:
            c.restore()

    # ------------------------------------------------------------------ helpers
    def _blur(self, px):
        return skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(px, 0.5), False)

    def _local_rect(self, o, sx, sy):
        a = o.data.get("anchor", "c")
        w, h = abs(sx), abs(sy)
        if a == "c":
            return skia.Rect(-w / 2, -h / 2, w / 2, h / 2)
        if a == "b":
            return skia.Rect(-w / 2, 0, w / 2, h) if sy >= 0 else skia.Rect(-w / 2, -h, w / 2, 0)
        if a == "t":
            return skia.Rect(-w / 2, -h, w / 2, 0) if sy >= 0 else skia.Rect(-w / 2, 0, w / 2, h)
        if a == "l":
            return skia.Rect(0, -h / 2, w, h / 2)
        if a == "r":
            return skia.Rect(-w, -h / 2, 0, h / 2)
        return skia.Rect(-w / 2, -h / 2, w / 2, h / 2)

    def _texture_paint(self, name, alpha, tile_world=2.0, x=0.0, y=0.0):
        img = self.tex[name]
        s = tile_world / img.width()
        lm = skia.Matrix.Scale(s, s)
        lm.postTranslate(-x, -y)     # we draw in object-local coords: anchor the texture to the world
        shader = img.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat, skia.SamplingOptions(skia.FilterMode.kLinear), lm)
        return skia.Paint(Shader=shader, AntiAlias=True, Alphaf=float(alpha))

    # ------------------------------------------------------------------ rect
    def _rect(self, c, o, sc, rgb, alpha, role, x, y, rot):
        r = self._local_rect(o, sc[0], sc[1])
        w, h = r.width(), r.height()
        if w <= 0 or h <= 0:
            return
        px = 1.0 / self.k
        if role == "backdrop":
            c.save()
            c.resetMatrix()
            c.drawImage(self.background, 0, 0, skia.SamplingOptions(), skia.Paint(Alphaf=float(alpha)))
            c.restore()
            return
        if role == "card":
            rad = min(0.13, w / 2, h / 2)
            rr = skia.RRect.MakeRectXY(r, rad, rad)
            sh = skia.Paint(Color=col((0, 0, 0), 0.42 * alpha), AntiAlias=True, MaskFilter=self._blur(12 * self.w / 1920))
            c.save()
            c.translate(0, -5 * px)
            c.drawRRect(rr, sh)
            c.restore()
            top, bot = lighten(rgb, 0.07), darken(rgb, 0.06)
            g = skia.GradientShader.MakeLinear([skia.Point(0, r.bottom()), skia.Point(0, r.top())], [col(top, alpha), col(bot, alpha)])
            c.drawRRect(rr, skia.Paint(Shader=g, AntiAlias=True))
            c.drawRRect(rr, skia.Paint(Color=col((1, 1, 1), 0.075 * alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.2 * px))
            return
        if role == "pill":
            rad = min(w, h) / 2
            rr = skia.RRect.MakeRectXY(r, rad, rad)
            sh = skia.Paint(Color=col((0, 0, 0), 0.35 * alpha), AntiAlias=True, MaskFilter=self._blur(7 * self.w / 1920))
            c.save()
            c.translate(0, -3 * px)
            c.drawRRect(rr, sh)
            c.restore()
            top, bot = lighten(rgb, 0.08), darken(rgb, 0.05)
            g = skia.GradientShader.MakeLinear([skia.Point(0, r.bottom()), skia.Point(0, r.top())], [col(top, alpha), col(bot, alpha)])
            c.drawRRect(rr, skia.Paint(Shader=g, AntiAlias=True))
            c.drawRRect(rr, skia.Paint(Color=col((1, 1, 1), 0.10 * alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.0 * px))
            return
        if role == "shaft":
            rad = h / 2
            rr = skia.RRect.MakeRectXY(r, rad, rad)
            if o.data.get("_base") in ACCENTS:
                c.drawRRect(rr, skia.Paint(Color=col(rgb, 0.45 * alpha), AntiAlias=True, MaskFilter=self._blur(max(4.0, h * self.k * 0.9))))
            c.drawRRect(rr, skia.Paint(Color=col(rgb, alpha), AntiAlias=True))
            return
        if role == "hair":
            c.drawRect(r, skia.Paint(Color=col(rgb, alpha), AntiAlias=True))
            return
        if role == "steel":
            horiz = w >= h   # gradient across the short axis
            if horiz:
                pts = [skia.Point(0, r.bottom()), skia.Point(0, r.top())]
            else:
                pts = [skia.Point(r.left(), 0), skia.Point(r.right(), 0)]
            g = skia.GradientShader.MakeLinear(pts, [col(darken(rgb, 0.38), alpha), col(lighten(rgb, 0.30), alpha), col(rgb, alpha),
                                                     col(darken(rgb, 0.10), alpha), col(darken(rgb, 0.42), alpha)],
                                               [0.0, 0.26, 0.5, 0.78, 1.0])
            c.drawRect(r, skia.Paint(Shader=g, AntiAlias=True))
            return
        if role in ("earth", "sand"):
            g = skia.GradientShader.MakeLinear([skia.Point(0, r.bottom()), skia.Point(0, r.top())],
                                               [col(darken(rgb, 0.10), alpha), col(lighten(rgb, 0.04), alpha)])
            c.drawRect(r, skia.Paint(Shader=g, AntiAlias=True))
            if not rot:
                if role == "earth":
                    c.drawRect(r, self._texture_paint("earth_dark", alpha, 2.2, x, y))
                    c.drawRect(r, self._texture_paint("earth_light", alpha, 2.2, x, y))
                else:
                    c.drawRect(r, self._texture_paint("sand_dark", alpha, 1.1, x, y))
                    c.drawRect(r, self._texture_paint("sand_light", alpha, 1.1, x, y))
            return
        if role == "sea":
            g = skia.GradientShader.MakeLinear([skia.Point(0, r.bottom()), skia.Point(0, r.top())],
                                               [col(darken(rgb, 0.30), alpha), col(lighten(rgb, 0.10), alpha)])
            c.drawRect(r, skia.Paint(Shader=g, AntiAlias=True))
            c.drawRect(r, self._texture_paint("sea", alpha, 3.0, x, y))
            return
        if role == "fluid":
            if w < h * 1.6:
                pts = [skia.Point(r.left(), 0), skia.Point(r.right(), 0)]
            else:
                pts = [skia.Point(0, r.bottom()), skia.Point(0, r.top())]
            g = skia.GradientShader.MakeLinear(pts, [col(darken(rgb, 0.16), alpha), col(lighten(rgb, 0.10), alpha), col(rgb, alpha),
                                                     col(darken(rgb, 0.16), alpha)], [0.0, 0.35, 0.6, 1.0])
            c.drawRect(r, skia.Paint(Shader=g, AntiAlias=True))
            if o.data.get("_base") == _h(P.CEMENT) and not rot:
                c.drawRect(r, self._texture_paint("cement", alpha, 1.2, x, y))
            return
        if role == "hole":
            c.drawRect(r, skia.Paint(Color=col(darken(rgb, 0.25), alpha), AntiAlias=True))
            return
        # flat / solid: soft top light + hairline edge for definition
        g = skia.GradientShader.MakeLinear([skia.Point(0, r.bottom()), skia.Point(0, r.top())],
                                           [col(darken(rgb, 0.08), alpha), col(lighten(rgb, 0.06), alpha)])
        if min(w, h) > 0.12 and role == "flat":
            rad = min(0.04, w / 4, h / 4)
            c.drawRRect(skia.RRect.MakeRectXY(r, rad, rad), skia.Paint(Shader=g, AntiAlias=True))
            c.drawRRect(skia.RRect.MakeRectXY(r, rad, rad), skia.Paint(Color=col(darken(rgb, 0.45), 0.5 * alpha), AntiAlias=True,
                                                                        Style=skia.Paint.kStroke_Style, StrokeWidth=1.0 * px))
        else:
            c.drawRect(r, skia.Paint(Shader=g, AntiAlias=True))

    # ------------------------------------------------------------------ ellipse / ring / poly
    def _ellipse(self, c, o, sc, rgb, alpha, role):
        rx, ry = abs(sc[0]), abs(sc[1])
        r = skia.Rect(-rx, -ry, rx, ry)
        if role == "orb":
            c.drawOval(skia.Rect(-rx * 1.5, -ry * 1.5, rx * 1.5, ry * 1.5),
                       skia.Paint(Color=col(rgb, 0.40 * alpha), AntiAlias=True, MaskFilter=self._blur(max(5.0, rx * self.k * 0.7))))
            g = skia.GradientShader.MakeRadial(skia.Point(-rx * 0.3, ry * 0.35), max(rx, ry) * 1.25,
                                               [col(lighten(rgb, 0.45), alpha), col(rgb, alpha), col(darken(rgb, 0.18), alpha)], [0.0, 0.55, 1.0])
            c.drawOval(r, skia.Paint(Shader=g, AntiAlias=True))
            return
        if role == "earth":
            c.drawOval(r, skia.Paint(Color=col(rgb, alpha), AntiAlias=True))
            return
        if role == "hole":
            c.drawOval(r, skia.Paint(Color=col(darken(rgb, 0.25), alpha), AntiAlias=True))
            return
        if role in ("flat", "solid"):
            c.drawOval(r, skia.Paint(Color=col(rgb, alpha), AntiAlias=True))
            return
        g = skia.GradientShader.MakeRadial(skia.Point(-rx * 0.25, ry * 0.3), max(rx, ry) * 1.3,
                                           [col(lighten(rgb, 0.12), alpha), col(rgb, alpha), col(darken(rgb, 0.12), alpha)], [0.0, 0.6, 1.0])
        c.drawOval(r, skia.Paint(Shader=g, AntiAlias=True))

    def _ring(self, c, o, rgb, alpha):
        ro, ri = o.data["r"], o.data["ri"]
        path = skia.Path()
        path.addCircle(0, 0, ro)
        path.addCircle(0, 0, ri)
        path.setFillType(skia.PathFillType.kEvenOdd)
        if _hexof(rgb) in ACCENTS:
            c.drawPath(path, skia.Paint(Color=col(rgb, 0.35 * alpha), AntiAlias=True, MaskFilter=self._blur(6 * self.w / 1920)))
        c.drawPath(path, skia.Paint(Color=col(rgb, alpha), AntiAlias=True))

    def _poly(self, c, o, rgb, alpha, role, x, y):
        pts = o.data["pts"]
        path = skia.Path()
        path.moveTo(*pts[0])
        for p in pts[1:]:
            path.lineTo(*p)
        path.close()
        if role == "head":
            if o.data.get("_base") in ACCENTS:
                c.drawPath(path, skia.Paint(Color=col(rgb, 0.45 * alpha), AntiAlias=True, MaskFilter=self._blur(5 * self.w / 1920)))
            p = skia.Paint(Color=col(rgb, alpha), AntiAlias=True)
            c.drawPath(path, p)
            p.setStyle(skia.Paint.kStroke_Style)
            p.setStrokeJoin(skia.Paint.kRound_Join)
            p.setStrokeWidth(0.035)
            c.drawPath(path, p)
            return
        if role == "earth":
            c.drawPath(path, skia.Paint(Color=col(rgb, alpha), AntiAlias=True))
            c.drawPath(path, self._texture_paint("earth_dark", alpha, 2.2, x, y))
            return
        if role == "sand":
            c.drawPath(path, skia.Paint(Color=col(rgb, alpha), AntiAlias=True))
            c.drawPath(path, self._texture_paint("sand_dark", alpha, 1.1, x, y))
            return
        if role == "sea":
            c.drawPath(path, skia.Paint(Color=col(rgb, alpha), AntiAlias=True))
            c.drawPath(path, self._texture_paint("sea", alpha, 3.0, x, y))
            return
        c.drawPath(path, skia.Paint(Color=col(rgb, alpha), AntiAlias=True))

    # ------------------------------------------------------------------ lines
    def _line(self, c, o, t, x, y, sc, rgb, alpha, role):
        pts = o.data["pts"]
        if len(pts) < 2:
            return
        path = skia.Path()
        path.moveTo(*pts[0])
        for p in pts[1:]:
            path.lineTo(*p)
        if o.data.get("closed"):
            path.close()
        width = o.data["width"]
        # moves translate the whole polyline; scale is ignored for lines (it never carried meaning)
        if (x, y) != (0.0, 0.0):
            c.translate(x, y)
        frac = o.ev("draw", t, 1.0)
        tip = None
        if frac < 0.999:
            if frac <= 0.0005:
                return
            meas = skia.PathMeasure(path, False)
            L = meas.getLength()
            seg = skia.Path()
            meas.getSegment(0, L * frac, seg, True)
            pos = meas.getPosTan(L * frac)
            tip = pos[0] if isinstance(pos, tuple) else None
            path = seg
        accent = o.data.get("_base") in ACCENTS and role in ("curve", "glow")
        if accent:
            g = skia.Paint(Color=col(rgb, 0.38 * alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width * 2.4,
                           StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join, MaskFilter=self._blur(max(3.0, width * self.k * 0.8)))
            c.drawPath(path, g)
        p = skia.Paint(Color=col(rgb, alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width,
                       StrokeCap=skia.Paint.kRound_Cap if role != "dash" else skia.Paint.kButt_Cap, StrokeJoin=skia.Paint.kRound_Join)
        c.drawPath(path, p)
        if tip is not None and accent:
            r = width * 1.5
            c.drawCircle(tip.x(), tip.y(), r * 2.6, skia.Paint(Color=col(lighten(rgb, 0.4), 0.55 * alpha), AntiAlias=True,
                                                             MaskFilter=self._blur(max(4.0, r * self.k))))
            c.drawCircle(tip.x(), tip.y(), r, skia.Paint(Color=col(lighten(rgb, 0.6), alpha), AntiAlias=True))

    # ------------------------------------------------------------------ procedural helpers (canvas is in world coords)
    def draw_particles(self, c, pos, color, r, alpha, glow=True):
        rgb = hex_rgb(color)
        if glow:
            g = skia.Paint(Color=col(rgb, 0.45 * alpha), AntiAlias=True, MaskFilter=self._blur(max(3.0, r * self.k * 1.1)))
            for p in pos:
                c.drawCircle(float(p[0]), float(p[1]), r * 1.8, g)
        core = skia.Paint(Color=col(lighten(rgb, 0.35), alpha), AntiAlias=True)
        for p in pos:
            c.drawCircle(float(p[0]), float(p[1]), r, core)

    def draw_ring(self, c, x, y, r, width, color, alpha):
        rgb = hex_rgb(color)
        p = skia.Paint(Color=col(rgb, alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width)
        c.drawCircle(x, y, r, skia.Paint(Color=col(rgb, 0.4 * alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                         StrokeWidth=width * 3, MaskFilter=self._blur(6 * self.w / 1920)))
        c.drawCircle(x, y, r, p)

    def draw_text(self, c, s, x, y, size, color, alpha, align="c", kind="sans"):
        from .stage import TEXT_SCALE, MIN_TEXT

        class _T:
            pass
        o = _T()
        o.data = {"s": s, "size": max(size * TEXT_SCALE, MIN_TEXT), "align": align, "valign": "c", "kind": kind}
        c.save()
        self._text(c, o, x, y, (1.0, 1.0), 0.0, hex_rgb(color), alpha)
        c.restore()

    # ------------------------------------------------------------------ text
    def _font(self, kind, size_px):
        tf = self.tf.get(kind if kind in ("sans", "bold", "mono") else "sans")
        if kind == "bold" and size_px > 44:
            tf = self.tf["display"]
        f = skia.Font(tf, size_px)
        f.setSubpixel(True)
        f.setEdging(skia.Font.Edging.kAntiAlias)
        return f

    def _runs(self, s, font, kind):
        """Split a line into runs with a fallback font for glyphs the main face lacks."""
        fb = skia.Font(self.tf["fallback_bold" if kind == "bold" else "fallback"], font.getSize())
        fb.setSubpixel(True)
        runs, cur, cur_f = [], "", None
        for ch in s:
            key = (id(font.getTypeface()), ch)
            ok = self._glyph_ok.get(key)
            if ok is None:
                ok = font.unicharToGlyph(ord(ch)) != 0 or ch in " \t"
                self._glyph_ok[key] = ok
            f = font if ok else fb
            if cur_f is None or f is cur_f:
                cur += ch
                cur_f = f
            else:
                runs.append((cur, cur_f))
                cur, cur_f = ch, f
        if cur:
            runs.append((cur, cur_f))
        return runs

    def _text(self, c, o, x, y, sc, rot, rgb, alpha):
        d = o.data
        size_px = d["size"] * self.k
        if size_px < 2:
            return
        font = self._font(d["kind"], size_px)
        lines = d["s"].split("\n")
        lh = size_px * 1.22
        cap = size_px * 0.727
        n = len(lines)
        if d["valign"] == "t":
            base0 = cap
        elif d["valign"] == "b":
            base0 = -(n - 1) * lh
        else:
            base0 = cap / 2 - (n - 1) * lh / 2
        # device position of the anchor
        pt = self.M.mapXY(x, y)
        c.save()
        c.resetMatrix()
        c.translate(pt.x(), pt.y())
        if rot:
            c.rotate(-math.degrees(rot))
        if sc[0] != 1.0 or sc[1] != 1.0:
            c.scale(sc[0], sc[1])
        shadow = skia.Paint(Color=col((0, 0, 0), 0.55 * alpha), AntiAlias=True, MaskFilter=self._blur(max(1.2, size_px * 0.06)))
        paint = skia.Paint(Color=col(rgb, alpha), AntiAlias=True)
        for i, line in enumerate(lines):
            runs = self._runs(line, font, d["kind"])
            widths = [f.measureText(s) for s, f in runs]
            tw = sum(widths)
            x0 = {"c": -tw / 2, "l": 0.0, "r": -tw}[d["align"]]
            by = base0 + i * lh
            xx = x0
            for (s, f), wdt in zip(runs, widths):
                blob = skia.TextBlob.MakeFromString(s, f)
                if blob is not None:
                    c.drawTextBlob(blob, xx, by + size_px * 0.05, shadow)
                    c.drawTextBlob(blob, xx, by, paint)
                xx += wdt
        c.restore()


# ---------------------------------------------------------------------------------------------- layout helpers
_MEASURE: dict = {}


def measure(s, size, kind="sans"):
    """Width (world units) of the widest line of `s` drawn by Stage.text(s, size=size, kind=kind)."""
    from .stage import TEXT_SCALE, MIN_TEXT
    ts = max(size * TEXT_SCALE, MIN_TEXT)
    key = kind if kind in ("sans", "bold", "mono") else "sans"
    if key not in _MEASURE:
        _MEASURE[key] = skia.Font(skia.Typeface.MakeFromFile(FONT_FILES[key]), 100.0)
        _MEASURE[key + "_fb"] = skia.Font(skia.Typeface.MakeFromFile(FONT_FILES["fallback_bold" if key == "bold" else "fallback"]), 100.0)
    f, fb = _MEASURE[key], _MEASURE[key + "_fb"]
    best = 0.0
    for line in s.split("\n"):
        w = 0.0
        for ch in line:
            w += (f if (f.unicharToGlyph(ord(ch)) != 0 or ch == " ") else fb).measureText(ch)
        best = max(best, w)
    return best / 100.0 * ts


def wrap_to(s, size, max_w, kind="sans"):
    """Greedy word wrap so every line fits max_w world units."""
    out = []
    for para in s.split("\n"):
        cur = ""
        for word in para.split():
            trial = (cur + " " + word).strip()
            if cur and measure(trial, size, kind) > max_w:
                out.append(cur)
                cur = word
            else:
                cur = trial
        out.append(cur)
    return "\n".join(out)
