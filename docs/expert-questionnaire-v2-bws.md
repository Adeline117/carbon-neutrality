# v0.6 Expert Consultation — Weight Calibration Questionnaire (v2-BWS)

*Structured questionnaire for carbon market practitioners, registry reviewers, project developers, DeFi protocol designers, and climate scientists. Completion time: 45-60 minutes.*

Please read `docs/v0.4-executive-summary.md` (2 pages) first, then skim `docs/methodology-gate-v0.4.md` and the pilot results in `data/pilot-scoring/analysis.md` + `data/tokenized-pilot/analysis.md`. Deep familiarity with the full workshop paper is helpful but not required.

**Why this questionnaire differs from v1.** The v1 questionnaire (v0.5) asked respondents to directly assign numeric weights to each dimension. Direct weight elicitation is known to suffer from anchoring bias — respondents tend to adjust incrementally from presented values rather than evaluating importance independently (Doyle et al., 1997; Saaty, 1980). Peer reviewers at top venues would rightly question whether weights derived through direct elicitation reflect genuine expert judgment or merely anchoring artifacts.

This v2 questionnaire replaces direct weight assignment with **Best-Worst Scaling (BWS)**, a choice-based method that produces ratio-scale importance scores free from scale-use bias and anchoring (Louviere et al., 2015; Finn & Louviere, 1992). We also include pairwise comparisons and scenario-based validation as cross-checks. Together, these three exercises triangulate dimension weights through complementary methodological lenses, producing results suitable for publication in venues such as Nature Sustainability, Nature Climate Change, or WWW.

**This questionnaire is deliberately not a rubber-stamp exercise.** For each decision we made, we want you to evaluate the alternatives we considered and tell us where we were wrong — not just confirm what we already did.

Respond inline in this document (copy it to your own fork) or via any format that preserves the section structure. Unanswered questions are fine if you do not have a view.

---

## Section 1 — Your Background (5 min)

Please fill these in so we can weight responses appropriately. Anonymity is an option; see Section 9.

1.1. **Name** (or "anonymous"): _____________________

1.2. **Affiliation** (or "independent"): _____________________

1.3. **Role**: [ ] Registry staff  [ ] Project developer  [ ] Commercial rater  [ ] DeFi protocol  [ ] Academic  [ ] Civil society / NGO  [ ] Other: _______

1.4. **Primary expertise area** (pick up to 3): [ ] Removal/CDR  [ ] Forestry/AFOLU  [ ] Methodology design  [ ] MRV/verification  [ ] Additionality assessment  [ ] Blockchain infrastructure  [ ] Carbon economics/policy  [ ] Commercial rating methodology  [ ] Community safeguards

1.5. **Years in voluntary carbon markets**: ___

---

## Section 2 — Dimension Weight Elicitation via Best-Worst Scaling (20 min)

### 2.0 Context and Instructions

Our framework scores carbon credits on **6 active dimensions** (co-benefits was moved to a safeguards-gate in v0.4 and carries weight 0; Section 3 revisits that decision). The current v0.5 weights are:

| # | Dimension | Code | Current weight | What it captures |
|---|-----------|------|----------------|------------------|
| 1 | Removal Type Hierarchy | `removal_type` | 0.25 | Engineered removal vs. avoidance; CDR permanence class |
| 2 | Additionality | `additionality` | 0.20 | Would the activity have happened without carbon finance? |
| 3 | Permanence | `permanence` | 0.175 | Duration and security of carbon storage |
| 4 | MRV Grade | `mrv_grade` | 0.20 | Measurement, reporting, verification rigor |
| 5 | Vintage Year | `vintage_year` | 0.10 | Age of the credit; regulatory and methodological currency |
| 6 | Registry & Methodology | `registry_methodology` | 0.075 | Registry tier and ICVCM CCP alignment |

**Your task in this section is NOT to assign weights directly.** Instead, you will complete three complementary exercises (BWS choice sets, pairwise comparisons, and scenario judgments) from which we will derive weights statistically. This removes anchoring bias and produces reproducible, publishable results.

### 2.1 Best-Worst Scaling (BWS) Exercise

**Instructions.** Each choice set below shows 4 of the 6 dimensions. For each set, please mark:

- **MOST**: Which of these 4 dimensions is the **most important** for determining carbon credit quality?
- **LEAST**: Which of these 4 dimensions is the **least important** for determining carbon credit quality?

