"""Scene 15 - Recap of the four phases and the end card."""
import math

import gfx as G
import overlays as O
import palette as P
from scene_base import Scene

SUMMARY = [
    ('the drilling window · a telescope of casings', 'two independent barriers'),
    ('a floating rig · the BOP', 'mud holding back the rock'),
    ('liner · perforations · tubing', 'safety valve · christmas tree'),
    ('permanent, rock-to-rock barriers', 'removed without a trace'),
]


class S(Scene):
    ID = 's15_outro'
    BLENDER = True

    def __init__(self):
        super().__init__()
        tl = self.tl
        self.T = dict(
            recap=tl.t('ou1'),
            p0=tl.t('ou2'), p1=tl.t('ou3'), p2=tl.t('ou4'), p3=tl.t('ou5'),
            decades=tl.t('ou6'),
            thanks=tl.word('ou6', 'Thanks'),
        )

    def build(self):
        import bl
        import equipment as E
        import models as MD
        tl = self.tl
        F = lambda s: int(round(s * 24))  # noqa: E731
        D = MD.Diorama(well=True, cores=False)
        d = D.dio
        for i in range(5):
            MD.casing_string(d, i)
        plug_m = bl.mat('plug_glow', '#E9E4D8', rough=0.8)
        for (a_, b_) in ((2780, 2930), (2560, 2700), (70, 210)):
            r = d.r(9.625) / 2 * 0.92
            bl.annulus('dio_plug', 0, r, d.z(b_), d.z(a_), 0, math.pi, 32, plug_m)
        MD.ocean(spatial=10, wave_scale=0.05, wind=9, alpha=0.96, col='#2A78B8',
                 frames=(0, tl.nframes + 40))
        cam = bl.Cam((14, -33, -2), (3.5, 1, -7), lens=35)
        n = tl.nframes + 30
        cam.orbit(0, n, (0.0, 2.0, -8.0), 52.0, 4.0, -64, -108, lens=35, target=(7.0, 2.0, -8.5))
        return {}

    def draw(self, ctx, t, f, A):
        T = self.T
        # right-hand recap panel
        pp = G.prog(t, T['recap'] - 0.3, 0.8) * (1 - G.prog(t, T['decades'] - 0.6, 0.6))
        if pp > 0:
            x0, y0 = 1060, 120
            G.panel(ctx, x0, y0, 800, 860, pp, alpha=0.94)
            G.text(ctx, 'RECAP', x0 + 60, y0 + 90, 30, 'ExtraBold', P.INK_SOFT, alpha=pp,
                   tracking=0.25)
            G.text(ctx, 'The life of a subsea well', x0 + 60, y0 + 150, 44, 'ExtraBold', P.INK,
                   alpha=pp)
            for i in range(4):
                p = G.prog(t, T['p%d' % i] - 0.2, 0.6)
                hi = G.window(t, T['p%d' % i] - 0.2, (T['p%d' % (i + 1)] - 0.2) if i < 3 else
                              T['decades'] - 0.6, 0.3)
                kind, title, col = O.PHASE_INFO[i]
                y = y0 + 230 + i * 150
                if p <= 0:
                    continue
                a = pp * p
                G.rrect(ctx, x0 + 40, y, 720, 128, 20)
                G.set_color(ctx, G.mix('#F3F6F9', col, 0.14 * hi), a)
                ctx.fill()
                G.circle(ctx, x0 + 112, y + 64, 46, fill=col, alpha=a)
                O.icon(ctx, kind, x0 + 112, y + 64, 0.5, P.WHITE, a)
                G.text(ctx, f'{i + 1}  {title.upper()}', x0 + 180, y + 48, 30, 'ExtraBold', col,
                       alpha=a, tracking=0.06)
                for k, ln in enumerate(SUMMARY[i]):
                    G.text(ctx, ln, x0 + 180, y + 84 + k * 27, 22, 'SemiBold', P.INK_SOFT, alpha=a)
        # end card
        ep = G.prog(t, T['decades'] - 0.4, 1.0)
        if ep > 0:
            ctx.set_source_rgba(0.04, 0.10, 0.17, 0.72 * ep)
            ctx.paint()
            G.text(ctx, 'Decades of engineering,', 960, 400, 56, 'Bold', '#D6E6F2', 'center',
                   alpha=ep)
            G.text(ctx, 'for one hole in the ground.', 960, 480, 56, 'Bold', '#D6E6F2', 'center',
                   alpha=G.prog(t, T['decades'] + 1.4, 0.8))
            tp = G.prog(t, T['thanks'] - 0.2, 0.9)
            G.text(ctx, 'THE LIFE OF A', 960, 640, 34, 'Bold', '#8FC3E3', 'center', alpha=tp,
                   tracking=0.25)
            G.text(ctx, 'SUBSEA WELL', 960, 735, 96, 'ExtraBold', P.WHITE, 'center', alpha=tp,
                   tracking=0.04)
            bw = 380 * tp
            G.rrect(ctx, 960 - bw / 2, 765, bw, 8, 4)
            G.set_color(ctx, P.ACCENT, tp)
            ctx.fill()
            G.text(ctx, 'Thanks for watching', 960, 840, 36, 'SemiBold', '#D6E6F2', 'center',
                   alpha=G.prog(t, T['thanks'] + 0.3, 0.8))
        # final fade to black
        fb = G.prog(t, self.tl.duration - 1.6, 1.5)
        if fb > 0:
            ctx.set_source_rgba(0, 0, 0, fb)
            ctx.paint()
