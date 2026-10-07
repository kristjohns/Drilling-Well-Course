#!/usr/bin/env python3
"""Neural narration (Kokoro-82M) and a voice-first timeline.

Every sentence of every beat is synthesised at the voice's natural pace (no time-stretching), level-matched, and laid
out with natural pauses. Beat durations then FOLLOW the speech: a beat lasts as long as its narration needs, but never
less than 75 % of the visual time the script budgeted for it. Chapters 1-9 open with a title card (INTRO seconds).

Inputs   script/timeline.json   (from `make script`; the budget version is kept as script/timeline_budget.json)
Outputs  script/timeline.json   rewritten with the real beat starts/durations (+ chapter `intro`)
         audio/narration.wav    master narration, mono 24 kHz
         audio/chNN.wav         per-chapter slices
         audio/sentences.json   {beat_id: [chapter-relative start of each sentence]}   -> scenes sync to the voice
         audio/cues.json        [{beat, start, end, text}] absolute times               -> subtitles
         audio/tts/             per-sentence cache (keyed by model + voice + speed + text)

Voice model: Kokoro-82M v1.0 (Apache-2.0) run with onnxruntime via kokoro-onnx. `python audio/build_audio.py --fetch`
downloads it from the npm registry (voice styles from the official `kokoro-js` package; the fp32 ONNX weights from the
`kokoro-fp32{a,b,c}-shards` packages, which redistribute onnx-community/Kokoro-82M-v1.0-ONNX `model.onnx`) and checks
the reassembled file against the expected size and SHA-256.

Environment: TTS_VOICE (default af_heart), TTS_SPEED (base speed, default 1.0), TTS_WPM (pacing target, default 165)
"""
from __future__ import annotations
import argparse
import glob
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tarfile
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TIMELINE = os.path.join(ROOT, "script", "timeline.json")
BUDGET_TL = os.path.join(ROOT, "script", "timeline_budget.json")
CACHE = os.path.join(HERE, "tts")
MODELS = os.path.join(HERE, "models")
MODEL = os.path.join(MODELS, "kokoro-v1.0.fp32.onnx")
VOICES = os.path.join(MODELS, "voices-v1.0.npz")
MODEL_SIZE = 325_532_232
MODEL_SHA256 = "8fbea51ea711f2af382e88c833d9e288c6dc82ce5e98421ea61c058ce21a34cb"
NPM_PACKAGES = ["kokoro-js@1.2.1", "kokoro-fp32a-shards@1.0.0", "kokoro-fp32b-shards@1.0.0", "kokoro-fp32c-shards@1.0.0"]

SR = 24000
VOICE = os.environ.get("TTS_VOICE", "af_heart")
SPEED = float(os.environ.get("TTS_SPEED", "1.0"))
TARGET_WPM = float(os.environ.get("TTS_WPM", "165"))   # per-sentence pacing target (Kokoro rushes short sentences)
SPEED_MIN = 0.75
LEAD, TAIL = 0.55, 0.65          # silence before / after the narration inside a beat
GAP, GAP_Q = 0.34, 0.55          # pause after a sentence / after a question
INTRO = 2.8                      # chapter title card (chapters 1..9)
FPS = 30                         # beat durations are whole video frames, so audio and video cannot drift
MIN_VISUAL = 0.75                # a beat keeps at least this fraction of its budgeted duration
TARGET_RMS_DB = -20.0

# Respellings for words the phonemiser gets wrong (checked against kokoro's espeak-ng phonemes).
PRON = [
    (r"\bBHA\b", "B H A"), (r"\bECD\b", "E C D"), (r"\bROV\b", "R O V"), (r"\bsg\b", "S G"),
    (r"\bvon Mises\b", "fon Meezes"), (r"\bTerzaghi\b", "Terzahghi"), (r"\bJurassic\b", "Joo-rassic"),
    (r"\bHavtil\b", "Hahvteel"), (r"\bSodir\b", "Soodeer"), (r"\bD-010\b", "D zero ten"),
    (r"→", " to "), (r"×", " times "), (r"°", " degrees "),
]


def prep(text: str) -> str:
    for pat, rep in PRON:
        text = re.sub(pat, rep, text)
    return re.sub(r"\s+", " ", text).strip()


PAUSE_RE = re.compile(r"\s*\[pause\s+([\d.]+)\]")


def split_sentences(vo: str) -> list[str]:
    """Sentences without inline [pause N] markers."""
    return [p for p in re.split(r"(?<=[.?!])\s+", PAUSE_RE.sub("", vo).strip()) if p]


