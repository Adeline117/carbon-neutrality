# CCP Calibration Effect Size Analysis

Seed: 42 | Bootstrap resamples: 10,000

## Data Summary

- CCP-eligible credits: n = 165
- Non-CCP credits: n = 153
- CCP mean grade (ordinal): 2.691
- Non-CCP mean grade (ordinal): 0.699
- CCP SD: 1.135
- Non-CCP SD: 1.077

### Grade distributions

| Grade | Ordinal | CCP | Non-CCP |
|-------|---------|-----|---------|
| AAA | 5 | 14 | 0 |
| AA | 4 | 28 | 12 |
| A | 3 | 34 | 0 |
| BBB | 2 | 71 | 0 |
| BB | 1 | 18 | 59 |
| B | 0 | 0 | 82 |

## Effect Sizes

| Metric | Value | 95% CI | Interpretation |
|--------|------:|--------|----------------|
| Cohen's d (pooled SD) | 1.7987 | [1.4984, 2.1610] | Large |
| Glass's delta (non-CCP SD) | 1.8499 | [1.4130, 2.5545] | Large |
| Cliff's delta (nonparametric) | 0.8277 | [0.7515, 0.8955] | Large |
| CLES | 0.9138 | [0.8750, 0.9481] | 91.4% probability CCP > non-CCP |

## Mann-Whitney U Test

- U statistic: 2175.0000
- z-score: 13.0554
- p-value (two-sided): 0.00e+00
- Significant at alpha=0.05: yes
- Significant at alpha=0.001: yes

## CLES (Common Language Effect Size)

- P(random CCP credit outranks random non-CCP credit) = **91.4%**
- 95% CI: [0.8750, 0.9481]

## Interpretation

- Cohen's d > 0.8 is conventionally 'large'; values > 2.0 indicate very large separation.
- Cliff's delta near +1.0 means CCP credits almost always outrank non-CCP credits.
- CLES close to 1.0 means a randomly chosen CCP credit will almost certainly outscore a randomly chosen non-CCP credit.
- The CCP quality gate effectively separates the credit quality distribution into two nearly non-overlapping populations.
