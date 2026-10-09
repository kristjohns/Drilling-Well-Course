"""Ch 1: The well, and the work after it.

1.01 the completed well builds up part by part as it is named: casing + cement, tubing, packer, downhole safety valve, tree
1.02 the fittings in the tubing (landing nipple, sliding sleeve, side-pocket mandrel, perforations), each with a close-up
1.03 the life of a well: drill, complete, produce (with interventions), plug and abandon; workover is the heavy loop
1.04 light versus heavy: live well (pressure held at the tree) versus a killed well
1.05 every well declines; an intervention bends the curve up; the cost of the spread decides if it pays
"""
from __future__ import annotations
import math

from scenes.common import palette as P, model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common import kit as K
from scenes.common import insets as I

TITLE = "The well, and the work after it"


def _wlabel(st, w, md, text, x, color=P.PANEL2, size=0.21, side="r", z=1.0, target_dx=None, fg=P.TEXT):
    """Pill at (x, y(md)) with a horizontal leader to the well at depth md."""
    y = w.y(md)
    tx = w.cx + (w.CAS_OD / 2 + 0.02 if side == "r" else -(w.CAS_OD / 2 + 0.02)) if target_dx is None else w.cx + target_dx
    return K.callout(st, text, x, y, tx, y, color=color, fg=fg, size=size, align="l" if side == "r" else "r")


# ====================================================================================================== 1.01
def b101(st, tl):
    b = tl["1.01"]
    s = b.sent
    with st.span(b.start, b.end):
        w = K.Well(st, cx=-3.6, y_top=2.75, scale=0.9, rock_w=2.0)
        rock = w.rock()
        sand = w.reservoir(3820, 4200)
        sea = w.seabed()
        st.fade_in(rock + sand + sea, b.start + 0.05, 0.5)
        # casing + cement grow downward during sentence 2
        w.grow = (s[2] + 0.6, s[2] + 3.6)
        cem = w.cement()
        cas = w.casing()
        w.grow = (s[3] + 0.3, s[3] + 3.0)
        tub = w.tubing(bore_alpha=0.0)
        w.grow = None
        pk = w.packer()
        dv = w.dhsv()
        tr = w.tree()
        # tubing bore fills with oil (alpha ramps via an overlaid rect), flowing upward
        oil = st.rect(w.cx, (w.y(0) + w.y(3800)) / 2, w.TUB_OD - 2 * w.TUB_WALL, w.y(0) - w.y(3800), P.OIL, 0.17, alpha=0.8)
        st.fade_in(oil, s[3] + 2.6, 0.6)
        st.flow([(w.cx, w.y(3800)), (w.cx, w.y(0) + 0.1)], s[3] + 3.0, b.end - 0.4, P.OIL, n=10, speed=0.7, r=0.04)
        # packer: appears, then rubber squeezes (scale in x)
        t_pk = b.word(4, "a packer")
        st.pop_in(pk, t_pk, 0.5)
        lp = K.callout(st, "packer", -2.2, w.y(M.PACKER_MD), w.cx + 0.52, w.y(M.PACKER_MD), size=0.21)
        st.fade_in(lp, t_pk + 0.2, 0.4)
        # safety valve + hydraulic control line
        t_dv = b.word(5, "downhole safety valve")
        dv_all = dv.body + dv.flapper + dv.ctrl
        st.fade_in(dv_all, t_dv, 0.5)
        ld = K.callout(st, "downhole safety valve", -2.2, w.y(M.DHSV_MD), w.cx + 0.4, w.y(M.DHSV_MD), size=0.21)
        st.fade_in(ld, t_dv + 0.2, 0.4)
        lc = K.note(st, "held open by control-line pressure", -2.2, w.y(M.DHSV_MD) - 0.42, 0.18, P.PORE)
        st.fade_in(lc, b.word(5, "held open"), 0.4)
        # flapper snaps shut when the pressure is lost
        t_slam = b.word(5, "slam shut")
        st.rotate(dv.flapper, t_slam + 0.2, t_slam + 0.55, 0)
        st.recolor(dv.ctrl, t_slam, t_slam + 0.3, P.BAD)
        st.rotate(dv.flapper, b.end - 1.4, b.end - 0.9, 80)
        st.recolor(dv.ctrl, b.end - 1.4, b.end - 0.9, P.PORE)
        # tree
        t_tr = b.word(6, "Christmas tree")
        st.fade_in(tr, t_tr - 0.5, 0.6)
        lt = K.callout(st, "Christmas tree", -2.2, w.y_top + 0.5, w.cx + 0.4, w.y_top + 0.5, size=0.21)
        st.fade_in(lt, t_tr, 0.4)
        # casing and tubing labels
        lcas = _wlabel(st, w, 1700, "casing + cement", -2.2)
        ltub = _wlabel(st, w, 2900, "tubing", -2.2, target_dx=0.25)
        st.fade_in(lcas, b.word(2, "Casing lines"), 0.4)
        st.fade_in(ltub, b.word(3, "tubing"), 0.4)
        # reservoir label
        lres = _wlabel(st, w, 4000, "reservoir", -2.2, color=P.SAND, size=0.21, fg=P.BG)
        st.fade_in(lres, s[0] + 0.6, 0.5)
        k = st.text("depths compressed", -7.6, -3.55, 0.17, P.MUTED, 0.6, align="l")
        st.fade_in(k, b.start + 0.5, 0.5)
        # a down arrow along the well at the first sentence: "reaching into"
        ar = st.arrow(w.cx - 1.15, w.y_top + 0.6, w.cx - 1.15, w.y(3900), P.PORE, 0.045, 0.2, 0.9)
        st.fade_in(ar, s[0], 0.5)
        st.fade_out(ar, s[1] + 0.2, 0.5)