You must select exactly one MOST and one LEAST per set. The two remaining dimensions are left unmarked. There are no right or wrong answers — we want your professional judgment.

**Tip:** Think about which single dimension, if you could only assess one, would tell you the most (or least) about whether a credit represents a real, high-quality tonne of CO₂ equivalent.

---

**Set 1 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Removal Type Hierarchy | [ ] | [ ] |
| B | Additionality | [ ] | [ ] |
| C | Permanence | [ ] | [ ] |
| D | MRV Grade | [ ] | [ ] |

**Set 2 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Removal Type Hierarchy | [ ] | [ ] |
| B | Additionality | [ ] | [ ] |
| C | Permanence | [ ] | [ ] |
| D | Vintage Year | [ ] | [ ] |

**Set 3 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Removal Type Hierarchy | [ ] | [ ] |
| B | Additionality | [ ] | [ ] |
| C | Permanence | [ ] | [ ] |
| D | Registry & Methodology | [ ] | [ ] |

**Set 4 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Removal Type Hierarchy | [ ] | [ ] |
| B | Additionality | [ ] | [ ] |
| C | MRV Grade | [ ] | [ ] |
| D | Vintage Year | [ ] | [ ] |

**Set 5 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Removal Type Hierarchy | [ ] | [ ] |
| B | Additionality | [ ] | [ ] |
| C | MRV Grade | [ ] | [ ] |
| D | Registry & Methodology | [ ] | [ ] |

**Set 6 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Removal Type Hierarchy | [ ] | [ ] |
| B | Additionality | [ ] | [ ] |
| C | Vintage Year | [ ] | [ ] |
| D | Registry & Methodology | [ ] | [ ] |

**Set 7 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Removal Type Hierarchy | [ ] | [ ] |
| B | Permanence | [ ] | [ ] |
| C | MRV Grade | [ ] | [ ] |
| D | Vintage Year | [ ] | [ ] |

**Set 8 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Removal Type Hierarchy | [ ] | [ ] |
| B | Permanence | [ ] | [ ] |
| C | MRV Grade | [ ] | [ ] |
| D | Registry & Methodology | [ ] | [ ] |

**Set 9 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Removal Type Hierarchy | [ ] | [ ] |
| B | Permanence | [ ] | [ ] |
| C | Vintage Year | [ ] | [ ] |
| D | Registry & Methodology | [ ] | [ ] |

**Set 10 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Removal Type Hierarchy | [ ] | [ ] |
| B | MRV Grade | [ ] | [ ] |
| C | Vintage Year | [ ] | [ ] |
| D | Registry & Methodology | [ ] | [ ] |

**Set 11 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Additionality | [ ] | [ ] |
| B | Permanence | [ ] | [ ] |
| C | MRV Grade | [ ] | [ ] |
| D | Vintage Year | [ ] | [ ] |

**Set 12 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Additionality | [ ] | [ ] |
| B | Permanence | [ ] | [ ] |
| C | MRV Grade | [ ] | [ ] |
| D | Registry & Methodology | [ ] | [ ] |

**Set 13 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Additionality | [ ] | [ ] |
| B | Permanence | [ ] | [ ] |
| C | Vintage Year | [ ] | [ ] |
| D | Registry & Methodology | [ ] | [ ] |

**Set 14 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Additionality | [ ] | [ ] |
| B | MRV Grade | [ ] | [ ] |
| C | Vintage Year | [ ] | [ ] |
| D | Registry & Methodology | [ ] | [ ] |

**Set 15 of 15**

| | Dimension | MOST | LEAST |
|---|-----------|------|-------|
| A | Permanence | [ ] | [ ] |
| B | MRV Grade | [ ] | [ ] |
| C | Vintage Year | [ ] | [ ] |
| D | Registry & Methodology | [ ] | [ ] |

---

**Design note for respondents.** The 15 sets above constitute a complete Balanced Incomplete Block Design — BIBD(6, 15, 10, 4, 6). Each dimension appears in exactly 10 of the 15 sets, and every pair of dimensions co-appears in exactly 6 sets. This ensures that every dimension is compared against every other dimension an equal number of times, eliminating positional and frequency biases. The design is the unique (up to isomorphism) complement of the (6,2)-design, i.e., all C(6,4)=15 four-element subsets of the six dimensions.

