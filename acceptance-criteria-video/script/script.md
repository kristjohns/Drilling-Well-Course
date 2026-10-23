# Acceptance criteria for structural analysis — NORSOK U-001:2026, Annex B
#
# Format
#   # <chapter no> | <title> | <id>
#   ## <beat id> | <short name>
#   SHOT: what the picture does (for the animator)
#   VO: narration. {cue} marks the word an animation is keyed to. [pause 0.8] adds silence after a sentence.
#   HOLD: extra seconds at the end of the beat
#
# Numbers quoted in the VO come from src/data/model.json (model/acceptance_model.py). The worked example is
# ILLUSTRATIVE (teaching inputs, not project data). The stress field along the SCL is a teaching stand-in built from
# beam and Lame stresses plus a fillet peak; the elastic-plastic curves come from a section (fibre) model of the neck.

# 0 | Cold open | coldopen

## 0.1 | drive-off
SHOT: 3D. Blue water, marine snow. The riser rises into the gloom above a BOP stack on the wellhead in a template slot. The rig drifts off: the riser leans, the stack tilts and the wellhead bends. The camera closes in on the wellhead connector and the neck of the high-pressure housing below it.
VO: {rig}Three hundred and fifty metres down, a drilling rig has lost its position. {pull}The riser drags the blowout preventer sideways, and the wellhead below it takes {moment}more than twelve meganewton metres of bending, on top of the well pressure. [pause 0.4] {fe}The engineer opens the finite element model of the wellhead housing, and there it is. {red}A red spot. Seven hundred and ninety-three megapascals. {above}Fifty percent above the yield strength.

## 0.2 | the questions
SHOT: 3D cutaway of the housing as an FE model: mesh lines, banded von Mises contour, the red spot at the neck fillet below the connector hub with a probe label "793 MPa". Three question cards appear on the left.
VO: So, has it failed? [pause 0.3] {q1}Is the acceptance criterion the yield strength of the material? {q2}Or is it a strain limit, from an elastic plastic analysis? {q3}And what exactly should we take out of the F E model, and compare with what?

## 0.3 | title
SHOT: Title card over the darkened FE frame: "Acceptance criteria for structural analysis" / "What NORSOK U-001:2026 Annex B actually asks for". A row of four topic pills.
VO: In this video we answer those questions the way {std}NORSOK U zero zero one, the twenty twenty-six edition, does it in its Annex B. We will {curve}read the stress strain diagram, {extract}extract stresses from an F E model, {ep}run the elastic plastic check, and at the end, {verdict}give the red spot its verdict.

# 1 | Load against capacity | answer

## 1.1 | scope
SHOT: 3D cutaway of the wellhead system in the template slot. Components in the scope of Annex B light up cyan with labels (wellhead housing, extension, conductor housing, connector); the conductor pipe lights amber ("pipe formulas, B.9"); the template yellow ("NORSOK N-001").
VO: First, which rules apply to what. {annexB}Annex B is normative. It covers the pressure containing and primary structural components in the riser load path: {wh}the wellhead housing and its extension, {ch}the conductor housing and its extension, {conn}the connectors, the tree, and the workover riser equipment. [pause 0.3] {pipe}Straight pipe, like the conductor itself, has its own capacity formulas in clause B nine. {tmpl}And the template is designed to NORSOK N zero zero one, outside Annex B.

## 1.2 | failure modes
SHOT: Table B.2 rebuilt as three columns: structural (brittle fracture, yielding, local failure, buckling, mechanical disengagement), functional (hub face separation, seal/gasket leak tightness, galling, loss of functionality), environmental (corrosion, environmental assisted cracking). Brittle fracture and EAC get a tag "prevented by material requirements (B.10)". Bottom: static capacity = minimum over the modes (B.3.1).
VO: Annex B asks us to design against {modes}failure modes, not against a stress. {struct}The structural ones are brittle fracture, yielding, local failure, buckling and mechanical disengagement. {func}The functional ones include hub face separation, leak tightness, galling and loss of function. [pause 0.3] {mat}Brittle fracture and environmental cracking are prevented by the material requirements, not by analysis. {min}And the static capacity of a component is the lowest capacity over all the remaining modes.

