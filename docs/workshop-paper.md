# Toward a Standardized Quality Rating for On-Chain Carbon Credits

*Workshop Paper -- Draft v0.4*

**Changelog vs v0.3**
- Adopted the **safeguards-gate mechanism** for scoring (`docs/methodology-gate-v0.4.md`). Co-benefits is no longer scored as a weighted dimension in the composite; it is attested as an informational field and used by assessors to set a new `communityHarm` disqualifier that caps the grade at BBB. The 0.075 previously on co-benefits is redistributed to removal_type (+0.05), permanence (+0.025), and mrv_grade (+0.05). This replaces the v0.3 "removal bonus" proposal, which was found in stress-testing to triple-count durability and leave C007 fragile at the AA/A boundary.
- **Oxford hierarchy restored at the top of the scale.** Three engineered-removal credits now reach AAA (Climeworks Orca 95.2, Heirloom DAC 93.05, Charm Industrial 90.15), versus zero under v0.3. §7 is rewritten around this result.
- Pilot dataset extended from 25 to 29 credits: four synthetic stress cases (C026–C029) validate each disqualifier cap tier, including the new `communityHarm` safeguards-gate.
- New §7.4 sensitivity section (weight perturbation + leave-one-out + key-credit boundary buffers).
- New fragility flag: **C004 Charm Industrial at 0.15 above the AAA boundary.** This is the v0.4 analog of the C007 fragility documented in v0.3.
- Solidity reference implementation updated; all 7 Foundry tests pass (was 5 in v0.3). New tests: `testCoBenefitsNoEffect`, `testCommunityHarmCapsAtBBB`.
- §9 (Limitations) adds items for the new fragility flags and the v0.3 grandfathering problem that workstream B will address.
- §10 (Next Steps) marks pilot and prototype as done, adds explicit v0.5 scope (real tokenized credit dataset + commercial rating rank correlation + expert consultation).

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

| Flag | Cap |
|------|-----|
| `doubleCounting` | B |
| `failedVerification` | B |
| `humanRights` | B |
| `sanctionedRegistry` | BB |
| `noThirdParty` | BBB |
| `communityHarm` (v0.4) | BBB |

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

A working reference implementation lives under `contracts/`:

- `ICarbonCreditRating.sol` -- interface + shared types (`Grade` enum, `DimensionScores`, `Disqualifiers`, `Rating`).
- `CarbonCreditRating.sol` -- storage + scoring logic. Composite is computed in basis points (`composite_bps = sum(score_i * weight_bps_i) / 100`) using the v0.2 weights from `data/scoring-rubrics/index.json`. Grade bands and disqualifier caps mirror the rubric exactly.
- `QualityGatedPool.sol` -- minimal ERC-20-like pool that only accepts deposits of rated credits whose `finalGrade >= minGrade`, directly implementing the "quality-tiered pool" remedy to Toucan's BCT failure.
- `test/CarbonCreditRating.t.sol` -- 5 Foundry tests covering composite calculation (cross-checked against the Python pilot scorer), nominal-to-final grade mapping, disqualifier caps, unrated-is-ineligible, and the full set-then-read path.

Key excerpt -- the composite math is intentionally deterministic and consumable by any off-chain implementer:

```solidity
// CarbonCreditRating.sol (abbreviated, v0.4)
uint256 sum =
      uint256(s.removalType)         * 2500    // 25%
    + uint256(s.additionality)       * 2000    // 20%
    + uint256(s.permanence)          * 1750    // 17.5%
    + uint256(s.mrvGrade)            * 2000    // 20%
    + uint256(s.vintageYear)         * 1000    // 10%
    + uint256(s.coBenefits)          * 0       // 0% (safeguards-gate)
    + uint256(s.registryMethodology) * 750;    // 7.5%
return uint16(sum / 100); // 0-10000 bps, matches off-chain scorer exactly
```

The `communityHarm` disqualifier flag is enforced by one additional line in `_applyDisqualifiers`:

```solidity
if (flags.communityHarm && capped > Grade.BBB) capped = Grade.BBB;
```

