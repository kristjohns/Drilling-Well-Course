"""Scene 9 - Drilling: the mud circulation loop, the PDC bit, MWD and steering."""
import math
import random

import gfx as G
import overlays as O
import palette as P
from scene_base import Scene

WX = 760            # well centre x in the 2D loop diagram
Y_DECK, Y_SEA, Y_BED, Y_SHOE, Y_BIT = 262, 300, 540, 820, 985
BIT_X = 200.0       # location of the bit product shot in 3D
DIO_X = 0.0


def _poly_len(pts):
    return sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:]))


def _at(pts, u):
    return G.point_at(pts, u)


SUPPLY = [(1310, 250), (1440, 250), (1500, 250), (1500, 110), (800, 110), (780, 130), (WX, 160),
          (WX, Y_BIT - 20)]
RET_L = [(WX - 3, Y_BIT - 6), (WX - 24, Y_BIT - 20), (WX - 24, Y_BED - 10), (WX - 14, Y_BED - 70),
         (WX - 14, Y_DECK + 8), (WX - 40, Y_DECK + 8), (610, 214), (540, 232), (470, 246),
         (460, 262), (520, 290), (1220, 290), (1310, 250)]
RET_R = [(WX + 3, Y_BIT - 6), (WX + 24, Y_BIT - 20), (WX + 24, Y_BED - 10), (WX + 14, Y_BED - 70),
         (WX + 14, Y_DECK + 8), (WX - 40, Y_DECK + 8)]


