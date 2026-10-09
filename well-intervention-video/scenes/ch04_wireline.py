"""Ch 4: Wireline: the thin line that does the work.

4.01 three kinds of wireline: slickline, braided line, electric line (cross-sections, what each can do, strength ordering)
4.02 a slickline spread: drum, measuring head, sheave, stuffing box; the weight trace is the operator's only window
4.03 the toolstring: rope socket, stem, jars, knuckle joint, running / pulling tool
4.04 how a mechanical jar works: pull, the wire stretches, release, the stem strikes; jar down
4.05 setting and pulling a plug on a lock mandrel in a landing nipple (equalise first)
4.06 changing a gas-lift valve with a kick-over tool in a side-pocket mandrel
4.07 other slickline jobs, and the limits: it cannot push or pump, and gravity runs out with inclination
4.08 electric line: logging with a casing collar locator; perforating with shaped charges
4.09 e-line also sets plugs and cuts pipe; tractors; beyond that, a pipe that can be pushed
4.10 the wireline scorecard
"""
from __future__ import annotations
import math

from scenes.common import palette as P, model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common import kit as K
from scenes.common import insets as I
from scenes.common import tools as T

TITLE = "Wireline: the thin line that does the work"


# ====================================================================================================== 4.01
def _cross_section(st, kind, x, y, z=0.6):
    """Wire cross-sections (not to scale). Returns objects."""
    out = []
    if kind == "slick":
        out.append(st.circle(x, y, 0.3, P.WIRE, z, role="disc"))
    elif kind == "braid":
        out.append(st.circle(x, y, 0.17, "#8d9bb0", z, role="disc"))
        for k in range(6):
            a = math.radians(60 * k)
            out.append(st.circle(x + 0.34 * math.cos(a), y + 0.34 * math.sin(a), 0.17, "#8d9bb0", z, role="disc"))
        for k in range(6):
            a = math.radians(60 * k + 30)
            out.append(st.circle(x + 0.6 * math.cos(a), y + 0.6 * math.sin(a), 0.0001, "#8d9bb0", z, role="disc"))
    else:
        for k in range(12):
            a = math.radians(30 * k)
            out.append(st.circle(x + 0.58 * math.cos(a), y + 0.58 * math.sin(a), 0.11, "#8d9bb0", z, role="disc"))
        for k in range(6):
            a = math.radians(60 * k)
            out.append(st.circle(x + 0.38 * math.cos(a), y + 0.38 * math.sin(a), 0.1, "#a9b4c6", z, role="disc"))
        out.append(st.circle(x, y, 0.27, "#e9ecef", z, role="disc"))
        out.append(st.circle(x, y, 0.15, P.COPPER, z + 0.01, role="disc"))
    return out


def b401(st, tl):
    b = tl["4.01"]
    s = b.sent
    with st.span(b.start, b.end):
        xs = [-5.55, -2.4, 0.75]
        names = ["SLICKLINE", "BRAIDED LINE", "ELECTRIC LINE"]
        cards, secs, ttl, desc, tags, bars = [], [], [], [], [], []
        times = [s[1] - 0.3, s[3] - 0.3, s[4] - 0.3]
        dtxt = ["a single solid strand", "stranded, like a rope", "braided, with conductors in the core"]
        kinds = ["slick", "braid", "eline"]
        tagset = [[("pull", P.PORE), ("push by weight", P.PORE), ("hammer", P.PORE)],
                  [("stronger", P.SAFE), ("heavy fishing", P.SAFE), ("needs grease head", P.GREASE)],
                  [("power down", P.COPPER), ("data up", P.COPPER), ("logs, perforates", P.COPPER)]]
        tag_t = [[s[2], s[2] + 0.5, s[2] + 1.0], [s[3] + 0.8, s[3] + 1.6, s[3] + 2.6], [s[5], s[5] + 0.5, s[5] + 1.2]]
        strength = [0.28, 1.0, 0.85]
        for i in range(3):
            x = xs[i]
            c = K.card(st, x, 0.0, 3.0, 5.7, P.PANEL, 0.2)
            t = st.text(names[i], x, 2.4, 0.3, P.TEXT, 0.5, kind="bold")
            sec = _cross_section(st, kinds[i], x, 1.2)
            d = K.note(st, dtxt[i], x, 0.2, 0.2, P.MUTED, align="c", wrap=22)
            tg = []
            for j, (lab, col) in enumerate(tagset[i]):
                g = K.tag(st, x, -0.55 - j * 0.58, lab, color=col if col != P.GREASE else P.GREASE, fg=P.BG, size=0.2, z=0.7)
                K.show(st, g, tag_t[i][j], None, 0.35)
                tg.append(g)
            K.show(st, c + [t] + sec + d, times[i], None, 0.5)
            # relative strength bar
            lab = st.text("breaking load (ordering only)", x, -2.2, 0.16, P.MUTED, 0.5)
            back = st.rect(x, -2.5, 2.4, 0.2, P.PANEL2, 0.45, role="pill")
            bar = st.rect(x - 1.2, -2.5, 0.01, 0.2, P.SAFE, 0.55, anchor="l", role="flat")
            K.show(st, [lab, back, bar], s[6] - 0.3, None, 0.4)
            st.scale_to(bar, s[6] + 0.1 + 0.4 * i, s[6] + 1.0 + 0.4 * i, sx=2.4 * strength[i])
        note = K.note(st, "cross-sections not to scale", -2.4, -3.35, 0.17, P.MUTED, align="c")
        st.fade_in(note, s[1], 0.5)


