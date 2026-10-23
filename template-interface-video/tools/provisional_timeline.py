#!/usr/bin/env python3
"""Write a provisional src/data/timeline.json from script word counts (155 wpm) so scenes can be developed
before the voice is synthesised. tools/tts.py overwrites it with the real, voice-timed timeline."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import tts  # noqa: E402

WPS = 155 / 60


def main():
    chapters = tts.parse_script()
    t = 0.0
    out = {"fps": 30, "voice": "provisional", "chapters": [], "provisional": True}
    for ch in chapters:
        c = {"no": ch["no"], "id": ch["id"], "title": ch["title"], "start": tts.snap(t), "beats": []}
        if ch["no"] > 0:
            c["title_card"] = [tts.snap(t), tts.snap(t + tts.TITLE)]
            t += tts.TITLE
        for b in ch["beats"]:
            bt = {"id": b["id"], "name": b["name"], "start": tts.snap(t), "sentences": [], "cues": {}}
            t += tts.LEAD
            sents = tts.split_sentences(b["vo"])
            for si, (stext, extra) in enumerate(sents):
                toks = tts.tokens_with_cues(stext)
                words = []
                for tok in toks:
                    d = max(0.18, len(tok["w"]) * 0.062)
                    words.append({"w": tok["w"], "s": round(t, 3), "e": round(t + d, 3)})
                    for cn in tok["cues"]:
                        bt["cues"][cn] = round(t, 3)
                    t += d + 0.04
                bt["sentences"].append({"text": " ".join(x["w"] for x in toks), "start": words[0]["s"], "end": round(t, 3), "words": words})
                t += (tts.GAP if si < len(sents) - 1 else 0) + extra
            bt["vo_end"] = round(t, 3)
            t = tts.snap(t + tts.TAIL + b["hold"])
            bt["end"] = t
            c["beats"].append(bt)
        c["end"] = tts.snap(t)
        out["chapters"].append(c)
    out["duration"] = tts.snap(t + 1)
    with open(tts.OUT_TL, "w") as f:
        json.dump(out, f, indent=1)
    print(f"provisional timeline {out['duration']/60:.1f} min")


if __name__ == "__main__":
    main()
