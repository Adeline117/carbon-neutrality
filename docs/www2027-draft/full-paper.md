# ERC-CCQR: The Missing Composability Primitive for Real-World Asset Quality

**Abstract.** ERC-20 made token balances composable; ERC-721 made ownership composable; ERC-4626 made vault shares composable. No standard exists for making the *quality* of a tokenized real-world asset composable. As trillions of dollars in real-world assets move on-chain -- from BlackRock's BUIDL fund to carbon credits to renewable energy certificates -- this missing primitive determines whether tokenization amplifies or resolves the information asymmetries inherent in heterogeneous asset classes. We present ERC-CCQR, a composable on-chain quality rating standard whose core primitive, `meetsGrade(address token, uint256 id, Grade min) -> bool`, is the quality analogue of `balanceOf()`: a zero-gas view function that any protocol can call via `staticcall` to determine whether a specific asset meets a quality threshold before accepting it. We validate the standard against the hardest possible test case -- voluntary carbon credits, an asset class with the highest documented quality variance (Lemons Index 0.076--0.724 across pools), the most acute information asymmetry (commercial rating agencies anti-correlated at Spearman +0.009), and a documented market-for-lemons collapse (Toucan BCT). Against 318 credits, the standard achieves: (i) a 1.99-grade gap between ICVCM CCP-eligible and non-CCP credits (Cohen's d = 1.80, p < 0.001); (ii) cross-type Spearman +0.901 versus BeZero across 12 project types (n = 27, 100% within one grade); (iii) Fleiss' kappa = 0.600 inter-rater reliability (ICC = 0.993); and (iv) counterfactual Lemons Index reduction from 0.724 to 0.405 under quality gating. We then demonstrate that the interface generalizes without modification to biodiversity credits and renewable energy certificates, with seven passing Foundry tests confirming zero-modification reuse across three RWA domains. The standard stores both composite score and variance on-chain (`compositeVarianceBps2`), enabling probabilistic grade computation -- a first for any real-world asset token standard.

---

## 1. Introduction

### 1.1 The Quality Composability Gap in Tokenized Real-World Assets

The tokenization of real-world assets (RWAs) is accelerating. BlackRock's BUIDL fund holds over $1.7 billion in on-chain U.S. Treasuries; Ondo Finance, Centrifuge, and Maple Finance have brought structured credit, receivables, and fixed-income products on-chain; voluntary carbon credits, biodiversity credits, and renewable energy certificates are traded as ERC-20 and ERC-721 tokens across Ethereum, Polygon, and Base. Estimates for the total addressable market range from $4 trillion (Boston Consulting Group, 2025) to $16 trillion (McKinsey, 2030 projection). The infrastructure for moving assets on-chain is maturing rapidly.

What is missing is the infrastructure for querying the *quality* of those assets once they arrive.

ERC-20 answers "how much does this address hold?" ERC-721 answers "who owns this specific token?" ERC-4626 answers "what is my share of this vault worth?" No standard answers the question that matters most for heterogeneous real-world assets: *"Is this specific asset good enough?"* A DeFi pool that accepts tokenized carbon credits cannot ask whether a given credit is high-integrity or a legacy junk offset. A lending protocol that collateralizes renewable energy certificates cannot distinguish a new-build solar REC providing grid additionality from a legacy hydro certificate with no incremental climate impact. A conservation fund that pools biodiversity credits cannot query whether a habitat protection covenant is durable or nominal.

The absence of this primitive -- a composable, on-chain quality query -- means that tokenization *amplifies* the information asymmetries already present in these markets. When all eligible assets are treated as fungible, Akerlof's lemons dynamic [9] is not merely theoretical: low-quality asset holders deposit aggressively into single-price pools, high-quality holders withhold supply, and the pool's average quality degrades until the market collapses.

### 1.2 Carbon Credits as the Hardest Test Case

We validate the standard against voluntary carbon credits -- the asset class where the quality composability gap is widest, the failure mode most documented, and the information asymmetry most acute.

**Highest quality variance.** The Lemons Index (a metric we introduce in this paper) ranges from 0.076 for curated engineered-CDR pools to 0.724 for Toucan Protocol's BCT pool, where the average deposited credit scored 27.6 out of 100. No other tokenized asset class exhibits a 10:1 quality range within a single supposedly-fungible pool [5].

**Documented market failure.** BCT accepted any Verra-registered credit with a post-2008 vintage, treating all eligible credits as worth the same price. Holders of legacy HFC-23 destruction, unverified grassland avoidance, and expired CDM wind credits deposited aggressively; holders of high-quality engineered carbon dioxide removal withheld supply. Not a single credit in BCT's 43-credit composition scored at grade A or above [5, 9]. Toucan's subsequent CHAR pool introduced binary allowlist gating via `checkEligible()`, but binary gating cannot express continuous quality gradients [6]. Klima Protocol 2.0 introduced treasury-level quality selection but still lacks a per-credit gate [7]. Zhou et al. showed that NFT-based models preserve per-credit identity but attach no quality metadata [8].

