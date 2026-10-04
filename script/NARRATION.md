# Narration script and shot list (generated: do not edit; edit `chNN_*.md` and run `make script`)

Runtime 30:00 · tags: **[NO]** Norway-specific · **[GEN]** general industry · **[SIM]** deliberate simplification · **[VERIFY]** not confirmed against a primary source · **[SEEN]** seen only in a secondary/web source

## Ch 0: Cold open: the window  (0:00–1:30)

### 0.01 · 0:00 · 17s · anim **[GEN]**

**VO:** This is North Sea seabed, three hundred metres down. Soon a drill will reach four kilometres into the rock beneath it. A few weeks later, it will all be gone, and the seabed will look exactly like this.

**SHOT:** Side-view descent from the sea surface through particle-speckled water to a bare seabed. Hold. A thin horizontal "300 m" depth tick passes. Title fades in over the seabed: "THE HOLE THAT FIGHTS BACK" and then out.

### 0.02 · 0:17 · 16s · anim **[GEN]** **[SIM]**

**VO:** Everything in between comes down to one problem. A well is a hole full of liquid, called drilling fluid, or mud, and we choose how heavy it is. Our well is illustrative: invented numbers, real physics.

**SHOT:** Cutaway: a vertical hole through layered rock, filled with amber liquid. To the right, a vertical slider labelled "weight of the mud" with a marker. A small badge reads "ILLUSTRATIVE WELL".

**Terms introduced:** drilling fluid

- **SIM:** composite wildcat; every number in the video comes from one made-up well model (scenes/common/well_model.py)

### 0.03 · 0:33 · 17.5s · anim **[GEN]**

**VO:** Deep rock is under pressure. Make the mud too light, and the rock pushes fluid in: a kick. Make it too heavy, and you crack the rock; the mud drains away, the level drops, and you are too light again.

**SHOT:** Slider moves down: blue arrows push from the rock walls into the hole, label "KICK" flashes. Slider moves up: red cracks open in the wall, amber liquid drains into them, the liquid level in the hole falls, then the blue arrows return.

**Terms introduced:** kick

### 0.04 · 0:50 · 23.5s · anim **[GEN]** **[SIM]** **[VERIFY]**

**VO:** So the weight must live inside a window. In our well, that mud weight window is about a seventh of the fluid's weight wide. In the hottest wells it can shrink to a few hundredths. Pause, and guess: how do you stay inside it, for four kilometres?

**SHOT:** The slider becomes a two-sided gauge: a blue "kick" zone below and a red "crack" zone above, with a narrow green band between. The band shrinks as the camera pulls out and a caption reads "how wide?". Hold for the pause.

**Terms introduced:** mud weight window

- **SIM:** "about a seventh": model window at TD is 1.54 to 1.76 sg, i.e. 0.22 sg on 1.62 sg of mud (13.6 %)
- **VERIFY:** "a few hundredths" for the hottest, highest-pressure wells is from memory (HPHT windows on the NCS), no primary source read

### 0.05 · 1:14 · 16s · anim **[GEN]**

**VO:** That is our question: how do you drill four kilometres through rock that wants to collapse or blow out, then leave the hole so safe nobody ever has to think about it again? First, a plan.

**SHOT:** The question types on screen over the gauge. The depth ruler and an empty well schematic slide in at the left edge (the persistent "well so far" strip). Cut to the planning chapter.

## Ch 1: Planning: casing from the bottom up  (1:30–5:30)

### 1.01 · 1:30 · 23s · anim **[GEN]** **[SIM]**

**VO:** Before anyone drills, someone decides what the hole is for. Geologists have picked a target: a sandstone at about three thousand nine hundred and fifty metres. Depth here means true vertical depth, TVD: straight down, not along the hole. Our job is to reach it safely, and find out what is in it.

**SHOT:** Cross-section of the North Sea: sea surface, seabed at 300 m, layered strata, a highlighted sandstone target at 3,950 m. Vertical dashed line labelled "TVD" and a wavy path labelled "measured depth" beside it. Depth ruler appears at left.

**Terms introduced:** target; true vertical depth

- **SIM:** all depths are TVD below sea level in a near-vertical well; rig-floor air gap ignored

### 1.02 · 1:53 · 29s · anim **[GEN]**

**VO:** Start with something you know. Dive ten metres and you feel one more bar. Hydrostatic pressure is density times gravity times depth. Mud is just a heavier liquid, and we quote its weight as specific gravity, sg: water is one. Rock pores hold fluid too, at a pore pressure. If they connect up to the sea, it is a column of water, and the pressure is normal.

**SHOT:** A diver icon with a 1 bar per 10 m gauge; then a column of water and a column of amber mud side by side with pressure-vs-depth lines. Then a rock block with magnified pores filled with blue fluid and a pressure gauge, connected by a thin channel to the sea.

**Terms introduced:** hydrostatic pressure; specific gravity (sg); pore pressure

### 1.03 · 2:22 · 26s · anim **[GEN]** **[SIM]**

**VO:** But sometimes fluid is trapped. Picture a water-filled cylinder with a spring, closed by a piston with a tiny hole. Load the piston: the water carries it first, then leaks, and the spring takes over. Block the hole, and the water keeps carrying the load: overpressure. What the grains carry is the effective stress: total stress minus pore pressure.

**SHOT:** Terzaghi piston-and-spring animation: load applied, pressure gauge jumps, water streams through the hole while the spring compresses and the gauge falls. Replay with the hole blocked: gauge stays high, spring barely moves. Equation appears after the animation: sigma-prime equals sigma minus p.

**Terms introduced:** overpressure; effective stress

- **SIM:** single-mechanism picture (disequilibrium compaction); other overpressure mechanisms exist and are not shown

### 1.04 · 2:48 · 25.5s · anim **[GEN]** **[SIM]**

**VO:** Now the other wall of the window. A hole in a plate concentrates stress, two to three times over, around its edge. Pressure inside the hole pushes back. Push hard enough and the rock splits: the fracture gradient. Too little, and the wall collapses. A leak-off test, pressurising the hole until the rock takes fluid, measures it directly.

**SHOT:** Plate-with-hole stress contour cartoon around a borehole circle: hoop stress arrows concentrated at the wall. Then internal pressure slider raising: a split opens at the wall at high pressure; at low pressure the wall chips inward. Small teaser pressure-vs-volume curve labelled "leak-off test".

**Terms introduced:** fracture gradient; leak-off test

- **SIM:** the factor depends on the stress state: about two for equal horizontal stresses, up to three for a uniaxial field (Kirsch)

### 1.05 · 3:14 · 30s · anim **[GEN]** **[SIM]**

**VO:** Plot both limits against depth, as an equivalent mud weight, the mud weight that would give that pressure. Pore pressure on the left, fracture on the right. The mud must stay between them, with a margin each side. In an overpressured basin the window narrows with depth, because pore pressure climbs faster than the rock's strength against fracture. Simplified: I draw the lower limit as pore pressure alone.

