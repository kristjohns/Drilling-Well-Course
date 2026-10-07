"""Ch 0: Cold open. Dive to the seabed -> true-scale pull-out (4 km of rock) -> the cutaway: squeeze, pore fluid, mud ->
kick vs losses (with the level-falls physics done right) -> the window gauge closing like a vice -> the window as a slice
moving down the depth plot -> the question -> the title."""
from __future__ import annotations
import math
import random

from scenes.common import palette as P, well_model as M
from scenes.common.chart import Chart
from scenes.common.shapes import pill
from scenes.common.look import wrap_to

TITLE = "Cold open: the window"

TOP, SEABED = 3.2, -12.0                 # sea surface and seabed (world y) in the descent scene
U_PER_M = (TOP - SEABED) / M.WATER_DEPTH  # true vertical scale: world units per metre


def zdepth(z_m):
    """World y of a depth (m below sea level) in the true-scale scene."""
    return TOP - z_m * U_PER_M


# ---------------------------------------------------------------- 0.01 dive, true-scale pull-out, back to an empty seabed
def beat_descent(st, tl):
    b = tl["0.01"]
    s = b.sent
    rnd = random.Random(7)
    t_land = b.word(0, "three hundred", 1.0) + 0.15
    t_out0 = b.word(1, "drill")
    t_out1 = t_out0 + 2.6
    t_gone = b.word(2, "rig")
    t_in0 = b.word(2, "steel") - 0.2
    t_in1 = min(t_in0 + 2.8, b.end - 2.0)
    deep = zdepth(M.TD)
    with st.span(b.start, b.end):
        st.rect(0, TOP + 40, 2000, 80, P.BG, -0.3, role="hole")                        # night sky
        st.rect(0, (TOP + SEABED) / 2, 2000, TOP - SEABED, P.SEA, -0.2)               # 300 m of water
        st.line([(-1000, TOP), (1000, TOP)], P.PORE, 0.05, 0.0, alpha=0.8)             # surface
        # geology, true scale: seabed band, strata, the reservoir sandstone
        layers = [(M.WATER_DEPTH, 900, P.SEABED), (900, 1900, P.ROCK2), (1900, 2600, P.ROCK), (2600, 3300, P.SHALE),
                  (3300, M.RES_TOP, P.ROCK), (M.RES_TOP, M.RES_BASE, P.SAND), (M.RES_BASE, 4600, P.ROCK2)]
        for a, c, col in layers:
            st.rect(0, (zdepth(a) + zdepth(c)) / 2, 2000, zdepth(a) - zdepth(c), col, -0.1)
        st.rect(0, SEABED - 0.06, 2000, 0.12, "#8b7a5e", -0.05)
        mounds = []
        for i in range(9):                                                               # soft sediment ripples
            x = -9 + i * 2.3 + rnd.uniform(-0.4, 0.4)
            w, h = rnd.uniform(1.2, 2.4), rnd.uniform(0.08, 0.2)
            mounds.append(st.poly([(x - w, SEABED), (x - w * 0.4, SEABED + h), (x + w * 0.3, SEABED + h * 0.8), (x + w, SEABED)], "#8b7a5e", -0.04))
        # marine snow, three parallax layers that always fill the view (procedural)
        snow = [(rnd.uniform(-9, 9), rnd.uniform(-5, 5), k) for k in (0, 1, 2) for _ in range(34)]

        def draw_snow(c, t, look):
            cx, cy, cw = st.cam_at(t)
            if cw > 30:
                return
            for layer, (rr, a, f) in enumerate(((0.025, 0.30, 0.6), (0.045, 0.42, 1.0), (0.08, 0.22, 1.5))):
                pos = []
                for (x0, y0, k) in snow:
                    if k != layer:
                        continue
                    y = y0 - 0.12 * t - cy * (f - 1.0)
                    y = (y - (-5)) % 10 - 5 + cy
                    x = x0 + 0.25 * math.sin(0.4 * t + x0) + cx * (1 - f) * 0.0
                    if y > SEABED + 0.1 and y < TOP - 0.1:
                        pos.append((x, y))
                look.draw_particles(c, pos, "#bcd6f2", rr, a, glow=False)
        st.procedural(b.start, b.end, -0.01, draw_snow)
        # depth read-out (screen-anchored HUD) during the dive
        def draw_hud(c, t, look):
            cx, cy, cw = st.cam_at(t)
            if cw > 30:
                return
            f = (0.6 - cy) / (0.6 - (SEABED + 1.6))
            depth = max(0.0, min(1.0, f)) * M.WATER_DEPTH
            a = min(1.0, (t - b.start - 0.2) / 0.5) * max(0.0, min(1.0, (t_out0 + 0.5 - t) / 0.6))
            if a <= 0:
                return
            k = cw / 16
            look.draw_text(c, "DEPTH", cx - 7.4 * k, cy + 3.95 * k, 0.14 * k, P.MUTED, a, "l", "bold")
            look.draw_text(c, f"{depth:5.0f} m", cx - 7.4 * k, cy + 3.55 * k, 0.32 * k, P.PORE, a, "l", "mono")
        st.procedural(b.start, t_out0 + 1.2, 5.0, draw_hud)
        # camera: eased dive that lands on "three hundred metres"
        st.camera(b.start, b.start + 0.01, cy=0.6, width=16)
        st.camera(b.start + 0.25, t_land, cy=SEABED + 1.6)
        call = pill(st, 3.6, SEABED + 1.1, "seabed · 300 m", P.PANEL2, P.TEXT, 0.24)
        lead = st.line([(2.25, SEABED + 1.1), (1.2, SEABED + 0.06)], P.TEXT, 0.025, 0.4, alpha=0.7)
        dot = st.circle(1.2, SEABED + 0.06, 0.06, P.TEXT, 0.41)
        st.fade_in(call + [lead, dot], t_land - 0.6, 0.4)
        st.fade_out(call + [lead, dot], t_out0 - 0.2, 0.4)
        # true-scale pull-out: the well path draws down 4 km with a depth counter at the bit
        W = 460.0
        mid = (TOP + 23.0 + deep - 6.0) / 2
        st.camera(t_out0, t_out1, cy=mid, width=W)
        path = st.line([(0, SEABED), (0, deep)], P.MUD, 1.3, 2.0, role="glow")
        t_draw0, t_draw1 = t_out0 + 1.0, max(t_out0 + 3.6, b.word(1, "beneath", 1.0))
        st.draw_on(path, t_draw0, t_draw1, "BEZIER")

        def draw_bit(c, t, look):
            if t < t_draw0:
                return
            f = min(1.0, max(0.0, (t - t_draw0) / (t_draw1 - t_draw0)))
            f = 4 * f ** 3 if f < 0.5 else 1 - (-2 * f + 2) ** 3 / 2
            y = SEABED + (deep - SEABED) * f
            z = M.WATER_DEPTH + (M.TD - M.WATER_DEPTH) * f
            a = min(1.0, (t - t_draw0) / 0.3) * max(0.0, min(1.0, (t_gone + 0.6 - t) / 0.6))
            if a > 0:
                look.draw_text(c, f"{z:,.0f} m", 9.0, y + 4.0, 9.0, P.MUD, a, "l", "mono")
        st.procedural(t_draw0, t_gone + 0.7, 3.0, draw_bit)
        lab_w = st.text("300 m of water", -14, (TOP + SEABED) / 2, 6.5, P.PORE, 2.0, align="r", kind="bold")
        lab_r = st.text("almost 4 km of rock", -14, (SEABED + deep) / 2, 9.0, P.TEXT, 2.0, align="r", kind="bold")
        lab_t = st.text("target sandstone", -14, (zdepth(M.RES_TOP) + zdepth(M.RES_BASE)) / 2 + 6.0, 7.0, P.SAND, 2.0, align="r", kind="bold")
        st.fade_in([lab_w, lab_r], t_out0 + 1.2, 0.6)
        st.fade_in(lab_t, t_draw1 - 0.6, 0.6)
        # the rig on the surface, then gone (time-lapse)
        rig = [st.rect(0, TOP + 2.2, 36, 3.2, P.STEEL_DK, 1.0, role="solid"),
               st.rect(-12, TOP - 1.2, 9, 3.4, P.STEEL_DK, 1.0, role="solid"), st.rect(12, TOP - 1.2, 9, 3.4, P.STEEL_DK, 1.0, role="solid"),
               st.poly([(-5, TOP + 3.8), (5, TOP + 3.8), (1.2, TOP + 21), (-1.2, TOP + 21)], P.STEEL, 1.0)]
        rl = st.text("drilling rig", 22, TOP + 4, 6.0, P.MUTED, 2.0, align="l", kind="bold")
        st.fade_in(rig + [rl], t_out0 + 0.6, 0.6)
        gone = rig + [rl, path, lab_w, lab_r, lab_t]
        st.fade_out(gone, t_gone, 0.9)
        # back down to the same, empty seabed; a ghost of the cut casing stub sinks out of sight
        st.camera(t_in0, t_in1, cy=SEABED + 1.6, width=16)
        stub = [st.rect(-0.45, SEABED - 0.55, 0.16, 1.0, P.STEEL, -0.07), st.rect(0.45, SEABED - 0.55, 0.16, 1.0, P.STEEL, -0.07)]
        st.fade_in(stub, t_in1 - 0.6, 0.4)
        st.fade_out(stub, t_in1 + 0.7, 1.2)
        cut = st.text("cut below the seabed", 0.0, SEABED - 1.55, 0.22, P.MUTED, 0.4)
        st.fade_in(cut, t_in1 - 0.4, 0.4)
        st.fade_out(cut, t_in1 + 0.9, 0.8)
        # hard reset of the camera for the next beats (they are drawn around the origin)
        st.camera(b.end - 0.02, b.end, cy=0.0, width=16, interp="CONSTANT")


