"""Scene 4 - Design: why casing, the telescope, and the three load cases."""
import math

import charts
import gfx as G
import palette as P
import well2d as W2
from scene_base import Scene

# 3D telescope proportions: (label, OD in, hole in, top z, shoe z)
TELE = [
    ('30" conductor', 30.0, 36.0, 0.0, -1.5),
    ('20" surface casing', 20.0, 26.0, 0.0, -3.4),
    ('13⅜" intermediate casing', 13.375, 17.5, 0.0, -5.3),
    ('9⅝" production casing', 9.625, 12.25, 0.0, -7.2),
    ('7" liner', 7.0, 8.5, -6.6, -9.0),
]
RK = 1.0 / 30.0      # radius units per inch of diameter
PIPE_X = 40.0        # location of the single-joint load-case model


class S(Scene):
    ID = 's04_casing'
    BLENDER = True
    PHASE = 0

    def __init__(self):
        super().__init__()
        tl = self.tl
        self.well = charts.schematic()
        self.chart = charts.WindowChart(self.well)
        self.T = dict(
            moves=tl.word('cs1', 'window moves'),
            need=tl.word('cs2', 'mud weight'),
            fracture=tl.word('cs2', 'fracture'),
            higher=tl.word('cs2', 'higher up'),
            seal=tl.word('cs3', 'seal off'),
            casing=tl.word('cs3', 'casing'),
            cemented=tl.word('cs3', 'cemented'),
            smaller=tl.word('cs3', 'smaller bit'),
            heavier=tl.word('cs3', 'heavier mud'),
            repeat=tl.t('cs4'),
            tele=tl.word('cs4', 'telescope'),
            c0=tl.word('cs5', 'thirty-inch'),
            c1=tl.word('cs5', 'twenty-inch'),
            c2=tl.word('cs5', 'Thirteen'),
            c3=tl.word('cs5', 'Nine'),
            c4=tl.word('cs5', 'seven-inch'),
            loads=tl.t('cs6'),
            burst=tl.word('cs6', 'Burst'),
            collapse=tl.word('cs6', 'Collapse'),
            tension=tl.word('cs6', 'tension'),
            tonnes=tl.word('cs6', 'hundreds of tonnes'),
        )
        T = self.T
        self.t3d = T['repeat'] - 0.6
        # casing steps in the 2D sequence
        s0 = T['seal'] - 0.2
        span = (T['heavier'] + 1.6 - s0)
        self.step_t = [s0 + span * i / 5 for i in range(5)]

    def render_ranges(self):
        import config as C
        return [(int(self.t3d * 24) - 2, self.nframes + C.HANDLE - 1)]

    # ------------------------------------------------------------------ 3D
    def build(self):
        import bl
        import equipment as E
        import models as MD
        T = self.T
        tl = self.tl
        F = lambda s: int(round(s * 24))  # noqa: E731
        steel, steel_cut = MD.steel_mats()
        steel = bl.mat('tele_steel', '#A9B8C7', rough=0.35, metal=0.15)
        cem, cem_cut = MD.cement_mats()
        a0, a1 = 0.0, 1.5 * math.pi       # remove the quadrant facing the camera
        A = {}
        land = [T['repeat'] + 0.9 + 1.0 * i for i in range(5)]
        for i, (lab, od, hole, top, shoe) in enumerate(TELE):
            r = od * RK / 1.0 * 0.5 * 2 / 2
            r = od * RK
            th = max(0.02, r * 0.09)
            cs = bl.annulus('tele_cs%d' % i, r - th, r, shoe, top, a0, a1, 96, steel, steel_cut)
            # collar ring at the top of each string for readability
            rh = hole * RK
            prev_shoe = TELE[i - 1][4] if i > 0 else top
            ctop = top if i < 2 else (prev_shoe + 0.7)
            parts = [bl.annulus('tele_cem%d' % i, r, rh, shoe, min(prev_shoe, top), a0, a1, 96,
                                cem, cem_cut)]
            if i > 0 and ctop > prev_shoe:
                pr = TELE[i - 1][1] * RK
                pth = max(0.02, pr * 0.09)
                parts.append(bl.annulus('tele_cem_ov%d' % i, r, pr - pth, prev_shoe, ctop, a0, a1,
                                        96, cem, cem_cut))
            for c in parts:
                bl.uv_cyl(c, 0.5)
            # animation: casing slides in from above, then cement rises from the shoe
            fl = F(land[i] - 0.7)
            bl.key(cs, 'location', max(0, fl - 18), (0, 0, 16.0))
            bl.key(cs, 'location', fl, (0, 0, 0.0))
            bl.show(cs, 0, False)
            bl.show(cs, max(0, fl - 18), True)
            for c in parts:
                MD.grow_up(c, fl + 2, fl + 16)
            A['shoe%d' % i] = (r * math.cos(1.5 * math.pi) + 0.0, -r - 0.02, shoe + 0.25)
            A['lab%d' % i] = (r * 0.72, -r * 0.72, shoe + 0.45)
        # HP wellhead housing on top
        wh = bl.revolve('tele_wh', [(0.30, 0.0), (0.42, 0.0), (0.42, 0.9), (0.36, 1.0), (0.30, 1.0)],
                        96, a0, a1, bl.mat('tele_wh', '#6F7C89', rough=0.3, metal=0.6), steel_cut)
        bl.pop_in(wh, F(T['c1'] + 0.3), 10)
        # -------------------------------------------------- single joint (load cases)
        pj = bl.empty('joint', (PIPE_X, 0, 0))
        R, Rin, L = 0.55, 0.47, 5.0
        body = bl.annulus('joint_body', Rin, R, -L / 2, L / 2, 0.0, 1.5 * math.pi, 96,
                          bl.mat('joint_steel', '#A9B8C7', rough=0.35, metal=0.15),
                          bl.mat('joint_cut', '#D7DFE7'))
        coup = bl.annulus('joint_coupling', Rin + 0.02, R + 0.1, L / 2 - 0.05, L / 2 + 0.55, 0.0,
                          1.5 * math.pi, 96, bl.mat('joint_coup', '#7F8FA0', rough=0.35, metal=0.15),
                          bl.mat('joint_cut', '#D7DFE7'))
        for o in (body, coup):
            o.location.x += PIPE_X
        bl.spin(body, F(T['loads'] - 1), F(tl.duration + 1), 0.08)
        bl.spin(coup, F(T['loads'] - 1), F(tl.duration + 1), 0.08)
        # camera
        cam = bl.Cam((9.0, -13.0, 1.5), (0, 0, -4.4), lens=35)
        cam.key(F(self.t3d), loc=(8.2, -12.6, 2.2), target=(0, 0, -4.6), lens=35)
        cam.key(F(T['c0'] - 0.6), loc=(9.0, -13.6, 1.0), target=(0, 0, -4.6), lens=35)
        cam.key(F(T['c0'] + 0.3), loc=(4.4, -6.2, 1.2), target=(0, 0, -1.2), lens=35)
        cam.key(F(T['c1'] + 0.3), loc=(4.6, -6.4, -0.6), target=(0, 0, -2.8), lens=35)
        cam.key(F(T['c2'] + 0.3), loc=(4.4, -6.2, -2.6), target=(0, 0, -4.6), lens=35)
        cam.key(F(T['c3'] + 0.3), loc=(4.2, -6.0, -4.6), target=(0, 0, -6.4), lens=35)
        cam.key(F(T['c4'] + 0.3), loc=(4.0, -5.8, -6.6), target=(0, 0, -8.2), lens=35)
        cam.key(F(T['c4'] + 2.0), loc=(8.5, -12.5, -1.0), target=(0, 0, -4.8), lens=35)
        cam.key(F(T['loads'] - 0.9), loc=(9.5, -14.0, 0.5), target=(0, 0, -4.6), lens=35)
        # cut to the single joint
        cam.key(F(T['loads'] - 0.8), loc=(PIPE_X + 4.2, -11.5, 3.0), target=(PIPE_X + 3.4, 0, 0.3), lens=30)
        cam.key(F(tl.duration + 0.6), loc=(PIPE_X + 5.6, -11.0, 2.2), target=(PIPE_X + 3.4, 0, 0.3), lens=30)

        for fc in bl._fcurves(cam.obj.animation_data.action) + bl._fcurves(
                cam.target.animation_data.action):
            for kp in fc.keyframe_points:
                if abs(kp.co[0] - F(T['loads'] - 0.9)) < 0.5:
                    kp.interpolation = 'CONSTANT'
        A.update({'j_burst': (PIPE_X + 0.3, -0.3, 0.4), 'j_coll': (PIPE_X + 0.95, -0.95, 0.8),
                  'j_top': (PIPE_X, 0, 4.2), 'j_bot': (PIPE_X, 0, -3.9)})
        return A

    # ------------------------------------------------------------------ 2D
    def draw(self, ctx, t, f, A):
        T = self.T
        fade2d = 1 - G.prog(t, self.t3d, 1.0)
        if fade2d > 0:
            self.draw_2d(ctx, t, fade2d)
        if t > self.t3d:
            self.draw_3d_labels(ctx, t, A)

    def draw_2d(self, ctx, t, a):
        T = self.T
        w = self.well
        c = self.chart
        ctx.save()
        # backdrop so the 2D fully covers the 3D layer during the handover
        ctx.push_group()
        G.bg_gradient(ctx)
        # schematic
        G.panel(ctx, w.x0 - 20, 150, w.x1 - w.x0 + 40, 870, 1.0, alpha=0.9)
        ctx.save()
        ctx.rectangle(w.x0, 160, w.x1 - w.x0, 850)
        ctx.clip()
        w.draw_earth(ctx, labels=True)
        steps = self.step_t
        ncas = sum(1 for s in steps if t >= s)
        # open hole drilled so far
        depth = 3450 if t < steps[0] else W2.CASINGS[min(4, ncas)][3] if ncas < 5 else 3430
        fb = 1 - G.prog(t, steps[0] - 0.4, 0.5)
        if fb > 0:
            ctx.rectangle(w.cx - 30, w.y(350), 60, w.y(3450) - w.y(350))
            G.set_color(ctx, P.MUD, fb)
            ctx.fill()
        if ncas > 0:
            w.fill_bore(ctx, 350, W2.CASINGS[min(4, ncas - 1)][3], P.MUD)
        for i in range(5):
            st = steps[i]
            p = G.prog(t, st, 0.9)
            if p > 0:
                w.cement(ctx, i, G.prog(t, st + 0.8, 0.8))
                w.casing(ctx, i, p)
        # crack at the weak zone
        ck = G.window(t, T['fracture'] - 0.2, T['seal'] + 0.3, 0.4)
        if ck > 0:
            y = w.y(1525)
            for s in (-1, 1):
                pts = [(w.cx + s * 30, y), (w.cx + s * 60, y - 12), (w.cx + s * 90, y + 8),
                       (w.cx + s * 125, y - 6), (w.cx + s * 160, y + 10)]
                G.line(ctx, pts, P.KICK, 5, ck, ck)
        ctx.restore()
        # chart
        c.axes(ctx, 1.0)
        c.window(ctx, 1.0)
        c.pore(ctx, 1.0)
        c.frac(ctx, 1.0)
        c.mud_line(ctx, 1.0 - G.prog(t, T['need'] - 0.5, 0.6), t)
        # window width markers ("the window moves")
        mv = G.window(t, T['moves'] - 0.3, T['need'] - 0.2, 0.4)
        if mv > 0:
            for k, dd in enumerate((700, 1900, 3050)):
                pk = G.prog(t, T['moves'] - 0.3 + 0.35 * k, 0.5)
                lo, hi = W2.interp(W2.PORE, dd), W2.interp(W2.FRAC, dd)
                x0, y = c.px(lo, dd)
                x1, _ = c.px(hi, dd)
                G.arrow(ctx, (x0 + x1) / 2, y, x0 + 4, y, P.INK, 4, 14, pk, mv)
                G.arrow(ctx, (x0 + x1) / 2, y, x1 - 4, y, P.INK, 4, 14, pk, mv)
        # single heavy mud line
        nl = G.window(t, T['need'] - 0.3, T['seal'] + 0.4, 0.4)
        if nl > 0:
            pts = [c.px(1.50, 3230), c.px(1.50, 350)]
            pl = G.prog(t, T['need'] - 0.3, 2.2)
            G.line(ctx, pts, P.HEAVY_MUD, 7, nl, pl)
            G.text(ctx, '1.50', pts[0][0] + 12, pts[0][1] - 10, 26, 'Bold', P.HEAVY_MUD, alpha=nl)
            xp = G.prog(t, T['fracture'] - 0.1, 0.5)
            if xp > 0:
                cx, cy = c.px(1.50, 1525)
                r = 22 * G.ease_out_back(xp)
                G.circle(ctx, cx, cy, r + 8, fill=P.WHITE, alpha=nl)
                G.line(ctx, [(cx - r * 0.6, cy - r * 0.6), (cx + r * 0.6, cy + r * 0.6)], P.KICK, 7, nl)
                G.line(ctx, [(cx - r * 0.6, cy + r * 0.6), (cx + r * 0.6, cy - r * 0.6)], P.KICK, 7, nl)
                G.label(ctx, cx, cy, cx + 60, cy - 90, 'Too heavy up here: fractures!',
                        G.prog(t, T['higher'] - 0.4, 0.8), col=P.WHITE, bg=P.KICK, size=24,
                        dot_col=P.KICK)
        # stair steps + shoes
        for i, st in enumerate(self.step_t):
            p = G.prog(t, st, 1.0)
            if p <= 0:
                continue
            d0, d1, sg = W2.MUD_STEPS[i]
            a0p, a1p = c.px(sg, d0), c.px(sg, d1)
            G.line(ctx, [a0p, a1p], P.MUD, 8, 1.0, p)
            if i > 0:
                prev = c.px(W2.MUD_STEPS[i - 1][2], d0)
                G.line(ctx, [prev, a0p], P.MUD, 3, 0.8, 1.0, dash=[6, 6])
            if p >= 1:
                sx, sy = c.px(sg, d1)
                G.poly(ctx, [(sx - 14, sy), (sx + 14, sy), (sx, sy - 18)], fill=P.INK)
                lab = W2.CASINGS[i][0].split(' ')[0]
                G.text(ctx, lab, sx + 20, sy - 2, 22, 'Bold', P.INK, alpha=G.prog(t, st + 0.9, 0.4))
        sp = G.window(t, T['seal'] - 0.2, 100, 0.5)
        if sp > 0:
            G.tag(ctx, 'CASING', 1290, 1045, sp, bg=P.STEEL_DARK, size=26, align='center')
            G.text(ctx, '= steel pipe, cemented in place', 1370, 1045, 24, 'SemiBold', P.INK_SOFT,
                   valign='middle', alpha=sp)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(a)
        ctx.restore()

    def draw_3d_labels(self, ctx, t, A):
        T = self.T
        a = self.A
        out = G.prog(t, T['loads'] - 1.2, 0.5)
        tp = G.window(t, T['tele'] - 0.2, T['c0'] - 0.4, 0.5)
        if tp > 0:
            G.tag(ctx, 'THE TELESCOPE', 520, 160, tp, bg=P.INK, size=40, align='center')
        for i in range(5):
            p = G.prog(t, T['c%d' % i] - 0.1, 0.9)
            pt = a(A, 'lab%d' % i)
            if pt and p > 0:
                lab = TELE[i][0]
                side = -1 if i % 2 else 1
                G.label(ctx, pt[0], pt[1], pt[0] + side * 260, pt[1] - 40, lab, p,
                        align='left' if side > 0 else 'right', size=30, out=out)
        # load cases as 2D cards
        self.load_cards(ctx, t)
        tn = G.prog(t, T['tonnes'] - 0.2, 0.8)
        if tn > 0:
            G.text(ctx, '≈ 250–300 t', 1580, 990, 44, 'ExtraBold', '#2FAF5B', 'center', alpha=tn)

    def load_cards(self, ctx, t):
        T = self.T
        x0, y0, w, h, gap = 880, 170, 290, 330, 30
        items = [('burst', 'BURST', 'pressure inside', '#E0342F'),
                 ('collapse', 'COLLAPSE', 'pressure outside', '#1F7CE0'),
                 ('tension', 'TENSION', 'its own weight', '#2FAF5B')]
        for i, (k, title, sub, col) in enumerate(items):
            p = G.prog(t, T[k] - 0.2, 0.7)
            if p <= 0:
                continue
            x = x0 + i * (w + gap)
            G.panel(ctx, x, y0, w, h + 190, p)
            a = G.clamp(p * 1.5)
            cx, cy = x + w / 2, y0 + 170
            if k in ('burst', 'collapse'):
                G.circle(ctx, cx, cy, 80, fill='#A9B8C7', alpha=a)
                G.circle(ctx, cx, cy, 62, fill='#F4F7FA', alpha=a)
                G.circle(ctx, cx, cy, 80, stroke='#5E6B78', lw=3, alpha=a)
                G.circle(ctx, cx, cy, 62, stroke='#5E6B78', lw=3, alpha=a)
                pul = 0.5 + 0.5 * math.sin(t * 5)
                for j in range(8):
                    ang = j * math.tau / 8
                    c, s_ = math.cos(ang), math.sin(ang)
                    if k == 'burst':
                        r0, r1 = 18, 56 + 4 * pul
                    else:
                        r0, r1 = 140 + 4 * pul, 88
                    G.arrow(ctx, cx + c * r0, cy + s_ * r0, cx + c * r1, cy + s_ * r1, col, 6, 16,
                            G.prog(t, T[k] + 0.1 + 0.03 * j, 0.5), a)
            else:
                G.rect(ctx, cx - 40, cy - 95, 80, 190, fill='#A9B8C7', stroke='#5E6B78', lw=3,
                       alpha=a)
                G.rect(ctx, cx - 48, cy - 110, 96, 30, fill='#6D7D8D', alpha=a)
                pe = G.prog(t, T[k] + 0.1, 0.6)
                G.arrow(ctx, cx, cy - 115, cx, cy - 165, col, 8, 22, pe, a)
                G.arrow(ctx, cx, cy + 100, cx, cy + 150, col, 8, 22, pe, a)
            G.text(ctx, title, cx, y0 + h + 40, 36, 'ExtraBold', col, 'center', alpha=a,
                   tracking=0.06)
            G.text(ctx, sub, cx, y0 + h + 85, 26, 'SemiBold', P.INK_SOFT, 'center', alpha=a)
