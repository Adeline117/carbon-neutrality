# Sensitivity Analysis

Baseline grades from v0.4 weights: {'removal_type': 0.25, 'additionality': 0.2, 'permanence': 0.175, 'mrv_grade': 0.2, 'vintage_year': 0.1, 'co_benefits': 0.0, 'registry_methodology': 0.075}

## 1. Weight perturbation (+/-5pp)

For each dimension, add or subtract 5 percentage points of weight and redistribute the delta proportionally across the other dimensions. Report the number of credits whose final grade changes.

| Dimension | Baseline | +5pp flips | -5pp flips |
|-----------|----------|-----------|-----------|
| removal_type | 0.250 | 0/29 | 0/29 |
| additionality | 0.200 | 0/29 | 1/29 |
| permanence | 0.175 | 2/29 | 2/29 |
| mrv_grade | 0.200 | 2/29 | 0/29 |
| vintage_year | 0.100 | 1/29 | 3/29 |
| co_benefits | 0.000 | 2/29 | 0/29 |
| registry_methodology | 0.075 | 2/29 | 1/29 |

## 2. Leave-one-out

For each dimension with nonzero weight, set its weight to 0 and redistribute proportionally to the others. Report grade flips. (co_benefits is skipped since its v0.4 weight is already 0.)

| Dropped dimension | Flips |
|-------------------|-------|
| removal_type | 4/29 |
| additionality | 2/29 |
| permanence | 4/29 |
| mrv_grade | 1/29 |
| vintage_year | 3/29 |
| registry_methodology | 1/29 |

## 3. Key-credit stability under score perturbation

Automatically identifies the credits closest to a grade boundary. Credits with buffer < 2.0 are grade-sensitive to small per-dimension rescoring.

| Credit | Current grade | Current composite | Nearest boundary | Buffer |
|--------|---------------|-------------------|------------------|--------|
| C014 Plan Vivo agroforestry (Mozambiq | A | 60.15 | 60 | 0.15 |
| C004 Charm Industrial bio-oil injecti | AAA | 90.53 | 90 | 0.53 |
| C007 Pachama-verified Brazilian refor | A | 74.05 | 75 | 0.95 |
| C010 Gold Standard cookstoves (Kenya) | BBB | 46.33 | 45 | 1.33 |
| C018 REDD+ Cordillera Azul (Peru) | B | 28.2 | 30 | 1.80 |
| C011 Adipic acid N2O destruction (Ind | BBB | 57.28 | 60 | 2.72 |

## 4. Interpretation notes

- Weight-perturbation flips near zero or one credit per perturbation indicate stable weighting; multi-credit flips indicate fragility that should be flagged to expert reviewers.
- Leave-one-out is a stronger test: if dropping a dimension leaves grades largely unchanged, the dimension is redundant with the others.
- Buffer < 2.0 in the key-credit table indicates a credit whose grade is sensitive to per-dimension rescoring and should be flagged in the paper's sensitivity discussion.
