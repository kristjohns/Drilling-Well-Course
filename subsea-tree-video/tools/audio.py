#!/usr/bin/env python3
"""Sound design + mix for the subsea-tree video.

  python3 tools/audio.py            -> build/audio_mix.wav (stereo, 48 kHz, float32, un-mastered)
                                       then ffmpeg loudnorm (-16 LUFS) -> build/audio_final.wav

Inputs : build/narration.wav (Kokoro TTS, aligned to src/data/timings.json)
         build/sfx.json      (cue list exported by the scene builders: node tools/dump-sfx.mjs)
Output : narration + synthesised foley / UI sounds + a quiet ambient bed that ducks under the voice.
Everything is synthesised here (numpy/scipy) – no third-party samples, so no licensing issues.
"""
import json, subprocess, sys, os, math
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.ndimage import maximum_filter1d

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
rng = np.random.default_rng(20250331)

timings = json.load(open(f'{ROOT}/src/data/timings.json'))
DUR = timings['meta']['duration']
N = int(round(DUR * SR)) + SR  # one second of tail


# ----------------------------------------------------------------------------- helpers
def movavg(x, w):
    """centred moving average (same length) via cumulative sums – O(N)"""
    c = np.cumsum(np.insert(x.astype(np.float64), 0, 0.0))
    y = np.empty(len(x))
    h = w // 2
    idx = np.arange(len(x))
    lo = np.clip(idx - h, 0, len(x))
    hi = np.clip(idx + w - h, 0, len(x))
    y = (c[hi] - c[lo]) / np.maximum(hi - lo, 1)
    return y


def t_of(n):
    return np.arange(n, dtype=np.float64) / SR


def exp_env(n, tau):
    return np.exp(-t_of(n) / tau)


def noise(n):
    return rng.standard_normal(n)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype='band', fs=SR, output='sos')
    return signal.sosfilt(sos, x)


def lp(x, fc, order=2):
    sos = signal.butter(order, fc, btype='low', fs=SR, output='sos')
    return signal.sosfilt(sos, x)


def hp(x, fc, order=2):
    sos = signal.butter(order, fc, btype='high', fs=SR, output='sos')
    return signal.sosfilt(sos, x)


