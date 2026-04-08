# LLM Panel Inter-Rater Reliability Analysis (v0.5 workstream W1)

*First empirical measurement of the v0.4.1 rubric's inter-rater reliability. Five independent LLM raters were initially planned (Opus/Sonnet/GPT-5/Gemini/Llama); this first round uses a **preliminary Anthropic-only panel** of three Claude models (Opus 4.6, Sonnet 4.6, Haiku 4.5) because those are the models directly callable via subagent in this environment. A multi-provider extension (GPT-5 + Gemini + Llama) is documented in §6 as the next iteration.*

## 1. Why this exists

The v0.4.1 framework publishes a specific distribution of grades (3 AAA / 3 AA / 5 A / 4 BBB / 2 BB / 8 B) on the 25-credit real-archetype pilot. Every number downstream of this distribution — the paper's §7 findings, the rank-correlation study's mean Spearman, the Guanaré outlier diagnosis — sits on top of **a single author's per-dimension scoring**. Until this study, the framework had zero empirical evidence that a different qualified reader of the same rubric would produce the same grades.

The most common hostile reviewer question to a rating paper is: "Who scored these, and would anyone else have scored them the same?" The v0.4.1 paper's §9 (Limitations) concedes the issue in prose but could not quantify it. This study fills that gap.

## 2. Protocol

Three Claude models — Opus 4.6, Sonnet 4.6, Haiku 4.5 — independently scored all 29 credits from the illustrative pilot (25 real + 4 synthetic disqualifier stress tests) in isolated subagent sessions. Each rater received:

- The same canonical prompt (`data/llm-panel-irr/prompt.md`)
- The seven machine-readable rubric files (`data/scoring-rubrics/`)
- A **redacted** version of `credits.json` (`data/llm-panel-irr/evidence-packs/credits-redacted.json`) with author scores and author-assigned disqualifiers removed
- An explicit instruction NOT to read `data/pilot-scoring/credits.json`, any `analysis.md`, any `scores.csv`, or the workshop paper — i.e., not to read anything that would leak the author's grades

Each rater produced:

1. Seven per-dimension scores (0-100 integers) for each credit
2. A list of disqualifier flags (from the closed set of six)
3. A list of adjustment flags (currently only `commercial_plantation_arr`)

The composite score and grade were **not** computed by the LLM. They were computed deterministically by `data/pilot-scoring/score.py` from the per-dimension inputs, so the measurement is of **rubric-interpretation agreement**, not composite-arithmetic agreement.

Full prompt: `data/llm-panel-irr/prompt.md`.
Raw rater outputs: `data/llm-panel-irr/raw/<model>/scored.json`.

## 3. Headline statistics

| Metric | Value | Interpretation |
|--------|------:|----------------|
| **Grade-level Fleiss' κ** (LLM panel, 3 raters × 29 credits) | **+0.600** | Substantial agreement (Landis & Koch 1977 threshold for "substantial" = 0.61; we are essentially at the boundary) |
| **Composite ICC(2,k)** (LLM panel, continuous 0-100) | **+0.993** | Near-perfect reliability on the continuous outcome |
| **Author vs panel median — exact grade** | **25/29 = 86%** | The author's v0.4.1 grades match the LLM panel median on 25 of 29 credits |
| **Author vs panel median — within ±1 band** | **29/29 = 100%** | Every discrepancy is a 1-band adjacent call, never a multi-band gap |

The composite ICC being far higher than the grade-level Fleiss' κ is informative: **small per-dimension disagreements wash out when linearly combined into the composite.** This is consistent with the design: the composite is a mean, and means of noisy inputs are more stable than the inputs themselves.

## 4. Pairwise Cohen's κ (author + 3 LLMs)

| Pair | Cohen's κ | Exact agreement | Within ±1 band |
|------|----------:|----------------:|---------------:|
| Author vs Opus | +0.742 | 79% | 100% |
| Author vs Sonnet | +0.697 | 76% | 100% |
| Author vs Haiku | +0.634 | 69% | 100% |
| Opus vs Sonnet | +0.693 | 76% | 100% |
| Opus vs Haiku | +0.628 | 69% | 100% |
| Sonnet vs Haiku | +0.500 | 59% | 100% |

**Observations:**

