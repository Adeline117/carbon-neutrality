// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ICarbonCreditRating} from "../ICarbonCreditRating.sol";

/// @title KlimaRetirementGate
/// @notice Example showing how Klima Protocol's kVCM retirement flow could
///         gate on our quality rating. Before retiring a credit from inventory,
///         check that it meets a minimum grade threshold.
///
///         Context: Klima 2.0 (kVCM on Base, 0x00fbac94fec8d4089d3fe979f39454f48c71a65d)
///         burns kVCM to retire credits. This gate could sit between the burn
///         request and the actual retirement execution.
///
/// @dev    This is an ILLUSTRATIVE EXAMPLE, not a production integration.
///         A real integration would need:
///         - Agreement from KlimaDAO governance
///         - Handling of the kVCM burn mechanics
///         - Fallback for unrated credits (allow with warning? reject?)
contract KlimaRetirementGate {
    ICarbonCreditRating public immutable ratings;
    ICarbonCreditRating.Grade public minRetirementGrade;
    address public owner;

    error BelowRetirementGrade(ICarbonCreditRating.Grade actual, ICarbonCreditRating.Grade required);
    error StaleRating();
    error Unrated();

    event RetirementApproved(address indexed creditToken, uint256 indexed tokenId, ICarbonCreditRating.Grade grade);
    event MinGradeUpdated(ICarbonCreditRating.Grade oldGrade, ICarbonCreditRating.Grade newGrade);

    constructor(ICarbonCreditRating _ratings, ICarbonCreditRating.Grade _minGrade) {
        ratings = _ratings;
        minRetirementGrade = _minGrade;
        owner = msg.sender;
    }

    /// @notice Check whether a credit is eligible for retirement under the
    ///         quality gate. Returns the credit's grade if eligible; reverts
    ///         if unrated, stale, or below threshold.
    /// @dev    In a real integration this would be called by the kVCM retirement
    ///         contract before executing the burn. The view-only pattern means
    ///         no gas cost for the check itself (it's a staticcall).
    function checkRetirementEligibility(address creditToken, uint256 tokenId)
        external
        view
        returns (ICarbonCreditRating.Grade)
    {
        // Check stale first (includes methodology version mismatch)
        if (ratings.isStale(creditToken, tokenId)) revert StaleRating();

        // Check rated and meets grade
        if (!ratings.meetsGrade(creditToken, tokenId, minRetirementGrade)) {
            // Distinguish between unrated and below-grade
            try ratings.ratingOf(creditToken, tokenId) returns (ICarbonCreditRating.Rating memory r) {
                revert BelowRetirementGrade(r.finalGrade, minRetirementGrade);
            } catch {
                revert Unrated();
            }
        }

        ICarbonCreditRating.Rating memory r = ratings.ratingOf(creditToken, tokenId);
        return r.finalGrade;
    }

    /// @notice Governance function to update the minimum retirement grade.
    ///         In production, this would be behind a timelock or multisig.
    function setMinGrade(ICarbonCreditRating.Grade newGrade) external {
        require(msg.sender == owner, "not owner");
        emit MinGradeUpdated(minRetirementGrade, newGrade);
        minRetirementGrade = newGrade;
    }
}
