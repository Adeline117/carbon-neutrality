# Toward a Standardized Quality Rating for On-Chain Carbon Credits

*Workshop Paper -- Draft v0.3*

**Changelog vs v0.2**
- Added Section 7 ("Pilot Scoring Results") summarizing a 25-credit hand-scored stress test of the rubrics. Moved subsequent sections down accordingly.
- Fixed duplicate Section 8 numbering (Limitations / Next Steps now Sections 9 / 10).
- Section 4 now references the machine-readable rubrics under `data/scoring-rubrics/`.
- Section 5.3 now points to the working Solidity prototype under `contracts/` instead of the sketched interface.
- Section 9 (Limitations) adds the "no AAA under current weights" finding surfaced by the pilot.

## Abstract

Tokenized carbon credit markets suffer from a quality indistinguishability problem. When credits of varying integrity are pooled into fungible on-chain instruments, adverse selection drives out high-quality supply and erodes buyer trust -- a dynamic formally modeled as a "market for lemons" (Manshadi et al. 2025). Recent empirical evidence shows that less than 16% of carbon credits represent real emission reductions (Nature Communications 2024), and 87% of offsets purchased by major companies carry high risk of no real climate impact (Trencher et al. 2024). Meanwhile, existing commercial rating agencies (Sylvera, BeZero, Calyx Global) produce inconsistent ratings for the same projects and operate as opaque, centralized entities incompatible with DeFi composability. This paper proposes a multi-dimensional quality rating framework designed for on-chain implementation, drawing on established integrity standards (ICVCM CCP, Oxford Principles, Verra VCS), lessons from Toucan Protocol's failure and Nori's NFT-based model (Zhou et al. 2023), and the emerging CCQI methodology. We define seven candidate rating dimensions, propose a scoring methodology, and outline a path toward expert validation.

## 1. Introduction

### 1.1 The Tokenized Carbon Market

The voluntary carbon market (VCM) has seen significant growth, reaching approximately $2B in 2023. Blockchain-based platforms emerged to bring transparency, liquidity, and composability to carbon credits by tokenizing verified offsets from registries like Verra and Gold Standard. However, recent systematic assessments paint a sobering picture: a Nature Communications (2024) meta-analysis of 2,346 projects covering ~1 billion tCO2e found that **less than 16% of carbon credits constitute real emission reductions** -- with cookstoves at 11%, REDD+ at 25%, and wind power showing no statistically significant reductions at all. The Annual Review of Environment and Resources (2025) concluded that most offset programs overestimate climate impact by **5-10x or more**.

### 1.2 The Pooling Problem

Toucan Protocol pioneered the bridging of Verra VCUs onto Polygon as tokenized credits (TCO2), then aggregated them into the Base Carbon Tonne (BCT) pool. BCT treated all eligible credits as fungible, regardless of:
- Whether the credit represented actual carbon removal or merely avoided emissions
- The rigor of the monitoring and verification process
- The permanence of the underlying carbon storage
- The vintage (age) of the credit

This created a classic "lemons problem" (Akerlof 1970): sellers deposited their lowest-quality eligible credits into BCT (since they received the same price as high-quality credits), while high-quality credit holders withheld supply. The pool's effective quality -- and market confidence -- degraded over time.

### 1.3 The Need for On-Chain Quality Differentiation

Off-chain rating agencies (Sylvera, BeZero, Calyx Global) have developed proprietary rating methodologies, but these are:
- **Opaque**: Detailed scoring criteria are not public
- **Centralized**: Single-entity assessments with limited appeal mechanisms
- **Off-chain**: Not natively composable with DeFi protocols

An open, transparent, on-chain rating standard could enable quality-tiered pools, automated quality gates in protocols, and buyer-driven quality preferences -- all without relying on a single centralized assessor.

Notably, not all on-chain carbon models suffered Toucan's fate. Zhou et al. (2023) analyzed Nori, an NFT-based voluntary carbon market on Polygon, where each credit is a unique, non-fungible NRT (Nori Removal Tonne). This per-credit identity inherently prevents the mixing problem. Their buyer clustering analysis (SOM) revealed that while 87.9% of buyers are experiential (one-time, small purchases), the 4% of institutional buyers drive 58.3% of transaction volume -- precisely the segment that would most benefit from quality-gated infrastructure. Their Granger causality analysis also showed Nori's market is driven primarily by public opinion rather than crypto cycles, suggesting genuine sustainability utility rather than speculation.