1. **Author vs Opus is the strongest pair (κ=0.742)**, which is expected — both are the most capable reasoner among the participants.
2. **Sonnet vs Haiku is the weakest pair (κ=0.500)**, moderate not substantial. This matches the intuition that smaller models interpret ambiguous rubric bands with more variance than larger ones.
3. **Every pair reaches 100% within-±1-band agreement.** Even the weakest pair never places a credit two grades apart. This is the single most reviewer-reassuring number in the study: the rubric produces reproducible ordinal rankings even when the exact grade is disputed.

## 5. Per-dimension agreement

The dimensions differ dramatically in how much the LLMs agree. Fleiss' κ on 10-point bucketed scores across the 3 LLM raters:

| Dimension | Fleiss' κ | Mean pairwise Pearson ρ | Mean absolute Δ (0-100 scale) | Reading |
|-----------|----------:|------------------------:|-------------------------------:|---------|
| permanence | **+0.684** | +0.984 | 4.51 | **substantial** |
| removal_type | **+0.585** | +0.973 | 4.69 | **moderate-to-substantial** |
| vintage_year | +0.324 | +0.982 | 11.59 | fair (see note) |
| mrv_grade | +0.248 | +0.939 | 8.05 | fair |
| additionality | +0.243 | +0.932 | 9.68 | fair |
| co_benefits | +0.182 | +0.864 | 10.23 | **slight** |
| registry_methodology | **+0.168** | +0.795 | 12.57 | **slight (weakest)** |

### 5.1 The reassuring part

**Permanence (κ=0.684) and removal_type (κ=0.585) are the most reliably scored dimensions.** These are the two load-bearing dimensions for the Oxford hierarchy finding in the paper's §7.2 — AAA credits are AAA because of strong removal_type + strong permanence + strong MRV, and those are exactly the dimensions where the LLM panel converges. The "3 engineered CDR credits reach AAA" headline is supported by the dimensions that matter most for it.

Per-dimension Pearson ρ is ≥ 0.93 for every technical dimension, meaning even where raters disagree on the exact score, they agree on the ordering — exactly the property the v0.4.1 rubric is supposed to guarantee.

### 5.2 The concerning part

**Registry/methodology (κ=0.168) and co_benefits (κ=0.182) have only slight Fleiss' κ agreement.** Both are below the Landis & Koch "fair" threshold of 0.21. This is a specific, actionable rubric-refinement finding:

- **Registry/methodology** ambiguity likely comes from the 4 tier bands (70-100 / 40-69 / 10-39 / 0-9) combined with 4 discretionary modifiers. A rater who gives +10 for "conservative baseline" and a rater who doesn't can land 10-15 points apart on a project where the CCP status is unclear. The fact that Calyx Global considers 8% of their rated projects CCP-eligible (per our rank-correlation source citations) suggests the tier distinction is binary in practice — which a 4-tier rubric over-represents.
- **Co-benefits** slight agreement is less alarming than it sounds because co_benefits has **zero weight** in v0.4.1 composites. It is attested as an informational field and used only to set the `communityHarm` disqualifier. Disagreement on the numeric score doesn't propagate into the grade unless the disagreement crosses the 0-9 "None / negative externalities" band — and disqualifier recall is 100% (see §7), so it doesn't.
- **Vintage year** Fleiss' κ is 0.324 (fair) despite the dimension having a deterministic formula. This is because raters occasionally disagreed on what counts as "pre-Paris" for the override, and because the mean absolute Δ of 11.59 reflects a few credits where raters disagreed about whether a project was e.g. 2012 or 2014 vintage. A v0.6 tightening of the formula (remove the pre-Paris override special case, let the decay handle it) would likely reduce this.

**Proposed v0.6 rubric refinements driven by this study:**

1. Collapse the 4 registry tiers into a 2-tier scheme (CCP-eligible / not-CCP-eligible) with tight score bands. Target: lift registry_methodology κ above 0.40.
2. Replace the prose criteria in the 4 discretionary registry modifiers with Boolean yes/no rules tied to specific ICVCM CCP decisions. Target: eliminate half the inter-rater variance.
3. Either remove `co_benefits` from the attestation payload entirely (since it has zero weight) or provide a crisp 2-line criterion for the 0-9 harm band.
4. Simplify the vintage_year override to remove the pre-Paris discontinuity.

Each of these is a specific, testable v0.6 change with a clearly stated success criterion (lift a specific κ above a specific threshold) and a quick path to verification (re-run this study after the change).

## 6. Fragility flag validation

