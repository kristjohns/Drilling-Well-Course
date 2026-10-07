# The Hole That Fights Back

A Veritasium-style explainer on the technical life of an offshore **exploration well**
(spud → discovery evaluation → permanent abandonment), written for an MSc mechanical engineer starting an
exploration-drilling rotation on the **Norwegian Continental Shelf**. Everything (narration, shot list,
animation, voice, music, subtitles, final export) is generated from this repo.

> **Accuracy over polish.** Simplifications are tagged `[SIM]`, Norway-specific material `[NO]` vs general
> industry practice `[GEN]`, and claims I could not confirm against a primary source `[VERIFY]`
> (see [`script/FLAGS.md`](script/FLAGS.md): 76 flagged items, 27 of them `VERIFY`). **The Norwegian primary sources
> (NORSOK D-010, Havtil/Sodir regulations) were unreachable from the build sandbox**, so every NORSOK/regulation
> statement is from search summaries or memory, and no clause number, plug length, test pressure or barrier count from
> D-010 is quoted as fact. Read the standard before relying on any `[NO]` item.

## What's in the box

| Output | Where | Notes |
|---|---|---|
| Final video, subtitles burned in | `build/the_hole_that_fights_back_1080p.mp4` | 36:42, 1920x1080 @ 30 fps, H.264 + AAC stereo, -16 LUFS (two-pass loudnorm) |
| Same, no burned-in subtitles | `build/..._1080p_nosubs.mp4` | video stream-copied |
| 720p copy in parts (< 29 MiB each, for sharing) | `build/..._720p_partN.mp4` | |
| Subtitles | `build/the_hole_that_fights_back_1080p.srt` | one cue per spoken sentence, timed to the voice |
| Narration script + shot list (real timestamps) | `script/NARRATION.md` | 11 chapters, 72 beats, 5,605 words |
| Flagged claims ledger | `script/FLAGS.md` | `VERIFY` / `SEEN` / `SIM` |
| Research outline + sources register | `script/00_outline.md`, `script/00_sources.md` | Stage 1 record |

`build/`, `renders/`, `audio/*.wav` and the voice model are git-ignored (large and reproducible: `make final`).

## Version 2 (October 2026): what changed

The first cut was reviewed beat by beat by drilling-engineering and motion-design reviewers (content, animation,
cross-chapter consistency, story). Every chapter was then rewritten and re-animated:

* **Voice.** The robotic offline TTS is replaced by **Kokoro-82M**, an open-weight (Apache-2.0) neural TTS model, run
  locally on the CPU with `kokoro-onnx` (voice `af_heart`). Each sentence is synthesised, measured and re-synthesised
  slower if it runs faster than 172 words per minute; the film's timeline then **follows the voice** (beats are as long
  as their narration needs), so pauses land where the script puts them (`[pause N]`).
* **Look.** The Blender Workbench renderer is replaced by a 2-D motion-graphics engine on Skia (`scenes/common/stage.py`,
  same scene API) with automatic styling by role (`look.py`): gradient backdrops, glass cards, metallic steel, textured
  rock, glowing curves that draw on with a travelling tip, particle flows for fluids, pills, counters, eased camera moves
  and dissolves at every beat. Term cards appear when a term is first *spoken*. Animation is keyed to the spoken words
  (`beat.word(i, "phrase")`), not to the beat start.
* **Sound.** A synthesised ambient music bed (ducked under the voice), a whoosh on chapter title cards and a tick when a
  term card appears (`audio/mix.py`; no samples, nothing licensed).
* **Content fixes** (selection): BOP stack order (wellhead connector, two pipe rams, blind shear rams, annular) and the
  shear sequence; consistent kill-sheet numbers (1.62 sg mud, ~18 bar SIDPP, ~1.67 sg kill mud vs ~1.71 sg at the shoe)
  and the driller's method as two circulations; the formation at the shoe as part of the secondary barrier; the linear
  part of a leak-off plot is the mud compressing; the bottom-up casing logic shows why kick allowance (not fracture
  alone) sets the 9⅝ in shoe; reservoir pressures, contacts and the free-water level anchored to one model, net-to-gross
  as net reservoir / gross (0.94); a DST needs a liner (our well skips the test); two permanent barriers for the
  overpressured sand in P&A and one plug list for every drawing; cement is always grey, verified plugs get a green outline.

## Reproduce

