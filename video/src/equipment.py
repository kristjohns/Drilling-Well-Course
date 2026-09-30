"""Procedural subsea equipment, rig and downhole tools (units: metres)."""
import math
import random

import bpy
from mathutils import Vector

import bl
import palette as P

TAU = math.tau


def mats():
    return dict(
        steel=bl.mat('eq_steel', '#9AA7B4', rough=0.3, metal=0.6),
        steel_dark=bl.mat('eq_steel_dark', '#5E6B78', rough=0.35, metal=0.6),
        cut=bl.mat('eq_cut', '#D5DDE5', rough=0.6),
        bop=bl.mat('eq_bop', P.BOP, rough=0.45),
        bop_body=bl.mat('eq_bop_body', '#707E8C', rough=0.35, metal=0.5),
        bop_dark=bl.mat('eq_bop_dark', '#3F4A55', rough=0.4, metal=0.4),
        rubber=bl.mat('eq_rubber', '#2A2E33', rough=0.8),
        packer=bl.mat('eq_packer', '#B23A2E', rough=0.7),
        ram=bl.mat('eq_ram', '#C9D2DB', rough=0.3, metal=0.6),
        blade=bl.mat('eq_blade', '#E8EDF2', rough=0.2, metal=0.8),
        xt=bl.mat('eq_xt', P.XT, rough=0.45),
        xt_dark=bl.mat('eq_xt_dark', P.XT_DARK, rough=0.45),
        yellow=bl.mat('eq_yellow', P.RIG_YELLOW, rough=0.45),
        blue=bl.mat('eq_blue', '#2F6FB5', rough=0.45),
        red=bl.mat('eq_red', P.RIG_RED, rough=0.45),
        white=bl.mat('eq_white', '#EEF1F4', rough=0.5),
        grey=bl.mat('eq_grey', '#A9B3BD', rough=0.5),
        dark=bl.mat('eq_dark', P.RIG_DARK, rough=0.5),
        pipe=bl.mat('eq_pipe', P.PIPE, rough=0.3, metal=0.6),
        glass=bl.mat('eq_glass', '#9FD3F0', rough=0.1),
        green=bl.mat('eq_green', '#3E8E5A', rough=0.5),
        orange=bl.mat('eq_orange', '#F07F2A', rough=0.45),
        black=bl.mat('eq_black', '#1C2126', rough=0.6),
    )


def _grp(name, objs, parent=None, loc=(0, 0, 0)):
    g = bl.empty(name, loc)
    for o in objs:
        if o is not None and o.parent is None:
            o.parent = g
    if parent:
        g.parent = parent
    return g


# ================================================================== wellhead

def wellhead(M, cut=False, stickup=True, conductor_depth=25.0, with_pgb=True):
    """Conductor + LP housing + HP housing. Origin at seabed (z=0), well axis = Z.

    Returns dict with objects; 'top' is the HP housing top height (m).
    """
    a0, a1 = (0.0, math.pi) if cut else (0.0, TAU)
    cm = M['cut'] if cut else None
    o = {}
    o['conductor'] = bl.annulus('conductor', 0.355, 0.381, -conductor_depth, 1.2, a0, a1, 64,
                                M['steel'], cm)
    lp = [(0.355, 0.9), (0.52, 0.9), (0.52, 1.0), (0.46, 1.1), (0.46, 1.75), (0.40, 1.85),
          (0.355, 1.85)]
    o['lp'] = bl.revolve('lp_housing', lp, 64, a0, a1, M['steel_dark'], cm)
    hp = [(0.24, -2.0), (0.30, -2.0), (0.30, 1.7), (0.36, 1.8), (0.36, 2.95), (0.42, 3.0),
          (0.42, 3.05), (0.36, 3.1), (0.36, 3.25), (0.42, 3.3), (0.42, 3.35), (0.36, 3.4),
          (0.36, 3.55), (0.30, 3.6), (0.24, 3.6)]
    o['hp'] = bl.revolve('hp_housing', hp, 64, a0, a1, M['steel'], cm)
    o['top'] = 3.6
    if with_pgb:
        parts = []
        s = 1.9
        for x in (-s, s):
            parts.append(bl.box('pgb_b', (0.22, 2 * s + 0.22, 0.3), loc=(x, 0, 1.05),
                                material=M['yellow']))
        for y in (-s, s):
            parts.append(bl.box('pgb_b', (2 * s, 0.22, 0.3), loc=(0, y, 1.05),
                                material=M['yellow']))
        for x, y in ((-s, -s), (s, -s), (-s, s), (s, s)):
            parts.append(bl.rod('pgb_d', (x, y, 1.05), (0, 0, 1.4), 0.07, M['yellow'], 8))
            parts.append(bl.cyl('pgb_leg', 0.16, 1.2, loc=(x, y, 0.5), material=M['yellow'],
                                seg=16))
        pgb = bl.join(parts, 'pgb')
        if cut:
            bl.cut_half(pgb, M['cut'])
        o['pgb'] = pgb
    return o


