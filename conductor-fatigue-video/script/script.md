# Fatigue of the conductor and the conductor–template interface — the NORSOK U-001:2026 method
#
# Format
#   # <chapter no> | <title> | <id>
#   ## <beat id> | <short name>
#   SHOT: what the picture does (for the animator)
#   VO: narration. {cue} marks the word an animation is keyed to. [pause 0.8] adds silence after a sentence.
#
# Numbers quoted in the VO come from src/data/model.json (model/fatigue_model.py). The worked example is
# ILLUSTRATIVE (teaching inputs, not project data); the S-N parameters are DNV-RP-C203 (2016) C1/D values for
# seawater with cathodic protection, shown for teaching. NORSOK U-001:2026 refers to DNV-RP-C203:2024.

# 0 | Cold open | coldopen

## 0.1 | storm
SHOT: 3D. Dusk, heavy swell. A semi-submersible drilling rig heaves; the camera starts at the drill floor and drops along the marine riser through the splash zone into blue water: god rays, marine snow.
VO: {rig}Three hundred and fifty metres below this drilling rig, one steel pipe is holding everything up. [pause 0.4] Every wave that lifts the rig {riser}tugs on the riser. The riser {bop}swings the blowout preventer, and the blowout preventer {bend}bends the wellhead. A little to one side. {other}Then a little to the other. [pause 0.3] About {count}seven and a half million times a year.

## 0.2 | hidden crack
SHOT: 3D. The camera reaches the seabed: BOP stack on the wellhead in a template slot. The seabed turns into a cutaway: conductor, surface casing, cement, soil. Two hot spots glow: the girth weld under the conductor housing and the template slot ring. A crack front creeps forward with each cycle.
VO: No single one of those cycles is dangerous. But together they can grow a crack in a weld that nobody will ever inspect: {gw}in the conductor, just below the template, {ts}or in the template slot that holds it. [pause 0.4] So the question every well engineer has to answer is simple. {q}How many days can we keep a riser connected to this well, before that happens?

## 0.3 | promise
SHOT: Title card builds over the frozen 3D frame: "Fatigue of the conductor and the conductor–template interface" / "The NORSOK U-001:2026 method, derived step by step". A tracker of 8 method steps fades in along the bottom.
VO: In this tutorial we will answer that question exactly the way {std}NORSOK U zero zero one, the twenty twenty-six edition, asks us to. We will {derive}derive every equation on the way, from the physics of a growing crack to the design check, and at the end we will run the numbers for a complete example, {example}bin by bin.

# 1 | The system and the rules | system

## 1.1 | anatomy
SHOT: 3D exploded view of the wellhead system rotating slowly; parts fly apart top to bottom with labels: wellhead connector, high-pressure wellhead housing, wellhead extension, 20 in surface casing, conductor housing, conductor extension, 36 in conductor, template well slot, cement, soil. Wellhead datum plane appears at the top of the housing.
VO: Let's start with the hardware. At the top, the {conn}wellhead connector of the blowout preventer latches onto the {wh}high pressure wellhead housing. The top of that housing is the {datum}wellhead datum, the reference point for every load in this method. [pause 0.3] The housing is welded to a {whx}wellhead extension, which continues down as the twenty inch {sc}surface casing. Around it sits the low pressure {ch}conductor housing, welded to a {cx}conductor extension and the thirty-six inch {cond}conductor. [pause 0.3] The conductor housing lands in a {slot}well slot of the template, a steel frame on the seabed. Below the mudline the conductor is {cement}cemented into the soil, and the surface casing is cemented inside the conductor.

## 1.2 | definitions
SHOT: Two definition cards from NORSOK U-001 clause 3: "3.1.7 conductor: tubulars installed and cemented in a well construction, providing support for, and load sharing with the surface casing" and "3.2.9 conductor extension". The 3D model behind highlights the conductor string in amber.
VO: The standard defines the conductor as {def}the tubulars installed and cemented in a well, providing support for, and load sharing with, the surface casing. [pause 0.3] Notice the words {share}load sharing. Most of this tutorial is really about who carries what.

## 1.3 | where the rules are
SHOT: A map of NORSOK U-001:2026 as stacked clause cards that light up one by one: Clause 8.1 riser forces, 13.3.6 structural design, Annex A.3.5 cyclic loads, Annex B.2.6 design format, Annex B.4 M-N curves, Annex J load paths; external links to DNV-RP-C203:2024 (S-N curves) and NORSOK N-001 (template design fatigue factors).
VO: The rules are spread over several parts of the standard. {c81}Clause eight point one says that the marine drilling riser loads in Annex A are the riser forces for the whole wellhead system: wellhead housing, wellhead extension, conductor housing and conductor extension, and that the load share between wellhead system and template shall be determined. [pause 0.3] {c1336}Clause thirteen point three point six covers the structural design of the template, the conductor and the load share. {annA}Annex A gives us the fatigue loads. {annB}Annex B gives the design format and the fatigue capacity. And {annJ}Annex J describes the load paths through the well. [pause 0.3] Two documents outside the standard do the rest: {dnv}D N V R P C two oh three for the S N curves, and {n001}NORSOK N zero zero one for the template's design fatigue factors.

## 1.4 | the recipe
SHOT: The 8-step method as a vertical flow chart that later becomes the HUD tracker: 1 Fatigue loads, 2 Load paths & load share, 3 Local response model, 4 Hot-spot stress, 5 S-N to M-N curve, 6 Damage, 7 Design check, 8 Screening, sensitivity & mitigation.
VO: Here is the whole method as a recipe of eight steps. {s1}One, get the fatigue load at the wellhead datum. {s2}Two, follow the load paths and find the load share. {s3}Three, build a local response model of the well. {s4}Four, convert moments into hot spot stresses. {s5}Five, turn S N curves into M N curves. {s6}Six, sum the damage. {s7}Seven, apply the design factor. {s8}And eight, screen, test the sensitivities, and mitigate. [pause 0.3] Before we can do any of that, we need one idea in our heads. What exactly is fatigue?

# 2 | Fatigue and the S-N curve | sn

## 2.1 | what fatigue is
SHOT: Macro view of a weld toe on the conductor, then microscopic: a crack nucleates at the toe and advances with each load cycle, leaving beach marks. Definition card NORSOK 3.2.19.
VO: The standard defines fatigue as {def}a process of progressive, localized structural change, under fluctuating stresses, that can end in cracks or complete fracture after enough load cycles. [pause 0.3] In a welded steel structure the story almost always starts at a {toe}weld toe. The weld leaves a sharp notch, tiny flaws and residual stress. Each cycle opens a microscopic crack a tiny bit more. {beach}Millions of cycles later, the crack is through the wall.

