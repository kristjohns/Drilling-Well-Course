"""Scene 1 - Hook: the diorama from sea surface to reservoir, the lifecycle, title."""
import math

import gfx as G
import overlays as O
import palette as P
from scene_base import Scene

RES_TOP, RES_BOT = 2950, 3100
CAP_TOP = 2800


class S(Scene):
    ID = 's01_intro'
    BLENDER = True

    def __init__(self):
        super().__init__()
        tl = self.tl
        self.T = dict(
            res=tl.word('hook1', 'layer of sandstone'),
            pores=tl.word('hook1', 'pores'),
            plate=tl.word('hook2', 'dinner plate'),
            water=tl.word('hook2', 'hundreds'),
            rock=tl.word('hook2', 'kilometers of solid rock'),
            press=tl.word('hook3', 'enormous pressures'),
            seal=tl.word('hook4', 'seal it'),
            forever=tl.word('hook4', 'forever'),
            ncs=tl.word('hook5', 'Norwegian'),
            life=tl.word('hook5', 'entire life'),
            d1=tl.word('hook6', 'designed'),
            d2=tl.word('hook6', 'drilled'),
            d3=tl.word('hook6', 'completed'),
            d4=tl.word('hook6', 'plugged'),
            title=tl.end('hook6', 0.6),
        )

    # ------------------------------------------------------------------ 3D
    def build(self):
        import bl
        import equipment as E
        import models as MD
        tl = self.tl
        T = self.T
        F = lambda s: int(round(s * 24))  # noqa: E731
        D = MD.Diorama(well=False)
        d = D.dio
        MD.ocean(spatial=10, wave_scale=0.05, wind=9, alpha=0.96, col='#2A78B8', frames=(0, tl.nframes + 20))
        # mini rig (schematic scale) with a drill string down to the seabed
        M = E.mats()
        rig_root, rig_body, der = E.semisub(M)
        rig_root.scale = (0.011, 0.011, 0.011)
        rig_root.location = (0, 0.0, d.sea_z)
        ds = bl.cyl('ministring', 0.012, d.sea_z + 0.4, loc=(0, 0.0, (d.sea_z + 0.4) / 2 - 0.2),
                    material=M['pipe'], seg=12)
        # well path (drawn on the cut face, slightly proud of it)
        path_m = bl.mat('path', P.ACCENT, rough=0.3)
        path = bl.curve_tube('wellpath', [(0, -0.08, 0.02), (0, -0.08, d.z(1500)),
                                          (0, -0.08, d.z(3000))], 0.07, path_m, smooth=False)
        cu = path.data
        cu.bevel_factor_end = 0.0
        f0, f1 = F(T['plate'] - 1.2), F(T['rock'] + 1.2)
        cu.bevel_factor_end = 0.0
        cu.keyframe_insert('bevel_factor_end', frame=f0)
        cu.bevel_factor_end = 1.0
        cu.keyframe_insert('bevel_factor_end', frame=f1)
        # cement plugs that "seal it forever"
        plug_m = bl.mat('plug', '#D9D4C7', rough=0.8)
        plugs = []
        for k, (a, b) in enumerate(((2780, 2950), (2450, 2620), (30, 180))):
            pl = bl.cyl('plug_%d' % k, 0.13, d.z(a) - d.z(b), loc=(0, -0.08, (d.z(a) + d.z(b)) / 2),
                        material=plug_m, seg=24)
            ft = F(T['seal'] + 0.2 + 0.45 * k)
            bl.pop_in(pl, ft, 8)
            plugs.append(pl)
        # fade the path after sealing (shrink radius)
        cu.keyframe_insert('bevel_depth', frame=F(T['forever'] - 0.3))
        cu.bevel_depth = 0.035
        cu.keyframe_insert('bevel_depth', frame=F(T['forever'] + 0.5))

        # camera
        cam = bl.Cam((3.0, -6.2, 2.9), (0, 1.0, 1.95), lens=40)
        cam.key(0, loc=(3.2, -6.4, 2.95), target=(0, 1.0, 2.0))
        cam.key(F(3.2), loc=(2.2, -6.2, 2.6), target=(0, 1.0, 1.85))
        cam.key(F(6.0), loc=(1.4, -9.5, 0.4), target=(0, 0.4, -1.2))
        cam.key(F(T['res'] - 0.4), loc=(2.6, -9.0, -13.2), target=(0, 0.2, -14.9))
        cam.key(F(T['plate'] - 1.0), loc=(3.2, -10.0, -12.6), target=(0, 0.3, -14.6))
        cam.key(F(T['rock'] + 0.8), loc=(13.0, -33.0, -1.5), target=(0, 1.0, -7.0))
        cam.key(F(T['press'] - 0.2), loc=(8.0, -22.0, -9.5), target=(0, 0.5, -12.5))
        cam.key(F(T['seal'] - 0.3), loc=(8.0, -21.5, -9.0), target=(0, 0.5, -12.0))
        cam.key(F(T['forever'] + 0.4), loc=(12.5, -32.0, -2.0), target=(0, 1.0, -7.0))
        cam.key(F(T['life']), loc=(-10.0, -33.0, 0.5), target=(-1.5, 1.5, -7.0))
        cam.key(F(tl.duration + 0.6), loc=(-18.0, -30.0, 3.0), target=(-2.0, 2.0, -7.0))

        z = d.z
        A = {
            'res_c': (2.0, 0.0, (z(RES_TOP) + z(RES_BOT)) / 2),
            'res_q0': (-8, 0, z(RES_TOP)), 'res_q1': (8, 0, z(RES_TOP)),
            'res_q2': (8, 0, z(RES_BOT)), 'res_q3': (-8, 0, z(RES_BOT)),
            'dim_x0': (-8.3, 0, d.sea_z), 'dim_x1': (-8.3, 0, 0.0), 'dim_x2': (-8.3, 0, z(RES_TOP)),
            'path_top': (0, -0.1, 0.0), 'path_bot': (0, -0.1, z(3000)),
            'plug0': (0.15, -0.1, z(2865)), 'rig': (0, 0, d.sea_z + 0.9),
            'seabed': (3.0, 0.0, 0.0),
        }
        return A

    # ------------------------------------------------------------------ 2D
    def draw(self, ctx, t, f, A):
        T = self.T
        a = self.A
        # reservoir highlight
        rq = [a(A, 'res_q%d' % i) for i in range(4)]
        hl = G.window(t, T['res'] - 0.3, T['plate'] + 1.0, 0.8)
        pr = G.window(t, T['press'] - 0.3, T['seal'], 0.6)
        if hl > 0:
            O.glow_quad(ctx, rq, '#FFFFFF', hl * (0.75 + 0.25 * math.sin(t * 3)))
        if pr > 0:
            O.glow_quad(ctx, rq, P.KICK, pr * (0.55 + 0.45 * math.sin(t * 6)))
        rc = a(A, 'res_c')
        if rc:
            G.label(ctx, rc[0], rc[1], rc[0] + 220, rc[1] - 150, 'Reservoir sandstone',
                    G.prog(t, T['res'], 1.0), sub='oil & gas trapped in its pores',
                    out=G.prog(t, T['plate'] - 0.5, 0.6), size=30)
            # pressure arrows
            if pr > 0:
                for k in range(-2, 3):
                    x = rc[0] - 60 + k * 90
                    ph = (t * 1.3 + k * 0.25) % 1.0
                    G.arrow(ctx, x, rc[1] - 10 - ph * 30, x, rc[1] - 70 - ph * 30, P.KICK, 6, 18,
                            1.0, pr * (1 - ph))
                G.tag(ctx, 'HIGH PRESSURE', rc[0] + 240, rc[1] - 120, pr, bg=P.KICK, size=30)
        # dimensions: water and rock
        x0, x1, x2 = a(A, 'dim_x0'), a(A, 'dim_x1'), a(A, 'dim_x2')
        dp = G.window(t, T['water'] - 0.2, T['press'] - 0.5, 0.6)
        if x0 and x1 and dp > 0:
            O.dim_v(ctx, x0[0] - 20, x0[1], x1[1], '350 m', G.prog(t, T['water'] - 0.2, 1.0),
                    col=P.SEAWATER_DARK, sub='of seawater', alpha=dp)
        dr = G.window(t, T['rock'] - 0.3, T['press'] - 0.5, 0.6)
        if x1 and x2 and dr > 0:
            O.dim_v(ctx, x1[0] - 20, x1[1], x2[1], '≈ 3 km', G.prog(t, T['rock'] - 0.3, 1.0),
                    col=P.INK, sub='of rock', alpha=dr)
        # dinner plate
        pp = G.window(t, T['plate'] - 0.2, T['press'] - 0.5, 0.5)
        if pp > 0:
            cx, cy = 1560, 300
            G.panel(ctx, cx - 190, cy - 170, 380, 360, pp, alpha=0.92)
            r = 105 * G.ease_out_back(G.clamp(pp * 1.2))
            G.circle(ctx, cx, cy - 10, r, fill='#FFFFFF', stroke='#C9D3DC', lw=6, alpha=pp)
            G.circle(ctx, cx, cy - 10, r * 0.66, stroke='#DCE3EA', lw=4, alpha=pp)
            G.arrow(ctx, cx - r, cy + r + 10, cx + r, cy + r + 10, P.INK, 3, 12, pp, pp, both=True)
            G.text(ctx, 'hole ≈ 20–90 cm wide', cx, cy + r + 60, 26, 'Bold', P.INK, 'center',
                   alpha=pp)
        # sealing
        sp = G.window(t, T['forever'] - 0.1, T['ncs'] - 0.4, 0.5)
        pl = a(A, 'plug0')
        if pl and sp > 0:
            G.label(ctx, pl[0], pl[1], pl[0] + 160, pl[1] - 110, 'Sealed. Forever.', sp,
                    col=P.WHITE, bg=P.INK, size=32, elbow=True)
        # map inset
        mp = G.window(t, T['ncs'] - 0.3, T['d1'] - 0.3, 0.6)
        if mp > 0:
            mx, my = O.map_inset(ctx, 1330, 170, 480, 560, mp, t)
            G.tag(ctx, 'NORWEGIAN CONTINENTAL SHELF', 1570, 790, mp, bg=P.INK, size=24,
                  align='center')
            G.label(ctx, mx, my, mx - 90, my + 120, 'Our subsea well', mp, size=24,
                    align='right', elbow=False)
        # lifecycle cards
        keys = ['d1', 'd2', 'd3', 'd4']
        out = G.prog(t, T['title'] - 0.4, 0.6)
        if t > T['d1'] - 0.5 and out < 1:
            w, gap = 260, 40
            x0 = 960 - (4 * w + 3 * gap) / 2
            for i, k in enumerate(keys):
                p = G.prog(t, T[k] - 0.15, 0.7, G.linear)
                hi = G.prog(t, T[k] - 0.1, 0.4)
                O.phase_card(ctx, i, x0 + i * (w + gap), 700, p * (1 - out), w=w, h=260,
                             highlight=hi)
                if i < 3 and p > 0.9:
                    G.arrow(ctx, x0 + i * (w + gap) + w + 6, 830, x0 + (i + 1) * (w + gap) - 6, 830,
                            P.INK_SOFT, 4, 14, G.prog(t, T[keys[i + 1]] - 0.6, 0.5), 1 - out)
        # title
        tp = G.prog(t, T['title'], 1.0)
        if tp > 0:
            ctx.save()
            ctx.rectangle(0, 0, 1920, 1080)
            ctx.set_source_rgba(0.04, 0.10, 0.17, 0.55 * tp)
            ctx.fill()
            ctx.restore()
            G.text(ctx, 'THE LIFE OF A', 960, 430 + (1 - tp) * 30, 54, 'Bold', '#BFE3F5', 'center',
                   alpha=tp, tracking=0.25)
            G.text(ctx, 'SUBSEA WELL', 960, 560 + (1 - tp) * 30, 150, 'ExtraBold', P.WHITE,
                   'center', alpha=tp, tracking=0.04)
            bw = 520 * G.prog(t, T['title'] + 0.4, 0.9)
            G.rrect(ctx, 960 - bw / 2, 600, bw, 10, 5)
            G.set_color(ctx, P.ACCENT, tp)
            ctx.fill()
            G.text(ctx, 'Design  ·  Drilling  ·  Completion  ·  Plug & Abandonment', 960, 680,
                   34, 'SemiBold', '#D6E6F2', 'center', alpha=G.prog(t, T['title'] + 0.7, 0.8))
            G.text(ctx, 'A subsea well on the Norwegian Continental Shelf', 960, 740, 28,
                   'Medium', '#9FC3DB', 'center', alpha=G.prog(t, T['title'] + 1.0, 0.8))
