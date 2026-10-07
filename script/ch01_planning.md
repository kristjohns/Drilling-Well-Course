# Ch 1: Planning: casing from the bottom up
BUDGET: 240

## 1.01 | 29 | anim
VO: Before anyone drills, someone decides what the hole is for. Geologists have picked a target: a sandstone at about three thousand nine hundred and fifty metres. Depth here means true vertical depth below sea level, TVD: straight down, not along the hole. Real well plans usually measure from the rig floor instead. Our job is to reach the target safely, and find out what is in it.
SHOT: Cross-section of the North Sea: sea surface, seabed at 300 m, layered strata, a highlighted sandstone target at 3,950 m. Vertical dashed line labelled "TVD" and a curved well path labelled "measured depth: along the hole" beside it; the two depth read-outs differ at the target. Depth ruler at left marked "m below sea level".
FLAGS: GEN; SIM: all depths are TVD below sea level in a near-vertical well; NCS well plans reference the rig floor (m RKB)
TERMS: target; true vertical depth

## 1.02 | 33 | anim
VO: Start with something you know. Dive ten metres and you feel one more bar. Hydrostatic pressure is density times gravity times depth. Mud is just a heavier liquid, and we quote its weight as specific gravity, sg: fresh water is one. Rock pores hold fluid too, at a pore pressure. If the pores connect all the way up, the pressure is that of a column of salty water, about one point oh three sg: normal pressure.
SHOT: A diver with a 1 bar per 10 m gauge (counter ticking); then a column of sea water and a column of amber mud side by side with pressure-vs-depth lines (sea water labelled 1.03 sg). Then a rock block with magnified pores filled with blue fluid and a gauge, connected through the pores to the sea.
FLAGS: GEN; SIM: normal pore pressure drawn as a 1.03 sg brine column
TERMS: hydrostatic pressure; specific gravity (sg); pore pressure

## 1.03 | 37.5 | anim
VO: But sometimes fluid is trapped. Picture a spring, the rock grains, in a cylinder of water, the pore fluid, under a piston with a tiny hole. Load it: at first the water takes the load, then it leaks away and the spring takes over. Bury sediment fast under tight shale, and the water cannot escape as fast as load is added, so it keeps carrying the load. That is overpressure. The grains carry only the effective stress: the weight of everything above, minus the pore pressure.
SHOT: Terzaghi piston-and-spring, labelled as rock: spring = grains, water = pore fluid. Load applied: gauge jumps, water streams out through the hole, spring compresses, gauge falls. Replay with a much smaller hole ("tight shale"): gauge stays high, spring barely moves, "overpressure". Equation after the animation: σ′ = σ − p, with σ labelled "overburden".
FLAGS: GEN; SIM: single-mechanism picture (disequilibrium compaction); other overpressure mechanisms exist and are not shown
TERMS: overpressure; effective stress

## 1.04 | 37.5 | anim
VO: Now the upper wall of the window. A hole in a plate concentrates stress, two to three times over, at its edge, and rock around a borehole is squeezed the same way. Mud pressure pushes back. Too little, and the concentrated stress crushes the wall: collapse. Too much, and the wall splits; that pressure, as a mud weight, is the fracture gradient. For planning it is predicted. Later, a leak-off test, pumping until the rock takes fluid, checks it at one depth in the real hole.
SHOT: Plate-with-hole cartoon around a borehole circle: hoop-stress arrows concentrated at the wall ("2-3x"). An internal pressure gauge: at low pressure the wall chips inward (collapse); at high pressure a split opens at the wall (fracture). Small pressure-vs-volume curve labelled "leak-off test: one depth, after casing is set".
FLAGS: GEN; SIM: the factor depends on the stress state: about two for equal horizontal stresses, up to three for a uniaxial field (Kirsch); leak-off pressure lies between the minimum horizontal stress and the breakdown pressure
TERMS: fracture gradient; leak-off test

## 1.05 | 36.5 | anim
VO: Plot both limits against depth, as an equivalent mud weight: the mud weight that would give that pressure. Pore pressure on the left, fracture on the right. The mud must stay between them, with a margin each side. In our well the window is tight near the seabed, widest around two and a half kilometres, then pinches in where overpressure builds, because pore pressure climbs faster than the stress needed to open a fracture. Simplified: I draw the lower limit as pore pressure alone.
SHOT: THE CORE CHART. Axes: equivalent mud weight (sg) horizontal, depth vertical (down). Blue pore-pressure curve draws on from the seabed downwards, then the orange fracture curve, the green window fills between them. Three width brackets: 0.17 sg near the seabed, ~0.59 sg around 2,400 m, ~0.19 sg at 3,900 m. Margins as thin dashed offsets. Small caption: "lower limit drawn as pore pressure only".
FLAGS: GEN; SIM: lower limit drawn as pore pressure only; the model's collapse curve lies below pore pressure in this basin and is not drawn
TERMS: equivalent mud weight