### 2.2 Pairwise Comparison Exercise

The BWS exercise produces a full importance ranking. The following 5 pairwise comparisons serve as a cross-validation, specifically targeting pairs where our current weights are close or where the ordering matters most for grade assignments.

**Instructions.** For each pair, imagine you can assess a carbon credit on **only one** of the two dimensions. Which single dimension would give you more information about the credit's true quality?

**Pair 1: Removal Type Hierarchy vs. Additionality**
*(Current weights: 0.25 vs. 0.20 — the two heaviest dimensions)*

> If I could only assess ONE: [ ] Removal Type Hierarchy  [ ] Additionality  [ ] Genuinely equal

**Pair 2: Permanence vs. MRV Grade**
*(Current weights: 0.175 vs. 0.20 — both mid-tier)*

> If I could only assess ONE: [ ] Permanence  [ ] MRV Grade  [ ] Genuinely equal

**Pair 3: Vintage Year vs. Registry & Methodology**
*(Current weights: 0.10 vs. 0.075 — the two lightest dimensions)*

> If I could only assess ONE: [ ] Vintage Year  [ ] Registry & Methodology  [ ] Genuinely equal

**Pair 4: Removal Type Hierarchy vs. MRV Grade**
*(Cross-tier comparison: 0.25 vs. 0.20)*

> If I could only assess ONE: [ ] Removal Type Hierarchy  [ ] MRV Grade  [ ] Genuinely equal

**Pair 5: Additionality vs. Permanence**
*(Cross-tier comparison: 0.20 vs. 0.175)*

> If I could only assess ONE: [ ] Additionality  [ ] Permanence  [ ] Genuinely equal

**2.2.1 Confidence.** For each pair above where you did not answer "genuinely equal," how confident are you? (1 = slight lean, 5 = absolutely certain)

| Pair | Confidence (1-5) |
|------|-------------------|
| Pair 1 | ___ |
| Pair 2 | ___ |
| Pair 3 | ___ |
| Pair 4 | ___ |
| Pair 5 | ___ |

### 2.3 Scenario-Based Validation

The BWS and pairwise exercises measure stated importance. The following scenario pairs test whether your revealed preferences are consistent. Each pair of hypothetical credits differs on **exactly one** dimension; all other dimensions are held equal.

**Scenario A: Testing Removal Type weight**

| | Removal Type | Additionality | Permanence | MRV Grade | Vintage Year | Registry & Methodology |
|---|---|---|---|---|---|---|
| Credit A1 | **90** | 70 | 70 | 70 | 70 | 70 |
| Credit A2 | **40** | 70 | 70 | 70 | 70 | 70 |

> Which credit is higher quality? [ ] A1 (obviously)  [ ] A2 (surprisingly)
> How much does the difference matter? [ ] Massive (2+ grade difference)  [ ] Large (1-2 grades)  [ ] Moderate (<1 grade)  [ ] Small

**Scenario B: Testing MRV Grade vs. Additionality relative weight**

| | Removal Type | Additionality | Permanence | MRV Grade | Vintage Year | Registry & Methodology |
|---|---|---|---|---|---|---|
| Credit B1 | 50 | 50 | 50 | **90** | 50 | 50 |
| Credit B2 | 50 | **90** | 50 | 50 | 50 | 50 |

> Which credit is higher quality? [ ] B1 (strong MRV, weak additionality)  [ ] B2 (strong additionality, weak MRV)  [ ] Genuinely equal

**Scenario C: Testing Permanence vs. Vintage Year relative weight**

| | Removal Type | Additionality | Permanence | MRV Grade | Vintage Year | Registry & Methodology |
|---|---|---|---|---|---|---|
| Credit C1 | 60 | 60 | **90** | 60 | **40** | 60 |
| Credit C2 | 60 | 60 | **40** | 60 | **90** | 60 |

> Which credit is higher quality? [ ] C1 (durable storage, old vintage)  [ ] C2 (recent vintage, fragile storage)  [ ] Genuinely equal

**2.3.1 Justification (optional free text).** If any scenario answer surprised you or conflicted with your BWS responses, explain why.

> _Free text:_

### 2.4 Missing or Redundant Dimensions

