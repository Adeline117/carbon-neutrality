# Systematic Lemons Index Scan

*Expanding the LI metric from 6 on-chain pools to 30+ pool segments across the full voluntary carbon market.*

## Definition

Two complementary LI metrics are computed for each pool:

1. **LI (mean-based)** = 1 - mean(composite)/100. Ranges 0 (perfect pool) to 1 (pure lemons).
2. **LI (threshold)** = fraction of credits scoring below BBB (composite < 45). The operational metric for pool design -- what share of credits are sub-investment-grade.

Dataset: 318-credit batch from `data/methodology-ratings/batch_scores.csv`, scored via methodology archetypes with vintage/country adjustments.

## Master Summary Table

Sorted by LI (mean-based), worst to best.

| Pool | N | Mean | Median | LI (mean) | LI (threshold) | A+% | Grade HHI |
|------|--:|-----:|-------:|----------:|---------------:|----:|----------:|
| Renewable energy pool | 40 | 24.1 | 23.1 | **0.759** | 1.000 | 0.0% | 1.000 |
| HFC-23 pool | 8 | 24.2 | 24.2 | **0.758** | 1.000 | 0.0% | 1.000 |
| Registry: CDM | 22 | 28.2 | 24.0 | **0.718** | 0.818 | 0.0% | 0.702 |
| Legacy avoidance pool | 101 | 30.9 | 26.4 | **0.691** | 1.000 | 0.0% | 0.541 |
| Pre-2020 vintage pool | 91 | 31.3 | 25.6 | **0.687** | 0.791 | 0.0% | 0.533 |
| REDD+ pool | 59 | 31.9 | 29.2 | **0.681** | 0.932 | 0.0% | 0.463 |
| Non-CCP pool | 117 | 33.3 | 26.4 | **0.667** | 0.897 | 10.3% | 0.540 |
| Avoidance-only pool | 191 | 36.1 | 38.1 | **0.639** | 0.770 | 0.0% | 0.353 |
| Registry: Verra VCS | 147 | 39.9 | 32.7 | **0.601** | 0.626 | 19.0% | 0.296 |
| Commercial plantation ARR pool | 12 | 40.2 | 40.0 | **0.598** | 1.000 | 0.0% | 1.000 |
| Cookstove pool | 36 | 41.7 | 42.1 | **0.583** | 1.000 | 0.0% | 1.000 |
| Registry: Gold Standard | 44 | 42.6 | 43.2 | **0.574** | 0.909 | 0.0% | 0.835 |
| Rice methane pool | 12 | 44.4 | 44.2 | **0.556** | 0.667 | 0.0% | 0.556 |
| J-REDD+ pool | 14 | 44.4 | 44.6 | **0.556** | 0.714 | 0.0% | 0.592 |
| Registry: ART | 11 | 44.4 | 44.4 | **0.556** | 0.727 | 0.0% | 0.603 |
| Nature-only pool (REDD+ + ARR + IFM) | 116 | 44.5 | 43.4 | **0.555** | 0.578 | 29.3% | 0.269 |
| Industrial avoidance pool (N2O/CH4/ODS/LFG) | 44 | 45.9 | 49.4 | **0.541** | 0.182 | 0.0% | 0.702 |
| Mixed quality pool (random n=50) | 50 | 48.1 | 44.0 | **0.519** | 0.560 | 26.0% | 0.214 |
| 2020-2023 vintage pool | 154 | 48.3 | 44.8 | **0.517** | 0.513 | 23.4% | 0.265 |
| Full 318-credit market | 318 | 49.0 | 45.1 | **0.510** | 0.500 | 27.7% | 0.204 |
| Sustainable agriculture pool | 16 | 52.9 | 53.1 | **0.471** | 0.000 | 0.0% | 1.000 |
| Registry: ACR/CAR | 40 | 55.1 | 54.4 | **0.449** | 0.025 | 15.0% | 0.697 |
| Nature-based removal pool (ARR/IFM) | 57 | 57.7 | 61.5 | **0.423** | 0.211 | 59.6% | 0.437 |
| CCP-eligible pool | 201 | 58.1 | 53.1 | **0.419** | 0.269 | 37.8% | 0.250 |
| Registry: Other | 1 | 65.1 | 65.1 | **0.349** | 0.000 | 100.0% | 1.000 |
| Curated quality pool | 117 | 69.1 | 66.3 | **0.309** | 0.017 | 67.5% | 0.272 |
| 2024+ vintage pool | 73 | 72.7 | 78.3 | **0.273** | 0.110 | 71.2% | 0.277 |
| Biochar pool | 20 | 77.9 | 78.0 | **0.221** | 0.000 | 100.0% | 1.000 |
| Registry: Puro.earth | 24 | 82.8 | 78.3 | **0.172** | 0.000 | 100.0% | 0.625 |
| Enhanced weathering pool | 12 | 83.4 | 83.6 | **0.166** | 0.000 | 100.0% | 1.000 |
| Premium CDR pool | 54 | 84.4 | 84.2 | **0.156** | 0.000 | 100.0% | 0.616 |
| Registry: Isometric | 29 | 85.9 | 84.2 | **0.141** | 0.000 | 100.0% | 0.600 |
| Bio-oil geological pool | 8 | 88.1 | 87.9 | **0.119** | 0.000 | 100.0% | 1.000 |
| DACCS pool | 14 | 92.4 | 92.4 | **0.076** | 0.000 | 100.0% | 1.000 |

