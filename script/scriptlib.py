#!/usr/bin/env python3
"""Parse, fit, lint and emit the narration script.

Chapter sources: script/chNN_*.md. Format (one beat per `##` block):

    # Ch 1: Title
    BUDGET: 240                      # seconds for the whole chapter

    ## 1.03 | 18 | anim              # id | duration s (rewritten by `fit`) | anim|still
    VO: narration text (may wrap over several lines)
    SHOT: what is on screen
    FLAGS: GEN | NO ; SIM: text ; VERIFY: text ; SEEN: text
    TERMS: glossary key; glossary key   # terms DEFINED in this beat's VO
    PAUSE: 3                         # optional trailing silence inside the beat, seconds

Commands:
    fit    rewrite beat durations so every chapter hits its BUDGET (pacing-proportional)
    lint   hard checks (budget sum, pacing, term-first-use, required fields); exit 1 on error
    build  fit + lint + write script/NARRATION.md, script/FLAGS.md, script/timeline.json
"""
from __future__ import annotations
import glob
import json
import math
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TOTAL_BUDGET = 1800
LEAD, TAIL = 0.4, 0.3            # silence before/after VO inside a beat, seconds
TTS_WPS = 2.70                   # SVOX Pico measured ~162 wpm
MAX_SPEEDUP = 1.15               # audio is fitted by atempo within [0.85, 1.15]
PACE_WPS = 2.35                  # narration pace used when distributing slack (≈ 141 wpm)
FIELD_RE = re.compile(r"^(VO|SHOT|FLAGS|TERMS|PAUSE):\s*(.*)$")
BEAT_RE = re.compile(r"^##\s+(\d+\.\d+)\s*\|\s*([\d.]+|auto)\s*\|\s*(anim|still)\s*$")


def words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-/.,]*", text.replace("—", " ")))


def parse_flags(raw: str):
    out = {"scope": [], "SIM": [], "VERIFY": [], "SEEN": []}
    # split only where a new flag keyword follows, so notes may contain their own semicolons
    parts = re.split(r";\s*(?=(?:NO|GEN)\s*(?:;|$)|(?:SIM|VERIFY|SEEN)\s*:)", raw.strip().rstrip(";"))
    for tok in [t.strip().rstrip(";").strip() for t in parts if t.strip()]:
        m = re.match(r"^(SIM|VERIFY|SEEN)\s*:\s*(.*)$", tok)
        if m:
            out[m.group(1)].append(m.group(2).strip())
        elif tok in ("NO", "GEN"):
            out["scope"].append(tok)
        else:
            raise ValueError(f"unknown flag token {tok!r}")
    return out


def load_chapters():
    chapters = []
    for path in sorted(glob.glob(os.path.join(HERE, "ch[0-9][0-9]_*.md"))):
        lines = open(path, encoding="utf-8").read().split("\n")
        ch = {"path": path, "title": "", "num": None, "budget": None, "beats": []}
        cur, field = None, None
        for ln in lines:
            m = re.match(r"^#\s+Ch\s+(\d+):\s*(.*)$", ln)
            if m:
                ch["num"], ch["title"] = int(m.group(1)), m.group(2).strip()
                continue
            m = re.match(r"^BUDGET:\s*(\d+)", ln)
            if m and cur is None:
                ch["budget"] = int(m.group(1))
                continue
            m = BEAT_RE.match(ln)
            if m:
                cur = {"id": m.group(1), "dur": m.group(2), "kind": m.group(3),
                       "vo": "", "shot": "", "flags_raw": "", "terms_raw": "", "pause": 0.0}
                ch["beats"].append(cur)
                field = None
                continue
            if cur is None:
                continue
            m = FIELD_RE.match(ln)
            if m:
                field = m.group(1)
                val = m.group(2)
                key = {"VO": "vo", "SHOT": "shot", "FLAGS": "flags_raw", "TERMS": "terms_raw", "PAUSE": "pause"}[field]
                cur[key] = float(val) if field == "PAUSE" and val.strip() else (0.0 if field == "PAUSE" else val)
                continue
            if field and field != "PAUSE" and ln.strip():
                key = {"VO": "vo", "SHOT": "shot", "FLAGS": "flags_raw", "TERMS": "terms_raw"}[field]
                cur[key] += " " + ln.strip()
        for b in ch["beats"]:
            b["vo"] = b["vo"].strip()
            b["terms"] = [t.strip() for t in b["terms_raw"].split(";") if t.strip()]
            b["flags"] = parse_flags(b["flags_raw"]) if b["flags_raw"].strip() else None
            b["words"] = words(b["vo"])
        chapters.append(ch)
    chapters.sort(key=lambda c: c["num"])
    return chapters


def min_dur(b) -> float:
    if not b["words"]:
        return 3.0 + b["pause"]
    return b["words"] / PACE_WPS + LEAD + TAIL + b["pause"]