# ====================================================================================================== 1.02
def b102(st, tl):
    b = tl["1.02"]
    s = b.sent
    with st.span(b.start, b.end):
        w = K.Well(st, cx=-5.5, y_top=2.75, scale=0.9, rock_w=1.15)
        base = w.rock() + w.reservoir(3820, 4200) + w.cement() + w.casing() + w.tubing(bore_alpha=0.0) + w.seabed() + w.tree()
        w.packer()
        w.dhsv()
        base += w.parts["packer"] + w.parts["dhsv"].body + w.parts["dhsv"].flapper + w.parts["dhsv"].ctrl
        mand = [w.mandrel(md) for md in M.GL_MANDRELS]
        sl = w.sleeve()
        nip = w.nipple()
        pf = w.perfs(n=5)
        base += sum([m.body + m.valve for m in mand], []) + sl.body + nip + pf
        oil = st.rect(w.cx, (w.y(0) + w.y(3800)) / 2, w.TUB_OD - 2 * w.TUB_WALL, w.y(0) - w.y(3800), P.OIL, 0.17, alpha=0.7)
        base.append(oil)
        st.flow([(w.cx, w.y(3800)), (w.cx, w.y(0) + 0.1)], b.start, b.end - 0.3, P.OIL, n=9, speed=0.6, r=0.035)
        # the well dims while an inset is up; the inset card sits at the centre
        CX, CY, SC = 0.1, -0.35, 1.38
        card = st.rect(CX, CY, 5.6, 5.9, P.PANEL, 0.1, role="card")
        card_t = st.text("", CX, CY + 2.75, 0.3, P.TEXT, 0.9)
        t_hdr = []

        def zoom_to(md, x_right=-2.7):
            y = w.y(md)
            ln = st.line([(w.cx + 0.58, y), (x_right, CY + 0.0 + (y - CY) * 0.3)], P.MUTED, 0.025, 0.28, role="hair")
            ring = st.ring(w.cx, y, 0.42, 0.05, P.WARN, 0.95)
            return ln, ring

        def header(t0, t1, text):
            h = st.text(text, CX, CY + 2.62, 0.3, P.TEXT, 0.9, kind="bold")
            show(h, t0, t1)
            return h

        def show(objs, t0, t1, d=0.4):
            K.show(st, objs, t0, t1, d)

        t0s = [b.word(2, "Landing nipples") - 0.1, b.word(3, "A sliding sleeve") - 0.1, b.word(4, "Side-pocket mandrels") - 0.1,
               b.word(5, "perforations") - 0.5]
        t1s = [t0s[1] - 0.25, t0s[2] - 0.25, t0s[3] - 0.25, b.word(6, "Almost everything") - 0.2]
        st.fade_in(card, t0s[0] - 0.1, 0.4)
        st.fade_out(card, b.word(6, "Almost everything") + 0.2, 0.5)
        # --- landing nipple
        ni = I.nipple_inset(st, CX, CY - 0.2, SC)
        parts = ni.walls + ni.bore + ni.body
        lbl = [st.text("machined locking groove", CX + 1.25, ni.groove_y, 0.2, P.WARN, 0.9, align="l", kind="bold"),
               st.text("polished seal bore", CX + 1.25, ni.seal_y[0], 0.2, P.TEXT, 0.9, align="l"),
               st.text("polished seal bore", CX + 1.25, ni.seal_y[1], 0.2, P.TEXT, 0.9, align="l")]
        ln, ring = zoom_to(M.NIPPLE_MD)
        for o in lbl:
            pass
        show(parts + lbl + [ln, ring], t0s[0], t1s[0])
        show(header(t0s[0], t1s[0], "landing nipple"), t0s[0], t1s[0])
        # --- sliding sleeve: sleeve slides down to open the ports
        sv = I.sleeve_inset(st, CX, CY - 0.2, SC)
        parts = sv.walls + sv.bore + sv.ports + sv.inner
        lbl = [st.text("port", CX + 1.35, CY - 0.2, 0.2, P.TEXT, 0.9, align="l"),
               st.text("inner sleeve", CX - 1.35, CY - 0.55, 0.2, P.PRIMARY_B, 0.9, align="r", kind="bold")]
        ln, ring = zoom_to(M.SLEEVE_MD)
        show(parts + lbl + [ln, ring], t0s[1], t1s[1])
        show(header(t0s[1], t1s[1], "sliding sleeve"), t0s[1], t1s[1])
        st.move(sv.inner, t0s[1] + 2.2, t0s[1] + 3.2, dy=sv.y_open - sv.y_closed)
        st.flow([(CX + 1.6, CY - 0.2), (CX, CY - 0.2)], t0s[1] + 3.4, t1s[1], P.OIL, n=5, speed=0.8, r=0.05)
        # --- side-pocket mandrel with valve
        md_ = I.mandrel_inset(st, CX - 0.3, CY - 0.2, 1.25)
        parts = md_.body + md_.bore + md_.pocket + md_.valve + md_.ports
        lbl = [st.text("off-centre pocket", CX + 1.25, CY - 1.95, 0.2, P.TEXT, 0.9, align="l"),
               st.text("valve", CX + 1.55, CY + 0.35, 0.22, P.GAS, 0.9, align="l", kind="bold")]
        ln, ring = zoom_to(M.GL_MANDRELS[1])
        show(parts + lbl + [ln, ring], t0s[2], t1s[2])
        show(header(t0s[2], t1s[2], "side-pocket mandrel"), t0s[2], t1s[2])
        # --- perforations
        pf_ = I.perf_inset(st, CX - 0.5, CY - 0.2, 1.3)
        parts = pf_.rock + pf_.cement + pf_.casing + pf_.bore + pf_.tunnels
        lbl = [st.text("sand", CX + 1.9, CY + 1.6, 0.2, P.SAND, 0.9, align="l", kind="bold"),
               st.text("cement", pf_.x_cem - 0.45, CY - 1.95, 0.2, P.MUTED, 0.9, align="c"),
               st.text("casing", pf_.x_cas[0] - 0.05, CY + 1.95, 0.2, P.MUTED, 0.9, align="c"),
               st.text("the well", pf_.x_cas[0] - 1.2, CY + 0.0, 0.2, P.TEXT, 0.9, align="c")]
        ln, ring = zoom_to(4000)
        show(parts + lbl + [ln, ring], t0s[3], t1s[3])
        show(header(t0s[3], t1s[3], "perforations"), t0s[3], t1s[3])
        for pth in pf_.paths:
            st.flow([(pth[0][0], pth[0][1]), (pth[1][0], pth[1][1])], t0s[3] + 1.0, t1s[3], P.OIL, n=4, speed=0.9, r=0.055)
        # the gas path in the mandrel
        st.flow(md_.gas_path, t0s[2] + 1.8, t1s[2], P.GAS, n=8, speed=0.9, r=0.045)


