# Methods

## 4. Methods

### Quality scoring framework

We developed a composite quality scoring framework for carbon credits that evaluates seven dimensions identified in the integrity literature as primary determinants of credit quality. Each credit was scored on a 0--100 scale across six active dimensions: removal type hierarchy (weight 0.250), additionality (0.200), monitoring, reporting, and verification (MRV) grade (0.200), permanence (0.175), vintage year (0.100), and registry and methodology quality (0.075). Weights reflect the relative importance assigned by the Oxford Offsetting Principles and the ICVCM Core Carbon Principles Assessment Framework, with removal type receiving the largest weight to encode the Oxford hierarchy (removal > avoidance > reduction).

The seventh dimension, co-benefits, was assigned a weight of zero and converted to a binary disqualifier gate. This design decision followed from evidence that buyers pay approximately double the premium for credits with co-benefit narratives regardless of underlying integrity. Including co-benefits as a scored dimension would amplify the adverse selection mechanism the framework was designed to detect. We retained the co-benefits rubric as an informational field and used its scoring bands to determine whether to flag the community harm disqualifier.

The composite score was computed as:

$$C = \sum_{i=1}^{7} w_i \times s_i$$

where $w_i$ is the weight and $s_i$ is the per-dimension score for dimension $i$, with $w_{\text{co-benefits}} = 0$. Composites were mapped to letter grades: AAA ($\geq$90), AA ($\geq$75), A ($\geq$60), BBB ($\geq$45), BB ($\geq$30), and B (<30).

Seven disqualifier conditions cap the maximum achievable grade regardless of composite score. Three conditions cap at grade B (evidence of double counting, failed verification, credible human rights violation claims). One condition caps at BB (registry or methodology under sanction). Three conditions cap at BBB (no independent third-party verification, documented community opposition or environmental damage, published evidence of biodiversity loss). Disqualifiers are applied after composite scoring and never raise a grade.

**Distributional scoring.** To propagate scoring uncertainty into grade assignments, we modelled each per-dimension score as normally distributed around its point estimate, with standard deviations calibrated empirically from the inter-rater reliability study. Calibrated per-dimension standard deviations ranged from $\sigma = 4.0$ (permanence) to $\sigma = 11.1$ (registry and methodology). Under the assumption of independent dimension scores, the composite variance was computed as:

$$\text{Var}(C) = \sum_{i} w_i^2 \times \sigma_i^2$$

Grade posteriors were computed via the Gaussian cumulative distribution function: $P(\text{grade} = G) = \Phi\bigl(\frac{u_G - \mu}{\sigma_C}\bigr) - \Phi\bigl(\frac{l_G - \mu}{\sigma_C}\bigr)$, where $l_G$ and $u_G$ are the lower and upper boundaries of grade $G$, $\mu$ is the composite point estimate, and $\sigma_C = \sqrt{\text{Var}(C)}$. The reported grade was the posterior mode. Machine-readable rubrics are provided in JSON format at `data/scoring-rubrics/`.

### CCP calibration protocol

We tested whether the framework's composite scores separated CCP-eligible from non-CCP credits using a dataset of 318 credits classified by ICVCM CCP eligibility status (165 CCP-eligible, 153 non-CCP) across 17 methodology categories. CCP classification was based on the ICVCM's published list of CCP-approved methodologies and CCP-eligible programmes as of 2025.

Five effect size measures were computed: Cohen's $d$ (pooled standard deviation), Glass's $\delta$ (using non-CCP standard deviation as denominator), Cliff's $\delta$ (nonparametric), the common language effect size (CLES), and a Mann--Whitney $U$ test with normal-approximation $z$-score including tie correction. For each effect size, 95% confidence intervals were obtained via the percentile bootstrap method with 10,000 resamples (seed = 42). Grade distributions were encoded on an ordinal scale (B = 0, BB = 1, BBB = 2, A = 3, AA = 4, AAA = 5).

### Rank correlation methodology

We assessed external validity by computing rank correlations between our framework's grades and publicly available ratings from three commercial carbon credit rating agencies: BeZero Carbon, Calyx Global, and Sylvera.

**REDD+ subset.** Six REDD+ projects were drawn from Carbon Market Watch (2023, Table 20), which reported simultaneous public ratings from all three agencies as of 2 June 2023. Each agency's ordinal scale was mapped to a monotonic integer sequence (higher = better quality), and each project was scored under our framework. Spearman rank correlations ($\rho$) and Kendall's $\tau$-b were computed for all six pairwise combinations of four raters.

**Cross-type extension.** An additional 21 projects spanning eight non-REDD+ methodology types (direct air capture, biochar, cookstoves, improved forest management, methane abatement, landfill gas, renewable energy, enhanced weathering) were compiled from BeZero case studies, Calyx research publications, Sylvera press releases, and project developer announcements. Projects were included only when a specific letter-grade rating was published in a publicly accessible source (no paywalled data). Each project was scored under the v0.6 rubric using the closest methodology archetype as a baseline, with per-project adjustments for vintage, MRV specifics, additionality evidence, and CCP status.

