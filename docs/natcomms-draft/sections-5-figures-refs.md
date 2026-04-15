# Figures, Extended Data, and References

---

## Figure Legends

### Figure 1. CCP calibration: the framework independently recovers the ICVCM quality threshold.

Dual violin plot comparing composite quality score distributions for credits issued under methodologies approved by the ICVCM Core Carbon Principles (CCP-eligible, *n* = 165, blue) versus credits from non-CCP methodologies (*n* = 153, red). Each point represents one credit's composite score (0--100 scale). Horizontal reference lines mark grade band thresholds: AAA (>=90), AA (>=75), A (>=60), BBB (>=45), BB (>=30), B (<30). CCP-eligible credits have a mean ordinal grade of 2.69 (between BBB and A) versus 0.70 (between B and BB) for non-CCP credits, a gap of 1.99 grade levels. The distributions are nearly non-overlapping: Mann-Whitney *U* = 2,175, *z* = 13.06, two-sided *p* < 10^-38. Effect sizes: Cohen's *d* = 1.80 (95% bootstrap CI [1.50, 2.16]), Cliff's delta = 0.83 (CI [0.75, 0.90]), and common language effect size (CLES) = 91.4% (CI [87.5%, 94.8%]), meaning a randomly drawn CCP credit outscores a randomly drawn non-CCP credit with >91% probability. The framework recovers the ICVCM's quality threshold from its own dimension weights without training on CCP labels, corroborating Calyx Global's independent finding that CCP-eligible projects average approximately two grade levels above non-CCP projects on their proprietary scale.

### Figure 2. Rank correlation between the framework and commercial rating agencies.

(**a**) Spearman rank correlation heatmap for pairwise comparisons among four raters on six REDD+ projects: our framework, BeZero Carbon, Calyx Global (net-zero-aligned metric), and Sylvera (net-zero-aligned metric). The mean inter-agency correlation among the three commercial raters is *rho* = +0.009 (range: -0.664 to +0.566), while the mean correlation between our framework and the three agencies is *rho* = +0.343. BeZero and Calyx are anti-correlated at -0.664, reflecting systematic disagreement on avoided-deforestation additionality. (**b**) Scatter plot of our framework's composite grade versus BeZero Carbon rating for 27 projects spanning REDD+, biochar, cookstoves, direct air capture, improved forest management, methane abatement, landfill gas, and renewable energy. Spearman *rho* = +0.901 (95% bootstrap CI [.783, .959], permutation *p* < .0001). Points are labelled by project type. The dashed line indicates the inter-agency mean (*rho* = +0.009) for comparison. Inset: subgroup correlations for CDR projects (*rho* = +0.973) and avoidance projects (*rho* = +0.802), demonstrating stronger agreement on projects with clearer quality signals.

### Figure 3. Quality atlas: 34-segment Lemons Index spectrum with null model.

Horizontal bar chart showing the Lemons Index for 34 methodology-vintage segments spanning the voluntary carbon market, sorted from lowest (best quality) to highest (worst quality). The Lemons Index ranges from 0.076 (DACCS with geological storage, *n* = 14) to 0.759 (pre-2016 grid-connected renewable energy, *n* = 18). The vertical dashed line at LI = 0.51 marks the null-model expectation under random credit selection from the 318-credit population; the grey band shows the null model's 95% interval (0.45--0.57). Six on-chain pools are annotated on the spectrum: BCT (0.724), MCO2 (0.713), NCT (0.601), kVCM (0.519), CHAR (0.221), and the hypothetical AAA-only pool (0.100). BCT falls 6.2 standard deviations above the null model, rejecting random composition (*p* < 10^-9). Bar colour follows a continuous red-to-green gradient mapping LI from 1.0 to 0.0. CCP-eligible segments are distinguished from non-CCP segments by bar outline. Vintage gradient annotation shows pre-2020 segments (mean LI = 0.687) versus 2024+ segments (mean LI = 0.273).

### Figure 4. Depositor portfolio case study: deposited versus retained credit quality.

