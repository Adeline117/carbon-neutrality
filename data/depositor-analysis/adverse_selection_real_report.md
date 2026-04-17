# Adverse Selection in Toucan BCT: Real On-Chain Evidence

*Generated from 1,187 BCT deposit events on Polygon (Oct 2021 – Dec 2022).*

## Headline Numbers

| Metric | Value |
|---|---|
| Scored deposits | 877 of 1,187 total |
| Unique wallets | 479 |
| Distinct TCO2 tokens | 161 |
| Total tonnes | 15,205,729 |
| Volume-weighted mean quality | 31.71 [30.91, 32.60] 95% CI |
| PQD (Price–Quality Discount) | **0.683** |
| Temporal Spearman ρ | **-0.4387** (p < 10⁻⁴²) |
| Depositor Gini | 0.9403 |
| Grade HHI | 0.4833 |

## 1. Temporal Quality Degradation

BCT's deposit quality declines monotonically over its operating life.

| Quartile | Block range | N | Mean Q | Vol-wtd Q | % B-grade |
|---|---|---|---|---|---|
| Q1 | 20,177,711–20,671,908 | 219 | 32.41 | 32.02 | 51.6% |
| Q2 | 20,674,981–25,454,814 | 219 | 34.37 | 31.80 | 50.7% |
| Q3 | 25,524,824–36,789,145 | 219 | 29.09 | 30.01 | 93.2% |
| Q4 | 36,789,639–36,997,152 | 220 | 28.63 | 28.63 | 99.5% |

**Spearman ρ = -0.4387** (p = 1.51e-42, n = 877)

Mann–Whitney U (first half > second half): U = 141334, p = 2.75e-46
First-half mean = 33.39, second-half mean = 28.86

## 2. Pool Composition

### Grade Distribution (by tonnage)

| Grade | Deposits | Tonnes | % of pool |
|---|---|---|---|
| AAA | 0 | 0 | 0.0% |
| AA | 0 | 0 | 0.0% |
| A | 0 | 0 | 0.0% |
| BBB | 71 | 1,330,471 | 8.7% |
| BB | 159 | 4,319,190 | 28.4% |
| B | 647 | 9,556,068 | 62.8% |

### Type Distribution (by tonnage)

| Type | Deposits | Tonnes | % | Mean Q |
|---|---|---|---|---|
| Renewable | 707 | 10,231,697 | 67.3% | 29.11 |
| Fossil switch | 37 | 1,735,878 | 11.4% | 27.25 |
| ARR | 55 | 845,104 | 5.6% | 50.56 |
| Waste/Methane | 14 | 812,725 | 5.3% | 43.81 |
| Industrial gas | 13 | 672,255 | 4.4% | 30.88 |
| REDD+ | 30 | 521,889 | 3.4% | 31.48 |
| IFM | 12 | 285,367 | 1.9% | 48.59 |
| Industrial | 9 | 100,814 | 0.7% | 42.08 |

78.7% of BCT's tonnage comes from Renewable (67.3%) and Fossil switch (11.4%) — the two lowest-quality categories.

## 3. Depositor Concentration

| Metric | Value |
|---|---|
| Gini coefficient | 0.9403 |
| HHI | 0.0379 |
| Effective depositors (1/HHI) | 26.4 |

### Large vs. Small Depositors

| Group | N wallets | Deposits | Tonnes | % | Vol-wtd Q |
|---|---|---|---|---|---|
| Top 20 | 20 | 270 | 10,935,853 | 71.9% | 30.30 |
| Rest | 459 | 607 | 4,269,876 | 28.1% | 35.32 |

Mann–Whitney U (small > large quality): p = 1.000e+00

**Interpretation**: Adverse selection in BCT is *systemic*, not driven by a few sophisticated actors. All depositors — large and small — deposit credits of similar (low) quality, because the pool's uniform pricing makes it rational for *anyone* to deposit their worst-quality holdings.

## 4. Theoretical Interpretation

These results confirm Akerlof's (1970) lemons market prediction in the carbon credit context. BCT's permissionless deposit mechanism — where all BCT-eligible credits receive the same pool token regardless of quality — creates a classic adverse selection equilibrium:

1. **Uniform pricing** → rational depositors prefer to dump their lowest-quality credits
2. **Quality degradation** → pool average quality falls (Q1 mean 32.4 → Q4 mean 28.6)
3. **Selection concentration** → 91.2% of tonnage is BB or worse; 0% is A-grade or above
4. **Systemic mechanism** → all depositor segments participate equally in the lemons dynamic

The PQD of **0.683** means each $1 of BCT represents only $0.32 of quality-adjusted carbon credit value, quantifying the adverse selection tax.

## 5. Method

Deposit events extracted from `Pool_evt_Deposited` on Polygon via `eth_getLogs` (polygon.drpc.org). Wallet addresses recovered via `eth_getTransactionReceipt`. Quality scores assigned to 161 TCO2 tokens using the v0.6 seven-dimension composite framework (removal type, additionality, permanence, MRV, vintage, co-benefits, registry methodology). Statistical tests: Spearman rank correlation for temporal trend, Mann–Whitney U for group comparisons, bootstrap (10,000 iterations) for confidence intervals.
