# Into the Live Well

A 37-minute narrated animation on **well intervention**: why we go back into a producing well, and how. It is a companion to
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
| 2 | Seven reasons to go back in: see, secure, clear, stimulate, lift (gas lift, the gas-lift valve, unloading), steer, finish | 4:27 | 6:17 |
| 3 | The airlock: working in a live well (lubricator, tree valves, stuffing box and grease head, the pressure force, barriers) | 10:45 | 3:55 |
| 4 | Wireline: the thin line that does the work (slickline, braided line, electric line; toolstring; jars; setting plugs; kick-over tool; perforating; the limits in deviated wells) | 14:40 | 7:17 |
| 5 | Coiled tubing: a pipe on a reel (reel, injector, stripper, BOP; balance point; fatigue; lock-up; cleanouts; nitrogen; acid; milling; other jobs) | 21:57 | 6:57 |
| 6 | Beyond the coil: snubbing, bullheading, and the rig workover | 28:55 | 2:10 |
| 7 | Subsea: riserless and riser-based light intervention from a vessel | 31:06 | 3:02 |
| 8 | Choosing a method, and closing the well (capability matrix; three worked cases; where the field is moving) | 34:09 | 2:27 |

Total runtime 36:37, about 5,700 words of narration.

## Version 2: what changed

After the first cut, every beat was reviewed for accuracy and for how well the picture explains the mechanism. The weakest
animations were rebuilt on a new procedural drawing layer (`scenes/common/pdraw.py`), with mechanisms whose parts move along
computed paths instead of keyframed rectangles:

* **Gas lift, end to end** (`scenes/common/gaslift.py`). A side-pocket mandrel with its orienting sleeve (helix and slot),
  latch lug, seal bores and annulus ports; an injection-pressure-operated valve with its nitrogen dome, bellows, ball and seat,
  packings and reverse-flow check valve; and a kick-over tool with its orienting key, pivot arm and pulling or running tool.
  - **4.06, changing a valve**: run past the mandrel, pick up, the key rides the helix and turns the tool (plan view), the
    line tension jumps at the top of the slot, the arm kicks over, slack off onto the latch, jar down, jar up to shear, the
    arm folds through the sleeve; a live line-tension trace shows what the operator sees. Pulling and setting are two trips.
  - **2.06, gas lift**: the column too heavy for the reservoir, gas down the annulus through the operating valve; a cutaway of
    the valve opening; unloading from the top valve down; the check valve.
  - The same drawings now appear in 1.02 and in the 8.02 worked case.
* **3.05, barriers during a wireline job**: the production envelopes, then the job envelopes (the open safety valve and tree
  valves cannot count; the stuffing box closes the primary, the BOP belongs to the secondary, the tree is shared), the stack
  pressure test, and a failure.
* **4.04, jars**: a plain jar and a spring-catch jar in a toolstring stuck under sand, with a force-at-the-tool trace.
* **7.02, subsea trees**: vertical and horizontal trees as cutaways (valves in line vs on the side outlet; crown plugs).
* **5.10, nitrogen lift**: gas bubbling up through the column instead of a piston.
* **Narration fixes**: calcium carbonate scale forms as CO2 leaves the water; a valve change is two wireline trips; the lock-up
  remedies (larger, stiffer tube instead of a taper); the slip change at the snubbing balance point; access to a horizontal tree;
  the jar description now distinguishes plain and spring-catch jars.
* The header, term cards and badges now always draw above the content, and the header band hides tools running in from above.

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
