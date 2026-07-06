# Supplementary Information

**Paper**: "Transparency without pricing: a credit-level forensic account of collapse in the first tokenized carbon pool"

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

For all {{composition.n_deposits}} BCT deposits (scored via extended scoring), we computed depositor-level concentration metrics: Gini coefficient, Herfindahl--Hirschman Index (HHI), and the effective number of depositors (1/HHI). To test whether large depositors systematically deposited lower-quality credits, we compared the quality distributions of the top 20 depositors by tonnage (71.9% of pool volume) against the remaining 459 scored depositors (479-wallet scored population) using a two-sided Mann--Whitney $U$ test. A two-sided Mann--Whitney $U$ test detects a small but significant difference ($p$ = 8.6e-5, FDR-adjusted $p$ = 1.7e-4), indicating a difference in quality distributions between large and small depositors under the unweighted deposit-level test. We note that the volume-weighted quality gap (30.3 for the top-20 vs. 35.3 for the rest, $p$ = 0.082 under permutation) does not survive multiple-testing correction, and the gap is driven by a small number of very large deposits rather than a systematic depositor-level pattern.

### Account forensics and quality swap analysis

To identify the actors responsible for selective extraction, we reconstructed the complete deposit and redemption history for each account address from the 161 scored TCO2 token transfer caches. For each token, all ERC-20 Transfer events were classified as deposits (recipient = BCT pool address `0x2f800db0fdb5223b3c3f354886d907a671414a7f`) or redemptions (sender = BCT pool address). Each event was attributed to the counterparty account and matched to the token's quality score and credit type from the extended scoring framework.

