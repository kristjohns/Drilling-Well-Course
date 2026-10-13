"""Chapter 6: Classifying well integrity."""
from __future__ import annotations

import math

import numpy as np
import skia

from engine.core import (C, W, H, arrow, chip, clamp, draw_panel, draw_paragraph, draw_text, ease_in_out, ease_out,
                         ease_out_back, glow_path, lerp, mix, paint, poly, rgb, trim_path, window, with_alpha, rrect)
from engine.scene import Scene
from engine.widgets import icon, bullets, Plot, waffle, counter, stamp

CATS = [
    ("green", "Green", C.green, "Healthy well", "Barrier philosophy intact; no or only minor issues."),
    ("yellow", "Yellow", C.yellow, "One barrier degraded", "The other barrier is intact. Increased risk, within the regulations."),
    ("orange", "Orange", C.orange, "One barrier failed", "The other is intact, or a single further failure could lead to a leak to surface."),
    ("red", "Red", C.red, "Failure and degradation", "One barrier failed and the other degraded or not verified, or a leak to surface."),
]


def mini_envelopes(c, x, y, s, state, a, t):
    """Two nested envelopes; state in green/yellow/orange/red."""
    inner = poly([(x - 0.18 * s, y + 0.42 * s), (x - 0.18 * s, y - 0.05 * s), (x + 0.18 * s, y - 0.05 * s), (x + 0.18 * s, y + 0.42 * s)])
    outer = poly([(x - 0.38 * s, y + 0.42 * s), (x - 0.38 * s, y - 0.32 * s), (x + 0.38 * s, y - 0.32 * s), (x + 0.38 * s, y + 0.42 * s)])
    c.drawRect(skia.Rect(x - 0.5 * s, y + 0.42 * s, x + 0.5 * s, y + 0.5 * s), paint(rgb("#3B3F44"), a))
    c.drawOval(skia.Rect(x - 0.14 * s, y + 0.3 * s, x + 0.14 * s, y + 0.4 * s), paint(C.amber, 0.8 * a))
    # outer (secondary)
    if state == "red":
        p = paint(C.secondary, a, stroke=4)
        p.setPathEffect(skia.DashPathEffect.Make([10, 8], t * 10))
        c.drawPath(outer, p)
    else:
        glow_path(c, outer, C.secondary, 3.5, a, glow=8)
    # inner (primary)
    if state == "green":
        glow_path(c, inner, C.primary, 3.5, a, glow=8)
    elif state == "yellow":
        p = paint(C.primary, a, stroke=4)
        p.setPathEffect(skia.DashPathEffect.Make([10, 7], 0))
        c.drawPath(inner, p)
    else:
        # broken inner with a gap
        c.drawPath(trim_path(inner, 0.0, 0.42), paint(C.primary, a, stroke=4))
        c.drawPath(trim_path(inner, 0.58, 1.0), paint(C.primary, a, stroke=4))
        c.drawCircle(x, y - 0.05 * s, 0.07 * s, paint(C.red, 0.5 * a, blur=6))
    if state in ("orange", "red"):
        for k in range(5):
            life = ((t * 0.5 + k / 5) % 1.0)
            c.drawCircle(x + (k - 2) * 0.05 * s, y - 0.05 * s - life * 0.22 * s, 3, paint(C.amber, a * (1 - life)))
    if state == "red":
        for k in range(4):
            life = ((t * 0.6 + k / 4) % 1.0)
            c.drawCircle(x + (k - 1.5) * 0.08 * s, y - 0.32 * s - life * 0.2 * s, 3.5, paint(C.amber, a * (1 - life)))


