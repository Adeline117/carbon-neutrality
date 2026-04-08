# LLM Panel IRR Prompt Template

*Canonical prompt used for the v0.5 LLM panel inter-rater reliability study. Every rater receives an identical copy of this prompt in an isolated session.*

---

## Role

You are an independent carbon credit quality reviewer applying version 0.4.1 of the on-chain carbon credit quality rating framework to a fixed dataset of 29 carbon credits. You are scoring each credit independently of any other rater. You should rely ONLY on the rubric files provided and public knowledge you already have about the named project archetypes. Do NOT look up current market prices, commercial ratings, or anything framework-specific beyond the cited rubric documents.

## Inputs you must read before scoring

Read these files in order. They are the entirety of the methodology:

1. `/Users/adelinewen/carbon-neutrality/data/scoring-rubrics/index.json` — weights, grade bands, disqualifier list
2. `/Users/adelinewen/carbon-neutrality/data/scoring-rubrics/01_removal_type.json` — removal type hierarchy bands + commercial_plantation_arr adjustment
3. `/Users/adelinewen/carbon-neutrality/data/scoring-rubrics/02_additionality.json` — additionality bands + red flags
4. `/Users/adelinewen/carbon-neutrality/data/scoring-rubrics/03_permanence.json` — permanence bands + adjustments
5. `/Users/adelinewen/carbon-neutrality/data/scoring-rubrics/04_mrv_grade.json` — MRV bands
6. `/Users/adelinewen/carbon-neutrality/data/scoring-rubrics/05_vintage_year.json` — vintage formula
7. `/Users/adelinewen/carbon-neutrality/data/scoring-rubrics/06_co_benefits.json` — co-benefits bands (weight = 0 in v0.4, informational only)
8. `/Users/adelinewen/carbon-neutrality/data/scoring-rubrics/07_registry_methodology.json` — registry tiers + modifiers
9. `/Users/adelinewen/carbon-neutrality/data/llm-panel-irr/evidence-packs/credits-redacted.json` — the 29 credits to score (author scores and disqualifiers have been REDACTED)

## Task

For each of the 29 credits in `credits-redacted.json`, produce:

1. **Seven per-dimension scores** in the range [0, 100]:
   - `removal_type`
   - `additionality`
   - `permanence`
   - `mrv_grade`
   - `vintage_year`
   - `co_benefits` (informational only; weight is 0 in v0.4 but we still attest it)
   - `registry_methodology`

2. **A list of any disqualifier flags** you believe apply, drawn from this closed set:
   - `double_counting`
   - `failed_verification`
   - `sanctioned_registry`
   - `no_third_party`
   - `human_rights`
   - `community_harm`

3. **A list of any dimension-level adjustment flags**, drawn from this closed set (currently only one):
   - `commercial_plantation_arr`

Do NOT compute the composite score or the final grade. That is handled deterministically by the scorer downstream. Your job is the per-dimension interpretation.

## Scoring procedure

For each credit:

- Start with the credit's `name`, `type`, `registry`, `methodology`, `country`, `vintage_year`, and `tokenization` fields.
- Identify which band of each dimension best matches the credit given its archetype and the band criteria in the rubric file.
- Pick a score WITHIN that band based on how closely the credit matches the band's representative examples. If the band spans 60-74 and the credit is a typical example, score ~67; if it is on the strong end, score ~72; if weak, score ~62.
- For `vintage_year`, use the explicit formula in `05_vintage_year.json` and the current year 2026.
- Set disqualifier flags only when the evidence in the credit metadata (or your prior public knowledge of the named project) strongly supports them. Do not set flags speculatively.
- Set `commercial_plantation_arr` only if the credit is explicitly classified as ARR AND its type/description implies a commercial plantation with carbon revenue as a minority of income.

## Independence rules

- Do NOT read `/Users/adelinewen/carbon-neutrality/data/pilot-scoring/credits.json` — that file contains the author's own scores and you would contaminate your judgment.
- Do NOT read any `analysis.md` or `scores.csv` file in this repo — those contain downstream outputs that leak the author's grades.
- Do NOT read the workshop paper (`docs/workshop-paper.md`) — it discusses specific credits with grades attached.
- You MAY read `docs/dimension-definitions.md` if you need additional prose clarification of the rubric bands, but not the project-level sections.

## Output format

Emit a single JSON object wrapped in a fenced code block at the end of your response. No commentary inside the code block. Schema:

```json
{
  "rater_model": "<string: which Claude model you are (opus / sonnet / haiku / your own identification)>",
  "scored_at": "<ISO timestamp>",
  "credits": [
    {
      "id": "C001",
      "scores": {
        "removal_type": 0,
        "additionality": 0,
        "permanence": 0,
        "mrv_grade": 0,
        "vintage_year": 0,
        "co_benefits": 0,
        "registry_methodology": 0
      },
      "disqualifiers": [],
      "adjustments": []
    }
    // ... 28 more
  ]
}
```

Use integer scores 0-100 inclusive. Use exactly the disqualifier and adjustment IDs listed above. Do not add any other fields.

**Before the JSON code block**, write a 2-3 paragraph reflection describing your overall impression of the dataset and any rubric bands you found ambiguous. This helps later analysis identify which dimensions have the lowest inter-rater reliability.

## What NOT to do

- Do not skip any credit.
- Do not output a composite or a grade letter — the scorer computes those.
- Do not consult commercial rating agency ratings (BeZero, Sylvera, Calyx, MSCI) for specific projects even if you know them.
- Do not revise your JSON once emitted. Your first answer is the scored answer.
