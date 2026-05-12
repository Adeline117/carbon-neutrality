# Supplementary Information

**Paper**: "Adverse selection in tokenized carbon markets: who profited from the first pool collapse"

---

## Supplementary Methods

### Pool Quality Deficit

We defined the Pool Quality Deficit (PQD) to quantify quality degradation in a carbon credit pool:

$$\text{PQD}(\text{pool}) = 1 - \frac{\bar{C}}{100}$$

where $\bar{C}$ is the tonnage-weighted mean composite score of all credits in the pool. The PQD ranges from 0 (every credit scores 100; no quality degradation) to 1 (every credit scores 0; complete quality failure). Higher values indicate worse quality. The metric is interpretable, pool-comparable, and computable from publicly available project data.

For BCT, $\bar{C}$ was computed as the tonnage-weighted mean across all {{composition.n_projects}} unique projects, using the composite scores from methodology-level archetypes with per-project vintage adjustments. For the 34-segment quality atlas, PQD was computed per segment using the methodology archetype score for each segment.

**Within-pool permutation test.** We tested whether tonnage allocation within BCT was biased toward the lowest-quality tokens using a single within-pool permutation test with 100,000 iterations (seed = 42). In each iteration, quality scores were permuted across the 345 BCT-eligible TCO2 tokens while preserving the actual tonnage distribution of deposits, and the volume-weighted mean composite was recomputed. The observed volume-weighted mean was compared against the permutation distribution to obtain a $z$-score ($z$ = $-$0.64, $p$ = 0.27) and empirical $p$-value. This test asks whether the specific tonnage-to-token assignment within BCT is non-random with respect to quality; it does not compare BCT to an external universe. We also computed the Spearman rank correlation between per-token quality and total deposited tonnes as a complementary measure of tonnage-quality association.

**Within-type temporal decomposition.** To identify which credit types drove the overall temporal quality decline, we computed separate Spearman rank correlations (block number vs. composite) for each of the eight methodology types with $n$ $\geq$ 10 scored deposits. We further computed a compositional shift metric: the Spearman correlation between block number and a binary renewable indicator (1 = renewable, 0 = other). An exit analysis tracked the median deposit block per credit type to identify the order in which types ceased active deposit.

**Vintage-adjusted partial correlation.** Within the renewable segment ($n$ = 932 with recoverable vintage metadata), we tested whether the temporal decline persisted after controlling for vintage year. We computed: (i) the Spearman correlation between block number and vintage; (ii) the Spearman correlation between block number and composite score; (iii) the Spearman correlation between vintage and composite; and (iv) the partial correlation between block and composite controlling for vintage, obtained by regressing both block and composite on vintage via ordinary least squares and correlating the residuals. A reversal of sign under partial correlation indicates that the apparent temporal quality decline is mediated by vintage drift (i.e., later deposits drew from progressively older vintages) rather than by within-vintage quality change.

### Extended scoring

Of the 345 unique TCO2 token addresses in the BCT pool, 161 were scored in the original methodology-archetype batch (corresponding to project-vintage combinations with sufficient metadata). The remaining 184 tokens were scored using the same `claude_opus_score.py` rubric rules applied to available metadata fields: methodology type (mapped to the archetype rubric for that category), vintage year (scored on the vintage decay curve), and country of origin (mapped to the registry-and-methodology sub-rubric for national registry strength). Each imputed score was flagged with `source="imputed"` in the output dataset, while the original 161 scores carry `source="original"`. This extended scoring brought coverage from 161/345 to 345/345 TCO2 tokens (100% of pool tokens scored). All analyses in this paper are reported on the full 345-token dataset; robustness checks confirm that results are qualitatively identical when restricted to the 161 original-scored tokens.

### Bridge-level decomposition

