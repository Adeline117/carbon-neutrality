# Regulatory Policy Mapping: ERC-CCQR Framework to Major Carbon Market Governance Frameworks

*Mapping the seven-dimension quality rating framework to specific provisions in ICVCM CCP, Paris Agreement Article 6, CORSIA, Singapore ICC, EU CRCF, and VCMI Claims Code.*

*Prepared for Nature Sustainability supplementary materials. Last updated: 2026-04-14.*

---

## 1. Summary Mapping Table

The following table maps each of the framework's seven quality dimensions (with current v0.6 weights) to specific provisions across six regulatory frameworks. Cells marked with a check indicate direct mapping; cells marked with a delta indicate the framework extends beyond the regulatory provision; cells marked with a dash indicate no direct mapping.

| Framework Dimension (Weight) | ICVCM CCP | Article 6.4 (PACM) | CORSIA EUC | Singapore ICC | EU CRCF | VCMI Claims Code |
|------------------------------|-----------|---------------------|------------|---------------|---------|------------------|
| **Removal type hierarchy** (0.250) | CCP 7 (no lock-in) | Removal/reduction distinction in SB methodology standards | No explicit hierarchy; avoidance and removal both eligible | No explicit hierarchy | Central: 4 activity categories with distinct rules | Defers to CCP |
| **Additionality** (0.200) | CCP 8 (programme-level + category-level) | SB Standard: financial + barrier + common practice analysis | EUC Criterion 3 (additionality) | ICC Criterion: "Additional" | CRCF Art. 4(1)(b): beyond standard practice and legal requirements | Defers to CCP |
| **MRV grade** (0.200) | CCP 4 (robust validation/verification) + CCP 5 (robust quantification) | SB Standards on baseline, monitoring, leakage | EUC: monitoring/verification by accredited independent entity | ICC Criterion: "Quantified and verified" | CRCF Art. 4(1)(a): quantification with net benefit calculation | Defers to CCP |
| **Permanence** (0.175) | CCP 9 (permanence + compensation for reversals; >=40-yr monitoring; >=20% buffer) | SB Standard on non-permanence/reversals | EUC: permanence provisions | ICC Criterion: "Permanent" | CRCF Art. 4(1)(c): monitoring period rules; permanent vs. temporary storage distinction | Defers to CCP |
| **Vintage year** (0.100) | No explicit vintage criterion; recency implied by methodology approval dates | No vintage restriction; corresponding adjustment timing matters | Phase 2 (2027-2029): vintage eligibility windows apply | Vintage must be 2021-2030 | Monitoring period start date; no explicit vintage decay | No vintage criterion |
| **Co-benefits / Safeguards gate** (0.000 weight; disqualifier only) | CCP 10 (sustainable development benefits + safeguards); requires FPIC, biodiversity, human rights assessments | Environmental and social safeguards required | EUC: "do no net harm" + environmental/social safeguards | ICC Criterion: "No net harm" | CRCF Art. 4(1)(d): sustainability; positive biodiversity co-benefit required for carbon farming | VCMI Foundational Step: Paris-aligned targets + high-quality credits |
| **Registry & methodology** (0.075) | Programme-level assessment (5 approved programmes); category-level assessment (36+ approved methodologies) | SB methodology approval process; CDM transition pathway | TAB programme assessment (7+ eligible programmes) | NEA approval process informed by BeZero/Calyx/Sylvera ratings panel | Certification scheme recognition + certification body accreditation | Requires CCP-labelled credits |

### Key: Where the framework adds value beyond each regulatory provision

| Capability | ICVCM CCP | Article 6.4 | CORSIA | Singapore ICC | EU CRCF | VCMI |
|-----------|-----------|-------------|--------|---------------|---------|------|
| **Continuous scoring** (0-100 vs binary) | Extends: CCP is pass/fail; framework scores 0-100 within and above threshold | Extends: PACM is approve/reject; framework provides gradient | Extends: TAB is eligible/ineligible; framework scores within eligible set | Extends: NEA is approve/reject; framework adds granularity | Extends: CRCF certifies or not; framework differentiates quality among certified units | Extends: VCMI defers quality definition; framework operationalises it |
| **Distributional uncertainty** (P(grade)) | Novel: no CCP provision for uncertainty quantification | Novel: no PACM provision | Novel: no CORSIA provision | Novel: rating agencies produce point ratings, not distributions | Novel: no CRCF provision | Novel: no VCMI provision |
| **On-chain enforcement** (meetsGrade()) | Novel: CCP labels are off-chain registry metadata | Novel: corresponding adjustments are manual bilateral processes | Novel: CORSIA eligibility is manual TAB list | Novel: NEA approval is manual regulatory process | Novel: CRCF certification is manual EU process | Novel: VCMI claims are self-reported |
| **Adverse selection metric** (Lemons Index) | Novel: no CCP-level pool quality metric | Novel: no Article 6 pool metric | Relevant: could assess CORSIA eligible pool quality | Novel: could assess ICC-eligible credit pool quality | Not directly applicable (individual certification, not pooling) | Relevant: could assess quality of credits used for claims |

---

## 2. Per-Framework Detailed Analysis

### 2A. ICVCM Core Carbon Principles (CCP)

#### Framework overview

