# Weight Perturbation Analysis (Extended Data 4)

Deterministic +/-5pp perturbation and leave-one-out analysis for the
7-dimension scoring framework.

Baseline weights: removal_type=0.25, additionality=0.2, permanence=0.175, mrv_grade=0.2, vintage_year=0.1, co_benefits=0.0, registry_methodology=0.075
Credits scored: 29

## 1. Weight Perturbation Summary (+/-5pp)

For each dimension, weight is increased/decreased by 5 percentage points
with the delta redistributed proportionally among other non-zero dimensions.

| Dimension | Baseline wt | +5pp flips | +5pp max |delta| | -5pp flips | -5pp max |delta| |
|-----------|:-----------:|:----------:|:---------------:|:----------:|:---------------:|
| removal_type | 0.250 | 0/29 | 1.52 | 0/29 | 1.51 |
| additionality | 0.200 | 0/29 | 0.80 | 1/29 | 0.80 |
| permanence | 0.175 | 2/29 | 2.87 | 2/29 | 2.87 |
| mrv_grade | 0.200 | 2/29 | 1.48 | 0/29 | 1.48 |
| vintage_year | 0.100 | 1/29 | 2.57 | 3/29 | 2.57 |
| co_benefits | 0.000 | 2/29 | 4.00 | 0/29 | 0.00 |
| registry_methodology | 0.075 | 2/29 | 3.68 | 1/29 | 3.68 |

## 2. Per-Perturbation Grade Flips (+/-5pp)

Credits whose final grade changes under each perturbation.

### additionality -5pp (1 flip)

Perturbed weights: removal_type=0.2656, additionality=0.1500, permanence=0.1859, mrv_grade=0.2125, vintage_year=0.1063, registry_methodology=0.0797

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C014 Plan Vivo agroforestry (Mozambique) | A | BBB | 60.15 | 59.66 | -0.49 |

### permanence +5pp (2 flips)

Perturbed weights: removal_type=0.2348, additionality=0.1879, permanence=0.2250, mrv_grade=0.1879, vintage_year=0.0939, registry_methodology=0.0705

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C010 Gold Standard cookstoves (Kenya) | BBB | BB | 46.33 | 44.00 | -2.32 |
| C014 Plan Vivo agroforestry (Mozambique) | A | BBB | 60.15 | 59.23 | -0.92 |

### permanence -5pp (2 flips)

Perturbed weights: removal_type=0.2652, additionality=0.2121, permanence=0.1250, mrv_grade=0.2121, vintage_year=0.1061, registry_methodology=0.0795

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C007 Pachama-verified Brazilian reforestation | A | AA | 74.05 | 75.02 | +0.97 |
| C011 Adipic acid N2O destruction (India) | BBB | A | 57.28 | 60.14 | +2.87 |

### mrv_grade +5pp (2 flips)

Perturbed weights: removal_type=0.2344, additionality=0.1875, permanence=0.1641, mrv_grade=0.2500, vintage_year=0.0938, registry_methodology=0.0703

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C004 Charm Industrial bio-oil injection | AAA | AA | 90.53 | 89.99 | -0.53 |
| C014 Plan Vivo agroforestry (Mozambique) | A | BBB | 60.15 | 59.83 | -0.32 |

### vintage_year +5pp (1 flip)

Perturbed weights: removal_type=0.2361, additionality=0.1889, permanence=0.1653, mrv_grade=0.1889, vintage_year=0.1500, registry_methodology=0.0708

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C007 Pachama-verified Brazilian reforestation | A | AA | 74.05 | 75.49 | +1.44 |

### vintage_year -5pp (3 flips)

Perturbed weights: removal_type=0.2639, additionality=0.2111, permanence=0.1847, mrv_grade=0.2111, vintage_year=0.0500, registry_methodology=0.0792

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C004 Charm Industrial bio-oil injection | AAA | AA | 90.53 | 90.00 | -0.53 |
| C010 Gold Standard cookstoves (Kenya) | BBB | BB | 46.33 | 44.01 | -2.32 |
| C014 Plan Vivo agroforestry (Mozambique) | A | BBB | 60.15 | 58.60 | -1.55 |

### co_benefits +5pp (2 flips)

Perturbed weights: removal_type=0.2375, additionality=0.1900, permanence=0.1662, mrv_grade=0.1900, vintage_year=0.0950, co_benefits=0.0500, registry_methodology=0.0712

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C002 Heirloom DAC (California) | AAA | AA | 93.20 | 89.54 | -3.66 |
| C004 Charm Industrial bio-oil injection | AAA | AA | 90.53 | 87.10 | -3.43 |

### registry_methodology +5pp (2 flips)

Perturbed weights: removal_type=0.2365, additionality=0.1892, permanence=0.1655, mrv_grade=0.1892, vintage_year=0.0946, registry_methodology=0.1250

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C004 Charm Industrial bio-oil injection | AAA | AA | 90.53 | 89.96 | -0.57 |
| C014 Plan Vivo agroforestry (Mozambique) | A | BBB | 60.15 | 59.33 | -0.82 |

### registry_methodology -5pp (1 flip)

Perturbed weights: removal_type=0.2635, additionality=0.2108, permanence=0.1845, mrv_grade=0.2108, vintage_year=0.1054, registry_methodology=0.0250

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C010 Gold Standard cookstoves (Kenya) | BBB | BB | 46.33 | 44.77 | -1.55 |

## 3. Leave-One-Out Summary

For each non-zero dimension, set its weight to 0 and redistribute proportionally.
co_benefits is skipped (weight already 0).

