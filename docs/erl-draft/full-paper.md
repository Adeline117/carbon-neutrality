# An open, distributional quality framework for voluntary carbon credits: validation against regulatory thresholds and commercial ratings

---

## Abstract

Commercial carbon credit rating agencies ask buyers to trust proprietary judgments they cannot reproduce, disagree with each other at levels indistinguishable from random, and provide no callable interface for automated quality enforcement. We present an open, seven-dimension quality framework that produces distributional grade posteriors P(grade) via Gaussian variance propagation, validated against the Integrity Council for the Voluntary Carbon Market's Core Carbon Principles (CCP) label and three commercial rating agencies. The framework recovers the CCP quality threshold with a 1.99-grade separation between CCP-eligible and non-CCP credits (Cohen's *d* = 1.80, common language effect size = 91.4%, *n* = 318), independently converging on Calyx Global's published measurement. On 27 projects spanning 12 credit types, Spearman rank correlation with BeZero Carbon is +0.901 (95% CI [+0.783, +0.959], *p* < 0.0001), with subgroup correlations of +0.973 for carbon dioxide removal and +0.802 for avoidance credits. The framework's mean correlation with commercial agencies (+0.343) exceeds the mean inter-agency correlation (+0.009) on a six-project overlap sample where BeZero and Calyx Global are anti-correlated at -0.664. Applied as a quality atlas across 34 market segments, the Lemons Index ranges from 0.076 (direct air capture) to 0.759 (renewable energy), with a null-model baseline of 0.51. Monte Carlo weight sensitivity analysis confirms 93.7% global grade robustness across 10,000 Dirichlet-sampled weight vectors. All rubrics, scoring code, and data are published under an open-source licence.

---

## 1. Introduction

In June 2023, Carbon Market Watch published the only publicly available multi-rater comparison of the three leading carbon credit rating agencies --- BeZero Carbon, Calyx Global, and Sylvera --- on the same six REDD+ projects [1]. The mean pairwise Spearman rank correlation among the three agencies was +0.009: effectively zero. BeZero and Calyx Global were not merely uncorrelated but strongly anti-correlated (*rho* = -0.664), meaning they systematically disagreed on which projects were higher and lower quality. One agency rated Keo Seima Wildlife Sanctuary at A; another rated it at E, the lowest possible grade. Yet voluntary carbon markets depend on these agencies to distinguish credits that represent real emission reductions from credits that do not. Annual trading volume surpassed $2 billion in 2023, and recent empirical work suggests that fewer than 16% of credits traded represent real emission reductions [2,3]. Corporate offset portfolios fare no better: 87% of credits retired by major firms carry high risk of non-additionality or over-crediting [4].

Three structural gaps underlie this problem. First, commercial ratings are proprietary: buyers cannot inspect the rubric, reproduce the score, or audit the weighting. When agencies disagree --- as they do on virtually every REDD+ project --- there is no way for a third party to adjudicate because neither agency's reasoning is fully public. Second, no commercial agency publishes distributional uncertainty. A credit rated "BBB" might sit comfortably in the middle of that grade band or perch 0.15 points above the boundary, yet the buyer receives the same point estimate in both cases. Third, and most fundamentally, no open, reproducible quality framework exists that provides both continuous scores and callable grade assessments against which market participants can benchmark commercial offerings.

The Integrity Council for the Voluntary Carbon Market (ICVCM) has partially addressed the first gap through its Core Carbon Principles (CCP) label, which certifies methodology-level quality [5]. CCP-labelled credits command a roughly 25% price premium [6], and Singapore's National Environment Agency in 2025 became the first sovereign body to mandate commercial ratings for carbon tax offset eligibility [7]. But CCP is a binary label at the methodology level, not a continuous, credit-level quality measure.

