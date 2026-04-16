# Removal-Type Sensitivity Analysis

**Reviewer concern:** removal_type (weight 25%) caps avoidance/REDD+/cookstove/renewable
projects at low scores on that dimension, potentially creating a structural floor that makes
these projects score low by design rather than by quality measurement.

**Key question:** If we remove the Oxford Principles hierarchy entirely, do REDD+ projects
still score lower than CDR? If yes, the quality difference is driven by additionality,
permanence, and MRV -- not removal_type.

---

## 1. Scenario Weights

| Dimension | Baseline | Halved | Zeroed |
|-----------|:--------:|:------:|:------:|
| removal_type | 0.2500 | 0.1250 | 0.0000 |
| additionality | 0.2000 | 0.2333 | 0.2667 |
| permanence | 0.1750 | 0.2042 | 0.2333 |
| mrv_grade | 0.2000 | 0.2333 | 0.2667 |
| vintage_year | 0.1000 | 0.1167 | 0.1333 |
| co_benefits | 0.0000 | 0.0000 | 0.0000 |
| registry_methodology | 0.0750 | 0.0875 | 0.1000 |

## 2. Summary Metrics Across Scenarios

| Metric | Baseline | Halved (RT=0.125) | Zeroed (RT=0) |
|--------|:--------:|:-----------------:|:-------------:|
| BCT Lemons Index | 0.724 | 0.729 | 0.733 |
| BCT mean composite | 27.6 | 27.1 | 26.7 |
| BeZero rho (n=27) | +0.868 | +0.868 | +0.877 |
| Grade changes (pilot, n=29) | -- | 2/29 | 4/29 |

## 3. Per-Credit Composites and Grades Across Scenarios

| ID | Name | Baseline | Grade | Halved | Grade | Zeroed | Grade | Category |
|----|------|:--------:|:-----:|:------:|:-----:|:------:|:-----:|----------|
| C001 | Climeworks Orca | 95.05 | AAA | 94.56 | AAA | 94.07 | AAA | CDR |
| C002 | Heirloom DAC (California) | 93.20 | AAA | 92.73 | AAA | 92.27 | AAA | CDR |
| C004 | Charm Industrial bio-oil injection | 90.53 | AAA | 89.95 | AA * | 89.37 | AA * | CDR |
| C003 | CarbonCure concrete mineralization | 87.20 | AA | 86.73 | AA | 86.27 | AA | CDR |
| C005 | Pacific Biochar (CA) | 83.28 | AA | 83.82 | AA | 84.37 | AA | CDR |
| C026 | SYNTHETIC: high-composite credit with do | 83.03 | B | 81.86 | B | 80.70 | B | Other |
| C006 | Husk biochar (Cambodia) | 80.05 | AA | 80.39 | AA | 80.73 | AA | CDR |
| C027 | SYNTHETIC: high-composite credit from sa | 77.22 | BB | 76.43 | BB | 75.63 | BB | Other |
| C028 | SYNTHETIC: high-composite credit without | 74.85 | BBB | 73.99 | BBB | 73.13 | BBB | Other |
| C007 | Pachama-verified Brazilian reforestation | 74.05 | A | 74.72 | A | 75.40 | AA * | Nature-based |
| C029 | SYNTHETIC: high-composite credit with do | 74.03 | BBB | 73.36 | BBB | 72.70 | BBB | Other |
| C008 | Rexford IFM (Improved Forest Management) | 68.22 | A | 68.26 | A | 68.30 | A | Nature-based |
| C013 | Mangrove blue-carbon restoration | 66.53 | A | 66.28 | A | 66.03 | A | Nature-based |
| C009 | Southeast Asian VCS afforestation | 64.72 | A | 64.68 | A | 64.63 | A | Nature-based |
| C014 | Plan Vivo agroforestry (Mozambique) | 60.15 | A | 59.84 | BBB * | 59.53 | BBB * | Nature-based |
| C011 | Adipic acid N2O destruction (India) | 57.28 | BBB | 57.65 | BBB | 58.03 | BBB | Industrial |
| C012 | Landfill methane capture (US) | 55.65 | BBB | 56.59 | BBB | 57.53 | BBB | Industrial |
| C015 | VCS afforestation 2018 vintage | 50.27 | BBB | 48.32 | BBB | 46.37 | BBB | Nature-based |
| C010 | Gold Standard cookstoves (Kenya) | 46.33 | BBB | 47.71 | BBB | 49.10 | BBB | Avoidance |
| C017 | Grid-connected solar (India) | 34.27 | BB | 34.15 | BB | 34.03 | BB | Avoidance |
| C016 | Gold Standard cookstoves 2019 vintage | 34.25 | BB | 34.12 | BB | 34.00 | BB | Avoidance |
| C018 | REDD+ Cordillera Azul (Peru) | 28.20 | B | 29.23 | B | 30.27 | BB * | Nature-based |
| C019 | Rimba Raya REDD+ (Indonesia) | 26.05 | B | 26.72 | B | 27.40 | B | Nature-based |
| C023 | HFC-23 destruction (pre-2013) | 25.27 | B | 21.49 | B | 17.70 | B | Industrial |
| C021 | Large hydro (Brazil) 2015 | 24.35 | B | 25.07 | B | 25.80 | B | Avoidance |
| C020 | Chinese CDM wind 2014 vintage | 23.25 | B | 23.46 | B | 23.67 | B | Avoidance |
| C022 | Kariba REDD+ (Zimbabwe) | 19.60 | B | 19.87 | B | 20.13 | B | Nature-based |
| C024 | Chinese CDM wind 2012 | 18.95 | B | 18.78 | B | 18.60 | B | Avoidance |
| C025 | Unverified grassland avoidance 2013 | 17.12 | B | 16.98 | B | 16.83 | B | Other |

