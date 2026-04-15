# Paper A: Nature Sustainability — Full Article Outline

## Transparent Quality Rating Prevents Adverse Selection in Voluntary Carbon Markets

*Target: Nature Sustainability, Full Article*
*Main text: 3,000-5,000 words (excluding Methods, references, figure legends)*
*Methods: no word limit*
*Display items: up to 6 main figures/tables, up to 10 Extended Data items*

---

## Abstract (150 words max)

The voluntary carbon market (VCM) suffers from a quality crisis: fewer than 16% of credits represent real emission reductions (Calel et al. 2024), and price premiums of 4x for high-integrity credits (MSCI 2025) coexist with pools where 60% of eligible credits grade below standard quality. We present an open, multi-dimensional quality rating framework that scores individual carbon credits across seven dimensions, producing six-tier grades (AAA-B) with distributional uncertainty quantification. Validating against 318 credits, we find: (i) a 1.99-grade gap between CCP-eligible and non-CCP credits, matching independently measured gaps; (ii) rank correlation with commercial agencies (mean Spearman +0.343) exceeding their agreement with each other (+0.009); (iii) inter-rater reliability of kappa = 0.600 with ICC = 0.993. Implemented as a composable on-chain smart contract, the framework enables quality-gated pools that prevent the Toucan BCT-style adverse selection that collapsed the first generation of tokenized carbon markets. All code, data, and rubrics are open-source.

---

## 1. Introduction — The VCM quality crisis demands transparent infrastructure

**Word budget:** 800-1,000 words
**Key argument:** The VCM is failing at its primary purpose because quality is invisible. Three converging lines of evidence make the case urgent: empirical measurement of credit failure rates, price-premium evidence that markets will pay for quality, and a real-world failure case (Toucan BCT) that demonstrates the consequences.

**Key data points to cite:**
- <16% of credits represent real reductions across 2,346 projects and ~1 billion tCO2e (Calel et al., Nature Communications 2024)
- Offsets overestimate climate impact by 5-10x (Annual Review of Environment and Resources 2025)
- 87% of offsets purchased by the 20 largest buyers carry high risk of no real reductions (Trencher et al., Nature Communications 2024)
- ICVCM CCP-labelled credits command 25% price premium (ICVCM 2025)
- MSCI high-integrity index trades at 4x the low-integrity index, up from 2x in 2024 (MSCI 2025)
- Third-party auditors approved 95 projects that substantially overstated climate benefits (Coglianese & Giles, Science 2025)
- Singapore formally appointed BeZero, Calyx, Sylvera for Article 6 compliance quality assessment — the first sovereign mandate for carbon credit ratings (Singapore NEA 2025)

**Narrative arc:** Open with the $2B/year VCM paradox — money flowing in, climate impact not flowing out. Establish the three failure modes: (a) most credits are ineffective, (b) buyers cannot distinguish effective from ineffective, (c) existing quality infrastructure is proprietary and inconsistent. Introduce the Toucan BCT case as a microcosm. Close with the thesis: transparent, granular, composable quality infrastructure is the missing market mechanism.

**Display item:** None in this section (save budget for results).

---

## 2. Background — From Akerlof to carbon pools

**Word budget:** 600-800 words
**Key argument:** Adverse selection in the VCM is now formally modeled and empirically documented. The Toucan BCT collapse is the canonical case study. Existing quality infrastructure (commercial raters, CCP) is either binary, proprietary, or off-chain — none is composable with the emerging on-chain carbon market.

**Subsections:**

### 2.1 Adverse selection in VCMs
- Manshadi et al. (2025): first rigorous economic model showing market-for-lemons collapse when certification noise exceeds a threshold
- Berg et al. (2025): empirical evidence that buyers pay 2x for co-benefit narratives regardless of integrity — mispricing that quality rating should correct
- Battocletti et al. (2024): legal analysis of VCM market failures

### 2.2 The Toucan BCT failure
- Timeline: Oct 2021 launch, peak BCT at $8, quality degradation, Verra tokenization ban (May 2022), eventual collapse
- Root cause: fungibility trap (HFC-23 2009 credits treated identically to 2022 reforestation), no quality price discovery, information asymmetry, governance lag
- CarbonPlan analysis: 99.9% of BCT credits ineligible for CORSIA; 85% ineligible for Article 6
- Our retrospective: BCT composition was 60% grade-B by our scoring

