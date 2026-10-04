# Stage 1: Research outline, chapter timings, environment audit

**Working title:** *The Hole That Fights Back*: how an offshore exploration well is drilled, judged, and erased
**Runtime target:** 30:00 · **Narration budget:** ≈ 4,200 words (≈ 140 wpm including pauses for visuals)

> **Status: awaiting your approval.** Nothing is committed. Sections 6–7 list what I need from you.

---

## 1. Environment audit

| Need | Status | Notes |
|---|---|---|
| **Blender** | **Binary missing.** `bpy` 4.5.14 LTS *works* via pip | `pip install bpy` succeeded on Python 3.11 (950 MB venv, scratch only, nothing system-wide). `download.blender.org` is blocked; Ubuntu apt offers Blender 4.0.2 as a fallback. Not tested: bpy 5.0.x. |
| **GPU** | **None** (4 vCPU, 15 GB RAM) | Cycles = CPU only. EEVEE runs under `xvfb-run` with software GL. |
| **ffmpeg / ffprobe** | OK, 6.1.1 | libx264, libass (subtitles), drawtext, xfade, loudnorm, minterpolate all present. |
| **Python** | 3.11.15 | `numpy`, `matplotlib`, `Pillow` missing (pip-installable; PyPI reachable). `PyYAML` present. |
| **TTS** | **None installed.** | `espeak-ng` is apt-installable (robotic; fine as a timing placeholder). Neural voices (Piper, Kokoro, Coqui) need model downloads from HuggingFace (**blocked**) or GitHub Releases (the one Piper page I tried returned **403**; `raw.githubusercontent.com` does work). So I don't expect to produce a natural-sounding voice *in this sandbox* (see decision D3). |
| **Fonts** | DejaVu, Liberation, FreeSans | Adequate. `fonts-inter` is apt-installable if you want a nicer look. |
| **Primary sources** | **`havtil.no`, `sodir.no`, `standard.no` blocked** | I could only read search-result summaries, not NORSOK D-010 or the regulations. See `script/00_sources.md` §E. |

### Render benchmark (toy scene, 1080p, 4 CPU cores)

| Engine | Time / frame | Verdict |
|---|---|---|
| Cycles, 16 spp + denoise | ≈ 14 s | Photoreal is out of reach: 30 min × 24 fps = 43,200 frames ≈ **170 h** |
| Cycles, 64 spp | ≈ 33 s | Hero shots only, if at all |
| EEVEE (software GL), 8 samples | ≈ 5.4 s steady (9.6 s first frame) | Proper transparency and soft shading; ≈ 16–30 h for the 3D share of the film |
| **Workbench** (flat shading + outlines) | **≈ 0.7 s** | ≈ 2–6 h for the 3D share. Alpha blending renders but looks flat; needs a real test in Stage 4 |

*Caveat: the benchmark scene is trivial. Real scenes (many casing strings, particles, text) will be several times slower. Treat these as order-of-magnitude.*
The cloud container is also **ephemeral**, so multi-hour renders should be per-chapter, resumable, and probably done on your own machine (decision D4).

**Planning consequence:** I propose a *technical-illustration* look (flat, outlined, schematic cutaways), with ~50 % of runtime as 3D animation (rendered at 12 fps and frame-doubled where motion allows) and the rest as 2D charts, schematics and title cards. This is also better for explaining: nothing decorative competes with the mechanism.

---

## 2. Framing

**Central question (stated at ≈ 1:20):**
*How do you drill 4 km below the seabed through rock that is trying either to collapse or to blow out, and then leave the hole so safe that nobody ever has to think about it again?*

**Protagonist: the pressure window.** Every chapter returns to one chart: pore pressure on the left, fracture pressure on the right, mud weight forced to live in between. Each chapter *changes the same chart*: planning draws it, casing seats reset it, ECD squeezes it, a kick falls out of it, pressure measurements redraw it, P&A makes a permanent version of it.

**Recurring devices (identical visual language in every chapter):**
1. **Depth ruler + "well so far" schematic** pinned at screen left. It grows chapter by chapter, so the viewer always knows *where* in the well we are.
2. **Predict-then-reveal beats**: "Pause and guess…". ≥ 1 per chapter, 3 s of silence.
3. **Analogy first, then equation**: the equation always appears *after* the viewer has the picture; never before.
4. **Tag badges (on-screen and in the script):** **[NO]** = Norway/NCS-specific (NORSOK D-010, Havtil/Sodir rules); **[GEN]** = general industry; **[SIM]** = deliberate simplification (spoken or captioned: "simplified"); **[VERIFY]** = I'm not sure (script-only, never shipped).
5. **Bookend:** open on an empty seabed; close on the same empty seabed.

**Illustrative well (composite, *not* a real well):** a North Sea wildcat, ~300 m water depth, TD ≈ 4,200 m TVD, Jurassic sandstone target, reservoir pore pressure ≈ 1.5-1.6 sg (EMW), ~140 °C. One Python data module will hold depths/pressures/casing seats and feed **both** the charts and the Blender scenes so they can never disagree. All numbers `[SIM]`, finalised in Stage 2.

