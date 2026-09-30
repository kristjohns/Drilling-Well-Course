"""Blender helper library for the subsea-well course video.

Everything is procedural: geometry, materials, lighting and animation are
built from Python so the whole video can be regenerated from source.
Rendering uses the Workbench engine (fast on CPU-only machines) with custom
studio lighting, cavity shading and soft shadows, and a transparent film so
that backgrounds and overlays can be composited afterwards.
"""
import json
import math
import os

import bpy  # noqa: F401  (must be imported before bmesh)
import bmesh
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Euler, Matrix, Vector

FPS = 24
W, H = 1920, 1080
TAU = math.tau


# ---------------------------------------------------------------- scene setup

def reset(fps=FPS):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = fps
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100
    return sc


def hex_rgba(h, a=1.0):
    """'#RRGGBB' -> linear RGBA tuple (Blender colours are scene-linear)."""
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (lin[0], lin[1], lin[2], a)


def setup_workbench(aa='8', shadows=True, cavity=True, outline=False,
                    light_dir=(0.45, -0.55, 0.70), shadow_intensity=0.28,
                    specular=True, lights='soft'):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.render_aa = aa
    sh = sc.display.shading
    sh.light = 'STUDIO'
    sh.studio_light = 'paint.sl'
    sh.use_world_space_lighting = False
    sh.color_type = 'TEXTURE'
    sh.show_shadows = shadows
    sh.shadow_intensity = shadow_intensity
    sh.show_cavity = cavity
    sh.cavity_type = 'BOTH'
    sh.cavity_ridge_factor = 0.8
    sh.cavity_valley_factor = 0.9
    sh.curvature_ridge_factor = 0.6
    sh.curvature_valley_factor = 0.7
    sh.show_specular_highlight = specular
    sh.show_object_outline = outline
    sh.object_outline_color = (0.08, 0.1, 0.13)
    sc.display.light_direction = Vector(light_dir).normalized()
    sc.display.shadow_shift = 0.05
    sc.display.shadow_focus = 0.25
    sc.render.film_transparent = True
    try:
        sc.view_settings.view_transform = 'Standard'
        sc.view_settings.look = 'None'
    except TypeError:
        pass
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.image_settings.compression = 20
    set_solid_lights(lights)


def set_solid_lights(style='soft'):
    """Custom 'studio' lights for the Workbench engine (camera space)."""
    s = bpy.context.preferences.system
    s.use_studio_light_edit = False
    if style == 'soft':
        cfg = [
            # direction (camera space), diffuse, specular, smooth
            ((-0.45, 0.55, 0.70), (0.78, 0.76, 0.72), (0.35, 0.35, 0.33), 0.55),  # warm key, upper left
            ((0.65, 0.15, 0.75), (0.30, 0.34, 0.40), (0.10, 0.12, 0.15), 0.80),   # cool fill, right
            ((0.00, 0.90, -0.35), (0.22, 0.24, 0.27), (0.25, 0.27, 0.30), 0.60),  # rim from top/back
            ((0.00, -0.60, 0.80), (0.12, 0.12, 0.12), (0.00, 0.00, 0.00), 1.00),  # soft bounce from below
        ]
        amb = (0.10, 0.11, 0.13)
    elif style == 'underwater':
        cfg = [
            ((-0.35, 0.75, 0.55), (0.62, 0.74, 0.80), (0.25, 0.32, 0.36), 0.60),
            ((0.70, 0.10, 0.70), (0.18, 0.28, 0.36), (0.05, 0.08, 0.10), 0.85),
            ((0.00, 0.95, -0.30), (0.20, 0.30, 0.36), (0.20, 0.28, 0.32), 0.60),
            ((0.00, -0.60, 0.80), (0.06, 0.10, 0.13), (0.00, 0.00, 0.00), 1.00),
        ]
        amb = (0.08, 0.13, 0.17)
    else:
        raise ValueError(style)
    for light, (d, dif, spec, sm) in zip(s.solid_lights, cfg):
        light.use = True
        light.direction = Vector(d).normalized()
        light.diffuse_color = dif
        light.specular_color = spec
        light.smooth = sm
    s.light_ambient = amb


