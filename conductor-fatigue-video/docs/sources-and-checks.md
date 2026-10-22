# Sources and checks

What the video states, where it comes from, and what a reviewer should confirm. "U-001" is NORSOK U-001:2026
(edition 4). Clause, table and formula numbers are those of that edition.

## Statements taken from NORSOK U-001:2026

| On screen / in the narration | Source | Checked against the text |
| --- | --- | --- |
| Conductor: "tubulars installed and cemented in a well construction, providing support for, and load sharing with the surface casing" | 3.1.7 | yes |
| Fatigue definition; fatigue failure at Miner's sum 1.0 | 3.2.19, 3.2.21 | yes |
| S-N curve defined at mean minus two standard deviations, 2.3 % below the curve, 97.7 % probability of survival | 3.2.43 note 1 | yes (the standard adds "with at least 75 % confidence") |
| Riser loads of Annex A act on the wellhead system; the WH / template load share shall be determined | 8.1 | yes |
| Load share shall satisfy fatigue for the wellhead system and the template at the same time | 8.1 | yes |
| Conductor girth welds (conductor housing to extension) shall meet S-N class C1 | 13.3.6.2 | yes |
| Template designed for a relative vertical displacement of 100 mm between template and conductor or wellhead, including thermal growth and settlement | 13.3.6 | yes |
| Indicative structure vertical load share factors, 50 % (single caisson, 1 slot) down to 20 % (centre slot, 6 slots) | Table 4 (informative, "shall be confirmed during detail design") | yes |
| Fatigue loads as an annual single-load bending moment range ΔM₀ and a general bending moment histogram | A.3.5.1 | yes |
| ΔM₀ at the WH datum: 80–250 m 2 124 / 2 466 kNm, 250–500 m 1 436 / 1 766 kNm, 500–1 500 m 1 194 / 1 452 kNm (BOP on WH / BOP on XT) | Table A.7 | yes |
| Normalised histogram, 0.1 … 2.9, 7 472 771 cycles per year; Example 1: 0.1 × 2 124 = 212.4 kNm at 3 948 892 cycles | Table A.8, A.3.5.1 example 1 | yes |
| Minimum calculated fatigue service life 1 year (template, wellhead system) | A.3.5.2, A.3.5.3 | yes |
| H_LFJ ≤ 13.7 m, H_XT ≤ 2.5 m for the standard design case | Table A.3 | yes |
| Service life ≤ fatigue life / D_F (B.3); inspection interval ≤ fatigue life / D_F (B.4); D_F = 10 permanent, 3 temporary, 10 for inspection intervals | B.2.6, Table B.4 | yes |
| Nonlinear relation between load and stress for connectors and wellheads: use FE analysis | B.4.1 | yes |
| Local response procedure a) to f), fully reversed loading, six load levels 6 000, 3 000, 1 500, 750, 375 and 187.5 kNm | B.4.2.4 | yes |
| Bilinear M-N curve (B.10), knee (B.11), lower bound over the hot spots, fatigue life reduction factor RF from DNV-RP-C203:2024 section 5.7, ΔM_c at 10⁶ cycles | B.4.4, Tables B.11, B.12 | yes |
| "Linear and bi-linear M-N curves shall include a fatigue life reduction factor (RF) in accordance with DNV-RP-C203:2024 Section 5.7" (quoted in 7.9) | B.4.4 | yes |
| Table B.4 layout: permanent equipment service life 10 (footnote a: inspection of permanent equipment assumed not performed); temporary equipment service life 3 and inspection interval 10 | Table B.4 | yes |
| (B.12) ΔM₀ from ā, (B.13) ā from (n, ΔM_eq), (B.14) ΔM_eq | B.4.4 | yes |
| Four to six fatigue hot spots with the lowest capacity are typically sufficient | Table B.11 note a | yes |
| Contact areas A–H and three load paths | Figure J.1, J.2.1 | yes |
| Load sharing depends on tolerances and relative stiffness, including soil properties | J.2.1 | yes |
| Conductor installation (driven, drilled and driven, drilled and cemented) and the soil interface | J.2.2 | yes |
| Operational levers (overpull, flex joint, riser tally, drill pipe tension, beam seas), monitoring | Table J.1, J.4.3 | yes |
| References: DNV-RP-C203:2024 (S-N curves), NORSOK N-001 (template DFF), DNV-RP-E104 (wellhead fatigue analysis) | Bibliography | yes |

