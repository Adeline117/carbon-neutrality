# Rank Correlation Study

Empirical comparison of our framework against public commercial carbon credit ratings (BeZero, Calyx Global, Sylvera, MSCI).

## Files

| File | Purpose |
|------|---------|
| `dataset.json` | Original dataset: 6 REDD+ projects (CMW 2023 Table 20) + 11 cross-type projects + 2 anchors, with our v0.4/v0.6 per-dimension scores |
| `expanded_dataset.json` | **Expanded dataset (Apr 2026)**: 30 projects across 12 types with agency ratings from BeZero (26), Calyx (10), Sylvera (7), MSCI (1). Machine-readable. |
| `expanded_dataset.md` | Full table of all 30 credits with agency ratings, our scores, sources, and correlation analysis |
| `cross_type_notes.md` | Detailed analysis of the 11 non-REDD+ cross-type projects (v0.6 W4) |
| `compute.py` | Pure-Python script that computes pairwise Spearman and Kendall across all raters |
| `results.md` | Generated: correlation tables and per-project grade comparison |
| `results.csv` | Generated: raw correlation values |
| `analysis.md` | Full interpretation, findings, and implications (updated with expanded dataset notes) |

## Running

```bash
python3 compute.py
```

## Key results

### REDD+-only (n=6, v0.4.1)
- Our mean pairwise Spearman with commercial raters: **+0.343**
- Inter-agency mean Spearman: **+0.009**
- Our framework's agreement exceeds the agencies' agreement with each other.

### Cross-type only (n=9 vs BeZero, v0.6)
- Spearman vs BeZero: **+0.906**
- Strong agreement when project types have clear quality signals.

### Expanded dataset (n=18 scored vs BeZero)
- Spearman vs BeZero: **+0.891** (Kendall tau: +0.805)
- Spans B-to-AAA across 12 project types (REDD+, DACCS, biochar, cookstoves, methane abatement, IFM, landfill gas, renewable energy, ARR, ODS, ERW, J-REDD+).
- 10 additional projects need our framework scoring; scoring those with BeZero ratings would bring n to 28.

## Primary sources

1. Perspectives Climate Group / Carbon Market Watch (2023). "Assessing and comparing carbon credit rating agencies." [PDF](https://carbonmarketwatch.org/wp-content/uploads/2023/09/PCG_CMW_rating_agencies_final_report_.pdf), Table 20.
2. BeZero Carbon public listings: https://bezerocarbon.com/ratings/listings (677+ projects, Apr 2026).
3. Various press releases, case studies, and investigative reports (full list in `expanded_dataset.json`).
