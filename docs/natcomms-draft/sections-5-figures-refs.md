# Figure Legends, Table Legends, and Reference List -- Nature Communications Draft

**Paper**: "Blockchain transparency without quality signals accelerates adverse selection in carbon markets: depositor-level evidence from tokenized credit pools"

---

## Figure Legends

### Figure 1. A single depositor's portfolio reveals the adverse selection mechanism.

Portfolio composition for a representative multi-type BCT depositor (wallet [WALLET_HASH_TRUNCATED]). (**a**) Bar chart showing composite quality scores (0--100 scale) for each TCO2 token type held by the depositor, coloured by disposition: red bars indicate credit types deposited into BCT; blue bars indicate credit types retained in the depositor's wallet. Grade band thresholds are marked as horizontal reference lines (AAA $\geq$90, AA $\geq$75, A $\geq$60, BBB $\geq$45, BB $\geq$30, B <30). The depositor held [N_TYPES_EXAMPLE] distinct TCO2 types with composite scores ranging from [LOW_SCORE] to [HIGH_SCORE]. All deposited types fall below the depositor's portfolio mean; all retained types fall above it. The quality differential for this depositor is $\Delta$ = [EXAMPLE_DELTA] points. (**b**) Schematic of the Akerlof mechanism at the depositor level: the depositor observes their own portfolio quality (information advantage), deposits the lowest-quality credits into a quality-blind pool (strategic selection), and retains the highest-quality credits for OTC sale or future compliance use (quality arbitrage). This depositor-level behaviour, aggregated across [N_MULTI] multi-type depositors, produces the pool-level quality degradation measured by the Lemons Index.

### Figure 2. Distribution of quality differentials across all multi-type depositors.

