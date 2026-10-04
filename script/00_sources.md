# Sources & standards register (Stage 1)

## Read this first: what "verified" means here

The sandbox's egress policy **blocks `havtil.no`, `sodir.no` and `standard.no`** (the
regulator, the directorate and the NORSOK publisher), so **nothing below has been read
from a primary Norwegian source.** Every entry carries one of three tags:

| Tag | Meaning |
|---|---|
| `[seen]` | Title/number/claim appeared in a web-search result. Still *secondary* (a search summary, a vendor blog or a third-party report), not the document itself. |
| `[memory]` | From my training knowledge. Title/number believed right; edition, year and clause numbers **not** checked. |
| `[unsure]` | I am not confident this exists, is current, or says what I think. Do not rely on it. |

**Nothing in the Stage 2 script will cite a NORSOK clause number, table number, plug
length or test pressure unless it has been read from the document** (see "Access plan"
at the bottom). Until then those items are `[VERIFY]` in the outline.

Scope flag used throughout: **[NO]** = Norway/NCS-specific (regulation or NORSOK practice),
**[GEN]** = general industry practice.

---

## A. Norwegian regulation & NCS-specific material  **[NO]**

| # | Source | Feeds | Tag | Notes |
|---|---|---|---|---|
| A1 | **NORSOK D-010, *Well integrity in drilling and well operations*, Rev. 5 (2021)**, Standards Norway | All chapters; core for Ch 7 and Ch 9 | `[seen]` | Edition confirmed by several results; the *month* of publication is inconsistent across results (one says January 2021). Rev. 4 (2013) is the previous edition and is still widely quoted in older papers, so beware mixing them up. Rev. 5 restructured to ISO format and added new element-acceptance tables incl. perforate-wash-cement (PWC) (`[seen]`, via a vendor blog, treat as indicative). |
| A2 | **Activities Regulations (Aktivitetsforskriften), §85 *Well barriers*** + Guidelines, Havtil | Ch 7, 9 | `[seen]` | Result summary says: tested well barriers with sufficient independence; if a barrier fails, only activity to restore it may continue; Guidelines point to D-010 (chapters 5.2-5.4, 6.1-6.3, 9, Annex C) as the means of compliance. **Exact wording and which D-010 edition the Guidelines cite must be read.** |
| A3 | **Facilities Regulations (Innretningsforskriften), §48 *Well barriers*** + Guidelines | Ch 7 | `[seen]` | Appears to carry the "two well barriers where a pressure differential could cause uncontrolled outflow" wording. Which of A2/A3 says what needs checking. |
| A4 | Other Activities-Regulations sections: well control, relief-well planning, kick-tolerance/BOP testing, plugging & abandonment, notification/consent | Ch 3, 7, 9 | `[unsure]` | I know these topics are regulated but **do not know the section numbers**. Need to be located, not guessed. |
| A5 | **Resource Management Regulations (Ressursforskriften) + Guidelines**, Sodir | Ch 8 | `[seen]` (guidelines exist) | Discovery notification, data and sample submission. Details `[memory]`. |
| A6 | **Sodir well definitions & classification; resource classification system (report NPD-07-16 / Sodir "ressursklassifisering")** | Ch 8 | `[seen]` | Discovery = "petroleum deposit(s) discovered in the same wellbore for which testing, sampling or logging has established the probability of mobile petroleum" (covers technical *and* commercial discoveries). Wildcat = well drilled to prove whether petroleum exists. Both `[seen]`. |
| A7 | Havtil reports: *Technology and methods for permanent plugging on the NCS* (2021); *PWC qualification* paper; *Temporary plugged and abandoned wells on the NCS* (2022) | Ch 9 | `[seen]` | One result states exploration wells begun after 1 Jan 2014 may not be temporarily abandoned >2 years. `[seen]`, from a secondary summary, so verify against the report. |
| A8 | NORSOK D-001 *Drilling facilities* | Ch 3, 7 | `[unsure]` | Probably where BOP/well-control *equipment* requirements live; edition/clauses unknown. |
| A9 | Miljødirektoratet (environment agency) permit requirements for flaring/emissions during well testing; CO2 tax | Ch 8 (DST) | `[seen]` (World Bank flaring summary: flaring prohibited except brief testing/safety, authority approval) | Details of the permit process `[memory]`. |
| A10 | Fiskeridirektoratet (fisheries) expectations for seabed clearance after P&A | Ch 9 | `[unsure]` | Plausible, not verified. |
| A11 | Equinor internal technical requirements (TR/WR series) | all | n/a | Operator-internal; not public and I will not cite numbers. You have access; use them as a second-pass check on the final script. |
| A12 | Name changes: PSA → **Havtil** (2024); NPD → **Sodir / Norwegian Offshore Directorate** (2022) | narration | `[seen]` (site names) / `[memory]` (dates) | Script will use current names and mention the old ones once. |