**2.4.1 Are any dimensions missing?** v0.5 has six active dimensions plus the safeguards-gate. If you would add a seventh active dimension (e.g., a dedicated leakage dimension, a policy-risk dimension, a buffer pool adequacy dimension), name it and sketch how it would interact with the existing six.

> _Free text:_

**2.4.2 Are any dimensions redundant?** v0.4's sensitivity analysis found some overlap between `removal_type` and `permanence` in a previous edition but the leave-one-out analysis showed permanence doing independent work. Do you see dimensions that should be merged?

> _Free text:_

---

## Section 3 — The Safeguards-Gate Decision (10 min)

v0.4 adopted the safeguards-gate mechanism (Alt-3 in `docs/methodology-gate-v0.4.md`): co-benefits is dropped from the weighted composite and becomes a disqualifier-style gate (`communityHarm` caps the grade at BBB). The three options we rejected:

- **Rev-1+2** (the original naive proposal): Rev-1 reweight + `+5` additive bonus if removal_type >= 90 AND permanence >= 90 AND mrv_grade >= 85
- **Alt-1** (multiplicative): Rev-1 reweight + `x1.05` multiplier on the same indicator
- **Alt-2** (geomean core): `composite = 0.60 x geomean(removal_type, permanence, mrv_grade) + 0.40 x linear(other 4)`

**3.1. Pick your preferred mechanism.** [ ] Safeguards-gate (Alt-3, v0.4)  [ ] Rev-1+2 bonus  [ ] Alt-1 multiplicative  [ ] Alt-2 geomean core  [ ] A different mechanism (describe below)

**3.2. Argue against your second-favorite.** What would you say to convince us that your second choice is strictly worse than your first?

> _Free text:_

**3.3. Does the safeguards-gate correctly encode Berg et al. (2025)?** Berg et al. found that buyers pay a 2x premium for co-benefit narratives regardless of underlying integrity. Our argument is that rewarding co-benefits in a quality rating reinforces this mispricing. Do you accept this reasoning?

> _[ ] Yes, clearly / [ ] Yes, with caveats / [ ] No, co-benefits are priced for real reasons not narrative / free text:_

**3.4. Is BBB the right cap level for `communityHarm`?** Higher-quality caps (B) would prevent harmful projects from entering any pool; lower caps would admit them to low-grade pools. The v0.4 choice admits them but keeps them out of premium pools.

> _[ ] BBB is right / [ ] BB is better / [ ] B is better / [ ] A is better / free text:_

**3.5. Should registries self-attest the `communityHarm` flag, or should it be externally attestable by civil society?** The v0.4 contract allows only allowlisted raters to set disqualifiers. Many community-harm concerns are raised by NGOs after a project is already certified.

> _Free text:_

---

## Section 4 — Disqualifier Lattice (10 min)

v0.4 has six disqualifiers with three distinct cap levels:

| Flag | Cap |
|------|-----|
| `doubleCounting` | B |
| `failedVerification` | B |
| `humanRights` | B |
| `sanctionedRegistry` | BB |
| `noThirdParty` | BBB |
| `communityHarm` | BBB |

**4.1. Are the caps calibrated correctly?** Any changes you would propose?

> _Free text:_

**4.2. Are there disqualifiers you would add?** Candidates we considered but did not include: `leakage_evidence`, `sanctions_exposure`, `reversal_event_in_buffer_pool`, `methodology_under_active_icvcm_review`.

> _Free text:_

**4.3. Are there disqualifiers you would remove?** Specifically, is `noThirdParty` (caps at BBB) still meaningful given that the framework already requires attestation via a rater role in v0.4, and the v0.5 decentralized-rater design doc (`docs/decentralized-rater-design.md`) assumes registry-primary attesters?

> _Free text:_

---

## Section 5 — Grade Boundaries (5 min)

v0.4 uses these boundaries (composite in 0-100):

| Grade | Min |
|-------|-----|
| AAA | 90 |
| AA | 75 |
| A | 60 |
| BBB | 45 |
| BB | 30 |
| B | 0 |

**5.1. Are these boundaries defensible?** Commercial agencies use different scales (Sylvera AAA-D, BeZero AAA-D 8-point, Calyx risk-based). We chose 6 tiers with 15-point bands above 30 and one 30-point band at the bottom.

> _Free text:_

