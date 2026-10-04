"""Ch 8: Formation evaluation: discovery or dry hole? Includes the pressure-gradient / free-water-level reveal.

Every curve, saturation, contact and thickness shown here is computed in scenes/common/logs.py (synthetic data)."""
from __future__ import annotations
import math
import random

from scenes.common import palette as P, well_model as M, furniture as F, logs as L
from scenes.common.chart import Chart
from scenes.common.shapes import Cutaway, pill, loop_move

TITLE = "Formation evaluation: discovery or dry hole?"
LG = L.generate()


def _dec(arr, k=2):
    return arr[::k]


# ---------------------------------------------------------------- 8.01 the ladder of measurements
def beat_ladder(st, tl):
    b = tl["8.01"]
    s = b.sent
    with st.span(b.start, b.end):
        rows = [("mud log", 1.0, 0.25, 0.1), ("logging while drilling", 0.9, 0.4, 0.3), ("wireline logs", 0.6, 0.6, 0.45),
                ("pressures + samples", 0.4, 0.8, 0.55), ("core", 0.2, 0.9, 0.7), ("well test", 0.1, 1.0, 1.0)]
        head = [st.text("speed", 2.0, 3.3, 0.24, P.PORE, 0.3, kind="bold"), st.text("certainty", 4.2, 3.3, 0.24, P.SAFE, 0.3, kind="bold"),
                st.text("cost", 6.4, 3.3, 0.24, P.WARN, 0.3, kind="bold")]
        st.fade_in(head, s[1], 0.5)
        for i, (name, sp, ce, co) in enumerate(rows):
            y = 2.4 - 1.0 * i
            t = s[2] + 0.5 + 0.9 * i
            lab = st.text(name, -5.9, y, 0.3, P.TEXT, 0.3, align="l", kind="bold")
            st.fade_in(lab, t, 0.4)
            for x0, v, col in ((0.8, sp, P.PORE), (3.0, ce, P.SAFE), (5.2, co, P.WARN)):
                tr = st.rect(x0, y, 2.0, 0.28, P.PANEL2, 0.1, anchor="l")
                bar = st.rect(x0, y, 0.0001, 0.28, col, 0.2, anchor="l")
                st.fade_in(tr, t, 0.3)
                st.scale_to(bar, t + 0.2, t + 0.9, sx=2.0 * v)
        ar = st.arrow(-6.1, 3.0, -6.1, -2.9, P.MUTED, 0.05, 0.25, 0.3)
        st.fade_in(ar, s[2], 0.5)
        fx = st.text("fast, cheap, uncertain  →  slow, costly, definitive", 0.8, -3.6, 0.28, P.WARN, 0.3, kind="bold")
        st.fade_in(fx, s[2] + 4.0, 0.6)


# ---------------------------------------------------------------- 8.02 mud log + lag time
def beat_mudlog(st, tl):
    b = tl["8.02"]
    s = b.sent
    rnd = random.Random(2)
    with st.span(b.start, b.end):
        yt, yb = 3.2, -3.1
        cut = Cutaway(st, -4.6, yt, yb, hole_w=1.6, pipe_w=0.5, rock_w=1.0, wall=0.05)
        base = cut.draw(pipe_bottom=yb + 0.4)
        mud = [cut.static_gap("l", P.MUD, yt, yb, 0.03), cut.static_gap("r", P.MUD, yt, yb, 0.03), cut.static_bore(P.MUD, yt, yb + 0.4, 0.03)]
        bit = st.poly([(-4.95, yb + 0.4), (-4.25, yb + 0.4), (-4.6, yb + 0.05)], P.WARN, 0.3)
        st.fade_in(base + mud + [bit], s[0], 0.5)
        st.fade_in(st.text("mud log", -1.9, 3.7, 0.32, P.TEXT, 0.3, kind="bold"), s[0], 0.5)
        # UV tray
        tray = st.rect(0.8, 2.0, 4.2, 2.0, P.PANEL, 0.0)
        glow = [st.circle(-0.4 + 0.6 * i, 1.9 + 0.3 * math.sin(i), 0.13, "#d9d9d9" if i % 3 else "#fff27a", 0.3) for i in range(6)]
        uvl = st.text("under ultraviolet light, oil glows", 0.8, 3.15, 0.24, P.WARN, 0.3, kind="bold")
        st.fade_in([tray, uvl] + glow[:2], s[1], 0.5)
        for i, g in enumerate(glow[2:]):
            st.fade_in(g, s[1] + 0.8 + 0.4 * i, 0.3)
        st.recolor(glow[0::3], s[1] + 2.0, s[1] + 2.8, "#fff27a")
        # chromatograph
        c = Chart(st, -0.9, -3.0, 4.4, 3.0, (0, 6), (0, 10))
        fr = c.frame(xticks=[], yticks=[], xlabel="C1   C2   C3   C4   C5", ylabel="gas", grid=False)
        bars = []
        for i, h in enumerate((9.0, 4.2, 2.6, 1.3, 0.6)):
            bars.append(st.rect(c.X(0.6 + i), c.Y(0), 0.45, 0.0001, P.GAS, 0.3, anchor="b"))
        gt = st.text("gas chromatograph", c.X(3.0), c.Y(10) + 0.3, 0.26, P.GAS, 0.3, kind="bold")
        st.fade_in(fr + [gt], s[2], 0.4)
        for i, (bb, h) in enumerate(zip(bars, (9.0, 4.2, 2.6, 1.3, 0.6))):
            st.fade_in(bb, s[2] + 0.3, 0.1)
            st.scale_to(bb, s[2] + 0.4 + 0.2 * i, s[2] + 0.9 + 0.2 * i, sy=c.Y(h) - c.Y(0))
        # lag: a cutting travels up the annulus slowly
        gx = (cut.gap_r[0] + cut.gap_r[1]) / 2
        cp = st.circle(gx, yb + 0.5, 0.11, "#fff27a", 0.5)
        st.fade_in(cp, s[3], 0.3)
        st.move(cp, s[3] + 0.5, b.end - 0.6, to=(gx, yt - 0.2), interp="LINEAR")
        lag = st.text("lag time = annulus volume ÷ flow rate", 3.7, -1.0, 0.24, P.TEXT, 0.4, kind="mono", align="c")
        old = st.text("cuttings are old news\nwhen they arrive", 3.7, -2.0, 0.28, P.WARN, 0.4, kind="bold")
        st.fade_in([lag, old], s[3] + 0.5, 0.5)


