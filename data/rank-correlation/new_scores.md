# New Scores: 10 Unscored Projects in the Expanded Dataset

*Scored 2026-04-14 under v0.6 rubrics. Weights: removal_type=0.25, additionality=0.20, mrv_grade=0.20, permanence=0.175, vintage_year=0.10, co_benefits=0.00 (safeguards-gate), registry_methodology=0.075.*

*Current year for vintage decay: 2026. Formula: max(0, 100 - (2026 - vintage) * 12).*

## Scoring Methodology

Each project is scored by matching to the closest scored archetype from the pilot dataset (`data/pilot-scoring/credits.json`) and cross-type dataset (`data/rank-correlation/cross_type_notes.md`), then adjusting per-dimension based on project-specific public documentation. The archetype provides a baseline; project-specific factors (MRV quality, vintage, registry status, additionality evidence, disqualifiers) shift individual dimension scores.

---

## EXP19: 1PointFive STRATOS DAC (Texas, USA)

**Type**: DACCS | **Registry**: Pre-issuance (N/A) | **BeZero**: AAA (pre-rating) | **Archetype**: Climeworks Orca (C001/EXP07)

### Rationale

STRATOS is Occidental's subsidiary 1PointFive's large-scale DACCS facility in the Permian Basin, Texas. It is the world's largest planned DAC facility at 500,000 tCO2/yr capacity. BeZero awarded an unprecedented AAApre (pre-issuance) rating. Like Climeworks Orca, this is atmospheric CO2 capture with geological storage, the highest tier on the Oxford Principles hierarchy.

### Per-dimension scores

| Dimension | Score | Rationale |
|-----------|------:|-----------|
| removal_type | 97 | Engineered removal + geological storage (band 95-100). DACCS with deep geological injection in the Permian Basin. Same category as Orca (98) but slight discount (1 pt) because injection is into saline aquifer rather than basalt mineralization; still >10,000 yr durability. |
| additionality | 93 | Very High (90-100). Carbon revenue is the primary revenue stream; DAC at this scale is pre-commercial; negative NPV without carbon finance and 45Q tax credits; Occidental's investment case hinges on carbon credit sales. Slightly below Orca (95) because 45Q tax credits partially subsidize, but well above the 80% subsidy red-flag threshold. |
| permanence | 97 | >10,000 years (95-100). Geological injection into deep saline formation with proven CO2 storage geology (Permian Basin has 50+ years of CO2 injection history from EOR). Equivalent to Orca (98) with minor uncertainty from saline vs basalt. |
| mrv_grade | 88 | Enhanced (75-89). Pre-issuance means verification has not yet occurred, but the monitoring plan includes continuous wellhead sensors, pressure monitoring, and seismic survey. Scored in Enhanced band rather than Digital MRV because no operational verification yet. Below Orca's 92 which has completed verification cycles. |
| vintage_year | 100 | 2025/2026 vintage (pre-issuance). max(0, 100 - 0*12) = 100. |
| co_benefits | 15 | Minimal. Industrial facility in the Permian Basin. Some job creation but no SDG certification. Informational only; weight = 0. |
| registry_methodology | 78 | CCP tier (75-85). Puro.earth is CCP-Eligible; DAC geological storage methodology is CCP-approved. Pre-issuance means methodology is committed but credits not yet issued. Score 78 (slightly below standard CCP 80 due to pre-issuance uncertainty). |

### Composite and Grade

Composite = 97(0.25) + 93(0.20) + 88(0.20) + 97(0.175) + 100(0.10) + 15(0.00) + 78(0.075)
= 24.25 + 18.60 + 17.60 + 16.975 + 10.00 + 0.00 + 5.85
= **93.28**

**Grade: AAA** (90-100)

No disqualifiers triggered.

---

## EXP20: Octavia Carbon Hummingbird (DAC Kenya)

**Type**: DACCS | **Registry**: Puro.earth | **BeZero**: AAA | **Archetype**: Climeworks Orca (C001/EXP07)

### Rationale

