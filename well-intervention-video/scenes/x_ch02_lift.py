"""Ch 2, beat 2.06 (LIFT): gas lift, the gas-lift valve and unloading; then liquid loading and the velocity string.

Scenes, in narration order:
  A  a tall well: the liquid column outweighs the reservoir (pressure bars); gas is injected down the annulus and enters the
     tubing through the operating valve; the column lightens and the well flows.
  B  close-up of an injection-pressure-operated valve in its pocket: nitrogen dome, bellows, ball and seat, ports between the
     packings, check valve. Annulus pressure rises, the bellows compress, the ball lifts, gas streams through to the tubing.
  C  start-up (unloading): the annulus is full of liquid; gas pushes the level down past valve 1, 2 and 3; each valve passes
     gas, then closes when the next one takes over; the deepest becomes the operating valve.
  D  the check valve blocks reverse flow; valves wear out and are changed by wire.
  E  gas well: droplets fall back, a pool grows (liquid loading); a velocity string speeds the gas and clears it.
"""
from __future__ import annotations
import math

from scenes.common import palette as P
from scenes.common import kit as K
from scenes.common import gaslift as G
from scenes.common import pdraw as D
from scenes.common.look import darken, lighten
from scenes.common.stage import hex_rgb


def b206(st, tl, reason_head):
    b = tl["2.06"]
    s = b.sent
    with st.span(b.start, b.end):
        reason_head(st, 5, b.start + 0.2, s[8] - 0.3)
        t_end_lift = s[8] - 0.3                       # everything gas-lift fades here; the gas-well scene follows
        # ------------------------------------------------------------------ well geometry (left)
        cx = -5.6
        ci, ti = 0.9, 0.31                            # casing / tubing inner half-widths
        y_head, y_pk, y_bot = 2.05, -2.55, -3.45
        y_m = [0.95, -0.55, -1.95]                    # mandrels (valve 1, 2, 3)
        xv = cx + ti + 0.16                           # valve x (on the tubing's annulus side)
        # unloading timing
        u0 = s[5] + 0.4
        tv_open = [u0 + 2.2, u0 + 5.4, u0 + 8.6]      # each valve uncovered and opening
        tv_close = [u0 + 6.0, u0 + 9.2, None]         # the one above closes when the next takes over
        level_keys = [(u0, y_head - 0.05), (tv_open[0], y_m[0] - 0.12), (tv_open[0] + 0.6, y_m[0] - 0.12), (tv_open[1], y_m[1] - 0.12),
                      (tv_open[1] + 0.6, y_m[1] - 0.12), (tv_open[2], y_m[2] - 0.12)]
        t_gas_a = s[2] + 0.6                          # scene A: steady gas lift at the deepest valve

        def ann_level(t):
            if t < u0 - 0.6:
                return None                           # scene A: annulus full of gas down to the operating valve
            return D.keys(t, level_keys)

        def valve_open(i, t):
            """0..1 open state of valve i (0 = top)."""
            if t < u0 - 0.6:
                return 1.0 if (i == 2 and t > t_gas_a + 0.4) else 0.0
            a = D.ramp(t, tv_open[i] - 0.3, tv_open[i] + 0.2)
            if tv_close[i] is not None:
                a *= 1.0 - D.ramp(t, tv_close[i], tv_close[i] + 0.5)
            return a

        def draw_well(c, t, look):
            a = D.vis(t, b.start + 0.2, t_end_lift, 0.5)
            if a <= 0:
                return
            # rock and reservoir
            D.fill(c, cx - 2.0, y_pk - 0.35, cx + 2.0, y_head - 0.1, P.ROCK, 0.55 * a)
            D.fill(c, cx - 2.0, y_bot, cx + 2.0, y_pk - 0.35, P.SAND, 0.85 * a)
            # casing (with the annulus) and tubing
            D.fill(c, cx - ci, y_pk - 0.35, cx + ci, y_head, darken(hex_rgb(P.BG), 0.3), a)
            for sd in (-1, 1):
                D.steel(c, cx + sd * ci, y_pk - 0.4, cx + sd * (ci + 0.09), y_head, P.STEEL_DK, a)
            # annulus contents
            lv = ann_level(t)
            gas_rgb = P.GAS
            for sd in (-1, 1):
                x0, x1 = (cx - ci, cx - ti - 0.07) if sd < 0 else (cx + ti + 0.07, cx + ci)
                if lv is None:
                    g_on = D.ramp(t, t_gas_a, t_gas_a + 2.0)
                    yb = y_m[2] - 0.1
                    D.fill(c, x0, y_pk, x1, y_head, "#3b5f86", 0.55 * a * (1 - g_on) + 0.0)
                    D.fill(c, x0, yb, x1, y_head, gas_rgb, 0.28 * a * g_on)
                    D.fill(c, x0, y_pk, x1, yb, "#3b5f86", 0.55 * a * g_on)
                else:
                    D.fill(c, x0, y_pk, x1, lv, "#3b5f86", 0.6 * a)
                    D.fill(c, x0, lv, x1, y_head, gas_rgb, 0.28 * a)
                    D.stroke(c, [(x0, lv), (x1, lv)], lighten(hex_rgb("#3b5f86"), 0.4), 0.02, a)
            # tubing liquid: heavy oil column, lightened by gas above the active valve
            D.fluid(c, cx - ti, y_pk - 0.3, cx + ti, y_head + 0.6, P.OIL, 0.85 * a)
            for sd in (-1, 1):
                D.steel(c, cx + sd * ti, y_pk - 0.3, cx + sd * (ti + 0.07), y_head + 0.6, P.STEEL, a)
            # packer
            for sd in (-1, 1):
                x0, x1 = (cx - ci, cx - ti - 0.07) if sd < 0 else (cx + ti + 0.07, cx + ci)
                D.flat(c, x0, y_pk - 0.12, x1, y_pk + 0.12, "#5a6b8c", a)
            # perforations
            for k in range(3):
                yy = y_bot + 0.25 + 0.2 * k
                for sd in (-1, 1):
                    D.fill(c, cx + sd * (ci + 0.09), yy - 0.03, cx + sd * (ci + 0.6), yy + 0.03, darken(hex_rgb(P.BG), 0.3), a)
            # mandrels and valves
            for i, ym in enumerate(y_m):
                D.steel(c, cx + ti + 0.07, ym - 0.3, cx + ti + 0.3, ym + 0.3, P.STEEL, a)
                o = valve_open(i, t)
                col = P.SAFE if o > 0.5 else P.STEEL_DK
                D.flat(c, xv - 0.06, ym - 0.17, xv + 0.06, ym + 0.17, col, a, r=0.03)
                if o > 0.05:
                    D.glow(c, look, xv, ym, 0.22, P.SAFE, 0.6 * o * a)
                D.text(c, look, str(i + 1), cx + ti + 0.48, ym, 0.16, P.MUTED, a * D.vis(t, s[5], None, 0.4), kind="bold")
            # wellhead, tree and lines
            D.steel(c, cx - ci - 0.25, y_head, cx + ci + 0.25, y_head + 0.3, P.STEEL_DK, a)
            D.steel(c, cx - 0.25, y_head + 0.3, cx + 0.25, y_head + 0.95, P.STEEL, a)
            D.steel(c, cx + 0.25, y_head + 0.68, cx + 1.4, y_head + 0.82, P.STEEL, a)          # flowline
            D.steel(c, cx + ci + 0.25, y_head + 0.08, cx + ci + 1.1, y_head + 0.2, P.STEEL, a)   # gas injection line
            g_in = D.ramp(t, t_gas_a - 0.6, t_gas_a) if t < u0 - 0.6 else 1.0
            D.arrow(c, cx + ci + 1.25, y_head + 0.14, cx + ci + 0.45, y_head + 0.14, P.GAS, 0.06, 0.18, a * g_in)
            D.text(c, look, "gas in", cx + ci + 1.0, y_head + 0.42, 0.16, P.GAS, a * g_in, kind="bold")
            flowing = t > s[2] + 2.5
            D.arrow(c, cx + 1.05, y_head + 0.75, cx + 1.7, y_head + 0.75, P.OIL, 0.06, 0.18, a * D.ramp(t, s[2] + 2.5, s[2] + 3.2))

        st.procedural(b.start, b.end, 0.3, draw_well)

        # gas bubbles in the tubing above the active valve, and gas down the annulus
        def bubbles(i, t0, t1):
            st.flow([(xv, y_m[i]), (cx + 0.05, y_m[i] + 0.1), (cx, y_head + 0.5)], t0, t1, P.GAS, n=7, speed=0.55, r=0.045, z=0.35, jitter=0.05)
        bubbles(2, t_gas_a + 0.8, u0 - 0.6)
        st.flow([(cx + ci - 0.15, y_head - 0.1), (cx + ci - 0.15, y_m[2] + 0.1), (xv + 0.08, y_m[2])], t_gas_a, u0 - 0.6, P.GAS, n=6, speed=0.6, r=0.035, z=0.34)
        for i in range(3):
            t1 = tv_close[i] + 0.4 if tv_close[i] else t_end_lift
            bubbles(i, tv_open[i], t1)
        st.flow([(cx, y_pk - 0.2), (cx, y_head + 0.5), (cx + 1.6, y_head + 0.75)], s[2] + 2.5, t_end_lift, P.OIL, n=8, speed=0.45, r=0.04, z=0.33)
        stall = K.xmark(st, cx + 1.25, y_head + 0.75, 0.16, s[1] + 2.0)
        K.show(st, stall, s[1] + 1.9, s[2] + 2.3, 0.3)

        # ------------------------------------------------------------------ scene A: pressure at the bottom of the well
        bx0, by0 = -2.9, -2.9
        bars = [st.rect(bx0, by0, 0.5, 1.6, P.WATER, 0.6, anchor="b", role="flat"), st.rect(bx0 + 1.35, by0, 0.5, 2.25, P.MUD, 0.6, anchor="b", role="flat")]
        bl = [st.text("reservoir\npushes", bx0, by0 - 0.2, 0.17, P.WATER, 0.6, valign="t"), st.text("column\nweighs", bx0 + 1.35, by0 - 0.2, 0.17, P.MUD, 0.6, valign="t")]
        bt = st.text("PRESSURE AT THE BOTTOM", bx0 + 0.68, by0 + 2.6, 0.16, P.MUTED, 0.6, kind="bold")
        K.show(st, bars + bl + [bt], s[1] + 0.5, s[3] - 0.4, 0.5)
        st.scale_to(bars[1], s[2] + 1.0, s[2] + 3.5, sy=1.2)
        lab_a = K.callout(st, "gas lightens the column", -3.95, 1.05, cx + 0.2, 0.55, size=0.18, align="l")
        K.show(st, lab_a, s[2] + 2.0, s[3] - 0.3, 0.4)

        # ------------------------------------------------------------------ scene B / D: the valve close-up
        vx, vtop, L, w = -0.3, 3.1, 5.8, 1.2
        yv = lambda k: vtop - k * L
        x_web0, x_web1 = vx - w / 2 - 0.24, vx - w / 2 - 0.1
        x_out0, x_out1 = vx + w / 2 + 0.1, vx + w / 2 + 0.24
        y_port = yv(sum(G.VF["ports"]) / 2)
        y_nose = yv(1.0)
        x_ann = x_out1 + 0.55
        win1 = (s[3] - 0.3, s[5] + 0.2)
        win2 = (s[6] - 0.5, t_end_lift)
        t_open = b.word(4, "push it open")
        t_press = b.word(4, "until the gas pressure")

        def close_alpha(t):
            return max(D.vis(t, win1[0], win1[1], 0.5), D.vis(t, win2[0], win2[1], 0.5))

        def lift_state(t):
            if t < win2[0]:
                return D.ramp(t, t_open - 0.2, t_open + 0.8)
            return 0.0

        def draw_close(c, t, look):
            a = close_alpha(t)
            if a <= 0:
                return
            D.flat(c, -2.2, -3.4, 1.62, 3.42, P.PANEL, 0.75 * a, r=0.12)
            # tubing (left of the web) and annulus (right of the outer wall)
            D.fluid(c, -2.05, -3.3, x_web0, 3.3, P.OIL, 0.55 * a)
            D.fill(c, x_out1, -3.3, x_ann, 3.3, P.GAS, 0.22 * a)
            D.steel(c, x_ann, -3.3, x_ann + 0.08, 3.3, P.STEEL_DK, 0.9 * a)
            # pocket: web with the discharge opening, outer wall with the port, bottom cap, latch lug
            D.fill(c, x_web1, y_nose - 0.25, x_out0, vtop + 0.25, darken(hex_rgb(P.BG), 0.3), a)
            D.steel(c, x_web0, y_nose - 0.12, x_web1, 3.3, P.STEEL, a)
            D.steel(c, x_web0, -3.3, x_web1, y_nose - 0.32, P.STEEL, a)
            D.steel(c, x_out0, y_port + 0.1, x_out1, 3.3, P.STEEL, a)
            D.steel(c, x_out0, -3.3, x_out1, y_port - 0.1, P.STEEL, a)
            D.steel(c, x_web1, y_nose - 0.45, x_out0, y_nose - 0.3, P.STEEL_DK, a)
            yl = yv(G.VF["ring"][0]) + 0.03
            for x0, x1 in ((x_web1, x_web1 + 0.06), (x_out0 - 0.06, x_out0)):
                D.steel(c, x0, yl, x1, yl + 0.08, P.STEEL_DK, a)
            # gauge: annulus pressure
            p = 0.35 + 0.5 * D.ramp(t, t_press, t_open)
            gx, gy, gr = 2.35, 3.2, 0.28
            D.disc(c, gx, gy, gr, P.PANEL2, a)
            D.ring(c, gx, gy, gr, 0.025, P.STEEL, a)
            ang = math.radians(210 - 240 * p)
            D.stroke(c, [(gx, gy), (gx + 0.8 * gr * math.cos(ang), gy + 0.8 * gr * math.sin(ang))], P.GAS, 0.03, a)
            D.text(c, look, "annulus pressure", gx, gy - 0.46, 0.14, P.MUTED, a)
            D.stroke(c, [(gx - gr, gy), (x_ann - 0.05, gy - 0.2)], P.MUTED, 0.012, 0.7 * a)
            # the valve
            chk = 1.0 if (lift_state(t) > 0.5) else 0.0
            G.draw_valve(c, look, vx, vtop, L, w, a, detail="full", lift=lift_state(t), check_open=chk)
            # reverse flow blocked (scene D)
            if t > s[6]:
                f = D.ramp(t, s[6] + 0.3, s[6] + 1.3)
                D.arrow(c, -1.6, y_nose - 0.38, vx - 0.05, y_nose - 0.38, P.BAD, 0.06, 0.2, a * f)
                D.arrow(c, vx, y_nose - 0.3, vx, yv(G.VF["check"][1]) + 0.05, P.BAD, 0.05, 0.17, a * D.ramp(t, s[6] + 1.0, s[6] + 1.8))
                D.flash(c, look, vx, yv(G.VF["check"][0]) - 0.05, 0.4, P.BAD, (t - (s[6] + 1.9)) / 0.8)

        st.procedural(b.start, b.end, 0.7, draw_close)
        # the gas path through the valve, while it is open
        path = G.valve_flow_path(vx, vtop, L, w, x_ann - 0.1, -1.3, 3.2)
        st.flow(path, t_open + 0.6, win1[1], P.GAS, n=14, speed=0.9, r=0.05, z=0.75)
        # zoom lines from the operating mandrel to the close-up
        zl = [st.line([(xv + 0.25, y_m[2] + 0.3), (-2.2, 3.42)], P.MUTED, 0.015, 0.25), st.line([(xv + 0.25, y_m[2] - 0.3), (-2.2, -3.4)], P.MUTED, 0.015, 0.25)]
        K.show(st, zl, win1[0], win1[1], 0.5)
        # labels on the valve
        lx = 1.95
        labels = [("latch", yv(0.17), (vx + 0.42 * w, yv(0.17)), s[3] + 0.4, None),
                  ("nitrogen dome", yv(0.365), (vx + 0.3 * w, yv(0.365)), b.word(4, "charged with nitrogen"), None),
                  ("bellows", yv(0.52) + 0.1, (vx + 0.28 * w, yv(0.52)), b.word(4, "A bellows"), None),
                  ("ports to the annulus", yv(0.638) + 0.2, (x_out1, y_port), t_press, None),
                  ("ball on its seat", yv(0.675) - 0.3, (vx + 0.1 * w, yv(0.675)), b.word(4, "holds a ball"), None),
                  ("packing", yv(0.74) - 0.55, (vx + 0.55 * w, yv(0.74)), t_press + 0.6, None),
                  ("check valve", yv(0.86) - 0.45, (vx + 0.1 * w, yv(0.86)), s[3] + 0.8, None),
                  ("into the tubing", y_nose - 0.6, (-1.3, y_nose - 0.3), t_open + 1.0, None)]
        for text, y, (tx, ty), t0, _ in labels:
            parts = K.callout(st, text, lx, y, tx, ty, size=0.17, align="l", z=1.1)
            st.fade_in(parts, t0, 0.35)
            st.fade_out(parts, win1[1] - 0.2, 0.4)
        for text, y, (tx, ty) in [("check valve: no flow back", yv(0.86), (vx + 0.1 * w, yv(0.86))), ("latch", yv(0.17), (vx + 0.42 * w, yv(0.17)))]:
            parts = K.callout(st, text, lx, y, tx, ty, size=0.17, align="l", z=1.1, color=P.PANEL2)
            K.show(st, parts, win2[0] + 0.2, t_end_lift - 0.3, 0.35)
        wire = K.tag(st, 1.95, -2.75, "changed by wire: chapter 4", color=P.WARN, fg=P.BG, size=0.17, z=1.2, align="l")
        K.show(st, wire, s[7] + 0.1, t_end_lift - 0.3, 0.35)

        # ------------------------------------------------------------------ scene C: unloading steps
        steps = ["gas enters at the top valve", "the level passes valve 2: it opens", "valve 1 closes", "gas reaches the deepest: the operating valve"]
        times = [tv_open[0], tv_open[1], tv_close[0], tv_open[2] + 0.4]
        title = K.title(st, "START-UP: UNLOADING", -3.1, 2.55, 0.27, P.TEXT)
        K.show(st, title, s[5] + 0.1, s[6] - 0.6, 0.4)
        sl = K.steps_list(st, -2.9, 1.75, steps, times, size=0.22, dy=0.65, z=0.9, color=P.SAFE)
        st.fade_out(sl, s[6] - 0.6, 0.4)
        op = K.callout(st, "operating valve", -3.1, -2.55, xv + 0.08, y_m[2], color=P.SAFE, fg=P.BG, size=0.18, align="l", z=1.0)
        K.show(st, op, tv_open[2] + 0.6, t_end_lift - 0.3, 0.4)
        lvl = K.callout(st, "annulus liquid level", -3.1, -0.4, cx + ci - 0.2, 0.3, size=0.17, align="l", z=1.0)
        K.show(st, lvl, u0 + 0.6, tv_open[1], 0.4)

        # ------------------------------------------------------------------ scene E: gas well, liquid loading, velocity string
        t_e = s[8]
        for k, gx in enumerate((-3.6, 2.4)):
            title = ["gas well: liquid loading", "with a velocity string"][k]
            t_show = t_e - 0.1 if k == 0 else s[11] - 0.4
            yt_, yb_ = 2.45, -3.0
            cas = [st.rect(gx - 0.95, (yt_ + yb_) / 2, 0.1, yt_ - yb_, P.STEEL_DK, 0.4, role="steel"), st.rect(gx + 0.95, (yt_ + yb_) / 2, 0.1, yt_ - yb_, P.STEEL_DK, 0.4, role="steel")]
            tub = [st.rect(gx - 0.42, (yt_ + yb_) / 2 + 0.1, 0.08, yt_ - yb_ - 0.2, P.STEEL, 0.45, role="steel"), st.rect(gx + 0.42, (yt_ + yb_) / 2 + 0.1, 0.08, yt_ - yb_ - 0.2, P.STEEL, 0.45, role="steel")]
            sand = [st.rect(gx, yb_ - 0.2, 2.6, 0.45, P.SAND, 0.2)]
            gas = st.rect(gx, (yt_ + yb_) / 2 + 0.1, 0.76, yt_ - yb_ - 0.2, P.GAS, 0.3, alpha=0.18)
            ttl = st.text(title, gx, yt_ + 0.35, 0.22, P.TEXT, 0.8, kind="bold")
            K.show(st, cas + tub + sand + [gas, ttl], t_show, None, 0.5)
            if k == 0:
                st.flow([(gx, yb_ + 0.3), (gx, yt_ - 0.1)], t_e + 0.3, b.end, P.GAS, n=5, speed=0.25, r=0.045, z=0.5)
                st.flow([(gx - 0.15, yt_ - 0.4), (gx - 0.15, yb_ + 0.8)], s[9] + 0.2, b.end, P.WATER, n=6, speed=0.35, r=0.06, z=0.52, jitter=0.08)
                st.flow([(gx + 0.15, yt_ - 0.9), (gx + 0.15, yb_ + 0.8)], s[9] + 0.8, b.end, P.WATER, n=5, speed=0.3, r=0.05, z=0.52, jitter=0.08)
                pool = st.rect(gx, yb_ + 0.15, 0.76, 0.0001, P.WATER, 0.5, anchor="b")
                K.show(st, [pool], s[9] + 0.5, None, 0.3)
                st.scale_to(pool, s[9] + 1.0, s[10] + 1.5, sy=1.4)
                K.show(st, K.tag(st, gx + 1.6, yb_ + 0.8, "liquid pool: the well chokes", color=P.WATER, fg=P.BG, size=0.17, z=0.9, align="l"), s[10] - 0.2, None, 0.4)
                K.show(st, K.tag(st, gx + 1.6, 1.0, "slow gas: droplets fall back", color=P.PANEL2, size=0.17, z=0.9, align="l"), s[9] + 1.0, None, 0.4)
            else:
                vs = [st.rect(gx - 0.17, (yt_ + yb_) / 2 + 0.3, 0.05, yt_ - yb_ - 0.8, P.WIRE, 0.6, role="steel"), st.rect(gx + 0.17, (yt_ + yb_) / 2 + 0.3, 0.05, yt_ - yb_ - 0.8, P.WIRE, 0.6, role="steel")]
                K.show(st, vs, s[11] + 0.2, None, 0.5)
                st.flow([(gx, yb_ + 0.6), (gx, yt_ - 0.1)], s[11] + 0.6, b.end, P.GAS, n=10, speed=1.1, r=0.04, z=0.62)
                st.flow([(gx, yb_ + 0.7), (gx, yt_ - 0.1)], s[11] + 0.9, b.end, P.WATER, n=5, speed=1.1, r=0.045, z=0.63)
                K.show(st, K.tag(st, gx + 1.25, 0.6, "velocity string", color=P.WIRE, fg=P.BG, size=0.18, z=0.9, align="l"), s[11] + 0.4, None, 0.4)
                K.show(st, K.tag(st, gx + 1.25, 0.05, "faster gas carries the water out", color=P.PANEL2, size=0.17, z=0.9, align="l"), s[11] + 1.5, None, 0.4)