# ---------------------------------------------------------------- 8.03 LWD log tracks drawn as the bit passes
def _track(st, x, w, key_fn, xr, color, title, t0, t1, yr=(L.Z0, L.Z1), y=-3.0, h=5.8, log=False, ticks=None):
    c = Chart(st, x, y, w, h, xr, yr, invert_y=True)
    fr = c.frame(xticks=ticks or [], yticks=[], grid=True, panel=False, tick_size=0.16)
    tt = st.text(title, x + w / 2, y + h + 0.3, 0.22, color, 0.3, kind="bold")
    return c, fr + [tt]


def beat_lwd(st, tl):
    b = tl["8.03"]
    s = b.sent
    with st.span(b.start, b.end):
        zs = _dec(LG.z)
        # depth labels + fluid column
        c0 = Chart(st, -5.8, -3.0, 0.6, 5.8, (0, 1), (L.Z0, L.Z1), invert_y=True)
        dl = [st.text(f"{z:,}", c0.X(0.5), c0.Y(z), 0.18, P.MUTED, 0.3) for z in (3950, 4000, 4050, 4100)]
        st.fade_in(dl, s[0], 0.4)
        # track 1: gamma ray
        c1, f1 = _track(st, -4.8, 3.0, None, (0, 150), P.SAFE, "gamma ray", 0, 0, ticks=[0, 50, 100, 150])
        g1 = c1.curve(_dec(LG.gr), zs, P.SAFE, 0.05, 0.3)
        sh = c1.vline(75, P.GRID, 0.02, 0.1)
        st.fade_in(f1 + [sh], s[0] + 0.5, 0.4)
        st.draw_on(g1, s[1], s[1] + 3.0)
        st.fade_in(c1.label(30, 3960, "sand", 0.2, P.SAND, "l"), s[1] + 1.0, 0.3)
        st.fade_in(c1.label(100, 3938, "shale", 0.2, P.MUTED, "r"), s[1] + 0.5, 0.3)
        # track 2: resistivity (log10)
        c2, f2 = _track(st, -1.2, 3.0, None, (math.log10(0.2), math.log10(300)), P.BAD, "resistivity (log scale)", 0, 0)
        g2 = c2.curve([math.log10(r) for r in _dec(LG.rt)], zs, P.BAD, 0.05, 0.3)
        st.fade_in(f2, s[2] - 0.3, 0.4)
        st.draw_on(g2, s[2], s[2] + 3.5)
        st.fade_in(c2.label(math.log10(40), 3985, "hydrocarbons:\nhigh resistivity", 0.2, P.BAD, "c"), s[2] + 2.0, 0.4)
        # track 3: density / neutron with gas crossover
        c3, f3 = _track(st, 2.4, 3.0, None, (0.45, -0.15), P.PORE, "density (blue)  neutron (amber)", 0, 0)
        # reversed axis: porosity increases to the left
        c3.xr = (0.45, -0.05)
        gd = c3.curve(_dec(LG.dphi), zs, P.PORE, 0.05, 0.3)
        gn = c3.curve(_dec(LG.nphi), zs, P.WARN, 0.05, 0.3)
        gas_pts = [(z, d, n) for z, d, n in zip(LG.z, LG.dphi, LG.nphi) if M.RES_TOP <= z < M.GOC and n < d]
        cross = st.poly([c3.pt(d, z) for z, d, n in gas_pts[::2]] + [c3.pt(n, z) for z, d, n in reversed(gas_pts[::2])], P.GAS, 0.2, 0.5)
        st.fade_in(f3, s[3] - 0.3, 0.4)
        st.draw_on(gd, s[3], s[3] + 3.0)
        st.draw_on(gn, s[3], s[3] + 3.0)
        st.fade_in(cross, s[3] + 2.4, 0.5)
        st.fade_in(st.text("gas crossover", c3.X(0.2), c3.Y(3930), 0.2, P.GAS, 0.5, kind="bold"), s[3] + 2.5, 0.4)
        # mud pulse telemetry
        pulses = []
        for i in range(5):
            r = st.ring(6.3, 0.0, 0.2, 0.04, P.WARN, 0.3, 0.0)
            pulses.append(r)
            t = s[4] + 0.4 + 0.9 * i
            st.fade_in(r, t, 0.1)
            st.move(r, t, t + 1.6, dy=2.2)
            st.scale_to(r, t, t + 1.6, sx=1.6, sy=1.6)
            st.fade_out(r, t + 1.0, 0.6)
        pipe = st.rect(6.3, 0.0, 0.3, 5.4, P.STEEL, 0.2)
        mp = st.text("mud pulses up the pipe:\na few bits per second", 6.3, -3.3, 0.2, P.WARN, 0.4, kind="bold")
        st.fade_in([pipe, mp], s[4], 0.5)


