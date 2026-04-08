# Pilot Scoring Analysis (v0.4)

*29 credits (25 real-archetype + 4 synthetic disqualifier stress tests), scored against v0.4 rubrics using the safeguards-gate mechanism (`docs/methodology-gate-v0.4.md`).*

This analysis supersedes the v0.3 edition. The v0.3 headline finding — "no credit reached AAA under the current weights" — has been resolved in v0.4; the Oxford hierarchy is now correctly reflected at the top of the scale. New fragility flags have emerged that should be acknowledged in the workshop paper's sensitivity discussion.

## 1. Overall distribution

| Grade | v0.3 count | v0.3 share | v0.4 count | v0.4 share | Score range (v0.4, real credits only) |
|-------|-----------|-----------|-----------|-----------|----------|
| AAA   | 0  | 0%  | **3** | 12% | 90.2 – 95.2 |
| AA    | 7  | 28% | 3     | 12% | 80.05 – 87.2 |
| A     | 4  | 16% | 5     | 20% | 60.9 – 73.9 |
| BBB   | 4  | 16% | 4     | 16% | 46.1 – 59.53 |
| BB    | 3  | 12% | 2     | 8%  | 33.27 – 36.52 |
| B     | 7  | 28% | 8     | 32% | 16.38 – 28.57 |

Synthetic stress tests (C026–C029) are excluded from the distribution above. They demonstrate that each disqualifier cap tier triggers correctly; see §4.

Reference: MSCI's 2025 Integrity Report rated fewer than 10% of 4,400+ projects AAA-A; our pilot at 44% AA-A remains spectrum-sampled rather than VCM-representative.

## 2. Key findings

### 2.1 Oxford inversion resolved

Three credits now reach AAA, all of them engineered carbon dioxide removal with durable storage — exactly what the Oxford Principles say a quality rating should place at the top:

| ID | Credit | Composite | Grade |
|----|--------|-----------|-------|
| C001 | Climeworks Orca (DACCS + geological storage) | 95.20 | AAA |
| C002 | Heirloom DAC + concrete mineralization | 93.05 | AAA |
| C004 | Charm Industrial bio-oil injection | 90.15 | AAA |

Under v0.3 these scored 86.8, 85.3, and 83.0 respectively — all AA. The blocking factor was the 10% weight on co_benefits, which systematically penalized industrial CDR projects that have no SDG narrative. Under v0.4's safeguards-gate (`docs/methodology-gate-v0.4.md`), co_benefits no longer enters the composite, and the 7.5 points of freed weight are redistributed into removal_type, permanence, and mrv_grade.

The v0.4 change is also strictly *better at the middle of the scale*. The Rev-1+2 proposal considered in the A2 gate would have left C004 (Charm Industrial) stuck at 85.0 AA because its mrv_grade of 82 just missed the arbitrary 85 bonus threshold. Under Alt-3 (the chosen mechanism), Charm scores 90.15 AAA on pure weights — no threshold gymnastics.

### 2.2 BCT retrospective — stable reframing

The v0.3 paper's Toucan retrospective claimed "only 2 of 10 BCT-eligible credits in our pilot would have passed a grade-A gated pool." That finding is preserved under v0.4, but the grade distribution of the top two changes:

| ID | Credit | v0.3 grade | v0.4 grade |
|----|--------|-----------|-----------|
| C007 | Pachama Brazilian reforestation | **AA** (75.7) | **A** (73.9) |
| C009 | SE Asian VCS afforestation | A (66.4) | A (66.2) |
| C015 | VCS afforestation 2018 vintage | BBB | BBB |
| C017 | Grid-connected solar (India) | BB | BB |
| C018 | REDD+ Cordillera Azul | BB | **B** |
| C019 | Rimba Raya REDD+ | B | B |
| C020 | Chinese CDM wind 2014 | B | B |
| C021 | Large hydro Brazil 2015 | B | B |
| C022 | Kariba REDD+ | B | B |
| C023 | HFC-23 destruction 2012 | B | B |

