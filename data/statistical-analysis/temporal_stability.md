# Cross-Temporal Stability Analysis

Compares framework ratings across 3 methodology versions (v0.3, v0.4, v0.6) for 29 credits.

## Weight Vectors

| Dimension | v0.3 | v0.4 | v0.6 |
|-----------|-----:|-----:|-----:|
| removal_type | 0.200 | 0.250 | 0.250 |
| additionality | 0.200 | 0.200 | 0.200 |
| permanence | 0.150 | 0.175 | 0.175 |
| mrv_grade | 0.150 | 0.200 | 0.200 |
| vintage_year | 0.100 | 0.100 | 0.100 |
| co_benefits | 0.100 | 0.000 | 0.000 |
| registry_methodology | 0.100 | 0.075 | 0.075 |
| **sum** | 1.000 | 1.000 | 1.000 |

v0.6 uses the same weight vector as v0.4. The v0.6 changes are rubric-level: registry_methodology collapsed from 4-tier to 2-tier (CCP=80, non-CCP=25-50), and vintage_year tightened (pre-Paris removed for new ratings).

## Grade Agreement Rate

| Version pair | Agreement | Changed | Rate |
|-------------|----------:|--------:|-----:|
| v0.3->v0.4 | 24/29 | 5/29 | 82.8% |
| v0.4->v0.6 | 29/29 | 0/29 | 100.0% |

## Spearman Rank Correlation (composite scores)

| Version pair | Spearman rho |
|-------------|-------------:|
| v0.3->v0.4 | +0.992118 |
| v0.4->v0.6 | +1.000000 |
| v0.3->v0.6 | +0.992118 |

A rho near +1.0 indicates that the *relative ordering* of credits is preserved across versions even if absolute composites shift.

## Maximum Grade Change

Maximum grade-step change: **1** (credit C001, pair v0.3->v0.4)

## Convergence Metric

| Version pair | Avg grade magnitude | Avg composite delta |
|-------------|--------------------:|--------------------:|
| v0.3->v0.4 | 0.1724 | 3.1966 |
| v0.4->v0.6 | 0.0000 | 0.0000 |

Converging: **Yes** -- Grade-change magnitude is non-increasing across consecutive version pairs, indicating the framework is converging.

## Credits with Grade Changes

### v0.3->v0.4: 5 change(s)

| ID | Name | From | To | Composite from | Composite to | Magnitude |
|----|------|------|----|---------------:|-------------:|----------:|
| C001 | Climeworks Orca | AA | AAA | 86.60 | 95.05 | 1 |
| C002 | Heirloom DAC (California) | AA | AAA | 85.50 | 93.20 | 1 |
| C004 | Charm Industrial bio-oil injection | AA | AAA | 83.55 | 90.53 | 1 |
| C007 | Pachama-verified Brazilian reforestation | AA | A | 75.90 | 74.05 | 1 |
| C018 | REDD+ Cordillera Azul (Peru) | BB | B | 30.70 | 28.20 | 1 |

### v0.4->v0.6: no grade changes

**Stable credits** (same grade across all versions): 24/29 (83%)

## Per-Credit Detail

| ID | Name | v0.3 comp | v0.3 grade | v0.4 comp | v0.4 grade | v0.6 comp | v0.6 grade | Stable |
|----|------|----------:|-----------:|----------:|-----------:|----------:|-----------:|--------|
| C001 | Climeworks Orca | 86.60 | AA | 95.05 | AAA | 95.05 | AAA | **NO** |
| C002 | Heirloom DAC (California) | 85.50 | AA | 93.20 | AAA | 93.20 | AAA | **NO** |
| C003 | CarbonCure concrete mineralizati | 79.95 | AA | 87.20 | AA | 87.20 | AA | yes |
| C004 | Charm Industrial bio-oil injecti | 83.55 | AA | 90.53 | AAA | 90.53 | AAA | **NO** |
| C005 | Pacific Biochar (CA) | 81.15 | AA | 83.28 | AA | 83.28 | AA | yes |
| C006 | Husk biochar (Cambodia) | 81.00 | AA | 80.05 | AA | 80.05 | AA | yes |
| C007 | Pachama-verified Brazilian refor | 75.90 | AA | 74.05 | A | 74.05 | A | **NO** |
| C008 | Rexford IFM (Improved Forest Man | 67.35 | A | 68.22 | A | 68.22 | A | yes |
| C009 | Southeast Asian VCS afforestatio | 64.40 | A | 64.72 | A | 64.72 | A | yes |
| C010 | Gold Standard cookstoves (Kenya) | 52.10 | BBB | 46.33 | BBB | 46.33 | BBB | yes |
| C011 | Adipic acid N2O destruction (Ind | 53.50 | BBB | 57.27 | BBB | 57.27 | BBB | yes |
| C012 | Landfill methane capture (US) | 54.15 | BBB | 55.65 | BBB | 55.65 | BBB | yes |
| C013 | Mangrove blue-carbon restoration | 67.95 | A | 66.53 | A | 66.53 | A | yes |
| C014 | Plan Vivo agroforestry (Mozambiq | 62.30 | A | 60.15 | A | 60.15 | A | yes |
| C015 | VCS afforestation 2018 vintage | 49.20 | BBB | 50.27 | BBB | 50.27 | BBB | yes |
| C016 | Gold Standard cookstoves 2019 vi | 39.65 | BB | 34.25 | BB | 34.25 | BB | yes |
| C017 | Grid-connected solar (India) | 34.25 | BB | 34.27 | BB | 34.27 | BB | yes |
| C018 | REDD+ Cordillera Azul (Peru) | 30.70 | BB | 28.20 | B | 28.20 | B | **NO** |
| C019 | Rimba Raya REDD+ (Indonesia) | 29.25 | B | 26.05 | B | 26.05 | B | yes |
| C020 | Chinese CDM wind 2014 vintage | 21.90 | B | 23.25 | B | 23.25 | B | yes |
| C021 | Large hydro (Brazil) 2015 | 23.45 | B | 24.35 | B | 24.35 | B | yes |
| C022 | Kariba REDD+ (Zimbabwe) | 19.65 | B | 19.60 | B | 19.60 | B | yes |
| C023 | HFC-23 destruction (pre-2013) | 22.05 | B | 25.27 | B | 25.27 | B | yes |
| C024 | Chinese CDM wind 2012 | 17.55 | B | 18.95 | B | 18.95 | B | yes |
| C025 | Unverified grassland avoidance 2 | 16.35 | B | 17.12 | B | 17.12 | B | yes |
| C026 | SYNTHETIC: high-composite credit | 78.45 | B | 83.03 | B | 83.03 | B | yes |
| C027 | SYNTHETIC: high-composite credit | 73.10 | BB | 77.22 | BB | 77.22 | BB | yes |
| C028 | SYNTHETIC: high-composite credit | 70.60 | BBB | 74.85 | BBB | 74.85 | BBB | yes |
| C029 | SYNTHETIC: high-composite credit | 65.30 | BBB | 74.03 | BBB | 74.03 | BBB | yes |