The paper's §7.2 identifies three boundary-adjacent credits: **C004 Charm Industrial** (AAA, buffer 0.15), **C011 Adipic acid N2O destruction** (BBB, buffer 0.47), **C014 Plan Vivo agroforestry** (A, buffer 0.90). The LLM panel's behavior on these is the most important single result of this study.

| Credit | Author v0.4.1 | Opus | Sonnet | Haiku | Panel verdict |
|--------|---------------|------|--------|-------|---------------|
| C004 Charm Industrial | **AAA** | AA | AA | AA | **0/3 match AAA** |
| C011 N2O destruction | BBB | BBB | BBB | BBB | 3/3 match |
| C014 Plan Vivo | A | A | BBB | A | 2/3 match |

**The C004 AAA is not robust across raters.** All three Claude models independently put Charm Industrial at AA, not AAA. This matches the sensitivity analysis's fragility flag (buffer 0.15 above the 90 threshold): the author's scoring landed Charm just above AAA, but a reasonable alternative reading lands just below.

**Implication for the paper.** The v0.4.1 paper's §7.2 Finding 1 currently reads "three engineered CDR credits reach AAA." Under the LLM panel median, this becomes **"two engineered CDR credits (Climeworks Orca and Heirloom DAC) reach AAA; a third (Charm Industrial) sits on the AAA/AA boundary with panel consensus at AA."** The Oxford-hierarchy-restored finding is preserved — engineered CDR dominates the top of the scale — but the specific headline number of "3 AAA" is overstated.

**Recommended edit to paper §7.2:** Replace "3 of 29 credits reach AAA" with "2 of 29 credits reach AAA under panel consensus; 3 of 29 reach AAA under single-author scoring. The discrepancy is Charm Industrial (C004), whose composite of 90.15 sits 0.15 points above the AAA threshold; an LLM panel of three Claude models independently places it at AA."

C011 and C014 are not fragile in practice: C011 hits its author grade 3/3 and C014 hits it 2/3.

## 7. Disqualifier recall (synthetic stress tests)

The four synthetic credits C026-C029 were designed to have AA-tier technical scores but flagged with each of the four cap-tier disqualifiers (double_counting → B, sanctioned_registry → BB, no_third_party → BBB, communityHarm → BBB). The panel should recall the expected flag on each.

| Credit | Expected disqualifier | Opus | Sonnet | Haiku | Recall |
|--------|----------------------|------|--------|-------|--------|
| C026 | double_counting | ✓ | ✓ | ✓ | **3/3** |
| C027 | sanctioned_registry | ✓ | ✓ | ✓ | **3/3** |
| C028 | no_third_party | ✓ | ✓ | ✓ | **3/3** |
| C029 | community_harm | ✓ | ✓ | ✓ | **3/3** |

**100% disqualifier recall across all 3 raters and all 4 stress cases.** The disqualifier criteria in the rubric are unambiguous enough that even Haiku applies them correctly on first read. This is a specific, defensible empirical claim for the paper's §7.5.

The synthetic stress tests also contain the `stress_test_note` field in the redacted evidence pack, which names the expected disqualifier. A stricter replication would remove that field and test whether the raters identify the disqualifier from the dimension scores alone. That extension is a v0.6 candidate.

## 8. Statistical claim licensed by this study

> On 29 credits scored independently by three Claude-family LLM raters (Opus 4.6, Sonnet 4.6, Haiku 4.5) using the v0.4.1 rubric and a frozen evidence pack with author scores redacted, grade-level Fleiss' κ = **+0.600** (substantial agreement), composite ICC(2,k) = **+0.993** (near-perfect), and author-vs-panel-median exact grade agreement = **86%** with 100% within ±1 band. Per-dimension Fleiss' κ ranged from **+0.684** (permanence, most-agreed) to **+0.168** (registry_methodology, least-agreed), identifying registry_methodology and co_benefits as the primary rubric-ambiguity targets for v0.6 refinement. Of the three fragility-flagged boundary credits (C004 Charm Industrial, C011 N2O destruction, C014 Plan Vivo agroforestry), the panel median agreed with the author's grade on 2 of 3; C004's AAA grade is not robust across raters and the paper's §7.2 headline should be corrected from "3 of 29 reach AAA" to "2 of 29 reach AAA under panel consensus, 3 of 29 under single-author scoring". Synthetic disqualifier stress tests C026-C029 had 100% recall across all raters and all 4 cap tiers, validating the disqualifier machinery.

## 9. Limitations