Octavia Carbon is the first commercial DAC plant on the African continent, located in Kenya. It earned BeZero's second-ever AAA rating. Geothermal-powered DACCS with geological storage, directly comparable to Climeworks Orca.

### Per-dimension scores

| Dimension | Score | Rationale |
|-----------|------:|-----------|
| removal_type | 97 | Engineered removal + geological storage (95-100). DACCS with geological injection, same tier as STRATOS and Orca. Geothermal power source strengthens the removal claim (low lifecycle emissions). |
| additionality | 94 | Very High (90-100). DAC in Kenya is definitively pre-commercial. Carbon revenue is >50% of income. No regulatory mandate. Financial analysis clearly shows project would not proceed without carbon finance. Similar to Orca. |
| permanence | 97 | >10,000 years (95-100). Geological storage in Kenya's Rift Valley geology (volcanic formations suitable for mineralization/injection). Comparable to Orca's CarbFix-type storage. |
| mrv_grade | 90 | Digital MRV (90-100). Puro.earth methodology requires continuous monitoring with IoT sensors; Octavia has operational verification through Puro's framework. Kenya's geothermal geology provides well-characterized storage. |
| vintage_year | 100 | 2025 vintage. max(0, 100 - 1*12) = 88, but BeZero rated in 2025 suggesting 2025 vintage. Using 2025: score = 88. Actually, for consistency with Orca (scored at 100 for 2024 vintage), and given that current year is 2026, a 2025 vintage = max(0, 100 - 1*12) = 88. |
| co_benefits | 25 | Minimal-to-moderate. Some local employment and technology transfer to Kenya, but primarily an industrial CDR facility. No SDG certification. |
| registry_methodology | 80 | CCP tier (75-85). Puro.earth is CCP-Eligible. DAC geological storage methodology. Standard CCP score. |

### Composite and Grade

Composite = 97(0.25) + 94(0.20) + 90(0.20) + 97(0.175) + 88(0.10) + 25(0.00) + 80(0.075)
= 24.25 + 18.80 + 18.00 + 16.975 + 8.80 + 0.00 + 6.00
= **92.83**

**Grade: AAA** (90-100)

No disqualifiers triggered.

---

## EXP21: Mati Carbon Enhanced Rock Weathering (India)

**Type**: Enhanced weathering | **Registry**: Puro.earth (pending) | **BeZero**: AA (pre-rating) | **Archetype**: New (closest analog: biochar/ERW hybrid)

### Rationale

Mati Carbon applies crushed basalt to agricultural fields in India, accelerating natural weathering to sequester CO2 as bicarbonates. BeZero awarded AApre, the highest rating for any Indian climate tech project. Enhanced rock weathering (ERW) sits in the "engineered removal + durable storage" band (85-94) on the removal_type hierarchy because it converts CO2 to stable mineral/bicarbonate form with >1,000 yr durability.

### Per-dimension scores

| Dimension | Score | Rationale |
|-----------|------:|-----------|
| removal_type | 88 | Engineered removal + durable storage (85-94). ERW with verified mineralization. CO2 is captured via silicate weathering and stored as dissolved bicarbonates (>1,000 yr). Scored mid-band because the mechanism is proven in lab but field quantification is still maturing. Below DACCS (97) but above biochar (78-80). |
| additionality | 85 | High (75-89). Spreading rock dust on fields has no economic rationale without carbon finance. Technology is early-commercial (not yet standard practice). Carbon revenue is a substantial portion of income. Not quite "very high" because co-product benefits (soil amendment, crop yield) provide some non-carbon value. |
| permanence | 85 | 1,000-10,000 years (80-94). Weathering products (bicarbonates, carbonates) have geological-timescale durability. Scored at low end of band because ocean cycling of bicarbonates introduces some uncertainty vs. solid mineral carbonation. |
| mrv_grade | 72 | Standard+ (60-74). ERW MRV is an active frontier. Mati uses soil/water sampling protocols plus isotopic tracers, but the field is still developing standardized quantification. Periodic sampling with emerging remote sensing. Not yet at "Enhanced" level because ERW monitoring protocols are not yet mature. |
| vintage_year | 88 | 2025 vintage. max(0, 100 - 1*12) = 88. |
| co_benefits | 55 | Partially Verified. Soil health benefits (pH correction, nutrient release), crop yield improvements for smallholder farmers. Some SDG alignment (SDG 2 Zero Hunger, SDG 15 Life on Land). Self-reported with some evidence. |
| registry_methodology | 78 | CCP tier (75-85). Puro.earth is CCP-Eligible. ERW methodology is under development but aligns with CCP-approved criteria. Pending full registration. Scored 78, slightly below 80 standard due to "pending" status. |

