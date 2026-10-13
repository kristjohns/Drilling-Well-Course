"""Chapter 2: The Norwegian framework."""
from __future__ import annotations

import math

import numpy as np
import skia

from engine.core import (C, W, H, arrow, chip, clamp, draw_panel, draw_paragraph, draw_text, ease_in_out, ease_out,
                         ease_out_back, glow_path, lerp, mix, paint, poly, rgb, trim_path, window, with_alpha, rrect,
                         path_point)
from engine.scene import Scene
from engine.widgets import icon, bullets


class SceneImpl(Scene):
    id = "s02_framework"

    def setup(self):
        self.fields = ["Ekofisk", "Valhall", "Sleipner", "Johan Sverdrup", "Oseberg", "Troll", "Gullfaks", "Statfjord",
                       "Snorre", "Heidrun", "Norne", "Aasta Hansteen", "Snøhvit", "Johan Castberg"]

    def draw(self, c, t):
        self.draw_functional(c, t)
        self.draw_hierarchy(c, t)
        self.draw_norsok(c, t)
        self.draw_guidelines(c, t)
        self.draw_forums(c, t)

    # ------------------------------------------------------------------
    def draw_functional(self, c, t):
        a = self.vis(t, "functional", "facilities", fi=0.7, fo=0.7, b_off=-0.6)
        if a <= 0:
            return
        k_reg = ease_out(clamp((t - self.c0("functional") - 0.2) / 0.9))
        k_std = ease_out(clamp((t - self.word_time("functional", "guidelines")) / 0.9))
        y = 300
        # regulations
        if k_reg > 0:
            c.save()
            c.translate(0, (1 - k_reg) * 40)
            draw_panel(c, 230, y, 600, 300, a * k_reg, glow=C.primary)
            icon(c, "book", 320, y + 95, 90, C.text, a * k_reg, C.primary)
            draw_text(c, "Regulations", 400, y + 110, 46, C.text, 600, a * k_reg, display=True)
            draw_text(c, "WHAT must be achieved", 290, y + 205, 30, C.primary, 600, a * k_reg)
            draw_text(c, "functional requirements", 290, y + 248, 24, C.muted, 400, a * k_reg)
            c.restore()
        if k_std > 0:
            c.save()
            c.translate(0, (1 - k_std) * 40)
            draw_panel(c, 1090, y, 600, 300, a * k_std, glow=C.teal)
            icon(c, "doc", 1180, y + 95, 90, C.text, a * k_std, C.teal)
            draw_text(c, "Standards", 1260, y + 110, 46, C.text, 600, a * k_std, display=True)
            draw_text(c, "HOW it can be achieved", 1150, y + 205, 30, C.teal, 600, a * k_std)
            draw_text(c, "recognized industry practice", 1150, y + 248, 24, C.muted, 400, a * k_std)
            c.restore()
            arrow(c, 850, y + 150, 1070, y + 150, C.muted, 3, a * k_std, glow=True)
            draw_text(c, "guidelines refer to", 960, y + 130, 20, C.muted, 500, a * k_std, "center")
        # Havtil card
        a_h = self.vis(t, "havtil", "facilities", fi=0.7, fo=0.6, b_off=-0.6)
        if a_h > 0:
            k = ease_out(clamp((t - self.c0("havtil")) / 0.9))
            yy = 700
            c.save()
            c.translate(0, (1 - k) * 30)
            draw_panel(c, 560, yy, 800, 190, a_h, border=C.line)
            icon(c, "shield", 660, yy + 95, 90, C.text, a_h, C.green)
            draw_text(c, "Havtil", 740, yy + 80, 46, C.text, 700, a_h, display=True)
            draw_text(c, "Norwegian Ocean Industry Authority", 740, yy + 122, 26, C.text, 500, a_h)
            draw_text(c, "known as the Petroleum Safety Authority (Ptil) until 2024", 740, yy + 158, 21, C.muted, 400, a_h)
            c.restore()

    # ------------------------------------------------------------------
    def draw_hierarchy(self, c, t):
        a = self.vis(t, "facilities", "norsok", fi=0.8, fo=0.7, a_off=-0.3, b_off=-0.4)
        if a <= 0:
            return
        x0, y0 = 120, 200
        bw = 560
        boxes = [
            ("act", "Petroleum Act", 0),
            ("frame", "Framework Regulations", 1),
            ("mgmt", "Management Regulations", 2),
            ("fac", "Facilities Regulations", 3),
            ("act2", "Activities Regulations", 4),
        ]
        active = None
        if t >= self.c0("management") - 0.3:
            active = "mgmt"
        elif t >= self.c0("activities") - 0.3:
            active = "act2"
        elif t >= self.c0("facilities") - 0.3:
            active = "fac"
        draw_text(c, "REGULATORY HIERARCHY", x0, y0 - 30, 18, C.muted, 600, a, tracking=4)
        for i, (key, lab, lvl) in enumerate(boxes):
            k = ease_out(clamp((t - self.c0("facilities") + 0.2 - i * 0.18) / 0.7))
            if k <= 0:
                continue
            indent = 0 if lvl < 2 else 50
            y = y0 + i * 112
            hot = 1.0 if key == active else 0.0
            col = mix(C.line, C.primary, hot)
            c.save()
            c.translate((1 - k) * -40, 0)
            draw_panel(c, x0 + indent, y, bw - indent, 88, a * k, fill=mix(C.panel, C.panel_hi, hot), border=col,
                       glow=C.primary if hot else None)
            draw_text(c, lab, x0 + indent + 30, y + 56, 30, C.text if hot or lvl < 2 else C.muted, 600 if hot else 500, a * k, display=True)
            c.restore()
            if lvl >= 2:
                c.drawLine(x0 + 22, y0 + 88 + 112, x0 + 22, y + 44, paint(C.line, a * k, stroke=2))
                c.drawLine(x0 + 22, y + 44, x0 + indent, y + 44, paint(C.line, a * k, stroke=2))
        # requirement panel on the right
        px, py, pw, ph = 760, 200, 1040, 640
        panels = [
            ("fac", "Facilities Regulations · § 48", "Well barriers", "facilities", "activities", [
                ("Designed so that well integrity is ensured and barrier functions are safeguarded during the well's lifetime", "facilities", "designed so"),
                ("Barrier performance must be verifiable", "facilities", "verifiable"),
                ("When abandoned: designed for the longest period the well is expected to remain abandoned", "abandon", "abandoned"),
                ("Casings can be cut safely when the well is finally plugged", "abandon", "cut the casings"),
            ]),
            ("act2", "Activities Regulations · § 85", "Well barriers", "activities", "management", [
                ("Tested well barriers with sufficient independence during drilling and well activities", "activities", "tested well"),
                ("If a barrier fails, no other activities than those intended to restore it", "activities", "if a barrier"),
                ("At handover, barrier status is tested, verified and documented", "handover", "handed over"),
            ]),
            ("mgmt", "Management Regulations · § 5", "Barriers", "management", "norsok", [
                ("Barriers are established and maintained", "management", "established"),
                ("It is known which barriers exist and what function they serve", "management", "which barriers"),
                ("Performance requirements are defined, and it is known whether the barriers work", "management", "performance"),
            ]),
        ]
        for key, head, sub, ca, cb, items in panels:
            ap = self.vis(t, ca, cb, fi=0.6, fo=0.5, a_off=-0.2, b_off=-0.5) * a
            if ap <= 0:
                continue
            draw_panel(c, px, py, pw, ph, ap, glow=C.primary)
            draw_text(c, head.upper(), px + 50, py + 70, 22, C.primary, 700, ap, tracking=3)
            draw_text(c, sub, px + 50, py + 130, 50, C.text, 600, ap, display=True)
            times = [self.word_time(cue, kw) - 0.3 for (_, cue, kw) in items]
            times[0] = min(times[0], self.c0(items[0][1]) + 0.6)
            bullets(c, [it[0] for it in items], px + 50, py + 230, t, times, size=33, max_w=pw - 140, alpha=ap, gap=1.9,
                    accent=C.primary)

    # ------------------------------------------------------------------
    def draw_norsok(self, c, t):
        a = self.vis(t, "norsok", "guidelines", fi=0.8, fo=0.6, a_off=-0.2, b_off=-0.5)
        if a <= 0:
            return
        # document page
        k = ease_out(clamp((t - self.c0("norsok") + 0.2) / 1.0))
        dx, dy, dw, dh = 170, 190, 520, 700
        c.save()
        c.translate(0, (1 - k) * 60)
        c.drawRoundRect(skia.Rect(dx + 14, dy + 14, dx + dw + 14, dy + dh + 14), 10, 10, paint(C.black, 0.4 * a, blur=16))
        pg = skia.Paint(AntiAlias=True)
        pg.setShader(skia.GradientShader.MakeLinear([skia.Point(dx, dy), skia.Point(dx + dw, dy + dh)],
                                                    [rgb("#F4F6F9"), rgb("#DCE2EA")]))
        pg.setAlphaf(a)
        c.drawRoundRect(skia.Rect(dx, dy, dx + dw, dy + dh), 10, 10, pg)
        c.drawRect(skia.Rect(dx, dy, dx + dw, dy + 120), paint(rgb("#1D3557"), a))
        draw_text(c, "NORSOK", dx + 40, dy + 78, 44, C.white, 800, a, display=True, tracking=4)
        draw_text(c, "D-010", dx + 40, dy + 220, 96, rgb("#1D3557"), 800, a, display=True)
        draw_paragraph(c, "Well integrity in drilling and well operations", dx + 40, dy + 300, dw - 80, 34,
                       rgb("#1D3557"), 600, a, display=True)
        draw_text(c, "Edition 5 · 2021", dx + 40, dy + 470, 28, rgb("#3D5A80"), 600, a)
        draw_text(c, "consolidated with corrections · 2024", dx + 40, dy + 510, 24, rgb("#5C7391"), 500, a)
        for kk in range(5):
            c.drawLine(dx + 40, dy + 570 + kk * 22, dx + dw - 40 - (kk % 2) * 80, dy + 570 + kk * 22, paint(rgb("#B8C4D3"), a, stroke=6))
        c.restore()
        # right side: what it is / rev 5
        a1 = self.vis(t, "norsok", "rev5", fi=0.6, fo=0.5, a_off=0.6, b_off=-0.3)
        if a1 > 0:
            draw_text(c, "The recommended way to meet", 800, 300, 26, C.muted, 500, a1)
            draw_text(c, "the well barrier requirements", 800, 340, 26, C.muted, 500, a1)
            items = ["Minimum functional and performance requirements for well barriers",
                     "Covers the whole life cycle: drilling, completion, production, intervention, abandonment",
                     "Element acceptance tables for each type of barrier element"]
            times = [self.c0("norsok") + 2.5 + i * 3.0 for i in range(3)]
            bullets(c, items, 800, 440, t, times, size=30, max_w=950, alpha=a1, accent=C.primary)
        a2 = self.vis(t, "rev5", "guidelines", fi=0.6, fo=0.5, b_off=-0.5)
        if a2 > 0:
            draw_text(c, "WHAT REVISION 5 ADDED", 800, 240, 20, C.primary, 700, a2, tracking=4)
            items = [
                ("Reorganized structure and a barrier requirements matrix", "reorganized"),
                ("Premises for creeping formation as a barrier element", "creeping"),
                ("Barrier materials other than cement", "materials other"),
                ("Perforate, wash and cement · section milling", "perforate"),
                ("Expanded managed pressure drilling chapter", "managed pressure"),
                ("Qualification of new technology", "qualifying"),
            ]
            times = [self.word_time("rev5", kw) - 0.3 for _, kw in items]
            times[0] = self.c0("rev5") + 0.4
            yy = 300
            for i, ((lab, _), ti) in enumerate(zip(items, times)):
                kk = ease_out(clamp((t - ti) / 0.6))
                if kk <= 0:
                    continue
                y = yy + i * 98
                c.save()
                c.translate((1 - kk) * 40, 0)
                draw_panel(c, 800, y, 960, 78, a2 * kk, r=14)
                icon(c, "check", 845, y + 39, 40, C.text, a2 * kk, C.green)
                draw_text(c, lab, 885, y + 50, 30, C.text, 500, a2 * kk)
                c.restore()

    # ------------------------------------------------------------------
    def draw_guidelines(self, c, t):
        a = self.vis(t, "guidelines", "forums", fi=0.7, fo=0.6, a_off=-0.2, b_off=-0.5)
        if a <= 0:
            return
        draw_text(c, "Offshore Norge guidelines", W / 2, 220, 52, C.text, 600, a, "center", display=True)
        cards = [
            ("117", "Recommended guidelines for well integrity",
             ["Well integrity classification", "Annulus pressure management · MAASP", "Handover documentation"], C.primary, "guideline"),
            ("135", "Classification and categorisation of well control and well integrity incidents",
             ["Common incident categories", "Consistent reporting across operators"], C.amber, "one-thirty-five"),
        ]
        for i, (num, title, items, col, kw) in enumerate(cards):
            ti = self.c0("guidelines") + 0.3 if i == 0 else self.word_time("guidelines", "one-thirty-five") - 0.4
            k = ease_out(clamp((t - ti) / 0.8))
            if k <= 0:
                continue
            x = 200 + i * 790
            y = 300
            c.save()
            c.translate(0, (1 - k) * 40)
            draw_panel(c, x, y, 730, 560, a * k, glow=col)
            draw_text(c, num, x + 50, y + 160, 120, col, 300, a * k, display=True)
            draw_text(c, "GUIDELINE", x + 50, y + 54, 18, C.muted, 600, a * k, tracking=4)
            draw_paragraph(c, title, x + 50, y + 225, 630, 32, C.text, 600, a * k, display=True)
            tt = [ti + 1.5 + j * 1.6 for j in range(len(items))]
            bullets(c, items, x + 50, y + 360, t, tt, size=27, max_w=600, alpha=a * k, accent=col)
            c.restore()

    # ------------------------------------------------------------------
    def draw_forums(self, c, t):
        a = self.vis(t, "forums", None, fi=0.8, fo=0.6, b_off=3)
        if a <= 0:
            return
        cx, cy, R = W / 2, 560, 330
        n = len(self.fields)
        pts = []
        for i in range(n):
            ang = -math.pi / 2 + i * 2 * math.pi / n
            pts.append((cx + R * 1.45 * math.cos(ang), cy + R * math.sin(ang)))
        k = ease_out(clamp((t - self.c0("forums")) / 1.2))
        # links
        for i in range(n):
            for j in (i + 1, i + 3, i + 5):
                j %= n
                kk = clamp(k * 1.3 - 0.2)
                c.drawLine(*pts[i], *pts[j], paint(C.line, 0.5 * a * kk, stroke=1.2))
            c.drawLine(*pts[i], cx, cy, paint(C.line, 0.4 * a * k, stroke=1))
        # lesson pulse from one field to all others
        src = 6  # Gullfaks
        ph = clamp((t - self.c0("forums") - 2.5) / 4.0)
        for i in range(n):
            if i == src or ph <= 0:
                continue
            pth = poly([pts[src], (cx, cy), pts[i]])
            q = ease_in_out(clamp(ph * 1.2 - (abs(i - src) % n) * 0.02))
            (hx, hy), _ = path_point(pth, q)
            if 0 < q < 1:
                c.drawCircle(hx, hy, 9, paint(C.amber, 0.5 * a, blur=6))
                c.drawCircle(hx, hy, 4, paint(C.white, a))
        for i, (x, y) in enumerate(pts):
            reached = ph > 0.85 or i == src
            col = C.amber if reached else C.primary
            c.drawCircle(x, y, 13, paint(col, a * k))
            c.drawCircle(x, y, 24, paint(col, 0.25 * a * k, blur=8))
            al = "left" if x > cx + 5 else ("right" if x < cx - 5 else "center")
            ox = 22 if al == "left" else (-22 if al == "right" else 0)
            oy = 8 if al != "center" else (-26 if y < cy else 40)
            draw_text(c, self.fields[i], x + ox, y + oy, 22, C.text, 500, a * k, al)
        c.drawCircle(cx, cy, 120, paint(C.panel, 0.95 * a * k))
        c.drawCircle(cx, cy, 120, paint(C.amber, 0.8 * a * k, stroke=2))
        draw_text(c, "Shared", cx, cy - 8, 34, C.text, 600, a * k, "center", display=True)
        draw_text(c, "lessons", cx, cy + 32, 34, C.text, 600, a * k, "center", display=True)
        draw_text(c, "Industry forums for well integrity and for plug and abandonment", W / 2, 1000, 26, C.muted, 500,
                  a * k, "center")
