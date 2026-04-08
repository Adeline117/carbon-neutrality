# Pilot Scoring Analysis

*25 illustrative credits, hand-scored against the v0.2 rubrics*

This analysis is a **methodology stress test**, not a formal rating of the named projects. Per-dimension scores were assigned by the authors based on public project documentation and archetype-level knowledge. The goal is to check whether the proposed weights and bands produce intuitively defensible grades across the full quality spectrum, and to surface any weighting issues that warrant revision before expert consultation.

## 1. Overall distribution

| Grade | Count | Share | Score range |
|-------|-------|-------|-------------|
| AAA   | 0     | 0%    | —           |
| AA    | 7     | 28%   | 75.7 – 86.8 |
| A     | 4     | 16%   | 63.3 – 70.5 |
| BBB   | 4     | 16%   | 50.9 – 56.5 |
| BB    | 3     | 12%   | 31.2 – 38.4 |
| B     | 7     | 28%   | 15.4 – 29.3 |

Reference benchmarks: MSCI's 2025 Integrity Report rated **<10%** of 4,400+ projects AAA-A. Our pilot distribution is somewhat more forgiving (44% AA-A combined), which reflects deliberate spectrum sampling — not a claim that the market is 44% high quality.

## 2. Key findings

### 2.1 No credit reached AAA (finding: co-benefits weight compresses engineered removal)

Climeworks Orca -- the top-scoring credit -- received 86.8, **3.2 points short of AAA**. Inspection reveals the binding constraint: engineered removal projects score ~15-22 on co-benefits (industrial projects, no direct SDG alignment) while the weight on that dimension is 10%. This single dimension costs DACCS roughly 7-8 points on the composite.

**Implication**: the current weighting makes it mathematically difficult for any pure-engineered-removal credit to reach AAA regardless of how rigorous the removal, storage, and MRV are. This inverts the Oxford Principles, which place engineered removal with durable storage at the top of the hierarchy.

**Recommended revisions to explore in Phase 2 expert consultation:**
- Option A: Introduce a **removal-type boost**: +5 composite for credits with removal_type >= 90 and permanence >= 90.
- Option B: Reduce co_benefits weight to 5%, redistribute to removal_type (to 22.5%) or MRV (to 17.5%).
- Option C: Make co_benefits a *safeguards gate* rather than a weighted dimension — score 0 on co_benefits acts as a grade cap at BBB if and only if there is documented community/environmental harm; otherwise it doesn't penalize.

The author's prior is toward **Option A**, since it preserves the safeguards function of co_benefits while rewarding high-integrity CDR.

### 2.2 Rating inversion between industrial DAC and nature-based removal

Pacific Biochar (C005: 80.95) scores nearly identically to Heirloom DAC (C002: 85.3) and *above* CarbonCure (C003: 79.95) despite CarbonCure's much more durable storage. The strong biochar co_benefits score (60) compensates for slightly weaker permanence and registry bases. This may or may not be desired behavior.

**Interpretation**: The framework currently rewards projects that are *balanced* across all dimensions more than it rewards *peaks* in the most important dimensions. For a quality rating, this is a debatable choice -- a "jack of all trades" AFOLU credit and a "specialist" CDR credit can end up at the same grade even though they represent fundamentally different climate products.

### 2.3 Toucan BCT pool composition in retrospect

Of the 25 credits, 10 are tagged as historically "BCT-pooled" or eligible:

| ID | Credit | Final grade |
|----|--------|-------------|
| C007 | Brazilian reforestation (CCB Gold) | AA |
| C009 | SE Asian afforestation | A |
| C015 | VCS afforestation 2018 vintage | BBB |
| C017 | Grid-connected solar (India) | BB |
| C018 | REDD+ Cordillera Azul | BB |
| C019 | Rimba Raya REDD+ | B |
| C020 | Chinese wind 2014 | B |
| C021 | Large hydro 2015 | B |
| C022 | Kariba REDD+ | B |
| C023 | HFC-23 destruction 2012 | B |

