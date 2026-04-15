# Deployment runbook — v0.6 Base Sepolia

> **PRELIMINARY AUTHOR ATTESTATIONS — NOT ENDORSED BY ANY REGISTRY, RATING AGENCY, OR REAL-WORLD CARBON MARKET PARTICIPANT.** Any ratings written to Base Sepolia by these scripts are author judgment for a testnet demonstration. Any value derived from them is play money.

This directory holds the Foundry scripts that deploy the v0.6 contracts to Base Sepolia and seed them with the 16 tokenized-pilot credits.

## Contracts (8 total)

| # | Contract | Source | Purpose |
|---|----------|--------|---------|
| 1 | `CarbonCreditRating` | `contracts/CarbonCreditRating.sol` | Core rating storage: 7 dimension scores, 7 stds, 7 disqualifier flags (v0.6: +biodiversityHarm), composite, grade |
| 2 | `ICarbonCreditRating` | `contracts/ICarbonCreditRating.sol` | Interface consumed by all downstream contracts |
| 3 | `QualityGatedPool` (AA) | `contracts/QualityGatedPool.sol` | Premium pool: rejects deposits below AA grade |
| 4 | `QualityGatedPool` (A) | `contracts/QualityGatedPool.sol` | Standard pool: rejects deposits below A grade |
| 5 | `CarbonCreditRatingEASAdapter` | `contracts/CarbonCreditRatingEASAdapter.sol` | v0.6 decentralized rater: relays EAS attestations from trusted attesters into CarbonCreditRating |
| 6 | `IEASMinimal` | `contracts/IEASMinimal.sol` | Minimal EAS read interface (getAttestation) |
| 7 | `KlimaRetirementGate` | `contracts/examples/KlimaRetirementGate.sol` | Example: quality-gated Klima kVCM retirement flow |
| 8 | `CHARQualityOverlay` | `contracts/examples/CHARQualityOverlay.sol` | Example: quality overlay for Toucan CHAR pool on Base |

Contracts 7-8 are illustrative examples (not deployed in the standard flow). Deploy them manually if demonstrating integration patterns.

## Files

| File | Purpose |
|------|---------|
| `Deploy.s.sol` | Deploys `CarbonCreditRating` + 2 `QualityGatedPool`s (AA-gated and A-gated) |
| `SeedRatings.s.sol` | Deploys 16 `MockCarbonCredit` ERC-20s and writes a rating for each, reading from `seed/tokenized_pilot.json` |
| `register-eas-schema.sh` | Registers the v0.6 EAS schema on Base Sepolia SchemaRegistry (run once before deploying the EAS adapter) |
| `seed/tokenized_pilot.json` | Pre-generated from `data/tokenized-pilot/credits.json` via `python3 tools/regen_seed.py` |

## One-time setup

```bash
# 1. Install Foundry if you don't have it
curl -L https://foundry.paradigm.xyz | bash
foundryup

# 2. Generate a fresh testnet-only key
cast wallet new

# 3. Copy the example env and fill in values
cp .env.example .env
# Edit .env: set DEPLOYER_PRIVATE_KEY, BASESCAN_API_KEY

# 4. Fund the deployer with Base Sepolia ETH
# Use any faucet from https://docs.base.org/docs/tools/network-faucets/
# You need ~0.01 ETH for the full deploy + seed flow

# 5. Verify you can build
forge build
```

## Deploy

### Step 1: Core contracts (CarbonCreditRating + 2 pools)

```bash
source .env

forge script script/Deploy.s.sol \
    --rpc-url $BASE_SEPOLIA_RPC_URL \
    --broadcast \
    --verify \
    --etherscan-api-key $BASESCAN_API_KEY \
    -vvv

# Save the printed addresses into .env:
#   RATING_ADDRESS="0x..."
#   PREMIUM_POOL_ADDRESS="0x..."
#   STANDARD_POOL_ADDRESS="0x..."
```

### Step 2: Register EAS schema (one-time, before deploying adapter)

```bash
export PRIVATE_KEY=$DEPLOYER_PRIVATE_KEY
export RPC_URL=$BASE_SEPOLIA_RPC_URL
./script/register-eas-schema.sh

# Save the output schema UID into .env:
#   EAS_SCHEMA_ID="0x..."
```

### Step 3: Deploy EAS Adapter (manual via forge create)

```bash
source .env

# EAS on Base Sepolia: 0x4200000000000000000000000000000000000021
# (Use the predeploy EAS address for your chain)
forge create contracts/CarbonCreditRatingEASAdapter.sol:CarbonCreditRatingEASAdapter \
    --constructor-args $RATING_ADDRESS 0x4200000000000000000000000000000000000021 $EAS_SCHEMA_ID \
    --rpc-url $BASE_SEPOLIA_RPC_URL \
    --private-key $DEPLOYER_PRIVATE_KEY \
    --verify \
    --etherscan-api-key $BASESCAN_API_KEY

# Save the adapter address:
#   EAS_ADAPTER_ADDRESS="0x..."

# Authorize the adapter as a rater on the rating contract:
cast send $RATING_ADDRESS \
    "setRater(address,bool)" \
    $EAS_ADAPTER_ADDRESS true \
    --rpc-url $BASE_SEPOLIA_RPC_URL \
    --private-key $DEPLOYER_PRIVATE_KEY

# Add trusted attesters (e.g., your test attester address):
cast send $EAS_ADAPTER_ADDRESS \
    "setAttester(address,bool)" \
    <ATTESTER_ADDRESS> true \
    --rpc-url $BASE_SEPOLIA_RPC_URL \
    --private-key $DEPLOYER_PRIVATE_KEY
```

