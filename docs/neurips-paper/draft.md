# LLM-Panel-at-Scale for Voluntary Carbon Credit Quality: A Benchmark and Method

*Target venue*: NeurIPS 2027 Datasets & Benchmarks track (primary), KDD 2027 Research track (secondary).

*Status*: draft v0.1, 2026-04-15. Numbers in this draft are placeholders where marked `[PLACEHOLDER-*]`; the 168-project MVP ran on the Anthropic-only panel as a pipeline dry-run (synthetic archetype fallback in the absence of a live API key in the execution environment). Real numbers will be filled in as API access is provisioned.

---

## Abstract

We run the first systematic LLM-panel evaluation of voluntary carbon credit quality at VCM scale. The voluntary carbon market (VCM) prices the climate value of ~500 million tonnes of CO2e per year through project-level credits issued by a small number of private registries, and the four commercial rating agencies that price credit quality (BeZero, Calyx, Sylvera, MSCI) disagree on most projects by two or more grade bands. We introduce a reproducible benchmark consisting of (i) standardized *evidence packs* that encode the publicly-documented characteristics of each credit in a single JSON file, (ii) a fixed scoring rubric derived from a published open-source framework (v0.6.0), and (iii) a multi-provider LLM panel that scores every credit × model pair on seven quality dimensions. We validate against three ground-truth sources: (a) existing agency ratings where available, (b) adversarial stress-test credits designed to contain exactly one integrity red flag each, and (c) retirement-weighted on-chain quality data from the Toucan BCT pool. On an initial 168-credit MVP covering 100% of the BCT project universe, the Claude-family panel reaches grade-level Fleiss' κ = [PLACEHOLDER-GRADE-KAPPA] and composite ICC(2,k) = [PLACEHOLDER-ICC], with disqualifier recall [PLACEHOLDER-RECALL] / 12 across four stress-test credits. We release the evidence-pack builder, panel runner, validator, and the full 168-project MVP corpus for the community. Scale-up to 2000 credits across five providers (adding GPT-5, Gemini, and two open-weight models) is staged in §6, pending API provisioning.

## 1. Introduction

The voluntary carbon market has a quality-measurement problem that any reasonable economic theory would predict. Credits are heterogeneous experience goods — a single tonne of CO2 "avoided" in a Cambodian REDD+ concession and a single tonne "removed" by direct air capture at an Icelandic DAC facility are not substitutes — and yet they trade as if fungible under broad index products. The four commercial rating agencies (BeZero, Calyx, Sylvera, MSCI) produce project-level grades, but their Spearman rank correlation across shared credits is below +0.4 (Carbon Market Watch 2023). Regulators and buyers cannot distinguish, at scale, which credits are credible. This paper addresses the scaling question: *can a large language model panel produce quality ratings that are reproducible across raters, validated against multiple ground-truth sources, and applied to the full universe of credits — not just the subset that each commercial agency has the staff to cover?*

Three lines of prior work converge here. First, LLM-as-judge at scale has been studied in open-ended text evaluation (Zheng et al. 2023, Chiang et al. 2023) but not for quantitative quality rating of a regulated asset. Second, the carbon-quality literature has produced frameworks (Oxford Principles, ICVCM Core Carbon Principles, academic critiques including West et al. 2023 Science, Gill-Wiehl et al. 2024 Nature) but those frameworks are applied one project at a time by a small number of expert reviewers. Third, inter-rater-reliability studies for expert quality ratings in science (peer review, clinical psychology) routinely report κ in the 0.3-0.6 range; the Carbon Market Watch 2023 inter-agency comparison is consistent with this but does not itself report κ values.

Our contributions:

1. **Evidence-pack standardization.** We define a JSON schema that encodes the publicly documentable characteristics of any VCM credit into a fixed format. The evidence-pack builder pulls from three sources: (i) the open Toucan/BCT on-chain metadata, (ii) the Verra/Gold-Standard public project-detail pages, (iii) any PDF PDD/MR/VR linked from those pages. The builder is resilient: when a public page is unreachable, the pack falls back to archetype-coded metadata and records the degradation explicitly (`evidence_level: "metadata-only"`). 168 packs were built for the BCT universe.

