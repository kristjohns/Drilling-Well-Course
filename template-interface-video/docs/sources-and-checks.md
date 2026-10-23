# Sources and checks — the template interface

This note lists, for every statement in the video, where it comes from and how well it was checked. Three levels:

* **Read** — read in the document itself during this work (only NORSOK U-001:2026 was available as a file).
* **Secondary** — confirmed through published sources that quote or apply the clause (no access to the standard).
* **Not verified here** — from general knowledge of the standard; the document could not be opened in this session
  (paywalled, or the host was blocked by the session's network policy: `rules.dnv.com`, `standard.no` and most other
  standards sites). Check these against the editions in your design basis.

## 1. NORSOK U-001:2026 (read)

| Topic | Clause | What it says (as used in the video) |
| --- | --- | --- |
| Load share | 3.1.12 | "distribution of applied loads between the well (including conductor, casing and soil) and the template structure and its foundation"; notes: differs for vertical, horizontal and bending loads; vertical share governed by relative stiffness (Table 4); bending share by geometric constraints and relative stiffness |
| Yielding | 3.1.22 | failure mode when the elastic limit (0,2 % plastic strain) is exceeded (the wellhead side, Annex B) |
| Subsea structures | 5.2.2 | "Subsea structures shall be designed according to NORSOK N-001, and requirements in Clause 13." |
| Load share wellhead / template | 8.1 | load share to be determined for in-place riser loads and the components of Table 3; see Figure J.1 |
| Structural design of the template | 13.3.6.1 | "Structural design shall follow NS-EN ISO 13628-15:2011 clause 5.4 and NORSOK N-001." Load share always based on local conditions, with conservative assumptions |
| Conductor | 13.3.6.2 | conductor capacities to B.9; "A relative vertical displacement of 100 mm between the template and the conductor or wellhead, including thermal upward growth and template settlement, shall be accounted for in the template design unless otherwise specified." |
| Template | 13.3.6.4 | fully / partially supporting conductor methodologies, Table 4 indicative vertical load share factors (single caisson 50 %, template 1-slot 40 %, 2-slot 45 %, 4-slot 35 %, 6-slot 30 % / 20 %); final inclination ≤ 0,3 degrees unless the tolerance loops allow more |
| Foundation | 13.3.7 | load and material factors from NORSOK N-001; soil material factor 1,5 |
| Template loads | Annex A, Table A.2 | ULS and ALS load factors per NORSOK N-001; extreme riser loads 1,3 (case K), accidental riser loads 1,0 (case L); note d: relative displacement conductor–template is an SLS check with load factor 1,0, margins to the upper and lower end stops are checked, end stops reached → template preload forces → separate ULS load cases |
| Contacts and load paths | Annex J, Figure J.1 | contacts A–H; C = template structure / conductor housing, D = bottom of structure / conductor housing, G = guide structure to seabed; load path 3 = WH, conductor, guide base/structure to seabed; "The load sharing is dependent upon tolerances and relative stiffness of the different elements including soil properties." |
| Normative references | Clause 2 | NORSOK N-001 (undated), NORSOK N-004:2022 |
| Materials | (structural materials clause) | selection of structural materials for subsea use per NORSOK N-004:2022; design class guidance in N-004 Annex B |

U-001 itself contains no stress or strain acceptance criterion for the template steel: it hands the structural design
to ISO 13628-15 clause 5.4 and NORSOK N-001.

## 2. The chain N-001 → N-004 → Eurocode 3 (not verified here)

* NORSOK N-001 sends the design of steel structures to NORSOK N-004; N-004 builds on Eurocode 3 (NS-EN 1993) with
  offshore additions. This is how the NORSOK structural standards have been arranged for years; the 2022 edition of
  N-004 was not available for checking.
* Material factor for steel: **γM = 1.15 in ULS** (N-004) and **1.0 in ALS** (N-001 / N-004). Shown in chapter 2 and used
  as γM0 in the elastic check. N-004 rev. 3 (2013) also has a slenderness-dependent γM for tubular members (its
  section 6.3.7 is cited by software documentation found during the search). Confirm the values in N-004:2022.
* In ALS, N-004 Annex A (design against accidental actions) gives its own ductility limits for tension failure
  (a NORSOK N-006 extract found in the search refers to them). The video does not quote numbers from it.
* ISO 13628-15:2011 clause 5.4 was not read.

## 3. Eurocode 3 (secondary / not verified here)