The ICVCM Assessment Framework (Version 3, May 2024) operationalises ten Core Carbon Principles through a two-level assessment: programme-level (governance, tracking, transparency, independent verification) and category-level (methodology-specific requirements for additionality, permanence, quantification, safeguards). Five programmes are currently approved (ACR, ART, Climate Action Reserve, Gold Standard, Verra VCS), with 36+ methodology categories approved as of late 2025 covering approximately 101 million credits and 4% of 2024 market volume.

**Sources**: ICVCM Assessment Framework v3 (May 2024); ICVCM CCP-Approved Methodologies list; ICVCM Assessment Status page.

#### Dimension-by-dimension mapping to CCP criteria

**1. Removal type hierarchy (weight 0.250) --> CCP 7 (Transition towards net-zero emissions)**

CCP 7 requires that mitigation activities "shall not lock in levels of GHG emissions, technologies or carbon-intensive practices that are incompatible with the objective of achieving net zero GHG emissions by mid-century." This implicitly creates a hierarchy: technologies that lock in fossil infrastructure score lower. Our framework makes this explicit via the Oxford Principles hierarchy, scoring engineered removal with geological storage (95-100) through avoidance with baseline uncertainty (15-29). The ICVCM's "fast track" vs. "deeper assessment" vs. "very unlikely to meet criteria" classification at the category level functionally encodes a coarse version of this hierarchy -- renewable energy and HFC-23 destruction were rejected ("very unlikely"), while DACCS and biochar were fast-tracked.

**Our framework extends CCP 7** by providing a continuous score within the removal-type space rather than a ternary classification. A DACCS credit (score ~95) and a biochar credit (score ~80) both pass CCP but differ meaningfully on permanence risk and removal pathway -- our scoring captures this.

**2. Additionality (weight 0.200) --> CCP 8 (Additionality)**

CCP 8 requires additionality demonstration at both programme level (the programme must have rules requiring additionality analysis) and category level (the methodology must specify tests appropriate to the project type). The Assessment Framework details acceptable approaches: investment analysis, barrier analysis, common practice analysis, and regulatory surplus tests.

Our additionality dimension scores 0-100 based on carbon revenue dependency, investment barrier documentation, common practice analysis, and regulatory surplus -- the same criteria CCP 8 requires, but expressed as a continuous score rather than a binary pass/fail. Credits scoring below 30 on our additionality dimension would almost certainly fail CCP 8's additionality requirements; credits scoring 45-75 represent the grey zone where CCP's binary decision is most contested.

**Our framework extends CCP 8** by capturing additionality gradient. A project with carbon revenue at 45% of income (strong additionality) and one at 16% (marginal additionality) may both pass CCP 8 but receive materially different scores (e.g., 82 vs. 50) in our framework.

**3. MRV grade (weight 0.200) --> CCP 4 (Robust independent third-party validation and verification) + CCP 5 (Robust quantification)**

CCP 4 requires "robust independent third-party validation and verification" by bodies accredited to ISO 14065. CCP 5 requires "robust quantification of emission reductions and removals based on conservative approaches, completeness and sound scientific methods." The Assessment Framework further specifies that baselines must be "estimated conservatively" and that uncertainty must be addressed.

Our MRV dimension scores monitoring quality (sensor/satellite coverage), reporting quality (uncertainty quantification), and verification independence (third-party cross-validation). Scores of 90-100 (digital MRV with continuous IoT/sensor data) substantially exceed CCP 4/5's requirements; scores of 45-59 (standard registry compliance) represent the CCP 4/5 baseline. Our framework specifically rewards dMRV (digital measurement, reporting, and verification) -- validated by Gold Standard's fully digital cookstove credits on Hedera Guardian (2025) and Verra's DMRV pilot (2026) -- as the frontier of MRV quality.

**Our framework extends CCP 4/5** by (a) differentiating between traditional VVB verification and dMRV, and (b) incorporating the Coglianese & Giles (Science, 2025) finding that 95 projects passing VVB audit substantially overstated benefits -- our framework penalises reliance on traditional VVB as the sole verification mechanism.

**4. Permanence (weight 0.175) --> CCP 9 (Permanence)**

CCP 9 is among the most prescriptive CCPs. It requires: (a) for removal activities, a minimum 40-year monitoring period for categories assessed as high risk of reversal; (b) a buffer pool contribution of at least 20% for nature-based activities; (c) a compensation mechanism for reversals during the monitoring period; (d) additional requirements for geological storage certification.

Our permanence dimension maps storage duration to a 0-100 scale: geological storage >10,000 years scores 95-100; biological storage with 40-100 year commitment and >=20% buffer scores 50-64. The CCP 9 "40-year monitoring + 20% buffer" threshold corresponds approximately to a score of 50-55 in our framework -- the lower bound of what we classify as BBB-grade permanence. This means CCP 9 compliance establishes a floor at approximately BBB on our permanence dimension, consistent with our empirical finding that CCP-eligible credits cluster at BBB-A overall.

**Our framework extends CCP 9** by scoring permanence on a continuous duration scale. A biochar project with 1,000+ year demonstrated stability (score ~88) and a reforestation project with a 40-year commitment and 20% buffer (score ~52) both satisfy CCP 9, but our framework correctly differentiates the order-of-magnitude difference in storage durability.

**5. Vintage year (weight 0.100) --> No direct CCP criterion**