def hard_min(b) -> float:
    """Shortest duration the TTS can physically fit (max speed-up)."""
    if not b["words"]:
        return 3.0 + b["pause"]
    return b["words"] / TTS_WPS / MAX_SPEEDUP + LEAD + TAIL + b["pause"]


def fit(chapters) -> list[str]:
    msgs = []
    for ch in chapters:
        mins = [min_dur(b) for b in ch["beats"]]
        total_min = sum(mins)
        budget = ch["budget"]
        if total_min > budget:
            hard = sum(hard_min(b) for b in ch["beats"])
            msgs.append(f"Ch {ch['num']}: natural pace needs {total_min:.1f}s > budget {budget}s "
                        f"(hard floor {hard:.1f}s) -> trim ~{(total_min-budget)*PACE_WPS:.0f} words")
            if hard > budget:
                continue
            # compress: scale between hard floor and natural pace
            floors = [hard_min(b) for b in ch["beats"]]
            t = (budget - sum(floors)) / (total_min - sum(floors))
            durs = [f + t * (m - f) for f, m in zip(floors, mins)]
        else:
            slack = budget - total_min
            durs = [m + slack * m / total_min for m in mins]
        # round to 0.5 s, then repair the sum on the longest beat
        durs = [round(d * 2) / 2 for d in durs]
        durs[max(range(len(durs)), key=lambda i: durs[i])] += budget - sum(durs)
        for b, d in zip(ch["beats"], durs):
            b["dur"] = d
    return msgs


def write_durations(chapters):
    for ch in chapters:
        text = open(ch["path"], encoding="utf-8").read().split("\n")
        by_id = {b["id"]: b for b in ch["beats"]}
        for i, ln in enumerate(text):
            m = BEAT_RE.match(ln)
            if m:
                b = by_id[m.group(1)]
                d = b["dur"]
                d_txt = f"{d:g}" if isinstance(d, (int, float)) else str(d)
                text[i] = f"## {b['id']} | {d_txt} | {b['kind']}"
        open(ch["path"], "w", encoding="utf-8").write("\n".join(text))


def load_glossary():
    g = yaml.safe_load(open(os.path.join(HERE, "glossary.yaml"), encoding="utf-8"))
    for key, v in g.items():
        v["aliases"] = [a.lower() for a in ([key] + v.get("aliases", []))]
    return g


def alias_regex(aliases):
    alts = sorted({re.escape(a) for a in aliases}, key=len, reverse=True)
    return re.compile(r"(?<![A-Za-z0-9])(?:" + "|".join(alts) + r")(?![A-Za-z0-9])", re.I)


def lint(chapters) -> tuple[list[str], list[str]]:
    errors, warns = [], []
    gloss = load_glossary()
    seen_defined = set()
    t_abs = 0.0
    for ch in chapters:
        if ch["budget"] is None:
            errors.append(f"Ch {ch['num']}: missing BUDGET")
            continue
        tot = sum(float(b["dur"]) for b in ch["beats"] if b["dur"] != "auto")
        if abs(tot - ch["budget"]) > 0.01:
            errors.append(f"Ch {ch['num']}: durations sum {tot:g}s != BUDGET {ch['budget']}s (run `fit`)")
        for b in ch["beats"]:
            if b["dur"] == "auto":
                errors.append(f"{b['id']}: duration is 'auto' (run `fit`)")
                continue
            d = float(b["dur"])
            if not b["shot"].strip():
                errors.append(f"{b['id']}: missing SHOT")
            if b["flags"] is None:
                errors.append(f"{b['id']}: missing FLAGS")
            if b["words"]:
                window = d - LEAD - TAIL - b["pause"]
                need = b["words"] / TTS_WPS
                if need > window * MAX_SPEEDUP + 1e-6:
                    errors.append(f"{b['id']}: VO too long: {b['words']} words need {need:.1f}s, window {window:.1f}s")
                elif b["words"] / max(window, 0.1) > 2.75:
                    warns.append(f"{b['id']}: brisk pace {b['words']/window:.2f} w/s ({b['words']} words in {window:.1f}s)")
            # term-first-use: terms listed must appear in VO; first appearance of any glossary term must be a defining beat
            for t in b["terms"]:
                if t not in gloss:
                    errors.append(f"{b['id']}: TERMS entry {t!r} not in glossary.yaml")
                elif not alias_regex(gloss[t]["aliases"]).search(b["vo"]):
                    errors.append(f"{b['id']}: TERMS entry {t!r} does not appear in this beat's VO")
                if t in seen_defined:
                    warns.append(f"{b['id']}: term {t!r} defined again (already defined earlier)")
            for key, v in gloss.items():
                if key in seen_defined or key in b["terms"]:
                    continue
                if alias_regex(v["aliases"]).search(b["vo"]):
                    errors.append(f"{b['id']}: term {key!r} used before it is defined (add to TERMS here or move definition earlier)")
            seen_defined.update(b["terms"])
            b["start"] = t_abs
            t_abs += d
    unused = [k for k in gloss if k not in seen_defined]
    for k in unused:
        warns.append(f"glossary term {k!r} is never defined in a beat")
    if abs(t_abs - TOTAL_BUDGET) > 0.01:
        errors.append(f"total runtime {t_abs:g}s != {TOTAL_BUDGET}s")
    return errors, warns