def inline_pauses(vo: str) -> list[float]:
    """Extra silence after each sentence, from inline `[pause N]` markers (placed right after a sentence)."""
    out = []
    for chunk in re.split(r"(?<=[.?!])\s+(?!\[pause)|(?<=\])\s+", vo.strip()):
        if not PAUSE_RE.sub("", chunk).strip():
            continue
        m = PAUSE_RE.search(chunk)
        out.append(float(m.group(1)) if m else 0.0)
    return out


# ---------------------------------------------------------------------------------------------- model
def fetch_model() -> None:
    """Download Kokoro from the npm registry and verify it."""
    os.makedirs(MODELS, exist_ok=True)
    tmp = os.path.join(MODELS, "npm")
    os.makedirs(tmp, exist_ok=True)
    subprocess.run(["npm", "pack", "--silent", *NPM_PACKAGES], cwd=tmp, check=True)
    parts, voices = {}, {}
    for tgz in glob.glob(os.path.join(tmp, "*.tgz")):
        with tarfile.open(tgz) as tf:
            for m in tf.getmembers():
                mm = re.search(r"kokoro-fp32\.part(\d+)\.bin$", m.name)
                if mm:
                    parts[int(mm.group(1))] = tf.extractfile(m).read()
                vm = re.search(r"voices/(\w+)\.bin$", m.name)
                if vm:
                    voices[vm.group(1)] = np.frombuffer(tf.extractfile(m).read(), dtype=np.float32).reshape(510, 1, 256)
    blob = b"".join(parts[i] for i in sorted(parts))
    sha = hashlib.sha256(blob).hexdigest()
    if len(blob) != MODEL_SIZE or sha != MODEL_SHA256:
        sys.exit(f"Kokoro model check failed: {len(blob)} bytes, sha256 {sha}")
    open(MODEL, "wb").write(blob)
    np.savez(VOICES, **voices)
    shutil.rmtree(tmp)
    print(f"Kokoro model OK ({len(blob):,} bytes, sha256 {sha[:12]}...), {len(voices)} voices -> {MODELS}")


_KOKORO = None


def kokoro():
    global _KOKORO
    if _KOKORO is None:
        if not (os.path.exists(MODEL) and os.path.exists(VOICES)):
            fetch_model()
        from kokoro_onnx import Kokoro
        _KOKORO = Kokoro(MODEL, VOICES)
    return _KOKORO


def paced(text: str) -> np.ndarray:
    """Synthesise at the base speed, measure the speaking rate, and re-synthesise slower if it is above TARGET_WPM."""
    a = synth(text, SPEED)
    words = max(len(prep(text).split()), 1)
    wpm = words / max(len(a) / SR, 0.2) * 60
    if wpm <= TARGET_WPM * 1.04:
        return a
    sp = max(SPEED * TARGET_WPM / wpm, SPEED_MIN)
    return synth(text, round(sp, 3))


def synth(text: str, speed: float = SPEED) -> np.ndarray:
    """Float32 mono 24 kHz, cached; leading/trailing silence trimmed, level-matched."""
    t = prep(text)
    key = hashlib.sha1(f"kokoro-v1.0|{VOICE}|{speed}|{t}".encode()).hexdigest()[:16]
    path = os.path.join(CACHE, f"{key}.npy")
    if os.path.exists(path):
        return np.load(path)
    lang = "en-gb" if VOICE[0] == "b" else "en-us"
    a, sr = kokoro().create(t, voice=VOICE, speed=speed, lang=lang)
    assert sr == SR
    a = np.asarray(a, dtype=np.float32)
    # trim silence (threshold relative to peak), keep 30 ms margins
    env = np.abs(a)
    thr = max(env.max() * 0.02, 1e-4)
    idx = np.where(env > thr)[0]
    if len(idx):
        a = a[max(idx[0] - int(0.03 * SR), 0): idx[-1] + int(0.06 * SR)]
    # level match on the speech RMS
    frames = a[: len(a) // 480 * 480].reshape(-1, 480)
    rms = np.sqrt((frames ** 2).mean(axis=1))
    active = rms[rms > rms.max() * 0.1]
    if len(active):
        g = 10 ** (TARGET_RMS_DB / 20) / max(float(np.sqrt((active ** 2).mean())), 1e-6)
        a = a * g
    a = np.clip(a, -0.98, 0.98)
    os.makedirs(CACHE, exist_ok=True)
    np.save(path, a)
    return a


def write_wav(path: str, data: np.ndarray) -> None:
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(data, -1, 1) * 32767).astype(np.int16).tobytes())


