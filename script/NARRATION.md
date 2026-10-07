# Narration script and shot list (generated: do not edit; edit `chNN_*.md` and run `make script`)

Runtime 36:42 (voice-timed: kokoro-v1.0 af_heart, paced to 172 wpm) · tags: **[NO]** Norway-specific · **[GEN]** general industry · **[SIM]** deliberate simplification · **[VERIFY]** not confirmed against a primary source · **[SEEN]** seen only in a secondary/web source

## Ch 0: Cold open: the window  (0:00–1:49)

### 0.01 · 0:00 · 17.8s · anim **[GEN]**

**VO:** This is the North Sea floor, three hundred metres down. Soon a drill will reach almost four kilometres into the rock beneath it. A few months from now, the rig will be gone, the steel cut off below the seabed, and you will barely find a trace.

**SHOT:** Eased dive from the sea surface through drifting marine snow (parallax layers) to a bare seabed, landing on "three hundred metres" with a "seabed · 300 m" callout. Camera pulls out to true vertical scale: a dashed well path draws down 4 km with a depth counter. A rig and wellhead silhouette fade in, then out (time-lapse), and the camera returns to the same empty seabed. Title: "THE HOLE THAT FIGHTS BACK / how an offshore exploration well is drilled, judged, and sealed for ever".

### 0.02 · 0:18 · 16s · anim **[GEN]**

**VO:** Almost everything in between comes back to one problem. The rock squeezes in on the hole, and the fluid in its pores pushes to get in. Our defence is a liquid, drilling fluid, or mud, and we choose how heavy it is.

**SHOT:** Camera dives through the seabed into a cutaway: sea band and seabed on top, a hole drilled down from a wellhead stub with a rounded bottom, layered rock with a sandstone near the bottom. Inward squeeze arrows on the walls (rock), small blue arrows from the sand (pore fluid). The hole fills with amber mud; a "mud weight" slider appears beside it as "we choose how heavy" is said.

**Terms introduced:** drilling fluid

### 0.03 · 0:34 · 22.2s · anim **[GEN]** **[SIM]**

**VO:** Deep down, the fluid in the rock's pores is under pressure. Make the mud too light, and that fluid pushes into the hole: a kick. Make it too heavy, and you crack the rock. The mud drains into the crack, the level in the hole falls, the pressure at the bottom drops, and the fluid comes in anyway.

**SHOT:** Balance first: blue arrows from the sand, amber arrows from the mud, equal. Slider down: blue grows, blue blobs stream from the sand into the hole and rise, "KICK" pops on the word. Slider up: one wedge-shaped fracture opens in the upper rock and fills with amber; the mud level falls (still above the fracture mouth); the slider STAYS at heavy while a "pressure at the bottom" marker slides down past the pore-pressure tick; blue inflow returns at the sand.

**Terms introduced:** kick

- **SIM:** one loss zone and one kicking sand; the fracture is drawn larger than life

### 0.04 · 0:56 · 30.4s · anim **[GEN]** **[SIM]** **[VERIFY]**

**VO:** So the weight must live inside a window: the mud weight window. In the deepest part of our well, the gap between too light and too heavy is only about a tenth of the mud's weight. In high-pressure wells, and in fields already drained by production, it can be just a few per cent. And the window moves with every metre. Pause, and guess: how do you stay inside it, for four kilometres?

**SHOT:** The slider track becomes a horizontal gauge: KICK zone on the left (pore-pressure blue), CRACK zone on the right (fracture orange), green window between, mud marker inside. "≈ 10 % of the mud weight" label. The KICK and CRACK zones close in like a vice for the high-pressure example ("a few %"), then reopen. On "moves with every metre" the camera pulls out: the gauge is one slice of a depth plot whose pore and fracture curves run from the seabed to 4 km. Hold for the pause.

**Terms introduced:** mud weight window

- **SIM:** "about a tenth": in the deepest (8½ in) section the mud must stay above the highest pore pressure in the open hole (1.55 sg at 3,900 m) and below the weakest rock, the 9⅝ in shoe at 3,400 m (1.71 sg): 0.16 sg on 1.62 sg of mud ≈ 10 %
- **VERIFY:** "a few per cent" for high-pressure and depleted wells is general knowledge, no primary source read

### 0.05 · 1:26 · 22.4s · anim **[GEN]** **[SIM]**

**VO:** That is our question: how do you drill four kilometres through rock whose fluids want to push in, and that cracks if you push back too hard, then leave the hole so safe nobody ever has to think about it again? Our well is invented; the physics is real. First, a plan.

**SHOT:** Kinetic type keyed to the spoken words over the dimmed depth plot: "DRILL 4 km" / "HOLD BACK THE FLUIDS" / "DON'T CRACK THE ROCK" / "SEAL IT FOR EVER". An "ILLUSTRATIVE WELL: invented numbers, real physics" badge pops on "invented". The well-so-far strip slides in at the left edge.

- **SIM:** composite wildcat; every number in the video comes from one made-up well model (scenes/common/well_model.py)

## Ch 1: Planning: casing from the bottom up  (1:49–6:46)

### 1.01 · 1:52 · 26.2s · anim **[GEN]** **[SIM]**

**VO:** Before anyone drills, someone decides what the hole is for. Geologists have picked a target: a sandstone at about three thousand nine hundred and fifty metres. Depth here means true vertical depth below sea level, TVD: straight down, not along the hole. Real well plans usually measure from the rig floor instead. Our job is to reach the target safely, and find out what is in it.

**SHOT:** Cross-section of the North Sea: sea surface, seabed at 300 m, layered strata, a highlighted sandstone target at 3,950 m. Vertical dashed line labelled "TVD" and a curved well path labelled "measured depth: along the hole" beside it; the two depth read-outs differ at the target. Depth ruler at left marked "m below sea level".

**Terms introduced:** target; true vertical depth

- **SIM:** all depths are TVD below sea level in a near-vertical well; NCS well plans reference the rig floor (m RKB)

### 1.02 · 2:18 · 30.2s · anim **[GEN]** **[SIM]**

**VO:** Start with something you know. Dive ten metres and you feel one more bar. Hydrostatic pressure is density times gravity times depth. Mud is just a heavier liquid, and we quote its weight as specific gravity, sg: fresh water is one. Rock pores hold fluid too, at a pore pressure. If the pores connect all the way up, the pressure is that of a column of salty water, about one point oh three sg: normal pressure.

**SHOT:** A diver with a 1 bar per 10 m gauge (counter ticking); then a column of sea water and a column of amber mud side by side with pressure-vs-depth lines (sea water labelled 1.03 sg). Then a rock block with magnified pores filled with blue fluid and a gauge, connected through the pores to the sea.

**Terms introduced:** hydrostatic pressure; specific gravity (sg); pore pressure

- **SIM:** normal pore pressure drawn as a 1.03 sg brine column

### 1.03 · 2:48 · 32.5s · anim **[GEN]** **[SIM]**

**VO:** But sometimes fluid is trapped. Picture a spring, the rock grains, in a cylinder of water, the pore fluid, under a piston with a tiny hole. Load it: at first the water takes the load, then it leaks away and the spring takes over. Bury sediment fast under tight shale, and the water cannot escape as fast as load is added, so it keeps carrying the load. That is overpressure. The grains carry only the effective stress: the weight of everything above, minus the pore pressure.

**SHOT:** Terzaghi piston-and-spring, labelled as rock: spring = grains, water = pore fluid. Load applied: gauge jumps, water streams out through the hole, spring compresses, gauge falls. Replay with a much smaller hole ("tight shale"): gauge stays high, spring barely moves, "overpressure". Equation after the animation: σ′ = σ − p, with σ labelled "overburden".

**Terms introduced:** overpressure; effective stress

- **SIM:** single-mechanism picture (disequilibrium compaction); other overpressure mechanisms exist and are not shown

### 1.04 · 3:21 · 32.2s · anim **[GEN]** **[SIM]**

**VO:** Now the upper wall of the window. A hole in a plate concentrates stress, two to three times over, at its edge, and rock around a borehole is squeezed the same way. Mud pressure pushes back. Too little, and the concentrated stress crushes the wall: collapse. Too much, and the wall splits; that pressure, as a mud weight, is the fracture gradient. For planning it is predicted. Later, a leak-off test, pumping until the rock takes fluid, checks it at one depth in the real hole.

**SHOT:** Plate-with-hole cartoon around a borehole circle: hoop-stress arrows concentrated at the wall ("2-3x"). An internal pressure gauge: at low pressure the wall chips inward (collapse); at high pressure a split opens at the wall (fracture). Small pressure-vs-volume curve labelled "leak-off test: one depth, after casing is set".

**Terms introduced:** fracture gradient; leak-off test

- **SIM:** the factor depends on the stress state: about two for equal horizontal stresses, up to three for a uniaxial field (Kirsch); leak-off pressure lies between the minimum horizontal stress and the breakdown pressure

### 1.05 · 3:53 · 31.2s · anim **[GEN]** **[SIM]**