CCP does not impose an explicit vintage restriction. However, the methodology approval date functions as an implicit recency filter: credits issued under methodologies that fail the category-level assessment cannot receive CCP labels regardless of vintage. Our vintage dimension applies a temporal decay formula (12 points per year), which captures the empirical finding that newer vintages have materially lower Lemons Index scores (pre-2020: LI=0.687; 2024+: LI=0.273). This dimension has no CCP analogue and represents independent quality information.

**6. Co-benefits / Safeguards gate (weight 0.000; disqualifier only) --> CCP 10 (Sustainable development benefits and safeguards)**

CCP 10 requires: (a) robust social and environmental safeguards; (b) assessment and mitigation of risks to Indigenous Peoples and local communities; (c) FPIC (free, prior, and informed consent); (d) biodiversity risk assessment; and (e) transparent benefit-sharing. These are programme-level requirements that all CCP-approved programmes must enforce.

Our framework converts CCP 10 into two mechanisms: (a) a safeguards gate where documented community harm, human rights violations, or biodiversity harm trigger disqualifier caps (at BBB, BB, or B depending on severity); and (b) removal of co-benefits from the composite score to prevent narrative washing. CCP 10 requires safeguards but does not separate safeguards from co-benefit narratives -- a programme can satisfy CCP 10 by having safeguards policies in place without demonstrating that positive co-benefit claims are not inflating perceived quality.

**Our framework extends CCP 10** by implementing the separation advocated by Calyx Global and Sylvera, who both exclude co-benefits from integrity scores. Our safeguards-gate-only approach means that a project cannot compensate for poor carbon integrity with strong SDG narratives -- a design that prevents the narrative-washing dynamic identified by Berg et al. (2025).

**7. Registry & methodology (weight 0.075) --> Programme-level + category-level assessments**

Our registry dimension uses a binary CCP-eligible (score ~80) vs. non-CCP (score 25-50) classification that directly encodes the ICVCM assessment outcome. The v0.6 simplification of this dimension was motivated by the finding that the original four-tier rubric produced the lowest inter-rater reliability (kappa = 0.168), while the binary CCP/non-CCP classification produces clean separation validated at 1.99 grade levels against Calyx Global's independent measurement.

#### Where the framework goes beyond CCP

1. **Continuous scoring vs. binary labelling**: CCP produces a single binary label (CCP-approved or not). Our framework provides a 0-100 composite with six grade tiers, enabling differentiation among CCP-approved credits -- the 43% BBB to 8% AAA range within CCP-eligible credits that CCP itself cannot express.

2. **Distributional uncertainty**: No CCP document addresses grade uncertainty. Our P(grade) posteriors -- computed via Gaussian CDF from empirically calibrated per-dimension variances -- are, to our knowledge, the first published uncertainty quantification for any carbon credit rating system.

3. **Pool-level adverse selection metric**: CCP assesses individual credit categories, not pools. Our Lemons Index quantifies the aggregate quality of any pool or portfolio, showing that CCP filtering alone reduces adverse selection from LI=0.667 to LI=0.419 (37% improvement) but does not eliminate it.

4. **On-chain enforcement**: CCP labels exist as off-chain metadata in registry systems. Our `meetsGrade()` function makes quality gates callable by smart contracts, enabling automated enforcement at deposit, retirement, and trading.

#### How CCP could adopt quality ratings

The ICVCM Assessment Procedure already uses a three-tier classification (fast track / deeper assessment / very unlikely to meet) that maps to our scoring gradient. The CCP Assessment Framework could augment its binary label with a quality score overlay:

- **Step 1**: Map CCP Assessment Framework criteria to our seven-dimension rubric (or a CCP-derived variant), producing a continuous score alongside the binary label.
- **Step 2**: Publish quality score distributions per approved methodology category, enabling buyers to differentiate among CCP-labelled credits.
- **Step 3**: Integrate `meetsGrade()` or equivalent into CCP-approved registry APIs, making quality gates available to market platforms without requiring blockchain infrastructure.

---

### 2B. Article 6 of the Paris Agreement

#### Article 6.2: Cooperative Approaches and Corresponding Adjustments

Article 6.2, operationalised through Decision 2/CMA.3 (Glasgow, 2021) and refined in Decision -/CMA.4 (Sharm el-Sheikh, 2022), establishes the framework for internationally transferred mitigation outcomes (ITMOs). Parties engaging in cooperative approaches must apply corresponding adjustments to their NDC accounting to prevent double counting.

**How quality ratings support corresponding adjustments:**

Corresponding adjustments require host countries to deduct transferred mitigation outcomes from their NDC accounting. The political and economic cost of this deduction increases with credit quality -- a host country should be more willing to transfer a low-additionality credit (which may not represent real mitigation) than a high-additionality one (which directly contributes to NDC achievement). Our framework's additionality and MRV dimensions directly inform the quality of the mitigation outcome being transferred:

- **High-scoring credits (AA-AAA)**: Represent verifiable, additional mitigation. Host countries face a real NDC cost from corresponding adjustments. Quality ratings help host countries price this cost accurately.
- **Low-scoring credits (B-BB)**: May not represent real mitigation. Corresponding adjustments on these credits create phantom NDC deductions -- the host country deducts a claimed reduction that may not exist, while the acquiring country counts it toward their target. Our framework's Lemons Index for Article 6 credit pools would quantify this risk.

As of 2025, over 90 Article 6.2 agreements have been signed, but only one ITMO transfer has been completed (Columbia CGEP, 2025). Quality uncertainty is a plausible contributor to this implementation gap -- parties cannot confidently commit to corresponding adjustments when the quality of the underlying mitigation outcomes is uncertain. Our framework addresses this by providing a transparent, reproducible quality signal that both transferring and acquiring parties can reference.

