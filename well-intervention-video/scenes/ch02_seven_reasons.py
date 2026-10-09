"""Ch 2: Seven reasons to go back in.

2.01 the seven reasons as chips, each with a marker in the well; three questions to ask of each
2.02 SEE      pressure build-up gauge, production log (spinner), caliper
2.03 SECURE   two barrier envelopes, a leak, annulus pressure, three ways to restore the barrier
2.04 CLEAR    scale, wax, hydrate, sand fill narrow the bore; the cures; a fish
2.05 STIMULATE damage around a perforation dissolved by acid; more perforations, a fracture
2.06 LIFT     gas lift valves; liquid loading and the velocity string
2.07 STEER    water breakthrough, water cut, shutting a zone off
2.08 FINISH   plugs for abandonment; converting to an injector; a side-track
2.09 the capabilities these jobs need, as a matrix
"""
from __future__ import annotations
import math

from scenes.common import palette as P, model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common import kit as K
from scenes.common import insets as I

TITLE = "Seven reasons to go back in"

REASONS = [("SEE", "look inside"), ("SECURE", "keep two barriers"), ("CLEAR", "remove what blocks"), ("STIMULATE", "improve the inflow"),
           ("LIFT", "help it flow"), ("STEER", "control what it makes"), ("FINISH", "end or change the well")]


def reason_head(st, n, t0, t1=None):
    """Top-left badge for reason n (1..7): number orb, the word, and a row of seven progress dots."""
    word, sub = REASONS[n - 1]
    orb = st.circle(-7.35, 3.4, 0.27, P.PORE, 0.8)
    num = st.text(str(n), -7.35, 3.395, 0.3, P.BG, 0.81, kind="bold")
    w = st.text(word, -6.95, 3.43, 0.42, P.TEXT, 0.8, align="l", kind="bold")
    sb = st.text(sub, -6.95, 3.04, 0.2, P.MUTED, 0.8, align="l")
    dots = []
    for i in range(7):
        col = P.PORE if i == n - 1 else (P.SAFE if i < n - 1 else P.GRID)
        dots.append(st.circle(-7.35 + i * 0.26, 2.68, 0.07 if i != n - 1 else 0.09, col, 0.8, role="disc"))
    allp = [orb, num, w, sb] + dots
    K.show(st, allp, t0, t1, 0.45)
    return allp


def _well(st, cx, y_top=2.35, scale=0.85, rock_w=1.35, perfs=True, mandrels=True, extras=True):
    w = K.Well(st, cx=cx, y_top=y_top, scale=scale, rock_w=rock_w)
    base = w.rock() + w.reservoir(3820, 4200) + w.cement() + w.casing() + w.tubing(bore_alpha=0.0) + w.seabed() + w.tree()
    w.packer()
    w.dhsv()
    base += w.parts["packer"] + w.parts["dhsv"].body + w.parts["dhsv"].flapper + w.parts["dhsv"].ctrl
    if mandrels:
        for md in M.GL_MANDRELS:
            m = w.mandrel(md)
            base += m.body + m.valve
    if extras:
        sl = w.sleeve()
        nip = w.nipple()
        base += sl.body + nip
    if perfs:
        base += w.perfs(n=5)
    oil = st.rect(w.cx, (w.y(0) + w.y(3800)) / 2, w.TUB_OD - 2 * w.TUB_WALL, w.y(0) - w.y(3800), P.OIL, 0.17, alpha=0.7)
    base.append(oil)
    w.base = base
    w.oil = oil
    return w


# ====================================================================================================== 2.01
def b201(st, tl):
    b = tl["2.01"]
    s = b.sent
    with st.span(b.start, b.end):
        w = _well(st, 1.0, y_top=2.3, scale=0.85, rock_w=1.7)
        st.flow([(w.cx, w.y(3800)), (w.cx, w.y(0) + 0.1)], b.start, b.end - 0.3, P.OIL, n=9, speed=0.6, r=0.035)
        # chips
        needles = ["to see", "to secure", "to clear", "to stimulate", "to lift", "to steer", "to finish"]
        chips = []
        for i, (word, sub) in enumerate(REASONS):
            y = 2.85 - i * 0.82
            t = b.word(1, needles[i])
            plate = st.rect(-5.2, y, 3.6, 0.62, P.PANEL2, 0.5, role="pill")
            orb = st.circle(-6.7, y, 0.2, P.PORE, 0.6)
            num = st.text(str(i + 1), -6.7, y - 0.005, 0.22, P.BG, 0.61, kind="bold")
            txt = st.text(word, -6.35, y, 0.26, P.TEXT, 0.6, align="l", kind="bold")
            st.fade_in([plate, orb, num, txt], t - 0.1, 0.35)
            chips.append((plate, orb, num, txt))
        # markers in the well, same numbers
        mk = [(1, 3700, 1), (2, 900, -1), (3, 2900, 1), (4, 4000, -1), (5, 2100, 1), (6, 3550, -1), (7, 1400, 1)]
        for n, md, side in mk:
            x = w.cx + side * 1.15
            y = w.y(md)
            lead = st.line([(w.cx + side * 0.3, y), (x - side * 0.17, y)], P.MUTED, 0.02, 0.8, role="hair")
            g = K.orb_num(st, x, y, n, 0.0, color=P.PORE, r=0.17, z=1.0)
            t = b.word(1, needles[n - 1]) + 0.2
            st.fade_in([lead], t, 0.3)
            for o in g:
                o.windows  # (objects already created inside the span)
            # pop-in numbers are keyed from t=0: re-key to the spoken time
            st.fade_in(g, t, 0.3)
        # three questions
        qs = [("What is wrong?", 3), ("How would we know?", 4), ("What would we do?", 5)]
        for i, (q, si) in enumerate(qs):
            y = 1.85 - i * 0.95
            plate = st.rect(5.0, y, 3.9, 0.7, P.PANEL2, 0.5, role="pill")
            dot = st.circle(3.4, y, 0.1, P.WARN, 0.6)
            t = st.text(q, 3.65, y, 0.27, P.TEXT, 0.6, align="l", kind="bold")
            st.fade_in([plate, dot, t], s[si] - 0.05, 0.4)


