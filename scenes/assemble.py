#!/usr/bin/env python3
"""Assemble rendered chapter frames + narration + subtitles into the final video with ffmpeg.

    python scenes/assemble.py                                  # full film from renders/final -> build/
    python scenes/assemble.py --renders renders/preview --chapters 0 --tag preview   # test a slice

Per chapter: frames.txt (concat list with hold durations) -> constant 24 fps H.264. Chapters are concatenated, the
narration is loudness-normalised (EBU R128, -16 LUFS) and muxed, and a second pass burns the subtitles in.
Outputs in build/:  <name>_<tag>.mp4 (burned-in subtitles), <name>_<tag>_nosubs.mp4 (stream-copied video), <name>.srt"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
NAME = "the_hole_that_fights_back"


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run(cmd, check=True, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", default=os.path.join(ROOT, "renders", "final"))
    ap.add_argument("--chapters", default=None, help="comma list, default all (must be contiguous)")
    ap.add_argument("--out", default=os.path.join(ROOT, "build"))
    ap.add_argument("--tag", default="1080p")
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--skip-subbed", action="store_true")
    a = ap.parse_args()
    tl = json.load(open(os.path.join(ROOT, "script", "timeline.json")))
    chs = [c for c in tl["chapters"] if a.chapters is None or c["num"] in [int(x) for x in a.chapters.split(",")]]
    t0, t1 = chs[0]["start"], chs[-1]["start"] + chs[-1]["dur"]
    os.makedirs(a.out, exist_ok=True)
    tmp = os.path.join(a.out, f"tmp_{a.tag}")
    os.makedirs(tmp, exist_ok=True)
    # 1. per-chapter silent video, constant 24 fps
    parts = []
    for c in chs:
        d = os.path.join(a.renders, f"ch{c['num']:02d}")
        out = os.path.join(tmp, f"ch{c['num']:02d}.mp4")
        if not os.path.exists(os.path.join(d, "frames.txt")):
            sys.exit(f"missing {d}/frames.txt: render chapter {c['num']} first")
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(d, "frames.txt"),
             "-vf", "fps=24,format=yuv420p", "-t", f"{c['dur']}", "-c:v", "libx264", "-preset", "veryfast", "-crf", str(a.crf), "-an", out])
        parts.append(out)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    video = os.path.join(tmp, "video_all.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])
    # 2. subtitles for this time slice (re-based to 0)
    sys.path.insert(0, os.path.join(ROOT, "audio"))
    import subtitles
    cues = json.load(open(os.path.join(ROOT, "audio", "cues.json")))
    ass, srt = os.path.join(tmp, "subs.ass"), os.path.join(a.out, f"{NAME}_{a.tag}.srt")
    n = subtitles.write(cues, srt, ass, t0, t1)
    print(f"{n} subtitle cues")
    # 3. narration slice, loudness-normalised, mono -> stereo, 48 kHz
    narr = os.path.join(ROOT, "audio", "narration.wav")
    af = "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,pan=stereo|c0=c0|c1=c0"
    nosubs = os.path.join(a.out, f"{NAME}_{a.tag}_nosubs.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-ss", f"{t0}", "-t", f"{t1 - t0}", "-i", narr,
         "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", af, "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", nosubs])
    if not a.skip_subbed:
        final = os.path.join(a.out, f"{NAME}_{a.tag}.mp4")
        # the ass filter wants a plain path: run from the tmp dir
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-ss", f"{t0}", "-t", f"{t1 - t0}", "-i", narr,
             "-vf", "ass=subs.ass", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf + 1),
             "-pix_fmt", "yuv420p", "-af", af, "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", final], cwd=tmp)
        print("final:", final)
    print("no-subs:", nosubs, "| srt:", srt)


if __name__ == "__main__":
    main()
