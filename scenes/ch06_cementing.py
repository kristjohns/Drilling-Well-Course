"""Ch 6: Cementing. Includes THE CEMENT DISPLACEMENT animation (eccentric annulus vs centralised)."""
from __future__ import annotations
import math

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common.shapes import Cutaway, WindowChart, pill, loop_move

TITLE = "Cementing"


# ---------------------------------------------------------------- 6.01 three jobs
def beat_jobs(st, tl):
    b = tl["6.01"]
    s = b.sent
    with st.span(b.start, b.end):
        cx, yt, yb = -3.4, 3.4, -3.0
        cut = Cutaway(st, cx, yt, yb, hole_w=2.4, pipe_w=1.0, rock_w=1.8)
        base = cut.draw()
        cem = [cut.static_gap("l", P.CEMENT, yt, yb, 0.05), cut.static_gap("r", P.CEMENT, yt, yb, 0.05)]
        mud = cut.static_bore(P.MUD, yt, yb, 0.05)
        st.fade_in(base + cem + [mud], b.start, 0.5)
        lab = {}
        # 1 support
        a1 = st.arrow(0.6, 2.4, cut.pipe[1] + 0.05, 2.0, P.PORE, 0.06, 0.2, 0.5)
        l1 = pill(st, 2.6, 2.4, "1  supports the pipe", P.PANEL2, P.PORE, 0.26, 0.5, align="l")
        st.fade_in(a1 + l1, s[1], 0.5)
        # 2 isolation: formation fluid trying to run up the outside is blocked
        flow = st.arrow(cut.hole[1] + 0.9, -2.2, cut.hole[1] + 0.9, 0.0, P.WATER, 0.1, 0.3, 0.5)
        blk = [st.line([(cut.hole[1] - 0.1, 0.25), (cut.hole[1] + 0.9, 0.25)], P.BAD, 0.1, 0.55)]
        l2 = pill(st, 2.6, 0.2, "2  seals the gap: nothing\n   flows along the outside", P.PANEL2, P.WATER, 0.26, 0.5, align="l")
        st.fade_in(flow + blk + l2, s[2], 0.5)
        # 3 protection
        sh = st.ring(cx, 0.0, 0.55, 0.06, P.SAFE, 0.5)
        l3 = pill(st, 2.6, -2.0, "3  protects the steel\n   from corrosion", P.PANEL2, P.SAFE, 0.26, 0.5, align="l")
        st.fade_in([sh] + l3, s[3], 0.5)
        # barrier glow
        st.recolor(cem, s[4] + 0.3, s[4] + 1.2, P.SAFE)
        bl = pill(st, 2.6, -3.15, "the cement behind the casing is\nitself a well barrier", P.SAFE, "#06201c", 0.26, 0.6, align="l")
        st.fade_in(bl, s[4] + 0.8, 0.5)


