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

---

# Cross-Type Rank Correlation (v0.6 extension)

Dataset: 11 non-REDD+ projects with publicly documented agency ratings, scored under v0.6 using methodology archetypes.

## Per-project grades (cross-type)

| ID | Project | Type | Our v0.6 | BeZero | Calyx | Sylvera |
|----|---------|------|----------|--------|-------|---------|
| CT01 | Climeworks Orca (DACCS Iceland) | CDR | AAA | AAA | - | - |
| CT02 | Novocarbo Carbon Removal Site Rhine | Biochar | AA | A | - | - |
| CT03 | Exomad Green Concepcion (Biochar Bolivia) | Biochar | AA | AA | - | AA |
| CT04 | EcoSafi Clean Cooking (Kenya) | Cookstoves | BBB | A | - | - |
| CT05 | BURN / Key Carbon Global Cookstoves (Kenya) | Cookstoves | BBB | - | AA | - |
| CT06 | Arborify Cookstoves Togo | Cookstoves | BBB | - | A | - |
| CT07 | Rebellion Energy Heartland Methane Abatement | Methane abatement | A | A | - | - |
| CT08 | Family Forest Carbon Program (US IFM) | IFM | BBB | BBB | - | - |
| CT09 | Southern Cardamom REDD+ (Cambodia) | REDD+ | B | B | - | - |
| CT10 | Qnergy Weber County Landfill Methane | Landfill gas | BBB | A | - | - |
| CT11 | Chinese Onshore Wind (VCS 1188) | Renewable energy | B | C | - | - |

## Overall cross-type: Our v0.6 vs BeZero

- n = 9 projects with both ratings
- Spearman rho: **+0.906**
- Kendall tau: **+0.853**

## Per-type Spearman: Our v0.6 vs BeZero

| Project type | n | Spearman rho | Kendall tau |
|--------------|---|-------------:|------------:|
| Biochar | 2 | n/a (tied) | n/a (tied) |
| CDR | 1 | n/a (n<2) | n/a |
| Cookstoves | 1 | n/a (n<2) | n/a |
| IFM | 1 | n/a (n<2) | n/a |
| Landfill gas | 1 | n/a (n<2) | n/a |
| Methane abatement | 1 | n/a (n<2) | n/a |
| REDD+ | 1 | n/a (n<2) | n/a |
| Renewable energy | 1 | n/a (n<2) | n/a |

## Our v0.6 vs Calyx (cross-type)

- n = 2 projects with both ratings
- Spearman rho: **n/a (tied on one or both variables)**
- Kendall tau: **n/a**

## Combined dataset: REDD+ + cross-type vs BeZero

Pooling the 6 REDD+ projects (our v0.4.1 grades) with the cross-type projects (our v0.6 grades) for an overall correlation against BeZero.