To distinguish bridge-level from pool-level selection, we enumerated all TCO2 token contracts created by Toucan's `ToucanCarbonOffsetsFactory` on Polygon (queried via Dune Analytics decoded event tables: `ToucanCarbonOffsetsFactory_evt_TokenCreated`, filtered to `evt_block_time` $\leq$ 1 January 2023). We then cross-referenced against the set of TCO2 addresses appearing in BCT deposit events (`basecarbontonne_evt_deposited`). The ratio of BCT-deposited tokens to total bridged tokens measures the pass-through rate: a rate near 100% indicates that pool composition is determined at the bridge level, while a low rate would imply pool-level selection from a diverse bridged universe.

**Tonnage verification.** The token-count pass-through (345/369 = 93.5%) was supplemented with a tonnage-weighted verification. We queried `totalSupply()` via Polygon RPC for each of the 24 non-BCT bridged TCO2 tokens and compared against the known BCT deposited tonnage (21,984,482 tonnes from 1,187 deposit events). The 24 non-BCT tokens held a combined 86,683 tonnes of current supply, yielding a tonnage pass-through of 99.6% (21.98M / 22.07M). Because `totalSupply()` returns current supply after retirements and burns, the non-BCT figure is a lower bound on originally bridged tonnage, making the 99.6% an upper bound on BCT's share. Even under this conservative interpretation, pool-level selection space was negligible by tonnage.

### Event study

We exploited two exogenous shocks to the crypto-carbon market to test whether the quality composition of BCT deposits changed in response to market stress events:

1. **Terra/LUNA collapse**: May 9, 2022 (approximate Polygon block 28,400,000), when the UST algorithmic stablecoin lost its peg, triggering a broad DeFi liquidity crisis.
2. **FTX collapse**: November 6, 2022 (approximate Polygon block 35,200,000), when the FTX exchange filed for bankruptcy.

For each event, we split scored deposits into pre-event and post-event periods and computed the Spearman rank correlation between block number and composite quality score within each period. Period-split correlations were compared to assess whether quality degradation accelerated, reversed, or was unaffected by the shock. As a robustness check, we restricted the analysis to the pre-Terra subsample only (deposits before block 28,400,000) and recomputed the temporal correlation to test whether the quality decline was already established before the first exogenous shock.

### Vintage-free robustness check

Because vintage year is mechanically correlated with deposit timing (later deposits necessarily draw from the same or later vintage pool), the vintage dimension (weight 0.10) risks introducing a tautological component into the temporal quality decline. To test this, we recomputed the composite score with vintage weight set to zero and the freed weight redistributed proportionally across the five remaining active dimensions: removal type (0.2778), additionality (0.2222), permanence (0.1944), MRV (0.2222), and registry and methodology (0.0833). The temporal correlation (Spearman $\rho$ between block number and vintage-free composite) was recomputed on the full scored deposit series. A sign reversal under the vintage-free composite (from negative to positive or to near-zero) would indicate that the vintage dimension is the primary driver of the temporal signal, undermining the interpretation that intrinsic credit quality declined over time.

### Depositor-level analysis

For all {{composition.n_deposits}} BCT deposits (scored via extended scoring), we computed depositor-level concentration metrics: Gini coefficient, Herfindahl--Hirschman Index (HHI), and the effective number of depositors (1/HHI). To test whether large depositors systematically deposited lower-quality credits, we compared the quality distributions of the top 20 depositors by tonnage (71.9% of pool volume) against the remaining 489 depositors using a two-sided Mann--Whitney $U$ test. A two-sided Mann--Whitney $U$ test detects a small but significant difference ($p$ = 8.6e-5, FDR-adjusted $p$ = 1.7e-4), indicating a difference in quality distributions between large and small depositors under the unweighted deposit-level test. We note that the volume-weighted quality gap (30.3 for the top-20 vs. 35.3 for the rest, $p$ = 0.082 under permutation) does not survive multiple-testing correction, and the gap is driven by a small number of very large deposits rather than a systematic depositor-level pattern.

### Account forensics and quality swap analysis

