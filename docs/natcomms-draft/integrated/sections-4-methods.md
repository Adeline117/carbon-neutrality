# Methods

**Paper**: "Adverse selection in tokenized carbon markets: who profited from the first pool collapse"

---

## Methods

### Data collection

We collected all deposit transactions to the Toucan Protocol BCT pool contract on the Polygon blockchain using a Polygon RPC endpoint. We identified {{composition.n_deposits}} deposit transactions spanning the period from BCT's launch in October 2021 to the effective cessation of new deposits in late 2022, mapping to {{composition.n_projects}} unique VCS project identifiers (345 unique TCO2 token addresses) and approximately 22 million tonnes of tokenized carbon credits. For each deposit, we recorded: transaction hash, block number and timestamp, depositor address, TCO2 token contract address, Verra VCS project identifier, vintage year, and tonnage. Project identifiers were cross-referenced against the Verra registry to obtain methodology category, country of origin, and CCP eligibility status.

**Project classification.** Each project was classified into one of eleven methodology categories based on the Verra registry entry: renewable energy (grid-connected wind, hydro, solar; CDM methodologies AMS-I.D, ACM0002), fossil fuel switching, waste management and methane capture, REDD+ (VM0007, VM0009, VM0015), afforestation/reforestation (ARR), industrial gas destruction, improved forest management (IFM), energy efficiency, industrial processes, agriculture, and cookstoves. Pool-level composition statistics were computed with tonnage weighting.

**NCT data.** We collected all 708 deposit events from the Toucan NCT pool on the same Polygon blockchain over the same block range. NCT restricts deposits to AFOLU credits with vintage $\geq$2012, functioning as a minimal quality gate on project type. NCT and BCT share identical protocol infrastructure and blockchain substrate.

**Price data.** Daily BCT-USDC prices were obtained from the DeFi Llama API for the Polygon SushiSwap BCT-USDC pair (828 observations, October 2021 -- July 2024).

### Quality scoring framework

We developed a composite quality scoring framework evaluating six active dimensions on a 0--100 scale: removal type hierarchy (weight 0.250), additionality (0.200), MRV grade (0.200), permanence (0.175), vintage year (0.100), and registry and methodology quality (0.075). Initial weights were derived from the Oxford Offsetting Principles^11^ and the ICVCM CCP Assessment Framework^8^. A pilot Best-Worst Scaling expert panel ($n$ = 5) confirmed consistency with our weights (Spearman $\rho$ = +0.814). Monte Carlo perturbation (10,000 Dirichlet-sampled weight vectors) confirms 93.7% grade stability. The composite was computed as $C = \sum_{i} w_i \times s_i$ and mapped to letter grades: AAA ($\geq$90), AA ($\geq$75), A ($\geq$60), BBB ($\geq$45), BB ($\geq$30), B (<30). Seven disqualifier conditions cap maximum grades regardless of composite score. Co-benefits was assigned zero weight to avoid amplifying adverse selection through co-benefit narratives^6^. The Pool Quality Deficit (PQD = $1 - \bar{C}/100$) quantifies tonnage-weighted quality degradation per pool. Full scoring details, distributional scoring model, extended scoring procedures, and sensitivity analyses are provided in Supplementary Methods.

### Base-rate comparison

BCT's renewable energy share was compared against the Verra VCS base rate (central estimate 37%, sensitivity range 26--48%, from MSCI^7^ and Ecosystem Marketplace reports). The selection coefficient $S = f_{\text{BCT,renewable}} / f_{\text{VCS,renewable}}$ was tested via exact binomial test, with account-clustered robustness (permutation, HHI-adjusted, and bootstrap tests; see Supplementary Methods).

### Difference-in-differences

A deposit-level DiD panel pooling all 1,895 events (1,187 BCT + 708 NCT) tested whether BCT's quality trajectory diverged from NCT's:

$$\text{quality}_i = \beta_0 + \beta_1 \cdot \text{BCT}_i + \beta_2 \cdot \text{PostShock}_i + \beta_3 \cdot (\text{BCT} \times \text{PostShock})_i + \varepsilon_i$$

