#!/usr/bin/env bash
# ============================================================================
# register-eas-schema.sh — Register the v0.6 carbon credit quality rating
# schema on the EAS SchemaRegistry (Base Sepolia).
#
# One-time operation. After running, save the schema UID printed at the end
# as EAS_SCHEMA_ID in your .env file.
#
# Required environment variables:
#   PRIVATE_KEY          — Deployer / schema registrant private key (testnet only!)
#   RPC_URL              — Base Sepolia RPC endpoint
#                          (e.g. https://sepolia.base.org or an Alchemy/Infura URL)
#
# Optional:
#   EAS_SCHEMA_REGISTRY  — Override the SchemaRegistry address
#                          (default: 0x4200000000000000000000000000000000000020 for Base Sepolia)
#
# Usage:
#   export PRIVATE_KEY="0x..."
#   export RPC_URL="https://sepolia.base.org"
#   ./script/register-eas-schema.sh
# ============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Validate required env vars
if [ -z "${PRIVATE_KEY:-}" ]; then
    echo "ERROR: PRIVATE_KEY env var is not set."
    echo "       Export your testnet deployer private key before running."
    exit 1
fi

if [ -z "${RPC_URL:-}" ]; then
    echo "ERROR: RPC_URL env var is not set."
    echo "       Export your Base Sepolia RPC URL before running."
    exit 1
fi

# EAS SchemaRegistry on Base Sepolia (predeploy address)
SCHEMA_REGISTRY="${EAS_SCHEMA_REGISTRY:-0x4200000000000000000000000000000000000020}"

# The v0.6 schema string.
# Must match docs/eas-schema-registration.md and the abi.decode layout in
# CarbonCreditRatingEASAdapter.sol:relay().
#
# Fields:
#   7 DimensionScores  (uint8 each)
#   7 DimensionStds    (uint8 each)
#   7 Disqualifiers    (bool each, including v0.6 biodiversityHarm)
#   uint64 expiresAt
#   bytes32 evidenceHash
SCHEMA="uint8 removalType, uint8 additionality, uint8 permanence, uint8 mrvGrade, uint8 vintageYear, uint8 coBenefits, uint8 registryMethodology, uint8 stdRemovalType, uint8 stdAdditionality, uint8 stdPermanence, uint8 stdMrvGrade, uint8 stdVintageYear, uint8 stdCoBenefits, uint8 stdRegistryMethodology, bool doubleCounting, bool failedVerification, bool sanctionedRegistry, bool noThirdParty, bool humanRights, bool communityHarm, bool biodiversityHarm, uint64 expiresAt, bytes32 evidenceHash"

# Resolver address: zero address (no resolver contract; anyone can attest)
RESOLVER="0x0000000000000000000000000000000000000000"

# Revocable: true (attestations can be revoked by the attester)
REVOCABLE="true"

echo "============================================================"
echo "EAS Schema Registration — Base Sepolia"
echo "============================================================"
echo ""
echo "SchemaRegistry:  $SCHEMA_REGISTRY"
echo "Resolver:        $RESOLVER"
echo "Revocable:       $REVOCABLE"
echo "Schema:          $SCHEMA"
echo ""
echo "------------------------------------------------------------"
echo "Step 1: Registering schema..."
echo "------------------------------------------------------------"

# ---------------------------------------------------------------------------
# Register the schema
# ---------------------------------------------------------------------------
# SchemaRegistry.register(string schema, address resolver, bool revocable)
# Returns: bytes32 schemaId (the UID of the newly registered schema)
TX_OUTPUT=$(cast send "$SCHEMA_REGISTRY" \
    "register(string,address,bool)" \
    "$SCHEMA" \
    "$RESOLVER" \
    "$REVOCABLE" \
    --rpc-url "$RPC_URL" \
    --private-key "$PRIVATE_KEY" \
    --json 2>&1)

echo "$TX_OUTPUT" | python3 -m json.tool 2>/dev/null || echo "$TX_OUTPUT"

# Extract the transaction hash
TX_HASH=$(echo "$TX_OUTPUT" | python3 -c "import sys,json; print(json.load(sys.stdin)['transactionHash'])" 2>/dev/null || true)

if [ -z "$TX_HASH" ]; then
    echo ""
    echo "WARNING: Could not extract transaction hash from output."
    echo "         Check the output above for errors."
    echo "         If the transaction succeeded, find the schema UID in the logs."
    exit 1
fi

echo ""
echo "Transaction hash: $TX_HASH"
echo ""

# ---------------------------------------------------------------------------
# Verification: read back the schema UID from transaction logs
# ---------------------------------------------------------------------------
echo "------------------------------------------------------------"
echo "Step 2: Fetching transaction receipt to extract schema UID..."
echo "------------------------------------------------------------"

RECEIPT=$(cast receipt "$TX_HASH" --rpc-url "$RPC_URL" --json 2>&1)

# The SchemaRegistry emits Registered(bytes32 uid, address registrant, ...)
# The schema UID is the first topic (topic[1]) of the Registered event,
# or it can be extracted from the first log's data depending on EAS version.
# For the Base predeploy, the UID is typically in logs[0].topics[1].
SCHEMA_UID=$(echo "$RECEIPT" | python3 -c "
import sys, json
receipt = json.load(sys.stdin)
logs = receipt.get('logs', [])
if logs:
    topics = logs[0].get('topics', [])
    if len(topics) > 1:
        print(topics[1])
    else:
        # Fallback: try data field
        print(logs[0].get('data', 'UNKNOWN'))
else:
    print('UNKNOWN')
" 2>/dev/null || echo "UNKNOWN")

echo ""
echo "Schema UID: $SCHEMA_UID"
echo ""

# ---------------------------------------------------------------------------
# Verification: read back the schema record from the registry
# ---------------------------------------------------------------------------
echo "------------------------------------------------------------"
echo "Step 3: Verifying schema by reading it back from the registry..."
echo "------------------------------------------------------------"

if [ "$SCHEMA_UID" != "UNKNOWN" ]; then
    # SchemaRegistry.getSchema(bytes32 uid) returns (SchemaRecord)
    # SchemaRecord { bytes32 uid, address resolver, bool revocable, string schema }
    SCHEMA_RECORD=$(cast call "$SCHEMA_REGISTRY" \
        "getSchema(bytes32)" \
        "$SCHEMA_UID" \
        --rpc-url "$RPC_URL" 2>&1)

    echo "Raw schema record:"
    echo "$SCHEMA_RECORD"
    echo ""
fi

echo "============================================================"
echo "DONE"
echo ""
echo "Save the following in your .env file:"
echo ""
echo "  EAS_SCHEMA_ID=$SCHEMA_UID"
echo ""
echo "Use this schema UID as the _schemaId constructor argument"
echo "when deploying CarbonCreditRatingEASAdapter."
echo "============================================================"