**Specific UNFCCC decision provisions:**
- Decision 2/CMA.3, para 4: Requires that cooperative approaches "promote sustainable development; ensure environmental integrity and transparency, including in governance; and shall apply robust accounting." Our framework's MRV dimension (environmental integrity), transparency (open-source scoring), and additionality dimension (robust accounting) directly address these requirements.
- Decision -/CMA.4, para 7(a-d): Requires that ITMOs are "real, verified, and additional." Our framework scores all three attributes.

#### Article 6.4: The Paris Agreement Crediting Mechanism (PACM)

Article 6.4, established by Decision 3/CMA.3 and governed by the Article 6.4 Supervisory Body, creates a centralised UNFCCC mechanism replacing the CDM. The Supervisory Body (SB) approves methodologies, sets baseline and additionality standards, and oversees the issuance of Article 6.4 Emission Reductions (A6.4ERs).

**How the SB methodology approval maps to our registry_methodology dimension:**

The SB adopted five methodological standards in 2025 covering baseline-setting, additionality, leakage, suppressed demand, and non-permanence/reversals, and approved the first PACM methodology (landfill gas flaring/use). This approval process is functionally equivalent to ICVCM's category-level assessment -- it determines which project types and methodologies can generate A6.4ERs.

Our registry_methodology dimension encodes this approval as a binary quality signal: SB-approved methodologies would score as CCP-equivalent (score ~80), while CDM legacy methodologies transitioning without SB re-approval would score lower (score ~40-50), reflecting the known quality gap between CDM-era and PACM-era standards. The SB's methodological standards on additionality (financial analysis + barrier analysis + common practice analysis) map directly to our additionality dimension scoring rubric.

**How the Lemons Index applies to Article 6.4 credit pools:**

As the PACM begins issuing A6.4ERs, credit pools will form around methodology categories. Our systematic Lemons Index scan shows that CDM legacy credits (LI=0.718) represent severe adverse selection risk. If CDM credits transition to Article 6.4 without re-assessment under the new SB standards, the resulting Article 6.4 pool could inherit CDM-era quality problems. Our framework provides a quantitative tool to monitor this risk:

- **Pre-transition monitoring**: Score CDM credits under our framework to identify the quality distribution that would transfer to Article 6.4.
- **Post-transition quality gates**: Require minimum quality scores (e.g., BBB) for CDM credits seeking Article 6.4 recognition.
- **Ongoing pool health metrics**: Compute Lemons Index for the Article 6.4 credit pool over time, providing the SB with an aggregate quality indicator.

**Cite**: Decision 2/CMA.3 (Article 6.2 guidance); Decision 3/CMA.3 (Article 6.4 rules, modalities, and procedures); Columbia CGEP (2025), "How to Fully Operationalize Article 6."

---

### 2C. CORSIA (Carbon Offsetting and Reduction Scheme for International Aviation)

#### ICAO Eligible Emissions Unit Criteria

CORSIA, established by ICAO, requires airlines to offset CO2 emissions from international aviation that exceed baseline levels. The Technical Advisory Body (TAB) assesses emissions unit programmes against the CORSIA Emissions Unit Eligibility Criteria (EUC), which comprise Programme Design Elements and Carbon Offset Credit Integrity Assessment Criteria. TAB completed assessments in 2019-2025 and is conducting its 2026 cycle for the Phase 2 compliance period (2027-2029).

The EUC Carbon Offset Credit Integrity Assessment Criteria require:

1. **Additionality**: Credits must represent reductions/removals exceeding legal mandates and business-as-usual scenarios (maps to our additionality dimension, weight 0.200).
2. **Realistic and conservative baselines**: Offset credits must be based on defensible, conservative baseline estimations (maps to our MRV grade dimension, weight 0.200, specifically the quantification sub-criterion).
3. **Monitoring and verification**: Reductions must be calculated conservatively and transparently, verified by accredited independent entities prior to issuance (maps to our MRV grade dimension).
4. **Permanence**: Credits must address permanence and have provisions for reversals (maps to our permanence dimension, weight 0.175).
5. **No double counting**: Programmes must address double issuance, double claiming, and double use (addressed by our disqualifier: evidence of double counting caps grade at B).
6. **Do no net harm**: Projects must comply with social and environmental safeguards (maps to our safeguards gate).

#### Framework grade thresholds as CORSIA eligibility filters

CarbonPlan's analysis found that 99.9% of Toucan BCT credits were ineligible for CORSIA. Our framework's scoring can explain why: BCT's mean composite score of 27.6 (grade B) reflects credits that would fail CORSIA's additionality, permanence, and baseline conservatism requirements. Using our framework as a CORSIA eligibility filter:

- **AAA-AA credits (composite >=75)**: Very likely CORSIA-eligible. These credits score highly on additionality, MRV, and permanence -- the three dimensions most weighted by CORSIA's integrity criteria.
- **A credits (composite 60-74)**: Likely CORSIA-eligible for most methodology categories. Some nature-based credits in this range may face permanence challenges under CORSIA's stricter Phase 2 requirements.
- **BBB credits (composite 45-59)**: Marginal CORSIA eligibility. Credits in this range -- primarily cookstoves, rice methane, and older vintage nature-based credits -- may meet Programme Design Element criteria but struggle with the integrity assessment criteria.
- **BB-B credits (composite <45)**: Very unlikely CORSIA-eligible. This includes renewable energy (LI=0.759), HFC-23 (LI=0.758), and CDM legacy credits (LI=0.718) -- categories that TAB has rejected or restricted.