### 2.3 Existing quality infrastructure
- ICVCM CCP: 36 methodologies approved, ~101M eligible credits, but binary (pass/fail)
- Commercial raters (BeZero, Calyx, Sylvera, MSCI): proprietary, inconsistent (CMW 2023 found same project rated high by Sylvera, low by Calyx/BeZero), none incorporate safeguards
- CCQI: open but methodology-level only, 1-5 scale, no on-chain implementation
- Gap: no system combines credit-level granularity, uncertainty quantification, and on-chain composability

**Display item:** None (background section).

---

## 3. Framework — Seven-dimension quality scoring with distributional uncertainty

**Word budget:** 800-1,000 words
**Key argument:** The framework scores individual credits across seven weighted dimensions using a linear composite with distributional uncertainty propagation, producing grades with posterior probabilities. A safeguards-gate mechanism prevents co-benefit narratives from inflating integrity grades.

**Subsections:**

### 3.1 Dimension design and weight calibration
- Seven dimensions: removal type (25%), additionality (20%), MRV grade (20%), permanence (17.5%), vintage (10%), co-benefits (0% safeguards-gate), registry/methodology (7.5%)
- Design grounded in Oxford Principles (removal hierarchy), CCQI (7 quality objectives), and ICVCM CCP (10 principles)
- Weights calibrated via stress-testing against 4 alternative mechanisms (methodology-gate-v0.4.md analysis)

### 3.2 Safeguards-gate mechanism
- Co-benefits removed from composite after six independent sources converged on the same conclusion: Berg et al. 2025, BeZero 2024 (31-61% SDG premium), Calyx 2025 (separate GHG/SDG scales), Sylvera 2025 (excludes co-benefits from integrity), Lou et al. 2023 (reputational purchasing), Oeko-Institut/Calyx 2024 (cookstove 9-10x overcrediting)
- Encoded as communityHarm disqualifier (caps at BBB) rather than scored dimension
- Preserves technical climate integrity while filtering for documented community/environmental harm

### 3.3 Distributional scoring and P(grade)
- Per-dimension standard deviations calibrated from empirical inter-rater data (sigma range 4.0-11.1)
- Composite variance propagated via Gaussian assumption
- Posterior P(grade) computed for each credit — first uncertainty quantification in any carbon rating system
- Enables honest reporting: Climeworks Orca AAA at P=96% vs. Charm Industrial AAA at P=57%

### 3.4 Seven disqualifier caps
- doubleCounting (B), failedVerification (B), humanRights (B), sanctionedRegistry (BB), noThirdParty (BBB), communityHarm (BBB), biodiversityHarm (BBB, per Zeng et al. 2026)

**Display item:**
- **Figure 1** — Framework architecture diagram: seven dimensions feeding into weighted composite, distributional uncertainty propagation, disqualifier lattice, grade assignment. Visual comparison with the Toucan BCT single-pool model and the proposed quality-tiered pool model. *(This is the "hero figure" — must be immediately comprehensible.)*

---

## 4. Results — Empirical validation across four studies

**Word budget:** 1,200-1,500 words (the core of the paper)
**Key argument:** The framework produces ratings that are empirically validated by four independent tests: CCP calibration, commercial agency correlation, inter-rater reliability, and adverse selection quantification.

### 4.1 CCP empirical calibration

**Key data points:**
- 1.99-grade gap between CCP-eligible (n=165) and non-CCP (n=153) credits
- Calyx Global's independently measured gap: ~2 grade levels (CCP average A vs. non-CCP average C)
- CCP-eligible credits cluster at A-AA; non-CCP credits cluster at BB-B
- The framework implicitly recovers the ICVCM's quality threshold without being trained on CCP labels

**Display item:**
- **Figure 2** — Violin or box plot: composite score distributions for CCP-eligible vs. non-CCP credits, with grade bands overlaid. The 1.99-grade separation should be visually striking.

### 4.2 Rank correlation with commercial agencies

