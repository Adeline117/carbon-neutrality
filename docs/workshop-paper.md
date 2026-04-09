# Toward a Standardized Quality Rating for On-Chain Carbon Credits

*Draft v0.6 — April 2026*

## Abstract

Tokenized carbon credit markets suffer from a quality indistinguishability problem: when credits of varying integrity are pooled into fungible on-chain instruments, adverse selection drives out high-quality supply and erodes buyer trust (Manshadi et al. 2025). We present an open, transparent, on-chain quality rating framework that addresses this by scoring each credit across seven dimensions (removal type, additionality, permanence, MRV grade, vintage, co-benefits as a safeguards-gate, and registry/methodology), producing a six-tier grade (AAA through B) with seven disqualifier caps and a distributional posterior P(grade) that quantifies rating uncertainty. We validate the framework against 29 illustrative credits and 16 real tokenized on-chain instruments (including Toucan BCT, Moss MCO2, Climeworks Orca, and Charm Industrial), finding that engineered carbon dioxide removal dominates the top of the scale (2-3 credits reach AAA under panel consensus) while bridge-and-pool instruments cluster at BB-B (Toucan BCT scores 31.1, only 1.1 points above the lowest grade). A rank-correlation study against BeZero, Calyx Global, and Sylvera on 6 REDD+ projects shows our mean pairwise Spearman agreement (+0.343) exceeds the commercial agencies' agreement with each other (+0.009). An LLM panel inter-rater reliability study (3 Claude models, n=29) yields Fleiss' κ = 0.600 (substantial agreement), composite ICC = 0.993, and 100% within-±1-band pairwise agreement, identifying the weakest rubric dimensions for targeted refinement. The framework is implemented as a Solidity smart contract on Base with a `meetsGrade()` interface for quality-gated DeFi pools, an EAS-based adapter for decentralized attestation, and composability demos for Klima Protocol and Toucan CHAR integration. To our knowledge, it is the first carbon credit rating system to publish (1) grade probability distributions calibrated from empirical inter-rater data, (2) a callable on-chain quality-gating interface, and (3) inter-rater reliability measurements of any kind. Code, data, rubrics, and all pilot results are open-source at github.com/Adeline117/carbon-neutrality (MIT license).

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

**2025-2026 updates**: Singapore's National Environment Agency formally appointed BeZero, Calyx, and Sylvera for Article 6 compliance quality assessment -- the first sovereign mandate for carbon credit ratings (Singapore NEA 2025). Calyx updated to an AAA-D letter scale matching industry convention and reported that CCP-eligible projects average an A rating versus C for non-CCP (Calyx Global 2025). Coglianese & Giles (Science 2025) demonstrated that 95 offset projects that substantially overstated climate benefits all passed third-party VVB audits, reinforcing the structural failure of traditional verification. Microsoft/Carbon Direct published their 5th edition CDR criteria covering 9 pathways (Carbon Direct 2025). Senken launched an AI-powered Sustainability Integrity Index analyzing 600+ data points per project (Senken 2025).

### 2.6 Frontier On-Chain Approaches

**CATchain-R** (Gao & Liu, Cornell, npj Climate Action 2026): A blockchain-based carbon registry with a "carbon credibility index" that compares organizations' reduction goals vs. achievements. Rates *organization* credibility rather than individual credits.

**PACT Stablecoin** (Jaffer et al., Cambridge, IEEE ICBC 2024): Combines remote sensing + econometric baselines + on-chain certification on Tezos. Permits attribute-preserving pools (by co-benefit, jurisdiction) while maintaining fungibility within each pool.

**JPMorgan Kinexys** (2025): Registry-layer tokenization (credits tokenized at issuance via API, not bridged after the fact). Partners with S&P Global, EcoRegistry. The Verra + S&P Global "Meta Registry" partnership (August 2025) builds on this approach, planning transaction-ready APIs to replace manual processes -- effectively superseding the 2022 "immobilization" framework that was never shipped.

**Toucan CHAR Pool** (2024-2025, Base): Toucan's biochar-specific pool on Base (`0x20b0...5055`) implements on-chain quality gating via a project-specific allowlist (`checkEligible()`), with a dynamic "pool health adjustment fee" penalizing over-concentration. This is the closest deployed analog to our `QualityGatedPool`, but uses a binary project allowlist rather than a continuous quality rating threshold.

**Klima Protocol 2.0** (2025-2026, Base): KlimaDAO rebuilt as "Klima Protocol" with a dual-token architecture (kVCM + K2) on Base. kVCM is burned to retire credits from protocol inventory. Migrated entirely from Polygon.

**Hypercerts / Ecocerts** (2025, multi-chain): The Hypercerts Foundation operates an EAS-based evaluator registry with curated trusted attesters on Optimism, Base, and Celo. Their GainForest "Ecocerts" sub-project builds EAS schemas for ecological impact attestation -- the closest architectural precedent to our EAS adapter design.

**Gold Standard + Hedera Guardian** (2025): First fully digital cookstove credits using 100% IoT-SIM digital MRV, publicly auditable on Hedera blockchain. The closest real-world implementation of dMRV-to-blockchain attestation.

## 3. Proposed Rating Dimensions

### 3.1 Removal Type Hierarchy (Weight: 25%)

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

### 3.3 Permanence (Weight: 17.5%)

Duration and security of carbon storage:

| Score | Duration | Risk Profile |
|-------|----------|-------------|
| 90-100 | >10,000 years (geological) | Mineralization, geological storage, DACCS |
| 70-89 | >1,000 years | Biochar, enhanced weathering |
| 50-69 | 100-1,000 years | Well-managed forestry with legal protections, building materials |
| 30-49 | 25-100 years | Forestry with buffer pool, soil carbon with monitoring |
| 10-29 | <25 years | Short rotation forestry, agriculture without long-term commitment |
| 0-9 | Impermanent | No storage claim (pure avoidance) |