**Most acute information asymmetry.** Commercial rating agencies -- BeZero, Sylvera, Calyx Global, MSCI -- produce proprietary quality assessments, but the mean inter-agency Spearman rank correlation is +0.009 [13]. The same Amazon REDD+ project received the highest possible rating from one agency and the lowest from another. None provides a smart contract interface. Quality information exists but is off-chain, contradictory, and invisible to the protocols that need it most [1, 2, 3]. A companion methods paper [52] presents the off-chain quality framework and its validation against CCP and commercial ratings; a companion empirical paper [53] documents depositor-level adverse selection in BCT using the quality scores derived from that framework.

If a composable quality primitive works for carbon credits -- the worst case -- it works for any tokenized real-world asset.

### 1.3 Contributions

This paper makes five contributions:

1. **A composable quality standard for real-world asset tokens.** We define ERC-CCQR, a three-level compliance hierarchy: Level 1 (boolean quality query via `meetsGrade` and `isStale`), Level 2 (full `Rating` struct with composite score, variance, and provenance metadata), and Level 3 (decentralized attestation relay via the Ethereum Attestation Service). The interface is domain-agnostic; only the scoring implementation is domain-specific. This is the same separation that makes ERC-20 universal: the standard defines the query, not the asset.

2. **The `meetsGrade()` primitive -- the quality analogue of `balanceOf()`.** A zero-gas view function that encapsulates grade lookup, staleness check, and threshold comparison in a single `staticcall`, enabling any DeFi protocol to gate deposits, retirements, or fee structures on a continuous quality threshold.

3. **Distributional on-chain scoring with uncertainty quantification.** The first real-world asset token standard to store both a composite score and its variance on-chain (`compositeVarianceBps2`), enabling downstream consumers to compute P(grade >= threshold) via Gaussian CDF without additional oracle calls.

4. **The Lemons Index for DeFi pool health.** A quantitative adverse-selection metric, L(pool) = 1 - (mean composite / 100), applied to five real carbon credit pools and counterfactual quality-gated scenarios, establishing a measurable link between Akerlof's theory [9] and on-chain market outcomes.

5. **Empirical validation on the hardest RWA domain, plus cross-domain generalization.** CCP calibration against 318 credits (1.99-grade gap, Cohen's d = 1.80), commercial agency rank correlation (Spearman +0.901 vs. BeZero, n = 27, 12 project types), LLM panel inter-rater reliability (Fleiss' kappa = 0.600, ICC = 0.993), adversarial testing with 100% disqualifier recall, and zero-modification interface reuse demonstrated across biodiversity credits and renewable energy certificates (seven passing generalization tests).

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

### 2.6 Oracle and Compliance Interface Comparison

ERC-CCQR's `meetsGrade()` and `ratingOf()` functions superficially resemble existing on-chain oracle interfaces, but the design requirements for a *quality oracle* differ fundamentally from those for a *price oracle* or an *identity compliance gate*. This subsection compares ERC-CCQR against four established systems -- Chainlink Data Feeds, UMA Optimistic Oracle V3, Pyth Network, and ERC-3643 (T-REX) -- to delineate what is novel, what is adapted, and what is deliberately excluded.

[Table 6: Oracle and compliance interface comparison. Columns: System, Core query function, Query semantic, Return data type, Staleness model, Update model, Composability pattern. Rows: Chainlink AggregatorV3 (latestRoundData(), "What is the current price?", int256 answer + uint256 updatedAt, heartbeat + deviation threshold, push -- DON nodes update on deviation or heartbeat, staticcall to view function); UMA OptimisticOracleV3 (assertTruth() / getAssertion(), "Is this claim true?", bool + Assertion struct, challenge window liveness period, optimistic -- assert then dispute, callback-based with assertionResolvedCallback); Pyth Network (getPrice() / getPriceUnsafe(), "What is the current price?", Price struct: int64 price + uint64 conf + int32 expo + uint publishTime, caller-specified max staleness via getPriceNoOlderThan, pull -- consumer updates on-chain before reading, staticcall to view function); ERC-3643 T-REX (canTransfer() / isVerified(), "Can this address hold/receive this token?", bool, no expiry -- identity claims managed by trusted issuers, push -- claim issuers update ONCHAINID, called within transfer function); ERC-CCQR (meetsGrade() / ratingOf(), "Does this asset meet a quality threshold?", bool + Rating struct with compositeBps + compositeVarianceBps2 + Grade enum, dual: time expiry via expiresAt + methodology version via CURRENT_METHODOLOGY_VERSION, push -- authorized rater calls setRating or relays EAS attestation, staticcall to view function).]

