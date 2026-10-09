"""Ch 4, beats 4.08 - 4.10 (called from ch04_wireline.build).

4.08 electric line: real-time logging tied to casing collars (CCL), then a shaped charge: cone collapses into a jet through casing, cement, rock
4.09 e-line sets a bridge plug, cuts a pipe, and drives a tractor in a deviated well; beyond that: a pipe that can be pushed
4.10 the wireline scorecard (carry, pull, pump, push, rotate, power and data, stay live)
"""
from __future__ import annotations
import math
import random

from scenes.common import palette as P, model as M
from scenes.common import kit as K
from scenes.common import tools as T
from scenes.common.chart import Chart


# ====================================================================================================== 4.08
def b408(st, tl):
    b = tl["4.08"]
    s = b.sent
    with st.span(b.start, b.end):
        # ---------------- part 1: logging with a casing collar locator
        cx = -5.4
        collar_ys = [-2.9, -1.7, -0.5, 0.7, 1.9, 3.1]
        walls = [st.rect(cx - 0.62, 0.15, 0.14, 6.9, P.STEEL_DK, 0.3, role="steel"), st.rect(cx + 0.62, 0.15, 0.14, 6.9, P.STEEL_DK, 0.3, role="steel")]
        collars = [st.rect(cx, y, 1.6, 0.2, P.STEEL, 0.32, role="steel") for y in collar_ys]
        bore = st.rect(cx, 0.15, 1.1, 6.9, P.BG, 0.2)
        st.fade_in(walls + collars + [bore], b.start + 0.1, 0.5)
        y0, y1 = -2.4, 3.0
        tool = [st.rect(cx, y0, 0.5, 1.5, P.STEEL, 0.6, role="steel"), st.rect(cx, y0 + 0.55, 0.52, 0.2, P.WARN, 0.62, role="solid")]
        cable = st.rect(cx, 4.2, 0.05, 4.2 - (y0 + 0.75), P.COPPER, 0.55, anchor="t", role="steel")
        K.show(st, tool + [cable], s[0] + 0.3, None, 0.5)
        # electricity down, data up
        dn = st.arrow(cx + 0.95, 3.3, cx + 0.95, 2.3, P.WARN, 0.07, 0.26, 0.8)
        up = st.arrow(cx + 1.3, 2.3, cx + 1.3, 3.3, P.SAFE, 0.07, 0.26, 0.8)
        dt = K.note(st, "power", cx + 1.0, 3.55, 0.19, P.WARN, align="c")
        ut = K.note(st, "data", cx + 1.45, 3.55, 0.19, P.SAFE, align="c")
        K.show(st, dn + up + dt + ut, s[0] + 0.6, s[2], 0.4)
        # the tool is pulled up while the log is drawn in real time
        t_log0, t_log1 = s[1] + 0.3, s[2] + 7.0
        st.move(tool, t_log0, t_log1, dy=y1 - y0)
        st.scale_to(cable, t_log0, t_log1, sy=4.2 - (y1 + 0.75))
        # log tracks
        card = K.card(st, -1.55, 0.15, 4.0, 7.2, P.PANEL, 0.2)
        ccl_c, gr_c = -2.55, -0.65
        t1 = st.text("CCL", ccl_c, 3.5, 0.2, P.WARN, 0.5, kind="bold")
        t2 = st.text("GAMMA RAY", gr_c, 3.5, 0.2, P.PORE, 0.5, kind="bold")
        sep = st.rect(-1.55, 0.15, 0.015, 6.6, P.GRID, 0.3)
        K.show(st, card + [t1, t2, sep], s[1], None, 0.5)
        rnd = random.Random(3)
        ccl_pts = []
        gr_pts = []
        n = 140
        for k in range(n + 1):
            y = y0 + (y1 - y0) * k / n
            v = 0.0
            for cyy in collar_ys:
                v += 0.75 * math.exp(-((y - cyy) / 0.08) ** 2)
            ccl_pts.append((ccl_c - 0.55 + v * 0.0 + min(v, 1.0) * 1.1, y))
            gr_pts.append((gr_c + 0.35 * math.sin(y * 3.1) + 0.25 * math.sin(y * 7.7 + 1.0) + 0.12 * rnd.uniform(-1, 1), y))
        ccl = st.line(ccl_pts, P.WARN, 0.05, 0.5)
        gr = st.line(gr_pts, P.PORE, 0.05, 0.5)
        K.show(st, [ccl, gr], s[1], None, 0.1)
        st.draw_on(ccl, t_log0, t_log1, "LINEAR")
        st.draw_on(gr, t_log0, t_log1, "LINEAR")
        rt = K.tag(st, -1.55, -3.55, "real-time log", color=P.SAFE, fg=P.BG, size=0.21, z=0.9)
        K.show(st, rt, s[1] + 0.3, s[3] - 0.3, 0.4)
        # the collar log is tied to known collar depths
        ties = []
        for cyy in collar_ys[1:4]:
            ties += st.dashed((cx + 0.85, cyy), (ccl_c - 0.5, cyy), P.WARN, 0.025, 0.12, 0.1, 0.4)
        tt = b.word(2, "tied")
        K.show(st, ties, tt, s[3] - 0.3, 0.5)
        lab = K.tag(st, 1.3, -3.0, "log tied to known collar depths", color=P.WARN, fg=P.BG, size=0.2, z=0.9)
        K.show(st, lab, tt, s[3] - 0.3, 0.4)
        # fade the whole logging picture at the start of the next sentence group
        t_cut = s[3] - 0.3
        everything = walls + collars + [bore] + tool + [cable] + card + [t1, t2, sep, ccl, gr]
        st.fade_out(everything, t_cut, 0.5)

        # ---------------- part 2: a shaped charge
        t3 = s[3]
        # gun icon with three charges
        gun = [st.rect(-5.7, 3.5, 3.0, 0.5, P.STEEL_DK, 0.4, role="steel")]
        for xg in (-6.6, -5.7, -4.8):
            gun.append(st.poly([(xg - 0.18, 3.75), (xg + 0.18, 3.75), (xg, 3.32)], P.COPPER, 0.5, role="flat"))
        gl = K.note(st, "perforating gun: a carrier of shaped charges", -3.9, 3.5, 0.21, P.MUTED, align="l")
        K.show(st, gun + gl, t3 + 0.2, None, 0.5)
        # the charge: case, explosive, liner, detonator pointing right
        case = st.poly([(-6.5, -0.5), (-6.5, 0.5), (-4.4, 1.05), (-4.4, -1.05)], P.STEEL_DK, 0.4, role="solid")
        expl = st.poly([(-6.35, -0.42), (-6.35, 0.42), (-4.5, 0.92), (-4.5, -0.92)], "#e76f51", 0.45, alpha=0.9, role="flat")
        liner = [st.line([(-5.7, 0.0), (-4.42, 0.95)], P.COPPER, 0.13, 0.55), st.line([(-5.7, 0.0), (-4.42, -0.95)], P.COPPER, 0.13, 0.55)]
        det = st.circle(-6.62, 0.0, 0.1, P.WARN, 0.6, role="disc")
        cl = [K.callout(st, "metal-lined cone (liner)", -7.5, 2.0, -5.0, 0.5, size=0.2, align="l"), K.callout(st, "explosive", -7.5, -2.0, -5.9, -0.3, size=0.2, align="l")]
        K.show(st, [case, expl] + liner + [det] + cl[0] + cl[1], s[4] - 0.2, None, 0.5)
        # casing, cement, rock to the right
        cas = st.rect(-2.85, 0.0, 0.2, 5.0, P.STEEL, 0.4, role="steel")
        cem = st.rect(-2.5, 0.0, 0.5, 5.0, P.CEMENT, 0.38)
        rock = st.rect(-0.55, 0.0, 3.4, 5.0, P.SAND, 0.36)
        well = st.text("the well", -3.5, -2.7, 0.2, P.MUTED, 0.5)
        l_c = [st.text("casing", -2.85, 2.75, 0.19, P.MUTED, 0.5), st.text("cement", -2.4, -2.75, 0.19, P.MUTED, 0.5), st.text("reservoir rock", -0.5, 2.75, 0.19, P.SAND, 0.5)]
        K.show(st, [cas, cem, rock, well] + l_c, s[4], None, 0.5)
        # detonation: flash at the back, then the liner collapses into a jet
        t5 = b.word(5, "detonates")
        fl = st.circle(-6.62, 0.0, 0.18, P.WARN, 0.9)
        st.fade_in(fl, t5, 0.08)
        st.scale_to(fl, t5 + 0.1, t5 + 0.7, sx=1.8, sy=1.8)
        st.fade_out(fl, t5 + 0.2, 0.5)
        st.recolor([expl], t5 + 0.1, t5 + 0.6, "#ffd166")
        st.fade_out(liner, t5 + 0.6, 0.4)
        jet = st.rect(-4.5, 0.0, 0.01, 0.1, P.WARN, 0.8, anchor="l", role="shaft")
        K.show(st, [jet], t5 + 0.5, None, 0.1)
        st.scale_to(jet, t5 + 0.6, t5 + 1.3, sx=2.0)
        st.scale_to(jet, t5 + 1.3, t5 + 1.9, sx=4.9)
        tun = st.rect(-2.95, 0.0, 0.01, 0.2, P.BG, 0.7, anchor="l", role="hole")
        K.show(st, [tun], t5 + 1.1, None, 0.1)
        st.scale_to(tun, t5 + 1.1, t5 + 1.9, sx=3.0)
        st.fade_out(jet, t5 + 1.9, 0.5)
        jl = K.tag(st, -0.6, 1.1, "jet: several km per second", color=P.PANEL2, fg=P.WARN, size=0.22, z=0.9)
        K.show(st, jl, t5 + 0.7, None, 0.4)
        pen = K.note(st, "through casing, cement and a few tens of centimetres of rock", -2.0, -3.3, 0.2, P.TEXT, align="c")
        K.show(st, pen, b.word(5, "punches"), None, 0.5)
        # sentence 6: fired at the depth the collar log gave us
        fin = K.tag(st, 4.7, -2.6, "fired at the depth the collar log gave us", color=P.SAFE, fg=P.BG, size=0.22, z=0.9)
        K.show(st, fin, s[6], None, 0.5)


