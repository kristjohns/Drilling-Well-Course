"""Chapter 3: Barrier philosophy - concepts, drilling well, production well."""
from __future__ import annotations

import math

import numpy as np
import skia

from engine.core import (C, W, H, arrow, chip, clamp, draw_panel, draw_paragraph, draw_text, ease_in_out, ease_out,
                         ease_out_back, glow_path, lerp, mix, paint, poly, rgb, trim_path, window, with_alpha, rrect,
                         path_point, make_particles, prog, font)
from engine.scene import Scene
from engine.widgets import icon, bullets, Plot, gauge, stamp
from engine.well import (WellView, WellState, draw_formation, draw_well, draw_surface, draw_bop, draw_tree,
                         draw_wellhead, draw_tubing_hanger, region_casing, region_cement, region_formation,
                         highlight_path, highlight, draw_rcd, draw_pce, depth_scale, cement_texture)
from engine.core import image_shader

G = 0.0981  # bar per metre per SG


def pore_emw(d):
    if d < 2000:
        return 1.03
    if d < 3000:
        return 1.03 + 0.15 * (d - 2000) / 1000
    return 1.18


def frac_emw(d):
    return float(np.interp(d, [0, 500, 1800, 3000, 3400], [1.30, 1.45, 1.62, 1.75, 1.77]))


