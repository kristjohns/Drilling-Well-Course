"""Scene 10 - Drilling: the drill/case/cement/test cycle, the cement job, the leak-off test."""
import math

import gfx as G
import palette as P
import well2d as W2
from scene_base import Scene

CX = 760                    # casing centre x
Y_TOP, Y_FC, Y_SHOE, Y_BOT = 130, 860, 940, 985
CI, CO, HW = 64, 76, 132   # casing inner/outer half-width, hole half-width
VC = 400.0                  # cement volume (in casing-length pixels)
L_C = Y_FC - Y_TOP


def step_icon(ctx, kind, cx, cy, s, col, a):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    if kind == 'drill':
        G.poly(ctx, [(-22, -30), (22, -30), (16, 10), (0, 34), (-16, 10)], fill=col, alpha=a)
        G.rect(ctx, -6, -60, 12, 30, fill=col, alpha=a)
    elif kind == 'casing':
        G.rect(ctx, -26, -44, 12, 88, fill=col, alpha=a)
        G.rect(ctx, 14, -44, 12, 88, fill=col, alpha=a)
        G.poly(ctx, [(-26, 44), (-36, 44), (-26, 30)], fill=col, alpha=a)
        G.poly(ctx, [(26, 44), (36, 44), (26, 30)], fill=col, alpha=a)
    elif kind == 'cement':
        G.poly(ctx, [(-30, -10), (30, -10), (22, 40), (-22, 40)], fill=col, alpha=a)
        ctx.new_path()
        ctx.arc(0, -10, 30, math.pi, 2 * math.pi)
        G.set_color(ctx, col, a * 0.6)
        ctx.fill()
    else:
        G.circle(ctx, 0, 0, 38, stroke=col, lw=8, alpha=a)
        G.line(ctx, [(0, 0), (22, -18)], col, 7, a)
        G.circle(ctx, 0, 0, 7, fill=col, alpha=a)
    ctx.restore()


