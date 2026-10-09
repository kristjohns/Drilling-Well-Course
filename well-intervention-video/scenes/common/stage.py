"""A small 2-D motion-graphics engine (skia) for the explainer.

World: a 16 x 9 unit canvas, x in [-8, 8], y in [-4.5, 4.5], y up; larger z draws on top.
Time: seconds from the start of the chapter.

The API is the one the chapter modules were written against (it began life as a thin layer over Blender):
  * `with st.span(t0, t1):` every object created inside is only visible between t0 and t1.
  * Animation helpers (fade_in, move, scale_to, recolor, draw_on, pop_in, rotate, camera) add keyframes.
  * Objects expose `.location`, `.scale`, `.rotation_euler`, `.hide_render`, `.color` like the Blender objects did.
The *look* lives in `look.py`: every primitive is drawn by role (card, pill, steel, rock, fluid, curve, text ...),
so the chapters get a modern rendering without knowing about it.

Rendering: `render_video()` evaluates every frame at `fps`, re-uses the previous frame when nothing changed, and pipes
raw RGBA into ffmpeg. Beat boundaries can be given to `set_transitions()` for a soft dissolve between beats.
"""
from __future__ import annotations
import bisect
import math
import os
import subprocess
import textwrap
import time as _time

import numpy as np
import skia

from . import palette as P

W, H = 16.0, 9.0
TEXT_SCALE = 1.18   # global legibility bump: all text() sizes are multiplied by this (min 0.2)
MIN_TEXT = 0.2


# ---------------------------------------------------------------------------------------------- colour helpers
def hex_rgb(c):
    """'#rrggbb' -> (r, g, b) floats in 0..1 (sRGB). Tuples pass through."""
    if isinstance(c, str):
        h = c.lstrip("#")
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return tuple(c[:3])


def rgba(color, alpha: float = 1.0):
    r, g, b = hex_rgb(color)
    return (r, g, b, alpha)


def as_list(objs):
    if objs is None:
        return []
    if isinstance(objs, (list, tuple, set)):
        out = []
        for o in objs:
            out.extend(as_list(o))
        return out
    return [objs]


# ---------------------------------------------------------------------------------------------- easing
def ease_inout(f):          # cubic in-out: the default for moves / scales / camera
    return 4 * f * f * f if f < 0.5 else 1 - (-2 * f + 2) ** 3 / 2


def ease_out(f):
    return 1 - (1 - f) ** 3


def ease_back(f, s=1.4):    # gentle overshoot for pop-ins
    f -= 1
    return f * f * ((s + 1) * f + s) + 1


_EASE = {"BEZIER": ease_inout, "LINEAR": lambda f: f, "OUT": ease_out, "BACK": ease_back}


def _lerp(a, b, f):
    if isinstance(a, tuple):
        return tuple(x + (y - x) * f for x, y in zip(a, b))
    return a + (b - a) * f


class Track:
    """Keyframes [t, value, interp]; the interpolation of a segment is that of its left key (Blender semantics).
    Constant extrapolation before the first and after the last key."""
    __slots__ = ("keys", "_ts")

    def __init__(self):
        self.keys: list = []
        self._ts: list = []

    def set(self, t, v, interp="BEZIER"):
        i = bisect.bisect_left(self._ts, t - 1e-9)
        if i < len(self._ts) and abs(self._ts[i] - t) < 1e-9:
            self.keys[i] = [t, v, interp]
            return
        self._ts.insert(i, t)
        self.keys.insert(i, [t, v, interp])

    def __bool__(self):
        return bool(self.keys)

    def eval(self, t):
        ks = self.keys
        if t <= ks[0][0]:
            return ks[0][1]
        if t >= ks[-1][0]:
            return ks[-1][1]
        i = bisect.bisect_right(self._ts, t) - 1
        t0, v0, it = ks[i]
        t1, v1, _ = ks[i + 1]
        if it == "CONSTANT" or t1 <= t0:
            return v0
        f = (t - t0) / (t1 - t0)
        return _lerp(v0, v1, _EASE.get(it, ease_inout)(f))

    def segment_at(self, t):
        """(v0, v1, progress 0..1 eased by nothing) of the segment containing t, or None."""
        ks = self.keys
        if not ks or t <= ks[0][0] or t >= ks[-1][0]:
            return None
        i = bisect.bisect_right(self._ts, t) - 1
        t0, v0, _ = ks[i]
        t1, v1, _ = ks[i + 1]
        return v0, v1, (t - t0) / max(t1 - t0, 1e-9)

    def change_intervals(self):
        """Time intervals (a, b] in which the value changes; CONSTANT steps give zero-length (b, b]."""
        out = []
        ks = self.keys
        for (t0, v0, it), (t1, v1, _) in zip(ks[:-1], ks[1:]):
            if v0 == v1:
                continue
            out.append((t1, t1) if it == "CONSTANT" else (t0, t1))
        return out


