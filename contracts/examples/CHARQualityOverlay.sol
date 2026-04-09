// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ICarbonCreditRating} from "../ICarbonCreditRating.sol";

/// @title CHARQualityOverlay
/// @notice Example showing how Toucan's CHAR pool could augment its
///         binary project-allowlist gating with continuous quality rating.
///
///         Context: CHAR pool on Base (0x20b048fA035D5763685D695e66aDF62c5D9F5055)
///         uses checkEligible() to allowlist specific Puro-certified biochar
///         projects. This overlay adds a second gate: even if a project passes
///         CHAR's allowlist, it must also meet a minimum quality grade from
///         our rating contract. This enables CHAR to evolve from binary
///         (allowed/not) to continuous (allowed AND rated AA+).
///
/// @dev    ILLUSTRATIVE EXAMPLE. A real integration would:
///         - Be a modification to CHAR's Pool contract, not a standalone overlay
///         - Use CHAR's existing TCO2 token interface
///         - Handle the dynamic fee mechanism alongside the quality gate
contract CHARQualityOverlay {
    ICarbonCreditRating public immutable ratings;
    ICarbonCreditRating.Grade public immutable minGrade;

    error BelowMinGrade(ICarbonCreditRating.Grade actual, ICarbonCreditRating.Grade required);
    error StaleOrUnrated();

    event QualityCheckPassed(address indexed creditToken, uint256 indexed tokenId, ICarbonCreditRating.Grade grade, uint16 compositeBps);

    constructor(ICarbonCreditRating _ratings, ICarbonCreditRating.Grade _minGrade) {
        ratings = _ratings;
        minGrade = _minGrade;
    }

    /// @notice Quality check to run AFTER CHAR's checkEligible passes.
    ///         Returns the composite score (in basis points) for use in
    ///         dynamic fee calculation — higher-quality credits could get
    ///         a lower fee, incentivizing quality deposits.
    /// @return compositeBps The credit's composite quality score (0-10000)
    function qualityGate(address creditToken, uint256 tokenId)
        external
        view
        returns (uint16 compositeBps)
    {
        if (!ratings.meetsGrade(creditToken, tokenId, minGrade)) {
            // Distinguish stale/unrated from below-grade
            try ratings.ratingOf(creditToken, tokenId) returns (ICarbonCreditRating.Rating memory r) {
                if (ratings.isStale(creditToken, tokenId)) revert StaleOrUnrated();
                revert BelowMinGrade(r.finalGrade, minGrade);
            } catch {
                revert StaleOrUnrated();
            }
        }

        ICarbonCreditRating.Rating memory r = ratings.ratingOf(creditToken, tokenId);
        return r.compositeBps;
    }

    /// @notice Suggest a fee discount based on quality. Higher quality → lower fee.
    ///         CHAR's dynamic fee penalizes concentration; this adds a quality
    ///         bonus that rewards integrity. The two mechanisms are complementary.
    /// @return discountBps Fee discount in basis points (0-500, max 5% discount)
    function qualityFeeDiscount(address creditToken, uint256 tokenId)
        external
        view
        returns (uint16 discountBps)
    {
        try ratings.ratingOf(creditToken, tokenId) returns (ICarbonCreditRating.Rating memory r) {
            if (ratings.isStale(creditToken, tokenId)) return 0;
            // AAA: 500 bps (5%) discount, AA: 300, A: 100, BBB+: 0
            if (r.finalGrade == ICarbonCreditRating.Grade.AAA) return 500;
            if (r.finalGrade == ICarbonCreditRating.Grade.AA) return 300;
            if (r.finalGrade == ICarbonCreditRating.Grade.A) return 100;
            return 0;
        } catch {
            return 0;
        }
    }
}