# ================================================================== BOP stack

class BOP:
    """Subsea BOP stack. Origin = bottom of the wellhead connector.

    With cut=True the pressure-containing bodies are sectioned (y >= 0 kept)
    so rams and annular packers can be animated inside.
    """

    RAM_Z = (2.2, 3.5, 4.8)          # cavity centre heights: pipe, pipe, blind shear
    ANN_Z = (6.2, 9.4)              # annular preventers (lower, upper)
    HEIGHT = 12.8

    def __init__(self, M, cut=False, pipe_r=0.085, frame=True, name='BOP'):
        self.M = M
        self.cut = cut
        self.root = bl.empty(name)
        self.parts = []
        self.rams = {}
        self.packers = []
        a0, a1 = (0.0, math.pi) if cut else (0.0, TAU)
        cm = M['cut'] if cut else None
        bore = 0.24
        # wellhead connector
        con = [(bore, 0), (0.95, 0), (0.95, 0.25), (0.8, 0.35), (0.8, 1.2), (0.62, 1.4),
               (bore, 1.4)]
        self._add(bl.revolve('bop_conn', con, 64, a0, a1, M['bop_dark'], cm))
        # studded flange rings
        for z in (1.4, 5.5):
            self._add(bl.annulus('bop_flange', bore, 0.72, z, z + 0.2, a0, a1, 64,
                                 M['bop_body'], cm))
        # ram bodies
        for i, zc in enumerate(self.RAM_Z):
            self._ram_body(zc, bore, i)
        # annulars
        for k, zc in enumerate(self.ANN_Z):
            prof = [(bore, zc - 0.8), (0.85, zc - 0.8), (0.95, zc - 0.5), (0.95, zc + 0.2),
                    (0.75, zc + 0.7), (0.45, zc + 0.9), (bore, zc + 0.9)]
            body = bl.revolve('annular_%d' % k, prof, 64, a0, a1, M['bop_dark'], cm)
            self._add(body)
            if cut:
                # packing element: rubber doughnut in a cavity
                pk = [(bore + 0.02, zc - 0.25), (0.62, zc - 0.25), (0.62, zc + 0.35),
                      (bore + 0.02, zc + 0.35)]
                inner = bl.revolve('ann_cavity', pk, 64, a0, a1, M['bop_dark'], M['cut'])
                # represent cavity by recolouring: packer drawn slightly proud of the cut face
                bpy.data.objects.remove(inner, do_unlink=True)
                pack = bl.revolve('packer_%d' % k,
                                  [(bore + 0.005, zc - 0.22), (0.58, zc - 0.22), (0.58, zc + 0.32),
                                   (bore + 0.005, zc + 0.32)], 64, a0, a1, M['packer'], M['packer'])
                pack.location.y = -0.004
                self._add(pack)
                self.packers.append(pack)
        # LMRP connector + flex joint + riser adapter
        lm = [(bore, 7.3), (0.9, 7.3), (0.9, 8.3), (0.6, 8.5), (bore, 8.5)]
        self._add(bl.revolve('lmrp_conn', lm, 64, a0, a1, M['bop_body'], cm))
        fj = [(bore, 10.3), (0.7, 10.3), (0.75, 10.8), (0.5, 11.6), (0.34, 12.8), (bore, 12.8)]
        self._add(bl.revolve('flex_joint', fj, 64, a0, a1, M['bop_body'], cm))
        if frame:
            self._frame()
        for o in self.parts:
            o.parent = self.root

    def _add(self, o):
        self.parts.append(o)
        return o

    def _ram_body(self, zc, bore, i):
        M = self.M
        h, hx, hy = 1.1, 0.75, 0.62
        body = bl.box('ram_body_%d' % i, (2 * hx, 2 * hy, h), loc=(0, 0, zc),
                      material=M['bop_body'])
        cav = bl.box('_cav', (2 * hx + 0.1, 0.62, 0.38), loc=(0, 0, zc), material=M['cut'])
        bl.boolean(body, cav)
        cyl = bl.cyl('_bore', bore, 3.0, loc=(0, 0, zc), material=M['cut'], seg=48)
        bl.boolean(body, cyl)
        if self.cut:
            bl.cut_half(body, M['cut'])
        self._add(body)
        # bonnets and operators on both sides
        for s in (-1, 1):
            bon = bl.cyl('bonnet', 0.46, 0.7, loc=(s * (hx + 0.35), 0, zc),
                         rot=(0, math.pi / 2, 0), material=M['bop'], seg=40)
            op = bl.cyl('operator', 0.56, 0.5, loc=(s * (hx + 0.95), 0, zc),
                        rot=(0, math.pi / 2, 0), material=M['bop_body'], seg=40)
            cap = bl.cyl('opcap', 0.3, 0.25, loc=(s * (hx + 1.32), 0, zc),
                         rot=(0, math.pi / 2, 0), material=M['bop_dark'], seg=24)
            for o in (bon, op, cap):
                if self.cut:
                    bl.cut_half(o, M['cut'])
                self._add(o)
        # ram blocks (only needed for the cutaway animation)
        if self.cut:
            kind = 'shear' if i == 2 else 'pipe'
            blocks = []
            for s in (-1, 1):
                blk = self._ram_block(zc, s, kind, i)
                blocks.append(blk)
            self.rams[i] = (kind, blocks)

    def _ram_block(self, zc, s, kind, i):
        """Ram block on side s (+1 = right). Origin at its retracted position."""
        M = self.M
        L, W, Hh = 0.52, 0.56, 0.34
        blk = bl.box('ram_%d_%d' % (i, s), (L, W, Hh), loc=(s * (0.26 + L / 2), 0, zc),
                     material=M['ram'])
        if kind == 'pipe':
            notch = bl.cyl('_notch', 0.09, 1.0, loc=(0, 0, zc), material=M['rubber'], seg=32)
            bl.boolean(blk, notch)
            # rubber face seal
            seal = bl.box('ram_seal', (0.05, W, Hh * 0.98), loc=(s * (0.26 + 0.025), 0, zc),
                          material=M['rubber'])
            n2 = bl.cyl('_notch2', 0.09, 1.0, loc=(0, 0, zc), material=M['rubber'], seg=32)
            bl.boolean(seal, n2)
            blk = bl.join([blk, seal])
        else:
            # shear blade: a wedge that overlaps the opposite blade vertically
            dz = 0.06 * s
            blade = bl.box('blade', (0.14, W, Hh * 0.5), loc=(s * (0.26 + 0.07) - s * 0.10, 0,
                                                               zc + dz),
                           material=M['blade'])
            blk.location.z += 0
            blk = bl.join([blk, blade])
        bl.cut_half(blk, M['cut'])
        blk.name = 'ram_%d_%d' % (i, s)
        blk.parent = self.root
        self.parts.append(blk)
        return blk

    def _frame(self):
        M = self.M
        s = 2.1
        parts = []
        for x, y in ((-s, -s), (s, -s), (-s, s), (s, s)):
            parts.append(bl.box('bf_post', (0.22, 0.22, 11.0), loc=(x, y, 5.5),
                                material=M['bop']))
        for z in (0.2, 5.6, 7.2, 10.2):
            for x in (-s, s):
                parts.append(bl.box('bf_b', (0.18, 2 * s, 0.18), loc=(x, 0, z), material=M['bop']))
            for y in (-s, s):
                parts.append(bl.box('bf_b', (2 * s, 0.18, 0.18), loc=(0, y, z), material=M['bop']))
        # accumulator bottles
        for k in range(6):
            x = -1.5 + k * 0.6
            for y in (s - 0.45,):
                parts.append(bl.cyl('accu', 0.24, 2.0, loc=(x, y, 8.5), material=M['yellow'],
                                    seg=20))
        frame = bl.join(parts, 'bop_frame')
        if self.cut:
            bl.cut_half(frame, M['cut'])
        frame.parent = self.root
        self.parts.append(frame)
        # choke & kill lines (behind, so visible in cutaway)
        for x in (-1.25, 1.25):
            ln = bl.cyl('ck_line', 0.07, 11.5, loc=(x, 1.05, 6.4), material=M['steel'], seg=12)
            ln.parent = self.root
            self.parts.append(ln)
        # control pods
        for x, mat in ((-1.3, M['blue']), (1.3, M['yellow'])):
            pod = bl.box('pod', (0.8, 0.8, 1.6), loc=(x, 1.55 if self.cut else -1.55, 11.2),
                         material=mat, bevel=0.05)
            pod.parent = self.root
            self.parts.append(pod)

    # ---------------------------------------------------------------- animation
    def close_ram(self, i, f0, f1, stroke=None):
        kind, blocks = self.rams[i]
        stroke = stroke if stroke is not None else 0.26
        for blk in blocks:
            s = 1 if blk.location.x > 0 else -1
            x0 = blk.location.x
            bl.key(blk, 'location', f0, Vector((x0, blk.location.y, blk.location.z)))
            bl.key(blk, 'location', f1, Vector((x0 - s * stroke, blk.location.y, blk.location.z)))
            blk.location.x = x0

    def squeeze_annular(self, k, f0, f1, amount=0.62):
        pk = self.packers[k]
        bl.key(pk, 'scale', f0, (1, 1, 1))
        bl.key(pk, 'scale', f1, (amount, amount, 1.0))


