# Acceptance criteria for structural analysis — NORSOK U-001:2026, Annex B

A 22-minute narrated tutorial on what NORSOK U-001:2026 actually accepts when a wellhead component is checked by
analysis: is the criterion the yield strength, is it a strain limit, and what do you take out of an FE model? It
reads the stress–strain diagram, extracts and linearises stresses along a stress classification line, runs the
limit-load and plastic-collapse checks, and ends with a worked example on the 3D wellhead model of this repository.
1080p / 30 fps, English narration, soft subtitles, chapter markers, −16 LUFS.

| File | What it is |
| --- | --- |
| `out/acceptance-criteria_part1_1080p.mp4` | Cold open, 01 Load against capacity, 02 The stress-strain diagram |
| `out/acceptance-criteria_part2_1080p.mp4` | 03 The elastic route: extracting stress, 04 The elastic-plastic route |
| `out/acceptance-criteria_part3_1080p.mp4` | 05 Where strain is the criterion, 06 Worked example: the red spot, 07 Summary |
| `out/acceptance-criteria_full_720p.mp4` | The whole film in one file, 720p (94 MiB), with subtitles and chapters |
| `out/acceptance-criteria.srt` / `.vtt` | Captions for the full running time (numbers and symbols written the way they are read) |
| `out/acceptance-criteria_transcript.md` | Full transcript with chapter and beat timestamps |
| `out/poster.png` | Title-card still |

The 1080p video is split into parts at chapter boundaries so that every file stays below GitHub's 100 MiB limit; the
720p file holds the whole film. Every file carries a subtitle track and chapter markers.

## The short answer

| Question | Answer in U-001:2026 |
| --- | --- |
| Is the acceptance criterion the yield strength? | The yield strength σ_y = min(Y_y·SMYS; 0.9·Y_u·SMTS) (B.5), defined at 0.2 % plastic strain, anchors every check, but it is never compared with a peak stress. The design format is formula (B.2): load ≤ F_d × capacity, with F_d from Table B.3 (normal 0.67, extreme 0.80, accidental 0.90/1.00, pressure 0.60, functional 1.00). |
| Elastic FE analysis | Linearised stresses along a stress classification line (ASME VIII-2 Annex 5-A), by category, against Table B.7: P_m, P_L ≤ σ_y; P + P_b ≤ 1.5 σ_y; P + Q range ≤ 2 σ_y; shear ≤ 0.57 σ_y; bearing ≤ σ_y. Preliminary design only (B.3.3), and for pressure-containing parts only when D/t > 10 (B.3.5.1). |
| Is it a strain limit in elastic-plastic analysis? | Not for yielding. The yielding capacity is a load: the limit load (true curve cut off at σ_y, structural instability / non-convergence) or the plastic collapse load divided by MAX[1.2; σ_u/σ_y] (B.3.6.3.2). |
| Where is strain the criterion? | (1) Studs, clamp segments and connector locking segments in bending: 0.2 % equivalent plastic strain through the root section. (2) Local failure: accumulated plastic strain against the triaxiality-dependent limit of ASME VIII-3 KD-232, waived for carbon and low-alloy steels with elongation ≥ 17 % and reduction of area ≥ 35 % (SMYS ≤ 655 MPa) (B.3.6.3.3). |
| Other modes | Buckling: maximum load / 1.10. Mechanical disengagement: load / 1.1. Ratcheting only above 180 °C. Functional capacities at F_d = 1.0 with manufacturer criteria validated by test. |

## Storyline (22:11)

| Time | Chapter | What it covers |
| --- | --- | --- |
| 00:00 | Cold open | A drive-off bends the wellhead; the FE model of the housing shows 793 MPa at the neck fillet, 53 % above σ_y; three questions; title |
| 01:10 | 01 Load against capacity | Scope of Annex B on the 3D wellhead (housings, extensions, connectors; conductor pipe → B.9; template → N-001), Table B.2 failure modes, formula (B.2) and Table B.3, the three capacity methods of B.3.3 |
| 03:56 | 02 The stress-strain diagram | Tensile test, 0.2 % offset (3.1.22, 3.1.23), design values (B.5)/(B.6) for a 75K forging, true stress and strain, the KM-620 curve, the three FE material curves of Figure B.5 |
| 07:16 | 03 The elastic route: extracting stress | FE model and von Mises contour, why the peak is not the static criterion, the SCL, linearisation (membrane, bending, peak), stress categories, Table B.7 and the shape factor 1.5, the check with F_d, the fine print (preliminary design, D/t > 10) |
| 11:44 | 04 The elastic-plastic route | FE requirements and load sequence, the limit load (yielded zone growing to a plastic hinge, non-convergence), the factored plastic collapse load and the factor 1.2, Figure B.6, the capacity chart of (B.7) |
| 15:05 | 05 Where strain is the criterion | Studs in bending (0.2 % through the root section), local failure (triaxiality, KD-232 strain limit, damage over the load history), the ductility exemption, the remaining modes |
| 18:14 | 06 Worked example: the red spot | Table A.4 loads moved to the neck, pressure end load, (B.7) for ALS (0.88) and ULS (0.61), the other failure modes, the verdict |
| 20:48 | 07 Summary | The three answers on one page; sources and disclaimer |