# ====================================================================================================== 4.02
def b402(st, tl):
    b = tl["4.02"]
    s = b.sent
    with st.span(b.start, b.end):
        # winch drum + power pack + measuring head + sheave + stack
        dx, dy = -6.0, -1.7
        skid = [st.rect(dx + 0.7, -3.05, 4.2, 0.35, P.STEEL_DK, 0.3)]
        dr = K.drum(st, dx, dy, 0.95, turns=5)
        pack = [st.rect(-3.9, -2.4, 1.2, 1.1, "#2b3b57", 0.35, role="solid"), st.text("hydraulic\npower", -3.9, -2.4, 0.17, P.TEXT, 0.4)]
        mh_x, mh_y = -2.3, -0.1
        wheels = [st.circle(mh_x, mh_y + 0.28, 0.24, P.STEEL_DK, 0.5, role="solid"), st.circle(mh_x, mh_y - 0.28, 0.24, P.STEEL_DK, 0.5, role="solid")]
        mh_b = st.rect(mh_x, mh_y, 0.8, 1.4, P.PANEL2, 0.35, role="card")
        sh_x, sh_y, sh_r = 4.0, 2.55, 0.32
        sheave = [st.circle(sh_x, sh_y, sh_r, P.STEEL_DK, 0.5, role="solid"), st.circle(sh_x, sh_y, 0.07, P.STEEL, 0.55, role="disc")]
        chain = st.line([(sh_x, sh_y - sh_r), (sh_x, 1.75)], P.STEEL, 0.04, 0.45, role="hair")
        tx, ty0 = 4.4, -2.75
        tree = K.dry_tree(st, tx, ty0, 0.9)
        pce = K.pce_stack(st, tx, tree.top, 0.9, tube_h=1.3)
        base = skid + dr.body + dr.turns + pack + wheels + [mh_b] + sheave + [chain] + tree.parts + tree.gates + pce.parts
        st.fade_in(base, b.start + 0.2, 0.6)
        st.rotate(dr.body[1:], s[1], s[1] + 8.0, 360 * 4)
        # the wire path
        path = [(dx + 0.2, dy + 0.95), (mh_x - 0.0, mh_y + 0.52), (mh_x, mh_y - 0.0), (sh_x - 0.2, sh_y + 0.26), (sh_x + 0.0, sh_y + sh_r), (sh_x + 0.32, sh_y), (tx, pce.top - 0.1), (tx, pce.y_t1)]
        wire = st.line(path, P.WIRE, 0.035, 0.6)
        st.draw_on(wire, s[1] + 0.3, s[2] + 2.5, "LINEAR")
        # callouts as they are named
        lab_d = K.callout(st, "winch drum", -6.3, 0.4, dx, dy + 0.6, size=0.21, align="l")
        lab_m = K.callout(st, "measuring head: depth and tension", -3.8, 1.5, mh_x, mh_y + 0.6, size=0.21, align="l")
        lab_s = K.callout(st, "sheave", 2.2, 3.35, sh_x - 0.2, sh_y + 0.2, size=0.21, align="l")
        lab_b = K.callout(st, "stuffing box", 5.0, 1.55, tx + 0.25, pce.y_box, size=0.21, align="l")
        lab_t = K.callout(st, "lubricator and tree", 5.25, 0.2, tx + 0.15, 0.2, size=0.21, align="l")
        K.show(st, lab_d, b.word(1, "drum"), s[2] - 0.2, 0.4)
        K.show(st, lab_m, b.word(2, "measuring head"), s[3], 0.4)
        K.show(st, lab_s, b.word(2, "sheave"), s[3], 0.4)
        K.show(st, lab_b, b.word(2, "stuffing box"), s[3], 0.4)
        K.show(st, lab_t, b.word(2, "lubricator") if "lubricator" in b.vo else s[2] + 3.0, s[3], 0.4)
        dep = st.counter(mh_x, mh_y - 1.0, s[2] + 1.0, s[3], 0, 2450, "{:,.0f} m", 0.22, P.PORE, 0.6, hold=b.end - 0.2)
        # weight trace: the operator's only window into the well
        ch = Chart(st, -0.1, -3.0, 3.5, 2.2, (0, 10), (40, 140))
        fr = ch.frame(xticks=[], yticks=[], xlabel="time", ylabel="tension", tick_size=0.17, panel=True)
        K.show(st, fr, s[3] - 0.3, None, 0.5)
        pts = []
        for i in range(0, 101):
            t = i / 10
            v = 100.0
            if 3.6 < t < 4.8:
                v += 26 * math.sin(math.pi * (t - 3.6) / 1.2) ** 2
            if t >= 7.2:
                v = 100 - 30 * min((t - 7.2) / 0.15, 1.0)
            v += 1.6 * math.sin(t * 9.0)
            pts.append(ch.pt(t, v))
        trace = st.line(pts, P.WARN, 0.055, 0.5)
        K.show(st, [trace], s[3], None, 0.1)
        st.draw_on(trace, s[5] - 0.2, b.end - 0.6, "LINEAR")
        l1 = st.text("weight of the string", ch.X(1.5), ch.Y(100) + 0.28, 0.18, P.TEXT, 0.6)
        l2 = st.text("snag at a tight spot", ch.X(4.2), ch.Y(128) + 0.28, 0.18, P.WARN, 0.6)
        l3 = st.text("pin shears", ch.X(8.5), ch.Y(70) - 0.28, 0.18, P.BAD, 0.6)
        K.show(st, [l1], b.word(5, "the weight of the string"), None, 0.4)
        K.show(st, [l2], b.word(5, "the snag"), None, 0.4)
        K.show(st, [l3], b.word(5, "the sudden drop"), None, 0.4)
        # "they cannot see the tools": an eye that is crossed out
        ey = [st.ellipse(-5.5, 2.3, 0.45, 0.22, P.TEXT, 0.6, role="disc"), st.circle(-5.5, 2.3, 0.14, P.BG, 0.65, role="disc")]
        K.show(st, ey, s[4] - 0.2, None, 0.4)
        K.xmark(st, -5.5, 2.3, 0.4, s[4] + 0.3)
        et = K.note(st, "cannot see the tools", -5.5, 1.72, 0.19, P.MUTED, align="c")
        K.show(st, et, s[4], None, 0.4)


