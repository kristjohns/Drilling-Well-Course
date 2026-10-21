#!/usr/bin/env python3
"""Music bed, ambience, sound effects and the final mix.

  python3 tools/audio.py      -> build/audio/mix.wav (48 kHz stereo, 16 bit, about -16 LUFS integrated, -1.5 dBTP)

Inputs : build/audio/narration.wav (24 kHz mono, from tools/tts.py) and src/data/timeline.json (chapters, beats, cues).
Output : narration + an ambient music bed that ducks under the voice + underwater / surface ambience in the 3D shots +
         a few sound effects keyed to the picture (title-card whooshes, stamps, step ticks, counters, splashes).
Everything is synthesised here with numpy/scipy: no samples, so no licensing questions.
"""
import json
import math
import os
import subprocess

import numpy as np
import soundfile as sf
from scipy import signal
from scipy.ndimage import maximum_filter1d

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
AUDIO = os.path.join(ROOT, 'build', 'audio')
TL = json.load(open(os.path.join(ROOT, 'src', 'data', 'timeline.json')))
DUR = TL['duration']
N = int(round(DUR * SR)) + SR
rng = np.random.default_rng(20261021)

BEATS = {b['id']: b for c in TL['chapters'] for b in c['beats']}
CH = {c['no']: c for c in TL['chapters']}


def cue(bid, name):
    return BEATS[bid]['cues'][name]


def word(bid, w, nth=0):
    k = 0
    for s in BEATS[bid]['sentences']:
        for x in s['words']:
            if ''.join(ch for ch in x['w'].lower() if ch.isalnum() or ch in "'-") == w:
                if k == nth:
                    return x['s']
                k += 1
    raise KeyError(f'{bid}:{w}')


# ----------------------------------------------------------------------------------------------- dsp helpers
def tt(n):
    return np.arange(n, dtype=np.float64) / SR


def env_exp(n, tau):
    return np.exp(-tt(n) / tau)


def sos(kind, f, order=2):
    return signal.butter(order, f, btype=kind, fs=SR, output='sos')


def filt(x, kind, f, order=2):
    return signal.sosfilt(sos(kind, f, order), x, axis=0)


