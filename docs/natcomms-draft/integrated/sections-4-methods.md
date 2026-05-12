# Methods

**Paper**: "Adverse selection in tokenized carbon markets: who profited from the first pool collapse"

---

## Data collection

We collected all deposit transactions to the Toucan Protocol BCT pool contract on the Polygon blockchain using a Polygon RPC endpoint. We identified {{composition.n_deposits}} deposit transactions spanning the period from BCT's launch in October 2021 to the effective cessation of new deposits in late 2022, mapping to {{composition.n_projects}} unique VCS project identifiers (345 unique TCO2 token addresses) and approximately 22 million tonnes of tokenized carbon credits. For each deposit, we recorded: transaction hash, block number and timestamp, depositor address, TCO2 token contract address, Verra VCS project identifier, vintage year, and tonnage. Project identifiers were cross-referenced against the Verra registry to obtain methodology category, country of origin, and CCP eligibility status.

**Project classification.** Each project was classified into one of eleven methodology categories based on the Verra registry entry: renewable energy (grid-connected wind, hydro, solar; CDM methodologies AMS-I.D, ACM0002), fossil fuel switching, waste management and methane capture, REDD+ (VM0007, VM0009, VM0015), afforestation/reforestation (ARR), industrial gas destruction, improved forest management (IFM), energy efficiency, industrial processes, agriculture, and cookstoves. Pool-level composition statistics were computed with tonnage weighting.

**NCT data.** We collected all 708 deposit events from the Toucan NCT pool on the same Polygon blockchain over the same block range. NCT restricts deposits to AFOLU credits with vintage $\geq$2012, functioning as a minimal quality gate on project type. NCT and BCT share identical protocol infrastructure and blockchain substrate.

**Price data.** Daily BCT-USDC prices were obtained from the DeFi Llama API for the Polygon SushiSwap BCT-USDC pair (828 observations, October 2021 -- July 2024).

## Quality scoring framework

We developed a composite quality scoring framework evaluating six active dimensions on a 0--100 scale: removal type hierarchy (weight 0.250), additionality (0.200), MRV grade (0.200), permanence (0.175), vintage year (0.100), and registry and methodology quality (0.075). Initial weights were derived from the Oxford Offsetting Principles and the ICVCM CCP Assessment Framework. A pilot Best-Worst Scaling expert panel ($n$ = 5) confirmed consistency with our weights (Spearman $\rho$ = +0.814). Monte Carlo perturbation (10,000 Dirichlet-sampled weight vectors) confirms 93.7% grade stability. The composite was computed as $C = \sum_{i} w_i \times s_i$ and mapped to letter grades: AAA ($\geq$90), AA ($\geq$75), A ($\geq$60), BBB ($\geq$45), BB ($\geq$30), B (<30). Seven disqualifier conditions cap maximum grades regardless of composite score. Co-benefits was assigned zero weight to avoid amplifying adverse selection through co-benefit narratives. The Pool Quality Deficit (PQD = $1 - \bar{C}/100$) quantifies tonnage-weighted quality degradation per pool. Full scoring details, distributional scoring model, extended scoring procedures, and sensitivity analyses are provided in Supplementary Methods.

## Base-rate comparison

BCT's renewable energy share was compared against the Verra VCS base rate (central estimate 37%, sensitivity range 26--48%, from MSCI and Ecosystem Marketplace reports). The selection coefficient $S = f_{\text{BCT,renewable}} / f_{\text{VCS,renewable}}$ was tested via exact binomial test, with account-clustered robustness (permutation, HHI-adjusted, and bootstrap tests; see Supplementary Methods).

## Difference-in-differences

A deposit-level DiD panel pooling all 1,895 events (1,187 BCT + 708 NCT) tested whether BCT's quality trajectory diverged from NCT's:

$$\text{quality}_i = \beta_0 + \beta_1 \cdot \text{BCT}_i + \beta_2 \cdot \text{PostTerra}_i + \beta_3 \cdot (\text{BCT} \times \text{PostTerra})_i + \varepsilon_i$$

where $\text{PostTerra}_i$ indicates deposits after the Terra/LUNA collapse (May 2022). Standard errors were cluster-robust at the TCO2 token level (349 clusters) with small-sample correction. Robustness: permutation test (10,000 iterations), Bayesian bootstrap, and continuous-time specification. A compositional DiD (binary renewable outcome) provided a framework-free test of the same divergence.

## Redemption analysis

Redemptions were identified from ERC-20 Transfer events where the BCT pool contract appears as the sender, yielding {{redemption.n_transfer_events}} events across the 161 originally scored tokens (15.2M of 22M total tonnes). Redemption rates were computed per credit type as redeemed/deposited tonnage. The within-token cross-pool comparison exploited 14 tokens deposited into both BCT and NCT to test whether the same credits experienced different fates under different pool designs. Account forensics, destination tracing, and profit quantification methods are detailed in Supplementary Methods.

## Price-quality dynamics

Cumulative PQD and renewable share were merged with daily BCT prices ($n$ = 331 overlapping days). A first-differenced OLS with Newey--West HAC standard errors (10 lags) tested contemporaneous co-movement. Bidirectional Granger causality was tested at weekly frequency ($n$ = {{price_quality.n_weekly_obs}}) using VAR(2) selected by AIC. We acknowledge the small sample limits power; the daily regression ($n$ = 330) provides the more robust test.

## Statistical inference

All $p$-values were corrected using the Benjamini--Hochberg FDR procedure at $\alpha$ = 0.05 across 10 primary tests. Headline claims were supplemented with 10,000-permutation $p$-values. Cluster-robust bootstrap (clustered by depositor account, 10,000 iterations) was used for deposit-level statistics. Additional inference details (account-clustered tests, CCP calibration, inter-rater reliability, rank correlations with commercial agencies) are provided in Supplementary Methods.

## Data availability

All data, scoring rubrics, analysis scripts, and smart contract source code are available at https://github.com/Adeline117/carbon-neutrality under an MIT licence. Machine-readable rubrics are in JSON format (`data/scoring-rubrics/`). The 318-credit methodology batch dataset with per-dimension scores is included. All 345/345 BCT tokens are scored (161 original + 184 imputed), with complete scores in `data/depositor-analysis/tco2_scores_complete.json`. On-chain deposit data for both BCT (1,187 transactions) and NCT (708 transactions) are provided with transaction hashes enabling independent verification. LLM panel outputs for all models across 29 credits are provided at `data/llm-panel-irr/raw/`. Analysis scripts are pure Python with NumPy/SciPy as sole dependencies.

## References

1. Allen, M. et al. The Oxford Principles for Net Zero Aligned Carbon Offsetting. University of Oxford (2020).
2. Integrity Council for the Voluntary Carbon Market. The Core Carbon Principles, Assessment Framework and Assessment Procedure. ICVCM (2023).
3. Berg, F., Kolbel, J., Pavlova, A. & Rigobon, R. The market for voluntary carbon offsets. SSRN Working Paper (2025).
4. Zeng, Y. et al. Biodiversity risks of carbon offset projects. *Nat. Rev. Biodivers.* (2026).
5. Carbon Market Watch & Perspectives Climate Group. Assessing and comparing carbon credit rating agencies. Carbon Market Watch Policy Brief (2023).
6. Akerlof, G. A. The market for "lemons": quality uncertainty and the market mechanism. *Q. J. Econ.* **84**, 488--500 (1970).
