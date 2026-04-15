# Depositor-Level Adverse Selection Analysis: Results

*Testing whether BCT depositors strategically deposited low-quality credits* *while retaining high-quality ones.*

> **NOTE:** These results use **simulated data** for pipeline validation.
> The simulation encodes a 70% adverse selection rate to verify that the
> statistical pipeline correctly detects the signal. Real on-chain data is
> needed for publication-ready results.

## Summary Statistics

| Metric | Value |
|--------|-------|
| Depositors analyzed | 200 |
| Mean quality differential ($\Delta$) | 3.083 |
| Median $\Delta$ | 3.900 |
| SD of $\Delta$ | 3.391 |
| Selection rate ($\Delta > 0$) | 83.5% |
| Depositors with $\Delta > 0$ | 167 / 200 |

## Interpretation of $\Delta$

$\Delta = \bar{{Q}}_{{\text{{retained}}}} - \bar{{Q}}_{{\text{{deposited}}}}$

- $\Delta > 0$: depositor retained higher-quality credits than they deposited (**adverse selection**)
- $\Delta = 0$: no quality differential (random deposit behavior)
- $\Delta < 0$: depositor deposited higher-quality credits than they retained (reverse selection)

## Statistical Tests

### Paired t-test ($H_0$: $\mu_\Delta = 0$)

- $t$ = 12.857
- $p$ = 0.000000
- **Significant at $\alpha = 0.05$**

### Wilcoxon signed-rank test (nonparametric)

- $W^+$ = 17551, $W^-$ = 2150
- $z$ = -9.538
- $p$ = 0.000000
- **Significant**

### Bootstrap 95% CI for mean $\Delta$

- CI: [2.603, 3.547]
- CI excludes zero: **evidence of adverse selection**

### Permutation test (one-sided)

- $p$ = 0.0000

### Effect size

- Cohen's $d$ = 0.909 (large)

## Robustness: Excluding KlimaDAO

| Metric | All depositors | Excluding KlimaDAO |
|--------|---------------|-------------------|
| $n$ | 200 | 200 |
| Mean $\Delta$ | 3.083 | 3.083 |
| Selection rate | 83.5% | 83.5% |
| Cohen's $d$ | 0.909 | 0.909 |
| $p$ (permutation) | 0.0000 | 0.0000 |

## Distribution of Per-Depositor Quality Differentials

| $\Delta$ range | Count | Proportion |
|----------------|-------|------------|
| < -20 | 0 | 0.0% |
| -20 to -10 | 0 | 0.0% |
| -10 to 0 | 31 | 15.5% |
| 0 to +10 | 169 | 84.5% |
| +10 to +20 | 0 | 0.0% |
| > +20 | 0 | 0.0% |

## Methodology

See `methodology.md` for full description of the depositor-level analysis
pipeline, including data collection, quality scoring, statistical tests,
and robustness checks.