def riser(M, z0, z1, name='riser', cut=False, buoyancy=True, joint=22.86):
    """Marine riser from z0 up to z1 along the Z axis with buoyancy modules."""
    parts = []
    a0, a1 = (0, math.pi) if cut else (0, TAU)
    parts.append(bl.annulus(name + '_pipe', 0.24, 0.27, z0, z1, a0, a1, 48, M['steel'],
                            M['cut'] if cut else None))
    if buoyancy:
        z = z0 + 3
        while z + joint * 0.8 < z1:
            parts.append(bl.annulus(name + '_buoy', 0.27, 0.62, z, z + joint * 0.85, a0, a1, 48,
                                    M['white'], M['cut'] if cut else None))
            parts.append(bl.annulus(name + '_flange', 0.27, 0.45, z + joint * 0.9, z + joint,
                                    a0, a1, 32, M['steel_dark'], None))
            z += joint
    for x in (-0.5, 0.5):
        parts.append(bl.cyl(name + '_ck', 0.06, z1 - z0, loc=(x, 0.55, (z0 + z1) / 2),
                            material=M['steel_dark'], seg=10))
    return bl.join(parts, name)


# ================================================================== christmas tree

def xmas_tree(M, name='XT'):
    """Subsea horizontal-style christmas tree. Origin = bottom of tree connector."""
    root = bl.empty(name)
    parts = []
    parts.append(bl.revolve('xt_conn', [(0.2, 0), (0.95, 0), (0.95, 1.0), (0.7, 1.2),
                                        (0.2, 1.2)], 48, material=M['steel_dark']))
    body = bl.box('xt_body', (1.4, 1.4, 2.2), loc=(0, 0, 2.3), material=M['steel'], bevel=0.04)
    parts.append(body)
    # production wing branch (+X) with valves and choke
    parts.append(bl.cyl('xt_wing', 0.2, 2.2, loc=(1.8, 0, 2.6), rot=(0, math.pi / 2, 0),
                        material=M['steel'], seg=24))
    for k, x in enumerate((1.05, 1.75)):
        vb = bl.box('xt_valve', (0.5, 0.6, 0.6), loc=(x, 0, 2.6), material=M['steel_dark'],
                    bevel=0.03)
        act = bl.cyl('xt_act', 0.2, 0.7, loc=(x, 0, 3.2), material=M['yellow'], seg=20)
        parts += [vb, act]
    choke = bl.box('xt_choke', (0.7, 0.7, 0.9), loc=(2.5, 0, 2.9), material=M['xt_dark'],
                   bevel=0.04)
    parts.append(choke)
    hub = bl.revolve('xt_hub', [(0.1, 0), (0.33, 0), (0.33, 0.35), (0.25, 0.45), (0.1, 0.45)],
                     32, material=M['steel_dark'])
    hub.rotation_euler = (0, math.pi / 2, 0)
    hub.location = (2.9, 0, 2.6)
    parts.append(hub)
    # annulus side (-X)
    parts.append(bl.cyl('xt_ann', 0.14, 1.2, loc=(-1.2, 0, 2.0), rot=(0, math.pi / 2, 0),
                        material=M['steel'], seg=20))
    parts.append(bl.box('xt_aval', (0.4, 0.5, 0.5), loc=(-1.2, 0, 2.0), material=M['steel_dark']))
    parts.append(bl.cyl('xt_aact', 0.16, 0.5, loc=(-1.2, 0, 2.45), material=M['yellow'], seg=16))
    # tree cap
    parts.append(bl.revolve('xt_cap', [(0.0, 3.4), (0.62, 3.4), (0.62, 3.9), (0.45, 4.1),
                                       (0.0, 4.1)], 40, material=M['xt_dark']))
    # SCM (control module)
    parts.append(bl.box('xt_scm', (0.9, 0.7, 1.3), loc=(-0.9, 1.25, 3.0), material=M['yellow'],
                        bevel=0.05))
    # frame
    s = 1.9
    fr = []
    for x, y in ((-s, -s), (s, -s), (-s, s), (s, s)):
        fr.append(bl.box('xtf_post', (0.18, 0.18, 4.2), loc=(x, y, 2.1), material=M['xt']))
    for z in (0.15, 4.2):
        for x in (-s, s):
            fr.append(bl.box('xtf_b', (0.16, 2 * s, 0.16), loc=(x, 0, z), material=M['xt']))
        for y in (-s, s):
            fr.append(bl.box('xtf_b', (2 * s, 0.16, 0.16), loc=(0, y, z), material=M['xt']))
    # diagonal braces on the sides
    for y in (-s, s):
        fr.append(bl.rod('xtf_d', (-s, y, 0.15), (s, y, 4.2), 0.06, M['xt'], 8))
    # ROV panel
    fr.append(bl.box('xt_panel', (1.8, 0.12, 1.0), loc=(0, -s, 1.4), material=M['grey']))
    for k in range(4):
        fr.append(bl.cyl('xt_knob', 0.1, 0.12, loc=(-0.6 + k * 0.4, -s - 0.08, 1.4),
                         rot=(math.pi / 2, 0, 0), material=M['yellow'] if k % 2 else M['red'],
                         seg=16))
    parts.append(bl.join(fr, 'xt_frame'))
    for p in parts:
        p.parent = root
    return root


