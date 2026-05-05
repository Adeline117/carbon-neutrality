# ERC-CCQR: The Missing Composability Primitive for Real-World Asset Quality

**Abstract.** ERC-20 made token balances composable; ERC-721 made ownership composable; ERC-4626 made vault shares composable. No standard exists for making the *quality* of a tokenized real-world asset composable. As trillions of dollars in real-world assets move on-chain -- from BlackRock's BUIDL fund to carbon credits to renewable energy certificates -- this missing primitive determines whether tokenization amplifies or resolves the information asymmetries inherent in heterogeneous asset classes. We present ERC-CCQR, a composable on-chain quality rating standard whose core primitive, `meetsGrade(address token, uint256 id, Grade min) -> bool`, is the quality analogue of `balanceOf()`: a zero-gas view function that any protocol can call via `staticcall` to determine whether a specific asset meets a quality threshold before accepting it. We validate the standard against the hardest possible test case -- voluntary carbon credits, an asset class where a companion study [52] documents design-enabled adverse selection across 509 depositors and 28,897 redeemers and validates the underlying quality framework against regulatory thresholds and commercial ratings. Against 318 credits, the standard achieves a 1.99-grade gap between CCP-eligible and non-CCP credits (Cohen's d = 1.87) and counterfactual Lemons Index reduction from 0.679 to 0.405 under quality gating. We then demonstrate that the interface generalizes without modification to biodiversity credits and renewable energy certificates, with seven passing Foundry tests confirming zero-modification reuse across three RWA domains. The standard stores both composite score and variance on-chain (`compositeVarianceBps2`), enabling probabilistic grade computation -- a first for any real-world asset token standard.

---

## 1. Introduction

### 1.1 The Quality Composability Gap in Tokenized Real-World Assets

The tokenization of real-world assets (RWAs) is accelerating. BlackRock's BUIDL fund holds over $1.7 billion in on-chain U.S. Treasuries; Ondo Finance, Centrifuge, and Maple Finance have brought structured credit, receivables, and fixed-income products on-chain; voluntary carbon credits, biodiversity credits, and renewable energy certificates are traded as ERC-20 and ERC-721 tokens across Ethereum, Polygon, and Base. Estimates for the total addressable market range from $4 trillion (Boston Consulting Group, 2025) to $16 trillion (McKinsey, 2030 projection).

What is missing is the infrastructure for querying the *quality* of those assets once they arrive.

ERC-20 answers "how much does this address hold?" ERC-721 answers "who owns this specific token?" ERC-4626 answers "what is my share of this vault worth?" No standard answers the question that matters most for heterogeneous real-world assets: *"Is this specific asset good enough?"* A DeFi pool that accepts tokenized carbon credits cannot ask whether a given credit is high-integrity or a legacy junk offset. A lending protocol that collateralizes renewable energy certificates cannot distinguish a new-build solar REC providing grid additionality from a legacy hydro certificate with no incremental climate impact.

The absence of this primitive means that tokenization *amplifies* the information asymmetries already present in these markets. When all eligible assets are treated as fungible, Akerlof's lemons dynamic [9] is not merely theoretical: low-quality asset holders deposit aggressively into single-price pools, high-quality holders withhold supply, and the pool's average quality degrades until the market collapses.

### 1.2 Carbon Credits as the Hardest Test Case

We validate the standard against voluntary carbon credits -- the asset class where the quality composability gap is widest and the failure mode most documented.

A companion paper [52] provides the first complete on-chain forensics of a tokenized market collapse alongside the validated quality framework: Toucan Protocol's BCT pool on Polygon, where 69.1% of deposited tonnage was CDM-era renewable energy credits with near-zero additionality, five wallets extracted 1.55 million tonnes of high-demand credits, and 9.6 million tonnes of B-grade credits remain stranded on-chain. The same nature-based tokens were 100% redeemed from BCT but only 28.5% from quality-gated NCT, demonstrating that pool design -- not credit quality -- determines asset fate. The quality framework underpinning these findings is validated against the ICVCM Core Carbon Principles label (1.99-grade separation, Cohen's d = 1.87, n = 318) and commercial rating agencies (Spearman +0.901 vs. BeZero, n = 27, 12 project types), with inter-rater reliability of Fleiss' kappa = 0.600 and ICC = 0.993.

