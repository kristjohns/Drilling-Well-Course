"""Ch 3: The airlock: working in a live well.

3.01 the lubricator airlock, step by step: shut, load, pressure up, equalise, open, run in, and back out
3.02 the tree: two master valves, the wing valve, the swab valve (our door); the lubricator goes on top
3.03 the moving seal on one big cutaway: stuffing box on solid wire, grease head on stranded cable, tool catcher, wireline BOP
3.04 the invisible force: pressure x area on a wire (118 N) and on a 2 in coiled tube (40.5 kN = 4.1 t)
3.05 two tested barrier envelopes (primary blue, secondary red), the pressure control equipment is part of them
"""
from __future__ import annotations
import math

from scenes.common import palette as P, model as M, furniture as F
from scenes.common import kit as K

TITLE = "The airlock: working in a live well"


# ====================================================================================================== 3.01
def b301(st, tl):
    b = tl["3.01"]
    s = b.sent
    with st.span(b.start, b.end):
        cx, SC = -5.1, 1.22
        y0 = -2.3
        tub = [st.rect(cx - 0.15, -2.9, 0.08, 1.2, P.STEEL, 0.4, role="steel"), st.rect(cx + 0.15, -2.9, 0.08, 1.2, P.STEEL, 0.4, role="steel"),
               st.rect(cx, -2.9, 0.22, 1.2, P.OIL, 0.3, alpha=0.8)]
        tree = K.dry_tree(st, cx, y0, SC)
        pce = K.pce_stack(st, cx, tree.top, SC, tube_h=1.5)
        st.fade_in(tub + tree.parts + tree.gates, b.start + 0.1, 0.5)
        st.flow([(cx, -3.5), (cx, y0 + 0.1)], b.start, b.end - 0.3, P.OIL, n=4, speed=0.6, r=0.045)
        oil_a = st.rect(cx, (y0 + tree.y_swab) / 2, 0.19 * SC, tree.y_swab - y0, P.OIL, 0.3, alpha=0.8)
        oil_b = st.rect(cx, (tree.y_swab + tree.top) / 2, 0.19 * SC, tree.top - tree.y_swab, P.OIL, 0.3, alpha=0.8)
        st.fade_in([oil_a, oil_b], b.start + 0.1, 0.5)
        st.fade_out(oil_b, s[2], 0.4)
        # sentence 1: open the top and it flows
        st.flow([(cx, tree.top - 0.2), (cx, tree.top + 1.6)], s[1], s[2] + 0.2, P.OIL, n=9, speed=1.3, r=0.06, jitter=0.15)
        jt = K.tag(st, cx + 1.9, tree.top + 1.0, "open top: it flows", color=P.BAD, fg=P.BG, size=0.22, z=0.9)
        K.show(st, jt, s[1], s[2], 0.35)
        # sentence 2: swab valve closes, the lubricator lands on top
        K.valve_to(st, tree.swab, s[2], s[2] + 0.5, False)
        K.show(st, pce.parts, s[2] + 0.3, None, 0.6)
        # toolstring on a wire, in the lubricator
        y_ts_top = pce.y_t1 - 0.12
        ts = K.toolstring_simple(st, cx, y_ts_top, SC)
        wire = st.rect(cx, pce.top, 0.03, pce.top - y_ts_top, P.WIRE, 0.65, anchor="t", role="steel")
        K.show(st, ts.parts + [wire], s[3] - 0.2, None, 0.5)
        lt = K.callout(st, "lubricator", cx + 1.1, (pce.y_t0 + pce.y_t1) / 2 + 0.55, cx + 0.2, (pce.y_t0 + pce.y_t1) / 2 + 0.55, size=0.21)
        tt = K.callout(st, "toolstring", cx + 1.1, (pce.y_t0 + pce.y_t1) / 2 - 0.35, cx + 0.12, (pce.y_t0 + pce.y_t1) / 2 - 0.35, size=0.21)
        K.show(st, lt, b.word(3, "lubricator"), s[4], 0.4)
        K.show(st, tt, b.word(3, "toolstring"), s[4], 0.4)
        # sentence 5: pressure up the lubricator; the pressurised volume turns green, the dial climbs
        lub_fill = st.rect(cx, (pce.y_bop - 0.27 * SC + pce.y_t1) / 2, 0.21 * SC, pce.y_t1 - (pce.y_bop - 0.27 * SC), P.OIL, 0.25, alpha=0.8)
        K.show(st, lub_fill, s[5] + 0.3, None, 0.9)
        gx = -2.55
        g_well = K.dial(st, gx, 0.2, 0.5, s[4], s[4] + 0.8, 60, 60, color=P.OIL)
        gw_t = st.text("200 bar", gx, -0.5, 0.22, P.OIL, 0.8, kind="mono")
        gw_l = st.text("well", gx, 0.95, 0.2, P.MUTED, 0.8)
        g_lub = K.dial(st, gx, 2.1, 0.5, s[5] + 0.2, s[5] + 2.4, 210, 60, color=P.PORE)
        needle = g_lub[2]
        gl_l = st.text("lubricator", gx, 2.85, 0.2, P.MUTED, 0.8)
        st.counter(gx, 1.4, s[5] + 0.2, s[5] + 2.4, 0, 200, "{:.0f} bar", 0.22, P.PORE, 0.8, hold=b.word(7, "bled") - 0.1)
        K.show(st, g_well + [gw_t, gw_l], s[4], None, 0.5)
        K.show(st, g_lub + [gl_l], s[4], None, 0.5)
        eq = K.tag(st, gx, 1.5, "equal", color=P.SAFE, fg=P.BG, size=0.2, z=0.9)
        eq_t = s[5] + 2.4
        K.show(st, eq, eq_t, s[6] + 0.8, 0.3)
        # sentence 6: swab valve opens, the toolstring runs down the tubing
        K.valve_to(st, tree.swab, s[6] + 0.2, s[6] + 0.7, True)
        D = (y_ts_top - ts.h) - (-3.15)
        st.move(ts.parts, s[6] + 0.8, s[6] + 3.8, dy=-D)
        st.scale_to(wire, s[6] + 0.8, s[6] + 3.8, sy=pce.top - y_ts_top + D)
        # sentence 7: back out, valve closed, bleed down, open
        t7, t7b, t7c, t7d = (b.word(7, "tools up"), b.word(7, "valve closed"), b.word(7, "lubricator bled"), b.word(7, "opened"))
        st.move(ts.parts, t7 - 0.3, t7 + 2.2, dy=D)
        st.scale_to(wire, t7 - 0.3, t7 + 2.2, sy=pce.top - y_ts_top)
        K.valve_to(st, tree.swab, t7b + 0.3, t7b + 0.9, False)
        st.rotate(needle, t7c, t7c + 1.4, 210)
        st.fade_out(lub_fill, t7c, 1.2)
        # step list
        steps = [("valve shut, tools loaded", s[4]), ("pressure up to well pressure", s[5]), ("equal: open the valve, run in", s[6]),
                 ("tools up, valve closed", t7), ("bleed the lubricator down", t7c - 0.2), ("open it: tools out", t7d - 0.2)]
        for i, (txt, t) in enumerate(steps):
            y = 3.0 - i * 0.66
            K.orb_num(st, -0.8, y, i + 1, t, color=P.PORE, r=0.19, z=0.9)
            tx = st.text(txt, -0.5, y, 0.24, P.TEXT, 0.9, align="l")
            st.fade_in(tx, t + 0.1, 0.35)
        # pressure against time: the lubricator is brought up to well pressure, then bled down again
        from scenes.common.chart import Chart
        ch = Chart(st, -0.5, -2.45, 3.4, 2.0, (0, 10), (0, 240))
        fr = ch.frame(xticks=[], yticks=[0, 200], xlabel="time", ylabel="bar", fx="{:.0f}", fy="{:,.0f}", tick_size=0.17)
        pts = [(0, 0), (2.0, 0), (4.0, 200), (6.5, 200), (8.5, 0), (10, 0)]
        c_well = st.line([ch.pt(0, 200), ch.pt(10, 200)], P.OIL, 0.05, 0.4)
        c_lub = st.line([ch.pt(*p_) for p_ in pts], P.PORE, 0.06, 0.45)
        t_a, t_b = s[5] - 0.6, t7c + 1.6
        K.show(st, fr + [c_well], s[4], None, 0.5)
        K.show(st, [c_lub], s[4], None, 0.1)
        st.draw_on(c_lub, t_a, t_b, "LINEAR")
        cl1 = st.text("well", ch.X(0.3), ch.Y(200) + 0.2, 0.17, P.OIL, 0.5, align="l")
        cl2 = st.text("lubricator", ch.X(0.3), ch.Y(30), 0.17, P.PORE, 0.5, align="l")
        K.show(st, [cl1, cl2], s[4], None, 0.5)
        nm = K.tag(st, 1.0, -3.2, "the well never meets the atmosphere", color=P.SAFE, fg=P.BG, size=0.24, z=0.9)
        K.show(st, nm, s[8], None, 0.5)