# ================================================================== manifold

def manifold(M, name='manifold', size=(12, 9, 4.5)):
    """Protective template / manifold structure with sloped (trawl-friendly) roof."""
    sx, sy, h = size
    parts = []
    # base
    parts.append(bl.box('mf_base', (sx, sy, 0.5), loc=(0, 0, 0.25), material=M['xt_dark']))
    # corner posts
    for x in (-sx / 2, sx / 2):
        for y in (-sy / 2, sy / 2):
            parts.append(bl.box('mf_post', (0.35, 0.35, h), loc=(x, y, h / 2), material=M['yellow']))
    # sloped roof panels
    for s in (-1, 1):
        pan = bl.box('mf_roof', (sx, sy / 2 + 0.6, 0.18), loc=(0, s * sy / 4, h + 0.4),
                     rot=(s * 0.22, 0, 0), material=M['yellow'])
        parts.append(pan)
    for x in (-sx / 2, sx / 2):
        parts.append(bl.box('mf_end', (0.18, sy, h * 0.6), loc=(x, 0, h * 0.55), material=M['yellow']))
    # headers (pipes) inside
    for y in (-1.0, 1.0):
        parts.append(bl.cyl('mf_header', 0.28, sx - 1, loc=(0, y, 1.3), rot=(0, math.pi / 2, 0),
                            material=M['steel'], seg=24))
    for x in (-3, 0, 3):
        parts.append(bl.box('mf_valve', (0.6, 0.6, 0.8), loc=(x, 0, 1.6), material=M['steel_dark']))
        parts.append(bl.cyl('mf_act', 0.18, 0.6, loc=(x, 0, 2.3), material=M['orange'], seg=16))
    return bl.join(parts, name)


