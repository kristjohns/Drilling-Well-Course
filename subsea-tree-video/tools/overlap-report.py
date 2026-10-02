#!/usr/bin/env python3
"""Summarise build/qa/overlaps.json (from tools/overlap-scan.mjs): persistent findings only.

  python3 tools/overlap-report.py [--min-dur 0.75]

Drops giant dimmer rectangles, wrapped-text union boxes and short cross-fade hits; what remains
should be looked at in a rendered frame (tools/frame.mjs) before deciding whether it is a real collision.
"""
import collections, json, re, sys

MIN_DUR = float(sys.argv[sys.argv.index('--min-dur') + 1]) if '--min-dur' in sys.argv else 0.75
STEP = 0.25
hits = json.load(open('build/qa/overlaps.json'))
groups = collections.OrderedDict()
for h in hits:
    if h['kind'] == 'occluded':
        by = h['by'][0] if h['by'] else '?'
        m = re.search(r'@(-?\d+),(-?\d+) (\d+)x(\d+)', by)
        if m and int(m.group(3)) >= 2500:
            continue
        if h['pts'] < 3:
            continue
        key = ('OCC', h['t'], re.sub(r'@.*?( "|$)', r'\1', by)[:60])
    else:
        if h['frac'] >= 0.99:
            continue
        key = ('TXT', h['t'], h['t2'])
    g = groups.setdefault(key, {'times': [], 'max': 0, 'box': h['box']})
    g['times'].append(h['time'])
    g['max'] = max(g['max'], h.get('pts', 0) or h.get('frac', 0))
rows = []
for k, g in groups.items():
    ts = sorted(set(g['times']))
    ranges = []
    for t in ts:
        if ranges and t - ranges[-1][1] <= STEP * 1.51:
            ranges[-1][1] = t
        else:
            ranges.append([t, t])
    ranges = [r for r in ranges if r[1] - r[0] >= MIN_DUR - 0.01]
    if ranges:
        rows.append((ranges[0][0], k, ranges, g))
rows.sort(key=lambda r: r[0])
print(len(rows), f'findings lasting >= {MIN_DUR} s')
for _, k, ranges, g in rows:
    rs = ', '.join(f'{a:.2f}-{b:.2f}' for a, b in ranges)
    what = ('by ' + k[2]) if k[0] == 'OCC' else ('<> ' + k[2][:40])
    print(f'{rs:30s} {k[0]} "{k[1][:42]}"  {what}  max {g["max"]} box {g["box"]}')
