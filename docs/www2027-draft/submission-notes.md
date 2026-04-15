# WWW 2027 Submission Notes

## Suggested Track

**Primary:** Web3 and Decentralized Systems

**Rationale:** The paper presents ERC-CCQR, a composable on-chain quality rating standard for tokenized real-world assets, validated through Foundry smart contract tests on Base L2. The core contribution -- the `meetsGrade()` primitive as a quality analogue of `balanceOf()` -- is a DeFi composability pattern. The empirical validation against carbon credits is the use case; the systems contribution is the interface standard and its composability cascade across deposit pools, retirement gates, and fee overlays.

**Alternative:** If the conference programme includes a "Real-World Assets" or "Tokenization" track, this paper would also be a strong fit given its focus on bridging off-chain quality assessment to on-chain enforcement across carbon credits, biodiversity credits, and renewable energy certificates.

---

## Suggested Reviewers

1. **Fan Zhang** -- Assistant Professor, Yale University, Department of Computer Science. Research on blockchain systems, oracle design, and decentralized finance infrastructure. Published on blockchain oracle mechanisms and MEV. Relevant because ERC-CCQR is architecturally positioned as a quality oracle with novel staleness and threshold-query patterns distinct from price oracles (Chainlink, Pyth, UMA).

2. **Ari Juels** -- Jacobs Technion-Cornell Professor, Cornell Tech / Technion; Co-Director, Initiative for CryptoCurrencies and Contracts (IC3). Co-creator of Chainlink. Published extensively on oracle design, trusted execution, and decentralized data feeds. His perspective on ERC-CCQR's deviation from the price-oracle paradigm (ordinal grades vs. continuous prices, methodology versioning vs. heartbeat staleness) would be valuable.

3. **Lewis Gudgeon** -- Research Scientist, Imperial College London / Gauntlet Networks. Published on DeFi composability, protocol risk, and adverse selection in automated market makers (including foundational work on sandwich attacks and liquidation mechanisms). His expertise in DeFi protocol design and adverse selection mechanics directly relates to the Lemons Index analysis and quality-gated pool patterns.

---

## Conflict of Interest Statement

The author declares no conflicts of interest. The ERC-CCQR standard is open-source under MIT licence and the author has no financial relationship with any carbon credit rating agency, registry, or DeFi protocol discussed in the paper. Toucan Protocol, KlimaDAO, Moss, and other protocols analysed are evaluated using publicly available data. The author has no equity, advisory, or employment relationship with any entity whose products are rated by the framework.

---

## Data and Code Availability Statement

All source code is open-source and available at https://github.com/Adeline117/carbon-neutrality under an MIT licence. Specifically:

- **Smart contracts:** Solidity 0.8.24 source for `CarbonCreditRating.sol`, `QualityGatedPool.sol`, `KlimaRetirementGate.sol`, `CHARQualityOverlay.sol`, `CarbonCreditRatingEASAdapter.sol`, `BiodiversityCreditGate.sol`, and `RenewableEnergyCertGate.sol` are in `contracts/`.
- **Foundry test suite:** All tests (unit tests, gas benchmarks, generalization tests, adversarial tests, counterfactual simulation) are reproducible via `forge test` with Foundry. Test files are in `contracts/test/`.
- **Scoring engine:** Python scoring implementation (`score.py`) produces bit-identical results to the Solidity contract. No external dependencies beyond the Python standard library.
- **Scoring rubrics:** Machine-readable JSON rubrics are in `data/scoring-rubrics/`.
- **Evaluation data:** The 318-credit batch dataset, 29-credit pilot dataset, LLM panel raw outputs, and all rank correlation datasets are included in the repository.
- **Gas benchmarks:** All gas measurements were obtained via `forge test --gas-report` on Base Sepolia and are reproducible.

---

## Supplementary Materials List

### Main Text (within page limit)

**Tables:**
- Table 1: Complete weight vector, grade band definitions, and disqualifier cap lattice
- Table 2: Gas benchmarks for all ERC-CCQR operations
- Table 3: Comparison of on-chain carbon protocols and their quality mechanisms
- Table 4: Spearman rank correlation matrix (framework vs. BeZero, cross-type n=27)
- Table 5: Positioning matrix (ERC-CCQR vs. CATchain-R, PACT, Toucan CHAR, Hypercerts)
- Table 6: Oracle and compliance interface comparison (Chainlink, UMA, Pyth, ERC-3643, ERC-CCQR)

**Figures:**
- Figure 1: ERC-CCQR architecture diagram (three compliance levels)
- Figure 2: Sequence diagrams for three composability patterns
- Figure 3: Gas cost breakdown (quality gate overhead vs. base transaction costs)
- Figure 4: CCP calibration violin plot (CCP-eligible vs. non-CCP, n=318)
- Figure 5: Per-dimension Fleiss' kappa bar chart with Landis-Koch bands
- Figure 6: Lemons Index comparison across pool types

### Appendix / Supplementary

- Extended Data Table ED1: Per-credit scoring details for all 29 pilot credits
- Extended Data Table ED2: Full 34-segment Lemons Index scan results
- Extended Data Table ED3: Leave-one-out rank correlation stability analysis (27 jackknife samples)
- Extended Data Table ED4: Counterfactual quality gating results for all six pools at all thresholds
- Extended Data Table ED5: Per-credit Monte Carlo weight sensitivity (stability at concentration 20, 50, 100)
- Extended Data Figure ED1: Bootstrap distribution of Spearman rho (10,000 resamples)
- Extended Data Figure ED2: Dirichlet weight perturbation grade stability heatmap
- Extended Data Figure ED3: Adversarial credit detection results (5/5 attack vectors)
- Appendix A: Full ERC-CCQR Solidity interface specification
- Appendix B: EAS attestation schema definition
- Appendix C: Per-dimension rubric definitions (all seven dimensions, score ranges, data sources)
- Appendix D: Off-chain/on-chain equivalence proof (Climeworks Orca test vector)
