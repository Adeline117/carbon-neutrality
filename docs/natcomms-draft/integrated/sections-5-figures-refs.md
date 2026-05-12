# Figure Legends, Table Legends, and Reference List --- Nature Communications Draft

**Paper**: "Adverse selection in tokenized carbon markets: who profited from the first pool collapse"

---

## Figure Legends

### Figure 1. BCT pool composition by methodology category, weighted by deposited tonnage.

Pie chart showing the tonnage-weighted composition of {{composition.n_deposits}} deposit transactions to the Toucan BCT pool on the Polygon blockchain ({{composition.n_projects}} unique VCS projects, approximately 22 million tonnes). Renewable energy credits (grid-connected wind, hydro, and solar, predominantly from China and India, CDM methodologies AMS-I.D and ACM0002) constitute {{composition.renewable_pct_tonnes}}% of total deposited tonnage. The remaining composition: fossil fuel switching ({{composition.fossil_switch_pct}}%), waste management and methane capture ({{composition.waste_methane_pct}}%), REDD+ ({{composition.redd_pct_tonnes}}%), afforestation/reforestation (3.9%), industrial gas destruction ({{composition.industrial_gas_pct}}%), improved forest management (2%), and smaller categories below 1%. The REDD+ share --- widely cited in academic and industry commentary as the primary driver of BCT's quality collapse --- is more than 16 times smaller than the renewable energy share. This finding contradicts the prevailing narrative that BCT failed because of low-quality avoided-deforestation credits with contested baselines. The actual driver was CDM-era renewable energy credits with near-zero additionality: grid-connected projects in countries where renewables were already economically competitive during the 2008--2013 crediting period. Data source: BCT deposit records from Toucan Protocol's public transaction ledger, cross-referenced against Verra VCS registry methodology classifications. See Methods for data collection protocol.

### Figure 2. CCP calibration: quality score distributions for CCP-eligible versus non-CCP credits.

Dual violin plot comparing composite quality score distributions for credits issued under methodologies approved by the ICVCM Core Carbon Principles (CCP-eligible, $n$ = 165, blue) versus credits from non-CCP methodologies ($n$ = 153, red). Each point represents one credit's composite score on a 0--100 scale. Horizontal reference lines mark grade band thresholds: AAA ($\geq$90), AA ($\geq$75), A ($\geq$60), BBB ($\geq$45), BB ($\geq$30), B (<30). CCP-eligible credits have a mean ordinal grade of 2.69 (between BBB and A) versus 0.7 (between B and BB) for non-CCP credits, a gap of 1.99 grade levels. Effect sizes: Cohen's $d$ = 1.87 (95% CI [1.68, 2.11]), CLES = 91.4% (95% CI [87.5%, 94.8%]), Cliff's $\delta$ = 0.83 (95% CI [0.75, 0.9]). Mann--Whitney $U$ = 2175, $z$ = 13.06, $p$ $\approx$ 0. No CCP-eligible credit scored B; no non-CCP credit scored A or AAA. The framework recovers the ICVCM quality threshold from its own dimension weights without training on CCP labels. This gap is independently validated by Calyx Global, who reported approximately two grade levels of separation between CCP-eligible and non-CCP projects on their proprietary scale.

### Figure 3. Quality atlas: 34-segment PQD spectrum with null model baseline.

Horizontal bar chart showing the Pool Quality Deficit (PQD) for 34 methodology-geography-vintage segments of the voluntary carbon market, sorted from lowest PQD (highest quality) to highest PQD (lowest quality). PQD ranges from 0.076 (DACCS, Climeworks Orca type) to 0.759 (grid-connected renewables, Chinese CDM wind type). The vertical dashed line at PQD = 0.51 marks the null-model baseline (random selection from the 318-credit dataset, 10,000 Monte Carlo iterations, SD = 0.028). Segments to the right of the null model exhibit quality degradation relative to random; segments to the left exhibit quality enrichment. Key segments annotated: DACCS (0.076), bio-oil injection (0.095), biochar (0.17--0.2), improved forest management (0.318), mangrove restoration (0.335), cookstoves (0.537), REDD+ (0.69--0.72), industrial gas destruction (0.65--0.747), grid-connected renewables (0.759). BCT's tonnage-weighted PQD of {{quality.bct_pqd}} is marked as a horizontal reference line. A within-pool permutation null model ($z$ = $-$0.64, $p$ = 0.27, 100,000 iterations) confirms that BCT's low quality reflects the eligible universe rather than selective deposit behaviour. CHAR's PQD of 0.221 is marked at the high-quality end for comparison. The 10-fold range demonstrates that the VCM is not a single market with a single quality level but a collection of quality-heterogeneous segments that require differentiated assessment. Colour gradient from green (low PQD) to red (high PQD).

