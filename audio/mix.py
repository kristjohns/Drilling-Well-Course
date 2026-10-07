#!/usr/bin/env python3
"""Music bed + sound design + narration -> audio/mix.wav (48 kHz stereo).

Everything here is synthesised (no samples, no licensing):
  * an ambient pad: slow chord changes, detuned sine partials, gentle stereo width, ducked under the voice
  * sparse soft plucks on chord tones between sentences
  * a whoosh + low swell on every chapter title card, a quiet tick when a term card appears
Levels are relative; the assembly step normalises the final mix to -16 LUFS.

    python audio/mix.py            # MUSIC=0 disables the music bed, SFX=0 disables sound effects
"""
from __future__ import annotations
import json
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SR = 48000
MUSIC = os.environ.get("MUSIC", "1") != "0"
SFX = os.environ.get("SFX", "1") != "0"
MUSIC_DB = -25.0          # pad level relative to the voice (before ducking)
DUCK_DB = -7.0            # extra attenuation while the voice is speaking

# progression (MIDI notes), each chord ~9.6 s: D maj9 - B min7 - G maj7(#11) - A sus2 ; wonder without drama
CHORDS = [[50, 57, 62, 64, 66, 69], [47, 54, 62, 66, 69, 71], [43, 55, 62, 66, 69, 73], [45, 57, 62, 64, 69, 71]]
CHORD_LEN = 9.6


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def read_wav_mono(path):
    with wave.open(path, "rb") as w:
        sr, n, ch, sw = w.getframerate(), w.getnframes(), w.getnchannels(), w.getsampwidth()
        x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    if sr != SR:   # linear resample (narration is 24 kHz -> exact 2x)
        t = np.arange(int(len(x) * SR / sr)) * sr / SR
        x = np.interp(t, np.arange(len(x)), x).astype(np.float32)
    return x


def write_wav_stereo(path, lr):
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(lr, -1, 1) * 32767).astype(np.int16).reshape(-1).tobytes())


def smooth(x, sec):
    """One-pole smoothing (both directions) of an envelope."""
    a = np.exp(-1.0 / (sec * SR / 64))
    y = x[::64].copy()
    for rng in (range(1, len(y)), range(len(y) - 2, -1, -1)):
        prev = y[rng[0] - (1 if rng.step > 0 else -1)]
        for i in rng:
            prev = a * prev + (1 - a) * y[i]
            y[i] = prev
    return np.interp(np.arange(len(x)), np.arange(len(y)) * 64, y).astype(np.float32)


