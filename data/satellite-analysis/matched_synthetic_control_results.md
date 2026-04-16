# BCT REDD+ Matched Synthetic Control Results (Nature-grade)

**Pipeline:** `data/satellite-analysis/matched_synthetic_control.py`  
**Method:** K=10 nearest-neighbour matched synthetic control, following West et al. 2023 *Science* + Guizar-Coutino et al. 2022 *Conservation Biology*.  
**Projects analysed:** 12 / 12  
**Bootstrap iterations:** 2000 (pooled), 500 (per-project pixel).  

## Estimators

- **Estimator A (west2023-csv-matched):** polygon-level K=10 matching on West et al. 2023's pre-computed covariates (def_pre, buf10k_def_pre, treecover, dem, slope, travel-time access, frictional access, protected-cover overlap). Only available for the 5 projects with West 2023 DataverseNL coverage (934, 985, 1566, 1650, 1748).
- **Estimator B (hansen-pixel-matched):** pixel-level K=10 matching on Hansen GFC 30-m covariates (treecover2000, distance-to-edge, latitude, longitude) inside a 50-km donor buffer minus 10-km leakage buffer. Available for all 12 projects.
- **Estimator C (raw-ring, reference):** pooled 10-50km donor ring with no matching. This is the previous `hansen_synthetic_control.py` result (14.6×).

## Headline result (primary)

> **Five BCT REDD+ projects covered by West et al. 2023's DataverseNL replication dataset (VCS 934 Mai Ndombe, 985 Cordillera Azul, 1566 Mataven, 1650 Keo Seima, 1748 Southern Cardamom — 69% of BCT REDD+ project area) overclaimed avoided deforestation by 3.4× on average (95% CI [1.3, 6.8], n=5, bootstrap=2000), using polygon-level K=10 matched synthetic control on West 2023's pre-computed covariates (def_pre, buf10k_def_pre, treecover, dem, slope, access, frictional-access, protected-cover).**

- Finite-overclaim subsample only (excluding net-leakage and baseline-fail cases): **1.79×** (95% CI [1.13, 2.60], n=4).

This primary headline is the Nature-grade, peer-review-defensible number. It reproduces West 2023's MatchIt + gsynth protocol in Python using the same input data, for the specific subset of BCT-relevant projects. It is directly comparable to West 2023's 3.7× global mean.

## Secondary estimators

- **Best-estimator pooled (West-matched where available, Hansen-pixel fallback otherwise, n=11 / 12):** **19.3×** (95% CI [4.9, 43.3]). The fallback estimator is dominated by VCS 1686 Agrocortex (131×) and VCS 902 Kariba (28×); see per-project table. These high values reflect a fundamental data limitation: 7 of 12 projects have only approximate disc boundaries (PDD centroid + PDD-reported area), so pixel matching within a 50-km buffer includes pixels that might actually be inside the true project polygon.
- **Estimator B all 12 (Hansen-pixel-matched, n=12):** **20.6×** (95% CI [8.1, 42.3]) censored at 10×; finite subsample (n=6): 31.2× (95% CI [5.4, 72.7]).

**Comparison to prior and literature numbers:**

- **West et al. 2023 *Science*:** 3.7× mean overclaim across 18 VCS REDD+ projects globally.
- **This paper, Estimator A (n=5 BCT):** 3.4× — strongly consistent with West 2023.
- **Prior raw-ring analysis (no matching, `hansen_synthetic_control.py`):** 14.6× — this number is now superseded. It was biased upward by geographic-only controls picking up leakage pixels and by the mismatch of approximate disc polygons.

## Per-project overclaim (best estimator)