# ---------------------------------------------------------------- materials

_MATS = {}


def mat(name, color, alpha=1.0, rough=0.5, metal=0.0, unique=False):
    """Workbench material (uses the viewport display colour)."""
    if isinstance(color, str):
        color = hex_rgba(color, alpha)
    else:
        color = tuple(color[:3]) + (alpha,)
    key = name
    if not unique and key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(name)
    m.diffuse_color = color
    m.roughness = rough
    m.metallic = metal
    if alpha < 1.0:
        try:
            m.surface_render_method = 'BLENDED'
        except AttributeError:
            pass
    _MATS[key] = m
    return m


_IMGS = {}


def tex_mat(name, path, rough=0.9, metal=0.0):
    """Material showing an image texture in Workbench TEXTURE colour mode."""
    if name in _MATS:
        return _MATS[name]
    img = _IMGS.get(path)
    if img is None:
        img = bpy.data.images.load(path)
        _IMGS[path] = img
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = img
    tex.interpolation = 'Linear'
    nt.links.new(tex.outputs['Color'], nt.nodes['Principled BSDF'].inputs['Base Color'])
    m.roughness = rough
    m.metallic = metal
    _MATS[name] = m
    return m


def uv_box(obj, scale=1.0, offset=(0.0, 0.0, 0.0)):
    """World-space box-projection UVs (1 texture tile per `scale` units)."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    uv = bm.loops.layers.uv.verify()
    mw = obj.matrix_world
    ox, oy, oz = offset
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for lp in f.loops:
            co = mw @ lp.vert.co
            x, y, z = co.x + ox, co.y + oy, co.z + oz
            if ax == 0:
                u, v = y, z
            elif ax == 1:
                u, v = x, z
            else:
                u, v = x, y
            lp[uv].uv = (u / scale, v / scale)
    bm.to_mesh(me)
    bm.free()


def uv_cyl(obj, scale=1.0):
    """Cylindrical UVs around the Z axis (for notch/hole walls and cores)."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    uv = bm.loops.layers.uv.verify()
    mw = obj.matrix_world
    for f in bm.faces:
        n = f.normal
        for lp in f.loops:
            co = mw @ lp.vert.co
            if abs(n.z) > 0.7:
                u, v = co.x, co.y
            elif abs(n.y) > 0.95:
                u, v = co.x, co.z
            else:
                r = math.hypot(co.x, co.y)
                u, v = math.atan2(co.y, co.x) * max(r, 0.2), co.z
            lp[uv].uv = (u / scale, v / scale)
    bm.to_mesh(me)
    bm.free()


def assign(obj, *mats):
    obj.data.materials.clear()
    for m in mats:
        obj.data.materials.append(m)
    return obj


# ---------------------------------------------------------------- objects

def link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj)
    return obj


def empty(name, loc=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None)
    o.location = loc
    link(o)
    if parent:
        o.parent = parent
    return o


