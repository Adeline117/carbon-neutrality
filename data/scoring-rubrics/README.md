# Scoring Rubrics

Machine-readable JSON rubrics for the seven rating dimensions, derived from `docs/dimension-definitions.md`. These files are the source of truth for:

- The pilot scoring script (`data/pilot-scoring/`)
- The Solidity rating contract (`contracts/`)
- Any third-party implementer of the framework

## Files

| File | Dimension | v0.3 weight | v0.4 weight |
|------|-----------|-------------|-------------|
| `index.json` | Framework index (weights, grades, disqualifiers) | — | — |
| `01_removal_type.json` | Removal Type Hierarchy | 20% | **25%** |
| `02_additionality.json` | Additionality | 20% | 20% |
| `03_permanence.json` | Permanence | 15% | **17.5%** |
| `04_mrv_grade.json` | MRV Grade | 15% | **20%** |
| `05_vintage_year.json` | Vintage Year | 10% | 10% |
| `06_co_benefits.json` | Co-benefits | 10% | **0% (safeguards-gate)** |
| `07_registry_methodology.json` | Registry & Methodology | 10% | 7.5% |

**v0.4 mechanism change:** co_benefits is no longer scored in the composite. It is attested as an informational value and used by assessors to decide whether to set the `community_harm` disqualifier (caps at BBB). See `docs/methodology-gate-v0.4.md` for the decision rationale and `06_co_benefits.json` for the updated dimension doc.

## Schema Conventions

- All scores are integers in `[0, 100]`.
- `bands` are ordered high-to-low; a project matches the first band whose criteria are met.
- `adjustments` apply additively to the band-derived raw score; final score is clamped to `[0, 100]`.
- `red_flags` and `overrides` can cap the achievable score before clamping.
- `disqualifiers` (in `index.json`) cap the achievable **grade** regardless of numeric score.

## Composite Score

```
composite = sum(dimension_score_i * weight_i)
grade     = first g in grades where composite in [g.min, g.max]
grade     = min(grade, disqualifier_caps)
```

## Versioning

- `schema_version` follows SemVer. Breaking changes bump the major version.
- `paper_version` tracks the workshop paper version these rubrics derive from.
- Weight changes (even if the schema is unchanged) bump the minor version, since they alter scoring behavior.
