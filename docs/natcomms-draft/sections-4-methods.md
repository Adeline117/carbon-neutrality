# Methods

**Paper**: "Anatomy of a market failure: on-chain evidence reveals renewable energy credits, not REDD+, drove the collapse of tokenized carbon markets"

---

## On-chain data collection

We collected all deposit transactions to the Toucan Protocol BCT pool contract on the Polygon blockchain using a Polygon RPC endpoint. The BCT pool contract accepts Toucan-bridged TCO2 tokens, each representing a specific Verra VCS project and vintage year. We identified 1,187 deposit transactions spanning the period from BCT's launch in October 2021 to the effective cessation of new deposits in late 2022. These 1,187 deposits mapped to 90 unique VCS project identifiers and approximately 22 million tonnes of tokenized carbon credits.

For each deposit, we recorded: the transaction hash, block number and timestamp, depositor address, TCO2 token contract address, Verra VCS project identifier (extracted from the TCO2 token metadata), vintage year, and tonnage deposited. Project identifiers were cross-referenced against the Verra registry to obtain methodology category (e.g., VM0007 for REDD+, AMS-I.D for grid-connected renewables), country of origin, and CCP eligibility status.

**Project classification.** Each of the 90 unique projects was classified into one of six methodology categories based on the Verra registry entry: (i) renewable energy (grid-connected wind, hydro, solar, and geothermal; CDM methodologies AMS-I.D, ACM0002, and equivalents), (ii) REDD+ (avoided deforestation and reduced degradation; VM0007, VM0009, VM0015, VM0006), (iii) waste management and methane capture (landfill gas, waste-to-energy; AMS-III.G, ACM0001), (iv) industrial gas destruction (HFC-23, N$_2$O; AM0001, AM0021), (v) energy efficiency and fuel switching (AMS-II.G, AMS-III.B), and (vi) unclassified (projects not falling into the above categories). Tonnage-weighted shares were computed for each category. Classification was performed by the authors based on Verra's published methodology descriptions; we did not independently verify registry-assigned categories.

**Tonnage weighting.** Pool-level composition statistics and quality metrics were computed with tonnage weighting: a project contributing 500,000 tonnes to the pool received 50 times the weight of a project contributing 10,000 tonnes. This reflects the pool's actual quality exposure: a single large deposit of low-quality credits has a greater impact on the pool's average quality than many small deposits of high-quality credits.

## Quality scoring framework

We developed a composite quality scoring framework evaluating seven dimensions identified in the integrity literature as the primary determinants of credit quality. Each credit was scored on a 0--100 scale across six active dimensions: removal type hierarchy (weight 0.250), additionality (0.200), monitoring, reporting, and verification (MRV) grade (0.200), permanence (0.175), vintage year (0.100), and registry and methodology quality (0.075). Weights were chosen to reflect the relative importance assigned by the Oxford Offsetting Principles^1^ and the ICVCM CCP Assessment Framework^2^, with removal type receiving the largest weight to encode the Oxford hierarchy (removal > avoidance > reduction).

The seventh dimension, co-benefits, was assigned a weight of zero and converted to a binary disqualifier gate (the "safeguards-gate"). This design decision followed from Berg et al.^3^, who found that buyers pay approximately double the premium for credits with co-benefit narratives regardless of underlying integrity. Including co-benefits as a scored dimension would therefore amplify adverse selection by inflating the scores of credits whose quality deficits are obscured by compelling co-benefit narratives. We retained the co-benefits rubric as an informational field and used its scoring bands to determine whether to flag the community-harm disqualifier.

The composite score was computed as:

$$C = \sum_{i=1}^{7} w_i \times s_i$$

where $w_i$ is the weight and $s_i$ is the per-dimension score for dimension $i$, with $w_{\text{co-benefits}} = 0$. Composites were mapped to letter grades: AAA ($\geq$90), AA ($\geq$75), A ($\geq$60), BBB ($\geq$45), BB ($\geq$30), and B (<30).

Seven disqualifier conditions cap the maximum achievable grade regardless of composite score. Three conditions cap at grade B (evidence of double counting, failed verification, credible human rights violation claims). One condition caps at BB (registry or methodology under sanction). Three conditions cap at BBB (no independent third-party verification, documented community opposition or environmental damage, published evidence of biodiversity loss^4^). Disqualifiers were applied after composite scoring and never raised a grade, only lowered it.

**Distributional scoring.** Each per-dimension score was modelled as normally distributed around its point estimate, with standard deviations calibrated from the inter-rater reliability study. Calibrated per-dimension standard deviations ranged from $\sigma$ = 4.0 (permanence) to $\sigma$ = 11.1 (registry and methodology). Under the assumption of independent dimension scores, composite variance was computed as:

