"""Scene 5 - Design: the two-barrier principle (NORSOK D-010)."""
import math

import gfx as G
import palette as P
import schem
import well2d as W2
from scene_base import Scene


class S(Scene):
    ID = 's05_barriers'
    PHASE = 0

    def __init__(self):
        super().__init__()
        tl = self.tl
        self.w = schem.make()
        self.T = dict(
            rule=tl.word('ba1', 'golden rule'),
            norsok=tl.word('ba1', 'Norsok'),
            two=tl.word('ba1', 'two independent'),
            reservoir=tl.word('ba1', 'reservoir'),
            outside=tl.word('ba1', 'outside world'),
            fails=tl.word('ba2', 'fails'),
            holds=tl.word('ba2', 'holds'),
            env=tl.word('ba3', 'envelopes'),
            blue=tl.word('ba3', 'blue'),
            red=tl.word('ba3', 'red'),
            check=tl.word('ba3', 'keep checking'),
        )
        self.t_schem = tl.t('ba3') - 0.6

    def draw(self, ctx, t, f, A):
        T = self.T
        s1 = 1 - G.prog(t, self.t_schem, 0.8)
        if s1 > 0:
            self.draw_shields(ctx, t, s1)
        s2 = G.prog(t, self.t_schem + 0.2, 0.8)
        if s2 > 0:
            self.draw_schematic(ctx, t, s2)

    def draw_shields(self, ctx, t, a):
        T = self.T
        G.text(ctx, 'THE GOLDEN RULE', 960, 190, 30, 'Bold', P.INK_SOFT, 'center',
               alpha=a * G.prog(t, T['rule'] - 0.3, 0.6), tracking=0.2)
        nb = G.prog(t, T['norsok'] - 0.2, 0.6)
        G.tag(ctx, 'NORSOK D-010', 960, 260, nb * a, bg=P.INK, size=34, align='center')
        G.text(ctx, 'Two independent, tested well barriers', 960, 360, 52, 'ExtraBold', P.INK,
               'center', alpha=a * G.prog(t, T['two'] - 0.2, 0.7))
        # reservoir block
        rp = G.prog(t, T['rule'] + 0.8, 0.6) * a
        if rp > 0:
            G.shadow_rrect(ctx, 170, 520, 360, 300, 30, alpha=0.2 * rp)
            G.rrect(ctx, 170, 520, 360, 300, 30)
            G.set_color(ctx, P.RESERVOIR, rp)
            ctx.fill()
            G.text(ctx, 'RESERVOIR', 350, 780, 34, 'ExtraBold', P.WHITE, 'center', alpha=rp,
                   tracking=0.08)
            for k in range(7):
                x = 230 + (k * 53) % 250
                y = 580 + (k * 37) % 140
                G.circle(ctx, x + 10 * math.sin(t * 2 + k), y, 14, fill=P.OIL, alpha=rp * 0.9)
        op = G.prog(t, T['rule'] + 1.3, 0.6) * a
        if op > 0:
            G.shadow_rrect(ctx, 1390, 520, 360, 300, 30, alpha=0.2 * op)
            G.rrect(ctx, 1390, 520, 360, 300, 30)
            G.set_color(ctx, '#3A93CF', op)
            ctx.fill()
            for k in range(3):
                pts = [(1420 + i * 10, 610 + k * 50 + 10 * math.sin(i * 0.35 + t * 2)) for i in range(31)]
                G.line(ctx, pts, P.WHITE, 5, op * 0.8)
            G.text(ctx, 'ENVIRONMENT', 1570, 780, 34, 'ExtraBold', P.WHITE, 'center', alpha=op,
                   tracking=0.08)
        # shields
        crack = G.prog(t, T['fails'] - 0.2, 0.5)
        brk = G.prog(t, T['fails'] + 0.3, 0.5)
        sp1 = G.prog(t, T['two'] + 0.3, 0.6) * a
        sp2 = G.prog(t, T['two'] + 0.7, 0.6) * a
        x1 = 760 + 30 * brk
        schem.shield(ctx, x1, 670, 170, 220, P.PRIMARY, sp1 * (1 - 0.65 * brk), crack, '1')
        schem.shield(ctx, 1150, 670, 170, 220, P.SECONDARY, sp2, 0, '2')
        # flow arrows pushing from the reservoir
        fl = G.prog(t, T['reservoir'] + 0.8, 0.8) * a
        if fl > 0:
            stop = 660 if brk < 0.5 else 1040
            for k in range(3):
                y = 610 + k * 60
                ph = (t * 0.9 + k * 0.3) % 1.0
                x = 560 + (stop - 560) * ph
                G.arrow(ctx, x - 60, y, x, y, P.OIL, 7, 20, 1.0, fl * (0.3 + 0.7 * (1 - ph)))
        hp = G.prog(t, T['holds'] - 0.1, 0.5) * a
        if hp > 0:
            G.tag(ctx, 'HOLDS', 1150, 850, hp, bg=P.GOOD, size=34, align='center')
            G.tag(ctx, 'FAILED', x1, 850, hp, bg='#8A96A3', size=30, align='center')

    def draw_schematic(self, ctx, t, a):
        T = self.T
        w = self.w
        G.panel(ctx, w.x0 - 20, 80, w.x1 - w.x0 + 40, 960, a, alpha=0.95)
        ctx.save()
        ctx.push_group()
        schem.drilling_well(ctx, w, t)
        prim, sec = schem.drilling_envelopes(w)
        pb = G.prog(t, T['blue'] - 0.3, 1.6)
        pr = G.prog(t, T['red'] - 0.3, 1.8)
        W2.envelope(ctx, prim, P.PRIMARY, pb)
        W2.envelope(ctx, sec, P.SECONDARY, pr)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(a)
        ctx.restore()
        G.text(ctx, 'While drilling', 1340, 190, 44, 'ExtraBold', P.INK, 'center', alpha=a)
        schem.legend(ctx, 930, 280, [
            (P.PRIMARY, 'Primary barrier', 'the column of drilling mud',
             G.prog(t, T['blue'] - 0.2, 0.6)),
            (P.SECONDARY, 'Secondary barrier', 'casing, cement, wellhead and BOP',
             G.prog(t, T['red'] - 0.2, 0.6)),
        ], a)
        ck = G.prog(t, T['check'] - 0.2, 0.7) * a
        if ck > 0:
            G.panel(ctx, 930, 560, 820, 170, ck)
            G.text(ctx, 'Every barrier element is tested', 1340, 630, 34, 'Bold', P.INK, 'center',
                   alpha=ck)
            G.text(ctx, 'and monitored, at every stage of the well’s life', 1340, 680, 28,
                   'SemiBold', P.INK_SOFT, 'center', alpha=ck)
