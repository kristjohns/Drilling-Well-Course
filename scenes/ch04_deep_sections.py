"""Ch 4: Drilling the deep sections: BHA, steering, mud, ECD, MPD."""
from __future__ import annotations
import math
import random

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common.shapes import WindowChart, Cutaway, pill, loop_move

TITLE = "Drilling the deep sections"


# ---------------------------------------------------------------- 4.01 BHA + "we drill by pulling"
def beat_bha(st, tl):
    b = tl["4.01"]
    s = b.sent
    with st.span(b.start, b.end):
        cx = -2.6
        top, neutral, bot = 3.8, -0.4, -2.7
        pipe = st.rect(cx, (top + neutral) / 2, 0.16, top - neutral, P.STEEL, 0.2)
        collars = st.rect(cx, (neutral + bot) / 2, 0.55, neutral - bot, "#8fa1b8", 0.2)
        bit = st.poly([(cx - 0.35, bot), (cx + 0.35, bot), (cx + 0.18, bot - 0.35), (cx - 0.18, bot - 0.35)], P.WARN, 0.25)
        rock = st.rect(cx, bot - 0.65, 2.4, 0.6, P.ROCK, 0.0)
        st.fade_in([pipe, collars, bit, rock], b.start, 0.5)
        # BHA bracket + parts list
        br = st.rect(cx + 0.55, (neutral + bot - 0.35) / 2 + 0.05, 0.05, neutral - bot + 0.4, P.PORE, 0.3)
        parts = [("bit", bot - 0.15), ("steering tool", bot + 0.55), ("instruments (MWD / LWD)", bot + 1.1), ("drill collars: heavy steel", bot + 1.75)]
        pl = [st.text(n, cx + 0.8, y, 0.23, P.TEXT, 0.3, align="l", kind="bold") for n, y in parts]
        bl = st.text("bottom-hole assembly: BHA", cx + 0.8, neutral + 0.3, 0.26, P.PORE, 0.3, align="l", kind="bold")
        st.fade_in([br, bl], s[0] + 0.3, 0.5)
        for i, t in enumerate(pl):
            st.fade_in(t, s[0] + 1.0 + 0.8 * i, 0.4)
        # tension / compression
        ten = []
        for y in (2.8, 1.6, 0.4):
            ten += st.arrow(cx - 0.4, y - 0.4, cx - 0.4, y + 0.15, P.PORE, 0.06, 0.2, 0.4)
        com = []
        for y in (-0.8, -1.5, -2.2):
            com += st.arrow(cx - 0.55, y + 0.15, cx - 0.55, y - 0.3, P.BAD, 0.06, 0.2, 0.4)
        np_ = st.dashed((cx - 1.1, neutral), (cx + 0.5, neutral), P.TEXT, 0.03, 0.12, 0.08, 0.4)
        npl = st.text("neutral point", cx - 1.15, neutral, 0.2, P.TEXT, 0.4, align="r")
        tl_ = st.text("pipe in tension", cx - 0.7, 1.6, 0.22, P.PORE, 0.4, align="r", kind="bold")
        cl = st.text("collars in compression:\nweight on bit", cx - 0.75, -1.5, 0.22, P.BAD, 0.4, align="r", kind="bold")
        st.fade_in(ten + [tl_], s[3], 0.5)
        st.fade_in(com + np_ + [npl, cl], s[3] + 0.8, 0.5)
        pull = st.text("we drill by pulling", 4.1, 3.5, 0.4, P.TEXT, 0.5, kind="bold")
        st.fade_in(pull, s[2], 0.5)
        # buckling when pushed from the top
        px = 4.1
        pts = [(px + 0.45 * math.sin(i / 14 * math.pi * 4) * (0.4 + 0.6 * i / 14), 2.6 - i * 0.37) for i in range(15)]
        bk = st.line(pts, P.BAD, 0.12, 0.4)
        push = st.arrow(px, 3.1, px, 2.6, P.BAD, 0.1, 0.3, 0.4)
        x1 = st.line([(px - 1.0, 2.7), (px + 1.0, -2.4)], P.BAD, 0.14, 0.5)
        x2 = st.line([(px - 1.0, -2.4), (px + 1.0, 2.7)], P.BAD, 0.14, 0.5)
        bl2 = st.text("pushed from the top:\na slender column buckles", px, -3.1, 0.24, P.BAD, 0.4, kind="bold")
        st.fade_in(push, s[4], 0.3)
        st.draw_on(bk, s[4] + 0.2, s[4] + 2.0)
        st.draw_on(x1, s[4] + 2.0, s[4] + 2.5)
        st.draw_on(x2, s[4] + 2.4, s[4] + 2.9)
        st.fade_in(bl2, s[4] + 1.5, 0.4)


