# The Hole That Fights Back

A 30-minute, Veritasium-style explainer on the technical life of an offshore **exploration well**
(spud → discovery evaluation → permanent abandonment), written for an MSc mechanical engineer starting an
exploration-drilling rotation on the **Norwegian Continental Shelf**. Everything (narration, shot list,
Blender animations, audio, subtitles, final export) is generated from this repo.

> **Accuracy over polish.** Simplifications are tagged `[SIM]`, Norway-specific material `[NO]` vs general
> industry practice `[GEN]`, and claims I could not confirm against a primary source `[VERIFY]`
> (see [`script/FLAGS.md`](script/FLAGS.md): 69 flagged items). **The Norwegian primary sources (NORSOK D-010,
> Havtil/Sodir regulations) were unreachable from the build sandbox**, so every NORSOK/regulation statement
> is from search summaries or memory, and no clause number, plug length, test pressure or barrier count from
> D-010 is quoted as fact. Read the standard before relying on any `[NO]` item.

## What's in the box

| Output | Where | Notes |
|---|---|---|
| Final video, 1080p24, subtitles burned in | `build/the_hole_that_fights_back_1080p.mp4` | 30:00, H.264 + AAC, -16 LUFS |
| Same, no burned-in subtitles | `build/..._1080p_nosubs.mp4` | video stream-copied |
| Subtitles | `build/the_hole_that_fights_back_1080p.srt` | 365 cues, timed to the narration |
| Narration script + shot list (timestamped) | `script/NARRATION.md` | 72 beats, 3,905 words |
| Flagged claims ledger | `script/FLAGS.md` | `VERIFY` / `SEEN` / `SIM` |
| Research outline + sources register | `script/00_outline.md`, `script/00_sources.md` | Stage 1 record |

`build/`, `renders/` and `audio/*.wav` are git-ignored (large and reproducible: `make final`).

## The five stages

| Stage | Deliverable | Where |
|---|---|---|
| 1 | Research outline, chapter timings (sum 30:00), sources/standards | `script/00_outline.md`, `00_sources.md` |
| 2 | Narration + shot list per beat, term-first-use lint, glossary | `script/chNN_*.md`, `glossary.yaml`, `scriptlib.py` |
| 3 | Blender (`bpy`, headless) scene modules + shared style | `scenes/` |
| 4 | Low-res preview + fast style QA (contact sheets) | `make qa`, `make preview CH=n` |
| 5 | TTS narration, subtitles, ffmpeg assembly, 1080p export | `audio/`, `scenes/assemble.py` |

## Reproduce

```sh
make venv        # .venv with bpy 4.5 LTS, numpy, matplotlib, Pillow, PyYAML (~1 GB)
sudo apt install ffmpeg xvfb libttspico-utils   # (and espeak-ng as a fallback voice)
make doctor      # what is installed / missing
make final       # script -> audio -> subs -> 1080p render -> assemble   (render step: ~1.5 h on 4 CPU cores)
```

Individual steps: `make script`, `make audio`, `make subs`, `make qa`, `make preview CH=1`, `make render`, `make assemble`.
No GPU or Blender binary is needed: the pip `bpy` module renders headless under `xvfb-run` (software GL).

## How it works

* **One well model.** `scenes/common/well_model.py` defines a single *illustrative composite* North Sea wildcat
  (300 m water, TD 4,200 m, overpressured Jurassic sandstone target) and *computes* its casing programme with
  the bottom-up algorithm shown in Chapter 1 (30″@390 m, 20″@1,000 m, 13⅜″@2,000 m, 9⅝″@3,400 m, 8½″ to TD).
  Charts, animations and narration numbers all read from it, so they cannot disagree. `scenes/common/logs.py` generates
  synthetic logs and applies Archie, cutoffs and gradient intersection to them (the free-water level on screen is
  *computed* from fitted pressure gradients).
* **Script as data.** Each beat has `VO`, `SHOT`, `FLAGS`, `TERMS`. `make script` fits durations to the 30:00 budget, lints
  pacing, enforces that **every glossary term is defined in the beat where it first appears**, and emits `timeline.json`.
* **Animations that explain.** Flat technical-illustration style (Blender Workbench, orthographic, outlined), driven by the
  narration: scenes key off the *measured* start of each spoken sentence. The five required mechanisms:
  mud-weight window + casing telescoping (`ch01`), BOP closing (`ch03`), cement displacement in an eccentric annulus
  (`ch06`), kick propagating up the annulus with Boyle's-law growth (`ch07`), plug placement (`ch09`).
* **Render budget.** Only frames where something changes are rendered (`Stage.plan_frames`); holds are encoded as durations.
* **Audio.** Placeholder voice = SVOX Pico (offline). Each sentence is synthesised, measured, fitted into its beat with one
  tempo factor, and placed on a 30:00 master track; the same timings drive subtitles and animation sync.

## Decisions taken (you said "finish on your own", so these are the defaults I recommended in Stage 1)

| | Decision |
|---|---|
| D1 style | Flat technical illustration in Workbench (Cycles ≈ 170 h here; infeasible). No photoreal 3D, no EEVEE hero shots. |
| D2 example | Fictional composite wildcat (invented numbers, real physics), flagged on screen and in the end card. |
| D3 voice | Offline placeholder (Pico en-GB). **Replace with a real recording** by dropping in `audio/narration.wav`, then `make subs assemble`. |
| D4 render | Rendered in the cloud sandbox at 5 AA samples (visually identical to 8, 40 % faster). |
| D5 sources | Hosts stayed blocked; nothing from NORSOK/regulations is verified against the primary text. |
| D6 incident | Physics-puzzle hook; one incident (Macondo 2010) in Ch 7, facts cross-checked against CSB/OGJ/IADC search results. |
| D7 units | bar / sg / m, casing sizes in inches. |

## Known limitations (honest list)

* The voice is robotic (offline TTS). Subtitles carry the content; a human voice-over is the biggest quality upgrade available.
* Visuals are schematic 2-D cutaways, not CFD or 3-D renders: the cement displacement, kick expansion and bubble sizes are
  simple models (documented as `[SIM]` in the script), not simulations.
* `[VERIFY]` claims (barrier counts per source in P&A, BOP test rules, riserless-top-hole barrier treatment, DST frequency on the
  NCS, "a few hundredths" HPHT window width, common-barrier-element wording, ...) need checking against the primary documents.
* Equinor internal requirements (TR/WR series) are not public and are not used.

## Layout

```
script/    narration chapters (chNN_*.md), glossary, scriptlib (lint/fit/emit), generated NARRATION/FLAGS/timeline
scenes/    common/{palette,stage,chart,shapes,furniture,timeline,well_model,logs}.py, chNN_*.py, render.py,
           assemble.py, contact_sheet.py
audio/     build_audio.py (TTS fit), subtitles.py  (generated wav/json are git-ignored)
renders/   frame output (git-ignored)      build/  final mp4 + srt (git-ignored)      sources/  your PDFs (git-ignored)
Makefile   all entry points                requirements.txt
```
