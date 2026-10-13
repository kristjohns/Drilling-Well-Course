"""Chapter 4: Verification and testing."""
from __future__ import annotations

import math

import numpy as np
import skia

from engine.core import (C, W, H, arrow, chip, clamp, draw_panel, draw_paragraph, draw_text, ease_in_out, ease_out,
                         ease_out_back, glow_path, lerp, mix, paint, poly, rgb, trim_path, window, with_alpha, rrect,
                         image_shader, font)
from engine.scene import Scene
from engine.widgets import icon, bullets, Plot, gauge, stamp
from engine.well import steel_paint, cement_texture, lith_texture, WellView, WellState, draw_bop


def test_curve(tmin, mode="pass"):
    """Pressure (bar) vs time (min) for a low + high pressure test."""
    p = []
    for x in tmin:
        if x < 1.0:
            v = 18 * x
        elif x < 6.0:
            v = 18 - 0.3 * (x - 1.0) / 5.0
        elif x < 7.0:
            v = 17.7 * (1 - (x - 6.0))
        elif x < 9.0:
            v = 345 * (x - 7.0) / 2.0
        else:
            dt = x - 9.0
            if mode == "pass":
                v = 345 - 8 * (1 - math.exp(-dt / 1.6))
            else:
                v = 345 - 9 * dt
        p.append(max(0.0, v))
    return p


