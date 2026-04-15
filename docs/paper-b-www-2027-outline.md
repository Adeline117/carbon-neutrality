# Paper B: WWW 2027 — Full Paper Outline

## ERC-CCQR: A Composable On-Chain Quality Rating Standard for Carbon Credit DeFi

*Target: The Web Conference (WWW) 2027, Full Paper*
*Track: Web and Society (primary) or Blockchain and Decentralized Systems (secondary)*
*Format: ACM double-column, 12 pages including references*
*Deadline: approximately October 2026*

---

## Abstract (250 words)

Tokenized carbon credit pools suffered catastrophic adverse selection: Toucan Protocol's Base Carbon Tonne (BCT) pool, which treated all post-2008 Verra credits as fungible, accumulated a Lemons Index of 0.724 — meaning the average credit quality was below 28/100 — because low-quality credit holders exploited the single-price pool while high-quality holders withheld supply. We present ERC-CCQR, a composable on-chain quality rating standard for carbon credits that prevents this failure mode. The standard's core primitive, `meetsGrade(address creditToken, uint256 tokenId, Grade minGrade) -> bool`, is a zero-gas view function that any DeFi protocol can call to gate deposits, retirements, or fee structures on a continuous quality threshold. The rating system scores credits across seven weighted dimensions (removal type 25%, additionality 20%, MRV 20%, permanence 17.5%, vintage 10%, safeguards-gate 0%, registry 7.5%) with distributional uncertainty propagation, producing six-tier grades (AAA-B) with posterior P(grade) stored on-chain as `compositeVarianceBps2`. We validate the standard against 318 credits, achieving: (i) a 1.99-grade empirical gap between ICVCM CCP-eligible and non-CCP credits; (ii) cross-type Spearman correlation of +0.906 vs. BeZero (n=9), exceeding inter-agency agreement of +0.009; (iii) LLM panel inter-rater reliability of Fleiss' kappa=0.600 (ICC=0.993); and (iv) a Lemons Index reduction from 0.724 (BCT) to 0.221 (quality-gated biochar pool). We demonstrate three composability patterns — quality-gated deposit pools, Klima Protocol retirement gates, and Toucan CHAR fee overlays — with gas costs of 26k (meetsGrade), 89k (setRating), and 112k (batch-4 setRating) on Base. The standard is implemented in Solidity with 14 Foundry tests, an EAS-based decentralized attestation adapter referencing the Hypercerts evaluator registry, and full open-source availability. To our knowledge, ERC-CCQR is the first on-chain standard to provide continuous quality gating with uncertainty quantification for any class of real-world asset tokens.

---

## 1. Introduction

**Page budget:** 1.0-1.2 pages
**Key technical contribution:** Frame the problem as a composability gap in DeFi infrastructure, not just a carbon market problem. Existing on-chain carbon protocols lack a callable quality primitive. ERC-CCQR fills this gap.

### 1.1 The quality composability gap in carbon DeFi

**Key points:**
- On-chain carbon market grew to $2B+ in value locked, but quality differentiation remained entirely off-chain (commercial raters: BeZero, Calyx, Sylvera, MSCI — all proprietary, no smart contract interface)
- Toucan BCT demonstrated that fungible pools without quality gates produce measurable adverse selection (Lemons Index 0.724)
- Toucan CHAR introduced binary allowlist gating (`checkEligible()`), but binary is insufficient for continuous quality gradients
- No existing standard provides a callable quality primitive analogous to ERC-20's `balanceOf()` or ERC-721's `ownerOf()` — a composable building block that any protocol can invoke
- Zhou et al. (2023) showed the NFT model (Nori NRT) preserves per-credit identity, but still lacks quality metadata

### 1.2 Contributions

Enumerate five concrete contributions:
1. **ERC-CCQR standard specification** — three compliance levels (meetsGrade, full Rating struct, EAS relay) for progressive adoption
2. **meetsGrade() composable primitive** — zero-gas view function that any DeFi protocol calls for quality gating, analogous to how ERC-20 `allowance()` enables composable spending
3. **Distributional on-chain scoring** — first real-world asset rating to store both composite score and variance on-chain (`compositeVarianceBps2`), enabling P(grade >= threshold) computation by downstream consumers
4. **Lemons Index** — quantitative metric for DeFi pool health that detects adverse selection, applied to real-world pool data (BCT, CHAR, NCT, MCO2)
5. **Empirical validation suite** — four independent validation studies (CCP calibration, commercial agency correlation, inter-rater reliability, adversarial testing) establishing the rating's accuracy and reproducibility

---

## 2. Background and Related Work

**Page budget:** 1.5-2.0 pages
**Key technical contribution:** Position ERC-CCQR against existing on-chain and off-chain quality infrastructure, establishing novelty.

### 2.1 On-chain carbon protocols

| Protocol | Chain | Quality mechanism | Limitation |
|----------|-------|-------------------|------------|
| Toucan BCT | Polygon | Vintage + methodology filter | No quality differentiation (Lemons Index 0.724) |
| Toucan CHAR | Base | Binary project allowlist (`checkEligible`) | Binary; no continuous gradient |
| Moss MCO2 | Ethereum/Polygon | Single-project pool | No cross-project quality comparison |
| Nori NRT | Polygon | NFT per credit (Zhou et al. 2023) | Per-credit identity but no quality metadata |
| Klima Protocol 2.0 | Base | kVCM/K2 dual-token | Treasury-level quality selection, no per-credit gate |
| Carbonmark Direct | Polygon | On-chain native issuance | No quality rating |
| Regen Network | Cosmos | Ecological credit attestation | Cosmos SDK, not EVM composable |

