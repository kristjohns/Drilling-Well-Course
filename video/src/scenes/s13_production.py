"""Scene 13 - Production: decades of flow, declining pressure, end of life."""
import math

import gfx as G
import palette as P
from scene_base import Scene
from scenes.s07_tophole import underwater_bg


class S(Scene):
    ID = 's13_production'
    BLENDER = True
    PHASE = 2
    DARK = True

    def __init__(self):
        super().__init__()
        tl = self.tl
        self.T = dict(
            produces=tl.word('pd1', 'produces'),
            pressure=tl.word('pd2', 'pressure slowly falls'),
            water=tl.word('pd2', 'more water'),
            end=tl.word('pd2', 'end of its life'),
            final=tl.word('pd3', 'final chapter'),
        )

    def draw_bg(self, ctx, t, f):
        underwater_bg(ctx, t)

    def build(self):
        import bl
        import equipment as E
        import seabed_set
        tl = self.tl
        F = lambda s: int(round(s * 24))  # noqa: E731
        M = E.mats()
        S_ = seabed_set.production_set(M)
        cam = bl.Cam((10, -30, 14), (5, 2, 2), lens=35)
        cam.key(0, loc=(4, -32, 15), target=(5, 2, 2.5))
        cam.key(F(tl.duration + 0.6), loc=(20, -26, 11), target=(6, 2, 2.0))
        A = {}
        pts = S_['jumper_pts']
        for i in range(12):
            u = i / 11
            A['j%d' % i] = self._pt(pts, u)
        A['xt'] = (0, 0, 6.8)
        return A

    @staticmethod
    def _pt(pts, u):
        L = [0.0]
        for a, b in zip(pts[:-1], pts[1:]):
            L.append(L[-1] + math.dist(a, b))
        tgt = L[-1] * u
        for i in range(len(pts) - 1):
            if L[i] <= tgt <= L[i + 1]:
                k = (tgt - L[i]) / max(1e-9, L[i + 1] - L[i])
                return tuple(pts[i][j] + (pts[i + 1][j] - pts[i][j]) * k for j in range(3))
        return pts[-1]

    def draw(self, ctx, t, f, A):
        T = self.T
        a = self.A
        dur = self.tl.duration
        # flow along the jumper (fades as the well ages)
        age = G.clamp((t - 0.5) / (T['end'] - 0.5))
        fa = (1 - 0.7 * age) * (1 - G.prog(t, T['final'] - 0.5, 1.0))
        pts = [a(A, 'j%d' % i) for i in range(12)]
        if all(pts):
            for k in range(20):
                ph = (t * (0.5 - 0.3 * age) + k / 20) % 1.0
                x, y = G.point_at(pts, ph)
                oil = G.mix(P.OIL_GLOW, '#6FB3DE', age * G.clamp(k % 3 / 2 + 0.2))
                G.circle(ctx, x, y, 7, fill=oil, alpha=0.9 * fa)
        # year counter
        yp = G.window(t, 0.6, T['final'] - 0.2, 0.5)
        if yp > 0:
            year = 1 + int(29 * G.clamp((t - 1.0) / (T['end'] - 1.0)))
            G.panel(ctx, 80, 150, 330, 150, yp)
            G.text(ctx, 'YEAR', 245, 205, 26, 'Bold', P.INK_SOFT, 'center', alpha=yp, tracking=0.2)
            G.text(ctx, str(year), 245, 275, 70, 'ExtraBold', P.INK, 'center', alpha=yp)
        # production chart
        cp = G.window(t, T['pressure'] - 0.8, T['final'] - 0.2, 0.6)
        if cp > 0:
            G.panel(ctx, 1180, 150, 640, 460, cp)
            c = G.Chart(1260, 220, 500, 300, (0, 30), (0, 1))
            c.axes(ctx, cp, size=22, grid=False, xticks=(10, 20, 30),
                   tick_fmt=lambda v: f'{v} yr')
            n = G.prog(t, T['pressure'] - 0.5, T['end'] - T['pressure'] + 0.5, G.linear)
            oil = [(x, 0.92 * math.exp(-x / 11) + 0.04) for x in range(0, 31)]
            wat = [(x, 0.9 / (1 + math.exp(-(x - 16) / 4))) for x in range(0, 31)]
            c.curve(ctx, oil, P.OIL_GLOW, 5, n, cp)
            c.curve(ctx, wat, '#3A93CF', 5, G.prog(t, T['water'] - 0.4, 3.0, G.linear), cp)
            G.text(ctx, 'oil rate', 1300, 250, 24, 'Bold', P.OIL_GLOW, alpha=cp)
            G.text(ctx, 'water cut', 1300, 285, 24, 'Bold', '#3A93CF',
                   alpha=cp * G.prog(t, T['water'] - 0.2, 0.6))
            G.text(ctx, 'reservoir pressure falls', 1500, 590, 24, 'SemiBold', P.INK_SOFT, 'center',
                   alpha=cp * G.prog(t, T['pressure'], 0.6))
        # final chapter
        fp = G.prog(t, T['final'] - 0.8, 1.2)
        if fp > 0:
            ctx.set_source_rgba(0.03, 0.07, 0.12, 0.65 * fp)
            ctx.paint()
            G.text(ctx, 'END OF LIFE', 960, 540, 80, 'ExtraBold', P.WHITE, 'center', alpha=fp,
                   tracking=0.12)
            G.text(ctx, '...and then comes the final chapter', 960, 620, 34, 'SemiBold', '#BFD6E8',
                   'center', alpha=G.prog(t, T['final'] - 0.4, 0.8))
