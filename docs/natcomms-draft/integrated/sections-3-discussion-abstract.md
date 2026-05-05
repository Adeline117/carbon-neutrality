# Discussion and Abstract

**Paper**: "On-chain forensics reveal adverse selection in the first tokenized carbon market"

---

## Discussion

### The wrong credits, the wrong narrative

The informal narrative around BCT's collapse^16,17,18^ attributes it to REDD+ credits with contested baselines --- a plausible frame given the broader academic evidence of REDD+ overcrediting^2,4^ but one that was never verified against BCT's on-chain composition. Our forensic reconstruction reveals a different picture: the pool was 69.1% renewable energy credits --- CDM-era projects with near-zero additionality --- while a small number of type-specialist wallets extracted the credits that off-chain markets still valued. The misattribution likely arose because REDD+ quality problems are visible and controversial, while the additionality failure of CDM-era renewables is structurally invisible: the wind farms exist, the electricity is real, but grid-connected wind in China was already economically competitive by 2010. Quality infrastructure must address additionality with the same rigour currently applied to baseline accuracy.

### 9.6 million tonnes stranded

The 98.8% stranding rate for B-grade credits is the starkest outcome: nearly 10 million tonnes of nominally valid carbon offsets are functionally worthless, already retired on Verra's registry but trapped in a pool no one will pay to redeem from. Using literature additionality rates^2,24^ and the social cost of carbon, we estimate the welfare gap at approximately \$100--250 million relative to a counterfactual market-average pool (Monte Carlo median \$146M, 90% CI \$68M--\$252M). This is an illustrative order-of-magnitude estimate conditional on both the additionality assumptions and the counterfactual composition.

A reasonable objection is whether BCT's outcome is worse than the counterfactual of no tokenization. Without BCT, these CDM-era renewable credits would have remained in Verra registries, occasionally purchased at \$0.50--1.00 by companies seeking inexpensive offsets to claim carbon neutrality. In that scenario, the credits circulate and generate false confidence in emission reductions that likely never occurred. BCT inadvertently removed 9.6 million tonnes of low-quality credits from active circulation --- a permanent illiquidity event that no registry-level intervention has achieved. The welfare cost of BCT is therefore not absolute but relative to a counterfactual where the same credits continued to be traded and retired against climate commitments. The pool's failure as a market may paradoxically have been a success as an inadvertent quality filter.

### Identification and limits

The 1.87$\times$ base-rate over-selection ($p$ < 0.0001, wallet-clustered) is the paper's strongest test, requiring no external control. The over-selection reflects a joint product of architectural incentives (uniform pricing under voluntary participation) and supply-side factors (holders of CDM-era renewables had large inventories and low opportunity costs); we characterise this as design-enabled rather than design-determined. The 93.5% bridge pass-through confirms that selection operated at the bridge level, not through pool-level cherry-picking.

The Granger causality ($n$ = 55 weeks, VAR(2) selected by AIC) is suggestive of lead-lag dynamics but underpowered and potentially overfitted (10 parameters on 55 observations). The first-differenced daily regression ($n$ = 330, $\beta$ = $-$1.8, $p$ < 0.001) tests a different hypothesis --- contemporaneous co-movement rather than temporal precedence --- but provides stronger evidence on a larger sample that quality and price are linked, and this feedback is BCT-specific ($R^2$ = 0.04 vs. ETH). The within-token comparison of the 14 tokens deposited into both BCT and NCT provides the strongest identification: the same credits were 100% redeemed from BCT versus 28.5% from NCT, with ARR tokens showing the most extreme contrast (100% vs. 0%). This within-token design controls for credit quality and isolates the pool-design effect, though BCT and NCT still differ in timing and participant population.

### Cross-domain evidence

Curve Finance's stETH/ETH stableswap pool provides independent cross-domain evidence from an unrelated DeFi market on Ethereum. Curve's stableswap treats stETH (Lido's liquid staking derivative) and ETH as near-equivalent --- a uniform-pricing mechanism analogous to BCT's 1:1 credit tokenization. The Terra/LUNA collapse (May 7--12, 2022) triggered an exogenous quality shock as cascading liquidations (Celsius, Three Arrows Capital) raised stETH counterparty risk. On-chain data reveals a composition shift matching the adverse-selection prediction:

- **May 2**: stETH net +64,939 (low-quality flooding in), ETH net $-$93,270 (high-quality extracted). Composition shift: 158,209 ETH-equivalent --- **40$\times$ the pre-depeg baseline** of $\pm$4,000 ETH/week.
- **May 9** (Terra crash): Both assets drain, but ETH drains 74,087 more than stETH.
- **May 16**: stETH floods back 27$\times$ faster than ETH. Composition shift: 148,573.

Over three weeks, the pool shifted by 380,869 ETH-equivalent toward the low-quality asset (approximately \$762M at contemporaneous prices). The structural parallel to BCT is precise: near-uniform pricing of quality-heterogeneous assets produced selective extraction of the high-quality component. Two disanalogies warrant note: Curve's stableswap is partially quality-actionable (effective prices deviate from 1:1 as composition shifts, unlike BCT's strict uniform pricing), and the acute episode is also consistent with a classical bank-run interpretation. Together they demonstrate that the pattern is not specific to carbon markets, though the evidence base remains limited to two independent cases.

### Recovery requires quality infrastructure

