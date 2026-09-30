"""Scene 3 - Design: pore pressure, kicks, P = rho g h, fracture pressure, the window."""
import math
import random

import charts
import gfx as G
import palette as P
import well2d as W2
from scene_base import Scene


def piano(ctx, x, y, s=1.0, alpha=1.0):
    """Stylised grand piano (side view) with its lid open, feet at (x, y)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    dark = '#1E2329'
    # legs
    for lx in (-95, 70):
        G.poly(ctx, [(lx, 0), (lx + 14, 0), (lx + 16, -70), (lx - 2, -70)], fill=dark, alpha=alpha)
    # case
    G.rrect(ctx, -120, -120, 240, 52, 10)
    G.set_color(ctx, dark, alpha)
    ctx.fill()
    # keyboard
    G.rect(ctx, -140, -92, 40, 18, fill='#F4F4F4', alpha=alpha)
    for i in range(5):
        G.rect(ctx, -138 + i * 8, -92, 4, 10, fill=dark, alpha=alpha)
    # lid (propped open)
    G.poly(ctx, [(-110, -120), (118, -120), (40, -205)], fill='#2C333B', alpha=alpha)
    G.line(ctx, [(-10, -120), (20, -175)], '#8A939C', 3, alpha)
    ctx.restore()


def fingertip(ctx, x, y, s=1.0, alpha=1.0):
    """Upward-pointing fingertip whose tip is at (x, y)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    G.rrect(ctx, -26, 0, 52, 170, 26)
    G.set_color(ctx, '#F1C7A6', alpha)
    ctx.fill()
    G.rrect(ctx, -16, 8, 32, 40, 14)
    G.set_color(ctx, '#F9E1D0', alpha)
    ctx.fill()
    G.line(ctx, [(-18, 95), (18, 95)], '#D9A887', 3, alpha)
    G.line(ctx, [(-14, 105), (14, 105)], '#D9A887', 3, alpha)
    ctx.restore()