### 2.2 Off-chain quality frameworks

- **ICVCM CCP:** Binary pass/fail. 36 methodologies, ~101M eligible credits. 25% price premium. Not callable on-chain.
- **Commercial raters (BeZero, Calyx, Sylvera, MSCI):** Proprietary scores. Significant inter-agency disagreement (CMW 2023). No smart contract interfaces.
- **CCQI:** Open methodology, 1-5 scale, but methodology-level only (not credit-level). No on-chain implementation.
- **Renoster Mercury Rubric:** Open rubric, but off-chain and forestry-only.
- **Senken Sustainability Integrity Index:** AI-powered, 600+ data points, but proprietary and not callable.

### 2.3 On-chain quality and credibility systems

- **CATchain-R** (Gao & Liu, npj Climate Action 2026): Blockchain-based carbon registry with credibility index. Rates organizations, not individual credits. Applied to NYC transportation.
- **PACT** (Jaffer et al., IEEE ICBC 2024): Remote sensing + econometric baselines on Tezos. Attribute-preserving pools. No continuous quality threshold.
- **JPMorgan Kinexys** (2025): Registry-layer tokenization via API. Quality assessment not included in tokenization pipeline.
- **Hypercerts / Ecocerts** (2025): EAS-based evaluator registry on Optimism/Base/Celo. GainForest Ecocerts for ecological impact attestation. Closest architectural precedent to our EAS adapter but lacks quality scoring logic.

### 2.4 DeFi composability standards

- ERC-20 (`balanceOf`, `transfer`, `approve/transferFrom`): the composability template
- ERC-721 (`ownerOf`, `safeTransferFrom`): per-token identity
- ERC-4626 (tokenized vaults): standardized deposit/withdraw for yield
- **Gap:** No standard for querying a real-world quality attribute of a token. ERC-CCQR fills this gap.

### 2.5 Positioning table

| Capability | CATchain-R | PACT | Toucan CHAR | Hypercerts | **ERC-CCQR** |
|------------|------------|------|-------------|------------|--------------|
| Credit-level quality rating | No (org) | No | No (binary) | No (impact) | **Yes** |
| Continuous quality threshold | No | No | No (binary) | No | **Yes (meetsGrade)** |
| Uncertainty quantification | No | No | No | No | **Yes (P(grade))** |
| EVM composable | No | No (Tezos) | Yes | Yes | **Yes** |
| Published IRR | No | No | No | No | **Yes (kappa=0.600)** |
| DeFi pool integration | No | Attribute pools | Project allowlist | N/A | **Quality-gated deposit, retirement, fees** |

---

## 3. ERC-CCQR Standard Specification

**Page budget:** 2.0-2.5 pages
**Key technical contribution:** The standard itself — interface definitions, data structures, compliance levels, security properties.

### 3.1 Design principles

1. **Minimality:** Level 1 compliance requires only two functions (`meetsGrade`, `isStale`)
2. **Progressive disclosure:** Three compliance levels (boolean query, full struct, decentralized attestation)
3. **Zero-gas reads:** All query functions are `view` — protocols call them via `staticcall` at no gas cost
4. **Grade universality:** AAA-B enum maps to the letter-grade convention used by Moody's, S&P, BeZero, Sylvera, Calyx, MSCI
5. **Uncertainty as first-class citizen:** `compositeVarianceBps2` stored alongside `compositeBps` in the on-chain struct

### 3.2 Grade enum and interface definitions

```solidity
enum Grade { B, BB, BBB, A, AA, AAA }

// Level 1: Boolean quality query
interface ICCQR {
    function meetsGrade(address creditToken, uint256 tokenId, Grade minGrade)
        external view returns (bool);
    function isStale(address creditToken, uint256 tokenId)
        external view returns (bool);
}

// Level 2: Full rating struct
interface ICCQR_Extended is ICCQR {
    struct Rating {
        uint16 compositeBps;            // 0-10000
        uint32 compositeVarianceBps2;   // Variance in bps^2
        Grade nominalGrade;             // Before disqualifiers
        Grade finalGrade;               // After disqualifiers
        uint64 lastUpdatedAt;           // Unix seconds
        uint64 expiresAt;               // 0 = never
        uint16 methodologyVersion;      // e.g., 0x0600
        bytes32 evidenceHash;           // Off-chain attestation pointer
        address attestedBy;             // Rater address
    }
    function ratingOf(address creditToken, uint256 tokenId)
        external view returns (Rating memory);
}

// Level 3: Decentralized attestation relay
interface ICCQR_EAS is ICCQR_Extended {
    function relay(bytes32 attestationUid, address creditToken, uint256 tokenId)
        external;
}
```

### 3.3 Scoring methodology (on-chain)

