# Figure Legends, Table Legends, and Reference List

**Paper**: "On-chain forensics reveal adverse selection in the first tokenized carbon market"

---

## Figure Legends

### Figure 1. BCT pool composition by methodology category, weighted by deposited tonnage.

Pie chart showing the tonnage-weighted composition of 1,187 deposit transactions to the Toucan BCT pool on the Polygon blockchain (168 unique VCS projects, approximately 22 million tonnes). Renewable energy credits (grid-connected wind, hydro, and solar, predominantly from China and India, CDM methodologies AMS-I.D and ACM0002) constitute 69.1% of total deposited tonnage. The remaining composition: fossil fuel switching (10.4%), waste management and methane capture (5.5%), REDD+ (4.2%), afforestation/reforestation (3.9%), industrial gas destruction (3.1%), improved forest management (2%), and smaller categories below 1%. REDD+ --- widely cited as the primary driver of BCT's quality collapse --- is more than 16 times smaller than the renewable energy share. Referenced in Section 2.1.

### Figure 2. Redemption outcome by credit type: the Gresham sequence.

(**a**) Type-level redemption rates. Non-renewable credits were preferentially extracted: industrial gas 100% redeemed, REDD+ 99.8%, IFM 93%, ARR 91.3% --- compared with just 3.6% of renewable credits. (**b**) Temporal sequence of exit. ARR credits exited earliest (median March 2022), followed by industrial gas (July), IFM (October), REDD+ (November), and renewable energy last (December) --- perfectly ordered by off-chain market demand ($\rho$ = $-$0.74, $n$ = 7 types). Tonnage-weighted mean quality of redeemed credits (38.7) exceeded that of deposited credits (31.7). Referenced in Section 2.3.

### Figure 3. Price-quality feedback loop: bidirectional Granger causality.

(**a**) Dual-axis time series showing BCT-USDC daily price (left Y-axis, blue) and cumulative Pool Quality Deficit (right Y-axis, red) over the 331-day overlap period. Pearson $r$ = 0.774, $p$ <10^-66. First-differenced OLS: $\hat{\beta}$($\Delta$Renewable%) = $-$1.8 (SE = 0.197, $p$ <0.001). (**b**) Granger causality summary: quality $\rightarrow$ price ($F$ = 6.32, $p$ = 0.004) and price $\rightarrow$ quality ($F$ = 16.08, $p$ <10^-5), with the price-to-quality channel 2.5$\times$ stronger. Referenced in Section 2.3.

### Figure 4. Quality atlas: 34-segment PQD spectrum with null-model baseline.

Horizontal bar chart showing PQD for 34 VCM segments sorted from lowest (DACCS, 0.076) to highest (grid-connected renewables, 0.759). Vertical dashed line at PQD = 0.51 marks the null-model baseline (10,000 Monte Carlo iterations). BCT's PQD of 0.679 is marked (6.2 SD above random). CHAR's PQD of 0.221 is marked for comparison. Colour gradient from green (low PQD) to red (high PQD). Referenced in Section 2.8.

### Figure 5. BCT grade distribution versus CHAR grade distribution.

Paired stacked bar charts. BCT ($n$ = 168 projects): 100% at BB and B grades, PQD = 0.679. CHAR ($n$ = 12 projects): 100% at AA, PQD = 0.221. The 0.46-point PQD gap quantifies the quality improvement achievable through pool-design restrictions. Both pools operated on the same blockchain infrastructure. Referenced in Section 2.8.

### Figure 6. Same credit, different pool, different fate: BCT versus NCT within-token comparison.

Bar chart comparing redemption rates for the 14 TCO2 tokens deposited into both BCT and NCT. In BCT (no quality gate): **100% redeemed**. In NCT (nature-based quality gate): **28.5% redeemed**. ARR credits: 100% vs. 0.0%. An ARR credit that was a rare, undervalued asset in BCT's renewable-dominated pool became an ordinary constituent of NCT's nature-based pool --- correctly priced and no longer worth selectively extracting. Referenced in Section 2.6.