[PLACEHOLDER FIGURE] Paired bar chart for one illustrative depositor (address [PLACEHOLDER]). Left bars show the composite quality scores of the [PLACEHOLDER] TCO2 token types deposited into BCT (mean composite = [PLACEHOLDER], all graded [PLACEHOLDER]). Right bars show the [PLACEHOLDER] TCO2 token types retained in the depositor's wallet (mean composite = [PLACEHOLDER], graded [PLACEHOLDER]). The quality delta of [PLACEHOLDER] points is annotated. Deposited credits are dominated by [PLACEHOLDER]; retained credits include [PLACEHOLDER]. This within-depositor comparison controls for depositor-level confounders (risk appetite, market access, geographic location) and isolates the quality-sorting mechanism.

### Figure 5. Quality delta distribution across depositors.

[PLACEHOLDER FIGURE] Histogram of per-depositor quality deltas ($\Delta_i = \bar{C}_{\text{deposited}} - \bar{C}_{\text{retained}}$) for [M] multi-holding depositors in BCT. The distribution is centred at [PLACEHOLDER] (median = [PLACEHOLDER]), with [PLACEHOLDER]% of depositors showing negative deltas (deposited credits scoring lower than retained credits, consistent with adverse selection). The vertical dashed line at $\Delta$ = 0 marks the null expectation under random deposit. A normal reference curve (mean = [PLACEHOLDER], SD = [PLACEHOLDER]) is overlaid. Inset: summary statistics including Wilcoxon signed-rank test *p*-value and Cohen's *d* for paired samples. The KlimaDAO-excluded subsample (*n* = [PLACEHOLDER]) is shown as a lighter histogram overlay.

### Figure 6. Time-stratified adverse selection.

[PLACEHOLDER FIGURE] Line plot showing the mean quality delta ($\bar{\Delta}$) across depositors in six-month windows from BCT's launch (October 2021) through late 2022. The delta [PLACEHOLDER: deepens/remains constant] over time, with the earliest window showing $\bar{\Delta}$ = [PLACEHOLDER] and the latest showing $\bar{\Delta}$ = [PLACEHOLDER]. Error bars represent 95% bootstrap confidence intervals for the window mean. The x-axis is annotated with market events (BCT launch, KlimaDAO bond program, BCT price collapse). The temporal pattern is consistent with depositor learning: as market participants gained experience with BCT's quality-blind acceptance mechanism, [PLACEHOLDER: they increasingly exploited the quality-dumping opportunity].

### Figure 7. Counterfactual quality gating reduces adverse selection.

Line plot showing the Lemons Index as a function of minimum grade threshold applied at pool deposit time (x-axis: B, BB, BBB, A, AA, AAA) for three pools: Toucan BCT (red), Klima 2.0 kVCM (blue), and Toucan CHAR (green, flat line at LI = 0.221 across all thresholds up to AA). A secondary y-axis shows the number of credits admitted at each threshold. BCT declines from 0.724 (no gate, 43 credits) to 0.547 (>=BB, 7 credits) to 0.405 (>=BBB, 2 credits); no BCT credits score A or above, so the line terminates at BBB. kVCM shows a smoother decline from 0.519 (20 credits) through 0.273 (>=BBB, 8 credits) to 0.076 (>=AAA, 1 credit). CHAR's flat line demonstrates that type-level quality gating (biochar allowlist) achieves naturally what grade-level gating would enforce. The shaded region between BCT's baseline and gated trajectories represents prevented adverse selection. The BBB threshold is highlighted as the minimum viable quality gate: it balances quality improvement against pool liquidity.

---

## Extended Data

### Extended Data Figure 1. Per-dimension inter-rater reliability across three independent raters.

