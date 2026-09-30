# Drilling-Well-Course

**The Life of a Subsea Well** is an animated course video, about 13 minutes long, on how a subsea well on the
Norwegian Continental Shelf (NCS) is **designed, drilled, completed and plugged & abandoned**. It is made in
the style of *The Efficient Engineer*: clean 3D cutaways, animated diagrams, labels that point at the
hardware, and a calm voice-over.

Everything in the video is generated from code in this repository. That covers the 3D models (Blender),
the 2D diagrams (cairo), the narration (neural text-to-speech) and the music and sound effects (numpy),
so the whole video can be edited and rebuilt.

## Output

| File | Contents |
|---|---|
| `video/output/subsea_well_lifecycle_*.mp4` | The finished video with narration, music and chapter markers |
| `video/output/subsea_well_lifecycle.en.srt` | English subtitles |
| `video/script/narration.md` | Full narration script, sorted by chapter |

## Chapters

| # | Chapter | What is covered |
|---|---|---|
| – | Introduction | From the sea surface down to the reservoir, and the four phases of a well's life |
| – | The setting | 350 m of water, the subsea production system, the reservoir, the cap rock as "nature's lid" |
| 1 | Design | Pore pressure, kicks and blowouts, P = ρgh, fracture pressure, **the drilling window**, casing setting depths, the casing telescope (30″ → 7″), burst / collapse / tension, the **two-barrier principle (NORSOK D-010)** |
| 2 | Drilling | The semi-submersible rig, moorings, derrick and top drive, riserless top hole, conductor and wellhead housings, the **BOP** (annulars, pipe rams, blind shear rams), the marine riser, the mud circulation loop, the PDC bit, MWD mud-pulse telemetry, rotary steerable drilling, cementing (plugs, bumping the plug), the leak-off test, well control |
| 3 | Completion | Liner, perforating with shaped charges, production tubing, the production packer, the downhole safety valve, the subsea christmas tree, jumpers and umbilical, the production barrier envelopes, production decline |
| 4 | P&A | The "eternal perspective", killing the well, rock-to-rock barriers over the full cross-section, poor annular cement, section milling vs. perforate-wash-cement, primary, secondary and surface plugs, verification, cutting the casings below the seabed |

## How it is built

```
video/src/
  script.py            narration text, split into scenes and "beats"
  tts.py               Kokoro TTS -> per-beat audio + timeline.json (beat timings)
  tl.py                scene-local timing helpers (beats and word timing)
  bl.py                Blender helpers: Workbench look, geometry, keyframes, label anchors
  models.py            geology diorama, strata, casing strings, ocean surface
  equipment.py         wellhead, BOP (with working rams), riser, christmas tree, manifold,
                       ROV, semi-submersible rig, FPSO, PDC bit
  textures.py          procedural lithology textures (sandstone dots, shale dashes, chalk bricks)
  gfx.py / overlays.py cairo toolkit: labels, charts, titles, icons, map inset
  well2d.py / schem.py 2D well schematics and barrier envelopes
  charts.py            the drilling-window chart
  scenes/sNN_*.py      one file per scene: build() for the 3D layer, draw() for the 2D layer
  run_blender.py       builds a scene in Blender, exports label anchors, renders frames
  render_daemon.py     background render queue
  compose.py           background + 3D frames + overlays -> one video segment per scene
  audio.py             procedural music bed, sound effects, ducking mix
  build.py             concatenation, soundtrack, chapters, subtitles
```

Animation is driven by the narration. Each scene reads the start and end times of its beats, and estimates
the time of individual words, from `timeline.json`. Change a line in `script.py`, rerun `tts.py`, and the
animation follows the new timing.

### Rebuilding

Requirements: Python 3.11, `bpy` (Blender 5.0 as a Python module), `pycairo`, `numpy<2`, `pillow`,
`soundfile`, `kokoro-onnx` (plus the `kokoro-v1.0.onnx` and `voices-v1.0.bin` model files), and `ffmpeg`.

```bash
cd video/src
python3 tts.py                       # narration + timeline
python3 textures.py                  # lithology textures
python3 run_blender.py s06_rig       # render one scene's 3D layer (repeat for 3D scenes)
python3 build.py segments            # composite every scene into video/build/segments
python3 audio.py                     # music + SFX + narration mix
python3 build.py final               # final MP4, chapters, subtitles
```

Tips:
- To preview single frames: `python3 run_blender.py <scene> --still 120 480`, then
  `python3 compose.py <scene> --png 120 480`.
- To change the voice, set `WELL_VOICE`, for example `bm_george`, and optionally `WELL_SPEED`,
  then rebuild.

## Technical notes

- The well is a generic NCS subsea well in about 350 m of water with a sandstone reservoir about 3 km
  below the seabed. The casing programme is 30″ / 20″ / 13⅜″ / 9⅝″ with a 7″ liner.
- The pressure profiles, depths and sizes are representative teaching values, not data from a real well.
- Diameters are exaggerated in the cutaways so that the hardware is readable. Depth is compressed where
  noted.
- Barrier envelopes follow the NORSOK D-010 convention: primary in blue, secondary in red.
