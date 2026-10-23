# The template interface — when has it failed?
#
# Format
#   # <chapter no> | <title> | <id>
#   ## <beat id> | <short name>
#   SHOT: what the picture does (for the animator)
#   VO: narration. {cue} marks the word an animation is keyed to. [pause 0.8] adds silence after a sentence.
#   HOLD: extra seconds at the end of the beat
#
# Numbers quoted in the VO come from src/data/model.json (model/interface_model.py). The slot ring, its load and the
# material factors are ILLUSTRATIVE (teaching inputs, not project data). The ring is analysed with a fibre beam model
# (materially non-linear, geometrically linear); the 3D contour is drawn from that model.

# 0 | Cold open | coldopen

## 0.1 | the push
SHOT: 3D. A four-slot template on the seabed, the well in one slot. The camera descends to the slot. The riser load bends the well; the conductor pushes on the lower slot ring D, which glows at the contact.
VO: {tmpl}This is where the well meets the template. {slot}The conductor housing lands in a slot of the template structure, {ring}and lower down, the conductor is guided by a ring in the bottom of the structure. [pause 0.3] {push}When the riser pulls on the wellhead, the conductor pushes on that ring.

## 0.2 | the questions
SHOT: Close-up on the slot ring with the conductor inside it and an arrow for the contact force. Three question cards on the left: "0.2 % plastic strain?", "5 % strain?", "2 % strain?".
VO: So when has this interface failed, according to the standard? {q1}When the steel reaches zero point two percent plastic strain, the yield strength? {q2}Or at a strain limit, like the five percent, {q3}or the two percent, that people attribute to Eurocode three, part one five?

## 0.3 | title
SHOT: Title card over the darkened ring: "The template interface" / "When has it failed?" and the chain NORSOK U-001:2026 → N-001 → N-004 → Eurocode 3. Four topic pills.
VO: In this follow-up to the acceptance criteria video, we find out {who}which standard owns the interface, {what}what failure means on each side of it, {ec}what Eurocode three actually says, {check}and we check the slot ring both ways.

# 1 | Who owns the interface | owner

## 1.1 | the contacts
SHOT: 3D cutaway of the wellhead in the template slot. Letters from U-001 Figure J.1: F, A, C, D, G. Load path 3 draws as a glowing line F → A → C → D → G (guide structure to seabed).
VO: NORSOK U zero zero one names the contacts in Figure J one. {C}Contact C is between the template structure and the conductor housing, {D}and contact D is at the bottom of the structure. [pause 0.3] {path}When the template is in the load path, load path three runs from the wellhead, through the conductor, {G}into the guide structure and down to the seabed. {share}How much load goes that way is the load share. {stiff}It depends on the tolerances and on the relative stiffness of well, template and soil.

## 1.2 | two sides, two rule books
SHOT: Two columns. Left, the wellhead side (conductor housing, conductor): U-001 Annex B and B.9, σy at 0.2 % plastic strain, capacities as loads. Right, the template side (slot rings, struts): clause 13.3.6.1 → ISO 13628-15 clause 5.4 + NORSOK N-001 → NORSOK N-004:2022 → Eurocode 3 (NS-EN 1993). A tag on the right: "no failure criterion for the template steel in U-001".
VO: The interface has two sides, and each side has its own rule book. {wh}The wellhead side, the conductor housing and the conductor, is checked to Annex B of U zero zero one {b9}and the pipe formulas of clause B nine. That was the first video: the yield strength at zero point two percent plastic strain, and capacities found as loads. [pause 0.3] {tm}The template side is different. {clause}Clause thirteen point three point six point one says that structural design shall follow I S O thirteen six twenty-eight, part fifteen, clause five point four, and NORSOK N zero zero one. {n004}N zero zero one sends steel design on to N zero zero four, {ec3}and N zero zero four builds on Eurocode three. [pause 0.3] {none}So U zero zero one has no failure criterion of its own for the template steel. It hands it over.

## 1.3 | the interface as a mechanism
SHOT: Schematic section of the slot: the conductor housing between a lower and an upper end stop, with gaps. The well grows up (thermal growth) while the template settles; the gap closes. Cards: 13.3.6.2 "100 mm relative vertical displacement", Table A.2 note d "SLS, load factor 1.0, margins to the end stops; end stop reached → preload → separate ULS load cases", 13.3.6.4 "template inclination ≤ 0.3°".
VO: Before any stress, the interface can fail as a mechanism. {grow}The well grows with temperature, and the template settles. {mm}Clause thirteen point three point six point two asks the template design to account for a relative vertical displacement of one hundred millimetres between template and conductor, unless otherwise specified. {sls}Note d of Table A two makes this a serviceability check, with load factor one point zero: {stops}the margins to the upper and lower end stops are checked. {preload}If an end stop is reached, the template is preloaded, and that force goes into separate ultimate limit state load cases. [pause 0.3] {tilt}And the installed template may not lean more than zero point three degrees, unless the tolerance loops allow it.

# 2 | The template steel: the elastic check | elastic