All 7 Foundry tests pass under v0.4; cross-check: `computeComposite` for the Climeworks Orca test vector (removal 98, additionality 95, permanence 98, mrv 92, vintage 100, co-benefits 15, registry 82) returns exactly 9520 bps, matching the Python pilot scorer's 95.20 composite to the basis point.

The contract uses a single-owner rater role as a placeholder. A production deployment would replace this with a decentralized attestation network (EAS, optimistic oracle, or multi-rater quorum) -- this is the main open governance question discussed in Section 9, and a design doc comparing the four options ships alongside v0.4 at `docs/decentralized-rater-design.md`. v0.4 also introduces rating freshness (`expiresAt`) and a `methodologyVersion` field to the `Rating` struct so that v0.3-era ratings cannot be consumed by v0.4 logic without explicit re-attestation.

## 6. Comparison with Toucan's Approach

| Aspect | Toucan BCT | This Framework |
|--------|-----------|----------------|
| Quality differentiation | None (single pool) | 6-tier grading |
| Scoring dimensions | N/A | 7 weighted dimensions |
| Transparency | Pool eligibility rules only | Full scoring methodology public |
| On-chain logic | Bridge + pool | Rating + quality-gated pools |
| Adverse selection mitigation | None | Grade-specific pools prevent mixing |

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

### 7.4 Impact on co-benefit-heavy credits

Worth naming explicitly since the safeguards-gate is the part of v0.4 that hits co-benefit-heavy credits hardest. No grade flips occur in the pilot, but composites drop meaningfully:

| Credit | v0.3 | v0.4 | Δ | Flip? |
|--------|------|------|---|-------|
| C006 Husk biochar | 81.0 | 80.05 | −0.95 | No (still AA) |
| C010 Kenya cookstoves | 51.8 | 46.10 | −5.70 | No (still BBB) |
| C014 Plan Vivo agroforestry | 63.3 | 60.90 | −2.40 | No (still A, narrow) |
| C016 Ghana cookstoves 2019 | 38.4 | 33.27 | −5.13 | No (still BB) |

Cookstoves take the largest hit, as expected -- they are fundamentally avoidance-based with weak permanence but strong co-benefit narratives. Under v0.3 the narrative could push a cookstove credit into grade A territory if its other dimensions were unusually strong; under v0.4 that is structurally impossible, which matches the Alt-3 mechanism's design intent.

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

**Planned for v0.5:**
1. **Real-tokenized-credit dataset.** Score 15-20 actually on-chain credits (MCO2, BCT/NCT, NRT, Puro CDR, C3, Regen Network) under v0.4 rubrics and compare the distribution to the illustrative pilot.
2. **Commercial rating rank correlation.** For projects where Sylvera / BeZero / Calyx / MSCI ratings are public, compute pairwise grade-rank agreement with our framework. Success criterion: pairwise agreement *no worse than* the commercial agencies' pairwise agreement with each other (Carbon Market Watch 2023 documented significant inter-rater disagreement among them).
3. **Expert consultation.** Circulate v0.4 (not v0.3) to 10-15 carbon market practitioners, registry reviewers, project developers, and DeFi protocol designers. Ask them to react to the safeguards-gate decision menu from `docs/methodology-gate-v0.4.md` rather than rubber-stamp the chosen mechanism. Use CCQI-style structured elicitation.
4. **Implement chosen decentralized rater model** from the v0.4 design doc, informed by expert feedback on trust assumptions.
5. **Sensitivity-harden the pilot** by adding a random-MRV stress test (current leave-one-out shows 0 flips for MRV drop, which may be a dataset artifact).

**Deferred to v0.6 or later:**
- 7→6 dimension collapse (merge removal_type + permanence into "Durability") -- only if v0.5 expert consultation recommends it. The v0.4 sensitivity analysis (§7.3) showed permanence doing independent work (5/29 leave-one-out flips), so the collapse is no longer clearly warranted.
- Production decentralized rater deployment with live attestation.
- Integration pilot with a real DeFi protocol that wants quality-gated pools.

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