## 1.3 | design format
SHOT: Formula (B.2) builds: Load or load effect ≤ Fd × Static capacity. Then Table B.3 as a card: single load (internal pressure 0.60, external pressure 0.60, FAT 0.90, make and break 0.90), combined load (normal 0.67, extreme 0.80, accidental 1.00 above / 0.90 below barrier elements), functional 1.00. Finally both sides of (B.2) are highlighted: LOAD and LOAD.
VO: Then comes the design format, formula B two. {b2}The load, or load effect, shall not exceed the static design factor, F d, times the static capacity. [pause 0.3] {table}F d comes from Table B three. {normal}Zero point six seven for normal conditions, {extreme}zero point eight for extreme, {acc}and zero point nine or one point zero for accidental conditions. {press}Pressure design on its own uses zero point six, {func}and functional failure modes always use one point zero. [pause 0.3] {only}Now look at both sides of that inequality. {both}Both are loads. {notstress}The acceptance criterion is not a stress, and not a strain. It is a load, compared with a capacity.

## 1.4 | three ways
SHOT: Three cards (B.3.3): 1 capacity by formulas (pipes B.9, flanges Annex C); 2 elastic FEA (preliminary design only); 3 elastic-plastic FEA (direct method). Under card 1 a note: pipe formulas use σy directly — fully plastic for seamless riser pipe, first yield at the outer fibre for conductors and casing (B.9.5). A strip below: "σy enters all three · strain only in 3".
VO: So the real question is: how do we find the capacity? Clause B three point three gives three ways. {formulas}By formulas, for simple shapes like pipes and flanges. {pipes}For pipe, the yield strength enters directly: the fully plastic section for seamless riser pipe, and first yield at the outer fibre for conductors and casing. {elastic}Second, by elastic finite element analysis, which NORSOK limits to preliminary design. {ep}And third, by elastic plastic finite element analysis, the direct method. [pause 0.3] {where}The yield strength enters all three, but in a different way each time, and strain only appears in the last one. To see why, we need the stress strain diagram.

# 2 | The stress-strain diagram | curve

## 2.1 | tensile test
SHOT: A round tensile specimen in grips (left). As it is pulled, the engineering stress-strain curve draws on a chart (right): linear part with slope E, the knee, hardening to the tensile strength, necking, fracture. The specimen necks and breaks in step with the curve.
VO: Everything starts with a tensile test. {pull}A specimen is pulled, and we plot the force divided by the original area, {strain}against the elongation divided by the original length. [pause 0.3] {elastic}First the line is straight. Stress is proportional to strain, the slope is Young's modulus, and if we unload, the specimen springs back. {yield}Then the line bends: the steel starts to yield. {hard}It hardens, {uts}up to a maximum, the tensile strength. {neck}After that the specimen necks, and finally it breaks.

## 2.2 | the 0.2 % offset
SHOT: Zoom on the knee of the curve (strain 0 to 1 %). An offset line from 0.2 % strain parallel to the elastic line meets the curve: the yield strength. An unloading path from that point returns along a parallel line to 0.2 % permanent strain. Definition cards: 3.1.23 yield strength, 3.1.22 yielding.
VO: Where exactly does yielding start? There is no sharp point, so we agree on one. {offset}Draw a line parallel to the elastic line, starting at zero point two percent strain. {cross}Where it crosses the curve is the yield strength. {unload}Unload from there, and the specimen keeps zero point two percent of permanent strain. [pause 0.3] {def}NORSOK uses exactly this. The yield strength is the stress at a zero point two percent offset, {yielding}and the failure mode called yielding is defined as exceeding that elastic limit of zero point two percent plastic strain.

## 2.3 | design values
SHOT: Formulas (B.5) and (B.6) build: σy = min[Yy·SMYS; 0.90·Yu·SMTS], σu = Yu·SMTS. Notes: de-rating above 40 °C; the 0.9·SMTS cap. Example card: API 75K forging, SMYS 517 MPa, SMTS 655 MPa → σy = min(517; 589.5) = 517 MPa, σu = 655 MPa.
VO: The design does not use the result of one test. {b5}Formula B five takes the specified minimum yield strength, de-rated for temperature, {cap}but never more than ninety percent of the de-rated minimum tensile strength. {b6}Formula B six gives the tensile strength. {derate}De-rating is needed above forty degrees Celsius. [pause 0.3] {ex}Our example is a wellhead housing forged in seventy-five K material: {smys}five hundred and seventeen megapascals minimum yield, {smts}and six hundred and fifty-five tensile. {result}Below forty degrees, sigma y is five hundred and seventeen, and sigma u is six hundred and fifty-five.

