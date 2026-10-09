"""Ch 4, beat 4.06: changing a gas-lift valve with a kick-over tool (called from x_ch04b.build in place of the old beat).

A full-height side-pocket mandrel cutaway is the stage. The kick-over tool is run past the mandrel, picked up; its orienting
key rides the helical sleeve (the plan view shows the tool turning) into the slot; at the top of the slot the line tension
jumps; a little more pull and the arm kicks over above the pocket; slack off, the pulling tool lands on the valve's latch;
jar down to latch on, jar up to shear the latch pin; the valve comes out; the arm folds through the sleeve. A live
line-tension trace shows what the operator sees. Then a fast replay of setting a new valve, and the two-trip count.
All the moving hardware is drawn procedurally (scenes/common/gaslift.py) so the linkage geometry stays exact.
"""
from __future__ import annotations
import math

from scenes.common import palette as P
from scenes.common import kit as K
from scenes.common import gaslift as G
from scenes.common import pdraw as D
from scenes.common.look import darken
from scenes.common.stage import hex_rgb


def b406(st, tl):
    b = tl["4.06"]
    s = b.sent
    with st.span(b.start, b.end):
        g = G.SPM(-4.95, 3.75, -3.7, s=1.3)
        S = g.s
        t_in = b.start + 0.1
        # ------------------------------------------------------------------ the pulling run (absolute chapter times)
        ts0, ts1 = s[1] + 0.8, s[1] + 5.6                  # a straight tool passes the pocket by
        tk0, tk1 = s[2] + 0.1, s[3] + 3.4                  # kick-over tool runs in past the mandrel
        tp0 = s[3] + 3.9                                    # pick-up starts
        th0, th1 = s[4] + 0.8, s[4] + 7.0                  # key on the helix: the tool turns
        t_top = s[5] - 0.1                                  # key at the top of the slot
        tk_0, tk_1 = s[6] + 1.6, s[6] + 2.2                # the arm kicks over
        tl0, tl1 = s[8] + 0.1, s[8] + 3.6                  # slack off; the pulling tool lands on the latch
        tjd = [s[9] + 0.5, s[9] + 1.3]                      # jar down
        tju0, tju = s[10] + 0.2, s[10] + 1.4               # jar up: wire stretches, the jar fires, the pin shears
        tr0, tr1 = s[10] + 1.8, s[10] + 5.4                # the valve is pulled out of the pocket
        tf0, tf1 = s[11] + 0.1, s[11] + 2.0                # the arm folds through the sleeve while rising
        to0, to1 = s[11] + 2.1, s[11] + 3.5                # tool and valve leave upward
        # setting replay (trip 2)
        u0 = s[12]
        tn0, tn1 = u0 + 0.2, u0 + 1.6                      # running tool + new valve come down, arm folded, already turned
        tnk0, tnk1 = u0 + 1.8, u0 + 2.4                    # kick
        tnl0, tnl1 = u0 + 2.6, u0 + 5.0                    # lower the valve into the pocket
        tnd = u0 + 5.6                                      # jar down: the latch ring snaps under the lug
        tnu = u0 + 7.4                                      # jar up: the running tool shears free
        tnr0, tnr1 = u0 + 7.8, u0 + 9.0                    # running tool lifts away (fold)
        tno0, tno1 = u0 + 9.0, u0 + 10.4                   # and leaves

        y_low = g.key_for_tool_bottom(-3.45, kick=0.0)       # run past: tool well below the pocket
        key_hold = g.key_land
        # rise that lifts the valve clear of the pocket, then the folding stretch
        rise_a = (g.y_pt + 0.1) - (g.v_top - g.L) - 0.45
        y_key_out_a = key_hold + rise_a
        y_key_fold = y_key_out_a + 0.75

        def key_y(t):
            if t < tk0:
                return None
            pts = [(tk0, 6.9), (tk1, y_low), (tp0, y_low), (th0, g.ys1), (th1, g.y_slot), (t_top, g.key_top), (tl0, g.key_top),
                   (tl1, key_hold), (tju0, key_hold), (tju, key_hold + 0.05 * S), (tr0, key_hold + 0.05 * S), (tr1, y_key_out_a),
                   (tf0, y_key_out_a), (tf1, y_key_fold), (to0, y_key_fold), (to1, y_key_fold + 6.0)]
            y = D.keys_lin(t, pts[:3]) if t < tp0 else D.keys(t, pts[2:])
            # jar-down bumps (the tool is hammered down a hair), and a small stretch before the jar fires
            for tj in tjd:
                y -= 0.04 * S * math.exp(-((t - tj) / 0.08) ** 2)
            return y

        def phi(t):
            if t < th0:
                return math.pi
            if t > th1:
                return 0.0
            y = key_y(t)
            u = min(max((y - g.ys1) / (g.y_slot - g.ys1), 0.0), 1.0)
            return math.pi * (1.0 - u)

        def kick(t):
            return D.ramp(t, tk_0, tk_1) * (1.0 - D.ramp(t, tf0, tf1))

        def grip(t):
            return D.ramp(t, tjd[0] - 0.1, tjd[0] + 0.1)

        # ------------------------------------------------------------------ the second trip
        new_key_hi = g.key_top + 0.0
        def key_y2(t):
            if t < tn0 or t > tno1 + 0.5:
                return None
            pts = [(tn0, 6.5), (tn1, new_key_hi), (tnl0, new_key_hi), (tnl1, key_hold), (tnd - 0.05, key_hold),
                   (tnr0, key_hold), (tnr1, key_hold + 0.9), (tno0, key_hold + 0.9), (tno1, key_hold + 7.0)]
            y = D.keys(t, pts)
            y -= 0.04 * S * math.exp(-((t - tnd) / 0.08) ** 2)
            return y

        def kick2(t):
            return D.ramp(t, tnk0, tnk1) * (1.0 - D.ramp(t, tnr0, tnr1))

        def draw(c, t, look):
            a_m = D.vis(t, t_in, None, 0.6)
            # casing and annulus (right of the mandrel)
            xc = g.xO + g.wall + 0.42
            D.fill(c, g.xO + g.wall, -3.7, xc, 3.9, P.GAS, 0.07 * a_m)
            D.steel(c, xc, -3.7, xc + 0.12, 3.9, P.STEEL_DK, 0.85 * a_m)
            hl = "sleeve" if s[4] < t < s[5] + 1 else ("lug" if s[9] - 0.2 < t < s[10] + 1.5 else None)
            G.draw_spm(c, look, g, a_m, highlight=hl)
            # ---- the old valve: in the pocket until the pin shears, then it rides out on the pulling tool
            k = key_y(t)
            tool_xy = None
            if k is not None:
                a_t = D.vis(t, tk0, to1 - 0.4, 0.4)
                tool_xy = G.draw_kot(c, look, g, k, phi(t), kick(t), a_t, tool="pulling", grip=grip(t), wire_top=4.6)
            sheared = t >= tju
            if not sheared or tool_xy is None:
                G.draw_valve(c, look, g.px, g.v_top, g.L, g.vw, a_m, detail="body", ring=1.0, pin=1.0, outline=P.BAD if t > s[0] + 1 else None)
            else:
                xv, ytb = tool_xy
                G.draw_valve(c, look, xv, ytb + 0.12 * S, g.L, g.vw, D.vis(t, tk0, to1 - 0.4, 0.4), detail="body", ring=0.0, pin=0.0,
                             outline=P.BAD)
            if tool_xy is not None and t < tju:
                # draw the pulling tool over the valve neck once it lands (it covers the neck)
                pass
            # ---- the straight tool that misses
            if ts0 - 0.2 < t < ts1 + 0.6:
                yb = D.keys_lin(t, [(ts0, 6.2), (ts1, -4.6)])
                G.draw_straight_tool(c, look, g.bx, yb, S, D.vis(t, ts0 - 0.2, ts1 + 0.1, 0.4))
            # ---- trip 2: running tool and the new valve
            k2 = key_y2(t)
            if k2 is not None:
                a2 = D.vis(t, tn0, tno1 - 0.4, 0.4)
                set_ = t >= tnu
                xy2 = G.draw_kot(c, look, g, k2, 0.0, kick2(t), a2, tool="running", wire_top=4.6)
                if xy2 is not None and not set_:
                    xv, ytb = xy2
                    G.draw_valve(c, look, xv, ytb + 0.12 * S, g.L, g.vw, a2, detail="body", ring=D.ramp(t, tnd - 0.05, tnd + 0.15),
                                 pin=1.0, outline=P.SAFE)
            if t >= tnu:
                G.draw_valve(c, look, g.px, g.v_top, g.L, g.vw, a_m, detail="body", ring=1.0, pin=1.0, outline=P.SAFE)
            # ---- impacts
            for tj in tjd:
                D.flash(c, look, g.px, g.v_top + 0.05 * S, 0.45 * S, P.WARN, (t - tj) / 0.6)
            D.flash(c, look, g.px, g.valve_y(0.145), 0.5 * S, P.BAD, (t - tju) / 0.7)
            D.flash(c, look, g.px, g.y_lug, 0.5 * S, P.SAFE, (t - tnd) / 0.7)
            D.flash(c, look, g.px, g.v_top + 0.2 * S, 0.45 * S, P.BAD, (t - tnu) / 0.6)
            D.flash(c, look, g.bx + g.key_r, g.key_top, 0.35 * S, P.WARN, (t - t_top) / 0.8)
            D.flash(c, look, g.bx, g.key_top - g.key_to_pivot, 0.4 * S, P.WARN, (t - tk_1) / 0.7)
            # ---- plan view
            a_p = D.vis(t, s[1] - 0.3, s[13] - 0.5, 0.5)
            ph = phi(t) if t < u0 else 0.0
            kk = kick(t) if t < u0 else kick2(t)
            G.draw_plan(c, look, 2.25, 1.45, 0.5, ph, kk, a_p, title="looking down the well")

        st.procedural(b.start, b.end, 0.5, draw)

        # ------------------------------------------------------------------ line-tension trace (what the operator sees)
        gx0, gx1, gy0, gy1 = -1.75, 7.55, -3.3, -0.62
        tw0, tw1 = s[3] - 0.3, s[11] + 3.4

        def tension(t):
            v = 1.0 + 0.025 * math.sin(t * 7.3) + 0.015 * math.sin(t * 17.1)
            v += 0.12 * D.ramp(t, tp0, tp0 + 0.6)                       # picking up: drag adds to the weight
            v += 0.05 * math.sin((t - th0) * 3.0) * (th0 < t < th1)       # the key rubbing up the helix
            v += 0.62 * D.ramp(t, t_top - 0.25, t_top + 0.1)              # top of the slot: tension jumps
            v += 0.22 * D.lin(t, tk_0 - 1.4, tk_0)                       # a little more pull ...
            v -= 0.84 * D.ramp(t, tk_0, tk_1)                             # ... the arm kicks over: back to the pick-up weight
            v -= 0.12 * D.ramp(t, tl0, tl0 + 0.5)                         # slacking off: no drag
            v -= 0.55 * D.ramp(t, tl1 - 0.4, tl1)                         # the tool lands: weight set down
            for tj in tjd:
                v -= 0.32 * math.exp(-((t - tj) / 0.07) ** 2)             # jar down blows
            v += 0.55 * D.ramp(t, tju0, tju - 0.05)                       # pulling up: the wire stretches
            v += 1.05 * math.exp(-((t - tju) / 0.06) ** 2)                # the jar fires: a sharp spike, the pin shears
            v -= 0.55 * D.ramp(t, tju, tju + 0.2)
            v += 0.35 * D.ramp(t, tr0, tr0 + 0.3) - 0.35 * D.ramp(t, tr0 + 0.6, tr0 + 1.4)   # packing drag as the valve unseats
            return v

        def gmap(t, v):
            return gx0 + 0.3 + (gx1 - gx0 - 0.5) * (t - tw0) / (tw1 - tw0), gy0 + 0.35 + (gy1 - gy0 - 0.75) * (v / 2.6)

        notes = [(tk1 - 1.0, "running in"), (tp0 + 1.0, "picking up"), (t_top, "top of the slot: tension jumps"), (tk_1, "arm kicks over"),
                 (tl1, "tool lands"), (tjd[0], "jar down"), (tju, "jar up: pin shears"), (tr1 - 1.5, "valve out")]

        def draw_trace(c, t, look):
            a = D.vis(t, s[3] - 0.4, s[12] - 0.2, 0.5)
            if a <= 0:
                return
            D.flat(c, gx0, gy0, gx1, gy1, P.PANEL, 0.92 * a, r=0.1)
            D.text(c, look, "LINE TENSION AT THE SURFACE", gx0 + 0.25, gy1 - 0.2, 0.15, P.MUTED, a, align="l", kind="bold")
            D.stroke(c, [(gx0 + 0.3, gy0 + 0.3), (gx1 - 0.2, gy0 + 0.3)], P.GRID, 0.012, a)
            D.stroke(c, [(gx0 + 0.3, gy0 + 0.3), (gx0 + 0.3, gy1 - 0.4)], P.GRID, 0.012, a)
            D.text(c, look, "time", gx1 - 0.45, gy0 + 0.15, 0.13, P.MUTED, a)
            yw = gmap(tw0, 1.0)[1]
            D.dashed(c, (gx0 + 0.3, yw), (gx1 - 0.2, yw), P.MUTED, 0.01, 0.6 * a)
            D.text(c, look, "string weight", gx0 + 0.35, yw + 0.13, 0.12, P.MUTED, 0.8 * a, align="l")
            te = min(t, tw1)
            if te <= tw0:
                return
            n = int((te - tw0) / 0.04) + 2
            pts = [gmap(tw0 + (te - tw0) * i / (n - 1), tension(tw0 + (te - tw0) * i / (n - 1))) for i in range(n)]
            D.stroke(c, pts, P.WARN, 0.045, a)
            D.glow(c, look, pts[-1][0], pts[-1][1], 0.12, P.WARN, 0.8 * a)
            D.disc(c, pts[-1][0], pts[-1][1], 0.045, "#ffffff", a)
            for i, (tn, label) in enumerate(notes):
                if t >= tn:
                    x, y = gmap(tn, tension(tn))
                    up = (i % 2 == 0)
                    ly = min(y + 0.42, gy1 - 0.55) if up else max(y - 0.4, gy0 + 0.5)
                    D.stroke(c, [(x, y), (x, ly)], P.MUTED, 0.01, 0.7 * a * D.lin(t, tn, tn + 0.3))
                    D.text(c, look, label, x, ly + (0.1 if up else -0.1), 0.13, P.TEXT, a * D.lin(t, tn, tn + 0.3))

        st.procedural(b.start, b.end, 0.6, draw_trace)

        # ------------------------------------------------------------------ the caption: what is happening now
        steps = [(s[0] + 0.6, "a gas-lift valve, latched in its pocket"), (ts0, "a tool run straight down passes the pocket by"),
                 (tk0, "run in past the mandrel, arm folded"), (tp0, "pick up: the key rides the helix, the tool turns"),
                 (t_top - 0.3, "top of the slot: the tension jumps"), (tk_0 - 0.6, "a little more pull: the arm kicks over"),
                 (tl0, "slack off: the pulling tool slides into the pocket"), (tjd[0] - 0.3, "jar down: latch on"),
                 (tju - 0.4, "jar up: the pin shears, the valve comes out"), (tf0, "through the sleeve the arm folds flat"),
                 (u0, "trip 2: a running tool sets the new valve"), (s[13], "pulling and setting: two trips per valve")]

        def draw_caption(c, t, look):
            cur = None
            for i, (tt, txt) in enumerate(steps):
                if t >= tt:
                    cur = i
            if cur is None:
                return
            for i in (cur - 1, cur):
                if i < 0:
                    continue
                tt, txt = steps[i]
                a = D.lin(t, tt, tt + 0.35) if i == cur else 1.0 - D.lin(t, steps[cur][0], steps[cur][0] + 0.3)
                if a > 0:
                    D.pill(c, look, txt, -2.25, 3.45, 0.21, P.PANEL2 if i != len(steps) - 1 else P.SAFE, P.TEXT if i != len(steps) - 1 else P.BG,
                           a * D.vis(t, b.start, b.end - 0.4, 0.3), align="l", kind="bold")

        st.procedural(b.start, b.end, 0.9, draw_caption)

        # ------------------------------------------------------------------ labels on the mandrel
        lab = [("main bore", g.xL - 0.4, 0.9, g.bx, 0.9, s[0] + 0.8, s[3])]
        for text, x, y, tx, ty, t0, t1 in lab:
            K.show(st, K.callout(st, text, x, y, tx, ty, size=0.18, align="r", z=1.2), t0, t1, 0.35)
        xs_ = g.xO + g.wall + 0.75
        lab_s = [("orienting sleeve", xs_, g.ys0 - 0.05, g.xR - 0.05, g.ys0 - 0.1, s[4] - 0.2, s[6]),
                 ("helix: turns the tool", xs_, g.ys1 - 0.25, g.bx + 0.1, g.ys1 + 0.12, s[4] + 1.0, s[6]),
                 ("slot", xs_, g.y_slot - 0.12, g.bx + g.key_r + 0.07, g.y_slot + 0.15, s[4] + 5.5, s[6])]
        for text, x, y, tx, ty, t0, t1 in lab_s:
            K.show(st, K.callout(st, text, x, y, tx, ty, size=0.18, align="l", z=1.2), t0, t1, 0.35)
        xr = g.xO + g.wall + 0.75
        lab_r = [("pocket", xr, 0.75, g.px, g.y_pt + 0.2, s[0] + 1.2, s[2]),
                 ("gas-lift valve", xr, g.v_top - 0.75, g.px + 0.15, g.v_top - 0.75, s[0] + 1.6, s[2]),
                 ("latch: neck and locking ring", xr, g.y_lug + 0.05, g.px + 0.2, g.y_lug + 0.02, s[8] + 2.5, s[10] + 1.2),
                 ("ports to the annulus", xr, g.y_port - 0.55, g.xO + g.wall / 2, g.y_port, s[0] + 2.0, s[2]),
                 ("annulus", xr, 2.0, g.xO + g.wall + 0.2, 2.0, s[0] + 2.4, s[2])]
        for text, x, y, tx, ty, t0, t1 in lab_r:
            K.show(st, K.callout(st, text, x, y, tx, ty, size=0.18, align="l", z=1.2), t0, t1, 0.35)

        # ------------------------------------------------------------------ the two-trip count
        trips = [K.tag(st, -1.6, -1.25, "TRIP 1   pull the old valve", color=P.PANEL2, size=0.22, z=1.3, align="l"),
                 K.tag(st, -1.6, -1.95, "TRIP 2   set the new valve", color=P.PANEL2, size=0.22, z=1.3, align="l")]
        K.show(st, trips[0], s[12] - 0.2, None, 0.4)
        K.show(st, trips[1], s[12] + 0.2, None, 0.4)
        K.show(st, K.check(st, 2.45, -1.25, s[12] + 0.3, s=0.17, z=1.4), s[12] + 0.2, None, 0.3)
        K.show(st, K.check(st, 2.45, -1.95, tnu + 0.3, s=0.17, z=1.4), tnu + 0.2, None, 0.3)
        tot = K.tag(st, -1.6, -2.75, "two trips for every valve changed", color=P.WARN, fg=P.BG, size=0.24, z=1.3, align="l")
        K.show(st, tot, s[13] + 0.3, None, 0.4)