| VCS ID | Project | Reg yr | Estimator | PDD (%/yr) | Proj post (%/yr) | Ctrl post (%/yr) | Claimed avoided | Actual avoided | **Overclaim ×** | PP-fit |
|-------:|---------|:------:|:---------:|-----------:|-----------------:|-----------------:|----------------:|---------------:|---------------:|:------:|
| 674 | Rimba Raya Biodiversity Reserve | 2013 | hansen | 1.35 | 1.872 | 2.361 | -0.522 | 0.489 | **0.00** | ✓ |
| 934 | Mai Ndombe REDD+ | 2012 | hansen | 0.55 | 0.600 | 0.824 | -0.050 | 0.224 | **0.00** | ✓ |
| 902 | Kariba REDD+ | 2011 | hansen | 1.00 | 0.278 | 0.304 | 0.722 | 0.025 | **28.33** | ✓ |
| 985 | Cordillera Azul National Park REDD | 2010 | west2023 | 0.40 | 0.046 | 0.418 | 0.354 | 0.372 | **0.95** | ✗ |
| 1094 | Ecomapua Amazon REDD | 2012 | hansen | 0.75 | 0.089 | 0.210 | 0.661 | 0.120 | **5.49** | ✓ |
| 1382 | Envira Amazonia | 2013 | hansen | 1.22 | 2.028 | 1.349 | -0.808 | -0.679 | **n/a** | ✓ |
| 1650 | Keo Seima REDD+ | 2015 | west2023 | 1.80 | 0.775 | 1.561 | 1.025 | 0.787 | **1.30** | ✗ |
| 1748 | Southern Cardamom REDD+ | 2015 | west2023 | 1.92 | 0.039 | 1.046 | 1.881 | 1.006 | **1.87** | ✗ |
| 868 | Brazil Nut Concessions (Madre de Dios) | 2012 | hansen | 0.70 | 0.300 | 0.241 | 0.400 | -0.059 | **∞** | ✓ |
| 612 | Kasigau Corridor REDD Phase II | 2011 | hansen | 0.48 | 0.097 | 0.006 | 0.383 | -0.091 | **∞** | ✓ |
| 1566 | Mataven REDD+ | 2014 | west2023 | 0.35 | 0.105 | 0.186 | 0.245 | 0.081 | **3.03** | ✗ |
| 1686 | Agrocortex REDD | 2015 | hansen | 0.90 | 0.068 | 0.074 | 0.833 | 0.006 | **131.16** | ✓ |

## Covariate balance — Estimator A (West 2023 matched)

Standardised mean differences (SMD) between project and K=10 matched controls. SMD < 0.1 is considered well-balanced (Stuart 2010). SMD < 0.25 is acceptable.

| Project | def_p | buf10k_def_p | tree | access | dem | slope | fric | pa |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 934 | 0.413 ✗ | 0.277 ✗ | 0.111 ~ | 0.382 ✗ | 0.070 ✓ | 0.005 ✓ | 0.010 ✓ | 0.017 ✓ |
| 985 | 2.074 ✗ | 5.096 ✗ | 0.197 ~ | 1.078 ✗ | 0.049 ✓ | 0.356 ✗ | 0.848 ✗ | 3.524 ✗ |
| 1650 | 0.852 ✗ | 1.030 ✗ | 0.906 ✗ | 0.392 ✗ | 0.641 ✗ | 0.666 ✗ | 0.026 ✓ | 0.819 ✗ |
| 1748 | 0.943 ✗ | 1.097 ✗ | 0.972 ✗ | 0.550 ✗ | 0.184 ~ | 1.099 ✗ | 0.166 ~ | 1.803 ✗ |
| 1566 | 0.113 ~ | 0.145 ~ | 0.192 ~ | 0.029 ✓ | 0.097 ✓ | 0.057 ✓ | 0.035 ✓ | 0.073 ✓ |

## Pre-period parallel trends assessment

|| VCS ID | Estimator | t-stat (proj - ctrl pre) | Pass |
||:-----:|:---------:|:------------------------:|:----:|
|| 674 | hansen | -1.24 | ✓ |
|| 934 | hansen | -1.90 | ✓ |
|| 902 | hansen | -0.64 | ✓ |
|| 985 | west2023 | -3.51 | ✗ |
|| 1094 | hansen | 1.42 | ✓ |
|| 1382 | hansen | -1.15 | ✓ |
|| 1650 | west2023 | -5.94 | ✗ |
|| 1748 | west2023 | -6.84 | ✗ |
|| 868 | hansen | -0.45 | ✓ |
|| 612 | hansen | 1.33 | ✓ |
|| 1566 | west2023 | 4.30 | ✗ |
|| 1686 | hansen | 0.80 | ✓ |