## 2.2 | anatomy of a cycle
SHOT: A stress-time signal draws on. Annotate stress range delta-sigma (max minus min), amplitude, mean, and R = min/max. Then a fully reversed cycle R = -1 with zero mean.
VO: Let's name the parts of a stress cycle. The {range}stress range, delta sigma, is the maximum minus the minimum. The {amp}amplitude is half of that, and the {mean}mean sits in the middle. The ratio of minimum to maximum is called {R}R. [pause 0.3] NORSOK asks for {rev}fully reversed loading, R equal to minus one, so the cycle swings symmetrically about zero.

## 2.3 | why only the range matters
SHOT: Weld toe residual stress near yield; the local cycle hangs down from yield; two signals with different means but the same range produce the same local cycle at the toe.
VO: Why do we only care about the range, and not the mean? Because a fresh weld carries {resid}residual tensile stress close to yield. Whatever the nominal mean is, the material right at the toe is cycling down from that high tensile level. {same}Two cycles with the same range do the same damage. That is why every S N curve for welded joints is written in terms of the stress range alone.

## 2.4 | Paris law
SHOT: Equation board. Crack of depth a in a plate; da/dN = C ΔK^m appears, then ΔK = Y Δσ √(πa).
VO: Now, where does the S N curve come from? Let's derive it. A fatigue crack grows a small amount every cycle. Experiments show that the {paris}growth per cycle, d a by d N, is proportional to the stress intensity range, delta K, raised to a power m. This is the Paris law. [pause 0.3] {dk}The stress intensity range is the stress range, times the square root of pi times the crack depth, times a geometry factor Y.

## 2.5 | integrate
SHOT: Equation morph: substitute ΔK, separate variables, integrate from a_i to a_f. Brace the integral: "depends only on geometry and flaw sizes". Result: N Δσ^m = constant = ā.
VO: Substitute delta K into the Paris law and {sep}separate the variables: d N equals d a, divided by C, times Y to the m, times delta sigma to the m, times pi a to the power m over two. [pause 0.4] {int}Now integrate from the initial flaw size to the final crack size. {brace}The integral depends only on the geometry and the flaw sizes, not on the load. So it is just a constant. [pause 0.3] {result}And what is left is beautifully simple. The number of cycles, times the stress range to the power m, is a constant. We call that constant {abar}a bar.

## 2.6 | log-log line
SHOT: Take log10 of both sides: log N = log ā − m log Δσ. A log-log chart draws a straight line with slope −1/m in the Δσ–N plane; m = 3 highlighted. Mention welded details m ≈ 3.
VO: Take the logarithm of both sides and you get {log}log N equals log a bar, minus m times log delta sigma. [pause 0.3] On log log paper that is a {line}straight line. The slope m is the inverse slope of the S N curve, and for welded steel it is {m3}about three, the same exponent the Paris law gives for steel. A doubling of the stress range divides the life by two to the power three. {eight}Eight times shorter.

## 2.7 | design curve
SHOT: Scatter of test results around a mean line; a normal distribution of log N drawn sideways; the design curve shifts left by two standard deviations. Callout: NORSOK 3.2.43 note — 2.3 % fractile, 97.7 % survival.
VO: Real test data scatter. {scatter}At a given stress range, log N follows roughly a normal distribution. The design S N curve is placed {shift}two standard deviations below the mean. As NORSOK puts it, {frac}two point three percent of the test values are expected to fall below the curve. A ninety-seven point seven percent probability of survival.

## 2.8 | DNV curves and environment
SHOT: DNV-RP-C203 S-N chart: C1 in air (knee at 1e7), C1 in seawater with cathodic protection (knee at 1e6, slopes 3 then 5), free corrosion (single slope). Parameter table for C1 seawater + CP: m1 = 3, log ā1 = 12.049 (N ≤ 1e6), m2 = 5, log ā2 = 16.081 (N > 1e6). Flag: "DNV-RP-C203 (2016) values for teaching — use DNV-RP-C203:2024 for design".
VO: NORSOK sends us to {dnv}D N V R P C two oh three for the curves themselves. They come in families. {air}In air, the curve bends at ten million cycles, from slope three to a flatter slope five. {cp}In seawater with cathodic protection, the bend comes earlier, at one million cycles. {fc}And under free corrosion there is no bend at all. [pause 0.3] We will use the {c1}C one curve in seawater with cathodic protection. For fewer than a million cycles, m one is three and log a bar is twelve point zero four nine. Above a million cycles, m two is five and log a bar is sixteen point zero eight one. [pause 0.2] {flag}These are the values from the twenty sixteen edition, for teaching. The twenty twenty-four edition that NORSOK refers to revised the seawater curves, so always take design values from the edition in your design basis.

## 2.9 | thickness effect
SHOT: Equation: log N = log ā − m log(Δσ (t/t_ref)^k); t_ref = 25 mm. Two plates of different thickness with through-thickness stress gradients at the toe. Example: t = 50.8 mm, k = 0.15 → factor 1.112.
VO: One more correction. {thick}Thick sections are weaker in fatigue than thin ones, because the stress at the weld toe decays more slowly through the thickness and there is more volume for flaws. The S N curve handles this with a {tf}thickness factor: the stress range is multiplied by t over t ref, to the power k, with t ref equal to twenty-five millimetres. [pause 0.3] For our two inch conductor wall and k equal to zero point one five, {num}the stress is scaled up by about eleven percent.

## 2.10 | class C1 requirement
SHOT: Callout NORSOK 13.3.6.2 and B.10.4: "Girth welds on the conductor (e.g. conductor housing to conductor extension) shall meet S–N class C1 in accordance with DNV-RP-C203:2024." The C1 curve lifts above the D and F curves.
VO: And here is a direct requirement from the standard. {req}Girth welds on the conductor, for example the weld between the conductor housing and the conductor extension, shall meet S N class C one. {above}C one sits above the classes you would give an ordinary as-welded joint, so the weld profile, the fit-up tolerances and the inspection have to be good enough to justify it.

# 3 | From waves to the wellhead moment | loads

## 3.1 | the chain
SHOT: 3D wide shot: rig in waves, riser with buoyancy, lower flex joint, LMRP and BOP on the wellhead. Animated chain of arrows: waves → vessel motion → riser angle and tension → flex joint → BOP stack → bending at the wellhead datum.
VO: Step one of the method is the fatigue load. Follow the chain. {waves}Waves move the rig. {vessel}The rig drags the top of the riser around. {fj}The riser rotates in the lower flex joint just above the stack, and the {stack}tall, heavy B O P stack sways on the wellhead like an inverted pendulum. All of that arrives at the wellhead datum as a {moment}bending moment and a shear force.

## 3.2 | lever arm
SHOT: Free-body diagram: BOP stack from the datum up to the lower flex joint at height H_LFJ. Horizontal force Q at the flex joint, moment M_w at the datum. Equilibrium: M_w = Q H_LFJ → Q_w = M_w / H_LFJ. Table A.3: H_LFJ ≤ 13.7 m; BOP on XT: H_LFJ + H_XT, H_XT ≤ 2.5 m.
VO: Let's derive the relation between the moment and the shear. Treat the {hinge}lower flex joint as a hinge that passes a horizontal force Q but almost no moment. It sits a height H above the wellhead datum. [pause 0.3] Take moments about the datum, and {eq}the moment there is simply Q times H. So the shear at the datum is the moment divided by H. That is exactly the formula in the footnotes to tables A four and A five. [pause 0.3] {h137}For the standard design case, H is up to thirteen point seven metres. {xt}With the B O P on top of a christmas tree, the lever grows by the height of the tree, up to another two and a half metres.