**SHOT:** THE CORE CHART. Axes: equivalent mud weight (sg) horizontal, depth vertical (down). Blue pore-pressure curve draws on from the seabed downwards, then the orange fracture curve, the green window fills between them and visibly narrows below 3,000 m. Margins appear as thin dashed offsets. Small caption: "lower limit drawn as pore pressure only".

**Terms introduced:** equivalent mud weight

- **SIM:** lower limit drawn as pore pressure only; model collapse curve exists in well_model but is shown from Ch 4 on

### 1.06 · 3:44 · 19.5s · anim **[GEN]** **[SIM]** **[VERIFY]**

**VO:** Near the seabed, hazards must be ruled out first. Shallow gas: pockets only a few hundred metres down that can arrive fast, with little warning. Boulders left by glaciers. Soft, uneven seabed. A seabed survey looks for all of them before the rig arrives.

**SHOT:** Seabed cutaway: a red gas pocket under a thin cap, boulders in glacial till, a pockmark. A survey ship icon with a dotted sonar fan sweeps over, hazards light up with labels.

**Terms introduced:** shallow gas

- **SIM:** shallow water flow, common in other basins, omitted
- **VERIFY:** whether a seabed/shallow-gas survey is a Norwegian regulatory requirement (and its wording) not confirmed

### 1.07 · 4:03 · 29.5s · anim **[GEN]** **[SIM]**

**VO:** Now the clever part: where do we put steel pipe, called casing, to hold the hole open? We design from the bottom up. At total depth we need about one point six two sg. Draw that line up until it meets the fracture curve, less margins; above that the hole would crack. So casing must end below it. The bottom end of a casing string is its shoe.

**SHOT:** On the window chart, a vertical amber line at 1.62 sg from TD 4,200 m rising until it meets the fracture curve minus margin (dashed) at about 3,370 m; a red band marks "would crack above here". A casing string with a shoe symbol telescopes down from the seabed to the first valid depth.

**Terms introduced:** casing; casing shoe

- **SIM:** margins are invented: 0.07 sg trip/ECD allowance on pore pressure, 0.03 sg below fracture, plus a 150 m gas-kick term (see well_model.py)

### 1.08 · 4:32 · 28.5s · anim **[GEN]** **[SIM]**

**VO:** Set that string at about three thousand four hundred metres. The section above used lighter mud, one point four nine sg, so repeat: the next shoe lands at two thousand metres. The mud above that, one point one two sg, is so light that other things decide: shallow hazards, and anchoring the safety valves we add shortly. About a thousand metres. The result is a staircase.

**SHOT:** Repeat of the stair-step: from 3,400 m the amber line steps left to 1.49 sg and rises to meet fracture at ~2,000 m (string 2 telescopes into place); step again to 1.12 sg: line meets fracture at 660 m, but a label "BOP anchor + shallow hazards: not shallower than 1,000 m" snaps the third shoe to 1,000 m. Three shoes + the conductor, drawn as nested strings.

- **SIM:** the surface-casing depth floor of 1,000 m is an assumption standing in for hazard and kick-tolerance reasoning

### 1.09 · 5:01 · 29s · anim **[GEN]** **[SIM]**

**VO:** The strings nest like a telescope, because each must pass through the one above. So the sizes step down: thirty inch, twenty, thirteen and three eighths, nine and five eighths, then eight and a half inch to the bottom. Every string costs diameter. And this is a wildcat, an exploration well with no neighbours to learn from, so the forecast is uncertain: the plan carries contingency strings.

**SHOT:** Nested casing strings drawn to scale in a cross-section ring view and in a side telescoping view with size labels. A dashed "7 in liner" and "contingency" string appears in reserve. Caption: "wildcat = no offset wells".

**Terms introduced:** wildcat; contingency string

- **SIM:** standard NCS-style size ladder is from general knowledge; the conductor shoe (390 m) is soil-driven, not pressure-driven

## Ch 2: Top hole: drilling with no safety net  (5:30–8:45)

### 2.01 · 5:30 · 31.5s · anim **[GEN]**

**VO:** Now we drill. The first section is the strangest. The drill string, the pipe that turns the bit, hangs in open sea, with no riser and no blowout preventer, a stack of valves that can close the well. This is riserless drilling. Seawater is pumped down the pipe and comes straight out at the seabed, carrying the cuttings, the chips of rock. Nothing returns to the rig.

**SHOT:** Seabed cutaway, camera at the seabed. A drill string hangs from the surface through open water into the first hole. Seawater arrows go down the pipe, out of the bit and a grey cuttings plume billows out onto the seabed around the hole. A greyed-out "BOP" and "riser" ghost outline at the surface with a cross through them.

**Terms introduced:** drill string; riserless drilling; blowout preventer; cuttings

### 2.02 · 6:02 · 42.5s · anim **[GEN]** **[VERIFY]**

**VO:** Pause and think. We are about to drill a kilometre with nothing that can close the well. Why is that allowed? Near the seabed, most of the weight above the rock is just water, so the rock is weak. If gas flowed in and we tried to shut the well, the pressure would crack the rock and break out beside the well. So there is nothing to shut. The defences are the survey that looked for gas first, and a stock of heavy mud ready to pump.

**SHOT:** Side-by-side cartoon: left, closed-in well with a pressure gauge climbing until a crack runs to the seabed ("broaches"); right, open top hole with a tank of heavy "kill mud" labelled "ready to pump". The weak shallow fracture gradient from the window chart is shown as a small inset.

- **VERIFY:** how NORSOK D-010 treats the barrier status of the riserless top hole (one fluid barrier? conditions?) is NOT confirmed; the narration describes the physics only and does not cite the standard

### 2.03 · 6:44 · 38.5s · anim **[GEN]** **[SIM]**

**VO:** This is the spud, the first metres of the well. A guide base on the seabed keeps everything aligned. Then comes the conductor, a thirty inch pipe that is the well's foundation. It is either jetted into soft seabed, or drilled in and cemented. Think of it as a pile. Soil friction holds up the wellhead, the hardware at the top of the well, and later a blowout preventer weighing hundreds of tonnes, while the riser tugs sideways at it with every wave.

**SHOT:** A square guide base lands on the seabed. A 30-inch conductor is lowered; split view shows (a) jetting: water jets at the shoe, the pipe sinks; (b) drill-and-cement. Then a free-body cartoon: vertical soil-friction arrows along the pipe, a lateral spring-bed (soil springs) and a wave-driven sideways force arrow on top.

**Terms introduced:** spud; guide base; conductor; wellhead

- **SIM:** BOP weight given only as "hundreds of tonnes" [memory]; TGB/PGB guide base detail omitted

### 2.04 · 7:22 · 21.5s · anim **[GEN]**

**VO:** Next, a bigger hole, twenty-six inches, down to about a thousand metres. Into it goes the twenty inch surface casing, with the high-pressure wellhead housing at its top. That housing is the first hardware that can contain pressure, and everything else will hang from it.

**SHOT:** The conductor hole is shown; a 26-inch hole extends to 1,000 m on the depth ruler; the 20-inch casing string is lowered with the wellhead housing on top and lands inside the conductor housing.