class Obj:
    """One drawable. Static properties mimic Blender's object attributes; tracks override them when keyed."""
    __slots__ = ("kind", "idx", "location", "scale", "rotation_euler", "color", "hide_render", "data", "role",
                 "tracks", "windows", "entrance", "name")

    def __init__(self, kind, idx, data, color, alpha, loc, scale=(1.0, 1.0, 1.0), rot=0.0, role=None):
        self.kind = kind
        self.idx = idx
        self.data = data
        self.location = list(loc)
        self.scale = list(scale)
        self.rotation_euler = [0.0, 0.0, rot]
        self.color = list(rgba(color, alpha))
        self.hide_render = False
        self.role = role
        self.tracks: dict = {}
        self.windows: list = []        # [(a, b)] visibility windows (intersection of all enclosing spans)
        self.entrance = None           # (t_start, t_end) of the first fade-in, for the slide-up micro-animation
        self.name = None

    def track(self, name):
        tr = self.tracks.get(name)
        if tr is None:
            tr = self.tracks[name] = Track()
        return tr

    # evaluated state ------------------------------------------------------------------------------
    def visible(self, t):
        if self.hide_render:
            return False
        for a, b in self.windows:
            if not (a <= t < b):
                return False
        return True

    def ev(self, name, t, static):
        tr = self.tracks.get(name)
        return tr.eval(t) if tr else static