**Redeemer profiling.** For each of the {{redemption.n_unique_redeemers}} unique redeemer accounts, we computed: total redeemed tonnage, number of redemption events, tonnage-weighted mean quality of redeemed tokens, dominant credit type (the type comprising the largest share of each account's redeemed tonnage), block span (range of blocks across redemption events), and whether the account also appeared as a depositor. Accounts were ranked by total redeemed tonnage to identify the top 20 redeemers and characterise their extraction patterns.

**Depositor-redeemer overlap and quality swap.** We identified 399 accounts appearing in both the depositor and redeemer populations ({{redemption.depositor_redeemer_overlap_pct}}% of {{redemption.n_unique_redeemers}} redeemers; 394 when restricted to the 161-token scored subset). For each overlap account, we computed the tonnage-weighted mean quality of deposited tokens and redeemed tokens separately, and defined the quality swap as the difference (redeemed quality minus deposited quality). A positive quality swap indicates that the account systematically redeemed higher-quality credits than it deposited. We computed the unweighted mean quality swap across all overlap accounts and the tonnage-weighted mean (weighting by the minimum of deposited and redeemed tonnage per account). The distribution of quality swaps was characterised by the number of positive, negative, and zero-swap accounts.

**Post-extraction destination tracing.** For each redemption event involving a top-20 redeemer account, we identified the next Transfer event for the same TCO2 token originating from that account address. The destination address was classified into five categories: (i) burn address (0x000...000 or 0x000...dead) indicating retirement; (ii) NCT pool contract (`0xD838...0107`) indicating cross-pool deposit; (iii) BCT pool contract indicating re-deposit; (iv) transfer to another address (likely OTC sale or DEX); (v) no subsequent outbound transfer found (still held). Hold duration was computed as the block difference between the BCT redemption event and the next outbound transfer. This tracing covers all 161 scored token transfer caches and captures the immediate next destination only; multi-hop tracing was not performed. The classification is exhaustive by construction (every traced redemption receives one of the five categories) and is computed by `data/depositor-analysis/post_extraction_tracing.py` (results in `post_extraction_tracing_results.json`), which reproduces the reported shares exactly.

**Profit quantification.** To estimate the profit from selective redemption, we assigned off-chain credit prices by type using contemporaneous (2021--2022) market data from Ecosystem Marketplace and Carbon Pulse trade reports: industrial gas \$3--12/tonne, REDD+ \$4--15/tonne, IFM \$5--18/tonne, ARR \$6--20/tonne, renewable energy \$0.30--1.50/tonne. BCT redemption cost was estimated as the BCT pool price at the time of redemption plus the Toucan selective redemption fee (which varied over the pool's lifetime; selective redemption (required for type-targeted extraction) carried a premium over non-selective FIFO redemption), yielding a range of \$1--5/tonne across the pool's operating period. Profit per account was computed as $\sum_i (\text{offchain\_price}_i - \text{BCT\_cost}) \times \text{tonnes}_i$ where $i$ indexes the credit types redeemed by each account. Low, central, and high scenarios use the respective bounds of the price ranges, with negative per-type margins floored at zero (an arbitrageur would not redeem at a loss). Computed by `data/statistical-analysis/profit_quantification.py` (aggregate: $0.3M low / $10.3M mid / $22.0M high across the top-5 accounts); this scripted computation supersedes earlier hand-recorded totals. Gas fees and DEX slippage were not included and are expected to be negligible relative to the per-tonne price differentials.

**Framework-free prediction.** To test whether the quality scoring framework adds predictive power beyond credit type classification, we defined a type-only prediction rule: tokens in high-demand categories (REDD+, IFM, ARR, industrial gas, identified ex post from the observed type-level redemption rates in Table 4) were predicted as "majority redeemed" (redemption rate $>$ 50%); all other tokens were predicted as "stranded." This rule was compared against a quality-grade prediction rule (BBB or above predicted as redeemed; BB or below predicted as stranded). Both rules were evaluated on the 161 scored BCT tokens. We note that the type-only rule's category selection is ex post, and the 96.9% accuracy should be interpreted as a characterisation of which variable drives redemption rather than as a prospective prediction. A within-type test compared BB-grade versus B-grade redemption rates among the 116 renewable energy tokens (72 B-grade, 44 BB-grade) using a chi-squared test at the tonnage level and a Mann--Whitney $U$ test at the token level.

### Entity-level independence check (first-funder analysis)

The dual-margin claim rests on the separation between deposit-side and redemption-side accounts. Because a single entity can operate multiple addresses, we tested for entity-level links between the top 20 deposit accounts (by tonnage, from the deposit ledger) and the top 20 redemption accounts (by tonnage, aggregated from pool-to-wallet Transfer events across all 161 scored token caches). Two accounts appeared in both top-20 lists, leaving 38 unique accounts, of which 5 are smart contracts (including the single largest extractor, a retirement aggregator) and 33 are externally owned accounts (EOAs).

**First-funder resolution.** For each of the 33 EOAs we retrieved the earliest incoming native-MATIC transaction (Etherscan API, chainid 137, ascending order; falling back to the internal-transaction list for wallets funded through contracts) and recorded the funding address; 32 of 33 resolved (9 via internal transactions; one wallet has no native incoming transaction in either list). A funding address that funds three or more analysed wallets is tagged a likely exchange or disperser address, since shared exchange funding is evidence neither of common control nor of independence; one funder met this threshold (it funds three redemption-side wallets, a same-side pattern that contributes no cross-side evidence) and was discounted accordingly.

**Findings.** (i) One cross-side common funder: address `0xaeb6...cc7a` (1,458 lifetime transactions, not exchange-like) funded both the third-largest depositor (1.33 Mt) and one top-20 redeemer (20,889 t) within a 77-hour window in October 2021. (ii) Seven direct TCO2 transfers link two top-20 depositors and one top-20 redeemer (roughly 0.29 Mt moved between the sides, in both directions); direct transfers indicate interaction (same entity or bilateral trading), not necessarily common control. (iii) Two accounts are active on both margins (depositing 344 kt and 317 kt; redeeming 46 kt and 30 kt). Together the linked accounts hold 26% of top-20 deposit tonnage and 9% of top-20 redemption tonnage. Three wallets' first funders were manually re-verified against independent explorer queries.

Per-wallet results are listed in Supplementary Table 5.

**Interpretation.** The two margins are largely, but not fully, separated at the entity level. We therefore state the dual-margin separation as an account-level observation in the main text and do not claim that quality loading and extraction were performed by disjoint entities. The mechanism itself is unaffected: it is the pool's uniform pricing, not the identity of the participants, that connects entry-side quality loading to exit-side extraction. Reproduction: `data/depositor-analysis/entity_funding_analysis.py`, results in `entity_funding_analysis.json`.

### Account-clustered inference

To address the concern that the naive binomial test ($p$ = 1.35e-187) overstates significance due to within-account deposit clustering, we conducted three account-level robustness tests.

**Account-level permutation test.** For each of 10,000 iterations, we resampled accounts with their complete deposit portfolios under the null hypothesis that each deposit independently draws a renewable credit with probability $P$ = 0.37 (the VCS base rate). The account-mean renewable share was recomputed for each permutation. The observed account-mean renewable share (0.892) fell outside the entire permutation distribution (null mean = 0.37, SD = 0.02), yielding $p$ <0.0001.

**HHI-adjusted binomial test.** The effective number of independent observations was computed as $n_{\text{eff}}$ = 1/HHI, where HHI is the Herfindahl--Hirschman Index of account-level deposit concentration. With HHI = 0.012 and $n_{\text{eff}}$ = 83.5, the binomial test yielded $p$ = 2.9e-15, reduced by 172 orders of magnitude from the naive test but still highly significant.

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

**Removal-type sensitivity.** To test whether the framework's discriminatory power depends on the removal-type dimension (which carries the largest single weight of 0.25 and which some critics may view as normatively contestable), we set the removal-type weight to zero and redistributed its weight proportionally across the remaining dimensions. Quality differences between credit categories persisted at 98% significance under this perturbation, indicating that the framework's quality discrimination is distributed across multiple dimensions rather than concentrated in removal type.

**Cross-temporal stability.** The same 29 credits were scored under three methodology versions (v0.3, v0.4, v0.6). Grade agreement between v0.4 and v0.6 was 100% (29/29). Spearman $\rho$ between v0.3 and v0.6 composite rankings was 0.992.

### Within-token matched-pair design and sensitivity analysis

The {{within_token.n_shared_tokens}} TCO2 tokens deposited into both BCT and NCT were identified by intersecting the deposit ledgers of the two pools. For each shared token, deposited and redeemed tonnage in each pool were reconstructed from the raw ERC-20 Transfer logs cached per token (`transfer_cache/<token>.json`): a deposit is a Transfer to the pool contract, a redemption a Transfer from it. Summed over the 14 tokens this reproduces the published aggregate rates — BCT 100.0%, NCT 28.5%, with type-level NCT rates IFM 30.9% / ARR 0.0% / REDD+ 69.0% — to within 0.01 percentage points and 0.2 tonnes, confirming that the NCT per-token rates are measured rather than imputed.

Three exact tests were applied to the per-token difference $d_i$ = (BCT rate − NCT rate): a paired sign test, a permutation test enumerating all $2^{13}$ per-token sign assignments, and a Wilcoxon signed-rank test. One token (`0x463de2a5`) whose BCT rate departs from 100% only by ≈1 tonne of dust in 1.5 million is an effective tie ($|d_i| \le 10^{-4}$); because the direction is unanimous across all other pairs, the tests return $p$ = {{within_token.sign_test_p}} whether this token is dropped (13 pairs) or retained (14 pairs). The cross-token mean gap and its uncertainty were estimated by a percentile bootstrap over the {{within_token.n_shared_tokens}} per-token differences (20,000 resamples): +{{within_token.boot_gap_mean_pp}} percentage points, 95% CI [{{within_token.boot_gap_ci_lo_pp}}, {{within_token.boot_gap_ci_hi_pp}}]. A tonne-level Beta–Binomial model with uniform Beta(1,1) priors (deposited tonnes as trials, redeemed tonnes as successes) yields a much narrower interval, but it treats each tonne as an independent Bernoulli trial when redemptions are executed in large batched transactions; it therefore overstates precision and is reported only as a descriptive summary, not used for inference.

**Rosenbaum sensitivity.** Because each credit is matched to itself across pools, quality, vintage, registry, and project type cannot confound the comparison. For a hidden confounder that nonetheless biased the per-pair treatment-odds, the matched-pair sign-test result remains significant at $\alpha$ = 0.05 up to $\Gamma$ = {{within_token.sensitivity_gamma}}: an unobserved factor would have to make a credit more than threefold more likely to be redeemed from one pool than the other, for reasons unrelated to pool design, before the inference is overturned. The remaining threat is selection into the shared set (which credits reached both pools); the directed acyclic graph in Supplementary Fig. 3 makes the assumed causal structure explicit. A mixed-effects logit with a token random intercept agrees in direction but suffers quasi-complete separation (BCT redemption ≈ 100%) and is not used for inference.

### Quasi-experimental evidence for the sorting channel (NCT launch)

A second design tests a specific causal mechanism: did the appearance of a screened pool divert high-quality credits away from the unscreened one? The screened pool (NCT) launched on 2022-02-04, three months before the May-2022 market crash and therefore separable from it. We treat its launch as an event in a difference-in-differences with NCT-eligible (nature-based) credits as the treated group — they gain an alternative venue — and NCT-ineligible renewables as the control, whose BCT-deposit behaviour cannot be affected by NCT's existence. Parallel pre-trends hold (the nature-versus-renewable trend interaction is non-significant before launch, $p$ = 0.59). After launch, the nature-based share of BCT deposits collapses from {{nct_launch.nature_share_pre}}% to {{nct_launch.nature_share_post}}%, and a regression-discontinuity-in-time shows a {{nct_launch.rdit_pts}}-point break in BCT deposit quality at the launch date beyond trend ($p$ = {{nct_launch.rdit_p}}). The difference-in-differences in quality ({{nct_launch.did_pts}} points, nature-based falling further than renewables) is, however, not significant under cluster-robust or wild-bootstrap inference ($p \geq$ {{nct_launch.did_p_clustered}}): because NCT-eligibility is a credit-type characteristic, the comparison reduces to effectively two groups, which (with a small post-launch nature-based sample, $n$ = 19) precludes a significant clustered estimate. We therefore read the sorting channel as suggestive evidence, not an identified effect. Its design strengths — a genuine control group of NCT-ineligible renewables and confirmed parallel pre-trends — make it more credible than a naive before/after, and it is consistent with the broader mechanism: screening degrades the unscreened pool because good credits leave when a better venue appears.

### Additional robustness

**Compositional shift.** Renewable share rises from 67% (Q1) to 99.5% (Q4). Token diversity collapses from 24 distinct scores to 2. Higher-quality types (IFM, Waste/Methane, ARR) ceased depositing earlier (median blocks 20.4M--21.7M) than renewables (32.6M).

**Depositor concentration.** Deposits were highly concentrated: {{selection.n_wallets}} accounts participated, with the top 10 accounting for 50% of tonnage (Gini = {{selection.gini}}). Large and small depositors deposited similar-quality credits (rank-biserial $r$ = $-$0.17; the volume-weighted gap of 5 quality points does not survive permutation, $p$ = 0.082).

### Counterfactual quality-gate simulation

For BCT and five additional pools, we simulated the application of quality gates at all six grade thresholds (B, BB, BBB, A, AA, AAA). At each threshold, only credits whose final grade met or exceeded the threshold were admitted. We recomputed: the number of admitted credits, the new tonnage-weighted mean composite, the resulting PQD, and the fraction of admitted credits at grade A or above.

### Quality-gate counterfactual on the real deposit stream

Grade floors were applied to the actual tonnage-weighted BCT deposit stream (1,187/1,187 deposits scored; `quality_gate_real.py`, results in `quality_gate_real_results.json`). Baseline deposit-weighted Lemons Index: 0.689 (this deposit-level aggregation differs from the project-level composition PQD of 0.679 only in weighting basis). A BB floor yields 0.630 while admitting 34.3% of tonnage; a BBB floor yields 0.506 while admitting 7.2%; floors of A and above admit no tonnage at all. The BBB result quantifies both the benefit and the cost of gating: the deficit falls by 27% in relative terms, but the pool retains only a fourteenth of its volume, because the eligible universe was itself low quality. This analysis supersedes an earlier simulation (`counterfactual_simulation.py`) that evaluated floors on stylized pool compositions rather than the real deposit stream; numbers previously quoted from it (0.724 to 0.405) should not be used.

### 34-segment quality atlas

We defined 34 quality segments by the intersection of project type (17 methodology categories from the ICVCM taxonomy), geographic region (where sufficient data existed), and vintage band (pre-2015, 2015--2019, 2020--2023, 2024+). Each segment was scored using the median archetype score from the 318-credit methodology dataset. PQD was computed per segment. The vintage gradient was computed as the tonnage-weighted mean PQD across all segments within each vintage band.

### Account-forensics destination tracing (relocated from Results)

Tracing the immediate destination of each redeemed credit across the 20 largest extractors (2.57 million tonnes) reveals three pathways. **Cross-pool transfer (39.2%):** re-deposited into the quality-screened NCT pool, a counterpart sharing identical protocol infrastructure, capturing the price differential between the unscreened pool's uniform price and the screened pool's nature-based premium. **Immediate retirement (34.6%):** permanently retired (formally cancelled, never reusable as emission offsets) within seconds of extraction, indicating pre-arranged retirement pipelines; the largest extractor (0x65a5..., 651,334 tonnes of industrial gas) retired 100% of its credits in the same transaction as the redemption, and an on-chain code check confirms this address is a smart contract, consistent with a retirement aggregator rather than an individual extractor. **Secondary market (17.0%):** transferred to other addresses, with 6.9% re-deposited into BCT and 2.3% still held; the five categories are exhaustive and sum to 100%. The cross-pool movement was systematic, not opportunistic: of 31 credits deposited into both pools, 14 were redeemed from the unscreened pool, and all 14 follow the same temporal sequence — unscreened-pool deposit → unscreened-pool redemption → screened-pool deposit (median 103 days, then 14 days). Not a single credit violated this ordering.

### Granger causality (price–quality, weekly; relocated from Results)

At weekly frequency (n = 55), Granger tests are asymmetric and bidirectional: the dominant channel runs from price to pool quality (F = 8.40, p < 10^-4 at lag 4), with the reverse channel 2.5× weaker (F = 3.40, p = 0.04 at lag 2), consistent with the architecture setting the initial composition and price then driving further deterioration. This small-sample analysis is presented as exploratory; the first-differenced daily regression (n = 330, β = −1.8, p < 0.001) is the more powerful confirmation.

### Framework-free early-warning variant

The Lemons Index depends on the composite quality score. To test whether the early warning survives without the scoring framework, we recomputed the trigger using only ledger data and Verra credit-type labels: the cumulative renewable share of deposited tonnage, R(t) = renewable tonnes deposited up to t / total tonnes up to t, with a 0.50 danger threshold (majority of pool tonnage in the credit category with independently documented near-zero additionality) and a 100,000-tonne burn-in. We evaluate two standard trigger rules. Rule 1 (first crossing): the signal crossed the 0.50 threshold on 2021-10-06, the same day as the Lemons Index trigger, at a renewable share of 77.4% over the first ~102,000 tonnes. Rule 2 (persistence-confirmed, the rule a deployed monitor would use to suppress start-up noise): the signal is confirmed once it stays above threshold permanently, which occurs from 2021-10-10, after two transient start-up dips within the pool's first ~4.3 Mt, still roughly eight and a half months before the price halved. Both rules deliver the warning within the pool's first week. The share ends at 69.11%, matching the headline composition, so any threshold at or below ~0.69 is permanently exceeded from 2021-10-10. All 1,187 deposits are type-resolved. Reproduction: `data/depositor-analysis/early_warning_framework_free.py`, results in `early_warning_framework_free_results.json`.

### Within-type cross-pool quality check

The cross-pool design-to-quality gradient is definitional if screens act only on credit type. To measure the boundary, we compared the tonnage-weighted mean composite of deposits within each nature-based credit type across the unscreened (BCT) and nature-screened (NCT) pools: ARR 50.8 vs 50.9, IFM 48.4 vs 48.2, REDD+ 31.7 vs 31.4 (maximum within-type difference 0.32 points). The screen therefore acts on type composition, not on within-type quality, which (i) makes the gradient's definitional character a measured quantity rather than an assumption and (ii) corroborates the within-token matched-pair design: credits admitted to both pools are quality-identical within type. Reproduction: `data/depositor-analysis/within_type_crosspool.py`, results in `within_type_crosspool_results.json`.

### Base-rate over-selection: extended sensitivity (relocated from Results)

BCT's renewable share is 78.5% by deposit count (versus 69.1% by tonnage). Deposits cluster by account (509 accounts, Gini = 0.94, effective N = 83.5 by HHI), motivating account-clustered inference. An excess-share coefficient (the renewable share above the 37% null, rather than the ratio) is 0.522 with an account-level bootstrap 95% CI of [0.496, 0.547]. Under conservative assumptions (the 48% high band of the base-rate confidence interval), the selection coefficient remains 1.44x (count-basis p = 1.97e-88). Over-selection becomes non-significant only at base rates exceeding 78.5%, an implausible assumption.

### Type-level Gresham exit ordering (relocated from Results)

The most valuable credit types were extracted first: ARR credits exited earliest (median March 2022), followed by industrial gas (July), IFM (October), REDD+ (November), and renewable energy last (December) — perfectly ordered by off-chain market demand (ρ = −0.74, n = 7 types).

---

## From diagnosis to remedy: an open-source quality-gating implementation

The three design principles in the Discussion (quality-differentiated pricing, dual-margin gating, dynamic floors) are implemented as an open-source reference implementation (Solidity/Foundry; MIT licence; `contracts/` in the code repository). It is a prototype for standards discussion, not production code, and has not been deployed to any network; all figures below are from the local Foundry test suite (94 passing tests, re-measured for this paper).

**Components.** (i) A rating registry (`CarbonCreditRating.sol`, implementing the `ICarbonCreditRating` interface): stores per-credit dimension scores, computes the composite in basis points, maps it to the six-tier grade scheme used in this paper, applies the seven disqualifier caps, and tracks staleness. (ii) A single-call composability primitive, `meetsGrade(token, minGrade)`, the quality analogue of `balanceOf`: any pool, exchange, or retirement contract can gate on it without understanding the scoring internals. (iii) A gated pool (`QualityGatedPool.sol`) that accepts a deposit only if the credit meets a minimum grade and its rating is fresh, the deposit-side half of dual-margin gating. (iv) A real-time monitor implementing the cumulative Lemons Index and the framework-free renewable-share variant of this paper's early-warning section (an off-chain Python reference script, `early_warning.py`, not a contract).

**Oracle trust.** Ratings enter the registry under a staged trust model: a single authorised rater (stage 1, the prototype default); k-of-n attestations relayed from the Ethereum Attestation Service (stage 2, implemented in `CarbonCreditRatingEASAdapter.sol`); staked raters with slashing (stage 3, design only). Known limitations are documented in the repository (no dispute mechanism, ERC-20 credits only, no proof-of-retirement linkage).

**Measured gas (Foundry `forge test --gas-report`, solc 0.8.24).** Rating write (`setRating`): 167,720 gas cold, 30,308 warm update. Gate check (`meetsGrade`): 19,244 gas. Rating read (`ratingOf`): 20,823. Staleness check: 7,097 (early exit) to 19,097. EAS attestation relay: 96,592 to 250,086. Registry deployment: ~2.36M gas. A single `meetsGrade` gate check costs about 19k gas; the prototype pool's two-call pattern (`ratingOf` plus `isStale`) adds roughly 30-40k gas to a deposit, still small relative to typical pool interactions.

**Cross-domain generalization.** The same registry and gate contracts, with zero code modification, gate biodiversity credits and renewable energy certificates in the test suite (`Generalization.t.sol`; example gates for Klima retirement, Toucan CHAR fee tiers, biodiversity, and RECs in `contracts/examples/`). The failure mode this paper documents, and the remedy, are not carbon-specific.

## Supplementary Figures

### Supplementary Figure 1. Rank correlation between the framework and commercial carbon credit rating agencies.

**Provenance note (non-blind).** The expanded comparison set (n = 27) was scored with public agency ratings in view: the scoring rationales in `data/rank-correlation/new_scores.md` explicitly reference agency ratings for several projects. The correlation is therefore a concordance check, not a blind validation. The earlier REDD+-only subset (n = 6, scored against ratings published in a third-party comparison table) gives a mean pairwise Spearman of +0.343 against commercial raters, against an inter-agency mean of +0.009.

(**a**) Spearman rank correlation heatmap for pairwise comparisons among four raters on six REDD+ projects: our framework, BeZero Carbon, Calyx Global (net-zero-aligned metric), and Sylvera (net-zero-aligned metric). Cell values are Spearman $\rho$; colour scale ranges from -1 (red) to +1 (blue). The mean inter-agency correlation among the three commercial raters is $\rho$ = 0.009 (range: -0.664 to +0.566), while the mean correlation between our framework and the three agencies is $\rho$ = 0.343 (range: -0.200 to +0.664). The BeZero--Calyx anti-correlation ($\rho$ = -0.664) indicates systematic disagreement on how to weight additionality concerns in avoided-deforestation projects. (**b**) Scatter plot of our framework's composite grade versus BeZero Carbon rating for 27 paired projects spanning 12 methodology types (REDD+, biochar, enhanced weathering, cookstoves, direct air capture, improved forest management, methane abatement, landfill gas, ODS destruction, renewable energy, jurisdictional REDD+, and ARR). Each point is labelled by project type. Spearman $\rho$ = +{{quality.bezero_rho}} (Kendall $\tau$-b = 0.821, 100% within $\pm$1 grade). The framework's agreement with BeZero exceeds the mean pairwise agreement among the three commercial agencies across both datasets. The stronger cross-type correlation ($\rho$ = +{{quality.bezero_rho}}) compared to REDD+-only ($\rho$ = 0.664) confirms that inter-rater disagreement is concentrated in credit categories where counterfactual baselines are inherently uncertain.

### Supplementary Figure 2. BCT grade distribution (scored subset, dominated by BB--B) versus CHAR grade distribution (100% AA).

Paired stacked bar charts comparing the grade distributions of the Toucan BCT pool (left, $n$ = {{composition.n_projects}} unique projects, tonnage-weighted) and the Toucan CHAR biochar pool (right, $n$ = 12 projects). BCT: in this illustrative scored subset, credits fall almost entirely within the BB and B grade bands. (Across the full 345-token pool, BBB-grade credits account for roughly 10% of tonnage; the gating counterfactual in the main text is run on the real deposit stream, where a BBB floor admits this BBB tonnage and cuts the deposit-weighted deficit from 0.689 to 0.506 while admitting 7.2% of tonnage.) CHAR: 100% of credits score AA (composite scores ranging from 75 to 84, mean 77.9). PQD = 0.221. The two pools operated on the same blockchain infrastructure (Toucan bridge) and drew from overlapping registries (Verra VCS for BCT; Puro.earth and Verra for CHAR). The sole design difference is CHAR's quality restriction: a narrow project allowlist limited to high-integrity biochar projects with durable carbon storage ($>$100-year permanence). The 0.46-point PQD gap ({{quality.bct_pqd}} vs. {{quality.char_pqd}}) quantifies the quality improvement achievable through pool-design restrictions. BCT's 100% BB--B distribution represents a low-type pooling equilibrium with no quality gradient remaining. CHAR's 100% AA distribution demonstrates that category restriction at the pool-design level prevents quality collapse within the restricted universe.

### Supplementary Figure 3. Directed acyclic graph for the within-token matched-pair design.

Causal diagram for the {{within_token.n_shared_tokens}}-token within-pool comparison. Nodes: credit identity (quality, vintage, registry, project type), pool membership (BCT vs NCT), pool design (uniform vs quality-screened pricing), off-chain resale value, and redemption outcome. Because the same credit identity feeds both pools, the matched-pair contrast severs every path from credit identity to outcome that does not run through pool design: credit-quality confounding is blocked *by construction* (the identity node is held fixed within each pair). The one open backdoor is selection into the shared set — the process by which a credit comes to be deposited in both pools — represented as an arrow from credit identity and depositor behaviour to "in both pools". The Rosenbaum bound ($\Gamma$ = {{within_token.sensitivity_gamma}}) quantifies how strongly this unobserved selection would have to act on the redemption odds to overturn the result. Arrows from pool design to redemption outcome (the estimand) and from off-chain value to redemption outcome (the economic mechanism: high off-chain value motivates extraction from the unscreened pool) are the structural relationships the matched-pair design isolates.

---

## Supplementary Tables

### Supplementary Table 1. Temporal quartile analysis of BCT deposit quality.

{{composition.n_deposits}} BCT deposits divided into four equal-sized quartiles by block number. For each quartile: block range, number of deposits, simple mean composite, volume-weighted mean composite, percentage at B grade, and total tonnes deposited. Full-sample Spearman $\rho$ = -0.24 ($p$ < 10$^{-16}$). Quality declines monotonically across quartiles. The dramatic volume decline from Q1 to Q4 reflects both the approaching end of BCT's active period and the price collapse reducing deposit incentives. By Q4, quality variance has collapsed: the pool accepts effectively a single credit type.

### Methane screening pipeline (literature-anchored; not used for any claim)

**India CDM grid emission factor comparison (methodological wedge, not an integrity finding).** A comparison of CDM combined-margin emission factors against Ember grid-*average* emission factors for Indian CDM renewable projects in the pool produces an apparent per-unit wedge. This comparison sets a combined-margin (build + operating margin) quantity against a grid-average quantity, so it is subject to an average-versus-marginal caveat and carries essentially no project-level information; we therefore report it only as a methodological wedge and do **not** use it as an integrity finding.

**Methane screening pipeline (not a measurement).** The repository includes a screening pipeline (`data/satellite-analysis/sentinel_ch4_analysis.py`) that scores waste/methane projects against Sentinel-5P TROPOMI-style site-versus-background enhancements and public plume catalogues. The committed outputs are generated from literature-anchored reference series bundled with the script (so the pipeline runs end-to-end without Earth-observation credentials), not from live retrievals; they are therefore illustrative of the method only and are not used to support any claim in this paper. Running the pipeline against live TROPOMI retrievals (function `pull_s5p_series_live`) is left as the activation step for a remote-sensing collaboration, alongside the unprocessed REDD+ deforestation pipeline noted below.

### NFTX cross-asset replication (quantitative)

To test whether uniform-pricing selection generalises beyond carbon, we ran a BCT-isomorphic pipeline on six NFTX v2 vaults on Ethereum (MILADY, PHUNK, WIZARD, MEEB, BGAN, MANA): pools where non-fungible tokens deposit and redeem at one vault-token price regardless of which item is involved. All mint/redeem events (9,866 mint and 11,017 redeem events moving 21,871 and 19,843 items) and wallet-level vault-token transfers were reconstructed from on-chain logs via the Etherscan API; the per-item value panel (120,680 ETH-denominated marketplace sales fetched, 120,427 usable after excluding zero-price or blockless records) via the Alchemy NFT API. Each deposited or redeemed item was assigned the price percentile of its nearest-in-block sale (any date; the percentile is computed among collection sales within +/-200,000 blocks of that sale, so ranks are drift-controlled; an item's collection-relative rank is assumed persistent between its sale and the vault event). Items with no observable sale are excluded; coverage is reported per vault (68-89%, except MANA at ~15%). Reproduction: `data/cross-domain/fetch_nftx_events.py`, `fetch_nft_sales.py`, `nftx_dual_margin.py`; results in `nftx_dual_margin_results.json`.

**Entry-margin selection replicates in all six vaults.** Collections are strongly value-heterogeneous under uniform pricing (sale P90/P10 of 7x to 110x), and deposited items sit below the collection median in every vault (median deposited-item percentile 0.33-0.49, MILADY at 0.485; per-vault Wilcoxon p < 0.05 in all six; cross-vault sign test p = 0.016). Under a strict matching rule (only sales within 200,000 blocks of the event; coverage 10-42%), the effect is stronger in five vaults (median percentiles 0.25-0.40, each p < 1e-10) and marginal in MILADY (0.495, not significant): the entry-margin result is robust in five of six vaults and directional in all six. This is consistent with owners depositing low-value items and keeping high-value ones: the entry margin, which NFTX leaves open (any collection item mints one vault token), exhibits exactly the lemons selection this paper documents for BCT's entry side. The result is unchanged when the low-coverage vault (MANA, ~15% sale coverage) is excluded: 5 of 5 remaining vaults, sign test p = 0.031.

**Exit-margin extraction is absent** (redeemed-vs-deposited percentile gaps of -3.4 to +1.4 pp, none significant). We checked and rejected one candidate mechanism: deposited items remain value-dispersed (IQR of deposited-item percentiles 0.35-0.50 against a uniform baseline of 0.50), so scarcity of extractable spread does not explain the absence. One design fact is consistent with it: selective use of the exit is priced (current on-chain fees, 2026-07-03: random redemption 1-2% vs targeted 2-8% in all six vaults; historical fee schedules may have differed), but we do not identify the mechanism here. The cross-asset picture is therefore: at BCT the bridge passed heterogeneous credits in wholesale (99.6% pass-through) and selection expressed at both margins, entry-side quality loading and exit-side extraction; at NFTX selection expresses at entry, and the exit shows none.

**Account structure (corrected).** Minter/redeemer wallet overlap, net of router contracts (addresses handling >5% of a side's events), ranges from 10.4% (MILADY) to 42.6% (MEEB) of redeemers, with redeemer-to-minter ratios of 0.8x to 3.5x. These figures supersede the aggregate overlap statistics previously reported for NFTX (1.3% overlap, 2-31x ratios), which derived from an unsaved query whose wallet attribution was confounded by router contracts; the corrected pipeline is fully reproducible from the committed scripts. NFT vault account separation is accordingly weaker than BCT's (1.4% overlap), an honest difference between the markets.

| Vault | Sale P90/P10 | Deposited median pctile | Wilcoxon p (<0.5) | Exit gap (pp) | MW p | Coverage (dep/red) | Acct overlap | Fees rand/target |
|---|---|---|---|---|---|---|---|---|
| MILADY | 22.26 | 0.48 | 0.000527 | -1.0 | 0.691 | 89%/89% | 10.4% | 1%/2% |
| PHUNK | 14.25 | 0.44 | 1.8e-12 | +0.5 | 0.463 | 68%/68% | 24.5% | 2%/3% |
| WIZARD | 31.25 | 0.43 | 1.33e-16 | -0.8 | 0.807 | 82%/83% | 34.8% | 2%/3% |
| MEEB | 109.54 | 0.36 | 6.04e-66 | +1.4 | 0.216 | 85%/86% | 42.6% | 2%/3% |
| BGAN | 10.8 | 0.33 | 4.18e-74 | +0.5 | 0.262 | 79%/80% | 31.0% | 2%/3% |
| MANA | 6.97 | 0.34 | 1.64e-19 | -3.4 | 0.723 | 14%/15% | 25.0% | 2%/8% |

Deposited median pctile: tonnage here is item count; pctile below 0.50 means deposits come from the cheaper half of collection sales (drift-controlled at the matched sale's date). Exit gap: redeemed minus deposited median percentile. Fees read via on-chain view calls on 2026-07-03 (`fetch_vault_fees.py`, output committed) and recorded as constants in the analysis script.

### Supplementary Table 2. Vintage-free robustness check: temporal correlation with and without vintage dimension.

Robustness analysis comparing the temporal quality correlation under two composite specifications: the full composite (all dimensions including vintage) and a vintage-free composite (vintage dimension removed, remaining weights renormalized). Full composite: Spearman $\rho$ = -0.24 ($p$ < 10$^{-16}$); vintage-free composite: $\rho$ = +0.24, sign reversal. The reversal demonstrates that the observed temporal decline is entirely attributable to the vintage dimension: later deposits carried systematically older vintages, which score lower. This is reported as a transparency and robustness result: the temporal decline is real in the composite but is mechanistically a vintage-selection effect rather than evidence of causal quality degradation over calendar time; the table reports both specifications side by side to allow readers to assess the sensitivity of the temporal finding to the inclusion of vintage scoring.

### Supplementary Table 3. Framework-free prediction accuracy.

A type-only prediction rule (credits in high-demand categories predicted redeemed, all others stranded) achieves 96.9% accuracy, 9.9 percentage points above a naive null model; the quality-grade rule (BBB+ predicted redeemed) achieves 91.9%. Credit type captures the dominant axis of selective redemption, and the quality framework adds no predictive power beyond type classification. The monotonic grade–redemption pattern (B 2.4% < BB 31.0% < BBB 78.0%) reflects this: all BBB tokens are nature-based credits with strong off-chain demand, while B-grade tokens are CDM-era renewables with none. Within the 116 renewable tokens, neither vintage (ρ = 0.112, p = 0.23) nor quality grade (p = 0.20) significantly predicts redemption. The type-only rule's category selection is ex post, so the 96.9% accuracy should be read as a characterisation of which variable drives redemption rather than as a prospective prediction.

### Supplementary Table 4. Mean deposit composite by pool and screening design.

Cross-sectional comparison of five tokenized pools across two independent operators, each classified by screening design. Mean deposit quality rises monotonically with screening strength (UBO = C3's unscreened pool; NBO = C3's nature-screened pool).

| Pool | Operator | Screening design | Mean composite |
|------|----------|------------------|---------------:|
| BCT  | Toucan   | unscreened       | 31.1 |
| UBO  | C3       | unscreened       | 28.9 |
| NCT  | Toucan   | nature-screened  | 40.0 |
| NBO  | C3       | nature-screened  | 39.0 |
| CHAR | Toucan   | category-allowlist | 77.9 |

The ~10-point unscreened-to-screened gap appears within each operator separately, isolating it from operator-specific factors. Both unscreened pools degrade over their operating life (BCT ρ = −0.439; C3 ρ = −0.329, p = 0.004) while the screened pools do not. Moss MCO2, a single fungible basket token with no per-token credit identity, is structurally outside this comparison.

### Supplementary Table 5. Entity-level independence audit: top-20 accounts per margin, with first-funder resolution.

| Account | Margin | Deposited (t) | Redeemed (t) | Type | First funder | Notes |
|---|---|---|---|---|---|---|
| 0xaf52…81b0 | deposit | 1,967,489 | 0 | EOA | 0xe806…a5ed | via internal tx |
| 0xf367…2156 | deposit | 1,526,175 | 0 | EOA | 0x1fdc…f661 | via internal tx |
| 0xee99…0b83 | deposit | 1,328,930 | 0 | EOA | 0xaeb6…cc7a | shared cross-side funder |
| 0xe519…688f | deposit | 1,284,435 | 0 | EOA | 0x8c5a…ae7e |  |
| 0xc465…1a8c | deposit | 1,273,817 | 0 | EOA | 0x4c76…94d7 |  |
| 0xdab7…e900 | deposit | 1,192,245 | 0 | EOA | 0xdb6f…f498 | via internal tx |
| 0x5298…26e2 | deposit | 942,657 | 0 | EOA | 0x02a8…eb9b |  |
| 0x2845…8b20 | deposit | 921,023 | 0 | EOA | 0x5216…b8d6 |  |
| 0xd85c…001f | deposit | 822,698 | 0 | EOA | 0xc9d1…7e7a |  |
| 0xe8d7…91ff | deposit | 763,977 | 0 | EOA | 0x886b…eb82 |  |
| 0x0000…826f | deposit | 681,776 | 0 | EOA | 0x8670…46b1 |  |
| 0x65a5…995c | redeem | 0 | 651,334 | contract | n/a |  |
| 0xa3fb…c075 | deposit | 477,970 | 0 | EOA | 0x0000…1010 | via internal tx |
| 0xc450…eaf5 | deposit | 464,905 | 0 | EOA | 0x1b02…7506 | via internal tx |
| 0x79c8…52d7 | deposit | 450,186 | 0 | EOA | 0xfa0b…81b9 |  |
| 0xac5f…f05f | both | 343,952 | 46,000 | EOA | 0xe2e4…c8af | dual-margin |
| 0x0bf9…d496 | deposit | 385,347 | 0 | EOA | 0x1b02…7506 | via internal tx |
| 0x51d3…36be | deposit | 383,674 | 0 | EOA | 0xb192…3771 |  |
| 0xcf23…6e5a | deposit | 365,157 | 0 | EOA | 0x0824…08da |  |
| 0xb0ee…01cf | both | 317,391 | 30,000 | EOA | 0x1730…ef34 | dual-margin |
| 0x1b8e…5d64 | redeem | 0 | 335,556 | EOA | 0x0ff1…6ff5 |  |
| 0xb208…fa93 | deposit | 307,424 | 0 | EOA | unresolved |  |
| 0xee4b…e3e9 | redeem | 0 | 195,051 | EOA | 0xeec0…8205 |  |
| 0x4b3e…c3c8 | redeem | 0 | 188,205 | EOA | 0x7837…53f7 | likely exchange/disperser; via internal tx |
| 0x8556…83bc | redeem | 0 | 183,629 | EOA | 0x51e3…75e0 |  |
| 0xcefb…89ca | redeem | 0 | 162,960 | contract | n/a |  |
| 0x3626…29c0 | redeem | 0 | 143,046 | EOA | 0x7cea…092e |  |
| 0x7de5…1596 | redeem | 0 | 135,100 | EOA | 0xc465…1a8c |  |
| 0x92ac…ddf2 | redeem | 0 | 116,000 | EOA | 0x7837…53f7 | likely exchange/disperser; via internal tx |
| 0xc4fe…c437 | redeem | 0 | 103,785 | EOA | 0x7837…53f7 | likely exchange/disperser; via internal tx |
| 0x2008…0050 | redeem | 0 | 67,703 | contract | n/a |  |
| 0x222a…adbf | redeem | 0 | 56,194 | contract | n/a |  |
| 0x1633…d429 | redeem | 0 | 51,767 | EOA | 0xe780…e245 |  |
| 0x0c69…4473 | redeem | 0 | 40,708 | contract | n/a |  |
| 0x8a30…87b7 | redeem | 0 | 21,057 | EOA | 0x375c…61d5 |  |
| 0x84f5…e684 | redeem | 0 | 20,889 | EOA | 0xaeb6…cc7a | shared cross-side funder |
| 0x1730…ef34 | redeem | 0 | 15,477 | EOA | 0x842e…4e0e |  |
| 0xe067…029b | redeem | 0 | 9,288 | EOA | 0xe780…e245 |  |

Margins: side(s) of the pool on which the account is a top-20 participant. First funder: source of the wallet's earliest incoming native-MATIC transfer (plain or internal transaction). The shared cross-side funder `0xaeb6…cc7a` funded one deposit-side and one redemption-side wallet within 77 hours in October 2021. Full addresses and transaction identifiers are in `data/depositor-analysis/entity_funding_analysis.json`.

### Supplementary Table 6. Robustness summary: what each headline claim rests on.

| Claim | Evidence base | Depends on author framework? | Reproduction file |
|---|---|---|---|
| 69.1% renewable / 4.2% REDD+ composition | Ledger tonnage + Verra type labels | No | `bct_composition_complete.json` |
| 1.87x base-rate over-selection | Type shares vs VCS registry base rates | No | `base_rate_analysis.json` |
| Redemption asymmetry (industrial gas 100% vs renewables 3.7%) | Pool Transfer events + Verra type labels | No | `redemption_analysis.json` |
| Within-token +73.9 pp cross-pool gap | Identical tokens in both pools; type/vintage/registry held fixed | No | `within_token_did.json` |
| Dual-margin account structure (account-level) | On-chain transfers + first-funder audit | No | `entity_funding_analysis.json` |
| $146M welfare gap (illustrative) | Type-level additionality distributions from independent literature + SCC Monte Carlo | No (framework-adjacent: uses literature additionality rates, not composite scores) | `welfare_quantification_results.json` |
| Early-warning trigger (~9-month lead) | Lemons Index (composite-based); framework-free variant permanently above threshold from the pool's first week | Partially (framework-free variant confirms) | `early_warning_results.json`, `early_warning_framework_free_results.json` |
| NFT-vault cross-asset replication (entry-margin selection, 6/6 vaults) | On-chain events + marketplace sale percentiles | No | `nftx_dual_margin_results.json` (data/cross-domain/) |
| CCP calibration and cross-pool gradient | Composite scores vs CCP labels / pool means | Yes (gradient measured as definitional: within-type cross-pool differences <=0.32 points) | `ccp_effect_size_results.json`, `multipool_comparison.json` |

File paths are relative to `data/depositor-analysis/` or `data/statistical-analysis/`. The first five rows carry the paper's core findings; the framework-dependent rows are validation and corroboration, not load-bearing claims.