**Units:** NCS convention (bar, sg, m), casing sizes in inches (industry-wide, even in Norway); a one-time "Rosetta" card for psi/ppg since most literature uses them.

**Voice:** "we" narration, curious, one idea per sentence, jargon *named* on first use and *defined in the same breath*.

---

## 3. Chapter timings (sums to 30:00)

| # | Chapter | Start | Length | Core idea |
|---|---|---|---|---|
| 0 | Cold open: the window | 0:00 | **1:30** | A hole has two ways to die; the gap between them can be razor-thin |
| 1 | Planning: casing from the bottom up | 1:30 | **4:00** | Pressures dictate casing seats; start at TD and walk upward |
| 2 | Top hole: drilling with no safety net | 5:30 | **3:15** | Riserless, spud, conductor, surface casing, cement, wellhead |
| 3 | BOP, riser, and the closed loop | 8:45 | **2:00** | Closing the system gives you a pressure *knob*, and a test of reality (LOT) |
| 4 | Drilling the deep sections | 10:45 | **3:00** | BHA, steering, mud, ECD: pumping changes the pressure; MPD concept |
| 5 | Casing & tubular design | 13:45 | **2:45** | Burst, collapse, tension, von Mises; threads that must not leak |
| 6 | Cementing | 16:30 | **2:30** | Pumping a liquid that becomes the seal; how we check it worked |
| 7 | Well control & barriers | 19:00 | **3:15** | Kick → shut-in → kill; two independent barriers (NORSOK D-010) |
| 8 | Formation evaluation: discovery or dry? | 22:15 | **4:00** | Mud log → LWD → wireline → pressures → core → DST → verdict |
| 9 | Plugging & abandonment | 26:15 | **3:15** | Turning a hole back into rock, "rock-to-rock", and proving it |
| 10 | Outro: the empty seabed | 29:30 | **0:30** | The win must be permanent |
| | **Total** | | **30:00** | |

**Cut list if the first script overruns** (dropped in this order): wellhead fatigue sidebar (Ch 2) → riser margin (Ch 3) → thermal derating (Ch 5) → DST detail (Ch 8) → kick-tolerance derivation (Ch 7).

---

## 4. Chapter-by-chapter outline

Format per chapter: **Beats**, **Wait, why?**, **Analogy → equation**, **Animation** (explains, not decorates), **Terms introduced**, **Standards / scope flags**, **Simplifications**, **To verify**.

### Ch 0: Cold open: the window (0:00-1:30)

