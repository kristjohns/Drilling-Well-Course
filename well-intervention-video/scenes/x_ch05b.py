"""Ch 5, beats 5.05 - 5.08 (called from ch05_coiled_tubing.build).

5.05 the bottom hole assembly: connector, check valves (flaps), disconnect (ball + pressure), the working tool
5.06 the force balance: push 40.5 kN (4.1 t) against buoyed weight 39 N/m: the balance point at 1,035 m (from the model)
5.07 fatigue: six bends per trip, strain 2.3 % versus yield 0.27 %, a paperclip, pressure shortens life, retire at ~80 %
5.08 reach: sinusoidal -> helical buckling -> lock-up; reach versus friction coefficient (from the model); remedies
"""
from __future__ import annotations
import math
import random

from scenes.common import palette as P, model as M
from scenes.common import kit as K
from scenes.common import ct as C
from scenes.common.chart import Chart


# ====================================================================================================== 5.05
def b505(st, tl):
    b = tl["5.05"]
    s = b.sent
    with st.span(b.start, b.end):
        cx = -3.9
        tube = st.rect(cx, 3.5, 0.4, 0.9, P.STEEL, 0.5, role="steel")
        # connector
        conn = [st.rect(cx, 2.85, 0.6, 0.55, P.STEEL_DK, 0.5, role="steel"), st.rect(cx, 2.85, 0.28, 0.55, P.BG, 0.52), st.rect(cx, 2.85, 0.42, 0.08, P.WARN, 0.55, role="solid")]
        # check valves: housing with two flappers
        y_c0, y_c1 = 2.5, 1.2
        chk = [st.rect(cx - 0.4, (y_c0 + y_c1) / 2, 0.14, y_c0 - y_c1, P.STEEL_DK, 0.5, role="steel"), st.rect(cx + 0.4, (y_c0 + y_c1) / 2, 0.14, y_c0 - y_c1, P.STEEL_DK, 0.5, role="steel"),
               st.rect(cx, (y_c0 + y_c1) / 2, 0.66, y_c0 - y_c1, P.BG, 0.45)]
        fl_l = st.rect(cx - 0.33, 2.0, 0.62, 0.07, P.WARN, 0.6, anchor="l", role="solid")
        fl_r = st.rect(cx + 0.33, 1.6, 0.62, 0.07, P.WARN, 0.6, anchor="r", role="solid")
        # disconnect: housing with a ball seat; the lower half can separate
        up_disc = [st.rect(cx - 0.4, 0.85, 0.14, 0.6, P.STEEL_DK, 0.5, role="steel"), st.rect(cx + 0.4, 0.85, 0.14, 0.6, P.STEEL_DK, 0.5, role="steel")]
        lo_disc = [st.rect(cx - 0.4, 0.3, 0.14, 0.5, P.PRIMARY_B, 0.5, role="flat"), st.rect(cx + 0.4, 0.3, 0.14, 0.5, P.PRIMARY_B, 0.5, role="flat"),
                   st.rect(cx - 0.18, 0.55, 0.24, 0.07, P.STEEL, 0.55, role="steel"), st.rect(cx + 0.18, 0.55, 0.24, 0.07, P.STEEL, 0.55, role="steel")]
        disc_bg = st.rect(cx, 0.6, 0.66, 1.1, P.BG, 0.45)
        # working tool (carousel)
        tool_parts = {}
        tool_parts["nozzle"] = [st.rect(cx, -0.55, 0.5, 1.0, P.STEEL, 0.55, role="steel")] + [st.line([(cx + dx, -1.05), (cx + dx * 2.2, -1.5)], P.SPACER, 0.05, 0.6) for dx in (-0.2, 0.0, 0.2)]
        tool_parts["motor + mill"] = [st.rect(cx, -0.35, 0.5, 0.65, P.PRIMARY_B, 0.55, role="flat"), st.rect(cx, -1.0, 0.44, 0.5, P.STEEL_DK, 0.55, role="steel")] + \
                                     [st.rect(cx + dx, -1.28, 0.08, 0.14, P.WARN, 0.6, role="solid") for dx in (-0.16, -0.05, 0.06, 0.17)]
        tool_parts["inflatable packer"] = [st.rect(cx, -0.55, 0.3, 1.0, P.STEEL, 0.55, role="steel"), st.ellipse(cx, -0.55, 0.45, 0.4, P.RUBBER, 0.56, role="solid")]
        tool_parts["perforating gun"] = [st.rect(cx, -0.65, 0.5, 1.3, P.STEEL_DK, 0.55, role="steel")] + [st.rect(cx, -0.2 - 0.4 * k, 0.52, 0.09, P.WARN, 0.6, role="solid") for k in range(3)]
        tool_parts["logging tool"] = [st.rect(cx, -0.65, 0.45, 1.3, P.STEEL, 0.55, role="steel")] + [st.rect(cx + 0.28, -0.3 - 0.4 * k, 0.12, 0.16, P.PORE, 0.6, role="solid") for k in range(2)]
        K.show(st, [tube] + conn + chk + [fl_l, fl_r] + up_disc + lo_disc + [disc_bg], b.start + 0.2, None, 0.5)
        for g in tool_parts.values():
            for o in g:
                o.hide_render = False
        # labels on the right
        def lab(text, y, t, t1=None, color=P.PANEL2, fg=P.TEXT):
            g = K.callout(st, text, -2.4, y, cx + 0.5, y, color=color, fg=fg, size=0.21, align="l")
            K.show(st, g, t, t1, 0.4)
        lab("connector: fixes the assembly to the tube", 2.85, b.word(1, "connector"), s[2])
        lab("check valves: two flaps, flow only goes down", 1.85, b.word(2, "check valves"), s[3])
        lab("disconnect: can release everything below", 0.85, b.word(3, "disconnect"), s[4])
        # sentence 2: flow down opens the flaps; well fluid cannot come up (flaps shut)
        t2 = b.word(2, "only open for flow going down")
        st.rotate(fl_l, t2, t2 + 0.5, -75)
        st.rotate(fl_r, t2, t2 + 0.5, 75)
        st.flow([(cx, 3.0), (cx, 0.9)], t2, t2 + 3.0, P.SPACER, n=6, speed=1.2, r=0.045)
        t2b = b.word(2, "cannot come up")
        st.rotate(fl_l, t2b - 0.2, t2b + 0.3, 0)
        st.rotate(fl_r, t2b - 0.2, t2b + 0.3, 0)
        up_arr = st.arrow(cx, 0.8, cx, 1.75, P.BAD, 0.06, 0.2, 0.9)
        K.show(st, up_arr, t2b, s[3], 0.3)
        K.xmark(st, cx, 1.35, 0.2, t2b + 0.3)
        # sentence 3: a ball is dropped, seats, pressure parts the tool
        ball = st.circle(cx, 3.6, 0.13, P.WARN, 0.8, role="orb")
        t3 = b.word(3, "drop a ball")
        K.show(st, [ball], t3 - 0.3, None, 0.2)
        st.move(ball, t3, t3 + 1.6, to=(cx, 0.62))
        st.rotate(fl_l, t3 + 0.3, t3 + 0.6, -75)
        st.rotate(fl_r, t3 + 0.3, t3 + 0.6, 75)
        st.rotate(fl_l, t3 + 1.0, t3 + 1.3, 0)
        st.rotate(fl_r, t3 + 1.0, t3 + 1.3, 0)
        pr = st.arrow(cx + 0.9, 1.6, cx + 0.9, 0.9, P.PORE, 0.07, 0.24, 0.8)
        pt = K.note(st, "pressure", cx + 1.15, 1.25, 0.19, P.PORE, align="l")
        t_sep = b.word(3, "parts the tool")
        K.show(st, pr + pt, t3 + 1.6, t_sep + 0.8, 0.3)
        low = lo_disc
        st.move(low, t_sep, t_sep + 0.5, dy=-0.5)
        sep = K.tag(st, cx + 1.9, 0.0, "released", color=P.WARN, fg=P.BG, size=0.21, z=0.9)
        K.show(st, sep, t_sep + 0.3, s[4], 0.3)
        # sentence 4: a carousel of working tools
        names = list(tool_parts.keys())
        ts = [b.word(4, "a jetting nozzle"), b.word(4, "a motor and mill"), b.word(4, "an inflatable packer"), b.word(4, "a perforating gun"), b.word(4, "a logging tool")]
        for i, nm in enumerate(names):
            t0 = ts[i] - 0.1
            t1 = ts[i + 1] - 0.1 if i + 1 < len(ts) else s[5] + 1.5
            K.show(st, tool_parts[nm], t0, t1, 0.3)
            g = K.callout(st, nm, -2.4, -0.7, cx + 0.3, -0.7, color=P.PRIMARY_B, fg=P.BG, size=0.22, align="l")
            K.show(st, g, t0, t1, 0.3)
        fin = K.tag(st, -0.3, -2.6, "same tube, different tool on the end", color=P.SAFE, fg=P.BG, size=0.26, z=0.9, align="l")
        K.show(st, fin, s[5], None, 0.5)


