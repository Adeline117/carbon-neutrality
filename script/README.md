# Deployment runbook — v0.4.1 Base Sepolia

> **PRELIMINARY AUTHOR ATTESTATIONS — NOT ENDORSED BY ANY REGISTRY, RATING AGENCY, OR REAL-WORLD CARBON MARKET PARTICIPANT.** Any ratings written to Base Sepolia by these scripts are author judgment for a testnet demonstration. Any value derived from them is play money.

This directory holds the Foundry scripts that deploy the v0.4.1 rating contract to Base Sepolia and seed it with the 14 tokenized-pilot credits.

## Files

| File | Purpose |
|------|---------|
| `Deploy.s.sol` | Deploys `CarbonCreditRating` + 2 `QualityGatedPool`s (AA-gated and A-gated) |
| `SeedRatings.s.sol` | Deploys 14 `MockCarbonCredit` ERC-20s and writes a rating for each, reading from `seed/tokenized_pilot.json` |
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

```bash
source .env

# Step 1: deploy the rating contract and the two pools
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
- Deploys 14 `MockCarbonCredit` ERC-20 tokens (MCC-T001 … MCC-T014)
- Mints 1,000 of each to the deployer
- Calls `setRating(...)` once per credit with the scores from `seed/tokenized_pilot.json`
- Sets `expiresAt = now + 365 days`
- Stamps an `evidenceHash` = `keccak256(credit_id || "v0.4.1")`

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

1. Fill in the addresses in `docs/v0.4.1-deployment-notes.md`.
2. Update the "Try it on Base Sepolia" section of `README.md` with the real addresses.
3. Run `python3 tools/snapshot.py` to generate `docs/api/v0.4.1/ratings.json`.
4. Enable GitHub Pages on the repo (Settings → Pages → source: main branch, /docs folder).
5. Enable the `.github/workflows/snapshot.yml` action so the API refreshes daily.

## Key custody

The `DEPLOYER_PRIVATE_KEY` is the only address allowed to write ratings after deployment (single-rater v0.4 design; v0.5 decentralized rater replaces this — see `docs/decentralized-rater-design.md`).

- Treat the key as **TESTNET ONLY**.
- Do NOT reuse on mainnet.
- Store in a password manager or hardware wallet, not a .env file on a shared machine.
- If you need to rotate, deploy a new rating contract with a new key. The old contract's on-chain data is public and immutable; rotate the *rater authority*, not the contract.

## Re-seeding / re-running

The scripts are idempotent-ish: running `Deploy.s.sol` twice deploys two separate rating contracts (second run costs more gas but is harmless). Running `SeedRatings.s.sol` twice deploys 14 *new* MockCarbonCredit instances each time — the old ones remain on-chain but the new batch is what gets rated by the target contract. To refresh an existing rating instead of creating a new credit, you would call `setRating()` directly via `cast send` against the same mock address; this pattern is what the v0.5 `expiresAt` field is designed for.