# ---------------------------------------------------------------- 6.02 U-tube, plugs, float valve, plug bumped
def beat_utube(st, tl):
    b = tl["6.02"]
    s = b.sent
    with st.span(b.start, b.end):
        cx, yt, yb = -3.6, 3.5, -3.0
        shoe_y = -2.4
        cut = Cutaway(st, cx, yt, yb, hole_w=2.4, pipe_w=1.1, rock_w=1.6)
        base = cut.draw(pipe_bottom=shoe_y)
        mb = cut.static_bore(P.MUD, yt, shoe_y, 0.03)
        ml = cut.static_gap("l", P.MUD, yt, yb, 0.03)
        mr = cut.static_gap("r", P.MUD, yt, yb, 0.03)
        st.fade_in(base + [mb, ml, mr], b.start, 0.5)
        # float valve at the bottom of the string
        fv = st.poly([(cx - 0.45, shoe_y + 0.35), (cx + 0.45, shoe_y + 0.35), (cx, shoe_y + 0.05)], P.WARN, 0.4)
        fvl = st.text("float valve:\none-way", cx + 0.95, shoe_y + 0.3, 0.2, P.WARN, 0.4, align="l", kind="bold")
        st.fade_in([fv], b.start + 0.5, 0.4)
        # U-tube labels
        d = st.text("down the inside", cx - 1.4, 2.2, 0.24, P.CEMENT, 0.4, align="r", kind="bold")
        u = st.text("up the outside", cx + 1.4, 2.2, 0.24, P.CEMENT, 0.4, align="l", kind="bold")
        st.fade_in([d, u], s[0], 0.5)
        # fluid train in the pipe (front to back): spacer, bottom plug, cement, top plug
        w = 0.95
        y0 = 2.0
        spacer = st.rect(cx, y0 + 0.25, w, 0.5, P.SPACER, 0.2)
        bplug = st.rect(cx, y0 + 0.56, w, 0.12, P.WARN, 0.25)
        cement = st.rect(cx, y0 + 1.37, w, 1.5, P.CEMENT, 0.2)
        tplug = st.rect(cx, y0 + 2.18, w, 0.12, P.BAD, 0.25)
        train = [spacer, bplug, cement, tplug]
        st.fade_in(train, s[2] - 0.3, 0.4)
        names = [st.text("spacer", cx - 0.75, y0 + 0.25, 0.2, P.SPACER, 0.4, align="r", kind="bold"),
                 st.text("bottom plug", cx - 0.75, y0 + 0.62, 0.2, P.WARN, 0.4, align="r", kind="bold"),
                 st.text("cement", cx - 0.75, y0 + 1.37, 0.2, P.CEMENT, 0.4, align="r", kind="bold"),
                 st.text("top plug", cx - 0.75, y0 + 2.18, 0.2, P.BAD, 0.4, align="r", kind="bold")]
        st.fade_in(names, s[2] + 0.2, 0.4)
        t_move0, t_move1 = s[2] + 1.0, s[3] + 3.0
        drop = (y0 + 0.0) - (shoe_y + 0.45) - 0.0
        st.move(train + names, t_move0, t_move1, dy=-(drop - 0.02), interp="LINEAR")
        # annulus: spacer then cement rise up the outside
        t_up0 = t_move1 - 0.6
        sp_l = cut.fill_gap("l", P.SPACER, shoe_y, 1.2, t_up0, t_up0 + 3.0, 0.12, interp="LINEAR")
        sp_r = cut.fill_gap("r", P.SPACER, shoe_y, 1.2, t_up0, t_up0 + 3.0, 0.12, interp="LINEAR")
        ce_l = cut.fill_gap("l", P.CEMENT, shoe_y, -0.4, t_up0 + 0.4, t_up0 + 3.0, 0.13, interp="LINEAR")
        ce_r = cut.fill_gap("r", P.CEMENT, shoe_y, -0.4, t_up0 + 0.4, t_up0 + 3.0, 0.13, interp="LINEAR")
        st.fade_in([sp_l, sp_r, ce_l, ce_r], t_up0, 0.1)
        # pipeline pig inset (the analogy)
        pc = st.rect(4.5, 2.7, 3.6, 0.55, P.PANEL2, 0.2)
        pig = st.circle(4.9, 2.7, 0.2, P.WARN, 0.3)
        pl = st.text("pipeline pig", 4.5, 3.3, 0.22, P.TEXT, 0.3, kind="bold")
        st.fade_in([pc, pig, pl], s[1], 0.5)
        st.move(pig, s[1] + 0.5, s[1] + 3.0, dx=-0.9, interp="LINEAR")
        # float valve text appears at s3
        st.fade_in(fvl, s[3], 0.4)
        # pressure trace with spike when the top plug lands
        c = Chart(st, 1.6, -2.7, 5.6, 3.6, (0, 10), (0, 1))
        fr = c.frame(xticks=[], yticks=[], xlabel="volume pumped", ylabel="pump pressure", grid=False)
        tr = c.curve([0, 1, 5, 7.8, 8.0, 8.4, 8.6, 10], [0.15, 0.2, 0.3, 0.32, 0.38, 0.88, 0.9, 0.9], P.PORE, 0.08, 0.4)
        bump = c.label(8.3, 0.95, "top plug lands:\npressure jumps\n= displaced", 0.2, P.WARN, "r", dx=-0.1, dy=0.35)
        st.fade_in(fr, s[4] - 1.0, 0.4)
        st.draw_on(tr, s[4] - 0.6, s[4] + 3.4)
        st.fade_in(bump, s[4] + 2.6, 0.5)
        st.move(tplug, s[4] + 0.5, s[4] + 1.0, dy=0.0)