The economic case for quality differentiation is now well-established: ICVCM CCP-labelled credits command a **25% price premium** (ICVCM 2025), and MSCI's high-integrity index trades at **4x** the level of its low-integrity index (MSCI 2025). The market clearly pays for verified quality.

## 2. Existing Frameworks

### 2.1 ICVCM Core Carbon Principles (CCP)

The Integrity Council for the Voluntary Carbon Market established 10 Core Carbon Principles:

1. Effective governance
2. Tracking
3. Transparency
4. Robust independent third-party validation and verification
5. Additionality
6. Permanence
7. Robust quantification of emission reductions and removals
8. No double counting
9. Sustainable development benefits and safeguards
10. Contribution toward net zero transition

CCP provides a binary threshold (meets/does not meet) rather than a granular quality spectrum. Our framework builds on CCP as a baseline, adding granularity.

### 2.2 Oxford Principles for Net Zero Aligned Carbon Offsetting

Key contribution: the **removal hierarchy**:
1. Emissions reductions with long-lived storage (highest)
2. Emissions removals with long-lived storage
3. Emissions reductions with short-lived storage
4. Emissions removals with short-lived storage
5. Emissions reductions (avoidance) (lowest among quality offsets)

The Oxford Principles also emphasize shifting purchasing toward removal over time, and the importance of permanence.

### 2.3 Verra Verified Carbon Standard (VCS)

Verra is the largest voluntary market registry by volume. VCS provides:
- Approved methodologies per project type
- Validation/verification body accreditation
- Buffer pool mechanisms for permanence risk (AFOLU projects)
- Vintage tracking

VCS methodology quality varies significantly -- some methodologies have been criticized (e.g., REDD+ baseline inflation), while others are considered rigorous.

### 2.4 Carbon Credit Quality Initiative (CCQI)

A collaborative effort by Environmental Defense Fund, WWF-US, and Oeko-Institut. Uses 7 quality objectives scored 1-5 by independent domain experts. The methodology is public and the scoring tool is free -- the closest existing precedent to an open quality standard. CCQI evaluates at the *methodology* level rather than individual projects, which limits granularity but improves scalability.

### 2.5 Commercial Ratings

| Agency | Scale | Approach | Public? |
|--------|-------|----------|---------|
| Sylvera | AAA to D | ML-based remote sensing + expert review (1,500-2,500 hrs per framework) | No |
| BeZero | AAA to D (8-point) | 6 risk factors: additionality, over-crediting, non-permanence, leakage, perverse incentives, policy | Ratings public, methodology proprietary |
| Calyx Global | Risk-based | Three-tier (program/methodology/project); additive scoring; peer-reviewed | Partially |
| MSCI | AAA to CCC | 4,400+ projects assessed; <10% rated AAA-A | Report public, methodology proprietary |

**Critical finding**: A 2023 Carbon Market Watch study found significant inter-rater disagreement -- the same Amazon REDD+ project received high ratings from Sylvera but low ratings from Calyx and BeZero. None of the four agencies incorporate safeguards for local community impacts. This inconsistency undermines buyer confidence and strengthens the case for an open, reproducible methodology.

### 2.6 Frontier On-Chain Approaches

Two recent academic proposals are particularly relevant:

**CATchain-R** (Gao & Liu, Cornell, npj Climate Action 2026): A blockchain-based carbon registry with a "carbon credibility index" that compares organizations' reduction goals vs. achievements. Rates *organization* credibility rather than individual credits.

**PACT Stablecoin** (Jaffer et al., Cambridge, IEEE ICBC 2024): Combines remote sensing + econometric baselines + on-chain certification on Tezos. Permits attribute-preserving pools (by co-benefit, jurisdiction) while maintaining fungibility within each pool.

**JPMorgan Kinexys** (2025): Registry-layer tokenization (credits tokenized at issuance via API, not bridged after the fact). Partners with S&P Global, EcoRegistry. Solves the provenance gap that undermined Toucan.