**Key data points:**
- 6 REDD+ projects (CMW 2023 overlap): mean pairwise Spearman with commercial agencies +0.343 vs. inter-agency +0.009
- Cross-type extension (n=9, spanning CDR, biochar, cookstoves, IFM, methane, landfill gas, renewable energy): Spearman vs. BeZero +0.906, 5/9 exact grade matches
- Anchor points: BeZero's AAA for Climeworks Orca (our AAA, P=96%); BeZero's D/delisted for Kariba REDD+ (our B, 100% confidence)
- Systematic divergence on cookstoves: our framework caps avoidance at BBB while agencies rate at A-AA — a defensible design choice reflecting the Oxford Principles removal hierarchy

**Display item:**
- **Figure 3** — Heatmap or Spearman correlation matrix: our framework vs. BeZero, Calyx, Sylvera. Shows our position as a "compromise rater" that agrees more with each agency than they agree with each other.

### 4.3 Inter-rater reliability

**Key data points:**
- 3-model LLM panel (Claude Opus, Sonnet, Haiku), n=29 credits
- Grade-level Fleiss' kappa = 0.600 ("substantial" per Landis & Koch 1977)
- Composite ICC(2,k) = 0.993 ("near-perfect")
- Author vs. panel: 86% exact grade agreement, 100% within +/-1 band
- Per-dimension kappa: permanence highest (0.684), registry/methodology lowest (0.168) — targeted for rubric refinement
- Disqualifier recall: 12/12 (100%) on synthetic stress tests

**Display item:**
- **Figure 4** — Per-dimension Fleiss' kappa bar chart with 95% CIs, annotated with rubric-refinement actions. Combined with a confusion matrix of author grades vs. panel median grades.

### 4.4 Lemons Index: quantifying adverse selection in DeFi carbon pools

**Key data points:**
- Lemons Index definition: 1 minus (mean composite score / 100); higher = worse adverse selection
- Toucan BCT pool: Lemons Index 0.724 (average credit quality below 28/100)
- Toucan CHAR pool: Lemons Index 0.221 (biochar-only filter substantially reduces adverse selection)
- Hypothetical grade-A gated pool: Lemons Index ~0.10-0.15
- BCT at 31.1 composite (BB) sits only 1.1 points above the B boundary (P(BB) = 65%)
- No nature-based credit reaches AA in the tokenized sample — confirming the adverse selection dynamic

**Display item:**
- **Figure 5** — Lemons Index comparison across pool types (BCT, CHAR, NCT, hypothetical AAA pool, hypothetical AA pool, hypothetical A pool). This is the "killer figure" for the policy audience — it translates adverse selection from theory to a measurable, comparable metric.

### 4.5 Adversarial testing

**Key data points:**
- 5/5 adversarial credits correctly identified and graded appropriately
- Vectors tested: narrative washing, double counting, registry shopping, vintage arbitrage, biodiversity destruction
- Each adversarial credit was designed to maximize composite score while exploiting a specific failure mode

---

## 5. Discussion — Policy implications and market mechanism design

**Word budget:** 600-800 words
**Key argument:** Quality-gated pools are a concrete, deployable market mechanism that addresses adverse selection without requiring regulatory reform. The framework's open architecture enables multiple complementary use cases.

### 5.1 Quality-gated pools as market infrastructure
- The meetsGrade() interface enables automated quality enforcement at the protocol level — no governance vote needed
- Quality-tiered pricing: different grades earn different prices, restoring price discovery that fungible pools destroyed
- Insurance integration: P(grade) posteriors feed directly into actuarial underwriting for carbon credit invalidation insurance (Oka, Howden, Lockton, WTW)

### 5.2 Relationship to regulatory infrastructure
- CCP labeling is necessary but not sufficient (binary pass/fail misses the quality gradient above the threshold)
- Singapore's NEA appointment of commercial raters validates the regulatory need for quality assessment
- Framework can serve as granularity layer above CCP baseline — complementary, not competing