$$\text{Var}(C) = \sum_{i} w_i^2 \times \sigma_i^2$$

Grade posteriors were computed via the Gaussian CDF: $P(\text{grade} = G) = \Phi\bigl(\frac{u_G - \mu}{\sigma_C}\bigr) - \Phi\bigl(\frac{l_G - \mu}{\sigma_C}\bigr)$, where $l_G$ and $u_G$ are the lower and upper boundaries of grade $G$, $\mu$ is the composite point estimate, and $\sigma_C = \sqrt{\text{Var}(C)}$. The reported grade was the posterior mode. Machine-readable rubrics are provided in JSON format at `data/scoring-rubrics/`.

## Pool Quality Deficit

We defined the Pool Quality Deficit (PQD) to quantify quality degradation in a carbon credit pool:

$$\text{PQD}(\text{pool}) = 1 - \frac{\bar{C}}{100}$$

where $\bar{C}$ is the tonnage-weighted mean composite score of all credits in the pool. The PQD ranges from 0 (every credit scores 100; no quality degradation) to 1 (every credit scores 0; complete quality failure). Higher values indicate worse quality. The metric is interpretable, pool-comparable, and computable from publicly available project data.

For BCT, $\bar{C}$ was computed as the tonnage-weighted mean across all 90 unique projects, using the composite scores from methodology-level archetypes with per-project vintage adjustments. For the 34-segment quality atlas, PQD was computed per segment using the methodology archetype score for each segment.

**Null model.** To establish a baseline expectation for PQD under random credit selection, we sampled 90 projects uniformly at random (with replacement) from the full 318-credit methodology dataset 10,000 times. For each sample, we computed the mean composite and the resulting PQD. The null-model PQD distribution (mean = 0.510, SD = 0.028) provides a reference against which observed pool PQDs can be compared. A pool with PQD significantly above 0.510 exhibits quality degradation consistent with adverse selection; a pool with PQD significantly below 0.510 exhibits quality enrichment consistent with positive selection.

## CCP empirical calibration

We tested whether the framework's composite scores separated CCP-eligible from non-CCP credits using a dataset of 318 credits classified by ICVCM CCP eligibility status (165 CCP-eligible, 153 non-CCP) across 17 methodology categories. CCP classification was based on the ICVCM's published list of CCP-approved methodologies and CCP-eligible programmes as of 2025.

Five effect size measures were computed: Cohen's $d$ (pooled standard deviation), Glass's $\delta$ (using non-CCP standard deviation as denominator), Cliff's $\delta$ (nonparametric), the common language effect size (CLES), and a Mann--Whitney $U$ test with normal-approximation $z$-score including tie correction. For each parametric and nonparametric effect size, 95% confidence intervals were obtained via the percentile bootstrap method with 10,000 resamples (seed = 42). Grade distributions were encoded on an ordinal scale (B = 0, BB = 1, BBB = 2, A = 3, AA = 4, AAA = 5).

## Rank correlation with commercial rating agencies

We assessed external validity by computing rank correlations between our framework's grades and publicly available ratings from three commercial carbon credit rating agencies: BeZero Carbon, Calyx Global, and Sylvera.

**REDD+ subset.** Six REDD+ projects were drawn from Carbon Market Watch^5^ (2023, Table 20), which reported simultaneous public ratings from all three agencies as of 2 June 2023. Each agency's ordinal scale was mapped to a monotonic integer sequence (higher = better quality), and each project was scored under our framework. Spearman rank correlations ($\rho$) and Kendall's $\tau$-b were computed for all six pairwise combinations of four raters (our framework, BeZero, Calyx, Sylvera).

**Cross-type extension.** An additional 9 projects spanning seven non-REDD+ methodology types (direct air capture, biochar, cookstoves, improved forest management, methane abatement, landfill gas, renewable energy) were compiled from BeZero case studies, Calyx research publications, and Sylvera press releases. These were scored under the v0.6 rubric and correlated against each agency where pairwise coverage existed.

**Statistical inference.** For the combined dataset (REDD+ and cross-type, $n$ = 15), Spearman $\rho$ was computed with 10,000-resample percentile bootstrap 95% confidence intervals and a two-sided permutation test $p$-value (10,000 permutations, seed = 42). We report significance at $\alpha$ = 0.05. Sub-type correlations were computed for CDR credits ($\rho$ = +0.973) and avoidance credits ($\rho$ = +0.802) separately, though sub-type sample sizes are small and these should be interpreted as directional evidence.

