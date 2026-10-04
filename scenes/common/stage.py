"""A tiny 2-D motion-graphics layer on top of Blender (bpy) for flat technical illustration.

Everything lives in the z=0 plane of a 16 x 9 world-unit canvas seen by an orthographic camera
(x in [-8, 8], y in [-4.5, 4.5]); larger z = nearer the camera. Rendering uses the Workbench engine with
flat lighting and per-object colour (alpha supported), which is ~20x cheaper than Cycles on a CPU-only box.

Time is in seconds from the start of the chapter. Frame 1 == t 0.

Key ideas
  * `with st.span(t0, t1):` every object created inside is only visible between t0 and t1.
  * Animation helpers (fade_in, move, grow, recolor, draw_on, camera) add keyframes; they never loop in Python.
  * `plan_frames()` finds the frames at which ANY animated value changes, so static stretches are rendered once.
"""
from __future__ import annotations
import math
import os
import textwrap

import bpy

from . import palette as P

W, H = 16.0, 9.0
TEXT_SCALE = 1.18   # global legibility bump: all text() sizes are multiplied by this (min 0.2)
MIN_TEXT = 0.2
FONT_DIR = "/usr/share/fonts/truetype"
FONTS = {
    "sans": f"{FONT_DIR}/liberation/LiberationSans-Regular.ttf",
    "bold": f"{FONT_DIR}/liberation/LiberationSans-Bold.ttf",
    "mono": f"{FONT_DIR}/dejavu/DejaVuSansMono.ttf",
}


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgba(color, alpha: float = 1.0):
    """'#rrggbb' (sRGB) or an (r,g,b[,a]) tuple already in linear space -> linear RGBA."""
    if isinstance(color, str):
        h = color.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        return (_lin(r), _lin(g), _lin(b), alpha)
    return (color[0], color[1], color[2], color[3] if len(color) > 3 else alpha)


def as_list(objs):
    if objs is None:
        return []
    if isinstance(objs, (list, tuple, set)):
        out = []
        for o in objs:
            out.extend(as_list(o))
        return out
    return [objs]