If a composable quality primitive works for carbon credits -- the worst case -- it works for any tokenized real-world asset.

### 1.3 Contributions

This paper makes five contributions:

1. **A composable quality standard for real-world asset tokens.** We define ERC-CCQR, a three-level compliance hierarchy: Level 1 (boolean quality query via `meetsGrade` and `isStale`), Level 2 (full `Rating` struct with composite score, variance, and provenance metadata), and Level 3 (decentralized attestation relay via the Ethereum Attestation Service). The interface is domain-agnostic; only the scoring implementation is domain-specific.

2. **The `meetsGrade()` primitive -- the quality analogue of `balanceOf()`.** A zero-gas view function that encapsulates grade lookup, staleness check, and threshold comparison in a single `staticcall`.

3. **Distributional on-chain scoring with uncertainty quantification.** The first real-world asset token standard to store both a composite score and its variance on-chain (`compositeVarianceBps2`), enabling probabilistic grade computation via Gaussian CDF without additional oracle calls.

4. **The Lemons Index for DeFi pool health.** A quantitative adverse-selection metric, L(pool) = 1 - (mean composite / 100), applied to five real carbon credit pools and counterfactual quality-gated scenarios.

5. **Empirical validation plus cross-domain generalization.** CCP calibration (1.99-grade gap), counterfactual quality gating (BCT LI reduction from 0.679 to 0.405), adversarial testing (100% disqualifier recall), and zero-modification interface reuse across biodiversity credits and renewable energy certificates (seven passing generalization tests).

---

## 2. Background and Related Work

### 2.1 On-Chain Carbon Protocols

The first wave of on-chain carbon markets (2021--2023) focused on bridging off-chain registry credits onto EVM-compatible blockchains. Toucan Protocol bridged Verra credits to Polygon as TCO2 tokens, pooling them into fungible BCT and NCT pools [5]. Moss bridged Amazon conservation credits into the MCO2 token [10]. Both treated quality as an implicit property of the pool's eligibility filter rather than an explicit, queryable attribute of individual credits.

The second wave (2024--2026) introduced more sophisticated mechanisms. Toucan's CHAR pool on Base uses a binary project allowlist (`checkEligible()`) restricting deposits to Puro-certified biochar projects. Klima Protocol 2.0 migrated to Base with kVCM and K2 tokens, applying treasury-level quality curation. Carbonmark launched direct on-chain credit issuance on Polygon. However, none of these protocols exposes a callable quality-query interface usable by arbitrary downstream contracts.

[Table 3: Comparison of on-chain carbon protocols and their quality mechanisms.]

### 2.2 Off-Chain Quality Frameworks

The ICVCM Core Carbon Principles (CCP) framework represents the most authoritative off-chain quality signal. CCP provides binary classification rather than continuous scoring, and the label is not queryable on-chain. Commercial rating agencies (BeZero, Sylvera, Calyx Global, MSCI) produce proprietary assessments but show significant inter-agency disagreement: the mean pairwise Spearman correlation is +0.009 [13]. None provides a smart contract interface. A companion paper [52] presents the first open framework to simultaneously achieve credit-level scoring, distributional uncertainty, and published inter-rater reliability.

### 2.3 On-Chain Quality and Credibility Systems

CATchain-R introduces a blockchain-based carbon registry with an organizational credibility index [16]. PACT combines remote sensing with econometric baselines on Tezos [17]. JPMorgan's Kinexys platform introduced registry-layer tokenization via API [18]. The Hypercerts Foundation operates an EAS-based evaluator registry on Base, Optimism, and Celo [19]. None of these systems exposes a continuous quality threshold queryable by arbitrary consuming contracts.

### 2.4 Adverse Selection in Carbon Markets

Akerlof's lemons model predicts that when buyers cannot distinguish quality, low-quality goods drive out high-quality goods [9]. Manshadi, Monachou, and Morgenstern developed the first formal adverse-selection model specific to VCMs [20]. A companion paper [52] documents the complete empirical realization of this dynamic in the BCT pool.