class SceneImpl(Scene):
    id = "s04_verify"

    def setup(self):
        rnd = np.random.default_rng(3)
        self.drips = [(rnd.uniform(-1, 1), rnd.uniform(0, 1)) for _ in range(24)]
        self.tmin = np.linspace(0, 21, 300)

    def draw(self, c, t):
        self.draw_assume(c, t)
        self.draw_ptest(c, t)
        self.draw_inflow(c, t)
        self.draw_macondo(c, t)
        self.draw_valves(c, t)
        self.draw_bop(c, t)
        self.draw_cement(c, t)
        self.draw_cbl(c, t)
        self.draw_ultra(c, t)
        self.draw_lengths(c, t)
        self.draw_doc(c, t)

    # ------------------------------------------------------------------
    def draw_assume(self, c, t):
        a = self.vis(t, "assume", "ptest", fi=0.8, fo=0.6, b_off=-0.3)
        if a <= 0:
            return
        draw_text(c, "A barrier that has not been verified", W / 2, 420, 64, C.text, 600, a, "center", display=True)
        w1 = font(64, 600, True).measureText("is an ")
        w2 = font(64, 700, True).measureText("assumption")
        x0 = W / 2 - (w1 + w2) / 2
        draw_text(c, "is an ", x0, 520, 64, C.text, 600, a, display=True)
        kf = ease_in_out(clamp((t - self.word_time("assume", "verification") + 0.2) / 1.0))
        draw_text(c, "assumption.", x0 + w1, 520, 64, C.amber, 700, a, display=True)
        if kf > 0:
            kv = ease_out(clamp((t - self.word_time("assume", "verification") - 0.4) / 0.8)) * a
            w3 = font(56, 600, True).measureText("Verification turns it into ")
            w4 = font(56, 700, True).measureText("a fact")
            x1 = W / 2 - (w3 + w4) / 2
            draw_text(c, "Verification turns it into ", x1, 660, 56, C.text, 600, kv, display=True)
            draw_text(c, "a fact", x1 + w3, 660, 56, C.green, 700, kv, display=True)
            kr = ease_out(clamp((t - self.word_time("assume", "recorded") + 0.2) / 0.8)) * a
            draw_text(c, "recorded for the life of the well", W / 2, 740, 32, C.muted, 400, kr, "center")

    # ------------------------------------------------------------------
    def test_rig(self, c, t, x, y, h, a, plug_kind="mech", leak=0.0, pressure=0.0, inflow=False):
        """Casing section with a plug, pressurised from above (or bled off for inflow)."""
        hw = 80
        for side in (-1, 1):
            xo = x + side * hw
            c.drawRect(skia.Rect(min(xo, xo + side * 14), y, max(xo, xo + side * 14), y + h), steel_paint(min(xo, xo + side * 14), max(xo, xo + side * 14), a))
        # fluid above the plug, intensity with pressure
        py = y + h * 0.68
        col = mix(rgb("#2D5F86"), rgb("#7FC4FF"), clamp(pressure))
        if inflow:
            col = mix(rgb("#2D5F86"), rgb("#9BB8C9"), clamp(pressure))
        c.drawRect(skia.Rect(x - hw, y, x + hw, py - 26), paint(col, 0.75 * a))
        # plug
        if plug_kind == "mech":
            c.drawRect(skia.Rect(x - hw, py - 26, x + hw, py + 26), paint(rgb("#2A2D33"), a))
            for k in range(5):
                c.drawLine(x - hw, py - 20 + k * 10, x + hw, py - 20 + k * 10, paint(C.steel_hi, 0.4 * a, stroke=1))
        else:
            cp = skia.Paint(Shader=image_shader(cement_texture(), 0.5))
            cp.setAlphaf(a)
            c.drawRect(skia.Rect(x - hw, py - 60, x + hw, py + 26), cp)
        # below the plug: formation pressure
        c.drawRect(skia.Rect(x - hw, py + 26, x + hw, y + h), paint(rgb("#6B4A22"), 0.65 * a))
        # surface connection + gauge line
        c.drawLine(x, y, x, y - 40, paint(C.steel_hi, a, stroke=6))
        c.drawLine(x, y - 40, x + 140, y - 40, paint(C.steel_hi, a, stroke=6))
        # pressure arrows
        if not inflow and pressure > 0.05:
            for k in range(3):
                xx = x - 50 + k * 50
                arrow(c, xx, py - 90, xx, py - 34, C.primary_hi, 3, a * clamp(pressure * 2), head=10)
        if inflow:
            for k in range(3):
                xx = x - 50 + k * 50
                arrow(c, xx, py + 70, xx, py + 32, C.amber, 3, a, head=10)
        # leak drips around the plug
        if leak > 0:
            for (u, v_) in self.drips:
                life = (v_ + t * 0.6) % 1.0
                xx = x + (hw - 6) * (1 if u > 0 else -1)
                yy = py - 26 + life * 70
                c.drawCircle(xx, yy, 3.5, paint(C.red, a * leak * (1 - life)))
        return py

    def draw_ptest(self, c, t):
        a = self.vis(t, "ptest", "inflow", fi=0.7, fo=0.6, b_off=-0.4)
        if a <= 0:
            return
        draw_text(c, "POSITIVE PRESSURE TEST", 120, 200, 20, C.primary, 700, a, tracking=4)
        draw_text(c, "Pressure applied, then held", 120, 256, 44, C.text, 600, a, display=True)
        # time mapping: chart progress over the ptest + stable cues
        tA, tB = self.c0("ptest") + 0.8, self.c1("stable") - 0.5
        f = clamp((t - tA) / (tB - tA))
        tm = 21 * f
        fail = ease_in_out(clamp((t - self.c0("fail") - 0.2) / 0.8))
        kf = ease_in_out(clamp((t - self.c0("fail")) / 3.0))
        p_pass = float(np.interp(tm, self.tmin, test_curve(self.tmin)))
        p_fail = float(np.interp(9.0 + 12.0 * kf, self.tmin, test_curve(self.tmin, "fail")))
        pg = lerp(p_pass, p_fail, fail)
        self.test_rig(c, t, 330, 400, 560, a, "mech", leak=fail, pressure=pg / 345)
        gauge(c, 560, 330, 56, pg, 0, 400, "", "bar", a, color=mix(C.primary, C.red, fail))
        # chart
        pl = Plot(820, 300, 960, 560, (0, 21), (0, 400), xlabel="Time (minutes)", ylabel="Pressure (bar)",
                  xticks=[0, 5, 10, 15, 20], yticks=[0, 100, 200, 300, 400])
        pl.axes(c, a)
        ys = test_curve(self.tmin)
        pl.line(c, self.tmin, ys, C.primary, 3.5, a * (1 - 0.6 * fail), reveal=f)
        # annotations
        if tm > 1.5:
            ka = a * clamp((tm - 1.5) / 1.0)
            c.drawRect(skia.Rect(pl.px(1), pl.py(40), pl.px(6), pl.py(0)), paint(C.teal, 0.12 * ka))
            draw_text(c, "Low test 15–20 bar", pl.px(1), pl.py(40) - 28, 20, C.teal, 600, ka)
            draw_text(c, "≥ 5 min stable", pl.px(1), pl.py(40) - 6, 18, C.muted, 500, ka)
        if tm > 11:
            ka = a * clamp((tm - 11) / 1.0)
            c.drawRect(skia.Rect(pl.px(11), pl.py(360), pl.px(21), pl.py(320)), paint(C.green, 0.12 * ka))
            draw_text(c, "Static test pressure observed ≥ 10 min · stable", pl.px(11), pl.py(360) - 14, 20, C.green, 600, ka)
        ks = ease_out(clamp((t - self.word_time("stable", "acceptable leak rate")) / 0.8))
        if ks > 0 and fail < 0.5:
            chip(c, 820, 940, "Acceptable leak rate: zero, unless the acceptance table says otherwise", C.green, a * ks * (1 - fail), size=22)
        if fail > 0:
            yf = test_curve(self.tmin, "fail")
            i9 = int(np.searchsorted(self.tmin, 9.0))
            pl.line(c, self.tmin[i9:], yf[i9:], C.red, 3.5, a * fail, reveal=kf)
            draw_text(c, "never flattens: leak", pl.px(11), pl.py(240), 24, C.red, 700, a * fail * clamp(kf * 2))
            stamp(c, 600, 820, "NOT ACCEPTED", C.red, ease_out(clamp((t - self.c0("fail") - 2.5) / 0.6)) * a, size=26)

    def draw_inflow(self, c, t):
        a = self.vis(t, "inflow", "macondo", fi=0.7, fo=0.6, b_off=-0.4)
        if a <= 0:
            return
        draw_text(c, "INFLOW (NEGATIVE) TEST", 120, 200, 20, C.amber, 700, a, tracking=4)
        draw_text(c, "Reduce the pressure above, watch for flow", 120, 256, 44, C.text, 600, a, display=True)
        kb = ease_in_out(clamp((t - self.word_time("inflow", "pressure above") + 0.2) / 2.0))
        self.test_rig(c, t, 330, 400, 560, a, "cement", pressure=1 - kb, inflow=True)
        gauge(c, 560, 330, 56, 80 * (1 - kb), 0, 120, "", "bar", a, color=C.amber)
        pl = Plot(820, 300, 960, 560, (0, 40), (0, 30), xlabel="Time (minutes)", ylabel="Pressure above barrier (bar)",
                  xticks=[0, 10, 20, 30, 40], yticks=[0, 10, 20, 30])
        pl.axes(c, a)
        f = clamp((t - self.word_time("inflow", "if nothing flows") + 0.5) / 7.0)
        xs = np.linspace(0, 40, 160)
        ys = [0.6 + 0.15 * math.sin(x * 0.8) * math.exp(-x / 6) for x in xs]
        pl.line(c, xs, ys, C.green, 3.5, a, reveal=f)
        yb = [0.6 + 22 * (1 - math.exp(-x / 14)) for x in xs]
        pl.line(c, xs, yb, C.red, 2.5, a * 0.8 * clamp(f * 1.5), reveal=f, dash=[10, 8])
        if f > 0.3:
            ka = a * clamp((f - 0.3) * 3)
            draw_text(c, "stable: barrier holds", pl.px(22), pl.py(3.5), 22, C.green, 700, ka)
            draw_text(c, "build-up: barrier leaks", pl.px(22), pl.py(20), 22, C.red, 600, ka)
            c.drawRect(skia.Rect(pl.px(0), pl.py(30), pl.px(30), pl.py(0)), paint(C.amber, 0.05 * ka))
            draw_text(c, "≥ 30 minutes stable", pl.px(15), pl.py(30) + 30, 20, C.amber, 600, ka, "center")

    def draw_macondo(self, c, t):
        a = self.vis(t, "macondo", "valves", fi=0.7, fo=0.6, b_off=-0.4)
        if a <= 0:
            return
        draw_panel(c, 360, 260, 1200, 560, a, border=mix(C.line, C.red, 0.5))
        icon(c, "warning", 480, 380, 110, C.text, a, C.red)
        draw_text(c, "INTERNATIONAL LESSON", 580, 350, 20, C.red, 700, a, tracking=4)
        draw_text(c, "Macondo · Gulf of Mexico · April 2010", 580, 410, 44, C.text, 600, a, display=True)
        items = ["A negative pressure test was performed before the riser was displaced",
                 "Pressure on the drill pipe was explained away and the test accepted",
                 "Hydrocarbons entered the well; the blowout came hours later"]
        times = [self.c0("macondo") + 1.0, self.word_time("macondo", "misread") - 0.3, self.word_time("macondo", "blew out") - 0.3]
        bullets(c, items, 440, 520, t, times, size=28, max_w=1060, alpha=a, accent=C.red)
        kk = ease_out(clamp((t - self.word_time("macondo", "blew out")) / 0.8))
        draw_text(c, "11 lives lost · the largest marine oil spill in US history", 960, 880, 26, C.muted, 500, a * kk, "center")

    def draw_valves(self, c, t):
        a = self.vis(t, "valves", "bop", fi=0.7, fo=0.6, b_off=-0.4)
        if a <= 0:
            return
        draw_text(c, "VALVES WITH AN ALLOWABLE LEAK RATE", 120, 200, 20, C.primary, 700, a, tracking=4)
        draw_text(c, "DHSV inflow test", 120, 256, 44, C.text, 600, a, display=True)
        # tubing with closed flapper, cavity above
        x, y0, y1 = 360, 360, 940
        bw = 60
        for side in (-1, 1):
            xo = x + side * bw
            c.drawRect(skia.Rect(min(xo, xo + side * 14), y0, max(xo, xo + side * 14), y1), steel_paint(min(xo, xo + side * 14), max(xo, xo + side * 14), a))
        ycl = 760
        kb = ease_in_out(clamp((t - self.word_time("valves", "bleeding off") + 0.3) / 2.0))
        c.drawRect(skia.Rect(x - bw, y0, x + bw, ycl), paint(mix(C.oil, rgb("#3A3F4A"), kb), 0.75 * a))
        c.drawRect(skia.Rect(x - bw, ycl, x + bw, y1), paint(C.oil, 0.85 * a))
        c.drawLine(x - bw, ycl, x + bw, ycl, paint(C.amber, a, stroke=9))
        draw_text(c, "closed DHSV", x + bw + 24, ycl + 8, 22, C.text, 600, a)
        draw_text(c, "closed volume above", x + bw + 24, (y0 + ycl) / 2, 22, C.muted, 500, a)
        draw_text(c, "well pressure below", x + bw + 24, (ycl + y1) / 2 + 10, 22, C.muted, 500, a)
        for k in range(3):
            arrow(c, x - 30 + k * 30, ycl + 70, x - 30 + k * 30, ycl + 14, C.amber, 3, a, head=10)
        # chart of build-up
        pl = Plot(860, 330, 900, 420, (0, 30), (0, 80), xlabel="Time (minutes)", ylabel="Pressure above valve (bar)",
                  xticks=[0, 10, 20, 30], yticks=[0, 20, 40, 60, 80])
        pl.axes(c, a)
        f = clamp((t - self.word_time("valves", "build-up") + 0.3) / 5.0)
        xs = np.linspace(0, 30, 120)
        ys = [5 + 0.9 * x for x in xs]
        pl.line(c, xs, ys, C.amber, 3.5, a, reveal=f)
        if f > 0.5:
            ka = a * clamp((f - 0.5) * 2)
            draw_text(c, "ΔP / Δt × volume × compressibility → leak rate", pl.px(1), pl.py(80) - 16, 22, C.text, 600, ka)
        kc = ease_out(clamp((t - self.word_time("valves", "seventy bar")) / 0.6))
        chip(c, 860, 860, "Production phase: ~70 bar differential recommended", C.primary, a * kc, size=22)
        kd = ease_out(clamp((t - self.word_time("valves", "seventy bar") - 1.2) / 0.6))
        draw_text(c, "Typical DHSV criterion (API RP 14B): 0.42 m³/min gas or 0.4 L/min liquid", 860, 960, 22, C.muted, 500, a * kd)

    def draw_bop(self, c, t):
        a = self.vis(t, "bop", "cement", fi=0.7, fo=0.6, b_off=-0.4)
        if a <= 0:
            return
        draw_text(c, "BLOWOUT PREVENTER", 120, 200, 20, C.secondary, 700, a, tracking=4)
        draw_text(c, "Tested when installed, and at intervals", 120, 256, 44, C.text, 600, a, display=True)
        v = WellView(axis_x=430, y_top=900, y_bot=1100, sx=8)
        st = WellState()
        st.bop_close = 0.5 + 0.5 * math.sin(max(0.0, t - self.c0("bop") - 1.0) * 1.4)
        c.save()
        c.translate(430, 880)
        c.scale(1.7, 1.7)
        c.translate(-430, -880)
        draw_bop(c, v, st, a, y_base=880)
        c.restore()
        items = [("Function test", "every preventer and valve operates"), ("Pressure test", "low and high pressure, held stable")]
        for i, (h1, h2) in enumerate(items):
            kk = ease_out(clamp((t - self.c0("bop") - 0.8 - i * 1.2) / 0.6)) * a
            draw_panel(c, 800, 360 + i * 150, 960, 120, kk, r=14)
            icon(c, "check", 860, 420 + i * 150, 50, C.text, kk, C.green)
            draw_text(c, h1, 910, 410 + i * 150, 32, C.text, 600, kk, display=True)
            draw_text(c, h2, 910, 448 + i * 150, 23, C.muted, 400, kk)
        # 14-day calendar
        k14 = ease_out(clamp((t - self.word_time("bop", "fourteen")) / 0.6)) * a
        if k14 > 0:
            draw_text(c, "Pressure test interval kept at 14 days in revision 5", 800, 720, 26, C.text, 600, k14)
            for d in range(14):
                x = 800 + d * 66
                fill = clamp((t - self.word_time("bop", "fourteen") - d * 0.12) / 0.3)
                c.drawRoundRect(skia.Rect(x, 750, x + 56, 806), 8, 8, paint(C.panel_hi, k14))
                c.drawRoundRect(skia.Rect(x, 750, x + 56, 806), 8, 8, paint(C.line, k14, stroke=1.2))
                draw_text(c, str(d + 1), x + 28, 787, 20, C.muted if d < 13 else C.secondary_hi, 600, k14 * (0.4 + 0.6 * fill), "center")
            c.drawRoundRect(skia.Rect(800 + 13 * 66, 750, 800 + 13 * 66 + 56, 806), 8, 8, paint(C.secondary, k14, stroke=2.5))

    def draw_cement(self, c, t):
        a = self.vis(t, "cement", "cbl", fi=0.7, fo=0.6, b_off=-0.4)
        if a <= 0:
            return
        draw_text(c, "CASING CEMENT", 120, 200, 20, C.primary, 700, a, tracking=4)
        draw_text(c, "We cannot see it, so we infer it", 120, 256, 44, C.text, 600, a, display=True)
        # cement job animation: casing inside a hole, slurry pumped down between plugs, up the annulus
        x, top, bot = 420, 340, 980
        hw, hole = 70, 120
        f = clamp((t - self.c0("cement") + 0.2) / 9.0)
        # formation
        p = skia.Paint(Shader=image_shader(lith_texture("shale"), 0.5))
        p.setAlphaf(a)
        c.drawRect(skia.Rect(x - 260, top, x + 260, bot), p)
        c.drawRect(skia.Rect(x - hole, top, x + hole, bot), paint(C.mud, a))
        # positions: slurry volume enters casing top then goes down; then up annulus
        total = (bot - top) * 2
        lead = f * total * 1.05           # front of cement (leading)
        tail = max(0.0, lead - (bot - top) * 0.95)  # back of cement column (top plug)
        def depth_in_casing(s):
            return top + min(s, bot - top)
        cp = skia.Paint(Shader=image_shader(cement_texture(), 0.5))
        cp.setAlphaf(a)
        # inside casing
        s0, s1 = tail, lead
        if s0 < (bot - top):
            y0 = top + s0
            y1 = top + min(s1, bot - top - 10)
            if y1 > y0:
                c.drawRect(skia.Rect(x - hw, y0, x + hw, y1), cp)
        # annulus part
        if s1 > (bot - top):
            ann = min(s1 - (bot - top), (bot - top) * 0.9)
            ya = bot - ann
            for side in (-1, 1):
                c.drawRect(skia.Rect(min(x + side * hw, x + side * hole), ya, max(x + side * hw, x + side * hole), bot), cp)
        # top plug & bottom plug
        if f > 0:
            yb = top + min(s1, bot - top - 12)
            c.drawRect(skia.Rect(x - hw, yb - 8, x + hw, yb + 4), paint(rgb("#C0392B"), a))
            yt = top + min(s0, bot - top - 24)
            c.drawRect(skia.Rect(x - hw, yt - 10, x + hw, yt + 2), paint(rgb("#2C3E50"), a))
            draw_text(c, "top plug", x + hw + 140, yt, 18, C.muted, 500, a * clamp(f * 4))
            c.drawLine(x + hw + 2, yt - 4, x + hw + 132, yt - 6, paint(C.muted, 0.6 * a, stroke=1.2))
        # displacement mud above the top plug
        if s0 > 0:
            c.drawRect(skia.Rect(x - hw, top, x + hw, top + min(s0, bot - top - 24) - 10), paint(C.mud, 0.9 * a))
        for side in (-1, 1):
            xo = x + side * hw
            c.drawRect(skia.Rect(min(xo, xo + side * 10), top, max(xo, xo + side * 10), bot - 6), steel_paint(min(xo, xo + side * 10), max(xo, xo + side * 10), a))
        # bump indicator
        if f > 0.98:
            stamp(c, x, 300, "PLUG BUMPED", C.green, ease_out(clamp((t - self.c0("cement") - 9.2) / 0.5)) * a, size=22)
        # evidence list
        items = [("Job data: volumes, pressures, returns", "volumes"), ("Pressure test of the casing", "pressure test"),
                 ("Formation strength at the shoe", "formation strength"), ("Logs", "logs")]
        times = [self.word_time("cement", kw) - 0.3 for _, kw in items]
        yy = 380
        for i, ((txt, _), ti) in enumerate(zip(items, times)):
            kk = ease_out(clamp((t - ti) / 0.6)) * a
            draw_panel(c, 900, yy + i * 130, 860, 100, kk, r=14)
            icon(c, ["chart", "gauge", "layers", "magnifier"][i], 960, yy + i * 130 + 50, 52, C.text, kk, C.primary)
            draw_text(c, txt, 1010, yy + i * 130 + 60, 30, C.text, 500, kk)

    def draw_cbl(self, c, t):
        a = self.vis(t, "cbl", "ultra", fi=0.7, fo=0.6, b_off=-0.4)
        if a <= 0:
            return
        draw_text(c, "CEMENT BOND LOG", 120, 200, 20, C.primary, 700, a, tracking=4)
        draw_text(c, "Free pipe rings, bonded pipe is damped", 120, 256, 44, C.text, 600, a, display=True)
        x, top, bot = 300, 330, 1000
        hw, hole = 60, 110
        ztoc = 620  # screen y of top of cement
        p = skia.Paint(Shader=image_shader(lith_texture("claystone"), 0.5))
        p.setAlphaf(a)
        c.drawRect(skia.Rect(x - 200, top, x + 200, bot), p)
        c.drawRect(skia.Rect(x - hole, top, x + hole, ztoc), paint(C.mud, 0.9 * a))
        cp = skia.Paint(Shader=image_shader(cement_texture(), 0.5))
        cp.setAlphaf(a)
        c.drawRect(skia.Rect(x - hole, ztoc, x + hole, bot), cp)
        c.drawRect(skia.Rect(x - hw, top, x + hw, bot), paint(rgb("#2D5F86"), 0.9 * a))
        for side in (-1, 1):
            xo = x + side * hw
            c.drawRect(skia.Rect(min(xo, xo + side * 9), top, max(xo, xo + side * 9), bot), steel_paint(min(xo, xo + side * 9), max(xo, xo + side * 9), a))
        draw_text(c, "free pipe", x + hole + 14, (top + ztoc) / 2, 20, C.text, 600, a)
        draw_text(c, "cemented", x + hole + 14, (ztoc + bot) / 2, 20, C.text, 600, a)
        # tool moving up
        f = clamp((t - self.c0("cbl") - 0.5) / 9.5)
        ty = bot - 40 - f * (bot - top - 120)
        c.drawRoundRect(skia.Rect(x - 14, ty - 60, x + 14, ty + 60), 6, 6, paint(rgb("#C9A227"), a))
        c.drawLine(x, top - 20, x, ty - 60, paint(C.steel_hi, a, stroke=1.5))
        # sonic pulse rings
        ph = (t * 2.2) % 1.0
        c.drawCircle(x, ty - 30, 10 + ph * 50, paint(C.primary_hi, a * (1 - ph) * 0.8, stroke=2))
        bonded = ty > ztoc
        # waveform panel
        draw_panel(c, 700, 330, 520, 300, a, r=14)
        draw_text(c, "Received waveform", 730, 370, 22, C.muted, 600, a)
        amp = 18 if bonded else 95
        wf = skia.Path()
        for i in range(200):
            xx = 730 + i * 2.3
            tt = i / 200 * 8
            env = math.exp(-((tt - 2.2) ** 2) / 1.5) if bonded else math.exp(-tt / 3.5)
            yy = 490 - amp * 0.85 * env * math.sin(tt * 9 + t * 4)
            (wf.moveTo if i == 0 else wf.lineTo)(xx, yy)
        c.drawPath(wf, paint(C.primary_hi if not bonded else C.green, a, stroke=2.5))
        draw_text(c, "HIGH amplitude · free pipe" if not bonded else "LOW amplitude · good bond", 730, 608, 22,
                  C.amber if not bonded else C.green, 700, a, shadow=True)
        # reading guide
        draw_panel(c, 700, 670, 520, 330, a, r=14)
        guide = [("Amplitude", "strength of the casing signal: high in free pipe, low where cement is bonded"),
                 ("VDL", "the full waveform, depth by depth: straight lines are casing arrivals, wavy lines come from the formation")]
        gy = 720
        for (h1, body) in guide:
            draw_text(c, h1, 730, gy, 24, C.primary_hi, 700, a)
            hb = draw_paragraph(c, body, 730, gy + 34, 460, 22, C.muted, 400, a)
            gy += 150
        # log track: amplitude vs depth built as the tool passes
        lx, lw = 1300, 220
        draw_panel(c, lx, 330, lw, 670, a, r=10)
        draw_text(c, "Amplitude", lx + lw / 2, 312, 20, C.muted, 600, a, "center")
        trace = skia.Path()
        first = True
        y = bot - 40
        while y >= ty:
            val = 0.12 if y > ztoc + 10 else (0.85 if y < ztoc - 10 else 0.5)
            val += 0.018 * math.sin(y * 0.071) + 0.014 * math.sin(y * 0.193 + 1.1) + 0.008 * math.sin(y * 0.47 + 2.3)
            xx = lx + 20 + val * (lw - 40)
            (trace.moveTo if first else trace.lineTo)(xx, y)
            first = False
            y -= 4
        c.drawPath(trace, paint(C.primary_hi, a, stroke=2.5))
        # VDL strip
        vx, vw = 1560, 260
        draw_panel(c, vx, 330, vw, 670, a, r=10)
        draw_text(c, "VDL", vx + vw / 2, 312, 20, C.muted, 600, a, "center")
        c.save()
        c.clipRect(skia.Rect(vx + 6, max(ty, 336), vx + vw - 6, bot - 6))
        for k in range(26):
            xx = vx + 10 + k * 9.5
            if True:
                # free pipe: straight casing arrivals; cemented: wavy formation arrivals
                p1 = skia.Path()
                yy = 336
                p1.moveTo(xx, yy)
                while yy < bot:
                    wig = 0 if yy < ztoc else 4 * math.sin(yy * 0.05 + k * 0.7)
                    p1.lineTo(xx + wig, yy)
                    yy += 6
                c.drawPath(p1, paint(C.text if k % 2 == 0 else C.bg0, 0.8 * a, stroke=3.2, cap=skia.Paint.kButt_Cap))
        c.restore()

    def draw_ultra(self, c, t):
        a = self.vis(t, "ultra", "lengths", fi=0.7, fo=0.6, b_off=-0.4)
        if a <= 0:
            return
        draw_text(c, "ULTRASONIC IMAGING", 120, 200, 20, C.primary, 700, a, tracking=4)
        draw_text(c, "All the way around the casing", 120, 256, 44, C.text, 600, a, display=True)
        # top view: rotating transducer
        cx, cy = 420, 610
        c.drawCircle(cx, cy, 230, paint(rgb("#A7A291"), 0.35 * a))
        cp = skia.Paint(Shader=image_shader(cement_texture(), 0.6))
        cp.setAlphaf(a)
        c.drawCircle(cx, cy, 200, cp)
        # channel sector (mud) in the cement
        sector = skia.Path()
        sector.moveTo(cx, cy)
        sector.arcTo(skia.Rect(cx - 200, cy - 200, cx + 200, cy + 200), 150, 45, False)
        sector.close()
        c.drawPath(sector, paint(C.mud, a))
        c.drawCircle(cx, cy, 140, paint(C.steel, a))
        c.drawCircle(cx, cy, 124, paint(rgb("#2D5F86"), a))
        ang = (t * 160) % 360
        rad = math.radians(ang)
        beam = poly([(cx, cy), (cx + 210 * math.cos(rad - 0.05), cy + 210 * math.sin(rad - 0.05)),
                     (cx + 210 * math.cos(rad + 0.05), cy + 210 * math.sin(rad + 0.05))], close=True)
        c.drawPath(beam, paint(C.primary_hi, 0.35 * a, blur=4))
        c.drawCircle(cx, cy, 26, paint(rgb("#C9A227"), a))
        c.drawCircle(cx + 22 * math.cos(rad), cy + 22 * math.sin(rad), 7, paint(C.white, a))
        draw_text(c, "mud channel", cx - 250, cy + 150, 22, rgb("#C9A27A"), 700, a, "right")
        # unrolled impedance map
        mx, my, mw, mh = 860, 330, 640, 640
        draw_panel(c, mx - 10, my - 10, mw + 20, mh + 20, a, r=10)
        f = clamp((t - self.c0("ultra") - 0.5) / 8.0)
        rows = 64
        cols = 72
        rnd = np.random.default_rng(1)
        noise = rnd.uniform(-0.08, 0.08, (rows, cols))
        cw, ch = mw / cols, mh / rows
        shown = int(rows * f)
        for r_ in range(rows - shown, rows):
            for k in range(cols):
                az = k / cols * 360
                depth_frac = r_ / rows
                if depth_frac < 0.25:
                    z = 0.28  # free pipe / fluid
                else:
                    z = 0.85
                    if 150 <= az <= 195 and depth_frac > 0.35:
                        z = 0.18
                z = clamp(z + noise[r_, k])
                col = mix(rgb("#2B6CB0"), rgb("#E0B04A"), z)
                if z < 0.08:
                    col = C.red
                c.drawRect(skia.Rect(mx + k * cw, my + r_ * ch, mx + (k + 1) * cw + 0.6, my + (r_ + 1) * ch + 0.6), paint(col, a))
        draw_text(c, "0°", mx, my + mh + 34, 18, C.muted, 500, a)
        draw_text(c, "360°", mx + mw, my + mh + 34, 18, C.muted, 500, a, "right")
        draw_text(c, "azimuth", mx + mw / 2, my + mh + 34, 18, C.muted, 500, a, "center")
        # legend
        lg = [("Gas", C.red), ("Liquid", rgb("#2B6CB0")), ("Cement", rgb("#E0B04A"))]
        for i, (nm, col) in enumerate(lg):
            c.drawRect(skia.Rect(1560, 420 + i * 60, 1600, 450 + i * 60), paint(col, a))
            draw_text(c, nm, 1616, 444 + i * 60, 24, C.text, 500, a)
        draw_text(c, "acoustic impedance", 1560, 400, 18, C.muted, 600, a)
        if f > 0.8:
            kk = ease_out(clamp((f - 0.8) * 5)) * a
            c.drawRoundRect(skia.Rect(mx + 150 / 360 * mw - 6, my + 0.35 * mh, mx + 195 / 360 * mw + 6, my + mh), 8, 8, paint(C.amber, kk, stroke=3))
            draw_paragraph(c, "A channel that a bond log would average away", 1560, 700, 300, 26, C.amber, 600, kk)

    def draw_lengths(self, c, t):
        a = self.vis(t, "lengths", "doc", fi=0.7, fo=0.6, b_off=-0.4)
        if a <= 0:
            return
        draw_text(c, "HOW MUCH CEMENT IS ENOUGH?", 120, 200, 20, C.primary, 700, a, tracking=4)
        draw_text(c, "Minimum lengths in the annulus", 120, 256, 44, C.text, 600, a, display=True)
        cols = [("Verified by volumes", "longer minimum length", 520, C.amber, "volumes"),
                ("Bond confirmed by logs", "shorter minimum length", 300, C.green, "logs")]
        for i, (h1, h2, hh, col, kw) in enumerate(cols):
            x = 300 + i * 520
            ti = self.word_time("lengths", kw) - 0.4
            k = ease_out(clamp((t - ti) / 1.0)) * a
            if k <= 0:
                continue
            bot = 900
            cp = skia.Paint(Shader=image_shader(cement_texture(), 0.5))
            cp.setAlphaf(k)
            c.drawRect(skia.Rect(x - 70, bot - hh * k, x - 30, bot), cp)
            c.drawRect(skia.Rect(x + 30, bot - hh * k, x + 70, bot), cp)
            for side in (-1, 1):
                xo = x + side * 30
                c.drawRect(skia.Rect(min(xo, xo - side * 8), 340, max(xo, xo - side * 8), bot), steel_paint(min(xo, xo - side * 8), max(xo, xo - side * 8), k))
            c.drawLine(x + 100, bot, x + 100, bot - hh * k, paint(col, k, stroke=3))
            c.drawLine(x + 90, bot, x + 110, bot, paint(col, k, stroke=3))
            c.drawLine(x + 90, bot - hh * k, x + 110, bot - hh * k, paint(col, k, stroke=3))
            draw_text(c, h1, x, 960, 26, C.text, 600, k, "center")
            draw_text(c, h2, x, 994, 22, col, 600, k, "center")
        kp = ease_out(clamp((t - self.word_time("lengths", "permanent")) / 0.8)) * a
        if kp > 0:
            draw_panel(c, 1220, 420, 600, 300, kp, r=16, glow=C.primary)
            draw_text(c, "For permanent abandonment", 1250, 480, 28, C.primary_hi, 600, kp)
            draw_paragraph(c, "External cement must be verified over a defined interval, usually by logging, before it can be "
                           "credited as a barrier element.", 1250, 530, 540, 26, C.text, 400, kp)

    def draw_doc(self, c, t):
        a = self.vis(t, "doc", None, fi=0.7, fo=0.6, b_off=3)
        if a <= 0:
            return
        k = ease_out(clamp((t - self.c0("doc")) / 1.0))
        x, y, w, h = 560, 200, 800, 720
        c.save()
        c.translate(0, (1 - k) * 40)
        draw_panel(c, x, y, w, h, a * k, glow=C.green)
        draw_text(c, "PRESSURE TEST RECORD", x + 40, y + 70, 24, C.text, 700, a * k, tracking=3)
        rows = [("Well", "Production well · illustrative"), ("Element", "Production casing"), ("Test", "Low 18 bar · high 345 bar"),
                ("Duration", "10 min stable"), ("Result", "Accepted"), ("Linked to", "Well barrier schematic · rev. C"),
                ("Signed", "Toolpusher · company representative")]
        for i, (k_, v_) in enumerate(rows):
            kk = ease_out(clamp((t - self.c0("doc") - 0.5 - i * 0.35) / 0.5)) * a
            yy = y + 140 + i * 74
            c.drawLine(x + 40, yy + 22, x + w - 40, yy + 22, paint(C.line, 0.6 * kk, stroke=1))
            draw_text(c, k_, x + 40, yy, 22, C.muted, 600, kk)
            draw_text(c, v_, x + 260, yy, 26, C.green if k_ == "Result" else C.text, 600 if k_ == "Result" else 500, kk)
        c.restore()
        ks = ease_out(clamp((t - self.word_time("doc", "last proven")) / 0.6))
        stamp(c, x + w - 150, y + h - 80, "VERIFIED", C.green, ks * a, size=30)