# ---------------------------------------------------------------- 4.02 bit, steering, why steer
def beat_steering(st, tl):
    b = tl["4.02"]
    s = b.sent
    rnd = random.Random(5)
    with st.span(b.start, b.end):
        xs = (-4.0, 0.9, 5.7)
        cards = [st.rect(x, 0.15, 4.4, 6.9, P.PANEL, 0.0) for x in xs]
        st.fade_in(cards[0], b.start, 0.4)
        t1 = st.text("PDC bit: shears like a lathe tool", xs[0], 3.35, 0.24, P.TEXT, 0.3, kind="bold")
        # card 1: bit shearing rock
        rock = st.rect(xs[0], -1.4, 3.6, 2.2, P.ROCK, 0.1)
        body = st.poly([(xs[0] - 0.9, 1.4), (xs[0] + 0.9, 1.4), (xs[0] + 1.0, 0.2), (xs[0] - 1.0, 0.2)], "#8fa1b8", 0.2)
        cut = [st.rect(xs[0] - 0.8 + 0.4 * i, 0.12, 0.28, 0.2, P.WARN, 0.3) for i in range(5)]
        st.fade_in([t1, rock, body] + cut, s[0], 0.5)
        chips = []
        for i in range(6):
            c = st.poly([(xs[0] - 0.8 + 0.3 * i, -0.3), (xs[0] - 0.6 + 0.3 * i, -0.2), (xs[0] - 0.75 + 0.3 * i, -0.05)], "#b49b7b", 0.25)
            chips.append(c)
            st.fade_in(c, s[0] + 0.8 + 0.2 * i, 0.2)
            st.move(c, s[0] + 0.8 + 0.2 * i, s[0] + 3.0, dx=rnd.uniform(-0.3, 0.6), dy=rnd.uniform(0.3, 0.9))
        st.move([body] + cut, s[0] + 0.5, s[0] + 2.0, dx=0.0)
        # card 2: steering
        st.fade_in(cards[1], s[1], 0.4)
        t2 = st.text("steering: needs a bend", xs[1], 3.35, 0.24, P.TEXT, 0.3, kind="bold")
        st.fade_in(t2, s[1], 0.4)
        # motor: slide (curved) vs rotate (straight)
        mpath_slide = [(xs[1] - 1.9 + 0.35 * i, 2.5 - 0.05 * i * i * 0.45 - 0.1 * i) for i in range(10)]
        slide = st.line(mpath_slide, P.WARN, 0.1, 0.3)
        mpath_rot = [(xs[1] - 1.9 + 0.35 * i, 1.0 - 0.05 * i) for i in range(10)]
        rot = st.line(mpath_rot, P.PORE, 0.1, 0.3)
        st.draw_on(slide, s[2], s[2] + 2.2)
        st.fade_in(st.text("motor + bent housing: slide = curve", xs[1], 2.95, 0.19, P.WARN, 0.3, kind="bold"), s[2], 0.4)
        st.draw_on(rot, s[2] + 2.0, s[2] + 3.6)
        st.fade_in(st.text("rotate = straight (bend averages out)", xs[1], 0.45, 0.19, P.PORE, 0.3, kind="bold"), s[2] + 2.0, 0.4)
        # RSS: pad pushes while string spins
        pipe = st.rect(xs[1] - 0.2, -1.8, 0.35, 1.9, P.STEEL, 0.2)
        wall = st.rect(xs[1] + 0.55, -1.8, 0.2, 2.2, P.ROCK, 0.1)
        pad = st.rect(xs[1] + 0.2, -1.8, 0.2, 0.5, P.WARN, 0.3)
        rs = st.arrow(xs[1] + 0.05, -1.0, xs[1] + 0.05, -0.55, P.TEXT, 0.05, 0.16, 0.4)
        rl = st.text("rotary steerable: pad pushes\nwhile the whole string turns", xs[1] - 0.2, -3.2, 0.19, P.TEXT, 0.3, kind="bold")
        st.fade_in([pipe, wall, pad, rl] + rs, s[3], 0.5)
        st.move(pad, s[3] + 0.8, s[3] + 1.4, dx=0.12)
        st.move(pad, s[3] + 1.4, s[3] + 2.0, dx=-0.12)
        # card 3: why steer: top-view map
        st.fade_in(cards[2], s[4], 0.4)
        t3 = st.text("why steer?", xs[2], 3.35, 0.24, P.TEXT, 0.3, kind="bold")
        st.fade_in(t3, s[4], 0.4)
        rig = st.circle(xs[2] - 1.5, 2.3, 0.14, P.WARN, 0.3)
        tgt = st.circle(xs[2] + 1.4, -2.0, 0.2, P.OIL, 0.3)
        nb = st.circle(xs[2] - 0.1, 0.2, 0.14, P.BAD, 0.3)
        nbr = st.ring(xs[2] - 0.1, 0.2, 0.55, 0.05, P.BAD, 0.25)
        straight = st.dashed((xs[2] - 1.5, 2.3), (xs[2] + 1.4, -2.0), P.MUTED, 0.03, 0.12, 0.1, 0.2)
        path = st.line([(xs[2] - 1.5, 2.3), (xs[2] - 1.0, 0.8), (xs[2] - 0.9, -0.6), (xs[2] + 0.3, -1.6), (xs[2] + 1.4, -2.0)], P.PORE, 0.08, 0.35)
        lb = [st.text("rig", xs[2] - 1.5, 2.65, 0.2, P.WARN, 0.3, kind="bold"), st.text("target", xs[2] + 1.4, -2.4, 0.2, P.OIL, 0.3, kind="bold"),
              st.text("other well", xs[2] + 0.15, 0.9, 0.18, P.BAD, 0.3)]
        st.fade_in([rig, tgt, nb, nbr, straight] + lb, s[4] + 0.5, 0.4)
        st.draw_on(path, s[5], s[5] + 3.0)
        dd = st.text("directional drilling", xs[2], -3.0, 0.24, P.PORE, 0.3, kind="bold")
        st.fade_in(dd, s[5] + 1.0, 0.4)