### Step 4 (optional): Deploy example contracts

```bash
# KlimaRetirementGate (illustrative, BBB minimum)
forge create contracts/examples/KlimaRetirementGate.sol:KlimaRetirementGate \
    --constructor-args $RATING_ADDRESS 2 \
    --rpc-url $BASE_SEPOLIA_RPC_URL \
    --private-key $DEPLOYER_PRIVATE_KEY

# CHARQualityOverlay (illustrative, AA minimum)
forge create contracts/examples/CHARQualityOverlay.sol:CHARQualityOverlay \
    --constructor-args $RATING_ADDRESS 4 \
    --rpc-url $BASE_SEPOLIA_RPC_URL \
    --private-key $DEPLOYER_PRIVATE_KEY
```

## Seed

```bash
source .env  # reload with RATING_ADDRESS filled in

forge script script/SeedRatings.s.sol \
    --rpc-url $BASE_SEPOLIA_RPC_URL \
    --broadcast \
    --verify \
    --etherscan-api-key $BASESCAN_API_KEY \
    -vvv
```

The seed script:
- Deploys 16 `MockCarbonCredit` ERC-20 tokens (MCC-T001 ... MCC-T016)
- Mints 1,000 of each to the deployer
- Calls `setRating(...)` once per credit with the scores from `seed/tokenized_pilot.json`
- Includes v0.5 default per-dimension stds (empirical W1 IRR data)
- Sets `expiresAt = now + 365 days`
- Stamps an `evidenceHash` = `keccak256(credit_id || "v0.5.0")`
- v0.6: `biodiversityHarm` disqualifier flag defaults to `false` for all pilot credits

Total on-chain cost on Base Sepolia: well under 0.01 ETH. All ratings are author attestations as described in the disclaimer at the top of this file.

## Verify the deployment

```bash
# Read Climeworks Orca (should be AAA, composite 9520 bps)
cast call $RATING_ADDRESS \
    "ratingOf(address,uint256)" \
    <MCC-T009 address from seed logs> 0 \
    --rpc-url $BASE_SEPOLIA_RPC_URL

# Read Toucan BCT (should be BB, composite 3110 bps)
cast call $RATING_ADDRESS \
    "ratingOf(address,uint256)" \
    <MCC-T001 address from seed logs> 0 \
    --rpc-url $BASE_SEPOLIA_RPC_URL

# Check the AA-gated pool rejects BCT
cast call $PREMIUM_POOL_ADDRESS \
    "deposit(address,uint256,uint256)" \
    <MCC-T001 address> 0 100 \
    --rpc-url $BASE_SEPOLIA_RPC_URL
# Expected: reverts with BelowMinGrade(BB, AA)
```

## After deployment

1. Fill in the addresses in deployment notes (rating, pools, EAS adapter, example contracts).
2. Update the "Try it on Base Sepolia" section of `README.md` with the real addresses.
3. Run `python3 tools/snapshot.py` to generate the public read API JSON.
4. Enable GitHub Pages on the repo (Settings → Pages → source: main branch, /docs folder).
5. Enable the `.github/workflows/snapshot.yml` action so the API refreshes daily.
6. Verify the EAS adapter can relay attestations end-to-end (create a test attestation via the EAS SDK, then call `adapter.relay()`).

## Key custody

The `DEPLOYER_PRIVATE_KEY` serves two roles in v0.6:

1. **Rating contract owner** — can add/remove raters via `setRater()`.
2. **EAS adapter owner** — can add/remove trusted attesters via `setAttester()`.

The deployer is also set as the initial rater for direct `setRating()` calls (seed script). In production, the EAS adapter would be the primary rater, with the deployer key used only for admin operations.

- Treat the key as **TESTNET ONLY**.
- Do NOT reuse on mainnet.
- Store in a password manager or hardware wallet, not a .env file on a shared machine.
- If you need to rotate, transfer ownership (`transferOwnership()` on both the rating contract and the adapter) to a new address, then revoke the old key's rater/attester status.
- For mainnet: use a timelocked multisig for ownership (see `CarbonCreditRatingEASAdapter.sol` @dev notes).

## Re-seeding / re-running

The scripts are idempotent-ish: running `Deploy.s.sol` twice deploys two separate rating contracts (second run costs more gas but is harmless). Running `SeedRatings.s.sol` twice deploys 16 *new* MockCarbonCredit instances each time -- the old ones remain on-chain but the new batch is what gets rated by the target contract. To refresh an existing rating instead of creating a new credit, you would call `setRating()` directly via `cast send` against the same mock address; this pattern is what the `expiresAt` field is designed for.

## v0.6 changes from v0.4.1

- **Disqualifiers**: 7 flags (added `biodiversityHarm`, caps at BBB; per Zeng et al., Nature Reviews Biodiversity 2026).
- **EAS adapter**: New `CarbonCreditRatingEASAdapter` contract relays EAS attestations from trusted attesters. Requires EAS schema registration before deployment.
- **Example integrations**: `KlimaRetirementGate` and `CHARQualityOverlay` demonstrate real-world integration patterns.
- **registry_methodology**: Rubric changed from 4-tier to 2-tier (CCP/Non-CCP). Run `python3 tools/remap_registry_v06.py` before `regen_seed.py` if starting from v0.5 data.
- **Seed data**: 16 credits (up from 14 in v0.4.1), including T015 Toucan CHAR and T016 Rainbow Standard biochar.
