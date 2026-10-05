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
    ap.add_argument("--reuse", action="store_true", help="keep per-chapter clips already encoded in build/tmp_<tag> (audio/subtitle-only changes)")
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
        if a.reuse and os.path.exists(out):
            parts.append(out)
            continue
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
    # mono -> stereo FIRST: duplicating channels after loudnorm would add +3 LU. Then a measured two-pass loudnorm
    # (single-pass is inaccurate on speech with long pauses): measure the slice, apply the measured values linearly.
    pre = "aresample=48000,pan=stereo|c0=c0|c1=c0"
    ln = "loudnorm=I=-16:TP=-1.5:LRA=11"
    meas = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-ss", f"{t0}", "-t", f"{t1 - t0}", "-i", narr,
                           "-af", f"{pre},{ln}:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    af = (f"{pre},{ln}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")
    print(f"narration {m['input_i']} LUFS (stereo) -> -16 LUFS two-pass", flush=True)
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
