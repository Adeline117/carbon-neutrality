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
  foundry.toml                       # Foundry config for contracts/
  .env.example                       # Base Sepolia deployment env template
  docs/
    workshop-paper.md                # Phase 1 workshop paper (v0.4.1)
    methodology-gate-v0.4.md         # A2 design note: scoring mechanism decision
    v0.4.1-changelog.md              # Guanaré commercial_plantation_arr patch
    decentralized-rater-design.md    # D design note: rater architecture comparison
    v0.4-executive-summary.md        # 2-page briefing for expert reviewers
    v0.5-weight-calibration-questionnaire.md  # Structured expert questionnaire
    v0.4.1-deployment-notes.md       # Base Sepolia addresses + key custody log
    announcement-v0.4.1.md           # Held public announcement draft
    demo/index.html                  # Vanilla HTML Base Sepolia demo (no wallet required)
    api/v0.4.1/                      # Snapshot of deployed contract state (GitHub Pages)
    dimension-definitions.md
    toucan-failure-analysis.md
    literature-review.md
  data/
    scoring-rubrics/                 # Machine-readable JSON rubrics (1 per dimension + index)
    pilot-scoring/                   # 29-credit illustrative pilot + Python scorer + sensitivity
    tokenized-pilot/                 # 14-credit real-tokenized pilot
    rank-correlation/                # BeZero/Calyx/Sylvera rank correlation study (n=6 REDD+)
    llm-panel-irr/                   # v0.5 LLM panel inter-rater reliability study
  contracts/
    ICarbonCreditRating.sol          # Interface + shared types (Rating struct with freshness)
    CarbonCreditRating.sol           # Reference rating contract (v0.4 safeguards-gate)
    QualityGatedPool.sol             # Example pool that rejects deposits below a minimum grade
    MockCarbonCredit.sol             # Minimal ERC-20 for Base Sepolia demo tokens
    test/
      CarbonCreditRating.t.sol       # Foundry tests (12 passing in v0.4)
  script/
    Deploy.s.sol                     # Deploy CarbonCreditRating + 2 QualityGatedPools
    SeedRatings.s.sol                # Seed 14 MockCarbonCredit + setRating from tokenized pilot
    seed/tokenized_pilot.json        # Regenerate with tools/regen_seed.py
    README.md                        # Deployment runbook
  tools/
    snapshot.py                      # Read deployed contract state -> docs/api/v0.4.1/ratings.json
    regen_seed.py                    # Regenerate script/seed/tokenized_pilot.json from data/
  .github/workflows/
    snapshot.yml                     # Daily cron refreshing the read API via GitHub Pages
```

## Status

**Exploratory** | Target: Late 2026

- **v0.4.1 (current):** Workshop paper with the safeguards-gate scoring mechanism. 3 engineered-CDR credits reach AAA (Orca, Heirloom, Charm). Illustrative pilot at 29 credits; tokenized pilot at 14 real on-chain credits; rank-correlation study against BeZero/Calyx/Sylvera on 6 REDD+ projects (mean Spearman +0.343 vs inter-agency +0.009 under v0.4.1). Expert consultation materials drafted. Base Sepolia deployment infrastructure ready (scripts + demo HTML + read-API snapshot tool); physical deployment pending a rater key and faucet ETH.
- **v0.5 (next):** LLM panel IRR study, distributional composite with per-dimension uncertainty propagation, gather expert feedback via the questionnaire, integrate into v0.5 methodology diff.

## Try it on Base Sepolia

> **PRELIMINARY AUTHOR ATTESTATIONS — NOT ENDORSED BY ANY REGISTRY, RATING AGENCY, OR REAL-WORLD CARBON MARKET PARTICIPANT.** The ratings below are author judgment applied to public documentation, for a Base Sepolia testnet demo. Any value derived from these grades is play money.

Once deployed (see `script/README.md` for the runbook), the framework offers three integration surfaces:

| Surface | URL / address |
|---------|---------------|
| Rating contract (`CarbonCreditRating`) | `0x0000000000000000000000000000000000000000` *(fill in after `forge script script/Deploy.s.sol`)* |
| Premium pool (`AA+` gated) | `0x0000000000000000000000000000000000000000` |
| Standard pool (`A+` gated) | `0x0000000000000000000000000000000000000000` |
| Read API (no RPC required) | `https://<user>.github.io/carbon-neutrality/api/v0.4.1/ratings.json` |
| Interactive demo (no wallet required) | `https://<user>.github.io/carbon-neutrality/demo/` |

A 14-credit seed dataset (Toucan BCT/NCT/Kariba, Moss MCO2, Nori NRT, Puro CDR, Heirloom DAC, Climeworks Orca, Charm Industrial, JPMorgan Kinexys, Open Forest Protocol, Regen Network, C3, Flowcarbon) is written on-chain as `MockCarbonCredit` ERC-20s. Pick any of them in the demo to see the seven dimension bars, composite, final grade, methodology version, expiry, and evidence hash — all fetched live from the deployed contract via a daily GitHub Action snapshot to GitHub Pages.

**Limitations of this deployment:**
1. Single-rater testnet key — not decentralized; see `docs/decentralized-rater-design.md` for the v0.5 plan
2. Author attestations only — no registry or agency endorsement
3. Base Sepolia — no economic value, no mainnet exposure
4. Scores are archetype judgment from public documentation — the `MockCarbonCredit` addresses are NOT the real Toucan/Moss/Nori tokens (those live on Polygon)

See `docs/v0.4.1-deployment-notes.md` for the MCC-* address table and `docs/announcement-v0.4.1.md` for the (held) public announcement text.

Consensus methodology (CCQI-style structured elicitation or formal Delphi) to be determined after initial expert feedback.

## License

MIT