## 3.3 | moment below the datum
SHOT: Cut the well at depth z below the datum: M(z) = Q (H + z) = M_w (1 + z/H). Moment diagram grows linearly downward; at the mudline 4 m below datum: 1.29 M_w.
VO: Now cut the well at a depth z below the datum. The same force Q now has a longer lever, H plus z. {mz}So the moment is M w times one plus z over H. This is why the standard says that the moment below the datum shall be increased due to the shear force. [pause 0.3] {mud}In our example the mudline is four metres below the datum, so the moment there is already twenty-nine percent bigger than at the datum.

## 3.4 | static versus fatigue loads
SHOT: Table A.4 (ULS and ALS wellhead design loads, BOP on WH) shown dimmed with a tag "static design"; then Annex A text: "For the purpose of fatigue design, fatigue loads are specified in terms of a single-load bending moment range and a general bending moment fatigue histogram."
VO: Annex A gives two kinds of riser load. {static}The extreme and accidental moments in tables A four and A five are for static design. For fatigue, {fat}the standard specifies a single load bending moment range, and a general bending moment histogram. Let's look at both.

## 3.5 | table A.7
SHOT: Table A.7 builds: annual single-load bending moment range ΔMo for BOP on WH and BOP on XT by water depth band: 2124/2466, 1436/1766, 1194/1452 kNm. Shallow water highlighted.
VO: {a7}Table A seven gives the annual single load bending moment range, delta M zero, at the wellhead datum. It depends on the water depth, and on whether the B O P sits on the wellhead or on a tree. {shallow}Notice that shallow water is the worst case: a short, stiff riser passes more of the vessel motion down to the well. {xtmode}And the tree mode is always worse than the wellhead mode, because the stack is taller and heavier.

## 3.6 | table A.8
SHOT: Table A.8 as a bar chart on a log axis: normalised ranges 0.1 to 2.9 with cycle counts from 3,948,892 down to 1. Total 7,472,771 cycles per year (one every ~4.2 s).
VO: {a8}Table A eight is the shape of the year. It lists normalised moment ranges from zero point one to two point nine, and how many cycles of each happen in one year. {small}Small cycles are extremely common: almost four million cycles at zero point one. {big}The biggest cycles happen once or twice a year. [pause 0.3] {total}In total that is seven point four seven million cycles per year, roughly one every four seconds.

## 3.7 | scaling
SHOT: Multiply every range by ΔMo: the x-axis rescales from normalised to kNm. Example 1 from A.3.5.1: 0.1 × 2124 = 212.4 kNm at 3,948,892 cycles. Then our case: 350 m, BOP on WH → ΔMo = 1436 kNm, bins from 143.6 to 4164 kNm.
VO: To get the histogram for a real project, you {mult}multiply every range in table A eight by the single load range from table A seven. The standard's own example: for eighty to two hundred and fifty metres of water, {ex1}zero point one times twenty-one twenty-four gives two hundred and twelve kilonewton metres, three point nine million times a year. [pause 0.3] {ours}Our example well is in three hundred and fifty metres of water with the B O P on the wellhead, so delta M zero is fourteen thirty-six kilonewton metres, and the bins run from about one hundred and forty, up to over four thousand kilonewton metres.

## 3.8 | fatigue service life
SHOT: Callouts from A.3.5: "fatigue service life = fatigue life / DF", "equivalent to the permissible operational days with a BOP and marine drilling riser connected", "minimum calculated fatigue service life shall be 1 year" (A.3.5.2 templates, A.3.5.3 wellhead systems). Note: VIV not included.
VO: Two more rules from Annex A. {svc}The fatigue service life is the fatigue life divided by the design factor, and it is equivalent to the permissible number of operational days with a B O P and riser connected. {min}For both the template and the wellhead system, the minimum calculated fatigue service life is one year. [pause 0.3] {viv}And the histogram does not include vortex induced vibration of the riser. If that is relevant, its damage must be added.

# 4 | Load paths and load share | share

## 4.1 | contact areas
SHOT: 3D cutaway of the wellhead in the template slot (after NORSOK Figure J.1). Contact areas appear one by one with letter badges: F connector/WH, A top of WH/conductor housing, B bottom of WH/conductor housing, C template/conductor housing, D bottom of structure/conductor housing, G structure/seabed, E top of cement between conductor and surface casing, H conductor/soil-cement.
VO: Step two. Where does the moment go once it enters the well? Annex J answers with eight contact areas. {F}F, where the connector meets the wellhead. {A}A and {B}B, where the wellhead housing bears against the conductor housing, at the top and at the bottom. {C}C and {D}D, where the conductor housing bears against the template slot. {G}G, where the template sits on the seabed. {E}E, the top of the cement between conductor and surface casing. And {H}H, the conductor against the soil and cement.

## 4.2 | three load paths
SHOT: 3D: three glowing particle streams. Path 1 (blue): WH → surface casing → cement at E → soil. Path 2 (amber): WH → A,B → conductor housing → conductor → soil H. Path 3 (green): WH → conductor housing → C,D → template → seabed G.
VO: Through those contacts the load can travel along three paths. {p1}Path one goes down the wellhead extension and the surface casing, and into the soil below the top of the cement. {p2}Path two jumps across to the conductor housing at A and B, and goes down the conductor into the soil. {p3}Path three goes from the conductor housing into the template at C and D, and through the template into the seabed. [pause 0.3] {quote}The standard says the load sharing depends on tolerances and on the relative stiffness of all the elements, including the soil. So let's understand stiffness.

## 4.3 | springs in parallel
SHOT: Two springs k1, k2 side by side under a rigid bar pushed down by force F; same displacement δ. Derivation: F1 = k1 δ, F2 = k2 δ, F = F1 + F2 → δ = F/(k1 + k2) → F_i = k_i/(k1 + k2) F. Slogan: "stiffness attracts load".
VO: Picture two springs side by side under a rigid bar. Push the bar down with a force F. {same}Both springs must move by the same amount, delta. That is compatibility. {each}Each spring pushes back with its stiffness times delta. That is the material law. {sum}And the two forces must add up to F. That is equilibrium. [pause 0.3] {solve}Solve for delta, put it back, and the share of each spring is its stiffness divided by the total stiffness. {attract}Stiffness attracts load. That one line is the core of every load share analysis.

