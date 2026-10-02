#!/usr/bin/env bash
# Final encodes from the silent render + mixed audio. Two-pass, size-targeted x264, so each 1080p file stays
# below GitHub's 100 MiB file limit (default target 92 MiB, about 1 Mbit/s for the picture).
#   out/subsea-tree_1080p.mp4            clean picture, soft subtitle track + chapters
#   out/subsea-tree_1080p_captions.mp4   captions burned in
#   out/subsea-tree_720p.mp4             light copy for quick sharing (soft subtitles + chapters)
#   out/poster.png                       title-card still
#
#   bash tools/encode.sh                 (TARGET_MB=92 PRESET=slow)
#   TARGET_MB=140 bash tools/encode.sh   (larger files, more headroom for fine detail)
set -euo pipefail
cd "$(dirname "$0")/.."
PRESET="${PRESET:-slow}"
TARGET_MB="${TARGET_MB:-92}"     # MiB per 1080p file (picture + audio + subtitles)
AUDIO_K="${AUDIO_K:-160}"        # AAC kbit/s
V=build/render/video.mp4
A=build/audio_final.wav
mkdir -p out

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V")
VK=$(awk -v mb="$TARGET_MB" -v d="$DUR" -v a="$AUDIO_K" 'BEGIN { printf "%d", mb * 8388.608 / d - a - 8 }')
echo "target ${TARGET_MB} MiB over ${DUR} s -> picture ${VK} kbit/s + audio ${AUDIO_K} kbit/s"

X264=(-c:v libx264 -preset "$PRESET" -tune animation -b:v "${VK}k" -maxrate 4000k -bufsize 8000k
      -x264-params aq-mode=3:aq-strength=0.8 -pix_fmt yuv420p -profile:v high -level 4.1 -g 60 -bf 3
      -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv)
AUD=(-c:a aac -b:a "${AUDIO_K}k" -ar 48000)
GRAPH="[0:v]split=2[v1][v2];[v2]subtitles=build/captions.ass:fontsdir=build/fonts[vc]"
rm -f build/x264_clean-*.log* build/x264_caps-*.log*

echo "pass 1/2 …"
ffmpeg -y -hide_banner -loglevel error -stats -i "$V" -filter_complex "$GRAPH" \
  -map "[v1]" -an "${X264[@]}" -pass 1 -passlogfile build/x264_clean -f null /dev/null \
  -map "[vc]" -an "${X264[@]}" -pass 1 -passlogfile build/x264_caps -f null /dev/null

echo "pass 2/2 …"
ffmpeg -y -hide_banner -loglevel error -stats \
  -i "$V" -i "$A" -i out/subsea-tree.srt -i build/chapters.ffmeta -filter_complex "$GRAPH" \
  -map "[v1]" -map 1:a -map 2:s -map_metadata 3 -map_chapters 3 "${X264[@]}" -pass 2 -passlogfile build/x264_clean "${AUD[@]}" \
      -c:s mov_text -metadata:s:s:0 language=eng -metadata:s:s:0 title=English -metadata:s:a:0 language=eng \
      -movflags +faststart out/subsea-tree_1080p.mp4 \
  -map "[vc]" -map 1:a -map_metadata 3 -map_chapters 3 "${X264[@]}" -pass 2 -passlogfile build/x264_caps "${AUD[@]}" \
      -metadata:s:a:0 language=eng -movflags +faststart out/subsea-tree_1080p_captions.mp4

# poster: the title card (28.5 s in), taken from the near-lossless render
ffmpeg -y -hide_banner -loglevel error -ss 28.5 -i "$V" -frames:v 1 \
  -vf "scale=in_range=tv:in_color_matrix=bt709,format=rgb24" out/poster.png

# light 720p copy (from the render, constant quality, capped)
echo "720p copy …"
ffmpeg -y -hide_banner -loglevel error -stats -i "$V" -i "$A" -i out/subsea-tree.srt -i build/chapters.ffmeta \
  -map 0:v -map 1:a -map 2:s -map_metadata 3 -map_chapters 3 -vf scale=1280:720:flags=lanczos \
  -c:v libx264 -preset medium -crf 24 -tune animation -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -profile:v high -level 4.0 -g 60 \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  -c:a aac -b:a 128k -ar 48000 -c:s mov_text -metadata:s:s:0 language=eng -metadata:s:s:0 title=English -metadata:s:a:0 language=eng \
  -movflags +faststart out/subsea-tree_720p.mp4

ls -la out
for f in out/subsea-tree_1080p.mp4 out/subsea-tree_1080p_captions.mp4 out/subsea-tree_720p.mp4; do
  echo "$f"; ffprobe -v error -show_entries format=duration,size,bit_rate -of default=nw=1 "$f"
  [ "$(stat -c %s "$f")" -gt 104857600 ] && echo "WARNING: $f is larger than 100 MiB (GitHub's file limit)"
done
exit 0
