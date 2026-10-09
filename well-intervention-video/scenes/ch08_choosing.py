"""Ch 8: Choosing a method, and closing the well.

8.01 the capability matrix: six methods against seven capabilities and a cost ordering; "take the lightest row that has every column you need"
8.02 three worked cases: a failed gas-lift valve (wireline), scale in a 55 degree well (coiled tubing), a tubing leak (patch, or a rig)
8.03 the edges are moving: tractors, instrumented coiled tubing, vessels; the three timeless principles
8.04 the seven reasons and the method ladder meet at the well; the closing card with the disclaimers
"""
from __future__ import annotations
import math

from scenes.common import palette as P, model as M, furniture as F
from scenes.common import kit as K
from scenes.common import insets as I
from scenes.common.look import wrap_to
from scenes.common.ct import arc_pts
from scenes.ch02_seven_reasons import _well, REASONS

TITLE = "Choosing a method, and closing the well"

C_SLICK, C_ELINE, C_CT, C_SNUB, C_RIG = P.WIRE, P.COPPER, P.PORE, P.WARN, P.BAD
COST_COL = ["#2a9d8f", "#6fb06a", P.WARN, "#ff8a5c", P.BAD]


def fact(st, x, y, label, text, t, color=P.PORE, size=0.23, w=4.2, z=0.9, t1=None):
    """A labelled statement: small coloured caps label over wrapped text. Returns (objects, height used)."""
    body = wrap_to(text, size, w)
    lab = st.text(label, x, y, 0.16, color, z, align="l", kind="bold")
    tx = st.text(body, x, y - 0.2, size, P.TEXT, z, align="l", valign="t")
    K.show(st, [lab, tx], t, t1, 0.4)
    return [lab, tx], 0.2 + 0.33 * (body.count("\n") + 1) + 0.28


# ====================================================================================================== 8.01
ROWS = ["SLICKLINE", "BRAIDED LINE", "ELECTRIC LINE", "COILED TUBING", "SNUBBING UNIT", "DRILLING RIG"]
COLS = ["CARRY", "PULL /\nHAMMER", "PUMP", "PUSH", "ROTATE", "POWER /\nDATA", "STAY\nLIVE", "RELATIVE\nCOST"]
#            carry pull pump push rotate power live      F full, P partial, N none
CAP = ["FFNNNNF", "FFNNNNF", "FPNNNFF", "FPFFPPF", "FFFFFNF", "FFFFFPN"]
COST = [1, 1, 2, 3, 4, 5]