## 4.4 | vertical load share
SHOT: Table 4 of NORSOK (indicative structure vertical load share factors): single caisson 1-slot 50 %, template 1-slot 40 %, 2-slot 45 %, 4-slot 35 %, 6-slot 30 % corner / 20 % centre. Springs: well vs template foundation. Fully supporting conductor methodology: conductor designed for 100 % of vertical hang-off loads AND template designed for its stiffness share.
VO: Vertically, the well and the template's foundation are two springs in parallel. {t4}Table four gives indicative shares carried by the structure: from fifty percent for a single caisson down to twenty percent for the centre slot of a six slot template. [pause 0.3] {fully}Under the fully supporting conductor methodology, which is the main principle, the conductor is designed to carry all vertical hang-off loads, while the template is still designed for its stiffness based share. {both}Each element is designed for the share that is worst for it.

## 4.5 | bending share between bonded strings
SHOT: Below the top of cement E: conductor and surface casing bonded, same curvature κ. Derivation: M_i = E_i I_i κ → M_i = E_i I_i / Σ EI · M. Numbers: I_conductor = 0.01289 m⁴, I_casing = 0.00112 m⁴ → 92 % / 8 %. Above E (cement shortfall) the strings act separately.
VO: The same idea works for bending. Below the top of the cement, the conductor and the surface casing are glued together, so they must bend to the {kappa}same curvature, kappa. Each string resists with its own bending stiffness, E I, times kappa, and the moments add up. {emi}So each string takes its E I divided by the total E I. [pause 0.3] {num}For a thirty-six by two inch conductor around a twenty by one inch casing, the conductor takes about ninety-two percent. [pause 0.3] {short}But above the top of the cement, in the cement shortfall, the strings are not bonded. The surface casing must carry its share on its own, which is why the standard calls cement shortfall one of the main factors in wellhead fatigue.

## 4.6 | the template as a rotational spring
SHOT: Conductor housing in the slot with rings C and D a distance h apart. Rotate by θ about the stiffness centre; ring forces form a couple. Derivation for equal rings: forces ±kθh/2, couple (kθh/2)·h → k_θ = k h²/2; general k_θ = k_C k_D h² / (k_C + k_D). Numbers: 200 and 400 MN/m, h = 2 m → 533 MNm/rad. Moment share M_T = k_θT / (k_θT + k_θW) · M. Then the gap: nothing until it closes.
VO: Now the conductor template interface. The slot holds the conductor housing at two rings, {rings}C and D, a distance h apart. If the housing tilts by a small angle theta, {defl}one ring is pushed by theta times h over two, the other the opposite way. {couple}The two ring forces form a couple, and the couple divided by theta is a rotational stiffness: k times h squared over two. With different ring stiffnesses, {gen}it becomes the product over the sum, times h squared. [pause 0.3] {kt}For rings of two hundred and four hundred meganewtons per metre, two metres apart, that is about five hundred and thirty meganewton metres per radian. {parallel}The template and the well below it are two rotational springs in parallel, and the moment splits by the same stiffness rule. [pause 0.3] {gap}But real slots have a radial clearance. Until the gap closes, the template carries nothing at all. So the share depends on the size of the cycle, and that makes the problem nonlinear.

## 4.7 | relative vertical displacement
SHOT: Callout NORSOK 13.3.6.2: "A relative vertical displacement of 100 mm between the template and the conductor or wellhead, including thermal upward growth and template settlement, shall be accounted for in the template design unless otherwise specified." Thermal growth derivation: δ = α ΔT L = 1.2e-5 × 60 × 120 m = 86 mm; fully restrained force F = E A α ΔT = 5.7 MN for the 20 in casing. 3D: wellhead slides up in the slot while the rings keep it laterally.
VO: Vertically, the interface has a different job. A producing well heats up and {grow}grows. The free growth of a steel string is the expansion coefficient, times the temperature rise, times the free length. {num}Twelve millionths per degree, times sixty degrees, times one hundred and twenty metres, is about eighty-six millimetres. {restrain}If you stopped that growth completely, the force would be E A alpha delta T, almost six meganewtons in the surface casing alone. [pause 0.3] {req}So the standard requires the template design to accommodate a relative vertical displacement of one hundred millimetres between template and conductor, including thermal growth and settlement. {both}The slot must let the well slide vertically, and still hold it laterally.

# 5 | The conductor in the soil | soil

## 5.1 | Winkler foundation
SHOT: Section view: conductor below the mudline with soil drawn as a bed of springs. Element of length dz: shear V, moment M, soil reaction p = k y. Derivation: dV/dz = −k y, dM/dz = V, M = EI y'' (sign convention on screen) → EI y'''' + k y = 0.
VO: Below the mudline, the conductor is a beam pushed against the soil. The simplest model treats the soil as a {bed}bed of independent springs: the soil pushes back with a force per metre equal to a modulus k times the lateral deflection y. [pause 0.3] Take a short slice of the conductor. {shear}The change in shear force along the slice equals the soil reaction. {mom}The change in moment equals the shear. {ei}And the moment is E I times the curvature. Put the three together and you get {ode}E I times the fourth derivative of y, plus k times y, equals zero.

## 5.2 | solving the equation
SHOT: Try y = e^{λz}: EI λ⁴ + k = 0 → λ⁴ = −4β⁴ with β = (k/4EI)^{1/4} → λ = β(±1 ± i). Keep the decaying pair: y = e^{−βz}(C1 cos βz + C2 sin βz). Annotate 1/β as characteristic length.
VO: Try a solution of the form e to the lambda z. {char}The equation becomes E I lambda to the fourth plus k equals zero. If we define {beta}beta as the fourth root of k over four E I, the four roots are beta times plus or minus one, plus or minus i. [pause 0.3] Far down the conductor the deflection has to die out, so we {decay}keep only the two decaying roots: an exponential decay times a cosine and a sine. {len}One over beta is a length, the distance over which the conductor feels the soil.

## 5.3 | boundary conditions
SHOT: At the mudline: moment M0 = M_w(1 + h/H) and shear P = Q_w. Derivatives y'' and y''' at 0 → C2 = M0/(2EIβ²), C1 = −P/(2EIβ³) − C2. Result: M(x) = M0 e^{−βx}(cos βx + sin βx) + (P/β) e^{−βx} sin βx.
VO: At the mudline, the stick-up hands over a {m0}moment M zero and a shear P. Differentiate the solution twice and three times, set the moment and the shear at the mudline, and the two constants fall out. [pause 0.3] {result}The moment down the conductor is M zero times e to the minus beta x, times cosine plus sine, plus P over beta, times e to the minus beta x, times sine. A decaying, slightly oscillating wave of bending.

