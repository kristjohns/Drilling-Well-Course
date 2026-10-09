#!/usr/bin/env python3
"""Render one chapter with the skia engine.

    .venv/bin/python scenes/render.py --chapter 1                       # full chapter -> renders/video/ch01.mp4 (1080p30)
    .venv/bin/python scenes/render.py --chapter 1 --qa                  # 2 stills per beat -> renders/qa/ch01/*.png
    .venv/bin/python scenes/render.py --chapter 1 --stills 12.5,40      # stills at chapter times
    .venv/bin/python scenes/render.py --chapter 1 --beat 1.05 --res 960x540   # one beat as a short clip

Every frame is evaluated; frames where nothing changes re-use the previous image. Beat boundaries dissolve softly.
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

from scenes.common.stage import Stage          # noqa: E402
from scenes.common import timeline, furniture  # noqa: E402


def load_chapter_module(num: int):
    path = glob.glob(os.path.join(HERE, f"ch{num:02d}_*.py"))[0]
    spec = importlib.util.spec_from_file_location(f"scenes.ch{num:02d}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_stage(num: int, res=(1920, 1080), fps=30):
    tl = timeline.load_chapter(num)
    st = Stage(tl.dur, fps=fps, res=res, name=f"ch{num:02d}")
    mod = load_chapter_module(num)
    mod.build(st, tl)
    furniture.auto_overlays(st, tl)
    st.set_transitions([b.start for b in tl.beats] + furniture.extra_transitions(tl))
    return st, tl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", type=int, required=True)
    ap.add_argument("--res", default="1920x1080")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--out", default=None, help="output mp4 (default renders/video/chNN.mp4) or still dir")
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--t1", type=float, default=None)
    ap.add_argument("--beat", default=None)
    ap.add_argument("--qa", action="store_true", help="stills at 50 %% and 92 %% of every beat")
    ap.add_argument("--fracs", default="0.5,0.92", help="beat fractions for --qa stills, e.g. 0.2,0.5,0.8,0.95")
    ap.add_argument("--stills", default=None, help="comma list of chapter times for stills")
    ap.add_argument("--crf", type=int, default=17)
    ap.add_argument("--preset", default="medium")
    ap.add_argument("--threads", type=int, default=None)
    a = ap.parse_args()
    w, h = (int(v) for v in a.res.split("x"))
    t_build = time.time()
    st, tl = build_stage(a.chapter, (w, h), a.fps)
    print(f"ch{a.chapter:02d}: built {len(st.objs)} objects in {time.time() - t_build:.1f}s, {tl.dur:.1f}s long", flush=True)
    if a.qa or a.stills:
        outdir = a.out or os.path.join(ROOT, "renders", "qa", f"ch{a.chapter:02d}")
        os.makedirs(outdir, exist_ok=True)
        shots = []
        if a.stills:
            shots = [(float(x), f"t{float(x):07.2f}") for x in a.stills.split(",")]
        else:
            for b in tl.beats:
                if a.beat and b.id != a.beat:
                    continue
                for frac in [float(x) for x in a.fracs.split(',')]:
                    shots.append((b.start + b.dur * frac, f"beat_{b.id.replace('.', '_')}_{int(frac * 100):02d}"))
        t_r = time.time()
        for t, name in shots:
            st.save_png(os.path.join(outdir, name + ".png"), t)
        print(f"ch{a.chapter:02d}: {len(shots)} stills in {time.time() - t_r:.1f}s -> {outdir}", flush=True)
        return
    t0, t1 = a.t0, a.t1
    if a.beat:
        b = tl.beat(a.beat)
        t0, t1 = b.start, b.end
    out = a.out or os.path.join(ROOT, "renders", "video", f"ch{a.chapter:02d}.mp4")
    t_r = time.time()
    n = st.render_video(out, t0, t1, crf=a.crf, preset=a.preset, threads=a.threads)
    print(f"ch{a.chapter:02d}: rendered {n} unique frames in {time.time() - t_r:.1f}s -> {out}", flush=True)


if __name__ == "__main__":
    main()
