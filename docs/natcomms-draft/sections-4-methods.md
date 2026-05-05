# Methods

**Paper**: "On-chain forensics reveal who profited from the first tokenized carbon collapse"

---

## On-chain data collection

We collected all deposit transactions to the Toucan Protocol BCT pool contract on the Polygon blockchain using a Polygon RPC endpoint. The BCT pool contract accepts Toucan-bridged TCO2 tokens, each representing a specific Verra VCS project and vintage year. We identified 1187 deposit transactions spanning the period from BCT's launch in October 2021 to the effective cessation of new deposits in late 2022. These 1187 deposits mapped to 168 unique VCS project identifiers (345 unique TCO2 token addresses, reflecting multiple vintages per project) and approximately 22 million tonnes of tokenized carbon credits.

For each deposit, we recorded: the transaction hash, block number and timestamp, depositor address, TCO2 token contract address, Verra VCS project identifier (extracted from the TCO2 token metadata), vintage year, and tonnage deposited. Project identifiers were cross-referenced against the Verra registry to obtain methodology category (e.g., VM0007 for REDD+, AMS-I.D for grid-connected renewables), country of origin, and CCP eligibility status.

**Project classification.** Each of the 168 unique projects was classified into one of eleven methodology categories based on the Verra registry entry: (i) renewable energy (grid-connected wind, hydro, solar, and geothermal; CDM methodologies AMS-I.D, ACM0002, and equivalents), (ii) fossil fuel switching, (iii) waste management and methane capture (landfill gas, waste-to-energy; AMS-III.G, ACM0001), (iv) REDD+ (avoided deforestation and reduced degradation; VM0007, VM0009, VM0015, VM0006), (v) afforestation/reforestation (ARR), (vi) industrial gas destruction (HFC-23, N$_2$O; AM0001, AM0021), (vii) improved forest management (IFM), (viii) energy efficiency, (ix) industrial processes, (x) agriculture, and (xi) cookstoves. Tonnage-weighted shares were computed for each category. Classification was performed by the authors based on Verra's published methodology descriptions; we did not independently verify registry-assigned categories.

**Tonnage weighting.** Pool-level composition statistics and quality metrics were computed with tonnage weighting: a project contributing 500,000 tonnes to the pool received 50 times the weight of a project contributing 10,000 tonnes. This reflects the pool's actual quality exposure: a single large deposit of low-quality credits has a greater impact on the pool's average quality than many small deposits of high-quality credits.

## Quality scoring framework

We developed a composite quality scoring framework evaluating seven dimensions identified in the integrity literature as the primary determinants of credit quality. Each credit was scored on a 0--100 scale across six active dimensions: removal type hierarchy (weight 0.250), additionality (0.200), monitoring, reporting, and verification (MRV) grade (0.200), permanence (0.175), vintage year (0.100), and registry and methodology quality (0.075). Weights were chosen to reflect the relative importance assigned by the Oxford Offsetting Principles^1^ and the ICVCM CCP Assessment Framework^2^, with removal type receiving the largest weight to encode the Oxford hierarchy (removal > avoidance > reduction).

The seventh dimension, co-benefits, was assigned a weight of zero and converted to a binary disqualifier gate (the "safeguards-gate"). This design decision followed from Berg et al.^3^, who found that buyers pay approximately double the premium for credits with co-benefit narratives regardless of underlying integrity. Including co-benefits as a scored dimension would therefore amplify adverse selection by inflating the scores of credits whose quality deficits are obscured by compelling co-benefit narratives. We retained the co-benefits rubric as an informational field and used its scoring bands to determine whether to flag the community-harm disqualifier.

The composite score was computed as:

$$C = \sum_{i=1}^{7} w_i \times s_i$$

where $w_i$ is the weight and $s_i$ is the per-dimension score for dimension $i$, with $w_{\text{co-benefits}} = 0$. Composites were mapped to letter grades: AAA ($\geq$90), AA ($\geq$75), A ($\geq$60), BBB ($\geq$45), BB ($\geq$30), and B (<30).

Seven disqualifier conditions cap the maximum achievable grade regardless of composite score. Three conditions cap at grade B (evidence of double counting, failed verification, credible human rights violation claims). One condition caps at BB (registry or methodology under sanction). Three conditions cap at BBB (no independent third-party verification, documented community opposition or environmental damage, published evidence of biodiversity loss^4^). Disqualifiers were applied after composite scoring and never raised a grade, only lowered it.

