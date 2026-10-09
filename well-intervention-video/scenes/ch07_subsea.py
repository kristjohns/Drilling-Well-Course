"""Ch 7: Subsea: intervention from a vessel.

7.01 the tree is on the seabed (300 m down): through open water without a riser, or inside a riser
7.02 vertical tree (straight bore, tree lifts off alone) versus horizontal tree (hanger inside the tree, plugs, BOP and riser needed)
7.03 riserless light well intervention: moonpool, well control package, lubricator, pressure control head, heave compensation, ROV
7.04 riser-based light well intervention: a pressure-tight conduit, coiled tubing on deck, a safety package that shears and disconnects
7.05 the ladder: RLWI vessel, riser-based vessel, drilling rig; the vessels exist because they are far cheaper than a rig
"""
from __future__ import annotations
import math

from scenes.common import palette as P, model as M, furniture as F
from scenes.common import kit as K

TITLE = "Subsea: intervention from a vessel"

SEA_TOP, SEABED = 1.9, -3.2


def _sea(st, t0, x0=-8.0, x1=8.0):
    sea = st.rect((x0 + x1) / 2, (SEA_TOP + SEABED) / 2, x1 - x0, SEA_TOP - SEABED, P.SEA, 0.0, alpha=0.55)
    bed = st.rect((x0 + x1) / 2, SEABED - 0.2, x1 - x0, 0.4, P.SEABED, 0.05)
    surf = st.rect((x0 + x1) / 2, SEA_TOP, x1 - x0, 0.03, "#7fb2ff", 0.1, alpha=0.7)
    st.fade_in([sea, bed, surf], t0, 0.5)
    return [sea, bed, surf]


def _subsea_tree(st, cx, z=0.4):
    base = [st.rect(cx, SEABED + 0.12, 1.1, 0.24, P.STEEL_DK, z, role="steel"), st.rect(cx, SEABED + 0.5, 0.7, 0.52, P.STEEL, z, role="steel"),
            st.rect(cx, SEABED + 0.95, 0.5, 0.38, P.STEEL_DK, z, role="steel"), st.rect(cx + 0.6, SEABED + 0.5, 0.5, 0.16, P.STEEL, z - 0.01, role="steel"),
            st.rect(cx, SEABED + 1.25, 0.34, 0.22, P.STEEL, z, role="steel")]
    return base


# ====================================================================================================== 7.01
def b701(st, tl):
    b = tl["7.01"]
    s = b.sent
    with st.span(b.start, b.end):
        _sea(st, b.start + 0.1)
        xl, xr = -4.6, 1.2
        t_l = _subsea_tree(st, xl)
        t_r = _subsea_tree(st, xr)
        K.show(st, t_l + t_r, s[1] - 0.2, None, 0.5)
        # 300 m depth marker
        dim = st.line([(-7.4, SEA_TOP), (-7.4, SEABED)], P.MUTED, 0.03, 0.5, role="hair")
        dt = st.text("300 m", -7.4, (SEA_TOP + SEABED) / 2, 0.24, P.TEXT, 0.6, kind="bold")
        K.show(st, [dim, dt], s[1], None, 0.4)
        lt = K.callout(st, "the tree is on the seabed", -3.5, SEABED + 0.7, xl + 0.4, SEABED + 0.6, size=0.2, align="l")
        K.show(st, lt, s[1] + 0.5, s[2], 0.4)
        nd = K.note(st, "no deck beside it to stand a wireline unit on", -3.0, -2.0, 0.21, P.MUTED, align="l")
        K.show(st, nd, b.word(1, "no deck"), s[2], 0.4)
        # vessels
        v_l = K.vessel(st, xl + 0.32, SEA_TOP, 0.75)
        v_r = K.vessel(st, xr + 0.32, SEA_TOP, 0.75)
        gv = v_l.hull + v_l.moonpool + v_l.derrick + v_l.crane + v_r.hull + v_r.moonpool + v_r.derrick + v_r.crane
        K.show(st, gv, s[2] - 0.2, None, 0.6)
        st.fade_in([], 0)
        q = K.note(st, "a vessel connected to a tree it cannot touch", -1.8, 3.75, 0.23, P.TEXT, align="c")
        K.show(st, q, s[2] + 0.2, s[3], 0.4)
        # two ways
        wa = K.tag(st, xl, -3.75, "through open water: no riser", color=P.PRIMARY_B, fg=P.BG, size=0.24, z=0.9)
        wb = K.tag(st, xr + 0.5, -3.75, "inside a riser", color=P.SAFE, fg=P.BG, size=0.24, z=0.9)
        K.show(st, wa, s[4] - 0.1, None, 0.4)
        K.show(st, wb, b.word(5, "inside a riser"), None, 0.4)
        line = st.rect(xl, SEA_TOP + 0.1, 0.03, 0.001, P.WIRE, 0.5, anchor="t", role="steel")
        K.show(st, [line], s[4], None, 0.1)
        st.scale_to(line, s[4] + 0.2, s[4] + 2.0, sy=SEA_TOP + 0.1 - (SEABED + 1.45), interp="LINEAR")
        riser = st.rect(xr, SEA_TOP + 0.1, 0.34, 0.001, P.STEEL, 0.5, anchor="t", role="steel")
        K.show(st, [riser], b.word(5, "a pipe from the vessel"), None, 0.1)
        st.scale_to(riser, b.word(5, "a pipe from the vessel"), b.word(5, "a pipe from the vessel") + 2.2, sy=SEA_TOP + 0.1 - (SEABED + 1.45), interp="LINEAR")


