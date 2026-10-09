"""Ch 5, beats 5.09 - 5.11 (called from ch05_coiled_tubing.build).

5.09 circulation: pump down the tube, return up the annulus carrying sand; annular velocity; foam; friction
5.10 nitrogen lift, acid placement across the perforations, scale removal (jet, then a mill on a downhole motor)
5.11 plugs, perforating, logging in a horizontal well, cement, fishing, velocity string; coiled tubing drilling
"""
from __future__ import annotations
import math
import random

from scenes.common import palette as P, model as M
from scenes.common import kit as K
from scenes.common import ct as C
from scenes.common.chart import Chart
from scenes.common.stage import hex_rgb
from scenes.common.look import lighten


def _tubing(st, cx, top, bot, half=1.3, z=0.3):
    walls = [st.rect(cx - half, (top + bot) / 2, 0.14, top - bot, P.STEEL, z, role="steel"), st.rect(cx + half, (top + bot) / 2, 0.14, top - bot, P.STEEL, z, role="steel"),
             st.rect(cx, (top + bot) / 2, 2 * half, top - bot, P.BG, z - 0.1)]
    return walls


# ====================================================================================================== 5.09
def b509(st, tl):
    b = tl["5.09"]
    s = b.sent
    with st.span(b.start, b.end):
        cx = -3.9
        top, bot = 3.5, -3.1
        walls = _tubing(st, cx, top, bot)
        sand = st.rect(cx, bot + 0.55, 2.6, 1.1, P.SAND, 0.32)
        perf = [st.rect(cx - 1.55, bot + 1.35, 0.5, 0.08, P.BG, 0.3, role="hole"), st.rect(cx + 1.55, bot + 1.35, 0.5, 0.08, P.BG, 0.3, role="hole")]
        st.fade_in(walls + [sand] + perf, b.start + 0.2, 0.5)
        # coiled tube lowered to the sand
        ct = st.rect(cx, top + 0.3, 0.3, 0.2, P.STEEL, 0.5, anchor="t", role="steel")
        nozzle = st.rect(cx, top + 0.1, 0.36, 0.3, P.WARN, 0.55, role="solid")
        d_end = bot + 1.45
        st.fade_in([ct, nozzle], s[0] + 0.5, 0.4)
        st.scale_to(ct, s[1] + 0.2, s[1] + 2.4, sy=top + 0.3 - d_end, interp="LINEAR")
        st.move(nozzle, s[1] + 0.2, s[1] + 2.4, dy=-(top + 0.1 - d_end + 0.0), interp="LINEAR")
        tl_ = K.callout(st, "coiled tube with a jetting nozzle", -1.8, 3.1, cx + 0.2, 3.0, size=0.21, align="l")
        K.show(st, tl_, s[1], s[2], 0.4)
        # fluid down the tube, up the annulus carrying sand
        t_f = s[1] + 2.4
        st.flow([(cx, top + 0.2), (cx, d_end)], t_f, s[5], P.SPACER, n=9, speed=1.6, r=0.05)
        for sd in (-1, 1):
            st.flow([(cx + sd * 0.7, d_end - 0.1), (cx + sd * 0.7, top + 0.3)], t_f + 0.3, s[3] - 0.2, P.SAND, n=4, speed=0.5, r=0.055, jitter=0.12)
        for sd in (-1, 1):
            st.flow([(cx + sd * 0.7, d_end - 0.1), (cx + sd * 0.7, top + 0.3)], s[4] - 0.2, b.end - 0.4, P.SAND, n=9, speed=1.5, r=0.055, jitter=0.12)
        jets = [st.line([(cx, d_end - 0.2), (cx + dx, d_end - 0.6)], P.SPACER, 0.05, 0.6) for dx in (-0.5, -0.25, 0.25, 0.5)]
        K.show(st, jets, t_f, None, 0.3)
        ann = K.callout(st, "returns up the annulus, carrying the sand", -1.8, 0.4, cx + 0.8, 0.4, size=0.21, align="l")
        K.show(st, ann, b.word(1, "returns"), s[2], 0.4)
        # annular velocity gauge
        gx0, gy = -1.6, 2.3
        axis = st.rect(gx0 + 1.5, gy, 3.0, 0.05, P.MUTED, 0.5)
        thr = st.rect(gx0 + 1.8, gy, 0.05, 0.6, P.WARN, 0.55)
        tt = st.text("annular velocity  →", gx0 + 1.5, gy + 0.55, 0.2, P.TEXT, 0.6)
        tl2 = st.text("carrying velocity", gx0 + 1.8, gy - 0.5, 0.18, P.WARN, 0.6)
        mk = st.circle(gx0 + 0.6, gy, 0.12, P.TEXT, 0.7, role="orb")
        K.show(st, [axis, thr, tt, tl2, mk], s[2], None, 0.4)
        t3, t4 = s[3], s[4]
        # slow: the sand falls out; fast: it travels to the surface
        grains = [st.circle(cx + (0.55 if k % 2 else -0.55) + 0.05 * (k % 3), 1.5 - 0.35 * k, 0.05, P.SAND, 0.6, role="disc") for k in range(6)]
        K.show(st, grains, t3, t4 - 0.2, 0.3)
        st.move(grains, t3 + 0.3, t4 - 0.3, dy=-1.6, interp="LINEAR")
        sl = K.tag(st, 1.5, 1.2, "too slow: the sand falls out", color=P.BAD, fg=P.BG, size=0.21, z=0.9, align="l")
        fs = K.tag(st, 1.5, 1.2, "fast enough: it travels to the surface", color=P.SAFE, fg=P.BG, size=0.21, z=0.9, align="l")
        K.show(st, sl, t3, t4 - 0.2, 0.3)
        K.show(st, fs, t4, s[5] - 0.3, 0.3)
        st.move(mk, t3 + 0.0, t3 + 0.5, dx=0.0)
        st.move(mk, t4, t4 + 1.0, dx=1.9)
        # returns leave at the top to a separator
        rt = st.arrow(cx + 0.7, top + 0.25, cx + 2.2, top + 0.25, P.SAND, 0.07, 0.24, 0.7)
        K.show(st, rt, t4 + 0.5, s[5], 0.4)
        # foam
        foam = []
        for sd in (-1, 1):
            st.flow([(cx + sd * 0.7, d_end - 0.1), (cx + sd * 0.7, top + 0.3)], s[5], b.end - 0.4, P.N2, n=12, speed=1.2, r=0.07, jitter=0.15)
        fo = K.tag(st, 1.5, 0.4, "nitrogen foam: a lighter fluid", color=P.N2, fg=P.BG, size=0.21, z=0.9, align="l")
        K.show(st, fo, b.word(5, "nitrogen"), s[6] - 0.3, 0.4)
        # trade: friction against tube size
        t6 = s[6]
        ch = Chart(st, 1.9, -2.5, 1.7, 2.2, (0, 10), (0, 10))
        fr = ch.frame(xticks=[], yticks=[], xlabel="tube size", ylabel="friction pressure", tick_size=0.17)
        crv = st.line([ch.pt(0.5, 9.3), ch.pt(2.5, 4.3), ch.pt(5.0, 2.2), ch.pt(9.5, 0.9)], P.BAD, 0.06, 0.5)
        K.show(st, fr, t6, None, 0.5)
        K.show(st, [crv], t6, None, 0.1)
        st.draw_on(crv, t6 + 0.3, t6 + 1.8, "BEZIER")
        tr = K.note(st, "bigger tube: more flow,\nbut heavier and stiffer", 1.9, -3.4, 0.2, P.TEXT, align="c")
        K.show(st, tr, t6 + 1.0, None, 0.5)