def fade(x, a=0.005, b=0.01):
    n = len(x)
    ia, ib = min(int(a * SR), n // 2), min(int(b * SR), n // 2)
    if ia:
        x[:ia] *= np.linspace(0, 1, ia)
    if ib:
        x[-ib:] *= np.linspace(1, 0, ib)
    return x


def norm_peak(x, p=1.0):
    m = np.max(np.abs(x)) or 1.0
    return x / m * p


def sine(f, n, ph=0.0):
    return np.sin(2 * np.pi * f * t_of(n) + ph)


def sweep(f0, f1, n, exp=True):
    t = t_of(n)
    T = n / SR
    if exp:
        k = (f1 / f0) ** (1 / T)
        phase = 2 * np.pi * f0 * (k ** t - 1) / math.log(k)
    else:
        phase = 2 * np.pi * (f0 * t + (f1 - f0) * t ** 2 / (2 * T))
    return np.sin(phase)


def compress(x, thr_db=-21.0, ratio=3.2, knee=8.0, makeup_db=3.0):
    """offline, zero-phase (look-ahead) soft-knee compressor for the voice track"""
    a = np.abs(x)
    env = maximum_filter1d(a, size=int(0.006 * SR))
    env = signal.sosfiltfilt(signal.butter(2, 45, fs=SR, output='sos'), env)
    env_db = 20 * np.log10(np.maximum(env, 1e-6))
    over = env_db - thr_db
    red = np.where(over < -knee / 2, 0.0, np.where(over > knee / 2, over * (1 - 1 / ratio), ((over + knee / 2) ** 2) / (2 * knee) * (1 - 1 / ratio)))
    gain_db = signal.sosfiltfilt(signal.butter(2, 25, fs=SR, output='sos'), -red) + makeup_db
    return x * (10 ** (gain_db / 20))


# ------------------------------------------------------------------------- sound recipes
def s_tick(g=1.0):
    n = int(0.09 * SR)
    x = sine(2300, n) * exp_env(n, 0.006) * 0.6 + hp(noise(n), 3000) * exp_env(n, 0.002) * 0.25
    return fade(x) * 0.5 * g


def s_clock(tock=False):
    n = int(0.14 * SR)
    f = 760 if tock else 1010
    x = sine(f, n) * exp_env(n, 0.014) * 0.6 + sine(f * 2.4, n) * exp_env(n, 0.006) * 0.25 + bp(noise(n), 1500, 4500) * exp_env(n, 0.004) * 0.4
    return fade(x) * 1.1


def s_chime(g=1.0):
    def bell(f, dur=1.4):
        n = int(dur * SR)
        x = np.zeros(n)
        for ratio, amp, tau in [(1, 1.0, 0.7), (2.76, 0.35, 0.35), (5.4, 0.12, 0.18), (0.5, 0.25, 0.9)]:
            x += amp * sine(f * ratio, n) * exp_env(n, tau)
        return fade(x, 0.002, 0.05)
    a = bell(988, 1.4)
    b = bell(1480, 1.6)
    out = np.zeros(int(1.9 * SR))
    out[:len(a)] += a * 0.7
    d = int(0.11 * SR)
    out[d:d + len(b)] += b * 0.6
    return out * 0.38 * g


def s_clunk(g=1.0, deep=False):
    n = int(0.7 * SR)
    x = np.zeros(n)
    k = int(0.22 * SR)
    x[:k] += sweep(130, 42, k) * np.linspace(1, 0, k) ** 1.5 * 0.95
    for f, a, tau in [(310, 0.30, 0.09), (470, 0.22, 0.07), (740, 0.14, 0.05), (1130, 0.08, 0.035)]:
        x += a * sine(f * (1 + 0.01 * rng.standard_normal()), n) * exp_env(n, tau)
    x += lp(noise(n), 1400) * exp_env(n, 0.018) * 0.55
    if deep:
        x = lp(x, 700) * 1.3
    return fade(x, 0.001, 0.08) * 0.62 * g


def s_slide(g=1.0, d=0.9):
    n = int(d * SR)
    t = t_of(n)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5
    x = bp(noise(n), 350, 1600) * env * 0.5 + sine(95, n) * env * 0.12 + bp(noise(n), 2500, 6500) * env * 0.12
    return fade(x, 0.02, 0.05) * 0.5 * g


def s_valve_open(d=1.2, deep=False):
    d = float(np.clip(d, 0.5, 3.0))
    n = int((d + 0.35) * SR)
    t = t_of(n)
    env = np.clip(t / (0.15 * d), 0, 1) * np.clip((d - t) / (0.3 * d) + 0.2, 0, 1) * (t < d + 0.1)
    hiss = bp(noise(n), 2200, 7000) * env * 0.16
    rumble = lp(noise(n), 260) * np.clip(t / 0.1, 0, 1) * np.clip((d - t) / 0.12, 0, 1) * 0.5
    hum = sine(70 + 25 * np.clip(t / d, 0, 1), n) * env * 0.08
    x = hiss + rumble + hum
    # end-stop click
    k = int(0.09 * SR)
    st = int(d * SR)
    x[st:st + k] += (sine(900, k) * exp_env(k, 0.012) * 0.35 + lp(noise(k), 1800) * exp_env(k, 0.01) * 0.4)
    if deep:
        x = lp(x, 900)
    return fade(x, 0.01, 0.1) * 0.7


def s_valve_close(d=0.6, deep=False):
    d = float(np.clip(d, 0.3, 2.0))
    n = int((d + 0.9) * SR)
    t = t_of(n)
    # vent psss + spring release
    vent = bp(noise(n), 3000, 8000) * np.exp(-t / 0.12) * 0.22
    spring = sweep(300, 900, int(0.15 * SR)) * np.linspace(1, 0, int(0.15 * SR))
    x = vent
    x[:len(spring)] += spring * 0.18
    slide = lp(noise(n), 300) * np.clip(t / 0.05, 0, 1) * np.clip((d - t) / 0.08, 0, 1) * 0.5
    x += slide
    c = s_clunk(1.0, deep)
    st = int(d * SR)
    m = min(len(c), n - st)
    x[st:st + m] += c[:m] * 1.1
    return fade(x, 0.003, 0.1)


def s_choke(d=1.0):
    d = float(np.clip(d, 0.3, 3.0))
    n = int((d + 0.1) * SR)
    x = np.zeros(n)
    k = int(0.03 * SR)
    for i in range(max(2, int(d * 9))):
        s = int(i / 9 * SR)
        if s + k >= n:
            break
        x[s:s + k] += (sine(1400, k) * exp_env(k, 0.005) * 0.4 + hp(noise(k), 2500) * exp_env(k, 0.003) * 0.3)
    x += lp(noise(n), 180) * 0.08 * np.clip(t_of(n) / 0.1, 0, 1)
    return x * 0.6


def s_alarm():
    out = np.zeros(int(3.0 * SR))
    for i in range(6):
        f = 720 if i % 2 == 0 else 540
        n = int(0.42 * SR)
        t = t_of(n)
        env = np.clip(t / 0.01, 0, 1) * np.clip((0.42 - t) / 0.04, 0, 1)
        sq = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * f * t) * 0.5
        x = bp(sq, 350, 3000) * env
        s = int(i * 0.45 * SR)
        out[s:s + n] += x
    out = lp(out, 3500)
    return fade(out, 0.01, 0.2) * 0.30


