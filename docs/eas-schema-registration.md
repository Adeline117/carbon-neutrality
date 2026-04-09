# EAS Schema Registration Guide

*How to register the carbon credit quality rating schema on EAS and begin publishing attestations.*

## Schema definition

The v0.6 EAS schema encodes a complete rating attestation as a single ABI-encoded tuple:

```
(
  (uint8,uint8,uint8,uint8,uint8,uint8,uint8),   // DimensionScores
  (uint8,uint8,uint8,uint8,uint8,uint8,uint8),   // DimensionStds
  (bool,bool,bool,bool,bool,bool,bool),           // Disqualifiers (7 flags in v0.6)
  uint64,                                          // expiresAt
  bytes32                                          // evidenceHash
)
```

Human-readable field names (for EAS schema registration):

```
uint8 removalType, uint8 additionality, uint8 permanence, uint8 mrvGrade, uint8 vintageYear, uint8 coBenefits, uint8 registryMethodology, uint8 stdRemovalType, uint8 stdAdditionality, uint8 stdPermanence, uint8 stdMrvGrade, uint8 stdVintageYear, uint8 stdCoBenefits, uint8 stdRegistryMethodology, bool doubleCounting, bool failedVerification, bool sanctionedRegistry, bool noThirdParty, bool humanRights, bool communityHarm, bool biodiversityHarm, uint64 expiresAt, bytes32 evidenceHash
```

## Registration

### On Base Sepolia (testnet)

EAS SchemaRegistry on Base Sepolia: `0x4200000000000000000000000000000000000020`

```bash
# Register schema (one-time)
cast send 0x4200000000000000000000000000000000000020 \
    "register(string,address,bool)" \
    "uint8 removalType, uint8 additionality, uint8 permanence, uint8 mrvGrade, uint8 vintageYear, uint8 coBenefits, uint8 registryMethodology, uint8 stdRemovalType, uint8 stdAdditionality, uint8 stdPermanence, uint8 stdMrvGrade, uint8 stdVintageYear, uint8 stdCoBenefits, uint8 stdRegistryMethodology, bool doubleCounting, bool failedVerification, bool sanctionedRegistry, bool noThirdParty, bool humanRights, bool communityHarm, bool biodiversityHarm, uint64 expiresAt, bytes32 evidenceHash" \
    0x0000000000000000000000000000000000000000 \
    true \
    --rpc-url $BASE_SEPOLIA_RPC_URL \
    --private-key $DEPLOYER_PRIVATE_KEY
```

The returned transaction receipt contains the schema UID. Save it as `EAS_SCHEMA_ID` in `.env`.

### On Base mainnet (future)

EAS on Base mainnet: `0x4200000000000000000000000000000000000021`

Same command with mainnet RPC. Only do this after expert consultation (v0.6 W3).

## Publishing attestations

Once the schema is registered and the adapter is deployed:

1. **An attester** (e.g., a registry or independent assessor) publishes an EAS attestation using the schema above, encoding the 7 dimension scores + 7 stds + 7 disqualifier flags + expiresAt + evidenceHash.

2. **Anyone** can then call `adapter.relay(attestationUid, creditToken, tokenId)` to push the attestation into the `CarbonCreditRating` contract.

3. The adapter verifies: schema match, not revoked, not expired, attester is in the trusted set.

4. The rating contract stores the decoded data and emits `RatingSet`.

## Interoperability with Hypercerts / Ecocerts

The Hypercerts Foundation operates an EAS-based evaluator registry on Base, Optimism, and Celo. Their GainForest "Ecocerts" sub-project uses similar EAS schemas for ecological impact claims (see `docs/research-on-chain-2025-2026.md` Finding 1, 12).

Our schema is structurally compatible: both use EAS attestations from a curated set of trusted evaluators. A future v0.7 integration could register our adapter as a Hypercerts-compatible evaluator for the "carbon credit quality" domain, enabling cross-ecosystem discovery.

## Schema versioning

The schema is tied to the `Disqualifiers` struct layout. Adding a new disqualifier (as in v0.6's `biodiversityHarm`) changes the schema. Use a new schema UID for breaking changes; the adapter's `schemaId` immutable ensures it only processes attestations from the matching schema version.