Bar chart showing Fleiss' kappa for each of seven scoring dimensions, computed across a panel of three Claude-family language models (Opus 4.6, Sonnet 4.6, Haiku 4.5) independently scoring 29 credits. Bars ordered by decreasing kappa: permanence (0.684, substantial), removal type (0.585, moderate), vintage year (0.324, fair), MRV grade (0.248, fair), additionality (0.243, fair), co-benefits (0.182, slight), and registry/methodology (0.168, slight). Horizontal bands indicate Landis-Koch interpretation thresholds. The two highest-reliability dimensions carry the heaviest combined weight (0.425), meaning the framework's load-bearing dimensions are also its most reproducible. Co-benefits has zero weight (safeguards-gate only), so its low kappa does not propagate into grades. Grade-level Fleiss' kappa across all dimensions is 0.600; composite ICC(2,k) = 0.993.

### Extended Data Figure 2. Weight perturbation and leave-one-out sensitivity.

(**a**) Monte Carlo weight perturbation results (10,000 Dirichlet samples, concentration $\alpha$ = 50). Per-credit grade stability shown as a strip plot for 29 pilot credits, sorted by stability. Global robustness = 93.7%. Five credits flagged as fragile (stability <90%): Plan Vivo agroforestry (51.5%), Gold Standard cookstoves (66.1%), Charm Industrial bio-oil (72.7%), Pachama reforestation (74.0%), adipic acid N2O (78.1%). All five sit within 3 points of a grade boundary. (**b**) Deterministic perturbation matrix: rows are dimensions (weight +/-5pp), columns are credits, cells are coloured by grade change. Most perturbations flip 0--2 credits; vintage_year at -5pp produces the most flips (3/29). (**c**) Leave-one-out analysis: dropping permanence produces the most grade changes (5/29), confirming it is a load-bearing dimension; dropping MRV produces zero changes. (**d**) Robustness at three concentration levels: $\alpha$ = 20 (90.1%), $\alpha$ = 50 (93.7%), $\alpha$ = 100 (95.4%).

### Extended Data Figure 3. Bootstrap distribution for Spearman rho.

Histogram of 10,000 bootstrap resamples of Spearman *rho* between our framework and BeZero Carbon on the combined *n* = 27 dataset. The observed *rho* = +0.901 is marked with a vertical line. The 95% percentile CI [.783, .959] is shaded. The permutation null distribution (10,000 permutations) is overlaid in grey, with the permutation *p*-value < .0001 annotated. Inset: bootstrap distributions for the REDD+-only subsample (*n* = 6, *rho* = +0.664, wide CI reflecting small sample) and the CDR-only subsample (*rho* = +0.973, narrow CI reflecting strong agreement on projects with clear quality signals).

### Extended Data Figure 4. Subgroup rank correlations: CDR versus avoidance, CCP versus non-CCP.

(**a**) Scatter plots of framework grade versus BeZero grade, separated by project type. CDR projects (DACCS, biochar, enhanced weathering): *rho* = +0.973. Avoidance projects (cookstoves, landfill gas, renewable energy): *rho* = +0.802. The systematic cookstove divergence (framework BBB versus agency A) is annotated as a documented design choice reflecting the Oxford Principles removal-avoidance hierarchy. (**b**) Scatter plots separated by CCP eligibility. CCP-eligible projects show tighter clustering around the diagonal; non-CCP projects show greater dispersion. (**c**) Summary table of all subgroup correlations with 95% bootstrap CIs and permutation p-values.

### Extended Data Figure 5. Quality gating simulation across four pools and 16 credit types.

Extended version of Fig. 7 showing counterfactual Lemons Index trajectories for all six pools (BCT, NCT, MCO2, kVCM, CHAR, hypothetical AAA-only) across all six grade thresholds. Each trajectory is annotated with the number of credits admitted and the fraction rated A or above. A heatmap below the line plots shows the composition of each pool at each threshold by credit type (REDD+, renewable energy, biochar, DACCS, cookstoves, etc.), revealing which credit types are progressively excluded. BCT's first exclusions are HFC-23 and pre-2013 renewables (B-rated); at >=BB, REDD+ projects begin to be excluded; at >=BBB, only two credits remain (both improved forest management with strong MRV). MCO2 shows a similar pattern but is even more concentrated in Amazon REDD+ (28 of 30 credits graded B). CHAR's flat line across all thresholds up to AA confirms that biochar-only type gating subsumes grade gating up to the AA level.

---

## References