# ====================================================================================================== 2.02
def b202(st, tl):
    b = tl["2.02"]
    s = b.sent
    with st.span(b.start, b.end):
        reason_head(st, 1, b.start + 0.2)
        w = _well(st, -4.7, y_top=2.0, scale=0.82, rock_w=1.1, mandrels=False, extras=False)
        st.fade_in(w.base, b.start + 0.1, 0.4)
        # the black box: a cover over the well while we only have two gauges at the surface
        cover = st.rect(w.cx, (w.y_top + w.y_bot) / 2 + 0.4, 3.6, w.y_top - w.y_bot + 1.0, P.BG, 3.0, alpha=0.93, role="flat")
        qm = st.text("?", w.cx, w.y(2000), 1.4, P.WARN, 3.1, kind="bold")
        st.fade_in([cover, qm], s[1] - 0.1, 0.5)
        st.fade_out([cover, qm], s[3] + 0.2, 0.7)
        g1 = K.dial(st, w.cx + 2.3, 2.2, 0.4, s[2], s[2] + 1.0, 180, 70, color=P.PORE)
        g1l = st.text("pressure", w.cx + 2.3, 1.62, 0.19, P.MUTED, 0.8)
        g2 = st.text("1,000", w.cx + 2.3, 1.15, 0.28, P.OIL, 0.8, kind="mono")
        g2l = st.text("m³/d", w.cx + 2.3, 0.82, 0.19, P.MUTED, 0.8)
        st.fade_in(g1 + [g1l, g2, g2l], s[2], 0.5)
        st.fade_out(g1 + [g1l, g2, g2l], s[3] + 0.8, 0.6)
        # instrument going down the well in sentence 3
        tool = st.rect(w.cx, w.y_top + 0.7, 0.12, 0.5, P.WARN, 1.0, role="steel")
        wire = st.rect(w.cx, w.y_top + 1.2, 0.025, 0.5, P.WIRE, 0.95, anchor="t", role="steel")
        st.fade_in([tool, wire], s[3], 0.3)
        y_run = w.y(3850)
        st.move(tool, s[3] + 0.4, s[4] - 0.2, to=(w.cx, y_run))
        st.scale_to(wire, s[3] + 0.4, s[4] - 0.2, sy=w.y_top + 1.2 - y_run - 0.25)

        # -------- panel (a): pressure build-up
        PX, PY = 0.4, -0.35
        t_a0, t_a1 = s[4] - 0.2, s[6] - 0.3
        ch = Chart(st, -1.35, -2.0, 4.3, 3.5, (0, 20), (200, 330))
        fr = ch.frame(xticks=[0, 5, 10, 15, 20], yticks=[200, 250, 300], xlabel="hours after shut-in", ylabel="pressure (bar)", fx="{:.0f}", fy="{:,.0f}", tick_size=0.18)
        ts = [i * 0.5 for i in range(0, 41)]
        pr = [310 - 95 * math.exp(-t / 3.8) for t in ts]
        cur = st.line([ch.pt(t, v) for t, v in zip(ts, pr)], P.PORE, 0.07, 0.4)
        res = st.rect(ch.x + ch.w / 2, ch.Y(310), ch.w, 0.025, P.MUTED, 0.3, alpha=0.8)
        rl = st.text("reservoir pressure", ch.X(20) - 0.1, ch.Y(310) + 0.2, 0.18, P.MUTED, 0.4, align="r")
        shut = K.tag(st, ch.X(2.3), ch.Y(214) - 0.0, "well shut in", color=P.PANEL2, size=0.18, z=0.7)
        pa = fr + [cur, res, rl] + shut
        K.show(st, pa, t_a0, t_a1)
        st.draw_on(cur, t_a0 + 0.6, t_a1 - 0.5, "LINEAR")
        q1 = K.note(st, "how easily the rock gives up its oil", 0.8, -3.05, 0.2, P.TEXT, align="c")
        q2 = K.note(st, "how much damage is near the well", 0.8, -3.4, 0.2, P.MUTED, align="c")
        K.show(st, q1, b.word(5, "how easily"), t_a1)
        K.show(st, q2, b.word(5, "how much damage"), t_a1)

        # -------- panel (b): production log
        t_b0, t_b1 = s[6] - 0.3, s[7] - 0.3
        cx_b = -0.7
        cas = [st.rect(cx_b - 0.5, 0.0, 0.1, 4.5, P.STEEL_DK, 0.3, role="steel"), st.rect(cx_b + 0.5, 0.0, 0.1, 4.5, P.STEEL_DK, 0.3, role="steel"),
               st.rect(cx_b, 0.0, 0.9, 4.5, P.BG, 0.2)]
        zones = [1.45, 0.25, -0.95]
        shares = [(55, P.OIL), (40, P.OIL), (5, P.WATER)]
        pf, flows, bars = [], [], []
        for y, (pct, colr) in zip(zones, shares):
            for sd in (-1, 1):
                pf.append(st.rect(cx_b + sd * 0.82, y, 0.62, 0.07, P.BG, 0.25, role="hole"))
        tool_b = [st.rect(cx_b, 0.0, 0.2, 1.1, P.STEEL, 0.6, role="steel")]
        spin = [st.rect(cx_b, -0.62, 0.55, 0.06, P.WARN, 0.7, role="solid"), st.rect(cx_b, -0.62, 0.06, 0.55, P.WARN, 0.7, role="solid")]
        bb = K.note(st, "spinner", cx_b + 0.55, -0.72, 0.18, P.WARN, align="l")
        group_b = cas + pf + tool_b + spin + bb
        K.show(st, group_b, t_b0, t_b1)
        # tool moves up through the zones; the spinner turns fast in strong inflow
        st.move(tool_b + spin + bb, t_b0 + 0.6, t_b1 - 0.4, dy=2.9)
        for k, sp in enumerate(spin):
            st.rotate(sp, t_b0 + 0.6, t_b1 - 0.4, 360 * 5 + (90 if k else 0))
        # flow contribution bars
        for y, (pct, colr), lab in zip(zones, shares, ("55 %", "40 %", "5 %  watering out")):
            bar = st.rect(0.45, y, 0.03, 0.34, colr, 0.5, anchor="l", role="flat")
            txt = st.text(lab, 0.5, y, 0.21, P.TEXT if colr != P.WATER else P.WATER, 0.6, align="l", kind="bold")
            ti = t_b0 + 1.0 + zones.index(y) * 0.8
            K.show(st, [bar], ti, t_b1)
            st.scale_to(bar, ti, ti + 0.8, sx=pct / 55 * 2.2 + 0.05)
            K.show(st, [txt], ti + 0.6, t_b1)
        pl = K.note(st, "flow past each perforation", cx_b + 1.9, 2.1, 0.2, P.MUTED, align="c")
        K.show(st, pl, t_b0 + 0.2, t_b1)

        # -------- panel (c): caliper
        t_c0, t_c1 = s[7] - 0.3, b.end - 0.5
        cx_c = -0.8
        wl = st.rect(cx_c - 0.55, 0.0, 0.16, 4.4, P.STEEL, 0.3, role="steel")
        wr = st.rect(cx_c + 0.55, 0.0, 0.16, 4.4, P.STEEL, 0.3, role="steel")
        pit = st.poly([(cx_c - 0.47, 0.35), (cx_c - 0.3, 0.0), (cx_c - 0.47, -0.35)], P.BAD, 0.35, role="flat")
        body = st.rect(cx_c, -0.2, 0.24, 1.0, P.STEEL, 0.6, role="steel")
        arms = [st.line([(cx_c - 0.12, y0), (cx_c - 0.5, y0 + 0.2)], P.WARN, 0.03, 0.62, role="hair") for y0 in (0.1, -0.1)] + \
               [st.line([(cx_c + 0.12, y0), (cx_c + 0.5, y0 + 0.2)], P.WARN, 0.03, 0.62, role="hair") for y0 in (0.1, -0.1)]
        # wall-thickness trace to the right
        tr = Chart(st, 1.0, -2.0, 1.6, 4.0, (3, 10), (0, 4.0), invert_y=True)
        trace_pts = []
        for i in range(61):
            yv = i / 60 * 4.0
            thick = 9.0 - (3.4 * math.exp(-((yv - 2.0) / 0.28) ** 2) if True else 0)
            trace_pts.append(tr.pt(thick, yv))
        trace = st.line(trace_pts, P.WARN, 0.05, 0.5)
        tt = st.text("wall thickness", 1.8, 2.35, 0.19, P.MUTED, 0.5)
        pit_l = K.tag(st, -2.4, 0.45, "corrosion pit", color=P.BAD, fg=P.BG, size=0.19, z=0.8)
        grp = [wl, wr, pit, body, tt, trace] + arms + pit_l
        K.show(st, grp, t_c0, t_c1)
        st.move([body] + arms, t_c0 + 0.5, t_c1 - 0.6, dy=1.5)
        st.draw_on(trace, t_c0 + 0.6, t_c1 - 0.5, "LINEAR")
        end = K.note(st, "nearly every other job starts with one of these", 1.6, -3.25, 0.22, P.TEXT, align="c")
        st.fade_in(end, s[8], 0.5)