class Stage:
    def __init__(self, duration: float, fps: int = 12, res=(1920, 1080), samples: int = 8, name: str = "stage"):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.sc = bpy.context.scene
        self.name = name
        self.fps = fps
        self.duration = duration
        self.nframes = int(round(duration * fps))   # frames 1..N cover [0, duration)
        sc = self.sc
        sc.render.resolution_x, sc.render.resolution_y = res
        sc.render.resolution_percentage = 100
        sc.render.fps = fps
        sc.frame_start, sc.frame_end = 1, self.nframes
        sc.render.engine = "BLENDER_WORKBENCH"
        sc.render.image_settings.file_format = "PNG"
        sc.render.film_transparent = False
        sh = sc.display.shading
        sh.light = "FLAT"
        sh.color_type = "OBJECT"
        sh.show_object_outline = True
        sh.object_outline_color = rgba(P.OUTLINE)[:3]
        sh.show_cavity = False
        sh.show_shadows = False
        sc.display.render_aa = str(samples) if samples in (0, 5, 8, 11, 16, 32) else "8"
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
        sc.world = bpy.data.worlds.new("w")
        sc.world.color = rgba(P.BG)[:3]
        cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
        bpy.context.collection.objects.link(cam)
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = W
        cam.data.clip_start, cam.data.clip_end = 0.1, 100.0
        cam.location = (0, 0, 20)
        sc.camera = cam
        self.cam = cam
        self._cam_state = dict(x=0.0, y=0.0, scale=W)
        self.state: dict = {}
        self._vis: dict = {}      # obj -> {'in': first fade-in time, 'out': last fade-out end}; drives hide_render (outlines ignore alpha)
        self._span: tuple | None = None
        self._span_objs: list = []
        self._fonts: dict = {}
        self._mesh_cache: dict = {}
        self._n = 0
        self._build_shared_meshes()

    # ------------------------------------------------------------------ time / keys
    def fr(self, t: float) -> float:
        return 1.0 + t * self.fps

    def _key(self, idblock, path, t, interp="BEZIER", index=-1):
        bpy.context.preferences.edit.keyframe_new_interpolation_type = interp
        idblock.keyframe_insert(data_path=path, index=index, frame=self.fr(t))

    # ------------------------------------------------------------------ meshes
    def _build_shared_meshes(self):
        def quad(name, x0, x1, y0, y1):
            me = bpy.data.meshes.new(name)
            me.from_pydata([(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], [], [(0, 1, 2, 3)])
            return me
        self._mesh_cache["c"] = quad("rect_c", -.5, .5, -.5, .5)
        self._mesh_cache["b"] = quad("rect_b", -.5, .5, 0, 1)    # origin at bottom-centre
        self._mesh_cache["t"] = quad("rect_t", -.5, .5, -1, 0)   # origin at top-centre
        self._mesh_cache["l"] = quad("rect_l", 0, 1, -.5, .5)    # origin at left-centre
        self._mesh_cache["r"] = quad("rect_r", -1, 0, -.5, .5)   # origin at right-centre
        n = 48
        me = bpy.data.meshes.new("circle")
        me.from_pydata([(0, 0, 0)] + [(math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n), 0) for i in range(n)],
                       [], [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)])
        self._mesh_cache["circle"] = me

    def _next(self, kind):
        self._n += 1
        return f"{kind}{self._n}"

    def _register(self, obj, alpha=1.0, loc=(0, 0, 0), scale=(1, 1, 1), rot=0.0):
        self.state[obj] = dict(alpha=alpha, loc=tuple(loc), scale=tuple(scale), rot=rot,
                               color=tuple(obj.color))
        if self._span is not None:
            self._span_objs.append(obj)
        return obj

    def _link(self, obj):
        bpy.context.collection.objects.link(obj)

    # ------------------------------------------------------------------ spans (visibility windows)
    class _Span:
        def __init__(self, st, t0, t1):
            self.st, self.t0, self.t1 = st, t0, t1

        def __enter__(self):
            st = self.st
            self.prev = (st._span, st._span_objs)
            st._span, st._span_objs = (self.t0, self.t1), []
            return self

        def __exit__(self, *a):
            st = self.st
            objs = st._span_objs
            st._span, st._span_objs = self.prev
            for o in objs:
                v = st._vis.get(o, {})
                a = max(self.t0, v.get("in", self.t0))
                b = min(self.t1, v.get("out", self.t1))
                if a <= 0 and b >= st.duration:
                    continue
                if a > 0:
                    o.hide_render = True
                    st._key(o, "hide_render", 0, "CONSTANT")
                o.hide_render = False
                st._key(o, "hide_render", a, "CONSTANT")
                if b < st.duration:
                    o.hide_render = True
                    st._key(o, "hide_render", b, "CONSTANT")
                    o.hide_render = False  # leave the python-side value visible (keys drive render)
            if st._span is not None:       # nested spans: parent also owns these objects
                st._span_objs.extend(objs)

    def span(self, t0: float, t1: float):
        return Stage._Span(self, t0, t1)

    # ------------------------------------------------------------------ primitives
    def rect(self, x, y, w, h, color, z=0.0, anchor="c", rot=0.0, alpha=1.0, name=None):
        o = bpy.data.objects.new(name or self._next("rect"), self._mesh_cache[anchor])
        self._link(o)
        o.location, o.scale = (x, y, z), (w, h, 1)
        o.rotation_euler[2] = math.radians(rot)
        o.color = rgba(color, alpha)
        return self._register(o, alpha, (x, y, z), (w, h, 1), rot)

    def circle(self, x, y, r, color, z=0.0, alpha=1.0):
        o = bpy.data.objects.new(self._next("circ"), self._mesh_cache["circle"])
        self._link(o)
        o.location, o.scale = (x, y, z), (r, r, 1)
        o.color = rgba(color, alpha)
        return self._register(o, alpha, (x, y, z), (r, r, 1))

    def ellipse(self, x, y, rx, ry, color, z=0.0, alpha=1.0):
        o = bpy.data.objects.new(self._next("ell"), self._mesh_cache["circle"])
        self._link(o)
        o.location, o.scale = (x, y, z), (rx, ry, 1)
        o.color = rgba(color, alpha)
        return self._register(o, alpha, (x, y, z), (rx, ry, 1))

    def ring(self, x, y, r, thick, color, z=0.0, alpha=1.0):
        n = 48
        ri = max(r - thick, 0.001)
        verts = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), 0) for i in range(n)] + \
                [(ri * math.cos(2 * math.pi * i / n), ri * math.sin(2 * math.pi * i / n), 0) for i in range(n)]
        faces = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
        me = bpy.data.meshes.new(self._next("ringm"))
        me.from_pydata(verts, [], faces)
        o = bpy.data.objects.new(self._next("ring"), me)
        self._link(o)
        o.location = (x, y, z)
        o.color = rgba(color, alpha)
        return self._register(o, alpha, (x, y, z))

    def poly(self, pts, color, z=0.0, alpha=1.0):
        """Filled polygon from world-space points (convex or simple)."""
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        me = bpy.data.meshes.new(self._next("polym"))
        me.from_pydata([(p[0] - cx, p[1] - cy, 0) for p in pts], [], [tuple(range(len(pts)))])
        o = bpy.data.objects.new(self._next("poly"), me)
        self._link(o)
        o.location = (cx, cy, z)
        o.color = rgba(color, alpha)
        return self._register(o, alpha, (cx, cy, z))

    def line(self, pts, color, width=0.05, z=0.0, alpha=1.0, closed=False):
        cv = bpy.data.curves.new(self._next("ln"), "CURVE")
        cv.dimensions = "3D"
        sp = cv.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for i, p in enumerate(pts):
            sp.points[i].co = (p[0], p[1], 0, 1)
        sp.use_cyclic_u = closed
        cv.bevel_depth = width / 2
        cv.bevel_resolution = 1
        cv.fill_mode = "FULL"
        o = bpy.data.objects.new(self._next("line"), cv)
        self._link(o)
        o.location = (0, 0, z)
        o.color = rgba(color, alpha)
        return self._register(o, alpha, (0, 0, z))

    def dashed(self, p0, p1, color, width=0.04, dash=0.18, gap=0.12, z=0.0, alpha=1.0):
        """Dashed straight line as a list of small rect objects."""
        (x0, y0), (x1, y1) = p0, p1
        L = math.hypot(x1 - x0, y1 - y0)
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        out, s = [], 0.0
        while s < L:
            e = min(s + dash, L)
            m = (s + e) / 2
            out.append(self.rect(x0 + (x1 - x0) * m / L, y0 + (y1 - y0) * m / L, e - s, width, color, z, rot=ang, alpha=alpha))
            s += dash + gap
        return out

    def arrow(self, x0, y0, x1, y1, color, width=0.07, head=0.28, z=0.0, alpha=1.0):
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        shaft_len = max(L - head, 0.01)
        ang = math.degrees(math.atan2(uy, ux))
        shaft = self.rect(x0 + ux * shaft_len / 2, y0 + uy * shaft_len / 2, shaft_len, width, color, z, rot=ang, alpha=alpha)
        bx, by = x0 + ux * shaft_len, y0 + uy * shaft_len
        nx, ny = -uy, ux
        hw = head * 0.55
        tip = self.poly([(x1, y1), (bx + nx * hw, by + ny * hw), (bx - nx * hw, by - ny * hw)], color, z, alpha)
        return [shaft, tip]

    def _font(self, kind):
        if kind not in self._fonts:
            try:
                self._fonts[kind] = bpy.data.fonts.load(FONTS[kind])
            except Exception:
                self._fonts[kind] = None
        return self._fonts[kind]

    def text(self, s, x, y, size=0.3, color=P.TEXT, z=0.0, align="c", kind="sans", wrap=None, alpha=1.0, valign="c"):
        if wrap:
            s = "\n".join(textwrap.wrap(s, wrap)) if "\n" not in s else s
        cv = bpy.data.curves.new(self._next("tx"), "FONT")
        cv.body = s
        cv.size = max(size * TEXT_SCALE, MIN_TEXT)
        cv.align_x = {"c": "CENTER", "l": "LEFT", "r": "RIGHT"}[align]
        cv.align_y = {"c": "CENTER", "t": "TOP", "b": "BOTTOM"}[valign]
        cv.space_line = 1.05
        f = self._font(kind)
        if f is not None:
            cv.font = f
        o = bpy.data.objects.new(self._next("text"), cv)
        self._link(o)
        o.location = (x, y, z)
        o.color = rgba(color, alpha)
        return self._register(o, alpha, (x, y, z))

    # ------------------------------------------------------------------ colour/alpha helpers
    def _set_alpha(self, o, a):
        c = list(o.color)
        c[3] = a
        o.color = c

    def _key_color(self, o, t, interp="LINEAR"):
        self._key(o, "color", t, interp)

    def fade(self, objs, t0, t1, a0=0.0, a1=1.0):
        for o in as_list(objs):
            base = self.state[o]["alpha"]
            self._set_alpha(o, a0 * base)
            self._key_color(o, t0)
            self._set_alpha(o, a1 * base)
            self._key_color(o, t1)
            self.state[o]["color"] = tuple(o.color)

    def fade_in(self, objs, t, d=0.35):
        for o in as_list(objs):
            v = self._vis.setdefault(o, {})
            v["in"] = min(v.get("in", t), t)
            base = self.state[o]["alpha"]
            start = self._span[0] if self._span else 0.0
            if t > start + 1e-6:
                self._set_alpha(o, 0.0)
                self._key_color(o, start)
                self._key_color(o, t)
            else:
                self._set_alpha(o, 0.0)
                self._key_color(o, t)
            self._set_alpha(o, base)
            self._key_color(o, t + d)
            self.state[o]["color"] = tuple(o.color)

    def fade_out(self, objs, t, d=0.35):
        for o in as_list(objs):
            v = self._vis.setdefault(o, {})
            v["out"] = max(v.get("out", -1.0), t + d)
            base = self.state[o]["alpha"]
            self._set_alpha(o, base)
            self._key_color(o, t)
            self._set_alpha(o, 0.0)
            self._key_color(o, t + d)
            self.state[o]["color"] = tuple(o.color)

    def recolor(self, objs, t0, t1, color):
        for o in as_list(objs):
            cur = list(self.state[o]["color"])
            o.color = cur
            self._key_color(o, t0)
            new = rgba(color, self.state[o]["alpha"])
            o.color = new
            self._key_color(o, t1)
            self.state[o]["color"] = tuple(new)

    # ------------------------------------------------------------------ transforms
    def move(self, objs, t0, t1, dx=0.0, dy=0.0, to=None, interp="BEZIER"):
        for o in as_list(objs):
            s = self.state[o]
            x, y, z = s["loc"]
            o.location = (x, y, z)
            self._key(o, "location", t0, interp)
            nx, ny = (to[0], to[1]) if to is not None else (x + dx, y + dy)
            o.location = (nx, ny, z)
            self._key(o, "location", t1, interp)
            s["loc"] = (nx, ny, z)

    def scale_to(self, objs, t0, t1, sx=None, sy=None, interp="BEZIER"):
        for o in as_list(objs):
            s = self.state[o]
            cur = s["scale"]
            o.scale = cur
            self._key(o, "scale", t0, interp)
            new = (cur[0] if sx is None else sx, cur[1] if sy is None else sy, 1)
            o.scale = new
            self._key(o, "scale", t1, interp)
            s["scale"] = new

    def pop_in(self, objs, t, d=0.3):
        for o in as_list(objs):
            s = self.state[o]
            full = s["scale"]
            start = self._span[0] if self._span else 0.0
            o.scale = (0, 0, 0)
            self._key(o, "scale", start if t > start else t, "CONSTANT")
            if t > start:
                self._key(o, "scale", t, "BEZIER")
            o.scale = full
            self._key(o, "scale", t + d, "BEZIER")

    def rotate(self, objs, t0, t1, deg, interp="BEZIER"):
        for o in as_list(objs):
            s = self.state[o]
            o.rotation_euler[2] = math.radians(s["rot"])
            self._key(o, "rotation_euler", t0, interp, index=2)
            o.rotation_euler[2] = math.radians(deg)
            self._key(o, "rotation_euler", t1, interp, index=2)
            s["rot"] = deg

    def draw_on(self, line, t0, t1, interp="LINEAR"):
        """Reveal a line() object progressively."""
        cv = line.data
        start = self._span[0] if self._span else 0.0
        cv.bevel_factor_end = 0.0
        self._key(cv, "bevel_factor_end", start if t0 > start else t0, "CONSTANT")
        if t0 > start:
            self._key(cv, "bevel_factor_end", t0, interp)
        cv.bevel_factor_end = 1.0
        self._key(cv, "bevel_factor_end", t1, interp)

    def set_text_visible_chars(self, *a, **k):  # intentionally unsupported: use fade_in on separate text objects
        raise NotImplementedError

    # ------------------------------------------------------------------ camera
    def camera(self, t0, t1, cx=None, cy=None, width=None, interp="BEZIER"):
        cs = self._cam_state
        self.cam.location = (cs["x"], cs["y"], 20)
        self.cam.data.ortho_scale = cs["scale"]
        self._key(self.cam, "location", t0, interp)
        self._key(self.cam.data, "ortho_scale", t0, interp)
        cs["x"] = cs["x"] if cx is None else cx
        cs["y"] = cs["y"] if cy is None else cy
        cs["scale"] = cs["scale"] if width is None else width
        self.cam.location = (cs["x"], cs["y"], 20)
        self.cam.data.ortho_scale = cs["scale"]
        self._key(self.cam, "location", t1, interp)
        self._key(self.cam.data, "ortho_scale", t1, interp)

    # ------------------------------------------------------------------ frame planning + render
    def plan_frames(self, t0: float = 0.0, t1: float | None = None) -> list[int]:
        """Frames (1-based) that must be rendered: those where any animated value differs from the frame before."""
        t1 = self.duration if t1 is None else t1
        N = self.nframes
        changed = {1}
        for act in bpy.data.actions:
            for fc in act.fcurves:
                kp = fc.keyframe_points
                for a, b in zip(kp[:-1], kp[1:]):
                    if abs(a.co[1] - b.co[1]) < 1e-9:
                        continue
                    if a.interpolation == "CONSTANT":
                        changed.add(int(math.ceil(b.co[0] - 1e-9)))
                    else:
                        lo, hi = int(math.floor(a.co[0] + 1e-9)) + 1, int(math.ceil(b.co[0] - 1e-9))
                        changed.update(range(lo, hi + 1))
        f0, f1 = int(math.floor(self.fr(t0) + 1e-9)), int(math.ceil(self.fr(t1) - 1e-9)) - 1   # frames strictly before t1
        sel = sorted(f for f in changed if max(1, f0) <= f <= min(N, f1))
        first = max(1, f0)
        if first not in sel:
            sel.insert(0, first)
        return sel

    def render_frames(self, outdir: str, frames: list[int], t_limit: float | None = None, progress=True):
        os.makedirs(outdir, exist_ok=True)
        sc = self.sc
        done = 0
        for f in frames:
            path = os.path.join(outdir, f"frame_{f:05d}.png")
            if os.path.exists(path) and os.path.getsize(path) > 0:
                done += 1
                continue
            sc.frame_set(f)
            sc.render.filepath = path
            bpy.ops.render.render(write_still=True)
            done += 1
            if progress and done % 50 == 0:
                print(f"  rendered {done}/{len(frames)}", flush=True)
        return frames

    def write_concat(self, outdir: str, frames: list[int], last_frame: int | None = None):
        """ffmpeg concat-demuxer list: each rendered image is held until the next changed frame."""
        last = (self.nframes + 1 if last_frame is None else last_frame)
        lines = []
        for i, f in enumerate(frames):
            nxt = frames[i + 1] if i + 1 < len(frames) else last
            dur = max(nxt - f, 1) / self.fps
            lines.append(f"file 'frame_{f:05d}.png'\nduration {dur:.6f}")
        lines.append(f"file 'frame_{frames[-1]:05d}.png'")
        with open(os.path.join(outdir, "frames.txt"), "w") as fh:
            fh.write("\n".join(lines) + "\n")