## 1.06 | 49.5 | anim
VO: Remember the question: how do you stay inside the window for four kilometres? You don't, not all at once. You stay inside it one section at a time, and lock each finished section behind steel pipe, casing, cemented in place. We design from the bottom up. The deepest section needs about one point six two sg: its highest pore pressure, one point five five, plus a margin. Draw that line up until it meets the fracture curve, less a margin and room for a gas kick. Above that point we could not safely shut in a kick, closing the well against it, so casing must end below it. Its bottom end is the casing shoe.
SHOT: On the window chart, a vertical amber line at 1.62 sg ("deepest section: 1.55 sg pore + margin") rises from TD until it meets the yellow curve "fracture, less margin and kick allowance" at ~3,370 m; a red band marks "shoe too weak for a kick above here". A faint tick shows where plain fracture-minus-margin would cross (~2,420 m) to show that the kick allowance decides. A casing string with a shoe symbol telescopes down from the seabed to the first valid depth.
FLAGS: GEN; SIM: margins are invented: 0.07 sg trip (swab) margin over pore pressure; 0.03 sg below fracture covering ECD and surge; plus a 150 m gas-kick term at the shoe (see well_model.py). Without the kick term the 1.62 sg line would cross fracture-less-margin near 2,420 m
TERMS: casing; casing shoe; shut-in

## 1.07 | 31 | anim
VO: Near the top, pressure is not the only enemy. Shallow gas: pockets a few hundred metres below the seabed, reached before any blowout preventer, the well's big emergency seal-off stack, is in place, so a gas flow there cannot simply be shut in. Boulders left by glaciers. Soft, uneven seabed. A site survey, seabed mapping plus high-resolution seismic of the shallow layers, looks for all of them before the rig arrives.
SHOT: Seabed cutaway: a red gas pocket under a thin cap, boulders in glacial till, a pockmark. A survey vessel tows a seismic streamer: sub-bottom wavefronts penetrate the sediment and light up the gas pocket (bright spot) while a multibeam fan maps the seabed; hazards light up with labels.
FLAGS: GEN; VERIFY: whether a seabed/shallow-gas site survey is a Norwegian regulatory requirement (and its wording) not confirmed; SIM: shallow water flow, common in other basins, omitted
TERMS: shallow gas; blowout preventer

## 1.08 | 36 | anim
VO: Then repeat. The deepest string ends at about three thousand four hundred metres. Above that shoe the mud can be lighter, one point four nine sg, and its line meets the fracture curve near two thousand metres: the next shoe. Above that, the mud, one point one two sg, is so light that pressure no longer decides. Shallow hazards do, and the need for a strong anchor for the seabed hardware and the preventer. About a thousand metres. The result is a staircase.
SHOT: Repeat of the stair-step: from 3,400 m the amber line steps left to 1.49 sg and rises to meet the curve at ~2,000 m (string 2 telescopes into place); step again to 1.12 sg: the line would meet the curve at 660 m, but a label "shallow hazards + wellhead/BOP anchor: not shallower than 1,000 m" snaps the third shoe to 1,000 m. Three shoes + the conductor, drawn as nested strings: the staircase.
FLAGS: GEN; SIM: the surface-casing depth floor of 1,000 m is an assumption standing in for hazard and kick-tolerance reasoning
TERMS:

## 1.09 | 45 | anim
VO: The strings nest like a telescope, because each must pass through the one above. So the sizes step down: thirty inch, twenty, thirteen and three eighths, nine and five eighths, each set in a bigger drilled hole, and finally an eight and a half inch open hole to the bottom. Every string costs diameter. And this is a wildcat, the first well into an untested prospect. Nearby wells help, but may sit in a different pressure compartment, so the forecast is uncertain. The plan keeps a spare, contingency string, in reserve, and that only fits if everything above is sized bigger from the start.
SHOT: Nested casing strings to scale in a cross-section ring view and a side telescoping view, each string with its drilled hole size (36, 26, 17½, 12¼ in) and the 8½ in open hole. A dashed "contingency string (7 in)" appears in reserve. Caption: "wildcat: first well on an untested prospect".
FLAGS: GEN; SIM: standard NCS-style size ladder is from general knowledge; the conductor shoe (390 m) is soil-driven, not pressure-driven
TERMS: wildcat; contingency string