**Grades versus prices: ordinal versus continuous.** Chainlink and Pyth return continuous numeric values (int256 or int64) representing a market price at arbitrary precision. ERC-CCQR returns an *ordinal* Grade enum (B through AAA) alongside a continuous composite score in basis points. The ordinal grade is a deliberate design choice: quality assessment produces ranked categories, not precise measurements. A carbon credit rated AA is categorically better than one rated BBB, but the difference between composite scores 7600 and 7800 within the AA band is not economically meaningful in the way that a $0.02 price difference is for a stablecoin. The `meetsGrade()` function abstracts away the continuous score entirely, returning a boolean -- the minimal decision primitive that a consuming protocol needs. Neither Chainlink nor Pyth offers this threshold-query pattern; consumers must implement their own comparison logic against `latestAnswer()` or `getPrice()`.

**Disqualifiers versus deviation.** Price oracles handle uncertainty through deviation: Chainlink triggers an update when the price moves beyond a deviation threshold (typically 0.5--1%), and Pyth returns an explicit confidence interval (`conf` field). ERC-CCQR handles uncertainty through two orthogonal mechanisms: (i) *distributional uncertainty* via `compositeVarianceBps2`, which enables probabilistic grade computation (P(grade >= threshold) via Gaussian CDF), and (ii) *categorical disqualifiers*, which are binary flags that can cap the maximum achievable grade regardless of the composite score. Disqualifiers have no analogue in price oracles -- there is no concept of a price being "disqualified." A credit with a high composite but an active `doubleCounting` flag is capped at grade B; this categorical override mechanism is novel to the quality-oracle domain. Pyth's `conf` field is the closest architectural precedent for on-chain uncertainty, and we adapted the principle of storing uncertainty as a first-class return value, but the semantics differ: `conf` bounds a price estimate symmetrically, while `compositeVarianceBps2` enables asymmetric grade-boundary probability computation.

**Methodology versioning versus heartbeat.** Chainlink uses a heartbeat model: if no update arrives within a specified period (e.g., 3600 seconds), the feed is considered stale. Pyth delegates staleness enforcement to the consumer via `getPriceNoOlderThan(maxAge)`. UMA uses a liveness window during which assertions can be disputed. ERC-CCQR introduces a *dual staleness model* that is novel among oracle interfaces: ratings expire both by time (`expiresAt`) *and* by methodology version (`methodologyVersion < CURRENT_METHODOLOGY_VERSION`). The methodology-version dimension has no counterpart in price oracles because prices do not have "methodologies" -- they are observations, not assessments. When a rating framework is revised (e.g., the v0.6 addition of `biodiversityHarm`), all ratings written under the prior version become stale in O(1) time by incrementing a single contract constant. This is architecturally analogous to Chainlink's aggregator upgrade pattern (deploying a new aggregator address), but achieved without contract migration.

**ERC-3643 comparison: asset-centric versus identity-centric gating.** ERC-3643 (T-REX) is the closest functional analogue to ERC-CCQR in that both gate token transfers on a compliance/quality condition evaluated via a view function. ERC-3643's `canTransfer(address _from, address _to, uint256 _amount)` checks whether the *participants* are compliant -- whether the receiver holds valid identity claims (KYC/AML) from trusted issuers registered in the Identity Registry. ERC-CCQR's `meetsGrade(address creditToken, uint256 tokenId, Grade minGrade)` checks whether the *asset* is compliant -- whether the credit meets a quality threshold regardless of who holds it. This is the fundamental architectural distinction: ERC-3643 is *identity-centric* (gates on "who can hold"), while ERC-CCQR is *asset-centric* (gates on "what quality is the asset"). Both standards use a trusted-issuer/trusted-rater allowlist pattern for write access, and both expose boolean view functions for zero-gas reads by consuming contracts. The compliance module architecture of ERC-3643 -- where modular rule contracts (MaxOwnershipByCountry, MaxBalance) are composed via an ICompliance interface -- informed our decision to separate the rating contract from consuming contracts (QualityGatedPool, KlimaRetirementGate) rather than embedding quality logic within the token itself. However, ERC-3643's claim-topic model (identity claims issued by trusted issuers) operates at a fundamentally different abstraction level from ERC-CCQR's dimension-score model (quality scores derived from technical assessment). A future integration could combine both: ERC-3643 gates on *who* can trade a credit, while ERC-CCQR gates on *which credits* are eligible for a pool.

**Summary of novel versus adapted design decisions.** Three design elements are novel to ERC-CCQR: (i) the threshold-query pattern (`meetsGrade()` returning a boolean for a caller-specified ordinal threshold), which abstracts away score internals and has no equivalent in Chainlink, Pyth, or UMA; (ii) the dual staleness model combining time expiry with methodology versioning; and (iii) the categorical disqualifier cap lattice, which overrides continuous scores with binary safety flags. Three elements are adapted from existing patterns: the `view`-function composability model follows Chainlink and ERC-3643; the on-chain uncertainty field adapts Pyth's `conf` design to ordinal distributions; and the trusted-rater allowlist follows ERC-3643's trusted-issuer registry and Hypercerts' evaluator registry [19].

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