class S(Scene):
    ID = 's09_circulation'
    BLENDER = True
    PHASE = 1

    def __init__(self):
        super().__init__()
        tl = self.tl
        self.T = dict(
            star=tl.word('mc1', 'star of the show'),
            pumps=tl.word('mc2', 'pumps'),
            inside=tl.word('mc2', 'inside of the drill string'),
            nozzles=tl.word('mc2', 'nozzles'),
            cooling=tl.word('mc2', 'cooling'),
            flushing=tl.word('mc2', 'flushing'),
            cuttings=tl.word('mc3', 'cuttings'),
            annulus=tl.word('mc3', 'annulus'),
            gap=tl.word('mc3', 'the gap'),
            riser=tl.word('mc3', 'riser'),
            shakers=tl.word('mc4', 'shale shakers'),
            pits=tl.word('mc4', 'pits'),
            again=tl.word('mc4', 'round again'),
            pdc=tl.t('mc5'),
            diamond=tl.word('mc5', 'synthetic diamond'),
            plane=tl.word('mc5', 'plane shaving'),
            sensors=tl.word('mc6', 'sensors'),
            direction=tl.word('mc6', 'direction'),
            pulses=tl.word('mc6', 'pressure pulses'),
            rss=tl.word('mc7', 'rotary steerable'),
            bend=tl.word('mc7', 'bend the well'),
            target=tl.word('mc7', 'target'),
        )
        T = self.T
        self.t_bit0 = tl.t('mc5') - 0.5
        self.t_bit1 = tl.t('mc6') - 0.5
        self.t_dio0 = tl.t('mc7') - 0.5
        rnd = random.Random(9)
        self.chips = [(rnd.uniform(0, 1), rnd.choice((-1, 1)), rnd.uniform(3, 6)) for _ in range(40)]

    def render_ranges(self):
        import config as C
        F = lambda s: int(round(s * 24))  # noqa: E731
        return [(F(self.t_bit0 - 0.3), F(self.t_bit1 + 0.4)),
                (F(self.t_dio0 - 0.5), self.nframes + C.HANDLE - 1)]

    def in_3d(self, t):
        return self.t_bit0 <= t <= self.t_bit1 or t >= self.t_dio0

    # ------------------------------------------------------------------ 3D
    def build(self):
        import bl
        import equipment as E
        import models as MD
        tl = self.tl
        T = self.T
        F = lambda s: int(round(s * 24))  # noqa: E731
        M = E.mats()
        # ---- PDC bit product shot
        bit = E.pdc_bit(M, r=0.155, blades=6, name='PDC')
        holder = bl.empty('bit_holder', (BIT_X, 0, 0))
        bit.parent = holder
        holder.rotation_euler = (math.radians(-125), 0, math.radians(20))
        bl.spin(bit, F(self.t_bit0), F(self.t_bit1), 0.9)
        # BHA above the bit
        bha = bl.cyl('bha', 0.1, 1.2, loc=(0, 0, 1.35), material=M['steel_dark'], seg=32)
        bha.parent = bit
        # ---- steering diorama
        D = MD.Diorama(well=False)
        d = D.dio
        MD.ocean(spatial=10, wave_scale=0.05, wind=9, alpha=0.96, col='#2A78B8',
                 frames=(0, tl.nframes + 40))
        path_pts = [(0, -0.12, 0.0), (0, -0.12, d.z(900)), (0.25, -0.12, d.z(1500)),
                    (1.2, -0.12, d.z(2100)), (2.6, -0.12, d.z(2600)), (3.7, -0.12, d.z(2950)),
                    (4.3, -0.12, d.z(3050))]
        path = bl.curve_tube('steer_path', path_pts, 0.09, bl.mat('steer', P.ACCENT, rough=0.3))
        cu = path.data
        cu.bevel_factor_end = 0.02
        cu.keyframe_insert('bevel_factor_end', frame=F(self.t_dio0))
        cu.bevel_factor_end = 1.0
        cu.keyframe_insert('bevel_factor_end', frame=F(T['target'] + 1.2))
        # target ring in the reservoir
        ring = bl.annulus('target', 0.28, 0.36, -0.02, 0.02, material=bl.mat('tgt', '#FFFFFF'),
                          seg=48)
        ring.rotation_euler = (math.pi / 2, 0, 0)
        ring.location = (4.3, -0.14, d.z(3050))
        bl.pop_in(ring, F(T['target'] - 0.3), 10)
        rig_root, rig_body, der = E.semisub(M)
        rig_root.scale = (0.011, 0.011, 0.011)
        rig_root.location = (0, 0.0, d.sea_z)
        bl.cyl('ministring', 0.012, d.sea_z + 0.4, loc=(0, 0.0, (d.sea_z + 0.4) / 2 - 0.2),
               material=M['pipe'], seg=12)
        # camera: bit shot, then diorama
        cam = bl.Cam((BIT_X + 0.9, -0.9, 0.4), (BIT_X, 0, 0.05), lens=50)
        f0, f1, f2 = F(self.t_bit0), F(self.t_bit1), F(self.t_dio0)
        cam.key(f0, loc=(BIT_X + 0.75, -0.95, 0.30), target=(BIT_X + 0.05, 0, 0.02), lens=50)
        cam.key(f1, loc=(BIT_X + 0.55, -0.75, 0.22), target=(BIT_X + 0.02, 0, 0.0), lens=50)
        cam.key(f2 - 1, loc=(BIT_X + 0.55, -0.75, 0.22), target=(BIT_X + 0.02, 0, 0.0), lens=50)
        cam.key(f2, loc=(8.0, -22.0, -6.0), target=(1.8, 0.5, -10.5), lens=35)
        cam.key(F(tl.duration + 0.6), loc=(10.0, -21.0, -8.0), target=(2.2, 0.5, -12.0), lens=35)
        for obj in (cam.obj, cam.target, cam.obj.data):
            ad = obj.animation_data
            for fc in bl._fcurves(ad.action):
                for kp in fc.keyframe_points:
                    if abs(kp.co[0] - (f2 - 1)) < 0.5:
                        kp.interpolation = 'CONSTANT'
        # anchors
        return {
            'bit_face': (BIT_X, 0, 0), 'cutter': (BIT_X + 0.12, -0.08, 0.03),
            'nozzle': (BIT_X + 0.03, -0.05, -0.02),
            'tgt': (4.3, -0.14, d.z(3050)), 'kick': (0.2, -0.14, d.z(1500)),
            'path_mid': (1.9, -0.14, d.z(2350)), 'rig': (0, 0, d.sea_z + 0.8),
        }

    # ------------------------------------------------------------------ 2D
    def draw_bg(self, ctx, t, f):
        G.bg_gradient(ctx)

    def draw(self, ctx, t, f, A):
        T = self.T
        if t < self.t_bit1 - 0.3:
            a2d = 1 - G.prog(t, self.t_bit0 - 0.2, 0.5)
        elif t < self.t_dio0 - 0.4:
            a2d = G.prog(t, self.t_bit1 - 0.3, 0.6)
        else:
            a2d = 1 - G.prog(t, self.t_dio0 - 0.4, 0.6)
        if a2d > 0:
            ctx.save()
            ctx.push_group()
            G.bg_gradient(ctx)
            self.draw_loop(ctx, t)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(a2d)
            ctx.restore()
        if self.t_bit0 < t < self.t_bit1 + 0.2:
            self.draw_bit_labels(ctx, t, A)
        if t > self.t_dio0:
            self.draw_steer(ctx, t, A)

    # ------------------------------------------------------------------ loop diagram
    def draw_loop(self, ctx, t):
        T = self.T
        # title for mc1
        st = G.window(t, 0.3, T['pumps'] - 0.3, 0.5)
        self.draw_rig(ctx, t)
        if st > 0:
            G.panel(ctx, 1010, 600, 660, 260, st, alpha=0.95)
            G.tag(ctx, 'DRILLING MUD', 1340, 690, st, bg=P.MUD, size=48, align='center')
            G.text(ctx, 'the star of the show', 1340, 790, 36, 'SemiBold', P.INK_SOFT,
                   'center', alpha=st)
        # flow particles
        run = G.prog(t, T['pumps'] - 0.5, 1.0)
        if run > 0:
            self.particles(ctx, t, SUPPLY, P.MUD, run, speed=0.10, n=26)
            cut = G.prog(t, T['flushing'], 1.0)
            self.particles(ctx, t, RET_L, P.MUD_LIGHT, run * G.prog(t, T['nozzles'], 1.0),
                           speed=0.07, n=34, chips=cut)
            self.particles(ctx, t, RET_R, P.MUD_LIGHT, run * G.prog(t, T['nozzles'], 1.0),
                           speed=0.10, n=14, chips=cut)
        # shaker: cuttings fall into the skip
        sh = G.prog(t, T['shakers'] - 0.5, 0.5)
        if sh > 0:
            for i, (ph0, sgn, spd) in enumerate(self.chips[:14]):
                ph = (t * 0.6 + ph0) % 1.0
                x = 470 - 20 * ph
                y = 250 + 35 * ph
                G.rect(ctx, x + sgn * 8, y, 7, 5, fill=P.CUTTINGS, alpha=sh * (1 - ph))
        self.draw_labels(ctx, t)
        # zoom inset at the bit
        zi = G.window(t, T['nozzles'] - 0.4, T['annulus'] - 0.4, 0.5)
        if zi > 0:
            self.bit_inset(ctx, t, zi)
        # MWD pulses
        mw = G.window(t, T['sensors'] - 0.8, self.t_dio0, 0.5)
        if mw > 0 and t > self.t_bit1:
            self.mwd(ctx, t, mw)

    def draw_rig(self, ctx, t):
        # sea
        G.rect(ctx, 300, Y_SEA, 1320, Y_BED - Y_SEA, fill='#5DAFE3', alpha=0.55)
        # earth
        from well2d import pattern
        ctx.save()
        ctx.rectangle(300, Y_BED, 1320, 1040 - Y_BED)
        ctx.clip()
        ctx.set_source(pattern('claystone', 0.45))
        ctx.paint()
        ctx.restore()
        G.line(ctx, [(300, Y_BED), (1620, Y_BED)], '#8A7A5A', 3)
        # well: casing + open hole
        G.rect(ctx, WX - 40, Y_BED, 80, Y_SHOE - Y_BED, fill='#CFC9BB')
        G.rect(ctx, WX - 34, Y_BED, 68, Y_BIT - Y_BED, fill='#3B4652')
        G.rect(ctx, WX - 30, Y_BED, 60, Y_BIT - Y_BED, fill=P.MUD, alpha=0.35)
        for sx in (-1, 1):
            G.line(ctx, [(WX + sx * 34, Y_BED), (WX + sx * 34, Y_SHOE)], P.STEEL_DARK, 6)
        # riser
        G.rect(ctx, WX - 20, Y_DECK, 40, Y_BED - Y_DECK, fill='#B8C4CF')
        G.rect(ctx, WX - 15, Y_DECK, 30, Y_BED - Y_DECK, fill=P.MUD, alpha=0.35)
        # BOP
        G.rect(ctx, WX - 44, Y_BED - 70, 88, 64, fill=P.BOP)
        G.rect(ctx, WX - 30, Y_BED - 60, 60, 44, fill='#6F7C8A')
        G.rect(ctx, WX - 22, Y_BED - 6, 44, 10, fill='#4A5663')
        # drill string + bit
        G.rect(ctx, WX - 6, 160, 12, Y_BIT - 20 - 160, fill=P.PIPE)
        G.rect(ctx, WX - 10, Y_BIT - 110, 20, 90, fill='#46505B')  # BHA
        G.poly(ctx, [(WX - 28, Y_BIT - 22), (WX + 28, Y_BIT - 22), (WX + 22, Y_BIT), (WX - 22, Y_BIT)],
               fill='#2F363D')
        # rig: pontoons, columns, deck, derrick, top drive
        G.rect(ctx, 480, Y_SEA + 70, 560, 40, fill='#9E3A30', alpha=0.9)
        for x in (520, 940):
            G.rect(ctx, x, Y_DECK + 18, 60, Y_SEA + 70 - Y_DECK - 18, fill='#E7E9EC')
        G.rect(ctx, 420, Y_DECK, 1200, 20, fill='#8C969F')
        G.poly(ctx, [(690, Y_DECK), (720, 60), (800, 60), (830, Y_DECK)], stroke='#CBD2D8', lw=6,
               close=False)
        for y in (110, 160, 210):
            k = (y - 60) / (Y_DECK - 60)
            G.line(ctx, [(720 - 30 * k, y), (800 + 30 * k, y)], '#CBD2D8', 4)
        G.rect(ctx, WX - 18, 125, 36, 40, fill=P.RIG_YELLOW)
        # standpipe
        G.line(ctx, [(1500, 250), (1500, 110), (800, 110), (780, 130)], '#7E8B98', 8)
        # shaker, skip, pits, pump
        G.poly(ctx, [(460, 238), (610, 206), (616, 216), (466, 250)], fill='#6F7C89')
        for k in range(6):
            G.line(ctx, [(470 + k * 24, 236 - k * 5), (476 + k * 24, 246 - k * 5)], '#A9B3BD', 2)
        G.rect(ctx, 400, 262, 100, 40, fill='#4A5663')
        G.rect(ctx, 1150, 205, 180, 57, fill='#6F7C89')
        G.rect(ctx, 1156, 222, 168, 38, fill=P.MUD)
        G.rect(ctx, 1400, 205, 150, 57, fill='#4A5663')
        px = 1420 + 20 * (0.5 + 0.5 * math.sin(t * 6))
        G.rect(ctx, px, 222, 60, 22, fill='#A9B3BD')
        G.line(ctx, [(1330, 250), (1400, 250)], '#7E8B98', 8)
        G.line(ctx, [(WX - 20, Y_DECK + 8), (610, 214)], '#7E8B98', 8)
        G.line(ctx, [(520, 290), (1220, 290), (1240, 262)], '#7E8B98', 6)

    def particles(self, ctx, t, pts, col, alpha, speed=0.1, n=24, chips=0.0):
        L = _poly_len(pts)
        for i in range(n):
            u = (t * speed * 1000 / L + i / n) % 1.0
            x, y = _at(pts, u)
            G.circle(ctx, x, y, 6, fill=col, alpha=alpha)
            if chips > 0 and i % 2 == 0 and u < 0.62:
                G.rect(ctx, x + 6, y - 3, 7, 6, fill=P.CUTTINGS, alpha=alpha * chips)

    def draw_labels(self, ctx, t):
        T = self.T
        out = G.prog(t, self.t_bit0 - 0.6, 0.4)
        L = [
            ((1480, 225), (1600, 380), 'Mud pumps', T['pumps']),
            ((WX - 6, 680), (WX - 170, 680), 'Down the drill string', T['inside']),
            ((WX + 26, 760), (WX + 200, 760), 'Up the annulus', T['annulus']),
            ((WX + 18, 420), (WX + 200, 420), 'Up the riser', T['riser']),
            ((540, 225), (520, 110), 'Shale shakers', T['shakers']),
            ((1240, 230), (1240, 150), 'Mud pits', T['pits']),
        ]
        for (ax, ay), (tx, ty), txt, t0 in L:
            G.label(ctx, ax, ay, tx, ty, txt, G.prog(t, t0 - 0.1, 0.7), out=out, size=28,
                    align='left' if tx > ax else 'right', elbow=False)
        ag = G.prog(t, T['again'] - 0.3, 0.6) * (1 - out)
        if ag > 0:
            G.tag(ctx, 'A CLOSED LOOP', 1340, 980, ag, bg=P.INK, size=32, align='center')

    def bit_inset(self, ctx, t, a):
        cx, cy, r = 1320, 760, 210
        G.line(ctx, [(WX + 30, Y_BIT - 10), (cx - r * 0.8, cy + r * 0.5)], P.INK, 3, a)
        G.circle(ctx, WX, Y_BIT - 10, 40, stroke=P.INK, lw=3, alpha=a)
        ctx.save()
        ctx.new_path()
        ctx.arc(cx, cy, r, 0, math.tau)
        ctx.clip()
        G.set_color(ctx, '#3B4652', a)
        ctx.paint()
        G.rect(ctx, cx - r, cy - r, 2 * r, 2 * r, fill=P.MUD, alpha=a * 0.35)
        # rock bottom
        G.rect(ctx, cx - r, cy + 120, 2 * r, 200, fill=P.CLAYSTONE, alpha=a)
        # bit body
        G.poly(ctx, [(cx - 130, cy + 30), (cx + 130, cy + 30), (cx + 110, cy + 110), (cx - 110, cy + 110)],
               fill='#56616D', alpha=a)
        G.rect(ctx, cx - 45, cy - r, 90, r + 30, fill='#46505B', alpha=a)
        G.rect(ctx, cx - 16, cy - r, 32, r + 60, fill=P.MUD, alpha=a * 0.9)
        # jets from nozzles
        for k, sx in enumerate((-70, 0, 70)):
            ph = (t * 3 + k * 0.33) % 1.0
            for j in range(4):
                q = (ph + j * 0.25) % 1.0
                G.circle(ctx, cx + sx + sx * 0.2 * q, cy + 110 + q * 20, 7 - 3 * q, fill=P.MUD_LIGHT,
                         alpha=a * (1 - q))
        # cuttings swept up the sides
        for k in range(10):
            ph = (t * 0.8 + k * 0.1) % 1.0
            side = -1 if k % 2 else 1
            x = cx + side * (140 + 15 * math.sin(ph * 6))
            y = cy + 110 - ph * 300
            G.rect(ctx, x, y, 10, 7, fill=P.CUTTINGS, alpha=a)
            G.arrow(ctx, cx + side * 175, cy + 60, cx + side * 175, cy - 120, P.MUD_LIGHT, 5, 16, 1, a * 0.8)
        ctx.restore()
        G.circle(ctx, cx, cy, r, stroke=P.WHITE, lw=10, alpha=a)
        G.text(ctx, 'cools the bit  ·  lifts the cuttings', cx, cy + r + 50, 28, 'Bold', P.INK,
               'center', alpha=a)

    def mwd(self, ctx, t, a):
        T = self.T
        # highlight BHA
        pb = G.prog(t, T['sensors'] - 0.2, 0.6)
        G.rect(ctx, WX - 16, Y_BIT - 116, 32, 100, stroke=P.ACCENT, lw=5, alpha=a * pb)
        G.label(ctx, WX + 16, Y_BIT - 70, WX + 190, Y_BIT - 90, 'MWD / LWD sensors', pb * a,
                sub='direction · inclination · rock properties', size=28, elbow=False)
        pp = G.prog(t, T['pulses'] - 0.3, 0.6)
        if pp > 0:
            for k in range(6):
                ph = (t * 0.45 + k / 6) % 1.0
                y = (Y_BIT - 120) - ph * (Y_BIT - 120 - 170)
                w = 18
                G.rect(ctx, WX - w / 2, y - 4, w, 8, fill='#FFFFFF', alpha=a * pp)
                G.rect(ctx, WX - w / 2 - 3, y - 6, w + 6, 12, stroke=P.ACCENT, lw=3, alpha=a * pp)
            # surface display
            G.panel(ctx, 1160, 360, 560, 300, pp * a)
            G.text(ctx, 'MUD-PULSE TELEMETRY', 1440, 410, 28, 'ExtraBold', P.ACCENT, 'center',
                   alpha=pp * a, tracking=0.08)
            pts = []
            for i in range(200):
                x = 1190 + i * 2.5
                v = 1 if math.sin((i - t * 40) * 0.18) > 0.3 else 0
                pts.append((x, 520 - v * 50))
            G.line(ctx, pts, P.INK, 3, pp * a)
            G.text(ctx, 'Inclination 32.4°   Azimuth 147°   Gamma 86 API', 1440, 610, 22, 'SemiBold',
                   P.INK_SOFT, 'center', alpha=pp * a)

    # ------------------------------------------------------------------ 3D overlays
    def draw_bit_labels(self, ctx, t, A):
        T = self.T
        a = self.A
        tp = G.window(t, self.t_bit0 + 0.3, self.t_bit1, 0.5)
        G.tag(ctx, 'PDC BIT', 200, 160, tp, bg=P.INK, size=40)
        G.text(ctx, 'Polycrystalline Diamond Compact', 200, 240, 30, 'SemiBold', P.INK_SOFT,
               alpha=tp)
        c = a(A, 'cutter')
        if c:
            G.label(ctx, c[0], c[1], c[0] + 260, c[1] - 200, 'Diamond cutters',
                    G.prog(t, T['diamond'] - 0.2, 0.8), sub='synthetic diamond tables', size=30)
        # shaving inset
        sp = G.window(t, T['plane'] - 0.5, self.t_bit1, 0.4)
        if sp > 0:
            cx, cy = 1550, 790
            G.panel(ctx, cx - 280, cy - 190, 560, 360, sp)
            ctx.save()
            G.rrect(ctx, cx - 260, cy - 170, 520, 320, 16)
            ctx.clip()
            G.rect(ctx, cx - 260, cy + 20, 520, 140, fill=P.CLAYSTONE, alpha=sp)
            ph = (t * 0.5) % 1.0
            x = cx - 220 + 360 * ph
            # removed layer
            G.rect(ctx, x, cy, cx + 260 - x, 20, fill=P.CLAYSTONE, alpha=sp)
            # curled shaving
            ctx.new_path()
            ctx.arc(x - 30, cy - 30, 30 + 10 * ph, math.pi * 0.2, math.pi * 1.6)
            G.set_color(ctx, '#8C7A62', sp)
            ctx.set_line_width(10)
            ctx.stroke()
            # cutter
            G.poly(ctx, [(x, cy + 20), (x + 20, cy - 60), (x + 60, cy - 50), (x + 40, cy + 30)],
                   fill='#2F353B', alpha=sp)
            G.line(ctx, [(x, cy + 20), (x + 20, cy - 60)], '#FFFFFF', 6, sp)
            G.arrow(ctx, x + 70, cy - 90, x + 150, cy - 90, P.INK, 4, 14, 1, sp)
            ctx.restore()
            G.text(ctx, 'shearing, like a plane on wood', cx, cy + 210, 26, 'Bold', P.INK, 'center',
                   alpha=sp)

    def draw_steer(self, ctx, t, A):
        T = self.T
        a = self.A
        tg = a(A, 'tgt')
        if tg:
            G.label(ctx, tg[0], tg[1], tg[0] + 120, tg[1] + 110, 'Target', G.prog(t, T['target'], 0.7),
                    sub='kilometres from the rig', size=30, elbow=False)
        km = a(A, 'kick')
        if km:
            G.label(ctx, km[0], km[1], km[0] - 150, km[1] - 60, 'Rotary steerable system',
                    G.prog(t, T['rss'], 0.8), sub='steers while rotating', size=30, align='right',
                    elbow=False)