### 2.5 DeFi Composability Standards

ERC-20's `balanceOf()` established the paradigm for composable on-chain primitives [23]. ERC-721 extended this to non-fungible tokens [24]. ERC-4626 standardized tokenized vault operations [25]. No standard currently exists for querying a quality attribute of a token. ERC-CCQR fills this gap.

### 2.6 Oracle and Compliance Interface Comparison

ERC-CCQR's `meetsGrade()` and `ratingOf()` differ from existing on-chain oracle interfaces in three novel design elements: (i) the threshold-query pattern returning a boolean for a caller-specified ordinal threshold; (ii) a dual staleness model combining time expiry with methodology versioning; and (iii) a categorical disqualifier cap lattice overriding continuous scores with binary safety flags. Three elements are adapted from existing patterns: the `view`-function composability model follows Chainlink and ERC-3643; the on-chain uncertainty field adapts Pyth's `conf` design; and the trusted-rater allowlist follows ERC-3643's trusted-issuer registry.

[Table 5: Positioning matrix comparing ERC-CCQR against related systems across six capabilities.]
[Table 6: Oracle and compliance interface comparison with Chainlink, UMA, Pyth, ERC-3643.]

---

## 3. ERC-CCQR Standard Specification

### 3.1 Design Principles

**Minimality.** Level 1 compliance requires only two functions (`meetsGrade` and `isStale`).

**Progressive disclosure.** Three compliance levels: Level 1 for boolean quality gating, Level 2 for distributional scoring and provenance, Level 3 for decentralized attestation via EAS.

**Zero-gas reads.** All query functions are `view`, executed via `staticcall` at zero marginal gas cost.

**Grade universality.** The six-tier AAA-through-B grade enum maps to the letter-grade convention used by Moody's, S&P, BeZero, Sylvera, Calyx, and MSCI.

**Uncertainty as a first-class citizen.** The `compositeVarianceBps2` field stores variance alongside the point estimate.

### 3.2 Grade Enum and Interface Definitions

```
enum Grade { B, BB, BBB, A, AA, AAA }
```

**Level 1 (Boolean Quality Query).**
```
function meetsGrade(address creditToken, uint256 tokenId,
    Grade minGrade) external view returns (bool);
function isStale(address creditToken, uint256 tokenId)
    external view returns (bool);
```

**Level 2 (Full Rating Struct).**
```
struct Rating {
    uint16 compositeBps;          // 0--10000
    uint32 compositeVarianceBps2; // Variance in bps^2
    Grade nominalGrade;           // Before disqualifier caps
    Grade finalGrade;             // After disqualifier caps
    uint64 lastUpdatedAt;
    uint64 expiresAt;             // 0 = never
    uint16 methodologyVersion;
    bytes32 evidenceHash;
    address attestedBy;
}
```

**Level 3 (EAS Relay).**
```
function relay(bytes32 attestationUid, address creditToken,
    uint256 tokenId) external;
```

[Figure 1: ERC-CCQR architecture diagram showing three compliance levels.]

### 3.3 Scoring Methodology

Seven dimensions are encoded as a `DimensionScores` struct. The weight vector, expressed in basis points summing to 10,000, reflects the safeguards-gate design. Full weight calibration and validation are detailed in the companion paper [52].

[Table 1: Weight vector, grade bands, and disqualifier cap lattice.]

### 3.4 Staleness Detection and Methodology Versioning

The `isStale()` function checks two conditions: time expiry and methodology version mismatch. When the methodology version is bumped, all existing ratings become stale in O(1) time.

### 3.5 Security Properties

**Re-entrancy safety.** View functions with no state mutation.
**Disqualifier integrity.** `meetsGrade()` compares against `finalGrade` (post-disqualifier).
**Checks-effects-interactions.** QualityGatedPool calls `meetsGrade()` before `transferFrom()`.
**Methodology version gating.** Legacy ratings are automatically stale.
**Attester trust boundary.** EAS adapter restricts relay to allowlisted attester addresses.

### 3.6 Oracle Trust Architecture

We position ERC-CCQR within a three-stage trust progression:

**Stage 1: Single authorized rater** (current). Trust is centralized but transparent: ratings, methodology versions, and evidence hashes are immutably recorded.

**Stage 2: Multi-rater consensus via EAS** (partially implemented). K-of-n consensus from independent attesters. The inter-agency disagreement documented in [52] (mean Spearman +0.009) suggests consensus thresholds must be calibrated per credit type.

**Stage 3: Staked rater with slashing** (design space). Economic incentive alignment via bonds. Not implemented.

---

## 4. Composability Patterns

Three DeFi integration patterns demonstrate `meetsGrade()` as a reusable building block. All target Base L2.

### 4.1 Quality-Gated Deposit Pool

```
function deposit(address creditToken, uint256 tokenId) external {
    require(ratingContract.meetsGrade(
        creditToken, tokenId, minGrade),
        "Below minimum grade");
    // transfer credit into pool
}
```

Gas overhead: ~19,244 gas for the `staticcall`.

### 4.2 Additional Patterns

**Retirement quality gate.** KlimaRetirementGate gates kVCM retirement with configurable `minRetirementGrade`.

**Quality-based fee discount.** CHARQualityOverlay reads the full `Rating` struct and returns grade-tiered fee discounts (5% for AAA, 3% for AA, 1% for A).

### 4.3 EAS Attestation Relay

The adapter verifies provenance, decodes attestation data, and writes ratings. Structurally compatible with the Hypercerts evaluator registry pattern [19].

[Figure 2: Sequence diagrams for three composability patterns.]

---

## 5. Scoring Framework

### 5.1 Seven Weighted Dimensions

The framework evaluates carbon credits across seven dimensions, each scored 0--100. Full dimension definitions, rubric design rationale, and validation against the ICVCM CCP label and commercial rating agencies are detailed in the companion paper [52].

### 5.2 Distributional Scoring and Uncertainty Quantification

ERC-CCQR stores both composite score and variance on-chain. Per-dimension standard deviations are empirically calibrated from the three-model LLM panel IRR study [52]. The composite variance is propagated via:

Var(C) = sum(w_i^2 * sigma_i^2)

Any downstream consumer can compute P(grade >= threshold) via Gaussian CDF. Monte Carlo validation on 10 boundary credits confirms the Gaussian approximation is accurate (maximum absolute error 3.7%, mean 1.1%).

### 5.3 Off-Chain/On-Chain Scoring Invariant

The Python scoring engine and Solidity contract produce bit-identical results, enforced by Foundry tests.

---

## 6. Evaluation

### 6.1 Gas Benchmarks

[Table 2: Gas benchmarks for all ERC-CCQR operations.]

The `meetsGrade()` call at 19,244 gas adds ~30--40% to an ERC-20 `transfer()`, ~10--15% to a Uniswap V3 swap, and ~8--10% to an Aave V3 `supply()`. Read operations are free via `staticcall`.

### 6.2 Scalability Analysis

Read scalability is O(1) via mapping-based storage. Write scalability: a full re-rating of 318 credits requires ~53 million gas; methodology-version staleness handles incremental updates gracefully.

### 6.3 Scoring Framework Validation

The quality scores underlying all empirical results were validated against three independent external benchmarks. Full protocols and statistical details are in the companion paper [52]; key results are summarized here to establish that the on-chain scores are credible.

[Table 3: Framework validation summary. Columns: Validation test, Metric, Value, Benchmark/interpretation.

| Validation test | Metric | Value | Benchmark |
|----------------|--------|-------|-----------|
| CCP calibration (n=318) | Grade gap | 1.99 levels | Matches Calyx Global's independent measurement |
| | Cohen's d | 1.87 [1.68, 2.11] | Large effect (>0.8) |
| | CLES | 91.4% | CCP credit outscores non-CCP 91% of the time |
| BeZero correlation (n=27, 12 types) | Spearman rho | +0.901 [+0.783, +0.959] | Exceeds inter-agency mean (+0.009) |
| | Exact grade match | 52% | 100% within +/-1 grade |
| | LOO stability | +0.889 to +0.922 | No single project drives result |
| Inter-rater reliability (n=29) | Fleiss' kappa | 0.600 | Moderate-to-substantial (Landis-Koch) |
| | ICC(2,k) | 0.993 | Near-perfect composite reliability |
| Multi-provider replication (n=5) | Cross-provider kappa | 0.647 | Exceeds single-provider baseline (+0.600) |
| Weight robustness (10,000 MC draws) | Global grade stability | 93.7% | 5 fragile credits, all on grade boundaries |
| Removal-type sensitivity | CCP gap retention | 101.4% | Separation not driven by removal-type dimension |
| Adversarial testing (n=5) | Detection rate | 5/5 (100%) | All attack vectors caught |
]

