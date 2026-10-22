# Fatigue of the conductor and the conductor–template interface — the NORSOK U-001 method

A 44-minute narrated tutorial that works through the fatigue assessment of a subsea conductor and of the
conductor/template interface the way **NORSOK U-001:2026** (Annex A, Annex B, Annex J and clause 13.3.6) asks
for it. Every equation is derived on screen, step by step, and the method is then applied to one worked example
well. 1080p / 30 fps, English narration, soft subtitles, chapter markers, −16 LUFS.

| File | What it is |
| --- | --- |
| `out/conductor-fatigue_part1_1080p.mp4` | Cold open, 01 The system and the rules, 02 Fatigue and the S-N curve |
| `out/conductor-fatigue_part2_1080p.mp4` | 03 From waves to the wellhead moment, 04 Load paths and load share |
| `out/conductor-fatigue_part3_1080p.mp4` | 05 The conductor in the soil, 06 From moment to hot-spot stress |
| `out/conductor-fatigue_part4_1080p.mp4` | 07 Building the M-N curve, 08 Damage, life and the design check |
| `out/conductor-fatigue_part5_1080p.mp4` | 09 Worked example, 10 Summary |
| `out/conductor-fatigue.srt` / `.vtt` | Captions for the full running time (numbers and acronyms written the way they are read) |
| `out/conductor-fatigue_transcript.md` | Full transcript with chapter and beat timestamps |
| `out/poster.png` | Title-card still |

The video is split into five parts at chapter boundaries so that every file stays below GitHub's 100 MiB limit.
Each part carries its own subtitle track and chapter markers. `python3 tools/encode.py --full` also writes one
full-length file to `build/`.

## Storyline (44:28)

