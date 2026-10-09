"""Ch 5: Coiled tubing: a pipe on a reel.

5.01 what it is: strip steel -> tube -> slanted butt welds -> reel; carry, push AND pump
5.02 the spread: reel, gooseneck, injector head, stripper, BOP stack, lubricator, tree, cabin, pump
5.03 the injector head: two endless gripper chains squeezed onto the tube (they really move)
5.04 the stripper and the quad BOP: blind, shear, slip, pipe rams; the emergency sequence
5.05 the bottom hole assembly: connector, check valves, disconnect, working tool
5.06 the force balance: pressure pushes the tube out (4.1 t), weight grows, the balance point at ~1,035 m
5.07 fatigue: bending cycles over the reel and gooseneck, strain versus yield, life tracked and retired at ~80 %
5.08 reach: buckling (sine -> helix -> lock-up), reach versus friction (from the model), remedies
5.09 circulation: cleaning out sand, annular velocity, foam, friction
5.10 three jobs: nitrogen lift, acid placement, scale removal (jet and mill on a motor)
5.11 more jobs, and coiled tubing drilling
"""
from __future__ import annotations
import math

from scenes.common import palette as P, model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common import kit as K
from scenes.common import ct as C

TITLE = "Coiled tubing: a pipe on a reel"


# ====================================================================================================== 5.01
def b501(st, tl):
    b = tl["5.01"]
    s = b.sent
    with st.span(b.start, b.end):
        # ---- strip coil, forming, the tube
        cx0, cy0 = -6.1, 1.4
        coil = K.drum(st, cx0, cy0, 0.95, turns=6, color=P.STEEL)
        strip = st.rect(cx0 + 0.95 + 1.0, cy0 - 0.7, 2.0, 0.05, P.STEEL, 0.5, role="steel")
        K.show(st, coil.all() + [strip], b.start + 0.3, None, 0.5)
        l_s = K.note(st, "flat steel strip", cx0 + 0.3, cy0 - 1.45, 0.2, P.MUTED, align="c")
        K.show(st, l_s, s[2], None, 0.4)
        # four forming stages (cross-sections) along y = 1.4
        sx = [-2.8, -1.4, 0.0, 1.4]
        r = 0.42
        stg = []
        stg.append([st.line([(sx[0] - 0.5, 1.4), (sx[0] + 0.5, 1.4)], P.STEEL, 0.07, 0.5)])
        stg.append([st.line(C.arc_pts(sx[1], 1.5, r, 200, 340, 24), P.STEEL, 0.07, 0.5)])
        stg.append([st.line(C.arc_pts(sx[2], 1.4, r, 120, 420, 36), P.STEEL, 0.07, 0.5)])
        spark = [st.line([(sx[3] + 0.0, 1.4 + r + 0.05), (sx[3] + 0.3 * math.cos(math.radians(a)), 1.4 + r + 0.05 + 0.3 * math.sin(math.radians(a)))], P.WARN, 0.05, 0.7)
                 for a in (30, 60, 90, 120, 150)]
        stg.append([st.ring(sx[3], 1.4, r, 0.07, P.STEEL, 0.5)] + spark)
        for i, g in enumerate(stg):
            K.show(st, g, s[2] + 0.3 * i + 0.2, None, 0.4)
        ft = K.note(st, "rolled into a tube,\nwelded along the seam", -0.7, 2.45, 0.2, P.MUTED, align="c")
        K.show(st, ft, s[2] + 0.3, None, 0.4)
        # ---- the slanted butt welds: two strips make one continuous length
        px0, px1, py = -3.4, 0.9, -0.5
        pa = st.rect((px0 + 0.9) / 2 + 0.0, py, 0.9 - px0 - 0.0, 0.7, "#9fb0c8", 0.45, role="steel")
        pb = st.rect((0.9 + px1) / 2, py, px1 - 0.9, 0.7, P.STEEL, 0.45, role="steel")
        weld = st.rect(0.9, py, 0.07, 0.95, P.WARN, 0.6, rot=-25, role="solid")
        wl = K.note(st, "strips welded end to end at a slant: one continuous length", -1.2, py - 0.75, 0.2, P.TEXT, align="c")
        K.show(st, [pa, pb, weld] + wl, b.word(2, "the strips are welded") - 0.2, None, 0.5)
        # ---- the reel fills up
        rx, ry, R = 4.5, 0.4, 1.6
        reel = K.drum(st, rx, ry, R, turns=7, color=P.STEEL)
        K.show(st, reel.body, s[0] + 0.5, None, 0.5)
        for i, t in enumerate(reel.turns):
            K.show(st, [t], s[1] + 0.2 * i, None, 0.4)
        st.counter(rx, ry - R - 0.55, s[1], s[1] + 2.5, 0, 5000, "{:,.0f} m on one reel", 0.28, P.WARN, 0.7, kind="mono")
        rl = K.note(st, "1.5 to over 7 km", rx, ry + R + 0.35, 0.22, P.TEXT, align="c")
        K.show(st, rl, s[1], None, 0.4)
        # ---- sizes and strength
        sz = K.tag(st, -3.0, 3.4, "1 to 3.5 inch", color=P.PRIMARY_B, fg=P.BG, size=0.24, z=0.9)
        K.show(st, sz, s[0] + 0.8, None, 0.5)
        ys = K.tag(st, 4.5, 3.4, "yield ≥ 80,000 psi (552 MPa)", color=P.SAFE, fg=P.BG, size=0.22, z=0.9)
        K.show(st, ys, s[3], None, 0.5)
        bend = K.note(st, "…and still bends round the reel", 4.5, 2.85, 0.2, P.MUTED, align="c")
        K.show(st, bend, b.word(3, "yet it bends"), None, 0.5)
        # ---- carry, push and pump
        cps = [("CARRY", s[5], P.MUTED, "a wireline can"), ("PUMP", s[4], P.PORE, "because it is a pipe"), ("PUSH", s[6], P.SAFE, "")]
        xs = [-4.5, -1.5, 1.5]
        pills = []
        for (nm, t, colr, sub), x in zip(cps, xs):
            pill = K.tag(st, x, -2.7, nm, color=colr, fg=P.BG, size=0.32, z=0.9)
            K.show(st, pill, t, None, 0.5)
            pills.append(pill)
        # the order in which they appear: PUMP (s4), CARRY (s5), then PUSH (s6); all turn green on the last sentence
        for pill in pills:
            st.recolor(pill[0], s[6] + 0.8, s[6] + 1.2, P.SAFE)
        fin = K.note(st, "a coiled tube can carry, push, and pump", -1.5, -3.4, 0.24, P.TEXT, align="c")
        K.show(st, fin, s[6], None, 0.5)


