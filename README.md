# On-Chain Carbon Credit Quality Rating Framework

A standardized quality classification system for on-chain carbon credits, addressing the fundamental problem that plagued Toucan Protocol and similar tokenized carbon markets: the inability to distinguish low-quality from high-quality credits within pooled instruments.

## Problem Statement

Toucan Protocol's BCT (Base Carbon Tonne) pool collapsed in value because it mixed credits of vastly different quality into a single fungible token. Without on-chain quality differentiation, the market experienced adverse selection -- low-quality credits flooded the pool while high-quality credits were withheld, driving the effective quality (and price) toward zero.

This project develops a transparent, reproducible quality rating methodology that can be applied on-chain to enable:
- Quality-tiered carbon credit pools
- Price differentiation based on verifiable attributes
- Automated quality gating in DeFi protocols
- Buyer confidence through standardized assessment

## Rating Dimensions

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Removal Type Hierarchy | 20% | Removal > Avoidance > Reduction (Oxford Principles) |
| Additionality | 20% | Would the project have happened without carbon finance? |
| Permanence | 15% | Duration of carbon storage and reversal risk |
| MRV Grade | 15% | Monitoring, Reporting, and Verification quality |
| Vintage Year | 10% | Recency of emission reduction |
| Co-benefits | 10% | SDG alignment, community impact, biodiversity |
| Registry & Methodology | 10% | Verra VCS, Gold Standard, ACR, CAR methodology rigor |

## Rating Scale

| Grade | Score | Description |
|-------|-------|-------------|
| AAA | 90-100 | Premium: engineered removal, high permanence, rigorous MRV |
| AA | 75-89 | High quality: nature-based removal or strong avoidance with robust verification |
| A | 60-74 | Standard quality: meets ICVCM Core Carbon Principles |
| BBB | 45-59 | Acceptable: legacy methodology, adequate but not leading-edge verification |
| BB | 30-44 | Below standard: questionable additionality or weak MRV |
| B | < 30 | Low quality: significant integrity concerns |

## Approach

Rather than prescribing a single consensus method upfront, this project takes an iterative approach:

1. **Phase 1 -- Workshop Paper** (current): Define candidate dimensions, survey existing frameworks, propose initial weighting
2. **Phase 2 -- Expert Consultation**: Gather feedback from carbon market practitioners, registry experts, and blockchain developers
3. **Phase 3 -- Pilot Implementation**: Deploy rating logic as on-chain smart contract with sample credits
4. **Phase 4 -- Refinement**: Adjust weights and thresholds based on empirical testing and expert consensus

## Key References

- [ICVCM Core Carbon Principles (CCP)](https://icvcm.org/the-core-carbon-principles/) -- Global benchmark; 25% price premium for CCP-labelled credits
- [Oxford Principles for Net Zero Aligned Carbon Offsetting](https://www.ox.ac.uk/news/2020-09-29-oxford-launches-new-principles-net-zero-aligned-carbon-offsetting) -- Removal vs avoidance hierarchy
- [Verra VCS Program](https://verra.org/programs/verified-carbon-standard/) -- Dominant voluntary market registry
- [CCQI](https://carboncreditquality.org/) -- Open methodology by EDF/WWF/Oeko-Institut; 7 objectives, 1-5 scale
- [Sylvera](https://www.sylvera.com/) / [BeZero](https://bezerocarbon.com/) / [Calyx Global](https://calyxglobal.com/) -- Commercial rating agencies (significant inter-rater disagreement documented)
- [MSCI 2025 Integrity Report](https://www.msci.com/) -- High-integrity index at 4x low-integrity; <10% of projects rated AAA-A
- Zhou et al. (2023) -- Nori NFT-based carbon market analysis, buyer clustering, Granger causality
- [Manshadi et al. (2025)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5792202) -- Formal adverse selection model for VCM
- [CATchain-R (Cornell, 2026)](https://www.nature.com/articles/s44168-026-00342-w) -- Blockchain carbon registry with credibility index
- [PACT Stablecoin (Cambridge, 2024)](https://arxiv.org/abs/2403.14581) -- Attribute-preserving carbon tokens on Tezos

## Project Structure

```
carbon-neutrality/
  README.md                          # This file
  docs/
    workshop-paper.md                # Phase 1 workshop/short paper (v0.2)
    dimension-definitions.md         # Detailed scoring criteria per dimension
    toucan-failure-analysis.md       # What went wrong and lessons learned
    literature-review.md             # Comprehensive survey of 27+ papers/reports (2022-2026)
  contracts/
    (future) Solidity rating contracts
  data/
    scoring-rubrics/                 # Detailed rubrics for each dimension
```

## Status

**Exploratory** | Target: Late 2026

Starting with workshop paper and dimension definitions. Consensus methodology (Delphi or alternative) to be determined after initial expert feedback.

## License

MIT