# ====================================================================================================== 3.02
def b302(st, tl):
    b = tl["3.02"]
    s = b.sent
    with st.span(b.start, b.end):
        cx, SC = -3.7, 1.45
        y0 = -3.2
        tub = [st.rect(cx - 0.2, y0 - 0.1, 0.1, 0.3, P.STEEL, 0.4, role="steel"), st.rect(cx + 0.2, y0 - 0.1, 0.1, 0.3, P.STEEL, 0.4, role="steel")]
        tree = K.dry_tree(st, cx, y0, SC)
        oil = st.rect(cx, (y0 + tree.y_swab) / 2, 0.19 * SC, tree.y_swab - y0, P.OIL, 0.3, alpha=0.8)
        st.fade_in(tub + tree.parts + tree.gates + [oil], b.start + 0.1, 0.5)

        def lab(text, y, tx, t, color=P.PANEL2, fg=P.TEXT, x=-1.3):
            g = K.callout(st, text, x, y, tx, y, color=color, fg=fg, size=0.22)
            K.show(st, g, t, None, 0.4)
        lab("lower master valve", tree.y_lmv, cx + 0.5 * SC, b.word(1, "Two master valves"))
        lab("upper master valve", tree.y_umv, cx + 0.5 * SC, b.word(1, "one above the other"))
        lab("wing valve → flowline", tree.y_wing, cx + 0.88 * SC + 0.3, b.word(2, "wing valve"), x=0.3)
        lab("swab valve", tree.y_swab, cx + 0.5 * SC, b.word(3, "swab valve"), color=P.WARN, fg=P.BG)
        door = K.tag(st, 1.5, tree.y_swab, "our door", color=P.SAFE, fg=P.BG, size=0.24, z=0.9)
        K.show(st, door, s[4], None, 0.4)
        for key, t in (("lmv", b.word(1, "Two master valves")), ("umv", b.word(1, "one above the other")), ("wing", b.word(2, "wing valve")), ("swab", b.word(3, "swab valve"))):
            v = tree[key]
            st.ripple(v.body[0].location[0], v.body[0].location[1], t, t + 1.2, P.WARN, period=0.9, r0=0.15, r1=0.6)
        fl = st.line([(cx + 0.88 * SC + 0.4, tree.y_wing), (0.0, tree.y_wing)], P.STEEL, 0.1, 0.3)
        K.show(st, [fl], b.word(2, "wing valve"), None, 0.4)
        st.flow([(cx + 0.88 * SC + 0.4, tree.y_wing), (0.0, tree.y_wing)], b.word(2, "wing valve") + 0.4, b.end - 0.3, P.OIL, n=5, speed=0.8, r=0.045)
        # the lubricator is bolted on top; the valves below form the barrier between tools and well
        pce = K.pce_stack(st, cx, tree.top, SC, tube_h=0.85)
        K.show(st, pce.parts, s[5] - 0.2, None, 0.6)
        x_b = cx - 0.95 * SC
        brk = st.line([(x_b, tree.y_lmv - 0.35), (x_b - 0.14, tree.y_lmv - 0.35), (x_b - 0.14, tree.y_swab + 0.35), (x_b, tree.y_swab + 0.35)], P.SAFE, 0.05, 0.8)
        bl = K.note(st, "swab and master\nvalves: the barrier\nbetween tools\nand well", x_b - 0.3, (tree.y_lmv + tree.y_swab) / 2, 0.21, P.SAFE, align="r")
        K.show(st, [brk] + bl, s[5] + 0.3, None, 0.5)
        nor = K.tag(st, -1.3, -3.45, "NORWAY: at least two main valves, one of them automatic", color=P.NO_BADGE, fg=P.TEXT, size=0.21, z=0.9, align="l")
        K.show(st, nor, s[6], None, 0.5)
        act = [st.rect(cx + 0.78 * SC, tree.y_lmv - 0.0, 0.26 * SC, 0.36 * SC, P.PRIMARY_B, 0.45, role="flat")]
        K.show(st, act, b.word(6, "one of them automatic"), None, 0.5)
        al = K.callout(st, "automatic (actuated)", 0.3, tree.y_lmv - 0.65, cx + 0.9 * SC, tree.y_lmv - 0.1, color=P.PRIMARY_B, fg=P.BG, size=0.2)
        K.show(st, al, b.word(6, "one of them automatic"), None, 0.5)