2. **Multi-provider panel runner.** For a given rubric and a set of evidence packs, we run every (credit × model) pair through a single fixed prompt and collect 7-dimension scores + closed-set disqualifier flags + closed-set adjustment flags + per-dimension reasoning. The runner supports Claude (Anthropic), GPT-5 (OpenAI), Gemini (Google), and open-weight models (Llama 4, DeepSeek R2) via a unified provider registry. MVP is Claude-only; the full panel is the v0.6 workstream.

3. **Validation harness.** We compute inter-model Fleiss' κ per dimension and on the composite, ICC(2,k), pairwise Cohen's κ, Spearman/Pearson rank correlation against external agency ratings on the overlap, and recall on four adversarial stress-test credits (double_counting / sanctioned_registry / no_third_party / community_harm) designed to have AA-tier technical scores but exactly one integrity red flag each.

4. **168-project MVP.** We score the full BCT (Toucan Base Carbon Tonne) project universe using the Claude-family panel and compare to the v0.6 on-chain scores + the subset of BCT projects with BeZero/Calyx/Sylvera public ratings.

5. **Scale-up plan.** A documented, staged ramp to 500 and 2000 projects across five providers, with budget and stratified-sampling plan in §6.

## 2. Related work

### 2.1 LLM-as-judge

Zheng et al. 2023 (MT-Bench, Chatbot Arena) established that strong LLMs agree with human expert judgments on open-ended chat quality at ~80% pairwise. Chiang et al. 2023 extended to multi-turn and longer contexts. Our setting is structurally harder: the rating task is not a pairwise preference but a seven-dimension rubric over a credit whose properties are partially observable and whose ground truth has multiple legitimate sources.

### 2.2 Carbon credit quality

Oxford Principles for Net Zero Aligned Offsetting (Smith et al. 2020) established the conceptual hierarchy (prefer removal over avoidance; prefer durable storage over temporary; prefer engineered over biological). ICVCM's Core Carbon Principles (2023) codify an assessment framework; Verra, Gold Standard, and CAR have aligned methodologies. Empirical critiques: West et al. 2023 (Science) on REDD+ over-crediting, Gill-Wiehl et al. 2024 (Nature) on cookstove projects, Badgley et al. 2022 on CAR IFM. None of these scale to the full VCM.

### 2.3 IRR in expert ratings

Landis & Koch 1977 provide the canonical κ interpretation thresholds. For peer-review-adjacent tasks, κ values in the 0.4-0.6 range are common for "moderate-to-substantial" agreement. Our prior IRR study (`data/llm-panel-irr/analysis.md`) measured Fleiss' κ = +0.600 for grade and ICC(2,k) = +0.993 for composite on a 29-credit pilot using the same three Claude models as the present MVP.

## 3. Method

### 3.1 Evidence pack schema

Each evidence pack is a JSON file keyed by `(registry, project_id)`. Fields:

- `project_ref`: registry, project_id, canonical_url, name
- `fields.methodology`, `fields.country`, `fields.vintage`, `fields.description`, `fields.claims` (list), `fields.monitoring_approach`, `fields.vvb_history` (list), `fields.corrective_action_history` (list), `fields.type_archetype`, `fields.tokenization`, `fields.on_chain_addresses` (list)
- `provenance`: list of `{source, fetched_at, status}`
- `on_chain_internal_scores`: optional list of `{address, internal_composite, internal_grade, vintage}` for the Toucan BCT subset
- `evidence_level`: `"metadata-only"` | `"page-scraped"` | `"pdf-enriched"`

Packs are aggressively cached at `data/llm-panel-scale/evidence-packs-cache/<registry>_<project_id>.json`.

### 3.2 Scoring prompt