**VO:** Plot both limits against depth, as an equivalent mud weight: the mud weight that would give that pressure. Pore pressure on the left, fracture on the right. The mud must stay between them, with a margin each side. In our well the window is tight near the seabed, widest around two and a half kilometres, then pinches in where overpressure builds, because pore pressure climbs faster than the stress needed to open a fracture. Simplified: I draw the lower limit as pore pressure alone.

**SHOT:** THE CORE CHART. Axes: equivalent mud weight (sg) horizontal, depth vertical (down). Blue pore-pressure curve draws on from the seabed downwards, then the orange fracture curve, the green window fills between them. Three width brackets: 0.17 sg near the seabed, ~0.59 sg around 2,400 m, ~0.19 sg at 3,900 m. Margins as thin dashed offsets. Small caption: "lower limit drawn as pore pressure only".

**Terms introduced:** equivalent mud weight

- **SIM:** lower limit drawn as pore pressure only; the model's collapse curve lies below pore pressure in this basin and is not drawn

### 1.06 · 4:24 · 43.8s · anim **[GEN]** **[SIM]**

**VO:** Remember the question: how do you stay inside the window for four kilometres? You don't, not all at once. You stay inside it one section at a time, and lock each finished section behind steel pipe, casing, cemented in place. We design from the bottom up. The deepest section needs about one point six two sg: its highest pore pressure, one point five five, plus a margin. Draw that line up until it meets the fracture curve, less a margin and room for a gas kick. Above that point we could not safely shut in a kick, closing the well against it, so casing must end below it. Its bottom end is the casing shoe.

**SHOT:** On the window chart, a vertical amber line at 1.62 sg ("deepest section: 1.55 sg pore + margin") rises from TD until it meets the yellow curve "fracture, less margin and kick allowance" at ~3,370 m; a red band marks "shoe too weak for a kick above here". A faint tick shows where plain fracture-minus-margin would cross (~2,420 m) to show that the kick allowance decides. A casing string with a shoe symbol telescopes down from the seabed to the first valid depth.

**Terms introduced:** casing; casing shoe; shut-in

- **SIM:** margins are invented: 0.07 sg trip (swab) margin over pore pressure; 0.03 sg below fracture covering ECD and surge; plus a 150 m gas-kick term at the shoe (see well_model.py). Without the kick term the 1.62 sg line would cross fracture-less-margin near 2,420 m

### 1.07 · 5:08 · 28.3s · anim **[GEN]** **[SIM]** **[VERIFY]**

**VO:** Near the top, pressure is not the only enemy. Shallow gas: pockets a few hundred metres below the seabed, reached before any blowout preventer, the well's big emergency seal-off stack, is in place, so a gas flow there cannot simply be shut in. Boulders left by glaciers. Soft, uneven seabed. A site survey, seabed mapping plus high-resolution seismic of the shallow layers, looks for all of them before the rig arrives.

**SHOT:** Seabed cutaway: a red gas pocket under a thin cap, boulders in glacial till, a pockmark. A survey vessel tows a seismic streamer: sub-bottom wavefronts penetrate the sediment and light up the gas pocket (bright spot) while a multibeam fan maps the seabed; hazards light up with labels.

**Terms introduced:** shallow gas; blowout preventer

- **SIM:** shallow water flow, common in other basins, omitted
- **VERIFY:** whether a seabed/shallow-gas site survey is a Norwegian regulatory requirement (and its wording) not confirmed

### 1.08 · 5:36 · 31.8s · anim **[GEN]** **[SIM]**

**VO:** Then repeat. The deepest string ends at about three thousand four hundred metres. Above that shoe the mud can be lighter, one point four nine sg, and its line meets the fracture curve near two thousand metres: the next shoe. Above that, the mud, one point one two sg, is so light that pressure no longer decides. Shallow hazards do, and the need for a strong anchor for the seabed hardware and the preventer. About a thousand metres. The result is a staircase.

**SHOT:** Repeat of the stair-step: from 3,400 m the amber line steps left to 1.49 sg and rises to meet the curve at ~2,000 m (string 2 telescopes into place); step again to 1.12 sg: the line would meet the curve at 660 m, but a label "shallow hazards + wellhead/BOP anchor: not shallower than 1,000 m" snaps the third shoe to 1,000 m. Three shoes + the conductor, drawn as nested strings: the staircase.

- **SIM:** the surface-casing depth floor of 1,000 m is an assumption standing in for hazard and kick-tolerance reasoning

### 1.09 · 6:08 · 38.4s · anim **[GEN]** **[SIM]**

**VO:** The strings nest like a telescope, because each must pass through the one above. So the sizes step down: thirty inch, twenty, thirteen and three eighths, nine and five eighths, each set in a bigger drilled hole, and finally an eight and a half inch open hole to the bottom. Every string costs diameter. And this is a wildcat, the first well into an untested prospect. Nearby wells help, but may sit in a different pressure compartment, so the forecast is uncertain. The plan keeps a spare, contingency string, in reserve, and that only fits if everything above is sized bigger from the start.

**SHOT:** Nested casing strings to scale in a cross-section ring view and a side telescoping view, each string with its drilled hole size (36, 26, 17½, 12¼ in) and the 8½ in open hole. A dashed "contingency string (7 in)" appears in reserve. Caption: "wildcat: first well on an untested prospect".

**Terms introduced:** wildcat; contingency string

- **SIM:** standard NCS-style size ladder is from general knowledge; the conductor shoe (390 m) is soil-driven, not pressure-driven

## Ch 2: Top hole: drilling with no safety net  (6:46–10:15)

### 2.01 · 6:49 · 32.7s · anim **[GEN]** **[SIM]**

**VO:** Now we drill. The first section is the strangest. The drill string, the pipe that turns the bit, hangs in open sea, with no riser, the big pipe that would carry the mud back up to the rig, and no blowout preventer. This is riserless drilling. Seawater, with slugs of thick gel to sweep the hole clean, is pumped down the pipe, out of the bit, and back up around it, spilling the cuttings, the chips of rock, onto the seabed. Usually, nothing returns to the rig.

**SHOT:** Seabed cutaway, camera at the seabed. A drill string hangs from the surface through open water into the first hole. Flow particles go down the pipe, out of the bit, back up the annulus around the pipe, and a grey cuttings plume billows out onto the seabed around the hole. A greyed-out "BOP" and "riser" ghost outline at the surface with a cross through them.

**Terms introduced:** drill string; marine riser; riserless drilling; cuttings

- **SIM:** riserless mud recovery (used on some NCS wells) not shown

### 2.02 · 7:22 · 46.7s · anim **[GEN]** **[VERIFY]**

**VO:** Pause and think. We are about to drill seven hundred metres below the seabed with nothing that can close the well. Why is that allowed? [pause 2] This shallow, only a thin layer of sediment presses down, so the grains are barely squeezed and the rock splits at low pressure. Shut in a gas flow here, and the trapped pressure would crack the rock and send gas up outside the well, where nothing can stop it. Better to let it bubble out at the seabed, far below the rig. So the defences come first: a survey for gas, a narrow pilot hole where in doubt, a remotely operated vehicle, an ROV, watching the hole, and heavy mud ready to pump.

**SHOT:** Headline "700 m below the seabed, nothing that can close the well". Side-by-side cartoon: left, closed-in well with a pressure gauge climbing until a crack runs to the seabed and gas escapes outside the well ("broach"); right, open top hole where gas bubbles out at the seabed, 300 m below the rig. Then the defences as a checklist: survey, pilot hole, ROV camera, heavy mud tank. Small inset: the weak shallow fracture gradient from the window chart.

**Terms introduced:** ROV

- **VERIFY:** how NORSOK D-010 treats the barrier status of the riserless top hole (one fluid barrier? conditions?) is NOT confirmed; the narration describes the physics only and does not cite the standard

### 2.03 · 8:08 · 45.9s · anim **[GEN]** **[SIM]**

**VO:** It starts with the spud, the first metres of the well. Often a guide base, a steel frame on the seabed, helps guide the pipe and keep everything aligned. Then comes the conductor, a thirty inch pipe that is the well's foundation. It is either jetted, washed down by water jets at its tip while its own weight sinks it into soft clay, or, as in our well, drilled in a thirty-six inch hole and cemented, about ninety metres deep. Think of it as a pile. Soil friction on it, later helped by the cemented casing inside, carries the wellhead, the hardware at the top of the well, and then a blowout preventer of hundreds of tonnes, while the moving rig and riser bend it back and forth.

**SHOT:** A guide base lands on the seabed. A 30-inch conductor is lowered; split view shows (a) jetting: water jets at the tip, the pipe sinks under its own weight; (b) drill a 36-inch hole and cement ("our well", 90 m). Then a free-body cartoon: vertical soil-friction arrows along the pipe, lateral soil springs, a bending moment from rig and riser motion at the top.

**Terms introduced:** spud; guide base; conductor; wellhead

- **SIM:** BOP weight given only as "hundreds of tonnes" [memory]; guide-base variants (temporary, permanent, guideline-less, suction-anchor foundations) not shown

### 2.04 · 8:54 · 21.4s · anim **[GEN]**