## 2.1 | partial factors
SHOT: Design format S_d ≤ R_d with S_d = γf·S_k and R_d = R_k/γM. A table: ULS (case K): riser loads × 1.3, γM 1.15; ALS (case L): × 1.0, γM 1.0; SLS: × 1.0.
VO: On the template side there are no design factors. It is {lrfd}load and resistance factor design. {load}The loads are multiplied by the load factors of N zero zero one, which Table A two lists: one point three on the extreme riser loads in the ultimate limit state, one point zero in the accidental case. {res}The resistance is divided by a material factor: {gm}one point one five for steel in the ultimate limit state, in N zero zero four, and one point zero in the accidental limit state.

## 2.2 | yield, the Eurocode way
SHOT: Stress-strain diagram of S355 plate (strain 0 to 1 %): elastic line, upper yield point, yield plateau; the 0.2 % offset line. Labels: fy = 345 MPa for 16 < t ≤ 40 mm (EN 10025-2), εy = fy/E = 0.16 %.
VO: And the yield strength? {s355}For a forty millimetre plate of S three fifty-five, the nominal yield strength, f y, is three hundred and forty-five megapascals. {reh}Eurocode three takes it from the product standard: the upper yield strength, {rp}or the zero point two percent proof strength when the steel shows no distinct yield point. {same}So yes, it is the same idea as the zero point two percent offset. {ey}And it is reached at a strain of only zero point one six percent.

## 2.3 | the elastic check
SHOT: Left: the criterion of EN 1993-1-1 6.2.1(5) with γM0. Right: 3D FE view of the slot ring (40 mm plate, inner radius 459 mm, width 200 mm, four struts) with the conductor pushing between two struts; banded von Mises contour at the design contact force 1.6 MN; probe at the outer edge behind the contact: 416 MPa; legend with fy/γM0 = 300 MPa. Utilisation 1.39, a FAIL stamp.
VO: The first Eurocode check is elastic. {vm}Clause six point two point one, paragraph five, of part one one: the von Mises stress at the critical point shall not exceed f y divided by gamma M zero. [pause 0.3] {ring}Here is the lower slot ring, cut from that plate, with the conductor pushing on it between two struts. {contour}At the design contact force of one point six meganewtons, {peak}the outer edge behind the contact reaches four hundred and sixteen megapascals. {fyd}The limit is three hundred. {util}Utilisation, one point three nine. [pause 0.3] {fail}So by the elastic check, the ring has failed. {but}But that check stops at the first point that yields. It is the most conservative option, not the only one.

# 3 | Non-linear FE: EN 1993-1-5 Annex C | annexc

## 3.1 | Annex C
SHOT: Card: EN 1993-1-5 Annex C (informative), Finite element methods of analysis. Two rows after Table C.1: material non-linear, geometry linear, no imperfections → plastic resistance (ULS); material and geometry non-linear with imperfections → elastic-plastic resistance with buckling (ULS). The first row is highlighted for the stocky ring.
VO: For a plated detail in a finite element model, Eurocode three offers another route: {annex}Annex C of part one five, finite element methods of analysis. {inf}It is an informative annex, so the National Annex and your design basis decide whether it is used. {mna}For a stocky part that cannot buckle, like this ring, a materially non-linear analysis is enough. {gmnia}Where buckling is possible, the geometric non-linearity and the imperfections must be included as well.

## 3.2 | material and load
SHOT: Stress-strain chart with the material models of C.6: (a) elastic-plastic without strain hardening, (b) with a nominal plateau slope, (c) with linear strain hardening, (d) true stress-strain curve from tests. "characteristic values: fy, not fy/γM". Then: design loads × α (C.7), α increasing.
VO: Clause C six gives the material models: {a}elastic plastic without strain hardening, {b}with a nominal plateau slope, {c}with linear strain hardening, {d}or a true stress strain curve from tests. {char}They use characteristic values: f y itself, not divided by the material factor. [pause 0.3] {load}Clause C seven puts the factored design loads into the model, multiplied by one load multiplier, alpha, {ramp}which the analysis increases until a limit state is reached.

## 3.3 | the limit state criteria
SHOT: Quote card of C.8(1): 1. for structures susceptible to buckling phenomena: attainment of the maximum load; 2. for regions subjected to tensile stresses: attainment of a limiting value of the principal membrane strain. Note 1: the National Annex may specify the limiting value of a principal strain; 5 % is recommended. Note 2: other criteria may be used, e.g. attainment of the yielding criterion or limitation of the yielding zone. Then a shell section: membrane strain at mid-thickness vs surface strain.
VO: And here is the clause you heard about: C eight, the limit state criteria. {buck}Where the structure is susceptible to buckling, the criterion is reaching the maximum load. {tens}In regions in tension, it is reaching a limiting value of the principal membrane strain. {five}Note one: the National Annex may specify that value, {rec}and five percent is recommended. {other}Note two: other criteria may be used, for example reaching the yield criterion, or limiting the yielded zone. [pause 0.3] {membrane}Membrane means the strain at mid thickness of the shell, not the surface value with plate bending added on top.