# ---------------------------------------------------------------- 8.04 Archie: the salty sponge
def beat_archie(st, tl):
    b = tl["8.04"]
    s = b.sent
    rnd = random.Random(21)
    ex = L.archie_example()
    with st.span(b.start, b.end):
        sx, sy = -3.2, 0.4
        sponge = st.rect(sx, sy, 5.2, 4.0, P.SAND, 0.0)
        pores = []
        for i in range(6):
            for j in range(5):
                x = sx - 2.1 + i * 0.84 + rnd.uniform(-0.12, 0.12)
                y = sy - 1.6 + j * 0.8 + rnd.uniform(-0.1, 0.1)
                pores.append(st.circle(x, y, 0.24, P.WATER, 0.2))
        st.fade_in([sponge], s[1], 0.5)
        for i, p in enumerate(pores):
            st.fade_in(p, s[1] + 0.2 + 0.04 * i, 0.2)
        cap = st.text("rock = a sponge soaked in salty water", sx, 3.0, 0.28, P.TEXT, 0.3, kind="bold")
        st.fade_in(cap, s[1], 0.5)
        # current through the salt water
        path_pts = [(sx - 2.5, sy - 1.6), (sx - 2.1, sy - 1.6), (sx - 1.3, sy - 0.8), (sx - 0.4, sy - 0.8), (sx + 0.4, sy), (sx + 1.3, sy), (sx + 2.1, sy + 0.8), (sx + 2.5, sy + 0.8)]
        cur = st.line(path_pts, P.WARN, 0.1, 0.4)
        cl = st.text("current flows through the salt water", sx, -2.1, 0.24, P.WARN, 0.4, kind="bold")
        st.draw_on(cur, s[2], s[2] + 2.0)
        st.fade_in(cl, s[2] + 0.8, 0.4)
        # replace some water with oil: current falls
        oil_idx = [1, 2, 3, 7, 8, 9, 13, 14, 15, 19, 20, 21, 25, 26, 27]
        st.recolor([pores[i] for i in oil_idx], s[3], s[3] + 1.2, P.OIL)
        st.recolor(cur, s[3] + 0.6, s[3] + 1.6, P.MUTED)
        ol = st.text("oil is an insulator: less current", sx, -2.7, 0.24, P.OIL, 0.4, kind="bold")
        st.fade_in(ol, s[3] + 0.8, 0.5)
        # equation + worked example
        card = st.rect(4.2, 0.9, 6.0, 5.4, P.PANEL, 0.0)
        eq = st.text("Sw = ( a · Rw / (φᵐ · Rt) )^(1/n)", 4.2, 2.8, 0.3, P.TEXT, 0.3, kind="mono")
        st.fade_in([card, eq], s[4], 0.5)
        wk = [st.text("worked example (gas zone):", 4.2, 1.8, 0.24, P.MUTED, 0.3, kind="bold"),
              st.text(f"Rw = {ex['rw']:.2f} Ω·m     φ = {ex['phi']:.2f}", 4.2, 1.1, 0.26, P.TEXT, 0.3, kind="mono"),
              st.text(f"Rt = {ex['rt']:.0f} Ω·m     (a = 1, m = n = 2)", 4.2, 0.5, 0.26, P.TEXT, 0.3, kind="mono"),
              st.text(f"Sw ≈ {ex['sw']:.2f}   →   80 % gas", 4.2, -0.4, 0.34, P.GAS, 0.3, kind="bold")]
        for i, t in enumerate(wk):
            st.fade_in(t, s[4] + 1.5 + 0.8 * i, 0.4)
        sm = st.text("simplified: fails in shaly sands", 4.2, -2.4, 0.26, P.SIM_BADGE, 0.3, kind="bold")
        st.fade_in(sm, s[5], 0.5)