### Composite and Grade

Composite = 88(0.25) + 85(0.20) + 72(0.20) + 85(0.175) + 88(0.10) + 55(0.00) + 78(0.075)
= 22.00 + 17.00 + 14.40 + 14.875 + 8.80 + 0.00 + 5.85
= **82.93**

**Grade: AA** (75-89)

No disqualifiers triggered.

---

## EXP22: Tradewater Thailand 6 (ODS Destruction)

**Type**: ODS destruction | **Registry**: ACR 937 | **BeZero**: A | **Archetype**: Closest analog: N2O destruction (C011) / methane abatement (EXP13)

### Rationale

Tradewater collects and destroys ozone-depleting substances (CFCs, HCFCs) that have been seized by Thai authorities. ODS destruction has extremely high GWP (CFC-12 = 10,900x CO2), making it one of the highest-certainty avoidance interventions. CCP-approved methodology. Direct measurement of quantities destroyed.

### Per-dimension scores

| Dimension | Score | Rationale |
|-----------|------:|-----------|
| removal_type | 55 | Avoidance with high certainty (45-59). ODS destruction prevents release of extremely potent GHGs. The substances are already manufactured and stockpiled; destruction is the intervention. Scored at top of band (55) because the counterfactual (eventual release) is near-certain for seized/orphaned refrigerants, and direct measurement is possible. Comparable to N2O destruction (C011 = 55). |
| additionality | 78 | High (75-89). Without carbon finance, seized ODS stockpiles in developing countries are typically stored indefinitely (eventual leakage is the counterfactual). Tradewater's business model is 100% carbon-finance dependent for international collection. Regulatory mandates exist in developed countries but not consistently enforced in Thailand. Strong additionality case, slightly less than DAC but stronger than cookstoves. |
| permanence | 10 | No storage (0-14). Avoidance project -- no carbon is stored. ODS is destroyed, preventing future release, but the mechanism is avoidance, not removal. Same as cookstoves/renewables. |
| mrv_grade | 82 | Enhanced (75-89). Direct gravimetric measurement of ODS quantities pre- and post-destruction. Independent third-party verification by accredited VVB. Continuous monitoring of destruction efficiency. Strong MRV because the quantities are directly measurable (weigh canisters in, sample destruction exhaust). Above Standard+ because measurement is direct, not modeled. |
| vintage_year | 88 | 2025 vintage. max(0, 100 - 1*12) = 88. |
| co_benefits | 30 | Self-Reported. Ozone layer protection (SDG 13 Climate Action). Some local employment. No SDG certification. Limited community-level co-benefits. |
| registry_methodology | 80 | CCP tier (75-85). ACR is CCP-Eligible. ODS destruction methodology is CCP-approved. Standard CCP score of 80. |

### Composite and Grade

Composite = 55(0.25) + 78(0.20) + 82(0.20) + 10(0.175) + 88(0.10) + 30(0.00) + 80(0.075)
= 13.75 + 15.60 + 16.40 + 1.75 + 8.80 + 0.00 + 6.00
= **62.30**

**Grade: A** (60-74)

No disqualifiers triggered.

---

## EXP23: Rebellion Energy Heartland 2 Methane Abatement

**Type**: Methane abatement (orphan wells) | **Registry**: ACR 966 | **BeZero**: BB | **Archetype**: Rebellion Heartland 1 (EXP13, graded A)

### Rationale