# ====================================================================================================== 3.03
def b303(st, tl):
    b = tl["3.03"]
    s = b.sent
    with st.span(b.start, b.end):
        cx = -4.2
        W, top, bot = 3.0, 2.85, -3.2          # housing: x = cx +- W/2, y from bot to top
        walls = [st.rect(cx - W / 2 - 0.07, (top + bot) / 2, 0.14, top - bot, P.STEEL, 0.3, role="steel"),
                 st.rect(cx + W / 2 + 0.07, (top + bot) / 2, 0.14, top - bot, P.STEEL, 0.3, role="steel"),
                 st.rect(cx, (top + bot) / 2, W, top - bot, P.BG, 0.2)]
        y_seal0, y_seal1 = 1.2, 2.5
        well = st.rect(cx, (y_seal0 + bot) / 2, W, y_seal0 - bot, P.OIL, 0.22, alpha=0.28)
        st.fade_in(walls + [well], b.start + 0.2, 0.5)
        wp = K.note(st, "well pressure 200 bar", cx - W / 2 + 0.2, bot + 0.3, 0.21, P.OIL, align="l")
        st.fade_in(wp, b.start + 0.5, 0.5)
        ups = [st.arrow(cx + dx, y_seal0 - 0.9, cx + dx, y_seal0 - 0.1, P.BAD, 0.05, 0.2, 0.5) for dx in (-1.0, 1.0)]
        st.fade_in(sum([list(a) for a in ups], []), b.start + 0.6, 0.5)

        # ------------ solid wire + stuffing box (sentence 2)
        wire = st.rect(cx, 0.0, 0.07, 6.6, P.WIRE, 0.6, role="steel")
        pack = [st.rect(cx - 0.75, 1.85, 1.2, 1.3, P.RUBBER, 0.5, role="solid"), st.rect(cx + 0.75, 1.85, 1.2, 1.3, P.RUBBER, 0.5, role="solid"),
                st.rect(cx - 0.75, 1.85, 1.2, 1.3, P.RUBBER_HI, 0.49, alpha=0.45, role="flat"), st.rect(cx + 0.75, 1.85, 1.2, 1.3, P.RUBBER_HI, 0.49, alpha=0.45, role="flat")]
        piston = [st.rect(cx - 1.42, 1.85, 0.16, 1.0, P.STEEL, 0.55, role="steel"), st.rect(cx + 1.42, 1.85, 0.16, 1.0, P.STEEL, 0.55, role="steel")]
        parr = [st.arrow(cx - 1.95, 1.85, cx - 1.6, 1.85, P.PORE, 0.06, 0.22, 0.6), st.arrow(cx + 1.95, 1.85, cx + 1.6, 1.85, P.PORE, 0.06, 0.22, 0.6)]
        t_sb = s[2]
        t_stuff = K.tag(st, cx, 3.45, "stuffing box on solid wire", color=P.PRIMARY_B, fg=P.BG, size=0.22, z=0.9)
        sb_group = [wire] + pack + piston + sum([list(a) for a in parr], [])
        K.show(st, sb_group, t_sb - 0.2, s[3] - 0.2, 0.5)
        K.show(st, t_stuff, t_sb - 0.2, s[3] - 0.2, 0.5)
        st.move(wire, t_sb + 1.0, t_sb + 2.6, dy=0.6)
        st.move(wire, t_sb + 2.6, s[3] - 0.3, dy=-0.6)
        ok1 = K.check(st, cx + 1.85, 0.95, t_sb + 2.2)
        K.show(st, ok1, t_sb + 2.2, s[3] - 0.2, 0.2)
        note1 = K.note(st, "tight enough to seal,\nloose enough to let the wire slide", 0.0, 1.9, 0.23, P.MUTED, align="l")
        K.show(st, note1, b.word(2, "tight enough"), s[3] - 0.2, 0.5)

        # ------------ stranded cable (sentence 3): gaps, the packing leaks
        cable = st.rect(cx, 0.0, 0.3, 6.6, "#8d9bb0", 0.6, role="steel")
        grooves = [st.line([(cx - 0.15, 0.2 + 0.4 * k), (cx + 0.15, 0.38 + 0.4 * k)], P.BG, 0.035, 0.62, role="hair") for k in range(-5, 8)]
        pack2 = [st.rect(cx - 0.8, 1.85, 1.1, 1.3, P.RUBBER, 0.5, role="solid"), st.rect(cx + 0.8, 1.85, 1.1, 1.3, P.RUBBER, 0.5, role="solid")]
        leaks = [st.arrow(cx + dx, 1.3, cx + dx, 2.5, P.BAD, 0.04, 0.16, 0.7) for dx in (-0.2, 0.2)]
        t_str = K.tag(st, cx, 3.45, "stranded cable: gaps", color=P.PANEL2, size=0.22, z=0.9)
        K.show(st, [cable] + grooves + pack2 + [o for a in leaks for o in a] + t_str, s[3] - 0.1, s[4] - 0.2, 0.4)
        cxs, cys = 1.4, -0.4
        xs_w = [st.circle(cxs - 1.0, cys, 0.36, P.WIRE, 0.6, role="disc")]
        strands = [st.circle(cxs + 1.3 + 0.37 * math.cos(math.radians(60 * k)), cys + 0.37 * math.sin(math.radians(60 * k)), 0.19, "#8d9bb0", 0.6, role="disc") for k in range(6)] + \
                  [st.circle(cxs + 1.3, cys, 0.19, "#8d9bb0", 0.6, role="disc")]
        xl = [st.text("solid: no gaps", cxs - 1.0, cys - 0.75, 0.2, P.MUTED, 0.6), st.text("stranded: gaps between strands", cxs + 1.3, cys - 0.85, 0.2, P.BAD, 0.6)]
        K.show(st, xs_w + [xl[0]], t_sb + 0.2, s[4] - 0.2, 0.5)
        K.show(st, strands + [xl[1]], s[3] + 0.3, s[4] - 0.2, 0.5)

        # ------------ grease injection head (sentences 4 and 5)
        tubes = [st.rect(cx - 0.3, 1.85, 0.1, 1.5, P.STEEL, 0.55, role="steel"), st.rect(cx + 0.3, 1.85, 0.1, 1.5, P.STEEL, 0.55, role="steel"),
                 st.rect(cx - 0.55, 1.85, 0.4, 1.5, P.STEEL_DK, 0.5, role="solid"), st.rect(cx + 0.55, 1.85, 0.4, 1.5, P.STEEL_DK, 0.5, role="solid")]
        grease = [st.rect(cx - 0.22, 1.85, 0.07, 1.4, P.GREASE, 0.52, alpha=0.95), st.rect(cx + 0.22, 1.85, 0.07, 1.4, P.GREASE, 0.52, alpha=0.95)]
        inlet = [st.rect(cx + 1.3, 1.3, 1.8, 0.14, P.GREASE, 0.5, alpha=0.95, role="flat"), st.rect(cx + 0.45, 1.3, 0.5, 0.14, P.GREASE, 0.5, alpha=0.95, role="flat")]
        t_gh = K.tag(st, cx, 3.45, "grease injection head", color=P.GREASE, fg=P.BG, size=0.22, z=0.9)
        K.show(st, [cable] + grooves + tubes + grease + inlet + t_gh, s[4] - 0.1, s[6] - 0.5, 0.5)
        st.flow([(cx + 2.3, 1.3), (cx + 0.3, 1.3), (cx + 0.22, 2.4)], s[5], s[6] - 0.8, P.GREASE, n=8, speed=0.9, r=0.06)
        st.counter(cx + 2.1, 0.8, s[5], s[5] + 1.0, 0, 220, "grease {:.0f} bar", 0.22, P.GREASE, 0.8, hold=s[6] - 0.5)
        st.counter(cx + 2.1, -0.1, s[5], s[5] + 1.0, 0, 200, "well {:.0f} bar", 0.22, P.OIL, 0.8, hold=s[6] - 0.5)
        ok2 = K.check(st, cx + 1.85, 2.4, s[5] + 1.2)
        K.show(st, ok2, s[5] + 1.2, s[6] - 0.5, 0.2)
        note2 = K.note(st, "the grease itself is the seal", 0.2, 2.2, 0.24, P.GREASE, align="l")
        K.show(st, note2, b.word(5, "the grease itself"), s[6] - 0.5, 0.5)

        # ------------ sentence 6: wireline BOP lower in the stack; sentence 7: tool catcher and a parted line
        y_bop = -1.55
        bop_body = [st.rect(cx - W / 2 - 0.5, y_bop, 0.9, 1.0, P.STEEL_DK, 0.35), st.rect(cx + W / 2 + 0.5, y_bop, 0.9, 1.0, P.STEEL_DK, 0.35)]
        ramsL = st.rect(cx - 1.05, y_bop, 1.0, 0.7, P.BAD, 0.55, role="solid")
        ramsR = st.rect(cx + 1.05, y_bop, 1.0, 0.7, P.BAD, 0.55, role="solid")
        cableC = st.rect(cx, 0.0, 0.3, 6.6, "#8d9bb0", 0.58, role="steel")
        t_bop = K.tag(st, cx, 3.45, "wireline BOP and tool catcher", color=P.BAD, fg=P.BG, size=0.22, z=0.9)
        K.show(st, bop_body + [ramsL, ramsR, cableC] + t_bop, s[6] - 0.3, None, 0.6)
        t_em = b.word(6, "emergency")
        st.move(ramsL, t_em - 0.3, t_em + 0.6, to=(cx - 0.3, y_bop))
        st.move(ramsR, t_em - 0.3, t_em + 0.6, to=(cx + 0.3, y_bop))
        n_bop = K.note(st, "rams close on the line\nand seal around it", 0.2, y_bop + 0.1, 0.23, P.BAD, align="l")
        K.show(st, n_bop, t_em, s[7] - 0.2, 0.5)
        y_cat = -0.2
        fingers = [st.poly([(cx - 1.4, y_cat + 0.1), (cx - 0.25, y_cat - 0.25), (cx - 0.25, y_cat - 0.05), (cx - 1.4, y_cat + 0.3)], P.WARN, 0.55, role="flat"),
                   st.poly([(cx + 1.4, y_cat + 0.1), (cx + 0.25, y_cat - 0.25), (cx + 0.25, y_cat - 0.05), (cx + 1.4, y_cat + 0.3)], P.WARN, 0.55, role="flat")]
        ts = K.toolstring_simple(st, cx, y_cat + 1.35, 1.0)
        brk = st.line([(cx - 0.3, 1.0), (cx + 0.05, 0.88), (cx - 0.1, 0.76), (cx + 0.3, 0.64)], P.BAD, 0.06, 0.8)
        K.show(st, fingers + ts.parts, s[7] - 0.2, None, 0.5)
        t_cut = b.word(7, "breaks")
        K.show(st, [brk], t_cut, None, 0.2)
        st.fade_out(cableC, t_cut, 0.2)
        st.move(ts.parts, t_cut + 0.3, t_cut + 0.9, dy=-1.1)
        n_tc = K.note(st, "the toolstring cannot fall\nback into the well", 0.2, y_cat + 0.5, 0.23, P.WARN, align="l")
        K.show(st, n_tc, t_cut + 0.5, None, 0.5)