## B. International standards  **[GEN]**  (editions to be pinned in Stage 2)

| # | Standard | Feeds | Tag |
|---|---|---|---|
| B1 | **ISO 16530-1** *Well integrity – Part 1: Life cycle governance* | Ch 7, 9 | `[memory]` |
| B2 | **API Spec 5CT / ISO 11960** *Casing and tubing* | Ch 5 | `[memory]` |
| B3 | **API TR 5C3 / ISO 10400** *Formulae & calculations for casing, tubing, drill pipe, line pipe properties* (burst, collapse, tension, triaxial/VME) | Ch 5 | `[memory]` (ISO/TR 10400 was upgraded to a full ISO 10400 around 2018, `[unsure]` on exact year) |
| B4 | **ISO 13679 / API RP 5C5** *Testing casing and tubing connections* (connection application levels) | Ch 5 | `[memory]` |
| B5 | **API RP 5A3 / ISO 13678** *Thread compounds* | Ch 5 | `[memory]` |
| B6 | **API Spec 10A / ISO 10426-1** *Cements*; **API RP 10B-2 / ISO 10426-2** *Testing well cements* | Ch 6 | `[memory]` |
| B7 | **API RP 10D-2 / ISO 10427-2** *Centralizer placement & stop-collar testing* | Ch 6 | `[memory]` |
| B8 | **API RP 65-2** *Isolating potential flow zones during well construction* | Ch 2, 6 | `[memory]` |
| B9 | **API Std 53** *Well control equipment systems for drilling wells* | Ch 3, 7 | `[memory]` |
| B10 | **API Spec 16A / ISO 13533** *Drill-through equipment*; **API Spec 16D** *Control systems* | Ch 3 | `[memory]` |
| B11 | **API RP 16Q / ISO 13624-1** *Marine drilling riser systems* | Ch 3 | `[memory]` |
| B12 | **API Spec 6A / ISO 10423**; **API Spec 17D / ISO 13628-4** *Wellhead & subsea wellhead/tree equipment* | Ch 2 | `[memory]` |
| B13 | **API RP 59** *Well control operations*; **API RP 64** *Diverter systems* | Ch 2, 7 | `[memory]` |
| B14 | **API RP 7G / ISO 10407** *Drill stem design*; **API RP 13B-1/-2 (ISO 10414)** *Field testing of drilling fluids*; **API RP 13D** *Rheology & hydraulics* | Ch 4 | `[memory]` |
| B15 | **ISO 15156 (NACE MR0175)** *Materials for H2S-containing environments* | Ch 5 | `[memory]` |
| B16 | IADC *Well Control guidelines*; IADC MPD/UBO definitions; IWCF/IADC WellCAP syllabi (industry competence standards) | Ch 4, 7 | `[memory]` |
| B17 | OEUK (ex-Oil & Gas UK) *Guidelines for the suspension and abandonment of wells* (UK counterpart to D-010 ch. 9; useful "general practice" contrast) | Ch 9 | `[memory]`, issue number `[unsure]` |
| B18 | ISCWSA wellbore-survey error model (Williamson, SPE 67616) | Ch 4 | `[memory]` |
| B19 | SPE-PRMS (resource classification) | Ch 8 | `[memory]` |
| B20 | API RP 40 *Core analysis*; API RP 44 *Sampling reservoir fluids* | Ch 8 | `[memory]` |

