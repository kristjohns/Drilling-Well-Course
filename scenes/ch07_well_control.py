"""Ch 7: Well control and barriers.

One worked kick runs through the whole chapter, every number derived from well_model:
  bit at 4,000 m TVD, drilling with the planned 1.62 sg (9-5/8in section), forecast pore pressure pp(4000) = 1.547 sg;
  'the window lied': actual pore pressure = forecast + 0.12 sg below the 9-5/8in shoe -> 654 bar;
  mud column 1.62 sg x 4,000 m = 636 bar -> SIDPP 18 bar -> kill mud 1.67 sg;
  a 50 m gas influx (illustrative) -> SICP 25 bar; shoe at 3,400 m with leak-off limit fg(3400) = 1.71 sg (571 bar).
The shoe-pressure and choke-pressure curves (7.06, 7.07) come from a single-bubble, constant-bottom-hole-pressure model
(ideal gas, no temperature, no slip): kick tolerance is the biggest influx whose shoe-pressure peak stays under the limit.

No camera moves: the header, well strip and term cards live in world space, so detail is shown by re-staging."""
from __future__ import annotations
import math

import skia

from scenes.common import palette as P, well_model as M, furniture as F
from scenes.common.chart import Chart
from scenes.common.shapes import BopStack, pill
from scenes.common.look import col, hex_rgb, lighten, darken, wrap_to

TITLE = "Well control and barriers"

# ---------------------------------------------------------------- the worked kick (all from well_model)
MW = M.section_mud_weights()["9-5/8in intermediate"]       # 1.62 sg, planned mud for the 8 1/2in section
TVD = 4000.0                                                # bit depth
PP_FC = M.pp(TVD)                                           # forecast pore pressure, 1.547 sg
DPP = 0.12                                                  # 'the window lied' (illustrative)
SHOE = [s.shoe for s in M.programme() if s.name.startswith("9-5/8")][0]    # 3,400 m
DEV0, DEV1 = SHOE, SHOE + 150.0                             # the deviation ramps in below the shoe (above it, 1.49 sg held)


def act_pp(z):
    """'Actual' pore pressure: forecast + 0.12 sg below the 9-5/8in shoe (ramped over 150 m)."""
    f = min(max((z - DEV0) / (DEV1 - DEV0), 0.0), 1.0)
    return M.pp(z) + DPP * f


PP_ACT = act_pp(TVD)                                        # 1.667 sg
P_PORE = M.bar(TVD, PP_ACT)                                 # 654 bar
P_HYD = M.bar(TVD, MW)                                      # 636 bar
SIDPP = P_PORE - P_HYD                                      # 18.3 bar
KMW = MW + SIDPP / (M.G * TVD)                              # 1.67 sg
FG_SHOE = M.fg(SHOE)                                        # 1.71 sg
P_FRAC_SHOE = M.bar(SHOE, FG_SHOE)                          # 571 bar
C_MUD = MW * M.G                                            # bar/m of old mud
C_GAS = M.RHO_GAS * M.G                                     # bar/m of gas at depth
KICK_H = 50.0                                               # m of gas in the annulus at shut-in [SIM]
SICP = SIDPP + KICK_H * (MW - M.RHO_GAS) * M.G              # 25 bar: lighter gas in the annulus -> SICP > SIDPP
A_ANN = math.pi / 4 * (0.2159 ** 2 - 0.127 ** 2)            # 8 1/2in hole x 5in pipe, m2
V_KICK = KICK_H * A_ANN                                     # 1.2 m3 pit gain at the influx
P_ATM = 1.013
X_CROSS = next(z for z in range(int(SHOE), int(M.TD)) if act_pp(z) >= MW)     # ~3,700 m: actual pore pressure passes 1.62


def gas_h(h0, ztop):
    """Height of the gas slug whose top is at ztop (m), constant BHP = P_PORE, ideal gas p*h = const."""
    B = P_PORE - C_MUD * (TVD - ztop)
    return (-B + math.sqrt(B * B + 4 * C_MUD * P_PORE * h0)) / (2 * C_MUD)


def shoe_p(h0, ztop):
    """Pressure at the shoe (bar) while circulating out a gas slug at constant bottom-hole pressure."""
    h = gas_h(h0, ztop)
    zb = ztop + h
    if ztop >= SHOE:
        return P_PORE - C_MUD * (TVD - zb) - C_GAS * h - C_MUD * (ztop - SHOE)
    if zb <= SHOE:
        return P_PORE - C_MUD * (TVD - SHOE)
    return P_PORE - C_MUD * (TVD - zb) - C_GAS * (zb - SHOE)


def choke_p(h0, ztop):
    h = gas_h(h0, max(ztop, 0.0))
    return P_PORE - C_MUD * (TVD - h) - C_GAS * h


def _bisect(fn, lo, hi):
    for _ in range(60):
        m = (lo + hi) / 2
        lo, hi = (lo, m) if fn(m) else (m, hi)
    return lo


KT_H = _bisect(lambda h: shoe_p(h, SHOE) > P_FRAC_SHOE, 1.0, 400.0)             # kick tolerance, m of gas (~84 m)
SI_H = _bisect(lambda h: shoe_p(h, TVD - h) > P_FRAC_SHOE, 1.0, 400.0)          # cracks already at shut-in (~95 m)
BIG_H = round((KT_H + SI_H) / 2)                                                 # 'too big': fine at shut-in, cracks later
KT_V = KT_H * A_ANN


# ---------------------------------------------------------------- small helpers
def W(b, i, needle, frac=0.0):
    """Time `needle` is spoken in sentence i of beat b (fails loudly if the script changed)."""
    txt = b._sentences()[i]
    if needle.lower() not in txt.lower():
        raise KeyError(f"{b.id} sentence {i}: {needle!r} not in {txt!r}")
    return b.word(i, needle, frac)


def _sm(f):
    f = min(max(f, 0.0), 1.0)
    return f * f * (3 - 2 * f)


def _env(t, a, b, d=0.35):
    """Fade envelope for procedurals: 0 before a, 1 inside, 0 after b."""
    return max(0.0, min(1.0, (t - a) / d, (b - t) / d))


def tag(st, x, y, text, fg=P.TEXT, size=0.2, align="l", bg=P.PANEL2, z=0.5):
    return pill(st, x, y, text, bg, fg, size, z, align=align)


def leader(st, x0, y0, x1, y1, color=P.MUTED, z=0.45):
    return [st.line([(x0, y0), (x1, y1)], color, 0.022, z, alpha=0.85), st.circle(x1, y1, 0.05, color, z + 0.01)]


def row(st, x, y, n, color, text, size=0.19, width=3.75):
    """Numbered row: badge + wrapped bold text (left aligned at x + 0.35)."""
    return num_badge(st, x, y, n, color) + [st.text(wrap_to(text, size, width, "bold"), x + 0.35, y, size, P.TEXT, 0.5, align="l", kind="bold")]


def num_badge(st, x, y, n, color=P.PORE, z=0.5):
    return [st.circle(x, y, 0.2, P.PANEL2, z, role="solid"), st.ring(x, y, 0.2, 0.03, color, z + 0.01),
            st.text(str(n), x, y, 0.2, color, z + 0.02, kind="bold")]


def _orb(c, look, x, y, rx, ry, color, alpha):
    rgb = hex_rgb(color)
    c.drawOval(skia.Rect(x - rx * 1.45, y - ry * 1.3, x + rx * 1.45, y + ry * 1.3),
               skia.Paint(Color=col(rgb, 0.38 * alpha), AntiAlias=True, MaskFilter=look._blur(max(5.0, min(rx, 0.4) * look.k * 0.6))))
    g = skia.GradientShader.MakeRadial(skia.Point(x - rx * 0.3, y + ry * 0.35), max(rx, ry) * 1.25,
                                       [col(lighten(rgb, 0.45), alpha), col(rgb, alpha), col(darken(rgb, 0.18), alpha)], [0.0, 0.55, 1.0])
    c.drawOval(skia.Rect(x - rx, y - ry, x + rx, y + ry), skia.Paint(Shader=g, AntiAlias=True))


def _slug(c, look, x0, y0, x1, y1, color, alpha, glow=True):
    """Rounded fluid slug (gas) between x0..x1, y0..y1 (world)."""
    rgb = hex_rgb(color)
    w, h = x1 - x0, y1 - y0
    if w <= 0 or h <= 0 or alpha <= 0:
        return
    r = min(w, h) * 0.45
    rect = skia.Rect(x0, y0, x1, y1)
    if glow:
        c.drawRoundRect(rect, r, r, skia.Paint(Color=col(rgb, 0.4 * alpha), AntiAlias=True, MaskFilter=look._blur(8 * look.w / 1920)))
    g = skia.GradientShader.MakeLinear([skia.Point(x0, 0), skia.Point(x1, 0)],
                                       [col(darken(rgb, 0.15), alpha), col(lighten(rgb, 0.3), alpha), col(darken(rgb, 0.15), alpha)], [0.0, 0.45, 1.0])
    c.drawRoundRect(rect, r, r, skia.Paint(Shader=g, AntiAlias=True))