| Statement | Source | Level |
| --- | --- | --- |
| EN 1993-1-5 Annex C, C.8(1): structures susceptible to buckling → attainment of the maximum load; regions subjected to tensile stresses → attainment of a limiting value of the principal membrane strain. NOTE 1: the National Annex may specify the limiting value; **a value of 5 % is recommended** | IDEA StatiCa support centre ("Why is 5 % plastic strain limit used…", citing Annex C, C.8, Note 1); Hilti PROFIS technical background (5 % default under the same clause, engineer to check national rules); Cyprus National Annex to EN 1993-1-5, NA 2.13 for C.8(1) (adopts the recommended 5 %); Dlubal knowledge base; a 2025 Alexandria Engineering Journal paper on design plastic strain limits ("Annex C of EN 1993-1-5 sets the design plastic strain limit at 5 %") | Secondary |
| C.8 NOTE 2: other criteria may be used, e.g. attainment of the yielding criterion or limitation of the yielding zone | general knowledge of EN 1993-1-5:2006 | Not verified here; the on-screen card says "wording abridged" |
| Annex C is informative | general knowledge | Not verified here |
| C.6 material models (a) without strain hardening, (b) with a nominal plateau slope, (c) with linear strain hardening, (d) true stress-strain curve from tests; characteristic values | general knowledge | Not verified here. The slopes of Figure C.2 are deliberately not quoted (IDEA StatiCa cites tan⁻¹(E/1000) for the plateau slope, memory said E/10 000) |
| C.7 single load multiplier α on the factored design loads | general knowledge | Not verified here |
| C.9: αu ≥ α1·α2; α1 model uncertainty from test calibrations (EN 1990 Annex D); α2 = γM1 if instability governs, γM2 if fracture governs | general knowledge | Not verified here |
| EN 1993-1-1 6.2.1(5): von Mises yield criterion at the critical point with fy/γM0 (formula 6.1) | general knowledge | Not verified here |
| EN 1993-1-1 3.2.1: fy = ReH and fu = Rm from the product standard | general knowledge | Not verified here |
| EN 10025-2: S355 nominal yield strength 355 / 345 / 335 MPa for t ≤ 16 / 16–40 / 40–63 mm; Rp0.2 when there is no distinct yield point | general knowledge | Not verified here |
| EN 1993-1-14:2025 "Design assisted by finite element analysis" exists (second generation), developed from Annex C of EN 1993-1-5 | CEN / national catalogue listings (ELOT, SIS, DIN 2025-10); Dunai et al., *Structures* (2026), "Structural steel design assisted by finite element analysis – an introduction to EN 1993-1-14 and TR 1993-1-141" | Secondary |

## 4. The 2 % (what was found, and what was not)

* **No 2 % strain criterion was found in EN 1993-1-5.** Annex C has one strain value, the recommended 5 % (NDP).
  U-001:2026 contains no 2 % strain limit either.
* Places where a 2 % appears in offshore practice, **none of them verified here and none of them in EN 1993-1-5**:
  * DNV-RP-C208 (non-linear FE capacity) has a "gross yielding" check in addition to local ductile fracture; a forum
    post found in the search describes gross yielding as plastic strain above 2 % over a zone longer than about 20
    plate thicknesses, and an LS-DYNA benchmark of the RP uses a critical gross-yield strain of 0.04 in an example.
    The RP itself (rules.dnv.com) was blocked in this session.
  * NORSOK N-004 Annex A / DNV-RP-C204 give critical strains for ALS that depend on the steel grade, the plate
    thickness and the length of the plastic zone.
  * DNV-ST-F101 (pipelines): supplementary requirement P for line pipe with an accumulated plastic strain above 2 %
    (from memory).
  * IDEA StatiCa shows a sensitivity study with plastic strain limits from 2 % to 8 % (the moment resistance changed
    by less than 4 %).
* If a 2 % limit is quoted for a project, ask for the document and clause, which strain it limits (membrane, surface,
  equivalent plastic) and with which material model and mesh.

## 5. The worked example (teaching model)

`model/ring_fe.py` and `model/interface_model.py`; results in `src/data/model.json`.

| Input | Value |
| --- | --- |
| Ring | lower slot ring D, annular plate cut from 40 mm S355 plate, inner radius 459 mm (36 in conductor + 1.8 mm), radial width 200 mm |
| Supports | four struts at 0°, 90°, 180°, 270°, pinned (radial and tangential restraint, free rotation) |
| Load | contact pressure of the conductor on the inner face, cosine distribution over ±20°, centred at 45° (between two struts) |
| Design contact force | 1.6 MN, ULS, load factor 1.3 included (assumed result of a load-share analysis) |
| Material | E 210 000 MPa, fy 345 MPa; (a) no hardening (nominal slope E/10 000 for the solver), (c) linear hardening E/100 |
| Analysis | 2D frame of 288 straight fibre beam elements (3 Gauss points, 40 fibres over the 200 mm depth), materially non-linear, geometrically linear, displacement control at the loaded node |

| Result | Value |
| --- | --- |
| Elastic stress at the critical point (outer edge behind the contact) | 260 MPa per MN → 416 MPa at 1.6 MN |
| Elastic check | 416 / (345/1.15 = 300) = 1.39 → fails |
| First yield | α = 0.83 (1.33 MN) |
| 0.2 % plastic strain at the edge | α = 1.25 |
| Model (a): plateau (mechanism) / 5 % / 2 % | 1.54 / 1.53 / 1.49 |
| Model (c): 5 % (αu) / 2 % | 1.76 / 1.59 |
| C.9 | αu = 1.76 ≥ α1·α2 = 1.0 × 1.3 (α1 assumed 1.0 for a benchmarked model, α2 taken no larger than 1.3) |
| Mesh study, model (a), strain at α = 1.50 | 1.41 % (5°), 1.98 % (2.5°), 2.27 % (1.25°), 2.40 % (0.625°); α at 5 %: 1.54 … 1.52 |
| Mesh study, model (c), strain at α = 1.50 | 0.98 %, 1.07 %, 1.09 %, 1.10 % (converged) |

Limitations: the ring is a beam model, not a shell model; struts are pins; the stocky ring is assumed not to buckle
(lateral-torsional buckling of a 40 × 200 mm ring between struts was only estimated by hand, slenderness ≈ 0.4);
contact, welds, the funnel and the template frame are not modelled; the strain shown is the fibre (hoop) strain,
which in a shell model of the plate ring would be the in-plane membrane strain.

## 6. Teaching choices

* The interface check is shown with ULS numbers; for ALS, NORSOK uses γM = 1.0 and N-004 Annex A ductility limits.
* "Utilisation 1.39" uses γM0 = 1.15 on fy; "first yield at 83 %" uses fy without the material factor.
* The 3D view shows model (c) only; the field is interpolated between the stored analysis steps.
