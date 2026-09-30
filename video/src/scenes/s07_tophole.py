"""Scene 7 - Drilling: riserless top hole, conductor, surface casing, wellhead housings."""
import math
import random

import gfx as G
import overlays as O
import palette as P
from scene_base import Scene

RS = 1.6   # radial exaggeration for readability
R36, R30o, R30i = 0.457 * RS, 0.381 * RS, 0.355 * RS
R26, R20o, R20i = 0.33 * RS, 0.254 * RS, 0.235 * RS
Z_COND, Z_TD = -12.0, -22.0


def underwater_bg(ctx, t, top='#2D86C4', bot='#0B2D4B', snow=True, seed=5):
    G.bg_multi(ctx, [(0, top), (0.55, '#15548A'), (1, bot)], vignette=0.25)
    if snow:
        rnd = random.Random(seed)
        for i in range(90):
            x0, y0 = rnd.uniform(0, 1920), rnd.uniform(0, 1080)
            sp = rnd.uniform(6, 18)
            r = rnd.uniform(1.0, 2.6)
            y = (y0 + t * sp) % 1100 - 10
            x = x0 + 12 * math.sin(t * 0.3 + i)
            G.circle(ctx, x, y, r, fill='#FFFFFF', alpha=0.18 + 0.2 * (r / 2.6))
    # light shafts from the surface
    import cairo
    for k in range(4):
        x = 300 + k * 420 + 80 * math.sin(t * 0.2 + k)
        g = cairo.LinearGradient(0, 0, 0, 900)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.07)
        g.add_color_stop_rgba(1, 1, 1, 1, 0.0)
        ctx.new_path()
        ctx.move_to(x - 60, 0)
        ctx.line_to(x + 60, 0)
        ctx.line_to(x + 260, 900)
        ctx.line_to(x + 60, 900)
        ctx.close_path()
        ctx.set_source(g)
        ctx.fill()