def mesh_obj(name, verts, faces, material=None, smooth=False, sharp_angle=None,
             loc=(0, 0, 0), parent=None, face_mats=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.validate(clean_customdata=False)
    me.update()
    o = bpy.data.objects.new(name, me)
    o.location = loc
    link(o)
    if material is not None:
        mats = material if isinstance(material, (list, tuple)) else [material]
        for m in mats:
            me.materials.append(m)
    if face_mats is not None:
        for p, mi in zip(me.polygons, face_mats):
            p.material_index = mi
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
        if sharp_angle is not None:
            me.set_sharp_from_angle(angle=math.radians(sharp_angle))
    if parent:
        o.parent = parent
    return o


def annulus(name, r_in, r_out, z0, z1, a0=0.0, a1=TAU, seg=64, material=None,
            cap_material=None, loc=(0, 0, 0), parent=None):
    """Hollow (or solid if r_in==0) cylinder sector between angles a0..a1.

    Separate vertex rings per surface so curved faces shade smoothly while the
    flat caps and cut faces stay crisp. Material slot 0 = body, slot 1 = cut faces.
    """
    full = abs((a1 - a0) - TAU) < 1e-6
    n = max(3, int(round(seg * abs(a1 - a0) / TAU)))
    angs = [a0 + (a1 - a0) * i / n for i in range(n + (0 if full else 1))]
    verts, faces, fm, smooth_faces = [], [], [], []

    def ring(r, z):
        base = len(verts)
        for a in angs:
            verts.append((r * math.cos(a), r * math.sin(a), z))
        return base

    m = len(angs)
    segs = range(n) if not full else range(m)

    def strip(b0, b1, flip, mat_i=0, smooth=True):
        for i in segs:
            j = (i + 1) % m
            f = (b0 + i, b0 + j, b1 + j, b1 + i)
            faces.append(f[::-1] if flip else f)
            fm.append(mat_i)
            smooth_faces.append(smooth)

    # outer wall
    o0, o1 = ring(r_out, z0), ring(r_out, z1)
    strip(o0, o1, False)
    if r_in > 0:
        i0, i1 = ring(r_in, z0), ring(r_in, z1)
        strip(i0, i1, True)
        # top and bottom caps (annular)
        t0, t1 = ring(r_in, z1), ring(r_out, z1)
        strip(t0, t1, True, 0, False)
        b0, b1 = ring(r_in, z0), ring(r_out, z0)
        strip(b0, b1, False, 0, False)
    else:
        # solid caps as fans
        c_top = len(verts); verts.append((0, 0, z1))
        t = ring(r_out, z1)
        c_bot = len(verts); verts.append((0, 0, z0))
        b = ring(r_out, z0)
        for i in segs:
            j = (i + 1) % m
            faces.append((c_top, t + i, t + j)); fm.append(0); smooth_faces.append(False)
            faces.append((c_bot, b + j, b + i)); fm.append(0); smooth_faces.append(False)
    if not full:
        ci = 1 if cap_material is not None else 0
        for a, flip in ((a0, True), (a1, False)):
            ca, sa = math.cos(a), math.sin(a)
            base = len(verts)
            verts += [(r_in * ca, r_in * sa, z0), (r_out * ca, r_out * sa, z0),
                      (r_out * ca, r_out * sa, z1), (r_in * ca, r_in * sa, z1)]
            f = (base, base + 1, base + 2, base + 3)
            faces.append(f[::-1] if flip else f)
            fm.append(ci)
            smooth_faces.append(False)
    mats = [material] if material else []
    if cap_material is not None:
        mats.append(cap_material)
    o = mesh_obj(name, verts, faces, mats or None, loc=loc, parent=parent, face_mats=fm)
    for p, s in zip(o.data.polygons, smooth_faces):
        p.use_smooth = s
    # merge coincident verts only within the degenerate r_in==0 cut faces is unnecessary
    return o


def revolve(name, profile, seg=64, a0=0.0, a1=TAU, material=None, cap_material=None,
            loc=(0, 0, 0), parent=None, sharp_angle=35):
    """Lathe a closed (r, z) profile polygon about the Z axis.

    profile: list of (r, z) points, counter-clockwise, forming a closed outline.
    If the sweep is partial, the two cut faces are filled with the profile.
    """
    full = abs((a1 - a0) - TAU) < 1e-6
    n = max(3, int(round(seg * abs(a1 - a0) / TAU)))
    angs = [a0 + (a1 - a0) * i / n for i in range(n + (0 if full else 1))]
    m = len(angs)
    P = len(profile)
    verts, faces, fm = [], [], []
    for a in angs:
        ca, sa = math.cos(a), math.sin(a)
        for r, z in profile:
            verts.append((r * ca, r * sa, z))
    for i in (range(m) if full else range(m - 1)):
        j = (i + 1) % m
        for k in range(P):
            k2 = (k + 1) % P
            faces.append((i * P + k, j * P + k, j * P + k2, i * P + k2))
            fm.append(0)
    if not full:
        ci = 1 if cap_material is not None else 0
        for idx, flip in ((0, False), (m - 1, True)):
            a = angs[idx]
            ca, sa = math.cos(a), math.sin(a)
            base = len(verts)
            for r, z in profile:
                verts.append((r * ca, r * sa, z))
            f = list(range(base, base + P))
            faces.append(tuple(f[::-1] if flip else f))
            fm.append(ci)
    mats = [material] if material else []
    if cap_material is not None:
        mats.append(cap_material)
    o = mesh_obj(name, verts, faces, mats or None, loc=loc, parent=parent, face_mats=fm)
    me = o.data
    for p in me.polygons:
        p.use_smooth = True
    me.set_sharp_from_angle(angle=math.radians(sharp_angle))
    if not full:
        # triangulate the (possibly concave) cut faces for robust shading
        bm = bmesh.new(); bm.from_mesh(me)
        big = [f for f in bm.faces if len(f.verts) > 4]
        bmesh.ops.triangulate(bm, faces=big, quad_method='BEAUTY', ngon_method='EAR_CLIP')
        bm.to_mesh(me); bm.free()
    return o


def box(name, size, loc=(0, 0, 0), material=None, rot=(0, 0, 0), parent=None, bevel=0.0):
    sx, sy, sz = size
    v = [(-sx / 2, -sy / 2, -sz / 2), (sx / 2, -sy / 2, -sz / 2), (sx / 2, sy / 2, -sz / 2),
         (-sx / 2, sy / 2, -sz / 2), (-sx / 2, -sy / 2, sz / 2), (sx / 2, -sy / 2, sz / 2),
         (sx / 2, sy / 2, sz / 2), (-sx / 2, sy / 2, sz / 2)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    o = mesh_obj(name, v, f, material, loc=loc, parent=parent)
    o.rotation_euler = rot
    if bevel > 0:
        mod = o.modifiers.new('bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'NONE'
    return o


def cyl(name, r, depth, loc=(0, 0, 0), rot=(0, 0, 0), material=None, seg=48, parent=None,
        z_base=False):
    """Solid cylinder along local Z. If z_base, origin at the bottom face."""
    z0, z1 = (0, depth) if z_base else (-depth / 2, depth / 2)
    o = annulus(name, 0, r, z0, z1, seg=seg, material=material, loc=loc, parent=parent)
    o.rotation_euler = rot
    return o


def cone(name, r0, r1, depth, loc=(0, 0, 0), rot=(0, 0, 0), material=None, seg=32, parent=None):
    prof = [(0, 0), (r0, 0), (r1, depth), (0, depth)]
    prof = [(max(r, 1e-5), z) for r, z in prof]
    o = revolve(name, prof, seg=seg, material=material, loc=loc, parent=parent)
    o.rotation_euler = rot
    return o


def sphere(name, r, loc=(0, 0, 0), material=None, seg=24, rings=12, parent=None):
    prof = []
    for i in range(rings + 1):
        a = -math.pi / 2 + math.pi * i / rings
        prof.append((max(r * math.cos(a), 1e-5), r * math.sin(a)))
    o = revolve(name, prof, seg=seg, material=material, loc=loc, parent=parent, sharp_angle=80)
    return o


def rod(name, p0, p1, r, material=None, seg=12, parent=None):
    """Cylinder between two points (for trusses, lines)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    L = d.length
    o = annulus(name, 0, r, 0, L, seg=seg, material=material)
    o.location = p0
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    if parent:
        o.parent = parent
    return o


def join(objs, name=None):
    """Join objects into the first one (applies transforms of parts)."""
    objs = [o for o in objs if o is not None]
    ctx = bpy.context
    for o in ctx.selected_objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    ctx.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = ctx.view_layer.objects.active
    if name:
        o.name = name
    return o


def apply_transform(o):
    ctx = bpy.context
    for s in ctx.selected_objects:
        s.select_set(False)
    o.select_set(True)
    ctx.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def curve_tube(name, pts, r, material=None, res=12, closed=False, parent=None, smooth=True):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = r
    cu.bevel_resolution = max(1, res // 4)
    cu.use_fill_caps = True
    cu.resolution_u = 12
    sp = cu.splines.new('POLY' if not smooth else 'BEZIER')
    if smooth:
        sp.bezier_points.add(len(pts) - 1)
        for bp, p in zip(sp.bezier_points, pts):
            bp.co = p
            bp.handle_left_type = bp.handle_right_type = 'AUTO'
    else:
        sp.points.add(len(pts) - 1)
        for pp, p in zip(sp.points, pts):
            pp.co = (p[0], p[1], p[2], 1)
    sp.use_cyclic_u = closed
    o = bpy.data.objects.new(name, cu)
    link(o)
    if material:
        cu.materials.append(material)
    if parent:
        o.parent = parent
    cu.bevel_factor_mapping_start = 'SPLINE'
    cu.bevel_factor_mapping_end = 'SPLINE'
    return o


# ---------------------------------------------------------------- animation

def ease_keys(obj, prop, index=-1, interp='BEZIER', easing='AUTO'):
    ad = obj.animation_data if hasattr(obj, 'animation_data') else None
    if not ad or not ad.action:
        return
    for fc in _fcurves(ad.action):
        if fc.data_path == prop and (index < 0 or fc.array_index == index):
            for kp in fc.keyframe_points:
                kp.interpolation = interp
                kp.easing = easing


def _fcurves(action):
    """Blender 5 layered actions keep fcurves inside channelbags."""
    if hasattr(action, 'fcurves') and action.fcurves is not None:
        try:
            return list(action.fcurves)
        except Exception:
            pass
    out = []
    for layer in getattr(action, 'layers', []):
        for strip in layer.strips:
            for bag in strip.channelbags:
                out += list(bag.fcurves)
    return out


def key(obj, prop, frame, value=None, index=-1, interp=None):
    """Set (optionally) and keyframe a property. Returns obj for chaining."""
    if value is not None:
        tgt, attr = _resolve(obj, prop)
        if index >= 0:
            getattr(tgt, attr)[index] = value
        else:
            setattr(tgt, attr, value)
    obj.keyframe_insert(data_path=prop, frame=frame, index=index)
    if interp:
        ad = obj.animation_data
        for fc in _fcurves(ad.action):
            if fc.data_path == prop:
                for kp in fc.keyframe_points:
                    if abs(kp.co[0] - frame) < 1e-3:
                        kp.interpolation = interp
    return obj


def _resolve(obj, path):
    parts = path.split('.')
    tgt = obj
    for p in parts[:-1]:
        tgt = getattr(tgt, p)
    return tgt, parts[-1]


def move(obj, f0, f1, v0, v1, prop='location', interp=None):
    key(obj, prop, f0, Vector(v0) if len(v0) == 3 else v0, interp=interp)
    key(obj, prop, f1, Vector(v1) if len(v1) == 3 else v1, interp=interp)


def show(obj, frame, visible=True, recursive=True):
    """Hard visibility switch at a frame (constant interpolation)."""
    objs = [obj] + (list(obj.children_recursive) if recursive else [])
    for o in objs:
        o.hide_render = not visible
        o.keyframe_insert('hide_render', frame=frame)
        for fc in _fcurves(o.animation_data.action):
            if fc.data_path == 'hide_render':
                for kp in fc.keyframe_points:
                    kp.interpolation = 'CONSTANT'


def hide_at(obj, frame, recursive=True):
    """Visible until `frame`, hidden from then on."""
    show(obj, 0, True, recursive)
    show(obj, max(1, frame), False, recursive)


def visible_between(obj, f_in, f_out=None, recursive=True):
    show(obj, 0, False, recursive)
    show(obj, f_in, True, recursive)
    if f_out is not None:
        show(obj, f_out, False, recursive)


def pop_in(obj, f, dur=10, scale=None):
    s = Vector(scale or obj.scale)
    key(obj, 'scale', f, Vector((0.001, 0.001, 0.001)))
    key(obj, 'scale', f + dur, s)
    show(obj, 0, False)
    show(obj, f, True)


def fade(material, f0, f1, a0, a1):
    c = list(material.diffuse_color)
    c[3] = a0
    material.diffuse_color = c
    material.keyframe_insert('diffuse_color', index=3, frame=f0)
    c[3] = a1
    material.diffuse_color = c
    material.keyframe_insert('diffuse_color', index=3, frame=f1)
    try:
        material.surface_render_method = 'BLENDED'
    except AttributeError:
        pass


def color_to(material, f0, f1, c0, c1):
    for f, c in ((f0, c0), (f1, c1)):
        if isinstance(c, str):
            c = hex_rgba(c, material.diffuse_color[3])
        material.diffuse_color = c
        material.keyframe_insert('diffuse_color', frame=f)


def spin(obj, f0, f1, turns, axis=2, start=0.0):
    """Constant-speed rotation about a local axis."""
    obj.rotation_mode = 'XYZ'
    r = list(obj.rotation_euler)
    r[axis] = start
    obj.rotation_euler = r
    obj.keyframe_insert('rotation_euler', index=axis, frame=f0)
    r[axis] = start + TAU * turns
    obj.rotation_euler = r
    obj.keyframe_insert('rotation_euler', index=axis, frame=f1)
    for fc in _fcurves(obj.animation_data.action):
        if fc.data_path == 'rotation_euler' and fc.array_index == axis:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'


def linear_all(obj):
    if obj.animation_data and obj.animation_data.action:
        for fc in _fcurves(obj.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'


# ---------------------------------------------------------------- camera

class Cam:
    """Camera that always looks at a target empty; both are keyframed."""

    def __init__(self, loc, target, lens=35, ortho=None, clip=(0.05, 5000)):
        cd = bpy.data.cameras.new('Cam')
        cd.lens = lens
        cd.clip_start, cd.clip_end = clip
        if ortho:
            cd.type = 'ORTHO'
            cd.ortho_scale = ortho
        self.obj = bpy.data.objects.new('Cam', cd)
        link(self.obj)
        self.obj.location = loc
        self.target = empty('CamTarget', target)
        c = self.obj.constraints.new('TRACK_TO')
        c.target = self.target
        c.track_axis = 'TRACK_NEGATIVE_Z'
        c.up_axis = 'UP_Y'
        bpy.context.scene.camera = self.obj
        self.data = cd

    def key(self, frame, loc=None, target=None, lens=None, ortho=None, roll=None):
        if loc is not None:
            self.obj.location = loc
            self.obj.keyframe_insert('location', frame=frame)
        if target is not None:
            self.target.location = target
            self.target.keyframe_insert('location', frame=frame)
        if lens is not None:
            self.data.lens = lens
            self.data.keyframe_insert('lens', frame=frame)
        if ortho is not None:
            self.data.ortho_scale = ortho
            self.data.keyframe_insert('ortho_scale', frame=frame)
        return self

    def hold(self, frame):
        """Duplicate the current pose at `frame` (for pauses between moves)."""
        return self.key(frame, loc=self.obj.location.copy(), target=self.target.location.copy(),
                        lens=self.data.lens)

    def orbit(self, f0, f1, center, radius, height, a0, a1, lens=None, steps=None, target=None):
        """Keyframed circular move around `center` (angles in degrees)."""
        steps = steps or max(2, int(abs(a1 - a0) / 15) + 1)
        for i in range(steps + 1):
            t = i / steps
            a = math.radians(a0 + (a1 - a0) * t)
            f = f0 + (f1 - f0) * t
            loc = (center[0] + radius * math.cos(a), center[1] + radius * math.sin(a),
                   center[2] + height)
            self.key(f, loc=loc, target=target or center, lens=lens)
        # linear in between inner keys so the orbit keeps constant speed
        for fc in _fcurves(self.obj.animation_data.action):
            for kp in fc.keyframe_points:
                if f0 < kp.co[0] < f1:
                    kp.interpolation = 'BEZIER'


# ---------------------------------------------------------------- anchors / export

def export_anchors(path, anchors, f0, f1):
    """Project 3D anchor points to pixel coordinates for every frame.

    anchors: dict name -> object | (object, (dx,dy,dz)) | (x,y,z)
    Writes {frame: {name: [x, y, depth, visible]}} to JSON.
    """
    sc = bpy.context.scene
    cam = sc.camera
    out = {}
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        fr = {}
        for name, a in anchors.items():
            if isinstance(a, tuple) and len(a) == 2 and a[0] == 'horizon':
                m = cam.matrix_world
                fwd = -(m.to_3x3() @ Vector((0, 0, 1)))
                fwd.z = 0
                fwd.normalize()
                p = m.translation + fwd * a[1]
                p.z = 0
                vis = True
            elif isinstance(a, tuple) and len(a) == 2 and hasattr(a[0], 'matrix_world'):
                p = a[0].matrix_world @ Vector(a[1])
                vis = not a[0].hide_render
            elif hasattr(a, 'matrix_world'):
                p = a.matrix_world.translation.copy()
                vis = not a.hide_render
            else:
                p = Vector(a)
                vis = True
            co = world_to_camera_view(sc, cam, p)
            fr[name] = [round(co.x * W, 2), round((1 - co.y) * H, 2), round(co.z, 3), bool(vis)]
        cd = cam.data
        fr['_cam'] = [list(map(lambda x: round(x, 4), cam.matrix_world.translation)), cd.lens]
        out[f] = fr
    with open(path, 'w') as fh:
        json.dump(out, fh)


def render(out_dir, f0, f1, aa=None):
    sc = bpy.context.scene
    os.makedirs(out_dir, exist_ok=True)
    if aa:
        sc.display.render_aa = aa
    sc.frame_start, sc.frame_end = f0, f1
    sc.render.filepath = os.path.join(out_dir, '')
    sc.render.use_overwrite = False
    sc.render.use_placeholder = True
    bpy.ops.render.render(animation=True)


def render_still(path, frame):
    sc = bpy.context.scene
    sc.frame_set(frame)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------- booleans

def boolean(obj, cutter, op='DIFFERENCE', remove_cutter=True, transfer=True):
    m = obj.modifiers.new('bool', 'BOOLEAN')
    m.object = cutter
    m.operation = op
    m.solver = 'EXACT'
    try:
        m.material_mode = 'TRANSFER' if transfer else 'INDEX'
    except (AttributeError, TypeError):
        pass
    with bpy.context.temp_override(object=obj, active_object=obj):
        bpy.ops.object.modifier_apply(modifier=m.name)
    if remove_cutter:
        bpy.data.objects.remove(cutter, do_unlink=True)
    return obj


def cut_half(obj, cap_mat=None, plane_y=0.0, size=400.0, keep='pos'):
    """Cut away the half of `obj` with y < plane_y (keep='pos') for cutaway views."""
    cy = plane_y - size / 2 if keep == 'pos' else plane_y + size / 2
    mw = obj.matrix_world
    cutter = box('_cutter', (size, size, size), loc=(mw.translation.x, cy, mw.translation.z),
                 material=cap_mat)
    return boolean(obj, cutter)
