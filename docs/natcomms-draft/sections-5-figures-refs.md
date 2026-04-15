# Figure Legends, Table Legends, and Reference List -- Nature Communications Draft

**Paper**: "Quantifying adverse selection in tokenized carbon credit pools"

---

## Figure Legends

### Figure 1. Adverse selection severity across six tokenized carbon credit pools.

Horizontal bar chart showing the Lemons Index (LI) for six on-chain carbon credit pools, sorted from highest (most severe adverse selection) to lowest. The Lemons Index is defined as LI = 1 - (mean composite quality score / 100), where composite scores are computed from a seven-dimension weighted framework (see Methods). Pools span a range from LI = 0.724 (Toucan BCT at historical peak, n = 43 credits, mean composite = 27.6) to LI = 0.100 (hypothetical AAA-only pool, n = 13, mean composite = 90.0). The vertical dashed line at LI = 0.5 separates severe adverse selection (right) from moderate (left). Toucan BCT (0.724), Moss MCO2 (0.713, n = 30), and Toucan NCT (0.601, n = 28) fall in the severe zone; Klima 2.0 kVCM (0.519, n = 20) sits near the boundary; Toucan CHAR (0.221, n = 12) and the hypothetical AAA-only pool fall in the low-adverse-selection zone. Bar colour follows a continuous red-to-green gradient mapping LI from 1.0 to 0.0. Quality gate annotations indicate each pool's admission mechanism: BCT and MCO2 accepted any Verra VCS credit (no gate); NCT restricted to nature-based credits (category gate); kVCM applies a curated inventory on Base; CHAR enforces a biochar-only project allowlist; the hypothetical pool restricts admission to credits scoring AAA under the framework. BCT and MCO2 compositions are from their 2022 historical peaks; NCT from 2023; kVCM and CHAR from their Base deployments as of early 2026. The 0.5-point LI gap between BCT and CHAR quantifies the value of quality filtering in preventing Akerlof-type adverse selection in pooled carbon instruments.

### Figure 2. Quality score distributions for CCP-eligible versus non-CCP credits.

Dual violin plot (or box plot with jitter overlay) comparing composite quality score distributions for credits issued under methodologies approved by the Integrity Council for the Voluntary Carbon Market's Core Carbon Principles (CCP-eligible, n = 165, blue) versus credits from non-CCP methodologies (n = 153, red). Each point represents one credit's composite score (0--100 scale). Horizontal reference lines mark grade band thresholds: AAA (>=90), AA (>=75), A (>=60), BBB (>=45), BB (>=30), B (<30). CCP-eligible credits have a mean ordinal grade of 2.69 (between BBB and A) versus 0.70 (between B and BB) for non-CCP credits, a gap of 1.99 grade levels. The distributions are nearly non-overlapping: Mann-Whitney U = 2,175, z = 13.06, two-sided p < 10^-38. Effect sizes: Cohen's d = 1.80 (95% bootstrap CI [1.50, 2.16]), Glass's delta = 1.85 (CI [1.41, 2.55]), Cliff's delta = 0.83 (CI [0.75, 0.90]), and common language effect size (CLES) = 91.4% (CI [87.5%, 94.8%]), meaning a randomly drawn CCP credit outscores a randomly drawn non-CCP credit with >91% probability. The framework recovers the ICVCM's quality threshold from its own dimension weights without training on CCP labels. This convergence corroborates Calyx Global's independent finding that CCP-eligible projects average an A rating versus C for non-CCP projects on their proprietary scale.

### Figure 3. Rank correlation between the framework and commercial carbon credit rating agencies.

