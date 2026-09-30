"""Procedural soundtrack: ambient music bed, sound effects and the final mix.

Everything is synthesised with numpy, so the soundtrack is royalty-free and
reproducible. Output: build/soundtrack.wav (48 kHz stereo).
"""
import json
import math
import os

import numpy as np
import soundfile as sf

import config as C

SR = 48000
RNG = np.random.default_rng(7)


# ------------------------------------------------------------------ helpers

def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    """Fast low-pass using FFT-domain filtering (zero phase)."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    H = 1 / (1 + (f / fc) ** (2 * order))
    return np.fft.irfft(X * H, n)


def hp(x, fc, order=2):
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    H = 1 - 1 / (1 + (f / max(fc, 1)) ** (2 * order))
    return np.fft.irfft(X * H, n)


def env_adsr(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na) ** 1.5
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** 1.5
    return e


def saw(f, n, phase=0.0):
    t = np.arange(n) / SR
    return 2 * ((f * t + phase) % 1.0) - 1


# ------------------------------------------------------------------ music

CHORDS = [  # (bass, [pad notes]) — D major-ish, calm and hopeful
    (38, [62, 66, 69, 73]),     # Dmaj7
    (35, [59, 62, 66, 69]),     # Bm7
    (31, [59, 62, 67, 71]),     # Gmaj7
    (33, [57, 61, 64, 69]),     # A6/9
]


def music(duration, bar=4.8):
    n = int(duration * SR)
    out = np.zeros((n, 2))
    nb = int(bar * SR)
    k = 0
    pos = 0
    while pos < n:
        bass, notes = CHORDS[k % 4]
        seg = min(nb + int(1.5 * SR), n - pos)
        pad = np.zeros(seg)
        for m in notes:
            f = midi_hz(m)
            for det in (-0.12, 0.0, 0.13):
                pad += saw(f * 2 ** (det / 12), seg, RNG.random()) * 0.05
        pad = lp(pad, 900)
        pad *= env_adsr(seg, 1.4, 1.6)
        sub = np.sin(2 * np.pi * midi_hz(bass + 12) * np.arange(seg) / SR) * 0.10
        sub *= env_adsr(seg, 0.8, 1.4)
        # arpeggio plucks
        arp = np.zeros(seg)
        step = int(bar / 8 * SR)
        pattern = [0, 2, 1, 3, 2, 1, 3, 2]
        for j in range(8):
            if RNG.random() < 0.25:
                continue
            m = notes[pattern[j]] + 12
            st = j * step
            ln = min(int(1.2 * SR), seg - st)
            if ln <= 0:
                continue
            t = np.arange(ln) / SR
            f = midi_hz(m)
            tone = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 4.0)
            arp[st:st + ln] += tone * 0.05
        mono = pad + sub + arp
        # simple stereo: slight delay on the right channel for the plucks
        d = int(0.013 * SR)
        right = pad + sub + np.concatenate([np.zeros(d), arp[:-d]])
        out[pos:pos + seg, 0] += mono
        out[pos:pos + seg, 1] += right
        pos += nb
        k += 1
    # gentle reverb-ish smear (feedback delay network lite)
    for dl, g in ((0.071, 0.25), (0.113, 0.2), (0.197, 0.15)):
        d = int(dl * SR)
        out[d:] += out[:-d] * g
    out /= np.max(np.abs(out)) + 1e-9
    return out * 0.5


# ------------------------------------------------------------------ sound effects

def sfx_whoosh(dur=0.9, rise=True):
    n = int(dur * SR)
    x = RNG.standard_normal(n)
    t = np.linspace(0, 1, n)
    # sweep a band-pass by mixing lp/hp over time (cheap approximation)
    lo = lp(x, 500)
    hi = lp(x, 3500) - lo
    y = lo * (1 - t) + hi * t if rise else lo * t + hi * (1 - t)
    e = np.sin(np.pi * t) ** 2
    return (y * e * 0.25)


def sfx_boom(dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (55 * np.exp(-t * 2)) * t) * np.exp(-t * 3)
    noise = lp(RNG.standard_normal(n), 900) * np.exp(-t * 6) * 0.8
    crack = hp(RNG.standard_normal(n), 2000) * np.exp(-t * 25) * 0.4
    return (body + noise + crack) * 0.55


def sfx_clank(dur=0.8):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for f, d in ((310, 9), (523, 11), (847, 14), (1290, 18)):
        y += np.sin(2 * np.pi * f * t) * np.exp(-t * d)
    y += hp(RNG.standard_normal(n), 1500) * np.exp(-t * 40) * 0.6
    return y * 0.16


def sfx_thud(dur=0.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 70 * t) * np.exp(-t * 9) * 0.5 + \
        lp(RNG.standard_normal(n), 300) * np.exp(-t * 12) * 0.3


def sfx_rumble(dur=3.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = lp(RNG.standard_normal(n), 160) * 1.5
    return y * env_adsr(n, 0.4, 1.2) * 0.35


def sfx_pop(dur=0.12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 900 * t * (1 - t * 3)) * np.exp(-t * 45) * 0.06


def sfx_chime(dur=1.4):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for m, a in ((81, 1.0), (88, 0.6), (93, 0.4)):
        f = midi_hz(m)
        y += np.sin(2 * np.pi * f * t) * np.exp(-t * 3) * a
    return y * 0.08


SFX = {'whoosh': sfx_whoosh, 'boom': sfx_boom, 'clank': sfx_clank, 'thud': sfx_thud,
       'rumble': sfx_rumble, 'pop': sfx_pop, 'chime': sfx_chime}


def sfx_cues():
    """(name, global_time_s, gain) cues derived from scene timings."""
    import scene_base
    tl = json.load(open(C.TIMELINE))
    cues = []
    starts = {s['id']: s['start'] for s in tl['scenes']}
    for s in tl['scenes'][1:]:
        cues.append(('whoosh', s['start'] - 0.45, 0.7))
    def add(sid, key, name, gain=1.0, off=0.0, attr='T'):
        sc = scene_base.load(sid)
        t = getattr(sc, attr)[key] if attr else key
        cues.append((name, starts[sid] + t + off, gain))
    add('s01_intro', 'title', 'chime', 1.0)
    add('s03_pressure', 'blowout', 'rumble', 0.9, -0.2)
    add('s03_pressure', 'crack', 'clank', 0.5)
    add('s04_casing', 'fracture', 'pop', 1.0)
    add('s08_bop', 'latched', 'clank', 0.8, -1.2)
    add('s08_bop', 'cut', 'clank', 1.0, -0.05)
    add('s08_bop', 'cut', 'thud', 0.6)
    add('s10_cementing', 'bumped', 'thud', 0.8, -0.8)
    add('s12_completion', 'charge', 'boom', 1.0, 0.4)
    add('s12_completion', 'snaps', 'clank', 0.7)
    add('s12_completion', 'tree', 'thud', 0.6, 0.2)
    add('s14_pa', 'lid', 'chime', 1.0, -0.2)
    add('s15_outro', 'thanks', 'chime', 1.0, -0.3)
    return cues


# ------------------------------------------------------------------ mix

def movavg(x, w):
    c = np.cumsum(np.concatenate([[0.0], x]))
    y = (c[w:] - c[:-w]) / w
    pad = len(x) - len(y)
    return np.concatenate([np.full(pad // 2, y[0]), y, np.full(pad - pad // 2, y[-1])])


def build(out_path=None):
    tl = json.load(open(C.TIMELINE))
    dur = tl['duration'] + 1.0
    n = int(dur * SR)
    narr, sr = sf.read(os.path.join(C.BUILD, 'narration.wav'), dtype='float32')
    # resample 24k -> 48k (linear interpolation is fine for speech at 2x)
    x_old = np.arange(len(narr)) / sr
    x_new = np.arange(int(len(narr) * SR / sr)) / SR
    narr48 = np.interp(x_new, x_old, narr)
    voice = np.zeros(n)
    voice[:min(n, len(narr48))] = narr48[:n]
    # speech envelope for ducking
    envv = movavg(np.abs(voice), int(0.25 * SR))
    duck = np.clip(envv / 0.02, 0, 1)
    duck = movavg(duck, int(0.6 * SR))
    mus = music(dur)
    gain = 0.30 - 0.19 * duck            # ~ -10 dB in gaps, ~ -20 dB under speech
    # fade music in/out
    fi = int(2.0 * SR)
    fo = int(4.0 * SR)
    gain[:fi] *= np.linspace(0, 1, fi)
    gain[-fo:] *= np.linspace(1, 0, fo)
    mix = mus * gain[:, None]
    mix[:, 0] += voice * 0.92
    mix[:, 1] += voice * 0.92
    for name, t0, g in sfx_cues():
        s = SFX[name]()
        i = int(max(0, t0) * SR)
        j = min(n, i + len(s))
        mix[i:j, 0] += s[:j - i] * g
        mix[i:j, 1] += s[:j - i] * g * 0.95
    peak = np.max(np.abs(mix))
    if peak > 0.98:
        mix *= 0.98 / peak
    out_path = out_path or os.path.join(C.BUILD, 'soundtrack.wav')
    sf.write(out_path, mix.astype(np.float32), SR)
    print('soundtrack', out_path, round(dur, 1), 's, peak', round(float(peak), 3))
    return out_path


if __name__ == '__main__':
    build()
