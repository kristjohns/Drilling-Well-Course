"""Cold open: sea, platform, strata, the well, title and agenda."""
from __future__ import annotations

import math

import numpy as np
import skia

from engine.core import (C, W, H, clamp, draw_text, ease_in_out, ease_out, ease_out_quint, glow_path, lerp, mix,
                         paint, poly, prog, rgb, trim_path, window, with_alpha, image_shader, draw_paragraph, font,
                         path_point)
from engine.scene import Scene
from engine.well import lith_texture, STRATIGRAPHY, cement_texture, LITH_COLORS
from engine.widgets import icon

WATER = 300.0  # water depth (m)


def dome(x, crest, amp=260.0, width=2600.0):
    """Anticline: depth of a horizon at lateral position x (m)."""
    return crest + amp * (1 - math.exp(-(x / width) ** 2))


class World:
    """Static description of the cross-section, in metres (x lateral, z depth below sea level)."""

    def __init__(self):
        self.xs = np.linspace(-6000, 6000, 121)
        rnd = np.random.default_rng(3)
        # horizon depths (below sea level) for each stratigraphic top
        self.horizons = []
        for i, L in enumerate(STRATIGRAPHY):
            base = WATER + L.top
            if L.top == 0:
                z = WATER + 4 * np.sin(self.xs / 380.0) + 3 * np.sin(self.xs / 97.0 + 1)
            else:
                # deeper horizons follow the dome more strongly
                amp = 40 + 260 * clamp((L.top - 900) / 2100)
                z = np.array([dome(x, base, amp, 2800) for x in self.xs])
                z += 6 * np.sin(self.xs / 610.0 + i) + rnd.normal(0, 1.5, len(self.xs))
            self.horizons.append(z)
        self.bottom = np.full_like(self.xs, WATER + 4200)

    def layer_path(self, i):
        top = self.horizons[i]
        bot = self.horizons[i + 1] if i + 1 < len(self.horizons) else self.bottom
        pts = list(zip(self.xs, top)) + list(zip(self.xs[::-1], bot[::-1]))
        return poly(pts, close=True)

    def z_at(self, i, x):
        return float(np.interp(x, self.xs, self.horizons[i]))