def b801(st, tl):
    b = tl["8.01"]
    s = b.sent
    with st.span(b.start, b.end):
        x0, y0, cw, rh, lw = -7.75, 2.55, 0.98, 0.66, 2.2
        mx = K.matrix(st, x0, y0, cw, rh, ROWS, COLS, row_label_w=lw, row_size=0.2, head_size=0.16)
        st.fade_in(mx.frame, s[1], 0.5)
        st.fade_in(mx.heads, s[1] + 0.2, 0.5)
        xc = lambda c: x0 + lw + c * cw + cw / 2
        yr = lambda r: y0 - r * rh - rh / 2
        # legend
        ly = y0 - 6 * rh - 0.32
        leg = []
        leg += K.mark(st, (-5.2, ly), "full", s[1] + 0.4, size=0.14, z=0.8) + [st.text("does it well", -4.95, ly, 0.16, P.MUTED, 0.8, align="l")]
        leg += K.mark(st, (-3.4, ly), "part", s[1] + 0.6, size=0.14, z=0.8) + [st.text("limited", -3.2, ly, 0.16, P.MUTED, 0.8, align="l")]
        leg += K.mark(st, (-2.0, ly), "none", s[1] + 0.8, size=0.14, z=0.8) + [st.text("cannot", -1.8, ly, 0.16, P.MUTED, 0.8, align="l")]
        # row highlight and column highlight bars
        def rowbar(r0, r1, t0, t1, color):
            h = (r1 - r0 + 1) * rh
            o = st.rect((x0 + 2.29) / 2, y0 - (r0 + (r1 - r0 + 1) / 2) * rh, 2.29 - x0, h - 0.04, color, 0.45, alpha=0.18)
            K.show(st, [o], t0, t1, 0.35)
            return o

        def colbars(cs, t0, t1):
            for c in cs:
                o = st.rect(xc(c), y0 - 3 * rh, cw - 0.06, 6 * rh, P.PORE, 0.44, alpha=0.14)
                K.show(st, [o], t0, t1, 0.35)
                st.recolor(mx.heads[c], t0, t0 + 0.3, P.WARN)
                st.recolor(mx.heads[c], t1, t1 + 0.3, P.MUTED)

        def fill_row(r, t, color):
            K.show(st, [mx.rowlabels[r]], t, None, 0.4)
            for c, k in enumerate(CAP[r]):
                kind = {"F": "full", "P": "part", "N": "none"}[k]
                K.mark(st, mx.cells[(r, c)], kind, t + 0.25 + 0.12 * c, size=0.17)
            x, y = mx.cells[(r, 7)]
            n = COST[r]
            tx = st.text("$" * n, x, y, 0.22, COST_COL[n - 1], 0.8, kind="bold")
            st.fade_in(tx, t + 0.25 + 0.12 * 7, 0.4)

        # right-hand list: what the job needs -> which method
        px, py, dy = 3.05, 2.95, 0.92
        K.show(st, [st.text("WHAT THE JOB NEEDS", px, 3.3, 0.16, P.MUTED, 0.9, align="l", kind="bold")], s[1] + 0.2, s[12] - 0.2, 0.4)
        needs = [("carry and hammer", "SLICKLINE", C_SLICK, 2, 3), ("real-time data, power, perforating", "ELECTRIC LINE", C_ELINE, 4, 5),
                 ("pumping, pushing, circulating, milling", "COILED TUBING", C_CT, 6, 7), ("rotation and heavy loads in a live well", "SNUBBING", C_SNUB, 8, 9),
                 ("the tubing itself has to come out", "DRILLING RIG", C_RIG, 10, 11)]
        for i, (need, meth, colr, sq, sa) in enumerate(needs):
            y = py - i * dy
            bar = st.rect(px - 0.18, y - 0.18, 0.07, 0.72, colr, 0.9)
            q = st.text(wrap_to(need, 0.2, 4.4), px, y, 0.2, P.MUTED, 0.9, align="l", valign="c")
            a = st.text(meth, px, y - 0.38, 0.3, colr, 0.9, align="l", kind="bold")
            K.show(st, [bar, q], s[sq], s[12] - 0.2, 0.4)
            K.show(st, [a], s[sa], s[12] - 0.2, 0.4)
        # sentence 2/3: carry and hammer -> slickline (and braided line, the same family)
        colbars([0, 1], s[2], s[3] + 1.6)
        rb = rowbar(0, 1, s[3], s[4] - 0.1, C_SLICK)
        fill_row(0, s[3] + 0.1, C_SLICK)
        fill_row(1, s[3] + 1.2, C_SLICK)
        # sentence 4/5: data, power -> electric line
        colbars([5], s[4], s[5] + 2.2)
        rowbar(2, 2, s[5], s[6] - 0.1, C_ELINE)
        fill_row(2, s[5] + 0.1, C_ELINE)
        # sentence 6/7: pumping, pushing -> coiled tubing
        colbars([2, 3], s[6], s[7] + 2.6)
        rowbar(3, 3, s[7], s[8] - 0.1, C_CT)
        fill_row(3, s[7] + 0.1, C_CT)
        # sentence 8/9: rotation and heavy loads, live well -> snubbing
        colbars([4, 6], s[8], s[9] + 2.6)
        rowbar(4, 4, s[9], s[10] - 0.1, C_SNUB)
        fill_row(4, s[9] + 0.1, C_SNUB)
        # sentence 10/11: the tubing has to come out -> a rig (and the well is no longer live)
        rowbar(5, 5, s[11], s[12] - 0.1, C_RIG)
        fill_row(5, s[11] + 0.1, C_RIG)
        K.show(st, leg, s[1] + 0.3, None, 0.5)
        # sentence 12: the lightest method that can do the job
        ar = st.arrow(2.6, y0 - 0.1, 2.6, y0 - 6 * rh + 0.1, P.WARN, 0.07, 0.26, 0.8)
        lt = st.text("lighter", 2.82, y0 - 0.1, 0.22, P.TEXT, 0.9, align="l", kind="bold")
        hv = st.text("heavier", 2.82, y0 - 6 * rh + 0.1, 0.22, P.TEXT, 0.9, align="l", kind="bold")
        K.show(st, [ar, lt, hv], s[12], None, 0.5)
        notes = [("cheaper", "cheaper"), ("faster", "faster"), ("keeps the well live", "live")]
        for i, (txt, key) in enumerate(notes):
            y = 2.0 - i * 0.75
            t = b.word(12, key)
            tx = st.text(txt, 3.9, y, 0.3, P.TEXT, 0.9, align="l", kind="bold")
            K.show(st, [tx] + K.check(st, 3.55, y, t + 0.1, s=0.15), t - 0.1, None, 0.3)
        st.recolor(mx.heads[7], b.word(12, "cheaper"), b.word(12, "cheaper") + 0.3, P.WARN)
        st.recolor(mx.heads[6], b.word(12, "live"), b.word(12, "live") + 0.3, P.WARN)
        rule = K.card(st, -2.73, -2.75, 9.9, 0.8, P.PANEL2, 0.4)
        rt = st.text("TAKE THE LIGHTEST ROW THAT HAS EVERY COLUMN YOU NEED", -2.73, -2.75, 0.23, P.WARN, 0.9, kind="bold")
        K.show(st, rule + [rt], s[12] + 0.3, None, 0.5)
        K.show(st, K.note(st, "ticks are qualitative; real limits depend on equipment size", -2.73, -3.4, 0.17, P.MUTED, align="c"), s[12] + 0.6, None, 0.5)


# ====================================================================================================== 8.02
def slant(p0, ang, a, o=0.0):
    r = math.radians(ang)
    return (p0[0] + a * math.cos(r) - o * math.sin(r), p0[1] + a * math.sin(r) + o * math.cos(r))