## 5.4 | maximum moment
SHOT: dM/dx = 0 → tan βx = P/(2βM0 + P). Chart of M(x)/M_w for k = 1, 5, 20 MPa; example k = 5 MPa: β = 0.147 1/m, 1/β = 6.8 m, max 1.33 M_w at 1.1 m below mudline; decays within ~20 m. Rotational stiffness at the mudline k_θ = EIβ = 393 MNm/rad.
VO: Where is the moment largest? Set the derivative to zero, and {tan}the tangent of beta x equals P, divided by two beta M zero plus P. [pause 0.3] {num}For our conductor in soil with k equal to five megapascals, one over beta is six point eight metres, and the peak is one point three three times the wellhead moment, about one metre below the mudline. {soft}In softer soil the peak moves deeper, and the bending reaches further down. [pause 0.3] {ktheta}The same solution also tells us how stiff the well is in rotation at the mudline: E I times beta, about three hundred and ninety meganewton metres per radian. {compare}Compare that with the template's five hundred and thirty, and in this simple picture the template would take more than half of the moment, if there were no gap.

## 5.5 | reality check
SHOT: Callouts from Annex J: conductor–soil interface depends on installation: driven (best), drilled and driven (very good), drilled and cemented (least predictable, poorest horizontal support). Real p–y curves are nonlinear, stiffen with depth and degrade under cycling. B.4.2.4: analyse a range of parameters.
VO: Real soil is less tidy. {py}Its resistance is nonlinear, grows with depth and softens under cycling. And the interface depends on how the conductor went in. {driven}Driven gives the best contact, {cemented}while a drilled and cemented conductor is the least predictable, with the poorest horizontal support. [pause 0.3] That is why NORSOK does not rely on one hand calculation. It asks for a {fe}local response model, and for the fatigue capacity to be determined over a range of parameters.

# 6 | From moment to hot-spot stress | stress

## 6.1 | bending stress
SHOT: Beam slice: plane sections remain plane → ε = κ y; Hooke σ = E κ y; equilibrium M = ∫σ y dA = E κ ∫y² dA = E I κ → σ = M y / I; outer fibre σ = M / W, W = 2I/D.
VO: Step four turns moments into stresses. Start with beam theory. {plane}Plane sections stay plane, so the strain grows linearly with the distance y from the neutral axis: strain equals curvature times y. {hooke}Steel is elastic, so stress is E times strain. {eq}Add up the moment of all those stresses over the cross section and you get E times kappa times the integral of y squared, which is E I kappa. [pause 0.3] {sigma}Eliminate kappa, and the stress is M y over I. At the outer surface, it is M divided by the section modulus W.

## 6.2 | second moment of a tube
SHOT: Polar integral: J = ∫ r² dA = ∫ r² 2πr dr = π(r_o⁴ − r_i⁴)/2; by symmetry I = J/2 = π(D⁴ − d⁴)/64. Numbers: 36 × 2 in: D = 914.4 mm, d = 812.8 mm → I = 1.289×10¹⁰ mm⁴, W = 2.820×10⁷ mm³. Thin-wall check I ≈ π r³ t.
VO: For a tube, the trick is to integrate in rings. {polar}The polar moment, the integral of r squared over the area, is pi over two times r outer to the fourth minus r inner to the fourth. {sym}By symmetry, the bending moment of inertia is half of that. In diameters: {i}pi over sixty-four, times D to the fourth minus d to the fourth. [pause 0.3] {num}For our conductor, nine hundred and fourteen millimetres outside and eight hundred and thirteen inside, I is one point two nine times ten to the ten millimetres to the fourth, and W is two point eight two times ten to the seven cubic millimetres.

## 6.3 | nominal stress at GW1
SHOT: The local model's moment diagram for a 3000 kNm wellhead range; at GW1 (3.0 m below the datum) the conductor carries 2583 kNm (shear lever minus load share to the template and casing). Δσ_nom = 2583e6 / 2.82e7 = 91.6 MPa.
VO: Here is our first hot spot, {gw1}G W one, the girth weld between the conductor housing and the conductor extension, three metres below the datum. When the wellhead sees a moment range of three thousand kilonewton metres, the shear lever pushes the moment up on the way down, and the load share to the template and the casing pulls it back. {m}The local model says the conductor carries two thousand five hundred and eighty-three kilonewton metres at this weld. {nom}Divide by W, and the nominal stress range is ninety-one point six megapascals.

## 6.4 | stress concentration
SHOT: Two plates offset by e under axial force N; the eccentric load path creates a moment N·e shared equally by both sides: bending stress 6(Ne/2)/t² = 3Ne/t²; SCF = 1 + 3e/t. Tubular joints restrain the offset more; DNV-RP-C203 gives the tubular formula. Example SCF = 1.10 → Δσ_hs = 100.7 MPa.
VO: The weld itself raises the stress. The most important reason in a girth weld is {mis}misalignment. Offset two plates by e and pull them with a force N: the line of force has to jog sideways, which creates a {moment}moment N times e at the weld. If both sides restrain it equally, each takes half, and the extra bending stress is three N e over t squared. {scf}So the stress concentration factor is one plus three e over t. [pause 0.3] {tube}A tube restrains the offset better than a flat plate, and D N V gives the tubular version. In our example we use an S C F of one point one zero, so {hs}the hot spot stress range is one hundred point seven megapascals.

## 6.5 | the template slot hot spot
SHOT: TS1: the upper slot ring welded to two support beams. Ring force F split into two fixed-fixed beams loaded at mid span: M_mid = (F/2)L/8 = FL/16. σ = SCF·FL/(16W) → κ_T = 2.0 × 2.5 / (16 × 2.0e-3) = 0.156 MPa per kN. At 3000 kNm: ΔF_C = 598 kN → 93.5 MPa.
VO: Our second hot spot, {ts1}T S one, is in the template: the weld where the upper slot ring meets its support beams. The ring force is shared by two beams, each fixed at both ends and loaded at mid span. {beam}A fixed-fixed beam with a central load P has a mid span moment of P L over eight, so each beam sees F L over sixteen. {kappa}With an S C F of two, that gives zero point one five six megapascals per kilonewton of ring force. [pause 0.3] {num}At a wellhead moment range of three thousand, the ring force range is five hundred and ninety-eight kilonewtons, and the hot spot stress range is ninety-three megapascals.

## 6.6 | where the hot spots are
SHOT: 3D: hot spots light up on the model with labels: WH housing–extension weld, surface casing at top of cement, GW1 conductor housing–extension girth weld, conductor below mudline (girth welds/connectors — connectors outside U-001 scope), TS1 template slot weld. Callout B.2.3 e) and Table B.11 note: 4–6 hot spots with the lowest capacity are typically sufficient.
VO: In a real assessment, {fea}the critical regions are found by finite element analysis, and the standard notes that four to six hot spots with the lowest capacity are usually enough. {list}Typical candidates are the wellhead housing to extension weld, the surface casing near the top of the cement, the conductor girth welds, and the template slot welds. We follow two of them all the way: G W one and T S one.

# 7 | Building the M-N curve | mn

## 7.1 | why M-N
SHOT: Side by side: S-N (stress range vs cycles) and M-N (wellhead moment range vs cycles). Arrow: "capacity expressed at the same datum as the load". Callout B.4.2.1: M-N curves shall be established for all connectors and wellheads.
VO: Step five. The load histogram is written in wellhead moments, but the S N curve is written in stress. So NORSOK asks us to express the capacity directly in moments: an {mn}M N curve, the number of cycles to failure against the moment range at the wellhead datum. {why}Load and capacity then live at the same point, and comparing them becomes trivial.