# ====================================================================================================== 7.02
# 7.02 (vertical and horizontal trees) lives in scenes/x_ch07_trees.py
from scenes.x_ch07_trees import b702  # noqa: E402


# ====================================================================================================== 7.03
def b703(st, tl):
    b = tl["7.03"]
    s = b.sent
    with st.span(b.start, b.end):
        _sea(st, b.start + 0.1)
        vcx = -3.4
        v = K.vessel(st, vcx, SEA_TOP, 0.8)
        mp_x = vcx - 0.4 * 0.8
        tree = _subsea_tree(st, mp_x)
        K.show(st, v.hull + v.moonpool + v.derrick + v.crane + tree, b.start + 0.2, None, 0.6)
        vessel_parts = v.hull + v.moonpool + v.derrick + v.crane
        # the stack: well control package, lubricator, pressure control head (one lift)
        y_land = SEABED + 1.35
        wcp = [st.rect(mp_x, y_land + 0.45, 0.95, 0.9, P.STEEL_DK, 0.5, role="steel"), st.rect(mp_x, y_land + 0.45, 0.26, 0.9, P.BG, 0.52),
               st.rect(mp_x - 0.35, y_land + 0.45, 0.3, 0.2, P.BAD, 0.55, role="solid"), st.rect(mp_x + 0.35, y_land + 0.45, 0.3, 0.2, P.BAD, 0.55, role="solid")]
        lub = [st.rect(mp_x, y_land + 1.6, 0.4, 1.4, P.STEEL, 0.5, role="steel"), st.rect(mp_x, y_land + 1.6, 0.18, 1.4, P.BG, 0.52)]
        pch = [st.rect(mp_x, y_land + 2.5, 0.62, 0.5, P.GREASE, 0.55, role="solid"), st.text("PCH", mp_x, y_land + 2.5, 0.14, P.BG, 0.6, kind="bold")]
        stack = wcp + lub + pch
        D = (SEA_TOP + 0.8) - y_land
        K.show(st, stack, s[1] - 0.4, None, 0.1)
        st.move(stack, s[1] - 0.4, s[1] - 0.39, dy=D)
        st.move(stack, s[1] + 0.3, s[1] + 5.2, dy=-D, interp="LINEAR")
        # labels
        def lab(text, y, tx, t, t1=None, x=-1.2):
            g = K.callout(st, text, x, y, tx, y, size=0.2, align="l")
            K.show(st, g, t, t1, 0.4)
        lab("well control package", y_land + 0.45, mp_x + 0.5, b.word(1, "well control package") + 3.0, s[2])
        lab("lubricator", y_land + 1.6, mp_x + 0.25, b.word(1, "lubricator") + 3.0, s[2])
        lab("pressure control head", y_land + 2.5, mp_x + 0.35, b.word(1, "pressure control head") + 3.0, s[2])
        # the line runs through open water to the stack
        t2 = s[2]
        line = st.rect(mp_x, SEA_TOP + 0.1, 0.03, 0.001, P.WIRE, 0.6, anchor="t", role="steel")
        K.show(st, [line], t2, None, 0.1)
        st.scale_to(line, t2 + 0.3, t2 + 2.2, sy=SEA_TOP + 0.1 - (y_land + 2.75), interp="LINEAR")
        lt = K.note(st, "the line runs through open sea", mp_x + 0.9, 0.0, 0.21, P.TEXT, align="l")
        K.show(st, lt, t2 + 0.3, s[3], 0.4)
        # sentence 3: rams close on the line, grease, glycol against hydrates
        t3 = s[3]
        st.move(wcp[2], t3 + 0.3, t3 + 0.8, dx=+0.12)
        st.move(wcp[3], t3 + 0.3, t3 + 0.8, dx=-0.12)
        gl = K.callout(st, "glycol injection: no hydrates", mp_x + 1.4, y_land + 1.2, mp_x + 0.25, y_land + 1.1, color=P.HYDRATE, fg=P.BG, size=0.2, align="l")
        gr = K.callout(st, "grease keeps the seal tight", mp_x + 1.4, y_land + 2.0, mp_x + 0.3, y_land + 2.3, color=P.GREASE, fg=P.BG, size=0.2, align="l")
        va = K.callout(st, "valves can close on the line", mp_x + 1.4, y_land + 0.3, mp_x + 0.45, y_land + 0.45, size=0.2, align="l")
        K.show(st, gl, b.word(3, "glycol"), s[4], 0.4)
        K.show(st, gr, b.word(3, "grease"), s[4], 0.4)
        K.show(st, va, t3, s[4], 0.4)
        # sentence 4: heave: the vessel rises and falls, the stack does not; an ROV watches
        t4 = s[4]
        for k in range(5):
            st.move(vessel_parts, t4 + 0.3 + k * 1.4, t4 + 1.0 + k * 1.4, dy=+0.14)
            st.move(vessel_parts, t4 + 1.0 + k * 1.4, t4 + 1.7 + k * 1.4, dy=-0.14)
        wave = st.line([(-7.8 + 0.4 * k, SEA_TOP + 0.04 * ((-1) ** k)) for k in range(41)], "#9cc4ff", 0.03, 0.2, role="hair")
        K.show(st, [wave], t4, None, 0.4)
        hv = K.tag(st, vcx + 3.2, 3.2, "heave compensation", color=P.SAFE, fg=P.BG, size=0.22, z=0.9)
        K.show(st, hv, t4, None, 0.4)
        rov = [st.rect(mp_x + 1.6, y_land + 0.3, 0.7, 0.4, P.WARN, 0.6, role="solid"), st.text("ROV", mp_x + 1.6, y_land + 0.3, 0.15, P.BG, 0.65, kind="bold")]
        teth = st.line([(mp_x + 1.25, y_land + 0.35), (mp_x + 0.7, y_land + 1.1), (mp_x + 0.5, SEA_TOP - 0.2)], P.MUTED, 0.02, 0.3, role="hair")
        K.show(st, rov + [teth], b.word(4, "ROV"), None, 0.5)
        # sentence 5: toolstring runs down the line into the tree
        t5 = s[5]
        tool = st.rect(mp_x, SEA_TOP - 0.2, 0.14, 0.4, P.WARN, 0.7, role="solid")
        K.show(st, [tool], t5, None, 0.3)
        st.move(tool, t5 + 0.4, t5 + 4.2, to=(mp_x, SEABED + 0.5), interp="LINEAR")
        tt = K.note(st, "slickline or electric line, as before", mp_x + 1.1, 1.7, 0.21, P.TEXT, align="l")
        K.show(st, tt, t5, None, 0.4)


