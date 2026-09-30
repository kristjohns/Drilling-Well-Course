"""Reusable 2D overlay elements: icons, phase cards, map inset, dimension brackets."""
import json
import math
import os

import config as C
import gfx as G
import palette as P

# ------------------------------------------------------------------ icons (drawn in a 100x100 box)


def icon(ctx, kind, cx, cy, s=1.0, col=P.WHITE, alpha=1.0):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    G.set_color(ctx, col, alpha)
    lw = 7
    ctx.set_line_width(lw)
    if kind == 'design':      # set square + pencil
        G.poly(ctx, [(-38, 34), (34, 34), (-38, -38)], stroke=col, lw=lw, alpha=alpha)
        G.poly(ctx, [(-24, 20), (6, 20), (-24, -10)], stroke=col, lw=4, alpha=alpha)
        ctx.save()
        ctx.rotate(math.radians(45))
        G.rrect(ctx, -8, -52, 16, 56, 3)
        G.set_color(ctx, col, alpha)
        ctx.fill()
        G.poly(ctx, [(-8, 4), (8, 4), (0, 18)], fill=col, alpha=alpha)
        ctx.restore()
    elif kind == 'drill':     # derrick
        G.poly(ctx, [(-30, 40), (-8, -42), (8, -42), (30, 40)], stroke=col, lw=lw, alpha=alpha,
               close=False)
        for y in (-14, 14):
            w = 12 + (y + 42) * 0.27
            G.line(ctx, [(-w, y), (w, y)], col, 5, alpha)
        G.line(ctx, [(-38, 40), (38, 40)], col, lw, alpha)
        G.line(ctx, [(0, -42), (0, 50)], col, 4, alpha)
    elif kind == 'complete':  # christmas tree valves
        G.line(ctx, [(0, 44), (0, -40)], col, 12, alpha)
        for y in (-18, 14):
            G.line(ctx, [(-24, y), (24, y)], col, 7, alpha)
            G.circle(ctx, -28, y, 8, fill=col, alpha=alpha)
            G.circle(ctx, 28, y, 8, fill=col, alpha=alpha)
        G.line(ctx, [(0, -4), (40, -4)], col, 8, alpha)
        G.rrect(ctx, -14, -50, 28, 12, 4)
        ctx.fill()
    elif kind == 'pa':        # plug in a well
        G.line(ctx, [(-22, -44), (-22, 44)], col, 6, alpha)
        G.line(ctx, [(22, -44), (22, 44)], col, 6, alpha)
        G.rrect(ctx, -18, -14, 36, 34, 4)
        G.set_color(ctx, col, alpha)
        ctx.fill()
        for y in (-30, 34):
            G.line(ctx, [(-12, y), (12, y)], col, 3, alpha * 0.6, dash=[4, 5])
    ctx.restore()


PHASE_INFO = [('design', 'Design', P.ACCENT), ('drill', 'Drilling', '#2F80C9'),
              ('complete', 'Completion', P.XT), ('pa', 'P&A', '#6A5ACD')]


def phase_card(ctx, i, x, y, p, w=250, h=250, highlight=1.0, sub=None, alpha=1.0):
    """Rounded card with icon + title. (x, y) top-left."""
    if p <= 0:
        return
    kind, title, col = PHASE_INFO[i]
    pe = G.ease_out_back(G.clamp(p))
    a = G.clamp(p * 2) * alpha
    cx, cy = x + w / 2, y + h / 2
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(0.7 + 0.3 * pe, 0.7 + 0.3 * pe)
    ctx.translate(-cx, -cy)
    G.shadow_rrect(ctx, x, y, w, h, 28, alpha=0.25 * a)
    G.rrect(ctx, x, y, w, h, 28)
    G.set_color(ctx, G.mix('#FFFFFF', col, 0.12 + 0.88 * highlight), a)
    ctx.fill()
    ic = G.mix(col, '#FFFFFF', highlight)
    icon(ctx, kind, cx, y + h * 0.40, 0.95, ic, a)
    G.text(ctx, f'{i + 1}', x + 22, y + 44, 30, 'ExtraBold', ic, alpha=a * 0.8)
    G.text(ctx, title.upper(), cx, y + h - 38, 30, 'ExtraBold', ic, 'center', alpha=a,
           tracking=0.06)
    if sub:
        G.text(ctx, sub, cx, y + h + 40, 24, 'SemiBold', P.INK_SOFT, 'center', alpha=a)
    ctx.restore()


# ------------------------------------------------------------------ dimension bracket