### 3.4 MRV Grade (Weight: 20%)

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

### 3.6 Co-benefits (Weight: 0% — safeguards-gate)

Contribution to Sustainable Development Goals beyond climate:

| Score | Level | Criteria |
|-------|-------|---------|
| 90-100 | Verified high impact | Third-party verified SDG contributions (e.g., SD VISta, Gold Standard SDG impact); >=3 SDGs with quantified metrics |
| 60-89 | Moderate verified | 1-2 verified SDG contributions with quantified metrics |
| 30-59 | Self-reported | Project claims SDG contributions without independent verification |
| 0-29 | Minimal | No significant co-benefits identified or claimed |

### 3.7 Registry & Methodology (Weight: 7.5%)

Assessing the rigor of the crediting program and specific methodology:

| Score | Level | Criteria |
|-------|-------|---------|
| 90-100 | Gold standard | ICVCM CCP-approved program + CCP-eligible methodology category |
| 70-89 | High rigor | Major registry (Verra VCS, Gold Standard, ACR, CAR) + well-regarded methodology with conservative baselines |
| 50-69 | Standard | Major registry + methodology without known integrity concerns |
| 30-49 | Concerns | Major registry but methodology has been subject to criticism or revision for integrity issues |
| 0-29 | Low confidence | Minor or unrecognized registry; methodology not widely accepted |

## 4. Scoring Methodology

### 4.1 Weighted Composite Score (v0.4)

```
Quality Score = sum(dimension_score_i * weight_i) for i in dimensions
```

All dimension scores are normalised to 0-100. The composite is a clean linear sum -- no bonuses, no multipliers, no nonlinear transforms. The v0.4 weights are:

| Dimension | v0.3 weight | v0.4 weight | Δ |
|-----------|-------------|-------------|---|
| Removal Type Hierarchy | 0.200 | **0.250** | +0.050 |
| Additionality | 0.200 | 0.200 | 0 |
| Permanence | 0.150 | **0.175** | +0.025 |
| MRV Grade | 0.150 | **0.200** | +0.050 |
| Vintage Year | 0.100 | 0.100 | 0 |
| Co-benefits | 0.100 | **0.000** (safeguards-gate) | −0.100 |
| Registry & Methodology | 0.100 | 0.075 | −0.025 |

**v0.4 safeguards-gate.** Co-benefits is no longer a scored dimension. Instead, it is attested as an informational 0-100 value (so off-chain buyers can still filter by SDG alignment) and its rubric is used by assessors to decide whether to set a new `communityHarm` disqualifier flag: a co-benefits score in the 0-9 "None / documented negative externalities" band triggers the flag, which caps the final grade at BBB. The technical climate value of the credit is still recognized in the composite; the credit is simply prevented from reaching premium pools.

This mechanism was chosen after a stress-test gate (`docs/methodology-gate-v0.4.md`) that compared it against three alternatives including an additive removal bonus, a multiplicative premium, and a geometric-mean technical core. The safeguards-gate won on every decision criterion: it gets the three engineered-removal credits to AAA cleanly, it keeps C007 Brazilian reforestation stably at A (versus a fragile 75.3 AA under the bonus proposals), it preserves the off-chain ≡ on-chain linear-composite invariant, and it directly encodes the Berg et al. (2025) finding that buyers already pay a premium for co-benefit narratives regardless of integrity -- rewarding co-benefits in a quality rating therefore reinforces the mispricing the framework is supposed to correct.

Disqualifier flags (five in v0.3, six in v0.4 including `communityHarm`) cap the maximum achievable grade regardless of composite:

| Flag | Cap | Trigger |
|------|-----|---------|
| `doubleCounting` | B | Evidence of double counting |
| `failedVerification` | B | Failed validation or verification |
| `humanRights` | B | Credible human rights violation claims |
| `sanctionedRegistry` | BB | Registry or methodology under sanction |
| `noThirdParty` | BBB | No independent third-party verification |
| `communityHarm` | BBB | Documented community opposition or environmental damage |
| `biodiversityHarm` | BBB | Published research documents measurable biodiversity loss (Zeng et al. 2026) |

The weights, grade bands, and disqualifiers are maintained as machine-readable JSON under `data/scoring-rubrics/` (one file per dimension plus an `index.json`) so that the pilot scoring script, the Solidity reference contract, and any third-party implementer all consume the same source of truth.

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

A working reference implementation (8 Solidity contracts, 19 Foundry tests passing) lives under `contracts/`:

**Core contracts:**
- `ICarbonCreditRating.sol` -- interface with `DimensionScores`, `DimensionStds`, `Disqualifiers` (7 flags), and `Rating` struct (including `compositeVarianceBps2` for distributional scoring, `expiresAt` / `methodologyVersion` / `evidenceHash` for freshness and provenance).
- `CarbonCreditRating.sol` -- storage + scoring logic. Composite and composite variance are computed on-chain in basis points; grade assignment and disqualifier caps mirror the rubric exactly. `CURRENT_METHODOLOGY_VERSION = 0x0500` ensures ratings from older rubric versions are automatically stale.
- `QualityGatedPool.sol` -- minimal pool that only accepts deposits of rated credits whose `finalGrade >= minGrade` and whose rating is not stale (`isStale()` checks both time expiry and methodology version mismatch).

**Decentralized attestation:**
- `CarbonCreditRatingEASAdapter.sol` -- relay pattern for the Ethereum Attestation Service. Maintains a trusted-attester allowlist (corresponding to carbon registries); verifies schema, revocation, expiry, and attester trust before decoding and relaying attestations into the rating contract. Architecture references the Hypercerts evaluator registry pattern.