- Seven dimensions encoded as `DimensionScores` struct (uint16[7] in basis points)
- Weight vector: [2500, 2000, 1750, 2000, 1000, 0, 750] (sums to 10000 bps)
- Composite: `sum(scores[i] * weights[i]) / 10000` computed in a single loop
- Variance: `sum(weights[i]^2 * stds[i]^2) / 10000^2` — linear propagation
- Grade assignment: AAA >= 9000, AA >= 7500, A >= 6000, BBB >= 4500, BB >= 3000, B < 3000
- Seven disqualifier flags with grade cap lattice (doubleCounting->B, failedVerification->B, humanRights->B, sanctionedRegistry->BB, noThirdParty->BBB, communityHarm->BBB, biodiversityHarm->BBB)

### 3.4 Staleness detection

- `isStale()` checks two conditions: (a) block.timestamp > expiresAt (time expiry), (b) rating.methodologyVersion != CURRENT_METHODOLOGY_VERSION (rubric outdated)
- `meetsGrade()` internally calls `isStale()` — returns false for stale ratings
- Ensures downstream consumers always read fresh data without explicit staleness checks

### 3.5 EAS adapter architecture

- Trusted-attester allowlist maintained by governance multisig
- `relay()` decodes EAS attestation, verifies: (a) schema match, (b) attester in allowlist, (c) not revoked, (d) not expired
- References Hypercerts evaluator registry pattern for allowlist management
- Enables decentralized multi-rater attestation without single-owner key

### 3.6 Security properties

- **Re-entrancy safety:** `meetsGrade()` and `ratingOf()` are view functions (no state mutation)
- **Disqualifier integrity:** `meetsGrade()` uses `finalGrade` (post-disqualifier), not `nominalGrade`
- **Checks-effects-interactions:** QualityGatedPool calls `meetsGrade()` before `transferFrom()`
- **Methodology version gating:** Ratings from outdated methodology versions are automatically stale
- **Attester trust boundary:** EAS adapter restricts attestation relay to allowlisted addresses

**Display item:**
- **Figure 1** — ERC-CCQR architecture diagram: three compliance levels as concentric layers. Level 1 (meetsGrade/isStale) at center, Level 2 (full Rating struct) wrapping it, Level 3 (EAS relay) as outer layer. Show DeFi protocol integration arrows (QualityGatedPool, KlimaRetirementGate, CHARQualityOverlay).

---

## 4. Composability Patterns

**Page budget:** 1.5-2.0 pages
**Key technical contribution:** Three concrete DeFi integration patterns demonstrating that meetsGrade() is a reusable building block.

### 4.1 Pattern 1: Quality-gated deposit pool (QualityGatedPool.sol)

```solidity
function deposit(address creditToken, uint256 tokenId) external {
    require(ratingContract.meetsGrade(creditToken, tokenId, minGrade),
            "Below minimum grade");
    // transfer credit into pool
}
```

- **Use case:** Replaces Toucan BCT's undifferentiated pool with tiered pools (AAA pool, AA pool, A pool)
- **Adverse selection prevention:** Low-quality credits cannot enter high-quality pools — the contract enforces the boundary
- **Gas overhead:** Single `staticcall` to meetsGrade() (~26k gas) added to deposit transaction
- **Comparison with CHAR:** CHAR uses `checkEligible()` binary allowlist; QualityGatedPool uses continuous threshold

### 4.2 Pattern 2: Retirement quality gate (KlimaRetirementGate.sol)

```solidity
function retire(address creditToken, uint256 tokenId, Grade minGrade) external {
    require(ratingContract.meetsGrade(creditToken, tokenId, minGrade),
            "Below retirement quality threshold");
    // burn credit from kVCM inventory
}
```

- **Use case:** Klima Protocol 2.0's kVCM retirement flow. Before burning a credit for retirement claims, verify it meets the buyer's quality requirement.
- **Compliance integration:** Corporate buyers can set minGrade = Grade.AA for SBTi-aligned claims, minGrade = Grade.A for general voluntary claims
- **Gas overhead:** Same 26k static call; no additional storage reads beyond the rating lookup

### 4.3 Pattern 3: Quality-based fee discount (CHARQualityOverlay.sol)

```solidity
function depositWithDiscount(address creditToken, uint256 tokenId) external {
    Rating memory r = ratingContract.ratingOf(creditToken, tokenId);
    uint256 fee = baseFee;
    if (r.finalGrade == Grade.AAA) fee = fee * 95 / 100;      // -5%
    else if (r.finalGrade == Grade.AA) fee = fee * 97 / 100;   // -3%
    else if (r.finalGrade == Grade.A)  fee = fee * 99 / 100;   // -1%
    // apply fee and transfer credit
}
```

- **Use case:** Augment Toucan CHAR's existing binary allowlist with continuous quality-based pricing incentives
- **Economic mechanism:** Higher-quality deposits receive lower fees, incentivizing quality supply
- **Gas overhead:** Single `staticcall` to ratingOf() (~30k gas) + fee computation (~5k gas)

### 4.4 Composability with existing Base ecosystem

All three patterns target Base, where both Toucan CHAR (`0x20b0...5055`) and Klima Protocol 2.0 (kVCM: `0x00fb...a65d`) are deployed. This is not coincidental — deploying on the same L2 enables atomic composability (single-transaction quality check + deposit/retirement).

