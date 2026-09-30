"""Procedural 3D models: geology diorama and the well itself."""
import math

import bpy
import bmesh
from mathutils import Vector

import bl
import palette as P

TAU = math.tau


def M(name, alpha=1.0, rough=0.5, metal=0.0, color=None, unique=False):
    col = color or getattr(P, name)
    return bl.mat(name + ('_u%d' % id(object()) if unique else ''), col, alpha=alpha,
                  rough=rough, metal=metal, unique=unique)


# ------------------------------------------------------------------ well geometry
# Real depths below seabed (m). Water depth 350 m.
WATER_DEPTH = 350.0

STRATA = [
    # name, top, bottom, colour, texture
    ('Soft clay', 0, 250, P.SOFT_CLAY, 'soft_clay'),
    ('Claystone', 250, 900, P.CLAYSTONE, 'claystone'),
    ('Siltstone', 900, 1500, P.SILTSTONE, 'siltstone'),
    ('Chalk', 1500, 2150, P.CHALK, 'chalk'),
    ('Claystone', 2150, 2800, '#A2957F', 'claystone2'),
    ('Cap rock', 2800, 2950, P.SHALE, 'shale'),
    ('Reservoir', 2950, 3100, P.RESERVOIR, 'reservoir'),
    ('Water zone', 3100, 3300, P.WATER_ZONE, 'water_zone'),
    ('Deeper rock', 3300, 3800, P.BASEMENT, 'basement'),
]
_TEX = None


def tex(name):
    global _TEX
    if _TEX is None:
        import textures
        _TEX = textures.build_all()
    return _TEX[name]


def strata_mat(texname):
    return bl.tex_mat('lith_' + texname, tex(texname))

# label, casing OD (in), hole size (in), shoe depth (m below seabed), hanger top (m)
CASINGS = [
    ('30" conductor', 30.0, 36.0, 80, 0),
    ('20" surface casing', 20.0, 26.0, 1000, 0),
    ('13⅜" intermediate casing', 13.375, 17.5, 2000, 0),
    ('9⅝" production casing', 9.625, 12.25, 2880, 0),
    ('7" liner', 7.0, 8.5, 3080, 2780),
]
TD = 3080.0


class Dio:
    """Diorama mapping: real metres -> scene units (vertical and radial exaggeration)."""

    def __init__(self, vscale=200.0, rscale=0.0105, water_depth=WATER_DEPTH):
        self.vs = vscale
        self.rk = rscale
        self.wd = water_depth

    def z(self, depth_m):
        return -depth_m / self.vs

    def r(self, inches):
        return inches * self.rk

    @property
    def sea_z(self):
        return self.wd / self.vs


def notched_slab(name, x0, x1, y0, y1, z0, z1, R, material, seg=40):
    """Box whose front face (y = y0) has a half-cylinder notch of radius R at x = 0."""
    outline = [(x0, y0)]
    if R > 0:
        outline.append((-R, y0))
        for i in range(1, seg):
            a = math.pi - math.pi * i / seg
            outline.append((R * math.cos(a), y0 + R * math.sin(a)))
        outline.append((R, y0))
    outline += [(x1, y0), (x1, y1), (x0, y1)]
    bm = bmesh.new()
    vb = [bm.verts.new((x, y, z0)) for x, y in outline]
    vt = [bm.verts.new((x, y, z1)) for x, y in outline]
    n = len(outline)
    bm.faces.new(vb[::-1])
    bm.faces.new(vt)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bl.link(o)
    me.materials.append(material)
    for p in me.polygons:
        p.use_smooth = True
    me.set_sharp_from_angle(angle=math.radians(25))
    return o