# ====================================================================================================== 2.03
def b203(st, tl):
    b = tl["2.03"]
    s = b.sent
    with st.span(b.start, b.end):
        reason_head(st, 2, b.start + 0.2)
        w = _well(st, -3.6, y_top=2.05, scale=0.8, rock_w=1.3, mandrels=False, extras=False)
        st.fade_in(w.base, b.start + 0.1, 0.4)
        st.flow([(w.cx, w.y(3800)), (w.cx, w.y(0) + 0.1)], b.start, b.end - 0.3, P.OIL, n=9, speed=0.6, r=0.035)
        # barrier envelopes (outline only): primary blue around tubing, packer and valve; secondary red around casing and tree
        yt, yp = w.y(0) + 0.05, w.y(M.PACKER_MD) - 0.25
        prim = st.line([(w.cx - 0.52, yt), (w.cx + 0.52, yt), (w.cx + 0.52, yp), (w.cx - 0.52, yp)], P.PRIMARY_B, 0.05, 0.9, closed=True)
        ys = w.y_top + 1.15
        yc = w.y(3820)
        sec = st.line([(w.cx - 0.78, ys), (w.cx + 0.78, ys), (w.cx + 0.78, yc), (w.cx - 0.78, yc)], P.SECOND_B, 0.05, 0.85, closed=True)
        t_b = b.word(1, "two independent barriers")
        st.draw_on(prim, t_b, t_b + 1.2, "BEZIER")
        st.draw_on(sec, t_b + 0.6, t_b + 1.8, "BEZIER")
        lp = K.callout(st, "primary barrier: tubing, packer, valve", -1.9, w.y(1100), w.cx + 0.52, w.y(1100), color=P.PRIMARY_B, fg=P.BG, size=0.19)
        ls = K.callout(st, "secondary barrier: casing, tree", -1.9, w.y(2300), w.cx + 0.78, w.y(2300), color=P.SECOND_B, fg=P.BG, size=0.19)
        K.show(st, lp, t_b + 0.8, s[2])
        K.show(st, ls, t_b + 1.4, s[2])
        # failures, each as the sentence says it
        t3, t4, t5 = s[3], s[4], s[5]
        hole = st.circle(w.cx - 0.2, w.y(1700), 0.0001, P.BAD, 0.95)
        st.scale_to(hole, t3 + 0.2, t3 + 1.4, sx=0.11, sy=0.11)
        l3 = K.callout(st, "corrosion", -1.9, w.y(1700), w.cx - 0.12, w.y(1700), color=P.PANEL2, size=0.19)
        K.show(st, l3, t3, s[6])
        leak_pk = st.flow([(w.cx - 0.1, w.y(M.PACKER_MD) + 0.15), (w.cx - 0.4, w.y(M.PACKER_MD) - 0.1)], t4 + 0.3, s[8] - 0.6, P.OIL, n=3, speed=0.3, r=0.04)
        l4 = K.callout(st, "packer seal leaks", -1.9, w.y(M.PACKER_MD) + 0.05, w.cx + 0.4, w.y(M.PACKER_MD) + 0.05, color=P.PANEL2, size=0.19)
        K.show(st, l4, t4, s[6])
        xm = K.xmark(st, w.cx, w.y(M.DHSV_MD), 0.3, t5 + 0.6)
        l5 = K.callout(st, "valve fails its test", -1.9, w.y(M.DHSV_MD), w.cx + 0.4, w.y(M.DHSV_MD), color=P.PANEL2, size=0.19)
        K.show(st, l5, t5, s[6])
        # pressure appears in the annulus
        ann = w.fill("annulus", P.OIL, 0, 1700, z=0.12, alpha=0.0) if False else None
        sprays = st.flow([(w.cx - 0.2, w.y(1700)), (w.cx - 0.45, w.y(1700))], t3 + 1.2, s[8] - 0.4, P.OIL, n=4, speed=0.3, r=0.04)
        ag = K.dial(st, 1.9, 2.15, 0.5, s[6] + 0.2, s[6] + 2.0, 210, 70, color=P.BAD)
        agt = st.counter(1.9, 1.35, s[6] + 0.2, s[6] + 2.0, 0, 40, "{:.0f} bar", 0.28, P.BAD, 0.8, hold=s[8] - 0.4)
        agl = st.text("annulus pressure", 1.9, 1.0, 0.2, P.MUTED, 0.8)
        K.show(st, ag + [agl], s[6], s[8] - 0.4)
        # a note with the rule
        rule = K.note(st, "a failed barrier must be understood and dealt with,\nor the well must be shut in", 1.9, 0.0, 0.2, P.TEXT, align="c")
        K.show(st, rule, s[7], s[8] - 0.4)
        # the three fixes cycle in the leak region (sentence 8)
        t_f = s[8]
        fix_names = ["plug set below the leak", "patch across the leak", "replacement valve"]
        x_fix = 2.3
        fixes = []
        for i, nm in enumerate(fix_names):
            y = 2.05 - i * 0.82
            ti = b.word(8, ["a plug", "a patch", "a replacement"][i])
            pl = K.tag(st, x_fix, y, nm, color=P.SAFE, fg=P.BG, size=0.2, z=0.8)
            K.show(st, pl, ti - 0.2, None, 0.35)
            fixes.append(pl)
        # the visual fixes at the leak point: patch (a sleeve over the hole), then everything turns green
        patch = st.rect(w.cx, w.y(1700), 0.6, 0.5, P.SAFE, 1.0, alpha=0.6, role="flat")
        st.fade_in(patch, b.word(8, "a patch"), 0.5)
        okring = st.line([(w.cx - 0.52, yt), (w.cx + 0.52, yt), (w.cx + 0.52, yp), (w.cx - 0.52, yp)], P.SAFE, 0.05, 0.95, closed=True)
        st.fade_in(okring, b.word(8, "a replacement") + 0.6, 0.5)
        st.draw_on(okring, b.word(8, "a replacement") + 0.4, b.word(8, "a replacement") + 1.4, "BEZIER")