(**a**) Spearman rank correlation heatmap for pairwise comparisons among four raters on six REDD+ projects: our framework (v0.4), BeZero Carbon, Calyx Global (net-zero-aligned metric), and Sylvera (net-zero-aligned metric). Cell values are Spearman rho; colour scale ranges from -1 (red) to +1 (blue). The mean inter-agency correlation among the three commercial raters is rho = +0.009 (range: -0.664 to +0.566), while the mean correlation between our framework and the three agencies is rho = +0.343 (range: -0.200 to +0.664). Project ratings are drawn from Carbon Market Watch (2023) Table 20. (**b**) Scatter plot of our framework's composite grade (v0.6) versus BeZero Carbon rating for 15 cross-type projects spanning REDD+, biochar, cookstoves, direct air capture, improved forest management, methane abatement, landfill gas, and renewable energy. Each point is labelled by project type. Spearman rho = +0.913 (95% bootstrap CI [+0.78, +0.97], permutation p < 0.001). The regression line (reduced major axis) and 95% confidence envelope are shown. Our framework's rank agreement with BeZero exceeds the mean pairwise agreement among the three commercial agencies on the full dataset (mean inter-agency rho = +0.124). Sample sizes are small (n = 6 for REDD+ only; n = 15 for combined), and confidence intervals remain wide for the REDD+-only subsample; expansion to >=30 projects is needed to narrow estimates.

### Figure 4. Counterfactual quality gating reduces adverse selection in tokenized pools.

Line plot showing the Lemons Index (Y-axis, left) as a function of minimum grade threshold applied at pool deposit time (X-axis: B, BB, BBB, A, AA, AAA) for three pools: Toucan BCT (red), Toucan NCT (orange), and Klima 2.0 kVCM (blue). A secondary Y-axis (right) or annotation track shows the number of credits admitted at each threshold. BCT's Lemons Index declines from 0.724 (no gate, 43 credits admitted) to 0.547 (>=BB, 7 admitted) to 0.405 (>=BBB, 2 admitted); no BCT credits score A or above, so the line terminates at BBB. NCT drops from 0.601 (28 credits) to 0.390 (>=BB, 10 credits) and plateaus through BBB before reaching 0.385 at >=A (8 credits). kVCM shows a smoother decline from 0.519 (20 credits) through 0.371 (>=BB, 12), 0.273 (>=BBB, 8), 0.181 (>=AA, 4), to 0.076 (>=AAA, 1 credit). The horizontal dashed line at LI = 0.221 marks CHAR's Lemons Index for comparison: a >=BBB gate on BCT (LI = 0.405) approaches but does not reach CHAR's level, while a >=BBB gate on kVCM (LI = 0.273) achieves comparable quality. The shaded region between BCT's baseline and gated trajectories represents prevented adverse selection. The highlighted "sweet spot" at the BBB threshold balances quality improvement against pool liquidity: it excludes HFC-23 destruction, pre-2013 renewables, and poorly verified REDD+ while retaining legitimate avoidance projects with adequate verification.

### Figure 5. Per-dimension inter-rater reliability across three independent raters.

Bar chart showing Fleiss' kappa for each of seven scoring dimensions, computed across a panel of three Claude-family language models (Opus 4.6, Sonnet 4.6, Haiku 4.5) independently scoring 29 credits using the v0.4.1 rubric with author scores redacted. Bars are ordered by decreasing kappa: permanence (0.684, substantial), removal type (0.585, moderate), vintage year (0.324, fair), MRV grade (0.248, fair), additionality (0.243, fair), co-benefits (0.182, slight), and registry/methodology (0.168, slight). Horizontal coloured bands indicate Landis-Koch interpretation thresholds: slight (0.00--0.20, grey), fair (0.21--0.40, yellow), moderate (0.41--0.60, light blue), substantial (0.61--0.80, blue), and almost perfect (0.81--1.00, dark blue). The two highest-reliability dimensions -- permanence and removal type -- carry the heaviest combined weight in the composite (0.175 + 0.250 = 0.425), meaning the framework's load-bearing dimensions are also its most reproducible. Co-benefits has zero weight in the composite (safeguards-gate only), so its low kappa does not propagate into grades. Registry/methodology kappa (0.168) motivated a v0.6 rubric refinement collapsing four tiers to a binary CCP-eligible/non-CCP-eligible classification. Grade-level Fleiss' kappa across all dimensions is 0.600 (substantial), and composite ICC(2,k) = 0.993 (near-perfect). All pairwise comparisons achieve 100% within-plus-or-minus-one-grade-band agreement (29/29 credits).

### Figure 6. Quality rating framework overview and on-chain integration.