# ---------------------------------------------------------------- 6.03 THE CEMENT DISPLACEMENT ANIMATION
def _inset(st, cx, cy, ecc, t, label):
    outer = st.ring(cx, cy, 0.5, 0.05, P.ROCK, 0.3)
    hole = st.circle(cx, cy, 0.46, P.MUD, 0.2)
    pipe = st.circle(cx + ecc, cy, 0.22, P.STEEL, 0.4)
    lab = st.text(label, cx, cy - 0.78, 0.2, P.TEXT, 0.4, kind="bold")
    st.fade_in([outer, hole, pipe, lab], t, 0.5)
    return [outer, hole, pipe, lab]


def beat_displacement(st, tl):
    b = tl["6.03"]
    s = b.sent
    yt, yb = 2.3, -3.1
    H = yt - yb
    with st.span(b.start, b.end):
        title = st.text("a section of the annulus, cutaway", 0.8, 4.0, 0.22, P.MUTED, 0.3)
        # LEFT: off-centre pipe
        cxL, cxR = -2.9, 3.6
        L = Cutaway(st, cxL, yt, yb, hole_w=2.6, pipe_w=1.0, eccentric=0.55, rock_w=1.2)
        R = Cutaway(st, cxR, yt, yb, hole_w=2.6, pipe_w=1.0, eccentric=0.0, rock_w=1.2)
        baseL, baseR = L.draw(), R.draw()
        mudsL = [L.static_gap("l", P.MUD, yt, yb, 0.03), L.static_gap("r", P.MUD, yt, yb, 0.03)]
        mudsR = [R.static_gap("l", P.MUD, yt, yb, 0.03), R.static_gap("r", P.MUD, yt, yb, 0.03)]
        boreL, boreR = L.static_bore(P.CEMENT, yt, yb, 0.03), R.static_bore(P.CEMENT, yt, yb, 0.03)
        st.fade_in([title] + baseL + baseR + mudsL + mudsR + [boreL, boreR], b.start, 0.5)
        tL = st.text("OFF-CENTRE", cxL, 3.45, 0.3, P.BAD, 0.4, kind="bold")
        tR = st.text("CENTRALISED", cxR, 3.45, 0.3, P.SAFE, 0.4, kind="bold")
        st.fade_in(tL, s[0], 0.4)
        iL = _inset(st, cxL - 2.2, 3.4, 0.2, s[0] + 0.5, "")
        # LEFT fills: wide gap (left) races up, narrow gap (right) lags and stalls
        t0, t1 = s[1] + 0.3, s[1] + 5.3
        wideL = L.fill_gap("l", P.CEMENT, yb, yt, t0, t1, 0.12, interp="LINEAR")
        narrowL = L.fill_gap("r", P.CEMENT, yb, yb + 0.42 * H, t0, t1, 0.12, interp="LINEAR")
        lab_w = st.text("cement races up the wide side", cxL - 1.25, 0.9, 0.22, P.CEMENT, 0.4, align="r", kind="bold")
        lab_n = st.text("mud on the narrow\nside barely moves", cxL + 2.55, 1.4, 0.22, P.MUD, 0.4, align="l", kind="bold")
        st.fade_in([lab_w], s[1] + 1.0, 0.4)
        st.fade_in([lab_n], s[1] + 2.0, 0.4)
        # channel highlight
        gx0, gx1 = L.gap_r
        ytop_ch = yb + 0.42 * H
        ch = [st.rect((gx0 + gx1) / 2, (ytop_ch + yt) / 2, gx1 - gx0 + 0.12, yt - ytop_ch + 0.1, P.BAD, 0.45, alpha=0.0)]
        outline = [st.rect((gx0 + gx1) / 2, yt + 0.05, gx1 - gx0 + 0.2, 0.05, P.BAD, 0.5), st.rect((gx0 + gx1) / 2, ytop_ch, gx1 - gx0 + 0.2, 0.05, P.BAD, 0.5),
                   st.rect(gx0 - 0.04, (ytop_ch + yt) / 2, 0.05, yt - ytop_ch, P.BAD, 0.5), st.rect(gx1 + 0.04, (ytop_ch + yt) / 2, 0.05, yt - ytop_ch, P.BAD, 0.5)]
        ch_lab = pill(st, cxL + 2.0, -0.3, "a channel of mud left\nbehind the pipe:\na hidden path for fluid", P.BAD, "#ffffff", 0.22, 0.6, align="l")
        st.fade_in(outline + ch_lab, s[2] + 0.2, 0.5)
        # RIGHT: centralisers
        st.fade_in(tR, s[3], 0.4)
        _inset(st, cxR - 2.2, 3.4, 0.0, s[3] + 0.3, "")
        bows = []
        for yy in (1.5, -0.2, -1.9):
            for sx in (-1, 1):
                pts = [(R.pipe[0 if sx < 0 else 1], yy - 0.4), (R.pipe[0 if sx < 0 else 1] + sx * 0.28, yy), (R.pipe[0 if sx < 0 else 1], yy + 0.4)]
                bows.append(st.line(pts, P.WARN, 0.07, 0.4))
        st.fade_in(bows, s[3] + 0.3, 0.4)
        r0, r1 = s[3] + 1.0, s[3] + 6.0
        wl = R.fill_gap("l", P.CEMENT, yb, yt, r0, r1, 0.12, interp="LINEAR")
        wr = R.fill_gap("r", P.CEMENT, yb, yt, r0, r1, 0.12, interp="LINEAR")
        bl = st.text("centralisers", cxR + 2.35, 1.0, 0.22, P.WARN, 0.4, align="l", kind="bold")
        mv = st.text("pipe movement\nsweeps the mud", cxR + 2.35, -1.1, 0.22, P.SAFE, 0.4, align="l", kind="bold")
        ar = st.arrow(R.pipe[1] + 0.9, -0.2, R.pipe[1] + 0.9, 0.6, P.SAFE, 0.05, 0.18, 0.4) + st.arrow(R.pipe[1] + 0.9, 0.6, R.pipe[1] + 0.9, -0.2, P.SAFE, 0.05, 0.18, 0.4)
        st.fade_in([bl], s[3] + 0.6, 0.4)
        st.fade_in([mv] + ar, s[3] + 3.0, 0.4)
        st.fade_in(st.text("clean sheath, no channel", cxR, -3.55, 0.26, P.SAFE, 0.4, kind="bold"), r1, 0.5)