# ====================================================================================================== 5.06
def b506(st, tl):
    b = tl["5.06"]
    s = b.sent
    with st.span(b.start, b.end):
        F0 = M.ct_push_force_n() / 1000.0                 # kN
        w = M.ct_geom()["w_buoyed"] / 1000.0              # kN per m
        d_bal = M.balance_depth_m()
        Dmax = 2000.0
        # ---- left: ruler, the injector and the tube going in
        ky = 5.8 / Dmax
        top = 2.8
        ruler = [st.rect(-6.9, top - 2.9, 0.03, 5.8, P.MUTED, 0.3)]
        ticks = []
        for dm in (0, 500, 1000, 1500, 2000):
            ticks.append(st.rect(-6.9, top - dm * ky, 0.2, 0.025, P.MUTED, 0.3))
            ticks.append(st.text(f"{dm:,} m", -7.1, top - dm * ky, 0.17, P.MUTED, 0.3, align="r"))
        inj = [st.rect(-6.1, top + 0.45, 1.3, 0.7, P.PANEL2, 0.45, role="card"), st.text("injector", -6.1, top + 0.45, 0.19, P.TEXT, 0.5)]
        tube = st.rect(-6.1, top, 0.16, 0.001, P.STEEL, 0.5, anchor="t", role="steel")
        K.show(st, ruler + ticks + inj + [tube], b.start + 0.2, None, 0.5)
        t_a = s[2]
        t_b = b.word(4, "a kilometre") + 1.0
        t_c = s[6] + 0.5
        st.scale_to(tube, t_a, t_b, sy=d_bal * ky, interp="LINEAR")
        st.scale_to(tube, t_b, t_c, sy=Dmax * ky, interp="LINEAR")
        st.counter(-3.4, top - 1.55, t_a, t_b, 0, d_bal, "{:,.0f} m in the hole", 0.22, P.TEXT, 0.7, hold=t_b)
        st.counter(-3.4, top - 1.55, t_b, t_c, d_bal, Dmax, "{:,.0f} m in the hole", 0.22, P.TEXT, 0.7)
        # force arrows near the injector
        a_push = st.arrow(-5.3, top - 0.2, -5.3, top - 1.5, P.SAFE, 0.06, 0.22, 0.8)
        a_hold = st.arrow(-5.3, top - 1.5, -5.3, top - 0.2, P.PORE, 0.06, 0.22, 0.8)
        # s1: pressure pushes the tube out (about four tonnes)
        pt = st.arrow(-5.75, top - 1.3, -5.75, top - 0.1, P.BAD, 0.08, 0.28, 0.8)
        K.show(st, pt, s[1], None, 0.4)
        ptl = K.note(st, "pressure pushes the tube out:\n40.5 kN (4.1 t)", -5.4, top - 2.3, 0.21, P.BAD, align="l")
        K.show(st, ptl, s[1] + 0.3, None, 0.4)
        # injector arrow: push before the balance point, hold-back after it
        K.show(st, a_push, s[2], t_b, 0.4)
        K.show(st, a_hold, t_b, None, 0.4)
        lp = K.tag(st, -4.9, top - 0.85, "injector pushes", color=P.SAFE, fg=P.BG, size=0.2, z=0.9, align="l")
        lh = K.tag(st, -4.9, top - 0.85, "injector holds back", color=P.PORE, fg=P.BG, size=0.2, z=0.9, align="l")
        K.show(st, lp, s[2], t_b, 0.4)
        K.show(st, lh, t_b, None, 0.4)
        # ---- right: injector force against depth
        ch = Chart(st, 0.2, -2.3, 2.7, 4.5, (0, Dmax), (-45, 50))
        fr = ch.frame(xticks=[0, 500, 1000, 1500, 2000], yticks=[-40, 0, 40], xlabel="tube in the hole (m)", ylabel="injector force (kN)", fx="{:,.0f}", fy="{:+.0f}", tick_size=0.17)
        K.show(st, fr, s[1], None, 0.5)
        zero = st.rect(ch.x + ch.w / 2, ch.Y(0), ch.w, 0.025, P.TEXT, 0.4, alpha=0.8)
        pos = st.poly([ch.pt(0, 0), ch.pt(0, F0), ch.pt(d_bal, 0)], P.SAFE, 0.2, alpha=0.3)
        neg = st.poly([ch.pt(d_bal, 0), ch.pt(Dmax, F0 - w * Dmax), ch.pt(Dmax, 0)], P.PORE, 0.2, alpha=0.3)
        line = st.line([ch.pt(0, F0), ch.pt(Dmax, F0 - w * Dmax)], P.WARN, 0.07, 0.5)
        K.show(st, [zero, pos, neg], s[1], None, 0.5)
        K.show(st, [line], s[1], None, 0.1)
        st.draw_on(line, t_a, t_c, "LINEAR")
        dot = st.circle(ch.X(0), ch.Y(F0), 0.11, P.TEXT, 0.9, role="orb")
        K.show(st, [dot], t_a - 0.2, None, 0.3)
        st.move(dot, t_a, t_b, to=ch.pt(d_bal, 0), interp="LINEAR")
        st.move(dot, t_b, t_c, to=ch.pt(Dmax, F0 - w * Dmax), interp="LINEAR")
        l_push = st.text("push", ch.X(250), ch.Y(F0) - 0.55, 0.2, P.SAFE, 0.5, kind="bold")
        l_hold = st.text("hold back", ch.X(1550), ch.Y(-14), 0.2, P.PORE, 0.5, kind="bold")
        K.show(st, [l_push], s[2], None, 0.4)
        K.show(st, [l_hold], s[5], None, 0.4)
        # weight note
        wn = K.note(st, f"buoyed weight {w * 1000:.0f} N per metre", ch.X(1000), ch.Y(-40) + 0.1, 0.18, P.MUTED, align="c")
        K.show(st, wn, s[3], None, 0.4)
        # the balance point
        bal = st.ring(ch.X(d_bal), ch.Y(0), 0.28, 0.05, P.WARN, 0.9)
        bl = K.tag(st, ch.X(d_bal) - 0.2, ch.Y(0) + 0.7, f"balance point  {d_bal:,.0f} m", color=P.WARN, fg=P.BG, size=0.21, z=0.9)
        K.show(st, [bal] + bl, b.word(6, "balance point") - 0.3, None, 0.4)
        st.ripple(ch.X(d_bal), ch.Y(0), b.word(6, "balance point"), b.word(6, "balance point") + 2.0, P.WARN, period=0.8, r0=0.2, r1=0.8)
        eq = K.note(st, "40.5 kN  =  39 N/m × 1,035 m", -3.4, -3.2, 0.24, P.TEXT, align="c", kind="mono")
        K.show(st, eq, b.word(4, "balance"), None, 0.5)


