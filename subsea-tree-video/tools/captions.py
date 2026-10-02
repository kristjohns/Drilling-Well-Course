#!/usr/bin/env python3
"""Captions + chapters from the narration timings.

  python3 tools/captions.py   -> out/subsea-tree.srt, out/subsea-tree.vtt, build/captions.ass, build/chapters.ffmeta

Cue text = the display text of each narration beat, split at sentence / clause boundaries into
cues of at most two balanced lines (<= 42 characters per line).
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(f'{ROOT}/src/data/timings.json'))
DUR = T['meta']['duration']
MAXLINE, MAXCHARS = 42, 84
os.makedirs(f'{ROOT}/out', exist_ok=True)
os.makedirs(f'{ROOT}/build', exist_ok=True)


def split_beat(beat):
    """-> list of (i0, i1) word index ranges"""
    words = beat['words']
    out, i0, chars = [], 0, 0
    for i, w in enumerate(words):
        chars += len(w['w']) + 1
        tok = w['w']
        last = i == len(words) - 1
        sentence_end = bool(re.search(r'[.!?]["”)]?$', tok))
        clause_end = bool(re.search(r'[,;:]$', tok))
        n_words = i - i0 + 1
        brk = False
        if last:
            brk = True
        elif sentence_end and n_words >= 3 and chars >= 18:
            brk = True
        elif clause_end and chars >= 52:
            brk = True
        elif chars >= MAXCHARS:
            brk = True
        if brk:
            out.append((i0, i))
            i0, chars = i + 1, 0
    return out


def balance(text):
    """split into at most two balanced lines"""
    if len(text) <= MAXLINE:
        return [text]
    words = text.split(' ')
    best, bd = None, 1e9
    for k in range(1, len(words)):
        a, b = ' '.join(words[:k]), ' '.join(words[k:])
        if max(len(a), len(b)) > MAXLINE + 6:
            continue
        d = abs(len(a) - len(b))
        if d < bd:
            best, bd = [a, b], d
    return best or [text]


cues = []
for sc in T['scenes']:
    for bid in sc['order']:
        b = sc['beats'][bid]
        words = b['words']
        for i0, i1 in split_beat(b):
            text = ' '.join(w['w'] for w in words[i0:i1 + 1])
            start = b['start'] + words[i0]['s'] - 0.06
            end = b['start'] + words[i1]['e'] + 0.30
            cues.append({'start': max(0.0, start), 'end': end, 'lines': balance(text)})
cues.sort(key=lambda c: c['start'])
# tidy timing: no overlaps, minimum duration, hold a little longer for long cues
for i, c in enumerate(cues):
    nxt = cues[i + 1]['start'] if i + 1 < len(cues) else DUR
    c['end'] = min(c['end'], nxt - 0.04, DUR)
    if c['end'] - c['start'] < 1.0:
        c['end'] = min(c['start'] + 1.0, nxt - 0.04)


def ts(t, sep=','):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}'


with open(f'{ROOT}/out/subsea-tree.srt', 'w', encoding='utf-8') as f:
    for i, c in enumerate(cues, 1):
        f.write(f'{i}\n{ts(c["start"])} --> {ts(c["end"])}\n' + '\n'.join(c['lines']) + '\n\n')
with open(f'{ROOT}/out/subsea-tree.vtt', 'w', encoding='utf-8') as f:
    f.write('WEBVTT\n\n')
    for i, c in enumerate(cues, 1):
        f.write(f'{i}\n{ts(c["start"], ".")} --> {ts(c["end"], ".")}\n' + '\n'.join(c['lines']) + '\n\n')


# ---- ASS (burned-in captions: Inter, bottom centre, safe margins)
def ass_ts(t):
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f'{h}:{m:02d}:{s:02d}.{cs:02d}'


ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Inter,42,&H00FFFFFF,&H00FFFFFF,&HE6140A04,&H80000000,1,0,0,0,100,100,0,0,1,4.5,1.5,2,160,160,24,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
for c in cues:
    ass += f'Dialogue: 0,{ass_ts(c["start"])},{ass_ts(c["end"])},Default,,0,0,0,,' + '\\N'.join(c['lines']).replace('{', '(').replace('}', ')') + '\n'
open(f'{ROOT}/build/captions.ass', 'w', encoding='utf-8').write(ass)

# ---- chapters (ffmetadata)
chap = [(s['start'], s['chapter']) for s in T['scenes'] if s.get('chapter')]
meta = ';FFMETADATA1\ntitle=The Subsea Christmas Tree: How It Works\nartist=\ncomment=Educational animation. Schematic illustrations; verify details against current company requirements.\n'
for i, (t0, name) in enumerate(chap):
    t1 = chap[i + 1][0] if i + 1 < len(chap) else DUR
    meta += f'\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(t0 * 1000)}\nEND={int(t1 * 1000)}\ntitle={name}\n'
open(f'{ROOT}/build/chapters.ffmeta', 'w', encoding='utf-8').write(meta)

# ---- transcript (markdown) grouped by chapter
def mmss(t):
    return f'{int(t // 60):02d}:{int(t % 60):02d}'


tr = ['# The Subsea Christmas Tree: How It Works — transcript', '', f'Running time {mmss(DUR)}. Timestamps are mm:ss.', '']
cur = None
for sc in T['scenes']:
    if sc.get('chapter') and sc['chapter'] != cur:
        cur = sc['chapter']
        tr += ['', f'## {mmss(sc["start"])}  {cur}', '']
    for bid in sc['order']:
        b = sc['beats'][bid]
        tr.append(f'**[{mmss(b["start"])}]** {b["text"]}  ')
open(f'{ROOT}/out/subsea-tree_transcript.md', 'w', encoding='utf-8').write('\n'.join(tr) + '\n')

# ---- font for libass: convert Inter (woff2 from @fontsource) to TTF
fdir = f'{ROOT}/build/fonts'
os.makedirs(fdir, exist_ok=True)
try:
    from fontTools.ttLib import TTFont
    for wgt in (400, 700):
        src = f'{ROOT}/node_modules/@fontsource/inter/files/inter-latin-{wgt}-normal.woff2'
        f = TTFont(src)
        f.flavor = None
        f.save(f'{fdir}/Inter-{wgt}.ttf')
    print('fonts converted')
except Exception as e:  # noqa
    print('font conversion skipped:', e)

print(f'{len(cues)} cues; longest {max(c["end"] - c["start"] for c in cues):.1f}s; chapters {len(chap)}')
