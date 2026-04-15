# Gas Benchmarks for CarbonCreditRating

## Why Gas Benchmarks Matter for a Quality-Gating Primitive

The CarbonCreditRating contract is designed to be composed inline with DeFi
operations -- a Uniswap pool hook, an ERC-20 transfer check, or a collateral
eligibility gate. Unlike an oracle that is read once and cached, a quality gate
is called on every qualifying transaction. If the gas overhead is too high, it
either prices out small-value carbon retirements or forces integrators to adopt
unsafe caching patterns that introduce staleness windows.

The benchmarks in `GasBenchmark.t.sol` quantify:

1. **Write costs** -- how expensive it is for a rater to publish or update a
   rating. These are amortized over the lifetime of the rating and paid by the
   rating oracle, not by end users.
2. **Read costs** -- how expensive the `meetsGrade()`, `ratingOf()`, and
   `isStale()` view calls are. These are paid by every DeFi transaction that
   gates on credit quality.
3. **Pure computation costs** -- the gas overhead of the composite scoring
   arithmetic in isolation, relevant for off-chain simulation and gas
   estimation.
4. **Scalability** -- confirmation that read costs are O(1) regardless of how
   many ratings exist in the contract (mapping-based storage).

## What the Expected Gas Costs Mean for DeFi Composability

### Write path (`setRating`)

| Operation                     | Expected gas  | Notes                                  |
|-------------------------------|---------------|----------------------------------------|
| First write (cold storage)    | ~120k-160k    | 7 dimension scores + 7 stds + 7 flags + metadata in fresh slots |
| Update (warm storage)         | ~40k-70k      | SSTORE from nonzero to nonzero is 5k vs 20k for cold |

Write costs are paid by the rating oracle (the authorized rater address). They
are a one-time cost per credit per re-assessment cycle (typically annual). At
$0.01/gwei and 30 gwei base fee, a cold write costs roughly $0.04-$0.05 -- well
within the economic margin of a credit worth $5-$150.

### Read path (`meetsGrade`, `ratingOf`, `isStale`)

| Operation                     | Expected gas | Notes                                   |
|-------------------------------|--------------|-----------------------------------------|
| `meetsGrade()` (fresh)        | ~6k-10k      | One SLOAD (mapping read) + enum compare |
| `meetsGrade()` (stale, early exit) | ~5k-8k | Same SLOAD, exits before grade compare  |
| `meetsGrade()` (unrated, early exit) | ~3k-5k | SLOAD returns zero, immediate false   |
| `ratingOf()` (full struct)    | ~6k-10k      | Full struct copy to memory              |
| `isStale()` (fresh)           | ~5k-8k       | SLOAD + timestamp compare               |

### Pure computation

| Operation                     | Expected gas | Notes                                   |
|-------------------------------|--------------|-----------------------------------------|
| `computeComposite()`          | ~1k-2k       | 7 multiplications + 6 additions         |
| `computeCompositeVariance()`  | ~1k-3k       | 7 squared terms                          |
| `gradeFromComposite()`        | ~200-500     | 5 comparisons (worst case)               |
| `applyDisqualifiers()` (0 flags) | ~200-400  | 7 bool checks, no capping               |
| `applyDisqualifiers()` (7 flags) | ~400-700  | 7 bool checks + 7 cap operations        |

## Comparison Framework: Quality Gate vs Typical DeFi Operations

To understand whether the quality-gating overhead is acceptable, compare
`meetsGrade()` against the baseline cost of common operations:

| Operation                     | Typical gas  | Source                                  |
|-------------------------------|--------------|-----------------------------------------|
| ERC-20 `transfer()`          | ~45k-65k     | OpenZeppelin ERC-20                      |
| Uniswap V3 single-hop swap   | ~130k-185k   | Uniswap V3 Router                       |
| Uniswap V2 swap              | ~100k-150k   | Uniswap V2 Router                       |
| Aave V3 `supply()`           | ~180k-250k   | Aave V3 Pool                            |
| `meetsGrade()` quality gate   | ~6k-10k      | CarbonCreditRating                      |

**Key takeaways:**

- A `meetsGrade()` check adds roughly **5-15%** to an ERC-20 transfer.
- It adds roughly **3-7%** to a Uniswap V3 swap.
- It adds roughly **2-5%** to an Aave supply operation.
- For a carbon retirement transaction (which typically involves a swap + burn),
  the quality gate is a **negligible** fraction of total gas.

These margins confirm that inline quality gating is economically viable. There
is no need for off-chain caching or commit-reveal patterns that would weaken
the freshness guarantee.

## How to Run

### Full gas report

```bash
forge test --match-contract GasBenchmarkTest --gas-report
```

### Individual test (to isolate a specific operation)

```bash
forge test --match-test test_gas_setRating_coldStorage_firstWrite -vvvv
```

The `-vvvv` verbosity level shows the full EVM trace, including per-opcode gas
costs, which is useful for identifying optimization opportunities.

### Scalability tests only

```bash
forge test --match-test "test_gas_meetsGrade_after" --gas-report
```

These three tests (100, 500, 1000 pre-existing ratings) should all show the same
`meetsGrade` gas cost, confirming O(1) lookup.

### Comparing across contract versions

To track gas regressions across methodology versions, save the output:

```bash
forge test --match-contract GasBenchmarkTest --gas-report > data/gas-benchmarks/report-v0.5.txt
```

Then diff against the previous version's report to catch any storage layout
changes or new computation that increases read-path costs.

### Snapshot for CI

```bash
forge snapshot --match-contract GasBenchmarkTest
```

This writes a `.gas-snapshot` file that can be committed and diffed in CI to
catch gas regressions automatically.