def _trace(c, look, pts, color, alpha, width=0.06, dash=None, glow=True):
    if len(pts) < 2 or alpha <= 0:
        return
    rgb = hex_rgb(color)
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    if glow:
        c.drawPath(path, skia.Paint(Color=col(rgb, 0.35 * alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width * 2.4,
                                    StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join,
                                    MaskFilter=look._blur(max(3.0, width * look.k * 0.8))))
    p = skia.Paint(Color=col(rgb, alpha), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width,
                   StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(list(dash), 0.0))
        p.setStrokeCap(skia.Paint.kButt_Cap)
    c.drawPath(path, p)
    tip = pts[-1]
    c.drawCircle(tip[0], tip[1], width * 1.2, skia.Paint(Color=col(lighten(rgb, 0.4), alpha), AntiAlias=True))


# ---------------------------------------------------------------- 7.01 the window lied
def beat_lied(st, tl):
    b = tl["7.01"]
    s = b.sent
    with st.span(b.start, b.end):
        # --- the window chart, zoomed on the deep sections
        c = Chart(st, -5.0, -2.75, 6.0, 5.9, (1.3, 1.8), (2800.0, 4200.0), invert_y=True)
        fr = c.frame(xticks=[1.3, 1.4, 1.5, 1.6, 1.7, 1.8], yticks=[2800, 3000, 3200, 3400, 3600, 3800, 4000, 4200],
                     xlabel="equivalent mud weight (sg)", ylabel="depth (m)", fx="{:.1f}", tick_size=0.17)
        zs = list(range(2800, 4201, 25))
        zpp = [z for z in zs if M.pp(z) >= 1.3]
        band = c.band([(max(M.pp(z), 1.3), z) for z in zs], [(M.fg(z), z) for z in zs], P.SAFE, 0.08, 0.16)
        ppf = c.curve([M.pp(z) for z in zpp], zpp, P.PORE, 0.045, 0.3)
        fgc = c.curve([M.fg(z) for z in zs], zs, P.FRAC, 0.055, 0.3)
        shoe_ln = st.dashed(c.pt(1.3, SHOE), c.pt(1.8, SHOE), P.MUTED, 0.018, 0.1, 0.1, 0.12, 0.7)
        shoe_l = c.label(1.305, SHOE - 45, "9⅝ in shoe", 0.15, P.MUTED, "l", "bold")
        st.fade_in(fr + [band, shoe_l] + shoe_ln, b.start + 0.1, 0.5)
        st.draw_on([ppf, fgc], b.start + 0.2, b.start + 1.3, "BEZIER")
        fgl = c.label(1.695, 2870, "fracture", 0.2, P.FRAC, "l", "bold")
        ppl = st.text("forecast", c.X(1.45) - 0.15, c.Y(3480), 0.2, P.PORE, 0.3, align="r", kind="bold")
        st.fade_in([fgl, ppl], b.start + 0.9, 0.4)
        # the planned staircase: 1.49 sg to the 9-5/8in shoe, then 1.62 sg
        mws = M.section_mud_weights()
        mw_up = mws["13-3/8in intermediate"]
        stair = st.line([c.pt(mw_up, 2800), c.pt(mw_up, SHOE), c.pt(MW, SHOE), c.pt(MW, 4200)], P.MUD, 0.07, 0.35)
        st.draw_on(stair, s[0] - 0.1, s[0] + 1.3, "BEZIER")
        mwl = st.text(f"planned\nmud {mw_up:.2f}", c.X(mw_up) - 0.14, c.Y(3020), 0.2, P.MUD, 0.35, align="r", kind="bold")
        mwl2 = st.text(f"{MW:.2f} sg", c.X(MW) - 0.14, c.Y(4120), 0.2, P.MUD, 0.35, align="r", kind="bold")
        st.fade_in([mwl, mwl2], s[0] + 0.6, 0.4)
        # the actual pore pressure: forecast + 0.12 sg below the shoe
        t_hi = W(b, 0, "higher")
        za = list(range(int(SHOE) - 100, 4201, 20))
        act = c.curve([act_pp(z) for z in za], za, P.PORE, 0.085, 0.38)
        st.draw_on(act, t_hi - 0.2, t_hi + 1.4, "BEZIER")
        st.fade(ppf, t_hi, t_hi + 0.6, 1.0, 0.45)
        al = st.text(f"actual\n+{DPP:.2f} sg", c.X(act_pp(4060)) + 0.12, c.Y(4060), 0.2, P.PORE, 0.4, align="l", kind="bold")
        st.fade_in(al, t_hi + 1.0, 0.4)
        # where it crosses the mud weight: underbalanced below ~3,700 m
        xc, yc = c.pt(MW, X_CROSS)
        under = st.poly([c.pt(MW, X_CROSS)] + [c.pt(act_pp(z), z) for z in range(X_CROSS, 4201, 25)] + [c.pt(MW, 4200)], P.BAD, 0.3, alpha=0.35)
        ring = st.ring(xc, yc, 0.16, 0.035, P.BAD, 0.45)
        t_x = t_hi + 1.3
        st.fade_in(under, t_x, 0.5)
        st.pop_in(ring, t_x)
        st.ripple(xc, yc, t_x, t_x + 2.2, P.BAD, period=0.8, r0=0.15, r1=0.9)

        # --- right: the well (not to scale) and the three ways a kick starts
        SX = 2.3
        top, shoe_y, bot = 3.3, -0.9, -3.3
        rock = [st.rect(SX - 0.56, (top + bot) / 2, 0.5, top - bot, P.ROCK, 0.0), st.rect(SX + 0.56, (top + bot) / 2, 0.5, top - bot, P.ROCK, 0.0),
                st.rect(SX, bot - 0.06, 1.62, 0.12, P.ROCK, 0.0)]
        sand = [st.rect(SX - 0.56, -2.8, 0.5, 0.6, P.SAND, 0.01), st.rect(SX + 0.56, -2.8, 0.5, 0.6, P.SAND, 0.01)]
        hole = st.rect(SX, (shoe_y + bot) / 2, 0.62, shoe_y - bot, P.MUD, 0.05)
        csg_bg = st.rect(SX, (top + shoe_y) / 2, 0.66, top - shoe_y, P.BG, 0.04)
        csg = [st.rect(SX - 0.35, (top + shoe_y) / 2, 0.06, top - shoe_y, P.STEEL, 0.2), st.rect(SX + 0.35, (top + shoe_y) / 2, 0.06, top - shoe_y, P.STEEL, 0.2)]
        mud_c = st.rect(SX, shoe_y, 0.64, top - 0.15 - shoe_y, P.MUD, 0.05, anchor="b")
        pipe = st.rect(SX, (top + bot + 0.45) / 2, 0.12, top - (bot + 0.45), P.STEEL, 0.3)
        bit = st.poly([(SX - 0.27, bot + 0.45), (SX + 0.27, bot + 0.45), (SX + 0.2, bot + 0.2), (SX - 0.2, bot + 0.2)], P.STEEL_DK, 0.31)
        well = rock + sand + [hole, csg_bg, mud_c, pipe, bit] + csg
        st.fade_in(well, b.start + 0.4, 0.5)
        # rows
        RX = 3.6
        r1 = row(st, RX, 1.85, 1, P.PORE, "pore pressure higher than forecast: below 3,700 m it beats the mud")
        st.fade_in(r1, t_hi + 0.2, 0.4)
        t_sw = W(b, 1, "pulling")
        r2 = row(st, RX, 0.8, 2, P.GAS, "swab: pulling the pipe sucks fluid in, like a syringe")
        st.fade_in(r2, t_sw - 0.1, 0.4)
        t_ls = W(b, 1, "losses")
        r3 = row(st, RX, -0.95, 3, P.MUD, "losses: mud escapes into a crack and the level falls")
        st.fade_in(r3, t_ls - 0.1, 0.4)
        st.fade(r1, t_sw - 0.1, t_sw + 0.3, 1.0, 0.45)
        st.fade(r2, t_ls - 0.1, t_ls + 0.3, 1.0, 0.45)
        # swab: the pipe and bit are pulled up; fluid is sucked in below the bit
        st.move([pipe, bit], t_sw, t_sw + 1.6, dy=0.55)
        upa = st.arrow(SX + 0.62, bot + 0.9, SX + 0.62, bot + 1.6, P.TEXT, 0.05, 0.16, 0.5)
        st.fade_in(upa, t_sw, 0.3)
        st.fade_out(upa, t_sw + 1.9, 0.4)
        for y0, sd in ((-2.65, -1), (-2.95, 1)):
            st.flow([(SX + sd * 0.8, y0), (SX + sd * 0.2, y0 + 0.05), (SX + sd * 0.05, y0 + 0.4)], t_sw + 0.4, b.end, P.GAS, n=5, speed=0.45, r=0.04, z=0.4)
        # the syringe (an analogy, under row 2)
        sy_x, sy_y = 4.4, 0.0
        barrel = st.rect(sy_x + 0.9, sy_y, 1.8, 0.42, P.PANEL2, 0.4, role="solid")
        rim = st.line([(sy_x, sy_y + 0.21), (sy_x + 1.8, sy_y + 0.21), (sy_x + 1.8, sy_y - 0.21), (sy_x, sy_y - 0.21), (sy_x, sy_y + 0.21)],
                      P.STEEL_DK, 0.03, 0.43)
        nozzle = st.rect(sy_x - 0.15, sy_y, 0.3, 0.1, P.STEEL_DK, 0.42)
        fill = st.rect(sy_x + 0.02, sy_y, 0.25, 0.36, P.GAS, 0.41, anchor="l")
        piston = st.rect(sy_x + 0.32, sy_y, 0.1, 0.38, P.STEEL_DK, 0.44)
        rod = st.rect(sy_x + 0.37, sy_y, 1.9, 0.07, P.STEEL, 0.44, anchor="l")
        handle = st.rect(sy_x + 2.27, sy_y, 0.08, 0.5, P.STEEL, 0.44)
        syr = [barrel, rim, nozzle, fill, piston, rod, handle]
        st.fade_in(syr, t_sw + 0.1, 0.4)
        st.move([piston, rod, handle], t_sw + 0.5, t_sw + 2.2, dx=0.95)
        st.scale_to(fill, t_sw + 0.5, t_sw + 2.2, sx=1.25)
        st.flow([(sy_x - 0.7, sy_y), (sy_x + 0.1, sy_y)], t_sw + 0.5, t_sw + 2.4, P.GAS, n=5, speed=0.8, r=0.035, z=0.45)
        st.fade_out(syr, t_ls - 0.2, 0.5)
        # losses: a crack below the shoe takes mud; the level falls
        fy = shoe_y - 0.35
        crack = st.line([(SX + 0.31, fy), (SX + 0.45, fy - 0.05), (SX + 0.6, fy + 0.04), (SX + 0.8, fy - 0.03)], P.FRAC, 0.04, 0.35)
        st.draw_on(crack, t_ls, t_ls + 0.6)
        st.flow([(SX, fy + 0.5), (SX + 0.25, fy), (SX + 0.8, fy - 0.02)], t_ls + 0.3, s[2] + 0.5, P.MUD, n=6, speed=0.6, r=0.035, z=0.36)
        st.scale_to(mud_c, t_ls + 0.3, t_ls + 2.2, sy=(top - 0.15 - shoe_y) - 1.2)
        lvl = st.arrow(SX - 0.19, top - 0.2, SX - 0.19, top - 1.2, P.MUD, 0.05, 0.16, 0.5)
        st.fade_in(lvl, t_ls + 0.8, 0.3)
        st.fade_out(lvl, s[2], 0.4)
        # formation fluid enters the well; unchecked it reaches surface
        t_in = s[2]
        for xo in (-0.2, 0.2):
            st.flow([(SX + xo, bot + 0.6), (SX + xo, shoe_y), (SX + xo * 1.1, top - 1.4)], t_in, b.end, P.GAS, n=10, speed=0.9, r=0.04, z=0.37)
        st.ripple(SX, -2.8, t_in, t_in + 1.6, P.GAS, period=0.8, r0=0.2, r1=0.9)
        inf = tag(st, RX - 0.25, -3.1, "formation fluid enters the well", P.GAS, 0.19)
        st.fade_in(inf, t_in + 0.1, 0.4)
        st.fade(r3, t_in, t_in + 0.4, 1.0, 0.45)
        t_k = W(b, 3, "kick")
        t_bo = W(b, 3, "blowout")
        k1 = tag(st, RX - 0.25, -1.95, "KICK", "#ffffff", 0.24, bg=P.BAD)
        kx = RX - 0.25 + st.measure("KICK", 0.24, "bold") + 0.6
        ka = st.arrow(kx, -1.95, kx + 0.55, -1.95, P.BAD, 0.05, 0.18, 0.5)
        k2 = tag(st, kx + 0.75, -1.95, "BLOWOUT", "#ffffff", 0.24, bg=P.BAD)
        k3 = st.text("a flow nobody can stop", kx + 0.75, -2.45, 0.17, P.MUTED, 0.5, align="l", kind="bold")
        st.fade_in(k1, t_k - 0.1, 0.3)
        st.fade_in(ka + k2, t_bo - 0.15, 0.3)
        st.fade_in(k3, W(b, 3, "nobody") - 0.1, 0.4)
        for xo in (-0.15, 0.15):
            st.flow([(SX + xo, shoe_y), (SX + xo, top), (SX + xo * 4, top + 0.45)], t_bo, b.end, P.GAS, n=8, speed=1.6, r=0.045, z=0.5)


# ---------------------------------------------------------------- 7.02 THE KICK PROPAGATING UP THE ANNULUS
CX2, HR2 = -4.3, 0.62
Y_SURF, Y_SB, Y_BOT = 3.3, 2.1, -3.25


def ycol(z):
    """Column y for a depth (riser 0-300 m drawn at ~3x the scale of the well below the seabed)."""
    if z <= M.WATER_DEPTH:
        return Y_SURF - z / M.WATER_DEPTH * (Y_SURF - Y_SB)
    return Y_SB - (z - M.WATER_DEPTH) / (TVD - M.WATER_DEPTH) * (Y_SB - Y_BOT)


def p_open(z):
    """Absolute pressure at depth z in the open well (mud above it)."""
    return P_ATM + M.bar(z, MW)


RATIO = p_open(TVD) / P_ATM                       # ~629: how much bigger at the surface (Boyle, ideal gas)
R0 = 0.56 / RATIO ** (1 / 3)


def beat_kick(st, tl):
    b = tl["7.02"]
    s = b.sent
    with st.span(b.start, b.end):
        x0c, x1c = CX2 - 1.25, CX2 + 1.25
        sea = st.rect(CX2, (Y_SURF + Y_SB) / 2, 2.5, Y_SURF - Y_SB, P.SEA, 0.0)
        rock = [st.rect(x0c + 0.315, (Y_SB + Y_BOT - 0.15) / 2, 0.63, Y_SB - Y_BOT + 0.15, P.ROCK, 0.0),
                st.rect(x1c - 0.315, (Y_SB + Y_BOT - 0.15) / 2, 0.63, Y_SB - Y_BOT + 0.15, P.ROCK, 0.0),
                st.rect(CX2, Y_BOT - 0.075, 2 * HR2, 0.15, P.ROCK, 0.0)]
        mud = st.rect(CX2, (Y_SURF + Y_BOT) / 2, 2 * HR2, Y_SURF - Y_BOT, P.MUD, 0.05)
        riser = [st.rect(CX2 - HR2 - 0.04, (Y_SURF + Y_SB) / 2, 0.08, Y_SURF - Y_SB, P.STEEL, 0.2),
                 st.rect(CX2 + HR2 + 0.04, (Y_SURF + Y_SB) / 2, 0.08, Y_SURF - Y_SB, P.STEEL, 0.2)]
        bop = [st.rect(CX2 - HR2 - 0.22, Y_SB + 0.2, 0.44, 0.4, P.STEEL_DK, 0.25), st.rect(CX2 + HR2 + 0.22, Y_SB + 0.2, 0.44, 0.4, P.STEEL_DK, 0.25)]
        pipe = st.rect(CX2, (Y_SURF + 0.15 + Y_BOT + 0.3) / 2, 0.2, Y_SURF + 0.15 - (Y_BOT + 0.3), P.STEEL, 0.3)
        bit = st.poly([(CX2 - 0.3, Y_BOT + 0.3), (CX2 + 0.3, Y_BOT + 0.3), (CX2 + 0.22, Y_BOT + 0.08), (CX2 - 0.22, Y_BOT + 0.08)], P.STEEL_DK, 0.31)
        bopl = st.text("BOP", x0c - 0.1, Y_SB + 0.2, 0.17, P.TEXT, 0.3, align="r", kind="bold")
        rl = st.text("riser", x0c - 0.1, (Y_SURF + Y_SB) / 2 + 0.25, 0.17, P.MUTED, 0.3, align="r", kind="bold")
        ticks = []
        for z, lab in ((0, "0 m"), (300, "300 m"), (1000, "1,000"), (2000, "2,000"), (3000, "3,000"), (4000, "4,000 m")):
            ticks.append(st.text(lab, x1c + 0.1, ycol(z), 0.15, P.MUTED, 0.3, align="l"))
            ticks.append(st.rect(x1c + 0.03, ycol(z), 0.06, 0.02, P.MUTED, 0.3))
        col_objs = [sea, mud, bit, pipe, bopl, rl] + rock + riser + bop + ticks
        st.fade_in(col_objs, b.start + 0.1, 0.5)

        # timing
        t_bub = W(b, 1, "bubble")
        t_p = W(b, 1, "six hundred")
        t_q = s[2]
        t_ans = s[3]
        t_step = W(b, 4, "small gain")
        t_r0 = W(b, 4, "gas rises") - 0.2
        t_r1 = W(b, 4, "near the top", 1.0)
        t_obm = s[5]
        t_bo = W(b, 5, "breaks out")
        Z_BO = 200.0                                                   # break-out depth: in the riser, above the BOP

        def z_rise(t):
            f = min(max((t - t_r0) / (t_r1 - t_r0), 0.0), 1.0)
            return TVD - (TVD - M.WATER_DEPTH) * f / 0.78 if f < 0.78 else M.WATER_DEPTH * (1 - (f - 0.78) / 0.22)

        def bubble_geom(z):
            r = R0 * (p_open(TVD) / p_open(z)) ** (1 / 3)
            rx = min(r, HR2 - 0.05)
            ry = r ** 3 / rx ** 2
            xc = CX2 + (HR2 * 0.58) * max(0.0, 1.0 - max(r - 0.17, 0.0) / 0.18)
            yc = max(ycol(z), Y_BOT + 0.1 + ry)
            yc = min(yc, Y_SURF - ry - 0.02)
            return xc, yc, rx, ry

        def draw_bubble(cv, t, look):
            if t < t_bub - 0.2:
                return
            a = min(1.0, (t - t_bub + 0.2) / 0.4)
            z = z_rise(t)
            if t > t_r1:
                a *= max(0.0, 1.0 - (t - t_r1) / 0.6)
            if a <= 0:
                return
            xc, yc, rx, ry = bubble_geom(z)
            _orb(cv, look, xc, yc, rx, ry, P.GAS, a)
        st.procedural(t_bub - 0.2, t_r1 + 0.7, 0.28, draw_bubble)
        bl = tag(st, CX2 + 2.1, Y_BOT + 0.85, "gas bubble", P.GAS, 0.18)
        bll = leader(st, CX2 + 2.05, Y_BOT + 0.85, CX2 + 0.45, Y_BOT + 0.25, P.GAS)
        st.fade_in(bl + bll, t_bub, 0.4)
        st.fade_out(bl + bll, t_r0, 0.4)
        st.ripple(CX2 + 0.36, Y_BOT + 0.2, t_bub, t_bub + 1.8, P.GAS, period=0.6, r0=0.08, r1=0.5)

        # HUD: depth / pressure / volume, all from the same z(t)
        t_up0 = t_step - 1.0
        t_sm0 = t_step - 0.6
        hud_x = [0.0, 2.55, 5.1]

        def draw_hud(cv, t, look):
            a = _env(t, t_bub, t_obm - 0.1, 0.4)
            if a <= 0:
                return
            z = z_rise(t)
            p = p_open(z)
            # big rows mid-screen during the puzzle, then a small top row while the chart runs (cross-fade, no slide)
            ab = 1.0 - min(1.0, max(0.0, (t - t_up0) / 0.4))
            asm = min(1.0, max(0.0, (t - t_sm0) / 0.4))
            vol = f"×{p_open(TVD) / p:,.0f}" if t > t_r0 else ("× 1" if t < t_q + 0.6 else "× ?")
            items = [("GAS AT", f"{z:,.0f} m", P.TEXT, t_bub), ("PRESSURE", f"{p:,.0f} bar", P.TEXT, t_p), ("VOLUME", vol, P.GAS, t_q)]
            for i, (lab, val, colr, ti) in enumerate(items):
                ai = a * min(1.0, max(0.0, (t - ti + 0.2) / 0.4))
                if ai <= 0:
                    continue
                if ab > 0:
                    yb = 2.75 - 0.95 * i
                    look.draw_text(cv, lab, 0.7, yb, 0.18, P.MUTED, ai * ab, "l", "bold")
                    look.draw_text(cv, val, 3.0, yb, 0.46, colr, ai * ab, "l", "mono")
                if asm > 0:
                    look.draw_text(cv, lab, hud_x[i], 3.55, 0.13, P.MUTED, ai * asm, "l", "bold")
                    look.draw_text(cv, val, hud_x[i], 3.12, 0.32, colr, ai * asm, "l", "mono")
        st.procedural(t_bub - 0.1, t_obm + 0.4, 0.6, draw_hud)

        # the puzzle (during the pause) and its answer
        q = st.text("How much bigger\nat the surface?", 3.6, -1.35, 0.46, P.TEXT, 0.5, kind="bold")
        st.fade_in(q, t_q + 0.2, 0.5)
        st.fade_out(q, t_ans - 0.25, 0.3)
        ans = st.text(f"≈ {round(RATIO, -1):,.0f} × bigger", 3.6, -1.2, 0.8, P.GAS, 0.5, kind="bold")
        ans2 = st.text("ideal gas: pressure × volume stays the same", 3.6, -2.25, 0.2, P.MUTED, 0.5, kind="bold")
        st.pop_in(ans, t_ans - 0.05, 0.4)
        st.fade_in(ans2, t_ans + 0.4, 0.4)
        st.fade_out([ans, ans2], t_step - 1.0, 0.35)

        # pit gain vs depth of the gas (linear depth; m3)
        ymax = 20.0
        c = Chart(st, 0.9, -2.65, 5.9, 4.55, (TVD, 0.0), (0.0, ymax))
        fr = c.frame(xticks=[4000, 3000, 2000, 1000, 0], yticks=[0, 5, 10, 15, 20], xlabel="depth of the gas (m)", ylabel="pit gain (m³)",
                     fx="{:,.0f}", tick_size=0.17)
        rz = st.rect((c.X(M.WATER_DEPTH) + c.X(0)) / 2, c.y + c.h / 2, c.X(0) - c.X(M.WATER_DEPTH), c.h, P.SEA, 0.07, alpha=0.45, role="flat")
        rzl = st.text("riser", (c.X(M.WATER_DEPTH) + c.X(0)) / 2, c.y + 0.2, 0.14, P.TEXT, 0.3, kind="bold")
        st.fade_in(fr + [rz, rzl], t_step - 0.6, 0.5)
        V0 = V_KICK

        def wbm_pts(t):
            if t < t_step:
                return []
            fs = min(1.0, (t - t_step) / 0.5)
            pts = [c.pt(TVD, 0.0), c.pt(TVD, V0 * fs)]
            if t < t_r0:
                return pts
            znow = z_rise(t)
            z = TVD
            while z > znow:
                z = max(z - 25.0, znow)
                v = V0 * p_open(TVD) / p_open(z)
                if v >= ymax:
                    # find where it leaves the chart and stop there
                    pts.append(c.pt(z, ymax))
                    break
                pts.append(c.pt(z, v))
            return pts

        def draw_wbm(cv, t, look):
            a = _env(t, t_step, b.end, 0.3)
            pts = wbm_pts(t)
            if t > t_obm + 0.3:
                a *= 0.55
            _trace(cv, look, pts, P.GAS, a, 0.065)
        st.procedural(t_step, b.end, 0.4, draw_wbm)
        st.ripple(c.X(TVD), c.Y(V0), t_step, t_step + 1.4, P.GAS, period=0.7, r0=0.08, r1=0.6)
        g1 = tag(st, c.X(3650), c.Y(4.2), f"influx ≈ {V0:.1f} m³: a small gain", P.GAS, 0.18)
        st.fade_in(g1, t_step + 0.3, 0.4)
        st.fade_out(g1, W(b, 4, "slowly"), 0.4)
        t_v = W(b, 4, "violently")
        z_off = _bisect(lambda z: V0 * p_open(TVD) / p_open(z) < ymax, 0.0, TVD)
        up = st.arrow(c.X(z_off), c.Y(ymax) - 0.05, c.X(z_off), c.Y(ymax) + 0.35, P.GAS, 0.05, 0.16, 0.45)
        g2 = st.text(f"→ ≈ {round(V0 * RATIO, -1):,.0f} m³ at the surface", c.X(z_off) - 0.15, c.Y(ymax) + 0.55, 0.18, P.GAS, 0.45, align="r",
                     kind="bold")
        g3 = tag(st, c.X(1900), c.Y(9.5), "most of the growth: the last few hundred metres", P.TEXT, 0.17, align="c")
        st.fade_in(up, t_r1 - 0.2, 0.3)
        st.fade_in(g2, t_r1 - 0.1, 0.4)
        st.fade_in(g3, t_v, 0.4)
        st.fade_out(g3, t_obm, 0.4)

        # oil-based mud: the gas dissolves, hides, then breaks out in the riser
        t_d0 = t_obm + 0.3
        t_d1 = t_bo
        Vd = 0.4 * V0                                   # dissolved: a smaller, flat gain [SIM]
        V_bo = V0 * p_open(TVD) / p_open(Z_BO)

        def z_obm(t):
            f = _sm((t - t_d0) / (t_d1 - t_d0)) if t < t_d1 else 1.0
            z = TVD - (TVD - Z_BO) * f
            if t > t_d1:
                z = Z_BO * max(0.0, 1.0 - (t - t_d1) / 1.6)
            return z

        import random
        rnd = random.Random(11)
        cloud = [(rnd.uniform(-HR2 + 0.06, HR2 - 0.06), rnd.uniform(-0.3, 0.3)) for _ in range(34)]
        cloud = [p for p in cloud if abs(p[0]) > 0.14]

        def draw_obm(cv, t, look):
            if t < t_d0 - 0.3:
                return
            a = _env(t, t_d0 - 0.3, b.end, 0.4)
            z = z_obm(t)
            if t < t_d1:
                y = ycol(z)
                look.draw_particles(cv, [(CX2 + dx, y + dy) for dx, dy in cloud], P.GAS, 0.03, 0.4 * a, glow=False)
            else:
                f = min(1.0, (t - t_d1) / 1.6)
                v = V_bo * p_open(Z_BO) / p_open(z)
                r = R0 * (v / V0) ** (1 / 3)
                rx = min(r, HR2 - 0.05)
                ry = min(r ** 3 / rx ** 2, (Y_SURF - Y_SB - 0.5) / 2)
                yc = min(ycol(z), Y_SURF - ry - 0.02)
                look.draw_particles(cv, [(CX2 + dx, ycol(Z_BO) + dy) for dx, dy in cloud], P.GAS, 0.03, 0.4 * a * (1 - f), glow=False)
                _orb(cv, look, CX2, yc, rx * min(1.0, 0.3 + 2 * f), ry * min(1.0, 0.3 + 2 * f), P.GAS, a)
            # pit gain (dashed)
            pts = [c.pt(TVD, 0.0), c.pt(TVD, Vd)]
            zz = TVD
            while zz > max(z, Z_BO):
                zz = max(zz - 50.0, max(z, Z_BO))
                pts.append(c.pt(zz, Vd))
            if t >= t_d1:
                pts.append(c.pt(Z_BO, min(ymax, V_bo)))
            _trace(cv, look, pts, P.GAS, a, 0.055, dash=(0.14, 0.09))
        st.procedural(t_d0 - 0.3, b.end, 0.29, draw_obm)
        obm = tag(st, CX2, Y_BOT - 0.38, "oil-based mud", P.MUD, 0.17, align="c")
        st.fade_in(obm, t_obm, 0.4)
        hid = tag(st, CX2 + 1.4, ycol(2600), "dissolved: hidden", P.GAS, 0.17)
        st.fade_in(hid, W(b, 5, "dissolves"), 0.4)
        st.fade_out(hid, t_bo - 0.2, 0.3)
        g4 = tag(st, c.X(2900), c.Y(6.0), "oil-based mud: almost flat…", P.GAS, 0.17, align="c")
        st.fade_in(g4, W(b, 5, "hides"), 0.4)
        bo_l = tag(st, CX2 + 2.1, Y_SB + 0.75, "breaks out in the riser,\nabove the BOP", P.GAS, 0.17)
        st.fade_in(bo_l, W(b, 5, "riser") - 0.2, 0.4)
        st.ripple(CX2, ycol(Z_BO), t_bo, t_bo + 1.6, P.GAS, period=0.6, r0=0.3, r1=1.2)


# ---------------------------------------------------------------- 7.03 detection dashboard
def _card(st, x0, y0, x1, y1, title, t_in, z=0.0):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    card = st.rect(cx, cy, x1 - x0, y1 - y0, P.PANEL, z)
    tt = st.text(title, x0 + 0.25, y1 - 0.32, 0.19, P.TEXT, z + 0.3, align="l", kind="bold")
    dot = st.circle(x1 - 0.3, y1 - 0.32, 0.09, P.MUTED, z + 0.3)
    st.fade_in([card, tt, dot], t_in, 0.45)
    return [card, tt, dot], dot


def _alarm(st, dot, t):
    st.recolor(dot, t, t + 0.3, P.BAD)
    x, y = dot.location[0], dot.location[1]
    st.ripple(x, y, t, t + 1.5, P.BAD, period=0.6, r0=0.1, r1=0.45)


def beat_detect(st, tl):
    b = tl["7.03"]
    s = b.sent
    with st.span(b.start, b.end):
        t0 = b.start + 0.3
        A = (-6.15, 0.95, -1.65, 3.65)
        B = (-1.35, 0.95, 3.1, 3.65)
        C = (-6.15, -2.05, -1.65, 0.65)
        D = (-1.35, -2.05, 3.1, 0.65)
        E = (3.4, -2.55, 7.75, 0.5)
        ca, da = _card(st, *A, "FLOW OUT vs FLOW IN", t0)
        cb, db = _card(st, *B, "PIT LEVEL", t0 + 0.1)
        cc, dc = _card(st, *C, "TRIP TANK (on a trip)", t0 + 0.2)
        cd, dd = _card(st, *D, "DRILLING RATE", t0 + 0.3)
        # 1 flow in vs out: two meters with mud flowing
        t1 = s[1]
        x0, x1 = A[0] + 1.3, A[2] - 0.35
        L = (x1 - x0) * 0.72
        yi, yo = 2.55, 1.6
        li = st.text("in", A[0] + 0.3, yi, 0.18, P.MUTED, 0.3, align="l", kind="bold")
        lo = st.text("out", A[0] + 0.3, yo, 0.18, P.MUTED, 0.3, align="l", kind="bold")
        bi = st.rect(x0, yi, L, 0.32, P.MUD, 0.2, anchor="l", alpha=0.85)
        bo = st.rect(x0, yo, L, 0.32, P.MUD, 0.2, anchor="l", alpha=0.85)
        extra = st.rect(x0 + L, yo, 0.0001, 0.32, P.BAD, 0.21, anchor="l")
        st.fade_in([li, lo, bi, bo, extra], t1 - 0.2, 0.4)
        st.flow([(x0, yi), (x0 + L, yi)], t1, b.end, P.MUD, n=7, speed=0.6, r=0.04, z=0.3, glow=False)
        st.flow([(x0, yo), (x0 + L * 1.28, yo)], t1, b.end, P.MUD, n=8, speed=0.75, r=0.04, z=0.3, glow=False)
        t1b = W(b, 1, "greater")
        st.scale_to(extra, t1b, t1b + 1.0, sx=L * 0.28)
        ex = st.text("more comes out than goes in", (x0 + x1) / 2, 1.13, 0.17, P.BAD, 0.4, kind="bold")
        st.fade_in(ex, t1b + 0.6, 0.4)
        _alarm(st, da, t1b + 0.8)
        # 2 pit level: tank + trace
        t2 = s[2]
        tx, ty = B[0] + 0.85, 1.85
        tank = st.rect(tx, ty, 0.9, 1.3, P.PANEL2, 0.2, role="solid")
        lvl = st.rect(tx, ty - 0.62, 0.84, 0.55, P.MUD, 0.22, anchor="b")
        st.fade_in([tank, lvl], t2 - 0.2, 0.4)
        st.scale_to(lvl, W(b, 2, "rising"), W(b, 2, "rising") + 2.5, sy=1.0)
        cB = Chart(st, B[0] + 1.75, 1.3, 2.75, 1.65, (0, 10), (0, 10))
        frB = cB.frame(grid=False, panel=False, xlabel="", ylabel="")
        capB = [st.text("time →", cB.x + cB.w, cB.y - 0.2, 0.15, P.MUTED, 0.3, align="r"),
                st.text("pit volume", cB.x + 0.05, cB.y + cB.h + 0.08, 0.15, P.MUTED, 0.3, align="l")]
        trB = cB.curve([0, 4, 5, 6.5, 8, 10], [2.5, 2.5, 2.7, 4.2, 6.5, 8.8], P.MUD, 0.06, 0.3)
        st.fade_in(frB + capB, t2, 0.4)
        st.draw_on(trB, t2 + 0.3, t2 + 2.6)
        _alarm(st, db, t2 + 2.0)
        # 3 trip tank: steel pulled out vs mud taken to fill the hole
        t3 = s[3]
        bx0 = C[0] + 0.9
        base = C[1] + 0.62
        steel = st.rect(bx0 + 0.3, base, 0.75, 0.0001, P.STEEL, 0.2, anchor="b")
        mudt = st.rect(bx0 + 1.6, base, 0.75, 0.0001, P.MUD, 0.2, anchor="b")
        ls = st.text("steel\npulled out", bx0 + 0.3, base - 0.3, 0.15, P.MUTED, 0.3, kind="bold")
        lm = st.text("mud\ntaken", bx0 + 1.6, base - 0.3, 0.15, P.MUTED, 0.3, kind="bold")
        st.fade_in([steel, mudt, ls, lm], t3, 0.3)
        st.scale_to(steel, W(b, 3, "takes"), W(b, 3, "takes") + 1.0, sy=1.45)
        st.scale_to(mudt, W(b, 3, "less mud"), W(b, 3, "less mud") + 1.0, sy=0.95)
        gap = st.rect(bx0 + 1.6, base + 0.95 + 0.25, 0.75, 0.5, P.BAD, 0.21, alpha=0.35, role="flat")
        gapl = st.text("missing:\nsomething\nflowed in", bx0 + 2.3, base + 1.2, 0.16, P.BAD, 0.4, align="l", kind="bold")
        st.fade_in([gap, gapl], W(b, 3, "steel we pulled"), 0.4)
        _alarm(st, dc, W(b, 3, "steel we pulled") + 0.3)
        # 4 drilling break: rate of penetration jumps and stays high
        t4 = s[4]
        cD = Chart(st, D[0] + 0.75, -1.6, 3.4, 1.4, (0, 10), (0, 10))
        frD = cD.frame(grid=False, panel=False)
        capD = [st.text("time →", cD.x + cD.w, cD.y - 0.2, 0.15, P.MUTED, 0.3, align="r")]
        trD = cD.curve([0, 2, 4, 4.8, 5.1, 6.5, 8, 10], [2.4, 2.6, 2.3, 2.5, 7.6, 7.9, 7.4, 7.8], P.TEXT, 0.06, 0.3)
        st.fade_in(frD + capD, t4, 0.4)
        st.draw_on(trD, t4 + 0.2, W(b, 4, "drilling break", 1.0))
        wb = tag(st, cD.X(10.0), cD.y + cD.h + 0.12, "drilling break: a warning", P.WARN, 0.16, align="r")
        st.fade_in(wb, W(b, 4, "warning") - 0.2, 0.3)
        _alarm(st, dd, W(b, 4, "warning"))
        # 5 the response: a flow check
        t_stop = W(b, 4, "stop the pumps")
        ce, de = _card(st, *E, "FLOW CHECK", t_stop - 0.3)
        arr = st.arrow(D[2] - 0.15, -0.7, E[0] + 0.25, -0.7, P.WARN, 0.06, 0.2, 0.5)
        st.fade_in(arr, t_stop - 0.3, 0.3)
        wx = E[0] + 0.9
        wy0, wy1 = -2.35, -0.55
        hole = st.rect(wx, (wy0 + wy1) / 2, 0.72, wy1 - wy0, P.BG, 0.1)
        ann = [st.rect(wx - 0.24, (wy0 + wy1) / 2, 0.2, wy1 - wy0, P.MUD, 0.12), st.rect(wx + 0.24, (wy0 + wy1) / 2, 0.2, wy1 - wy0, P.MUD, 0.12)]
        dp = st.rect(wx, (wy0 + 0.1 + wy1 + 0.45) / 2, 0.2, wy1 + 0.45 - wy0 - 0.1, P.STEEL, 0.2)
        fl = st.rect(wx + 1.3, wy1 - 0.1, 2.0, 0.14, P.STEEL_DK, 0.15)
        fll = st.text("returns", wx + 2.4, wy1 - 0.1, 0.14, P.MUTED, 0.3, align="l", kind="bold")
        st.fade_in([hole, dp, fl, fll] + ann, t_stop - 0.1, 0.4)
        st.flow([(wx, wy1 + 0.45), (wx, wy0 + 0.15)], t_stop - 0.1, t_stop + 0.9, P.MUD, n=5, speed=0.9, r=0.035, z=0.3, glow=False)
        po = tag(st, wx + 0.5, -0.27, "pumps OFF", P.MUTED, 0.16)
        st.fade_in(po, t_stop + 0.4, 0.3)
        t_watch = W(b, 4, "watch the well")
        st.flow([(wx + 0.24, wy0 + 0.2), (wx + 0.24, wy1 - 0.1), (wx + 2.3, wy1 - 0.1)], t_stop - 0.1, b.end, P.MUD, n=8, speed=0.5, r=0.035,
                z=0.3, glow=False)
        sf = tag(st, wx + 0.7, -1.55, "still flowing:\nshut the well in", P.BAD, 0.17)
        st.fade_in(sf, s[5] + 0.2, 0.4)
        st.ripple(wx + 1.8, wy1 - 0.1, t_watch + 0.4, t_watch + 3.0, P.BAD, period=0.8, r0=0.1, r1=0.55)
        _alarm(st, de, s[5] + 0.3)
        # the aim
        aim = tag(st, -1.4, -3.1, "catch it while it is still small", P.SAFE, 0.26, align="c")
        st.fade_in(aim, s[6] + 0.1, 0.5)


# ---------------------------------------------------------------- the barrier schematic (7.04, reused in 7.08)
class Schematic:
    """Drilling well barrier schematic, not to scale: subsea BOP on the wellhead, 13-3/8in and 9-5/8in casing cemented,
    8 1/2in open hole below the 9-5/8in shoe, drill string with bit. Radii obey the hole/casing nesting."""

    def __init__(self, st, cx=-3.6, cased_to_td=False):
        self.st, self.cx = st, cx
        self.y_bop0, self.y_bop1 = 2.35, 3.3
        self.y_wh0, self.y_wh1 = 2.0, 2.35
        self.y_sb = 2.12
        self.y_s13, self.y_s9 = 0.95, -0.95
        self.y_toc13, self.y_toc9 = 1.65, 0.35
        self.y_td = -3.3
        self.r_oh, self.r9i, self.r9o, self.r12, self.r13i, self.r13o, self.r17 = 0.40, 0.43, 0.50, 0.72, 0.78, 0.85, 1.07
        self.cased = cased_to_td
        if cased_to_td:          # Macondo-style: production casing to TD, shoe track at the bottom
            self.y_s9 = self.y_td + 0.15

    def draw(self, sand_y=None):
        st, cx = self.st, self.cx
        o = {}
        R = 2.05
        o["sea"] = st.rect(cx, (self.y_sb + 3.85) / 2, 2 * R, 3.85 - self.y_sb, P.SEA, 0.0)
        o["rock"] = st.rect(cx, (self.y_sb + self.y_td - 0.2) / 2, 2 * R, self.y_sb - (self.y_td - 0.2), P.ROCK, 0.0)
        if sand_y:
            o["sand"] = st.rect(cx, (sand_y[0] + sand_y[1]) / 2, 2 * R, sand_y[0] - sand_y[1], P.SAND, 0.01)
        objs = [o["sea"], o["rock"]] + ([o["sand"]] if sand_y else [])
        # 17 1/2in hole: cement then mud above, 13-3/8 casing
        y_top = self.y_wh0
        objs.append(st.rect(cx, (y_top + self.y_s13) / 2, 2 * self.r17, y_top - self.y_s13, P.MUD, 0.02, alpha=0.3))
        objs.append(st.rect(cx, (self.y_toc13 + self.y_s13) / 2, 2 * self.r17, self.y_toc13 - self.y_s13, P.CEMENT, 0.03))
        # 12 1/4in hole below the 13-3/8 shoe
        objs.append(st.rect(cx, (self.y_s13 + self.y_s9) / 2, 2 * self.r12, self.y_s13 - self.y_s9, P.MUD, 0.02, alpha=0.3))
        objs.append(st.rect(cx, (self.y_toc9 + self.y_s9) / 2, 2 * self.r12, self.y_toc9 - self.y_s9, P.CEMENT, 0.03))
        # inside the 13-3/8: the 9-5/8 x 13-3/8 annulus (mud)
        objs.append(st.rect(cx, (y_top + self.y_s13) / 2, 2 * self.r13i, y_top - self.y_s13, P.BG, 0.034))
        objs.append(st.rect(cx, (y_top + self.y_s13) / 2, 2 * self.r13i, y_top - self.y_s13, P.MUD, 0.035, alpha=0.3))
        if self.y_toc9 > self.y_s13:
            objs.append(st.rect(cx, (self.y_toc9 + self.y_s13) / 2, 2 * self.r13i, self.y_toc9 - self.y_s13, P.CEMENT, 0.036))
        # casing walls
        o["csg13"] = [st.rect(cx + sd * (self.r13i + self.r13o) / 2, (y_top + self.y_s13) / 2, self.r13o - self.r13i, y_top - self.y_s13, P.STEEL_DK, 0.2)
                      for sd in (-1, 1)]
        o["csg9"] = [st.rect(cx + sd * (self.r9i + self.r9o) / 2, (y_top + self.y_s9) / 2, self.r9o - self.r9i, y_top - self.y_s9, P.STEEL, 0.21)
                     for sd in (-1, 1)]
        objs += o["csg13"] + o["csg9"]
        o["cem9"] = [st.rect(cx + sd * (self.r9o + self.r12) / 2, (self.y_toc9 + self.y_s9) / 2, self.r12 - self.r9o, self.y_toc9 - self.y_s9,
                             P.CEMENT, 0.04) for sd in (-1, 1)]
        objs += o["cem9"]
        # wellbore fluid: inside the 9-5/8 and the open hole
        o["mud_in"] = st.rect(cx, (y_top + self.y_s9) / 2, 2 * self.r9i, y_top - self.y_s9, P.MUD, 0.05)
        objs.append(o["mud_in"])
        if not self.cased:
            o["mud_oh"] = st.rect(cx, (self.y_s9 + self.y_td) / 2, 2 * self.r_oh, self.y_s9 - self.y_td, P.MUD, 0.05)
            objs.append(o["mud_oh"])
        # shoe marks
        for y, r in ((self.y_s13, self.r13o), (self.y_s9, self.r9o)):
            for sd in (-1, 1):
                objs.append(st.poly([(cx + sd * r, y), (cx + sd * (r + 0.12), y), (cx + sd * r, y + 0.14)], P.STEEL, 0.22))
        # wellhead + BOP + riser stub
        o["wh"] = st.rect(cx, (self.y_wh0 + self.y_wh1) / 2, 1.3, self.y_wh1 - self.y_wh0, P.STEEL_DK, 0.25)
        o["bop"] = st.rect(cx, (self.y_bop0 + self.y_bop1) / 2, 1.9, self.y_bop1 - self.y_bop0, P.PANEL2, 0.25, role="solid")
        o["bop_bore"] = st.rect(cx, (self.y_bop0 + self.y_bop1) / 2, 2 * self.r9i, self.y_bop1 - self.y_bop0, P.MUD, 0.26)
        o["bop_l"] = st.text("BOP", cx - 0.68, (self.y_bop0 + self.y_bop1) / 2, 0.16, P.TEXT, 0.27, kind="bold")
        o["riser"] = [st.rect(cx + sd * 0.5, (self.y_bop1 + 3.85) / 2, 0.07, 3.85 - self.y_bop1, P.STEEL, 0.25) for sd in (-1, 1)]
        o["riser_mud"] = st.rect(cx, (self.y_bop1 + 3.85) / 2, 0.93, 3.85 - self.y_bop1, P.MUD, 0.24)
        objs += [o["wh"], o["bop"], o["bop_bore"], o["bop_l"], o["riser_mud"]] + o["riser"]
        # drill string
        if not self.cased:
            yb = self.y_td + 0.22
            o["pipe"] = st.rect(cx, (3.85 + yb + 0.55) / 2, 0.16, 3.85 - (yb + 0.55), P.STEEL, 0.3)
            o["bha"] = st.rect(cx, yb + 0.35, 0.34, 0.5, P.STEEL_DK, 0.3)
            o["bit"] = st.poly([(cx - 0.33, yb + 0.12), (cx + 0.33, yb + 0.12), (cx + 0.25, yb - 0.08), (cx - 0.25, yb - 0.08)], P.STEEL_DK, 0.31)
            objs += [o["pipe"], o["bha"], o["bit"]]
        self.o = o
        self.objs = objs
        return objs

    def primary_outline(self, inset=0.36):
        """Blue outline around the wellbore fluid column (sides+top, bottom edge separate so it can break)."""
        st, cx = self.st, self.cx
        y0 = self.y_td + 0.06
        y1 = self.y_wh1 + 0.15
        main = st.line([(cx - inset, y0), (cx - inset, y1), (cx + inset, y1), (cx + inset, y0)], P.PRIMARY_B, 0.06, 0.6)
        bottom = st.line([(cx - inset, y0), (cx + inset, y0)], P.PRIMARY_B, 0.06, 0.6)
        return main, bottom

    def secondary_outline(self, band_h=0.5):
        """Red outline: formation just below the shoe, casing cement, casing, wellhead, BOP (closes over the BOP top)."""
        st, cx = self.st, self.cx
        ys = self.y_s9
        yb = ys - band_h
        xr_c = self.r12 + 0.07
        xr_k = self.r9o + 0.05
        pts_r = [(self.r_oh + 0.02, yb), (xr_c, yb), (xr_c, self.y_toc9), (xr_k, self.y_toc9), (xr_k, self.y_wh0 - 0.05),
                 (0.72, self.y_wh0 - 0.05), (0.72, self.y_bop0 - 0.02), (1.02, self.y_bop0 - 0.02), (1.02, self.y_bop1 + 0.06)]
        pts = [(cx - x, y) for x, y in pts_r] + [(cx + x, y) for x, y in reversed(pts_r)]
        line = st.line(pts, P.SECOND_B, 0.06, 0.62)
        bands = []
        for sd in (-1, 1):
            xa, xb = cx + sd * (self.r_oh + 0.02), cx + sd * xr_c
            bands.append(st.rect((xa + xb) / 2, (ys + yb) / 2, abs(xb - xa), ys - yb, P.SECOND_B, 0.58, alpha=0.5, role="flat"))
        return line, bands


def beat_barriers(st, tl):
    b = tl["7.04"]
    s = b.sent
    with st.span(b.start, b.end):
        sch = Schematic(st, cx=-3.6)
        sand = (sch.y_td + 0.75, sch.y_td - 0.2)
        objs = sch.draw(sand_y=sand)
        st.fade_in(objs, b.start + 0.1, 0.6)
        cx = sch.cx
        nts = st.text("schematic, not to scale", cx, -3.62, 0.14, P.MUTED, 0.3)
        st.fade_in(nts, b.start + 0.5, 0.4)
        # s1: the Norwegian rule (right side, before the term cards arrive)
        t1 = s[1]
        rule_head = st.text("WHEREVER A FORMATION COULD FLOW TO SURFACE", 2.75, 2.85, 0.2, P.MUTED, 0.5, kind="bold")
        rule = st.text("two independent well barriers", 2.75, 2.15, 0.42, P.TEXT, 0.5, kind="bold")
        st.fade_in(rule_head, W(b, 1, "wherever") - 0.1, 0.4)
        st.fade_in(rule, W(b, 1, "two independent") - 0.1, 0.4)
        ic = [st.ring(1.3, 1.1, 0.32, 0.06, P.PRIMARY_B, 0.5), st.ring(2.75, 1.1, 0.32, 0.06, P.SECOND_B, 0.5)]
        icl = [st.text("1", 1.3, 1.1, 0.24, P.PRIMARY_B, 0.51, kind="bold"), st.text("2", 2.75, 1.1, 0.24, P.SECOND_B, 0.51, kind="bold")]
        st.pop_in(ic + icl, W(b, 1, "two independent") + 0.4, 0.4)
        src = st.arrow(cx, sch.y_td - 0.1, cx, sch.y_td + 0.6, P.GAS, 0.07, 0.22, 0.55)
        st.fade_in(src, W(b, 1, "formation could flow"), 0.4)
        st.fade_out(src, s[2], 0.4)
        rule_all = [rule_head, rule] + ic + icl
        st.fade_out(rule_all, s[2] - 0.2, 0.4)
        # s2: envelope = a set of elements that together stop flow
        env = st.text("a well barrier envelope:\nelements that together stop flow", -1.0, 3.3, 0.2, P.MUTED, 0.5, align="l", kind="bold")
        st.fade_in(env, W(b, 2, "set of elements") - 0.2, 0.4)
        st.fade_out(env, s[3] - 0.2, 0.4)
        # s3: primary = the mud column (blue)
        pm, pb = sch.primary_outline()
        t3 = W(b, 3, "primary")
        st.draw_on([pm, pb], t3, t3 + 1.4, "BEZIER")
        pl = tag(st, -1.0, -2.25, "PRIMARY: the mud column", P.PRIMARY_B, 0.2)
        pll = leader(st, -1.05, -2.25, cx + 0.2, -2.05, P.PRIMARY_B)
        st.fade_in(pl + pll, W(b, 3, "mud column") - 0.2, 0.4)
        # s4: secondary (red), element by element as spoken
        sl, bands = sch.secondary_outline()
        t4 = W(b, 4, "secondary")
        st.draw_on(sl, t4, W(b, 4, "preventer", 1.0), "LINEAR")
        sh = st.text("SECONDARY", -1.0, 3.3, 0.2, P.SECOND_B, 0.5, align="l", kind="bold")
        st.fade_in(sh, t4, 0.4)
        items = [("rock", "rock just below the shoe\n(proven by a leak-off test)", sch.y_s9 - 0.42, (cx + 0.6, sch.y_s9 - 0.25)),
                 ("casing cement", "casing cement", 0.0, (cx + 0.62, 0.0)),
                 ("the casing", "casing", 1.2, (cx + 0.47, 1.2)),
                 ("wellhead", "wellhead", 2.17, (cx + 0.66, 2.17)),
                 ("preventer", "BOP", 2.85, (cx + 0.96, 2.85))]
        for needle, txt, y, (ex, ey) in items:
            t = W(b, 4, needle) - 0.15
            p_ = tag(st, -1.0, y, txt, P.TEXT, 0.18)
            ld = leader(st, -1.05, y, ex, ey, P.SECOND_B)
            st.fade_in(p_ + ld, t, 0.35)
            st.ripple(ex, ey, t, t + 0.9, P.SECOND_B, period=0.9, r0=0.05, r1=0.45)
            if needle == "rock":
                st.fade_in(bands, t, 0.4)
        # s5: the airlock: two doors that must never fail together (right, after the term cards)
        t5 = s[5]
        ax, ay = 5.55, 0.95
        corr = st.rect(ax, ay, 4.2, 1.5, P.PANEL, 0.0)
        floor = st.rect(ax, ay - 0.62, 4.0, 0.03, P.GRID, 0.1)
        d1 = st.rect(ax - 0.9, ay, 0.22, 1.25, P.PRIMARY_B, 0.3, role="solid")
        d2 = st.rect(ax + 0.9, ay, 0.22, 1.25, P.SECOND_B, 0.3, role="solid")
        lk = st.line([(ax - 0.9, ay + 0.85), (ax - 0.9, ay + 1.0), (ax + 0.9, ay + 1.0), (ax + 0.9, ay + 0.85)], P.MUTED, 0.03, 0.3)
        lkl = st.text("interlock", ax, ay + 1.18, 0.15, P.MUTED, 0.3, kind="bold")
        lab = st.text("two airlock doors", ax, ay - 1.05, 0.22, P.TEXT, 0.4, kind="bold")
        st.fade_in([corr, floor, d1, d2, lk, lkl, lab], t5 + 0.2, 0.5)
        ta = W(b, 5, "airlock")
        st.move(d1, ta, ta + 0.6, dy=1.0)
        st.move(d1, ta + 1.4, ta + 2.0, dy=-1.0)
        st.move(d2, ta + 2.2, ta + 2.8, dy=1.0)
        nv = tag(st, ax, ay - 1.55, "never both open: independent", P.WARN, 0.18, align="c")
        st.fade_in(nv, W(b, 5, "never fail") - 0.1, 0.4)
        st.move(d2, s[6] - 0.3, s[6] + 0.3, dy=-1.0)
        # s6: tested; if one fails, only restoration work
        t6 = s[6]
        tk = tag(st, 3.5, -1.35, "✓ both tested", P.SAFE, 0.18)
        st.fade_in(tk, W(b, 6, "tested") - 0.1, 0.4)
        ban = tag(st, 3.5, -2.05, "one fails → only restoration work", P.WARN, 0.18)
        st.fade_in(ban, W(b, 6, "only work") - 0.2, 0.4)
        # s7: a kick = the mud barrier has failed
        t7 = s[7]
        tf = W(b, 7, "failed")
        st.recolor(pb, t7 + 0.3, t7 + 0.7, P.BAD)
        st.fade_out(pb, tf - 0.2, 0.5)
        st.fade(pm, tf, tf + 0.6, 1.0, 0.35)
        for xo in (-0.18, 0.18):
            st.flow([(cx + xo, sch.y_td - 0.1), (cx + xo, sch.y_td + 0.3), (cx + xo * 1.2, sch.y_s9 + 0.6)], t7 + 0.2, b.end, P.GAS, n=8, speed=0.8,
                    r=0.045, z=0.65)
        st.ripple(cx, sch.y_td + 0.35, t7 + 0.2, b.end, P.GAS, period=0.9, r0=0.15, r1=0.6)
        lost = tag(st, 3.5, -2.75, "primary lost: secondary holds", P.BAD, 0.18)
        st.fade_in(lost, tf - 0.1, 0.4)
        st.fade(pl, tf, tf + 0.4, 1.0, 0.4)


# ---------------------------------------------------------------- 7.05 shut-in, then the U-tube
def beat_shutin(st, tl):
    b = tl["7.05"]
    s = b.sent
    with st.span(b.start, b.end):
        t_lift = W(b, 0, "lift the bit")
        t_pumps = W(b, 0, "stop the pumps")
        t_check = W(b, 0, "check for flow")
        t_close = W(b, 0, "close the well")
        t_out = s[1] + 0.3
        steps = [(t_lift, "pick up off bottom:\nno tool joint in the BOP"), (t_pumps, "pumps off"), (t_check, "flow check"), (t_close, "close the BOP")]
        rows = []
        for i, (t, txt) in enumerate(steps):
            y = 2.5 - 1.15 * i
            r = num_badge(st, -5.8, y, i + 1, P.PORE) + [st.text(txt, -5.4, y, 0.22, P.TEXT, 0.5, align="l", kind="bold")]
            st.fade_in(r, t - 0.15, 0.35)
            if i + 1 < len(steps):
                st.fade(r, steps[i + 1][0] - 0.1, steps[i + 1][0] + 0.3, 1.0, 0.5)
            rows += r
        # the BOP stack, a tool joint spaced out of it, the annular closing on pipe body
        bop = BopStack(st, 1.2, -3.05, s=0.92, pipe_top=3.7, label=True)
        st.fade_in(bop.all, b.start + 0.2, 0.5)
        tj = st.rect(bop.cx, bop.y_ann, 0.5 * bop.s, 0.4 * bop.s, P.STEEL_DK, bop.z + 0.06)
        tjl = tag(st, bop.cx - 0.45, bop.y_ann + 0.05, "tool joint", P.WARN, 0.16, align="r")
        st.fade_in([tj] + tjl, b.start + 0.4, 0.4)
        st.ripple(bop.cx, bop.y_ann, b.start + 0.6, t_lift + 0.4, P.WARN, period=0.9, r0=0.2, r1=0.7)
        dy = bop.y_top + 0.55 - bop.y_ann
        st.move([tj] + tjl, t_lift + 0.2, t_lift + 1.8, dy=dy)
        up = st.arrow(bop.cx - 1.75, bop.y_top - 0.3, bop.cx - 1.75, bop.y_top + 0.5, P.TEXT, 0.05, 0.16, 0.5)
        st.fade_in(up, t_lift, 0.3)
        st.fade_out(up, t_lift + 2.2, 0.4)
        # pumping, then pumps off; returns keep coming -> flow; close -> shut in
        st.flow([(bop.cx, 3.7), (bop.cx, bop.cy - 0.2)], b.start + 0.3, t_pumps + 0.5, P.MUD, n=9, speed=0.9, r=0.04, z=0.6, glow=False)
        po = tag(st, bop.cx + 0.35, 3.35, "pumps off", P.MUTED, 0.16)
        st.fade_in(po, t_pumps + 0.3, 0.3)
        for sd in (-1, 1):
            xa = bop.cx + sd * 0.27 * bop.s
            st.flow([(xa, bop.cy + 0.2), (xa, 3.7)], b.start + 0.3, t_close + 0.6, P.MUD, n=9, speed=0.6, r=0.035, z=0.6, glow=False)
            st.flow([(xa, bop.cy + 0.2), (xa, bop.y_ann - 0.3)], t_close + 0.4, t_out, P.MUD, n=4, speed=0.0001, r=0.035, z=0.6, glow=False)
        fl = tag(st, bop.cx + 0.35, bop.y_top + 1.0, "still flowing", P.BAD, 0.16)
        st.fade_in(fl, t_check + 0.3, 0.3)
        st.fade_out(fl, t_close + 0.3, 0.3)
        bop.close_annular(t_close, t_close + 0.9)
        si = tag(st, bop.cx + 0.35, bop.y_top + 1.0, "shut in", P.SAFE, 0.18)
        st.fade_in(si, t_close + 0.7, 0.3)
        st.ripple(bop.cx, bop.y_ann, t_close + 0.6, t_close + 2.0, P.SAFE, period=0.7, r0=0.3, r1=1.0)
        stage1 = rows + bop.all + [tj] + tjl + po + si
        st.fade_out(stage1, t_out, 0.5)

        # ---- the U-tube: drill pipe (known mud) | annulus (gas of unknown size)
        t_u = t_out + 0.4
        xp, xa = -4.65, -1.25
        wp, wa = 0.75, 1.15
        ytop, ybot = 1.6, -2.6
        yb0 = ybot - 0.55
        walls = [st.rect(xp - wp / 2 - 0.04, (ytop + yb0) / 2, 0.07, ytop - yb0, P.STEEL, 0.2), st.rect(xp + wp / 2 + 0.04, (ytop + ybot) / 2, 0.07, ytop - ybot, P.STEEL, 0.2),
                 st.rect(xa - wa / 2 - 0.04, (ytop + ybot) / 2, 0.07, ytop - ybot, P.STEEL, 0.2), st.rect(xa + wa / 2 + 0.04, (ytop + yb0) / 2, 0.07, ytop - yb0, P.STEEL, 0.2),
                 st.rect((xp + xa) / 2, yb0 - 0.035, xa + wa / 2 + 0.08 - (xp - wp / 2 - 0.08), 0.07, P.STEEL, 0.2)]
        mp = st.rect(xp, (ytop + ybot) / 2, wp, ytop - ybot, P.MUD, 0.1)
        ma = st.rect(xa, (ytop + ybot) / 2, wa, ytop - ybot, P.MUD, 0.1)
        mb = st.rect((xp + xa) / 2, (ybot + yb0) / 2, xa + wa / 2 - (xp - wp / 2), ybot - yb0 + 0.01, P.MUD, 0.1)
        h_g = 0.95
        gas = st.rect(xa, ybot + 0.12 + h_g / 2, wa - 0.12, h_g, P.GAS, 0.15)
        lp = st.text("drill pipe", xp, ytop + 0.3, 0.2, P.TEXT, 0.3, kind="bold")
        la = st.text("annulus", xa, ytop + 0.3, 0.2, P.TEXT, 0.3, kind="bold")
        ut = walls + [mp, ma, mb, gas, lp, la]
        st.fade_in(ut, t_u, 0.5)
        # gauges: rise and settle (SICP > SIDPP: gas in the annulus is lighter)
        t_g = W(b, 1, "gauges")
        tau = 1.3
        gauges = [(xp, SIDPP, "SIDPP"), (xa, SICP, "SICP")]
        for gx, val, name in gauges:
            dial = st.circle(gx, 2.75, 0.42, P.PANEL2, 0.3, role="solid")
            rim = st.ring(gx, 2.75, 0.42, 0.04, P.STEEL_DK, 0.31)
            stem = st.rect(gx, 2.1, 0.08, 0.5, P.STEEL_DK, 0.15)
            st.fade_in([dial, rim, stem], t_u + 0.2, 0.4)

            def draw_g(cv, t, look, gx=gx, val=val, name=name):
                a = _env(t, t_u + 0.3, b.end, 0.4)
                if a <= 0:
                    return
                k = 1.0 - math.exp(-max(0.0, t - t_g) / tau)
                v = val * k
                ang = math.radians(210 - 240 * v / 40.0)
                x1, y1 = gx + 0.32 * math.cos(ang), 2.75 + 0.32 * math.sin(ang)
                pnt = skia.Paint(Color=col(hex_rgb(P.WARN), a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.045,
                                 StrokeCap=skia.Paint.kRound_Cap)
                cv.drawLine(gx, 2.75, x1, y1, pnt)
                cv.drawCircle(gx, 2.75, 0.05, skia.Paint(Color=col(hex_rgb(P.WARN), a), AntiAlias=True))
                look.draw_text(cv, f"{name} {v:.0f} bar", gx, 3.45, 0.2, P.TEXT, a, "c", "mono")
            st.procedural(t_u, b.end, 0.4, draw_g)
        st.ripple(xp, 2.75, t_g, t_g + 1.6, P.WARN, period=0.8, r0=0.45, r1=1.0)
        st.ripple(xa, 2.75, t_g, t_g + 1.6, P.WARN, period=0.8, r0=0.45, r1=1.0)
        # s2: unknown gas vs known mud
        t_unk = W(b, 2, "unknown")
        q = tag(st, (xp + xa) / 2 - 0.15, ybot + 0.6, "gas: unknown size", P.GAS, 0.17, align="c")
        ql = st.line([((xp + xa) / 2 + 0.95, ybot + 0.6), (xa - 0.1, ybot + 0.6)], P.GAS, 0.022, 0.45)
        q = q + [ql]
        st.fade_in(q, t_unk - 0.2, 0.4)
        st.ripple(xa, ybot + 0.6, t_unk, t_unk + 1.4, P.GAS, period=0.7, r0=0.3, r1=0.9)
        t_kn = W(b, 2, "clean mud")
        kn = tag(st, xp, 0.2, f"clean mud\n{MW:.2f} sg ✓", P.MUD, 0.17, align="c")
        st.fade_in(kn, t_kn - 0.1, 0.4)
        # s3: U-tube -> bottom-hole pressure = mud column + SIDPP
        t_ut = W(b, 3, "U-tube")
        u = st.line([(xp, ytop - 0.1), (xp, ybot - 0.28), (xa, ybot - 0.28), (xa, ytop - 0.1)], P.TEXT, 0.035, 0.35, alpha=0.8)
        st.draw_on(u, t_ut - 0.3, t_ut + 1.2, "BEZIER")
        utl = st.text("a U-tube", (xp + xa) / 2, -0.4, 0.28, P.TEXT, 0.4, kind="bold")
        st.fade_in(utl, t_ut + 0.4, 0.4)
        st.fade_out([u, utl], W(b, 3, "pressure at the bottom") - 0.2, 0.4)
        t_bhp = W(b, 3, "pressure at the bottom")
        bh = st.ring((xp + xa) / 2, ybot - 0.28, 0.2, 0.04, P.TEXT, 0.4)
        bhl = tag(st, (xp + xa) / 2, ybot - 0.85, "bottom-hole pressure", P.TEXT, 0.17, align="c")
        st.fade_in([bh] + bhl, t_bhp - 0.1, 0.4)
        # the equation card, built as spoken
        ex0, ex1 = 0.55, 7.6
        card = st.rect((ex0 + ex1) / 2, -0.85, ex1 - ex0, 4.4, P.PANEL, 0.0)
        hd = st.text("BOTTOM-HOLE PRESSURE, SHUT IN", ex0 + 0.35, 1.0, 0.18, P.MUTED, 0.3, align="l", kind="bold")
        st.fade_in([card, hd], t_unk - 0.4, 0.4)
        anote = st.text("the annulus gauge (SICP) includes gas of unknown size:\nit cannot give the pore pressure", ex0 + 0.35, -2.7, 0.15, P.MUTED,
                        0.3, align="l", kind="bold")
        st.fade_in(anote, t_unk, 0.4)
        t_col = t_kn
        r1a = st.text("mud column in the pipe", ex0 + 0.35, 0.35, 0.22, P.TEXT, 0.3, align="l", kind="bold")
        r1b = st.text(f"{MW:.2f} sg × 0.0981 × {TVD:,.0f} m", ex0 + 0.35, -0.08, 0.17, P.MUTED, 0.3, align="l", kind="mono")
        st.fade_in([r1a, r1b], t_col - 0.1, 0.4)
        st.counter(ex1 - 0.35, 0.35, t_col, t_col + 1.2, 0, P_HYD, fmt="{:.0f} bar", size=0.3, color=P.MUD, align="r")
        t_sid = W(b, 3, "plus the shut-in")
        r2a = st.text("+ shut-in drill pipe pressure", ex0 + 0.35, -0.75, 0.22, P.TEXT, 0.3, align="l", kind="bold")
        st.fade_in(r2a, t_sid, 0.4)
        st.counter(ex1 - 0.35, -0.75, t_sid + 0.2, t_sid + 1.2, 0, SIDPP, fmt="{:.0f} bar", size=0.3, color=P.WARN, align="r")
        rule = st.rect((ex0 + ex1) / 2, -1.25, ex1 - ex0 - 0.6, 0.025, P.MUTED, 0.3)
        st.fade_in(rule, t_sid + 0.8, 0.3)
        t_pp = W(b, 4, "pore pressure")
        r3a = st.text("= pore pressure", ex0 + 0.35, -1.75, 0.26, P.PORE, 0.3, align="l", kind="bold")
        r3b = st.text(f"{PP_ACT:.2f} sg, not the {PP_FC:.2f} forecast", ex0 + 0.35, -2.2, 0.17, P.MUTED, 0.3, align="l", kind="bold")
        st.fade_in(r3a, W(b, 4, "One reading") - 0.1, 0.4)
        st.counter(ex1 - 0.35, -1.75, W(b, 4, "One reading"), W(b, 4, "One reading") + 1.0, 0, P_PORE, fmt="{:.0f} bar", size=0.36,
                   color=P.PORE, align="r")
        st.fade_in(r3b, t_pp, 0.4)
        st.ripple(ex1 - 0.9, -1.75, t_pp, t_pp + 1.6, P.PORE, period=0.8, r0=0.3, r1=1.0)


# ---------------------------------------------------------------- 7.06 kill: kill mud, driller's method (two circulations)
def beat_kill(st, tl):
    b = tl["7.06"]
    s = b.sent
    with st.span(b.start, b.end):
        # s0: kill mud balances the pore pressure on its own
        t_bal = W(b, 0, "balance")
        bx0 = -5.9
        Lmax = 7.6
        k = Lmax / P_PORE
        kb = st.rect(bx0, -0.3, 0.0001, 0.5, P.KILL_MUD, 0.2, anchor="l")
        pb = st.rect(bx0, -1.15, 0.0001, 0.5, P.PORE, 0.2, anchor="l", alpha=0.85)
        kbl = st.text(f"kill mud column: {KMW:.2f} sg × 0.0981 × {TVD:,.0f} m", bx0, 0.2, 0.18, P.KILL_MUD, 0.3, align="l", kind="bold")
        pbl = st.text("pore pressure", bx0, -1.65, 0.18, P.PORE, 0.3, align="l", kind="bold")
        t_km = W(b, 0, "kill mud")
        st.fade_in([kb, kbl], t_km - 0.2, 0.3)
        st.scale_to(kb, t_km, t_km + 1.5, sx=P_PORE * k)
        st.fade_in([pb, pbl], t_bal - 0.4, 0.3)
        st.scale_to(pb, t_bal - 0.3, t_bal + 0.9, sx=P_PORE * k)
        st.counter(bx0 + P_PORE * k + 0.15, -0.3, t_km, t_km + 1.5, 0, M.bar(TVD, KMW), fmt="{:.0f} bar", size=0.24, color=P.KILL_MUD, align="l",
                   hold=s[2] - 0.2)
        st.counter(bx0 + P_PORE * k + 0.15, -1.15, t_bal - 0.3, t_bal + 0.9, 0, P_PORE, fmt="{:.0f} bar", size=0.24, color=P.PORE, align="l",
                   hold=s[2] - 0.2)
        eq_ok = tag(st, bx0, -2.4, "balanced on its own: no help from the choke needed", P.SAFE, 0.18)
        st.fade_in(eq_ok, W(b, 0, "on its own") - 0.2, 0.4)
        # s1: the formula, term by term
        t_f = s[1]
        f1 = st.text("kill mud  =  old weight  +  SIDPP / (g · TVD)", bx0, 2.9, 0.26, P.TEXT, 0.4, align="l", kind="mono")
        st.fade_in(f1, t_f, 0.4)
        parts = [(W(b, 1, "old weight"), "=  " + f"{MW:.2f}", P.MUD),
                 (W(b, 1, "shut-in drill pipe pressure"), f"  +  {SIDPP:.1f}", P.WARN),
                 (W(b, 1, "true vertical depth") - 0.6, f" / (0.0981 × {TVD:,.0f})", P.TEXT)]
        x = bx0
        nums = []
        for t, txt, colr in parts:
            o = st.text(txt, x, 2.15, 0.26, colr, 0.4, align="l", kind="mono")
            st.fade_in(o, t, 0.35)
            nums.append(o)
            x += st.measure(txt, 0.26, "mono")
        res = tag(st, bx0, 1.25, f"kill mud ≈ {KMW:.2f} sg", P.KILL_MUD, 0.3)
        st.pop_in(res, W(b, 1, "true vertical depth", 1.0) - 0.1, 0.4)
        stage0 = [kb, pb, kbl, pbl, f1] + eq_ok + nums
        st.fade_out(stage0, s[2] - 0.35, 0.35)
        # ---- s2: the well, subsea; driller's method in two circulations
        t2 = s[2]
        WX = -3.9
        ydeck, ysea0, ysb = 3.35, 3.1, 1.35
        yshoe, ytd = -1.5, -3.3
        rh, rp = 0.42, 0.1
        sea = st.rect(WX + 0.4, (ysea0 + ysb) / 2, 4.6, ysea0 - ysb, P.SEA, 0.0)
        rock = st.rect(WX + 0.4, (ysb + ytd - 0.2) / 2, 4.6, ysb - ytd + 0.2, P.ROCK, 0.0)
        deck = st.rect(WX + 0.9, ydeck, 5.0, 0.12, P.STEEL_DK, 0.3, role="solid")
        hole_bg = st.rect(WX, (ysb + ytd) / 2, 2 * rh, ysb - ytd, P.BG, 0.02)
        cem = [st.rect(WX + sd * (rh + 0.17), (yshoe + (-0.5)) / 2, 0.24, -0.5 - yshoe, P.CEMENT, 0.03) for sd in (-1, 1)]
        csg = [st.rect(WX + sd * (rh + 0.03), (ysb + yshoe) / 2, 0.06, ysb - yshoe, P.STEEL, 0.2) for sd in (-1, 1)]
        bop = [st.rect(WX - 0.42, ysb + 0.35, 0.34, 0.7, P.STEEL_DK, 0.25), st.rect(WX + 0.42, ysb + 0.35, 0.34, 0.7, P.STEEL_DK, 0.25)]
        bopl = st.text("BOP", WX - 0.85, ysb + 0.35, 0.16, P.TEXT, 0.3, align="r", kind="bold")
        ann_el = [st.rect(WX - rp - 0.1, ysb + 0.5, 0.2, 0.22, "#2f2f35", 0.27), st.rect(WX + rp + 0.1, ysb + 0.5, 0.2, 0.22, "#2f2f35", 0.27)]
        riser = [st.rect(WX + sd * 0.3, (ysb + 0.7 + ydeck) / 2, 0.06, ydeck - ysb - 0.7, P.STEEL, 0.2) for sd in (-1, 1)]
        y_cl = ysb + 0.22
        xcl = WX + 1.7
        chk_line = st.line([(WX + 0.6, y_cl), (xcl, y_cl), (xcl, ydeck + 0.25)], P.STEEL, 0.07, 0.22)
        choke = st.poly([(xcl - 0.2, ydeck + 0.25), (xcl + 0.2, ydeck + 0.25), (xcl, ydeck + 0.45)], P.WARN, 0.3)
        choke2 = st.poly([(xcl - 0.2, ydeck + 0.65), (xcl + 0.2, ydeck + 0.65), (xcl, ydeck + 0.45)], P.WARN, 0.3)
        chl = st.text("choke", xcl - 0.28, ydeck + 0.45, 0.16, P.WARN, 0.3, align="r", kind="bold")
        sep = st.text("to the mud-gas separator", xcl + 1.4, ydeck + 0.45, 0.14, P.MUTED, 0.3, align="l", kind="bold")
        pump = st.rect(WX - 1.4, ydeck + 0.35, 0.6, 0.4, P.PANEL2, 0.3, role="solid")
        pumpl = st.text("pump", WX - 1.4, ydeck + 0.35, 0.14, P.TEXT, 0.31, kind="bold")
        sp = st.line([(WX - 1.1, ydeck + 0.35), (WX, ydeck + 0.35), (WX, ydeck)], P.STEEL, 0.06, 0.22)
        # fluids
        y_bit = ytd + 0.3
        mud_ann = [st.rect(WX + sd * (rp + (rh - rp) / 2), (ydeck + ytd) / 2, rh - rp, ydeck - ytd, P.MUD, 0.05) for sd in (-1, 1)]
        mud_ann_r = [st.rect(WX, (ysb + 0.7 + ydeck) / 2, 0.54, ydeck - ysb - 0.7, P.MUD, 0.04)]
        mud_bot = st.rect(WX, (y_bit + ytd) / 2, 2 * rh, y_bit - ytd, P.MUD, 0.05)
        pipe = st.rect(WX, (ydeck + y_bit) / 2, 2 * rp, ydeck - y_bit, P.STEEL, 0.3)
        bit = st.poly([(WX - 0.3, y_bit + 0.1), (WX + 0.3, y_bit + 0.1), (WX + 0.22, y_bit - 0.1), (WX - 0.22, y_bit - 0.1)], P.STEEL_DK, 0.31)
        shoe_l = st.text("9⅝ in shoe", WX - rh - 0.45, yshoe, 0.15, P.MUTED, 0.3, align="r", kind="bold")
        well = [sea, rock, deck, hole_bg, bopl, chk_line, choke, choke2, chl, sep, pump, pumpl, sp, mud_bot, pipe, bit, shoe_l] + cem + csg + bop + \
            ann_el + riser + mud_ann + mud_ann_r
        st.fade_in(well, t2 - 0.1, 0.5)
        ann_closed = [WX - rp - 0.04, WX + rp + 0.04]
        st.move(ann_el[0], t2 - 0.1, t2, to=(ann_closed[0] - 0.06, ysb + 0.5))
        st.move(ann_el[1], t2 - 0.1, t2, to=(ann_closed[1] + 0.06, ysb + 0.5))
        kl = tag(st, -1.2, 1.4, f"kill mud {KMW:.2f} sg (from the formula)", P.KILL_MUD, 0.17)
        st.fade_in(kl, t2, 0.4)
        st.fade_out(res, t2 - 0.35, 0.3)
        # circulation timing
        t_c1 = W(b, 2, "first") - 0.1
        t_c2 = W(b, 2, "then kill mud") - 0.1
        t_gas_out = t_c2 - 0.6
        t_k1 = t_c2 + 2.4                                       # kill mud at the bit
        t_k2 = min(b.end - 1.0, s[4] + 2.6)                       # kill mud back at the surface
        # pump + annulus flow (old mud in circulation 1, kill mud later)
        down = [(WX - 1.1, ydeck + 0.35), (WX, ydeck + 0.35), (WX, y_bit)]
        up_r = [(WX + rp + 0.16, y_bit), (WX + rp + 0.16, y_cl), (xcl, y_cl), (xcl, ydeck + 0.45), (xcl + 1.3, ydeck + 0.45)]
        up_l = [(WX - rp - 0.16, y_bit), (WX - rp - 0.16, y_cl), (WX + 0.6, y_cl), (xcl, y_cl), (xcl, ydeck + 0.45), (xcl + 1.3, ydeck + 0.45)]
        st.flow(down, t_c1, t_c2, P.MUD, n=12, speed=0.9, r=0.035, z=0.6, glow=False)
        st.flow(down, t_c2, b.end, P.KILL_MUD, n=12, speed=0.9, r=0.035, z=0.6, glow=False)
        t_k2_ = min(b.end - 1.0, s[4] + 2.6)
        for path in (up_r, up_l):
            st.flow(path, t_c1, t_k2_, P.MUD, n=18, speed=0.8, r=0.035, z=0.6, glow=False)
            st.flow(path, t_k2_ - 0.2, b.end, P.KILL_MUD, n=18, speed=0.5, r=0.035, z=0.6, glow=False)
        # the gas: rises with the old mud, expands, leaves through the choke line
        h_px = 0.0016                                            # world units per metre (below the seabed, approx.)

        def zy(z):
            return ysb - (z - M.WATER_DEPTH) / (TVD - M.WATER_DEPTH) * (ysb - y_bit)

        def gas_top(t):
            f = min(max((t - t_c1) / (t_gas_out - 1.2 - t_c1), 0.0), 1.0)
            return (TVD - KICK_H) * (1 - f) + M.WATER_DEPTH * f * 0.98

        def draw_gas(cv, t, look):
            if t < t2 or t > t_gas_out + 0.6:
                return
            a = _env(t, t2, t_gas_out + 0.4, 0.4)
            zt = gas_top(t)
            h = gas_h(KICK_H, zt)
            hv = 0.3 + 0.0035 * h                                # drawn taller than true scale so it can be seen
            y0 = max(zy(min(zt + h, TVD)), y_bit - 0.05)
            y1 = min(y0 + hv, y_cl + 0.1)
            y0 = min(y0, y1 - 0.12)
            for sd in (-1, 1):
                xa = WX + sd * (rp + 0.02)
                xb = WX + sd * (rh - 0.02)
                _slug(cv, look, min(xa, xb), y0, max(xa, xb), y1, P.GAS, a)
        st.procedural(t2, t_gas_out + 0.7, 0.55, draw_gas)
        st.flow([(WX + 0.6, y_cl), (xcl, y_cl), (xcl, ydeck + 0.45), (xcl + 1.3, ydeck + 0.45)], t_gas_out - 1.4, t_gas_out + 0.6, P.GAS, n=10,
                speed=1.4, r=0.05, z=0.62)
        # circulation 2: kill mud down the pipe, then up the annulus
        kfill_p = st.rect(WX, ydeck, 2 * rp - 0.07, 0.0001, P.KILL_MUD, 0.33, anchor="t")
        st.fade_in(kfill_p, t_c2, 0.2)
        st.scale_to(kfill_p, t_c2, t_k1, sy=ydeck - y_bit, interp="LINEAR")
        kf = [st.rect(WX + sd * (rp + (rh - rp) / 2), y_bit, rh - rp, 0.0001, P.KILL_MUD, 0.07, anchor="b") for sd in (-1, 1)]
        kf_b = st.rect(WX, ytd, 2 * rh, 0.0001, P.KILL_MUD, 0.07, anchor="b")
        st.fade_in(kf + [kf_b], t_k1 - 0.3, 0.2)
        st.scale_to(kf_b, t_k1 - 0.3, t_k1, sy=y_bit - ytd + 0.01, interp="LINEAR")
        st.scale_to(kf, t_k1, t_k2, sy=ydeck - y_bit, interp="LINEAR")
        # circulation pills
        c1 = tag(st, -1.2, 0.85, "CIRCULATION 1  ·  old mud carries the gas out", P.MUD, 0.17)
        c2 = tag(st, -1.2, 0.2, "CIRCULATION 2  ·  kill mud replaces the old mud", P.KILL_MUD, 0.17)
        st.fade_in(c1, t_c1, 0.4)
        st.fade(c1, t_c2, t_c2 + 0.4, 1.0, 0.45)
        st.fade_in(c2, t_c2, 0.4)
        # bottom-hole pressure held just above pore pressure; choke pressure from the model
        cx0, cy0, cw, chh = 0.0, -3.15, 6.6, 1.55
        cB = Chart(st, cx0, cy0, cw, chh, (0.0, 1.0), (636.0, 668.0))
        bpan = st.rect(cx0 + cw / 2 - 0.25, cy0 + chh / 2 + 0.2, cw + 1.4, chh + 1.0, P.PANEL, 0.0)
        frB = [bpan] + cB.frame(yticks=[640, 654, 668], xlabel="", ylabel="", tick_size=0.15, grid=False, panel=False)
        bl = st.text("BOTTOM-HOLE PRESSURE (bar) DURING THE KILL", cx0 - 0.8, cy0 + chh + 0.35, 0.15, P.MUTED, 0.3, align="l", kind="bold")
        ppl = cB.hline(P_PORE, P.PORE, 0.035, 0.2)
        ppt = st.text("pore pressure", cx0 + cw - 0.05, cB.Y(P_PORE) - 0.22, 0.15, P.PORE, 0.3, align="r", kind="bold")
        st.fade_in(frB + [bl, ppl, ppt], t_c1 - 0.5, 0.4)
        T0, T1 = t_c1, t_k2

        def draw_bhp(cv, t, look):
            if t < T0:
                return
            a = _env(t, T0, b.end, 0.3)
            f = min(1.0, (t - T0) / (T1 - T0))
            pts = [cB.pt(x / 40 * f, P_PORE + 2.5) for x in range(41)]
            _trace(cv, look, pts, P.MUD, a, 0.05)
        st.procedural(T0, b.end, 0.4, draw_bhp)
        jl = st.text("held just above", cx0 + 0.15, cB.Y(P_PORE + 2.5) + 0.25, 0.15, P.MUD, 0.3, align="l", kind="bold")
        st.fade_in(jl, W(b, 2, "just above") - 0.1, 0.4)

        def choke_now(t):
            if t < t_c1:
                return SICP
            if t < t_gas_out - 1.2:
                return choke_p(KICK_H, gas_top(t))
            if t < t_gas_out + 0.4:
                f = (t - (t_gas_out - 1.2)) / 1.6
                return choke_p(KICK_H, M.WATER_DEPTH * 0.98) * (1 - f) + SIDPP * f
            if t < t_k1:
                return SIDPP
            f = min(1.0, (t - t_k1) / (t_k2 - t_k1))
            return SIDPP * (1 - f)

        def draw_choke(cv, t, look):
            a = _env(t, t2 + 0.2, b.end, 0.4)
            if a <= 0:
                return
            look.draw_text(cv, f"{choke_now(t):3.0f} bar", xcl + 0.3, ydeck + 0.12, 0.17, P.WARN, a, "l", "mono")
        st.procedural(t2, b.end, 0.62, draw_choke)
        st.ripple(xcl, ydeck + 0.45, W(b, 2, "choke holds"), W(b, 2, "choke holds") + 1.8, P.WARN, period=0.7, r0=0.2, r1=0.7)
        # s3: wait-and-weight
        ww = tag(st, -1.2, -0.45, "wait-and-weight: kill mud in ONE circulation", P.TEXT, 0.17)
        st.fade_in(ww, s[3] - 0.1, 0.4)
        # s4: choke-line friction (subsea): flow goes UP the long line; friction adds back-pressure
        t4 = s[4]
        hl = st.line([(WX + 0.6, y_cl), (xcl, y_cl), (xcl, ydeck + 0.25)], P.WARN, 0.05, 0.23)
        st.draw_on(hl, W(b, 4, "choke line") - 0.3, W(b, 4, "choke line") + 0.8)
        chev = []
        for yy in (2.15, 2.75):
            chev.append(st.line([(xcl - 0.18, yy + 0.1), (xcl, yy - 0.06), (xcl + 0.18, yy + 0.1)], P.BAD, 0.04, 0.63))
        st.fade_in(chev, W(b, 4, "friction") - 0.1, 0.4)
        fr_t = tag(st, xcl + 0.35, 2.6, "friction in the long choke line\nadds back-pressure", P.BAD, 0.17)
        st.fade_in(fr_t, W(b, 4, "friction"), 0.4)
        sl = tag(st, xcl + 0.35, 2.0, "pump slowly, open the choke to correct", P.TEXT, 0.17)
        st.fade_in(sl, W(b, 4, "pump slowly") - 0.1, 0.4)


# ---------------------------------------------------------------- 7.07 the shoe: peak pressure and kick tolerance
def beat_tolerance(st, tl):
    b = tl["7.07"]
    s = b.sent
    with st.span(b.start, b.end):
        Z0, Z1 = 2950.0, TVD
        YT, YB = 3.35, -3.2
        WX = -4.35
        rh, rp, r9o, r12 = 0.42, 0.12, 0.5, 0.74

        def zy(z):
            return YT - (z - Z0) / (Z1 - Z0) * (YT - YB)
        ys = zy(SHOE)
        rock = st.rect(WX, (YT + YB - 0.15) / 2, 3.2, YT - YB + 0.15, P.ROCK, 0.0)
        cem = [st.rect(WX + sd * (r9o + r12) / 2, (YT + ys) / 2, r12 - r9o, YT - ys, P.CEMENT, 0.03) for sd in (-1, 1)]
        csg = [st.rect(WX + sd * (rh + 0.045), (YT + ys) / 2, 0.08, YT - ys, P.STEEL, 0.2) for sd in (-1, 1)]
        mud_c = st.rect(WX, (YT + ys) / 2, 2 * (rh + 0.01), YT - ys, P.MUD, 0.05)
        mud_o = st.rect(WX, (ys + YB) / 2, 2 * (rh - 0.02), ys - YB, P.MUD, 0.05)
        pipe = st.rect(WX, (YT + YB + 0.3) / 2, 2 * rp, YT - YB - 0.3, P.STEEL, 0.3)
        shoe = [st.poly([(WX + sd * (rh + 0.09), ys), (WX + sd * (rh + 0.25), ys), (WX + sd * (rh + 0.09), ys + 0.18)], P.STEEL, 0.22) for sd in (-1, 1)]
        dl = [st.text(f"{Z0 + 50:,.0f} m", WX + 1.7, zy(Z0 + 50), 0.15, P.MUTED, 0.3, align="l"),
              st.text(f"{TVD:,.0f} m", WX + 1.7, zy(TVD) + 0.12, 0.15, P.MUTED, 0.3, align="l")]
        objs = [rock, mud_c, mud_o, pipe] + cem + csg + shoe + dl
        st.fade_in(objs, b.start + 0.1, 0.5)
        sl = tag(st, WX + 1.75, ys, "9⅝ in shoe\n3,400 m", P.TEXT, 0.16)
        st.fade_in(sl, b.start + 0.4, 0.4)
        t_wk = W(b, 0, "weak point")
        st.ripple(WX + rh, ys, t_wk, t_wk + 2.0, P.FRAC, period=0.8, r0=0.1, r1=0.6)
        oh = st.line([(WX - rh - 0.3, ys - 0.05), (WX - rh - 0.4, ys - 0.05), (WX - rh - 0.4, YB + 0.05), (WX - rh - 0.3, YB + 0.05)], P.TEXT, 0.025, 0.4)
        ohl = st.text("open\nhole", WX - rh - 0.5, (ys + YB) / 2, 0.15, P.TEXT, 0.4, align="r", kind="bold")
        st.fade_in([oh, ohl], W(b, 0, "open hole") - 0.2, 0.4)
        wk = tag(st, WX + 1.75, ys - 0.75, "the weak point", P.FRAC, 0.17)
        st.fade_in(wk, t_wk, 0.4)

        # the chart: shoe pressure vs the depth of the gas top
        c = Chart(st, 0.75, -2.75, 6.1, 3.3, (Z1, Z0), (556.0, 576.0))
        fr = c.frame(xticks=[4000, 3800, 3600, 3400, 3200, 3000], yticks=[560, 565, 570, 575], xlabel="depth of the top of the gas (m)",
                     ylabel="pressure at the shoe (bar)", fx="{:,.0f}", tick_size=0.15)
        lim = c.hline(P_FRAC_SHOE, P.FRAC, 0.05, 0.3)
        liml = st.text(f"leak-off limit\n{FG_SHOE:.2f} sg = {P_FRAC_SHOE:.0f} bar", c.X(3010), c.Y(P_FRAC_SHOE) - 0.38, 0.16, P.FRAC, 0.3, align="r",
                       kind="bold")
        sv = st.dashed(c.pt(SHOE, 556), c.pt(SHOE, 576), P.MUTED, 0.02, 0.1, 0.08, 0.15, 0.8)
        svl = st.text("gas top\nat the shoe", c.X(SHOE) - 0.1, c.Y(558.3), 0.14, P.MUTED, 0.3, align="r", kind="bold")
        t1 = s[1]
        st.fade_in(fr + [lim, svl, liml] + sv, t1 - 0.3, 0.5)
        st.ripple(c.X(3150), c.Y(P_FRAC_SHOE), W(b, 2, "leak-off"), W(b, 2, "leak-off") + 1.6, P.FRAC, period=0.8, r0=0.1, r1=0.6)
        # gas rising during circulation (small kick, then a bigger one)
        gx0, gx1 = rp + 0.02, rh - 0.04
        t_a0, t_a1 = t1 + 0.2, W(b, 1, "as the gas arrives", 1.0) + 0.6
        t_a2 = s[2] - 0.2
        t_b0, t_b1 = W(b, 2, "too big") - 0.2, W(b, 2, "passes the limit", 1.0)
        t_b2 = W(b, 2, "escapes underground", 1.0)

        def run(h0, ta, tb, tc):
            """ztop over time: bottom -> shoe in [ta, tb], shoe -> 3,050 m in [tb, tc]."""
            def zt(t):
                if t <= ta:
                    return TVD - h0
                if t <= tb:
                    f = (t - ta) / (tb - ta)
                    return (TVD - h0) + (SHOE - (TVD - h0)) * f
                f = min(1.0, (t - tb) / max(tc - tb, 0.1))
                return SHOE + (3050.0 - SHOE) * f
            return zt
        zs_small = run(KICK_H, t_a0, t_a1 - 0.6, t_a2)
        zs_big = run(BIG_H, t_b0, t_b1, t_b2)

        def draw_gas(cv, t, look):
            if t < t1 - 0.4:
                return
            if t < t_b0 - 0.4:
                zt, a = zs_small(t), _env(t, t1 - 0.4, t_b0 - 0.5, 0.3)
                h0 = KICK_H
            else:
                zt, a = zs_big(t), _env(t, t_b0 - 0.4, b.end, 0.3)
                h0 = BIG_H
            h = gas_h(h0, zt)
            y1, y0 = zy(zt), zy(min(zt + h, TVD))
            for sd in (-1, 1):
                xa, xb = WX + sd * gx0, WX + sd * gx1
                _slug(cv, look, min(xa, xb), y0, max(xa, xb), y1, P.GAS, a)

        def curve_pts(h0, zfun, ta, t):
            pts = []
            n = 60
            for i in range(n + 1):
                tt = ta + (t - ta) * i / n
                z = zfun(tt)
                pts.append(c.pt(z, min(max(shoe_p(h0, z), 556.0), 576.0)))
            return pts

        def draw_curves(cv, t, look):
            if t >= t_a0:
                a = _env(t, t_a0, b.end, 0.3) * (0.55 if t > t_b0 else 1.0)
                _trace(cv, look, curve_pts(KICK_H, zs_small, t_a0, min(t, t_a2)), P.SAFE, a, 0.06)
            if t >= t_b0:
                a = _env(t, t_b0, b.end, 0.3)
                _trace(cv, look, curve_pts(BIG_H, zs_big, t_b0, min(t, t_b2)), P.TEXT, a, 0.06)
        st.procedural(t1 - 0.4, b.end, 0.32, draw_gas)
        st.procedural(t_a0, b.end, 0.4, draw_curves)
        pk = tag(st, c.X(3720), c.Y(562.4), f"{KICK_H:.0f} m of gas: peaks as it arrives", P.SAFE, 0.16, align="c")
        st.fade_in(pk, W(b, 1, "peaks") - 0.1, 0.4)
        st.fade(pk, t_b0, t_b0 + 0.4, 1.0, 0.5)
        # choke adds pressure as the gas expands
        t_ch = W(b, 1, "choke adds")

        def draw_choke(cv, t, look):
            a = _env(t, t_ch - 0.2, t_b0 - 0.3, 0.4)
            if a <= 0:
                return
            zt = zs_small(t)
            look.draw_text(cv, "CHOKE", 0.75, 2.75, 0.13, P.MUTED, a, "l", "bold")
            look.draw_text(cv, f"{choke_p(KICK_H, zt):.1f} bar ↑", 0.75, 2.35, 0.26, P.WARN, a, "l", "mono")
            look.draw_text(cv, "BOTTOM HOLE", 3.2, 2.75, 0.13, P.MUTED, a, "l", "bold")
            look.draw_text(cv, f"{P_PORE:.0f} bar, held", 3.2, 2.35, 0.26, P.MUD, a, "l", "mono")
        st.procedural(t_ch - 0.3, t_b0, 0.6, draw_choke)
        # too big a kick: past the limit -> crack and losses underground
        bigl = tag(st, c.X(3990), c.Y(568.6), f"too big: {BIG_H:.0f} m of gas", P.TEXT, 0.16)
        st.fade_in(bigl, t_b0 + 0.2, 0.4)
        t_cr = W(b, 2, "rock cracks")
        st.ripple(c.X(SHOE), c.Y(P_FRAC_SHOE), t_b1 - 0.2, t_b1 + 2.0, P.BAD, period=0.7, r0=0.1, r1=0.7)
        crack = [st.line([(WX + sd * (rh - 0.02), ys - 0.12), (WX + sd * 0.75, ys - 0.2), (WX + sd * 1.1, ys - 0.1), (WX + sd * 1.5, ys - 0.25)], P.FRAC,
                         0.045, 0.35) for sd in (-1, 1)]
        st.draw_on(crack, t_cr - 0.2, t_cr + 0.6)
        for sd in (-1, 1):
            st.flow([(WX + sd * 0.3, ys - 0.12), (WX + sd * 0.75, ys - 0.2), (WX + sd * 1.1, ys - 0.1), (WX + sd * 1.5, ys - 0.25)], t_cr, b.end, P.MUD,
                    n=6, speed=0.5, r=0.035, z=0.36)
        esc = tag(st, WX + 1.75, ys - 1.35, "fluid escapes\nunderground", P.FRAC, 0.16)
        st.fade_in(esc, W(b, 2, "escapes") - 0.1, 0.4)
        # kick tolerance
        t_kt = W(b, 3, "kick tolerance")
        kt = tag(st, 0.75, 1.6, f"KICK TOLERANCE here ≈ {KT_H:.0f} m of gas (≈ {KT_V:.1f} m³):\nthe biggest kick whose peak stays under the line\n"
                 "(one of the margins built into the chapter 1 casing design)", P.TEXT, 0.17, align="l")
        st.fade_in(kt, t_kt - 0.3, 0.4)
        ktm = st.ring(c.X(SHOE), c.Y(P_FRAC_SHOE), 0.13, 0.03, P.TEXT, 0.45)
        st.pop_in(ktm, t_kt)


# ---------------------------------------------------------------- 7.08 Macondo (restrained, factual)
def beat_macondo(st, tl):
    b = tl["7.08"]
    s = b.sent
    with st.span(b.start, b.end):
        title = st.text("Macondo  ·  Gulf of Mexico  ·  2010", -6.1, 3.45, 0.3, P.TEXT, 0.5, align="l", kind="bold")
        st.fade_in(title, s[0] + 0.1, 0.5)
        # a simple cased well: casing to the bottom, cement at the bottom, mud column, BOP on the seabed
        WX = -4.4
        ysb, ytd = 1.9, -3.2
        rh = 0.45
        sea = st.rect(WX, (ysb + 3.05) / 2, 2.8, 3.05 - ysb, P.SEA, 0.0)
        rock = st.rect(WX, (ysb + ytd - 0.15) / 2, 2.8, ysb - ytd + 0.15, P.ROCK, 0.0)
        sand = st.rect(WX, ytd + 0.35, 2.8, 0.7, P.SAND, 0.01)
        csg = [st.rect(WX + sd * (rh + 0.04), (ysb + ytd) / 2, 0.07, ysb - ytd, P.STEEL, 0.2) for sd in (-1, 1)]
        cem_a = [st.rect(WX + sd * (rh + 0.22), ytd + 0.55, 0.3, 1.1, P.CEMENT, 0.05) for sd in (-1, 1)]
        cem_s = st.rect(WX, ytd + 0.3, 2 * rh, 0.6, P.CEMENT, 0.05)
        y_sw = ysb - 0.62 * (ysb - ytd - 0.6)                     # displaced to seawater down to here (illustrative)
        mud = st.rect(WX, (ysb + y_sw) / 2, 2 * rh, ysb - y_sw, P.MUD, 0.05)
        mud_lo = st.rect(WX, (y_sw + 0.06 + ytd + 0.6) / 2, 2 * rh, y_sw + 0.06 - ytd - 0.6, P.MUD, 0.049)
        bop = st.rect(WX, ysb + 0.35, 1.5, 0.7, P.PANEL2, 0.25, role="solid")
        bopl = st.text("BOP", WX, ysb + 0.35, 0.17, P.TEXT, 0.27, kind="bold")
        riser = [st.rect(WX + sd * 0.35, (ysb + 0.7 + 3.05) / 2, 0.06, 3.05 - ysb - 0.7, P.STEEL, 0.2) for sd in (-1, 1)]
        rmud = st.rect(WX, (ysb + 0.7 + 3.05) / 2, 0.64, 3.05 - ysb - 0.7, P.MUD, 0.05)
        well = [sea, rock, sand, cem_s, mud, mud_lo, bop, bopl, rmud] + csg + cem_a + riser
        st.fade_in(well, s[0] + 0.3, 0.6)
        nts = st.text("schematic", WX, -3.55, 0.14, P.MUTED, 0.3)
        st.fade_in(nts, s[0] + 0.6, 0.4)
        # five slices of Swiss cheese, one per failure, as spoken
        xs = [-1.6, 0.25, 2.1, 3.95, 5.8]
        names = ["bottom cement", "inflow test", "mud column", "kick detection", "BOP"]
        fails = ["did not seal", "warnings\nexplained away", "replaced with\nseawater", "missed for\n~40 minutes", "did not seal"]
        times = [W(b, 1, "did not seal"), W(b, 3, "explained away"), W(b, 3, "seawater"), W(b, 4, "unnoticed"), W(b, 5, "did not seal")]
        sy0, sy1 = -2.0, 0.6
        slices = []
        hole_y = [-0.3, -1.0, -0.55, -1.15, -0.4]
        for i, x in enumerate(xs):
            sl = st.poly([(x - 0.5, sy0), (x + 0.35, sy0 + 0.25), (x + 0.35, sy1 + 0.25), (x - 0.5, sy1)], P.STEEL_DK, 0.2, alpha=0.9)
            nm = st.text(names[i], x - 0.07, sy0 - 0.35, 0.17, P.TEXT, 0.3, kind="bold")
            st.fade_in([sl, nm], s[0] + 1.2 + 0.25 * i, 0.4)
            slices.append(sl)
            t = times[i]
            hole = st.ellipse(x - 0.07, hole_y[i], 0.2, 0.28, P.BG, 0.25, role="hole")
            st.pop_in(hole, t)
            st.recolor(sl, t, t + 0.5, "#4a5568")
            fl = st.text(fails[i], x - 0.07, sy0 - 0.85, 0.15, P.BAD, 0.3, kind="bold")
            st.fade_in(fl, t + 0.1, 0.4)
        # 1 cement at the bottom did not seal: gas path through it
        t1 = times[0]
        crk = st.line([(WX - 0.2, ytd), (WX - 0.05, ytd + 0.25), (WX - 0.15, ytd + 0.45), (WX + 0.05, ytd + 0.6)], P.BAD, 0.04, 0.3)
        st.draw_on(crk, t1 - 0.3, t1 + 0.4)
        # 2 the negative (inflow) test: pressure inside dropped below the rock's
        t_nt = W(b, 2, "drops the pressure")
        gx, gy = -1.6, 2.35
        gp = st.rect(0.375, gy, 4.55, 1.0, P.PANEL, 0.0)
        lab_r = st.text("rock", gx - 0.2, gy + 0.22, 0.15, P.PORE, 0.3, align="l", kind="bold")
        lab_w = st.text("inside the well", gx - 0.2, gy - 0.22, 0.15, P.MUD, 0.3, align="l", kind="bold")
        bar_r = st.rect(gx + 1.3, gy + 0.22, 2.2, 0.16, P.PORE, 0.1, anchor="l")
        bar_w = st.rect(gx + 1.3, gy - 0.22, 2.6, 0.16, P.MUD, 0.1, anchor="l")
        st.fade_in([gp, lab_r, lab_w, bar_r, bar_w], s[2] + 0.2, 0.4)
        st.scale_to(bar_w, t_nt, t_nt + 1.2, sx=1.6)
        prove = st.text("no flow back = the seal holds", 0.375, gy - 0.75, 0.15, P.MUTED, 0.3, kind="bold")
        st.fade_in(prove, W(b, 2, "prove") - 0.2, 0.4)
        # 3 warnings explained away (pressure came back); mud replaced by seawater
        t_w = W(b, 3, "warnings")
        st.scale_to(bar_w, t_w, t_w + 0.8, sx=2.0)
        st.recolor(prove, t_w, t_w + 0.3, P.BAD)
        t_sw = W(b, 3, "seawater")
        st.recolor([mud, rmud], t_sw - 0.2, t_sw + 1.6, P.SEA)
        swl = tag(st, WX + 0.75, 1.2, "seawater", P.TEXT, 0.15)
        st.fade_in(swl, t_sw + 0.4, 0.4)
        st.fade_out([gp, lab_r, lab_w, bar_r, bar_w, prove], s[4] - 0.3, 0.4)
        # 4 the kick, unnoticed ~40 minutes
        t_k = s[4]
        for xo in (-0.15, 0.15):
            st.flow([(WX + xo, ytd + 0.05), (WX + xo, ytd + 0.7), (WX + xo, ysb + 0.1)], t_k, b.end, P.GAS, n=10, speed=0.7, r=0.04, z=0.4)
        clk = st.counter(-1.6, 2.35, t_k + 0.2, s[5] - 0.3, 0, 40, fmt="{:.0f} min unnoticed", size=0.26, color=P.GAS, align="l", hold=s[6] - 0.2)
        # 5 the BOP did not seal
        t_b = times[4]
        st.recolor(bop, t_b - 0.1, t_b + 0.4, "#5a2333")
        st.flow([(WX - 0.1, ysb), (WX - 0.1, 3.05)], t_b, b.end, P.GAS, n=6, speed=1.0, r=0.045, z=0.45)
        st.ripple(WX, ysb + 0.35, t_b, t_b + 1.5, P.BAD, period=0.7, r0=0.3, r1=1.0)
        # 6 eleven people died
        t_d = s[6]
        lives = st.text("11 lives lost", 2.2, 2.35, 0.42, P.TEXT, 0.5, kind="bold")
        st.fade_in(lives, t_d - 0.1, 0.8)
        dimmable = slices
        # 7 every barrier had a flaw: the path through every hole
        t_l = s[7]
        path = [(-2.6, hole_y[0] + 0.3)] + [(x - 0.07, hy) for x, hy in zip(xs, hole_y)] + [(6.9, hole_y[-1] - 0.2)]
        ln = st.line(path, P.GAS, 0.06, 0.4)
        st.draw_on(ln, t_l - 0.2, t_l + 1.8, "BEZIER")
        st.flow(path, t_l + 1.6, b.end, P.GAS, n=10, speed=1.0, r=0.04, z=0.42)
        les = st.text("every barrier had a flaw; every warning was explained away", 2.2, -3.35, 0.2, P.WARN, 0.5, kind="bold")
        st.fade_in(les, W(b, 7, "every barrier") - 0.2, 0.6)


def build(st, tl):
    F.header(st, tl)
    F.well_strip(st, 0.0, tl.dur, strings=[p.name for p in M.programme()], marker=TVD)
    beat_lied(st, tl)
    beat_kick(st, tl)
    beat_detect(st, tl)
    beat_barriers(st, tl)
    beat_shutin(st, tl)
    beat_kill(st, tl)
    beat_tolerance(st, tl)
    beat_macondo(st, tl)