**VO:** Next, drilling through the conductor, a twenty-six inch hole goes down to a thousand metres below sea level, seven hundred below the seabed. Into it goes the twenty inch surface casing, with the high-pressure wellhead housing at its top. That housing is the first hardware that can contain pressure, and everything else will hang from it.

**SHOT:** A 26-inch bit passes down through the conductor and drills to 1,000 m on the depth ruler ("700 m below seabed"); the 20-inch casing string is lowered with the high-pressure housing on top and lands inside the conductor housing.

**Terms introduced:** surface casing

### 2.05 · 9:16 · 26.7s · anim **[GEN]** **[VERIFY]**

**VO:** Then we cement it: pumped down the inside of the pipe and up the outside, until grey cement appears at the seabed, spotted by the camera on the ROV. Cement fills the annulus, the ring-shaped gap around a pipe: here, between the casing and the rock, and up inside the conductor. It supports the wellhead, and seals off shallow zones. We will see how cement behaves in chapter six.

**SHOT:** U-tube cutaway of the 20-inch string, annulus initially full of seawater: grey cement travels down inside the pipe behind a plug, around the shoe and up the annulus, displacing the seawater; it is followed down the pipe by seawater, leaving only a short grey shoe track inside the pipe. At the seabed a puff of grey cement exits and the ROV camera view highlights it with a "returns" label.

**Terms introduced:** annulus; cement

- **VERIFY:** the practice of cementing to the seabed with ROV-confirmed returns on current NCS wells is from general knowledge, not confirmed

### 2.06 · 9:42 · 32.6s · anim **[GEN]** **[SIM]**

**VO:** A wellhead is nested seats, like stacked bowls. The high-pressure housing, on top of the twenty inch casing, lands inside the low-pressure conductor housing. Each later string will hang inside it on a casing hanger, with a seal that closes the gap behind it. One more thing for a subsea engineer: once the preventer and riser are on, this becomes a tall slender column bent back and forth by rig motion and currents, so fatigue of the wellhead and conductor is a real design driver.

**SHOT:** Exploded cutaway of the wellhead: the low-pressure (30 in) housing and the high-pressure housing nested; a casing hanger with seal drops into place and the gap behind it is sealed. Then the BOP and riser appear on top and the whole column sways slowly (rig motion, current arrows) with a stress-range counter incrementing.

**Terms introduced:** casing hanger

- **SIM:** cuttable sidebar (fatigue) if the cut is over budget

## Ch 3: BOP, riser, and the closed loop  (10:15–12:49)

### 3.01 · 10:18 · 19.5s · anim **[GEN]** **[SIM]**

**VO:** Now we close the loop. The blowout preventer is lowered on the marine riser and latches onto the wellhead. For the first time the mud makes a full circuit: down the drill pipe, up the annulus and the riser, and back to the rig's tanks instead of onto the seabed.

**SHOT:** The BOP stack descends on the riser from the surface to the wellhead and latches (a clamp animation). Flow particles go down the drill pipe, up the annulus and inside the riser to the rig's tanks. The ghosted riserless BOP/riser outline from Ch 2 becomes solid.

- **SIM:** the circulation loop is closed, but the riser top is open to atmosphere at the rig (not a sealed system)

### 3.02 · 10:37 · 28.9s · anim **[GEN]** **[SIM]** **[VERIFY]**

**VO:** A blowout preventer is a stack of valves, each with a job. The annular preventer squeezes a rubber element around whatever is in the hole. Pipe rams close around the drill pipe. And the last resort: the blind shear rams, which can cut through the drill pipe body, though not its thick joints, and seal the hole. Gas-charged accumulators store hydraulic energy, so the preventers close fast, even if the rig loses power.

**SHOT:** THE BOP CLOSING ANIMATION. Cutaway of a subsea stack in the correct order, top to bottom: annular preventer, blind shear rams, two pipe rams, wellhead connector; drill pipe through the bore. In the order of use: the annular's rubber element squeezes onto the pipe; the pipe rams slide in and grip; the blind shear rams slide in above them, cut the pipe body (the stub below drops, the bore closes with no pipe through it). A gas-charged accumulator bottle with a pre-charge gauge beside it.

**Terms introduced:** annular preventer; ram; blind shear ram; accumulator

- **SIM:** stack drawn with one annular, the blind shear rams above two pipe rams; real NCS stacks have more cavities (casing shear, second annular)
- **VERIFY:** Norwegian requirements on BOP configuration (shear-ram redundancy, test pressure, test interval) not confirmed against NORSOK D-010 / D-001 / Activities Regulations

### 3.03 · 11:06 · 43.8s · anim **[GEN]** **[SIM]**

**VO:** Why does the closed loop matter? Three reasons. The mud comes back, so we can afford a real, weighted mud and tune it to control pressure. We can compare the flow we pump in with the flow coming back, and watch the tank level: our earliest warning of a kick. And if something goes wrong, we can shut the well in at the seabed and circulate the kick out through the choke, an adjustable valve on a line back to the rig, not up the riser. From here on, two barriers, things that can each stop flow, stand between the reservoir and the sea: the mud, and behind it steel, cement and this preventer.

**SHOT:** Three icon panels animate in turn: (1) a mud-weight dial and a bottom-hole pressure bar; (2) "flow in" and "flow out" meters with a difference needle and a rising pit-level gauge; (3) the BOP closing at the seabed with the kick routed out through the choke line and its adjustable choke valve. Then a simple two-layer shield graphic: inner "mud", outer "steel + cement + BOP", between "reservoir" and "sea".

**Terms introduced:** choke

- **SIM:** the two-barrier picture is introduced informally here and made precise in Ch 7

### 3.04 · 11:50 · 13.7s · anim **[GEN]** **[SEEN]**

**VO:** None of it counts until it is tested. A barrier you have not tested is a hope, not a barrier. So every preventer is pressure-tested, and the rock gets tested too.

**SHOT:** The stack with the pipe pulled out of it and a test plug in the wellhead: a pressure gauge ramps to a test pressure with a "HOLD" timer; a green tick appears on each element as it is function- and pressure-tested (the blind shear rams tested on an empty bore).

- **SEEN:** Activities Regulations s.85 requires tested well barriers (search summary)

### 3.05 · 12:04 · 45.8s · anim **[GEN]** **[SIM]**

**VO:** Then we drill out the cement at the bottom of the twenty inch, and a few metres of fresh rock, and test it: the rock, and the cement seal at the shoe. Close the well and pump slowly. Pressure rises in a straight line, because we are squeezing a sealed volume of slightly compressible mud, until the line bends: fluid has started to leak into the formation. That is the leak-off point. Add the surface reading, about thirty-seven bar, to the weight of the mud column, and it converts to about one point five sg at the shoe. That one point checks our fracture forecast at this depth, and it caps the mud weight and the kick size for the next section.

**SHOT:** Casing-shoe cutaway with a few metres of open hole below and the BOP closed at the top. Right: a pressure vs pumped-volume plot draws a straight rise ("compressing the mud"), then bends over (leak-off point, dot, "37 bar at surface"). An equation card: 37 bar + mud column (1.12 sg, 1,000 m) = 1.50 sg at the shoe. The dot is carried across to the window chart, landing on the fracture curve at 1,000 m.

**Terms introduced:** leak-off point

- **SIM:** leak-off point plotted exactly on the model curve; real tests scatter and are usually stopped at the first deviation from the line

## Ch 4: Drilling the deep sections  (12:49–16:41)

### 4.01 · 12:52 · 36s · anim **[GEN]**

**VO:** At the bottom of the drill string is the bottom-hole assembly, the BHA: the bit, a steering tool, measurement sensors, and heavy steel drill collars. A puzzle: we need tonnes of force on the bit. Do we push from the rig? [pause 1.5] No. The rig holds the pipe back. It hangs in tension, like a plumb line, and only part of the heavy collars' weight rests on the bit. In a vertical hole, push down with the slender pipe instead and it would buckle, so we keep the compression in the collars.

**SHOT:** Vertical drill string drawn full height with the hook at the top: tension (blue arrows) in the long drill pipe, a neutral point marker about 80 % of the way up the collars, compression (red arrows) in the collars at the bottom with the bit. Puzzle beat: a ghost string pushed from the top buckles into a sine shape and is crossed out. A weight-on-bit gauge shows only part of the collar weight on the bit.

**Terms introduced:** bottom-hole assembly; drill collar

### 4.02 · 13:28 · 41.4s · anim **[GEN]** **[SIM]**

**VO:** Why steer at all? To reach a target that is not straight below, to stay clear of other wells, and, in a vertical wildcat like ours, to keep the hole straight. That is directional drilling. To steer, we tilt the bit or push it sideways. A mud motor, driven by the mud flowing through it, has a slight bend in its housing: stop turning the pipe and just slide, and the hole curves. A rotary steerable tool pushes pads against the wall, so it steers while the whole string turns. At the tip, a PDC bit, polycrystalline diamond compact, shears rock with diamond cutters, like a lathe tool.

**SHOT:** Overhead map: a well deviating from the rig position to an offset target around a neighbour well; then a vertical well kept straight. Steering panels: (a) bent-housing motor: one continuous path, straight while rotating, curving while sliding (toolface arrow), straight again on the new tangent; (b) rotary steerable: pads push sideways on the wall while the string spins. Close-up of a PDC bit shearing a rock layer like a lathe tool.