**5.2. Should there be sub-grades** (AAA+, AA-)? This is a v0.6 question, but your view would help us decide whether to signal it in v0.5.

> _[ ] Yes / [ ] No / [ ] Maybe later / free text:_

---

## Section 6 — Pilot Scoring Review (10 min)

Please skim `data/pilot-scoring/credits.json` and `data/tokenized-pilot/credits.json`. You do not need to review all 39 credits — we are interested in whether any specific scoring strikes you as obviously wrong.

**6.1. Which credits, if any, did we score wrong?** For each, specify the dimension(s) and direction.

> _Free text (e.g. "C010 Kenya cookstoves — permanence should be 15 not 8, cookstoves have some residual permanence from the displaced deforestation"):_

**6.2. C004 / T010 Charm Industrial is our AAA fragility flag** (0.15 above the AAA boundary under v0.4; distributional analysis gives P(AAA)=0.521). Do you think Charm is appropriately AAA, or is our scoring of it too generous, or too harsh?

> _Free text:_

**6.3. Toucan BCT (T001) scores 31.1 BB under v0.4.** Is this in the right ballpark for the historical BCT pool, too harsh, or too generous?

> _[ ] Right / [ ] Too harsh (should be BBB+) / [ ] Too generous (should be B) / free text:_

**6.4. The tokenized pilot has no nature-based AA credits.** (Section 3.1 of `data/tokenized-pilot/analysis.md`.) Is this a true observation about the on-chain carbon market, or an artifact of our dataset construction?

> _Free text:_

---

## Section 7 — On-Chain Architecture (5 min, optional for non-technical reviewers)

These questions are primarily for DeFi protocol designers and blockchain engineers. Skip if not relevant.

**7.1. Is EAS (Ethereum Attestation Service) the right base layer** for the decentralized rater (per `docs/decentralized-rater-design.md`)?

> _[ ] Yes / [ ] No, prefer UMA / [ ] No, prefer multi-rater quorum / [ ] No, prefer registry-attester with expert challenge / free text:_

**7.2. Is the off-chain = on-chain invariant the right constraint?** We committed to keeping the Python scorer and Solidity contract bit-identical. This rules out mechanisms that require cube roots or fixed-point math. A reviewer who thinks on-chain is the wrong venue might want us to drop this.

> _[ ] Keep the invariant / [ ] Drop it; composability matters less than methodology / free text:_

**7.3. Is 18 months the right rating freshness window?** The v0.4 contract supports any `expiresAt` but does not enforce a policy. Annual is the default suggestion; 18 months is our preference to buffer verification delays.

> _[ ] 12 months / [ ] 18 months / [ ] 24 months / [ ] Methodology-specific (describe) / free text:_

---

## Section 8 — Integration and Use Cases (5 min)

**8.1. Would your organization integrate this framework?** If yes, what would you need to see in v0.5 / v0.6 to make that decision easier?

> _Free text:_

**8.2. Is there an existing framework we should merge with rather than compete with?** ICVCM CCP, CCQI, and RMI Carbon Crediting Data Framework are the three most obvious candidates; each has overlap with our rubric.

> _Free text:_

**8.3. What would kill this project?** We want to know the single most likely failure mode from your perspective.

> _Free text:_

---

## Section 9 — Logistics and Attribution

**9.1. May we attribute your responses in v0.6 acknowledgements?** [ ] Yes, by name  [ ] Yes, by affiliation only  [ ] Anonymous  [ ] Do not reference at all

**9.2. Are you available for a 30-minute follow-up call?** [ ] Yes  [ ] No  [ ] Only if asked specific questions in writing first

**9.3. May we share your responses (excluding name, if anonymous) with other v0.6 reviewers** so they can see a spectrum of views? [ ] Yes  [ ] No

**9.4. Deadline.** We are aiming to incorporate v0.6 expert feedback before the end of the current workshop cycle. Completed questionnaires before that date carry the most weight.

---

## Section 10 — Anything Else

**10.1. What did we not ask that we should have?**

> _Free text:_

**10.2. What is the single most important thing you would change about v0.5?**

> _Free text:_

---

## Appendix A — BWS Analysis Plan

This appendix explains how your BWS responses (Section 2.1) will be analyzed. We include it for transparency and so that methodologically-oriented respondents can evaluate the rigor of our weight derivation.

### A.1 Count Analysis (Individual Level)