### Figure 4. Depositor-level evidence: temporal dynamics, base-rate selection, and robustness checks.

(**a**) BCT temporal quality by quartile. Scatter plot of composite quality score (Y-axis) versus deposit block number (X-axis) for all {{composition.n_deposits}} BCT deposits, coloured by temporal quartile (Q1--Q4). Spearman $\rho$ = {{temporal.spearman_rho_full}} ($p$ < 10$^{-16}$). Quality declines monotonically from Q1 to Q4 as the pool converges on a single low-quality credit type. (**b**) Base-rate comparison: BCT renewable share versus VCS population. BCT's renewable energy share ({{composition.renewable_pct_tonnes}}%) versus the VCS registry base rate (37%), yielding a selection coefficient of 1.87$\times$ (binomial $p$ < 10$^{-187}$). Bar chart with BCT observed share, VCS base rate, and 95% binomial confidence interval. The BCT pool over-selected renewable credits at nearly twice the rate expected under random draws from the VCS-eligible universe. (**c**) Event study and difference-in-differences. Deposit-level quality plotted against block number with vertical reference lines at the May 2022 cryptocurrency market crash and the November 2022 exchange collapse (see Methods). Pre-shock deposits show significant decline (Spearman $\rho$ = {{temporal.spearman_rho_preterra}}, $p$ = 4.0 $\times$ 10$^{-4}$); post-shock deposits show accelerated degradation as speculative capital exits; post-November deposits are sparse and uniformly low quality. A deposit-level DiD panel (1,895 events) confirms BCT's quality fell 7.3 points more than NCT after the May 2022 shock ($p$ = 0.004, cluster-robust; permutation $p$ < 0.0001). (**d**) Vintage-free robustness check. Paired scatter plots showing the composite-quality temporal correlation with vintage included in the composite ($\rho$ = -0.24) versus vintage removed from the composite ($\rho$ = +0.24). The sign reversal demonstrates that the observed temporal decline is entirely mediated by vintage drift: later deposits carried older vintages, and older vintages score lower on the vintage dimension. This is reported as a transparency result, not as a claim of causal temporal degradation.

### Figure 5. Price-quality feedback loop: bidirectional Granger causality.

(**a**) Dual-axis time series showing BCT daily price (left Y-axis, USD, blue) and cumulative Pool Quality Deficit (right Y-axis, inverted, red) over the 331-day overlap period (21 October 2021 to 11 November 2022). The two series co-move strongly (Pearson $r$ = 0.774, $p$ <10^-66). Price declines from approximately $7 to $1 over the observation window, while cumulative PQD remains stable at approximately 31, reflecting the dominance of early large deposits in the cumulative metric. The cumulative renewable share (dashed grey) fluctuates between 69% and 72% (non-monotonic due to intermittent non-renewable deposits). First-differenced OLS with HAC standard errors: $\hat{\beta}$(d(Renewable%)) = $-$1.8 (SE = 0.197, $p$ <0.001), indicating that daily increases in renewable share are associated with contemporaneous price declines. (**b**) Granger causality summary diagram showing bidirectional feedback at weekly frequency ($n$ = {{price_quality.n_weekly_obs}}). Quality composition Granger-causes price: cumulative renewable share $\rightarrow$ price ($F$ = 6.32, $p$ = {{price_quality.granger_quality_to_price_p}}, lag 2). Price Granger-causes quality composition: price $\rightarrow$ cumulative renewable share ($F$ = {{price_quality.granger_price_to_quality_f}}, $p$ <10^-5, lag 2). The asymmetry in $F$-statistics (16.08 vs. 6.32) indicates that the price $\rightarrow$ quality channel is stronger than the quality $\rightarrow$ price channel, consistent with the Gresham mechanism: price declines attract lower-quality deposits, which further depress price. Rolling 30-day quality metrics show no Granger causality in either direction, confirming that the feedback operates through accumulated pool composition rather than marginal deposit quality. Data sources: BCT daily price in US-dollar terms (828 observations; see Methods), deposit-level quality composition from the public transaction ledger.

