"""Scene 11 - Drilling: kick detection, shut-in and circulating out the influx."""
import math

import gfx as G
import palette as P
import schem
import well2d as W2
from scene_base import Scene


class S(Scene):
    ID = 's11_wellcontrol'
    PHASE = 1

    def __init__(self):
        super().__init__()
        tl = self.tl
        self.w = schem.make()
        self.T = dict(
            kick=tl.word('wc1', 'kick'),
            surface=tl.word('wc1', 'surface'),
            pits=tl.word('wc1', 'mud pits'),
            gain=tl.word('wc1', 'gain volume'),
            shut=tl.word('wc2', 'shuts in'),
            reads=tl.word('wc2', 'reads the pressures'),
            circ=tl.word('wc2', 'circulates'),
            choke=tl.word('wc2', 'choke line'),
            kill=tl.word('wc2', 'kill mud'),
            control=tl.word('wc3', 'under control'),
            two=tl.word('wc3', 'two barriers'),
        )

    def draw(self, ctx, t, f, A):
        T = self.T
        w = self.w
        G.panel(ctx, w.x0 - 20, 80, w.x1 - w.x0 + 40, 960, 1.0, alpha=0.95)
        closed = G.prog(t, T['shut'] - 0.1, 0.8)
        # kill mud rising from the bottom of the well
        kp = G.prog(t, T['kill'] - 0.5, 5.0, G.linear)
        schem.drilling_well(ctx, w, t, bop_closed=closed)
        ctx.save()
        ctx.rectangle(w.x0, 90, w.x1 - w.x0, 940)
        ctx.clip()
        if kp > 0:
            top = 3050 - (3050 - 350) * kp
            shoe = W2.CASINGS[2][3]
            w.fill_bore(ctx, max(top, shoe), 3050, P.HEAVY_MUD, 1.0)
            if top < shoe:
                ihw = w.hw(W2.CASINGS[2][1]) - max(4.0, w.k * 0.9)
                G.rect(ctx, w.cx - ihw, w.y(top), 2 * ihw, w.y(shoe) - w.y(top), fill=P.HEAVY_MUD)
            G.rect(ctx, w.cx - 5, w.y(top), 10, w.y(3050) - w.y(top) - 14, fill=P.PIPE)
        # choke line from the BOP up to the rig
        y_bed = w.y(350)
        ch = G.prog(t, T['choke'] - 0.4, 0.6)
        G.line(ctx, [(w.cx + 58, y_bed - 90), (w.cx + 90, y_bed - 90), (w.cx + 90, 90)], '#7E8B98',
               8, 1.0)
        # the influx (gas bubble group)
        self.influx(ctx, t, closed)
        ctx.restore()
        if ch > 0:
            G.label(ctx, w.cx + 90, 200, w.cx + 180, 170, 'Choke line', ch, size=24, elbow=False)
        # right-hand side: pit gain, gauges, outcome
        self.right_panel(ctx, t)
        # barriers at the end
        ev = G.prog(t, T['two'] - 0.4, 1.4)
        if ev > 0:
            prim, sec = schem.drilling_envelopes(w)
            W2.envelope(ctx, prim, P.PRIMARY, ev)
            W2.envelope(ctx, sec, P.SECONDARY, ev)

    def influx(self, ctx, t, closed):
        T = self.T
        w = self.w
        t0 = T['kick'] - 1.0
        if t < t0:
            return
        # depth of the influx over time: rises slowly, pauses at shut-in, then circulated out
        if t < T['shut']:
            d = 3000 - 900 * G.clamp((t - t0) / (T['shut'] - t0 + 2))
            size = 1.0 + 0.5 * G.clamp((t - t0) / 6)
            out = 0
        else:
            d_shut = 3000 - 900 * G.clamp((T['shut'] - t0) / (T['shut'] - t0 + 2))
            u = G.prog(t, T['circ'] - 0.2, 4.5, G.ease_in_out)
            d = d_shut - (d_shut - 330) * u
            size = 1.5 + 1.2 * u
            out = G.prog(t, T['circ'] + 4.0, 1.2)
        if out >= 1:
            return
        y = w.y(d)
        hw = w.hole_hw(max(d, 360)) - 12 if d > 350 else 14
        a = 1 - out
        for k in range(7):
            ph = k / 7 * math.tau
            x = w.cx + math.cos(ph + t) * hw * 0.7
            yy = y + math.sin(ph * 2 + t * 1.3) * 16 * size
            if d <= 340:
                # leaving through the choke line
                x = w.cx + 90
                yy = w.y(340) - 40 - out * 250 - k * 14
            G.circle(ctx, x, yy, 8 * size, fill=P.KICK, alpha=0.85 * a)

    def right_panel(self, ctx, t):
        T = self.T
        x0 = 960
        # pit gain
        pg = G.prog(t, T['pits'] - 0.4, 0.6) * (1 - G.prog(t, T['reads'] - 0.4, 0.5))
        if pg > 0:
            G.panel(ctx, x0, 180, 820, 560, pg)
            G.text(ctx, 'MUD PIT VOLUME', x0 + 410, 250, 30, 'ExtraBold', P.INK, 'center',
                   alpha=pg, tracking=0.08)
            lvl = 0.45 + 0.35 * G.prog(t, T['gain'] - 0.6, 2.0)
            tx, ty, tw, th = x0 + 90, 300, 300, 360
            G.rect(ctx, tx, ty, tw, th, stroke=P.INK, lw=5, alpha=pg)
            G.rect(ctx, tx + 4, ty + th * (1 - lvl), tw - 8, th * lvl - 4, fill=P.MUD, alpha=pg)
            G.line(ctx, [(tx - 10, ty + th * 0.55), (tx + tw + 10, ty + th * 0.55)], P.INK, 2, pg,
                   dash=[8, 6])
            gain = G.prog(t, T['gain'] - 0.4, 0.5)
            flash = 0.6 + 0.4 * math.sin(t * 10)
            G.arrow(ctx, tx + tw + 70, ty + th * 0.6, tx + tw + 70, ty + th * 0.2, P.KICK, 8, 24,
                    gain, pg)
            G.tag(ctx, 'PIT GAIN!', tx + tw + 110, ty + th * 0.3, gain * pg, bg=P.KICK, size=36,
                  alpha=flash)
            G.text(ctx, 'influx pushes mud out of the well', tx + tw + 110, ty + th * 0.3 + 70, 24,
                   'SemiBold', P.INK_SOFT, alpha=gain * pg)
        # shut-in gauges
        gp = G.prog(t, T['reads'] - 0.4, 0.6) * (1 - G.prog(t, T['control'] - 0.5, 0.5))
        if gp > 0:
            G.panel(ctx, x0, 180, 820, 560, gp)
            G.tag(ctx, 'WELL SHUT IN', x0 + 410, 250, gp, bg=P.BOP, col=P.INK, size=30,
                  align='center')
            rise = G.prog(t, T['reads'] - 0.2, 1.5)
            fall = G.prog(t, T['kill'] + 1.0, 4.0)
            W2.gauge(ctx, x0 + 230, 470, 120, (45 + 10 * math.sin(t * 2) * 0) * rise * (1 - 0.8 * fall),
                     100, 'DRILL PIPE', alpha=gp)
            W2.gauge(ctx, x0 + 590, 470, 120, 62 * rise * (1 - 0.8 * fall), 100, 'CASING', alpha=gp)
            kp = G.prog(t, T['kill'] - 0.3, 0.6)
            if kp > 0:
                G.rrect(ctx, x0 + 120, 640, 580, 70, 35)
                G.set_color(ctx, P.HEAVY_MUD, gp * kp)
                ctx.fill()
                G.text(ctx, 'pumping heavier kill mud', x0 + 410, 686, 30, 'Bold', P.WHITE, 'center',
                       alpha=gp * kp)
        cp = G.prog(t, T['control'] - 0.3, 0.6)
        if cp > 0:
            G.panel(ctx, x0, 300, 820, 300, cp)
            G.circle(ctx, x0 + 150, 450, 70 * G.ease_out_back(cp), fill=P.GOOD, alpha=cp)
            G.line(ctx, [(x0 + 118, 452), (x0 + 142, 478), (x0 + 186, 425)], P.WHITE, 12, cp)
            G.text(ctx, 'Under control', x0 + 260, 440, 54, 'ExtraBold', P.INK, alpha=cp)
            G.text(ctx, 'two barriers, always', x0 + 262, 500, 32, 'SemiBold', P.INK_SOFT,
                   alpha=G.prog(t, T['two'] - 0.2, 0.6))
        # title at the start
        tt = G.window(t, 0.2, T['pits'] - 0.4, 0.5)
        if tt > 0:
            G.text(ctx, 'WELL CONTROL', x0 + 410, 420, 64, 'ExtraBold', P.KICK, 'center', alpha=tt,
                   tracking=0.08)
            G.text(ctx, 'what happens when a kick occurs?', x0 + 410, 490, 32, 'SemiBold', P.INK_SOFT,
                   'center', alpha=tt)