Three results are particularly relevant for the on-chain standard. First, the removal-type sensitivity check ensures that ERC-CCQR's grade assignments are not mechanically determined by a single dimension: removing the highest-weighted dimension preserves the full quality gradient. Second, the Monte Carlo weight robustness means that grades are stable to weight perturbation --- a practical requirement for on-chain scores that cannot be cheaply re-rated. Third, the multi-provider replication (GPT-5, Gemini 2.5 Pro, Llama 4 Maverick) confirms that rubric reproducibility extends beyond a single model family, addressing the concern that LLM-derived scores might reflect provider-specific biases.

### 6.4 Adverse Selection Prevention: Lemons Index

BCT's LI = 0.679 versus CHAR's LI = 0.221: a 3.1x gap quantifying the adverse selection that quality-blind pooling permits. Intermediate pools confirm the monotonic relationship: MCO2 (0.713), NCT (0.601), kVCM (0.519). A full 34-segment systematic scan is reported in [52].

### 6.5 Counterfactual Quality Gating

Under a BBB gate, BCT's LI drops from 0.679 to 0.405 (admitting 12 of 161 tokens). An on-chain Foundry simulation validated these projections: 16 credits across 4 pools, 64 deposit attempts, 100% gate accuracy, ~26.4 million gas total. The core value proposition: `meetsGrade()` can replicate CHAR's quality profile for pools accepting diverse project types.

### 6.6 Adversarial Testing

Five adversarial credits (narrative washing, double counting, registry shopping, vintage arbitrage, biodiversity destruction) were all correctly caught by both the automated framework and the LLM panel (5/5 detection rate).

### 6.7 Interface Generalization

The `meetsGrade()` interface generalizes without modification to biodiversity credits and renewable energy certificates. A Foundry test suite deploys `BiodiversityCreditGate` and `RenewableEnergyCertGate` against a single `CarbonCreditRating` backend. All seven generalization tests pass.

[Table 4: Domain-specific dimension mapping (carbon, biodiversity, REC).]

---

## 7. Discussion

### 7.1 Broader Applicability

The `meetsGrade()` pattern applies to any tokenized asset class with quality heterogeneity: real estate, structured credit, ESG bonds, commodity-backed tokens. The insurance industry provides a near-term use case: carbon credit insurers consume quality ratings as underwriting inputs, and P(grade) posteriors translate directly into probability-of-loss estimates.

### 7.2 Limitations

**Oracle trust.** Rating accuracy depends on off-chain assessment quality.
**Credit coverage.** Validated on 318 credits versus 4,400+ rated by MSCI.
**Weight calibration.** Not yet validated by a formal expert panel; 20 experts identified for structured elicitation.
**Centralized bootstrapping.** Current deployment uses single-owner rater.
**Cookstove divergence.** The Oxford-hierarchy-based scoring caps avoidance projects below grade A.

### 7.3 Adoption Pathway

Phase 1 (current): single-rater prototype on Base Sepolia. Phase 2: mainnet deployment with Klima 2.0 and Toucan CHAR integration. Phase 3: decentralized multi-rater attestation via EAS.

---

## 8. Conclusion

ERC-CCQR makes *quality* composable. The `meetsGrade()` primitive enables any DeFi protocol to gate deposits, retirements, or fee structures on a continuous quality threshold via a single `staticcall`, at zero gas overhead. The standard stores both composite score and variance on-chain; no prior RWA standard provides distributional quality estimates.