class S(Scene):
    ID = 's07_tophole'
    BLENDER = True
    PHASE = 1
    DARK = True

    def __init__(self):
        super().__init__()
        tl = self.tl
        self.T = dict(
            riserless=tl.word('th1', 'riser-less'),
            nopipe=tl.word('th1', 'no pipe'),
            hole36=tl.word('th2', 'thirty-six'),
            spill=tl.word('th2', 'spill out'),
            conductor=tl.word('th3', 'conductor'),
            cemented=tl.word('th3', 'cemented'),
            lp=tl.word('th3', 'low-pressure'),
            foundation=tl.word('th3', 'structural foundation'),
            hole26=tl.word('th4', 'twenty-six'),
            casing20=tl.word('th4', 'twenty-inch'),
            hp=tl.word('th4', 'high-pressure'),
            anchor=tl.word('th4', 'anchor point'),
        )
        T = self.T
        # animation schedule (seconds)
        self.S = dict(
            desc0=0.3, desc1=T['hole36'] - 0.3,
            drill0=T['hole36'] - 0.2, drill1=T['spill'] + 1.8,
            pull0=T['spill'] + 1.9, pull1=T['conductor'] - 0.4,
            cond0=T['conductor'] - 0.3, cond1=T['cemented'] - 0.2,
            cem0=T['cemented'], cem1=T['lp'] + 0.6,
        )
        th4 = tl.t('th4')
        S_ = self.S
        S_['d2a'] = th4 - 0.3
        S_['d2b'] = S_['d2a'] + 1.0
        S_['dr2a'] = S_['d2b'] + 0.05
        S_['dr2b'] = S_['dr2a'] + 1.5
        S_['pull2'] = S_['dr2b'] + 0.05
        S_['cs0'] = S_['pull2'] + 0.4
        S_['cs1'] = S_['cs0'] + 2.0
        S_['cem2a'] = S_['cs1'] + 0.2
        S_['cem2b'] = S_['cem2a'] + 2.3

    def draw_bg(self, ctx, t, f):
        underwater_bg(ctx, t)

    def build(self):
        import bl
        import equipment as E
        import models as MD
        tl = self.tl
        S_ = self.S
        F = lambda s: int(round(s * 24))  # noqa: E731
        M = E.mats()
        soil = MD.strata_mat('soft_clay')
        seabed = bl.tex_mat('seabed', MD.tex('seabed'))
        # soil block with the (future) hole as a notch; cores fill it until drilled
        sections = [(0.0, -4.0, R36), (-4.0, -8.0, R36), (-8.0, Z_COND, R36),
                    (Z_COND, -17.0, R26), (-17.0, Z_TD, R26), (Z_TD, -28.0, 0.0)]
        cores = []
        for (zt, zb, R) in sections:
            sl = MD.notched_slab('soil', -14, 14, 0, 14, zb, zt, R, soil, seg=48)
            bl.uv_box(sl, 3.0)
            if zt == 0.0:
                sl.data.materials.append(seabed)
                for p in sl.data.polygons:
                    if p.normal.z > 0.9:
                        p.material_index = 1
            if R > 0:
                c = bl.annulus('core', 0, R * 1.002, 0, zt - zb, 0, math.pi, 48, soil)
                c.location = (0, 0, zb)
                bl.uv_box(c, 3.0)
                cores.append((zt, zb, c))
        # seabed plane behind
        bed = bl.box('bed', (400, 200, 0.2), loc=(0, 114, -0.1), material=seabed)
        bl.uv_box(bed, 6.0)
        for x in (-114, 114):
            b2 = bl.box('bed2', (200, 14, 0.2), loc=(x, 7, -0.1), material=seabed)
            bl.uv_box(b2, 6.0)

        # ---------------- drill string with bit (reused for both sections)
        def make_string(r_bit, name):
            root = bl.empty(name)
            bit = E.pdc_bit(M, r=r_bit, blades=6, name=name + '_bit')
            bit.parent = root
            col = bl.cyl(name + '_dc', 0.2, 18, loc=(0, 0, 9.6), material=M['steel_dark'], seg=24)
            dp = bl.cyl(name + '_dp', 0.12, 80, loc=(0, 0, 58.6), material=M['pipe'], seg=16)
            stab = bl.cyl(name + '_stab', r_bit * 0.95, 0.8, loc=(0, 0, 1.6),
                          material=M['steel'], seg=24)
            for o in (col, dp, stab):
                o.parent = root
            return root

        s36 = make_string(R36 * 0.98, 'str36')
        f = F
        bl.key(s36, 'location', f(S_['desc0']), (0, 0, 30.0))
        bl.key(s36, 'location', f(S_['desc1']), (0, 0, 0.05))
        bl.key(s36, 'location', f(S_['drill0']), (0, 0, 0.05))
        bl.key(s36, 'location', f(S_['drill1']), (0, 0, Z_COND))
        bl.key(s36, 'location', f(S_['pull0']), (0, 0, Z_COND))
        bl.key(s36, 'location', f(S_['pull1']), (0, 0, 40.0))
        bl.spin(s36, f(S_['drill0'] - 0.5), f(S_['drill1']), 7)
        bl.hide_at(s36, f(S_['pull1']) + 1)
        s26 = make_string(R26 * 0.98, 'str26')
        bl.visible_between(s26, f(S_['d2a']), f(S_['cs0'] + 0.9))
        bl.key(s26, 'location', f(S_['d2a']), (0, 0, 40.0))
        bl.key(s26, 'location', f(S_['d2b']), (0, 0, Z_COND))
        bl.key(s26, 'location', f(S_['dr2a']), (0, 0, Z_COND))
        bl.key(s26, 'location', f(S_['dr2b']), (0, 0, Z_TD + 0.5))
        bl.key(s26, 'location', f(S_['pull2']), (0, 0, Z_TD + 0.5))
        bl.key(s26, 'location', f(S_['cs0'] + 0.8), (0, 0, 45.0))
        bl.spin(s26, f(S_['dr2a'] - 0.3), f(S_['dr2b']), 5)

        # cores disappear as the bit passes
        def bit_depth_frames(zt, zb, t0, t1, z0, z1):
            fa = t0 + (t1 - t0) * (zt - z0) / (z1 - z0)
            fb = t0 + (t1 - t0) * (zb - z0) / (z1 - z0)
            return F(fa), F(fb)
        for (zt, zb, c) in cores:
            if zt > Z_COND - 0.1:
                fa, fb = bit_depth_frames(zt, zb, S_['drill0'], S_['drill1'], 0.05, Z_COND)
            else:
                fa, fb = bit_depth_frames(zt, zb, S_['dr2a'], S_['dr2b'], Z_COND, Z_TD + 0.5)
            # shrink from the top: origin at bottom (already), scale z
            bl.key(c, 'scale', fa, (1, 1, 1))
            bl.key(c, 'scale', fb, (1, 1, 0.001))
            bl.linear_all(c)
            bl.hide_at(c, fb + 1)

        # ---------------- cuttings plume at the hole mouth
        rnd = random.Random(3)
        cm = bl.mat('cuttings', P.CUTTINGS, rough=0.9)
        cm2 = bl.mat('cuttings2', '#A8977E', rough=0.9)
        for i in range(90):
            t0 = S_['drill0'] + rnd.uniform(0.0, (S_['drill1'] - S_['drill0']) * 0.95)
            if i % 3 == 0:
                t0 = S_['dr2a'] + rnd.uniform(0, (S_['dr2b'] - S_['dr2a']) * 0.9)
            ang = rnd.uniform(-0.2, math.pi + 0.2) if rnd.random() < 0.7 else rnd.uniform(0, math.tau)
            r0 = 0.5
            r1 = rnd.uniform(0.9, 2.2)
            r2 = rnd.uniform(1.2, 3.8)
            h = rnd.uniform(0.8, 2.6)
            sp = bl.sphere('cut', rnd.uniform(0.05, 0.13), material=cm if i % 2 else cm2, seg=8,
                           rings=5)
            c, s = math.cos(ang), math.sin(ang)
            bl.key(sp, 'location', F(t0), (c * r0, s * r0 + 0.3, 0.1))
            bl.key(sp, 'location', F(t0 + 0.8), (c * r1, s * r1 + 0.3, h))
            bl.key(sp, 'location', F(t0 + 2.6), (c * r2, s * r2 + 0.3, 0.05))
            bl.show(sp, 0, False)
            bl.show(sp, F(t0), True)

        # ---------------- conductor + LP housing
        steel, cut = M['steel'], M['cut']
        cond = bl.empty('conductor_grp')
        c1 = bl.annulus('conductor', R30i, R30o, Z_COND, 1.2, 0, math.pi, 64, steel, cut)
        lp = bl.revolve('lp', [(0.355 * RS, 0.9), (0.56 * RS, 0.9), (0.56 * RS, 1.0), (0.48 * RS, 1.1),
                               (0.48 * RS, 1.75), (0.40 * RS, 1.85), (0.355 * RS, 1.85)], 64, 0,
                        math.pi, M['steel_dark'], cut)
        guide = bl.revolve('lp_funnel', [(0.56 * RS, 1.0), (1.2 * RS, 1.5), (1.26 * RS, 1.5),
                                         (0.62 * RS, 1.0)], 64, 0, math.pi, M['yellow'], cut)
        for o in (c1, lp, guide):
            o.parent = cond
        bl.key(cond, 'location', F(S_['cond0']), (0, 0, 28.0))
        bl.key(cond, 'location', F(S_['cond1']), (0, 0, 0.0))
        bl.show(cond, 0, False)
        bl.show(cond, F(S_['cond0']), True)
        cem, cem_cut = MD.cement_mats()
        c_an = bl.annulus('cem36', R30o, R36, Z_COND, 0.0, 0, math.pi, 64, cem, cem_cut)
        bl.uv_cyl(c_an, 1.0)
        MD.grow_up(c_an, F(S_['cem0']), F(S_['cem1']))
        # ---------------- 20" casing + HP housing
        cs = bl.empty('casing20_grp')
        c2 = bl.annulus('casing20', R20i, R20o, Z_TD + 1.0, 1.7, 0, math.pi, 64, steel, cut)
        hp_prof = [(0.24, 1.6), (0.35, 1.6), (0.35, 1.85), (0.36, 1.9), (0.36, 2.95),
                   (0.42, 3.0), (0.42, 3.05), (0.36, 3.1), (0.36, 3.25), (0.42, 3.3),
                   (0.42, 3.35), (0.36, 3.4), (0.36, 3.55), (0.30, 3.6), (0.24, 3.6)]
        hp = bl.revolve('hp', [(r * RS, z) for r, z in hp_prof], 64, 0, math.pi, M['steel'], cut)
        for o in (c2, hp):
            o.parent = cs
        bl.key(cs, 'location', F(S_['cs0']), (0, 0, 42.0))
        bl.key(cs, 'location', F(S_['cs1']), (0, 0, 0.0))
        bl.show(cs, 0, False)
        bl.show(cs, F(S_['cs0']), True)
        c_b = bl.annulus('cem26', R20o, R26, Z_TD + 1.0, Z_COND, 0, math.pi, 64, cem, cem_cut)
        c_c = bl.annulus('cem26b', R20o, R30i, Z_COND, -1.0, 0, math.pi, 64, cem, cem_cut)
        for c in (c_b, c_c):
            bl.uv_cyl(c, 1.0)
        MD.grow_up(c_b, F(S_['cem2a']), F(S_['cem2a'] + 1.2))
        MD.grow_up(c_c, F(S_['cem2a'] + 1.2), F(S_['cem2b']))

        # ---------------- camera
        cam = bl.Cam((10, -26, 9), (0, 2, 5.0), lens=35)
        cam.key(0, loc=(11, -27, 10), target=(0, 2, 6.0))
        cam.key(F(S_['desc1']), loc=(10, -27, 5), target=(0, 1, 0.0))
        cam.key(F(S_['drill0'] + 1.5), loc=(10, -28, 3), target=(0, 0, -3.0))
        cam.key(F(S_['drill1']), loc=(10, -28, 2), target=(0, 0, -3.5))
        cam.key(F(S_['cond0'] + 0.5), loc=(8, -21, 2), target=(0, 0, -3.5))
        cam.key(F(S_['cem1']), loc=(7, -19, 1), target=(0, 0, -4.0))
        cam.key(F(S_['d2b']), loc=(9, -25, -3), target=(0, 0, -8.0))
        cam.key(F(S_['dr2b']), loc=(9, -25, -4), target=(0, 0, -9.0))
        cam.key(F(S_['cs1'] - 0.5), loc=(8, -22, -2), target=(0, 0, -6.0))
        cam.key(F(S_['cem2a'] + 1.0), loc=(5.5, -12.5, 3.0), target=(0, 0, 0.8))
        cam.key(F(tl.duration + 0.6), loc=(4.5, -10.5, 3.6), target=(0, 0, 1.2))
        return {
            'bit36': (s36, (0.6, -0.2, 0.3)), 'mouth': (2.2, 0.4, 0.6),
            'cond': (-R30o, -0.05, -5.0), 'lp': (0.55 * RS, -0.1, 1.5), 'cem1': (R36 * 0.95, -0.05, -8.0),
            'bit26': (s26, (0.36, -0.2, 0.3)), 'cs20': (-R20o, -0.05, -16.0),
            'hp': (0.42 * RS, -0.1, 3.2), 'seabed': (4, 0, 0),
        }

    def draw(self, ctx, t, f, A):
        T = self.T
        S_ = self.S
        a = self.A
        tg = G.window(t, T['riserless'] - 0.3, S_['drill1'], 0.5)
        if tg > 0:
            G.tag(ctx, 'RISERLESS', 960, 150, tg, bg=P.ACCENT, size=40, align='center')
            G.text(ctx, 'no pipe back to the rig, returns go to the seabed', 960, 225, 30,
                   'SemiBold', P.WHITE, 'center', alpha=tg)
        items = [
            ('bit36', '36" hole', 'drilled with seawater', T['hole36'], S_['pull0']),
            ('mouth', 'Cuttings spill onto the seabed', None, T['spill'], S_['pull0'] + 0.5),
            ('cond', '30" conductor', None, T['conductor'], S_['d2a']),
            ('lp', 'Low-pressure wellhead housing', None, T['lp'], S_['d2a']),
            ('cem1', 'Cement', None, S_['cem0'] + 0.4, S_['d2a']),
            ('bit26', '26" hole', None, T['hole26'], S_['pull2']),
            ('cs20', '20" surface casing', None, max(T['casing20'], S_['cs0'] + 1.0), 100),
            ('hp', 'High-pressure wellhead housing', '18¾" bore', max(T['hp'], S_['cs1'] - 0.3), 100),
        ]
        offs = {'bit36': (260, -40), 'mouth': (200, -150), 'cond': (-300, -60),
                'lp': (260, -120), 'cem1': (280, 60), 'bit26': (280, -40), 'cs20': (-280, -80),
                'hp': (300, -120)}
        for key, txt, sub, t0, t1 in items:
            pt = a(A, key)
            if not pt:
                continue
            dx, dy = offs[key]
            G.label(ctx, pt[0], pt[1], pt[0] + dx, pt[1] + dy, txt, G.prog(t, t0, 0.8), sub=sub,
                    out=G.prog(t, t1, 0.5), size=30, align='left' if dx > 0 else 'right')
        ap = G.prog(t, T['anchor'] - 0.2, 0.7)
        if ap > 0:
            G.tag(ctx, 'THE ANCHOR POINT FOR EVERYTHING THAT FOLLOWS', 960, 980, ap, bg=P.INK,
                  size=28, align='center')