**Terms introduced:** directional drilling; mud motor; rotary steerable system; PDC bit

- **SIM:** our example well is nearly vertical; steering is shown as concept only

### 4.03 · 14:10 · 43.7s · anim **[GEN]** **[SIM]**

**VO:** A curved hole has a cost. Pulling pipe through a bend is like a rope around a capstan: the tension needed multiplies by e to the mu theta, where theta is the total angle the hole turns through. The sharpness of the bend, in degrees per thirty metres, is the dogleg severity. Pipe rotating through a sharp bend is flexed back and forth on every turn, which breeds fatigue cracks, so we limit it. To know where we are, measurement-while-drilling sensors, MWD, measure the hole's inclination and direction, and we compute the path from those angles. Each survey carries a small error, so the uncertainty in our position, an ellipse, grows the farther we drill.

**SHOT:** A rope round a capstan with the equation T2 = T1·e^(μθ) after the picture (T2 > T1); then a deviated well with drag arrows and θ marked as the total turn. A dogleg zoom: "° per 30 m", with a rotating pipe flexing (alternating tension/compression on its outer fibre). A plan-view uncertainty ellipse that grows along the well path, computed from survey stations.

**Terms introduced:** dogleg severity; measurement while drilling

- **SIM:** friction factor and dogleg numbers are illustrative

### 4.04 · 14:53 · 34.3s · anim **[GEN]** **[NO]** **[VERIFY]**

**VO:** Meanwhile the mud is the hardest-working part of the system. Its weight holds back the formation fluids and props up the wall, which it seals with a thin filter cake. It carries cuttings up, cools the bit, and carries signals to the surface. It may be water-based, or oil-based in deep sections, and most of its extra weight comes from barite, a mineral powder about four times as dense as water. On the Norwegian shelf, cuttings coated in oil-based mud may not be dumped at sea: they are shipped to shore or injected underground.

**SHOT:** Cutaway annulus with panels in turn: pressure arrows on the wall and a thin filter-cake layer on the permeable sand; cuttings rising in the stream (flow particles); cool/lubricate at the bit; pulses travelling up the pipe. A barite cloud in a beaker raises a density gauge (4.2 sg barite). A skip of oily cuttings goes onto a supply boat instead of overboard.

**Terms introduced:** filter cake; water-based mud; oil-based mud; barite

- **VERIFY:** the NCS ban on discharging oil-based-mud cuttings (OSPAR Decision 2000/3, Norwegian activities rules) is from memory, not checked against the primary text

### 4.05 · 15:28 · 32.3s · anim **[GEN]** **[SIM]**

**VO:** Now the twist. With the pumps on, the mud has to push its way up the narrow gap around the pipe. Friction adds pressure at the bottom. So bottom-hole pressure is higher while we pump than when we stop. Expressed as an equivalent mud weight, that pumping pressure is the equivalent circulating density, ECD. And every time we stop the pumps to screw on another stand of pipe, about twenty-eight metres, a pause drillers call a connection, the pressure at the bottom drops.

**SHOT:** Annulus cutaway with a bottom-hole pressure gauge (counter). Pumps ON: flow particles and friction arrows along the annulus, gauge reads high; pumps OFF at a connection: friction vanishes, gauge drops, a step trace on a pressure-vs-time chart (ECD trace amber, static line dashed amber). Equation after the animation: ECD = MW + annular friction ΔP / (g · TVD).

**Terms introduced:** equivalent circulating density; connection

- **SIM:** Newtonian-style friction picture; real annular hydraulics use Herschel-Bulkley rheology

### 4.06 · 16:00 · 40.9s · anim **[GEN]** **[NO]** **[SIM]** **[VERIFY]**

**VO:** So the real window is squeezed from both sides. With the pumps off, or worse, while pulling pipe out, pressure must still beat the pore pressure. With the pumps on, it must stay under the fracture limit at the weakest point, usually the last casing shoe. In a narrow window, sometimes no mud weight does both. Managed pressure drilling, MPD, adds a knob. A rotating seal closes the top of the annulus around the turning pipe, the returns go through a choke, and when the pumps stop the choke adds back pressure at the surface, holding bottom-hole pressure steady. Then the mud alone is no longer the whole barrier.

**SHOT:** The window chart returns, zoomed on the open hole below the 9⅝ in shoe (3,400 m to TD): pumps-off marker at 1.62 sg, pumps-on (ECD) marker at ~1.67 sg, both amber; "weakest point: shoe at 3,400 m, 1.71 sg" tick. A hypothetical narrower window shows the two markers unable to fit ("sometimes no mud weight does both"). Then the MPD schematic: a rotating seal on top of the annulus, a choke on the return line; as the pump trace drops, the choke back-pressure trace rises and the BHP trace stays flat.

**Terms introduced:** managed pressure drilling; back pressure

- **SIM:** MPD variants collapsed into one concept
- **VERIFY:** NORSOK D-010 treatment of managed pressure drilling (dedicated section in Rev 5?) not confirmed

## Ch 5: Casing and tubular design  (16:41–19:55)

### 5.01 · 16:44 · 27.2s · anim **[GEN]** **[VERIFY]**

**VO:** Casing is the well's tunnel lining. It holds the hole open, contains pressure, and isolates formations. Its grade is a letter and a number: P one-ten means a minimum yield of one hundred and ten thousand psi, about seven hundred and sixty megapascals. Hydrogen sulphide drives hydrogen into hard steel and cracks it, so sour-service grades cap hardness, and P one-ten is too hard for most sour wells.

**SHOT:** Tunnel-lining cutaway analogy morphs into the casing string in the hole. A pipe tag reads "P110: 110 ksi ≈ 758 MPa". A hardness-vs-cracking sketch for sour service: H2S at the surface, hydrogen atoms diffusing into a hard steel lattice, a crack opening; a "sour grades: hardness capped" note.

**Terms introduced:** casing grade; sour service

- **VERIFY:** grade list and yield conversion are from memory of API 5CT / ISO 11960 (110 ksi = 758 MPa is arithmetic and exact); sour-service rule wording (ISO 15156-2) not checked

### 5.02 · 17:11 · 37.3s · anim **[GEN]** **[VERIFY]**

**VO:** Three loads, three ways to fail. Burst: pressure inside exceeds pressure outside, and the wall yields, like an over-pressured pipeline. Its rating is worked out on a wall twelve and a half percent thinner than nominal, the mill tolerance. Collapse: pressure outside, and the pipe gives way. Thin pipe buckles like a crushed can; thick pipe yields first. The diameter-to-thickness ratio decides which, and most casing sits in between. Tension: the string's weight hanging in mud, plus any pull on it, limited by the pipe body or, often, by the weaker connection.

**SHOT:** Three cross-section panels in sequence: a ring with net outward arrows (inside minus outside) swelling then yielding, with the Barlow-type formula 0.875 × 2Yt/D after; a ring with inward arrows: a thin ring buckles into an oval, a thick ring yields, a D/t slider shows the regime changing; a hanging string with a buoyed-weight arrow, a stretch indicator and a connection highlighted.

**Terms introduced:** diameter-to-thickness ratio

- **VERIFY:** the 0.875 factor and the four collapse regimes (yield, plastic, transition, elastic) are from memory of API TR 5C3 / ISO 10400

### 5.03 · 17:48 · 30.7s · anim **[GEN]** **[SIM]**

**VO:** The design basis picks the worst credible cases. For burst: typically a gas kick, with the well shut in, or the casing pressure test itself. For collapse: lost circulation, where mud drains away into cracked rock, lets the level inside the pipe fall, partly or completely, while the full mud column outside pushes in. For tension: the string's weight as it is lowered in, shock from sudden stops, and overpull, the extra pull needed to free it if it sticks.

**SHOT:** Three load-case cartoons on the well schematic: shut-in gas column with a surface pressure arrow (burst); the mud level inside the casing falling (partial, then full evacuation) with heavy mud outside (collapse); a string being lowered with a buoyed-weight arrow down at mid-string and an overpull arrow UP at the top (tension). A small "design basis" table fills in.

**Terms introduced:** design basis; lost circulation

- **SIM:** one load case per mode; real design bases list several per string

### 5.04 · 18:19 · 33.9s · anim **[GEN]** **[SIM]**

**VO:** But those ratings are one load at a time. Real casing is pulled, squeezed and pressurised at once. So we check the von Mises equivalent stress against yield, with a design factor. Plotted as an ellipse of axial force against pressure, it answers a puzzle. Does pulling on a pipe make it easier or harder to crush? [pause 2] Easier. Steel already stretched along its length has less strength left to resist being squeezed, so the collapse rating is corrected for tension too.

**SHOT:** The VME ellipse centred on the origin of an axial-force vs differential-pressure plane, touching the tension and compression yield lines at zero pressure, bulging beyond the API burst line in the tension quadrant and falling inside the collapse line there. The uniaxial rectangle for comparison; a red dot that passes uniaxial but fails von Mises in the tension-collapse corner. A shrunken inner ellipse labelled "design factor". The puzzle question on screen during the pause, then the answer.

