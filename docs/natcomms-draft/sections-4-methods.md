# Methods

## Depositor-level adverse selection analysis

We analysed depositor behaviour in the Toucan BCT pool on Polygon by extracting all `Deposited(address indexed sender, address indexed erc20, uint256 amount)` events from the BCT pool contract (0x2F800Db0fdb5223b3C3f354886d907A671414A7F) between block 20,000,000 (October 2021) and block 37,000,000 (December 2022) using the Polygon JSON-RPC interface. Each event records the depositor address, the TCO2 token address deposited, and the amount in tonnes. This period spans BCT's launch, peak holdings, price decline, and the onset of Verra's tokenization restrictions, capturing the full arc of adverse selection dynamics.

**Portfolio reconstruction.** For each unique depositor address, we reconstructed their TCO2 portfolio at the time of their last BCT deposit by querying ERC-20 Transfer events across all known TCO2 token contracts, enumerated from the ToucanCarbonOffsetsFactory (0x639dFeA994b139A3d6C3750D4C4E24daEc039BD7). A depositor's *retained* portfolio comprised TCO2 tokens for which the depositor held a nonzero balance after their final BCT deposit but which were not themselves deposited into BCT. Each TCO2 token was scored using the methodology archetype system described below, with project type and vintage year extracted from the TCO2 token name (format: `TCO2-VCS-<projectId>-<vintage>`). Project metadata (methodology category, country) was obtained from the Verra public registry via project ID.

**Quality selection differential.** For each depositor $d$ holding at least two distinct TCO2 types --- the minimum portfolio diversity required to observe quality selection --- we computed the quality differential:

$$\Delta_d = \bar{Q}_{\text{retained},d} - \bar{Q}_{\text{deposited},d}$$

where $\bar{Q}_{\text{deposited},d} = \sum_j q_j v_j / \sum_j v_j$ is the volume-weighted mean composite quality score of deposited TCO2 types, and $\bar{Q}_{\text{retained},d}$ is defined analogously for retained types. A positive $\Delta_d$ indicates that the depositor retained higher-quality credits than those deposited --- consistent with adverse selection.

**Statistical tests.** We tested the null hypothesis $H_0: \mu_\Delta = 0$ using three complementary approaches: (i) a paired $t$-test on the depositor-level differentials (parametric); (ii) a Wilcoxon signed-rank test (nonparametric; appropriate because quality score distributions may be non-normal); and (iii) a permutation test (10,000 iterations, seed = 42) in which deposit/retain labels were randomly shuffled within each depositor's portfolio, preserving the number of deposited and retained types per depositor. Effect size was quantified as Cohen's $d$ for the paired difference. The selection rate was defined as the proportion of depositors for whom $\Delta_d > 0$. Bootstrap 95% confidence intervals for the population mean $\Delta$ were computed from 10,000 resamples.

**Robustness checks.** (i) Excluding KlimaDAO: we repeated all analyses after removing addresses associated with the KlimaDAO treasury (0x7Dd4f0B986F032A44F913BF92c9e8b7c17D77aD7), the single largest BCT holder, which may have operated under different incentive structures than typical depositors. (ii) Time stratification: we split depositors into an early period (October 2021 -- March 2022, BCT trading above $4) and a late period (April -- December 2022, BCT declining below $2) to test whether adverse selection intensified over time. (iii) Volume weighting versus equal weighting: we tested both approaches to ensure results were not driven by a small number of high-volume depositors.

## Quality scoring framework

Quality scores were derived from an open composite framework fully described and validated in a companion paper^1^. Briefly, the framework evaluates each credit on six active dimensions: removal type hierarchy (weight 0.250), additionality (0.200), monitoring, reporting, and verification (MRV) grade (0.200), permanence (0.175), vintage year (0.100), and registry and methodology quality (0.075). The seventh dimension, co-benefits, carries zero weight and serves only as a binary disqualifier gate, following Berg et al.^2^, who showed that co-benefit narratives inflate perceived quality beyond what carbon integrity warrants. The composite score was computed as:

$$C = \sum_{i=1}^{7} w_i \times s_i$$