**Distributional scoring.** Each per-dimension score was modelled as normally distributed around its point estimate, with standard deviations calibrated from the inter-rater reliability study. Calibrated per-dimension standard deviations ranged from $\sigma$ = 4.0 (permanence) to $\sigma$ = 11.1 (registry and methodology). Under the assumption of independent dimension scores, composite variance was computed as:

$$\text{Var}(C) = \sum_{i} w_i^2 \times \sigma_i^2$$

Grade posteriors were computed via the Gaussian CDF: $P(\text{grade} = G) = \Phi\bigl(\frac{u_G - \mu}{\sigma_C}\bigr) - \Phi\bigl(\frac{l_G - \mu}{\sigma_C}\bigr)$, where $l_G$ and $u_G$ are the lower and upper boundaries of grade $G$, $\mu$ is the composite point estimate, and $\sigma_C = \sqrt{\text{Var}(C)}$. The reported grade was the posterior mode. Machine-readable rubrics are provided in JSON format at `data/scoring-rubrics/`.

## Pool Quality Deficit

We defined the Pool Quality Deficit (PQD) to quantify quality degradation in a carbon credit pool:

$$\text{PQD}(\text{pool}) = 1 - \frac{\bar{C}}{100}$$

where $\bar{C}$ is the tonnage-weighted mean composite score of all credits in the pool. The PQD ranges from 0 (every credit scores 100; no quality degradation) to 1 (every credit scores 0; complete quality failure). Higher values indicate worse quality. The metric is interpretable, pool-comparable, and computable from publicly available project data.

For BCT, $\bar{C}$ was computed as the tonnage-weighted mean across all 168 unique projects, using the composite scores from methodology-level archetypes with per-project vintage adjustments. For the 34-segment quality atlas, PQD was computed per segment using the methodology archetype score for each segment.

**Within-pool permutation test.** We tested whether tonnage allocation within BCT was biased toward the lowest-quality tokens using a single within-pool permutation test with 100,000 iterations (seed = 42). In each iteration, quality scores were permuted across the 345 BCT-eligible TCO2 tokens while preserving the actual tonnage distribution of deposits, and the volume-weighted mean composite was recomputed. The observed volume-weighted mean was compared against the permutation distribution to obtain a $z$-score ($z$ = $-$0.64, $p$ = 0.27) and empirical $p$-value. This test asks whether the specific tonnage-to-token assignment within BCT is non-random with respect to quality; it does not compare BCT to an external universe. We also computed the Spearman rank correlation between per-token quality and total deposited tonnes as a complementary measure of tonnage-quality association.

**Within-type temporal decomposition.** To identify which credit types drove the overall temporal quality decline, we computed separate Spearman rank correlations (block number vs. composite) for each of the eight methodology types with $n$ $\geq$ 10 scored deposits. We further computed a compositional shift metric: the Spearman correlation between block number and a binary renewable indicator (1 = renewable, 0 = other). An exit analysis tracked the median deposit block per credit type to identify the order in which types ceased active deposit.

**Vintage-adjusted partial correlation.** Within the renewable segment ($n$ = 932 with recoverable vintage metadata), we tested whether the temporal decline persisted after controlling for vintage year. We computed: (i) the Spearman correlation between block number and vintage; (ii) the Spearman correlation between block number and composite score; (iii) the Spearman correlation between vintage and composite; and (iv) the partial correlation between block and composite controlling for vintage, obtained by regressing both block and composite on vintage via ordinary least squares and correlating the residuals. A reversal of sign under partial correlation indicates that the apparent temporal quality decline is mediated by vintage drift (i.e., later deposits drew from progressively older vintages) rather than by within-vintage quality change.

## Extended scoring

Of the 345 unique TCO2 token addresses in the BCT pool, 161 were scored in the original methodology-archetype batch (corresponding to project-vintage combinations with sufficient metadata). The remaining 184 tokens were scored using the same `claude_opus_score.py` rubric rules applied to available metadata fields: methodology type (mapped to the archetype rubric for that category), vintage year (scored on the vintage decay curve), and country of origin (mapped to the registry-and-methodology sub-rubric for national registry strength). Each imputed score was flagged with `source="imputed"` in the output dataset, while the original 161 scores carry `source="original"`. This extended scoring brought coverage from 161/345 to 345/345 TCO2 tokens (100% of pool tokens scored). All analyses in this paper are reported on the full 345-token dataset; robustness checks confirm that results are qualitatively identical when restricted to the 161 original-scored tokens.

## Base-rate comparison

