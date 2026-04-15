# Bootstrap Analysis: Expanded Rank Correlation (n=27)

Date: 2026-04-14  
Bootstrap resamples: 10,000 | Permutations: 10,000 | Seed: 42  
Method: Python standard library only

## 1. Point Estimates

| Statistic | Value |
|-----------|-------|
| Spearman rho | +0.9008 |
| Kendall tau-b | +0.8210 |
| n (paired projects) | 27 |

## 2. Bootstrap Confidence Intervals

### Spearman rho

| Metric | Value |
|--------|-------|
| Point estimate | +0.9008 |
| Bootstrap SE | 0.0452 |
| 95% percentile CI | [+0.7828, +0.9589] |
| 99% percentile CI | [+0.7326, +0.9717] |
| 95% BCa CI | [+0.7777, +0.9580] |
| BCa z0 (bias) | -0.0082 |
| BCa a (acceleration) | -0.0130 |

### Kendall tau-b

| Metric | Value |
|--------|-------|
| Point estimate | +0.8210 |
| Bootstrap SE | 0.0555 |
| 95% percentile CI | [+0.6954, +0.9112] |
| 99% percentile CI | [+0.6399, +0.9310] |

## 3. Permutation Test

One-sided test: H0: rho <= 0, H1: rho > 0

| Metric | Spearman rho | Kendall tau |
|--------|:------------:|:-----------:|
| Observed | +0.9008 | +0.8210 |
| Permutation p-value | 0.0000 | 0.0000 |
| Significant (alpha=0.05) | Yes | Yes |
| Significant (alpha=0.01) | Yes | Yes |
| Significant (alpha=0.001) | Yes | Yes |

p < 1/10,000 = 1.0e-04 (no permuted rho reached the observed value)

## 4. Leave-One-Out Cross-Validation

| Metric | Value |
|--------|-------|
| Full-sample rho | +0.9008 |
| LOO rho range | [+0.8885, +0.9215] |
| LOO rho mean | +0.9005 |
| Max |delta rho| | 0.0207 |
| Most influential | Rimba Raya |
| Stability | GOOD: No single project changes rho by more than 0.05 |

### Per-project LOO results (sorted by influence)

| Rank | ID | Project | Ours | BeZero | rho_LOO | delta |
|-----:|:---|:--------|:----:|:------:|--------:|------:|
| 1 | EXP29 | Rimba Raya | B | BB | +0.9215 | +0.0207 |
| 2 | EXP04 | Envira | BB | BBB | +0.9136 | +0.0128 |
| 3 | EXP07 | Climeworks Orca | AAA | AAA | +0.8885 | -0.0123 |
| 4 | EXP19 | STRATOS DACCS | AAA | AAA | +0.8885 | -0.0123 |
| 5 | EXP20 | Octavia DAC | AAA | AAA | +0.8885 | -0.0123 |
| 6 | EXP09 | Exomad Green | AA | AA | +0.8899 | -0.0109 |
| 7 | EXP21 | Mati Carbon ERW | AA | AA | +0.8899 | -0.0109 |
| 8 | EXP23 | Rebellion H2 | BBB | BB | +0.9079 | +0.0071 |
| 9 | EXP24 | Rebellion H3 | BBB | BB | +0.9079 | +0.0071 |
| 10 | EXP25 | Guyana J-REDD+ | BBB | BB | +0.9079 | +0.0071 |
| 11 | EXP01 | Ecomapua | BB | C | +0.9073 | +0.0065 |
| 12 | EXP18 | Kariba | B | D | +0.8943 | -0.0065 |
| 13 | EXP27 | Brazil Nut | BB | C | +0.9073 | +0.0065 |
| 14 | EXP13 | Rebellion H1 | A | A | +0.8956 | -0.0052 |
| 15 | EXP22 | Tradewater ODS | A | A | +0.8956 | -0.0052 |
| 16 | EXP03 | Mai Ndombe | BB | BB | +0.9047 | +0.0039 |
| 17 | EXP17 | Chinese Wind | B | C | +0.8969 | -0.0039 |
| 18 | EXP30 | Cordillera Azul | B | C | +0.8969 | -0.0039 |
| 19 | EXP15 | Southern Cardamom | B | B | +0.9045 | +0.0037 |
| 20 | EXP08 | Novocarbo Rhine | AA | A | +0.8981 | -0.0027 |
| 21 | EXP05 | Luangwa | BB | B | +0.9024 | +0.0016 |
| 22 | EXP06 | Guanare | BB | B | +0.9024 | +0.0016 |
| 23 | EXP14 | Family Forest | BBB | BBB | +0.9005 | -0.0003 |
| 24 | EXP02 | Keo Seima | BBB | A | +0.9006 | -0.0001 |
| 25 | EXP10 | EcoSafi Cookstove | BBB | A | +0.9006 | -0.0001 |
| 26 | EXP16 | Qnergy LFG | BBB | A | +0.9006 | -0.0001 |
| 27 | EXP26 | BRCarbon APD | BBB | A | +0.9006 | -0.0001 |

## 5. Subgroup Analysis

| Subgroup | n | Spearman rho | 95% CI | SE | Perm p |
|----------|--:|:------------:|--------|---:|-------:|
| Removal/CDR (DACCS, biochar, ERW) | 9 | +0.9733 | [+0.8463, +1.0000] | 0.0469 | 0.0003 |
| Avoidance (REDD+, cookstoves, renewables, methane, ODS) | 18 | +0.8019 | [+0.5443, +0.9171] | 0.0978 | 0.0000 |
| CCP-eligible subset | 10 | +0.9677 | [+0.8286, +1.0000] | 0.0490 | 0.0002 |
| Non-CCP subset | 17 | +0.7753 | [+0.4776, +0.9232] | 0.1162 | 0.0003 |

**Removal/CDR (DACCS, biochar, ERW)** (n=9): Climeworks Orca, Novocarbo Rhine, Exomad Green, Rebellion H1, STRATOS DACCS, Octavia DAC, Mati Carbon ERW, Rebellion H2, Rebellion H3

**Avoidance (REDD+, cookstoves, renewables, methane, ODS)** (n=18): Ecomapua, Keo Seima, Mai Ndombe, Envira, Luangwa, Guanare, EcoSafi Cookstove, Family Forest, Southern Cardamom, Qnergy LFG, Chinese Wind, Kariba, Rimba Raya, Cordillera Azul, Tradewater ODS, Guyana J-REDD+, BRCarbon APD, Brazil Nut

**CCP-eligible subset** (n=10): Climeworks Orca, Novocarbo Rhine, Exomad Green, Rebellion H1, STRATOS DACCS, Octavia DAC, Mati Carbon ERW, Tradewater ODS, Rebellion H2, Rebellion H3

**Non-CCP subset** (n=17): Ecomapua, Keo Seima, Mai Ndombe, Envira, Luangwa, Guanare, EcoSafi Cookstove, Family Forest, Southern Cardamom, Qnergy LFG, Chinese Wind, Kariba, Rimba Raya, Cordillera Azul, Guyana J-REDD+, BRCarbon APD, Brazil Nut

## 6. Interpretation

- The observed Spearman rho of +0.901 is highly statistically significant (p < 1.0e-04).
- The 95% bootstrap CI [+0.783, +0.959] does not include zero, confirming strong positive rank agreement.
- LOO analysis shows the result is good (max single-project influence: 0.021).
- Both removal/CDR and avoidance subgroups show positive correlations, though sample sizes limit subgroup power.
