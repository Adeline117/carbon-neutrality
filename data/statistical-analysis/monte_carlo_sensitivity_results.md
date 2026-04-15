# Monte Carlo Sensitivity Analysis

Seed: 42 | Iterations per concentration: 10,000

Weight vectors sampled from Dirichlet(alpha_i = w_i * concentration).
co_benefits weight forced to 0 (safeguards-gate).

## Global Robustness by Concentration

| Concentration | Global robustness | Fragile credits (stability < 90%) |
|:-------------:|:-----------------:|:---------------------------------:|
| 20 | 90.06% | 10 / 29 |
| 50 | 93.68% | 5 / 29 |
| 100 | 95.43% | 5 / 29 |

## Per-Credit Results (concentration=50)

| ID | Name | Base grade | Stability | P(up) | P(down) | Comp mean +/- std |
|----|------|-----------|-----------|-------|---------|-------------------|
| C014 | Plan Vivo agroforestry (Mozambique) | A | 51.5% **FRAGILE** | 0.0% | 48.5% | 60.1 +/- 1.7 |
| C010 | Gold Standard cookstoves (Kenya) | BBB | 66.1% **FRAGILE** | 0.0% | 33.9% | 46.3 +/- 3.2 |
| C004 | Charm Industrial bio-oil injection | AAA | 72.7% **FRAGILE** | 0.0% | 27.3% | 90.5 +/- 0.9 |
| C007 | Pachama-verified Brazilian reforest | A | 74.0% **FRAGILE** | 26.0% | 0.0% | 74.0 +/- 1.6 |
| C011 | Adipic acid N2O destruction (India) | BBB | 78.1% **FRAGILE** | 21.9% | 0.0% | 57.2 +/- 3.5 |
| C012 | Landfill methane capture (US) | BBB | 90.5% | 9.3% | 0.2% | 55.6 +/- 3.4 |
| C016 | Gold Standard cookstoves 2019 vinta | BB | 95.0% | 0.0% | 5.0% | 34.3 +/- 2.6 |
| C017 | Grid-connected solar (India) | BB | 96.6% | 0.0% | 3.4% | 34.3 +/- 2.3 |
| C018 | REDD+ Cordillera Azul (Peru) | B | 97.3% | 2.7% | 0.0% | 28.2 +/- 0.9 |
| C015 | VCS afforestation 2018 vintage | BBB | 97.8% | 0.0% | 2.2% | 50.3 +/- 2.3 |
| C023 | HFC-23 destruction (pre-2013) | B | 97.8% | 2.2% | 0.0% | 25.3 +/- 2.3 |
| C009 | Southeast Asian VCS afforestation | A | 99.7% | 0.0% | 0.3% | 64.7 +/- 1.9 |
| C021 | Large hydro (Brazil) 2015 | B | 99.8% | 0.2% | 0.0% | 24.4 +/- 1.9 |
| C003 | CarbonCure concrete mineralization | AA | 99.8% | 0.2% | 0.0% | 87.2 +/- 0.9 |
| C013 | Mangrove blue-carbon restoration | A | 100.0% | 0.0% | 0.0% | 66.5 +/- 2.0 |
| C002 | Heirloom DAC (California) | AAA | 100.0% | 0.0% | 0.0% | 93.2 +/- 0.7 |
| C001 | Climeworks Orca | AAA | 100.0% | 0.0% | 0.0% | 95.0 +/- 0.7 |
| C005 | Pacific Biochar (CA) | AA | 100.0% | 0.0% | 0.0% | 83.3 +/- 0.8 |
| C006 | Husk biochar (Cambodia) | AA | 100.0% | 0.0% | 0.0% | 80.0 +/- 0.7 |
| C008 | Rexford IFM (Improved Forest Manage | A | 100.0% | 0.0% | 0.0% | 68.2 +/- 1.3 |
| C019 | Rimba Raya REDD+ (Indonesia) | B | 100.0% | 0.0% | 0.0% | 26.1 +/- 1.2 |
| C020 | Chinese CDM wind 2014 vintage | B | 100.0% | 0.0% | 0.0% | 23.2 +/- 1.7 |
| C022 | Kariba REDD+ (Zimbabwe) | B | 100.0% | 0.0% | 0.0% | 19.6 +/- 1.0 |
| C024 | Chinese CDM wind 2012 | B | 100.0% | 0.0% | 0.0% | 18.9 +/- 1.7 |
| C025 | Unverified grassland avoidance 2013 | B | 100.0% | 0.0% | 0.0% | 17.1 +/- 0.9 |
| C026 | SYNTHETIC: high-composite credit wi | B | 100.0% | 0.0% | 0.0% | 83.0 +/- 2.8 |
| C027 | SYNTHETIC: high-composite credit fr | BB | 100.0% | 0.0% | 0.0% | 77.2 +/- 2.6 |
| C028 | SYNTHETIC: high-composite credit wi | BBB | 100.0% | 0.0% | 0.0% | 74.8 +/- 2.6 |
| C029 | SYNTHETIC: high-composite credit wi | BBB | 100.0% | 0.0% | 0.0% | 74.0 +/- 2.6 |

## Fragile Credits (stability < 90%, concentration=50)

### C014: Plan Vivo agroforestry (Mozambique)
- Baseline: A (composite 60.15)
- Stability: 51.5%
- Grade distribution: {'BBB': 0.485, 'A': 0.515}

### C010: Gold Standard cookstoves (Kenya)
- Baseline: BBB (composite 46.33)
- Stability: 66.1%
- Grade distribution: {'BB': 0.3385, 'BBB': 0.6615}

### C004: Charm Industrial bio-oil injection
- Baseline: AAA (composite 90.53)
- Stability: 72.7%
- Grade distribution: {'AA': 0.2727, 'AAA': 0.7273}

### C007: Pachama-verified Brazilian reforestation
- Baseline: A (composite 74.05)
- Stability: 74.0%
- Grade distribution: {'A': 0.7397, 'AA': 0.2603}

### C011: Adipic acid N2O destruction (India)
- Baseline: BBB (composite 57.28)
- Stability: 78.1%
- Grade distribution: {'BB': 0.0004, 'BBB': 0.781, 'A': 0.2186}


## Weight Sensitivity (boundary-adjacent credits, concentration=50)

Pearson correlation between each weight value and composite score across MC iterations.

| Credit | Dimension | Correlation |
|--------|-----------|:-----------:|
| C027 | registry_methodology | -0.947 |
| C028 | registry_methodology | -0.925 |
| C029 | registry_methodology | -0.916 |
| C011 | permanence | -0.875 |
| C009 | vintage_year | +0.865 |
| C012 | permanence | -0.858 |
| C019 | vintage_year | -0.855 |
| C017 | permanence | -0.798 |
| C002 | registry_methodology | -0.780 |
| C023 | removal_type | +0.777 |
| C007 | vintage_year | +0.770 |
| C010 | permanence | -0.769 |
| C014 | vintage_year | +0.749 |
| C018 | mrv_grade | +0.724 |
| C016 | permanence | -0.719 |
| C003 | additionality | -0.698 |
| C004 | mrv_grade | -0.681 |
| C007 | permanence | -0.654 |
| C003 | vintage_year | +0.650 |
| C017 | mrv_grade | +0.636 |
| C016 | registry_methodology | +0.629 |
| C018 | vintage_year | -0.604 |
| C010 | vintage_year | +0.603 |
| C014 | permanence | -0.566 |
| C018 | removal_type | -0.548 |
| C019 | mrv_grade | +0.512 |
| C004 | vintage_year | +0.510 |
| C004 | registry_methodology | -0.490 |
| C023 | vintage_year | -0.487 |
| C029 | vintage_year | +0.479 |
| C002 | vintage_year | +0.475 |
| C023 | permanence | -0.471 |
| C028 | vintage_year | +0.461 |
| C012 | vintage_year | +0.445 |
| C009 | permanence | -0.431 |
| C009 | registry_methodology | -0.423 |
| C011 | mrv_grade | +0.422 |
| C011 | vintage_year | +0.418 |
| C027 | vintage_year | +0.412 |
| C012 | mrv_grade | +0.401 |
| C017 | vintage_year | +0.377 |
| C014 | registry_methodology | -0.363 |
| C010 | registry_methodology | +0.348 |
| C002 | removal_type | +0.345 |
| C004 | removal_type | +0.340 |
| C016 | vintage_year | -0.336 |
| C002 | mrv_grade | -0.325 |
| C004 | permanence | +0.325 |
| C003 | permanence | +0.323 |
| C003 | registry_methodology | -0.311 |
| C014 | additionality | +0.302 |
| C023 | additionality | -0.299 |
| C016 | additionality | +0.295 |
| C019 | removal_type | -0.289 |
| C012 | registry_methodology | +0.276 |
| C007 | mrv_grade | +0.272 |
| C023 | mrv_grade | +0.269 |
| C002 | permanence | +0.256 |
| C003 | removal_type | +0.255 |
| C011 | additionality | +0.254 |
| C019 | additionality | +0.251 |
| C010 | removal_type | -0.208 |
| C016 | mrv_grade | +0.205 |
| C007 | removal_type | -0.203 |
| C014 | mrv_grade | -0.196 |
| C010 | additionality | +0.179 |
| C017 | registry_methodology | -0.172 |
| C028 | removal_type | +0.167 |
| C003 | mrv_grade | -0.165 |
| C018 | additionality | +0.154 |
| C027 | removal_type | +0.153 |
| C011 | registry_methodology | -0.152 |
| C019 | registry_methodology | +0.141 |
| C007 | registry_methodology | +0.140 |
| C012 | removal_type | -0.136 |
| C002 | additionality | -0.133 |
| C029 | removal_type | +0.130 |
| C009 | mrv_grade | +0.128 |
| C018 | permanence | +0.127 |
| C029 | mrv_grade | +0.112 |
| C009 | additionality | -0.112 |
| C019 | permanence | +0.109 |
| C007 | additionality | -0.101 |
| C014 | removal_type | +0.096 |
| C010 | mrv_grade | +0.090 |
| C018 | registry_methodology | +0.084 |
| C028 | additionality | +0.079 |
| C027 | additionality | +0.070 |
| C017 | additionality | -0.069 |
| C027 | permanence | +0.060 |
| C004 | additionality | -0.058 |
| C029 | permanence | -0.057 |
| C011 | removal_type | -0.055 |
| C029 | additionality | +0.049 |
| C012 | additionality | +0.044 |
| C027 | mrv_grade | +0.026 |
| C017 | removal_type | +0.022 |
| C009 | removal_type | +0.021 |
| C016 | removal_type | +0.013 |
| C028 | mrv_grade | +0.010 |
| C028 | permanence | -0.004 |
| C023 | registry_methodology | -0.003 |

## Concentration Comparison

| Credit | Baseline | c=20 stability | c=50 stability | c=100 stability |
|--------|----------|:--------------:|:--------------:|:---------------:|
| C001 Climeworks Orca | AAA | 99.9% | 100.0% | 100.0% |
| C002 Heirloom DAC (California) | AAA | 99.5% | 100.0% | 100.0% |
| C003 CarbonCure concrete mineraliza | AA | 96.9% | 99.8% | 100.0% |
| C004 Charm Industrial bio-oil injec | AAA | 65.6% | 72.7% | 80.4% |
| C005 Pacific Biochar (CA) | AA | 100.0% | 100.0% | 100.0% |
| C006 Husk biochar (Cambodia) | AA | 100.0% | 100.0% | 100.0% |
| C007 Pachama-verified Brazilian ref | A | 66.7% | 74.0% | 80.2% |
| C008 Rexford IFM (Improved Forest M | A | 99.8% | 100.0% | 100.0% |
| C009 Southeast Asian VCS afforestat | A | 96.0% | 99.7% | 100.0% |
| C010 Gold Standard cookstoves (Keny | BBB | 60.5% | 66.1% | 72.2% |
| C011 Adipic acid N2O destruction (I | BBB | 65.3% | 78.1% | 86.9% |
| C012 Landfill methane capture (US) | BBB | 75.5% | 90.5% | 96.7% |
| C013 Mangrove blue-carbon restorati | A | 97.8% | 100.0% | 100.0% |
| C014 Plan Vivo agroforestry (Mozamb | A | 50.0% | 51.5% | 53.4% |
| C015 VCS afforestation 2018 vintage | BBB | 91.4% | 97.8% | 99.7% |
| C016 Gold Standard cookstoves 2019  | BB | 84.8% | 95.0% | 99.0% |
| C017 Grid-connected solar (India) | BB | 88.3% | 96.6% | 99.5% |
| C018 REDD+ Cordillera Azul (Peru) | B | 89.1% | 97.3% | 99.7% |
| C019 Rimba Raya REDD+ (Indonesia) | B | 99.5% | 100.0% | 100.0% |
| C020 Chinese CDM wind 2014 vintage | B | 98.9% | 100.0% | 100.0% |
| C021 Large hydro (Brazil) 2015 | B | 96.4% | 99.8% | 100.0% |
| C022 Kariba REDD+ (Zimbabwe) | B | 100.0% | 100.0% | 100.0% |
| C023 HFC-23 destruction (pre-2013) | B | 89.9% | 97.8% | 99.7% |
| C024 Chinese CDM wind 2012 | B | 100.0% | 100.0% | 100.0% |
| C025 Unverified grassland avoidance | B | 100.0% | 100.0% | 100.0% |
| C026 SYNTHETIC: high-composite cred | B | 100.0% | 100.0% | 100.0% |
| C027 SYNTHETIC: high-composite cred | BB | 100.0% | 100.0% | 100.0% |
| C028 SYNTHETIC: high-composite cred | BBB | 100.0% | 100.0% | 100.0% |
| C029 SYNTHETIC: high-composite cred | BBB | 100.0% | 100.0% | 100.0% |

## Notes

- Concentration=20 is a wide prior (more weight variation); 100 is tight.
- A 'fragile' credit has grade stability < 90%, meaning its grade changes in >10% of random weight samples.
- Global robustness is the mean grade stability across all credits.
- The safeguards-gate (co_benefits=0) is maintained in all samples.