To test whether BCT's composition reflects selection bias rather than the underlying VCS supply, we compared BCT's renewable energy share against the Verra VCS base rate. The base rate was estimated from two independent sources: the MSCI Carbon Markets report (2023), which estimated renewable energy credits at approximately 37% of active VCS supply, and the Ecosystem Marketplace State of the Voluntary Carbon Markets report (2023), which reported a range of 26--48% depending on vintage window and counting methodology. We adopted 37% as the central estimate with a sensitivity range of 26--48%.

The selection coefficient was defined as:

$$S = \frac{f_{\text{BCT,renewable}}}{f_{\text{VCS,renewable}}}$$

where $f_{\text{BCT,renewable}}$ is the tonnage-weighted share of renewable energy credits in BCT and $f_{\text{VCS,renewable}}$ is the VCS base rate. An exact binomial test was used to test the null hypothesis that BCT's renewable share equals the VCS base rate, with $n$ equal to the effective number of independent project-vintage units and $k$ equal to the number classified as renewable. Sensitivity analysis repeated the binomial test across the full base-rate range (26--48%) and extended to post-2008 VCS vintage-adjusted rates up to 55% to confirm that the selection result was robust to base-rate uncertainty. At all tested base rates up to 55%, the selection coefficient remained significant ($p$ < 0.05).

## Bridge-level decomposition

To distinguish bridge-level from pool-level selection, we enumerated all TCO2 token contracts created by Toucan's `ToucanCarbonOffsetsFactory` on Polygon (queried via Dune Analytics decoded event tables: `ToucanCarbonOffsetsFactory_evt_TokenCreated`, filtered to `evt_block_time` $\leq$ 1 January 2023). We then cross-referenced against the set of TCO2 addresses appearing in BCT deposit events (`basecarbontonne_evt_deposited`). The ratio of BCT-deposited tokens to total bridged tokens measures the pass-through rate: a rate near 100% indicates that pool composition is determined at the bridge level, while a low rate would imply pool-level selection from a diverse bridged universe.

## Event study

We exploited two exogenous shocks to the crypto-carbon market to test whether the quality composition of BCT deposits changed in response to market stress events:

1. **Terra/LUNA collapse**: May 9, 2022 (approximate Polygon block 28,400,000), when the UST algorithmic stablecoin lost its peg, triggering a broad DeFi liquidity crisis.
2. **FTX collapse**: November 6, 2022 (approximate Polygon block 35,200,000), when the FTX exchange filed for bankruptcy.

For each event, we split scored deposits into pre-event and post-event periods and computed the Spearman rank correlation between block number and composite quality score within each period. Period-split correlations were compared to assess whether quality degradation accelerated, reversed, or was unaffected by the shock. As a robustness check, we restricted the analysis to the pre-Terra subsample only (deposits before block 28,400,000) and recomputed the temporal correlation to test whether the quality decline was already established before the first exogenous shock.

## Vintage-free robustness check

Because vintage year is mechanically correlated with deposit timing (later deposits necessarily draw from the same or later vintage pool), the vintage dimension (weight 0.10) risks introducing a tautological component into the temporal quality decline. To test this, we recomputed the composite score with vintage weight set to zero and the freed weight redistributed proportionally across the five remaining active dimensions: removal type (0.2778), additionality (0.2222), permanence (0.1944), MRV (0.2222), and registry and methodology (0.0833). The temporal correlation (Spearman $\rho$ between block number and vintage-free composite) was recomputed on the full scored deposit series. A sign reversal under the vintage-free composite (from negative to positive or to near-zero) would indicate that the vintage dimension is the primary driver of the temporal signal, undermining the interpretation that intrinsic credit quality declined over time.

## NCT cross-pool comparison

To contextualise the BCT temporal pattern, we collected all deposit events from the Toucan NCT (Nature Carbon Tonne) pool (contract address `0xD838290e877E0188a4A44700463419ED96c16107`) on the same Polygon blockchain over the same block range (20,000,000 to 37,000,000) using `eth_getLogs` with the Toucan `Deposited(address,uint256)` event signature. We identified 708 NCT deposit events. Depositor wallet addresses were recovered via `eth_getTransactionReceipt` for all 708 events. Of 708 deposits, 264 (37.3%) matched the original 161 scored TCO2 tokens. With extended scoring (345 tokens), all 708 NCT deposits (100%) are scored.

NCT and BCT share identical protocol infrastructure, bridge architecture, and blockchain substrate. NCT restricts deposits to AFOLU (agriculture, forestry, and other land use) credits with vintage $\geq$2012, functioning as a minimal quality gate on project type.

