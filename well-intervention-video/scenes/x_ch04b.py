"""Ch 4, beats 4.05 - 4.07 (called from ch04_wireline.build).

4.05 setting a plug: lock mandrel past the landing nipple, pull up, keys catch the groove, jar down, pull test; retrieval after equalising
4.06 changing a gas-lift valve with the kick-over tool (orient, kick over, latch, pull, set a new one)
4.07 other slickline jobs; the limits: cannot push or pump; gravity runs out with inclination (tan i = 1 / friction)
"""
from __future__ import annotations
import math

from scenes.common import palette as P, model as M
from scenes.common import kit as K
from scenes.common import insets as I
from scenes.common import tools as T
from scenes.common.chart import Chart


# ====================================================================================================== 4.05
def b405(st, tl):
    b = tl["4.05"]
    s = b.sent
    with st.span(b.start, b.end):
        cx, SC = -3.4, 1.2
        cy = -0.9
        ni = I.nipple_inset(st, cx, cy, SC, y_top=3.75, y_bot=-3.45)
        base = ni.walls + ni.bore + ni.body
        st.fade_in(base, b.start + 0.1, 0.5)
        lab_n = K.callout(st, "landing nipple: locking groove", -0.3, cy + 0.0, cx + ni.B * 1.12 + 0.12, cy, size=0.21)
        K.show(st, lab_n, s[0] + 0.2, s[1] + 1.5, 0.4)
        # fluid below the plug (oil) and above (empty until equalised)
        # ---- plug assembly with its running tool, jar and wire, raised above the nipple
        U = 2.2
        neck_top = cy + 0.6 * SC + U
        zz = 0.38
        plug = T.plug_assembly(st, cx, neck_top, SC, zz)
        y_rt = neck_top + 0.6 * SC
        rt = T.running_tool(st, cx, y_rt, SC, zz)
        y_jar = y_rt + 1.1 * SC + 0.15
        jar = T.jar_closed(st, cx, y_jar, SC, zz)
        wire = st.rect(cx, 4.4, 0.035, 4.4 - y_jar, P.WIRE, zz + 0.05, anchor="t", role="steel")
        grp_all = plug.parts + rt.parts + jar.parts
        K.show(st, grp_all + [wire], s[1] - 0.2, None, 0.5)
        run_group = rt.parts + jar.parts

        def move_all(t0, t1, dy):
            st.move(grp_all, t0, t1, dy=dy)
            st.scale_to(wire, t0, t1, sy=wire_h[0] - dy)
            wire_h[0] -= dy
        wire_h = [4.4 - y_jar]

        def move_run(t0, t1, dy):
            st.move(run_group, t0, t1, dy=dy)
            st.scale_to(wire, t0, t1, sy=wire_h[0] - dy)
            wire_h[0] -= dy
        lbl_lm = K.callout(st, "lock mandrel: spring-loaded keys", -0.3, 2.3, cx + 0.5 * SC + 0.1, plug.y_keys, size=0.21)
        K.show(st, lbl_lm, b.word(1, "lock mandrel"), s[2], 0.4)
        t2 = s[2]
        # sentence 2: lowered past the nipple, pulled up gently, keys catch the groove
        move_all(t2 + 0.2, t2 + 2.6, -(U + 1.1))
        # the keys are compressed while passing through the seal bore: they ride in the bore, then spring out into the groove
        t_up = t2 + 3.2
        move_all(t_up, t_up + 1.4, +1.1)
        for k, sd in zip(plug.kobj, (-1, 1)):
            st.move(k, t_up + 1.4, t_up + 1.8, dx=sd * 0.22 * SC)
        lt = K.callout(st, "keys catch the groove", -0.3, cy - 0.7, cx + 0.8, cy, size=0.21, color=P.WARN, fg=P.BG)
        K.show(st, lt, t_up + 1.3, s[3], 0.4)
        # sentence 3: downward jar locks them in and shears the running tool free
        t3 = s[3]
        st.move(grp_all, t3 + 0.3, t3 + 0.45, dy=-0.12)
        st.move(grp_all, t3 + 0.45, t3 + 0.7, dy=0.12)
        st.fade_out(rt.pin, t3 + 0.5, 0.2)
        sh = K.tag(st, -0.3, 1.8, "pin shears: the plug is released", color=P.BAD, fg=P.BG, size=0.21, z=0.9)
        K.show(st, sh, t3 + 0.4, s[4] - 0.2, 0.3)
        # the running tool, jar and wire lift away
        move_run(t3 + 1.2, t3 + 2.4, +1.3)
        # sentence 4: pull test
        pt = st.arrow(cx + 1.3, 2.6, cx + 1.3, 3.5, P.PORE, 0.07, 0.26, 0.9)
        K.show(st, pt + K.note(st, "pull test: it holds", cx + 1.55, 3.05, 0.21, P.PORE, align="l"), s[4], s[5] - 0.2, 0.4)
        ck = K.check(st, cx + 2.0, 0.5, s[4] + 1.2)
        K.show(st, ck, s[4] + 1.2, s[5] - 0.2, 0.2)
        # sentence 5: the tubing below the plug is isolated, work above in safety. The tool leaves.
        move_run(s[5] + 0.3, s[5] + 2.0, +3.4)
        y_seal = cy - 0.9
        below = st.rect(cx, (y_seal - 0.2 + ni.bot) / 2, 0.8, y_seal - 0.2 - ni.bot, P.OIL, 0.15, alpha=0.5)
        K.show(st, below, s[5], None, 0.5)
        iso = K.tag(st, -0.3, -2.4, "below the plug: isolated, 200 bar", color=P.OIL, fg=P.BG, size=0.21, z=0.9)
        abv = K.tag(st, -0.3, 2.3, "above the plug: 0 bar, safe to work", color=P.SAFE, fg=P.BG, size=0.21, z=0.9)
        K.show(st, iso, s[5] + 0.2, None, 0.4)
        K.show(st, abv, s[5] + 0.6, s[6] - 0.3, 0.4)
        steps = K.steps_list(st, 3.8, -0.15, ["run in past the nipple", "pull up: keys catch the groove", "jar down: locked, pin shears", "pull test: it holds", "below the plug: isolated",
                                             "pulling tool latches the neck", "equalise, jar up: plug out"],
                             [s[2] + 0.2, t_up + 1.3, t3 + 0.2, s[4], s[5], t6_ := b.word(6, "a pulling tool"), b.word(7, "equalised")], size=0.2, dy=0.5, t_out=s[8] - 0.2)
        # ---- retrieval: a pulling tool latches onto the fishing neck
        y_rt2 = (cy + 0.6 * SC) + 0.6 * SC
        D2 = 3.4
        rt2 = T.running_tool(st, cx, y_rt2 + D2, SC, zz, color=P.WARN)
        jar2 = T.jar_closed(st, cx, y_rt2 + D2 + 1.1 * SC + 0.15, SC, zz)
        wire2 = st.rect(cx, 4.4, 0.035, 4.4 - (y_rt2 + D2 + 1.1 * SC + 0.15), P.WIRE, zz + 0.05, anchor="t", role="steel")
        grp2 = rt2.parts + jar2.parts
        h2 = [4.4 - (y_rt2 + D2 + 1.1 * SC + 0.15)]
        t6 = b.word(6, "a pulling tool")
        K.show(st, grp2 + [wire2], t6 - 0.2, None, 0.5)
        st.move(grp2, t6 + 0.2, t6 + 2.6, dy=-D2)
        st.scale_to(wire2, t6 + 0.2, t6 + 2.6, sy=h2[0] + D2)
        pl = K.callout(st, "pulling tool latches the fishing neck", -0.3, 1.2, cx + 0.3, cy + 0.6 * SC + 0.1, size=0.21)
        K.show(st, pl, t6 + 1.8, b.word(7, "equalised") - 0.4, 0.4)
        # sentence 7: equalise first: the prong opens a port, the pressure above rises to match
        t7 = b.word(7, "equalised") - 0.3
        top_fill = st.rect(cx, (cy + 0.6 * SC + 3.75) / 2 + 0.0, 0.8, 3.75 - (cy + 0.6 * SC), P.OIL, 0.15, alpha=0.5)
        K.show(st, top_fill, t7 + 0.4, None, 1.6)
        c_ab = st.counter(1.15, 2.3, t7 + 0.4, t7 + 2.0, 0, 200, "above: {:.0f} bar", 0.24, P.PORE, 0.9, hold=b.end - 0.2)
        c_be = st.text("below: 200 bar", 1.15, 1.75, 0.24, P.OIL, 0.9, kind="mono")
        K.show(st, [c_be], t7, None, 0.4)
        eq = K.tag(st, 1.15, 1.2, "equalised", color=P.SAFE, fg=P.BG, size=0.22, z=0.9)
        K.show(st, eq, t7 + 2.0, None, 0.4)
        # keys retract on the upward jar; the plug comes out with the tool
        t_out = t7 + 2.6
        st.move(plug.kobj[0], t_out - 0.4, t_out - 0.1, dx=+0.22 * SC)
        st.move(plug.kobj[1], t_out - 0.4, t_out - 0.1, dx=-0.22 * SC)
        # sentence 8: the warning (the plug that was not equalised)
        t8 = s[8]
        wx, wy = 5.1, -1.6
        warn_panel = K.card(st, wx + 0.9, wy, 3.9, 3.2, P.PANEL, 0.2)
        w_tub = [st.rect(wx, wy, 0.9, 2.8, P.OIL, 0.25, alpha=0.4), st.rect(wx - 0.5, wy, 0.1, 2.8, P.STEEL, 0.3, role="steel"), st.rect(wx + 0.5, wy, 0.1, 2.8, P.STEEL, 0.3, role="steel")]
        w_plug = st.rect(wx, wy - 0.3, 0.8, 0.4, P.STEEL_DK, 0.4, role="steel")
        w_up = st.arrow(wx + 0.0, wy - 1.0, wx, wy - 0.45, P.BAD, 0.09, 0.3, 0.6)
        w_t1 = st.text("200 bar", wx + 1.75, wy - 0.9, 0.22, P.OIL, 0.5, kind="mono")
        w_t2 = st.text("0 bar", wx + 1.75, wy + 0.8, 0.22, P.MUTED, 0.5, kind="mono")
        w_lab = K.tag(st, wx + 0.9, wy + 1.75, "not equalised", color=P.BAD, fg=P.BG, size=0.2, z=0.9)
        w_blow = K.note(st, "the plug is blown up the hole", wx + 0.9, wy - 1.27, 0.19, P.BAD, align="c")
        K.show(st, warn_panel + w_tub + [w_plug, w_t1, w_t2] + w_up + w_lab, t8 - 0.2, None, 0.5)
        K.show(st, w_blow, t8 + 1.0, None, 0.4)
        st.move(w_plug, t8 + 0.9, t8 + 1.3, dy=1.1)
        st.ripple(wx, wy + 0.8, t8 + 1.3, t8 + 2.6, P.BAD, period=0.6, r0=0.2, r1=0.9)
        # finally everything comes out of the well together
        t_f = b.end - 2.6
        st.move(plug.parts + grp2, t_f, t_f + 2.0, dy=+3.2)
        st.scale_to(wire2, t_f, t_f + 2.0, sy=h2[0] + D2 - 3.2)