**Terms introduced:** von Mises equivalent stress; design factor

- **SIM:** ellipse is the simplified VME yield envelope without bending or thermal load; collapse instability is checked separately (API/ISO collapse with tension correction); design factors are shown unlabelled as "operator-specific"

### 5.05 · 18:53 · 18s · anim **[GEN]**

**VO:** Each load peaks in a different place. Tension, and often burst, are worst at the top, where tension also eats into collapse strength. Collapse is worst at the bottom. So long strings are often tapered: thicker wall, or stronger steel, only where it is needed.

**SHOT:** A depth vs load/capacity plot: burst load peaking near the top, tension largest at the top, collapse largest at the bottom; a single-weight capacity line fails at both ends, then morphs into steps (stronger at top and bottom, lighter in the middle) that sit above every load curve. A casing string beside it colour-coded by section.

**Terms introduced:** tapered string

### 5.06 · 19:11 · 27.9s · anim **[GEN]** **[VERIFY]**

**VO:** And then the connections, here meaning the threaded joints between pipes. Basic threaded couplings seal with thread compound. Premium connections add metal-to-metal seals and a torque shoulder, to stay gas-tight. They are qualified by testing to ISO thirteen six seven nine, and checked during make-up, as they are screwed together, on a torque-turn plot: torque against turns. The pipe body may be fine; connections are where most leaks start.

**SHOT:** Thread cross-section: API round thread with a spiral leak path filled by thread compound; then a premium connection with a conical metal-to-metal seal at the pin nose and a torque shoulder (separate labels with leader lines). A torque-vs-turns plot with a sharp shoulder-engagement kink and an acceptance window.

**Terms introduced:** premium connection; torque-turn plot

- **VERIFY:** ISO 13679 as the connection-testing standard is from memory; "most leaks start at connections" is a generalisation

### 5.07 · 19:39 · 16.7s · anim **[NO]** **[VERIFY]**

**VO:** In the barrier language of chapter seven, the casing that seals off the well becomes a well barrier element: one object that helps stop flow, accepted on a documented design and a pressure test. The conductor is structure, not barrier.

**SHOT:** The well schematic: the last-set casing and its cement light up in blue with a "tested" tick and the label "well barrier element"; the 30 in conductor stays grey, labelled "structural, not a barrier".

**Terms introduced:** well barrier element

- **VERIFY:** element acceptance criteria wording in NORSOK D-010 for casing (design + test) not confirmed

## Ch 6: Cementing  (19:55–23:07)

### 6.01 · 19:58 · 21.2s · anim **[GEN]** **[NO]** **[VERIFY]**

**VO:** Cement does three jobs. It holds the pipe in place, stopping it from buckling or moving. It seals the gap, so nothing flows along the outside. And it shields the steel from corrosive fluids. The seal is the point: if it is long enough and verified, the cement behind the casing is a well barrier element.

**SHOT:** Cutaway of casing, cement sheath and rock with three labelled arrows (holds in place, seals, protects). The sheath then glows blue as a barrier element over a verified length, with the label "casing cement = a well barrier element".

- **VERIFY:** NORSOK D-010 requirements for casing cement as a well barrier element (required length/height and verification) not confirmed

### 6.02 · 20:19 · 36.4s · anim **[GEN]** **[SIM]**

**VO:** To place it, we pump down the inside and up the outside: a U-tube. Spacer goes first, to push the mud away. Then rubber plugs keep cement and mud apart, and pipeline engineers will recognise them: they are pigs. A bottom plug runs ahead of the cement, a top plug behind. A one-way float valve stops the heavier cement U-tubing back. When the top plug lands on the float collar, at the calculated volume, pressure jumps: displacement is complete. The few joints below it, the shoe track, stay full of cement on purpose.

**SHOT:** U-tube cutaway, fluids in colour: mud (amber), spacer (white), cement (grey). Order down the pipe: spacer, bottom plug, cement, top plug, then displacement mud. The bottom plug's membrane ruptures at the float collar; cement turns the corner at the shoe and rises in the annulus (flow particles). A one-way valve symbol on the float collar. The top plug lands on the float collar; a pump-pressure trace spikes ("plug bump"). The shoe track below the float collar stays grey.

**Terms introduced:** spacer; wiper plug; float valve; shoe track

- **SIM:** single-stage primary job; multi-stage tools and foam cement omitted; on a floater the plugs are subsea-release plugs at the casing running tool, launched by darts from the rig

### 6.03 · 20:56 · 29.5s · anim **[GEN]** **[SIM]**

**VO:** The hard part is mud removal: getting every bit of mud out of the annulus. If the pipe sits off-centre, mud on the narrow side barely moves, while cement races up the wide side. That leaves a channel of mud behind the pipe: a path for fluid, hidden. Centralisers push the pipe back towards the middle. Conditioning the mud, a well-designed spacer and a high pump rate do the rest; on land wells and liners, moving the pipe helps too.

**SHOT:** THE CEMENT DISPLACEMENT ANIMATION. A vertical slice of an eccentric annulus (wide gap left, narrow gap right) with an inset top-down ring. Cement fronts rise: the wide-side front races ahead, the narrow-side front lags; a mud channel is left trapped on the narrow side (red outline "channel"). Replay with bow-spring centralisers on the pipe: standoff improves, fronts rise nearly level and a clean grey sheath forms.

**Terms introduced:** centraliser; channelling

- **SIM:** front speeds are invented ratios; a real eccentric displacement needs CFD or a hydraulics simulator

### 6.04 · 21:25 · 39.1s · anim **[GEN]** **[VERIFY]**

**VO:** Cement is bound by the window too. While it is pumped, its column plus friction must stay below the fracture limit and above pore pressure. So a lighter lead slurry fills the upper annulus, and a dense, strong tail goes at the shoe, with the top of cement placed above every zone it must seal, like a thin overpressured sand near three thousand metres. Lab tests at downhole temperature and pressure measure how long it stays pumpable, its thickening time, and how fast it gains strength. Above about a hundred and ten degrees, as in our deepest sections, silica is added, so the strength does not fade.

**SHOT:** Window chart with the cement-column pressure line (hydrostatic plus friction) between pore and fracture for the 9⅝ in job; lead (lighter) and tail (denser) slurries in the annulus with a "top of cement" marker above a thin sand at ~2,980 m ("Sand A"). A lab panel: a thickening-time curve rising sharply (pressurised consistometer) and a compressive-strength curve vs time; a temperature axis with a mark at ~110 °C and a "silica" tag.

**Terms introduced:** thickening time

- **VERIFY:** silica addition above roughly 110 C is general industry knowledge from memory (strength retrogression), not checked against API/ISO cement standards

### 6.05 · 22:04 · 27.5s · anim **[GEN]** **[SIM]**

**VO:** Then comes a dangerous period, minutes to hours long. As cement sets, it starts to hold itself up, like concrete stiffening in a bucket. Its weight stops pressing down, so the pressure holding gas back falls, but it is not yet solid enough to block gas. If that pressure drops below a gas zone's, gas can slip in and leave a path. So timing is everything: good slurries set fast through that gap.

**SHOT:** Time axis with three coloured phases of the cement column: liquid (full hydrostatic), gel (the cement holds itself up, a pressure counter falls and crosses the gas-zone pressure line), solid. At the crossing, gas bubbles enter the cement through the wall and leave a thin channel. A second, fast-setting slurry closes the gap before the crossing.

- **SIM:** gel-strength mechanics reduced to one picture; no numbers given

### 6.06 · 22:32 · 35.4s · anim **[GEN]** **[SIM]**

**VO:** How do we know it worked? First, the job record: full returns, meaning no mud lost to the rock, the right volumes, a plug bump on time. Then, where it matters, logs. A cement bond log listens to sound travelling along the casing: good cement damps it. Ultrasonic tools map all round the pipe. But a log measures contact, not seal. A hairline gap, a microannulus, can make good cement look bad, and a narrow channel can slip past the tool. So we weigh it all together, with the pressure test at the shoe.

**SHOT:** A job-record checklist ticks first (full returns, volumes, plug bump). A logging tool in the casing emitting sound: waveform panels for free pipe (ringing) vs bonded pipe (damped). A 360° ultrasonic map with a coloured channel stripe. A microannulus sketch: a hairline gap makes good cement read "free pipe". Final checklist: returns, volumes, plug bump, shoe pressure test (LOT/FIT), logs.

**Terms introduced:** full returns; cement bond log; ultrasonic cement log; microannulus

- **SIM:** log responses are schematic, not real data

## Ch 7: Well control and barriers  (23:07–27:28)

### 7.01 · 23:10 · 16.6s · anim **[GEN]** **[SIM]**

**VO:** Suppose the window lied: pore pressure is higher than forecast. Or pulling the pipe swabbed the hole like a syringe, or losses dropped the mud level. Formation fluid enters the well. Unchecked, that kick becomes a blowout: a flow nobody can stop.