**TAB assessment process vs. our automated scoring:**

TAB conducts expert-driven programme assessments on multi-year cycles (annual since 2019). The 2026 cycle received 25 programme applications for the 2027-2029 compliance period, with public comment open until 26 April 2026. This process assesses programmes, not individual credits.

Our framework complements TAB by providing credit-level scoring within TAB-approved programmes. A programme approved by TAB (e.g., Verra VCS) may contain credits ranging from B to AA on our scale -- TAB approval does not guarantee individual credit quality. The `meetsGrade()` function could serve as a second-layer CORSIA eligibility filter: airlines would only retire credits from TAB-approved programmes that also meet a minimum quality grade.

**CORSIA Phase 2 demand context**: IATA projects 146-236 million EEU demand for Phase 1 (2024-2026) and offsetting requirements covering 550-600 million tonnes CO2 annually from 2027. At these volumes, quality differentiation within the eligible supply becomes critical -- our framework provides the mechanism.

---

### 2D. Singapore NEA International Carbon Credit Framework

#### What Singapore mandated

Singapore's National Environment Agency (NEA) established the International Carbon Credit (ICC) Framework under the Carbon Pricing (Amendment) Act 2022, enabling carbon tax-liable facilities to offset up to 5% of their taxable emissions using eligible ICCs from 1 January 2024. The carbon tax rate follows a progressive schedule: S$5/tonne (pre-2024), S$25/tonne (2024-2025), S$45/tonne (2026+), with planned increases to S$50-80/tonne by 2030.

The ICC Framework requires credits to meet seven internationally recognised integrity principles:

1. **No double counting**: Must not be counted toward more than one entity's climate target.
2. **Additional**: Must exceed legal requirements and business-as-usual.
3. **Real**: Must represent genuine emission reductions or removals that have occurred.
4. **Quantified and verified**: Must be measurably quantified and independently verified.
5. **Permanent**: Must not be reversible.
6. **No net harm**: Must not violate applicable laws or cause environmental/social harm.
7. **No leakage**: Must not displace emissions to another location.

Credits must represent emissions reductions or removals occurring between 1 January 2021 and 31 December 2030.

On 7 November 2025, NEA appointed BeZero Carbon, Calyx Global, and Sylvera through a competitive tender to serve as an independent ratings panel for the ICC Framework. The panel's role is to provide expert assessments of methodology and project submissions, informing NEA's approval process. This was the first sovereign mandate requiring commercial carbon credit ratings for regulatory compliance.

#### How the Singapore mandate aligns with our framework

The alignment is remarkably close. Singapore's seven ICC principles map directly to our seven dimensions:

| Singapore ICC Principle | Framework Dimension | Weight | Mapping |
|------------------------|---------------------|--------|---------|
| Additional | Additionality | 0.200 | Direct: both assess whether reductions exceed BAU |
| Quantified and verified | MRV grade | 0.200 | Direct: both assess measurement and verification quality |
| Permanent | Permanence | 0.175 | Direct: both assess storage duration and reversal risk |
| No double counting | Disqualifier | Cap at B | Direct: our double-counting disqualifier caps grade at B |
| No net harm | Safeguards gate | Cap at BBB | Direct: our communityHarm and biodiversityHarm disqualifiers |
| No leakage | Subsumed in MRV grade and additionality | -- | Our MRV dimension includes leakage assessment in quantification |
| Real | Composite of removal type + additionality + MRV | -- | "Realness" is an emergent property of scoring well across dimensions |

Singapore's approach of appointing commercial rating agencies (BeZero, Calyx, Sylvera) validates the core thesis of our framework: that independent quality rating is becoming regulatory infrastructure. However, the reliance on proprietary, opaque agency ratings creates the same inter-agency inconsistency problem documented by Carbon Market Watch (2023) -- mean pairwise Spearman rho of +0.009 among the three agencies.

#### What implementation would look like

Our framework could serve as an open, transparent complement to or replacement for the proprietary ratings panel:

1. **Transparent scoring**: Unlike proprietary agency ratings, our open-source rubrics enable NEA to audit and reproduce every score. Singapore's emphasis on transparency (publishing an Overall Eligibility List) aligns with our open-source approach.
2. **On-chain enforcement**: As Singapore explores carbon market digitalisation, the `meetsGrade()` interface enables automated ICC eligibility checking at the point of credit retirement.
3. **Quality differentiation within ICC-eligible credits**: NEA currently makes binary approve/reject decisions. Our continuous scoring (0-100) would enable tiered pricing or differentiated carbon tax offsets -- e.g., AAA credits could offset at full value while BBB credits offset at a discount.
4. **Lemons Index monitoring**: NEA could compute the Lemons Index for the ICC-eligible credit pool over time, tracking whether the 5% offset allowance attracts high- or low-quality credits.

---

### 2E. EU Carbon Removal Certification Framework (CRCF)

#### Key provisions

Regulation (EU) 2024/3012, applying from 26 December 2024, establishes a voluntary EU-wide certification framework for carbon removals and soil emission reductions. The CRCF distinguishes four activity categories:

