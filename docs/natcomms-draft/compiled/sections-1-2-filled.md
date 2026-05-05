# Anatomy of a market failure: on-chain evidence reveals renewable energy credits, not REDD+, drove the collapse of tokenized carbon markets

## 1. Introduction

The collapse of Toucan Protocol's Base Carbon Tonne (BCT) pool --- from a peak price of approximately $7 per token in late 2021 to below $0.50 by mid-2023 --- is widely cited as evidence that tokenized carbon markets failed because of low-quality REDD+ credits flooding the pool. Industry post-mortems, Toucan's own pool redesign decisions (creating NCT specifically for nature-based credits), and the broader VCM discourse have converged on a narrative in which avoided-deforestation projects with contested baselines exploited BCT's quality-blind design, driving a quality collapse that destroyed buyer confidence^1,2,3^. This narrative has shaped regulatory responses, pool design decisions, and academic commentary on blockchain-based environmental markets.

But no one has actually looked at what BCT contained.

The on-chain composition of BCT --- the specific credits deposited by specific addresses via specific transactions on the Polygon blockchain --- is public, immutable, and trivially queryable. Yet the academic literature on BCT's collapse has relied exclusively on aggregate market data (price, volume, total value locked) rather than on the credit-level composition data that the blockchain was designed to make transparent^4,5,6^.