**Finding**: 6 of 10 BCT-eligible credits in this sample grade B (lowest tier). Two grade BB. Only two grade A or above. This maps directly to the "lemons problem" dynamic: BCT's minimal eligibility (any post-2008 VCU) let the B-tier dominate by volume while any AA-grade credits were withdrawn for higher OTC prices. Had the proposed framework existed, a grade-gated pool at A or higher would have admitted only C007 and C009 from this sample.

### 2.4 Vintage dimension is doing most of the pre-Paris work

The `pre_paris_override` (vintage score cap at 20 for vintage < 2016) cleanly separates old credits from new. Credits C020-C025 (all vintage <2016) have vintage scores of 0-20, pulling their composite down by roughly 8-10 points relative to current-vintage counterparts. This override is arguably doing some of the work that `sanctioned_registry` and `no_third_party` disqualifiers are also doing -- which is fine (defense in depth) but worth noting.

### 2.5 Disqualifier interaction is currently invisible

The five disqualifiers in `index.json` never produced a visible grade cap in this dataset, because every flagged credit (C022, C023, C025) already scored low enough to be B on composite alone. **The disqualifiers are backstops, not primary filters.** In a production setting, the disqualifiers would matter for edge cases where an otherwise high-scoring credit has a single catastrophic failure (e.g., discovered double counting mid-life).

**Recommendation**: Add a test case to the dataset where a high-composite credit has a disqualifier flag, so the interaction is demonstrated. Proposed: a hypothetical "C026" with scores matching C007 (Brazilian reforestation) but flagged `double_counting` -- should cap at B.

## 3. Correlation observations

Raw composite scores across the 25 credits show:
- Strong positive correlation between `removal_type` and `permanence` (both track Oxford hierarchy) -- may indicate mild collinearity. Expert review should confirm both are warranted or whether they should be merged.
- `vintage_year` is effectively bimodal: recent credits score 88-100, pre-2016 credits score 0-20. Very few "middle-aged" credits exist in the VCM because most old vintages have either been retired or sit unsold.
- `co_benefits` is the dimension with the largest within-class variance (0-88 for credits of similar technical type), reflecting how much discretion project developers have in pursuing SDG certifications.

## 4. Sensitivity checks (to run in next iteration)

- **Weight perturbation**: Recompute all grades under +/-5pp perturbations to each weight. How many credits change grade? If >20% of credits flip with small perturbations, weights are fragile.
- **Leave-one-out**: Drop each dimension and recompute. Which dimensions are load-bearing vs. redundant?
- **Rank correlation vs MSCI / BeZero**: For credits where commercial ratings are public, how does our ranking correlate? Carbon Market Watch 2023 found significant inter-rater disagreement among commercial agencies, so we should not expect perfect correlation -- but large divergence would warrant investigation.

## 5. Proposed revisions for paper v0.3

1. **Adjust weights** toward removal_type (0.20 -> 0.225) and mrv_grade (0.15 -> 0.175), pulling from co_benefits (0.10 -> 0.075) and registry_methodology (0.10 -> 0.075). Rationale: co_benefits and registry are somewhat overlapping quality proxies; reducing them in favor of direct technical dimensions should produce cleaner signal.
2. **Add a removal bonus**: +5 composite (capped at 100) if removal_type >= 90 AND permanence >= 90 AND mrv_grade >= 85. Preserves Oxford hierarchy at the top of the scale.
3. **Introduce `human_rights` as both a disqualifier and a co_benefits cap at 0** (already in 06_co_benefits.json; ensure contract mirrors).
4. **Add disqualifier interaction test case** (C026 proposed above) to the pilot dataset.
5. **Do not change grade band boundaries** yet; the current boundaries (90/75/60/45/30) produced a defensible distribution.

## 6. Caveats and limitations

- Per-dimension scores were assigned by the authors without a structured expert panel. For any named project, scores should be considered **illustrative archetype** rather than a formal rating.
- The dataset is not a random sample of the VCM; credits were chosen to span the quality spectrum for methodology testing.
- CCQI and commercial rating agency assessments were used for calibration of some credits (e.g., REDD+ rated low) but no single project was scored against a specific commercial rating.
- The analysis does not currently include "C026" or any other disqualifier stress test; this is noted as follow-up.