# ================================================================== ROV

def rov(M, name='ROV'):
    root = bl.empty(name)
    parts = [
        bl.box('rov_float', (2.6, 1.7, 0.7), loc=(0, 0, 1.25), material=M['yellow'], bevel=0.12),
        bl.box('rov_frame', (2.5, 1.6, 0.9), loc=(0, 0, 0.45), material=M['black'], bevel=0.05),
    ]
    for x in (-0.9, 0.9):
        for y in (-0.95, 0.95):
            parts.append(bl.annulus('rov_thr', 0.2, 0.24, -0.25, 0.25, material=M['dark'],
                                    loc=(x, y, 0.5)))
    parts.append(bl.cyl('rov_vthr', 0.22, 0.3, loc=(0, 0, 1.7), material=M['dark'], seg=20))
    for y in (-0.4, 0.4):
        parts.append(bl.sphere('rov_light', 0.1, loc=(1.3, y, 1.0), material=M['white']))
    parts.append(bl.box('rov_cam', (0.3, 0.3, 0.25), loc=(1.3, 0, 0.6), material=M['dark']))
    # manipulator arms
    parts.append(bl.rod('rov_arm', (1.25, -0.5, 0.2), (1.9, -0.6, 0.0), 0.06, M['steel'], 10))
    parts.append(bl.rod('rov_arm2', (1.9, -0.6, 0.0), (2.3, -0.5, -0.3), 0.05, M['steel'], 10))
    parts.append(bl.rod('rov_arm3', (1.25, 0.5, 0.2), (1.8, 0.6, -0.2), 0.06, M['steel'], 10))
    for p in parts:
        p.parent = root
    return root


