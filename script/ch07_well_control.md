# Ch 7: Well control and barriers
BUDGET: 195

## 7.01 | 16 | anim
VO: Suppose the window lied. Pore pressure was higher than forecast, or pulling the pipe swabbed the hole like a syringe. Formation fluid enters the well. If we do not stop it, a kick becomes a blowout.
SHOT: The window chart with the pore-pressure curve jumping right past the amber mud-weight line: blue influx arrows enter the hole. A syringe cartoon shows pipe withdrawal sucking fluid in (swab). A small "kick -> blowout" arrow.
FLAGS: GEN
TERMS: swabbing

## 7.02 | 23 | anim
VO: A kick is easy to miss, because gas behaves strangely. At four kilometres it is compressed hundreds of times, and expands as it rises: tiny at the bottom, enormous near the surface. In oil-based mud it is worse: the gas dissolves, and hides until it comes out of solution near the top.
SHOT: THE KICK PROPAGATING UP THE ANNULUS. A tall annulus; a small gas bubble at the bottom; as it rises it grows (volume vs pressure), the pit-gain trace next to it stays flat for most of the trip, then spikes in the last stretch. A second variant bubble is shaded "dissolved" (invisible) until a flash-point depth where it suddenly appears.
FLAGS: GEN; SIM: expansion factor is ideal-gas Boyle with no compressibility factor, no slip velocity, no mud solubility curve
TERMS:

## 7.03 | 19.5 | anim
VO: So we watch. Flow out greater than flow in. A rising pit level. The well flowing with the pumps off, called a flow check. A sudden faster drilling rate, a drilling break. The aim is to catch a kick while it is still small.
SHOT: A dashboard of four gauges: flow in vs flow out difference needle; pit volume trace; a "pumps off - still flowing" flow check indicator; rate-of-penetration spike. Each lights red as the kick occurs.
FLAGS: GEN; VERIFY: no numeric detection-volume target is claimed
TERMS: flow check; drilling break

## 7.04 | 31.5 | anim
VO: The Norwegian rule is blunt: two independent well barriers, at all times. Each is a well barrier envelope: a set of elements that together stop flow. While drilling, the primary barrier is the mud column, and the secondary barrier is casing, cement, wellhead and preventer. Independence is the whole point: two airlock doors that must never fail together. Barriers must be tested, and if one fails, work stops until it is restored.
SHOT: THE BARRIER SCHEMATIC. Flat 2D panel style (outline only): the well schematic with the primary envelope outlined in blue around the mud column, and the secondary envelope outlined in red around casing, cement, wellhead and BOP. An airlock cartoon with two doors and an interlock. A "barrier lost - stop work" banner.
FLAGS: NO; SEEN: Activities Regulations s.85 (tested barriers with sufficient independence; if one fails only restoration work may continue) and Facilities Regulations s.48; VERIFY: whether NORSOK D-010 permits "common" well barrier elements with a risk assessment, or the regulations require none, appears to conflict between sources; the narration says only "independent". Blue/red colour convention for primary/secondary is from memory
TERMS: well barrier envelope; primary barrier; secondary barrier

## 7.05 | 25 | anim
VO: When a kick is detected: stop drilling, flow check, close the preventer. Now the well is shut in, and the pipe pressure shows something remarkable. The drill pipe is a U-tube. Pressure at the bottom equals the mud in the pipe plus the shut-in drill pipe pressure. So pore pressure is the hydrostatic pressure plus that reading.
SHOT: U-tube manometer drawing: the drill pipe on one side, the annulus on the other, both gauges at the surface (SIDPP and SICP), bottom pressure balancing. The BOP closes (reuse of 3.02). An equation line: P_pore = P_hyd(pipe) + SIDPP.
FLAGS: GEN; VERIFY: hard vs soft shut-in practice on the NCS not stated
TERMS: shut-in drill pipe pressure

## 7.06 | 27 | anim
VO: To kill the well we need kill mud: heavier mud, weighing the old weight plus the shut-in pressure divided by gravity and depth. Pump it down, using the choke to hold bottom-hole pressure just above pore pressure. The driller's method circulates twice. With a subsea preventer, friction in the long choke line adds pressure, so we pump slowly and correct for it.
SHOT: Two-column well with colours changing: old mud amber, kill mud darker amber displacing it down the pipe and up the annulus; a choke gauge and bottom-hole pressure stay level. A choke-line friction arrow along the long line from the seabed to the surface. Equation: KMW = MW + SIDPP / (g x TVD).
FLAGS: GEN; SIM: no numbers; wait-and-weight, volumetric method and bullheading mentioned only on screen as text labels
TERMS: kill mud; driller's method

## 7.07 | 21.5 | anim
VO: The weak point is the shoe. As the gas reaches it, the pressure there peaks. Take too big a kick, and the rock cracks, the test we saw in chapter three. That is what kick tolerance means, and it is why casing seats were chosen from the bottom up.
SHOT: Annulus with a gas slug rising; a pressure trace at the casing shoe climbs as the top of the slug reaches the shoe and touches the fracture line from the window chart; label "kick tolerance = biggest kick that keeps this below the fracture line".
FLAGS: GEN; SIM: kick tolerance shown as a concept, no calculation
TERMS: kick tolerance

## 7.08 | 32 | anim
VO: In twenty ten, on the Macondo well in the Gulf of Mexico, the barriers failed in a chain. Cement and the shoe track did not isolate the reservoir. A negative pressure test, which lowers the pressure in the well to check the barriers hold, was misread. The blowout preventer did not seal. Eleven people died. Barriers do not fail one at a time. They fail when we stop checking.
SHOT: A restrained, factual timeline graphic on the barrier schematic: three barrier elements turn grey one by one with labels (cement/shoe track, verification test misread, BOP failure to seal). A simple text card: "Macondo, 2010 - 11 lives lost". No dramatic imagery.
FLAGS: GEN; SEEN: facts match CSB / BP / IADC summaries in web search results (cement and shoe-track barrier failure, negative pressure test misinterpreted, BOP failure, eleven fatalities); primary investigation reports not read in this environment
PAUSE: 2
TERMS: negative pressure test