### 5.3 Normative assumptions (acknowledge explicitly)
- Removal > avoidance (Oxford Principles): consequential for cookstoves, REDD+
- Co-benefits excluded from integrity composite (safeguards-gate): supported by 6/6 sources but constrains "development-first" framing
- Additionality is assessable at the project level: counterfactuals are inherently unobservable (Coglianese & Giles 2025)
- Quality rating makes credits more useful, not more harmful: does not resolve the "offsets delay structural decarbonization" critique (Cheong 2025)

### 5.4 Limitations
- Weight calibration: not yet validated by domain expert panel (v0.6 expert consultation in progress with 20 identified reviewers)
- Credit coverage: 318 credits vs. 4,400+ at MSCI — resource-intensive gap
- LLM panel: single-provider (Anthropic); multi-provider replication needed to detect provider-specific biases
- Registry/methodology dimension: weakest IRR (kappa = 0.168); collapsed to 2-tier in v0.6

**Display item:**
- **Table 1** — Comparison matrix: this framework vs. CCQI, BeZero, Calyx, Sylvera, MSCI, CCP. Columns: credit-level scoring, composite weighted score, on-chain interface, uncertainty quantification, published IRR, quality-gated pools, open-source.

---

## 6. Conclusion

**Word budget:** 200-300 words
Close with the thesis restated as an evidence-backed claim. The VCM quality crisis is empirically documented, the adverse selection mechanism is formally modeled, and this framework provides the first transparent, composable, uncertainty-quantified quality infrastructure. Three verifiable claims of structural advantage. All code, data, and rubrics open-source under MIT license.

---

## Methods (separate section, no word limit)

### M1. Scoring methodology
- Seven dimensions with 0-100 rubric per dimension
- Weight calibration process: stress-testing against 4 alternative mechanisms (Rev-1+2, Alt-1 multiplicative, Alt-2 geometric mean, Alt-3 safeguards-gate)
- Linear weighted composite: Quality Score = sum(dimension_score_i * weight_i)
- Grade band assignment: AAA (90-100), AA (75-89), A (60-74), BBB (45-59), BB (30-44), B (<30)
- Disqualifier lattice: 7 flags with cap tiers

### M2. Safeguards-gate design
- Six-source literature convergence analysis
- Comparison against four alternative mechanisms
- Berg et al. (2025) framing: co-benefit narratives reinforce mispricing; removing them from composite corrects this

### M3. Distributional uncertainty propagation
- Per-dimension standard deviations from empirical LLM panel IRR (sigma values)
- Composite variance via linear propagation: Var(composite) = sum(w_i^2 * sigma_i^2)
- P(grade) via Gaussian CDF at grade boundaries

### M4. CCP empirical calibration
- ICVCM published list of 36 CCP-approved methodologies as classifier
- 318 credits classified as CCP-eligible (n=165) or non-CCP (n=153)
- Mean composite gap computed; grade-level gap = composite gap / grade band width (15 points)

### M5. Commercial agency rank correlation
- 6 REDD+ projects from CMW 2023 public dataset
- 9 cross-type projects with publicly available BeZero, Calyx, Sylvera ratings
- Grade ordinal mapping (AAA=8, AA=7, ... D=1) for Spearman rank correlation
- Pairwise Spearman rho computed for all pairs; mean reported

### M6. LLM panel inter-rater reliability
- 3 Claude models (Opus 4.6, Sonnet 4.6, Haiku 4.5)
- Independent scoring against v0.4.1 rubric with redacted evidence packs (author scores removed)
- Fleiss' kappa computed at the grade level (6 categories)
- ICC(2,k) computed on continuous composite scores (0-100)
- Per-dimension kappa breakdown

### M7. Lemons Index computation
- Definition: L(pool) = 1 - (mean composite score of pool credits / 100)
- Applied to BCT (reconstructed from project-type composition), CHAR (from allowlist), and hypothetical gated pools

### M8. Adversarial testing protocol
- 5 synthetic credits designed to maximize composite score while exploiting: narrative washing, double counting, registry shopping, vintage arbitrage, biodiversity destruction
- Each scored by framework and independently by LLM panel
- Pass criterion: correct grade cap applied or correct low score assigned