## C. Textbooks & papers (for the physics and the analogies)

| # | Reference | Feeds |
|---|---|---|
| C1 | Bourgoyne, Millheim, Chenevert, Young, *Applied Drilling Engineering* (SPE Textbook Vol. 2, 1986) | Ch 1, 4, 7 |
| C2 | Mitchell & Miska, *Fundamentals of Drilling Engineering* (SPE Textbook Vol. 12, 2011) | Ch 1, 4, 5 |
| C3 | **Aadnøy, *Modern Well Design*** (2nd ed., 2010) and Aadnøy & Looyeh, *Petroleum Rock Mechanics*: Norwegian author, UiS; good on casing design from the bottom up and fracture/collapse | Ch 1, 5 |
| C4 | Nelson & Guillot, *Well Cementing* (2nd ed., Schlumberger, 2006) | Ch 6, 9 |
| C5 | Grace, *Blowout and Well Control Handbook* | Ch 7 |
| C6 | Fjær et al., *Petroleum Related Rock Mechanics*; Zoback, *Reservoir Geomechanics* | Ch 1 |
| C7 | Eaton (1969), "Fracture gradient prediction and its application in oilfield operations" (JPT); Terzaghi, *Theoretical Soil Mechanics* (1943), for the consolidation (piston-and-spring) analogy and effective stress | Ch 1 |
| C8 | Asquith & Krygowski, *Basic Well Log Analysis* (AAPG); Bateman, *Openhole Log Analysis and Formation Evaluation*; Dake, *Fundamentals of Reservoir Engineering* (for pressure gradients/contacts) | Ch 8 |
| C9 | Hydrawell/SPE paper "Perforate, Wash, and Cement: A Review of Practices and Where to Go Next" (SPE 226204-PA) | Ch 9 | 
| | *(C9 is `[seen]`. Authors are connected to a PWC vendor, so read as practice review, not neutral evidence.)* | |

All of C1–C8 are `[memory]` for title/edition.

## D. Incident / case material (candidates for stories, not yet chosen)

| # | Case | Possible use | Tag |
|---|---|---|---|
| D1 | **Macondo / Deepwater Horizon (2010)**: cement job, negative-test interpretation, BOP failure to seal. Sources: BOEMRE/USCG Joint Investigation (2011), National Commission report (2011), US CSB (2016) | Ch 6 (cement), 7 (barriers & verification) | `[memory]` |
| D2 | **Snorre A gas blowout (2004)**, PSA investigation report | Ch 2/7 | `[memory]`, details `[unsure]` (do not narrate until the report is read) |
| D3 | **Gullfaks C well-control incident (2010)**, PSA investigation | Ch 7 | `[memory]`, details `[unsure]` |
| D4 | **Ekofisk Bravo blowout (1977)**, historical origin of the barrier philosophy | Ch 7 | `[memory]`, details `[unsure]` |
| D5 | A shallow-gas blowout on the NCS (a well in the Ekofisk area, late 1980s, rings a bell) | Ch 2 | `[unsure]` (do **not** use unless confirmed) |

## E. Access plan (how to turn `[seen]`/`[memory]` into verified)

Pick one (or both):

1. **Unblock hosts** in the environment's Network access settings (Custom → Allowed domains):
   `www.havtil.no`, `www.sodir.no`, `standard.no`, `factpages.sodir.no`. Cloud-environment docs:
   <https://code.claude.com/docs/en/cloud-environments#network-access>.
2. **Drop PDFs in `sources/`** (git-ignored, because the standards are copyrighted): NORSOK D-010 Rev 5,
   the Activities/Facilities Regulations + Guidelines (English), and any API/ISO excerpts you can legally share.

With either, Stage 2 will cite page/clause/table numbers, and every `[VERIFY]` in the outline will be
resolved or kept visibly open.