def pad(n, t0_abs, rng):
    """Ambient pad for n samples starting at absolute time t0_abs (chord grid is absolute, so chapters join smoothly)."""
    t = (np.arange(n) / SR + t0_abs).astype(np.float64)
    out = np.zeros((n, 2), dtype=np.float32)
    k0 = int(t[0] // CHORD_LEN) - 1
    k1 = int(t[-1] // CHORD_LEN) + 1
    for k in range(k0, k1 + 1):
        c0 = k * CHORD_LEN
        # raised-cosine window spanning the chord plus 3 s crossfades
        a, b = c0 - 3.0, c0 + CHORD_LEN + 3.0
        i0, i1 = max(int((a - t0_abs) * SR), 0), min(int((b - t0_abs) * SR), n)
        if i1 <= i0:
            continue
        tt = t[i0:i1]
        w = np.clip((tt - a) / 3.0, 0, 1)
        w = np.minimum(w, np.clip((b - tt) / 3.0, 0, 1))
        w = (0.5 - 0.5 * np.cos(np.pi * w)).astype(np.float32)
        chord = CHORDS[k % len(CHORDS)]
        for j, m in enumerate(chord):
            f = midi_hz(m)
            amp = 0.16 / (1 + 0.35 * j)
            for det, pan in ((-0.0016, 0.25), (0.0016, 0.75)):
                ph = rng.random() * 2 * np.pi
                s = np.sin(2 * np.pi * f * (1 + det) * tt + ph) + 0.18 * np.sin(4 * np.pi * f * (1 + det) * tt + ph)
                trem = 1.0 + 0.12 * np.sin(2 * np.pi * (0.07 + 0.013 * j) * tt + ph)
                v = (amp * s * trem * w).astype(np.float32)
                out[i0:i1, 0] += v * (1 - pan)
                out[i0:i1, 1] += v * pan
    return out


def plucks(n, t0_abs, voice_env, rng):
    """Soft sine plucks on chord tones, only where the voice is quiet."""
    out = np.zeros((n, 2), dtype=np.float32)
    t = 0.6
    L = int(1.6 * SR)
    env = np.exp(-np.arange(L) / (0.45 * SR)).astype(np.float32)
    env[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    while t < n / SR - 2:
        i = int(t * SR)
        if voice_env[i] < 0.02:
            chord = CHORDS[int((t + t0_abs) // CHORD_LEN) % len(CHORDS)]
            m = chord[rng.integers(2, len(chord))] + 12
            f = midi_hz(m)
            tt = np.arange(L) / SR
            s = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) * np.exp(-tt / 0.15)) * env * 0.05
            pan = rng.uniform(0.25, 0.75)
            j = min(i + L, n)
            out[i:j, 0] += s[: j - i] * (1 - pan)
            out[i:j, 1] += s[: j - i] * pan
            # echo
            d = int(0.38 * SR)
            if j + d < n:
                out[i + d:j + d, 0] += s[: j - i] * pan * 0.35
                out[i + d:j + d, 1] += s[: j - i] * (1 - pan) * 0.35
        t += rng.uniform(1.6, 3.4)
    return out


def whoosh(rng, dur=1.4):
    n = int(dur * SR)
    noise = rng.standard_normal(n).astype(np.float32)
    # moving band-pass via two one-pole filters whose cutoff sweeps up then down
    tt = np.arange(n) / n
    fc = 300 + 2600 * np.sin(np.pi * tt) ** 1.5
    lp = np.zeros(n, dtype=np.float32)
    hp = np.zeros(n, dtype=np.float32)
    yl, yh_prev, x_prev = 0.0, 0.0, 0.0
    for i in range(n):
        al = 1 - np.exp(-2 * np.pi * fc[i] / SR)
        yl += al * (noise[i] - yl)
        lp[i] = yl
    # gentle high-pass: subtract a slow low-pass
    slow = np.zeros(n, dtype=np.float32)
    y = 0.0
    a = 1 - np.exp(-2 * np.pi * 180 / SR)
    for i in range(n):
        y += a * (lp[i] - y)
        slow[i] = y
    s = (lp - slow) * (np.sin(np.pi * tt) ** 2) * 0.22
    boom = (np.sin(2 * np.pi * 52 * np.arange(n) / SR) * np.exp(-np.arange(n) / (0.35 * SR)) * 0.25).astype(np.float32)
    boom = np.roll(boom, int(0.45 * n))
    boom[: int(0.45 * n)] = 0
    st = np.stack([s * 0.9 + boom, np.roll(s, 90) * 0.9 + boom], axis=1)
    return st.astype(np.float32)


def tick():
    n = int(0.09 * SR)
    tt = np.arange(n) / SR
    s = (np.sin(2 * np.pi * 1760 * tt) + 0.5 * np.sin(2 * np.pi * 2640 * tt)) * np.exp(-tt / 0.018) * 0.05
    return np.stack([s, s], axis=1).astype(np.float32)


def main():
    tl = json.load(open(os.path.join(ROOT, "script", "timeline.json")))
    voice = read_wav_mono(os.path.join(HERE, "narration.wav"))
    total = int(round(tl["total"] * SR))
    voice = np.pad(voice, (0, max(total - len(voice), 0)))[:total]
    rng = np.random.default_rng(7)
    venv = smooth(np.abs(voice), 0.25)
    speaking = np.clip(venv / 0.03, 0, 1)
    duck = 10 ** ((DUCK_DB * speaking) / 20)
    bed = np.zeros((total, 2), dtype=np.float32)
    if MUSIC:
        g = 10 ** (MUSIC_DB / 20)
        for ch in tl["chapters"]:
            i0, i1 = int(round(ch["start"] * SR)), int(round((ch["start"] + ch["dur"]) * SR))
            seg = pad(i1 - i0, ch["start"], rng) + plucks(i1 - i0, ch["start"], venv[i0:i1], rng)
            # chapter envelope: swell under the title card, settle, fade out over the last 0.8 s
            tt = np.arange(i1 - i0) / SR
            env = np.ones(i1 - i0, dtype=np.float32)
            intro = ch.get("intro", 0.0)
            if intro > 0:
                env *= np.where(tt < intro + 1.5, 1.0 + 0.8 * np.clip(1 - (tt - intro) / 1.5, 0, 1), 1.0)
            fin = np.clip((ch["dur"] - tt) / 0.8, 0, 1)
            fade_in = np.clip(tt / 1.2, 0, 1)
            env *= fin * fade_in
            bed[i0:i1] += seg * (env * g)[:, None]
        bed *= duck[:, None]
        if tl["chapters"]:
            last = tl["chapters"][-1]
    fx = np.zeros((total, 2), dtype=np.float32)
    if SFX:
        w = whoosh(rng)
        tk = tick()
        for ch in tl["chapters"]:
            if ch.get("intro", 0.0) > 0:
                i = max(int(round(ch["start"] * SR)) - int(0.15 * SR), 0)
                j = min(i + len(w), total)
                fx[i:j] += w[: j - i] * 0.8
            for b in ch["beats"]:
                if b.get("terms"):
                    i = int(round((b["start"] + 0.5) * SR))
                    j = min(i + len(tk), total)
                    fx[i:j] += tk[: j - i]
    mix = np.stack([voice, voice], axis=1) + bed + fx
    peak = np.abs(mix).max()
    if peak > 0.98:
        mix *= 0.98 / peak
    write_wav_stereo(os.path.join(HERE, "mix.wav"), mix)
    print(f"mix: {total / SR:.1f}s, music={'on' if MUSIC else 'off'}, sfx={'on' if SFX else 'off'}, peak {peak:.2f} -> audio/mix.wav")
    return 0


if __name__ == "__main__":
    sys.exit(main())
