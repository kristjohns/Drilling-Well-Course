"""Ch 10: Outro. The whole film on one chart: the window, the casing staircase won a section at a time, steel and cement,
two barriers, flow in = flow out; an argument with the Earth; then the plugs that seal the win -> dissolve to the empty
seabed of the cold open (ghosted plugs and cut stubs under the mud) -> the camera rises to the surface -> end card."""
from __future__ import annotations
import math
import random

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common.shapes import pill

TITLE = "Outro: the empty seabed"

PROG = {s.name: s for s in M.programme()}
MW = M.section_mud_weights()
# the sections as drilled: (top, bottom, mud weight); the top hole (300-1,000 m) is riserless with seawater (Ch 2)
STEPS = [(PROG["20in surface casing"].shoe, PROG["13-3/8in intermediate"].shoe, MW["20in surface casing"]),
         (PROG["13-3/8in intermediate"].shoe, PROG["9-5/8in intermediate"].shoe, MW["13-3/8in intermediate"]),
         (PROG["9-5/8in intermediate"].shoe, M.TD, MW["9-5/8in intermediate"])]
# the plug list of Ch 9 (m below sea level): (top, bottom, label)
PLUGS = [(3300.0, 3700.0, "reservoir: secondary"), (3700.0, 4110.0, "reservoir: primary"),
         (2700.0, 2800.0, "Sand A: secondary"), (2900.0, 2980.0, "Sand A: primary"), (305.0, 450.0, "surface plug")]
# casing half-widths and drilled-hole half-widths in the schematic (world units)
CASING = [("30in conductor", 0.50, 0.58), ("20in surface casing", 0.40, 0.48), ("13-3/8in intermediate", 0.30, 0.37),
          ("9-5/8in intermediate", 0.21, 0.27)]
OPEN_HOLE = 0.18


def _ramp(t, a, b):
    return 0.0 if t <= a else 1.0 if t >= b else (t - a) / (b - a)


