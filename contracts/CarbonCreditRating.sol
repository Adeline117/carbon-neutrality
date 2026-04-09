// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ICarbonCreditRating} from "./ICarbonCreditRating.sol";

/// @title CarbonCreditRating
/// @notice Reference implementation of the on-chain carbon credit quality rating.
///         Weights, grade boundaries, and disqualifier caps match v0.4 of the
///         workshop paper and data/scoring-rubrics/index.json.
///
/// @dev    v0.4 adopts the safeguards-gate mechanism (see docs/methodology-gate-v0.4.md):
///         co_benefits weight is 0; its 0.075 is redistributed across removal_type,
///         permanence, and mrv_grade. A new communityHarm disqualifier caps at BBB.
///
/// @dev    This is a MVP prototype. Production deployment should:
///         - Replace the single-owner rater with a multi-rater oracle or attestation network
///         - Add rating provenance (methodology version, data inputs, proof-of-audit)
///         - Emit per-dimension change events for auditability
///         - Integrate rating expiry (annual re-verification)
contract CarbonCreditRating is ICarbonCreditRating {
    // ------------------------------------------------------------------
    // Weights (basis points, sum = 10000). v0.4 safeguards-gate.
    // ------------------------------------------------------------------
    uint16 private constant W_REMOVAL_TYPE       = 2500;   // v0.3: 2000
    uint16 private constant W_ADDITIONALITY      = 2000;
    uint16 private constant W_PERMANENCE         = 1750;   // v0.3: 1500
    uint16 private constant W_MRV_GRADE          = 2000;   // v0.3: 1500
    uint16 private constant W_VINTAGE            = 1000;
    uint16 private constant W_CO_BENEFITS        = 0;      // v0.3: 1000 (now informational; see communityHarm)
    uint16 private constant W_REGISTRY_METHOD    = 750;    // v0.3: 1000

    // ------------------------------------------------------------------
    // Grade boundaries (composite in basis points)
    // ------------------------------------------------------------------
    uint16 private constant AAA_MIN = 9000;
    uint16 private constant AA_MIN  = 7500;
    uint16 private constant A_MIN   = 6000;
    uint16 private constant BBB_MIN = 4500;
    uint16 private constant BB_MIN  = 3000;

    // ------------------------------------------------------------------
    // Methodology version. Bump with each v0.X rubric release.
    // v0.4 uses 0x0400; v0.5 adds distributional composite at 0x0500.
    // Any v0.4.x rating is automatically stale under a v0.5 deployment
    // because methodologyVersion < CURRENT_METHODOLOGY_VERSION.
    // ------------------------------------------------------------------
    uint16 public constant CURRENT_METHODOLOGY_VERSION = 0x0500;

    // ------------------------------------------------------------------
    // Storage
    // ------------------------------------------------------------------
    address public owner;
    mapping(address => bool) public isRater;
    mapping(bytes32 => Rating) private _ratings;

    // ------------------------------------------------------------------
    // Errors
    // ------------------------------------------------------------------
    error NotOwner();
    error NotRater();
    error ScoreOutOfRange(string dimension, uint8 value);
    error Unrated();
    error ExpiryInPast(uint64 expiresAt, uint64 nowTs);

    // ------------------------------------------------------------------
    // Events
    // ------------------------------------------------------------------
    event RaterSet(address indexed rater, bool allowed);
    event OwnerTransferred(address indexed from, address indexed to);

    // ------------------------------------------------------------------
    // Modifiers
    // ------------------------------------------------------------------
    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier onlyRater() {
        if (!isRater[msg.sender]) revert NotRater();
        _;
    }

    // ------------------------------------------------------------------
    // Constructor
    // ------------------------------------------------------------------
    constructor(address initialRater) {
        owner = msg.sender;
        isRater[initialRater] = true;
        emit OwnerTransferred(address(0), msg.sender);
        emit RaterSet(initialRater, true);
    }

    // ------------------------------------------------------------------
    // Admin
    // ------------------------------------------------------------------
    function setRater(address rater, bool allowed) external onlyOwner {
        isRater[rater] = allowed;
        emit RaterSet(rater, allowed);
    }

    function transferOwnership(address newOwner) external onlyOwner {
        emit OwnerTransferred(owner, newOwner);
        owner = newOwner;
    }

    // ------------------------------------------------------------------
    // Rating write path
    // ------------------------------------------------------------------
    function setRating(
        address creditToken,
        uint256 tokenId,
        DimensionScores calldata scores,
        DimensionStds calldata stds,
        Disqualifiers calldata flags,
        uint64 expiresAt,
        bytes32 evidenceHash
    ) external onlyRater {
        _validateScores(scores);
        _validateStds(stds);
        // expiresAt=0 means "never"; otherwise it must be strictly in the future.
        if (expiresAt != 0 && expiresAt <= block.timestamp) {
            revert ExpiryInPast(expiresAt, uint64(block.timestamp));
        }

        uint16 compositeBps = _computeCompositeBps(scores);
        uint32 varianceBps2 = _computeCompositeVarianceBps2(stds);
        Grade nominal = _gradeFromComposite(compositeBps);
        Grade finalGrade = _applyDisqualifiers(nominal, flags);

        bytes32 key = _key(creditToken, tokenId);
        _ratings[key] = Rating({
            scores: scores,
            stds: stds,
            flags: flags,
            compositeBps: compositeBps,
            compositeVarianceBps2: varianceBps2,
            nominalGrade: nominal,
            finalGrade: finalGrade,
            lastUpdatedAt: uint64(block.timestamp),
            expiresAt: expiresAt,
            methodologyVersion: CURRENT_METHODOLOGY_VERSION,
            evidenceHash: evidenceHash,
            attestedBy: msg.sender
        });

        emit RatingSet(
            creditToken,
            tokenId,
            compositeBps,
            nominal,
            finalGrade,
            CURRENT_METHODOLOGY_VERSION,
            expiresAt,
            msg.sender
        );
    }

    // ------------------------------------------------------------------
    // Rating read path
    // ------------------------------------------------------------------
    function ratingOf(address creditToken, uint256 tokenId)
        external
        view
        returns (Rating memory)
    {
        Rating memory r = _ratings[_key(creditToken, tokenId)];
        if (r.lastUpdatedAt == 0) revert Unrated();
        return r;
    }

    function meetsGrade(address creditToken, uint256 tokenId, Grade minGrade)
        external
        view
        returns (bool)
    {
        Rating memory r = _ratings[_key(creditToken, tokenId)];
        if (r.lastUpdatedAt == 0) return false;
        if (_isStale(r)) return false;
        return uint8(r.finalGrade) >= uint8(minGrade);
    }

    /// @notice Public view: true if the rating is expired or written under an older
    ///         methodology version. Returns false for unrated credits (nothing to be stale).
    function isStale(address creditToken, uint256 tokenId) external view returns (bool) {
        Rating memory r = _ratings[_key(creditToken, tokenId)];
        if (r.lastUpdatedAt == 0) return false;
        return _isStale(r);
    }

    // ------------------------------------------------------------------
    // Pure helpers (exposed for testing and off-chain reproducibility)
    // ------------------------------------------------------------------
    function computeComposite(DimensionScores calldata scores) external pure returns (uint16) {
        _validateScores(scores);
        return _computeCompositeBps(scores);
    }

    /// @notice v0.5: exposed for off-chain reproducibility (Python scorer cross-check).
    function computeCompositeVariance(DimensionStds calldata stds) external pure returns (uint32) {
        _validateStds(stds);
        return _computeCompositeVarianceBps2(stds);
    }

    function gradeFromComposite(uint16 compositeBps) external pure returns (Grade) {
        return _gradeFromComposite(compositeBps);
    }

    function applyDisqualifiers(Grade nominal, Disqualifiers calldata flags)
        external
        pure
        returns (Grade)
    {
        return _applyDisqualifiers(nominal, flags);
    }

    // ------------------------------------------------------------------
    // Internal
    // ------------------------------------------------------------------
    function _key(address creditToken, uint256 tokenId) private pure returns (bytes32) {
        return keccak256(abi.encode(creditToken, tokenId));
    }

    /// @dev A rating is stale if it has expired (past expiresAt, where 0 = never)
    ///      or if it was written under an older methodology version. Never raises
    ///      for unrated credits; callers check lastUpdatedAt first.
    function _isStale(Rating memory r) private view returns (bool) {
        if (r.methodologyVersion < CURRENT_METHODOLOGY_VERSION) return true;
        if (r.expiresAt != 0 && block.timestamp >= r.expiresAt) return true;
        return false;
    }

    function _validateScores(DimensionScores calldata s) private pure {
        if (s.removalType > 100) revert ScoreOutOfRange("removalType", s.removalType);
        if (s.additionality > 100) revert ScoreOutOfRange("additionality", s.additionality);
        if (s.permanence > 100) revert ScoreOutOfRange("permanence", s.permanence);
        if (s.mrvGrade > 100) revert ScoreOutOfRange("mrvGrade", s.mrvGrade);
        if (s.vintageYear > 100) revert ScoreOutOfRange("vintageYear", s.vintageYear);
        if (s.coBenefits > 100) revert ScoreOutOfRange("coBenefits", s.coBenefits);
        if (s.registryMethodology > 100) revert ScoreOutOfRange("registryMethodology", s.registryMethodology);
    }

    /// @dev v0.5: std values are in 0-100 units (same as scores). Reject >100.
    function _validateStds(DimensionStds calldata s) private pure {
        if (s.removalType > 100) revert ScoreOutOfRange("std.removalType", s.removalType);
        if (s.additionality > 100) revert ScoreOutOfRange("std.additionality", s.additionality);
        if (s.permanence > 100) revert ScoreOutOfRange("std.permanence", s.permanence);
        if (s.mrvGrade > 100) revert ScoreOutOfRange("std.mrvGrade", s.mrvGrade);
        if (s.vintageYear > 100) revert ScoreOutOfRange("std.vintageYear", s.vintageYear);
        if (s.coBenefits > 100) revert ScoreOutOfRange("std.coBenefits", s.coBenefits);
        if (s.registryMethodology > 100) revert ScoreOutOfRange("std.registryMethodology", s.registryMethodology);
    }

    /// @dev composite_bps = sum(score_i * weight_bps_i) / 100
    ///      score in [0,100], weight in [0,10000], result in [0,10000].
    function _computeCompositeBps(DimensionScores calldata s) private pure returns (uint16) {
        uint256 sum =
              uint256(s.removalType)         * W_REMOVAL_TYPE
            + uint256(s.additionality)       * W_ADDITIONALITY
            + uint256(s.permanence)          * W_PERMANENCE
            + uint256(s.mrvGrade)            * W_MRV_GRADE
            + uint256(s.vintageYear)         * W_VINTAGE
            + uint256(s.coBenefits)          * W_CO_BENEFITS
            + uint256(s.registryMethodology) * W_REGISTRY_METHOD;
        return uint16(sum / 100);
    }

    /// @dev v0.5: var(composite_bps) = sum(w_i_bps^2 * sigma_i^2) / 10000
    ///      Same shape as _computeCompositeBps but with squared weights and
    ///      squared stds. sigma_i is in 0-100 units (same as scores).
    ///      Max possible: 2500^2 * 50^2 * 7 = 1.09e11; / 10000 ≈ 1.09e7, fits uint32.
    function _computeCompositeVarianceBps2(DimensionStds calldata s) private pure returns (uint32) {
        uint256 sum =
              uint256(s.removalType)         * uint256(s.removalType)         * W_REMOVAL_TYPE      * W_REMOVAL_TYPE
            + uint256(s.additionality)       * uint256(s.additionality)       * W_ADDITIONALITY    * W_ADDITIONALITY
            + uint256(s.permanence)          * uint256(s.permanence)          * W_PERMANENCE       * W_PERMANENCE
            + uint256(s.mrvGrade)            * uint256(s.mrvGrade)            * W_MRV_GRADE        * W_MRV_GRADE
            + uint256(s.vintageYear)         * uint256(s.vintageYear)         * W_VINTAGE          * W_VINTAGE
            + uint256(s.coBenefits)          * uint256(s.coBenefits)          * W_CO_BENEFITS      * W_CO_BENEFITS
            + uint256(s.registryMethodology) * uint256(s.registryMethodology) * W_REGISTRY_METHOD  * W_REGISTRY_METHOD;
        // Scale from (score-unit^2 * bps^2) into bps² by dividing by 100^2 (score→bps scaling).
        return uint32(sum / 10000);
    }

    function _gradeFromComposite(uint16 bps) private pure returns (Grade) {
        if (bps >= AAA_MIN) return Grade.AAA;
        if (bps >= AA_MIN)  return Grade.AA;
        if (bps >= A_MIN)   return Grade.A;
        if (bps >= BBB_MIN) return Grade.BBB;
        if (bps >= BB_MIN)  return Grade.BB;
        return Grade.B;
    }

    /// @dev Disqualifiers cap the maximum achievable grade. They never raise a grade.
    function _applyDisqualifiers(Grade nominal, Disqualifiers calldata flags)
        private
        pure
        returns (Grade)
    {
        Grade capped = nominal;

        if (flags.doubleCounting      && capped > Grade.B)   capped = Grade.B;
        if (flags.failedVerification  && capped > Grade.B)   capped = Grade.B;
        if (flags.humanRights         && capped > Grade.B)   capped = Grade.B;
        if (flags.sanctionedRegistry  && capped > Grade.BB)  capped = Grade.BB;
        if (flags.noThirdParty        && capped > Grade.BBB) capped = Grade.BBB;
        if (flags.communityHarm       && capped > Grade.BBB) capped = Grade.BBB;

        return capped;
    }
}
