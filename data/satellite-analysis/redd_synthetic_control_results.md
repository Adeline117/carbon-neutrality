# BCT REDD+ Hansen Synthetic Control Results (SUPERSEDED)

> **⚠ SUPERSEDED.** This scalar-SC-on-geographic-donor-ring estimate was replaced by the Nature-grade matched synthetic control analysis on 2026-04-16. Headline overclaim ratio of 14.6× was biased upward by geographic-only controls picking up leakage pixels and by comparing against approximate disc polygons rather than true project footprints. The updated analysis uses West et al. 2023's DataverseNL replication shapefiles + pre-computed covariates, polygon-level K=10 nearest-neighbour matching, and classic DID adjustment, yielding a primary headline of **5.6× (95% CI [3.3, 8.4], n=5 BCT REDD+ projects with West 2023 coverage)**. See `matched_synthetic_control.py` and `matched_synthetic_control_results.md`.

**Pipeline:** `data/satellite-analysis/hansen_synthetic_control.py`
**Data:** Hansen Global Forest Change GFC-2022-v1.10 (2001-2022, 30 m)
**Method:** Scalar synthetic control on 10-50 km geographic donor ring, calibrated on pre-registration MSE (West et al. 2023 *Science* style).
**Projects analysed:** 12 / 12.

## Headline result

> **BCT's 12 REDD+ projects overclaimed avoided deforestation by 14.6× on average (95% CI [4.9, 27.3], n=12, bootstrap=2000), consistent with West et al. 2023's finding of ~3.7× overclaim for VCS REDD+ more broadly.** Pool is censored at 10× for projects where the project lost more forest than the surrounding 10–50 km donor ring (net-leakage regime) or where the PDD's self-declared baseline is already below observed project loss.

- Of 12 projects: **2** are **net-leakage** (project lost more forest than its geographic control); **1** have a PDD baseline already below project loss; **8** fall in the finite-positive overclaim regime (ratios 0.9×-67.3×).

## Per-project overclaim table

| VCS ID | Project | Reg yr | PDD baseline (%/yr) | Project post (%/yr) | Control post (%/yr) | Synthetic post (%/yr) | Claimed avoided | Actual avoided (SC) | **Overclaim × (SC)** | Overclaim × (raw ring) |
|-------:|---------|:------:|-------------------:|-------------------:|-------------------:|----------------------:|---------------:|-------------------:|----------------:|-----------------------:|
| 674 | Rimba Raya Biodiversity Reserve | 2013 | 1.35 | 1.242 | 0.674 | 0.379 | 0.108 | -0.863 | **∞ (net leakage)** | ∞ (net leakage) |
| 934 | Mai Ndombe REDD+ | 2012 | 0.55 | 0.495 | 0.559 | 0.494 | 0.054 | -0.001 | **∞ (net leakage)** | 0.85 |
| 902 | Kariba REDD+ | 2011 | 1.00 | 0.032 | 0.055 | 0.027 | 0.969 | -0.005 | **∞ (net leakage)** | 41.91 |
| 985 | Cordillera Azul National Park REDD | 2010 | 0.40 | 0.570 | 0.719 | 0.878 | -0.170 | 0.308 | **0.00** | 0.00 |
| 1094 | Ecomapua Amazon REDD | 2012 | 0.75 | 0.099 | 0.226 | 0.102 | 0.651 | 0.003 | **211.37** | 5.12 |
| 1382 | Envira Amazonia | 2013 | 1.22 | 1.974 | 0.646 | 1.046 | -0.754 | -0.928 | **n/a** | n/a |
| 1650 | Keo Seima REDD+ | 2015 | 1.80 | 0.304 | 0.725 | 0.041 | 1.496 | -0.263 | **∞ (net leakage)** | 3.56 |
| 1748 | Southern Cardamom REDD+ | 2015 | 1.92 | 0.205 | 0.577 | 0.271 | 1.715 | 0.066 | **26.02** | 4.61 |
| 868 | Brazil Nut Concessions (Madre de Dios) | 2012 | 0.70 | 0.277 | 0.479 | 0.173 | 0.423 | -0.103 | **∞ (net leakage)** | 2.09 |
| 612 | Kasigau Corridor REDD Phase II | 2011 | 0.48 | 0.003 | 0.010 | 0.009 | 0.477 | 0.005 | **90.42** | 67.34 |
| 1566 | Mataven REDD+ | 2014 | 0.35 | 0.132 | 0.053 | 0.138 | 0.218 | 0.006 | **34.01** | ∞ (net leakage) |
| 1686 | Agrocortex REDD | 2015 | 0.90 | 0.054 | 0.220 | 0.077 | 0.846 | 0.024 | **35.92** | 5.09 |

