// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ICarbonCreditRating} from "../ICarbonCreditRating.sol";

/// @title RenewableEnergyCertGate
/// @notice Generalization demonstration: the ERC-CCQR interface (`meetsGrade`,
///         `ratingOf`, `isStale`) applied to Renewable Energy Certificate (REC)
///         quality gating.
///
///         This is the second generalization example proving that `meetsGrade()`
///         works for non-carbon real-world assets. RECs face the same quality
///         heterogeneity problem as carbon credits: a solar REC from a new
///         plant providing grid additionality is not equivalent to a legacy
///         hydro REC from an existing dam.
///
/// @dev    REC-SPECIFIC SCORING DIMENSIONS (domain-specific rubric):
///         A REC-specific implementation would replace the carbon dimensions
///         with the following:
///
///         1. Generation Source (weight ~25%)
///            Technology type and quality tier. New-build solar/wind scores
///            higher than existing large hydro. Analogous to carbon's
///            "removal type" dimension (Oxford hierarchy).
///
///         2. Grid Impact (weight ~20%)
///            Marginal vs. average grid displacement. A wind farm in a
///            coal-heavy grid displaces more emissions than one in a hydro-
///            dominated grid. Measured via locational marginal emission rates.
///
///         3. Temporal Matching (weight ~20%)
///            Hourly or sub-hourly matching between generation and consumption
///            (24/7 CFE). Annual matching (bundled RECs) scores lower than
///            hourly matching (Google 24/7, EnergyTag granular certificates).
///
///         4. Additionality (weight ~17.5%)
///            Did the REC purchase cause new renewable capacity? New-build
///            projects with PPA score higher than existing plants selling
///            unbundled RECs. Same concept as carbon additionality.
///
///         5. Vintage & Delivery (weight ~10%)
///            Recency of generation and delivery verification. Current-year
///            RECs score higher than banked multi-year-old certificates.
///
///         6. Registry & Tracking (weight ~7.5%)
///            I-REC, TIGR, M-RETS, EU GoO, or national registry. Registry
///            credibility and double-counting prevention mechanisms.
///
///         The Grade enum (B through AAA) and meetsGrade() semantics are
///         IDENTICAL to the carbon use case. Only the scoring dimensions
///         and their weights change in the implementation contract.
///
/// @dev    ILLUSTRATIVE EXAMPLE for the WWW 2027 generalization argument.
///         Not a production contract.
contract RenewableEnergyCertGate {
    ICarbonCreditRating public immutable ratings;
    ICarbonCreditRating.Grade public immutable minGrade;

    error BelowMinGrade(ICarbonCreditRating.Grade actual, ICarbonCreditRating.Grade required);
    error StaleOrUnrated();

    event RECDepositAccepted(
        address indexed creditToken,
        uint256 indexed tokenId,
        ICarbonCreditRating.Grade grade,
        uint16 compositeBps
    );

    constructor(ICarbonCreditRating _ratings, ICarbonCreditRating.Grade _minGrade) {
        ratings = _ratings;
        minGrade = _minGrade;
    }

    /// @notice Gate a REC deposit using the same meetsGrade() interface.
    ///         The consuming protocol asks "does this REC meet grade A?"
    ///         without knowing whether the underlying dimensions are carbon-
    ///         specific or REC-specific. This is the generalization insight.
    function checkDeposit(address creditToken, uint256 tokenId)
        external
        view
        returns (uint16 compositeBps)
    {
        if (!ratings.meetsGrade(creditToken, tokenId, minGrade)) {
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
}
