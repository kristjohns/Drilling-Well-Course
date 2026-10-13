"""Synthesize all narration segments and build the timeline.

Outputs (in build/audio):
  seg/<scene>__<nn>_<cue>.wav   per-segment narration (24 kHz mono)
  timeline.json                 per scene: duration, cues {name: [start, end]}, sentences
  phonemes.txt                  phoneme log for review
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import tts  # noqa: E402

VOICE = os.environ.get("VOICE", "af_heart")
SPEED = float(os.environ.get("SPEED", "0.94"))
FPS = 30
SEG_GAP = 0.70          # silence between segments
SCENE_TAIL = 0.6        # extra air at scene end
OUT = os.path.join(ROOT, "build", "audio")


def load_script():
    spec = importlib.util.spec_from_file_location("narration", os.path.join(ROOT, "script", "narration.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.SCENES


def main(only: set[str] | None = None):
    os.makedirs(os.path.join(OUT, "seg"), exist_ok=True)
    cache_dir = os.path.join(ROOT, "build", "tts_cache")
    os.makedirs(cache_dir, exist_ok=True)
    k = tts.Kokoro()
    voice = tts.load_voice(VOICE)
    timeline = {}
    tl_path = os.path.join(OUT, "timeline.json")
    if os.path.exists(tl_path):
        timeline = json.load(open(tl_path))
    plog = []
    for sc in load_script():
        if only and sc["id"] not in only:
            continue
        t = 0.0
        cues = {}
        sentences = []
        files = []
        for i, (cue, text) in enumerate(sc["segments"]):
            if cue == "@pause":
                t += float(text)
                continue
            ph_key = "|".join(tts.phonemize(x) for x in tts.split_sentences(text))
            key = hashlib.sha1(f"{VOICE}|{SPEED}|{ph_key}".encode()).hexdigest()[:16]
            cpath = os.path.join(cache_dir, key + ".npz")
            if os.path.exists(cpath):
                z = np.load(cpath, allow_pickle=True)
                audio, sent_durs, phon = z["audio"], list(z["sent_durs"]), list(z["phon"])
            else:
                parts = []
                sent_durs = []
                phon = []
                for sent in tts.split_sentences(text):
                    a, ph = tts.synth_text(k, sent, voice, SPEED)
                    parts.append(a)
                    sent_durs.append(len(a) / tts.SAMPLE_RATE)
                    phon += ph
                    parts.append(np.zeros(int(0.30 * tts.SAMPLE_RATE), np.float32))
                parts.pop()
                audio = np.concatenate(parts)
                np.savez(cpath, audio=audio, sent_durs=np.array(sent_durs), phon=np.array(phon, dtype=object))
            dur = len(audio) / tts.SAMPLE_RATE
            fn = f"{sc['id']}__{i:02d}_{cue}.wav"
            sf.write(os.path.join(OUT, "seg", fn), audio, tts.SAMPLE_RATE, subtype="PCM_16")
            cues[cue] = [round(t, 3), round(t + dur, 3)]
            # sentence timings for subtitles
            st = t
            for s_text, sd in zip(tts.split_sentences(text), sent_durs):
                clean = s_text
                import re
                clean = re.sub(r"\{[A-Z]+\}", "", clean)
                clean = re.sub(r"\[([^\]]+)\]\(/[^)]*\)", r"\1", clean)
                sentences.append([round(st, 3), round(st + float(sd), 3), clean])
                st += float(sd) + 0.30
            files.append([fn, round(t, 3)])
            plog.append(f"[{sc['id']}:{cue}] {text}\n    " + "\n    ".join(phon))
            t += dur + SEG_GAP
        t += SCENE_TAIL
        # whole number of video frames, so concatenated scenes stay in sync with the audio
        t = round(t * FPS) / FPS
        timeline[sc["id"]] = dict(duration=round(t, 4), cues=cues, sentences=sentences, files=files,
                                  title=sc["title"], chapter=sc["chapter"])
        print(f"{sc['id']}: {t:7.2f} s  ({len(cues)} segments)", flush=True)
    json.dump(timeline, open(tl_path, "w"), indent=1, ensure_ascii=False)
    with open(os.path.join(OUT, "phonemes.txt"), "w") as f:
        f.write("\n".join(plog))
    total = sum(v["duration"] for v in timeline.values())
    print(f"TOTAL {total:.1f} s = {total/60:.2f} min")


if __name__ == "__main__":
    main(set(sys.argv[1:]) or None)