## 7.2 | linear transfer derivation
SHOT: If Δσ = κ ΔM: N = ā_σ (κΔM)^{−m} = (ā_σ κ^{−m}) ΔM^{−m} → ā_ΔM = ā_σ κ^{−m}, log ā_ΔM = log ā_σ − m log κ. Formulas B.8 and B.9 appear.
VO: If the stress were simply proportional to the moment, {lin}delta sigma equal to kappa times delta M, the conversion would be one line. Put it into the S N curve: N equals a bar sigma, times kappa delta M, to the minus m. {group}Group the constants, and you get the same power law in the moment, with a new intercept, a bar sigma times kappa to the minus m. {b8}That is formula B eight, and in logarithms, B nine. The slope does not change. Only the intercept moves.

## 7.3 | why it is not that simple
SHOT: The transfer functions from the local model: Δσ_GW1 vs ΔM (slightly bending over) and Δσ_TS1 vs ΔM (zero until the 2 mm gap closes, then rising). Callout B.4.1: "there may be a nonlinear relation between load and stress, finite element analysis shall be used".
VO: But in a wellhead, the stress is {nonlin}not proportional to the moment. Contacts open and close, gaps take up, and preload is overcome. {gwcurve}Look at our girth weld: the curve bends over as the template slot starts to help. {tscurve}And the template weld sees nothing at all until the two millimetre gap closes. That is why the standard requires finite element analysis to find the stress ranges.

## 7.4 | the B.4.2.4 procedure
SHOT: Procedure B.4.2.4 a)–f) as animated steps on the local model: a) 3D elastic model with contacts, preload, cement shortfall, friction, tolerances, clearances; b) apply M_w,i and Q_w,i = M_w,i/H_LFJ; c) fully reversed R = −1: +M then −M, ΔM = 2M, ΔQ = 2M/H_LFJ, stress range at each hot spot, iterate to convergence; d) N_i from the S-N curve; e) report N_i vs ΔM_w,i; f) repeat to cover 1e4–1e8 cycles. Note 1 moment ranges: 6000, 3000, 1500, 750, 375 and 187.5 kNm.
VO: The procedure in clause B four point two point four goes like this. {a}a, build a three dimensional elastic model with all the contacts, preloads, cement shortfall, friction, tolerances and clearances. {b}b, apply a moment at the datum, together with its shear, the moment over H. {c}c, apply it plus, then minus, fully reversed, and compute the stress range at every hot spot, iterating until the contacts converge. {d}d, read the cycles to failure from the S N curve. {e}e, report those cycles against the moment range. {f}And f, repeat with different moment levels until you cover ten to the four to ten to the eight cycles. The standard suggests six levels, halving each time, from six thousand down to one hundred and eighty-seven and a half kilonewton metres.

## 7.5 | our local model
SHOT: The teaching model: two beam strings (wellhead/surface casing inside, conductor housing/conductor outside), contacts A and B, template rings C and D with a 2 mm gap, bonded below the top of cement E, soil springs H. Deflected shape (exaggerated) and moment diagrams in both strings for ±1500 kNm. Badge: "teaching stand-in for the 3D FE model".
VO: For this tutorial we built a simplified version of that model, {beams}two beam strings, the wellhead and casing inside, the conductor housing and conductor outside, {springs}joined at the contacts, supported by the template rings with a two millimetre gap, glued together below the top of the cement, and resting on soil springs. {honest}It is a teaching stand-in for the three dimensional model, but it follows the same steps, so let's run them.

## 7.6 | six points
SHOT: Table of the six levels: ΔM, Δσ_GW1, N_GW1, ΔF_C, Δσ_TS1, N_TS1 (from model.json). Points drop onto a log-log M-N chart one by one.
VO: {six}Six moment ranges, plus and minus each. At six thousand kilonewton metres the girth weld sees two hundred megapascals and fails after about one hundred thousand cycles. {three}At three thousand, a hundred megapascals, and about eight hundred thousand cycles. {low}At the low end, the stresses are a few megapascals and the lives run into the hundreds of billions of cycles. [pause 0.3] {tsp}The template weld follows the same pattern, but it falls away much faster at small moments, because there the gap is open.

## 7.7 | bilinear curve and the knee
SHOT: Formula B.10 (two branches) and the knee: setting log ā1 − m1 log ΔM = log ā2 − m2 log ΔM gives log ΔM_1,2 = (log ā2 − log ā1)/(m2 − m1), formula B.11.
VO: Because the S N curve has two slopes, the natural capacity format is a {bil}bilinear M N curve, formula B ten: slope m one for large moments, slope m two for small ones. Where do the branches meet? {set}Set the two expressions for log N equal. {knee}The log of the moment at the knee is the difference of the intercepts, divided by the difference of the slopes. That is formula B eleven.

## 7.8 | lower bound fit
SHOT: Keep the slopes 3 and 5, slide each branch down until no point lies below it: log ā = min_i (log N_i + m log ΔM_i). Results GW1: log ā1 = 16.33, log ā2 = 22.75, ΔM_1,2 = 1617 kNm. TS1: 16.25, 23.26, 3229 kNm. Note: the smallest moment controls the GW1 m = 5 branch.
VO: The standard asks for a {lower}lower bound, a capacity curve at or below every point. A simple way is to keep the S N slopes, three and five, and {slide}slide each branch down until no point lies below it. In logs, each intercept is the smallest value of log N plus m log delta M over the points of that branch. [pause 0.3] {gwres}For G W one that gives sixteen point three three for the steep branch, twenty-two point seven five for the flat branch, and a knee at about sixteen hundred kilonewton metres. {note}Notice that the flat branch is set by the smallest moment, where the gap is open and the conductor works alone. The lower bound protects you from exactly that kind of nonlinearity.

## 7.9 | RF and ΔMc
SHOT: Callout B.4.4: "Linear and bi-linear M-N curves shall include a fatigue life reduction factor (RF) in accordance with DNV-RP-C203:2024 Section 5.7": N_design = N / RF → log ā − log RF; life ∝ 1/RF. Then ΔMc: the single-load fatigue capacity at 10^6 cycles, DF = 1: GW1 2780 kNm, TS1 2838 kNm. Table B.12 filled in.
VO: Two more items complete the capacity. {rf}The M N curve shall include a fatigue life reduction factor, R F, from D N V R P C two oh three section five point seven. It divides the cycles, so it simply lowers log a bar by log R F. We keep it at one in this example so the arithmetic stays visible. Just remember that the life scales with one over R F. [pause 0.3] {dmc}And the standard asks you to tabulate delta M c, the single load fatigue capacity at one million cycles. For our girth weld it is about two thousand seven hundred and eighty kilonewton metres, and for the template weld about two thousand eight hundred and forty.