class SceneImpl(Scene):
    id = "s06_classify"

    def setup(self):
        rnd = np.random.default_rng(4)
        self.pilot_colors = [C.amber if i in set(rnd.choice(406, 73, replace=False)) else rgb("#2A4A6E") for i in range(406)]
        cols = [C.green] * 263 + [C.yellow] * 192 + [C.orange] * 30 + [C.red] * 3
        self.ta_colors = cols

    def draw(self, c, t):
        self.draw_categories(c, t)
        self.draw_rnnp(c, t)
        self.draw_pilot(c, t)
        self.draw_ta(c, t)

    def draw_categories(self, c, t):
        a = self.vis(t, "intro", "rnnp", fi=0.8, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        k_use = ease_in_out(clamp((t - self.c0("use") + 0.3) / 1.0))
        draw_text(c, "Offshore Norge guideline 117", 120, 210, 22, C.muted, 600, a * (1 - k_use), tracking=2)
        draw_text(c, "Well integrity categories", 120, 268, 52, C.text, 600, a * (1 - k_use), display=True)
        n = 4
        tw, th, gap = 400, 560, 30
        x0 = W / 2 - (n * tw + (n - 1) * gap) / 2
        for i, (key, name, col, head, desc) in enumerate(CATS):
            ti = self.c0("intro") + 1.0 + i * 0.35
            k = ease_out(clamp((t - ti) / 0.7)) * a
            if k <= 0:
                continue
            active = self.vis(t, key, None, fi=0.4, fo=0.5, b_off=0.4)
            past = t > self.c0(key)
            x = x0 + i * (tw + gap)
            y = 340 + (1 - k) * 40 - k_use * 160
            hh = th - k_use * 250
            c.drawRoundRect(skia.Rect(x, y, x + tw, y + hh), 22, 22, paint(mix(C.panel, mix(C.panel, col, 0.18), active), k))
            c.drawRoundRect(skia.Rect(x, y, x + tw, y + hh), 22, 22, paint(mix(C.line, col, 0.3 + 0.7 * active), k, stroke=2))
            if active > 0:
                c.drawRoundRect(skia.Rect(x, y, x + tw, y + hh), 22, 22, paint(col, 0.25 * active * k, blur=18, stroke=8))
            c.drawRect(skia.Rect(x + 24, y + 30, x + 84, y + 42), paint(col, k))
            draw_text(c, name.upper(), x + 24, y + 86, 34, col, 800, k, display=True, tracking=3)
            if k_use < 0.99:
                ka = k * (1 - k_use)
                mini_envelopes(c, x + tw / 2, y + 230, 220, key, ka * (0.35 + 0.65 * (1 if past else 0)), t)
                kt = ease_out(clamp((t - self.c0(key) + 0.2) / 0.6)) * ka
                draw_text(c, head, x + 24, y + 410, 30, C.text, 600, kt, display=True)
                draw_paragraph(c, desc, x + 24, y + 452, tw - 48, 23, C.muted, 400, kt, leading=1.35)
            else:
                draw_text(c, head, x + 24, y + 150, 26, C.text, 600, k)
        if k_use > 0:
            items = [("Which wells are repaired first", "repaired first", "chart"), ("Which wells are shut in", "shut in", "valve"),
                     ("Compensating measures in the meantime", "compensating", "shield")]
            for i, (txt, kw, ic) in enumerate(items):
                kk = ease_out(clamp((t - self.word_time("use", kw) + 0.3) / 0.6)) * a
                y = 560 + i * 130
                draw_panel(c, 360, y, 1200, 100, kk, r=16)
                icon(c, ic, 430, y + 50, 52, C.text, kk, C.primary)
                draw_text(c, txt, 490, y + 62, 34, C.text, 500, kk, display=True)
            draw_text(c, "The category drives priorities", 360, 520, 30, C.muted, 600, a * k_use)

    def draw_rnnp(self, c, t):
        a = self.vis(t, "rnnp", "pilot", fi=0.7, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        draw_panel(c, 360, 260, 1200, 560, a, glow=C.teal)
        draw_text(c, "RNNP", 420, 380, 110, C.teal, 800, a, display=True)
        draw_text(c, "Trends in risk level in the Norwegian petroleum activity", 420, 450, 32, C.text, 500, a)
        draw_text(c, "Havtil · annual survey", 420, 494, 24, C.muted, 500, a)
        items = [("Well control incidents", "chart"), ("Well integrity", "shield")]
        for i, (txt, ic) in enumerate(items):
            kk = ease_out(clamp((t - self.word_time("rnnp", "well control") - 0.2 + i * 0.8) / 0.6)) * a
            x = 420 + i * 520
            c.drawRoundRect(skia.Rect(x, 560, x + 480, 740), 18, 18, paint(C.panel_hi, kk))
            icon(c, ic, x + 70, 650, 70, C.text, kk, C.teal)
            draw_text(c, txt, x + 130, 662, 30, C.text, 600, kk)
            # sparkline
            pts = [(x + 130 + j * 26, 710 - 16 * math.sin(j * 0.9 + i) - j * 1.5) for j in range(12)]
            c.drawPath(poly(pts), paint(C.teal, 0.8 * kk, stroke=2))

    def draw_pilot(self, c, t):
        a = self.vis(t, "pilot", "ta", fi=0.7, fo=0.6, b_off=-0.5)
        if a <= 0:
            return
        draw_text(c, "PILOT STUDY FOR THE PETROLEUM SAFETY AUTHORITY", 120, 210, 20, C.muted, 700, a, tracking=3)
        draw_text(c, "406 production and injection wells · 12 facilities", 120, 268, 44, C.text, 600, a, display=True)
        rev = clamp((t - self.word_time("pilot", "four hundred") + 0.3) / 3.0)
        hl = ease_out(clamp((t - self.word_time("pilot", "eighteen percent")) / 1.0))
        cols = [mix(rgb("#2A4A6E"), col, hl) for col in self.pilot_colors]
        waffle(c, 140, 360, 406, 29, 22, 8, cols, reveal=rev, a=a)
        if hl > 0:
            counter(c, 18 * hl, 1440, 560, 180, C.amber, a * hl, fmt="{:.0f}", suffix="%")
            draw_paragraph(c, "had a well integrity failure, issue or uncertainty", 1180, 640, 560, 34, C.text, 500, a * hl,
                           align="center")
        kt = ease_out(clamp((t - self.word_time("pilot", "production tubing") + 0.2) / 0.8)) * a
        if kt > 0:
            draw_panel(c, 1180, 760, 560, 160, kt, r=16, glow=C.primary)
            icon(c, "valve", 1250, 840, 60, C.text, kt, C.primary)
            draw_text(c, "Most common failing component:", 1310, 826, 22, C.muted, 600, kt)
            draw_text(c, "production tubing", 1310, 872, 36, C.text, 700, kt, display=True)
        draw_text(c, "Vignes and Aadnøy, SPE Production & Operations, 2010", 140, 1000, 20, C.dim, 500, a)

    def draw_ta(self, c, t):
        a = self.vis(t, "ta", self.dur, fi=0.7, fo=0.6)
        if a <= 0:
            return
        draw_text(c, "HAVTIL SURVEY · TEMPORARILY ABANDONED AND INACTIVE WELLS", 120, 210, 20, C.muted, 700, a, tracking=3)
        k_cnt = ease_in_out(clamp((t - self.c0("tacount") + 0.2) / 1.0))
        k_rules = self.vis(t, "tarules", "tacount", fi=0.5, fo=0.5, b_off=-0.3)
        # bars 2022 vs 2024
        kb = 1 - ease_in_out(clamp((t - self.c0("tarules") + 0.3) / 0.5))
        if kb > 0:
            draw_text(c, "Reported wells", 120, 268, 48, C.text, 600, a * kb, display=True)
            for i, (yr, n, kw) in enumerate([(2022, 227, "double"), (2024, 488, "four hundred")]):
                ti = self.word_time("ta", kw) - (0.5 if i == 0 else 0.3)
                kk = ease_out(clamp((t - ti) / 1.2))
                y = 400 + i * 200
                wbar = 1100 * n / 488 * kk
                c.drawRoundRect(skia.Rect(320, y, 320 + wbar, y + 110), 14, 14, paint(C.primary if i else rgb("#4C6A92"), a * kb))
                draw_text(c, str(yr), 290, y + 72, 40, C.text, 600, a * kb, "right", display=True)
                counter(c, n * kk, 320 + wbar + 24, y + 74, 54, C.text, a * kb * clamp(kk * 3), align="left")
            ke = ease_out(clamp((t - self.word_time("ta", "partly because") + 0.2) / 0.8)) * a * kb
            draw_paragraph(c, "Roughly double, partly because inactive production wells were included under the EU methane regulation.",
                           320, 860, 1300, 30, C.muted, 500, ke)
        if k_rules > 0:
            draw_text(c, "While temporarily abandoned", 120, 268, 48, C.text, 600, a * k_rules, display=True)
            rules = [("Qualified, independent barriers, designed for the planned period", "lock"),
                     ("Subsea wells left for more than 12 months: integrity must be monitored", "gauge")]
            for i, (txt, ic) in enumerate(rules):
                kk = ease_out(clamp((t - self.c0("tarules") - 0.3 - i * (self.word_time("tarules", "subsea") - self.c0("tarules") - 0.3)) / 0.6)) * a * k_rules
                y = 400 + i * 200
                draw_panel(c, 240, y, 1440, 150, kk, r=18, glow=C.primary)
                icon(c, ic, 330, y + 75, 70, C.text, kk, C.primary)
                draw_paragraph(c, txt, 400, y + 66, 1220, 34, C.text, 500, kk, display=True)
        if k_cnt > 0:
            draw_text(c, "2024 survey: 488 wells", 120, 268, 48, C.text, 600, a * k_cnt, display=True)
            rev = clamp((t - self.c0("tacount") - 0.2) / 4.0)
            waffle(c, 130, 350, 488, 32, 22, 7, self.ta_colors, reveal=rev, a=a * k_cnt)
            legend = [("Green", 263, C.green, "two hundred and sixty-three"), ("Yellow", 192, C.yellow, "ninety-two"),
                      ("Orange", 30, C.orange, "thirty orange"), ("Red", 3, C.red, "classified red")]
            for i, (nm, n, col, kw) in enumerate(legend):
                kk = ease_out(clamp((t - self.word_time("tacount", kw) + 0.2) / 0.5)) * a * k_cnt
                y = 380 + i * 92
                c.drawCircle(1150, y, 16, paint(col, kk))
                draw_text(c, nm, 1185, y + 12, 32, C.text, 500, kk)
                draw_text(c, str(n), 1500, y + 12, 40, col, 700, kk, "right", display=True)
            kr = ease_out(clamp((t - self.word_time("tacount", "rose from")) / 0.8)) * a * k_cnt
            if kr > 0:
                draw_panel(c, 1130, 760, 660, 150, kr, r=16, glow=C.orange)
                draw_text(c, "Red + orange", 1160, 815, 26, C.muted, 600, kr)
                v = lerp(17, 33, ease_in_out(clamp((t - self.word_time("tacount", "rose from") - 0.5) / 2.0)))
                draw_text(c, f"17  →  {v:.0f}", 1160, 880, 52, C.orange, 800, kr, display=True)
                draw_text(c, "2022 → 2024", 1600, 880, 24, C.muted, 500, kr)
        ke = self.vis(t, "expect", None, fi=0.6, fo=0.5, b_off=3) * a
        if ke > 0:
            c.drawRect(skia.Rect(0, 0, W, H), paint(C.bg0, 0.92 * ke))
            draw_text(c, "Havtil's expectation", W / 2, 330, 50, C.text, 600, ke, "center", display=True)
            rows = [("RED", C.red, "permanently plugged", self.word_time("expect", "red wells")),
                    ("ORANGE", C.orange, "brought back into use, or permanently plugged", self.word_time("expect", "orange wells"))]
            for i, (lab, col, txt, ti) in enumerate(rows):
                kk = ease_out(clamp((t - ti + 0.2) / 0.6)) * ke
                y = 440 + i * 170
                draw_panel(c, 360, y, 1200, 130, kk, r=18, border=col, glow=col)
                draw_text(c, lab, 410, y + 82, 40, col, 800, kk, display=True, tracking=3)
                draw_text(c, "→  " + txt, 700, y + 80, 36, C.text, 500, kk, display=True)