## Inter-rater reliability study

To assess reproducibility, we conducted an inter-rater reliability study using three independent large language model raters: Claude Opus 4.6, Claude Sonnet 4.6, and Claude Haiku 4.5 (Anthropic, 2025). Each model scored 29 credits (25 real-world archetypes plus 4 synthetic stress-test credits) using the v0.4.1 rubric in isolated sessions with author grades redacted. No inter-rater communication was permitted.

Agreement metrics: (i) Fleiss' $\kappa$ across the three raters at the grade level (six categories: B through AAA); (ii) per-dimension Fleiss' $\kappa$, with continuous scores binned into 10 buckets of 10 points each; (iii) ICC(2,$k$) on the continuous composite using a two-way random effects model; (iv) exact grade agreement and within-one-band agreement between the author's grades and the panel median.

Per-dimension kappa values: permanence 0.684 (substantial), removal type 0.585 (moderate), vintage year 0.324 (fair), MRV 0.248 (fair), additionality 0.243 (fair), co-benefits 0.182 (slight), registry methodology 0.168 (slight). Per-dimension standard deviations from this study were used to calibrate the distributional scoring model.

## Sensitivity analysis

**Monte Carlo weight perturbation.** We sampled 10,000 weight vectors from a Dirichlet distribution centred on the current weights with concentration parameter 50, with co-benefits weight forced to zero. For each sampled vector, all 29 credits were rescored and assigned a grade. Global robustness was defined as the mean proportion of iterations under which each credit's grade remains unchanged (93.7% at concentration 50; 90.1% at concentration 20; 95.4% at concentration 100).

**Removal-type sensitivity.** To test whether the framework's discriminatory power depends on the removal-type dimension --- which carries the largest single weight (0.25) and which some critics may view as normatively contestable --- we set the removal-type weight to zero and redistributed its weight proportionally across the remaining dimensions. Quality differences between credit categories persisted at 98% significance under this perturbation, indicating that the framework's quality discrimination is distributed across multiple dimensions rather than concentrated in removal type.

**Cross-temporal stability.** The same 29 credits were scored under three methodology versions (v0.3, v0.4, v0.6). Grade agreement between v0.4 and v0.6 was 100% (29/29). Spearman $\rho$ between v0.3 and v0.6 composite rankings was 0.992.

## Counterfactual quality-gate simulation

For BCT and five additional pools, we simulated the application of quality gates at all six grade thresholds (B, BB, BBB, A, AA, AAA). At each threshold, only credits whose final grade met or exceeded the threshold were admitted. We recomputed: the number of admitted credits, the new tonnage-weighted mean composite, the resulting PQD, and the fraction of admitted credits at grade A or above.

## 34-segment quality atlas

We defined 34 quality segments by the intersection of project type (17 methodology categories from the ICVCM taxonomy), geographic region (where sufficient data existed), and vintage band (pre-2015, 2015--2019, 2020--2023, 2024+). Each segment was scored using the median archetype score from the 318-credit methodology dataset. PQD was computed per segment. The vintage gradient was computed as the tonnage-weighted mean PQD across all segments within each vintage band.

## Data availability

All data, scoring rubrics, analysis scripts, and smart contract source code are available at https://github.com/Adeline117/carbon-neutrality under an MIT licence. Machine-readable rubrics are in JSON format (`data/scoring-rubrics/`). The 318-credit methodology batch dataset with per-dimension scores is included. On-chain deposit data (547 transactions) are provided with transaction hashes enabling independent verification on the Polygon blockchain. LLM panel outputs for all three models across 29 credits are provided at `data/llm-panel-irr/raw/`. Analysis scripts are pure Python with no external dependencies.

## References

1. Allen, M. et al. The Oxford Principles for Net Zero Aligned Carbon Offsetting. University of Oxford (2020).
2. Integrity Council for the Voluntary Carbon Market. The Core Carbon Principles, Assessment Framework and Assessment Procedure. ICVCM (2023).
3. Berg, F., Kolbel, J., Pavlova, A. & Rigobon, R. The market for voluntary carbon offsets. SSRN Working Paper (2025).
4. Zeng, Y. et al. Biodiversity risks of carbon offset projects. *Nat. Rev. Biodivers.* (2026).
5. Carbon Market Watch & Perspectives Climate Group. Assessing and comparing carbon credit rating agencies. Carbon Market Watch Policy Brief (2023).
6. Akerlof, G. A. The market for "lemons": quality uncertainty and the market mechanism. *Q. J. Econ.* **84**, 488--500 (1970).
