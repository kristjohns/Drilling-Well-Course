"""Ch 3, beat 3.05: the two-barrier rule, and how the envelopes change during a live wireline job.

A well-barrier schematic drawn procedurally: reservoir, casing and cement, tubing with packer and downhole safety valve,
wellhead, tree, wireline BOP, lubricator and stuffing box, with the line running down to a toolstring.
  s1  the production envelopes: primary (blue) = packer, tubing, closed safety valve; secondary (red) = casing, cement,
      wellhead, tree with its master valves closed;
  s2  during the job the safety valve and tree valves stand open with the line through them: they cannot count;
  s3  the equipment on top takes their place;
  s4  primary now runs up through the tree and lubricator to the stuffing box; the secondary closes at the BOP rams;
      the tree (between the hanger and the BOP) is shared by both;
  s5  everything on the stack is pressure-tested (low then high, hold);
  s6  the split is set by NORSOK D-010 and operator procedures;
  s7  a barrier fails (the stuffing box leaks): the BOP closes on the line, the job stops until it is restored.
"""
from __future__ import annotations
import math

from scenes.common import palette as P
from scenes.common import kit as K
from scenes.common import pdraw as D
from scenes.common.look import darken, lighten
from scenes.common.stage import hex_rgb


def _partial(pts, f):
    """The first fraction f (0..1) of a polyline, by length."""
    if f >= 1.0:
        return pts
    if f <= 0.0:
        return pts[:1]
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:])]
    L = sum(seg) * f
    out = [pts[0]]
    for (a, b), l in zip(zip(pts[:-1], pts[1:]), seg):
        if L <= l:
            k = L / l if l > 0 else 0
            out.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
            return out
        out.append(b)
        L -= l
    return out