# ====================================================================================================== 2.04
def b204(st, tl):
    b = tl["2.04"]
    s = b.sent
    with st.span(b.start, b.end):
        reason_head(st, 3, b.start + 0.2)
        # long section of tubing (left) with deposits growing on the walls
        cx = -4.3
        top, bot = 2.2, -3.1
        walls = [st.rect(cx - 0.85, (top + bot) / 2, 0.16, top - bot, P.STEEL, 0.3, role="steel"),
                 st.rect(cx + 0.85, (top + bot) / 2, 0.16, top - bot, P.STEEL, 0.3, role="steel"),
                 st.rect(cx, (top + bot) / 2, 1.54, top - bot, P.OIL, 0.15, alpha=0.35)]
        st.fade_in(walls, b.start + 0.1, 0.4)
        perf = [st.rect(cx - 1.25, -2.55, 0.7, 0.08, P.BG, 0.2, role="hole"), st.rect(cx + 1.25, -2.55, 0.7, 0.08, P.BG, 0.2, role="hole"),
                st.rect(cx - 1.25, -2.85, 0.7, 0.08, P.BG, 0.2, role="hole"), st.rect(cx + 1.25, -2.85, 0.7, 0.08, P.BG, 0.2, role="hole")]
        st.fade_in(perf, b.start + 0.1, 0.4)
        st.flow([(cx, bot + 0.1), (cx, top - 0.1)], b.start, b.end - 0.3, P.OIL, n=10, speed=0.55, r=0.04, jitter=0.4)

        def deposit(y0, y1, color, t0, t1, thick=0.0, z=0.35):
            h = abs(y1 - y0)
            out = []
            for sd in (-1, 1):
                r = st.rect(cx + sd * 0.77, (y0 + y1) / 2, 0.0001, h, color, z, role="flat")
                st.scale_to(r, t0, t1, sx=thick)
                st.move(r, t0, t1, dx=-sd * thick / 2)
                out.append(r)
            return out
        d_scale = deposit(1.8, 0.6, P.SCALE, s[1] + 1.0, s[1] + 3.0, 0.4)
        d_wax = deposit(2.15, 1.55, P.WAX, s[2] + 0.2, s[2] + 2.0, 0.34)
        d_hyd = deposit(-0.1, -1.1, P.HYDRATE, s[3] + 0.5, s[3] + 2.5, 0.46)
        sand = st.rect(cx, bot, 1.54, 0.0001, P.SAND, 0.36, anchor="b")
        st.scale_to(sand, s[4], s[4] + 2.0, sy=1.0)
        lx = cx + 1.2
        labs = [K.tag(st, lx, 1.2, "scale", color=P.SCALE, fg=P.BG, size=0.2, z=0.9, align="l"), K.tag(st, lx, 1.9, "wax", color=P.WAX, fg=P.BG, size=0.2, z=0.9, align="l"),
                K.tag(st, lx, -0.6, "hydrate", color=P.HYDRATE, fg=P.BG, size=0.2, z=0.9, align="l"), K.tag(st, lx, -2.2, "sand fill", color=P.SAND, fg=P.BG, size=0.2, z=0.9, align="l")]
        for lab, t in zip(labs, [b.word(1, "Scale") + 0.4, b.word(2, "Wax") + 0.2, b.word(3, "Hydrates") + 0.2, b.word(4, "Sand") + 0.2]):
            K.show(st, lab, t, None, 0.35)
        chem = K.note(st, "Ba²⁺ + SO₄²⁻  →  BaSO₄", 1.1, 1.0, 0.24, P.TEXT, align="c", kind="mono")
        chem_t = K.note(st, "injected seawater meets formation water", 1.1, 0.62, 0.18, P.MUTED, align="c")
        K.show(st, chem + chem_t, b.word(1, "barium sulphate"), s[2] - 0.2, 0.4)
        # cross-section: the bore closes as the deposits grow; the rate falls
        ccx, ccy, R = 1.6, 0.2, 1.45
        ring = st.ring(ccx, ccy, R, 0.18, P.STEEL, 0.4)
        solid = st.circle(ccx, ccy, R - 0.18, P.SCALE, 0.35, role="flat")
        open_ = st.circle(ccx, ccy, R - 0.18, P.OIL, 0.45, alpha=0.9, role="flat")
        st.scale_to(open_, s[5] - 0.2, s[5] + 2.2, sx=0.5, sy=0.5)
        cl = K.note(st, "tubing cross-section", ccx, ccy + R + 0.3, 0.2, P.MUTED, align="c")
        rate = st.counter(ccx, ccy - R - 0.45, s[5] - 0.2, s[5] + 2.2, 100, 45, "flow {:.0f} %", 0.3, P.WARN, 0.8, hold=s[6] - 0.2)
        K.show(st, [ring, solid, open_] + cl, s[5] - 0.5, s[6] - 0.2, 0.5)
        # cures
        cures = ["scrape", "jet", "mill", "dissolve", "wash out"]
        for i, c in enumerate(cures):
            x = -0.2 + i * 1.8
            pl = K.tag(st, x, -2.65, c, color=P.SAFE, fg=P.BG, size=0.22, z=0.8)
            t = b.word(6, c.split()[0]) - 0.1
            K.show(st, pl, t, s[7] - 0.2, 0.3)
        # the fish
        fx, fy = 1.4, -0.1
        tool = [st.rect(fx, fy, 0.34, 1.7, P.STEEL, 0.6, role="steel", rot=-18), st.rect(fx - 0.2, fy + 0.8, 0.2, 0.22, P.STEEL_DK, 0.62, role="steel", rot=-18)]
        hook = [st.line([(fx + 1.1, fy + 2.4), (fx + 0.6, fy + 1.4), (fx + 0.28, fy + 1.05)], P.WARN, 0.06, 0.7, role="hair")]
        fl = K.tag(st, fx + 1.5, fy - 0.2, "a fish", color=P.BAD, fg=P.BG, size=0.22, z=0.9)
        K.show(st, tool + fl, s[7], None, 0.5)
        K.show(st, hook, s[8] - 0.2, None, 0.5)
        st.move(hook, s[8] + 0.3, s[8] + 1.6, dx=-0.6, dy=-0.7)
        fi = K.tag(st, fx + 1.5, fy - 0.8, "fishing", color=P.SAFE, fg=P.BG, size=0.22, z=0.9)
        K.show(st, fi, b.word(8, "fishing") - 0.2, None, 0.4)