**SHOT:** The window chart around the open hole: the planned mud-weight staircase (1.49 sg to 3,400 m, then 1.62 sg to TD); a red "actual pore pressure" curve (forecast + 0.12 sg below 3,000 m) crosses the 1.62 sg line near 3,700 m; gas influx (crimson flow particles) enters the hole. A syringe cartoon: pipe withdrawal sucks fluid in (swab). A falling mud level from losses. A small "kick → blowout" arrow.

**Terms introduced:** swabbing

- **SIM:** the "actual" pore pressure is the forecast + 0.12 sg below 3,000 m, invented for this example

### 7.02 · 23:27 · 32.1s · anim **[GEN]** **[SIM]**

**VO:** A gas kick is deceptive. Here is a puzzle: a bubble of gas at four kilometres, where the pressure is over six hundred bar. How much bigger is it at the surface? [pause 2] Hundreds of times. So the pits first show only a small gain, then as the gas rises it expands, slowly at first, then violently near the top. In oil-based mud it dissolves and hides, then breaks out near the top, sometimes in the riser, above the preventer.

**SHOT:** THE KICK PROPAGATING UP THE ANNULUS. A tall annulus with a depth axis; a small crimson gas bubble at the bottom with a pressure counter (~640 bar) and a volume counter; during the pause the question "how much bigger at the surface?". As it rises it grows (Boyle), the pit-gain trace next to it shows a small step at influx, stays nearly flat, then spikes in the last few hundred metres ("expansion is back-loaded"). A second variant: the bubble is shaded "dissolved in oil-based mud" until a break-out depth near the top, above the BOP in the riser.

- **SIM:** expansion factor is ideal-gas Boyle with no temperature or compressibility factor, no slip velocity, no mud solubility curve

### 7.03 · 23:59 · 25.9s · anim **[GEN]** **[VERIFY]**

**VO:** So we watch. Flow out greater than flow in. A rising level in the mud tanks, the pits. On a trip, a hole that takes less mud than the steel we pulled out. A sudden faster drilling rate, a drilling break, is a warning: stop the pumps and watch the well. That is a flow check. The aim is to catch a kick while it is still small.

**SHOT:** A dashboard of gauges lighting up in turn: flow in vs flow out difference needle; pit volume trace (counter); trip tank: mud taken vs steel volume pulled; rate-of-penetration spike labelled "warning"; then a flow check: pumps off, the well keeps flowing, red. Caption: "catch it while it is still small".

**Terms introduced:** drilling break; flow check

- **VERIFY:** no numeric detection-volume target is claimed

### 7.04 · 24:25 · 41.4s · anim **[NO]** **[VERIFY]** **[SEEN]**

**VO:** Remember the two barriers? In Norway the rule is blunt: wherever a formation could flow to the surface, two independent well barriers must stand in the way. Each is a well barrier envelope: a set of elements that together stop flow. While drilling, the primary barrier is the mud column. The secondary barrier is the rock just below the last casing shoe, the casing cement, the casing, the wellhead and the preventer. Independence is the whole point: two airlock doors that must never fail together. Barriers must be tested, and if one fails, the only work allowed is restoring it. A kick is exactly that: the mud barrier has failed.

**SHOT:** THE BARRIER SCHEMATIC. Flat 2-D panel (outline only): the well schematic with the primary envelope outlined in blue around the mud column, and the secondary envelope outlined in red around the formation at the shoe (the outline closes across the open hole just below the shoe, labelled "formation at shoe, tested by leak-off"), casing cement, casing, wellhead and BOP. An airlock cartoon with two doors and an interlock. A "barrier lost: only restoration work" banner, then the blue envelope breaks where the kick enters.

**Terms introduced:** well barrier envelope; primary barrier; secondary barrier

- **VERIFY:** the in-situ formation below the shoe as a secondary well barrier element while drilling is from memory of the NORSOK D-010 drilling schematic; whether D-010 permits "common" well barrier elements with a risk assessment is not confirmed; the narration says only "independent". Blue/red colour convention for primary/secondary is from memory
- **SEEN:** Activities Regulations s.85 (tested barriers with sufficient independence; if one fails only restoration work may continue) and Facilities Regulations s.48

### 7.05 · 25:06 · 32.6s · anim **[GEN]** **[SIM]**

**VO:** When a kick is suspected: lift the bit off bottom so no pipe joint sits in the preventer, stop the pumps, check for flow, and close the well. Now it is shut in, and the gauges hide a gift. The annulus holds gas of unknown size, but the drill pipe holds clean mud we know. Drill pipe and annulus form a U-tube: once the gauges settle, pressure at the bottom is that clean mud column plus the shut-in drill pipe pressure. One reading, and we know the pore pressure.

**SHOT:** Shut-in sequence icons (bit off bottom, pumps off, flow check, BOP closes). Then a U-tube: the drill pipe leg full of clean amber mud, the annulus leg with a crimson gas slug; two surface gauges (SIDPP, SICP) settle. An equation card built from the well model: mud in the pipe 636 bar (1.62 sg, 4,000 m) + SIDPP 18 bar = pore pressure 654 bar.

**Terms introduced:** shut-in drill pipe pressure

- **SIM:** numbers from the illustrative "actual" pore pressure (forecast + 0.12 sg); float valves in the BHA and hard vs soft shut-in practice not covered

### 7.06 · 25:39 · 36.2s · anim **[GEN]** **[SIM]**

**VO:** To kill the well we need kill mud: just heavy enough to balance the pore pressure on its own. That is the old weight plus the shut-in drill pipe pressure divided by g times the true vertical depth. The driller's method does it in two circulations: first, the old mud carries the kick out while the choke holds bottom-hole pressure just above pore pressure; then kill mud replaces the old mud. Wait-and-weight does both at once. With a subsea preventer, friction in the long choke line adds pressure, so we pump slowly and correct for it.

**SHOT:** Equation: KMW = MW + SIDPP / (g · TVD) = 1.62 + 18.3 / (0.0981 × 4,000) ≈ 1.67 sg. Two-column well: circulation 1, the crimson gas leaves up the annulus with the old amber mud through the choke (flow particles) while a BHP gauge stays level; circulation 2, darker kill mud (KILL_MUD) displaces the old mud down the pipe and up the annulus. A choke-line friction arrow along the long line from the seabed to the rig. A small "wait-and-weight: one circulation" note.

**Terms introduced:** kill mud; driller's method

- **SIM:** volumetric method and bullheading not covered; the kill-mud weight ignores a safety margin

### 7.07 · 26:15 · 32.3s · anim **[GEN]** **[SIM]**

**VO:** The weak point is the shoe, the top of the open hole. Rising gas expands, so the choke adds pressure to hold the bottom steady, and that pressure peaks at the shoe as the gas arrives. Take too big a kick, or one too far above our mud weight, and the shoe pressure passes the limit a leak-off test measures, repeated below every shoe: the rock cracks and fluid escapes underground. The biggest kick that survives is the kick tolerance, one of the margins built into chapter one's staircase.

**SHOT:** Annulus with a gas slug rising during circulation; a pressure trace at the 9⅝ in shoe (3,400 m) climbs as the top of the slug approaches and peaks as it arrives, against the shoe limit line (fracture 1.71 sg, measured by the leak-off test). A bigger slug pushes the peak over the line: a crack and losses underground. Label "kick tolerance = biggest kick that keeps this peak below the line".

**Terms introduced:** kick tolerance

- **SIM:** kick tolerance shown as a concept, no calculation

### 7.08 · 26:47 · 40.4s · anim **[GEN]** **[SEEN]**

**VO:** In twenty ten, on the Macondo well in the Gulf of Mexico, barriers failed one after another. The cement at the bottom of the well did not seal the reservoir. A negative pressure test, on the Norwegian shelf called an inflow test, drops the pressure inside the well below the rock's to prove the seal holds. Its warnings were explained away, and the heavy mud was replaced with seawater. The kick went unnoticed for about forty minutes. The preventer did not seal. Eleven people died. No single failure did that: every barrier had a flaw, and every warning was explained away.

**SHOT:** A restrained, factual timeline on the barrier schematic: elements turn grey one by one with labels (bottom cement / shoe track, inflow test misread, mud displaced to seawater, kick missed ~40 min, BOP failed to seal). A simple text card: "Macondo, 2010 · 11 lives lost". No dramatic imagery.

**Terms introduced:** negative pressure test

- **SEEN:** facts match CSB / BP / IADC summaries in web search results (bottom cement and shoe-track barrier failure, negative pressure test misinterpreted, displacement to seawater, kick indications missed for roughly 40 minutes, BOP failure, eleven fatalities); primary investigation reports not read in this environment

## Ch 8: Formation evaluation: discovery or dry hole?  (27:28–32:16)

### 8.01 · 27:30 · 20.4s · anim **[GEN]**

**VO:** Now the question flips. Until now it was how to get there safely; now it is what we found. A well is an expensive way to buy measurements, and they rank from fast, cheap and uncertain, to slow, costly and definitive. The order on this ladder is by price, not by time.

**SHOT:** A ladder diagram descending the screen: mud log, logging while drilling, wireline, pressures and samples, core, well test. Each rung has a time-to-result and a certainty bar; the cost bar grows. A small note: "ranked by cost and certainty, not by time".

### 8.02 · 27:51 · 20.8s · anim **[GEN]** **[SIM]**

