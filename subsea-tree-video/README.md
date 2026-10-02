# The Subsea Christmas Tree – how it works

An 11-minute, narrated, animated lesson on how a subsea Christmas tree works, with the trees used on the
Norwegian Continental Shelf (NCS) as the running example. Built as a course asset: 1080p / 30 fps,
English narration, burned-in or soft captions, chapter markers.

| File | What it is |
| --- | --- |
| `out/subsea-tree_1080p.mp4` | Final video, 1080p / 30 fps, clean picture (soft subtitle track + 14 chapters), 92 MiB, −16 LUFS |
| `out/subsea-tree_1080p_captions.mp4` | Same video with captions burned in, for players that cannot show a subtitle track, 92 MiB |
| `out/subsea-tree_720p.mp4` | Light copy for quick sharing (soft subtitles + chapters), 40 MiB |
| `out/subsea-tree.srt` / `.vtt` | Captions (180 cues) |
| `out/poster.png` | Title-card still for the course platform |
| `out/subsea-tree_transcript.md` | Full transcript with chapter timestamps |
| `out/valve-cheat-sheet.pdf` | One-page A4 companion: valves, fail-safe logic, shutdown order, barriers, quiz answers |

## Storyline (11:17)

1. **Cold open** – 300 m down, a steel structure holds back a reservoir
2. **Learning objectives**
3. **The big picture** – wells, templates, flowlines, umbilical, host
4. **Four jobs** – control flow · isolate · inject & monitor · give access
5. **Anatomy of a vertical tree** – x-ray wipe from exterior to cut-away
6. **The fail-safe valve** – hydraulic gate valve, spring, "pressure on = open"
7. **Meet the valves** – PMV, PWV, choke, swab, annulus valves, crossover, chemical injection, DHSV
8. **How the valves are controlled** – MCS → umbilical → SCM → solenoid → DCV → actuator, sensors back, ROV override
9. **Two-barrier principle** – primary (blue) and secondary (red) barrier, NORSOK D-010
10. **Start-up and emergency shutdown** – with a "which valve first?" question
11. **Vertical or horizontal?** – installation, workover, Equinor's standard VXT, 7×5 / 7×7, flow module, weight
12. **On the Norwegian shelf** – Troll, Åsgard, Aasta Hansteen, Johan Castberg
13. **Check your understanding** – three questions with think-time
14. **Summary and sources**

## How it is built

Everything on screen is a pure function of the clock, so any frame can be rendered on any worker, in any order
(verified: out-of-order and in-order renders are byte-identical).

```
src/data/script.json      narration script (22 scenes / 105 beats)
tools/tts.py              Kokoro-82M (ONNX) text-to-speech -> build/narration.wav + src/data/timings.json
src/js/engine.js          GSAP paused timeline + per-frame animators, camera, flow-dot engine, SFX cue list
src/js/art/*.js           SVG art: valve, tree, well, DHSV, exterior, icons, map data
src/js/stages/*.js        one file per scene (all timed to word-level narration times)
tools/frame.mjs           render single frames / contact sheets for review
tools/dump-sfx.mjs        export sound-effect cues from the scene code
tools/audio.py            synthesised foley + ambient bed + voice mix, ducking, -16 LUFS master
tools/captions.py         SRT / VTT / ASS captions + chapter metadata from the word timings
tools/render.mjs          parallel Playwright (Chromium) renderer -> ffmpeg
tools/encode.sh           final two-pass, size-targeted encodes (clean, captioned, 720p) and poster
tools/cheatsheet.mjs      renders src/cheatsheet.html -> out/valve-cheat-sheet.pdf
tools/overlap-scan.mjs    QA: finds on-screen text that is covered by a line, label, ring or tag (whole video in ~90 s)
tools/overlap-report.py   QA: short list of the persistent findings from that scan
tools/qa.sh               QA of the final MP4: streams, chapters, loudness, sample frames
```

Rebuild from scratch:

```bash
npm install
pip install numpy scipy soundfile onnxruntime num2words fonttools brotli    # kokoro-onnx model files are fetched by tools/tts.py
python3 tools/tts.py                 # narration + word timings (only if script.json changed)
node tools/dump-sfx.mjs              # sound cues
python3 tools/audio.py               # audio mix  -> build/audio_final.wav
python3 tools/captions.py            # captions, chapters, caption font
node tools/render.mjs                # ~25 min on 4 cores -> build/render/video.mp4
bash tools/encode.sh                 # ~25 min; 92 MiB per 1080p file (TARGET_MB=140 for more headroom) -> out/*.mp4, poster
node tools/cheatsheet.mjs            # -> out/valve-cheat-sheet.pdf
```

Re-render only what changed: delete the matching `build/render/seg_XXXXXX.mp4.done` markers (each segment is 600 frames = 20 s)
and run `node tools/render.mjs` again.

Preview in a browser: `node tools/server.mjs 8080`, open `http://127.0.0.1:8080/src/index.html?play=1` and click once to start
(plays the narration in real time; `?t=123` jumps to a time, `tools/frame.mjs` renders stills and contact sheets).

## Content notes — please read before using in a course

A claim-by-claim sheet with the public pages consulted is in [`docs/fact-check.md`](docs/fact-check.md) — hand it to the reviewing SME.

* The research behind the script was done with public web sources (Equinor, Aker Solutions, the Norwegian Offshore
  Directorate, SPE JPT, World Oil, Offshore Magazine, Offshore Norge / NORSOK D-010). Several primary documents were not
  directly accessible during the build, so a **subject-matter expert should review** the following claims before release:
  * Norne (1997) as the first NCS field with horizontal trees
  * Equinor's standard vertical tree developed with Aker Solutions; the "7×5 / 7×7" naming (shown only as "named after bore sizes")
  * "Roughly half the weight of earlier trees" (attributed to Aker Solutions)
  * Troll Phase 3 (2021), Åsgard subsea gas compression (2015), Aasta Hansteen 1,300 m, Johan Castberg first oil March 2025 with 30 subsea wells
  * Shutdown order PWV → PMV → DHSV and "closes against the flow" wording (company procedures differ)
* The narration is a **synthetic voice** (Kokoro-82M, American English). Norwegian names (Equinor, Åsgard, Snøhvit, Johan Castberg,
  Aasta Hansteen, Norne, Aker, NORSOK) are spoken from hand-written pronunciations in `tools/lexicon.json`, which could not be
  auditioned by a Norwegian speaker during the build — listen once, and adjust the entries if a name sounds wrong
  (then rerun `tts.py`, `audio.py`, `captions.py`, `render.mjs`, `encode.sh`). For a human voice-over, keep the beat structure
  of `src/data/script.json`; the scene timings are read from `src/data/timings.json`.
* The tree, valve and facility drawings are **schematic**; facility layouts and field positions on the map are simplified.
* No company logos or branding are used. Add course branding in `src/index.html` / `src/css/style.css` (the HUD has free space top-right).

## Credits and licences

Fonts: Inter and JetBrains Mono (SIL OFL). Animation: GSAP 3. Map: Natural Earth via `world-atlas` and `d3-geo` (public domain / ISC).
Voice: Kokoro-82M (Apache-2.0), voice `af_heart`. Music, ambience and all sound effects are synthesised in `tools/audio.py` (no samples).