```sh
sudo apt install ffmpeg espeak-ng fonts-inter fonts-jetbrains-mono libegl1 libgl1 npm
make venv          # .venv: skia-python, kokoro-onnx, onnxruntime, numpy, Pillow, PyYAML
make doctor        # what is installed / missing
make voice-model   # Kokoro-82M weights + voices (~350 MB) from the npm registry, SHA-256 verified
make final         # script -> voice -> mix -> 1080p render -> assemble
```

Timing on 4 CPU cores: voice ~30 min (cached per sentence afterwards), mix ~2 min, render ~45 min (`JOBS=2`),
assembly ~25 min. Individual steps: `make script | audio | mix | qa | preview CH=n | render | assemble`.
To change one scene: edit `scenes/chNN_*.py`, check it with `python scenes/render.py --chapter N --qa --res 960x540`
(two stills per beat in `renders/qa/chNN/`), re-render that chapter, then `make assemble`.

## How it works

* **One well model.** `scenes/common/well_model.py` defines a single *illustrative composite* North Sea wildcat
  (300 m water, TD 4,200 m, overpressured Jurassic sandstone target) and *computes* its casing programme with
  the bottom-up algorithm shown in Chapter 1 (30 in @ 390 m, 20 in @ 1,000 m, 13⅜ in @ 2,000 m, 9⅝ in @ 3,400 m,
  8½ in open hole to TD). Charts, animations and narration numbers read from it, so they cannot disagree.
  `scenes/common/logs.py` generates synthetic logs and applies Archie, cutoffs and gradient intersection to them
  (the free-water level on screen is *computed* from fitted pressure gradients).
* **Script as data.** Each beat has `VO`, `SHOT`, `FLAGS`, `TERMS`. `script/scriptlib.py` lints pacing and enforces that
  **every glossary term is defined in the beat where it first appears**; the voice build writes the real timeline.
* **Animations that explain.** The required mechanisms: mud-weight window + casing telescoping (Ch 1), BOP closing
  (Ch 3), cement displacement in an eccentric annulus (Ch 6), a kick expanding up the annulus (Ch 7), plug placement (Ch 9).
* **Render budget.** Only frames where something changes are drawn; holds are repeated by the encoder.

## Decisions taken (you said "finish on your own")

| | Decision |
|---|---|
| D1 style | 2-D motion graphics (schematic cutaways, charts), not photoreal 3-D. |
| D2 example | Fictional composite wildcat (invented numbers, real physics), flagged on screen and in the end card. |
| D3 voice | Kokoro-82M neural TTS. A human voice-over still beats it: drop a recording in as `audio/narration.wav` (one file, same sentence timings in `audio/sentences.json`) and re-run `make mix assemble`. |
| D4 length | 36:42, not 30:00: the review added physics the first cut skipped, and at a natural speaking pace it does not fit in 30 minutes without cutting content (Ch 1, 7 and 8 are the longest). |
| D5 sources | Hosts stayed blocked; nothing from NORSOK/regulations is verified against the primary text. |
| D6 incident | Physics-puzzle hooks; one incident (Macondo 2010) in Ch 7. |
| D7 units | bar / sg / m, casing sizes in inches. |

## Known limitations (honest list)

* Synthetic voice: natural-sounding, but an American-English TTS voice; occasional odd stress or pronunciation of
  technical words is possible.
* Visuals are schematic 2-D cutaways, not CFD or 3-D renders: cement displacement, kick expansion and bubble sizes are
  simple models (`[SIM]` in the script), not simulations.
* `[VERIFY]` claims (barrier counts per source in P&A, BOP test rules, riserless top-hole barrier treatment, DST frequency
  on the NCS, ...) need checking against the primary documents.
* Visual QA was done on sampled stills (several per beat, plus key spoken moments), not frame by frame.
* Equinor internal requirements (TR/WR series) are not public and are not used.

## Layout

```
script/    narration chapters (chNN_*.md), glossary, scriptlib (lint/fit/emit), generated NARRATION/FLAGS/timeline
scenes/    common/{stage,look,palette,chart,shapes,furniture,timeline,well_model,logs}.py, chNN_*.py, render.py,
           assemble.py, STYLE.md (engine + layout rules for scene authors)
audio/     build_audio.py (Kokoro voice + timeline), mix.py (music + sound design), subtitles.py
renders/   chapter videos and QA stills (git-ignored)      build/  final mp4 + srt (git-ignored)
Makefile   all entry points                               requirements.txt
```
