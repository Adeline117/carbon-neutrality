# Depositor-Level Adverse Selection Analysis: Methodology

## Objective

Test whether adverse selection actually occurred at the individual depositor level
in Toucan's Base Carbon Tonne (BCT) pool on Polygon. Specifically: did depositors
who held multiple carbon credit types selectively deposit their lowest-quality
credits into BCT while retaining higher-quality ones?

This analysis elevates the paper's contribution from "we measured pool quality" to
"we found evidence that depositors strategically selected against the pool" ---
the precise mechanism Akerlof's (1970) theory predicts.

## Hypothesis

**H1 (Adverse Selection):** Among depositors who held multiple TCO2 token types at
the time of their BCT deposit, the mean quality score of *deposited* credits is
significantly lower than the mean quality score of *retained* credits.

**H0 (No Selection):** Deposited and retained credits have equal mean quality
(depositors deposit randomly from their holdings).

## Key Contracts

| Contract | Address (Polygon) | Purpose |
|----------|-------------------|---------|
| BCT Pool | `0x2F800Db0fdb5223b3C3f354886d907A671414A7F` | Base Carbon Tonne pool; receives TCO2 deposits |
| NCT Pool | `0xD838290e877E0188a4A44700463419ED96c16107` | Nature Carbon Tonne pool (comparison) |
| TCO2 Factory | `0x639dFeA994b139A3d6C3750D4C4E24daEc039BD7` | Deploys per-project-vintage TCO2 ERC-20 tokens |
| Carbon Offset Batches | `0x8a4D7458dDe3023A3b24225D62087701a88B09Dd` | NFTs representing bridged credit batches |
| Contract Registry | Discoverable via BCT.contractRegistry() | Central directory of all Toucan contracts |

## Toucan Architecture Overview

1. **Bridging:** A credit holder retires Verra VCUs in the off-chain registry and
   bridges them via the Toucan Carbon Bridge. Each batch becomes a CarbonOffsetBatch
   NFT, which is then fractionalized into fungible TCO2 ERC-20 tokens.

2. **TCO2 tokens:** Each unique (project, vintage) pair has its own ERC-20 contract.
   A TCO2 token for "VCS-934 vintage 2016" is a different ERC-20 from "VCS-934
   vintage 2017". The token name encodes the project ID and vintage.

3. **Pool deposit:** Holders call `deposit(address tco2, uint256 amount)` (or
   the newer `deposit(address tco2, uint256 amount, uint256 maxFee)`) on the BCT
   pool contract. The pool verifies eligibility via `checkEligible(tco2)`, transfers
   TCO2 from the depositor, and mints BCT 1:1.

4. **Events emitted:** The pool emits a `Deposited(address indexed sender,
   address indexed erc20, uint256 amount)` event on each deposit. This is the
   primary data source.

## Data Collection Pipeline

### Step 1: Extract BCT Deposit Events

Query all `Deposited` events from the BCT pool contract on Polygon from
deployment (block ~20000000, Oct 2021) through end-2022 (the peak adverse
selection period).

**Event signature:**
```
event Deposited(address indexed sender, address indexed erc20, uint256 amount);
```

**Topic0 (keccak256 hash):**
```
keccak256("Deposited(address,address,uint256)")
= 0x2d3caabd9... (computed at runtime)
```

**Data source options (ranked by reliability):**
1. Direct RPC via Polygon public endpoint + web3.py `eth.get_logs()`
2. PolygonScan Event Log API (rate-limited to 10k results per call)
3. Dune Analytics SQL (Toucan tables are indexed: `polygon.logs`)
4. Subgraph: Toucan maintains a subgraph at `api.thegraph.com`

### Step 2: Identify Unique Depositor Addresses

Group deposit events by `sender` address. Each unique sender is a depositor.
Expected population: ~500--2,000 unique depositor addresses during 2021--2022.

### Step 3: Snapshot Depositor TCO2 Holdings at Deposit Time

For each depositor, at the block of their deposit transaction:
- Query the ERC-20 balance of every known TCO2 token for that address
- TCO2 token addresses are enumerable from the TCO2 Factory's deployment events
- A depositor "retained" a TCO2 if they held a nonzero balance *after* the
  deposit transaction but did *not* deposit it into BCT in that transaction

**Practical approach:** Rather than querying balances at every historical block
(expensive), we use Transfer events:
1. Get all TCO2 Transfer events where `to == depositor_address` (incoming)
2. Get all TCO2 Transfer events where `from == depositor_address` (outgoing)
3. Reconstruct the depositor's TCO2 portfolio at the block of each deposit

### Step 4: Map TCO2 Tokens to Quality Scores

Each TCO2 token name encodes the Verra project ID and vintage year. Parse these
to extract:
- `methodology_category` (from Verra project ID -> methodology mapping)
- `vintage_year` (from token name)
- `country` (from Verra project metadata)

