# Ch 1: Planning: casing from the bottom up
BUDGET: 240

## 1.01 | 23 | anim
VO: Before anyone drills, someone decides what the hole is for. Geologists have picked a target: a sandstone at about three thousand nine hundred and fifty metres. Depth here means true vertical depth, TVD: straight down, not along the hole. Our job is to reach it safely, and find out what is in it.
SHOT: Cross-section of the North Sea: sea surface, seabed at 300 m, layered strata, a highlighted sandstone target at 3,950 m. Vertical dashed line labelled "TVD" and a wavy path labelled "measured depth" beside it. Depth ruler appears at left.
FLAGS: GEN; SIM: all depths are TVD below sea level in a near-vertical well; rig-floor air gap ignored
TERMS: target; true vertical depth

## 1.02 | 29 | anim
VO: Start with something you know. Dive ten metres and you feel one more bar. Hydrostatic pressure is density times gravity times depth. Mud is just a heavier liquid, and we quote its weight as specific gravity, sg: water is one. Rock pores hold fluid too, at a pore pressure. If they connect up to the sea, it is a column of water, and the pressure is normal.
SHOT: A diver icon with a 1 bar per 10 m gauge; then a column of water and a column of amber mud side by side with pressure-vs-depth lines. Then a rock block with magnified pores filled with blue fluid and a pressure gauge, connected by a thin channel to the sea.
FLAGS: GEN
TERMS: hydrostatic pressure; specific gravity (sg); pore pressure

## 1.03 | 26 | anim
VO: But sometimes fluid is trapped. Picture a water-filled cylinder with a spring, closed by a piston with a tiny hole. Load the piston: the water carries it first, then leaks, and the spring takes over. Block the hole, and the water keeps carrying the load: overpressure. What the grains carry is the effective stress: total stress minus pore pressure.
SHOT: Terzaghi piston-and-spring animation: load applied, pressure gauge jumps, water streams through the hole while the spring compresses and the gauge falls. Replay with the hole blocked: gauge stays high, spring barely moves. Equation appears after the animation: sigma-prime equals sigma minus p.
FLAGS: GEN; SIM: single-mechanism picture (disequilibrium compaction); other overpressure mechanisms exist and are not shown
TERMS: overpressure; effective stress

## 1.04 | 25.5 | anim
VO: Now the other wall of the window. A hole in a plate concentrates stress, two to three times over, around its edge. Pressure inside the hole pushes back. Push hard enough and the rock splits: the fracture gradient. Too little, and the wall collapses. A leak-off test, pressurising the hole until the rock takes fluid, measures it directly.
SHOT: Plate-with-hole stress contour cartoon around a borehole circle: hoop stress arrows concentrated at the wall. Then internal pressure slider raising: a split opens at the wall at high pressure; at low pressure the wall chips inward. Small teaser pressure-vs-volume curve labelled "leak-off test".
FLAGS: GEN; SIM: the factor depends on the stress state: about two for equal horizontal stresses, up to three for a uniaxial field (Kirsch)
TERMS: fracture gradient; leak-off test

## 1.05 | 30 | anim
VO: Plot both limits against depth, as an equivalent mud weight, the mud weight that would give that pressure. Pore pressure on the left, fracture on the right. The mud must stay between them, with a margin each side. In an overpressured basin the window narrows with depth, because pore pressure climbs faster than the rock's strength against fracture. Simplified: I draw the lower limit as pore pressure alone.
SHOT: THE CORE CHART. Axes: equivalent mud weight (sg) horizontal, depth vertical (down). Blue pore-pressure curve draws on from the seabed downwards, then the orange fracture curve, the green window fills between them and visibly narrows below 3,000 m. Margins appear as thin dashed offsets. Small caption: "lower limit drawn as pore pressure only".
FLAGS: GEN; SIM: lower limit drawn as pore pressure only; model collapse curve exists in well_model but is shown from Ch 4 on
TERMS: equivalent mud weight

## 1.06 | 19.5 | anim
VO: Near the seabed, hazards must be ruled out first. Shallow gas: pockets only a few hundred metres down that can arrive fast, with little warning. Boulders left by glaciers. Soft, uneven seabed. A seabed survey looks for all of them before the rig arrives.
SHOT: Seabed cutaway: a red gas pocket under a thin cap, boulders in glacial till, a pockmark. A survey ship icon with a dotted sonar fan sweeps over, hazards light up with labels.
FLAGS: GEN; VERIFY: whether a seabed/shallow-gas survey is a Norwegian regulatory requirement (and its wording) not confirmed; SIM: shallow water flow, common in other basins, omitted
TERMS: shallow gas

## 1.07 | 29.5 | anim
VO: Now the clever part: where do we put steel pipe, called casing, to hold the hole open? We design from the bottom up. At total depth we need about one point six two sg. Draw that line up until it meets the fracture curve, less margins; above that the hole would crack. So casing must end below it. The bottom end of a casing string is its shoe.
SHOT: On the window chart, a vertical amber line at 1.62 sg from TD 4,200 m rising until it meets the fracture curve minus margin (dashed) at about 3,370 m; a red band marks "would crack above here". A casing string with a shoe symbol telescopes down from the seabed to the first valid depth.
FLAGS: GEN; SIM: margins are invented: 0.07 sg trip/ECD allowance on pore pressure, 0.03 sg below fracture, plus a 150 m gas-kick term (see well_model.py)
TERMS: casing; casing shoe

## 1.08 | 28.5 | anim
VO: Set that string at about three thousand four hundred metres. The section above used lighter mud, one point four nine sg, so repeat: the next shoe lands at two thousand metres. The mud above that, one point one two sg, is so light that other things decide: shallow hazards, and anchoring the safety valves we add shortly. About a thousand metres. The result is a staircase.
SHOT: Repeat of the stair-step: from 3,400 m the amber line steps left to 1.49 sg and rises to meet fracture at ~2,000 m (string 2 telescopes into place); step again to 1.12 sg: line meets fracture at 660 m, but a label "BOP anchor + shallow hazards: not shallower than 1,000 m" snaps the third shoe to 1,000 m. Three shoes + the conductor, drawn as nested strings.
FLAGS: GEN; SIM: the surface-casing depth floor of 1,000 m is an assumption standing in for hazard and kick-tolerance reasoning
TERMS:

## 1.09 | 29 | anim
VO: The strings nest like a telescope, because each must pass through the one above. So the sizes step down: thirty inch, twenty, thirteen and three eighths, nine and five eighths, then eight and a half inch to the bottom. Every string costs diameter. And this is a wildcat, an exploration well with no neighbours to learn from, so the forecast is uncertain: the plan carries contingency strings.
SHOT: Nested casing strings drawn to scale in a cross-section ring view and in a side telescoping view with size labels. A dashed "7 in liner" and "contingency" string appears in reserve. Caption: "wildcat = no offset wells".
FLAGS: GEN; SIM: standard NCS-style size ladder is from general knowledge; the conductor shoe (390 m) is soil-driven, not pressure-driven
TERMS: wildcat; contingency string