Here we analyse all 1187 deposit transactions representing 168 unique VCS projects and 21984482 tonnes of carbon credits deposited into BCT on Polygon between October 2021 and late 2022. We find that the prevailing narrative is wrong. BCT was 69.1% renewable energy credits --- grid-connected wind, hydro, and solar from China and India --- and just 4.2% REDD+. This 69.1% represents a 1.87$\times$ over-selection relative to the Verra VCS base rate of approximately 37% renewable (wallet-clustered permutation $p$ <0.0001), robust across all plausible base-rate assumptions (26--55%). Using an open quality scoring framework validated against the ICVCM Core Carbon Principles (CCP) label (Cohen's $d$ = 1.8) and BeZero Carbon ratings ($\rho$ = +0.901, $n$ = 27), we show that BCT's quality composition is connected to its price trajectory through a bidirectional feedback loop: quality changes Granger-cause price movements ($p$ = 0.004) and price declines attract progressively lower-quality deposits ($p$ < 10$^{-5}$). Quality-gated pools exhibit descriptively better outcomes --- NCT (PQD 0.601), CHAR (PQD 0.221) --- though these cross-pool comparisons are observational. The on-chain implementation of quality gating is detailed in our companion paper on the ERC-CCQR standard^9^.


## 2. Results

### 2.1 BCT's real composition contradicts the REDD+ narrative

We queried the Polygon blockchain for all deposit transactions to the Toucan BCT pool contract, identifying 1187 deposits spanning 168 unique Verra VCS projects and 21984482 tonnes of tokenized carbon credits. Each project was classified by Verra registry methodology category (see Methods).

The composition was overwhelmingly dominated by renewable energy credits (Fig. 1). Grid-connected wind, hydro, and solar projects constituted 69.1% of total deposited tonnage, drawn almost entirely from Chinese CDM-era wind farms and Indian grid-connected solar and hydro projects registered between 2008 and 2013 --- precisely the categories that the ICVCM has declined to approve for CCP eligibility, and that Cames et al.^12^ and Schneider et al.^13^ have documented as having near-zero additionality.

The remaining composition: fossil fuel switching 10.4%, waste management and methane capture 5.5%, REDD+ 4.2%, afforestation/reforestation (ARR) 3.9%, industrial gas destruction 3.1%, improved forest management (IFM) 2%, and smaller categories below 1%. The REDD+ share is more than 16 times smaller than the renewable energy share; even combining all nature-based categories, the total is 10.3% versus 69.1% for renewables alone.


### 2.2 Base-rate selection: BCT over-selected renewables at 1.87$\times$ the registry rate

BCT's renewable dominance could, in principle, reflect the shape of the VCS-eligible universe. We obtained Verra VCS issuance data from MSCI (2023) and Ecosystem Marketplace (2023) indicating that renewable energy credits constitute approximately 37% of total VCS issuance by volume (sensitivity range 26--48% depending on vintage window).

BCT's renewable share (69.1% by tonnage; 78.5% by deposit count) yields a selection coefficient of 1.87$\times$ the VCS base rate. Because deposits are clustered by wallet (509 wallets, Gini = 0.94, effective $N$ = 83.5 by HHI), we use wallet-clustered inference rather than a naive binomial test. A wallet-level permutation test (10,000 iterations, resampling wallets with their full deposit portfolios under the null $P(\text{renewable})$ = 0.37) produces $p$ <0.0001; 89% of wallets have majority-renewable portfolios. The selection coefficient with wallet-level bootstrap 95% CI is 0.522 [0.496, 0.547] (excess renewable share above the 37% null). Under conservative base-rate assumptions (post-2008 VCS at 55%), the selection coefficient remains 1.43$\times$ ($p$ <10^-64). Over-selection becomes non-significant only at base rates exceeding 78.5% --- an implausible assumption.

Conversely, REDD+ is under-represented at 0.2$\times$ the VCS base rate (BCT 4.2% vs. VCS $\sim$17%), directly contradicting the narrative that REDD+ credits overwhelmed the pool.

**Bridge-level decomposition.** Enumerating all TCO2 tokens created by Toucan's factory contract reveals 369 unique tokens bridged before 2023, of which 345 (93.5%) were deposited into BCT. Only 24 bridged tokens never entered the pool. This near-complete pass-through indicates that the 1.87$\times$ over-selection relative to the VCS base rate is primarily a bridge-level phenomenon --- Toucan's permissionless bridge disproportionately attracted renewable energy credits from Verra --- rather than depositors selectively choosing renewables from a diverse bridged universe.


### 2.3 Price-quality feedback loop: composition predicts price collapse

The preceding sections establish *what* BCT contained and that its composition reflects selection. The critical question --- flagged by all three reviewers of an earlier draft --- is whether quality composition is connected to BCT's price trajectory.

We obtained daily BCT-USDC prices from DeFi Llama (828 daily observations, October 2021 -- July 2024) and merged with daily cumulative quality metrics computed from the deposit stream ($n$ = 331 overlapping days).

**Correlation.** BCT's price and cumulative PQD are strongly correlated (Pearson $r$ = 0.774, $p$ <10^-66): as the pool's quality declined, its price declined proportionally. In a first-differenced OLS regression (the credible specification for non-stationary series), changes in renewable share predict price changes ($\beta$ = $-$1.8, $p$ <0.001): each percentage-point increase in the renewable share of deposits is associated with a \$1.80 decrease in BCT's price.

**Granger causality.** At weekly frequency ($n$ = 55), we find bidirectional Granger causality (Fig. 7). Quality composition changes precede price movements ($F$ = 6.32, $p$ = 0.004 at lag 1--2): deteriorating deposit quality predicts subsequent price decline. Conversely, price changes precede quality changes ($F$ = 16.08, $p$ <10^-5): lower prices attract lower-quality deposits. This bidirectional feedback loop is the empirical signature of a uniform-price pooling collapse.

**Redemption-side evidence.** Analysis of 35432 Transfer events from the BCT pool contract reveals that the selection dynamic operated on both sides. Non-renewable credits were preferentially redeemed out of the pool: industrial gas 100% redeemed, REDD+ 99.8%, IFM 93%, ARR 91.3% --- compared with just 3.6% of renewable credits. The tonnage-weighted mean quality of redeemed credits (38.7) exceeded that of deposited credits (31.7) by 7 points ($\chi^2$ test for differential redemption by type: $p$ $\approx$ 0). As a result, BCT's net renewable share increased from 71% to 76% over the pool's lifetime.

The exit was temporally ordered: redemption quality correlates negatively with time (Spearman $\rho$ = -0.095, $p$ = 2.6e-71, $n$ = 35432). Pre-Terra redemptions (1692408 tonnes, 65% of total) had tonnage-weighted quality of 42.02 versus 32.35 post-Terra --- a 10-point gap reflecting selective exit when BCT's price was still high enough to make redemption profitable. Critically, depositors and redeemers are almost entirely distinct populations: only 1.4% of redeemer addresses overlap with the 509 depositor wallets (399 of 28897 unique redeemers). The top 10 redeemers account for 85% of tonnage (Gini 0.999), and redemption events are extremely bursty (coefficient of variation 17.1, median inter-event gap = 2 blocks $\approx$ 4.6 seconds), consistent with automated smart contract execution. This is Gresham's law with identified actors: a concentrated group of depositors (509 wallets, Gini 0.94) pushed low-quality credits into the pool, while a distinct, concentrated group of sophisticated actors systematically extracted the high-quality credits via programmatic redemption.


### 2.4 Quality atlas: 10-fold variation across the VCM

Scoring methodology archetypes across 34 segments reveals systematic, large-magnitude variation in credit quality (Fig. 4). PQD ranges from 0.076 (DACCS) to 0.759 (grid-connected renewables), a 10-fold range. Engineered CDR clusters at the high-quality end; avoidance methods (renewables, industrial gas) cluster at the low end --- consistent with the Oxford Principles hierarchy^14^, which the framework encodes through the removal-type dimension weight. BCT's PQD of 0.679 is dominated by the lowest-quality segment.

A within-pool permutation test ($z$ = $-$0.64, $p$ = 0.27, 100,000 iterations on 345 tokens) finds no evidence that depositors selected the worst tokens *within* the eligible universe. The eligible universe itself was uniformly low-quality (mean 32.3, range 27.3--52). Selection operates at the token-eligibility stage --- what gets tokenized and bridged --- not through selective deposit behaviour within the pool.

**CCP filtering and vintage gradient.** Applying the CCP label as a binary filter reduces VCM-wide PQD from 0.51 to 0.419. A vintage gradient (pre-2020 PQD 0.687, 2024+ PQD 0.273) confirms that the quality problem is concentrated in legacy credits --- the credits that dominated BCT.


### 2.5 Quality gating as market mechanism

A minimum quality gate at BBB would have admitted only 2 of BCT's 168 projects (1.2%), reducing PQD from 0.679 to 0.405 --- a 40.5% improvement. No BCT credit scored A or above. The Toucan CHAR pool (biochar allowlist, PQD 0.221) demonstrates that category restriction prevents quality collapse: the 0.46-point PQD gap between BCT and CHAR quantifies the quality improvement achievable through pool design alone^9^.


### 2.6 Temporal dynamics and robustness

**Temporal quality decline.** Deposit quality declines over BCT's operating life: Spearman $\rho$ = -0.24 ($n$ = 1187, permutation $p$ < 0.0001, BH-FDR significant). The signal is present before the Terra/LUNA crash ($\rho$ = -0.13, $p$ = 0.0001, $n$ = 792 pre-May 2022) and not attributable to KlimaDAO treasury activity (zero wallet overlap). However, cluster-robust bootstrap CI (token-level resampling) is [-0.32, +0.02], marginally including zero.

**Vintage confound.** The temporal decline is driven by the vintage-year component of the composite score. A vintage-free robustness check reverses the sign ($\rho$ = +0.24 for renewables; $\rho$ = $-$0.01 for all types). The temporal signal is a vintage-composition effect --- late deposits drew from progressively older vintages --- not within-vintage quality deterioration.

**Compositional shift.** Renewable share rises from 67% (Q1) to 99.5% (Q4). Token diversity collapses from 24 distinct scores to 2. Higher-quality types (IFM, Waste/Methane, ARR) ceased depositing earlier (median blocks 20.4M--21.7M) than renewables (32.6M).

**Depositor concentration.** 509 wallets; Gini 0.94; top 10 = 50% of tonnage. Large and small depositors deposit similar quality (two-sided Mann--Whitney $p$ = 8.6e-5, FDR-adjusted, rank-biserial $r$ = -0.17). The volume-weighted gap (5 points) does not survive permutation ($p$ = 0.082).

**Cross-pool comparison.** BCT (PQD 0.679), NCT (0.601), CHAR (0.221) form a descriptive gradient. The BCT--NCT comparison is observational only: 88.6% token overlap, 19 shared wallets, NCT designed post-BCT, cluster-robust $p$ = 0.24. No independent control pool operated during BCT's lifetime.