**Display item:**
- **Figure 2** — Sequence diagrams for all three composability patterns: (a) QualityGatedPool deposit flow, (b) KlimaRetirementGate retire flow, (c) CHARQualityOverlay fee discount flow. Each showing the meetsGrade()/ratingOf() staticcall, the quality decision, and the subsequent token transfer.

---

## 5. Scoring Framework

**Page budget:** 1.0-1.5 pages
**Key technical contribution:** The multi-dimensional scoring methodology that produces the on-chain ratings. Shorter than Paper A's treatment because WWW cares more about the on-chain system than the rubric.

### 5.1 Seven weighted dimensions

| Dimension | Weight (bps) | Data source | On-chain feasibility |
|-----------|-------------|-------------|---------------------|
| Removal type hierarchy | 2500 | Methodology category mapping | High (lookup table) |
| Additionality | 2000 | Project financial analysis | Low (oracle/attestation) |
| MRV grade | 2000 | Verification reports, dMRV | Low (oracle/attestation) |
| Permanence | 1750 | Storage mechanism + duration | Medium (type-based defaults) |
| Vintage year | 1000 | Token metadata | High (on-chain native) |
| Co-benefits (safeguards-gate) | 0 | SDG certification | Gate only (communityHarm flag) |
| Registry & methodology | 750 | CCP-eligibility status | High (binary CCP lookup) |

### 5.2 Distributional scoring

- Standard deviations empirically calibrated from 3-model LLM panel IRR study (range: sigma = 4.0 to 11.1 per dimension)
- Composite variance: `Var(C) = sum(w_i^2 * sigma_i^2)` — stored as `compositeVarianceBps2`
- P(grade >= threshold) computable by any downstream consumer via: `P = 1 - Phi((threshold - compositeBps) / sqrt(compositeVarianceBps2))`
- First real-world asset rating standard with on-chain uncertainty quantification

### 5.3 Off-chain/on-chain scoring invariant

- Python scorer (`score.py`) and Solidity contract produce bit-identical results
- Test vector: Climeworks Orca = 9505 bps in both
- Composite variance: 83,706 bps^2 in both
- Invariant enforced by Foundry tests that compare expected values against Python outputs

**Display item:**
- **Table 1** — Complete weight vector and grade band definitions. Include the disqualifier cap lattice.

---

## 6. Evaluation

**Page budget:** 3.0-3.5 pages (largest section — this is the core of the WWW submission)
**Key technical contribution:** Five evaluation dimensions: gas benchmarks, scalability, quality accuracy, reproducibility, and adverse selection prevention.

### 6.1 Gas benchmarks

**Methodology:** Measured on Base Sepolia using Foundry's `forge test --gas-report`. All values in gas units (multiply by Base L2 gas price for USD cost).

| Operation | Gas (units) | USD estimate (Base L2, $0.001/unit) |
|-----------|------------|--------------------------------------|
| `setRating` (single credit) | ~89,000 | ~$0.089 |
| `meetsGrade` (view, staticcall) | ~26,000 | $0 (view function) |
| `ratingOf` (view, staticcall) | ~30,000 | $0 (view function) |
| `isStale` (view, staticcall) | ~8,000 | $0 (view function) |
| Batch `setRating` (4 credits) | ~112,000 | ~$0.112 |
| EAS `relay` (attestation) | ~150,000 | ~$0.150 |
| QualityGatedPool `deposit` (including meetsGrade) | ~95,000 | ~$0.095 |

**Key insight:** Read operations (meetsGrade, ratingOf) are free because they are view functions. The quality check adds zero marginal gas cost to any DeFi protocol that already performs token transfers. Write operations (setRating) cost less than $0.10 per credit on Base L2.

**Display item:**
- **Figure 3** — Gas cost breakdown: stacked bar chart comparing deposit-with-quality-gate vs. deposit-without for each composability pattern. The quality gate overhead should be visually minimal compared to the token transfer cost.

### 6.2 Scalability analysis

**Methodology:** Model storage growth and query performance as credit count scales from current (318) to target (1,000) to aspirational (100,000).

| Metric | 318 credits | 1,000 credits | 100,000 credits |
|--------|-------------|---------------|-----------------|
| On-chain storage (Rating structs) | ~50 KB | ~160 KB | ~16 MB |
| setRating throughput (per block) | Limited by block gas | ~50 per block | Requires batching across blocks |
| meetsGrade query time | O(1) mapping lookup | O(1) | O(1) |
| Full re-rating (methodology version bump) | ~28M gas | ~89M gas | Requires multi-tx migration |

**Key insight:** Read scalability is O(1) due to Solidity mapping architecture — meetsGrade() is constant-time regardless of total credits rated. Write scalability is the bottleneck; batch operations and methodology-version staleness (ratings become stale, not deleted) manage this gracefully.

### 6.3 Quality accuracy: CCP empirical calibration

- 318 credits classified by ICVCM CCP eligibility (165 CCP-eligible, 153 non-CCP)
- Mean composite gap: 1.99 grade levels
- Independently measured gap (Calyx Global 2025): ~2 grade levels (CCP average A vs. non-CCP average C)
- The framework recovers the ICVCM quality threshold without training on CCP labels — a form of external validity

