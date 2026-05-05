# Methods

**Paper**: "On-chain forensics reveal adverse selection in the first tokenized carbon market"

---

## On-chain data collection

We collected all deposit transactions to the Toucan Protocol BCT pool contract on the Polygon blockchain using a Polygon RPC endpoint. The BCT pool contract accepts Toucan-bridged TCO2 tokens, each representing a specific Verra VCS project and vintage year. We identified 1187 deposit transactions spanning the period from BCT's launch in October 2021 to the effective cessation of new deposits in late 2022. These 1187 deposits mapped to 168 unique VCS project identifiers (345 unique TCO2 token addresses, reflecting multiple vintages per project) and approximately 22 million tonnes of tokenized carbon credits.

For each deposit, we recorded: the transaction hash, block number and timestamp, depositor address, TCO2 token contract address, Verra VCS project identifier (extracted from the TCO2 token metadata), vintage year, and tonnage deposited. Project identifiers were cross-referenced against the Verra registry to obtain methodology category (e.g., VM0007 for REDD+, AMS-I.D for grid-connected renewables), country of origin, and CCP eligibility status.

**Project classification.** Each of the 168 unique projects was classified into one of eleven methodology categories based on the Verra registry entry: (i) renewable energy (grid-connected wind, hydro, solar, and geothermal; CDM methodologies AMS-I.D, ACM0002, and equivalents), (ii) fossil fuel switching, (iii) waste management and methane capture (landfill gas, waste-to-energy; AMS-III.G, ACM0001), (iv) REDD+ (avoided deforestation and reduced degradation; VM0007, VM0009, VM0015, VM0006), (v) afforestation/reforestation (ARR), (vi) industrial gas destruction (HFC-23, N$_2$O; AM0001, AM0021), (vii) improved forest management (IFM), (viii) energy efficiency, (ix) industrial processes, (x) agriculture, and (xi) cookstoves. Tonnage-weighted shares were computed for each category.

**Tonnage weighting.** Pool-level composition statistics and quality metrics were computed with tonnage weighting: a project contributing 500,000 tonnes to the pool received 50 times the weight of a project contributing 10,000 tonnes.

## Quality scoring framework

We developed a composite quality scoring framework evaluating seven dimensions identified in the integrity literature as the primary determinants of credit quality. Each credit was scored on a 0--100 scale across six active dimensions: removal type hierarchy (weight 0.250), additionality (0.200), monitoring, reporting, and verification (MRV) grade (0.200), permanence (0.175), vintage year (0.100), and registry and methodology quality (0.075). Weights were chosen to reflect the relative importance assigned by the Oxford Offsetting Principles^11^ and the ICVCM CCP Assessment Framework^8^, with removal type receiving the largest weight to encode the Oxford hierarchy (removal > avoidance > reduction).

The seventh dimension, co-benefits, was assigned a weight of zero and converted to a binary disqualifier gate (the "safeguards-gate"). This design decision followed from Berg et al.^6^, who found that buyers pay approximately double the premium for credits with co-benefit narratives regardless of underlying integrity. Including co-benefits as a scored dimension would therefore amplify adverse selection by inflating the scores of credits whose quality deficits are obscured by compelling co-benefit narratives.

The composite score was computed as:

$$C = \sum_{i=1}^{7} w_i \times s_i$$

where $w_i$ is the weight and $s_i$ is the per-dimension score for dimension $i$, with $w_{\text{co-benefits}} = 0$. Composites were mapped to letter grades: AAA ($\geq$90), AA ($\geq$75), A ($\geq$60), BBB ($\geq$45), BB ($\geq$30), and B (<30).

Seven disqualifier conditions cap the maximum achievable grade regardless of composite score. Three conditions cap at grade B (evidence of double counting, failed verification, credible human rights violation claims). One condition caps at BB (registry or methodology under sanction). Three conditions cap at BBB (no independent third-party verification, documented community opposition or environmental damage, published evidence of biodiversity loss^21^). Disqualifiers were applied after composite scoring and never raised a grade, only lowered it.

**Distributional scoring.** Each per-dimension score was modelled as normally distributed around its point estimate, with standard deviations calibrated from the inter-rater reliability study (see below). Calibrated per-dimension standard deviations ranged from $\sigma$ = 4.0 (permanence) to $\sigma$ = 11.1 (registry and methodology). Under the assumption of independent dimension scores, composite variance was computed as:

$$\text{Var}(C) = \sum_{i} w_i^2 \times \sigma_i^2$$