## 2.4 | true stress and strain
SHOT: Engineering and true curves on one chart: σt = σ(1 + ε), εt = ln(1 + ε). The true curve keeps rising to the true ultimate, 743 MPa at 13 % true strain. Reference card: ASME VIII-3 KM-620 material model.
VO: One more step. The engineering curve divides by the original area, but the specimen gets thinner. {true}Divide by the actual area and you get the true stress, sigma times one plus epsilon, against the true strain, the natural log of one plus epsilon. {rise}The true curve keeps rising. For our steel it reaches {tu}seven hundred and forty-three megapascals at thirteen percent true strain. {fe}F E programs with large strains need this true curve, and if no test curve is available, {km}NORSOK points to the material model in ASME section eight, division three, K M six twenty.

## 2.5 | three curves for the FE model
SHOT: Figure B.5 rebuilt from the model: linear elastic (grey), true curve cut off at σy (orange) with the allowed stabilising slope (+5 % at 20 % plastic strain, dashed), true curve cut off at the true ultimate (cyan). Each gets a tag with its use: elastic analysis (B.3.5); limit load method; plastic collapse method and local failure.
VO: From the test curve, NORSOK builds three material models for the F E analysis. {lin}A straight line, for the elastic analysis. {cuty}The true curve, cut off at the yield strength with no hardening, for the limit load method. {stab}A tiny slope is allowed to help the solver: no more than five percent at twenty percent plastic strain. {cutu}And the true curve cut off at the true ultimate strength, for the plastic collapse method and for the local failure check. [pause 0.3] {keep}Keep these three curves in mind. Each one belongs to a different acceptance check.

# 3 | The elastic route: extracting stress | elastic

## 3.1 | the FE model
SHOT: 3D: the high-pressure wellhead housing on its own, cut in half, with an FE mesh. Load arrows at the datum (moment, shear, tension) and a pressure symbol in the bore. The banded von Mises contour fades in with a legend 0 to 800 MPa; the neck fillet below the hub is red. Small tag: illustrative stress field.
VO: Here is our wellhead housing, cut in half. {mesh}The F E model divides it into small elements. {loads}At the wellhead datum we apply the accidental loads from Table A four, {press}plus the rated working pressure inside. {contour}A linear elastic analysis gives six stress components at every point. {vm}To plot them, we combine them into one number: the von Mises equivalent stress.

## 3.2 | von Mises
SHOT: Equation board: σe = √(½[(σ1 − σ2)² + (σ2 − σ3)² + (σ3 − σ1)²]). A small cube with three principal stresses: equal stresses (pure pressure) give σe = 0, unequal ones distort the cube. Clause chip B.3.5.1: von Mises or Tresca.
VO: The von Mises stress takes the three principal stresses and measures {dist}how much they distort the material, rather than squeeze it. {equal}When it reaches the yield strength from the tensile test, yielding starts. {crit}NORSOK allows von Mises or Tresca for elastic analysis.

## 3.3 | the peak is not the criterion
SHOT: 3D close-up on the red spot at the fillet with a probe: 793 MPa. A 2D magnifier shows the peak living in a thin skin about 1 cm deep. Cartoon: the skin yields, the load moves to the material beside it. Tag: "peak → fatigue".
VO: Now, the red spot. {peak}Seven hundred and ninety-three megapascals sits in a thin skin at the fillet, about a centimetre deep. {local}If that skin yields, nothing collapses. The load just moves to the material next to it. [pause 0.3] {fatigue}A peak stress like this matters for fatigue, because that is where cracks start. {static}For static strength, comparing the peak with the yield strength is the wrong question.

## 3.4 | the stress classification line
SHOT: 3D: a stress classification line (SCL) across the wall at the fillet root, from the bore to the outside surface, on the tension side. Then a 2D path plot: axial, hoop and radial stress along the SCL (0 at the bore, 112 mm at the outside).
VO: Instead, we cut through the wall with a {scl}stress classification line, from the bore to the outside, at the critical section. {path}Along that line we read the stress components: {axial}the axial stress from bending and tension, {hoop}and the hoop and radial stresses from the pressure.