# ====================================================================================================== 4.03
def b403(st, tl):
    b = tl["4.03"]
    s = b.sent
    with st.span(b.start, b.end):
        cx, SC = -3.9, 1.2
        ytop = 3.2
        wire = st.rect(cx, 3.6, 0.035, 0.7, P.WIRE, 0.65, role="steel")
        ts = T.toolstring(st, cx, ytop, SC)
        names = ["socket", "stem", "jar", "knuckle", "run"]
        times = [s[1], s[2], s[3], s[4], s[5]]
        labels = ["rope socket: ties off the wire", "stem (weight bars): weight and mass", "jars: hammer, up and down", "knuckle joint: bends round curves", "running / pulling tool: does the job"]
        y = ytop
        K.show(st, [wire], b.start + 0.2, None, 0.5)
        for nm, t, lb in zip(names, times, labels):
            c = ts.by[nm]
            K.show(st, c.parts, t - 0.1, None, 0.5)
            yc = y - c.h / 2
            g = K.callout(st, lb, -2.2, yc, cx + c.w / 2 + 0.05, yc, size=0.22, align="l")
            K.show(st, g, t, None, 0.4)
            y -= c.h
        # a dimension bracket: about 6 m in all
        br = st.line([(cx - 0.75, ytop), (cx - 0.9, ytop), (cx - 0.9, ts.y_bottom), (cx - 0.75, ts.y_bottom)], P.MUTED, 0.03, 0.5)
        bt = K.note(st, "a few metres in all", cx - 1.0, (ytop + ts.y_bottom) / 2, 0.19, P.MUTED, align="r")
        K.show(st, [br] + bt, s[5] + 0.5, None, 0.5)
        # job-specific tools at the bottom
        alts = ["plug running tool", "pulling tool", "shifting tool", "bailer", "gauge cutter"]
        for i, a in enumerate(alts):
            g = K.tag(st, -2.2 + (i % 3) * 2.0, -2.35 - (i // 3) * 0.5, a, color=P.PANEL2, size=0.18, z=0.8, align="l")
            K.show(st, g, b.word(5, "whatever the job needs") + 0.2 * i, None, 0.4)


# ====================================================================================================== 4.04
def b404(st, tl):
    b = tl["4.04"]
    s = b.sent
    with st.span(b.start, b.end):
        cx, cy = -4.4, -0.2
        top_h, bot_h = 2.1, -2.1
        # housing with a cavity; fixed to the tool below (the "anvil")
        walls = [st.rect(cx - 0.62, (top_h + bot_h) / 2, 0.26, top_h - bot_h, P.STEEL_DK, 0.3, role="steel"),
                 st.rect(cx + 0.62, (top_h + bot_h) / 2, 0.26, top_h - bot_h, P.STEEL_DK, 0.3, role="steel"),
                 st.rect(cx, (top_h + bot_h) / 2, 1.0, top_h - bot_h, P.BG, 0.2),
                 st.rect(cx, top_h - 0.12, 1.5, 0.24, P.STEEL_DK, 0.32, role="steel"), st.rect(cx, bot_h + 0.1, 1.5, 0.2, P.STEEL_DK, 0.32, role="steel")]
        anvil = [st.rect(cx, bot_h - 0.6, 0.6, 1.0, P.STEEL, 0.4, role="steel")]
        # moving parts: stem above, shaft, collar
        stem = st.rect(cx, 3.0, 0.5, 1.2, P.STEEL, 0.5, role="steel")
        shaft = st.rect(cx, 1.6, 0.3, 3.0, P.STEEL, 0.45, role="steel")
        collar = st.rect(cx, -1.2, 0.84, 0.4, P.STEEL, 0.46, role="steel")
        latch = [st.rect(cx - 0.5, -0.9, 0.14, 0.24, P.WARN, 0.55, role="solid"), st.rect(cx + 0.5, -0.9, 0.14, 0.24, P.WARN, 0.55, role="solid")]
        wire = st.rect(cx, 4.0, 0.035, 0.6, P.WIRE, 0.6, role="steel")
        stroke = st.line([(cx + 0.95, -1.2), (cx + 0.95, 0.9)], P.MUTED, 0.03, 0.4, role="hair")
        st_t = st.text("stroke", cx + 1.2, -0.15, 0.17, P.MUTED, 0.4, align="l")
        st.fade_in(walls + anvil + [stem, shaft, collar, wire] + latch + [stroke, st_t], b.start + 0.2, 0.5)
        mov = [stem, shaft, collar, wire]
        # sentence 3 and 4: pull, the load builds, the wire stretches like a spring
        t_pull0, t_rel = s[3], b.word(5, "Then the jar releases")
        pull = st.arrow(cx + 1.15, 3.6, cx + 1.15, 4.4, P.PORE, 0.08, 0.28, 0.7)
        pl = K.note(st, "pull on the wire", cx + 1.4, 4.0, 0.2, P.PORE, align="l")
        K.show(st, pull + pl, t_pull0, t_rel, 0.4)
        stretch = st.rect(cx - 0.6, 3.5, 0.12, 0.001, P.WARN, 0.6, anchor="b", role="flat")
        sl = K.note(st, "the wire stretches\nlike a spring", cx - 0.9, 3.3, 0.2, P.WARN, align="r")
        K.show(st, [stretch] + sl, s[4] - 0.1, t_rel + 0.5, 0.3)
        st.scale_to(stretch, s[4], t_rel, sy=0.9)
        hold = K.note(st, "the latch holds", cx + 1.2, -0.95, 0.2, P.WARN, align="l")
        K.show(st, hold, s[4], t_rel, 0.4)
        # the release: latch opens, the stem flies up and strikes the top of the stroke
        st.move(latch[0], t_rel - 0.05, t_rel + 0.1, dx=-0.15)
        st.move(latch[1], t_rel - 0.05, t_rel + 0.1, dx=0.15)
        st.move(mov, t_rel, t_rel + 0.22, dy=2.0)
        flash = st.circle(cx, top_h - 0.5, 0.2, P.WARN, 0.9)
        st.fade_in(flash, t_rel + 0.2, 0.05)
        st.scale_to(flash, t_rel + 0.22, t_rel + 0.7, sx=1.1, sy=1.1)
        st.fade_out(flash, t_rel + 0.3, 0.45)
        st.ripple(cx, top_h - 0.5, t_rel + 0.22, t_rel + 1.2, P.WARN, period=0.5, r0=0.2, r1=1.2)
        bl = K.tag(st, cx + 3.2, 1.9, "far harder than the pull", color=P.WARN, fg=P.BG, size=0.21, z=0.9)
        K.show(st, bl, t_rel + 0.3, s[6] - 0.3, 0.3)
        # jar down: slack off, the stem falls onto the tool below
        t_dn = s[6]
        st.move(mov, t_dn + 0.2, t_dn + 1.6, dy=-2.0)
        flash2 = st.circle(cx, bot_h + 0.45, 0.2, P.WARN, 0.9)
        st.fade_in(flash2, t_dn + 1.55, 0.05)
        st.scale_to(flash2, t_dn + 1.6, t_dn + 2.1, sx=1.1, sy=1.1)
        st.fade_out(flash2, t_dn + 1.7, 0.4)
        dn = K.note(st, "slack off: the stem falls", cx + 1.2, 0.2, 0.2, P.PORE, align="l")
        K.show(st, dn, t_dn, t_dn + 2.4, 0.4)
        # the force trace on the right
        ch = Chart(st, 0.2, -2.3, 6.6, 4.4, (0, 12), (0, 110))
        fr = ch.frame(xticks=[], yticks=[], xlabel="time", ylabel="force at the tool", tick_size=0.17)
        K.show(st, fr, t_pull0, None, 0.5)
        pts1 = [ch.pt(0.5, 3), ch.pt(1.0, 3)]
        ramp = st.line([ch.pt(0.8, 3), ch.pt(5.0, 24)], P.PORE, 0.07, 0.5)
        spike = st.line([ch.pt(5.0, 24), ch.pt(5.15, 100), ch.pt(5.4, 12), ch.pt(5.7, 22), ch.pt(6.0, 6), ch.pt(6.4, 3)], P.WARN, 0.07, 0.5)
        down = st.line([ch.pt(6.4, 3), ch.pt(9.3, 3), ch.pt(9.4, 62), ch.pt(9.7, 8), ch.pt(10.0, 3), ch.pt(11.8, 3)], P.PORE, 0.07, 0.5)
        K.show(st, [ramp, spike, down], t_pull0, None, 0.1)
        st.draw_on(ramp, t_pull0 + 0.2, t_rel, "LINEAR")
        st.draw_on(spike, t_rel, t_rel + 0.7, "LINEAR")
        st.draw_on(down, t_dn + 0.1, t_dn + 2.4, "LINEAR")
        c1 = st.text("steady pull", ch.X(2.4), ch.Y(24) + 0.3, 0.2, P.PORE, 0.6)
        c2 = st.text("blow ≫ pull", ch.X(6.9), ch.Y(98), 0.22, P.WARN, 0.6, kind="bold")
        c3 = st.text("downward blow", ch.X(9.4), ch.Y(76), 0.2, P.PORE, 0.6)
        K.show(st, [c1], s[4], None, 0.4)
        K.show(st, [c2], t_rel + 0.4, None, 0.4)
        K.show(st, [c3], t_dn + 1.6, None, 0.4)
        fin = K.tag(st, 3.5, 3.0, "hundreds of blows, up and down", color=P.SAFE, fg=P.BG, size=0.26, z=0.9)
        K.show(st, fin, s[7], None, 0.5)


def build(st, tl):
    F.header(st, tl)
    b401(st, tl)
    b402(st, tl)
    b403(st, tl)
    b404(st, tl)
    import importlib
    for name in ("x_ch04b", "x_ch04c"):
        try:
            importlib.import_module("scenes." + name).build(st, tl)
        except ModuleNotFoundError as e:
            if name not in str(e):
                raise