Score each TCO2 using the methodology archetype scoring system (same framework
used for pool-level Lemons Index computation).

### Step 5: Compute Per-Depositor Selection Differential

For each depositor $d$ with at least 2 distinct TCO2 types:

$$\Delta_d = \bar{Q}_{\text{retained},d} - \bar{Q}_{\text{deposited},d}$$

where $\bar{Q}_{\text{deposited},d}$ is the volume-weighted mean composite score
of TCO2 types deposited into BCT, and $\bar{Q}_{\text{retained},d}$ is the
volume-weighted mean composite score of TCO2 types held but not deposited.

**Adverse selection indicator:** $\Delta_d > 0$ (retained credits are higher
quality than deposited credits).

### Step 6: Statistical Tests

1. **Wilcoxon signed-rank test** on depositor-level $\Delta_d$ values (paired,
   nonparametric; appropriate because quality score distributions may be
   non-normal).

2. **Paired t-test** on $(\bar{Q}_{\text{retained}}, \bar{Q}_{\text{deposited}})$
   pairs (parametric complement).

3. **Bootstrap confidence interval** for the population mean $\Delta$
   (10,000 resamples).

4. **Effect size:** Cohen's $d$ for the paired difference, plus the proportion
   of depositors for whom $\Delta_d > 0$ (selection rate).

### Step 7: Robustness Checks

- **Exclude KlimaDAO treasury:** KlimaDAO (largest holder, ~8M+ BCT) may have
  different incentives. Re-run excluding known KlimaDAO-associated addresses.
- **Time stratification:** Split into early period (Oct 2021--Mar 2022, high BCT
  price) vs. late period (Apr--Dec 2022, declining price). Adverse selection
  should strengthen as prices decline.
- **Volume weighting vs. equal weighting:** Test both approaches.
- **Depositor size:** Stratify by total deposit volume (large vs. small depositors).

## Null Model

Under the null hypothesis (random deposit), the expected $\Delta = 0$. We also
construct a permutation null: for each depositor, randomly reassign which of their
TCO2 types are "deposited" vs. "retained" (preserving the number of each), and
recompute $\Delta$. Repeat 10,000 times to build the null distribution.

## Relation to Existing Literature

### CarbonPlan "Zombies on the blockchain" (2022)
CarbonPlan identified "zombie" projects --- long-dormant credits that were newly
issued specifically to sell into BCT. This is *supply-side* adverse selection:
projects that had no buyers in the traditional market found a buyer in BCT.
Our analysis tests the complementary *depositor-side* mechanism: among entities
that held multiple credit types, did they selectively deposit their worst?

### Manshadi et al. (2023) theoretical model
Formalized quality-blind pooling as producing a separating equilibrium where
high-integrity credits are excluded. Our depositor-level analysis provides the
first empirical test of their prediction at the individual agent level.

### Frontiers in Blockchain KlimaDAO study (2024)
Analyzed KlimaDAO's market capitalization and staking dynamics but did not examine
depositor-level quality selection. Our analysis fills this gap.

## Expected Findings

Based on the pool-level evidence (BCT LI = 0.724, zero A+ credits), we expect:
- **Selection rate > 50%:** More than half of multi-TCO2 depositors deposited
  lower-quality credits than they retained.
- **Mean $\Delta > 0$:** Population-level evidence of adverse selection.
- **Effect size moderate to large:** Cohen's $d$ > 0.5 on the paired difference.
- **Time-varying selection:** Stronger adverse selection in the later period
  as sophisticated actors learned to exploit the pool.

## Limitations

1. **Portfolio completeness:** We observe on-chain TCO2 holdings only. Depositors
   may hold credits off-chain (in Verra accounts) that we cannot observe. This
   biases *against* finding adverse selection (we undercount retained credits).

2. **Intermediary wallets:** Some deposits may come through intermediary contracts
   or aggregator services, obscuring the true depositor's portfolio.

3. **Scoring uncertainty:** TCO2-to-quality mapping uses archetype scores, not
   per-project expert assessment. However, the same scoring framework is used for
   both deposited and retained credits, so any systematic bias cancels in the
   $\Delta$ calculation.

4. **Causal inference:** Observing $\Delta > 0$ is consistent with adverse selection
   but does not rule out alternative explanations (e.g., depositors may prefer to
   deposit older credits because they are less useful for future compliance
   obligations, not because of quality arbitrage).

## Data Requirements Summary

| Data | Source | Volume |
|------|--------|--------|
| BCT Deposited events | Polygon RPC / PolygonScan API | ~5,000--15,000 events |
| TCO2 Transfer events (all tokens) | Polygon RPC / subgraph | ~50,000--200,000 events |
| TCO2 token -> project ID mapping | TCO2 token name parsing + Verra API | ~200--400 TCO2 contracts |
| Verra project metadata | Verra public registry | ~200--400 projects |
| Quality scores per methodology | Our framework (archetypes.json) | 17 methodology categories |
