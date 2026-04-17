# Figure Legends, Table Legends, and Reference List --- Nature Communications Draft

**Paper**: "Anatomy of a market failure: on-chain evidence reveals renewable energy credits, not REDD+, drove the collapse of tokenized carbon markets"

---

## Figure Legends

### Figure 1. BCT pool composition by methodology category, weighted by deposited tonnage.

Pie chart showing the tonnage-weighted composition of 1,187 deposit transactions to the Toucan BCT pool on the Polygon blockchain (168 unique VCS projects, approximately 22 million tonnes). Renewable energy credits (grid-connected wind, hydro, and solar, predominantly from China and India, CDM methodologies AMS-I.D and ACM0002) constitute 69.1% of total deposited tonnage. The remaining composition: fossil fuel switching (10.4%), waste management and methane capture (5.5%), REDD+ (4.2%), afforestation/reforestation (3.9%), industrial gas destruction (3.1%), improved forest management (2.0%), and smaller categories below 1%. The REDD+ share --- widely cited in academic and industry commentary as the primary driver of BCT's quality collapse --- is more than 16 times smaller than the renewable energy share. This finding contradicts the prevailing narrative that BCT failed because of low-quality avoided-deforestation credits with contested baselines. The actual driver was CDM-era renewable energy credits with near-zero additionality: grid-connected projects in countries where renewables were already economically competitive during the 2008--2013 crediting period. Data source: Polygon RPC endpoint, BCT pool contract deposit events, cross-referenced against Verra VCS registry methodology classifications.

### Figure 2. CCP calibration: quality score distributions for CCP-eligible versus non-CCP credits.

Dual violin plot comparing composite quality score distributions for credits issued under methodologies approved by the ICVCM Core Carbon Principles (CCP-eligible, $n$ = 165, blue) versus credits from non-CCP methodologies ($n$ = 153, red). Each point represents one credit's composite score on a 0--100 scale. Horizontal reference lines mark grade band thresholds: AAA ($\geq$90), AA ($\geq$75), A ($\geq$60), BBB ($\geq$45), BB ($\geq$30), B (<30). CCP-eligible credits have a mean ordinal grade of 2.69 (between BBB and A) versus 0.70 (between B and BB) for non-CCP credits, a gap of 1.99 grade levels. Effect sizes: Cohen's $d$ = 1.80 (95% CI [1.50, 2.16]), CLES = 91.4% (95% CI [87.5%, 94.8%]), Cliff's $\delta$ = 0.83 (95% CI [0.75, 0.90]). Mann--Whitney $U$ = 2,175, $z$ = 13.06, $p$ $\approx$ 0. No CCP-eligible credit scored B; no non-CCP credit scored A or AAA. The framework recovers the ICVCM quality threshold from its own dimension weights without training on CCP labels. This gap is independently validated by Calyx Global, who reported approximately two grade levels of separation between CCP-eligible and non-CCP projects on their proprietary scale.

### Figure 3. Rank correlation between the framework and commercial carbon credit rating agencies.

(**a**) Spearman rank correlation heatmap for pairwise comparisons among four raters on six REDD+ projects: our framework, BeZero Carbon, Calyx Global (net-zero-aligned metric), and Sylvera (net-zero-aligned metric). Cell values are Spearman $\rho$; colour scale ranges from -1 (red) to +1 (blue). The mean inter-agency correlation among the three commercial raters is $\rho$ = +0.009 (range: -0.664 to +0.566), while the mean correlation between our framework and the three agencies is $\rho$ = +0.343 (range: -0.200 to +0.664). The BeZero--Calyx anti-correlation ($\rho$ = -0.664) indicates systematic disagreement on how to weight additionality concerns in avoided-deforestation projects. (**b**) Scatter plot of our framework's composite grade versus BeZero Carbon rating for 15 cross-type projects spanning REDD+, biochar, cookstoves, direct air capture, improved forest management, methane abatement, landfill gas, and renewable energy. Each point is labelled by project type. Spearman $\rho$ = +0.901 (95% CI [0.783, 0.959], permutation $p$ < 0.001). The framework's agreement with BeZero exceeds the mean pairwise agreement among the three commercial agencies across both datasets. The stronger cross-type correlation ($\rho$ = +0.901) compared to REDD+-only ($\rho$ = +0.664) confirms that inter-rater disagreement is concentrated in credit categories where counterfactual baselines are inherently uncertain.

### Figure 4. Quality atlas: 34-segment PQD spectrum with null model baseline.