# ====================================================================================================== 2.05
def b205(st, tl):
    b = tl["2.05"]
    s = b.sent
    with st.span(b.start, b.end):
        reason_head(st, 4, b.start + 0.2)
        SC = 1.5
        pf = I.perf_inset(st, -2.4, -0.45, SC, n=3)
        ys = pf.ys
        base = pf.rock + pf.cement + pf.casing + pf.bore + pf.tunnels
        st.fade_in(base, b.start + 0.1, 0.4)
        import random
        rnd = random.Random(7)
        x0, x1 = pf.x_cem + 0.05, pf.x_end - 0.1
        ytop, ybot = -0.45 + 1.8 * SC - 0.1, -0.45 - 1.8 * SC + 0.1
        pores_open, pores_dead = [], []
        for _ in range(110):
            px, py = rnd.uniform(x0, x1), rnd.uniform(ybot, ytop)
            near = any(abs(py - y) < 0.55 * SC and px < pf.x_cem + 1.45 * SC for y in ys)
            if near:
                pores_dead.append(st.circle(px, py, 0.045, "#2a1d16", 0.3, role="disc"))
            else:
                pores_open.append(st.circle(px, py, 0.045, "#8a6a35", 0.3, role="disc"))
        halos = [st.ellipse(pf.x_cem + 0.7 * SC, y, 0.95 * SC, 0.5 * SC, "#3a2a20", 0.2, alpha=0.8, role="disc") for y in ys]
        K.show(st, halos + pores_dead + pores_open, b.start + 0.2, None, 0.5)
        dmg = K.tag(st, pf.x_cem + 1.9 * SC, ys[0] + 0.62 * SC, "damaged zone", color=P.BAD, fg=P.BG, size=0.19, z=0.9)
        K.show(st, dmg, s[1] + 0.6, s[3] - 0.2, 0.4)
        # thin inflow before the treatment, strong afterwards
        for y in ys:
            st.flow([(pf.x_cem + 1.6 * SC, y), (pf.x_cas[0] - 0.4 * SC, y)], s[2], s[3] + 1.0, P.OIL, n=2, speed=0.25, r=0.04)
        # acid pumped from the bore through the tunnels dissolves the damage
        t_ac = s[3] + 0.3
        for y in ys:
            st.flow([(pf.x_cas[0] - 0.9 * SC, y), (pf.x_cem + 1.2 * SC, y)], t_ac, t_ac + 3.2, P.ACID, n=7, speed=1.0, r=0.06)
        st.fade_out(halos + pores_dead, t_ac + 1.2, 1.8)
        for y in ys:
            st.flow([(pf.x_cem + 1.9 * SC, y), (pf.x_cas[0] - 0.4 * SC, y)], t_ac + 3.3, s[4] + 1.0, P.OIL, n=8, speed=0.9, r=0.05)
        ac = K.tag(st, pf.x_cas[0] - 1.2 * SC, ys[2] + 1.0, "acid", color=P.ACID, fg=P.BG, size=0.2, z=0.9)
        K.show(st, ac, t_ac, t_ac + 3.2, 0.3)
        rate = st.counter(2.35, -0.6, t_ac + 1.2, t_ac + 3.2, 100, 160, "inflow {:.0f} %", 0.3, P.OIL, 0.8, hold=b.end - 0.3)
        rl = st.text("", 1.1, 0.5, 0.2, P.MUTED, 0.8)
        # more perforations, a fracture
        extra = []
        for k, dy in enumerate((-1.45 * SC, 1.45 * SC)):
            y = -0.45 + dy
            extra.append(st.poly([(pf.x_cas[0] - 0.02 * SC, y - 0.1 * SC), (pf.x_cas[0] - 0.02 * SC, y + 0.1 * SC), (pf.x_cem + 1.55 * SC, y + 0.035 * SC),
                                  (pf.x_cem + 1.55 * SC, y - 0.035 * SC)], P.BG, 0.5, role="flat"))
        K.show(st, extra, b.word(4, "more perforations"), None, 0.5)
        fy = -0.45 - 1.45 * SC
        pts = [(pf.x_cem + 1.55 * SC, fy), (pf.x_cem + 1.9 * SC, fy - 0.25), (pf.x_cem + 2.15 * SC, fy - 0.1), (pf.x_cem + 2.5 * SC, fy - 0.45)]
        frac = st.line(pts, P.FRAC, 0.07, 0.6)
        st.draw_on(frac, b.word(4, "hydraulic fracture"), b.word(4, "hydraulic fracture") + 1.0, "BEZIER")
        fl = K.tag(st, pf.x_cem + 2.6 * SC, fy - 0.1, "fracture", color=P.FRAC, fg=P.BG, size=0.19, z=0.9)
        K.show(st, fl, b.word(4, "hydraulic fracture") + 0.4, None, 0.4)
        # placed at a precise depth
        br = st.line([(pf.x_cas[0] - 1.9 * SC, -0.45 + 2.0 * SC - 0.1), (pf.x_cas[0] - 1.9 * SC + 0.15, -0.45 + 2.0 * SC - 0.1), (pf.x_cas[0] - 1.9 * SC + 0.15, -0.45 - 2.0 * SC + 0.1),
                         (pf.x_cas[0] - 1.9 * SC, -0.45 - 2.0 * SC + 0.1)], P.WARN, 0.045, 0.8)
        bt = K.tag(st, pf.x_cas[0] - 1.9 * SC + 0.55, -0.45 - 2.0 * SC - 0.0 + 0.55, "placed at the right depth", color=P.WARN, fg=P.BG, size=0.19, z=0.9, align="l")
        K.show(st, [br] + bt, s[5], None, 0.5)


