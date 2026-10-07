# Ch 5: Casing and tubular design
BUDGET: 165

## 5.01 | 29.5 | anim
VO: Casing is the well's tunnel lining. It holds the hole open, contains pressure, and isolates formations. Its grade is a letter and a number: P one-ten means a minimum yield of one hundred and ten thousand psi, about seven hundred and sixty megapascals. Hydrogen sulphide drives hydrogen into hard steel and cracks it, so sour-service grades cap hardness, and P one-ten is too hard for most sour wells.
SHOT: Tunnel-lining cutaway analogy morphs into the casing string in the hole. A pipe tag reads "P110: 110 ksi ≈ 758 MPa". A hardness-vs-cracking sketch for sour service: H2S at the surface, hydrogen atoms diffusing into a hard steel lattice, a crack opening; a "sour grades: hardness capped" note.
FLAGS: GEN; VERIFY: grade list and yield conversion are from memory of API 5CT / ISO 11960 (110 ksi = 758 MPa is arithmetic and exact); sour-service rule wording (ISO 15156-2) not checked
TERMS: casing grade; sour service

## 5.02 | 40 | anim
VO: Three loads, three ways to fail. Burst: pressure inside exceeds pressure outside, and the wall yields, like an over-pressured pipeline. Its rating is worked out on a wall twelve and a half percent thinner than nominal, the mill tolerance. Collapse: pressure outside, and the pipe gives way. Thin pipe buckles like a crushed can; thick pipe yields first. The diameter-to-thickness ratio decides which, and most casing sits in between. Tension: the string's weight hanging in mud, plus any pull on it, limited by the pipe body or, often, by the weaker connection.
SHOT: Three cross-section panels in sequence: a ring with net outward arrows (inside minus outside) swelling then yielding, with the Barlow-type formula 0.875 × 2Yt/D after; a ring with inward arrows: a thin ring buckles into an oval, a thick ring yields, a D/t slider shows the regime changing; a hanging string with a buoyed-weight arrow, a stretch indicator and a connection highlighted.
FLAGS: GEN; VERIFY: the 0.875 factor and the four collapse regimes (yield, plastic, transition, elastic) are from memory of API TR 5C3 / ISO 10400
TERMS: diameter-to-thickness ratio

## 5.03 | 34.5 | anim
VO: The design basis picks the worst credible cases. For burst: typically a gas kick, with the well shut in, or the casing pressure test itself. For collapse: lost circulation, where mud drains away into cracked rock, lets the level inside the pipe fall, partly or completely, while the full mud column outside pushes in. For tension: the string's weight as it is lowered in, shock from sudden stops, and overpull, the extra pull needed to free it if it sticks.
SHOT: Three load-case cartoons on the well schematic: shut-in gas column with a surface pressure arrow (burst); the mud level inside the casing falling (partial, then full evacuation) with heavy mud outside (collapse); a string being lowered with a buoyed-weight arrow down at mid-string and an overpull arrow UP at the top (tension). A small "design basis" table fills in.
FLAGS: GEN; SIM: one load case per mode; real design bases list several per string
TERMS: design basis; lost circulation

## 5.04 | 35 | anim
VO: But those ratings are one load at a time. Real casing is pulled, squeezed and pressurised at once. So we check the von Mises equivalent stress against yield, with a design factor. Plotted as an ellipse of axial force against pressure, it answers a puzzle. Does pulling on a pipe make it easier or harder to crush? [pause 2] Easier. Steel already stretched along its length has less strength left to resist being squeezed, so the collapse rating is corrected for tension too.
SHOT: The VME ellipse centred on the origin of an axial-force vs differential-pressure plane, touching the tension and compression yield lines at zero pressure, bulging beyond the API burst line in the tension quadrant and falling inside the collapse line there. The uniaxial rectangle for comparison; a red dot that passes uniaxial but fails von Mises in the tension-collapse corner. A shrunken inner ellipse labelled "design factor". The puzzle question on screen during the pause, then the answer.
FLAGS: GEN; SIM: ellipse is the simplified VME yield envelope without bending or thermal load; collapse instability is checked separately (API/ISO collapse with tension correction); design factors are shown unlabelled as "operator-specific"
TERMS: von Mises equivalent stress; design factor

## 5.05 | 20 | anim
VO: Each load peaks in a different place. Tension, and often burst, are worst at the top, where tension also eats into collapse strength. Collapse is worst at the bottom. So long strings are often tapered: thicker wall, or stronger steel, only where it is needed.
SHOT: A depth vs load/capacity plot: burst load peaking near the top, tension largest at the top, collapse largest at the bottom; a single-weight capacity line fails at both ends, then morphs into steps (stronger at top and bottom, lighter in the middle) that sit above every load curve. A casing string beside it colour-coded by section.
FLAGS: GEN
TERMS: tapered string

## 5.06 | 30 | anim
VO: And then the connections, here meaning the threaded joints between pipes. Basic threaded couplings seal with thread compound. Premium connections add metal-to-metal seals and a torque shoulder, to stay gas-tight. They are qualified by testing to ISO thirteen six seven nine, and checked during make-up, as they are screwed together, on a torque-turn plot: torque against turns. The pipe body may be fine; connections are where most leaks start.
SHOT: Thread cross-section: API round thread with a spiral leak path filled by thread compound; then a premium connection with a conical metal-to-metal seal at the pin nose and a torque shoulder (separate labels with leader lines). A torque-vs-turns plot with a sharp shoulder-engagement kink and an acceptance window.
FLAGS: GEN; VERIFY: ISO 13679 as the connection-testing standard is from memory; "most leaks start at connections" is a generalisation
TERMS: premium connection; torque-turn plot

## 5.07 | 18.5 | anim
VO: In the barrier language of chapter seven, the casing that seals off the well becomes a well barrier element: one object that helps stop flow, accepted on a documented design and a pressure test. The conductor is structure, not barrier.
SHOT: The well schematic: the last-set casing and its cement light up in blue with a "tested" tick and the label "well barrier element"; the 30 in conductor stays grey, labelled "structural, not a barrier".
FLAGS: NO; VERIFY: element acceptance criteria wording in NORSOK D-010 for casing (design + test) not confirmed
PAUSE: 1
TERMS: well barrier element