**Combined dataset.** The REDD+ and cross-type datasets were pooled to produce a combined sample of *n* = 27 projects with pairwise coverage against BeZero. Spearman $\rho$ was computed with 10,000-resample percentile bootstrap 95% confidence intervals and a two-sided permutation test $p$-value (10,000 permutations, seed = 42).

**Subgroup analysis.** Separate correlations were computed for carbon dioxide removal projects (DACCS, biochar, enhanced weathering) and avoidance projects (cookstoves, landfill gas, renewable energy) to test whether agreement varies by project type, as the literature predicts that inter-agency disagreement is concentrated in avoided-deforestation and nature-based projects.

### Inter-rater reliability study

We assessed reproducibility of the scoring framework using a panel of three independent large language model raters: Claude Opus 4.6, Claude Sonnet 4.6, and Claude Haiku 4.5 (Anthropic, 2025). Each model scored 29 credits (25 real-world archetypes plus 4 synthetic stress-test credits) using the v0.4.1 rubric. No inter-rater communication was permitted: each model received an identical prompt containing the complete rubric and publicly available project documentation, and returned per-dimension scores and disqualifier flags independently.

Agreement metrics computed: (i) Fleiss' $\kappa$ across the three LLM raters at the grade level (six categories: B through AAA); (ii) per-dimension Fleiss' $\kappa$, with continuous scores binned into 10-point buckets; (iii) the intraclass correlation coefficient ICC(2,$k$) on the continuous composite, using a two-way random effects model with mean-of-$k$-raters consistency; (iv) exact grade agreement and within-one-band agreement between the author's grades and the LLM panel's median grade.

Four synthetic stress-test credits were constructed with known correct disqualifiers (double counting, sanctioned registry, no third-party verification, community harm) to test disqualifier recall. All four were correctly identified by the panel. Per-dimension standard deviations from this study were used to calibrate the distributional scoring model.

**Limitations acknowledged.** The single-provider LLM panel (*kappa* = 0.600) establishes baseline reproducibility but cannot rule out correlated biases shared across Claude-family models. Per-dimension reliability varied substantially: permanence ($\kappa$ = 0.684, substantial) and removal type ($\kappa$ = 0.585, moderate) showed the strongest agreement, consistent with their crisper categorical rubric distinctions. Additionality ($\kappa$ = 0.243, fair) and MRV ($\kappa$ = 0.248, fair) showed weaker agreement, reflecting the inherent subjectivity in assessing counterfactual baselines and verification quality from documentary evidence. The high composite ICC (0.993) despite moderate per-dimension kappa values is a designed property: the weighted composite mean smooths out per-dimension noise, producing stable grades even when individual dimension scores diverge.

### Depositor analysis

**Event extraction.** All `Deposited` and `Redeemed` events were extracted from Toucan Protocol's pool contracts on Polygon for BCT (contract address [PLACEHOLDER]), NCT, and CHAR. For each event, we recorded the depositor address, the TCO2 token contract address (identifying the underlying credit type), the amount deposited, and the block timestamp. Transfer events on each TCO2 token contract were separately extracted to reconstruct the complete holding history of each depositor address.

**Portfolio reconstruction.** For each address that deposited into BCT, we computed: (i) the set of TCO2 token types deposited, (ii) the set of TCO2 token types held at the time of deposit but not deposited, and (iii) the quality score of each TCO2 token type, assigned by mapping the token's underlying credit to its methodology archetype in the 318-credit batch dataset. A depositor's quality delta -- the Selection Index (SI) for that depositor -- was defined as:

$$\text{SI}_i = \bar{C}_{\text{deposited},i} - \bar{C}_{\text{retained},i}$$

where $\bar{C}_{\text{deposited},i}$ is the mean composite score of credits deposited by address $i$ and $\bar{C}_{\text{retained},i}$ is the mean composite of credits held but not deposited. Analysis was restricted to addresses holding at least two distinct TCO2 token types to enable within-depositor comparison.

**Statistical tests.** The Wilcoxon signed-rank test was applied to the vector of per-depositor Selection Indices to test the null hypothesis that the median SI is zero. Cohen's *d* for paired samples was computed as the mean SI divided by the standard deviation of SI values. The selection rate was defined as the proportion of depositors with negative SI (deposited credits scoring lower than retained credits). Time stratification split the deposit record into six-month windows to test whether the selection effect changed over time.

**Robustness.** KlimaDAO's treasury addresses were identified from publicly documented wallet addresses and excluded in a sensitivity analysis, as KlimaDAO's accumulation strategy (bonding any available credits at market price) may not represent quality-selective deposit behaviour.

### Pool Quality Deficit, Selection Index, and null model

We define two complementary metrics that measure distinct aspects of quality failure in carbon credit pools.