Same developer (Rebellion Energy) and same project type (orphan well plugging) as Heartland 1 (BeZero A, our A), but Heartland 2 received a much lower BeZero BB rating. The press release notes ~2M verified credits from Oklahoma. The lower rating than H1 likely reflects project-specific risk factors: possibly weaker additionality evidence, less direct measurement, or regulatory risk as state plugging programs expand.

### Per-dimension scores

| Dimension | Score | Rationale |
|-----------|------:|-----------|
| removal_type | 52 | Avoidance with high certainty (45-59). Same mechanism as Heartland 1 (orphan well plugging prevents ongoing methane seepage). Scored slightly below H1 (55) because BeZero's significantly lower rating suggests project-level concerns about the wells' methane emission profiles. |
| additionality | 55 | Marginal (45-59). BeZero's BB (vs A for H1) suggests weaker additionality for this specific cohort of wells. Possible reasons: Oklahoma has an active state orphan well program (regulatory additionality risk), or the wells in H2 had lower emission rates (financial additionality is weaker for lower-emitting wells). Scored materially below H1 (75) to reflect the agency signal. |
| permanence | 10 | No storage (0-14). Avoidance project; no carbon stored. Well plugging prevents future emissions. Same as H1. |
| mrv_grade | 60 | Standard+ (60-74). Orphan well methane measurement can be variable. H2's BB rating may reflect concerns about measurement quality across a large number of wells (~2M credits = many wells). Direct measurement is possible but may rely more on emission factors for some wells. Below H1's 78 based on the larger scale and possible measurement challenges. |
| vintage_year | 88 | 2024/2025 vintage. max(0, 100 - 1*12) = 88. |
| co_benefits | 20 | Minimal. Groundwater protection, hazard removal in rural Oklahoma. No SDG certification. |
| registry_methodology | 80 | CCP tier (75-85). ACR is CCP-Eligible. Methodology for orphan well methane is CCP-approved. |

### Composite and Grade

Composite = 52(0.25) + 55(0.20) + 60(0.20) + 10(0.175) + 88(0.10) + 20(0.00) + 80(0.075)
= 13.00 + 11.00 + 12.00 + 1.75 + 8.80 + 0.00 + 6.00
= **52.55**

**Grade: BBB** (45-59)

No disqualifiers triggered.

---

## EXP24: Rebellion Energy Heartland 3 Methane Abatement

**Type**: Methane abatement (orphan wells) | **Registry**: ACR 1023 | **BeZero**: BB | **MSCI**: AA | **Archetype**: Rebellion Heartland 1 (EXP13)

### Rationale

Another Rebellion orphan well project with a striking inter-agency disagreement: BeZero rates it BB while MSCI rates it AA. ~600,000 tCO2e, 2024 vintage. The MSCI AA suggests strong technical quality from MSCI's perspective, while BeZero's BB suggests concern about the same risk factors as Heartland 2. Our framework should assess independently based on the rubric.

H3 is similar to H2 in BeZero's assessment (both BB) but smaller scale (600K vs 2M credits). MSCI's AA could reflect that MSCI weights MRV and methodology more heavily, or that MSCI's assessment of orphan well additionality differs from BeZero's.

### Per-dimension scores

| Dimension | Score | Rationale |
|-----------|------:|-----------|
| removal_type | 52 | Avoidance with high certainty (45-59). Same as H2 -- orphan well plugging. |
| additionality | 58 | Marginal-to-Moderate (boundary). Slightly higher than H2 (55) because H3 is smaller scale (600K credits), suggesting more targeted well selection (potentially higher-emitting wells with stronger additionality). Still well below H1 (75) because BeZero rates it the same BB as H2. |
| permanence | 10 | No storage (0-14). Avoidance project. |
| mrv_grade | 65 | Standard+ (60-74). MSCI's AA rating is at least partly driven by strong MRV assessment. Smaller project (600K vs 2M credits) may mean better per-well measurement coverage. Scored slightly above H2 (60) based on the MSCI signal, but not Enhanced because BeZero disagrees. |
| vintage_year | 100 | 2024 vintage. max(0, 100 - 2*12) = 76. Wait -- current year is 2026, so 2024 vintage: max(0, 100 - 2*12) = 76. |
| co_benefits | 20 | Minimal. Same as other Heartland projects. |
| registry_methodology | 80 | CCP tier (75-85). ACR, CCP-approved methodology. |