# ================================================================== semi-submersible rig

def semisub(M, name='Rig'):
    """Semi-submersible drilling rig. Origin at the waterline, well centre (moonpool)."""
    root = bl.empty(name)
    parts = []
    hull = bl.mat('rig_hull', '#B7392F', rough=0.5)
    col_m = bl.mat('rig_col', '#F0F2F4', rough=0.45)
    deck_m = bl.mat('rig_deck', '#C9D0D6', rough=0.5)
    der_m = bl.mat('rig_derrick', '#F2F2EE', rough=0.4)
    # pontoons (below water)
    for y in (-30, 30):
        parts.append(bl.box('pontoon', (104, 17, 9), loc=(0, y, -17.5), material=hull, bevel=2.5))
    # columns
    for x in (-38, 0, 38):
        for y in (-30, 30):
            c = bl.cyl('column', 7.5, 34, loc=(x, y, 0), material=col_m, seg=40)
            band = bl.annulus('col_band', 7.45, 7.6, -13, 1.5, material=hull, loc=(x, y, 0),
                              seg=40)
            parts += [c, band]
    # braces
    for x in (-38, 0, 38):
        parts.append(bl.cyl('brace', 1.4, 60, loc=(x, 0, -8), rot=(math.pi / 2, 0, 0),
                            material=col_m, seg=16))
    # deck box
    parts.append(bl.box('deck', (92, 78, 9), loc=(0, 0, 21.5), material=deck_m, bevel=0.8))
    parts.append(bl.box('deck_top', (92, 78, 0.6), loc=(0, 0, 26.3), material=bl.mat('rig_decktop', '#8C969F')))
    # living quarters
    for k in range(4):
        lq = bl.box('lq', (22, 26 - k * 2, 3.2), loc=(-33, 22, 28.3 + k * 3.3), material=M['white'],
                    bevel=0.2)
        win = bl.box('lq_win', (22.2, 26.2 - k * 2, 0.9), loc=(-33, 22, 28.6 + k * 3.3),
                     material=bl.mat('rig_win', '#2F4B66'))
        parts += [lq, win]
    # helideck
    heli = bl.cyl('helideck', 12.5, 0.8, loc=(-38, 26, 42.5), material=bl.mat('rig_heli', '#4F7F5E'),
                  seg=8)
    parts.append(heli)
    parts.append(bl.annulus('heli_ring', 5, 6, 42.9, 43.0, material=M['yellow'], loc=(-38, 26, 0),
                            seg=32))
    for dx, dy in ((-6, -6), (6, -6), (0, 8)):
        parts.append(bl.rod('heli_leg', (-38 + dx, 26 + dy, 42), (-38 + dx * 0.6, 20 + dy * 0.3, 40.8),
                            0.5, M['grey'], 8))
    # pipe deck, modules
    parts.append(bl.box('pipe_rack', (30, 16, 2.5), loc=(20, -25, 28), material=M['dark']))
    for k in range(6):
        parts.append(bl.cyl('pipes', 0.8, 28, loc=(20, -31 + k * 2.2, 29.8),
                            rot=(0, math.pi / 2, 0), material=M['steel'], seg=12))
    parts.append(bl.box('module', (18, 14, 7), loc=(30, 18, 30), material=M['grey'], bevel=0.3))
    parts.append(bl.box('module2', (14, 12, 5), loc=(-5, -28, 29), material=M['white'], bevel=0.3))
    # lifeboats
    for k in range(3):
        parts.append(bl.box('lifeboat', (6, 2.5, 2.5), loc=(-47, -10 + k * 7, 25), material=M['orange'],
                            bevel=0.9))
    # cranes
    for (x, y, rot) in ((40, -34, 0.6), (-20, -36, 2.5)):
        parts.append(bl.cyl('crane_ped', 1.8, 12, loc=(x, y, 32), material=M['yellow'], seg=20))
        parts.append(bl.box('crane_cab', (4, 4, 3.5), loc=(x, y, 39.5), material=M['yellow']))
        boom_end = (x + 38 * math.cos(rot), y + 38 * math.sin(rot), 58)
        parts.append(bl.rod('crane_boom', (x, y, 40), boom_end, 0.9, M['yellow'], 8))
    # drill floor & substructure
    parts.append(bl.box('substructure', (16, 16, 8), loc=(0, 0, 30), material=M['grey']))
    parts.append(bl.box('drill_floor', (18, 18, 1.0), loc=(0, 0, 34.5), material=M['dark']))
    parts.append(bl.box('doghouse', (6, 5, 4), loc=(-9, -9, 37), material=M['white']))
    rig = bl.join(parts, name + '_body')
    rig.parent = root
    # derrick (lattice)
    derrick = lattice_tower('derrick', 13, 4, 58, levels=10, r=0.35, material=der_m)
    derrick.location = (0, 0, 35)
    derrick.parent = root
    crown = bl.box('crown', (6, 6, 3), loc=(0, 0, 94), material=M['yellow'])
    crown.parent = root
    return root, rig, derrick


