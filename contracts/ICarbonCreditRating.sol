// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title ICarbonCreditRating
/// @notice Interface for the on-chain carbon credit quality rating framework.
///         See docs/workshop-paper.md and data/scoring-rubrics/ for the full methodology.
///         Scores are uint8 values in [0, 100]. Composite is expressed in basis points
///         (0-10000) so that grade boundaries map to round numbers (AAA=9000+, etc.).
interface ICarbonCreditRating {
    /// @notice Six-tier quality grade. Ordered from lowest (B) to highest (AAA).
    ///         Higher enum value = higher quality.
    enum Grade {
        B,    // 0   <  30
        BB,   // 1   30-44
        BBB,  // 2   45-59
        A,    // 3   60-74
        AA,   // 4   75-89
        AAA   // 5   90-100
    }

    /// @notice Per-dimension scores for a credit, all in [0, 100].
    ///         Struct order MUST match the weight layout in CarbonCreditRating.
    ///         v0.4: co_benefits is no longer scored in the composite (weight = 0);
    ///         it is attested as an informational field and used by assessors to
    ///         decide whether to set the communityHarm disqualifier flag.
    struct DimensionScores {
        uint8 removalType;          // v0.4: 25% weight
        uint8 additionality;        // v0.4: 20% weight
        uint8 permanence;           // v0.4: 17.5% weight
        uint8 mrvGrade;             // v0.4: 20% weight
        uint8 vintageYear;          // v0.4: 10% weight
        uint8 coBenefits;           // v0.4: 0% weight (informational; see communityHarm)
        uint8 registryMethodology;  // v0.4: 7.5% weight
    }

    /// @notice Bitmap of disqualifier flags. Any set bit may cap the final grade.
    ///         Bit positions are stable and must match the rubric index.json order.
    ///         v0.4: adds communityHarm (caps at BBB) as the safeguards-gate.
    struct Disqualifiers {
        bool doubleCounting;       // caps at B
        bool failedVerification;   // caps at B
        bool sanctionedRegistry;   // caps at BB
        bool noThirdParty;         // caps at BBB
        bool humanRights;          // caps at B
        bool communityHarm;        // caps at BBB (v0.4 safeguards-gate)
    }

    /// @notice Full rating result for a credit token.
    /// @dev v0.4: expiresAt + methodologyVersion + evidenceHash added for
    ///      freshness, version-grandfathering, and off-chain attestation provenance.
    struct Rating {
        DimensionScores scores;
        Disqualifiers flags;
        uint16 compositeBps;        // 0-10000
        Grade nominalGrade;         // pre-disqualifier
        Grade finalGrade;           // post-disqualifier
        uint64 lastUpdatedAt;       // unix seconds
        uint64 expiresAt;           // v0.4: unix seconds; 0 means "never"
        uint16 methodologyVersion;  // v0.4: e.g. 0x0400 for v0.4; contract constant at write time
        bytes32 evidenceHash;       // v0.4: keccak256 of the attestation bundle (PDD, verification report, etc.)
        address attestedBy;
    }

    /// @notice Emitted when a credit's scores are set or updated.
    event RatingSet(
        address indexed creditToken,
        uint256 indexed tokenId,
        uint16 compositeBps,
        Grade nominalGrade,
        Grade finalGrade,
        uint16 methodologyVersion,
        uint64 expiresAt,
        address indexed attestedBy
    );

    /// @notice Set or update the per-dimension scores and disqualifier flags for a credit.
    ///         Only an authorized rater may call. The composite, nominal grade and final
    ///         grade are recomputed and stored. The methodology version is stamped from
    ///         the contract constant, not from the caller.
    /// @param expiresAt    Unix seconds after which the rating is considered stale. Use 0 for never.
    /// @param evidenceHash keccak256 of the off-chain attestation bundle (PDD, verification report, etc.).
    function setRating(
        address creditToken,
        uint256 tokenId,
        DimensionScores calldata scores,
        Disqualifiers calldata flags,
        uint64 expiresAt,
        bytes32 evidenceHash
    ) external;

    /// @notice Fetch the full rating for a credit. Reverts if unrated.
    function ratingOf(address creditToken, uint256 tokenId)
        external
        view
        returns (Rating memory);

    /// @notice Returns whether `(creditToken, tokenId)` meets the minimum grade.
    ///         Unrated or stale credits are considered ineligible.
    function meetsGrade(
        address creditToken,
        uint256 tokenId,
        Grade minGrade
    ) external view returns (bool);

    /// @notice Returns true if the rating has expired (past `expiresAt`, where 0 means never)
    ///         or if it was written under an older methodology version.
    ///         Unrated credits return false (there is nothing to be stale).
    function isStale(address creditToken, uint256 tokenId) external view returns (bool);
}