# ====================================================================================================== 2.06
# 2.06 (gas lift, unloading, liquid loading) lives in scenes/x_ch02_lift.py


# ====================================================================================================== 2.07
def b207(st, tl):
    b = tl["2.07"]
    s = b.sent
    with st.span(b.start, b.end):
        reason_head(st, 6, b.start + 0.2)
        cx = -4.6
        # three sand zones either side of the well, with shale between
        zones = [(1.45, "zone 1"), (0.25, "zone 2"), (-0.95, "zone 3")]
        top, bot = 2.15, -2.35
        shale_l = st.rect(cx - 1.55, (top + bot) / 2, 2.2, top - bot, P.SHALE, 0.0)
        shale_r = st.rect(cx + 1.55, (top + bot) / 2, 2.2, top - bot, P.SHALE, 0.0)
        sands = []
        for y, n in zones:
            sands.append(st.rect(cx - 1.55, y, 2.2, 0.62, P.SAND, 0.05))
            sands.append(st.rect(cx + 1.55, y, 2.2, 0.62, P.SAND, 0.05))
        well = [st.rect(cx - 0.3, (top + bot) / 2, 0.1, top - bot, P.STEEL, 0.3, role="steel"), st.rect(cx + 0.3, (top + bot) / 2, 0.1, top - bot, P.STEEL, 0.3, role="steel"),
                st.rect(cx, (top + bot) / 2, 0.5, top - bot, P.OIL, 0.15, alpha=0.5)]
        perfs = []
        for y, n in zones:
            for sd in (-1, 1):
                perfs.append(st.rect(cx + sd * 0.45, y, 0.35, 0.06, P.BG, 0.35, role="hole"))
        zl = [st.text(n, cx - 1.55, y, 0.19, P.BG, 0.2, kind="bold") for y, n in zones]
        base = [shale_l, shale_r] + sands + well + perfs + zl
        st.fade_in(base, b.start + 0.1, 0.4)
        # water rising in zone 3 (the lowest), from the bottom of the sand, both sides
        wat = []
        for sd in (-1, 1):
            r = st.rect(cx + sd * 1.55, -0.95 - 0.31, 2.2, 0.0001, P.WATER, 0.1, anchor="b", alpha=0.85)
            st.scale_to(r, s[2] + 0.3, s[2] + 3.0, sy=0.62)
            wat.append(r)
        K.show(st, wat, s[2] + 0.2, None, 0.3)
        st.flow([(cx + 1.2, -0.95), (cx + 0.5, -0.95)], s[2] + 1.8, s[4], P.WATER, n=5, speed=0.6, r=0.05)
        st.flow([(cx + 1.2, 1.45), (cx + 0.5, 1.45)], s[1] + 0.5, s[4], P.OIL, n=4, speed=0.6, r=0.05)
        st.flow([(cx + 1.2, 0.25), (cx + 0.5, 0.25)], s[1] + 0.5, s[4], P.OIL, n=4, speed=0.6, r=0.05)
        wl = K.tag(st, cx, -1.75, "water arrives early", color=P.WATER, fg=P.BG, size=0.18, z=0.9)
        K.show(st, wl, s[2] + 0.4, s[4] - 0.3, 0.4)
        # the water cut chart on the right
        ch = Chart(st, -0.3, -2.2, 3.7, 3.9, (0, 14), (0, 100))
        fr = ch.frame(xticks=[0, 4, 8, 12], yticks=[0, 50, 90], xlabel="years", ylabel="water cut (%)", fx="{:.0f}", fy="{:,.0f}", tick_size=0.18)
        K.show(st, fr, s[2] - 0.2, None, 0.5)

        def wc(t, t_fix=9.0):
            if t < t_fix:
                return 3 + 90 * (1 - math.exp(-((t / 8.0) ** 2.2)))
            return 25 + 5 * (t - t_fix)
        ts = [i * 0.25 for i in range(0, 57)]
        pre = [t for t in ts if t <= 9.0]
        post = [t for t in ts if t >= 9.0]
        c1 = st.line([ch.pt(t, wc(t)) for t in pre], P.WATER, 0.07, 0.5)
        c2 = st.line([ch.pt(t, wc(t)) for t in post], P.SAFE, 0.07, 0.5)
        st.draw_on(c1, s[2] + 0.4, s[3] + 2.4, "LINEAR")
        die = st.rect(ch.x + ch.w / 2, ch.Y(90), ch.w, 0.025, P.BAD, 0.4, alpha=0.8)
        dl = st.text("well no longer pays", ch.X(0.3), ch.Y(90) + 0.2, 0.17, P.BAD, 0.5, align="l")
        K.show(st, [die, dl], s[3] + 0.5, None, 0.5)
        # fix: plug below zone 2 (or sleeve closes zone 3), new perforation higher
        t4 = s[4]
        plug = st.rect(cx, -0.45, 0.46, 0.34, P.STEEL, 0.6, role="steel")
        K.show(st, plug, b.word(4, "a plug"), None, 0.4)
        pt = K.tag(st, cx + 1.1, -0.45, "plug", color=P.STEEL, fg=P.BG, size=0.18, z=0.9)
        K.show(st, pt, b.word(4, "a plug"), s[5] - 0.2, 0.4)
        cem = st.rect(cx, -1.0, 0.46, 0.0001, P.CEMENT, 0.5, anchor="b")
        sleeve = st.rect(cx, -0.95, 0.5, 0.2, P.PRIMARY_B, 0.55, role="flat")
        K.show(st, sleeve, b.word(4, "closing a sliding sleeve"), s[5] - 0.2, 0.4)
        newp = []
        for sd in (-1, 1):
            newp.append(st.rect(cx + sd * 0.45, 2.0, 0.35, 0.06, P.BG, 0.35, role="hole"))
        K.show(st, newp, b.word(4, "perhaps open another"), None, 0.5)
        st.draw_on(c2, b.word(4, "perhaps open another") - 0.2, b.word(4, "perhaps open another") + 1.5, "LINEAR")
        st.fade_out(wat, b.word(4, "a plug") + 1.0, 1.0)
        nz = K.tag(st, cx, 2.35, "open a higher zone", color=P.SAFE, fg=P.BG, size=0.18, z=0.9)
        K.show(st, nz, b.word(4, "perhaps open another"), None, 0.4)
        sm = K.note(st, "a few smart wells do this on command", 1.0, 2.7, 0.2, P.MUTED, align="c")
        K.show(st, sm, s[5], None, 0.5)


