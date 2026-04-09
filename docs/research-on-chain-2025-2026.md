# On-Chain Carbon Market Infrastructure: 2025-2026 Research Findings

*Compiled 2026-04-08 via deep research agent. Covers 12 findings relevant to the v0.5 framework deployment and integration strategy.*

## Priority findings for immediate action

### 1. Hypercerts + EAS Evaluator Registry (implementation reference for our EAS adapter)

The Hypercerts Foundation maintains a curated evaluator registry on EAS (Ethereum, Optimism, Base, Celo). Trusted evaluators publish structured attestations via EAS schemas; downstream consumers read those attestations. This is architecturally near-identical to our Option A2 design. The "Ecocerts" sub-project (collaboration with GainForest) builds EAS schemas specifically for ecological impact claims.

- **URL:** https://www.hypercerts.org/docs/developer/attestations
- **Schema reference:** https://github.com/hypercerts-org/ecocerts/issues/3
- **Action:** Study the Ecocerts schema design for our v0.5 EAS schema registration. Consider interoperability with Hypercerts evaluator registry.

### 2. Toucan CHAR Pool on Base — quality-gated pool with dynamic fees

Toucan's biochar-specific pool implements on-chain quality gating via a project allowlist (`checkEligible`). Also introduces a "pool health adjustment fee" penalizing over-concentration of any single project. Closest deployed analog to our `QualityGatedPool`, but uses binary allowlist not continuous rating.

- **Chain:** Base + Celo
- **Contract (Base):** `0x20b048fA035D5763685D695e66aDF62c5D9F5055`
- **GitHub:** https://github.com/ToucanProtocol/dynamic-fee-pools
- **Action:** Add as T015 in tokenized pilot. Study dynamic fee mechanism for v0.6 QualityGatedPool enhancement.

### 3. Klima Protocol 2.0 on Base — kVCM/K2 dual-token relaunch

KlimaDAO rebuilt as "Klima Protocol" with dual-token (kVCM + K2) architecture on Base. kVCM is burned to retire credits from protocol inventory. Migrated entirely from Polygon to Base.

- **Contract (kVCM on Base):** `0x00fbac94fec8d4089d3fe979f39454f48c71a65d`
- **Launch:** TGE October 2025, full activation February 2026
- **Action:** Priority integration target. Our CarbonCreditRating on Base + kVCM on Base = natural composability.

### 4. Verra + S&P Global Next-Generation Registry with Meta Registry

Verra partnered with S&P Global to rebuild its registry infrastructure using a "Meta Registry" on distributed ledger technology. Transaction-ready APIs replace manual processes. Effectively supersedes the 2022 "immobilization" framework that was never shipped.

- **URL:** https://press.spglobal.com/2025-08-21-Verra-and-S-P-Global
- **Timeline:** Phase 1 within 6 months of August 2025 announcement (≈ Q1 2026), Phase 2 in 2026
- **Action:** Monitor Phase 1 launch. Plan v0.5.1 integration path where a trusted attester reads from the Verra API and relays attestations on EAS.

### 5. Rainbow Standard — new CCP-Eligible CDR registry

France-headquartered CDR-focused registry covering biochar, enhanced rock weathering, BiCRS, biogas. Recently gained ICVCM CCP-Eligible status. 80+ projects, 400K+ credits. ~6% of durable CDR registry market.

- **URL:** https://rainbowstandard.io/
- **Action:** Add to EAS adapter allowlist candidates. Add a Rainbow biochar credit as T016 in tokenized pilot.

### 6. Carbonmark Direct — on-chain native issuance bypassing traditional registries

Allows project developers to issue carbon credits directly on-chain (Polygon) for novel methodologies not yet recognized by Verra/Gold Standard (Ocean Alkalinity Enhancement, enhanced rock weathering, DACCS, BECCS). Verified by third-party V&VBs. Issuance in 2-3 weeks vs months.

- **URL:** https://www.carbonmark.com/carbonmark-direct
- **Chain:** Polygon
- **Launch:** January 2025
- **Action:** High-priority integration. These credits need our quality signal most urgently — they bypass traditional registries so have no external quality assessment.

### 7. ICVCM CCP: 36 methodologies now approved

7 programs and 36 methodologies approved. ~101M credits eligible for CCP label. Gold Standard made CCP certification mandatory for new projects starting 2026.

- **URL:** https://icvcm.org/ccp-approved-methodologies/
- **Action:** Update `ccp_eligible` flags in credits.json. Cross-reference the 36 approved methodologies against our scoring rubric.

### 8. Microsoft/Carbon Direct CDR Criteria (5th edition, July 2025)

Covers 9 CDR pathways including marine CDR. Microsoft has contracted 22M+ tonnes of CDR. Most rigorous buyer-side quality framework in the market.

- **URL:** https://www.carbon-direct.com/press/2025-criteria-for-high-quality-cdr
- **Action:** Add to paper §2.5. Use as benchmark for validating our CDR scoring (T008, T009, T010).

### 9. Isometric Registry — 32% of durable CDR market, buyer-pays MRV model

MRV and issuance costs paid by the buyer (not the supplier), removing the conflict of interest that incentivizes over-crediting. Expanded methodology coverage to include biochar.

- **Action:** Update T008 metadata. Add a second Isometric entry (biochar). Reference buyer-pays model in EAS adapter design for attestation cost structure.

### 10. Open Forest Protocol + Kanop — dynamic baselines via AI satellite intelligence

OFP partnered with Kanop for continuously updated baselines based on real satellite data rather than static projections. Directly addresses West et al. 2023 baseline inflation problem. 280+ projects across 25+ countries.

- **URL:** https://www.openforestprotocol.org/blog/open-forest-protocol-and-kanop-unite
- **Action:** Update T012 scores and metadata to reflect Kanop partnership.

### 11. Senken Sustainability Integrity Index — AI-powered quality scoring competitor

AI-powered quality scoring analyzing 600+ data points per project. Filters for top 5% of projects. Acquired Ivy Protocol in April 2025. Proprietary — exactly the kind of opaque single-rater model our framework is designed to improve upon.

- **URL:** https://www.senken.io/
- **Action:** Add to paper §2.5 as emerging commercial rater. Consider for rank correlation if data becomes available.

### 12. GainForest Ecocerts/Bumicerts — live EAS-based ecological impact attestation

Environmental impact certificates built on Hypercerts using EAS attestations. AI + satellite data for verification. 46 projects between Feb-Nov 2025. Most directly relevant implementation reference for our v0.5 EAS adapter.

- **GitHub:** https://github.com/hypercerts-org/ecocerts
- **Action:** Study schema design for our EAS schema registration. Most valuable implementation reference.

## Key architectural conclusion

**No existing on-chain quality-gating mechanism does continuous-rating-threshold gating.** Toucan's CHAR pool (Finding 2) is the closest, using a binary project allowlist. Our `meetsGrade(creditToken, tokenId, minGrade)` pattern remains architecturally novel. The Base ecosystem (CHAR + Klima 2.0 + our framework) is the natural composability cluster.
