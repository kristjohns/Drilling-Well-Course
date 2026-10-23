# Sources and checks

What the video states, where it comes from, and what a reviewer should confirm. "U-001" is NORSOK U-001:2026
(published 2026-09-21). Clause, table and formula numbers are those of that edition; page numbers are the printed ones.

## The answer in one paragraph

U-001 Annex B (normative) does not use the peak von Mises stress, and does not use a strain limit, as the general
acceptance criterion. The design format is formula (B.2), *load or load effect ≤ F_d × static capacity*, with F_d from
Table B.3 (normal 0.67, extreme 0.80, accidental 0.90/1.00, pressure-only 0.60, FAT and make-break 0.90, functional 1.00).
The yield strength σ_y (B.5, at 0.2 % plastic strain) anchors the capacity: in an elastic analysis through linearised
stress categories against Table B.7 (preliminary design only, D/t > 10 for pressure-containing parts), in an
elastic-plastic analysis through the material curve that produces the limit load or the factored plastic collapse load
(B.3.6.3.2). Strain becomes the criterion only for studs/segments/locking segments in bending (0.2 % equivalent plastic
strain through the root cross section) and for local failure (ASME VIII-3 KD-232 accumulated strain limit), the latter
waived for carbon and low-alloy steels that meet the ductility requirements of B.3.6.3.3.

## Statements taken from NORSOK U-001:2026

| On screen / in the narration | Source | Checked against the text |
| --- | --- | --- |
| Yielding: failure mode when the elastic limit (0.2 % plastic strain) is exceeded; by elastic analysis, limit load or factored plastic collapse | 3.1.22 | yes |
| Yield strength: stress at a specified deviation from proportionality, offset 0.20 % (or total extension under load, usually 0.50 %) | 3.1.23 | yes |
| Local failure: initiation of a ductile crack at a point of elevated triaxial stress, by microvoid nucleation, growth and coalescence | 3.2.27 | yes |
| Plastic collapse, plastic collapse load, yielding capacity (through-section yielding of preloaded parts in bending, note 2) | 3.2.32, 3.2.33, 3.2.54 | yes |
| Limit load = yielding capacity without strain hardening; limit-load method = elastic-perfectly plastic | 3.3.14, 3.3.15 | yes |
| Annex B scope: pressure-containing and primary structural components in the riser load path; housings, extensions, connectors, tree, C/WO riser equipment | B.1, Table B.1 | yes |
| Failure modes: structural (brittle fracture, yielding, local failure, buckling, mechanical disengagement), functional, environmental | Table B.2 | yes |
| Brittle fracture and EAC prevented by material requirements (B.10); local failure prevented by ductility requirements | B.2.2.2, B.2.2.4, B.2.2.5, note c to Table B.2 | yes |
| (B.2) load ≤ F_d × static capacity; Table B.3 factors; F_d only applies to yielding | B.2.5.1, Table B.3, note a to Tables B.5 and B.6 | yes |
| Accidental F_d 1.00 above / 0.90 below and including barrier elements; F_d 1.0 requires retrieval for inspection (note e) | Table B.3 | yes; applying 0.90 to a wellhead housing (permanent, below the BOP) is an interpretation, see below |
| σ_y = min(Y_y·SMYS; 0.90·Y_u·SMTS), σ_u = Y_u·SMTS; de-rate above 40 °C | B.2.7.4, (B.5), (B.6) | yes |
| Static load capacity = minimum of structural and functional capacities | B.3.1, B.3.6.1 | yes |
| Capacity methods: formulas (pipes B.9, spheres, flanges Annex C), elastic FEA, elastic-plastic FEA; elastic analysis limited to preliminary design and not for functional capacities | B.3.3 | yes |
| Mesh refinement where local failure modes are evaluated; 3D analysis for non-axisymmetric geometry or load | B.3.4 | yes |
| Elastic: von Mises or Tresca; large deformations; D/t > 10 for pressure-containing components; ASME VIII-2 Annex 5-A (or VIII-3 App. 9) linearisation; preloaded equipment: P + Q taken as primary if not separable | B.3.5.1 | yes |
| Table B.7: P_m, P_L ≤ σ_y; P_m/L + P_b ≤ 1.5 σ_y; P + Q range ≤ 2.0 σ_y; shear ≤ 0.57 σ_y; bearing ≤ σ_y | B.3.5.2, Table B.7 | yes |
| Elastic triaxial check σ1 + σ2 + σ3 ≤ 2.5 SMYS, waived for steels meeting B.3.6.3.3 | B.3.5.3 | yes |
| Ratcheting not checked up to and including 180 °C (KD-234) | B.3.5.4, B.3.6.3.4 | yes |
| Elastic-plastic: limit load (true curve cut off at yield, KM-620 up to yield, ≤ 5 % rise at 20 % plastic strain allowed) or factored plastic collapse (true curve cut off at true ultimate, KM-620 if no test curve); yield at 0.2 % plastic strain | B.3.6.2 | yes |
| FE requirements: von Mises with associated flow, large deformations, large strains, hardening (isotropic for static, kinematic for reversed yielding) | B.3.6.2 a)–d), notes 2 and 3 | yes |
| Limit load = load at structural instability, indicated by non-convergence; plot load against displacement/rotation | B.3.6.3.2.2 | yes |
| Plastic collapse load / MAX[1.2; σ_u/σ_y]; note 1 (typically 10 % to 20 % above the limit load); note 2 (ASME VIII-3 1.8, ISO 13628-7 1.5 → 1.2) | B.3.6.3.2.3 | yes |
| Studs in a flange, segments in clamps, connector locking segments in bending: yielding capacity at 0.2 % equivalent plastic strain through the cross section | B.3.6.3.2.2, B.3.6.3.2.3, Figure B.7 | yes |
| Limit load method for connectors requires a full-scale test load ≥ 1.2 × the actual limit load | B.3.6.3.2.1 | yes |
| Local failure: total accumulated local strain damage per ASME VIII-3 KD-232 over preload, hydrostatic test and the yielding capacity; KD-230.4 load factor modified to 1.0; true curve cut off at true tensile strength | B.3.6.3.3 | yes |
| Exemption: C/LAS with elongation ≥ 17 % / 16 % and RA ≥ 35 % / 45 % (SMYS ≤ 655 / 655–830 MPa); low-alloy studs and nuts to D.7.2 | B.3.6.3.3, B.10.2.1 | yes |
| Mechanical disengagement capacity = load at disengagement / 1.1; buckling capacity = maximum load / 1.10 | B.3.6.3.5, B.3.6.3.6 | yes |
| Functional criteria from the manufacturer, validated by testing | B.3.6.4.3–B.3.6.4.6 | yes |
| Figure B.6 levels (plastic collapse, limit load, mechanical disengagement, seal leak tightness, preload exceedance, preload exceedance after loading to 80 %) | Figure B.6 | yes (redrawn schematically) |
| Load sequence; Table B.8 load case 1 (bending to instability, pressure and tension zero); nonlinear capacities with loads divided by F_d (Table B.9) | B.3.6.5, Tables B.8, B.9 | yes |
| (B.7) (T_w/T_c + |M|/M_c)·(1/F_d) ≤ 1.0 with T_w = T_e + π/4·D_s²·(p_i − p_e); RWP as internal design pressure; capacities at the wellhead datum | B.3.6.6.1, B.3.6.6.2 | yes |
| Static capacities of connectors from FEA validated by full-scale testing | B.2.3 b), B.7.6 | yes |
| Conductor capacities per B.9; B.9.3 (limit load, seamless/forged per B.10) vs B.9.5 (initial yield, wellhead conductors and surface casing, API 5L/5CT pipe) | 13.3.6.2, B.9.1, B.9.3, B.9.5 | yes |
| Template structural design to ISO 13628-15 and NORSOK N-001 | 13.3.6.1 | yes |
| Table A.4 ULS/ALS loads (BOP on WH) and the shear increase below the datum; ULS → extreme, ALS → accidental | A.3.3, A.3.4, Table A.4 | yes |

