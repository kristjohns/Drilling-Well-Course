"""Ch 4, beat 4.04: why jars, and how a wire hammers.

A toolstring in the tubing, drawn procedurally: wire, rope socket, stem (two weight bars), a jar (housing with an anvil at each
end of the stroke, a mandrel with a hammer collar and a spring catch), and a tool stuck in a nipple under packed sand.
  s1  the wire pulls, nothing moves (stuck);
  s2  the jar's parts and its stroke;
  s3-4  jar up: the stem accelerates through the stroke and slams into the top anvil;
  s5  the spring catch holds while the wire stretches, then lets go: a bigger blow;
  s6  jar down: the stem falls onto the bottom anvil;
  s7  hundreds of blows; the tool comes free.
A force-at-the-tool trace shows each blow as a spike far above the steady pull.
"""
from __future__ import annotations
import math

from scenes.common import palette as P
from scenes.common import kit as K
from scenes.common import pdraw as D
from scenes.common.look import darken, lighten
from scenes.common.stage import hex_rgb


def b404(st, tl):
    b = tl["4.04"]
    s = b.sent
    with st.span(b.start, b.end):
        cx = -4.6
        ti = 0.62                                  # tubing inner half-width
        stroke = 1.1                               # jar stroke
        y_h_bot = -1.7                             # housing bottom (fixed to the tool below)
        y_h_top = y_h_bot + 2.1
        y_anvil_lo = y_h_bot + 0.3                 # bottom anvil face (top of the lower shoulder)
        y_anvil_hi = y_h_top - 0.25                # top anvil face (underside of the upper shoulder)
        coll_h = 0.28
        # mandrel position m: 0 = collar resting on the bottom anvil, stroke = collar against the top anvil
        T0 = b.start + 0.2
        # jar up (plain): accelerate from m=0, impact at t_hit1
        ta1 = s[3] + 0.7
        t_hit1 = s[4] + 0.6
        # reset: slack off back down (gently) before the spring-catch demonstration
        tr0, tr1 = s[4] + 4.5, s[4] + 6.0
        # spring catch: holds, the wire stretches, lets go
        tc0 = s[5] + 0.4
        t_let = b.word(5, "and then it lets go") + 0.2
        t_hit2 = t_let + 0.32
        # jar down: fall from the top
        td0 = s[6] + 1.2
        t_hit3 = td0 + 0.62
        # repeated blows, then the tool comes free
        tb0 = s[7] + 0.2
        n_rep = 6
        per = 0.42
        t_free = tb0 + n_rep * per + 0.3

        def m_of(t):
            if t < ta1:
                return 0.0
            if t < t_hit1:
                f = (t - ta1) / (t_hit1 - ta1)
                return stroke * f * f
            if t < tr0:
                return stroke
            if t < tr1:
                return stroke * (1 - D.ramp(t, tr0, tr1))
            if t < t_let:
                return 0.0
            if t < t_hit2:
                f = (t - t_let) / (t_hit2 - t_let)
                return stroke * f * f
            if t < td0:
                return stroke
            if t < t_hit3:
                f = (t - td0) / (t_hit3 - td0)
                return stroke * (1 - f * f)
            if t < tb0:
                return 0.0
            k = int((t - tb0) / per)
            if k < n_rep:
                f = ((t - tb0) % per) / per
                if f < 0.5:
                    return stroke * (2 * f) ** 2                 # up
                return stroke * (1 - (2 * (f - 0.5)) ** 2)      # down
            return 0.0

        def tool_dy(t):
            """The stuck tool: a hair of movement at each upward blow, free at the end."""
            dy = 0.0
            for th in (t_hit1, t_hit2):
                dy += 0.03 * D.ramp(t, th, th + 0.05)
            for k in range(n_rep):
                dy += 0.012 * D.ramp(t, tb0 + k * per + per / 2, tb0 + k * per + per / 2 + 0.05)
            dy += 1.9 * D.ramp(t, t_free, t_free + 1.6)
            return dy

        hits_up = [t_hit1, t_hit2] + [tb0 + k * per + per / 2 for k in range(n_rep)]
        hits_dn = [t_hit3] + [tb0 + (k + 1) * per for k in range(n_rep)]

        def stretch(t):
            """Wire stretch while the catch holds (0..1)."""
            return D.lin(t, tc0 + 0.4, t_let) * (1 - D.ramp(t, t_let, t_let + 0.15))

        def draw(c, t, look):
            a = D.vis(t, T0, None, 0.5)
            if a <= 0:
                return
            # tubing
            D.fill(c, cx - ti, -3.5, cx + ti, 3.9, darken(hex_rgb(P.BG), 0.3), a)
            for sd in (-1, 1):
                D.steel(c, cx + sd * ti, -3.5, cx + sd * (ti + 0.14), 3.9, P.STEEL, a)
            # nipple and the stuck tool, packed sand on top of it
            yn = -2.7
            for sd in (-1, 1):
                D.steel(c, cx + sd * (ti - 0.12), yn - 0.35, cx + sd * ti, yn + 0.35, P.STEEL_DK, a)
            dy = tool_dy(t)
            y_hb = y_h_bot + dy
            # tool below the housing
            D.steel(c, cx - 0.32, yn - 0.55 + dy, cx + 0.32, y_hb, P.STEEL_DK, a)
            for sd in (-1, 1):
                D.flat(c, cx + sd * 0.32, yn - 0.12 + dy, cx + sd * 0.48, yn + 0.12 + dy, P.WARN, a, r=0.02)
            sand_a = a * (1.0 - D.ramp(t, t_free, t_free + 1.0))
            D.fill(c, cx - ti, yn + 0.15, cx - 0.32, yn + 1.0, P.SAND, 0.9 * sand_a)
            D.fill(c, cx + 0.32, yn + 0.15, cx + ti, yn + 1.0, P.SAND, 0.9 * sand_a)
            # jar housing (moves only with the tool)
            yt_ = y_h_top + dy
            D.steel(c, cx - 0.42, y_hb, cx - 0.3, yt_, P.STEEL, a)
            D.steel(c, cx + 0.3, y_hb, cx + 0.42, yt_, P.STEEL, a)
            D.fill(c, cx - 0.3, y_hb, cx + 0.3, yt_, darken(hex_rgb(P.BG), 0.15), a)
            D.steel(c, cx - 0.42, y_hb, cx + 0.42, y_anvil_lo + dy, P.STEEL_DK, a)                     # bottom anvil
            D.steel(c, cx - 0.42, y_anvil_hi + dy, cx - 0.1, yt_, P.STEEL_DK, a)                        # top anvil (a ring
            D.steel(c, cx + 0.1, y_anvil_hi + dy, cx + 0.42, yt_, P.STEEL_DK, a)                        #  around the mandrel)
            # mandrel, collar (hammer) and the stem above
            m = m_of(t)
            yc = y_anvil_lo + dy + m                                         # collar bottom
            D.steel(c, cx - 0.27, yc, cx + 0.27, yc + coll_h, P.STEEL, a)
            D.steel(c, cx - 0.09, yc + coll_h, cx + 0.09, yt_ + 0.25 + m, P.STEEL, a)                    # mandrel rod
            y_stem0 = yt_ + 0.25 + m
            D.steel(c, cx - 0.27, y_stem0, cx + 0.27, y_stem0 + 0.72, P.STEEL_DK, a)
            D.steel(c, cx - 0.27, y_stem0 + 0.76, cx + 0.27, y_stem0 + 1.48, P.STEEL_DK, a)
            D.steel(c, cx - 0.16, y_stem0 + 1.48, cx + 0.16, y_stem0 + 1.75, P.STEEL, a)                 # rope socket
            # spring catch: two detent fingers in the housing that hold the collar until the pull builds
            ca = a * D.vis(t, s[5] - 0.2, td0, 0.4)
            if ca > 0:
                hold = (t < t_let) and m < 0.02
                yk = y_anvil_lo + dy + coll_h + 0.02
                for sd in (-1, 1):
                    x0 = cx + sd * 0.3
                    xi = cx + sd * (0.16 if hold else 0.28)
                    D.poly(c, [(x0, yk - 0.04), (xi, yk + 0.06), (x0, yk + 0.18)], P.WARN, ca)
                    D.zigzag(c, x0 - sd * 0.02, x0 - sd * 0.12, yk + 0.18, yk + 0.6, 4, P.TEXT, 0.025, ca)
                if hold and t > tc0:
                    D.glow(c, look, cx, yk + 0.06, 0.35, P.WARN, 0.35 * ca)
            # the wire, drawn as a spring while it stretches
            wy0 = y_stem0 + 1.75
            sk = stretch(t)
            if sk > 0.02:
                n = 9
                ys = [wy0 + (3.95 - wy0) * i / (2 * n) for i in range(2 * n + 1)]
                pts = [(cx + (0.0 if i % 2 == 0 else (0.12 if (i // 2) % 2 == 0 else -0.12) * sk), y) for i, y in enumerate(ys)]
                D.stroke(c, pts, P.WARN, 0.03, a)
            else:
                D.stroke(c, [(cx, wy0), (cx, 3.95)], P.WIRE, 0.03, a)
            # impacts
            for th in hits_up:
                D.flash(c, look, cx, y_anvil_hi + dy, 0.75 if th in (t_hit1, t_hit2) else 0.5, P.WARN, (t - th) / (0.8 if th == t_hit2 else 0.6))
            for th in hits_dn:
                D.flash(c, look, cx, y_anvil_lo + dy, 0.6 if th == t_hit3 else 0.45, P.PORE, (t - th) / 0.6)
            # speed streaks while the stem flies
            for (t0_, t1_) in ((ta1 + 0.35, t_hit1), (t_let, t_hit2)):
                if t0_ < t < t1_ + 0.05:
                    f = D.lin(t, t0_, t1_)
                    for k in range(3):
                        x = cx - 0.45 - 0.12 * k
                        D.stroke(c, [(x, y_stem0 + 0.2), (x, y_stem0 + 1.6)], P.TEXT, 0.015, 0.5 * a * f)
            # stroke dimension
            sa = a * D.vis(t, s[2], s[4] + 2, 0.4)
            xs = cx + 0.75
            D.stroke(c, [(xs, y_anvil_lo + coll_h + dy), (xs, y_anvil_hi + dy)], P.MUTED, 0.015, sa)
            for yy in (y_anvil_lo + coll_h + dy, y_anvil_hi + dy):
                D.stroke(c, [(xs - 0.08, yy), (xs + 0.08, yy)], P.MUTED, 0.015, sa)
            D.text(c, look, "stroke", xs + 0.12, (y_anvil_lo + y_anvil_hi) / 2 + dy, 0.15, P.MUTED, sa, align="l")
            # pull arrow at the top
            pa = a * (D.vis(t, s[1] + 0.5, s[2], 0.3) + D.vis(t, s[3], t_hit1, 0.2) + D.vis(t, tc0, t_let, 0.2))
            D.arrow(c, cx + 0.45, 3.0, cx + 0.45, 3.75, P.PORE, 0.06, 0.2, min(pa, 1.0))

        st.procedural(b.start, b.end, 0.4, draw)

        # ------------------------------------------------------------------ the force at the tool
        gx0, gx1, gy0, gy1 = -1.6, 7.55, -3.3, 0.95
        tw0, tw1 = s[1] + 0.3, t_free + 0.6

        def force(t):
            f = 0.05
            f += 0.16 * D.vis(t, s[1] + 0.5, s[2], 0.4)                       # the stuck pull (nothing moves)
            f += 0.14 * D.lin(t, ta1, t_hit1) * (t < t_hit1 + 0.02)
            f += 0.22 * D.lin(t, tc0 + 0.3, t_let) * (t < t_let + 0.02)        # spring catch: the pull builds
            for th, h in ((t_hit1, 0.62), (t_hit2, 0.95)):
                f += h * math.exp(-((t - th) / 0.045) ** 2)
            f -= 0.5 * math.exp(-((t - t_hit3) / 0.045) ** 2)
            for k in range(n_rep):
                f += 0.48 * math.exp(-((t - (tb0 + k * per + per / 2)) / 0.04) ** 2)
                f -= 0.36 * math.exp(-((t - (tb0 + (k + 1) * per)) / 0.04) ** 2)
            return f

        def gmap(t, v):
            return gx0 + 0.45 + (gx1 - gx0 - 0.65) * (t - tw0) / (tw1 - tw0), gy0 + 1.75 + (gy1 - gy0 - 2.3) * v

        def draw_trace(c, t, look):
            a = D.vis(t, s[1] + 0.2, None, 0.5)
            if a <= 0:
                return
            D.flat(c, gx0, gy0, gx1, gy1, P.PANEL, 0.92 * a, r=0.1)
            D.text(c, look, "FORCE AT THE STUCK TOOL", gx0 + 0.3, gy1 - 0.22, 0.15, P.MUTED, a, align="l", kind="bold")
            y0 = gmap(tw0, 0.0)[1]
            D.stroke(c, [(gx0 + 0.45, y0), (gx1 - 0.2, y0)], P.GRID, 0.012, a)
            D.text(c, look, "up", gx0 + 0.25, y0 + 0.5, 0.13, P.MUTED, a)
            D.text(c, look, "down", gx0 + 0.25, y0 - 0.5, 0.13, P.MUTED, a)
            yp = gmap(tw0, 0.21)[1]
            D.dashed(c, (gx0 + 0.45, yp), (gx1 - 0.2, yp), P.PORE, 0.012, 0.6 * a)
            D.text(c, look, "the most the wire can pull steadily", gx1 - 0.3, yp + 0.13, 0.12, P.PORE, 0.8 * a, align="r")
            te = min(t, tw1)
            if te <= tw0:
                return
            n = int((te - tw0) / 0.012) + 2
            pts = [gmap(tw0 + (te - tw0) * i / (n - 1), force(tw0 + (te - tw0) * i / (n - 1))) for i in range(n)]
            D.stroke(c, pts, P.WARN, 0.04, a)
            D.glow(c, look, pts[-1][0], pts[-1][1], 0.1, P.WARN, 0.8 * a)
            for th, lab, v in ((t_hit1, "jar up: a blow", 0.68), (t_hit2, "spring catch: harder", 1.0), (t_hit3, "jar down", -0.55)):
                if t > th:
                    x, y = gmap(th, v)
                    D.text(c, look, lab, x + 0.15, y + (0.1 if v > 0 else -0.12), 0.14, P.TEXT, a * D.lin(t, th, th + 0.3), align="l", kind="bold")

        st.procedural(b.start, b.end, 0.6, draw_trace)

        # ------------------------------------------------------------------ labels
        lx = cx + 1.25
        labs = [("wire: it can only pull", 3.3, cx + 0.05, 3.3, s[1] + 0.2, s[3]),
                ("stem: the hammer's weight", 1.5, cx + 0.27, 1.5, s[2] - 0.3, s[3]),
                ("jar: a sliding joint", 0.35, cx + 0.42, 0.35, s[2] + 0.2, s[3]),
                ("tool stuck under sand", -2.35, cx + ti, -2.35, s[1] + 0.8, s[3])]
        for text, y, tx, ty, t0, t1 in labs:
            K.show(st, K.callout(st, text, lx, y, tx, ty, size=0.17, align="l", z=1.1), t0, t1, 0.35)
        cl = K.callout(st, "spring catch", lx, -1.05, cx + 0.32, -1.05, color=P.WARN, fg=P.BG, size=0.17, align="l", z=1.1)
        K.show(st, cl, s[5] + 0.2, td0, 0.35)
        ws = K.tag(st, lx, 3.3, "the wire stretches like a spring", color=P.WARN, fg=P.BG, size=0.17, z=1.1, align="l")
        K.show(st, ws, tc0 + 0.8, t_let + 0.6, 0.35)
        free = K.tag(st, lx, -2.35, "free", color=P.SAFE, fg=P.BG, size=0.2, z=1.1, align="l")
        K.show(st, free, t_free + 0.6, None, 0.35)
        cnt = st.counter(4.9, 1.45, tb0, tb0 + n_rep * per, 1, 240, fmt="blows: {:.0f}", size=0.24, color=P.TEXT, z=1.1, kind="mono")
        K.show(st, K.tag(st, 2.2, 1.45, "hundreds of blows", color=P.SAFE, fg=P.BG, size=0.22, z=1.1), tb0, None, 0.35)