def b802(st, tl):
    b = tl["8.02"]
    s = b.sent
    with st.span(b.start, b.end):
        w = _well(st, -5.9, y_top=2.55, scale=0.8, rock_w=0.9)
        K.show(st, w.base, b.start + 0.1, None, 0.6)
        # case tabs
        tabs = [("A  FAILED GAS-LIFT VALVE", -2.3, s[1], s[4]), ("B  SCALE, 55° WELL", 1.5, s[4], s[7]), ("C  TUBING LEAK", 4.7, s[7], b.end)]
        for text, x, ta, tb in tabs:
            base = K.tag(st, x, 3.4, text, color=P.PANEL2, fg=P.MUTED, size=0.19, align="l", z=0.9)
            K.show(st, base, s[0] + 0.3, None, 0.5)
            on = K.tag(st, x, 3.4, text, color=P.PORE, fg=P.BG, size=0.19, align="l", z=1.0)
            K.show(st, on, ta, tb - 0.3 if tb < b.end else None, 0.35)
        lx, y_top = -2.3, 2.75
        wtop = w.y(0) + 0.1
        # -------------------------------------------------------------------------- case A: a failed gas-lift valve, slickline
        tA = s[4] - 0.4
        mxy = w.y(2100)
        st.ripple(w.cx + 0.17, mxy, s[1] + 0.8, tA, P.BAD)
        K.show(st, K.callout(st, "valve fails", -4.15, mxy + 0.55, w.cx + 0.2, mxy + 0.05, size=0.17, align="l"), s[1] + 0.8, tA, 0.4)
        y = y_top
        _, h = fact(st, lx, y, "WRONG", "A gas-lift valve in its pocket at 2,100 m MD has failed.", s[1] + 0.5, P.BAD, t1=tA); y -= h
        _, h = fact(st, lx, y, "NEEDS", "Carry a tool down, latch the valve, pull it, set a new one.", s[2] - 0.4, P.PORE, t1=tA); y -= h
        _, h = fact(st, lx, y, "METHOD", "Slickline with a kick-over tool: one trip to pull, one to set.", s[2] + 0.4, C_SLICK, t1=tA); y -= h
        _, h = fact(st, lx, y, "RESULT", "Production back within a day or two.", s[3], P.SAFE, t1=tA)
        # the toolstring runs down the well to the mandrel
        wire = st.rect(w.cx, wtop, 0.03, 0.001, P.WIRE, 0.9, anchor="t")
        st.scale_to(wire, s[2] - 0.6, s[2] + 1.6, sy=wtop - (mxy + 0.45))
        tool = st.rect(w.cx, mxy + 0.3, 0.12, 0.34, P.WARN, 0.92, role="solid")
        K.show(st, [wire], s[2] - 0.6, tA, 0.2)
        K.show(st, [tool], s[2] + 1.4, tA, 0.3)
        st.flow([(w.cx, w.y(3800)), (w.cx, wtop)], s[3] + 0.5, tA, P.OIL, n=9, speed=0.6, r=0.035)
        # detail: side-pocket mandrel; trip 1 pulls the failed valve, trip 2 sets a new one (procedural, as in 4.06)
        from scenes.common import gaslift as G, pdraw as PD
        g = G.SPM(4.0, 3.0, -3.1, s=0.72)
        t0 = s[2] - 0.6
        T1 = (t0, t0 + 4.2)                     # trip 1
        T2 = (t0 + 4.6, t0 + 8.8)               # trip 2
        k_hold = g.key_land
        k_hi = g.key_top
        rise = (g.y_pt + 0.1) - (g.v_top - g.L)

        def trip_key(t, T):
            a_, b_ = T
            pts = [(a_, 5.5), (a_ + 1.0, k_hi), (a_ + 1.6, k_hi), (a_ + 2.2, k_hold), (a_ + 2.7, k_hold), (a_ + 3.4, k_hold + rise), (b_, k_hold + rise + 5)]
            return PD.keys(t, pts)

        def draw_caseA(c, t, look):
            a = PD.vis(t, s[1] + 0.2, tA, 0.5)
            if a <= 0:
                return
            G.draw_spm(c, look, g, a, annulus=P.GAS)
            if t < T1[0] + 2.7:
                G.draw_valve(c, look, g.px, g.v_top, g.L, g.vw, a, detail="body", outline=P.BAD)
            if T1[0] < t < T1[1]:
                ky = trip_key(t, T1)
                kk = PD.ramp(t, T1[0] + 1.0, T1[0] + 1.5) * (1 - PD.ramp(t, T1[0] + 3.4, T1[0] + 3.9))
                xy = G.draw_kot(c, look, g, ky, 0.0, kk, a * PD.vis(t, T1[0], T1[1] - 0.4, 0.3), tool="pulling", grip=PD.ramp(t, T1[0] + 2.3, T1[0] + 2.5))
                if xy and t >= T1[0] + 2.7:
                    G.draw_valve(c, look, xy[0], xy[1] + 0.12 * g.s, g.L, g.vw, a * PD.vis(t, T1[0], T1[1] - 0.4, 0.3), detail="body", ring=0, pin=0, outline=P.BAD)
                PD.flash(c, look, g.px, g.v_top, 0.4, P.BAD, (t - (T1[0] + 2.65)) / 0.6)
            if T2[0] < t < T2[1]:
                ky = trip_key(t, T2)
                kk = PD.ramp(t, T2[0] + 1.0, T2[0] + 1.5) * (1 - PD.ramp(t, T2[0] + 2.9, T2[0] + 3.4))
                xy = G.draw_kot(c, look, g, ky if t < T2[0] + 2.7 else PD.keys(t, [(T2[0] + 2.7, k_hold), (T2[0] + 3.4, k_hold + 0.6), (T2[1], k_hold + 6)]),
                                0.0, kk, a * PD.vis(t, T2[0], T2[1] - 0.4, 0.3), tool="running")
                if xy and t < T2[0] + 2.7:
                    G.draw_valve(c, look, xy[0], xy[1] + 0.12 * g.s, g.L, g.vw, a, detail="body", outline=P.SAFE)
                PD.flash(c, look, g.px, g.y_lug, 0.4, P.SAFE, (t - (T2[0] + 2.4)) / 0.6)
            if t >= T2[0] + 2.7:
                G.draw_valve(c, look, g.px, g.v_top, g.L, g.vw, a, detail="body", outline=P.SAFE)

        st.procedural(b.start, b.end, 0.5, draw_caseA)
        K.show(st, K.note(st, "side-pocket mandrel", g.bx + 0.3, -3.35, 0.18, P.MUTED, align="c"), s[1] + 0.4, tA, 0.4)
        xl_ = g.xO + g.wall + 0.25
        ft = K.tag(st, xl_, g.v_top - 0.4, "failed valve", color=P.BAD, fg=P.BG, size=0.16, z=1.0, align="l")
        K.show(st, ft, s[1] + 1.0, T1[0] + 3.0, 0.35)
        tr1 = K.tag(st, xl_, 2.0, "trip 1: pull", color=P.PANEL2, size=0.16, z=1.0, align="l")
        tr2 = K.tag(st, xl_, 1.55, "trip 2: set", color=P.PANEL2, size=0.16, z=1.0, align="l")
        K.show(st, tr1, T1[0] + 0.2, tA, 0.3)
        K.show(st, tr2, T2[0] + 0.2, tA, 0.3)
        ok = K.tag(st, xl_, g.v_top - 0.4, "new valve set", color=P.SAFE, fg=P.BG, size=0.16, z=1.0, align="l")
        K.show(st, ok, T2[0] + 3.0, tA, 0.35)

        # -------------------------------------------------------------------------- case B: scale in a 55 degree well, coiled tubing
        tB = s[7] - 0.4
        sc_a, sc_b = w.y(3050), w.y(3540)
        scale1 = st.rect(w.cx, (sc_a + sc_b) / 2, w.TUB_OD - 2 * w.TUB_WALL, sc_a - sc_b, P.SCALE, 0.19)
        scale2 = st.rect(w.cx, (w.y(3800) + w.y(4100)) / 2, w.CAS_OD - 2 * w.CAS_WALL, w.y(3800) - w.y(4100), P.SCALE, 0.12)
        K.show(st, [scale1, scale2], s[4] + 0.6, tB, 0.8)
        st.fade_out(scale1, s[6] + 1.2, 1.2)
        st.fade_out(scale2, s[6] + 2.2, 1.2)
        K.show(st, K.callout(st, "scale", -4.15, (sc_a + sc_b) / 2, w.cx + 0.15, (sc_a + sc_b) / 2, size=0.17, align="l"), s[4] + 0.8, tB, 0.4)
        y = y_top
        _, h = fact(st, lx, y, "WRONG", "Scale narrows the tubing and clogs the perforations. The well leans at 55°.", s[4] + 0.5, P.BAD, t1=tB); y -= h
        _, h = fact(st, lx, y, "NEEDS", "Pump a jet or a mill, and push it down the inclined well.", s[5] - 0.5, P.PORE, t1=tB); y -= h
        _, h1 = fact(st, lx, y, "A WIRE", "can carry a gauge and see it, but cannot pump or push.", s[5], C_SLICK, t1=s[6] - 0.2)
        _, h2 = fact(st, lx, y, "METHOD", "Coiled tubing with a jetting nozzle, or a motor and mill.", s[6], C_CT, t1=tB)
        y -= max(h1, h2)
        _, h = fact(st, lx, y, "RESULT", "Bore open, perforations clear, inflow restored.", s[6] + 2.2, P.SAFE, t1=tB)
        # the wire runs down with a gauge, stops at the scale
        wb = st.rect(w.cx, wtop, 0.03, 0.001, P.WIRE, 0.9, anchor="t")
        st.scale_to(wb, s[5], s[5] + 1.8, sy=wtop - (sc_a + 0.25))
        gb = st.rect(w.cx, sc_a + 0.12, 0.12, 0.26, P.WARN, 0.92, role="solid")
        K.show(st, [wb], s[5] - 0.1, s[6] - 0.2, 0.2)
        K.show(st, [gb], s[5] + 1.6, s[6] - 0.2, 0.3)
        # the coil: thicker, with a nozzle
        cb = st.rect(w.cx, wtop, 0.075, 0.001, P.PORE, 0.9, anchor="t")
        st.scale_to(cb, s[6] + 0.1, s[6] + 2.6, sy=wtop - w.y(4000))
        nz = st.rect(w.cx, wtop, 0.12, 0.14, P.WARN, 0.92, role="solid")
        st.move(nz, s[6] + 0.1, s[6] + 2.6, dy=-(wtop - w.y(4000)))
        K.show(st, [cb, nz], s[6] + 0.1, tB, 0.2)
        # detail: an inclined section, 55 degrees from vertical; the coil pushes down it and jets the scale away
        p0 = (2.5, 2.1)
        ang = -(90 - 55)                      # 55 degrees from the vertical = 35 degrees below horizontal
        L, od = 5.2, 0.56
        walls = [st.rect(*slant(p0, ang, L / 2, o), L, 0.07, P.STEEL, 0.4, rot=ang, role="steel") for o in (od / 2, -od / 2)]
        bore = st.rect(*slant(p0, ang, L / 2), L, od, P.PANEL, 0.3, rot=ang)
        vert = st.dashed(p0, (p0[0], p0[1] - 2.2), P.MUTED, 0.03)
        arc = st.line(arc_pts(p0[0], p0[1], 1.4, -90, ang, 20), P.WARN, 0.04, 0.8)
        deg = st.text("55°", p0[0] + 0.55, p0[1] - 1.9, 0.3, P.WARN, 0.9, kind="bold")
        K.show(st, walls + [bore, vert, arc, deg], s[4] + 0.4, tB, 0.5)
        blocks = [st.rect(*slant(p0, ang, a), 0.22, od * 0.8, P.SCALE, 0.45, rot=ang) for a in (3.4, 3.85, 4.3, 4.75)]
        K.show(st, blocks, s[4] + 0.8, tB, 0.5)
        for k, blk in enumerate(blocks):
            st.fade_out(blk, s[6] + 0.9 + 0.45 * k, 0.5)
        reach = 4.55
        coil = st.rect(*slant(p0, ang, 0.0), 0.001, 0.1, P.PORE, 0.5, anchor="l", rot=ang)
        st.scale_to(coil, s[6] + 0.1, s[6] + 2.6, sx=reach)
        noz = st.rect(*slant(p0, ang, 0.0), 0.18, 0.24, P.WARN, 0.55, rot=ang, role="solid")
        d = slant(p0, ang, reach)
        st.move(noz, s[6] + 0.1, s[6] + 2.6, dx=d[0] - p0[0], dy=d[1] - p0[1])
        K.show(st, [coil, noz], s[6] + 0.1, tB, 0.2)
        st.flow([slant(p0, ang, reach), slant(p0, ang, reach + 0.55)], s[6] + 2.5, tB, P.ACID, n=5, speed=0.5, r=0.04)
        # what a wire cannot do
        need = []
        for i, nm in enumerate(("push", "pump")):
            yy = -1.55 - i * 0.55
            need.append(K.tag(st, 3.0, yy, nm, color=P.PANEL2, size=0.2, z=0.9, align="l"))
        xs = []
        for i in range(2):
            xs += K.xmark(st, 4.15, -1.55 - i * 0.55, 0.11, b.word(5, "cannot") + 0.2 + 0.2 * i)
        K.show(st, need[0] + need[1], s[5] + 0.3, s[6] - 0.2, 0.4)
        K.show(st, xs, b.word(5, "cannot") + 0.2, s[6] - 0.2, 0.2)

        # -------------------------------------------------------------------------- case C: a tubing leak, a patch or a rig
        ly_ = w.y(1800)
        hole = st.circle(w.cx - w.TUB_OD / 2 + 0.02, ly_, 0.07, P.BAD, 0.95, role="disc")
        K.show(st, [hole], s[7] + 0.6, s[8] + 2.6, 0.3)
        st.flow([(w.cx - 0.2, ly_), (w.cx - 0.5, ly_ + 0.05)], s[7] + 0.8, s[8] + 2.6, P.OIL, n=4, speed=0.5, r=0.03)
        K.show(st, K.callout(st, "leak", -4.15, ly_ + 0.55, w.cx - 0.2, ly_ + 0.02, size=0.17, align="l"), s[7] + 0.8, b.end, 0.4)
        y = y_top
        _, h = fact(st, lx, y, "WRONG", "The tubing has a leak at 1,800 m MD.", s[7] + 0.5, P.BAD); y -= h
        _, h = fact(st, lx, y, "FIRST TRY", "A patch set across the hole, on electric line or coiled tubing.", s[8], C_ELINE); y -= h
        _, h = fact(st, lx, y, "IF IT CANNOT", "The tubing has to come out.", s[9], C_RIG); y -= h
        _, h = fact(st, lx, y, "METHOD", "A rig, and the well is killed first.", s[9] + 1.0, C_RIG)
        patch = st.rect(w.cx, wtop + 0.1, w.TUB_OD - 2 * w.TUB_WALL - 0.02, 0.3, P.COPPER, 0.93, role="solid")
        st.move(patch, s[8] + 0.2, s[8] + 2.6, to=(w.cx, ly_))
        K.show(st, [patch], s[8] + 0.1, None, 0.3)
        st.fade_out(hole, s[8] + 2.6, 0.4)
        # detail: a tubing section with a hole, and a patch with seals sliding over it
        tcx, tcy = 4.4, 0.5
        up = [st.rect(tcx - 0.45 + 0.04, tcy + 1.0, 0.08, 1.9, P.STEEL, 0.4, role="steel"), st.rect(tcx - 0.45 + 0.04, tcy - 1.0, 0.08, 1.9, P.STEEL, 0.4, role="steel"),
              st.rect(tcx + 0.45 - 0.04, tcy, 0.08, 3.9, P.STEEL, 0.4, role="steel")]
        bore2 = st.rect(tcx, tcy, 0.82, 3.9, P.BG, 0.2)
        pit = [st.rect(tcx - 0.45 + 0.04, tcy + 0.09, 0.08, 0.05, P.BAD, 0.45, role="solid"), st.rect(tcx - 0.45 + 0.04, tcy - 0.09, 0.08, 0.05, P.BAD, 0.45, role="solid")]
        K.show(st, up + [bore2], s[7] + 0.2, b.end, 0.5)
        K.show(st, pit, s[7] + 0.6, s[8] + 2.6, 0.4)
        st.flow([(tcx - 0.2, tcy), (tcx - 1.0, tcy)], s[7] + 0.8, s[8] + 2.6, P.OIL, n=5, speed=0.5, r=0.04)
        pt = [st.rect(tcx, tcy + 2.4, 0.74, 0.7, P.COPPER, 0.6, role="solid"),
              st.rect(tcx, tcy + 2.4 + 0.3, 0.74, 0.09, P.RUBBER, 0.62, role="solid"), st.rect(tcx, tcy + 2.4 - 0.3, 0.74, 0.09, P.RUBBER, 0.62, role="solid")]
        K.show(st, pt, s[8] + 0.2, b.end, 0.4)
        st.move(pt, s[8] + 0.6, s[8] + 2.8, dy=-2.4)
        K.show(st, K.note(st, "patch with seals", tcx + 0.9, tcy + 1.0, 0.18, P.MUTED, align="l"), s[8] + 2.0, b.end, 0.4)
        K.show(st, K.note(st, "hole in the tubing", tcx + 0.9, tcy - 0.5, 0.18, P.MUTED, align="l"), s[7] + 1.0, s[8] + 2.6, 0.4)
        # calendar: a rig is weeks
        cal = [st.rect(5.6 + c * 0.25, -1.85 - r * 0.27, 0.2, 0.2, P.PANEL2, 0.5) for r in range(3) for c in range(7)]
        K.show(st, cal, s[9] + 0.4, b.end, 0.4)
        for i, o in enumerate(cal):
            st.recolor(o, s[9] + 1.4 + 0.12 * i, s[9] + 1.55 + 0.12 * i, P.BAD)
        K.show(st, K.note(st, "a rig job: weeks", 6.35, -1.35, 0.2, P.TEXT, align="c"), s[9] + 0.4, b.end, 0.4)
        K.show(st, K.note(st, "(illustrative)", 6.35, -2.9, 0.16, P.MUTED, align="c"), s[9] + 0.6, b.end, 0.4)


