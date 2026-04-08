# Sensitivity Analysis

Baseline grades from v0.4 weights: {'removal_type': 0.25, 'additionality': 0.2, 'permanence': 0.175, 'mrv_grade': 0.2, 'vintage_year': 0.1, 'co_benefits': 0.0, 'registry_methodology': 0.075}

## 1. Weight perturbation (+/-5pp)

For each dimension, add or subtract 5 percentage points of weight and redistribute the delta proportionally across the other dimensions. Report the number of credits whose final grade changes.

| Dimension | Baseline | +5pp flips | -5pp flips |
|-----------|----------|-----------|-----------|
| removal_type | 0.250 | 1/14 | 1/14 |
| additionality | 0.200 | 0/14 | 0/14 |
| permanence | 0.175 | 0/14 | 1/14 |
| mrv_grade | 0.200 | 1/14 | 1/14 |
| vintage_year | 0.100 | 1/14 | 1/14 |
| co_benefits | 0.000 | 2/14 | 0/14 |
| registry_methodology | 0.075 | 1/14 | 1/14 |

## 2. Leave-one-out

For each dimension with nonzero weight, set its weight to 0 and redistribute proportionally to the others. Report grade flips. (co_benefits is skipped since its v0.4 weight is already 0.)

| Dropped dimension | Flips |
|-------------------|-------|
| removal_type | 1/14 |
| additionality | 0/14 |
| permanence | 1/14 |
| mrv_grade | 2/14 |
| vintage_year | 1/14 |
| registry_methodology | 2/14 |

## 3. Key-credit stability under score perturbation

Automatically identifies the credits closest to a grade boundary. Credits with buffer < 2.0 are grade-sensitive to small per-dimension rescoring.

| Credit | Current grade | Current composite | Nearest boundary | Buffer |
|--------|---------------|-------------------|------------------|--------|
| T010 Charm Industrial bio-oil | AAA | 90.15 | 90 | 0.15 |
| T003 Moss MCO2 | BB | 30.5 | 30 | 0.50 |
| T001 Toucan BCT (Base Carbon Tonne) | BB | 31.1 | 30 | 1.10 |
| T002 Toucan NCT (Nature Carbon Tonne) | BBB | 47.15 | 45 | 2.15 |
| T006 C3 C3T (Universal Base) | BBB | 47.23 | 45 | 2.23 |
| T008 Isometric/Heirloom DAC attestati | AAA | 93.05 | 90 | 3.05 |

## 4. Interpretation notes

- Weight-perturbation flips near zero or one credit per perturbation indicate stable weighting; multi-credit flips indicate fragility that should be flagged to expert reviewers.
- Leave-one-out is a stronger test: if dropping a dimension leaves grades largely unchanged, the dimension is redundant with the others.
- Buffer < 2.0 in the key-credit table indicates a credit whose grade is sensitive to per-dimension rescoring and should be flagged in the paper's sensitivity discussion.