# ====================================================================================================== 4.09
def b409(st, tl):
    b = tl["4.09"]
    s = b.sent
    with st.span(b.start, b.end):
        t_a = s[0] + 0.3
        t_b = b.word(0, "cuts pipe")
        t_c = s[1]
        # ---------- A: bridge plug and its powder-charge setting tool
        ax = -5.8
        cas = [st.rect(ax - 0.75, 0.3, 0.14, 5.4, P.STEEL_DK, 0.3, role="steel"), st.rect(ax + 0.75, 0.3, 0.14, 5.4, P.STEEL_DK, 0.3, role="steel"),
               st.rect(ax, 0.3, 1.5, 5.4, P.BG, 0.2)]
        wire = st.rect(ax, 3.1, 0.035, 0.7, P.COPPER, 0.5, role="steel")
        sett = st.rect(ax, 1.9, 0.6, 1.5, P.PRIMARY_B, 0.55, role="flat")
        rubber = st.rect(ax, 0.55, 0.9, 0.7, P.RUBBER, 0.55, role="solid")
        rub_hi = st.rect(ax, 0.55, 0.9, 0.7, P.RUBBER_HI, 0.54, alpha=0.35, role="flat")
        slips = [st.rect(ax - 0.4, -0.1, 0.22, 0.5, P.WARN, 0.57, role="solid"), st.rect(ax + 0.4, -0.1, 0.22, 0.5, P.WARN, 0.57, role="solid"),
                 st.rect(ax - 0.4, 1.2, 0.22, 0.4, P.WARN, 0.57, role="solid"), st.rect(ax + 0.4, 1.2, 0.22, 0.4, P.WARN, 0.57, role="solid")]
        body = st.rect(ax, 0.5, 0.36, 2.4, P.STEEL, 0.5, role="steel")
        grpA = cas + [wire, sett, body, rubber, rub_hi] + slips
        tA = K.tag(st, ax, 3.55, "bridge plug", color=P.PANEL2, size=0.23, z=0.9)
        K.show(st, grpA + tA, b.start + 0.2, None, 0.5)
        pw = K.note(st, "slow-burning powder charge\ndrives the setting tool", ax, -2.75, 0.19, P.WARN, align="c")
        K.show(st, pw, t_a, t_b, 0.4)
        st.scale_to(rubber, t_a + 1.0, t_a + 2.2, sx=1.5)
        st.scale_to(rub_hi, t_a + 1.0, t_a + 2.2, sx=1.5)
        for k, sd in zip(slips, (-1, 1, -1, 1)):
            st.move(k, t_a + 1.0, t_a + 2.2, dx=sd * 0.2)
        st.move([sett, wire], t_a + 2.4, t_a + 3.4, dy=+1.2)
        ok = K.check(st, ax + 1.4, 0.5, t_a + 3.2)
        K.show(st, ok, t_a + 3.2, None, 0.2)
        # ---------- B: cutter
        bx = -2.3
        tw = [st.rect(bx - 0.5, 1.4, 0.14, 2.4, P.STEEL, 0.4, role="steel"), st.rect(bx + 0.5, 1.4, 0.14, 2.4, P.STEEL, 0.4, role="steel"),
              st.rect(bx - 0.5, -1.4, 0.14, 2.4, P.STEEL, 0.4, role="steel"), st.rect(bx + 0.5, -1.4, 0.14, 2.4, P.STEEL, 0.4, role="steel")]
        top_walls = tw[:2]
        cutter = st.rect(bx, 0.0, 0.5, 1.5, P.WARN, 0.6, role="solid")
        cw = st.rect(bx, 2.7, 0.035, 1.6, P.COPPER, 0.5, role="steel")
        tB = K.tag(st, bx, 3.55, "cutter", color=P.PANEL2, size=0.23, z=0.9)
        K.show(st, tw + [cutter, cw] + tB, t_b - 0.3, None, 0.5)
        flash = []
        for k in range(8):
            a = math.radians(45 * k + 22)
            flash.append(st.line([(bx + 0.3 * math.cos(a), 0.0 + 0.3 * math.sin(a)), (bx + 0.7 * math.cos(a), 0.0 + 0.7 * math.sin(a))], P.WARN, 0.06, 0.8))
        tc = t_b + 1.2
        K.show(st, flash, tc, None, 0.1)
        st.fade_out(flash, tc + 0.3, 0.5)
        st.move(top_walls, tc + 0.4, tc + 0.9, dy=0.35)
        gap = K.note(st, "pipe severed", bx, -2.75, 0.19, P.BAD, align="c")
        K.show(st, gap, tc + 0.4, None, 0.4)
        # ---------- C: tractor
        pipe_y = -0.2
        x0, x1 = 0.5, 7.5
        hw = [st.rect((x0 + x1) / 2, pipe_y + 0.55, x1 - x0, 0.14, P.STEEL_DK, 0.3, role="steel"), st.rect((x0 + x1) / 2, pipe_y - 0.55, x1 - x0, 0.14, P.STEEL_DK, 0.3, role="steel"),
              st.rect((x0 + x1) / 2, pipe_y, x1 - x0, 1.1, P.BG, 0.2)]
        tr_x = 2.2
        body_t = st.rect(tr_x, pipe_y, 1.6, 0.5, P.PRIMARY_B, 0.55, role="flat")
        wheels = [st.circle(tr_x - 0.5, pipe_y + 0.4, 0.2, P.STEEL, 0.6, role="solid"), st.circle(tr_x + 0.5, pipe_y + 0.4, 0.2, P.STEEL, 0.6, role="solid"),
                  st.circle(tr_x - 0.5, pipe_y - 0.4, 0.2, P.STEEL, 0.6, role="solid"), st.circle(tr_x + 0.5, pipe_y - 0.4, 0.2, P.STEEL, 0.6, role="solid")]
        spokes = [st.rect(w.location[0], w.location[1], 0.34, 0.04, P.STEEL_DK, 0.62, role="solid") for w in wheels]
        cab = st.rect(x0 - 0.1, pipe_y, 0.01, 0.05, P.COPPER, 0.5, anchor="l", role="steel")
        tC = K.tag(st, 3.7, 3.55, "downhole tractor", color=P.PANEL2, size=0.23, z=0.9)
        incl = K.note(st, "highly deviated or horizontal: tools no longer fall", 3.9, 1.3, 0.21, P.MUTED, align="c")
        K.show(st, hw + [body_t] + wheels + spokes + [cab] + tC + incl, t_c - 0.3, None, 0.5)
        dxm = 3.4
        t_m0, t_m1 = t_c + 0.8, t_c + 7.0
        st.move([body_t] + wheels + spokes, t_m0, t_m1, dx=dxm)
        st.scale_to(cab, t_m0, t_m1, sx=tr_x + dxm - 0.8 - x0 + 0.0)
        st.rotate(spokes, t_m0, t_m1, 360 * 3)
        pt = K.note(st, "wheels grip the wall and drive the string along,\npowered through the cable", 3.9, -1.9, 0.21, P.TEXT, align="c")
        K.show(st, pt, t_c + 1.0, None, 0.5)
        # ---------- the end of the wire's reach
        t2 = s[2]
        t3 = s[3]
        end = K.note(st, "beyond the tractor's reach, in long horizontal wells:", 0.0, -3.0, 0.26, P.MUTED, align="c")
        K.show(st, end, t2, None, 0.5)
        pipe = K.tag(st, 0.0, -3.55, "a pipe that can be pushed  →", color=P.WARN, fg=P.BG, size=0.32, z=1.0)
        K.show(st, pipe, t3, None, 0.5)