class Diorama:
    """Layered-earth cutaway block + sea, with a well drilled at x = 0, y = 0.

    Front (cut) face is the plane y = 0; the block extends into +Y.
    """

    def __init__(self, dio=None, width=16.0, depth=8.0, casings=CASINGS, strata=STRATA,
                 bottom=3800, well=True, cores=True, sea=True, x_center=0.0):
        self.dio = dio or Dio()
        self.width, self.depth = width, depth
        self.casings = casings
        self.objs = {'slabs': [], 'cores': [], 'casing': [], 'cement': [], 'sea': []}
        self.core_of = []  # (top_depth, bottom_depth, core_obj)
        d = self.dio
        x0, x1 = -width / 2 + x_center, width / 2 + x_center
        # split strata at section boundaries so each slab has one hole radius
        cuts = sorted({0} | {c[3] for c in casings} | {s[1] for s in strata} |
                      {s[2] for s in strata} | {bottom})
        cuts = [c for c in cuts if c <= bottom]
        seabed = bl.tex_mat('seabed', tex('seabed'))
        tscale = 1.6
        for a, b in zip(cuts[:-1], cuts[1:]):
            texname = next(s[4] for s in strata if s[1] <= a < s[2])
            R = self.hole_r(a + 0.5) if (well and a < TD) else 0.0
            m = strata_mat(texname)
            sl = notched_slab('slab_%d' % a, x0, x1, 0.0, depth, d.z(b), d.z(a), R, m)
            bl.uv_box(sl, tscale)
            if a == 0:
                sl.data.materials.append(seabed)
                for p in sl.data.polygons:
                    if p.normal.z > 0.9:
                        p.material_index = 1
            self.objs['slabs'].append(sl)
            if R > 0 and cores:
                core = bl.annulus('core_%d' % a, 0, R * 1.001, 0, d.z(a) - d.z(b), 0, math.pi,
                                  seg=40, material=m)
                core.location = (0, 0, d.z(b))
                bl.uv_box(core, tscale)
                self.objs['cores'].append(core)
                self.core_of.append((a, b, core))
        if sea:
            self.water = bl.box('water', (width, depth, d.sea_z),
                                loc=(x_center, depth / 2, d.sea_z / 2),
                                material=water_mat())
            self.water.visible_shadow = False
            self.objs['sea'].append(self.water)

    def hole_r(self, depth):
        prev = 0
        for (_, od, hole, shoe, top) in self.casings:
            if prev <= depth <= shoe:
                return self.dio.r(hole) / 2
            prev = shoe
        return 0.0

    # --------------------------------------------------------------- animation
    def drill(self, depth_frames):
        """depth_frames: list of (frame, depth_m) for the bit; cores shrink as it passes."""
        pts = sorted(depth_frames)

        def frame_at(depth):
            for (f0, d0), (f1, d1) in zip(pts[:-1], pts[1:]):
                if d0 <= depth <= d1 and d1 > d0:
                    return f0 + (f1 - f0) * (depth - d0) / (d1 - d0)
            return None

        for a, b, core in self.core_of:
            fa, fb = frame_at(a), frame_at(b)
            if fa is None and fb is None:
                if pts and pts[-1][1] >= b:
                    core.hide_render = True
                continue
            fa = fa if fa is not None else pts[0][0]
            fb = fb if fb is not None else pts[-1][0]
            bl.key(core, 'scale', max(0, int(fa) - 1), (1, 1, 1))
            bl.key(core, 'scale', int(round(fb)) + 1, (1, 1, 0.0))
            bl.linear_all(core)
            bl.hide_at(core, int(round(fb)) + 2)

    def pre_drilled(self, upto_depth):
        for a, b, core in self.core_of:
            if b <= upto_depth + 1e-6:
                core.hide_render = True


def water_mat(alpha=0.16, col='#3F9BE0'):
    m = bl.mat('water_vol_%g' % alpha, col, alpha=alpha, rough=0.2)
    m.use_backface_culling = True
    return m


def steel_mats():
    return (bl.mat('steel', P.STEEL, rough=0.3, metal=0.5),
            bl.mat('steel_cut', P.STEEL_CUT, rough=0.5))


def cement_mats():
    return (bl.tex_mat('cement', tex('cement')), bl.tex_mat('cement_cut', tex('cement')))


def casing_string(dio, i, casings=CASINGS, sector=(0.0, math.pi), name='casing',
                  with_cement=True, cement_top=None):
    """One casing string (half-shell cutaway) + its cement sheath."""
    label, od, hole, shoe, top = casings[i]
    a0, a1 = sector
    steel, steel_cut = steel_mats()
    cem, cem_cut = cement_mats()
    r_out = dio.r(od) / 2
    t = max(0.010, r_out * 0.12)
    z0, z1 = dio.z(shoe), dio.z(top)
    cs = bl.annulus('%s_%d' % (name, i), r_out - t, r_out, z0, z1, a0, a1, seg=64,
                    material=steel, cap_material=steel_cut)
    parts = {'casing': cs, 'cement': []}
    cs.visible_shadow = False
    if with_cement:
        prev_shoe = casings[i - 1][3] if i > 0 else 0
        r_hole = dio.r(hole) / 2
        # open-hole section: casing OD -> hole wall
        c = bl.annulus('%s_cem_oh_%d' % (name, i), r_out, r_hole, z0, dio.z(prev_shoe), a0, a1,
                       seg=64, material=cem, cap_material=cem_cut)
        bl.uv_cyl(c, 0.6)
        parts['cement'].append(c)
        # overlap inside previous casing, up to cement top
        ctop = cement_top if cement_top is not None else (0 if i < 2 else max(top, prev_shoe - 250))
        if i > 0 and ctop < prev_shoe:
            pod = casings[i - 1][1]
            pr = dio.r(pod) / 2
            pr_in = pr - max(0.010, pr * 0.12)
            c2 = bl.annulus('%s_cem_ov_%d' % (name, i), r_out, pr_in, dio.z(prev_shoe),
                            dio.z(ctop), a0, a1, seg=64, material=cem, cap_material=cem_cut)
            bl.uv_cyl(c2, 0.6)
            parts['cement'].append(c2)
    return parts