# ====================================================================================================== 7.04
def b704(st, tl):
    b = tl["7.04"]
    s = b.sent
    with st.span(b.start, b.end):
        _sea(st, b.start + 0.1)
        vcx = -3.2
        v = K.vessel(st, vcx, SEA_TOP, 0.9)
        mp_x = vcx - 0.36
        tree = _subsea_tree(st, mp_x)
        # equipment on deck: reel + injector over the moonpool
        reel = K.drum(st, vcx + 1.1, SEA_TOP + 1.25, 0.5, turns=3, color=P.STEEL)
        inj = [st.rect(mp_x, SEA_TOP + 1.35, 0.8, 0.8, P.PANEL2, 0.65, role="card"), st.text("injector", mp_x, SEA_TOP + 1.35, 0.14, P.TEXT, 0.7)]
        gdeck = [st.line([(vcx + 0.7, SEA_TOP + 1.2), (mp_x + 0.4, SEA_TOP + 1.5)], P.STEEL, 0.05, 0.62)]
        vessel_parts = v.hull + v.moonpool + v.derrick + v.crane + reel.body + reel.turns + inj + gdeck
        # the riser from the vessel to a safety package on the tree
        y_pk = SEABED + 1.55
        riser_up = st.rect(mp_x, (SEA_TOP + 0.9 + y_pk + 0.65) / 2, 0.42, SEA_TOP + 0.9 - (y_pk + 0.65), P.STEEL, 0.5, role="steel")
        riser_core = st.rect(mp_x, (SEA_TOP + 0.9 + y_pk + 0.65) / 2, 0.2, SEA_TOP + 0.9 - (y_pk + 0.65), P.BG, 0.52)
        ct_line = st.rect(mp_x, (SEA_TOP + 0.9 + y_pk) / 2, 0.05, SEA_TOP + 0.9 - y_pk, P.WIRE, 0.58, role="steel")
        pk = [st.rect(mp_x, y_pk + 0.0, 1.1, 0.8, P.STEEL_DK, 0.5, role="steel"), st.rect(mp_x, y_pk, 0.22, 0.8, P.BG, 0.52),
              st.rect(mp_x - 0.4, y_pk - 0.12, 0.4, 0.2, P.BAD, 0.55, role="solid"), st.rect(mp_x + 0.4, y_pk - 0.12, 0.4, 0.2, P.BAD, 0.55, role="solid"),
              st.rect(mp_x, y_pk + 0.3, 1.2, 0.1, P.WARN, 0.55, role="solid")]
        K.show(st, vessel_parts + tree + [riser_up, riser_core, ct_line] + pk, b.start + 0.2, None, 0.6)
        l1 = K.callout(st, "coiled tubing injector on deck", vcx + 2.2, SEA_TOP + 2.0, mp_x + 0.4, SEA_TOP + 1.6, size=0.2, align="l")
        l2 = K.callout(st, "riser: a pressure-tight pipe to the tree", mp_x + 1.0, 0.0, mp_x + 0.22, 0.0, size=0.2, align="l")
        l3 = K.callout(st, "safety package: shear rams + disconnect", mp_x + 1.0, y_pk + 0.05, mp_x + 0.55, y_pk, size=0.2, align="l")
        K.show(st, l1, b.word(1, "lubricator"), s[2], 0.4)
        K.show(st, l2, b.word(1, "A riser"), s[2], 0.4)
        K.show(st, l3, s[2], s[3], 0.4)
        # sentence 2: the vessel drifts, the package shears the tool and the riser disconnects
        t2 = b.word(2, "loses position")
        drift = st.arrow(vcx + 1.4, SEA_TOP + 0.9, vcx + 2.6, SEA_TOP + 0.9, P.BAD, 0.09, 0.3, 0.9)
        K.show(st, drift, t2 - 0.5, t2 + 2.0, 0.3)
        st.move(vessel_parts + [riser_up, riser_core, ct_line], t2, t2 + 1.6, dx=0.5, interp="LINEAR")
        st.move(pk[2], t2 + 1.2, t2 + 1.7, dx=+0.1)
        st.move(pk[3], t2 + 1.2, t2 + 1.7, dx=-0.1)
        st.fade_out(ct_line, t2 + 1.6, 0.2)
        st.move(vessel_parts + [riser_up, riser_core], t2 + 2.2, t2 + 3.2, dy=+0.5)
        dc = K.tag(st, mp_x + 2.2, y_pk + 1.0, "sheared, disconnected: the tree stays closed", color=P.SAFE, fg=P.BG, size=0.2, z=0.9, align="l")
        K.show(st, dc, t2 + 1.8, None, 0.4)
        # sentence 3: larger, more capable vessel
        fin = K.tag(st, -0.9, 3.5, "riser-based light well intervention", color=P.PANEL2, size=0.26, z=0.9)
        K.show(st, fin, s[3], None, 0.5)