where $\text{PostShock}_i$ indicates deposits after the May 2022 cryptocurrency market crash. Standard errors were cluster-robust at the TCO2 token level (349 clusters) with small-sample correction. Robustness: permutation test (10,000 iterations), Bayesian bootstrap, and continuous-time specification. A compositional DiD (binary renewable outcome) provided a framework-free test; we note that NCT mechanically cannot accept renewable credits, so the compositional result partially reflects eligibility constraints rather than a pure treatment effect.

### Redemption analysis

Redemptions were identified from ERC-20 Transfer events where the BCT pool contract appears as the sender, yielding {{redemption.n_transfer_events}} events across the 161 originally scored tokens (15.2M of 22M total tonnes). Redemption rates were computed per credit type as redeemed/deposited tonnage. The within-token cross-pool comparison exploited 14 tokens deposited into both BCT and NCT to test whether the same credits experienced different fates under different pool designs. Account forensics, destination tracing, and profit quantification methods are detailed in Supplementary Methods.

### Price-quality dynamics

Cumulative PQD and renewable share were merged with daily BCT prices ($n$ = 331 overlapping days). A first-differenced OLS with Newey--West HAC standard errors (10 lags) tested contemporaneous co-movement. Bidirectional Granger causality was tested at weekly frequency ($n$ = {{price_quality.n_weekly_obs}}) using VAR(2) selected by AIC. We acknowledge the small sample limits power; the daily regression ($n$ = 330) provides the more robust test.

### Cross-domain comparison

To test whether the adverse selection pattern generalises beyond carbon markets, we analysed composition shifts in the Curve Finance stETH/ETH liquidity pool on Ethereum during the May 2022 market crash. Curve's stableswap treats stETH (a liquid staking derivative) and ETH as near-equivalent --- a uniform-pricing mechanism analogous to BCT's 1:1 tokenization. We computed weekly net flows for each asset and defined the composition shift as the absolute difference in net flows (ETH outflow minus stETH outflow). The pre-crisis baseline was the mean weekly absolute composition shift over the 8 weeks preceding 7 May 2022. This analysis is presented as supporting evidence; the Curve comparison is observational and also consistent with a classical bank-run interpretation.

### Welfare gap estimation

We estimated the welfare cost of BCT's quality degradation using a Monte Carlo simulation (10,000 iterations). Each iteration sampled: (i) additionality rates per credit type from literature-derived distributions^2,24^ (renewable energy: 0--20%; REDD+: 25--75%; IFM: 30--70%; ARR: 40--80%); (ii) the social cost of carbon from a uniform distribution (\$50--200/tCO$_2$); and (iii) a counterfactual pool composition matching VCS registry base rates. The welfare gap was computed as the difference in expected climate value between the counterfactual pool and BCT's actual composition. This estimate is illustrative and conditional on both the additionality assumptions and the counterfactual specification.

### Statistical inference

All $p$-values were corrected using the Benjamini--Hochberg FDR procedure at $\alpha$ = 0.05 across the following 10 primary tests: (1) base-rate selection coefficient (binomial), (2) full-sample temporal correlation, (3) pre-shock temporal correlation, (4) DiD quality-score $\beta_3$, (5) DiD compositional $\beta_3$, (6) Granger quality$\rightarrow$price, (7) Granger price$\rightarrow$quality, (8) within-pool permutation, (9) depositor concentration Mann--Whitney, (10) redemption differential chi-squared. Headline claims were supplemented with 10,000-permutation $p$-values. Cluster-robust bootstrap (clustered by depositor account, 10,000 iterations) was used for deposit-level statistics. Additional inference details (account-clustered tests, CCP calibration, inter-rater reliability, rank correlations with commercial agencies) are provided in Supplementary Methods.

### Data availability

All data, scoring rubrics, analysis scripts, and smart contract source code are available at https://github.com/Adeline117/carbon-neutrality under an MIT licence. Machine-readable rubrics are in JSON format (`data/scoring-rubrics/`). The 318-credit methodology batch dataset with per-dimension scores is included. All 345/345 BCT tokens are scored (161 original + 184 imputed), with complete scores in `data/depositor-analysis/tco2_scores_complete.json`. On-chain deposit data for both BCT (1,187 transactions) and NCT (708 transactions) are provided with transaction hashes enabling independent verification. LLM panel outputs for all models across 29 credits are provided at `data/llm-panel-irr/raw/`. Analysis scripts are pure Python with NumPy/SciPy as sole dependencies.