**Display item:**
- **Figure 4** — CCP calibration: dual violin plot of composite score distributions (CCP-eligible vs. non-CCP), with grade bands as horizontal reference lines and the 1.99-grade gap annotated.

### 6.4 Quality accuracy: commercial agency rank correlation

- REDD+-specific (n=6, CMW 2023): mean pairwise Spearman vs. agencies = +0.343; inter-agency = +0.009
- Cross-type (n=9, CDR + biochar + cookstoves + IFM + methane + landfill + RE): Spearman vs. BeZero = +0.906, 5/9 exact matches
- Cross-type expansion (n=17, in progress): target for final submission
- Systematic divergence: cookstoves capped at BBB (avoidance-based per Oxford hierarchy) vs. agency ratings of A-AA

| Pair | Spearman rho (REDD+ n=6) | Spearman rho (cross-type n=9) |
|------|--------------------------|-------------------------------|
| Ours vs. BeZero | +0.664 | +0.906 |
| Ours vs. Sylvera | +0.566 | — |
| Ours vs. Calyx | -0.200 | — |
| BeZero vs. Calyx | -0.664 | — |
| Inter-agency mean | +0.009 | — |

### 6.5 Reproducibility: inter-rater reliability

- 3 LLM models (Claude Opus 4.6, Sonnet 4.6, Haiku 4.5), n=29 credits, v0.4.1 rubric
- Grade-level Fleiss' kappa = 0.600 ("substantial" per Landis & Koch 1977)
- Composite ICC(2,k) = 0.993 ("near-perfect" reliability)
- Author vs. panel: 86% exact grade agreement, 100% within +/-1 band
- Per-dimension kappa: permanence 0.684 (highest), additionality 0.519, MRV 0.487, removal_type 0.448, vintage 0.339, co-benefits 0.333, registry 0.168 (lowest, collapsed to 2-tier in v0.6)
- Disqualifier recall: 12/12 (100%) on 4 synthetic stress credits

**Key insight for WWW audience:** The rubric is reproducible by independent systems (LLMs as proxy for human raters). The per-dimension kappa breakdown provides a specific map for rubric refinement — standard software engineering practice of measuring test reliability by module.

**Display item:**
- **Figure 5** — Per-dimension kappa bar chart with Landis-Koch interpretation bands. Annotate registry_methodology as the v0.6 refinement target.

### 6.6 Adverse selection prevention: Lemons Index

**Definition:** `L(pool) = 1 - (mean composite score of pool credits / 100)`
- Range: 0 (all credits are perfect) to 1 (all credits score 0)
- Higher values indicate worse adverse selection
- Named after Akerlof's (1970) "Market for Lemons"

**Results:**

| Pool | Lemons Index | Quality gate | Interpretation |
|------|-------------|-------------|----------------|
| Toucan BCT | **0.724** | Vintage + methodology filter | Severe adverse selection; 60% of eligible credits grade B |
| Moss MCO2 | ~0.69 | Single-project | Similar to BCT |
| Toucan NCT | ~0.55 | Nature + vintage filter | Moderate improvement over BCT |
| Toucan CHAR | **0.221** | Binary biochar allowlist | Substantial improvement; biochar is inherently higher quality |
| Hypothetical Grade-A pool | ~0.15 | `meetsGrade(_, _, Grade.A)` | Near-elimination of adverse selection |
| Hypothetical Grade-AA pool | ~0.08 | `meetsGrade(_, _, Grade.AA)` | Minimal adverse selection |

**Key insight for WWW audience:** The Lemons Index is a measurable DeFi pool health metric. It connects Akerlof's economic theory to a concrete, computable number that pool operators and liquidity providers can monitor. A pool's Lemons Index should be published alongside TVL and APY as a third fundamental metric.

**Display item:**
- **Figure 6** — Lemons Index comparison across pool types: horizontal bar chart, sorted from worst (BCT) to best (Grade-AA hypothetical). Annotate the quality gate mechanism for each pool.

### 6.7 Adversarial testing

- 5 adversarial credits designed to exploit specific attack vectors:
  1. **Narrative washing:** High co-benefit scores masking low removal/permanence -> correctly capped by safeguards-gate
  2. **Double counting:** Duplicate credit across registries -> doubleCounting disqualifier fires, caps at B
  3. **Registry shopping:** Credit issued on unrecognized registry -> low registry score + noThirdParty disqualifier
  4. **Vintage arbitrage:** Ancient credit with inflated dimension scores -> vintage dimension pulls composite below threshold
  5. **Biodiversity destruction:** Monoculture plantation with high carbon removal -> biodiversityHarm disqualifier fires, caps at BBB
- All 5/5 correctly caught by both framework and independent LLM panel

---

## 7. Discussion

**Page budget:** 1.0-1.5 pages

### 7.1 ERC-CCQR as a general real-world asset rating standard

- The meetsGrade() pattern generalizes beyond carbon credits to any tokenized real-world asset requiring quality differentiation: biodiversity credits, water credits, renewable energy certificates
- The compositeVarianceBps2 field for uncertainty quantification is applicable to any rating where confidence matters (financial credit ratings, ESG scores)
- Design principle: quality metadata should be as composable as ownership metadata (ERC-721) or balance metadata (ERC-20)

### 7.2 Limitations

