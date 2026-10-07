# Visual style guide (skia engine)

The film is drawn by `scenes/common/stage.py` (API) + `scenes/common/look.py` (how things look). Chapter modules only
call the Stage API; the look is applied automatically **by role**, inferred from the primitive and its palette colour.

## What the engine does for you
| You draw | It renders as |
|---|---|
| `rect` in `P.PANEL` / `P.PANEL2` (> 0.2 thick) | **card**: rounded corners, soft drop shadow, top-lit gradient, hairline border |
| `pill(...)` (shapes.py), badges | **pill**: fully rounded plate with shadow |
| `rect` in `P.STEEL`, `P.STEEL_DK`, casing greys | **steel**: cylindrical metallic gradient across the short axis |
| `rect`/`poly` in `P.ROCK`, `P.ROCK2`, `P.SEABED`, `P.SHALE` | **earth**: world-anchored grain + strata texture; `P.SAND`: speckled grain |
| `rect`/`poly` in `P.SEA` | vertical gradient with faint caustics |
| `rect` in a fluid colour (`MUD`, `KILL_MUD`, `CEMENT`, `SPACER`, `WATER`, `OIL`, `GAS`) | soft cylindrical sheen (cement: fine grain) |
| `rect` in `P.BG` | the open borehole (darker than the background) |
| thin `rect` (< 0.035) | hairline rule (grid, axis, tick) |
| `arrow(...)` | round-capped shaft + softened head; **glows** if the colour is an accent |
| `line(...)` ≥ 0.03 wide in an accent colour | **glowing curve**; `draw_on` shows a bright travelling tip |
| `circle` in an accent colour | **orb**: radial gradient + glow (bubbles, data points, alarms) |
| `text(...)` | Inter (sans = Medium, bold = SemiBold, big bold = Inter Display), JetBrains Mono for `kind="mono"`; soft shadow |

Accent colours: `PORE, FRAC, MUD, WARN, BAD, OIL, GAS, SAFE, WATER, COLLAPSE, PRIMARY_B, SECOND_B, KILL_MUD, NO_BADGE`.
Override the inferred role with `role=` on `rect/circle/poly/line` (`"card"`, `"pill"`, `"solid"`, `"flat"`, `"steel"`,
`"fluid"`, `"earth"`, `"glow"` for a glowing line, `"hair"`).

Automatic motion: anything that `fade_in`s and is text/card/pill also **slides up ~0.07** while it appears; `pop_in` uses
a gentle overshoot; moves/scales/camera use cubic ease-in-out; **every beat boundary is a 0.45 s dissolve**; chapters 1-9
open with a title card (`tl.intro` seconds, ~2.8 s) and every chapter fades to the bare background over its last 0.5 s.
`header()`, term cards, scope badges and the title card come from `furniture.py` (driven by the script) — do not
re-implement them in chapters.

## Motion helpers (new)
- `st.flow(pts, t0, t1, color, n=18, speed=0.8, r=0.045, z=0.5, jitter=0.0)` — particles streaming along a polyline.
  Use it for **any moving fluid**: circulation (down the pipe, up the annulus), cement displacement, gas migration,
  returns to the shakers. Prefer it over `loop_move` arrows.
- `st.ripple(x, y, t0, t1, color, period=1.2, r0=0.1, r1=0.9)` — expanding rings: alarms, pressure pulses, emphasis.
- `st.counter(x, y, t0, t1, v0, v1, fmt="{:.0f} bar", size=0.3, color=P.TEXT, kind="mono")` — a number that ticks
  from v0 to v1 (gauges, pit volume, pressures). Numbers must come from `well_model.py` / the narration.
- `st.measure(text, size, kind)` — real width in world units (use it to size plates and avoid overlaps).
- `look.wrap_to(text, size, max_width, kind)` — wrap text to a width.
- `st.camera(t0, t1, cx, cy, width)` — slow push-ins on the detail being discussed (width 16 = full frame).

## Layout zones (world units; canvas x -8..8, y -4.5..4.5)
- Header row: y > 3.95 (chapter tag + title at left, badges at right). Keep content below y 3.9.
- Well-so-far strip: x < -6.45. Keep content right of x -6.3.
- **Term cards**: top-right x > 3.25, y from 3.92 down; one card is ~1.0-1.3 tall, two stack to y ≈ 1.5. During a beat
  that defines terms (see `TERMS:` in the script), keep that zone free for the first ~9 s of the beat.
- **Subtitle band**: y < -3.75 (burned-in subtitles). Nothing important below y -3.7.
- Keep ≥ 0.15 clearance between labels and other elements; never let text overlap curves/geometry it does not label.

## Design rules
1. One idea per frame. Fewer, larger elements; generous spacing; align things to a clear grid.
2. Typography: titles 0.34-0.42 bold; labels 0.2-0.24; small notes ≥ 0.16 (TEXT_SCALE 1.18 is applied on top).
   Labels go on pills or sit in clear space; muted (`P.MUTED`) for secondary info.
3. Colour has ONE meaning everywhere (see `palette.py`): mud amber, cement light grey, spacer white, formation water
   blue, oil green, gas crimson, pore pressure light blue, fracture orange, safe window teal; D-010 barrier envelopes:
   primary blue outline, secondary red outline (barrier panels only). Never reuse a fluid colour for something else.
4. Things move because something physical moves: flows use `flow()`, pressures use `counter()`/charts, closing rams
   slide, cement rises. Static diagrams should still have life (a slow flow, a gentle camera push) but nothing gratuitous.
5. Sync to the voice: key animations to sentence starts `s = tl["x.yy"].sent; s[i]` so the picture shows what is being
   said *as* it is said. Do not hard-code absolute times that assume a beat length; use `b.start`, `b.end`, `b.dur`, `s[i]`.
6. Technical correctness beats prettiness: geometry, order of components, flow directions and numbers must be right.

## QA loop
```
.venv/bin/python scenes/render.py --chapter N --qa --res 960x540          # 2 stills per beat -> renders/qa/chNN/
.venv/bin/python scenes/render.py --chapter N --stills 12.5,40.2          # stills at chapter times
.venv/bin/python scenes/render.py --chapter N --beat N.05 --res 960x540   # one beat as an mp4 (check motion)
```
Open the PNGs (they are the truth). Check: overlaps, clipped text, empty frames, wrong colours, content in the subtitle
band or under the term cards, and that each frame matches the narration at that moment.
