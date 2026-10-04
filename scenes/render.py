#!/usr/bin/env python3
"""Render one chapter (or a time window of it) headless with Blender's Workbench engine.

    xvfb-run -a .venv/bin/python scenes/render.py --chapter 1 --res 854x480 --out renders/preview

Only frames where something animates are rendered; `frames.txt` (ffmpeg concat list) holds each still
until the next change. Re-running skips frames already on disk.
"""
from __future__ import annotations
import argparse
import glob
import importlib.util
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from scenes.common.stage import Stage          # noqa: E402  (needs bpy)
from scenes.common import timeline, furniture  # noqa: E402


def load_chapter_module(num: int):
    path = glob.glob(os.path.join(HERE, f"ch{num:02d}_*.py"))[0]
    spec = importlib.util.spec_from_file_location(f"scenes.ch{num:02d}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_stage(num: int, res=(1920, 1080), fps=12, samples=8):
    tl = timeline.load_chapter(num)
    st = Stage(tl.dur, fps=fps, res=res, samples=samples, name=f"ch{num:02d}")
    mod = load_chapter_module(num)
    mod.build(st, tl)
    furniture.auto_overlays(st, tl)
    return st, tl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", type=int, required=True)
    ap.add_argument("--res", default="1920x1080")
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--samples", type=int, default=5)
    ap.add_argument("--out", default=os.path.join(ROOT, "renders", "preview"))
    ap.add_argument("--t0", type=float, default=0.0, help="chapter-relative start (s)")
    ap.add_argument("--t1", type=float, default=None, help="chapter-relative end (s)")
    ap.add_argument("--beat", default=None, help="render only this beat id (e.g. 1.05)")
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--qa", action="store_true", help="fast style check: render only two settled frames per beat (50 %% and 92 %%)")
    a = ap.parse_args()
    w, h = (int(v) for v in a.res.split("x"))
    t_build = time.time()
    st, tl = build_stage(a.chapter, (w, h), a.fps, a.samples)
    t0, t1 = a.t0, a.t1
    if a.beat:
        b = tl.beat(a.beat)
        t0, t1 = b.start, b.end
    frames = st.plan_frames(t0, t1)
    if a.qa:
        qs = set()
        for b in tl.beats:
            if a.beat and b.id != a.beat:
                continue
            for frac in (0.5, 0.92):
                qs.add(int(1 + (b.start + b.dur * frac) * a.fps))
        frames = sorted(qs)
    total = int(round(((t1 if t1 is not None else st.duration) - t0) * a.fps))
    print(f"ch{a.chapter:02d}: build {time.time() - t_build:.1f}s, {len(frames)} of {total} frames need rendering "
          f"({100 * len(frames) / max(total, 1):.0f} %)", flush=True)
    if a.plan_only:
        return
    outdir = os.path.join(a.out, f"ch{a.chapter:02d}" + (f"_b{a.beat.replace('.', '_')}" if a.beat else ""))
    t_r = time.time()
    st.render_frames(outdir, frames)
    if not a.qa:
        last = int(round(st.fr(t1))) if t1 is not None else None
        st.write_concat(outdir, frames, last_frame=last)
    print(f"ch{a.chapter:02d}: rendered in {time.time() - t_r:.1f}s -> {outdir}", flush=True)


if __name__ == "__main__":
    main()