## 3. Proposed Rating Dimensions

### 3.1 Removal Type Hierarchy (Weight: 20%)

Based on Oxford Principles, scoring the fundamental nature of the climate intervention:

| Score | Category | Examples |
|-------|----------|----------|
| 95-100 | Engineered removal + durable storage | DACCS, enhanced weathering with mineralization |
| 80-94 | Nature-based removal + long storage | Biochar, afforestation (>100yr commitment) |
| 65-79 | Engineered avoidance | Industrial process change, CCS on point source |
| 50-64 | Nature-based removal + short storage | Soil carbon, mangrove restoration |
| 35-49 | Avoidance / reduction | Renewable energy displacement, cookstoves |
| 20-34 | Avoidance with measurement uncertainty | REDD+ (avoided deforestation) |

### 3.2 Additionality (Weight: 20%)

Assessing whether the emission reduction/removal would have occurred without carbon finance:

| Score | Level | Criteria |
|-------|-------|---------|
| 90-100 | Very High | Activity is financially unviable without carbon revenue; clear regulatory surplus; no alternative funding |
| 70-89 | High | Carbon revenue is a significant income stream (>30% of project revenue); passes barrier analysis |
| 50-69 | Moderate | Carbon revenue is material but project has other revenue streams; common practice analysis supports additionality |
| 30-49 | Low | Project type is becoming common practice; additionality argument relies primarily on barrier analysis |
| 0-29 | Questionable | Project type is standard practice in jurisdiction; regulatory requirements may mandate similar activities |

### 3.3 Permanence (Weight: 15%)

Duration and security of carbon storage:

| Score | Duration | Risk Profile |
|-------|----------|-------------|
| 90-100 | >10,000 years (geological) | Mineralization, geological storage, DACCS |
| 70-89 | >1,000 years | Biochar, enhanced weathering |
| 50-69 | 100-1,000 years | Well-managed forestry with legal protections, building materials |
| 30-49 | 25-100 years | Forestry with buffer pool, soil carbon with monitoring |
| 10-29 | <25 years | Short rotation forestry, agriculture without long-term commitment |
| 0-9 | Impermanent | No storage claim (pure avoidance) |

### 3.4 MRV Grade (Weight: 15%)

Quality of Monitoring, Reporting, and Verification:

| Score | Level | Characteristics |
|-------|-------|----------------|
| 90-100 | Digital MRV | Continuous sensor monitoring, satellite verification, automated reporting, third-party audited data pipeline |
| 70-89 | Enhanced traditional | Regular third-party verification, remote sensing cross-checks, quantified uncertainty bounds |
| 50-69 | Standard | Periodic third-party verification per registry requirements, standard uncertainty factors |
| 30-49 | Basic | Minimum registry requirements met, limited independent verification, high reliance on self-reporting |
| 0-29 | Deficient | Known MRV gaps, unresolved audit findings, methodology-level concerns |

### 3.5 Vintage Year (Weight: 10%)

Recency of the emission reduction/removal:

| Score | Vintage | Rationale |
|-------|---------|-----------|
| 90-100 | Current year or year-1 | Fresh credits; reflects current project performance |
| 70-89 | 2-3 years old | Reasonably recent |
| 50-69 | 4-5 years old | Aging but still representative |
| 30-49 | 6-10 years old | May not reflect current project status |
| 0-29 | >10 years old | Stale; project conditions may have changed significantly |

### 3.6 Co-benefits (Weight: 10%)

Contribution to Sustainable Development Goals beyond climate:

| Score | Level | Criteria |
|-------|-------|---------|
| 90-100 | Verified high impact | Third-party verified SDG contributions (e.g., SD VISta, Gold Standard SDG impact); >=3 SDGs with quantified metrics |
| 60-89 | Moderate verified | 1-2 verified SDG contributions with quantified metrics |
| 30-59 | Self-reported | Project claims SDG contributions without independent verification |
| 0-29 | Minimal | No significant co-benefits identified or claimed |

### 3.7 Registry & Methodology (Weight: 10%)

Assessing the rigor of the crediting program and specific methodology:

| Score | Level | Criteria |
|-------|-------|---------|
| 90-100 | Gold standard | ICVCM CCP-approved program + CCP-eligible methodology category |
| 70-89 | High rigor | Major registry (Verra VCS, Gold Standard, ACR, CAR) + well-regarded methodology with conservative baselines |
| 50-69 | Standard | Major registry + methodology without known integrity concerns |
| 30-49 | Concerns | Major registry but methodology has been subject to criticism or revision for integrity issues |
| 0-29 | Low confidence | Minor or unrecognized registry; methodology not widely accepted |

## 4. Scoring Methodology

### 4.1 Weighted Composite Score

```
Quality Score = sum(dimension_score_i * weight_i) for i in dimensions
```

All dimension scores normalized to 0-100. Weights as defined above (summing to 100%).

The weights, grade bands, adjustment factors, and disqualifiers are maintained as machine-readable JSON under `data/scoring-rubrics/` (one file per dimension plus an `index.json`) so that the pilot scoring script, the Solidity reference contract, and any third-party implementer all consume the same source of truth.

### 4.2 Grade Assignment

| Grade | Score Range | Market Implication |
|-------|------------|-------------------|
| AAA | 90-100 | Premium pool eligible; suitable for corporate net-zero claims under SBTi |
| AA | 75-89 | High-quality pool; suitable for most compliance-adjacent and voluntary claims |
| A | 60-74 | Standard quality; meets baseline integrity expectations |
| BBB | 45-59 | Acceptable for portfolio diversification; not suitable for primary offset claims |
| BB | 30-44 | Below standard; significant discount expected |
| B | <30 | Not recommended; integrity concerns |

### 4.3 Disqualifiers

Certain findings should cap the maximum achievable grade regardless of composite score:
- **Double counting evidence**: Capped at B
- **Failed validation/verification**: Capped at B
- **Sanctioned registry or methodology**: Capped at BB
- **No third-party verification**: Capped at BBB

## 5. On-Chain Implementation Considerations

### 5.1 Data Availability

The primary challenge is making rating inputs available on-chain:
- **On-chain native**: Vintage year, registry, methodology ID (from tokenization metadata)
- **Oracle-dependent**: Additionality assessment, MRV grade, co-benefits (require off-chain evaluation)
- **Hybrid**: Removal type can be derived from methodology category mapping

### 5.2 Architecture Options

**Option A: Oracle-Attested Ratings**
- Off-chain rating calculation, on-chain attestation via oracle network
- Pro: Full methodology flexibility; Con: Centralization risk

**Option B: On-Chain Rule Engine**
- Scoring logic in smart contract; inputs from attestation layer
- Pro: Transparent, auditable; Con: Limited to quantifiable dimensions

**Option C: Hybrid**
- Core dimensions (removal type, vintage, registry) scored on-chain
- Complex dimensions (additionality, MRV) attested via decentralized oracle with dispute mechanism
- Recommended approach

### 5.3 Smart Contract Prototype

A working reference implementation lives under `contracts/`:

- `ICarbonCreditRating.sol` -- interface + shared types (`Grade` enum, `DimensionScores`, `Disqualifiers`, `Rating`).
- `CarbonCreditRating.sol` -- storage + scoring logic. Composite is computed in basis points (`composite_bps = sum(score_i * weight_bps_i) / 100`) using the v0.2 weights from `data/scoring-rubrics/index.json`. Grade bands and disqualifier caps mirror the rubric exactly.
- `QualityGatedPool.sol` -- minimal ERC-20-like pool that only accepts deposits of rated credits whose `finalGrade >= minGrade`, directly implementing the "quality-tiered pool" remedy to Toucan's BCT failure.
- `test/CarbonCreditRating.t.sol` -- 5 Foundry tests covering composite calculation (cross-checked against the Python pilot scorer), nominal-to-final grade mapping, disqualifier caps, unrated-is-ineligible, and the full set-then-read path.

Key excerpt -- the composite math is intentionally deterministic and consumable by any off-chain implementer:

```solidity
// CarbonCreditRating.sol (abbreviated)
uint256 sum =
      uint256(s.removalType)         * 2000    // 20%
    + uint256(s.additionality)       * 2000    // 20%
    + uint256(s.permanence)          * 1500    // 15%
    + uint256(s.mrvGrade)            * 1500    // 15%
    + uint256(s.vintageYear)         * 1000    // 10%
    + uint256(s.coBenefits)          * 1000    // 10%
    + uint256(s.registryMethodology) * 1000;   // 10%
return uint16(sum / 100); // 0-10000 bps, matches off-chain scorer exactly
```

The contract uses a single-owner rater role as a placeholder. A production deployment would replace this with a decentralized attestation network (EAS, optimistic oracle, or multi-rater quorum) -- this is the main open governance question discussed in Section 9.

## 6. Comparison with Toucan's Approach

| Aspect | Toucan BCT | This Framework |
|--------|-----------|----------------|
| Quality differentiation | None (single pool) | 6-tier grading |
| Scoring dimensions | N/A | 7 weighted dimensions |
| Transparency | Pool eligibility rules only | Full scoring methodology public |
| On-chain logic | Bridge + pool | Rating + quality-gated pools |
| Adverse selection mitigation | None | Grade-specific pools prevent mixing |

## 7. Pilot Scoring Results

To stress-test the v0.2 weights before expert consultation, we hand-scored 25 illustrative credits spanning the full quality spectrum using the machine-readable rubrics. Full data and the Python scorer are in `data/pilot-scoring/`. This is a methodology validation, not a formal rating of the named projects.

### 7.1 Distribution

| Grade | Count | Share | Score range |
|-------|-------|-------|-------------|
| AAA   | 0     | 0%    | —           |
| AA    | 7     | 28%   | 75.7 – 86.8 |
| A     | 4     | 16%   | 63.3 – 70.5 |
| BBB   | 4     | 16%   | 50.9 – 56.5 |
| BB    | 3     | 12%   | 31.2 – 38.4 |
| B     | 7     | 28%   | 15.4 – 29.3 |

Reference: MSCI's 2025 Integrity Report rated fewer than 10% of 4,400+ projects AAA-A. Our pilot is spectrum-sampled rather than VCM-representative, so the absolute shares are not directly comparable.

### 7.2 Key findings

**Finding 1 -- No credit reached AAA; the co-benefits weight compresses engineered removal.** Climeworks Orca scored 86.8, 3.2 points below the AAA threshold. Inspection revealed the binding constraint: pure-CDR projects score ~15-22 on co-benefits (industrial, no direct SDG alignment) while that dimension carries a 10% weight, costing them roughly 7-8 composite points. Under the current weighting it is mathematically difficult for any engineered-removal credit to reach AAA, which inverts the Oxford Principles. Three revisions are under consideration for v0.4, listed in Section 9.

**Finding 2 -- BCT pool composition in retrospect.** Of the 25 credits, 10 are tagged as historically BCT-eligible. Six graded B, two graded BB, and only two graded A or above. Had a grade-gated pool at minimum grade A existed, the BCT pool would have admitted only 2 of these 10 credits, directly neutralizing the adverse selection dynamic that drove BCT's collapse.

**Finding 3 -- Disqualifiers are currently backstops only.** Every flagged credit in the pilot already scored low enough on composite alone to land at B; no high-composite credit was capped by a disqualifier in the dataset. This is defensible (disqualifiers are an edge-case safety net for catastrophic failures of otherwise high-quality credits) but should be validated with a synthetic stress test added to the pilot dataset in v0.4.

**Finding 4 -- Latent collinearity between removal type and permanence.** The two dimensions correlate strongly in this dataset (both track Oxford hierarchy). Expert review should confirm whether both are warranted or whether they should be collapsed into a single "Durability" dimension.

### 7.3 Revisions proposed for v0.4

Based on the pilot findings:

1. **Reweight** toward technical dimensions: `removal_type` 0.20 → 0.225, `mrv_grade` 0.15 → 0.175, `co_benefits` 0.10 → 0.075, `registry_methodology` 0.10 → 0.075.
2. **Removal bonus**: +5 composite (capped at 100) if `removal_type >= 90 AND permanence >= 90 AND mrv_grade >= 85`, preserving Oxford hierarchy at the top of the scale.
3. **Add a disqualifier stress test case** (synthetic high-composite credit with `double_counting`) to the pilot dataset so interaction with the grade-cap logic is demonstrated end-to-end.
4. **Do not change grade band boundaries** (the current 90/75/60/45/30 split produced a defensible distribution).