1. **Permanent carbon removal**: Geological storage (DACCS, BECCS with geological injection), mineralisation. Storage for centuries or millennia.
2. **Carbon farming -- temporary carbon storage**: Afforestation, reforestation, soil organic carbon enhancement, wetland restoration. Biological storage with reversal risk.
3. **Carbon farming -- soil emission reduction**: Reduced tillage, livestock feed additives, organic fertiliser substitution. Avoided emissions from agricultural practices.
4. **Carbon storage in long-lasting products**: Timber construction, biochar in concrete, carbon-mineralised building materials. Storage for the product's design life.

Four quality criteria must be met (CRCF Art. 4):
- **Quantification** (Art. 4(1)(a)): Net carbon removal benefit calculated against standardised baselines.
- **Additionality** (Art. 4(1)(b)): Activities must exceed standard practice and legal requirements.
- **Permanence/storage and liability** (Art. 4(1)(c)): Operators must monitor and guarantee storage over a monitoring period; liable for reversals.
- **Sustainability** (Art. 4(1)(d)): Carbon farming and forestry must show positive biodiversity and ecosystem co-benefits.

Methodologies are being developed in 2025-2026 for DACCS, biochar, carbon farming, and carbon storage in buildings. Implementing Regulation (EU) 2025/2358 (November 2025) established technical rules for certification schemes and bodies.

#### How our removal_type hierarchy maps to CRCF categories

Our removal type dimension (weight 0.250) encodes a hierarchy that closely mirrors the CRCF's four-category structure:

| CRCF Category | Our Removal Type Score Range | Grade Implication |
|---------------|------------------------------|-------------------|
| Permanent carbon removal (geological) | 95-100 | AAA floor from this dimension alone |
| Permanent carbon removal (mineralisation) | 85-94 | AA-AAA contribution |
| Carbon storage in long-lasting products (biochar, timber) | 75-84 | AA contribution |
| Carbon farming -- temporary carbon storage (afforestation) | 60-74 | A contribution |
| Carbon farming -- soil emission reduction | 45-59 | BBB contribution |

The CRCF's sustainability criterion (Art. 4(1)(d)) maps to our safeguards gate: our biodiversityHarm disqualifier (cap at BBB) operationalises the CRCF's requirement that carbon farming activities must demonstrate positive biodiversity co-benefits. Importantly, the CRCF's sustainability requirement goes further than our current safeguards gate by requiring positive biodiversity impact for carbon farming (our framework only penalises negative impact).

**Novel contribution to CRCF implementation**: The CRCF does not differentiate quality within each category. A DACCS project with excellent MRV and a DACCS project with deficient monitoring are both "permanent carbon removals" under the CRCF. Our framework provides the within-category quality differentiation that the CRCF lacks.

---

### 2F. Voluntary Carbon Market Integrity Initiative (VCMI)

#### Claims Code of Practice

The VCMI Claims Code of Practice (updated August 2025) establishes a framework for corporate carbon credit claims at three tiers:

1. **Silver**: Purchase and retire high-quality carbon credits equivalent to >=10% and <50% of remaining emissions after demonstrating progress toward near-term emission reduction targets.
2. **Gold**: Purchase and retire high-quality credits equivalent to 60-100% of remaining emissions.
3. **Platinum**: Purchase and retire high-quality credits equivalent to >=100% of remaining emissions.

**Critical definitional link**: VCMI defines "high-quality carbon credits" as those meeting the ICVCM Core Carbon Principles. This creates a direct dependency chain: VCMI Claims --> CCP quality definition --> our framework's continuous scoring above the CCP threshold.

#### How quality ratings support corporate claim tiers

The VCMI's claim tiers are defined by *quantity* (percentage of remaining emissions offset) but not by *quality gradient* within the "high-quality" definition. A company retiring 100% of emissions using BBB-grade CCP-eligible credits and a company retiring 100% using AAA-grade credits both achieve Platinum status. Our framework enables a quality-weighted claims approach:

- **Quality-weighted retirement volume**: Instead of counting each credit equally, weight retirements by quality score. A company retiring 50 AAA credits (composite ~92) provides equivalent quality-weighted volume to 100 BBB credits (composite ~50).
- **Quality floor for claim tiers**: VCMI could require minimum quality grades for each tier: Silver requires BBB+, Gold requires A+, Platinum requires AA+. This prevents companies from achieving Platinum status with high volumes of marginally-CCP-eligible credits.
- **Lemons Index for corporate portfolios**: Compute the Lemons Index for each company's retired credit portfolio, providing a portfolio-level quality metric that supplements the VCMI tier.

Our framework's distributional uncertainty (P(grade)) is particularly valuable for VCMI claims: a company can report not just the grade of each retired credit but the probability that the grade is correct, enabling honest disclosure of quality uncertainty in sustainability reports.

---

## 3. Gap Analysis

### What our framework covers that regulators don't

| Capability | Gap in Current Regulatory Frameworks |
|-----------|--------------------------------------|
| **Continuous quality scoring (0-100)** | All six frameworks use binary or ternary decisions (approved/rejected, eligible/ineligible). None provides a continuous quality gradient. |
| **Distributional uncertainty (P(grade))** | No regulatory framework quantifies the uncertainty of its quality assessments. Our P(grade) posteriors are novel across all six frameworks. |
| **Pool-level adverse selection metric (Lemons Index)** | No framework assesses aggregate pool quality. CORSIA and Article 6.4 assess programmes and methodologies but not the pools that form from approved credits. |
| **On-chain enforcement (meetsGrade())** | All quality gates are currently manual, off-chain processes. Automated enforcement via smart contracts is novel. |
| **Vintage decay scoring** | Only Singapore ICC has a vintage window (2021-2030). No framework applies a continuous temporal decay function capturing the empirical relationship between vintage age and quality. |
| **Cross-framework comparability** | Each framework has its own quality definition and assessment process. Our seven-dimension scoring provides a common language enabling cross-framework comparison. |

