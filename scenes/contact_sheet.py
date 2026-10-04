#!/usr/bin/env python3
"""Tile one frame per beat (at a chosen fraction of the beat) into a contact sheet for style review.

    python scenes/contact_sheet.py --chapter 1 --renders renders/preview [--frac 0.9] [--cols 3] [--beats 1.05,1.07]

Needs only Pillow (no Blender)."""
from __future__ import annotations
import argparse
import glob
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from scenes.common.timeline import load_chapter  # noqa: E402


def rendered_frames(d):
    return sorted(int(re.search(r"frame_(\d+)\.png", p).group(1)) for p in glob.glob(os.path.join(d, "frame_*.png")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", type=int, required=True)
    ap.add_argument("--renders", default=os.path.join(ROOT, "renders", "preview"))
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--frac", type=float, default=0.9)
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--thumb", type=int, default=640)
    ap.add_argument("--beats", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    d = os.path.join(a.renders, f"ch{a.chapter:02d}")
    frames = rendered_frames(d)
    tl = load_chapter(a.chapter)
    want = a.beats.split(",") if a.beats else [b.id for b in tl.beats]
    tiles = []
    for b in tl.beats:
        if b.id not in want:
            continue
        f = int(1 + (b.start + b.dur * a.frac) * a.fps)
        cand = [x for x in frames if x <= f]
        if not cand:
            continue
        im = Image.open(os.path.join(d, f"frame_{cand[-1]:05d}.png")).convert("RGB")
        w = a.thumb
        im = im.resize((w, int(w * im.height / im.width)))
        dr = ImageDraw.Draw(im)
        dr.rectangle([0, 0, 150, 22], fill=(0, 0, 0))
        dr.text((6, 5), f"{b.id}  t={b.start + b.dur * a.frac:5.1f}s", fill=(255, 255, 255))
        tiles.append(im)
    if not tiles:
        print("no frames found in", d)
        return
    cols = min(a.cols, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    tw, th = tiles[0].size
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 6, rows * th + (rows + 1) * 6), (30, 30, 30))
    for i, t in enumerate(tiles):
        sheet.paste(t, (6 + (i % cols) * (tw + 6), 6 + (i // cols) * (th + 6)))
    out = a.out or os.path.join(a.renders, f"sheet_ch{a.chapter:02d}.png")
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
