#!/usr/bin/env python3
"""
Narration pipeline: script.json -> per-beat speech (Kokoro-82M via kokoro-onnx)
-> timeline (timings.json), one narration track (narration.wav) and captions.

Every beat (a sentence or two) is synthesised on its own so that the
animation can be cued to exact beat start times. Word times inside a beat are
estimated from phoneme counts and the pauses actually found in the audio.

Usage:
  python3 tools/tts.py                 # build everything (cached per beat)
  python3 tools/tts.py --force         # ignore the cache
  python3 tools/tts.py --only pmv      # (re)build just one scene's beats, keep the rest cached
  python3 tools/tts.py --voice bf_emma --speed 0.95
"""
import argparse, hashlib, json, os, re, sys, time
from pathlib import Path

import numpy as np
import soundfile as sf
from num2words import num2words

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src/data/script.json"
LEXICON = ROOT / "tools/lexicon.json"
OUT_DATA = ROOT / "src/data/timings.json"
BUILD = ROOT / "build"
CACHE = BUILD / "tts-cache"
MODEL_DIR = Path(os.environ.get("KOKORO_DIR", BUILD / "models"))
SR = 24000

PUNCT_PRE = "\"'(["
PUNCT_POST = ".,;:!?\")]"
PAUSE_MARKS = {",": 0.16, ";": 0.2, ":": 0.22, ".": 0.34, "?": 0.34, "!": 0.34}


def split_token(tok):
    pre = ""
    while tok and tok[0] in PUNCT_PRE:
        pre += tok[0]
        tok = tok[1:]
    post = ""
    while tok and tok[-1] in PUNCT_POST:
        post = tok[-1] + post
        tok = tok[:-1]
    return pre, tok, post


def spoken_for(core, lex):
    """Return (spoken text, ipa-or-None) for one display token (punctuation already removed)."""
    if core in lex["ipa"]:
        return core, lex["ipa"][core]
    if core in lex["text"]:
        return lex["text"][core], None
    m = re.fullmatch(r"\d{1,3}(?:,\d{3})+|\d+", core)
    if m:
        n = int(core.replace(",", ""))
        if 1100 <= n <= 2099:
            return num2words(n, to="year"), None
        return num2words(n), None
    return core.replace("-", " ") if re.search(r"[A-Za-z]-[A-Za-z]", core) else core, None


def tokenize_beat(text, lex):
    toks = []
    for raw in text.split():
        pre, core, post = split_token(raw)
        spoken, ipa = spoken_for(core, lex)
        toks.append(dict(raw=raw, pre=pre, core=core, post=post, spoken=spoken, ipa=ipa))
    return toks


def phonemize_beat(k, toks, lang):
    out, buf = [], []

    def flush():
        if buf:
            s = " ".join(buf).strip()
            if s:
                out.append(k.tokenizer.phonemize(s, lang))
            buf.clear()

    for t in toks:
        if t["ipa"]:
            flush()
            out.append(t["pre"] + t["ipa"] + t["post"])
        else:
            buf.append(t["pre"] + t["spoken"] + t["post"])
    flush()
    return " ".join(out)


def find_silences(audio, sr, thresh_db=-42.0, min_len=0.09):
    frame = int(0.01 * sr)
    n = len(audio) // frame
    if n == 0:
        return []
    rms = np.sqrt((audio[: n * frame].reshape(n, frame) ** 2).mean(1))
    peak = rms.max() + 1e-9
    quiet = rms < peak * 10 ** (thresh_db / 20)
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j + 1 < n and quiet[j + 1]:
                j += 1
            if (j - i + 1) * 0.01 >= min_len:
                runs.append((i * 0.01, (j + 1) * 0.01))
            i = j + 1
        else:
            i += 1
    return runs