# ---------------------------------------------------------------- 4.03 drag, dogleg, survey uncertainty
def beat_drag(st, tl):
    b = tl["4.03"]
    s = b.sent
    with st.span(b.start, b.end):
        xs = (-4.0, 0.9, 5.7)
        cards = [st.rect(x, 0.15, 4.4, 6.9, P.PANEL, 0.0) for x in xs]
        # capstan
        st.fade_in(cards[0], s[0], 0.4)
        cap = st.circle(xs[0], 0.8, 0.9, "#8fa1b8", 0.2)
        rope = st.line([(xs[0] - 2.0, -0.2)] + [(xs[0] + 1.15 * math.cos(math.radians(a)), 0.8 + 1.15 * math.sin(math.radians(a))) for a in range(200, 20, -12)] + [(xs[0] + 2.0, 1.6)], P.WARN, 0.07, 0.3)
        t1 = st.arrow(xs[0] - 2.0, -0.2, xs[0] - 1.3, -0.2, P.PORE, 0.07, 0.2, 0.4)
        t2 = st.arrow(xs[0] + 1.3, 1.6, xs[0] + 2.1, 1.6, P.BAD, 0.14, 0.3, 0.4)
        tl1 = st.text("T₁", xs[0] - 1.65, -0.55, 0.24, P.PORE, 0.4, kind="bold")
        tl2 = st.text("T₂ ≫ T₁", xs[0] + 1.8, 2.0, 0.24, P.BAD, 0.4, kind="bold")
        eq = st.text("T₂ = T₁ · e^(μθ)", xs[0], -1.6, 0.34, P.TEXT, 0.4, kind="mono")
        cl = st.text("drag in a bend: a rope on a capstan", xs[0], 3.35, 0.22, P.TEXT, 0.3, kind="bold")
        st.fade_in([cap, cl], s[1], 0.4)
        st.draw_on(rope, s[1] + 0.3, s[1] + 2.0)
        st.fade_in(t1 + t2 + [tl1, tl2], s[1] + 1.5, 0.4)
        st.fade_in(eq, s[1] + 3.0, 0.5)
        # dogleg
        st.fade_in(cards[1], s[2], 0.4)
        arc = st.line([(xs[1] - 1.8 + 3.6 * t / 20, 2.4 - 3.0 * (t / 20) ** 2 * 1.0 - 0.2 * t / 20) for t in range(21)], P.PORE, 0.12, 0.3)
        dl = st.text("dogleg severity:\ncurvature, degrees per 30 m", xs[1], 3.3, 0.22, P.TEXT, 0.3, kind="bold")
        bend = st.text("bends the pipe each\nturn it makes: limit it", xs[1], -2.9, 0.22, P.WARN, 0.4, kind="bold")
        st.fade_in(dl, s[2], 0.4)
        st.draw_on(arc, s[2] + 0.3, s[2] + 2.5)
        st.fade_in(bend, s[2] + 2.5, 0.5)
        # survey ellipses
        st.fade_in(cards[2], s[3], 0.4)
        path = st.line([(xs[2] - 1.5, 2.6), (xs[2] - 0.9, 1.0), (xs[2] - 0.3, -0.6), (xs[2] + 0.3, -2.1)], P.PORE, 0.08, 0.3)
        ell = [st.ellipse(xs[2] - 1.5 + 0.0, 2.6, 0.12, 0.08, P.WARN, 0.2, 0.7),
               st.ellipse(xs[2] - 0.9, 1.0, 0.28, 0.17, P.WARN, 0.2, 0.55),
               st.ellipse(xs[2] - 0.3, -0.6, 0.55, 0.33, P.WARN, 0.2, 0.45),
               st.ellipse(xs[2] + 0.3, -2.1, 0.95, 0.55, P.WARN, 0.2, 0.35)]
        sv = st.text("survey: inclination + direction\nthe uncertainty ellipse grows with depth", xs[2], 3.3, 0.2, P.TEXT, 0.3, kind="bold")
        st.fade_in(sv, s[3], 0.4)
        st.draw_on(path, s[3] + 0.3, s[3] + 3.0)
        for i, e in enumerate(ell):
            st.fade_in(e, s[3] + 1.0 + 0.8 * i, 0.4)