## 3.5 | linearisation
SHOT: Path plot of the axial stress: the curve, its average (membrane, 517 MPa) as a flat line, the linear part (bending, ±148 MPa) as a sloped line, the remainder (peak) shaded. Formulas: σm = (1/t)∫σ dx, σb = (6/t²)∫σ(t/2 − x) dx. A linearisation output table like an FE post-processor: membrane 482, membrane + bending 613, peak 180, total 793 MPa.
VO: Then we linearise, as described in ASME section eight, division two, annex five A. {mem}The membrane stress is the average over the wall. {bend}The bending stress is the linear part with the same moment. {pk}What is left over is the peak. [pause 0.3] {table}Do that for every component, and combine them with von Mises again. Here the {m482}membrane stress is four hundred and eighty-two megapascals, {mb613}membrane plus bending is six hundred and thirteen, {p180}and the peak adds about one hundred and eighty, to the total of seven hundred and ninety-three.

## 3.6 | stress categories
SHOT: Three category cards: Primary P (equilibrium with the applied load, not self-limiting): Pm, PL, Pb. Secondary Q (constraint: thermal, preload; self-limiting). Peak F (notches; fatigue only). A note: preloaded equipment — if P and Q cannot be separated, all is primary (B.3.5.1).
VO: Each part gets a category. {prim}Primary stress is what the component needs to carry the load. It does not go away when the material yields. {pm}General membrane stress is P m, {pl}local membrane stress near a discontinuity is P l, {pb}and bending is P b. {sec}Secondary stress, Q, comes from constraint, like thermal expansion or preload, and it relaxes once the material yields. {pk}And the peak, F, only counts for fatigue. {preload}For preloaded equipment, if you cannot separate primary from secondary, treat it all as primary.

## 3.7 | Table B.7
SHOT: Table B.7 rows animate in: (σeq)Pm ≤ σy; (σeq)PL ≤ σy; (σeq)Pm/PL+Pb ≤ 1.5 σy; (σeq)P+Q range ≤ 2.0 σy; τ shear ≤ 0.57 σy; bearing ≤ σy. Side animation: a rectangular wall section in bending, first the elastic triangle at first yield, then the fully plastic rectangle: Mp/My = 1.5. Then 0.57 = 1/√3.
VO: Now we compare. Table B seven sets {pm}the membrane stress against the yield strength, {pb}membrane plus bending against one and a half times the yield strength, {pq}the primary plus secondary range against two times, {sh}shear against zero point five seven times, and bearing against the yield strength. [pause 0.3] {why}Why one and a half for bending? {first}When the wall first yields at its surface, the inside is still elastic. {full}It can carry more, until the whole thickness has yielded. For a rectangular wall, that {ratio}fully plastic moment is exactly one and a half times the first yield moment. {shear}And zero point five seven is one over root three, the shear yield stress of von Mises.

## 3.8 | with the design factor
SHOT: The check for the accidental case: PL = 482 MPa against Fd·σy = 0.9 × 517 = 465 MPa → 1.04, FAIL stamp; PL + Pb = 613 against 698 → 0.88. Then the fine print cards: B.3.3 elastic analysis only for preliminary design; B.3.5.1 pressure-containing parts only with D/t > 10; our neck D/t = 6.25 → not permitted.
VO: The design factor scales the allowable stress. For the accidental load, F d is zero point nine. {pl}So the membrane stress of four hundred and eighty-two must stay below zero point nine times five hundred and seventeen, which is four hundred and sixty-five. {fail}It does not. The elastic route fails, by four percent. {plpb}Membrane plus bending would pass. [pause 0.4] {but}But read the fine print. {prelim}NORSOK limits elastic analysis to preliminary design, {dt}and for pressure containing parts, to a diameter to thickness ratio above ten. {neck}Our neck has six point two five. {notallowed}So this result cannot be used for acceptance at all. We need the direct method.

# 4 | The elastic-plastic route | plastic

## 4.1 | the analysis
SHOT: Checklist card (B.3.6.2): von Mises yield function with associated flow rule; large deformations; large strains; strain hardening model (isotropic for static, kinematic for reversed yielding). Load sequence strip (B.3.6.5): preload → pressure → tension → bending increased to instability (Table B.8, load case 1).
VO: An elastic plastic analysis follows the material past yield. {list}The F E model needs the von Mises yield function with associated flow, {large}large deformations and large strains, {iso}and a hardening rule: isotropic for static capacities, {kin}kinematic if the loading reverses beyond yield. [pause 0.3] {seq}The loads are applied in the real sequence: preload, pressure and tension first. {ramp}Then one load, here the bending moment, is increased step by step until the component can take no more.