def b305(st, tl):
    b = tl["3.05"]
    s = b.sent
    with st.span(b.start, b.end):
        cx = -3.4
        # vertical layout (world y)
        y_sb0, y_sb1 = 2.95, 3.4              # stuffing box
        y_lub0 = 1.6                          # lubricator: y_lub0 .. y_sb0
        y_bop0, y_bop1 = 1.0, 1.6             # wireline BOP
        y_tr0, y_tr1 = -0.15, 1.0             # tree
        y_wh0, y_wh1 = -0.5, -0.15            # wellhead (tubing hanger inside)
        y_dhsv = -1.15
        y_pk = -2.45
        y_res = -2.75
        y_tool = -1.95
        ci, cw = 0.78, 0.09                   # casing inner half-width, wall
        ti, tw_ = 0.26, 0.06                  # tubing
        cem = 0.22
        T_in = b.start + 0.2
        t1 = b.word(1, "two tested barriers")
        t_env1 = (t1 - 0.2, t1 + 1.6)          # production primary
        t_env2 = (t1 + 1.0, t1 + 2.8)          # production secondary
        t_open = s[2] + 0.6
        t_fade_prod = s[3] - 0.2
        t_top = s[3] + 0.2
        t_new1 = (b.word(4, "the stuffing box") - 0.2, b.word(4, "the stuffing box") + 2.6)
        t_new2 = (b.word(4, "the blowout preventer") - 0.2, b.word(4, "the blowout preventer") + 2.6)
        t_shared = b.word(4, "shared by both") - 0.3
        t_test = s[5]
        t_fail = s[7] + 0.4
        t_rams = t_fail + 1.4

        # outlines (offset so the two colours never sit on top of each other)
        prod_primary = [(cx - ci + 0.06, y_pk - 0.17), (cx + ci - 0.06, y_pk - 0.17), (cx + ci - 0.06, y_pk + 0.17), (cx + ti + tw_ + 0.04, y_pk + 0.17),
                        (cx + ti + tw_ + 0.04, y_dhsv + 0.12), (cx - ti - tw_ - 0.04, y_dhsv + 0.12), (cx - ti - tw_ - 0.04, y_pk + 0.17),
                        (cx - ci + 0.06, y_pk + 0.17), (cx - ci + 0.06, y_pk - 0.17)]
        mv_y = y_tr0 + 0.32                   # lower master valve
        prod_secondary = [(cx - ci - cw - cem - 0.05, y_pk - 0.22), (cx - ci - cw - cem - 0.05, y_wh0 - 0.05), (cx - 1.05, y_wh0 - 0.05),
                          (cx - 1.05, y_wh1 + 0.02), (cx - 0.58, y_wh1 + 0.02), (cx - 0.58, mv_y + 0.12), (cx + 0.58, mv_y + 0.12),
                          (cx + 0.58, y_wh1 + 0.02), (cx + 1.05, y_wh1 + 0.02), (cx + 1.05, y_wh0 - 0.05), (cx + ci + cw + cem + 0.05, y_wh0 - 0.05),
                          (cx + ci + cw + cem + 0.05, y_pk - 0.22), (cx - ci - cw - cem - 0.05, y_pk - 0.22)]
        job_primary = [(cx - ci + 0.06, y_pk - 0.17), (cx + ci - 0.06, y_pk - 0.17), (cx + ci - 0.06, y_pk + 0.17), (cx + ti + tw_ + 0.04, y_pk + 0.17),
                       (cx + ti + tw_ + 0.04, y_wh1 - 0.02), (cx + 0.36, y_wh1 - 0.02), (cx + 0.36, y_bop0 + 0.02), (cx + 0.33, y_lub0),
                       (cx + 0.33, y_sb1 + 0.06), (cx - 0.33, y_sb1 + 0.06), (cx - 0.33, y_lub0), (cx - 0.36, y_bop0 + 0.02),
                       (cx - 0.36, y_wh1 - 0.02), (cx - ti - tw_ - 0.04, y_wh1 - 0.02), (cx - ti - tw_ - 0.04, y_pk + 0.17), (cx - ci + 0.06, y_pk + 0.17),
                       (cx - ci + 0.06, y_pk - 0.17)]
        y_ram = (y_bop0 + y_bop1) / 2
        job_secondary = [(cx - ci - cw - cem - 0.05, y_pk - 0.22), (cx - ci - cw - cem - 0.05, y_wh0 - 0.05), (cx - 1.05, y_wh0 - 0.05),
                         (cx - 1.05, y_wh1 + 0.02), (cx - 0.62, y_wh1 + 0.02), (cx - 0.62, y_bop0), (cx - 0.72, y_bop0), (cx - 0.72, y_ram + 0.1),
                         (cx + 0.72, y_ram + 0.1), (cx + 0.72, y_bop0), (cx + 0.62, y_bop0), (cx + 0.62, y_wh1 + 0.02), (cx + 1.05, y_wh1 + 0.02),
                         (cx + 1.05, y_wh0 - 0.05), (cx + ci + cw + cem + 0.05, y_wh0 - 0.05), (cx + ci + cw + cem + 0.05, y_pk - 0.22),
                         (cx - ci - cw - cem - 0.05, y_pk - 0.22)]

        def gate(c, look, x, y, open_, a, horiz=False):
            """A gate valve symbol on the bore: body, gate (raised when open), handwheel stem."""
            D.steel(c, x - 0.5, y - 0.13, x + 0.5, y + 0.13, P.STEEL_DK, a)
            D.fill(c, x - 0.22, y - 0.13, x + 0.22, y + 0.13, darken(hex_rgb(P.BG), 0.3), a)
            go = 0.24 * open_
            D.flat(c, x - 0.6 - go, y - 0.08, x - 0.22 - go + 0.44 * (1 - open_), y + 0.08, P.WARN if open_ < 0.5 else P.STEEL, a, r=0.02)

        def draw(c, t, look):
            a = D.vis(t, T_in, None, 0.6)
            if a <= 0:
                return
            # rock, cement, reservoir
            D.fill(c, cx - 2.3, y_res, cx + 2.3, y_wh0, P.ROCK, 0.45 * a)
            D.fill(c, cx - 2.3, -3.5, cx + 2.3, y_res, P.SAND, 0.8 * a)
            D.fill(c, cx - 2.3, y_wh0, cx + 2.3, y_wh0 + 0.04, P.SEABED, 0.9 * a)
            for sd in (-1, 1):
                D.fill(c, cx + sd * (ci + cw), -3.35, cx + sd * (ci + cw + cem), y_wh0, P.CEMENT, 0.85 * a)
            D.fill(c, cx - ci, -3.35, cx + ci, y_wh0, darken(hex_rgb(P.BG), 0.3), a)
            for sd in (-1, 1):
                D.steel(c, cx + sd * ci, -3.35, cx + sd * (ci + cw), y_wh0, P.STEEL_DK, a)
            for k in range(3):
                yy = -3.15 + 0.17 * k
                for sd in (-1, 1):
                    D.fill(c, cx + sd * (ci + cw), yy - 0.03, cx + sd * (ci + cw + cem + 0.6), yy + 0.03, darken(hex_rgb(P.BG), 0.3), a)
            # tubing and well fluid
            D.fluid(c, cx - ti, y_pk - 0.1, cx + ti, y_wh1, P.OIL, 0.45 * a)
            for sd in (-1, 1):
                D.steel(c, cx + sd * ti, y_pk - 0.15, cx + sd * (ti + tw_), y_wh1, P.STEEL, a)
            # packer
            for sd in (-1, 1):
                D.flat(c, cx + sd * (ti + tw_), y_pk - 0.14, cx + sd * ci, y_pk + 0.14, "#5a6b8c", a, r=0.02)
            # downhole safety valve: body and flapper (closed until the job starts, then open)
            fo = D.ramp(t, t_open - 0.4, t_open + 0.4)
            for sd in (-1, 1):
                D.steel(c, cx + sd * ti, y_dhsv - 0.18, cx + sd * (ti + 0.13), y_dhsv + 0.18, P.STEEL_DK, a)
            ang = math.radians(-90 * fo)
            D.stroke(c, [(cx - ti, y_dhsv), (cx - ti + 2 * ti * math.cos(ang), y_dhsv + 2 * ti * math.sin(ang))], P.WARN, 0.06, a)
            D.stroke(c, [(cx + ti + 0.13, y_dhsv), (cx + ci - 0.05, y_dhsv), (cx + ci - 0.05, y_wh0 + 0.02)], P.PORE, 0.015, 0.7 * a)
            # wellhead
            D.steel(c, cx - 1.1, y_wh0, cx + 1.1, y_wh1, P.STEEL_DK, a)
            D.fill(c, cx - ti, y_wh0, cx + ti, y_wh1, darken(hex_rgb(P.BG), 0.3), a)
            D.steel(c, cx - 0.42, y_wh0 + 0.05, cx - ti, y_wh1, P.STEEL, a)          # tubing hanger
            D.steel(c, cx + ti, y_wh0 + 0.05, cx + 0.42, y_wh1, P.STEEL, a)
            # tree: body with lower and upper master valves, the wing outlet and the swab valve at the top
            D.steel(c, cx - 0.55, y_tr0, cx + 0.55, y_tr1, P.STEEL, a)
            D.fill(c, cx - 0.2, y_tr0, cx + 0.2, y_tr1, darken(hex_rgb(P.BG), 0.3), a)
            D.steel(c, cx + 0.55, y_tr0 + 0.62, cx + 1.35, y_tr0 + 0.8, P.STEEL, a)
            vo = D.ramp(t, t_open - 0.6, t_open + 0.2)
            for yy in (mv_y, mv_y + 0.32, y_tr1 - 0.15):
                D.steel(c, cx - 0.2, yy - 0.06, cx + 0.2, yy + 0.06, P.STEEL_DK, a * (1 - vo))
                D.flat(c, cx - 0.78, yy - 0.07, cx - 0.55, yy + 0.07, P.WARN if vo > 0.5 else P.STEEL_DK, a, r=0.02)
            # wireline BOP: body and rams (closing at the failure)
            D.steel(c, cx - 0.65, y_bop0, cx + 0.65, y_bop1, P.STEEL_DK, a)
            D.fill(c, cx - 0.2, y_bop0, cx + 0.2, y_bop1, darken(hex_rgb(P.BG), 0.3), a)
            rc = D.ramp(t, t_rams, t_rams + 0.6)
            for sd in (-1, 1):
                x_in = cx + sd * (0.2 - 0.18 * rc)
                D.flat(c, x_in, y_ram - 0.1, cx + sd * 0.95, y_ram + 0.1, P.BAD, a, r=0.02)
            # lubricator and stuffing box
            for sd in (-1, 1):
                D.steel(c, cx + sd * 0.2, y_lub0, cx + sd * 0.27, y_sb0, P.STEEL, a)
            D.fill(c, cx - 0.2, y_lub0, cx + 0.2, y_sb0, darken(hex_rgb(P.BG), 0.25), a)
            D.steel(c, cx - 0.3, y_sb0, cx + 0.3, y_sb1, P.STEEL_DK, a)
            D.rubber_stack(c, cx - 0.2, cx + 0.2, y_sb0 + 0.06, y_sb1 - 0.06, 3, a)
            # the line and the toolstring (the wire runs through everything)
            ja = D.vis(t, s[2] - 0.2, None, 0.6)
            D.stroke(c, [(cx, 3.8), (cx, y_tool + 0.7)], P.WIRE, 0.025, ja * a)
            D.steel(c, cx - 0.1, y_tool, cx + 0.1, y_tool + 0.7, P.STEEL_DK, ja * a)
            D.flat(c, cx - 0.12, y_tool - 0.25, cx + 0.12, y_tool, P.WARN, ja * a, r=0.02)
            # ---- the production envelopes (s1), dimming when the job opens the valves
            ap = a * (1.0 - 0.75 * D.ramp(t, t_fade_prod, t_fade_prod + 0.8)) * (1.0 - D.ramp(t, t_new1[0], t_new1[0] + 0.6))
            f1 = D.lin(t, *t_env1)
            f2 = D.lin(t, *t_env2)
            if f1 > 0:
                D.stroke(c, _partial(prod_primary, f1), P.PRIMARY_B, 0.055, ap)
            if f2 > 0:
                D.stroke(c, _partial(prod_secondary, f2), P.SECOND_B, 0.055, ap)
            # the closed safety valve and master valve broken once open
            if t > t_open:
                k = D.ramp(t, t_open, t_open + 0.5)
                D.flash(c, look, cx, y_dhsv + 0.12, 0.45, P.BAD, (t - t_open) / 0.9)
                D.flash(c, look, cx, mv_y + 0.12, 0.45, P.BAD, (t - t_open - 0.3) / 0.9)
            # ---- the job envelopes (s4)
            g1 = D.lin(t, *t_new1)
            g2 = D.lin(t, *t_new2)
            fail = D.ramp(t, t_fail, t_fail + 0.5)
            if g1 > 0:
                col1 = P.PRIMARY_B if fail < 0.5 else P.BAD
                D.stroke(c, _partial(job_primary, g1), col1, 0.06, a)
            if g2 > 0:
                D.stroke(c, _partial(job_secondary, g2), P.SECOND_B, 0.06, a)
            # shared elements (tree, wellhead): hatched in both colours
            sh = D.vis(t, t_shared, None, 0.6)
            if sh > 0:
                D.hatch(c, cx - 0.55, y_tr0, cx - 0.2, y_tr1, P.PRIMARY_B, 0.55 * sh * a, spacing=0.12, w=0.02)
                D.hatch(c, cx + 0.2, y_tr0, cx + 0.55, y_tr1, P.SECOND_B, 0.55 * sh * a, spacing=0.12, w=0.02)
            # ---- failure: the stuffing box leaks
            if t > t_fail - 0.2:
                for i in range(7):
                    ph = ((t - t_fail) * 1.6 + i / 7.0) % 1.0
                    ang_ = math.radians(30 + 120 * (i / 6.0))
                    r = 0.15 + 0.7 * ph
                    D.disc(c, cx + r * math.cos(ang_), y_sb1 + 0.05 + r * math.sin(ang_) * 0.7, 0.035, P.OIL, a * (1 - ph) * D.lin(t, t_fail, t_fail + 0.3))
                D.flash(c, look, cx, y_ram, 0.55, P.SAFE, (t - t_rams - 0.6) / 0.9)

        st.procedural(b.start, b.end, 0.5, draw)

        # ------------------------------------------------------------------ labels and explanations
        lx = cx + 1.65
        labels = [("stuffing box", (y_sb0 + y_sb1) / 2, cx + 0.3, s[3] + 0.3),
                  ("lubricator", 2.25, cx + 0.27, s[3] + 0.6),
                  ("wireline BOP", y_ram + 0.05, cx + 0.95, s[3] + 0.9),
                  ("tree", 0.45, cx + 0.55, s[1] + 3.0),
                  ("wellhead and hanger", y_wh0 + 0.17, cx + 1.1, s[1] + 3.3),
                  ("downhole safety valve", y_dhsv, cx + ti + 0.13, s[1] + 2.2),
                  ("tubing", -1.7, cx + ti + tw_, s[1] + 2.4),
                  ("packer", y_pk, cx + ci, s[1] + 2.6),
                  ("casing and cement", -3.0, cx + ci + cw + cem, s[1] + 3.6)]
        for text, y, tx, t0 in labels:
            K.show(st, K.callout(st, text, lx, y, tx, y, size=0.17, align="l", z=1.1), t0, None, 0.35)
        # legend (left)
        lp = K.tag(st, -7.75, 2.9, "PRIMARY", color=P.PRIMARY_B, fg=P.BG, size=0.2, z=1.0, align="l")
        ls = K.tag(st, -7.75, 2.35, "SECONDARY", color=P.SECOND_B, fg=P.BG, size=0.2, z=1.0, align="l")
        K.show(st, lp, t_env1[0] + 0.3, None, 0.4)
        K.show(st, ls, t_env2[0] + 0.3, None, 0.4)
        prod = K.note(st, "producing well", -7.75, 3.4, 0.17, P.MUTED, align="l", kind="bold")
        job = K.note(st, "during the wireline job", -7.75, 3.4, 0.17, P.WARN, align="l", kind="bold")
        K.show(st, prod, t_env1[0], t_new1[0] - 0.2, 0.3)
        K.show(st, job, t_new1[0], None, 0.3)
        # s2: open, the line through: cannot count
        xo = cx + 1.65
        op1 = K.tag(st, xo + 2.9, y_dhsv, "OPEN: cannot count", color=P.BAD, fg=P.BG, size=0.16, z=1.2, align="l")
        op2 = K.tag(st, xo + 2.9, 0.45, "OPEN: cannot count", color=P.BAD, fg=P.BG, size=0.16, z=1.2, align="l")
        K.show(st, op1, t_open + 0.1, t_new1[0], 0.35)
        K.show(st, op2, t_open + 0.4, t_new1[0], 0.35)
        top = K.tag(st, xo + 2.9, 2.25, "the equipment on top takes their place", color=P.WARN, fg=P.BG, size=0.17, z=1.2, align="l")
        K.show(st, top, t_top, t_new1[0] + 0.5, 0.35)
        n1 = K.tag(st, xo + 2.9, (y_sb0 + y_sb1) / 2, "closes the primary at the top", color=P.PRIMARY_B, fg=P.BG, size=0.16, z=1.2, align="l")
        n2 = K.tag(st, xo + 2.9, y_ram + 0.05, "closes on the line: secondary", color=P.SECOND_B, fg=P.BG, size=0.16, z=1.2, align="l")
        n3 = K.tag(st, xo + 2.9, 0.45, "shared by both", color=P.PANEL2, size=0.16, z=1.2, align="l")
        K.show(st, n1, t_new1[0] + 0.6, t_test - 0.2, 0.35)
        K.show(st, n2, t_new2[0] + 0.6, t_test - 0.2, 0.35)
        K.show(st, n3, t_shared + 0.3, t_test - 0.2, 0.35)

        # ------------------------------------------------------------------ s5: the pressure test, before the well is opened
        gx0, gx1, gy0, gy1 = 1.2, 7.55, -3.35, -0.95
        tt0, tt1 = t_test + 0.4, t_test + 4.2

        def test_curve(u):
            # low test, hold, bleed, high test, hold
            if u < 0.12:
                return 0.25 * u / 0.12
            if u < 0.32:
                return 0.25
            if u < 0.4:
                return 0.25 - 0.25 * (u - 0.32) / 0.08
            if u < 0.58:
                return 0.95 * (u - 0.4) / 0.18
            return 0.95 - 0.01 * (u - 0.58)

        def draw_test(c, t, look):
            a = D.vis(t, t_test, s[7] - 0.2, 0.5)
            if a <= 0:
                return
            D.flat(c, gx0, gy0, gx1, gy1, P.PANEL, 0.92 * a, r=0.1)
            D.text(c, look, "PRESSURE TEST, BEFORE THE WELL IS OPENED", gx0 + 0.25, gy1 - 0.2, 0.13, P.MUTED, a, align="l", kind="bold")
            px0, px1, py0, py1 = gx0 + 0.35, gx1 - 0.3, gy0 + 0.3, gy1 - 0.6
            D.stroke(c, [(px0, py0), (px1, py0)], P.GRID, 0.012, a)
            D.stroke(c, [(px0, py0), (px0, py1)], P.GRID, 0.012, a)
            u = D.lin(t, tt0, tt1)
            if u > 0:
                n = max(int(u * 120), 2)
                pts = [(px0 + (px1 - px0) * (i / (n - 1)) * u, py0 + (py1 - py0) * test_curve((i / (n - 1)) * u)) for i in range(n)]
                D.stroke(c, pts, P.SAFE, 0.045, a)
                D.glow(c, look, pts[-1][0], pts[-1][1], 0.1, P.SAFE, 0.8 * a)
            for uu, lab, dy in ((0.22, "low-pressure test: hold", 0.22), (0.78, "high-pressure test: hold", -0.25)):
                if u > uu:
                    x = px0 + (px1 - px0) * uu
                    y = py0 + (py1 - py0) * test_curve(uu)
                    D.text(c, look, lab, x, y + dy, 0.13, P.TEXT, a * D.lin(u, uu, uu + 0.08))
            D.text(c, look, "time", px1 - 0.2, py0 - 0.15, 0.12, P.MUTED, a)

        st.procedural(b.start, b.end, 0.9, draw_test)
        for i, (y, t0) in enumerate((((y_sb0 + y_sb1) / 2, tt1 - 0.6), (y_ram + 0.05, tt1 - 0.3), (0.45, tt1))):
            K.show(st, K.tag(st, cx - 1.0, y, "TESTED", color=P.SAFE, fg=P.BG, size=0.15, z=1.3, align="r"), t0, None, 0.35)
        nor = K.tag(st, 1.2, 3.35, "the exact split: NORSOK D-010 + operator procedures", color=P.NO_BADGE, fg=P.TEXT,
                    size=0.17, z=1.2, align="l")
        K.show(st, nor, s[6] + 0.2, None, 0.4)
        # s7: failure
        fl = K.tag(st, cx + 0.45, 3.75 - 0.2, "leak", color=P.BAD, fg=P.BG, size=0.16, z=1.3, align="l")
        K.show(st, fl, t_fail + 0.2, None, 0.3)
        hold = K.tag(st, xo + 2.9, y_ram + 0.05, "BOP closes: the secondary holds", color=P.SAFE, fg=P.BG, size=0.17, z=1.3, align="l")
        K.show(st, hold, t_rams + 0.5, None, 0.35)
        stop = K.tag(st, 1.2, -2.15, "barrier failed: the job stops until it is restored", color=P.BAD, fg=P.BG, size=0.22, z=1.3, align="l")
        K.show(st, stop, t_fail + 0.3, None, 0.4)