# ---------------------------------------------------------------- 0.02 / 0.03 cutaway: squeeze, pore fluid, mud; kick vs losses
HX, HW = -2.5, 0.9                       # hole centre and width
SEA_Y, HOLE_BOT = 3.0, -2.55             # seabed in the cutaway, bottom of the hole
SAND = (-0.75, -1.95)                    # sand layer (top, bottom)


def beat_cutaway(st, tl):
    b2, b3 = tl["0.02"], tl["0.03"]
    t0, t1 = b2.start, b3.end
    with st.span(t0, t1):
        # sea, seabed, strata
        st.rect(-2.5, SEA_Y + 0.45, 6.6, 0.9, P.SEA, 0.0)
        layers = [(SEA_Y, 1.75, P.ROCK2), (1.75, 0.45, P.ROCK), (0.45, SAND[0], P.SHALE), (SAND[0], SAND[1], P.SAND), (SAND[1], -3.45, P.ROCK)]
        strata = [st.rect(-2.5, (a + c) / 2, 6.6, a - c, col, 0.0) for a, c, col in layers]
        seabed = st.rect(-2.5, SEA_Y, 6.6, 0.06, "#8b7a5e", 0.02)
        hole = [st.rect(HX, (SEA_Y + HOLE_BOT) / 2, HW, SEA_Y - HOLE_BOT, P.BG, 0.05), st.circle(HX, HOLE_BOT, HW / 2, P.BG, 0.05, role="hole")]
        whd = [st.rect(HX, SEA_Y + 0.17, 1.35, 0.3, P.STEEL_DK, 0.3, role="steel"), st.rect(HX, SEA_Y + 0.42, 0.7, 0.22, P.STEEL, 0.3)]
        st.fade_in([*strata, seabed, *hole, *whd], t0, 0.6)
        wl = st.text("well", HX + 0.95, SEA_Y + 0.35, 0.2, P.MUTED, 0.3, align="l", kind="bold")
        st.fade_in(wl, t0 + 0.4, 0.5)
        _act_02(st, b2)
        _act_03(st, b2, b3)