# ====================================================================================================== 4.06
def b406(st, tl):
    b = tl["4.06"]
    s = b.sent
    with st.span(b.start, b.end):
        cx, cy, SC = -3.5, -0.3, 1.45
        md = I.mandrel_inset(st, cx, cy, SC, valve=True, open_top=True)
        base = md.body + md.bore + md.pocket + md.ports
        st.fade_in(base + md.valve, b.start + 0.1, 0.5)
        vx = md.vx
        valve = md.valve
        v_neck_y = cy + 1.4 * SC
        lab_v = K.callout(st, "gas-lift valve in its pocket", 0.2, cy + 0.6, vx + 0.25, cy + 0.6, size=0.21)
        K.show(st, lab_v, s[0] + 1.0, s[2], 0.4)
        # sentence 1: a straight tool runs down the bore and misses
        tool0 = st.rect(cx, 3.6, 0.4, 1.2, P.STEEL_DK, 0.5, role="steel")
        K.show(st, tool0, s[1] - 0.1, None, 0.3)
        st.move(tool0, s[1] + 0.2, s[1] + 2.4, dy=-5.4)
        st.fade_out(tool0, s[1] + 2.2, 0.4)
        ms = K.tag(st, 0.2, 2.3, "a straight tool misses the valve", color=P.BAD, fg=P.BG, size=0.21, z=0.9)
        K.show(st, ms, s[1] + 0.8, s[2], 0.4)
        # the kick-over tool: body in the bore, arm hinged on its right side
        P_ = (cx + 0.25, cy + 1.18)               # pivot when aligned with the valve neck
        U = 1.3
        body = st.rect(cx, P_[1] + 0.15 + U, 0.5, 2.3, P.PRIMARY_B, 0.55, role="flat")
        key = st.rect(cx - 0.3, P_[1] - 0.6 + U, 0.14, 0.2, P.WARN, 0.57, role="solid")
        arm = st.rect(P_[0], P_[1] + U, 1.48, 0.16, P.WARN, 0.6, anchor="l", rot=90, role="solid")
        pivot = st.circle(P_[0], P_[1] + U, 0.1, P.STEEL, 0.62, role="disc")
        ko = [body, key, arm, pivot]
        wire = st.rect(cx, 4.4, 0.035, 4.4 - (P_[1] + U + 1.3), P.WIRE, 0.6, anchor="t", role="steel")
        hw = [4.4 - (P_[1] + U + 1.3)]
        K.show(st, ko + [wire], s[2] - 0.1, None, 0.5)
        kt = K.callout(st, "kick-over tool", 0.2, 3.0, cx + 0.3, P_[1] + U + 0.9, size=0.21)
        K.show(st, kt, s[2], s[4], 0.4)

        def mv(objs, t0, t1, dy, dx=0.0):
            st.move(objs, t0, t1, dx=dx, dy=dy)
        def mv_tool(t0, t1, dy):
            st.move(ko, t0, t1, dy=dy)
            st.scale_to(wire, t0, t1, sy=hw[0] - dy)
            hw[0] -= dy
        # sentence 3: runs in with its arm folded
        mv_tool(s[3] + 0.2, s[3] + 3.0, -U)
        # sentence 4: orienting key turns the tool to face the pocket (plan view)
        px, py = 1.7, -1.6
        plan = K.card(st, px + 0.8, py, 3.5, 2.8, P.PANEL, 0.2)
        circ = st.ring(px, py, 0.8, 0.12, P.STEEL, 0.4)
        bump = st.ring(px + 0.95, py, 0.4, 0.1, P.STEEL, 0.4)
        tool_pl = st.rect(px, py, 0.7, 0.2, P.WARN, 0.55, anchor="l", rot=215, role="solid")
        hub = st.circle(px, py, 0.14, P.PRIMARY_B, 0.6, role="disc")
        ptxt = st.text("plan view", px + 0.8, py + 1.15, 0.18, P.MUTED, 0.5)
        pk = st.text("pocket", px + 1.2, py - 0.62, 0.18, P.GAS, 0.5)
        pl = K.note(st, "an orienting key turns\nthe tool to face the pocket", px + 0.8, py - 1.5 + 0.0, 0.19, P.TEXT, align="c")
        K.show(st, plan + [circ, bump, tool_pl, hub, ptxt, pk] + pl, s[4] - 0.2, s[5] + 0.5, 0.4)
        st.rotate(tool_pl, s[4] + 0.6, s[4] + 2.0, 360)
        # sentence 5: pull up, slack off, the arm kicks over to meet the valve
        t5 = s[5]
        mv_tool(t5 + 0.1, t5 + 0.7, +0.35)
        mv_tool(t5 + 0.8, t5 + 1.4, -0.35)
        st.rotate(arm, t5 + 1.2, t5 + 2.2, 35)
        # sentence 6: jar down: the tool latches the valve (a latch appears on the neck)
        t6 = s[6]
        mv_tool(t6 + 0.2, t6 + 0.35, -0.1)
        mv_tool(t6 + 0.35, t6 + 0.55, +0.1)
        latch = st.circle(vx, v_neck_y, 0.14, P.WARN, 0.9, role="disc")
        K.show(st, [latch], t6 + 0.4, None, 0.2)
        lk = K.tag(st, 0.2, v_neck_y + 0.9, "latched", color=P.WARN, fg=P.BG, size=0.21, z=0.9)
        K.show(st, lk, t6 + 0.5, s[7], 0.4)
        # sentence 7: pull up: the old valve is out through the top of the pocket and swings into the bore
        t7 = s[7]
        v_all = valve + [latch]
        mv(v_all, t7 + 0.2, t7 + 1.3, 1.2)
        st.rotate(arm, t7 + 1.0, t7 + 1.8, 90)
        mv(v_all, t7 + 1.3, t7 + 1.9, 0.5, dx=-(vx - cx - 0.62))
        mv_tool(t7 + 1.9, t7 + 4.2, +U + 1.0)
        mv(v_all, t7 + 1.9, t7 + 4.2, U + 1.0)
        ov = K.tag(st, 0.2, 2.6, "old valve out", color=P.SAFE, fg=P.BG, size=0.21, z=0.9)
        K.show(st, ov, t7 + 1.3, s[8], 0.4)
        # sentence 8: the same tool with a new valve puts it back
        t8 = s[8]
        nv = I.gl_valve(st, cx + 0.62, cy + U + 2.7, SC, 0.52, color=P.PANEL2)
        K.show(st, nv, t8 - 0.2, None, 0.4)
        # tool + new valve descend together, the arm kicks over, the valve slides into the pocket, the tool leaves
        mv_tool(t8 + 0.2, t8 + 2.4, -(U + 1.0))
        mv(nv, t8 + 0.2, t8 + 2.4, -(U + 1.0))
        st.rotate(arm, t8 + 2.0, t8 + 2.6, 35)
        mv(nv, t8 + 2.6, t8 + 3.2, -0.5, dx=(vx - cx - 0.62))
        mv(nv, t8 + 3.2, t8 + 4.2, -1.2)
        st.rotate(arm, t8 + 4.3, t8 + 4.8, 90)
        # gas flows through the new valve
        st.flow(md.gas_path, t8 + 4.6, b.end - 0.3, P.GAS, n=8, speed=0.9, r=0.045)
        K.steps_list(st, 3.8, -0.1, ["run in, arm folded", "a key turns the tool to the pocket", "pull up, slack off: arm kicks over", "jar down: latch the valve", "pull up: old valve out",
                                     "new valve in, jar down: seated"], [s[3], s[4], s[5], s[6], s[7], s[8]], size=0.2, dy=0.5)
        # sentence 9: three pockets, one trip each
        t9 = s[9]
        for i in range(3):
            g = K.tag(st, 0.2, 2.3 - i * 0.62, f"pocket {i + 1}: one trip", color=P.SAFE, fg=P.BG, size=0.2, z=0.9, align="l")
            K.show(st, g, t9 + 0.6 * i, None, 0.35)