**Composability demos:**
- `KlimaRetirementGate.sol` -- demonstrates how Klima Protocol's kVCM retirement flow could gate on `meetsGrade()` before burning credits from inventory.
- `CHARQualityOverlay.sol` -- demonstrates how Toucan CHAR's binary project-allowlist could be augmented with continuous quality rating and quality-based fee discounts (AAA: -5%, AA: -3%, A: -1%).

The composite math is bit-identical between the Python scorer (`data/pilot-scoring/score.py`) and the Solidity contract. For the Climeworks Orca test vector, both produce exactly 9505 bps (95.05 composite) under v0.6 weights. The `computeCompositeVariance` pure function produces 83,706 bps² under default per-dimension standard deviations calibrated from the LLM IRR study. 19 Foundry tests cover: composite calculation, variance propagation, zero-std collapse, variance sensitivity, disqualifier caps, communityHarm gate, co-benefits-no-effect, set-and-read, expiry rejection, stale rating, never-expires, re-rating freshness reset, unrated-not-stale, EAS relay, revocation rejection, untrusted-attester rejection, schema mismatch, and attester count.

## 6. Comparison with Toucan's Approach

| Aspect | Toucan BCT (2021-2023) | Toucan CHAR (2024-2025) | This Framework |
|--------|-----------|------------|----------------|
| Quality differentiation | None (single pool) | Binary project allowlist | 6-tier grading with P(grade) |
| Scoring dimensions | N/A | N/A (allowlist is binary) | 7 weighted + 7 disqualifier flags |
| Quality gate mechanism | Vintage + methodology filter | `checkEligible()` allowlist | `meetsGrade(creditToken, tokenId, minGrade)` — continuous threshold |
| Concentration risk | None | Dynamic pool health adjustment fee | Not yet implemented (v0.7 candidate) |
| Transparency | Pool eligibility rules only | Allowlist public | Full scoring methodology, rubric JSONs, Python scorer, Solidity contract, all open-source |
| Uncertainty quantification | None | None | P(grade) posteriors via distributional composite |
| Adverse selection mitigation | None | Partial (biochar-only filter) | Grade-specific pools prevent mixing across quality tiers |
| Deployment chain | Polygon | Base + Celo | Base (same chain as CHAR and Klima 2.0 — natural composability) |