## Statements taken from the ASME code (referenced by U-001, not reproduced in it)

| Item | Used as | What to check |
| --- | --- | --- |
| Linearisation σ_m = (1/t)∫σ dx, σ_b = (6/t²)∫σ(t/2 − x) dx along an SCL | ASME BPVC VIII-2 Annex 5-A (3D formulas) | the edition in the design basis; axisymmetric SCLs have extra terms |
| Net-section bending of a shell across the full section is primary membrane | ASME VIII-2 Table 5.6 (classification examples) | classification of discontinuity bending (Q or P_b) is project practice; the video treats the linearised bending as P_b |
| True stress-strain model (ε_p = 2·10⁻⁵, m₂ = 0.60(1 − R), ε_ys = 0.002, tanh blend) | ASME VIII-2 Annex 3-D / VIII-3 KM-620 | the model and constants of the 2025 edition |
| ε_L = ε_Lu·exp[−α_sl/(1 + m₂)·(T − 1/3)], damage Σ Δε_peq/ε_L ≤ 1; α_sl = 2.2 for ferritic steel | ASME VIII-2 5.3.3 / VIII-3 KD-232 | the coefficients of Table KM-620 in the edition used; the video only shows the ratio ε_L/ε_Lu |

## Teaching choices (illustrative, not project data)

