# Into the Live Well

A 35-minute narrated animation on **well intervention**: why we go back into a producing well, and how. It is a companion to
the drilling-and-well film ("The Hole That Fights Back") and is written for the same viewer: a mechanical-engineering MSc
starting a rotation on the Norwegian continental shelf (NCS), who knows statics, fluids and materials but has not yet seen a
wellhead.

The film explains the **reasons** (seven of them) and the **methods** (wireline, coiled tubing, snubbing, bullheading, rig
workover, subsea light intervention from vessels) in detail, with the mechanics worked through: wire tension and the pressure
force that tries to blow a cable out of the well, jar impact, the balance point in a coiled-tubing string, helical buckling and
lock-up, fatigue on the reel.

Everything on screen is a 2-D animation drawn by code (skia). The voice is a neural text-to-speech voice (Kokoro-82M, run
locally). The music and sound design are synthesised. There are no stock clips, no samples and no licensed material.

## What you get

`make final` writes to `build/` (the folder is git-ignored because the files are large and reproducible):

| File | What it is |
|---|---|
| `into_the_live_well_1080p.mp4` | Full film, 1080p30, subtitles burned in |
| `into_the_live_well_1080p_nosubs.mp4` | Same, without burned-in subtitles |
| `into_the_live_well_1080p.srt` | Subtitles (also timed from the real speech) |
| `into_the_live_well_720p_partNofM.mp4` | Compact 720p parts for sharing in chat |
| `web/` | Web player (1080p HLS, chapter menu, subtitles on/off, speed); `make web`, then publish `web/index.html` with the other files beside it |

The 720p parts and the subtitles of the finished film are also committed in `out/` (six parts, about 26 MiB each, subtitles
burned in; play them in order). The 1080p masters are over GitHub's file-size limit and are rebuilt by `make final`.

Plain-text companions, generated from the script:

* `script/NARRATION.md`: the full narration with real timestamps, chapter by chapter.
* `script/FLAGS.md`: **the ledger of flagged claims** (see "What to check before relying on it" below).
* `script/glossary.yaml`: the ~65 terms that pop up as definition cards the first time they are spoken.

## Chapters

| # | Chapter | Starts | Length |
|---|---|---|---|
| 0 | Cold open: a well that is slowly dying, and no way in | 0:00 | 1:11 |
| 1 | The well, and the work after it (anatomy; intervention vs workover; light vs heavy; value) | 1:11 | 3:15 |
| 2 | Seven reasons to go back in: see, secure, clear, stimulate, lift, steer, finish | 4:27 | 5:49 |
| 3 | The airlock: working in a live well (lubricator, tree valves, stuffing box and grease head, the pressure force, barriers) | 10:16 | 3:38 |
| 4 | Wireline: the thin line that does the work (slickline, braided line, electric line; toolstring; jars; setting plugs; kick-over tool; perforating; the limits in deviated wells) | 13:55 | 6:29 |
| 5 | Coiled tubing: a pipe on a reel (reel, injector, stripper, BOP; balance point; fatigue; lock-up; cleanouts; nitrogen; acid; milling; other jobs) | 20:25 | 6:58 |
| 6 | Beyond the coil: snubbing, bullheading, and the rig workover | 27:23 | 2:10 |
| 7 | Subsea: riserless and riser-based light intervention from a vessel | 29:33 | 3:02 |
| 8 | Choosing a method, and closing the well (capability matrix; three worked cases; where the field is moving) | 32:36 | 2:27 |

Total runtime 35:04, about 5,400 words of narration.

## How it is built