def fade(x, a=0.01, b=0.05):
    n = len(x)
    ia, ib = min(int(a * SR), n // 2), min(int(b * SR), n // 2)
    if ia:
        x[:ia] *= np.linspace(0, 1, ia)[:, None] if x.ndim == 2 else np.linspace(0, 1, ia)
    if ib:
        x[-ib:] *= np.linspace(1, 0, ib)[:, None] if x.ndim == 2 else np.linspace(1, 0, ib)
    return x


def pan(x, p):
    """mono -> stereo, p in [-1, 1], constant power"""
    a = (p + 1) * math.pi / 4
    return np.stack([x * math.cos(a), x * math.sin(a)], axis=1)


def add(bus, x, t0, gain=1.0):
    i = int(round(t0 * SR))
    if i >= len(bus):
        return
    j0 = max(0, -i)
    i = max(0, i)
    n = min(len(x) - j0, len(bus) - i)
    if n > 0:
        bus[i:i + n] += (x[j0:j0 + n] * gain).astype(np.float32)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def ir(seconds=3.2, rt60=2.8, lp=5200):
    """stereo reverb impulse response: decorrelated exponentially decaying noise, darker as it decays"""
    n = int(seconds * SR)
    e = np.exp(-6.91 * tt(n) / rt60)
    out = []
    for _ in range(2):
        x = rng.standard_normal(n) * e
        x = filt(x, 'low', lp)
        x[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
        out.append(x)
    h = np.stack(out, axis=1)
    return h / np.sqrt(np.sum(h ** 2) / 2)


def circ_reverb(x, h, wet=0.35):
    """circular convolution: the reverb tail wraps around, so a loop stays seamless when tiled"""
    n = len(x)
    y = np.empty_like(x)
    for ch in range(2):
        hh = np.zeros(n)
        m = min(n, len(h))
        hh[:m] = h[:m, ch]
        y[:, ch] = np.fft.irfft(np.fft.rfft(x[:, ch]) * np.fft.rfft(hh), n)
    return x * (1 - wet) + y * wet


# ----------------------------------------------------------------------------------------------- music
PROG_A = [[50, 57, 60, 64, 65], [46, 53, 57, 62, 65], [41, 53, 57, 60, 67], [48, 55, 62, 64, 67]]   # Dm9 Bbmaj7 Fadd9 Csus2
PROG_B = [[43, 55, 58, 62, 69], [39, 51, 55, 58, 62], [46, 53, 58, 60, 65], [41, 53, 57, 60, 64]]   # Gm9 Ebmaj7 Bbadd9 Fmaj7
CHORD_S = 8.0


def pad_voice(f, n, seed):
    """one sustained pad note: three detuned partial stacks with slow vibrato and a soft attack/release"""
    r = np.random.default_rng(seed)
    t = tt(n)
    y = np.zeros(n)
    for det in (-0.0021, 0.0, 0.0024):
        ph = r.uniform(0, 2 * math.pi)
        vib = 1 + 0.0012 * np.sin(2 * math.pi * r.uniform(0.08, 0.18) * t + r.uniform(0, 6))
        w = 2 * math.pi * f * (1 + det) * vib
        phase = np.cumsum(w) / SR + ph
        y += np.sin(phase) + 0.18 * np.sin(2 * phase) + 0.06 * np.sin(3 * phase)
    return y / 3


def music_loop(prog, cycles=4, seed=1):
    """`cycles` passes through a four-chord progression (8 s per chord), pad + sub + sparse bell plucks, with a
    circular reverb so the loop tiles without a seam. Returns stereo float32."""
    L = int(len(prog) * cycles * CHORD_S * SR)
    out = np.zeros((L, 2))
    seg = int(CHORD_S * SR)
    att, rel = int(3.0 * SR), int(4.5 * SR)
    r = np.random.default_rng(seed)
    for k in range(len(prog) * cycles):
        notes = prog[k % len(prog)]
        n = seg + rel
        envl = np.ones(n)
        envl[:att] = np.sin(np.linspace(0, math.pi / 2, att)) ** 2
        envl[seg:] = np.cos(np.linspace(0, math.pi / 2, rel)) ** 2
        for j, m in enumerate(notes):
            f = midi(m)
            v = pad_voice(f, n, seed * 1000 + k * 10 + j) * envl
            g = 0.55 if j == 0 else 0.32
            st = pan(v, -0.45 + 0.9 * j / (len(notes) - 1))
            i0 = k * seg
            a = min(n, L - i0)
            out[i0:i0 + a] += st[:a] * g
            if a < n:
                out[: n - a] += st[a:] * g
        # sub: chord root an octave down
        sub = np.sin(2 * math.pi * midi(notes[0] - 12) * tt(n)) * envl * 0.35
        st = pan(sub, 0)
        i0 = k * seg
        a = min(n, L - i0)
        out[i0:i0 + a] += st[:a]
        if a < n:
            out[: n - a] += st[a:]
        # bells: 1-3 soft plucks per chord from the upper chord tones, an octave up
        for _ in range(r.integers(1, 4)):
            m = int(r.choice(notes[2:])) + 12
            nn = int(2.6 * SR)
            b = (np.sin(2 * math.pi * midi(m) * tt(nn)) + 0.25 * np.sin(2 * math.pi * midi(m) * 2.76 * tt(nn)) * env_exp(nn, 0.4)) * env_exp(nn, 0.9)
            b[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
            st = pan(b * 0.16, r.uniform(-0.8, 0.8))
            i0 = k * seg + int(r.uniform(0.2, 7.0) * SR)
            i0 %= L
            a = min(nn, L - i0)
            out[i0:i0 + a] += st[:a]
            if a < nn:
                out[: nn - a] += st[a:]
    # gentle tone shaping: warm low-pass, remove rumble
    out = filt(out, 'low', 2600)
    out = filt(out, 'high', 38)
    out = circ_reverb(out, ir(), wet=0.42)
    return (out / np.sqrt(np.mean(out ** 2))).astype(np.float32)          # unit RMS: levels below are RMS levels


# ----------------------------------------------------------------------------------------------- ambience
def underwater(dur, seed):
    n = int(dur * SR)
    r = np.random.default_rng(seed)
    out = np.zeros((n, 2))
    for ch in range(2):
        b = np.cumsum(r.standard_normal(n))
        b = filt(b, 'high', 18)
        b = filt(b, 'low', 420)
        mod = 0.7 + 0.3 * np.sin(2 * math.pi * 0.07 * tt(n) + ch) + 0.15 * np.sin(2 * math.pi * 0.19 * tt(n) + 2 * ch)
        out[:, ch] = b / (np.std(b) + 1e-9) * mod
    out *= 0.5
    # bubbles: short rising chirps
    for _ in range(int(dur * 0.9)):
        t0 = r.uniform(0, max(dur - 0.2, 0.1))
        nn = int(r.uniform(0.03, 0.08) * SR)
        f0 = r.uniform(380, 1100)
        f = f0 * (1 + 0.8 * tt(nn) / (nn / SR))
        x = np.sin(2 * math.pi * np.cumsum(f) / SR) * env_exp(nn, nn / SR / 3) * r.uniform(0.15, 0.4)
        i = int(t0 * SR)
        out[i:i + nn] += pan(x, r.uniform(-0.8, 0.8))[: n - i]
    return out


def surface(dur, seed):
    n = int(dur * SR)
    r = np.random.default_rng(seed)
    out = np.zeros((n, 2))
    t = tt(n)
    for ch in range(2):
        w = filt(r.standard_normal(n), 'band', [160, 2400])
        swell = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * math.pi * t / 6.3 + ch * 0.9)) ** 2.2 + 0.2 * np.sin(2 * math.pi * t / 2.7 + ch)
        wind = filt(r.standard_normal(n), 'band', [900, 5200]) * (0.25 + 0.1 * np.sin(2 * math.pi * 0.11 * t + ch))
        out[:, ch] = w * np.clip(swell, 0.05, None) + wind
    return out / (np.std(out) + 1e-9) * 0.5


# ----------------------------------------------------------------------------------------------- sound effects
def s_whoosh(dur=1.3):
    n = int(dur * SR)
    t = tt(n)
    x = rng.standard_normal(n)
    # band-pass whose centre sweeps up then down; built from short overlapping blocks
    out = np.zeros(n)
    hop = int(0.01 * SR)
    win = np.hanning(2 * hop)
    for i in range(0, n - 2 * hop, hop):
        u = i / n
        fc = 300 + 2600 * math.sin(math.pi * min(1, u * 1.15)) ** 1.6
        blk = signal.sosfilt(sos('band', [fc * 0.6, min(fc * 1.6, 20000)]), x[i:i + 2 * hop])
        out[i:i + 2 * hop] += blk * win
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.8
    y = out * e
    st = np.stack([y * (1 - 0.5 * t / dur), y * (0.5 + 0.5 * t / dur)], axis=1)     # left -> right
    return fade(st / np.max(np.abs(st)), 0.01, 0.1)


def s_tick():
    n = int(0.08 * SR)
    x = np.sin(2 * math.pi * 1900 * tt(n)) * env_exp(n, 0.008) * 0.7 + filt(rng.standard_normal(n), 'high', 3000) * env_exp(n, 0.002) * 0.3
    return pan(fade(x, 0.001, 0.02), 0)


def s_chime():
    def bell(f, d):
        n = int(d * SR)
        y = np.zeros(n)
        for ratio, a, tau in [(1, 1.0, 0.8), (2.76, 0.35, 0.35), (5.4, 0.12, 0.18), (0.5, 0.2, 1.0)]:
            y += a * np.sin(2 * math.pi * f * ratio * tt(n)) * env_exp(n, tau)
        return fade(y, 0.002, 0.08)
    a, b = bell(midi(74), 1.8), bell(midi(81), 2.0)
    out = np.zeros(int(2.4 * SR))
    out[: len(a)] += a * 0.7
    d = int(0.12 * SR)
    out[d:d + len(b)] += b * 0.6
    return np.stack([out, np.roll(out, int(0.006 * SR))], axis=1) * 0.5


def s_fail():
    n = int(1.6 * SR)
    y = np.zeros(n)
    for m in (45, 46, 57):
        y += np.sin(2 * math.pi * midi(m) * tt(n)) * env_exp(n, 0.5)
    y += filt(rng.standard_normal(n), 'low', 500) * env_exp(n, 0.05) * 0.6
    return pan(fade(y / 3, 0.002, 0.2), 0)


def s_impact():
    n = int(4.0 * SR)
    t = tt(n)
    f = 70 * np.exp(-t / 0.6) + 34
    y = np.sin(2 * math.pi * np.cumsum(f) / SR) * env_exp(n, 1.1)
    y += filt(rng.standard_normal(n), 'low', 1800) * env_exp(n, 0.08) * 0.5
    sh = np.zeros(n)
    for m in (74, 81, 86):
        sh += np.sin(2 * math.pi * midi(m) * t) * env_exp(n, 1.6) * (1 - np.exp(-t / 0.3))
    st = pan(y, 0) + np.stack([sh, np.roll(sh, int(0.009 * SR))], axis=1) * 0.12
    return fade(st / np.max(np.abs(st)), 0.002, 0.5)


def s_roll(dur):
    """accelerating soft ticks for a counter"""
    n = int((dur + 0.2) * SR)
    out = np.zeros((n, 2))
    tk = s_tick()
    t = 0.0
    while t < dur:
        u = t / dur
        add(out, tk * (0.35 + 0.65 * (1 - u)), t)
        t += 0.11 - 0.07 * math.sin(math.pi * u)
    return out


def s_splash(up=False):
    n = int(1.4 * SR)
    t = tt(n)
    x = filt(rng.standard_normal(n), 'band', [250, 6000]) * (np.exp(-t / 0.25) if not up else np.exp(-((t - 0.25) / 0.18) ** 2))
    b = underwater(1.4, 77)[:, 0] * 0.3 * np.exp(-t / 0.5)
    y = x + b
    return pan(fade(y / np.max(np.abs(y)), 0.005, 0.2), 0)


# ----------------------------------------------------------------------------------------------- build the mix
def main():
    os.makedirs(AUDIO, exist_ok=True)
    print('voice …', flush=True)
    v, sr = sf.read(os.path.join(AUDIO, 'narration.wav'), dtype='float32')
    assert sr == 24000, sr
    v = signal.resample_poly(v, 2, 1).astype(np.float32)
    voice = np.zeros(N, dtype=np.float32)
    voice[: min(N, len(v))] = v[:N]
    del v
    voice = signal.sosfilt(sos('high', 70), voice).astype(np.float32)
    # ducking envelope: 1 while the narrator speaks, 0 otherwise (fast attack, slow release)
    a = maximum_filter1d(np.abs(voice), size=int(0.03 * SR))
    hop = 480
    e = a[::hop]
    on = (e > 0.02).astype(np.float32)
    att, rel = 0.25, 0.012
    sm = np.zeros_like(on)
    g = 0.0
    for i, x in enumerate(on):
        g = g + (x - g) * (att if x > g else rel)
        sm[i] = g
    duck = np.interp(np.arange(N) / hop, np.arange(len(sm)), sm).astype(np.float32)
    del a, e, on, sm
    vr = float(np.sqrt(np.mean(voice[duck > 0.9] ** 2)))
    print(f'voice rms {20 * math.log10(vr):.1f} dBFS', flush=True)

    master = np.zeros((N, 2), dtype=np.float32)

    # ---- music: one long loop per progression, tiled per chapter, crossfaded at chapter boundaries
    print('music …', flush=True)
    loops = {'A': music_loop(PROG_A, 4, seed=3), 'B': music_loop(PROG_B, 4, seed=5)}
    lvl_free, lvl_duck = vr * 10 ** (-17 / 20), vr * 10 ** (-27 / 20)
    xf = 3.0
    for c in TL['chapters']:
        t0, t1 = max(0.0, c['start'] - xf / 2), min(DUR + 1, c['end'] + xf / 2)
        lp = loops['A' if c['no'] % 2 == 0 else 'B']
        n = int((t1 - t0) * SR)
        off = int((c['no'] * 37.0) * SR) % len(lp)
        idx = (np.arange(n) + off) % len(lp)
        seg = lp[idx].astype(np.float32)
        tt0 = t0 + np.arange(n) / SR
        gfx = np.clip((tt0 - t0) / xf, 0, 1) * np.clip((t1 - tt0) / xf, 0, 1)
        if c['no'] == 0:
            gfx = np.clip((tt0 - 0.0) / 6.0, 0, 1) * np.clip((t1 - tt0) / xf, 0, 1)     # the film opens on the sea
        if c['no'] == 10:
            gfx = np.clip((tt0 - t0) / xf, 0, 1) * np.clip((DUR - tt0) / 2.5, 0, 1)
        # title-card swell: the bed lifts while the chapter title is on screen
        if c.get('title_card'):
            a0, a1 = c['title_card']
            gfx = gfx * (1 + 0.8 * np.clip(1 - np.abs(tt0 - (a0 + a1) / 2) / ((a1 - a0) / 2 + 1.0), 0, 1))
        i0 = int(t0 * SR)
        d = duck[i0:i0 + n]
        lv = (lvl_free + (lvl_duck - lvl_free) * d) * gfx
        master[i0:i0 + n] += seg[: len(d)] * lv[:, None]
    del loops

    # ---- ambience in the 3D shots
    print('ambience …', flush=True)
    tR = cue('0.1', 'riser')
    tU1 = word('10.2', 'field') - 0.2 + 2.6
    t_surface10 = tU1 + 13.9
    regions = [
        ('surface', 0.0, tR - 0.5, 0.75), ('under', tR - 0.7, BEATS['0.3']['end'], 1.0),
        ('under', BEATS['1.1']['start'], BEATS['1.2']['end'], 0.55), ('under', BEATS['4.1']['start'], BEATS['4.2']['end'], 0.5),
        ('under', BEATS['6.6']['start'], BEATS['6.6']['end'], 0.5),
        ('under', BEATS['10.2']['start'], t_surface10 + 0.2, 0.9), ('surface', t_surface10 - 0.2, DUR, 0.8),
    ]
    amb_free, amb_duck = vr * 10 ** (-24 / 20), vr * 10 ** (-31 / 20)
    for k, (kind, t0, t1, g) in enumerate(regions):
        x = underwater(t1 - t0, 100 + k) if kind == 'under' else surface(t1 - t0, 200 + k)
        x = fade(x, 1.2, 1.5)
        n = len(x)
        i0 = int(t0 * SR)
        d = duck[i0:i0 + n]
        lv = (amb_free + (amb_duck - amb_free) * d) * g
        if t1 >= DUR - 0.01:
            lv = lv * np.clip((DUR - (t0 + np.arange(len(d)) / SR)) / 2.5, 0, 1)
        master[i0:i0 + len(d)] += (x[: len(d)] * lv[:, None]).astype(np.float32)

    # ---- sound effects
    print('sfx …', flush=True)
    sfx = np.zeros((N, 2), dtype=np.float32)
    wh = s_whoosh()
    for c in TL['chapters']:
        if c.get('title_card'):
            add(sfx, wh, c['title_card'][0] - 0.15, 0.55)
    add(sfx, s_impact(), BEATS['0.3']['start'] + 0.25, 0.5)
    tk = s_tick()
    for k in ('s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8'):
        add(sfx, tk, cue('1.4', k), 0.35)
    for k in ('loads', 'share', 'soil', 'stress', 'mn', 'damage', 'check'):
        add(sfx, tk, cue('10.1', k) - 0.1, 0.35)
    add(sfx, tk, word('10.1', 'check') - 0.1, 0.35)
    add(sfx, s_roll(2.6), cue('0.1', 'count'), 0.3)
    add(sfx, s_roll(2.2), cue('3.6', 'total'), 0.3)
    add(sfx, s_fail(), cue('9.3', 'fail'), 0.5)
    ch = s_chime()
    add(sfx, ch, cue('9.4', 'pass'), 0.6)
    add(sfx, ch, cue('9.6', 'pass'), 0.6)
    add(sfx, s_splash(), tR - 0.55, 0.45)
    add(sfx, s_splash(up=True), t_surface10 - 0.3, 0.4)
    add(sfx, s_impact() * 0.6, cue('10.2', 'end') - 0.2, 0.4)
    master += sfx * (vr * 10 ** (-4 / 20) / max(float(np.max(np.abs(sfx))), 1e-9))
    del sfx

    master += voice[:, None]
    del voice

    # ---- master: gentle peak control, then EBU R128 normalisation with ffmpeg (two pass, linear)
    pk = float(np.max(np.abs(master)))
    master *= 0.5 / pk
    raw = os.path.join(AUDIO, 'mix_raw.wav')
    sf.write(raw, master, SR, subtype='FLOAT')
    del master
    print('loudness …', flush=True)
    target = 'I=-16:TP=-1.5:LRA=11'
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', raw, '-af', f'loudnorm={target}:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True)
    js = r.stderr[r.stderr.rindex('{'): r.stderr.rindex('}') + 1]
    m = json.loads(js)
    af = (f"loudnorm={target}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    out = os.path.join(AUDIO, 'mix.wav')
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', raw, '-af', af, '-ar', str(SR), '-c:a', 'pcm_s16le', out], check=True)
    os.remove(raw)
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', out, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    summ = r.stderr[r.stderr.rindex('Summary:'):]
    print(summ)


if __name__ == '__main__':
    main()