def _arrow_set(st, ys, color, inward=True, length=0.6, z=0.35, width=0.07):
    """Arrows on both walls of the hole at heights ys (inward = towards the hole)."""
    out = []
    for y in ys:
        for side in (-1, 1):
            wall = HX + side * HW / 2
            far = wall + side * length
            out.append(st.arrow(far, y, wall + side * 0.06, y, color, width, 0.22, z) if inward else
                       st.arrow(wall + side * 0.08, y, far, y, color, width, 0.22, z))
    return out


def _act_02(st, b):
    s = b.sent
    # the rock squeezes in
    t_sq = b.word(1, "squeezes")
    sq = _arrow_set(st, (2.2, 1.1, -0.1, -2.3), P.STEEL_DK, inward=True, length=0.75, width=0.09)
    st.fade_in(sq, t_sq - 0.2, 0.4)
    sql = pill(st, 1.2, 1.55, "rock squeezes in", P.PANEL2, P.TEXT, 0.2, align="l")
    st.fade_in(sql, t_sq, 0.4)
    st.fade_out(sql, b.end - 0.6, 0.4)
    # the pore fluid pushes to get in (from the sand)
    t_pf = b.word(1, "fluid")
    pf = _arrow_set(st, (-1.1, -1.6), P.PORE, inward=True, length=0.75)
    st.fade_in(pf, t_pf, 0.4)
    pfl = pill(st, 1.2, -1.35, "pore fluid pushes in", P.PANEL2, P.PORE, 0.2, align="l")
    st.fade_in(pfl, t_pf + 0.2, 0.4)
    st.fade_out(pfl, b.end - 0.6, 0.4)
    st.fade_out(sq + pf, b.end - 0.6, 0.5)
    # mud fills the hole, then the slider appears on "we choose"
    t_mud = b.word(2, "liquid")
    mud = st.rect(HX, HOLE_BOT, HW, 0.0001, P.MUD, 0.1, anchor="b")
    mud_b = st.circle(HX, HOLE_BOT, HW / 2, P.MUD, 0.1, role="disc")
    st.fade_in(mud_b, t_mud, 0.3)
    st.scale_to(mud, t_mud, t_mud + 1.8, sy=SEA_Y - HOLE_BOT)
    st.state["_mud"] = (mud, mud_b)
    slider(st, b.word(2, "we choose") - 0.3, b.word(2, "heavy"))


