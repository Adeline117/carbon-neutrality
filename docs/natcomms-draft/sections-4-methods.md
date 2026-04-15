# Methods

## Quality scoring framework

We developed a composite quality scoring framework for carbon credits that evaluates seven dimensions identified in the integrity literature as the primary determinants of credit quality. Each credit was scored on a 0--100 scale across six active dimensions: removal type hierarchy (weight 0.250), additionality (0.200), monitoring, reporting, and verification (MRV) grade (0.200), permanence (0.175), vintage year (0.100), and registry and methodology quality (0.075). Weights were chosen to reflect the relative importance assigned by the Oxford Offsetting Principles^1^ and the Integrity Council for the Voluntary Carbon Market (ICVCM) Core Carbon Principles (CCP) Assessment Framework^2^, with removal type receiving the largest weight to encode the Oxford hierarchy (removal > avoidance > reduction).

The seventh dimension, co-benefits, was assigned a weight of zero and converted to a binary disqualifier gate. This design decision followed from Berg et al.^3^, who found that buyers pay approximately double the premium for credits with co-benefit narratives regardless of underlying integrity. Including co-benefits as a scored dimension would therefore amplify the adverse selection mechanism the framework was designed to detect. We retained the co-benefits rubric as an informational field and used its scoring bands to determine whether to flag the community harm disqualifier (Supplementary Table 1).

The composite score was computed as the weighted linear sum:

$$C = \sum_{i=1}^{7} w_i \times s_i$$

where $w_i$ is the weight and $s_i$ is the per-dimension score for dimension $i$, with $w_{\text{co-benefits}} = 0$. Composites were mapped to letter grades: AAA ($\geq$90), AA ($\geq$75), A ($\geq$60), BBB ($\geq$45), BB ($\geq$30), and B (<30).

Seven disqualifier conditions were defined to cap the maximum achievable grade regardless of composite score. Three conditions capped at grade B (evidence of double counting, failed verification, credible human rights violation claims). One condition capped at BB (registry or methodology under sanction). Three conditions capped at BBB (no independent third-party verification, documented community opposition or environmental damage, published evidence of biodiversity loss^4^). Disqualifiers were applied after composite scoring and never raised a grade, only lowered it.

**Distributional scoring.** To propagate scoring uncertainty into grade assignments, we modelled each per-dimension score as normally distributed around its point estimate, with standard deviations calibrated empirically from the inter-rater reliability study described below. Calibrated per-dimension standard deviations ranged from $\sigma = 4.0$ (permanence) to $\sigma = 11.1$ (registry and methodology), reflecting the observed inter-rater disagreement. Under the assumption of independent dimension scores, the composite variance was computed as:

$$\text{Var}(C) = \sum_{i} w_i^2 \times \sigma_i^2$$

Grade posteriors were computed via the Gaussian cumulative distribution function: $P(\text{grade} = G) = \Phi\bigl(\frac{u_G - \mu}{\sigma_C}\bigr) - \Phi\bigl(\frac{l_G - \mu}{\sigma_C}\bigr)$, where $l_G$ and $u_G$ are the lower and upper boundaries of grade $G$, $\mu$ is the composite point estimate, and $\sigma_C = \sqrt{\text{Var}(C)}$. The reported grade was the posterior mode. Machine-readable rubrics are provided in JSON format at `data/scoring-rubrics/`.

## Lemons Index

We defined the Lemons Index $L$ to quantify the degree of adverse selection in a tokenized carbon credit pool:

$$L(\text{pool}) = 1 - \frac{\bar{C}}{100}$$

where $\bar{C}$ is the mean composite score of all credits in the pool. The index ranges from 0 (every credit scores 100; no adverse selection) to 1 (every credit scores 0; complete quality failure). The metric is named after Akerlof's^5^ characterisation of markets in which information asymmetry drives out high-quality goods.

We computed $L$ for six pool compositions. Four were based on publicly documented holdings of deployed tokenized carbon pools: Toucan Base Carbon Tonne (BCT; 43 credits across 9 methodology categories at 2022 peak holdings on Polygon), Toucan Nature Carbon Tonne (NCT; 28 credits, agriculture, forestry, and other land use only, vintage $\geq$ 2012), Moss MCO2 (30 credits, Amazon REDD+-dominated), and Toucan CHAR (12 credits, biochar-only with project allowlist, deployed on Base in 2025). Two were prospective compositions: Klima 2.0 kVCM (20 credits, mixed legacy and carbon dioxide removal, projected for 2026) and a hypothetical AAA-only pool (13 credits, engineered CDR including direct air carbon capture and storage, bio-oil injection, and enhanced weathering). Each credit within a pool was scored using methodology-level archetypes from a 318-credit batch dataset, with vintage-year adjustments applied via a temporal decay formula.

## CCP empirical calibration