### M9. On-chain implementation
- Solidity reference implementation: CarbonCreditRating.sol (Level 2 ICCQR compliant)
- meetsGrade() view function: zero-gas quality gating primitive
- QualityGatedPool.sol: deposit requires meetsGrade(credit, tokenId, minGrade) = true
- EAS adapter: relay attestations from trusted attester registry
- Composability demos: KlimaRetirementGate.sol, CHARQualityOverlay.sol
- All contracts on Foundry with 14+ passing tests
- Deployment target: Base (same chain as Toucan CHAR, Klima Protocol 2.0)

---

## Figure and Table Plan

### Main display items (6 max)

| # | Type | Title | Content | Section |
|---|------|-------|---------|---------|
| Fig 1 | Schematic | Framework architecture and quality-tiered pool model | 7 dimensions -> composite -> grade with P(grade). Visual comparison: BCT single-pool vs. quality-tiered pools. Include meetsGrade() interface. | 3 |
| Fig 2 | Violin/box plot | CCP empirical calibration | Composite distributions for CCP-eligible vs. non-CCP credits. 1.99-grade gap. Grade bands overlaid as horizontal lines. | 4.1 |
| Fig 3 | Heatmap | Rank correlation with commercial agencies | Spearman correlation matrix (ours + BeZero + Calyx + Sylvera). Our position as "compromise rater." Annotate BeZero-Calyx anti-correlation. | 4.2 |
| Fig 4 | Bar chart + confusion matrix | Inter-rater reliability by dimension | Per-dimension Fleiss' kappa with 95% CIs + author vs. panel grade confusion matrix. Flag weakest dimensions. | 4.3 |
| Fig 5 | Bar chart | Lemons Index across pool types | BCT (0.724), CHAR (0.221), NCT, and hypothetical gated pools. The visual "proof" that quality gating works. | 4.4 |
| Table 1 | Comparison matrix | Framework vs. existing quality infrastructure | This framework, CCQI, BeZero, Calyx, Sylvera, MSCI, CCP across 7 capability dimensions. | 5 |

### Extended Data items (10 max)

| # | Type | Title | Content |
|---|------|-------|---------|
| ED1 | Table | Full scoring rubric: all 7 dimensions with band definitions | Complete rubric for reproducibility |
| ED2 | Table | 29-credit illustrative pilot: per-dimension scores, composites, grades | Full pilot dataset |
| ED3 | Table | 16-credit tokenized pilot: per-dimension scores, composites, grades, P(grade) | On-chain credit scoring |
| ED4 | Figure | Weight sensitivity analysis: +/-5pp perturbation and leave-one-out | Heat map of grade flips per perturbation |
| ED5 | Table | Cross-type rank correlation detail: 9 projects, our grades vs. BeZero/Calyx/Sylvera | Per-project comparison |
| ED6 | Figure | Distributional scoring posteriors for 6 load-bearing credits | P(grade) distributions showing fragile vs. stable grades |
| ED7 | Table | Disqualifier stress test results: C026-C029 + 5 adversarial credits | Cap tier verification |
| ED8 | Figure | Methodology-gate decision analysis: 4 alternatives compared on 5 criteria | How safeguards-gate won |
| ED9 | Table | LLM panel raw outputs: all 29 credits x 3 models x 7 dimensions | Full IRR reproducibility dataset |
| ED10 | Figure | Toucan BCT timeline and quality degradation reconstruction | Annotated timeline with credit-type composition changes |

---

## Supplementary Information

### SI-1: Solidity smart contract specifications
- Full ICCQR interface (Level 1, 2, 3)
- Gas benchmarks for setRating, meetsGrade, batch operations
- Foundry test results (14+ tests)

### SI-2: ERC-CCQR standard proposal
- Full specification from docs/erc-ccqr.md
- Rationale for meetsGrade() as core primitive
- Security considerations

### SI-3: Complete reference list (95+ sources)
- All references cited in main text, methods, and extended data

### SI-4: Normative assumption sensitivity analysis
- Framework outputs under alternative normative assumptions (co-benefits restored, removal hierarchy flattened, etc.)

### SI-5: Decentralized rater architecture design
- Four options compared: EAS, UMA optimistic oracle, multi-rater quorum, registry-attester-with-dispute
- EAS selected, with Hypercerts evaluator registry as implementation precedent