# ====================================================================================================== 1.03
def b103(st, tl):
    b = tl["1.03"]
    s = b.sent
    with st.span(b.start, b.end):
        y = -0.2
        stages = [("DRILL", -7.3, -5.0, P.PANEL2), ("COMPLETE", -4.9, -2.9, P.PANEL2), ("PRODUCE", -2.8, 4.6, P.PRIMARY_B),
                  ("PLUG & ABANDON", 4.7, 7.5, P.PANEL2)]
        objs = []
        for name, x0, x1, col in stages:
            r = st.rect((x0 + x1) / 2, y, x1 - x0, 0.72, col, 0.5, role="pill")
            t = st.text(name, (x0 + x1) / 2, y, 0.24, P.TEXT if col != P.PRIMARY_B else P.BG, 0.6, kind="bold")
            objs.append((r, t))
        st.fade_in(objs[0][0] + objs[0][1] if False else [objs[0][0], objs[0][1]], s[0], 0.4)
        # drilling builds the well
        st.fade_in([objs[1][0], objs[1][1], objs[2][0], objs[2][1], objs[3][0], objs[3][1]], s[0] + 0.5, 0.4)
        # intervention loops hang below PRODUCE
        xs = [-1.2, 1.4, 3.8]
        loops = []
        for i, x in enumerate(xs):
            heavy = i == 2
            name = "workover" if heavy else "intervention"
            col = P.WARN if heavy else P.PORE
            ys = y - 1.25 if not heavy else y - 1.7
            st_line = st.line([(x, y - 0.38), (x, ys + 0.3)], col, 0.04, 0.5, role="curve")
            wd = st.measure(name, 0.22, "bold") + 0.5
            pl = K.tag(st, x, ys, name, color=col, fg=P.BG, size=0.22, z=0.8)
            loops.append((st_line, pl))
        t1 = b.word(1, "Intervention")
        for i, (ln_, pl) in enumerate(loops[:2]):
            st.draw_on(ln_, t1 + 0.3 * i, t1 + 0.3 * i + 0.5, "BEZIER")
            st.fade_in(pl, t1 + 0.3 * i + 0.3, 0.4)
        t2 = b.word(2, "workover")
        st.draw_on(loops[2][0], t2, t2 + 0.5, "BEZIER")
        st.fade_in(loops[2][1], t2 + 0.3, 0.4)
        # sub-captions
        c1 = K.note(st, "go in to measure something, or to change something", -0.2, y - 2.2, 0.21, P.MUTED, align="c")
        st.fade_in(c1, t1 + 0.4, 0.5)
        c2 = K.note(st, "the heavy end: pull the tubing out and replace it", 2.4, y - 2.85, 0.21, P.WARN, align="c")
        st.fade_in(c2, b.word(3, "heavy end"), 0.5)
        # a bracket under DRILL: "drilling builds the well"
        c0 = K.note(st, "builds the well", -6.1, y + 0.8, 0.21, P.MUTED, align="c")
        st.fade_in(c0, s[0] + 0.2, 0.5)