Grade posteriors were computed via the Gaussian CDF: $P(\text{grade} = G) = \Phi\bigl(\frac{u_G - \mu}{\sigma_C}\bigr) - \Phi\bigl(\frac{l_G - \mu}{\sigma_C}\bigr)$, where $l_G$ and $u_G$ are the lower and upper boundaries of grade $G$, $\mu$ is the composite point estimate, and $\sigma_C = \sqrt{\text{Var}(C)}$. The reported grade was the posterior mode. Machine-readable rubrics are provided in JSON format at `data/scoring-rubrics/`.

## Framework validation

The quality framework was validated against three independent external benchmarks to establish that the scores used throughout this paper are credible measures of credit quality.

### CCP empirical calibration

We tested whether the framework's composite scores separated CCP-eligible from non-CCP credits using a dataset of 318 credits classified by ICVCM CCP eligibility status (165 CCP-eligible, 153 non-CCP) across 17 methodology categories. CCP classification was based on the ICVCM's published list of CCP-approved methodologies and CCP-eligible programmes as of 2025.

CCP-eligible credits achieved a mean ordinal grade of 2.69 on a 0--5 scale (where B = 0 and AAA = 5), while non-CCP credits scored 0.70 --- a gap of 1.99 grade levels. Five effect size measures were computed: Cohen's $d$ = 1.87 (95% CI: 1.68--2.11, pooled SD), Glass's $\delta$, Cliff's $\delta$ = 0.83 (95% CI: 0.75--0.90), CLES = 91.4% (95% CI: 87.5--94.8%), and Mann--Whitney $U$ ($z$ = 13.06, $p$ $\approx$ 0). For each measure, 95% confidence intervals were obtained via the percentile bootstrap method with 10,000 resamples (seed = 42). No CCP-eligible credit scored B; no non-CCP credit scored A or AAA.

This gap was not designed: the framework was constructed from the Oxford Principles hierarchy and literature-derived dimension definitions, without fitting to CCP labels. That it independently recovers the approximately two-grade-level gap that Calyx Global --- an ICVCM-appointed rating agency --- reported between CCP-eligible and non-CCP projects constitutes convergent validation.

**Removal-type sensitivity.** A potential circularity concern --- that the removal-type dimension (weight 0.250) mechanically reproduces the CCP label --- was tested by setting the removal-type weight to zero and redistributing proportionally. The CCP/non-CCP composite gap was preserved at 101.4% (27.7 vs. 27.3 points), with Cohen's $d$ increasing from 1.87 to 2.44 ($n$ = 318). The separation is driven by additionality, permanence, and MRV rather than by removal type alone.

### Rank correlation with commercial rating agencies

External validity was assessed by computing Spearman rank correlations between framework grades and publicly available ratings from three commercial carbon credit rating agencies: BeZero Carbon, Calyx Global, and Sylvera.

**REDD+ subset.** Six REDD+ projects were drawn from Carbon Market Watch^9^ (2023, Table 20), which reported simultaneous ratings from all three agencies. Spearman rank correlations were computed for all six pairwise combinations of four raters (our framework, BeZero, Calyx, Sylvera). The mean correlation between our framework and the three agencies was $\rho$ = +0.343, compared with a mean inter-agency correlation of $\rho$ = +0.009. BeZero and Calyx Global were anti-correlated at $\rho$ = $-$0.664 on the same six projects.

**Cross-type extension.** An expanded dataset of 27 projects spanning 12 credit types (REDD+, DACCS, biochar, enhanced weathering, cookstoves, methane abatement, IFM, landfill gas, ODS destruction, renewable energy, jurisdictional REDD+, and ARR) was compiled from BeZero case studies, Calyx research publications, and Sylvera press releases. Spearman $\rho$ = +0.901 (95% CI [+0.783, +0.959], Kendall $\tau$ = 0.821, permutation $p$ < 0.0001), with 52% exact grade match and 100% within $\pm$1 grade. Leave-one-out cross-validation confirmed stability: $\rho$ ranged from +0.889 to +0.922 across all 27 jackknife samples. Subgroup analysis: CDR credits ($\rho$ = +0.973, $n$ = 9), avoidance credits ($\rho$ = +0.802, $n$ = 18).

### Inter-rater reliability study

Reproducibility was tested using a panel of three Claude-family language models (Opus 4.6, Sonnet 4.6, Haiku 4.5), each scoring 29 credits independently in isolated sessions using redacted evidence packs with author grades removed. No inter-rater communication was permitted.

Grade-level Fleiss' $\kappa$ across the three-rater panel was 0.600, at the boundary between moderate and substantial agreement per Landis and Koch. Composite-level ICC(2,$k$) was 0.993. The author's grades matched the panel median on 25/29 credits (86%), with every discrepancy confined to a single adjacent grade band. Per-dimension $\kappa$: permanence 0.684 (substantial), removal type 0.585 (moderate), vintage year 0.324 (fair), MRV 0.248 (fair), additionality 0.243 (fair), co-benefits 0.182 (slight), registry methodology 0.168 (slight). Per-dimension standard deviations from this study were used to calibrate the distributional scoring model.

