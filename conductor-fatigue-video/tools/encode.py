#!/usr/bin/env python3
"""Final encodes from the silent render (build/render/video.mp4) and the mix (build/audio/mix.wav).

  python3 tools/encode.py               -> out/conductor-fatigue_partN_1080p.mp4 (five parts, cut at chapter boundaries)
  python3 tools/encode.py --full        -> also build/conductor-fatigue_full_1080p.mp4 (one file, too big for GitHub)
  TARGET_MB=92 PRESET=slow python3 tools/encode.py
  python3 tools/encode.py --force       -> re-encode parts that are already newer than the render and the mix
  python3 tools/encode.py --parts=1,3   -> only these parts (VIDEO=... picks another silent render, e.g. a partial concat)

Each part is a two-pass, size-targeted x264 encode that stays below GitHub's 100 MiB file limit, with AAC audio, a soft
English subtitle track and chapter markers. out/poster.png is a still of the title card.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
TL = json.load(open('src/data/timeline.json'))
DUR = TL['duration']
CH = {c['no']: c for c in TL['chapters']}
NAME = 'conductor-fatigue'
PRESET = os.environ.get('PRESET', 'slow')
TARGET_MB = float(os.environ.get('TARGET_MB', '92'))
AUDIO_K = 160
V, A = os.environ.get('VIDEO', 'build/render/video.mp4'), 'build/audio/mix.wav'
PARTS = [(0, 2), (3, 4), (5, 6), (7, 8), (9, 10)]          # chapter ranges
# what x264's own CLI does for a first pass (x264_param_apply_fastfirstpass): only the stats matter there
FAST_FIRST = 'ref=1:no-8x8dct=1:partitions=none:me=dia:subme=2:trellis=0:fast-pskip=1'


def chap_title(c):
    return 'Cold open' if c['no'] == 0 else f'{c["no"]:02d} {c["title"]}'


def srt_cues():
    out = []
    for block in open(f'out/{NAME}.srt', encoding='utf-8').read().strip().split('\n\n'):
        lines = block.split('\n')
        a, b = lines[1].split(' --> ')
        tsec = lambda s: int(s[:2]) * 3600 + int(s[3:5]) * 60 + int(s[6:8]) + int(s[9:12]) / 1000
        out.append((tsec(a), tsec(b), lines[2:]))
    return out


def ts(t):
    ms = int(round(max(t, 0) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


def x264(vk):
    return ['-c:v', 'libx264', '-preset', PRESET, '-tune', 'animation', '-b:v', f'{vk}k', '-maxrate', '6000k', '-bufsize', '12000k',
            '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.1', '-g', '60', '-bf', '3',
            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv']


def encode(t0, t1, out, title, chapters, cues, target_mb):
    d = t1 - t0
    # resume after an interruption: a part newer than both inputs is kept (--force re-encodes everything)
    if '--force' not in sys.argv and os.path.exists(out) and os.path.getmtime(out) > max(os.path.getmtime(V), os.path.getmtime(A)):
        print(f'{out}: up to date', flush=True)
        return
    vk = int(target_mb * 8388.608 / d - AUDIO_K - 8)
    base = os.path.splitext(os.path.basename(out))[0]
    srt, meta, log = f'build/parts/{base}.srt', f'build/parts/{base}.ffmeta', f'build/parts/{base}_x264'
    tmp = f'build/parts/{base}.partial.mp4'
    with open(srt, 'w', encoding='utf-8') as f:
        k = 0
        for a, b, lines in cues:
            if b <= t0 or a >= t1:
                continue
            k += 1
            f.write(f'{k}\n{ts(a - t0)} --> {ts(min(b, t1) - t0)}\n' + '\n'.join(lines) + '\n\n')
    m = f';FFMETADATA1\ntitle={title}\nartist=Conductor fatigue tutorial (NORSOK U-001:2026)\n' \
        'comment=The worked example uses illustrative teaching inputs, not project data.\n'
    for c in chapters:
        a, b = max(c['start'], t0) - t0, min(c['end'], t1) - t0
        m += f'\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(a * 1000)}\nEND={int(b * 1000)}\ntitle={chap_title(c)}\n'
    open(meta, 'w', encoding='utf-8').write(m)
    print(f'{out}: {d:.1f} s, picture {vk} kbit/s', flush=True)
    common = ['-ss', f'{t0:.3f}', '-to', f'{t1:.3f}', '-i', V]
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-stats', *common, '-an', *x264(vk),
                    '-x264-params', f'aq-mode=3:aq-strength=0.8:pass=1:stats={log}.log:{FAST_FIRST}', '-f', 'null', '/dev/null'], check=True)
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-stats', *common, '-ss', f'{t0:.3f}', '-to', f'{t1:.3f}', '-i', A,
                    '-i', srt, '-i', meta, '-map', '0:v', '-map', '1:a', '-map', '2:s', '-map_metadata', '3', '-map_chapters', '3',
                    *x264(vk), '-x264-params', f'aq-mode=3:aq-strength=0.8:pass=2:stats={log}.log',
                    '-c:a', 'aac', '-b:a', f'{AUDIO_K}k', '-ar', '48000', '-af', f'afade=t=in:d=0.3,afade=t=out:st={d - 0.4:.3f}:d=0.4',
                    '-c:s', 'mov_text', '-metadata:s:s:0', 'language=eng', '-metadata:s:s:0', 'title=English', '-metadata:s:a:0', 'language=eng',
                    '-movflags', '+faststart', tmp], check=True)
    os.replace(tmp, out)                     # out/ only ever holds finished files
    size = os.path.getsize(out)
    print(f'  -> {size / 2 ** 20:.1f} MiB', flush=True)
    if size > 100 * 2 ** 20:
        print('  WARNING: larger than 100 MiB (GitHub file limit)')


def main():
    os.makedirs('out', exist_ok=True)
    os.makedirs('build/parts', exist_ok=True)
    cues = srt_cues()
    only = next((a.split('=')[1] for a in sys.argv if a.startswith('--parts=')), None)
    for i, (c0, c1) in enumerate(PARTS, 1):
        if only and str(i) not in only.split(','):
            continue
        t0 = CH[c0]['start']
        t1 = CH[c1]['end'] if c1 < max(CH) else DUR
        chs = [CH[k] for k in range(c0, c1 + 1)]
        names = ', '.join(chap_title(c) for c in chs)
        encode(t0, t1, f'out/{NAME}_part{i}_1080p.mp4', f'Conductor fatigue, NORSOK U-001 · part {i} of {len(PARTS)} · {names}', chs, cues, TARGET_MB)
    if '--full' in sys.argv:
        encode(0, DUR, f'build/{NAME}_full_1080p.mp4', 'Fatigue of the conductor and the conductor-template interface (NORSOK U-001:2026)',
               [CH[k] for k in sorted(CH)], cues, float(os.environ.get('FULL_MB', '700')))
    # poster: the cold-open title card
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-ss', f'{CH[0]["beats"][2]["start"] + 9.0:.2f}', '-i', V, '-frames:v', '1',
                    '-vf', 'scale=in_range=tv:in_color_matrix=bt709,format=rgb24', 'out/poster.png'], check=True)
    for f in sorted(os.listdir('out')):
        print(f'{f:48s} {os.path.getsize(os.path.join("out", f)) / 2 ** 20:8.1f} MiB')


if __name__ == '__main__':
    main()