def lattice_tower(name, base_w, top_w, height, levels=8, r=0.03, material=None):
    parts = []

    def corners(w, z):
        return [(-w / 2, -w / 2, z), (w / 2, -w / 2, z), (w / 2, w / 2, z), (-w / 2, w / 2, z)]
    lv = []
    for k in range(levels + 1):
        z = height * k / levels
        w = base_w + (top_w - base_w) * k / levels
        lv.append(corners(w, z))
    for k in range(levels):
        for c in range(4):
            p0, p1 = lv[k][c], lv[k + 1][c]
            q0, q1 = lv[k][(c + 1) % 4], lv[k + 1][(c + 1) % 4]
            parts.append(bl.rod(name + '_leg', p0, p1, r * 1.8, material, seg=8))
            parts.append(bl.rod(name + '_br', p0, q1, r * 0.8, material, seg=6))
            parts.append(bl.rod(name + '_br2', q0, p1, r * 0.8, material, seg=6))
            parts.append(bl.rod(name + '_h', p1, q1, r, material, seg=6))
    return bl.join(parts, name)


def top_drive(M):
    root = bl.empty('TopDrive')
    parts = [bl.box('td_body', (2.4, 2.0, 4.5), loc=(0, 0, 2.25), material=M['yellow'], bevel=0.15),
             bl.box('td_motor', (1.6, 1.6, 1.6), loc=(0, 0, 5.3), material=M['red'], bevel=0.1),
             bl.cyl('td_shaft', 0.3, 1.5, loc=(0, 0, -0.6), material=M['steel'], seg=16)]
    # travelling block + hook
    parts.append(bl.box('tblock', (2.0, 1.2, 2.2), loc=(0, 0, 7.4), material=M['yellow'], bevel=0.1))
    for p in parts:
        p.parent = root
    return root


# ================================================================== FPSO (distant)

def fpso(M, name='FPSO', L=260, B=48):
    parts = []
    hull = bl.mat('fpso_hull', '#35414D', rough=0.5)
    hullr = bl.mat('fpso_hullr', '#9E3A30', rough=0.5)
    parts.append(bl.box('fpso_hull', (L, B, 26), loc=(0, 0, 4), material=hull, bevel=3))
    parts.append(bl.box('fpso_boot', (L + 0.5, B + 0.5, 8), loc=(0, 0, -6), material=hullr, bevel=2))
    rnd = random.Random(4)
    for k in range(9):
        x = -L / 2 + 40 + k * 22
        h = rnd.uniform(8, 18)
        parts.append(bl.box('topside', (18, B * 0.7, h), loc=(x, 0, 17 + h / 2),
                            material=M['grey'] if k % 2 else M['white'], bevel=0.5))
    parts.append(bl.box('fpso_lq', (26, B * 0.9, 20), loc=(L / 2 - 20, 0, 27), material=M['white']))
    parts.append(bl.cyl('fpso_turret', 12, 30, loc=(-L / 2 + 20, 0, 18), material=M['grey'], seg=24))
    parts.append(bl.rod('flare', (-L / 2 + 30, 0, 17), (-L / 2 + 10, 0, 90), 1.5, M['grey'], 8))
    return bl.join(parts, name)


# ================================================================== PDC bit