A multi-provider replication using GPT-5, Gemini 2.5 Pro, and Llama 4 Maverick ($n$ = 5 credits) yielded pooled Fleiss' $\kappa$ = 0.647, composite ICC = 1.000, mean pairwise Cohen's $\kappa$ = +0.658 (range: +0.500 to +0.737), 73% exact grade agreement, and 100% within-one-band agreement. Per-provider systematic bias was minimal (max $|\Delta|$ = 1.5 composite points).

### Weight sensitivity analysis

**Monte Carlo weight perturbation.** 10,000 weight vectors sampled from a Dirichlet distribution centred on the current weights (concentration 50, co-benefits forced to zero). Global grade robustness: 93.7% (90.1% at concentration 20; 95.4% at concentration 100). Five credits were flagged as fragile (stability <90%), all within 3 points of a grade boundary. At the extremes --- Climeworks Orca (AAA, 100% stable) and Kariba REDD+ (B, 100% stable) --- grades were invariant regardless of weight perturbation.

**Deterministic sensitivity.** Shifting any single dimension's weight by $\pm$5pp: maximum 3 grade flips out of 29 credits. Leave-one-out (dropping each dimension entirely): maximum 4 grade flips.

**Cross-temporal stability.** v0.3 to v0.6 Spearman $\rho$ = 0.992 on composite rankings; 0 grade changes between v0.4 and v0.6.

## Pool Quality Deficit

We defined the Pool Quality Deficit (PQD) to quantify quality degradation in a carbon credit pool:

$$\text{PQD}(\text{pool}) = 1 - \frac{\bar{C}}{100}$$

where $\bar{C}$ is the tonnage-weighted mean composite score of all credits in the pool. The PQD ranges from 0 (every credit scores 100; no quality degradation) to 1 (every credit scores 0; complete quality failure).

## Extended scoring

Of the 345 unique TCO2 token addresses in the BCT pool, 161 were scored in the original methodology-archetype batch. The remaining 184 tokens were scored using the same rubric rules applied to available metadata fields. Each imputed score was flagged with `source="imputed"`. All analyses are reported on the full 345-token dataset; robustness checks confirm qualitatively identical results when restricted to the 161 original-scored tokens.

## Base-rate comparison

To test whether BCT's composition reflects selection bias rather than the underlying VCS supply, we compared BCT's renewable energy share against the Verra VCS base rate estimated from MSCI (2023) and Ecosystem Marketplace (2023) at 37% (sensitivity range 26--48%). The selection coefficient was defined as $S = f_{\text{BCT,renewable}} / f_{\text{VCS,renewable}}$. An exact binomial test was used to test the null hypothesis that BCT's renewable share equals the VCS base rate. Sensitivity analysis repeated the test across the full base-rate range (26--48%) and extended to post-2008 VCS vintage-adjusted rates up to 55%.

## Bridge-level decomposition

To distinguish bridge-level from pool-level selection, we enumerated all TCO2 token contracts created by Toucan's `ToucanCarbonOffsetsFactory` on Polygon (queried via Dune Analytics, filtered to events before 1 January 2023). We cross-referenced against the set of TCO2 addresses appearing in BCT deposit events. The ratio of BCT-deposited tokens to total bridged tokens measures the pass-through rate.

## Event study

We exploited two exogenous shocks --- the Terra/LUNA collapse (May 2022) and the FTX collapse (November 2022) --- to test whether deposit quality changed in response to market stress. For each event, we split scored deposits into pre-event and post-event periods and computed Spearman rank correlations within each period.

## Vintage-free robustness check

We recomputed the composite score with vintage weight set to zero and the freed weight redistributed proportionally across the five remaining active dimensions: removal type (0.2778), additionality (0.2222), permanence (0.1944), MRV (0.2222), and registry and methodology (0.0833). The temporal correlation was recomputed on the full scored deposit series.

## NCT cross-pool comparison

We collected all 708 deposit events from the Toucan NCT pool on Polygon over the same block range. NCT restricts deposits to AFOLU credits with vintage $\geq$2012. **Within-token cross-pool comparison.** 14 TCO2 tokens (all nature-based: 5 REDD+, 5 IFM, 4 ARR) were deposited into both BCT and NCT. For each, we computed the redemption rate separately in each pool. The identifying assumption is that the same token's intrinsic quality does not differ between pools; any difference in redemption rate is attributable to pool-level factors. **Observational comparison.** The broader BCT--NCT comparison (88.6% token overlap) is observational. Standard errors were computed using cluster-robust bootstrap (clustered by depositor wallet, 10,000 iterations, seed = 42).