# ======================================================================================================== 10.01
def beat_recap(st, tl):
    b = tl["10.01"]
    s = b.sent
    W = b.word
    t_dis = s[5] - 0.35                        # dissolve to the seabed
    with st.span(b.start, t_dis + 1.0):
        # ---------------------------------------------------------------- the window chart (left)
        c = Chart(st, -5.45, -2.75, 5.7, 6.05, (1.0, 1.9), (0.0, M.TD), invert_y=True, z=0.1)
        fr = c.frame(xticks=[1.0, 1.2, 1.4, 1.6, 1.8], yticks=[0, 1000, 2000, 3000, 4000], xlabel="equivalent mud weight (sg)",
                     ylabel="depth (m)", fx="{:.1f}", tick_size=0.17)
        st.fade_in(fr, b.start + 0.1, 0.5)
        zs = [M.WATER_DEPTH + 25.0 * i for i in range(int((M.TD - M.WATER_DEPTH) / 25) + 1)]
        sea = st.rect(c.x + c.w / 2, (c.Y(0) + c.Y(M.WATER_DEPTH)) / 2, c.w, c.Y(0) - c.Y(M.WATER_DEPTH), P.SEA, 0.12, alpha=0.6)
        band = c.band([(M.pp(z), z) for z in zs], [(M.fg(z), z) for z in zs], P.SAFE, 0.13, 0.28)
        ppc = c.curve([M.pp(z) for z in zs], zs, P.PORE, 0.06, 0.3)
        fgc = c.curve([M.fg(z) for z in zs], zs, P.FRAC, 0.06, 0.3)
        st.fade_in(sea, b.start + 0.3, 0.5)
        st.draw_on([ppc, fgc], s[0] + 0.1, W(0, "window") + 0.4, "BEZIER")
        st.fade_in(band, W(0, "window") - 0.2, 0.6)
        ppl = c.label(M.pp(3700) - 0.04, 3720, "pore\npressure", 0.16, P.PORE, "r", "bold")
        fgl = c.label(M.fg(3000) + 0.03, 3000, "fracture", 0.16, P.FRAC, "l", "bold")
        wl = c.label(1.36, 2700, "window", 0.2, P.SAFE, "c", "bold")
        st.fade_in([ppl, fgl], W(0, "window"), 0.4)
        st.fade_in(wl, W(0, "window") + 0.2, 0.4)
        A = fr + [sea, band, ppc, fgc, ppl, fgl, wl]

        # ---------------------------------------------------------------- the well, same depth scale (right)
        WX = 3.3
        Y = c.Y
        top_y = c.Y(0) + 0.05
        sea_w = st.rect(WX, (top_y + Y(M.WATER_DEPTH)) / 2, 3.2, top_y - Y(M.WATER_DEPTH), P.SEA, 0.1)
        rock = st.rect(WX, (Y(M.WATER_DEPTH) + Y(M.TD) - 0.15) / 2, 3.2, Y(M.WATER_DEPTH) - Y(M.TD) + 0.15, P.ROCK, 0.1)
        res = st.rect(WX, (Y(M.RES_TOP) + Y(M.RES_BASE)) / 2, 3.2, Y(M.RES_TOP) - Y(M.RES_BASE), P.SAND, 0.11)
        sand_a = st.rect(WX, (Y(M.SAND_A[0]) + Y(M.SAND_A[1])) / 2, 3.2, max(Y(M.SAND_A[0]) - Y(M.SAND_A[1]), 0.04), P.SAND, 0.11)
        mud_l = st.rect(WX, Y(M.WATER_DEPTH), 3.2, 0.03, P.SEABED, 0.12)
        st.fade_in([sea_w, rock, res, sand_a, mud_l], b.start + 0.3, 0.5)
        G = [sea_w, rock, res, sand_a, mud_l]
        # four kilometres: the hole draws down with a depth counter
        t_4k = W(0, "four kilometres")
        hole = st.rect(WX, Y(M.WATER_DEPTH), 2 * OPEN_HOLE, 0.0001, P.BG, 0.14, anchor="t")
        st.fade_in(hole, t_4k - 0.3, 0.2)
        st.scale_to(hole, t_4k - 0.2, t_4k + 1.6, sy=Y(M.WATER_DEPTH) - Y(M.TD))
        st.counter(WX + 1.85, Y(M.TD) + 0.05, t_4k - 0.2, t_4k + 1.6, M.WATER_DEPTH, M.TD, fmt="{:,.0f} m", size=0.2,
                   color=P.TEXT, align="l", hold=s[1] + 0.3)
        G.append(hole)

        # ---------------------------------------------------------------- "not all at once": one mud weight fails
        t_one = s[1] - 0.1
        mw = MW["9-5/8in intermediate"]
        one = st.line([c.pt(mw, M.WATER_DEPTH), c.pt(mw, M.TD)], P.MUD, 0.05, 0.4)
        st.draw_on(one, t_one, t_one + 0.9, "BEZIER")
        z_x = 2000.0                                                       # fg(2,000 m) = 1.62: above it this mud cracks the rock
        bad = st.line([c.pt(mw, M.WATER_DEPTH), c.pt(mw, z_x)], P.BAD, 0.09, 0.41)
        st.fade_in(bad, t_one + 0.7, 0.3)
        bp = pill(st, c.X(mw) + 0.2, c.Y(900), f"one weight, {mw:.2f} sg:\ncracks the rock up here", P.PANEL2, P.BAD, 0.17, 0.6, align="l")
        st.fade_in(bp, t_one + 0.8, 0.3)
        st.fade_out([one, bad] + bp, s[2] - 0.25, 0.35)

        # ---------------------------------------------------------------- a few hundred metres at a time: the staircase
        t_st0, t_st1 = W(2, "a few hundred metres"), W(2, "at a time", 1.0) + 0.3
        stair = []
        n = len(STEPS)
        for i, (z0, z1, w) in enumerate(STEPS):
            ta = t_st0 + (t_st1 - t_st0) * i / n
            tb = t_st0 + (t_st1 - t_st0) * (i + 1) / n
            seg = st.line([c.pt(w, z0), c.pt(w, z1)], P.MUD, 0.08, 0.45)
            st.draw_on(seg, ta, tb, "BEZIER")
            stair.append(seg)
            if i + 1 < n:
                w2 = STEPS[i + 1][2]
                jog = st.line([c.pt(w, z1), c.pt(w2, z1)], P.MUD, 0.08, 0.45)
                st.draw_on(jog, tb - 0.05, tb + 0.15)
                stair.append(jog)
            lab = c.label(w + 0.02, (z0 + z1) / 2 + 120, f"{w:.2f}", 0.15, P.MUD, "l", "bold")
            st.fade_in(lab, tb - 0.2, 0.3)
            stair.append(lab)
        th = c.label(1.08, 650, "top hole: seawater,\nriserless (Ch 2)", 0.14, P.MUTED, "l")
        st.fade_in(th, t_st0, 0.4)
        stair.append(th)

        # ---------------------------------------------------------------- lock each stretch behind steel and cement
        t_lk = W(2, "lock each stretch")
        t_sc = W(2, "steel and cement", 1.0)
        steel = []
        for k, (name, hw, hh) in enumerate(CASING):
            p = PROG[name]
            tk = t_lk + (t_sc + 0.6 - t_lk) * k / len(CASING)
            yt, yb = Y(M.WATER_DEPTH), Y(p.shoe)
            for sd in (-1, 1):
                cem = st.rect(WX + sd * (hw + hh) / 2, yt, hh - hw, 0.0001, P.CEMENT, 0.15 + 0.01 * k, anchor="t")
                pipe = st.rect(WX + sd * hw, yt, 0.04, 0.0001, P.STEEL, 0.2 + 0.01 * k, anchor="t")
                st.fade_in([cem, pipe], tk, 0.1)
                st.scale_to(pipe, tk, tk + 0.5, sy=yt - yb)
                st.scale_to(cem, tk + 0.25, tk + 0.75, sy=yt - yb)
                steel += [cem, pipe]
            # the shoe on the chart: a dashed line across the window
            sh = st.dashed(c.pt(1.0, p.shoe), c.pt(1.9, p.shoe), P.STEEL, 0.02, 0.1, 0.07, 0.16, alpha=0.6)
            st.fade_in(sh, tk + 0.2, 0.3)
            steel += sh
        sl = st.text("steel + cement", WX + 1.75, Y(2900), 0.17, P.CEMENT, 0.5, align="l", kind="bold")
        sll = st.line([(WX + 1.7, Y(2900)), (WX + 0.36, Y(2900))], P.CEMENT, 0.02, 0.5, alpha=0.7)
        st.fade_in([sl, sll], t_sc - 0.2, 0.4)
        steel += [sl, sll]
        # wellhead + BOP on the seabed, riser to the rig (needed for the secondary barrier)
        bop = [st.rect(WX, Y(M.WATER_DEPTH) + 0.22, 0.95, 0.42, P.STEEL_DK, 0.3, role="solid"),
               st.rect(WX, Y(M.WATER_DEPTH) + 0.05, 1.2, 0.1, P.STEEL, 0.31)]
        riser = st.rect(WX, (top_y + Y(M.WATER_DEPTH) + 0.43) / 2, 0.34, top_y - Y(M.WATER_DEPTH) - 0.43, P.STEEL_DK, 0.25, alpha=0.8)
        st.fade_in(bop + [riser], t_lk - 0.2, 0.4)
        # mud in the bore
        mud = st.rect(WX, Y(M.WATER_DEPTH), 2 * OPEN_HOLE - 0.02, Y(M.WATER_DEPTH) - Y(M.TD), P.MUD, 0.17, anchor="t", alpha=0.85)
        st.fade_in(mud, t_sc, 0.5)

        # ---------------------------------------------------------------- two barriers between the rock and the sea
        t_2b = W(2, "two barriers")
        y_top_b, y_bot = Y(M.WATER_DEPTH) + 0.45, Y(M.TD) + 0.02
        prim = st.line([(WX - 0.15, Y(M.WATER_DEPTH) - 0.05), (WX - 0.15, y_bot + 0.06), (WX + 0.15, y_bot + 0.06),
                        (WX + 0.15, Y(M.WATER_DEPTH) - 0.05)], P.PRIMARY_B, 0.05, 0.6, closed=True)
        sec_pts = [(WX - 0.62, y_top_b), (WX + 0.62, y_top_b), (WX + 0.62, Y(M.WATER_DEPTH)),
                   (WX + 0.33, Y(M.WATER_DEPTH)), (WX + 0.33, Y(PROG["9-5/8in intermediate"].shoe) - 0.25),
                   (WX - 0.33, Y(PROG["9-5/8in intermediate"].shoe) - 0.25), (WX - 0.33, Y(M.WATER_DEPTH)),
                   (WX - 0.62, Y(M.WATER_DEPTH))]
        sec = st.line(sec_pts, P.SECOND_B, 0.05, 0.61, closed=True)
        st.draw_on(prim, t_2b - 0.1, t_2b + 0.9)
        st.draw_on(sec, t_2b + 0.3, t_2b + 1.3)
        pl = pill(st, WX + 1.75, Y(3800), "primary:\nthe mud", P.PANEL2, P.PRIMARY_B, 0.16, 0.7, align="l")
        sl2 = pill(st, WX + 1.75, Y(2400), "secondary: steel,\ncement, rock, BOP", P.PANEL2, P.SECOND_B, 0.16, 0.7, align="l")
        st.fade_in(pl, t_2b + 0.2, 0.3)
        st.fade_in(sl2, t_2b + 0.7, 0.3)
        BAR = [prim, sec] + pl + sl2

        # ---------------------------------------------------------------- watch every barrel: flow in = flow out
        t_bb = W(2, "watch every barrel")
        gx, gy = 6.4, 1.6
        card = st.rect(gx, gy, 2.6, 2.2, P.PANEL, 0.4)
        ttl = st.text("FLOW OUT − FLOW IN", gx, gy + 0.8, 0.15, P.MUTED, 0.45, kind="bold")
        arc = []
        for k in range(13):
            th_ = math.radians(160 - 140 * k / 12)
            arc.append(st.rect(gx + 0.85 * math.cos(th_), gy - 0.55 + 0.85 * math.sin(th_), 0.1 if k != 6 else 0.16, 0.025,
                               P.SAFE if k == 6 else P.GRID, 0.45, rot=math.degrees(th_)))
        needle = st.rect(gx, gy - 0.55, 0.78, 0.04, P.TEXT, 0.5, anchor="l", rot=150)
        hub = st.circle(gx, gy - 0.55, 0.06, P.TEXT, 0.51)
        zero = st.text("0", gx, gy + 0.48, 0.15, P.SAFE, 0.45, kind="bold")
        st.fade_in([card, ttl, zero, hub, needle] + arc, t_bb - 0.2, 0.4)
        st.rotate(needle, t_bb + 0.1, t_bb + 1.2, 90.0, interp="BACK")
        ok = st.text("balanced", gx, gy - 0.82, 0.16, P.SAFE, 0.45, kind="bold")
        st.fade_in(ok, t_bb + 1.0, 0.3)
        GAUGE = [card, ttl, zero, hub, needle, ok] + arc

        # ---------------------------------------------------------------- an argument with the Earth, won every hour
        t_arg = W(3, "argument")
        dim_objs = A + G + stair + steel + bop + [riser, mud] + BAR + GAUGE
        st.fade(dim_objs, s[3] - 0.1, s[3] + 0.5, 1.0, 0.18)
        st.fade(dim_objs, s[4] - 0.35, s[4] + 0.2, 0.18, 1.0)
        k1 = st.text("an argument with the Earth", 0.0, 0.75, 0.62, P.TEXT, 2.0, kind="bold")
        k2 = st.text("about pressure", 0.0, -0.2, 0.42, P.PORE, 2.0, kind="bold")
        k3 = st.text("that you win every hour", 0.0, -1.1, 0.42, P.MUD, 2.0, kind="bold")
        st.fade_in(k1, t_arg - 0.15, 0.4)
        st.fade_in(k2, W(3, "about pressure") - 0.1, 0.35)
        st.fade_in(k3, W(3, "every hour") - 0.25, 0.35)
        st.fade_out([k1, k2, k3], s[4] - 0.45, 0.35)

        # ---------------------------------------------------------------- seal the win: plugs, BOP away, barriers retired
        t_seal = W(4, "seal the win")
        st.fade_out(BAR + GAUGE, s[4] - 0.3, 0.4)
        st.move(bop + [riser], t_seal, t_seal + 1.2, dy=1.0)
        st.fade_out(bop + [riser], t_seal + 0.4, 0.8)
        st.fade(mud, t_seal, t_seal + 0.8, 1.0, 0.35)
        plugs = []
        for k, (z0, z1, _lab) in enumerate(PLUGS):
            tk = t_seal + 0.15 + 0.22 * k
            yt, yb = Y(z0), Y(z1)
            hw = OPEN_HOLE if z0 >= PROG["9-5/8in intermediate"].shoe else CASING[3][1] - 0.02
            if z0 < PROG["20in surface casing"].shoe:
                hw = CASING[3][1] - 0.02
            g = st.rect(WX, (yt + yb) / 2, 2 * hw, max(yt - yb, 0.05), P.CEMENT, 0.62)
            o = st.line([(WX - hw, yt), (WX + hw, yt), (WX + hw, yb), (WX - hw, yb)], P.SAFE, 0.035, 0.63, closed=True)
            st.pop_in(g, tk, 0.35)
            st.fade_in(o, W(4, "for ever") - 0.1 + 0.08 * k, 0.3)
            plugs += [g, o]
        pp_ = pill(st, WX + 1.75, Y(3200), "plugs: cement,\nverified", P.PANEL2, P.SAFE, 0.16, 0.7, align="l")
        st.fade_in(pp_, W(4, "for ever") - 0.1, 0.4)

        # ---------------------------------------------------------------- dissolve out
        st.fade_out(A + G + stair + steel + [mud] + plugs + pp_, t_dis, 0.8)