### What regulators cover that our framework doesn't

| Regulatory Provision | Gap in Our Framework |
|---------------------|---------------------|
| **Corresponding adjustments (Art. 6.2)** | Our framework scores credit quality but does not address NDC accounting mechanics. Integration with national registry systems for corresponding adjustment tracking is outside scope. |
| **Host country authorisation** | Article 6.2/6.4 and CORSIA Phase 2 require host country authorisation (Letters of Authorisation). Our framework does not assess sovereign consent. |
| **Governance requirements** | ICVCM CCP 1-3 assess programme governance (board structure, stakeholder input, grievance mechanisms). Our registry_methodology dimension encodes governance outcomes (CCP-approved or not) but does not directly assess governance processes. |
| **CRCF sustainability requirement** (positive biodiversity) | The CRCF requires positive biodiversity impact for carbon farming. Our safeguards gate only penalises negative impact; it does not require positive impact. This is a gap that could be addressed by adding a biodiversity co-benefit requirement for nature-based credits. |
| **Leakage** | Singapore ICC and CORSIA explicitly require no-leakage assessment. Our framework subsumes leakage within the MRV and additionality dimensions but does not score it as a standalone criterion. |
| **Benefit-sharing** | CCP 10 requires transparent benefit-sharing with local communities. Our framework does not assess benefit-sharing arrangements. |

---

## 4. Implementation Pathway

### 4.1 Near-term (2026-2027): Regulatory pilot integrations

| Framework | Implementation Step | Effort | Stakeholder |
|-----------|-------------------|--------|-------------|
| **ICVCM CCP** | Provide continuous quality scores as a supplementary layer to CCP binary labels. Pilot with 2-3 CCP-approved methodology categories. | Medium | ICVCM Assessment Team |
| **Singapore ICC** | Propose as open-source complement to proprietary ratings panel. Demonstrate scoring reproducibility and transparency advantages. Submit to NEA competitive tender for future panel cycles. | Medium | NEA, MSE |
| **VCMI** | Develop quality-weighted retirement calculator for VCMI Claims Code. Publish quality distribution analysis of credits used for Silver/Gold/Platinum claims. | Low | VCMI Secretariat |

### 4.2 Medium-term (2027-2028): Regulatory standard proposals

| Framework | Implementation Step | Effort | Stakeholder |
|-----------|-------------------|--------|-------------|
| **CORSIA** | Submit framework to TAB for assessment as a quality differentiation tool within CORSIA-eligible programmes. Align grade thresholds with Phase 2 stricter EUC requirements. | High | ICAO TAB |
| **Article 6.4** | Propose Lemons Index as a pool-level quality metric for the Article 6.4 Supervisory Body. Demonstrate applicability to CDM-to-PACM transition quality monitoring. | Medium | UNFCCC SB |
| **EU CRCF** | Align removal type hierarchy with CRCF four-category structure. Propose within-category quality differentiation methodology for CRCF certification schemes. | Medium | European Commission DG CLIMA |

### 4.3 Long-term (2028-2030): Regulatory convergence

- **Cross-framework quality harmonisation**: Use the seven-dimension scoring as a common translation layer between CCP, CORSIA EUC, ICC, CRCF, and VCMI quality definitions. A credit scored under our framework can be assessed for eligibility across all six frameworks simultaneously.
- **On-chain regulatory reporting**: Integrate `meetsGrade()` into national registry APIs (not necessarily blockchain-based) to enable automated compliance checking. Singapore's digitalisation agenda and the EU's push for digital product passports create natural entry points.
- **Global quality rating standard**: Propose through UNFCCC or ISO as an open international standard for carbon credit quality assessment, building on the ISO 14065 verification standard.

---

## 5. Economic Impact Estimates

### Market size context

| Metric | Value | Source |
|--------|-------|-------|
| VCM value (2025) | $1.6-2.8 billion | Multiple market reports |
| VCM projected value (2030) | $10-50 billion | TSVCM, BloombergNEF, various |
| VCM projected value (2035) | ~$47.5 billion | Roots Analysis (2025) |
| CORSIA Phase 1 demand (2024-2026) | 146-236 million units | IATA (August 2025) |
| CORSIA Phase 2 annual demand (2027+) | 550-600 MtCO2/yr | IATA |
| CCP price premium | ~25% over non-CCP | ICVCM Impact Report (2025) |
| High-integrity vs. low-integrity price ratio | 4:1 | MSCI (2025) |
| Singapore carbon tax rate (2026+) | S$45/tCO2e | Singapore CPA 2022 |
| Singapore ICC offset allowance | 5% of taxable emissions | Singapore CPA 2022 |
| Credits committed to new generation (2025) | >$10 billion | Carbon Direct (2026) |

### Value at stake from quality differentiation