**VO:** First, the mud log. Geologists describe the cuttings coming up with the mud, and look at them under ultraviolet light, where oil glows. A gas chromatograph measures the gases in the mud. But there is a delay: the lag time, annulus volume divided by flow rate, means cuttings are old news when they arrive.

**SHOT:** Cutaway annulus with a bit cutting a layer; a coloured cutting particle rises with the mud (flow particles) over a time counter ("lag"), arriving at a shaker minutes later. A UV-lit tray with a glowing yellow cutting. A chromatograph trace with peaks labelled C1 to C5.

**Terms introduced:** mud log; lag time; gas chromatograph

- **SIM:** lag time shown as a single number; no recycled-gas or bit-metamorphism cautions in the narration

### 8.03 · 28:12 · 36.2s · anim **[GEN]** **[SIM]** **[VERIFY]**

**VO:** Next, logging while drilling, LWD: sensors a few metres behind the bit, reading the rock minutes after it is cut. Gamma ray usually separates shale from sand. Resistivity: hydrocarbons conduct poorly, so high resistivity can mean oil or gas. Density and neutron give porosity, the fraction of the rock that is pore space; where the two curves cross over, that is the signature of gas. A thin stream of data climbs the pipe as pressure pulses in the mud, a few bits per second; the full log waits in the tool's memory.

**SHOT:** Scrolling log tracks vs depth over the reservoir interval with synthetic curves (gamma ray, resistivity, density-neutron) drawn on as the sensors pass, a few metres behind the bit. The density-neutron crossover in the gas leg is highlighted ("gas"). A mud-pulse line with a data-rate counter ("a few bits/s") and a memory chip icon ("full log in memory").

**Terms introduced:** logging while drilling; gamma ray; resistivity; porosity

- **SIM:** log curves are synthetic and generated from the well model
- **VERIFY:** telemetry rate "a few bits per second" is a rounded memory figure

### 8.04 · 28:48 · 26.8s · anim **[GEN]** **[SIM]**

**VO:** Why can resistivity find oil? Picture the rock as a sponge soaked in salty water. Current flows through the salt water. Replace some with oil, an insulator, and less current flows. Archie's equation turns that into numbers: water saturation from porosity, measured resistivity and the salt water's own resistivity. Simplified: clays conduct too, so shaly sands need extended versions.

**SHOT:** Sponge cartoon with a salty-water current path (flow particles); oil droplets replace water and the current path narrows. Then the equation Sw = (a·Rw / (φ^m·Rt))^(1/n) with Sw highlighted and Rw labelled "salt water's resistivity", worked example from the model (Rw 0.05, φ 0.23, Rt 23.6 → Sw ≈ 0.20). A caption: "shaly sands: extended models".

**Terms introduced:** water saturation

- **SIM:** Archie only; no Simandoux or Waxman-Smits

### 8.05 · 29:15 · 41.8s · anim **[GEN]** **[SIM]** **[VERIFY]**

**VO:** After the bottom section is drilled, more logs run on a cable: wireline. Then comes the best trick. A formation tester presses a probe against the rock and measures pressure at a series of depths. In a fluid column, pressure rises with depth at that fluid's own weight: gas, about a quarter of a bar per ten metres; oil, about three quarters; water, about one bar. Plot pressure against depth and the slopes differ. Where the oil line meets the water line is the free-water level, found from pressures alone. Here the well crossed it, but the same trick finds a contact a well never reached, using water pressures from a neighbouring well.

**SHOT:** THE PRESSURE GRADIENT PLOT. A wireline formation tester probe sets on the wall at stations down the reservoir. Pressure (bar) vs depth (m): dots appear one by one in the gas leg, the oil leg and the water leg (the well crossed into the water leg); three straight lines fit them (slopes 0.025, 0.076, 0.106 bar/m); the oil and water lines meet at 4,052 m ("FWL"), the gas/oil crossing marks the gas-oil contact at 3,990 m. A last ghost example: oil points only, with the water line borrowed from a neighbouring well.

**Terms introduced:** wireline; formation tester; free-water level

- **SIM:** gradients (0.025 / 0.076 / 0.106 bar/m) and contacts are the model's invented values
- **VERIFY:** typical reservoir-condition fluid gradients quoted from memory

### 8.06 · 29:56 · 22s · anim **[GEN]** **[SIM]**

**VO:** The tool also pumps out samples, analysed downhole and in the lab. If two sands sit on different pressure lines, they are not in pressure contact; sharing a line suggests a connection but does not prove one. And the free-water level is a pressure surface: the oil-water contact on the logs is a little higher, because of capillary forces.

**SHOT:** Sample bottle filling in the tool with an optical-analysis dial; two pressure-vs-depth plots, one single line, one with a visible offset between two sands labelled "not in pressure contact". A thin zoom on the contact: the FWL (pressure) and a slightly higher OWC (logs, 6 m above) with a small transition zone.

- **SIM:** transition zone thickness illustrative (the model puts the OWC 6 m above the FWL)

### 8.07 · 30:18 · 31.3s · anim **[GEN]**

**VO:** A core is the only large, intact piece of the rock: a cylinder cut by a hollow bit while the reservoir is being drilled, unlike crushed cuttings or thumb-sized sidewall plugs. The lab gives porosity, permeability, how easily fluid flows through the rock, and, for a mechanical engineer's pleasure, triaxial strength tests that calibrate our collapse and rock-strength models; the fracture limit still comes from leak-off tests. Routine results take weeks, special tests months.

**SHOT:** A hollow core bit cutting a cylinder, the core barrel being pulled and laid out on a tray, next to crushed cuttings and small sidewall plugs for scale ("the only intact sample"). A triaxial test cell with a stress-strain curve and a Mohr-Coulomb envelope; a permeability plug test cartoon.

**Terms introduced:** core; permeability

### 8.08 · 30:50 · 33.1s · anim **[NO]** **[VERIFY]** **[SEEN]**

**VO:** The last rung is a drill stem test, DST. A liner is cemented across the reservoir, then temporary pipe, a seal called a packer and downhole valves let the well flow to surface. We shut it in and watch the pressure build up: that gives productivity, permeability, near-well damage and boundaries. But it is costly, it burns hydrocarbons, and in Norway emissions are tightly controlled and taxed. So operators often rely on logs, pressures and samples, and our example well does exactly that.

**SHOT:** A test string in a liner cemented across the reservoir (liner hung inside the 9⅝ in casing), with a packer, a downhole valve and surface test equipment (separator, burner) drawn simply. A rate-vs-time and a pressure build-up plot with the log-time derivative bump. A small "NO: flaring and CO2 tax" note. The test string fades: "our well: logs, pressures, samples".

**Terms introduced:** drill stem test; liner; packer

- **VERIFY:** how often DSTs are run on the NCS and the exact permit route are not confirmed; the narration avoids a frequency claim
- **SEEN:** flaring prohibited except brief testing and safety (World Bank flaring summary)

### 8.09 · 31:23 · 23.2s · anim **[GEN]** **[SIM]**

**VO:** Then interpretation. Set cutoffs: rock with too much shale, too little porosity, or too much water does not count. Net reservoir over gross thickness is the net-to-gross ratio, here about nought point nine four. Net pay, eighty-nine metres, is the part that holds hydrocarbons. Our cutoffs are illustrative; real ones depend on the field.

**SHOT:** The log tracks return with coloured flags added in three passes (net sand, net reservoir, net pay coloured by fluid: gas crimson, oil green); a thickness bar chart for gross 160 m, net reservoir 151 m, net pay 89 m; "N/G = net reservoir / gross = 151 / 160 = 0.94" computed live; net pay shown separately.

**Terms introduced:** cutoff; net-to-gross ratio; net pay

- **SIM:** cutoffs are invented (shale volume, porosity, water saturation); real cutoffs are field-specific

### 8.10 · 31:46 · 30.1s · anim **[NO]** **[VERIFY]** **[SEEN]**

**VO:** So, is ours a discovery? Hydrocarbons present: about forty metres of gas over some fifty-five metres of oil. Movable: the tester pumped them out of the rock. The Norwegian Offshore Directorate calls that a discovery: probably movable petroleum, shown by testing, sampling or logging. That bar is technical: it says nothing yet about whether the find will pay. And a dry hole would still be data about the basin.

**SHOT:** A decision tree lights its branches in turn: hydrocarbons present? (gas 40 m over oil ~56 m, from the model contacts) movable? (sample bottle) how much? The Sodir definition appears as a quote card ("covers technical and commercial discoveries"); the final node lights "DISCOVERY (technical)", with the "DRY: still data" branch greyed.

**Terms introduced:** discovery; dry hole

- **VERIFY:** well-result category names and discovery notification rules not confirmed
- **SEEN:** Sodir definition of a discovery and of a wildcat well (Sodir pages in web search results)

## Ch 9: Plugging and abandonment  (32:16–36:02)

### 9.01 · 32:19 · 35.9s · anim **[GEN]** **[NO]** **[VERIFY]**