**Terms introduced:** surface casing

### 2.05 · 7:44 · 29.5s · anim **[GEN]** **[VERIFY]**

**VO:** Then we cement it: pumped down the inside of the pipe and up the outside, until grey cement appears at the seabed, spotted by the camera on a remotely operated vehicle, an ROV. Cement fills the gap between the pipe and the rock, the annulus. It supports the wellhead, and seals off shallow zones. We will see how cement behaves in chapter six.

**SHOT:** U-tube cutaway of the 20-inch string: grey cement travels down inside the pipe, around the shoe, up the annulus; at the seabed a puff of grey cement exits and an ROV camera view highlights it with a "returns" label.

**Terms introduced:** annulus; cement; ROV

- **VERIFY:** the practice of cementing to the seabed with ROV-confirmed returns on current NCS wells is from general knowledge, not confirmed

### 2.06 · 8:14 · 31.5s · anim **[GEN]** **[SIM]**

**VO:** A wellhead is nested seats, like stacked bowls. The twenty inch housing lands inside the conductor housing. Each later string will hang inside it on a casing hanger, with a seal that closes the gap behind it. One more thing for a subsea engineer: this whole stack is a long slender structure rocked by waves, so fatigue of the wellhead and conductor is a real design driver.

**SHOT:** Exploded cutaway of the wellhead: two nested housings with hanger shoulders; a casing hanger with seal drops into place and the gap behind it is sealed. Then a slow sinusoidal sway of the whole stack with a stress-range counter incrementing.

**Terms introduced:** casing hanger

- **SIM:** cuttable sidebar (fatigue) if the cut is over budget

## Ch 3: BOP, riser, and the closed loop  (8:45–10:45)

### 3.01 · 8:45 · 23.5s · anim **[GEN]**

**VO:** Now we close the loop. The blowout preventer is lowered on a marine riser, a large steel pipe running up to the rig, and latches onto the wellhead. For the first time the well is a closed system: mud pumped down the pipe returns up the riser, not into the sea.

**SHOT:** The BOP stack descends on a riser from the surface to the wellhead and latches (a clamp animation). Mud arrows now go down the drill pipe and up inside the riser to the surface. The ghosted riserless BOP/riser outline from Ch 2 becomes solid.

**Terms introduced:** marine riser

### 3.02 · 9:08 · 28s · anim **[GEN]** **[NO]** **[VERIFY]**

**VO:** A blowout preventer is a stack of valves, each with a job. The annular preventer squeezes a rubber element around whatever is in the hole. Pipe rams close around the drill pipe. And the last resort: the blind shear rams, which cut the pipe and seal the hole. Gas-charged accumulators store hydraulic energy, so they can close even if power is lost.

**SHOT:** THE BOP CLOSING ANIMATION. Cutaway of the stack with drill pipe through the bore. In sequence: the annular's rubber element squeezes inward onto the pipe; pipe rams slide in from both sides and grip; the blind shear rams slide in, cut the pipe (the cut section falls) and meet in the middle sealing the bore. A gas-charged accumulator bottle with a pre-charge gauge sits beside it.

**Terms introduced:** annular preventer; ram; blind shear ram; accumulator

- **VERIFY:** Norwegian requirements on BOP configuration (shear-ram redundancy, test pressure, test interval) not confirmed against NORSOK D-010 / D-001 / Activities Regulations

### 3.03 · 9:36 · 10.5s · anim **[GEN]** **[NO]** **[SEEN]**

**VO:** None of it counts until it is tested. A barrier you have not tested is a hope, not a barrier.

**SHOT:** The stack is shown with a pressure gauge ramping to a test pressure and a "HOLD" timer; a green tick appears on each ram and the annular as they are function-tested and pressure-tested.

- **SEEN:** Activities Regulations s.85 requires tested well barriers (search summary)

### 3.04 · 9:47 · 22s · anim **[GEN]**

**VO:** Why does the closed loop matter? Three reasons. We can change the weight of the mud to control pressure. We can compare the flow coming in with the flow going out, the single best kick detector there is. And if something goes wrong, we can shut the well.

**SHOT:** Three icon panels animate in turn: (1) a mud-weight dial and a bottom-hole pressure bar; (2) two flow meters labelled "flow in" and "flow out" with a difference needle; (3) the BOP close icon.

### 3.05 · 10:09 · 36s · anim **[GEN]** **[SIM]**

**VO:** Then we drill out the cement at the bottom of the twenty inch, and test the rock below it. Close the well and pump slowly. Pressure rises in a straight line, because the rock is elastic, until the line bends: fluid has started to leak into the formation. That is the leak-off point, the first real measurement of the fracture limit in this well. It looks like a stress-strain curve, and it tells us whether our fracture line was right.

**SHOT:** Casing-shoe cutaway with a small open-hole stub below. Right: a pressure vs pumped-volume plot draws a straight rise, then bends over (the leak-off point marked with a dot). The dot is carried across to the window chart, landing on the fracture curve at 1,000 m.

**Terms introduced:** leak-off point

- **SIM:** leak-off point plotted exactly on the model curve; real tests scatter and are usually stopped before fracture

## Ch 4: Drilling the deep sections  (10:45–13:45)

### 4.01 · 10:45 · 28s · anim **[GEN]**

**VO:** At the bottom of the drill string is the bottom-hole assembly, the BHA: the bit, a steering tool, instruments, and heavy steel drill collars. Here is a surprise for a mechanical engineer. We drill by pulling. The pipe hangs in tension, and the collars push the bit down. Push with the pipe instead, and a slender column would buckle.

**SHOT:** Vertical drill string drawn full height: tension (blue arrows) in the long drill pipe, a neutral point marker, compression (red arrows) in the collars at the bottom with the bit. A ghost second string pushed from the top buckles into a sine shape and is crossed out.

**Terms introduced:** bottom-hole assembly; drill collar

### 4.02 · 11:13 · 33.5s · anim **[GEN]** **[SIM]**

**VO:** Modern PDC bits cut by shearing, like a lathe tool, with diamond cutters. To steer, we need a bend. A mud motor with a bent housing steers when we stop turning the pipe and just slide. A rotary steerable tool steers while the whole string turns. Why steer at all, what we call directional drilling? To hit a target that is not straight below, and to stay clear of other wells.

**SHOT:** Close-up of a PDC bit shearing a rock layer. Then two panels: (a) bent-housing motor: slide mode curves the path, rotate mode averages the bend out to a straight path; (b) rotary steerable: a pad pushes sideways on the wall while the string spins. Overhead map shows a well deviating from the rig position to an offset target around a neighbour well.

**Terms introduced:** PDC bit; mud motor; rotary steerable system; directional drilling

- **SIM:** our example well is nearly vertical; steering is shown as concept only

### 4.03 · 11:46 · 32.5s · anim **[GEN]** **[SIM]**