## 4.2 | the limit load
SHOT: Split screen. Left, 3D: the neck of the housing under increasing bending, with an equivalent plastic strain contour; the zone above 0.2 % grows in from both surfaces until the whole section is plastic. Right: moment against end rotation; load increments as dots, the steps get longer; the step after 99.5 % finds no equilibrium (red cross: not converged). Limit load 20.3 MNm.
VO: First, the limit load method, with the curve cut off at the yield strength. {first}At first the neck is elastic. {yield0}At close to ninety percent of the final load, the outer surface reaches zero point two percent plastic strain. It has yielded. {spread}With every step, the yielded zone grows inwards from both sides, and the rotation grows faster than the load. {hinge}When the whole section has yielded, it acts as a plastic hinge. {nc}The next load step finds no equilibrium, and the solution does not converge. [pause 0.3] {cap}The last converged load is the limit load. For our neck, {mc}twenty point three meganewton metres. {fd1}That is the yielding capacity, at a design factor of one.

## 4.3 | the plastic collapse load
SHOT: The chart zooms out: the curve with hardening (cut-off at the true ultimate) rises above the limit load, peaks at 25.2 MNm (plastic collapse) and falls. Divide by MAX[1.2; σu/σy] = 1.27 → 19.9 MNm, next to the limit load 20.3. Note: ASME VIII-3 margin 1.8 / ISO 13628-7 margin 1.5 = 1.2.
VO: The second option is the factored plastic collapse method. {hard}Now the material hardens, up to the true ultimate strength. {peak}The moment climbs past the limit load and peaks at twenty-five point two meganewton metres. That maximum is the plastic collapse load. {div}It is divided by the larger of one point two, and sigma u over sigma y. {r127}For our steel that is one point two seven, {res}which gives nineteen point nine meganewton metres. [pause 0.3] {why}Why one point two? ASME section eight, division three, uses a margin of one point eight on plastic collapse, and the workover riser standard uses one point five on yielding. {agree}One point eight over one point five is one point two, so the two methods are meant to agree. Here they do, within two percent.

## 4.4 | more than one limit on the curve
SHOT: Figure B.6 rebuilt: one moment-rotation curve with dashed levels, bottom to top: preload exceedance, seal leak tightness, mechanical disengagement, limit load, plastic collapse. The lowest relevant level is highlighted: static capacity = minimum of structural and functional capacities.
VO: For a connector, the same curve carries more than one limit. {levels}Preload exceedance, seal leak tightness, mechanical disengagement, the limit load, and the plastic collapse load. {lowest}The static capacity is the lowest of the structural and functional capacities. {plot}That is why NORSOK recommends that you always plot the load against the rotation or displacement.

## 4.5 | the capacity chart
SHOT: Capacity chart, true wall tension against bending moment: straight lines of formula (B.7) for Fd = 0.67, 0.8 and 0.9; the exact plastic interaction of the section model as a dashed curve outside them. Note: nonlinear capacities — analyse with all loads divided by Fd (Table B.9).
VO: Single load capacities are combined in a capacity chart. {b7}For linear behaviour, formula B seven adds the true wall tension over the tension capacity, and the moment over the bending capacity, and the sum shall not exceed F d. {env}That gives one envelope per load condition: {n}normal, {x}extreme, {a}and accidental. {nonlin}Where pressure or tension changes the bending capacity, NORSOK asks for nonlinear charts, analysed with all the loads divided by F d.

# 5 | Where strain is the criterion | strain

## 5.1 | so, is it a strain limit?
SHOT: Statement card: "Yielding capacity = a LOAD (limit load or factored plastic collapse). No strain limit." Below it two exception cards appear: studs and segments in bending (0.2 % equivalent plastic strain through the section), local failure (triaxiality-dependent strain limit).
VO: So, is the acceptance criterion a strain limit? {no}For the yielding capacity, no. It is a load, and you do not read off a strain to find it. {two}Strain becomes the criterion in exactly two places.

## 5.2 | studs in bending
SHOT: Drawing in the style of Figure B.7: a flange pair with studs under a bending moment. Close-up of the most loaded stud: the equivalent plastic strain contour grows from the tension side across the root section; when the whole root section exceeds 0.2 %, the yielding capacity is reached.
VO: The first is {studs}studs in a flange, segments in a clamp, and locking segments in a connector, when they are bent. {why}For these parts, NORSOK does not wait for the structure to become unstable. {through}The yielding capacity is the load at which the whole root cross section has reached zero point two percent equivalent plastic strain. {stretch}A stud that has yielded right through is permanently stretched, and its preload is gone.