# ====================================================================================================== 2.08
def b208(st, tl):
    b = tl["2.08"]
    s = b.sent
    with st.span(b.start, b.end):
        reason_head(st, 7, b.start + 0.2)
        w = _well(st, -3.6, y_top=1.85, scale=0.78, rock_w=1.2, mandrels=False, extras=False)
        st.fade_in(w.base, b.start + 0.1, 0.4)
        plugs = [(3550, 3750, "plug 1"), (1900, 2100, "plug 2"), (350, 550, "plug 3")]
        t0 = b.word(1, "permanently plugged")
        for i, (m0, m1, name) in enumerate(plugs):
            y0, y1 = w.y(m0), w.y(m1)
            h = abs(y0 - y1)
            body = st.rect(w.cx, y1, w.TUB_OD + 0.4, 0.0001, P.CEMENT, 0.7, anchor="b")
            st.scale_to(body, t0 + 0.4 + i * 1.2, t0 + 1.6 + i * 1.2, sy=h)
            outl = st.line([(w.cx - 0.43, y1), (w.cx + 0.43, y1), (w.cx + 0.43, y1 + h), (w.cx - 0.43, y1 + h)], P.SAFE, 0.035, 0.8, closed=True)
            st.fade_in(outl, t0 + 1.6 + i * 1.2, 0.4)
        st.fade_out(w.oil, t0 + 0.4, 2.0)
        pl = K.callout(st, "cement plugs: a permanent barrier", -1.6, w.y(2000), w.cx + 0.45, w.y(2000), color=P.SAFE, fg=P.BG, size=0.19)
        K.show(st, pl, t0 + 2.4, None, 0.4)
        steps = ["log it", "clean it out", "cut the pipes"]
        for i, nm in enumerate(steps):
            t = b.word(2, ["logged", "cleaned out", "cut"][i])
            tg = K.tag(st, -1.3, 3.0 - i * 0.6, nm, color=P.PANEL2, size=0.21, z=0.8, align="l")
            K.show(st, tg, t - 0.1, s[3] - 0.2, 0.35)
        nr = K.tag(st, -1.3, 3.0, "some of it with no rig", color=P.SAFE, fg=P.BG, size=0.21, z=0.8, align="l")
        K.show(st, nr, s[3], s[4] - 0.2, 0.4)
        # alternatives to finishing: an injector and a side-track
        t_alt = s[4]
        x1, x2 = 1.5, 5.3
        inj = [st.rect(x1, 0.35, 0.5, 3.2, P.STEEL, 0.4, role="steel"), st.rect(x1, 0.35, 0.3, 3.2, P.WATER, 0.5, alpha=0.9),
               st.rect(x1, -1.65, 2.6, 0.9, P.SAND, 0.1)]
        st.flow([(x1, 1.8), (x1, -1.5), (x1 + 1.1, -1.5)], t_alt + 0.6, b.end - 0.3, P.WATER, n=9, speed=0.8, r=0.05)
        il = K.tag(st, x1, 2.2, "producer  →  water injector", color=P.PANEL2, size=0.2, z=0.9)
        K.show(st, inj + il, b.word(4, "converted"), None, 0.5)
        st_main = [st.rect(x2, 0.35, 0.5, 3.2, P.STEEL, 0.4, role="steel"), st.rect(x2, 0.35, 0.3, 3.2, P.BG, 0.5), st.rect(x2 + 1.2, -1.75, 2.4, 0.9, P.SAND, 0.1)]
        branch = st.line([(x2, -0.2), (x2 + 0.6, -0.8), (x2 + 1.2, -1.4), (x2 + 2.0, -1.7)], P.OIL, 0.12, 0.6)
        sl_ = K.tag(st, x2 + 0.5, 2.2, "side-track into fresh reservoir", color=P.PANEL2, size=0.2, z=0.9)
        K.show(st, st_main + sl_, b.word(4, "side-track"), None, 0.5)
        st.draw_on(branch, b.word(4, "side-track") + 0.5, b.word(4, "side-track") + 2.0, "BEZIER")
        end = K.note(st, "either way: an intervention prepares the ground", 3.3, -3.0, 0.22, P.TEXT, align="c")
        K.show(st, end, s[5], None, 0.5)