# ====================================================================================================== 5.10
def b510(st, tl):
    b = tl["5.10"]
    s = b.sent
    with st.span(b.start, b.end):
        cx = -3.9
        top, bot = 3.5, -3.1
        walls = _tubing(st, cx, top, bot)
        st.fade_in(walls, b.start + 0.2, 0.5)
        # job list on the right (current job highlighted)
        jobs = [("1  nitrogen lift", s[1]), ("2  acid placement", s[3]), ("3  scale removal", s[4])]
        for i, (txt, t) in enumerate(jobs):
            g = K.tag(st, 1.3, 2.9 - i * 0.7, txt, color=P.PANEL2, size=0.23, z=0.9, align="l")
            K.show(st, g, t, None, 0.4)

        # ---------------- 1: nitrogen lift: gas from the nozzle bubbles up through the column and lightens it
        t1a, t1b = s[1] - 0.2, s[3] - 0.3
        from scenes.common import pdraw as D
        import random
        rnd = random.Random(11)
        bub = [(rnd.uniform(-0.95, 0.95), rnd.uniform(0, 1), rnd.uniform(0.6, 1.2), rnd.uniform(0.03, 0.07)) for _ in range(70)]
        t_g = s[1] + 0.8

        def n2_lift(c, t, look):
            a = D.vis(t, t1a, t1b, 0.4)
            if a <= 0:
                return
            gas = D.ramp(t, t_g, s[2] + 1.5)                   # how gasified the column is
            lvl = 3.0
            D.fluid(c, cx - 1.08, bot, cx + 1.08, lvl, P.OIL, (0.6 - 0.32 * gas) * a)
            D.gradient_rect_v(c, cx - 1.08, bot, cx + 1.08, lvl, P.N2, P.N2, 0.0 + 0.28 * gas * a)
            # the coiled tube with the nozzle at the bottom
            D.steel(c, cx - 0.15, -2.4, cx + 0.15, top + 0.3, P.STEEL, a)
            D.flat(c, cx - 0.2, -2.6, cx + 0.2, -2.4, P.WARN, a, r=0.03)
            # bubbles rising from the nozzle: more as the injection builds
            if t > t_g:
                n_on = int(len(bub) * min(1.0, (t - t_g) / 2.5))
                for i, (bx, ph, sp, r) in enumerate(bub[:n_on]):
                    u = (ph + (t - t_g) * sp * 0.35) % 1.0
                    y = -2.4 + u * (lvl + 2.4)
                    x = cx + bx * (0.25 + 0.75 * min(u * 3, 1.0)) + 0.04 * math.sin(7 * u + i)
                    D.disc(c, x, y, r * (0.8 + 0.6 * u), lighten(hex_rgb(P.N2), 0.35), 0.85 * a * min(1.0, 4 * (1 - u)))
            # liquid unloaded out of the top
            if t > t_g + 0.6:
                D.arrow(c, cx + 1.25, 3.25, cx + 2.6, 3.25, P.OIL, 0.07, 0.22, a * D.lin(t, t_g + 0.6, t_g + 1.0))

        st.procedural(b.start, b.end, 0.22, n2_lift)
        st.flow([(cx, top), (cx, -2.45)], s[1] + 0.3, t1b, P.N2, n=8, speed=1.6, r=0.05, z=0.55)
        # the reservoir flows in as the column lightens
        inflow = [st.arrow(cx + 2.5, -2.6 - 0.0 + 0.2 * k, cx + 1.4, -2.6 - 0.0 + 0.2 * k, P.OIL, 0.05, 0.18, 0.6) for k in range(3)]
        K.show(st, sum([list(a) for a in inflow], []), s[2] + 1.0, t1b, 0.4)
        nl = K.callout(st, "nitrogen bubbles lighten the column", cx + 1.6, 0.6, cx + 0.5, 0.6, size=0.18, align="l", z=0.9)
        K.show(st, nl, t_g + 0.8, t1b, 0.4)
        g1 = K.dial(st, cx + 3.0, 1.9, 0.5, s[2] - 0.2, s[2] + 1.6, 60, 175, color=P.PORE)
        g1l = st.text("column pressure", cx + 3.0, 1.25, 0.18, P.MUTED, 0.6)
        K.show(st, g1 + [g1l], s[2] - 0.3, t1b, 0.4)
        # ---------------- 2: acid across the perforations
        t2a, t2b = s[3] - 0.2, s[4] - 0.3
        pf = []
        for k in range(5):
            y = -1.2 + 0.55 * k
            for sd in (-1, 1):
                pf.append(st.rect(cx + sd * 1.55, y, 0.5, 0.09, P.BG, 0.3, role="hole"))
        sand2 = [st.rect(cx - 2.2, -0.1, 1.2, 3.4, P.SAND, 0.12), st.rect(cx + 2.2, -0.1, 1.2, 3.4, P.SAND, 0.12)]
        ct2 = st.rect(cx, top + 0.3, 0.3, top + 0.3 - 1.4, P.STEEL, 0.5, anchor="t", role="steel")
        noz = st.rect(cx, 1.5, 0.4, 0.3, P.WARN, 0.6, role="solid")
        K.show(st, pf + sand2 + [ct2, noz], t2a, t2b, 0.4)
        # the tube moves up and down across the zone
        y_lo, y_hi = 1.6, -1.6
        legs = [(s[3] + 0.5, s[3] + 1.5, -2.8), (s[3] + 1.5, s[3] + 3.0, +2.8), (s[3] + 3.0, s[3] + 4.2, -2.0)]
        cur = 1.5
        for a, c_, dy in legs:
            st.move(noz, a, c_, dy=dy, interp="LINEAR")
            st.scale_to(ct2, a, c_, sy=(top + 0.3 - (cur + dy)), interp="LINEAR")
            cur += dy
        st.flow([(cx, 1.9), (cx, 1.3)], s[3] + 0.5, t2b, P.ACID, n=3, speed=0.8, r=0.05)
        for k in range(5):
            y = -1.2 + 0.55 * k
            for sd in (-1, 1):
                st.flow([(cx + sd * 0.5, y), (cx + sd * 2.0, y)], s[3] + 1.0 + 0.3 * k, t2b, P.ACID, n=3, speed=0.7, r=0.05)
        cov = st.rect(cx + 3.2, -1.2, 0.3, 0.001, P.ACID, 0.6, anchor="b", role="flat")
        covb = st.rect(cx + 3.2, 0.0, 0.3, 2.5, P.PANEL2, 0.5, role="pill")
        covl = st.text("coverage", cx + 3.2, 1.45, 0.18, P.MUTED, 0.6)
        K.show(st, [covb, covl, cov], t2a, t2b, 0.4)
        st.scale_to(cov, s[3] + 0.8, s[3] + 4.4, sy=2.4, interp="LINEAR")
        al = K.tag(st, cx + 3.0, -2.0, "moved up and down: every part is treated", color=P.ACID, fg=P.BG, size=0.2, z=0.9)
        K.show(st, al, b.word(3, "moved up and down"), t2b, 0.4)
        # ---------------- 3: scale removal
        t3a = s[4] - 0.2
        crust = []
        for sd in (-1, 1):
            r = st.rect(cx + sd * 1.1, 1.7, 0.4, 2.7, P.SCALE, 0.28, role="flat")
            crust.append(r)
        plug = st.rect(cx, -1.4, 2.0, 0.9, P.SCALE, 0.28, role="flat")
        K.show(st, crust + [plug], t3a, None, 0.4)
        ct3 = st.rect(cx, top + 0.3, 0.3, top + 0.3 - 2.0, P.STEEL, 0.5, anchor="t", role="steel")
        K.show(st, [ct3], s[5] - 0.3, None, 0.4)
        # soft scale is washed off by a jet
        jet = [st.line([(cx, 1.6), (cx + dx, 1.9 + dy)], P.SPACER, 0.05, 0.6) for dx, dy in ((-0.7, 0.2), (0.7, 0.2), (-0.6, -0.5), (0.6, -0.5))]
        t5 = b.word(5, "A jet of water")
        K.show(st, jet, t5, b.word(5, "hard scale"), 0.3)
        st.fade_out(crust, t5 + 0.6, 2.5)
        jl = K.tag(st, cx + 2.8, 1.8, "jet: washes soft scale off", color=P.SPACER, fg=P.BG, size=0.2, z=0.9)
        K.show(st, jl, t5, b.word(5, "hard scale"), 0.3)
        # hard scale needs a mill driven by a downhole motor
        t6 = b.word(5, "hard scale")
        st.scale_to(ct3, t6 + 0.5, t6 + 2.0, sy=top + 0.3 - (-0.35), interp="LINEAR")
        motor = [st.rect(cx, -0.1, 0.62, 0.9, P.PRIMARY_B, 0.55, role="flat")]
        spiral = [st.line([(cx - 0.18, -0.45 + 0.17 * k), (cx + 0.18, -0.36 + 0.17 * k)], P.PANEL2, 0.04, 0.6, role="hair") for k in range(5)]
        mill = st.rect(cx, -0.78, 0.8, 0.26, P.WARN, 0.6, role="solid")
        teeth = [st.rect(cx + dx, -0.94, 0.07, 0.14, P.STEEL, 0.62, role="steel") for dx in (-0.3, -0.1, 0.1, 0.3)]
        gpart = motor + spiral + [mill] + teeth
        K.show(st, gpart, t6 + 0.2, None, 0.5)
        st.move(gpart, t6 + 0.5, t6 + 2.0, dy=-0.0)
        st.scale_to(plug, t6 + 3.0, b.end - 0.5, sy=0.15, interp="LINEAR")
        st.move(plug, t6 + 3.0, b.end - 0.5, dy=-0.35, interp="LINEAR")
        st.move(gpart, t6 + 3.0, b.end - 0.5, dy=-0.7, interp="LINEAR")
        st.scale_to(ct3, t6 + 3.0, b.end - 0.5, sy=top + 0.3 - (-1.05), interp="LINEAR")
        for k, tooth in enumerate(teeth):
            st.rotate(tooth, t6 + 0.6, b.end - 0.4, 360 * 6)
        chips = st.flow([(cx, -1.3), (cx + 1.1, -0.7)], t6 + 3.0, b.end - 0.4, P.SCALE, n=6, speed=0.7, r=0.05, jitter=0.2)
        ml = K.tag(st, cx + 2.8, -0.2, "mill turned by a motor", color=P.PRIMARY_B, fg=P.BG, size=0.2, z=0.9)
        nr = K.tag(st, cx + 2.8, -0.85, "the tube does not rotate", color=P.SAFE, fg=P.BG, size=0.2, z=0.9)
        K.show(st, ml, b.word(6, "A mill"), None, 0.4)
        K.show(st, nr, b.word(6, "never"), None, 0.4)
        st.flow([(cx, top), (cx, -0.3)], t6 + 0.8, b.end - 0.4, P.SPACER, n=8, speed=1.6, r=0.045)


