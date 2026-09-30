"""Scene 12 - Completion: liner, perforating, tubing, packer, safety valve, christmas tree."""
import math
import random

import gfx as G
import overlays as O
import palette as P
import schem
import well2d as W2
from scene_base import Scene
from scenes.s07_tophole import underwater_bg

RS = 5.0
R_CSG_O, R_CSG_I, R_HOLE12 = 0.1222 * RS, 0.1100 * RS, 0.1556 * RS
R_LNR_O, R_LNR_I, R_HOLE8 = 0.0889 * RS, 0.0790 * RS, 0.1080 * RS
R_TBG_O, R_TBG_I = 0.0571 * RS, 0.0500 * RS
Z_TOP, Z_SHOE, Z_LTOP, Z_TD = 55.0, 6.0, 8.0, -11.0
Z_RES_T, Z_RES_B = 4.0, -12.0
Z_CAP_T = 10.0
Z_PKR = 16.0
Z_DHSV = 45.0
GUN = (-9.0, 1.0)
SEA_X = 300.0   # the seabed set is built far away and reached by a camera cut


class S(Scene):
    ID = 's12_completion'
    BLENDER = True
    PHASE = 2
    TRACKER_IN = 3.8

    def __init__(self):
        super().__init__()
        tl = self.tl
        self.T = dict(
            card_out=3.9,
            hole=tl.word('co1', 'hole lined with steel'),
            producer=tl.word('co1', 'producer'),
            liner=tl.word('co2', 'seven-inch liner'),
            guns=tl.word('co2', 'perforating guns'),
            charge=tl.word('co3', 'shaped charge'),
            seven=tl.word('co3', 'seven kilometers'),
            punching=tl.word('co3', 'punching'),
            deep=tl.word('co3', 'deep into the reservoir'),
            upper=tl.word('co4', 'upper completion'),
            tubing=tl.word('co4', 'production tubing'),
            flow=tl.word('co4', 'flow through'),
            packer=tl.word('co5', 'production packer'),
            seals=tl.word('co5', 'seals the gap'),
            dhsv=tl.word('co6', 'downhole safety valve'),
            hydraulic=tl.word('co6', 'hydraulic pressure'),
            lose=tl.word('co6', 'Lose that pressure'),
            snaps=tl.word('co6', 'snaps shut'),
            pulled=tl.word('co7', 'pulled'),
            tree=tl.word('co7', 'christmas tree'),
            valves=tl.word('co7', 'compact assembly'),
            flowlines=tl.word('co8', 'flowlines'),
            umbilical=tl.word('co8', 'umbilical'),
            chemicals=tl.word('co8', 'chemicals'),
            cleaned=tl.word('co9', 'cleaned up'),
            two=tl.word('co9', 'Two barriers'),
            blue=tl.word('co9', 'in blue'),
            red=tl.word('co9', 'in red'),
        )
        T = self.T
        self.t_fire = T['charge'] + 0.4
        self.t_sea = tl.t('co7') - 0.6
        self.t_2d = tl.t('co9') - 0.8
        rnd = random.Random(12)
        self.flow_ph = [rnd.uniform(0, 1) for _ in range(60)]

    def render_ranges(self):
        return [(0, int(round((self.t_2d + 0.8) * 24)))]

    def draw_bg(self, ctx, t, f):
        if self.t_sea - 0.2 < t < self.t_2d + 0.8:
            underwater_bg(ctx, t)
        else:
            G.bg_gradient(ctx)

    # ------------------------------------------------------------------ 3D
    def build(self):
        import bl
        import equipment as E
        import models as MD
        from mathutils import Vector
        tl = self.tl
        T = self.T
        F = lambda s: int(round(s * 24))  # noqa: E731
        M = E.mats()
        cut = bl.mat('cmp_cut', '#C3CDD7', rough=0.5)
        steel = bl.mat('cmp_steel', '#A7B4C1', rough=0.35, metal=0.15)
        tbg_m = bl.mat('cmp_tbg', '#5E8FC9', rough=0.35)          # tubing: blue-ish steel
        cem, cem_cut = MD.cement_mats()
        # ---------------- rock
        layers = [(Z_TOP, Z_CAP_T, 'claystone2'), (Z_CAP_T, Z_RES_T, 'shale'),
                  (Z_RES_T, Z_RES_B, 'reservoir'), (Z_RES_B, -16.0, 'water_zone')]
        for (zt, zb, tex) in layers:
            m = MD.strata_mat(tex)
            cuts = sorted({zt, zb} | ({Z_SHOE} if zb < Z_SHOE < zt else set()) |
                          ({Z_TD} if zb < Z_TD < zt else set()), reverse=True)
            for a, b in zip(cuts[:-1], cuts[1:]):
                mid = (a + b) / 2
                R = R_HOLE12 if mid > Z_SHOE else (R_HOLE8 if mid > Z_TD else 0.0)
                sl = MD.notched_slab('rock', -7, 7, 0, 7, b, a, R, m, seg=48)
                bl.uv_box(sl, 2.2)
        # ---------------- casing, liner, cement
        a0, a1 = 0.0, math.pi
        bl.annulus('prod_csg', R_CSG_I, R_CSG_O, Z_SHOE, Z_TOP, a0, a1, 64, steel, cut)
        c1 = bl.annulus('csg_cem', R_CSG_O, R_HOLE12, Z_SHOE, Z_TOP, a0, a1, 64, cem, cem_cut)
        bl.annulus('liner', R_LNR_I, R_LNR_O, Z_TD, Z_LTOP, a0, a1, 64, steel, cut)
        c2 = bl.annulus('lnr_cem', R_LNR_O, R_HOLE8, Z_TD, Z_SHOE, a0, a1, 64, cem, cem_cut)
        c3 = bl.annulus('lnr_cem2', R_LNR_O, R_CSG_I, Z_SHOE, Z_LTOP, a0, a1, 64, cem, cem_cut)
        for c in (c1, c2, c3):
            bl.uv_cyl(c, 1.0)
        # liner hanger ring
        bl.annulus('lnr_hanger', R_LNR_O, R_CSG_I, Z_LTOP - 0.4, Z_LTOP, a0, a1, 64,
                   M['steel_dark'], cut)
        # ---------------- perforating gun
        g0, g1 = GUN
        gun = bl.empty('gun_grp')
        gbody = bl.annulus('gun', 0, 0.16, g0, g1, a0, a1, 48, bl.mat('gun', '#3F4A55', rough=0.4), cut)
        gbody.parent = gun
        wire = bl.cyl('gun_wire', 0.02, 60, loc=(0, 0.0, g1 + 30), material=M['dark'], seg=8)
        wire.parent = gun
        bl.key(gun, 'location', F(T['guns'] - 1.0), (0, 0, 30.0))
        bl.key(gun, 'location', F(self.t_fire - 0.4), (0, 0, 0.0))
        bl.key(gun, 'location', F(T['deep'] + 1.0), (0, 0, 0.0))
        bl.key(gun, 'location', F(T['upper'] - 0.2), (0, 0, 40.0))
        bl.visible_between(gun, F(T['guns'] - 1.1), F(T['upper'] - 0.1))
        # charges, jets and tunnels (only directions visible in the cutaway)
        jet_m = bl.mat('jet', '#FFE7A0', rough=0.2)
        tun_m = bl.mat('tunnel', '#3A2A12', rough=0.9)
        dirs = [0.0, math.pi / 3, 2 * math.pi / 3, math.pi]
        self_tunnels = []
        k = 0
        for z in [g0 + 0.8 + i * 0.75 for i in range(12)]:
            ang = dirs[k % 4]
            k += 1
            d = Vector((math.cos(ang), math.sin(ang), 0))
            tf = self.t_fire + 0.03 * k
            jet = bl.cone('jet', 0.07, 0.005, 1.6, material=jet_m, seg=12)
            jet.location = Vector((0, 0, z)) + d * 0.15
            jet.rotation_mode = 'QUATERNION'
            jet.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
            bl.key(jet, 'scale', F(tf), (1, 1, 0.01))
            bl.key(jet, 'scale', F(tf) + 3, (1, 1, 1))
            bl.key(jet, 'scale', F(tf) + 8, (0.3, 0.3, 1.05))
            bl.visible_between(jet, F(tf), F(tf) + 9)
            if abs(math.sin(ang)) < 1e-6:
                self_tunnels.append((z, math.copysign(1, math.cos(ang)), tf))

        # ---------------- tubing string with packer and DHSV (run in from above)
        tb = bl.empty('tubing_grp')
        bl.annulus('tubing', R_TBG_I, R_TBG_O, Z_PKR - 4, Z_TOP + 30, a0, a1, 48, tbg_m, cut).parent = tb
        # packer mandrel + slips + rubber elements
        bl.annulus('pkr_body', R_TBG_O, R_TBG_O + 0.05, Z_PKR - 0.8, Z_PKR + 1.4, a0, a1, 48,
                   M['steel_dark'], cut).parent = tb
        rubbers = []
        for j in range(3):
            rb = bl.annulus('pkr_rubber', R_TBG_O + 0.04, R_TBG_O + 0.11, Z_PKR + j * 0.34,
                            Z_PKR + j * 0.34 + 0.3, a0, a1, 48, M['rubber'], M['rubber'])
            rb.parent = tb
            rubbers.append(rb)
        slips = bl.annulus('pkr_slips', R_TBG_O + 0.05, R_TBG_O + 0.09, Z_PKR - 0.7, Z_PKR - 0.3,
                           a0, a1, 48, M['yellow'], M['yellow'])
        slips.parent = tb
        # DHSV body, flow tube and flapper
        bl.annulus('dhsv_body', R_TBG_O, R_TBG_O + 0.07, Z_DHSV - 1.2, Z_DHSV + 1.2, a0, a1, 48,
                   bl.mat('dhsv', '#E0342F', rough=0.4), cut).parent = tb
        flap = bl.cyl('flapper', R_TBG_I * 0.97, 0.04, material=bl.mat('flap', '#F2B705'), seg=32)
        hinge = bl.empty('hinge', (-R_TBG_I * 0.95, 0.0, Z_DHSV - 0.2))
        hinge.parent = tb
        flap.parent = hinge
        flap.location = (R_TBG_I * 0.95, 0, 0)
        # control line on the back side
        cl = bl.cyl('control_line', 0.025, Z_TOP + 30 - Z_DHSV, loc=(0, R_TBG_O + 0.06,
                    (Z_TOP + 30 + Z_DHSV) / 2), material=M['yellow'], seg=8)
        cl.parent = tb
        f_run0, f_run1 = F(T['tubing'] - 0.8), F(T['packer'] - 0.4)
        bl.key(tb, 'location', f_run0, (0, 0, 32.0))
        bl.key(tb, 'location', f_run1, (0, 0, 0.0))
        bl.visible_between(tb, f_run0, F(self.t_sea))
        # packer setting: rubbers expand to the casing wall
        grow = (R_CSG_I - 0.005) / (R_TBG_O + 0.11)
        for j, rb in enumerate(rubbers):
            bl.key(rb, 'scale', F(T['seals'] - 0.5), (1, 1, 1))
            bl.key(rb, 'scale', F(T['seals'] + 0.6), (grow, grow, 1))
        bl.key(slips, 'scale', F(T['seals'] - 0.7), (1, 1, 1))
        bl.key(slips, 'scale', F(T['seals'] + 0.2), (grow * 0.98, grow * 0.98, 1))
        # flapper: open (vertical, against the wall) -> snaps shut -> reopens
        bl.key(hinge, 'rotation_euler', F(T['dhsv']), (0, -math.pi / 2, 0))
        bl.key(hinge, 'rotation_euler', F(T['snaps'] - 0.15), (0, -math.pi / 2, 0))
        bl.key(hinge, 'rotation_euler', F(T['snaps'] + 0.15), (0, 0, 0))
        bl.key(hinge, 'rotation_euler', F(self.t_sea - 1.5), (0, 0, 0))
        bl.key(hinge, 'rotation_euler', F(self.t_sea - 0.8), (0, -math.pi / 2, 0))
        hinge.rotation_euler = (0, -math.pi / 2, 0)

        # ---------------- seabed set: BOP pulled, tree installed, tie-in
        root = bl.empty('seabed_set', (SEA_X, 0, 0))
        seabed = bl.tex_mat('seabed', MD.tex('seabed'))
        bed = bl.box('bed', (300, 300, 0.4), loc=(SEA_X, 0, -0.2), material=seabed)
        bl.uv_box(bed, 6.0)
        wh = E.wellhead(M, cut=False)
        for o in list(wh.values()):
            if hasattr(o, 'location'):
                o.location.x += SEA_X
        bop = E.BOP(M, cut=False, name='BOP_cmp')
        rs = E.riser(M, 12.8, 300, name='riser_cmp')
        rs.parent = bop.root
        f_s = F(self.t_sea)
        bl.key(bop.root, 'location', f_s, (SEA_X, 0, 2.3))
        bl.key(bop.root, 'location', F(T['pulled'] + 1.2), (SEA_X, 0, 60.0))
        bl.hide_at(bop.root, F(T['pulled'] + 1.3))
        xt = E.xmas_tree(M)
        bl.key(xt, 'location', F(T['pulled'] + 1.0), (SEA_X, 0, 40.0))
        bl.key(xt, 'location', F(T['tree'] + 0.2), (SEA_X, 0, 2.6))
        # wire it hangs from
        xw = bl.cyl('xt_wire', 0.03, 80, loc=(0, 0, 44), material=M['dark'], seg=8)
        xw.parent = xt
        bl.hide_at(xw, F(T['tree'] + 0.8))
        # manifold, jumper and umbilical
        mf = E.manifold(M)
        mf.location = (SEA_X + 16, 3, 0)
        jumper_pts = [(SEA_X + 3.2, 0, 5.2), (SEA_X + 5, 0, 7.5), (SEA_X + 9.5, 1.5, 7.5),
                      (SEA_X + 10.5, 3, 2.2)]
        jp = bl.curve_tube('jumper', jumper_pts, 0.16, M['yellow'])
        jp.location.z = 0
        bl.key(jp, 'location', F(T['flowlines'] - 1.0), (0, 0, 18.0))
        bl.key(jp, 'location', F(T['flowlines'] + 0.6), (0, 0, 0.0))
        bl.visible_between(jp, F(T['flowlines'] - 1.1))
        umb_pts = [(SEA_X - 60, 30, 0.15), (SEA_X - 20, 12, 0.15), (SEA_X - 6, 4, 0.15),
                   (SEA_X - 2.5, 1.3, 3.0)]
        um = bl.curve_tube('umbilical', umb_pts, 0.14, bl.mat('umb', '#F59E1B', rough=0.5))
        um.data.bevel_factor_end = 0.0
        um.data.keyframe_insert('bevel_factor_end', frame=F(T['umbilical'] - 0.6))
        um.data.bevel_factor_end = 1.0
        um.data.keyframe_insert('bevel_factor_end', frame=F(T['umbilical'] + 1.2))
        rov = E.rov(M)
        bl.key(rov, 'location', f_s, (SEA_X - 8, -7, 6))
        bl.key(rov, 'location', F(T['tree'] + 1.0), (SEA_X - 5, -5, 4.5))
        bl.key(rov, 'location', F(T['flowlines'] + 1.5), (SEA_X + 7, -4, 5.0))
        bl.key(rov, 'location', F(self.t_2d + 1), (SEA_X + 6, -5, 5.5))
        bl.key(rov, 'rotation_euler', f_s, (0, 0, 0.3))
        bl.key(rov, 'rotation_euler', F(self.t_2d + 1), (0, 0, 1.2))

        # ---------------- camera
        cam = bl.Cam((3.0, -9.0, 4.0), (0, 0, 1.0), lens=35)
        cam.key(0, loc=(3.4, -9.8, 5.5), target=(0, 0, 2.5))
        cam.key(F(T['liner'] + 0.5), loc=(3.0, -8.8, 1.5), target=(0, 0, -1.5))
        cam.key(F(self.t_fire - 0.5), loc=(2.6, -8.0, -1.5), target=(0, 0, -3.5))
        cam.key(F(T['deep'] + 1.5), loc=(2.8, -8.4, -1.8), target=(0, 0, -3.8))
        cam.key(F(T['upper'] + 0.2), loc=(2.6, -8.0, 19.0), target=(0, 0, 17.0))
        cam.key(F(T['flow'] + 0.3), loc=(2.4, -7.2, 18.6), target=(0, 0, 16.8))
        cam.key(F(T['seals'] + 1.2), loc=(2.0, -6.0, 18.0), target=(0, 0, 16.6))
        cam.key(F(T['dhsv'] - 0.6), loc=(2.2, -6.4, 46.8), target=(0, 0, 45.0))
        cam.key(F(self.t_sea - 0.8), loc=(1.9, -5.8, 46.4), target=(0, 0, 45.0))
        cam.key(f_s, loc=(SEA_X + 14, -30, 16), target=(SEA_X, 0, 6))
        cam.key(F(T['tree'] + 0.8), loc=(SEA_X + 10, -22, 9.5), target=(SEA_X + 1, 0, 3.5))
        cam.key(F(T['flowlines'] - 0.5), loc=(SEA_X + 10, -36, 17), target=(SEA_X + 6, 3, 2.0))
        cam.key(F(self.t_2d + 1), loc=(SEA_X + 2, -38, 18), target=(SEA_X + 5, 3, 2.0))
        for obj in (cam.obj, cam.target):
            for fc in bl._fcurves(obj.animation_data.action):
                for kp in fc.keyframe_points:
                    if abs(kp.co[0] - F(self.t_sea - 0.8)) < 0.5:
                        kp.interpolation = 'CONSTANT'
        A = {
            'liner': (R_LNR_O, -0.05, -1.5), 'csg': (R_CSG_O, -0.05, 12.0),
            'gun': (gun, (0.16, -0.05, -3.0)), 'res': (3.5, 0, -6.0),
            'tbg': (R_TBG_O, -0.05, 22.0), 'pkr': (R_CSG_I * 0.8, -0.05, Z_PKR + 0.5),
            'dhsv': (R_TBG_O + 0.07, -0.05, Z_DHSV + 0.6), 'flap': (0.0, 0.0, Z_DHSV - 0.2),
            'cline': (0.0, R_TBG_O + 0.06, Z_DHSV + 3.0),
            'xt': (SEA_X + 1.9, -1.9, 5.5), 'bop': (bop.root, (1.8, -2.2, 8.0)),
            'jumper': (SEA_X + 7.2, 0.7, 7.5), 'umb': (SEA_X - 10, 6.5, 0.2), 'mf': (SEA_X + 16, 3, 4.5),
            'rov': (rov, (0, 0, 1.6)),
        }
        for j, (z, sx, tf) in enumerate(self_tunnels):
            A['tn_a_%d' % j] = (sx * R_HOLE8, -0.01, z)
            A['tn_b_%d' % j] = (sx * (R_HOLE8 + 1.4), -0.01, z)
        # flow-path anchors along the in-plane tunnels (for oil particles)
        for s_ in (-1, 1):
            for i, z in enumerate((-7.5, -4.5, -1.5)):
                A['tun_%d_%d' % (s_, i)] = (s_ * (R_HOLE8 + 1.3), -0.02, z)
                A['tun_in_%d_%d' % (s_, i)] = (s_ * R_LNR_I, -0.02, z)
        return A

    # ------------------------------------------------------------------ 2D
    def draw(self, ctx, t, f, A):
        T = self.T
        a = self.A
        G.chapter_title(ctx, 3, 'Completion', t, 0.2, T['card_out'], sub='From a hole to a producer',
                        accent=P.XT, backdrop=True)
        # flash when the charges fire
        fl = 1 - abs(t - self.t_fire) / 0.3
        if fl > 0:
            ctx.set_source_rgba(1, 0.95, 0.8, 0.8 * fl)
            ctx.paint()
        if t < self.t_sea:
            self.labels_downhole(ctx, t, A)
        if self.t_sea - 0.1 < t < self.t_2d + 0.2:
            self.labels_seabed(ctx, t, A)
        # transitions
        for tt in (self.t_sea,):
            q = 1 - abs(t - tt) / 0.25
            if q > 0:
                ctx.set_source_rgba(1, 1, 1, 0.9 * q)
                ctx.paint()
        b2 = G.prog(t, self.t_2d, 0.8)
        if b2 > 0:
            ctx.save()
            ctx.push_group()
            G.bg_gradient(ctx)
            self.barriers_2d(ctx, t)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(b2)
            ctx.restore()

    def depth_tag(self, ctx, txt, p):
        if p > 0:
            G.tag(ctx, txt, 1760, 150, p, bg=P.INK, size=26, align='right')

    def labels_downhole(self, ctx, t, A):
        T = self.T
        a = self.A
        items = [
            ('liner', '7" liner, cemented', T['liner'], T['upper'] - 1.0, (260, 60), None),
            ('gun', 'Perforating gun', T['guns'], self.t_fire - 0.2, (-280, -60), None),
            ('res', 'Reservoir sandstone', T['hole'] - 0.5, T['guns'] - 0.5, (60, -150), None),
            ('tbg', 'Production tubing', T['tubing'], T['dhsv'] - 1.0, (260, -60),
             'the oil and gas flow up inside'),
            ('pkr', 'Production packer', T['packer'], T['dhsv'] - 1.0, (280, 60),
             'seals tubing to casing'),
            ('dhsv', 'Downhole safety valve', T['dhsv'], self.t_sea - 0.4, (280, -80),
             'fail-safe closed'),
            ('cline', 'Hydraulic control line', T['hydraulic'], self.t_sea - 0.4, (300, -40), None),
        ]
        for key, txt, t0, t1, off, sub in items:
            pt = a(A, key)
            if pt:
                ty = min(max(pt[1] + off[1], 250), 1000)   # keep clear of the depth tag
                G.label(ctx, pt[0], pt[1], pt[0] + off[0], ty, txt, G.prog(t, t0, 0.8),
                        sub=sub, out=G.prog(t, t1, 0.4), size=30,
                        align='left' if off[0] > 0 else 'right')
        # perforation tunnels drawn on the cut face
        j = 0
        while ('tn_a_%d' % j) in A:
            pa, pb = a(A, 'tn_a_%d' % j), a(A, 'tn_b_%d' % j)
            tp = G.prog(t, self.t_fire + 0.05 * j, 0.25) * (1 - G.prog(t, T['upper'] - 0.6, 0.4))
            if pa and pb and tp > 0:
                ex, ey = pa[0] + (pb[0] - pa[0]) * tp, pa[1] + (pb[1] - pa[1]) * tp
                nx, ny = -(pb[1] - pa[1]), (pb[0] - pa[0])
                L = math.hypot(nx, ny) or 1
                nx, ny = nx / L * 9, ny / L * 9
                G.poly(ctx, [(pa[0] + nx, pa[1] + ny), (ex, ey), (pa[0] - nx, pa[1] - ny)],
                       fill='#2A1D0C', alpha=0.9)
            j += 1
        # jet speed callout
        js = G.window(t, T['seven'] - 0.3, T['upper'] - 0.8, 0.4)
        if js > 0:
            G.panel(ctx, 1320, 760, 470, 200, js)
            G.text(ctx, '≈ 7 km/s', 1555, 850, 72, 'ExtraBold', P.KICK, 'center', alpha=js)
            G.text(ctx, 'jet of metal from a shaped charge', 1555, 910, 24, 'SemiBold', P.INK_SOFT,
                   'center', alpha=js)
        # oil flowing in through the new tunnels
        of = G.window(t, T['deep'] + 0.3, T['upper'] - 0.6, 0.6)
        if of > 0:
            for s_ in (-1, 1):
                for i in range(3):
                    p0, p1 = a(A, 'tun_%d_%d' % (s_, i)), a(A, 'tun_in_%d_%d' % (s_, i))
                    if not p0 or not p1:
                        continue
                    for j in range(5):
                        ph = (t * 0.9 + j / 5 + self.flow_ph[i * 5 + j]) % 1.0
                        x = p0[0] + (p1[0] - p0[0]) * ph
                        y = p0[1] + (p1[1] - p0[1]) * ph
                        G.circle(ctx, x, y, 7, fill=P.OIL, alpha=of * 0.9)
                        G.circle(ctx, x - 2, y - 2, 2.5, fill=P.OIL_GLOW, alpha=of * 0.9)
        # depth tags
        self.depth_tag(ctx, 'RESERVOIR  ·  ≈ 3,000 m', G.window(t, 0.4, T['upper'] - 0.3, 0.4))
        self.depth_tag(ctx, 'ABOVE THE RESERVOIR  ·  ≈ 2,800 m', G.window(t, T['upper'] + 0.3,
                                                                          T['dhsv'] - 0.8, 0.4))
        self.depth_tag(ctx, 'A FEW HUNDRED METRES BELOW THE SEABED',
                       G.window(t, T['dhsv'] - 0.4, self.t_sea - 0.3, 0.4))
        sn = G.window(t, T['snaps'] - 0.1, self.t_sea - 1.2, 0.3)
        if sn > 0:
            G.tag(ctx, 'VALVE CLOSED', 960, 980, sn, bg=P.KICK, size=32, align='center')

    def labels_seabed(self, ctx, t, A):
        T = self.T
        a = self.A
        items = [
            ('bop', 'BOP and riser pulled', self.t_sea + 0.3, T['tree'] - 0.6, (260, -40), None),
            ('xt', 'Subsea christmas tree', T['tree'], self.t_2d, (-300, -120),
             'valves that control the flow'),
            ('jumper', 'Flowline jumper', T['flowlines'], self.t_2d, (200, -120), 'to the manifold'),
            ('umb', 'Umbilical', T['umbilical'], self.t_2d, (200, 150),
             'hydraulics · power · chemicals'),
        ]
        for key, txt, t0, t1, off, sub in items:
            pt = a(A, key)
            if pt:
                G.label(ctx, pt[0], pt[1], pt[0] + off[0], pt[1] + off[1], txt, G.prog(t, t0, 0.8),
                        sub=sub, out=G.prog(t, t1, 0.4), size=30,
                        align='left' if off[0] > 0 else 'right')

    # ------------------------------------------------------------------ production barriers
    def barriers_2d(self, ctx, t):
        T = self.T
        w = schem.make()
        G.panel(ctx, w.x0 - 20, 80, w.x1 - w.x0 + 40, 960, 1.0, alpha=0.95)
        ctx.save()
        ctx.rectangle(w.x0, 90, w.x1 - w.x0, 940)
        ctx.clip()
        w.draw_earth(ctx, labels=True)
        w.fill_bore(ctx, 350, 3430, '#9FD3E8')
        for i in range(5):
            w.cement(ctx, i, 1.0)
            w.casing(ctx, i, 1.0)
        y_bed = w.y(350)
        # tubing + packer + DHSV
        th = 12
        yp = w.y(3100)
        for sx in (-1, 1):
            G.rect(ctx, w.cx + sx * 16 - (th if sx < 0 else 0) + (0 if sx < 0 else 0), y_bed - 30,
                   th, yp + 20 - y_bed + 30, fill=P.PIPE)
        G.rect(ctx, w.cx - 16, y_bed - 30, 32, yp + 20 - y_bed + 30, fill=P.OIL, alpha=0.75)
        ihw = w.hw(9.625) - 4
        G.rect(ctx, w.cx - ihw, yp, 2 * ihw, 22, fill='#2B2F33')
        yd = w.y(700)
        G.rect(ctx, w.cx - 26, yd - 16, 52, 32, fill=P.KICK)
        # perforations
        for k in range(6):
            y = w.y(3330 + k * 18)
            for sx in (-1, 1):
                G.line(ctx, [(w.cx + sx * w.hw(8.5), y), (w.cx + sx * (w.hw(8.5) + 40), y)], P.OIL,
                       4)
        W2.draw_wellhead(ctx, w.cx, y_bed, 1.0)
        W2.draw_xt(ctx, w.cx, y_bed - 30, 0.9)
        ctx.restore()
        # envelopes
        cx = w.cx
        pr = G.prog(t, T['blue'] - 0.8, 1.6)
        ctx_pts_p = [(cx - ihw - 6, w.y(3230)), (cx - ihw - 6, yp - 8), (cx - 22, yp - 8),
                     (cx - 22, yd - 20), (cx + 22, yd - 20), (cx + 22, yp - 8), (cx + ihw + 6, yp - 8),
                     (cx + ihw + 6, w.y(3230))]
        W2.envelope(ctx, ctx_pts_p, P.PRIMARY, pr)
        rr = G.prog(t, T['red'] - 0.8, 1.8)
        oc = w.hw(12.25) + 6
        top = y_bed - 30 - 0.9 * 122
        ctx_pts_s = [(cx - oc, w.y(3230)), (cx - oc, w.y(2400)),
                     (cx - w.hw(9.625) - 6, w.y(1800)), (cx - w.hw(9.625) - 6, y_bed + 6),
                     (cx - 58, y_bed - 20), (cx - 58, top), (cx + 58, top), (cx + 58, y_bed - 20),
                     (cx + w.hw(9.625) + 6, y_bed + 6), (cx + w.hw(9.625) + 6, w.y(1800)),
                     (cx + oc, w.y(2400)), (cx + oc, w.y(3230))]
        W2.envelope(ctx, ctx_pts_s, P.SECONDARY, rr)
        G.text(ctx, 'Ready to produce', 1340, 190, 44, 'ExtraBold', P.INK, 'center')
        schem.legend(ctx, 930, 280, [
            (P.PRIMARY, 'Primary barrier', 'tubing, production packer, safety valve',
             G.prog(t, T['blue'] - 0.6, 0.6)),
            (P.SECONDARY, 'Secondary barrier', 'casing, cement, wellhead and christmas tree',
             G.prog(t, T['red'] - 0.6, 0.6)),
        ])
        cl = G.prog(t, T['cleaned'] - 0.2, 0.6) * (1 - G.prog(t, T['two'] - 0.6, 0.5))
        if cl > 0:
            G.panel(ctx, 930, 560, 820, 150, cl)
            G.text(ctx, 'Cleaned up · tested · handed over', 1340, 650, 34, 'Bold', P.GOOD, 'center',
                   alpha=cl)