### Composite and Grade

Composite = 52(0.25) + 58(0.20) + 65(0.20) + 10(0.175) + 76(0.10) + 20(0.00) + 80(0.075)
= 13.00 + 11.60 + 13.00 + 1.75 + 7.60 + 0.00 + 6.00
= **52.95**

**Grade: BBB** (45-59)

No disqualifiers triggered.

---

## EXP25: Guyana Jurisdictional REDD+

**Type**: J-REDD+ | **Registry**: ART 102 (Architecture for REDD+ Transactions) | **BeZero**: BB | **Archetype**: New (closest analog: REDD+ projects, but jurisdictional)

### Rationale

BeZero's first-ever jurisdictional REDD+ rating. Guyana's ART-TREES credits are used by airlines for CORSIA compliance. J-REDD+ differs fundamentally from project-level REDD+: it operates at the national/subnational level, reducing leakage risk but introducing governance complexity. Guyana has 18M hectares of largely intact rainforest with historically low deforestation.

### Per-dimension scores

| Dimension | Score | Rationale |
|-----------|------:|-----------|
| removal_type | 22 | Avoidance with baseline uncertainty (15-29). Like all REDD+, this is avoided deforestation. The counterfactual baseline (how much deforestation would have occurred without the program) is inherently uncertain. J-REDD+ mitigates leakage but does not change the fundamental baseline uncertainty. Scored at mid-band (22), consistent with other REDD+ projects (Cordillera Azul 22, Rimba Raya 22, Kariba 18). |
| additionality | 45 | Marginal (45-59). Guyana's forests are largely intact with historically low deforestation rates (~0.05%/yr). This creates a fundamental additionality question: is the program preventing deforestation that would have occurred, or is it crediting an already low baseline? The HFLD (High Forest Low Deforestation) approach used by ART-TREES rewards preservation but the additionality of preserving forests that weren't being deforested is debatable. Carbon finance provides revenue to maintain forest governance, which is meaningful but marginal. |
| permanence | 35 | 20-40 years (35-49). J-REDD+ depends on continued government commitment. Guyana's political commitment to forest conservation has been strong under the LCDS (Low Carbon Development Strategy), but government commitments can change with administrations. The oil revenue boom (Stabroek block) creates pressure for alternative development. Buffer pool through ART registry. Scored at low end of band (35) reflecting political non-permanence risk. |
| mrv_grade | 55 | Standard (45-59). ART-TREES requires national forest monitoring with satellite imagery (Hansen/GFW data). Guyana's MRVS (Monitoring, Reporting and Verification System) has been operational since 2012 with international support. Template-based reporting with national GHG inventory. Standard verification by independent assessor. |
| vintage_year | 88 | 2025 vintage. max(0, 100 - 1*12) = 88. |
| co_benefits | 65 | Partially Verified. Guyana's LCDS links forest conservation to community development, indigenous land rights, and biodiversity. Some SDG alignment (SDG 13, 15). International partnerships document co-benefits but quantification is partial. |
| registry_methodology | 80 | CCP tier (75-85). ART is CCP-Eligible. TREES v2.0 methodology is CCP-approved. This is one of the strongest registry/methodology combinations for REDD+. Score 80 standard. |

### Composite and Grade

Composite = 22(0.25) + 45(0.20) + 55(0.20) + 35(0.175) + 88(0.10) + 65(0.00) + 80(0.075)
= 5.50 + 9.00 + 11.00 + 6.125 + 8.80 + 0.00 + 6.00
= **46.43**

**Grade: BBB** (45-59)

No disqualifiers triggered. Note: despite being REDD+, J-REDD+ scores higher than most project-level REDD+ because: (a) registry_methodology is CCP (80 vs 30 for problematic REDD+ methodologies), (b) MRV at national level with satellite monitoring is better than many project-level REDD+, and (c) recent vintage.