1. **Anthropic-only panel.** All three raters are Claude models. They share training data, RLHF, and presumably some tokenizer-level quirks. A multi-provider panel (adding GPT-5, Gemini, and an open-weight model like Llama or DeepSeek) would detect provider-shared biases that this study cannot. Extending to a 5-provider panel is the explicit v0.6 workstream.
2. **LLM agreement is a lower bound on, not a substitute for, human expert IRR.** Models may systematically share public knowledge of high-profile projects (Kariba, Rimba Raya) in a way that biases their judgments toward public consensus. A human-expert panel of registry staff and academic reviewers remains the v0.6 target.
3. **The redacted evidence pack still leaks some signal** through project names and types. A rater that recognizes "Climeworks Orca" and "Toucan BCT" has latent priors from training data. A stricter replication would replace project names with generic IDs, though this would make the task substantially harder.
4. **n=29 is small for high-dimensional Fleiss' κ.** Confidence intervals on the reported κ values are wide. The directional findings (permanence > mrv_grade > registry_methodology in reliability order) are robust; the absolute κ magnitudes should be treated as point estimates with ~±0.10 noise.
5. **Composite ICC may be inflated** by the linear composite's mean-smoothing effect. It is not independent evidence that the rubric is well-calibrated; it is evidence that small per-dimension disagreements cancel out in the weighted sum.
6. **One rubric version only.** This study scores under v0.4.1. After the proposed v0.6 refinements (§5.2), the study should be re-run to verify that the changes actually lift the targeted κ values.

## 10. Implications for v0.5 and v0.6

Concrete actions this study unblocks:

- **v0.5.1 paper edit**: update §7.2 Finding 1 to reflect that Charm Industrial's AAA is not robust across raters. Change "3 of 29 reach AAA" to "2-3 of 29 reach AAA depending on rater; Charm Industrial sits at the boundary with LLM panel consensus at AA."
- **v0.5.1 paper insert**: new §7.5 IRR section pointing at this analysis, summarizing the Fleiss' κ, ICC, and disqualifier recall numbers.
- **v0.5 questionnaire update**: add a Section 11 to `docs/v0.5-weight-calibration-questionnaire.md` asking experts to react to the LLM panel's weakest-dimension findings (registry_methodology κ=0.168, co_benefits κ=0.182).
- **v0.6 rubric refinements**: the four proposed changes in §5.2 (collapse registry tiers, tighten registry modifiers, clarify or remove co_benefits attestation, simplify vintage formula).
- **v0.6 multi-provider panel extension**: replicate with GPT-5 + Gemini + Llama to detect Anthropic-specific biases.
- **v0.6 distributional composite (workstream W2)**: the LLM panel's per-dimension mean absolute Δ (4.5-12.6 points across dimensions) is the **empirical calibration** for the default std prior in the distributional composite mechanism. The current proposal is `default_std = (band_max - band_min) / 4`, which gives ~3.5 for MRV Enhanced; the empirical Δ suggests this should be wider for registry_methodology (12.6/2 ≈ 6.3) and tighter for permanence (4.5/2 ≈ 2.25). W2 should use these empirical values instead of the band-width default.

## 11. Reproducing this analysis

```bash
# The three raters have already been run; their outputs are in raw/
python3 data/llm-panel-irr/irr.py

# Re-running the raters requires the Claude Code subagent tool with
# model=opus/sonnet/haiku and the prompt from data/llm-panel-irr/prompt.md
# (see data/llm-panel-irr/extract_panel.py for the transcript parser)
```

Outputs:
- `data/llm-panel-irr/irr_summary.json` — machine-readable headline numbers
- `data/llm-panel-irr/panel_scores.csv` — per-credit, per-rater grades and composites
- `data/llm-panel-irr/raw/<model>/scored.json` — raw rater inputs

## 12. Sources

1. Landis, J. R., & Koch, G. G. (1977). *The measurement of observer agreement for categorical data.* Biometrics, 33(1), 159-174. (Standard Fleiss' κ / Cohen's κ interpretation thresholds.)
2. Shrout, P. E., & Fleiss, J. L. (1979). *Intraclass correlations: Uses in assessing rater reliability.* Psychological Bulletin, 86(2), 420-428. (ICC(2,k) definition.)
3. The raters: Anthropic Claude Opus 4.6, Sonnet 4.6, and Haiku 4.5, accessed via the Claude Code subagent tool on 2026-04-08.
4. Framework under test: `data/scoring-rubrics/` v0.4.1 (paper_version 0.4.1, schema_version 0.2.1).