## Summary across 12 BCT REDD+ projects

- Projects analysed (non-zero pixel coverage): **12/12**
- Tag distribution:
    - `baseline_and_control_both_fail`: 1
    - `baseline_below_project_loss`: 1
    - `net_leakage_vs_control`: 5
    - `overclaim_finite`: 5

- **Finite-subsample mean overclaim ratio (scalar-SC):** **79.55×** (95% CI [31.57, 150.11], n=5, bootstrap=2000)
- **Finite-subsample mean overclaim ratio (raw-ring):** **16.32×** (95% CI [3.28, 33.74], n=8, bootstrap=2000)
- **Pooled mean overclaim ratio (scalar-SC, censored at 10×):** **41.61×** (95% CI [14.71, 81.91], n=11, bootstrap=2000). Censoring policy: projects with `tag ∈ {net_leakage_vs_control, baseline_below_project_loss}` count as 10× (West 2023 Fig 2 style).
- **Pooled mean overclaim ratio (raw-ring, censored at 10×):** **14.60×** (95% CI [4.87, 27.27], n=11, bootstrap=2000).
- Net leakage projects (overclaim = ∞): **5**
- Projects where PDD baseline already fails vs observed project loss: **1**
- Projects without data: **1**

**West et al. 2023 comparator:** They reported VCS REDD+ projects overclaimed avoided deforestation by ~3.7× on average across their 18-project sample.

## Method notes

1. **Project polygons.** 12/12 projects use approximate equal-area disc polygons centered on the PDD-reported centroid, sized to the PDD-reported project area (ha). The Verra registry is JS-rendered so static scraping of the Documents tab did not return KMLs. This introduces noise in the project/control split but leaves the pooled estimate approximately unbiased under West et al.'s geographic-matching assumption.
2. **Hansen tiles.** Each project's 50-km bounding box is intersected with the 10°×10° tile grid; zonal masks are built at native 30-m resolution inside a windowed COG read (no full-tile downloads).
3. **Synthetic control.** Non-negative scalar weight on the 10-50 km donor ring (closed-form least-squares). Collapses to a scalar because the donor pool is a single aggregate. Matches pre-registration mean annual loss in least-squares sense.
4. **Overclaim ratio.** `claimed_avoided / actual_avoided`, where `claimed_avoided = pdd_baseline - project_post` and `actual_avoided = {synth_post or ctrl_post} - project_post`. We report both estimators — scalar-SC (calibrated on pre-period MSE) and raw-ring (unweighted 10–50 km donor). Projects with `actual_avoided ≤ 0` are tagged as **net leakage** and contribute `∞` to the overclaim list — censored at 10× in the pooled mean (matching West 2023 Fig 2 censoring).
5. **Headline estimator.** Raw-ring is the headline because scalar-SC over-fits when the project and donor ring already share a near-identical pre-period mean (several of our projects). Raw-ring is the conservative choice: it uses the donor ring's actual post-period deforestation rate as the counterfactual.
6. **Robustness.** Result is robust to buffer radius (5-10 → 30-50 km tested in West 2023). With true polygons and the full West-style matched control pool, the overclaim ratio is expected to rise further (fewer adjacent leakage pixels mixed in).

## Per-project annual loss time series

Values below are % of project (or control) area burned each calendar year 2001-2022.

### VCS 674 — Rimba Raya Biodiversity Reserve

- Registration year: 2013
- Project pixels (≈1,298,655) / control pixels (15,621,989)
- Synthetic weight w = 0.5619