# ====================================================================================================== 1.04
def _mini_tree(st, x, y, z=0.5):
    """Dry tree stub: stack of valves on a wellhead. Returns objs and the y of its top."""
    o = [st.rect(x, y, 0.9, 0.34, P.STEEL_DK, z), st.rect(x, y + 0.34, 0.5, 0.34, P.STEEL, z), st.rect(x, y + 0.66, 0.5, 0.3, P.STEEL_DK, z),
         st.rect(x + 0.55, y + 0.34, 0.6, 0.16, P.STEEL, z - 0.01)]
    return o, y + 0.81


def b104(st, tl):
    b = tl["1.04"]
    s = b.sent
    with st.span(b.start, b.end):
        lx, rx = -4.85, 0.1
        pw, ph, py = 4.9, 6.3, -0.3
        pl = st.rect(lx, py, pw, ph, P.PANEL, 0.2, role="card")
        pr = st.rect(rx, py, pw, ph, P.PANEL, 0.2, role="card")
        st.fade_in(pl, b.start + 0.3, 0.5)
        st.fade_in(pr, s[2] - 0.1, 0.5)
        tl_ = K.tag(st, lx, 3.35, "LIGHT", color=P.SAFE, fg=P.BG, size=0.24, z=0.6)
        tr_ = K.tag(st, rx, 3.35, "HEAVY", color=P.WARN, fg=P.BG, size=0.24, z=0.6)
        st.fade_in(tl_, s[1] - 0.2, 0.4)
        st.fade_in(tr_, s[2], 0.4)

        # ---- LIGHT: a wire through a tree on a live well
        tube = [st.rect(lx, -1.0, 0.46, 3.4, P.STEEL, 0.4, role="steel"), st.rect(lx, -1.0, 0.28, 3.4, P.OIL, 0.41, alpha=0.9)]
        tree, ytop = _mini_tree(st, lx, 0.7)
        lub = [st.rect(lx, ytop + 0.5, 0.34, 1.0, P.STEEL_DK, 0.55, role="steel"), st.rect(lx, ytop + 1.04, 0.5, 0.12, P.STEEL, 0.56)]
        y_pk = ytop + 1.1
        wire_ = st.rect(lx, y_pk, 0.03, 0.9, P.WIRE, 0.7, anchor="t", role="steel")
        tool = st.rect(lx, y_pk - 0.9 - 0.12, 0.16, 0.26, P.WARN, 0.7)
        drum_ = K.drum(st, lx - 1.75, 1.35, 0.45, turns=3)
        drum_line = st.line([(lx - 1.75, 1.8), (lx - 1.2, 2.55), (lx, y_pk)], P.WIRE, 0.025, 0.6, role="hair")
        light = tube + tree + lub + [wire_, tool, drum_line] + drum_.all()
        st.fade_in(light, s[1] + 0.2, 0.6)
        st.flow([(lx, -2.65), (lx, 0.75)], s[1] + 1.0, b.end - 0.4, P.OIL, n=7, speed=0.55, r=0.035)
        st.move([tool], s[1] + 1.4, s[1] + 3.4, dy=-2.2)
        st.scale_to(wire_, s[1] + 1.4, s[1] + 3.4, sy=0.9 + 2.2)
        g1 = K.dial(st, lx + 1.75, 1.2, 0.45, s[4], s[4] + 1.0, 210, 60, color=P.OIL)
        g1t = st.counter(lx + 1.75, 0.45, s[4], s[4] + 1.0, 0, 200, "{:.0f} bar", 0.22, P.OIL, 0.8, hold=b.end - 0.2)
        lt = K.note(st, "live well: pressure held at the tree", lx, -3.2, 0.2, P.OIL, align="c")
        st.fade_in(g1 + lt, s[4] - 0.1, 0.5)

        # ---- HEAVY: rig, tree removed, kill fluid in the tubing
        rig = [st.line([(rx - 0.9, 1.55), (rx, 2.75), (rx + 0.9, 1.55)], P.STEEL, 0.06, 0.5, role="hair"),
               st.line([(rx - 0.55, 1.95), (rx + 0.55, 1.95)], P.STEEL, 0.04, 0.5, role="hair"),
               st.line([(rx - 0.3, 2.45), (rx + 0.3, 2.45)], P.STEEL, 0.04, 0.5, role="hair")]
        bop = [st.rect(rx, 1.2, 1.0, 0.7, P.STEEL_DK, 0.5), st.rect(rx, 1.2, 0.3, 0.7, P.BG, 0.52),
               st.rect(rx - 0.38, 1.2, 0.3, 0.2, P.WARN, 0.55), st.rect(rx + 0.38, 1.2, 0.3, 0.2, P.WARN, 0.55)]
        tube2 = [st.rect(rx, -0.95, 0.46, 3.9, P.STEEL, 0.4, role="steel"), st.rect(rx, -0.95, 0.28, 3.9, P.OIL, 0.41, alpha=0.9)]
        tree_off, _ = _mini_tree(st, rx + 1.65, -2.2)
        off_t = st.text("tree removed", rx + 1.65, -2.72, 0.19, P.MUTED, 0.6)
        heavy = rig + bop + tube2 + tree_off + [off_t]
        st.fade_in(heavy, s[2] + 0.3, 0.6)
        fill = st.rect(rx, 1.0, 0.28, 0.001, P.KILL_MUD, 0.45, anchor="t")
        st.scale_to(fill, s[5] + 0.6, s[5] + 2.8, sy=3.9)
        g2 = K.dial(st, rx + 1.65, 1.5, 0.45, s[5] + 0.6, s[5] + 2.8, 60, 210, color=P.KILL_MUD)
        g2t = st.counter(rx + 1.65, 0.75, s[5] + 0.6, s[5] + 2.8, 200, 0, "{:.0f} bar", 0.22, P.KILL_MUD, 0.8, hold=b.end - 0.2)
        kt = K.note(st, "killed well: kill fluid holds it", rx, -3.2, 0.2, P.KILL_MUD, align="c")
        st.fade_in(g2 + kt, s[5] - 0.1, 0.5)

        # the price of killing, then the conclusion
        pen = [K.tag(st, rx - 1.25, 0.75 - i * 0.62, txt, color=P.BAD, fg=P.BG, size=0.19, z=0.9)
               for i, txt in enumerate(["days lost", "rock damage", "weaker well"])]
        for i, g in enumerate(pen):
            K.show(st, g, s[6] + 0.3 + i * 0.9, s[7] - 0.2, 0.35)
        halo = K.tag(st, lx, 2.85, "so we work live", color=P.SAFE, fg=P.BG, size=0.2, z=0.9)
        st.fade_in(halo, s[7] + 0.1, 0.5)