**VO:** A curved hole has a cost. Drag in a bend acts like a rope around a capstan: it grows exponentially with the wrapped angle. The sharpness of the bend, the dogleg severity, also bends the pipe every time it turns, so we limit it. To know where we are, measurement-while-drilling sensors in the string measure inclination and direction, but every survey has an error ellipse that grows with depth.

**SHOT:** A rope round a capstan with the equation T2 = T1 e^(mu theta) drawn after the picture; then a deviated well in 3D-ish side view with drag arrows. A dogleg zoom with a bend radius. A plan-view uncertainty ellipse that grows along the well path.

**Terms introduced:** dogleg severity; measurement while drilling

- **SIM:** friction factor and dogleg numbers are illustrative

### 4.04 · 12:19 · 22s · anim **[GEN]** **[NO]** **[VERIFY]**

**VO:** Meanwhile the mud is the hardest-working part of the system. It holds back the formation. It carries cuttings up. It cools the bit, and carries signals to the surface. It may be water-based or oil-based, and it gets its weight from barite, a dense mineral powder.

**SHOT:** Cutaway annulus with four labelled panels in turn: pressure arrows on the wall; cuttings rising in the stream; cool/lubricate at the bit; pulses travelling up the pipe. A barite particle cloud in a beaker raises the level on a density gauge.

**Terms introduced:** barite; water-based mud; oil-based mud

- **VERIFY:** environmental discharge rules for oil-based cuttings on the NCS are regulation-specific and were not checked; none are cited

### 4.05 · 12:41 · 32s · anim **[GEN]** **[SIM]**

**VO:** Now the twist. With the pumps on, the mud has to push its way up the narrow gap around the pipe. Friction adds pressure at the bottom. So bottom-hole pressure is higher while we pump than when we stop. That is the equivalent circulating density, ECD. And it means that every time we stop the pumps to add a pipe, a connection, the pressure at the bottom drops.

**SHOT:** Annulus cutaway with a bottom-hole pressure gauge. Pumps ON: friction arrows along the annulus, gauge reads high; pumps OFF at a connection: friction vanishes, gauge drops, a step trace on a pressure-vs-time chart. Equation after the animation: ECD = MW + friction pressure / (g x depth).

**Terms introduced:** equivalent circulating density; connection

- **SIM:** Newtonian-style friction picture; real annular hydraulics use Herschel-Bulkley rheology

### 4.06 · 13:13 · 32s · anim **[GEN]** **[NO]** **[SIM]** **[VERIFY]**

**VO:** So the real window is squeezed from both sides. With the pumps off, pressure must still beat the pore pressure. With the pumps on, it must stay under the fracture limit. Sometimes no mud weight does both. Managed pressure drilling, MPD, adds a knob: seal the top of the annulus, route the mud through a choke, and add back pressure when the pumps stop, holding bottom-hole pressure steady.

**SHOT:** The window chart returns: two horizontal markers (pumps-off BHP, pumps-on ECD) wiggle between pore and fracture curves and touch the limits. Then the MPD schematic: a sealed annulus, a choke on the return line; as the pump trace drops, the choke closes and the BHP trace stays flat.

**Terms introduced:** managed pressure drilling; choke; back pressure

- **SIM:** MPD variants collapsed into one concept
- **VERIFY:** NORSOK D-010 treatment of managed pressure drilling (dedicated section in Rev 5?) not confirmed

## Ch 5: Casing and tubular design  (13:45–16:30)

### 5.01 · 13:45 · 24.5s · anim **[GEN]** **[VERIFY]**

**VO:** Casing is the well's tunnel lining. It holds the hole open, contains pressure, and isolates formations. Its grade is a number: P one-ten means a minimum yield of one hundred and ten thousand psi, about seven hundred and sixty megapascals. Sour-service grades limit hardness, because hydrogen sulphide cracks hard steel.

**SHOT:** Tunnel-lining cutaway analogy morphs into the casing string in the hole. A pipe tag reads "P110: 110 ksi = 758 MPa". A hardness-vs-cracking sketch for sour service with an H2S molecule label.

**Terms introduced:** casing grade; sour service

- **VERIFY:** grade list and yield conversion are from memory of API 5CT / ISO 11960 (110 ksi = 758 MPa is arithmetic and exact); sour-service rule wording (ISO 15156) not checked

### 5.02 · 14:10 · 30.5s · anim **[GEN]** **[SIM]** **[VERIFY]**

**VO:** Three loads, three mechanisms. Burst is internal pressure, a thin-wall yield problem, and the API rating already includes a twelve and a half percent wall tolerance. Collapse is external pressure, and it is a buckling problem set by the diameter-to-thickness ratio, like crushing a can from outside. Tension is the string's own weight, limited by the pipe body and, usually, by the connection.

**SHOT:** Three cross-section panels in sequence: a ring with outward arrows swelling then yielding (burst, with the Barlow-type formula 0.875 x 2 Y t / D appearing after); a ring with inward arrows buckling into an oval (collapse) with a D/t slider moving the failure pressure; a hanging string with a stretch indicator and a connection highlighted (tension).

**Terms introduced:** diameter-to-thickness ratio

- **SIM:** only the elastic-collapse picture is drawn
- **VERIFY:** the 0.875 factor and the "four collapse regimes" are from memory of API TR 5C3 / ISO 10400

### 5.03 · 14:40 · 22s · anim **[GEN]**

**VO:** The design basis picks the worst credible cases. For burst: a gas kick, with the well shut in, meaning closed at the surface. For collapse: the pipe emptied by lost circulation, with heavy mud outside. For tension: running in the hole, with overpull and shock.

**SHOT:** Three load-case cartoons on the well schematic: shut-in gas column with surface pressure arrow (burst); evacuated casing with heavy mud outside (collapse); string being run with an overpull arrow (tension). A small "design basis" table fills in.

**Terms introduced:** design basis; shut-in

### 5.04 · 15:02 · 22.5s · anim **[GEN]** **[SIM]**

**VO:** But those ratings are uniaxial. Real casing feels axial, radial and hoop stress at once. So we check the von Mises equivalent stress against yield, with a design factor. Plotted as an ellipse of axial force against pressure, it shows something odd: tension reduces collapse resistance.

**SHOT:** A VME ellipse in the axial-force vs differential-pressure plane with burst and collapse intercepts. Adding tension tilts and shifts the ellipse so the collapse intercept moves inward. Load-case dots from beat 5.03 appear inside; a shrunken inner ellipse labelled "design factor" appears. The von Mises expression is shown after the picture.

**Terms introduced:** von Mises equivalent stress; design factor

- **SIM:** ellipse is the simplified VME yield envelope without bending or thermal load; design factors are shown unlabelled as "operator-specific"

### 5.05 · 15:24 · 19.5s · anim **[GEN]**

**VO:** That creates a trap. The top of a string carries the most tension, which cuts its collapse capacity, while the pressures are greatest deep down. So strings are tapered: heavier wall, or stronger steel, only where it is needed.

**SHOT:** A casing string with colour-coded sections: heavy wall at the top (tension) and at the bottom (collapse), lighter in the middle. A depth-vs-utilisation plot shows each load as a curve staying under the section capacity steps.