**Pool Quality Deficit (PQD).** The Pool Quality Deficit (informally, the Lemons Index) quantifies pool-level quality degradation:

$$\text{PQD}(\text{pool}) = 1 - \frac{\bar{C}}{100}$$

where $\bar{C}$ is the mean composite score of all credits in the pool. The index ranges from 0 (every credit scores 100) to 1 (every credit scores 0). A high PQD is *consistent with* adverse selection but does not by itself prove it -- a pool could accumulate low-quality credits through mechanisms other than strategic depositor behaviour (e.g., if only low-quality credits were tokenized). The PQD measures the outcome (quality degradation) rather than the mechanism (strategic sorting).

**Selection Index (SI).** The Selection Index measures depositor-level strategic behaviour -- the mechanism predicted by Akerlof's model:

$$\text{SI}_i = \bar{C}_{\text{deposited},i} - \bar{C}_{\text{retained},i}$$

where $\bar{C}_{\text{deposited},i}$ is the mean composite score of credits deposited by address $i$ and $\bar{C}_{\text{retained},i}$ is the mean composite of credits held but not deposited. SI < 0 indicates that a depositor systematically deposits lower-quality credits while retaining higher-quality ones -- the behavioural signature of adverse selection. The pool-level Selection Index is the mean SI across all multi-holding depositors. SI is only computable when depositor portfolio data is available; PQD can be computed for any pool whose credit composition is known. Together, PQD measures the severity of quality degradation and SI identifies the depositor-level mechanism that produces it.

We computed PQD for six pool compositions drawn from publicly documented holdings: Toucan BCT (43 credits, 2022 peak), Toucan NCT (28 credits, 2023), Moss MCO2 (30 credits, 2022), Toucan CHAR (12 credits, Base, 2025), Klima 2.0 kVCM (20 credits, Base, 2026), and a hypothetical AAA-only pool (13 credits).

**Null model.** To establish a statistical baseline, we computed the expected PQD under random credit selection from the 318-credit population. For a pool of size $n$, we drew 100,000 random samples of $n$ credits (with replacement) and computed PQD for each sample. The null distribution's mean (0.51) and standard deviation (0.032 for $n$ = 43) provide the reference against which observed pool quality is evaluated. BCT's $z$-score of 6.2 against this null rejects random composition at any conventional significance level.

**Quality atlas.** PQD values were computed for 34 methodology-vintage segments by crossing the 17 methodology categories with vintage bins (pre-2016, 2016--2019, 2020--2023, 2024+) and retaining segments with $n \geq 5$ credits.

### Counterfactual quality-gate simulation

For each of six pools, we simulated the application of a quality gate at all six grade thresholds (B, BB, BBB, A, AA, AAA). At each threshold, only credits whose final grade met or exceeded the threshold were admitted. We then recomputed: the number of admitted credits, the new mean composite score, the resulting PQD, and the fraction of admitted credits at grade A or above.

The simulation assumes 100% gate accuracy -- that is, perfect correspondence between the framework's grade and the credit's true quality. This is an upper bound. In practice, scoring uncertainty (quantified by the distributional model) would produce false admissions and false rejections. The distributional scoring framework enables a probabilistic extension in which the gate admits credits whose $P(\text{grade} \geq \text{threshold}) > p$ for a configurable confidence level $p$, but we defer this extension to future work.

Four threshold levels were simulated across each pool to quantify the tradeoff between quality improvement (PQD reduction) and liquidity loss (fraction of credits excluded). The BBB threshold was identified as the minimum viable quality gate: it excludes the bulk of low-integrity credits (HFC-23 destruction, pre-2013 renewables, poorly verified REDD+) while retaining legitimate avoidance projects with adequate verification.

### Sensitivity and robustness

**Monte Carlo weight perturbation.** We assessed the robustness of grade assignments by sampling 10,000 random weight vectors from a Dirichlet distribution centred on the framework's weights (concentration parameter $\alpha$ = 50). The co-benefits weight was forced to zero in all samples. Per-credit grade stability was defined as the fraction of iterations retaining the baseline grade. Global robustness was 93.7% (24 of 29 pilot credits maintained their grade in >90% of draws). Five boundary-adjacent credits were flagged as fragile (stability <90%), all within 3 points of a grade boundary.

**Cross-temporal stability.** The same 29 pilot credits were scored under three framework versions (v0.3, v0.4, v0.6) differing in weight vectors and rubric definitions. The Spearman rank correlation between v0.3 and v0.6 composite scores was $\rho$ = 0.992, indicating near-perfect preservation of relative credit ordering across framework iterations.

### Data and code availability

All data, scoring rubrics, analysis scripts, and smart contract source code are available at https://github.com/Adeline117/carbon-neutrality under an MIT licence. Machine-readable rubrics are provided in JSON format. The 318-credit methodology batch dataset with per-dimension scores, raw LLM panel outputs for all three models, and counterfactual simulation results are included. Analysis scripts are pure Python with no external dependencies.
