# Ch 8: Formation evaluation: discovery or dry hole?
BUDGET: 240

## 8.01 | 23 | anim
VO: Now the question flips. Until now it was how to get there safely; now it is what we found. A well is an expensive way to buy measurements, and they rank from fast, cheap and uncertain, to slow, costly and definitive. The order on this ladder is by price, not by time.
SHOT: A ladder diagram descending the screen: mud log, logging while drilling, wireline, pressures and samples, core, well test. Each rung has a time-to-result and a certainty bar; the cost bar grows. A small note: "ranked by cost and certainty, not by time".
FLAGS: GEN
TERMS:

## 8.02 | 23.5 | anim
VO: First, the mud log. Geologists describe the cuttings coming up with the mud, and look at them under ultraviolet light, where oil glows. A gas chromatograph measures the gases in the mud. But there is a delay: the lag time, annulus volume divided by flow rate, means cuttings are old news when they arrive.
SHOT: Cutaway annulus with a bit cutting a layer; a coloured cutting particle rises with the mud (flow particles) over a time counter ("lag"), arriving at a shaker minutes later. A UV-lit tray with a glowing yellow cutting. A chromatograph trace with peaks labelled C1 to C5.
FLAGS: GEN; SIM: lag time shown as a single number; no recycled-gas or bit-metamorphism cautions in the narration
TERMS: mud log; lag time; gas chromatograph

## 8.03 | 40 | anim
VO: Next, logging while drilling, LWD: sensors a few metres behind the bit, reading the rock minutes after it is cut. Gamma ray usually separates shale from sand. Resistivity: hydrocarbons conduct poorly, so high resistivity can mean oil or gas. Density and neutron give porosity, the fraction of the rock that is pore space; where the two curves cross over, that is the signature of gas. A thin stream of data climbs the pipe as pressure pulses in the mud, a few bits per second; the full log waits in the tool's memory.
SHOT: Scrolling log tracks vs depth over the reservoir interval with synthetic curves (gamma ray, resistivity, density-neutron) drawn on as the sensors pass, a few metres behind the bit. The density-neutron crossover in the gas leg is highlighted ("gas"). A mud-pulse line with a data-rate counter ("a few bits/s") and a memory chip icon ("full log in memory").
FLAGS: GEN; SIM: log curves are synthetic and generated from the well model; VERIFY: telemetry rate "a few bits per second" is a rounded memory figure
TERMS: logging while drilling; gamma ray; resistivity; porosity

## 8.04 | 26 | anim
VO: Why can resistivity find oil? Picture the rock as a sponge soaked in salty water. Current flows through the salt water. Replace some with oil, an insulator, and less current flows. Archie's equation turns that into numbers: water saturation from porosity, measured resistivity and the salt water's own resistivity. Simplified: clays conduct too, so shaly sands need extended versions.
SHOT: Sponge cartoon with a salty-water current path (flow particles); oil droplets replace water and the current path narrows. Then the equation Sw = (a·Rw / (φ^m·Rt))^(1/n) with Sw highlighted and Rw labelled "salt water's resistivity", worked example from the model (Rw 0.05, φ 0.23, Rt 23.6 → Sw ≈ 0.20). A caption: "shaly sands: extended models".
FLAGS: GEN; SIM: Archie only; no Simandoux or Waxman-Smits
TERMS: water saturation

## 8.05 | 49 | anim
VO: After the bottom section is drilled, more logs run on a cable: wireline. Then comes the best trick. A formation tester presses a probe against the rock and measures pressure at a series of depths. In a fluid column, pressure rises with depth at that fluid's own weight: gas, about a quarter of a bar per ten metres; oil, about three quarters; water, about one bar. Plot pressure against depth and the slopes differ. Where the oil line meets the water line is the free-water level, found from pressures alone. Here the well crossed it, but the same trick finds a contact a well never reached, using water pressures from a neighbouring well.
SHOT: THE PRESSURE GRADIENT PLOT. A wireline formation tester probe sets on the wall at stations down the reservoir. Pressure (bar) vs depth (m): dots appear one by one in the gas leg, the oil leg and the water leg (the well crossed into the water leg); three straight lines fit them (slopes 0.025, 0.076, 0.106 bar/m); the oil and water lines meet at 4,052 m ("FWL"), the gas/oil crossing marks the gas-oil contact at 3,990 m. A last ghost example: oil points only, with the water line borrowed from a neighbouring well.
FLAGS: GEN; SIM: gradients (0.025 / 0.076 / 0.106 bar/m) and contacts are the model's invented values; VERIFY: typical reservoir-condition fluid gradients quoted from memory
TERMS: wireline; formation tester; free-water level