(**a**) Radar chart comparing per-dimension scores (0--100) for a representative AAA credit (Climeworks Orca direct air capture, composite = 95.0) and a representative B credit (Kariba REDD+ Zimbabwe, composite = 19.6) across seven dimensions: removal type, permanence, additionality, MRV grade, vintage year, registry/methodology, and co-benefits. The AAA credit scores >=85 on all technical dimensions; the B credit scores <30 on five of seven, illustrating the multi-dimensional nature of quality differentiation. (**b**) Schematic of the composite scoring pipeline. Seven per-dimension scores (0--100) are multiplied by calibrated weights (removal type 0.250, MRV grade 0.200, additionality 0.200, permanence 0.175, vintage year 0.100, registry/methodology 0.075, co-benefits 0.000) and summed to produce a composite score. The composite maps to a six-tier letter grade (AAA >=90, AA >=75, A >=60, BBB >=45, BB >=30, B <30). A disqualifier check then applies grade caps: double counting caps at B, sanctioned registry at BB, no third-party verification at BBB, and community harm at BBB. The final grade is the minimum of the composite-derived grade and any applicable cap. (**c**) On-chain integration via the ERC-CCQR interface. A DeFi protocol (pool contract, retirement contract, or aggregator) issues a staticcall to the CarbonCreditRating contract's `meetsGrade(creditToken, tokenId, minGrade)` function, which returns a boolean. The rating contract reads from Ethereum Attestation Service attestations published by independent raters. This zero-gas-cost view call enables composable quality gating: any protocol can enforce any quality threshold without custom integration.

---

## Table Legends

### Table 1. Per-dimension inter-rater reliability and framework calibration.

Summary of scoring dimension properties, inter-rater agreement, and calibration actions. Weight: relative contribution to the composite score (sums to 1.000 excluding co-benefits). Fleiss' kappa: nominal-scale agreement among three independent LLM raters (Opus 4.6, Sonnet 4.6, Haiku 4.5) on 10-point-bucketed dimension scores across 29 credits. Interpretation follows Landis and Koch (1977): slight (0.00--0.20), fair (0.21--0.40), moderate (0.41--0.60), substantial (0.61--0.80), almost perfect (0.81--1.00). v0.6 action: rubric refinements motivated by the inter-rater reliability findings. "Tightened formula" for vintage year removes the pre-Paris override discontinuity. "Safeguards-gate (weight = 0)" means co-benefits is attested as informational metadata and used only to trigger the communityHarm disqualifier, not in composite computation. "Collapsed to 2-tier CCP/non-CCP" reduces registry/methodology from four tiers to a binary classification aligned with ICVCM Core Carbon Principles approval status.

### Table 2. Summary statistics for framework validation.

Key metrics from the empirical validation of the quality rating framework. CCP/non-CCP gap: difference in mean ordinal grade between credits under CCP-approved methodologies (n = 165) and non-CCP methodologies (n = 153). Cohen's d and CLES: effect sizes for the CCP calibration study (10,000 bootstrap resamples). Spearman rho: rank correlation between framework grades and BeZero Carbon ratings on 15 cross-type projects (10,000 bootstrap and permutation resamples). Fleiss' kappa: grade-level inter-rater reliability across three independent LLM raters on 29 credits. ICC(2,k): two-way random effects, average measures intraclass correlation on continuous composite scores. Monte Carlo robustness: proportion of credits retaining their baseline grade across 10,000 Dirichlet-sampled weight perturbations (concentration = 50). BCT and CHAR Lemons Index: adverse selection severity at pool level. 95% confidence intervals are bootstrap percentile intervals unless otherwise noted. Dashes indicate metrics for which confidence intervals are not applicable or not computed.

---

## References

1. Akerlof, G. A. The market for "lemons": quality uncertainty and the market mechanism. *Q. J. Econ.* **84**, 488--500 (1970).

2. Calel, R., Colmer, J., Dechezlepretre, A. & Glachant, M. Systematic assessment of the achieved emission reductions of carbon crediting projects. *Nat. Commun.* **15**, 5535 (2024).