**VO:** Now the twist. We found oil, and we are going to seal this well for ever. Why? [pause 2] An exploration well is a measuring instrument, not a producer; if the field is developed, it gets new wells built for the job. So this one gets plugging and abandonment, P and A: sealed from reservoir to seabed, for geological time. And it is designed in from the start: an outline plan exists before the first metre is drilled, and the detailed programme is written once the logs tell us what we found.

**SHOT:** The finished well schematic with the discovery highlighted (gas over oil); during the pause, a big "WHY?" question. Then the well becomes a thin tube connecting the reservoir (high-pressure gauge) to the seabed (open end) with the caption "sealed for geological time". A planning icon: "outline P&A plan before spud → detailed programme after logging".

**Terms introduced:** plugging and abandonment

- **VERIFY:** that NORSOK D-010 has an eternal-perspective design basis for permanent barriers, and when the P&A programme must exist, are from memory, not confirmed

### 9.02 · 32:55 · 23.5s · anim **[NO]** **[VERIFY]**

**VO:** First, find every source of inflow. Not only the reservoir: any permeable layer with pressure. In our well, a thin overpressured sand at three thousand metres, drilled through weeks ago, could push fluid all the way to the seabed. Under the Norwegian standard, a hydrocarbon zone, or an overpressured zone that can flow to the seabed, needs two permanent barriers.

**SHOT:** The well schematic with the reservoir interval (3,950 to 4,110 m) and the thin overpressured "Sand A" (2,980 to 3,000 m) highlighted with flow-potential arrows (flow particles) heading up the wellbore. Two barrier brackets at each source: primary (blue outline) and secondary (red outline); Sand A's secondary may be shared with a shallower plug.

**Terms introduced:** permanent well barrier

- **VERIFY:** barrier count per source (two for hydrocarbon-bearing or overpressured zones with flow potential to surface, one for other permeable zones) from memory of NORSOK D-010, not confirmed; no minimum lengths or test pressures are narrated

### 9.03 · 33:18 · 25.8s · anim **[NO]** **[VERIFY]** **[SEEN]**

**VO:** A permanent barrier must seal across the whole cross-section of the well, every annulus included, and sit against tight rock strong enough not to crack under the pressure below: rock to rock. Think of sealing a tunnel. A door in the corridor is no use if there is a gap behind the tunnel lining. A plug inside the casing is no use if fluid can run behind it.

**SHOT:** Two cutaway cross-sections side by side: left, a plug inside casing with a leak path arrow (flow particles) running up an uncemented annulus behind it (fails, red); right, a plug spanning casing, annulus cement and tight caprock on all sides (holds). A tunnel sketch with a door and a gap behind the lining. All cement grey; "holds" shown with a green outline and tick.

**Terms introduced:** rock to rock

- **VERIFY:** exact wording
- **SEEN:** D-010 Rev 5 permanent barriers extend across the full cross-section, sealing vertically and horizontally with all annuli closed (secondary web summaries)

### 9.04 · 33:44 · 31.1s · anim **[NO]** **[VERIFY]** **[SEEN]**

**VO:** In open hole, the plug already sits against the rock. Behind casing there are three ways. If the cement behind the casing is good, proven by a log and the job record over enough length, it can form part of the barrier; our overpressured sand is covered by the cement from chapter six. Or we mill a window in the casing, section milling, and plug against the rock. Or we perforate the casing, wash the annulus clean, and pump cement: perforate, wash, cement.

**SHOT:** An open-hole plug against rock (no extra work). Then three cased-hole panels in sequence: (a) a bond log with a good interval across Sand A, top of cement above it, and a plug placed across it; (b) a section mill cutting a window out of the casing and leaving open hole against the rock; (c) perforating guns firing, a wash tool jetting behind the casing, cement filling the cleaned annulus.

**Terms introduced:** section milling; perforate wash cement

- **VERIFY:** any acceptance criteria and qualification matrix not read
- **SEEN:** perforate-wash-cement recognised in NORSOK D-010 Rev 5 (vendor blog and SPE review)

### 9.05 · 34:15 · 36.1s · anim **[GEN]** **[SIM]** **[VERIFY]**

**VO:** To place a plug in casing, first set a mechanical base: a bridge plug, a steel-and-rubber plug that seals the casing and holds the cement up. In open hole, a thick, viscous pill does that job. Then cement is pumped through open-ended pipe as a balanced plug: the fluid columns inside and outside the pipe weigh the same, so, like the U-tube we met earlier, nothing surges up or drops out. The pipe is pulled slowly out of the cement, and any excess is circulated out. In our drawing, the plug is about a hundred metres long.

**SHOT:** THE PLUG PLACEMENT ANIMATION, depicting the cased-hole plug across Sand A (~2,900 to 3,000 m in the 9⅝ in casing): a bridge plug sets; the drill pipe lowers to just above it; spacer, cement, spacer are pumped; the columns inside the pipe and in the annulus balance; the pipe is pulled up through the cement leaving a clean grey plug; a reverse-circulation arrow clears the excess above. Plug length dimensioned ~100 m, "drawing only". An inset: an open-hole plug resting on a viscous pill.

**Terms introduced:** bridge plug; balanced plug

- **SIM:** plug length of about 100 m is a drawing value, not a requirement
- **VERIFY:** minimum plug lengths in NORSOK D-010 Rev 5 (a secondary search summary quotes 100 m open hole / 50 m cased on a mechanical base / 30 m with a qualifying bond log) are NOT narrated

### 9.06 · 34:51 · 28.5s · anim **[NO]** **[VERIFY]**

**VO:** And then we prove it. Before the plug goes in, the cement behind the casing is logged. After it sets, we tag it: lower the pipe until it rests on the plug, and load it with weight. In casing, we pressure test it, usually from above, and where we can, with an inflow test from below. An open-hole plug is proven by the tag. A barrier that has not been verified is not a barrier.

**SHOT:** Sequence: a bond-log tool logging the cement behind the casing ("logged before the plug"); drill pipe set down on top of the hardened plug with a weight indicator; a pressure test from above with a gauge holding flat; a small inflow-test arrow from below. A green "VERIFIED" outline and tick land on the plug.

**Terms introduced:** tag the plug

- **VERIFY:** tag weight and test pressure requirements deliberately not stated

### 9.07 · 35:20 · 26.3s · anim **[NO]** **[VERIFY]** **[SEEN]**

**VO:** Last, the steel: cut and pull. We cut the casing and conductor below the seabed, and lift out the wellhead. An ROV survey checks the seabed is clear, with nothing left for a fishing trawl to catch. And a modern exploration well cannot sit in limbo: temporary abandonment, plugged but with the wellhead left so we can come back, is time-limited on the Norwegian shelf.

**SHOT:** A casing cutter inside the strings cuts below the seabed; the wellhead and guide base lift away. ROV view sweeps the seabed: debris check, a clean seabed with a low mound of old cuttings. A calendar icon with a "limit" tag for temporary abandonment.

**Terms introduced:** cut and pull; temporary abandonment

- **VERIFY:** cutting depth, seabed clearance requirement and who sets it not confirmed; the narration states no figures
- **SEEN:** Havtil report states exploration wells begun after 1 January 2014 may not be temporarily abandoned longer than two years (search summary)

### 9.08 · 35:46 · 15.7s · anim **[NO]** **[VERIFY]**

**VO:** Finally, a last plug just below the seabed seals the well off from the sea, and an as-abandoned drawing is filed. It is the last page in the well's life, and it has to be right for the long term.

**SHOT:** The final as-abandoned schematic built from one plug list (the same as the well strip): reservoir plugs in open hole, the Sand A plug in casing, a shallow plug just below the seabed; all plugs in cement grey with green "verified" outlines; the cut-off casing stubs below the seabed, the seabed clean. The drawing is stamped and filed into an archive icon.

- **VERIFY:** the exact reporting duty to the authorities not confirmed

## Ch 10: Outro: the empty seabed  (36:02–36:42)

### 10.01 · 36:02 · 34.8s · anim **[GEN]**

**VO:** So how do you stay inside the window for four kilometres? You don't, not all at once. You win it a few hundred metres at a time, lock each stretch behind steel and cement, keep two barriers between the rock and the sea, and watch every barrel that comes back. A well is an argument with the Earth, about pressure, that you have to win every hour. And at the end, you seal the win so it lasts for ever. Three hundred metres down, there is barely a trace.

**SHOT:** The window chart from the opening returns with the casing staircase drawn over it (section by section), then two barrier outlines, then a flow-in/flow-out needle. It dissolves into the seabed from Chapter 0: bare, still, a low mound of old cuttings; beneath the mud, faint ghosted plugs and cut casing stubs. The camera rises slowly through the water column to the surface.

### 10.02 · 36:36 · 5.3s · still **[GEN]**

**VO:** *(none: visual only)*

**SHOT:** End card on dark background: "THE HOLE THAT FIGHTS BACK", then small print: "Illustrative composite well: invented numbers, real physics. Norway-specific material carried a red NORWAY / NORSOK-SPECIFIC badge. Verify any requirement against NORSOK D-010 and the current regulations before relying on it." Credits line: "Voice: Kokoro-82M neural TTS · Animation: generated in code".

*Total narration: 5605 words ≈ 153 wpm averaged over the runtime.*