We tested whether the framework's composite scores separated CCP-eligible from non-CCP credits using a dataset of 318 credits classified by ICVCM CCP eligibility status (165 CCP-eligible, 153 non-CCP) across 17 methodology categories. CCP classification was based on the ICVCM's published list of CCP-approved methodologies and CCP-eligible programmes as of 2025.

Five effect size measures were computed: Cohen's $d$ (pooled standard deviation), Glass's $\delta$ (using non-CCP standard deviation as denominator), Cliff's $\delta$ (nonparametric), the common language effect size (CLES), and a Mann--Whitney $U$ test with normal-approximation $z$-score including tie correction. For each parametric and nonparametric effect size, 95% confidence intervals were obtained via the percentile bootstrap method with 10,000 resamples (seed = 42). Grade distributions were encoded on an ordinal scale (B = 0, BB = 1, BBB = 2, A = 3, AA = 4, AAA = 5).

## Rank correlation with commercial rating agencies

We assessed external validity by computing rank correlations between our framework's grades and publicly available ratings from three commercial carbon credit rating agencies: BeZero Carbon, Calyx Global, and Sylvera.

**REDD+ subset.** Six REDD+ projects were drawn from Carbon Market Watch^6^ (2023, Table 20), which reported simultaneous public ratings from all three agencies as of 2 June 2023. Each agency's ordinal scale was mapped to a monotonic integer sequence (higher = better quality), and each project was scored under our framework (v0.4.1 rubric). Spearman rank correlations ($\rho$) and Kendall's $\tau$-b were computed for all six pairwise combinations of four raters (our framework, BeZero, Calyx, Sylvera).

**Cross-type extension.** An additional 11 projects spanning seven non-REDD+ methodology types (direct air capture, biochar, cookstoves, improved forest management, methane abatement, landfill gas, renewable energy) were compiled from BeZero case studies, Calyx research publications, and Sylvera press releases. These were scored under the v0.6 rubric and correlated against each agency where pairwise coverage existed.

**Statistical inference.** For the combined dataset (REDD+ and cross-type), Spearman $\rho$ was computed with 10,000-resample percentile bootstrap 95% confidence intervals and a two-sided permutation test $p$-value (10,000 permutations, seed = 42). We report significance at $\alpha = 0.05$. Results are provided in Supplementary Table 2.

## Inter-rater reliability study

To assess reproducibility of the scoring framework, we conducted an inter-rater reliability (IRR) study using three independent large language model (LLM) raters: Claude Opus 4.6, Claude Sonnet 4.6, and Claude Haiku 4.5 (Anthropic, 2025). Each model scored all 29 credits (25 real-world archetypes plus 4 synthetic stress-test credits) using the v0.4.1 rubric. No inter-rater communication was permitted: each model received an identical prompt containing the complete rubric and publicly available project documentation, and returned per-dimension scores and disqualifier flags independently.

We computed the following agreement metrics. (i) Fleiss' $\kappa$ across the three LLM raters at the grade level (six categories: B through AAA). (ii) Per-dimension Fleiss' $\kappa$, with continuous scores binned into 10 buckets of 10 points each. (iii) The intraclass correlation coefficient ICC(2,$k$) on the continuous composite, using a two-way random effects model with mean-of-$k$-raters consistency. (iv) Exact grade agreement and within-one-band agreement between the author's v0.4.1 grades and the LLM panel's median grade.

**Disqualifier recall.** Four synthetic stress-test credits (C026--C029) were constructed with known correct disqualifiers (double counting, sanctioned registry, no third-party verification, community harm). Recall was defined as the fraction of LLM raters that correctly flagged each disqualifier.

**Fragility validation.** Three boundary-adjacent credits (C004 Charm Industrial, composite 90.53, AAA; C011 adipic acid N$_2$O destruction, 57.28, BBB; C014 Plan Vivo agroforestry, 60.15, A) were flagged a priori as fragile due to proximity to grade boundaries (buffer < 3.0 points). LLM panel consensus was checked against the author's baseline grade to determine whether boundary-adjacent credits exhibited higher inter-rater disagreement than interior credits.

Per-dimension standard deviations from this study were used to calibrate the distributional scoring model described above: for each dimension, $\sigma_i \approx \overline{|\Delta|} / 1.128$, where $\overline{|\Delta|}$ is the mean absolute pairwise difference across the three-rater panel and $1.128$ is the Gaussian estimator relating mean absolute difference to standard deviation.

## Counterfactual quality-gate simulation