- **Oracle trust:** Rating accuracy depends on off-chain assessment quality. The "garbage in, garbage out" problem is not solved by on-chain transparency alone.
- **Single-provider LLM panel:** IRR study uses only Claude models. Multi-provider replication (GPT-5, Gemini, Llama) needed for generalizability.
- **Credit coverage:** 318 credits vs. commercial agencies' 4,400+. The framework is validated on accuracy and reproducibility, not coverage.
- **Weight calibration:** Not yet validated by domain expert panel (20 experts identified, consultation in progress).
- **Centralized rater bootstrapping:** V0.6 uses trusted-attester allowlist; true decentralization requires broader attestation ecosystem maturity.
- **Cookstove divergence:** Our Oxford-hierarchy-based scoring caps avoidance projects below A, diverging from commercial agencies. This is a normative design choice, not a bug, but limits comparability for avoidance-heavy portfolios.

### 7.3 Ethical considerations

- Framework embeds normative assumptions (removal > avoidance, co-benefits excluded from integrity composite)
- All assumptions are documented and configurable — users can modify weights by changing one JSON file
- The framework does not resolve the "offsets delay structural decarbonization" debate (Cheong 2025)
- Quality rating may inadvertently legitimate low-quality credits by grading them (rather than rejecting them entirely)

---

## 8. Related Work (Consolidated Positioning)

**Page budget:** 0.5-0.8 pages
**Purpose:** Formal related work section per ACM convention, more concise than Section 2 because the detailed positioning is already in Section 2.

### 8.1 Carbon credit quality assessment
- CCQI (EDF/WWF/Oeko-Institut): 7 objectives, methodology-level, 1-5 scale, no on-chain
- Huber et al. (2024): 15-criteria meta-analysis; only 2/15 are universal, validating our focused 7-dimension approach
- NUS SGFIN (2024): 9-principle program evaluation (VCS meets 6/9 at 60% threshold)
- Carbon Direct/Microsoft (2025): 6 CDR principles, 400+ evaluations; buyer-side quality framework

### 8.2 Blockchain-based environmental markets
- CATchain-R (Gao & Liu 2026): org-level credibility index, not credit-level quality rating
- PACT (Jaffer et al. 2024): attribute-preserving pools on Tezos, no continuous quality threshold
- Bosshard et al. (2025): network structure analysis of blockchain VCM; documents Toucan/Klima ecosystem
- Zhou et al. (2023): Nori NFT model — buyer clustering (87.9% experiential vs. 4% institutional driving 58.3% volume)

### 8.3 Adverse selection in information goods markets
- Akerlof (1970): original lemons model
- Manshadi et al. (2025): first formal VCM adverse selection model; certification noise threshold for market collapse
- Berg et al. (2025): empirical evidence of co-benefit mispricing

### 8.4 DeFi standards and composability
- ERC-20, ERC-721, ERC-4626: established composability patterns
- EAS (Ethereum Attestation Service): attestation infrastructure we build on
- Hypercerts + Ecocerts: closest architectural precedent for on-chain environmental attestation

---

## 9. Conclusion and Future Work

**Page budget:** 0.3-0.5 pages

### Conclusion
ERC-CCQR provides the first composable on-chain quality rating standard for carbon credits. The meetsGrade() primitive enables quality-gated pools that prevent the adverse selection that collapsed Toucan BCT (Lemons Index 0.724). The standard's distributional scoring with on-chain uncertainty quantification is, to our knowledge, unprecedented for any class of real-world asset tokens. Four validation studies — CCP calibration, commercial agency correlation, inter-rater reliability, and adversarial testing — establish the rating's accuracy, reproducibility, and robustness.

### Future work
1. **Expert-validated weight calibration** using structured elicitation with 20 identified domain experts
2. **Multi-provider LLM panel** replication for IRR generalizability
3. **Production deployment** on Base mainnet with Klima Protocol 2.0 and Toucan CHAR integration
4. **EAS schema registration** and trusted-attester onboarding (Verra, Gold Standard, Puro, Isometric)
5. **Generalization** of meetsGrade() pattern to biodiversity credits, water credits, and renewable energy certificates
6. **Dynamic re-rating** pipeline with dMRV input (Pachama satellite, Open Forest Protocol, Kanop AI)

---

## Figure and Table Plan (Complete)

| # | Type | Title | Section | Size |
|---|------|-------|---------|------|
| Fig 1 | Architecture diagram | ERC-CCQR standard: three compliance levels with DeFi integration arrows | 3 | 1 column |
| Fig 2 | Sequence diagrams | Three composability patterns: deposit gate, retirement gate, fee overlay | 4 | 2 columns |
| Fig 3 | Stacked bar chart | Gas cost breakdown: quality gate overhead vs. base transaction cost | 6.1 | 1 column |
| Fig 4 | Dual violin plot | CCP empirical calibration: CCP-eligible vs. non-CCP composite distributions | 6.3 | 1 column |
| Fig 5 | Bar chart | Per-dimension Fleiss' kappa with Landis-Koch interpretation bands | 6.5 | 1 column |
| Fig 6 | Horizontal bar chart | Lemons Index across pool types (BCT through hypothetical Grade-AA) | 6.6 | 1 column |
| Table 1 | Reference table | Weight vector, grade bands, disqualifier cap lattice | 5 | 1 column |
| Table 2 | Gas benchmarks | Full gas measurements for all operations | 6.1 | 1 column |
| Table 3 | Comparison matrix | ERC-CCQR vs. CATchain-R, PACT, CHAR, Hypercerts | 2.5 | 2 columns |
| Table 4 | Rank correlation | Spearman rho matrix (ours + 3 agencies) | 6.4 | 1 column |