1. Calel, R., Colmer, J., Dechezlepretre, A. & Glachant, M. Systematic assessment of the achieved emission reductions of carbon crediting projects. *Nat. Commun.* **15**, 5535 (2024).

2. Trencher, G. et al. Demand for low-quality offsets by major companies undermines climate integrity of the voluntary carbon market. *Nat. Commun.* **15**, 10890 (2024).

3. Akerlof, G. A. The market for "lemons": quality uncertainty and the market mechanism. *Q. J. Econ.* **84**, 488--500 (1970).

4. Manshadi, V. H., Monachou, F. & Morgenstern, I. Offsetting carbon with lemons: adverse selection and certification in the voluntary carbon market. SSRN Working Paper (2025).

5. West, T. A. P., Borner, J., Sills, E. O. & Kontoleon, A. Overstated carbon emission reductions from voluntary REDD+ projects in the Brazilian Amazon. *Science* **381**, 873--877 (2023).

6. Integrity Council for the Voluntary Carbon Market. The Core Carbon Principles, Assessment Framework and Assessment Procedure. ICVCM (2023).

7. Sylvera. State of Carbon Credits 2025: From Volume to Value. Sylvera Research Report (2025).

8. MSCI. State of integrity in the global carbon-credit market. MSCI ESG Research (2025).

9. Carbon Market Watch & Perspectives Climate Group. Assessing and comparing carbon credit rating agencies. Carbon Market Watch Policy Brief (2023).

10. Calyx Global. Are carbon credit quality indicators delivering? Calyx Global Research Report (2025).

11. Cohen, J. *Statistical Power Analysis for the Behavioral Sciences* 2nd edn (Lawrence Erlbaum Associates, 1988).

12. Allen, M. et al. The Oxford Principles for Net Zero Aligned Carbon Offsetting. University of Oxford (2020).

13. Berg, F., Kolbel, J., Pavlova, A. & Rigobon, R. The market for voluntary carbon offsets. SSRN Working Paper (2025).

14. Landis, J. R. & Koch, G. G. The measurement of observer agreement for categorical data. *Biometrics* **33**, 159--174 (1977).

15. Fleiss, J. L. Measuring nominal scale agreement among many raters. *Psychol. Bull.* **76**, 378--382 (1971).

16. Shrout, P. E. & Fleiss, J. L. Intraclass correlations: uses in assessing rater reliability. *Psychol. Bull.* **86**, 420--428 (1979).

17. CarbonPlan. OffsetsDB: a comprehensive database of carbon offset projects. CarbonPlan (2024). https://carbonplan.org/research/offsets-db

18. Singapore National Environment Agency. Carbon rating panel: appointment of BeZero, Calyx Global, and Sylvera under the International Carbon Credit Framework. NEA Regulatory Notice (2025).

19. Carbon Credit Quality Initiative. CCQI scoring methodology v3.0. Environmental Defense Fund, WWF & Oeko-Institut (2024).

20. Huber, R., Bach, V. & Finkbeiner, M. A systematic review of quality criteria and their assessment in carbon crediting. *J. Environ. Manage.* **370**, 122693 (2024).

21. Coglianese, C. & Giles, C. Auditors can't save carbon offsets. *Science* **389**, 6733 (2025).

22. Zhou, C., Chen, H., Wang, S., Sun, X., El Saddik, A. & Cai, W. Harnessing Web3 on carbon offset market for sustainability: framework and a case study. *IEEE Wirel. Commun.* **30**, 104--111 (2023).

23. Gao, Y. & Liu, Z. CATchain-R: a blockchain-based carbon registry platform with credibility index. *npj Clim. Action* **5**, 12 (2026).

24. Jaffer, J. et al. Global, robust and comparable digital carbon assets: PACT carbon stablecoin. In *Proc. IEEE International Conference on Blockchain and Cryptocurrency (ICBC)* 1--9 (IEEE, 2024).

25. Jirasek, M. KlimaDAO: a crypto answer to carbon markets. In *Blockchain Driven Supply Chains and Enterprise Information Systems* (eds Treiblmaier, H. & Clohessy, T.) Ch. 12 (Springer, 2023).