# ---------------------------------------------------------------- 6.04 window + lab tests
def beat_slurry(st, tl):
    b = tl["6.04"]
    s = b.sent
    with st.span(b.start, b.end):
        wc = WindowChart(st, x=-5.3, y=-3.0, w=5.0, h=6.3)
        objs = wc.axes() + [wc.curves()["pp"], wc.objs["fg"], wc.objs["pp_lbl"], wc.objs["fg_lbl"], wc.band()]
        st.fade_in(objs, b.start, 0.5)
        c = wc.c
        z = 3400
        heavy = st.circle(c.X(1.88), c.Y(z), 0.14, P.BAD, 0.6)
        light = st.circle(c.X(1.50), c.Y(z), 0.14, P.SAFE, 0.6)
        hl = pill(st, c.X(1.88) - 0.2, c.Y(z) + 0.55, "full-length dense cement\nexceeds the fracture limit", P.BAD, "#ffffff", 0.2, 0.7, align="r")
        ll = pill(st, c.X(1.50) - 0.2, c.Y(z) - 0.55, "lightweight lead slurry:\ninside the window", P.SAFE, "#06201c", 0.2, 0.7, align="r")
        st.fade_in([heavy] + hl, s[1] - 0.3, 0.5)
        st.fade_in([light] + ll, s[1] + 1.8, 0.5)
        # lab panels
        c1 = Chart(st, 1.2, 0.4, 2.6, 2.5, (0, 10), (0, 10))
        f1 = c1.frame(xticks=[], yticks=[], xlabel="time", ylabel="consistency", grid=False)
        tt = c1.curve([0, 6, 7.5, 8.3, 8.6], [1.2, 1.5, 2.4, 6.5, 9.5], P.PORE, 0.08, 0.4)
        ttl = c1.label(5.0, 9.0, "pumpable → sets:\nthickening time", 0.19, P.PORE, "r", dy=0.0)
        st.fade_in(f1, s[2], 0.4)
        st.draw_on(tt, s[2] + 0.4, s[2] + 2.4)
        st.fade_in(ttl, s[2] + 1.5, 0.4)
        c2 = Chart(st, 5.1, 0.4, 2.6, 2.5, (0, 10), (0, 10))
        f2 = c2.frame(xticks=[], yticks=[], xlabel="time", ylabel="strength", grid=False)
        cs = c2.curve([0, 2, 4, 6, 8, 10], [0.2, 1.5, 4.0, 6.5, 8.0, 8.8], P.SAFE, 0.08, 0.4)
        csl = c2.label(0.5, 9.2, "compressive strength", 0.19, P.SAFE, "l")
        st.fade_in(f2, s[2] + 1.2, 0.4)
        st.draw_on(cs, s[2] + 1.6, s[2] + 3.6)
        st.fade_in(csl, s[2] + 2.5, 0.4)
        # silica above ~110 C
        fade = c2.curve([6, 7, 8, 9, 10], [6.5, 6.0, 4.8, 3.6, 2.6], P.BAD, 0.06, 0.45)
        fl = c2.label(7.2, 3.0, "strength\nfades", 0.18, P.BAD, "l", dy=-0.2)
        sil = pill(st, 3.5, -1.4, "above about 110 °C:\nadd silica so strength holds", P.PANEL2, P.WARN, 0.24, 0.6)
        st.draw_on(fade, s[3], s[3] + 1.6)
        st.fade_in([fl] + sil, s[3] + 0.8, 0.5)
        st.recolor(fade, s[3] + 2.2, s[3] + 3.0, P.SAFE)