# ====================================================================================================== 4.07
def _incl_diagram(st, x, y, i_deg, mu, L=1.3, z=0.5):
    """Mini inclined pipe with a tool: green = along-hole weight component, red = friction. Returns (objs, ok)."""
    i = math.radians(i_deg)
    d = (math.sin(i), -math.cos(i))
    phi = math.degrees(math.atan2(d[1], d[0]))
    pipe = st.rect(x, y, L * 1.8, 0.5, P.STEEL, z, rot=phi, role="steel")
    bore = st.rect(x, y, L * 1.8, 0.34, P.BG, z + 0.01, rot=phi)
    tool = st.rect(x, y, 0.5, 0.2, P.WARN, z + 0.02, rot=phi, role="solid")
    a, f = math.cos(i), mu * math.sin(i)
    k = 1.0
    ok = a > f
    arrows = []
    if a * k > 0.05:
        arrows += st.arrow(x, y, x + d[0] * a * k, y + d[1] * a * k, P.SAFE, 0.06, 0.2, z + 0.05)
    if f * k > 0.05:
        arrows += st.arrow(x, y, x - d[0] * f * k, y - d[1] * f * k, P.BAD, 0.06, 0.2, z + 0.05)
    lab = st.text(f"{i_deg:g}°", x, y - 1.35, 0.26, P.TEXT, z + 0.1, kind="bold")
    return [pipe, bore, tool] + arrows + [lab], ok


