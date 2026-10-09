"""Ch 6: Beyond the coil: snubbing, bullheading and rigs.

6.01 the snubbing unit: two slip sets, jacks, jointed pipe pushed in a few metres at a time; pipe-light then pipe-heavy
6.02 bullheading: pumping down the tubing pushes the well fluids into the reservoir ahead of it
6.03 the rig workover: kill, check, plugs, tree off / BOP on, pull tubing, repair, run new, tree on; weeks and kill-fluid damage
"""
from __future__ import annotations
import math

from scenes.common import palette as P, model as M, furniture as F
from scenes.common import kit as K

TITLE = "Beyond the coil: snubbing, bullheading and rigs"


# ====================================================================================================== 6.01
def b601(st, tl):
    b = tl["6.01"]
    s = b.sent
    with st.span(b.start, b.end):
        cx = -3.9
        y_hi, y_lo = 2.3, 1.1
        # frame: BOP stack, fixed slips, jacks, travelling plate with slips; pipe with joints
        bop = [st.rect(cx, -2.55, 1.9, 1.3, P.STEEL_DK, 0.4, role="steel"), st.rect(cx, -2.55, 0.5, 1.3, P.BG, 0.42),
               st.rect(cx - 1.15, -2.55, 0.5, 0.35, P.STEEL, 0.38, role="steel"), st.rect(cx + 1.15, -2.55, 0.5, 0.35, P.STEEL, 0.38, role="steel")]
        fixed_h = st.rect(cx, -0.75, 1.7, 0.7, P.STEEL_DK, 0.4, role="steel")
        fixed_bore = st.rect(cx, -0.75, 0.5, 0.7, P.BG, 0.42)
        jack_out = [st.rect(cx - 1.6, 0.5, 0.3, 1.6, P.STEEL_DK, 0.4, role="steel"), st.rect(cx + 1.6, 0.5, 0.3, 1.6, P.STEEL_DK, 0.4, role="steel")]
        rods = [st.rect(cx - 1.6, -0.3, 0.14, y_hi + 0.3, P.STEEL, 0.45, anchor="b", role="steel"), st.rect(cx + 1.6, -0.3, 0.14, y_hi + 0.3, P.STEEL, 0.45, anchor="b", role="steel")]
        plate = st.rect(cx, y_hi, 3.6, 0.28, P.PANEL2, 0.45, role="solid")
        pipe = st.rect(cx, 0.0, 0.4, 7.0, P.STEEL, 0.5, role="steel")
        joints = [st.rect(cx, 3.2 - k * 1.1, 0.5, 0.14, P.STEEL_DK, 0.52, role="steel") for k in range(7)]
        fs = [st.rect(cx - 0.3, -0.75, 0.3, 0.5, P.WARN, 0.55, role="solid"), st.rect(cx + 0.3, -0.75, 0.3, 0.5, P.WARN, 0.55, role="solid")]
        ts = [st.rect(cx - 0.75, y_hi, 0.3, 0.5, "#ff8a5c", 0.55, role="solid"), st.rect(cx + 0.75, y_hi, 0.3, 0.5, "#ff8a5c", 0.55, role="solid")]
        sw = [st.rect(cx, 3.9, 0.9, 0.35, P.PRIMARY_B, 0.55, role="flat"), st.rect(cx, 3.9, 0.12, 0.35, P.WARN, 0.6, role="solid")]
        K.show(st, bop + [fixed_h, fixed_bore] + jack_out + [plate, pipe] + joints + fs + ts, b.start + 0.2, None, 0.6)
        K.show(st, rods, b.start + 0.2, None, 0.6)
        # labels
        lt = K.callout(st, "travelling slips on the jacks", 0.2, 2.3, cx + 0.95, 2.3, size=0.21, align="l")
        lf = K.callout(st, "fixed slips", 0.2, -0.75, cx + 0.95, -0.75, size=0.21, align="l")
        lb = K.callout(st, "BOP stack", 0.2, -2.55, cx + 1.45, -2.55, size=0.21, align="l")
        K.show(st, lt, b.word(3, "two sets of slips"), s[4], 0.4)
        K.show(st, lf, b.word(3, "one fixed"), s[4], 0.4)
        K.show(st, lb, s[1], s[3], 0.4)
        # sentence 2: the pipe can be rotated (a swivel at the top)
        K.show(st, sw, s[2] - 0.2, s[3], 0.4)
        st.rotate(sw[1], s[2], s[3], 360 * 3)
        rt = K.tag(st, 0.2, 3.7, "stiff jointed pipe: can be rotated, carries heavy loads", color=P.SAFE, fg=P.BG, size=0.2, z=0.9, align="l")
        K.show(st, rt, s[2] + 0.3, s[3] - 0.2, 0.4)
        # sentence 4: two stroke cycles
        pipe_parts = [pipe] + joints

        def grip(objs, sd_open, t0, t1):
            for o, sd in zip(objs, (-1, 1)):
                st.move(o, t0, t1, dx=-sd * (0.45 if sd_open else -0.45) * 0 + (0.0))
        # blocks: grip = x +- 0.3 ; open = x +- 0.75
        def travelling(t0, t1, closed):
            st.move(ts[0], t0, t1, to=(cx - (0.3 if closed else 0.75), st.state[ts[0]]["loc"][1]))
            st.move(ts[1], t0, t1, to=(cx + (0.3 if closed else 0.75), st.state[ts[1]]["loc"][1]))

        def fixed(t0, t1, closed):
            st.move(fs[0], t0, t1, to=(cx - (0.3 if closed else 0.75), -0.75))
            st.move(fs[1], t0, t1, to=(cx + (0.3 if closed else 0.75), -0.75))
        # initial state: fixed slips hold the pipe (pressure pushes it out), travelling slips open
        fixed(b.start + 0.3, b.start + 0.4, True)
        travelling(b.start + 0.3, b.start + 0.4, False)
        t0 = s[4] + 0.2
        for k in range(2):
            T = t0 + k * 7.0
            travelling(T, T + 0.4, True)
            fixed(T + 0.5, T + 0.9, False)
            # jacks push down
            st.move([plate] + ts, T + 1.0, T + 3.0, dy=-(y_hi - y_lo), interp="LINEAR")
            for r in rods:
                st.scale_to(r, T + 1.0, T + 3.0, sy=y_lo + 0.3, interp="LINEAR")
            st.move(pipe_parts, T + 1.0, T + 3.0, dy=-(y_hi - y_lo), interp="LINEAR")
            fixed(T + 3.1, T + 3.5, True)
            travelling(T + 3.6, T + 4.0, False)
            # jacks retract
            st.move([plate] + ts, T + 4.2, T + 6.2, dy=+(y_hi - y_lo), interp="LINEAR")
            for r in rods:
                st.scale_to(r, T + 4.2, T + 6.2, sy=y_hi + 0.3, interp="LINEAR")
        cyc = K.note(st, "one grips while the other releases;\nthe pipe moves a few metres at a time", 0.2, 1.2, 0.21, P.TEXT, align="l")
        K.show(st, cyc, s[4] + 0.3, s[5] - 0.2, 0.4)
        # sentence 5: pipe-light, balance point, pipe-heavy
        bar_y = -1.6
        light = st.rect(1.7, bar_y, 3.0, 0.45, P.SAFE, 0.5, role="pill")
        heavy = st.rect(4.8, bar_y, 3.0, 0.45, P.PORE, 0.5, role="pill")
        lt1 = st.text("pipe-light: pushed in", 1.7, bar_y, 0.2, P.BG, 0.6, kind="bold")
        lt2 = st.text("pipe-heavy: weight held", 4.8, bar_y, 0.2, P.BG, 0.6, kind="bold")
        mk = st.circle(0.3, bar_y + 0.55, 0.14, P.WARN, 0.8, role="orb")
        bp = K.note(st, "balance point: slips reversed", 3.25, bar_y - 0.6, 0.22, P.WARN, align="c")
        K.show(st, [light, heavy, lt1, lt2, mk], s[5] - 0.2, None, 0.4)
        st.move(mk, s[5] + 0.3, s[5] + 4.0, dx=5.9, interp="LINEAR")
        K.show(st, bp, b.word(5, "balance point"), None, 0.4)