class S(Scene):
    ID = 's10_cementing'
    PHASE = 1

    def __init__(self):
        super().__init__()
        tl = self.tl
        self.T = dict(
            drill=tl.word('ce1', 'Drill.'),
            run=tl.word('ce1', 'Run casing'),
            cement=tl.word('ce1', 'Cement.'),
            test=tl.word('ce1', 'Test.'),
            choreo=tl.word('ce2', 'choreography'),
            bplug=tl.word('ce2', 'bottom plug'),
            cem=tl.word('ce2', 'the cement'),
            tplug=tl.word('ce2', 'top plug'),
            mud=tl.word('ce2', 'finally mud'),
            lands=tl.word('ce3', 'top plug lands'),
            spikes=tl.word('ce3', 'spikes'),
            bumped=tl.word('ce3', 'bumped the plug'),
            annulus=tl.word('ce3', 'annulus'),
            sets=tl.word('ce3', 'sets hard'),
            drilling=tl.word('ce4', 'drilling a few'),
            lot=tl.word('ce4', 'leak-off test'),
            shoe=tl.word('ce4', 'casing shoe'),
            heavier=tl.word('ce4', 'heavier mud'),
        )
        T = self.T
        self.t_job0 = T['choreo'] - 0.2
        self.t_bump = T['lands'] + 0.3
        self.t_lot = tl.t('ce4') - 0.3

    def V(self, t):
        """Pumped volume (pixels of casing length)."""
        return (L_C + VC) * G.clamp((t - self.t_job0) / (self.t_bump - self.t_job0))

    # ------------------------------------------------------------------ draw
    def draw(self, ctx, t, f, A):
        T = self.T
        cyc = 1 - G.prog(t, self.t_job0 - 0.6, 0.6)
        if cyc > 0:
            self.draw_cycle(ctx, t, cyc)
        job = G.prog(t, self.t_job0 - 0.3, 0.7)
        if job > 0:
            ctx.save()
            ctx.push_group()
            self.draw_section(ctx, t)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(job)
            ctx.restore()
            self.draw_right(ctx, t, job)

    def draw_cycle(self, ctx, t, a):
        T = self.T
        cx, cy, R = 960, 560, 250
        steps = [('drill', 'DRILL', T['drill']), ('casing', 'RUN CASING', T['run']),
                 ('cement', 'CEMENT', T['cement']), ('test', 'TEST', T['test'])]
        G.text(ctx, 'SECTION BY SECTION', cx, 170, 34, 'Bold', P.INK_SOFT, 'center', alpha=a,
               tracking=0.2)
        # circular arrows
        for i in range(4):
            a0 = -math.pi / 2 + i * math.pi / 2 + 0.38
            a1 = a0 + math.pi / 2 - 0.76
            p = G.prog(t, steps[i][2] + 0.2, 0.6)
            pts = [(cx + R * math.cos(a0 + (a1 - a0) * k / 30), cy + R * math.sin(a0 + (a1 - a0) * k / 30))
                   for k in range(31)]
            G.arrow_path(ctx, pts, P.INK_SOFT, 6, 22, p, a)
        for i, (kind, lab, t0) in enumerate(steps):
            ang = -math.pi / 2 + i * math.pi / 2
            x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
            p = G.prog(t, t0 - 0.2, 0.6)
            hi = G.window(t, t0 - 0.2, (steps[i + 1][2] - 0.2) if i < 3 else 100, 0.3)
            if p <= 0:
                continue
            r = 95 * G.ease_out_back(p)
            G.circle(ctx, x, y + 6, r, fill=(0, 0, 0, 0.15), alpha=a)
            G.circle(ctx, x, y, r, fill=G.mix('#FFFFFF', '#2F80C9', hi), alpha=a)
            step_icon(ctx, kind, x, y - 12, 0.9, G.mix('#2F80C9', '#FFFFFF', hi), a * p)
            G.text(ctx, lab, x, y + 62, 22, 'ExtraBold', G.mix(P.INK, '#FFFFFF', hi), 'center',
                   alpha=a * p, tracking=0.06)

    def draw_section(self, ctx, t):
        T = self.T
        V = self.V(t)
        # rock
        from well2d import pattern
        ctx.save()
        ctx.rectangle(CX - 360, Y_TOP - 20, 720, Y_BOT + 60 - Y_TOP)
        ctx.clip()
        ctx.set_source(pattern('siltstone', 0.6))
        ctx.paint()
        ctx.restore()
        # open hole with mud
        G.rect(ctx, CX - HW, Y_TOP - 20, 2 * HW, Y_BOT - Y_TOP + 20, fill=P.MUD)
        # new hole below the shoe (leak-off stage)
        dr = G.prog(t, T['drilling'] - 0.3, 1.2)
        if dr > 0:
            G.rect(ctx, CX - 50, Y_BOT - 2, 100, 60 * dr, fill=P.MUD)
        # annulus cement
        ann_h = max(0.0, V - L_C) * (2 * CI) / (2 * (HW - CO))
        if ann_h > 0:
            y0 = Y_BOT - ann_h
            for sx in (-1, 1):
                x0 = CX + sx * CO
                ctx.rectangle(min(x0, x0 + sx * (HW - CO)), y0, HW - CO, Y_BOT - y0)
                ctx.save()
                ctx.clip()
                ctx.set_source(pattern('cement', 0.4))
                ctx.paint()
                ctx.restore()
            # cement under the shoe
            G.rect(ctx, CX - HW, Y_SHOE, 2 * HW, Y_BOT - Y_SHOE, fill=P.CEMENT)
        # casing inside: mud, cement between plugs, displacement mud
        y_bp = min(Y_FC, Y_TOP + V)
        y_tp = min(Y_FC - 18, Y_TOP + max(0.0, V - VC))
        started = V > 0
        G.rect(ctx, CX - CI, Y_TOP, 2 * CI, Y_SHOE - Y_TOP, fill=P.MUD)
        if started:
            # cement column between the plugs
            c_top = y_tp if V > VC else Y_TOP
            c_bot = y_bp
            ctx.rectangle(CX - CI, c_top, 2 * CI, c_bot - c_top)
            ctx.save()
            ctx.clip()
            ctx.set_source(pattern('cement', 0.4))
            ctx.paint()
            ctx.restore()
            if V > VC:
                G.rect(ctx, CX - CI, Y_TOP, 2 * CI, y_tp - Y_TOP, fill=P.HEAVY_MUD)
            # shoe track below the float collar fills with cement once the bottom plug lands
            if V > L_C:
                ctx.rectangle(CX - CI, Y_FC, 2 * CI, Y_SHOE - Y_FC)
                ctx.save()
                ctx.clip()
                ctx.set_source(pattern('cement', 0.4))
                ctx.paint()
                ctx.restore()
        # drilled-out shoe track during the LOT stage
        if dr > 0:
            G.rect(ctx, CX - 50, Y_FC - 30, 100, (Y_BOT - Y_FC + 30), fill=P.MUD, alpha=dr)
        # casing walls, float collar, shoe
        for sx in (-1, 1):
            G.rect(ctx, CX + sx * CI if sx > 0 else CX - CO, Y_TOP - 20, CO - CI, Y_SHOE - Y_TOP + 20,
                   fill=P.STEEL_DARK)
        G.rect(ctx, CX - CO, Y_FC - 4, 2 * CO, 10, fill='#4A5663')
        G.poly(ctx, [(CX - CO, Y_SHOE), (CX + CO, Y_SHOE), (CX + CO - 10, Y_SHOE + 16),
                     (CX - CO + 10, Y_SHOE + 16)], fill='#4A5663')
        # plugs
        if started and (dr < 0.5):
            self.plug(ctx, y_bp, P.KICK, burst=V > L_C)
        if V > VC and dr < 0.5:
            self.plug(ctx, y_tp, '#1E2329')
        # flow arrows in the annulus while displacing
        flowing = self.t_job0 + 1 < t < self.t_bump
        if flowing and V > L_C:
            for sx in (-1, 1):
                for k in range(3):
                    ph = (t * 1.2 + k / 3) % 1.0
                    y = Y_BOT - 20 - ph * 400
                    G.arrow(ctx, CX + sx * (CO + HW) / 2, y + 20, CX + sx * (CO + HW) / 2, y - 20,
                            '#FFFFFF', 5, 14, 1, 0.8 * (1 - ph))
        # labels
        L = [
            (CX + CI, y_bp - 18, 'Bottom plug', T['bplug'], P.KICK, self.t_bump + 1),
            (CX + CI, (y_tp + y_bp) / 2 if V > VC else (Y_TOP + y_bp) / 2, 'Cement', T['cem'],
             P.INK, T['mud'] + 1.5),
            (CX + CI, y_tp - 18, 'Top plug', T['tplug'], '#1E2329', self.t_bump + 1),
            (CX + CI, Y_TOP + 60, 'Displacement mud', T['mud'], P.HEAVY_MUD, self.t_bump + 1),
        ]
        for ax, ay, txt, t0, col, t1 in L:
            G.label(ctx, ax, ay, CX + 220, ay, txt, G.prog(t, t0 - 0.1, 0.6), size=26,
                    out=G.prog(t, t1, 0.4), elbow=False, col=P.WHITE, bg=col)
        sh = G.prog(t, T['sets'] - 0.3, 0.6) * (1 - G.prog(t, self.t_lot, 0.4))
        if sh > 0:
            G.label(ctx, CX - (CO + HW) / 2, Y_BOT - 200, CX - 240, Y_BOT - 260, 'Cement sets hard',
                    sh, sub='annulus sealed', size=28, align='right', elbow=False)

    def plug(self, ctx, y, col, burst=False):
        G.rrect(ctx, CX - CI + 4, y - 30, 2 * CI - 8, 30, 8)
        G.set_color(ctx, col)
        ctx.fill()
        for k in range(3):
            G.rect(ctx, CX - CI, y - 28 + k * 9, 2 * CI, 4, fill=G.mix(col, '#FFFFFF', 0.25))
        if burst:
            G.rect(ctx, CX - 18, y - 30, 36, 30, fill=P.CEMENT)

    def draw_right(self, ctx, t, a):
        T = self.T
        # pumping pressure chart (cement job)
        pj = G.prog(t, T['spikes'] - 1.2, 0.6) * (1 - G.prog(t, self.t_lot - 0.2, 0.5))
        if pj > 0:
            c = G.Chart(1150, 300, 620, 380, (0, 10), (0, 10))
            G.panel(ctx, 1080, 180, 760, 600, pj)
            G.text(ctx, 'PUMP PRESSURE', 1460, 250, 28, 'ExtraBold', P.INK, 'center', alpha=pj,
                   tracking=0.08)
            c.axes(ctx, pj, xlabel='time', ylabel='pressure', size=22, grid=False)
            data = [(x / 10, 2.5 + 0.8 * math.sin(x / 7) + 0.02 * x) for x in range(0, 86)]
            data += [(8.6 + k * 0.02, 3.6 + k * 0.28) for k in range(20)]
            prog = G.prog(t, T['spikes'] - 1.2, 1.6, G.linear)
            end = c.curve(ctx, data, '#2F80C9', 5, prog, pj)
            bp = G.prog(t, T['bumped'] - 0.2, 0.6)
            if bp > 0 and end:
                G.label(ctx, end[0], end[1], end[0] - 40, end[1] + 120, 'Bumped the plug!', bp,
                        col=P.WHITE, bg=P.KICK, size=26, align='right', elbow=False)
        # leak-off test chart
        lp = G.prog(t, T['lot'] - 0.3, 0.6)
        if lp > 0:
            c = G.Chart(1150, 300, 620, 380, (0, 10), (0, 10))
            G.panel(ctx, 1080, 180, 760, 600, lp)
            G.text(ctx, 'LEAK-OFF TEST', 1460, 250, 28, 'ExtraBold', P.INK, 'center', alpha=lp,
                   tracking=0.08)
            c.axes(ctx, lp, xlabel='volume pumped', ylabel='pressure', size=22, grid=False)
            data = [(x / 10, x / 10 * 1.0) for x in range(0, 66)]
            data += [(6.6 + k / 10, 6.6 + 0.9 * (1 - math.exp(-k / 8)) * 1.6) for k in range(30)]
            prog = G.prog(t, T['lot'] + 0.2, 3.0, G.linear)
            c.curve(ctx, data, P.SECONDARY, 5, prog, lp)
            lk = G.prog(t, T['shoe'] - 0.2, 0.6)
            if lk > 0:
                x, y = c.px(6.6, 6.6)
                G.label(ctx, x, y, x - 40, y - 130, 'Leak-off point', lk, col=P.WHITE,
                        bg=P.SECONDARY, size=26, align='right', elbow=False)
            hv = G.prog(t, T['heavier'] - 0.2, 0.6)
            if hv > 0:
                G.text(ctx, 'sets the maximum mud weight for the next section', 1460, 290, 24,
                       'Bold', P.SECONDARY, 'center', alpha=hv)
            # pressure arrows at the shoe on the section
            if lk > 0:
                for sx in (-1, 1):
                    G.arrow(ctx, CX + sx * 50, Y_BOT + 30, CX + sx * 150, Y_BOT + 30, P.SECONDARY, 6,
                            18, lk, lk)
