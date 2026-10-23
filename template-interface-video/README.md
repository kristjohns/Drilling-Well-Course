# The template interface — when has it failed?

An 11-minute narrated follow-up to the acceptance-criteria tutorial (`acceptance-criteria-video/`). It looks at the
interface between the subsea wellhead and the template slot and asks: when has it failed according to the standard?
At 0.2 % yield, at a 5 % strain, or at the 2 % strain sometimes attributed to Eurocode 3, Part 1-5? It follows
NORSOK U-001:2026 to the documents it calls up and checks a slot ring of the 3D model both ways.
1080p / 30 fps, English narration, soft subtitles, chapter markers, −16 LUFS.

| File | What it is |
| --- | --- |
| `out/template-interface_part1_1080p.mp4` | Cold open, 01 Who owns the interface, 02 The template steel: the elastic check (5:31, 92 MiB) |
| `out/template-interface_part2_1080p.mp4` | 03 Non-linear FE: EN 1993-1-5 Annex C, 04 Five percent, and the two, 05 Summary (5:49, 92 MiB) |
| `out/template-interface_full_720p.mp4` | The whole film in one file, 720p (94 MiB), with subtitles and chapters |
| `out/template-interface.srt` / `.vtt` | Captions (numbers and symbols written the way they are read) |
| `out/template-interface_transcript.md` | Full transcript with chapter and beat timestamps |
| `out/poster.png` | Title-card still |

## The short answer

| Question | Answer |
| --- | --- |
| Who sets the failure criterion of the template side? | Not U-001. Clause 13.3.6.1: "Structural design shall follow NS-EN ISO 13628-15:2011 clause 5.4 and NORSOK N-001." N-001 sends steel design to NORSOK N-004 (normative reference N-004:2022), which builds on Eurocode 3. |
| And the wellhead side of the same contact? | U-001 Annex B (conductor pipe: B.9): load ≤ F<sub>d</sub> × capacity, with σ<sub>y</sub> defined at 0.2 % plastic strain — the subject of the first video. |
| Can the interface fail without any stress limit being reached? | Yes, as a mechanism: the relative displacement (100 mm to be accounted for, 13.3.6.2) uses up the margin to the end stops — an SLS check with load factor 1.0 (Table A.2 note d); reaching an end stop preloads the template and creates separate ULS load cases. Template inclination ≤ 0.3° (13.3.6.4). |
| Is it the 0.2 % yield on the template side? | In an elastic Eurocode check, effectively yes: von Mises at the critical point ≤ f<sub>y</sub>/γ<sub>M0</sub> (EN 1993-1-1 6.2.1(5)); f<sub>y</sub> is R<sub>eH</sub>, or R<sub>p0.2</sub> when there is no distinct yield point. It is the most conservative route: first yield at a point. |
| And in a non-linear FE analysis? | EN 1993-1-5 Annex C (informative): failure is the **maximum load** where buckling is possible, or a **limiting principal membrane strain** in regions in tension — **5 % recommended**, the National Annex may set another value (C.8); and the load multiplier at that state must satisfy α<sub>u</sub> > α<sub>1</sub>·α<sub>2</sub> (C.9, formula C.2). |
| Is there a 2 % criterion in Eurocode 3, Part 1-5? | Not that we could find. Annex C has one strain value, the 5 %. A 2 % appears in other offshore documents (see `docs/sources-and-checks.md`), none of which were verified here. |

## Storyline (11:20)

| Time | Chapter | What it covers |
| --- | --- | --- |
| 00:00 | Cold open | The well in its template slot; the conductor pushes on the lower slot ring D; three questions; title |
| 00:55 | 01 Who owns the interface | Figure J.1 contacts C and D and load path 3, load share (3.1.12, Table 4), the two rule books (Annex B and B.9 · 13.3.6.1 → ISO 13628-15 §5.4 + N-001 → N-004 → Eurocode 3), the interface as a mechanism (100 mm, end stops, SLS, 0.3°) |
| 03:25 | 02 The template steel: the elastic check | Load and material factors, the yield strength in Eurocode 3 (R<sub>eH</sub> / R<sub>p0.2</sub>, ε<sub>y</sub> = 0.16 %), the von Mises check on the slot ring: 416 MPa against 300 MPa |
| 05:31 | 03 Non-linear FE: EN 1993-1-5 Annex C | The annex, material models (C.6, Figure C.2), load multiplier (C.7), limit state criteria (C.8, the 5 %), the ring analysis with the 3D strain contour, the margin (C.9, αu > α1·α2) |
| 08:51 | 04 Five percent, and the two | No 2 % in Part 1-5; what a 2 % limit would change on the ring; the strain at a point depends on the mesh, the load hardly does; EN 1993-1-14:2025 |
| 10:12 | 05 Summary | When has the interface failed: one table; sources and disclaimer |

## Worked example (illustrative teaching inputs, not project data)

Lower slot ring D of the 4-slot template: an annular plate cut from 40 mm S355 plate (f<sub>y</sub> 345 MPa), inner
radius 459 mm, width 200 mm, pinned at four struts; the conductor bears on it over ±20° between two struts with a ULS
design contact force of 1.6 MN.