class SceneImpl(Scene):
    id = "s03_barriers"

    def setup(self):
        rnd = np.random.default_rng(7)
        self.src_particles = [(rnd.uniform(-1, 1), rnd.uniform(0, 1), rnd.uniform(2, 4.5)) for _ in range(70)]
        self.circ = [(rnd.uniform(0, 1), rnd.uniform(-1, 1), rnd.uniform(1.2, 2.6)) for _ in range(120)]
        self.bubbles = [(rnd.uniform(0, 1), rnd.uniform(-1, 1), rnd.uniform(0.7, 1.3), rnd.uniform(0, 1)) for _ in range(60)]
        self.oil = [(rnd.uniform(-1, 1), rnd.uniform(0, 1)) for _ in range(50)]

    # ================================================================== top level
    def draw(self, c, t):
        if t < self.c0("drilling") + 0.5:
            self.draw_concepts(c, t)
        if t > self.c0("drilling") - 1.0:
            self.draw_well_part(c, t)

    # ================================================================== part A: concepts
    def env_geom(self, cx=960, top=380, bot=830, half=70, wall=16, cem=26):
        return dict(cx=cx, top=top, bot=bot, half=half, wall=wall, cem=cem)

    def draw_concepts(self, c, t):
        a_all = window(t, self.c0("barrier") - 0.4, self.c0("drilling") - 0.4, 0.8, 0.7)
        if a_all <= 0:
            return
        # ------------------------------------------------ definition banner
        a_def = self.vis(t, "barrier", "element", fi=0.6, fo=0.5, b_off=-0.3) * a_all
        if a_def > 0:
            draw_text(c, "WELL BARRIER", 160, 210, 20, C.primary, 700, a_def, tracking=5)
            draw_paragraph(c, "An envelope of one or several well barrier elements preventing fluids from flowing "
                           "unintentionally from a formation into the wellbore, into another formation, or to the "
                           "external environment.", 160, 262, 560, 32, C.text, 500, a_def, display=True,
                           reveal=clamp((t - self.c0("barrier")) / 12.0))
        # ------------------------------------------------ scene geometry
        if t < self.c0("two") - 0.2:
            self.draw_single_envelope(c, t, a_all)
        else:
            self.draw_double_envelope(c, t, a_all)

    def draw_rock(self, c, x0, x1, y0, y1, a, label=True):
        from engine.well import lith_texture
        p = skia.Paint(Shader=image_shader(lith_texture("caprock"), 0.6))
        p.setAlphaf(a)
        c.drawRect(skia.Rect(x0, y0, x1, y1), p)
        if label:
            draw_text(c, "Cap rock", x1 - 16, y0 + 34, 22, C.text, 600, a * 0.9, "right", shadow=True)

    def draw_source(self, c, cx, y, w, a, t):
        res = skia.Paint()
        res.setShader(skia.GradientShader.MakeRadial(skia.Point(cx, y), w,
                                                     [with_alpha(C.amber, 0.9 * a), with_alpha(rgb("#B5651D"), 0.75 * a),
                                                      with_alpha(rgb("#B5651D"), 0.0)], [0, 0.6, 1]))
        c.drawOval(skia.Rect(cx - w, y - w * 0.32, cx + w, y + w * 0.32), res)
        draw_text(c, "Source: reservoir under pressure", cx, y + w * 0.32 + 40, 24, C.amber, 600, a, "center")

    def draw_single_envelope(self, c, t, a_all):
        cx, top, bot, half, wall, cem = 1260, 330, 800, 64, 14, 26
        t0 = self.c0("barrier")
        tE = self.c0("element")
        a = a_all
        # rock and source
        self.draw_rock(c, 900, 1620, bot - 30, bot + 40, a)
        self.draw_source(c, cx, bot + 130, 260, a, t)
        c.drawRect(skia.Rect(cx - half, bot + 40, cx + half, bot + 110), paint(rgb("#1E1A16"), a))
        # element fly-in progress (assembled during 'barrier'); during 'element' the cement & valve are removed then return
        def fly(i):
            return ease_out(clamp((t - t0 - 2.0 - i * 1.2) / 1.4))
        k_cas, k_cem, k_val = fly(0), fly(1), fly(2)
        # during 'element': remove cement and valve, then restore
        rem = ease_in_out(clamp((t - tE - 0.2) / 1.0)) * (1 - ease_in_out(clamp((t - self.at("element", 0.62)) / 1.2)))
        k_cem2 = k_cem * (1 - rem)
        k_val2 = k_val * (1 - rem)
        # casing walls
        for side in (-1, 1):
            off = (1 - k_cas) * 500 * side
            x_o = cx + side * half + off
            r = skia.Rect(min(x_o, x_o - side * wall), top, max(x_o, x_o - side * wall), bot + 40)
            from engine.well import steel_paint
            c.drawRect(r, steel_paint(r.left(), r.right(), a * clamp(k_cas * 2)))
        # cement sheath
        if k_cem2 > 0:
            cp = skia.Paint(Shader=image_shader(cement_texture(), 0.5))
            cp.setAlphaf(a * k_cem2)
            for side in (-1, 1):
                yy = (1 - k_cem2) * 300
                x_o = cx + side * half
                r = skia.Rect(min(x_o, x_o + side * cem), top + yy, max(x_o, x_o + side * cem), bot + 40 + yy)
                c.drawRect(r, cp)
        # valve on top
        if k_val2 > 0:
            yv = top - 30 - (1 - k_val2) * 200
            vr = skia.Rect(cx - half - 26, yv, cx + half + 26, yv + 46)
            from engine.well import steel_paint
            c.drawRoundRect(vr, 8, 8, steel_paint(vr.left(), vr.right(), a * k_val2))
            c.drawCircle(cx, yv + 23, 7, paint(C.red, a * k_val2))
            c.drawLine(cx, yv, cx, yv - 26, paint(C.steel_hi, a * k_val2, stroke=4))
            c.drawLine(cx - 30, yv - 26, cx + 30, yv - 26, paint(C.steel_hi, a * k_val2, stroke=4))
        # labels
        labs = [("Casing", k_cas, cx + half + 80, 470), ("Cement", k_cem2, cx + half + 80, 640), ("Valve", k_val2, cx + half + 80, top - 6),
                ("Cap rock", 0, 0, 0)]
        for (lab, k, lx, ly) in labs[:3]:
            if k > 0.6:
                al = a * clamp((k - 0.6) * 2.5)
                c.drawLine(cx + half + (cem if lab != "Valve" else 30), ly - 8, lx - 10, ly - 8, paint(C.muted, al, stroke=1.4))
                draw_text(c, lab, lx, ly, 28, C.text, 600, al)
        closed = k_cas * k_cem2 * k_val2
        # fluid particles from the source
        ph = t * 0.25
        for (u, v_, r) in self.src_particles:
            life = (v_ + ph) % 1.0
            x = cx + u * (half - wall - 6)
            y = bot + 100 - life * (bot + 100 - top)
            esc = 0.0
            if closed < 0.98 and y < top + 40:
                # escaping through the open top
                y = top + 40 - (top + 40 - y) * 1.6
                x = cx + u * (half - wall) * (1 + (top + 40 - y) / 120)
            if closed > 0.98:
                # pool below the valve
                y = max(y, top + 20 + (1 - u * u) * 30 + 40 * (1 - life))
            c.drawCircle(x, y, r, paint(C.amber, 0.75 * a))
        # leak around the outside when no cement
        if rem > 0.2:
            for k in range(14):
                life = ((t * 0.3 + k / 14) % 1.0)
                for side in (-1, 1):
                    x = cx + side * (half + 10)
                    y = bot + 30 - life * (bot - top + 60)
                    c.drawCircle(x, y, 3.5, paint(C.red, 0.85 * a * rem))
            draw_text(c, "A component alone is not a barrier", 160, 700, 34, C.red, 600, a * rem, display=True)
        # envelope outline when closed
        if closed > 0.95 and t > t0 + 9:
            ke = ease_in_out(clamp((t - max(t0 + 9, self.at("element", 0.75))) / 2.0)) if t > tE else ease_in_out(clamp((t - t0 - 9) / 2.5))
            pth = poly([(cx - half - cem, bot - 10), (cx - half - cem, top - 34), (cx + half + cem, top - 34), (cx + half + cem, bot - 10)])
            glow_path(c, trim_path(pth, 0, ke), C.primary, 5, a, glow=14)
            if t > tE + 1:
                kk = ease_out(clamp((t - self.at("element", 0.7)) / 1.0))
                draw_text(c, "Only the complete, closed envelope", 160, 700, 34, C.primary_hi, 600, a * kk, display=True)
                draw_text(c, "is a barrier", 160, 746, 34, C.primary_hi, 600, a * kk, display=True)

    def draw_double_envelope(self, c, t, a_all):
        cx, bot = 1260, 800
        a = a_all * window(t, self.c0("two") - 0.2, self.c0("drilling") - 0.6, 0.6, 0.6)
        if a <= 0:
            return
        self.draw_rock(c, 900, 1620, bot - 30, bot + 40, a)
        self.draw_source(c, cx, bot + 130, 260, a, t)
        c.drawRect(skia.Rect(cx - 50, bot + 40, cx + 50, bot + 110), paint(rgb("#1E1A16"), a))
        k_in = ease_out(clamp((t - self.c0("two") - 0.3) / 1.2))
        k_out = ease_out(clamp((t - self.word_time("two", "secondary") + 0.2) / 1.2))
        fail = ease_in_out(clamp((t - self.at("two", 0.85)) / 1.2))
        inner = poly([(cx - 60, bot - 10), (cx - 60, 470), (cx + 60, 470), (cx + 60, bot - 10)])
        outer = poly([(cx - 150, bot - 10), (cx - 150, 330), (cx + 150, 330), (cx + 150, bot - 10)])
        # secondary first (behind)
        if k_out > 0:
            c.drawRect(skia.Rect(cx - 150, 330, cx + 150, bot - 10), paint(C.secondary, 0.06 * a * k_out))
            glow_path(c, trim_path(outer, 0, k_out), C.secondary, 5, a, glow=14)
            draw_text(c, "Secondary well barrier", cx + 175, 360, 30, C.secondary_hi, 600, a * k_out, display=True)
            draw_text(c, "takes over if the primary fails", cx + 175, 396, 22, C.muted, 400, a * k_out)
        if k_in > 0:
            col = mix(C.primary, C.red, fail)
            glow_path(c, trim_path(inner, 0, k_in), col, 5, a, glow=14)
            draw_text(c, "Primary well barrier", cx - 180, 500, 30, C.primary_hi, 600, a * k_in, "right", display=True)
            draw_text(c, "first envelope against flow from the source", cx - 180, 536, 22, C.muted, 400, a * k_in, "right")
        # particles
        ph = t * 0.25
        for (u, v_, r) in self.src_particles:
            life = (v_ + ph) % 1.0
            x = cx + u * 44
            y = bot + 100 - life * (bot + 100 - 470)
            y = max(y, 490 + 30 * (1 - life))
            if fail > 0.3:
                # leak through the crack into the space between envelopes
                lf = (v_ * 1.7 + ph * 1.3) % 1.0
                xx = cx + 62 + lf * 70 * (0.5 + abs(u))
                yy = 560 - lf * 210 + u * 30
                c.drawCircle(xx, max(yy, 352), r * 0.9, paint(C.amber, 0.75 * a * fail))
            c.drawCircle(x, y, r, paint(C.amber, 0.75 * a))
        if fail > 0:
            # crack flash
            c.drawCircle(cx + 60, 560, 26 * fail, paint(C.red, 0.4 * a * fail, blur=10))
            draw_text(c, "primary fails", cx + 75, 600, 22, C.red, 600, a * fail)
        # common element
        a_c = self.vis(t, "common", "drilling", fi=0.6, fo=0.5, b_off=-0.6) * a_all
        if a_c > 0:
            c.drawRect(skia.Rect(cx - 160, bot - 34, cx + 160, bot - 6), paint(C.common, 0.55 * a_c))
            c.drawRect(skia.Rect(cx - 160, bot - 34, cx + 160, bot - 6), paint(C.common, a_c, stroke=2))
            c.drawRect(skia.Rect(cx - 160, bot - 34, cx + 160, bot - 6), paint(C.common, 0.4 * a_c, blur=10))
            draw_text(c, "Common well barrier element", 160, 720, 36, C.common, 600, a_c, display=True)
            draw_text(c, "part of both envelopes: the extra risk", 160, 766, 28, C.text, 400, a_c)
            draw_text(c, "must be assessed and mitigated", 160, 804, 28, C.text, 400, a_c)
            c.drawLine(cx - 165, bot - 20, 900, 760, paint(C.common, 0.7 * a_c, stroke=1.5))
        # independence principle text
        a_t = self.vis(t, "two", "common", fi=0.6, fo=0.5, b_off=-0.3) * a_all
        if a_t > 0:
            draw_text(c, "THE TWO-BARRIER PRINCIPLE", 160, 260, 20, C.primary, 700, a_t, tracking=4)
            draw_paragraph(c, "Two independent, tested well barriers between the source and the environment.", 160, 320,
                           620, 40, C.text, 600, a_t, display=True)

    # ================================================================== part B/C: the well
    def view(self, t):
        k_int = ease_in_out(clamp((t - self.c0("intervention") + 0.2) / 1.6))
        return WellView(axis_x=560, y_top=lerp(400, 600, k_int), y_bot=1032, sx=7.6, x_left=170, x_right=950)

    def state(self, t):
        st = WellState()
        k_prod = ease_in_out(clamp((t - self.c0("production") + 0.3) / 5.2))
        self.k_prod = k_prod
        # drilling configuration -> completed configuration
        st.show_strings = {"liner": clamp(k_prod * 2)}
        st.string_extent = {"liner": ease_in_out(clamp(k_prod * 1.6))}
        st.cement_fill = {"liner": clamp((k_prod - 0.45) * 3)}
        st.hole_td = lerp(3150, 3330, clamp(k_prod * 2.5))
        st.drillstring = 1.0 - clamp(k_prod * 3)
        st.bit_depth = 3150 - 3150 * ease_in_out(clamp(k_prod * 3)) if k_prod > 0 else 3150
        st.rotation = t * 0.8
        st.completion = clamp((k_prod - 0.5) * 2)
        st.a_annulus_fluid = C.brine if k_prod > 0.95 else None
        st.perforations = clamp((k_prod - 0.85) * 6)
        mud = C.mud
        # MPD lighter mud
        k_mpd = self.vis(t, "mpd", "production", fi=0.8, fo=0.6, b_off=-0.6)
        if k_mpd > 0:
            mud = mix(C.mud, rgb("#A58A68"), k_mpd)
        st.bore_fluid = mix(mud, C.oil, clamp((k_prod - 0.7) * 3.3))
        st.annulus_fluid = C.mud
        st.surface = "bop" if k_prod < 0.5 else "tree"
        st.surface_alpha = 1.0 - clamp(k_prod * 4) if k_prod < 0.5 else clamp((k_prod - 0.6) * 3)
        # kick / losses
        tk = self.c0("kick")
        lvl = 420 * ease_in_out(clamp((t - self.word_time("kick", "losses")) / 2.5))
        lvl *= 1 - ease_in_out(clamp((t - self.word_time("shutin", "closes")) / 0.8))
        st.fluid_level = lvl
        # BOP close
        st.bop_close = ease_in_out(clamp((t - self.word_time("shutin", "closes")) / 1.2)) * (1 - ease_in_out(clamp((t - self.c0("mpd") + 0.5) / 1.0)))
        # kill mud fronts
        tkill = self.word_time("shutin", "circulating")
        f1 = clamp((t - tkill) / 3.5)        # down the drill pipe
        f2 = clamp((t - tkill - 3.5) / 4.5)  # up the annulus
        fade_kill = 1 - ease_in_out(clamp((t - self.c0("mpd") + 0.8) / 1.0))
        if f1 > 0 and fade_kill > 0:
            st.overlays.append(dict(kind="dp", d0=0, d1=3150 * f1, color=C.kill_mud, alpha=0.95 * fade_kill))
            if f2 > 0:
                st.overlays.append(dict(kind="bore", d0=3150 * (1 - f2), d1=3150, color=C.kill_mud, alpha=0.95 * fade_kill,
                                        keep_dp=None))
                st.overlays.append(dict(kind="dp", d0=0, d1=3150, color=C.kill_mud, alpha=0.95 * fade_kill))
        self.kill = (f1, f2, fade_kill)
        # DHSV closing in the dhsv beat
        tclose = self.word_time("dhsv", "if that pressure") + 0.4
        st.dhsv_open = 1 - ease_in_out(clamp((t - tclose) / 1.6)) * (1 - ease_in_out(clamp((t - self.c0("secondary_prod")) / 1.0)))
        return st

    def draw_well_part(self, c, t):
        a = window(t, self.c0("drilling") - 0.6, self.dur, 0.9, 0.5)
        if a <= 0:
            return
        v = self.view(t)
        st = self.state(t)
        c.save()
        c.clipRect(skia.Rect(150, 90, 970, 1045))
        draw_formation(c, v, alpha=a, reservoir_glow=0.6)
        draw_well(c, v, st, t, a)
        # circulation particles (drilling)
        self.draw_circulation(c, t, v, st, a)
        self.draw_kick(c, t, v, st, a)
        top = draw_surface(c, v, st, a)
        if st.surface == "bop" and self.vis(t, "mpd", "production", fi=0.6, fo=0.4, b_off=-0.5) > 0:
            draw_rcd(c, v, top, a * self.vis(t, "mpd", "production", fi=0.6, fo=0.4, b_off=-0.5))
        if t > self.c0("intervention") - 0.2:
            kp = ease_out(clamp((t - self.c0("intervention") - 0.8) / 1.2))
            if kp > 0:
                tool = 300 + 1100 * ease_in_out(clamp((t - self.c0("intervention") - 2.5) / 6.0))
                ytree_top = v.y(0) - 46 - 4 * 48 - 18
                draw_pce(c, v, ytree_top, a * kp, tool_depth=tool)
        self.draw_well_highlights(c, t, v, st, a)
        c.restore()
        depth_scale(c, v, 150 + 0, alpha=0)  # (kept off: busy)
        self.draw_right_panel(c, t, v, st, a)

    # ------------------------------------------------------------------ particles
    def draw_circulation(self, c, t, v, st, a):
        k = st.drillstring * (1 - self.vis(t, "shutin", "mpd", fi=0.3, fo=0.6, a_off=0.6, b_off=-0.3)) * window(t, self.c0("drilling"), self.c0("production"), 0.6, 0.6)
        if k <= 0:
            return
        bit = st.bit_depth
        for (u, x_, r) in self.circ:
            life = (u + t * 0.07) % 1.0
            if x_ < 0:
                # down the drill pipe
                d = life * bit
                x = v.ax + (x_ + 0.5) * v.r(4.0)
                col = rgb("#E3C9A3")
            else:
                # up the annulus
                d = bit - life * bit
                if d < st.fluid_level:
                    continue
                side = 1 if x_ > 0.5 else -1
                rr = v.r(5.5) + 3 + (x_ % 0.5) * 2 * (v.r(8.5) - v.r(5.5) - 6)
                x = v.ax + side * rr
                col = rgb("#6B4F35")
            c.drawCircle(x, v.y(d), r, paint(col, 0.85 * a * k))

    def draw_kick(self, c, t, v, st, a):
        tin = self.word_time("kick", "formation fluid") - 0.3
        if t < tin or t > self.c0("mpd") + 1.0:
            return
        f2 = self.kill[1]
        fade = (1 - ease_in_out(clamp((f2 - 0.6) / 0.4))) * self.kill[2] if f2 > 0 else 1.0
        fade *= 1 - ease_in_out(clamp((t - self.c0("mpd")) / 1.0))
        n = int(len(self.bubbles) * clamp((t - tin) / 6.0))
        bit = 3150.0
        closed = st.bop_close
        for i in range(n):
            u, x_, sz, ph = self.bubbles[i]
            # rising speed reduces when shut in (gas migration is slow), increases when circulating out
            age = (t - tin) - u * 6.0
            if age < 0:
                continue
            speed = 260.0 if closed < 0.5 else 60.0
            if self.kill[1] > 0:
                speed = 420.0
            d = bit - age * speed
            d = max(d, 40 + ph * 300)
            p_here = 1 + G * 1.3 * d
            p_bit = 1 + G * 1.3 * bit
            rad = 3.4 * sz * (p_bit / p_here) ** (1 / 3) * 1.4
            side = 1 if x_ > 0 else -1
            rr = v.r(5.5) + 4 + abs(x_) * (v.r(8.5) - v.r(5.5) - 8)
            x = v.ax + side * rr
            y = v.y(d)
            c.drawCircle(x, y, rad, paint(C.gas, 0.85 * a * fade))
            c.drawCircle(x - rad * 0.3, y - rad * 0.3, rad * 0.35, paint(C.white, 0.6 * a * fade))
        # losses arrows into weak zone below the shoe
        kl = self.vis(t, "kick", "shutin", fi=0.4, fo=0.6, a_off=self.word_time("kick", "losses") - self.c0("kick"))
        if kl > 0:
            for k in range(3):
                y = v.y(2985 + k * 12)
                for side in (-1, 1):
                    x0 = v.ax + side * v.r(8.5)
                    off = ((t * 1.4 + k * 0.3) % 1.0) * 40
                    arrow(c, x0 + side * off, y, x0 + side * (off + 26), y, rgb("#C9A27A"), 2.5, a * kl, head=9)

    # ------------------------------------------------------------------ highlights
    def draw_well_highlights(self, c, t, v, st, a):
        # primary barrier: fluid column during drilling
        a_fc = self.vis(t, "drilling", "kick", fi=0.8, fo=0.6, a_off=1.5)
        a_fc = max(a_fc, self.vis(t, "shutin", "production", fi=0.8, fo=0.6, a_off=self.word_time("shutin", "restored") - self.c0("shutin")))
        if a_fc > 0 and "bore_fluid" in v.regions:
            highlight_path(c, v.regions["bore_fluid"], C.primary, a * a_fc * 0.75, fill=0.35)
        # secondary during drilling
        a_sd = self.vis(t, "secondary_drill", "production", fi=0.6, fo=0.6, a_off=0.0, b_off=-0.6)
        a_sd *= 1.0 - 0.6 * ease_in_out(clamp((t - self.c1("secondary_drill") - 0.5) / 1.0))
        if a_sd > 0:
            items = [("formation", self.word_time("secondary_drill", "formation")),
                     ("cement", self.word_time("secondary_drill", "casing cement")),
                     ("casing", self.word_time("secondary_drill", "the casing,")),
                     ("wellhead", self.word_time("secondary_drill", "wellhead")),
                     ("bop", self.word_time("secondary_drill", "blowout"))]
            for key, ti in items:
                k = ease_out(clamp((t - ti + 0.2) / 0.6)) * a_sd * a
                if k <= 0:
                    continue
                if key == "formation":
                    highlight_path(c, region_formation(v, st, "liner", 2952, 3010, width=34), C.secondary, k)
                elif key == "cement":
                    highlight_path(c, region_cement(v, st, "prod", 2350, 2950), C.secondary, k)
                elif key == "casing":
                    highlight_path(c, region_casing(v, st, "prod", 0, 2950), C.secondary, k)
                elif key == "wellhead":
                    highlight(c, v, "wellhead", C.secondary, k)
                elif key == "bop":
                    highlight(c, v, "bop", C.secondary, k, fill=0.22)
        # production: primary
        a_pp = self.vis(t, "primary_prod", "intervention", fi=0.6, fo=0.6, a_off=-0.2, b_off=0.2)
        if a_pp > 0:
            P = st.packer_depth
            groups = [
                (self.word_time("primary_prod", "casing and cement"), [region_casing(v, st, "prod", P, 2950), region_cement(v, st, "prod", P, 2950),
                                                                       region_casing(v, st, "liner", 2850, 3035), region_cement(v, st, "liner", 2850, 3000)]),
                (self.word_time("primary_prod", "packer itself"), ["packer", "liner_top_packer"]),
                (self.word_time("primary_prod", "tubing"), ["tubing"]),
                (self.word_time("primary_prod", "safety valve"), ["dhsv"]),
            ]
            for ti, regs in groups:
                k = ease_out(clamp((t - ti + 0.1) / 0.6)) * a_pp * a
                for r in regs:
                    if isinstance(r, str):
                        highlight(c, v, r, C.primary, k)
                    else:
                        highlight_path(c, r, C.primary, k)
        a_sp = self.vis(t, "secondary_prod", "intervention", fi=0.6, fo=0.6, a_off=-0.2, b_off=0.2)
        if a_sp > 0:
            P = st.packer_depth
            groups = [
                (self.word_time("secondary_prod", "cap rock"), [region_formation(v, st, "prod", 2350, P, width=30), region_cement(v, st, "prod", 2350, P)]),
                (self.word_time("secondary_prod", "production casing"), [region_casing(v, st, "prod", 0, P)]),
                (self.word_time("secondary_prod", "wellhead"), ["wellhead"]),
                (self.word_time("secondary_prod", "tubing hanger"), ["tubing_hanger"]),
                (self.word_time("secondary_prod", "annulus valves"), ["annulus_valve"]),
                (self.word_time("secondary_prod", "master valve"), ["lmv"]),
            ]
            for ti, regs in groups:
                k = ease_out(clamp((t - ti + 0.1) / 0.6)) * a_sp * a
                for r in regs:
                    if isinstance(r, str):
                        highlight(c, v, r, C.secondary, k)
                    else:
                        highlight_path(c, r, C.secondary, k)
        # envelope outlines for the WBS beat
        a_env = self.vis(t, "wbs", None, fi=0.6, fo=0.6, b_off=60)
        if a_env > 0:
            ke = ease_in_out(clamp((t - self.c0("wbs") - 0.3) / 2.5))
            ax = v.ax
            yD, yP = v.y(st.dhsv_depth), v.y(st.packer_depth)
            for side in (-1, 1):
                blue = poly([(ax, yD), (ax + side * v.r(4.5), yD), (ax + side * v.r(4.5), yP - 12), (ax + side * v.r(12.25) + side * 2, yP - 12),
                             (ax + side * v.r(12.25) + side * 2, v.y(2950)), (ax + side * v.r(8.5) + side * 2, v.y(2950)),
                             (ax + side * v.r(8.5) + side * 2, v.y(3000))])
                glow_path(c, trim_path(blue, 0, ke), C.primary, 3.5, a * a_env, glow=10)
                yL = v.y(0) - 46 - 21
                tw = v.r(9.0) + 18
                red = poly([(ax, yL), (ax + side * (tw + 4), yL), (ax + side * (tw + 4), v.y(0) - 50), (ax + side * (v.r(30) + 20), v.y(0) - 50),
                            (ax + side * (v.r(30) + 20), v.y(0) + 8), (ax + side * v.r(9.625) + side * 2, v.y(0) + 8),
                            (ax + side * v.r(9.625) + side * 2, v.y(2350)), (ax + side * v.r(12.25) + side * 2, v.y(2350)),
                            (ax + side * v.r(12.25) + side * 2, yP - 14)])
                glow_path(c, trim_path(red, 0, ke), C.secondary, 3.5, a * a_env, glow=10)

    # ------------------------------------------------------------------ right panel
    def draw_right_panel(self, c, t, v, st, a):
        X0 = 1030
        # ---- drilling: primary label
        a1 = self.vis(t, "drilling", "hydro", fi=0.6, fo=0.5, a_off=0.5, b_off=-0.2)
        if a1 > 0:
            draw_text(c, "DRILLING", X0, 250, 20, C.muted, 700, a1, tracking=5)
            draw_text(c, "Primary barrier:", X0, 330, 44, C.text, 600, a1, display=True)
            draw_text(c, "the fluid column", X0, 386, 44, C.primary_hi, 600, a1, display=True)
            draw_paragraph(c, "The weight of the mud holds back the formation pressure. Mud is pumped down the drill "
                           "pipe and returns up the annulus with the cuttings.", X0, 470, 760, 28, C.muted, 400, a1)
        # ---- pressure-depth plot (hydro, lot, kick, mpd)
        a_pl = max(self.vis(t, "hydro", "secondary_drill", fi=0.7, fo=0.6, b_off=-0.3),
                   self.vis(t, "kick", "mpd", fi=0.6, fo=0.6, b_off=-0.3),
                   self.vis(t, "mpd", "production", fi=0.6, fo=0.6, b_off=-0.5))
        if a_pl > 0:
            self.draw_pd_plot(c, t, a_pl * a)
        # ---- secondary labels (drilling)
        a_sd = self.vis(t, "secondary_drill", "lot", fi=0.6, fo=0.5, b_off=-0.3)
        if a_sd > 0:
            draw_text(c, "Secondary barrier", X0, 300, 44, C.secondary_hi, 600, a_sd, display=True)
            items = ["In-situ formation at the casing shoe", "Casing cement", "Casing", "Wellhead", "Blowout preventer (BOP)"]
            kws = ["formation", "casing cement", "the casing,", "wellhead", "blowout"]
            times = [self.word_time("secondary_drill", kw) - 0.2 for kw in kws]
            bullets(c, items, X0, 400, t, times, size=32, max_w=760, alpha=a_sd, accent=C.secondary, gap=1.8)
        # ---- leak-off test
        a_lot = self.vis(t, "lot", "kick", fi=0.6, fo=0.6, b_off=-0.3)
        if a_lot > 0:
            self.draw_lot(c, t, v, st, a_lot * a)
        # ---- shut-in gauges
        a_si = self.vis(t, "shutin", "mpd", fi=0.5, fo=0.6, a_off=self.word_time("shutin", "closes") - self.c0("shutin") + 0.8, b_off=-0.4)
        if a_si > 0:
            # pressure gauges near the BOP
            gauge(c, 1540, 820, 50, 12 * ease_out(clamp((t - self.word_time("shutin", "closes") - 1) / 2)), 0, 60, "Drill pipe", "bar", a_si,
                  color=C.primary)
            gauge(c, 1740, 820, 50, 28 * ease_out(clamp((t - self.word_time("shutin", "closes") - 1) / 2)), 0, 60, "Casing", "bar", a_si,
                  color=C.amber)
        # ---- kick text
        a_k = self.vis(t, "kick", "mpd", fi=0.5, fo=0.5, b_off=-0.3)
        if a_k > 0:
            lines = [("Losses lower the mud level", self.word_time("kick", "losses") - 0.3, C.text),
                     ("Hydrostatic falls below pore pressure", self.word_time("kick", "losses") + 1.5, C.text),
                     ("Influx: gas expands as it rises", self.word_time("kick", "gas expands") - 0.4, C.gas),
                     ("BOP closed: secondary barrier holds", self.word_time("shutin", "closes") - 0.2, C.secondary_hi),
                     ("Circulate out, kill mud restores primary", self.word_time("shutin", "circulating") - 0.2, C.primary_hi)]
            for i, (txt, ti, col) in enumerate(lines):
                kk = ease_out(clamp((t - ti) / 0.6)) * a_k
                if kk > 0:
                    draw_text(c, "●  " + txt, 1450, 300 + i * 46, 22, col, 600, kk)
            # pit gain
            pg = 3.2 * ease_out(clamp((t - self.word_time("kick", "formation fluid")) / 6.0))
            kk = ease_out(clamp((t - self.word_time("kick", "formation fluid")) / 0.6)) * a_k
            if kk > 0:
                draw_text(c, "PIT GAIN", 1460, 580, 18, C.muted, 600, kk, tracking=4)
                draw_text(c, f"+{pg:.1f} m³", 1460, 640, 54, C.gas, 700, kk, display=True)
        # ---- MPD text
        a_m = self.vis(t, "mpd", "production", fi=0.5, fo=0.5, b_off=-0.6)
        if a_m > 0:
            draw_text(c, "MANAGED PRESSURE DRILLING", 1460, 300, 18, C.teal, 700, a_m, tracking=3)
            draw_paragraph(c, "Lighter mud, a closed system and surface back-pressure from a choke keep the bottom-hole "
                           "pressure inside the window.", 1460, 350, 400, 25, C.text, 400, a_m)
            chip(c, 1460, 520, "Expanded in D-010 rev. 5", C.teal, a_m, size=20)
            gauge(c, 1560, 700, 52, 25, 0, 60, "Surface back-pressure", "bar", a_m, color=C.teal)
        # ---- production: element lists
        a_p = self.vis(t, "production", "primary_prod", fi=0.6, fo=0.5, a_off=0.5, b_off=-0.2)
        if a_p > 0:
            draw_text(c, "COMPLETED AND PRODUCING", X0, 300, 20, C.muted, 700, a_p, tracking=5)
            draw_text(c, "The envelopes are now hardware", X0, 370, 44, C.text, 600, a_p, display=True)
        a_pl = self.vis(t, "primary_prod", "dhsv", fi=0.6, fo=0.5, b_off=-0.3)
        if a_pl > 0:
            draw_text(c, "Primary well barrier", X0, 300, 44, C.primary_hi, 600, a_pl, display=True)
            items = ["Casing and cement below the production packer", "Production packer", "Production tubing", "Downhole safety valve (DHSV)"]
            kws = ["casing and cement", "packer itself", "tubing", "safety valve"]
            times = [self.word_time("primary_prod", kw) - 0.2 for kw in kws]
            bullets(c, items, X0, 400, t, times, size=32, max_w=780, alpha=a_pl, accent=C.primary, gap=1.8)
        a_dh = self.vis(t, "dhsv", "secondary_prod", fi=0.6, fo=0.6, b_off=-0.3)
        if a_dh > 0:
            self.draw_dhsv_detail(c, t, a_dh * a)
        a_sl = self.vis(t, "secondary_prod", "wbs", fi=0.6, fo=0.5, b_off=-0.3)
        if a_sl > 0:
            draw_text(c, "Secondary well barrier", X0, 260, 44, C.secondary_hi, 600, a_sl, display=True)
            items = ["Cap rock (in-situ formation)", "Casing cement above the reservoir", "Production casing", "Wellhead",
                     "Tubing hanger", "Annulus valves", "Master valve on the Christmas tree"]
            kws = ["cap rock", "casing cement", "production casing", "wellhead", "tubing hanger", "annulus valves", "master valve"]
            times = [self.word_time("secondary_prod", kw) - 0.2 for kw in kws]
            bullets(c, items, X0, 350, t, times, size=30, max_w=780, alpha=a_sl, accent=C.secondary, gap=1.62)
        a_w = self.vis(t, "wbs", "eac", fi=0.6, fo=0.5, b_off=-0.3)
        if a_w > 0:
            self.draw_wbs_sheet(c, t, a_w)
        a_e = self.vis(t, "eac", "intervention", fi=0.6, fo=0.5, b_off=-0.3)
        if a_e > 0:
            self.draw_eac(c, t, a_e)
        a_i = self.vis(t, "intervention", None, fi=0.6, fo=0.5, b_off=4)
        if a_i > 0:
            draw_text(c, "WELL INTERVENTION", X0, 300, 20, C.muted, 700, a_i, tracking=5)
            draw_paragraph(c, "Wireline or coiled tubing: the pressure control equipment on top of the tree becomes part "
                           "of the barrier envelopes.", X0, 370, 800, 36, C.text, 500, a_i, display=True)
            labels = [("Stuffing box / grease head", 0), ("Lubricator", 1), ("Wireline BOP", 2)]
            for txt, i in labels:
                kk = ease_out(clamp((t - self.c0("intervention") - 2.0 - i * 0.8) / 0.6)) * a_i
                if kk > 0:
                    draw_text(c, "●  " + txt, X0, 560 + i * 48, 28, C.text, 500, kk)
            ks = ease_out(clamp((t - self.word_time("intervention", "updated schematic")) / 0.8))
            stamp(c, X0 + 300, 820, "SCHEMATIC UPDATED", C.green, ks * a_i, size=30)

    # ------------------------------------------------------------------ plots
    def draw_pd_plot(self, c, t, a):
        pl = Plot(1080, 220, 680, 720, (0, 600), (0, 3300), invert_y=True, xlabel="Pressure (bar)", ylabel="Depth (m)",
                  xticks=[0, 100, 200, 300, 400, 500, 600], yticks=[0, 500, 1000, 1500, 2000, 2500, 3000])
        if t > self.c0("kick") - 0.5:
            pl = Plot(1080, 220, 340, 720, (0, 600), (0, 3300), invert_y=True, xlabel="Pressure (bar)", ylabel="Depth (m)",
                      xticks=[0, 200, 400, 600], yticks=[0, 1000, 2000, 3000])
        pl.axes(c, a)
        ds = np.linspace(0, 3300, 67)
        k = ease_in_out(clamp((t - self.c0("hydro") - 0.3) / 2.5))
        pore = [pore_emw(d) * G * d for d in ds]
        frac = [frac_emw(d) * G * d for d in ds]
        pl.line(c, pore, ds, C.amber, 3, a, reveal=k, glow=False, dash=[10, 7])
        pl.line(c, frac, ds, C.red, 3, a, reveal=ease_in_out(clamp((t - self.c0("hydro") - 1.0) / 2.5)), glow=False, dash=[10, 7])
        mw = 1.30
        lvl = 0.0
        sbp = 0.0
        k_mpd = self.vis(t, "mpd", "production", fi=0.8, fo=0.6, b_off=-0.6)
        if t > self.c0("kick"):
            lvl = 420 * ease_in_out(clamp((t - self.word_time("kick", "losses")) / 2.5)) * (1 - ease_in_out(clamp((t - self.word_time("shutin", "closes")) / 0.8)))
        mw = lerp(mw, 1.15, k_mpd)
        sbp = 25 * k_mpd
        mud = [max(0.0, mw * G * (d - lvl)) + sbp for d in ds]
        kmud = ease_in_out(clamp((t - self.word_time("hydro", "mud with") + 0.2) / 2.5))
        pl.line(c, mud, ds, C.primary, 4, a, reveal=kmud)
        # labels
        if t < self.c0("kick") - 0.5:
            la = a * ease_out(clamp((t - self.c0("hydro") - 2.0) / 1.0))
            draw_text(c, "Pore pressure", pl.px(pore[-12]) - 10, pl.py(ds[-12]) + 64, 20, C.amber, 600, la, "right")
            draw_text(c, "Fracture pressure", pl.px(frac[-20]) + 8, pl.py(ds[-20]) - 18, 20, C.red, 600, la)
            lm = a * kmud
            draw_text(c, "Mud hydrostatic", pl.px(mud[-30]) + 12, pl.py(ds[-30]) - 10, 20, C.primary_hi, 600, lm)
            # formula + numbers
            kf = ease_out(clamp((t - self.word_time("hydro", "hydrostatic pressure equals") + 0.2) / 0.8))
            draw_panel(c, 1220, 240, 520, 160, a * kf, r=14)
            draw_text(c, "P = ρ · g · h", 1250, 300, 40, C.text, 600, a * kf, display=True)
            kn = ease_out(clamp((t - self.word_time("hydro", "one point three")) / 0.8))
            draw_text(c, "1.30 SG · 3 000 m  →  ≈ 383 bar", 1250, 356, 26, C.primary_hi, 600, a * kn)
            kp = ease_out(clamp((t - self.word_time("hydro", "pore pressure")) / 0.8))
            if kp > 0:
                y3 = pl.py(3000)
                c.drawCircle(pl.px(1.30 * G * 3000), y3, 7, paint(C.primary_hi, a * kp))
                c.drawCircle(pl.px(1.18 * G * 3000), y3, 7, paint(C.amber, a * kp))
                draw_text(c, "≈ 350 bar pore", pl.px(1.18 * G * 3000) - 14, y3 + 34, 20, C.amber, 600, a * kp, "right")
                draw_text(c, "overbalance", pl.px(1.24 * G * 3000), y3 - 16, 18, C.text, 500, a * kp, "center")
        else:
            # kick: show underbalance at bit
            yb = pl.py(3150)
            kk = ease_out(clamp((t - self.word_time("kick", "losses") - 1.5) / 0.6)) * (1 - ease_in_out(clamp((t - self.word_time("shutin", "closes")) / 0.8)))
            if kk > 0:
                c.drawCircle(pl.px(pore_emw(3150) * G * 3150), yb, 8, paint(C.gas, a * kk))
                draw_text(c, "underbalanced", pl.px(300), yb + 40, 18, C.gas, 700, a * kk, "center")

    def draw_lot(self, c, t, v, st, a):
        # magnifier of the shoe
        mx, my, mr = 1250, 380, 170
        c.save()
        clip = skia.Path()
        clip.addCircle(mx, my, mr)
        c.clipPath(clip, skia.ClipOp.kIntersect, True)
        c.drawCircle(mx, my, mr, paint(C.bg0))
        mv = WellView(axis_x=mx, y_top=my - mr * 3.1, y_bot=my + mr * 1.35, sx=15, knots_d=(2900, 3000), knots_f=(0.70, 1.0),
                      x_left=mx - mr, x_right=mx + mr)
        mv.y_top, mv.y_bot = my - mr, my + mr
        mv.kd = np.array([0, 2850, 3050, 3400.0])
        mv.kf = np.array([-20.0, 0.0, 1.0, 2.75])
        ms = WellState()
        ms.show_strings = {"liner": 0.0}
        ms.hole_td = 2958 + 22 * ease_out(clamp((t - self.c0("lot") - 2.0) / 2.0))
        ms.bore_fluid = C.mud
        draw_formation(c, mv, alpha=a)
        draw_well(c, mv, ms, t, a)
        # pressure arrows and fracture
        kpr = ease_in_out(clamp((t - self.word_time("lot", "pressured up")) / 3.0))
        kfr = ease_out(clamp((t - self.word_time("lot", "begins to take")) / 1.0))
        for k in range(4):
            yy = mv.y(2960 + k * 5)
            for side in (-1, 1):
                x0 = mx + side * mv.r(8.5)
                arrow(c, x0 - side * 18, yy, x0 + side * (4 + 10 * kpr), yy, C.primary_hi, 2.4, a * kpr, head=8)
        if kfr > 0:
            for side in (-1, 1):
                x0 = mx + side * mv.r(8.5)
                fr = poly([(x0, mv.y(2970)), (x0 + side * 30 * kfr, mv.y(2968)), (x0 + side * 70 * kfr, mv.y(2972)), (x0 + side * 110 * kfr, mv.y(2969))])
                c.drawPath(fr, paint(C.primary_hi, a * kfr, stroke=2.5))
        c.restore()
        c.drawCircle(mx, my, mr, paint(C.primary, 0.9 * a, stroke=3))
        draw_text(c, "9⅝ in shoe", mx, my + mr + 34, 22, C.text, 600, a, "center")
        draw_text(c, "a few meters of new hole", mx, my + mr + 62, 18, C.muted, 400, a, "center")
        # LOT plot
        pl = Plot(1500, 230, 320, 300, (0, 10), (0, 180), xlabel="Volume pumped", ylabel="", xticks=[], yticks=[])
        pl.axes(c, a, grid=False)
        draw_text(c, "Surface pressure", 1500, 214, 18, C.muted, 600, a)
        kk = ease_in_out(clamp((t - self.word_time("lot", "pressured up")) / 6.0))
        xs = np.linspace(0, 10, 80)
        ys = []
        for x in xs:
            if x < 5.5:
                ys.append(26 * x)
            elif x < 7.0:
                ys.append(143 + 14 * (x - 5.5) - 6 * (x - 5.5) ** 2)
            else:
                ys.append(150 - 22 * (x - 7.0))
        pl.line(c, xs, ys, C.primary_hi, 3.5, a, reveal=kk)
        if kk > 0.6:
            ka = ease_out(clamp((kk - 0.6) * 4))
            c.drawCircle(pl.px(5.5), pl.py(143), 7, paint(C.amber, a * ka))
            draw_text(c, "leak-off", pl.px(5.5) - 12, pl.py(143) - 14, 18, C.amber, 700, a * ka, "right")
        # explanation
        kx = ease_out(clamp((t - self.word_time("lot", "sets the upper")) / 0.8))
        draw_panel(c, 1050, 640, 790, 240, a * kx, r=14)
        draw_paragraph(c, "The leak-off pressure sets the limit for the mud weight, and for the pressure the secondary "
                       "barrier can hold at the shoe.", 1080, 700, 730, 28, C.text, 500, a * kx)
        draw_text(c, "Formation integrity test (FIT): pressure to a set limit", 1080, 820, 21, C.muted, 400, a * kx)
        draw_text(c, "Leak-off test (LOT): until the rock begins to take fluid", 1080, 852, 21, C.muted, 400, a * kx)

    # ------------------------------------------------------------------ DHSV detail
    def draw_dhsv_detail(self, c, t, a):
        x0, y0 = 1080, 200
        draw_text(c, "DOWNHOLE SAFETY VALVE", x0, y0, 20, C.primary, 700, a, tracking=4)
        draw_text(c, "Fail-safe closed", x0, y0 + 56, 44, C.text, 600, a, display=True)
        y0 += 0
        cx = 1450
        top, bot = 300, 980
        tclose = self.word_time("dhsv", "if that pressure") + 0.4
        kc = ease_in_out(clamp((t - tclose) / 1.6))      # 0 open -> 1 closed
        hyd = 1 - ease_in_out(clamp((t - tclose + 0.6) / 0.8))
        bw = 64          # bore half width
        hw = 150         # housing half width
        # housing
        from engine.well import steel_paint
        for side in (-1, 1):
            xo = cx + side * hw
            c.drawRect(skia.Rect(min(xo, xo - side * 26), 420, max(xo, xo - side * 26), 900), steel_paint(min(xo, xo - side * 26), max(xo, xo - side * 26), a))
            # tubing above/below
            xt = cx + side * (bw + 18)
            c.drawRect(skia.Rect(min(xt, xt - side * 14), top, max(xt, xt - side * 14), 420), steel_paint(min(xt, xt - side * 14), max(xt, xt - side * 14), a))
            c.drawRect(skia.Rect(min(xt, xt - side * 14), 900, max(xt, xt - side * 14), bot), steel_paint(min(xt, xt - side * 14), max(xt, xt - side * 14), a))
            c.drawRect(skia.Rect(min(cx + side * (bw + 18), cx + side * hw), 410, max(cx + side * (bw + 18), cx + side * hw), 430), steel_paint(cx - hw, cx + hw, a))
            c.drawRect(skia.Rect(min(cx + side * (bw + 18), cx + side * hw), 890, max(cx + side * (bw + 18), cx + side * hw), 910), steel_paint(cx - hw, cx + hw, a))
        # bore fluid
        c.drawRect(skia.Rect(cx - bw - 4, top, cx + bw + 4, bot), paint(C.oil, 0.55 * a))
        # flow tube (moves up when closing)
        dy = -185 * kc
        ft_top, ft_bot = 560 + dy, 860 + dy
        for side in (-1, 1):
            xo = cx + side * (bw + 4)
            c.drawRect(skia.Rect(min(xo, xo - side * 10), ft_top, max(xo, xo - side * 10), ft_bot), steel_paint(min(xo, xo - side * 10), max(xo, xo - side * 10), a, tint=C.primary))
        # piston shoulder on flow tube
        c.drawRect(skia.Rect(cx - hw + 26, ft_top + 40, cx - bw - 4, ft_top + 60), paint(rgb("#4C5B70"), a))
        # power spring between shoulder and housing bottom
        sy0, sy1 = ft_top + 60, 870
        spring = skia.Path()
        n = 12
        xa, xb = cx - hw + 34, cx - bw - 12
        spring.moveTo(xa, sy0)
        for k in range(n):
            yy = sy0 + (k + 0.5) * (sy1 - sy0) / n
            spring.lineTo(xb if k % 2 == 0 else xa, yy)
        spring.lineTo(xa, sy1)
        c.drawPath(spring, paint(C.steel_hi, 0.9 * a, stroke=3))
        spring2 = skia.Path()
        xa2, xb2 = cx + hw - 34, cx + bw + 12
        spring2.moveTo(xa2, sy0)
        for k in range(n):
            yy = sy0 + (k + 0.5) * (sy1 - sy0) / n
            spring2.lineTo(xb2 if k % 2 == 0 else xa2, yy)
        spring2.lineTo(xa2, sy1)
        c.drawPath(spring2, paint(C.steel_hi, 0.9 * a, stroke=3))
        c.drawRect(skia.Rect(cx + bw + 4, ft_top + 40, cx + hw - 26, ft_top + 60), paint(rgb("#4C5B70"), a))
        # hydraulic chamber above the piston and control line
        if ft_top + 40 > 432:
            c.drawRect(skia.Rect(cx - hw + 26, 430, cx - bw - 4, ft_top + 40), paint(C.teal, 0.55 * a * hyd + 0.08 * a))
        cl = poly([(cx - hw + 40, 430), (cx - hw + 40, 380), (cx - hw - 40, 380), (cx - hw - 40, top - 20)])
        c.drawPath(cl, paint(C.teal, a * (0.35 + 0.65 * hyd), stroke=5))
        # flapper: hinge at right below flow tube
        hx, hy = cx + bw + 2, 820
        ang = math.radians(-90 + 90 * kc)  # -90 = vertical up (open, behind tube) ; 0 = horizontal (closed)
        L = 2 * bw + 2
        fx, fy = hx - L * math.cos(ang) * 0 + (-L) * math.sin(-ang) * 0, 0
        # direction: open = pointing up along the wall; closed = pointing left across the bore
        dxv, dyv = -math.cos(math.radians(90 * kc - 90)) * 0, 0
        theta = math.radians(90 - 90 * kc)  # 90 -> up, 0 -> left
        ex = hx - L * math.cos(theta)
        ey = hy - L * math.sin(theta)
        c.drawLine(hx, hy, ex, ey, paint(C.amber, a, stroke=9))
        c.drawCircle(hx, hy, 8, paint(C.steel_hi, a))
        # flow particles
        for (u, v_) in self.oil:
            life = (v_ + t * (0.35 * (1 - kc))) % 1.0
            y = bot - life * (bot - top)
            if kc > 0.6 and y < hy + 10:
                y = hy + 14 + (1 - life) * 20
            c.drawCircle(cx + u * (bw - 14), y, 4, paint(C.amber, 0.8 * a))
        # labels
        def lab(txt, x, y, tx, ty, k=1.0):
            kk = a * k
            c.drawLine(x, y, tx, ty, paint(C.muted, 0.7 * kk, stroke=1.4))
            c.drawCircle(x, y, 4, paint(C.muted, kk))
            draw_text(c, txt, tx + 8, ty + 7, 22, C.text, 600, kk)
        kl = ease_out(clamp((t - self.c0("dhsv") - 0.8) / 1.0))
        lab("Control line (hydraulic pressure)", cx - hw - 40, 330, cx + 40, 250, kl)
        lab("Piston and flow tube", cx - bw - 10, ft_top + 50, cx + hw + 40, 470, kl)
        lab("Power spring", cx + hw - 50, 700, cx + hw + 40, 620, kl)
        lab("Flapper", hx + 4, hy, cx + hw + 40, 820, kl)
        state_txt = "OPEN · held by hydraulic pressure" if kc < 0.5 else "CLOSED · spring and well pressure"
        chip(c, x0, 995, state_txt, C.green if kc < 0.5 else C.red, a, size=22)

    # ------------------------------------------------------------------ WBS / EAC
    def draw_wbs_sheet(self, c, t, a):
        x, y, w, h = 1020, 170, 850, 840
        draw_panel(c, x, y, w, h, a)
        c.drawRect(skia.Rect(x, y, x + w, y + 70), paint(C.panel_hi, a))
        draw_text(c, "WELL BARRIER SCHEMATIC", x + 30, y + 46, 24, C.text, 700, a, tracking=3)
        draw_text(c, "Production well · illustrative", x + w - 30, y + 46, 20, C.muted, 500, a, "right")
        prim = ["Casing cement below packer", "Production casing / liner below packer", "Production packer", "Completion string (tubing)",
                "Downhole safety valve"]
        sec = ["In-situ formation (cap rock)", "Casing cement", "Production casing", "Wellhead", "Tubing hanger", "Annulus valves",
               "Christmas tree master valve"]
        ka = ease_out(clamp((t - self.c0("wbs") - 0.5) / 0.8))
        draw_text(c, "PRIMARY WELL BARRIER", x + 30, y + 120, 20, C.primary, 700, a * ka, tracking=3)
        for i, it in enumerate(prim):
            kk = ease_out(clamp((t - self.c0("wbs") - 0.8 - i * 0.25) / 0.5)) * a
            c.drawRect(skia.Rect(x + 30, y + 140 + i * 46, x + 36, y + 172 + i * 46), paint(C.primary, kk))
            draw_text(c, it, x + 52, y + 165 + i * 46, 24, C.text, 500, kk)
        draw_text(c, "SECONDARY WELL BARRIER", x + 30, y + 420, 20, C.secondary, 700, a * ka, tracking=3)
        for i, it in enumerate(sec):
            kk = ease_out(clamp((t - self.c0("wbs") - 2.0 - i * 0.25) / 0.5)) * a
            c.drawRect(skia.Rect(x + 30, y + 440 + i * 46, x + 36, y + 472 + i * 46), paint(C.secondary, kk))
            draw_text(c, it, x + 52, y + 465 + i * 46, 24, C.text, 500, kk)
        kf = ease_out(clamp((t - self.word_time("wbs", "formation strength")) / 0.6)) * a
        c.drawLine(x + 30, y + 785, x + w - 30, y + 785, paint(C.line, kf, stroke=1))
        draw_text(c, "Formation strength at 9⅝ in shoe: 1.74 SG EMW · status: verified", x + 30, y + 820, 21, C.green, 600, kf)

    def draw_eac(self, c, t, a):
        x, y, w, h = 1020, 170, 850, 840
        draw_panel(c, x, y, w, h, a)
        c.drawRect(skia.Rect(x, y, x + w, y + 70), paint(C.panel_hi, a))
        draw_text(c, "ELEMENT ACCEPTANCE TABLE", x + 30, y + 46, 24, C.text, 700, a, tracking=3)
        draw_text(c, "example: production packer", x + w - 30, y + 46, 20, C.muted, 500, a, "right")
        rows = [
            ("Function", "Seals the annulus between tubing and casing, stopping flow from the reservoir into the A-annulus."),
            ("Design and selection", "Rated for the maximum differential pressure, temperature and well fluids it will see."),
            ("Initial test and verification", "Pressure tested in the direction of flow before it is accepted."),
            ("Use", "Operated within its rated envelope."),
            ("Monitoring", "A-annulus pressure monitored continuously."),
            ("Failure modes", "Leak past the sealing element; loss of anchoring."),
        ]
        kws = ["function", "designed", "tested and verified", "how it must be monitored", "monitored", "maintained"]
        for i, (k_, v_) in enumerate(rows):
            ti = self.c0("eac") + 0.8 + i * 1.6
            kk = ease_out(clamp((t - ti) / 0.6)) * a
            yy = y + 110 + i * 118
            c.drawLine(x + 30, yy - 30, x + w - 30, yy - 30, paint(C.line, 0.6 * kk, stroke=1))
            draw_text(c, k_, x + 30, yy + 4, 22, C.primary_hi, 700, kk)
            draw_paragraph(c, v_, x + 300, yy + 4, w - 340, 23, C.text, 400, kk, leading=1.3)
        draw_text(c, "Structure as in NORSOK D-010 element acceptance tables · wording illustrative", x + 30, y + h - 26, 17,
                  C.dim, 500, a)
