"""Chapter 9: A new chapter - CO2 storage."""
from __future__ import annotations

import math

import numpy as np
import skia

from engine.core import (C, W, H, arrow, chip, clamp, draw_panel, draw_paragraph, draw_text, ease_in_out, ease_out,
                         ease_out_back, glow_path, lerp, mix, paint, poly, rgb, trim_path, window, with_alpha, rrect,
                         image_shader, path_point)
from engine.scene import Scene
from engine.widgets import icon, bullets, Plot, stamp
from engine.well import steel_paint, cement_texture, lith_texture, LITH_COLORS
from engine.ncsmap import MapView, draw_map, FIELDS


class SceneImpl(Scene):
    id = "s09_ccs"

    def setup(self):
        self.mv = MapView(90, 170, 900, 830, 1.8, 6.4, 59.6, 61.3)
        rnd = np.random.default_rng(31)
        self.parts = [(rnd.uniform(0, 1), rnd.uniform(-1, 1), rnd.uniform(1.5, 3.5)) for _ in range(80)]

    def draw(self, c, t):
        self.draw_northern(c, t)
        self.draw_chem(c, t)
        self.draw_cycles(c, t)
        self.draw_legacy(c, t)
        self.draw_sintef(c, t)

    def draw_northern(self, c, t):
        a = self.vis(t, "northern", "co2", fi=0.8, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        draw_map(c, self.mv, a, fields=["Troll", "Oseberg", "Aurora", "Øygarden"], hot=("Aurora",), t=t)
        x0, y0 = self.mv.p(*FIELDS["Øygarden"])
        x1, y1 = self.mv.p(*FIELDS["Aurora"])
        pipe = poly([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 + 20), (x1, y1)])
        kp = ease_in_out(clamp((t - self.c0("northern") - 1.5) / 2.5))
        glow_path(c, trim_path(pipe, 0, kp), C.co2, 4, a, glow=8)
        if kp > 0.99:
            for k in range(8):
                q = ((t * 0.18 + k / 8) % 1.0)
                (px, py), _ = path_point(pipe, q)
                c.drawCircle(px, py, 5, paint(C.white, 0.9 * a))
        draw_text(c, "pipeline ≈ 100 km", (x0 + x1) / 2 + 30, (y0 + y1) / 2 - 30, 20, C.co2, 600, a * kp, "center", shadow=True)
        # ship arriving at terminal
        ks = ease_out(clamp((t - self.c0("northern") - 0.5) / 3.0))
        icon(c, "ship", x0 - 70 - 90 * (1 - ks), y0 - 70 - 60 * (1 - ks), 54, C.text, a * ks, C.co2)
        # right: facts and injection well section
        draw_text(c, "NORTHERN LIGHTS", 1060, 220, 22, C.co2, 700, a, tracking=5)
        draw_text(c, "First CO₂ injected · August 2025", 1060, 280, 44, C.text, 600, a, display=True)
        # section: seabed, overburden, caprock, Aurora reservoir with plume
        X0, X1, top = 1060, 1840, 330
        sb = top + 30
        layers = [(sb, sb + 200, "claystone"), (sb + 200, sb + 270, "caprock"), (sb + 270, sb + 390, "sand"), (sb + 390, sb + 450, "shale")]
        c.save()
        c.clipRect(skia.Rect(X0, top, X1, sb + 450))
        c.drawRect(skia.Rect(X0, top, X1, sb), paint(rgb("#0E3550"), a))
        for (y0_, y1_, lith) in layers:
            p = skia.Paint(Shader=image_shader(lith_texture(lith), 0.6))
            p.setAlphaf(a)
            c.drawRect(skia.Rect(X0, y0_, X1, y1_), p)
        draw_text(c, "cap rock", X1 - 12, sb + 245, 20, C.text, 600, a, "right", shadow=True)
        draw_text(c, "storage reservoir", X1 - 12, sb + 340, 20, C.text, 600, a, "right", shadow=True)
        wx = 1300
        c.drawLine(wx, sb - 10, wx, sb + 345, paint(C.steel_hi, a, stroke=6))
        kpl = ease_out(clamp((t - self.c0("northern") - 4.0) / 8.0))
        plume = skia.Path()
        plume.addOval(skia.Rect(wx - 230 * kpl, sb + 275, wx + 300 * kpl, sb + 275 + 60 * max(kpl, 0.05)))
        c.drawPath(plume, paint(C.co2, 0.45 * a))
        c.drawPath(plume, paint(C.co2, 0.8 * a, stroke=1.5))
        c.drawLine(X0 + 20, sb, X0 + 20, sb + 300, paint(C.muted, 0.6 * a, stroke=1.5))
        draw_text(c, "≈ 2.5 km", X0 + 30, sb + 160, 20, C.text, 600, a, shadow=True)
        c.restore()
        facts = [("Equinor, Shell and TotalEnergies", self.c0("northern") + 1.0), ("1.5 Mt/yr, expanding to at least 5 Mt/yr", self.c0("northern") + 2.5),
                 ("CO₂ stored offshore since 1996: Sleipner, then Snøhvit", self.word_time("northern", "since 1996") - 0.3)]
        for i, (txt, ti) in enumerate(facts):
            kk = ease_out(clamp((t - ti) / 0.6)) * a
            c.drawCircle(1072, 990 - (2 - i) * 46 - 8, 6, paint(C.co2, kk))
            draw_text(c, txt, 1090, 990 - (2 - i) * 46, 24, C.text, 500, kk)

    def draw_chem(self, c, t):
        a = self.vis(t, "co2", "cycles", fi=0.7, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        draw_text(c, "CO₂ changes the load case", 120, 250, 50, C.text, 600, a, display=True)
        k = ease_out(clamp((t - self.c0("co2") - 0.5) / 1.0))
        eq = "CO₂  +  H₂O   →   H₂CO₃"
        draw_text(c, eq, 120, 380, 60, C.co2, 700, a * k, display=True)
        draw_text(c, "carbonic acid", 760, 430, 24, C.muted, 600, a * k)
        # casing wall corroding & cement carbonating
        x, y = 260, 520
        kc = ease_in_out(clamp((t - self.word_time("co2", "attacks") + 0.2) / 6.0))
        c.drawRect(skia.Rect(x, y, x + 120, y + 420), paint(rgb("#3E6E8E"), 0.7 * a))
        draw_text(c, "CO₂ + water", x + 60, y + 460, 20, C.muted, 600, a, "center")
        sp = steel_paint(x + 120, x + 170, a)
        c.drawRect(skia.Rect(x + 120, y, x + 170, y + 420), sp)
        rnd = np.random.default_rng(2)
        for _ in range(int(40 * kc)):
            yy = rnd.uniform(y, y + 420)
            c.drawOval(skia.Rect(x + 116, yy, x + 128 + rnd.uniform(0, 14 * kc), yy + rnd.uniform(4, 12)), paint(rgb("#8B4513"), 0.9 * a))
        draw_text(c, "steel", x + 145, y - 14, 20, C.muted, 600, a, "center")
        cp = skia.Paint(Shader=image_shader(cement_texture(), 0.5))
        cp.setAlphaf(a)
        c.drawRect(skia.Rect(x + 170, y, x + 370, y + 420), cp)
        fp = skia.Paint(Shader=image_shader(lith_texture("sand"), 0.5))
        fp.setAlphaf(a)
        c.drawRect(skia.Rect(x + 370, y, x + 470, y + 420), fp)
        c.drawRect(skia.Rect(x + 370, y, x + 470, y + 420), paint(C.co2, 0.25 * a))
        draw_text(c, "formation", x + 420, y - 14, 20, C.muted, 600, a, "center")
        draw_text(c, "CO₂-rich brine", x + 420, y + 460, 20, C.muted, 600, a, "center")
        c.drawRect(skia.Rect(x + 370 - 110 * kc, y, x + 370, y + 420), paint(rgb("#C96F3A"), 0.35 * a))
        draw_text(c, "cement", x + 270, y - 14, 20, C.muted, 600, a, "center")
        if kc > 0.2:
            ka = a * clamp((kc - 0.2) / 0.2)
            fx = x + 370 - 110 * kc
            c.drawLine(fx, y + 203, x + 482, y + 203, paint(rgb("#E2925E"), ka, stroke=1.5))
            c.drawCircle(fx, y + 203, 4, paint(rgb("#E2925E"), ka))
            draw_text(c, "carbonation front", x + 490, y + 210, 22, rgb("#E2925E"), 700, ka)
        # impurities and remedies
        ai = self.vis(t, "impurities", "cycles", fi=0.6, fo=0.5, b_off=-0.5)
        if ai > 0:
            draw_panel(c, 1000, 320, 820, 620, ai, r=20, glow=C.co2)
            draw_text(c, "IMPURITIES", 1040, 380, 20, C.co2, 700, ai, tracking=4)
            imps = [("Water", "water"), ("Oxygen", "oxygen"), ("Sulfur compounds", "sulfur")]
            for i, (nm, kw) in enumerate(imps):
                kk = ease_out(clamp((t - self.word_time("impurities", kw) + 0.2) / 0.5)) * ai
                chip(c, 1040 + i * 250, 410, nm, C.amber, kk, size=24)
            draw_paragraph(c, "can make the stream even more aggressive", 1040, 520, 740, 28, C.muted, 400,
                           ai * ease_out(clamp((t - self.word_time("impurities", "aggressive")) / 0.5)))
            draw_text(c, "WHERE IT MATTERS", 1040, 640, 20, C.green, 700, ai, tracking=4)
            rem = ["Corrosion resistant alloys", "CO₂-resistant cement systems"]
            times = [self.word_time("impurities", "corrosion resistant") - 0.3, self.word_time("impurities", "cement systems") - 0.3]
            bullets(c, rem, 1040, 700, t, times, size=32, max_w=740, alpha=ai, accent=C.green, gap=1.8)

    def draw_cycles(self, c, t):
        a = self.vis(t, "cycles", "legacy", fi=0.7, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        draw_text(c, "Intermittent injection: thermal and pressure cycles", 120, 250, 46, C.text, 600, a, display=True)
        pl = Plot(220, 360, 860, 420, (0, 40), (0, 100), xlabel="Time", ylabel="Wellbore temperature", xticks=[], yticks=[])
        pl.axes(c, a)
        xs = np.linspace(0, 40, 400)
        ys = [55 + 35 * (1 if (x % 10) < 5 else -1) * (1 - math.exp(-((x % 5)) / 1.0)) * 0.9 for x in xs]
        f = clamp((t - self.c0("cycles")) / 6.0)
        pl.line(c, xs, ys, C.co2, 3, a, reveal=f)
        draw_text(c, "injection on", pl.px(2), pl.py(10), 18, C.muted, 600, a)
        draw_text(c, "off", pl.px(7.5), pl.py(95), 18, C.muted, 600, a)
        # micro-annulus opening
        x, y = 1240, 360
        gap = 1 + 10 * f + 2 * math.sin(t * 4) * f
        cp = skia.Paint(Shader=image_shader(cement_texture(), 0.5))
        cp.setAlphaf(a)
        c.drawRect(skia.Rect(x, y, x + 80, y + 440), steel_paint(x, x + 80, a))
        c.drawRect(skia.Rect(x + 80 + gap, y, x + 320, y + 440), cp)
        c.drawRect(skia.Rect(x + 80, y, x + 80 + gap, y + 440), paint(C.gas, 0.8 * a * f))
        draw_text(c, "casing", x + 40, y - 14, 20, C.muted, 600, a, "center")
        draw_text(c, "cement", x + 200, y - 14, 20, C.muted, 600, a, "center")
        draw_text(c, "micro-annulus opens", x + 90, y + 480, 26, C.gas, 700, a * f)

    def draw_legacy(self, c, t):
        a = self.vis(t, "legacy", "sintef", fi=0.7, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        draw_text(c, "Every old well in the storage complex", 120, 250, 50, C.text, 600, a, display=True)
        X0, X1, top = 120, 1800, 330
        layers = [(top, top + 300, "claystone"), (top + 300, top + 420, "caprock"), (top + 420, top + 600, "sand"), (top + 600, top + 700, "shale")]
        for (y0_, y1_, lith) in layers:
            p = skia.Paint(Shader=image_shader(lith_texture(lith), 0.6))
            p.setAlphaf(a)
            c.drawRect(skia.Rect(X0, y0_, X1, y1_), p)
        k = ease_out(clamp((t - self.c0("legacy")) / 6.0))
        inj = 900
        c.drawLine(inj, top - 20, inj, top + 560, paint(C.steel_hi, a, stroke=6))
        plume = skia.Path()
        plume.addOval(skia.Rect(inj - 600 * k, top + 425, inj + 700 * k, top + 425 + 120 * max(k, 0.05)))
        c.drawPath(plume, paint(C.co2, 0.45 * a))
        draw_text(c, "injector", inj, top - 30, 20, C.co2, 700, a, "center")
        for i, xw in enumerate((420, 1450)):
            c.drawLine(xw, top - 20, xw, top + 650, paint(C.steel, 0.9 * a, stroke=5))
            cp = skia.Paint(Shader=image_shader(cement_texture(), 0.5))
            cp.setAlphaf(a)
            c.drawRect(skia.Rect(xw - 8, top + 330, xw + 8, top + 400), cp)
            reached = k > (0.55 if i == 0 else 0.65)
            draw_text(c, "legacy well (plugged)", xw, top - 30, 20, C.text, 600, a, "center")
            if reached:
                pr = (t * 0.9) % 1.0
                c.drawCircle(xw, top + 410, 16 + 26 * pr, paint(C.amber, a * (1 - pr), stroke=2.5))
                if i == 0:
                    draw_text(c, "potential leak path?", xw + 30, top + 370, 22, C.amber, 700, a)
                else:
                    draw_text(c, "potential leak path?", xw - 30, top + 370, 22, C.amber, 700, a, "right")
        draw_text(c, "cap rock", X1 - 12, top + 370, 22, C.text, 600, a, "right", shadow=True)
        draw_text(c, "storage formation", X1 - 12, top + 520, 22, C.text, 600, a, "right", shadow=True)

    def mini_well(self, c, cx, top, bot, fluid, a, label):
        """Telescoping casing scheme in a small formation panel."""
        X0, X1 = cx - 150, cx + 150
        rz = bot - 90
        for (y0_, y1_, lith) in ((top, rz - 60, "claystone"), (rz - 60, rz, "caprock"), (rz, bot, "sand")):
            p = skia.Paint(Shader=image_shader(lith_texture(lith), 0.45))
            p.setAlphaf(a)
            c.drawRect(skia.Rect(X0, y0_, X1, y1_), p)
        c.drawRect(skia.Rect(X0, rz + 8, X1, bot - 8), paint(fluid, 0.35 * a))
        cp = skia.Paint(Shader=image_shader(cement_texture(), 0.4))
        cp.setAlphaf(a)
        strings = [(64, 0.30), (48, 0.62), (34, 0.97)]
        H_ = bot - top
        for (hw, shoe) in strings:
            ys = top + shoe * H_
            for sd in (-1, 1):
                c.drawRect(skia.Rect(min(cx + sd * hw, cx + sd * (hw + 10)), ys - 0.22 * H_, max(cx + sd * hw, cx + sd * (hw + 10)), ys), cp)
        for (hw, shoe) in strings:
            ys = top + shoe * H_
            for sd in (-1, 1):
                r = skia.Rect(min(cx + sd * hw, cx + sd * (hw - 5)), top, max(cx + sd * hw, cx + sd * (hw - 5)), ys)
                c.drawRect(r, steel_paint(r.left(), r.right(), a))
        c.drawRect(skia.Rect(cx - 10, top, cx + 10, rz - 20), paint(fluid, 0.85 * a))
        c.drawRect(skia.Rect(cx - 13, top, cx - 10, rz - 20), paint(C.steel_hi, a))
        c.drawRect(skia.Rect(cx + 10, top, cx + 13, rz - 20), paint(C.steel_hi, a))
        c.drawRect(skia.Rect(cx - 36, rz - 70, cx + 36, rz - 52), paint(C.steel, a))
        c.drawRect(skia.Rect(X0, top, X1, bot), paint(C.line, a, stroke=1.5))
        draw_text(c, label, cx, bot + 44, 26, C.text, 600, a, "center")

    def draw_sintef(self, c, t):
        a = self.vis(t, "sintef", self.dur, fi=0.7, fo=0.6)
        if a <= 0:
            return
        draw_text(c, "SINTEF FOR STANDARDS NORWAY · 2024", 120, 200, 22, C.co2, 700, a, tracking=4)
        draw_text(c, "CCS well design requirements", 120, 270, 52, C.text, 600, a, display=True)
        k1 = ease_out(clamp((t - self.word_time("sintef", "built much like") + 0.3) / 0.8)) * a
        if k1 > 0:
            self.mini_well(c, 290, 360, 860, C.oil, k1, "Petroleum well")
            self.mini_well(c, 690, 360, 860, C.co2, k1, "CO\u2082 well")
            draw_text(c, "\u2248", 490, 640, 72, C.muted, 300, k1, "center")
            draw_text(c, "Built much like petroleum wells", 490, 975, 28, C.co2, 600, k1, "center")
        cards = [("the fluid", "drop", "The fluid", "CO\u2082 with water forms acid; impurities add to it"),
                 ("the load pattern", "wave", "The load pattern", "Cold injection and start-stop cycles"),
                 ("the longer lifetime", "infinity", "The lifetime", "Containment for far longer than a producing well")]
        for i, (kw, ic, h1, body) in enumerate(cards):
            kk = ease_out_back(clamp((t - self.word_time("sintef", kw) + 0.2) / 0.6)) * a
            if kk <= 0:
                continue
            y = 340 + i * 175
            draw_panel(c, 1000, y, 800, 150, kk, r=18, glow=C.co2)
            icon(c, ic, 1075, y + 75, 64, C.text, kk, C.co2)
            draw_text(c, h1, 1140, y + 64, 34, C.text, 600, kk, display=True)
            draw_text(c, body, 1140, y + 106, 24, C.muted, 400, kk)
        kd = ease_out(clamp((t - self.word_time("sintef", "different risk") + 0.2) / 0.6)) * a
        if kd > 0:
            draw_text(c, "\u2192  a different risk picture", 1000, 900, 30, C.amber, 700, kd)
        kr = ease_out(clamp((t - self.word_time("sintef", "revision") + 0.2) / 0.7)) * a
        if kr > 0:
            chip(c, 1000, 975, "To be addressed in the revision of NORSOK D-010", C.co2, kr, size=24)