## 5.3 | local failure
SHOT: Microscopic cartoon at a notch: voids nucleate, grow and join into a ductile crack (definition 3.2.27). Triaxiality T = σm/σe: 1/3 in a tensile test, above 1 at a constrained notch. Formula: εL = εLu · exp[−αsl/(1 + m2) · (T − 1/3)]. Chart of εL/εLu against T: at T = 1.2 only 18 %. Damage: Σ Δεpeq/εL ≤ 1.0 over preload, pressure test and yielding capacity; ASME load factor set to 1.0.
VO: The second is local failure. {def}NORSOK defines it as a ductile crack that starts at a point of high triaxial stress, as tiny voids form, grow, and join. {tri}Triaxiality is the mean stress divided by the von Mises stress. In a tensile test it is one third. {notch}At a notch, where the material is held back in every direction, it can be well above one. {limit}ASME section eight, division three, clause K D two three two, gives the strain limit as an exponential function of triaxiality. {drop}At a triaxiality of one point two, a steel has only about eighteen percent of the ductility it shows in a tensile test. [pause 0.3] {damage}The plastic strain is summed over the load history, preload, pressure test, and the yielding capacity, and the damage shall not exceed one. {factor}NORSOK sets the ASME load factor for this check to one point zero, and runs the history all the way up to the yielding capacity.

## 5.4 | the ductility exemption
SHOT: Card of B.3.6.3.3: carbon and low-alloy steels; elongation ≥ 17 % (SMYS ≤ 655 MPa) or 16 % (655 < SMYS ≤ 830 MPa); reduction of area ≥ 35 % or 45 % → no local failure check. Studs and nuts to D.7.2: exempt. Tick: API 75K, 17 % / 35 %. Elastic-route equivalent (B.3.5.3): σ1 + σ2 + σ3 ≤ 2.5 SMYS.
VO: In practice there is a shortcut. {duct}Carbon and low alloy steels that meet the ductility requirements need no local failure check: {el}an elongation of at least seventeen percent and a reduction of area of at least thirty-five percent, for a minimum yield strength up to six hundred and fifty-five megapascals. {bolts}Studs and nuts made to annex D are exempt too. {us}Our seventy-five K forging meets this. [pause 0.3] {el2}In the elastic route, the same idea is a simple sum: the three principal stresses together shall stay below two and a half times the minimum yield strength.

## 5.5 | the other failure modes
SHOT: Four small cards: buckling = maximum load / 1.10 (imperfections, all mode shapes); mechanical disengagement = load at disengagement / 1.1; ratcheting only above 180 °C (KD-234); functional capacities (hub face separation, leak tightness, galling, loss of function) with Fd = 1.0 and manufacturer criteria validated by test.
VO: The remaining modes are load based again. {buck}The buckling capacity is the maximum load divided by one point one zero, {dis}the mechanical disengagement capacity is the load at disengagement divided by one point one, {ratch}and ratcheting only needs checking above one hundred and eighty degrees. {funct}Functional capacities, like seal leak tightness and hub face separation, use an F d of one, with acceptance criteria from the manufacturer, validated by testing.

# 6 | Worked example: the red spot | example

## 6.1 | the case
SHOT: 3D: the BOP on the wellhead in the template slot; the datum plane glows; load arrows at the datum for the accidental case: Mw = 12 217 kNm, Qw = 892 kN, Te = 3 424 kN. The neck section 0.6 m below the datum is marked. Card: the Table A.4 row for 250–500 m (ULS and ALS). Equation: M = Mw + Qw · 0.6 m = 12.75 MNm.
VO: Back to the red spot. {depth}Our well is in three hundred and fifty metres of water, with the blowout preventer on the wellhead. {a4}Table A four gives the design loads at the wellhead datum. {als}The accidental case is twelve thousand two hundred and seventeen kilonewton metres of bending, eight hundred and ninety-two kilonewtons of shear, and three thousand four hundred and twenty-four kilonewtons of tension. {shear}The neck is zero point six metres below the datum, so the shear adds to the moment: {m}twelve point seven five meganewton metres.

