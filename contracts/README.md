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

where the weights (sum = 10000) mirror `data/scoring-rubrics/index.json` (v0.4):

| Dimension | Weight (bps) |
|-----------|------|
| removalType | 2500 |
| additionality | 2000 |
| permanence | 1750 |
| mrvGrade | 2000 |
| vintageYear | 1000 |
| coBenefits | 0 (safeguards-gate) |
| registryMethodology | 750 |

**v0.4 co-benefits mechanism.** Co-benefits is still attested as an informational dimension but carries zero weight in the composite. Assessors use the co-benefits rubric bands to decide whether to set the new `communityHarm` disqualifier flag, which caps the final grade at BBB. See `docs/methodology-gate-v0.4.md` for the decision rationale.

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

### Disqualifiers (7 in v0.6)

Flags that **cap** the final grade regardless of composite score. They never raise grades.

| Flag | Cap | Notes |
|------|-----|-------|
| `doubleCounting` | B | |
| `failedVerification` | B | |
| `humanRights` | B | |
| `sanctionedRegistry` | BB | |
| `noThirdParty` | BBB | |
| `communityHarm` | BBB | v0.4 safeguards-gate |
| `biodiversityHarm` | BBB | v0.6; Zeng et al. 2026 |

### Freshness and provenance (v0.4+)

The `Rating` struct carries three new fields:

- `expiresAt` (uint64) — unix timestamp after which the rating is considered stale. A value of `0` means "never expires". `setRating` rejects any non-zero value that is not strictly in the future.
- `methodologyVersion` (uint16) — stamped from `CURRENT_METHODOLOGY_VERSION` (v0.6 = `0x0500`) at write time. A rating written under an older methodology version is automatically stale even if its `expiresAt` has not elapsed. This is the grandfathering mechanism: bumping the contract's methodology version invalidates all prior ratings until they are explicitly re-attested.
- `evidenceHash` (bytes32) — `keccak256` of the off-chain attestation bundle (project design document, verification report, satellite imagery index, etc.). The contract does not enforce any particular content; it is a pointer that assessors, downstream verifiers, and dispute resolvers can check against their canonical copy.

`isStale(address, uint256) view returns (bool)` is the single source of truth for freshness. `meetsGrade(...)` returns `false` for stale ratings. `QualityGatedPool.deposit(...)` rejects stale ratings with a `StaleRating` error.

### Access control

- `owner` (set in constructor) manages the rater allowlist.
- Any allowlisted `rater` can call `setRating`. Anyone can read ratings.

**This is deliberately simple.** A production deployment would replace the single-role rater with a decentralized attestation network (e.g., EAS, UMA-style optimistic oracle, or multi-rater majority). See `docs/decentralized-rater-design.md` for the trade-off analysis and recommended migration path.

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

## Known limitations (v0.6)

1. **Single rater role.** Centralization risk; documented in workshop paper §9 and addressed in `docs/decentralized-rater-design.md`.
2. ~~No rating expiry~~ **resolved in v0.4** — `expiresAt` + `methodologyVersion` + `isStale()`.
3. ~~No provenance~~ **resolved in v0.4** — `evidenceHash` field on `Rating`.
4. **ERC-20 only.** Pool logic assumes a fungible ERC-20 credit; ERC-1155 / ERC-721 support (Nori-style NRTs) is not yet implemented.
5. **No proof-of-retirement.** Retirement should decrement pool reserves and emit a canonical retirement event.
6. **No on-chain expiry policy enforcement.** Raters can pass any future `expiresAt` they like; there is no contract-level minimum/maximum freshness window. A production deployment should probably enforce e.g. "expiresAt must be between 3 months and 3 years from now" to prevent abuse.
7. **No dispute mechanism.** A v0.4 rating can only be overridden by the same rater (or another allowlisted rater) re-attesting. There is no challenge window, no economic bond, no appeal. This is the main motivation for the decentralized rater design doc.