### Figure 7. Temporal dynamics: quartile quality decline, event study, and vintage-free robustness.

(**a**) BCT temporal quality by quartile. Scatter plot of composite quality score versus deposit block number for all 1,187 deposits, coloured by quartile. Spearman $\rho$ = -0.24 ($p$ < 10$^{-16}$). (**b**) Base-rate comparison: BCT renewable share (69.1%) versus VCS base rate (37%), selection coefficient 1.87$\times$. (**c**) Event study: pre-Terra ($\rho$ = -0.13), post-Terra ($\rho$ = -0.36), post-FTX (sparse and uniformly low quality). (**d**) Vintage-free robustness: $\rho$ = -0.24 with vintage $\rightarrow$ $\rho$ = +0.24 without vintage, demonstrating the decline is entirely mediated by vintage drift. Referenced in Section 2.7.

---

## Extended Data Figure Legends

### Extended Data Fig. 1. CCP calibration: quality score distributions for CCP-eligible versus non-CCP credits.

Dual violin plot comparing composite quality score distributions for CCP-eligible ($n$ = 165, blue) versus non-CCP ($n$ = 153, red) credits across 17 methodology categories. Grade band thresholds overlaid. CCP-eligible mean ordinal grade = 2.69 versus non-CCP = 0.70, a gap of 1.99 grade levels. Cohen's $d$ = 1.87 (95% CI [1.68, 2.11]), CLES = 91.4%, Cliff's $\delta$ = 0.83. No CCP-eligible credit scored B; no non-CCP credit scored A or AAA. This gap was not designed: the framework was constructed from the Oxford Principles hierarchy without fitting to CCP labels. Referenced in Methods (Framework validation).

### Extended Data Fig. 2. Rank correlation between the framework and commercial rating agencies.

(**a**) Spearman rank correlation heatmap for four raters on six REDD+ projects. Mean inter-agency correlation = +0.009; mean framework-agency correlation = +0.343. BeZero--Calyx anti-correlation = $-$0.664. (**b**) Scatter plot of framework grade versus BeZero rating for 27 projects spanning 12 types. Spearman $\rho$ = +0.901 (Kendall $\tau$ = 0.821, 100% within $\pm$1 grade). Leave-one-out stability: $\rho$ range +0.889 to +0.922. Subgroups: CDR $\rho$ = +0.973 ($n$ = 9), avoidance $\rho$ = +0.802 ($n$ = 18). Referenced in Methods (Framework validation).

### Extended Data Fig. 3. Counterfactual quality gating: PQD reduction under progressive grade thresholds.

Line plot showing PQD as a function of minimum grade threshold for four pools: BCT, NCT, kVCM, and MCO2. BCT declines from 0.679 (no gate) to 0.405 ($\geq$BBB, 2 admitted). CHAR's PQD (0.221) marked for comparison. The BBB threshold is highlighted as the recommended minimum viable quality gate. Referenced in Section 2.8 and Discussion.

---

## Table Legends

### Table 1. Per-dimension inter-rater reliability and framework calibration.

Summary of scoring dimension properties, inter-rater agreement, and calibration. Weight: relative contribution to the composite score. Fleiss' $\kappa$: agreement among three independent LLM raters across 29 credits. Highest-weight dimensions (removal type 0.250, permanence 0.175) exhibit the highest reproducibility ($\kappa$ = 0.585 and 0.684), meaning the framework's load-bearing dimensions are its most reproducible. Co-benefits ($\kappa$ = 0.182) carries zero weight. Referenced in Methods.

### Table 2. Top 5 redeemers by tonnage.

Wallet address (truncated), tonnes redeemed, dominant credit type, tonnage-weighted mean quality, and depositor status. These five wallets extracted 1.55 million tonnes with estimated profit of \$4--8 million. Fifteen of the twenty largest redeemers never deposited anything. Referenced in Section 2.4.

### Table 3. Redemption outcome by quality grade.

Grade, number of tokens, deposited tonnes, redeemed tonnes, redemption rate, and stranding rate. Monotonic pattern: B 2.4% < BB 31.0% < BBB 78.0%. 9.6 million tonnes of B-grade credits remain unredeemed. Referenced in Section 2.5.

