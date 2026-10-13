"""Render scenes.

  python3 src/render.py still <scene_id> <t1> [t2 ...]     -> build/stills/<scene>_<t>.png
  python3 src/render.py sheet <scene_id> [step]             -> contact sheet PNG every `step` s
  python3 src/render.py video <scene_id> [...]              -> build/video/<scene>.mp4
  python3 src/render.py all [jobs]                          -> every scene, in parallel
"""
from __future__ import annotations

import importlib
import os
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from engine.core import W, H, FPS  # noqa: E402
from engine.scene import load_timeline  # noqa: E402

SCENE_MODULES = [
    "s00_open", "s01_definition", "s02_framework", "s03_barriers", "s04_verify", "s05_annulus",
    "s06_classify", "s07_failures", "s08_pa", "s09_ccs", "s10_future", "s11_credits",
]


def scene_class(sid):
    mod = importlib.import_module(f"scenes.{sid}")
    return mod.SceneImpl


def make_scene(sid, tl=None):
    tl = tl if tl is not None else load_timeline()
    return scene_class(sid)(tl)


def still(sid, times, out_dir=None):
    out_dir = out_dir or os.path.join(ROOT, "build", "stills")
    os.makedirs(out_dir, exist_ok=True)
    sc = make_scene(sid)
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    paths = []
    for t in times:
        t = float(t)
        c.save()
        sc.render(c, t)
        c.restore()
        p = os.path.join(out_dir, f"{sid}_{t:07.2f}.png")
        surf.makeImageSnapshot().save(p)
        paths.append(p)
    return paths


def sheet(sid, step=4.0, cols=4, scale=0.25):
    sc = make_scene(sid)
    times = list(np.arange(0.5, sc.dur, step))
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    tw, th = int(W * scale), int(H * scale)
    rows = (len(times) + cols - 1) // cols
    out = skia.Surface(tw * cols, th * rows)
    oc = out.getCanvas()
    oc.clear(skia.ColorBLACK)
    f = skia.Font(skia.Typeface("Inter"), 14)
    for i, t in enumerate(times):
        c.save()
        sc.render(c, float(t))
        c.restore()
        img = surf.makeImageSnapshot()
        r, k = divmod(i, cols)
        oc.drawImageRect(img, skia.Rect.MakeXYWH(k * tw, r * th, tw, th), skia.SamplingOptions(skia.FilterMode.kLinear))
        oc.drawString(f"{t:.1f}s", k * tw + 6, r * th + 18, f, skia.Paint(Color=skia.ColorYELLOW))
    p = os.path.join(ROOT, "build", "stills", f"sheet_{sid}.png")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    out.makeImageSnapshot().save(p)
    return p


def video(sid, crf=17, preset="medium", threads=2):
    out_dir = os.path.join(ROOT, "build", "video")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{sid}.mp4")
    sc = make_scene(sid)
    n = int(round(sc.dur * FPS))
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-",
           "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
           "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-tune", "animation",
           "-threads", str(threads), "-g", str(FPS * 4),
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-movflags", "+faststart", out + ".part.mp4"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    buf = np.empty((H, W, 4), np.uint8)
    info = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
    t0 = time.time()
    for i in range(n):
        t = i / FPS
        c.save()
        sc.render(c, t)
        c.restore()
        surf.readPixels(info, buf, W * 4, 0, 0)
        proc.stdin.write(memoryview(buf))
        if i % (FPS * 10) == 0:
            el = time.time() - t0
            print(f"[{sid}] {i}/{n} frames  {el:6.1f}s  ({(el / max(1, i)) * 1000:.0f} ms/frame)", flush=True)
    proc.stdin.close()
    proc.wait()
    os.replace(out + ".part.mp4", out)
    print(f"[{sid}] done in {time.time() - t0:.1f}s -> {out}", flush=True)
    return out


def _video_job(sid):
    try:
        return video(sid)
    except Exception as e:  # pragma: no cover
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        for p in still(sys.argv[2], sys.argv[3:]):
            print(p)
    elif mode == "sheet":
        print(sheet(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 4.0))
    elif mode == "video":
        for sid in sys.argv[2:]:
            video(sid)
    elif mode == "all":
        jobs = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        ids = sys.argv[3:] or SCENE_MODULES
        with Pool(jobs) as pool:
            for r in pool.imap_unordered(_video_job, ids):
                print("finished", r, flush=True)