## 6.2 | the pressure end load
SHOT: Equation: Tw = Te + π/4 · Ds² · (pi − pe) = 3.42 + π/4 · 0.50² · 69 = 3.42 + 13.55 = 16.97 MN. Notes: Ds = gasket sealing diameter (illustrative); external pressure ignored (conservative).
VO: The well pressure also pulls on the housing. {tw}Formula B seven uses the true wall tension: the applied tension plus the pressure end load on the gasket sealing diameter. {num}With six hundred and ninety bar on a sealing diameter of half a metre, the end load is thirteen point five meganewtons, and the true wall tension becomes {res}seventeen point zero meganewtons.

## 6.3 | the check
SHOT: The capacity chart with the envelopes for Fd = 0.67, 0.8 and 0.9 (Tc = 107.0 MN, Mc = 20.26 MNm). The ALS point (12.75 MNm, 16.97 MN) lands inside the 0.9 envelope, the ULS point (7.68, 12.08) inside the 0.8 envelope. Formula (B.7) with numbers: ALS 0.88 → PASS, ULS 0.61 → PASS. A small reminder: elastic route 1.04 (not permitted).
VO: Now the check. {cap}The limit load analysis gave a bending capacity of twenty point three meganewton metres, and the tension capacity, sigma y times the area, is one hundred and seven meganewtons. {als}For the accidental case: seventeen over one hundred and seven, plus twelve point seven five over twenty point three, divided by zero point nine, {uf}gives zero point eight eight. It passes. {uls}The extreme case, with a design factor of zero point eight, gives zero point six one. [pause 0.3] {compare}The same neck failed the elastic check by four percent, because that check stops at the first yield through the wall, and ignores the reserve of the full section.

## 6.4 | the other checks
SHOT: Checklist: local failure — exempt (75K meets 17 % / 35 %); buckling — not relevant for a wall this thick; functional — connector hub face separation and gasket leak tightness at minimum preload (supplier data); connector capacities from FEA validated by full-scale test (B.2.3). Verdict stamp over the 3D red spot: "acceptable".
VO: To finish the job, we tick off the other failure modes. {local}Local failure: exempt, because the forging meets the ductility requirements. {buck}Buckling: not an issue for a wall this thick. {func}The functional capacities of the connector, like hub face separation and gasket leak tightness at minimum preload, come from the supplier, and connector capacities from F E analysis must be validated by a full scale test. [pause 0.3] {verdict}So, the verdict on the red spot: seven hundred and ninety-three megapascals of peak stress, and the wellhead is still acceptable.

# 7 | Summary | summary

## 7.1 | the answers
SHOT: One page with three answers. 1 Yield strength? The anchor: σy (0.2 % offset, B.5); elastic: linearised stresses against σy multiples (Table B.7); elastic-plastic: shapes the material curve that produces the capacity; pipe formulas use it directly (B.9). 2 Strain limit? Not for yielding (limit load or factored plastic collapse); yes for studs/segments in bending (0.2 % through the section) and local failure (KD-232, unless ductile enough). 3 What to extract? Linearised stresses along SCLs, or a load-rotation curve to instability, plus plastic strain at critical points. Bottom line: Load ≤ Fd × capacity.
VO: Let's put the answers on one page. {q1}Is the criterion the yield strength? The yield strength is the anchor of every check, but it is never compared with a peak stress. {q1b}In the elastic route it limits linearised stresses, and in the elastic plastic route it shapes the material curve that produces the capacity. {q2}Is it a strain limit? Not for yielding. {q2b}Strain is the criterion only for studs and segments in bending, and for local failure, unless the material is ductile enough. {q3}And from the F E model we extract linearised stresses along classification lines, or a load rotation curve to instability. [pause 0.3] {last}Whichever route you take, the final check is always the same. The load shall not exceed F d times the capacity.

## 7.2 | outro
SHOT: 3D: wide, quiet shot of the wellhead and the BOP in the template slot. Sources card: NORSOK U-001:2026 Annex A, Annex B (B.2.5, B.2.7, B.3, B.9), definitions 3.1 and 3.2; ASME BPVC VIII-2 Annex 5-A; ASME BPVC VIII-3 KM-620, KD-232, KD-234. Disclaimer: the worked example uses illustrative inputs.
VO: {src}The rules are in NORSOK U zero zero one, Annex B. The details of the linearisation, the material curve and the strain limit are in the ASME code. {disc}The worked example used illustrative inputs, so take your design values from your own project. Thanks for watching.
HOLD: 3.0
