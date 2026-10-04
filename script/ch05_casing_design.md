# Ch 5: Casing and tubular design
BUDGET: 165

## 5.01 | 24.5 | anim
VO: Casing is the well's tunnel lining. It holds the hole open, contains pressure, and isolates formations. Its grade is a number: P one-ten means a minimum yield of one hundred and ten thousand psi, about seven hundred and sixty megapascals. Sour-service grades limit hardness, because hydrogen sulphide cracks hard steel.
SHOT: Tunnel-lining cutaway analogy morphs into the casing string in the hole. A pipe tag reads "P110: 110 ksi = 758 MPa". A hardness-vs-cracking sketch for sour service with an H2S molecule label.
FLAGS: GEN; VERIFY: grade list and yield conversion are from memory of API 5CT / ISO 11960 (110 ksi = 758 MPa is arithmetic and exact); sour-service rule wording (ISO 15156) not checked
TERMS: casing grade; sour service

## 5.02 | 30.5 | anim
VO: Three loads, three mechanisms. Burst is internal pressure, a thin-wall yield problem, and the API rating already includes a twelve and a half percent wall tolerance. Collapse is external pressure, and it is a buckling problem set by the diameter-to-thickness ratio, like crushing a can from outside. Tension is the string's own weight, limited by the pipe body and, usually, by the connection.
SHOT: Three cross-section panels in sequence: a ring with outward arrows swelling then yielding (burst, with the Barlow-type formula 0.875 x 2 Y t / D appearing after); a ring with inward arrows buckling into an oval (collapse) with a D/t slider moving the failure pressure; a hanging string with a stretch indicator and a connection highlighted (tension).
FLAGS: GEN; VERIFY: the 0.875 factor and the "four collapse regimes" are from memory of API TR 5C3 / ISO 10400; SIM: only the elastic-collapse picture is drawn
TERMS: diameter-to-thickness ratio

## 5.03 | 22 | anim
VO: The design basis picks the worst credible cases. For burst: a gas kick, with the well shut in, meaning closed at the surface. For collapse: the pipe emptied by lost circulation, with heavy mud outside. For tension: running in the hole, with overpull and shock.
SHOT: Three load-case cartoons on the well schematic: shut-in gas column with surface pressure arrow (burst); evacuated casing with heavy mud outside (collapse); string being run with an overpull arrow (tension). A small "design basis" table fills in.
FLAGS: GEN
TERMS: design basis; shut-in

## 5.04 | 22.5 | anim
VO: But those ratings are uniaxial. Real casing feels axial, radial and hoop stress at once. So we check the von Mises equivalent stress against yield, with a design factor. Plotted as an ellipse of axial force against pressure, it shows something odd: tension reduces collapse resistance.
SHOT: A VME ellipse in the axial-force vs differential-pressure plane with burst and collapse intercepts. Adding tension tilts and shifts the ellipse so the collapse intercept moves inward. Load-case dots from beat 5.03 appear inside; a shrunken inner ellipse labelled "design factor" appears. The von Mises expression is shown after the picture.
FLAGS: GEN; SIM: ellipse is the simplified VME yield envelope without bending or thermal load; design factors are shown unlabelled as "operator-specific"
TERMS: von Mises equivalent stress; design factor

## 5.05 | 19.5 | anim
VO: That creates a trap. The top of a string carries the most tension, which cuts its collapse capacity, while the pressures are greatest deep down. So strings are tapered: heavier wall, or stronger steel, only where it is needed.
SHOT: A casing string with colour-coded sections: heavy wall at the top (tension) and at the bottom (collapse), lighter in the middle. A depth-vs-utilisation plot shows each load as a curve staying under the section capacity steps.
FLAGS: GEN
TERMS: tapered string

## 5.06 | 28 | anim
VO: And then the connections. Basic threaded couplings seal with thread compound. Premium connections add metal-to-metal seals and a torque shoulder, to stay gas-tight; they are qualified to ISO thirteen six seven nine, and checked as they are screwed together with a torque-turn plot: torque against turns. The pipe may be fine. The connection is where leaks start.
SHOT: Thread cross-section: API round thread with a spiral leak path and thread compound; then a premium connection with a metal-to-metal seal ring and torque shoulder. A torque-vs-turns plot with a sharp shoulder-engagement kink and an acceptance window.
FLAGS: GEN; VERIFY: ISO 13679 as the connection-testing standard is from memory; "premium connections leak less" is a generalisation
TERMS: premium connection; torque-turn plot

## 5.07 | 18 | anim
VO: In the barrier language of the next chapters, every string is itself a well barrier element, a single object that helps stop flow, with a documented design and a pressure test to prove it.
SHOT: The casing strings of the well schematic light up in blue one by one with a small "tested" tick; label "well barrier element".
FLAGS: NO; VERIFY: element acceptance criteria wording in NORSOK D-010 for casing (design + test) not confirmed
PAUSE: 1
TERMS: well barrier element