# ====================================================================================================== 5.02
def b502(st, tl):
    b = tl["5.02"]
    s = b.sent
    with st.span(b.start, b.end):
        rx, ry, R = -5.4, -1.0, 1.7
        reel = K.drum(st, rx, ry, R, turns=6, color=P.STEEL)
        hub = st.circle(rx, ry, 0.25, P.STEEL, 0.6, role="solid")
        deck = st.rect(0.0, -3.55, 15.0, 0.2, P.STEEL_DK, 0.3)
        # stack at x = 1.4, from the tree up to the injector; the gooseneck arcs over to the reel
        injx = 1.4
        Cx, Cy, Rg = injx - 1.2, 2.6, 1.2
        path = [(rx, ry + R * 0.92), (-3.8, 1.0), (-2.4, 1.9), (Cx - Rg + 0.0, Cy - 0.3), (Cx - Rg, Cy)] + C.arc_pts(Cx, Cy, Rg, 180, 0, 28)[1:] + [(injx, 1.8), (injx, -3.4)]
        tube = st.line(path, P.STEEL, 0.11, 0.55)
        inj = [st.rect(injx, 1.8, 1.8, 1.6, P.PANEL2, 0.45, role="card"), st.rect(injx - 0.42, 1.8, 0.18, 1.3, P.STEEL_DK, 0.5, role="solid"), st.rect(injx + 0.42, 1.8, 0.18, 1.3, P.STEEL_DK, 0.5, role="solid")]
        strip = C.stripper(st, injx, 0.7, w=1.5, h=0.6)
        bop = C.bop_quad(st, injx, 0.4, sec_h=0.4, w=1.6, tube_w=0.2)
        lub = [st.rect(injx, -1.65, 0.55, 0.9, P.STEEL, 0.45, role="steel"), st.rect(injx, -1.65, 0.22, 0.9, P.BG, 0.46)]
        tree = K.dry_tree(st, injx, -3.4, 0.6)
        cab = [st.rect(5.6, -2.75, 2.0, 1.2, "#2b3b57", 0.4, role="solid"), st.rect(5.6, -2.55, 1.2, 0.45, "#294a7a", 0.45, role="solid")]
        pump = [st.rect(-7.15, -3.0, 1.1, 0.9, "#2b3b57", 0.4, role="solid"), st.text("pump", -7.15, -3.0, 0.19, P.TEXT, 0.5)]
        hose = st.line([(-6.55, -2.95), (-5.6, -2.5), (rx, ry - 0.2)], P.SPACER, 0.05, 0.5)
        st.fade_in(reel.body + reel.turns + [hub, deck] + cab + pump + [hose] + inj + strip.parts + bop.body + lub + tree.parts + tree.gates, b.start + 0.2, 0.6)
        for nm in bop.names:
            sec = bop.sections[nm]
            st.fade_in([sec["left"], sec["right"]], b.start + 0.2, 0.6)
        st.fade_in([tube], b.start + 0.3, 0.1)
        st.draw_on(tube, s[1] + 0.2, s[2] + 2.5, "LINEAR")
        st.flow(path, s[5] + 0.3, b.end - 0.3, P.SPACER, n=22, speed=1.6, r=0.045)

        def lab(text, x, y, tx, ty, t, t1=None, align="l"):
            g = K.callout(st, text, x, y, tx, ty, size=0.21, align=align)
            K.show(st, g, t, t1, 0.4)
        lab("reel", -7.6, 1.5, rx - 0.9, ry + 1.2, b.word(1, "reel"), s[2])
        lab("gooseneck: a curved guide", -5.6, 3.6, Cx - 0.5, Cy + 1.05, b.word(2, "gooseneck"), s[3])
        lab("injector head", -3.4, 0.2, injx - 0.9, 1.5, b.word(2, "injector head"), s[3])
        lab("stripper", -1.6, 0.7, injx - 0.75, 0.7, b.word(3, "stripper"), s[4], align="r")
        lab("blowout preventers", -1.0, -0.45, injx - 0.85, -0.45, b.word(3, "blowout preventers"), s[4], align="r")
        lab("lubricator", -1.0, -1.65, injx - 0.3, -1.65, b.word(3, "lubricator"), s[4], align="r")
        lab("tree", -1.0, -2.75, injx - 0.45, -2.75, b.word(3, "tree"), s[4], align="r")
        cl = K.callout(st, "control cabin", 3.4, -1.45, 5.0, -2.2, size=0.21, align="l")
        K.show(st, cl, s[4], s[5], 0.4)
        cn = K.note(st, "pressure · depth · weight · pump rate", 3.4, -1.9, 0.19, P.MUTED, align="l")
        K.show(st, cn, s[4] + 0.3, s[5], 0.4)
        pl = K.callout(st, "pump: fluid to the centre of the reel", -7.7, -2.0, -7.0, -2.65, size=0.2, align="l")
        K.show(st, pl, b.word(5, "pump"), None, 0.4)