# ====================================================================================================== 4.10
def b410(st, tl):
    b = tl["4.10"]
    s = b.sent
    with st.span(b.start, b.end):
        rows = ["slickline", "braided line", "electric line"]
        cols = ["CARRY / PLACE", "PULL / HAMMER", "PUMP", "PUSH", "ROTATE", "POWER / DATA", "STAY LIVE"]
        mx = K.matrix(st, -7.2, 1.9, 1.35, 0.85, rows, cols, row_label_w=2.6, row_size=0.25, head_size=0.17)
        st.fade_in(mx.frame + mx.heads + mx.rowlabels, b.start + 0.2, 0.6)
        marks = {0: ["full", "full", "none", "part", "none", "none", "full"],
                 1: ["full", "full", "none", "part", "none", "none", "full"],
                 2: ["full", "part", "none", "part", "none", "full", "full"]}
        for r in range(3):
            for c in range(7):
                if c in (2, 3, 4):
                    continue
                K.mark(st, mx.cells[(r, c)], marks[r][c], s[0] + 0.3 * r + 0.1 * c, size=0.2)
        # strength and gravity
        t1, t2, t3 = s[1], s[2], s[3]
        br = K.tag(st, -2.3, -1.15, "strength: a few tonnes at the very most", color=P.WARN, fg=P.BG, size=0.23, z=0.9)
        K.show(st, br, t1, None, 0.4)
        gr = K.tag(st, -2.3, -1.85, "gravity: tools stop falling as the well leans over", color=P.WARN, fg=P.BG, size=0.23, z=0.9)
        K.show(st, gr, t2, None, 0.4)
        for r in range(3):
            for c in (2, 3, 4):
                K.mark(st, mx.cells[(r, c)], "none", t3 + 0.3 * r + 0.1 * c, size=0.2)
        # the pump and push columns glow
        x_p = mx.cells[(0, 2)][0]
        x_q = mx.cells[(0, 3)][0]
        gl = st.rect((x_p + x_q) / 2, 1.9 - 1.3, 2.9, 3.0, P.BAD, 0.3, alpha=0.18, role="flat")
        K.show(st, gl, t3, None, 0.4)
        nx = K.tag(st, -2.3, -2.7, "when a job needs those: the next method", color=P.SAFE, fg=P.BG, size=0.26, z=0.9)
        K.show(st, nx, s[4], None, 0.5)
        # a short legend for the partial mark
        lg = K.note(st, "●  partial     ✓  yes     ✕  no", 3.2, -2.9, 0.19, P.MUTED, align="c")
        K.show(st, lg, s[0] + 1.0, None, 0.4)


def build(st, tl):
    b408(st, tl)
    b409(st, tl)
    b410(st, tl)
