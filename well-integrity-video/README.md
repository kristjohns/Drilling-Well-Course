# Well Integrity on the Norwegian Continental Shelf: course video

A ~28-minute animated, narrated training film on well integrity, focused on Norwegian Continental Shelf (NCS)
practice and current developments (NORSOK D-010 rev. 5, Havtil regulations and findings, Offshore Norge 117,
P&A, creeping shale, Troll/Deepsea Bollsta 2025, CO₂ storage).

Everything is generated from code: the narration is synthesized offline, the animations are drawn frame by frame
with Skia, and the soundtrack is synthesized in NumPy.

## Chapters
| # | Chapter | Content |
|---|---------|---------|
| – | Cold open | North Sea, platform, stratigraphy, the well, agenda |
| 1 | What is well integrity? | D-010 definition, technical/operational/organizational, life cycle, ISO 16530 |
| 2 | The Norwegian framework | Havtil, Facilities §48, Activities §85, Management §5, NORSOK D-010 rev. 5, Offshore Norge 117/135 |
| 3 | Barrier philosophy | Envelopes, two-barrier principle, drilling well (hydrostatics, LOT, kick, shut-in, MPD), production well, DHSV, WBS, EAC, intervention |
| 4 | Verification and testing | Pressure and inflow tests, Macondo, DHSV leak test, BOP tests, cement job, CBL/VDL, ultrasonic imaging |
| 5 | Annulus pressure management | A/B/C annuli, thermal and trapped pressure, gas lift, leaks, MAASP (worked example), monitoring, Gullfaks C |
| 6 | Classifying well integrity | Green/yellow/orange/red, RNNP, PSA pilot study, Havtil 2024 survey of temporarily abandoned wells |
| 7 | When barriers fail | Failure modes, Ekofisk subsidence, Snorre A 2004, Gullfaks C 2010, Troll/Deepsea Bollsta 2025 |
| 8 | Plug and abandonment | Scale on the NCS, three phases, eternal perspective, rock to rock, plug lengths, milling, PWC, cut and pull, creeping shale, bismuth, thermite |
| 9 | CO₂ storage | Northern Lights, carbonic acid, impurities, cycling, legacy wells, SINTEF 2024 |
| 10 | Digital well integrity and key lessons | Monitoring, digital WBS, WIMS, calibration, six lessons |

## Files
- `output/` – final video (MP4, 1080p30, AAC audio, embedded English subtitles) and `subtitles.srt`
- `script/narration.py` – the narration script with cue names
- `SOURCES.md` – references for all facts and figures
- `src/` – pipeline: `tts.py` + `build_audio.py` (narration), `engine/` + `scenes/` + `render.py` (animation),
  `build_mix.py` (music, SFX, ducking, loudness, subtitles), `assemble.py` (final MP4)

## Rebuild
Requirements: Python 3.11+, `skia-python`, `numpy`, `scipy`, `soundfile`, `onnxruntime`, `misaki`, `spacy`,
`num2words`, `espeak-ng`, `ffmpeg`; Kokoro-82M ONNX weights and voices (set `KOKORO_DIR`).

```sh
python3 src/build_audio.py        # narration + timeline
python3 src/render.py all 3       # render all scenes (3 parallel jobs)
python3 src/build_mix.py          # music, SFX, mix, loudness, subtitles
python3 src/assemble.py           # final MP4
```
Review helpers: `python3 src/render.py sheet <scene> 5` (contact sheet), `python3 src/render.py still <scene> <t>`.

Values in schematics and plots are illustrative and not for engineering use. Narration voice: Kokoro-82M (Apache-2.0).