To identify the actors responsible for selective extraction, we reconstructed the complete deposit and redemption history for each account address from the 161 scored TCO2 token transfer caches. For each token, all ERC-20 Transfer events were classified as deposits (recipient = BCT pool address `0x2f800db0fdb5223b3c3f354886d907a671414a7f`) or redemptions (sender = BCT pool address). Each event was attributed to the counterparty account and matched to the token's quality score and credit type from the extended scoring framework.

**Redeemer profiling.** For each of the {{redemption.n_unique_redeemers}} unique redeemer accounts, we computed: total redeemed tonnage, number of redemption events, tonnage-weighted mean quality of redeemed tokens, dominant credit type (the type comprising the largest share of each account's redeemed tonnage), block span (range of blocks across redemption events), and whether the account also appeared as a depositor. Accounts were ranked by total redeemed tonnage to identify the top 20 redeemers and characterise their extraction patterns.

**Depositor-redeemer overlap and quality swap.** We identified 399 accounts appearing in both the depositor and redeemer populations ({{redemption.depositor_redeemer_overlap_pct}}% of {{redemption.n_unique_redeemers}} redeemers; 394 when restricted to the 161-token scored subset). For each overlap account, we computed the tonnage-weighted mean quality of deposited tokens and redeemed tokens separately, and defined the quality swap as the difference (redeemed quality minus deposited quality). A positive quality swap indicates that the account systematically redeemed higher-quality credits than it deposited. We computed the unweighted mean quality swap across all overlap accounts and the tonnage-weighted mean (weighting by the minimum of deposited and redeemed tonnage per account). The distribution of quality swaps was characterised by the number of positive, negative, and zero-swap accounts.

**Post-extraction destination tracing.** For each redemption event involving a top-20 redeemer account, we identified the next Transfer event for the same TCO2 token originating from that account address. The destination address was classified into five categories: (i) burn address (0x000...000 or 0x000...dead) indicating retirement; (ii) NCT pool contract (`0xD838...0107`) indicating cross-pool deposit; (iii) BCT pool contract indicating re-deposit; (iv) transfer to another address (likely OTC sale or DEX); (v) no subsequent outbound transfer found (still held). Hold duration was computed as the block difference between the BCT redemption event and the next outbound transfer. This tracing covers all 161 scored token transfer caches and captures the immediate next destination only; multi-hop tracing was not performed.

**Profit quantification.** To estimate the profit from selective redemption, we assigned off-chain credit prices by type using contemporaneous (2021--2022) market data from Ecosystem Marketplace and Carbon Pulse trade reports: industrial gas \$3--12/tonne, REDD+ \$4--15/tonne, IFM \$5--18/tonne, ARR \$6--20/tonne, renewable energy \$0.30--1.50/tonne. BCT redemption cost was estimated as the BCT pool price at the time of redemption plus the Toucan selective redemption fee (which varied over the pool's lifetime; selective redemption --- required for type-targeted extraction --- carried a premium over non-selective FIFO redemption), yielding a range of \$1--5/tonne across the pool's operating period. Profit per account was computed as $\sum_i (\text{offchain\_price}_i - \text{BCT\_cost}) \times \text{tonnes}_i$ where $i$ indexes the credit types redeemed by each account. Low, central, and high scenarios use the respective bounds of the price ranges. Gas fees and DEX slippage were not included and are expected to be negligible relative to the per-tonne price differentials.

**Framework-free prediction.** To test whether the quality scoring framework adds predictive power beyond credit type classification, we defined a type-only prediction rule: tokens in high-demand categories (REDD+, IFM, ARR, industrial gas --- identified ex post from the observed type-level redemption rates in Table 4) were predicted as "majority redeemed" (redemption rate $>$ 50%); all other tokens were predicted as "stranded." This rule was compared against a quality-grade prediction rule (BBB or above predicted as redeemed; BB or below predicted as stranded). Both rules were evaluated on the 161 scored BCT tokens. We note that the type-only rule's category selection is ex post, and the 96.9% accuracy should be interpreted as a characterisation of which variable drives redemption rather than as a prospective prediction. A within-type test compared BB-grade versus B-grade redemption rates among the 116 renewable energy tokens (72 B-grade, 44 BB-grade) using a chi-squared test at the tonnage level and a Mann--Whitney $U$ test at the token level.

### Account-clustered inference

To address the concern that the naive binomial test ($p$ = 1.35e-187) overstates significance due to within-account deposit clustering, we conducted three account-level robustness tests.

**Account-level permutation test.** For each of 10,000 iterations, we resampled accounts with their complete deposit portfolios under the null hypothesis that each deposit independently draws a renewable credit with probability $P$ = 0.37 (the VCS base rate). The account-mean renewable share was recomputed for each permutation. The observed account-mean renewable share (0.892) fell outside the entire permutation distribution (null mean = 0.37, SD = 0.02), yielding $p$ <0.0001.

**HHI-adjusted binomial test.** The effective number of independent observations was computed as $n_{\text{eff}}$ = 1/HHI, where HHI is the Herfindahl--Hirschman Index of account-level deposit concentration. With HHI = 0.012 and $n_{\text{eff}}$ = 83.5, the binomial test yielded $p$ = 2.9e-15 --- reduced by 172 orders of magnitude from the naive test but still highly significant.

**DEFF-adjusted binomial test.** As a further robustness check, we computed the design effect (DEFF) assuming an intraclass correlation coefficient (ICC) of 0.5 (a conservatively high value reflecting strong within-account homogeneity). The resulting DEFF = 4.4 yielded $n_{\text{eff}}$ = 270 and $p$ = 4.7e-44.

**Bootstrap CI on selection coefficient.** An account-level bootstrap (10,000 iterations, BCa correction) was used to construct a 95% confidence interval on the selection coefficient, defined as the account-mean renewable share minus the VCS base rate. The observed selection coefficient was 0.522 with a BCa 95% CI of [0.496, 0.547], indicating that the over-selection of renewable credits is robust to the clustering structure of deposits.

**External validation with BeZero ratings.** 7 BCT projects had public BeZero ratings (from our expanded rank-correlation dataset). We mapped BeZero letter grades to a numeric scale (AAA = 95, AA = 80, A = 65, BBB = 50, BB = 35, B = 20, C = 15, D = 5) and computed the Spearman correlation between our framework composites and BeZero numerics on the overlap subset. We also assessed whether the temporal degradation pattern held under external ratings by dividing BeZero-matched deposits into terciles by block number.

### CCP empirical calibration

We tested whether the framework's composite scores separated CCP-eligible from non-CCP credits using a dataset of 318 credits classified by ICVCM CCP eligibility status (165 CCP-eligible, 153 non-CCP) across 17 methodology categories. CCP classification was based on the ICVCM's published list of CCP-approved methodologies and CCP-eligible programmes as of 2025.

Five effect size measures were computed: Cohen's $d$ (pooled standard deviation), Glass's $\delta$ (using non-CCP standard deviation as denominator), Cliff's $\delta$ (nonparametric), the common language effect size (CLES), and a Mann--Whitney $U$ test with normal-approximation $z$-score including tie correction. For each parametric and nonparametric effect size, 95% confidence intervals were obtained via the percentile bootstrap method with 10,000 resamples (seed = 42). Grade distributions were encoded on an ordinal scale (B = 0, BB = 1, BBB = 2, A = 3, AA = 4, AAA = 5).

### Rank correlation with commercial rating agencies

We assessed external validity by computing rank correlations between our framework's grades and publicly available ratings from three commercial carbon credit rating agencies: BeZero Carbon, Calyx Global, and Sylvera.

**REDD+ subset.** Six REDD+ projects were drawn from Carbon Market Watch (2023, Table 20), which reported simultaneous public ratings from all three agencies as of 2 June 2023. Each agency's ordinal scale was mapped to a monotonic integer sequence (higher = better quality), and each project was scored under our framework. Spearman rank correlations ($\rho$) and Kendall's $\tau$-b were computed for all six pairwise combinations of four raters (our framework, BeZero, Calyx, Sylvera).

**Cross-type extension.** An additional 24 projects spanning 12 non-REDD+ methodology types (direct air capture, biochar, enhanced weathering, cookstoves, improved forest management, methane abatement, landfill gas, ODS destruction, renewable energy, jurisdictional REDD+, and ARR) were compiled from BeZero case studies, Calyx research publications, Sylvera press releases, and developer press releases. All 30 projects were scored under the v0.6 rubric. Of these, 27 had BeZero ratings, 9 had Calyx ratings, 7 had Sylvera ratings, and 1 had an MSCI rating. 8 projects had ratings from 2+ agencies.

**Statistical inference.** For the combined BeZero-paired dataset ($n$ = 27), Spearman $\rho$ = +{{quality.bezero_rho}}, Kendall $\tau$-b = 0.821, with 100% of projects within $\pm$1 mapped grade and 52% exact matches. Sub-type correlations were computed for CDR credits ($\rho$ = 0.973) and avoidance credits ($\rho$ = 0.802) separately, though sub-type sample sizes are small and should be interpreted as directional evidence.

### Inter-rater reliability study

To assess reproducibility, we conducted an inter-rater reliability study using three independent large language model raters: Claude Opus 4.6, Claude Sonnet 4.6, and Claude Haiku 4.5 (Anthropic, 2025). Each model scored 29 credits (25 real-world archetypes plus 4 synthetic stress-test credits) using the v0.4.1 rubric in isolated sessions with author grades redacted. No inter-rater communication was permitted.

Agreement metrics: (i) Fleiss' $\kappa$ across the three raters at the grade level (six categories: B through AAA); (ii) per-dimension Fleiss' $\kappa$, with continuous scores binned into 10 buckets of 10 points each; (iii) ICC(2,$k$) on the continuous composite using a two-way random effects model; (iv) exact grade agreement and within-one-band agreement between the author's grades and the panel median.

Per-dimension kappa values: permanence 0.684 (substantial), removal type 0.585 (moderate), vintage year 0.324 (fair), MRV 0.248 (fair), additionality 0.243 (fair), co-benefits 0.182 (slight), registry methodology 0.168 (slight). Per-dimension standard deviations from this study were used to calibrate the distributional scoring model.

### Sensitivity analysis

**Monte Carlo weight perturbation.** We sampled 10,000 weight vectors from a Dirichlet distribution centred on the current weights with concentration parameter 50, with co-benefits weight forced to zero. For each sampled vector, all 29 credits were rescored and assigned a grade. Global robustness was defined as the mean proportion of iterations under which each credit's grade remains unchanged (93.7% at concentration 50; 90.1% at concentration 20; 95.4% at concentration 100).

**Removal-type sensitivity.** To test whether the framework's discriminatory power depends on the removal-type dimension --- which carries the largest single weight (0.25) and which some critics may view as normatively contestable --- we set the removal-type weight to zero and redistributed its weight proportionally across the remaining dimensions. Quality differences between credit categories persisted at 98% significance under this perturbation, indicating that the framework's quality discrimination is distributed across multiple dimensions rather than concentrated in removal type.

**Cross-temporal stability.** The same 29 credits were scored under three methodology versions (v0.3, v0.4, v0.6). Grade agreement between v0.4 and v0.6 was 100% (29/29). Spearman $\rho$ between v0.3 and v0.6 composite rankings was 0.992.

### Counterfactual quality-gate simulation

For BCT and five additional pools, we simulated the application of quality gates at all six grade thresholds (B, BB, BBB, A, AA, AAA). At each threshold, only credits whose final grade met or exceeded the threshold were admitted. We recomputed: the number of admitted credits, the new tonnage-weighted mean composite, the resulting PQD, and the fraction of admitted credits at grade A or above.

### 34-segment quality atlas

We defined 34 quality segments by the intersection of project type (17 methodology categories from the ICVCM taxonomy), geographic region (where sufficient data existed), and vintage band (pre-2015, 2015--2019, 2020--2023, 2024+). Each segment was scored using the median archetype score from the 318-credit methodology dataset. PQD was computed per segment. The vintage gradient was computed as the tonnage-weighted mean PQD across all segments within each vintage band.

---

## Supplementary Figures

### Supplementary Figure 1. Rank correlation between the framework and commercial carbon credit rating agencies.

(**a**) Spearman rank correlation heatmap for pairwise comparisons among four raters on six REDD+ projects: our framework, BeZero Carbon, Calyx Global (net-zero-aligned metric), and Sylvera (net-zero-aligned metric). Cell values are Spearman $\rho$; colour scale ranges from -1 (red) to +1 (blue). The mean inter-agency correlation among the three commercial raters is $\rho$ = 0.009 (range: -0.664 to +0.566), while the mean correlation between our framework and the three agencies is $\rho$ = 0.343 (range: -0.200 to +0.664). The BeZero--Calyx anti-correlation ($\rho$ = -0.664) indicates systematic disagreement on how to weight additionality concerns in avoided-deforestation projects. (**b**) Scatter plot of our framework's composite grade versus BeZero Carbon rating for 27 paired projects spanning 12 methodology types (REDD+, biochar, enhanced weathering, cookstoves, direct air capture, improved forest management, methane abatement, landfill gas, ODS destruction, renewable energy, jurisdictional REDD+, and ARR). Each point is labelled by project type. Spearman $\rho$ = +{{quality.bezero_rho}} (Kendall $\tau$-b = 0.821, 100% within $\pm$1 grade). The framework's agreement with BeZero exceeds the mean pairwise agreement among the three commercial agencies across both datasets. The stronger cross-type correlation ($\rho$ = +{{quality.bezero_rho}}) compared to REDD+-only ($\rho$ = 0.664) confirms that inter-rater disagreement is concentrated in credit categories where counterfactual baselines are inherently uncertain.

### Supplementary Figure 2. BCT grade distribution (100% BB--B) versus CHAR grade distribution (100% AA).

Paired stacked bar charts comparing the grade distributions of the Toucan BCT pool (left, $n$ = {{composition.n_projects}} unique projects, tonnage-weighted) and the Toucan CHAR biochar pool (right, $n$ = 12 projects). BCT: 100% of credits fall within the BB and B grade bands (approximately 8% BB, 92% B by tonnage), with zero credits at BBB or above. PQD = 0.679. CHAR: 100% of credits score AA (composite scores ranging from 75 to 84, mean 77.9). PQD = 0.221. The two pools operated on the same blockchain infrastructure (Toucan bridge) and drew from overlapping registries (Verra VCS for BCT; Puro.earth and Verra for CHAR). The sole design difference is CHAR's quality restriction: a narrow project allowlist limited to high-integrity biochar projects with durable carbon storage ($>$100-year permanence). The 0.46-point PQD gap ({{quality.bct_pqd}} vs. {{quality.char_pqd}}) quantifies the quality improvement achievable through pool-design restrictions. BCT's 100% BB--B distribution represents a low-type pooling equilibrium with no quality gradient remaining. CHAR's 100% AA distribution demonstrates that category restriction at the pool-design level prevents quality collapse within the restricted universe.

---

## Supplementary Tables

### Supplementary Table 1. Temporal quartile analysis of BCT deposit quality.

{{composition.n_deposits}} BCT deposits divided into four equal-sized quartiles by block number. For each quartile: block range, number of deposits, simple mean composite, volume-weighted mean composite, percentage at B grade, and total tonnes deposited. Full-sample Spearman $\rho$ = -0.24 ($p$ < 10$^{-16}$). Quality declines monotonically across quartiles. The dramatic volume decline from Q1 to Q4 reflects both the approaching end of BCT's active period and the price collapse reducing deposit incentives. By Q4, quality variance has collapsed: the pool accepts effectively a single credit type.

### Satellite verification of BCT credit quality

**India CDM grid emission factor analysis.** To independently verify the quality classification of CDM-era renewable energy credits in BCT, we compared CDM-claimed grid emission factors against observed emission factors from the Ember Global Electricity Review for 28 Indian renewable energy projects present in the BCT pool. For each project, we identified the CDM Combined Margin (CM) emission factor from the Central Electricity Authority (CEA) CO$_2$ Baseline Database (versions 5--19, covering 2008--2023) and the corresponding Ember observed emission factor for the same vintage years. The overclaim ratio was computed as claimed tCO$_2$ / Ember-consistent tCO$_2$ for each project. Across 28 projects, the mean overclaim was 26.5% (range 23.6--28.8%), with aggregate claimed emissions of 3,391,304 tCO$_2$ versus 2,701,756 tCO$_2$ consistent with observed grid data. This overclaim is driven by the CDM's use of a combined margin methodology that assumes a higher-emitting counterfactual grid than was actually operating during the crediting period.

**Sentinel-5P TROPOMI methane verification.** For 9 waste management and methane capture projects in the BCT pool, we analysed Sentinel-5P TROPOMI Level 3 methane column data (COPERNICUS/S5P/OFFL/L3\_CH4, CH4\_column\_volume\_mixing\_ratio\_dry\_air band) over the period 2019--2023. For each project, we defined a site radius of 10 km around the project coordinates and a background annulus of 50--100 km. The methane plume signal was computed as the difference between site-level and background methane concentrations, converted to tCO$_2$-equivalent using GWP100 = 28. Of 9 projects analysed, 5 (56%) showed methane concentrations inconsistent with claimed reductions (site-level concentrations not significantly below background), 1 was inconclusive, and 3 were not applicable (project type incompatible with satellite methane detection). No project showed satellite-confirmed methane reduction at the magnitude claimed in its VCS documentation.

### NFTX cross-domain validation

To test whether the dual-margin adverse selection pattern generalises beyond carbon and fungible-token markets, we analysed NFTX V1 vaults on Ethereum mainnet --- uniform-price pools where non-fungible tokens (NFTs) are deposited and redeemed at a single floor price per vault, analogous to BCT's uniform pricing of heterogeneous carbon credits. Data were collected from Dune Analytics decoded event tables (`nftx_v2_ethereum.nftxvaultupgradeable_v1_evt_minted` and `_redeemed`) as of 22 April 2026.

We selected the 20 largest vaults by mint count ($\geq$50 mints), covering 20,238 mints and 20,781 redemptions across vaults spanning collectibles (MILADY, PHUNK), gaming items (WIZARD, WARRIOR), and art (MOONCAT, AVASTR). For each vault, we computed the redeem/mint ratio and net outflow. 12 of 20 vaults (60%) exhibited net redemption outflow, consistent with selective extraction of higher-value items. The three largest vaults by activity (MILADY, REMIO, PHUNK) all showed net exit, with MANA exhibiting the strongest cherry-picking effect (redeem/mint ratio = 1.43).

The dual-margin population structure replicates BCT's pattern: in MILADY, only 1.3% of redeemers also appear as minters, compared to BCT's 1.4% depositor--redeemer overlap. Redeemer populations are 2--31$\times$ larger than minter populations across the top vaults, confirming that --- as in BCT --- distinct populations exploit the entry and exit margins of the same uniform-pricing mechanism.

### Supplementary Table 2. Vintage-free robustness check: temporal correlation with and without vintage dimension.

Robustness analysis comparing the temporal quality correlation under two composite specifications: the full composite (all dimensions including vintage) and a vintage-free composite (vintage dimension removed, remaining weights renormalized). Full composite: Spearman $\rho$ = -0.24 ($p$ < 10$^{-16}$); vintage-free composite: $\rho$ = +0.24, sign reversal. The reversal demonstrates that the observed temporal decline is entirely attributable to the vintage dimension: later deposits carried systematically older vintages, which score lower. This is reported as a transparency and robustness result --- the temporal decline is real in the composite but is mechanistically a vintage-selection effect rather than evidence of causal quality degradation over calendar time. The table reports both specifications side by side to allow readers to assess the sensitivity of the temporal finding to the inclusion of vintage scoring.