## Worked example (illustrative teaching inputs, not project data)

HP wellhead housing neck just below the connector hub (all wellhead datum load passes through it): API 75K forging
(σ_y 517 MPa, σ_u 655 MPa), OD 0.700 m, bore 0.476 m, 0.6 m below the datum; Table A.4, 250–500 m, BOP on WH;
690 bar on a 0.50 m gasket sealing diameter.

| Result | Value |
| --- | --- |
| Moment at the neck, true wall tension | ALS 12.75 MNm, 16.97 MN · ULS 7.68 MNm, 12.08 MN |
| Peak von Mises at the fillet (ALS) | 793 MPa |
| Elastic route (ALS), F_d = 0.9 | P_L 482 MPa vs 465 → 1.04, fails; P_L + P_b 613 vs 698 → 0.88; not permitted anyway (D/t = 6.25) |
| Limit load (bending) | 20.26 MNm (surface at 0.2 % plastic strain at 0.89 of it) |
| Factored plastic collapse (bending) | 25.22 / 1.267 = 19.91 MNm |
| Tension capacity | 107.0 MN |
| (B.7) with the limit-load capacities | ALS 0.88 (F_d 0.9), ULS 0.61 (F_d 0.8): acceptable |
| Local failure | exempt (75K meets 17 % / 35 %) |

All numbers come from [`model/acceptance_model.py`](model/acceptance_model.py), which writes `src/data/model.json`;
the scenes read their numbers from that file and the narration was written from it. Every statement attributed to
the standard is listed with its clause in [`docs/sources-and-checks.md`](docs/sources-and-checks.md).

## Content notes — please read before using this in a course or a project

* **Stand-ins, not FE results.** The stress field on the 3D housing and along the SCL is built from beam stresses,
  Lamé pressure stresses and an assumed fillet peak (K_t 1.5, 12 mm deep). The load–rotation curves come from a section
  (fibre) model of the neck. A real check follows B.3.4: a 3D FE model with contacts, preload, friction, tolerances,
  and test validation for connectors. Both are labelled on screen.
* **ASME material.** The KM-620 curve, the Annex 5-A linearisation formulas and the KD-232 strain limit are taken from
  ASME BPVC as referenced by U-001; the constants were not taken from the 2025 edition. Check them against the edition
  in your design basis.
* **Design factor for the wellhead.** The accidental case uses F_d = 0.90 (below and including barrier elements; a
  wellhead is not retrieved for inspection). Confirm the classification for your equipment.
* **Inputs.** The neck geometry, D_s, the pressure combination and the material are illustrative.
* **A remark on the standard.** B.3.6.2 note 4 says the plastic collapse load "will typically be 0 % higher" than the
  yielding capacity; a number seems to be missing (B.3.6.3.2.3 note 1 says 10 % to 20 %).

## How it is built

The pipeline is the one of the conductor-fatigue tutorial (`claude/conductor-fatigue-norsok-video` branch): the same
deterministic keyframe engine, three.js world, Kokoro narration, audio mix, captions and encoder, with new chapters and
three additions to the 3D model: the housing neck and fillet, an FE view of the housing (cut half, mesh lines, banded
von Mises or equivalent-plastic-strain contour computed in the fragment shader) and the SCL marker.

```
model/acceptance_model.py  design strength, KM-620 curves, SCL linearisation, section model, (B.7) checks -> src/data/model.json
script/script.md           narration script: 8 chapters, 36 beats, {cue} markers for the animation
tools/tts.py               Kokoro-82M (ONNX) narration + word timings -> build/audio/narration.wav, src/data/timeline.json
src/js/three/models.js     wellhead, template, BOP, riser, rig, sea; HP_PROFILE with the neck; feMaterial, feHousing
src/js/scenes/ch00-07.js   one file per chapter, timed to the narration cues; fx.js shared helpers (legends, probes, capacity chart)
tools/render.mjs           parallel Playwright/Chromium (SwiftShader WebGL) renderer -> build/render/video.mp4
tools/audio.py             music bed, ambience and effects, ducking, -16 LUFS master -> build/audio/mix.wav
tools/captions.py          SRT / VTT captions, chapter metadata and transcript
tools/encode.py            two-pass x264 parts below 100 MiB with subtitles and chapters, poster
```

Rebuild:

```bash
npm install
pip install numpy scipy soundfile kokoro-onnx num2words   # docopt may need: pip install --use-pep517 docopt
python3 model/acceptance_model.py
python3 tools/tts.py              # narration + timeline (only if script.md changed)
python3 tools/audio.py
python3 tools/captions.py
node tools/render.mjs --workers 3
python3 tools/encode.py
```

Preview in a browser: `node tools/server.mjs 8080`, open `http://127.0.0.1:8080/src/index.html?play=1&t=440` and
click once. `node tools/frame.mjs --chapter 3 --sheet` renders a contact sheet of a chapter.

Third-party pieces: three.js (MIT), KaTeX (MIT), Kokoro-82M voice (Apache-2.0), Inter and JetBrains Mono fonts (OFL).