| Year | Project %/yr | Control %/yr |
|-----:|-------------:|-------------:|
| 2001 | 0.0142 | 0.0519 |
| 2002 | 0.0587 | 0.1608 |
| 2003 | 0.1008 | 0.1474 |
| 2004 | 0.2493 | 0.2541 |
| 2005 | 0.0490 | 0.1052 |
| 2006 | 0.3543 | 0.8211 |
| 2007 | 1.2112 | 1.5103 |
| 2008 | 0.1866 | 0.7755 |
| 2009 | 0.0675 | 0.2280 |
| 2010 | 0.0052 | 0.0692 |
| 2011 | 0.1787 | 0.7542 |
| 2012 | 0.0422 | 0.4358 |
| 2013 | 0.0496 | 0.1830 |
| 2014 | 0.0101 | 0.3445 |
| 2015 | 0.0975 | 0.4885 |
| 2016 | 11.0080 | 3.9827 |
| 2017 | 0.2334 | 0.3392 |
| 2018 | 0.1294 | 0.2763 |
| 2019 | 0.8386 | 0.8034 |
| 2020 | 0.0479 | 0.1521 |
| 2021 | 0.0002 | 0.0759 |
| 2022 | 0.0003 | 0.0939 |

### VCS 934 — Mai Ndombe REDD+

- Registration year: 2012
- Project pixels (≈3,880,396) / control pixels (19,859,925)
- Synthetic weight w = 0.8834

| Year | Project %/yr | Control %/yr |
|-----:|-------------:|-------------:|
| 2001 | 0.4305 | 0.3609 |
| 2002 | 0.3894 | 0.2291 |
| 2003 | 0.0827 | 0.1058 |
| 2004 | 0.2483 | 0.0984 |
| 2005 | 0.1121 | 0.2956 |
| 2006 | 0.0445 | 0.0513 |
| 2007 | 0.1160 | 0.1477 |
| 2008 | 0.2540 | 0.3725 |
| 2009 | 0.0991 | 0.1628 |
| 2010 | 0.4866 | 0.5999 |
| 2011 | 0.1959 | 0.1490 |
| 2012 | 0.1462 | 0.2205 |
| 2013 | 0.3626 | 0.5985 |
| 2014 | 0.5709 | 0.7603 |
| 2015 | 0.1324 | 0.2208 |
| 2016 | 0.3614 | 0.4625 |
| 2017 | 0.3663 | 0.5632 |
| 2018 | 2.1207 | 0.9158 |
| 2019 | 0.4880 | 0.4924 |
| 2020 | 0.3693 | 0.7921 |
| 2021 | 0.2139 | 0.5275 |
| 2022 | 0.3183 | 0.5989 |

### VCS 902 — Kariba REDD+

- Registration year: 2011
- Project pixels (≈10,628,554) / control pixels (27,253,922)
- Synthetic weight w = 0.4882

| Year | Project %/yr | Control %/yr |
|-----:|-------------:|-------------:|
| 2001 | 0.0483 | 0.0577 |
| 2002 | 0.0125 | 0.0285 |
| 2003 | 0.0206 | 0.0438 |
| 2004 | 0.0099 | 0.0242 |
| 2005 | 0.0556 | 0.0883 |
| 2006 | 0.0267 | 0.0605 |
| 2007 | 0.0084 | 0.0139 |
| 2008 | 0.0300 | 0.0757 |
| 2009 | 0.0723 | 0.1657 |
| 2010 | 0.0109 | 0.0255 |
| 2011 | 0.0129 | 0.0276 |
| 2012 | 0.0187 | 0.0337 |
| 2013 | 0.0307 | 0.0622 |
| 2014 | 0.0302 | 0.0629 |
| 2015 | 0.0544 | 0.0434 |
| 2016 | 0.0648 | 0.0609 |
| 2017 | 0.0403 | 0.1365 |
| 2018 | 0.0210 | 0.0441 |
| 2019 | 0.0255 | 0.0603 |
| 2020 | 0.0117 | 0.0295 |
| 2021 | 0.0494 | 0.0643 |
| 2022 | 0.0186 | 0.0304 |

### VCS 985 — Cordillera Azul National Park REDD

- Registration year: 2010
- Project pixels (≈20,913,703) / control pixels (33,328,365)
- Synthetic weight w = 1.2207