We demonstrate three concrete DeFi integration patterns showing that `meetsGrade()` functions as a reusable building block for on-chain quality infrastructure. All three patterns target Base L2, where both Toucan CHAR (0x20b0...5055) and Klima Protocol 2.0 (kVCM: 0x00fb...a65d) are deployed, enabling atomic composability within single transactions.

**The composability cascade.** The transformative power of ERC-20 was not any single protocol -- it was the fact that thousands of protocols could compose with any token implementing the standard, without bespoke integration. `balanceOf()` and `transfer()` created a cascade: DEXs, lending protocols, yield aggregators, and payment rails all inherited the same token interface. `meetsGrade()` enables the same cascade for quality. Any protocol that accepts tokenized real-world assets -- deposit pools, retirement gates, lending vaults, insurance underwriters, compliance dashboards -- can inherit quality signals from the rating layer via a single `staticcall`, at zero gas overhead, without knowing or caring how the quality score is computed. The rating contract handles the assessment; the consuming protocol handles the business logic; the interface is the bridge. Just as ERC-20 composability turned isolated tokens into a financial ecosystem, quality composability can turn opaque real-world assets into transparently-graded instruments that any protocol can reason about.

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

### 4.2 Additional Composability Patterns

Two additional contracts demonstrate that `meetsGrade()` composes into distinct DeFi workflows beyond deposit gating.

**Retirement quality gate.** The KlimaRetirementGate contract gates Klima Protocol 2.0's kVCM retirement flow. Before burning a kVCM token to effect an off-chain retirement claim, the gate calls `isStale()` and `meetsGrade()` with a configurable `minRetirementGrade`. Corporate buyers set `Grade.AA` for SBTi-aligned claims or `Grade.A` for general voluntary claims. The threshold is governance-updatable without contract redeployment, and the view-only pattern incurs zero gas for the eligibility check itself.

**Quality-based fee discount.** The CHARQualityOverlay contract augments Toucan CHAR's binary `checkEligible()` allowlist with continuous pricing incentives. After a credit passes CHAR's eligibility filter, the overlay reads the full `Rating` struct via `ratingOf()` and returns a grade-tiered fee discount: 5% for AAA, 3% for AA, 1% for A, and 0% otherwise. This creates a positive economic incentive that complements CHAR's existing concentration-penalty fee mechanism by rewarding integrity. The overlay incurs approximately 35,000 gas (struct copy plus fee computation).

### 4.3 EAS Attestation Relay

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

**Normality assumption.** The P(grade >= threshold) computation assumes that the composite score follows a Gaussian distribution. With seven weighted dimensions and bounded [0, 100] scores, the Central Limit Theorem provides partial justification: the composite is a weighted sum of independent dimension scores, and even with modest n = 7, simulation studies show that weighted sums of bounded variates converge to near-normality when no single weight dominates. However, boundary effects exist. Credits whose composites fall near grade thresholds (e.g., a composite of 4480 bps near the BBB/BB boundary at 4500) may exhibit asymmetric distributions because dimension scores are truncated at 0 and 100. For such boundary credits, the Gaussian CDF may overestimate or underestimate P(grade) by several percentage points. The practical impact is modest because `compositeVarianceBps2` is used for grade *probability estimation*, not point prediction: consuming protocols call `meetsGrade()` on the deterministic `finalGrade`, and the variance field serves as supplementary risk information. We note this as a known approximation; future work will validate the empirical distribution shape via Monte Carlo sampling of dimension scores drawn from calibrated per-dimension distributions, comparing the resulting composite CDF against the Gaussian approximation (see Section 7.2).

### 5.3 Off-Chain/On-Chain Scoring Invariant

The Python scoring engine (`score.py`) and the Solidity contract produce bit-identical results. The test vector Climeworks Orca yields a composite of 9505 bps and a composite variance of 83,706 bps^2 in both implementations. This invariant is enforced by Foundry tests that compare expected values computed by the Python scorer against the Solidity contract's `computeComposite()` and `computeCompositeVariance()` outputs.

---

## 6. Evaluation

### 6.1 Gas Benchmarks

All gas measurements were obtained on Base Sepolia using Foundry's `forge test --gas-report`.

[Table 2: Gas benchmarks for all ERC-CCQR operations (measured via `forge test --gas-report`, Foundry 2025). Columns: Operation, Measured Gas, Notes. Rows: setRating (single credit, cold) 167,720 (7 dimension scores + 7 stds + 7 flags + metadata in fresh slots); setRating (warm update) 30,308 (SSTORE nonzero-to-nonzero); meetsGrade (view) 19,244 (one SLOAD mapping read + staleness check + enum compare); ratingOf (view) 20,823 (full struct copy to memory); isStale (view) 19,057 (SLOAD + timestamp compare); isStale (unrated) 7,097 (early return); EAS relay (happy path) 250,086 (getAttestation + decode + setRating); QualityGatedPool deposit 57,000--162,000 (meetsGrade + transferFrom).]