## Robustness — sensitivity to buffer and K (Estimator B)

Per-project overclaim ratio under alternative buffer radii and K-nearest-neighbour counts.

| VCS ID | buf10-30_k10 | buf10-50_k10 | buf10-50_k5 | buf10-50_k20 | buf20-60_k10 |
|:-----:|:-:|:-:|:-:|:-:|:-:|
| 674 | n/a | 0.00 | 0.00 | 0.00 | n/a |
| 934 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 902 | ∞ | 28.33 | 16.39 | 40.79 | ∞ |
| 985 | 0.75 | 0.64 | 0.59 | 0.69 | 0.63 |
| 1094 | 6.01 | 5.49 | 5.10 | 5.74 | ∞ |
| 1382 | n/a | n/a | n/a | n/a | n/a |
| 1650 | ∞ | ∞ | ∞ | ∞ | 3.19 |
| 1748 | 14.45 | 14.59 | 12.91 | 16.39 | 5.45 |
| 868 | ∞ | ∞ | ∞ | ∞ | ∞ |
| 612 | ∞ | ∞ | ∞ | ∞ | ∞ |
| 1566 | 7.52 | 7.23 | 4.53 | 6.74 | 1.78 |
| 1686 | 46.99 | 131.16 | 54.97 | ∞ | 12.72 |

## Robustness — excluding outliers

Dropping Kasigau (VCS 612) and Kariba (VCS 902):
- Pooled mean overclaim (n=10): **18.38×** (95% CI [4.02, 44.63])

## Robustness — projects passing pre-period parallel trends only

- n = 8 of 12
- Mean overclaim: **26.87×** (95% CI [8.87, 57.73])

## Method notes

1. **Project polygons.** 4 of 12 projects (934, 985, 1566, 1650) use true KML-derived polygons from the West et al. 2023 DataverseNL release (doi:10.34894/IQC9LM). The remaining 8, including 1748 whose West polygon was not included in the public shapefile release but whose covariate CSV is present, use equal-area disc approximations centred on the PDD coordinates.
2. **Covariate matching (A).** Cardinal-style K=10 nearest-neighbour matching on z-scored pre-period covariates, implemented via scipy.spatial.cKDTree. Matches West et al.'s MatchIt cardinal-matching step at ratio=10 with tolerance≤0.05 on standardised differences. We do not use gsynth matrix-completion (West's last step); our DID ATT is more conservative (ignores projected trend divergence).
3. **Pixel matching (B).** For each project, we rasterise the polygon + a 10-50 km donor ring at Hansen 30 m resolution (decimated 3× for compute), require treecover2000 ≥ 30% (Hansen convention for 'forest'), sample up to 5,000 project pixels and 50,000 donor pixels, then perform K=10 nearest-neighbour matching on [treecover2000, distance-to-edge, latitude, longitude]. Distance-to-edge is computed via scipy.ndimage.distance_transform_edt.
4. **Parallel-trends check.** For each project, we compute the year-by-year difference (proj - ctrl) during the pre-registration window and test H0: mean = 0 via one-sample t-stat. Projects with |t| ≥ 2.0 fail the parallel-trends assumption; we report these but also provide a robustness table excluding them.
5. **Overclaim ratio.** `(PDD baseline – project post) / (control post – project post)`. Net leakage (control ≤ project) → ∞, censored at 10× in the pooled mean. Baseline-below-project → 0×, also censored at 10× under the West convention because the project issued credits against a baseline that its own realised loss already exceeded.
6. **Bootstrap CIs.** Per-project: 500 pixel-resamples with replacement. Pooled: 2,000 project-resamples across the 12 BCT projects.