Horizontal bar chart showing the Pool Quality Deficit (PQD) for 34 methodology-geography-vintage segments of the voluntary carbon market, sorted from lowest PQD (highest quality) to highest PQD (lowest quality). PQD ranges from 0.076 (DACCS, Climeworks Orca type) to 0.759 (grid-connected renewables, Chinese CDM wind type). The vertical dashed line at PQD = 0.510 marks the null-model baseline (random selection from the 318-credit dataset, 10,000 Monte Carlo iterations, SD = 0.028). Segments to the right of the null model exhibit quality degradation relative to random; segments to the left exhibit quality enrichment. Key segments annotated: DACCS (0.076), bio-oil injection (0.095), biochar (0.170--0.200), improved forest management (0.318), mangrove restoration (0.335), cookstoves (0.537), REDD+ (0.690--0.720), industrial gas destruction (0.650--0.747), grid-connected renewables (0.759). BCT's tonnage-weighted PQD of 0.679 is marked as a horizontal reference line. A within-pool permutation null model ($z$ = $-$0.79, $p$ = 0.22, 100,000 iterations) confirms that BCT's low quality reflects the eligible universe rather than selective deposit behaviour. CHAR's PQD of 0.221 is marked at the high-quality end for comparison. The 10-fold range demonstrates that the VCM is not a single market with a single quality level but a collection of quality-heterogeneous segments that require differentiated assessment. Colour gradient from green (low PQD) to red (high PQD).

### Figure 5. BCT grade distribution (100% BB--B) versus CHAR grade distribution (100% AA).

Paired stacked bar charts comparing the grade distributions of the Toucan BCT pool (left, $n$ = 168 unique projects, tonnage-weighted) and the Toucan CHAR biochar pool (right, $n$ = 12 projects). BCT: 100% of credits fall within the BB and B grade bands (approximately 8% BB, 92% B by tonnage), with zero credits at BBB or above. PQD = 0.679. CHAR: 100% of credits score AA (composite scores ranging from 75 to 84, mean 77.9). PQD = 0.221. The two pools operated on the same blockchain infrastructure (Toucan bridge) and drew from overlapping registries (Verra VCS for BCT; Puro.earth and Verra for CHAR). The sole design difference is CHAR's quality restriction: a narrow project allowlist limited to high-integrity biochar projects with durable carbon storage ($>$100-year permanence). The 0.460-point PQD gap (0.679 vs. 0.221) quantifies the quality improvement achievable through pool-design restrictions. BCT's 100% BB--B distribution represents a low-type pooling equilibrium with no quality gradient remaining. CHAR's 100% AA distribution demonstrates that category restriction at the pool-design level prevents quality collapse within the restricted universe.

### Figure 6. Depositor-level evidence: temporal dynamics, base-rate selection, and robustness checks.

(**a**) BCT temporal quality by quartile. Scatter plot of composite quality score (Y-axis) versus deposit block number (X-axis) for all 1,187 BCT deposits, coloured by temporal quartile (Q1--Q4). Spearman $\rho$ = $-$0.24 ($p$ < 10$^{-16}$). Quality declines monotonically from Q1 to Q4 as the pool converges on a single low-quality credit type. (**b**) Base-rate comparison: BCT renewable share versus VCS population. BCT's renewable energy share (69.1%) versus the VCS registry base rate (37%), yielding a selection coefficient of 1.87$\times$ (binomial $p$ < 10$^{-154}$). Bar chart with BCT observed share, VCS base rate, and 95% binomial confidence interval. The BCT pool over-selected renewable credits at nearly twice the rate expected under random draws from the VCS-eligible universe. (**c**) Event study: pre-Terra, post-Terra, and post-FTX quality trajectories. Deposit-level quality plotted against block number with vertical reference lines at the Terra/LUNA collapse (May 2022) and FTX collapse (November 2022). Pre-Terra deposits show significant decline (Spearman $\rho$ = $-$0.12, $p$ = 0.007); post-Terra deposits show accelerated degradation as speculative capital exits; post-FTX deposits are sparse and uniformly low quality. (**d**) Vintage-free robustness check. Paired scatter plots showing the composite-quality temporal correlation with vintage included in the composite ($\rho$ = $-$0.24) versus vintage removed from the composite ($\rho$ = +0.24). The sign reversal demonstrates that the observed temporal decline is entirely mediated by vintage drift: later deposits carried older vintages, and older vintages score lower on the vintage dimension. This is reported as a transparency result, not as a claim of causal temporal degradation.

