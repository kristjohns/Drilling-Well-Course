"""The drilling-window chart shared by the pressure and casing scenes."""
import gfx as G
import palette as P
import well2d as W2

# shared schematic geometry for scenes 3 and 4
KNOTS = [(0, 170), (350, 250), (3450, 1000)]


def schematic():
    return W2.Well2D(cx=400, knots=KNOTS, x0=150, x1=650, k=2.4)


class WindowChart:
    def __init__(self, well, x0=820, x1=1760, sg=(1.0, 2.0)):
        self.w = well
        self.x0, self.x1 = x0, x1
        self.sg = sg

    def px(self, sg, d):
        return (self.x0 + (sg - self.sg[0]) / (self.sg[1] - self.sg[0]) * (self.x1 - self.x0),
                self.w.y(d))

    def pts(self, table_samples):
        return [self.px(v, d) for v, d in table_samples]

    def axes(self, ctx, p, alpha=1.0):
        if p <= 0:
            return
        y_top = self.w.y(350)
        y_bot = self.w.y(3450)
        # panel
        G.panel(ctx, self.x0 - 110, y_top - 110, self.x1 - self.x0 + 170, y_bot - y_top + 150,
                p, alpha=0.9 * alpha)
        pa = G.ease_in_out(G.clamp((p - 0.2) / 0.8)) * alpha
        # grid
        for sg in (1.2, 1.4, 1.6, 1.8, 2.0):
            x, _ = self.px(sg, 0)
            G.line(ctx, [(x, y_top), (x, y_bot)], '#B8C7D6', 1.2, pa * 0.7)
        for d in (1000, 2000, 3000):
            y = self.w.y(d)
            G.line(ctx, [(self.x0, y), (self.x1, y)], '#B8C7D6', 1.2, pa * 0.7)
            G.text(ctx, f'{d:,} m', self.x0 - 16, y, 22, 'Medium', P.INK_SOFT, 'right', 'middle',
                   alpha=pa)
        # axes: pressure along top, depth downwards
        G.arrow(ctx, self.x0, y_top, self.x1 + 30, y_top, P.INK, 3.5, 16, p, alpha)
        G.arrow(ctx, self.x0, y_top, self.x0, y_bot + 30, P.INK, 3.5, 16, p, alpha)
        for sg in (1.0, 1.2, 1.4, 1.6, 1.8, 2.0):
            x, _ = self.px(sg, 0)
            G.text(ctx, f'{sg:.1f}', x, y_top - 16, 22, 'Medium', P.INK_SOFT, 'center', alpha=pa)
        G.text(ctx, 'PRESSURE  →', (self.x0 + self.x1) / 2, y_top - 58, 24, 'Bold', P.INK,
               'center', alpha=pa, tracking=0.08)
        G.text(ctx, '(as equivalent mud density, s.g.)', (self.x0 + self.x1) / 2 + 190,
               y_top - 58, 18, 'Medium', P.INK_SOFT, 'left', alpha=pa)
        G.text(ctx, 'DEPTH ↓', self.x0 - 16, y_top - 16, 22, 'Bold', P.INK, 'right', alpha=pa,
               tracking=0.08)

    def pore(self, ctx, p, alpha=1.0, lw=6):
        return G.line(ctx, self.pts(W2.sample(W2.PORE, 350, 3450, 120)), P.PRIMARY, lw, alpha, p)

    def frac(self, ctx, p, alpha=1.0, lw=6):
        return G.line(ctx, self.pts(W2.sample(W2.FRAC, 350, 3450, 120)), P.SECONDARY, lw, alpha, p)

    def window(self, ctx, p, alpha=1.0, col=P.GOOD):
        if p <= 0:
            return
        d1 = 350 + (3450 - 350) * p
        lo = self.pts(W2.sample(W2.PORE, 350, d1, 100))
        hi = self.pts(W2.sample(W2.FRAC, 350, d1, 100))
        G.poly(ctx, lo + hi[::-1], fill=col, alpha=0.22 * alpha)

    def kick_zone(self, ctx, alpha):
        if alpha <= 0:
            return
        lo = self.pts(W2.sample(W2.PORE, 350, 3450, 100))
        left = [(self.x0, y) for _, y in lo]
        G.poly(ctx, left + lo[::-1], fill=P.KICK, alpha=0.10 * alpha)

    def loss_zone(self, ctx, alpha):
        if alpha <= 0:
            return
        hi = self.pts(W2.sample(W2.FRAC, 350, 3450, 100))
        right = [(self.x1, y) for _, y in hi]
        G.poly(ctx, hi + right[::-1], fill=P.MUD, alpha=0.12 * alpha)

    def mud_line(self, ctx, p, t, alpha=1.0, wobble=True):
        """A single mud-weight curve weaving inside the window."""
        import math
        pts = []
        for i in range(121):
            d = 350 + 3100 * i / 120
            lo, hi = W2.interp(W2.PORE, d), W2.interp(W2.FRAC, d)
            k = 0.5 + (0.12 * math.sin(d / 260 + t * 1.5) if wobble else 0)
            pts.append(self.px(lo + (hi - lo) * k, d))
        G.line(ctx, pts, P.MUD, 9, alpha * 0.25, p)
        G.line(ctx, pts, P.MUD, 4.5, alpha, p, dash=[14, 10])

    def steps(self, ctx, p, alpha=1.0, upto=5):
        """Stair-step mud weights per hole section, drawn progressively bottom-up."""
        segs = W2.MUD_STEPS[:upto]
        n = len(segs)
        for i, (d0, d1, sg) in enumerate(segs):
            pi = G.clamp(p * n - i)
            if pi <= 0:
                continue
            a = self.px(sg, d0)
            b = self.px(sg, d1)
            G.line(ctx, [a, b], P.MUD, 7, alpha, pi)
            if i + 1 < n and pi >= 1:
                nb = self.px(segs[i + 1][2], d1)
                G.line(ctx, [b, nb], P.MUD, 3, alpha * 0.8, 1.0, dash=[6, 6])