## 8.06 | 26 | anim
VO: The tool also pumps out samples, analysed downhole and in the lab. If two sands sit on different pressure lines, they are not in pressure contact; sharing a line suggests a connection but does not prove one. And the free-water level is a pressure surface: the oil-water contact on the logs is a little higher, because of capillary forces.
SHOT: Sample bottle filling in the tool with an optical-analysis dial; two pressure-vs-depth plots, one single line, one with a visible offset between two sands labelled "not in pressure contact". A thin zoom on the contact: the FWL (pressure) and a slightly higher OWC (logs, 6 m above) with a small transition zone.
FLAGS: GEN; SIM: transition zone thickness illustrative (the model puts the OWC 6 m above the FWL)
TERMS:

## 8.07 | 32 | anim
VO: A core is the only large, intact piece of the rock: a cylinder cut by a hollow bit while the reservoir is being drilled, unlike crushed cuttings or thumb-sized sidewall plugs. The lab gives porosity, permeability, how easily fluid flows through the rock, and, for a mechanical engineer's pleasure, triaxial strength tests that calibrate our collapse and rock-strength models; the fracture limit still comes from leak-off tests. Routine results take weeks, special tests months.
SHOT: A hollow core bit cutting a cylinder, the core barrel being pulled and laid out on a tray, next to crushed cuttings and small sidewall plugs for scale ("the only intact sample"). A triaxial test cell with a stress-strain curve and a Mohr-Coulomb envelope; a permeability plug test cartoon.
FLAGS: GEN
TERMS: core; permeability

## 8.08 | 36 | anim
VO: The last rung is a drill stem test, DST. A liner is cemented across the reservoir, then temporary pipe, a seal called a packer and downhole valves let the well flow to surface. We shut it in and watch the pressure build up: that gives productivity, permeability, near-well damage and boundaries. But it is costly, it burns hydrocarbons, and in Norway emissions are tightly controlled and taxed. So operators often rely on logs, pressures and samples, and our example well does exactly that.
SHOT: A test string in a liner cemented across the reservoir (liner hung inside the 9⅝ in casing), with a packer, a downhole valve and surface test equipment (separator, burner) drawn simply. A rate-vs-time and a pressure build-up plot with the log-time derivative bump. A small "NO: flaring and CO2 tax" note. The test string fades: "our well: logs, pressures, samples".
FLAGS: NO; SEEN: flaring prohibited except brief testing and safety (World Bank flaring summary); VERIFY: how often DSTs are run on the NCS and the exact permit route are not confirmed; the narration avoids a frequency claim
TERMS: drill stem test; liner; packer

## 8.09 | 23.5 | anim
VO: Then interpretation. Set cutoffs: rock with too much shale, too little porosity, or too much water does not count. Net reservoir over gross thickness is the net-to-gross ratio, here about nought point nine four. Net pay, eighty-nine metres, is the part that holds hydrocarbons. Our cutoffs are illustrative; real ones depend on the field.
SHOT: The log tracks return with coloured flags added in three passes (net sand, net reservoir, net pay coloured by fluid: gas crimson, oil green); a thickness bar chart for gross 160 m, net reservoir 151 m, net pay 89 m; "N/G = net reservoir / gross = 151 / 160 = 0.94" computed live; net pay shown separately.
FLAGS: GEN; SIM: cutoffs are invented (shale volume, porosity, water saturation); real cutoffs are field-specific
TERMS: cutoff; net-to-gross ratio; net pay

## 8.10 | 30 | anim
VO: So, is ours a discovery? Hydrocarbons present: about forty metres of gas over some fifty-five metres of oil. Movable: the tester pumped them out of the rock. The Norwegian Offshore Directorate calls that a discovery: probably movable petroleum, shown by testing, sampling or logging. That bar is technical: it says nothing yet about whether the find will pay. And a dry hole would still be data about the basin.
SHOT: A decision tree lights its branches in turn: hydrocarbons present? (gas 40 m over oil ~56 m, from the model contacts) movable? (sample bottle) how much? The Sodir definition appears as a quote card ("covers technical and commercial discoveries"); the final node lights "DISCOVERY (technical)", with the "DRY: still data" branch greyed.
FLAGS: NO; SEEN: Sodir definition of a discovery and of a wildcat well (Sodir pages in web search results); VERIFY: well-result category names and discovery notification rules not confirmed
TERMS: discovery; dry hole