**New phrasing for paper §7.2**: "Of 10 BCT-eligible credits in our pilot, 2 grade A or higher, 1 BBB, 1 BB, 6 at B. A grade-A gated pool would have admitted only C007 and C009 — 20% of the BCT population."

C007 moves from fragile-AA (v0.3 had it at 75.3 under the proposed Rev-1+2 reweight, just 0.3 above the AA boundary) to stable-A (v0.4 at 73.9 with a 13.9-point buffer to the BBB boundary). This is a **cleaner reframing** than preserving the AA grade through a magic-number bonus, and the substantive finding — BCT was dominated by junk — is identical.

Cordillera Azul (C018) also correctly drops from BB to B, matching the Carbon Market Watch 2023 assessment that flagged the project.

### 2.3 New fragility flags (see §3 for data)

Three credits now sit within 1 point of a grade boundary and should be flagged to expert reviewers:

| ID | Credit | Grade | Composite | Buffer | Direction |
|----|--------|-------|-----------|--------|-----------|
| C004 | Charm Industrial bio-oil | AAA | 90.15 | **0.15** | down → AA |
| C011 | Adipic acid N2O destruction | BBB | 59.53 | **0.47** | up → A |
| C014 | Plan Vivo agroforestry | A | 60.90 | **0.90** | down → BBB |

**C004 is the v0.4 analog of v0.3's C007 fragility.** It is the weakest of the three AAA credits and a 1-point downward rescoring on any dimension would flip it to AA. This should be explicitly flagged in paper §7 as the "load-bearing AAA boundary" credit: any later rescoring by an expert reviewer that moves Charm below 90 changes the headline distribution from 3 AAA to 2 AAA.

**C011 and C014 represent the new sub-AA fragility cluster.** C011 (industrial N2O abatement) would benefit from any rescoring that moves it from BBB to A. C014 (smallholder agroforestry) would lose A if rescored slightly downward.

### 2.4 Co-benefit-heavy credits: expected compression, no grade flips

The Alt-3 safeguards-gate explicitly removes the co_benefits reward. Credits that relied on strong SDG narratives lose composite points but do not flip grades in this pilot:

| Credit | v0.3 | v0.4 | Δ | Flip? |
|--------|------|------|---|-------|
| C006 Husk biochar (Cambodia) | 81.0 | 80.05 | −0.95 | No (still AA) |
| C010 Kenya cookstoves | 51.8 | 46.1 | −5.70 | No (still BBB) |
| C014 Plan Vivo agroforestry | 63.3 | 60.9 | −2.40 | No (still A, narrow) |
| C016 Ghana cookstoves 2019 | 38.4 | 33.27 | −5.13 | No (still BB) |
| C013 Mangrove blue-carbon | 70.5 | 68.4 | −2.10 | No (still A) |

Cookstove projects take the largest hit (−5.7), as expected — they are fundamentally avoidance-based with weak permanence but strong co-benefit narratives. The framework now refuses to let that narrative push them above BBB. This is the intended Alt-3 behavior.

## 3. Sensitivity results

Generated by `python3 score.py --sensitivity`; full output in `sensitivity.md`.

### 3.1 Weight perturbation (±5 percentage points per dimension)

| Dimension | Weight | +5pp flips | −5pp flips |
|-----------|--------|-----------|-----------|
| removal_type | 0.250 | 0/29 | 1/29 |
| additionality | 0.200 | 1/29 | 0/29 |
| permanence | 0.175 | 2/29 | 2/29 |
| mrv_grade | 0.200 | 2/29 | 0/29 |
| vintage_year | 0.100 | 2/29 | 3/29 |
| co_benefits | 0.000 (gate) | 2/29 | 0/29 |
| registry_methodology | 0.075 | 2/29 | 1/29 |