def beat_seabed(st, tl):
    """The empty seabed of the cold open: what is left under the mud, then the camera rises to the surface."""
    b = tl["10.01"]
    s = b.sent
    t_dis = s[5] - 0.35
    t_rise0 = b.word(5, "barely a trace") - 0.2
    t_rise1 = b.end - 0.25
    SB, SURF = -1.0, 12.0
    rnd = random.Random(11)
    with st.span(t_dis, b.end):
        objs = []
        objs.append(st.rect(0, SURF + 6.0, 60, 12.0, P.BG, 3.0, role="hole"))                           # night sky
        objs.append(st.rect(0, (SURF + SB) / 2, 60, SURF - SB, P.SEA, 3.0))                            # the water
        for k in range(6):                                                                             # lighter near the top
            y0 = SB + (SURF - SB) * (0.45 + 0.09 * k)
            objs.append(st.rect(0, (y0 + SURF) / 2, 60, SURF - y0, "#2c6aa8", 3.01, alpha=0.06))
        objs.append(st.line([(-30, SURF), (30, SURF)], P.PORE, 0.05, 3.05, alpha=0.85))               # sea surface
        objs.append(st.rect(0, SB - 5.0, 60, 10.0, P.SEABED, 3.02))                                   # sediment
        objs.append(st.rect(0, SB - 0.04, 60, 0.08, "#8b7a5e", 3.03))
        for i in range(10):                                                                            # sediment ripples
            x = -10 + i * 2.2 + rnd.uniform(-0.4, 0.4)
            w, h = rnd.uniform(1.2, 2.2), rnd.uniform(0.06, 0.16)
            objs.append(st.poly([(x - w, SB), (x - w * 0.4, SB + h), (x + w * 0.3, SB + h * 0.8), (x + w, SB)], "#8b7a5e", 3.04))
        # the old cuttings mound around the site, low and smoothed over
        mound = [(-2.6 + 5.2 * i / 30, SB + 0.28 * math.exp(-((-2.6 + 5.2 * i / 30) / 1.2) ** 2)) for i in range(31)]
        objs.append(st.poly([(-2.6, SB)] + mound + [(2.6, SB)], "#94826a", 3.05))
        # under the mud, ghosted: cut casing stubs (~5 m down) and the surface plug; deeper plugs fade into the dark
        ghost = []
        for k, (name, hw, hh) in enumerate(CASING):
            ln = (1.2, 1.9, 2.7, 3.5)[k]                                   # deeper strings reach further down
            for sd in (-1, 1):
                ghost.append(st.rect(sd * hw * 1.4, SB - 0.25 - ln / 2, 0.06, ln, P.STEEL, 3.06, alpha=0.32))
        ghost.append(st.rect(0, SB - 0.8, 0.52, 0.85, P.CEMENT, 3.07, alpha=0.45))
        ghost.append(st.line([(-0.26, SB - 0.375), (0.26, SB - 0.375), (0.26, SB - 1.225), (-0.26, SB - 1.225)], P.SAFE, 0.03, 3.08,
                             alpha=0.5, closed=True))
        for (y0, h, a) in ((SB - 2.35, 0.35, 0.28), (SB - 2.95, 0.3, 0.22), (SB - 3.5, 0.8, 0.16)):
            ghost.append(st.rect(0, y0, 0.36, h, P.CEMENT, 3.07, alpha=a))
        st.fade_in(objs, t_dis, 0.8)
        st.fade_in(ghost, t_dis + 0.6, 1.2)
        lab = st.text("300 m down: barely a trace", 0.0, SB + 1.15, 0.3, P.TEXT, 3.2, kind="bold")
        sub = st.text("cut casing stubs and verified cement plugs, under the mud", 0.0, SB + 0.62, 0.17, P.MUTED, 3.2)
        st.fade_in(lab, s[5] + 0.2, 0.5)
        st.fade_in(sub, s[5] + 0.9, 0.5)
        st.fade_out([lab, sub], t_rise0 + 1.2, 0.6)

        # marine snow, three parallax layers that always fill the view
        snow = [(rnd.uniform(-9, 9), rnd.uniform(-5, 5), k) for k in (0, 1, 2) for _ in range(30)]

        def draw_snow(c, t, look):
            cx, cy, cw = st.cam_at(t)
            a = _ramp(t, t_dis, t_dis + 0.8)
            for layer, (rr, al, f) in enumerate(((0.025, 0.30, 0.6), (0.045, 0.42, 1.0), (0.08, 0.22, 1.5))):
                pos = []
                for (x0, y0, k) in snow:
                    if k != layer:
                        continue
                    y = y0 - 0.12 * t - cy * (f - 1.0)
                    y = (y - (-5)) % 10 - 5 + cy
                    x = x0 + 0.25 * math.sin(0.4 * t + x0)
                    if SB + 0.1 < y < SURF - 0.1:
                        pos.append((x, y))
                look.draw_particles(c, pos, "#bcd6f2", rr, al * a, glow=False)
        st.procedural(t_dis, b.end, 3.1, draw_snow)

        # the rise: from the seabed to the surface (camera only; nothing is left down there to look at)
        st.camera(t_rise0, t_rise1, cy=SURF - 2.2, width=16, interp="BEZIER")