# 8 | Damage, life and the design check | damage

## 8.1 | Palmgren-Miner
SHOT: A "life bar". One cycle at level i consumes 1/N_i of the life; n_i cycles consume n_i/N_i; the bar fills with coloured segments from each bin: D = Σ n_i/N_i; failure at D = 1 (NORSOK 3.2.21).
VO: Step six is the damage. {one}If a moment range gives failure after N i cycles, then one cycle uses up a fraction, one over N i, of the life. {ni}n i cycles use up n i over N i. The Palmgren Miner rule simply {sum}adds these fractions over all the bins, ignoring the order in which the cycles come. {fail}Failure is predicted when the sum reaches one.

## 8.2 | from damage to life
SHOT: For an annual histogram, D_year → fatigue life T_f = 1 / D_year. Formula B.3: service life ≤ fatigue life / DF; B.4: inspection interval ≤ fatigue life / DF. Table B.4: permanent equipment 10, temporary 3 for service life and 10 for inspection interval.
VO: Our histogram covers one year, so the damage is a {dy}damage per year, and the fatigue life in years is simply {inv}one over that damage. [pause 0.3] {b3}The design format, formula B three, then says that the service life must not exceed the fatigue life divided by the design fatigue factor. {b4}The same format sets inspection intervals. {table}And table B four gives the factor: ten for permanent equipment, which is assumed never to be inspected, three for the service life of temporary equipment, and ten for inspection intervals.

## 8.3 | template design fatigue factor
SHOT: NORSOK N-001 DFF matrix: rows substantial / without substantial consequences, columns no access or splash zone / accessible below splash zone / above splash zone or internal: 10 3 2 / 3 2 1. The template slot weld: no access, substantial consequences → 10. Flag: check the N-001 edition in the design basis.
VO: For the template, Annex A sends us to {n001}NORSOK N zero zero one, where the design fatigue factor depends on two questions. Can the detail be inspected and repaired? And would its failure have substantial consequences? {ts}A slot weld hidden behind the conductor housing cannot be inspected, and losing it would take away support from the well. {ten}So we use ten.

## 8.4 | the equivalent moment range
SHOT: Derivation of B.14 for a linear curve: D = Σ n_i ΔM_i^m / ā; define n cycles of ΔM_eq with the same damage: n ΔM_eq^m / ā = Σ n_i ΔM_i^m / ā → ΔM_eq = [(1/n) Σ n_i ΔM_i^m]^{1/m}. Numbers: n = 7,472,771, m = 3 → ΔM_eq = 683 kNm.
VO: Now let's derive the remaining formulas of clause B four point four. With a linear M N curve, the damage is {d}the sum of n i times delta M i to the m, divided by a bar. Ask: what single moment range, {neq}applied for all n cycles, would do the same damage? Set the two damages equal. The a bar cancels, {meq}and the equivalent range is the average of delta M to the m, raised to the power one over m. That is formula B fourteen. [pause 0.3] {num}For our histogram and m equal to three, seven point four seven million cycles at six hundred and eighty-three kilonewton metres do the same damage as the whole year.

## 8.5 | the single-load moment range
SHOT: Derivation of B.13 and B.12: the "demand curve" through (n, ΔM_eq) has log ā = log n + m log ΔM_eq (B.13); the moment range on that curve at 10^6 cycles: log ΔMo = (1/m)(log ā − log 10^6) (B.12). Numbers: ΔMo = 1335 kNm for m = 3 → 0.93 × 1436: Table A.7 is slightly conservative.
VO: The standard goes one step further. {through}Draw a demand curve with slope m through that equivalent point. Its intercept is log n plus m log delta M e q. That is formula B thirteen. {at6}Now read that curve at one million cycles. The moment range there is delta M zero, formula B twelve: one over m, times log a bar minus six. [pause 0.3] {num}If we do this for our histogram with m equal to three, we get about thirteen hundred and thirty-five kilonewton metres, seven percent below the fourteen thirty-six in table A seven. {cons}So the tabulated single load value is slightly conservative. A nice check that we understand what it means.

## 8.6 | the screening check
SHOT: Derivation: damage for the annual histogram D = (ΔMo/ΔMc)^m → fatigue life T_f = T (ΔMc/ΔMo)^m; requirement T_f/DF ≥ T → ΔMc / DF^{1/m} ≥ ΔMo (Example 2 in A.3.5.1, EXAMPLE in B.4.4). DF in moment space: 10^{1/3} = 2.15. Sensitivity: +10 % moment → life × 0.75 (m = 3), × 0.62 (m = 5).
VO: Here is the payoff. If the demand and the capacity are both written at one million cycles, the damage of one year is just {ratio}delta M zero over delta M c, to the power m. So the fatigue life is the histogram period times delta M c over delta M zero, to the m. {req}Require that life divided by the design factor is at least one year, take both sides to the power one over m, {screen}and you get the screening check: delta M c divided by D F to the one over m must be at least delta M zero. [pause 0.3] {dfm}In moment space, a design factor of ten is only a factor of two point one five, because the moment enters to the power three. {sens}The flip side: ten percent more moment costs a quarter of the life with m equal to three, and almost forty percent with m equal to five.

# 9 | Worked example | example

## 9.1 | the example well
SHOT: Input card (ILLUSTRATIVE): 350 m water depth, BOP on WH mode, ΔMo = 1436 kNm, H_LFJ = 13.7 m; 36 × 2 in conductor, 20 × 1 in surface casing; datum 4.0 m above mudline; template rings C and D at 1.6 m and 3.6 m below datum, 200 and 400 MN/m, 2 mm radial gap; soil k = 5 MPa; cement shortfall 5 m; GW1 at 3.0 m, C1 seawater + CP, SCF 1.10, t = 50.8 mm; TS1 class D seawater + CP, 0.156 MPa/kN; DF = 10, DFF = 10. Banner: "Illustrative inputs — not project data".
VO: Time to put it all together. {inputs}Here is our example well: three hundred and fifty metres of water, B O P on the wellhead, a thirty-six inch conductor and a twenty inch surface casing, a four slot template with two millimetres of clearance in the slot, soft clay, and five metres of cement shortfall. {flag}All inputs are illustrative teaching values, not data from a real project. The steps, though, are exactly the standard's.

## 9.2 | step 1 — loads
SHOT: Histogram builds: 29 bins, ΔM_i = r_i × 1436 kNm, n_i from Table A.8.
VO: {hist}Step one: twenty-nine bins, each normalised range from table A eight multiplied by fourteen thirty-six kilonewton metres.

## 9.3 | screening
SHOT: Screening GW1: ΔMc = 2780 kNm, DF^{1/3} = 2.154 → 1290 kNm < ΔMo = 1436 kNm → FAIL (red). Equivalent life (ΔMc/ΔMo)^3 = 7.3 years → service life 0.73 years.
VO: {screen}First, the quick screening check for the girth weld. Delta M c is two thousand seven hundred and eighty. Divide by ten to the power one third, and we get twelve hundred and ninety, {fail}which is less than fourteen thirty-six. The screening fails. It predicts a fatigue life of only seven point three years, and less than one year of service. [pause 0.3] {nopanic}But the screening uses a single slope of three for every cycle. Most of our cycles live on the flatter slope of five, where they do far less damage. So let's do the real calculation.