# ====================================================================================================== 6.02
def b602(st, tl):
    b = tl["6.02"]
    s = b.sent
    with st.span(b.start, b.end):
        cx = -3.9
        top, bot = 3.0, -3.0
        tub = [st.rect(cx - 0.3, (top + bot) / 2, 0.1, top - bot, P.STEEL, 0.4, role="steel"), st.rect(cx + 0.3, (top + bot) / 2, 0.1, top - bot, P.STEEL, 0.4, role="steel")]
        oil = st.rect(cx, (top + bot) / 2, 0.5, top - bot, P.OIL, 0.3, alpha=0.8)
        cas = [st.rect(cx - 0.85, (top + bot) / 2, 0.1, top - bot, P.STEEL_DK, 0.3, role="steel"), st.rect(cx + 0.85, (top + bot) / 2, 0.1, top - bot, P.STEEL_DK, 0.3, role="steel")]
        res = [st.rect(cx - 2.0, -2.4, 2.2, 1.6, P.SAND, 0.1), st.rect(cx + 2.0, -2.4, 2.2, 1.6, P.SAND, 0.1)]
        pf = [st.rect(cx + sd * 1.0, y, 0.7, 0.08, P.BG, 0.35, role="hole") for sd in (-1, 1) for y in (-1.9, -2.4, -2.9)]
        st.fade_in(tub + [oil] + cas + res + pf, b.start + 0.2, 0.5)
        # pump at the surface
        pump = [st.rect(cx - 2.2, 3.4, 1.6, 0.8, "#2b3b57", 0.4, role="solid"), st.text("pump", cx - 2.2, 3.4, 0.2, P.TEXT, 0.5)]
        hose = st.line([(cx - 1.4, 3.4), (cx - 0.3, 3.4), (cx, 3.2)], P.STEEL, 0.06, 0.4)
        K.show(st, pump + [hose], s[1] - 0.2, None, 0.5)
        # the fluid slug pushes the oil ahead of it, into the reservoir
        slug = st.rect(cx, top, 0.5, 0.001, P.KILL_MUD, 0.35, anchor="t")
        t1 = s[1] + 0.5
        st.scale_to(slug, t1, t1 + 5.0, sy=top - bot - 0.6, interp="LINEAR")
        st.scale_to(oil, t1, t1 + 5.0, sy=0.8, interp="LINEAR")
        st.move(oil, t1, t1 + 5.0, dy=-(top - bot - 0.8) / 2, interp="LINEAR")
        for sd in (-1, 1):
            st.flow([(cx + sd * 0.4, -2.4), (cx + sd * 2.4, -2.4)], t1 + 3.0, s[3] - 0.5, P.OIL, n=6, speed=0.8, r=0.05, jitter=0.15)
        fl = K.tag(st, cx + 1.1, -0.4, "fluid pushes the oil back into the reservoir", color=P.KILL_MUD, fg=P.BG, size=0.2, z=0.9, align="l")
        K.show(st, fl, s[1] + 0.8, s[3] - 0.3, 0.4)
        # pump pressure gauge with the fracture limit
        g = K.dial(st, cx + 3.6, 2.8, 0.55, t1, t1 + 4.0, 210, 85, color=P.WARN)
        gl = st.text("pump pressure", cx + 3.6, 2.05, 0.19, P.MUTED, 0.6)
        lim = st.rect(cx + 3.6 + 0.0, 3.55, 0.05, 0.001, P.BAD, 0.6)
        K.show(st, g + [gl], s[1] + 0.5, None, 0.4)
        # three outcomes (sentence 2)
        outs = [("kill the well", b.word(2, "kill a well")), ("place a scale inhibitor deep in the rock", b.word(2, "scale inhibitor")), ("squeeze cement into leak paths", b.word(2, "squeeze cement"))]
        for i, (txt, t) in enumerate(outs):
            g_ = K.tag(st, 1.2, 1.7 - i * 0.7, txt, color=P.SAFE, fg=P.BG, size=0.23, z=0.9, align="l")
            K.show(st, g_, t, None, 0.4)
        ch = K.tag(st, 1.2, -0.7, "cheap and fast: nothing enters the well but liquid", color=P.PRIMARY_B, fg=P.BG, size=0.22, z=0.9, align="l")
        K.show(st, ch, s[3], None, 0.4)
        l1 = K.tag(st, 1.2, -1.45, "no choice of depth", color=P.BAD, fg=P.BG, size=0.22, z=0.9, align="l")
        l2 = K.tag(st, 1.2, -2.2, "the reservoir must be able to take the fluid", color=P.BAD, fg=P.BG, size=0.22, z=0.9, align="l")
        K.show(st, l1, b.word(4, "chosen depth"), None, 0.4)
        K.show(st, l2, b.word(4, "has to be able"), None, 0.4)