3. Trencher, G. et al. Demand for low-quality offsets by major companies undermines climate integrity of the voluntary carbon market. *Nat. Commun.* **15**, 10890 (2024).

4. West, T. A. P., Borner, J., Sills, E. O. & Kontoleon, A. Overstated carbon emission reductions from voluntary REDD+ projects in the Brazilian Amazon. *Science* **381**, 873--877 (2023).

5. Coglianese, C. & Giles, C. Auditors can't save carbon offsets. *Science* **389**, 6733 (2025).

6. Manshadi, V. H., Monachou, F. & Morgenstern, I. Offsetting carbon with lemons: adverse selection and certification in the voluntary carbon market. SSRN Working Paper (2025).

7. Berg, F., Kolbel, J., Pavlova, A. & Rigobon, R. The market for voluntary carbon offsets. SSRN Working Paper (2025).

8. MSCI. State of integrity in the global carbon-credit market. MSCI ESG Research (2025).

9. Integrity Council for the Voluntary Carbon Market. Core Carbon Principles, Assessment Framework, and Assessment Procedure. ICVCM (2023).

10. Carbon Credit Quality Initiative. CCQI scoring methodology v3.0. Environmental Defense Fund, WWF & Oeko-Institut (2024).

11. Allen, M. et al. The Oxford Principles for Net Zero Aligned Carbon Offsetting. University of Oxford (2020).

12. Calyx Global. Are carbon credit quality indicators delivering? Calyx Global Research Report (2025).

13. Carbon Market Watch & Perspectives Climate Group. Assessing and comparing carbon credit rating agencies. Carbon Market Watch Policy Brief (2023).

14. Huber, R., Bach, V. & Finkbeiner, M. A systematic review of quality criteria and their assessment in carbon crediting. *J. Environ. Manage.* **370**, 122693 (2024).

15. Zhou, C., Chen, H., Wang, S., Sun, X., El Saddik, A. & Cai, W. Harnessing Web3 on carbon offset market for sustainability: framework and a case study. *IEEE Wirel. Commun.* **30**, 104--111 (2023).

16. Gao, Y. & Liu, Z. CATchain-R: a blockchain-based carbon registry platform with credibility index. *npj Clim. Action* **5**, 12 (2026).

17. Jaffer, J. et al. Global, robust and comparable digital carbon assets: PACT carbon stablecoin. In *Proc. IEEE International Conference on Blockchain and Cryptocurrency (ICBC)* 1--9 (IEEE, 2024).

18. Jirasek, M. KlimaDAO: a crypto answer to carbon markets. In *Blockchain Driven Supply Chains and Enterprise Information Systems* (eds Treiblmaier, H. & Clohessy, T.) Ch. 12 (Springer, 2023).

19. Bosshard, C. et al. Blockchain-based voluntary carbon market: strategic insights into network structure. *Front. Blockchain* **8**, 1603695 (2025).

20. Frontiers in Blockchain. Tokenized carbon credits in voluntary carbon markets: the case of KlimaDAO. *Front. Blockchain* **7**, 1360918 (2024).

21. Zeng, Y. et al. Limitations of carbon markets for biodiversity conservation. *Nat. Rev. Biodivers.* (2026). https://doi.org/10.1038/s44358-026-00150-4

22. Cabiyo, B. & Field, C. B. Embracing imperfection: carbon offset markets must learn to mitigate the risk of overcrediting. *PNAS Nexus* **4**, pgaf091 (2025).

23. Singapore National Environment Agency. Carbon rating panel: appointment of BeZero, Calyx Global, and Sylvera under the International Carbon Credit Framework. NEA Regulatory Notice (2025).

24. Landis, J. R. & Koch, G. G. The measurement of observer agreement for categorical data. *Biometrics* **33**, 159--174 (1977).

25. Fleiss, J. L. Measuring nominal scale agreement among many raters. *Psychol. Bull.* **76**, 378--382 (1971).

26. Shrout, P. E. & Fleiss, J. L. Intraclass correlations: uses in assessing rater reliability. *Psychol. Bull.* **86**, 420--428 (1979).

27. West, T. A. P. et al. Demystifying the romanticized narratives about carbon credits from voluntary forest conservation. *Glob. Change Biol.* **31**, e70527 (2025).