# ====================================================================================================== 8.03
def b803(st, tl):
    b = tl["8.03"]
    s = b.sent
    with st.span(b.start, b.end):
        tiles = [(-5.3, "TRACTORS", "push wireline tools into horizontal wells", s[1]),
                 (0.0, "INSTRUMENTED COIL", "fibre or conductors: real-time data", s[2]),
                 (5.3, "VESSELS", "work that once needed a rig", s[3])]
        cy, th = 0.85, 4.5
        for cx, name, sub, ta in tiles:
            card = K.card(st, cx, cy, 4.7, th, P.PANEL, 0.3)
            ttl = K.title(st, name, cx, cy + th / 2 - 0.35, 0.27, P.TEXT, align="c")
            sb = K.note(st, sub, cx, cy + th / 2 - 0.72, 0.18, P.MUTED, align="c")
            K.show(st, card + ttl + sb, ta - 0.2, None, 0.5)
        # --- tractor in a horizontal well
        cx, py = -5.3, 0.9
        pipe = K.pipe_h(st, py, cx - 2.1, cx + 2.1, 0.8, 0.07, P.STEEL, 0.4)
        K.show(st, pipe.walls, s[1] - 0.2, None, 0.5)
        wire = st.rect(cx - 2.05, py, 0.001, 0.03, P.WIRE, 0.9, anchor="l")
        st.scale_to(wire, s[1] + 0.2, s[1] + 4.2, sx=2.9)
        tr = [st.rect(cx - 1.15, py, 0.8, 0.22, P.WARN, 0.9, role="solid")]
        for dx in (-0.25, 0.25):
            tr += [st.circle(cx - 1.15 + dx, py + 0.2, 0.09, P.STEEL, 0.92, role="disc"), st.circle(cx - 1.15 + dx, py - 0.2, 0.09, P.STEEL, 0.92, role="disc")]
        tool = [st.rect(cx - 0.62, py, 0.4, 0.14, P.STEEL, 0.9, role="steel")]
        K.show(st, [wire] + tr + tool, s[1] + 0.2, None, 0.4)
        st.move(tr + tool, s[1] + 0.2, s[1] + 4.2, dx=2.9)
        K.show(st, K.note(st, "wheels grip the wall", cx, -0.2, 0.2, P.TEXT, align="c"), s[1] + 1.0, None, 0.5)
        K.show(st, K.note(st, "gravity alone would not get it there", cx, -0.65, 0.17, P.MUTED, align="c"), s[1] + 2.0, None, 0.5)
        # --- instrumented coil: a tube with a light fibre down the middle
        cx = 0.0
        tube = K.pipe_h(st, py, cx - 2.1, cx + 2.1, 0.8, 0.08, P.PORE, 0.4)
        fib = st.rect(cx, py, 4.2, 0.05, P.ACID, 0.6, role="flat")
        K.show(st, tube.walls + [fib], s[2] - 0.2, None, 0.5)
        st.flow([(cx - 2.0, py), (cx + 2.0, py)], s[2] + 0.2, b.end, P.ACID, n=7, speed=0.9, r=0.05, glow=True)
        pts = [(cx - 1.8 + 3.6 * i / 60, -0.4 + 0.25 * math.sin(i * 0.5) + 0.12 * math.sin(i * 1.9)) for i in range(61)]
        trace = st.line(pts, P.ACID, 0.04, 0.7)
        K.show(st, [trace], s[2] + 1.0, None, 0.3)
        st.draw_on(trace, s[2] + 1.0, s[2] + 4.0, "LINEAR")
        K.show(st, K.note(st, "pressure, temperature, strain: live", cx, -1.1, 0.17, P.MUTED, align="c"), s[2] + 2.0, None, 0.5)
        # --- vessel: plugging a subsea well from a vessel
        cx, wl, sbd = 5.3, 0.95, -0.55
        sea = [st.rect(cx, (wl + sbd) / 2, 4.7, wl - sbd, P.SEA, 0.35, alpha=0.6)]
        sb_ = st.rect(cx, sbd, 4.7, 0.1, P.SEABED, 0.4)
        v = K.vessel(st, cx - 0.9, wl, scale=0.5, z=0.6)
        well = [st.rect(cx, sbd - 0.45, 0.3, 0.9, P.STEEL_DK, 0.4, role="steel"), st.rect(cx, sbd - 0.15, 0.55, 0.3, P.STEEL, 0.45, role="steel")]
        K.show(st, sea + [sb_] + v.hull + v.moonpool + v.derrick + v.crane + well, s[3] - 0.2, None, 0.5)
        ln = st.line([(cx - 0.9, wl - 0.2), (cx - 0.9, sbd + 0.3), (cx, sbd + 0.3), (cx, sbd - 0.1)], P.WIRE, 0.03, 0.8)
        K.show(st, [ln], s[3] + 0.6, None, 0.2)
        st.draw_on(ln, s[3] + 0.6, s[3] + 3.0, "LINEAR")
        plug = st.rect(cx, sbd - 0.7, 0.24, 0.3, P.SAFE, 0.5, role="solid")
        K.show(st, [plug], s[3] + 3.0, None, 0.4)
        K.show(st, K.note(st, "a plug set from a vessel", cx - 0.4, sbd - 0.62, 0.17, P.MUTED, align="r"), s[3] + 3.2, None, 0.5)
        # --- the principles
        pr = [("AIRLOCK", "a pressure-tight way in", P.PORE, -5.3), ("CARRY", "a way to place the tools", P.WARN, 0.0), ("TWO BARRIERS", "at all times", P.SAFE, 5.3)]
        K.show(st, K.note(st, "what has not changed", 0.0, -1.7, 0.19, P.MUTED, align="c"), s[4], None, 0.5)
        for i, (nm, sb, colr, x) in enumerate(pr):
            ac = st.rect(x, -2.2, 3.6, 0.05, colr, 0.8)
            t1 = st.text(nm, x, -2.6, 0.42, colr, 0.9, kind="bold")
            t2 = st.text(sb, x, -3.05, 0.22, P.MUTED, 0.9)
            tt = b.word(4, ["airlock", "carry", "two barriers"][i])
            K.show(st, [ac, t1, t2], tt - 0.1, None, 0.5)