# ---------------------------------------------------------------- 4.04 mud's jobs + barite
def beat_mud(st, tl):
    b = tl["4.04"]
    s = b.sent
    rnd = random.Random(11)
    with st.span(b.start, b.end):
        cells = [(-4.9, 1.6), (-1.5, 1.6), (-4.9, -1.9), (-1.5, -1.9)]
        titles = ["holds back the formation", "carries cuttings up", "cools the bit", "carries signals"]
        starts = [s[1], s[2], s[3], s[3] + 2.0]
        for (x, y), t, ts in zip(cells, titles, starts):
            card = st.rect(x, y, 3.2, 3.2, P.PANEL, 0.0)
            lab = st.text(t, x, y + 1.35, 0.22, P.TEXT, 0.3, kind="bold")
            st.fade_in([card, lab], ts, 0.4)
        # 1 pressure on wall
        x, y = cells[0]
        rock = [st.rect(x - 1.05, y - 0.1, 0.5, 2.4, P.ROCK, 0.1), st.rect(x + 1.05, y - 0.1, 0.5, 2.4, P.ROCK, 0.1)]
        mud = st.rect(x, y - 0.1, 1.5, 2.4, P.MUD, 0.1)
        pa = []
        for yy in (y - 0.8, y - 0.1, y + 0.6):
            pa += st.arrow(x - 0.6, yy, x - 0.9, yy, P.MUD, 0.06, 0.16, 0.3) + st.arrow(x + 0.6, yy, x + 0.9, yy, P.MUD, 0.06, 0.16, 0.3)
        st.fade_in(rock + [mud] + pa, starts[0] + 0.3, 0.4)
        # 2 cuttings rising
        x, y = cells[1]
        a1 = st.rect(x - 0.9, y - 0.1, 0.6, 2.4, P.ROCK, 0.1)
        a2 = st.rect(x + 0.9, y - 0.1, 0.6, 2.4, P.ROCK, 0.1)
        a3 = st.rect(x, y - 0.1, 1.2, 2.4, P.MUD, 0.1)
        st.fade_in([a1, a2, a3], starts[1] + 0.3, 0.4)
        cuts = []
        for i in range(8):
            c = st.circle(x + rnd.uniform(-0.45, 0.45), y - 1.1 + 0.2 * i, 0.07, "#6b5a46", 0.3)
            cuts.append(c)
        st.fade_in(cuts, starts[1] + 0.5, 0.3)
        loop_move(st, cuts, starts[1] + 0.6, b.end - 0.3, 1.2, cycles=4)
        # 3 cool the bit
        x, y = cells[2]
        bit = st.poly([(x - 0.5, y + 0.3), (x + 0.5, y + 0.3), (x + 0.3, y - 0.2), (x - 0.3, y - 0.2)], P.WARN, 0.2)
        stem = st.rect(x, y + 0.9, 0.3, 1.2, P.STEEL, 0.2)
        cool = []
        for dx in (-0.7, 0.7):
            cool += st.arrow(x + dx * 0.3, y - 0.2, x + dx, y - 0.6, P.PORE, 0.06, 0.16, 0.3)
        st.fade_in([bit, stem] + cool, starts[2] + 0.3, 0.4)
        # 4 signal pulses up the pipe
        x, y = cells[3]
        pp = st.rect(x, y - 0.1, 0.25, 2.4, P.STEEL, 0.2)
        pulses = [st.ring(x, y - 1.0 + 0.0, 0.3, 0.05, P.WARN, 0.3, 0.0) for _ in range(3)]
        st.fade_in(pp, starts[3] + 0.3, 0.4)
        for i, p in enumerate(pulses):
            t = starts[3] + 0.6 + 1.0 * i
            st.fade_in(p, t, 0.1)
            st.move(p, t, t + 1.4, dy=1.8)
            st.scale_to(p, t, t + 1.4, sx=1.5, sy=1.5)
            st.fade_out(p, t + 0.9, 0.5)
        # barite beaker
        bx, by = 3.6, 0.2
        glass = st.rect(bx, by, 1.8, 2.8, P.PANEL2, 0.3)
        liq = st.rect(bx, by - 1.4, 1.6, 0.0001, P.MUD, 0.35, anchor="b")
        st.fade_in([glass], s[4], 0.4)
        st.scale_to(liq, s[4] + 0.5, s[4] + 1.0, sy=1.8)
        parts = [st.circle(bx + rnd.uniform(-0.6, 0.6), by + 1.6, 0.06, "#e8e8e8", 0.5) for _ in range(14)]
        for i, p in enumerate(parts):
            t = s[4] + 1.0 + 0.2 * i
            st.fade_in(p, t, 0.1)
            st.move(p, t, t + 1.0, dy=-1.8 - 0.1 * (i % 3), interp="LINEAR")
            st.fade_out(p, t + 0.8, 0.2)
        gauge = st.rect(5.0, by - 1.4, 0.3, 0.0001, P.FRAC, 0.4, anchor="b")
        st.fade_in(st.rect(5.0, by, 0.34, 2.8, P.PANEL2, 0.3), s[4], 0.4)
        st.scale_to(gauge, s[4] + 1.0, s[4] + 5.0, sy=2.3)
        bl = st.text("barite: dense\nmineral powder", bx, by + 2.1, 0.22, P.TEXT, 0.4, kind="bold")
        wl = st.text("water-based  /  oil-based", bx + 0.7, by - 2.3, 0.22, P.MUD, 0.4, kind="bold")
        dn = st.text("density", 5.0, by + 1.8, 0.18, P.FRAC, 0.4, kind="bold")
        st.fade_in([bl, wl, dn], s[4] + 0.3, 0.4)


