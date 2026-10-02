#!/usr/bin/env bash
# Post-encode checks: streams, chapters, subtitle track, loudness, sample frames (build/qa/)
set -euo pipefail
cd "$(dirname "$0")/.."
F="${1:-out/subsea-tree_1080p.mp4}"
echo "== streams"; ffprobe -v error -show_entries stream=index,codec_type,codec_name,width,height,r_frame_rate,pix_fmt,color_space,color_primaries,color_transfer,sample_rate,channels,bit_rate,duration -of compact "$F"
echo "== format"; ffprobe -v error -show_entries format=duration,size,bit_rate -of default=nw=1 "$F"
echo "== chapters"; ffprobe -v error -show_chapters -of compact=p=0:nk=1 "$F" | awk -F'|' '{printf "%s  %s\n", $5, $7}' | head -20 || true
echo "== loudness"; ffmpeg -hide_banner -nostats -i "$F" -vn -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=summary -f null - 2>&1 | grep -E "Input (Integrated|True Peak|LRA)" || true
mkdir -p build/qa; rm -f build/qa/*.png
for t in 3 28 75 140 200 245 300 345 380 410 455 478 505 530 575 600 622 655 673; do
  ffmpeg -y -hide_banner -loglevel error -ss $t -i "$F" -frames:v 1 "build/qa/q_$(printf %04d $t).png"
done
montage build/qa/q_*.png -tile 4x -geometry 480x270+3+3 -background '#111' build/qa/contact.png
echo "contact sheet: build/qa/contact.png"
