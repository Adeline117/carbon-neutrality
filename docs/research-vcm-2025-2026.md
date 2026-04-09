# VCM 2025-2026 Literature Survey Findings

*Compiled 2026-04-08 via deep research agent. 15 new sources not currently cited in `docs/literature-review.md`.*

## Summary table

| # | Source | Area | Relationship |
|---|--------|------|-------------|
| 1 | Cabiyo & Field, PNAS Nexus 2025 | Overcrediting mechanisms | Extends (ex-post adjustment) |
| 2 | Coglianese & Giles, Science 2025 | Audit failure — 95 projects passed VVB but overstated | Supports (dMRV over VVBs) |
| 3 | Garcia & Sanford, PNAS 2026 | Jurisdictional REDD+ gaming — anticipatory deforestation | Extends (new risk vector) |
| 4 | West et al., GCB 2025 | REDD+ follow-up: "romanticized narratives" | Supports (data-driven assessment) |
| 5 | Fernandez Salguero, arXiv 2025 | Umbrella meta-review: <16% real reductions confirmed | Supports (structural quality gap) |
| 6 | Cheong, Anthropocene Science 2025 | Theoretical critique of carbon markets | Challenges (market premise) |
| 7 | Zeng et al., Nature Rev Biodiversity 2026 | Carbon-biodiversity tradeoffs — 3.7% habitat disturbance increase | Extends (safeguards dimension) |
| 8 | ICVCM CDR + cookstove approvals 2025-2026 | 6 CDR + 3 cookstove methodologies with conditions | Supports (CCP calibration) |
| 9 | Singapore NEA rating panel appointment | First sovereign use of BeZero/Calyx/Sylvera for compliance | Supports (regulatory validation) |
| 10 | Calyx "Quality indicators delivering" 2025 | CCP projects average A vs C for non-CCP on Calyx scale | Supports (CCP threshold design) |
| 11 | Verra DMRV pilot first credits 2026 | 80/20 buffer split for high-frequency issuance | Extends (buffer pattern) |
| 12 | Gold Standard + Hedera Guardian 2025 | First fully digital cookstove credits with IoT-SIM dMRV on-chain | Supports (architecture validation) |
| 13 | Bosshard et al., Frontiers in Blockchain 2025 | VCM network analysis — blockchain affiliation drives collaboration | Extends (ecosystem positioning) |
| 14 | Columbia CGEP, Article 6 operationalization 2025 | 90+ Art 6.2 agreements but only 1 ITMO transfer completed | Supports (regulatory convergence) |
| 15 | Calyx scale update + VM0050 cookstove coverage 2026 | AAA-D scale convergence; 1,074 ratings across 20 programs | Supports (scale + calibration) |

## Most impactful for our framework

### Coglianese & Giles (Science 2025) — "Auditors can't save carbon offsets"

95 offset projects that substantially overstated climate benefits ALL passed third-party audits. >80% of issued credits may not reflect real reductions despite VVB review. The conflict of interest (auditors selected/paid by developers) is structural.

**Impact on our framework:** Validates our heavy MRV weighting (20%) and the preference for dMRV over traditional VVBs. Strengthens the case for our decentralized rater design (docs/decentralized-rater-design.md) where attesters are NOT selected by the credit developer.

### Singapore NEA rating panel — sovereign regulatory adoption

Singapore appointed BeZero, Calyx, and Sylvera for Article 6 compliance quality assessment. Companies can offset up to 5% of taxable emissions using ICC-eligible credits.

**Impact on our framework:** First government to formally mandate commercial carbon credit ratings for compliance. Validates the entire concept of independent quality rating as regulatory infrastructure — exactly our thesis. Opens a regulatory pathway for on-chain transparent ratings.

### Zeng et al. (Nature Rev Biodiversity 2026) — carbon-biodiversity tradeoffs

Offset projects associated with 3.7% increase in habitat disturbance. Monoculture plantations optimized for carbon uptake reduce species diversity.

**Impact on our framework:** Strengthens the v0.4 safeguards-gate decision. Our `communityHarm` disqualifier should potentially also cover biodiversity harm, not just community opposition. The commercial_plantation_arr adjustment (v0.4.1) is partially validated by this finding — commercial plantations optimizing for carbon may harm biodiversity.

### Gold Standard + Hedera Guardian (2025) — fully digital cookstove credits on-chain

100% digital MRV via IoT-SIMs on all cookstove devices, issued on Gold Standard registry, publicly auditable on Hedera blockchain. Every credit independently viewable on-chain.

**Impact on our framework:** Closest real-world implementation to our vision of dMRV + on-chain traceability + registry integration. Validates our architecture direction. Demonstrates how MRV automation works in practice for cookstoves — should score highest in our MRV dimension.

## Full citations

1. Cabiyo, B. & Field, C.B. (2025). "Embracing imperfection: Carbon offset markets must learn to mitigate the risk of overcrediting." *PNAS Nexus*, 4(5), pgaf091. DOI: 10.1093/pnasnexus/pgaf091
2. Coglianese, C. & Giles, C. (2025). "Auditors can't save carbon offsets." *Science*, 389(6733). DOI: 10.1126/science.ady4864
3. Garcia, A. & Sanford, L. (2026). "On the potential for strategic behavior in jurisdictional REDD+." *PNAS*, 123(14). DOI: 10.1073/pnas.2531612123
4. West, T.A.P. et al. (2025). "Demystifying the Romanticized Narratives About Carbon Credits From Voluntary Forest Conservation." *Global Change Biology*, 31(10), e70527. DOI: 10.1111/gcb.70527
5. Fernandez Salguero, R.A. (2025). "Effectiveness of Carbon Pricing and Compensation Instruments: An Umbrella Review." *arXiv*, 2512.06887.
6. Cheong, B.C. (2025). "The Paradox and Fallacy of Global Carbon Credits." *Anthropocene Science*, 4, 72-83. DOI: 10.1007/s44177-025-00084-0
7. Zeng, Y. et al. (2026). "Limitations of carbon markets for biodiversity conservation." *Nature Reviews Biodiversity*. DOI: 10.1038/s44358-026-00150-4
8. ICVCM (2025-2026). CDR methodology approvals (6) + cookstove approvals (3, with conditions). icvcm.org
9. Singapore NEA (2025). Carbon Rating Panel: BeZero, Calyx, Sylvera for ICC Framework. nea.gov.sg
10. Calyx Global (2025). "Are carbon credit quality indicators delivering?" calyxglobal.com
11. Verra (2026). First DMRV pilot credits approved for high-frequency issuance. verra.org
12. Gold Standard & ATEC Global (2025). First fully digital cookstove credits on Hedera Guardian. goldstandard.org
13. Bosshard et al. (2025). "Blockchain-based voluntary carbon market: strategic insights into network structure." *Frontiers in Blockchain*, 8, 1603695.
14. Columbia CGEP (2025). Ahonen, P. et al. "How to Fully Operationalize Article 6." energypolicy.columbia.edu
15. Calyx Global (2026). New AAA-D scale + VM0050 cookstove ratings. calyxglobal.com