# ---------------------------------------------------------------- 6.05 the danger hour
def beat_danger(st, tl):
    b = tl["6.05"]
    s = b.sent
    with st.span(b.start, b.end):
        c = Chart(st, -4.2, -2.7, 6.2, 5.2, (0, 10), (0, 10))
        fr = c.frame(xticks=[], yticks=[], xlabel="time after placement", ylabel="pressure the cement column passes down", grid=False)
        zones = [(0, 3.2, P.WATER, "liquid"), (3.2, 7.0, P.WARN, "gel"), (7.0, 10, P.STEEL_DK, "solid")]
        zs = []
        for x0, x1, col, nm in zones:
            zs.append(st.rect(c.X((x0 + x1) / 2), c.Y(5), c.X(x1) - c.X(x0), c.Y(0) - c.Y(10), col, 0.05, alpha=0.22))
            zs.append(st.text(nm, c.X((x0 + x1) / 2), c.Y(9.4), 0.24, col, 0.2, kind="bold"))
        pore = c.hline(5.2, P.PORE, 0.05, 0.3)
        pl = c.label(9.8, 5.6, "pore pressure", 0.2, P.PORE, "r")
        st.fade_in(fr + zs + [pore, pl], s[0], 0.5)
        tr = c.curve([0, 2.5, 3.5, 5, 6.5, 8, 10], [8.0, 7.9, 7.0, 5.2, 3.3, 2.3, 2.0], P.MUD, 0.09, 0.4)
        trl = c.label(0.2, 8.4, "cement column", 0.2, P.MUD, "l")
        st.draw_on(tr, s[1], s[1] + 4.5)
        st.fade_in(trl, s[1] + 0.5, 0.4)
        cross = c.dot(5.0, 5.2, 0.16, P.BAD, 0.5)
        cl = pill(st, c.X(5.0) + 0.3, c.Y(6.8), "pressure support falls\nbelow pore pressure:\nstill permeable", P.BAD, "#ffffff", 0.2, 0.7, align="l")
        st.fade_in([cross] + cl, s[1] + 2.6, 0.5)
        # right: gas migrating into the annulus
        cut = Cutaway(st, 5.6, 2.8, -2.6, hole_w=1.8, pipe_w=0.8, rock_w=1.0)
        base = cut.draw()
        gl = cut.static_gap("l", P.CEMENT, 2.8, -2.6, 0.04)
        gr = cut.static_gap("r", P.CEMENT, 2.8, -2.6, 0.04)
        st.fade_in(base + [gl, gr], s[2] - 0.3, 0.5)
        gx = (cut.gap_r[0] + cut.gap_r[1]) / 2
        bubbles = [st.circle(cut.hole[1] + 0.05, -2.0 + 0.45 * i, 0.07, P.GAS, 0.5) for i in range(6)]
        for i, bb in enumerate(bubbles):
            t = s[2] + 0.4 * i
            st.fade_in(bb, t, 0.15)
            st.move(bb, t, t + 2.4, to=(gx, 0.2 + 0.4 * i), interp="LINEAR")
        path = st.line([(gx, -2.0), (gx, 2.4)], P.GAS, 0.07, 0.5)
        st.draw_on(path, s[2] + 2.8, s[2] + 4.0)
        pl2 = st.text("gas leaves a path", 5.6, -3.15, 0.26, P.GAS, 0.5, kind="bold")
        st.fade_in(pl2, s[2] + 3.0, 0.5)
        sm = st.text("designed around timing", 5.6, 3.5, 0.24, P.TEXT, 0.4, kind="bold")
        st.fade_in(sm, s[3], 0.5)