Once a pool reaches a low-type equilibrium, recovery requires discontinuous intervention --- quality gating or quality-differentiated pricing --- not marginal improvement. The quality-volume frontier (Extended Data Fig. 3) reveals the tradeoff: a BBB gate ($\geq$45) achieves PQD 0.503 but retains only 8.7% of tokens. Critically, quality gating must operate on both margins. BCT's dual-margin forensics show that the exit side --- where concentrated, sophisticated actors conducted programmatic type-targeted extraction --- was at least as damaging as the entry side. Effective pool design must either apply quality-differentiated redemption pricing or maintain net-composition quality floors that restrict redemptions pushing the pool below a threshold.

The need for quality infrastructure extends beyond tokenized markets. Six major carbon market governance frameworks --- the ICVCM Core Carbon Principles, the Paris Agreement Article 6.4 mechanism, CORSIA, the Singapore International Carbon Credit Framework, the EU Carbon Removal Certification Framework, and the VCMI Claims Code --- all require the same integrity criteria (additionality, permanence, quantification, safeguards), yet none provides continuous quality scoring, uncertainty quantification, or automated enforcement. Singapore's 2025 mandate for commercial carbon credit ratings^15^ represents the first sovereign move from voluntary to mandatory quality differentiation. Detailed regulatory mapping of our framework's dimensions to all six frameworks is provided in Supplementary Note 1.

### Economic magnitude

The adverse selection costs are substantial. At BCT's 2022 peak, the implied mispricing --- conservatively \$3.30 per credit, or \$64--122 million in aggregate --- represents value transferred from buyers who assumed average quality to depositors of below-average credits. More broadly, applying MSCI's 4:1 quality price ratio to 2025 retirement volumes (~160 million tCO$_2$e at ~\$1 billion total value) suggests that quality-tiered pricing could unlock \$76--278 million per year in additional price discovery value. The cost of on-chain quality gating infrastructure is negligible: quality checks cost approximately 19,000 gas per call (~\$0.003--0.005 at current L2 fee levels), implying a benefit-cost ratio exceeding 100:1 (Supplementary Information). These are partial-equilibrium projections; market participants would adapt their behaviour under quality gating.

### Limitations

Several limitations warrant acknowledgment. First, the quality scores are author-derived. Although validated against CCP labels ($d$ = 1.87), commercial ratings ($\rho$ = +0.901, $n$ = 27), and an LLM panel ($\kappa$ = 0.6; see Methods), the rubric reflects a single group's judgment. A multi-provider replication (GPT-5, Gemini 2.5 Pro, Llama 4 Maverick, $n$ = 5) yields cross-provider $\kappa$ = 0.647, partially addressing single-family bias concerns. A structured expert elicitation via Best-Worst Scaling with 20 identified domain experts remains a planned next step. The PQD metric embeds normative assumptions (Oxford hierarchy, specific weights); all rubrics are published for re-weighting.

Second, the cross-pool comparison (BCT, NCT, CHAR) is observational. BCT and NCT share 88.6% of tokens and 19 depositor wallets; cluster-robust inference renders the naive correlation difference non-significant ($p$ = 0.24 vs. naive $p$ = 2.3 $\times$ 10$^{-7}$). No independent control pool operated during BCT's lifetime.

Third, the temporal decline ($\rho$ = -0.24) is driven by the vintage-year component of the composite. A vintage-free robustness check reverses the sign ($\rho$ = +0.24), indicating vintage-composition drift rather than within-vintage quality deterioration.

Fourth, the BeZero BCT validation covers only 7 projects ($p$ = 0.073, not significant at $\alpha$ = 0.05). BCT composition relies on Verra registry metadata without independent verification, though the 69.1% renewable dominance is robust to misclassification.

Fifth, the bridge decomposition (93.5% pass-through by token count) establishes that entry-side selection is primarily architectural. The pass-through rate is by unique token count rather than tonnage and should be interpreted as a lower bound on bridge-level dominance.

Sixth, additionality remains the weakest scoring dimension across all raters ($\kappa$ = 0.243), reflecting the fundamental difficulty of assessing counterfactual baselines from documentary evidence. The framework rates credits on public documentation only, which may miss proprietary information available to commercial agencies.

---

## Abstract

The world's largest tokenized carbon credit pool collapsed because of renewable energy credits with near-zero additionality (69.1% of pool content), not REDD+ credits (4.2%) as widely claimed. Analysing all 1,187 deposits, 35,432 redemptions, and 28,897 unique wallets in Toucan's BCT pool on Polygon (22 million tonnes) using an open quality framework validated against the ICVCM Core Carbon Principles label (Cohen's $d$ = 1.87, $n$ = 318) and commercial ratings (Spearman $\rho$ = +0.901 with BeZero, $n$ = 27), we reconstruct the first complete on-chain forensics of a tokenized market collapse. Renewables were selected at 1.87$\times$ the VCS registry base rate ($p$ < 0.0001); 93.5% of all bridged tokens entered BCT directly, indicating design-enabled rather than strategic selection. Two nearly disjoint wallet populations (1.4% overlap) operated on opposite margins: 509 depositors fed the pool with what the bridge produced, while type-specialist extractors --- 15 of the 20 largest redeemers never deposited --- removed the credits off-chain markets still valued. Five wallets extracted 1.55 million tonnes of high-demand credits; 9.6 million tonnes of B-grade renewables remain stranded on-chain. The pool's uniform pricing of quality-heterogeneous assets under voluntary participation was sufficient to produce this outcome despite full quality transparency. A within-token cross-pool comparison confirms that design drives outcome: the same 14 nature-based tokens were 100% redeemed from BCT but only 28.5% from quality-gated NCT. A 34-segment quality atlas reveals a 10-fold quality range across the voluntary carbon market (PQD 0.076--0.759), demonstrating that quality-actionable mechanism design is a precondition for tokenized market viability.