**Within-token cross-pool comparison.** We exploited the fact that 14 TCO2 tokens (all nature-based: 5 REDD+, 5 IFM, 4 ARR) were deposited into both BCT and NCT, providing a within-token comparison that holds credit quality constant while varying pool design. For each of the 14 overlap tokens, we computed the redemption rate (redeemed/deposited tonnage) separately in each pool from the same transfer cache data. The identifying assumption is that the same token's intrinsic quality does not differ between pools; any difference in redemption rate is therefore attributable to pool-level factors (composition, pricing, participant population). We note that this comparison is still observational --- BCT and NCT differ in timing, participant composition, and market conditions as well as quality-gate design --- but the within-token structure eliminates confounding from credit quality.

**Observational comparison.** The broader BCT--NCT comparison (88.6% token overlap across all scored deposits) is observational, not causal, violating the independence assumption required for difference-in-differences. Standard errors for within-pool statistics are computed using cluster-robust bootstrap (clustered by depositor wallet, 10,000 iterations, seed = 42) to account for the non-independence of deposits from the same wallet. The high token overlap means that supply-side composition changes (e.g., which projects Toucan bridged over time) affect both pools simultaneously, precluding clean causal attribution of quality differences to pool design.

**Temporal analysis.** For each pool, we computed the Spearman rank correlation between block number and composite quality score. We also divided each pool's scored deposits into quartiles by block number and computed the mean composite per quartile. A Mann--Whitney $U$ test compared the first-half and second-half quality distributions within each pool.

## Depositor-level analysis

For all 1187 BCT deposits (scored via extended scoring), we computed depositor-level concentration metrics: Gini coefficient, Herfindahl--Hirschman Index (HHI), and the effective number of depositors (1/HHI). To test whether large depositors systematically deposited lower-quality credits, we compared the quality distributions of the top 20 depositors by tonnage (71.9% of pool volume) against the remaining 489 depositors using a two-sided Mann--Whitney $U$ test. A two-sided Mann--Whitney $U$ test detects a small but significant difference ($p$ = 8.6e-5, FDR-adjusted $p$ = 1.7e-4), indicating a difference in quality distributions between large and small depositors under the unweighted deposit-level test. We note that the volume-weighted quality gap (30.3 for the top-20 vs. 35.3 for the rest) was not formally tested with a tonnage-weighted permutation test, because the unweighted test already failed to reject the null and the volume-weighted gap is driven by a small number of very large deposits rather than a systematic depositor-level pattern.

## Price-quality dynamics

Daily BCT-USDC prices were obtained from the DeFi Llama API for the Polygon SushiSwap BCT-USDC pair (828 observations). Cumulative Pool Quality Deficit (PQD) and cumulative rolling renewable share were computed from the deposit stream at daily frequency. Price and quality series were merged at daily frequency, yielding $n$ = 331 overlapping observations (21 October 2021 to 11 November 2022).

**Levels regression.** An OLS regression of BCT price on cumulative PQD and cumulative renewable share was estimated with Newey--West heteroskedasticity- and autocorrelation-consistent (HAC) standard errors (10 lags) to account for serial correlation in the non-stationary levels series. This specification captures the long-run co-movement but does not support causal interpretation due to non-stationarity.

**First-differenced regression.** To address non-stationarity, we estimated a first-differenced OLS specification: $\Delta\text{Price}_t = \alpha + \beta_1 \Delta\text{PQD}_t + \beta_2 \Delta\text{Renewable}_t + \varepsilon_t$, with HAC standard errors (Newey--West, 10 lags). The first-differenced specification yielded $\hat{\beta}_2$ = $-$1.8 (SE = 0.197, $p$ <0.001) for $\Delta$Renewable share, indicating that day-over-day increases in renewable composition were associated with contemporaneous price declines.

**Granger causality.** Bidirectional Granger causality was tested at weekly frequency using a VAR(2) model estimated via the `statsmodels` VAR module. Weekly aggregation reduced the sample to $n$ = 55 observations. Lag length was selected by AIC from candidates 1--4; AIC selected lag 2. Both the cumulative renewable share and price series are trending (non-stationary in levels); we report Granger tests on cumulative series as suggestive evidence of lead-lag relationships, noting that the small sample ($n$ = 55) limits statistical power and that the first-differenced daily regression ($n$ = 330) provides a more robust test of co-movement. Four directional tests were conducted: (i) quality $\rightarrow$ price ($F$ = 6.32, $p$ = 0.004); (ii) price $\rightarrow$ quality ($F$ = 16.08, $p$ <10^-5); (iii) cumulative PQD $\rightarrow$ price ($F$ = 3.4, $p$ = 0.042); (iv) price $\rightarrow$ cumulative PQD ($F$ = 8.4, $p$ < 10$^{-4}$). Rolling 30-day quality metrics showed no significant Granger causality in either direction. Post-hoc power analysis: at $n$ = 55 with VAR(2) (df1 = 2, df2 = 50), the minimum detectable $F$-statistic at 80% power ($\alpha$ = 0.05) is approximately 6.4. The quality-to-price result ($F$ = 6.32) falls at the power boundary; the price-to-quality result ($F$ = 16.08, 2.5$\times$ MDE) is well-powered.

