"""Scene 8 - Drilling: the blowout preventer and the marine riser."""
import math

import gfx as G
import overlays as O
import palette as P
from scene_base import Scene
from scenes.s07_tophole import underwater_bg

BOP_Z = 2.3


class S(Scene):
    ID = 's08_bop'
    BLENDER = True
    PHASE = 1
    DARK = True

    def __init__(self):
        super().__init__()
        tl = self.tl
        self.T = dict(
            safety=tl.word('bp1', 'safety net'),
            bop=tl.word('bp1', 'blowout preventer'),
            valves=tl.word('bp2', 'hydraulic valves'),
            tall=tl.word('bp2', 'fifteen meters'),
            tonnes=tl.word('bp2', 'several hundred'),
            latched=tl.word('bp2', 'latched'),
            annular=tl.word('bp3', 'Annular'),
            squeeze=tl.word('bp3', 'squeeze'),
            pipe_rams=tl.word('bp3', 'Pipe rams'),
            close=tl.word('bp3', 'close tightly'),
            defence=tl.word('bp4', 'last line'),
            shear=tl.word('bp4', 'blind shear'),
            cut=tl.word('bp4', 'cut straight'),
            seal=tl.word('bp4', 'seal the well'),
            riser=tl.word('bp5', 'marine riser'),
            up=tl.word('bp5', 'all the way up'),
            mud=tl.word('bp5', 'mud can return'),
        )
        T = self.T
        self.t_land = T['bop'] + 0.6
        self.t_cutaway = tl.t('bp3') - 0.5
        self.t_back = tl.t('bp5') - 0.6

    def draw_bg(self, ctx, t, f):
        underwater_bg(ctx, t)

    def build(self):
        import bl
        import equipment as E
        import models as MD
        tl = self.tl
        T = self.T
        F = lambda s: int(round(s * 24))  # noqa: E731
        M = E.mats()
        M['cut'] = bl.mat('eq_cut2', '#95A2AF', rough=0.6)
        M['ram'] = bl.mat('eq_ram_or', '#F08A24', rough=0.4)
        M['blade'] = bl.mat('eq_blade_w', '#FFFFFF', rough=0.2)
        M['ram_cut'] = bl.mat('eq_ram_cut', '#F7A457', rough=0.5)
        seabed = bl.tex_mat('seabed', MD.tex('seabed'))
        bed = bl.box('bed', (400, 400, 0.4), loc=(0, 0, -0.2), material=seabed)
        bl.uv_box(bed, 6.0)
        wh = E.wellhead(M, cut=False)
        # full BOP + riser, lowered and latched
        full = E.BOP(M, cut=False, name='BOP_full')
        rs = E.riser(M, 12.8, 420, name='riser_full')
        rs.parent = full.root
        f_land = F(self.t_land)
        bl.key(full.root, 'location', F(0.2), (0, 0, 24.0))
        bl.key(full.root, 'location', f_land, (0, 0, BOP_Z))
        # cutaway BOP swaps in for the internal view
        cutb = E.BOP(M, cut=True, name='BOP_cut')
        cutb.root.location = (0, 0, BOP_Z)
        rsc = E.riser(M, 12.8, 420, name='riser_cut', cut=True)
        rsc.parent = cutb.root
        f_cut, f_back = F(self.t_cutaway), F(self.t_back)
        bl.visible_between(cutb.root, f_cut, f_back)
        bl.show(full.root, 0, True)
        bl.show(full.root, f_cut, False)
        bl.show(full.root, f_back, True)
        # drill pipe through the stack, sheared later
        dp_m = bl.mat('dp_bright', '#5B6773', rough=0.3, metal=0.1)
        zs = BOP_Z + E.BOP.RAM_Z[2]
        pipe = bl.cyl('dp_whole', 0.085, 60, loc=(0, 0, 10), material=dp_m, seg=24)
        up = bl.cyl('dp_up', 0.085, 40 - (zs - 0.02), loc=(0, 0, (zs + 0.02 + 40) / 2),
                    material=dp_m, seg=24)
        lo = bl.cyl('dp_lo', 0.085, zs - 0.02 + 20, loc=(0, 0, (zs - 0.02 - 20) / 2),
                    material=dp_m, seg=24)
        f_shear = F(T['cut'] - 0.1)
        bl.visible_between(pipe, f_cut, f_shear)
        bl.visible_between(up, f_shear, f_back)
        bl.visible_between(lo, f_shear, f_back)
        bl.key(lo, 'location', f_shear, lo.location.copy())
        loc2 = lo.location.copy()
        loc2.z -= 0.6
        bl.key(lo, 'location', f_shear + 10, loc2)
        # ram and annular animation
        cutb.squeeze_annular(0, F(T['squeeze'] - 0.1), F(T['squeeze'] + 0.9), amount=0.55)
        cutb.close_ram(0, F(T['close'] - 0.3), F(T['close'] + 0.5))
        cutb.close_ram(1, F(T['close'] - 0.1), F(T['close'] + 0.7))
        cutb.close_ram(2, F(T['cut'] - 0.6), F(T['cut'] + 0.15), stroke=0.34)
        # camera
        cam = bl.Cam((16, -30, 20), (0, 0, 12), lens=35)
        cam.key(0, loc=(15, -32, 26), target=(0, 0, 18))
        cam.key(F(self.t_land - 0.6), loc=(13, -27, 10), target=(0, 0, 6.5))
        cam.key(F(T['latched'] + 0.5), loc=(-11, -26, 12), target=(0, 0, 7.5))
        cam.key(f_cut - 1, loc=(-10, -25, 11), target=(0, 0, 7.5))
        cam.key(f_cut, loc=(2.6, -12.5, 10.0), target=(0, 0, 9.0))
        cam.key(F(T['squeeze'] + 1.2), loc=(2.4, -11.5, 9.5), target=(0, 0, 8.5))
        cam.key(F(T['pipe_rams'] - 0.3), loc=(2.6, -9.5, 6.6), target=(0, 0, 5.2))
        cam.key(F(T['close'] + 1.2), loc=(2.4, -9.0, 6.6), target=(0, 0, 5.4))
        cam.key(F(T['shear'] - 0.4), loc=(2.2, -8.0, 7.8), target=(0, 0, 7.0))
        cam.key(F(T['seal'] + 1.0), loc=(2.0, -7.6, 7.8), target=(0, 0, 7.1))
        cam.key(f_back - 1, loc=(2.0, -7.6, 7.8), target=(0, 0, 7.1))
        cam.key(f_back, loc=(9, -24, 8), target=(0, 0, 12))
        cam.key(F(T['riser'] + 0.5), loc=(9, -26, 22), target=(0, 0, 26))
        cam.key(F(tl.duration + 0.6), loc=(8, -24, 60), target=(0, 0, 78))
        for obj in (cam.obj, cam.target):
            for fc in bl._fcurves(obj.animation_data.action):
                for kp in fc.keyframe_points:
                    if kp.co[0] in (f_cut - 1, f_back - 1):
                        kp.interpolation = 'CONSTANT'
        z = BOP_Z
        return {
            'bop_top': (0, -1.0, z + 12.0), 'dim_bot': (-2.6, -2.2, z), 'dim_top': (-2.6, -2.2, z + 12.8),
            'bop_mid': (1.9, -2.2, z + 6.0), 'wh': (0.45, -0.3, 2.5),
            'ann': (0.55, -0.05, z + E.BOP.ANN_Z[0]), 'ann2': (0.55, -0.05, z + E.BOP.ANN_Z[1]),
            'pram': (0.34, -0.05, z + E.BOP.RAM_Z[0]), 'pram2': (0.34, -0.05, z + E.BOP.RAM_Z[1]),
            'shear': (0.3, -0.05, zs), 'riser': (0.62, -0.3, 30.0), 'riser_hi': (0, 0, 70.0),
            'riser_lo': (0, 0, 20.0),
        }

    def draw(self, ctx, t, f, A):
        T = self.T
        a = self.A
        # title
        tp = G.window(t, T['bop'] - 0.2, T['valves'] + 1.5, 0.5)
        if tp > 0:
            G.tag(ctx, 'BLOWOUT PREVENTER (BOP)', 960, 150, tp, bg=P.BOP, col=P.INK, size=40,
                  align='center')
        # dimension + weight
        d0, d1 = a(A, 'dim_bot'), a(A, 'dim_top')
        dw = G.window(t, T['tall'] - 0.3, self.t_cutaway, 0.4)
        if d0 and d1 and dw > 0:
            O.dim_v(ctx, d0[0], d1[1], d0[1], '≈ 15 m', G.prog(t, T['tall'] - 0.3, 0.9),
                    col=P.WHITE, size=40, alpha=dw)
        wt = G.window(t, T['tonnes'] - 0.2, self.t_cutaway, 0.4)
        if wt > 0:
            G.panel(ctx, 1440, 760, 390, 170, wt)
            G.text(ctx, '300–400 t', 1635, 850, 58, 'ExtraBold', P.INK, 'center', alpha=wt)
            G.text(ctx, 'of hydraulic valves', 1635, 900, 26, 'SemiBold', P.INK_SOFT, 'center',
                   alpha=wt)
        lt = a(A, 'wh')
        if lt:
            G.label(ctx, lt[0], lt[1], lt[0] + 260, lt[1] + 60, 'Latched onto the wellhead',
                    G.prog(t, T['latched'], 0.7), out=G.prog(t, self.t_cutaway - 0.6, 0.4), size=28)
        # flash at the cutaway swap
        for tt in (self.t_cutaway, self.t_back):
            fl = 1 - abs(t - tt) / 0.25
            if fl > 0:
                ctx.set_source_rgba(1, 1, 1, 0.85 * fl)
                ctx.paint()
        cv = G.window(t, self.t_cutaway + 0.2, self.t_back - 0.3, 0.4)
        if cv > 0:
            G.tag(ctx, 'CUTAWAY VIEW', 1760, 150, cv, bg=P.INK, size=24, align='right')
        items = [
            ('ann', 'Annular preventer', 'rubber packer squeezes shut', T['annular'], T['pipe_rams'] - 0.3,
             (330, -60)),
            ('pram', 'Pipe rams', 'close around the drill pipe', T['pipe_rams'], T['shear'] - 0.4,
             (330, 40)),
            ('shear', 'Blind shear rams', 'cut the pipe and seal the well', T['shear'], self.t_back - 0.4,
             (330, -40)),
        ]
        for key, txt, sub, t0, t1, off in items:
            pt = a(A, key)
            if pt:
                G.label(ctx, pt[0], pt[1], pt[0] + off[0], pt[1] + off[1], txt, G.prog(t, t0, 0.8),
                        sub=sub, out=G.prog(t, t1, 0.4), size=32)
        cutp = 1 - abs(t - T['cut']) / 0.35
        if cutp > 0:
            pt = a(A, 'shear')
            if pt:
                for k in range(10):
                    ang = k * math.tau / 10
                    r0, r1 = 20, 20 + 90 * (1 - cutp)
                    G.line(ctx, [(pt[0] - 60 + r0 * math.cos(ang), pt[1] + r0 * math.sin(ang)),
                                 (pt[0] - 60 + r1 * math.cos(ang), pt[1] + r1 * math.sin(ang))],
                           '#FFE9A8', 5, cutp)
        sl = G.window(t, T['seal'] - 0.2, self.t_back - 0.3, 0.4)
        if sl > 0:
            G.tag(ctx, 'WELL SEALED', 960, 980, sl, bg=P.GOOD, size=34, align='center')
        # riser
        rp = a(A, 'riser')
        if rp:
            G.label(ctx, rp[0], rp[1], rp[0] + 280, rp[1] - 40, 'Marine riser',
                    G.prog(t, T['riser'], 0.8), sub='connects the well to the rig', size=34)
        mp = G.prog(t, T['mud'] - 0.3, 0.8)
        hi = a(A, 'riser_hi')
        if mp > 0 and hi:
            for k in range(6):
                ph = (t * 0.6 + k / 6) % 1.0
                y = 950 - 800 * ph
                for sx in (-90, 90):
                    G.arrow(ctx, hi[0] + sx, y + 30, hi[0] + sx, y - 30, P.MUD_LIGHT, 7, 20, 1.0,
                            mp * math.sin(ph * math.pi))
            G.tag(ctx, 'MUD RETURNS TO THE RIG', 960, 980, mp, bg=P.MUD, size=30, align='center')