# ---------------------------------------------------------------------------------------------- stage
class Stage:
    def __init__(self, duration: float, fps: int = 30, res=(1920, 1080), samples: int = 0, name: str = "stage"):
        self.name = name
        self.fps = fps
        self.duration = duration
        self.nframes = int(round(duration * fps))
        self.res = res
        self.objs: list[Obj] = []
        self.state: dict = {}
        self._vis: dict = {}
        self.fade_out_fixes: list = []      # (obj, t, alpha at t, creation alpha): fade-outs of already-faded objects
        self._span_stack: list = []
        self._span_objs: list = []
        self.cam = Obj("camera", -1, None, "#000000", 1.0, (0.0, 0.0, 20.0))
        self._cam_state = dict(x=0.0, y=0.0, scale=W)
        self.cam_tracks = {"x": Track(), "y": Track(), "w": Track()}
        self.transitions: list = []     # [(T, d)] dissolve windows
        self.continuous: list = []      # [(a, b)] intervals with procedural motion (flow particles etc.)
        self.procedurals: list = []     # callables draw(canvas, t, xf) with (a, b, z)
        self._n = 0

    # ------------------------------------------------------------------ time
    def fr(self, t: float) -> float:
        """Blender-compatible frame number (frame 1 == t 0)."""
        return 1.0 + t * self.fps

    @property
    def _span(self):
        return self._span_stack[-1] if self._span_stack else None

    # ------------------------------------------------------------------ registration
    def _new(self, kind, data, color, alpha, loc, scale=(1.0, 1.0, 1.0), rot=0.0, role=None):
        self._n += 1
        o = Obj(kind, self._n, data, color, alpha, loc, scale, rot, role)
        r, g, b = hex_rgb(color)
        data["_base"] = "#%02x%02x%02x" % (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))
        self.objs.append(o)
        self.state[o] = dict(alpha=alpha, loc=tuple(loc), scale=tuple(scale), rot=math.degrees(rot),
                             color=tuple(o.color))
        if self._span_stack:
            self._span_objs[-1].append(o)
        return o

    class _Span:
        def __init__(self, st, t0, t1):
            self.st, self.t0, self.t1 = st, t0, t1

        def __enter__(self):
            self.st._span_stack.append((self.t0, self.t1))
            self.st._span_objs.append([])
            return self

        def __exit__(self, *a):
            st = self.st
            st._span_stack.pop()
            objs = st._span_objs.pop()
            for o in objs:
                v = st._vis.get(o, {})
                a = max(self.t0, v.get("in", self.t0))
                b = min(self.t1, v.get("out", self.t1))
                o.windows.append((a, b))
            if st._span_objs:
                st._span_objs[-1].extend(objs)

    def span(self, t0: float, t1: float):
        return Stage._Span(self, t0, t1)

    # ------------------------------------------------------------------ primitives
    def rect(self, x, y, w, h, color, z=0.0, anchor="c", rot=0.0, alpha=1.0, name=None, role=None):
        o = self._new("rect", {"anchor": anchor}, color, alpha, (x, y, z), (w, h, 1.0), math.radians(rot), role)
        o.name = name
        return o

    def circle(self, x, y, r, color, z=0.0, alpha=1.0, role=None):
        return self._new("ellipse", {}, color, alpha, (x, y, z), (r, r, 1.0), 0.0, role)

    def ellipse(self, x, y, rx, ry, color, z=0.0, alpha=1.0, role=None):
        return self._new("ellipse", {}, color, alpha, (x, y, z), (rx, ry, 1.0), 0.0, role)

    def ring(self, x, y, r, thick, color, z=0.0, alpha=1.0, role=None):
        return self._new("ring", {"r": r, "ri": max(r - thick, 0.001)}, color, alpha, (x, y, z), role=role)

    def poly(self, pts, color, z=0.0, alpha=1.0, role=None):
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        return self._new("poly", {"pts": [(p[0] - cx, p[1] - cy) for p in pts]}, color, alpha, (cx, cy, z), role=role)

    def line(self, pts, color, width=0.05, z=0.0, alpha=1.0, closed=False, role=None):
        pts = [(float(p[0]), float(p[1])) for p in pts]
        return self._new("line", {"pts": pts, "width": width, "closed": closed}, color, alpha, (0.0, 0.0, z), role=role)

    def dashed(self, p0, p1, color, width=0.04, dash=0.18, gap=0.12, z=0.0, alpha=1.0):
        """Dashed straight line as a list of short segments (each fades/moves like any object)."""
        (x0, y0), (x1, y1) = p0, p1
        L = math.hypot(x1 - x0, y1 - y0)
        out, s = [], 0.0
        while s < L:
            e = min(s + dash, L)
            out.append(self.line([(x0 + (x1 - x0) * s / L, y0 + (y1 - y0) * s / L), (x0 + (x1 - x0) * e / L, y0 + (y1 - y0) * e / L)],
                                 color, width, z, alpha, role="dash"))
            s += dash + gap
        return out

    def arrow(self, x0, y0, x1, y1, color, width=0.07, head=0.28, z=0.0, alpha=1.0):
        L = max(math.hypot(x1 - x0, y1 - y0), 1e-6)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        shaft_len = max(L - head * 0.85, 0.01)
        ang = math.degrees(math.atan2(uy, ux))
        shaft = self.rect(x0 + ux * shaft_len / 2, y0 + uy * shaft_len / 2, shaft_len, width, color, z, rot=ang, alpha=alpha, role="shaft")
        bx, by = x0 + ux * (L - head), y0 + uy * (L - head)
        nx, ny = -uy, ux
        hw = head * 0.55
        tip = self.poly([(x1, y1), (bx + nx * hw, by + ny * hw), (bx - nx * hw, by - ny * hw)], color, z + 1e-4, alpha, role="head")
        return [shaft, tip]

    def text(self, s, x, y, size=0.3, color=P.TEXT, z=0.0, align="c", kind="sans", wrap=None, alpha=1.0, valign="c"):
        if wrap:
            s = "\n".join(textwrap.wrap(s, wrap)) if "\n" not in s else s
        return self._new("text", {"s": s, "size": max(size * TEXT_SCALE, MIN_TEXT), "align": align, "valign": valign,
                                  "kind": kind}, color, alpha, (x, y, z), role="text")

    @staticmethod
    def measure(s, size=0.3, kind="sans"):
        """World-unit width of text drawn with text(s, size=size, kind=kind)."""
        from .look import measure
        return measure(s, size, kind)

    # ------------------------------------------------------------------ alpha / colour
    def _alpha_key(self, o, t, a, interp="LINEAR"):
        o.track("alpha").set(t, a, interp)

    def fade(self, objs, t0, t1, a0=0.0, a1=1.0):
        for o in as_list(objs):
            base = self.state[o]["alpha"]
            self._alpha_key(o, t0, a0 * base)
            self._alpha_key(o, t1, a1 * base)

    def fade_in(self, objs, t, d=0.35):
        for o in as_list(objs):
            v = self._vis.setdefault(o, {})
            v["in"] = min(v.get("in", t), t)
            base = self.state[o]["alpha"]
            start = self._span[0] if self._span else 0.0
            if t > start + 1e-6:
                self._alpha_key(o, start, 0.0)
            self._alpha_key(o, t, 0.0, "OUT")
            self._alpha_key(o, t + d, base)
            if o.entrance is None or t < o.entrance[0]:
                o.entrance = (t, t + max(d, 0.3) * 1.4)

    def fade_out(self, objs, t, d=0.35):
        """Fade from the alpha the object has at t (not its creation alpha) to 0: fading out something that is already
        invisible keeps it invisible instead of flashing it back."""
        for o in as_list(objs):
            v = self._vis.setdefault(o, {})
            v["out"] = max(v.get("out", -1.0), t + d)
            base = self.state[o]["alpha"]
            tr = o.track("alpha")
            cur = tr.eval(t) if (tr and tr.keys[0][0] <= t) else base
            if cur < base - 1e-6:
                self.fade_out_fixes.append((o, t, cur, base))
            self._alpha_key(o, t, cur)
            self._alpha_key(o, t + d, 0.0)

    def recolor(self, objs, t0, t1, color):
        for o in as_list(objs):
            cur = tuple(self.state[o]["color"][:3])
            tr = o.track("rgb")
            tr.set(t0, cur, "LINEAR")
            new = hex_rgb(color)
            tr.set(t1, new, "LINEAR")
            self.state[o]["color"] = new + (self.state[o]["alpha"],)
            o.color[:3] = list(new)

    # ------------------------------------------------------------------ transforms
    def move(self, objs, t0, t1, dx=0.0, dy=0.0, to=None, interp="BEZIER"):
        for o in as_list(objs):
            s = self.state[o]
            x, y, z = s["loc"]
            tr = o.track("loc")
            tr.set(t0, (x, y), interp)
            nx, ny = (to[0], to[1]) if to is not None else (x + dx, y + dy)
            tr.set(t1, (nx, ny), interp)
            s["loc"] = (nx, ny, z)
            o.location[0], o.location[1] = nx, ny

    def scale_to(self, objs, t0, t1, sx=None, sy=None, interp="BEZIER"):
        for o in as_list(objs):
            s = self.state[o]
            cur = s["scale"]
            tr = o.track("scale")
            tr.set(t0, (cur[0], cur[1]), interp)
            new = (cur[0] if sx is None else sx, cur[1] if sy is None else sy, 1.0)
            tr.set(t1, (new[0], new[1]), interp)
            s["scale"] = new
            o.scale = list(new)

    def pop_in(self, objs, t, d=0.3):
        for o in as_list(objs):
            full = self.state[o]["scale"]
            start = self._span[0] if self._span else 0.0
            tr = o.track("scale")
            if t > start:
                tr.set(start, (0.0, 0.0), "CONSTANT")
            tr.set(t, (0.0, 0.0), "BACK")
            tr.set(t + max(d, 0.35), (full[0], full[1]), "BEZIER")

    def rotate(self, objs, t0, t1, deg, interp="BEZIER"):
        for o in as_list(objs):
            s = self.state[o]
            tr = o.track("rot")
            tr.set(t0, math.radians(s["rot"]), interp)
            tr.set(t1, math.radians(deg), interp)
            s["rot"] = deg
            o.rotation_euler[2] = math.radians(deg)

    def draw_on(self, line, t0, t1, interp="LINEAR"):
        """Reveal a line() object progressively (with a glowing tip while drawing)."""
        for o in as_list(line):
            start = self._span[0] if self._span else 0.0
            tr = o.track("draw")
            if t0 > start:
                tr.set(start, 0.0, "CONSTANT")
            tr.set(t0, 0.0, "OUT" if interp == "BEZIER" else interp)
            tr.set(t1, 1.0, interp)

    # ------------------------------------------------------------------ camera
    def camera(self, t0, t1, cx=None, cy=None, width=None, interp="BEZIER"):
        cs = self._cam_state
        for k, key in (("x", "x"), ("y", "y"), ("w", "scale")):
            self.cam_tracks[k].set(t0, cs[key], interp)
        cs["x"] = cs["x"] if cx is None else cx
        cs["y"] = cs["y"] if cy is None else cy
        cs["scale"] = cs["scale"] if width is None else width
        for k, key in (("x", "x"), ("y", "y"), ("w", "scale")):
            self.cam_tracks[k].set(t1, cs[key], interp)

    def cam_at(self, t):
        cx = self.cam_tracks["x"].eval(t) if self.cam_tracks["x"] else 0.0
        cy = self.cam_tracks["y"].eval(t) if self.cam_tracks["y"] else 0.0
        w = self.cam_tracks["w"].eval(t) if self.cam_tracks["w"] else W
        return cx, cy, w

    # ------------------------------------------------------------------ procedural / transitions
    def procedural(self, a, b, z, fn):
        """Register a custom drawing callback fn(canvas, t, look) active in [a, b) at depth z (e.g. flow particles)."""
        self.procedurals.append((a, b, z, fn))
        self.continuous.append((a, b))

    def flow(self, pts, t0, t1, color, n=18, speed=0.8, r=0.045, z=0.5, fade=0.4, alpha=0.9, glow=True, jitter=0.0):
        """Particles streaming along polyline `pts` (world coords) between t0 and t1: circulation, displacement, migration.
        speed in world units per second (negative = reverse direction); particles fade in/out over `fade` seconds."""
        import numpy as _np
        P_ = _np.array(pts, dtype=float)
        seg = _np.hypot(*(P_[1:] - P_[:-1]).T)
        cum = _np.concatenate([[0.0], _np.cumsum(seg)])
        L = float(cum[-1])
        rng = _np.random.default_rng(len(self.procedurals) + 1)
        offs = (_np.arange(n) + rng.random(n) * 0.6) / n
        side = (rng.random(n) - 0.5) * 2 * jitter

        def at(s):
            s = s % L
            i = min(int(_np.searchsorted(cum, s, side="right")) - 1, len(seg) - 1)
            f = (s - cum[i]) / max(seg[i], 1e-9)
            p = P_[i] + (P_[i + 1] - P_[i]) * f
            d = (P_[i + 1] - P_[i]) / max(seg[i], 1e-9)
            return p, d

        def draw(c, t, look):
            env = min(1.0, (t - t0) / fade, (t1 - t) / fade) if fade > 0 else 1.0
            if env <= 0:
                return
            pos = []
            for k in range(n):
                s = (offs[k] * L + speed * (t - t0))
                p, d = at(s)
                if jitter:
                    p = p + _np.array([-d[1], d[0]]) * side[k]
                pos.append(p)
            look.draw_particles(c, pos, color, r, alpha * env, glow)
        self.procedural(t0, t1, z, draw)

    def ripple(self, x, y, t0, t1, color, period=1.2, r0=0.1, r1=0.9, width=0.04, z=0.6):
        """Expanding emphasis rings at (x, y), one every `period` seconds."""
        def draw(c, t, look):
            k = 0
            while True:
                a = t0 + k * period
                if a > t:
                    break
                f = (t - a) / (period * 1.6)
                if 0 <= f < 1 and t < t1 + period:
                    look.draw_ring(c, x, y, r0 + (r1 - r0) * f, width, color, (1 - f) ** 1.5 * 0.9)
                k += 1
        self.procedural(t0, t1 + period * 1.6, z, draw)

    def counter(self, x, y, t0, t1, v0, v1, fmt="{:.0f}", size=0.3, color=P.TEXT, z=0.6, align="c", kind="mono", hold=None):
        """A number that counts from v0 to v1 over [t0, t1] (eased) and stays until `hold` (default: span end)."""
        end = hold if hold is not None else (self._span[1] if self._span else self.duration)

        def draw(c, t, look):
            f = min(max((t - t0) / max(t1 - t0, 1e-6), 0.0), 1.0)
            v = v0 + (v1 - v0) * ease_inout(f)
            a = min(1.0, (t - t0 + 0.3) / 0.3)
            look.draw_text(c, fmt.format(v), x, y, size, color, a, align, kind)
        self.procedural(max(t0 - 0.3, 0.0), end, z, draw)

    def set_transitions(self, times, d=0.45):
        self.transitions = [(T, d) for T in sorted(times) if 0.0 < T < self.duration - 0.05]

    # ------------------------------------------------------------------ frame planning
    def _dirty(self):
        """Boolean per frame: does anything change between frame i-1 and frame i?"""
        N = self.nframes
        fps = self.fps
        dirty = np.zeros(N, dtype=bool)
        if N:
            dirty[0] = True

        def mark(a, b):
            # frames whose time lies in (a, b]; zero-length = the first frame at/after b
            i0 = max(int(math.floor(a * fps + 1e-9)) + 1, 0)
            i1 = min(int(math.ceil(b * fps - 1e-9)), N - 1)
            if b <= a:
                i = min(max(int(math.ceil(b * fps - 1e-9)), 0), N - 1)
                dirty[i] = True
                return
            if i1 >= i0:
                dirty[i0:i1 + 1] = True
            j = min(max(int(math.ceil(b * fps - 1e-9)), 0), N - 1)
            dirty[j] = True

        for o in self.objs:
            if o.hide_render:
                continue
            for tr in o.tracks.values():
                for a, b in tr.change_intervals():
                    mark(a, b)
            if o.entrance:
                mark(*o.entrance)
            for a, b in o.windows:
                mark(a, a)
                mark(b, b)
        for tr in self.cam_tracks.values():
            for a, b in tr.change_intervals():
                mark(a, b)
        for a, b in self.continuous:
            mark(a, b)
        for T, d in self.transitions:
            mark(T - 1.0 / fps, T + d)
        return dirty

    # ------------------------------------------------------------------ rendering
    def _active(self, t):
        return [o for o in self.objs if o.visible(t)]

    def render_frame(self, t, look=None):
        """Render the scene at time t; returns an RGBA uint8 array (H, W, 4)."""
        from .look import Look
        look = look or Look.get(self.res)
        return look.render(self, t)

    def render_video(self, out_mp4, t0=0.0, t1=None, crf=17, preset="medium", progress=True, threads=None):
        from .look import Look
        look = Look.get(self.res)
        t1 = self.duration if t1 is None else t1
        f0, f1 = int(round(t0 * self.fps)), int(round(t1 * self.fps))
        dirty = self._dirty()
        w, h = self.res
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}", "-r", str(self.fps),
               "-i", "-", "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p", "-tune", "animation"]
        if threads:
            cmd += ["-threads", str(threads)]
        cmd += [out_mp4]
        os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        cache = {}
        last = None
        rendered = 0
        tstart = _time.time()
        for i in range(f0, f1):
            t = i / self.fps
            if last is None or dirty[min(i, len(dirty) - 1)]:
                frame = look.render(self, t)
                tr = self._transition_at(t)
                if tr is not None:
                    T, d = tr
                    if T not in cache:
                        cache.clear()
                        cache[T] = look.render(self, T - 1e-3)
                    p = ease_inout(min(max((t - T) / d, 0.0), 1.0))
                    frame = (cache[T].astype(np.float32) * (1 - p) + frame.astype(np.float32) * p).astype(np.uint8)
                last = frame
                rendered += 1
            proc.stdin.write(last.tobytes())
            if progress and (i - f0) % (self.fps * 20) == 0 and i > f0:
                el = _time.time() - tstart
                print(f"  {self.name}: {i - f0}/{f1 - f0} frames ({rendered} rendered) {el:.0f}s", flush=True)
        proc.stdin.close()
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg failed for {out_mp4}")
        return rendered

    def _transition_at(self, t):
        for T, d in self.transitions:
            if T <= t < T + d:
                return T, d
        return None

    def save_png(self, path, t):
        from PIL import Image
        arr = self.render_frame(t)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        Image.fromarray(arr, "RGBA").convert("RGB").save(path)
