# Pilot Scoring

Hand-scored pilot dataset of 25 illustrative carbon credits, used to stress-test the rubrics under `../scoring-rubrics/` before expert consultation.

## Files

| File | Purpose |
|------|---------|
| `credits.json` | 25 credits with per-dimension scores and disqualifier flags |
| `score.py` | Pure-Python scorer (no dependencies) that reads the rubrics + credits and emits composite scores and grades |
| `scores.csv` | Generated output: all rows, all dimensions, composite, nominal grade, final grade |
| `scores.md` | Generated markdown summary with distribution table |
| `analysis.md` | Qualitative analysis of the pilot results, findings, and proposed revisions for paper v0.3 |

## Running

```bash
python3 score.py
```

Regenerates `scores.csv` and `scores.md` from `credits.json` + `../scoring-rubrics/index.json`.

## Important disclaimers

- Per-dimension scores were assigned by the author(s) based on public documentation and archetype-level knowledge. They are **not** a formal rating of the named projects.
- The dataset is deliberately spectrum-sampled (full quality range) for methodology testing, not representative of VCM composition.
- All findings in `analysis.md` are methodology observations, not project ratings.