| Item | Value | Why / what to check |
| --- | --- | --- |
| Material | API 75K forging: SMYS 517 MPa, SMTS 655 MPa, E = 207 GPa, min. elongation 17 %, RA 35 % | Metal temperature below 40 °C (drilling phase), so Y_y = Y_u = 1.0 |
| Critical section | HP housing neck just below the connector hub, OD 0.700 m, bore 0.476 m (t = 112 mm, D/t = 6.25), 0.6 m below the datum | All datum load passes through it (above contact A); the 3D model's housing was given this neck |
| Loads | Table A.4, 250–500 m, BOP on WH: ULS 7 354 kNm / 537 kN / −1 472 kN; ALS 12 217 kNm / 892 kN / 3 424 kN | Section moment M = M_w + Q_w·0.6 m |
| Pressure end load | p_i = 69 MPa (690 bar), D_s = 0.50 m, p_e = 0 | D_s is illustrative; ignoring p_e is conservative for the load (B.2.7.1 does not allow credit from external pressure for wellhead equipment) |
| Design factors | ULS → extreme 0.80; ALS → accidental 0.90 | 0.90 because the wellhead is a permanent barrier element that is not retrieved for inspection (note e of Table B.3) |
| Elastic stress field | beam stresses (T_w/A + M·r/I), Lamé hoop and radial stresses, fillet peak K_t = 1.5 decaying over 12 mm | A stand-in for an FE result, labelled on screen; the 3D contour uses the same expressions with visual load tapers in the hub and below the landing ring |
| Elastic-plastic response | section (fibre) model of the neck; limit load with the KM-620 curve cut off at σ_y; collapse with the curve cut off at the true ultimate and geometric softening represented by the engineering stress (force per original area) | A stand-in for the 3D FE analysis of B.3.4, labelled on screen; it gives collapse/limit = 1.25 (U-001 note 1: typically 1.1–1.2) |
| Rotation | curvature × 1 m of neck | Only for plotting |
| 3D plastic strain view | ε_p = κ(y)·|x| − σ_y/E, κ of the neck from the section model, κ elsewhere from a bilinear tube law | Visual |
| Local failure curve | α_sl = 2.2, m₂ = 0.126, shown as ε_L/ε_Lu | Illustrates the trend only; the 75K example is exempt |

## Numbers in the worked example

Produced by `python3 model/acceptance_model.py` (`src/data/model.json`).

| Quantity | Value |
| --- | --- |
| σ_y, σ_u, σ_u/σ_y | 517 MPa, 655 MPa, 1.267 (so MAX[1.2; σ_u/σ_y] = 1.267) |
| True curve | true ultimate 743 MPa at 13.0 % true strain; σ_y reached at 0.45 % total strain; uniform elongation 13.9 % |
| Neck section | A = 0.2069 m², I = 0.009266 m⁴, Z = 0.02647 m³, Z_p = 0.03919 m³, shape factor 1.48 |
| M at the neck | ULS 7.68 MNm, ALS 12.75 MNm |
| End load, T_w | 13.55 MN; T_w ULS 12.08 MN, ALS 16.97 MN |
| Elastic route, ALS (SCL at the fillet root, outside surface) | membrane 482 MPa ≤ 0.9 × 517 = 465 → 1.04 (fails); membrane + bending 613 ≤ 698 → 0.88; total 793 MPa; peak 180 MPa; σ1+σ2+σ3 = 964 ≤ 1 293 MPa |
| Elastic route, ULS | membrane 302 ≤ 414 → 0.73; membrane + bending 364 ≤ 620 → 0.59 |
| First yield / plastic moment | M_y = 13.69 MNm, M_p = 20.26 MNm |
| Limit load (bending) | 20.26 MNm; the outside surface reaches 0.2 % plastic strain at 18.05 MNm (0.89 M_p) |
| Plastic collapse (bending) | 25.22 MNm at 440 mrad; factored 25.22 / 1.267 = 19.91 MNm (1.8 % below the limit load) |
| Tension capacity | T_c = σ_y·A = 107.0 MN (factored collapse σ_u·A / 1.267 gives the same) |
| (B.7), limit load capacities | ALS (16.97/107.0 + 12.75/20.26)/0.9 = 0.876; ULS (12.08/107.0 + 7.68/20.26)/0.8 = 0.615 |
| (B.7), factored collapse capacities | ALS 0.888; ULS 0.623 |
| Exact plastic interaction (section model) at T_w = 17.1 MN | M = 19.6 MNm (B.7's straight line is conservative) |
| Local strain limit at T = 1.2 | ε_L/ε_Lu = 0.18 |

## Remarks on the text of U-001:2026

* B.3.6.2 note 4 reads "The maximum load (plastic collapse) or overall structural capacity will typically be 0 % higher
  than the yielding capacity …". A number appears to be missing; B.3.6.3.2.3 note 1 gives "10 % to 20 %". The video
  quotes note 1 only.
* B.3.6.5.3 example 3 lists pressures "0 MPa, 34,5 MPa, 690 MPa"; 69 MPa is evidently meant (Table B.9 uses 69).
* Formula (B.7) is linear in T_w and M; U-001 notes that it does not hold for all connectors (pressure and axial load can
  change the bending capacity) and asks for nonlinear capacity charts in that case (B.3.6.6.3).