def s_whoosh(g=1.0, d=0.8):
    n = int(d * SR)
    t = t_of(n)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    x = noise(n)
    out = np.zeros(n)
    # time-varying lowpass: crude by mixing a few band-limited copies
    for fc, w in [(400, 1.0), (1200, 0.8), (3500, 0.5), (8000, 0.3)]:
        c = lp(x, fc)
        out += c * w * np.exp(-((t / d - (np.log(fc) - np.log(300)) / (np.log(9000) - np.log(300))) ** 2) / 0.04)
    return fade(out * env, 0.02, 0.1) * 0.3 * g


def s_thud():
    n = int(1.4 * SR)
    x = sweep(90, 34, n, exp=True) * exp_env(n, 0.45) * 0.9 + lp(noise(n), 300) * exp_env(n, 0.12) * 0.5
    return fade(x, 0.002, 0.2) * 0.85


def s_scan(d=2.4):
    n = int(d * SR)
    t = t_of(n)
    x = sweep(260, 1500, n, exp=True) * (0.6 + 0.4 * np.sin(2 * np.pi * 16 * t))
    x = lp(x, 3500) * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 0.8
    return fade(x, 0.05, 0.2) * 0.22


def s_pop():
    n = int(0.09 * SR)
    x = sweep(480, 1500, n) * exp_env(n, 0.02)
    return fade(x, 0.001, 0.02) * 0.4


def s_hiss():
    n = int(1.0 * SR)
    t = t_of(n)
    x = bp(noise(n), 3500, 9000) * np.exp(-t / 0.35) * np.clip(t / 0.03, 0, 1)
    return fade(x, 0.005, 0.1) * 0.35


def s_ping():
    n = int(2.4 * SR)
    x = (sine(1180, n) + 0.3 * sine(2360, n)) * exp_env(n, 0.8)
    return fade(x, 0.003, 0.2) * 0.22


RECIPES = {
    'tick': lambda c: s_tick(c.get('gain', 1)),
    'chime': lambda c: s_chime(c.get('gain', 1)),
    'clunk': lambda c: s_clunk(c.get('gain', 1)),
    'slide': lambda c: s_slide(c.get('gain', 1)),
    'whoosh': lambda c: s_whoosh(c.get('gain', 1)),
    'thud': lambda c: s_thud(),
    'scan': lambda c: s_scan(2.4),
    'pop': lambda c: s_pop(),
    'hiss': lambda c: s_hiss(),
    'ping': lambda c: s_ping(),
    'alarm': lambda c: s_alarm(),
    'valveOpen': lambda c: s_valve_open(c.get('d', 1.2), c.get('deep', False)),
    'valveClose': lambda c: s_valve_close(c.get('d', 0.6), c.get('deep', False)),
    'chokeAdjust': lambda c: s_choke(c.get('d', 1.0)),
}