**Terms introduced:** tapered string

### 5.06 · 15:44 · 28s · anim **[GEN]** **[VERIFY]**

**VO:** And then the connections. Basic threaded couplings seal with thread compound. Premium connections add metal-to-metal seals and a torque shoulder, to stay gas-tight; they are qualified to ISO thirteen six seven nine, and checked as they are screwed together with a torque-turn plot: torque against turns. The pipe may be fine. The connection is where leaks start.

**SHOT:** Thread cross-section: API round thread with a spiral leak path and thread compound; then a premium connection with a metal-to-metal seal ring and torque shoulder. A torque-vs-turns plot with a sharp shoulder-engagement kink and an acceptance window.

**Terms introduced:** premium connection; torque-turn plot

- **VERIFY:** ISO 13679 as the connection-testing standard is from memory; "premium connections leak less" is a generalisation

### 5.07 · 16:12 · 18s · anim **[NO]** **[VERIFY]**

**VO:** In the barrier language of the next chapters, every string is itself a well barrier element, a single object that helps stop flow, with a documented design and a pressure test to prove it.

**SHOT:** The casing strings of the well schematic light up in blue one by one with a small "tested" tick; label "well barrier element".

**Terms introduced:** well barrier element

- **VERIFY:** element acceptance criteria wording in NORSOK D-010 for casing (design + test) not confirmed

## Ch 6: Cementing  (16:30–19:00)

### 6.01 · 16:30 · 18s · anim **[GEN]** **[NO]** **[VERIFY]**

**VO:** Cement does three jobs. It supports the pipe. It seals the gap, so nothing flows along the outside. And it protects the steel from corrosion. The seal is the point: the cement behind the casing is itself a barrier.

**SHOT:** Cutaway of casing, cement sheath and rock with three labelled arrows (support, isolation, protection). The sheath glows as a barrier ring.

- **VERIFY:** NORSOK D-010 requirements for casing cement as a well barrier element (required length/height and verification) not confirmed

### 6.02 · 16:48 · 30s · anim **[GEN]** **[SIM]**

**VO:** To place it, we pump down the inside and up the outside, a U-tube. Pipeline engineers will recognise the trick. Plugs, like pigs, keep cement and mud apart: a bottom plug ahead of the cement, a top plug behind it, with spacer fluid between. A float valve stops the heavy cement flowing back. When the top plug lands and pressure jumps, the displacement is complete.

**SHOT:** U-tube cutaway: fluids in colour: mud (amber), spacer (white), cement (grey). Bottom plug, cement, top plug travel down the string; the bottom plug ruptures at the float collar; cement rises in the annulus. A one-way check valve symbol on the float collar. A pump-pressure trace spikes ("plug bumped") when the top plug lands.

**Terms introduced:** spacer; float valve; wiper plug

- **SIM:** single-stage primary job; multi-stage tools and foam cement omitted

### 6.03 · 17:18 · 25s · anim **[GEN]** **[SIM]**

**VO:** The hard part is displacement. If the pipe sits off-centre, mud on the narrow side barely moves, while cement races up the wide side. That leaves a channel of mud behind the pipe: a path for fluid, hidden. Centralisers hold the pipe in the middle, and moving the pipe helps sweep the mud out.

**SHOT:** THE CEMENT DISPLACEMENT ANIMATION. A vertical slice of an eccentric annulus (wide gap left, narrow gap right) with an inset top-down circle. Cement fronts rise: left front races ahead, right front lags, a mud channel is left trapped on the narrow side (red outline "channel"). Replay with centralisers (bow-springs drawn on the pipe): fronts rise nearly level and a clean grey sheath forms.

**Terms introduced:** centraliser; channelling

- **SIM:** front speeds are invented ratios; a real eccentric displacement needs CFD or a hydraulics simulator

### 6.04 · 17:43 · 29s · anim **[GEN]** **[VERIFY]**

**VO:** Cement is bound by the window too. Its column has to stay under the fracture limit, so the first slurry is lightweight. The recipe is tested in the lab at the well's temperature: how long it stays pumpable, its thickening time, and how fast it gains strength. Above about a hundred and ten degrees, silica is added, so the strength does not fade away.

**SHOT:** Window chart with a cement-column pressure line (hydrostatic plus friction) kept under the fracture curve at the shoe. A lab panel: a thickening-time curve rising sharply (consistometer) and a compressive-strength curve vs time; a temperature axis with a mark at ~110 C and a "silica" tag.

**Terms introduced:** thickening time

- **VERIFY:** silica addition above roughly 110 C is general industry knowledge from memory (strength retrogression), not checked against API/ISO cement standards

### 6.05 · 18:12 · 21.5s · anim **[GEN]** **[SIM]**

**VO:** There is a dangerous hour. As cement turns from liquid to gel to solid, it stops passing pressure down before it becomes impermeable. In that gap, gas can migrate in, and leave a path. This is simplified, but it is why cement jobs are designed around timing.

**SHOT:** Time axis with three coloured phases of the cement column: liquid (full hydrostatic), gel (pressure support fading, pore pressure line crossing it), solid. At the crossing a gas bubble trail enters the cement column through the wall; the finished sheath keeps a thin leak channel.

- **SIM:** gel-strength mechanics reduced to one picture; no numbers given

### 6.06 · 18:34 · 26.5s · anim **[GEN]** **[SIM]**

**VO:** How do we know it worked? Logs. A cement bond log listens to sound travelling along the casing: good cement damps the signal. Ultrasonic tools scan around the pipe. But a quiet log is not proof of a seal. A thin gap, a microannulus, can fool the tool. So we combine logs with returns, volumes, and pressure tests.

**SHOT:** A logging tool in the casing emitting sound: waveform panels for free pipe (ringing) vs bonded pipe (damped). A 360-degree ultrasonic unrolled map with a coloured channel stripe. A micro-gap sketch labelled "microannulus". A checklist of "returns, volumes, bump pressure, pressure test".

**Terms introduced:** cement bond log; ultrasonic cement log; microannulus

- **SIM:** log responses are schematic, not real data

## Ch 7: Well control and barriers  (19:00–22:15)

### 7.01 · 19:00 · 16s · anim **[GEN]**

**VO:** Suppose the window lied. Pore pressure was higher than forecast, or pulling the pipe swabbed the hole like a syringe. Formation fluid enters the well. If we do not stop it, a kick becomes a blowout.

**SHOT:** The window chart with the pore-pressure curve jumping right past the amber mud-weight line: blue influx arrows enter the hole. A syringe cartoon shows pipe withdrawal sucking fluid in (swab). A small "kick -> blowout" arrow.

**Terms introduced:** swabbing

### 7.02 · 19:16 · 23s · anim **[GEN]** **[SIM]**

**VO:** A kick is easy to miss, because gas behaves strangely. At four kilometres it is compressed hundreds of times, and expands as it rises: tiny at the bottom, enormous near the surface. In oil-based mud it is worse: the gas dissolves, and hides until it comes out of solution near the top.