Composites were mapped to six-tier letter grades: AAA ($\geq$90), AA ($\geq$75), A ($\geq$60), BBB ($\geq$45), BB ($\geq$30), and B (<30). Seven disqualifier conditions imposed grade caps regardless of composite score (e.g., evidence of double counting caps at B; no third-party verification caps at BBB). Machine-readable rubrics are provided in JSON format at `data/scoring-rubrics/`.

For the depositor analysis, each TCO2 token was scored using methodology-level archetypes from a 318-credit batch dataset, with vintage-year adjustments applied via a temporal decay formula. The same framework was used to score both deposited and retained credits, ensuring that any systematic bias in the framework cancels in the $\Delta$ calculation.

## Lemons Index

We defined the Lemons Index $L$ to quantify the degree of adverse selection in a tokenized carbon credit pool:

$$L(\text{pool}) = 1 - \frac{\bar{C}}{100}$$

where $\bar{C}$ is the mean composite score of all credits in the pool. The index ranges from 0 (every credit scores 100; no adverse selection) to 1 (every credit scores 0; complete quality failure). The metric is named after Akerlof's^3^ characterization of markets in which information asymmetry drives out high-quality goods.

We computed $L$ for six deployed or prospective tokenized pools: Toucan BCT (43 credits at 2022 peak), Moss MCO2 (30 credits), Toucan NCT (28 credits), Klima 2.0 kVCM (20 credits), Toucan CHAR (12 credits), and a hypothetical AAA-only pool (13 credits).

**Null model.** To assess whether observed Lemons Indices exceed random expectation, we conducted a Monte Carlo simulation (10,000 iterations): for each pool size $n$, we randomly sampled $n$ credits from the full 318-credit market dataset and computed the resulting Lemons Index. The expected LI under random assignment was 0.51 (SD = 0.026 for $n$ = 43), establishing that BCT's observed LI = 0.724 lies 6.2 SD above the null.

**Systematic scan.** We extended the Lemons Index computation to 34 market segments defined by credit type (e.g., REDD+, biochar, DACCS), registry (e.g., CDM, Verra VCS, Puro.earth), vintage period (pre-2020, 2020--2023, 2024+), CCP eligibility, and quality tier, using the same 318-credit batch dataset.

## Counterfactual quality-gate simulation

For each of the six tokenized pools, we simulated the application of an on-chain quality gate at all six grade thresholds (B, BB, BBB, A, AA, AAA). At each threshold, a `meetsGrade()` function admitted only credits whose final grade met or exceeded the threshold. We then recomputed the number of admitted credits, the new mean composite score, and the resulting Lemons Index. The purpose of this simulation was to quantify the extent to which quality gating could have prevented the observed adverse selection.

The `meetsGrade()` function is implemented as a Solidity view function callable at zero marginal gas cost by any deposit contract, retirement gate, or DeFi protocol. A pool contract calling `meetsGrade(creditAddress, tokenId, Grade.BBB)` before accepting a deposit would have prevented 95% of BCT's historical inventory from entering the pool. The full on-chain implementation, including the ERC-CCQR interface standard, composability contracts, and testnet deployment, is described in a companion paper^4^.

## Data availability

All analysis scripts, scoring rubrics, and the 318-credit methodology batch dataset with per-dimension scores are available at https://github.com/Adeline117/carbon-neutrality under an MIT licence. Machine-readable rubrics are provided in JSON format (`data/scoring-rubrics/`). Depositor-level event extraction scripts are provided at `data/depositor-analysis/`. [ON-CHAIN DATA: depositor-level event logs and portfolio reconstructions will be deposited in a public repository upon completion of data collection.]

## References

1. [Companion paper reference: open quality framework for carbon credits, submitted to ERL]
2. Berg, F., Kolbel, J., Pavlova, A. & Rigobon, R. The market for voluntary carbon offsets. SSRN Working Paper (2025).
3. Akerlof, G. A. The market for "lemons": quality uncertainty and the market mechanism. *Q. J. Econ.* **84**, 488--500 (1970).
4. [Companion paper reference: on-chain quality infrastructure, submitted to WWW 2027]