# ---------------------------------------------------------------- 8.05 THE PRESSURE GRADIENT REVEAL
def beat_gradients(st, tl):
    b = tl["8.05"]
    s = b.sent
    data = L.fitted_contacts()
    with st.span(b.start, b.end):
        c = Chart(st, -3.6, -3.0, 6.4, 6.0, (604.0, 620.0), (3940.0, 4125.0), invert_y=True)
        fr = c.frame(xticks=[606, 610, 614, 618], yticks=[3950, 4000, 4050, 4100], xlabel="formation pressure (bar)", ylabel="depth (m)", fx="{:g}")
        st.fade_in(fr, s[2] - 0.3, 0.5)
        # wireline tool / probe on the wall at each station
        wall = st.rect(-5.35, (c.Y(3940) + c.Y(4125)) / 2, 0.3, c.Y(3940) - c.Y(4125), P.ROCK, 0.1)
        probe = st.rect(-5.0, c.Y(3955), 0.5, 0.2, P.WARN, 0.4)
        pl = st.text("formation tester:\nprobe on the wall", -5.9, 3.3, 0.2, P.WARN, 0.4, align="l", kind="bold")
        st.fade_in([wall, probe, pl], s[2], 0.5)
        colors = {"gas": P.GAS, "oil": P.OIL, "water": P.WATER}
        dots, t = [], s[2] + 1.2
        prev_y = c.Y(3955)
        for i, (fl, z, p) in enumerate(data["points"]):
            d = st.circle(c.X(p), c.Y(z), 0.1, colors[fl], 0.5)
            dots.append(d)
            ti = t + 0.55 * i
            st.move(probe, ti - 0.35, ti, to=(-5.0, c.Y(z)))
            st.fade_in(d, ti, 0.15)
        t_end = t + 0.55 * len(data["points"])
        # gradient labels
        gl = [pill(st, 5.6, 2.4, "gas:  ~0.25 bar / 10 m", P.PANEL2, P.GAS, 0.24, 0.5, align="c"),
              pill(st, 5.6, 1.5, "oil:  ~0.75 bar / 10 m", P.PANEL2, P.OIL, 0.24, 0.5, align="c"),
              pill(st, 5.6, 0.6, "water:  ~1.0 bar / 10 m", P.PANEL2, P.WATER, 0.24, 0.5, align="c")]
        for i, g in enumerate(gl):
            st.fade_in(g, s[3] + 0.5 + 1.2 * i, 0.4)
        # fitted lines
        lines = {}
        for fl in ("gas", "oil", "water"):
            a, g = data["lines"][fl]
            zr = {"gas": (3950, 3990), "oil": (3992, 4052), "water": (4052, 4115)}[fl]
            pts = [(a + g * z, z) for z in (zr[0], zr[1])]
            lines[fl] = st.line([c.pt(p, z) for p, z in pts], colors[fl], 0.07, 0.4)
            st.draw_on(lines[fl], s[4] + 0.3 * ("gas", "oil", "water").index(fl), s[4] + 0.3 * ("gas", "oil", "water").index(fl) + 1.8)
        st.fade_in(st.text("slopes differ", c.X(618) - 0.1, c.Y(3965), 0.28, P.TEXT, 0.5, align="r", kind="bold"), s[4] + 1.0, 0.4)
        # extend oil and water lines to their intersection: the free-water level
        zf = data["fwl"]
        ao, go = data["lines"]["oil"]
        aw, gw = data["lines"]["water"]
        ext_o = st.dashed(c.pt(ao + go * 4052, 4052), c.pt(ao + go * zf, zf), P.OIL, 0.04, 0.12, 0.08, 0.35)
        pf = ao + go * zf
        mk = st.circle(c.X(pf), c.Y(zf), 0.17, P.TEXT, 0.6)
        fl_line = st.dashed(c.pt(604, zf), c.pt(pf, zf), P.TEXT, 0.04, 0.2, 0.1, 0.3)
        fl_lbl = pill(st, c.X(605.5), c.Y(zf) + 0.4, f"free-water level  ≈ {zf:,.0f} m", P.TEXT, "#0b1220", 0.26, 0.7, align="l")
        st.fade_in(ext_o + [mk] + fl_line + fl_lbl, s[5], 0.6)
        nv = st.text("a contact the well never had to cross", 5.6, -2.6, 0.26, P.WARN, 0.6, kind="bold")
        st.fade_in(nv, s[5] + 1.0, 0.6)


