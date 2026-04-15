# ERL Supplementary Materials Outline

Environmental Research Letters permits supplementary materials hosted alongside the published letter. This document defines the boundary between main text and supplementary content.

---

## Content Retained in Main Text

The following content stays in the Letter (target: 3,500--4,000 words for ERL):

1. **Abstract** (~250 words)
2. **Introduction** -- the three structural gaps (proprietary, no uncertainty, no open benchmark), CCP and Singapore context, three contributions
3. **Methods summary** -- scoring framework (seven dimensions, weights, composite formula), distributional scoring (variance propagation, grade posteriors), Lemons Index definition, CCP calibration protocol, rank correlation methodology, inter-rater reliability design
4. **Results**
   - Section 3.1: CCP calibration (1.99-grade gap, d = 1.80, CLES = 91.4%) -- with key summary statistics inline
   - Section 3.2: Framework agreement vs. inter-agency agreement (mean rho = +0.343 vs. +0.009; expanded n=27 rho = +0.901) -- with subgroup summaries
   - Section 3.3: Inter-rater reliability (kappa = 0.600, ICC = 0.993) -- summary only
   - Section 3.4: Quality atlas (LI range 0.076--0.759, 34 segments) -- summary with key segment highlights
   - Section 3.5: Weight robustness (93.7% global grade robustness) -- one-paragraph summary
5. **Discussion** -- what makes this not another rating agency, five limitations, future directions (companion papers mention)
6. **Data availability statement**
7. **Key figures** (main text, ~4 figures):
   - Figure 1: CCP calibration violin plot (CCP-eligible vs. non-CCP distributions)
   - Figure 2: Spearman correlation heatmap (four raters on six REDD+ projects) with inset scatter for n=27
   - Figure 3: Lemons Index across 34 segments (horizontal bar chart with null model reference)
   - Figure 4: Weight robustness summary (global stability by concentration level)

---

## Content for Supplementary Information

### S1. Detailed Per-Dimension Rubric Definitions
- Full rubric for each of the seven dimensions: score ranges (0--100), tier descriptions, data sources, and scoring guidance
- Table S1: Removal type hierarchy scoring (CDR tiers, avoidance tiers, reduction tiers with score ranges)
- Table S2: Additionality assessment rubric (six tiers from demonstrated surplus to no evidence)
- Table S3: MRV grade rubric (digital MRV to no third-party verification)
- Table S4: Permanence scoring rubric (geological storage to no permanence mechanism)
- Table S5: Vintage year decay function parameters
- Table S6: Registry and methodology scoring (CCP-eligible vs. non-CCP binary)
- Table S7: Co-benefits safeguards-gate criteria and disqualifier trigger conditions

### S2. Full 34-Segment Lemons Index Scan Table
- Table S8: Complete 34-segment scan with columns: segment name, segment type (project type / registry / vintage / CCP / quality tier), n credits, mean composite score, Lemons Index, SD, z-score vs. null model, percentage at A or above
- Includes all 14 project-type segments, 5 registry segments, 3 vintage segments, 2 CCP segments, and 10 pool-type/cross-cutting segments

### S3. Per-Credit Leave-One-Out Analysis
- Table S9: LOO rank correlation stability for all 27 credits in the expanded BeZero dataset
  - Columns: credit name, project type, framework grade, BeZero grade, LOO rho (credit removed), delta rho from full-sample rho, LOO rank
  - Key finding: no single credit changes rho by more than 0.021

### S4. Bootstrap Distribution Plots
- Figure S1: Bootstrap distribution of Spearman rho (10,000 resamples) for the n=27 dataset, with 95% CI marked, BCa-corrected CI overlay, and one-sided permutation p-value annotation
- Figure S2: Bootstrap distributions of Cohen's d for CCP calibration (10,000 resamples), with 95% CI and comparison to Calyx Global's independently reported gap
- Figure S3: Bootstrap distributions for subgroup correlations (CDR: rho = +0.973, n = 9; avoidance: rho = +0.802, n = 18)

### S5. Monte Carlo Weight Sensitivity Details
- Table S10: Per-credit grade stability across three Dirichlet concentrations (20, 50, 100)
  - Columns: credit name, base grade, stability at alpha=20, stability at alpha=50, stability at alpha=100, fragile flag
  - Five fragile credits identified with stability < 90% at alpha=50
- Figure S4: Dirichlet weight perturbation heatmap (29 credits x 3 concentration levels)
- Figure S5: Deterministic sensitivity (single-dimension +/-5pp weight shifts, grade flips per perturbation)
- Table S11: Leave-one-dimension-out analysis (dropping each dimension, grade flips, rho change)

### S6. Inter-Rater Reliability Extended Data
- Table S12: Per-dimension Fleiss' kappa with 95% bootstrap CIs
- Table S13: Full confusion matrix (author grades vs. panel median, 29 credits)
- Table S14: Per-credit agreement detail (credit name, author grade, Opus grade, Sonnet grade, Haiku grade, panel median, agreement status)
- Figure S6: Scatter plot of author composite vs. panel mean composite (ICC = 0.993)

### S7. CCP Calibration Extended Data
- Table S15: Grade distribution by CCP status (percentage in each grade tier for CCP-eligible and non-CCP)
- Figure S7: Stacked bar chart of grade distributions for CCP-eligible vs. non-CCP
- Table S16: All five effect size measures with bootstrap CIs (Cohen's d, Glass's delta, Cliff's delta, CLES, Mann-Whitney z and p)

### S8. Cross-Temporal Framework Stability
- Table S17: Spearman rho between framework versions (v0.3 to v0.6) on composite rankings
- Grade change counts across version pairs (5 in v0.3-to-v0.4, 0 in v0.4-to-v0.6)

### S9. Companion Paper Cross-References
- Brief descriptions of the companion empirical paper (Nature Communications, depositor-level adverse selection) and companion systems paper (WWW 2027, ERC-CCQR on-chain interface)
- Clarification of which results appear in which paper