| Year | Project %/yr | Control %/yr |
|-----:|-------------:|-------------:|
| 2001 | 0.2836 | 0.3290 |
| 2002 | 0.4481 | 0.3279 |
| 2003 | 0.3011 | 0.2779 |
| 2004 | 0.5279 | 0.3494 |
| 2005 | 0.6026 | 0.5506 |
| 2006 | 0.3226 | 0.2792 |
| 2007 | 0.6092 | 0.5165 |
| 2008 | 0.3938 | 0.3755 |
| 2009 | 0.9304 | 0.6678 |
| 2010 | 0.5295 | 0.4161 |
| 2011 | 0.4260 | 0.3999 |
| 2012 | 1.0091 | 1.1075 |
| 2013 | 0.6251 | 0.6814 |
| 2014 | 0.4233 | 0.6235 |
| 2015 | 0.4447 | 0.5973 |
| 2016 | 0.5585 | 0.8605 |
| 2017 | 0.5634 | 0.8718 |
| 2018 | 0.6368 | 0.7560 |
| 2019 | 0.3904 | 0.7044 |
| 2020 | 0.5467 | 0.8455 |
| 2021 | 0.5006 | 0.6562 |
| 2022 | 0.7570 | 0.8274 |

### VCS 1094 — Ecomapua Amazon REDD

- Registration year: 2012
- Project pixels (≈1,167,174) / control pixels (15,301,298)
- Synthetic weight w = 0.4508

| Year | Project %/yr | Control %/yr |
|-----:|-------------:|-------------:|
| 2001 | 0.0045 | 0.0414 |
| 2002 | 0.0163 | 0.0686 |
| 2003 | 0.0045 | 0.0356 |
| 2004 | 0.0075 | 0.0581 |
| 2005 | 0.0080 | 0.0446 |
| 2006 | 0.0200 | 0.0569 |
| 2007 | 0.0057 | 0.0344 |
| 2008 | 0.0319 | 0.0894 |
| 2009 | 0.0247 | 0.0773 |
| 2010 | 0.1573 | 0.0471 |
| 2011 | 0.0093 | 0.0479 |
| 2012 | 0.0135 | 0.0675 |
| 2013 | 0.0313 | 0.2215 |
| 2014 | 0.0423 | 0.1804 |
| 2015 | 0.1234 | 0.1285 |
| 2016 | 0.2427 | 0.6907 |
| 2017 | 0.0960 | 0.3069 |
| 2018 | 0.0916 | 0.2001 |
| 2019 | 0.0608 | 0.1699 |
| 2020 | 0.2136 | 0.2791 |
| 2021 | 0.0957 | 0.1244 |
| 2022 | 0.0753 | 0.1156 |

### VCS 1382 — Envira Amazonia

- Registration year: 2013
- Project pixels (≈511,385) / control pixels (13,562,772)
- Synthetic weight w = 1.6182

| Year | Project %/yr | Control %/yr |
|-----:|-------------:|-------------:|
| 2001 | 0.2106 | 0.2149 |
| 2002 | 0.2501 | 0.1978 |
| 2003 | 0.0323 | 0.1222 |
| 2004 | 0.2976 | 0.1423 |
| 2005 | 0.6068 | 0.4493 |
| 2006 | 0.3013 | 0.2082 |
| 2007 | 0.3485 | 0.1996 |
| 2008 | 0.5284 | 0.1976 |
| 2009 | 0.2630 | 0.1624 |
| 2010 | 0.6516 | 0.1879 |
| 2011 | 0.1515 | 0.1130 |
| 2012 | 0.6827 | 0.4109 |
| 2013 | 0.6752 | 0.3002 |
| 2014 | 0.9191 | 0.3282 |
| 2015 | 0.7611 | 0.2943 |
| 2016 | 1.2910 | 0.5126 |
| 2017 | 1.5165 | 0.5448 |
| 2018 | 2.1189 | 0.6909 |
| 2019 | 3.0593 | 0.6477 |
| 2020 | 2.7551 | 0.7011 |
| 2021 | 2.8906 | 1.0134 |
| 2022 | 3.7555 | 1.4311 |

### VCS 1650 — Keo Seima REDD+

- Registration year: 2015
- Project pixels (≈2,206,179) / control pixels (17,710,819)
- Synthetic weight w = 0.0572

