# Counterfactual Simulation: Quality Gating in Carbon Pools

What if historical on-chain carbon pools had applied quality gates?

## Summary: BBB Quality Gate Impact

| Pool | Baseline LI | Gated LI (BBB+) | LI improvement | Admitted | A+% |
|------|:-----------:|:---------------:|:--------------:|:--------:|:---:|
| Toucan BCT (historical peak, 2022) | 0.724 | 0.405 | +0.319 | 5% (2) | 0% |
| Toucan NCT (2023) | 0.602 | 0.390 | +0.211 | 36% (10) | 80% |
| Toucan CHAR (Base, 2025) | 0.221 | 0.221 | +0.000 | 100% (12) | 100% |
| Moss MCO2 (2022) | 0.713 | 0.391 | +0.323 | 7% (2) | 100% |
| Klima 2.0 kVCM inventory (Base, 2026) | 0.519 | 0.273 | +0.246 | 40% (8) | 100% |
| Hypothetical AAA-only pool | 0.100 | 0.100 | +0.000 | 100% (13) | 100% |

## Toucan BCT (historical peak, 2022)

Baseline: 43 credits, LI=0.724, mean composite=27.6, A+%=0%

| Threshold | Admitted | Mean composite | Lemons Index | LI improvement | A+% |
|:---------:|:--------:|:--------------:|:------------:|:--------------:|:---:|
| >= B | 43 (100%) | 27.6 | 0.724 | +0.000 | 0% |
| >= BB | 7 (16%) | 45.3 | 0.547 | +0.177 | 0% |
| >= BBB | 2 (5%) | 59.5 | 0.405 | +0.319 | 0% |
| >= A | 0 (0%) | - | - | - | - |
| >= AA | 0 (0%) | - | - | - | - |
| >= AAA | 0 (0%) | - | - | - | - |

## Toucan NCT (2023)

Baseline: 28 credits, LI=0.602, mean composite=39.9, A+%=29%

| Threshold | Admitted | Mean composite | Lemons Index | LI improvement | A+% |
|:---------:|:--------:|:--------------:|:------------:|:--------------:|:---:|
| >= B | 28 (100%) | 39.9 | 0.602 | +0.000 | 29% |
| >= BB | 10 (36%) | 61.0 | 0.390 | +0.211 | 80% |
| >= BBB | 10 (36%) | 61.0 | 0.390 | +0.211 | 80% |
| >= A | 8 (29%) | 61.5 | 0.385 | +0.216 | 100% |
| >= AA | 0 (0%) | - | - | - | - |
| >= AAA | 0 (0%) | - | - | - | - |

## Toucan CHAR (Base, 2025)

Baseline: 12 credits, LI=0.221, mean composite=77.9, A+%=100%

| Threshold | Admitted | Mean composite | Lemons Index | LI improvement | A+% |
|:---------:|:--------:|:--------------:|:------------:|:--------------:|:---:|
| >= B | 12 (100%) | 77.9 | 0.221 | +0.000 | 100% |
| >= BB | 12 (100%) | 77.9 | 0.221 | +0.000 | 100% |
| >= BBB | 12 (100%) | 77.9 | 0.221 | +0.000 | 100% |
| >= A | 12 (100%) | 77.9 | 0.221 | +0.000 | 100% |
| >= AA | 12 (100%) | 77.9 | 0.221 | +0.000 | 100% |
| >= AAA | 0 (0%) | - | - | - | - |

## Moss MCO2 (2022)

Baseline: 30 credits, LI=0.713, mean composite=28.7, A+%=7%

| Threshold | Admitted | Mean composite | Lemons Index | LI improvement | A+% |
|:---------:|:--------:|:--------------:|:------------:|:--------------:|:---:|
| >= B | 30 (100%) | 28.7 | 0.713 | +0.000 | 7% |
| >= BB | 2 (7%) | 61.0 | 0.391 | +0.323 | 100% |
| >= BBB | 2 (7%) | 61.0 | 0.391 | +0.323 | 100% |
| >= A | 2 (7%) | 61.0 | 0.391 | +0.323 | 100% |
| >= AA | 0 (0%) | - | - | - | - |
| >= AAA | 0 (0%) | - | - | - | - |

## Klima 2.0 kVCM inventory (Base, 2026)

Baseline: 20 credits, LI=0.519, mean composite=48.1, A+%=40%

| Threshold | Admitted | Mean composite | Lemons Index | LI improvement | A+% |
|:---------:|:--------:|:--------------:|:------------:|:--------------:|:---:|
| >= B | 20 (100%) | 48.1 | 0.519 | +0.000 | 40% |
| >= BB | 12 (60%) | 62.9 | 0.371 | +0.148 | 67% |
| >= BBB | 8 (40%) | 72.7 | 0.273 | +0.246 | 100% |
| >= A | 8 (40%) | 72.7 | 0.273 | +0.246 | 100% |
| >= AA | 4 (20%) | 81.9 | 0.181 | +0.337 | 100% |
| >= AAA | 1 (5%) | 92.4 | 0.076 | +0.443 | 100% |

## Hypothetical AAA-only pool

Baseline: 13 credits, LI=0.100, mean composite=90.0, A+%=100%

| Threshold | Admitted | Mean composite | Lemons Index | LI improvement | A+% |
|:---------:|:--------:|:--------------:|:------------:|:--------------:|:---:|
| >= B | 13 (100%) | 90.0 | 0.100 | +0.000 | 100% |
| >= BB | 13 (100%) | 90.0 | 0.100 | +0.000 | 100% |
| >= BBB | 13 (100%) | 90.0 | 0.100 | +0.000 | 100% |
| >= A | 13 (100%) | 90.0 | 0.100 | +0.000 | 100% |
| >= AA | 13 (100%) | 90.0 | 0.100 | +0.000 | 100% |
| >= AAA | 8 (62%) | 92.0 | 0.080 | +0.020 | 100% |

## BCT vs CHAR: Quality Gating Equivalence

- BCT baseline Lemons Index: 0.7238
- BCT with grade>=BBB gate: LI=0.4045, admission=0.0465, n=2
- CHAR (biochar-only allowlist): LI=0.2212
- Closest BCT gate to match CHAR: >= BBB (LI diff = 0.1833)

**Quality gating BCT at grade>=BBB would have produced LI=0.4045 vs CHAR's LI=0.2212. CHAR achieves comparable quality through its biochar-only allowlist rather than an explicit grade gate.**

## Key Findings

1. **BCT's Lemons Index drops dramatically** with even a modest BBB gate, because most of its credits are low-quality REDD+, old wind, and HFC-23.
2. **CHAR's allowlist achieves naturally** what a grade gate would enforce: by restricting to biochar projects with known high-quality profiles, it avoids adverse selection without needing an on-chain quality score.
3. **An on-chain meetsGrade() check** could replicate CHAR's quality profile for pools that accept diverse project types -- this is the core value proposition of the ERC-CCQR standard.
4. **The BBB threshold** is the minimum viable quality gate: it excludes the bulk of low-integrity credits while still admitting legitimate avoidance projects (cookstoves, landfill gas) with adequate verification.
