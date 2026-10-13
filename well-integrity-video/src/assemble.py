"""Concatenate rendered scenes, mux the audio mix and soft subtitles into the final MP4.

  python3 src/assemble.py            -> output/well_integrity_ncs.mp4
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from render import SCENE_MODULES  # noqa: E402

VID = os.path.join(ROOT, "build", "video")
AUD = os.path.join(ROOT, "build", "audio")
OUT = os.path.join(ROOT, "output")


def main(name="well_integrity_ncs.mp4"):
    os.makedirs(OUT, exist_ok=True)
    lst = os.path.join(VID, "concat.txt")
    with open(lst, "w") as f:
        for sid in SCENE_MODULES:
            p = os.path.join(VID, f"{sid}.mp4")
            assert os.path.exists(p), p
            f.write(f"file '{p}'\n")
    joined = os.path.join(VID, "joined.mp4")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", joined], check=True)
    out = os.path.join(OUT, name)
    # the output length comes from the video: -shortest would also stop at the last subtitle cue
    vdur = video_duration(joined)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", joined, "-i", os.path.join(AUD, "mix.wav"),
                    "-i", os.path.join(AUD, "subtitles.srt"),
                    "-map", "0:v", "-map", "1:a", "-map", "2:s",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-c:s", "mov_text",
                    "-metadata", "title=Well Integrity on the Norwegian Continental Shelf",
                    "-metadata:s:a:0", "language=eng", "-metadata:s:s:0", "language=eng",
                    "-t", f"{vdur:.3f}", "-movflags", "+faststart", out], check=True)
    shutil.copyfile(os.path.join(AUD, "subtitles.srt"), os.path.join(OUT, "subtitles.srt"))
    print(out)


def video_duration(path):
    """Exact video length from the frame count."""
    n = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                        "stream=nb_read_packets", "-of", "csv=p=0", path], check=True, capture_output=True, text=True)
    return int(n.stdout.strip()) / 30.0


def fmt_ts(sec):
    ms = int(round(max(0.0, sec) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_srt(path):
    def ts(x):
        h, m, rest = x.split(":")
        sec, ms = rest.split(",")
        return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
    cues = []
    for block in open(path).read().strip().split("\n\n"):
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            a, b = lines[1].split(" --> ")
            cues.append((ts(a), ts(b), "\n".join(lines[2:])))
    return cues


def chapters():
    """One MP4 per chapter (credits appended to the last chapter), for course use."""
    import json
    from engine.scene import CREDITS_DUR
    tl = json.load(open(os.path.join(AUD, "timeline.json")))
    ids = list(tl.keys())
    starts, acc = {}, 0.0
    for i in ids:
        starts[i] = acc
        acc += tl[i]["duration"]
    names = {
        "s00_open": "00_introduction", "s01_definition": "01_what_is_well_integrity", "s02_framework": "02_norwegian_framework",
        "s03_barriers": "03_barrier_philosophy", "s04_verify": "04_verification_and_testing", "s05_annulus": "05_annulus_pressure_management",
        "s06_classify": "06_classifying_well_integrity", "s07_failures": "07_when_barriers_fail", "s08_pa": "08_plug_and_abandonment",
        "s09_ccs": "09_co2_storage", "s10_future": "10_digital_and_key_lessons",
    }
    main_cues = parse_srt(os.path.join(AUD, "subtitles.srt"))
    cdir = os.path.join(OUT, "chapters")
    os.makedirs(cdir, exist_ok=True)
    for sid in ids:
        parts = [os.path.join(VID, f"{sid}.mp4")]
        dur = tl[sid]["duration"]
        if sid == ids[-1]:
            parts.append(os.path.join(VID, "s11_credits.mp4"))
            dur += CREDITS_DUR
        lst = os.path.join(VID, f"concat_{sid}.txt")
        with open(lst, "w") as f:
            for p in parts:
                f.write(f"file '{p}'\n")
        # subtitles for this chapter: entries of the main SRT inside the chapter window, shifted
        srt = os.path.join(VID, f"{sid}.srt")
        k = 1
        with open(srt, "w") as f:
            for (g0, g1, text) in main_cues:
                if starts[sid] - 0.01 <= g0 < starts[sid] + dur:
                    f.write(f"{k}\n{fmt_ts(g0 - starts[sid])} --> {fmt_ts(g1 - starts[sid])}\n{text}\n\n")
                    k += 1
        out = os.path.join(cdir, f"{names[sid]}.mp4")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-ss", f"{starts[sid]:.3f}", "-t", f"{dur:.3f}", "-i", os.path.join(AUD, "mix.wav"), "-i", srt,
                        "-map", "0:v", "-map", "1:a", "-map", "2:s", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-c:s", "mov_text", "-metadata", f"title=Well Integrity - {tl[sid]['title']}",
                        "-metadata:s:s:0", "language=eng", "-t", f"{dur:.3f}", "-movflags", "+faststart", out], check=True)
        print(out, os.path.getsize(out) // 1_000_000, "MB")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "chapters":
        chapters()
    else:
        main(*(sys.argv[1:]))