- **Beats:** Empty seabed, calm. Hook puzzle: a drilled hole is full of liquid whose weight you choose. Too light → the rock pushes fluid in (a *kick*, then blowout). Too heavy → you break the rock and lose the fluid (then the level falls and you're too light). In deep, hot, high-pressure wells the gap between those two limits can shrink to a few hundredths of a sg `[VERIFY: typical HPHT window width on the NCS]`. State central question. Roadmap in one sentence: "we'll follow one well from first metre to last plug".
- **Wait, why?** The hook *is* the wait-why: "why can't you just make the mud heavier to be safe?"
- **Analogy → equation:** Divers feel ~1 bar per 10 m. Mud is just *heavier water you get to choose*. Equation withheld until Ch 1.
- **Animation:** Slow camera down from the sea surface to a bare seabed; a 2-sided gauge needle (collapse ↔ fracture) with the mud weight marker squeezed between.
- **Terms:** *well*, *spud* (teased), *kick*, *mud weight* (informal).
- **Flags:** [GEN]. The hook uses physics, **not a real incident** (see D6).

### Ch 1: Planning: casing from the bottom up (1:30-5:30)

- **Beats:**
  1. The *target*: a point in 3-D with a geological reason (others found it; we're told *what* and *how deep*). Explain MD vs TVD in one line.
  2. **Pressure intuition.** Hydrostatic = ρ g h. **Pore pressure** = pressure of fluid in rock pores. "Normal" = a brine column connected to the sea. **Overpressure** = trapped fluid carrying weight the grains should carry.
  3. **Terzaghi piston-and-spring** analogy (a mech. engineer's picture): load on a perforated piston over a water-filled spring cylinder, where water carries the load first and then slowly hands it to the spring. → *effective stress* σ′ = σ − p.
  4. **Fracture gradient**: the hole-wall stress concentration (Kirsch, 2-3× far-field, like a hole in a plate) plus internal pressure from the mud; the rock *cracks* when mud pressure beats the smallest compressive stress plus tensile strength; it *shear-collapses* when the mud is too light. Measured by the **leak-off test (LOT)**, preview only; shown properly in Ch 3.
  5. **The window chart** (pore/collapse left, fracture right, margins), and why it narrows with depth in overpressured basins.
  6. **Shallow hazards**: shallow gas, boulders/glacial till, seabed features, soft soil (shallow water flow is mainly a Gulf of Mexico issue; mention, then drop) `[VERIFY: NCS-relevant shallow hazards list]`. Site survey.
  7. **Bottom-up casing design.** Start at TD: mud weight needed at TD is X. Draw a vertical line up at X until it hits the fracture curve (minus margin). Above that depth the open hole *cannot be left uncased*. So a shoe must be set below it. Now the section above must be drilled with *its* lower mud weight … repeat to the top. Result: a stair-step.
  8. **Why strings telescope**: each string must pass *through* the one above, so every extra string costs hole diameter. 36″/30″ → 26″/20″ → 17½″/13⅜″ → 12¼″/9⅝″ → 8½″/7″ liner is the standard ladder `[GEN, memory]`. **Wildcat twist:** no offset data → pressure prediction is uncertain → plan *contingency* strings (and larger top-hole) up front.
  9. Plan the exit before the entry: P&A scheme and relief-well plan exist before spud `[NO: VERIFY requirement and section]`.
- **Wait, why?** "Why can't we use one big pipe?" and "Why does the earth get *harder* to drill safely the deeper you go, when rock gets stronger?" (because pore pressure grows *faster* than the stress that resists fracture in overpressured rock).
- **Analogy → equation:** Piston-spring → σ′ = σ_v − p. Eaton: FG = (ν/(1−ν))(σ_v − p) + p, introduced as "the fraction of the squeeze that the rock passes sideways".
- **Animation (core one):** *Mud weight window vs depth*. Pore-pressure and fracture curves draw down the screen; the mud weight line tries to stay in; at the depth where it hits the fracture curve, a casing string telescopes down to that depth, the usable window *resets*, the line steps right; repeat. Casing strings telescope in a side column in sync.
- **Terms:** target, TVD/MD, hydrostatic, pore pressure, overburden, effective stress, fracture gradient, EMW (sg), overbalance, kick, losses, casing shoe/seat, LOT/FIT, shallow gas, contingency string.
- **Standards:** [NO] NORSOK D-010 (design basis; well-barrier design), Activities Regs.; [GEN] ISO 16530-1, API RP 65-2, Aadnøy *Modern Well Design*, Eaton 1969.
- **Simplifications:** [SIM] lower bound drawn as pore pressure only (really max of pore pressure and collapse pressure); no kick tolerance in the first pass (only a margin line).
- **To verify:** D-010 wording on shoe strength / kick margin and design basis; typical NCS HPHT window width; whether the relief-well/P&A-planned-up-front requirement is in D-010 or the Regs.

### Ch 2: Top hole: drilling with no safety net (5:30-8:45)

- **Beats:**
  1. **Riserless drilling.** No BOP, no riser; drill string alone in the sea; fluid returns spill out at the seabed (*pump-and-dump*). Seawater as fluid, high-viscosity sweeps to clean the hole; a heavier *kill-mud* pill is spotted before pulling out.
  2. **Spud**: first metres. A *guide base* on the seabed orients everything that follows.
  3. **Conductor (30″/36″).** Two ways: jet it in, or drill and cement it. The conductor is *a pile in mud* carrying the wellhead, and later the BOP, and bending loads from the riser. (Mech-eng hook: a few-hundred-tonne BOP on a pile in soft clay.)
  4. **26″ hole, 20″ surface casing + 18¾″ high-pressure wellhead housing.** Cemented to the seabed with returns visible on ROV `[VERIFY: practice in current NCS]`. Cement support = structure + isolation of shallow zones.
  5. **Wellhead = nested seats**: housings, casing hangers, seal assemblies. This is the first pressure-containing, load-carrying hardware.
- **Wait, why?** *"We drill the first ~1 km with nothing that can close the well. Why is that allowed?"* Because (a) overburden here is mostly seawater → shallow fracture pressure is tiny, so a closed-in kick would simply fracture to the seabed; (b) a BOP needs a casing strong enough to attach to; (c) shallow-gas risk is managed *before* spud by survey and pilot-hole practice, not by closing in.
- **Analogy → equation:** Foundation pile (soil friction ↔ axial capacity, p-y behaviour ↔ lateral). No new equation; keeps the Terzaghi/FG picture alive.
- **Animation:** Riserless cutaway: cuttings plume at the seabed; conductor lowered and "driven" in soft soil; 20″ landing with wellhead housing seating *into* the 30″ housing; cement fills the annulus from the shoe upward and exits at the seabed.
- **Terms:** riserless, spud, returns, sweep, pump-and-dump, kill-mud, guide base, conductor, jetting, surface casing, annulus, wellhead housing, casing hanger, top of cement.
- **Standards:** [GEN] API Spec 6A/17D (ISO 10423 / 13628-4), API RP 65-2; [NO] shallow-gas site-survey expectation, and **how D-010 treats the barrier status of the riserless top hole**.
- **Simplifications:** [SIM] one composite top-hole sequence; depths illustrative; TGB/PGB detail dropped.
- **To verify (high priority):** **Does D-010 permit the riserless top hole to rely on a single (fluid) barrier, and under what conditions?** (I believe there is a specific treatment but don't know the wording.) Also whether a "Norwegian shallow-gas blowout" story is real (D5), and typical NCS 20″ shoe depth.

### Ch 3: BOP, riser, and the closed loop (8:45-10:45)

- **Beats:**
  1. Run the **BOP + marine riser** and latch onto the wellhead: the well becomes a **closed system**.
  2. BOP anatomy by *function*: annular (squeezes anything), pipe/variable-bore rams (grip pipe), blind shear ram (cut pipe and seal, last resort); choke and kill lines; stored hydraulic energy (accumulators: "pre-charged gas springs") so it can close without power.
  3. **Test it**: pressure and function tests before it's trusted: no tested barrier = no barrier.
  4. **Closed loop**: returns now come *up the riser* to the rig where flow in vs flow out is measured. Why that matters: (i) mud weight becomes a knob, (ii) volume balance is the best kick detector, (iii) the BOP can shut the system.
  5. **Drill out the shoe track and do the LOT/FIT**: first *measured* fracture strength in this well; a pressure-vs-volume plot (linear elastic → leak-off, like a stress-strain curve). It reconciles the model with the rock.
- **Wait, why?** "A subsea BOP is rated for ~1000 bar (15,000 psi class, `[memory]`) but tested to a specific number, so what exactly are you proving?" (sealing + function + the wellhead/casing it sits on).
- **Analogy → equation:** Check valves + stored-energy actuators (familiar subsea hardware); LOT curve ↔ stress-strain. No new equations (LOT pressure → equivalent mud weight is just ρ = P/(g·h)).
- **Animation:** **BOP closing**: annular element squeezing around pipe, rams sweeping in, shear ram cutting a pipe section and sealing, shown at the stack cutaway; then an LOT plot filling in real time next to the shoe.
- **Terms:** BOP, ram, annular, shear ram, LMRP, marine riser, choke/kill line, accumulator, closed loop, flowline, trip tank, shoe track, LOT/FIT.
- **Standards:** [GEN] API Std 53, API Spec 16A/16D, API RP 16Q; [NO] D-010 requirements on BOP configuration, test pressure and test interval; D-001 (drilling facilities). **All numbers `[VERIFY]`.**
- **Simplifications:** [SIM] rig-side systems (control pods, diverter, riser tensioners) omitted by scope; riser margin dropped (cut list).
- **To verify:** BOP test interval and test-pressure rule in D-010 (I recall 14-21 days; not sure); shear-ram redundancy expectation on NCS.

### Ch 4: Drilling the deep sections (10:45-13:45)

- **Beats:**
  1. **BHA** bottom-up: bit (PDC shears like a lathe tool; roller-cone crushes), steering tool, MWD/LWD, stabilisers, collars. *You drill by pulling*: the drill pipe hangs in tension and the heavy collars push (a slender column in compression would buckle).
  2. **Directional drilling basics**: why deviate (target offset, collision avoidance, geological sidetracks, relief wells); **motor with bent housing** (slide = steer, rotate = go straight) vs **rotary steerable** (steers while rotating). **Dogleg severity** = curvature. Drag in a curved hole behaves like rope on a capstan (T₂ = T₁ e^{μθ}). Survey uncertainty ellipse grows with depth.
  3. **Mud as the hardest-working component**: hydrostatic barrier, hole cleaning (shear-thinning rheology), cooling/lubrication, wall support, signal path. WBM vs OBM/SBM; barite as weighting (and barite sag in deviated, hot holes).
  4. **ECD**: *pumping adds friction pressure in the annulus, so bottom-hole pressure is higher when pumping than when stopped.* Every connection (pumps off) drops it; tripping pipe swabs/surges it. So the *usable* window = [pumps-off BHP > pore] and [pumps-on ECD + surge < fracture].
  5. **MPD (concept)**: close the annulus at the surface with a rotating control device and a choke; apply back pressure when pumps stop → hold bottom-hole pressure constant. "Add a pressure knob so mud weight isn't the only one."
- **Wait, why?** *"The well is safest while you're pumping, and most vulnerable the moment you stop to add a pipe."* And: *"You can run out of window before you run out of hole: pushing enough fluid to clean cuttings can fracture the rock."*
- **Analogy → equation:** Garden hose with a clogged nozzle, *in reverse*: friction in the annulus pushes back on the bottom. → ECD = MW + ΔP_ann /(0.0981·TVD) (sg, bar, m).
- **Animation:** Cutaway annulus with a bottom-hole pressure gauge: pumps on (BHP up), pumps off at a connection (BHP drops to MW alone), window bars squeezing; then MPD: choke closes as pumps stop and BHP stays flat.
- **Terms:** BHA, bit, PDC, WOB, ROP, MWD/LWD, mud motor, RSS, inclination/azimuth, DLS, rheology, barite, WBM/OBM, ECD, swab/surge, connection, trip, MPD, RCD, back pressure.
- **Standards:** [GEN] API RP 7G (ISO 10407), API RP 13B/13D, ISCWSA error model, IADC MPD definitions; [NO] D-010 treatment of MPD as barrier-system `[VERIFY: whether Rev 5 has a dedicated MPD section]`; **environmental constraints on OBM cuttings discharge are [NO] regulation** (permits), kept to one line.
- **Simplifications:** [SIM] Newtonian-ish ECD formula (real: Herschel-Bulkley hydraulics); torsional/axial vibration and stick-slip not covered; MPD variants (CBHP/PMCD/DGD) collapsed to one concept.
- **To verify:** NCS drilling-fluid discharge rules; Equinor/NCS MPD usage statement (don't claim any specific field).

### Ch 5: Casing & tubular design (13:45-16:30)

- **Beats:**
  1. Casing = **tunnel lining**: structure, pressure containment, isolation, guide for later strings.
  2. **Grades**: the number is minimum yield in ksi (P110 → 110 ksi ≈ 758 MPa); sour-service grades (hardness limits, ISO 15156).
  3. **Three failure modes, three mechanics:** *burst* = internal pressure, Barlow/Lamé-type yield (API rating includes the 12.5 % wall tolerance: 0.875·2Y·t/D); *collapse* = **external-pressure buckling**, governed by D/t (four regimes: yield, plastic, transition, elastic, like a soda can crushed from outside); *tension* = body yield vs **connection** strength.
  4. **Load cases (design basis):** burst (gas kick shut-in, pressure test), collapse (full/partial evacuation, cementing differential), tension/compression (running, overpull, landing, thermal).
  5. **Triaxial / von Mises:** API ratings are *uniaxial*; real pipe sees axial + radial + hoop together. The **VME ellipse** in axial-force vs differential-pressure space; tension *reduces* collapse resistance, compression reduces burst. **Design factor** = yield / σ_vme.
  6. **Connections**: API threaded-and-coupled (needs thread compound to seal) vs premium **metal-to-metal gas-tight** with torque shoulder; qualified by ISO 13679 application levels; make-up checked by **torque-turn** plots.
  7. Each string is also a **well barrier element** with an acceptance table (pressure test / documented design).
- **Wait, why?** *"Casing is weakest in collapse exactly where it is strongest in tension demand…"*: the top of a string carries the highest tension (which cuts its collapse capacity) while pressure loads grow with depth. Hence **tapered strings** (heavier wall/higher grade where needed).
- **Analogy → equation:** Soda can crushed by outside pressure → collapse regime curve; then σ_vme = √½[(σ_a−σ_t)² + (σ_t−σ_r)² + (σ_r−σ_a)²] (the audience already knows it; just map it to this pipe).
- **Animation:** The **VME design ellipse** appears and *tilts/shrinks* as tension is added; load-case points (burst, collapse, tension) plotted inside/outside with a design-factor shrink. Torque-turn curve with shoulder detection.
- **Terms:** grade, yield (ksi), wall thickness, D/t, burst/collapse/tension, biaxial/triaxial, VME, design factor, coupling, premium connection, torque-turn, tapered string.
- **Standards:** [GEN] API Spec 5CT/ISO 11960, **API TR 5C3 / ISO 10400**, ISO 13679/API RP 5C5, ISO 15156; [NO] D-010 requirement that casing has a documented design; **design factors are operator-specific (Equinor internal), not NORSOK**. `[VERIFY]`.
- **Simplifications:** [SIM] design factors quoted only as "typical ranges, operator-specific"; thermal derating and annular pressure build-up omitted; fatigue only mentioned for wellhead/conductor.
- **To verify:** that D-010 does *not* itself fix design factors; ISO 10400 edition/year; premium-connection CAL levels naming.

### Ch 6: Cementing (16:30-19:00)

- **Beats:**
  1. **Why cement:** support, **zonal isolation** (it is the annular barrier), corrosion protection.
  2. **Placement, the U-tube:** pump down the *inside*, up the *outside*. Fluid train: **spacer** → **lead** (light) → **tail** (dense/strong), separated from mud by **bottom/top plugs** (think pipeline pigs). **Float equipment** stops the heavy cement from U-tubing back. **Bumping the plug** (pressure rise) = displacement complete.
  3. **Displacement quality:** the narrow side of an eccentric annulus is where mud is left behind (**channeling**) → **centralisers**, pipe movement, density/rheology hierarchy.
  4. **The window again:** cement column ECD must stay below fracture, so lightweight lead slurries.
  5. **Slurry design:** thickening time, strength development (**UCA**), fluid loss; high-temp strength retrogression → silica flour above ~110 °C `[GEN, memory]`.
  6. **The danger hour:** as cement transitions from fluid to gel to solid it **stops transmitting hydrostatic pressure before it becomes impermeable**, so gas can migrate in. (Simplified; real model uses static gel strength.)
  7. **Evaluation:** **CBL/VDL** (sonic amplitude of casing arrival → bond) and **ultrasonic** pulse-echo/flexural tools (360° maps, can tell solid from liquid/gas). Pitfalls: **microannulus**, light cement, eccentred tool. *A quiet log is not the same as a seal.* Other evidence: returns, volumes, bump pressure, shoe LOT.
- **Wait, why?** "Why pump cement the hard way round?" and "why can a good-looking log still hide a leak path?"
- **Analogy → equation:** Pipeline pigs & check valves (subsea-native); toothpaste-tube displacement. Minimal equations: slurry density vs window (hydrostatic again).
- **Animation:** **Cement displacement:** fluid fronts rising in an *eccentric* annulus (wide side leading, narrow side lagging; then the same with centralisers → even). Built from independently advancing angular sectors (explanatory, not a fluid sim). Then a CBL/VDL panel scanning a good vs a channeled interval.
- **Terms:** cement, slurry, annulus, TOC, spacer, lead/tail, wiper plug, float collar/shoe, centraliser, displacement, channeling, thickening time, UCA, compressive strength, CBL/VDL, ultrasonic log, microannulus.
- **Standards:** [GEN] API Spec 10A/ISO 10426-1, API RP 10B-2/ISO 10426-2, API RP 10D-2/ISO 10427-2, API RP 65-2, Nelson & Guillot; [NO] D-010 cement as WBE: **required cement height/length and accepted verification methods `[VERIFY]`**, no numbers until read.
- **Simplifications:** [SIM] single-stage job only; foam/expanding cements and multi-stage tools omitted; displacement shown as sector heights, not CFD.
- **To verify:** D-010 casing-cement acceptance criteria (length above shoe/zone, logging basis); gel-strength numbers (will not quote).

### Ch 7: Well control & barriers (19:00-22:15)

- **Beats:**
  1. **If the window lies:** a **kick** is formation fluid entering the well (BHP < pore pressure). Causes: mud too light, swabbing, losses (level drop), not filling hole on trips.
  2. **The kick grows when it rises:** gas expands by *hundreds of times* from bottom to surface (Boyle). **In oil-based mud, gas dissolves and hides until it flashes near the surface.**
  3. **Detection:** flow-out > flow-in, pit gain, flow with pumps off (**flow check**), drilling break, pump-pressure/stroke changes.
  4. **Barrier philosophy** [NO]: **two independent barriers** at all times; *well barrier element* (WBE) vs *well barrier envelope*; **primary** = drilling-fluid column, **secondary** = casing + cement + wellhead + BOP (typical drilling schematic). **Independence = no shared hinge** (airlock analogy: two doors, never both open). A barrier must be **tested/verified** before use. If one fails, only work to restore it continues.
  5. **Shut-in:** stop, space out, flow-check, close BOP, read **SIDPP/SICP**. The drill pipe is a U-tube manometer: **pore pressure = hydrostatic in pipe + SIDPP.**
  6. **Kill:** kill-mud weight = old MW + SIDPP/(0.0981·TVD). **Driller's** (two circulations) vs **Wait-and-Weight** (one); **volumetric** and **bullheading** noted. **Subsea twist:** friction in the long choke line adds to BHP during circulation. **Shoe pressure peaks as the gas reaches the shoe** → **MAASP**/**kick tolerance** ties back to Ch 1.
  7. Story slot: one *verified* incident, **chosen with you (D6)**, tying barrier failure to a cement or verification failure.
- **Wait, why?** (a) "A 1 m³ kick is harmless at the bottom and a monster at the top." (b) "Why can't the drill pipe pressure just tell you the formation pressure?" (it *does*, via the U-tube).
- **Analogy → equation:** Soda bottle/gas expansion; U-tube manometer; airlock doors. → P = ρ g h reused; KMW formula.
- **Animation:** **Kick propagating up the annulus**: bubble starts small at depth, grows as it rises, pit-gain trace + annulus pressure + shoe pressure trace in sync; BOP closes (reuse Ch 3 asset); U-tube pressure diagram; choke holding BHP while kill mud displaces. **D-010-style barrier schematic**: primary envelope outlined in blue, secondary in red. [NO] convention, from memory: `[VERIFY]`.
- **Terms:** kick, blowout, underbalance, influx, pit gain, flow check, barrier, WBE, barrier envelope, primary/secondary, SIDPP/SICP, kill-mud weight, choke, driller's/W&W method, bullheading, MAASP, kick tolerance.
- **Standards:** [NO] **NORSOK D-010 well barrier philosophy; Activities Regs §85; Facilities Regs §48**; [GEN] API RP 59, API Std 53, IADC/IWCF well-control curricula.
- **Simplifications:** [SIM] single gas kick, vertical well, no choke-line friction numerically, no hydrates, no underground blowout detail.
- **To verify (high priority):** **common WBEs: allowed with risk assessment (my memory of D-010) vs. "no common elements" (a Havtil snippet)**: the two sources *appear to conflict* and I must read both. Colour convention (blue primary / red secondary). Shut-in method (hard/soft) NCS practice. Detection-volume targets.

### Ch 8: Formation evaluation: discovery or dry hole? (22:15-26:15)

- **Beats:** *Drilling is an expensive way to buy measurements*: sequence from fast/cheap/uncertain → slow/expensive/definitive.
  1. **Mud logging:** cuttings, UV fluorescence, **gas chromatograph** (C1-C5), **lag time** (annular volume ÷ flow rate: cuttings are old news when they arrive); cautions: recycled gas, contamination.
  2. **LWD** (formation read *fresh*): gamma ray (shale vs sand), resistivity (hydrocarbons resist current), density-neutron (porosity, gas crossover), sonic (also *flags overpressure*, tying back to Ch 1), NMR. **Mud-pulse telemetry sends a few bits per second**, so real-time logs are a coarse preview of the recorded memory log.
  3. **Wireline:** triple-combo, sonic, imaging, NMR. **Archie** (Sw = (a·Rw/(φᵐ·Rt))^{1/n}), taught via the "salty sponge" picture; shaly-sand caveat.
  4. **Formation pressure & sampling (the reveal):** a probe on the wall measures **pressure vs depth** and pumps out fluid for downhole analysis and lab PVT. Each fluid has a gradient (water ≈ 0.10-0.11, oil ≈ 0.07-0.09, gas ≈ 0.02-0.03 bar/m, typical `[VERIFY]`); **where the lines intersect is the free-water level**: you can locate a contact the well never crossed. (FWL ≠ OWC: capillary transition.) Different pressure trends ⇒ different compartments.
  5. **Coring:** conventional (weeks to results: porosity, permeability, saturations, SCAL, **rock-mechanics triaxial tests, a mech-eng home turf**) and sidewall cores.
  6. **DST:** temporary completion flowing the well to surface: build-up analysis → permeability, skin, boundaries, surface samples. **[NO]** on the NCS flaring is tightly restricted and emissions are taxed, so full DSTs are comparatively rare `[VERIFY with Factpages counts]`.
  7. **The verdict:** a decision tree: (i) **hydrocarbons present?** (shows + logs + samples) (ii) **movable?** (mobility/DST) (iii) **how much?** (net pay, contacts, thickness). **Net pay** = net sand → net reservoir → net pay as cutoffs (shale volume, porosity, saturation) are applied; **N/G**. **[NO]** Sodir defines a *discovery* as probable mobile petroleum shown by testing, sampling **or logging**: a **discovery is not the same as commercial**; economics are out of scope. "Dry" is still data.
- **Wait, why?** *"You can find the oil-water contact without ever drilling through it."* (pressure gradients) and *"The log you watched live isn't the log you'll interpret."*
- **Analogy → equation:** Barometer in a stairwell (gradient lines → intersection); salty sponge → Archie.
- **Animation:** Scrolling log tracks with cutoff shading turning net sand → net reservoir → net pay; **pressure-vs-depth plot** drawing the water line and the oil line and intersecting at the FWL; mud-log lag animation (cuttings arriving late); the decision tree lighting up.
- **Terms:** mud log, show, chromatograph, lag time, LWD/MWD, gamma ray, resistivity, density, neutron, crossover, sonic, NMR, wireline, formation tester, pretest, mobility, gradient, FWL/OWC/GOC, core, DST, build-up, net pay, N/G, cutoff, saturation.
- **Standards:** [NO] Resource Management Regs + Sodir classification (discovery definition `[seen]`); [GEN] SPE-PRMS, API RP 40/44, Asquith & Krygowski, Dake.
- **Simplifications:** [SIM] Archie only (no Simandoux/Waxman-Smits); cutoffs *illustrative*, since real ones are field-specific; no volumetrics/economics.
- **To verify:** sample/core submission rules; "discovery must be reported when / how"; DST frequency on NCS; the Sodir well-result category names.

### Ch 9: Plugging & abandonment (26:15-29:30)

- **Beats:**
  1. **Why you can't just leave:** a well is a flow path from reservoir to seabed for geological time. D-010's design target is an **eternal perspective** `[VERIFY]`.
  2. **Identify every source of inflow**, not just the reservoir. Even a thin, overpressured overburden sand can flow. Barrier count per source: **two** barriers for hydrocarbon-bearing/flow-potential reservoir, **one** for other flow potential `[VERIFY]` + a surface/environmental plug.
  3. **Rock-to-rock**: a permanent barrier must seal **vertically and horizontally across the entire cross-section including every annulus**, bonded to competent rock on all sides. *A plug inside casing is not a barrier if there's a leak path behind it.* Analogy: sealing a tunnel with a door when pipes run along the walls.
  4. **How to get rock-to-rock:** (a) **verified annular cement** (exploration wells: cement is days old and was logged), (b) **section milling** (cut the casing away, plug the open hole), (c) **perforate-wash-cement (PWC)**: perforate, wash the annulus clean, cement; now recognised in Rev 5 `[seen: vendor source]`, (d) emerging alloy plugs (mention only).
  5. **Placing the plug:** mechanical base ("fundament") → **balanced cement plug** (spacer-cement-spacer through open-ended pipe, pull out slowly, clean up) → **verify**: tag (set-down weight) + positive pressure test; inflow test where applicable; log if logging-qualified. Minimum plug lengths, *e.g.* 100 m open hole (≥ 50 m above any inflow point), 50 m cased hole on a base, 30 m if annulus qualified by log `[seen: third-party summary of Rev 5; do not narrate until D-010 is read]`.
  6. **Verification culture:** a misread negative/inflow test is a documented factor in a major accident (D1, only if D6 selects it).
  7. **Cut and pull:** cut casing/conductor below the seabed, retrieve wellhead and guide base; **ROV survey** to prove a clean, trawlable seabed `[NO, VERIFY requirement]`. Exploration wells can't stay temporarily abandoned indefinitely (**two-year limit for post-2014 exploration wells** `[seen, VERIFY]`).
  8. **As-abandoned schematic** filed with the authorities `[NO, VERIFY]`.
- **Wait, why?** *"Why does a plug *inside* the pipe not count?"* and *"Why is exploration-well P&A the 'easy' case? (fresh, logged cement) and what makes old wells hard?"*
- **Analogy → equation:** Tunnel + pipes-along-the-wall; cork sealing against the glass, not the liner. No equations (the pressure test criterion is a number from D-010, deferred).
- **Animation:** **Plug placement during P&A**: a cutaway of the well *as drilled* (reuse the Ch 1 schematic); mechanical plug sets; cement plug is placed through the drill pipe as a balanced column; pipe pulls up through it; tag-and-test gauge; section-milling sequence for the alternative; then casing cuts and wellhead lifts; **camera pulls back to the empty seabed** (bookend).
- **Terms:** P&A, temporary vs permanent abandonment, permanent well barrier, rock-to-rock, source of inflow, bridge plug, balanced plug, tag, pressure/inflow test, section milling, PWC, cut-and-pull, ROV survey.
- **Standards:** [NO] **NORSOK D-010 Rev 5, abandonment chapter + EAC tables (incl. new PWC table)**; Activities Regs; Havtil reports on permanent plugging; [GEN] ISO 16530-1, OEUK abandonment guidelines (contrast).
- **Simplifications:** [SIM] one hydrocarbon-bearing reservoir + one overburden flow-potential zone; no thermal/ageing of cement; no bismuth/alloy plugs beyond a mention.
- **To verify (high priority):** **all plug lengths, test pressures, tag loads, barrier counts per source, removal depth below seabed, ROV/seabed clearance rule and who requires it, consent/reporting steps.** None may be narrated until read from D-010/Regs.

### Ch 10: Outro: the empty seabed (29:30-30:00)

- **Beats:** Return to the Ch 0 seabed, now with the well gone. Recap in one line: *a well is the art of winning a pressure argument with the Earth every hour, and then making the win permanent.* Optional end-card: a one-glance list of **what was Norway-specific vs general**.
- **Animation:** Mirror the opening shot; the window gauge dissolves.

---

## 5. Cross-cutting checks I'll build into Stages 2-3

- **Glossary ledger (`script/glossary.yaml`)**: every term → chapter of first use + one-line definition; a lint (`make lint-script`) fails if a term is used before it's defined.
- **Single well model** (`scenes/common/well_model.py`) feeds plots, camera framing and animations (no hand-typed numbers in scene files).
- **Palette conflict to resolve in Stage 3:** D-010 barrier colours (blue primary/red secondary) clash with the oilfield fluid convention (blue water, red gas, green oil) and my pressure curves. Plan: barrier schematics are a *distinct 2-D panel style* with outline colours only.
- **Accessibility:** colour-blind-safe palette, plus line style/labels, not colour alone.

---

## 6. Decisions I need from you (my recommendation first)

| ID | Decision | Recommendation | Alternatives |
|---|---|---|---|
| **D1** | **Visual style / engine** | **A:** flat technical illustration in Workbench (+ matplotlib/2-D overlays); selective **B:** EEVEE for 3-4 hero shots | **C:** photoreal Cycles (≈ 170 h here; infeasible) |
| **D2** | **Running example** | **Fictional composite NCS wildcat** (numbers coherent, nothing misattributed) | Real well from Sodir Factpages (more compelling, but sodir.no is blocked here: you'd paste the data) |
| **D3** | **Narration voice (Stage 5)** | Placeholder `espeak-ng` here for timing; real voice = you record, **or** a cloud TTS you run locally, **or** allow-list `huggingface.co` (+ GitHub release downloads) so I can use Piper/Kokoro | Decide later; affects script phrasing (pronunciation of "kick", "sg", etc.) |
| **D4** | **Where full renders run** | Preview/previews here; **final 1080p on your machine** (same `make` targets). Container is ephemeral. | All here, chapter-by-chapter, with outputs pulled out as I go |
| **D5** | **Primary sources** | **Allow-list `havtil.no`, `sodir.no`, `standard.no`** (or drop PDFs in `sources/`) | Proceed from secondary sources with many `[VERIFY]` flags (not recommended for D-010 numbers) |
| **D6** | **Hook & incident** | Physics-puzzle hook (Ch 0), **no real incident in the hook**; one *verified* incident in Ch 7 (candidates: Macondo cement/negative-test, or a Havtil-investigated NCS event) | Incident-led cold open |
| **D7** | **Units** | bar/sg/m with a one-time psi/ppg card | oilfield units primary |

## 7. What happens after approval

**Stage 2** (needs D5 ideally first): full timestamped narration (≈ 4,200 words) per chapter, a shot list for every beat, inline `[NO]/[GEN]/[SIM]/[VERIFY]` tags, a "flagged claims" table, and the glossary ledger.
**Stages 3-5** as per your pipeline. `make doctor` already works (`Makefile`); `make venv` will install `bpy 4.5.14` locally.

*Sources and standards register: `script/00_sources.md`.*