```
script/chNN_*.md   one block per beat: VO text, SHOT description, FLAGS, TERMS, budget seconds
        |  script/scriptlib.py     lint, fit to budget, emit NARRATION.md / FLAGS.md / timeline.json
        v
audio/build_audio.py   Kokoro-82M (af_heart) speaks every sentence, paced to ~172 wpm; beat durations then follow
                       the speech (voice-first), and the real sentence start times are written to audio/sentences.json
        v
scenes/chNN_*.py   build(st, tl): drawings keyed to sentence starts, e.g. st.fade_in(obj, tl["4.05"].sent[3])
scenes/render.py   skia frame renderer (+ ffmpeg x264); every chapter is a whole number of frames
        v
audio/mix.py       pad + soft plucks + a whoosh on each title card + a tick on each term card, ducked under the voice
scenes/assemble.py concatenate chapters, loudness-normalise to -16 LUFS, mux, burn subtitles
```

Because the pictures are keyed to the measured sentence times, changing a sentence in the script moves the animation with it.

The numbers on screen come from one place, `scenes/common/model.py`, and the narration quotes the same figures (for example the
4.1 tonne pressure force on a 2 in coiled tube at 200 bar, or the balance point near 1,035 m for the example string).

### Rebuild

```
make venv            # skia-python, kokoro-onnx, onnxruntime, numpy, Pillow, PyYAML (needs ffmpeg with libx264 and libass)
make voice-model     # downloads the Kokoro voice and checks its SHA-256
make doctor          # what is missing, if anything
make final           # script -> audio -> mix -> render -> assemble -> web
make qa              # 3 stills per beat -> renders/qa/chNN/ for a quick visual check
make preview CH=5    # one chapter at 960x540
```

Order matters: `make script` rewrites `timeline.json` from the script budgets, and `make audio` re-times it from the real speech.
`make audio` runs both in the right order.

## What is, and is not, in the film

* **One composite well.** A 4,200 m MD well in a 300 m water-depth setting, with a gas-lift completion (three side-pocket
  mandrels), a sliding sleeve, packer, landing nipple, perforations and a safety valve. It is invented for teaching. It is not a
  real well and no operator's data is used. The depth axis is compressed and diameters are exaggerated in the pictures.
* **Norway-specific points** carry a red NORWAY badge; general-practice points carry none. Simplifications carry a yellow SIMPLIFIED badge.
* **Method coverage:** slickline, braided line, electric line (incl. tractors and perforating), coiled tubing (incl. nitrogen,
  acid, milling, drilling), snubbing, bullheading, rig workover, riserless and riser-based light well intervention.
  Hydraulic fracturing is mentioned as a reason, not worked through. Well testing, plug and abandonment design and well control
  calculations are out of scope.

## What to check before relying on it

This film is a teaching aid, not a procedure and not engineering advice. The following limits matter:

1. **Primary sources were not available.** Norwegian regulations (Activities, Facilities regulations), NORSOK D-010, API
   standards for coiled-tubing and wireline equipment and operator-specific procedures could not be read in full. Claims that
   depend on them are marked **VERIFY** (paraphrased from secondary summaries) or **SEEN** (confirmed in one web source) in
   `script/FLAGS.md`, with the exact sentence. Check those against the documents before you quote the film.
2. **Numbers are illustrative.** Forces, depths, flow rates, durations and costs are computed from a simple model of the composite
   well so that voice and picture agree. They are marked **SIM**. The cost ladder on the capability matrix is an ordering only.
3. **The capability matrix is qualitative.** Real limits depend on equipment size, rating and the particular well.
4. **Simplified mechanics.** The kick-over tool, the stripper, the injector and the BOP stack are drawn as working cutaways, not
   as any manufacturer's design. Vendor names and product names are not used.
5. **Voice.** The narration is synthetic. Some technical words may be pronounced oddly. The subtitles show the intended text.

## Repository layout

```
script/      narration source, glossary, linting and timing tool, generated NARRATION.md / FLAGS.md / timeline.json
scenes/      common/ (stage engine, look, kit, tools, insets, model) and one module per chapter
audio/       build_audio.py (TTS + timing), mix.py (music + SFX), subtitles.py; models/ and caches are git-ignored
renders/     frames and chapter videos (git-ignored)
build/       final deliverables (git-ignored)
```