The author's prior is to adopt revisions 1-3 by default and gather expert input on 4.

## 8. Adverse Selection: Formal Justification

Manshadi, Monachou, and Morgenstern (2025) provide the first rigorous economic model of adverse selection in the VCM:
- High-quality projects are costlier but indistinguishable from low-quality without certification
- When **certification noise exceeds a threshold**, a market-for-lemons collapse occurs (no trade)
- Interventions targeting only demand or supply side can actually **reduce** climate benefit without certification improvements

This formally validates our framework's core premise: reducing certification noise through granular, transparent, multi-dimensional scoring is *necessary* to prevent market collapse. A binary (pass/fail) certification is insufficient -- the noise threshold is too easily crossed. Multi-dimensional scoring with 0-100 granularity per dimension significantly lowers effective certification noise.

Empirical evidence from Berg et al. (2025), using proprietary dealer data, confirms that credits from **least reliable technologies but with positive non-carbon externalities are 2x more expensive** than trusted industrial solutions. Buyers are paying for *narratives* (co-benefits, sustainability stories) rather than *integrity* (real emission reductions). Quality rating should correct this mispricing by making integrity transparent and comparable.

## 9. Limitations and Open Questions

1. **Weight calibration**: Current weights are proposed based on literature review. Expert input needed to validate. CCQI-style structured expert elicitation is the recommended starting methodology. The pilot scoring (Section 7) has already surfaced one concrete weighting problem -- the inability of pure-CDR credits to reach AAA under the current co_benefits weight.
2. **Subjectivity in additionality**: Even with structured criteria, additionality assessment involves judgment. Calyx Global's additive scoring model (positive in one area cannot overcome risk in another) may partially address this.
3. **Dynamic vs static ratings**: Digital MRV advances (Verra-Pachama pilot, ESA SatMRV, Open Forest Protocol) may enable continuous re-rating. Initial implementation should be static with annual review cycles.
4. **Governance**: Who can propose methodology changes? Token-weighted governance risks plutocracy. Consider a hybrid: expert committee proposes, token holders ratify.
5. **Cross-registry comparability**: Different registries have different standards. Can a single framework fairly rate across all? ICVCM CCP provides a common baseline; our framework adds granularity above that baseline.
6. **Consensus methodology**: Start with structured expert elicitation (CCQI-style) for initial weights. Consider formal Delphi or Neutrosophic Delphi-DEMATEL (Nguyen 2025) for subsequent revisions if panel size permits.
7. **Oracle reliability**: Complex dimensions (additionality, MRV) depend on off-chain assessment. The "garbage in, garbage out" problem persists regardless of blockchain transparency.
8. **Safeguards gap**: All four major rating agencies fail to incorporate community impact safeguards (Carbon Market Watch 2023). Our co-benefits dimension partially addresses this, but a dedicated safeguards dimension may be needed.
9. **Decentralizing the rater role**: The v0.3 Solidity prototype uses a single-owner rater role. The open question is how to decentralize: EAS-based attestations, UMA-style optimistic oracle, multi-rater quorum, or a hybrid where registries are the primary attesters and a dispute mechanism allows challenges. Each carries different trust assumptions and latency profiles.
10. **Rating freshness / decay**: Ratings should expire if not reattested within a defined window (e.g., 18 months). Neither the contract nor the rubrics currently enforce this.

## 10. Next Steps

1. Circulate this paper (v0.3) for feedback from carbon market practitioners
2. Identify 10-15 experts for consultation (registry reviewers, project developers, DeFi protocol designers, climate scientists)
3. Select consensus methodology based on expert availability
4. ~~Pilot-score 20-30 tokenized credits across quality spectrum~~ **done in v0.3** -- results in `data/pilot-scoring/`
5. Iterate on weights and thresholds based on pilot results (revisions proposed in Section 7.3; to be finalized in v0.4 after expert input)
6. ~~Develop smart contract prototype~~ **done in v0.3** -- `contracts/CarbonCreditRating.sol` + Foundry tests pass
7. Decentralize the rater role; select an attestation model and implement
8. Design and prototype rating freshness / re-verification mechanics
9. Build a second pilot dataset focused on tokenized credits (MCO2, BCT, NCT, NRT) for ecosystem-relevant validation

