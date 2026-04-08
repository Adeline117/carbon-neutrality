# Contracts

Solidity reference implementation of the on-chain carbon credit quality rating framework. This is a **prototype for workshop discussion**, not production code.

## Contents

| File | Purpose |
|------|---------|
| `ICarbonCreditRating.sol` | Interface + shared types (`Grade`, `DimensionScores`, `Disqualifiers`, `Rating`) |
| `CarbonCreditRating.sol` | Reference implementation. Stores per-credit ratings, computes composite scores in basis points, assigns grades, applies disqualifier caps |
| `QualityGatedPool.sol` | Example pool that accepts deposits of an ERC-20-represented credit only if its rating is at or above a minimum grade |
| `test/CarbonCreditRating.t.sol` | Foundry-compatible tests covering composite calculation, grade mapping, disqualifier caps, and the full write-then-read path |

## Design

### Scoring

Each credit is described by 7 `uint8` dimension scores in `[0, 100]`. The composite is computed in basis points:

```
composite_bps = sum(score_i * weight_bps_i) / 100
```

where the weights (sum = 10000) mirror `data/scoring-rubrics/index.json`:

| Dimension | Weight (bps) |
|-----------|------|
| removalType | 2000 |
| additionality | 2000 |
| permanence | 1500 |
| mrvGrade | 1500 |
| vintageYear | 1000 |
| coBenefits | 1000 |
| registryMethodology | 1000 |

### Grading

Composite is mapped to a 6-tier grade enum (`B` < `BB` < `BBB` < `A` < `AA` < `AAA`):

| Grade | Min (bps) |
|-------|-----------|
| AAA   | 9000 |
| AA    | 7500 |
| A     | 6000 |
| BBB   | 4500 |
| BB    | 3000 |
| B     | 0 |

### Disqualifiers

Five flags can **cap** the final grade regardless of composite score. They never raise grades.

| Flag | Cap |
|------|-----|
| `doubleCounting` | B |
| `failedVerification` | B |
| `humanRights` | B |
| `sanctionedRegistry` | BB |
| `noThirdParty` | BBB |

### Access control

- `owner` (set in constructor) manages the rater allowlist.
- Any allowlisted `rater` can call `setRating`. Anyone can read ratings.

**This is deliberately simple.** A production deployment would replace the single-role rater with a decentralized attestation network (e.g., EAS, UMA-style optimistic oracle, or multi-rater majority).

## Running tests

Install Foundry:
```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

From the repo root:
```bash
forge init --no-commit --no-git    # first time only, if not already a Foundry project
forge test --match-path 'contracts/test/*.t.sol' -vv
```

The test file uses only native Solidity assertions (no forge-std imports) so it can be read as documentation even without Foundry installed.

## Known limitations (for paper v0.3 discussion)

1. **Single rater role.** Centralization risk; documented in workshop paper Section 5.2 Option C.
2. **No rating expiry.** Rerating cycle is not enforced.
3. **No provenance.** The attested data (verification reports, satellite imagery, etc.) is not linked on-chain.
4. **ERC-20 only.** Pool logic assumes a fungible ERC-20 credit; ERC-1155 / ERC-721 support (Nori-style NRTs) is not yet implemented.
5. **No proof-of-retirement.** Retirement should decrement pool reserves and emit a canonical retirement event.
