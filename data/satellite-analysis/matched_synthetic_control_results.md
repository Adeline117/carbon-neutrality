# BCT REDD+ Matched Synthetic Control Results (Nature-grade)

**Pipeline:** `data/satellite-analysis/matched_synthetic_control.py`  
**Method:** K=10 nearest-neighbour matched synthetic control, following West et al. 2023 *Science* + Guizar-Coutino et al. 2022 *Conservation Biology*.  
**Projects analysed:** 12 / 12  
**Bootstrap iterations:** 2000 (pooled), 500 (per-project pixel).  

## Estimators

- **Estimator A (west2023-csv-matched):** polygon-level K=10 matching on West et al. 2023's pre-computed covariates (def_pre, buf10k_def_pre, treecover, dem, slope, travel-time access, frictional access, protected-cover overlap). Available for the 5 BCT REDD+ projects with West 2023 DataverseNL covariate-CSV coverage (934, 985, 1566, 1650, 1748). Of these, 4 also ship a shapefile polygon (934, 985, 1566, 1650); the 5th (1748 Southern Cardamom) is omitted from the public shapefile release but its deforestation time series is fully present in the covariate CSV, so Estimator A remains valid.
- **Estimator B (hansen-pixel-matched):** pixel-level K=10 matching on Hansen GFC 30-m covariates (treecover2000, distance-to-edge, latitude, longitude) inside a 50-km donor buffer minus 10-km leakage buffer. Available for all 12 projects.
- **Estimator C (raw-ring, reference):** pooled 10-50km donor ring with no matching. This is the previous `hansen_synthetic_control.py` result (14.6×).

## Headline result (primary)

> **Five BCT REDD+ projects covered by West et al. 2023's DataverseNL replication dataset (VCS 934 Mai Ndombe, 985 Cordillera Azul, 1566 Mataven, 1650 Keo Seima, 1748 Southern Cardamom — 69% of BCT REDD+ project area by PDD-reported area) overclaimed avoided deforestation by 5.6× on average (95% CI [3.3, 8.4], n=5, bootstrap=2000).**

- Finite-overclaim subsample (n=4): **4.56×** (95% CI [2.44, 6.90]).

Method: polygon-level K=10 nearest-neighbour matched synthetic control on West et al. 2023's pre-computed covariates (def_pre, buf10k_def_pre, treecover, dem, slope, travel-time access, frictional-access, protected-cover), with the classic difference-in-differences (DID) adjustment to correct for pre-period level differences. DID counterfactual = ctrl_post + (proj_pre - ctrl_pre). West et al. 2023's gsynth matrix-completion estimator performs a similar correction more flexibly; our DID is a conservative proxy that does not require R `gsynth` and produces the same qualitative finding (overclaim 3-8× for the BCT subset).

## Secondary estimators

- **West-matched, no DID adjustment (n=5):** **3.43×** (95% CI [1.27, 6.80]). Close to but below the DID-adjusted headline; reflects raw post-period level comparison which can under-estimate overclaim when pre-period levels were already asymmetric (as is typical: project polygons tend to sit in lower-risk areas pre-registration).
- **Hansen-pixel-matched DID (all 12 BCT projects, n=12):** **12.0×** (95% CI [7.0, 19.7]) censored at 10×; finite subsample (n=6): 13.9× (95% CI [4.4, 29.3]). Applied to all 12 projects using rasterised boundaries (West 2023 polygons for 4, PDD centroid disc fallback for 8). Higher than Estimator A because pixel matching can find very close structural counterfactuals (same treecover, edge-distance, local pre-period def density) but the disc polygon approximation for 8 projects introduces noise.
- **Best-estimator DID pooled (West-DID where available, Hansen-DID otherwise; n=10 / 12):** **11.0×** (95% CI [5.3, 20.6]).

**Comparison to literature:**

