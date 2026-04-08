# Rank Correlation Results

Dataset: 6 REDD+ projects from Carbon Market Watch 2023 Table 20, scored under v0.4.

## Pairwise correlations

| Pair | Spearman rho | Kendall tau |
|------|-------------:|------------:|
| ours_v04 vs bezero | +0.664 | +0.598 |
| ours_v04 vs calyx_nzm | -0.200 | -0.200 |
| ours_v04 vs sylvera_nzm | +0.566 | +0.539 |
| bezero vs calyx_nzm | -0.664 | -0.598 |
| bezero vs sylvera_nzm | +0.125 | +0.161 |
| calyx_nzm vs sylvera_nzm | +0.566 | +0.539 |

## Per-project grades

| ID | Project | Our v0.4 | BeZero | Calyx NZM | Sylvera NZM |
|----|---------|----------|--------|-----------|-------------|
| CMW01 | Ecomapua Amazon REDD+ | BB | C | D | Tier 1 |
| CMW02 | Keo Seima Wildlife Sanctuary | BBB | A | E | Tier 1 |
| CMW03 | Mai Ndombe REDD+ | BB | BB | E | Tier 2 |
| CMW04 | Envira Amazonia Project | BB | BBB | E | Tier 2 |
| CMW05 | Luangwa Community Forests Project | BB | B | E | Tier 2 |
| CMW06 | Guanaré Forest Restoration Project | BB | B | E | Tier 3 |

## Interpretation: are we as agreeable as the commercial agencies are with each other?

- Inter-agency Spearman (mean of BeZero/Calyx/Sylvera pairs): **+0.009**
- Our-framework-vs-agency Spearman (mean of our pairs): **+0.343**
- **Our pairwise agreement with the commercial raters is no worse than the commercial raters' agreement with each other.** This is the success criterion from the v0.4 plan note.

Sample size is small (n=6). Treat the direction of the comparison as evidence, not the absolute magnitudes.