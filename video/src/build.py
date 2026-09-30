"""Final assembly: per-scene segments -> concatenated video + soundtrack + subtitles.

usage:
  python3 build.py segments [scene ...]   compose segments (default: all missing)
  python3 build.py final                  concat + mux + subtitles + chapters
  python3 build.py srt                    subtitles only
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as C  # noqa: E402
import scene_base  # noqa: E402
import script  # noqa: E402


def seg_path(sid):
    return os.path.join(C.SEGMENTS, sid + '.mp4')


def frames_complete(sid):
    sc = scene_base.load(sid)
    if not sc.BLENDER:
        return True
    d = os.path.join(C.FRAMES, sid)
    for a, b in sc.render_ranges():
        for f in range(a, b + 1):
            p = os.path.join(d, '%04d.png' % f)
            if not os.path.exists(p) or os.path.getsize(p) == 0:
                return False
    return True


def segments(ids=None, force=False):
    import compose
    ids = ids or scene_base.all_ids()
    for sid in ids:
        if os.path.exists(seg_path(sid)) and not force:
            print('have', sid)
            continue
        if not frames_complete(sid):
            print('frames incomplete, skip', sid)
            continue
        compose.compose(sid)


def fmt_ts(t):
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')


def srt(path=None):
    tl = json.load(open(C.TIMELINE))
    cues = []
    for sc in tl['scenes']:
        for b in sc['beats']:
            text = b['text']
            parts = re.split(r'(?<=[.!?])\s+', text)
            # distribute the beat duration over sentences by length
            total = sum(len(p) for p in parts) or 1
            t = b['start']
            for p in parts:
                d = (b['end'] - b['start']) * len(p) / total
                cues.append((t, t + d, p))
                t += d
    path = path or os.path.join(C.OUTPUT, 'subsea_well_lifecycle.en.srt')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fh:
        for i, (a, b, txt) in enumerate(cues, 1):
            fh.write(f'{i}\n{fmt_ts(a)} --> {fmt_ts(b)}\n{txt}\n\n')
    print('subtitles ->', path)
    return path


def chapters_meta(path):
    tl = json.load(open(C.TIMELINE))
    groups = [('Introduction', 's01_intro'), ('The setting', 's02_setting'),
              ('Design: the drilling window', 's03_pressure'), ('Design: casing', 's04_casing'),
              ('Design: two barriers', 's05_barriers'), ('Drilling: the rig', 's06_rig'),
              ('Drilling: top hole', 's07_tophole'), ('Drilling: the BOP', 's08_bop'),
              ('Drilling: mud, bit and steering', 's09_circulation'),
              ('Drilling: casing and cement', 's10_cementing'),
              ('Drilling: well control', 's11_wellcontrol'), ('Completion', 's12_completion'),
              ('Production', 's13_production'), ('Plug and abandonment', 's14_pa'),
              ('Recap', 's15_outro')]
    starts = {s['id']: (s['start'], s['end']) for s in tl['scenes']}
    with open(path, 'w') as fh:
        fh.write(';FFMETADATA1\ntitle=The Life of a Subsea Well\n'
                 'comment=Design, drilling, completion and P&A of a subsea well on the NCS\n\n')
        for title, sid in groups:
            a, b = starts[sid]
            fh.write(f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(a * 1000)}\nEND={int(b * 1000)}\n'
                     f'title={title}\n\n')


def final(crf=20, name='subsea_well_lifecycle_1080p.mp4', maxrate=None):
    import audio
    ids = scene_base.all_ids()
    missing = [s for s in ids if not os.path.exists(seg_path(s))]
    if missing:
        raise SystemExit(f'missing segments: {missing}')
    lst = os.path.join(C.BUILD, 'concat.txt')
    with open(lst, 'w') as fh:
        for sid in ids:
            fh.write(f"file '{seg_path(sid)}'\n")
    joined = os.path.join(C.BUILD, 'joined.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst,
                    '-c', 'copy', joined], check=True)
    snd = os.path.join(C.BUILD, 'soundtrack.wav')
    if not os.path.exists(snd):
        audio.build(snd)
    meta = os.path.join(C.BUILD, 'chapters.txt')
    chapters_meta(meta)
    os.makedirs(C.OUTPUT, exist_ok=True)
    out = os.path.join(C.OUTPUT, name)
    venc = ['-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-tune', 'animation',
            '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-movflags', '+faststart']
    if maxrate:
        venc += ['-maxrate', maxrate, '-bufsize', maxrate]
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', joined, '-i', snd, '-i', meta,
                    '-map', '0:v', '-map', '1:a', '-map_metadata', '2', '-map_chapters', '2'] + venc +
                   ['-c:a', 'aac', '-b:a', '160k', '-shortest', out], check=True)
    print('final ->', out, round(os.path.getsize(out) / 1e6, 1), 'MB')
    srt()
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    cmd = a[0] if a else 'final'
    if cmd == 'segments':
        segments(a[1:] or None, force='--force' in a)
    elif cmd == 'srt':
        srt()
    elif cmd == 'final':
        final()