# ====================================================================================================== 5.11
def b511(st, tl):
    b = tl["5.11"]
    s = b.sent
    with st.span(b.start, b.end):
        xs = [-6.0, -3.0, 0.0]
        ys = [1.55, -1.7]
        tiles = [("sets plugs and packers", b.word(0, "sets plugs")), ("perforates", b.word(0, "perforates")), ("logs a horizontal well", b.word(0, "pushes a logging")),
                 ("places cement", b.word(1, "places cement")), ("fishes", b.word(1, "fishes")), ("velocity string", b.word(2, "velocity string"))]
        for i, (nm, t) in enumerate(tiles):
            x, y = xs[i % 3], ys[i // 3]
            card = K.card(st, x, y, 2.85, 2.95, P.PANEL, 0.2)
            ttl = st.text(nm, x, y + 1.25, 0.22, P.TEXT, 0.5, kind="bold")
            g = card + [ttl]
            if i == 0:     # plug expands in a tubing
                w1 = [st.rect(x - 0.6, y - 0.2, 0.1, 1.8, P.STEEL, 0.3, role="steel"), st.rect(x + 0.6, y - 0.2, 0.1, 1.8, P.STEEL, 0.3, role="steel")]
                tb = st.rect(x, y + 0.45, 0.1, 0.9, P.STEEL, 0.4, role="steel")
                pl_ = st.rect(x, y - 0.3, 0.6, 0.45, P.RUBBER, 0.5, role="solid")
                g += w1 + [tb, pl_]
                st.scale_to(pl_, t + 1.0, t + 2.0, sx=1.1)
                st.move(tb, t + 2.5, t + 3.3, dy=0.6)
            elif i == 1:   # perforating gun flash
                w1 = [st.rect(x - 0.6, y - 0.2, 0.1, 1.8, P.STEEL, 0.3, role="steel"), st.rect(x + 0.6, y - 0.2, 0.1, 1.8, P.STEEL, 0.3, role="steel")]
                gun = st.rect(x, y - 0.1, 0.4, 0.9, P.STEEL_DK, 0.5, role="steel")
                fl = [st.line([(x + 0.2, y - 0.1 + dy), (x + 0.9, y - 0.1 + dy * 1.8)], P.WARN, 0.06, 0.6) for dy in (-0.2, 0.0, 0.2)]
                g += w1 + [gun]
                K.show(st, fl, t + 1.2, t + 2.5, 0.1)
            elif i == 2:   # horizontal pipe, tool pushed along
                hp = [st.rect(x, y + 0.05, 2.4, 0.08, P.STEEL, 0.3, role="steel"), st.rect(x, y - 0.55, 2.4, 0.08, P.STEEL, 0.3, role="steel")]
                tool = st.rect(x - 0.5, y - 0.25, 0.4, 0.3, P.WARN, 0.5, role="solid")
                tube_h = st.rect(x - 1.2, y - 0.25, 0.01, 0.1, P.STEEL, 0.4, anchor="l", role="steel")
                g += hp + [tool, tube_h]
                st.move(tool, t + 0.8, t + 3.0, dx=1.5)
                st.scale_to(tube_h, t + 0.8, t + 3.0, sx=2.2)
            elif i == 3:   # cement into perforations
                w1 = [st.rect(x - 0.6, y - 0.2, 0.1, 1.8, P.STEEL, 0.3, role="steel"), st.rect(x + 0.6, y - 0.2, 0.1, 1.8, P.STEEL, 0.3, role="steel")]
                cem = st.rect(x, y - 0.8, 1.1, 0.001, P.CEMENT, 0.45, anchor="b")
                g += w1
                K.show(st, [cem], t + 0.8, None, 0.2)
                st.scale_to(cem, t + 0.8, t + 3.0, sy=1.3)
            elif i == 4:   # hook and fish
                w1 = [st.rect(x - 0.6, y - 0.2, 0.1, 1.8, P.STEEL, 0.3, role="steel"), st.rect(x + 0.6, y - 0.2, 0.1, 1.8, P.STEEL, 0.3, role="steel")]
                fish = st.rect(x, y - 0.75, 0.3, 0.8, P.STEEL_DK, 0.5, role="steel", rot=-12)
                hook = st.line([(x, y + 0.9), (x, y + 0.2), (x + 0.12, y + 0.05)], P.WARN, 0.06, 0.6)
                g += w1 + [fish, hook]
                st.move([hook], t + 0.8, t + 2.0, dy=-0.55)
                st.move([hook, fish], t + 2.3, t + 3.5, dy=1.0)
            else:          # velocity string inside the tubing
                w1 = [st.rect(x - 0.6, y - 0.2, 0.1, 1.8, P.STEEL, 0.3, role="steel"), st.rect(x + 0.6, y - 0.2, 0.1, 1.8, P.STEEL, 0.3, role="steel")]
                vs = [st.rect(x - 0.12, y + 0.0, 0.04, 1.8, P.WIRE, 0.5, role="steel"), st.rect(x + 0.12, y + 0.0, 0.04, 1.8, P.WIRE, 0.5, role="steel")]
                g += w1 + vs
                st.flow([(x, y - 0.8), (x, y + 0.8)], t + 1.0, b.end - 0.3, P.GAS, n=5, speed=1.2, r=0.04)
            K.show(st, g, t - 0.3, None, 0.5)
        # coiled tubing drilling: a side-track out of the existing well
        sx_, sy_ = 4.9, -0.1
        K.show(st, K.card(st, sx_, sy_, 5.6, 6.1, P.PANEL, 0.2), s[3] - 0.3, None, 0.5)
        main = [st.rect(sx_ - 1.6, sy_ + 0.4, 0.5, 4.8, P.STEEL, 0.3, role="steel"), st.rect(sx_ - 1.6, sy_ + 0.4, 0.34, 4.8, P.BG, 0.31)]
        win = st.rect(sx_ - 1.38, sy_ - 0.6, 0.1, 0.5, P.BG, 0.4, role="hole")
        bpts = [(sx_ - 1.4, sy_ - 0.6), (sx_ - 0.6, sy_ - 1.1), (sx_ + 0.4, sy_ - 1.45), (sx_ + 1.4, sy_ - 1.45), (sx_ + 2.2, sy_ - 1.6)]
        branch = st.line(bpts, P.OIL, 0.16, 0.5)
        ctb = st.rect(sx_ - 1.6, sy_ + 1.55, 0.1, 3.0, P.STEEL, 0.5, role="steel")
        lab_t = st.text("coiled tubing drilling", sx_ + 0.5, sy_ + 2.7, 0.26, P.TEXT, 0.6, kind="bold")
        lab_s = K.note(st, "a side-track out of the existing well,\nthrough its tubing, without a rig", sx_, sy_ - 2.55, 0.21, P.MUTED, align="c")
        t = b.word(3, "coiled tubing drilling")
        K.show(st, main + [win, ctb, lab_t] + lab_s, s[3] - 0.2, None, 0.5)
        K.show(st, [branch], t, None, 0.1)
        st.draw_on(branch, t + 0.6, b.end - 1.0, "LINEAR")


def build(st, tl):
    b509(st, tl)
    b510(st, tl)
    b511(st, tl)
