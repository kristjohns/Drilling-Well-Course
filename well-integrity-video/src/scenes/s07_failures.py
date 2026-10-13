"""Chapter 7: When barriers fail - failure modes and NCS incidents."""
from __future__ import annotations

import math

import numpy as np
import skia

from engine.core import (font, C, W, H, arrow, chip, clamp, draw_panel, draw_paragraph, draw_text, ease_in_out, ease_out,
                         ease_out_back, glow_path, lerp, mix, paint, poly, rgb, trim_path, window, with_alpha, rrect,
                         image_shader)
from engine.scene import Scene
from engine.widgets import icon, bullets, Plot, gauge, stamp, counter
from engine.well import (WellView, WellState, draw_formation, draw_well, draw_surface, highlight, highlight_path,
                         region_casing, region_cement, steel_paint, lith_texture, cement_texture, draw_bop, draw_rcd,
                         LITH_COLORS, STRATIGRAPHY)
from engine.ncsmap import MapView, draw_map


class SceneImpl(Scene):
    id = "s07_failures"

    def setup(self):
        rnd = np.random.default_rng(12)
        self.bub = [(rnd.uniform(0, 1), rnd.uniform(-1, 1), rnd.uniform(2, 5)) for _ in range(80)]
        self.map_small = MapView(90, 170, 640, 820, 0.5, 6.5, 59.6, 62.0)

    def draw(self, c, t):
        self.draw_modes(c, t)
        self.draw_compaction(c, t)
        self.draw_snorre(c, t)
        self.draw_gullfaks(c, t)
        self.draw_troll(c, t)
        self.draw_common(c, t)

    # ------------------------------------------------------------------ failure modes
    def draw_modes(self, c, t):
        a = self.vis(t, "modes", "compaction", fi=0.7, fo=0.6, a_off=-0.3, b_off=-0.4)
        if a <= 0:
            return
        v = WellView(axis_x=520, y_top=400, y_bot=1030, sx=7.4, x_left=150, x_right=890)
        st = WellState()
        st.completion = 1
        st.a_annulus_fluid = C.brine
        st.perforations = 1
        st.bore_fluid = C.oil
        st.annulus_fluid = C.mud
        c.save()
        c.clipRect(skia.Rect(130, 90, 910, 1045))
        draw_formation(c, v, alpha=a)
        draw_well(c, v, st, t, a)
        draw_surface(c, v, st, a)
        # markers
        def ring(x, y, k):
            if k <= 0:
                return
            pr = (t * 0.9) % 1.0
            c.drawCircle(x, y, 14 + 26 * pr, paint(C.red, a * k * (1 - pr), stroke=2.5))
            c.drawCircle(x, y, 9, paint(C.red, a * k))
        kt = ease_out(clamp((t - self.c0("tubing") + 0.2) / 0.5))
        if kt > 0:
            yl = v.y(1600)
            for (u, x_, r) in self.bub[:25]:
                life = (u + t * 0.35) % 1.0
                c.drawCircle(v.ax - v.r(4.5) - 6 - abs(x_) * 12, yl - life * 140, r * 0.8, paint(C.gas, 0.8 * a * kt * (1 - life)))
            ring(v.ax - v.r(4.5), yl, kt)
        kd = ease_out(clamp((t - self.c0("dhsv") + 0.2) / 0.5))
        ring(v.ax, v.y(st.dhsv_depth), kd)
        kc = ease_out(clamp((t - self.c0("casing") + 0.2) / 0.5))
        if kc > 0:
            highlight_path(c, region_casing(v, st, "prod", 1850, 2150), C.red, a * kc, fill=0.6)
            ring(v.ax + v.r(9.625), v.y(2000), kc)
        kce = ease_out(clamp((t - self.c0("cement") + 0.2) / 0.5))
        if kce > 0:
            x0 = v.ax + v.r(9.625) + 3
            c.drawRect(skia.Rect(x0, v.y(2400), x0 + 7, v.y(2780)), paint(C.mud, a * kce))
            c.drawLine(v.ax - v.r(9.625) - 1, v.y(2380), v.ax - v.r(9.625) - 1, v.y(2780), paint(C.gas, a * kce, stroke=1.8))
            ring(x0 + 3, v.y(2600), kce)
        ks = ease_out(clamp((t - self.c0("seals") + 0.2) / 0.5))
        ring(v.ax + v.r(9.6), v.y(0) - 20, ks)
        c.restore()
        # list
        draw_text(c, "How barrier elements fail", 980, 220, 48, C.text, 600, a, display=True)
        items = [("Tubing", "corrosion, connection leaks", "tubing", "drop"), ("Safety valves", "fail to close, or leak when closed", "dhsv", "valve"),
                 ("Casing", "wear, corrosion, deformation", "casing", "layers"), ("Cement", "channels, cracks, micro-annulus", "cement", "magnifier"),
                 ("Seals", "wellhead and hanger seals age", "seals", "gear")]
        for i, (h1, h2, cue, ic) in enumerate(items):
            k = ease_out(clamp((t - self.c0(cue) + 0.3) / 0.6)) * a
            y = 300 + i * 136
            draw_panel(c, 980, y, 820, 112, k, r=16)
            icon(c, ic, 1046, y + 56, 54, C.text, k, C.red)
            draw_text(c, h1, 1100, y + 50, 32, C.text, 600, k, display=True)
            draw_text(c, h2, 1100, y + 88, 23, C.muted, 400, k)

    # ------------------------------------------------------------------ compaction
    def draw_compaction(self, c, t):
        a = self.vis(t, "compaction", "snorre", fi=0.7, fo=0.6, a_off=-0.2, b_off=-0.5)
        if a <= 0:
            return
        k = ease_in_out(clamp((t - self.c0("compaction") - 1.0) / 9.0))
        x0, x1 = 120, 1800
        sea, sb = 260, 420           # sea surface and seabed (screen y)
        sub = 46 * k                 # exaggerated seabed subsidence (px)

        def bowl(x, depth_amp):
            return depth_amp * math.exp(-((x - 960) / 520) ** 2)
        # water
        wp = skia.Paint()
        wp.setShader(skia.GradientShader.MakeLinear([skia.Point(0, sea), skia.Point(0, sb + sub)], [rgb("#1C5C78"), rgb("#0B2A40")]))
        c.drawRect(skia.Rect(x0, sea, x1, sb + 60), wp)
        # layers (seabed, overburden 3 layers, chalk reservoir, base)
        tops = [(sb, "clay", 1.0), (sb + 110, "claystone", 0.9), (sb + 260, "shale", 0.8), (sb + 420, "chalk", 1.0), (sb + 560, "shale", 0.0)]
        prev = None
        paths = []
        for i, (y, lith, amp_f) in enumerate(tops):
            amp = sub * (0.65 + 0.35 * amp_f) if i < 4 else sub * 0.0
            if i == 4:
                amp = 0
            pts = [(x, y + bowl(x, amp if i < 4 else 0)) for x in np.linspace(x0, x1, 60)]
            paths.append(pts)
        # reservoir compaction: top of chalk sinks more than base (thinning)
        for i in range(len(paths)):
            top = paths[i]
            bot = paths[i + 1] if i + 1 < len(paths) else [(x, 1040) for x, _ in top]
            pth = poly(top + bot[::-1], close=True)
            lith = tops[i][1]
            c.drawPath(pth, paint(LITH_COLORS[lith], a))
            tp = skia.Paint(AntiAlias=True, Shader=image_shader(lith_texture(lith), 0.6))
            tp.setAlphaf(0.5 * a)
            c.drawPath(pth, tp)
            c.drawPath(poly(top), paint(C.black, 0.4 * a, stroke=1.5))
        draw_text(c, "Chalk reservoir compacts", 1380, tops[3][0] + 80, 26, C.text, 600, a, shadow=True)
        draw_text(c, "Overburden and seabed follow", 1380, tops[1][0] + 70, 26, C.text, 600, a, shadow=True)
        # casing: vertical, kinked at the reservoir top
        cx = 960
        cas = skia.Path()
        cas.moveTo(cx, sb + bowl(cx, sub) - 20)
        ytop_res = tops[3][0] + bowl(cx, sub)
        cas.lineTo(cx, ytop_res - 30)
        kink = 16 * k
        cas.lineTo(cx + kink, ytop_res - 10)
        cas.lineTo(cx - kink, ytop_res + 10)
        cas.lineTo(cx, ytop_res + 30)
        cas.lineTo(cx, 1030)
        c.drawPath(cas, paint(C.steel_hi, a, stroke=7))
        if k > 0.6:
            kk = (k - 0.6) / 0.4
            pr = (t * 0.9) % 1.0
            c.drawCircle(cx, ytop_res, 18 + 20 * pr, paint(C.red, a * kk * (1 - pr), stroke=2.5))
            c.drawRRect(rrect(cx + 40, ytop_res - 18, font(22, 600).measureText("casing deformation") + 28, 22 * 1.6, 22 * 0.8),
                        paint(C.bg0, 0.75 * a * kk))
            chip(c, cx + 40, ytop_res - 18, "casing deformation", C.red, a * kk, size=22)
        # platform on jacket standing on the seabed
        base_y = sb + bowl(cx, sub)
        deck_y = base_y - 250
        for xx in (-60, -20, 20, 60):
            c.drawLine(cx + xx * 0.7, deck_y + 10, cx + xx, base_y, paint(rgb("#6B7788"), a, stroke=3))
        c.drawRect(skia.Rect(cx - 70, deck_y - 30, cx + 70, deck_y + 10), paint(rgb("#3B4656"), a))
        c.drawLine(x0, sea, x1, sea, paint(rgb("#BFEFFF"), 0.8 * a, stroke=1.5))
        # deck clearance indicator
        c.drawLine(cx + 110, sea, cx + 110, deck_y + 10, paint(C.amber, a, stroke=2))
        draw_text(c, "air gap shrinks", cx + 122, (sea + deck_y) / 2 + 6, 20, C.amber, 600, a)
        # counter
        draw_text(c, "EKOFISK", 140, 170, 22, C.amber, 700, a, tracking=5)
        draw_text(c, "Seabed subsidence", 140, 220, 30, C.text, 600, a)
        counter(c, 9 * k, 520, 222, 64, C.amber, a, fmt="{:.1f}", align="left", suffix=" m")
        kn = ease_out(clamp((t - self.c0("compaction") - 7) / 0.8)) * a
        draw_text(c, "In 1987 the Ekofisk Complex platforms were jacked up about 6 m", 1180, 200, 22, C.muted, 500, kn)
        draw_text(c, "vertical scale exaggerated", x1 - 10, 1030, 14, C.dim, 500, a, "right", italic=True)

    # ------------------------------------------------------------------ incident helpers
    def incident_header(self, c, t, title, date, a, hot):
        draw_map(c, self.map_small, a, fields=["Snorre", "Statfjord", "Gullfaks", "Oseberg", "Troll"], hot=(hot,), t=t)
        draw_text(c, date, 800, 210, 22, C.amber, 700, a, tracking=4)
        draw_text(c, title, 800, 270, 52, C.text, 600, a, display=True)

    def draw_snorre(self, c, t):
        a = self.vis(t, "snorre", "gullfaks", fi=0.8, fo=0.6, a_off=-0.3, b_off=-0.5)
        if a <= 0:
            return
        self.incident_header(c, t, "Snorre A · gas blowout", "28 NOVEMBER 2004", a, "Snorre")
        # schematic: floating platform, seabed, well with worn casing, gas path to seabed
        X, sea, sb = 1110, 460, 600
        wp = skia.Paint()
        wp.setShader(skia.GradientShader.MakeLinear([skia.Point(0, sea), skia.Point(0, sb)], [rgb("#1C5C78"), rgb("#0B2A40")]))
        c.drawRect(skia.Rect(860, sea, 1360, sb), wp)
        tp = skia.Paint(Shader=image_shader(lith_texture("claystone"), 0.6))
        tp.setAlphaf(a)
        c.drawRect(skia.Rect(860, sb, 1360, 1020), tp)
        rp = skia.Paint(Shader=image_shader(lith_texture("reservoir"), 0.6))
        rp.setAlphaf(a)
        c.drawRect(skia.Rect(860, 950, 1360, 1020), rp)
        c.drawLine(860, sea, 1360, sea, paint(rgb("#BFEFFF"), 0.8 * a, stroke=1.5))
        # TLP hull + tendons
        c.drawRect(skia.Rect(X - 150, sea - 60, X + 150, sea - 20), paint(rgb("#3B4656"), a))
        for xx in (-120, 120):
            c.drawRect(skia.Rect(X + xx - 22, sea - 20, X + xx + 22, sea + 50), paint(rgb("#4C5A6E"), a))
            c.drawLine(X + xx, sea + 50, X + xx, sb, paint(C.steel, 0.6 * a, stroke=2))
        c.drawRect(skia.Rect(X - 40, sea - 110, X - 10, sea - 60), paint(rgb("#4C5A6E"), a))
        # riser and well
        c.drawLine(X, sea - 20, X, sb, paint(C.steel_hi, 0.8 * a, stroke=4))
        for side in (-1, 1):
            for (od, bot) in ((34, 820), (22, 1000)):
                c.drawRect(skia.Rect(X + side * od - (3 if side > 0 else 0), sb, X + side * od + (0 if side > 0 else 3), bot), steel_paint(X + side * od - 3, X + side * od + 3, a))
        c.drawRect(skia.Rect(X - 19, sb, X + 19, 1000), paint(C.mud, 0.85 * a))
        # tubing being pulled (moves up)
        kp = ease_in_out(clamp((t - self.c0("snorre") - 3.0) / 8.0))
        tub_top = sb - 60 - 80 * kp
        c.drawRect(skia.Rect(X - 7, tub_top, X + 7, 960 - 220 * kp), steel_paint(X - 7, X + 7, a))
        arrow(c, X - 60, 800, X - 60, 710, C.amber, 3, a * window(t, self.c0("snorre") + 3, self.c0("snorre2"), 0.4, 0.6), head=12)
        draw_text(c, "pulling", X - 72, 760, 20, C.amber, 600, a * window(t, self.c0("snorre") + 3, self.c0("snorre2"), 0.4, 0.6))
        # worn casing hole
        hole_y = 720
        kh = ease_out(clamp((t - self.word_time("snorre", "worn casing") + 0.3) / 0.6))
        c.drawCircle(X + 22, hole_y, 7, paint(C.red, a * kh))
        if kh > 0:
            draw_text(c, "worn casing", X + 40, hole_y + 36, 20, C.red, 700, a * kh)
        # gas: up the well to the hole, out into formation, up to seabed, bubbling in the water
        kg = clamp((t - self.word_time("snorre", "drew gas") + 0.2) / 3.0)
        kill = ease_in_out(clamp((t - self.word_time("snorre2", "heavy mud")) / 3.0))
        if kg > 0:
            path = poly([(X, 960), (X, hole_y), (X + 22, hole_y), (X + 90, hole_y - 40), (X + 130, sb + 10), (X + 140, sb - 10)])
            glow_path(c, trim_path(path, 0, kg), C.gas, 3, a * (1 - kill), glow=10)
            for (u, x_, r) in self.bub:
                life = (u + t * 0.25) % 1.0
                if kg < 0.95:
                    continue
                bx = X + 140 + x_ * 50 + 10 * math.sin(t * 2 + u * 10)
                by = sb - life * (sb - sea - 10)
                c.drawCircle(bx, by, r * (0.6 + 0.6 * life), paint(C.gas, 0.8 * a * (1 - kill) * (1 - 0.5 * life)))
        if kill > 0:
            c.drawRect(skia.Rect(X - 19, sb, X + 19, sb + (1000 - sb) * kill), paint(C.kill_mud, a))
        # facts
        a2 = self.vis(t, "snorre2", "gullfaks", fi=0.6, fo=0.5, b_off=-0.5)
        facts = [("Production shut down", "production was shut", "warning"), ("180 evacuated by helicopter, 36 stayed", "evacuated", "heli"),
                 ("Well killed with heavy mud", "heavy mud", "drop"), ("Inadequate planning and risk assessment", "inadequate", "doc"),
                 ("Governing documents not followed", "governing", "cross")]
        for i, (txt, kw, ic) in enumerate(facts):
            kk = ease_out(clamp((t - self.word_time("snorre2", kw) + 0.3) / 0.6)) * a2
            if kk <= 0:
                continue
            y = 400 + i * 110
            icon(c, ic, 1420, y - 8, 36, C.text, kk, C.amber if i < 3 else C.red)
            draw_paragraph(c, txt, 1460, y, 380, 26, C.text, 500, kk)
        a1 = self.vis(t, "snorre", "snorre2", fi=0.6, fo=0.4, b_off=-0.3)
        if a1 > 0:
            draw_paragraph(c, "Tubing and casing were being pulled from an injection well to prepare a sidetrack.", 1420, 420, 400,
                           30, C.text, 500, a1)

    def draw_gullfaks(self, c, t):
        a = self.vis(t, "gullfaks", "troll", fi=0.8, fo=0.6, a_off=-0.3, b_off=-0.5)
        if a <= 0:
            return
        self.incident_header(c, t, "Gullfaks C · loss of well control", "MAY 2010", a, "Gullfaks")
        X, top, bot = 1080, 360, 1010
        tp = skia.Paint(Shader=image_shader(lith_texture("shale"), 0.6))
        tp.setAlphaf(a)
        c.drawRect(skia.Rect(860, top, 1320, bot), tp)
        rp = skia.Paint(Shader=image_shader(lith_texture("reservoir"), 0.6))
        rp.setAlphaf(a)
        c.drawRect(skia.Rect(860, 900, 1320, bot), rp)
        cp = skia.Paint(Shader=image_shader(cement_texture(), 0.5))
        cp.setAlphaf(a)
        for side in (-1, 1):
            c.drawRect(skia.Rect(min(X + side * 60, X + side * 80), 720, max(X + side * 60, X + side * 80), 800), cp)
        c.drawRect(skia.Rect(X - 60, top, X + 60, 800), paint(C.mud, 0.85 * a))
        c.drawRect(skia.Rect(X - 40, 800, X + 40, bot), paint(C.mud, 0.85 * a))
        for side in (-1, 1):
            c.drawRect(skia.Rect(min(X + side * 60, X + side * 66), top, max(X + side * 60, X + side * 66), 800), steel_paint(X - 66, X + 66, a))
        draw_text(c, "13⅜ in casing", X - 80, 420, 20, C.text, 600, a, "right")
        # hole in casing
        hy = 560
        kh = ease_out(clamp((t - self.word_time("gullfaks", "hole") + 0.3) / 0.6))
        c.drawRect(skia.Rect(X + 58, hy - 8, X + 68, hy + 8), paint(C.red, a * kh))
        if kh > 0:
            for k in range(4):
                off = ((t * 1.2 + k * 0.25) % 1.0) * 120
                arrow(c, X + 70 + off, hy, X + 96 + off, hy, C.mud, 3, a * kh, head=9)
            draw_text(c, "losses to the formation", X + 90, hy - 22, 20, C.mud, 700, a * kh)
        ki = clamp((t - self.word_time("gullfaks", "influx") + 0.3) / 2.0)
        if ki > 0:
            for (u, x_, r) in self.bub[:40]:
                life = (u + t * 0.18) % 1.0
                yy = bot - life * (bot - top) * ki
                c.drawCircle(X + x_ * 30, yy, r * 0.8, paint(C.gas, 0.8 * a))
            draw_text(c, "influx from the reservoir", X - 80, 960, 20, C.gas, 700, a * clamp(ki * 2), "right")
        facts = [("Managed pressure drilling", "managed pressure"), ("Hole in the 13⅜ in casing", "hole"),
                 ("Losses, then influx", "influx"), ("Insufficient technical integrity of the casing", "insufficient"),
                 ("More than two months to restore the barriers", "two months")]
        for i, (txt, kw) in enumerate(facts):
            kk = ease_out(clamp((t - self.word_time("gullfaks", kw) + 0.3) / 0.6)) * a
            y = 400 + i * 72
            c.drawCircle(1372, y - 8, 7, paint(C.amber, kk))
            draw_paragraph(c, txt, 1395, y, 430, 26, C.text, 500, kk)
        kk = ease_out(clamp((t - self.word_time("gullfaks", "two months") - 0.5) / 0.6)) * a
        draw_text(c, "Statoil estimated losses of about NOK 1.8 billion", 1372, 800, 20, C.muted, 500, kk)

    def draw_troll(self, c, t):
        a = self.vis(t, "troll", "common", fi=0.8, fo=0.6, a_off=-0.3, b_off=-0.5)
        if a <= 0:
            return
        self.incident_header(c, t, "Troll · Deepsea Bollsta", "23 SEPTEMBER 2025", a, "Troll")
        k2 = ease_in_out(clamp((t - self.c0("troll2") + 0.3) / 0.8))
        # schematic of P&A cut (left part of the right half)
        X, sea, sb = 1110, 450, 570
        alpha_s = a * (1 - 0.0 * k2)
        wp = skia.Paint()
        wp.setShader(skia.GradientShader.MakeLinear([skia.Point(0, sea), skia.Point(0, sb)], [rgb("#1C5C78"), rgb("#0B2A40")]))
        c.drawRect(skia.Rect(860, sea, 1360, sb), wp)
        tp = skia.Paint(Shader=image_shader(lith_texture("clay"), 0.6))
        tp.setAlphaf(alpha_s)
        c.drawRect(skia.Rect(860, sb, 1360, 1010), tp)
        c.drawLine(860, sea, 1360, sea, paint(rgb("#BFEFFF"), 0.8 * a, stroke=1.5))
        # semi-sub rig
        c.drawRect(skia.Rect(X - 150, sea - 70, X + 150, sea - 40), paint(rgb("#3B4656"), a))
        for xx in (-110, 110):
            c.drawRect(skia.Rect(X + xx - 18, sea - 40, X + xx + 18, sea + 40), paint(rgb("#4C5A6E"), a))
        c.drawPath(poly([(X - 30, sea - 70), (X, sea - 160), (X + 30, sea - 70)]), paint(C.steel_hi, a, stroke=2.5))
        # riser to subsea BOP
        c.drawLine(X, sea - 40, X, sb - 50, paint(C.steel_hi, 0.8 * a, stroke=6))
        c.drawRect(skia.Rect(X - 26, sb - 50, X + 26, sb), paint(rgb("#B3262E"), a))
        # casings: 20 in (outer) to 760, 13 3/8 to 980
        for side in (-1, 1):
            c.drawRect(skia.Rect(min(X + side * 46, X + side * 50), sb, max(X + side * 46, X + side * 50), 860), steel_paint(X - 50, X + 50, a))
            c.drawRect(skia.Rect(min(X + side * 28, X + side * 32), sb, max(X + side * 28, X + side * 32), 1000), steel_paint(X - 32, X + 32, a))
        c.drawRect(skia.Rect(X - 28, sb, X + 28, 1000), paint(C.brine, 0.6 * a))
        # deep cement plug already set
        cp = skia.Paint(Shader=image_shader(cement_texture(), 0.5))
        cp.setAlphaf(a)
        c.drawRect(skia.Rect(X - 28, 920, X + 28, 995), cp)
        # trapped gas behind 13 3/8 (in the annulus between 13 3/8 and 20)
        kgas = ease_out(clamp((t - self.word_time("troll", "accumulated") + 0.3) / 1.0))
        cut_t = self.word_time("troll", "was cut")
        released = ease_in_out(clamp((t - cut_t) / 2.0))
        gas_top, gas_bot = 680, 850
        for side in (-1, 1):
            xa, xb = X + side * 32, X + side * 46
            hgt = (gas_bot - gas_top) * (1 - 0.8 * released)
            c.drawRect(skia.Rect(min(xa, xb), gas_bot - hgt, max(xa, xb), gas_bot), paint(C.gas, 0.85 * a * kgas))
        if kgas > 0:
            draw_paragraph(c, "gas from the reservoir behind the 13⅜ in casing", X + 64, 760, 180, 19, C.gas, 700, a * kgas)
        # cutter
        ycut = 700
        kc = ease_out(clamp((t - self.c0("troll") - 2.0) / 1.0))
        c.drawLine(X, sb - 50, X, ycut - 20, paint(C.steel_hi, a * kc, stroke=3))
        c.drawRect(skia.Rect(X - 12, ycut - 20, X + 12, ycut + 20), paint(rgb("#C9A227"), a * kc))
        spin = t * 12
        for side in (-1, 1):
            ext = 14 + 6 * clamp((t - cut_t + 1.5) / 1.5)
            c.drawLine(X, ycut, X + side * ext, ycut + 3 * math.sin(spin), paint(C.steel_hi, a * kc, stroke=3))
        if t > cut_t - 0.3:
            fl = window(t, cut_t - 0.3, cut_t + 0.6, 0.2, 0.6)
            c.drawCircle(X, ycut, 40, paint(C.white, 0.5 * a * fl, blur=12))
        # gas flowing up to the rig
        if released > 0:
            stop = ease_out(clamp((t - cut_t - 3.0) / 1.5))
            for (u, x_, r) in self.bub:
                life = (u + t * 0.7) % 1.0
                yy = ycut - life * (ycut - (sea - 60))
                c.drawCircle(X + x_ * 8, yy, r * 0.7, paint(C.gas, 0.85 * a * released * (1 - 0.7 * stop)))
            kb = window(t, cut_t + 0.5, self.c1("troll") + 2, 0.4, 0.6)
            draw_text(c, "to the rig", X + 160, sea - 50, 20, C.gas, 700, a * kb)
        # facts
        facts_a = a * (1 - k2)
        facts = [("Well Q-21 being permanently plugged", "permanently plugged"), ("13⅜ in casing cut", "was cut"),
                 ("About 930 kg of gas released", "nine hundred"), ("114 people on board", "one hundred and fourteen")]
        for i, (txt, kw) in enumerate(facts):
            kk = ease_out(clamp((t - self.word_time("troll", kw) + 0.3) / 0.6)) * facts_a
            y = 400 + i * 90
            c.drawCircle(1420, y - 8, 7, paint(C.amber, kk))
            draw_paragraph(c, txt, 1445, y, 400, 27, C.text, 500, kk)
        kk = ease_out(clamp((t - self.word_time("troll", "one hundred and fourteen") - 0.5) / 0.6)) * facts_a
        draw_text(c, "Equinor: BOP closed after 71 seconds", 1420, 790, 20, C.muted, 500, kk)
        # Havtil findings
        if k2 > 0:
            draw_panel(c, 1390, 330, 470, 660, a * k2, glow=C.red, r=18)
            draw_text(c, "HAVTIL FINDINGS", 1420, 380, 20, C.red, 700, a * k2, tracking=4)
            fnd = [("Failure in the well's outer barrier", "outer barrier"), ("No barriers towards the reservoir during the cut", "lack of barriers"),
                   ("Technology and methods not qualified for the purpose", "not qualified"),
                   ("Faulty calibration: log data misinterpreted, gas not detected", "calibration"),
                   ("Potential for a major accident", "major accident")]
            y = 440
            for i, (txt, kw) in enumerate(fnd):
                kk = ease_out(clamp((t - self.word_time("troll2", kw) + 0.3) / 0.6)) * a * k2
                c.drawCircle(1420, y - 8, 7, paint(C.red, kk))
                y += draw_paragraph(c, txt, 1440, y, 400, 25, C.text, 500, kk) + 34
            kk = ease_out(clamp((t - self.word_time("troll2", "major accident") - 0.6) / 0.6)) * a * k2
            draw_text(c, "12 non-conformities · order to Equinor, 2026", 1420, 960, 19, C.muted, 500, kk)

    def draw_common(self, c, t):
        a = self.vis(t, "common", self.dur, fi=0.7, fo=0.5)
        if a <= 0:
            return
        draw_text(c, "Twenty years apart, the same threads", W / 2, 260, 50, C.text, 600, a, "center", display=True)
        y = 440
        k = ease_in_out(clamp((t - self.c0("common")) / 1.5))
        c.drawLine(400, y, 400 + 1120 * k, y, paint(C.line, a, stroke=3))
        for i, (yr, nm) in enumerate([("2004", "Snorre A"), ("2010", "Gullfaks C"), ("2025", "Troll")]):
            x = 400 + i * 560
            kk = ease_out_back(clamp((t - self.c0("common") - 0.3 - i * 0.4) / 0.6)) * a
            c.drawCircle(x, y, 16 * kk, paint(C.red, a))
            draw_text(c, yr, x, y - 40, 34, C.text, 700, kk, "center", display=True)
            draw_text(c, nm, x, y + 54, 24, C.muted, 500, kk, "center")
        words = [("Understand", "understand"), ("Verify", "verify"), ("Plan", "plan for"), ("Follow the plan", "follow")]
        for i, (wd, kw) in enumerate(words):
            kk = ease_out(clamp((t - self.word_time("common", kw) + 0.2) / 0.5)) * a
            x = 300 + i * 440
            draw_panel(c, x - 190, 620, 380, 130, kk, r=18, glow=C.primary)
            draw_text(c, wd, x, 700, 38, C.primary_hi, 700, kk, "center", display=True)