# ====================================================================================================== 3.04
def b304(st, tl):
    b = tl["3.04"]
    s = b.sent
    with st.span(b.start, b.end):
        F_w = M.wire_force_n()
        F_ct = M.ct_push_force_n()
        cx, cy = -4.6, -0.3
        W = 2.6
        chamber = [st.rect(cx, cy - 0.7, W, 3.0, P.OIL, 0.2, alpha=0.35),
                   st.rect(cx - W / 2 - 0.07, cy - 0.7, 0.14, 3.0, P.STEEL, 0.3, role="steel"), st.rect(cx + W / 2 + 0.07, cy - 0.7, 0.14, 3.0, P.STEEL, 0.3, role="steel"),
                   st.rect(cx, cy - 2.27, W + 0.28, 0.14, P.STEEL, 0.3, role="steel"),
                   st.rect(cx - 0.8, cy + 0.85, 1.0, 0.3, P.STEEL_DK, 0.3), st.rect(cx + 0.8, cy + 0.85, 1.0, 0.3, P.STEEL_DK, 0.3)]
        wire = st.rect(cx, cy + 2.3, 0.07, 2.4, P.WIRE, 0.5, role="steel")
        tool = st.rect(cx, cy - 1.6, 0.5, 0.55, P.STEEL, 0.55, role="steel")
        st.fade_in(chamber + [wire, tool], b.start + 0.1, 0.5)
        pr = K.note(st, "200 bar", cx, cy - 2.0, 0.26, P.OIL, align="c", kind="mono")
        st.fade_in(pr, b.start + 0.2, 0.4)
        push = st.arrow(cx + 0.5, cy + 0.5, cx + 0.5, cy + 1.7, P.BAD, 0.09, 0.3, 0.7)
        pl = K.note(st, "pressure pushes\nthe wire out", cx + 0.7, cy + 1.2, 0.2, P.BAD, align="l")
        K.show(st, push + pl, s[1] + 0.5, None, 0.5)
        card = K.card(st, 1.05, 2.0, 4.6, 1.9, P.PANEL, 0.2)
        f1 = st.text("force = pressure × area", 1.05, 2.65, 0.26, P.TEXT, 0.4, kind="bold")
        f2 = st.text("200 bar  ×  5.9 mm²", 1.05, 2.1, 0.28, P.PORE, 0.4, kind="mono")
        st.counter(1.05, 1.55, s[2] + 0.5, s[2] + 1.6, 0, F_w, "= {:.0f} N", 0.34, P.WARN, 0.5, kind="mono")
        K.show(st, card + [f1, f2], s[2] - 0.1, None, 0.4)
        kg = [st.rect(1.05, 0.15, 1.3, 1.0, P.STEEL_DK, 0.4, role="solid"), st.rect(1.05, 0.78, 0.5, 0.25, P.STEEL_DK, 0.4, role="solid")]
        kt = st.text("12 kg", 1.05, 0.12, 0.36, P.TEXT, 0.5, kind="bold")
        K.show(st, kg + [kt], s[3] - 0.1, None, 0.4)
        st.move([tool, wire], s[4] + 0.5, s[4] + 1.8, dy=1.2)
        st.move([tool, wire], s[4] + 2.2, s[4] + 2.6, dy=-1.2)
        st.scale_to(tool, s[5] + 0.0, s[5] + 0.8, sx=0.5, sy=1.5)
        st.recolor(tool, s[5], s[5] + 0.6, P.WARN)
        lt = K.tag(st, cx, cy - 1.1, "too light: blown out", color=P.BAD, fg=P.BG, size=0.21, z=0.9)
        ht = K.tag(st, cx, cy - 1.1, "heavy: stays put", color=P.SAFE, fg=P.BG, size=0.21, z=0.9)
        K.show(st, lt, s[4], s[5], 0.3)
        K.show(st, ht, s[5] + 0.3, s[6] - 0.3, 0.3)
        # the coiled tube: areas to scale (diameter ratio 18.5)
        wire_r = 0.04
        ct_r = wire_r * 50.8 / 2.74
        cwx, cwy = 0.4, -1.6
        c_wire = st.circle(cwx, cwy, wire_r, P.WIRE, 0.6, role="disc")
        c_ct = st.circle(3.6, -1.35, ct_r, P.STEEL, 0.5, role="steel")
        c_in = st.circle(3.6, -1.35, ct_r * 0.84, P.BG, 0.55, role="hole")
        wl = st.text("wire: 2.7 mm", cwx, cwy - 0.45, 0.21, P.MUTED, 0.6)
        cl = st.text("coiled tube: 2 in (50.8 mm)", 3.6, -0.3, 0.21, P.MUTED, 0.6)
        K.show(st, [c_wire, wl], s[6] - 0.5, None, 0.5)
        K.show(st, [c_ct, c_in, cl], s[6] + 0.2, None, 0.6)
        ratio = K.tag(st, 1.95, -1.35, "area × 340", color=P.WARN, fg=P.BG, size=0.24, z=0.9)
        K.show(st, ratio, s[7], None, 0.5)
        st.counter(3.6, -2.6, s[7] + 1.2, s[7] + 2.4, 0, F_ct / 1000, "{:.1f} kN", 0.4, P.WARN, 0.7, kind="mono")
        st.counter(3.6, -3.1, s[7] + 1.4, s[7] + 2.4, 0, F_ct / M.GRAV / 1000, "= {:.1f} tonnes", 0.32, P.WARN, 0.7, kind="mono")
        remember = K.tag(st, 3.6, 3.15, "remember: 4.1 tonnes", color=P.WARN, fg=P.BG, size=0.3, z=0.9)
        K.show(st, remember, s[8], None, 0.5)
        shapes = K.note(st, "it shapes everything about coiled tubing", 3.6, 2.45, 0.22, P.MUTED, align="c")
        K.show(st, shapes, s[9], None, 0.5)


# ====================================================================================================== 3.05
# 3.05 (the barrier envelopes during a wireline job) lives in scenes/x_ch03_barriers.py
from scenes.x_ch03_barriers import b305  # noqa: E402


def build(st, tl):
    F.header(st, tl)
    b301(st, tl)
    b302(st, tl)
    b303(st, tl)
    b304(st, tl)
    b305(st, tl)