# ---------------------------------------------------------------- 8.06 samples, compartments, FWL vs OWC
def beat_samples(st, tl):
    b = tl["8.06"]
    s = b.sent
    with st.span(b.start, b.end):
        # sample bottle + optical dial
        card1 = st.rect(-4.5, 0.4, 3.8, 5.0, P.PANEL, 0.0)
        bottle = st.rect(-4.9, 0.0, 0.8, 1.9, P.PANEL2, 0.2)
        fill = st.rect(-4.9, -0.95, 0.7, 0.0001, P.OIL, 0.25, anchor="b")
        dial = st.ring(-3.7, 0.9, 0.5, 0.07, P.MUTED, 0.2)
        nd = st.rect(-3.7, 0.9, 0.45, 0.05, P.WARN, 0.3, anchor="l", rot=150)
        t1 = st.text("fluid samples:\nanalysed downhole\nand in the lab", -4.5, 2.5, 0.24, P.TEXT, 0.3, kind="bold")
        st.fade_in([card1, bottle, dial, nd, t1], s[0], 0.5)
        st.scale_to(fill, s[0] + 0.8, s[0] + 3.0, sy=1.8)
        st.rotate(nd, s[0] + 1.0, s[0] + 3.0, 40)
        # compartments
        card2 = st.rect(0.1, 0.4, 3.8, 5.0, P.PANEL, 0.0)
        c = Chart(st, -1.4, -1.9, 3.0, 3.2, (0, 10), (0, 10), invert_y=True)
        fr = c.frame(xticks=[], yticks=[], xlabel="pressure", ylabel="depth", grid=False, panel=False)
        a = c.curve([2, 4.5], [1.5, 4.5], P.WATER, 0.08, 0.4)
        b2 = c.curve([5.5, 8.0], [5.5, 9.0], P.WATER, 0.08, 0.4)
        off = st.text("offset:\nnot connected", c.X(7.4), c.Y(3.0), 0.2, P.BAD, 0.4, kind="bold")
        t2 = st.text("two sands, two pressure lines", 0.1, 2.5, 0.24, P.TEXT, 0.3, kind="bold")
        st.fade_in([card2, t2] + fr, s[1], 0.5)
        st.draw_on(a, s[1] + 0.5, s[1] + 1.5)
        st.draw_on(b2, s[1] + 1.5, s[1] + 2.5)
        st.fade_in(off, s[1] + 2.5, 0.5)
        # FWL vs OWC
        card3 = st.rect(4.9, 0.4, 3.8, 5.0, P.PANEL, 0.0)
        t3 = st.text("pressure surface vs logs", 4.9, 2.5, 0.24, P.TEXT, 0.3, kind="bold")
        zone = st.rect(4.9, 0.0, 2.6, 0.9, P.OIL, 0.15, alpha=0.4)
        wat = st.rect(4.9, -1.35, 2.6, 1.8, P.WATER, 0.15, alpha=0.55)
        oil = st.rect(4.9, 1.0, 2.6, 1.0, P.OIL, 0.15)
        fw = st.rect(4.9, -0.45, 2.8, 0.06, P.TEXT, 0.4)
        ow = st.rect(4.9, 0.45, 2.8, 0.06, P.WARN, 0.4)
        fl = st.text("FWL: pressure", 6.4, -0.45, 0.2, P.TEXT, 0.5, align="l", kind="bold")
        ol = st.text("OWC: logs", 6.4, 0.45, 0.2, P.WARN, 0.5, align="l", kind="bold")
        cp = st.text("capillary\ntransition", 3.4, 0.0, 0.2, P.MUTED, 0.5, align="r")
        st.fade_in([card3, t3, zone, wat, oil, fw, ow, fl, ol, cp], s[2], 0.5)


