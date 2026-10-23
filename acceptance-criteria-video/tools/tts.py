#!/usr/bin/env python3
"""Narration and timeline: script/script.md -> Kokoro-82M speech -> src/data/timeline.json + build/audio/narration.wav

Every sentence is synthesised on its own (cached), so sentence start times are exact. Word times inside a sentence
are estimated from phoneme counts and anchored on the pauses actually found in the audio; {cue} markers in the
script resolve to the start time of the word that follows them. Beats last as long as their narration needs
(plus LEAD, TAIL and any HOLD line); chapters 1..10 open with a TITLE-second title card.

    python3 tools/tts.py                    # build (cached per sentence)
    python3 tools/tts.py --fetch            # only assemble + verify the voice model (npm registry)
    python3 tools/tts.py --voice bm_george  # other voice
Environment: TTS_VOICE (af_heart), TTS_SPEED (0.92), TTS_WPM (158 = re-synthesise slower above this pace)
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "script", "script.md")
OUT_TL = os.path.join(ROOT, "src", "data", "timeline.json")
BUILD = os.path.join(ROOT, "build")
CACHE = os.path.join(BUILD, "tts-cache")
AUDIO = os.path.join(BUILD, "audio")
MODELS = os.path.join(BUILD, "models")
MODEL = os.path.join(MODELS, "kokoro-v1.0.fp32.onnx")
VOICES = os.path.join(MODELS, "voices-v1.0.npz")
MODEL_SIZE = 325_532_232
MODEL_SHA256 = "8fbea51ea711f2af382e88c833d9e288c6dc82ce5e98421ea61c058ce21a34cb"
NPM_PACKAGES = ["kokoro-js@1.2.1", "kokoro-fp32a-shards@1.0.0", "kokoro-fp32b-shards@1.0.0",
                "kokoro-fp32c-shards@1.0.0"]

SR = 24000
FPS = 30
VOICE = os.environ.get("TTS_VOICE", "af_heart")
SPEED = float(os.environ.get("TTS_SPEED", "0.88"))
TARGET_WPM = float(os.environ.get("TTS_WPM", "158"))
SPEED_MIN = 0.78
LEAD, TAIL = 0.6, 0.75          # silence before the first / after the last sentence of a beat
GAP = 0.38                      # pause between sentences
TITLE = 3.2                     # chapter title card
TARGET_RMS_DB = -20.0

# Spoken respellings (applied to the TTS text only; subtitles keep the script text).
PRON = [
    (r"\bNORSOK\b", "Norsock"), (r"\bvon Mises\b", "von Meezes"), (r"\bASME\b", "Azmee"),
    (r"\btriaxiality\b", "tri-axiality"), (r"\btriaxial\b", "tri-axial"),
]
LETTERS = {"b": "bee", "c": "see", "d": "dee", "e": "ee", "f": "eff", "g": "gee", "h": "aitch", "i": "eye",
           "j": "jay", "k": "kay", "l": "el", "m": "em", "n": "en", "o": "oh", "p": "pee", "q": "queue",
           "r": "ar", "s": "ess", "t": "tee", "u": "you", "v": "vee", "w": "double you", "x": "ex",
           "y": "why", "z": "zee"}


def spoken(text: str) -> str:
    t = text
    for pat, rep in PRON:
        t = re.sub(pat, rep, t)

    def letter(m):
        w = m.group(0)
        if w == "a" or w == "I":
            return w
        if w == "A":
            return "ay"
        return LETTERS.get(w.lower(), w)
    t = re.sub(r"(?<![\w'’-])[A-Za-z](?![\w'’-])", letter, t)
    return re.sub(r"\s+", " ", t).strip()


# ------------------------------------------------------------------------------------------------ script parsing
def parse_script(path=SCRIPT):
    chapters, ch, beat = [], None, None
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        m = re.match(r"^# (\d+) \| (.+?) \| (\w+)\s*$", line)
        if m:
            no, title, cid = m.group(1), m.group(2).strip(), m.group(3)
            ch = {"no": int(no), "title": title, "id": cid, "beats": []}
            chapters.append(ch)
        elif line.startswith("## "):
            bid, name = [x.strip() for x in line[3:].split("|", 1)]
            beat = {"id": bid, "name": name, "shot": "", "vo": "", "hold": 0.0}
            ch["beats"].append(beat)
        elif line.startswith("SHOT:") and beat is not None:
            beat["shot"] = line[5:].strip()
        elif line.startswith("VO:") and beat is not None:
            beat["vo"] = line[3:].strip()
        elif line.startswith("HOLD:") and beat is not None:
            beat["hold"] = float(line[5:].strip())
    return chapters


PAUSE_RE = re.compile(r"\[pause\s+([\d.]+)\]")


def split_sentences(vo: str):
    """[(sentence text with {cues}, extra pause after)]"""
    out = []
    parts = re.split(r"(?<=[.?!])\s+", vo.strip())
    for p in parts:
        m = PAUSE_RE.search(p)
        extra = float(m.group(1)) if m else 0.0
        txt = PAUSE_RE.sub("", p).strip()
        if not txt:
            if out:
                out[-1] = (out[-1][0], out[-1][1] + extra)
            continue
        out.append((txt, extra))
    return out


def tokens_with_cues(sentence: str):
    """Display tokens and the cue names attached to the token that follows each {cue}."""
    toks, pending = [], []
    for raw in sentence.split():
        cues = re.findall(r"\{(\w+)\}", raw)
        word = re.sub(r"\{\w+\}", "", raw)
        pending += cues
        if not word:
            continue
        toks.append({"w": word, "cues": pending})
        pending = []
    if pending and toks:
        toks[-1]["cues_end"] = pending
    return toks


# ------------------------------------------------------------------------------------------------ voice
def fetch_model():
    os.makedirs(MODELS, exist_ok=True)
    if os.path.exists(MODEL) and os.path.exists(VOICES):
        return
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
    print(f"Kokoro model OK ({len(blob):,} bytes), {len(voices)} voices")


_K = None


def kokoro():
    global _K
    if _K is None:
        fetch_model()
        from kokoro_onnx import Kokoro
        _K = Kokoro(MODEL, VOICES)
    return _K


def synth(text: str, speed: float) -> np.ndarray:
    key = hashlib.sha1(f"kokoro-v1.0|{VOICE}|{speed}|{text}".encode()).hexdigest()[:16]
    path = os.path.join(CACHE, f"{key}.npy")
    if os.path.exists(path):
        return np.load(path)
    lang = "en-gb" if VOICE[0] == "b" else "en-us"
    a, sr = kokoro().create(text, voice=VOICE, speed=speed, lang=lang)
    assert sr == SR
    a = np.asarray(a, dtype=np.float32)
    env = np.abs(a)
    thr = max(env.max() * 0.02, 1e-4)
    idx = np.where(env > thr)[0]
    if len(idx):
        a = a[max(idx[0] - int(0.03 * SR), 0): idx[-1] + int(0.06 * SR)]
    frames = a[: len(a) // 480 * 480].reshape(-1, 480)
    rms = np.sqrt((frames ** 2).mean(axis=1))
    active = rms[rms > rms.max() * 0.1]
    if len(active):
        a = a * (10 ** (TARGET_RMS_DB / 20) / max(float(np.sqrt((active ** 2).mean())), 1e-6))
    a = np.clip(a, -0.98, 0.98).astype(np.float32)
    os.makedirs(CACHE, exist_ok=True)
    np.save(path, a)
    return a


def paced(text: str) -> tuple[np.ndarray, float]:
    a = synth(text, SPEED)
    words = max(len(text.split()), 1)
    wpm = words / max(len(a) / SR, 0.2) * 60
    if wpm <= TARGET_WPM * 1.03:
        return a, SPEED
    sp = round(max(SPEED * TARGET_WPM / wpm, SPEED_MIN), 3)
    return synth(text, sp), sp


# ------------------------------------------------------------------------------------------------ word timing
PAUSE_MARKS = {",": 0.16, ";": 0.2, ":": 0.22, ".": 0.34, "?": 0.34, "!": 0.34}


def find_silences(audio, thresh_db=-40.0, min_len=0.085):
    frame = int(0.01 * SR)
    n = len(audio) // frame
    if n == 0:
        return []
    rms = np.sqrt((audio[: n * frame].reshape(n, frame) ** 2).mean(1))
    quiet = rms < (rms.max() + 1e-9) * 10 ** (thresh_db / 20)
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j + 1 < n and quiet[j + 1]:
                j += 1
            if (j - i + 1) * 0.01 >= min_len and i > 0 and j < n - 1:
                runs.append((i * 0.01, (j + 1) * 0.01))
            i = j + 1
        else:
            i += 1
    return runs


def word_times(toks, audio, lang):
    """Phoneme-weighted word times, anchored on the silences found in the audio (snapped to punctuation)."""
    k = kokoro()
    dur = len(audio) / SR
    n = len(toks)
    weights, pause_after = [], []
    for i, t in enumerate(toks):
        ph = k.tokenizer.phonemize(spoken(t["w"]), lang)
        weights.append(max(1, len([c for c in ph if c not in " ˈˌː"])))
        post = re.findall(r"[.,;:!?]+$", t["w"])
        pause_after.append(max((PAUSE_MARKS.get(c, 0) for c in post[0]), default=0.0) if post and i < n - 1 else 0.0)
    sil = find_silences(audio)
    # candidate boundaries: after tokens with punctuation; match each silence to the closest predicted boundary
    tot_w = sum(weights)
    speech = dur - sum(pause_after)
    pred_end, t = [], 0.0
    for i in range(n):
        t += speech * weights[i] / tot_w
        pred_end.append(t)
        t += pause_after[i]
    anchors, used = [], set()
    for ss, se in sil:
        mid = 0.5 * (ss + se)
        best, bd = None, 1e9
        for i in range(n - 1):
            if i in used:
                continue
            d = abs(pred_end[i] - mid) * (0.6 if pause_after[i] > 0 else 1.0)
            if d < bd:
                best, bd = i, d
        if best is not None and bd < 0.6:
            anchors.append((best + 1, ss, se))
            used.add(best)
    anchors.sort()
    times = [None] * n
    prev_i, prev_t = 0, 0.0
    for b, ss, se in anchors + [(n, dur, dur)]:
        idx = list(range(prev_i, b))
        if idx:
            internal = sum(pause_after[j] for j in idx[:-1])
            sp = max(0.05, (ss - prev_t) - internal)
            tw = sum(weights[j] for j in idx)
            t0 = prev_t
            for j in idx:
                t1 = t0 + sp * weights[j] / tw
                times[j] = (t0, t1)
                t0 = t1 + (pause_after[j] if j != idx[-1] else 0.0)
        prev_i, prev_t = b, se
    return times


# ------------------------------------------------------------------------------------------------ build
def snap(t):
    return round(t * FPS) / FPS


def build(args):
    chapters = parse_script()
    lang = "en-gb" if VOICE[0] == "b" else "en-us"
    t = 0.0
    track = []                       # (start time, audio)
    out = {"fps": FPS, "voice": VOICE, "speed": SPEED, "chapters": []}
    nsent = sum(len(split_sentences(b["vo"])) for c in chapters for b in c["beats"])
    done = 0
    for ch in chapters:
        c = {"no": ch["no"], "id": ch["id"], "title": ch["title"], "start": snap(t), "beats": []}
        if ch["no"] > 0:
            c["title_card"] = [snap(t), snap(t + TITLE)]
            t = snap(t + TITLE)
        for b in ch["beats"]:
            bt = {"id": b["id"], "name": b["name"], "start": snap(t), "sentences": [], "cues": {}}
            t = t + LEAD
            sents = split_sentences(b["vo"])
            for si, (stext, extra) in enumerate(sents):
                toks = tokens_with_cues(stext)
                display = " ".join(x["w"] for x in toks)
                say = spoken(display)
                audio, sp = paced(say)
                d = len(audio) / SR
                wt = word_times(toks, audio, lang)
                s0 = t
                words = []
                for tok, (w0, w1) in zip(toks, wt):
                    words.append({"w": tok["w"], "s": round(s0 + w0, 3), "e": round(s0 + w1, 3)})
                    for cname in tok["cues"]:
                        bt["cues"][cname] = round(s0 + w0, 3)
                    for cname in tok.get("cues_end", []):
                        bt["cues"][cname] = round(s0 + w1, 3)
                bt["sentences"].append({"text": display, "start": round(s0, 3), "end": round(s0 + d, 3),
                                        "speed": sp, "words": words})
                track.append((s0, audio))
                t = s0 + d + (GAP if si < len(sents) - 1 else 0.0) + extra
                done += 1
                if done % 20 == 0:
                    print(f"  {done}/{nsent} sentences", flush=True)
            bt["vo_end"] = round(t, 3)
            t = snap(t + TAIL + b["hold"])
            bt["end"] = t
            c["beats"].append(bt)
        c["end"] = snap(t)
        out["chapters"].append(c)
    out["duration"] = snap(t + 1.0)
    # narration track
    os.makedirs(AUDIO, exist_ok=True)
    n = int(out["duration"] * SR) + SR
    mix = np.zeros(n, dtype=np.float32)
    for s0, a in track:
        i = int(round(s0 * SR))
        mix[i:i + len(a)] += a[: max(0, n - i)]
    with wave.open(os.path.join(AUDIO, "narration.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    os.makedirs(os.path.dirname(OUT_TL), exist_ok=True)
    with open(OUT_TL, "w") as f:
        json.dump(out, f, indent=1)
    words = sum(len(s["words"]) for c in out["chapters"] for b in c["beats"] for s in b["sentences"])
    print(f"timeline: {out['duration']:.1f} s ({out['duration']/60:.1f} min), {words} words, "
          f"{words / (sum(len(a) for _, a in track) / SR) * 60:.0f} wpm while speaking")
    for c in out["chapters"]:
        print(f"  ch{c['no']:>2} {c['title']:<40} {c['start']:7.1f} - {c['end']:7.1f}  ({(c['end']-c['start'])/60:4.1f} min)")


def main():
    global VOICE
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--voice")
    ap.add_argument("--say", help="synthesise one line to build/audio/say.wav (pronunciation check)")
    a = ap.parse_args()
    if a.voice:
        VOICE = a.voice
    if a.fetch:
        fetch_model()
        return
    if a.say:
        audio, sp = paced(spoken(a.say))
        os.makedirs(AUDIO, exist_ok=True)
        with wave.open(os.path.join(AUDIO, "say.wav"), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((audio * 32767).astype(np.int16).tobytes())
        print(spoken(a.say), f"-> {len(audio)/SR:.2f} s at speed {sp}")
        return
    build(a)


if __name__ == "__main__":
    main()