# ======================================================================================================== 10.02
def beat_endcard(st, tl):
    b = tl["10.02"]
    with st.span(b.start, b.end):
        st.camera(b.start - 0.01, b.start, cx=0.0, cy=0.0, width=16, interp="CONSTANT")
        st.rect(0, 0, 16.5, 9.5, P.BG, 0.0, role="backdrop")
        t0 = b.start + 0.15
        ttl = st.text("THE HOLE THAT FIGHTS BACK", 0, 1.55, 0.72, P.TEXT, 0.3, kind="bold")
        rule = st.line([(-3.2, 0.95), (3.2, 0.95)], P.PORE, 0.05, 0.3)
        st.fade_in(ttl, t0, 0.6)
        st.draw_on(rule, t0 + 0.3, t0 + 1.3, "BEZIER")
        lines = [("Illustrative composite well: invented numbers, real physics.", P.TEXT, 0.25),
                 ("Norway-specific material carried a red NORWAY / NORSOK-SPECIFIC badge.", P.MUTED, 0.21),
                 ("Verify any requirement against NORSOK D-010 and the current regulations before relying on it.", P.MUTED, 0.21)]
        y = 0.3
        for k, (txt, colr, size) in enumerate(lines):
            o = st.text(txt, 0, y, size, colr, 0.3)
            st.fade_in(o, t0 + 1.0 + 0.5 * k, 0.5)
            y -= 0.5
        badge = pill(st, 0, -1.55, "NORWAY / NORSOK-SPECIFIC", P.NO_BADGE, "#ffffff", 0.15, 0.3)
        st.fade_in(badge, t0 + 1.6, 0.4)
        cr = st.text("Voice: Kokoro-82M neural TTS  ·  Animation, music and sound: generated in code", 0, -2.55, 0.17, P.MUTED, 0.3)
        st.fade_in(cr, t0 + 2.6, 0.6)


def build(st, tl):
    F.header(st, tl, t1=tl["10.01"].sent[5] - 0.35 + 0.8)
    beat_recap(st, tl)
    beat_seabed(st, tl)
    beat_endcard(st, tl)