## Redemption analysis

Redemptions from BCT were identified from ERC-20 Transfer events where the BCT pool contract address appears as the `from` field. Transfer event logs were collected for all 161 scored TCO2 token contracts using `eth_getLogs` on the Polygon RPC endpoint, filtered to transfers originating from the BCT pool address. This yielded 35432 redemption events.

Each redemption was matched to the quality score of the corresponding TCO2 token (using the same extended scoring framework applied to deposits). Redemption tonnage was computed from the transfer `value` field (scaled by the TCO2 token's 18-decimal precision). Redemption rates were computed per credit type as the ratio of cumulative redeemed tonnes to cumulative deposited tonnes.

The type-level redemption rate differentials (renewable 3.6% vs. non-renewable 91--100%) are self-evidently large and do not require a formal significance test for the primary finding. We note that a chi-squared test on event counts ($\chi^2$ = 4.0e6, $p$ $\approx$ 0, df = 1) confirms the differential is non-zero, but the test statistic is inflated by the large sample size (35,432 events) and the magnitude of the differential (3.6% vs. 91--100%) is the substantively meaningful quantity.

Net pool composition was computed as cumulative deposits minus cumulative redemptions at monthly intervals over the 14-month observation period. The net renewable share increased from 71% (first half mean) to 76% (second half mean), with Spearman $\rho$ = 0.81 ($p$ < 0.001) between month index and net renewable share, confirming that differential redemption amplified the pool's renewable concentration over time.

Tonnage-weighted mean quality of redeemed credits (38.7) exceeded that of deposited credits (31.7), with a difference of 7 quality points. This pattern --- higher-quality credits being selectively withdrawn --- is consistent with the Gresham prediction that undervalued assets exit the pool when they can command higher prices elsewhere.

## Wallet forensics and quality swap analysis

To identify the actors responsible for selective extraction, we reconstructed the complete deposit and redemption history for each wallet address from the 161 scored TCO2 token transfer caches. For each token, all ERC-20 Transfer events were classified as deposits (recipient = BCT pool address `0x2f800db0fdb5223b3c3f354886d907a671414a7f`) or redemptions (sender = BCT pool address). Each event was attributed to the counterparty wallet and matched to the token's quality score and credit type from the extended scoring framework.

**Redeemer profiling.** For each of the 28,897 unique redeemer wallets, we computed: total redeemed tonnage, number of redemption events, tonnage-weighted mean quality of redeemed tokens, dominant credit type (the type comprising the largest share of each wallet's redeemed tonnage), block span (range of blocks across redemption events), and whether the wallet also appeared as a depositor. Wallets were ranked by total redeemed tonnage to identify the top 20 redeemers and characterise their extraction patterns.

**Depositor-redeemer overlap and quality swap.** We identified 399 wallets appearing in both the depositor and redeemer populations (1.4% of 28,897 redeemers; 394 when restricted to the 161-token scored subset). For each overlap wallet, we computed the tonnage-weighted mean quality of deposited tokens and redeemed tokens separately, and defined the quality swap as the difference (redeemed quality minus deposited quality). A positive quality swap indicates that the wallet systematically redeemed higher-quality credits than it deposited. We computed the unweighted mean quality swap across all overlap wallets and the tonnage-weighted mean (weighting by the minimum of deposited and redeemed tonnage per wallet). The distribution of quality swaps was characterised by the number of positive, negative, and zero-swap wallets.

**Post-extraction destination tracing.** For each redemption event involving a top-20 redeemer wallet, we identified the next Transfer event for the same TCO2 token originating from that wallet address. The destination address was classified into five categories: (i) burn address (0x000...000 or 0x000...dead) indicating on-chain retirement; (ii) NCT pool contract (`0xD838...0107`) indicating cross-pool deposit; (iii) BCT pool contract indicating re-deposit; (iv) transfer to another address (likely OTC sale or DEX); (v) no subsequent outbound transfer found (still held). Hold duration was computed as the block difference between the BCT redemption event and the next outbound transfer. This tracing covers all 161 scored token transfer caches and captures the immediate next destination only; multi-hop tracing was not performed.

**Profit quantification.** To estimate the profit from selective redemption, we assigned off-chain credit prices by type using contemporaneous (2021--2022) market data from Ecosystem Marketplace and Carbon Pulse trade reports: industrial gas \$3--12/tonne, REDD+ \$4--15/tonne, IFM \$5--18/tonne, ARR \$6--20/tonne, renewable energy \$0.30--1.50/tonne. BCT redemption cost was estimated as the BCT pool price at the time of redemption plus the Toucan selective redemption fee (which varied over the pool's lifetime; selective redemption --- required for type-targeted extraction --- carried a premium over non-selective FIFO redemption), yielding a range of \$1--5/tonne across the pool's operating period. Profit per wallet was computed as $\sum_i (\text{offchain\_price}_i - \text{BCT\_cost}) \times \text{tonnes}_i$ where $i$ indexes the credit types redeemed by each wallet. Low, central, and high scenarios use the respective bounds of the price ranges. Gas fees and DEX slippage were not included and are expected to be negligible relative to the per-tonne price differentials.

**Framework-free prediction.** To test whether the quality scoring framework adds predictive power beyond credit type classification, we defined a type-only prediction rule: tokens in high-demand categories (REDD+, IFM, ARR, industrial gas --- identified ex post from the observed type-level redemption rates in Table 6) were predicted as "majority redeemed" (redemption rate $>$ 50%); all other tokens were predicted as "stranded." This rule was compared against a quality-grade prediction rule (BBB or above predicted as redeemed; BB or below predicted as stranded). Both rules were evaluated on the 161 scored BCT tokens. We note that the type-only rule's category selection is ex post, and the 96.9% accuracy should be interpreted as a characterisation of which variable drives redemption rather than as a prospective prediction. A within-type test compared BB-grade versus B-grade redemption rates among the 116 renewable energy tokens (72 B-grade, 44 BB-grade) using a chi-squared test at the tonnage level and a Mann--Whitney $U$ test at the token level.

## Wallet-clustered inference

To address the concern that the naive binomial test ($p$ = 1.35e-187) overstates significance due to within-wallet deposit clustering, we conducted three wallet-level robustness tests.

**Wallet-level permutation test.** For each of 10,000 iterations, we resampled wallets with their complete deposit portfolios under the null hypothesis that each deposit independently draws a renewable credit with probability $P$ = 0.37 (the VCS base rate). The wallet-mean renewable share was recomputed for each permutation. The observed wallet-mean renewable share (0.892) fell outside the entire permutation distribution (null mean = 0.37, SD = 0.02), yielding $p$ <0.0001.

**HHI-adjusted binomial test.** The effective number of independent observations was computed as $n_{\text{eff}}$ = 1/HHI, where HHI is the Herfindahl--Hirschman Index of wallet-level deposit concentration. With HHI = 0.012 and $n_{\text{eff}}$ = 83.5, the binomial test yielded $p$ = 2.9e-15 --- reduced by 172 orders of magnitude from the naive test but still highly significant.

**DEFF-adjusted binomial test.** As a further robustness check, we computed the design effect (DEFF) assuming an intraclass correlation coefficient (ICC) of 0.5 (a conservatively high value reflecting strong within-wallet homogeneity). The resulting DEFF = 4.4 yielded $n_{\text{eff}}$ = 270 and $p$ = 4.7e-44.

**Bootstrap CI on selection coefficient.** A wallet-level bootstrap (10,000 iterations, BCa correction) was used to construct a 95% confidence interval on the selection coefficient, defined as the wallet-mean renewable share minus the VCS base rate. The observed selection coefficient was 0.522 with a BCa 95% CI of [0.496, 0.547], indicating that the over-selection of renewable credits is robust to the clustering structure of deposits.

**External validation with BeZero ratings.** 7 BCT projects had public BeZero ratings (from our expanded rank-correlation dataset). We mapped BeZero letter grades to a numeric scale (AAA = 95, AA = 80, A = 65, BBB = 50, BB = 35, B = 20, C = 15, D = 5) and computed the Spearman correlation between our framework composites and BeZero numerics on the overlap subset. We also assessed whether the temporal degradation pattern held under external ratings by dividing BeZero-matched deposits into terciles by block number.

## CCP empirical calibration

We tested whether the framework's composite scores separated CCP-eligible from non-CCP credits using a dataset of 318 credits classified by ICVCM CCP eligibility status (165 CCP-eligible, 153 non-CCP) across 17 methodology categories. CCP classification was based on the ICVCM's published list of CCP-approved methodologies and CCP-eligible programmes as of 2025.

Five effect size measures were computed: Cohen's $d$ (pooled standard deviation), Glass's $\delta$ (using non-CCP standard deviation as denominator), Cliff's $\delta$ (nonparametric), the common language effect size (CLES), and a Mann--Whitney $U$ test with normal-approximation $z$-score including tie correction. For each parametric and nonparametric effect size, 95% confidence intervals were obtained via the percentile bootstrap method with 10,000 resamples (seed = 42). Grade distributions were encoded on an ordinal scale (B = 0, BB = 1, BBB = 2, A = 3, AA = 4, AAA = 5).

## Rank correlation with commercial rating agencies

We assessed external validity by computing rank correlations between our framework's grades and publicly available ratings from three commercial carbon credit rating agencies: BeZero Carbon, Calyx Global, and Sylvera.

**REDD+ subset.** Six REDD+ projects were drawn from Carbon Market Watch^9^ (2023, Table 20), which reported simultaneous public ratings from all three agencies as of 2 June 2023. Each agency's ordinal scale was mapped to a monotonic integer sequence (higher = better quality), and each project was scored under our framework. Spearman rank correlations ($\rho$) and Kendall's $\tau$-b were computed for all six pairwise combinations of four raters (our framework, BeZero, Calyx, Sylvera).

**Cross-type extension.** An additional 24 projects spanning 12 non-REDD+ methodology types (direct air capture, biochar, enhanced weathering, cookstoves, improved forest management, methane abatement, landfill gas, ODS destruction, renewable energy, jurisdictional REDD+, and ARR) were compiled from BeZero case studies, Calyx research publications, Sylvera press releases, and developer press releases. All 30 projects were scored under the v0.6 rubric. Of these, 27 had BeZero ratings, 9 had Calyx ratings, 7 had Sylvera ratings, and 1 had an MSCI rating. 8 projects had ratings from 2+ agencies.

**Statistical inference.** For the combined BeZero-paired dataset ($n$ = 27), Spearman $\rho$ = +0.901, Kendall $\tau$-b = 0.821, with 100% of projects within $\pm$1 mapped grade and 52% exact matches. Sub-type correlations were computed for CDR credits ($\rho$ = 0.973) and avoidance credits ($\rho$ = 0.802) separately, though sub-type sample sizes are small and should be interpreted as directional evidence.

## Inter-rater reliability study

To assess reproducibility, we conducted an inter-rater reliability study using three independent large language model raters: Claude Opus 4.6, Claude Sonnet 4.6, and Claude Haiku 4.5 (Anthropic, 2025). Each model scored 29 credits (25 real-world archetypes plus 4 synthetic stress-test credits) using the v0.4.1 rubric in isolated sessions with author grades redacted. No inter-rater communication was permitted.

Agreement metrics: (i) Fleiss' $\kappa$ across the three raters at the grade level (six categories: B through AAA); (ii) per-dimension Fleiss' $\kappa$, with continuous scores binned into 10 buckets of 10 points each; (iii) ICC(2,$k$) on the continuous composite using a two-way random effects model; (iv) exact grade agreement and within-one-band agreement between the author's grades and the panel median.

Per-dimension kappa values: permanence 0.684 (substantial), removal type 0.585 (moderate), vintage year 0.324 (fair), MRV 0.248 (fair), additionality 0.243 (fair), co-benefits 0.182 (slight), registry methodology 0.168 (slight). Per-dimension standard deviations from this study were used to calibrate the distributional scoring model.

## Sensitivity analysis

**Monte Carlo weight perturbation.** We sampled 10,000 weight vectors from a Dirichlet distribution centred on the current weights with concentration parameter 50, with co-benefits weight forced to zero. For each sampled vector, all 29 credits were rescored and assigned a grade. Global robustness was defined as the mean proportion of iterations under which each credit's grade remains unchanged (93.7% at concentration 50; 90.1% at concentration 20; 95.4% at concentration 100).

**Removal-type sensitivity.** To test whether the framework's discriminatory power depends on the removal-type dimension --- which carries the largest single weight (0.25) and which some critics may view as normatively contestable --- we set the removal-type weight to zero and redistributed its weight proportionally across the remaining dimensions. Quality differences between credit categories persisted at 98% significance under this perturbation, indicating that the framework's quality discrimination is distributed across multiple dimensions rather than concentrated in removal type.

**Cross-temporal stability.** The same 29 credits were scored under three methodology versions (v0.3, v0.4, v0.6). Grade agreement between v0.4 and v0.6 was 100% (29/29). Spearman $\rho$ between v0.3 and v0.6 composite rankings was 0.992.

## Statistical inference and multiple testing

All reported $p$-values were corrected for multiple testing using the Benjamini--Hochberg false discovery rate (FDR) procedure at $\alpha$ = 0.05, applied to the family of 10 primary hypothesis tests (see Supplementary Table). For the three headline claims (base-rate selection coefficient, BCT temporal correlation, pre-Terra temporal correlation), we supplemented asymptotic $p$-values with 10,000-permutation $p$-values. Permutation tests randomly shuffled the dependent variable (composite scores or renewable labels) across observations while preserving the independent variable (block number or deposit identity), computing the test statistic for each permutation and reporting the empirical fraction of permutation statistics at least as extreme as the observed value.

**Cluster-robust inference.** Because multiple deposits may share the same TCO2 token (and thus the same quality score), the effective sample size for deposit-level tests is closer to the number of unique tokens ($n$ = 345) than the number of deposits ($n$ = 1187). We computed cluster-robust 95% confidence intervals for the BCT temporal Spearman $\rho$ using a bootstrap that resampled at the TCO2-token level (10,000 iterations, seed = 42): each bootstrap draw sampled tokens with replacement and included all deposits for each sampled token. We report both naive (deposit-level) and cluster-robust (token-level) CIs to allow readers to assess the sensitivity of temporal inference to the clustering structure.

## Counterfactual quality-gate simulation

For BCT and five additional pools, we simulated the application of quality gates at all six grade thresholds (B, BB, BBB, A, AA, AAA). At each threshold, only credits whose final grade met or exceeded the threshold were admitted. We recomputed: the number of admitted credits, the new tonnage-weighted mean composite, the resulting PQD, and the fraction of admitted credits at grade A or above.

## 34-segment quality atlas

We defined 34 quality segments by the intersection of project type (17 methodology categories from the ICVCM taxonomy), geographic region (where sufficient data existed), and vintage band (pre-2015, 2015--2019, 2020--2023, 2024+). Each segment was scored using the median archetype score from the 318-credit methodology dataset. PQD was computed per segment. The vintage gradient was computed as the tonnage-weighted mean PQD across all segments within each vintage band.

## Data availability

All data, scoring rubrics, analysis scripts, and smart contract source code are available at https://github.com/Adeline117/carbon-neutrality under an MIT licence. Machine-readable rubrics are in JSON format (`data/scoring-rubrics/`). The 318-credit methodology batch dataset with per-dimension scores is included. All 345/345 BCT tokens are scored (161 original + 184 imputed; see Extended scoring above), with complete scores in `data/depositor-analysis/tco2_scores_complete.json`. On-chain deposit data for both BCT (1187 transactions) and NCT (708 transactions) are provided with transaction hashes enabling independent verification on the Polygon blockchain. The depositor-level analysis dataset (`data/depositor-analysis/`) includes enriched deposits, wallet portfolios, Transfer event caches for 345 TCO2 tokens, quality scores, null model results (100,000 iterations), NCT comparison statistics, and BeZero validation results. Additional result files: `event_study_results.json` (Terra/LUNA and FTX event study), `base_rate_analysis.json` (VCS base-rate comparison and binomial test), `vintage_tautology_check.json` (vintage-free robustness check), and `valid_did_analysis.json` (observational NCT comparison). LLM panel outputs for all three models across 29 credits are provided at `data/llm-panel-irr/raw/`. Analysis scripts are pure Python with NumPy/SciPy as sole dependencies.

## References

1. Allen, M. et al. The Oxford Principles for Net Zero Aligned Carbon Offsetting. University of Oxford (2020).
2. Integrity Council for the Voluntary Carbon Market. The Core Carbon Principles, Assessment Framework and Assessment Procedure. ICVCM (2023).
3. Berg, F., Kolbel, J., Pavlova, A. & Rigobon, R. The market for voluntary carbon offsets. SSRN Working Paper (2025).
4. Zeng, Y. et al. Biodiversity risks of carbon offset projects. *Nat. Rev. Biodivers.* (2026).
5. Carbon Market Watch & Perspectives Climate Group. Assessing and comparing carbon credit rating agencies. Carbon Market Watch Policy Brief (2023).
6. Akerlof, G. A. The market for "lemons": quality uncertainty and the market mechanism. *Q. J. Econ.* **84**, 488--500 (1970).