def estimate_word_times(k, toks, audio, lang):
    """Per-token start/end times inside a beat.

    Phoneme-weighted distribution of the beat, anchored on the silences that are really
    in the audio (each silence is snapped to the token boundary the model predicts closest).
    """
    dur = len(audio) / SR
    n = len(toks)
    weights = []
    for t in toks:
        ph = t["ipa"] or k.tokenizer.phonemize(t["spoken"], lang)
        weights.append(max(1, len([c for c in ph if c not in " ˈˌː"])))
    pause_after = []
    for i, t in enumerate(toks):
        p = 0.0
        if i < n - 1 and t["post"]:
            p = max((PAUSE_MARKS.get(c, 0.0) for c in t["post"]), default=0.0)
        pause_after.append(p)

    def model(anchors):
        """anchors: sorted list of (boundary b, sil_start, sil_end); tokens [prev,b) end at sil_start."""
        times = [None] * n
        prev_i, prev_t = 0, 0.0
        for b, ss, se in anchors + [(n, dur, dur)]:
            idx = list(range(prev_i, b))
            if idx:
                internal = sum(pause_after[j] for j in idx[:-1])
                speech = max(0.05, (ss - prev_t) - internal)
                tw = sum(weights[j] for j in idx)
                t0 = prev_t
                for j in idx:
                    t1 = t0 + speech * weights[j] / tw
                    times[j] = (t0, t1)
                    t0 = t1 + (pause_after[j] if j != idx[-1] else 0.0)
            prev_i, prev_t = b, se
        return times

    sil = [s_ for s_ in find_silences(audio, SR, thresh_db=-38.0, min_len=0.11) if s_[0] > 0.12 and s_[1] < dur - 0.08]
    anchors = []
    for ss, se in sil:
        cur = model(anchors)
        lo = anchors[-1][0] + 1 if anchors else 1
        best, best_cost = None, 1e9
        for b in range(lo, n):
            e = cur[b - 1][1]
            cost = abs(e - ss) - (0.15 if toks[b - 1]["post"] else 0.0)
            if cost < best_cost:
                best, best_cost = b, cost
        if best is not None and best_cost < 0.6:
            anchors.append((best, ss, se))
    times = model(anchors)
    return [dict(w=t["raw"], s=round(a, 3), e=round(b, 3)) for t, (a, b) in zip(toks, times)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", help="scene id to (re)synthesise (others use cache)")
    ap.add_argument("--voice")
    ap.add_argument("--speed", type=float)
    args = ap.parse_args()

    script = json.loads(SCRIPT.read_text(encoding="utf-8"))
    lex = json.loads(LEXICON.read_text(encoding="utf-8"))
    meta = script["meta"]
    voice = args.voice or meta["voice"]
    speed = args.speed or meta["speed"]
    lang = meta.get("lang", "en-us")
    CACHE.mkdir(parents=True, exist_ok=True)

    from kokoro_onnx import Kokoro

    k = Kokoro(str(MODEL_DIR / "kokoro-v1.0.onnx"), str(MODEL_DIR / "voices-v1.0.bin"))
    vocab = k.tokenizer.vocab
    for w, ipa in lex["ipa"].items():
        bad = [c for c in ipa if c not in vocab]
        if bad:
            print(f"!! lexicon '{w}' has symbols outside the Kokoro vocab: {bad}")

    t_start = time.time()
    cursor = 0.0
    scenes_out = []
    chunks = []  # (start_sample, audio)
    n_new = 0
    for sc in script["scenes"]:
        s_start = cursor
        cursor += sc.get("lead", 0.4)
        beats_out = {}
        order = []
        for b in sc["beats"]:
            text = b.get("text", "")
            if text:
                toks = tokenize_beat(text, lex)
                ph = phonemize_beat(k, toks, lang)
                key = hashlib.sha1(f"{voice}|{speed}|{ph}|kokoro-v1.0".encode()).hexdigest()[:20]
                f = CACHE / f"{key}.npy"
                use_cache = f.exists() and not args.force and not (args.only == sc["id"])
                if use_cache:
                    audio = np.load(f)
                else:
                    audio, sr = k.create(ph, voice, speed=speed, lang=lang, is_phonemes=True, trim=True)
                    audio = audio.astype(np.float32)
                    # short fades to avoid clicks at the cuts
                    nf = int(0.006 * SR)
                    audio[:nf] *= np.linspace(0, 1, nf)
                    audio[-nf:] *= np.linspace(1, 0, nf)
                    np.save(f, audio)
                    n_new += 1
                dur = len(audio) / SR
                words = estimate_word_times(k, toks, audio, lang)
            else:
                audio = None
                dur = float(b.get("dur", 1.0))
                words = []
            start = cursor
            end = start + dur
            beats_out[b["id"]] = dict(
                id=b["id"], text=text, start=round(start, 3), end=round(end, 3),
                dur=round(dur, 3), words=words,
            )
            order.append(b["id"])
            if audio is not None:
                chunks.append((int(round(start * SR)), audio))
            cursor = end + b.get("post", 0.4)
        cursor += sc.get("tail", 0.5)
        scenes_out.append(
            dict(id=sc["id"], chapter=sc.get("chapter"), start=round(s_start, 3),
                 end=round(cursor, 3), order=order, beats=beats_out)
        )
        print(f"{sc['id']:10s} {s_start:7.1f} -> {cursor:7.1f}  ({cursor - s_start:5.1f}s)")

    total = cursor
    track = np.zeros(int(np.ceil(total * SR)) + SR, dtype=np.float32)
    for st, a in chunks:
        track[st : st + len(a)] += a
    BUILD.mkdir(exist_ok=True)
    sf.write(BUILD / "narration.wav", track, SR, subtype="FLOAT")
    OUT_DATA.write_text(
        json.dumps(dict(meta=dict(voice=voice, speed=speed, duration=round(total, 3), sr=SR),
                        scenes=scenes_out), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"\nTotal {total:.1f}s ({total/60:.1f} min); synthesised {n_new} new beats in {time.time()-t_start:.0f}s")
    print(f"voice={voice} speed={speed}")


if __name__ == "__main__":
    main()