## 3.4 | running the ring
SHOT: Left panel: 3D ring with the principal strain contour growing; white iso-line at 5 %. Right: chart of load multiplier α against the radial displacement at the contact, model (a) and model (c); markers at first yield 0.83, 0.2 % plastic strain 1.25, the plateau of (a) 1.54, 5 % of (c) 1.76.
VO: Let's run it. {lin}Up to eighty-three percent of the design load, the ring is elastic. {y}Then the outer edge behind the contact yields, {p02}and at one point two five times the design load it has zero point two percent plastic strain. {spread}The plastic zones spread, behind the contact and at the struts. {flat}Without strain hardening, the curve flattens at one point five four: {mech}a plastic mechanism. {hard}With linear hardening, it keeps rising. There is no peak and no buckling, {five}so the five percent strain decides: at one point seven six times the design load.

## 3.5 | the margin
SHOT: The criterion of C.9: αu ≥ α1·α2 with α1 (FE model uncertainty, from test calibration, EN 1990 Annex D) and α2 (γM1 if instability governs, γM2 if fracture governs). Check: 1.76 ≥ 1.0 × 1.3 and, without hardening, 1.53 ≥ 1.3. PASS stamp next to the earlier FAIL.
VO: Clause C nine sets the margin. {au}The multiplier at the limit state, alpha u, shall be at least alpha one times alpha two. {a1}Alpha one covers the uncertainty of the F E model, calibrated against tests. {a2}Alpha two covers the scatter of loads and resistance: gamma M one where instability governs, gamma M two where fracture governs. {ex}With alpha one equal to one, for a benchmarked model, and alpha two no more than one point three, {pass}alpha u of one point seven six passes, {passa}and so does one point five three without hardening. [pause 0.3] {verdict}So the ring that failed the elastic check is accepted by the non-linear one, with margin.

# 4 | Five percent, and the two | twopct

## 4.1 | where is the two percent?
SHOT: Card: EN 1993-1-5 Annex C — one strain value: 5 % (recommended, nationally determined). "2 %: not found in EN 1993-1-5". Bars: α at 2 % and at 5 % for model (c) 1.59 / 1.76 (−10 %) and model (a) 1.49 / 1.53 (−2 %).
VO: Now the two percent. {one}Annex C contains one strain value, the recommended five percent. {none}We found no two percent criterion in part one five. {ask}If someone quotes one, ask which document it comes from, and which strain it limits. [pause 0.3] {cmp}And what would it change here? {c}With hardening, stopping at two percent instead of five lowers the capacity by ten percent. {a}Without hardening, by only two percent, because the curve is already flat.

## 4.2 | strain depends on the mesh
SHOT: Chart of α against the largest strain for four element sizes (5°, 2.5°, 1.25°, 0.625°), model (a): the curves fan out to the right; a marker line at α = 1.50 with 1.4 % … 2.4 %. Model (c): the four curves lie on top of each other. Then a card: EN 1993-1-14:2025, Design assisted by finite element analysis.
VO: There is a catch with every strain limit. {mesh}Without hardening, the same load, one point five times the design load, gives one point four percent strain with coarse elements, and two point four percent with fine ones. {load}The load at the limit hardly moves, but the strain does. {harden}With hardening, the mesh no longer matters. [pause 0.3] {lesson}So a strain limit always comes with a material model, a mesh, and a definition of the strain. {ec14}The second generation of Eurocode three develops this into a part of its own, E N nineteen ninety-three, part one fourteen, published in twenty twenty-five. {edition}Check which edition your design basis calls for.

# 5 | Summary | summary

## 5.1 | when has it failed?
SHOT: Summary table: interface function (end-stop margins, 100 mm, 0.3°; SLS with load factor 1.0; U-001 13.3.6, Table A.2 note d) · wellhead side (load ≤ Fd × capacity, σy at 0.2 % plastic strain; U-001 Annex B, B.9) · template, elastic (von Mises ≤ fy/γM0 at the critical point; EN 1993-1-1 6.2.1(5), γM from N-004) · template, non-linear (maximum load if buckling, 5 % principal membrane strain in tension, αu ≥ α1·α2; EN 1993-1-5 Annex C) · 2 % (not in EN 1993-1-5).
VO: So, when has the template interface failed? {fn}As a mechanism, when the relative displacement uses up the margin to the end stops. {wh}On the wellhead side, when the load exceeds F d times the capacity of Annex B, with the yield strength at zero point two percent plastic strain. {tel}On the template side, by the elastic route, when the von Mises stress at a point reaches f y over gamma M. {tnl}And by the non-linear route, at the maximum load or at five percent principal membrane strain, with alpha u at least alpha one times alpha two. {two}Two percent is not a criterion of Eurocode three, part one five.

## 5.2 | outro
SHOT: Sources and a disclaimer: teaching model and inputs; verify the clauses against the editions and the National Annex of the design basis.
VO: The ring, its load and the factors in this video are teaching inputs. {src}The clauses are on screen, and the notes list what was checked and against which source. Use the editions and the National Annex of your own design basis.
HOLD: 2.0