# ====================================================================================================== 1.05
def _decline(t, q0=1000.0, d=0.18):
    return q0 * math.exp(-d * t)


def _stepped(t, t_step=8.0, ramp=0.5, gain=0.6):
    v = _decline(t)
    if t < t_step:
        return v
    return v * (1 + gain * min((t - t_step) / ramp, 1.0))


def b105(st, tl):
    b = tl["1.05"]
    s = b.sent
    with st.span(b.start, b.end):
        ch = Chart(st, -6.2, -2.2, 5.5, 4.3, (0, 14), (0, 1150))
        fr = ch.frame(xticks=[0, 2, 4, 6, 8, 10, 12, 14], yticks=[0, 400, 800], xlabel="years on production", ylabel="oil rate", fx="{:.0f}", fy="{:,.0f}",
                      tick_size=0.18)
        st.fade_in(fr, b.start + 0.1, 0.4)
        ts_pre = [i * 0.25 for i in range(0, 33)]            # 0..8
        ts_post = [8 + i * 0.25 for i in range(0, 25)]        # 8..14
        c_pre = st.line([ch.pt(t, _decline(t)) for t in ts_pre], P.OIL, 0.075, 0.45)
        c_post = st.line([ch.pt(t, _stepped(t)) for t in ts_post], P.OIL, 0.075, 0.45)
        c_base = st.line([ch.pt(t, _decline(t)) for t in ts_post], P.MUTED, 0.05, 0.4)
        st.draw_on(c_pre, s[1] + 0.2, s[3] - 0.2, "LINEAR")
        st.draw_on(c_base, s[3] - 0.1, s[3] + 1.0, "LINEAR")
        st.draw_on(c_post, s[3] + 0.3, s[3] + 1.8, "LINEAR")
        sh_pts = [ch.pt(t, _stepped(t)) for t in ts_post] + [ch.pt(t, _decline(t)) for t in reversed(ts_post)]
        shade = st.poly(sh_pts, P.OIL, 0.3, alpha=0.38)
        st.fade_in(shade, s[4] + 0.2, 0.6)
        l_old = st.text("without the job", ch.X(11.8), ch.Y(_decline(11.8)) - 0.3, 0.19, P.MUTED, 0.5, align="c")
        st.fade_in(l_old, s[3] + 0.8, 0.4)
        l_x = K.tag(st, ch.X(11.3), ch.Y(_stepped(11.3)) + 0.5, "extra oil", color=P.OIL, fg=P.BG, size=0.2, z=0.8)
        st.fade_in(l_x, s[4] + 0.5, 0.4)
        jl = st.rect(ch.X(8.0), (ch.Y(1000) + ch.Y(0)) / 2, 0.03, ch.Y(1000) - ch.Y(0), P.PORE, 0.35, alpha=0.8)
        l_job = st.text("intervention", ch.X(8.0), ch.Y(1000) + 0.2, 0.2, P.PORE, 0.6, kind="bold")
        st.fade_in([jl, l_job], s[3] + 0.0, 0.4)
        l_w = st.text("water arrives, pressure falls", ch.X(4.2), ch.Y(_decline(4.2)) + 0.45, 0.19, P.MUTED, 0.5)
        st.fade_in(l_w, s[2] + 0.6, 0.4)
        st.fade_out(l_w, s[3] - 0.1, 0.3)

        # ---- right: relative cost of the spread (ordering only)
        bx = 2.55
        title = K.note(st, "relative cost of the spread (ordering only)", 1.0, 2.75, 0.2, P.MUTED, align="l")
        st.fade_in(title, s[5], 0.4)
        names = ["wireline", "coiled tubing", "intervention vessel", "drilling rig"]
        vals = [1.0, 2.3, 5.0, 10.0]
        unit = 0.43
        t_in = [b.word(6, "wire unit"), b.word(6, "wire unit") + 1.6, b.word(7, "A rig") - 0.8, b.word(7, "A rig")]
        for i, (n, v) in enumerate(zip(names, vals)):
            yy = 1.85 - i * 0.82
            lab = st.text(n, bx - 0.12, yy, 0.21, P.TEXT, 0.6, align="r")
            col = P.SAFE if v < 6 else P.BAD
            bar = st.rect(bx, yy, unit * 0.05, 0.44, col, 0.55, anchor="l", role="flat")
            st.fade_in([lab, bar], t_in[i] - 0.1, 0.3)
            st.scale_to(bar, t_in[i], t_in[i] + 0.9, sx=unit * v)
        vx = bx + unit * 6.0
        vl = st.rect(vx, 0.45, 0.03, 3.5, P.OIL, 0.5, alpha=0.95)
        vlt = K.tag(st, vx, -1.45, "value of the extra oil", color=P.OIL, fg=P.BG, size=0.19, z=0.8)
        st.fade_in([vl, vlt], s[8] - 2.0, 0.5)
        mj = K.note(st, "the cheap way can turn a marginal job into a profitable one", 4.6, -2.3, 0.21, P.TEXT, align="c", wrap=34)
        st.fade_in(mj, b.word(8, "marginal"), 0.5)


def build(st, tl):
    F.header(st, tl)
    b101(st, tl)
    b102(st, tl)
    b103(st, tl)
    b104(st, tl)
    b105(st, tl)