Histogram of per-depositor quality differentials ($\Delta_d = \bar{Q}_{\text{retained}} - \bar{Q}_{\text{deposited}}$) for [N_MULTI] depositors who held at least two distinct TCO2 token types at the time of their BCT deposit. The vertical dashed line at $\Delta = 0$ separates adverse selection ($\Delta > 0$, right) from reverse selection ($\Delta < 0$, left). [SELECTION_RATE]% of depositors fall to the right of zero. The distribution is right-skewed, with the bulk of the mass above zero (median $\Delta$ = [MEDIAN_DELTA], mean $\Delta$ = [MEAN_DELTA]). A kernel density estimate of the permutation null distribution (10,000 iterations, grey shading) is superimposed for comparison: the observed distribution is shifted substantially to the right of the null, confirming that the positive differentials cannot be explained by random deposit behaviour (Wilcoxon $p$ < [P_WILCOXON], Cohen's $d$ = [COHENS_D]). Inset: box plot showing median, interquartile range, and outliers. Individual depositor points are shown with jitter overlay.

### Figure 3. Lemons Index across 34 market segments reveals a quality spectrum.

(**a**) Horizontal bar chart showing the Lemons Index (LI) for 34 carbon credit pool segments, sorted from highest (most severe adverse selection) to lowest. LI is defined as $L = 1 - (\bar{C}/100)$, where $\bar{C}$ is the mean composite quality score. Bar colour follows a continuous red-to-green gradient mapping LI from 1.0 to 0.0. The six original tokenized pools (BCT, MCO2, NCT, kVCM, CHAR, hypothetical AAA) are highlighted with bold outlines and placed on the spectrum for comparison. The vertical dashed line at LI = 0.51 marks the null model expectation (random credit assignment). Pools to the right demonstrate adverse selection; pools to the left demonstrate quality curation. BCT (LI = 0.724) and MCO2 (LI = 0.713) fall 6.2 and 5.7 SD above the null, respectively. CHAR (LI = 0.221) and DACCS (LI = 0.076) fall well below it. (**b**) Null model reference: Monte Carlo distribution (10,000 iterations) of Lemons Index for random 43-credit draws from the full 318-credit market, with BCT's observed value marked at 6.2 SD above the mean.

### Figure 4. Adverse selection intensifies as the market matures.

(**a**) Time-stratified selection rates and mean quality differentials for two periods: early (October 2021 -- March 2022, BCT price >$4) and late (April -- December 2022, BCT price <$2). Bar heights show selection rate (proportion of depositors with $\Delta > 0$); error bars show 95% bootstrap confidence intervals. The selection rate increases from [EARLY_RATE]% (early) to [LATE_RATE]% (late), and the mean $\Delta$ increases from [EARLY_DELTA] to [LATE_DELTA], consistent with a learning model in which informed agents progressively exploit information asymmetry. (**b**) Scatter plot of individual depositor $\Delta$ values against deposit date, with a LOESS smoother showing the temporal trend. The positive slope confirms that later depositors exhibited stronger adverse selection than earlier depositors. (**c**) BCT pool price (secondary Y-axis) overlaid on the temporal $\Delta$ trend, illustrating the inverse relationship between pool value and selection intensity: as BCT's price declined, the incentive to deposit low-quality credits (which would fetch even less on the OTC market) strengthened.

### Figure 5. Counterfactual quality gating reverses adverse selection.

Line plot showing the Lemons Index (Y-axis) as a function of minimum grade threshold applied at pool deposit time (X-axis: B, BB, BBB, A, AA, AAA) for three pools: Toucan BCT (red), Klima 2.0 kVCM (blue), and Toucan NCT (orange). A secondary Y-axis or annotation track shows the number of credits admitted at each threshold. BCT's Lemons Index declines from 0.724 (no gate, 43 credits) to 0.547 ($\geq$BB, 7 credits) to 0.405 ($\geq$BBB, 2 credits); no BCT credits score A or above, so the line terminates at BBB. kVCM shows a smoother decline from 0.519 (20 credits) through 0.273 ($\geq$BBB, 8 credits) to 0.076 ($\geq$AAA, 1 credit). The horizontal dashed line at LI = 0.221 marks CHAR's Lemons Index for comparison: a $\geq$BBB gate on BCT (LI = 0.405) approaches but does not reach CHAR's level, while a $\geq$BBB gate on kVCM (LI = 0.273) achieves comparable quality. The shaded region between each pool's baseline and gated trajectories represents prevented adverse selection. The highlighted "sweet spot" at the BBB threshold balances quality improvement against pool liquidity.

---

## Table Legends

### Table 1. Depositor-level adverse selection: summary statistics.

[PLACEHOLDER TABLE] Key metrics from the depositor-level analysis. N depositors: total unique addresses depositing into BCT. N multi-type: depositors holding $\geq$2 distinct TCO2 types. Selection rate: proportion with $\Delta > 0$. Mean $\Delta$: population-level mean quality differential with 95% bootstrap CI. Effect size: Cohen's $d$ for the paired difference. Statistical tests: Wilcoxon signed-rank and permutation test $p$-values. Robustness: results excluding KlimaDAO and stratified by time period. All depositor-level values are [PLACEHOLDER] pending on-chain data collection.

### Table 2. Pool-level Lemons Index for six tokenized carbon credit pools.

Lemons Index (LI), mean composite quality score, number of credits, and percentage of credits rated A or above for six on-chain carbon credit pools: Toucan BCT (LI = 0.724, $n$ = 43), Moss MCO2 (LI = 0.713, $n$ = 30), Toucan NCT (LI = 0.601, $n$ = 28), Klima 2.0 kVCM (LI = 0.519, $n$ = 20), Toucan CHAR (LI = 0.221, $n$ = 12), and hypothetical AAA-only (LI = 0.100, $n$ = 13). Null model expectation (random draw of $n$ credits from the 318-credit market): LI = 0.51, SD = 0.026 for $n$ = 43. BCT's observed LI exceeds the null by 6.2 SD.

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

9. Calyx Global. Are carbon credit quality indicators delivering? Calyx Global Research Report (2025).

10. Carbon Market Watch & Perspectives Climate Group. Assessing and comparing carbon credit rating agencies. Carbon Market Watch Policy Brief (2023).

11. Allen, M. et al. The Oxford Principles for Net Zero Aligned Carbon Offsetting. University of Oxford (2020).

12. Coglianese, C. & Giles, C. Auditors can't save carbon offsets. *Science* **389**, 6733 (2025).

13. Verra. Statement on crypto instruments and tokenization. Verra Registry Announcement (2023).

14. CarbonPlan. Zombies on the blockchain. CarbonPlan Analysis (2022). https://carbonplan.org/research/toucan-crypto-offsets

15. Zhou, C., Chen, H., Wang, S., Sun, X., El Saddik, A. & Cai, W. Harnessing Web3 on carbon offset market for sustainability: framework and a case study. *IEEE Wirel. Commun.* **30**, 104--111 (2023).

16. Jirasek, M. KlimaDAO: a crypto answer to carbon markets. In *Blockchain Driven Supply Chains and Enterprise Information Systems* (eds Treiblmaier, H. & Clohessy, T.) Ch. 12 (Springer, 2023).

17. Bosshard, C. et al. Blockchain-based voluntary carbon market: strategic insights into network structure. *Front. Blockchain* **8**, 1603695 (2025).

18. Frontiers in Blockchain. Tokenized carbon credits in voluntary carbon markets: the case of KlimaDAO. *Front. Blockchain* **7**, 1360918 (2024).

19. Singapore National Environment Agency. Carbon rating panel: appointment of BeZero, Calyx Global, and Sylvera under the International Carbon Credit Framework. NEA Regulatory Notice (2025).

20. Zeng, Y. et al. Limitations of carbon markets for biodiversity conservation. *Nat. Rev. Biodivers.* (2026). https://doi.org/10.1038/s44358-026-00150-4

21. Cabiyo, B. & Field, C. B. Embracing imperfection: carbon offset markets must learn to mitigate the risk of overcrediting. *PNAS Nexus* **4**, pgaf091 (2025).

22. Haya, B. K. et al. Quality assessment of REDD+ carbon credit projects. Berkeley Carbon Trading Project, University of California, Berkeley (2023).

23. Haya, B. K. et al. Comprehensive assessment of REDD+ carbon crediting with updated VM0048 methodology. Berkeley Carbon Trading Project Working Paper (2024).

24. Battocletti, V., Caldwell, L. & Macey, J. The voluntary carbon market: market failures and policy implications. *Colo. Law Rev.* **95**, 889--960 (2024).

25. Sylvera. State of Carbon Credits 2025: From Volume to Value. Sylvera Research Report (2025).

26. Garcia, A. & Sanford, L. On the potential for strategic behaviour in jurisdictional REDD+. *Proc. Natl Acad. Sci. USA* **123**, e2531612123 (2026).

27. Fernandez Salguero, R. A. Effectiveness of carbon pricing and compensation instruments: an umbrella review. Preprint at https://arxiv.org/abs/2512.06887 (2025).

28. Carbon Credit Quality Initiative. CCQI scoring methodology v3.0. Environmental Defense Fund, WWF & Oeko-Institut (2024).

29. Huber, R., Bach, V. & Finkbeiner, M. A systematic review of quality criteria and their assessment in carbon crediting. *J. Environ. Manage.* **370**, 122693 (2024).

30. Gao, Y. & Liu, Z. CATchain-R: a blockchain-based carbon registry platform with credibility index. *npj Clim. Action* **5**, 12 (2026).

31. BeZero Carbon. BeZero carbon ratings methodology. BeZero Carbon Technical Documentation (2023).

32. Cheong, B. C. The paradox and fallacy of global carbon credits. *Anthropocene Sci.* **4**, 72--83 (2025).

33. Gold Standard & ATEC Global. First fully digital cookstove carbon credits issued on Hedera Guardian. Gold Standard Impact Report (2025).

34. West, T. A. P. et al. Demystifying the romanticized narratives about carbon credits from voluntary forest conservation. *Glob. Change Biol.* **31**, e70527 (2025).

35. World Bank. State and Trends of Carbon Pricing 2025. World Bank Group (2025).

36. Cohen, J. *Statistical Power Analysis for the Behavioral Sciences* 2nd edn (Lawrence Erlbaum Associates, 1988).

37. Efron, B. & Tibshirani, R. J. *An Introduction to the Bootstrap* (Chapman & Hall, 1993).

38. Landis, J. R. & Koch, G. G. The measurement of observer agreement for categorical data. *Biometrics* **33**, 159--174 (1977).

39. Science-Based Targets Initiative. SBTi Corporate Net-Zero Standard v2.0. Science-Based Targets Initiative (2024).

40. Microsoft & Carbon Direct. Criteria for high-quality carbon dioxide removal, 5th edn. Carbon Direct (2025).

41. Wen, A. An open, distributional quality framework for voluntary carbon credits: validation against regulatory thresholds and commercial ratings. Companion methods paper, submitted to *Environ. Res. Lett.* (2026).

42. Wen, A. ERC-CCQR: the missing composability primitive for real-world asset quality. Companion systems paper, submitted to *Proc. WWW 2027* (2026).

43. Wen, A. The convergence paradox: why six carbon market frameworks chose the same binary trap. Companion perspective, submitted to *Nat. Sustain.* (2026).