### Figure 6. Counterfactual quality gating: PQD reduction under progressive grade thresholds.

Line plot showing the Pool Quality Deficit (Y-axis) as a function of minimum grade threshold applied at pool deposit time (X-axis: None, BB, BBB, A, AA, AAA) for four pools: Toucan BCT (red), Toucan NCT (orange), Klima 2.0 kVCM (blue), and Moss MCO2 (grey). A secondary annotation track shows the number of credits admitted at each threshold. BCT's PQD declines from {{quality.bct_pqd}} (no gate, {{composition.n_projects}} projects) to 0.547 ($\geq$BB, 7 admitted) to {{quality.bbb_gate_pqd}} ($\geq$BBB, 2 admitted); no BCT credits score A or above, so the line terminates at BBB. For kVCM, PQD drops from 0.519 (20 credits) through 0.371 ($\geq$BB, 12) to 0.273 ($\geq$BBB, 8) to 0.181 ($\geq$AA, 4) to 0.076 ($\geq$AAA, 1 credit). The horizontal dashed line at PQD = 0.221 marks CHAR's achieved PQD for comparison. The shaded region between each pool's baseline and gated trajectory represents prevented quality degradation. The highlighted region at the BBB threshold marks the recommended minimum viable quality gate: it excludes the bulk of non-additional credits (CDM-era renewables, industrial gas destruction, poorly verified REDD+) while retaining legitimate avoidance projects with adequate verification. The counterfactual demonstrates that BCT's collapse was preventable: had the pool enforced a BBB minimum gate at deposit time, it would have admitted only 2 of {{composition.n_projects}} projects but maintained a PQD of {{quality.bbb_gate_pqd}} rather than 0.679.

---

## Table Legends

### Table 1. Per-dimension inter-rater reliability and framework calibration.

Summary of scoring dimension properties, inter-rater agreement, and calibration. Weight: relative contribution to the composite score (sums to 1.000 excluding co-benefits). Fleiss' $\kappa$: agreement among three independent LLM raters on 10-point-bucketed dimension scores across 29 credits. Interpretation follows Landis and Koch (1977): slight (0.00--0.20), fair (0.21--0.40), moderate (0.41--0.60), substantial (0.61--0.80). Highest-weight dimensions (removal type 0.250, permanence 0.175) also exhibit the highest reproducibility ($\kappa$ = 0.585 and 0.684 respectively), meaning the framework's load-bearing dimensions are its most reproducible. Co-benefits ($\kappa$ = 0.182) carries zero weight in the composite and does not propagate into grade disagreement. Registry methodology ($\kappa$ = 0.168) was collapsed from four tiers to a binary CCP-eligible/non-CCP classification in v0.6.

### Table 2. Base-rate selection analysis: BCT composition versus VCS registry population.

Comparison of BCT pool composition against VCS registry base rates for each methodology category. Primary result: BCT renewable energy share = {{composition.renewable_pct_tonnes}}% versus VCS base rate = 37%, selection coefficient = {{selection.selection_coefficient}}$\times$ (binomial $p$ < 10$^{-187}$). The BCT pool over-selected renewable credits at nearly twice the registry rate. Sensitivity analysis at alternative base-rate assumptions: at 26% (lower bound, pre-2020 VCS share), selection coefficient = 2.66$\times$; at 37% (central estimate), 1.87$\times$; at 48% (upper bound, post-2020 VCS share), 1.44$\times$. All three yield $p$ < 10$^{-15}$. REDD+ exhibits the opposite pattern: BCT REDD+ share = {{composition.redd_pct_tonnes}}% versus VCS base rate = 17%, selection coefficient = 0.2$\times$ (binomial $p$ < 10$^{-40}$), indicating systematic under-selection of REDD+ credits. This contradicts the prevailing narrative that REDD+ drove BCT's quality collapse; REDD+ was in fact under-represented relative to the registry universe.