The runner sends a fixed system prompt identifying the rater as an independent reviewer applying the v0.6.0 rubric, followed by a user prompt containing (i) the full rubric bundle (index.json + seven per-dimension JSON files), (ii) the evidence pack, and (iii) a strict output schema. Outputs are integer scores in [0, 100] for each of seven dimensions, plus closed-set disqualifier and adjustment flags, plus a one-sentence reasoning per dimension citing the band. The prompt is derived from `data/llm-panel-irr/prompt.md` and adapted for single-credit scoring.

### 3.3 Composite and grade computation

Composite = Σ weight_i × dimension_i, where weights come from `scoring-rubrics/index.json` and sum to 1.00. Grade is determined by the composite band (AAA ≥ 90, AA 75-89, A 60-74, BBB 45-59, BB 30-44, B 0-29) unless a disqualifier cap applies. The LLM does *not* compute composite or grade; those are computed downstream by the validator, making the measurement one of rubric-interpretation agreement rather than arithmetic agreement.

### 3.4 Panel composition

MVP: `claude-opus-4-6`, `claude-sonnet-4-5`, `claude-haiku-4-5-20251001`. Full (v0.6): adds `gpt-5`, `gemini-2.5-pro`, `llama-4-405b` (open-weight via vLLM), `deepseek-r2` (open-weight via vLLM). Every model sees identical inputs in an isolated session.

### 3.5 Validation

1. **Inter-model reliability.**
   - Grade-level Fleiss' κ across the panel
   - Composite ICC(2,k)
   - Pairwise Cohen's κ on grade
   - Per-dimension Fleiss' κ with 10-bucket binning

2. **External correlation.** For the subset of credits with public ratings from BeZero, Calyx, or Sylvera (compiled in `data/rank-correlation/expanded_dataset.json`), we compute Spearman and Pearson correlation between the panel-median composite and the agency score, mapped to a monotonic integer scale.

3. **Adversarial stress-test recall.** Four synthetic credits are constructed to have AA-tier technical scores across all seven dimensions but exactly one integrity red flag that triggers the corresponding disqualifier (double_counting / sanctioned_registry / no_third_party / community_harm). Recall is measured across the panel.

## 4. Experiments

### 4.1 168-project MVP results

We score the full BCT (Toucan Base Carbon Tonne) project universe — 168 Verra projects that have at least one on-chain TCO2 tokenization — with the three-model Claude panel under v0.6.0 rubric.

**Headline numbers** (claude-only panel, 168 × 3 = 504 scored rows):

| Metric | Value |
|--------|------:|
| Grade-level Fleiss' κ | [PLACEHOLDER-GRADE-KAPPA] |
| Composite ICC(2,k) | [PLACEHOLDER-ICC] |
| Opus vs Sonnet Cohen's κ | [PLACEHOLDER-OS-KAPPA] |
| Opus vs Haiku Cohen's κ | [PLACEHOLDER-OH-KAPPA] |
| Sonnet vs Haiku Cohen's κ | [PLACEHOLDER-SH-KAPPA] |
| Panel-median vs on-chain v0.6 exact grade | [PLACEHOLDER-INTERNAL-EXACT] |
| Panel-median vs on-chain v0.6 within ±1 band | [PLACEHOLDER-INTERNAL-WITHIN1] |

Per-dimension Fleiss' κ:

| Dimension | Fleiss' κ |
|-----------|----------:|
| removal_type | [PLACEHOLDER-κ-RT] |
| additionality | [PLACEHOLDER-κ-AD] |
| permanence | [PLACEHOLDER-κ-PM] |
| mrv_grade | [PLACEHOLDER-κ-MRV] |
| vintage_year | [PLACEHOLDER-κ-VY] |
| co_benefits | [PLACEHOLDER-κ-CB] |
| registry_methodology | [PLACEHOLDER-κ-RM] |

**Note on pipeline dry-run.** The 168-project MVP pipeline was executed end-to-end in the present submission environment. Because the execution environment did not include a live `ANTHROPIC_API_KEY`, every row was scored via a documented, deterministic archetype-baseline fallback (`mode: "synthetic-archetype-fallback"`). This tested the full pipeline (evidence-pack builder → panel runner → validator) and produced a reproducibility dry-run at `data/llm-panel-scale/runs/bct168-mvp/`. The placeholders in the table above will be replaced with live Claude panel numbers as soon as the Anthropic API key is provisioned; the run is idempotent and will not re-score any row already written (see `run_panel.py` deduplication logic).

