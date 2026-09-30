"""Tileable lithology / material textures (PNG) generated with PIL.

Patterns follow the spirit of standard geological lithology symbols
(dots = sandstone, dashes = shale/claystone, bricks = chalk/limestone),
rendered subtly so they read as texture rather than noise.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import config as C

TEX_DIR = os.path.join(C.BUILD, 'tex')
S = 512


def _hex(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def _base(col, noise=6, seed=0):
    rng = np.random.default_rng(seed)
    a = np.zeros((S, S, 3), np.float32) + np.array(_hex(col), np.float32)
    # soft large-scale mottling (tileable by construction: sum of periodic sines)
    y, x = np.mgrid[0:S, 0:S] / S * 2 * np.pi
    m = np.zeros((S, S), np.float32)
    for _ in range(6):
        fx, fy = rng.integers(1, 5, 2)
        ph = rng.uniform(0, 6.28)
        m += np.sin(fx * x + fy * y + ph)
    m = m / 6
    a *= (1 + 0.035 * m)[..., None]
    a += rng.normal(0, noise, (S, S, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def _wrap_draw(draw, fn, x, y, *args):
    for dx in (-S, 0, S):
        for dy in (-S, 0, S):
            fn(draw, x + dx, y + dy, *args)


def _dot(d, x, y, r, c):
    d.ellipse([x - r, y - r, x + r, y + r], fill=c)


def _dash(d, x, y, L, t, c):
    d.rectangle([x - L / 2, y - t / 2, x + L / 2, y + t / 2], fill=c)


def dots(col, n=700, rmin=1.6, rmax=3.2, k=0.78, seed=1, extra=None):
    im = _base(col, seed=seed)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    dc = _shade(_hex(col), k)
    for _ in range(n):
        x, y = rng.uniform(0, S, 2)
        _wrap_draw(d, _dot, x, y, rng.uniform(rmin, rmax), dc)
    if extra:
        extra(d, rng)
    return im


def dashes(col, rows=16, k=0.8, L=(26, 46), t=3, gap=(14, 40), seed=2, dots_n=0):
    im = _base(col, seed=seed)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    dc = _shade(_hex(col), k)
    h = S / rows
    for r in range(rows):
        y = (r + 0.5) * h + rng.uniform(-2, 2)
        x = rng.uniform(0, 30)
        while x < S:
            ln = rng.uniform(*L)
            _wrap_draw(d, _dash, x + ln / 2, y, ln, t, dc)
            x += ln + rng.uniform(*gap)
    for _ in range(dots_n):
        x, y = rng.uniform(0, S, 2)
        _wrap_draw(d, _dot, x, y, 1.8, dc)
    return im


def bricks(col, rows=8, k=0.82, t=3, seed=3):
    im = _base(col, seed=seed)
    d = ImageDraw.Draw(im)
    dc = _shade(_hex(col), k)
    h = S / rows
    bw = S / 4
    for r in range(rows):
        y = r * h
        d.rectangle([0, y - t / 2, S, y + t / 2], fill=dc)
        off = (bw / 2) if r % 2 else 0
        for i in range(5):
            x = off + i * bw
            _wrap_draw(d, lambda dd, xx, yy: dd.rectangle([xx - t / 2, yy, xx + t / 2, yy + h],
                                                          fill=dc), x % S, y)
    return im


def speckle(col, n=2500, k=0.86, seed=4, light=None):
    im = _base(col, noise=4, seed=seed)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    dc = _shade(_hex(col), k)
    lc = _shade(_hex(col), 1.1) if light is None else _hex(light)
    for i in range(n):
        x, y = rng.uniform(0, S, 2)
        _wrap_draw(d, _dot, x, y, rng.uniform(0.8, 1.8), dc if i % 3 else lc)
    return im


def ripples(col, seed=5):
    """Sandy seabed with soft ripple marks."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:S, 0:S] / S * 2 * np.pi
    base = np.array(_hex(col), np.float32)
    w = np.sin(8 * x + 1.5 * np.sin(2 * y) + 0.6 * np.sin(3 * y + 1.0))
    a = base[None, None, :] * (1 + 0.045 * w)[..., None]
    a += rng.normal(0, 5, (S, S, 1))
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    dc = _shade(_hex(col), 0.85)
    for _ in range(900):
        xx, yy = rng.uniform(0, S, 2)
        _wrap_draw(d, _dot, xx, yy, rng.uniform(0.7, 1.6), dc)
    return im.filter(ImageFilter.GaussianBlur(0.4))


def crosses(col, k=0.8, seed=6):
    im = _base(col, seed=seed)
    d = ImageDraw.Draw(im)
    dc = _shade(_hex(col), k)
    step = 64
    for j in range(S // step):
        for i in range(S // step):
            x = i * step + (step / 2 if j % 2 else 0) + 16
            y = j * step + 20
            d.line([(x - 7, y - 7), (x + 7, y + 7)], fill=dc, width=3)
            d.line([(x - 7, y + 7), (x + 7, y - 7)], fill=dc, width=3)
    return im


def build_all(force=False):
    import palette as P
    os.makedirs(TEX_DIR, exist_ok=True)
    specs = {
        'soft_clay': lambda: dashes(P.SOFT_CLAY, rows=18, k=0.86, L=(14, 26), gap=(20, 50),
                                    dots_n=120),
        'claystone': lambda: dashes(P.CLAYSTONE, rows=16, k=0.82),
        'claystone2': lambda: dashes('#A2957F', rows=16, k=0.82, seed=9),
        'siltstone': lambda: dashes(P.SILTSTONE, rows=14, k=0.8, L=(18, 30), gap=(30, 60),
                                    dots_n=350),
        'chalk': lambda: bricks(P.CHALK),
        'shale': lambda: dashes(P.SHALE, rows=22, k=1.22, L=(30, 60), t=2.5, gap=(10, 30)),
        'reservoir': lambda: dots(P.RESERVOIR, n=900, k=0.72),
        'water_zone': lambda: dots(P.WATER_ZONE, n=700, k=0.82, seed=7),
        'basement': lambda: crosses(P.BASEMENT),
        'cement': lambda: speckle(P.CEMENT, n=3000, k=0.84),
        'seabed': lambda: ripples(P.SEABED),
    }
    from PIL import ImageEnhance
    out = {}
    for name, fn in specs.items():
        path = os.path.join(TEX_DIR, name + '.png')
        if force or not os.path.exists(path):
            im = fn()
            im = ImageEnhance.Brightness(im).enhance(1.07)
            im = ImageEnhance.Color(im).enhance(1.18)
            im.save(path)
        out[name] = path
    return out


if __name__ == '__main__':
    build_all(force=True)
    print('textures in', TEX_DIR)