SL_X, SL_Y0, SL_Y1 = 4.9, -2.3, 1.2      # slider track (bottom = light, top = heavy)
SL_MID = (SL_Y0 + SL_Y1) / 2


def slider(st, t_in, t_wiggle):
    track = st.rect(SL_X, SL_MID, 0.16, SL_Y1 - SL_Y0, P.GRID, 0.2, role="pill")
    knob = st.circle(SL_X, SL_MID + 0.35, 0.24, P.MUD, 0.32)
    cap = st.text("MUD WEIGHT", SL_X, SL_Y1 + 0.5, 0.2, P.TEXT, 0.3, kind="bold")
    hv = st.text("heavy", SL_X + 0.45, SL_Y1 - 0.05, 0.2, P.FRAC, 0.3, align="l", kind="bold")
    lt = st.text("light", SL_X + 0.45, SL_Y0 + 0.05, 0.2, P.PORE, 0.3, align="l", kind="bold")
    st.fade_in([track, knob, cap, hv, lt], t_in, 0.5)
    st.move(knob, t_wiggle - 0.2, t_wiggle + 0.5, dy=0.45)
    st.move(knob, t_wiggle + 0.5, t_wiggle + 1.2, dy=-0.45)
    st.state["_knob"] = knob


def _act_03(st, b2, b3):
    s = b3.sent
    mud, mud_b = st.state["_mud"]
    knob = st.state["_knob"]
    # balance: pore pressure (blue, in) vs mud pressure (amber, out) at the sand
    t_bal = s[0]
    blue = _arrow_set(st, (-1.1, -1.6), P.PORE, inward=True, length=0.7)
    amber = _arrow_set(st, (-1.35,), P.MUD, inward=False, length=0.7)
    st.fade_in(blue + amber, t_bal + 0.2, 0.4)
    ppl = pill(st, 1.2, -0.35, "pore pressure in the sand", P.PANEL2, P.PORE, 0.2, align="l")
    sand_glow = st.rect(-2.5, (SAND[0] + SAND[1]) / 2, 6.6, SAND[0] - SAND[1], P.PORE, 0.03, alpha=0.18, role="flat")
    st.fade_in([sand_glow] + ppl, b3.word(0, "pores"), 0.5)
    st.fade_out(ppl, s[1] - 0.2, 0.3)
    tick = st.rect(SL_X, SL_MID, 0.5, 0.04, P.PORE, 0.25)
    tickl = st.text("pore pressure", SL_X - 0.35, SL_MID, 0.16, P.PORE, 0.3, align="r", kind="bold")
    st.fade_in([tick, tickl], t_bal + 0.6, 0.4)
    # too light -> kick
    t_light = b3.word(1, "too light")
    st.move(knob, t_light, t_light + 1.0, to=(SL_X, SL_Y0 + 0.35))
    st.recolor([mud, mud_b], t_light, t_light + 1.0, "#ffe3a1")
    st.fade(amber, t_light, t_light + 1.0, 1.0, 0.25)
    t_push = b3.word(1, "pushes")
    t_kick = b3.word(1, "kick")
    paths = [[(HX - HW / 2 - 0.5, y), (HX - 0.15, y + 0.2), (HX - 0.12, SEA_Y - 0.3)] for y in (-1.15, -1.55)] + \
            [[(HX + HW / 2 + 0.5, y), (HX + 0.15, y + 0.2), (HX + 0.12, SEA_Y - 0.3)] for y in (-1.25, -1.7)]
    for p in paths:
        st.flow(p, t_push - 0.2, s[2] + 0.4, P.PORE, n=7, speed=1.6, r=0.05, z=0.45)
    kick = pill(st, HX, 0.9, "KICK", P.BAD, "#ffffff", 0.32, 0.6)
    st.fade_in(kick, t_kick - 0.1, 0.25)
    st.fade_out(kick, s[2] - 0.3, 0.3)
    st.ripple(HX, -1.35, t_kick - 0.1, t_kick + 1.4, P.BAD, period=0.7, r0=0.3, r1=1.4)
    # too heavy -> crack (one vertical loss zone in the upper rock), mud drains, level falls
    t_heavy = b3.word(2, "too heavy")
    st.move(knob, t_heavy, t_heavy + 1.0, to=(SL_X, SL_Y1 - 0.35))
    st.recolor([mud, mud_b], t_heavy, t_heavy + 1.0, P.KILL_MUD)
    st.fade_out(blue, t_heavy, 0.5)
    st.fade(amber, t_heavy, t_heavy + 0.8, 0.25, 1.0)
    t_crack = b3.word(2, "crack")
    wall = HX - HW / 2
    fy0, fy1 = 0.75, 1.55                       # fracture mouth on the wall (still below the fallen mud level)
    wedge = st.poly([(wall, fy1), (wall - 1.6, (fy0 + fy1) / 2 + 0.15), (wall, fy0)], P.MUD, 0.2)
    st.pop_in(wedge, t_crack, 0.6)
    edge = st.line([(wall, fy1), (wall - 0.5, fy1 - 0.12), (wall - 1.0, fy1 - 0.3), (wall - 1.6, (fy0 + fy1) / 2 + 0.15),
                    (wall - 1.0, fy0 + 0.25), (wall - 0.5, fy0 + 0.1), (wall, fy0)], P.FRAC, 0.05, 0.22)
    st.draw_on(edge, t_crack - 0.1, t_crack + 0.7)
    crl = pill(st, wall - 2.0, fy1 + 0.55, "fracture", P.PANEL2, P.FRAC, 0.2)
    st.fade_in(crl, t_crack + 0.3, 0.4)
    t_drain = b3.word(3, "drains")
    st.flow([(HX, 2.6), (HX - 0.2, (fy0 + fy1) / 2), (wall - 1.2, (fy0 + fy1) / 2 + 0.1)], t_drain - 0.2, b3.end, P.MUD, n=10, speed=1.2, r=0.05, z=0.45)
    t_level = b3.word(3, "level")
    new_top = fy1 + 0.25
    st.scale_to(mud, t_level - 0.2, t_level + 1.6, sy=new_top - HOLE_BOT)
    lv = st.text("level falls", HX + 0.62, new_top + 0.15, 0.2, P.TEXT, 0.5, align="l", kind="bold")
    lva = st.arrow(HX + 0.35, new_top + 0.7, HX + 0.35, new_top + 0.12, P.TEXT, 0.04, 0.14, 0.5)
    st.fade_in([lv] + lva, t_level + 0.6, 0.4)
    # bottom pressure marker slides down past the pore-pressure tick (the knob stays at heavy: density did not change)
    t_bhp = b3.word(3, "pressure at the bottom")
    bhp = st.ring(SL_X, SL_Y1 - 0.35, 0.27, 0.06, P.TEXT, 0.34)
    bhl = st.text("pressure at\nthe bottom", SL_X - 0.4, SL_Y1 - 0.35, 0.16, P.TEXT, 0.34, align="r", kind="bold")
    st.fade_in([bhp, bhl], t_bhp - 0.6, 0.3)
    st.move([bhp, bhl], t_bhp, t_bhp + 1.4, dy=-(SL_Y1 - 0.35 - (SL_MID - 0.55)))
    stay = st.text("density unchanged", SL_X + 0.45, SL_Y1 - 0.42, 0.15, P.MUTED, 0.3, align="l")
    st.fade_in(stay, t_bhp + 0.2, 0.4)
    # ... and the fluid comes in anyway
    t_anyway = b3.word(3, "comes in")
    blue2 = _arrow_set(st, (-1.1, -1.6), P.PORE, inward=True, length=0.7)
    st.fade_in(blue2, t_anyway - 0.3, 0.3)
    for p in paths[:2]:
        st.flow([(x, min(y, new_top - 0.2)) for x, y in p], t_anyway, b3.end, P.PORE, n=6, speed=1.4, r=0.05, z=0.46)
    st.ripple(HX, -1.35, t_anyway, b3.end, P.BAD, period=0.8, r0=0.3, r1=1.3)


