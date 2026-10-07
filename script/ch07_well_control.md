# Ch 7: Well control and barriers
BUDGET: 195

## 7.01 | 18.5 | anim
VO: Suppose the window lied: pore pressure is higher than forecast. Or pulling the pipe swabbed the hole like a syringe, or losses dropped the mud level. Formation fluid enters the well. Unchecked, that kick becomes a blowout: a flow nobody can stop.
SHOT: The window chart around the open hole: the planned mud-weight staircase (1.49 sg to 3,400 m, then 1.62 sg to TD); a red "actual pore pressure" curve (forecast + 0.12 sg below 3,000 m) crosses the 1.62 sg line near 3,700 m; gas influx (crimson flow particles) enters the hole. A syringe cartoon: pipe withdrawal sucks fluid in (swab). A falling mud level from losses. A small "kick → blowout" arrow.
FLAGS: GEN; SIM: the "actual" pore pressure is the forecast + 0.12 sg below 3,000 m, invented for this example
TERMS: swabbing

## 7.02 | 34.5 | anim
VO: A gas kick is deceptive. Here is a puzzle: a bubble of gas at four kilometres, where the pressure is over six hundred bar. How much bigger is it at the surface? [pause 2] Hundreds of times. So the pits first show only a small gain, then as the gas rises it expands, slowly at first, then violently near the top. In oil-based mud it dissolves and hides, then breaks out near the top, sometimes in the riser, above the preventer.
SHOT: THE KICK PROPAGATING UP THE ANNULUS. A tall annulus with a depth axis; a small crimson gas bubble at the bottom with a pressure counter (~640 bar) and a volume counter; during the pause the question "how much bigger at the surface?". As it rises it grows (Boyle), the pit-gain trace next to it shows a small step at influx, stays nearly flat, then spikes in the last few hundred metres ("expansion is back-loaded"). A second variant: the bubble is shaded "dissolved in oil-based mud" until a break-out depth near the top, above the BOP in the riser.
FLAGS: GEN; SIM: expansion factor is ideal-gas Boyle with no temperature or compressibility factor, no slip velocity, no mud solubility curve
TERMS:

## 7.03 | 29.5 | anim
VO: So we watch. Flow out greater than flow in. A rising level in the mud tanks, the pits. On a trip, a hole that takes less mud than the steel we pulled out. A sudden faster drilling rate, a drilling break, is a warning: stop the pumps and watch the well. That is a flow check. The aim is to catch a kick while it is still small.
SHOT: A dashboard of gauges lighting up in turn: flow in vs flow out difference needle; pit volume trace (counter); trip tank: mud taken vs steel volume pulled; rate-of-penetration spike labelled "warning"; then a flow check: pumps off, the well keeps flowing, red. Caption: "catch it while it is still small".
FLAGS: GEN; VERIFY: no numeric detection-volume target is claimed
TERMS: drilling break; flow check

## 7.04 | 47.5 | anim
VO: Remember the two barriers? In Norway the rule is blunt: wherever a formation could flow to the surface, two independent well barriers must stand in the way. Each is a well barrier envelope: a set of elements that together stop flow. While drilling, the primary barrier is the mud column. The secondary barrier is the rock just below the last casing shoe, the casing cement, the casing, the wellhead and the preventer. Independence is the whole point: two airlock doors that must never fail together. Barriers must be tested, and if one fails, the only work allowed is restoring it. A kick is exactly that: the mud barrier has failed.
SHOT: THE BARRIER SCHEMATIC. Flat 2-D panel (outline only): the well schematic with the primary envelope outlined in blue around the mud column, and the secondary envelope outlined in red around the formation at the shoe (the outline closes across the open hole just below the shoe, labelled "formation at shoe, tested by leak-off"), casing cement, casing, wellhead and BOP. An airlock cartoon with two doors and an interlock. A "barrier lost: only restoration work" banner, then the blue envelope breaks where the kick enters.
FLAGS: NO; SEEN: Activities Regulations s.85 (tested barriers with sufficient independence; if one fails only restoration work may continue) and Facilities Regulations s.48; VERIFY: the in-situ formation below the shoe as a secondary well barrier element while drilling is from memory of the NORSOK D-010 drilling schematic; whether D-010 permits "common" well barrier elements with a risk assessment is not confirmed; the narration says only "independent". Blue/red colour convention for primary/secondary is from memory
TERMS: well barrier envelope; primary barrier; secondary barrier