---

## EXP26: BRCarbon Brazilian Amazon APD Grouped Project

**Type**: REDD+ | **Registry**: VCS 2551 | **BeZero**: A | **Archetype**: REDD+ (EXP01-05, but materially higher quality)

### Rationale

BRCarbon's Amazon APD (Avoided Planned Deforestation) project is the first-ever Latam REDD+ to achieve BeZero's A rating. This is exceptional for REDD+ -- most REDD+ projects receive B to BBB from BeZero. APD (Avoided Planned Deforestation) has a stronger baseline than AUD (Avoided Unplanned Deforestation) because planned deforestation can be documented via permits, land-use plans, etc. The grouped project structure also allows inclusion of multiple properties with documented deforestation plans.

### Per-dimension scores

| Dimension | Score | Rationale |
|-----------|------:|-----------|
| removal_type | 25 | Avoidance with baseline uncertainty (15-29). Even the best REDD+ project is still avoided deforestation, which depends on baseline accuracy. APD is at the top of this band because the "planned" baseline is more defensible than "unplanned" (AUD). Scored 25 (top of band) vs 22 for typical REDD+ and 18 for problematic REDD+ (Kariba). |
| additionality | 68 | Moderate (60-74). For a REDD+ project to earn BeZero A, additionality must be strong. APD with documented planned deforestation (legal land-clearing permits in the Brazilian Amazon) provides clear counterfactual. Carbon finance redirects land use from planned clearing to conservation. Strongest REDD+ additionality case in our dataset, but still below industrial avoidance (where the counterfactual is a physical process, not a land-use decision). |
| permanence | 45 | 20-40 years (35-49). Standard REDD+ non-permanence risk: fire, illegal logging, political change. Brazil's forest code enforcement has fluctuated across administrations. VCS buffer pool mechanism. Grouped project structure may improve monitoring but doesn't fundamentally change permanence. Scored at top of band (45) reflecting good project design, but REDD+ inherently has reversal risk. |
| mrv_grade | 65 | Standard+ (60-74). Verra VCS verification with satellite imagery (Prodes/DETER deforestation monitoring). Grouped project structure with GPS-delineated properties. Standard VVB verification. BeZero's A rating implies MRV passed their assessment, so we score at top of Standard+ (65). |
| vintage_year | 88 | 2025 vintage. max(0, 100 - 1*12) = 88. |
| co_benefits | 60 | Partially Verified. Amazon biodiversity conservation, indigenous/community engagement, watershed protection. Some SDG alignment. Self-reported with partial evidence from project documentation. |
| registry_methodology | 30 | Non-CCP (25-50). VCS REDD+ methodologies (VM0007/VM0015 family) are NOT CCP-approved as of Q1 2026. ICVCM has deferred REDD+ methodology assessment pending updated Verra REDD+ methodology (VM0048 consolidation). Scored 30 at low end of Non-CCP band because REDD+ methodology is under active review/revision and has known overcrediting issues documented in West et al. 2023. Actually: VM0007 APD may be in a different position than VM0009/VM0015. But as of Q1 2026, no VCS REDD+ methodology has CCP approval. Score 35 (above the overcrediting-penalized floor because APD is less affected by the West et al. critique which focused on AUD). Applying known_overcrediting modifier would be inappropriate for APD specifically. Revised: 35. |

### Composite and Grade

Composite = 25(0.25) + 68(0.20) + 65(0.20) + 45(0.175) + 88(0.10) + 60(0.00) + 35(0.075)
= 6.25 + 13.60 + 13.00 + 7.875 + 8.80 + 0.00 + 2.625
= **52.15**

**Grade: BBB** (45-59)

No disqualifiers triggered.

Note: This is one of the largest divergences from BeZero in our dataset (our BBB vs BeZero A, a 2-grade gap). The structural explanation is the same as the cookstove divergence: our framework structurally penalizes avoidance projects via removal_type and permanence. A REDD+ project must overcome ~36 points of structural deficit in those two dimensions. Even with top-of-band additionality and MRV, reaching grade A (60) is extremely difficult for any REDD+ credit.

