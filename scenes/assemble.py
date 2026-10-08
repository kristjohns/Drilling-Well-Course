#!/usr/bin/env python3
"""Assemble the rendered chapters, the audio mix and the subtitles into the final video.

    python scenes/assemble.py                 # renders/video/chNN.mp4 + audio/mix.wav -> build/
    python scenes/assemble.py --small         # also a compact 720p copy (< 30 MiB per part) for sharing in chat

Steps: concatenate the chapter videos (stream copy; every chapter is a whole number of frames, so nothing drifts),
check durations against script/timeline.json, normalise the mix to -16 LUFS with a measured two-pass loudnorm,
mux, then burn in the subtitles for the main deliverable.
Outputs in build/: <name>_1080p.mp4 (burned-in subtitles), <name>_1080p_nosubs.mp4, <name>_1080p.srt
"""
from __future__ import annotations
import argparse
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
NAME = "the_hole_that_fights_back"


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd)[:240], flush=True)
    subprocess.run(cmd, check=True, **kw)


def probe_dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def loudnorm_filter(src, pre=""):
    ln = "loudnorm=I=-16:TP=-1.5:LRA=11"
    meas = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", src, "-af", f"{pre}{ln}:print_format=json", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    m = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    print(f"mix measured {m['input_i']} LUFS, true peak {m['input_tp']} dBTP -> -16 LUFS", flush=True)
    return (f"{pre}{ln}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
            f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", default=os.path.join(ROOT, "renders", "video"))
    ap.add_argument("--out", default=os.path.join(ROOT, "build"))
    ap.add_argument("--audio", default=os.path.join(ROOT, "audio", "mix.wav"))
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--small", action="store_true")
    ap.add_argument("--skip-subbed", action="store_true")
    ap.add_argument("--small-only", action="store_true",
                    help="only the 720p parts, from an existing no-subs master, burning the subtitles in at 720p")
    a = ap.parse_args()
    tl = json.load(open(os.path.join(ROOT, "script", "timeline.json")))
    os.makedirs(a.out, exist_ok=True)
    if a.small_only:
        tmp = os.path.join(a.out, "tmp")
        os.makedirs(tmp, exist_ok=True)
        sys.path.insert(0, os.path.join(ROOT, "audio"))
        import subtitles
        cues = json.load(open(os.path.join(ROOT, "audio", "cues.json")))
        subtitles.write(cues, os.path.join(a.out, f"{NAME}_1080p.srt"), os.path.join(tmp, "subs.ass"), 0.0, tl["total"])
        small(os.path.join(a.out, f"{NAME}_1080p_nosubs.mp4"), a.out, tl["total"], subs_dir=tmp)
        return
    tmp = os.path.join(a.out, "tmp")
    os.makedirs(tmp, exist_ok=True)
    # 1. chapters -> one video (stream copy)
    parts, drift = [], 0.0
    for c in tl["chapters"]:
        p = os.path.join(a.videos, f"ch{c['num']:02d}.mp4")
        if not os.path.exists(p):
            sys.exit(f"missing {p}: render chapter {c['num']} first (make render)")
        d = probe_dur(p)
        if abs(d - c["dur"]) > 0.05:
            sys.exit(f"{p}: {d:.3f}s but the timeline says {c['dur']:.3f}s - re-render it")
        drift += d - c["dur"]
        parts.append(p)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    video = os.path.join(tmp, "video_all.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])
    print(f"video {probe_dur(video):.2f}s (timeline {tl['total']:.2f}s, accumulated chapter drift {drift * 1000:.0f} ms)")
    # 2. subtitles
    sys.path.insert(0, os.path.join(ROOT, "audio"))
    import subtitles
    cues = json.load(open(os.path.join(ROOT, "audio", "cues.json")))
    ass, srt = os.path.join(tmp, "subs.ass"), os.path.join(a.out, f"{NAME}_1080p.srt")
    n = subtitles.write(cues, srt, ass, 0.0, tl["total"])
    print(f"{n} subtitle cues")
    # 3. audio: measured two-pass loudness normalisation
    af = loudnorm_filter(a.audio)
    aac = os.path.join(tmp, "mix.m4a")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.audio, "-af", af, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", aac])
    nosubs = os.path.join(a.out, f"{NAME}_1080p_nosubs.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", aac, "-map", "0:v", "-map", "1:a", "-c", "copy",
         "-shortest", "-movflags", "+faststart", nosubs])
    final = os.path.join(a.out, f"{NAME}_1080p.mp4")
    if not a.skip_subbed:
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", aac, "-vf", "ass=subs.ass", "-map", "0:v", "-map", "1:a",
             "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf), "-tune", "animation", "-pix_fmt", "yuv420p",
             "-c:a", "copy", "-shortest", "-movflags", "+faststart", final], cwd=tmp)
        print("final:", final, f"{os.path.getsize(final) / 2**20:.0f} MiB")
    print("no-subs:", nosubs, "| srt:", srt)
    if a.small:
        small(final if not a.skip_subbed else nosubs, a.out, tl["total"])


def small(src, outdir, total, limit_mib=29.0, vbr_target=480, subs_dir=None):
    """720p copy split into as many parts as needed for each to fit the chat upload limit at a decent bitrate
    (gradients, grain and particles smear below ~400 kbit/s at 720p)."""
    abr = 96
    parts = max(1, math.ceil(total * (vbr_target + abr) / 8 / 1024 / (limit_mib * 0.94)))
    seg = total / parts
    vbr = int((limit_mib * 8 * 1024 * 0.94) / seg - abr)     # kbit/s so each part fits
    out = []
    for i in range(parts):
        p = os.path.join(outdir, f"{NAME}_720p_part{i + 1}of{parts}.mp4")
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{i * seg:.3f}", "-t", f"{seg:.3f}", "-i", src,
             # input seeking restarts timestamps at 0: shift to film time for the subtitles, then back
             "-vf", "scale=1280:720:flags=lanczos" + (f",setpts=PTS+{i * seg:.3f}/TB,ass=subs.ass,setpts=PTS-STARTPTS" if subs_dir else ""),
             "-c:v", "libx264", "-preset", "slow", "-b:v", f"{vbr}k",
             "-maxrate", f"{int(vbr * 1.6)}k", "-bufsize", f"{vbr * 3}k", "-tune", "animation", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", f"{abr}k", "-ac", "2", "-movflags", "+faststart", p], cwd=subs_dir)
        out.append(p)
        print(f"small part {i + 1}: {os.path.getsize(p) / 2**20:.1f} MiB")
    return out


if __name__ == "__main__":
    main()
