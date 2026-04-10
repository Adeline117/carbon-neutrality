# Academic Survey: Carbon Credit Quality Frameworks (2022-2026)

*12 papers surveyed. Key finding: no published paper simultaneously proposes multi-dimensional weighted composite scoring at credit level with on-chain implementation, uncertainty quantification, and published IRR.*

## Our position in the literature

| Capability | CCQI v3.0 | Huber et al. | NUS SGFIN | FAIML 2025 | CATchain-R | PACT | **Ours** |
|---|---|---|---|---|---|---|---|
| Multi-dimensional scoring | ✅ 7 objectives | 15 criteria (taxonomy only) | 9 principles | ❌ | ❌ (org-level) | ❌ | **✅ 7 dims** |
| Credit-level (not methodology) | ❌ methodology | ❌ meta-analysis | ❌ program | ❌ | ❌ | ❌ | **✅** |
| Composite weighted score | ❌ separate | ❌ | threshold only | ❌ | single index | ❌ | **✅** |
| On-chain smart contract | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ Tezos | **✅ EVM** |
| Uncertainty (P(grade)) | ❌ | ❌ | ❌ | Monte Carlo (verification) | ❌ | ❌ | **✅** |
| Published IRR | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ κ=0.600** |
| Quality-gated pools | ❌ | ❌ | ❌ | ❌ | ❌ | attribute pools | **✅ meetsGrade()** |

**CCQI v3.0 is the closest precedent.** Same philosophy (open, transparent, 7 objectives), but operates at methodology level with 1-5 scale and no composite. We extend CCQI with credit-level granularity, 0-100 scoring, composite grades, on-chain enforcement, and empirical uncertainty.

## Papers to cite in the paper

| Paper | Why cite | Section |
|---|---|---|
| **Huber, Bach & Finkbeiner (2024)** — 15-criteria meta-analysis, J Environmental Management | Cross-check our 7 dims against their 15; their finding that only 2/15 are universal validates our focused approach | §2 or new Related Work |
| **NUS SGFIN (2024)** — 9-principle program evaluation | Program-level complement to our credit-level scoring; VCS meets only 6/9 at 60% threshold | §2 |
| **CCQI v3.0 (2024)** — updated from v2.0 we already cite | Most important direct comparison; should be explicit about what we extend beyond CCQI | §2.4 |
| **FAIML 2025** — AI verification with Monte Carlo uncertainty | Parallel uncertainty approach; their 18.5%→4.2% inter-verifier reduction parallels our IRR | §7.5 |
| **SBTi Evidence Synthesis (2024)** — will define corporate credit quality requirements | Our framework should demonstrate compatibility with SBTi Net-Zero Standard v2 | §8 |
| **Haya et al. (2024)** — VM0048 REDD+ quality assessment update | We cite BCTP 2023 but should add the 2024 follow-up on the updated methodology | References |

## MCDM weight elicitation methods found

| Method | Paper | Relevance |
|---|---|---|
| **IVSF-SWARA** | Nicholaus et al. 2024 | Alternative to AHP for expert weight calibration — lighter weight, handles uncertainty |
| **Fuzzy-DEMATEL** | Nguyen 2025 (already cited) | Inter-factor influence assessment |

These are candidates for v0.6 expert consultation weight elicitation if we move beyond simple questionnaire-based collection.