# ---------------------------------------------------------------- 0.04 the window: a vice, then a slice moving down the depth plot
G_Y, G_X0, G_X1 = 0.9, -5.2, 5.2       # gauge row and extent


def gx(sg):
    """Gauge x for a mud weight (sg): 10 world units per sg, 1.62 sg at x 0.3."""
    return 0.3 + (sg - 1.62) * 10.0


def beat_window(st, tl):
    b = tl["0.04"]
    s = b.sent
    pp_deep, fg_shoe = max(M.pp(z) for z in range(3400, int(M.TD) + 1, 10)), M.fg(3400)
    with st.span(b.start, b.end):
        frame = st.rect(0, G_Y, G_X1 - G_X0 + 0.5, 1.5, P.PANEL, 0.0)
        green = st.rect(0, G_Y, G_X1 - G_X0, 0.9, P.SAFE, 0.1, role="flat")
        kick = st.rect(G_X0, G_Y, 0.0001, 0.9, P.PORE, 0.15, anchor="l", role="flat")
        crack = st.rect(G_X1, G_Y, 0.0001, 0.9, P.FRAC, 0.15, anchor="r", role="flat")
        st.fade_in([frame, green], s[0], 0.5)
        st.fade_in([kick, crack], s[0], 0.2)
        st.scale_to(kick, s[0] + 0.2, s[0] + 1.6, sx=gx(pp_deep) - G_X0)
        st.scale_to(crack, s[0] + 0.2, s[0] + 1.6, sx=G_X1 - gx(fg_shoe))
        kl = st.text("too light: KICK", G_X0 + 0.2, G_Y - 0.85, 0.22, P.PORE, 0.3, align="l", kind="bold")
        cl = st.text("too heavy: CRACK", G_X1 - 0.2, G_Y - 0.85, 0.22, P.FRAC, 0.3, align="r", kind="bold")
        wl = st.text("the window", gx((pp_deep + fg_shoe) / 2), G_Y + 0.85, 0.22, P.SAFE, 0.3, kind="bold")
        st.fade_in([kl, cl], s[0] + 0.8, 0.4)
        st.fade_in(wl, b.word(0, "mud weight window"), 0.4)
        marker = st.rect(gx(1.62), G_Y, 0.07, 1.25, P.MUD, 0.3, role="shaft")
        st.fade_in(marker, s[1], 0.4)
        # ~10 % in the deepest section
        t_tenth = b.word(1, "a tenth")
        ten = pill(st, gx((pp_deep + fg_shoe) / 2), G_Y - 1.75, "deepest section of our well: ≈ 10 % of the mud weight", P.PANEL2, P.SAFE, 0.2)
        brk = st.line([(gx(pp_deep), G_Y - 0.55), (gx(pp_deep), G_Y - 0.75), (gx(fg_shoe), G_Y - 0.75), (gx(fg_shoe), G_Y - 0.55)], P.SAFE, 0.035, 0.3)
        st.draw_on(brk, t_tenth - 0.4, t_tenth + 0.2)
        st.fade_in(ten, t_tenth - 0.2, 0.4)
        # the vice: high-pressure / depleted wells
        t_hp = b.word(2, "high-pressure")
        nar = 0.045 * 1.62 * 10 / 2                              # a few per cent of 1.62 sg, either side of the marker
        st.scale_to(kick, t_hp, t_hp + 2.2, sx=gx(1.62) - nar - G_X0)
        st.scale_to(crack, t_hp, t_hp + 2.2, sx=G_X1 - (gx(1.62) + nar))
        st.fade_out(ten + [brk], t_hp, 0.3)
        hp = pill(st, gx(1.62), G_Y - 1.75, "high-pressure and depleted wells: a few %", P.PANEL2, P.WARN, 0.2)
        st.fade_in(hp, t_hp + 0.4, 0.4)
        t_moves = s[3]
        st.scale_to(kick, t_moves - 1.0, t_moves + 0.2, sx=gx(pp_deep) - G_X0)
        st.scale_to(crack, t_moves - 1.0, t_moves + 0.2, sx=G_X1 - gx(fg_shoe))
        gauge = [frame, green, kick, crack, kl, cl, wl, marker] + hp
        st.fade_out(gauge, t_moves, 0.5)
        # the window as a slice moving down the depth plot
        c = Chart(st, -3.4, -3.2, 6.0, 6.2, (0.95, 1.95), (0.0, M.TD), invert_y=True)
        fr = c.frame(xticks=[], yticks=[0, 1000, 2000, 3000, 4000], xlabel="mud weight  (light  →  heavy)", ylabel="depth (m)")
        zs = [M.WATER_DEPTH + i * 25 for i in range(int((M.TD - M.WATER_DEPTH) / 25) + 1)]
        band = c.band([(M.pp(z), z) for z in zs], [(M.fg(z), z) for z in zs], P.SAFE, 0.1, 0.28)
        pp = c.curve([M.pp(z) for z in zs], zs, P.PORE, 0.06, 0.3)
        fg = c.curve([M.fg(z) for z in zs], zs, P.FRAC, 0.06, 0.3)
        st.fade_in(fr + [band], t_moves + 0.2, 0.5)
        st.draw_on(pp, t_moves + 0.3, t_moves + 2.0, "BEZIER")
        st.draw_on(fg, t_moves + 0.3, t_moves + 2.0, "BEZIER")
        ppl = c.label(0.97, 3900, "pore pressure", 0.2, P.PORE, "l", "bold")
        fgl = c.label(1.66, 600, "fracture", 0.2, P.FRAC, "l", "bold")
        st.fade_in([ppl, fgl], t_moves + 1.2, 0.4)
        z_a, z_b = M.WATER_DEPTH + 50, M.TD - 20
        t_a, t_b = t_moves + 1.0, b.end - 0.2

        def draw_slice(cv, t, look):
            if t < t_a:
                return
            f = min(1.0, (t - t_a) / (t_b - t_a))
            f = 0.5 - 0.5 * math.cos(math.pi * f)
            z = z_a + (z_b - z_a) * f
            y = c.Y(z)
            x0, x1 = c.X(M.pp(z)), c.X(M.fg(z))
            a = min(1.0, (t - t_a) / 0.4)
            look.draw_ring(cv, x0, y, 0.07, 0.03, P.PORE, a)
            look.draw_ring(cv, x1, y, 0.07, 0.03, P.FRAC, a)
            import skia
            from scenes.common.look import col, hex_rgb
            p = skia.Paint(Color=col(hex_rgb(P.SAFE), 0.95 * a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.09,
                           StrokeCap=skia.Paint.kRound_Cap)
            cv.drawLine(x0, y, x1, y, p)
            look.draw_text(cv, f"{z:,.0f} m", x0 - 0.18, y, 0.19, P.TEXT, a, "r", "mono")
        st.procedural(t_a, b.end, 0.6, draw_slice)
        q = st.text(wrap_to("How do you stay inside it, for four kilometres?", 0.42, 4.1, "bold"), 5.45, 0.3, 0.42, P.TEXT, 0.5, kind="bold")
        st.fade_in(q, s[4] + 0.3, 0.6)


# ---------------------------------------------------------------- 0.05 the question, then the title
def beat_question(st, tl):
    b = tl["0.05"]
    s = b.sent
    with st.span(b.start, b.end):
        lines = [("drill four kilometres", "DRILL 4 KM DOWN", P.TEXT),
                 ("push in", "HOLD BACK THE FLUIDS", P.PORE),
                 ("cracks", "WITHOUT CRACKING THE ROCK", P.FRAC),
                 ("leave the hole", "THEN SEAL IT FOR EVER", P.SAFE)]
        objs = []
        for i, (needle, txt, colr) in enumerate(lines):
            y = 1.9 - i * 0.95
            t = b.word(0, needle) - 0.15
            num = st.text(f"0{i + 1}", -5.6, y, 0.22, colr, 0.5, align="l", kind="mono")
            o = st.text(txt, -4.9, y, 0.5, colr, 0.5, align="l", kind="bold")
            st.fade_in([num, o], t, 0.45)
            if i + 1 < len(lines):
                st.recolor(o, b.word(0, lines[i + 1][0]) - 0.15, b.word(0, lines[i + 1][0]) + 0.35, P.MUTED)
            objs += [num, o]
        badge = pill(st, -5.6, -2.3, "ILLUSTRATIVE WELL  ·  invented numbers, real physics", P.PANEL2, P.WARN, 0.2, align="l")
        st.fade_in(badge, b.word(1, "invented") - 0.2, 0.4)
        t_plan = b.word(2, "plan", 1.0)
        st.fade_out(objs + badge, s[2] - 0.7, 0.5)
        plan = st.text("First, a plan.", 0, 0.2, 0.5, P.WARN, 0.5, kind="bold")
        st.fade_in(plan, s[2] - 0.05, 0.4)
        st.fade_out(plan, t_plan + 0.4, 0.4)
        # the title, held during the pause
        t_title = t_plan + 0.6
        title = st.text("THE HOLE THAT FIGHTS BACK", 0, 0.45, 0.85, P.TEXT, 0.6, kind="bold")
        sub = st.text("how an offshore exploration well is drilled, judged, and sealed for ever", 0, -0.55, 0.26, P.MUTED, 0.6)
        rule = st.line([(-4.0, -0.12), (4.0, -0.12)], P.PORE, 0.045, 0.6)
        st.fade_in(title, t_title, 0.7)
        st.draw_on(rule, t_title + 0.2, t_title + 1.4, "BEZIER")
        st.fade_in(sub, t_title + 0.6, 0.7)


def build(st, tl):
    beat_descent(st, tl)
    beat_cutaway(st, tl)
    beat_window(st, tl)
    beat_question(st, tl)