26. Bosshard, C. et al. Blockchain-based voluntary carbon market: strategic insights into network structure. *Front. Blockchain* **8**, 1603695 (2025).

27. Frontiers in Blockchain. Tokenized carbon credits in voluntary carbon markets: the case of KlimaDAO. *Front. Blockchain* **7**, 1360918 (2024).

28. Zeng, Y. et al. Limitations of carbon markets for biodiversity conservation. *Nat. Rev. Biodivers.* (2026). https://doi.org/10.1038/s44358-026-00150-4

29. Cabiyo, B. & Field, C. B. Embracing imperfection: carbon offset markets must learn to mitigate the risk of overcrediting. *PNAS Nexus* **4**, pgaf091 (2025).

30. West, T. A. P. et al. Demystifying the romanticized narratives about carbon credits from voluntary forest conservation. *Glob. Change Biol.* **31**, e70527 (2025).

31. Garcia, A. & Sanford, L. On the potential for strategic behaviour in jurisdictional REDD+. *Proc. Natl Acad. Sci. USA* **123**, e2531612123 (2026).

32. Haya, B. K. et al. Quality assessment of REDD+ carbon credit projects. Berkeley Carbon Trading Project, University of California, Berkeley (2023).

33. Haya, B. K. et al. Comprehensive assessment of REDD+ carbon crediting with updated VM0048 methodology. Berkeley Carbon Trading Project Working Paper (2024).

34. Fernandez Salguero, R. A. Effectiveness of carbon pricing and compensation instruments: an umbrella review. Preprint at https://arxiv.org/abs/2512.06887 (2025).

35. Battocletti, V., Caldwell, L. & Macey, J. The voluntary carbon market: market failures and policy implications. *Colo. Law Rev.* **95**, 889--960 (2024).

36. BeZero Carbon. BeZero carbon ratings methodology. BeZero Carbon Technical Documentation (2023).

37. Calyx Global. CCP correlation analysis and AAA-D rating scale. Calyx Global Methodology Update (2026).

38. Cheong, B. C. The paradox and fallacy of global carbon credits. *Anthropocene Sci.* **4**, 72--83 (2025).

39. Gold Standard & ATEC Global. First fully digital cookstove carbon credits issued on Hedera Guardian. Gold Standard Impact Report (2025).

40. Verra. First credits approved under digital MRV pilot for high-frequency issuance. Verra Registry Announcement (2026).

41. Open Forest Protocol & Kanop. Dynamic baselines via AI satellite intelligence for forest carbon monitoring. OFP Technical Report (2025).

42. Columbia Center on Global Energy Policy. Ahonen, P. et al. How to fully operationalize Article 6 of the Paris Agreement. Columbia University CGEP Report (2025).

43. Nicholaus, N. et al. Evaluation of carbon credit quality criteria using an interval-valued spherical fuzzy SWARA method. *Environ. Sci. Pollut. Res.* **31**, 48923--48941 (2024).

44. Science-Based Targets Initiative. SBTi Corporate Net-Zero Standard v2.0. Science-Based Targets Initiative (2024).

45. World Bank. State and Trends of Carbon Pricing 2025. World Bank Group (2025).

46. Efron, B. & Tibshirani, R. J. *An Introduction to the Bootstrap* (Chapman & Hall, 1993).

47. NUS Sustainable and Green Finance Institute. Carbon credit quality assessment framework: a 9-principle evaluation of crediting programs. NUS SGFIN Working Paper (2024).

48. Nguyen, T. Application of neutrosophic Delphi-DEMATEL to carbon credit quality systems in Vietnam. *J. Clean. Prod.* **438**, 140744 (2025).

49. ICVCM. CCP-approved methodologies: six CDR and three cookstove methodology approvals. Integrity Council for the Voluntary Carbon Market (2025--2026). https://icvcm.org/ccp-approved-methodologies

50. Microsoft & Carbon Direct. Criteria for high-quality carbon dioxide removal, 5th edn. Carbon Direct (2025).