| Dropped dimension | Flips | Max |delta| | Mean |delta| |
|-------------------|:-----:|:-----------:|:------------:|
| removal_type | 4/29 | 7.57 | 1.35 |
| additionality | 2/29 | 3.18 | 1.05 |
| permanence | 4/29 | 10.03 | 2.72 |
| mrv_grade | 1/29 | 5.91 | 2.03 |
| vintage_year | 3/29 | 5.14 | 2.31 |
| co_benefits | (skipped, wt=0) | — | — |
| registry_methodology | 1/29 | 5.52 | 1.45 |

## 4. Per-Dimension Leave-One-Out Flips

### Drop removal_type (4 flips)

Redistributed weights: additionality=0.2667, permanence=0.2333, mrv_grade=0.2667, vintage_year=0.1333, registry_methodology=0.1000

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C004 Charm Industrial bio-oil injection | AAA | AA | 90.53 | 89.37 | -1.16 |
| C007 Pachama-verified Brazilian reforestation | A | AA | 74.05 | 75.40 | +1.35 |
| C014 Plan Vivo agroforestry (Mozambique) | A | BBB | 60.15 | 59.53 | -0.62 |
| C018 REDD+ Cordillera Azul (Peru) | B | BB | 28.20 | 30.27 | +2.07 |

### Drop additionality (2 flips)

Redistributed weights: removal_type=0.3125, permanence=0.2188, mrv_grade=0.2500, vintage_year=0.1250, registry_methodology=0.0938

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C010 Gold Standard cookstoves (Kenya) | BBB | BB | 46.33 | 44.16 | -2.17 |
| C014 Plan Vivo agroforestry (Mozambique) | A | BBB | 60.15 | 58.19 | -1.96 |

### Drop permanence (4 flips)

Redistributed weights: removal_type=0.3030, additionality=0.2424, mrv_grade=0.2424, vintage_year=0.1212, registry_methodology=0.0909

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C004 Charm Industrial bio-oil injection | AAA | AA | 90.53 | 89.58 | -0.95 |
| C007 Pachama-verified Brazilian reforestation | A | AA | 74.05 | 77.45 | +3.40 |
| C011 Adipic acid N2O destruction (India) | BBB | A | 57.28 | 67.30 | +10.03 |
| C012 Landfill methane capture (US) | BBB | A | 55.65 | 65.33 | +9.68 |

### Drop mrv_grade (1 flip)

Redistributed weights: removal_type=0.3125, additionality=0.2500, permanence=0.2188, vintage_year=0.1250, registry_methodology=0.0938

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C017 Grid-connected solar (India) | BB | B | 34.27 | 29.09 | -5.18 |

### Drop vintage_year (3 flips)

Redistributed weights: removal_type=0.2778, additionality=0.2222, permanence=0.1944, mrv_grade=0.2222, registry_methodology=0.0833

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C004 Charm Industrial bio-oil injection | AAA | AA | 90.53 | 89.47 | -1.05 |
| C010 Gold Standard cookstoves (Kenya) | BBB | BB | 46.33 | 41.69 | -4.63 |
| C014 Plan Vivo agroforestry (Mozambique) | A | BBB | 60.15 | 57.06 | -3.09 |

### Drop registry_methodology (1 flip)

Redistributed weights: removal_type=0.2703, additionality=0.2162, permanence=0.1892, mrv_grade=0.2162, vintage_year=0.1081

| Credit | Old grade | New grade | Old composite | New composite | Delta |
|--------|:---------:|:---------:|--------------:|--------------:|------:|
| C010 Gold Standard cookstoves (Kenya) | BBB | BB | 46.33 | 44.00 | -2.33 |

## 5. Aggregate Stability Metrics

- Total +/-5pp perturbations tested: 13
- Total +5pp grade flips: 9
- Total -5pp grade flips: 7
- Max grade flips in any single +/-5pp perturbation: 3
- Total leave-one-out tests: 6
- Total leave-one-out grade flips: 15
- Max grade flips in any single leave-one-out: 4

## 6. Most Perturbation-Sensitive Credits

Credits ranked by how many perturbation scenarios (out of 13 +/-5pp + 6 LOO = 19 total) cause a grade flip.

| Credit | Baseline grade | Composite | Total flips | Buffer to boundary |
|--------|:-------------:|---------:|:-----------:|:------------------:|
| C014 Plan Vivo agroforestry (Mozambique) | A | 60.15 | 8/19 | 0.15 |
| C004 Charm Industrial bio-oil injection | AAA | 90.53 | 7/19 | 0.53 |
| C010 Gold Standard cookstoves (Kenya) | BBB | 46.33 | 6/19 | 1.33 |
| C007 Pachama-verified Brazilian reforest | A | 74.05 | 4/19 | 0.95 |
| C011 Adipic acid N2O destruction (India) | BBB | 57.28 | 2/19 | 2.72 |
| C018 REDD+ Cordillera Azul (Peru) | B | 28.20 | 1/19 | 1.80 |
| C012 Landfill methane capture (US) | BBB | 55.65 | 1/19 | 4.35 |
| C017 Grid-connected solar (India) | BB | 34.27 | 1/19 | 4.27 |
| C002 Heirloom DAC (California) | AAA | 93.20 | 1/19 | 3.20 |

## Notes

- Perturbation redistributes the delta proportionally among other non-zero-weight
  dimensions, preserving sum-to-1. Disqualifier caps are re-applied after rescoring.
- Leave-one-out is the extreme case: the entire dimension weight is redistributed.
- A credit with many flips across perturbation scenarios is boundary-adjacent and
  should be flagged in the paper's sensitivity discussion.
- Synthetic stress-test credits (C026-C029) are included; their grades are typically
  locked by disqualifier caps and rarely flip.