**1. Quality premium capture**: MSCI reports a 4:1 price ratio between high-integrity and low-integrity credits. If the VCM reaches $10 billion by 2030, the quality premium represents $7.5 billion in value differentiation (the difference between high-integrity pricing and a hypothetical single-price market). Transparent quality ratings that enable this differentiation capture a fraction of this value as infrastructure rent.

**2. Adverse selection cost avoidance**: Our Lemons Index analysis shows that unfiltered pools (BCT: LI=0.724) destroy approximately 72% of potential quality value. For a $10 billion market, adverse selection costs -- the value destroyed by quality opacity and mixing -- could reach $5-7 billion annually. Quality gating that reduces average LI from 0.51 (market baseline) to 0.30 (curated pool level) would recover an estimated $2-3 billion in quality value.

**3. CORSIA compliance market**: CORSIA Phase 2 demand of 550-600 MtCO2/yr at even modest prices ($10-20/tonne) represents a $5.5-12 billion annual compliance market. Quality-differentiated pricing within CORSIA-eligible credits -- enabled by our framework's continuous scoring -- could shift $1-3 billion annually from low-quality to high-quality supply, creating incentives for credit quality improvement.

**4. Singapore ICC market**: At S$45/tCO2e with 5% offset allowance, Singapore's ICC market represents approximately S$200-400 million annually (based on estimated taxable emissions of ~50 MtCO2e). Quality-differentiated offset pricing could improve the climate effectiveness of this market by directing offsets toward higher-quality credits.

**5. Insurance and financial products**: Carbon credit insurers (Oka, Howden, Lockton, WTW) require quality ratings as actuarial inputs. Our P(grade) posteriors directly enable probability-of-loss calculations. The carbon credit insurance market is nascent but projected to grow rapidly as compliance demand increases and credit invalidation risk becomes insurable.

**Total estimated value at stake (2030)**: $10-20 billion annually across all frameworks, representing the difference between a quality-opaque market (where adverse selection destroys value) and a quality-transparent market (where price discovery rewards integrity). Quality rating infrastructure captures 1-5% of this value as a public good (if open-source) or as service revenue (if operated commercially).

---

## References

1. ICVCM. Core Carbon Principles, Assessment Framework and Assessment Procedure, Version 3. ICVCM (May 2024). https://icvcm.org/assessment-framework/
2. UNFCCC. Decision 2/CMA.3: Guidance on cooperative approaches referred to in Article 6, paragraph 2. UNFCCC (2021). https://unfccc.int/sites/default/files/resource/cma3_auv_12a_PA_6.2.pdf
3. UNFCCC. Decision 3/CMA.3: Rules, modalities and procedures for the mechanism established by Article 6, paragraph 4. UNFCCC (2021). https://unfccc.int/documents/642812
4. UNFCCC. Decision -/CMA.4: Matters relating to cooperative approaches. UNFCCC (2022). https://unfccc.int/sites/default/files/resource/cma4_auv_cma13_PA6.2.pdf
5. ICAO. CORSIA Emissions Unit Eligibility Criteria, Document 09. ICAO. https://www.icao.int/CORSIA/corsia-eligible-emissions-units
6. ICAO. TAB Procedures Version 8.0 (January 2026). https://www.icao.int/sites/default/files/environmental-protection/CORSIA/TAB/2026/TAB_Procedures_v8_Jan2026.pdf
7. Singapore NEA. Carbon Rating Panel appointment: BeZero, Calyx, Sylvera for ICC Framework (November 2025). https://www.nea.gov.sg
8. Singapore MSE. Eligibility Criteria for International Carbon Credits under the Carbon Tax Regime. https://www.mse.gov.sg/latest-news/eligibility-criteria-for-internationalcarboncredits/
9. European Parliament and Council. Regulation (EU) 2024/3012 establishing a Union certification framework for permanent carbon removals, carbon farming and carbon storage in products (CRCF). EUR-Lex (2024). https://eur-lex.europa.eu/EN/legal-content/summary/establishing-a-union-certification-framework-for-permanent-carbon-removals-carbon-farming-and-carbon-storage-in-products.html
10. European Commission. Implementing Regulation (EU) 2025/2358 laying down technical rules on certification schemes, certification bodies, and audits (November 2025).
11. VCMI. Claims Code of Practice, updated August 2025. https://vcmintegrity.org/vcmi-claims-code-of-practice/
12. Columbia CGEP. Ahonen, P. et al. How to Fully Operationalize Article 6 of the Paris Agreement (2025). https://www.energypolicy.columbia.edu/publications/how-to-fully-operationalize-article-6-of-the-paris-agreement/
13. IATA. CORSIA Fact Sheet (December 2025). https://www.iata.org/en/iata-repository/pressroom/fact-sheets/fact-sheet-corsia/
14. Carbon Direct. Key Trends in the 2026 Voluntary Carbon Market (2026). https://www.carbon-direct.com/insights/key-trends-2026-voluntary-carbon-market
15. Perspectives Climate Group. Analysis of the ICVCM's core carbon principles and assessment framework (July 2024). https://perspectives.cc/wp-content/uploads/2024/07/PCG_CCPs-AF-analysis_07_2024.pdf
16. Fastmarkets. UNFCCC's Article 6.4 Supervisory Body approves first PACM methodology (2025). https://www.fastmarkets.com/insights/unfccs-article-6-4-supervisory-body-approves-first-pacm-methodology/
17. IISD. The Paris Agreement's New Article 6 Rules. https://www.iisd.org/articles/paris-agreement-article-6-rules