def pdc_bit(M, r=0.155, blades=6, name='PDC'):
    """PDC drill bit, face pointing down (-Z), origin at the bit face centre."""
    root = bl.empty(name)
    body_m = bl.mat('bit_body', '#56616D', rough=0.35, metal=0.6)
    blade_m = bl.mat('bit_blade', '#6F7C89', rough=0.35, metal=0.6)
    cutter_m = bl.mat('bit_cutter', '#2F353B', rough=0.4, metal=0.5)
    diamond_m = bl.mat('bit_diamond', '#F4F7FA', rough=0.1, metal=0.9)
    nozzle_m = bl.mat('bit_nozzle', '#1B1F24', rough=0.6)
    # body (crown + shank + pin)
    prof = [(0.001, 0.02), (r * 0.5, 0.035), (r * 0.8, 0.07), (r * 0.9, 0.14), (r * 0.9, 0.30),
            (r * 0.75, 0.36), (r * 0.75, 0.5), (r * 0.55, 0.52), (r * 0.5, 0.62), (r * 0.35, 0.75),
            (0.001, 0.75)]
    body = bl.revolve('bit_body', prof, 64, material=body_m)
    body.parent = root
    # blade profile (outside the body): from centre along the face and up the gauge
    parts = []
    face = [(0.02, 0.0), (r * 0.45, 0.012), (r * 0.8, 0.04), (r * 0.97, 0.09), (r, 0.14),
            (r, 0.30)]
    rng = random.Random(2)
    for b in range(blades):
        ang = b * TAU / blades
        span = 0.16 if b % 2 == 0 else 0.13
        rstart = 0.02 if b % 2 == 0 else r * 0.35
        prof_b = [(max(rstart, x), z) for x, z in face if x >= rstart - 1e-6]
        inner = [(x * 0.82 + 0.004, z + 0.05) for x, z in prof_b]
        outline = prof_b + inner[::-1]
        bl_obj = bl.revolve('blade', outline, 64, a0=ang, a1=ang + span, material=blade_m,
                            cap_material=blade_m, sharp_angle=30)
        parts.append(bl_obj)
        # cutters along the leading edge
        n = 7 if b % 2 == 0 else 5
        for k in range(n):
            tpos = k / (n - 1)
            x, z = _along(prof_b, 0.08 + 0.84 * tpos)
            a = ang + span - 0.01
            p = Vector((x * math.cos(a), x * math.sin(a), z + 0.012))
            tang = Vector((-math.sin(a), math.cos(a), 0))   # direction of rotation
            c = bl.annulus('cutter', 0, 0.0135, -0.012, 0.012, seg=20, material=cutter_m)
            c.location = p
            c.rotation_mode = 'QUATERNION'
            c.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(tang)
            d = bl.annulus('diamond', 0, 0.0132, 0.010, 0.0145, seg=20, material=diamond_m)
            d.location = p
            d.rotation_mode = 'QUATERNION'
            d.rotation_quaternion = c.rotation_quaternion
            parts += [c, d]
    # nozzles in the junk slots
    for b in range(blades):
        ang = (b + 0.55) * TAU / blades
        x = r * 0.45
        nz = bl.cyl('nozzle', 0.012, 0.01, loc=(x * math.cos(ang), x * math.sin(ang), 0.036),
                    material=nozzle_m, seg=16)
        parts.append(nz)
    j = bl.join(parts, name + '_blades')
    j.parent = root
    return root


def _along(prof, t):
    L = [0]
    for i in range(len(prof) - 1):
        L.append(L[-1] + math.dist(prof[i], prof[i + 1]))
    target = L[-1] * t
    for i in range(len(prof) - 1):
        if L[i] <= target <= L[i + 1]:
            k = (target - L[i]) / max(1e-9, L[i + 1] - L[i])
            return (prof[i][0] + (prof[i + 1][0] - prof[i][0]) * k,
                    prof[i][1] + (prof[i + 1][1] - prof[i][1]) * k)
    return prof[-1]


def drill_pipe(M, z0, z1, r=0.064, name='dp', joint=9.4, tj=True):
    parts = [bl.cyl(name, r, z1 - z0, loc=(0, 0, (z0 + z1) / 2), material=M['pipe'], seg=24)]
    if tj:
        z = z0 + joint
        while z < z1:
            parts.append(bl.cyl(name + '_tj', r * 1.35, 0.45, loc=(0, 0, z), material=M['steel'],
                                seg=24))
            z += joint
    return bl.join(parts, name)
