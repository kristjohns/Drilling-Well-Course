"""Concatenate rendered scenes, mux the audio mix and soft subtitles into the final MP4.

  python3 src/assemble.py            -> output/well_integrity_ncs.mp4
"""
from __future__ import annotations

import os
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
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", joined, "-i", os.path.join(AUD, "mix.wav"),
                    "-i", os.path.join(AUD, "subtitles.srt"),
                    "-map", "0:v", "-map", "1:a", "-map", "2:s",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-c:s", "mov_text",
                    "-metadata", "title=Well Integrity on the Norwegian Continental Shelf",
                    "-metadata:s:a:0", "language=eng", "-metadata:s:s:0", "language=eng",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    print(out)


if __name__ == "__main__":
    main(*(sys.argv[1:]))
