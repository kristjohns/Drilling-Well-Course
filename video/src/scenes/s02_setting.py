"""Scene 2 - The setting: water depth, subsea production system, reservoir, cap rock."""
import math

import gfx as G
import overlays as O
import palette as P
from scene_base import Scene

RES_TOP, RES_BOT, CAP_TOP = 2950, 3100, 2800
FPSO_X = 17.0


class S(Scene):
    ID = 's02_setting'
    BLENDER = True

    def __init__(self):
        super().__init__()
        tl = self.tl
        self.T = dict(
            wd=tl.word('set2', 'three hundred'),
            waves=tl.word('set2', 'above the waves'),
            seabed=tl.word('set3', 'sits on'),
            wellhead=tl.word('set3', 'wellhead'),
            valves=tl.word('set3', 'valves'),
            pipes=tl.word('set3', 'pipelines'),
            facility=tl.word('set3', 'production facility'),
            km=tl.word('set3', 'many kilometers'),
            subsea=tl.word('set3', 'subsea well'),
            target=tl.t('set4'),
            three=tl.word('set4', 'three kilometers'),
            pores=tl.word('set4', 'pores'),
            grains=tl.word('set4', 'grains'),
            hold=tl.word('set4', 'hold the oil'),
            cap=tl.word('set5', 'impermeable'),
            reason=tl.word('set5', 'reason'),
            lid=tl.word('set5', "nature's own lid"),
            back=tl.word('set6', 'put that lid back'),
        )

    def build(self):
        import bl
        import equipment as E
        import models as MD
        T = self.T
        tl = self.tl
        F = lambda s: int(round(s * 24))  # noqa: E731
        D = MD.Diorama(well=False, width=36.0, x_center=8.0)
        d = D.dio
        MD.ocean(size=(36, 8), loc=(8, 4, d.sea_z), res=(360, 80), spatial=10, wave_scale=0.05,
                 wind=9, alpha=0.96, col='#2A78B8', frames=(0, tl.nframes + 20))
        M = E.mats()
        # subsea production system (schematic scale x0.08)
        k = 0.08
        xt = E.xmas_tree(M)
        xt.scale = (k, k, k)
        xt.location = (0, 1.2, 0.0)
        mf = E.manifold(M)
        mf.scale = (k, k, k)
        mf.location = (1.3, 1.2, 0.0)
        jumper = bl.curve_tube('jumper', [(0.23, 1.2, 0.21), (0.45, 1.2, 0.38), (0.75, 1.2, 0.38),
                                          (0.85, 1.2, 0.12)], 0.02, M['yellow'])
        # flowline along the seabed to the FPSO, then a lazy-wave riser
        fl_pts = [(1.8, 1.2, 0.03), (6, 1.3, 0.03), (12, 1.2, 0.03), (FPSO_X - 2.0, 1.2, 0.05),
                  (FPSO_X - 1.2, 1.2, 0.6), (FPSO_X - 1.4, 1.2, 1.1), (FPSO_X - 0.4, 1.2, 1.6),
                  (FPSO_X - 0.05, 1.2, d.sea_z)]
        fl = bl.curve_tube('flowline', fl_pts, 0.035, bl.mat('flowline', '#E8A33A', rough=0.4))
        fp = E.fpso(M)
        fp.scale = (0.006, 0.006, 0.006)
        fp.location = (FPSO_X + 0.7, 1.2, d.sea_z + 0.02)
        # planned well path (faint)
        path = bl.cyl('planned', 0.03, d.z(0) - d.z(3000), loc=(0, -0.05, d.z(3000) / 2),
                      material=bl.mat('planned', '#E9EEF2', alpha=0.6), seg=16)
        cam = bl.Cam((-6, -24, 4), (6, 2, -0.5), lens=35)
        cam.key(0, loc=(-7, -25, 4.5), target=(6, 2, -0.5))
        cam.key(F(2.2), loc=(-5.5, -23, 4.0), target=(6, 2, -0.8))
        cam.key(F(T['wd'] - 0.6), loc=(-3.0, -11.5, 2.2), target=(0.5, 1.0, 0.7))
        cam.key(F(T['waves'] + 0.6), loc=(-2.6, -11.0, 2.0), target=(0.5, 1.0, 0.6))
        cam.key(F(T['wellhead'] - 0.5), loc=(1.2, -4.2, 0.9), target=(0.6, 1.2, 0.15))
        cam.key(F(T['valves'] + 1.0), loc=(1.6, -4.0, 0.8), target=(0.8, 1.2, 0.15))
        cam.key(F(T['pipes'] + 0.6), loc=(7.0, -9.0, 1.5), target=(9.0, 1.2, 0.2))
        cam.key(F(T['facility'] + 1.0), loc=(13.5, -9.0, 2.6), target=(FPSO_X, 1.2, 1.2))
        cam.key(F(T['subsea'] - 0.8), loc=(6.0, -26.0, 4.5), target=(7.0, 1.5, -0.5))
        cam.key(F(T['subsea'] + 1.5), loc=(5.5, -25.0, 4.0), target=(6.5, 1.5, -1.0))
        cam.key(F(T['target'] + 2.5), loc=(3.2, -9.5, -13.0), target=(0.3, 0.5, -14.9))
        cam.key(F(T['hold'] + 1.0), loc=(3.0, -9.0, -13.2), target=(0.3, 0.5, -14.9))
        cam.key(F(T['cap'] - 0.5), loc=(3.8, -10.5, -12.2), target=(0.3, 0.5, -14.4))
        cam.key(F(T['back'] - 1.5), loc=(4.5, -12.0, -11.5), target=(0.3, 0.5, -14.2))
        cam.key(F(tl.duration + 0.6), loc=(5.5, -14.0, -11.0), target=(0.3, 0.5, -14.1))
        z = d.z
        A = {
            'surf_well': (0, 0, d.sea_z), 'bed_well': (0, 0, 0.0),
            'dimx0': (-1.0, 0, d.sea_z), 'dimx1': (-1.0, 0, 0.0),
            'xt': (0.0, 1.2, 0.28), 'mf': (1.3, 1.2, 0.35), 'fpso': (FPSO_X + 0.7, 1.2, d.sea_z + 0.25),
            'res_c': (1.5, 0, (z(RES_TOP) + z(RES_BOT)) / 2),
            'cap_c': (1.8, 0, (z(CAP_TOP) + z(RES_TOP)) / 2),
            'res_top_bed': (0, 0, 0), 'res_top': (0.6, 0, z(RES_TOP)),
        }
        for i, xx in enumerate((-10, 26)):
            pass
        for nm, dd in (('cap', (CAP_TOP, RES_TOP)), ('res', (RES_TOP, RES_BOT))):
            A[nm + '_q0'] = (-10, 0, z(dd[0]))
            A[nm + '_q1'] = (26, 0, z(dd[0]))
            A[nm + '_q2'] = (26, 0, z(dd[1]))
            A[nm + '_q3'] = (-10, 0, z(dd[1]))
        # points along the flowline for flow arrows
        for i in range(24):
            u = i / 23
            A['fl%d' % i] = self._flow_point(fl_pts, u)
        for i in range(-6, 7):
            A['cap_x%d' % (i + 6)] = (i * 0.9 + 0.8, 0, z(RES_TOP) + 0.02)
            A['res_x%d' % (i + 6)] = (i * 0.9 + 0.8, 0, z(RES_BOT) - 0.05)
        return A

    @staticmethod
    def _flow_point(pts, u):
        L = [0.0]
        for a, b in zip(pts[:-1], pts[1:]):
            L.append(L[-1] + math.dist(a, b))
        tgt = L[-1] * u
        for i in range(len(pts) - 1):
            if L[i] <= tgt <= L[i + 1]:
                k = (tgt - L[i]) / max(1e-9, L[i + 1] - L[i])
                return tuple(pts[i][j] + (pts[i + 1][j] - pts[i][j]) * k for j in range(3))
        return pts[-1]

    # ------------------------------------------------------------------ 2D
    def draw(self, ctx, t, f, A):
        T = self.T
        a = self.A
        # water depth dimension
        d0, d1 = a(A, 'dimx0'), a(A, 'dimx1')
        dw = G.window(t, T['wd'] - 0.3, T['wellhead'] - 0.3, 0.5)
        if d0 and d1 and dw > 0:
            O.dim_v(ctx, d0[0], d0[1], d1[1], '350 m', G.prog(t, T['wd'] - 0.3, 1.0),
                    col=P.WHITE, sub='water depth', alpha=dw, size=40)
        sw = a(A, 'surf_well')
        nw = G.window(t, T['waves'] - 0.3, T['seabed'] + 0.3, 0.5)
        if sw and nw > 0:
            G.label(ctx, sw[0], sw[1], sw[0] + 140, sw[1] - 120, 'Nothing above the surface',
                    nw, size=28)
        # seabed equipment
        xt, mf, fp = a(A, 'xt'), a(A, 'mf'), a(A, 'fpso')
        if xt:
            G.label(ctx, xt[0], xt[1], xt[0] - 120, xt[1] - 170, 'Wellhead & christmas tree',
                    G.prog(t, T['wellhead'], 0.9), out=G.prog(t, T['pipes'], 0.5), size=28,
                    align='right')
        if mf:
            G.label(ctx, mf[0], mf[1], mf[0] + 110, mf[1] - 200, 'Valves & manifold',
                    G.prog(t, T['valves'], 0.9), out=G.prog(t, T['pipes'], 0.5), size=28)
        # flow arrows along the flowline
        fa = G.window(t, T['pipes'] - 0.2, T['target'] + 1.0, 0.6)
        if fa > 0:
            pts = [a(A, 'fl%d' % i) for i in range(24)]
            for i in range(23):
                p0, p1 = pts[i], pts[i + 1]
                if not p0 or not p1:
                    continue
                ph = ((t * 1.6) - i * 0.25) % 1.0
                x = p0[0] + (p1[0] - p0[0]) * ph
                y = p0[1] + (p1[1] - p0[1]) * ph
                G.circle(ctx, x, y, 6, fill=P.OIL_GLOW, alpha=fa * 0.9)
        if fp:
            G.label(ctx, fp[0], fp[1], fp[0] - 60, fp[1] - 140, 'Production facility',
                    G.prog(t, T['facility'], 0.9), sub='FPSO or platform, km away',
                    out=G.prog(t, T['target'], 0.5), size=28, align='right')
        sp = G.window(t, T['subsea'] - 0.2, T['target'] + 0.8, 0.5)
        if sp > 0:
            G.tag(ctx, 'SUBSEA WELL', 960, 150, sp, bg=P.ACCENT, size=44, align='center')
            G.text(ctx, 'everything on the seabed, controlled remotely', 960, 230, 30, 'SemiBold',
                   P.INK_SOFT, 'center', alpha=sp)
        # reservoir
        rq = [a(A, 'res_q%d' % i) for i in range(4)]
        cq = [a(A, 'cap_q%d' % i) for i in range(4)]
        rh = G.window(t, T['target'] + 1.8, T['cap'] - 0.3, 0.8)
        O.glow_quad(ctx, rq, '#FFFFFF', rh * 0.8)
        rc = a(A, 'res_c')
        if rc:
            G.label(ctx, rc[0], rc[1], rc[0] + 60, rc[1] + 130, 'Sandstone reservoir',
                    G.prog(t, T['target'] + 2.0, 0.9), sub='≈ 3 km below the seabed',
                    out=G.prog(t, T['cap'] - 0.5, 0.5), size=30, elbow=False)
        pi = G.window(t, T['pores'] - 0.3, T['cap'] - 0.4, 0.6)
        if pi > 0 and rc:
            cx, cy = 1500, 420
            G.line(ctx, [(rc[0], rc[1]), (cx - 150, cy + 90)], P.WHITE, 3, pi)
            G.circle(ctx, rc[0], rc[1], 30, stroke=P.WHITE, lw=4, alpha=pi)
            G.pore_inset(ctx, cx, cy, 210 * G.ease_out_back(pi), fluid='#4A3314', alpha=pi)
            # little oil/gas blobs
            G.text(ctx, 'sand grains', cx, cy + 260, 28, 'Bold', P.INK, 'center',
                   alpha=G.prog(t, T['grains'], 0.6) * pi)
            G.text(ctx, 'oil & gas in the pore space', cx, cy + 300, 28, 'Bold', P.OIL, 'center',
                   alpha=G.prog(t, T['hold'], 0.6) * pi)
        # cap rock
        ch = G.window(t, T['cap'] - 0.3, 100, 0.8)
        pulse = 0.75 + 0.25 * math.sin(t * 2.5)
        O.glow_quad(ctx, cq, P.ACCENT, ch * pulse * 0.9)
        cc = a(A, 'cap_c')
        if cc:
            G.label(ctx, cc[0], cc[1], cc[0] + 90, cc[1] - 150, 'Cap rock (shale)',
                    G.prog(t, T['cap'], 0.9), sub='dense and impermeable', col=P.WHITE,
                    bg=P.SHALE, sub_col='#DDE6EA', size=32, elbow=False)
        # migrating oil blocked by the cap rock
        mg = G.window(t, T['reason'] - 0.5, T['back'] + 3, 0.6)
        if mg > 0:
            for i in range(13):
                top = a(A, 'cap_x%d' % i)
                bot = a(A, 'res_x%d' % i)
                if not top or not bot:
                    continue
                ph = (t * 0.7 + i * 0.37) % 1.0
                y = bot[1] + (top[1] - bot[1]) * min(1.0, ph * 1.4)
                x = bot[0] + (top[0] - bot[0]) * ph
                bounce = ph > 0.72
                G.circle(ctx, x, y + (8 if bounce else 0), 7, fill=P.OIL, alpha=mg * 0.85)
                if bounce:
                    G.circle(ctx, x, y - 6, 12 * (ph - 0.72) * 4, stroke=P.WHITE, lw=2,
                             alpha=mg * (1 - ph) * 2)
        lp = G.prog(t, T['lid'] - 0.2, 0.7)
        if lp > 0:
            G.tag(ctx, "NATURE'S LID", 960, 150, lp, bg=P.SHALE, size=44, align='center')
        bp = G.prog(t, T['back'] - 0.2, 0.7)
        if bp > 0:
            G.text(ctx, '...and at the end, we must put it back.', 960, 235, 34, 'SemiBold',
                   P.INK, 'center', alpha=bp)