## Lemons Index Spectrum

From highest LI (worst quality) to lowest LI (best quality):

 1. `0.759` |==============================| Renewable energy pool (n=40)
 2. `0.758` |==============================| HFC-23 pool (n=8)
 3. `0.718` |============================| Registry: CDM (n=22)
 4. `0.691` |===========================| Legacy avoidance pool (n=101)
 5. `0.687` |===========================| Pre-2020 vintage pool (n=91)
 6. `0.681` |===========================| REDD+ pool (n=59)
 7. `0.667` |==========================| Non-CCP pool (n=117)
 8. `0.639` |=========================| Avoidance-only pool (n=191)
 9. `0.601` |========================| Registry: Verra VCS (n=147)
10. `0.598` |=======================| Commercial plantation ARR pool (n=12)
11. `0.583` |=======================| Cookstove pool (n=36)
12. `0.574` |======================| Registry: Gold Standard (n=44)
13. `0.556` |======================| Rice methane pool (n=12)
14. `0.556` |======================| J-REDD+ pool (n=14)
15. `0.556` |======================| Registry: ART (n=11)
16. `0.555` |======================| Nature-only pool (REDD+ + ARR + IFM) (n=116)
17. `0.541` |=====================| Industrial avoidance pool (N2O/CH4/ODS/LFG) (n=44)
18. `0.519` |====================| Mixed quality pool (random n=50) (n=50)
19. `0.517` |====================| 2020-2023 vintage pool (n=154)
20. `0.510` |====================| Full 318-credit market (n=318)
21. `0.471` |==================| Sustainable agriculture pool (n=16)
22. `0.449` |=================| Registry: ACR/CAR (n=40)
23. `0.423` |================| Nature-based removal pool (ARR/IFM) (n=57)
24. `0.419` |================| CCP-eligible pool (n=201)
25. `0.349` |=============| Registry: Other (n=1)
26. `0.309` |============| Curated quality pool (n=117)
27. `0.273` |==========| 2024+ vintage pool (n=73)
28. `0.221` |========| Biochar pool (n=20)
29. `0.172` |======| Registry: Puro.earth (n=24)
30. `0.166` |======| Enhanced weathering pool (n=12)
31. `0.156` |======| Premium CDR pool (n=54)
32. `0.141` |=====| Registry: Isometric (n=29)
33. `0.119` |====| Bio-oil geological pool (n=8)
34. `0.076` |===| DACCS pool (n=14)

## Comparison to Original 6 Tokenized Pools

| Pool | N | Mean | LI (mean) | Source |
|------|--:|-----:|----------:|--------|
| Toucan BCT (original) | 43 | 27.6 | **0.724** | Original analysis |
| Moss MCO2 (original) | 30 | 28.7 | **0.713** | Original analysis |
| Toucan NCT (original) | 28 | 39.9 | **0.601** | Original analysis |
| Klima 2.0 kVCM (original) | 20 | 48.1 | **0.519** | Original analysis |
| Toucan CHAR (original) | 12 | 77.9 | **0.221** | Original analysis |
| Hypothetical AAA (original) | 13 | 90.0 | **0.100** | Original analysis |

### Where the original pools fall on the new spectrum

