# Expert BWS Weight Calibration Results

*N = 5 respondents, 500 bootstrap resamples.*

## 1. Aggregate BWS Scores

| Dimension | BWS Score (mean) | BWS Score (std) | Standardized |
|-----------|----------------:|----------------:|-------------:|
| removal_type | +4.80 | 4.32 | +0.480 |
| additionality | +5.00 | 4.00 | +0.500 |
| permanence | +2.40 | 3.97 | +0.240 |
| mrv_grade | +1.80 | 2.28 | +0.180 |
| vintage_year | -4.00 | 0.00 | -0.400 |
| registry_methodology | -10.00 | 0.00 | -1.000 |

## 2. Weight Comparison

| Dimension | Current weight | BWS weight | 95% CI | Delta |
|-----------|---------------:|-----------:|-------:|------:|
| removal_type | 0.250 | 0.247 | [0.200, 0.294] | -0.003 |
| additionality | 0.200 | 0.250 | [0.206, 0.289] | +0.050 |
| permanence | 0.175 | 0.207 | [0.167, 0.242] | +0.032 |
| mrv_grade | 0.200 | 0.197 | [0.172, 0.222] | -0.003 |
| vintage_year | 0.100 | 0.100 | [0.100, 0.100] | +0.000 |
| registry_methodology | 0.075 | 0.000 | [0.000, 0.000] | -0.075 |

**Current weight ordering:** removal_type > additionality > mrv_grade > permanence > vintage_year > registry_methodology

**BWS-derived ordering:** additionality > removal_type > permanence > mrv_grade > vintage_year > registry_methodology

**Weight-ordering Spearman rho:** +0.814

## 3. Chi-Squared Goodness-of-Fit Test

- chi2 = 0.467 (df = 5)
- p = 0.9914
- **Result: FAIL TO REJECT H0** -- BWS weights are not significantly different from current weights (p > 0.05).
- **Decision rule (A.8 case 1):** Retain current weights.

## 4. Grade Impact Analysis

**Grade changes:** 1 of 29 credits

| Credit | Old grade | New grade | Old composite | New composite |
|--------|----------|----------|-------------:|-------------:|
| C010 Gold Standard cookstoves (Keny | BBB | BB | 46.33 | 43.41 |

## 5. Rank Correlation

**Internal Spearman (current vs BWS weights):** +0.997

*Note: Rank correlation with BeZero cannot be computed until the n=27 overlap dataset is re-scored with the new weights. Run `score.py` with the updated index.json to generate the comparison.*

## 6. Per-Respondent BWS Score Ranges

| Respondent | Most-important dim | Least-important dim | Score range |
|------------|-------------------|--------------------|-----------:|
| R001 | removal_type (+10) | registry_methodology (-10) | 20 |
| R002 | additionality (+8) | registry_methodology (-10) | 18 |
| R003 | removal_type (+8) | registry_methodology (-10) | 18 |
| R004 | permanence (+9) | registry_methodology (-10) | 19 |
| R005 | additionality (+10) | registry_methodology (-10) | 20 |

## 7. Decision Summary for v0.6

| Check | Status |
|-------|--------|
| N >= 20 (stable count analysis) | BELOW TARGET (N=5) |
| N >= 30 (MNL estimation) | COUNT ONLY (N=5) |
| Chi-squared p > 0.05 | YES (p=0.9914) |
| Rank ordering matches | YES (rho=+0.814) |
| Grade flips | 1 |
| Max weight delta | 0.075 |
