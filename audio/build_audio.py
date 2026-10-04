#!/usr/bin/env python3
"""Offline TTS narration, fitted to the script timeline.

For every beat in script/timeline.json: synthesise each sentence separately (SVOX Pico via `pico2wave`, or espeak-ng),
measure the real durations, apply ONE tempo factor per beat (ffmpeg atempo, pitch preserved) so the speech fills the
beat's VO window, and place the sentences on a 30:00 master track.

Outputs (audio/ is git-ignored except this script):
  audio/narration.wav          master narration, mono, 16 kHz, exactly TOTAL seconds long
  audio/chNN.wav               per-chapter slices
  audio/sentences.json         {beat_id: [chapter-relative start of each sentence]}   -> scenes sync to REAL speech
  audio/cues.json              [{beat, start, end, text}] absolute times               -> subtitles
  audio/tts/                   per-sentence cache (keyed by text + engine + voice)

Environment:  TTS_ENGINE=pico|espeak (default pico)   TTS_VOICE=en-GB|en-US (pico) / en-gb (espeak)
This is a PLACEHOLDER voice (no neural TTS models are reachable in the build sandbox); swap in a real recording by
dropping `audio/narration.wav` in place and running `make subs assemble`.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TIMELINE = os.path.join(ROOT, "script", "timeline.json")
CACHE = os.path.join(HERE, "tts")
SR = 16000
LEAD, TAIL = 0.4, 0.3
GAP = 0.18                       # natural gap between sentences (s) before slack is distributed
TEMPO_MIN, TEMPO_MAX = 0.88, 1.28
ENGINE = os.environ.get("TTS_ENGINE", "pico")
VOICE = os.environ.get("TTS_VOICE", "en-GB")

# Spell out acronyms / symbols the offline voices would mangle.
PRON = [
    (r"\bTVD\b", "T V D"), (r"\bBHA\b", "B H A"), (r"\bECD\b", "E C D"), (r"\bMPD\b", "M P D"), (r"\bLWD\b", "L W D"),
    (r"\bDST\b", "D S T"), (r"\bPDC\b", "P D C"), (r"\bROV\b", "R O V"), (r"\bBOP\b", "B O P"), (r"\bsg\b", "S G"),
    (r"\bpsi\b", "P S I"), (r"\bP and A\b", "P and A"), (r"\bISO\b", "I S O"), (r"\bAPI\b", "A P I"),
    (r"\bMWD\b", "M W D"), (r"\bNCS\b", "N C S"), (r"\bMPa\b", "megapascals"), (r"\bUV\b", "U V"), (r"\bC1\b", "C one"),
    (r"→", " to "), (r"×", " times "), (r"°", " degrees "), (r"\bTD\b", "total depth"),
]


def prep(text: str) -> str:
    for pat, rep in PRON:
        text = re.sub(pat, rep, text)
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(vo: str) -> list[str]:
    return [p for p in re.split(r"(?<=[.?!])\s+", vo.strip()) if p]


def synth(text: str, path: str) -> None:
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    raw = path + ".raw.wav"
    t = prep(text)
    if ENGINE == "pico":
        subprocess.run(["pico2wave", "-l", VOICE, "-w", raw, t], check=True)
    else:
        subprocess.run(["espeak-ng", "-v", VOICE.lower(), "-s", "150", "-w", raw, t], check=True)
    # normalise to mono 16 kHz 16-bit
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-ac", "1", "-ar", str(SR), "-sample_fmt", "s16", path], check=True)
    os.remove(raw)


def read_wav(path: str) -> np.ndarray:
    with wave.open(path, "rb") as w:
        assert w.getframerate() == SR and w.getnchannels() == 1
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)


def atempo(path_in: str, path_out: str, tempo: float) -> None:
    if abs(tempo - 1.0) < 0.005:
        subprocess.run(["cp", path_in, path_out], check=True)
        return
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path_in, "-filter:a", f"atempo={tempo:.4f}", "-ar", str(SR), "-ac", "1", path_out], check=True)


def write_wav(path: str, data: np.ndarray) -> None:
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.clip(data, -32768, 32767).astype(np.int16).tobytes())


def main() -> int:
    tl = json.load(open(TIMELINE))
    total = int(round(tl["total"]))
    master = np.zeros(total * SR + SR, dtype=np.float32)
    sentences_rel, cues, warnings = {}, [], []
    os.makedirs(os.path.join(CACHE, "fit"), exist_ok=True)
    for ch in tl["chapters"]:
        for b in ch["beats"]:
            sents = split_sentences(b["vo"])
            if not sents:
                continue
            files = []
            for i, txt in enumerate(sents):
                key = hashlib.sha1(f"{ENGINE}|{VOICE}|{prep(txt)}".encode()).hexdigest()[:16]
                p = os.path.join(CACHE, f"{key}.wav")
                synth(txt, p)
                files.append(p)
            durs = [len(read_wav(f)) / SR for f in files]
            window = b["dur"] - LEAD - TAIL - b.get("pause", 0.0)
            natural = sum(durs) + GAP * (len(durs) - 1)
            tempo = min(max(natural / window, TEMPO_MIN), TEMPO_MAX)
            if natural / window > TEMPO_MAX:
                warnings.append(f"{b['id']}: speech {natural:.1f}s needs x{natural / window:.2f} for a {window:.1f}s window (capped at {TEMPO_MAX}) -> overruns")
            fitted = []
            for i, f in enumerate(files):
                out = os.path.join(CACHE, "fit", f"{b['id']}_{i}.wav")
                atempo(f, out, tempo)
                fitted.append(read_wav(out))
            speech = sum(len(x) for x in fitted) / SR
            slack = max(window - speech - GAP * (len(fitted) - 1), 0.0)
            gap = GAP + (slack / (len(fitted) - 1) if len(fitted) > 1 else 0.0)
            t = b["start"] + LEAD + (slack if len(fitted) == 1 else 0.0) * 0.0
            rel = []
            for i, x in enumerate(fitted):
                a = int(round(t * SR))
                master[a:a + len(x)] += x
                rel.append(round(t - ch["start"], 3))
                cues.append(dict(beat=b["id"], start=round(t, 3), end=round(t + len(x) / SR, 3), text=sents[i]))
                t += len(x) / SR + gap
            sentences_rel[b["id"]] = rel
    write_wav(os.path.join(HERE, "narration.wav"), master[: total * SR])
    for ch in tl["chapters"]:
        a, z = int(ch["start"] * SR), int((ch["start"] + ch["dur"]) * SR)
        write_wav(os.path.join(HERE, f"ch{ch['num']:02d}.wav"), master[a:z])
    json.dump(sentences_rel, open(os.path.join(HERE, "sentences.json"), "w"), indent=1)
    json.dump(cues, open(os.path.join(HERE, "cues.json"), "w"), indent=1)
    for w in warnings:
        print("WARN:", w)
    print(f"narration: {len(cues)} sentences, {len(sentences_rel)} beats, master {total}s -> audio/narration.wav ({ENGINE}/{VOICE})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