# ---------------------------------------------------------------- 4.05 ECD
def beat_ecd(st, tl):
    b = tl["4.05"]
    s = b.sent
    with st.span(b.start, b.end):
        cx, ytop, ybot = -3.6, 3.4, -3.0
        cut = Cutaway(st, cx, ytop, ybot, hole_w=2.4, pipe_w=0.9, rock_w=1.5, rock=P.ROCK)
        base = cut.draw(pipe_bottom=ybot + 0.5)
        mud_l = cut.static_gap("l", P.MUD, ytop, ybot, 0.03)
        mud_r = cut.static_gap("r", P.MUD, ytop, ybot, 0.03)
        mud_b = cut.static_bore(P.MUD, ytop, ybot + 0.5, 0.03)
        bit = st.poly([(cx - 0.45, ybot + 0.5), (cx + 0.45, ybot + 0.5), (cx, ybot + 0.15)], P.WARN, 0.3)
        st.fade_in(base + [mud_l, mud_r, mud_b, bit], b.start, 0.5)
        # BHP gauge at the bottom
        gx = cx + 3.0
        frame = st.rect(gx, 0.2, 0.5, 5.8, P.PANEL2, 0.2)
        bhp = st.rect(gx, -2.7, 0.44, 3.0, P.MUD, 0.3, anchor="b")
        lab = st.text("bottom-hole\npressure", gx, 3.4, 0.2, P.TEXT, 0.3, kind="bold")
        st.fade_in([frame, bhp, lab], s[1], 0.4)
        # flow up the annulus, friction arrows down
        ups = []
        for y in (-2.0, -0.9, 0.2, 1.3):
            ups += [st.poly([(cut.gap_l[0] + 0.05, y - 0.09), (cut.gap_l[1] - 0.05, y - 0.09), ((cut.gap_l[0] + cut.gap_l[1]) / 2, y + 0.07)], P.PORE, 0.4),
                    st.poly([(cut.gap_r[0] + 0.05, y - 0.09), (cut.gap_r[1] - 0.05, y - 0.09), ((cut.gap_r[0] + cut.gap_r[1]) / 2, y + 0.07)], P.PORE, 0.4)]
        st.fade_in(ups, s[1] + 0.8, 0.3)
        loop_move(st, ups, s[1] + 0.8, s[4], 1.1, cycles=5)
        fr = []
        for y in (-1.6, -0.2, 1.2):
            fr += st.arrow(cut.hole[0] - 0.2, y + 0.35, cut.hole[0] - 0.2, y - 0.25, P.BAD, 0.06, 0.18, 0.5)
        frl = st.text("friction\nin the narrow gap", cut.hole[0] - 0.35, 0.2, 0.2, P.BAD, 0.5, align="r", kind="bold")
        st.fade_in(fr + [frl], s[2], 0.4)
        st.scale_to(bhp, s[3], s[3] + 1.0, sy=3.5)
        # right: BHP vs time chart
        c = Chart(st, 1.8, -2.6, 5.2, 4.8, (0, 10), (0, 1.0))
        frm = c.frame(xticks=[], yticks=[], xlabel="time", ylabel="bottom-hole pressure", grid=False)
        base_y, hi_y = 0.45, 0.72
        hyd = st.dashed(c.pt(0, base_y), c.pt(10, base_y), P.MUD, 0.035, 0.18, 0.1, 0.3)
        hl = c.label(10, base_y, "static: mud weight alone", 0.2, P.MUD, "r", dy=-0.25)
        tr1 = c.curve([0, 4.0], [hi_y, hi_y], P.PORE, 0.09, 0.4)
        tr2 = c.curve([4.0, 4.0, 6.0, 6.0], [hi_y, base_y, base_y, hi_y], P.BAD, 0.09, 0.4)
        tr3 = c.curve([6.0, 10.0], [hi_y, hi_y], P.PORE, 0.09, 0.4)
        on = c.label(1.8, hi_y, "pumps ON: ECD", 0.22, P.PORE, "c", dy=0.28)
        off = c.label(5.0, base_y, "connection:\npumps OFF", 0.2, P.BAD, "c", dy=-0.45)
        eq = st.text("ECD = MW + friction ΔP / (g · depth)", 4.4, 2.6, 0.26, P.TEXT, 0.5, kind="mono")
        st.fade_in(frm + hyd + [hl], s[3], 0.4)
        st.draw_on(tr1, s[3] + 0.2, s[3] + 1.6)
        st.fade_in(on, s[3] + 1.2, 0.4)
        st.fade_in(eq, s[4], 0.5)
        st.draw_on(tr2, s[5], s[5] + 1.6)
        st.draw_on(tr3, s[5] + 1.6, s[5] + 2.6)
        st.fade_in(off, s[5] + 0.8, 0.4)
        st.scale_to(bhp, s[5], s[5] + 0.8, sy=3.0)
        st.scale_to(bhp, s[5] + 2.0, s[5] + 2.6, sy=3.5)