## References

1. Akerlof, G.A. (1970). The Market for "Lemons": Quality Uncertainty and the Market Mechanism. *Quarterly Journal of Economics*, 84(3), 488-500.
2. ICVCM. (2023). Core Carbon Principles, Assessment Framework and Assessment Procedure.
3. ICVCM. (2025). CCP Impact Report 2025.
4. Allen, M., et al. (2020). The Oxford Principles for Net Zero Aligned Carbon Offsetting. University of Oxford.
5. Verra. (2023). VCS Program Guide v4.4.
6. West, T.A.P., et al. (2023). Action needed to make carbon offsets from forest conservation work for climate change mitigation. *Science*, 381(6660), 873-877.
7. Zhou, C., Chen, H., Wang, S., Sun, X., El Saddik, A., & Cai, W. (2023). Harnessing Web3 on Carbon Offset Market for Sustainability: Framework and A Case Study. *IEEE Wireless Communications*, 30(5), 104-111.
8. Nature Communications. (2024). Systematic assessment of the achieved emission reductions of carbon crediting projects.
9. Annual Review of Environment and Resources. (2025). Are Carbon Offsets Fixable?
10. Trencher, G., et al. (2024). Demand for low-quality offsets by major companies undermines climate integrity of the voluntary carbon market. *Nature Communications*.
11. Manshadi, V., Monachou, F., & Morgenstern, I. (2025). Offsetting Carbon with Lemons: Adverse Selection and Certification in the Voluntary Carbon Market. *SSRN*.
12. Berg, F., et al. (2025). The Market for Voluntary Carbon Offsets. *SSRN*.
13. Battocletti, V., Enriques, L., & Romano, A. (2024). The Voluntary Carbon Market: Market Failures and Policy Implications. *Colorado Law Review*, 95.
14. MSCI. (2025). 2025 State of Integrity in the Global Carbon-Credit Market.
15. Carbon Credit Quality Initiative (CCQI). (2024). Methodology. carboncreditquality.org.
16. Perspectives Climate Group / Carbon Market Watch. (2023). Assessing and comparing carbon credit rating agencies.
17. Sylvera. (2025). State of Carbon Credits 2025.
18. BeZero Carbon. (2023). Rating Methodology and BCMA Framework.
19. Calyx Global. (2024). Ratings Explained.
20. Gao, H.O. & Liu, X. (2026). A blockchain-based carbon registry platform for credible climate action in transportation. *npj Climate Action*.
21. Jaffer, S., et al. (2024). Global, robust and comparable digital carbon assets. *IEEE ICBC / arXiv*.
22. JPMorgan Kinexys. (2025). Carbon Markets Reimagined: Scale, Resiliency, and Transparency.
23. Frontiers in Blockchain. (2024). Tokenized carbon credits in voluntary carbon markets: the case of KlimaDAO.
24. Jirasek, M. (2023). Klima DAO: a crypto answer to carbon markets. *Springer*.
25. Finance and Space. (2024). Carbon credits meet blockchain -- cryptocarbon projects and the algorithmic financialisation of voluntary carbon markets.
26. Nguyen, T. (2025). Assessing stakeholder preferences in carbon credit systems with neutrosophic DELPHI and DEMATEL.
27. Berkeley Carbon Trading Project. (2023). Quality Assessment of REDD+ Carbon Credit Projects.
28. ScienceDirect. (2025). Addressing scandals and greenwashing in carbon offset markets: A framework for reform.
29. Toucan Protocol. (2022-2023). Governance proposals and documentation. docs.toucan.earth.
30. Open Forest Protocol. openforestprotocol.org.
31. Isometric. (2024). First verified Enhanced Weathering credits. isometric.com.
32. RMI. Carbon Crediting Data Framework. rmi.org.

---

*This is a working draft for workshop discussion. All weights, scores, and thresholds are preliminary and subject to revision through expert consultation.*