---

## Reference Strategy

### Priority references for main text (~50 target)

**Must-cite (foundational to our claims):**
1. Akerlof 1970 — Market for Lemons (theoretical foundation)
2. Calel et al. 2024 — <16% real reductions (Nature Communications)
3. Annual Review 2025 — 5-10x overestimate
4. Trencher et al. 2024 — 87% low-quality offsets by major buyers (Nature Communications)
5. Manshadi et al. 2025 — Adverse selection formal model (SSRN/ACM EC)
6. Berg et al. 2025 — Co-benefit narrative premium (SSRN)
7. Coglianese & Giles 2025 — Auditors can't save offsets (Science)
8. Allen et al. 2020 — Oxford Principles
9. ICVCM 2023, 2025 — CCP framework and impact report
10. MSCI 2025 — 4x integrity premium
11. CMW 2023 — Inter-agency rating disagreement
12. CCQI 2024 — Open quality framework
13. Zeng et al. 2026 — Biodiversity tradeoffs (Nature Reviews Biodiversity)
14. Landis & Koch 1977 — Kappa interpretation benchmarks

**On-chain and DeFi (critical for mechanism contribution):**
15. Zhou et al. 2023 — Nori NFT model, buyer clustering (IEEE Wireless Comm)
16. Gao & Liu 2026 — CATchain-R (npj Climate Action)
17. Jaffer et al. 2024 — PACT stablecoin (IEEE ICBC)
18. JPMorgan Kinexys 2025 — Registry-layer tokenization
19. Jirasek 2023 — KlimaDAO analysis (Springer)
20. Frontiers in Blockchain 2024 — KlimaDAO tokenized credits
21. Finance and Space 2024 — Blockchain financialization critique

**Commercial raters (validation comparators):**
22. Sylvera 2025 — State of Carbon Credits
23. BeZero 2023, 2024 — Methodology, safeguards, SDG premium
24. Calyx Global 2024, 2025 — Ratings, CCP correlation
25. Calyx/Oeko-Institut 2024 — Cookstove overcrediting

**Additional quality/market context:**
26. Battocletti et al. 2024 — VCM market failures (Colorado Law Review)
27. West et al. 2023, 2025 — REDD+ baseline inflation (Science, Global Change Biology)
28. Garcia & Sanford 2026 — Jurisdictional REDD+ strategic behavior (PNAS)
29. Cabiyo & Field 2025 — Overcrediting risk and insurance (PNAS Nexus)
30. Cheong 2025 — Carbon credit paradox (Anthropocene Science)
31. Lou et al. 2023 — Corporate co-benefit purchasing motivations (npj Climate Action)
32. Singapore NEA 2025 — Sovereign rating mandate
33. Liu 2025 — Carbon inequality and price discovery (WFE/SSRN)
34. Gold Standard + ATEC 2025 — Digital MRV on Hedera

**Technical/methods:**
35. Huber et al. 2024 — 15-criteria meta-analysis (J Environmental Management)
36. NUS SGFIN 2024 — 9-principle program evaluation
37. Nguyen 2025 — Neutrosophic Delphi-DEMATEL
38. Carbon Direct/Microsoft 2025 — CDR criteria
39. Bosshard et al. 2025 — Blockchain VCM network structure (Frontiers in Blockchain)
40. Verra 2023, 2026 — VCS guidelines, DMRV pilot

**Registry/standards:**
41. Toucan Protocol docs, Toucan CHAR pool
42. Klima Protocol 2.0 (kVCM/K2)
43. Hypercerts Foundation / GainForest Ecocerts 2025
44. Rainbow Standard
45. Isometric
46. CarbonPlan OffsetsDB
47. Renoster Mercury Rubric

**Remaining slots (48-50):** Reserve for peer review additions or referee-suggested citations.

---

## Author Contribution Statement Template

A.W. conceived and designed the framework, developed the scoring methodology, implemented the smart contracts and Python scorer, conducted the pilot scoring studies, designed and executed the LLM panel inter-rater reliability study, performed the commercial agency rank correlation analysis, computed the Lemons Index, wrote the ERC-CCQR standard proposal, and wrote the manuscript. [Additional co-authors as applicable for expert consultation, DeFi integration testing, multi-provider LLM replication.]