def dim_v(ctx, x, y0, y1, label, p=1.0, col=P.INK, side='left', size=30, alpha=1.0, sub=None):
    """Vertical dimension arrow between y0 and y1 with a label."""
    if p <= 0:
        return
    pe = G.ease_in_out(p)
    ym = (y0 + y1) / 2
    G.arrow(ctx, x, ym, x, ym + (y0 - ym) * pe, col, 3.5, 14, 1.0, alpha)
    G.arrow(ctx, x, ym, x, ym + (y1 - ym) * pe, col, 3.5, 14, 1.0, alpha)
    for y in (y0, y1):
        G.line(ctx, [(x - 14, y), (x + 14, y)], col, 3, alpha * pe)
    ta = alpha * G.clamp((p - 0.4) / 0.6)
    tx = x - 22 if side == 'left' else x + 22
    G.text(ctx, label, tx, ym, size, 'ExtraBold', col, 'right' if side == 'left' else 'left',
           'middle', alpha=ta)
    if sub:
        G.text(ctx, sub, tx, ym + size * 0.95, size * 0.62, 'SemiBold', col,
               'right' if side == 'left' else 'left', 'middle', alpha=ta * 0.85)


def quad(ctx, pts, fill=None, stroke=None, lw=3, alpha=1.0):
    pts = [p for p in pts if p is not None]
    if len(pts) >= 3:
        G.poly(ctx, pts, fill=fill, stroke=stroke, lw=lw, alpha=alpha)


def glow_quad(ctx, pts, col, alpha):
    pts = [p for p in pts if p is not None]
    if len(pts) < 3 or alpha <= 0:
        return
    for w, a in ((22, 0.10), (12, 0.2), (5, 0.6)):
        G.poly(ctx, pts, stroke=col, lw=w, alpha=alpha * a)
    G.poly(ctx, pts, fill=col, alpha=alpha * 0.18)


# ------------------------------------------------------------------ map inset

_GEO = {}


def _country(code):
    if code not in _GEO:
        path = os.path.join(C.VIDEO, 'assets', 'geo', code + '.geo.json')
        gj = json.load(open(path))
        polys = []
        for feat in gj['features']:
            g = feat['geometry']
            if g['type'] == 'Polygon':
                polys.append(g['coordinates'][0])
            else:
                for poly in g['coordinates']:
                    polys.append(poly[0])
        _GEO[code] = polys
    return _GEO[code]


def map_inset(ctx, x, y, w, h, p, t, marker=(3.0, 60.8), alpha=1.0):
    """North-west Europe map with Norway highlighted and a pulsing marker."""
    if p <= 0:
        return
    pe = G.ease_out(p)
    a = alpha * G.clamp(p * 1.5)
    lon0, lon1, lat0, lat1 = -6.0, 32.0, 53.5, 71.8
    kx = math.cos(math.radians(63))

    def px(lon, lat):
        u = (lon - lon0) * kx / ((lon1 - lon0) * kx)
        v = (lat - lat0) / (lat1 - lat0)
        # keep aspect ratio: fit height
        s = h / (lat1 - lat0)
        return x + (lon - lon0) * kx * s + 10, y + h - v * h

    yy = y + (1 - pe) * 30
    ctx.save()
    ctx.translate(0, yy - y)
    G.shadow_rrect(ctx, x - 16, y - 16, w + 32, h + 32, 24, alpha=0.3 * a)
    G.rrect(ctx, x - 16, y - 16, w + 32, h + 32, 24)
    G.set_color(ctx, '#CFE6F6', a)
    ctx.fill()
    G.rrect(ctx, x - 16, y - 16, w + 32, h + 32, 24)
    ctx.clip()
    for code, col in (('GBR', '#E4E8EC'), ('SWE', '#E4E8EC'), ('FIN', '#E4E8EC'),
                      ('DNK', '#E4E8EC'), ('DEU', '#E4E8EC'), ('NLD', '#E4E8EC'),
                      ('NOR', P.ACCENT)):
        for poly in _country(code):
            pts = [px(lo, la) for lo, la in poly]
            G.poly(ctx, pts, fill=col, stroke='#FFFFFF', lw=1.5, alpha=a)
    G.text(ctx, 'NORTH SEA', *px(2.0, 57.2), 18, 'Bold', '#4C7FA8', 'center', alpha=a * 0.9,
           tracking=0.12)
    G.text(ctx, 'NORWEGIAN SEA', *px(4.0, 66.5), 18, 'Bold', '#4C7FA8', 'center', alpha=a * 0.9,
           tracking=0.12)
    G.text(ctx, 'NORWAY', *px(10.0, 61.8), 20, 'ExtraBold', '#FFFFFF', 'center', alpha=a,
           tracking=0.12)
    mx, my = px(*marker)
    pulse = (t * 0.8) % 1.0
    G.circle(ctx, mx, my, 10 + 30 * pulse, stroke=P.KICK, lw=3, alpha=a * (1 - pulse))
    G.circle(ctx, mx, my, 10, fill=P.KICK, alpha=a)
    G.circle(ctx, mx, my, 4, fill='#FFFFFF', alpha=a)
    ctx.restore()
    return px(*marker)[0], px(*marker)[1] + (yy - y)
