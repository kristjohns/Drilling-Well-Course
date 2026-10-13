"""Offline narration synthesis with Kokoro-82M (fp32 ONNX) and misaki G2P.

misaki normally needs a spaCy statistical model for tokenising and POS tags.
That model is not reachable from this environment, so we use spaCy's blank
English tokenizer plus a small rule tagger. Words whose pronunciation depends
on part of speech can be forced inline with ``word{VB}`` / ``word{NN}`` /
``word{JJ}`` markup, and any word can be given explicit phonemes with
misaki's ``[word](/phonemes/)`` syntax.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

import numpy as np
import onnxruntime as ort
import spacy
from misaki import en, espeak
from misaki.en import MToken

KOKORO_DIR = os.environ.get("KOKORO_DIR", "/home/user/tools/kokoro")
MODEL_PATH = os.path.join(KOKORO_DIR, "kokoro-v1.0-fp32.onnx")
VOICE_DIR = os.path.join(KOKORO_DIR, "kokoro-local-runtime/package/voices")
SAMPLE_RATE = 24000

# Pronunciations for names, acronyms and jargon (misaki US phoneme alphabet).
PRON = {
    "NORSOK": "nˈɔɹsɑk",
    "Havtil": "hˈɑvtˌil",
    "Ptil": "pˈitˌil",
    "MAASP": "mˈɑsp",
    "Equinor": "ˈɛkwɪnˌɔɹ",
    "Statoil": "stˈætˌɔɪl",
    "Statfjord": "stˈɑtfjˌɔɹd",
    "Gullfaks": "ɡˈʊlfˌɑks",
    "Snorre": "snˈɔɹə",
    "Snorre A": "snˈɔɹə ˈA",
    "Troll": "tɹˈɔl",
    "Valhall": "vˈɑlhˌɑl",
    "Ekofisk": "ˈɛkOfˌɪsk",
    "Sleipner": "slˈIpnəɹ",
    "Bollsta": "bˈɔlstə",
    "Norge": "nˈɔɹɡə",
    "SINTEF": "sˈɪntˌɛf",
    "SWIPA": "swˈipə",
    "Hydrawell": "hˈIdɹəwˌɛl",
    "Reflekt": "ɹəflˈɛkt",
    "Aurora": "əɹˈɔɹə",
    "Longship": "lˈɔŋʃˌɪp",
    "caprock": "kˈæpɹˌɑk",
    "Aker": "ˈɑkəɹ",
    "Valhall's": "vˈɑlhˌɑlz",
    "Heidrun": "hˈIdɹʊn",
    "Norne": "nˈɔɹnə",
    "Oseberg": "ˈusəbˌɛɹɡ",
    "ISO": "ˈIsO",
    "Q-21": "kjˈu twˈɛnti wˈʌn",
    "smectite": "smˈɛktˌIt",
    "thermite": "θˈɜɹmˌIt",
    "Aadnøy": "ˈɔdnˌɔɪ",
    "Vignes": "vˈiŋnəs",
    "Snøhvit": "snˈuvit",
    "Northern": "nˈɔɹðəɹn",
    "annuli": "ˈænjəlˌI",
    "inflow": "ˈɪnflˌO",
    "barite": "bˈɛɹˌIt",
    "overpressured": "ˌOvəɹpɹˈɛʃəɹd",
    "subsea": "sˈʌbsˌi",
    "workover": "wˈɜɹkˌOvəɹ",
    "wireline": "wˈIəɹlˌIn",
    "MPD": "ˌɛmpˌidˈi",
    "PWC": "pˌidˌʌbᵊljusˈi",
    "A-annulus": "ˈA ˈænjələs",
    "B-annulus": "bˈi ˈænjələs",
    "C-annulus": "sˈi ˈænjələs",
    "D-010": "dˈi zˈɪɹO tˈɛn",
    "CO2": "sˌiˌOtˈu",
    "Deepsea": "dˈipsˌi",
    "Macondo": "məkˈɑndO",
    "Havtil's": "hˈɑvtˌilz",
    "BOP": "bˌiˌOpˈi",
}

ESPEAK_FALLBACK = espeak.EspeakFallback(british=False)
_LEX = en.Lexicon(british=False)
_NLP = spacy.blank("en")
_TAG_RE = re.compile(r"(\S+?)\{(VB|VBD|VBN|VBP|VBZ|VBG|NN|NNS|JJ|RB|DT)\}")


def _rule_tag(tok: str, prev: str | None) -> str:
    if tok in (".", "?", "!"):
        return "."
    if tok == ",":
        return ","
    if tok in (";", ":", "—", "–", "…", "--"):
        return ":"
    if tok == "(":
        return "-LRB-"
    if tok == ")":
        return "-RRB-"
    if tok == "-":
        return "HYPH"
    if tok in ('"', "“"):
        return "``"
    if tok == "”":
        return "''"
    if re.fullmatch(r"[\d,.]+", tok) and any(c.isdigit() for c in tok):
        return "CD"
    if tok in ("a", "A", "an", "An", "the", "The"):
        return "DT"
    if tok in ("to", "To"):
        return "TO"
    if tok.isupper() and tok.isalpha() and len(tok) >= 2:
        return "NNP"
    if prev in ("to", "will", "must", "shall", "should", "can", "cannot", "may", "might", "could", "would"):
        return "VB"
    return "XX"


class G2P(en.G2P):
    """misaki G2P with a spaCy blank tokenizer and rule-based tags."""

    def __init__(self):  # noqa: D401 - intentionally bypass the spaCy model download
        self.british = False
        self.nlp = _NLP
        self.lexicon = _LEX
        self.fallback = ESPEAK_FALLBACK
        self.unk = ""
        self.forced_tags: dict[int, str] = {}

    def tokenize(self, text, tokens, features):
        doc = self.nlp(text)
        out = []
        prev = None
        for t in doc:
            tag = _rule_tag(t.text, prev)
            out.append(MToken(text=t.text, tag=tag, whitespace=t.whitespace_))
            prev = t.text.lower()
        # explicit phoneme features from [word](/ps/) markup
        if features:
            align = spacy.training.Alignment.from_strings(tokens, [t.text for t in out])
            for k, v in features.items():
                for i, j in enumerate(np.where(align.y2x.data == k)[0]):
                    if isinstance(v, str) and v.startswith("/"):
                        out[j].is_head = i == 0
                        out[j].phonemes = v.lstrip("/") if i == 0 else ""
                        out[j].rating = 5
                    elif not isinstance(v, str):
                        out[j].stress = v
        # forced tags: word index in whitespace tokens -> tag
        for t in out:
            pass
        return out


_G2P = G2P()


def preprocess_markup(text: str) -> str:
    """Convert word{TAG} markup and PRON dictionary words into misaki markup."""
    # Forced POS tags: we emulate by looking up the lexicon directly.
    def tag_sub(m):
        word, tag = m.group(1), m.group(2)
        core = re.match(r"^([A-Za-z'’-]+)(.*)$", word)
        if not core:
            return word
        w, tail = core.group(1), core.group(2)
        ps, _ = _LEX.get_word(w.lower(), tag, None, en.TokenContext())
        if ps is None:
            return word
        return f"[{w}](/{ps}/){tail}"

    text = _TAG_RE.sub(tag_sub, text)

    def pron_sub(m):
        w = m.group(0)
        return f"[{w}](/{PRON[w]}/)"

    keys = sorted(PRON.keys(), key=len, reverse=True)
    pat = r"(?<![\w\[/])(" + "|".join(re.escape(k) for k in keys) + r")(?![\w\]])"
    # avoid re-wrapping inside existing [..](/..../) blocks
    parts = re.split(r"(\[[^\]]*\]\(/[^)]*\))", text)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(pat, pron_sub, parts[i])
    return "".join(parts)


def phonemize(text: str) -> str:
    ps, tokens = _G2P(preprocess_markup(text))
    return ps


@dataclass
class Voice:
    name: str
    data: np.ndarray  # (510, 1, 256)


def load_voice(spec: str) -> Voice:
    """spec like 'af_heart' or 'af_heart:0.7,af_bella:0.3' (blend)."""
    parts = [p.split(":") for p in spec.split(",")]
    acc = None
    for p in parts:
        name = p[0]
        w = float(p[1]) if len(p) > 1 else 1.0
        arr = np.fromfile(os.path.join(VOICE_DIR, f"{name}.bin"), dtype=np.float32).reshape(-1, 1, 256)
        acc = arr * w if acc is None else acc + arr * w
    total = sum(float(p[1]) if len(p) > 1 else 1.0 for p in parts)
    return Voice(spec, acc / total)


class Kokoro:
    def __init__(self, model_path: str = MODEL_PATH, threads: int = 4):
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = threads
        opts.inter_op_num_threads = 1
        self.sess = ort.InferenceSession(model_path, opts, providers=["CPUExecutionProvider"])
        cfg = json.load(open(os.path.join(os.path.dirname(__import__("kokoro_onnx").__file__), "config.json")))
        self.vocab = cfg["vocab"]

    def tokens(self, phonemes: str) -> list[int]:
        return [self.vocab[c] for c in phonemes if c in self.vocab]

    def synth_phonemes(self, phonemes: str, voice: Voice, speed: float = 1.0) -> np.ndarray:
        toks = self.tokens(phonemes)
        assert len(toks) <= 510, f"too many tokens: {len(toks)}"
        style = voice.data[len(toks)]
        ids = np.array([[0, *toks, 0]], dtype=np.int64)
        out = self.sess.run(None, {"input_ids": ids, "style": style.astype(np.float32),
                                   "speed": np.array([speed], dtype=np.float32)})[0]
        return out.reshape(-1)


SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\[“\"])")


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENT_SPLIT.split(text.strip()) if s.strip()]


def trim_silence(x: np.ndarray, thresh_db: float = -45.0, pad: float = 0.03) -> np.ndarray:
    if x.size == 0:
        return x
    win = int(0.01 * SAMPLE_RATE)
    n = len(x) // win
    if n == 0:
        return x
    frames = x[: n * win].reshape(n, win)
    rms = np.sqrt((frames ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms / (np.abs(x).max() + 1e-9))
    idx = np.where(db > thresh_db)[0]
    if idx.size == 0:
        return x
    a = max(0, idx[0] * win - int(pad * SAMPLE_RATE))
    b = min(len(x), (idx[-1] + 1) * win + int(pad * SAMPLE_RATE))
    return x[a:b]


def synth_text(k: Kokoro, text: str, voice: Voice, speed: float = 1.0,
               sentence_gap: float = 0.28) -> tuple[np.ndarray, list[str]]:
    """Synthesize a paragraph sentence by sentence, joined with short pauses."""
    chunks = []
    phon_log = []
    for sent in split_sentences(text):
        ps = phonemize(sent)
        phon_log.append(ps)
        toks = k.tokens(ps)
        if len(toks) > 500:
            # split on commas / semicolons if a sentence is very long
            sub = re.split(r"(?<=[,;:—])\s+", sent)
            for s in sub:
                ps2 = phonemize(s)
                a = trim_silence(k.synth_phonemes(ps2, voice, speed))
                chunks.append(a)
                chunks.append(np.zeros(int(0.12 * SAMPLE_RATE), np.float32))
            chunks.pop()
        else:
            chunks.append(trim_silence(k.synth_phonemes(ps, voice, speed)))
        chunks.append(np.zeros(int(sentence_gap * SAMPLE_RATE), np.float32))
    if chunks:
        chunks.pop()
    audio = np.concatenate(chunks) if chunks else np.zeros(0, np.float32)
    return audio.astype(np.float32), phon_log


if __name__ == "__main__":
    import sys
    import soundfile as sf

    text = sys.argv[1]
    voice = sys.argv[2] if len(sys.argv) > 2 else "af_heart"
    out = sys.argv[3] if len(sys.argv) > 3 else "/tmp/tts_test.wav"
    k = Kokoro()
    audio, ph = synth_text(k, text, load_voice(voice))
    for p in ph:
        print(p)
    sf.write(out, audio, SAMPLE_RATE)
    print(out, len(audio) / SAMPLE_RATE, "s")