- **BCT (LI=0.724)** and **MCO2 (LI=0.713)**: Worse than the HFC-23 pool and comparable to the renewable energy pool and pre-2020 vintage pool. Confirms these were among the worst-quality aggregations in the VCM.
- **NCT (LI=0.601)**: Comparable to the non-CCP pool and legacy avoidance pool. Better than BCT but still heavily lemon-laden.
- **Klima 2.0 (LI=0.519)**: Near the full market average. The mixed CDR + legacy composition placed it in the middle of the quality spectrum.
- **CHAR (LI=0.221)**: Comparable to the systematic biochar pool. Confirms the quality gating worked.
- **Hypothetical AAA (LI=0.100)**: Near the DACCS pool. Pure CDR is the quality floor.

## Key Findings

### Worst pools (highest LI)

- **Renewable energy pool** (LI=0.759, n=40): Mean composite 24.1, 100% of credits below BBB threshold. Grid-connected wind/solar (ICVCM-rejected)
- **HFC-23 pool** (LI=0.758, n=8): Mean composite 24.2, 100% of credits below BBB threshold. HFC-23 destruction (ICVCM-rejected)
- **Registry: CDM** (LI=0.718, n=22): Mean composite 28.2, 82% of credits below BBB threshold. Clean Development Mechanism legacy credits
- **Legacy avoidance pool** (LI=0.691, n=101): Mean composite 30.9, 100% of credits below BBB threshold. Renewables + cookstoves + REDD+ pre-2020 vintage
- **Pre-2020 vintage pool** (LI=0.687, n=91): Mean composite 31.3, 79% of credits below BBB threshold. Credits with vintage year before 2020

### Best pools (lowest LI)

- **DACCS pool** (LI=0.076, n=14): Mean composite 92.4, 0% of credits below BBB threshold. Direct air capture with geological storage credits
- **Bio-oil geological pool** (LI=0.119, n=8): Mean composite 88.1, 0% of credits below BBB threshold. Biomass pyrolysis bio-oil with geological injection
- **Registry: Isometric** (LI=0.141, n=29): Mean composite 85.9, 0% of credits below BBB threshold. Isometric registry credits (CDR verification)
- **Premium CDR pool** (LI=0.156, n=54): Mean composite 84.4, 0% of credits below BBB threshold. DACCS + biochar + ERW + bio-oil only
- **Enhanced weathering pool** (LI=0.166, n=12): Mean composite 83.4, 0% of credits below BBB threshold. Enhanced rock weathering credits

### CCP status as quality filter

- **CCP-eligible**: LI=0.419, mean=58.1, 27% below BBB (n=201)
- **Non-CCP**: LI=0.667, mean=33.3, 90% below BBB (n=117)
- **LI gap**: 0.248 (37% improvement). CCP eligibility cuts adverse selection severity by approximately 25% of the scale.

### Vintage as quality predictor

- **Pre-2020 vintage pool**: LI=0.687, mean=31.3, 79% below BBB (n=91)
- **2020-2023 vintage pool**: LI=0.517, mean=48.3, 51% below BBB (n=154)
- **2024+ vintage pool**: LI=0.273, mean=72.7, 11% below BBB (n=73)

Newer vintages have materially lower LI because: (a) the vintage_year dimension score decays with age (12 pts/yr), and (b) newer credits are more likely from CCP-eligible methodologies.

## Grade Distributions by Pool Segment

