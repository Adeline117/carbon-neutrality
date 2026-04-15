# Draft Paragraph for Nature Communications Results Section

## Placement

This subsection should be inserted after the existing pool-level results
(after the paragraph ending "...cannot be determined from pool composition
data alone") and before "A seven-dimension quality framework recovers the
ICVCM quality threshold". It replaces the hedged sentence with direct
depositor-level evidence.

## Suggested subsection heading

### Depositor-level evidence of strategic quality selection

## Draft text (with placeholders for real data)

To distinguish strategic adverse selection from passive quality degradation,
we analysed individual depositor behaviour in the BCT pool by reconstructing
on-chain portfolios for all addresses that deposited TCO2 tokens between
October 2021 and December 2022. Using the `Deposited(address, address,
uint256)` events emitted by the BCT pool contract
(0x2F800Db...A7F on Polygon), we identified [N_DEPOSITORS] unique depositor
addresses that collectively deposited [TOTAL_TONNES] tonnes of tokenized
carbon credits across [N_TCO2_TYPES] distinct TCO2 token types. For each
depositor who held at least two TCO2 types at the time of deposit, we
computed the quality differential $\Delta_d = \bar{Q}_{\text{retained},d}
- \bar{Q}_{\text{deposited},d}$, where $\bar{Q}_{\text{deposited}}$ and
$\bar{Q}_{\text{retained}}$ are the volume-weighted mean composite quality
scores of the TCO2 tokens deposited into BCT and retained in the
depositor's wallet, respectively (see Methods).

Of [N_ANALYZED] depositors with multi-type portfolios, [SELECTION_RATE]%
deposited credits with lower mean quality than those they retained
($\Delta > 0$). The population-level mean differential was $\Delta$ =
[MEAN_DELTA] quality points (95% bootstrap CI: [CI_LO, CI_HI]; Wilcoxon
signed-rank $z$ = [Z_WILCOXON], $p$ [P_WILCOXON]; paired $t$ = [T_STAT],
$p$ [P_T]; Cohen's $d$ = [COHENS_D]). A permutation test in which
deposit/retain labels were randomly shuffled within each depositor's
portfolio confirmed that the observed differential exceeds what would arise
under random deposit behaviour ($p$ [P_PERM]). Excluding KlimaDAO treasury
addresses --- which held approximately 8 million BCT and may have operated
under different incentive structures --- did not materially change the
result ($\Delta$ = [MEAN_DELTA_NO_KLIMA], selection rate =
[SELECTION_RATE_NO_KLIMA]%).

This finding provides direct, individual-level evidence that BCT's quality
degradation was not merely a mechanical consequence of permissive pool
eligibility criteria attracting low-quality supply. Depositors who held
both low-quality and high-quality credits made directional choices:
they routed their lowest-quality credits into the pool while retaining
their best. This is the behavioural signature predicted by Akerlof's
(1970) theory of adverse selection and formalised for carbon credit pools
by Manshadi et al. (2023). CarbonPlan's (2022) finding that dozens of
previously dormant projects resumed issuance specifically to sell into BCT
--- the supply-side mechanism --- is complementary: our analysis identifies
the depositor-side mechanism operating within the pool itself.

---

## Corresponding Methods paragraph

### Depositor-level adverse selection analysis

We analysed depositor behaviour in the Toucan BCT pool on Polygon by
extracting all `Deposited(address indexed sender, address indexed erc20,
uint256 amount)` events from the BCT pool contract
(0x2F800Db0fdb5223b3C3f354886d907A671414A7F) between block 20,000,000
(October 2021) and block 37,000,000 (December 2022) using the Polygon
JSON-RPC interface. Each event records the depositor address, the TCO2
token address deposited, and the amount in tonnes.

For each unique depositor, we reconstructed their TCO2 portfolio at the
time of their last deposit by querying ERC-20 Transfer events across all
known TCO2 token contracts (enumerated from the ToucanCarbonOffsetsFactory
at 0x639dFeA994b139A3d6C3750D4C4E24daEc039BD7). A depositor's *retained*
portfolio comprised TCO2 tokens for which the depositor held a nonzero
balance after their final BCT deposit but which were not themselves
deposited into BCT. Each TCO2 token was scored using the methodology
archetype system described above, with project type and vintage year
extracted from the TCO2 token name (format: `TCO2-VCS-<projectId>-<vintage>`).

For each depositor $d$ holding at least two distinct TCO2 types, we
computed the quality selection differential:

$$\Delta_d = \bar{Q}_{\text{retained},d} - \bar{Q}_{\text{deposited},d}$$

where $\bar{Q}_{\text{deposited},d} = \sum_j q_j v_j / \sum_j v_j$ is the
volume-weighted mean composite score of deposited TCO2 types, and
$\bar{Q}_{\text{retained},d}$ is defined analogously for retained types.
A positive $\Delta_d$ indicates that the depositor retained higher-quality
credits than those deposited --- consistent with adverse selection.

We tested the null hypothesis $H_0: \mu_\Delta = 0$ using three approaches:
(i) a paired $t$-test on the depositor-level differentials; (ii) a Wilcoxon
signed-rank test (nonparametric); and (iii) a permutation test (10,000
iterations, seed = 42) in which deposit/retain labels were randomly
shuffled within each depositor's portfolio. Effect size was quantified as
Cohen's $d$ for the paired difference. The selection rate was defined as
the proportion of depositors for whom $\Delta_d > 0$. Bootstrap 95%
confidence intervals for the population mean $\Delta$ were computed from
10,000 resamples. As a robustness check, we repeated all analyses after
excluding addresses associated with the KlimaDAO treasury
(0x7Dd4f0B986F032A44F913BF92c9e8b7c17D77aD7), which represented the
single largest BCT holder and may have operated under different incentive
structures than typical depositors.

---

## Note on data status

As of the current analysis, the pipeline uses **simulated data** that
encodes a 70% adverse selection rate. The simulation validates that:

1. The statistical pipeline correctly detects the signal
2. All test statistics, CIs, and effect sizes compute correctly
3. The results format integrates with the existing paper structure

To produce publication-ready numbers, the following data collection is needed:

1. **BCT deposit events** (via Polygon RPC, PolygonScan API, or Dune Analytics)
   - Script ready: `fetch_deposits.py`
   - Dune SQL query included in the script
   - Estimated: 5,000--15,000 deposit events

2. **Depositor TCO2 portfolios** (via RPC balance queries or Transfer event reconstruction)
   - Script ready: `fetch_deposits.py --skip-portfolios=false`
   - Most expensive step: ~200,000 RPC calls
   - Alternative: Dune Analytics can reconstruct portfolios from Transfer events

3. **TCO2 metadata** (token name parsing for project ID and vintage)
   - Script ready: `fetch_deposits.py` handles this automatically
   - ~200--400 unique TCO2 token contracts

The Dune Analytics query in `fetch_deposits.py --dune-query-only` can
retrieve the deposit events directly. Portfolio reconstruction can be done
either via the Dune SQL extension query or via RPC balance snapshots.