| Check | Result |
| --- | --- |
| Elastic, EN 1993-1-1 6.2.1(5) | 416 MPa vs f<sub>y</sub>/γ<sub>M0</sub> = 300 MPa → utilisation 1.39, fails |
| First yield / 0.2 % plastic strain at the edge | α = 0.83 / 1.25 |
| Non-linear, nominal plateau, no hardening (Figure C.2 b) | mechanism at α = 1.54; 5 % strain at 1.53; 2 % at 1.49 |
| Non-linear, linear hardening E/100 (Figure C.2 c) | no peak, no buckling → 5 % strain governs: α<sub>u</sub> = 1.76 (2 % would give 1.59) |
| C.9 (C.2) | α<sub>u</sub> = 1.76 > α<sub>1</sub>·α<sub>2</sub> = 1.0 × 1.3 → accepted |
| Mesh study (nominal plateau) | at α = 1.50 the largest strain is 1.4 % with 5° elements and 2.4 % with 0.6° elements; α at 5 % changes from 1.54 to 1.52 |

All numbers come from [`model/interface_model.py`](model/interface_model.py) (fibre beam ring model in
[`model/ring_fe.py`](model/ring_fe.py)), which writes `src/data/model.json`; the scenes read their numbers from that
file. Every statement attributed to a standard is listed with its source and how well it was checked in
[`docs/sources-and-checks.md`](docs/sources-and-checks.md).

## Content notes — please read before using this in a course or a project

* **What was read and what was not.** NORSOK U-001:2026 was read, and so were clauses C.6 (Figure C.2), C.7, C.8 and
  C.9 of NS-EN 1993-1-5:2006+A2:2019 (pages 48–49, from a screenshot). EN 1993-1-1, EN 10025-2, NORSOK N-001 /
  N-004:2022, ISO 13628-15, the Norwegian National Annex value for C.8 and the DNV documents were not available in this
  session and are stated from general knowledge.
* **Material factors.** γ<sub>M</sub> = 1.15 (ULS) and 1.0 (ALS) as used with NORSOK N-004 / N-001; α<sub>1</sub> = 1.0
  and α<sub>2</sub> ≤ 1.3 are assumptions of the example. Confirm them in the editions of your design basis.
* **Teaching model, not an FE result of a real slot.** The ring is a beam model with pinned struts, analysed materially
  non-linear and geometrically linear (it is assumed stocky enough not to buckle). A real check models plates, welds,
  struts, the funnel and the contact, and decides with the design basis whether Annex C applies.
* **ALS.** In accidental limit states NORSOK uses γ<sub>M</sub> = 1.0 and the ductility limits of N-004 Annex A; the
  video does not quote them.

## How it is built

The pipeline is the one of the acceptance-criteria tutorial (deterministic keyframe engine, three.js world, Kokoro
narration, audio mix, captions, encoder), with new chapters and two additions to the 3D model: ring D of the template
as a 40 mm plate ring, and an FE view of that ring (deformed, banded von Mises stress or membrane-strain contour with
the 5 % line, computed per fragment from the ring model's results in a float texture).

```
model/ring_fe.py            2D fibre beam model of the ring (return mapping, displacement control)
model/interface_model.py    elastic check, material models (a) and (c), markers, mesh study -> src/data/model.json
script/script.md            narration script: 6 chapters, 18 beats, {cue} markers for the animation
tools/tts.py                Kokoro-82M (ONNX) narration + word timings -> build/audio/narration.wav, src/data/timeline.json
src/js/three/models.js      wellhead, template (ring D as a plate ring), BOP; feRing, ringMaterial, ringDeform
src/js/scenes/ch00-05.js    one file per chapter; ringfx.js helpers for the ring shots (legends, field, probe points)
tools/render.mjs            parallel Playwright/Chromium (SwiftShader WebGL) renderer -> build/render/video.mp4
tools/audio.py              music bed, ambience and effects, ducking, -16 LUFS master -> build/audio/mix.wav
tools/captions.py           SRT / VTT captions, chapter metadata and transcript
tools/encode.py             two-pass x264 parts below 100 MiB with subtitles and chapters, poster
```

Rebuild:

```bash
npm install
pip install numpy scipy soundfile kokoro-onnx num2words   # docopt may need: pip install --use-pep517 docopt
python3 model/interface_model.py
python3 tools/tts.py              # narration + timeline (only if script.md changed)
python3 tools/audio.py
python3 tools/captions.py
node tools/render.mjs --workers 3
python3 tools/encode.py --full720
```

Preview in a browser: `node tools/server.mjs 8080`, open `http://127.0.0.1:8080/src/index.html?play=1&t=440` and
click once. `node tools/frame.mjs --chapter 3 --sheet` renders a contact sheet of a chapter.

Third-party pieces: three.js (MIT), KaTeX (MIT), Kokoro-82M voice (Apache-2.0), Inter and JetBrains Mono fonts (OFL).