The read operations (`meetsGrade`, `ratingOf`, `isStale`) are free because they are `view` functions executed via `staticcall`. The quality check adds zero marginal gas cost to any DeFi protocol that already performs token transfers. Write operations (`setRating`) cost less than $0.10 per credit on Base L2 at current gas prices.

To contextualize these costs: a `meetsGrade()` call at 19,244 gas adds approximately 30--40% to an ERC-20 `transfer()` (~45,000--65,000 gas) as an external call, or approximately 25% inline. It adds approximately 10--15% to a Uniswap V3 swap (~130,000--185,000 gas), and approximately 8--10% to an Aave V3 `supply()` (~180,000--250,000 gas). For a carbon retirement transaction, which typically involves a swap and a burn, the quality gate remains a small fraction of total gas.

An end-to-end Foundry simulation confirmed these per-operation benchmarks at scale: 64 deposit attempts (16 credits across 4 quality-gated pools) consumed approximately 26.4 million gas total, averaging ~413,000 gas per deposit attempt including both the `meetsGrade()` check and the `transferFrom()` execution (or revert for rejected credits).

[Figure 3: Gas cost breakdown as stacked bar chart comparing deposit-with-quality-gate versus deposit-without for each composability pattern. The quality gate overhead (meetsGrade ~19k gas) is visually small compared to the base transaction costs (ERC-20 transfer ~65k, Uniswap swap ~185k, Aave supply ~250k).]

### 6.2 Scalability Analysis

Read scalability is O(1) due to Solidity's mapping-based storage architecture. The `meetsGrade()` function performs a constant-time `keccak256` hash of `(creditToken, tokenId)` followed by a single `SLOAD`, regardless of the total number of credits rated. Foundry tests confirm identical gas costs for `meetsGrade()` after 100, 500, and 1,000 pre-existing ratings.

Write scalability is the bottleneck. A full re-rating of 318 credits requires approximately 53 million gas (318 * 167,720 for cold writes); scaling to 1,000 credits requires approximately 168 million gas, achievable within a few blocks on Base. At 100,000 credits, batch operations spread across multiple transactions are required. The methodology-version staleness mechanism manages this gracefully: when the methodology is bumped, all outdated ratings become stale without requiring deletion, and re-rating can proceed incrementally.

### 6.3 CCP Empirical Calibration

