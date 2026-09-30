"""Shared 2D well-barrier schematic (drilling / production / P&A configurations)."""
import math

import gfx as G
import palette as P
import well2d as W2

KNOTS = [(0, 110), (350, 330), (1350, 560), (2350, 760), (3450, 1010)]


def make(cx=560, x0=260, x1=860, k=3.2, knots=KNOTS):
    return W2.Well2D(cx=cx, knots=knots, x0=x0, x1=x1, k=k, pat_scale=0.42)


def shield(ctx, cx, cy, w, h, col, alpha=1.0, crack=0.0, label=None):
    """Heraldic shield centred at (cx, cy)."""
    if alpha <= 0:
        return
    def path():
        ctx.new_path()
        ctx.move_to(cx - w / 2, cy - h / 2)
        ctx.curve_to(cx - w / 6, cy - h / 2 - h * 0.06, cx + w / 6, cy - h / 2 - h * 0.06,
                     cx + w / 2, cy - h / 2)
        ctx.line_to(cx + w / 2, cy)
        ctx.curve_to(cx + w / 2, cy + h * 0.3, cx + w * 0.2, cy + h * 0.42, cx, cy + h / 2)
        ctx.curve_to(cx - w * 0.2, cy + h * 0.42, cx - w / 2, cy + h * 0.3, cx - w / 2, cy)
        ctx.close_path()
    ctx.save()
    ctx.translate(0, 8)
    path()
    ctx.set_source_rgba(0.05, 0.08, 0.12, 0.2 * alpha)
    ctx.fill()
    ctx.restore()
    path()
    G.set_color(ctx, col, alpha)
    ctx.fill_preserve()
    G.set_color(ctx, '#FFFFFF', alpha * 0.9)
    ctx.set_line_width(6)
    ctx.stroke()
    if label:
        G.text(ctx, label, cx, cy - 6, h * 0.34, 'ExtraBold', P.WHITE, 'center', 'middle',
               alpha=alpha)
    if crack > 0:
        pts = [(cx - w * 0.1, cy - h / 2), (cx + w * 0.08, cy - h * 0.25), (cx - w * 0.12, cy - h * 0.05),
               (cx + w * 0.1, cy + h * 0.15), (cx - w * 0.04, cy + h * 0.45)]
        G.line(ctx, pts, '#1B2631', 7, alpha, crack)
        G.line(ctx, pts, '#FFFFFF', 2.5, alpha, crack)


def drilling_well(ctx, w, t, casings=3, td=3050, bop_closed=0.0, alpha=1.0, mud=P.MUD,
                  string=True, labels=True):
    """Draw the well in drilling configuration on schematic `w`."""
    y_bed = w.y(350)
    ctx.save()
    ctx.rectangle(w.x0, 90, w.x1 - w.x0, 940)
    ctx.clip()
    w.draw_earth(ctx, labels=labels, alpha=alpha)
    # open hole + mud
    last = W2.CASINGS[casings - 1]
    w.fill_bore(ctx, 350, td, mud, alpha)
    for i in range(casings):
        w.cement(ctx, i, 1.0, alpha)
        w.casing(ctx, i, 1.0, alpha)
    # riser & mud in the riser
    rhw = 16
    G.rect(ctx, w.cx - rhw - 6, 90, 2 * rhw + 12, y_bed - 180 - 90, fill='#8FA0B2', alpha=alpha)
    G.rect(ctx, w.cx - rhw, 90, 2 * rhw, y_bed - 180 - 90, fill=mud, alpha=alpha)
    W2.draw_wellhead(ctx, w.cx, y_bed, 1.0, alpha)
    W2.draw_bop(ctx, w.cx, y_bed - 30, 0.8, closed=bop_closed, alpha=alpha, pipe=string)
    if string:
        G.rect(ctx, w.cx - 5, 90, 10, w.y(td) - 90 - 14, fill=P.PIPE, alpha=alpha)
        G.poly(ctx, [(w.cx - 16, w.y(td) - 22), (w.cx + 16, w.y(td) - 22), (w.cx + 12, w.y(td)),
                     (w.cx - 12, w.y(td))], fill='#3A424B', alpha=alpha)
    ctx.restore()


def drilling_envelopes(w, td=3050, casings=3):
    """Return (primary_pts, secondary_pts) for the drilling configuration."""
    y_bed = w.y(350)
    shoe = W2.CASINGS[casings - 1][3]
    ihw = w.hw(W2.CASINGS[casings - 1][1]) - 8
    ohw = w.hole_hw(td - 10) - 6
    prim = [(w.cx - ihw, y_bed - 24), (w.cx - ihw, w.y(shoe)), (w.cx - ohw, w.y(shoe) + 4),
            (w.cx - ohw, w.y(td) - 4), (w.cx + ohw, w.y(td) - 4), (w.cx + ohw, w.y(shoe) + 4),
            (w.cx + ihw, w.y(shoe)), (w.cx + ihw, y_bed - 24)]
    chw = w.hw(W2.CASINGS[casings - 1][2]) + 6
    bt = y_bed - 30 - 0.8 * 175
    sec = [(w.cx - chw, w.y(shoe) + 30), (w.cx - chw, w.y(shoe) - 60),
           (w.cx - w.hw(W2.CASINGS[casings - 1][1]) - 3, w.y(1200)),
           (w.cx - w.hw(W2.CASINGS[casings - 1][1]) - 3, y_bed + 10),
           (w.cx - 62, y_bed - 10), (w.cx - 62, bt), (w.cx + 62, bt), (w.cx + 62, y_bed - 10),
           (w.cx + w.hw(W2.CASINGS[casings - 1][1]) + 3, y_bed + 10),
           (w.cx + w.hw(W2.CASINGS[casings - 1][1]) + 3, w.y(1200)),
           (w.cx + chw, w.y(shoe) - 60), (w.cx + chw, w.y(shoe) + 30)]
    return prim, sec


def legend(ctx, x, y, items, p=1.0, size=28):
    """items: list of (colour, title, subtitle, progress)."""
    for i, (col, title, sub, pi) in enumerate(items):
        a = G.ease_out(G.clamp(pi)) * p
        if a <= 0:
            continue
        yy = y + i * 120
        G.panel(ctx, x, yy, 820, 100, a)
        G.rrect(ctx, x + 22, yy + 30, 60, 14 + 0, 7)
        G.set_color(ctx, col, a)
        ctx.fill()
        G.text(ctx, title, x + 104, yy + 44, size, 'ExtraBold', col, alpha=a)
        G.text(ctx, sub, x + 104, yy + 80, size * 0.8, 'SemiBold', P.INK_SOFT, alpha=a)