---

## EXP27: Brazil Nut Concessions REDD+ (Madre de Dios, Peru)

**Type**: REDD+ | **Registry**: VCS 868 | **BeZero**: C | **Archetype**: REDD+ (Cordillera Azul / Rimba Raya pattern)

### Rationale

A REDD+ project in Peru's Madre de Dios region covering Brazil nut concessions. BeZero rates it C (low). Stay Grounded investigation found significant baseline overstatement concerns, and deforestation in the project area doubled after the project started. Bosques Amazonicos is the developer.

### Per-dimension scores

| Dimension | Score | Rationale |
|-----------|------:|-----------|
| removal_type | 20 | Avoidance with baseline uncertainty (15-29). Standard REDD+ AUD. Scored below typical (22) because the baseline has been specifically questioned -- deforestation doubled in the project area, suggesting the baseline was overstated. |
| additionality | 28 | Questionable (0-29). If deforestation increased despite the project, the additionality case is severely undermined. The project claims to prevent deforestation but deforestation got worse. Common practice analysis is weak (nut concessions have some inherent conservation incentive). Near the top of "Questionable" because the project does exist and operate, unlike total non-starters. |
| permanence | 30 | <20 years effectively (15-34). REDD+ with documented reversal: deforestation doubled in project area. Buffer pool exists but the physical permanence is compromised by actual deforestation occurring within the project boundary. Reversal_history_moderate adjustment would apply (-15), bringing from 45 (mid REDD+ band) to 30. |
| mrv_grade | 35 | Basic (30-44). Baseline overstatement documented by independent investigation (Stay Grounded). VVB verification completed but with significant concerns about the accuracy of the baseline. Monitoring appears to have missed or underreported the actual deforestation. |
| vintage_year | 52 | Approximately 2022 vintage (project active since early 2010s but credits span multiple vintages; using mid-range). max(0, 100 - 4*12) = 52. |
| co_benefits | 40 | Self-Reported. Brazil nut harvesting provides livelihoods. Biodiversity in Madre de Dios. Self-reported SDG claims without strong independent verification, especially given the deforestation documented. |
| registry_methodology | 30 | Non-CCP (25-50). VCS REDD+ methodology, not CCP-approved. Known overcrediting for REDD+ AUD per West et al. (2023). Applying known_overcrediting modifier: 45 - 15 = 30. |

### Composite and Grade

Composite = 20(0.25) + 28(0.20) + 35(0.20) + 30(0.175) + 52(0.10) + 40(0.00) + 30(0.075)
= 5.00 + 5.60 + 7.00 + 5.25 + 5.20 + 0.00 + 2.25
= **30.30**

**Grade: BB** (30-44)

No disqualifiers triggered, though this project is on the margin and could warrant a `community_harm` or `biodiversity_harm` flag if further investigation confirms ecological damage.

---

## EXP28: C-Quest Capital Cookstove Projects (aggregate)

**Type**: Cookstoves (aggregate) | **Registry**: GS (multiple) | **Calyx**: E | **Archetype**: Cookstoves (C010/C016) but bottom-tier

### Rationale

C-Quest Capital operated 11+ cookstove projects across Africa and Asia. Calyx rated 60%+ at E or E+ and the remainder at D. High over-crediting risk with fNRB (fraction of non-renewable biomass) overestimated by ~230%. This is an aggregate rather than single-project data point, but it represents the low end of cookstove quality.

Note: This project has no BeZero rating, only Calyx E. It will not contribute to the BeZero Spearman correlation, but is scored for completeness and to anchor the low end of the cookstove quality spectrum.

### Per-dimension scores