def grow_up(obj, f0, f1, base_z=None):
    """Animate an object growing upwards from its base (scale Z 0->1 about its bottom)."""
    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    zmin = min(v.z for v in bb) if base_z is None else base_z
    # shift origin to bottom
    me = obj.data
    off = zmin - obj.location.z
    for v in me.vertices:
        v.co.z -= off
    obj.location.z += off
    bl.key(obj, 'scale', f0, (1, 1, 0.001))
    bl.key(obj, 'scale', f1, (1, 1, 1))
    bl.show(obj, 0, False)
    bl.show(obj, f0, True)


def origin_to_bottom(obj):
    me = obj.data
    zmin = min(v.co.z for v in me.vertices)
    for v in me.vertices:
        v.co.z -= zmin
    obj.location.z += zmin * obj.scale.z
    return obj


def origin_to_top(obj):
    me = obj.data
    zmax = max(v.co.z for v in me.vertices)
    for v in me.vertices:
        v.co.z -= zmax
    obj.location.z += zmax * obj.scale.z
    return obj


def sea_surface(size=(16, 8), loc=(0, 4, 1.75), res=(160, 80), amp=0.035, name='Sea',
                col='#5AAEE3', alpha=0.55, wave_w=0.8, speed=1.0):
    """Subdivided plane with animated wave modifiers."""
    sx, sy = size
    nx, ny = res
    verts, faces = [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            verts.append((-sx / 2 + sx * i / nx, -sy / 2 + sy * j / ny, 0))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    m = bl.mat('sea_' + col + str(alpha), col, alpha=alpha, rough=0.12)
    o = bl.mesh_obj(name, verts, faces, m, smooth=True, loc=loc)
    o.visible_shadow = False
    for k, (w, sp, sx0, sy0) in enumerate(((1.0, 1.0, -sx * 1.3, -sy * 2.1),
                                            (0.6, 1.35, sx * 1.7, sy * 2.4),
                                            (0.35, 1.9, -sx * 2.2, sy * 1.6))):
        mod = o.modifiers.new('wave%d' % k, 'WAVE')
        mod.use_normal = False
        mod.height = amp * w
        mod.width = wave_w * w
        mod.speed = 0.010 * sp * speed
        mod.narrowness = 1.0
        mod.start_position_x = sx0
        mod.start_position_y = sy0
        mod.time_offset = -600
        mod.use_cyclic = True
        mod.falloff_radius = 0
    return o


def well_path(dio, pts_m, r=0.03, material=None, name='path'):
    """Curve tube along (x_m_scaled, depth_m) points in the XZ plane at y=0."""
    pts = [(x, 0.0, dio.z(dep)) for x, dep in pts_m]
    return bl.curve_tube(name, pts, r, material)


def ocean(size=(16, 8), loc=(0, 4, 1.75), res=(200, 100), spatial=10.0, wave_scale=0.4,
          wind=10.0, choppy=0.0, col='#3F95D6', alpha=0.72, frames=(0, 3000), speed=0.35,
          name='Ocean', seed=1, resolution=10, generate=False, repeat=(1, 1)):
    """Animated FFT ocean surface (Ocean modifier). Time runs linearly with frames."""
    m = bl.mat('ocean_%s_%g' % (col, alpha), col, alpha=alpha, rough=0.12)
    if generate:
        me = bpy.data.meshes.new(name)
        o = bpy.data.objects.new(name, me)
        bl.link(o)
        o.location = loc
    else:
        sx, sy = size
        nx, ny = res
        verts, faces = [], []
        for j in range(ny + 1):
            for i in range(nx + 1):
                verts.append((-sx / 2 + sx * i / nx, -sy / 2 + sy * j / ny, 0))
        for j in range(ny):
            for i in range(nx):
                a = j * (nx + 1) + i
                faces.append((a, a + 1, a + nx + 2, a + nx + 1))
        o = bl.mesh_obj(name, verts, faces, None, smooth=True, loc=loc)
    o.data.materials.append(m)
    mod = o.modifiers.new('ocean', 'OCEAN')
    mod.geometry_mode = 'GENERATE' if generate else 'DISPLACE'
    if generate:
        mod.repeat_x, mod.repeat_y = repeat
    mod.resolution = resolution
    mod.spatial_size = int(spatial)
    mod.wave_scale = wave_scale
    mod.wind_velocity = wind
    mod.choppiness = choppy
    mod.random_seed = seed
    mod.use_normals = True
    f0, f1 = frames
    mod.time = 1.0
    o.keyframe_insert('modifiers["ocean"].time', frame=f0)
    mod.time = 1.0 + (f1 - f0) / 24.0 * speed
    o.keyframe_insert('modifiers["ocean"].time', frame=f1)
    bl.linear_all(o)
    if generate:
        for p in o.data.polygons:
            p.use_smooth = True
    o.visible_shadow = False
    return o