The 318-credit dataset (165 CCP-eligible, 153 non-CCP) produces a 1.99-grade gap between groups (CCP mean = 2.69, non-CCP mean = 0.70; Cohen's d = 1.80, 95% bootstrap CI [1.50, 2.16]; Mann-Whitney p < 0.001; CLES = 0.914). The framework was not trained on CCP labels; the gap serves as external validation. Calyx Global (2025) independently reported an approximately two-grade gap between CCP-eligible and non-CCP projects on their own scale [30], confirming our weight calibration.

[Figure 4: Dual violin plot of composite score distributions for CCP-eligible (n = 165) versus non-CCP (n = 153) credits. The 1.99-grade gap is annotated.]

### 6.4 Commercial Agency Rank Correlation

The cross-type dataset (n = 27 projects, 12 project types) achieves Spearman +0.901 versus BeZero (95% bootstrap CI [+0.783, +0.959], p < 0.0001; Kendall tau = +0.821), with 52% exact grade match and 100% within one grade. Leave-one-out stability yields rho = +0.889 to +0.922 across all jackknife samples. For context, the mean inter-agency Spearman among BeZero, Sylvera, and Calyx on the same REDD+ projects is +0.009 [13].

[Table 4: Spearman rank correlation matrix. Key rows: Ours vs. BeZero (+0.664 REDD+ n=6, +0.901 cross-type n=27), Inter-agency mean (+0.009).]

Subgroup analysis: removal/CDR projects (n = 12) achieve rho = +0.973; avoidance projects (n = 15) rho = +0.802. One systematic divergence persists: the framework caps avoidance projects (including cookstoves) at BBB per the Oxford Principles hierarchy [29], while commercial agencies rate several at A or above -- a deliberate normative design choice.

### 6.5 Inter-Rater Reliability

Three Claude-family LLM raters (Opus 4.6, Sonnet 4.6, Haiku 4.5) independently scored 29 credits using the v0.4.1 rubric with author scores redacted. Grade-level Fleiss' kappa is +0.600 (moderate-to-substantial per Landis and Koch [32]); composite ICC(2,k) is +0.993. Author versus panel median agreement is 86% exact grade match and 100% within one grade. The two highest-weight dimensions -- permanence (kappa = 0.684) and removal type (kappa = 0.585) -- show the highest reliability, providing confidence that headline findings rest on the most reproducible components. The weakest dimension, registry/methodology (kappa = 0.168), motivated the v0.6 collapse from four tiers to two tiers (CCP-eligible vs. non-CCP). Disqualifier recall on four synthetic stress credits was 12/12 (100%).

[Figure 5: Per-dimension Fleiss' kappa bar chart with Landis-Koch interpretation bands.]

### 6.6 Adverse Selection Prevention: Lemons Index

We define the Lemons Index as L(pool) = 1 - (mean composite / 100), ranging from 0 (perfect quality) to 1 (zero quality) [9]. The key comparison: BCT's LI = 0.724 (n = 43, mean composite = 27.6, 0% at grade A or above) versus CHAR's LI = 0.221 (n = 12, mean composite = 77.9, 100% at A or above). The 3.3x gap quantifies the adverse selection that quality-blind pooling permits. Intermediate pools confirm the monotonic relationship: MCO2 (0.713), NCT (0.601), kVCM (0.519). A full 34-segment systematic scan across pool configurations is reported in Extended Data.

[Figure 6: Lemons Index comparison across pool types. BCT (0.724), MCO2 (0.713), NCT (0.601), kVCM (0.519), CHAR (0.221), AAA-only (0.100).]

### 6.7 Counterfactual Quality Gating

To quantify the value of on-chain quality gating, we simulate what would have happened if historical pools had applied a `meetsGrade()` check at various thresholds.

Under a BBB quality gate (`meetsGrade(_, _, Grade.BBB)`), BCT's Lemons Index would drop from 0.724 to 0.405 -- a modelled reduction of 0.319. Only 2 of 43 credits (5%) would have been admitted. The result is dramatic but also illustrates a tradeoff: strict quality gating severely limits pool liquidity. NCT's Lemons Index would drop from 0.601 to 0.390, admitting 10 of 28 credits (36%). Klima kVCM would drop from 0.519 to 0.273, admitting 8 of 20 credits (40%).

CHAR's Lemons Index is unchanged under any gate up to AA (0.221), because all 12 of its constituent biochar credits already score at grade A or above. This confirms that CHAR's project-type allowlist achieves naturally what a quality gate would enforce.

We validated these counterfactual projections through an on-chain simulation using the Foundry framework. Sixteen credits with known composite scores were deposited into four `QualityGatedPool` instances configured with progressively stringent thresholds (ungated, BBB, A, AAA), generating 64 total deposit attempts. The ungated pool admitted all 16 credits (mean composite 60.94, LI = 25%). The BBB-gated pool rejected 4 credits, admitting 12 with mean composite 70.94 and LI = 0%. The A-gated pool admitted 8 credits (mean composite 81.39, LI = 0%). The AAA-gated pool admitted only 3 credits (mean composite 92.92, LI = 0%). In every gated pool, the `meetsGrade()` function correctly rejected all below-threshold credits and admitted all above-threshold credits, achieving 100% gate accuracy. The total gas expenditure across all 64 deposit attempts was approximately 26.4 million gas, confirming that quality-gated deposits remain economically viable on L2 infrastructure.

The core value proposition of ERC-CCQR is that `meetsGrade()` can replicate CHAR's quality profile for pools that accept diverse project types. A pool operator who sets `minGrade = Grade.A` would achieve adverse selection prevention comparable to CHAR's biochar-only allowlist while remaining open to high-quality CDR, biochar, methane destruction, and improved forest management credits.

### 6.8 Monte Carlo Weight Sensitivity

We assessed grade robustness to weight perturbation via Monte Carlo analysis (10,000 iterations), sampling weight vectors from a Dirichlet distribution with the co-benefits weight forced to zero. At moderate perturbation (concentration = 50), global robustness is 93.7%: the average credit retains its grade in 93.7% of samples. Five of 29 credits are fragile (stability below 90%), all located on grade boundaries (e.g., Plan Vivo agroforestry at 51.5% stability on the A/BBB boundary). Interior credits are stable; boundary credits are not. Per-credit stability data across three concentration levels (20, 50, 100) are reported in Extended Data Table ED5. Crucially, Climeworks Orca and Heirloom DAC achieve 100% stability at all concentration levels, confirming that the framework's headline finding -- engineered CDR dominates the top of the quality scale -- is robust to weight uncertainty.

### 6.9 Adversarial Testing

Five adversarial credits were designed to exploit specific attack vectors:

1. **Narrative washing.** A credit with inflated co-benefit scores but low removal and permanence scores. Correctly caught by the safeguards-gate: co-benefits carry zero weight, and the low removal/permanence scores determine the composite.

2. **Double counting.** A duplicate credit issued across two registries. The `doubleCounting` disqualifier fires, capping the grade at B regardless of dimension scores.

3. **Registry shopping.** A credit issued on an unrecognized registry. Low registry score plus the `noThirdParty` disqualifier caps the grade at BBB.

4. **Vintage arbitrage.** An ancient credit with inflated dimension scores. The vintage decay function pulls the composite below the target threshold.

5. **Biodiversity destruction.** A monoculture plantation with high carbon removal but documented habitat disturbance. The `biodiversityHarm` disqualifier fires, capping at BBB, per Zeng et al.'s finding that offset projects are associated with a 3.7% increase in habitat disturbance [33].

All five adversarial credits were correctly caught by both the automated framework and the independent LLM panel (5/5 detection rate).

### 6.10 Interface Generalization: Zero-Modification Reuse Across Three RWA Domains

The carbon-specific evaluation above demonstrates that the *scoring implementation* works. This subsection demonstrates that the *interface* generalizes: the same `meetsGrade()`, `isStale()`, and `ratingOf()` functions, with zero modification, gate quality for entirely different asset classes.

The critical architectural insight is that the ERC-CCQR *standard* (the query interface) is domain-agnostic, while the *implementation* (the seven carbon-specific dimensions, weights, and disqualifier flags) is domain-specific. This is exactly the separation that makes ERC-20 universal: the standard defines `balanceOf()` and `transfer()` without prescribing how supply is managed. Similarly, ERC-CCQR defines the quality query without prescribing what "quality" means in a given domain.

**Biodiversity credits.** `BiodiversityCreditGate` (`contracts/examples/BiodiversityCreditGate.sol`) gates biodiversity credit deposits -- for standards such as Verra SD VISta and Plan Vivo -- using the same boolean quality query. A biodiversity-specific rating implementation would replace the carbon dimensions with species richness (Shannon-Wiener index), habitat connectivity (Circuitscape graph-theoretic metrics), permanence of habitat protection covenants, conservation additionality, MRV quality (eDNA surveys, camera traps, satellite land-cover change), and registry credibility. The consumer contract does not need to know which dimensions underlie the composite; it asks "does this credit meet grade AA?" and receives a boolean answer.

**Renewable energy certificates.** `RenewableEnergyCertGate` (`contracts/examples/RenewableEnergyCertGate.sol`) applies the same pattern to RECs. RECs face analogous quality heterogeneity: a new-build solar farm providing grid additionality in a coal-heavy region is not equivalent to a legacy hydroelectric dam selling unbundled certificates. REC-specific dimensions would include generation source (technology tier), grid impact (locational marginal emission rates), temporal matching (annual vs. hourly 24/7 CFE per EnergyTag standards), additionality, vintage and delivery verification, and registry tracking (I-REC, TIGR, M-RETS, EU GoO). The consumer contract calls `meetsGrade()` without awareness of these internals.

**Generalization test results.** A Foundry test suite (`contracts/test/Generalization.t.sol`) deploys both gate contracts against a single `CarbonCreditRating` backend, sets ratings for dummy biodiversity and REC tokens, and verifies that: (i) high-quality assets pass their respective gates, (ii) low-quality assets are rejected, (iii) unrated assets are rejected by both gates, and (iv) a single rating contract simultaneously serves biodiversity, REC, and carbon consumers with different minimum grade thresholds. All seven generalization tests pass, confirming zero-modification interface reuse across three RWA domains.

---

## 7. Discussion

### 7.1 Broader Applicability and Downstream Utility

The generalization results in Section 6.10 are a proof of concept, not a ceiling. The `meetsGrade()` pattern is applicable to any tokenized asset class where quality heterogeneity creates information asymmetry: real estate (property condition, tenant quality), structured credit (tranche quality, collateral adequacy), ESG bonds (impact verification), and commodity-backed tokens (provenance, grade). The `compositeVarianceBps2` field for uncertainty quantification is relevant wherever rating confidence matters -- including financial credit ratings, where S&P and Moody's publish point estimates but not posterior distributions.

The insurance industry provides a concrete near-term use case. Oka, Howden, Lockton, and WTW have launched carbon credit insurance products (invalidation, reversal, non-delivery) that consume quality ratings as underwriting inputs [34]. The composite score plus P(grade) posterior is precisely the actuarial input these models require. This aligns with Cabiyo and Field's [35] argument that carbon markets should embrace imperfection through risk management rather than demanding perfection.

### 7.2 Limitations

Several limitations constrain the current findings:

**Oracle trust.** Rating accuracy depends on off-chain assessment quality. The "garbage in, garbage out" problem is not solved by on-chain transparency alone. The rating contract is only as trustworthy as its raters.

**Single-provider LLM panel.** The IRR study uses only Anthropic Claude models (Opus 4.6, Sonnet 4.6, Haiku 4.5). These models share training data and RLHF procedures. A multi-provider replication (GPT-5, Gemini 2.5 Pro, Llama, DeepSeek) is necessary to detect provider-specific biases. The kappa = 0.600 should be treated as a preliminary estimate with approximately +/-0.10 noise given the n = 29 sample size.

**Credit coverage.** The framework has been validated on 318 credits. Commercial agencies rate 4,400+ projects (MSCI) to 9,000+ (CarbonPlan OffsetsDB). The framework is validated on accuracy and reproducibility, not coverage.

**Weight calibration.** The weight vector has not yet been validated by a formal domain expert panel. Twenty experts have been identified for structured elicitation; consultation is in progress. The CCP calibration provides population-level validation, but individual weights may benefit from expert adjustment.

**Centralized bootstrapping.** The current deployment uses a single-owner rater with trusted-attester allowlist for the EAS adapter. True decentralization requires broader attestation ecosystem maturity and governance mechanisms beyond the scope of this prototype.

**Cookstove divergence.** The framework's Oxford-hierarchy-based scoring caps avoidance projects below grade A, diverging from commercial agencies that rate several cookstove projects at A or above. This is a deliberate normative design choice, but it limits comparability for avoidance-heavy portfolios.

**Gaussian approximation for grade probabilities.** The `compositeVarianceBps2` field enables P(grade >= threshold) computation via Gaussian CDF (Section 5.2), but the normality assumption has not been empirically validated against the actual distribution of composite scores. With only seven dimensions and bounded [0, 100] inputs, credits near grade boundaries may have asymmetric composite distributions that deviate from Gaussian. Monte Carlo validation using calibrated per-dimension score distributions is planned to quantify the approximation error and determine whether boundary-specific corrections (e.g., beta-distribution fitting or kernel density estimation) are warranted.

### 7.3 Ethical Considerations

The framework embeds normative assumptions. The weight vector prioritizes removal over avoidance, consistent with the Oxford Principles for Net Zero Aligned Carbon Offsetting [29]. Co-benefits are excluded from the integrity composite, a choice that may disadvantage community-development-focused projects. All normative parameters are documented and configurable: users can modify weights by changing a single JSON file and redeploying.

Quality rating may inadvertently legitimate low-quality credits by grading them (B-rated) rather than rejecting them entirely. The framework does not resolve the fundamental debate about whether offsets delay structural decarbonization [36].

### 7.4 Adoption Pathway

We envision a three-phase adoption pathway. Phase 1 (current): single-rater prototype deployed on Base Sepolia with Foundry tests and open-source artifact. Mainnet deployment (Phase 2) will proceed following: (i) expert weight validation with N >= 10 respondents via Best-Worst Scaling, (ii) multi-provider IRR replication achieving cross-provider kappa >= 0.4, and (iii) integration commitment from at least one pool operator or registry. Phase 2 targets production deployment on Base mainnet with integration into Klima Protocol 2.0 retirement flow and Toucan CHAR fee overlay. Phase 3: decentralized multi-rater attestation via EAS with registry-level attesters (Verra, Gold Standard, Puro, Isometric) publishing ratings through the trusted-attester framework.

---

## 8. Conclusion

ERC-20 made balances composable. ERC-721 made ownership composable. ERC-4626 made vault shares composable. ERC-CCQR makes *quality* composable. The `meetsGrade()` primitive -- the quality analogue of `balanceOf()` -- enables any DeFi protocol to gate deposits, retirements, or fee structures on a continuous quality threshold via a single `staticcall`, at zero gas overhead. No prior real-world asset standard stores both composite score and variance on-chain; ERC-CCQR's distributional scoring makes grade probability computation possible without additional oracle calls.

We validated the standard against the hardest test case available: voluntary carbon credits, where Toucan BCT's quality-blind pooling produced a Lemons Index of 0.724 and commercial rating agencies agree at Spearman +0.009. Against 318 credits, the standard recovers the ICVCM quality threshold (1.99-grade gap, Cohen's d = 1.80), correlates with commercial ratings at Spearman +0.901 across 12 project types, achieves reproducible inter-rater reliability (Fleiss' kappa = 0.600, ICC = 0.993), and catches all adversarial attack vectors. The interface generalizes without modification to biodiversity credits and renewable energy certificates, with seven passing Foundry tests confirming zero-modification reuse across three RWA domains.

Carbon credits are the canary in the coal mine for tokenized real-world asset quality. The patterns documented here -- adverse selection, information asymmetry, quality-blind pooling, market-for-lemons collapse -- will recur in every asset class that moves on-chain without quality infrastructure. Real estate tokens, structured credit tranches, ESG bonds, commodity-backed instruments: each will face the same question that BCT failed to answer. `meetsGrade()` provides the answer, and the composability cascade it enables -- where thousands of protocols inherit quality signals from the rating layer, just as thousands of protocols inherited balance queries from ERC-20 -- is how tokenization resolves rather than amplifies the information asymmetries of the physical world.

Future work includes expert-validated weight calibration, multi-provider LLM panel replication, production deployment on Base mainnet with Klima Protocol 2.0 and Toucan CHAR integration, EAS schema registration with trusted-attester onboarding for major registries, and dynamic re-rating pipelines with digital MRV inputs from satellite and IoT sources.

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

[52] Wen, A. An open, distributional quality framework for voluntary carbon credits: validation against regulatory thresholds and commercial ratings. Companion methods paper, submitted to *Environmental Research Letters* (2026).

[53] Wen, A. Blockchain transparency without quality signals accelerates adverse selection in carbon markets: depositor-level evidence from tokenized credit pools. Companion empirical paper, submitted to *Nature Communications* (2026).