**SHOT:** THE KICK PROPAGATING UP THE ANNULUS. A tall annulus; a small gas bubble at the bottom; as it rises it grows (volume vs pressure), the pit-gain trace next to it stays flat for most of the trip, then spikes in the last stretch. A second variant bubble is shaded "dissolved" (invisible) until a flash-point depth where it suddenly appears.

- **SIM:** expansion factor is ideal-gas Boyle with no compressibility factor, no slip velocity, no mud solubility curve

### 7.03 · 19:39 · 19.5s · anim **[GEN]** **[VERIFY]**

**VO:** So we watch. Flow out greater than flow in. A rising pit level. The well flowing with the pumps off, called a flow check. A sudden faster drilling rate, a drilling break. The aim is to catch a kick while it is still small.

**SHOT:** A dashboard of four gauges: flow in vs flow out difference needle; pit volume trace; a "pumps off - still flowing" flow check indicator; rate-of-penetration spike. Each lights red as the kick occurs.

**Terms introduced:** flow check; drilling break

- **VERIFY:** no numeric detection-volume target is claimed

### 7.04 · 19:58 · 31.5s · anim **[NO]** **[VERIFY]** **[SEEN]**

**VO:** The Norwegian rule is blunt: two independent well barriers, at all times. Each is a well barrier envelope: a set of elements that together stop flow. While drilling, the primary barrier is the mud column, and the secondary barrier is casing, cement, wellhead and preventer. Independence is the whole point: two airlock doors that must never fail together. Barriers must be tested, and if one fails, work stops until it is restored.

**SHOT:** THE BARRIER SCHEMATIC. Flat 2D panel style (outline only): the well schematic with the primary envelope outlined in blue around the mud column, and the secondary envelope outlined in red around casing, cement, wellhead and BOP. An airlock cartoon with two doors and an interlock. A "barrier lost - stop work" banner.

**Terms introduced:** well barrier envelope; primary barrier; secondary barrier

- **VERIFY:** whether NORSOK D-010 permits "common" well barrier elements with a risk assessment, or the regulations require none, appears to conflict between sources; the narration says only "independent". Blue/red colour convention for primary/secondary is from memory
- **SEEN:** Activities Regulations s.85 (tested barriers with sufficient independence; if one fails only restoration work may continue) and Facilities Regulations s.48

### 7.05 · 20:30 · 25s · anim **[GEN]** **[VERIFY]**

**VO:** When a kick is detected: stop drilling, flow check, close the preventer. Now the well is shut in, and the pipe pressure shows something remarkable. The drill pipe is a U-tube. Pressure at the bottom equals the mud in the pipe plus the shut-in drill pipe pressure. So pore pressure is the hydrostatic pressure plus that reading.

**SHOT:** U-tube manometer drawing: the drill pipe on one side, the annulus on the other, both gauges at the surface (SIDPP and SICP), bottom pressure balancing. The BOP closes (reuse of 3.02). An equation line: P_pore = P_hyd(pipe) + SIDPP.

**Terms introduced:** shut-in drill pipe pressure

- **VERIFY:** hard vs soft shut-in practice on the NCS not stated

### 7.06 · 20:55 · 27s · anim **[GEN]** **[SIM]**

**VO:** To kill the well we need kill mud: heavier mud, weighing the old weight plus the shut-in pressure divided by gravity and depth. Pump it down, using the choke to hold bottom-hole pressure just above pore pressure. The driller's method circulates twice. With a subsea preventer, friction in the long choke line adds pressure, so we pump slowly and correct for it.

**SHOT:** Two-column well with colours changing: old mud amber, kill mud darker amber displacing it down the pipe and up the annulus; a choke gauge and bottom-hole pressure stay level. A choke-line friction arrow along the long line from the seabed to the surface. Equation: KMW = MW + SIDPP / (g x TVD).

**Terms introduced:** kill mud; driller's method

- **SIM:** no numbers; wait-and-weight, volumetric method and bullheading mentioned only on screen as text labels

### 7.07 · 21:22 · 21.5s · anim **[GEN]** **[SIM]**

**VO:** The weak point is the shoe. As the gas reaches it, the pressure there peaks. Take too big a kick, and the rock cracks, the test we saw in chapter three. That is what kick tolerance means, and it is why casing seats were chosen from the bottom up.

**SHOT:** Annulus with a gas slug rising; a pressure trace at the casing shoe climbs as the top of the slug reaches the shoe and touches the fracture line from the window chart; label "kick tolerance = biggest kick that keeps this below the fracture line".

**Terms introduced:** kick tolerance

- **SIM:** kick tolerance shown as a concept, no calculation

### 7.08 · 21:44 · 31.5s · anim **[GEN]** **[SEEN]**

**VO:** In twenty ten, on the Macondo well in the Gulf of Mexico, the barriers failed in a chain. Cement and the shoe track did not isolate the reservoir. A negative pressure test, which lowers the pressure in the well to check the barriers hold, was misread. The blowout preventer did not seal. Eleven people died. Barriers do not fail one at a time. They fail when we stop checking.

**SHOT:** A restrained, factual timeline graphic on the barrier schematic: three barrier elements turn grey one by one with labels (cement/shoe track, verification test misread, BOP failure to seal). A simple text card: "Macondo, 2010 - 11 lives lost". No dramatic imagery.

**Terms introduced:** negative pressure test

- **SEEN:** facts match CSB / BP / IADC summaries in web search results (cement and shoe-track barrier failure, negative pressure test misinterpreted, BOP failure, eleven fatalities); primary investigation reports not read in this environment

## Ch 8: Formation evaluation: discovery or dry hole?  (22:15–26:15)

### 8.01 · 22:15 · 18s · anim **[GEN]**

**VO:** Now the question flips. Until now it was how to get there safely; now it is what we found. A well is an expensive way to buy measurements, bought in order from fast, cheap and uncertain, to slow, costly and definitive.

**SHOT:** A ladder diagram descending the screen: mud log, logging while drilling, wireline, pressure and samples, core, well test. Each rung has a time-to-result and a certainty bar; the cost bar grows.

### 8.02 · 22:33 · 23.5s · anim **[GEN]** **[SIM]**

**VO:** First, the mud log. Geologists describe the cuttings coming up with the mud, and look at them under ultraviolet light, where oil glows. A gas chromatograph measures the gases in the mud. But there is a delay: the lag time, annulus volume divided by flow rate, means cuttings are old news when they arrive.

**SHOT:** Cutaway annulus with a bit cutting a layer; a coloured cutting particle rises with the mud over a time counter ("lag"), arriving at a shaker minutes later. A UV-lit tray with a glowing yellow cutting. A chromatograph trace with peaks labelled C1 to C5.

**Terms introduced:** mud log; lag time; gas chromatograph

- **SIM:** lag time shown as a single number; no recycled-gas or bit-metamorphism cautions in the narration

### 8.03 · 22:56 · 28.5s · anim **[GEN]** **[SIM]** **[VERIFY]**

