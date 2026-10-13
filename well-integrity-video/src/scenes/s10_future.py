"""Chapter 10: Digital well integrity and key lessons."""
from __future__ import annotations

import math

import numpy as np
import skia

from engine.core import (C, W, H, arrow, chip, dashed, clamp, draw_panel, draw_paragraph, draw_text, ease_in_out, ease_out,
                         ease_out_back, glow_path, lerp, mix, paint, poly, rgb, trim_path, window, with_alpha, rrect)
from engine.scene import Scene
from engine.widgets import icon, bullets, Plot, stamp
from engine.well import WellView, WellState, draw_formation, draw_well, draw_surface, highlight


class SceneImpl(Scene):
    id = "s10_future"

    def setup(self):
        rnd = np.random.default_rng(8)
        self.tiles = []
        for i in range(24):
            cat = rnd.choice(["g"] * 16 + ["y"] * 5 + ["o"] * 2 + ["r"] * 1)
            series = np.cumsum(rnd.normal(0, 1, 40)) * 0.6 + 20 + 5 * np.sin(np.linspace(0, 6, 40))
            self.tiles.append((cat, series, rnd.uniform(0, 6)))
        self.anom = 9

    def draw(self, c, t):
        self.draw_dashboard(c, t)
        self.draw_twin(c, t)
        self.draw_wims(c, t)
        self.draw_caution(c, t)
        self.draw_lessons(c, t)
        self.draw_close(c, t)

    def draw_dashboard(self, c, t):
        a = self.vis(t, "digital", "twin", fi=0.8, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        draw_text(c, "Well integrity is becoming digital", 120, 230, 50, C.text, 600, a, display=True)
        cols = {"g": C.green, "y": C.yellow, "o": C.orange, "r": C.red}
        tw, th = 270, 150
        for i, (cat, series, ph) in enumerate(self.tiles):
            r, k_ = divmod(i, 6)
            x = 120 + k_ * (tw + 18)
            y = 300 + r * (th + 18)
            ki = ease_out(clamp((t - self.c0("digital") - 0.3 - i * 0.04) / 0.5)) * a
            if ki <= 0:
                continue
            anomaly = i == self.anom
            ka = ease_out(clamp((t - self.word_time("digital", "automated analysis") + 0.2) / 0.8)) if anomaly else 0.0
            col = cols[cat] if not anomaly else mix(C.green, C.orange, ka)
            draw_panel(c, x, y, tw, th, ki, r=12, border=mix(C.line, col, 0.6))
            c.drawCircle(x + 22, y + 26, 7, paint(col, ki))
            draw_text(c, f"Well {['A', 'B', 'C', 'D'][r]}-{k_ + 1:02d}", x + 38, y + 33, 20, C.text, 600, ki)
            # sparkline (A-annulus pressure)
            n = len(series)
            vis_n = max(2, int(n * clamp((t - self.c0("digital") - 0.5) / 4.0)))
            vals = list(series[:vis_n])
            if anomaly and ka > 0:
                vals = [v + (max(0, j - 26) ** 1.6) * 0.5 * ka for j, v in enumerate(vals)]
            pts = [(x + 18 + j * (tw - 36) / (n - 1), y + th - 22 - (v - 10) * 2.2) for j, v in enumerate(vals)]
            c.drawPath(poly(pts), paint(col, ki, stroke=2))
            if anomaly and ka > 0:
                pr = (t * 0.9) % 1.0
                c.drawRoundRect(skia.Rect(x - 6 - 8 * pr, y - 6 - 8 * pr, x + tw + 6 + 8 * pr, y + th + 6 + 8 * pr), 16, 16, paint(C.orange, a * ka * (1 - pr), stroke=2.5))
        kk = ease_out(clamp((t - self.word_time("digital", "automated analysis") + 0.6) / 0.6)) * a
        chip(c, 120, 990, "Automated analysis flags abnormal annulus build-up", C.orange, kk, size=24)

    def draw_twin(self, c, t):
        a = self.vis(t, "twin", "wims", fi=0.7, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        v = WellView(axis_x=560, y_top=420, y_bot=1030, sx=7.0, x_left=200, x_right=920)
        st = WellState()
        st.completion = 1
        st.a_annulus_fluid = C.brine
        st.perforations = 1
        st.bore_fluid = C.oil
        c.save()
        c.clipRect(skia.Rect(180, 100, 940, 1045))
        draw_formation(c, v, alpha=a)
        draw_well(c, v, st, t, a)
        draw_surface(c, v, st, a)
        c.restore()
        draw_text(c, "Digital barrier schematic", 1000, 230, 50, C.text, 600, a, display=True)
        rows = [("DHSV", "Inflow test", "passed · 12 days ago", C.green, "dhsv"), ("Production packer", "A-annulus trend", "stable", C.green, "packer"),
                ("Tubing", "Pressure test", "passed · 2 years ago", C.green, "tubing"), ("Wellhead", "Seal test", "passed · 6 months ago", C.green, "wellhead"),
                ("Master valve", "Leak test", "due in 5 days", C.yellow, "lmv")]
        for i, (el, test, res, col, key) in enumerate(rows):
            kk = ease_out(clamp((t - self.c0("twin") - 0.3 - i * 0.5) / 0.5)) * a
            y = 320 + i * 120
            draw_panel(c, 1000, y, 820, 100, kk, r=14)
            c.drawCircle(1040, y + 50, 10, paint(col, kk))
            draw_text(c, el, 1070, y + 44, 28, C.text, 600, kk)
            draw_text(c, f"{test}: {res}", 1070, y + 78, 21, C.muted, 400, kk)
            highlight(c, v, key, col, kk * 0.8, fill=0.35)

    def draw_wims(self, c, t):
        a = self.vis(t, "wims", "caution", fi=0.7, fo=0.6, b_off=0.7)
        if a <= 0:
            return
        cx, cy = W / 2, 600
        c.drawCircle(cx, cy, 150, paint(C.panel, a))
        c.drawCircle(cx, cy, 150, paint(C.primary, a, stroke=2.5))
        draw_text(c, "Well integrity", cx, cy - 10, 32, C.text, 600, a, "center", display=True)
        draw_text(c, "management system", cx, cy + 30, 26, C.muted, 500, a, "center")
        items = [("Register of wells and elements", "register", "doc"), ("Risk-based test intervals", "test intervals", "clock"),
                 ("Handling of deviations", "deviations", "warning"), ("Competence requirements", "competence", "people"),
                 ("Regular audits", "audits", "magnifier")]
        R = 360
        for i, (txt, kw, ic) in enumerate(items):
            ang = -math.pi / 2 + i * 2 * math.pi / len(items)
            x, y = cx + R * 1.35 * math.cos(ang), cy + R * 0.95 * math.sin(ang)
            kk = ease_out_back(clamp((t - self.word_time("wims", kw) + 0.3) / 0.6)) * a
            if kk <= 0:
                continue
            c.drawLine(cx + 150 * math.cos(ang), cy + 150 * math.sin(ang), x, y, paint(C.line, kk, stroke=2))
            draw_panel(c, x - 200, y - 60, 400, 120, kk, r=16, glow=C.primary)
            icon(c, ic, x - 140, y, 56, C.text, kk, C.primary)
            draw_paragraph(c, txt, x - 95, y - 4, 280, 25, C.text, 600, kk)

    def draw_caution(self, c, t):
        a = self.vis(t, "caution", "lessons", fi=0.7, fo=0.6, a_off=1.2, b_off=-0.3)
        if a <= 0:
            return
        draw_text(c, "Only as good as calibration and interpretation", 120, 240, 46, C.text, 600, a, display=True)
        # the same interval logged twice: correctly calibrated vs miscalibrated
        x0, y0, h = 300, 330, 620
        gz0, gz1 = 0.45, 0.62
        kw = ease_out(clamp((t - self.word_time("caution", "still be wrong") + 0.2) / 0.8)) * a
        for j, (lab, col) in enumerate((("calibrated", C.green), ("miscalibrated", C.red))):
            x = x0 + j * 460
            draw_panel(c, x, y0, 380, h, a, r=12)
            draw_text(c, lab, x + 190, y0 - 14, 22, col, 700, a, "center")
            for g in range(1, 4):
                c.drawLine(x + 30 + g * 80, y0 + 16, x + 30 + g * 80, y0 + h - 16, paint(C.line, 0.5 * a, stroke=1))
            pth = skia.Path()
            for k in range(200):
                f = k / 199
                yy = y0 + 20 + f * (h - 40)
                gas = clamp((f - gz0) / 0.025) * clamp((gz1 - f) / 0.025)
                base = 0.30 + 0.07 * math.sin(k * 0.21) + 0.045 * math.sin(k * 0.57 + 1.3) + 0.03 * math.sin(k * 1.37 + 2.1)
                v = base + 0.42 * gas * (1.0 if j == 0 else 0.1)
                xx = x + 30 + v * 300
                (pth.moveTo if k == 0 else pth.lineTo)(xx, yy)
            reveal = clamp((t - self.c0("caution") - 1.0) / 3.0)
            c.drawPath(trim_path(pth, 0, reveal), paint(col, a, stroke=3))
            ya, yb = y0 + 20 + gz0 * (h - 40), y0 + 20 + gz1 * (h - 40)
            if j == 0:
                kg = a * clamp((reveal - gz1) / 0.1)
                c.drawRect(skia.Rect(x + 10, ya, x + 370, yb), paint(C.gas, 0.12 * kg))
                draw_text(c, "gas", x + 350, (ya + yb) / 2 + 8, 22, C.gas, 700, kg, "right")
            elif kw > 0:
                rp = skia.Path()
                rp.addRect(skia.Rect(x + 10, ya, x + 370, yb))
                dashed(c, rp, C.gas, 2, 10, 8, alpha=0.8 * kw)
                draw_text(c, "gas present,", x + 360, (ya + yb) / 2 - 4, 22, C.gas, 700, kw, "right")
                draw_text(c, "not seen", x + 360, (ya + yb) / 2 + 24, 22, C.gas, 700, kw, "right")
        draw_paragraph(c, "A log can look convincing, and still be wrong.", 1280, 520, 520, 40, C.text, 600, a, display=True)
        draw_text(c, "Troll, 2025", 1280, 700, 24, C.muted, 500, a)

    def draw_lessons(self, c, t):
        a = self.vis(t, "lessons", "close", fi=0.6, fo=0.7, b_off=-0.3)
        if a <= 0:
            return
        draw_text(c, "KEY LESSONS", 160, 180, 22, C.primary, 700, a, tracking=6)
        items = [("Two independent, tested barriers", "Know your envelopes, and draw them", "l1", "shield"),
                 ("Verify", "A barrier that is not verified is an assumption", "l2", "check"),
                 ("Respect the limits", "Know the MAASP of every annulus; watch the trends", "l3", "gauge"),
                 ("Classify honestly", "Act on degradation before yellow becomes red", "l4", "chart"),
                 ("Plug for eternity", "Rock to rock, qualified materials, verified in place", "l5", "infinity"),
                 ("People and planning", "Most failures begin long before steel or cement gives way", "l6", "people")]
        for i, (h1, h2, cue, ic) in enumerate(items):
            r, k_ = divmod(i, 2)
            x = 160 + k_ * 820
            y = 240 + r * 250
            kk = ease_out(clamp((t - self.c0(cue) + 0.2) / 0.6)) * a
            hot = window(t, self.c0(cue), self.c1(cue), 0.3, 0.6)
            if kk <= 0:
                continue
            draw_panel(c, x, y, 780, 220, kk, r=20, glow=C.primary if hot > 0.3 else None, border=mix(C.line, C.primary, hot))
            draw_text(c, f"{i + 1}", x + 60, y + 140, 96, C.primary, 200, kk, "center", display=True)
            draw_text(c, h1, x + 130, y + 95, 38, C.text, 600, kk, display=True)
            draw_paragraph(c, h2, x + 130, y + 145, 560, 26, C.muted, 400, kk)

    def draw_close(self, c, t):
        a = self.vis(t, "close", self.dur, fi=1.2, fo=0.8)
        if a <= 0:
            return
        k = ease_in_out(clamp((t - self.c0("close")) / 3.0))
        # an envelope that closes
        cx, cy = W / 2, 420
        pth = poly([(cx - 80, cy + 120), (cx - 80, cy - 60), (cx + 80, cy - 60), (cx + 80, cy + 120)])
        glow_path(c, trim_path(pth, 0, k), C.primary, 5, a, glow=16)
        c.drawOval(skia.Rect(cx - 60, cy + 100, cx + 60, cy + 140), paint(C.amber, 0.7 * a))
        draw_paragraph(c, "A well is a promise to the future:", 360, 700, 1200, 54, C.text, 600, a, align="center", display=True,
                       reveal=clamp((t - self.c0("close")) / 2.0))
        draw_paragraph(c, "that what we opened, we can keep closed.", 360, 780, 1200, 54, C.primary_hi, 600, a, align="center",
                       display=True, reveal=clamp((t - self.c0("close") - 1.6) / 2.0))