For each respondent *r* and each dimension *i*:

```
BWS_score(r, i) = B(r, i) - W(r, i)
```

where B(r, i) is the number of times respondent *r* selected dimension *i* as MOST important, and W(r, i) is the number of times *r* selected it as LEAST important.

In the BIBD(6, 15, 10, 4, 6) design, each dimension appears in exactly 10 of the 15 choice sets, so:
- Maximum possible BWS score: +10 (chosen as MOST in all 10 appearances)
- Minimum possible BWS score: -10 (chosen as LEAST in all 10 appearances)
- Expected score under random responding: 0

The individual-level **standardized BWS score** is:

```
BWS_std(r, i) = BWS_score(r, i) / 10
```

ranging from -1.0 (always least) to +1.0 (always most).

### A.2 Aggregated Count Analysis

Across all *N* respondents, the aggregate BWS score for dimension *i* is:

```
BWS_agg(i) = (1/N) * SUM_r [ BWS_score(r, i) ]
```

We report 95% confidence intervals via bootstrap (10,000 resamples with replacement across respondents).

### A.3 Converting BWS Scores to Weights

Raw BWS scores can be negative, so we apply a linear transformation before normalizing:

```
shifted(i) = BWS_agg(i) - min_j(BWS_agg(j))
weight(i) = shifted(i) / SUM_j(shifted(j))
```

This produces ratio-scale weights that sum to 1.0. The ordering is identical to the raw BWS ordering; only the scale changes.

### A.4 Multinomial Logit Model (Sensitivity Check)

As a robustness check, we fit a multinomial logit (MNL) model to the paired best-worst choices. For each choice set *s* with items *C_s*, the probability that respondent *r* selects item *i* as best and item *j* as worst is:

```
P(best=i, worst=j | C_s) = exp(lambda_i - lambda_j) / SUM_{k!=l in C_s} exp(lambda_k - lambda_l)
```

The estimated lambda parameters are on a log-ratio scale. Converting to weights:

```
weight_MNL(i) = exp(lambda_i) / SUM_j exp(lambda_j)
```

We report both count-based and MNL-based weights and note any divergences. The MNL model is estimated using maximum likelihood; we report log-likelihood, AIC, and BIC.

### A.5 Cross-Validation with Pairwise Data

The 5 pairwise comparisons (Section 2.2) are analyzed independently:
- Each pair where a respondent selects dimension *i* over *j* is tallied as a binomial trial.
- We compute the proportion preferring each dimension, with exact binomial 95% CIs.
- These proportions are compared with the BWS-implied pairwise ordering to check consistency.

The confidence ratings (1-5 scale) are used as weights in a weighted binomial analysis as a sensitivity variant.

### A.6 Scenario Consistency Check

The 3 scenario pairs (Section 2.3) serve as face-validity checks:
- **Scenario A** tests whether respondents agree that a 50-point swing on removal_type produces a material quality difference (expected: yes, by 1-2+ grades under current weights).
- **Scenario B** tests the relative weight of MRV vs. additionality. If BWS-derived weights give MRV > additionality, we expect more respondents to choose B1; if additionality > MRV, B2.
- **Scenario C** tests permanence vs. vintage. Under current weights (0.175 vs. 0.10), C1 should dominate.

We report the fraction of respondents whose scenario choices are consistent with their own BWS-implied ordering.

### A.7 Comparison with Current v0.5 Weights

The primary deliverable is a comparison table:

| Dimension | Current weight | BWS count weight | BWS MNL weight | Pairwise consistency |
|-----------|----------------|-------------------|-----------------|----------------------|
| removal_type | 0.250 | — | — | — |
| additionality | 0.200 | — | — | — |
| permanence | 0.175 | — | — | — |
| mrv_grade | 0.200 | — | — | — |
| vintage_year | 0.100 | — | — | — |
| registry_methodology | 0.075 | — | — | — |

We test the null hypothesis that the BWS-derived weight vector equals the current v0.5 weight vector using a chi-squared goodness-of-fit test:

```
chi2 = N * SUM_i [ (w_BWS(i) - w_current(i))^2 / w_current(i) ]
```

with 5 degrees of freedom (6 categories minus 1 for the sum-to-1 constraint). Rejection at alpha = 0.05 indicates the expert consensus differs significantly from our current calibration.