### Table 3. Summary statistics for framework validation and BCT analysis.

Key metrics: CCP/non-CCP gap (1.99 grade levels, Cohen's $d$ = {{quality.ccp_cohens_d}}), BeZero correlation ($\rho$ = +{{quality.bezero_rho}}, $n$ = 27), inter-agency mean correlation (0.009), Fleiss' $\kappa$ (0.6), ICC (0.993), Monte Carlo robustness (93.7%), BCT PQD ({{quality.bct_pqd}}), NCT PQD ({{quality.nct_pqd}}), CHAR PQD (0.221), BCT composition ({{composition.renewable_pct_tonnes}}% renewable energy, {{composition.redd_pct_tonnes}}% REDD+), within-pool permutation null ($z$ = $-$0.64, $p$ = 0.27), base-rate selection coefficient ({{selection.selection_coefficient}}$\times$, binomial $p$ < 10$^{-187}$), REDD+ under-selection (0.2$\times$), full-sample temporal $\rho$ (-0.24), pre-Terra $\rho$ ({{temporal.spearman_rho_preterra}}, permutation $p$ = 0.0001, $n$ = 792), vintage-free $\rho$ (+0.24, sign reversal), renewable share shift (Q1 67% $\rightarrow$ Q4 99.5%), cluster-robust observational comparison ($p$ = 0.24), event-study DiD ($\hat{\beta}_3$ = $-$7.33, $p$ = 0.004, 1,895 deposits), bridge tonnage pass-through (99.6%), depositor Gini (0.94), vintage gradient (pre-2020 PQD 0.687, 2024+ PQD 0.273), Granger causality quality $\rightarrow$ price ($F$ = 6.32, $p$ = {{price_quality.granger_quality_to_price_p}}), Granger causality price $\rightarrow$ quality ($F$ = {{price_quality.granger_price_to_quality_f}}, $p$ <10^-5), account-clustered permutation ($p$ <0.0001), selection coefficient 0.522 [{{selection.bootstrap_ci_lo}}, {{selection.bootstrap_ci_hi}}] (BCa 95% CI, account-level bootstrap), HHI-adjusted binomial ($n_{\text{eff}}$ = 83.5, $p$ = 2.9e-15), redemption differential (REDD+ {{redemption.redd_redeemed_pct}}% vs. Renewable {{redemption.renewable_redeemed_pct}}%), tonnage-weighted redeemed quality ({{redemption.mean_quality_redeemed_weighted}} vs. deposited {{redemption.mean_quality_deposited_weighted}}), net renewable share drift (71% $\rightarrow$ 76%). 95% confidence intervals are bootstrap percentile intervals (10,000 or 100,000 iterations).

### Table 4. Redemption analysis by credit type: deposit, redemption, and net pool composition.

Tonnage deposited, tonnage redeemed, redemption rate (%), and net remaining tonnes for each of the eight methodology categories observed in BCT. Redemption rates vary dramatically across credit types: REDD+ credits were {{redemption.redd_redeemed_pct}}% redeemed (521018 of 521889 tonnes), industrial gas destruction was {{redemption.industrial_gas_redeemed_pct}}% redeemed (672255 tonnes), ARR was {{redemption.arr_redeemed_pct}}% redeemed (771768 of 845104 tonnes), and IFM was {{redemption.ifm_redeemed_pct}}% redeemed (265368 of 285367 tonnes). In contrast, renewable energy credits were only {{redemption.renewable_redeemed_pct}}% redeemed (373597 of 10233697 tonnes), fossil fuel switching was 0% redeemed (3.9 of 1,735,878 tonnes), and waste/methane was 0% redeemed (15.1 of 812,725 tonnes). The chi-squared test for differential redemption by renewable/non-renewable status is highly significant ($\chi^2$ = 4.0e6, $p$ $\approx$ 0, df = 1). Tonnage-weighted mean quality of redeemed credits ({{redemption.mean_quality_redeemed_weighted}}) exceeds that of deposited credits ({{redemption.mean_quality_deposited_weighted}}), confirming that higher-quality credits were selectively withdrawn from the pool. The net effect is that BCT's renewable share increased from {{composition.renewable_pct_tonnes}}% (deposits only) to 78.2% (net of redemptions), amplifying the Gresham dynamic. Credit types are sorted by redemption rate. Total deposited: 15207729 tonnes; total redeemed: 2604025 tonnes; overall redemption rate: 17.1%. Columns: Credit type | Deposited (tonnes) | Redeemed (tonnes) | Redemption rate (%) | Net remaining (tonnes) | Net share (%).

---

## References

1. Akerlof, G. A. The market for "lemons": quality uncertainty and the market mechanism. *Q. J. Econ.* **84**, 488--500 (1970).

2. Probst, B., Toetzke, M., Kontoleon, A., Diaz Anadon, L. & Hoffmann, V. H. Systematic assessment of the achieved emission reductions of carbon crediting projects. *Nat. Commun.* **15**, 9698 (2024).

3. Trencher, G. et al. Demand for low-quality offsets by major companies undermines climate integrity of the voluntary carbon market. *Nat. Commun.* **15**, 10890 (2024).

4. West, T. A. P., Borner, J., Sills, E. O. & Kontoleon, A. Overstated carbon emission reductions from voluntary REDD+ projects in the Brazilian Amazon. *Science* **381**, 873--877 (2023).

5. Manshadi, V. H., Monachou, F. & Morgenstern, I. Offsetting carbon with lemons: adverse selection and certification in the voluntary carbon market. SSRN Working Paper (2025).

6. Berg, F., Kolbel, J., Pavlova, A. & Rigobon, R. The market for voluntary carbon offsets. SSRN Working Paper (2025).

7. MSCI. State of integrity in the global carbon-credit market. MSCI ESG Research (2025).

8. Integrity Council for the Voluntary Carbon Market. Core Carbon Principles, Assessment Framework, and Assessment Procedure. ICVCM (2023).

9. Carbon Market Watch & Perspectives Climate Group. Assessing and comparing carbon credit rating agencies. Carbon Market Watch Policy Brief (2023).

10. [Companion paper] ERC-CCQR: A composable quality rating standard for tokenized carbon credits. Manuscript in preparation.

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

24. Cames, M. et al. How additional is the Clean Development Mechanism? Analysis of the application of current tools and proposed alternatives. Oko-Institut Report CLlMA.B.3/SERl2013/0026r (2016).

25. Schneider, L., Lazarus, M. & Kollmuss, A. Industrial N2O projects under the CDM: adipic acid --- a case of carbon leakage? Stockholm Environment Institute Working Paper 2010-01 (2010).

26. West, T. A. P. et al. Demystifying the romanticized narratives about carbon credits from voluntary forest conservation. *Glob. Change Biol.* **31**, e70527 (2025).

27. Fleiss, J. L. Measuring nominal scale agreement among many raters. *Psychol. Bull.* **76**, 378--382 (1971).

28. Shrout, P. E. & Fleiss, J. L. Intraclass correlations: uses in assessing rater reliability. *Psychol. Bull.* **86**, 420--428 (1979).

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

46. Calel, R., Colmer, J., Dechezlepretre, A. & Glachant, M. Do carbon offsets offset carbon? *Am. Econ. J. Appl. Econ.* **17**, 1--41 (2025).

47. Gupta, A. et al. Learning lessons from over-crediting to ensure additionality in forest carbon credits. *Nat. Commun.* **17**, 71552 (2026).

48. Michaelowa, A. et al. Restoring credibility in carbon offsets through systematic ex post evaluation. *Nat. Sustain.* **8**, 1589 (2025).

49. ICVCM. Core Carbon Principles Impact Report 2025. Integrity Council for the Voluntary Carbon Market (2025). https://icvcm.org/engagement-impact/ccp-impact-report-2025
