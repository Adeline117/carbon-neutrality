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

| Operation                     | Expected gas  | Measured gas | Notes                                  |
|-------------------------------|---------------|--------------|----------------------------------------|
| First write (cold storage)    | ~120k-160k    | 167,720      | 7 dimension scores + 7 stds + 7 flags + metadata in fresh slots |
| Update (warm storage)         | ~40k-70k      | 30,308 (min) | SSTORE from nonzero to nonzero is 5k vs 20k for cold |
| Batch 16 credits              | --            | 2,777,736    | Average ~174k per credit (includes mock ERC-20 deploys) |

Write costs are paid by the rating oracle (the authorized rater address). They
are a one-time cost per credit per re-assessment cycle (typically annual). At
$0.01/gwei and 30 gwei base fee, a cold write costs roughly $0.04-$0.05 -- well
within the economic margin of a credit worth $5-$150.

### Read path (`meetsGrade`, `ratingOf`, `isStale`)

| Operation                            | Expected gas | Measured gas  | Notes                                   |
|--------------------------------------|--------------|---------------|-----------------------------------------|
| `meetsGrade()` (fresh)               | ~6k-10k      | 19,244        | One SLOAD (mapping read) + enum compare |
| `meetsGrade()` (stale, early exit)   | ~5k-8k       | 19,244 (max)  | Same SLOAD, exits before grade compare  |
| `meetsGrade()` (unrated, early exit) | ~3k-5k       | 18,953 (min)  | SLOAD returns zero, immediate false     |
| `ratingOf()` (full struct)           | ~6k-10k      | 20,823        | Full struct copy to memory              |
| `isStale()` (fresh)                  | ~5k-8k       | 19,057        | SLOAD + timestamp compare               |
| `isStale()` (unrated)               | --           | 7,097 (min)   | Early return false                       |

> **Note on measured vs expected:** Measured gas includes all EVM overhead
> (calldata, function dispatch, memory expansion). The "expected" column from
> earlier versions reflected only the core storage/compute cost. The measured
> values from `forge test --gas-report` (v0.5 contracts, Foundry 2025) are the
> authoritative numbers for integration gas estimation.

### Read path scalability (O(1) confirmation)

| Pre-existing ratings | `meetsGrade()` gas | Delta from 100 |
|---------------------:|-------------------:|---------------:|
| 100                  | ~14.6M (test total)| baseline       |
| 500                  | ~86.6M (test total)| ~0 per call    |
| 1000                 | ~174.8M (test total)| ~0 per call   |

The per-call gas for `meetsGrade()` is constant regardless of the number of
ratings in the contract, confirming O(1) mapping-based lookup.

### Pure computation

| Operation                        | Expected gas | Measured gas | Notes                                   |
|----------------------------------|--------------|-------------|-----------------------------------------|
| `computeComposite()`             | ~1k-2k       | 4,164       | 7 multiplications + 6 additions         |
| `computeCompositeVariance()`     | ~1k-3k       | 6,651       | 7 squared terms                          |
| `gradeFromComposite()`           | ~200-500     | 522-638     | 5 comparisons (worst case)               |
| `applyDisqualifiers()` (0 flags) | ~200-400     | 2,081       | 7 bool checks, no capping               |
| `applyDisqualifiers()` (1 flag)  | --           | 2,123       | 1 cap applied                            |
| `applyDisqualifiers()` (3 flags) | --           | 2,253       | 3 caps applied                           |
| `applyDisqualifiers()` (7 flags) | ~400-700     | 2,341       | 7 bool checks + 7 cap operations        |

### EAS Adapter (`relay`)

| Operation                     | Measured gas  | Notes                                   |
|-------------------------------|---------------|-----------------------------------------|
| `relay()` (happy path)        | 250,086 (max) | getAttestation + decode + setRating     |
| `relay()` (reverted)          | ~96,592-97,758| Schema mismatch / untrusted / revoked   |
| `setAttester()`               | 70,068        | Cold storage write for new attester     |

### Deployment costs

| Contract                          | Deployment gas | Size (bytes) |
|-----------------------------------|----------------|--------------|
| `CarbonCreditRating`              | 2,358,119      | 10,737       |
| `CarbonCreditRatingEASAdapter`    | 744,778        | 3,466        |
| `QualityGatedPool`                | 907,564        | 4,813        |
| `MockCarbonCredit`                | 532,661        | 2,972        |

## Comparison Framework: Quality Gate vs Typical DeFi Operations

To understand whether the quality-gating overhead is acceptable, compare
`meetsGrade()` against the baseline cost of common operations:

| Operation                     | Typical gas  | Measured   | Source                                  |
|-------------------------------|--------------|------------|-----------------------------------------|
| ERC-20 `transfer()`          | ~45k-65k     | --         | OpenZeppelin ERC-20                      |
| Uniswap V3 single-hop swap   | ~130k-185k   | --         | Uniswap V3 Router                       |
| Uniswap V2 swap              | ~100k-150k   | --         | Uniswap V2 Router                       |
| Aave V3 `supply()`           | ~180k-250k   | --         | Aave V3 Pool                            |
| `meetsGrade()` quality gate   | ~6k-10k      | ~19k       | CarbonCreditRating (measured via forge)  |
| `QualityGatedPool.deposit()`  | --           | ~57k-162k  | Pool contract (includes meetsGrade)      |

**Key takeaways (updated with measured gas):**

- The measured `meetsGrade()` cost of ~19k includes full EVM calldata and
  function dispatch overhead. Inline integration (where `meetsGrade()` is a
  direct internal call rather than an external call) would save ~2,600 gas
  (the base CALL cost).
- A `meetsGrade()` check adds roughly **30-40%** to an ERC-20 transfer as an
  external call, or **~25%** inline -- still economically viable.
- It adds roughly **10-15%** to a Uniswap V3 swap.
- It adds roughly **8-10%** to an Aave supply operation.
- For a carbon retirement transaction (which typically involves a swap + burn),
  the quality gate is a **small** fraction of total gas.
- The EAS adapter `relay()` path costs ~250k gas, comparable to a complex DeFi
  operation, but this is a write-path cost paid once per rating update.

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
