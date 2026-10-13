"""Build the final audio mix (narration + synthesized ambient music + subtle SFX) and subtitles.

Outputs (build/audio):
  narration_48k.wav, music.wav, mix_raw.wav, mix.wav (loudness normalised), subtitles.srt
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy.signal import lfilter, resample_poly, fftconvolve, butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from engine.scene import CREDITS_DUR  # noqa: E402

SR = 48000
AUD = os.path.join(ROOT, "build", "audio")
rng = np.random.default_rng(1234)


def note(n):  # MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def adsr(n, a, r):
    env = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    env[:na] = np.linspace(0, 1, na) ** 2
    env[n - nr:] *= np.linspace(1, 0, nr) ** 2
    return env


def pad_voice(freq, dur, detune_cents=(-7, 0, 7)):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for i, dc in enumerate(detune_cents):
        f = freq * 2 ** (dc / 1200)
        ph = rng.uniform(0, 2 * np.pi)
        w = (np.sin(2 * np.pi * f * t + ph) + 0.32 * np.sin(4 * np.pi * f * t + ph * 1.3)
             + 0.12 * np.sin(6 * np.pi * f * t + ph * 0.7) + 0.05 * np.sin(8 * np.pi * f * t))
        pan = (i - 1) * 0.6
        out[:, 0] += w * (1 - pan) * 0.5
        out[:, 1] += w * (1 + pan) * 0.5
    return out / len(detune_cents)


def reverb_ir(seconds=3.2, decay=2.6):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.normal(0, 1, (n, 2)) * np.exp(-t * decay)[:, None]
    sos = butter(2, 5000, "low", fs=SR, output="sos")
    ir = sosfilt(sos, ir, axis=0)
    ir[0] = 0
    return ir / np.sqrt((ir ** 2).sum(axis=0))


def make_loop():
    """64 s seamless ambient loop: Dm9 - Bbmaj7 - Fadd9 - Csus2, two voicings."""
    chords = [
        [38, 50, 57, 60, 64, 69],   # D2 D3 A3 C4 E4 A4  (Dm9)
        [34, 46, 53, 57, 62, 65],   # Bb maj7-ish
        [41, 48, 55, 60, 64, 67],   # F add9
        [36, 48, 55, 62, 67, 72],   # C sus2
        [38, 50, 53, 57, 64, 69],   # Dm (alt voicing)
        [34, 46, 53, 58, 62, 69],   # Bb add9
        [41, 53, 57, 60, 67, 72],   # F
        [43, 50, 55, 62, 65, 70],   # Gm7/C colour
    ]
    seg = 8.0
    over = 3.0
    total = seg * len(chords)
    n = int(total * SR)
    out = np.zeros((n + int(over * SR) * 2, 2))
    for i, ch in enumerate(chords):
        start = int(i * seg * SR)
        dur = seg + over
        buf = np.zeros((int(dur * SR), 2))
        for k, m in enumerate(ch):
            amp = 0.5 if m < 45 else (0.32 if m < 60 else 0.22)
            buf += pad_voice(note(m), dur) * amp
        buf *= adsr(len(buf), 2.6, 3.0)[:, None]
        out[start:start + len(buf)] += buf
    # wrap the tail into the beginning for a seamless loop
    tail = out[n:]
    out = out[:n]
    out[:len(tail)] += tail
    # gentle low-pass for warmth
    sos = butter(2, 1600, "low", fs=SR, output="sos")
    out = sosfilt(sos, out, axis=0)
    # circular reverb
    ir = reverb_ir()
    wet = np.zeros_like(out)
    for ch in range(2):
        conv = fftconvolve(np.concatenate([out[:, ch], out[:, ch]]), ir[:, ch])[: 2 * n]
        wet[:, ch] = conv[n:2 * n] + conv[:n] * 0  # second pass already contains wrap-around
    mix = out * 0.55 + wet * 0.9
    return mix / np.abs(mix).max()


def bells(total):
    """Sparse soft bell tones (pentatonic) across the whole film."""
    n = int(total * SR)
    out = np.zeros((n, 2))
    scale = [62, 64, 69, 72, 74, 76, 81]
    t = 6.0
    while t < total - 6:
        m = int(rng.choice(scale))
        f = note(m)
        dur = 4.0
        k = int(dur * SR)
        tt = np.arange(k) / SR
        env = (1 - np.exp(-tt * 60)) * np.exp(-tt * 1.4)
        w = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 3)) * env
        pan = rng.uniform(-0.6, 0.6)
        i0 = int(t * SR)
        seg = out[i0:i0 + k]
        seg[:, 0] += w[: len(seg)] * (1 - pan) * 0.5
        seg[:, 1] += w[: len(seg)] * (1 + pan) * 0.5
        t += rng.uniform(5.0, 11.0)
    ir = reverb_ir(2.5, 2.0)
    wet = np.stack([fftconvolve(out[:, c], ir[:, c])[:n] for c in range(2)], axis=1)
    return out * 0.4 + wet * 0.8


def whoosh(dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    out = np.zeros(n)
    # sweep a band-pass by blocks
    blocks = 40
    for b in range(blocks):
        a0, a1 = b * n // blocks, (b + 1) * n // blocks
        fc = 300 + 3500 * (b / blocks) ** 1.5
        sos = butter(2, [fc * 0.7, fc * 1.3], "band", fs=SR, output="sos")
        out[a0:a1] = sosfilt(sos, noise[a0:a1])
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    out *= env
    return np.stack([out, out], axis=1) / (np.abs(out).max() + 1e-9)


def swell(dur=3.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 55.0
    w = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2 * t)
    env = (1 - np.exp(-t * 3)) * np.exp(-t * 1.1)
    w *= env
    return np.stack([w, w], axis=1) / np.abs(w).max()


def place(dst, src, t, gain):
    i0 = int(t * SR)
    if i0 >= len(dst):
        return
    k = min(len(src), len(dst) - i0)
    dst[i0:i0 + k] += src[:k] * gain


def env_follow(x, attack=0.05, release=0.6):
    """Envelope follower on |x| (mono), returns 0..1-ish envelope."""
    a = np.abs(x)
    # smooth with one-pole filters (attack/release approximated by two passes)
    k_r = np.exp(-1.0 / (release * SR))
    env = lfilter([1 - k_r], [1, -k_r], a)
    k_a = np.exp(-1.0 / (attack * SR))
    env = lfilter([1 - k_a], [1, -k_a], env[::-1])[::-1]
    return env / (env.max() + 1e-9)


def fmt_ts(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def split_caption(text, maxlen=90):
    """Split a sentence into caption chunks at punctuation, then at word boundaries."""
    import re
    pieces = [p.strip() for p in re.split(r"(?<=[,;:])\s+", text) if p.strip()]
    chunks, cur = [], ""
    for p in pieces:
        cand = (cur + " " + p).strip()
        if len(cand) <= maxlen:
            cur = cand
        else:
            if cur:
                chunks.append(cur)
            cur = p
    if cur:
        chunks.append(cur)
    out = []
    for ch in chunks:
        while len(ch) > maxlen:
            words = ch.split()
            acc = ""
            i = 0
            while i < len(words) and len(acc + " " + words[i]) <= maxlen * 0.6:
                acc = (acc + " " + words[i]).strip()
                i += 1
            out.append(acc)
            ch = " ".join(words[i:])
        out.append(ch)
    return out


def two_lines(text, width=44):
    if len(text) <= width:
        return text
    words = text.split()
    best, best_d = None, 1e9
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        d = abs(len(a) - len(b))
        if d < best_d:
            best, best_d = (a, b), d
    return best[0] + "\n" + best[1]


def write_subtitles(tl, ids, starts):
    lines = []
    k = 1
    for sid in ids:
        for s0, s1, text in tl[sid]["sentences"]:
            text = text.replace("CO2", "CO\u2082")
            g0, g1 = starts[sid] + s0, starts[sid] + s1
            chunks = split_caption(text)
            tot = sum(len(ch) for ch in chunks)
            t = g0
            for ch in chunks:
                d = (g1 - g0) * len(ch) / tot
                lines.append(f"{k}\n{fmt_ts(t)} --> {fmt_ts(t + d)}\n{two_lines(ch)}\n")
                k += 1
                t += d
    with open(os.path.join(AUD, "subtitles.srt"), "w") as f:
        f.write("\n".join(lines))
    print(f"{k - 1} subtitle cues")


def main_subs():
    tl = json.load(open(os.path.join(AUD, "timeline.json")))
    ids = list(tl.keys())
    starts, acc = {}, 0.0
    for i in ids:
        starts[i] = acc
        acc += tl[i]["duration"]
    write_subtitles(tl, ids, starts)


def main():
    tl = json.load(open(os.path.join(AUD, "timeline.json")))
    ids = list(tl.keys())
    starts = {}
    acc = 0.0
    for i in ids:
        starts[i] = acc
        acc += tl[i]["duration"]
    total = acc + CREDITS_DUR
    n = int(total * SR) + SR
    # ---------------------------------------------------------------- narration
    narr = np.zeros(n)
    for sid in ids:
        for fn, t in tl[sid]["files"]:
            x, sr = sf.read(os.path.join(AUD, "seg", fn))
            x = resample_poly(x, SR, sr)
            place(narr, x, starts[sid] + t, 1.0)
    sf.write(os.path.join(AUD, "narration_48k.wav"), narr.astype(np.float32), SR)
    # ---------------------------------------------------------------- music
    loop = make_loop()
    reps = n // len(loop) + 1
    music = np.tile(loop, (reps, 1))[:n]
    music += bells(n / SR)[:n] * 0.35
    # slow movement in level
    tt = np.arange(n) / SR
    lfo = 0.85 + 0.15 * np.sin(2 * np.pi * tt / 47.0)
    music *= lfo[:, None]
    # duck under narration
    env = env_follow(narr)
    duck = 1.0 - 0.55 * np.clip(env * 3.0, 0, 1)
    duck = lfilter([1 - np.exp(-1 / (0.3 * SR))], [1, -np.exp(-1 / (0.3 * SR))], duck)
    music *= duck[:, None]
    # fade in / out
    fi, fo = int(3 * SR), int(8 * SR)
    music[:fi] *= np.linspace(0, 1, fi)[:, None]
    music[-fo:] *= np.linspace(1, 0, fo)[:, None]
    sf.write(os.path.join(AUD, "music.wav"), (music * 0.5).astype(np.float32), SR)
    # ---------------------------------------------------------------- sfx
    sfx = np.zeros((n, 2))
    wh, sw = whoosh(), swell()
    for sid in ids[1:]:
        place(sfx, wh, starts[sid] - 0.7, 0.10)
        if tl[sid]["chapter"]:
            place(sfx, sw, starts[sid] + 0.05, 0.18)
    place(sfx, sw, starts[ids[0]] + tl[ids[0]]["cues"]["title"][0] - 0.2, 0.25)
    place(sfx, wh, total - CREDITS_DUR - 0.7, 0.10)
    # ---------------------------------------------------------------- mix
    speech = narr[env > 0.08]
    speech_rms = np.sqrt((speech ** 2).mean())
    m_rms = np.sqrt((music ** 2).mean()) + 1e-9
    music_pre = music / m_rms * speech_rms * 10 ** (-14 / 20)   # duck already applied above (about -7 dB in speech)
    sfx_peak = np.abs(sfx).max() + 1e-9
    mix = np.zeros((n, 2))
    mix[:, 0] = narr
    mix[:, 1] = narr
    mix += music_pre
    mix += sfx / sfx_peak * speech_rms * 10 ** (-6 / 20)
    print(f"speech rms {speech_rms:.4f}, music rms after scaling {np.sqrt((music_pre**2).mean()):.4f}")
    peak = np.abs(mix).max()
    mix = mix / peak * 0.89
    raw = os.path.join(AUD, "mix_raw.wav")
    sf.write(raw, mix.astype(np.float32), SR, subtype="FLOAT")
    # ---------------------------------------------------------------- loudness normalisation (two-pass)
    out = os.path.join(AUD, "mix.wav")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", raw, "-af",
                        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    js = r.stderr[r.stderr.rindex("{"): r.stderr.rindex("}") + 1]
    m = json.loads(js)
    af = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", raw, "-af", af, "-ar", str(SR), out], check=True)
    print("loudness in:", m["input_i"], "LUFS ->", "-16 target")
    write_subtitles(tl, ids, starts)
    print(f"total {total:.1f} s")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "subs":
        main_subs()
    else:
        main()