# ====================================================================================================== 7.05
def b705(st, tl):
    b = tl["7.05"]
    s = b.sent
    with st.span(b.start, b.end):
        rows = [("RLWI vessel", "wire only: slickline, electric line", ["carry", "hammer", "log", "perforate"], 1.0, -1.9),
                ("vessel with a riser", "coiled tubing, pumping, circulation", ["wire", "coiled tubing", "pump", "push"], 2.6, 0.3),
                ("drilling rig", "BOP and marine riser: pull the tubing", ["everything above", "rotate", "pull the completion", "kill the well"], 6.0, 2.5)]
        t_rows = [b.start + 0.4, b.start + 1.4, b.word(0, "top of the ladder")]
        for (name, sub, tags, cost, y), t in zip(rows, t_rows):
            card = K.card(st, -1.8, y, 10.2, 1.75, P.PANEL, 0.2)
            nm = st.text(name, -6.7, y + 0.4, 0.3, P.TEXT, 0.5, align="l", kind="bold")
            sb = st.text(sub, -6.7, y - 0.05, 0.2, P.MUTED, 0.5, align="l")
            tg = []
            for j, tx in enumerate(tags):
                tg += K.tag(st, -6.7 + j * 2.3, y - 0.55, tx, color=P.PANEL2, size=0.17, z=0.6, align="l")
            K.show(st, card + [nm, sb] + tg, t, None, 0.5)
            # relative cost bar (ordering only), appears at sentence 2
            bar = st.rect(3.5, y, 0.01, 0.4, P.SAFE if cost < 4 else P.BAD, 0.5, anchor="l", role="flat")
            lab = st.text("cost (ordering only)", 5.0, y + 0.55, 0.16, P.MUTED, 0.5)
            tcost = s[2] + 0.4 * rows.index((name, sub, tags, cost, y))
            K.show(st, [bar, lab], tcost, None, 0.4)
            st.scale_to(bar, tcost, tcost + 0.8, sx=cost * 0.6)
        lad = st.arrow(-7.6, -2.6, -7.6, 3.2, P.MUTED, 0.05, 0.22, 0.4)
        K.show(st, lad, b.start + 0.3, None, 0.5)
        lt = K.note(st, "heavier", -7.6, 3.55, 0.17, P.MUTED, align="c")
        K.show(st, lt, b.start + 0.3, None, 0.5)
        # the NCS note (sentence 1)
        nc = K.tag(st, -1.0, -3.3, "NORWEGIAN SHELF: about 20 years of light intervention vessels, now contracted most days of the year", color=P.NO_BADGE, fg=P.TEXT, size=0.19, z=0.9)
        K.show(st, nc, s[1], None, 0.5)
        fin = K.tag(st, 4.7, -3.0, "that is why they exist", color=P.SAFE, fg=P.BG, size=0.26, z=0.9)
        K.show(st, fin, s[3], None, 0.5)


def build(st, tl):
    F.header(st, tl)
    b701(st, tl)
    b702(st, tl)
    b703(st, tl)
    b704(st, tl)
    b705(st, tl)