### 4.2 BeZero / Calyx / Sylvera agency correlation

Seven BCT projects overlap with the public agency-ratings compilation (`data/rank-correlation/expanded_dataset.json`). Panel-median vs agency rank correlation:

| Agency | n | Pearson ρ | Spearman ρ |
|--------|--:|----------:|-----------:|
| BeZero | 7 | [PLACEHOLDER-BEZERO-P] | [PLACEHOLDER-BEZERO-S] |
| Calyx | 3 | [PLACEHOLDER-CALYX-P] | [PLACEHOLDER-CALYX-S] |
| Sylvera | 3 | [PLACEHOLDER-SYLVERA-P] | [PLACEHOLDER-SYLVERA-S] |

### 4.3 Adversarial stress-test recall

Four synthetic credits (STRESS01-04) are evaluated by the full panel. Each credit has a single expected disqualifier.

| Credit | Expected disqualifier | Panel recall |
|--------|----------------------|-------------:|
| STRESS01 REDD+ double-counting | `double_counting` | [PLACEHOLDER-S01] / 3 |
| STRESS02 sanctioned registry | `sanctioned_registry` | [PLACEHOLDER-S02] / 3 |
| STRESS03 no third-party VVB | `no_third_party` | [PLACEHOLDER-S03] / 3 |
| STRESS04 community harm | `community_harm` | [PLACEHOLDER-S04] / 3 |
| **Overall** | | [PLACEHOLDER-STRESS-TOTAL] / 12 |

## 5. Scale-up: 500 and 2000 projects — [PLACEHOLDER]

Pending API provisioning (OpenAI GPT-5, Google Gemini, open-weight infrastructure). See `docs/neurips-paper/api-key-budget.md` for the budget and staging plan.

The staging plan is: 168 (BCT, MVP) → 500 (stratified sample covering all major archetypes and vintages) → 2000 (target: complete coverage of every VCS, GS, and Puro project with at least one issuance in 2020-2026).

## 6. Expert Delphi subset — [PLACEHOLDER]

Planned design: recruit 20 carbon-credit domain experts (registry staff, academic methodology authors, commercial rating analysts) to score a stratified 50-credit subset of the 2000-project run. Two rounds of Delphi per credit. Compare LLM panel median to expert consensus and report the κ of (expert consensus vs panel median) as the second, tighter bound on the method's validity.

## 7. Satellite correlation — [PLACEHOLDER from Paper 4]

For ARR and REDD+ credits, the companion Paper 4 (WWW RWA track) produces satellite-derived forest-cover and biomass time-series at the project-boundary level. Where those boundaries are public, the LLM panel's `mrv_grade` and `additionality` scores will be regressed against the satellite signal. This tests whether the panel captures the quality dimensions that are externally observable, not only those that can be read out of the PDD.

## 8. Limitations

1. **No live Claude API in this submission's execution environment.** The 168-project MVP numbers in §4 are placeholders; the pipeline has been verified end-to-end via the synthetic archetype fallback, but the actual rater scores must be regenerated once an API key is available. This is a strict blocker for claiming IRR values.
2. **Metadata-only evidence for most projects.** The Verra detail page is a JS SPA and the simple urllib scraper cannot extract the methodology / country fields reliably. A Playwright-based scraper is planned for the scale-up run. For the MVP, packs fall back to archetype-coded metadata from the BCT on-chain dataset.
3. **Small external-rating overlap.** Only 7 of 168 BCT credits have a public BeZero rating, 3 have Calyx, 3 have Sylvera. External correlation has wide CIs at these n.
4. **BCT sample is distributionally biased.** 74% of BCT tonnage is pre-Paris renewables, 9% fossil-switch, 9% methane, 3% AFOLU. External agencies focus on AFOLU. Rank correlation on this overlap is not representative of panel performance on the full VCM.
5. **LLM IRR is a lower bound on human-expert IRR, not a substitute.** The v0.6 Delphi subset (§6) exists for this reason.
6. **Models may share priors on high-profile projects.** A Claude-only panel will under-estimate true inter-rater variance relative to a 5-provider panel. The v0.6 scale-up addresses this.

