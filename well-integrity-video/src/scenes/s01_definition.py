"""Chapter 1: What is well integrity?"""
from __future__ import annotations

import math

import numpy as np
import skia

from engine.core import (C, W, H, clamp, draw_text, draw_panel, ease_in_out, ease_out, ease_out_back, glow_path, lerp,
                         mix, paint, poly, rgb, trim_path, window, with_alpha, draw_paragraph, chip, arrow, path_point,
                         make_particles)
from engine.scene import Scene
from engine.widgets import icon, quote_block, icon_card, gauge
from engine.well import WellView, WellState, draw_formation, draw_well, draw_surface, region_cement, highlight_path

DEF = ("The application of technical, operational and organizational solutions to reduce the risk of "
       "uncontrolled release of formation fluids and well fluids throughout the life cycle of a well.")


class SceneImpl(Scene):
    id = "s01_definition"

    def setup(self):
        self.stages = [
            ("Design", "doc", "designed"),
            ("Drill & complete", "rig", "drilled"),
            ("Produce / inject", "drop", "produces"),
            ("Intervene / workover", "gear", "intervened"),
            ("Suspend", "clock", "suspended"),
            ("Permanently abandon", "lock", "permanently abandoned"),
        ]
        self.v = WellView(axis_x=520, y_top=470, y_bot=1020, sx=6.0, x_left=180, x_right=860)
        st = WellState()
        st.completion = 1
        st.a_annulus_fluid = C.brine
        st.perforations = 1
        st.bore_fluid = C.oil
        st.annulus_fluid = C.brine
        self.st = st
        self.particles = make_particles(90, -1, 0, 1, 1, 1.5, 4.5, seed=4)

    def draw(self, c, t):
        # ---------------------------------------------------------- definition quote
        a_q = self.vis(t, "def", "technical", fi=0.8, fo=0.8, b_off=-0.2)
        if a_q > 0:
            x, w = 260, 1400
            draw_text(c, "DEFINITION", x, 360, 20, C.muted, 600, a_q, tracking=5)
            quote_block(c, DEF, x, 440, w, t, self.c0("def") + 0.2, self.c1("def") - 1.0, size=52, alpha=a_q,
                        highlights=[(("technical", "operational", "organizational"), C.primary),
                                    (("uncontrolled", "release"), C.amber), (("life", "cycle"), C.teal)])
            k = ease_out(clamp((t - self.c0("def") - 1.0) / 1.0))
            chip(c, x, 760, "NORSOK D-010 · definition of well integrity", C.primary, a_q * k, size=22)
            c.drawLine(x - 40, 390, x - 40, 720, paint(C.primary, 0.8 * a_q, stroke=4))
        # ---------------------------------------------------------- three pillars
        a_p = self.vis(t, "technical", "lifecycle", fi=0.6, fo=0.6, a_off=-0.4, b_off=-0.9)
        if a_p > 0:
            draw_text(c, "Three kinds of solutions", W / 2, 210, 50, C.text, 600, a_p, "center", display=True)
            cards = [
                ("Technical", "Casing, cement, packers, valves and wellheads, designed for the loads they will see.",
                 "valve", "technical", C.primary),
                ("Operational", "Procedures, testing, monitoring and operating limits that keep every component inside its design envelope.",
                 "gauge", "operational", C.teal),
                ("Organizational", "Competence, clear responsibilities, management of change and documentation that follows the well.",
                 "people", "organizational", C.amber),
            ]
            cw, ch, gap = 520, 420, 40
            x0 = W / 2 - (3 * cw + 2 * gap) / 2
            for i, (title, body, ic, cue, acc) in enumerate(cards):
                x = x0 + i * (cw + gap)
                y = 300
                ti = self.c0(cue) - 0.3
                k = ease_out(clamp((t - ti) / 0.9))
                a = k * a_p
                if a <= 0.01:
                    continue
                active = window(t, ti, self.c1(cue), 0.4, 0.6)
                c.save()
                c.translate(0, (1 - k) * 50)
                draw_panel(c, x, y, cw, ch, a, glow=acc if active > 0.3 else None, border=mix(C.line, acc, active))
                icon(c, ic, x + cw / 2, y + 110, 110, C.text, a, acc)
                draw_text(c, title, x + cw / 2, y + 230, 40, C.text, 600, a, "center", display=True)
                draw_paragraph(c, body, x + 50, y + 290, cw - 100, 25, C.muted, 400, a, align="center")
                c.restore()
        # ---------------------------------------------------------- life cycle chain
        a_l = self.vis(t, "lifecycle", "why", fi=0.7, fo=0.6, a_off=0.0, b_off=-0.7)
        if a_l > 0:
            draw_text(c, "The life cycle of a well", W / 2, 230, 50, C.text, 600, a_l, "center", display=True)
            n = len(self.stages)
            xs = [220 + i * (W - 440) / (n - 1) for i in range(n)]
            y = 520
            # connecting line
            kline = ease_in_out(clamp((t - self.c0("lifecycle")) / 6.0))
            c.drawLine(xs[0], y, xs[0] + (xs[-1] - xs[0]) * kline, y, paint(C.line, a_l, stroke=3))
            # moving pulse
            if kline > 0.02:
                px_ = xs[0] + (xs[-1] - xs[0]) * ((t * 0.12) % 1.0) * kline
                c.drawCircle(px_, y, 10, paint(C.primary, 0.45 * a_l, blur=8))
                c.drawCircle(px_, y, 4, paint(C.white, 0.9 * a_l))
            for i, (lab, ic, kw) in enumerate(self.stages):
                ti = self.word_time("lifecycle", kw) - 0.2 if i > 0 else self.c0("lifecycle") + 0.2
                k = ease_out_back(clamp((t - ti) / 0.7))
                a = clamp((t - ti) / 0.5) * a_l
                if a <= 0:
                    continue
                hot = window(t, ti, ti + 1.6, 0.2, 0.8)
                acc = C.primary if i < 5 else rgb("#8E9AF0")
                r = 62 * (0.6 + 0.4 * k)
                c.drawCircle(xs[i], y, r + 14 * hot, paint(acc, 0.25 * hot * a, blur=12))
                c.drawCircle(xs[i], y, r, paint(C.panel, a))
                c.drawCircle(xs[i], y, r, paint(mix(C.line, acc, 0.4 + 0.6 * hot), a, stroke=2.5))
                icon(c, ic, xs[i], y, 62, C.text, a, acc)
                draw_text(c, lab, xs[i], y + 115, 25, C.text, 600, a, "center")
            # handovers
            a_h = self.vis(t, "handover", "why", fi=0.6, fo=0.6)
            if a_h > 0:
                for i in range(n - 1):
                    mx = (xs[i] + xs[i + 1]) / 2
                    k = ease_out_back(clamp((t - self.c0("handover") - 0.6 - i * 0.35) / 0.6))
                    if k <= 0:
                        continue
                    c.save()
                    c.translate(mx, y - 120)
                    c.scale(k, k)
                    c.drawRoundRect(skia.Rect(-34, -40, 34, 40), 6, 6, paint(C.panel_hi, a_h))
                    c.drawRoundRect(skia.Rect(-34, -40, 34, 40), 6, 6, paint(C.green, a_h, stroke=2))
                    icon(c, "check", 0, 0, 44, C.text, a_h, C.green)
                    c.restore()
                    c.drawLine(mx, y - 78, mx, y - 12, paint(C.green, 0.5 * a_h * k, stroke=1.5))
                kk = ease_out(clamp((t - self.c0("handover") - 0.3) / 0.8))
                draw_text(c, "Every handover carries a documented, verified barrier status", W / 2, 780, 32, C.text, 500,
                          a_h * kk, "center", display=True)
                chip(c, W / 2, 820, "ISO 16530-1 · life-cycle governance", C.green, a_h * kk, size=22, align="center")
        # ---------------------------------------------------------- why it matters
        a_w = self.vis(t, "why", None, fi=0.8, fo=0.6, a_off=0.1, b_off=4)
        if a_w > 0:
            self.draw_why(c, t, a_w)

    def draw_why(self, c, t, a):
        v, st = self.v, self.st
        c.save()
        c.clipRect(skia.Rect(150, 100, 900, 1040))
        draw_formation(c, v, alpha=a)
        draw_well(c, v, st, t, a)
        draw_surface(c, v, st, a)
        c.restore()
        draw_text(c, "Why it matters", 1000, 230, 52, C.text, 600, a, display=True)
        items = [
            ("Blowout", "uncontrolled flow to surface", "blowout", C.red),
            ("Release to sea or air", "hydrocarbons into the environment", "release", C.amber),
            ("Underground flow", "crossflow between formations", "underground", C.orange),
            ("Slow, hidden leak", "pressure where it should not be", "slow leak", C.yellow),
        ]
        for i, (title, sub, kw, col) in enumerate(items):
            ti = self.word_time("why", kw) - 0.2
            k = ease_out(clamp((t - ti) / 0.7))
            if k <= 0:
                continue
            y = 330 + i * 150
            c.save()
            c.translate((1 - k) * 40, 0)
            c.drawCircle(1020, y - 12, 12, paint(col, a * k))
            c.drawCircle(1020, y - 12, 22, paint(col, 0.3 * a * k, blur=8))
            draw_text(c, title, 1056, y, 36, C.text, 600, a * k, display=True)
            draw_text(c, sub, 1056, y + 40, 25, C.muted, 400, a * k)
            c.restore()
            # visual on the schematic
            ph = t - ti
            if kw == "blowout":
                top = v.y(0) - 46 - 4 * 48 - 20
                for j, pt in enumerate(self.particles[:45]):
                    life = ((ph * 0.6 + pt.phase / 6.283) % 1.0)
                    yy = top - life * 120
                    xx = v.ax + pt.x * (10 + life * 70)
                    c.drawCircle(xx, yy, pt.r * (1 + life * 2.4), paint(col, 0.55 * a * k * (1 - life)))
            elif kw == "release":
                wy = v.y(0) - 20
                for j, pt in enumerate(self.particles[45:75]):
                    life = ((ph * 0.35 + pt.phase / 6.283) % 1.0)
                    xx = v.ax + 120 + life * 200 * (0.6 + abs(pt.x))
                    yy = wy - 30 * life + 18 * pt.y
                    c.drawCircle(xx, yy, pt.r * 1.3, paint(C.oil, 0.85 * a * k * (1 - life)))
            elif kw == "underground":
                # crossflow behind casing from reservoir to a shallower permeable zone
                xr = v.xr(12.25) + 3
                y0_, y1_ = v.y(3010), v.y(1950)
                pth = poly([(xr, y0_), (xr, y1_), (xr + 140, y1_)])
                glow_path(c, trim_path(pth, 0, ease_in_out(clamp(ph / 2.5))), col, 3, a * k, glow=8)
                kk = clamp(ph / 2.5)
                (hx, hy), _ = path_point(pth, (ph * 0.3) % 1.0 * kk)
                c.drawCircle(hx, hy, 5, paint(C.white, a * k))
                c.drawRect(skia.Rect(v.xr(12.25), v.y(1900), v.x_right, v.y(2000)), paint(col, 0.18 * a * k))
            elif kw == "slow leak":
                val = 20 + 160 * ease_in_out(clamp(ph / 6.0))
                gauge(c, 790, 300, 54, val, 0, 250, "", "bar", a * k,
                      zones=[(0, 120, C.green), (120, 200, C.yellow), (200, 250, C.red)])
                xa = v.ax + v.r(30) + 16 + 82
                c.drawLine(xa - 15, v.y(0) - 30, 745, 340, paint(C.muted, 0.6 * a * k, stroke=1.5))
                draw_text(c, "A-annulus", 790, 395, 18, C.text, 600, a * k, "center")