Additionally, we report:
- Spearman rank correlation between BWS-derived and current weight orderings
- Maximum absolute deviation: max_i |w_BWS(i) - w_current(i)|
- Whether the BWS data support the current 3-tier structure (heavy: removal+additionality, mid: permanence+MRV, light: vintage+registry)

### A.8 Decision Rule for v0.6

The v0.6 weights will be set as follows:
1. If the chi-squared test is non-significant (p > 0.05) and rank ordering matches, **retain current weights** (expert consensus is consistent with our calibration).
2. If the chi-squared test is significant but rank ordering matches, **adopt BWS-derived weights** (magnitudes differ but structure is confirmed).
3. If the rank ordering differs, **investigate dimension by dimension** — report the per-dimension bootstrap CIs and adopt BWS weights only for dimensions where the BWS 95% CI excludes the current weight.
4. In all cases, results are reported transparently in the v0.6 paper with full analysis code in `scripts/bws_analysis.py`.

### A.9 Required Sample Size

For a BIBD with 15 choice sets and 6 items, prior BWS studies (Louviere et al., 2015; Aizaki et al., 2015) suggest N >= 20 respondents for stable count-based weights and N >= 30 for MNL estimation. Our target of 15-25 expert respondents is sufficient for count analysis. If fewer than 20 respond, we rely on count analysis only and note the MNL limitation.

---

## Appendix B — BIBD Verification

For the reader who wishes to verify the design balance, the 15 choice sets are enumerated here with their composition. Each set contains 4 of the 6 dimensions (labeled 1-6 per the table in Section 2.0).

| Set | Dimensions included | Dimensions excluded |
|-----|---------------------|---------------------|
| 1 | {1, 2, 3, 4} | {5, 6} |
| 2 | {1, 2, 3, 5} | {4, 6} |
| 3 | {1, 2, 3, 6} | {4, 5} |
| 4 | {1, 2, 4, 5} | {3, 6} |
| 5 | {1, 2, 4, 6} | {3, 5} |
| 6 | {1, 2, 5, 6} | {3, 4} |
| 7 | {1, 3, 4, 5} | {2, 6} |
| 8 | {1, 3, 4, 6} | {2, 5} |
| 9 | {1, 3, 5, 6} | {2, 4} |
| 10 | {1, 4, 5, 6} | {2, 3} |
| 11 | {2, 3, 4, 5} | {1, 6} |
| 12 | {2, 3, 4, 6} | {1, 5} |
| 13 | {2, 3, 5, 6} | {1, 4} |
| 14 | {2, 4, 5, 6} | {1, 3} |
| 15 | {3, 4, 5, 6} | {1, 2} |

**Balance properties:**
- *b* = 15 blocks (choice sets)
- *v* = 6 treatments (dimensions)
- *r* = 10 (each dimension appears in exactly 10 sets)
- *k* = 4 (each set contains exactly 4 dimensions)
- *lambda* = 6 (each pair of dimensions co-occurs in exactly 6 sets)
- Verification: *lambda* = r(k-1)/(v-1) = 10 * 3 / 5 = 6. Confirmed.

---

## Appendix C — References for Methodology

- Doyle, J. R., Green, R. H., & Bottomley, P. A. (1997). Judging relative importance: Direct rating and point allocation are not equivalent. *Organizational Behavior and Human Decision Processes*, 70(1), 65-72.
- Finn, A., & Louviere, J. J. (1992). Determining the appropriate response to evidence of public concern: The case of food safety. *Journal of Public Policy & Marketing*, 11(2), 12-25.
- Louviere, J. J., Flynn, T. N., & Marley, A. A. J. (2015). *Best-Worst Scaling: Theory, Methods and Applications*. Cambridge University Press.
- Aizaki, H., Nakatani, T., & Sato, K. (2015). *Stated Preference Methods Using R*. CRC Press.
- Saaty, T. L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill.
- Berg, T., et al. (2025). The narrative premium in voluntary carbon markets. [Per project bibliography.]

---

### Submission

Send the completed questionnaire to: _[contact details TBD during v0.6 outreach]_

Thank you for your time. v0.6 will include a diff document showing explicitly which decisions were informed by which responses, so you can see the impact of your feedback. The BWS analysis code will be published as `scripts/bws_analysis.py` with all anonymized response data, enabling full reproducibility.
