"""Scene 6 - Drilling: the semi-submersible rig, moorings, derrick and top drive."""
import math

import gfx as G
import overlays as O
import palette as P
from scene_base import Scene


class S(Scene):
    ID = 's06_rig'
    BLENDER = True
    PHASE = 1
    TRACKER_IN = 3.6

    def __init__(self):
        super().__init__()
        tl = self.tl
        self.T = dict(
            card_in=0.2, card_out=3.9,
            semi=tl.word('rg2', 'semi-submersible'),
            floating=tl.word('rg2', 'floating platform'),
            pontoons=tl.word('rg2', 'pontoons'),
            ballast=tl.word('rg2', 'ballasted'),
            swell=tl.word('rg2', 'swell'),
            anchors=tl.word('rg3', 'anchors'),
            thrusters=tl.word('rg3', 'thrusters'),
            derrick=tl.word('rg4', 'derrick'),
            topdrive=tl.word('rg4', 'top drive'),
            string=tl.word('rg4', 'drill string'),
            steel=tl.word('rg4', 'screwed together'),
            km=tl.word('rg4', 'several kilometers'),
        )

    def draw_bg(self, ctx, t, f):
        O.sky(ctx, 420)

    def build(self):
        import bl
        import equipment as E
        import models as MD
        tl = self.tl
        T = self.T
        F = lambda s: int(round(s * 24))  # noqa: E731
        n = tl.nframes + 30
        M = E.mats()
        root, body, der = E.semisub(M)
        # darker hull below the waterline reads better through the water
        oc = MD.ocean(generate=True, repeat=(8, 8), spatial=250, wave_scale=1.1, wind=11,
                      choppy=0.6, alpha=0.72, col='#2C7DBE', loc=(-1000, -1000, 0.0),
                      frames=(0, n), speed=0.9, resolution=9)
        fm = oc.data.materials[0]
        deep = bl.box('deep', (300000, 300000, 1), loc=(0, 0, -420),
                      material=bl.mat('deep_sea', '#1A4E7C', rough=0.9))
        deep.visible_shadow = False
        for (x, y, sx, sy) in ((0, 30500, 120000, 59000), (0, -30500, 120000, 59000),
                               (30500, 0, 59000, 2000), (-30500, 0, 59000, 2000)):
            far = bl.box('far_sea', (sx, sy, 0.1), loc=(x, y, -0.3), material=fm)
            far.visible_shadow = False
        # moorings: 8 catenary lines from the corner columns
        chain = bl.mat('chain', '#C9D2DA', rough=0.6)
        for (cx, cy) in ((-38, -30), (38, -30), (-38, 30), (38, 30)):
            for da in (-0.35, 0.35):
                ang = math.atan2(cy, cx) + da
                x0, y0 = cx + 7 * math.cos(ang), cy + 7 * math.sin(ang)
                pts = []
                for k in range(9):
                    u = k / 8
                    dist = 30 + 950 * u
                    z = -8 - 350 * (1 - (1 - u) ** 2.2)
                    pts.append((cx + dist * math.cos(ang), cy + dist * math.sin(ang), z))
                pts[0] = (x0, y0, -8)
                bl.curve_tube('mooring', pts, 1.6, chain)
        # top drive + drill string
        td = E.top_drive(M)
        td.location = (0, 0, 84)
        bl.key(td, 'location', F(T['derrick'] - 1.0), (0, 0, 84))
        bl.key(td, 'location', F(tl.duration + 1.0), (0, 0, 44))
        string = bl.cyl('string', 0.45, 190, loc=(0, 0, -95), material=M['pipe'], seg=24)
        marks = []
        for z in range(-180, 0, 12):
            marks.append(bl.cyl('tj', 0.62, 0.8, loc=(0, 0, z), material=M['steel'], seg=24))
        stripe = bl.box('stripe', (0.2, 1.0, 190), loc=(0.35, 0, -95), material=M['yellow'])
        ds = bl.join([string, stripe] + marks, 'drillstring')
        ds.parent = td
        ds.location = (0, 0, -95.6)
        bl.spin(ds, 0, n, n / 24 * 0.6)
        # gentle heave of the rig
        for k in range(0, n + 48, 48):
            bl.key(root, 'location', k, (0, 0, 0.5 * math.sin(k / 48 * 1.3)))
            bl.key(root, 'rotation_euler', k, (0.004 * math.sin(k / 48 * 1.1), 0.003 * math.cos(k / 48 * 0.9), 0))
        td.parent = None
        cam = bl.Cam((330, -380, 150), (0, 0, 10), lens=35)
        cam.key(0, loc=(360, -420, 170), target=(0, 0, 5))
        cam.key(F(T['semi'] - 0.5), loc=(260, -300, 120), target=(0, 0, 10))
        cam.key(F(T['pontoons'] - 0.6), loc=(150, -170, 40), target=(0, 0, -6))
        cam.key(F(T['ballast'] + 0.8), loc=(40, -205, 36), target=(0, 0, -4))
        cam.key(F(T['swell'] + 0.4), loc=(-60, -200, 55), target=(0, 0, 8))
        cam.key(F(T['anchors'] - 0.8), loc=(-500, -700, 520), target=(0, 0, -60))
        cam.key(F(T['thrusters'] + 0.6), loc=(-420, -640, 460), target=(0, 0, -40))
        cam.key(F(T['derrick'] - 0.6), loc=(-110, -140, 175), target=(0, 0, 58))
        cam.key(F(T['topdrive'] + 0.2), loc=(-70, -88, 135), target=(0, 0, 62))
        cam.key(F(T['string'] + 0.5), loc=(-62, -78, 118), target=(0, 0, 53))
        cam.key(F(tl.duration + 0.6), loc=(-58, -74, 106), target=(0, 0, 46))
        return {
            'pontoon': (20, -38.5, -17.5), 'column': (38, -37.5, 5), 'deck': (-10, -39, 22),
            'derrick': (0, -6, 75), 'td': (td, (0, -1.2, 3.0)), 'floor': (4, -9, 35),
            'string': (0, -0.5, 46), 'moor': (-38 - 250, -30 - 200, -80),
            'rig': (0, 0, 60), 'wl': (60, -40, 0),
        }

    def draw(self, ctx, t, f, A):
        T = self.T
        a = self.A
        G.chapter_title(ctx, 2, 'Drilling', t, T['card_in'], T['card_out'],
                        sub='Making hole, safely', accent='#2F80C9', backdrop=True)
        L = [
            ('pontoon', 'Pontoons', 'ballasted below the waves', T['pontoons'], T['swell'] + 0.6,
             (-120, 130), 'right'),
            ('column', 'Columns', 'small waterplane = gentle motion', T['ballast'], T['swell'] + 0.6,
             (160, -150), 'left'),
            ('moor', 'Anchor lines', '8 mooring lines', T['anchors'], T['derrick'] - 1.0,
             (-60, -160), 'right'),
            ('derrick', 'Derrick', None, T['derrick'], 100, (190, -60), 'left'),
            ('td', 'Top drive', 'rotates the string', T['topdrive'], 100, (-260, -40), 'right'),
            ('string', 'Drill string', 'steel pipe, ~9 m per joint', T['string'], 100,
             (240, 120), 'left'),
        ]
        for key, txt, sub, t0, t1, off, al in L:
            pt = a(A, key)
            if not pt:
                continue
            p = G.prog(t, t0, 0.8)
            out = G.prog(t, t1, 0.5)
            G.label(ctx, pt[0], pt[1], pt[0] + off[0], pt[1] + off[1], txt, p, sub=sub, out=out,
                    align=al, size=30)
        tp = G.window(t, T['thrusters'] - 0.3, T['derrick'] - 1.0, 0.4)
        if tp > 0:
            G.tag(ctx, '...or computer-controlled thrusters (DP)', 960, 980, tp, bg=P.INK, size=28,
                  align='center')
        kp = G.prog(t, T['km'] - 0.3, 0.7)
        if kp > 0:
            G.panel(ctx, 1380, 780, 430, 190, kp)
            G.text(ctx, '3,000+ m', 1595, 870, 64, 'ExtraBold', P.INK, 'center', alpha=kp)
            G.text(ctx, 'of pipe, joint by joint', 1595, 925, 26, 'SemiBold', P.INK_SOFT, 'center',
                   alpha=kp)
