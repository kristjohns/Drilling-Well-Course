#!/usr/bin/env python3
"""Captions, chapters and transcript from the voice-timed timeline.

  python3 tools/captions.py   -> out/template-interface.srt / .vtt, out/template-interface_transcript.md,
                                 build/captions.ass (for burned-in captions), build/chapters.ffmeta
  python3 tools/captions.py --check   print every sentence whose caption text differs from the spoken text

The narration is written for the voice ("U zero zero one", "one point two nine"); captions show it the way it is
read: U-001, 1.29, S-N, DNV-RP-C203. The rewrite works on the timed word list, so merged tokens keep their timing.
Cues are cut at sentence and clause boundaries, at most two balanced lines of 42 characters.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, 'src', 'data', 'timeline.json')))
DUR = TL['duration']
NAME = 'template-interface'
MAXLINE, MAXCHARS = 42, 84

UNITS = {w: i for i, w in enumerate('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen '
                                    'fifteen sixteen seventeen eighteen nineteen'.split())}
TENS = {w: 10 * (i + 2) for i, w in enumerate('twenty thirty forty fifty sixty seventy eighty ninety'.split())}
DIGIT = {**{k: v for k, v in UNITS.items() if v < 10}, 'oh': 0}
SCALE = {'thousand': 1000, 'million': 10 ** 6}
UNIT_AFTER = {'metres', 'metre', 'millimetres', 'millimetre', 'mm', 'percent', 'degrees', 'megapascals', 'inch', 'years',
              'meganewtons', 'meganewton', 'kilonewton', 'kilonewtons', 'kilometres', 'bar'}
# multi-word replacements (matched on lower-case words without punctuation), longest first
PHRASES = [
    ('u zero zero one', 'U-001'), ('n zero zero one', 'N-001'), ('n zero zero four', 'N-004'), ('twenty twenty-six', '2026'),
    ('twenty twenty-five', '2025'), ('f e', 'FE'), ('f d', 'Fd'), ('f y', 'fy'), ('sigma y', 'σy'),
    ('i s o thirteen six twenty-eight part fifteen', 'ISO 13628-15'), ('s three fifty-five', 'S355'),
    ('e n nineteen ninety-three part one fourteen', 'EN 1993-1-14'), ('eurocode three', 'Eurocode 3'),
    ('part one five', 'part 1-5'), ('part one one', 'part 1-1'), ('figure j one', 'Figure J.1'),
    ('c six', 'C.6'), ('c seven', 'C.7'), ('c eight', 'C.8'), ('c nine', 'C.9'),
    ('gamma m zero', 'γM0'), ('gamma m one', 'γM1'), ('gamma m two', 'γM2'), ('gamma m', 'γM'),
    ('alpha u', 'αu'), ('alpha one', 'α1'), ('alpha two', 'α2'), ('alpha', 'α'),
    ('meganewton metres', 'MNm'), ('megapascals', 'MPa'), ('meganewtons', 'MN'),
]
PHRASES = sorted(((p.split(), r) for p, r in PHRASES), key=lambda x: -len(x[0]))


def bare(w):
    return re.sub(r"[^a-z0-9'\-]", '', w.lower())


def split_punct(w):
    m = re.match(r'^(.*?)([.,;:!?"”)]*)$', w)
    return m.group(1), m.group(2)


def parse_number(words, i, stop=()):
    """longest spoken number starting at words[i] -> (text, j) or None. words are bare lower-case; stop[k] is True when
    token k ends with punctuation (a number never runs across it)."""
    def simple(k):          # 0..99 at k (supports twenty-six / twenty six)
        w = words[k] if k < len(words) else ''
        if '-' in w:
            a, _, b = w.partition('-')
            if a in TENS and b in UNITS and UNITS[b] < 10:
                return TENS[a] + UNITS[b], k + 1
        if w in UNITS:
            return UNITS[w], k + 1
        if w in TENS:
            v = TENS[w]
            if k + 1 < len(words) and words[k + 1] in UNITS and 0 < UNITS[words[k + 1]] < 10:
                return v + UNITS[words[k + 1]], k + 2
            return v, k + 1
        return None

    def below_thousand(k):
        r = simple(k)
        if not r:
            return None
        v, k2 = r
        if k2 < len(words) and words[k2] == 'hundred':
            v *= 100
            k2 += 1
            if k2 + 1 < len(words) and words[k2] == 'and' and simple(k2 + 1) and not (simple(k2 + 1)[1] < len(words) and words[simple(k2 + 1)[1]] in ('hundred', 'thousand')):
                r2 = simple(k2 + 1)
                v += r2[0]
                k2 = r2[1]
            elif simple(k2):
                r2 = simple(k2)
                v += r2[0]
                k2 = r2[1]
        return v, k2

    r = below_thousand(i)
    if not r:
        return None
    total, k = r
    # "one hundred and eighty-seven and a half" -> 187.5
    if k + 2 < len(words) and words[k] == 'and' and words[k + 1] == 'a' and words[k + 2] == 'half' and not (k + 3 < len(words) and words[k + 3] in SCALE):
        return f'{total}.5', k + 3
    # two two-digit groups read as one four-digit number: "fourteen thirty-six" = 1436, "twenty-one twenty-four" = 2124
    if 10 <= total <= 99 and not stop[k - 1] and simple(k) and 10 <= simple(k)[0] <= 99 and \
            not (simple(k)[1] < len(words) and words[simple(k)[1]] in ('hundred', 'thousand', 'million', 'point')):
        total, k = total * 100 + simple(k)[0], simple(k)[1]
    whole = total
    # scales: "seven thousand four hundred", "seven and a half million"
    if k + 3 < len(words) and words[k] == 'and' and words[k + 1] == 'a' and words[k + 2] == 'half' and words[k + 3] in SCALE:
        return f'{total}.5 {words[k + 3]}', k + 4
    while k < len(words) and words[k] in SCALE:
        sc = words[k]
        k += 1
        rest = below_thousand(k) if k < len(words) else None
        if sc == 'million' and not rest:
            return (f'{whole:,}'.replace(',', ' ') + ' million'), k
        whole = whole * SCALE[sc]
        if rest:
            whole += rest[0]
            k = rest[1]
    # decimals: "one point two nine"
    if k + 1 < len(words) and words[k] == 'point' and words[k + 1] in DIGIT and not stop[k - 1]:
        ds = ''
        k += 1
        while k < len(words) and words[k] in DIGIT:
            ds += str(DIGIT[words[k]])
            k += 1
            if stop[k - 1]:
                break
        # clause numbers: "thirteen point three point six" -> 13.3.6
        while k + 1 < len(words) and words[k] == 'point' and words[k + 1] in DIGIT and not stop[k - 1]:
            ds += '.' + str(DIGIT[words[k + 1]])
            k += 2
        if k < len(words) and words[k] == 'million':
            return f'{whole}.{ds} million', k + 1
        return f'{whole}.{ds}', k
    return (f'{whole:,}'.replace(',', ' ') if whole >= 10000 else str(whole)), k


def rewrite(tokens):
    """tokens: [{'w','s','e'}] spoken words -> caption tokens"""
    out, i = [], 0
    words = [bare(t['w']) for t in tokens]
    stop = [bool(split_punct(t['w'])[1]) for t in tokens]
    while i < len(tokens):
        # "Table A seven" -> Table A.7, "Table four" -> Table 4, "class C one" -> class C1
        if words[i] in ('table', 'class') and i + 1 < len(tokens):
            ref = tokens[i + 1]['w']
            if len(bare(ref)) == 1 and bare(ref).isalpha() and i + 2 < len(tokens) and words[i + 2] in DIGIT and not stop[i + 1]:
                sep = '.' if words[i] == 'table' else ''
                out.append(dict(tokens[i]))
                out.append({'w': ref.upper() + sep + str(DIGIT[words[i + 2]]) + split_punct(tokens[i + 2]['w'])[1], 's': tokens[i + 1]['s'], 'e': tokens[i + 2]['e']})
                i += 3
                continue
            if words[i] == 'table' and words[i + 1] in DIGIT:
                out.append(dict(tokens[i]))
                out.append({'w': str(DIGIT[words[i + 1]]) + split_punct(tokens[i + 1]['w'])[1], 's': tokens[i + 1]['s'], 'e': tokens[i + 1]['e']})
                i += 2
                continue
        hit = None
        for pat, rep in PHRASES:
            n = len(pat)
            if words[i:i + n] == pat:
                hit = (rep, n)
                break
        if hit:
            rep, n = hit
            _, p = split_punct(tokens[i + n - 1]['w'])
            # keep a leading capital on sentence-initial words like "Delta"
            out.append({'w': rep + p, 's': tokens[i]['s'], 'e': tokens[i + n - 1]['e']})
            i += n
            continue
        # S-N class names: "C one" -> C1, "D one" -> D1 (upper-case class letters only)
        if re.fullmatch(r'[BCDEFGW]', split_punct(tokens[i]['w'])[0]) and i + 1 < len(tokens) and words[i + 1] in DIGIT and not stop[i] \
                and words[i + 1] != 'oh' and not (i + 2 < len(tokens) and words[i + 2] in ('point', 'hundred', 'thousand')):
            sep = '.' if tokens[i]['w'] == 'B' else ''            # B followed by a number is always a formula (B.3, B.8)
            out.append({'w': tokens[i]['w'] + sep + str(DIGIT[words[i + 1]]) + split_punct(tokens[i + 1]['w'])[1], 's': tokens[i]['s'], 'e': tokens[i + 1]['e']})
            i += 2
            continue
        num = parse_number(words, i, stop)
        if num:
            txt, j = num
            nxt = words[j] if j < len(words) else ''
            span = tokens[i:j]
            plain = ' '.join(t['w'] for t in span)
            is_dec = '.' in txt or 'million' in txt
            mnum = re.match(r'^\d+(\.\d+)?', txt.replace(' ', ''))
            val = float(mnum.group(0)) if mnum else 0
            small_start = i == 0 and len(span) == 1 and val < 10
            if (is_dec or val >= 10 or nxt in UNIT_AFTER) and not small_start and not (len(span) == 1 and val < 10 and not is_dec and nxt not in UNIT_AFTER):
                _, p = split_punct(span[-1]['w'])
                if nxt in ('percent',):
                    out.append({'w': txt + ' %' + split_punct(tokens[j]['w'])[1], 's': span[0]['s'], 'e': tokens[j]['e']})
                    i = j + 1
                    continue
                out.append({'w': txt + p, 's': span[0]['s'], 'e': span[-1]['e']})
                i = j
                continue
            # leave small stand-alone numbers as words
            out.extend(span)
            i = j
            continue
        out.append(dict(tokens[i]))
        i += 1
    # "clause B 4.2.4" -> clause B.4.2.4, "formula B 10" -> formula B.10
    k = 1
    while k + 1 < len(out):
        if re.fullmatch(r'[A-J]', out[k]['w']) and bare(out[k - 1]['w']) in ('clause', 'formula', 'formulas', 'table', 'annex') \
                and re.match(r'^\d[\d.]*', out[k + 1]['w']):
            out[k] = {'w': out[k]['w'] + '.' + out[k + 1]['w'], 's': out[k]['s'], 'e': out[k + 1]['e']}
            del out[k + 1]
        k += 1
    # capitalise the first word of the sentence again
    if out and re.match(r'[a-z]', out[0]['w'][:1]):
        out[0]['w'] = out[0]['w'][0].upper() + out[0]['w'][1:]
    return out


def cues_for(tokens):
    """split a sentence into cues of at most MAXCHARS: cut after the last clause mark that fits, otherwise at the word
    boundary that leaves no tiny tail -> list of token lists"""
    ln = lambda ts: sum(len(t['w']) + 1 for t in ts) - 1
    res, i = [], 0
    while i < len(tokens):
        j, L = i, -1
        while j < len(tokens) and L + len(tokens[j]['w']) + 1 <= MAXCHARS:
            L += len(tokens[j]['w']) + 1
            j += 1
        j = max(j, i + 1)
        if j >= len(tokens):
            res.append(tokens[i:])
            break
        marks = [k for k in range(i + 2, j) if re.search(r'[,;:]$', tokens[k]['w']) and ln(tokens[i:k + 1]) >= 28]
        if marks:
            k = marks[-1] + 1
        else:
            k = j
            if ln(tokens[j:]) < 30:          # a short remainder: cut the whole rest in two halves instead
                tot, acc, k = ln(tokens[i:]), 0, i + 1
                for m in range(i, len(tokens)):
                    acc += len(tokens[m]['w']) + 1
                    if acc >= tot / 2:
                        k = m + 1
                        break
        res.append(tokens[i:k])
        i = k
    return res


def balance(text):
    if len(text) <= MAXLINE:
        return [text]
    ws = text.split(' ')
    best, bd = [text], 1e9
    for k in range(1, len(ws)):
        a, b = ' '.join(ws[:k]), ' '.join(ws[k:])
        if max(len(a), len(b)) > MAXLINE + 6:
            continue
        d = abs(len(a) - len(b))
        if d < bd:
            best, bd = [a, b], d
    return best


def ts(t, sep=','):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}'


def main():
    check = '--check' in sys.argv
    cues, sents = [], []
    for c in TL['chapters']:
        for b in c['beats']:
            for s in b['sentences']:
                toks = rewrite(s['words'])
                spoken = ' '.join(w['w'] for w in s['words'])
                shown = ' '.join(w['w'] for w in toks)
                sents.append((c, b, s, shown))
                if check and spoken != shown:
                    print(f'{b["id"]:>5}  {spoken}\n       {shown}\n')
                for part in cues_for(toks):
                    text = ' '.join(t['w'] for t in part)
                    cues.append({'start': max(0.0, part[0]['s'] - 0.05), 'end': part[-1]['e'] + 0.35, 'lines': balance(text)})
    if check:
        return
    cues.sort(key=lambda x: x['start'])
    for i, cu in enumerate(cues):
        nxt = cues[i + 1]['start'] if i + 1 < len(cues) else DUR
        cu['end'] = min(cu['end'], nxt - 0.04, DUR)
        if cu['end'] - cu['start'] < 1.0:
            cu['end'] = min(cu['start'] + 1.0, nxt - 0.04)
    os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
    with open(os.path.join(ROOT, 'out', f'{NAME}.srt'), 'w', encoding='utf-8') as f:
        for i, cu in enumerate(cues, 1):
            f.write(f'{i}\n{ts(cu["start"])} --> {ts(cu["end"])}\n' + '\n'.join(cu['lines']) + '\n\n')
    with open(os.path.join(ROOT, 'out', f'{NAME}.vtt'), 'w', encoding='utf-8') as f:
        f.write('WEBVTT\n\n')
        for i, cu in enumerate(cues, 1):
            f.write(f'{i}\n{ts(cu["start"], ".")} --> {ts(cu["end"], ".")}\n' + '\n'.join(cu['lines']) + '\n\n')

    # ASS for burned-in captions: Inter, bottom centre, above the clause chip area
    def ass_ts(t):
        cs = int(round(t * 100))
        h, cs = divmod(cs, 360000)
        m, cs = divmod(cs, 6000)
        s, cs = divmod(cs, 100)
        return f'{h}:{m:02d}:{s:02d}.{cs:02d}'
    ass = ('[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n'
           '[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, '
           'StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
           'Style: Default,Inter,40,&H00FFFFFF,&H00FFFFFF,&H00140A04,&HA0000000,1,0,0,0,100,100,0,0,3,10,0,2,200,200,96,1\n\n'
           '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n')
    for cu in cues:
        ass += f'Dialogue: 0,{ass_ts(cu["start"])},{ass_ts(cu["end"])},Default,,0,0,0,,' + '\\N'.join(cu['lines']).replace('{', '(').replace('}', ')') + '\n'
    open(os.path.join(ROOT, 'build', 'captions.ass'), 'w', encoding='utf-8').write(ass)

    # chapters (ffmetadata)
    meta = (';FFMETADATA1\ntitle=The template interface: when has it failed? (NORSOK U-001:2026 · EN 1993-1-5 Annex C)\n'
            'comment=Tutorial. The worked example uses illustrative teaching inputs, not project data.\n')
    for c in TL['chapters']:
        t1 = min(c['end'], DUR)
        title = 'Cold open' if c['no'] == 0 else f'{c["no"]:02d} {c["title"]}'
        meta += f'\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(c["start"] * 1000)}\nEND={int(t1 * 1000)}\ntitle={title}\n'
    open(os.path.join(ROOT, 'build', 'chapters.ffmeta'), 'w', encoding='utf-8').write(meta)

    # transcript
    def mmss(t):
        return f'{int(t // 60):02d}:{int(t % 60):02d}'
    tr = ['# The template interface: when has it failed? — transcript', '',
          f'NORSOK U-001:2026, Annex B. Running time {mmss(DUR)}. Timestamps are mm:ss.', '']
    cur = None
    for c, b, s, shown in sents:
        if c['no'] != cur:
            cur = c['no']
            tr += ['', f'## {mmss(c["start"])}  ' + ('Cold open' if cur == 0 else f'{cur:02d} {c["title"]}'), '']
        if s is b['sentences'][0]:
            tr.append(f'**[{mmss(b["start"])}]** ' + ' '.join(x[3] for x in sents if x[1] is b) + '  ')
    open(os.path.join(ROOT, 'out', f'{NAME}_transcript.md'), 'w', encoding='utf-8').write('\n'.join(tr) + '\n')
    print(f'{len(cues)} cues, {len(TL["chapters"])} chapters')


if __name__ == '__main__':
    main()