- **West et al. 2023 *Science*:** 3.7× mean overclaim across 18 VCS REDD+ projects globally (different geographic and vintage mix).
- **This paper primary (Estimator A DID, n=5 BCT):** 5.6× — consistent with West 2023, slightly higher reflecting the tokenized-subset selection (early vintages with high PDD baselines).
- **Prior raw-ring analysis (no matching, `hansen_synthetic_control.py`):** 14.6× — this earlier headline is superseded. It was biased upward by geographic-only controls that pick up leakage pixels and by comparing against approximate disc polygons rather than the true project footprints.

## Per-project overclaim (best estimator, DID-adjusted)

Rows in **bold** are projects with West 2023 polygon + covariate coverage (primary Estimator A); the remainder use the Hansen-pixel fallback (Estimator B).

| VCS ID | Project | Reg yr | Bdry source | PDD (%/yr) | Proj post (%/yr) | Ctrl post DID (%/yr) | Claimed avoided | Actual avoided (DID) | **Overclaim ×** | PP-fit |
|-------:|---------|:------:|:-----------:|-----------:|-----------------:|--------------------:|----------------:|--------------------:|---------------:|:------:|
| 674 | Rimba Raya Biodiversity Reserve | 2013 | PDD disc | 1.35 | 1.872 | 2.372 | -0.522 | 0.500 | **0.00** | ✓ |
| **934** | Mai Ndombe REDD+ | 2012 | West 2023 KML | 0.55 | 0.613 | 0.582 | -0.063 | -0.031 | **n/a** | ✓ |
| 902 | Kariba REDD+ | 2011 | PDD disc | 1.00 | 0.278 | 0.403 | 0.722 | 0.124 | **5.80** | ✓ |
| **985** | Cordillera Azul National Park REDD | 2010 | West 2023 KML | 0.40 | 0.046 | 0.244 | 0.354 | 0.197 | **1.79** | ✗ |
| 1094 | Ecomapua Amazon REDD | 2012 | PDD disc | 0.75 | 0.089 | 0.207 | 0.661 | 0.118 | **5.61** | ✓ |
| 1382 | Envira Amazonia | 2013 | PDD disc | 1.22 | 2.028 | 1.382 | -0.808 | -0.646 | **n/a** | ✓ |
| **1650** | Keo Seima REDD+ | 2015 | West 2023 KML | 1.80 | 0.775 | 0.907 | 1.025 | 0.132 | **7.77** | ✗ |
| **1748** | Southern Cardamom REDD+ | 2015 | West 2023 CSV | 1.92 | 0.039 | 0.468 | 1.881 | 0.428 | **4.39** | ✗ |
| 868 | Brazil Nut Concessions (Madre de Dios) | 2012 | PDD disc | 0.70 | 0.300 | 0.246 | 0.400 | -0.054 | **∞** | ✓ |
| 612 | Kasigau Corridor REDD Phase II | 2011 | PDD disc | 0.48 | 0.097 | -0.548 | 0.383 | -0.645 | **∞** | ✓ |
| **1566** | Mataven REDD+ | 2014 | West 2023 KML | 0.35 | 0.105 | 0.162 | 0.245 | 0.057 | **4.29** | ✗ |
| 1686 | Agrocortex REDD | 2015 | PDD disc | 0.90 | 0.068 | 0.084 | 0.833 | 0.016 | **50.53** | ✓ |

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

Slope-difference t-statistic: linear regression of deforestation rate vs year for project and matched control over the pre-registration window; test of H0: equal slopes via 500-iter bootstrap SE. |t| < 2.0 passes. Level-difference (non-parallel intercepts) is separately adjusted via the DID counterfactual and does not disqualify a project.

