#!/usr/bin/env python3
"""Subtitles from audio/cues.json (real sentence timings): SRT sidecar + styled ASS for burn-in.

    python audio/subtitles.py                    # full film  -> audio/subtitles.srt / .ass
    python audio/subtitles.py --t0 0 --t1 90 --ass audio/test.ass   # a time slice, re-based to 0

Cues are wrapped to <= 2 lines of ~58 characters; longer sentences are split at punctuation in proportion to length.
The ASS style keeps text inside the bottom 12 % band that the scenes leave free (content ends at y = -3.6 of 4.5)."""
from __future__ import annotations
import argparse
import json
import os
import re
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
CUES = os.path.join(HERE, "cues.json")
WIDTH, MAX_LINES = 58, 2
HOLD = 0.25            # keep a cue on screen slightly past the last word


def split_cue(text: str, max_chars: int = WIDTH * MAX_LINES - 8) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    # split at the punctuation nearest the middle; recurse
    idx = [m.end() for m in re.finditer(r"[,;:](?=\s)", text)]
    if not idx:
        idx = [m.end() for m in re.finditer(r"\s", text)]
    mid = len(text) / 2
    cut = min(idx, key=lambda i: abs(i - mid))
    left, right = text[:cut].strip(), text[cut:].strip()
    return split_cue(left, max_chars) + split_cue(right, max_chars)


def expand(cues, t0=0.0, t1=1e9):
    out = []
    for c in cues:
        if c["end"] <= t0 or c["start"] >= t1:
            continue
        parts = split_cue(c["text"])
        total = sum(len(p) for p in parts)
        dur = c["end"] - c["start"] + HOLD
        t = c["start"]
        for p in parts:
            d = dur * len(p) / total
            out.append((t - t0, min(t + d, c["end"] + HOLD) - t0, "\n".join(textwrap.wrap(p, WIDTH))))
            t += d
    # never let a held cue overlap the next one (ASS would stack the two on screen)
    out.sort(key=lambda e: e[0])
    out = [(a, min(b, out[i + 1][0] - 0.03) if i + 1 < len(out) else b, txt) for i, (a, b, txt) in enumerate(out)]
    return [(a, max(b, a + 0.3), txt) for a, b, txt in out]


def srt_time(t: float) -> str:
    t = max(t, 0.0)
    h, rem = divmod(int(t), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{int(round((t - int(t)) * 1000)):03d}"


def ass_time(t: float) -> str:
    t = max(t, 0.0)
    h, rem = divmod(int(t), 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}.{int(round((t - int(t)) * 100)):02d}"


ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Liberation Sans,34,&H00FFFFFF,&H000000FF,&H00101010,&H90000000,-1,0,0,0,100,100,0,0,1,3,0,2,140,140,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def write(cues, srt_path=None, ass_path=None, t0=0.0, t1=1e9):
    ev = expand(cues, t0, t1)
    if srt_path:
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, (a, b, txt) in enumerate(ev, 1):
                f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n\n")
    if ass_path:
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ASS_HEADER)
            for a, b, txt in ev:
                f.write(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Default,,0,0,0,,{txt.replace(chr(10), chr(92) + 'N')}\n")
    return len(ev)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--t1", type=float, default=1e9)
    ap.add_argument("--srt", default=os.path.join(HERE, "subtitles.srt"))
    ap.add_argument("--ass", default=os.path.join(HERE, "subtitles.ass"))
    a = ap.parse_args()
    cues = json.load(open(CUES))
    n = write(cues, a.srt, a.ass, a.t0, a.t1)
    print(f"{n} subtitle cues -> {a.srt}, {a.ass}")


if __name__ == "__main__":
    main()