# ====================================================================================================== 5.03
def b503(st, tl):
    b = tl["5.03"]
    s = b.sent
    with st.span(b.start, b.end):
        t_in, t_out, t_hold = s[3], s[4], s[5]

        def ramp(x, w=0.5):
            return max(0.0, min(1.0, x / w))

        def speed(t):
            v = 0.0
            if t >= t_in:
                v += 0.9 * ramp(t - t_in)
            if t >= t_out:
                v -= 0.9 * ramp(t - t_out) + 0.9 * ramp(t - t_out)
            if t >= t_hold:
                v += 0.9 * ramp(t - t_hold)
            return v
        inj = C.injector(st, -3.3, 0.1, h=4.6, gap=0.6, rho=0.6, t0=b.start, t1=b.end, speed=speed)
        st.fade_in(inj.frame + inj.tube + inj.sprockets, b.start + 0.2, 0.5)
        # squeezing cylinders
        cyl = []
        for sd in (-1, 1):
            xx = (inj.left_x - 0.75) if sd < 0 else (inj.right_x + 0.75)
            cyl.append(st.rect(xx, 0.1, 0.5, 1.1, P.STEEL, 0.55, role="steel"))
            cyl += st.arrow(xx + (-0.5 if sd < 0 else 0.5), 0.1, xx + (0.5 if sd < 0 else -0.5), 0.1, P.PORE, 0.06, 0.2, 0.6)
        K.show(st, cyl, s[2] - 0.2, None, 0.5)
        # labels on the right
        rows = [("two endless chains", s[1]), ("gripper blocks shaped to the tube", b.word(1, "gripper blocks")),
                ("hydraulic cylinders squeeze the chains onto the pipe", s[2])]
        for i, (txt, t) in enumerate(rows):
            g = K.tag(st, -0.3, 2.6 - i * 0.65, txt, color=P.PANEL2, size=0.21, z=0.9, align="l")
            K.show(st, g, t, None, 0.4)
        d_in = K.tag(st, -0.3, 0.2, "chains down:  tube driven into the well", color=P.SAFE, fg=P.BG, size=0.24, z=0.9, align="l")
        d_out = K.tag(st, -0.3, -0.5, "chains up:  tube pulled out", color=P.PRIMARY_B, fg=P.BG, size=0.24, z=0.9, align="l")
        d_hold = K.tag(st, -0.3, -1.2, "holds still against 200 bar", color=P.WARN, fg=P.BG, size=0.24, z=0.9, align="l")
        K.show(st, d_in, t_in, t_out, 0.4)
        K.show(st, d_out, t_out, t_hold, 0.4)
        K.show(st, d_hold, t_hold, None, 0.4)
        big = K.tag(st, -0.3, -2.2, "or pulls the weight of a long string: tens of tonnes", color=P.PANEL2, size=0.22, z=0.9, align="l")
        K.show(st, big, b.word(5, "tens of tonnes") - 1.5, None, 0.4)
        eg = K.tag(st, -0.3, -3.0, "everything depends on the grip", color=P.WARN, fg=P.BG, size=0.28, z=0.9, align="l")
        K.show(st, eg, s[6], None, 0.5)