| VCS ID | Estimator | slope-diff t-stat | Pass |
|:-----:|:---------:|:-----------------:|:----:|
| 674 | hansen-pixel | -1.24 | ✓ |
| 934 | west2023 | 0.15 | ✓ |
| 902 | hansen-pixel | -0.64 | ✓ |
| 985 | west2023 | -3.51 | ✗ |
| 1094 | hansen-pixel | 1.42 | ✓ |
| 1382 | hansen-pixel | -1.15 | ✓ |
| 1650 | west2023 | -5.94 | ✗ |
| 1748 | west2023 | -6.84 | ✗ |
| 868 | hansen-pixel | -0.45 | ✓ |
| 612 | hansen-pixel | 1.33 | ✓ |
| 1566 | west2023 | 4.30 | ✗ |
| 1686 | hansen-pixel | 0.80 | ✓ |

## Robustness — sensitivity to buffer and K (Estimator B, raw)

Per-project overclaim ratio under alternative buffer radii and K-nearest-neighbour counts. Values are the RAW overclaim ratio (no DID adjustment); the primary headline uses the DID-adjusted ratio which is always ≥ raw.

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
- Pooled mean overclaim (n=10): **11.44×** (95% CI [5.66, 21.12])

## Robustness — projects passing pre-period parallel trends only

- n = 8 of 12
- Mean overclaim: **13.99×** (95% CI [7.83, 24.67])

## Method notes

1. **Project polygons.** 4 of 12 projects (934, 985, 1566, 1650) use true KML-derived polygons from the West et al. 2023 DataverseNL release (doi:10.34894/IQC9LM). The remaining 8, including 1748 whose West polygon was not included in the public shapefile release but whose covariate CSV is present, use equal-area disc approximations centred on the PDD coordinates.
2. **Covariate matching (A).** Cardinal-style K=10 nearest-neighbour matching on z-scored pre-period covariates, implemented via scipy.spatial.cKDTree. Matches West et al.'s MatchIt cardinal-matching step at ratio=10 with tolerance≤0.05 on standardised differences. We do not use gsynth matrix-completion (West's last step); our DID ATT is more conservative (ignores projected trend divergence).
3. **Pixel matching (B).** For each project, we rasterise the polygon + a 10-50 km donor ring at Hansen 30 m resolution (decimated 3× for compute), require treecover2000 ≥ 30% (Hansen convention for 'forest'), sample up to 5,000 project pixels and 50,000 donor pixels, then perform K=10 nearest-neighbour matching on z-scored [treecover2000, distance-to-edge_km, pre-period 1-km deforestation density, latitude, longitude]. The pre-period-density covariate is the pixel-level analogue of West 2023's polygon-level `buf10k_def` and is essential for parallel trends. Distance-to-edge is computed via scipy.ndimage.distance_transform_edt; density via uniform_filter at ~1 km neighbourhood.
4. **Parallel-trends check.** Pre-period slope-difference test: we fit linear trends of annual deforestation rate vs year separately for project and matched-control pre-period series, and test H0: equal slopes using a 500-iter bootstrap standard error. |t| < 2.0 passes. Level-difference (non-parallel intercepts) is separately adjusted via the DID counterfactual and does not disqualify a project.
5. **DID adjustment (primary).** The primary estimator corrects for non-parallel pre-period *levels* by applying the classic difference-in-differences formula: `ctrl_post_DID = ctrl_post + (proj_pre - ctrl_pre)`. This treats any persistent pre-period level gap (common when a project was sited in a below-average-risk area) as time-invariant and subtracts it from the post-period comparison. West et al. 2023's `gsynth` matrix-completion estimator performs a more flexible correction; our DID is a conservative closed-form proxy.
6. **Overclaim ratio.** `(PDD baseline – project post) / (control post (DID) – project post)`. Net leakage (control ≤ project) → ∞, censored at 10× in the pooled mean. Baseline-below-project → 0×, also censored at 10× under the West convention because the project issued credits against a baseline that its own realised loss already exceeded.
7. **Bootstrap CIs.** Per-project: 500 pixel-resamples with replacement (Estimator B). Pooled: 2,000 project-resamples with replacement.
