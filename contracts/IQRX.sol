// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ICarbonCreditRating} from "./ICarbonCreditRating.sol";

/// @title IQRX - Quality-Revealing Exchange
/// @notice Interface for the QRX mechanism: a bonded deposit scheme that
///         provably resists Akerlof (1970) adverse selection by forcing
///         depositors of tokenized carbon credits to post a bond proportional
///         to the quality they claim.
///
/// @dev    The core idea, stated informally:
///
///           Let q ∈ {B, BB, BBB, A, AA, AAA} be the depositor's claimed grade.
///           Let a be the tonnage deposited and b the bond posted (in a numeraire
///           token — USDC for the reference deployment).
///
///           The contract enforces a per-grade bond schedule b ≥ B(q, a).
///           The bond is slashed post-hoc if an oracle/arbiter certifies a true
///           grade q* < q. The slash fraction is
///
///               slash(q, q*) = max(0, rank(q) − rank(q*)) / 5
///
///           which scales linearly from 0 (truthful or over-strict) to 1 (claim
///           AAA, reveal B).
///
///           Under reasonable monotonicity assumptions (see docs/qrx-paper/
///           formal-model.md), this produces a **separating equilibrium**:
///           each quality type self-selects into a distinct (claim, bond)
///           pair. The pooling equilibrium that dooms BCT (LI=0.72, see
///           data/lemons-index/systematic_scan_results.md) is ruled out.
///
/// @dev    Design notes:
///
///           * QRX is **orthogonal** to a pre-deposit quality rating (see
///             CarbonCreditRating). Rating is what the rater thinks about a
///             credit before deposit; QRX's true grade is what the MRV oracle
///             certifies after the fact, possibly following a challenge.
///             A pool can compose the two: require (rating ≥ k) AND (bond ≥
///             B(claimed, amount)).
///
///           * The challenge window is open-ended until resolve() is called.
///             In production this would be bounded (e.g. 30 days) to let
///             honest depositors reclaim bonds promptly. The reference
///             implementation exposes the window as an immutable parameter.
///
///           * Bond is held in a single numeraire ERC-20 (bondToken) to keep
///             the mechanism currency-neutral with respect to the credit
///             being deposited.
interface IQRX {
    // ----------------------------------------------------------------------
    // Types
    // ----------------------------------------------------------------------

    /// @notice Lifecycle state of a single deposit.
    enum Status {
        None,        // 0 — default for unknown depositId
        Active,      // 1 — deposited, no challenge open
        Challenged,  // 2 — challenge raised, awaiting resolve()
        Resolved,    // 3 — resolved by arbiter; bond partially slashed
        Retired      // 4 — depositor withdrew with full (or post-slash) bond
    }

    /// @notice Record of a single QRX deposit.
    struct Deposit {
        address depositor;
        address creditToken;
        uint256 amount;                              // tonnes (in credit-token units)
        ICarbonCreditRating.Grade claimedGrade;      // depositor's claim
        ICarbonCreditRating.Grade trueGrade;         // oracle-certified, 0 until resolve()
        uint256 bond;                                // bond posted (in bondToken units)
        uint256 bondRemaining;                       // bond − slashed_so_far
        Status status;
        address challenger;                          // 0x0 unless Status ≥ Challenged
        bytes32 evidenceHash;                        // hash of challenge evidence
        uint64 depositedAt;                          // unix seconds
        uint64 challengedAt;                         // 0 if never challenged
        uint64 resolvedAt;                           // 0 if not yet resolved
    }

    // ----------------------------------------------------------------------
    // Events
    // ----------------------------------------------------------------------

    event Deposited(
        uint256 indexed depositId,
        address indexed depositor,
        address indexed creditToken,
        uint256 amount,
        ICarbonCreditRating.Grade claimedGrade,
        uint256 bond
    );

    event Challenged(
        uint256 indexed depositId,
        address indexed challenger,
        bytes32 evidenceHash
    );

    event Resolved(
        uint256 indexed depositId,
        ICarbonCreditRating.Grade claimedGrade,
        ICarbonCreditRating.Grade trueGrade,
        uint256 slashed,
        uint256 bondRemaining
    );

    event Retired(
        uint256 indexed depositId,
        address indexed depositor,
        uint256 bondReturned
    );

    event SlashDistributed(
        uint256 indexed depositId,
        address indexed challenger,
        uint256 challengerReward,
        address indexed treasury,
        uint256 treasuryShare
    );

    // ----------------------------------------------------------------------
    // Parameters (read-only views)
    // ----------------------------------------------------------------------

    /// @notice Bond requirement (in bondToken units) for a given (grade, amount).
    ///         Must be non-decreasing in both arguments. See QRX.sol for the
    ///         reference schedule b ≥ bondRatePerTonne[grade] × amount.
    function bondRequired(
        ICarbonCreditRating.Grade claimedGrade,
        uint256 amount
    ) external view returns (uint256);

    /// @notice Returns the slash amount for a given bond under (claim, true).
    ///         Slash is linear in the grade gap: slash = bond × max(0, rank(claim) − rank(true)) / 5.
    function slashAmount(
        uint256 bond,
        ICarbonCreditRating.Grade claimedGrade,
        ICarbonCreditRating.Grade trueGrade
    ) external pure returns (uint256);

    /// @notice Fetch a full deposit record. Reverts if depositId is unknown.
    function depositOf(uint256 depositId) external view returns (Deposit memory);

    /// @notice Total number of deposits ever created.
    function depositCount() external view returns (uint256);

    // ----------------------------------------------------------------------
    // Mutating entry points
    // ----------------------------------------------------------------------

    /// @notice Deposit `amount` of `creditToken` at a claimed grade and post a bond.
    /// @dev The caller must have approved both `creditToken` (for `amount`)
    ///      and the bondToken (for at least `bondRequired(claimedGrade, amount)`).
    /// @return depositId Assigned sequentially from 0.
    function deposit(
        address creditToken,
        uint256 amount,
        ICarbonCreditRating.Grade claimedGrade,
        uint256 bondAmount
    ) external returns (uint256 depositId);

    /// @notice Release remaining bond to depositor. Callable only while status
    ///         ∈ {Active, Resolved}. Under a resolved status the returned
    ///         amount is (bond − slashed).
    function retire(uint256 depositId) external;

    /// @notice Raise a challenge against an Active deposit. Anyone may call.
    ///         The evidence hash points off-chain to MRV evidence of a lower
    ///         true grade than the claim.
    function challenge(uint256 depositId, bytes32 evidenceHash) external;

    /// @notice Oracle/arbiter sets the true grade and slashes the bond.
    ///         Only callable on Challenged deposits, only by the arbiter.
    function resolve(uint256 depositId, ICarbonCreditRating.Grade trueGrade) external;
}