# ====================================================================================================== 5.04
def b504(st, tl):
    b = tl["5.04"]
    s = b.sent
    with st.span(b.start, b.end):
        cx = -4.2
        tube_up = st.rect(cx, 2.0, 0.4, 4.0, P.STEEL, 0.5, role="steel")
        tube_lo = st.rect(cx, -1.9, 0.4, 5.0, P.STEEL, 0.5, role="steel")
        # the stripper
        strip = C.stripper(st, cx, 3.1, w=2.2, h=0.8)
        bop = C.bop_quad(st, cx, 2.35, sec_h=0.9, w=2.2, tube_w=0.4)
        K.show(st, [tube_up, tube_lo] + strip.parts, b.start + 0.2, None, 0.5)
        sq = [st.arrow(cx - 1.55, 3.1, cx - 1.2, 3.1, P.PORE, 0.06, 0.2, 0.7), st.arrow(cx + 1.55, 3.1, cx + 1.2, 3.1, P.PORE, 0.06, 0.2, 0.7)]
        K.show(st, sum([list(a) for a in sq], []), s[0] + 0.5, None, 0.4)
        sl = K.callout(st, "stripper: rubber squeezed round the tube", -2.2, 3.1, cx + 1.1, 3.1, size=0.21, align="l")
        K.show(st, sl, s[0] + 0.3, s[2], 0.4)
        sl2 = K.note(st, "the dynamic seal, like the stuffing box:\nit wears", -2.1, 2.55, 0.2, P.MUTED, align="l")
        K.show(st, sl2, s[1], s[2], 0.4)
        # BOP stack
        K.show(st, bop.body, s[2] - 0.2, None, 0.5)
        for nm in bop.names:
            sec = bop.sections[nm]
            K.show(st, [sec["left"], sec["right"]], s[2] - 0.2, None, 0.5)
        # name each ram as it is spoken
        texts = {"blind rams": "seals an empty hole", "shear rams": "cut the tube", "slip rams": "grip the tube so it cannot fall", "pipe rams": "seal around the tube"}
        for nm in bop.names:
            yc = bop.sections[nm]["y"]
            t = b.word(3, nm.split()[0] + " rams")
            g = K.callout(st, f"{nm}: {texts[nm]}", -2.2, yc, cx + 1.1, yc, color=P.PANEL2, size=0.21, align="l")
            K.show(st, g, t, s[4], 0.4)
            st.ripple(cx, yc, t, t + 1.0, bop.sections[nm]["color"], period=0.7, r0=0.3, r1=1.0)
        # the emergency sequence, in order: pipe rams, slips, shear, blind
        order = [("pipe rams", b.word(4, "pipe rams"), "1  pipe rams seal"), ("slip rams", b.word(4, "slips"), "2  slips hold"),
                 ("shear rams", b.word(4, "shear to cut"), "3  shear cuts"), ("blind rams", b.word(4, "blind to seal"), "4  blind seals the bore")]
        for nm, t, txt in order:
            C.close_ram(st, bop, nm, t, t + 0.8)
            g = K.tag(st, 1.5, 1.9 - [o[0] for o in order].index(nm) * 0.62, txt, color=bop.sections[nm]["color"], fg=P.BG, size=0.22, z=0.9, align="l")
            K.show(st, g, t, None, 0.35)
        # after the shear the upper tube is pulled out through the open blind rams; then they close
        t_cut = order[2][1]
        st.move(tube_up, t_cut + 0.7, t_cut + 2.0, dy=+2.2)
        # the bore below stays held and sealed
        lb = K.note(st, "tube below the cut: held by the slips,\nsealed by the pipe rams", 1.5, -1.6, 0.2, P.TEXT, align="l")
        K.show(st, lb, t_cut + 1.0, None, 0.5)
        hd = K.tag(st, 1.5, 3.3, "in an emergency", color=P.BAD, fg=P.BG, size=0.22, z=0.9, align="l")
        K.show(st, hd, s[4], None, 0.4)


def build(st, tl):
    F.header(st, tl)
    b501(st, tl)
    b502(st, tl)
    b503(st, tl)
    b504(st, tl)
    import importlib
    for name in ("x_ch05b", "x_ch05c"):
        try:
            importlib.import_module("scenes." + name).build(st, tl)
        except ModuleNotFoundError as e:
            if name not in str(e):
                raise
