# ERC-CCQR: Carbon Credit Quality Rating Standard

*Proposed interface standard for on-chain carbon credit quality gating. Not a formal EIP submission — a standalone standard proposal for the carbon DeFi ecosystem.*

## Preamble

| | |
|---|---|
| Title | Carbon Credit Quality Rating |
| Author | Adeline Wen |
| Status | Draft |
| Type | Interface Standard |
| Created | 2026-04-09 |
| Reference Implementation | [github.com/Adeline117/carbon-neutrality](https://github.com/Adeline117/carbon-neutrality) |

## Abstract

This document specifies a minimal interface for on-chain carbon credit quality rating that enables quality-gated deposit pools, retirement gates, and composable quality queries across DeFi protocols. The core primitive is `meetsGrade(address creditToken, uint256 tokenId, Grade minGrade) → bool` — a view function that any protocol can call at zero gas cost to determine whether a credit meets a quality threshold before accepting it.

## Motivation

Tokenized carbon credit pools (Toucan BCT, Moss MCO2, KlimaDAO treasury) suffered adverse selection because they treated all eligible credits as fungible regardless of quality. BCT's Lemons Index at peak was 0.724 — meaning the average credit quality was below 28/100. No on-chain mechanism existed to gate deposits by quality.

Commercial rating agencies (BeZero, Sylvera, Calyx, MSCI) produce quality assessments but these are off-chain, proprietary, and not callable by smart contracts. Toucan's CHAR pool introduced binary allowlist gating (`checkEligible()`), but binary gating cannot express continuous quality gradients.

This standard defines a **continuous quality rating interface** that enables:
- Quality-tiered pools (AAA pool, AA pool, A pool — each with different admission criteria and pricing)
- Quality-gated retirements (only retire credits above a minimum grade for compliance claims)
- Quality-based fee discounts (higher-quality deposits get lower fees, incentivizing quality)
- Cross-protocol quality queries (any protocol can read any credit's rating without integration)

## Specification

### Grade enum

```solidity
enum Grade { B, BB, BBB, A, AA, AAA }
```

Grades are ordered: `B(0) < BB(1) < BBB(2) < A(3) < AA(4) < AAA(5)`. Comparison uses uint8 casting.

### Required interface (Compliance Level 1)

```solidity
interface ICCQR {
    /// @notice Returns whether the credit meets the minimum grade.
    ///         Returns false for unrated or stale credits.
    function meetsGrade(address creditToken, uint256 tokenId, Grade minGrade)
        external view returns (bool);

    /// @notice Returns true if the rating has expired or was written
    ///         under an outdated methodology version.
    function isStale(address creditToken, uint256 tokenId)
        external view returns (bool);
}
```

A protocol is **Level 1 compliant** if it implements `meetsGrade` and `isStale`. This is sufficient for quality-gated pools and retirement gates.

### Extended interface (Compliance Level 2)

```solidity
interface ICCQR_Extended is ICCQR {
    struct Rating {
        uint16 compositeBps;            // 0-10000 (100.00 in basis points)
        uint32 compositeVarianceBps2;   // Variance for distributional scoring
        Grade nominalGrade;             // Before disqualifier caps
        Grade finalGrade;               // After disqualifier caps
        uint64 lastUpdatedAt;           // Unix seconds
        uint64 expiresAt;               // 0 = never
        uint16 methodologyVersion;      // e.g. 0x0600
        bytes32 evidenceHash;           // Pointer to off-chain attestation
        address attestedBy;             // Who wrote this rating
    }

    /// @notice Fetch the full rating. Reverts if unrated.
    function ratingOf(address creditToken, uint256 tokenId)
        external view returns (Rating memory);
}
```

A protocol is **Level 2 compliant** if it stores and exposes the full `Rating` struct. This enables distributional scoring (P(grade) from compositeBps + compositeVarianceBps2) and provenance tracking.

### EAS relay interface (Compliance Level 3)

```solidity
interface ICCQR_EAS is ICCQR_Extended {
    /// @notice Relay an EAS attestation into the rating contract.
    function relay(bytes32 attestationUid, address creditToken, uint256 tokenId)
        external;
}
```

Level 3 adds decentralized attestation via the Ethereum Attestation Service, enabling registry-based or multi-rater attestation without a single-owner key.

## Rationale

### Why `meetsGrade()` instead of returning a score?

Protocols need a boolean decision ("should I accept this deposit?"), not a number. `meetsGrade()` encapsulates the grade lookup, staleness check, and threshold comparison in a single call. A protocol that only needs admission control does not need to understand composites, variance, or disqualifiers — it just calls `meetsGrade(credit, 0, Grade.AA)`.

### Why a Grade enum instead of a numeric threshold?

Grades are the universal language of credit rating (Moody's, S&P, BeZero, Sylvera, Calyx, MSCI all use letter grades). A `Grade.AA` is immediately understood by market participants; a `compositeBps >= 7500` is not.

### Why include `compositeVarianceBps2`?

No commercial rating agency publishes grade uncertainty. The variance field enables downstream consumers to compute P(grade ≥ threshold) via Gaussian CDF, making the rating honest about its own precision. This is the first standard to include uncertainty quantification as a first-class field.

### Why `isStale()`?

Ratings decay. A rating written under an outdated methodology version (e.g., before a rubric refinement) should not be used for quality gating. `isStale()` checks both time expiry and methodology version mismatch, ensuring consumers always read fresh data.

## Reference Implementation

- `contracts/CarbonCreditRating.sol` — Level 2 compliant
- `contracts/QualityGatedPool.sol` — Consumer using Level 1
- `contracts/CarbonCreditRatingEASAdapter.sol` — Level 3 relay
- `contracts/examples/KlimaRetirementGate.sol` — Retirement gate pattern
- `contracts/examples/CHARQualityOverlay.sol` — Fee discount pattern

All implementations: [github.com/Adeline117/carbon-neutrality/contracts/](https://github.com/Adeline117/carbon-neutrality/tree/main/contracts)

## Security Considerations

- **Oracle trust**: the rating contract is only as trustworthy as its raters. Level 3 (EAS relay) mitigates single-rater risk but introduces EAS trust assumptions.
- **Staleness**: consumers MUST check `isStale()` or use `meetsGrade()` (which checks internally). Reading `ratingOf()` directly without staleness check can return outdated data.
- **Disqualifier bypass**: the `finalGrade` (post-disqualifier) must be used for gating, not `nominalGrade` (pre-disqualifier). `meetsGrade()` uses `finalGrade` by default.
- **Re-entrancy**: `meetsGrade()` is a view function and cannot be re-entered. `deposit()` patterns that call `meetsGrade()` before `transferFrom()` follow checks-effects-interactions.

## Copyright

MIT License. The standard and all reference implementations are open source.