**VO:** Next, logging while drilling, LWD: sensors in the drill string reading the rock as it is cut. Gamma ray separates shale from sand. Resistivity: hydrocarbons conduct poorly, so high resistivity can mean oil or gas. Density and neutron give porosity, the fraction of the rock that is pore space. The data climbs the pipe as pressure pulses in the mud, a few bits per second.

**SHOT:** Scrolling log tracks vs depth over the reservoir interval with synthetic curves (gamma ray, resistivity, density-neutron crossover) drawn on as the bit passes. A tiny modem-style data-rate counter on the mud pulse line reads "a few bits per second".

**Terms introduced:** logging while drilling; gamma ray; resistivity; porosity

- **SIM:** log curves are synthetic and generated from the well model
- **VERIFY:** telemetry rate "a few bits per second" is a rounded memory figure

### 8.04 · 23:25 · 22s · anim **[GEN]** **[SIM]**

**VO:** Why can resistivity find oil? Picture the rock as a sponge soaked in salty water. Current flows through the salt water. Replace some with oil, an insulator, and less current flows. Archie's equation turns that into numbers: water saturation depends on porosity and resistivity. Simplified: it fails in shaly sands.

**SHOT:** Sponge cartoon with a salty-water current path; oil droplets replace water and the current path narrows. Then the equation Sw = (a Rw / (phi^m Rt))^(1/n) with Sw highlighted. A caption: "simplified: shaly sands need other models".

**Terms introduced:** water saturation

- **SIM:** Archie only; no Simandoux or Waxman-Smits

### 8.05 · 23:47 · 41s · anim **[GEN]** **[SIM]** **[VERIFY]**

**VO:** After the bottom section is drilled, more logs run on a cable: wireline. Then comes the best trick. A formation tester presses a probe against the rock and measures pressure at a series of depths. In a fluid column, pressure rises with depth at that fluid's own weight: gas, about a quarter of a bar per ten metres; oil, about three quarters; water, about one bar. Plot pressure against depth and the slopes differ. Where the oil line meets the water line is the free-water level: a contact the well never had to cross.

**SHOT:** THE PRESSURE GRADIENT PLOT. A wireline formation tester probe sets on the wall at stations down the reservoir. Pressure (bar) vs depth (m): dots appear one by one in the gas leg, the oil leg and the water leg; three straight lines fit them (slopes 0.025, 0.076, 0.106 bar/m); the oil and water lines are extended until they cross at 4,052 m, a horizontal "FWL" line is drawn; and the gas/oil crossing marks the gas-oil contact at 3,990 m.

**Terms introduced:** wireline; formation tester; free-water level

- **SIM:** gradients (0.025 / 0.076 / 0.106 bar/m) and contacts are the model's invented values
- **VERIFY:** typical reservoir-condition fluid gradients quoted from memory

### 8.06 · 24:28 · 20.5s · anim **[GEN]** **[SIM]**

**VO:** The tool also pumps out samples, analysed downhole and in the lab. If two sands sit on different pressure lines, they are not connected. And the free-water level is a pressure surface: the oil-water contact on the logs is a little higher, because of capillary forces.

**SHOT:** Sample bottle filling in the tool with an optical-analysis dial; two pressure-vs-depth plots, one single line, one with a visible offset between two sands labelled "different compartments". A thin zoom on the contact: the FWL (pressure) and a slightly higher OWC (logs) with a small transition zone.

- **SIM:** transition zone thickness illustrative (the model puts the OWC 6 m above the FWL)

### 8.07 · 24:48 · 21.5s · anim **[GEN]**

**VO:** A core is the only direct physical sample of the rock: a cylinder cut by a hollow bit. The lab gives porosity, permeability, how easily fluid flows through the rock, and, for a mechanical engineer's pleasure, triaxial strength tests that calibrate our fracture and collapse estimates. It takes weeks.

**SHOT:** A hollow core bit cutting a cylinder, the core barrel being pulled and laid out on a tray; a triaxial test cell with a stress-strain curve and a Mohr-Coulomb envelope; a permeability plug test cartoon.

**Terms introduced:** core; permeability

### 8.08 · 25:10 · 29s · anim **[NO]** **[VERIFY]** **[SEEN]**

**VO:** The last test is a drill stem test, DST: a temporary completion lets the well flow to surface, then we shut it in and watch the pressure build up. That gives permeability, damage near the well, and boundaries. But it is costly, and it means burning hydrocarbons, and on the Norwegian shelf emissions are tightly controlled and taxed. So operators often rely on logs, pressures and samples.

**SHOT:** A test string in the cased hole with a packer, a downhole valve and surface test equipment (separator, burner) drawn simply. A rate-vs-time and a pressure build-up plot with the log-time derivative bump. A small flag icon "NO: flaring and CO2 tax".

**Terms introduced:** drill stem test

- **VERIFY:** how often DSTs are run on the NCS and the exact permit route are not confirmed; the narration avoids a frequency claim
- **SEEN:** flaring prohibited except brief testing and safety (World Bank flaring summary)

### 8.09 · 25:39 · 16s · anim **[GEN]** **[SIM]**

**VO:** Then interpretation. Apply cutoffs on shale content, porosity and water saturation: net sand, net reservoir, net pay. Net pay over gross thickness is the net-to-gross ratio. These cutoffs are illustrative; real ones depend on the field.

**SHOT:** The log tracks return with coloured flags added in three passes (sand in yellow, reservoir in orange, pay in red or green by fluid); a thickness bar chart for gross, net sand, net reservoir and net pay; the net-to-gross ratio computed live.

**Terms introduced:** net pay; net-to-gross ratio; cutoff

- **SIM:** cutoffs are invented (shale volume, porosity, water saturation); real cutoffs are field-specific

### 8.10 · 25:55 · 20s · anim **[NO]** **[VERIFY]** **[SEEN]**

**VO:** So: is it a discovery? Are hydrocarbons present? Movable? How much? The Norwegian Offshore Directorate defines a discovery as a deposit where testing, sampling or logging shows probably movable petroleum. That is technical, not commercial. And a dry hole is still data about the basin.

**SHOT:** A decision tree lights its branches in turn: hydrocarbons present? movable? how much? The Sodir definition appears as a quote card; the final node splits into "DISCOVERY (technical)" and "DRY: still data". A badge "NO: classification by the Norwegian Offshore Directorate".

**Terms introduced:** discovery; dry hole

- **VERIFY:** well-result category names and discovery notification rules not confirmed
- **SEEN:** Sodir definition of a discovery and of a wildcat well (Sodir pages in web search results)

## Ch 9: Plugging and abandonment  (26:15–29:30)

### 9.01 · 26:15 · 26.5s · anim **[GEN]** **[NO]** **[VERIFY]**

**VO:** The well has done its job. We have the data. Now comes the hardest requirement of all. A well is a pipe from a pressurised reservoir to the seabed, and it must stay sealed for geological time. That is plugging and abandonment, P and A. And the plan for it exists before the first metre is drilled.

**SHOT:** The completed well schematic from Chapter 1's build, slowly transforming into a thin tube connecting the reservoir (high-pressure gauge) to the seabed (open end) with the caption "sealed for geological time". A planning-document icon labelled "P&A plan: written before spud".