# ---------------------------------------------------------------- 8.07 coring + lab tests
def beat_core(st, tl):
    b = tl["8.07"]
    s = b.sent
    with st.span(b.start, b.end):
        # core bit cutting a cylinder
        cx = -4.4
        rock = st.rect(cx, -1.4, 2.8, 2.6, P.SAND, 0.0)
        core = st.rect(cx, -0.1, 0.9, 0.0001, "#d8c08a", 0.2, anchor="t")
        bit = [st.rect(cx - 0.8, 1.6, 0.4, 1.0, "#8fa1b8", 0.3), st.rect(cx + 0.8, 1.6, 0.4, 1.0, "#8fa1b8", 0.3), st.rect(cx, 2.3, 2.0, 0.3, "#8fa1b8", 0.3)]
        st.fade_in([rock] + bit, b.start, 0.5)
        st.move(bit, s[0], s[0] + 3.0, dy=-1.6)
        st.fade_in(core, s[0], 0.2)
        st.move(core, s[0], s[0] + 3.0, dy=0.0)
        st.scale_to(core, s[0], s[0] + 3.0, sy=1.4)
        ct = st.text("a core: a cylinder of rock,\nthe only direct sample", cx, 3.5, 0.24, P.TEXT, 0.4, kind="bold")
        st.fade_in(ct, s[0] + 0.5, 0.5)
        # tray of core pieces
        tray = st.rect(cx, -3.1, 3.4, 0.7, P.PANEL, 0.0)
        pcs = [st.rect(cx - 1.3 + 0.65 * i, -3.1, 0.55, 0.4, "#d8c08a" if i % 2 else "#c8b078", 0.2) for i in range(5)]
        st.fade_in([tray] + pcs, s[0] + 3.0, 0.5)
        # lab results
        lab = [pill(st, -0.2, 2.9, "porosity", P.PANEL2, P.TEXT, 0.26, 0.4, align="l"), pill(st, -0.2, 2.1, "permeability: how easily fluid flows", P.PANEL2, P.PORE, 0.26, 0.4, align="l")]
        st.fade_in(lab[0], s[1], 0.4)
        st.fade_in(lab[1], s[1] + 0.8, 0.4)
        # triaxial: stress-strain + Mohr circle
        c = Chart(st, 1.4, -2.6, 2.6, 3.4, (0, 10), (0, 10))
        fr = c.frame(xticks=[], yticks=[], xlabel="strain", ylabel="stress", grid=False)
        ss = c.curve([0, 1, 2, 3, 4, 5, 6.5, 8, 10], [0, 2.4, 4.6, 6.6, 8.2, 8.9, 8.6, 7.6, 6.6], P.PORE, 0.08, 0.4)
        tx = st.text("triaxial test:\ncalibrates fracture\nand collapse estimates", 2.7, 1.6, 0.22, P.WARN, 0.4, kind="bold")
        st.fade_in(fr + [tx], s[1] + 1.8, 0.4)
        st.draw_on(ss, s[1] + 2.2, s[1] + 5.0)
        mc = [st.ring(6.2, -0.8, 1.0, 0.05, P.COLLAPSE, 0.4), st.line([(4.6, -2.4), (7.8, 0.4)], P.WARN, 0.06, 0.4), st.rect(6.2, -1.8, 3.4, 0.03, P.MUTED, 0.2)]
        mt = st.text("Mohr–Coulomb", 6.2, 1.0, 0.22, P.COLLAPSE, 0.4, kind="bold")
        st.fade_in(mc + [mt], s[1] + 3.0, 0.5)
        wk = st.text("it takes weeks", 6.2, -3.2, 0.34, P.MUTED, 0.4, kind="bold")
        st.fade_in(wk, s[2], 0.5)


