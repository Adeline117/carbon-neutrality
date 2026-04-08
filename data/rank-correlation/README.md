# Rank Correlation Study

Empirical comparison of our v0.4 framework against public commercial carbon credit ratings (BeZero, Calyx Global, Sylvera).

## Files

| File | Purpose |
|------|---------|
| `dataset.json` | 6 REDD+ projects with BeZero/Calyx/Sylvera ratings from Carbon Market Watch 2023 + our v0.4 per-dimension scores + 2 anchor projects (Orca, Kariba) |
| `compute.py` | Pure-Python script that computes pairwise Spearman ρ and Kendall τ across all four raters |
| `results.md` | Generated: correlation tables and per-project grade comparison |
| `results.csv` | Generated: raw correlation values |
| `analysis.md` | Full interpretation, findings, and v0.5 implications |

## Running

```bash
python3 compute.py
```

## Key result

Our mean pairwise Spearman with commercial raters: **−0.038**
Inter-agency mean Spearman (BeZero/Calyx/Sylvera among themselves): **+0.009**

Both are essentially zero. The v0.4 framework's agreement with commercial raters is indistinguishable from the commercial raters' agreement with each other. The headline is not "we match them" — the headline is "none of us agree on REDD+ scoring, and our framework refuses to pick a side in a genuine methodological dispute".

## Primary source

Perspectives Climate Group / Carbon Market Watch (2023). "Assessing and comparing carbon credit rating agencies." Freiburg, 11.09.2023. [PDF](https://carbonmarketwatch.org/wp-content/uploads/2023/09/PCG_CMW_rating_agencies_final_report_.pdf), Table 20.