Here we present an open quality framework designed to fill all three gaps simultaneously. The framework scores carbon credits on seven dimensions with published weights and machine-readable rubrics, propagates scoring uncertainty into distributional grade posteriors P(grade), and produces continuous composite scores validated against the CCP label and commercial ratings. We make three contributions. First, we demonstrate that the framework independently recovers the CCP quality threshold (1.99-grade separation, Cohen's *d* = 1.80), converging with Calyx Global's independently published measurement without training on CCP labels --- analogous to a new instrument confirming a known physical constant. Second, we show that the framework's mean rank correlation with commercial agencies (+0.343) exceeds the agencies' mean correlation with each other (+0.009), and that on an expanded 27-project, 12-type dataset, Spearman correlation with BeZero reaches +0.901 (95% CI [+0.783, +0.959]). Third, we publish grade posteriors P(grade) for every scored credit, making the framework the first to provide distributional quality estimates for voluntary carbon credits. All rubrics, code, and data are open-source.

---

## 2. Methods

### 2.1 Scoring framework

The framework evaluates each carbon credit on seven dimensions identified in the integrity literature as the primary determinants of credit quality: removal type hierarchy (weight 0.250), additionality (0.200), monitoring, reporting, and verification (MRV; 0.200), permanence (0.175), vintage year (0.100), co-benefits (0.000, safeguards-gate only), and registry and methodology quality (0.075). Weights encode the Oxford Offsetting Principles hierarchy (removal > avoidance > reduction) [8] and the ICVCM CCP Assessment Framework priorities [5].

Co-benefits receive zero weight and serve only as a binary disqualifier gate. This design follows Berg et al. [9], who found that buyers pay approximately double the premium for credits with co-benefit narratives regardless of underlying integrity; including co-benefits as a scored dimension would amplify the information asymmetry the framework is designed to detect.

The composite score is the weighted linear sum:

$$C = \sum_{i=1}^{7} w_i \times s_i$$

where *w_i* and *s_i* are the weight and per-dimension score (0--100) for dimension *i*. Composites map to six-tier letter grades: AAA (>=90), AA (>=75), A (>=60), BBB (>=45), BB (>=30), and B (<30). Seven disqualifier conditions impose grade caps that override the composite: double counting and failed verification cap at B; sanctioned registry at BB; no third-party verification, community harm, and documented biodiversity loss cap at BBB.

### 2.2 Distributional scoring and variance propagation

To propagate scoring uncertainty into grade assignments, each per-dimension score is modelled as normally distributed around its point estimate, with standard deviations calibrated empirically from the inter-rater reliability study (section 2.5). Calibrated per-dimension standard deviations range from *sigma* = 4.0 (permanence) to *sigma* = 11.1 (registry and methodology), reflecting observed inter-rater disagreement. Under the assumption of independent dimension scores, the composite variance is:

$$\text{Var}(C) = \sum_{i} w_i^2 \times \sigma_i^2$$

Grade posteriors are computed via the Gaussian cumulative distribution function: P(grade = *G*) = Phi((u_G - mu)/sigma_C) - Phi((l_G - mu)/sigma_C), where l_G and u_G are the grade boundaries, mu is the composite point estimate, and sigma_C is the composite standard deviation. The reported grade is the posterior mode.

### 2.3 Lemons Index as quality atlas metric

To characterize quality across market segments, we employ the Lemons Index *L* = 1 - (mean composite / 100), bounded between 0 (perfect quality) and 1 (complete quality failure), computed from the composite scores of all credits in a defined pool or segment [10]. We apply this metric across 34 pool segments defined by project type, registry, vintage era, and CCP status, computed from a 318-credit batch dataset scored via methodology-level archetypes. A Monte Carlo null model (10,000 iterations of random sampling from the 318-credit market) provides the baseline expectation under random credit assignment (LI = 0.51, SD = 0.036 for *n* = 30).

### 2.4 CCP calibration protocol

The 318-credit dataset was split by ICVCM CCP eligibility status (165 CCP-eligible, 153 non-CCP) across 17 methodology categories. CCP classification followed the ICVCM's published list of approved methodologies and eligible programmes as of 2025. Five effect size measures were computed: Cohen's *d* (pooled SD), Glass's delta, Cliff's delta (nonparametric), the common language effect size (CLES), and a Mann--Whitney *U* test. For each, 95% confidence intervals were obtained via percentile bootstrap (10,000 resamples, seed = 42).

### 2.5 Rank correlation methodology

External validity was assessed by computing Spearman rank correlations between framework grades and publicly available ratings from BeZero Carbon, Calyx Global, and Sylvera. On a six-project REDD+ overlap sample from Carbon Market Watch [1], all six pairwise correlations among four raters (framework + three agencies) were computed. An expanded dataset of 27 projects spanning 12 project types (REDD+, DACCS, biochar, cookstoves, methane abatement, ODS destruction, enhanced weathering, J-REDD+, IFM, landfill gas, renewable energy, and ARR) was compiled from agency press releases, case studies, and public listings. Bootstrap 95% confidence intervals (10,000 percentile resamples), BCa-corrected CIs, one-sided permutation *p*-values (10,000 permutations), and leave-one-out cross-validation were computed. Subgroup analyses were conducted for removal/CDR credits (*n* = 9) and avoidance credits (*n* = 18).

### 2.6 Inter-rater reliability study design

Reproducibility was tested using a panel of three Claude-family language models (Opus 4.6, Sonnet 4.6, Haiku 4.5), each scoring 29 credits independently in isolated sessions using redacted evidence packs with author grades removed. We computed Fleiss' kappa at the grade level, per-dimension Fleiss' kappa (10-point bucketed scores), and ICC(2,*k*) on the continuous composite. We acknowledge upfront that this is a single-provider panel: all three models share training data and alignment procedures, which may produce correlated biases invisible to within-family comparisons. A multi-provider replication (GPT-5, Gemini, open-weight models) and a human expert panel are planned as explicit next steps.

---

## 3. Results

### 3.1 CCP calibration independently recovers the regulatory quality threshold

The framework produced a 1.99-grade separation between CCP-eligible credits (*n* = 165, mean ordinal grade = 2.69 on a 0--5 scale where B = 0 and AAA = 5) and non-CCP credits (*n* = 153, mean ordinal grade = 0.70). The effect size was large: Cohen's *d* = 1.80 (95% CI: 1.50--2.16), Cliff's delta = 0.83 (95% CI: 0.75--0.90), and CLES = 91.4% (95% CI: 87.5--94.8%). A Mann--Whitney *U* test confirmed significance (*z* = 13.06, *p* approximately 0).

The distributions were nearly non-overlapping. No CCP-eligible credit scored B; no non-CCP credit scored A or AAA. The modal grade for CCP-eligible credits was BBB (43%); for non-CCP credits, B (54%). Overlap was confined to BB (11% of CCP, 39% of non-CCP) and AA (17% of CCP, 8% of non-CCP).

This result was not designed. The framework was constructed from the Oxford Principles hierarchy and literature-derived dimension definitions, without fitting to CCP labels or optimizing for CCP separation. That it independently recovers the approximately two-grade-level gap that Calyx Global --- an ICVCM-appointed rating agency --- reported between CCP-eligible projects (averaging A on their proprietary scale) and non-CCP projects (averaging C) [11] constitutes convergent validation. If the weights were miscalibrated --- overweighting or underweighting the dimensions that CCP selects for --- the separation would be either implausibly wide or implausibly narrow. A 1.99-grade gap matching an independent measurement from a different framework with different dimension definitions is the quality-assessment equivalent of a new instrument confirming a known physical constant.

### 3.2 Framework agreement exceeds inter-agency agreement

On the six-project REDD+ overlap sample, the mean Spearman correlation between the framework and the three commercial agencies was *rho* = +0.343, compared with a mean inter-agency correlation of *rho* = +0.009. The inter-agency baseline is effectively zero. BeZero and Calyx Global were anti-correlated at *rho* = -0.664 on the same six projects, reflecting systematic disagreement on how to weight additionality concerns in avoided-deforestation projects. The framework's strongest pairwise agreement was with BeZero (*rho* = +0.664) and Sylvera (*rho* = +0.566); the weakest was with Calyx (*rho* = -0.200), reflecting Calyx's distinctively harsh treatment of REDD+ credits (five of six rated at E).

That the framework correlates more strongly with each agency than the agencies correlate with each other suggests it measures the signal that each agency captures partially. BeZero weights additionality as a "limiting factor"; Calyx applies strict cross-sectoral caps; Sylvera uses a 100-year permanence benchmark. The framework's weighted composite smooths these divergent emphases into a single ordering that tracks each agency's direction without replicating any single agency's idiosyncratic penalty structure.

When expanded to 27 projects spanning 12 project types, the correlation with BeZero rose to *rho* = +0.901 (95% CI [+0.783, +0.959], Kendall *tau* = +0.821, permutation *p* < 0.0001). Exact grade match was 52% (14/27); within-one-grade agreement was 100% (27/27). Leave-one-out cross-validation confirmed stability: LOO *rho* ranged from +0.889 to +0.922 (mean +0.901), with no single project changing *rho* by more than 0.021.

Subgroup analysis revealed stronger agreement on carbon dioxide removal credits (CDR: *rho* = +0.973, *n* = 9, *p* = 0.0003) than on avoidance credits (*rho* = +0.802, *n* = 18, *p* < 0.0001). This asymmetry is consistent with the wider literature: inter-agency disagreement is concentrated in REDD+ and nature-based credits where baseline counterfactuals are inherently uncertain, while engineered removal and industrial avoidance credits generate broader consensus [1].

One systematic divergence warrants disclosure. The framework ranks cookstove credits lower than some agencies because the removal-type dimension applies the Oxford Principles hierarchy, which scores avoidance credits below removal credits regardless of co-benefit narratives. The safeguards-gate design --- removing co-benefits from the composite and using them only as a disqualifier trigger --- prevents narrative washing from inflating composite scores but produces systematic divergence from agencies that weight co-benefits positively.

### 3.3 Inter-rater reliability

Grade-level Fleiss' kappa across the three-rater LLM panel was 0.600, at the boundary of Landis and Koch's "substantial" agreement threshold [12]. Composite-level ICC(2,*k*) was 0.993 (near-perfect). The author's grades matched the panel median on 25 of 29 credits (86%), with every discrepancy confined to a single adjacent grade band (100% within +/-1).

Per-dimension reliability varied. Permanence (*kappa* = 0.684) and removal type (*kappa* = 0.585) --- the two highest-weighted dimensions --- showed the strongest agreement. Additionality (*kappa* = 0.243) and MRV (*kappa* = 0.248) showed fair agreement. Registry methodology (*kappa* = 0.168) was weakest, motivating a simplification to a two-tier CCP-eligible/non-CCP scheme. The high composite ICC despite moderate per-dimension kappa is a designed property: the weighted composite mean smooths per-dimension noise, producing stable grades even when individual dimension scores diverge by 5--12 points.

The single-provider limitation is real. All three raters are Claude models sharing training data and alignment procedures. We cannot rule out correlated biases invisible to within-family comparisons. A multi-provider replication incorporating models from different providers, followed by a human expert panel, is the necessary next step before claiming that rubric reproducibility generalizes beyond this model family.

### 3.4 Quality atlas: 34 market segments

Applied systematically across 34 pool segments defined by project type, registry, vintage era, and CCP status, the Lemons Index ranges from 0.076 (DACCS pool, *n* = 14, mean composite = 92.4) to 0.759 (renewable energy pool, *n* = 40, mean composite = 24.1). The full 318-credit market has LI = 0.510, matching the null-model baseline (0.51) --- random credit aggregation produces average-market quality by construction.

CCP eligibility acts as a meaningful but incomplete quality filter: CCP-eligible credits (LI = 0.419, *n* = 201) score 0.248 points better than non-CCP credits (LI = 0.667, *n* = 117), a 37% reduction in adverse selection severity. Vintage is a secondary predictor: pre-2020 credits (LI = 0.687) score markedly worse than 2024+ credits (LI = 0.273). Project type is the strongest quality lever: a DACCS-only or biochar-only pool achieves LI < 0.22 regardless of vintage or registry.

### 3.5 Weight robustness

Monte Carlo simulation with 10,000 Dirichlet-sampled weight vectors (concentration = 50) yielded 93.7% global grade robustness: the mean proportion of weight draws under which each credit's grade remains unchanged. At wider prior (concentration = 20), robustness was 90.1%; at tighter prior (concentration = 100), 95.4%. Five credits were flagged as fragile (stability < 90%), all sitting within 3 points of a grade boundary. At the extremes --- Climeworks Orca (AAA, 100% stable), Kariba REDD+ (B, 100% stable) --- the framework produced invariant grades regardless of weight perturbation.

Deterministic sensitivity confirmed the pattern: shifting any single dimension's weight by +/-5 percentage points caused a maximum of 3 grade flips out of 29 credits. Leave-one-out analysis (dropping each dimension entirely) caused a maximum of 4 grade flips. Cross-temporal stability between framework versions v0.3 and v0.6 showed Spearman *rho* = 0.992 on composite rankings, with decreasing perturbation magnitude across versions (5 grade changes in v0.3-to-v0.4, 0 in v0.4-to-v0.6), providing evidence of convergence.

---

## 4. Discussion

### 4.1 What makes this not another rating agency

The framework differs from commercial rating agencies in three structural ways. It is open: all rubrics are machine-readable JSON, the scoring engine is open-source Python, and the full dataset is published. It is reproducible: any researcher can substitute alternative weights and recompute every result. And it is distributional: instead of point-estimate grades, it publishes P(grade) posteriors that quantify boundary uncertainty. A credit sitting 0.15 points above the AAA threshold (such as Charm Industrial bio-oil injection) receives a posterior that reflects this precariousness; a credit sitting 5 points above receives a tighter posterior. This transparency is absent from current commercial offerings.

The CCP calibration result is particularly instructive. The framework was not designed to recover a specific effect size; the 1.99-grade gap and *d* = 1.80 emerged from independently chosen dimension definitions and weights. That this matches Calyx Global's independently published measurement suggests that the weight vector, while derived from literature synthesis rather than structured expert elicitation, captures the quality signal that the ICVCM's multi-year consultation process distilled into the CCP label. The convergence is not trivially guaranteed: a framework that overweighted permanence relative to additionality, or that failed to penalize avoidance credits appropriately, would produce a different separation.

### 4.2 Limitations

We are candid about five limitations. First, all credit scores derive from a single research group's judgment applied to public project documentation. Author-derived scores may carry systematic biases that expert elicitation would correct. We have identified 20 domain experts for a Best-Worst Scaling consultation designed to produce empirically grounded weight priors.

Second, the inter-rater reliability study uses a single-provider LLM panel. The kappa = 0.600 and ICC = 0.993 results are encouraging but may be inflated by within-family correlation. Multi-provider replication (GPT-5, Gemini, open-weight models) is necessary before claiming generalizable reproducibility.

Third, the sample size for rank correlation, while substantially larger than previous analyses (*n* = 27 versus the typical *n* = 6 overlap), remains modest. Confidence intervals narrow but do not eliminate uncertainty, particularly for the REDD+-only subsample where agency disagreement is most acute.

Fourth, the framework rates credits on public documentation only, which may miss proprietary information available to commercial agencies with registry partnerships. This is a deliberate design choice favouring reproducibility over coverage, but it means the framework cannot assess dimensions that depend on private data.

Fifth, additionality remains the weakest scoring dimension across all raters (kappa = 0.243), reflecting the fundamental difficulty of assessing counterfactual baselines from documentary evidence. This limitation is shared by every carbon quality assessment system and is the primary driver of inter-agency disagreement on projects where additionality is ambiguous.

### 4.3 Future directions

The framework's architecture is designed for iterative improvement. Structured expert elicitation via Best-Worst Scaling will replace literature-derived weight priors with empirically grounded estimates. Multi-provider LLM replication will test whether rubric reproducibility extends beyond Claude-family models. Expansion of the rank correlation dataset to include underrepresented project types (ocean alkalinity enhancement, tidal wetland restoration) will test generalizability at the frontier of carbon removal innovation. This framework has been applied to depositor-level adverse selection analysis in tokenized carbon credit pools (companion empirical paper [29] submitted to *Nature Communications*), where the Lemons Index serves as the quality metric for measuring pool-level quality degradation. A companion systems paper [30] (submitted to *Proc. WWW 2027*) implements the framework as a composable on-chain smart contract interface (ERC-CCQR) that enables automated quality gating at the protocol level.

---

## 5. Data availability

All scoring rubrics, analysis scripts, and data are available at https://github.com/Adeline117/carbon-neutrality under an MIT licence. Machine-readable rubrics are in JSON format. The 318-credit batch dataset with per-dimension scores, all LLM panel outputs, bootstrap analysis scripts, and the systematic Lemons Index scan are included. The framework is designed so that any researcher can substitute alternative weights and reproduce every result in this paper.

---

## References

1. Carbon Market Watch & Perspectives Climate Group. Assessing and comparing carbon credit rating agencies. Carbon Market Watch Report (2023).
2. Calel, R., Colmer, J., Dechezlepretre, A. & Glachant, M. Systematic assessment of the achieved emission reductions of carbon crediting projects. *Nat. Commun.* **15**, 5535 (2024).
3. West, T. A. P., Borner, J., Sills, E. O. & Kontoleon, A. Overstated carbon emission reductions from voluntary REDD+ projects in the Brazilian Amazon. *Science* **381**, 873--877 (2023).
4. Trencher, G. et al. Demand for low-quality offsets by major companies undermines climate integrity of the voluntary carbon market. *Nat. Commun.* **15**, 10890 (2024).
5. Integrity Council for the Voluntary Carbon Market. The Core Carbon Principles, Assessment Framework and Assessment Procedure. ICVCM (2023).
6. Sylvera. State of Carbon Credits 2025: From Volume to Value. Sylvera Research Report (2025).
7. Singapore National Environment Agency. Carbon rating panel: appointment of BeZero, Calyx Global, and Sylvera under the International Carbon Credit Framework. NEA Regulatory Notice (2025).
8. Allen, M. et al. The Oxford Principles for Net Zero Aligned Carbon Offsetting. University of Oxford (2020).
9. Berg, F., Kolbel, J., Pavlova, A. & Rigobon, R. The market for voluntary carbon offsets. SSRN Working Paper (2025).
10. Akerlof, G. A. The market for "lemons": quality uncertainty and the market mechanism. *Q. J. Econ.* **84**, 488--500 (1970).
11. Calyx Global. Are carbon credit quality indicators delivering? Calyx Global Research Report (2025).
12. Landis, J. R. & Koch, G. G. The measurement of observer agreement for categorical data. *Biometrics* **33**, 159--174 (1977).
13. Cohen, J. *Statistical Power Analysis for the Behavioral Sciences* 2nd edn (Lawrence Erlbaum Associates, 1988).
14. Fleiss, J. L. Measuring nominal scale agreement among many raters. *Psychol. Bull.* **76**, 378--382 (1971).
15. Shrout, P. E. & Fleiss, J. L. Intraclass correlations: uses in assessing rater reliability. *Psychol. Bull.* **86**, 420--428 (1979).
16. Efron, B. & Tibshirani, R. J. *An Introduction to the Bootstrap* (Chapman & Hall, 1993).
17. Coglianese, C. & Giles, C. Auditors can't save carbon offsets. *Science* **389**, 6733 (2025).
18. Huber, R., Bach, V. & Finkbeiner, M. A systematic review of quality criteria and their assessment in carbon crediting. *J. Environ. Manage.* **370**, 122693 (2024).
19. Haya, B. K. et al. Quality assessment of REDD+ carbon credit projects. Berkeley Carbon Trading Project, University of California, Berkeley (2023).
20. West, T. A. P. et al. Demystifying the romanticized narratives about carbon credits from voluntary forest conservation. *Glob. Change Biol.* **31**, e70527 (2025).
21. MSCI. State of integrity in the global carbon-credit market. MSCI ESG Research (2025).
22. Carbon Credit Quality Initiative. CCQI scoring methodology v3.0. Environmental Defense Fund, WWF & Oeko-Institut (2024).
23. Cabiyo, B. & Field, C. B. Embracing imperfection: carbon offset markets must learn to mitigate the risk of overcrediting. *PNAS Nexus* **4**, pgaf091 (2025).
24. Battocletti, V., Caldwell, L. & Macey, J. The voluntary carbon market: market failures and policy implications. *Colo. Law Rev.* **95**, 889--960 (2024).
25. Manshadi, V. H., Monachou, F. & Morgenstern, I. Offsetting carbon with lemons: adverse selection and certification in the voluntary carbon market. SSRN Working Paper (2025).
26. Nicholaus, N. et al. Evaluation of carbon credit quality criteria using an interval-valued spherical fuzzy SWARA method. *Environ. Sci. Pollut. Res.* **31**, 48923--48941 (2024).
27. Zeng, Y. et al. Limitations of carbon markets for biodiversity conservation. *Nat. Rev. Biodivers.* (2026).
28. BeZero Carbon. BeZero carbon ratings methodology. BeZero Carbon Technical Documentation (2023).
29. Wen, A. Blockchain transparency without quality signals accelerates adverse selection in carbon markets: depositor-level evidence from tokenized credit pools. Companion empirical paper, submitted to *Nat. Commun.* (2026).
30. Wen, A. ERC-CCQR: the missing composability primitive for real-world asset quality. Companion systems paper, submitted to *Proc. WWW 2027* (2026).
