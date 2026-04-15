// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ICarbonCreditRating} from "../ICarbonCreditRating.sol";

/// @title BiodiversityCreditGate
/// @notice Generalization demonstration: the ERC-CCQR interface (`meetsGrade`,
///         `ratingOf`, `isStale`) applied to biodiversity credit quality gating.
///
///         This contract proves that the STANDARD is domain-agnostic. The same
///         `meetsGrade(address, uint256, Grade) -> bool` primitive that gates
///         carbon credit deposits can gate biodiversity credit deposits with
///         zero interface changes. The separation is:
///           - INTERFACE (meetsGrade, Grade enum, isStale) = domain-agnostic
///           - IMPLEMENTATION (7 carbon dimensions, weights) = domain-specific
///
///         This mirrors ERC-20: the standard (balanceOf, transfer) is universal;
///         each token implements its own supply logic.
///
/// @dev    BIODIVERSITY CREDIT DIMENSIONS (domain-specific scoring rubric):
///         A biodiversity-specific implementation of ICarbonCreditRating would
///         replace the 7 carbon dimensions with biodiversity-relevant ones:
///
///         1. Species Richness (weight ~20%)
///            Measured taxa diversity (Shannon-Wiener index, Simpson's index).
///            Analogous to carbon's "removal type" -- the core outcome metric.
///
///         2. Habitat Connectivity (weight ~20%)
///            Landscape-scale corridor contribution. Assessed via GIS analysis
///            of patch connectivity (e.g., Circuitscape, graph-theoretic metrics).
///
///         3. Permanence (weight ~17.5%)
///            Duration of habitat protection covenant. Same concept as carbon
///            permanence but measured in habitat preservation guarantees.
///
///         4. Additionality (weight ~17.5%)
///            Would the biodiversity outcome have occurred without the project?
///            Same concept as carbon additionality, applied to conservation.
///
///         5. MRV Quality (weight ~15%)
///            Monitoring, Reporting, Verification rigor. eDNA surveys, camera
///            traps, satellite land-cover change detection (e.g., Verra SD VISta,
///            Plan Vivo biodiversity monitoring protocols).
///
///         6. Registry & Methodology (weight ~10%)
///            Credibility of the issuing standard (Verra SD VISta, Plan Vivo,
///            Wallacea Trust, GBF Target 3 alignment).
///
///         The Grade enum (B through AAA) and meetsGrade() semantics are
///         IDENTICAL. Only the DimensionScores struct fields and weights change.
///
/// @dev    ILLUSTRATIVE EXAMPLE for the WWW 2027 generalization argument.
///         Not a production contract.
contract BiodiversityCreditGate {
    ICarbonCreditRating public immutable ratings;
    ICarbonCreditRating.Grade public immutable minGrade;

    error BelowMinGrade(ICarbonCreditRating.Grade actual, ICarbonCreditRating.Grade required);
    error StaleOrUnrated();

    event BiodiversityDepositAccepted(
        address indexed creditToken,
        uint256 indexed tokenId,
        ICarbonCreditRating.Grade grade,
        uint16 compositeBps
    );

    constructor(ICarbonCreditRating _ratings, ICarbonCreditRating.Grade _minGrade) {
        ratings = _ratings;
        minGrade = _minGrade;
    }

    /// @notice Gate a biodiversity credit deposit using the same meetsGrade()
    ///         interface used for carbon credits. The consumer does not need to
    ///         know which dimensions underlie the composite -- it only asks
    ///         "does this credit meet grade AA?" and gets a boolean answer.
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