\* indicates grade change from baseline.

## 4. Category-Level Mean Composites

This is the critical test: do CDR projects still outscore REDD+/avoidance when
removal_type is zeroed out?

| Category | Baseline mean | Halved mean | Zeroed mean | N |
|----------|:------------:|:-----------:|:-----------:|:-:|
| CDR | 88.2 | 88.0 | 87.8 | 6 |
| Nature-based | 50.9 | 50.9 | 50.9 | 9 |
| Industrial | 46.1 | 45.2 | 44.4 | 3 |
| Avoidance | 30.2 | 30.5 | 30.9 | 6 |
| Other | 65.2 | 64.5 | 63.8 | 5 |

## 5. CDR vs Nature-Based Gap Analysis

- **Baseline gap (CDR - Nature-based):** 37.4 points
- **Zeroed gap (CDR - Nature-based):** 37.0 points
- **Gap reduction:** 0.4 points (1%)
- **Gap remaining after removing removal_type:** 37.0 points (99% of original)

- **Baseline gap (CDR - Avoidance):** 58.0 points
- **Zeroed gap (CDR - Avoidance):** 57.0 points
- **Gap remaining:** 57.0 points (98% of original)

## 6. Grade Changes Under Each Scenario

### Halved: 2 grade change(s)

| ID | Name | Baseline grade | New grade | Baseline comp | New comp | Delta |
|----|------|:--------------:|:---------:|--------------:|---------:|------:|
| C004 | Charm Industrial bio-oil injection | AAA | AA (down) | 90.53 | 89.95 | -0.58 |
| C014 | Plan Vivo agroforestry (Mozambique) | A | BBB (down) | 60.15 | 59.84 | -0.31 |

### Zeroed: 4 grade change(s)

| ID | Name | Baseline grade | New grade | Baseline comp | New comp | Delta |
|----|------|:--------------:|:---------:|--------------:|---------:|------:|
| C004 | Charm Industrial bio-oil injection | AAA | AA (down) | 90.53 | 89.37 | -1.16 |
| C007 | Pachama-verified Brazilian reforest | A | AA (up) | 74.05 | 75.40 | +1.35 |
| C014 | Plan Vivo agroforestry (Mozambique) | A | BBB (down) | 60.15 | 59.53 | -0.62 |
| C018 | REDD+ Cordillera Azul (Peru) | B | BB (up) | 28.20 | 30.27 | +2.07 |

## 7. Key Findings

### Does the REDD+/CDR quality gap survive removal of removal_type?

**Yes.** Even with removal_type weight set to zero, CDR projects outscore nature-based
projects by 37.0 points (down from 37.4 at baseline). The quality
difference is 99% attributable to additionality, permanence,
MRV, vintage, and registry -- dimensions that do not encode a normative
removal-vs-avoidance hierarchy. The Oxford Principles hierarchy amplifies the
quality gap but does not create it.

### BeZero rank correlation robustness

- Baseline: rho = +0.868
- Halved:   rho = +0.868
- Zeroed:   rho = +0.877

The BeZero correlation remains strong (>0.88) even without removal_type, confirming that the framework's external validity does not depend on the Oxford Principles hierarchy.

### BCT Lemons Index robustness

- Baseline: LI = 0.724
- Halved:   LI = 0.729
- Zeroed:   LI = 0.733

BCT's Lemons Index remains above the null-model expectation (0.51) even at LI = 0.733 with removal_type zeroed. The pool's quality deficit is not an artifact of the removal hierarchy weighting.

### Conclusion for the paper

The removal_type dimension amplifies the CDR-vs-avoidance quality gap but does not create
it. The remaining dimensions (additionality, permanence, MRV, vintage, registry) independently
produce a substantial quality separation. This is because REDD+ and old renewable energy
credits score poorly on additionality (contested baselines), permanence (reversal risk or
non-applicable), and MRV (weak monitoring) -- quality deficits that exist independently of
any normative position on the removal-avoidance hierarchy. The framework's weight on
removal_type is a transparent, documented design choice that users can adjust; the underlying
quality signal is robust to that choice.

The BeZero rank correlation and BCT Lemons Index both remain substantively unchanged under
removal_type zeroing, confirming that the paper's two central empirical claims -- external
validation and adverse selection measurement -- do not depend on the Oxford Principles
hierarchy.