class S(Scene):
    ID = 's03_pressure'
    PHASE = 0
    TRACKER_IN = 0.4

    def __init__(self):
        super().__init__()
        self.well = charts.schematic()
        self.chart = charts.WindowChart(self.well)
        tl = self.tl
        self.T = dict(
            card_out=3.4,
            bp_in=3.6,
            pressure=tl.word('pr1', 'pressure'),
            rock_in=tl.t('pr2') - 0.2,
            pore=tl.word('pr2', 'pore pressure'),
            falls=tl.word('pr3', 'falls'),
            pushing=tl.word('pr3', 'pushing'),
            kick=tl.word('pr3', 'kick'),
            blowout=tl.word('pr3', 'blowout'),
            mud_in=tl.t('pr4', 0.05),
            density=tl.word('pr4', 'density'),
            gravity=tl.word('pr4', 'gravity'),
            height=tl.word('pr4', 'height'),
            eq_in=tl.word('pr4', 'pressure at'),
            onehalf=tl.word('pr5', 'one and a half'),
            three=tl.word('pr5', 'three thousand'),
            bar=tl.word('pr5', 'four hundred'),
            piano=tl.word('pr5', 'grand piano'),
            heavy=tl.word('pr6', 'heavy as possible'),
            crack=tl.word('pr6', 'crack'),
            fracture=tl.word('pr6', 'fracture pressure'),
            pours=tl.word('pr6', 'mud pours'),
            kick2=tl.word('pr6', 'kick of its own'),
            window=tl.t('pr7'),
            above=tl.word('pr7', 'above the pore'),
            below=tl.word('pr7', 'below the fracture'),
            plot=tl.t('pr8'),
            title=tl.word('pr8', 'the drilling window'),
        )
        rnd = random.Random(3)
        self.bubbles = [(rnd.uniform(-0.8, 0.8), rnd.uniform(0, 1), rnd.uniform(0.7, 1.3),
                         rnd.uniform(5, 11)) for _ in range(40)]
        self.cracks = self._make_cracks()

    def _make_cracks(self):
        rnd = random.Random(7)
        out = []
        for side in (-1, 1):
            for d0 in (1400, 1520, 1650):
                pts = [(0, d0)]
                x, d = 0, d0
                for _ in range(9):
                    x += rnd.uniform(14, 26)
                    d += rnd.uniform(-35, 35)
                    pts.append((x, d))
                out.append((side, pts))
        return out

    # ------------------------------------------------------------------ helpers
    def bore_hw(self):
        return 30

    def draw_bore(self, ctx, t, fluid_col, level_d=350, alpha=1.0):
        w = self.well
        hw = self.bore_hw()
        top = w.y(350)
        bot = w.y(3450)
        # dark bore background (empty hole wall)
        G.rect(ctx, w.cx - hw, top, 2 * hw, bot - top, fill='#3B4652', alpha=alpha)
        yl = w.y(level_d)
        G.rect(ctx, w.cx - hw, yl, 2 * hw, bot - yl, fill=fluid_col, alpha=alpha)
        # subtle highlight
        G.rect(ctx, w.cx - hw + 6, yl, 6, bot - yl, fill='#FFFFFF', alpha=alpha * 0.12)
        G.line(ctx, [(w.cx - hw, top), (w.cx - hw, bot)], '#2A3440', 2, alpha)
        G.line(ctx, [(w.cx + hw, top), (w.cx + hw, bot)], '#2A3440', 2, alpha)

    def pore_arrows(self, ctx, t, alpha, strength=1.0):
        if alpha <= 0:
            return
        w = self.well
        for d in (1300, 2200, 3000, 3380):
            y = w.y(d)
            pulse = 0.5 + 0.5 * math.sin(t * 4 + d)
            L = (70 + 20 * pulse) * strength
            for s in (-1, 1):
                x1 = w.cx + s * (self.bore_hw() + 8)
                G.arrow(ctx, x1 + s * L, y, x1, y, P.PRIMARY, 6, 18, 1.0, alpha)

    def bubbles_draw(self, ctx, t, t0, speed, alpha, reach=1.0, n=40):
        w = self.well
        hw = self.bore_hw()
        bot = w.y(3440)
        top = w.y(350) + (1 - reach) * (bot - w.y(350))
        for (xo, ph, sp, r) in self.bubbles[:n]:
            life = (t - t0) * speed * sp - ph * 0.8
            if life < 0:
                continue
            y = bot - life * 160
            if y < top - 40:
                continue
            grow = 1 + (bot - y) / 500
            x = w.cx + xo * (hw - r * grow * 0.6)
            G.circle(ctx, x, y, r * grow * 0.7, fill=P.KICK, alpha=alpha * 0.85)
            G.circle(ctx, x - r * 0.25, y - r * 0.25, r * 0.25, fill='#FFFFFF', alpha=alpha * 0.5)

    # ------------------------------------------------------------------ draw
    def draw(self, ctx, t, f, A):
        T = self.T
        w = self.well
        # ---- chapter card + PRESSURE hero
        G.chapter_title(ctx, 1, 'Design', t, 0.3, T['card_out'], sub='Everything starts on paper')
        bpa = G.window(t, T['bp_in'], T['rock_in'], 0.5)
        if bpa > 0:
            dim = 1 - 0.6 * G.prog(t, T['pressure'] - 0.5, 0.6)
            self.blueprint(ctx, t, bpa * dim)
        ph = G.window(t, T['pressure'] - 0.5, T['rock_in'], 0.4)
        if ph > 0:
            v = 0.35 + 0.5 * G.prog(t, T['pressure'] - 0.4, 1.5) + 0.03 * math.sin(t * 9)
            G.circle(ctx, 960, 520, 260 * G.ease_out(ph), fill=P.WHITE, alpha=ph * 0.9)
            W2.gauge(ctx, 960, 470, 150 * G.ease_out_back(ph), v * 100, 100, alpha=ph)
            G.text(ctx, 'PRESSURE', 960, 700, 72, 'ExtraBold', P.INK, 'center', alpha=ph,
                   tracking=0.08)
        if t < T['rock_in']:
            return
        # ---- schematic
        shake = 0
        if T['blowout'] - 0.2 < t < T['blowout'] + 1.8:
            k = 1 - G.clamp((t - T['blowout']) / 2.0)
            shake = 5 * k
        ctx.save()
        ctx.translate(shake * math.sin(t * 60), shake * math.cos(t * 47))
        pin = G.prog(t, T['rock_in'], 1.0, G.ease_out)
        ctx.save()
        clip_h = (w.y(3700) - 150) * pin
        ctx.rectangle(0, 150, 1920, clip_h)
        ctx.clip()
        G.panel(ctx, w.x0 - 20, 150, w.x1 - w.x0 + 40, 870, 1.0, alpha=0.9)
        ctx.rectangle(w.x0, 160, w.x1 - w.x0, 850)
        ctx.clip()
        w.draw_earth(ctx, labels=True)
        # fluid state over time
        mud_p = G.prog(t, T['mud_in'], 2.5)
        heavy_p = G.prog(t, T['heavy'], 1.5) * (1 - G.prog(t, T['window'], 1.5))
        fluid = G.mix(P.SEAWATER, P.MUD, mud_p)
        fluid = G.mix(fluid, P.HEAVY_MUD, heavy_p)
        level = 350
        # losses: level drops
        loss_p = G.prog(t, T['pours'], 3.0) * (1 - G.prog(t, T['window'], 1.5))
        level = 350 + 700 * loss_p
        if t < T['mud_in'] + 2.5:
            # mud rises from the bottom as it replaces seawater
            fill_level = 3450 - (3450 - 350) * mud_p
            self.draw_bore(ctx, t, P.SEAWATER, 350)
            if mud_p > 0:
                hw = self.bore_hw()
                G.rect(ctx, w.cx - hw, w.y(fill_level), 2 * hw, w.y(3450) - w.y(fill_level),
                       fill=P.MUD)
        else:
            self.draw_bore(ctx, t, fluid, level)
        # fractures + losses into them
        cr = G.prog(t, T['crack'], 1.4) * (1 - G.prog(t, T['window'], 1.2))
        if cr > 0:
            for side, pts in self.cracks:
                pp = [(w.cx + side * (self.bore_hw() + x), w.y(d)) for x, d in pts]
                G.line(ctx, pp, '#2A2016', 4, 1.0, cr)
                G.line(ctx, pp, P.HEAVY_MUD, 2.5, 1.0, G.prog(t, T['pours'] - 0.5, 2.5) * cr)
                G.arrow(ctx, w.cx + side * (self.bore_hw() - 6), pp[0][1],
                        w.cx + side * (self.bore_hw() + 70), pp[0][1] + 20, P.HEAVY_MUD, 5, 14,
                        G.prog(t, T['pours'] - 0.8, 1.0) * cr, cr)
        # pore pressure arrows
        pa = G.prog(t, T['pore'] - 0.3, 0.8) * (1 - G.prog(t, T['window'], 1.0))
        strength = 1.0 + 0.5 * G.prog(t, T['falls'], 1.0) * (1 - G.prog(t, T['mud_in'], 1.0))
        self.pore_arrows(ctx, t, pa, strength)
        # kick bubbles (first kick) and blowout
        kb = G.prog(t, T['pushing'] - 0.3, 0.6) * (1 - G.prog(t, T['mud_in'] + 0.3, 1.2))
        if kb > 0:
            speed = 1.0 + 1.8 * G.prog(t, T['blowout'] - 0.8, 1.0)
            self.bubbles_draw(ctx, t, T['pushing'] - 0.3, speed, kb)
        kb2 = G.window(t, T['kick2'] - 0.2, T['window'] - 0.2, 0.5)
        if kb2 > 0:
            self.bubbles_draw(ctx, t, T['kick2'] - 0.2, 0.8, kb2, n=10)
        ctx.restore()
        # labels on schematic (outside clip)
        yb = w.y(3380)
        G.label(ctx, w.cx - 110, w.y(1300), w.cx - 90, w.y(1300) - 70, 'Pore pressure',
                G.prog(t, T['pore'], 1.0), col=P.WHITE, bg=P.PRIMARY, size=26,
                out=G.prog(t, T['mud_in'], 0.6), align='left', elbow=False)
        G.tag(ctx, 'KICK!', w.cx - 60, yb - 70, G.prog(t, T['kick'], 0.5) *
              (1 - G.prog(t, T['mud_in'], 0.5)), bg=P.KICK, size=30, align='right')
        if T['blowout'] - 0.1 < t < T['mud_in']:
            bl = G.window(t, T['blowout'] - 0.1, T['mud_in'], 0.3)
            flash = 0.6 + 0.4 * math.sin((t - T['blowout']) * 14)
            G.tag(ctx, '⚠ BLOWOUT', w.cx, w.y(350) - 40, bl, bg=P.KICK, size=34, align='center',
                  alpha=flash)
        G.tag(ctx, 'LOSSES', w.cx + 90, w.y(1600) + 70, G.prog(t, T['pours'], 0.5) *
              (1 - G.prog(t, T['window'], 0.5)), bg=P.HEAVY_MUD, size=28)
        G.tag(ctx, 'KICK!', w.cx - 60, yb - 70, G.window(t, T['kick2'], T['window'] - 0.3, 0.4),
              bg=P.KICK, size=30, align='right')
        # height dimension for rho g h
        hd = G.prog(t, T['height'] - 0.2, 0.8) * (1 - G.prog(t, T['heavy'], 0.6))
        if hd > 0:
            x = w.x0 + 36
            G.arrow(ctx, x, w.y(1900), x, w.y(350), P.INK, 4, 16, hd, hd)
            G.arrow(ctx, x, w.y(1900), x, w.y(3450), P.INK, 4, 16, hd, hd)
            G.circle(ctx, x, w.y(1900), 26, fill=P.WHITE, alpha=hd)
            G.text(ctx, 'h', x, w.y(1900), 36, 'Regular', P.INK, 'center', 'middle', alpha=hd,
                   family='Noto Serif', italic=True)
        ctx.restore()

        # ---- pore pressure explanation + kick condition (pr2 - pr3)
        cp1 = G.window(t, T['pore'] - 0.2, T['eq_in'] - 0.6, 0.6)
        if cp1 > 0:
            self.card_kick(ctx, t, cp1)
        # ---- equation panel (pr4 - pr6)
        ep = G.prog(t, T['eq_in'] - 0.4, 0.8) * (1 - G.prog(t, T['heavy'] - 0.3, 0.8))
        if ep > 0:
            self.draw_equation(ctx, t, ep)
        # ---- fracture pressure label
        fl = G.prog(t, T['fracture'], 0.8) * (1 - G.prog(t, T['window'], 0.6))
        G.label(ctx, w.cx - 80, w.y(1520), w.cx - 60, w.y(1150), 'Fracture pressure', fl,
                col=P.WHITE, bg=P.SECONDARY, size=26, elbow=False, align='right')
        hv = G.window(t, T['heavy'], T['window'] - 0.5, 0.5)
        if hv > 0:
            self.card_losses(ctx, t, hv)
        # ---- chart
        cp = G.prog(t, T['window'] - 0.3, 1.2)
        if cp > 0:
            self.draw_chart(ctx, t, cp)

    def blueprint(self, ctx, t, a):
        T = self.T
        x0, y0, w, h = 560, 150, 800, 860
        G.shadow_rrect(ctx, x0, y0, w, h, 18, alpha=0.3 * a)
        G.rrect(ctx, x0, y0, w, h, 18)
        G.set_color(ctx, '#0F3B63', a)
        ctx.fill()
        for gx in range(x0 + 40, x0 + w, 40):
            G.line(ctx, [(gx, y0 + 10), (gx, y0 + h - 10)], '#FFFFFF', 1, a * 0.07)
        for gy in range(y0 + 40, y0 + h, 40):
            G.line(ctx, [(x0 + 10, gy), (x0 + w - 10, gy)], '#FFFFFF', 1, a * 0.07)
        cx = x0 + 330
        ytop = y0 + 90

        def Y(d):
            return ytop + (d - 350) / 3100 * (h - 190)
        wht = '#EAF4FF'
        for i, (lab, od, hole, shoe, top) in enumerate(W2.CASINGS):
            p = G.prog(t, T['bp_in'] + 0.3 + i * 0.75, 1.1)
            if p <= 0:
                continue
            hw = od * 2.6
            for sgn in (-1, 1):
                G.line(ctx, [(cx + sgn * hw, Y(top)), (cx + sgn * hw, Y(shoe))], wht, 3.5, a, p)
                hh = hole * 2.6
                G.line(ctx, [(cx + sgn * hh, Y(max(top, W2.CASINGS[i - 1][3] if i else top))),
                             (cx + sgn * hh, Y(shoe))], wht, 1.2, a * 0.5, p, dash=[6, 6])
            if p >= 1:
                yb = Y(shoe)
                for sgn in (-1, 1):
                    G.poly(ctx, [(cx + sgn * hw, yb), (cx + sgn * (hw + 10), yb),
                                 (cx + sgn * hw, yb - 12)], fill=wht, alpha=a)
                lp = G.prog(t, T['bp_in'] + 0.9 + i * 0.75, 0.6)
                G.line(ctx, [(cx + hw + 14, yb - 6), (x0 + 540, yb - 6)], wht, 1.2, a * lp * 0.7)
                G.text(ctx, lab.replace(' casing', ''), x0 + 550, yb - 1, 24, 'SemiBold', wht,
                       alpha=a * lp)
        dp = G.prog(t, T['bp_in'] + 1.0, 2.5)
        G.arrow(ctx, x0 + 60, Y(350), x0 + 60, Y(3430), wht, 2, 12, dp, a)
        G.arrow(ctx, x0 + 60, Y(3430), x0 + 60, Y(350), wht, 2, 12, dp, a)
        if dp > 0.9:
            ctx.save()
            ctx.translate(x0 + 48, (Y(350) + Y(3430)) / 2)
            ctx.rotate(-math.pi / 2)
            G.text(ctx, '3,080 m below seabed', 0, 0, 20, 'SemiBold', wht, 'center', alpha=a)
            ctx.restore()
        tb = G.prog(t, T['bp_in'] + 2.5, 0.8)
        if tb > 0:
            bx, by = x0 + 110, y0 + h - 120
            G.rect(ctx, bx, by, 270, 90, stroke=wht, lw=1.5, alpha=a * tb)
            G.line(ctx, [(bx, by + 36), (bx + 270, by + 36)], wht, 1.2, a * tb)
            G.text(ctx, 'SUBSEA WELL · NCS', bx + 14, by + 26, 18, 'Bold', wht, alpha=a * tb,
                   tracking=0.06)
            G.text(ctx, 'Casing design  ·  rev. B', bx + 14, by + 68, 18, 'Medium', wht,
                   alpha=a * tb)

    def card_kick(self, ctx, t, a):
        T = self.T
        x0, y0 = 790, 200
        G.panel(ctx, x0, y0, 980, 780, a, alpha=0.93)
        cx = x0 + 490
        G.text(ctx, 'Fluid trapped in the pores is under pressure', cx, y0 + 80, 30, 'Bold',
               P.INK_SOFT, 'center', alpha=a)
        G.pore_inset(ctx, cx, y0 + 290, 165, fluid='#5AA9E6', alpha=a)
        # pressure arrows around the inset
        for k in range(8):
            ang = k * math.tau / 8 + 0.3
            pul = 0.5 + 0.5 * math.sin(t * 5 + k)
            r0, r1 = 180, 215 + 12 * pul
            G.arrow(ctx, cx + r0 * math.cos(ang), y0 + 290 + r0 * math.sin(ang),
                    cx + r1 * math.cos(ang), y0 + 290 + r1 * math.sin(ang), P.PRIMARY, 5, 14,
                    1.0, a)
        pk = G.prog(t, T['falls'], 0.7)
        if pk > 0:
            yy = y0 + 580
            G.rich(ctx, [('P', 'math'), ('well', 'sub'), ('  <  ', 'mathup'), ('P', 'math'),
                         ('pore', 'sub')], cx - 120, yy, 76, align='center', alpha=a * pk)
            G.arrow(ctx, cx + 110, yy - 24, cx + 200, yy - 24, P.INK, 5, 18, pk, a)
            G.tag(ctx, 'KICK', cx + 220, yy - 26, G.prog(t, T['kick'], 0.5), bg=P.KICK, size=40)
        pb = G.prog(t, T['blowout'] - 0.2, 0.6)
        if pb > 0:
            G.text(ctx, 'uncontrolled kick  =  blowout', cx, y0 + 700, 38, 'ExtraBold', P.KICK,
                   'center', alpha=a * pb)

    def card_losses(self, ctx, t, a):
        T = self.T
        x0, y0 = 790, 200
        G.panel(ctx, x0, y0, 980, 780, a, alpha=0.93)
        cx = x0 + 490
        G.text(ctx, 'Heavier mud...', cx, y0 + 150, 72, 'ExtraBold', P.HEAVY_MUD, 'center',
               alpha=a)
        G.text(ctx, '...pushes harder on the rock', cx, y0 + 230, 40, 'SemiBold', P.INK_SOFT,
               'center', alpha=a * G.prog(t, T['heavy'] + 0.6, 0.6))
        pf = G.prog(t, T['fracture'], 0.7)
        if pf > 0:
            yy = y0 + 420
            G.rich(ctx, [('P', 'math'), ('well', 'sub'), ('  >  ', 'mathup'), ('P', 'math'),
                         ('frac', 'sub')], cx - 130, yy, 76, align='center', alpha=a * pf)
            G.arrow(ctx, cx + 110, yy - 24, cx + 200, yy - 24, P.INK, 5, 18, pf, a)
            G.tag(ctx, 'LOSSES', cx + 220, yy - 26, G.prog(t, T['pours'], 0.5), bg=P.HEAVY_MUD,
                  size=40)
        pk = G.prog(t, T['kick2'] - 0.2, 0.6)
        if pk > 0:
            G.text(ctx, 'level drops  →  pressure drops  →  kick!', cx, y0 + 600, 36, 'Bold',
                   P.KICK, 'center', alpha=a * pk)

    def draw_equation(self, ctx, t, ep):
        T = self.T
        x0, y0 = 790, 170
        G.panel(ctx, x0, y0, 980, 830, ep, alpha=0.93)
        a = ep
        cx = x0 + 490
        G.text(ctx, 'Pressure at the bottom of a fluid column', cx, y0 + 70, 30, 'Bold',
               P.INK_SOFT, 'center', alpha=a)
        size = 120
        parts = [('P', 'math'), ('  =  ', 'mathup'), ('ρ', 'math'), ('  ·  ', 'mathup'),
                 ('g', 'math'), ('  ·  ', 'mathup'), ('h', 'math')]
        widths = [G.text_w(ctx, s, size, 'Regular', 'Noto Serif', st == 'math') for s, st in parts]
        xs = cx - sum(widths) / 2
        centers = []
        for (s_, st), wd in zip(parts, widths):
            G.text(ctx, s_, xs, y0 + 215, size, 'Regular', P.INK, family='Noto Serif',
                   italic=(st == 'math'), alpha=a)
            centers.append(xs + wd / 2)
            xs += wd
        for key, idx, lab, col in (('density', 2, 'density', P.MUD),
                                    ('gravity', 4, 'gravity', P.ACCENT),
                                    ('height', 6, 'height', P.PRIMARY)):
            p = G.prog(t, T[key] - 0.1, 0.5)
            if p > 0:
                G.circle(ctx, centers[idx], y0 + 178, 64 * G.ease_out_back(p), stroke=col, lw=5,
                         alpha=a * p)
                G.text(ctx, lab, centers[idx], y0 + 295, 30, 'Bold', col, 'center', alpha=a * p)
        n1 = G.prog(t, T['onehalf'], 0.6)
        n2 = G.prog(t, T['three'], 0.6)
        n3 = G.prog(t, T['bar'] - 0.2, 0.6)
        yy = y0 + 380
        if n1 > 0:
            G.rich(ctx, [('ρ', 'math'), (' = 1.5 × water = 1500 kg/m³', 'normal')], x0 + 80, yy,
                   34, alpha=a * n1)
        if n2 > 0:
            G.rich(ctx, [('g', 'math'), (' = 9.81 m/s²     ', 'normal'), ('h', 'math'),
                         (' = 3000 m', 'normal')], x0 + 80, yy + 55, 34, alpha=a * n2)
        if n3 > 0:
            G.rrect(ctx, x0 + 70, yy + 90, 560, 88, 18)
            G.set_color(ctx, P.INK, a * n3)
            ctx.fill()
            G.rich(ctx, [('P', 'math'), (' ≈ 44 MPa ≈ 440 bar', 'bold')], x0 + 350, yy + 150,
                   44, col=P.WHITE, align='center', alpha=a * n3)
        pp = G.prog(t, T['piano'] - 0.3, 0.8)
        if pp > 0:
            fx, fy = x0 + 800, y0 + 640
            drop = (1 - G.ease_out(pp)) * -80
            fingertip(ctx, fx, fy, 0.8, alpha=a * pp)
            piano(ctx, fx, fy + 68 * 0.8 + drop, 0.8, alpha=a * pp)
            G.text(ctx, 'a grand piano', x0 + 80, y0 + 690, 44, 'ExtraBold', P.INK, alpha=a * pp)
            G.text(ctx, 'on your fingertip:', x0 + 80, y0 + 740, 34, 'SemiBold', P.INK_SOFT,
                   alpha=a * pp)
            G.text(ctx, '≈ 450 kg per cm²', x0 + 80, y0 + 790, 34, 'Bold', P.MUD, alpha=a * pp)

    def draw_chart(self, ctx, t, cp):
        T = self.T
        c = self.chart
        c.axes(ctx, cp)
        pp = G.prog(t, T['above'] - 0.4, 1.4)
        fp = G.prog(t, T['below'] - 0.4, 1.4)
        c.kick_zone(ctx, G.prog(t, T['plot'] + 1.5, 1.0))
        c.loss_zone(ctx, G.prog(t, T['plot'] + 1.5, 1.0))
        c.window(ctx, G.prog(t, T['below'] + 0.8, 1.6))
        c.pore(ctx, pp)
        c.frac(ctx, fp)
        c.mud_line(ctx, G.prog(t, T['plot'] + 0.2, 2.0), t)
        # curve labels
        y = self.well.y(1900)
        x_p, _ = c.px(W2.interp(W2.PORE, 1900), 1900)
        x_f, _ = c.px(W2.interp(W2.FRAC, 1900), 1900)
        G.label(ctx, x_p, y, x_p - 60, y + 120, 'Pore pressure', G.prog(t, T['above'] + 0.4, 1.0),
                col=P.WHITE, bg=P.PRIMARY, size=24, align='right')
        G.label(ctx, x_f, self.well.y(1500), x_f + 60, self.well.y(1500) - 80, 'Fracture pressure',
                G.prog(t, T['below'] + 0.4, 1.0), col=P.WHITE, bg=P.SECONDARY, size=24,
                align='left')
        g = G.prog(t, T['plot'] + 1.5, 1.0)
        x_k, _ = c.px(1.05, 2900)
        G.text(ctx, 'KICK', x_k + 8, self.well.y(2950), 26, 'ExtraBold', P.KICK, alpha=g * 0.8,
               tracking=0.1)
        x_l, _ = c.px(1.93, 800)
        G.text(ctx, 'LOSSES', x_l, self.well.y(1000), 26, 'ExtraBold', P.HEAVY_MUD, 'right',
               alpha=g * 0.8, tracking=0.1)
        x_m, _ = c.px(1.55, 2700)
        G.text(ctx, 'mud', x_m - 20, self.well.y(2700), 26, 'Bold', P.MUD, 'center',
               alpha=G.prog(t, T['plot'] + 1.2, 0.8))
        tp = G.prog(t, T['title'] - 0.2, 0.8)
        if tp > 0:
            cx = (c.x0 + c.x1) / 2
            y0 = self.well.y(3450) - 110
            G.tag(ctx, 'THE DRILLING WINDOW', cx + 40, y0, tp, bg=P.GOOD, size=34,
                  align='center')