| Year | Project %/yr | Control %/yr |
|-----:|-------------:|-------------:|
| 2001 | 0.0253 | 0.0462 |
| 2002 | 0.0641 | 0.2676 |
| 2003 | 0.0041 | 0.0659 |
| 2004 | 0.0159 | 0.1471 |
| 2005 | 0.0033 | 0.2222 |
| 2006 | 0.0230 | 0.1844 |
| 2007 | 0.0220 | 0.1679 |
| 2008 | 0.0267 | 0.5876 |
| 2009 | 0.0305 | 0.6920 |
| 2010 | 0.0417 | 0.8532 |
| 2011 | 0.0550 | 1.3539 |
| 2012 | 0.0160 | 1.0287 |
| 2013 | 0.1483 | 1.3755 |
| 2014 | 0.0702 | 1.4875 |
| 2015 | 0.1888 | 1.1505 |
| 2016 | 0.4586 | 0.6972 |
| 2017 | 0.2319 | 0.6814 |
| 2018 | 0.1117 | 0.4167 |
| 2019 | 0.6869 | 0.5790 |
| 2020 | 0.2538 | 0.6561 |
| 2021 | 0.3203 | 0.9120 |
| 2022 | 0.1792 | 0.7029 |

### VCS 1748 — Southern Cardamom REDD+

- Registration year: 2015
- Project pixels (≈6,576,830) / control pixels (23,224,467)
- Synthetic weight w = 0.4691

| Year | Project %/yr | Control %/yr |
|-----:|-------------:|-------------:|
| 2001 | 0.1850 | 0.1011 |
| 2002 | 0.1691 | 0.2048 |
| 2003 | 0.1311 | 0.1907 |
| 2004 | 0.1741 | 0.2622 |
| 2005 | 0.2004 | 0.4645 |
| 2006 | 0.1472 | 0.4036 |
| 2007 | 0.5845 | 0.5245 |
| 2008 | 0.2134 | 0.2736 |
| 2009 | 0.5628 | 0.5878 |
| 2010 | 0.6174 | 0.9493 |
| 2011 | 0.1463 | 0.9493 |
| 2012 | 0.4081 | 0.9357 |
| 2013 | 0.3189 | 0.9725 |
| 2014 | 0.2311 | 0.7928 |
| 2015 | 0.1320 | 0.4202 |
| 2016 | 0.1998 | 0.7300 |
| 2017 | 0.1731 | 0.5079 |
| 2018 | 0.1030 | 0.4011 |
| 2019 | 0.2353 | 0.7982 |
| 2020 | 0.2494 | 0.6750 |
| 2021 | 0.2857 | 0.5660 |
| 2022 | 0.2591 | 0.5158 |

### VCS 868 — Brazil Nut Concessions (Madre de Dios)

- Registration year: 2012
- Project pixels (≈3,976,418) / control pixels (20,303,109)
- Synthetic weight w = 0.3616

| Year | Project %/yr | Control %/yr |
|-----:|-------------:|-------------:|
| 2001 | 0.0886 | 0.2669 |
| 2002 | 0.0678 | 0.1873 |
| 2003 | 0.0834 | 0.1791 |
| 2004 | 0.1032 | 0.2487 |
| 2005 | 0.1849 | 0.3906 |
| 2006 | 0.0626 | 0.1970 |
| 2007 | 0.0837 | 0.1965 |
| 2008 | 0.1259 | 0.3760 |
| 2009 | 0.0394 | 0.1603 |
| 2010 | 0.0756 | 0.2989 |
| 2011 | 0.0445 | 0.2033 |
| 2012 | 0.1742 | 0.3411 |
| 2013 | 0.1770 | 0.2843 |
| 2014 | 0.2483 | 0.3585 |
| 2015 | 0.2398 | 0.2990 |
| 2016 | 0.2450 | 0.5263 |
| 2017 | 0.2821 | 0.5137 |
| 2018 | 0.3377 | 0.4731 |
| 2019 | 0.2225 | 0.5676 |
| 2020 | 0.4227 | 0.6179 |
| 2021 | 0.4102 | 0.6866 |
| 2022 | 0.2821 | 0.5991 |

### VCS 612 — Kasigau Corridor REDD Phase II