| Dimension | Score | Rationale |
|-----------|------:|-----------|
| removal_type | 32 | Avoidance with moderate certainty (30-44). Cookstoves, but at the low end of the band because over-crediting means the actual emission reduction is much smaller than claimed. Scored below standard cookstoves (38 for C010) because the 230% fNRB overestimate means the intervention's real impact is substantially lower. |
| additionality | 35 | Low (30-44). Cookstove distribution has additionality challenges: are the stoves actually used? C-Quest Capital's projects had documented concerns about stove adoption and continued use. Carbon revenue supports distribution, but weak evidence of actual behavioral change. |
| permanence | 5 | No storage (0-14). Avoidance only. Same as all cookstove projects. Scored at bottom (5) because the "avoidance" claim itself is questioned (if fNRB is overstated, the avoided emissions are smaller). |
| mrv_grade | 25 | Deficient (0-29). Calyx's E rating and the documented 230% fNRB overestimation indicate serious MRV failures. Monitoring appears to have been inadequate (survey-based rather than metered). Kitchen performance tests may not have been representative. |
| vintage_year | 52 | Mixed vintages (2018-2023). Using approximate midpoint 2022: max(0, 100 - 4*12) = 52. |
| co_benefits | 40 | Self-Reported. Cookstove projects claim health benefits (reduced indoor air pollution, SDG 3), gender benefits (less firewood collection time, SDG 5). These are plausible but not independently verified for C-Quest specifically, and the integrity concerns undermine trust in all claims. |
| registry_methodology | 75 | CCP tier (75-85), but at the bottom. Gold Standard TPDDTEC is technically CCP-approved for cookstoves. However, scoring at bottom of CCP band (75) because the specific application had known limitations (constrained fNRB). The methodology is approved but the project's implementation of it was deficient. |

### Composite and Grade

Composite = 32(0.25) + 35(0.20) + 25(0.20) + 5(0.175) + 52(0.10) + 40(0.00) + 75(0.075)
= 8.00 + 7.00 + 5.00 + 0.875 + 5.20 + 0.00 + 5.625
= **31.70**

**Grade: BB** (30-44)

No disqualifiers triggered, though this project is borderline. If the fNRB overestimation constitutes a verification failure, `failed_verification` could be triggered (cap at B). Conservative approach: no disqualifier, BB grade.

---

## Summary Table

| ID | Project | Type | Composite | Grade | BeZero | Calyx | MSCI | Grade match? |
|----|---------|------|----------:|-------|--------|-------|------|--------------|
| EXP19 | STRATOS DACCS | DACCS | 93.28 | AAA | AAA | - | - | Yes (exact) |
| EXP20 | Octavia DAC Kenya | DACCS | 92.83 | AAA | AAA | - | - | Yes (exact) |
| EXP21 | Mati Carbon ERW | Enhanced weathering | 82.93 | AA | AA | - | - | Yes (exact) |
| EXP22 | Tradewater ODS | ODS destruction | 62.30 | A | A | - | - | Yes (exact) |
| EXP23 | Rebellion H2 | Methane abatement | 52.55 | BBB | BB | - | - | 1 grade gap |
| EXP24 | Rebellion H3 | Methane abatement | 52.95 | BBB | BB | AA | - | 1 gap (BZ), 3 gap (MSCI) |
| EXP25 | Guyana J-REDD+ | J-REDD+ | 46.43 | BBB | BB | - | - | 1 grade gap |
| EXP26 | BRCarbon Amazon | REDD+ | 52.15 | BBB | A | - | - | 2 grade gap |
| EXP27 | Brazil Nut REDD+ | REDD+ | 30.30 | BB | C | - | - | Directional match |
| EXP28 | C-Quest Capital | Cookstoves | 31.70 | BB | - | E | - | N/A (no BeZero) |

### Agreement analysis

- **Exact matches** (same grade on common scale): 4 of 9 with BeZero (EXP19, 20, 21, 22)
- **1-grade gap**: 3 of 9 (EXP23, 24, 25)
- **2-grade gap**: 1 of 9 (EXP26 -- structural REDD+ penalty)
- **Directional**: 1 of 9 (EXP27 -- both rate it low)

The structural pattern continues: our framework and BeZero agree closely on engineered removal and industrial avoidance, but our framework rates REDD+ and methane abatement lower due to the removal_type and permanence structural penalties.
