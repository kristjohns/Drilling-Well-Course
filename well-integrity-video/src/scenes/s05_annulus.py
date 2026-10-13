"""Chapter 5: Annulus pressure management."""
from __future__ import annotations

import math

import numpy as np
import skia

from engine.core import (C, W, H, arrow, chip, clamp, draw_panel, draw_paragraph, draw_text, ease_in_out, ease_out,
                         ease_out_back, glow_path, lerp, mix, paint, poly, rgb, trim_path, window, with_alpha, rrect,
                         image_shader)
from engine.scene import Scene
from engine.widgets import icon, bullets, Plot, gauge, stamp
from engine.well import (WellView, WellState, draw_formation, draw_well, draw_surface, highlight, highlight_path,
                         rect_path, _annulus_segments, region_casing, steel_paint, cement_texture)

G = 0.0981
COL_A, COL_B, COL_C = rgb("#2DD4BF"), rgb("#A78BFA"), rgb("#FB923C")


def a_internal(ps, d):
    return ps + 1.20 * G * d


def burst_limit(d):
    return 640 + 1.03 * G * d


def collapse_limit(d):
    return 120 + 0.2 * G * d + 470


class SceneImpl(Scene):
    id = "s05_annulus"

    def setup(self):
        rnd = np.random.default_rng(9)
        self.parts = [(rnd.uniform(0, 1), rnd.uniform(-1, 1), rnd.uniform(1.5, 3.2)) for _ in range(90)]
        self.v = WellView(axis_x=1420, y_top=380, y_bot=1030, sx=7.0, x_left=1060, x_right=1800)

    def state(self, t):
        st = WellState()
        st.completion = 1
        st.a_annulus_fluid = C.brine
        st.perforations = 1
        st.bore_fluid = C.oil
        st.annulus_fluid = C.mud
        hot = self.vis(t, "thermal", "apb", fi=0.8, fo=0.8)
        st.tubing_fluid = mix(C.oil, rgb("#FF7A2F"), hot)
        return st

    def ann_region(self, v, st, key, d0, d1):
        idx = next(i for i, s in enumerate(st.strings) if s.key == key)
        s = st.strings[idx]
        p = skia.Path()
        for (a, b, outer) in _annulus_segments(st, idx, d0, d1):
            for (xa, xb) in ((v.xl(outer), v.xl(s.od)), (v.xr(s.od), v.xr(outer))):
                p.addRect(skia.Rect(xa, v.y(a), xb, v.y(b)))
        return p

    def draw(self, c, t):
        self.draw_annuli(c, t)
        self.draw_sources(c, t)
        self.draw_maasp(c, t)
        self.draw_trend(c, t)
        self.draw_gullfaks(c, t)

    # ------------------------------------------------------------------ annuli & sources
    def draw_schematic(self, c, t, a, show_abc=1.0):
        v = self.v
        st = self.state(t)
        c.save()
        c.clipRect(skia.Rect(1040, 90, 1820, 1045))
        draw_formation(c, v, alpha=a)
        draw_well(c, v, st, t, a)
        draw_surface(c, v, st, a)
        if show_abc > 0:
            ka = ease_out(clamp((t - self.word_time("annuli", "a-annulus") + 0.3) / 0.6)) * show_abc
            kb = ease_out(clamp((t - self.word_time("annuli", "b-annulus") + 0.3) / 0.6)) * show_abc
            kc = ease_out(clamp((t - self.word_time("annuli", "c-annulus") + 0.3) / 0.6)) * show_abc
            highlight(c, v, "a_annulus", COL_A, a * ka, fill=0.45)
            highlight_path(c, self.ann_region(v, st, "prod", 0, 2350), COL_B, a * kb, fill=0.45)
            highlight_path(c, self.ann_region(v, st, "int", 0, 1200), COL_C, a * kc, fill=0.45)
        c.restore()
        return v, st

    def draw_annuli(self, c, t):
        a = self.vis(t, "annuli", "maasp", fi=0.8, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        v, st = self.draw_schematic(c, t, a, show_abc=self.vis(t, "annuli", "sources", fi=0.5, fo=0.6, b_off=1.0))
        # rings (top view) during annuli beat
        ar = self.vis(t, "annuli", "sources", fi=0.6, fo=0.6, b_off=-0.2)
        if ar > 0:
            cx, cy = 520, 600
            rings = [  # (radius px, colour, label)
                (300, rgb("#3F4A4B"), None), (270, C.cement, None), (240, C.steel, "20 in casing"),
                (226, COL_C, "C-annulus"), (190, C.steel, "13⅜ in casing"), (176, COL_B, "B-annulus"),
                (136, C.steel, "9⅝ in production casing"), (122, COL_A, "A-annulus"), (62, C.steel, "tubing"), (52, C.oil, None)]
            keys = {"A-annulus": "a-annulus", "B-annulus": "b-annulus", "C-annulus": "c-annulus"}
            for (r, col, lab) in rings:
                hot = 0.0
                if lab in keys:
                    hot = ease_out(clamp((t - self.word_time("annuli", keys[lab]) + 0.3) / 0.6))
                    col = mix(mix(col, C.bg0, 0.55), col, hot)
                if col == C.cement:
                    cp = skia.Paint(AntiAlias=True, Shader=image_shader(cement_texture(), 0.5))
                    cp.setAlphaf(ar)
                    c.drawCircle(cx, cy, r, cp)
                else:
                    c.drawCircle(cx, cy, r, paint(col, ar))
                if hot > 0:
                    c.drawCircle(cx, cy, r, paint(col, 0.35 * ar * hot, blur=10, stroke=6))
            # labels
            labs = [("A-annulus", 92, COL_A, "a-annulus"), ("B-annulus", 156, COL_B, "b-annulus"), ("C-annulus", 208, COL_C, "c-annulus")]
            for (txt, rr, col, kw) in labs:
                k = ease_out(clamp((t - self.word_time("annuli", kw) + 0.2) / 0.6)) * ar
                ang = math.radians(-35)
                x0, y0 = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
                c.drawLine(x0, y0, cx + 330, y0 - 80 + (rr - 92) * 0.9, paint(col, k, stroke=2))
                c.drawCircle(x0, y0, 5, paint(C.white, k))
                draw_text(c, txt, cx + 340, y0 - 72 + (rr - 92) * 0.9, 30, col, 700, k, display=True)
            draw_text(c, "Nested pressure vessels", 120, 220, 48, C.text, 600, ar, display=True)
            draw_text(c, "cross-section", cx, cy + 340, 20, C.muted, 500, ar, "center")

    def draw_sources(self, c, t):
        a = self.vis(t, "sources", "maasp", fi=0.6, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        draw_text(c, "Where annulus pressure comes from", 120, 220, 46, C.text, 600, a, display=True)
        items = [("Heat", "thermo", "thermal", rgb("#FF7A2F")), ("Applied", "gauge", "applied", COL_A), ("Leaks", "drop", "leak", C.red)]
        for i, (lab, ic, cue, col) in enumerate(items):
            ti = self.c0("sources") + 0.3 + i * 0.5
            k = ease_out_back(clamp((t - ti) / 0.6)) * a
            active = self.vis(t, cue, None, fi=0.4, fo=0.4)
            x = 140 + i * 280
            y = 330
            if k <= 0:
                continue
            c.drawRoundRect(skia.Rect(x, y, x + 240, y + 150), 18, 18, paint(mix(C.panel, C.panel_hi, active), k))
            c.drawRoundRect(skia.Rect(x, y, x + 240, y + 150), 18, 18, paint(mix(C.line, col, active), k, stroke=2))
            icon(c, ic, x + 120, y + 62, 60, C.text, k, col)
            draw_text(c, lab, x + 120, y + 128, 28, C.text, 600, k, "center")
        v = self.v
        st = self.state(t)
        # thermal beat
        at = self.vis(t, "thermal", "apb", fi=0.6, fo=0.5)
        if at > 0:
            val = 20 + 130 * ease_in_out(clamp((t - self.c0("thermal") - 1.0) / 6.0))
            gauge(c, 330, 680, 90, val, 0, 250, "A-annulus pressure", "bar", at, color=rgb("#FF7A2F"),
                  zones=[(0, 150, with_alpha(C.green, 0.5)), (150, 250, with_alpha(C.red, 0.5))])
            draw_paragraph(c, "Hot production fluid heats the trapped annulus fluid. In a sealed annulus it has nowhere to go.",
                           520, 620, 440, 28, C.text, 400, at)
            # agitated particles in the A-annulus
            prod_id = 8.535
            for (u, x_, r) in self.parts:
                d = u * 2700 + 30 * math.sin(t * 5 + x_ * 9)
                side = 1 if x_ > 0 else -1
                rr = v.r(4.5) + 3 + abs(x_) * (v.r(prod_id) - v.r(4.5) - 6)
                c.drawCircle(v.ax + side * rr + 1.5 * math.sin(t * 13 + u * 40), v.y(d), r, paint(C.white, 0.5 * at))
        # APB mitigations
        ap = self.vis(t, "apb", "applied", fi=0.6, fo=0.5)
        if ap > 0:
            draw_text(c, "SUBSEA WELLS", 140, 600, 20, COL_B, 700, ap, tracking=4)
            draw_paragraph(c, "Outer annuli are often sealed and cannot be bled off: trapped pressure is handled in the design.",
                           140, 650, 820, 30, C.text, 500, ap)
            mit = ["Stronger casing", "Burst disks", "Compressible foam or nitrogen cushions", "Insulated tubing"]
            kws = ["stronger", "burst", "foam", "insulated"]
            times = [self.word_time("apb", kw) - 0.3 for kw in kws]
            bullets(c, mit, 140, 780, t, times, size=28, max_w=820, alpha=ap, accent=COL_B, gap=1.55)
            # B and C annuli locked
            for key, d1, col in (("prod", 2350, COL_B), ("int", 1200, COL_C)):
                highlight_path(c, self.ann_region(v, st, key, 0, d1), col, ap * 0.8, fill=0.4)
            icon(c, "lock", v.ax + v.r(30) + 60, v.y(0) + 90, 54, C.text, ap, COL_B)
        # applied (gas lift)
        ag = self.vis(t, "applied", "leak", fi=0.6, fo=0.5)
        if ag > 0:
            draw_text(c, "GAS LIFT", 140, 600, 20, COL_A, 700, ag, tracking=4)
            draw_paragraph(c, "Lift gas is injected into the A-annulus and enters the tubing through gas lift valves.", 140, 650,
                           820, 30, C.text, 500, ag)
            highlight(c, v, "a_annulus", COL_A, ag * 0.5, fill=0.3)
            glv = 2300
            for (u, x_, r) in self.parts[:60]:
                life = (u + t * 0.25) % 1.0
                if x_ > 0:
                    d = life * glv
                    rr = v.r(4.5) + 4 + abs(x_) * (v.r(8.535) - v.r(4.5) - 8)
                    c.drawCircle(v.ax + rr, v.y(d), r, paint(C.white, 0.7 * ag))
                else:
                    d = glv - life * glv
                    c.drawCircle(v.ax + x_ * v.r(3.6), v.y(d), r * 1.3, paint(C.gas, 0.8 * ag))
            c.drawRect(skia.Rect(v.ax + v.r(4.5) - 2, v.y(glv) - 9, v.ax + v.r(4.5) + 9, v.y(glv) + 9), paint(COL_A, ag))
        # leaks
        al = self.vis(t, "leak", "maasp", fi=0.6, fo=0.6, b_off=-0.5)
        if al > 0:
            draw_text(c, "LEAK PATHS", 140, 600, 20, C.red, 700, al, tracking=4)
            paths = [("Tubing connection or packer leak", "connection"), ("Casing leak", "casing leak"), ("Gas migrating through poor cement", "migrating")]
            times = [self.word_time("leak", kw) - 0.3 for _, kw in paths]
            bullets(c, [p for p, _ in paths], 140, 660, t, times, size=28, max_w=820, alpha=al, accent=C.red, gap=1.5)
            # bubbles from a tubing connection into the A-annulus
            kd = clamp((t - times[0]) / 0.5)
            dleak = 1600
            for (u, x_, r) in self.parts[:40]:
                life = (u + t * 0.3) % 1.0
                d = dleak - life * dleak
                rr = v.r(4.5) + 4 + abs(x_) * (v.r(8.535) - v.r(4.5) - 8)
                c.drawCircle(v.ax - rr, v.y(d), r * 1.2, paint(C.gas, 0.85 * al * kd))
            c.drawCircle(v.ax - v.r(4.5), v.y(dleak), 10, paint(C.red, al * kd, stroke=2.5))
            # gas migration through poor cement in B annulus
            kg = clamp((t - times[2]) / 0.5)
            for (u, x_, r) in self.parts[40:70]:
                life = (u + t * 0.18) % 1.0
                d = 2700 - life * 2600
                c.drawCircle(v.ax + v.r(9.625) + 4 + abs(x_) * 6, v.y(d), r, paint(C.gas, 0.85 * al * kg))
            # SCP sawtooth
            ks = ease_out(clamp((t - self.word_time("leak", "sustained casing pressure") + 0.3) / 0.6)) * al
            if ks > 0:
                pl = Plot(560, 870, 420, 130, (0, 30), (0, 100), xlabel="", ylabel="", xticks=[], yticks=[])
                pl.axes(c, ks, grid=False)
                xs = np.linspace(0, 30, 300)
                ys = [80 * (1 - math.exp(-((x % 10)) / 2.5)) + 5 for x in xs]
                pl.line(c, xs, ys, C.red, 3, ks, reveal=clamp((t - self.word_time("leak", "sustained casing pressure")) / 4))
                draw_text(c, "bled off ... and it comes back", 560, 860, 20, C.red, 600, ks)

    # ------------------------------------------------------------------ MAASP
    def draw_maasp(self, c, t):
        a1 = self.vis(t, "maasp", "weakest", fi=0.7, fo=0.6, b_off=-0.4)
        if a1 > 0:
            draw_text(c, "MAASP", W / 2, 420, 150, C.amber, 800, a1, "center", display=True, tracking=8)
            draw_text(c, "Maximum Allowable Annulus Surface Pressure", W / 2, 500, 40, C.text, 500, a1, "center", display=True)
            kk = ease_out(clamp((t - self.word_time("maasp", "highest pressure")) / 0.8)) * a1
            draw_paragraph(c, "The highest pressure an annulus may contain, measured at the wellhead, without compromising any "
                           "well barrier element in that annulus.", 460, 620, 1000, 34, C.muted, 400, kk, align="center")
        a2 = self.vis(t, "weakest", "plot", fi=0.7, fo=0.6, b_off=-0.4)
        if a2 > 0:
            v = self.v
            st = self.state(t)
            c.save()
            c.clipRect(skia.Rect(1040, 90, 1820, 1045))
            draw_formation(c, v, alpha=a2)
            draw_well(c, v, st, t, a2)
            draw_surface(c, v, st, a2)
            c.restore()
            draw_text(c, "Find the weakest point", 120, 220, 48, C.text, 600, a2, display=True)
            pts = [
                ("Burst of the outer casing", "burst", v.ax - v.r(9.625), v.y(2200)),
                ("Collapse of the inner string", "collapse", v.ax - v.r(4.5), v.y(2700)),
                ("Packer rating", "packer", v.ax - v.r(7), v.y(2800)),
                ("Hanger, wellhead and valves", "wellhead", v.ax - v.r(30), v.y(0) - 25),
                ("Formation strength at the shoe", "formation", v.ax - v.r(17.5), v.y(1800)),
            ]
            for i, (txt, kw, x, y) in enumerate(pts):
                k = ease_out(clamp((t - self.word_time("weakest", kw) + 0.2) / 0.6)) * a2
                if k <= 0:
                    continue
                ly = 330 + i * 120
                c.drawLine(x, y, 960, ly, paint(C.amber, 0.7 * k, stroke=1.6))
                c.drawCircle(x, y, 9, paint(C.amber, k))
                c.drawCircle(x, y, 18, paint(C.amber, 0.3 * k, blur=6))
                draw_panel(c, 120, ly - 44, 840, 88, k, r=14)
                draw_text(c, txt, 150, ly + 11, 32, C.text, 500, k)
        a3 = self.vis(t, "plot", "limits", fi=0.7, fo=0.6, b_off=-0.5)
        if a3 > 0:
            self.draw_maasp_plot(c, t, a3)

    def draw_maasp_plot(self, c, t, a):
        pl = Plot(220, 230, 900, 740, (0, 900), (0, 2800), invert_y=True, xlabel="Pressure in the A-annulus (bar)", ylabel="Depth (m)",
                  xticks=[0, 150, 300, 450, 600, 750, 900], yticks=[0, 700, 1400, 2100, 2800])
        pl.axes(c, a)
        ds = np.linspace(0, 2800, 60)
        kl = ease_in_out(clamp((t - self.c0("plot") - 0.5) / 2.0))
        pl.line(c, [burst_limit(d) for d in ds], ds, C.red, 3, a, reveal=kl, glow=False, dash=[12, 7])
        pl.line(c, [collapse_limit(d) for d in ds], ds, C.amber, 3, a, reveal=kl, glow=False, dash=[12, 7])
        # wellhead rating at surface
        c.drawLine(pl.px(345), pl.py(0) - 2, pl.px(345), pl.py(180), paint(C.common, a * kl, stroke=4))
        draw_text(c, "Wellhead rating", pl.px(345) + 10, pl.py(170), 20, C.common, 600, a * kl)
        draw_text(c, "Casing burst limit", pl.px(burst_limit(900)) + 10, pl.py(900), 20, C.red, 600, a * kl)
        draw_text(c, "Tubing collapse limit", pl.px(collapse_limit(1500)) - 12, pl.py(1500), 20, C.amber, 600, a * kl, "right")
        # sweep surface pressure
        ts = self.word_time("plot", "raise the surface pressure") - 0.2
        ps = 315 * ease_in_out(clamp((t - ts) / 5.5))
        if t > ts:
            ys = [a_internal(ps, d) for d in ds]
            pl.line(c, ys, ds, C.primary, 4, a)
            c.drawCircle(pl.px(ps), pl.py(0), 8, paint(C.primary_hi, a))
            draw_text(c, f"surface pressure {ps:.0f} bar", pl.px(ps) + 12, pl.py(0) + 64, 22, C.primary_hi, 700, a)
        touch = ease_out(clamp((t - ts - 5.6) / 0.6))
        if touch > 0:
            x, y = pl.px(a_internal(315, 2800)), pl.py(2800)
            c.drawCircle(x, y, 14 + 10 * touch, paint(C.amber, 0.4 * a * touch, blur=8))
            c.drawCircle(x, y, 8, paint(C.amber, a * touch))
            draw_panel(c, 1200, 330, 620, 330, a * touch, glow=C.amber, r=18)
            draw_text(c, "MAASP", 1240, 400, 26, C.amber, 700, a * touch, tracking=4)
            draw_text(c, "≈ 315 bar", 1240, 480, 72, C.text, 700, a * touch, display=True)
            draw_paragraph(c, "Governed here by tubing collapse at the packer, deep in the well, not at the wellhead.", 1240, 540,
                           540, 26, C.muted, 400, a * touch)
            draw_text(c, "Illustrative values", 1240, 700, 18, C.dim, 500, a * touch, italic=True)
        kd = ease_out(clamp((t - self.c0("plot") - 1.0) / 0.8)) * (1 - touch)
        if kd > 0:
            draw_panel(c, 1200, 330, 620, 260, a * kd, r=18)
            draw_paragraph(c, "Each limit is evaluated at depth, corrected for the fluids inside and behind the annulus, and "
                           "derated for temperature and design factors.", 1240, 390, 540, 26, C.text, 400, a * kd)

    # ------------------------------------------------------------------ limits & trend
    def draw_trend(self, c, t):
        al = self.vis(t, "limits", "monitor", fi=0.6, fo=0.5, a_off=0.2, b_off=-0.4)
        if al > 0:
            draw_text(c, "Operating limits below MAASP", 120, 220, 48, C.text, 600, al, display=True)
            x, y0, y1 = 760, 300, 960
            zones = [(0, 0.62, C.green, "Normal operating range"), (0.62, 0.82, C.yellow, "Alarm and action levels"), (0.82, 1.0, C.red, "Approaching MAASP")]
            for i, (f0, f1, col, lab) in enumerate(zones):
                k = ease_out(clamp((t - self.c0("limits") - 0.3 - i * 0.6) / 0.6)) * al
                ya, yb = y1 - f1 * (y1 - y0), y1 - f0 * (y1 - y0)
                c.drawRect(skia.Rect(x, ya, x + 120, yb), paint(col, 0.75 * k))
                draw_text(c, lab, x + 150, (ya + yb) / 2 + 10, 30, C.text, 500, k)
            c.drawLine(x - 30, y0, x + 150, y0, paint(C.amber, al, stroke=4))
            draw_text(c, "MAASP", x - 40, y0 + 10, 28, C.amber, 700, al, "right")
            val = 0.35 + 0.05 * math.sin(t * 1.3)
            c.drawPath(poly([(x - 20, y1 - val * (y1 - y0) - 12), (x, y1 - val * (y1 - y0)), (x - 20, y1 - val * (y1 - y0) + 12)], close=True), paint(C.white, al))
        am = self.vis(t, "monitor", "gullfaks", fi=0.6, fo=0.6, b_off=-0.4)
        if am > 0:
            draw_text(c, "A-annulus pressure trend", 120, 220, 48, C.text, 600, am, display=True)
            pl = Plot(220, 320, 1100, 560, (0, 360), (0, 240), xlabel="Days in operation", ylabel="Pressure (bar)",
                      xticks=[0, 60, 120, 180, 240, 300, 360], yticks=[0, 60, 120, 180, 240])
            pl.axes(c, am)
            xs = np.linspace(0, 360, 720)
            ys = []
            for d in xs:
                if d < 6:
                    p = 18 + 85 * (d / 6)              # thermal rise on start-up
                elif d < 7:
                    p = 103 - 70 * (d - 6)             # bleed-off
                elif d < 200:
                    p = 33 + 4 * math.sin(d * 0.5)     # stable, thermal
                else:
                    cyc = (d - 200) % 40               # tubing-to-annulus communication
                    p = 30 + 135 * (1 - math.exp(-cyc / 9))
                ys.append(p)
            f1 = clamp((t - self.c0("monitor") - 0.3) / 7.0) * (200 / 360)
            f2 = clamp((t - self.c0("buildup") - 0.2) / 7.0) * (160 / 360)
            pl.line(c, xs, ys, COL_A, 3, am, reveal=f1 + f2)
            # tubing pressure reference
            pl.line(c, [0, 360], [180, 180], C.oil, 2, am * 0.8, glow=False, dash=[10, 8])
            draw_text(c, "tubing pressure", pl.px(10), pl.py(180) - 12, 20, C.oil, 600, am)
            k1 = ease_out(clamp((t - self.c0("monitor") - 2.0) / 0.6)) * am
            draw_text(c, "start-up: thermal rise, bled down", pl.px(12), pl.py(115), 20, C.text, 500, k1)
            draw_text(c, "stable: thermal behaviour", pl.px(70), pl.py(55), 20, C.green, 600, ease_out(clamp((t - self.c0("monitor") - 5) / 0.6)) * am)
            if f2 > 0.05:
                k2 = ease_out(clamp((t - self.c0("buildup") - 3) / 0.6)) * am
                draw_text(c, "builds back toward tubing pressure after every bleed-off", pl.px(205), pl.py(215), 20, C.red, 600, k2)
                draw_text(c, "gas returned", pl.px(260), pl.py(20), 20, C.gas, 600, k2)
            # status
            ka = ease_out(clamp((t - self.c0("action")) / 0.6)) * am
            status = "GREEN" if ka < 0.5 else "ORANGE"
            col = mix(C.green, C.orange, ka)
            draw_panel(c, 1420, 320, 400, 560, am, r=18)
            draw_text(c, "WELL STATUS", 1450, 370, 20, C.muted, 700, am, tracking=4)
            c.drawCircle(1500, 450, 26, paint(col, am))
            c.drawCircle(1500, 450, 40, paint(col, 0.3 * am, blur=10))
            draw_text(c, status, 1545, 462, 36, col, 800, am, display=True)
            acts = ["Reclassified: one barrier failed", "Risk-reducing measures", "Repair planned"]
            for i, txt in enumerate(acts):
                kk = ease_out(clamp((t - self.c0("action") - 0.5 - i * 1.4) / 0.5)) * am
                draw_paragraph(c, "→ " + txt, 1450, 560 + i * 90, 340, 26, C.text, 500, kk)

    def draw_gullfaks(self, c, t):
        a = self.vis(t, "gullfaks", None, fi=0.7, fo=0.6, b_off=3)
        if a <= 0:
            return
        draw_text(c, "CASE · GULLFAKS C · 2010", 120, 210, 22, C.red, 700, a, tracking=4)
        draw_text(c, "Weeks of warning in the C-annulus", 120, 270, 48, C.text, 600, a, display=True)
        pl = Plot(220, 380, 1000, 480, (0, 60), (0, 100), xlabel="Days", ylabel="C-annulus pressure", xticks=[0, 10, 20, 30, 40, 50, 60],
                  yticks=[])
        pl.axes(c, a)
        xs = np.linspace(0, 60, 240)
        ys = [10 + (0 if x < 15 else 1.6 * (x - 15)) + 2 * math.sin(x * 2) for x in xs]
        f = clamp((t - self.c0("gullfaks") - 0.5) / 7.0)
        pl.line(c, xs, ys, C.red, 3.5, a, reveal=f)
        if f > 0.4:
            k = ease_out(clamp((f - 0.4) * 3)) * a
            draw_text(c, "rising for weeks, not noticed", pl.px(28), pl.py(30), 24, C.red, 600, k)
        kk = ease_out(clamp((t - self.word_time("gullfaks", "hole in the casing")) / 0.6)) * a
        if kk > 0:
            draw_panel(c, 1300, 380, 520, 420, kk, glow=C.red, r=18)
            icon(c, "warning", 1360, 450, 60, C.text, kk, C.red)
            draw_paragraph(c, "A hole in the casing led to a serious well control incident.", 1330, 540, 460, 30, C.text, 600, kk)
            draw_paragraph(c, "Investigations: insufficient technical integrity of the casing and inadequate monitoring of the "
                           "C-annulus pressure.", 1330, 650, 460, 22, C.muted, 400, kk)