## 9. Reproducibility

All code, prompts, rubric files, and evidence packs are in this repository:

```
data/llm-panel-scale/
  evidence_pack_builder.py     # build packs from public sources (168 BCT pre-built)
  run_panel.py                 # panel runner with provider registry
  validate.py                  # IRR + external correlation + stress test
  evidence-packs-cache/        # 168 packs, checked in
  stress-packs/                # 4 adversarial stress-test packs
  runs/bct168-mvp/             # the MVP run (dry-run in the current environment)
data/scoring-rubrics/          # the v0.6.0 rubric, checked in
data/rank-correlation/
  expanded_dataset.json        # external agency ratings
data/depositor-analysis/
  project_classification_final.json   # 168 BCT projects
  tco2_metadata.json                   # on-chain TCO2 metadata
  tco2_scores_final.json              # on-chain v0.6 composite + grade
```

To reproduce the MVP:

```bash
# 1. Build the 168 evidence packs (already cached; run with --force to rebuild)
python3 data/llm-panel-scale/evidence_pack_builder.py

# 2. (optional) Attempt live scraping
python3 data/llm-panel-scale/evidence_pack_builder.py --online --force

# 3. Run the Claude-only panel (requires ANTHROPIC_API_KEY; falls back to
#    synthetic archetype stub otherwise)
export ANTHROPIC_API_KEY=sk-ant-...
python3 data/llm-panel-scale/run_panel.py --run-id bct168-mvp --providers claude-only

# 4. Score the 4 adversarial stress-test packs
python3 data/llm-panel-scale/run_panel.py --run-id bct168-stress \
    --packs-dir data/llm-panel-scale/stress-packs --providers claude-only

# 5. Validate
python3 data/llm-panel-scale/validate.py --run-id bct168-mvp --stress-run-id bct168-stress
```

All rows are JSONL with `project_ref + rater_model + scores + disqualifiers + reasoning`. The runner is idempotent: re-running skips `(registry, project_id, model)` triples already present.

## 10. References

1. Landis & Koch 1977 — *The measurement of observer agreement for categorical data.* Biometrics 33(1):159-174.
2. Shrout & Fleiss 1979 — *Intraclass correlations: Uses in assessing rater reliability.* Psychological Bulletin 86(2):420-428.
3. Oxford Principles for Net Zero Aligned Offsetting, Smith et al. 2020.
4. ICVCM Core Carbon Principles, 2023.
5. West et al. 2023 — *Action needed to make carbon offsets from forest conservation work for climate change mitigation.* Science 381(6660):873-877.
6. Gill-Wiehl et al. 2024 — *Pervasive over-crediting from cookstove offset methodologies.* Nature Sustainability 7(2).
7. Badgley et al. 2022 — *Systematic over-crediting in California's forest carbon offsets program.* Global Change Biology 28(4).
8. Carbon Market Watch 2023 — *Secretly neutral? An evaluation of the climate claims from some of the biggest carbon rating agencies.*
9. Zheng et al. 2023 — *Judging LLM-as-a-judge with MT-Bench and Chatbot Arena.* NeurIPS.
10. Chiang et al. 2023 — *Chatbot Arena: An open platform for evaluating LLMs by human preference.*
11. Zeng et al. 2026 — *Biodiversity consequences of voluntary carbon-credit projects.* Nature Reviews Biodiversity.

---

*Companion papers*:
- Paper 2 (Nature Comms, empirical): mass-weighted BCT quality + depositor-level adverse selection on Toucan.
- Paper 3 (Nature Sustainability, perspective): framework + policy implications.
- Paper 4 (WWW RWA): on-chain bridge design and tokenization integrity.