# ====================================================================================================== 2.09
def b209(st, tl):
    b = tl["2.09"]
    s = b.sent
    with st.span(b.start, b.end):
        rows = [r[0] for r in REASONS]
        cols = ["CARRY / PLACE", "PULL / HAMMER", "PUMP", "PUSH", "ROTATE", "POWER / DATA"]
        mx = K.matrix(st, -5.9, 2.35, 1.5, 0.6, rows, cols, row_label_w=2.2, row_size=0.21, head_size=0.17)
        st.fade_in(mx.frame, b.start + 0.1, 0.5)
        uses = {0: [0, 5], 1: [0, 1], 2: [1, 2, 3, 4], 3: [0, 2], 4: [0, 1, 3], 5: [0, 1, 2, 5], 6: [0, 1, 2, 4, 5]}
        sent_of_row = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7}
        # headers
        st.fade_in(mx.heads, s[7] - 0.4, 0.5)
        for r in range(7):
            t = s[sent_of_row[r]] if r < 6 else s[7] + 1.0
            lab = mx.rowlabels[r]
            st.fade_in(lab, t, 0.4)
            for k, c in enumerate(uses[r]):
                x, y = mx.cells[(r, c)]
                d = st.circle(x, y, 0.15, P.PORE, 0.8)
                st.pop_in(d, t + 0.5 + 0.15 * k, 0.3)
        # the capability list is read out in sentence 7: head labels light up in turn
        keys = ["carry and place", "pull and hammer", "pump", "push", "rotate", "send power"]
        for c, key in enumerate(keys):
            t = b.word(7, key)
            st.recolor(mx.heads[c], t, t + 0.3, P.WARN)
        # closing line
        bl = st.rect(-0.3, -2.45, 11.6, 0.03, P.PORE, 0.6, alpha=0.0)
        end = K.note(st, "every method is a different bundle of these", 0.8, -2.45, 0.3, P.TEXT, align="c", kind="bold")
        K.show(st, end, s[8], None, 0.5)
        nxt = K.note(st, "next: the bundles", 0.8, -3.0, 0.22, P.MUTED, align="c")
        K.show(st, nxt, s[9], None, 0.5)


# ====================================================================================================== build
def build(st, tl):
    F.header(st, tl)
    b201(st, tl)
    b202(st, tl)
    b203(st, tl)
    b204(st, tl)
    b205(st, tl)
    from scenes.x_ch02_lift import b206
    b206(st, tl, reason_head)
    b207(st, tl)
    b208(st, tl)
    b209(st, tl)