---

## Data Availability Statement

All data supporting the findings of this study are available in the project's GitHub repository at https://github.com/Adeline117/carbon-neutrality under the MIT license. This includes: scoring rubrics as machine-readable JSON (data/scoring-rubrics/), pilot credit datasets with per-dimension scores (data/pilot-scoring/, data/tokenized-pilot/), LLM panel raw outputs (data/llm-panel-irr/), rank correlation datasets (data/rank-correlation/), the Python scoring engine (data/pilot-scoring/score.py), and the Solidity reference implementation (contracts/). The ERC-CCQR standard specification is available at docs/erc-ccqr.md. No proprietary data was used.

---

## Code Availability Statement

The Solidity smart contracts (CarbonCreditRating.sol, QualityGatedPool.sol, CarbonCreditRatingEASAdapter.sol, and composability demonstrations) are available at https://github.com/Adeline117/carbon-neutrality/contracts/ under the MIT license. The Python scoring engine and analysis scripts are available at https://github.com/Adeline117/carbon-neutrality/data/. All code has been tested with Foundry (Solidity) and Python 3.10+.

---

## Target Editors and Reviewers

### Recommended editors at Nature Sustainability:
- **Monica Contestabile** (Chief Editor) — market mechanisms and policy
- **Ryan Scarrow** or **Aisha Bradshaw** — environmental economics and governance

### Suggested reviewers (non-conflicted):
1. **Vahideh Manshadi** (Yale) — Adverse selection model we build on; deepest understanding of certification noise threshold
2. **Danny Cullenward** (UPenn/CarbonPlan) — Open-source carbon quality analysis; will rigorously test claims
3. **Gregory Trencher** (Kyoto University) — Corporate offset purchasing behavior; demand-side validation
4. **Thales West** (VU Amsterdam) — REDD+ baseline integrity; our BCT/MCO2 scores depend on his work
5. **H. Oliver Gao** (Cornell) — CATchain-R comparison; on-chain credibility index

### Reviewers to exclude (conflict of interest):
- Staff at BeZero, Calyx Global, Sylvera, MSCI (their ratings are our comparators)
- Toucan Protocol / KlimaDAO team members (BCT is our failure case study)

---

## Pre-submission Checklist

- [ ] Expert consultation completed (20 identified reviewers)
- [ ] Multi-provider LLM replication (GPT-5, Gemini, DeepSeek) to address single-provider bias
- [ ] Credit dataset expanded from 318 to 500+ for statistical power
- [ ] Base Sepolia deployment live with public demo
- [ ] arXiv preprint posted for community feedback
- [ ] Lemons Index computation expanded to cover full BCT historical composition (not just archetypes)
- [ ] Cookstove divergence with commercial raters discussed with at least 2 domain experts
- [ ] Weight sensitivity analysis includes expert-elicited alternative weight vectors

---

## Narrative Arc Summary

1. **Hook** (Introduction): The VCM is a $2B/year market where <16% of credits work. Transparent quality infrastructure is the missing market mechanism.
2. **Theory** (Background): Adverse selection is formally modeled (Manshadi). The Toucan BCT collapse is the empirical proof. Existing infrastructure is binary, proprietary, or off-chain.
3. **Solution** (Framework): Seven-dimension scoring with safeguards-gate and distributional uncertainty. First system to publish P(grade). Implemented on-chain with composable meetsGrade() interface.
4. **Evidence** (Results): CCP calibration (1.99-grade gap matches independently). Commercial correlation (+0.343 > +0.009). IRR (kappa=0.600). Lemons Index (BCT 0.724 vs. CHAR 0.221). Adversarial resistance (5/5).
5. **Implications** (Discussion): Quality-gated pools prevent BCT-style collapse. Insurance integration via P(grade). Complementary to CCP, not competing. Normative assumptions acknowledged.
6. **Call to action** (Conclusion): Open-source, on-chain, uncertainty-quantified quality infrastructure is deployable today. The VCM can be fixed — but only if quality is transparent.