## 9.4 | Miner sum GW1
SHOT: The full Miner table for GW1 builds bin by bin (ΔM_i, n_i, N_i, d_i), with a damage-density chart: most damage from bins r = 0.7–1.6 (≈ 1000–2300 kNm); the 3.9 million smallest cycles contribute almost nothing. Total D = 0.0712 per year → fatigue life 14.0 years → service life 14.0 / 10 = 1.40 years = 513 days ≥ 1 year: PASS.
VO: {table}For each bin, read N from the bilinear M N curve and divide the cycles by it. {where}Look where the damage comes from. Not from the four million tiny cycles, and not from the one or two monsters, {mid}but from the middle: moment ranges between about one thousand and two thousand three hundred kilonewton metres do most of the work. [pause 0.3] {total}The damage adds up to zero point zero seven one per year. {life}So the fatigue life is fourteen years. Divide by the design factor of ten, and the {svc}fatigue service life is one point four years, or about five hundred and thirteen days with a riser connected. {pass}More than the one year minimum. The girth weld passes.

## 9.5 | linear versus bilinear
SHOT: Three bars: screening 7.3 years, linear m = 3 Miner 9.0 years, bilinear Miner 14.0 years (fatigue life). Labels: conservative → refined.
VO: {three}Compare the three answers: seven point three years from the screening, nine years from a full sum with a single slope, and fourteen years with the bilinear curve. {lesson}Each step removes a layer of conservatism. Use the screening to sort designs, and do the full sum when it matters.

## 9.6 | template slot TS1
SHOT: Same procedure for TS1: D = 0.0280 per year → fatigue life 35.7 years → DFF 10 → 3.57 years = 1304 days: PASS.
VO: {ts}The template weld gets the same treatment. Its damage is zero point zero two eight per year, {life}a fatigue life of thirty-six years, and with a design factor of ten, about three and a half years of fatigue service life. {pass}It passes too.

## 9.7 | the load-share trade-off
SHOT: Slider on the slot gap: 0 mm → GW1 service 7.3 years but TS1 0.39 years (fail); 1 mm → 2.0 / 2.7; 2 mm (base) → 1.4 / 3.6; 4 mm → 1.26 / 6.8. No template contact at all → GW1 0.98 years (fail). Caption: "load share moves damage — it does not delete it".
VO: Now play with the {gap}slot clearance. Close the gap completely, and the template grabs a big share of the moment. {gw}The girth weld's service life jumps to more than seven years, but {tsfail}the template weld drops below half a year and fails. Open the gap to four millimetres, and the opposite happens. {none}Remove the template contact altogether, and the girth weld fails at just under one year. [pause 0.3] {lesson}Load share moves damage around. It never deletes it. That is why clause eight point one asks for the load share to satisfy fatigue for the wellhead system, and the template, at the same time.

## 9.8 | sensitivities
SHOT: Tornado chart of GW1 fatigue service life (years): SCF 1.0 → 2.10, 1.2 → 0.99, 1.3 → 0.73; soil 2 MPa → 1.65, 20 MPa → 1.37; cement shortfall 0–15 m → 1.45–1.38; water depth band 80–250 m → 0.33, 500–1500 m → 3.07; BOP on XT mode (250–500 m) → 0.63.
VO: {tornado}Here is how the girth weld's service life responds to the other inputs. {scf}Fabrication quality is huge: an S C F of one point two instead of one point one, and the weld no longer passes. {depth}Water depth is huge: in the eighty to two hundred and fifty metre band the same well gets only a third of a year. {xt}And running the B O P on a christmas tree cuts the life by more than half. {soil}Soil stiffness and cement shortfall matter less for this particular weld, though they matter a lot for welds on the inner string.

## 9.9 | when it fails: mitigation
SHOT: Shallow-water case (80–250 m): GW1 0.33 years, TS1 0.53 years. Mitigation cards from NORSOK: lateral BOP support / load relief (13.2, OMAE2023-104891) — 40 % moment reduction → GW1 2.31 years, TS1 6.48 years; Table J.1 operational factors (LMRP overpull, lower flex joint stiffness, riser tally, drill pipe tension, rig heading — beam sea worst); monitoring (J.4.3) and life extension (NORSOK U-009).
VO: So what if your well is in shallow water and fails? {relief}NORSOK points to several levers. The template can be prepared for a lateral B O P support system. If it removes forty percent of the moment, our shallow water girth weld goes from a third of a year to more than two years. {j1}Table J one lists operational levers: less L M R P overpull, a softer lower flex joint, a better riser tally, lower drill pipe tension, and avoiding beam seas. {monitor}And monitoring the wellhead during operations replaces the conservative design histogram with measured loads, so the fatigue life can be updated, and extended.

# 10 | Summary | summary

## 10.1 | the method on one page
SHOT: One-page summary board with all key equations: M(z) = M_w(1 + z/H); F_i = k_i/Σk F; M_i = EI_i/ΣEI M; k_θ = k_C k_D h²/(k_C + k_D); EI y'''' + k y = 0; σ = M/W, I = π(D⁴ − d⁴)/64; SCF = 1 + 3e/t; N Δσ^m = ā; log ā_ΔM = log ā − m log κ; log ΔM_1,2 = (log ā2 − log ā1)/(m2 − m1); D = Σ n_i/N_i; ΔM_eq; ΔMo; ΔMc/DF^{1/m} ≥ ΔMo; service life ≤ fatigue life / DF.
VO: Let's recap the whole method on one page. {loads}Take the annual histogram at the wellhead datum, and remember that the moment grows below it. {share}Follow the load paths: stiffness attracts load, gaps make it nonlinear. {soil}Below the mudline the conductor is a beam on springs, with a peak moment just below the seabed. {stress}Convert moments to hot spot stresses with beam theory and stress concentration factors. {mn}Build lower bound M N curves from a local model. {damage}Add up the damage with Palmgren Miner, {check}divide the life by the design factor, and check it against at least one year of riser connected time.

## 10.2 | outro
SHOT: 3D: the camera pulls back from the wellhead and the template, up the riser, to the rig on the surface at dawn. End card: sources (NORSOK U-001:2026; DNV-RP-C203; NORSOK N-001; DNV wellhead fatigue method), note that the example is illustrative.
VO: {back}A conductor and a template slot are among the few parts of a subsea well that have to last for the whole life of the field, and can never be inspected. {care}The method in NORSOK U zero zero one lets us put a number on how much riser time they can take. Use it with care, check the S N data against the current D N V edition, and keep monitoring. [pause 0.4] {end}Thanks for watching.
HOLD: 7