For each of the six tokenized pools described above, we simulated the application of an on-chain quality gate at all six grade thresholds (B, BB, BBB, A, AA, AAA). At each threshold, a `meetsGrade()` function admitted only credits whose final grade met or exceeded the threshold. We then recomputed: the number of admitted credits, the new mean composite score, the resulting Lemons Index, and the fraction of admitted credits at grade A or above. The purpose of this simulation was to demonstrate the extent to which quality gating could reduce the Lemons Index toward levels observed in curated pools (e.g., CHAR), providing theoretical evidence that on-chain quality enforcement is a tractable mechanism to counteract adverse selection.

## Sensitivity analysis

**Monte Carlo weight perturbation.** We assessed the robustness of grade assignments to alternative weighting schemes by sampling 10,000 random weight vectors from a Dirichlet distribution centred on the current weights. The Dirichlet concentration parameter was set to 50 for the primary analysis, with robustness checks at concentrations of 20 (wide) and 100 (tight). The co-benefits weight was forced to zero in all samples to maintain the safeguards-gate design. For each sampled weight vector, all 29 credits were rescored and assigned a grade. Per-credit grade stability was defined as the fraction of iterations in which the credit received the same grade as under the baseline weights. Global robustness was the mean grade stability across all credits. Credits with stability below 90% were flagged as fragile (Supplementary Table 3).

**Deterministic weight perturbation.** We additionally performed a targeted perturbation analysis in which each dimension's weight was increased and decreased by 5 percentage points, with the delta redistributed proportionally across remaining dimensions. A leave-one-out analysis set each non-zero dimension weight to zero and redistributed proportionally. Both analyses reported the number of credits whose final grade changed.

**Cross-temporal stability.** The same 29 credits were scored under three methodology versions (v0.3, v0.4, v0.6) differing in weight vectors and rubric definitions. Grade agreement rate and Spearman $\rho$ of composite rankings were computed between consecutive versions to assess convergence behaviour.

## On-chain implementation

Smart contracts were written in Solidity 0.8.24, compiled and tested using the Foundry toolchain, and deployed on the Base Sepolia testnet. The core contract (`CarbonCreditRating.sol`) stored per-credit ratings as structured records containing per-dimension scores (uint8, 0--100), per-dimension standard deviations (uint8), composite score in basis points (uint16, 0--10000), composite variance in squared basis points (uint32), disqualifier flags (boolean struct), nominal and final grades (enum, B = 0 through AAA = 5), a methodology version identifier (uint16), an expiry timestamp (uint64), and a keccak256 evidence hash linking to off-chain audit materials.

The contract exposed two principal read functions. `ratingOf()` returned the complete rating record for a given credit token address and token identifier. `meetsGrade()` returned a boolean indicating whether a credit's final grade met or exceeded a specified minimum, rejecting stale ratings (expired or written under a superseded methodology version).

Three composability contracts demonstrated integration patterns. `QualityGatedPool.sol` called `meetsGrade()` as a deposit precondition, rejecting credits below the pool's quality threshold. `KlimaRetirementGate.sol` required `meetsGrade()` before permitting credit retirement. `CHARQualityOverlay.sol` read `ratingOf()` to apply fee discounts proportional to credit quality.

**Off-chain/on-chain equivalence.** The Python scoring implementation (`score.py`) and the Solidity contract were validated to produce bit-identical composite scores. The composite calculation in Solidity used integer arithmetic in basis points: $\text{composite}_{\text{bps}} = \sum_i (s_i \times W_i) / 100$, where $s_i \in [0,100]$ and $W_i$ is the weight in basis points $\in [0,10000]$. The variance calculation followed an analogous structure: $\text{var}_{\text{bps}^2} = \sum_i (\sigma_i^2 \times W_i^2) / 10000$. Test vector: Climeworks Orca yielded composite = 9505 bps in both implementations.

## Data availability

All data, scoring rubrics, analysis scripts, and smart contract source code are available at https://github.com/Adeline117/carbon-neutrality under an MIT licence. Machine-readable rubrics are provided in JSON format (`data/scoring-rubrics/`). The 318-credit methodology batch dataset with per-dimension scores is included. Raw LLM panel outputs for all three models across 29 credits are provided at `data/llm-panel-irr/raw/`. Analysis scripts are pure Python with no external dependencies.

## References

1. Allen, M. et al. The Oxford Principles for Net Zero Aligned Carbon Offsetting. University of Oxford (2020).
2. Integrity Council for the Voluntary Carbon Market. The Core Carbon Principles, Assessment Framework and Assessment Procedure. ICVCM (2023).
3. Berg, F. et al. Quantifying the option value of carbon credits. *Working paper* (2025).
4. Zeng, Y. et al. Biodiversity risks of carbon offset projects. *Nat. Rev. Biodivers.* (2026).
5. Akerlof, G. A. The market for "lemons": quality uncertainty and the market mechanism. *Q. J. Econ.* **84**, 488--500 (1970).
6. Carbon Market Watch. The carbon market conundrum: assessing credit quality in the voluntary carbon market. Carbon Market Watch Report (2023).