28. Garcia, A. & Sanford, L. On the potential for strategic behaviour in jurisdictional REDD+. *Proc. Natl Acad. Sci. USA* **123**, e2531612123 (2026).

29. Haya, B. K. et al. Quality assessment of REDD+ carbon credit projects. Berkeley Carbon Trading Project, University of California, Berkeley (2023).

30. Haya, B. K. et al. Comprehensive assessment of REDD+ carbon crediting with updated VM0048 methodology. Berkeley Carbon Trading Project Working Paper (2024).

31. Fernandez Salguero, R. A. Effectiveness of carbon pricing and compensation instruments: an umbrella review. Preprint at https://arxiv.org/abs/2512.06887 (2025).

32. Battocletti, V., Caldwell, L. & Macey, J. The voluntary carbon market: market failures and policy implications. *Colo. Law Rev.* **95**, 889--960 (2024).

33. Sylvera. State of Carbon Credits 2025: From Volume to Value. Sylvera Research Report (2025).

34. BeZero Carbon. BeZero carbon ratings methodology. BeZero Carbon Technical Documentation (2023).

35. Calyx Global. CCP correlation analysis and AAA-D rating scale. Calyx Global Methodology Update (2026).

36. Cheong, B. C. The paradox and fallacy of global carbon credits. *Anthropocene Sci.* **4**, 72--83 (2025).

37. Gold Standard & ATEC Global. First fully digital cookstove carbon credits issued on Hedera Guardian. Gold Standard Impact Report (2025).

38. Verra. First credits approved under digital MRV pilot for high-frequency issuance. Verra Registry Announcement (2026).

39. Open Forest Protocol & Kanop. Dynamic baselines via AI satellite intelligence for forest carbon monitoring. OFP Technical Report (2025).

40. CarbonPlan. OffsetsDB: a comprehensive database of carbon offset projects. CarbonPlan (2024). https://carbonplan.org/research/offsets-db

41. Columbia Center on Global Energy Policy. Ahonen, P. et al. How to fully operationalize Article 6 of the Paris Agreement. Columbia University CGEP Report (2025).

42. Buterin, V. et al. ERC-20: Token standard. Ethereum Improvement Proposals, EIP-20 (2015). https://eips.ethereum.org/EIPS/eip-20

43. Entriken, W., Shirley, D., Evans, J. & Sachs, N. ERC-721: Non-fungible token standard. Ethereum Improvement Proposals, EIP-721 (2018). https://eips.ethereum.org/EIPS/eip-721

44. Ethereum Attestation Service. EAS: making Ethereum attestations accessible and composable. EAS Documentation (2023). https://attest.sh

45. Nicholaus, N. et al. Evaluation of carbon credit quality criteria using an interval-valued spherical fuzzy SWARA method. *Environ. Sci. Pollut. Res.* **31**, 48923--48941 (2024).

46. Science-Based Targets Initiative. SBTi Corporate Net-Zero Standard v2.0. Science-Based Targets Initiative (2024).

47. World Bank. State and Trends of Carbon Pricing 2025. World Bank Group (2025).

48. Cohen, J. *Statistical Power Analysis for the Behavioral Sciences* 2nd edn (Lawrence Erlbaum Associates, 1988).

49. Efron, B. & Tibshirani, R. J. *An Introduction to the Bootstrap* (Chapman & Hall, 1993).

50. NUS Sustainable and Green Finance Institute. Carbon credit quality assessment framework: a 9-principle evaluation of crediting programs. NUS SGFIN Working Paper (2024).

51. Nguyen, T. Application of neutrosophic Delphi-DEMATEL to carbon credit quality systems in Vietnam. *J. Clean. Prod.* **438**, 140744 (2025).

52. ICVCM. CCP-approved methodologies: six CDR and three cookstove methodology approvals. Integrity Council for the Voluntary Carbon Market (2025--2026). https://icvcm.org/ccp-approved-methodologies

53. Microsoft & Carbon Direct. Criteria for high-quality carbon dioxide removal, 5th edn. Carbon Direct (2025).