### Figure 7. Counterfactual quality gating: PQD reduction under progressive grade thresholds.

Line plot showing the Pool Quality Deficit (Y-axis) as a function of minimum grade threshold applied at pool deposit time (X-axis: None, BB, BBB, A, AA, AAA) for four pools: Toucan BCT (red), Toucan NCT (orange), Klima 2.0 kVCM (blue), and Moss MCO2 (grey). A secondary annotation track shows the number of credits admitted at each threshold. BCT's PQD declines from 0.679 (no gate, 168 projects) to 0.547 ($\geq$BB, 7 admitted) to 0.405 ($\geq$BBB, 2 admitted); no BCT credits score A or above, so the line terminates at BBB. For kVCM, PQD drops from 0.519 (20 credits) through 0.371 ($\geq$BB, 12) to 0.273 ($\geq$BBB, 8) to 0.181 ($\geq$AA, 4) to 0.076 ($\geq$AAA, 1 credit). The horizontal dashed line at PQD = 0.221 marks CHAR's achieved PQD for comparison. The shaded region between each pool's baseline and gated trajectory represents prevented quality degradation. The highlighted region at the BBB threshold marks the recommended minimum viable quality gate: it excludes the bulk of non-additional credits (CDM-era renewables, industrial gas destruction, poorly verified REDD+) while retaining legitimate avoidance projects with adequate verification. The counterfactual demonstrates that BCT's collapse was preventable: had the pool enforced a BBB minimum gate at deposit time, it would have admitted only 2 of 168 projects but maintained a PQD of 0.405 rather than 0.679.

---

## Table Legends

### Table 1. Per-dimension inter-rater reliability and framework calibration.

Summary of scoring dimension properties, inter-rater agreement, and calibration. Weight: relative contribution to the composite score (sums to 1.000 excluding co-benefits). Fleiss' $\kappa$: agreement among three independent LLM raters on 10-point-bucketed dimension scores across 29 credits. Interpretation follows Landis and Koch (1977): slight (0.00--0.20), fair (0.21--0.40), moderate (0.41--0.60), substantial (0.61--0.80). Highest-weight dimensions (removal type 0.250, permanence 0.175) also exhibit the highest reproducibility ($\kappa$ = 0.585 and 0.684 respectively), meaning the framework's load-bearing dimensions are its most reproducible. Co-benefits ($\kappa$ = 0.182) carries zero weight in the composite and does not propagate into grade disagreement. Registry methodology ($\kappa$ = 0.168) was collapsed from four tiers to a binary CCP-eligible/non-CCP classification in v0.6.

### Table 2. Base-rate selection analysis: BCT composition versus VCS registry population.

Comparison of BCT pool composition against VCS registry base rates for each methodology category. Primary result: BCT renewable energy share = 69.1% versus VCS base rate = 37%, selection coefficient = 1.87$\times$ (binomial $p$ < 10$^{-154}$). The BCT pool over-selected renewable credits at nearly twice the registry rate. Sensitivity analysis at alternative base-rate assumptions: at 26% (lower bound, pre-2020 VCS share), selection coefficient = 2.66$\times$; at 37% (central estimate), 1.87$\times$; at 48% (upper bound, post-2020 VCS share), 1.44$\times$. All three yield $p$ < 10$^{-15}$. REDD+ exhibits the opposite pattern: BCT REDD+ share = 4.2% versus VCS base rate = 17%, selection coefficient = 0.20$\times$ (binomial $p$ < 10$^{-40}$), indicating systematic under-selection of REDD+ credits. This contradicts the prevailing narrative that REDD+ drove BCT's quality collapse; REDD+ was in fact under-represented relative to the registry universe.

### Table 3. Temporal quartile analysis of BCT deposit quality.

1,187 BCT deposits divided into four equal-sized quartiles by block number. For each quartile: block range, number of deposits, simple mean composite, volume-weighted mean composite, percentage at B grade, and total tonnes deposited. Full-sample Spearman $\rho$ = $-$0.24 ($p$ < 10$^{-16}$). Quality declines monotonically across quartiles. The dramatic volume decline from Q1 to Q4 reflects both the approaching end of BCT's active period and the price collapse reducing deposit incentives. By Q4, quality variance has collapsed: the pool accepts effectively a single credit type.

### Table 4. Vintage-free robustness check: temporal correlation with and without vintage dimension.