---

## Related Work Positioning: Specific Differentiation Claims

| Compared system | Their approach | Our advantage | Their advantage |
|-----------------|---------------|---------------|-----------------|
| CATchain-R (Gao & Liu 2026) | Org-level credibility index | Credit-level granularity; multi-dimensional composite; DeFi composability | Transportation-sector domain specificity; NYC real-world deployment |
| PACT (Jaffer et al. 2024) | Attribute-preserving pools on Tezos | Continuous quality threshold (not just attribute matching); EVM composability; distributional scoring | Econometric baseline methodology; remote sensing integration |
| Toucan CHAR | Binary project allowlist | Continuous quality gradient; uncertainty quantification; fee-discount composability | Deployed in production; dynamic pool health adjustment fee |
| Zhou et al. (2023) | Nori NFT buyer behavior analysis | Quality metadata on each credit; DeFi pool integration | Empirical buyer segmentation; Granger causality analysis |
| Jirasek (2023) | KlimaDAO governance analysis | Quality gating prevents the adverse selection Jirasek documents | Governance structure analysis; whale concentration findings |
| Hypercerts/Ecocerts | EAS-based ecological attestation | Quality scoring logic (not just attestation); meetsGrade composable primitive | Broader ecological impact scope; production attestation infrastructure |
| CCQI v3.0 | 7-objective methodology-level scoring | Credit-level granularity; 0-100 vs 1-5; on-chain enforcement; distributional uncertainty; published IRR | Expert panel validation; regulatory credibility; broader methodology coverage |

---

## Artifact Submission Plan (ACM Artifact Evaluation)

### Artifact components

1. **Smart contracts** (Solidity, MIT license)
   - `contracts/CarbonCreditRating.sol` — Level 2 ICCQR reference implementation
   - `contracts/QualityGatedPool.sol` — Pattern 1: quality-gated deposit pool
   - `contracts/CarbonCreditRatingEASAdapter.sol` — Level 3 EAS relay
   - `contracts/examples/KlimaRetirementGate.sol` — Pattern 2: retirement gate
   - `contracts/examples/CHARQualityOverlay.sol` — Pattern 3: fee overlay
   - `contracts/ICarbonCreditRating.sol` — Interface definitions
   - `contracts/IEASMinimal.sol` — Minimal EAS interface
   - `contracts/MockCarbonCredit.sol` — Test helper (ERC-721)

2. **Test suite** (Foundry, 14+ tests)
   - Composite calculation correctness
   - Variance propagation correctness
   - Zero-std collapse
   - Variance sensitivity
   - Disqualifier cap enforcement (all 7 flags)
   - communityHarm safeguards-gate
   - Co-benefits-no-effect on composite (weight = 0)
   - Set-and-read roundtrip
   - Expiry rejection
   - Stale rating detection
   - Never-expires behavior
   - Re-rating freshness reset
   - Unrated-not-stale behavior
   - EAS relay correctness
   - Revocation rejection
   - Untrusted-attester rejection
   - Schema mismatch rejection
   - Attester count tracking

3. **Scoring engine** (Python 3.10+)
   - `data/pilot-scoring/score.py` — Python scorer (bit-identical to Solidity)
   - `data/pilot-scoring/sensitivity.py` — Weight perturbation and leave-one-out analysis
   - `data/rank-correlation/compute.py` — Spearman correlation computation
   - `data/llm-panel-irr/irr.py` — Fleiss' kappa and ICC computation

4. **Data** (JSON/CSV, MIT license)
   - `data/scoring-rubrics/` — Machine-readable rubric definitions (7 dimension JSON files + index.json)
   - `data/pilot-scoring/credits.json` — 29 illustrative + 4 synthetic + 5 adversarial credits with per-dimension scores
   - `data/tokenized-pilot/` — 16 real tokenized credit scores
   - `data/rank-correlation/` — Commercial agency comparison datasets
   - `data/llm-panel-irr/` — Raw LLM panel outputs (3 models x 29 credits x 7 dimensions)

5. **Deployment scripts**
   - `script/Deploy.s.sol` — Base Sepolia deployment
   - `script/SeedRatings.s.sol` — Seed initial ratings for demo

### Artifact badges targeted
- **Available:** GitHub repository, MIT license, DOI via Zenodo
- **Functional:** `forge test` runs all 14+ tests; `python3 score.py` reproduces all composite scores
- **Reproduced:** Independent reviewer can re-run gas benchmarks, IRR computation, Lemons Index

### Reproducibility instructions
```bash
# Clone and build
git clone https://github.com/Adeline117/carbon-neutrality.git
cd carbon-neutrality
forge install && forge build

# Run all Foundry tests
forge test -vvv

# Run gas benchmark
forge test --gas-report

# Reproduce Python scoring
cd data/pilot-scoring && python3 score.py

# Reproduce IRR computation
cd data/llm-panel-irr && python3 irr.py

# Reproduce Lemons Index
cd data/tokenized-pilot && python3 lemons_index.py

# Reproduce rank correlation
cd data/rank-correlation && python3 compute.py
```