## Depositor-level analysis

For all 1187 BCT deposits, we computed depositor-level concentration metrics: Gini coefficient, HHI, and effective number of depositors (1/HHI). To test whether large depositors systematically deposited lower-quality credits, we compared quality distributions of the top 20 depositors by tonnage against the remaining 489 depositors using a two-sided Mann--Whitney $U$ test.

## Price-quality dynamics

Daily BCT-USDC prices were obtained from DeFi Llama (828 observations). Cumulative PQD and rolling renewable share were computed from the deposit stream at daily frequency, yielding $n$ = 331 overlapping observations. **First-differenced regression.** $\Delta\text{Price}_t = \alpha + \beta_1 \Delta\text{PQD}_t + \beta_2 \Delta\text{Renewable}_t + \varepsilon_t$, with HAC standard errors (Newey--West, 10 lags). **Granger causality.** Bidirectional Granger causality was tested at weekly frequency using a VAR(2) model ($n$ = 55). Lag length selected by AIC from candidates 1--4. Post-hoc power analysis: at $n$ = 55 with VAR(2), the minimum detectable $F$-statistic at 80% power is approximately 6.4.

## Redemption analysis

Redemptions were identified from ERC-20 Transfer events where the BCT pool contract address appears as the `from` field (35,432 events). Each redemption was matched to the quality score of the corresponding TCO2 token. Net pool composition was computed as cumulative deposits minus cumulative redemptions at monthly intervals.

## Wallet forensics and quality swap analysis

For each wallet, we computed: total redeemed tonnage, tonnage-weighted mean quality, dominant credit type, and whether the wallet also appeared as a depositor. **Post-extraction destination tracing.** For each redemption by a top-20 redeemer, the next Transfer event for the same TCO2 token was classified into five categories: burn address (on-chain retirement), NCT pool (cross-pool deposit), BCT pool (re-deposit), transfer to another address, or still held. **Profit quantification.** Off-chain credit prices were assigned by type using contemporaneous (2021--2022) market data from Ecosystem Marketplace and Carbon Pulse: industrial gas \$3--12/tonne, REDD+ \$4--15/tonne, IFM \$5--18/tonne, ARR \$6--20/tonne, renewable energy \$0.30--1.50/tonne. BCT redemption cost was estimated as the pool price at redemption time plus the Toucan selective redemption fee, yielding \$1--5/tonne across the pool's operating period. **Quality swap.** For each of the 399 overlap wallets, the tonnage-weighted mean quality of deposited and redeemed tokens was computed separately; the quality swap was defined as the difference (redeemed minus deposited quality).

## Wallet-clustered inference

**Wallet-level permutation test.** 10,000 iterations resampling wallets with their complete portfolios under the null $P(\text{renewable})$ = 0.37, yielding $p$ <0.0001. **HHI-adjusted binomial test.** $n_{\text{eff}}$ = 1/HHI = 83.5, $p$ = 2.9e-15. **DEFF-adjusted binomial test.** Assuming ICC = 0.5, DEFF = 4.4, $n_{\text{eff}}$ = 270, $p$ = 4.7e-44. **Bootstrap CI.** Wallet-level BCa bootstrap (10,000 iterations): selection coefficient 0.522 [0.496, 0.547].

## Counterfactual quality-gate simulation

For BCT and five additional pools, we simulated quality gates at all six grade thresholds. At each threshold, only credits meeting or exceeding the grade were admitted. We recomputed the number of admitted credits, new tonnage-weighted mean composite, and resulting PQD.

## 34-segment quality atlas

34 quality segments defined by project type (17 categories from the ICVCM taxonomy), vintage band (pre-2015, 2015--2019, 2020--2023, 2024+), and CCP eligibility. Each segment scored using median archetype scores from the 318-credit dataset. Monte Carlo null model: 10,000 random pools of matched size, baseline PQD = 0.51 (SD = 0.036).

## Statistical inference and multiple testing

All reported $p$-values were corrected using the Benjamini--Hochberg FDR procedure at $\alpha$ = 0.05, applied to the family of 10 primary hypothesis tests (Supplementary Table). For headline claims, permutation $p$-values (10,000 iterations) supplement asymptotic tests. **Cluster-robust inference.** Bootstrap resampled at the TCO2-token level (10,000 iterations, seed = 42).

## Data availability

All data, scoring rubrics, analysis scripts, and smart contract source code are available at https://github.com/Adeline117/carbon-neutrality under an MIT licence. Machine-readable rubrics in JSON format. The 318-credit methodology dataset, 29-credit pilot dataset, LLM panel outputs, and the complete 345/345 BCT token scores are included. On-chain deposit data for BCT (1187 transactions) and NCT (708 transactions) are provided with transaction hashes for independent verification.