def b407(st, tl):
    b = tl["4.07"]
    s = b.sent
    with st.span(b.start, b.end):
        # ---------- part A: five small jobs
        xs = [-5.9, -3.0, -0.1, 2.8, 5.7]
        titles = ["shifting tool", "bailer", "gauge cutter", "tag run", "memory gauge"]
        sub = ["opens or closes a sleeve", "scoops sand and debris", "proves the tubing is open", "measures how deep the well is", "records for days"]
        times = [b.word(1, "A shifting tool"), b.word(2, "A bailer"), b.word(3, "A gauge cutter"), b.word(3, "a tag run"), b.word(4, "A memory gauge")]
        t_end = b.word(5, "But slickline") - 0.4
        for i in range(5):
            x = xs[i]
            card = K.card(st, x, 0.7, 2.75, 4.6, P.PANEL, 0.2)
            t = st.text(titles[i], x, 2.75, 0.24, P.TEXT, 0.5, kind="bold")
            sb = K.note(st, sub[i], x, -1.35, 0.17, P.MUTED, align="c", wrap=22)
            gp = card + [t] + sb
            tubing = [st.rect(x - 0.55, 0.5, 0.12, 3.0, P.STEEL, 0.3, role="steel"), st.rect(x + 0.55, 0.5, 0.12, 3.0, P.STEEL, 0.3, role="steel")]
            gp += tubing
            if i == 0:   # sleeve + shifting tool
                inner = st.rect(x, 1.3, 1.0, 0.7, P.PRIMARY_B, 0.35, alpha=0.8, role="flat")
                ports = [st.rect(x - 0.55, 0.65, 0.12, 0.35, P.BG, 0.31), st.rect(x + 0.55, 0.65, 0.12, 0.35, P.BG, 0.31)]
                tool = st.rect(x, 2.0, 0.34, 0.9, P.WARN, 0.5, role="solid")
                gp += [inner, tool] + ports
                st.move([tool, inner], times[0] + 0.8, times[0] + 2.0, dy=-0.7)
            elif i == 1:  # bailer in sand
                sand = st.rect(x, -0.55, 1.0, 0.6, P.SAND, 0.32)
                bail = st.rect(x, 1.9, 0.4, 1.1, P.STEEL, 0.5, role="steel")
                grains = [st.circle(x - 0.25 + 0.12 * k, -0.4 + 0.08 * (k % 2), 0.045, P.SAND, 0.55, role="disc") for k in range(5)]
                gp += [sand, bail] + grains
                st.move([bail], times[1] + 0.6, times[1] + 1.6, dy=-1.9)
                st.move(grains, times[1] + 1.8, times[1] + 2.6, dy=0.9)
                st.move([bail] + grains, times[1] + 2.7, times[1] + 3.8, dy=1.9)
            elif i == 2:  # gauge cutter passing
                scale = [st.rect(x - 0.45, 0.6, 0.18, 0.5, P.SCALE, 0.33, role="flat"), st.rect(x + 0.45, 0.6, 0.18, 0.5, P.SCALE, 0.33, role="flat")]
                gc = st.rect(x, 2.2, 0.62, 0.55, P.WARN, 0.5, role="solid")
                gp += scale + [gc]
                st.move([gc], times[2] + 0.6, times[2] + 2.4, dy=-2.0)
            elif i == 3:  # tag: tool lands on the bottom, depth counter
                bot = st.rect(x, -0.55, 1.2, 0.2, P.STEEL_DK, 0.35)
                tg = st.rect(x, 2.0, 0.4, 0.7, P.WARN, 0.5, role="solid")
                gp += [bot, tg]
                st.move([tg], times[3] + 0.6, times[3] + 2.2, dy=-2.15)
                st.counter(x, 0.2, times[3] + 0.6, times[3] + 2.2, 0, 4180, "{:,.0f} m", 0.22, P.PORE, 0.6, hold=t_end)
            else:         # memory gauge: body with a clock
                gg = st.rect(x, 1.7, 0.5, 1.0, P.STEEL_DK, 0.5, role="steel")
                ck = [st.circle(x, 0.2, 0.3, P.PANEL2, 0.55, role="disc"), st.ring(x, 0.2, 0.3, 0.04, P.MUTED, 0.6)]
                hand = st.rect(x, 0.2, 0.2, 0.04, P.WARN, 0.62, anchor="l", rot=90, role="shaft")
                gp += [gg] + ck + [hand]
                st.rotate(hand, times[4] + 0.5, times[4] + 3.5, 90 - 720)
            K.show(st, gp, times[i] - 0.2, t_end, 0.4)

        # ---------- part B: the limits
        t5 = b.word(5, "But slickline")
        lim = K.tag(st, -5.6, 2.9, "slickline has limits", color=P.BAD, fg=P.BG, size=0.28, z=0.9)
        K.show(st, lim, t5, None, 0.5)
        l1 = K.tag(st, -5.4, 2.0, "cannot push: the tool must fall", color=P.PANEL2, size=0.23, z=0.8, align="l")
        l2 = K.tag(st, -5.4, 1.35, "cannot pump", color=P.PANEL2, size=0.23, z=0.8, align="l")
        K.show(st, l1, s[6], None, 0.4)
        K.show(st, l2, s[7], None, 0.4)
        # gravity: five inclinations with the force components
        t8 = s[8]
        mu = 0.3
        angles = [0, 30, 60, 73, 85]
        xs2 = [-5.6, -2.8, 0.0, 2.8, 5.6]
        ok_flags = []
        for xg, a in zip(xs2, angles):
            objs, ok = _incl_diagram(st, xg, -0.6, a, mu)
            K.show(st, objs, t8 + 0.4 + angles.index(a) * 0.35, None, 0.4)
            ok_flags.append(ok)
        leg = [K.tag(st, -3.6, -2.75, "weight along the hole  cos i", color=P.SAFE, fg=P.BG, size=0.2, z=0.8, align="l"),
               K.tag(st, 0.4, -2.75, "friction  μ sin i", color=P.BAD, fg=P.BG, size=0.2, z=0.8, align="l")]
        K.show(st, leg[0], s[9], None, 0.4)
        K.show(st, leg[1], s[9] + 0.6, None, 0.4)
        # the result
        t10 = s[10]
        res = K.tag(st, 2.8, 0.75, "equal at 73°: the tool stops", color=P.WARN, fg=P.BG, size=0.24, z=0.9)
        K.show(st, res, b.word(10, "seventy-three"), None, 0.4)
        prac = K.note(st, "μ = 0.3.   Real wire drag brings the limit lower.", 0.0, -3.35, 0.22, P.TEXT, align="c")
        K.show(st, prac, b.word(10, "in practice"), None, 0.5)
        stk = K.xmark(st, 5.6, -0.6, 0.35, b.word(10, "seventy-three") + 0.3)


def build(st, tl):
    b405(st, tl)
    b406(st, tl)
    b407(st, tl)