def tc(sec: float) -> str:
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


def emit(chapters):
    gloss = load_glossary()
    t = 0.0
    timeline = {"total": TOTAL_BUDGET, "chapters": []}
    narr = ["# Narration script and shot list (generated: do not edit; edit `chNN_*.md` and run `make script`)", "",
            f"Runtime {tc(TOTAL_BUDGET)} · tags: **[NO]** Norway-specific · **[GEN]** general industry · "
            "**[SIM]** deliberate simplification · **[VERIFY]** not confirmed against a primary source · "
            "**[SEEN]** seen only in a secondary/web source", ""]
    flags_rows = []
    total_words = 0
    for ch in chapters:
        cstart = t
        narr += [f"## Ch {ch['num']}: {ch['title']}  ({tc(cstart)}–{tc(cstart + ch['budget'])})", ""]
        tl_ch = {"num": ch["num"], "title": ch["title"], "start": cstart, "dur": ch["budget"], "beats": []}
        for b in ch["beats"]:
            d = float(b["dur"])
            fl = b["flags"]
            tags = " ".join(f"**[{s}]**" for s in fl["scope"])
            if fl["SIM"]:
                tags += " **[SIM]**"
            if fl["VERIFY"]:
                tags += " **[VERIFY]**"
            if fl["SEEN"]:
                tags += " **[SEEN]**"
            narr += [f"### {b['id']} · {tc(t)} · {d:g}s · {b['kind']} {tags}", ""]
            narr += [f"**VO:** {b['vo']}" if b["vo"] else "**VO:** *(none: visual only)*", "",
                     f"**SHOT:** {b['shot']}", ""]
            if b["terms"]:
                narr += ["**Terms introduced:** " + "; ".join(b["terms"]), ""]
            for kind in ("SIM", "VERIFY", "SEEN"):
                for txt in fl[kind]:
                    narr.append(f"- **{kind}:** {txt}")
                    flags_rows.append((b["id"], kind, txt, b["vo"][:90]))
            if any(fl[k] for k in ("SIM", "VERIFY", "SEEN")):
                narr.append("")
            total_words += b["words"]
            tl_ch["beats"].append({
                "id": b["id"], "start": t, "dur": d, "kind": b["kind"], "vo": b["vo"], "shot": b["shot"],
                "pause": b["pause"], "scope": fl["scope"], "sim": fl["SIM"], "verify": fl["VERIFY"],
                "terms": [{"term": k, "def": gloss[k]["def"]} for k in b["terms"]],
            })
            t += d
        timeline["chapters"].append(tl_ch)
    narr.append(f"*Total narration: {total_words} words ≈ {total_words / (TOTAL_BUDGET / 60):.0f} wpm averaged over the runtime.*")
    open(os.path.join(HERE, "NARRATION.md"), "w", encoding="utf-8").write("\n".join(narr) + "\n")
    json.dump(timeline, open(os.path.join(HERE, "timeline.json"), "w"), indent=1)
    # flags ledger
    order = {"VERIFY": 0, "SEEN": 1, "SIM": 2}
    flags_rows.sort(key=lambda r: (order[r[1]], r[0]))
    fl_md = ["# Flagged claims ledger (generated)", "",
             "**VERIFY** = in the narration but not confirmed against a primary source (read the cited document before publishing).  ",
             "**SEEN** = confirmed only in a secondary/web source.  **SIM** = deliberate simplification.", "",
             "| Beat | Kind | Claim / note | VO excerpt |", "|---|---|---|---|"]
    for bid, kind, txt, vo in flags_rows:
        fl_md.append(f"| {bid} | {kind} | {txt.replace('|', '/')} | {vo.replace('|', '/')}… |")
    open(os.path.join(HERE, "FLAGS.md"), "w", encoding="utf-8").write("\n".join(fl_md) + "\n")
    return total_words, len(flags_rows)


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "build"
    chapters = load_chapters()
    if cmd in ("fit", "build"):
        for m in fit(chapters):
            print("FIT:", m)
        write_durations(chapters)
        chapters = load_chapters()
    errors, warns = lint(chapters)
    for w in warns:
        print("WARN:", w)
    for e in errors:
        print("ERROR:", e)
    if errors:
        print(f"{len(errors)} error(s)")
        return 1
    if cmd == "build":
        nwords, nflags = emit(chapters)
        print(f"built: {len(chapters)} chapters, {sum(len(c['beats']) for c in chapters)} beats, {nwords} words, {nflags} flags")
    else:
        print("lint ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