class SceneImpl(Scene):
    id = "s00_open"
    chapter_card = False
    bg = "default"

    def setup(self):
        self.world = World()
        self.layer_paths = [self.world.layer_path(i) for i in range(len(STRATIGRAPHY))]
        res_i = next(i for i, L in enumerate(STRATIGRAPHY) if L.lith == "reservoir")
        self.res_i = res_i
        # hydrocarbon column: from reservoir top down to OWC (oil-water contact) and GOC (gas-oil)
        self.owc = WATER + 3000 + 150   # m below sea level (crest at 3300)
        self.goc = WATER + 3000 + 45
        rnd = np.random.default_rng(11)
        self.snow = [(rnd.uniform(-1, 1), rnd.uniform(0, 1), rnd.uniform(0.6, 2.0), rnd.uniform(0, 6.28)) for _ in range(160)]
        # main well trajectory (x, z), from platform at x=0
        pts = []
        for z in np.linspace(-20, 3000 + WATER + 30, 160):
            kop = 1200.0
            if z < kop:
                x = 0.0
            else:
                x = 380 * ((z - kop) / (3330 - kop)) ** 1.6
            pts.append((x, z))
        self.well_pts = pts
        self.well_path = poly(pts)
        # other wells from the same platform (fan)
        self.others = []
        for k, (dx, kop) in enumerate([(-1500, 700), (-900, 900), (-400, 1500), (900, 800), (1600, 600), (2300, 500), (-2100, 500)]):
            pp = []
            for z in np.linspace(-20, 3000 + WATER + 60, 120):
                x = 0.0 if z < kop else dx * ((z - kop) / (3360 - kop)) ** 1.25
                zz = z
                pp.append((x, zz))
            self.others.append(poly(pp))
        self.agenda = [
            ("Regulations and standards", "regulations"),
            ("Barrier philosophy", "barrier philosophy"),
            ("Verification and monitoring", "verified"),
            ("Classification", "classified"),
            ("When barriers fail", "goes wrong"),
            ("Plug and abandonment", "plug and abandonment"),
            ("CO₂ storage and the future", "industry is learning"),
        ]

    # ------------------------------------------------------------------ camera
    def camera(self, t):
        # (center_x, center_z, view_height)
        k0 = (40.0, -20.0, 230.0)
        k1 = (300.0, 1820.0, 4300.0)
        k2 = (330.0, 2950.0, 1900.0)
        a = self.c0("sea") + 0.6
        e1 = ease_in_out(clamp((t - a) / 7.5))
        cx = lerp(k0[0], k1[0], e1)
        cz = lerp(k0[1], k1[1], e1)
        hh = math.exp(lerp(math.log(k0[2]), math.log(k1[2]), e1))
        # follow the well down during 'well' then back out during 'life'
        e2 = ease_in_out(clamp((t - (self.c0("well") - 0.5)) / 4.0)) * (1 - ease_in_out(clamp((t - (self.c0("life") + 0.3)) / 4.5)))
        cx = lerp(cx, k2[0], e2)
        cz = lerp(cz, k2[1], e2)
        hh = math.exp(lerp(math.log(hh), math.log(k2[2]), e2))
        # slow drift afterwards
        drift = max(0.0, t - self.c0("title"))
        cz += drift * 6
        hh *= 1 + drift * 0.002
        return cx, cz, hh

    # ------------------------------------------------------------------ drawing
    def draw(self, c, t):
        cx, cz, hh = self.camera(t)
        s = H / hh
        dim = 1.0 - 0.62 * ease_in_out(clamp((t - self.c0("title") + 0.6) / 1.4))
        c.save()
        c.translate(W / 2, H / 2)
        c.scale(s, s)
        c.translate(-cx, -cz)
        self.draw_world(c, t, s, cx, cz, hh)
        c.restore()
        if dim < 1.0:
            c.drawRect(skia.Rect(0, 0, W, H), paint(C.bg0, 1.0 - dim))
        self.draw_ui(c, t, s, cx, cz, hh)

    def draw_world(self, c, t, s, cx, cz, hh):
        px = 1.0 / s  # one screen pixel in world units
        x0, x1 = cx - (W / 2) * px - 50, cx + (W / 2) * px + 50
        z0, z1 = cz - (H / 2) * px - 50, cz + (H / 2) * px + 50
        # sky
        if z0 < 0:
            sp = skia.Paint()
            sp.setShader(skia.GradientShader.MakeLinear([skia.Point(0, -320), skia.Point(0, 0)],
                                                        [rgb("#0A1630"), rgb("#2A2350"), rgb("#B4566A"), rgb("#F2A35E")],
                                                        [0.0, 0.55, 0.88, 1.0]))
            c.drawRect(skia.Rect(x0, min(z0, -400), x1, 0), sp)
            # sun glow on horizon
            gp = skia.Paint()
            gp.setShader(skia.GradientShader.MakeRadial(skia.Point(-260, 0), 300, [with_alpha(rgb("#FFD8A0"), 0.55), with_alpha(rgb("#FFD8A0"), 0)]))
            c.drawRect(skia.Rect(x0, -400, x1, 0), gp)
        # water
        if z0 < WATER:
            wp = skia.Paint()
            wp.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, WATER)],
                                                        [rgb("#1C5C78"), rgb("#0E3550"), rgb("#071A2C")], [0, 0.35, 1]))
            c.drawRect(skia.Rect(x0, 0, x1, WATER + 10), wp)
            # light rays
            for k in range(7):
                bx = -300 + k * 140 + 30 * math.sin(t * 0.3 + k)
                ray = poly([(bx, 0), (bx + 40, 0), (bx + 160, WATER), (bx + 60, WATER)], close=True)
                rp = skia.Paint(AntiAlias=True)
                rp.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, WATER)],
                                                            [with_alpha(rgb("#9FE3FF"), 0.10 + 0.04 * math.sin(t + k)), with_alpha(rgb("#9FE3FF"), 0)]))
                c.drawPath(ray, rp)
            # marine snow
            for (u, v, r, ph) in self.snow:
                xx = cx + u * (W / 2) * px
                zz = (v * WATER + t * 3 + ph * 10) % WATER
                c.drawCircle(xx + 3 * math.sin(t + ph), zz, r * px, paint(rgb("#CFEFFF"), 0.35))
        # strata: flat colour + soft texture + depth shading
        for i, L in enumerate(STRATIGRAPHY):
            pth = self.layer_paths[i]
            c.drawPath(pth, paint(LITH_COLORS[L.lith]))
            m = skia.Matrix()
            m.setScaleTranslate(0.9, 0.9, 0, 0)
            tp = skia.Paint(AntiAlias=True, Shader=lith_texture(L.lith).makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat,
                                                                                   skia.SamplingOptions(skia.FilterMode.kLinear), m))
            tp.setAlphaf(0.5)
            c.drawPath(pth, tp)
            ztop = float(np.mean(self.world.horizons[i]))
            zbot = float(np.mean(self.world.horizons[i + 1])) if i + 1 < len(STRATIGRAPHY) else ztop + 400
            sh = skia.Paint(AntiAlias=True)
            sh.setShader(skia.GradientShader.MakeLinear([skia.Point(0, ztop - 150), skia.Point(0, zbot + 150)],
                                                        [with_alpha(C.white, 0.06), with_alpha(C.black, 0.0), with_alpha(C.black, 0.28)],
                                                        [0, 0.45, 1]))
            c.drawPath(pth, sh)
            c.drawPath(pth, paint(C.black, 0.35, stroke=1.6 * px))
        # hydrocarbons in the reservoir crest (clip to reservoir layer)
        c.save()
        c.clipPath(self.layer_paths[self.res_i], skia.ClipOp.kIntersect, True)
        oil = skia.Paint()
        oil.setShader(skia.GradientShader.MakeLinear([skia.Point(0, self.goc), skia.Point(0, self.owc)],
                                                     [with_alpha(rgb("#E3A13A"), 0.55), with_alpha(rgb("#B5651D"), 0.65)]))
        c.drawRect(skia.Rect(-6000, WATER + 2900, 6000, self.owc), oil)
        c.drawRect(skia.Rect(-6000, WATER + 2900, 6000, self.goc), paint(rgb("#FFE29A"), 0.45))
        c.drawRect(skia.Rect(-6000, self.owc, 6000, WATER + 3600), paint(rgb("#2E6E8E"), 0.45))
        pulse = 0.5 + 0.5 * math.sin(t * 1.6)
        c.drawRect(skia.Rect(-6000, WATER + 2900, 6000, self.owc), paint(rgb("#FFC266"), 0.10 + 0.08 * pulse))
        c.restore()
        # fluid contacts
        if hh < 5000:
            c.save()
            c.clipPath(self.layer_paths[self.res_i], skia.ClipOp.kIntersect, True)
            for zc, col in ((self.goc, rgb("#FFE29A")), (self.owc, rgb("#7CC4E6"))):
                dp = paint(col, 0.6, stroke=2 * px, cap=skia.Paint.kButt_Cap)
                dp.setPathEffect(skia.DashPathEffect.Make([14 * px, 10 * px], 0))
                xl = -2400
                c.drawLine(xl, zc, -xl, zc, dp)
            c.restore()
        # sea surface waves
        if z0 < 20:
            wv = skia.Path()
            wv.moveTo(x0, 0)
            xx = x0
            while xx <= x1:
                wv.lineTo(xx, 1.2 * math.sin(xx * 0.08 + t * 1.8) + 0.7 * math.sin(xx * 0.21 - t * 1.1))
                xx += max(2.0, 6 * px)
            c.drawPath(wv, paint(rgb("#BFEFFF"), 0.75, stroke=1.6 * px))
        # other wells (portfolio)
        k_oth = ease_in_out(clamp((t - self.at("life", 0.15)) / 3.0))
        if k_oth > 0:
            for i, pth in enumerate(self.others):
                kk = clamp(k_oth * 1.4 - i * 0.06)
                glow_path(c, trim_path(pth, 0, kk), rgb("#7FB7FF"), 3.2 * px, 0.45 * kk, glow=6 * px)
        # platform
        self.draw_platform(c, t, px)
        # main well
        kw = ease_in_out(clamp((t - self.c0("well")) / 4.2))
        if kw > 0:
            pth = trim_path(self.well_path, 0, kw)
            glow_path(c, pth, rgb("#A9DBFF"), 5.5 * px, 1.0, glow=12 * px, core_color=C.white)
            (hx, hz), _ = path_point(self.well_path, kw)
            c.drawCircle(hx, hz, 9 * px, paint(C.white, 0.9 * (1 - ease_in_out(clamp((kw - 0.97) / 0.03)) * 0.5)))
            c.drawCircle(hx, hz, 22 * px, paint(rgb("#A9DBFF"), 0.35, blur=10 * px))

    def draw_platform(self, c, t, px):
        steel = rgb("#5C6878")
        steel_hi = rgb("#AEB9C7")
        # jacket (legs from seabed to deck)
        top_w, bot_w = 60, 110
        legs = [(-top_w / 2, -bot_w / 2), (-top_w / 6, -bot_w / 6), (top_w / 6, bot_w / 6), (top_w / 2, bot_w / 2)]
        jp = paint(steel, 1.0, stroke=max(1.2 * px, 2.2))
        for (xt, xb) in legs:
            c.drawLine(xt, -18, xb, WATER, jp)
        # bracing
        levels = np.linspace(-18, WATER, 7)
        for a, b in zip(levels[:-1], levels[1:]):
            fa, fb = (a + 18) / (WATER + 18), (b + 18) / (WATER + 18)
            wa, wb = lerp(top_w, bot_w, fa) / 2, lerp(top_w, bot_w, fb) / 2
            c.drawLine(-wa, a, wb, b, paint(steel, 0.8, stroke=max(0.9 * px, 1.2)))
            c.drawLine(wa, a, -wb, b, paint(steel, 0.8, stroke=max(0.9 * px, 1.2)))
            c.drawLine(-wb, b, wb, b, paint(steel, 0.8, stroke=max(0.9 * px, 1.2)))
        # topsides
        deck = skia.Rect(-46, -44, 46, -18)
        c.drawRect(deck, paint(rgb("#2B3442")))
        for k in range(5):
            mx = -44 + k * 18
            c.drawRect(skia.Rect(mx, -42 + (k % 2) * 4, mx + 15, -20), paint(rgb("#3B4656")))
            for wx in range(3):
                c.drawRect(skia.Rect(mx + 2 + wx * 4.5, -36 + (k % 2) * 4, mx + 4.5 + wx * 4.5, -34 + (k % 2) * 4),
                           paint(rgb("#FFD27A"), 0.75 + 0.25 * math.sin(t * 2 + k + wx)))
        # derrick
        der = poly([(-30, -44), (-24, -96), (-18, -44)], close=False)
        c.drawPath(der, paint(steel_hi, 1, stroke=max(1.0 * px, 1.6)))
        for k in range(6):
            yy = -44 - k * 8.5
            ww = 6 - k * 0.9
            c.drawLine(-24 - ww, yy, -24 + ww, yy - 8.5, paint(steel_hi, 0.7, stroke=max(0.6 * px, 0.8)))
        # helideck
        c.drawRect(skia.Rect(26, -50, 52, -46), paint(rgb("#3E4A5A")))
        # flare boom with flame
        c.drawLine(46, -40, 96, -78, paint(steel_hi, 1, stroke=max(1.0 * px, 1.6)))
        fl = 6 + 1.5 * math.sin(t * 9) + math.sin(t * 13.7)
        c.drawCircle(98, -82, fl * 2.2, paint(rgb("#FF8A3D"), 0.35, blur=fl * 1.4))
        c.drawCircle(98, -82, fl, paint(rgb("#FFC266"), 0.95, blur=fl * 0.35))
        # conductor/well slot through the jacket
        c.drawLine(0, -18, 0, WATER, paint(rgb("#8FA0B4"), 0.9, stroke=max(1.0 * px, 1.4)))

    # ------------------------------------------------------------------ UI
    def draw_ui(self, c, t, s, cx, cz, hh):
        # depth ruler (right)
        a_r = window(t, self.c0("sea") + 2.5, self.c0("title") - 0.5, 1.0, 0.8)
        if a_r > 0:
            xr = W - 90
            for d in range(0, 4001, 500):
                z = WATER + d
                y = H / 2 + (z - cz) * s
                if 40 < y < H - 40:
                    c.drawLine(xr, y, xr + 14, y, paint(C.muted, 0.8 * a_r, stroke=1.4))
                    draw_text(c, f"{d:,} m".replace(",", " "), xr - 8, y + 6, 17, C.muted, 500, a_r, "right")
            ys = H / 2 + (WATER - cz) * s
            if 40 < ys < H - 40:
                draw_text(c, "seabed", xr - 8, ys - 14, 15, C.dim, 500, a_r, "right")
        # bottom scrim for captions
        a_s = window(t, self.c0("sea") + 0.3, self.c0("title") - 0.4, 1.0, 0.8)
        if a_s > 0:
            sp = skia.Paint()
            sp.setShader(skia.GradientShader.MakeLinear([skia.Point(0, H - 330), skia.Point(0, H)],
                                                        [with_alpha(C.bg0, 0), with_alpha(C.bg0, 0.78 * a_s)]))
            c.drawRect(skia.Rect(0, H - 330, W, H), sp)
        # formation names during the descent
        a_f = window(t, self.c0("sea") + 3.0, self.c0("well") + 2.5, 1.0, 1.0)
        if a_f > 0:
            for i, L in enumerate(STRATIGRAPHY):
                zt = WATER + L.top
                zb = WATER + L.base
                ym = H / 2 + ((zt + zb) / 2 - cz) * s
                if 120 < ym < H - 200 and (zb - zt) * s > 46:
                    draw_text(c, L.group, 96, ym, 22, C.text, 600, 0.9 * a_f, shadow=True)
                    draw_text(c, L.name, 96, ym + 24, 17, C.muted, 400, 0.9 * a_f, shadow=True)
        # captions during the descent
        a1 = window(t, self.c0("sea") + 0.3, self.c0("well") - 0.2, 1.0, 0.8)
        if a1 > 0:
            draw_text(c, "THE NORTH SEA", 96, H - 150, 20, C.muted, 600, a1, tracking=5)
            draw_text(c, "Norwegian Continental Shelf", 96, H - 108, 40, C.text, 600, a1, display=True)
        # reservoir callout
        a2 = window(t, self.at("sea", 0.75), self.c0("life") + 2.0, 0.8, 0.8)
        if a2 > 0:
            zx, zz = -900.0, WATER + 3060
            sx_, sy_ = W / 2 + (zx - cx) * s, H / 2 + (zz - cz) * s
            if 0 < sy_ < H:
                c.drawCircle(sx_, sy_, 6, paint(C.amber, a2))
                c.drawLine(sx_, sy_, sx_ - 120, sy_ - 90, paint(C.amber, 0.8 * a2, stroke=1.6))
                draw_text(c, "Reservoir", sx_ - 130, sy_ - 128, 30, C.text, 600, a2, "right", display=True)
                draw_text(c, "oil and gas at several hundred bar", sx_ - 130, sy_ - 98, 20, C.muted, 400, a2, "right")
            # cap rock label
            zc = WATER + 2850
            yc = H / 2 + (zc - cz) * s
            if 0 < yc < H:
                draw_text(c, "Cap rock", W / 2 + (1600 - cx) * s, yc + 6, 20, C.text, 600, a2 * 0.9, shadow=True)
        # well label
        a3 = window(t, self.c0("well") + 1.0, self.c0("title") - 0.4, 0.8, 0.8)
        if a3 > 0:
            draw_text(c, "A well: the engineered path", 96, H - 150, 20, C.muted, 600, a3, tracking=3)
            draw_text(c, "between the reservoir and the world above", 96, H - 108, 34, C.text, 500, a3, display=True)
        # life cycle bar
        a4 = window(t, self.c0("life"), self.c0("title") - 0.2, 0.8, 0.8)
        if a4 > 0:
            x0, y0, wbar = 480, 150, 960
            k = ease_out(clamp((t - self.c0("life")) / 6.0))
            draw_text(c, "THE LIFE OF A WELL", W / 2, y0 - 40, 18, C.muted, 600, a4, "center", tracking=5)
            c.drawRoundRect(skia.Rect(x0 - 40, y0 - 78, x0 + wbar + 110, y0 + 70), 18, 18, paint(C.bg0, 0.72 * a4))
            segs = [(0.0, 0.14, "Drill & complete", C.teal), (0.14, 0.56, "Production · decades", C.primary),
                    (0.56, 0.70, "Plug & abandon", C.amber), (0.70, 1.0, "Abandoned · forever", rgb("#8E9AF0"))]
            for (f0, f1, lab, col) in segs:
                kk = clamp((k - f0) / (f1 - f0))
                if kk <= 0:
                    continue
                xa = x0 + f0 * wbar
                xb = x0 + (f0 + (f1 - f0) * kk) * wbar
                c.drawRoundRect(skia.Rect(xa + 2, y0, xb - 2, y0 + 14), 7, 7, paint(col, 0.9 * a4))
                if kk > 0.5:
                    draw_text(c, lab, (x0 + (f0 + f1) / 2 * wbar), y0 + 46, 20, C.text, 500, a4 * clamp((kk - 0.5) * 2), "center")
            if k > 0.9:
                icon(c, "infinity", x0 + wbar + 50, y0 + 7, 54, C.text, a4 * clamp((k - 0.9) * 10), rgb("#8E9AF0"))
        # title
        a5 = window(t, self.c0("title") - 0.3, self.c0("agenda") - 0.1, 1.0, 0.9)
        k5 = ease_out_quint(clamp((t - self.c0("title") + 0.3) / 1.6))
        if a5 > 0:
            c.save()
            c.translate(0, (1 - k5) * 24)
            draw_text(c, "WELL INTEGRITY", W / 2, H / 2 + 10, 132, C.text, 700, a5, "center", display=True, tracking=10)
            lw = 900 * k5
            c.drawLine(W / 2 - lw / 2, H / 2 + 52, W / 2 + lw / 2, H / 2 + 52, paint(C.primary, 0.9 * a5, stroke=3))
            c.drawLine(W / 2 - lw / 2, H / 2 + 52, W / 2 + lw / 2, H / 2 + 52, paint(C.primary, 0.5 * a5, stroke=10, blur=8))
            draw_text(c, "Barriers, verification and life-cycle management on the Norwegian Continental Shelf",
                      W / 2, H / 2 + 108, 30, C.muted, 400, a5 * ease_out(clamp((t - self.c0("title")) / 1.4)), "center")
            c.restore()
        # agenda
        a6 = window(t, self.c0("agenda") - 0.3, self.dur, 0.9, 0.5)
        if a6 > 0:
            draw_text(c, "WELL INTEGRITY", W / 2, 150, 44, C.text, 700, a6, "center", display=True, tracking=6)
            c.drawLine(W / 2 - 160, 176, W / 2 + 160, 176, paint(C.primary, 0.8 * a6, stroke=2))
            draw_text(c, "IN THIS FILM", W / 2, 236, 18, C.muted, 600, a6, "center", tracking=5)
            cols = 2
            bw, bh = 660, 92
            gx = 40
            x_start = W / 2 - (cols * bw + (cols - 1) * gx) / 2
            for i, (lab, kw) in enumerate(self.agenda):
                r, k = divmod(i, cols)
                if i == len(self.agenda) - 1:
                    k = 0
                    x = W / 2 - bw / 2
                else:
                    x = x_start + k * (bw + gx)
                y = 290 + r * (bh + 22)
                ti = self.word_time("agenda", kw) - 0.3
                if i == len(self.agenda) - 1:
                    ti = self.word_time("agenda", "plug and abandonment") + 1.6
                if i == 0:
                    ti = min(ti, self.c0("agenda") + 0.2)
                kk = ease_out(clamp((t - ti) / 0.8))
                hot = window(t, ti, ti + 2.2, 0.3, 0.8)
                if kk <= 0:
                    continue
                c.save()
                c.translate(0, (1 - kk) * 20)
                col = mix(C.panel, C.panel_hi, hot)
                c.drawRoundRect(skia.Rect(x, y, x + bw, y + bh), 16, 16, paint(col, 0.9 * kk * a6))
                c.drawRoundRect(skia.Rect(x, y, x + bw, y + bh), 16, 16, paint(mix(C.line, C.primary, hot), kk * a6, stroke=1.5))
                draw_text(c, f"{i + 1:02d}", x + 34, y + bh / 2 + 12, 32, C.primary, 300, kk * a6, display=True)
                draw_text(c, lab, x + 100, y + bh / 2 + 11, 32, C.text, 500, kk * a6, display=True)
                c.restore()