# ====================================================================================================== 5.07
def b507(st, tl):
    b = tl["5.07"]
    s = b.sent
    with st.span(b.start, b.end):
        # reel, gooseneck, injector in one picture
        rx, ry, R = -6.0, -1.3, 1.5
        reel = K.drum(st, rx, ry, R, turns=5, color=P.STEEL)
        Cx, Cy, Rg = -2.6, 1.2, 1.25
        pre = [(rx, ry + R * 0.92), (-4.9, 0.55), (-3.9, 0.95), (Cx - Rg, Cy)]
        arc = C.arc_pts(Cx, Cy, Rg, 180, 0, 30)
        post = [(Cx + Rg, Cy), (Cx + Rg, -1.6)]
        path = pre + arc[1:] + post[0:]
        tube = st.line(path, P.STEEL, 0.14, 0.5)
        inj = [st.rect(Cx + Rg, 0.2, 1.3, 1.3, P.PANEL2, 0.4, role="card"), st.rect(Cx + Rg, 0.2, 0.14, 1.0, P.STEEL_DK, 0.45, role="solid")]
        K.show(st, reel.body + reel.turns + [tube] + inj, b.start + 0.2, None, 0.5)
        # bend zones: reel departure, over the gooseneck, straightened into the injector
        zone_pts = [pre[0:3], arc, [(Cx + Rg, Cy), (Cx + Rg, 0.8)]]
        zone_cols = [P.WARN, P.BAD, P.WARN]
        zones = [st.line(pts, c, 0.2, 0.55) for pts, c in zip(zone_pts, zone_cols)]
        zl = [K.note(st, "off the reel", -5.2, 0.15, 0.19, P.WARN, align="c"), K.note(st, "over the gooseneck", Cx, 2.85, 0.2, P.BAD, align="c"),
              K.note(st, "straightened", Cx + Rg + 0.2, 1.2 + 0.0, 0.19, P.WARN, align="l")]
        K.show(st, zones + zl[0] + zl[1] + zl[2], s[1], s[3], 0.4)
        # a bright mark runs along the tube again and again
        st.flow(path, s[1], b.end - 0.5, P.WARN, n=3, speed=1.1, r=0.07)
        # the number of bends in a trip
        cnt = st.counter(-4.3, -3.0, s[2] + 0.2, s[2] + 2.4, 0, 6, "{:.0f} bends per round trip", 0.3, P.WARN, 0.8, hold=s[3])
        sub = K.note(st, "3 going in  +  3 coming out", -4.3, -3.4, 0.2, P.MUTED, align="c")
        K.show(st, sub, s[2] + 0.5, s[3], 0.4)
        # strain versus yield (elastic estimate)
        eps_y = 552e6 / M.STEEL_E * 100          # %
        eps_b = M.ct_min_bend_strain(radius_m=1.1) * 100
        bx = 0.5
        t3 = s[3]
        bars = []
        for i, (lab, v, colr) in enumerate((("yield strain", eps_y, P.PORE), ("bending strain", eps_b, P.BAD))):
            y = 2.7 - i * 0.7
            tx = st.text(lab, bx - 0.1, y, 0.2, P.TEXT, 0.6, align="r")
            bar = st.rect(bx, y, 0.01, 0.34, colr, 0.55, anchor="l", role="flat")
            val = st.text(f"{v:.2f} %", bx + v / 2.5 * 2.0 + 0.2, y, 0.22, colr, 0.6, align="l", kind="mono")
            K.show(st, [tx, bar], t3 + i * 0.5, None, 0.3)
            st.scale_to(bar, t3 + i * 0.5, t3 + i * 0.5 + 0.8, sx=v / 2.5 * 2.0)
            K.show(st, [val], t3 + i * 0.5 + 0.7, None, 0.3)
            bars.append(bar)
        pl = K.note(st, "a couple of percent of strain: the steel flows plastically", 1.6, 1.25, 0.2, P.TEXT, align="c")
        K.show(st, pl, b.word(3, "flows plastically") - 1.2, s[4] - 0.3, 0.4)
        # a paperclip bent back and forth
        px, py = 1.7, 0.45
        clip_a = st.rect(px, py, 1.0, 0.07, P.STEEL, 0.6, anchor="r", role="steel")
        clip_b = st.rect(px, py, 1.0, 0.07, P.STEEL, 0.6, anchor="l", role="steel")
        K.show(st, [clip_a, clip_b], s[4], s[5] - 0.3, 0.3)
        t4 = s[4]
        for k in range(5):
            tt = t4 + 0.4 + 0.5 * k
            st.rotate(clip_b, tt, tt + 0.25, 50 if k % 2 == 0 else -50)
        st.move(clip_b, t4 + 3.2, t4 + 3.8, dy=-0.5)
        st.fade_out(clip_b, t4 + 3.4, 0.4)
        pc = K.note(st, "a paperclip: a few cycles, then it breaks", px, py - 0.65, 0.19, P.MUTED, align="c")
        K.show(st, pc, s[4] + 0.3, s[5] - 0.3, 0.4)
        # internal pressure makes it worse
        ch = Chart(st, 0.5, -2.7, 2.3, 1.7, (0, 10), (0, 10))
        fr = ch.frame(xticks=[], yticks=[], xlabel="pressure", ylabel="cycles to failure", tick_size=0.17)
        crv = st.line([ch.pt(0.5, 9.2), ch.pt(3, 6.3), ch.pt(6, 3.4), ch.pt(9.5, 1.2)], P.BAD, 0.06, 0.5)
        K.show(st, fr, s[5], None, 0.5)
        K.show(st, [crv], s[5], None, 0.1)
        st.draw_on(crv, s[5] + 0.3, s[5] + 1.8, "BEZIER")
        pt = K.note(st, "pressure shortens the life", 1.6, -3.5, 0.19, P.BAD, align="c")
        K.show(st, pt, s[5] + 0.3, None, 0.4)
        # fatigue life is tracked; the string is retired at about 80 %
        lb_x, lb_y = 1.7, 0.45
        back = st.rect(lb_x, lb_y, 2.6, 0.3, P.PANEL2, 0.45, role="pill")
        used = st.rect(lb_x - 1.3, lb_y, 0.01, 0.3, P.SAFE, 0.55, anchor="l", role="flat")
        tick = st.rect(lb_x - 1.3 + 2.6 * 0.8, lb_y, 0.04, 0.5, P.WARN, 0.6)
        lab = K.note(st, "fatigue life used", lb_x, lb_y + 0.45, 0.19, P.MUTED, align="c")
        ret = K.note(st, "retire at about 80 %", lb_x - 1.3 + 2.6 * 0.8, lb_y - 0.5, 0.19, P.WARN, align="c")
        t6 = s[6]
        K.show(st, [back, used, tick] + lab + ret, t6, None, 0.4)
        st.scale_to(used, t6 + 0.5, t6 + 4.5, sx=2.6 * 0.8)
        st.recolor(used, t6 + 2.5, t6 + 4.5, P.WARN)