**Interpretation**: Most perturbations flip 0-2 credits, which is acceptable for a 29-credit dataset. The highest-flip dimension is **vintage_year** at −5pp (3 flips), which is expected because vintage scores are bimodal in this dataset (recent credits ~88-100, pre-2016 ~0-20), so small weight changes produce boundary-adjacent effects for the cluster of old credits. No single perturbation produces ≥4 grade changes, so the v0.4 weights are not fragile in aggregate.

### 3.2 Leave-one-out (drop each dimension, redistribute proportionally)

| Dropped dimension | Flips |
|-------------------|-------|
| removal_type | 4/29 |
| additionality | 2/29 |
| permanence | 5/29 |
| mrv_grade | 0/29 |
| vintage_year | 3/29 |
| registry_methodology | 1/29 |

**Interpretation**:
- **permanence** is the highest-impact dimension (5 flips when dropped) — it is doing real work, not merely collinear with removal_type as the v0.3 analysis worried. This argues *against* the 7→6 dimension collapse proposed for v0.6.
- **mrv_grade** dropping produces zero flips. This looks like redundancy, but it is actually an artifact of MRV scores being positively correlated with other technical dimensions in the pilot (high-quality CDR has high MRV, low-quality avoidance has low MRV), so redistributing mrv weight to similarly-ranked dimensions preserves grades. A random-MRV stress test would probably flip more credits.
- **removal_type** dropping produces 4 flips, confirming it is a load-bearing dimension even with v0.4's increased weight.

### 3.3 Key-credit boundary buffer

See §2.3 for the fragility flags (C004, C011, C014). All other spotlight credits (C001, C002, C007) have buffers greater than 3 points to their nearest relevant boundary and are not sensitivity-fragile.

## 4. Disqualifier stress tests (C026–C029)

Four synthetic credits were added to verify that each disqualifier cap tier triggers correctly when the nominal grade exceeds the cap. These credits do not represent real projects; they are a validation of the grade-capping lattice.

| ID | Nominal composite | Nominal grade | Disqualifier | Cap tier | Final grade | Pass? |
|----|-------------------|---------------|--------------|----------|-------------|-------|
| C026 | 88.05 | AA | `double_counting` | B | B | ✓ |
| C027 | 81.72 | AA | `sanctioned_registry` | BB | BB | ✓ |
| C028 | 79.12 | AA | `no_third_party` | BBB | BBB | ✓ |
| C029 | 78.53 | AA | `community_harm` (v0.4) | BBB | BBB | ✓ |

All four caps apply correctly. The disqualifier lattice is validated.

**C029 is the first test of the v0.4 safeguards-gate mechanism.** The credit has technical scores matching a mid-grade AA credit but is flagged `community_harm` via the co_benefits rubric's 0-9 "None / negative externalities" band. The gate correctly caps at BBB: the framework recognizes the technical climate value but refuses to admit the credit into premium pools where community impact is a buyer expectation.

## 5. Caveats and limitations

- **Per-dimension scores for real credits are illustrative**, hand-assigned by the authors based on public documentation. They are not a formal rating of the named projects. Any numeric claim in this analysis or the paper should be traceable to `scores.csv`, but the upstream inputs in `credits.json` are author judgment.
- **The dataset is deliberately spectrum-sampled** (full quality range) for methodology testing, not representative of VCM composition.
- **Synthetic stress tests C026–C029 are validation cases**, not real projects, and should never be conflated with the 25-credit real-archetype dataset.
- **The three new fragility flags (C004, C011, C014) should be mentioned in paper §7** so that a reviewer can see the boundaries the framework sits on.
- **C007 is no longer fragile under v0.4.** The v0.3 concern about the Rev-1+2 proposal leaving C007 at 75.3 AA (0.3 above the boundary) does not apply to the Alt-3 mechanism adopted here. C007 sits at 73.9 A with a 13.9-point buffer to BBB.
- **Sensitivity analysis was run on v0.4 weights only.** A comparative run under v0.3 weights could illuminate whether the v0.4 change increased or decreased overall stability, but is not in scope for this pilot.