## Statements that are teaching choices, not requirements

| Item | Value in the video | Why / what to check |
| --- | --- | --- |
| S-N constants | DNV-RP-C203:2016, C1 and D in seawater with CP (log ā 12.049 / 16.081 and 11.764 / 15.606, knee at 10⁶) | U-001:2026 refers to the 2024 edition, which revised the seawater curves. Said on screen. |
| Thickness effect | t_ref = 25 mm, k = 0.15, t = 50.8 mm → factor 1.11 | Check the exponent for the detail class in the edition used. |
| RF | 1.0 | B.4.4 requires RF from DNV-RP-C203:2024 §5.7. |
| Local response model | two beam strings with Winkler springs and gap contacts (`model/fatigue_model.py`) | A teaching stand-in for the 3D FE model of B.4.2.4, said on screen. |
| Soil | Winkler k = 2–20 MPa, base 5 MPa | Real p-y curves are nonlinear and degrade under cycling (shown as illustrative curves in 5.5). |
| Template rings | k_C = 200 MN/m, k_D = 400 MN/m, 2 m apart, 2 mm radial gap | Illustrative. |
| SCFs | GW1 1.10 (misalignment), TS1 2.0 | Illustrative. |
| TS1 stress per ring force | 0.156 MPa/kN from a fixed-fixed beam model (F L / 16 / W × SCF) | Illustrative geometry. |
| Template DFF | 10 (no access for inspection, substantial consequences) | Check the classification and the N-001 edition. |
| Example well | 350 m, BOP on WH, 36 × 2 in conductor, 20 × 1 in casing, 5 m cement shortfall | Illustrative; not project data. |

## Numbers in the worked example

Produced by `python3 model/fatigue_model.py`. The model checks its finite-element beam against the closed-form
beam-on-elastic-foundation solution (largest relative error 7 × 10⁻⁵, stored as `validation` in `src/data/model.json`);
the M-N intercepts are the minimum over the local-model points, so no point lies below its curve.

| Quantity | Value |
| --- | --- |
| ΔM_eq (m = 3), n = 7 472 771 | 683 kNm |
| ΔM₀ back-calculated from the histogram (m = 3) | 1 335 kNm (Table A.7: 1 436 kNm) |
| GW1 M-N curve | log ā₁ = 16.33 (m = 3), log ā₂ = 22.75 (m = 5), knee 1 617 kNm, ΔM_c = 2 780 kNm |
| TS1 M-N curve | log ā₁ = 16.25, log ā₂ = 23.26, knee 3 229 kNm, ΔM_c = 2 838 kNm |
| GW1 screening | 2 780 / 10^{1/3} = 1 290 < 1 436 → fails (single slope life 7.3 years) |
| GW1 full sum | D = 0.0712 per year, fatigue life 14.0 years, service life 1.40 years ≈ 513 days |
| GW1 single slope full sum | 9.0 years |
| TS1 full sum | D = 0.0280 per year, 35.7 years, service life 3.57 years |
| Gap 0 / 1 / 2 / 4 mm | GW1 7.3 / 2.0 / 1.4 / 1.26 years; TS1 0.39 / 2.7 / 3.6 / 6.8 years (service life) |
| Gap 8 mm (not shown) | TS1 repeats the 4 mm life: the lower-bound fit on the slope-5 branch is set by the largest stress per moment, which in a linear model with a gap depends on M / g, and the load levels halve while the gap doubles |
| No template contact | GW1 0.98 years |
| SCF 1.0 / 1.2 | GW1 2.10 / 0.99 years |
| Water depth 80–250 m / 500–1 500 m | GW1 0.33 / 3.07 years |
| BOP on XT, 250–500 m | GW1 0.63 years |
| 40 % lateral load relief, 80–250 m | GW1 2.31 years, TS1 6.48 years |
