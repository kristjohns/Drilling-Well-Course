# Drilling Well Course

A ~30-minute, Veritasium-style explainer on the technical lifecycle of an offshore
exploration well (spud → discovery evaluation → permanent abandonment), written for an
engineer new to drilling on the Norwegian Continental Shelf. Narration, shot list and
Blender (`bpy`) animations are generated from this repo.

**Accuracy over polish.** Simplifications are marked `[SIM]` in the script; Norway-specific
material is marked `[NO]` (NORSOK D-010, Havtil/Sodir rules) vs `[GEN]` (general industry
practice); unverified claims are marked `[VERIFY]` and never ship.

## Layout

| Path | Purpose |
|---|---|
| `script/` | Research outline, sources register, narration, shot lists, glossary |
| `scenes/` | Blender/`bpy` scene modules, one per chapter, plus shared style (added in Stage 3) |
| `renders/` | Frame/clip output (git-ignored) |
| `audio/` | Narration audio, music/SFX (git-ignored) |
| `sources/` | Your local copies of standards/regulations for me to cite (git-ignored, copyrighted) |
| `Makefile` | Build entry points (`make help`) |

## Pipeline status

| Stage | Deliverable | Status |
|---|---|---|
| 1 | Research outline, chapter timings, sources: `script/00_outline.md`, `script/00_sources.md` | **Awaiting approval** |
| 2 | Narration script with timestamps + shot list | not started |
| 3 | Blender scene scripts (shared style, one module per chapter) | not started |
| 4 | Low-res preview of one chapter | not started |
| 5 | Narration, ffmpeg assembly, subtitles, 1080p export | not started |

## Quick start

```sh
make doctor   # report which tools are installed / missing
make venv     # create .venv with bpy 4.5 LTS, numpy, matplotlib, Pillow, PyYAML (~1 GB)
```

`bpy` (the pip module) renders headless, so a Blender binary is not required.
EEVEE needs a GL context: run it under `xvfb-run -a` on machines without a display.