| Time | Chapter | What it covers |
| --- | --- | --- |
| 00:00 | Cold open | The rig in the swell, down the riser to the BOP and the wellhead, the cut through template and soil, the two hot spots |
| 01:16 | 01 The system and the rules | Exploded wellhead system (HP housing, extension, surface casing, conductor housing, conductor), definition 3.1.7, where the rules sit in U-001, the method in eight steps |
| 04:02 | 02 Fatigue and the S-N curve | Definition 3.2.19, stress range and mean stress, why welds see the full range, Paris law → N·Δσᵐ = ā, scatter and the design curve (mean − 2 s), DNV-RP-C203 class C1 in seawater with CP, thickness effect, 13.3.6.2 |
| 09:57 | 03 From waves to the wellhead moment | The load chain, lever arm Q = M/H, M(z) = M_w(1 + z/H), Table A.4 vs fatigue, Table A.7 ΔM₀, the Table A.8 histogram, service life = fatigue life / D_F |
| 14:30 | 04 Load paths and load share | Contact areas A–H and the three load paths of Figure J.1, springs in parallel, Table 4, bending share by EI, the template as a rotational spring k_θ = k_C k_D h²/(k_C + k_D), the radial gap, thermal growth and the 100 mm requirement |
| 19:59 | 05 The conductor in the soil | Beam on an elastic foundation: EI y'''' + k y = 0, β, the decaying solution, boundary conditions at the mudline, the peak moment below the mudline, k_θ of the well = EIβ, real p-y curves |
| 23:25 | 06 From moment to hot-spot stress | σ = My/I from plane sections, I of a tube from the polar moment, GW1 nominal stress, SCF = 1 + 3e/t for misalignment, the slot-ring beam model for TS1, where the hot spots are |
| 27:41 | 07 Building the M-N curve | S-N → M-N, constants (B.8)/(B.9), the nonlinear local response, B.4.2.4 a)–f), the six load levels, the knee (B.10)/(B.11), lower bound over the points, RF, Tables B.11/B.12 |
| 33:35 | 08 Damage, life and the design check | Palmgren–Miner, T_f = 1/D, (B.3)/(B.4) and Table B.4, NORSOK N-001 DFF, ΔM_eq (B.14), (B.13), (B.12) and a check against Table A.7, the screening check ΔM_c / D_F^{1/m} ≥ ΔM₀ |
| 37:57 | 09 Worked example | All eight steps on one illustrative well: screening fails, full Miner sum passes (GW1 1.40 years ≈ 513 days, TS1 3.57 years), the gap trade-off, sensitivities, mitigation |
| 43:00 | 10 Summary | The method on one page, the outro and the sources |

## Worked example (illustrative teaching inputs, not project data)

350 m water depth, BOP on the wellhead (ΔM₀ = 1 436 kNm, H_LFJ = 13.7 m), 36 in × 2 in conductor around a
20 in × 1 in surface casing, wellhead datum 4.0 m above the mudline, template rings C and D 1.6 m and 3.6 m below the
datum (200 and 400 MN/m) with a 2 mm radial gap, Winkler soil k = 5 MPa, 5 m cement shortfall.

| Result | GW1 conductor girth weld | TS1 template slot weld |
| --- | --- | --- |
| S-N curve | C1, seawater + CP, SCF 1.10, t = 50.8 mm | D, seawater + CP, 0.156 MPa per kN of ring force |
| ΔM_c (single-load capacity at 10⁶ cycles) | 2 780 kNm | 2 838 kNm |
| Screening ΔM_c / 10^{1/3} vs ΔM₀ | 1 290 < 1 436 → fails | 1 317 < 1 436 → fails |
| Annual damage, bilinear M-N curve | 0.0712 | 0.0280 |
| Fatigue life | 14.0 years | 35.7 years |
| Fatigue service life (D_F = 10 / DFF = 10) | **1.40 years ≈ 513 days** | **3.57 years** |

Single-slope full sum for GW1: 9.0 years; screening at 10⁶ cycles: 7.3 years. Back-calculated ΔM₀ from the
histogram with (B.12)–(B.14), m = 3: 1 335 kNm (Table A.7 gives 1 436 kNm).

All numbers come from [`model/fatigue_model.py`](model/fatigue_model.py), which writes `src/data/model.json`; the
scenes read their numbers from that file, and the narration was written from it.

## Content notes — please read before using this in a course or a project

* **S-N data.** The C1 and D curves in seawater with cathodic protection use the DNV-RP-C203 **2016** constants
  (C1: m = 3/5, log ā = 12.049/16.081, knee at 10⁶ cycles; D: 11.764/15.606). NORSOK U-001:2026 refers to
  DNV-RP-C203:2024, which revised the seawater curves. The video says so on screen; take design values from the
  edition in your design basis.
* **Fatigue life reduction factor.** RF = 1 is used in the example. Clause B.4.4 requires the RF from
  DNV-RP-C203:2024 section 5.7 for the hot spot in question.
* **Local response model.** B.4.2.4 asks for a 3D elastic FE model with contacts, preload, cement shortfall,
  friction, tolerances and clearances. The tutorial uses a simplified two-string beam model with Winkler springs
  and gap contacts as a teaching stand-in, and says so on screen.
* **Template DFF.** DFF = 10 for TS1 follows NORSOK N-001 for a weld with no access for inspection and substantial
  consequences. Check the classification and the N-001 edition for the actual template.
* **Inputs.** Ring stiffnesses, soil stiffness, cement shortfall, SCFs, the slot-ring beam model and the TS1 stress
  per kN are illustrative. Tables A.7 and A.8 and the clause references are from NORSOK U-001:2026; verify them
  against your copy of the standard.

## How it is built

Everything on screen is a pure function of the clock: any frame can be rendered by any worker, in any order.

```
model/fatigue_model.py    engineering model (loads, local response, M-N curves, Miner sums, sensitivities) -> src/data/model.json
script/script.md          narration script: 11 chapters, 69 beats, {cue} markers for the animation
tools/tts.py              Kokoro-82M (ONNX) narration + word timings -> build/audio/narration.wav, src/data/timeline.json
src/js/engine/            deterministic keyframe engine, KaTeX equations with morphs, SVG charts, HUD
src/js/three/             three.js world: wellhead, conductor, template, BOP, riser, rig, sea, sky, soil, cut-aways
src/js/scenes/ch00-10.js  one file per chapter, timed to the narration cues
tools/frame.mjs           stills and contact sheets for review
tools/render.mjs          parallel Playwright/Chromium (SwiftShader WebGL) renderer -> ffmpeg segments -> build/render/video.mp4
tools/audio.py            synthesised music bed, ambience and effects, ducking, -16 LUFS master -> build/audio/mix.wav
tools/captions.py         SRT / VTT / ASS captions, chapter metadata and transcript from the word timings
tools/encode.py           two-pass size-targeted x264 parts with subtitles and chapters, poster
```

Rebuild:

```bash
npm install
pip install numpy scipy soundfile kokoro-onnx num2words
python3 model/fatigue_model.py        # numbers -> src/data/model.json
python3 tools/tts.py                  # narration + timeline (only if script.md changed)
python3 tools/audio.py                # mix -> build/audio/mix.wav
python3 tools/captions.py             # captions, chapters, transcript
node tools/render.mjs                 # about 3 h on 4 cores; 3D frames cost about 1 s each in SwiftShader
python3 tools/encode.py               # -> out/*.mp4, poster
```

Re-render only what changed: delete the matching `build/render/seg_XXXXXX.mp4.done` markers (450 frames = 15 s each)
and run `node tools/render.mjs` again (chunk names are frame numbers, multiples of 450). Frames whose DOM and WebGL
state did not change re-use the previous screenshot. `--select 3d` / `--select 2d` split the WebGL chunks (best on one
worker) from the others, and `touch build/render/STOP` ends a pass at the next chunk boundary.

Preview in a browser: `node tools/server.mjs 8080`, open `http://127.0.0.1:8080/src/index.html?play=1&t=600` and
click once (plays the mix from 10:00). `node tools/frame.mjs --chapter 4 --sheet` renders a contact sheet.

Third-party pieces: three.js (MIT), KaTeX (MIT), Kokoro-82M voice (Apache-2.0), Inter and JetBrains Mono fonts
(OFL). The 3D equipment is procedural geometry inspired by the Blender models on the
`claude/equinor-subsea-well-video-uisotu` branch; all sound is synthesised in `tools/audio.py`.