**Terms introduced:** plugging and abandonment

- **VERIFY:** that NORSOK D-010 has an eternal-perspective design basis for permanent barriers, and that the P&A scheme / relief-well plan must exist before spud, are from memory, not confirmed

### 9.02 · 26:42 · 22.5s · anim **[NO]** **[VERIFY]**

**VO:** First, find every source of inflow. Not only the reservoir. A thin overpressured sand, here at about three thousand metres, can push fluid all the way to the seabed. Each source needs a permanent barrier, and where a hydrocarbon reservoir could flow, the Norwegian standard asks for two.

**SHOT:** The well schematic with the reservoir interval (3,950 to 4,050 m) and the thin overburden "Sand A" (2,980 to 3,000 m) highlighted with flow-potential arrows heading up the wellbore. Two barrier brackets appear at the reservoir; one at Sand A.

**Terms introduced:** permanent well barrier

- **VERIFY:** barrier count per source (two for a hydrocarbon-bearing reservoir, one for other flow potential) from memory of NORSOK D-010, not confirmed; no minimum lengths or test pressures are narrated

### 9.03 · 27:04 · 27.5s · anim **[NO]** **[VERIFY]** **[SEEN]**

**VO:** A permanent barrier must seal across the whole cross-section of the well, including every annulus, and be bonded to solid rock on all sides: rock to rock. Think of sealing a tunnel. A door in the corridor is no use if pipes run along the wall. A plug inside the casing is no use if fluid can run behind it.

**SHOT:** Two cutaway cross-sections side by side: left, a plug inside casing with a leak path arrow running up the cement-casing annulus around it (fails, red); right, a plug spanning casing, annulus cement and rock on all sides (holds, green). A tunnel-with-pipes analogy sketch.

**Terms introduced:** rock to rock

- **VERIFY:** exact wording
- **SEEN:** D-010 Rev 5 permanent barriers extend across the full cross-section, sealing vertically and horizontally with all annuli closed (secondary web summaries)

### 9.04 · 27:32 · 31s · anim **[NO]** **[VERIFY]** **[SEEN]**

**VO:** There are three ways to get there. If the cement behind the casing was logged and is good, and in an exploration well it is only weeks old, it can form part of the barrier. Or we cut the casing away by section milling, and plug the open hole against the rock. Or we perforate the casing, wash the annulus clean, and pump cement: perforate, wash, cement.

**SHOT:** Three panels animate in sequence: (a) a bond log with a green interval and a plug placed across it; (b) a section mill cutting a window out of the casing and leaving open hole against the rock; (c) perforating guns firing, a wash tool jetting behind the casing, cement filling the cleaned annulus.

**Terms introduced:** section milling; perforate wash cement

- **VERIFY:** any acceptance criteria and qualification matrix not read
- **SEEN:** perforate-wash-cement recognised in NORSOK D-010 Rev 5 (vendor blog and SPE review)

### 9.05 · 28:02 · 26s · anim **[GEN]** **[SIM]** **[VERIFY]**

**VO:** To place a plug, first set a mechanical base. Then cement is pumped through open-ended pipe as a balanced plug: balanced, so the levels inside and outside the pipe match. The pipe is pulled slowly out of the cement, and any excess is circulated out. In our drawing, the plug is about a hundred metres long.

**SHOT:** THE PLUG PLACEMENT ANIMATION. Well cutaway: a mechanical bridge plug sets in the 9-5/8 in casing; the drill pipe lowers to just above it; spacer, cement, spacer are pumped; levels inside the pipe and annulus equalise (balanced); the pipe is pulled up through the cement leaving a clean plug; a reverse-circulation arrow clears excess above. The plug length is dimensioned as ~100 m with a "drawing only" caption.

**Terms introduced:** balanced plug

- **SIM:** plug length of about 100 m is a drawing value, not a requirement
- **VERIFY:** minimum plug lengths in NORSOK D-010 Rev 5 (a secondary search summary quotes 100 m open hole / 50 m cased on a mechanical base / 30 m with a qualifying bond log) are NOT narrated

### 9.06 · 28:28 · 23s · anim **[NO]** **[VERIFY]**

**VO:** And then we prove it. Tag it: lower the pipe until it rests on the plug, and load it with weight. Pressure test it, in the direction it has to hold where possible. Log the cement behind the casing. A barrier that has not been verified is not a barrier.

**SHOT:** Drill pipe set down on top of the plug with a weight indicator; a pressure test with a gauge holding flat; a bond-log tool logging the cement behind casing, with a green tick. A stamp reading "VERIFIED" lands on the plug.

**Terms introduced:** tag the plug

- **VERIFY:** tag weight and test pressure requirements deliberately not stated

### 9.07 · 28:52 · 25.5s · anim **[NO]** **[VERIFY]** **[SEEN]**

**VO:** Last, the steel: cut and pull. We cut the casing and conductor below the seabed, and lift out the wellhead. A robot survey checks the seabed is clear, with nothing left for a fishing trawl to catch. And exploration wells are not left in limbo: temporary abandonment has a limited lifetime on the Norwegian shelf.

**SHOT:** A casing cutter inside the strings cuts below the seabed; the wellhead and guide base lift away. ROV view sweeps the seabed: debris check, a clean seabed. A calendar icon with a "limit" tag for temporary abandonment.

**Terms introduced:** cut and pull

- **VERIFY:** cutting depth, seabed clearance requirement and who sets it not confirmed; the narration states no figures
- **SEEN:** Havtil report states exploration wells begun after 1 January 2014 may not be temporarily abandoned longer than two years (search summary)

### 9.08 · 29:17 · 13s · anim **[NO]** **[VERIFY]**

**VO:** Finally, an as-abandoned drawing is filed. It is the last page in the well's life, and it has to be right for the long term.

**SHOT:** The final as-abandoned schematic: plugs in the cased and open-hole sections drawn in solid green, the cut-off casing stubs below the seabed, the seabed clean. The drawing is stamped and filed into an archive icon.

- **VERIFY:** the exact reporting duty to the authorities not confirmed

## Ch 10: Outro: the empty seabed  (29:30–30:00)

### 10.01 · 29:30 · 26s · anim **[GEN]**

**VO:** A well is an argument with the Earth, about pressure, that you have to win every hour. And at the end, you make the win permanent. Three hundred metres down, in the dark, there is nothing here.

**SHOT:** The seabed from Chapter 0 returns: bare, still. The window gauge from the opening dissolves into it. The camera rises slowly through the water column to the surface.

### 10.02 · 29:56 · 4s · still **[GEN]**

**VO:** *(none: visual only)*

**SHOT:** End card on dark background: "THE HOLE THAT FIGHTS BACK", then small print: "Illustrative composite well: invented numbers, real physics. Norway-specific material is flagged [NO]. Verify any requirement against NORSOK D-010 and the current regulations before relying on it."

*Total narration: 3905 words ≈ 130 wpm averaged over the runtime.*
