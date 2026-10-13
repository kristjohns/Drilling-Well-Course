#!/bin/sh
# Contact sheets from the final video: one frame every $2 seconds, 5x5 tiles per sheet, timestamps burned in.
# usage: review_sheets.sh <video.mp4> [interval_s]
set -e
V="$1"; I="${2:-4}"
OUT="$(dirname "$0")/../build/review"
mkdir -p "$OUT"; rm -f "$OUT"/sheet_*.png
ffmpeg -hide_banner -loglevel error -y -i "$V" -vf "fps=1/$I,scale=480:-1,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='%{pts\:hms}':x=6:y=6:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=5x5" "$OUT/sheet_%02d.png"
ls "$OUT"