# --------------------------------------------------------------------------- the bed
def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def pad_chord(notes, dur):
    n = int(dur * SR)
    t = t_of(n)
    out = np.zeros(n)
    for m in notes:
        f = midi(m)
        for det in (-0.07, 0.0, 0.08):
            vib = 1 + 0.0015 * np.sin(2 * np.pi * (0.12 + 0.05 * rng.random()) * t + rng.random() * 6)
            ph = 2 * np.pi * np.cumsum(f * (2 ** (det / 12)) * vib) / SR
            saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
            out += saw / 3.0
    out = lp(out, 760, 2) / max(1, len(notes)) * 1.6
    env = np.clip(t / 3.2, 0, 1) ** 1.5 * np.clip((dur - t) / 3.2, 0, 1) ** 1.5
    return out * env


def build_bed():
    L = np.zeros(N, dtype=np.float32)
    R = np.zeros(N, dtype=np.float32)
    # deep water rumble (brown noise, very low)
    for ch in (L, R):
        b = np.cumsum(rng.standard_normal(N)) / 600.0
        b = hp(b, 25, 2)
        b = lp(b, 130, 3)
        b = b / (np.max(np.abs(b)) + 1e-9)
        lfo = 0.65 + 0.35 * np.sin(2 * np.pi * 0.04 * t_of(N) + rng.random() * 6)
        ch += (b * lfo * 0.10).astype(np.float32)
    # chord pad: Am9 - Fmaj7 - C - G (12 s each, overlapping)
    prog = [[45, 52, 57, 60, 64, 71], [41, 48, 53, 57, 60, 64], [48, 55, 60, 64, 67, 71], [43, 50, 55, 59, 62, 66]]
    seg = 12.0
    pos = 0.0
    i = 0
    while pos < DUR + 6:
        notes = prog[i % 4]
        dur = seg + 3.2
        a = pad_chord(notes, dur)
        s = int(pos * SR)
        m = min(len(a), N - s)
        if m <= 0:
            break
        pan = 0.5 + 0.18 * math.sin(i * 1.7)
        L[s:s + m] += (a[:m] * (1 - pan) * 1.2).astype(np.float32)
        R[s:s + m] += (a[:m] * pan * 1.2).astype(np.float32)
        pos += seg
        i += 1
    # airy shimmer (fifth + octave, slow tremolo)
    t = t_of(N)
    sh = (sine(midi(81), N) + 0.6 * sine(midi(88), N)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)) ** 3 * 0.012
    L += sh.astype(np.float32)
    R += np.roll(sh, 900).astype(np.float32)
    # global fade in / out
    g = np.clip(t / 6.0, 0, 1) * np.clip((DUR + 0.5 - t) / 6.0, 0, 1)
    L *= g.astype(np.float32)
    R *= g.astype(np.float32)
    return L, R