# ---------------------------------------------------------------------------------------------- timeline
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="only download + verify the voice model")
    a = ap.parse_args()
    if a.fetch:
        fetch_model()
        return 0
    tl = json.load(open(TIMELINE))
    if not tl.get("voice_timed"):
        shutil.copy(TIMELINE, BUDGET_TL)          # fresh output of `make script`
    base = json.load(open(BUDGET_TL))
    # 1. synthesise
    speech = {}
    n = sum(len(split_sentences(b["vo"])) for ch in base["chapters"] for b in ch["beats"])
    done = 0
    for ch in base["chapters"]:
        for b in ch["beats"]:
            clips = []
            for s in split_sentences(b["vo"]):
                clips.append((s, paced(s)))
                done += 1
                if done % 25 == 0:
                    print(f"  synthesised {done}/{n} sentences", flush=True)
            speech[b["id"]] = clips
    # 2. lay out
    out = {"total": 0.0, "voice_timed": True, "voice": f"kokoro-v1.0 {VOICE}, paced to {TARGET_WPM:.0f} wpm", "chapters": []}
    t_abs = 0.0
    master_parts = []      # (abs_start, samples)
    sentences_rel, cues = {}, []
    for ch in base["chapters"]:
        intro = INTRO if 1 <= ch["num"] <= 9 else 0.0
        c_out = {k: v for k, v in ch.items() if k != "beats"}
        c_out["start"] = round(t_abs, 3)
        c_out["intro"] = intro
        c_out["beats"] = []
        t = t_abs + intro
        for b in ch["beats"]:
            clips = speech[b["id"]]
            extra = inline_pauses(b["vo"])
            extra += [0.0] * (len(clips) - len(extra))
            gaps = [(GAP_Q if s.rstrip().endswith("?") else GAP) + extra[i] for i, (s, _) in enumerate(clips[:-1])]
            talk = sum(len(x) / SR for _, x in clips) + sum(gaps)
            need = LEAD + talk + TAIL + b.get("pause", 0.0)
            dur = max(need, MIN_VISUAL * b["dur"]) if clips else max(b["dur"] * MIN_VISUAL, 3.0)
            dur = math.ceil(dur * FPS - 1e-6) / FPS
            slack = dur - need
            # spend up to 0.25 s of slack per gap on breathing room; the rest becomes a visual hold at the end
            extra_gap = min(0.25, slack * 0.5 / max(len(gaps), 1)) if gaps else 0.0
            bb = dict(b)
            bb["start"] = round(t, 3)
            bb["dur"] = round(dur, 3)
            c_out["beats"].append(bb)
            ts = t + LEAD
            rel = []
            for i, (s, x) in enumerate(clips):
                master_parts.append((ts, x))
                rel.append(round(ts - t_abs, 3))
                cues.append(dict(beat=b["id"], start=round(ts, 3), end=round(ts + len(x) / SR, 3), text=s))
                ts += len(x) / SR + (gaps[i] + extra_gap if i < len(gaps) else 0.0)
            sentences_rel[b["id"]] = rel
            t += dur
        c_out["dur"] = round(t - t_abs, 3)
        out["chapters"].append(c_out)
        t_abs = t
    out["total"] = round(t_abs, 3)
    # 3. render the master
    total_n = int(round(t_abs * SR)) + SR
    master = np.zeros(total_n, dtype=np.float32)
    for ts, x in master_parts:
        i = int(round(ts * SR))
        master[i:i + len(x)] += x
    master = master[: int(round(t_abs * SR))]
    write_wav(os.path.join(HERE, "narration.wav"), master)
    for ch in out["chapters"]:
        i0, i1 = int(round(ch["start"] * SR)), int(round((ch["start"] + ch["dur"]) * SR))
        write_wav(os.path.join(HERE, f"ch{ch['num']:02d}.wav"), master[i0:i1])
    json.dump(out, open(TIMELINE, "w"), indent=1)
    json.dump(sentences_rel, open(os.path.join(HERE, "sentences.json"), "w"), indent=1)
    json.dump(cues, open(os.path.join(HERE, "cues.json"), "w"), indent=1)
    words = sum(len(c["text"].split()) for c in cues)
    talk = sum(c["end"] - c["start"] for c in cues)
    print(f"narration: {len(cues)} sentences, {words} words, {talk / 60:.1f} min of speech ({words / (talk / 60):.0f} wpm while talking); "
          f"film {t_abs / 60:.2f} min ({int(t_abs // 60)}:{t_abs % 60:04.1f}) -> audio/narration.wav, script/timeline.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
