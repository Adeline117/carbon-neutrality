# ERC-CCQR: A Composable On-Chain Quality Rating Standard for Carbon Credit DeFi

**Abstract.** Tokenized carbon credit pools have suffered catastrophic adverse selection. Toucan Protocol's Base Carbon Tonne (BCT) pool, which treated all post-2008 Verra credits as fungible, accumulated a Lemons Index of 0.724, indicating that the average deposited credit scored below 28 out of 100, because low-quality credit holders exploited the single-price pool while high-quality holders withheld supply. We present ERC-CCQR, a composable on-chain quality rating standard for carbon credits that prevents this failure mode. The standard's core primitive, `meetsGrade(address creditToken, uint256 tokenId, Grade minGrade) -> bool`, is a zero-gas view function that any DeFi protocol can call to gate deposits, retirements, or fee structures by continuous quality threshold. The rating system scores credits across seven weighted dimensions (removal type 25%, additionality 20%, MRV 20%, permanence 17.5%, vintage 10%, registry 7.5%, safeguards-gate 0%) with distributional uncertainty propagation, producing six-tier letter grades (AAA through B) with posterior grade probability stored on-chain as `compositeVarianceBps2`. We validate the standard against 318 credits, achieving: (i) a 1.99-grade empirical gap between ICVCM CCP-eligible and non-CCP credits (Cohen's d = 1.80, p < 0.001); (ii) cross-type Spearman correlation of +0.901 versus BeZero (n = 27 projects, 12 project types, Kendall tau = +0.821, 52% exact grade match, 100% within plus or minus one grade), exceeding the inter-agency mean of +0.009; (iii) LLM panel inter-rater reliability of Fleiss' kappa = 0.600 with ICC(2,k) = 0.993; and (iv) counterfactual Lemons Index reduction from 0.724 (BCT) to 0.405 under a BBB quality gate. We demonstrate three composability patterns -- quality-gated deposit pools, retirement gates, and fee overlays -- with measured gas costs of 19,244 (meetsGrade view call), 167,720 (setRating cold write), and 30,308 (warm update) on Base L2. The standard is implemented in Solidity with 49 Foundry tests and an EAS-based decentralized attestation adapter. To our knowledge, ERC-CCQR is the first on-chain standard to provide continuous quality gating with uncertainty quantification for any class of real-world asset tokens.

---

## 1. Introduction

### 1.1 The Quality Composability Gap in Carbon DeFi

The on-chain carbon market grew to exceed two billion dollars in total value locked between 2021 and 2023, yet quality differentiation remained entirely off-chain. Commercial rating agencies -- BeZero Carbon, Sylvera, Calyx Global, and MSCI -- produce proprietary quality assessments with no smart contract interface, rendering their ratings invisible to the decentralized protocols that trade, pool, and retire carbon credits [1, 2, 3]. The result was predictable: adverse selection.

Toucan Protocol's BCT pool demonstrated this failure mode at scale. BCT accepted any Verra-registered credit with a post-2008 vintage and an approved methodology, treating all eligible credits as fungible tokens worth the same price. Holders of low-quality credits -- legacy HFC-23 destruction, unverified grassland avoidance, expired Chinese CDM wind -- deposited aggressively, while holders of high-quality engineered carbon dioxide removal withheld supply. At its peak composition in 2022, BCT's 43 constituent credits had a mean composite quality score of 27.6 out of 100. Not a single credit scored at grade A or above. The Lemons Index, a metric we introduce in this paper, quantifies this outcome at 0.724, where 1.0 represents a pool composed entirely of zero-quality credits [5, 9].

Toucan's subsequent CHAR pool on Base introduced binary allowlist gating via a `checkEligible()` function that restricts deposits to pre-approved biochar projects from the Puro.earth registry. While CHAR achieves a dramatically lower Lemons Index of 0.221, binary gating cannot express continuous quality gradients: a project is either eligible or not, with no distinction between a marginal pass and an exceptional one [6]. Klima Protocol 2.0 introduced kVCM and K2 dual-token structures with treasury-level quality selection, but still lacks a per-credit quality gate [7]. Zhou et al. demonstrated that the NFT model (Nori NRT) preserves per-credit identity on Polygon, enabling buyer clustering analysis, yet the model attaches no quality metadata to individual tokens [8].

No existing on-chain standard provides a callable quality primitive analogous to ERC-20's `balanceOf()` or ERC-721's `ownerOf()` -- a composable building block that any protocol can invoke to determine whether a credit meets a minimum quality threshold before accepting it. This is the gap ERC-CCQR fills.

### 1.2 Contributions

This paper makes five contributions:

1. **ERC-CCQR standard specification.** We define a three-level compliance hierarchy for on-chain carbon credit quality rating: Level 1 (boolean quality query via `meetsGrade` and `isStale`), Level 2 (full `Rating` struct with composite score, variance, and provenance metadata), and Level 3 (decentralized attestation relay via the Ethereum Attestation Service). The progressive-disclosure design ensures that protocols requiring only admission control need implement only two view functions, while protocols requiring distributional scoring or decentralized attestation can adopt higher compliance levels incrementally.

2. **The `meetsGrade()` composable primitive.** A zero-gas view function that encapsulates the grade lookup, staleness check, and threshold comparison in a single call, enabling any DeFi protocol to gate deposits, retirements, or fee structures on a continuous quality threshold via `staticcall`.

3. **Distributional on-chain scoring.** ERC-CCQR is, to our knowledge, the first real-world asset rating standard to store both a composite score and its variance on-chain (`compositeVarianceBps2`), enabling downstream consumers to compute P(grade >= threshold) via Gaussian CDF without additional oracle calls.

4. **The Lemons Index.** We introduce a quantitative metric for DeFi pool health that detects adverse selection, defined as L(pool) = 1 - (mean composite score / 100). We apply it to real pool compositions (BCT, NCT, MCO2, CHAR, kVCM) and to counterfactual quality-gated scenarios, establishing a measurable link between Akerlof's lemons theory [9] and on-chain carbon market outcomes.

5. **Empirical validation suite.** Four independent validation studies establish the rating's accuracy and reproducibility: CCP calibration against 318 credits (1.99-grade gap, Cohen's d = 1.80), commercial agency rank correlation (Spearman +0.901 vs. BeZero, n = 27 projects across 12 project types), LLM panel inter-rater reliability (Fleiss' kappa = 0.600, ICC = 0.993), and adversarial testing with 100% disqualifier recall on synthetic stress credits.

---

## 2. Background and Related Work

### 2.1 On-Chain Carbon Protocols

The first wave of on-chain carbon markets (2021--2023) focused on bridging off-chain registry credits onto EVM-compatible blockchains. Toucan Protocol bridged Verra credits to Polygon as TCO2 tokens, pooling them into fungible BCT and NCT pools [5]. Moss bridged Amazon conservation credits into the MCO2 token on Ethereum and Polygon [10]. Both treated quality as an implicit property of the pool's eligibility filter rather than an explicit, queryable attribute of individual credits.

[Table 3: Comparison of on-chain carbon protocols and their quality mechanisms. Columns: Protocol, Chain, Quality mechanism, Limitation. Rows: Toucan BCT (Polygon, vintage + methodology filter, no quality differentiation), Toucan CHAR (Base, binary project allowlist, no continuous gradient), Moss MCO2 (Ethereum/Polygon, single-project pool, no cross-project comparison), Nori NRT (Polygon, NFT per credit, no quality metadata), Klima Protocol 2.0 (Base, kVCM/K2 dual-token, no per-credit gate), Carbonmark Direct (Polygon, on-chain native issuance, no quality rating), Regen Network (Cosmos, ecological credit attestation, not EVM composable).]

The second wave (2024--2026) introduced more sophisticated mechanisms. Toucan's CHAR pool on Base uses a binary project allowlist (`checkEligible()`) restricting deposits to Puro-certified biochar projects. Klima Protocol 2.0 migrated to Base with kVCM and K2 tokens, applying treasury-level quality curation. Carbonmark launched direct on-chain credit issuance on Polygon. However, none of these protocols exposes a callable quality-query interface usable by arbitrary downstream contracts.

### 2.2 Off-Chain Quality Frameworks

The ICVCM Core Carbon Principles (CCP) framework represents the most authoritative off-chain quality signal. As of late 2025, five programs and 36 methodologies have been approved, covering approximately 101 million credits. CCP-labeled credits command a 25% price premium over unlabeled credits [11]. However, CCP provides binary classification (eligible or not) rather than continuous scoring, and the label is not queryable on-chain.

Commercial rating agencies have developed proprietary quality assessments. BeZero Carbon rates on an 8-point AAA-to-D scale emphasizing six risk factors; Sylvera uses a similar AAA-to-D scale with ML-based remote sensing; Calyx Global employs a three-level framework (program, methodology, project) with additive scoring; and MSCI assessed over 4,400 projects, finding fewer than 10% rated A or above [1, 2, 3, 12]. The Carbon Market Watch (CMW) 2023 comparison revealed significant inter-agency disagreement: the same Amazon REDD+ project received high marks from one agency and the lowest possible rating from another [13]. None of these agencies provides a smart contract interface.

The Carbon Credit Quality Initiative (CCQI), developed by the Environmental Defense Fund, WWF, and Oeko-Institut, offers an open methodology with seven quality objectives scored 1--5 by independent domain experts [14]. CCQI operates at the methodology level rather than the individual credit level and has no on-chain implementation. The Renoster Mercury Rubric provides an open rubric for forestry projects but is similarly off-chain and limited in scope [15].

### 2.3 On-Chain Quality and Credibility Systems

CATchain-R, proposed by Gao and Liu, introduces a blockchain-based carbon registry with a credibility index that compares organizations' carbon reduction goals versus achievements [16]. The system rates organizations, not individual credits, and was applied to New York City transportation systems. While architecturally innovative, the organizational focus precludes credit-level quality gating.

PACT, developed by Jaffer et al. at Cambridge, combines remote sensing with econometric baselines to produce comparable carbon assets on Tezos, with attribute-preserving pools that maintain co-benefit metadata [17]. PACT's attribute pools are a complementary approach to quality differentiation, but the system operates on Tezos rather than the EVM ecosystem where the largest carbon DeFi protocols are deployed, and it does not expose a continuous quality threshold.

JPMorgan's Kinexys platform (2025) introduced registry-layer tokenization via API, enabling credits to be tokenized at issuance rather than bridged after the fact [18]. While this solves provenance problems, quality assessment is not part of the tokenization pipeline.

The Hypercerts Foundation operates an EAS-based evaluator registry on Base, Optimism, and Celo. GainForest's Ecocerts sub-project uses EAS attestation schemas for ecological impact claims [19]. This is the closest architectural precedent to our EAS adapter, but the Hypercerts system provides attestation infrastructure without quality scoring logic.

### 2.4 Adverse Selection in Carbon Markets

Akerlof's original lemons model predicts that when buyers cannot distinguish quality, low-quality goods drive out high-quality goods [9]. Manshadi, Monachou, and Morgenstern developed the first formal adverse-selection model specific to voluntary carbon markets, proving that when certification noise exceeds a threshold, a market-for-lemons collapse occurs in which no trade is possible [20]. Berg et al. found empirically that credits from the least reliable technologies but with positive co-benefits are priced at twice the level of trusted industrial solutions, suggesting that buyers value narratives over integrity [21]. Trencher et al. documented that 87% of offsets purchased by the 20 largest corporate buyers carry high risk of not providing real or additional emission reductions [22].

### 2.5 DeFi Composability Standards

The ERC-20 standard's `balanceOf()`, `transfer()`, and `approve()/transferFrom()` functions established the paradigm for composable on-chain primitives: any protocol can query any token's balance and initiate transfers without bespoke integration [23]. ERC-721 extended this to non-fungible tokens with `ownerOf()` [24]. ERC-4626 standardized tokenized vault operations [25]. No standard currently exists for querying a real-world quality attribute of a token. ERC-CCQR fills this gap by providing `meetsGrade()` as a quality-query primitive analogous to `balanceOf()` as a balance-query primitive.

[Table 5: Positioning matrix comparing ERC-CCQR against related systems across six capabilities: credit-level quality rating, continuous quality threshold, uncertainty quantification, EVM composability, published IRR, and DeFi pool integration. Systems compared: CATchain-R, PACT, Toucan CHAR, Hypercerts, ERC-CCQR. ERC-CCQR is the only system achieving all six.]

---

## 3. ERC-CCQR Standard Specification

### 3.1 Design Principles

The standard is governed by five design principles:

**Minimality.** Level 1 compliance requires only two functions (`meetsGrade` and `isStale`), ensuring that the simplest integration path demands minimal implementation effort.

**Progressive disclosure.** Three compliance levels allow protocols to adopt the standard incrementally: Level 1 for boolean quality gating, Level 2 for distributional scoring and provenance tracking, and Level 3 for decentralized attestation via EAS.

**Zero-gas reads.** All query functions are declared `view`, meaning protocols invoke them via `staticcall` at zero marginal gas cost. Quality checks add no on-chain transaction cost to the consuming protocol.

**Grade universality.** The six-tier AAA-through-B grade enum maps directly to the letter-grade convention used by Moody's, S&P, BeZero, Sylvera, Calyx, and MSCI. A `Grade.AA` is immediately interpretable by market participants; a raw numeric threshold is not.

**Uncertainty as a first-class citizen.** The `compositeVarianceBps2` field stores the variance of the composite score alongside the point estimate, enabling downstream consumers to compute grade probabilities without additional oracle calls.

### 3.2 Grade Enum and Interface Definitions

The standard defines a six-tier quality grade ordered from lowest to highest:

```
enum Grade { B, BB, BBB, A, AA, AAA }
```

Grades are compared via `uint8` casting: `B = 0`, `BB = 1`, `BBB = 2`, `A = 3`, `AA = 4`, `AAA = 5`.

**Level 1 (Boolean Quality Query).** A protocol is Level 1 compliant if it implements two view functions:

```
function meetsGrade(address creditToken, uint256 tokenId,
    Grade minGrade) external view returns (bool);
function isStale(address creditToken, uint256 tokenId)
    external view returns (bool);
```

The `meetsGrade` function encapsulates the rating lookup, staleness check, and threshold comparison. It returns `false` for unrated credits, stale credits (expired or written under an outdated methodology version), and credits whose `finalGrade` falls below `minGrade`. The `isStale` function checks two conditions: (a) the current block timestamp exceeds the rating's `expiresAt` field (where 0 denotes no expiry), and (b) the rating's `methodologyVersion` is less than the contract's `CURRENT_METHODOLOGY_VERSION` constant. These two functions are sufficient for quality-gated pools and retirement gates.

**Level 2 (Full Rating Struct).** Level 2 adds the `ratingOf` function, which returns a complete `Rating` struct:

```
struct Rating {
    uint16 compositeBps;          // 0--10000 (basis points)
    uint32 compositeVarianceBps2; // Variance in bps^2 units
    Grade nominalGrade;           // Before disqualifier caps
    Grade finalGrade;             // After disqualifier caps
    uint64 lastUpdatedAt;         // Unix seconds
    uint64 expiresAt;             // 0 = never expires
    uint16 methodologyVersion;    // e.g., 0x0600 for v0.6
    bytes32 evidenceHash;         // Off-chain attestation pointer
    address attestedBy;           // Rater address
}
```

The struct stores per-dimension scores (`DimensionScores`), per-dimension standard deviations (`DimensionStds`), and disqualifier flags (`Disqualifiers`) alongside the derived composite, variance, and grades. The `compositeVarianceBps2` field enables downstream consumers to compute P(grade >= threshold) = 1 - Phi((threshold_bps - compositeBps) / sqrt(compositeVarianceBps2)), where Phi is the standard normal CDF [26].

**Level 3 (EAS Relay).** Level 3 adds decentralized attestation via the Ethereum Attestation Service [27]:

```
function relay(bytes32 attestationUid, address creditToken,
    uint256 tokenId) external;
```

The `relay` function pulls an EAS attestation, verifies (a) schema match against a registered schema UID, (b) the attester is in a trusted-attester allowlist, (c) the attestation is not revoked, and (d) the attestation has not expired. It then decodes the ABI-encoded dimension scores, standard deviations, and disqualifier flags and writes them to the rating contract. This design follows the Hypercerts evaluator registry pattern [19], enabling decentralized multi-rater attestation without a single-owner key.

[Figure 1: ERC-CCQR architecture diagram showing three compliance levels as concentric layers. Level 1 (meetsGrade/isStale) at center, Level 2 (full Rating struct with ratingOf) wrapping it, Level 3 (EAS relay with trusted-attester allowlist) as outer layer. Integration arrows from DeFi protocol consumers: QualityGatedPool, KlimaRetirementGate, CHARQualityOverlay.]

### 3.3 Scoring Methodology

Seven dimensions are encoded as a `DimensionScores` struct, each scored 0--100 by an authorized rater. The weight vector, expressed in basis points summing to 10,000, reflects the safeguards-gate design introduced in v0.4:

[Table 1: Complete weight vector, grade band definitions, and disqualifier cap lattice. Columns: Dimension, Weight (bps), Score range, Data source. Rows: Removal type (2500, 0-100, methodology category), Additionality (2000, 0-100, financial analysis), MRV grade (2000, 0-100, verification reports/dMRV), Permanence (1750, 0-100, storage mechanism + duration), Vintage year (1000, 0-100, token metadata), Co-benefits/safeguards-gate (0, 0-100, informational only -- communityHarm flag), Registry and methodology (750, 0-100, CCP eligibility). Grade bands: AAA >= 9000 bps, AA >= 7500, A >= 6000, BBB >= 4500, BB >= 3000, B < 3000. Disqualifier caps: doubleCounting -> B, failedVerification -> B, humanRights -> B, sanctionedRegistry -> BB, noThirdParty -> BBB, communityHarm -> BBB, biodiversityHarm -> BBB.]

The composite score is computed as:

composite_bps = sum(score_i * weight_i) / 100

where score_i is in [0, 100] and weight_i is in basis points. The computation executes in a single pass through the seven dimensions.

The composite variance is computed via linear propagation:

var(composite_bps) = sum(weight_i^2 * sigma_i^2) / 10000

where sigma_i is the per-dimension standard deviation, empirically calibrated from the LLM panel IRR study (range: 4.0 to 11.1 per dimension). This variance is stored as `compositeVarianceBps2`, a `uint32` field. The maximum possible value is bounded: 2500^2 * 50^2 * 7 / 10000 approximately equals 1.09 * 10^7, which fits within the uint32 range.

Seven disqualifier flags implement a grade cap lattice. Each flag, when set to `true`, caps the maximum achievable grade: `doubleCounting`, `failedVerification`, and `humanRights` cap at B; `sanctionedRegistry` caps at BB; `noThirdParty`, `communityHarm`, and `biodiversityHarm` cap at BBB. Disqualifiers never raise a grade; they only lower it. The `finalGrade` (post-disqualifier) is always used by `meetsGrade()`, ensuring that a credit with a high composite but an active disqualifier cannot bypass the safety gate.

### 3.4 Staleness Detection and Methodology Versioning

Ratings decay. A rating written under an outdated methodology version should not be used for quality gating, even if it has not expired. The `isStale()` function checks two conditions: time expiry (block.timestamp >= expiresAt, where expiresAt = 0 means never) and methodology version mismatch (rating.methodologyVersion < CURRENT_METHODOLOGY_VERSION). The `meetsGrade()` function calls `isStale()` internally, returning `false` for stale ratings. This ensures that consumers who rely solely on `meetsGrade()` are automatically protected against stale data.

When the methodology version is bumped (e.g., from v0.5 to v0.6), all existing ratings become stale without requiring deletion or migration. Credits must be re-rated under the new methodology to become active. This approach is gas-efficient: bumping a single constant in the contract invalidates all outdated ratings in O(1) time.

### 3.5 Security Properties

**Re-entrancy safety.** The `meetsGrade()` and `ratingOf()` functions are `view` functions that perform no state mutation, eliminating re-entrancy risk.

**Disqualifier integrity.** The `meetsGrade()` function compares against `finalGrade` (post-disqualifier), not `nominalGrade` (pre-disqualifier). A caller cannot bypass disqualifier caps by reading the nominal grade directly.

**Checks-effects-interactions.** The QualityGatedPool deposit pattern calls `meetsGrade()` before `transferFrom()`, conforming to the standard checks-effects-interactions pattern that prevents re-entrancy in the consuming contract.

**Methodology version gating.** Ratings from outdated methodology versions are automatically stale, preventing the use of legacy ratings that may not reflect current quality criteria.

**Attester trust boundary.** The EAS adapter restricts attestation relay to an allowlist of trusted attester addresses maintained by a governance multisig, preventing arbitrary accounts from writing ratings.

---

## 4. Composability Patterns

We demonstrate three concrete DeFi integration patterns showing that `meetsGrade()` functions as a reusable building block for on-chain carbon quality infrastructure. All three patterns target Base L2, where both Toucan CHAR (0x20b0...5055) and Klima Protocol 2.0 (kVCM: 0x00fb...a65d) are deployed, enabling atomic composability within single transactions.

### 4.1 Pattern 1: Quality-Gated Deposit Pool

The QualityGatedPool contract replaces Toucan BCT's undifferentiated pool with tiered quality pools. Before accepting a deposit, it calls `meetsGrade()`:

```
function deposit(address creditToken, uint256 tokenId)
    external {
    require(ratingContract.meetsGrade(
        creditToken, tokenId, minGrade),
        "Below minimum grade");
    // transfer credit into pool
}
```

An AAA pool sets `minGrade = Grade.AAA`; an AA pool sets `minGrade = Grade.AA`. The contract enforces the quality boundary: low-quality credits cannot enter high-quality pools. The gas overhead is a single `staticcall` to `meetsGrade()`, measured at approximately 19,244 gas. Compared to CHAR's binary `checkEligible()`, this pattern offers continuous quality gradients: a pool operator can set any of six grade thresholds, and the same interface serves all configurations.

### 4.2 Pattern 2: Retirement Quality Gate

The KlimaRetirementGate contract demonstrates how Klima Protocol 2.0's kVCM retirement flow could gate on quality. Before retiring a credit from inventory (burning the kVCM token to effect an off-chain retirement claim), the gate verifies that the credit meets a configurable minimum grade:

```
function checkRetirementEligibility(
    address creditToken, uint256 tokenId)
    external view returns (Grade) {
    if (ratings.isStale(creditToken, tokenId))
        revert StaleRating();
    if (!ratings.meetsGrade(
        creditToken, tokenId, minRetirementGrade))
        revert BelowRetirementGrade(...);
    return ratings.ratingOf(creditToken, tokenId)
        .finalGrade;
}
```

Corporate buyers can set `minRetirementGrade = Grade.AA` for SBTi-aligned claims or `minRetirementGrade = Grade.A` for general voluntary claims. The view-only pattern means no gas cost for the eligibility check itself. The `minRetirementGrade` is updatable by governance, enabling policy evolution without contract redeployment.

### 4.3 Pattern 3: Quality-Based Fee Discount

The CHARQualityOverlay contract augments Toucan CHAR's existing binary project allowlist with continuous quality-based pricing incentives. Even after a credit passes CHAR's `checkEligible()`, the overlay computes a fee discount based on the credit's grade:

```
function qualityFeeDiscount(
    address creditToken, uint256 tokenId)
    external view returns (uint16 discountBps) {
    Rating memory r = ratings.ratingOf(
        creditToken, tokenId);
    if (r.finalGrade == Grade.AAA) return 500; // 5%
    if (r.finalGrade == Grade.AA)  return 300; // 3%
    if (r.finalGrade == Grade.A)   return 100; // 1%
    return 0;
}
```

This creates a positive economic incentive: higher-quality deposits receive lower fees, attracting quality supply. CHAR's existing dynamic fee mechanism penalizes pool concentration; the quality discount is complementary, rewarding integrity. The overlay reads the full `Rating` struct via `ratingOf()`, incurring approximately 30,000 gas for the struct copy, plus approximately 5,000 gas for the fee computation.

### 4.4 EAS Attestation Relay

The CarbonCreditRatingEASAdapter enables decentralized rating by relaying EAS attestations from trusted attesters into the rating contract. The adapter maintains an allowlist of trusted attester addresses corresponding to carbon registries and independent assessors (e.g., Verra, Gold Standard, Puro, Isometric, ICVCM). Anyone can call `relay()` with an attestation UID; the adapter verifies provenance and decodes the attestation data:

The EAS schema encodes a complete rating as a single ABI-encoded tuple: seven dimension scores, seven standard deviations, seven disqualifier flags, an expiry timestamp, and an evidence hash. This schema is structurally compatible with the Hypercerts evaluator registry pattern, enabling potential cross-ecosystem integration in future versions [19].

[Figure 2: Sequence diagrams for three composability patterns: (a) QualityGatedPool deposit flow showing user -> pool -> meetsGrade staticcall -> rating contract -> bool response -> transferFrom; (b) KlimaRetirementGate retire flow showing buyer -> gate -> isStale + meetsGrade checks -> burn; (c) CHARQualityOverlay fee discount flow showing depositor -> CHAR checkEligible -> overlay qualityFeeDiscount -> ratingOf -> fee calculation.]

---

## 5. Scoring Framework

### 5.1 Seven Weighted Dimensions

The scoring framework evaluates carbon credits across seven dimensions, each scored 0--100 by an authorized rater. The weight vector reflects domain-prioritized calibration: removal type (25%) and additionality (20%) anchor the assessment on the two most consequential quality determinants. MRV grade (20%) reflects the empirical finding that third-party verification is structurally broken -- Coglianese and Giles found that 95 projects that substantially overstated climate benefits all passed VVB audits [28]. Permanence (17.5%) distinguishes durable storage (geological, mineralization) from reversible sequestration (forestry). Vintage year (10%) applies a decay function penalizing stale credits. Registry and methodology (7.5%) encodes CCP eligibility as a binary quality signal, reflecting the v0.6 collapse from a four-tier to a two-tier scheme (CCP-eligible: 75--85; non-CCP: 25--50) driven by the IRR finding that the original four tiers produced only slight inter-rater agreement (kappa = 0.168).

The co-benefits dimension carries zero weight in the composite. Its score is attested as an informational field and used exclusively to determine whether the `communityHarm` disqualifier flag should be set. This safeguards-gate design, introduced in v0.4, prevents narrative washing -- the strategy of inflating co-benefit scores to mask low removal and permanence scores [21].

### 5.2 Distributional Scoring and Uncertainty Quantification

No commercial carbon credit rating agency publishes grade uncertainty. ERC-CCQR stores both the composite score and its variance on-chain, enabling probabilistic grade computation by downstream consumers.

Per-dimension standard deviations are empirically calibrated from the three-model LLM panel IRR study. The mean absolute score differences across raters ranged from 4.51 (permanence, highest agreement) to 12.57 (registry/methodology, lowest agreement). The composite variance is propagated via the standard formula for the variance of a weighted linear combination:

Var(C) = sum(w_i^2 * sigma_i^2)

where w_i are the weights in basis points and sigma_i are the per-dimension standard deviations in the same 0--100 units as the scores. The result is stored as `compositeVarianceBps2`. Any downstream consumer can compute P(grade >= threshold) = 1 - Phi((threshold_bps - compositeBps) / sqrt(compositeVarianceBps2)), where Phi denotes the standard normal CDF.

### 5.3 Off-Chain/On-Chain Scoring Invariant

The Python scoring engine (`score.py`) and the Solidity contract produce bit-identical results. The test vector Climeworks Orca yields a composite of 9505 bps and a composite variance of 83,706 bps^2 in both implementations. This invariant is enforced by Foundry tests that compare expected values computed by the Python scorer against the Solidity contract's `computeComposite()` and `computeCompositeVariance()` outputs.

---

## 6. Evaluation

### 6.1 Gas Benchmarks

All gas measurements were obtained on Base Sepolia using Foundry's `forge test --gas-report`.

[Table 2: Gas benchmarks for all ERC-CCQR operations (measured via `forge test --gas-report`, Foundry 2025). Columns: Operation, Measured Gas, Notes. Rows: setRating (single credit, cold) 167,720 (7 dimension scores + 7 stds + 7 flags + metadata in fresh slots); setRating (warm update) 30,308 (SSTORE nonzero-to-nonzero); meetsGrade (view) 19,244 (one SLOAD mapping read + staleness check + enum compare); ratingOf (view) 20,823 (full struct copy to memory); isStale (view) 19,057 (SLOAD + timestamp compare); isStale (unrated) 7,097 (early return); EAS relay (happy path) 250,086 (getAttestation + decode + setRating); QualityGatedPool deposit 57,000--162,000 (meetsGrade + transferFrom).]

The read operations (`meetsGrade`, `ratingOf`, `isStale`) are free because they are `view` functions executed via `staticcall`. The quality check adds zero marginal gas cost to any DeFi protocol that already performs token transfers. Write operations (`setRating`) cost less than $0.10 per credit on Base L2 at current gas prices.

To contextualize these costs: a `meetsGrade()` call at 19,244 gas adds approximately 30--40% to an ERC-20 `transfer()` (~45,000--65,000 gas) as an external call, or approximately 25% inline. It adds approximately 10--15% to a Uniswap V3 swap (~130,000--185,000 gas), and approximately 8--10% to an Aave V3 `supply()` (~180,000--250,000 gas). For a carbon retirement transaction, which typically involves a swap and a burn, the quality gate remains a small fraction of total gas.

[Figure 3: Gas cost breakdown as stacked bar chart comparing deposit-with-quality-gate versus deposit-without for each composability pattern. The quality gate overhead (meetsGrade ~19k gas) is visually small compared to the base transaction costs (ERC-20 transfer ~65k, Uniswap swap ~185k, Aave supply ~250k).]

### 6.2 Scalability Analysis

Read scalability is O(1) due to Solidity's mapping-based storage architecture. The `meetsGrade()` function performs a constant-time `keccak256` hash of `(creditToken, tokenId)` followed by a single `SLOAD`, regardless of the total number of credits rated. Foundry tests confirm identical gas costs for `meetsGrade()` after 100, 500, and 1,000 pre-existing ratings.

Write scalability is the bottleneck. A full re-rating of 318 credits requires approximately 53 million gas (318 * 167,720 for cold writes); scaling to 1,000 credits requires approximately 168 million gas, achievable within a few blocks on Base. At 100,000 credits, batch operations spread across multiple transactions are required. The methodology-version staleness mechanism manages this gracefully: when the methodology is bumped, all outdated ratings become stale without requiring deletion, and re-rating can proceed incrementally.

### 6.3 CCP Empirical Calibration

The 318-credit batch dataset was partitioned by ICVCM CCP eligibility status: 165 credits using CCP-approved methodologies from CCP-eligible programs, and 153 non-CCP credits. The framework was not trained on CCP labels; rather, the CCP classification serves as an external validation signal.

The mean grade of CCP-eligible credits is 2.69 on the ordinal scale (B = 0 through AAA = 5), with a modal grade of BBB and 46% of credits at grade A or above. The mean grade of non-CCP credits is 0.70, with a modal grade of B and only 8% at A or above. The gap is 1.99 grade levels. Cohen's d with pooled standard deviation is 1.80 (95% bootstrap CI: [1.50, 2.16]), classified as a large effect size by conventional standards. The Mann-Whitney U test yields p < 0.001 (z = 13.06). The common-language effect size (CLES) is 0.914, meaning a randomly chosen CCP credit has a 91.4% probability of outscoring a randomly chosen non-CCP credit.

Calyx Global (2025) independently reported that CCP-eligible projects average approximately an A rating versus C for non-CCP projects -- a gap of approximately two grade levels on their scale [30]. Our 1.99-grade gap is consistent with this independent measurement, providing external validation of the framework's weight calibration without expert input.

[Figure 4: Dual violin plot of composite score distributions for CCP-eligible (n = 165) versus non-CCP (n = 153) credits, with grade band boundaries as horizontal reference lines (AAA >= 90, AA >= 75, A >= 60, BBB >= 45, BB >= 30, B < 30). The 1.99-grade gap is annotated. No CCP credit scores below BB; no non-CCP credit scores at AAA.]

### 6.4 Commercial Agency Rank Correlation

**REDD+ overlap (n = 6).** Using the six REDD+ projects with public ratings from BeZero, Calyx Global, and Sylvera documented in Carbon Market Watch (2023) Table 20 [13], we computed pairwise Spearman rank correlations. The mean inter-agency Spearman is +0.009, reflecting near-zero agreement. Our framework's mean correlation with the three agencies is +0.343, exceeding the inter-agency baseline by +0.334.

[Table 4: Spearman rank correlation matrix across raters. Columns: Pair, Spearman rho (REDD+ n=6), Spearman rho (cross-type n=27). Rows: Ours vs. BeZero (+0.664, +0.901), Ours vs. Sylvera (+0.566, --), Ours vs. Calyx (-0.200, --), BeZero vs. Calyx (-0.664, --), BeZero vs. Sylvera (+0.125, --), Calyx vs. Sylvera (+0.566, --), Inter-agency mean (+0.009, --), Our-vs-agency mean (+0.343, --).]

**Cross-type expansion (n = 27).** To test whether the near-zero REDD+ inter-agency agreement is project-type-specific, we extended the study to 27 projects spanning 12 project types (REDD+, DACCS, biochar, cookstoves, methane abatement, ODS destruction, enhanced weathering, J-REDD+, IFM, landfill gas, renewable energy, and ARR), using publicly available BeZero ratings. The overall Spearman versus BeZero is +0.901 (Kendall tau = +0.821), with 52% exact grade match and 100% within plus or minus one grade.

**Full dataset (n = 27).** The Spearman correlation versus BeZero across all 27 projects is +0.901 (Kendall tau = +0.821, permutation p < 0.001), with 52% exact grade match and 100% within plus or minus one grade across 12 project types.

One systematic divergence persists: cookstove projects. Our framework caps avoidance-based projects at grade BBB per the Oxford Principles hierarchy [29], which prioritizes removal over avoidance. Commercial agencies rate several cookstove projects at A or above. This is a normative design choice reflecting the framework's removal-first philosophy, not an error.

### 6.5 Inter-Rater Reliability

Three Claude-family LLM raters (Opus 4.6, Sonnet 4.6, Haiku 4.5) independently scored all 29 credits (25 real archetypes plus 4 synthetic disqualifier stress tests) using the v0.4.1 rubric with author scores redacted. Per-dimension scores were scored 0--100; composites and grades were computed deterministically by the Python scorer, measuring rubric-interpretation agreement rather than arithmetic agreement.

Grade-level Fleiss' kappa across the three raters is +0.600, at the boundary between moderate and substantial agreement per Landis and Koch [32]. The composite ICC(2,k) is +0.993, indicating near-perfect reliability on the continuous score. The gap between kappa and ICC is informative: small per-dimension disagreements cancel when linearly combined into the composite, consistent with the design in which the composite is a weighted mean of noisy inputs.

Author versus panel median agreement is 86% (25/29 exact grade match) and 100% within plus or minus one grade band. Every discrepancy is a single-band adjacent call; no multi-band gaps were observed.

Per-dimension Fleiss' kappa varies substantially: permanence (+0.684, substantial), removal type (+0.585, moderate-to-substantial), additionality (+0.243, fair), MRV (+0.248, fair), vintage (+0.324, fair), co-benefits (+0.182, slight), and registry/methodology (+0.168, slight). The two highest-reliability dimensions -- permanence and removal type -- are precisely the dimensions that carry the highest weights (17.5% and 25%, respectively), providing confidence that the framework's headline findings are supported by its most reproducible components.

The weakest dimension, registry/methodology (kappa = 0.168), motivated the v0.6 collapse from four tiers to two tiers (CCP-eligible versus non-CCP-eligible), reducing the scoring space from approximately 1,920 to approximately 40 outcomes.

[Figure 5: Per-dimension Fleiss' kappa bar chart with Landis-Koch interpretation bands (slight < 0.21, fair < 0.41, moderate < 0.61, substantial < 0.81, near-perfect). Bars ordered by kappa: permanence (0.684), removal_type (0.585), vintage (0.324), MRV (0.248), additionality (0.243), co_benefits (0.182), registry (0.168). Registry annotated as v0.6 refinement target.]

Pairwise Cohen's kappa between all rater pairs ranged from +0.500 (Sonnet vs. Haiku, the weakest pair) to +0.742 (Author vs. Opus, the strongest pair). All six pairs achieved 100% within-plus-or-minus-one-band agreement, demonstrating that the rubric produces reproducible ordinal rankings even when the exact grade is disputed.

Disqualifier recall on four synthetic stress credits (C026--C029), each designed with AA-tier technical scores but a single active disqualifier, was 12/12 (100%): all three raters correctly identified all four disqualifiers. This validates the unambiguous specification of the disqualifier criteria.

### 6.6 Adverse Selection Prevention: Lemons Index

We define the Lemons Index as:

L(pool) = 1 - (mean composite score of pool credits / 100)

The metric ranges from 0 (all credits are perfect quality) to 1 (all credits score zero). Higher values indicate more severe adverse selection. The name references Akerlof's "Market for Lemons" [9].

[Figure 6: Lemons Index comparison across pool types as horizontal bar chart, sorted from worst to best: Toucan BCT (0.724), Moss MCO2 (0.713), Toucan NCT (0.601), Klima kVCM (0.519), Toucan CHAR (0.221), Hypothetical AAA-only pool (0.100). Each bar annotated with the pool's quality gate mechanism.]

BCT's Lemons Index of 0.724 (n = 43 credits, mean composite = 27.6) confirms extreme adverse selection: 60% of eligible credits scored at grade B, and not a single credit reached grade A. Moss MCO2's Lemons Index of 0.713 (n = 30, mean composite = 28.7) is comparable. Toucan NCT, with a nature-focused and vintage filter, achieves a moderate improvement at 0.601 (n = 28, mean composite = 39.9, 28.6% at grade A or above). Klima 2.0's kVCM inventory scores 0.519 (n = 20, mean composite = 48.1, 40% at A or above).

CHAR's Lemons Index of 0.221 (n = 12, mean composite = 77.9, 100% at grade A or above) demonstrates that project-type-specific allowlisting effectively prevents quality degradation. A hypothetical AAA-only pool achieves 0.100 (n = 13, mean composite = 90.0), representing the practical floor -- even pure engineered CDR does not reach LI = 0 because vintage variation and per-project adjustments reduce composites below 100.

The Lemons Index should be published alongside TVL and APY as a third fundamental metric for DeFi pool health. A pool's LI provides a single number that liquidity providers and buyers can monitor to detect quality degradation before it becomes catastrophic.

### 6.7 Counterfactual Quality Gating

To quantify the value of on-chain quality gating, we simulate what would have happened if historical pools had applied a `meetsGrade()` check at various thresholds.

Under a BBB quality gate (`meetsGrade(_, _, Grade.BBB)`), BCT's Lemons Index would drop from 0.724 to 0.405 -- a modelled reduction of 0.319. Only 2 of 43 credits (5%) would have been admitted. The result is dramatic but also illustrates a tradeoff: strict quality gating severely limits pool liquidity. NCT's Lemons Index would drop from 0.601 to 0.390, admitting 10 of 28 credits (36%). Klima kVCM would drop from 0.519 to 0.273, admitting 8 of 20 credits (40%).

CHAR's Lemons Index is unchanged under any gate up to AA (0.221), because all 12 of its constituent biochar credits already score at grade A or above. This confirms that CHAR's project-type allowlist achieves naturally what a quality gate would enforce.

The core value proposition of ERC-CCQR is that `meetsGrade()` can replicate CHAR's quality profile for pools that accept diverse project types. A pool operator who sets `minGrade = Grade.A` would achieve adverse selection prevention comparable to CHAR's biochar-only allowlist while remaining open to high-quality CDR, biochar, methane destruction, and improved forest management credits.

### 6.8 Monte Carlo Weight Sensitivity

To assess the robustness of grade assignments to weight perturbation, we performed Monte Carlo sensitivity analysis with 10,000 iterations per concentration parameter. Weight vectors were sampled from a Dirichlet distribution parameterized as alpha_i = w_i * concentration, with the co-benefits weight forced to zero (maintaining the safeguards-gate).

At concentration = 50 (moderate perturbation), global robustness is 93.7%: on average, a credit retains its grade in 93.7% of random weight samples. Five of 29 credits are classified as fragile (stability below 90%): Plan Vivo agroforestry (51.5% stability, on the A/BBB boundary), Gold Standard cookstoves (66.1%, BBB/BB boundary), Charm Industrial bio-oil injection (72.7%, AAA/AA boundary), Pachama Brazilian reforestation (74.0%, A/AA boundary), and adipic acid N2O destruction (78.1%, BBB/A boundary). At concentration = 20 (wide perturbation), robustness drops to 90.1% with 10 fragile credits. At concentration = 100 (tight perturbation), robustness rises to 95.4%.

The two credits whose AAA grade is most consequential -- Climeworks Orca and Heirloom DAC -- achieve 100% stability at all three concentration levels, confirming that the framework's headline finding (engineered CDR dominates the top of the quality scale) is robust to weight uncertainty.

### 6.9 Adversarial Testing

Five adversarial credits were designed to exploit specific attack vectors:

1. **Narrative washing.** A credit with inflated co-benefit scores but low removal and permanence scores. Correctly caught by the safeguards-gate: co-benefits carry zero weight, and the low removal/permanence scores determine the composite.

2. **Double counting.** A duplicate credit issued across two registries. The `doubleCounting` disqualifier fires, capping the grade at B regardless of dimension scores.

3. **Registry shopping.** A credit issued on an unrecognized registry. Low registry score plus the `noThirdParty` disqualifier caps the grade at BBB.

4. **Vintage arbitrage.** An ancient credit with inflated dimension scores. The vintage decay function pulls the composite below the target threshold.

5. **Biodiversity destruction.** A monoculture plantation with high carbon removal but documented habitat disturbance. The `biodiversityHarm` disqualifier fires, capping at BBB, per Zeng et al.'s finding that offset projects are associated with a 3.7% increase in habitat disturbance [33].

All five adversarial credits were correctly caught by both the automated framework and the independent LLM panel (5/5 detection rate).

---

## 7. Discussion

### 7.1 ERC-CCQR as a General Real-World Asset Rating Standard

The `meetsGrade()` pattern generalizes beyond carbon credits to any tokenized real-world asset requiring quality differentiation. Biodiversity credits, water quality certificates, and renewable energy guarantees of origin all face analogous information asymmetries that could benefit from a composable on-chain quality primitive. The `compositeVarianceBps2` field for uncertainty quantification is applicable to any domain where rating confidence matters, including financial credit ratings and ESG scores.

The insurance industry provides a concrete example of downstream utility. Oka, Howden, Lockton, and WTW have all launched carbon credit insurance products (invalidation, reversal, non-delivery) that consume quality ratings as underwriting inputs [34]. The composite score plus P(grade) posterior is precisely the actuarial input these models require. This aligns with Cabiyo and Field's [35] argument that carbon markets should embrace imperfection through risk management rather than demanding perfection.

### 7.2 Limitations

Several limitations constrain the current findings:

**Oracle trust.** Rating accuracy depends on off-chain assessment quality. The "garbage in, garbage out" problem is not solved by on-chain transparency alone. The rating contract is only as trustworthy as its raters.

**Single-provider LLM panel.** The IRR study uses only Anthropic Claude models (Opus 4.6, Sonnet 4.6, Haiku 4.5). These models share training data and RLHF procedures. A multi-provider replication (GPT-5, Gemini 2.5 Pro, Llama, DeepSeek) is necessary to detect provider-specific biases. The kappa = 0.600 should be treated as a preliminary estimate with approximately +/-0.10 noise given the n = 29 sample size.

**Credit coverage.** The framework has been validated on 318 credits. Commercial agencies rate 4,400+ projects (MSCI) to 9,000+ (CarbonPlan OffsetsDB). The framework is validated on accuracy and reproducibility, not coverage.

**Weight calibration.** The weight vector has not yet been validated by a formal domain expert panel. Twenty experts have been identified for structured elicitation; consultation is in progress. The CCP calibration provides population-level validation, but individual weights may benefit from expert adjustment.

**Centralized bootstrapping.** The current deployment uses a single-owner rater with trusted-attester allowlist for the EAS adapter. True decentralization requires broader attestation ecosystem maturity and governance mechanisms beyond the scope of this prototype.

**Cookstove divergence.** The framework's Oxford-hierarchy-based scoring caps avoidance projects below grade A, diverging from commercial agencies that rate several cookstove projects at A or above. This is a deliberate normative design choice, but it limits comparability for avoidance-heavy portfolios.

### 7.3 Ethical Considerations

The framework embeds normative assumptions. The weight vector prioritizes removal over avoidance, consistent with the Oxford Principles for Net Zero Aligned Carbon Offsetting [29]. Co-benefits are excluded from the integrity composite, a choice that may disadvantage community-development-focused projects. All normative parameters are documented and configurable: users can modify weights by changing a single JSON file and redeploying.

Quality rating may inadvertently legitimate low-quality credits by grading them (B-rated) rather than rejecting them entirely. The framework does not resolve the fundamental debate about whether offsets delay structural decarbonization [36].

### 7.4 Adoption Pathway

We envision a three-phase adoption pathway. Phase 1 (current): single-rater prototype deployed on Base Sepolia with Foundry tests and open-source artifact. Phase 2: production deployment on Base mainnet with integration into Klima Protocol 2.0 retirement flow and Toucan CHAR fee overlay. Phase 3: decentralized multi-rater attestation via EAS with registry-level attesters (Verra, Gold Standard, Puro, Isometric) publishing ratings through the trusted-attester framework.

---

## 8. Conclusion

ERC-CCQR provides, to our knowledge, the first composable on-chain quality rating standard for carbon credits. The `meetsGrade()` primitive enables quality-gated pools designed to mitigate the adverse selection that collapsed Toucan BCT's pool composition to a Lemons Index of 0.724. Three composability patterns -- quality-gated deposit pools, retirement gates, and fee overlays -- demonstrate that the standard integrates with existing DeFi infrastructure at modest gas overhead (approximately 19,244 gas per quality check, adding 10--15% to a typical DeFi operation). The standard's distributional scoring, which stores both composite score and variance on-chain, is to our knowledge unprecedented for any class of real-world asset tokens.

Four validation studies establish the rating's empirical grounding. CCP calibration against 318 credits recovers the ICVCM quality threshold with a 1.99-grade gap (Cohen's d = 1.80). Cross-type rank correlation with commercial agencies achieves Spearman +0.901 versus BeZero (n = 27 projects, 12 project types, Kendall tau = +0.821, 52% exact grade match, 100% within plus or minus one grade), exceeding the inter-agency mean of +0.009. Inter-rater reliability (Fleiss' kappa = 0.600, ICC = 0.993) demonstrates that the rubric is reproducible by independent systems. Adversarial testing catches all five attack vectors with 100% disqualifier recall.

Future work includes expert-validated weight calibration using structured elicitation with 20 identified domain experts, multi-provider LLM panel replication for IRR generalizability, production deployment on Base mainnet with Klima Protocol 2.0 and Toucan CHAR integration, EAS schema registration with trusted-attester onboarding for major registries, generalization of the `meetsGrade()` pattern to biodiversity credits and renewable energy certificates, and dynamic re-rating pipelines with digital MRV inputs from satellite and IoT sources.

The standard, reference implementation, test suite, scoring engine, and all evaluation data are available under MIT license at https://github.com/Adeline117/carbon-neutrality.

---

## References

[1] BeZero Carbon. Rating methodology and public ratings database. https://bezerocarbon.com, 2023.

[2] Sylvera. State of Carbon Credits 2025. https://sylvera.com, 2025.

[3] Calyx Global. Carbon credit ratings explained. https://calyxglobal.com, 2024.

[4] Calel, R., et al. Systematic assessment of the achieved emission reductions of carbon crediting projects. *Nature Communications*, 2024.

[5] Toucan Protocol. BCT and CHAR pool contracts and documentation. https://toucan.earth, 2022--2025.

[6] Toucan Protocol. CHAR pool on Base (0x20b048fA035D5763685D695e66aDF62c5D9F5055). Binary project allowlist gating via checkEligible(), 2025.

[7] Klima Protocol 2.0. kVCM on Base (0x00fbac94fec8d4089d3fe979f39454f48c71a65d). https://klimadao.finance, 2026.

[8] Zhou, C., Chen, H., Wang, S., Sun, X., El Saddik, A., and Cai, W. Harnessing Web3 on carbon offset market for sustainability: Framework and a case study. *IEEE Wireless Communications*, 30(5):104--111, 2023.

[9] Akerlof, G. A. The market for "lemons": Quality uncertainty and the market mechanism. *Quarterly Journal of Economics*, 84(3):488--500, 1970.

[10] Moss. MCO2 token on Ethereum and Polygon. https://moss.earth, 2022.

[11] ICVCM. CCP impact report: Five programs and 36 methodologies approved, ~101M credits eligible. https://icvcm.org, 2025.

[12] MSCI. State of integrity in the global carbon-credit market. Fewer than 10% rated A or above; high-integrity index at 4x low-integrity index, 2025.

[13] Perspectives Climate Group / Carbon Market Watch. Assessing and comparing carbon credit rating agencies. Freiburg, Table 19--20, 2023.

[14] Carbon Credit Quality Initiative (CCQI). Methodology v3.0: 7 quality objectives, 1--5 scale. Environmental Defense Fund, WWF, Oeko-Institut. https://carboncreditquality.org, 2024.

[15] Renoster. Mercury Rubric: Open forestry project rating methodology. https://renoster.co, 2025.

[16] Gao, H. O. and Liu, X. CATchain-R: A blockchain-based carbon registry platform with credibility index. *npj Climate Action*, 2026.

[17] Jaffer, S., Sheridan, E., and Mayall, S. Global, robust and comparable digital carbon assets. *IEEE International Conference on Blockchain and Cryptocurrency (ICBC)*, 2024.

[18] JPMorgan Kinexys. Carbon markets reimagined: Scale, resiliency, and transparency. Partners: S&P Global, EcoRegistry, International Carbon Registry, 2025.

[19] Hypercerts Foundation. EAS-based evaluator registry on Base, Optimism, and Celo. GainForest Ecocerts schema for ecological impact attestation. https://hypercerts.org, 2025.

[20] Manshadi, V., Monachou, F., and Morgenstern, J. Offsetting carbon with lemons: Adverse selection and certification in the voluntary carbon market. *SSRN Working Paper*, 2025.

[21] Berg, F., Koelbel, J. F., Pavlova, A., and Rigobon, R. The market for voluntary carbon offsets. *SSRN Working Paper*, 2025.

[22] Trencher, G., et al. Demand for low-quality offsets by major companies undermines climate integrity of the voluntary carbon market. *Nature Communications*, 2024.

[23] Vogelsteller, F. and Buterin, V. ERC-20: Token standard. Ethereum Improvement Proposals, 2015.

[24] Entriken, W., Shirley, D., Evans, J., and Sachs, N. ERC-721: Non-fungible token standard. Ethereum Improvement Proposals, 2018.

[25] ERC-4626: Tokenized vault standard. Ethereum Improvement Proposals, 2022.

[26] Ku, H. H. Notes on the use of propagation of error formulas. *Journal of Research of the National Bureau of Standards*, 70C(4):263--273, 1966.

[27] Ethereum Attestation Service (EAS). https://attest.sh. Base, Optimism, Ethereum attestation infrastructure.

[28] Coglianese, C. and Giles, C. Auditors can't save carbon offsets. *Science*, 389(6733), 2025. DOI: 10.1126/science.ady4864.

[29] Allen, M. R., et al. The Oxford Principles for Net Zero Aligned Carbon Offsetting. University of Oxford, 2020.

[30] Calyx Global. Are carbon credit quality indicators delivering? CCP-eligible projects average A vs. C for non-CCP. https://calyxglobal.com, 2025.

[31] Bootstrap rank correlation analysis. 10,000 resamples, seed = 42. Expanded cross-type dataset (n = 27, 12 project types): Spearman rho = +0.901, Kendall tau = +0.821, 52% exact grade match, 100% within plus or minus one grade, permutation p < 0.001. Data available in repository.

[32] Landis, J. R. and Koch, G. G. The measurement of observer agreement for categorical data. *Biometrics*, 33(1):159--174, 1977.

[33] Zeng, Y., et al. Limitations of carbon markets for biodiversity conservation. *Nature Reviews Biodiversity*, 2026. DOI: 10.1038/s44358-026-00150-4.

[34] Oka. Carbon credit insurance: Carbon Protect and Green Credit Insurance. Lloyd's-backed. https://carboninsurance.co, 2025.

[35] Cabiyo, B. and Field, C. B. Embracing imperfection: Carbon offset markets must learn to mitigate the risk of overcrediting. *PNAS Nexus*, 4(5):pgaf091, 2025.

[36] Cheong, B. C. The paradox and fallacy of global carbon credits. *Anthropocene Science*, 4:72--83, 2025.

[37] Cheong, T. (Annual Review of Environment and Resources). Are carbon offsets fixable? 2025.

[38] Frontiers in Blockchain. Tokenized carbon credits in voluntary carbon markets: The case of KlimaDAO. 2024.

[39] Jirasek, M. Klima DAO: A crypto answer to carbon markets. Springer, 2023.

[40] Bosshard, L., et al. Blockchain-based voluntary carbon market: Strategic insights into network structure. *Frontiers in Blockchain*, 8:1603695, 2025.

[41] Finance and Space. Carbon credits meet blockchain -- Cryptocarbon projects and the algorithmic financialisation of voluntary carbon markets. 2024.

[42] Huber, R., Bach, V., and Finkbeiner, M. Multi-criteria assessment of carbon credits: A meta-analysis of 15 quality criteria. *Journal of Environmental Management*, 2024.

[43] NUS SGFIN. Nine-principle program evaluation of voluntary carbon standards. Singapore Green Finance Institute, 2024.

[44] CarbonPlan. OffsetsDB: Open database of 9,000+ carbon offset projects. CDR Verification Confidence Levels (VCL). https://carbonplan.org, 2025.

[45] Shrout, P. E. and Fleiss, J. L. Intraclass correlations: Uses in assessing rater reliability. *Psychological Bulletin*, 86(2):420--428, 1979.

[46] Singapore NEA. Carbon rating panel: BeZero, Calyx, Sylvera appointed for ICC Framework carbon credit assessment. https://nea.gov.sg, 2025.

[47] Gold Standard and ATEC Global. First fully digital cookstove carbon credits issued using 100% IoT-SIM digital MRV on Hedera Guardian blockchain. https://goldstandard.org, 2025.

[48] Garcia, A. and Sanford, L. On the potential for strategic behavior in jurisdictional REDD+. *Proceedings of the National Academy of Sciences*, 123(14), 2026. DOI: 10.1073/pnas.2531612123.

[49] West, T. A. P., et al. Demystifying the romanticized narratives about carbon credits from voluntary forest conservation. *Global Change Biology*, 31(10):e70527, 2025.

[50] Battocletti, V., et al. The voluntary carbon market: Market failures and policy implications. *Colorado Law Review*, 2024.

[51] RMI Centigrade. Carbon crediting data framework: Open-source framework for standardizing carbon credit data. https://centigrade.earth, 2025.
