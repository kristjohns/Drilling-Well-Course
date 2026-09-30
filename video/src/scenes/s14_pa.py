"""Scene 14 - Plug and abandonment: eternal perspective, permanent barriers, removal."""
import math

import gfx as G
import overlays as O
import palette as P
import schem
import well2d as W2
from scene_base import Scene
from scenes.s07_tophole import underwater_bg

PA_COL = '#6A5ACD'
RS = 1.6
CUT_Z = -5.0
DIO_X = 400.0
# plug depths (m MSL) on the 2D schematic
PRIM = (3120, 3260)
SEC = (2900, 3040)
SURF = (420, 560)


class S(Scene):
    ID = 's14_pa'
    BLENDER = True
    PHASE = 3
    TRACKER_IN = 3.8

    def __init__(self):
        super().__init__()
        tl = self.tl
        self.w = schem.make()
        self.T = dict(
            card_out=3.9,
            remarkable=tl.word('pa1', 'remarkable'),
            eternal=tl.word('pa1', 'eternal perspective'),
            years=tl.word('pa2', 'years'),
            decades=tl.word('pa2', 'decades'),
            rock=tl.word('pa2', 'as long as the rock'),
            killed=tl.word('pa3', 'killed'),
            tree=tl.word('pa3', 'christmas tree'),
            bop=tl.word('pa3', 'B O P'),
            tubing=tl.word('pa3', 'tubing'),
            permanent=tl.word('pa4', 'permanent'),
            cross=tl.word('pa4', 'entire cross-section'),
            annulus=tl.word('pa4', 'every annulus'),
            r2r=tl.word('pa4', 'Rock to rock'),
            tricky=tl.word('pa5', 'tricky'),
            missing=tl.word('pa5', 'missing'),
            sneak=tl.word('pa5', 'sneaking'),
            milled=tl.word('pa6', 'milled'),
            perforated=tl.word('pa6', 'perforated'),
            bonds=tl.word('pa6', 'bonds'),
            primary=tl.word('pa7', 'primary barrier'),
            caprock=tl.word('pa7', 'cap rock'),
            secondary=tl.word('pa7', 'secondary barrier'),
            tens=tl.word('pa7', 'tens of meters'),
            surface=tl.word('pa8', 'surface plug'),
            tagged=tl.word('pa9', 'tagged'),
            ptest=tl.word('pa9', 'pressure tested'),
            cut=tl.word('pa10', 'cut'),
            lifted=tl.word('pa10', 'lifted'),
            seabed=tl.word('pa11', 'just the seabed'),
            restored=tl.word('pa11', 'restored'),
            lid=tl.word('pa11', "Nature's lid"),
        )
        T = self.T
        self.t_3d = tl.t('pa10') - 0.7
        self.t_dio = tl.t('pa11') - 0.8

    def render_ranges(self):
        import config as C
        return [(int(round((self.t_3d - 0.2) * 24)), self.nframes + C.HANDLE - 1)]

    def draw_bg(self, ctx, t, f):
        if self.t_3d - 0.2 < t < self.t_dio:
            underwater_bg(ctx, t)
        else:
            G.bg_gradient(ctx)

    # ------------------------------------------------------------------ 3D
    def build(self):
        import bpy
        import bl
        import equipment as E
        import models as MD
        tl = self.tl
        T = self.T
        F = lambda s: int(round(s * 24))  # noqa: E731
        M = E.mats()
        steel = bl.mat('pa_steel', '#A7B4C1', rough=0.35, metal=0.15)
        cut = bl.mat('pa_cut', '#C3CDD7', rough=0.5)
        cem, cem_cut = MD.cement_mats()
        soil = MD.strata_mat('soft_clay')
        seabed = bl.tex_mat('seabed', MD.tex('seabed'))
        # soil block with the well notch
        R_OUT = 0.457 * RS
        for (zt, zb) in ((0.0, -4.0), (-4.0, -10.0), (-10.0, -24.0)):
            sl = MD.notched_slab('soil', -14, 14, 0, 14, zb, zt, R_OUT, soil, seg=48)
            bl.uv_box(sl, 3.0)
            if zt == 0.0:
                sl.data.materials.append(seabed)
                for p in sl.data.polygons:
                    if p.normal.z > 0.9:
                        p.material_index = 1
        bed = bl.box('bed', (400, 200, 0.2), loc=(0, 114, -0.1), material=seabed)
        bl.uv_box(bed, 6.0)
        for x in (-114, 114):
            b2 = bl.box('bed2', (200, 14, 0.2), loc=(x, 7, -0.1), material=seabed)
            bl.uv_box(b2, 6.0)
        # nested casings (radii exaggerated), each split at the cut depth
        strings = [(0.381, 0.355), (0.254, 0.235), (0.170, 0.156), (0.122, 0.110)]
        top = bl.empty('pulled_top')
        prev_in = 0.457
        for i, (ro, ri) in enumerate(strings):
            ro, ri = ro * RS, ri * RS
            zt = 1.2 if i == 0 else 1.7
            up = bl.annulus('cs_up_%d' % i, ri, ro, CUT_Z, zt, 0, math.pi, 64, steel, cut)
            lo = bl.annulus('cs_lo_%d' % i, ri, ro, -24, CUT_Z, 0, math.pi, 64, steel, cut)
            up.parent = top
            # cement between this string and the previous one
            ce_up = bl.annulus('ce_up_%d' % i, ro, prev_in * (RS if i == 0 else 1), CUT_Z, 0.0,
                               0, math.pi, 64, cem, cem_cut)
            ce_lo = bl.annulus('ce_lo_%d' % i, ro, prev_in * (RS if i == 0 else 1), -24, CUT_Z,
                               0, math.pi, 64, cem, cem_cut)
            for c in (ce_up, ce_lo):
                bl.uv_cyl(c, 1.0)
            if i > 0:
                ce_up.parent = top
            prev_in = ri
        # surface cement plug inside the innermost string
        plug = bl.annulus('surf_plug', 0, strings[-1][1] * RS, -22, -12, 0, math.pi, 48, cem, cem_cut)
        bl.uv_cyl(plug, 1.0)
        # housings
        lp = bl.revolve('lp', [(0.355 * RS, 0.9), (0.56 * RS, 0.9), (0.56 * RS, 1.0), (0.48 * RS, 1.1),
                               (0.48 * RS, 1.75), (0.40 * RS, 1.85), (0.355 * RS, 1.85)], 64, 0,
                        math.pi, M['steel_dark'], cut)
        hp = bl.revolve('hp', [(0.24 * RS, 1.6), (0.36 * RS, 1.6), (0.36 * RS, 3.3), (0.30 * RS, 3.6),
                               (0.24 * RS, 3.6)], 64, 0, math.pi, M['steel'], cut)
        for o in (lp, hp):
            o.parent = top
        # cutting tool
        tool = bl.empty('cutter')
        body = bl.cyl('cutter_body', 0.10, 1.2, loc=(0, 0, 0.6), material=M['dark'], seg=16)
        body.parent = tool
        for k in range(3):
            ang = k * math.tau / 3
            bl.box('knife', (0.34, 0.06, 0.08), loc=(0.2 * math.cos(ang), 0.2 * math.sin(ang), 0.1),
                   rot=(0, 0, ang), material=M['yellow']).parent = tool
        dp = bl.cyl('cut_dp', 0.06, 40, loc=(0, 0, 21.2), material=M['pipe'], seg=12)
        dp.parent = tool
        f_in = F(self.t_3d + 0.2)
        bl.key(tool, 'location', f_in, (0, 0, 20.0))
        bl.key(tool, 'location', F(T['cut'] - 0.3), (0, 0, CUT_Z - 0.1))
        bl.spin(tool, F(T['cut'] - 0.3), F(T['lifted'] - 0.6), 6)
        bl.key(tool, 'location', F(T['lifted'] - 0.6), (0, 0, CUT_Z - 0.1))
        bl.key(tool, 'location', F(T['lifted'] - 0.1), (0, 0, 25.0))
        bl.hide_at(tool, F(T['lifted']))
        # lift the wellhead with the casing stubs
        bl.key(top, 'location', F(T['lifted'] - 0.1), (0, 0, 0))
        bl.key(top, 'location', F(self.t_dio - 0.2), (0, 0, 26.0))
        # ---------------- plugged-well diorama (for the final shot)
        D = MD.Diorama(well=True, cores=False, x_center=0.0)
        dio_objs = D.objs['slabs'] + D.objs['sea']
        d = D.dio
        casings = []
        for i in range(5):
            parts = MD.casing_string(d, i)
            casings.append(parts['casing'])
            dio_objs += [parts['casing']] + parts['cement']
        plug_m = bl.mat('plug_glow', '#E9E4D8', rough=0.8)
        plugs = []
        for (a_, b_) in ((2780, 2930), (2560, 2700), (70, 210)):
            r = d.r(9.625) / 2 * 0.92
            pl = bl.annulus('dio_plug', 0, r, d.z(b_), d.z(a_), 0, math.pi, 32, plug_m)
            plugs.append(pl)
            dio_objs.append(pl)
        oc = MD.ocean(spatial=10, wave_scale=0.05, wind=9, alpha=0.96, col='#2A78B8',
                      frames=(0, tl.nframes + 40))
        dio_objs.append(oc)
        for o in dio_objs:
            o.location.x += DIO_X
        # camera
        cam = bl.Cam((10, -26, 7), (0, 1, -2.0), lens=35)
        cam.key(f_in - 2, loc=(9, -25, 5), target=(0, 1, -3.0))
        cam.key(F(T['cut'] + 0.5), loc=(8, -22, 2), target=(0, 0, -4.0))
        cam.key(F(T['lifted'] + 0.5), loc=(10, -26, 8), target=(0, 1, 3.0))
        fcut = F(self.t_dio)
        cam.key(fcut - 1, loc=(10, -26, 10), target=(0, 1, 6.0))
        cam.key(fcut, loc=(DIO_X + 5.0, -14.0, -11.0), target=(DIO_X, 0.5, -14.2))
        cam.key(F(T['restored'] + 0.5), loc=(DIO_X + 7.0, -20.0, -9.0), target=(DIO_X, 0.5, -12.5))
        cam.key(F(tl.duration + 0.6), loc=(DIO_X + 13.0, -33.0, -2.0), target=(DIO_X, 1.0, -7.0))
        for obj in (cam.obj, cam.target):
            for fc in bl._fcurves(obj.animation_data.action):
                for kp in fc.keyframe_points:
                    if abs(kp.co[0] - (fcut - 1)) < 0.5:
                        kp.interpolation = 'CONSTANT'
        # hide the seabed set once we cut to the diorama
        for o in list(bpy.data.objects):
            if o.location.x < DIO_X - 100 and o.type in ('MESH', 'CURVE', 'EMPTY') and o.parent is None:
                if o.name.startswith(('Cam',)):
                    continue
                bl.hide_at(o, fcut)
        z = d.z
        A = {
            'cut': (strings[0][0] * RS + 0.05, -0.05, CUT_Z), 'wh': (top, (0.6, -0.3, 2.4)),
            'plug3d': (0.12, -0.05, -17.0),
            'cap_q0': (DIO_X - 8, 0, z(2800)), 'cap_q1': (DIO_X + 8, 0, z(2800)),
            'cap_q2': (DIO_X + 8, 0, z(2950)), 'cap_q3': (DIO_X - 8, 0, z(2950)),
            'p_prim': (DIO_X + 0.05, -0.05, z(2860)), 'p_sec': (DIO_X + 0.05, -0.05, z(2630)),
            'p_surf': (DIO_X + 0.05, -0.05, z(140)), 'seabed': (DIO_X + 2, 0, 0.0),
        }
        return A

    # ------------------------------------------------------------------ 2D
    def draw(self, ctx, t, f, A):
        T = self.T
        a2 = 1 - G.prog(t, self.t_3d - 0.3, 0.6)
        if a2 > 0:
            ctx.save()
            ctx.push_group()
            G.bg_gradient(ctx)
            self.draw_2d(ctx, t)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(a2)
            ctx.restore()
        if t > self.t_3d - 0.3:
            self.draw_3d_labels(ctx, t, A)
        G.chapter_title(ctx, 4, 'Plug & Abandonment', t, 0.2, T['card_out'],
                        sub='Sealed with an eternal perspective', accent=PA_COL)

    def draw_2d(self, ctx, t):
        T = self.T
        # eternal perspective hero
        ep = G.window(t, T['remarkable'] - 0.2, T['killed'] - 0.8, 0.5)
        if ep > 0:
            self.eternal(ctx, t, ep)
        sp = G.prog(t, T['killed'] - 0.9, 0.7)
        if sp > 0:
            ctx.save()
            ctx.push_group()
            self.schematic(ctx, t)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(sp)
            ctx.restore()
            self.right_side(ctx, t, sp)

    def eternal(self, ctx, t, a):
        T = self.T
        pi = G.prog(t, T['eternal'] - 0.4, 0.8)
        G.text(ctx, 'THE REQUIREMENT', 960, 300, 32, 'Bold', P.INK_SOFT, 'center', alpha=a,
               tracking=0.2)
        G.text(ctx, 'An eternal perspective', 960, 420, 84, 'ExtraBold', PA_COL, 'center',
               alpha=a * pi)
        # timeline arrow
        tp = G.prog(t, T['years'] - 0.4, 0.6)
        if tp > 0:
            x0, x1, y = 360, 1560, 640
            reach = x0 + (x1 - x0) * (0.25 * G.prog(t, T['years'] - 0.3, 0.6) +
                                       0.25 * G.prog(t, T['decades'] - 0.3, 0.6) +
                                       0.5 * G.prog(t, T['rock'] - 0.3, 1.2))
            G.arrow(ctx, x0, y, max(x0 + 1, reach), y, P.INK, 6, 22, 1.0, a)
            marks = [(x0 + (x1 - x0) * 0.22, 'years', T['years'], False),
                     (x0 + (x1 - x0) * 0.48, 'decades', T['decades'], False),
                     (x1 + 40, '∞', T['rock'], True)]
            for x, lab, t0, good in marks:
                p = G.prog(t, t0 - 0.1, 0.5)
                if p <= 0:
                    continue
                G.circle(ctx, x, y, 14 * p, fill=P.GOOD if good else P.KICK, alpha=a)
                if lab == '∞':
                    G.text(ctx, '∞', x, y - 40, 110, 'Bold', PA_COL, 'center', alpha=a * p,
                           family='DejaVu Sans')
                    G.text(ctx, 'as long as the rock itself', x - 60, y + 70, 30, 'Bold', P.GOOD,
                           'center', alpha=a * p)
                else:
                    G.text(ctx, lab, x, y - 40, 36, 'Bold', P.INK_SOFT, 'center', alpha=a * p)
                    G.line(ctx, [(x - 18, y + 30), (x + 18, y + 66)], P.KICK, 6, a * p)
                    G.line(ctx, [(x - 18, y + 66), (x + 18, y + 30)], P.KICK, 6, a * p)

    def schematic(self, ctx, t):
        T = self.T
        w = self.w
        G.panel(ctx, w.x0 - 20, 80, w.x1 - w.x0 + 40, 960, 1.0, alpha=0.95)
        ctx.save()
        ctx.rectangle(w.x0, 90, w.x1 - w.x0, 940)
        ctx.clip()
        w.draw_earth(ctx, labels=True)
        kill = G.prog(t, T['killed'] - 0.2, 1.5)
        fluid = G.mix('#9FD3E8', P.HEAVY_MUD, kill)
        w.fill_bore(ctx, 350, 3430, fluid)
        for i in range(5):
            w.cement(ctx, i, 1.0)
            w.casing(ctx, i, 1.0)
        # poor cement behind the 9-5/8 in the upper part (the hidden problem)
        y_bed = w.y(350)
        # tubing string being pulled
        pull = G.prog(t, T['tubing'] - 0.2, 2.5)
        dy = -700 * pull
        yp = w.y(3100)
        if pull < 1:
            for sx in (-1, 1):
                G.rect(ctx, w.cx + sx * 16 - (12 if sx < 0 else 0), y_bed - 30 + dy, 12,
                       yp + 20 - y_bed + 30, fill=P.PIPE)
            ihw = w.hw(9.625) - 4
            G.rect(ctx, w.cx - ihw * (1 - pull * 0.3), yp + dy, 2 * ihw * (1 - pull * 0.3), 22,
                   fill='#2B2F33')
        # plugs
        plug_specs = [(PRIM, T['primary'] - 0.2), (SEC, T['secondary'] - 0.2), (SURF, T['surface'] - 0.2)]
        for (dt, db), t0 in plug_specs:
            p = G.prog(t, t0, 1.2)
            if p > 0:
                top = db - (db - dt) * p
                ihw = w.hw(9.625) - 4
                ctx.rectangle(w.cx - ihw, w.y(top), 2 * ihw, w.y(db) - w.y(top))
                ctx.save()
                ctx.clip()
                ctx.set_source(W2.pattern('cement', 0.35))
                ctx.paint()
                G.set_color(ctx, PA_COL, 0.12)
                ctx.paint()
                ctx.restore()
        W2.draw_wellhead(ctx, w.cx, y_bed, 1.0)
        tree_up = G.prog(t, T['tree'] - 0.2, 1.5)
        if tree_up < 1:
            W2.draw_xt(ctx, w.cx, y_bed - 30 - 300 * tree_up, 0.9, alpha=1 - tree_up)
        bop_in = G.prog(t, T['bop'] - 0.8, 1.2) * (1 - G.prog(t, T['surface'] + 1.5, 1.0))
        if bop_in > 0:
            W2.draw_bop(ctx, w.cx, y_bed - 30 - 250 * (1 - G.ease_out(G.clamp(bop_in * 1.2))), 0.8,
                        alpha=G.clamp(bop_in * 2), pipe=False)
        # tag test: pipe lowered onto the primary plug
        tg = G.window(t, T['tagged'] - 0.8, T['ptest'] + 1.5, 0.4)
        if tg > 0:
            y1 = w.y(PRIM[0]) - 4
            yy = 90 + (y1 - 90) * G.prog(t, T['tagged'] - 0.8, 0.8)
            G.rect(ctx, w.cx - 5, 90, 10, yy - 90, fill=P.PIPE, alpha=tg)
            G.arrow(ctx, w.cx + 40, yy - 120, w.cx + 40, yy - 20, P.INK, 6, 18,
                    G.prog(t, T['tagged'], 0.4), tg)
        ctx.restore()
        # envelopes
        cx = w.cx
        ev1 = G.prog(t, T['caprock'] - 0.3, 1.4)
        if ev1 > 0:
            oc = w.hw(12.25) + 8
            ihw = w.hw(9.625) - 4
            pts = [(cx - oc - 60, w.y(3300)), (cx - oc, w.y(3300)), (cx - oc, w.y(PRIM[0]) - 6),
                   (cx - ihw, w.y(PRIM[0]) - 6), (cx + ihw, w.y(PRIM[0]) - 6),
                   (cx + oc, w.y(PRIM[0]) - 6), (cx + oc, w.y(3300)), (cx + oc + 60, w.y(3300))]
            W2.envelope(ctx, pts, P.PRIMARY, ev1)
        ev2 = G.prog(t, T['secondary'] + 0.3, 1.4)
        if ev2 > 0:
            oc = w.hw(12.25) + 18
            ihw = w.hw(9.625) - 4
            pts = [(cx - oc - 60, w.y(3180)), (cx - oc, w.y(3180)), (cx - oc, w.y(SEC[0]) - 6),
                   (cx - ihw, w.y(SEC[0]) - 6), (cx + ihw, w.y(SEC[0]) - 6),
                   (cx + oc, w.y(SEC[0]) - 6), (cx + oc, w.y(3180)), (cx + oc + 60, w.y(3180))]
            W2.envelope(ctx, pts, P.SECONDARY, ev2)

    def right_side(self, ctx, t, a):
        T = self.T
        x0 = 930
        # step list during pa3
        st = G.window(t, T['killed'] - 0.6, T['permanent'] - 0.8, 0.5)
        if st > 0:
            G.panel(ctx, x0, 200, 840, 560, st)
            G.text(ctx, 'PREPARING THE WELL', x0 + 420, 270, 32, 'ExtraBold', PA_COL, 'center',
                   alpha=st, tracking=0.1)
            steps = [('Kill the well with heavy fluid', T['killed']),
                     ('Remove the christmas tree', T['tree']),
                     ('Install a BOP', T['bop']),
                     ('Pull the tubing', T['tubing'])]
            for i, (txt, t0) in enumerate(steps):
                p = G.prog(t, t0 - 0.2, 0.5)
                y = 360 + i * 100
                G.circle(ctx, x0 + 80, y, 28 * G.ease_out_back(p), fill=PA_COL, alpha=st)
                G.text(ctx, str(i + 1), x0 + 80, y, 30, 'ExtraBold', P.WHITE, 'center', 'middle',
                       alpha=st * p)
                G.text(ctx, txt, x0 + 135, y + 12, 34, 'Bold', P.INK, alpha=st * p)
        # cross-section rock-to-rock
        cs = G.window(t, T['permanent'] - 0.5, T['tricky'] - 0.6, 0.5)
        if cs > 0:
            self.cross_section(ctx, t, cs)
        # hidden problem: channel behind the casing
        hp = G.window(t, T['tricky'] - 0.4, T['milled'] - 0.6, 0.5)
        if hp > 0:
            self.channel(ctx, t, hp)
        # remedies
        rm = G.window(t, T['milled'] - 0.4, T['primary'] - 0.6, 0.5)
        if rm > 0:
            self.remedies(ctx, t, rm)
        # plug placement legend
        pl = G.prog(t, T['primary'] - 0.4, 0.6)
        if pl > 0:
            G.text(ctx, 'Permanent barriers', x0 + 420, 190, 44, 'ExtraBold', P.INK, 'center',
                   alpha=pl)
            schem.legend(ctx, x0 + 10, 260, [
                (P.PRIMARY, 'Primary barrier', 'cement plug set in the cap rock',
                 G.prog(t, T['primary'], 0.6)),
                (P.SECONDARY, 'Secondary barrier', 'a second plug backs it up',
                 G.prog(t, T['secondary'], 0.6)),
                ('#8C96A0', 'Surface plug', 'seals the well off from the ocean',
                 G.prog(t, T['surface'], 0.6)),
            ])
            tn = G.prog(t, T['tens'] - 0.3, 0.6)
            if tn > 0:
                G.panel(ctx, x0 + 10, 640, 820, 110, tn)
                G.text(ctx, 'each plug: typically 50–100 m of solid cement', x0 + 420, 707, 30,
                       'Bold', P.INK, 'center', alpha=tn)
            vp = G.prog(t, T['tagged'] - 0.4, 0.6)
            if vp > 0:
                G.panel(ctx, x0 + 10, 790, 820, 180, vp)
                G.text(ctx, 'VERIFIED', x0 + 420, 850, 32, 'ExtraBold', P.GOOD, 'center', alpha=vp,
                       tracking=0.12)
                p2 = G.prog(t, T['ptest'] - 0.2, 0.5)
                for (xx, txt, al) in ((x0 + 90, 'tagged with weight', vp),
                                      (x0 + 480, 'pressure tested', vp * p2)):
                    G.line(ctx, [(xx, 912), (xx + 12, 926), (xx + 34, 898)], P.GOOD, 7, al)
                    G.text(ctx, txt, xx + 50, 925, 30, 'Bold', P.INK, alpha=al)

    def cross_section(self, ctx, t, a):
        T = self.T
        cx, cy = 1350, 560
        G.panel(ctx, 930, 150, 840, 820, a)
        G.text(ctx, 'THE ENTIRE CROSS-SECTION', cx, 230, 32, 'ExtraBold', PA_COL, 'center', alpha=a,
               tracking=0.1)
        # plan view rings
        from well2d import pattern
        ctx.save()
        ctx.new_path()
        ctx.arc(cx, cy, 300, 0, math.tau)
        ctx.clip()
        ctx.set_source(pattern('shale', 0.6))
        ctx.paint_with_alpha(a)
        ctx.restore()
        fill_in = G.prog(t, T['cross'] - 0.3, 1.2)
        fill_ann = G.prog(t, T['annulus'] - 0.3, 1.2)
        rings = [(200, 'cement'), (150, 'steel'), (138, 'bore')]
        # annulus cement (outer), with a gap that gets filled
        ctx.save()
        ctx.new_path()
        ctx.arc(cx, cy, 200, 0, math.tau)
        ctx.arc_negative(cx, cy, 150, math.tau, 0)
        ctx.clip()
        ctx.set_source(pattern('cement', 0.4))
        ctx.paint_with_alpha(a)
        # the gap in the annulus
        gap = 1 - fill_ann
        if gap > 0:
            ctx.new_path()
            ctx.move_to(cx, cy)
            ctx.arc(cx, cy, 210, -0.9, -0.9 + 1.4 * gap)
            ctx.close_path()
            G.set_color(ctx, P.MUD, a)
            ctx.fill()
        ctx.restore()
        G.circle(ctx, cx, cy, 150, fill=P.STEEL_DARK, alpha=a)
        G.circle(ctx, cx, cy, 136, fill=G.mix('#9FD3E8', P.CEMENT, fill_in), alpha=a)
        if fill_in > 0:
            ctx.save()
            ctx.new_path()
            ctx.arc(cx, cy, 136 * fill_in, 0, math.tau)
            ctx.clip()
            ctx.set_source(pattern('cement', 0.4))
            ctx.paint_with_alpha(a)
            ctx.restore()
        G.text(ctx, 'formation', cx + 250, cy - 250, 24, 'Bold', P.WHITE, 'center', alpha=a)
        G.label(ctx, cx + 175, cy + 90, cx + 330, cy + 330, 'annulus', G.prog(t, T['annulus'], 0.6),
                size=24, elbow=False)
        G.label(ctx, cx - 60, cy + 40, cx - 330, cy + 330, 'inside the casing', G.prog(t, T['cross'], 0.6),
                size=24, align='right', elbow=False)
        rr = G.prog(t, T['r2r'] - 0.2, 0.8)
        if rr > 0:
            G.arrow(ctx, cx, cy, cx - 300 * rr, cy, P.GOOD, 7, 22, 1, a)
            G.arrow(ctx, cx, cy, cx + 300 * rr, cy, P.GOOD, 7, 22, 1, a)
            G.tag(ctx, 'ROCK TO ROCK', cx, cy - 40, rr * a, bg=P.GOOD, size=32, align='center')

    def channel(self, ctx, t, a):
        T = self.T
        x0, y0 = 930, 150
        G.panel(ctx, x0, y0, 840, 820, a)
        G.text(ctx, 'THE HIDDEN PROBLEM', x0 + 420, y0 + 80, 32, 'ExtraBold', P.KICK, 'center',
               alpha=a, tracking=0.1)
        from well2d import pattern
        cx, top, bot = x0 + 420, y0 + 130, y0 + 780
        ctx.save()
        ctx.rectangle(x0 + 40, top, 760, bot - top)
        ctx.clip()
        ctx.set_source(pattern('claystone2', 0.5))
        ctx.paint_with_alpha(a)
        ctx.restore()
        # annulus with patchy cement
        for sx in (-1, 1):
            xa = cx + sx * 110
            ctx.rectangle(min(xa, xa + sx * 70), top, 70, bot - top)
            ctx.save()
            ctx.clip()
            ctx.set_source(pattern('cement', 0.4))
            ctx.paint_with_alpha(a)
            ctx.restore()
        # channel on the right side
        G.rect(ctx, cx + 110, top, 34, bot - top, fill=P.MUD, alpha=a)
        # casing
        for sx in (-1, 1):
            G.rect(ctx, cx + sx * 110 - (12 if sx > 0 else 0), top, 12, bot - top, fill=P.STEEL_DARK,
                   alpha=a)
        G.rect(ctx, cx - 98, top, 196, bot - top, fill='#9FD3E8', alpha=a)
        # plug inside
        ctx.rectangle(cx - 98, top + 250, 196, 200)
        ctx.save()
        ctx.clip()
        ctx.set_source(pattern('cement', 0.4))
        ctx.paint_with_alpha(a)
        ctx.restore()
        G.label(ctx, cx - 40, top + 350, cx - 250, top + 330, 'plug inside the casing',
                G.prog(t, T['tricky'], 0.6), size=24, align='right', elbow=False)
        sn = G.prog(t, T['sneak'] - 0.6, 0.6)
        if sn > 0:
            for k in range(6):
                ph = (t * 0.6 + k / 6) % 1.0
                y = bot - ph * (bot - top)
                G.arrow(ctx, cx + 127, y + 25, cx + 127, y - 25, P.KICK, 6, 16, 1, a * sn)
            G.label(ctx, cx + 144, top + 120, cx + 230, top + 80, 'leak path outside!', sn,
                    col=P.WHITE, bg=P.KICK, size=24, elbow=False)
        ms = G.prog(t, T['missing'] - 0.2, 0.6)
        G.label(ctx, cx + 144, bot - 120, cx + 240, bot - 60, 'missing / poor cement', ms,
                size=24, elbow=False)

    def remedies(self, ctx, t, a):
        T = self.T
        from well2d import pattern
        G.panel(ctx, 930, 150, 840, 820, a)
        for k, (title, t0) in enumerate((('SECTION MILLING', T['milled']),
                                          ('PERFORATE · WASH · CEMENT', T['perforated']))):
            p = G.prog(t, t0 - 0.3, 0.6)
            cx = 1140 + k * 420
            top, bot = 290, 900
            G.text(ctx, title, cx, 240, 24, 'ExtraBold', PA_COL, 'center', alpha=a * p,
                   tracking=0.06)
            ctx.save()
            ctx.rectangle(cx - 190, top, 380, bot - top)
            ctx.clip()
            ctx.set_source(pattern('claystone2', 0.5))
            ctx.paint_with_alpha(a * p)
            # poor annulus
            G.rect(ctx, cx - 110, top, 40, bot - top, fill=P.MUD, alpha=a * p)
            G.rect(ctx, cx + 70, top, 40, bot - top, fill=P.MUD, alpha=a * p)
            G.rect(ctx, cx - 70, top, 140, bot - top, fill='#9FD3E8', alpha=a * p)
            bond = G.prog(t, T['bonds'] - 0.6, 1.2)
            if k == 0:
                # casing removed over a window, cement fills rock to rock
                win0, win1 = 470, 720
                mill = G.prog(t, t0, 1.5)
                for sx in (-1, 1):
                    xx = cx + sx * 70 - (10 if sx > 0 else 0)
                    G.rect(ctx, xx, top, 10, win0 - top, fill=P.STEEL_DARK, alpha=a * p)
                    G.rect(ctx, xx, win1, 10, bot - win1, fill=P.STEEL_DARK, alpha=a * p)
                    G.rect(ctx, xx, win0, 10, (win1 - win0) * (1 - mill), fill=P.STEEL_DARK, alpha=a * p)
                if bond > 0:
                    hh = (win1 - win0) * bond
                    ctx.rectangle(cx - 110, win1 - hh, 220, hh)
                    ctx.save()
                    ctx.clip()
                    ctx.set_source(pattern('cement', 0.4))
                    ctx.paint_with_alpha(a)
                    ctx.restore()
            else:
                for sx in (-1, 1):
                    xx = cx + sx * 70 - (10 if sx > 0 else 0)
                    G.rect(ctx, xx, top, 10, bot - top, fill=P.STEEL_DARK, alpha=a * p)
                perf = G.prog(t, t0, 0.4)
                for j in range(6):
                    y = 480 + j * 40
                    for sx in (-1, 1):
                        G.line(ctx, [(cx + sx * 60, y), (cx + sx * (60 + 60 * perf), y)], '#1B1F24',
                               6, a * p)
                wash = G.window(t, t0 + 0.6, T['bonds'] - 0.5, 0.3)
                if wash > 0:
                    for j in range(6):
                        y = 480 + j * 40
                        ph = (t * 3 + j * 0.2) % 1.0
                        for sx in (-1, 1):
                            G.circle(ctx, cx + sx * (70 + 30 * ph), y, 6, fill='#FFFFFF',
                                     alpha=a * wash * (1 - ph))
                if bond > 0:
                    hh = 300 * bond
                    for xa, w_ in ((cx - 110, 40), (cx + 70, 40), (cx - 70, 140)):
                        ctx.rectangle(xa, 740 - hh, w_, hh)
                    ctx.save()
                    ctx.clip()
                    ctx.set_source(pattern('cement', 0.4))
                    ctx.paint_with_alpha(a)
                    ctx.restore()
            ctx.restore()
        bp = G.prog(t, T['bonds'] - 0.2, 0.6)
        if bp > 0:
            G.tag(ctx, 'NEW CEMENT BONDS TO THE FORMATION', 1350, 940, bp * a, bg=P.GOOD, size=26,
                  align='center')

    # ------------------------------------------------------------------ 3D labels
    def draw_3d_labels(self, ctx, t, A):
        T = self.T
        a = self.A
        pt = a(A, 'cut')
        if pt and t < self.t_dio:
            G.label(ctx, pt[0], pt[1], pt[0] + 260, pt[1] + 60, 'Casings cut ~5 m below seabed',
                    G.prog(t, T['cut'], 0.8), out=G.prog(t, T['lifted'] + 0.8, 0.4), size=30)
            wh = a(A, 'wh')
            if wh:
                G.label(ctx, wh[0], wh[1], wh[0] + 240, wh[1] - 120, 'Wellhead recovered to surface',
                        G.prog(t, T['lifted'], 0.8), out=G.prog(t, self.t_dio - 0.6, 0.4), size=30)
        # flash to the diorama
        q = 1 - abs(t - self.t_dio) / 0.25
        if q > 0:
            ctx.set_source_rgba(1, 1, 1, 0.9 * q)
            ctx.paint()
        if t > self.t_dio:
            cq = [a(A, 'cap_q%d' % i) for i in range(4)]
            gl = G.prog(t, T['restored'] - 0.3, 1.0)
            O.glow_quad(ctx, cq, P.ACCENT, gl * (0.75 + 0.25 * math.sin(t * 2.5)))
            for key, txt, t0, off in (('p_prim', 'Primary plug', T['seabed'], (220, -40)),
                                      ('p_sec', 'Secondary plug', T['seabed'] + 0.4, (240, -60)),
                                      ('p_surf', 'Surface plug', T['seabed'] + 0.8, (240, 40))):
                pp = a(A, key)
                if pp:
                    G.label(ctx, pp[0], pp[1], pp[0] + off[0], pp[1] + off[1], txt, G.prog(t, t0, 0.7),
                            size=26, out=G.prog(t, T['lid'] - 0.3, 0.5))
            lp = G.prog(t, T['lid'] - 0.3, 0.8)
            if lp > 0:
                G.tag(ctx, "NATURE'S LID IS BACK IN PLACE", 960, 150, lp, bg=P.ACCENT, size=40,
                      align='center')
            sb = G.window(t, T['seabed'] - 0.3, T['restored'] - 0.2, 0.4)
            pt = a(A, 'seabed')
            if pt and sb > 0:
                G.label(ctx, pt[0], pt[1], pt[0] + 200, pt[1] - 120, 'Just the seabed', sb, size=30)