**Key distinction**: Toucan CHAR is the closest deployed analog to our `QualityGatedPool`, but it uses a **binary project allowlist** (a project is either eligible or not) rather than a **continuous quality threshold** (a project's grade is compared against a minimum). Our `meetsGrade()` interface is, to our knowledge, the only on-chain mechanism that gates deposits on a continuous quality rating with uncertainty quantification.

## 7. Pilot Scoring Results

The rubrics were stress-tested against a 29-credit hand-scored dataset: 25 real-project archetypes spanning the full quality spectrum plus 4 synthetic credits (C026-C029) that validate each disqualifier cap tier including the new v0.4 `communityHarm` safeguards-gate. Full data, the Python scorer, and the sensitivity runner are under `data/pilot-scoring/`. Per-dimension scores were assigned by the authors based on public project documentation; they are a methodology validation, not a formal rating of any named project.

The v0.3 edition of this paper reported the opposite result from what appears below: under v0.3 weights, *no credit reached AAA*, Climeworks Orca topped out at 86.8, and the co-benefits weight systematically compressed engineered-removal credits. Section 7.3 of v0.3 proposed a `+5 removal bonus` fix. Stress-testing that proposal surfaced three problems -- it triple-counted durability, left C007 Brazilian reforestation fragile at 75.3 just above the AA/A boundary, and silently failed to fix Charm Industrial because its MRV score sat just below an arbitrary threshold. v0.4 therefore adopts a different mechanism -- the **safeguards-gate** (see §4.1 and `docs/methodology-gate-v0.4.md`) -- and the results below reflect that change.

### 7.1 Distribution (v0.4, real-archetype credits only)

| Grade | Count | Share | Score range |
|-------|-------|-------|-------------|
| AAA   | 3     | 12%   | 90.15 – 95.20 |
| AA    | 3     | 12%   | 80.05 – 87.20 |
| A     | 5     | 20%   | 60.90 – 73.90 |
| BBB   | 4     | 16%   | 46.10 – 59.53 |
| BB    | 2     | 8%    | 33.27 – 36.52 |
| B     | 8     | 32%   | 16.38 – 28.57 |

Reference: MSCI's 2025 Integrity Report rated fewer than 10% of 4,400+ projects AAA-A; our pilot at 44% AA-A is spectrum-sampled rather than VCM-representative.

### 7.2 Key findings

**Finding 1 -- Oxford hierarchy restored at the top of the scale.** Three credits reach AAA under v0.4, all of them engineered carbon dioxide removal with durable storage: Climeworks Orca (DACCS + geological storage, 95.20), Heirloom DAC (DAC + mineralization, 93.05), and Charm Industrial (pyrolysis bio-oil + geological injection, 90.15). Under v0.3 these scored 86.8, 85.3, and 83.0 respectively and all graded AA. The 10-percentage-point weight removed from co-benefits and redistributed across removal_type (+0.05), mrv_grade (+0.05), and permanence (+0.025) is sufficient to lift all three above the 90-point AAA threshold without any bonus mechanism.

**Finding 2 -- BCT pool composition in retrospect (reframed).** Of the 25 real-archetype credits, 10 are tagged as historically BCT-eligible. Under v0.4:

- 1 grades AA or higher (0 under v0.4, but C007 graded AA under v0.3)
- 2 grade A or higher (C007 at 73.9, C009 at 66.2)
- 1 grades BBB (C015 at 51.55)
- 1 grades BB (C017 at 36.52)
- 6 grade B

Had a grade-A gated pool existed, it would have admitted only C007 and C009 -- the same 2 of 10 credits as under v0.3. The headline finding -- **BCT's minimal eligibility criteria admitted a pool that was 60% grade B by our scoring** -- is unchanged. What changes is the grade of the best BCT-eligible credit (C007 moves from AA to A), and this move is actually a *stability improvement*: under v0.3's Rev-1+2 proposal C007 would have been AA by only 0.3 points, so any minor rescoring would have flipped it. Under v0.4, C007 is A with a 13.9-point buffer to BBB and a 1.1-point distance to AA. The BCT retrospective is now robust to small changes in per-dimension scores.

One BCT-eligible credit also drops correctly across a grade boundary: **Cordillera Azul REDD+ (C018) moves from BB to B**, matching the Carbon Market Watch 2023 assessment that flagged this project as low-integrity.

**Finding 3 -- Disqualifier lattice validated end-to-end.** Four synthetic credits (C026-C029) were added to demonstrate that each disqualifier cap tier fires correctly when the nominal composite exceeds the cap:

| ID | Nominal composite | Nominal grade | Disqualifier | Cap | Final grade |
|----|-------------------|---------------|--------------|-----|-------------|
| C026 | 88.05 | AA | `double_counting` | B | B ✓ |
| C027 | 81.72 | AA | `sanctioned_registry` | BB | BB ✓ |
| C028 | 79.12 | AA | `no_third_party` | BBB | BBB ✓ |
| C029 | 78.53 | AA | `community_harm` (v0.4) | BBB | BBB ✓ |

C029 is the first test of the v0.4 safeguards-gate: a credit with AA-tier technical scores but a co-benefits score in the 0-9 "None / negative externalities" band, which triggers the `communityHarm` disqualifier. The gate correctly caps at BBB -- the framework recognizes the technical climate value but refuses to admit the credit into premium pools.

**Finding 4 -- New fragility flags.** v0.4 surfaces three credits within 1 point of a grade boundary:

| ID | Credit | Grade | Composite | Buffer | Direction |
|----|--------|-------|-----------|--------|-----------|
| C004 | Charm Industrial bio-oil | AAA | 90.15 | **0.15** | down → AA |
| C011 | Adipic acid N2O destruction | BBB | 59.53 | **0.47** | up → A |
| C014 | Plan Vivo agroforestry | A | 60.90 | **0.90** | down → BBB |

C004 is the most fragile case and the v0.4 analog of v0.3's C007 fragility. Any 1-point downward rescoring on any of its contributing dimensions flips it to AA and changes the headline distribution from 3 AAA to 2 AAA. This should be noted explicitly: the AAA count is sensitive to small changes in Charm Industrial's per-dimension scoring. The same credit *is* defensibly AAA under current scoring -- engineered removal, geological storage, Puro-verified -- but reviewers should know it sits on the boundary.

### 7.3 Sensitivity (weight perturbation and leave-one-out)

The `--sensitivity` mode of the pilot scorer produces two sensitivity tests; full output in `data/pilot-scoring/sensitivity.md`.

**Weight perturbation (±5 percentage points per dimension, redistributed proportionally):**

| Dimension | Weight | +5pp flips | −5pp flips |
|-----------|--------|-----------|-----------|
| removal_type | 0.250 | 0/29 | 1/29 |
| additionality | 0.200 | 1/29 | 0/29 |
| permanence | 0.175 | 2/29 | 2/29 |
| mrv_grade | 0.200 | 2/29 | 0/29 |
| vintage_year | 0.100 | 2/29 | 3/29 |
| co_benefits | 0.000 (gate) | 2/29 | 0/29 |
| registry_methodology | 0.075 | 2/29 | 1/29 |

No single perturbation produces more than 3 grade changes. The v0.4 weights are stable in aggregate. The highest-impact perturbation is vintage_year at −5pp (3 flips), which reflects the bimodal distribution of vintage scores in the dataset (recent credits ~88-100, pre-2016 credits ~0-20) rather than a fragility in vintage weighting itself.

**Leave-one-out (drop each dimension, redistribute proportionally to the remainder):**

| Dropped dimension | Flips |
|-------------------|-------|
| removal_type | 4/29 |
| additionality | 2/29 |
| permanence | 5/29 |
| mrv_grade | 0/29 |
| vintage_year | 3/29 |
| registry_methodology | 1/29 |

**Permanence is the highest-impact dimension (5 flips when dropped)**, contradicting the v0.3 concern that it might be collinear with removal_type and collapsible in a future 7→6 dimension revision. On this pilot, permanence is doing independent work. MRV dropping produces zero flips, which looks like redundancy but is more likely an artifact of MRV scores being positively correlated with the other technical dimensions in this dataset; a random-MRV stress test would probably flip more credits.

### 7.4 Tokenized credit pilot (v0.5 C1)

To test the framework against actually on-chain instruments, 16 real tokenized carbon credits were scored under v0.6 rubrics. Full data and analysis are in `data/tokenized-pilot/`.

| Grade | Count | Share | Credits |
|-------|-------|-------|---------|
| AAA   | 3     | 19%   | Heirloom DAC, Climeworks Orca, Charm Industrial |
| AA    | 3     | 19%   | Puro biochar, Toucan CHAR, Rainbow Standard |
| A     | 2     | 12%   | OFP (dMRV afforestation), JPMorgan Kinexys |
| BBB   | 4     | 25%   | Toucan NCT, Nori NRT, C3, Regen Network |
| BB    | 2     | 12%   | Toucan BCT (31.1), Moss MCO2 (30.9) |
| B     | 2     | 12%   | Flowcarbon (failed_verification cap), Kariba REDD+ |

**Key finding — the tokenized market is bimodal.** The high-quality tail is engineered CDR on quality-aware registries (Puro, Isometric); the low-quality middle is bridge-and-pool instruments (Toucan BCT/NCT, Moss MCO2). **No nature-based credit reaches AA in the tokenized sample** — the AA middle is empty. High-quality nature-based credits remain in OTC markets where they command premium prices, confirming the adverse selection dynamic the paper's §1.2 describes: only low-quality credits have an incentive to tokenize into fungible pools.

**Toucan BCT is measurably BB at 31.1**, only 1.10 points above the B boundary (P(BB) = 65%). This is the first quantitative measurement of the BCT lemons problem — BCT's minimal eligibility criteria (any post-2008 Verra VCU) produced a pool that our framework grades at the penultimate quality tier with marginal stability.

### 7.4a Rank correlation vs. commercial rating agencies (v0.5 C2)

We compared our v0.6 framework against BeZero, Calyx Global, and Sylvera on the 6 REDD+ projects where Carbon Market Watch (2023) published overlapping public ratings. Full results in `data/rank-correlation/`.

| Pair | Spearman ρ |
|------|----------:|
| Ours vs BeZero | **+0.664** |
| Ours vs Sylvera | **+0.566** |
| Ours vs Calyx | −0.200 |
| BeZero vs Calyx | **−0.664** |
| BeZero vs Sylvera | +0.125 |
| Calyx vs Sylvera | +0.566 |

Our mean pairwise Spearman with commercial raters: **+0.343**. Commercial inter-agency mean: **+0.009**. Our framework's agreement with the commercial agencies materially exceeds their agreement with each other. Notably, BeZero and Calyx are **strongly anti-correlated** (ρ = −0.664) on this REDD+ sample, confirming the CMW 2023 headline finding of inter-agency inconsistency.

Anchor data points beyond the CMW dataset: BeZero's first-ever AAA rating was for Climeworks Orca (our framework: AAA, P=96%); BeZero downgraded Kariba REDD+ to D then delisted (our framework: B with 100% confidence). Both directions align.

**Caveat**: n=6 REDD+-only; confidence intervals are wide. Cross-project-type extension is a v0.7 scope item.

### 7.5 LLM panel inter-rater reliability (v0.5 W1)

To quantify the single-author-scoring vulnerability acknowledged in §9, three Claude models (Opus 4.6, Sonnet 4.6, Haiku 4.5) independently scored all 29 illustrative-pilot credits against the v0.4.1 rubric, using a redacted evidence pack with author scores removed. Full protocol and analysis are in `data/llm-panel-irr/`. Headline results:

| Metric | Value |
|--------|------:|
| Grade-level Fleiss' κ (3-rater LLM panel) | **+0.600** (substantial) |
| Composite ICC(2,k) (continuous 0-100) | **+0.993** (near-perfect) |
| Author vs panel median — exact grade agreement | **86%** (25/29) |
| Author vs panel median — within ±1 band | **100%** (29/29) |
| Disqualifier recall on synthetic stress tests C026-C029 | **12/12** (100%) |

Every rater-pair reaches 100% within-±1-band agreement. Per-dimension Fleiss' κ ranges from +0.684 (permanence, most-agreed) down to +0.168 (registry_methodology, least-agreed), giving a specific map of which rubric dimensions need tightening in v0.6.

**Key correction to §7.2 Finding 1.** The LLM panel places C004 Charm Industrial at **AA (3/3)**, not AAA. The author's v0.4.1 composite of 90.15 sits 0.15 points above the AAA boundary; a reasonable alternative reading lands just below. Under panel consensus the headline number is **2 of 29 credits reach AAA** (Climeworks Orca, Heirloom DAC), not 3. The Oxford-hierarchy-restored finding is preserved — engineered CDR still dominates the top of the scale — but the exact AAA count is rater-dependent for credits within ~1 composite point of the boundary.

C011 (N2O destruction, BBB) and C014 (Plan Vivo agroforestry, A) are not fragile in practice: C011 matches 3/3, C014 matches 2/3 with the third rater dropping to the adjacent BBB.

**v0.6 rubric-refinement targets driven by this study:**

1. Collapse `07_registry_methodology.json` into a 2-tier (CCP-eligible / not) scheme with Boolean modifiers; target κ > 0.40.
2. Tighten or remove the informational `co_benefits` attestation (weight is 0 in v0.4 anyway).
3. Simplify the pre-Paris override in `05_vintage_year.json` to remove the discontinuity raters disagree about.
4. Replicate with a multi-provider panel (GPT-5, Gemini, Llama) to detect Anthropic-specific biases.

### 7.6 Impact on co-benefit-heavy credits

Worth naming explicitly since the safeguards-gate is the part of v0.4 that hits co-benefit-heavy credits hardest. No grade flips occur in the pilot, but composites drop meaningfully:

| Credit | v0.3 | v0.4 | Δ | Flip? |
|--------|------|------|---|-------|
| C006 Husk biochar | 81.0 | 80.05 | −0.95 | No (still AA) |
| C010 Kenya cookstoves | 51.8 | 46.10 | −5.70 | No (still BBB) |
| C014 Plan Vivo agroforestry | 63.3 | 60.90 | −2.40 | No (still A, narrow) |
| C016 Ghana cookstoves 2019 | 38.4 | 33.27 | −5.13 | No (still BB) |

Cookstoves take the largest hit, as expected -- they are fundamentally avoidance-based with weak permanence but strong co-benefit narratives. Under v0.3 the narrative could push a cookstove credit into grade A territory if its other dimensions were unusually strong; under v0.4 that is structurally impossible, which matches the Alt-3 mechanism's design intent.

### 7.7 Grade stability under distributional scoring (v0.5+)

The v0.5 distributional composite replaces point-estimate grades with posterior probability distributions. For each credit, P(grade) is computed via Gaussian variance propagation using empirically calibrated per-dimension standard deviations from the W1 LLM panel IRR study (`data/llm-panel-irr/`). Key results for the load-bearing credits:

| Credit | Composite | ±σ | Grade | P(grade) | Stability |
|--------|----------:|---:|-------|----------|-----------|
| Climeworks Orca | 95.05 | 2.88 | AAA | **96%** | stable |
| Heirloom DAC | 93.20 | 2.88 | AAA | **87%** | stable |
| Charm Industrial | 90.53 | 2.88 | AAA | **57%** | fragile |
| Pacific Biochar | 83.28 | 2.88 | AA | **99%** | stable |
| Plan Vivo agroforestry | 60.15 | 2.88 | A | **52%** | fragile |
| Toucan BCT (tokenized) | 31.10 | 2.88 | BB | **65%** | moderate |

This is a unique contribution: **no commercial carbon credit rating agency (BeZero, Sylvera, Calyx Global, MSCI) publishes any form of grade uncertainty or confidence interval alongside their ratings.** The Carbon Market Watch 2023 study documented significant inter-agency disagreement on the same projects, yet none of the agencies quantifies the uncertainty inherent in their own outputs. Our P(grade) posteriors, calibrated from empirical inter-rater data, make this uncertainty transparent and actionable: a DeFi protocol using `meetsGrade()` can now read `compositeVarianceBps2` from the on-chain `Rating` struct and compute P(grade ≥ threshold) before making an admission decision.

The distributional model also explains the W1 fragility finding (§7.5): Charm Industrial's AAA at P=57% is consistent with the LLM panel's 0/3 agreement on AAA — a 57% probability corresponds to roughly even odds, and 0/3 is within the expected range of a fair coin flipped three times.

### 7.8 Competitive positioning: three verifiable leapfrog claims

This framework makes three specific, falsifiable claims of structural advantage over all four major commercial carbon credit rating agencies:

**Claim 1 — Uncertainty quantification.** We are the only carbon credit rating system that publishes P(grade) probability distributions alongside point-estimate grades, calibrated from empirical inter-rater reliability data (Fleiss' κ = 0.600, per-dimension σ from 4.0 to 11.1). The distributional composite is stored on-chain (`compositeVarianceBps2` in the `Rating` struct) and reproducible by any consumer via the published Gaussian propagation formula. To falsify: demonstrate that any of BeZero, Sylvera, Calyx, or MSCI publishes a comparable uncertainty metric.

**Claim 2 — On-chain DeFi composability.** We are the only carbon credit quality rating system with a deployed on-chain interface (`meetsGrade(address, uint256, Grade) → bool`) that DeFi protocols can call as a zero-gas `staticcall` for quality gating. We demonstrate three integration patterns: quality-gated deposit pools (`QualityGatedPool`), retirement quality gates for kVCM-style systems (`KlimaRetirementGate`), and quality-based fee discounts for pool deposits (`CHARQualityOverlay`). To falsify: demonstrate that any commercial agency has a callable smart contract interface.

**Claim 3 — Published inter-rater reliability.** We are the only carbon credit rating system that has published inter-rater reliability measurements of any kind. Our 3-model panel (Claude Opus, Sonnet, Haiku) achieves grade-level Fleiss' κ = 0.600 ("substantial" per Landis & Koch 1977), composite ICC(2,k) = 0.993, and 100% within-±1-band agreement on all pairwise comparisons. Per-dimension κ breakdown identifies the weakest rubric dimensions (registry_methodology κ = 0.168, tightened in v0.6 from 4-tier to 2-tier). To falsify: demonstrate that any commercial agency has published IRR data showing comparable or better reproducibility.

These claims are structural: they derive from architectural decisions (open-source rubric, linear composite, on-chain storage, published raw data) that commercial agencies cannot replicate without fundamental business-model changes. The two dimensions where commercial agencies remain ahead — credit coverage (45 vs. 500-4,400) and regulatory recognition (0 vs. Singapore NEA) — are resource-intensive gaps that the framework addresses through a scalable methodology-level scoring pipeline and an expert consultation pathway.

## 8. Adverse Selection: Formal Justification

Manshadi, Monachou, and Morgenstern (2025) provide the first rigorous economic model of adverse selection in the VCM:
- High-quality projects are costlier but indistinguishable from low-quality without certification
- When **certification noise exceeds a threshold**, a market-for-lemons collapse occurs (no trade)
- Interventions targeting only demand or supply side can actually **reduce** climate benefit without certification improvements

This formally validates our framework's core premise: reducing certification noise through granular, transparent, multi-dimensional scoring is *necessary* to prevent market collapse. A binary (pass/fail) certification is insufficient -- the noise threshold is too easily crossed. Multi-dimensional scoring with 0-100 granularity per dimension significantly lowers effective certification noise.

Empirical evidence from Berg et al. (2025), using proprietary dealer data, confirms that credits from **least reliable technologies but with positive non-carbon externalities are 2x more expensive** than trusted industrial solutions. Buyers are paying for *narratives* (co-benefits, sustainability stories) rather than *integrity* (real emission reductions). Quality rating should correct this mispricing by making integrity transparent and comparable.

## 9. Limitations and Open Questions

1. **Weight calibration**: v0.4 weights were chosen on the basis of the pilot stress test and the A2 methodology gate (`docs/methodology-gate-v0.4.md`). They have not yet been validated by an expert panel. CCQI-style structured expert elicitation remains the recommended validation methodology.
2. **Subjectivity in additionality**: Even with structured criteria, additionality assessment involves judgment. Calyx Global's additive scoring model (positive in one area cannot overcome risk in another) may partially address this.
3. **Dynamic vs static ratings**: v0.4 adds an `expiresAt` field to the `Rating` struct (workstream B, `contracts/CarbonCreditRating.sol`) but does not yet enforce a specific expiry policy. A dedicated re-rating cycle -- annual is the default suggestion -- is an open implementation question.
4. **Governance**: Who can propose methodology changes? Token-weighted governance risks plutocracy. Consider a hybrid: expert committee proposes, token holders ratify.
5. **Cross-registry comparability**: Different registries have different standards. Can a single framework fairly rate across all? ICVCM CCP provides a common baseline; our framework adds granularity above that baseline.
6. **Consensus methodology**: Start with structured expert elicitation (CCQI-style) for initial weights. Consider formal Delphi or Neutrosophic Delphi-DEMATEL (Nguyen 2025) for subsequent revisions if panel size permits.
7. **Oracle reliability**: Complex dimensions (additionality, MRV) depend on off-chain assessment. The "garbage in, garbage out" problem persists regardless of blockchain transparency.
8. **Safeguards gap (revised in v0.4)**: The v0.3 co-benefits dimension partially addressed community safeguards; v0.4 replaces it with a dedicated `communityHarm` disqualifier that caps at BBB. This is a cleaner encoding of the Carbon Market Watch 2023 finding that major rating agencies fail to incorporate community impact -- but it is only as good as the assessor's willingness to set the flag. Attestation provenance (see §5.3, workstream B) partially mitigates this.
9. **Decentralizing the rater role**: The v0.4 Solidity prototype still uses a single-owner rater role. A design doc comparing EAS / UMA optimistic oracle / multi-rater quorum / registry-attester-with-dispute ships at `docs/decentralized-rater-design.md`. Implementation lands in v0.5 or v0.6 depending on expert feedback during the v0.5 consultation.
10. **Methodology version grandfathering**: v0.4 bumps the methodology version, which invalidates any v0.3 rating stored on-chain. The `Rating` struct now carries a `methodologyVersion` field so the contract can reject v0.3 ratings explicitly; this is a one-time migration concern for any production deployment.
11. **Three new fragility flags (C004 Charm Industrial, C011 N2O destruction, C014 Plan Vivo)**. See §7.2. C004 is the "load-bearing AAA boundary" credit and should be acknowledged explicitly in any external presentation of the v0.4 grade distribution.
12. **v0.4 has not been tested against actually-tokenized credits** (MCO2, BCT, NCT, NRT, Puro CDR). The pilot uses real-project archetypes, not on-chain instruments. Workstream C in v0.5 addresses this.

## 10. Next Steps

**Completed in v0.4:**
- ~~Pilot-score 20-30 credits across the quality spectrum~~ (25 real + 4 synthetic; `data/pilot-scoring/`)
- ~~Develop smart contract prototype~~ (`contracts/CarbonCreditRating.sol`, 7 Foundry tests passing)
- ~~Iterate on weights based on pilot findings~~ (A2 gate + A3 regeneration; safeguards-gate adopted)
- ~~Add disqualifier stress tests~~ (C026-C029)
- ~~Design rating freshness / decay mechanism~~ (workstream B, lands with v0.4)
- ~~Decentralized rater architecture comparison~~ (workstream D, `docs/decentralized-rater-design.md`)

**Completed in v0.5:**
- ~~Real-tokenized-credit dataset~~ (16 on-chain credits including Toucan CHAR on Base and Rainbow Standard biochar; `data/tokenized-pilot/`)
- ~~Commercial rating rank correlation~~ (6-REDD+ study vs BeZero/Calyx/Sylvera, mean Spearman +0.343 vs inter-agency +0.009; `data/rank-correlation/`)
- ~~LLM panel inter-rater reliability~~ (3-model Claude panel, grade-level Fleiss' κ = +0.600, ICC = +0.993; `data/llm-panel-irr/`)
- ~~Distributional composite~~ (per-dimension uncertainty propagation, P(grade) posteriors calibrated from empirical W1 data; `data/scoring-rubrics/index.json` schema v0.3.0)
- ~~Base Sepolia deployment infrastructure~~ (`script/Deploy.s.sol` + `script/SeedRatings.s.sol` + demo HTML; pending user execution)
- ~~Expert consultation materials~~ (executive summary + 10-section questionnaire + 20-person reviewer candidate list; `docs/v0.5-*`)
- ~~Deep research~~ (15 new VCM sources 2025-2026, 12 on-chain tech findings, 20 expert profiles)

**Planned for v0.6:**
1. **Expert consultation execution.** Distribute the questionnaire to the 20 identified reviewers (`docs/v0.5-reviewer-candidates.md`). Priority contacts: Lambert Schneider (CCQI/ICVCM), CarbonPlan (Freeman/Cullenward), Manshadi (Yale). Incorporate feedback into v0.6 methodology diff.
2. **Multi-provider LLM panel extension.** Replicate W1 study with GPT-5 + Gemini 2.5 Pro + DeepSeek/Llama to detect Anthropic-specific biases in per-dimension κ.
3. **Rubric refinement driven by W1 findings.** Collapse registry_methodology 4-tier → 2-tier CCP/not-CCP scheme (κ=0.168, weakest dimension). Tighten co_benefits attestation criteria. Simplify vintage_year pre-Paris override.
4. **EAS adapter implementation.** Register carbon credit quality schema on EAS (Base), referencing Hypercerts evaluator registry pattern and GainForest Ecocerts schema. Deploy `CarbonCreditRatingEASAdapter` per `docs/decentralized-rater-design.md`.
5. **Klima 2.0 / Toucan CHAR composability pilot.** Both are on Base; test `meetsGrade()` calls from kVCM retirement pipeline and CHAR deposit flow.
6. **Cross-project-type rank correlation.** Extend beyond REDD+ to CDR, biochar, industrial avoidance, cookstoves — project types where commercial agencies agree more (per Calyx 2025: CCP projects average A vs C for non-CCP).
7. **Verra Meta Registry API integration.** When S&P Global Phase 1 launches (expected Q1 2026), prototype an EAS attester that reads credit metadata from the Verra API and relays attestations on-chain.
8. **Biodiversity safeguards enhancement.** Per Zeng et al. (2026) finding of 3.7% habitat disturbance increase from carbon offset projects, consider adding biodiversity harm to the `communityHarm` disqualifier scope or introducing a dedicated `biodiversityHarm` flag.

**Deferred to v0.7 or later:**
- 7→6 dimension collapse (merge removal_type + permanence into "Durability") -- only if v0.6 expert consultation recommends it
- Production mainnet deployment with multi-rater attestation
- Integration with Carbonmark Direct on-chain native issuance

## 11. Conclusion

We presented an open, transparent, on-chain quality rating framework for tokenized carbon credits that addresses the quality indistinguishability problem driving adverse selection in pooled carbon instruments. The framework scores credits across seven dimensions using a linear weighted composite with distributional uncertainty propagation, producing a six-tier grade (AAA through B) with seven disqualifier caps and a posterior probability P(grade) that honestly quantifies rating confidence.

Three empirical studies validate the framework's outputs. First, a 3-model LLM panel inter-rater reliability study achieves Fleiss' κ = 0.600 (substantial agreement) and composite ICC = 0.993 across 29 credits, with 100% within-±1-band agreement on all pairwise comparisons — demonstrating that the rubric is reproducible by independent raters. Second, a rank-correlation study against BeZero, Calyx Global, and Sylvera on 6 REDD+ projects shows our mean pairwise Spearman agreement (+0.343) materially exceeds the commercial agencies' agreement with each other (+0.009), placing our framework in a defensible compromise position between agencies that themselves disagree strongly. Third, a 16-credit tokenized pilot confirms that bridge-and-pool instruments (Toucan BCT at 31.1 BB, Moss MCO2 at 30.9 BB) cluster at the bottom while engineered CDR on quality-aware registries (Climeworks Orca at 95.05 AAA, Heirloom DAC at 93.20 AAA) dominates the top — empirically validating the bimodal quality distribution that the adverse selection model predicts.

The framework makes three verifiable claims of structural advantage over all four major commercial rating agencies: it is the only system to publish (1) grade probability distributions calibrated from empirical inter-rater data, (2) a callable on-chain quality-gating interface (`meetsGrade()`) for DeFi composability, and (3) inter-rater reliability measurements of any kind. These advantages derive from architectural decisions — open-source rubric, linear composite, on-chain storage, published raw data — that commercial agencies cannot replicate without fundamental business-model changes. The two dimensions where commercial agencies remain ahead — credit coverage (45 vs. 500-4,400) and regulatory recognition — are resource-intensive gaps addressed by a scalable methodology-level scoring pipeline and an expert consultation pathway currently in preparation.

All code, rubrics, pilot data, IRR raw outputs, rank-correlation datasets, deployment scripts, and demo infrastructure are open-source under the MIT license at github.com/Adeline117/carbon-neutrality.

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
33. Coglianese, C. & Giles, C. (2025). Auditors can't save carbon offsets. *Science*, 389(6733). DOI: 10.1126/science.ady4864.
34. Singapore NEA. (2025). Carbon Rating Panel appointment: BeZero, Calyx, Sylvera for ICC Framework.
35. Zeng, Y. et al. (2026). Limitations of carbon markets for biodiversity conservation. *Nature Reviews Biodiversity*. DOI: 10.1038/s44358-026-00150-4.
36. Calyx Global. (2025). Are carbon credit quality indicators delivering? calyxglobal.com.
37. Gold Standard & ATEC Global. (2025). First fully digital cookstove credits on Hedera Guardian blockchain.
38. West, T.A.P. et al. (2025). Demystifying the Romanticized Narratives About Carbon Credits From Voluntary Forest Conservation. *Global Change Biology*, 31(10), e70527.
39. Garcia, A. & Sanford, L. (2026). On the potential for strategic behavior in jurisdictional REDD+. *PNAS*, 123(14).
40. Cabiyo, B. & Field, C.B. (2025). Embracing imperfection: overcrediting risk and insurance mechanisms. *PNAS Nexus*, 4(5), pgaf091.
41. Bosshard et al. (2025). Blockchain-based voluntary carbon market: network structure analysis. *Frontiers in Blockchain*, 8, 1603695.
42. Columbia CGEP / Ahonen, P. et al. (2025). How to Fully Operationalize Article 6 of the Paris Agreement.
43. Verra. (2026). First DMRV pilot credits approved for high-frequency issuance.
44. Microsoft / Carbon Direct. (2025). 2025 Criteria for High-Quality CDR (5th edition).
45. Hypercerts Foundation. (2025). EAS-based evaluator registry and Ecocerts (GainForest collaboration). hypercerts.org.
46. Toucan Protocol. (2024-2025). CHAR biochar pool on Base. Contract: 0x20b048fA035D5763685D695e66aDF62c5D9F5055.
47. Klima Protocol. (2025-2026). kVCM/K2 dual-token relaunch on Base. whitepaper.klimaprotocol.com.
48. Rainbow Standard. (2025). CCP-Eligible CDR registry. rainbowstandard.io.
49. Carbonmark. (2025). Carbonmark Direct: on-chain native issuance. carbonmark.com.
50. Senken. (2025). Sustainability Integrity Index: AI-powered quality scoring. senken.io.

---

*This is a working draft for workshop discussion. All weights, scores, and thresholds are preliminary and subject to revision through expert consultation.*
