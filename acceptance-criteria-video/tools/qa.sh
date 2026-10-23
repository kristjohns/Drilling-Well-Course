#!/usr/bin/env bash
# QA of the final encodes: streams, durations against the timeline, sizes, chapters, subtitle cues, loudness,
# and a contact sheet per part (one frame every 6 s) in build/qa/.
#   bash tools/qa.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/qa
TOTAL=0
for f in out/acceptance-criteria_part*_1080p.mp4; do
  b=$(basename "$f" .mp4)
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  s=$(stat -c %s "$f")
  TOTAL=$(python3 -c "print($TOTAL + $d)")
  echo "== $b  $(python3 -c "print(f'{$d:.2f} s, {$s / 2**20:.1f} MiB')")"
  ffprobe -v error -show_entries stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels -of compact=p=0:nk=1 "$f"
  echo "chapters: $(ffprobe -v error -show_chapters -of csv=p=0 "$f" | wc -l)   subtitle cues: $(ffmpeg -v error -i "$f" -map 0:s:0 -f srt - | grep -c -- '-->')"
  ffmpeg -hide_banner -nostats -i "$f" -map 0:a:0 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)" | tr -s ' ' | paste -sd' '
  [ "$s" -gt 104857600 ] && echo "WARNING: $f is larger than 100 MiB"
  ffmpeg -v error -y -i "$f" -vf "fps=1/6,scale=384:-1,tile=5x8:padding=4" -q:v 4 "build/qa/${b}_%02d.jpg"
done
python3 - "$TOTAL" <<'EOF'
import json, sys
d = json.load(open('src/data/timeline.json'))['duration']
print(f'parts total {float(sys.argv[1]):.2f} s vs timeline {d:.2f} s')
EOF
ls build/qa | head -40