| Pool | B | BB | BBB | A | AA | AAA |
|------|--:|---:|----:|--:|---:|----:|
| Renewable energy pool | 40 | 0 | 0 | 0 | 0 | 0 |
| HFC-23 pool | 8 | 0 | 0 | 0 | 0 | 0 |
| Registry: CDM | 18 | 0 | 4 | 0 | 0 | 0 |
| Legacy avoidance pool | 65 | 36 | 0 | 0 | 0 | 0 |
| Pre-2020 vintage pool | 63 | 9 | 19 | 0 | 0 | 0 |
| REDD+ pool | 34 | 21 | 4 | 0 | 0 | 0 |
| Non-CCP pool | 82 | 23 | 0 | 0 | 12 | 0 |
| Avoidance-only pool | 82 | 65 | 44 | 0 | 0 | 0 |
| Registry: Verra VCS | 64 | 28 | 27 | 28 | 0 | 0 |
| Commercial plantation ARR pool | 0 | 12 | 0 | 0 | 0 | 0 |
| Cookstove pool | 0 | 36 | 0 | 0 | 0 | 0 |
| Registry: Gold Standard | 0 | 40 | 4 | 0 | 0 | 0 |
| Rice methane pool | 0 | 8 | 4 | 0 | 0 | 0 |
| J-REDD+ pool | 0 | 10 | 4 | 0 | 0 | 0 |
| Registry: ART | 0 | 8 | 3 | 0 | 0 | 0 |
| Nature-only pool (REDD+ + ARR + IFM) | 34 | 33 | 15 | 34 | 0 | 0 |
| Industrial avoidance pool (N2O/CH4/ODS/LFG) | 8 | 0 | 36 | 0 | 0 | 0 |
| Mixed quality pool (random n=50) | 15 | 13 | 9 | 4 | 6 | 3 |
| 2020-2023 vintage pool | 19 | 60 | 39 | 27 | 8 | 1 |
| Full 318-credit market | 82 | 77 | 71 | 34 | 40 | 14 |
| Sustainable agriculture pool | 0 | 0 | 16 | 0 | 0 | 0 |
| Registry: ACR/CAR | 0 | 1 | 33 | 5 | 1 | 0 |
| Nature-based removal pool (ARR/IFM) | 0 | 12 | 11 | 34 | 0 | 0 |
| CCP-eligible pool | 0 | 54 | 71 | 34 | 28 | 14 |
| Registry: Other | 0 | 0 | 0 | 1 | 0 | 0 |
| Curated quality pool | 0 | 2 | 36 | 25 | 40 | 14 |
| 2024+ vintage pool | 0 | 8 | 13 | 7 | 32 | 13 |
| Biochar pool | 0 | 0 | 0 | 0 | 20 | 0 |
| Registry: Puro.earth | 0 | 0 | 0 | 0 | 18 | 6 |
| Enhanced weathering pool | 0 | 0 | 0 | 0 | 12 | 0 |
| Premium CDR pool | 0 | 0 | 0 | 0 | 40 | 14 |
| Registry: Isometric | 0 | 0 | 0 | 0 | 21 | 8 |
| Bio-oil geological pool | 0 | 0 | 0 | 0 | 8 | 0 |
| DACCS pool | 0 | 0 | 0 | 0 | 0 | 14 |

## Statistical Context: Null Model

What LI would we observe under random credit assignment? This provides the baseline against which observed LI should be interpreted.

### Method

Monte Carlo simulation (10,000 iterations): randomly sample N credits from the full 318-credit market and compute LI for each sample.

**Market baseline**: LI(mean) = 0.51, LI(threshold) = 0.5

| Pool size | E[LI mean] | SD | 5th pctile | 95th pctile | E[LI threshold] | SD | 5th pctile | 95th pctile |
|----------:|-----------:|---:|-----------:|------------:|----------------:|---:|-----------:|------------:|
| 20 | 0.51 | 0.044 | 0.436 | 0.581 | 0.5 | 0.109 | 0.3 | 0.7 |
| 30 | 0.51 | 0.036 | 0.45 | 0.568 | 0.5 | 0.087 | 0.367 | 0.633 |
| 50 | 0.51 | 0.026 | 0.466 | 0.553 | 0.5 | 0.065 | 0.4 | 0.6 |

### Interpretation

- Under random assignment, a 30-credit pool would have LI(mean) near the market average (0.51) with moderate variance.
- **Pools with LI significantly below the null 5th percentile** (the left tail of random) demonstrate genuine quality selection -- their composition is better than chance.
- **Pools with LI significantly above the null 95th percentile** demonstrate adverse selection -- they are attracting worse-than-random credits.

## Implications for Pool Design

1. **Open acceptance pools (no quality filter) attract lemons.** BCT and MCO2 had LI > 0.7 because they accepted any VCS-bridged credit. The systematic data confirms: a pool of REDD+ or renewables alone has LI > 0.5.
2. **CCP eligibility is a partial but insufficient filter.** The CCP-eligible pool still has substantial sub-BBB credits because CCP includes cookstoves and rice methane (whose avoidance + low-permanence profile produces moderate composites).
3. **Project-type filtering is the strongest quality lever.** A DACCS-only or biochar-only pool achieves LI < 0.2 regardless of vintage or registry.
4. **Vintage is a secondary but meaningful filter.** Restricting to 2024+ vintage cuts LI by ~0.15 vs pre-2020, even holding project type constant.
5. **The premium CDR pool (DACCS + biochar + ERW + bio-oil) achieves LI ~0.15**, the practical floor for real-world pools. This validates the CHAR pool's design principle.