# ---------------------------------------------------------------- 4.06 squeezed window + MPD
def beat_mpd(st, tl):
    b = tl["4.06"]
    s = b.sent
    with st.span(b.start, b.end):
        wc = WindowChart(st, x=-5.3, y=-3.0, w=5.4, h=6.3)
        objs = wc.axes() + [wc.curves()["pp"], wc.objs["fg"], wc.objs["pp_lbl"], wc.objs["fg_lbl"], wc.band()]
        st.fade_in(objs, b.start, 0.5)
        c = wc.c
        z = 4000
        off = st.rect(c.X(1.57), c.Y(z), 0.1, 0.5, P.PORE, 0.5)
        on = st.rect(c.X(1.74), c.Y(z), 0.1, 0.5, P.MUD, 0.5)
        offl = st.text("pumps off:\nstill above pore pressure", c.X(1.57) - 0.15, c.Y(z) - 0.85, 0.2, P.PORE, 0.5, align="r", kind="bold")
        onl = st.text("pumps on (ECD):\nunder the fracture limit", c.X(1.74) + 0.15, c.Y(z) + 0.8, 0.2, P.MUD, 0.5, align="r", kind="bold")
        st.fade_in([off, offl], s[1], 0.5)
        st.fade_in([on, onl], s[2], 0.5)
        sq = st.text("squeezed from both sides", c.X(1.35), c.Y(2700), 0.28, P.WARN, 0.5, kind="bold")
        st.fade_in(sq, s[0] + 0.3, 0.5)
        st.fade_in(st.text("sometimes no mud weight does both", c.X(1.4), c.Y(1500), 0.24, P.BAD, 0.5, kind="bold"), s[3], 0.5)
        # MPD schematic
        mx = 3.6
        cut = Cutaway(st, mx - 1.0, 2.6, -2.8, hole_w=1.6, pipe_w=0.7, rock_w=1.0)
        mpd = cut.draw(pipe_bottom=-2.4)
        mf = [cut.static_gap("l", P.MUD, 2.6, -2.8, 0.03), cut.static_gap("r", P.MUD, 2.6, -2.8, 0.03), cut.static_bore(P.MUD, 2.6, -2.4, 0.03)]
        rcd = st.rect(mx - 1.0, 2.75, 1.9, 0.35, P.BAD, 0.5)
        rl = st.text("sealed top: rotating control device", mx - 1.0, 3.3, 0.2, P.BAD, 0.5, kind="bold")
        line = st.line([(cut.hole[1] - 0.05, 2.5), (mx + 1.6, 2.5), (mx + 1.6, 1.4)], P.MUD, 0.1, 0.4)
        chk = st.poly([(mx + 1.3, 1.6), (mx + 1.9, 1.6), (mx + 1.6, 1.2)], P.WARN, 0.5)
        chl = st.text("choke", mx + 2.25, 1.4, 0.22, P.WARN, 0.5, align="l", kind="bold")
        st.fade_in(mpd + mf + [rcd, rl, line, chk, chl], s[4], 0.5)
        # mini traces: pump rate falls, choke closes, BHP flat
        c2 = Chart(st, mx + 0.1, -2.7, 3.2, 2.2, (0, 8), (0, 1))
        fr2 = c2.frame(xticks=[], yticks=[], grid=False)
        pump = c2.curve([0, 4, 4.4, 8], [0.85, 0.85, 0.15, 0.15], P.PORE, 0.07, 0.4)
        bhp = c2.curve([0, 8], [0.5, 0.5], P.MUD, 0.07, 0.4)
        c2.label(0.2, 0.9, "pump", 0.18, P.PORE, "l")
        c2.label(0.2, 0.62, "BHP: held flat", 0.18, P.MUD, "l")
        st.fade_in(fr2, s[4] + 2.0, 0.4)
        st.draw_on(pump, s[4] + 2.2, s[4] + 5.0)
        st.draw_on(bhp, s[4] + 2.2, s[4] + 5.0)
        st.scale_to(chk, s[4] + 3.8, s[4] + 4.6, sy=0.35)     # choke closes as the pump stops
        bpt = st.text("back pressure replaces the pump", mx + 1.8, -3.2, 0.2, P.WARN, 0.5, kind="bold")
        st.fade_in(bpt, s[4] + 3.8, 0.4)


def build(st, tl):
    F.header(st, tl)
    F.well_strip(st, 0.0, tl.dur, strings=["30in conductor", "20in surface casing", "13-3/8in intermediate"], marker=2000)
    beat_bha(st, tl)
    beat_steering(st, tl)
    beat_drag(st, tl)
    beat_mud(st, tl)
    beat_ecd(st, tl)
    beat_mpd(st, tl)