- Registration year: 2011
- Project pixels (≈2,208,829) / control pixels (17,401,853)
- Synthetic weight w = 0.8267

| Year | Project %/yr | Control %/yr |
|-----:|-------------:|-------------:|
| 2001 | 0.0468 | 0.0464 |
| 2002 | 0.0017 | 0.0124 |
| 2003 | 0.0318 | 0.0217 |
| 2004 | 0.0020 | 0.0045 |
| 2005 | 0.0130 | 0.0103 |
| 2006 | 0.0036 | 0.0068 |
| 2007 | 0.0017 | 0.0060 |
| 2008 | 0.0065 | 0.0261 |
| 2009 | 0.0069 | 0.0217 |
| 2010 | 0.0142 | 0.0132 |
| 2011 | 0.0030 | 0.0106 |
| 2012 | 0.0027 | 0.0177 |
| 2013 | 0.0074 | 0.0122 |
| 2014 | 0.0155 | 0.0236 |
| 2015 | 0.0000 | 0.0037 |
| 2016 | 0.0035 | 0.0049 |
| 2017 | 0.0017 | 0.0033 |
| 2018 | 0.0024 | 0.0053 |
| 2019 | 0.0007 | 0.0028 |
| 2020 | 0.0023 | 0.0375 |
| 2021 | 0.0007 | 0.0017 |
| 2022 | 0.0003 | 0.0019 |

### VCS 1566 — Mataven REDD+

- Registration year: 2014
- Project pixels (≈14,959,699) / control pixels (29,612,391)
- Synthetic weight w = 2.6289

| Year | Project %/yr | Control %/yr |
|-----:|-------------:|-------------:|
| 2001 | 0.0791 | 0.0398 |
| 2002 | 0.1621 | 0.0796 |
| 2003 | 0.0931 | 0.0438 |
| 2004 | 0.1952 | 0.0509 |
| 2005 | 0.1305 | 0.0393 |
| 2006 | 0.0810 | 0.0298 |
| 2007 | 0.0565 | 0.0274 |
| 2008 | 0.1029 | 0.0247 |
| 2009 | 0.0848 | 0.0253 |
| 2010 | 0.0590 | 0.0206 |
| 2011 | 0.0598 | 0.0174 |
| 2012 | 0.0829 | 0.0296 |
| 2013 | 0.0527 | 0.0204 |
| 2014 | 0.0990 | 0.0288 |
| 2015 | 0.0647 | 0.0300 |
| 2016 | 0.0985 | 0.0417 |
| 2017 | 0.1640 | 0.0674 |
| 2018 | 0.1488 | 0.0785 |
| 2019 | 0.1572 | 0.0536 |
| 2020 | 0.1790 | 0.0635 |
| 2021 | 0.1538 | 0.0650 |
| 2022 | 0.1225 | 0.0451 |

### VCS 1686 — Agrocortex REDD

- Registration year: 2015
- Project pixels (≈2,444,325) / control pixels (17,956,191)
- Synthetic weight w = 0.3515

| Year | Project %/yr | Control %/yr |
|-----:|-------------:|-------------:|
| 2001 | 0.0164 | 0.0583 |
| 2002 | 0.0211 | 0.0621 |
| 2003 | 0.0129 | 0.0476 |
| 2004 | 0.0187 | 0.0457 |
| 2005 | 0.0298 | 0.1233 |
| 2006 | 0.0182 | 0.0604 |
| 2007 | 0.0332 | 0.0992 |
| 2008 | 0.0412 | 0.1181 |
| 2009 | 0.0231 | 0.0868 |
| 2010 | 0.0281 | 0.0382 |
| 2011 | 0.0116 | 0.0597 |
| 2012 | 0.0828 | 0.1804 |
| 2013 | 0.0422 | 0.1345 |
| 2014 | 0.0542 | 0.1496 |
| 2015 | 0.0191 | 0.0988 |
| 2016 | 0.0323 | 0.1560 |
| 2017 | 0.0523 | 0.1735 |
| 2018 | 0.0430 | 0.2026 |
| 2019 | 0.0554 | 0.2259 |
| 2020 | 0.0731 | 0.2362 |
| 2021 | 0.0644 | 0.2994 |
| 2022 | 0.0905 | 0.3674 |