Validated against the hardest test case -- voluntary carbon credits where a companion study [52] documents complete adverse selection dynamics with Spearman +0.901 correlation against commercial ratings -- the standard generalizes without modification to biodiversity credits and renewable energy certificates.

The patterns documented here -- adverse selection, quality-blind pooling, market-for-lemons collapse -- will recur in every asset class that moves on-chain without quality infrastructure. `meetsGrade()` provides the answer.

The standard, reference implementation, test suite, scoring engine, and all evaluation data are available under MIT license at https://github.com/Adeline117/carbon-neutrality.

---

## References

[1] BeZero Carbon. Rating methodology. https://bezerocarbon.com, 2023.
[2] Sylvera. State of Carbon Credits 2025. https://sylvera.com, 2025.
[3] Calyx Global. Carbon credit ratings. https://calyxglobal.com, 2024.
[4] Calel, R., et al. Systematic assessment of emission reductions. *Nat. Commun.*, 2024.
[5] Toucan Protocol. BCT and CHAR pool contracts. https://toucan.earth, 2022--2025.
[6] Toucan Protocol. CHAR pool on Base. Binary allowlist gating, 2025.
[7] Klima Protocol 2.0. kVCM on Base. https://klimadao.finance, 2026.
[8] Zhou, C., et al. Harnessing Web3 on carbon offset market. *IEEE Wirel. Commun.*, 30(5):104--111, 2023.
[9] Akerlof, G. A. The market for "lemons". *Q. J. Econ.*, 84(3):488--500, 1970.
[10] Moss. MCO2 token. https://moss.earth, 2022.
[11] ICVCM. CCP impact report. https://icvcm.org, 2025.
[12] MSCI. State of integrity in the global carbon-credit market, 2025.
[13] Carbon Market Watch. Assessing and comparing carbon credit rating agencies, 2023.
[14] CCQI. Methodology v3.0. EDF, WWF, Oeko-Institut, 2024.
[15] Renoster. Mercury Rubric. https://renoster.co, 2025.
[16] Gao, H. O. and Liu, X. CATchain-R. *npj Clim. Action*, 2026.
[17] Jaffer, S., et al. PACT carbon stablecoin. *IEEE ICBC*, 2024.
[18] JPMorgan Kinexys. Carbon markets reimagined, 2025.
[19] Hypercerts Foundation. EAS-based evaluator registry. https://hypercerts.org, 2025.
[20] Manshadi, V., et al. Offsetting carbon with lemons. *SSRN*, 2025.
[21] Berg, F., et al. The market for voluntary carbon offsets. *SSRN*, 2025.
[22] Trencher, G., et al. Demand for low-quality offsets. *Nat. Commun.*, 2024.
[23] Vogelsteller, F. and Buterin, V. ERC-20. EIP, 2015.
[24] Entriken, W., et al. ERC-721. EIP, 2018.
[25] ERC-4626. Tokenized vault standard. EIP, 2022.
[26] Ku, H. H. Propagation of error formulas. *J. Res. NBS*, 70C(4):263--273, 1966.
[27] Ethereum Attestation Service (EAS). https://attest.sh.
[28] Coglianese, C. and Giles, C. Auditors can't save carbon offsets. *Science*, 389(6733), 2025.
[29] Allen, M. R., et al. Oxford Principles for Net Zero Aligned Carbon Offsetting, 2020.
[30] Calyx Global. Are carbon credit quality indicators delivering?, 2025.
[31] Bootstrap rank correlation analysis. n = 27, rho = +0.901.
[32] Landis, J. R. and Koch, G. G. Observer agreement. *Biometrics*, 33(1):159--174, 1977.
[33] Zeng, Y., et al. Carbon markets and biodiversity. *Nat. Rev. Biodivers.*, 2026.
[34] Oka. Carbon credit insurance. https://carboninsurance.co, 2025.
[35] Cabiyo, B. and Field, C. B. Embracing imperfection. *PNAS Nexus*, 4(5):pgaf091, 2025.
[36] Cheong, B. C. Paradox and fallacy of global carbon credits. *Anthropocene Sci.*, 4:72--83, 2025.
[52] Wen, A. On-chain forensics reveal adverse selection in the first tokenized carbon market. *Nat. Commun.* (2026).
