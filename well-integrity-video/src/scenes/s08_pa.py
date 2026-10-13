"""Chapter 8: Plug and abandonment."""
from __future__ import annotations

import dataclasses
import math

import numpy as np
import skia

from engine.core import (C, W, H, arrow, chip, clamp, draw_panel, draw_paragraph, draw_text, ease_in_out, ease_out,
                         ease_out_back, glow_path, lerp, mix, paint, poly, rgb, trim_path, window, with_alpha, rrect,
                         image_shader)
from engine.scene import Scene
from engine.widgets import icon, bullets, Plot, gauge, stamp, counter, waffle
from engine.well import (WellView, WellState, DEFAULT_STRINGS, draw_formation, draw_well, draw_surface, highlight,
                         highlight_path, region_casing, region_cement, steel_paint, lith_texture, cement_texture,
                         draw_wellhead, LITH_COLORS)

G = 0.0981
SHALLOW = rgb("#2DD4BF")


class SceneImpl(Scene):
    id = "s08_pa"

    def setup(self):
        rnd = np.random.default_rng(21)
        n = 2250
        hot = set(rnd.choice(n, 300, replace=False))
        self.dot_cols = [C.amber if i in hot else rgb("#2A4A6E") for i in range(n)]
        self.hot = hot
        self.parts = [(rnd.uniform(0, 1), rnd.uniform(-1, 1), rnd.uniform(1.5, 3.5)) for _ in range(120)]

    def draw(self, c, t):
        self.draw_scale(c, t)
        self.draw_phases(c, t)
        self.draw_eternal(c, t)
        self.draw_rock(c, t)
        self.draw_lengths(c, t)
        self.draw_material(c, t)
        self.draw_verify(c, t)
        self.draw_methods(c, t)
        self.draw_shale(c, t)
        self.draw_newtech(c, t)

    # ------------------------------------------------------------------ scale
    def draw_scale(self, c, t):
        a = self.vis(t, "scale", "phases", fi=0.8, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        k_ind = ease_in_out(clamp((t - self.c0("industrial") + 0.3) / 0.8))
        rev = clamp((t - self.c0("scale") - 0.3) / 6.0)
        hl = ease_out(clamp((t - self.word_time("scale", "three hundred") + 0.2) / 1.0))
        cols = [mix(rgb("#2A4A6E"), col, hl) for col in self.dot_cols]
        waffle(c, 120, 330, 2250, 75, 9, 4, cols, reveal=rev, a=a * (1 - 0.6 * k_ind))
        cnt = 2250 * ease_out(clamp((t - self.c0("scale") - 0.5) / 5.0))
        draw_text(c, "WELLS ON THE NORWEGIAN SHELF THAT WILL NEED PERMANENT P&A", 120, 220, 20, C.muted, 700, a, tracking=3)
        counter(c, cnt, 120, 300, 70, C.text, a, align="left", suffix="")
        draw_text(c, "≈", 92, 300, 50, C.muted, 500, a * clamp(rev * 3), "right")
        if hl > 0:
            draw_panel(c, 1240, 760, 560, 200, a * hl * (1 - k_ind), glow=C.amber, r=18)
            counter(c, 300 * hl, 1280, 860, 80, C.amber, a * hl * (1 - k_ind), align="left", suffix="")
            draw_text(c, "planned within the next 5–7 years", 1280, 920, 26, C.text, 500, a * hl * (1 - k_ind))
        draw_text(c, "Source: Havtil, 2025", 120, 1010, 18, C.dim, 500, a)
        if k_ind > 0:
            draw_panel(c, 560, 470, 800, 360, a * k_ind, glow=C.primary, r=22)
            icon(c, "rig", 700, 610, 140, C.text, a * k_ind, C.primary)
            draw_text(c, "Industrial P&A", 800, 590, 46, C.text, 600, a * k_ind, display=True)
            draw_text(c, "Semi-submersible designed for plugging", 800, 640, 26, C.muted, 500, a * k_ind)
            draw_text(c, "15–20 wells per year from 2026", 800, 720, 34, C.primary_hi, 700, a * k_ind)
            draw_text(c, "Equinor, 2025", 800, 770, 20, C.dim, 500, a * k_ind)

    # ------------------------------------------------------------------ P&A schematic state
    def pa_state(self, t):
        """Returns WellState for the plug-and-abandonment sequence (phases beat and later uses)."""
        st = WellState()
        st.completion = 0.0
        st.bore_fluid = C.brine
        st.annulus_fluid = C.mud
        st.perforations = 1
        st.surface = "none"
        tp = self.c0("phases")
        k1 = clamp((t - self.word_time("phases", "reservoir abandonment") + 0.3) / 3.0)
        k2 = clamp((t - self.word_time("phases", "intermediate abandonment") + 0.3) / 4.0)
        k3 = clamp((t - self.word_time("phases", "finally removal") + 0.3) / 3.5)
        if t > self.c1("phases") + 0.5:
            k1 = k2 = k3 = 1.0
        strings = list(DEFAULT_STRINGS)
        # phase 2: cut and pull 9 5/8 above TOC
        pull9 = ease_in_out(clamp((k2 - 0.2) / 0.5))
        if pull9 > 0:
            strings[3] = dataclasses.replace(strings[3], top=lerp(0, 2250, pull9) if pull9 < 1 else 2250)
        pull13 = ease_in_out(clamp((k3 - 0.0) / 0.4))
        if pull13 > 0:
            strings[2] = dataclasses.replace(strings[2], top=lerp(0, 450, pull13) if pull13 < 1 else 450)
        cut = ease_in_out(clamp((k3 - 0.6) / 0.4))
        if cut > 0:
            for i in (0, 1):
                strings[i] = dataclasses.replace(strings[i], top=5.0 * cut)
            for i in (2,):
                pass
        st.strings = strings
        plugs = []
        f = ease_out(clamp(k1 * 3))
        plugs.append(dict(top=2955, base=2975, kind="mechanical", alpha=f, key="bp"))
        plugs.append(dict(top=2860, base=2955, kind="cement", alpha=1.0, fill=ease_in_out(clamp(k1 * 2 - 0.3)), key="plug1", dia=8.535))
        plugs.append(dict(top=2560, base=2700, kind="cement", alpha=1.0, fill=ease_in_out(clamp(k1 * 2 - 1.0)), key="plug2", dia=8.535))
        plugs.append(dict(top=1600, base=1780, kind="cement", alpha=1.0, fill=ease_in_out(clamp((k2 - 0.7) / 0.3)), key="plug3", dia=12.415))
        plugs.append(dict(top=160, base=360, kind="cement", alpha=1.0, fill=ease_in_out(clamp((k3 - 0.35) / 0.3)), key="plug4", dia=18.73))
        st.plugs = [p for p in plugs if p.get("fill", 1.0) > 0 and p["alpha"] > 0]
        self.cut = cut
        return st

    def draw_pa_schematic(self, c, t, a, v=None, highlights=True):
        v = v or WellView(axis_x=520, y_top=300, y_bot=1030, sx=7.6, x_left=150, x_right=890,
                          knots_d=(0, 450, 1500, 2500, 3400), knots_f=(0, 0.16, 0.33, 0.56, 1.0))
        st = self.pa_state(t)
        c.save()
        c.clipRect(skia.Rect(130, 90, 910, 1045))
        # sea above the seabed
        c.drawRect(skia.Rect(v.x_left, v.y(0) - 190, v.x_right, v.y(0)), paint(rgb("#0E3550"), 0.9 * a))
        draw_formation(c, v, alpha=a)
        draw_well(c, v, st, t, a)
        if self.cut < 1:
            draw_wellhead(c, v, a * (1 - self.cut), y=v.y(0) - 60 * self.cut)
        else:
            c.drawLine(v.ax - 160, v.y(5), v.ax + 160, v.y(5), paint(C.amber, 0.8 * a, stroke=2))
        c.restore()
        return v, st

    def draw_phases(self, c, t):
        a = self.vis(t, "phases", "eternal", fi=0.8, fo=0.6, a_off=-0.3, b_off=-0.5)
        a_env = self.vis(t, "envelopes", "lengths", fi=0.6, fo=0.6, b_off=-0.5)
        a_ann = self.vis(t, "annulus", "milling", fi=0.6, fo=0.6, b_off=-0.5)
        aa = max(a, a_env, a_ann)
        if aa <= 0:
            return
        v, st = self.draw_pa_schematic(c, t, aa)
        if a > 0:
            draw_text(c, "Three phases", 980, 220, 50, C.text, 600, a, display=True)
            phases = [("1", "Reservoir abandonment", "deep primary and secondary barriers", "reservoir abandonment"),
                      ("2", "Intermediate abandonment", "isolate shallower sources; casing may be cut and pulled", "intermediate abandonment"),
                      ("3", "Wellhead and conductor removal", "cut below the seabed", "finally removal")]
            for i, (num, h1, h2, kw) in enumerate(phases):
                k = ease_out(clamp((t - self.word_time("phases", kw) + 0.3) / 0.6)) * a
                y = 300 + i * 200
                draw_panel(c, 980, y, 840, 170, k, r=18, glow=C.primary)
                draw_text(c, num, 1040, y + 112, 90, C.primary, 300, k, "center", display=True)
                draw_text(c, h1, 1110, y + 72, 36, C.text, 600, k, display=True)
                draw_paragraph(c, h2, 1110, y + 116, 680, 25, C.muted, 400, k)
        if a_env > 0:
            draw_text(c, "Barriers for every source", 980, 220, 50, C.text, 600, a_env, display=True)
            groups = [("Primary barrier", C.primary, ["plug1", "bp"], self.c0("envelopes") + 0.5),
                      ("Secondary barrier", C.secondary, ["plug2"], self.word_time("envelopes", "secondary") - 0.2),
                      ("Open hole to surface barrier", SHALLOW, ["plug4"], self.word_time("envelopes", "near the surface") - 0.2)]
            for i, (lab, col, keys, ti) in enumerate(groups):
                k = ease_out(clamp((t - ti) / 0.6)) * a_env
                for key in keys:
                    highlight(c, v, key, col, k)
                if key == "plug1":
                    highlight_path(c, region_cement(v, st, "prod", 2860, 2950), col, k * 0.8)
                if key == "plug2":
                    highlight_path(c, region_cement(v, st, "prod", 2560, 2700), col, k * 0.8)
                if key == "plug4":
                    highlight_path(c, region_cement(v, st, "surf", 160, 360), col, k * 0.8)
                y = 340 + i * 150
                draw_panel(c, 980, y, 840, 120, k, r=16, border=col)
                c.drawRect(skia.Rect(1000, y + 30, 1012, y + 90), paint(col, k))
                draw_text(c, lab, 1040, y + 72, 34, C.text, 600, k, display=True)
            # the reservoir as source
            kr = ease_out(clamp((t - self.c0("envelopes")) / 0.6)) * a_env
            draw_text(c, "source of inflow", v.x_right - 20, v.y(3120), 22, C.amber, 700, kr, "right", shadow=True)
            draw_text(c, "The plug in the 13⅜ in casing isolates intermediate sources", 980, 860, 22, C.muted, 500, kr)
        if a_ann > 0:
            draw_text(c, "The hard part: the annulus", 980, 220, 50, C.text, 600, a_ann, display=True)
            draw_paragraph(c, "A cement plug inside the casing does nothing if the cement outside the casing is missing.",
                           980, 300, 820, 32, C.text, 500, a_ann)
            # leak path around a plug where annulus cement is missing (illustrated at the 9 5/8 above TOC)
            yl0, yl1 = v.y(2000), v.y(2350)
            kk = ease_out(clamp((t - self.c0("annulus") - 1.5) / 0.8)) * a_ann
            xr = v.ax + v.r(9.625) + 6
            pth = poly([(xr, yl1 + 20), (xr, yl0 - 30)])
            glow_path(c, trim_path(pth, 0, kk), C.red, 3, a_ann, glow=8)
            opts = [("Section milling", "section milling"), ("Perforate, wash and cement", "perforate"), ("Cut and pull", "cut and pulled")]
            draw_text(c, "THREE MAIN OPTIONS", 980, 520, 20, C.amber, 700, a_ann * ease_out(clamp((t - self.word_time("annulus", "three main")) / 0.5)), tracking=4)
            for i, (txt, kw) in enumerate(opts):
                k = ease_out(clamp((t - self.word_time("annulus", "three main") - 0.2 - i * 0.4) / 0.5)) * a_ann
                draw_panel(c, 980, 560 + i * 110, 840, 90, k, r=14)
                draw_text(c, f"{i + 1}", 1020, 618 + i * 110, 36, C.amber, 700, k, "center", display=True)
                draw_text(c, txt, 1060, 618 + i * 110, 32, C.text, 500, k, display=True)

    # ------------------------------------------------------------------ eternal
    def draw_eternal(self, c, t):
        a = self.vis(t, "eternal", "rock", fi=0.7, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        draw_text(c, "PERMANENT ABANDONMENT", 120, 210, 20, C.primary, 700, a, tracking=4)
        draw_text(c, "With an eternal perspective", 120, 270, 52, C.text, 600, a, display=True)
        pl = Plot(240, 360, 1100, 560, (0, 100), (0, 400), xlabel="Time", ylabel="Reservoir pressure (bar)", xticks=[],
                  yticks=[0, 100, 200, 300, 400])
        pl.axes(c, a)
        xs = np.linspace(0, 100, 300)
        ys = []
        for x in xs:
            if x < 8:
                p = 350
            elif x < 38:
                p = 350 - 230 * (1 - math.exp(-(x - 8) / 10))
            else:
                p0 = 350 - 230 * (1 - math.exp(-3.0))
                p = p0 + (345 - p0) * (1 - math.exp(-(x - 38) / 14))
            ys.append(p)
        f = clamp((t - self.c0("eternal") - 0.5) / 8.0)
        pl.line(c, xs, ys, C.amber, 3.5, a, reveal=f)
        spans = [(0, 8, "drilling"), (8, 38, "production: decades"), (38, 100, "abandoned: forever")]
        for (x0, x1, lab) in spans:
            kk = clamp((f * 100 - x0) / 5.0) * a
            c.drawRect(skia.Rect(pl.px(x0) + 2, pl.py(400), pl.px(x1) - 2, pl.py(380)), paint(C.panel_hi, kk))
            draw_text(c, lab, (pl.px(x0) + pl.px(x1)) / 2, pl.py(400) - 14, 20, C.muted, 600, kk, "center")
        if f > 0.7:
            kk = ease_out(clamp((f - 0.7) * 4)) * a
            draw_paragraph(c, "Pressure can build back up over geological time", pl.px(55), pl.py(220), 400, 26, C.amber, 600, kk)
        icon(c, "infinity", 1600, 520, 200, C.text, a * ease_out(clamp((t - self.c0("eternal")) / 1.0)), rgb("#8E9AF0"))
        draw_paragraph(c, "No one will be monitoring the well. The barriers must last indefinitely.", 1450, 700, 380, 28, C.text, 500,
                       a * ease_out(clamp((t - self.word_time("eternal", "no one")) / 0.8)))

    # ------------------------------------------------------------------ rock-to-rock and depth
    def mini_well(self, c, x, top, bot, a, ann_cement=True, plug=(0.4, 0.6), leak=0.0, t=0.0, rock="shale"):
        tp = skia.Paint(Shader=image_shader(lith_texture(rock), 0.6))
        tp.setAlphaf(a)
        c.drawRect(skia.Rect(x - 180, top, x + 180, bot), tp)
        hw, hole = 50, 90
        cp = skia.Paint(Shader=image_shader(cement_texture(), 0.5))
        cp.setAlphaf(a)
        c.drawRect(skia.Rect(x - hole, top, x + hole, bot), paint(C.mud, a))
        if ann_cement:
            for side in (-1, 1):
                c.drawRect(skia.Rect(min(x + side * hw, x + side * hole), top + (bot - top) * plug[0] - 30,
                                     max(x + side * hw, x + side * hole), top + (bot - top) * plug[1] + 30), cp)
        c.drawRect(skia.Rect(x - hw, top, x + hw, bot), paint(C.brine, 0.6 * a))
        c.drawRect(skia.Rect(x - hw, top + (bot - top) * plug[0], x + hw, top + (bot - top) * plug[1]), cp)
        for side in (-1, 1):
            r = skia.Rect(min(x + side * hw, x + side * (hw + 12)), top, max(x + side * hw, x + side * (hw + 12)), bot)
            c.drawRect(r, steel_paint(r.left(), r.right(), a))
            c.drawRect(r, paint(C.bg0, 0.5 * a, stroke=1))
        if leak > 0:
            for side in (-1, 1):
                pth = poly([(x + side * (hw + 20), bot - 10), (x + side * (hw + 20), top + 10)])
                glow_path(c, trim_path(pth, 0, leak), C.red, 3, a, glow=8)
                for k in range(6):
                    life = ((t * 0.5 + k / 6) % 1.0) * leak
                    c.drawCircle(x + side * (hw + 20), bot - 10 - life * (bot - top - 20), 4, paint(C.amber, a))

    def draw_rock(self, c, t):
        a = self.vis(t, "rock", "envelopes", fi=0.7, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        draw_text(c, "Across the full cross-section, rock to rock", 120, 220, 46, C.text, 600, a, display=True)
        k_depth = ease_in_out(clamp((t - self.word_time("rock", "its base") + 0.3) / 0.8))
        a1 = a * (1 - k_depth)
        if a1 > 0:
            leak = clamp((t - self.c0("rock") - 1.5) / 2.0)
            self.mini_well(c, 520, 330, 960, a1, ann_cement=False, leak=leak, t=t)
            self.mini_well(c, 1300, 330, 960, a1, ann_cement=True, t=t)
            kx = ease_out(clamp((t - self.c0("rock") - 3.0) / 0.6)) * a1
            icon(c, "cross", 520, 1010, 50, C.text, kx, C.red)
            icon(c, "check", 1300, 1010, 50, C.text, kx, C.green)
            draw_text(c, "plug inside the casing only", 720, 640, 24, C.red, 600, kx)
            draw_text(c, "plug + annulus cement", 1500, 640, 24, C.green, 600, kx)
        if k_depth > 0:
            ak = a * k_depth
            pl = Plot(260, 330, 760, 620, (200, 600), (2000, 3300), invert_y=True, xlabel="Pressure (bar)", ylabel="Depth (m)",
                      xticks=[200, 300, 400, 500, 600], yticks=[2000, 2400, 2800, 3200])
            pl.axes(c, ak)
            ds = np.linspace(2000, 3300, 60)
            frac = [float(np.interp(d, [0, 500, 1800, 3000, 3400], [1.30, 1.45, 1.62, 1.75, 1.77])) * G * d for d in ds]
            pres = 1.18 * G * 3250
            pot = [pres - 0.25 * G * (3250 - d) for d in ds]   # gas column extrapolated upward
            pl.line(c, frac, ds, C.red, 3, ak, glow=False, dash=[10, 7])
            pl.line(c, pot, ds, C.amber, 3.5, ak)
            # intersection
            dint = next(d for d, f_, p_ in zip(ds, frac, pot) if f_ >= p_)
            c.drawLine(pl.px(200), pl.py(dint), pl.px(600), pl.py(dint), paint(C.text, 0.6 * ak, stroke=1.5))
            draw_text(c, "Fracture pressure", pl.px(frac[8]) + 8, pl.py(ds[8]), 20, C.red, 600, ak)
            draw_paragraph(c, "Potential pressure from below", pl.px(pot[20]) - 220, pl.py(ds[20]) + 4, 200, 20, C.amber, 600, ak)
            c.drawRect(skia.Rect(pl.px(200), pl.py(dint), pl.px(600), pl.py(3300)), paint(C.green, 0.06 * ak))
            c.drawRect(skia.Rect(pl.px(200), pl.py(2000), pl.px(600), pl.py(dint)), paint(C.red, 0.06 * ak))
            draw_text(c, "too shallow", pl.px(560), pl.py(dint) - 30, 22, C.red, 700, ak, "right")
            draw_text(c, "base of barrier here", pl.px(560), pl.py(dint) + 44, 22, C.green, 700, ak, "right")
            draw_panel(c, 1150, 380, 650, 380, ak, r=18, glow=C.primary)
            draw_paragraph(c, "The base of a permanent barrier must sit where the formation is strong enough to withstand the "
                           "potential pressure below.", 1190, 450, 580, 30, C.text, 500, ak)
            kk = ease_out(clamp((t - self.word_time("rock", "too shallow")) / 0.6)) * ak
            draw_paragraph(c, "Too shallow, and the reservoir could fracture the rock beneath the plug.", 1190, 640, 580, 26, C.amber, 600, kk)

    def draw_lengths(self, c, t):
        a = self.vis(t, "lengths", "material", fi=0.7, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        draw_text(c, "NORSOK D-010 REVISION 5 · CEMENT PLUGS", 120, 210, 20, C.primary, 700, a, tracking=3)
        draw_text(c, "Minimum plug lengths", 120, 270, 52, C.text, 600, a, display=True)
        cols = [("Open hole", "100 m MD, at least 50 m above any source of inflow", "open hole", "open"),
                ("Cased hole on a foundation", "50 m MD on a mechanical or cement plug", "fifty meters", "found"),
                ("Cased hole, no foundation", "100 m MD", "otherwise", "free")]
        for i, (h1, h2, kw, kind) in enumerate(cols):
            ti = self.word_time("lengths", kw) - 0.5
            if i == 0:
                ti = min(ti, self.c0("lengths") + 0.3)
            k = ease_out(clamp((t - ti) / 0.8)) * a
            if k <= 0:
                continue
            x = 330 + i * 600
            top, bot = 380, 900
            tp = skia.Paint(Shader=image_shader(lith_texture("shale" if kind != "open" else "claystone"), 0.6))
            tp.setAlphaf(k)
            c.drawRect(skia.Rect(x - 150, top, x + 150, bot), tp)
            cp = skia.Paint(Shader=image_shader(cement_texture(), 0.5))
            cp.setAlphaf(k)
            hw = 60
            if kind == "open":
                c.drawRect(skia.Rect(x - hw - 14, top, x + hw + 14, bot), paint(C.mud, k))
                # source of inflow (permeable zone) at the bottom
                c.drawRect(skia.Rect(x - 150, 740, x + 150, 880), paint(C.amber, 0.45 * k))
                draw_text(c, "source of", x + 160, 800, 20, C.amber, 600, k)
                draw_text(c, "inflow", x + 160, 826, 20, C.amber, 600, k)
                pt, pb = 520, 830
                c.drawRect(skia.Rect(x - hw - 14, pt, x + hw + 14, pb), cp)
                bracket = [(pt, pb, "100 m"), (pt, 820, "")]
            else:
                c.drawRect(skia.Rect(x - hw, top, x + hw, bot), paint(C.brine, 0.6 * k))
                for side in (-1, 1):
                    c.drawRect(skia.Rect(min(x + side * hw, x + side * (hw + 8)), top, max(x + side * hw, x + side * (hw + 8)), bot),
                               steel_paint(x - hw - 8, x + hw + 8, k))
                if kind == "found":
                    pt, pb = 640, 790
                    c.drawRect(skia.Rect(x - hw, 790, x + hw, 820), paint(rgb("#2A2D33"), k))
                    draw_text(c, "mechanical plug", x + 80, 815, 18, C.muted, 600, k)
                    bracket = [(pt, pb, "50 m")]
                else:
                    pt, pb = 490, 790
                    bracket = [(pt, pb, "100 m")]
                c.drawRect(skia.Rect(x - hw, pt, x + hw, pb), cp)
            for (b0, b1, lab) in bracket[:1]:
                bx = x - 190
                c.drawLine(bx, b0, bx, b1, paint(C.primary_hi, k, stroke=3))
                c.drawLine(bx - 10, b0, bx + 10, b0, paint(C.primary_hi, k, stroke=3))
                c.drawLine(bx - 10, b1, bx + 10, b1, paint(C.primary_hi, k, stroke=3))
                draw_text(c, lab, bx - 16, (b0 + b1) / 2 + 10, 30, C.primary_hi, 700, k, "right", display=True)
            if kind == "open":
                bx = x + 170
                c.drawLine(bx, 520, bx, 740, paint(C.amber, k, stroke=2))
                c.drawLine(bx - 6, 520, bx + 6, 520, paint(C.amber, k, stroke=2))
                c.drawLine(bx - 6, 740, bx + 6, 740, paint(C.amber, k, stroke=2))
                draw_text(c, "≥ 50 m", bx + 12, 620, 22, C.amber, 700, k)
                draw_text(c, "above", bx + 12, 646, 18, C.amber, 500, k)
            draw_text(c, h1, x, 950, 28, C.text, 600, k, "center", display=True)
            draw_paragraph(c, h2, x - 250, 990, 500, 21, C.muted, 400, k, align="center")

    def draw_material(self, c, t):
        a = self.vis(t, "material", "verify", fi=0.7, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        draw_text(c, "What a permanent barrier material must do", 120, 250, 50, C.text, 600, a, display=True)
        props = [("Impermeable", "drop", "impermeable", "No flow path through the material itself"),
                 ("Non-shrinking", "layers", "non-shrinking", "Stays in tight contact as it sets and ages"),
                 ("Withstands mechanical loads", "shield", "mechanical", "Pressure, temperature and formation stress"),
                 ("Resists H₂S, CO₂ and hydrocarbons", "flame", "hydrogen", "Chemically stable in the well fluids"),
                 ("Bonds to steel and rock", "lock", "bond", "No micro-annulus at the interfaces"),
                 ("Long-term integrity", "infinity", "impermeable", "Keeps these properties indefinitely")]
        for i, (txt, ic, kw, sub) in enumerate(props):
            r, k_ = divmod(i, 3)
            ti = self.word_time("material", kw) - 0.3 if i < 5 else self.word_time("material", "bond") + 0.9
            if i == 0:
                ti = min(ti, self.c0("material") + 0.3)
            k = ease_out(clamp((t - ti) / 0.6)) * a
            if k <= 0:
                continue
            x = 140 + k_ * 560
            y = 350 + r * 290
            draw_panel(c, x, y, 520, 250, k, r=18, glow=C.primary)
            icon(c, ic, x + 80, y + 95, 80, C.text, k, C.primary)
            hh = draw_paragraph(c, txt, x + 150, y + 82, 340, 30, C.text, 600, k, display=True)
            draw_paragraph(c, sub, x + 40, y + 190, 440, 22, C.muted, 400, k)

    def draw_verify(self, c, t):
        a = self.vis(t, "verify", "annulus", fi=0.7, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        draw_text(c, "Every plug is verified", 120, 250, 50, C.text, 600, a, display=True)
        x, top, bot = 480, 340, 1000
        pt = 720
        hw = 70
        c.drawRect(skia.Rect(x - hw, top, x + hw, bot), paint(C.brine, 0.6 * a))
        cp = skia.Paint(Shader=image_shader(cement_texture(), 0.5))
        cp.setAlphaf(a)
        c.drawRect(skia.Rect(x - hw, pt, x + hw, bot - 40), cp)
        for side in (-1, 1):
            c.drawRect(skia.Rect(min(x + side * hw, x + side * (hw + 10)), top, max(x + side * hw, x + side * (hw + 10)), bot),
                       steel_paint(x - hw - 10, x + hw + 10, a))
        # drill pipe tagging
        kt = ease_in_out(clamp((t - self.word_time("verify", "tagged") + 0.2) / 1.5))
        ptip = top + 40 + (pt - top - 40) * kt
        c.drawRect(skia.Rect(x - 16, top - 40, x + 16, ptip), steel_paint(x - 16, x + 16, a))
        if kt > 0.98:
            c.drawCircle(x, pt, 20, paint(C.amber, 0.5 * a, blur=8))
        kk = ease_out(clamp((t - self.word_time("verify", "tagged") - 1.2) / 0.5)) * a
        draw_panel(c, 800, 360, 1000, 150, kk, r=16)
        icon(c, "magnifier", 870, 435, 60, C.text, kk, C.amber)
        draw_text(c, "Tagged", 940, 425, 36, C.text, 600, kk, display=True)
        draw_text(c, "weight set down on the plug confirms its position", 940, 468, 24, C.muted, 400, kk)
        kp = ease_out(clamp((t - self.word_time("verify", "pressure tested") + 0.2) / 0.5)) * a
        draw_panel(c, 800, 540, 1000, 150, kp, r=16)
        icon(c, "gauge", 870, 615, 60, C.text, kp, C.primary)
        draw_text(c, "Pressure tested (cased hole)", 940, 605, 36, C.text, 600, kp, display=True)
        draw_text(c, "held stable, as for any barrier element", 940, 648, 24, C.muted, 400, kp)
        kl = ease_out(clamp((t - self.word_time("verify", "logging") + 0.2) / 0.5)) * a
        draw_panel(c, 800, 720, 1000, 150, kl, r=16)
        icon(c, "chart", 870, 795, 60, C.text, kl, C.green)
        draw_text(c, "Behind the casing: logged", 940, 785, 36, C.text, 600, kl, display=True)
        draw_text(c, "the external barrier must be verified too", 940, 828, 24, C.muted, 400, kl)

    # ------------------------------------------------------------------ annulus methods
    def method_well(self, c, x, top, bot, a, t, mode, k):
        """Casing in shale with poor annular cement; mode: milling / pwc / cutpull."""
        hw, hole = 64, 108
        tp = skia.Paint(Shader=image_shader(lith_texture("shale"), 0.6))
        tp.setAlphaf(a)
        c.drawRect(skia.Rect(x - 230, top, x + 230, bot), tp)
        c.drawRect(skia.Rect(x - hole, top, x + hole, bot), paint(C.mud, a))
        c.drawRect(skia.Rect(x - hw, top, x + hw, bot), paint(C.brine, 0.6 * a))
        win0, win1 = top + (bot - top) * 0.35, top + (bot - top) * 0.70
        cp = skia.Paint(Shader=image_shader(cement_texture(), 0.5))
        cp.setAlphaf(a)
        if mode == "milling":
            mill = clamp(k * 1.6)
            ycut = win0 + (win1 - win0) * mill
            # casing walls, removed between win0 and ycut
            for side in (-1, 1):
                for (y0, y1) in ((top, win0), (ycut, bot)):
                    if y1 > y0:
                        c.drawRect(skia.Rect(min(x + side * hw, x + side * (hw + 10)), y0, max(x + side * hw, x + side * (hw + 10)), y1),
                                   steel_paint(x - hw - 10, x + hw + 10, a))
            # mill on drill string
            if k < 0.7:
                c.drawRect(skia.Rect(x - 18, top - 40, x + 18, ycut - 10), steel_paint(x - 18, x + 18, a))
                spin = t * 10
                for side in (-1, 1):
                    c.drawLine(x, ycut - 6, x + side * (hw + 12), ycut - 6 + 4 * math.sin(spin), paint(C.amber, a, stroke=5))
                # swarf
                for (u, x_, r) in self.parts[:60]:
                    life = (u + t * 0.5) % 1.0
                    yy = ycut - life * (ycut - top)
                    xx = x + (hw - 10) * (0.3 + 0.7 * abs(x_)) * (1 if x_ > 0 else -1)
                    c.drawRect(skia.Rect(xx, yy, xx + r * 1.6, yy + r * 0.8), paint(C.steel_hi, 0.8 * a))
            kc = ease_in_out(clamp((k - 0.72) / 0.28))
            if kc > 0:
                c.drawRect(skia.Rect(x - hole - 6, win1 - (win1 - win0 + 60) * kc, x + hole + 6, win1 + 20), cp)
        elif mode == "pwc":
            perf = clamp(k / 0.25)
            wash = clamp((k - 0.25) / 0.35)
            cem = clamp((k - 0.62) / 0.38)
            for side in (-1, 1):
                c.drawRect(skia.Rect(min(x + side * hw, x + side * (hw + 10)), top, max(x + side * hw, x + side * (hw + 10)), bot),
                           steel_paint(x - hw - 10, x + hw + 10, a))
            nperf = 9
            for j in range(nperf):
                yy = win0 + (win1 - win0) * (j + 0.5) / nperf
                if (j + 0.5) / nperf <= perf:
                    for side in (-1, 1):
                        c.drawRect(skia.Rect(min(x + side * hw - side * 2, x + side * (hw + 12)), yy - 3, max(x + side * hw, x + side * (hw + 12)), yy + 3), paint(C.bg0, a))
                    if perf < 1 and abs((j + 0.5) / nperf - perf) < 0.12:
                        c.drawCircle(x, yy, 50, paint(C.amber, 0.5 * a, blur=14))
            # annulus being washed: mud fades
            if wash > 0:
                for side in (-1, 1):
                    xa, xb = x + side * (hw + 10), x + side * hole
                    c.drawRect(skia.Rect(min(xa, xb), win0, max(xa, xb), win1), paint(rgb("#3E6E8E"), 0.8 * a * wash))
                if wash < 1:
                    yj = win0 + (win1 - win0) * wash
                    c.drawRect(skia.Rect(x - 20, top - 40, x + 20, yj), steel_paint(x - 20, x + 20, a))
                    for side in (-1, 1):
                        ang = t * 8
                        c.drawLine(x, yj, x + side * (hw + 40), yj + 10 * math.sin(ang), paint(C.primary_hi, 0.8 * a, stroke=4))
            if cem > 0:
                hgt = (win1 - win0 + 40) * cem
                c.drawRect(skia.Rect(x - hole, win1 + 20 - hgt, x + hole, win1 + 20), cp)
        elif mode == "cutpull":
            lift = ease_in_out(clamp((k - 0.35) / 0.65)) * 180
            for side in (-1, 1):
                c.drawRect(skia.Rect(min(x + side * hw, x + side * (hw + 10)), top - lift, max(x + side * hw, x + side * (hw + 10)), win0 - lift),
                           steel_paint(x - hw - 10, x + hw + 10, a))
                c.drawRect(skia.Rect(min(x + side * hw, x + side * (hw + 10)), win0 + 8, max(x + side * hw, x + side * (hw + 10)), bot),
                           steel_paint(x - hw - 10, x + hw + 10, a))
            if k < 0.4:
                c.drawRect(skia.Rect(x - 14, top - 40, x + 14, win0), steel_paint(x - 14, x + 14, a))
                for side in (-1, 1):
                    c.drawLine(x, win0 + 4, x + side * (hw + 8), win0 + 4, paint(C.amber, a, stroke=4))

    def draw_methods(self, c, t):
        for cue, nxt, mode, title, sub in (
                ("milling", "pwc", "milling", "Section milling", "Mill away a length of casing, then set a plug from formation to formation"),
                ("pwc", "cutpull", "pwc", "Perforate, wash and cement", "Perforate, jet the annulus clean, cement behind the pipe, in a single trip"),
                ("cutpull", "shale", "cutpull", "Cut and pull", "Remove the casing above a cut, then plug across the open rock")):
            a = self.vis(t, cue, nxt, fi=0.7, fo=0.6, b_off=-0.5)
            if a <= 0:
                continue
            k = clamp((t - self.c0(cue) - 0.5) / (self.c1(cue) - self.c0(cue) - 1.0))
            draw_text(c, "ANNULUS OPTION", 120, 210, 20, C.amber, 700, a, tracking=4)
            draw_text(c, title, 120, 270, 52, C.text, 600, a, display=True)
            self.method_well(c, 560, 360, 1010, a, t, mode, k)
            draw_paragraph(c, sub, 1000, 420, 800, 34, C.text, 500, a)
            if mode == "milling":
                kk = ease_out(clamp((t - self.word_time("milling", "slow") + 0.2) / 0.6)) * a
                bullets(c, ["Proven", "Slow", "Large volumes of steel swarf"], 1000, 620, t,
                        [self.word_time("milling", "it works") - 0.2, self.word_time("milling", "slow") - 0.2, self.word_time("milling", "swarf") - 0.4],
                        size=32, alpha=a, accent=C.amber)
            elif mode == "pwc":
                steps = ["Perforate", "Wash", "Cement"]
                kws = ["shoots holes", "jets", "squeezes"]
                for i, (sname, kw) in enumerate(zip(steps, kws)):
                    kk = ease_out(clamp((t - self.word_time("pwc", kw) + 0.2) / 0.5)) * a
                    draw_panel(c, 1000 + i * 270, 600, 250, 100, kk, r=14, glow=C.primary)
                    draw_text(c, sname, 1125 + i * 270, 664, 32, C.text, 600, kk, "center", display=True)
                kc = ease_out(clamp((t - self.word_time("pwc", "revision five") + 0.2) / 0.6)) * a
                chip(c, 1000, 760, "D-010 rev. 5: defined premises and a best practice for verification", C.primary, kc, size=22)
            else:
                kw = ease_out(clamp((t - self.word_time("cutpull", "troll") + 0.2) / 0.6)) * a
                draw_panel(c, 1000, 600, 820, 220, kw, r=18, glow=C.red, border=C.red)
                icon(c, "warning", 1070, 680, 70, C.text, kw, C.red)
                draw_paragraph(c, "Keep well control barriers in place, and know what is behind the pipe before you cut.", 1130, 660,
                               650, 30, C.text, 600, kw)

    # ------------------------------------------------------------------ creeping shale
    def draw_shale(self, c, t):
        a = self.vis(t, "shale", "newtech", fi=0.7, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        k2 = ease_in_out(clamp((t - self.c0("shale2") + 0.3) / 0.8))
        draw_text(c, "FORMATION AS A BARRIER", 120, 210, 20, C.green, 700, a, tracking=4)
        draw_text(c, "Creeping shale", 120, 270, 52, C.text, 600, a, display=True)
        x, top, bot = 520, 360, 1010
        hw = 64
        creep = ease_in_out(clamp((t - self.c0("shale") - 1.5) / 9.0))
        gap0 = 60
        gap = gap0 * (1 - creep)
        tp = skia.Paint(Shader=image_shader(lith_texture("claystone"), 0.6))
        tp.setAlphaf(a)
        # shale walls moving inward in the middle interval
        zt, zb = 480, 880
        for side in (-1, 1):
            pth = skia.Path()
            xo = x + side * 260
            xi_far = x + side * (hw + 10 + gap0)
            xi_mid = x + side * (hw + 10 + gap)
            pth.moveTo(xo, top)
            pth.lineTo(xi_far, top)
            pth.lineTo(xi_far, zt)
            pth.cubicTo(xi_far, zt + 60, xi_mid, zt + 80, xi_mid, zt + 120)
            pth.lineTo(xi_mid, zb - 120)
            pth.cubicTo(xi_mid, zb - 80, xi_far, zb - 60, xi_far, zb)
            pth.lineTo(xi_far, bot)
            pth.lineTo(xo, bot)
            pth.close()
            c.drawRect(skia.Rect(min(xo, x + side * (hw + 10)), top, max(xo, x + side * (hw + 10)), bot), paint(C.mud, a))
            c.drawPath(pth, tp)
            c.drawPath(pth, paint(C.black, 0.3 * a, stroke=1.5))
        c.drawRect(skia.Rect(x - hw, top, x + hw, bot), paint(C.brine, 0.6 * a))
        for side in (-1, 1):
            c.drawRect(skia.Rect(min(x + side * hw, x + side * (hw + 10)), top, max(x + side * hw, x + side * (hw + 10)), bot),
                       steel_paint(x - hw - 10, x + hw + 10, a))
            for k in range(4):
                yy = zt + 140 + k * 70
                arrow(c, x + side * 230, yy, x + side * (hw + 30 + gap), yy, C.green, 2.5, a * (1 - creep * 0.7), head=10)
        if creep > 0.95:
            for side in (-1, 1):
                c.drawRect(skia.Rect(min(x + side * (hw + 10), x + side * (hw + 16)), zt + 120, max(x + side * (hw + 10), x + side * (hw + 16)), zb - 120),
                           paint(C.green, 0.8 * a))
            draw_text(c, "contact:", x + 275, (zt + zb) / 2 - 6, 22, C.green, 700, a)
            draw_text(c, "annulus sealed", x + 275, (zt + zb) / 2 + 22, 22, C.green, 700, a)
        items = ["Clay-rich, smectite-bearing shales", "Ductile, low permeability", "Creep under stress until they grip the casing",
                 "Used as a barrier element on the NCS since 2006"]
        kws = ["rich in clay", "ductile", "creep under", "since 2006"]
        times = [self.word_time("shale", kw) - 0.3 for kw in kws]
        bullets(c, items, 1000, 420, t, times, size=30, max_w=800, alpha=a * (1 - k2), accent=C.green, gap=1.7)
        if k2 > 0:
            ak = a * k2
            # verification by logging + Havtil report
            draw_panel(c, 1000, 420, 820, 210, ak, r=18)
            draw_text(c, "Verified by logging", 1040, 485, 34, C.text, 600, ak, display=True)
            draw_paragraph(c, "Bond-like response where no cement was placed; D-010 element acceptance criteria for creeping "
                           "formation.", 1040, 535, 740, 25, C.muted, 400, ak)
            kh = ease_out(clamp((t - self.word_time("shale2", "in 2025") + 0.3) / 0.6)) * ak
            draw_panel(c, 1000, 670, 820, 230, kh, r=18, glow=C.green)
            draw_text(c, "HAVTIL · 2025", 1040, 725, 20, C.green, 700, kh, tracking=4)
            draw_paragraph(c, "Knowledge study on creeping shale: potentially an efficient and cost-effective barrier behind "
                           "casing; further research and more specific requirements needed.", 1040, 775, 740, 25, C.text, 500, kh)

    # ------------------------------------------------------------------ new technology
    def draw_newtech(self, c, t):
        a = self.vis(t, "newtech", self.dur, fi=0.7, fo=0.6)
        if a <= 0:
            return
        kq = ease_in_out(clamp((t - self.c0("qualify") + 0.2) / 0.8))
        draw_text(c, "New materials and methods", 120, 250, 50, C.text, 600, a, display=True)
        tiles = [("Bismuth alloys", "Melted in place; expands slightly as it solidifies. Dozens of plugs set on Valhall.", "bismuth"),
                 ("Thermite", "Melts casing, cement and rock into a single seal. Tested at full scale in Norway.", "thermite"),
                 ("Through-tubing logging", "Logging through tubing and two casing strings may enable rigless P&A.", "logging through")]
        for i, (h1, body, kw) in enumerate(tiles):
            ti = self.word_time("newtech", kw) - 0.4
            k = ease_out(clamp((t - ti) / 0.7)) * a
            if k <= 0:
                continue
            x = 120 + i * 580
            y = 330
            draw_panel(c, x, y, 540, 600, k, r=20, glow=[rgb("#B7B9C8"), C.orange, C.primary][i])
            # illustration
            cx, cy = x + 270, y + 190
            ph = t - ti
            if i == 0:
                c.drawRect(skia.Rect(cx - 60, cy - 120, cx - 48, cy + 120), steel_paint(cx - 60, cx - 48, k))
                c.drawRect(skia.Rect(cx + 48, cy - 120, cx + 60, cy + 120), steel_paint(cx + 48, cx + 60, k))
                fill = clamp(ph / 3.0)
                col = mix(rgb("#FF8A3D"), rgb("#B7B9C8"), clamp((ph - 2.5) / 2.0))
                c.drawRect(skia.Rect(cx - 48, cy + 120 - 140 * fill, cx + 48, cy + 120), paint(col, k))
                if ph > 3.5:
                    for side in (-1, 1):
                        arrow(c, cx + side * 20, cy + 50, cx + side * 44, cy + 50, C.text, 2, k * clamp(ph - 3.5), head=8)
                    draw_text(c, "expands ~3% on freezing", cx, cy + 160, 18, C.muted, 600, k, "center")
            elif i == 1:
                glow = 0.5 + 0.5 * math.sin(ph * 6)
                c.drawCircle(cx, cy, 90, paint(rgb("#FF6A00"), 0.35 * k, blur=30))
                c.drawCircle(cx, cy, 60 + 6 * glow, paint(rgb("#FFB347"), 0.9 * k))
                c.drawCircle(cx, cy, 30, paint(C.white, 0.85 * k, blur=6))
                for kk in range(10):
                    ang = kk * 0.63 + ph * 2
                    rr = 70 + 30 * ((ph * 0.7 + kk * 0.1) % 1.0)
                    c.drawCircle(cx + rr * math.cos(ang), cy + rr * math.sin(ang), 3, paint(rgb("#FFD27A"), k))
            else:
                for side in (-1, 1):
                    for od in (40, 80, 110):
                        c.drawRect(skia.Rect(cx + side * od - (4 if side > 0 else 0), cy - 120, cx + side * od + (0 if side > 0 else 4), cy + 120),
                                   steel_paint(cx + side * od - 4, cx + side * od + 4, k))
                ty = cy - 80 + 160 * ((ph * 0.15) % 1.0)
                c.drawRoundRect(skia.Rect(cx - 12, ty - 40, cx + 12, ty + 40), 6, 6, paint(rgb("#C9A227"), k))
                for rr in (40, 80, 110):
                    pr = ((t * 1.5) % 1.0)
                    c.drawCircle(cx, ty, 20 + pr * 100, paint(C.primary_hi, k * (1 - pr) * 0.5, stroke=2))
            draw_text(c, h1, x + 40, y + 430, 34, C.text, 600, k, display=True)
            draw_paragraph(c, body, x + 40, y + 476, 460, 24, C.muted, 400, k)
        if kq > 0:
            c.drawRect(skia.Rect(0, 0, W, H), paint(C.bg0, 0.88 * kq * a))
            stamp(c, W / 2, H / 2 - 40, "QUALIFIED FOR ITS PURPOSE", C.green, kq * a, size=44)
            draw_text(c, "before it can be credited as a permanent barrier element", W / 2, H / 2 + 80, 32, C.text, 500, kq * a, "center")
            chip(c, W / 2, H / 2 + 120, "Technology qualification: DNV-RP-A203", C.green, kq * a, size=22, align="center")