# ---------------------------------------------------------------- 8.08 DST
def beat_dst(st, tl):
    b = tl["8.08"]
    s = b.sent
    with st.span(b.start, b.end):
        # test string in cased hole
        cx = -4.8
        csg = [st.rect(cx - 0.8, 0.2, 0.08, 6.4, P.STEEL, 0.2), st.rect(cx + 0.8, 0.2, 0.08, 6.4, P.STEEL, 0.2)]
        string = st.rect(cx, 0.8, 0.28, 5.2, P.STEEL, 0.3)
        packer = st.rect(cx, -1.3, 1.5, 0.35, P.WARN, 0.35)
        perf = [st.arrow(cx + 1.3, -2.4, cx + 0.5, -2.4, P.OIL, 0.07, 0.2, 0.4), st.arrow(cx - 1.3, -2.4, cx - 0.5, -2.4, P.OIL, 0.07, 0.2, 0.4)]
        sand = st.rect(cx, -2.7, 3.6, 0.8, P.SAND, 0.0)
        st.fade_in(csg + [string, packer, sand] + perf[0] + perf[1], s[0], 0.5)
        pl = st.text("temporary completion:\npacker + test string", cx + 0.2, 3.5, 0.22, P.TEXT, 0.4, kind="bold")
        st.fade_in(pl, s[0], 0.5)
        # surface equipment
        sep = st.rect(-1.9, 2.4, 1.4, 0.8, P.PANEL2, 0.3)
        sl = st.text("separator", -1.9, 2.4, 0.2, P.TEXT, 0.4, kind="bold")
        flame = st.poly([(-0.3, 1.9), (0.1, 1.9), (-0.1, 2.9)], P.FRAC, 0.4)
        fl = st.text("burner", -0.1, 1.5, 0.2, P.FRAC, 0.4, kind="bold")
        conn = st.line([(cx, 3.35), (cx, 3.75), (-1.9, 3.75), (-1.9, 2.85)], P.MUTED, 0.06, 0.3)
        st.fade_in([sep, sl, flame, fl, conn], s[0] + 1.0, 0.5)
        # build-up plot
        c = Chart(st, 1.2, -2.8, 4.3, 3.4, (0, 10), (0, 10))
        fr = c.frame(xticks=[], yticks=[], xlabel="time", ylabel="pressure", grid=False)
        tr = c.curve([0, 0.5, 2.5, 4, 4.2, 4.6, 5.4, 7, 10], [9.2, 5.5, 4.9, 4.7, 4.8, 6.2, 8.0, 8.9, 9.2], P.PORE, 0.08, 0.4)
        c.label(2.3, 3.6, "flow", 0.2, P.PORE, "c")
        c.label(7.2, 7.4, "build-up", 0.2, P.PORE, "c")
        st.fade_in(fr, s[0] + 1.5, 0.4)
        st.draw_on(tr, s[0] + 2.0, s[1] + 2.0)
        res = st.text("permeability · near-well damage · boundaries", 3.4, 3.2, 0.24, P.SAFE, 0.4, kind="bold")
        st.fade_in(res, s[1], 0.5)
        # NO: burning + tax
        cost = pill(st, 3.4, -3.55, "costly + burns hydrocarbons:\nemissions controlled and taxed on the NCS", P.NO_BADGE, "#ffffff", 0.24, 0.7)
        st.fade_in(cost, s[2], 0.5)
        alt = st.text("often: logs  ·  pressures  ·  samples instead", 0.5, 4.0, 0.26, P.WARN, 0.4, kind="bold")
        st.fade_in(alt, s[3], 0.5)


# ---------------------------------------------------------------- 8.09 net pay
def beat_netpay(st, tl):
    b = tl["8.09"]
    s = b.sent
    sm = L.summary(LG)
    with st.span(b.start, b.end):
        zs = _dec(LG.z)
        specs = [("shale volume", LG.vsh, (0, 1), L.CUT_VSH, P.MUTED, -5.2), ("porosity", LG.phi, (0.0, 0.35), L.CUT_PHI, P.PORE, -3.0), ("water saturation", LG.sw, (0, 1), L.CUT_SW, P.WATER, -0.8)]
        tracks = []
        for name, arr, xr, cut, col, x in specs:
            c = Chart(st, x, -3.0, 1.8, 5.8, xr, (L.Z0, L.Z1), invert_y=True)
            fr = c.frame(xticks=[], yticks=[], grid=False, panel=False)
            cv = c.curve(_dec(arr), zs, col, 0.05, 0.3)
            cl = c.vline(cut, P.WARN, 0.04, 0.35)
            tt = st.text(name, x + 0.9, 3.15, 0.2, col, 0.3, kind="bold")
            ct = st.text(f"cutoff {cut:g}", x + 0.9, -3.35, 0.18, P.WARN, 0.3)
            st.fade_in(fr + [tt, ct, cl], s[0], 0.4)
            st.draw_on(cv, s[0] + 0.3, s[0] + 2.5)
            tracks.append(c)
        # flag columns, in three passes
        c = tracks[0]
        def flag_col(flags, x, color_fn, label, t):
            parts = []
            run = None
            for z, f, fl in zip(LG.z, flags, LG.fluid):
                key = color_fn(fl) if f else None
                if key != run:
                    if run is not None:
                        parts.append(st.rect(x, (c.Y(run_start) + c.Y(z)) / 2, 0.45, abs(c.Y(run_start) - c.Y(z)), run, 0.3))
                    run, run_start = key, z
            if run is not None:
                parts.append(st.rect(x, (c.Y(run_start) + c.Y(LG.z[-1])) / 2, 0.45, abs(c.Y(run_start) - c.Y(LG.z[-1])), run, 0.3))
            lab = st.text(label, x, 3.3, 0.17, P.TEXT, 0.3, kind="bold")
            st.fade_in(parts + [lab], t, 0.6)
        flag_col(LG.net_sand, 1.3, lambda f: P.SAND, "net\nsand", s[1])
        flag_col(LG.net_res, 2.15, lambda f: "#e08a2e", "net\nreservoir", s[1] + 1.5)
        flag_col(LG.net_pay, 3.0, lambda f: {"gas": P.GAS, "oil": P.OIL}.get(f, P.WATER), "net\npay", s[1] + 3.0)
        # thickness bars
        bars = [("gross", sm["gross"], P.MUTED), ("net sand", sm["net_sand"], P.SAND), ("net reservoir", sm["net_reservoir"], "#e08a2e"), ("net pay", sm["net_pay"], P.OIL)]
        for i, (nm, v, col) in enumerate(bars):
            y = 2.3 - 0.75 * i
            tt = st.text(f"{nm}: {v:.0f} m", 4.1, y + 0.3, 0.2, P.TEXT, 0.3, align="l", kind="bold")
            bar = st.rect(4.1, y, 0.0001, 0.3, col, 0.3, anchor="l")
            st.fade_in(tt, s[1] + 0.6 + 1.2 * i, 0.3)
            st.scale_to(bar, s[1] + 0.8 + 1.2 * i, s[1] + 1.8 + 1.2 * i, sx=3.4 * v / sm["gross"])
        ntg = st.text(f"net-to-gross = net pay / gross\n= {sm['net_pay']:.0f} / {sm['gross']:.0f} = {sm['ntg']:.2f}", 5.7, -1.3, 0.26, P.WARN, 0.4, kind="bold")
        ntg_bg = st.rect(5.7, -1.3, 3.8, 1.1, P.PANEL2, 0.35)
        st.fade_in([ntg_bg, ntg], s[2], 0.5)
        st.fade_in(st.text("cutoffs are illustrative:\nreal ones are field-specific", 5.7, -2.5, 0.22, P.SIM_BADGE, 0.4, kind="bold"), s[3], 0.5)