### Table 4. Base-rate selection analysis: BCT composition versus VCS registry population.

BCT renewable share = 69.1% versus VCS base rate = 37%, selection coefficient = 1.87$\times$. Sensitivity analysis at alternative base rates (26--55%). REDD+ under-selection at 0.2$\times$. Referenced in Section 2.2.

### Table 5. Temporal quartile analysis of BCT deposit quality.

1,187 deposits divided into four quartiles. Quality declines monotonically; renewable share rises from 67% (Q1) to 99.5% (Q4). Referenced in Section 2.7.

### Table 6. Redemption analysis by credit type.

Tonnage deposited, redeemed, and redemption rate for each methodology category. REDD+ 99.8% redeemed versus renewable 3.6%. Referenced in Section 2.3.

### Table 7. Summary statistics for framework validation and BCT analysis.

All key metrics in one table. Referenced throughout.

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
10. [Companion paper] ERC-CCQR: A composable on-chain quality rating standard for real-world asset quality. In *Proc. The Web Conference (WWW)* (2027).
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
21. Zeng, Y. et al. Limitations of carbon markets for biodiversity conservation. *Nat. Rev. Biodivers.* (2026).
22. Cabiyo, B. & Field, C. B. Embracing imperfection: carbon offset markets must learn to mitigate the risk of overcrediting. *PNAS Nexus* **4**, pgaf091 (2025).
23. Landis, J. R. & Koch, G. G. The measurement of observer agreement for categorical data. *Biometrics* **33**, 159--174 (1977).
24. Cames, M. et al. How additional is the Clean Development Mechanism? Oko-Institut Report (2016).
25. Schneider, L., Lazarus, M. & Kollmuss, A. Industrial N2O projects under the CDM: adipic acid --- a case of carbon leakage? SEI Working Paper 2010-01 (2010).
26. Fleiss, J. L. Measuring nominal scale agreement among many raters. *Psychol. Bull.* **76**, 378--382 (1971).
27. Shrout, P. E. & Fleiss, J. L. Intraclass correlations: uses in assessing rater reliability. *Psychol. Bull.* **86**, 420--428 (1979).
28. West, T. A. P. et al. Demystifying the romanticized narratives about carbon credits from voluntary forest conservation. *Glob. Change Biol.* **31**, e70527 (2025).
29. Haya, B. K. et al. Quality assessment of REDD+ carbon credit projects. Berkeley Carbon Trading Project (2023).
30. Battocletti, V., Caldwell, L. & Macey, J. The voluntary carbon market: market failures and policy implications. *Colo. Law Rev.* **95**, 889--960 (2024).
31. Sylvera. State of Carbon Credits 2025: From Volume to Value. Sylvera Research Report (2025).
32. BeZero Carbon. BeZero carbon ratings methodology. BeZero Carbon Technical Documentation (2023).
33. Cohen, J. *Statistical Power Analysis for the Behavioral Sciences* 2nd edn (Lawrence Erlbaum Associates, 1988).
34. Efron, B. & Tibshirani, R. J. *An Introduction to the Bootstrap* (Chapman & Hall, 1993).
35. Carbon Credit Quality Initiative. CCQI scoring methodology v3.0. Environmental Defense Fund, WWF & Oeko-Institut (2024).
36. CarbonPlan. OffsetsDB: a comprehensive database of carbon offset projects. CarbonPlan (2024).
37. World Bank. State and Trends of Carbon Pricing 2025. World Bank Group (2025).
38. Ecosystem Marketplace. State of the Voluntary Carbon Market 2025. Ecosystem Marketplace (2025).
39. Cheong, B. C. The paradox and fallacy of global carbon credits. *Anthropocene Sci.* **4**, 72--83 (2025).
40. Nicholaus, N. et al. Evaluation of carbon credit quality criteria using an interval-valued spherical fuzzy SWARA method. *Environ. Sci. Pollut. Res.* **31**, 48923--48941 (2024).