# ====================================================================================================== 6.03
def b603(st, tl):
    b = tl["6.03"]
    s = b.sent
    with st.span(b.start, b.end):
        why = ["a leaking tubing string", "a failed packer", "a pump to replace", "a casing leak"]
        wt = [b.word(1, "a leaking"), b.word(1, "a failed packer"), b.word(1, "a pump"), b.word(1, "a casing leak")]
        for i, (txt, t) in enumerate(zip(why, wt)):
            g = K.tag(st, -3.6 + (i % 2) * 4.2, 2.0 - (i // 2) * 0.9, txt, color=P.PANEL2, size=0.26, z=0.8)
            K.show(st, g, t, s[3] - 0.2, 0.4)
        hd = K.tag(st, 0.0, 3.2, "only the completion itself can be reached by pulling it", color=P.WARN, fg=P.BG, size=0.26, z=0.9)
        K.show(st, hd, s[0] + 0.5, s[3] - 0.2, 0.4)
        steps = ["1  kill the well", "2  flow check", "3  plugs set", "4  tree off, BOP on", "5  pull the tubing", "6  repair", "7  run new completion", "8  tree on, bring in"]
        times = [s[3], s[3] + 2.5, s[4], s[5], s[6], b.word(7, "repair"), b.word(7, "new completion"), b.word(7, "brought back")]
        W = 1.78
        for i, (nm, t) in enumerate(zip(steps, times)):
            x = -7.0 + i * 1.98
            y = 1.1
            card = K.card(st, x, y, W, 3.0, P.PANEL, 0.2)
            cap = st.text(nm, x, y - 1.25, 0.17, P.TEXT, 0.5, kind="bold", wrap=14)
            g = card + [cap]
            tb = [st.rect(x - 0.35, y + 0.2, 0.08, 2.0, P.STEEL, 0.3, role="steel"), st.rect(x + 0.35, y + 0.2, 0.08, 2.0, P.STEEL, 0.3, role="steel")]
            if i == 0:
                fill = st.rect(x, y + 1.2, 0.55, 0.001, P.KILL_MUD, 0.35, anchor="t")
                g += tb + [fill]
                st.scale_to(fill, t + 0.5, t + 2.5, sy=2.0, interp="LINEAR")
            elif i == 1:
                g += tb + [st.rect(x, y + 0.2, 0.55, 2.0, P.KILL_MUD, 0.3)]
                dl = K.dial(st, x, y + 0.5, 0.45, t, t + 0.01, 210, 210, color=P.SAFE)
                g += dl
                ck = K.check(st, x, y - 0.4, t + 0.8)
                g += ck
            elif i == 2:
                g += tb + [st.rect(x, y + 0.2, 0.55, 2.0, P.KILL_MUD, 0.3), st.rect(x, y + 0.6, 0.6, 0.3, P.STEEL, 0.5, role="steel"), st.rect(x, y - 0.4, 0.6, 0.3, P.STEEL, 0.5, role="steel")]
            elif i == 3:
                tr = K.dry_tree(st, x, y - 0.9, 0.5)
                bp = [st.rect(x, y + 0.6, 1.1, 0.7, P.STEEL_DK, 0.5, role="steel"), st.rect(x, y + 0.6, 0.3, 0.7, P.BG, 0.52), st.rect(x - 0.35, y + 0.6, 0.3, 0.2, P.WARN, 0.55), st.rect(x + 0.35, y + 0.6, 0.3, 0.2, P.WARN, 0.55)]
                g += tb + tr.parts + tr.gates
                st.move(tr.parts + tr.gates, t + 0.5, t + 1.5, dy=+1.3)
                K.show(st, bp, t + 1.2, None, 0.4)
            elif i == 4:
                segs = [st.rect(x, y + 1.1 - k * 0.4, 0.16, 0.34, P.STEEL, 0.5, role="steel") for k in range(5)]
                g += [st.rect(x, y - 0.2, 0.4, 0.2, P.STEEL_DK, 0.45, role="solid")] + segs
                st.move(segs, t + 0.8, t + 3.0, dy=0.0)
                st.move(segs, t + 0.8, t + 3.0, dx=0.55, interp="LINEAR")
            elif i == 5:
                g += tb + [st.rect(x, y + 0.2, 0.7, 0.4, P.RUBBER, 0.5, role="solid")]
                ck = K.check(st, x, y - 0.3, t + 0.5)
                g += ck
            elif i == 6:
                segs = [st.rect(x - 0.55, y + 1.1 - k * 0.4, 0.16, 0.34, P.STEEL, 0.5, role="steel") for k in range(5)]
                g += tb + segs
                st.move(segs, t + 0.8, t + 3.0, dx=0.55, interp="LINEAR")
            else:
                tr = K.dry_tree(st, x, y - 0.9, 0.5)
                g += tb + tr.parts + tr.gates + [st.rect(x, y + 0.2, 0.3, 2.0, P.OIL, 0.35, alpha=0.9)]
            K.show(st, g, t - 0.3, None, 0.5)
        # the calendar strip: it can take weeks; the kill fluid lowers productivity
        wk = []
        for k in range(8):
            wk.append(st.rect(-6.3 + k * 1.0, -1.75, 0.9, 0.5, P.PANEL2, 0.4, role="pill"))
            wk.append(st.text(f"wk {k + 1}", -6.3 + k * 1.0, -1.75, 0.16, P.MUTED, 0.5))
        cl = K.note(st, "it can take weeks", -3.0, -2.35, 0.24, P.WARN, align="c")
        K.show(st, wk, s[8] - 0.3, None, 0.3)
        for k in range(8):
            st.recolor(wk[2 * k], s[8] + 0.2 * k, s[8] + 0.2 * k + 0.4, P.WARN)
        K.show(st, cl, s[8] + 0.3, None, 0.4)
        # productivity dips with the kill fluid and recovers only partly
        pb = st.rect(5.0, -1.75, 3.0, 0.4, P.PANEL2, 0.4, role="pill")
        pf = st.rect(3.5, -1.75, 3.0, 0.3, P.SAFE, 0.5, anchor="l", role="flat")
        pl = K.note(st, "productivity", 5.0, -1.2, 0.19, P.MUTED, align="c")
        K.show(st, [pb, pf] + pl, s[9] - 0.3, None, 0.4)
        st.scale_to(pf, s[9], s[9] + 1.0, sx=1.9)
        st.recolor(pf, s[9], s[9] + 1.0, P.BAD)
        pk = K.note(st, "kill fluid may leave the well weaker", 5.0, -2.35, 0.2, P.BAD, align="c")
        K.show(st, pk, b.word(9, "may reduce"), None, 0.4)
        fin = K.tag(st, -2.0, -3.3, "so it is done only when it must be", color=P.SAFE, fg=P.BG, size=0.26, z=0.9)
        K.show(st, fin, s[10], None, 0.5)


def build(st, tl):
    F.header(st, tl)
    b601(st, tl)
    b602(st, tl)
    b603(st, tl)