Robustness analysis comparing the temporal quality correlation under two composite specifications: the full composite (all dimensions including vintage) and a vintage-free composite (vintage dimension removed, remaining weights renormalized). Full composite: Spearman $\rho$ = $-$0.24 ($p$ < 10$^{-16}$); vintage-free composite: $\rho$ = +0.24, sign reversal. The reversal demonstrates that the observed temporal decline is entirely attributable to the vintage dimension: later deposits carried systematically older vintages, which score lower. This is reported as a transparency and robustness result --- the temporal decline is real in the composite but is mechanistically a vintage-selection effect rather than evidence of causal quality degradation over calendar time. The table reports both specifications side by side to allow readers to assess the sensitivity of the temporal finding to the inclusion of vintage scoring.

### Table 5. Summary statistics for framework validation and BCT analysis.

Key metrics: CCP/non-CCP gap (1.99 grade levels, Cohen's $d$ = 1.80), BeZero correlation ($\rho$ = +0.901, $n$ = 27), inter-agency mean correlation (+0.009), Fleiss' $\kappa$ (0.600), ICC (0.993), Monte Carlo robustness (93.7%), BCT PQD (0.679), NCT PQD (0.601), CHAR PQD (0.221), BCT composition (69.1% renewable energy, 4.2% REDD+), within-pool permutation null ($z$ = $-$0.79, $p$ = 0.22), base-rate selection coefficient (1.87$\times$, binomial $p$ < 10$^{-154}$), REDD+ under-selection (0.20$\times$), full-sample temporal $\rho$ ($-$0.24), pre-Terra $\rho$ ($-$0.12, $p$ = 0.007), vintage-free $\rho$ (+0.24, sign reversal), renewable share shift (Q1 67% $\rightarrow$ Q4 99.5%), cluster-robust DiD ($p$ = 0.24, observational only), depositor Gini (0.940), vintage gradient (pre-2020 PQD 0.687, 2024+ PQD 0.273). 95% confidence intervals are bootstrap percentile intervals (10,000 or 100,000 iterations).

---

## References

1. Akerlof, G. A. The market for "lemons": quality uncertainty and the market mechanism. *Q. J. Econ.* **84**, 488--500 (1970).

2. Calel, R., Colmer, J., Dechezlepretre, A. & Glachant, M. Systematic assessment of the achieved emission reductions of carbon crediting projects. *Nat. Commun.* **15**, 5535 (2024).

3. Trencher, G. et al. Demand for low-quality offsets by major companies undermines climate integrity of the voluntary carbon market. *Nat. Commun.* **15**, 10890 (2024).

4. West, T. A. P., Borner, J., Sills, E. O. & Kontoleon, A. Overstated carbon emission reductions from voluntary REDD+ projects in the Brazilian Amazon. *Science* **381**, 873--877 (2023).

5. Manshadi, V. H., Monachou, F. & Morgenstern, I. Offsetting carbon with lemons: adverse selection and certification in the voluntary carbon market. SSRN Working Paper (2025).

6. Berg, F., Kolbel, J., Pavlova, A. & Rigobon, R. The market for voluntary carbon offsets. SSRN Working Paper (2025).

7. MSCI. State of integrity in the global carbon-credit market. MSCI ESG Research (2025).

8. Integrity Council for the Voluntary Carbon Market. Core Carbon Principles, Assessment Framework, and Assessment Procedure. ICVCM (2023).

9. Carbon Market Watch & Perspectives Climate Group. Assessing and comparing carbon credit rating agencies. Carbon Market Watch Policy Brief (2023).

10. [Companion paper] ERC-CCQR: A composable on-chain quality rating standard for carbon credit DeFi. In *Proc. The Web Conference (WWW)* (2027).

11. Allen, M. et al. The Oxford Principles for Net Zero Aligned Carbon Offsetting. University of Oxford (2020).

12. Calyx Global. Are carbon credit quality indicators delivering? Calyx Global Research Report (2025).

13. Coglianese, C. & Giles, C. Auditors can't save carbon offsets. *Science* **389**, 6733 (2025).

14. Huber, R., Bach, V. & Finkbeiner, M. A systematic review of quality criteria and their assessment in carbon crediting. *J. Environ. Manage.* **370**, 122693 (2024).

15. Singapore National Environment Agency. Carbon rating panel: appointment of BeZero, Calyx Global, and Sylvera under the International Carbon Credit Framework. NEA Regulatory Notice (2025).

16. Bosshard, C. et al. Blockchain-based voluntary carbon market: strategic insights into network structure. *Front. Blockchain* **8**, 1603695 (2025).

17. Frontiers in Blockchain. Tokenized carbon credits in voluntary carbon markets: the case of KlimaDAO. *Front. Blockchain* **7**, 1360918 (2024).

18. Jirasek, M. KlimaDAO: a crypto answer to carbon markets. In *Blockchain Driven Supply Chains and Enterprise Information Systems* (eds Treiblmaier, H. & Clohessy, T.) Ch. 12 (Springer, 2023).

19. Zhou, C., Chen, H., Wang, S., Sun, X., El Saddik, A. & Cai, W. Harnessing Web3 on carbon offset market for sustainability: framework and a case study. *IEEE Wirel. Commun.* **30**, 104--111 (2023).

20. Gao, Y. & Liu, Z. CATchain-R: a blockchain-based carbon registry platform with credibility index. *npj Clim. Action* **5**, 12 (2026).

21. Zeng, Y. et al. Limitations of carbon markets for biodiversity conservation. *Nat. Rev. Biodivers.* (2026). https://doi.org/10.1038/s44358-026-00150-4

22. Cabiyo, B. & Field, C. B. Embracing imperfection: carbon offset markets must learn to mitigate the risk of overcrediting. *PNAS Nexus* **4**, pgaf091 (2025).

23. Landis, J. R. & Koch, G. G. The measurement of observer agreement for categorical data. *Biometrics* **33**, 159--174 (1977).

24. Fleiss, J. L. Measuring nominal scale agreement among many raters. *Psychol. Bull.* **76**, 378--382 (1971).

25. Shrout, P. E. & Fleiss, J. L. Intraclass correlations: uses in assessing rater reliability. *Psychol. Bull.* **86**, 420--428 (1979).

26. West, T. A. P. et al. Demystifying the romanticized narratives about carbon credits from voluntary forest conservation. *Glob. Change Biol.* **31**, e70527 (2025).

27. Haya, B. K. et al. Quality assessment of REDD+ carbon credit projects. Berkeley Carbon Trading Project, University of California, Berkeley (2023).

28. Haya, B. K. et al. Comprehensive assessment of REDD+ carbon crediting with updated VM0048 methodology. Berkeley Carbon Trading Project Working Paper (2024).

29. Battocletti, V., Caldwell, L. & Macey, J. The voluntary carbon market: market failures and policy implications. *Colo. Law Rev.* **95**, 889--960 (2024).

30. Sylvera. State of Carbon Credits 2025: From Volume to Value. Sylvera Research Report (2025).

31. BeZero Carbon. BeZero carbon ratings methodology. BeZero Carbon Technical Documentation (2023).

32. Calyx Global. CCP correlation analysis and AAA-D rating scale. Calyx Global Methodology Update (2026).

33. Cheong, B. C. The paradox and fallacy of global carbon credits. *Anthropocene Sci.* **4**, 72--83 (2025).

34. Gold Standard & ATEC Global. First fully digital cookstove carbon credits issued on Hedera Guardian. Gold Standard Impact Report (2025).

35. Verra. First credits approved under digital MRV pilot for high-frequency issuance. Verra Registry Announcement (2026).

36. CarbonPlan. OffsetsDB: a comprehensive database of carbon offset projects. CarbonPlan (2024). https://carbonplan.org/research/offsets-db

37. Cohen, J. *Statistical Power Analysis for the Behavioral Sciences* 2nd edn (Lawrence Erlbaum Associates, 1988).

38. Efron, B. & Tibshirani, R. J. *An Introduction to the Bootstrap* (Chapman & Hall, 1993).

39. Carbon Credit Quality Initiative. CCQI scoring methodology v3.0. Environmental Defense Fund, WWF & Oeko-Institut (2024).

40. ICVCM. CCP-approved methodologies: six CDR and three cookstove methodology approvals. Integrity Council for the Voluntary Carbon Market (2025--2026). https://icvcm.org/ccp-approved-methodologies

41. Microsoft & Carbon Direct. Criteria for high-quality carbon dioxide removal, 5th edn. Carbon Direct (2025).

42. Garcia, A. & Sanford, L. On the potential for strategic behaviour in jurisdictional REDD+. *Proc. Natl Acad. Sci. USA* **123**, e2531612123 (2026).

43. World Bank. State and Trends of Carbon Pricing 2025. World Bank Group (2025).

44. Science-Based Targets Initiative. SBTi Corporate Net-Zero Standard v2.0. Science-Based Targets Initiative (2024).

45. Fernandez Salguero, R. A. Effectiveness of carbon pricing and compensation instruments: an umbrella review. Preprint at https://arxiv.org/abs/2512.06887 (2025).