---

## Page Budget Summary

| Section | Pages | Cumulative |
|---------|-------|------------|
| Abstract | 0.3 | 0.3 |
| 1. Introduction | 1.1 | 1.4 |
| 2. Background and Related Work | 1.8 | 3.2 |
| 3. ERC-CCQR Standard Specification | 2.2 | 5.4 |
| 4. Composability Patterns | 1.7 | 7.1 |
| 5. Scoring Framework | 1.2 | 8.3 |
| 6. Evaluation | 3.2 | 11.5 |
| 7. Discussion | 1.2 | 12.7 |
| 8. Related Work (consolidated) | 0.7 | 13.4 |
| 9. Conclusion | 0.4 | 13.8 |
| References | 1.2 | 15.0 |

**Note:** At 15 pages this exceeds the 12-page limit. Compression strategy:
- Merge Section 8 into Section 2 (save 0.7 pages) — position related work as subsection of background
- Compress Section 5 scoring methodology into Section 3 (save 0.5 pages) — the on-chain encoding IS the methodology
- Tighten Section 6 evaluation (move detailed tables to appendix/artifact) (save 1.0 page)
- Reduce Section 7 discussion (save 0.3 pages)
- Target: 12.0-12.5 pages after compression

---

## Reference List (Key Citations for WWW Audience)

### On-chain / blockchain systems (core for WWW)
1. Zhou et al. 2023 — Nori Web3 carbon market (IEEE Wireless Communications)
2. Gao & Liu 2026 — CATchain-R blockchain carbon registry (npj Climate Action)
3. Jaffer et al. 2024 — PACT carbon stablecoin (IEEE ICBC)
4. Jirasek 2023 — KlimaDAO analysis (Springer)
5. Frontiers in Blockchain 2024 — KlimaDAO tokenized credits
6. Bosshard et al. 2025 — Blockchain VCM network structure (Frontiers in Blockchain)
7. Finance and Space 2024 — Blockchain financialization of VCMs
8. JPMorgan Kinexys 2025 — Registry-layer tokenization
9. Toucan Protocol — BCT, CHAR contracts and documentation
10. Klima Protocol 2.0 — kVCM/K2 documentation
11. Hypercerts Foundation 2025 — EAS evaluator registry
12. GainForest Ecocerts — EAS ecological attestation schemas
13. Gold Standard + ATEC 2025 — Digital MRV on Hedera

### Carbon market quality (supporting domain context)
14. Akerlof 1970 — Market for Lemons
15. Calel et al. 2024 — <16% real reductions (Nature Communications)
16. Manshadi et al. 2025 — VCM adverse selection model
17. Berg et al. 2025 — Co-benefit mispricing
18. ICVCM 2023, 2025 — CCP framework
19. CMW 2023 — Inter-agency rating disagreement
20. CCQI 2024 — Open quality framework
21. Coglianese & Giles 2025 — Auditor failure (Science)
22. MSCI 2025 — Integrity premium
23. Trencher et al. 2024 — Corporate low-quality purchasing (Nature Communications)
24. Calyx Global 2025 — CCP correlation
25. Sylvera 2025 — State of Carbon Credits

### Technical methods
26. Landis & Koch 1977 — Kappa interpretation
27. Huber et al. 2024 — 15-criteria meta-analysis
28. NUS SGFIN 2024 — 9-principle evaluation
29. Allen et al. 2020 — Oxford Principles

### DeFi standards
30. ERC-20, ERC-721, ERC-4626 specifications
31. EAS (Ethereum Attestation Service) documentation

**Target: ~35-40 references** (tighter than Paper A; WWW emphasizes technical novelty over exhaustive citation)

---

## Submission Timeline

| Date | Milestone |
|------|-----------|
| April 2026 | Outline complete (this document) |
| May 2026 | Expert consultation responses integrated into weights |
| June 2026 | Multi-provider LLM panel replication completed |
| July 2026 | Base mainnet deployment with live composability demo |
| August 2026 | Gas benchmarks finalized on mainnet |
| September 2026 | Full draft complete; internal review |
| October 2026 | WWW 2027 submission (exact deadline TBD) |
| November 2026 | Artifact preparation and Zenodo archival |

---

## Key Differentiators for WWW Reviewers

1. **Novel DeFi primitive:** meetsGrade() is the first composable quality-gating function for real-world asset tokens, analogous to balanceOf() for fungible tokens
2. **Real adverse selection measured:** Lemons Index applied to an actual DeFi pool (Toucan BCT) with actual token data, not a simulation
3. **Uncertainty on-chain:** First token rating standard with distributional uncertainty stored in the contract state (compositeVarianceBps2)
4. **Full artifact:** 8 Solidity contracts, 14+ Foundry tests, Python scorer, IRR pipeline, all open-source and reproducible
5. **Cross-disciplinary validation:** Combines blockchain systems evaluation (gas, scalability) with information economics (Lemons Index, Spearman correlation) and psychometrics (Fleiss' kappa, ICC)