# ------------------------------------------------------------------------------ mix
def main():
    print('loading narration …')
    nar, sr = sf.read(f'{ROOT}/build/narration.wav')
    if nar.ndim > 1:
        nar = nar.mean(axis=1)
    nar = signal.resample_poly(nar, SR // sr, 1) if SR % sr == 0 else signal.resample(nar, int(len(nar) * SR / sr))
    nar = hp(nar, 70, 2)
    # gentle level riding: normalise 400 ms RMS toward a target, limited to ±5 dB
    win = int(0.4 * SR)
    rms = np.sqrt(movavg(nar ** 2, win) + 1e-9)
    active = rms > 0.02
    tgt = np.median(rms[active])
    gain = np.clip(tgt / (rms + 1e-9), 0.56, 1.8)
    gain = np.where(active, gain, 1.0)
    gain = signal.sosfiltfilt(signal.butter(2, 4.0, btype='low', fs=SR, output='sos'), gain)
    nar = nar * gain
    nar = compress(nar)
    nar = np.tanh(nar * 1.15) / np.tanh(1.15)       # soft peak control
    nar = nar / np.max(np.abs(nar)) * 0.84
    NAR = np.zeros(N)
    m = min(len(nar), N)
    NAR[:m] = nar[:m]

    # narration activity envelope (for ducking)
    env = np.abs(NAR)
    env = np.sqrt(movavg(env ** 2, int(0.05 * SR)))
    act = np.clip(env / (np.percentile(env[env > 0.01], 70) if np.any(env > 0.01) else 1), 0, 1)
    # smooth: fast attack, slower release
    a_att, a_rel = math.exp(-1 / (0.06 * SR)), math.exp(-1 / (0.55 * SR))
    duck = np.zeros(N)
    d_ = 0.0
    step = 48
    for i in range(0, N, step):
        v = act[i:i + step].max()
        d_ = v if v > d_ else d_ * (a_rel ** step)
        duck[i:i + step] = d_
    duck = np.clip(duck, 0, 1)

    print('bed …')
    bL, bR = build_bed()
    bed_gain = 10 ** (-15.5 / 20)
    bedduck = 1.0 - 0.70 * duck
    bL = bL * bedduck * bed_gain
    bR = bR * bedduck * bed_gain

    print('sfx …')
    cues = json.load(open(f'{ROOT}/build/sfx.json'))
    manual = [c for c in cues if not c.get('auto')]
    sfxL = np.zeros(N)
    sfxR = np.zeros(N)

    def place(x, t, pan=0.5, g=1.0):
        s = int(max(0.0, t) * SR)
        if s >= N:
            return
        m = min(len(x), N - s)
        sfxL[s:s + m] += x[:m] * (1 - pan) * 2 * g * 0.5
        sfxR[s:s + m] += x[:m] * pan * 2 * g * 0.5

    def near_manual(t, names, tol=0.6):
        return any(abs(c['t'] - t) < tol and c['name'] in names for c in manual)

    n_placed = 0
    for c in cues:
        name = c['name']
        if name not in RECIPES:
            print('  (no recipe for', name, ')')
            continue
        t = c['t']
        if c.get('auto'):
            if name == 'valveOpen' and near_manual(t, ('slide', 'valveOpen'), 0.5):
                continue
            if name == 'valveClose' and near_manual(t + c.get('d', 0.6), ('clunk', 'valveClose'), 0.55):
                continue
        x = RECIPES[name](c)
        pan = 0.5 + 0.12 * rng.standard_normal()
        place(x, t, float(np.clip(pan, 0.3, 0.7)), 1.0)
        n_placed += 1
    # soft whoosh at every scene boundary
    for s in timings['scenes'][1:]:
        place(s_whoosh(0.55, 0.9), s['start'] - 0.45, 0.5)
    # thinking clock in the quiz
    for q, a in (('q1', 'a1'), ('q2', 'a2'), ('q3', 'a3')):
        sc = next(s for s in timings['scenes'] if s['id'] == 'quiz')
        t0 = sc['beats'][q]['end'] + 0.25
        t1 = sc['beats'][a]['start'] - 0.2
        k = 0
        while t0 + k < t1:
            place(s_clock(k % 2 == 1), t0 + k, 0.5)
            k += 1
    print('  placed', n_placed, 'cues')
    sd = 10 ** (-9 / 20)
    sduck = 1.0 - 0.30 * duck
    sfxL *= sduck * sd
    sfxR *= sduck * sd

    left = NAR + bL + sfxL
    right = NAR + bR + sfxR
    mix = np.stack([left, right], axis=1)[: int(DUR * SR)]
    pk = np.max(np.abs(mix))
    print('peak', round(20 * math.log10(pk), 2), 'dBFS')
    if pk > 0.95:
        mix *= 0.95 / pk
    sf.write(f'{ROOT}/build/audio_mix.wav', mix.astype(np.float32), SR, subtype='FLOAT')
    print('wrote build/audio_mix.wav')

    # master: two-pass loudnorm -> -16 LUFS / -1.5 dBTP
    src = f'{ROOT}/build/audio_mix.wav'
    p1 = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', src, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    j = p1.stderr[p1.stderr.rfind('{'):p1.stderr.rfind('}') + 1]
    st = json.loads(j)
    print('measured', {k: st[k] for k in ('input_i', 'input_tp', 'input_lra', 'input_thresh')})
    flt = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={st['input_i']}:measured_TP={st['input_tp']}:"
           f"measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', src, '-af', flt, '-ar', str(SR), f'{ROOT}/build/audio_final.wav'], check=True)
    p2 = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', f'{ROOT}/build/audio_final.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    j2 = json.loads(p2.stderr[p2.stderr.rfind('{'):p2.stderr.rfind('}') + 1])
    print('final   ', {k: j2[k] for k in ('input_i', 'input_tp', 'input_lra')})
    print('wrote build/audio_final.wav')


if __name__ == '__main__':
    main()