# ====================================================================================================== 8.04
def b804(st, tl):
    b = tl["8.04"]
    s = b.sent
    with st.span(b.start, b.end):
        w = _well(st, 0.0, y_top=2.9, scale=0.78, rock_w=1.0, extras=False)
        K.show(st, w.base, b.start + 0.1, None, 0.6)
        st.flow([(w.cx, w.y(3800)), (w.cx, w.y(0) + 0.1)], b.start + 0.5, b.end, P.OIL, n=8, speed=0.5, r=0.03)
        # the seven reasons (left) tick off with the voice
        words = ["to see", "to secure", "to clear", "to stimulate", "to lift", "to steer", "to finish"]
        for i, (word, sub) in enumerate(REASONS):
            y = 3.1 - i * 0.78
            chip = K.tag(st, -6.9, y, f"{i + 1}  {word}", color=P.PANEL2, fg=P.TEXT, size=0.24, z=0.9, align="l")
            K.show(st, chip, s[0] + 0.15 * i, None, 0.4)
            tt = b.word(1, words[i])
            ck = K.check(st, -3.95, y, tt + 0.15, s=0.15)
            K.show(st, ck, tt, None, 0.2)
        # the method ladder (right)
        rungs = [("WIRELINE", "carry and hammer", C_SLICK, "wire"), ("COILED TUBING", "also pump and push", C_CT, "tube"),
                 ("SNUBBING", "rotate, heavy loads, live", C_SNUB, "pipe"), ("DRILLING RIG", "pull the whole well apart", C_RIG, "rig")]
        for i, (nm, sub, colr, key) in enumerate(rungs):
            y = 2.8 - i * 1.25
            card = K.card(st, 5.3, y, 4.3, 0.95, P.PANEL, 0.4)
            bar = st.rect(3.2, y, 0.09, 0.95, colr, 0.5)
            t1 = st.text(nm, 3.5, y + 0.2, 0.3, colr, 0.5, align="l", kind="bold")
            t2 = st.text(sub, 3.5, y - 0.22, 0.21, P.MUTED, 0.5, align="l")
            tt = b.word(3, key)
            K.show(st, card + [bar, t1, t2], tt - 0.2, None, 0.4)
        arl = st.arrow(-3.7, 0.2, -1.9, 0.2, P.PORE, 0.06, 0.24, 0.8)
        arr = st.arrow(3.0, -0.3, 1.9, -0.3, P.WARN, 0.06, 0.24, 0.8)
        K.show(st, [arl], s[1] + 0.5, None, 0.4)
        K.show(st, [arr], s[3] + 0.5, None, 0.4)
        # sentence 4: a well is as healthy as the last time someone looked inside it
        hx, hy, hw = 0.0, -3.2, 4.4
        hl = st.text("WELL HEALTH", hx - hw / 2, hy + 0.42, 0.17, P.MUTED, 0.9, align="l", kind="bold")
        hb = st.rect(hx, hy, hw, 0.22, P.PANEL2, 0.8, role="card")
        hf = st.rect(hx - hw / 2, hy, hw, 0.22, P.SAFE, 0.85, anchor="l")
        K.show(st, [hl, hb, hf], s[4] - 0.3, None, 0.5)
        cn = st.counter(hx + hw / 2, hy + 0.42, s[4], s[4] + 3.3, 0, 540, fmt="days since a look inside: {:.0f}", size=0.17, color=P.MUTED, z=0.9, align="r", kind="sans")
        st.scale_to(hf, s[4], s[4] + 3.3, sx=hw * 0.35)
        st.recolor(hf, s[4], s[4] + 3.3, P.BAD)
        tool = st.rect(w.cx, w.y(0) + 0.2, 0.12, 0.34, P.WARN, 0.95, role="solid")
        st.move(tool, s[4] + 3.3, s[4] + 5.0, to=(w.cx, w.y(3000)))
        K.show(st, [tool], s[4] + 3.2, s[5] - 0.2, 0.3)
        st.scale_to(hf, s[5] - 0.2, s[5] + 0.6, sx=hw)
        st.recolor(hf, s[5] - 0.2, s[5] + 0.6, P.SAFE)
        # closing card
        T = s[5] + 0.7
        with st.span(T - 0.1, b.end):
            back = st.rect(0, 0, 16.5, 9.5, P.BG, 50.0, role="backdrop")
            big = st.text("INTO THE LIVE WELL", 0, 1.55, 0.95, P.TEXT, 50.2, kind="bold")
            sub = st.text("Well intervention: why we go back in, and how", 0, 0.7, 0.32, P.PORE, 50.2)
            rule = st.line([(-3.2, 0.15), (3.2, 0.15)], P.PORE, 0.04, 50.3)
            lines = ["An illustrative composite well. Depths, pressures and forces are teaching values (marked SIM in script/FLAGS.md), not field data.",
                     "Norwegian regulations and NORSOK D-010 are described from secondary sources and have not been checked against the primary documents (marked VERIFY).",
                     "General education only: not engineering advice, and not an operating procedure."]
            tx = [st.text(wrap_to(t, 0.2, 11.0), 0, -0.55 - i * 0.85, 0.2, P.MUTED, 50.2, valign="c") for i, t in enumerate(lines)]
            st.fade_in([back], T, 1.0)
            st.fade_in([big, sub], T + 0.6, 0.8)
            st.draw_on(rule, T + 0.8, T + 1.8, "BEZIER")
            for i, o in enumerate(tx):
                st.fade_in([o], T + 1.4 + 0.5 * i, 0.6)


# ====================================================================================================== build
def build(st, tl):
    F.header(st, tl)
    b801(st, tl)
    b802(st, tl)
    b803(st, tl)
    b804(st, tl)