## 7.05 | 38.5 | anim
VO: When a kick is suspected: lift the bit off bottom so no pipe joint sits in the preventer, stop the pumps, check for flow, and close the well. Now it is shut in, and the gauges hide a gift. The annulus holds gas of unknown size, but the drill pipe holds clean mud we know. Drill pipe and annulus form a U-tube: once the gauges settle, pressure at the bottom is that clean mud column plus the shut-in drill pipe pressure. One reading, and we know the pore pressure.
SHOT: Shut-in sequence icons (bit off bottom, pumps off, flow check, BOP closes). Then a U-tube: the drill pipe leg full of clean amber mud, the annulus leg with a crimson gas slug; two surface gauges (SIDPP, SICP) settle. An equation card built from the well model: mud in the pipe 636 bar (1.62 sg, 4,000 m) + SIDPP 18 bar = pore pressure 654 bar.
FLAGS: GEN; SIM: numbers from the illustrative "actual" pore pressure (forecast + 0.12 sg); float valves in the BHA and hard vs soft shut-in practice not covered
TERMS: shut-in drill pipe pressure

## 7.06 | 41.5 | anim
VO: To kill the well we need kill mud: just heavy enough to balance the pore pressure on its own. That is the old weight plus the shut-in drill pipe pressure divided by g times the true vertical depth. The driller's method does it in two circulations: first, the old mud carries the kick out while the choke holds bottom-hole pressure just above pore pressure; then kill mud replaces the old mud. Wait-and-weight does both at once. With a subsea preventer, friction in the long choke line adds pressure, so we pump slowly and correct for it.
SHOT: Equation: KMW = MW + SIDPP / (g · TVD) = 1.62 + 18.3 / (0.0981 × 4,000) ≈ 1.67 sg. Two-column well: circulation 1, the crimson gas leaves up the annulus with the old amber mud through the choke (flow particles) while a BHP gauge stays level; circulation 2, darker kill mud (KILL_MUD) displaces the old mud down the pipe and up the annulus. A choke-line friction arrow along the long line from the seabed to the rig. A small "wait-and-weight: one circulation" note.
FLAGS: GEN; SIM: volumetric method and bullheading not covered; the kill-mud weight ignores a safety margin
TERMS: kill mud; driller's method

## 7.07 | 38.5 | anim
VO: The weak point is the shoe, the top of the open hole. Rising gas expands, so the choke adds pressure to hold the bottom steady, and that pressure peaks at the shoe as the gas arrives. Take too big a kick, or one too far above our mud weight, and the shoe pressure passes the limit a leak-off test measures, repeated below every shoe: the rock cracks and fluid escapes underground. The biggest kick that survives is the kick tolerance, one of the margins built into chapter one's staircase.
SHOT: Annulus with a gas slug rising during circulation; a pressure trace at the 9⅝ in shoe (3,400 m) climbs as the top of the slug approaches and peaks as it arrives, against the shoe limit line (fracture 1.71 sg, measured by the leak-off test). A bigger slug pushes the peak over the line: a crack and losses underground. Label "kick tolerance = biggest kick that keeps this peak below the line".
FLAGS: GEN; SIM: kick tolerance shown as a concept, no calculation
TERMS: kick tolerance

## 7.08 | 45.5 | anim
VO: In twenty ten, on the Macondo well in the Gulf of Mexico, barriers failed one after another. The cement at the bottom of the well did not seal the reservoir. A negative pressure test, on the Norwegian shelf called an inflow test, drops the pressure inside the well below the rock's to prove the seal holds. Its warnings were explained away, and the heavy mud was replaced with seawater. The kick went unnoticed for about forty minutes. The preventer did not seal. Eleven people died. No single failure did that: every barrier had a flaw, and every warning was explained away.
SHOT: A restrained, factual timeline on the barrier schematic: elements turn grey one by one with labels (bottom cement / shoe track, inflow test misread, mud displaced to seawater, kick missed ~40 min, BOP failed to seal). A simple text card: "Macondo, 2010 · 11 lives lost". No dramatic imagery.
FLAGS: GEN; SEEN: facts match CSB / BP / IADC summaries in web search results (bottom cement and shoe-track barrier failure, negative pressure test misinterpreted, displacement to seawater, kick indications missed for roughly 40 minutes, BOP failure, eleven fatalities); primary investigation reports not read in this environment
PAUSE: 2
TERMS: negative pressure test