# ---------------------------------------------------------------- 8.10 the verdict
def beat_verdict(st, tl):
    b = tl["8.10"]
    s = b.sent
    with st.span(b.start, b.end):
        root = pill(st, 0.8, 3.5, "is it a discovery?", P.PANEL2, P.TEXT, 0.4, 0.4)
        st.fade_in(root, s[0], 0.5)
        qs = [("hydrocarbons present?", "shows · logs · samples", s[1], -4.6), ("movable?", "mobility · test", s[2], 0.8), ("how much?", "net pay · contacts · thickness", s[3], 6.2)]
        for t, ev, ts, x in qs:
            box = st.rect(x, 1.5, 4.3, 1.6, P.PANEL, 0.0)
            tt = st.text(t, x, 1.95, 0.3, P.PORE, 0.3, kind="bold")
            ee = st.text(ev, x, 1.1, 0.22, P.MUTED, 0.3)
            ck = st.text("✓", x + 1.9, 1.95, 0.4, P.SAFE, 0.5, kind="mono")
            st.fade_in([box, tt, ee], ts, 0.4)
            st.fade_in(ck, ts + 1.0, 0.3)
        # Sodir definition
        card = st.rect(0.8, -0.8, 12.6, 1.6, P.PANEL2, 0.0)
        q = st.text("discovery  =  testing, sampling or logging has shown the probability of mobile petroleum", 0.8, -0.55, 0.3, P.TEXT, 0.3, kind="bold")
        src = st.text("Norwegian Offshore Directorate (Sodir): technical, not commercial", 0.8, -1.25, 0.22, P.WARN, 0.3, kind="bold")
        st.fade_in([card, q, src], s[4], 0.6)
        dis = pill(st, -2.4, -3.0, "DISCOVERY (technical)", P.SAFE, "#06201c", 0.34, 0.5)
        dry = pill(st, 3.9, -3.0, "DRY HOLE: still data", P.PANEL2, P.TEXT, 0.34, 0.5)
        st.fade_in(dis, s[5], 0.5)
        st.fade_in(dry, s[6], 0.5)


def build(st, tl):
    F.header(st, tl)
    F.well_strip(st, 0.0, tl.dur, strings=[p.name for p in M.programme()], marker=M.TD)
    beat_ladder(st, tl)
    beat_mudlog(st, tl)
    beat_lwd(st, tl)
    beat_archie(st, tl)
    beat_gradients(st, tl)
    beat_samples(st, tl)
    beat_core(st, tl)
    beat_dst(st, tl)
    beat_netpay(st, tl)
    beat_verdict(st, tl)