# ---------------------------------------------------------------- 6.06 logs and their limits
def _wave(st, x0, y, amp, decay, n=60, length=3.0, color=P.PORE, z=0.4):
    pts = []
    for i in range(n):
        t = i / (n - 1)
        pts.append((x0 + length * t, y + amp * math.exp(-decay * t) * math.sin(18 * t)))
    return st.line(pts, color, 0.05, z)


def beat_logs(st, tl):
    b = tl["6.06"]
    s = b.sent
    with st.span(b.start, b.end):
        # CBL waveforms
        card = st.rect(-3.6, 0.9, 4.4, 4.9, P.PANEL, 0.0)
        ttl = st.text("cement bond log: sound along the pipe", -3.6, 3.15, 0.22, P.TEXT, 0.3, kind="bold")
        st.fade_in([card, ttl], s[1], 0.4)
        free = _wave(st, -5.7, 1.7, 0.7, 1.2)
        bonded = _wave(st, -5.7, 0.0, 0.7, 7.0)
        fl = st.text("free pipe: rings", -5.7, 2.6, 0.22, P.WARN, 0.4, align="l", kind="bold")
        bl = st.text("bonded: damped", -5.7, 0.9, 0.22, P.SAFE, 0.4, align="l", kind="bold")
        st.draw_on(free, s[2], s[2] + 2.0)
        st.fade_in(fl, s[2], 0.4)
        st.draw_on(bonded, s[2] + 2.0, s[2] + 4.0)
        st.fade_in(bl, s[2] + 2.0, 0.4)
        # ultrasonic 360 deg map
        card2 = st.rect(1.6, 0.9, 3.6, 4.9, P.PANEL, 0.0)
        t2 = st.text("ultrasonic: 360° map", 1.6, 3.15, 0.22, P.TEXT, 0.3, kind="bold")
        st.fade_in([card2, t2], s[3] - 0.2, 0.4)
        cells = []
        for i in range(9):
            for j in range(12):
                chan = (i in (3, 4)) and j >= 5
                cells.append(st.rect(0.25 + i * 0.3, 2.3 - j * 0.24, 0.28, 0.22, P.BAD if chan else P.CEMENT, 0.3, alpha=0.9))
        st.fade_in(cells, s[3] + 0.3, 0.6)
        chl = st.text("channel", 1.25, -0.5, 0.2, P.BAD, 0.5, kind="bold")
        st.fade_in(chl, s[3] + 1.4, 0.4)
        # microannulus
        quiet = st.text("a quiet log ≠ a seal", 5.9, 3.0, 0.3, P.WARN, 0.5, kind="bold")
        st.fade_in(quiet, s[4], 0.5)
        pipe = st.rect(5.6, 0.9, 0.4, 2.0, P.STEEL, 0.3)
        gap = st.rect(5.85, 0.9, 0.06, 2.0, P.BG, 0.4)
        cem = st.rect(6.2, 0.9, 0.5, 2.0, P.CEMENT, 0.3)
        ml = st.text("microannulus:\na hairline gap", 6.0, -0.5, 0.22, P.BAD, 0.4, kind="bold")
        st.fade_in([pipe, gap, cem, ml], s[5], 0.5)
        # combine
        chk = []
        for i, t in enumerate(("returns", "volumes", "bump pressure", "pressure test")):
            chk.append(st.text("✓ " + t, 3.6, -1.9 - 0.45 * i, 0.26, P.SAFE, 0.5, align="l", kind="mono"))
        st.fade_in(st.text("combine the evidence:", 3.6, -1.35, 0.26, P.TEXT, 0.5, align="l", kind="bold"), s[6], 0.5)
        for i, c in enumerate(chk):
            st.fade_in(c, s[6] + 0.8 + 0.6 * i, 0.3)


def build(st, tl):
    F.header(st, tl)
    F.well_strip(st, 0.0, tl.dur, strings=["30in conductor", "20in surface casing", "13-3/8in intermediate", "9-5/8in intermediate"], marker=M.TD)
    beat_jobs(st, tl)
    beat_utube(st, tl)
    beat_displacement(st, tl)
    beat_slurry(st, tl)
    beat_danger(st, tl)
    beat_logs(st, tl)