# ====================================================================================================== 5.08
def b508(st, tl):
    b = tl["5.08"]
    s = b.sent
    with st.span(b.start, b.end):
        yc = 2.2
        x0, x1 = -6.6, 3.2
        walls = [st.rect((x0 + x1) / 2, yc + 0.55, x1 - x0, 0.1, P.STEEL_DK, 0.3, role="steel"), st.rect((x0 + x1) / 2, yc - 0.55, x1 - x0, 0.1, P.STEEL_DK, 0.3, role="steel"),
                 st.rect((x0 + x1) / 2, yc, x1 - x0, 1.0, P.BG, 0.2)]
        inj = [st.rect(x0 - 0.5, yc, 1.0, 1.4, P.PANEL2, 0.4, role="card"), st.text("injector", x0 - 0.5, yc, 0.17, P.TEXT, 0.5)]
        st.fade_in(walls + inj, b.start + 0.2, 0.5)
        yl = yc - 0.35                                   # the low side of the hole
        xe = 2.6
        straight = st.line([(x0, yl), (xe, yl)], P.STEEL, 0.1, 0.5)
        pts_s, pts_h = [], []
        for k in range(0, 241):
            x = x0 + (xe - x0) * k / 240
            f = (x - x0) / (xe - x0)
            amp_s = 0.17 * min(f * 3.0, 1.0) * 1.0
            pts_s.append((x, yl + 0.17 + amp_s * math.sin(2 * math.pi * (x - x0) / 1.5)))
            amp_h = 0.34 * min(f * 3.0, 1.0)
            pts_h.append((x, yc + amp_h * math.sin(2 * math.pi * (x - x0) / 0.62)))
        sine = st.line(pts_s, P.STEEL, 0.1, 0.5)
        helix = st.line(pts_h, P.STEEL, 0.1, 0.5)
        K.show(st, [straight], s[1], s[3], 0.4)
        K.show(st, [sine], b.word(3, "gentle wave") - 0.3, b.word(3, "a helix") - 0.2, 0.5)
        K.show(st, [helix], b.word(3, "a helix") - 0.1, None, 0.5)
        # push and friction arrows
        push = st.arrow(x0 + 0.1, yc + 0.0, x0 + 1.2, yc + 0.0, P.WARN, 0.1, 0.32, 0.8)
        K.show(st, push, s[1], None, 0.4)
        fr = []
        for i in range(8):
            xx = x0 + 1.0 + i * 1.1
            fr += st.arrow(xx, yc - 0.82, xx - 0.5, yc - 0.82, P.BAD, 0.04, 0.16, 0.6)
        K.show(st, fr, s[2], None, 0.4)
        ft = K.note(st, "friction builds along the tube, so the tube is in compression", -1.8, yc - 1.25, 0.2, P.BAD, align="c")
        K.show(st, ft, s[2], s[4], 0.4)
        # lock-up
        lock = K.tag(st, -1.5, 3.55, "LOCK-UP: no more tube goes in", color=P.BAD, fg=P.BG, size=0.26, z=0.9)
        K.show(st, lock, b.word(4, "no more tube"), None, 0.4)
        # bigger push arrow, no movement
        push2 = st.arrow(x0 + 0.1, yc, x0 + 1.9, yc, P.BAD, 0.14, 0.42, 0.85)
        K.show(st, push2, b.word(4, "however hard"), None, 0.4)
        # reach versus friction (from the model)
        mus = [0.1, 0.2, 0.3, 0.4]
        unit = 5.2 / M.horizontal_reach_m(0.1)
        bx = -4.4
        K.show(st, K.note(st, "reach before helical buckling  (2 in tube in 5½ in tubing)", -2.4, 0.15, 0.21, P.MUTED, align="c"), s[6] - 0.3, None, 0.4)
        for i, mu in enumerate(mus):
            L = M.horizontal_reach_m(mu)
            y = -0.45 - i * 0.65
            tx = st.text(f"μ = {mu:g}", bx - 0.15, y, 0.22, P.TEXT, 0.6, align="r", kind="mono")
            bar = st.rect(bx, y, 0.01, 0.4, P.SAFE if mu <= 0.2 else (P.WARN if mu <= 0.3 else P.BAD), 0.55, anchor="l", role="flat")
            val = st.text(f"{L:,.0f} m", bx + L * unit + 0.15, y, 0.22, P.TEXT, 0.6, align="l", kind="mono")
            tt = [b.word(6, "friction coefficient") + 0.3, b.word(6, "friction coefficient") + 0.9, b.word(6, "0.3"), b.word(6, "0.1")][i]
            K.show(st, [tx, bar], tt, None, 0.3)
            st.scale_to(bar, tt, tt + 0.8, sx=L * unit)
            K.show(st, [val], tt + 0.7, None, 0.3)
        # remedies
        rem = [("lubricants", b.word(7, "lubricants")), ("larger, stiffer tube", b.word(7, "larger and stiffer")), ("tractor or vibrating tool", b.word(7, "tractor"))]
        for i, (txt, t) in enumerate(rem):
            g = K.tag(st, 3.0, -0.8 - i * 0.7, txt, color=P.SAFE, fg=P.BG, size=0.22, z=0.9, align="l")
            K.show(st, g, t, None, 0.4)


def build(st, tl):
    b505(st, tl)
    b506(st, tl)
    b507(st, tl)
    b508(st, tl)
