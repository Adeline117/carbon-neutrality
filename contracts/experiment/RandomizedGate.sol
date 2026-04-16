// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ICarbonCreditRating} from "../ICarbonCreditRating.sol";

/// @notice Minimal ERC-20-like interface for the underlying carbon credit.
interface IERC20Minimal {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function transfer(address to, uint256 amount) external returns (bool);
}

/// @notice Chainlink VRF v2 coordinator subset used by this contract. Defined
///         here to avoid an external dependency in the prototype; the mainnet
///         deployment imports from the chainlink/contracts package.
interface IVRFCoordinatorV2Plus {
    function requestRandomWords(
        bytes32 keyHash,
        uint64 subId,
        uint16 minConfirmations,
        uint32 callbackGasLimit,
        uint32 numWords
    ) external returns (uint256 requestId);
}

/// @title RandomizedGate
/// @notice Field-experiment retirement contract. When a user submits a
///         retirement request for a carbon credit, the contract randomly
///         assigns the user to one of two arms:
///
///           - TREATMENT: retirement only succeeds if the credit meets the
///                        configured minimum grade (quality gate enforced).
///           - CONTROL:   retirement always succeeds regardless of grade
///                        (no quality gate, BCT-style behavior).
///
///         Randomization is 50/50 and uses a commit-reveal pattern combined
///         with Chainlink VRF to prevent user-side manipulation:
///
///           1. commitRetire() — user locks in their credit and pays any fee;
///                               the contract requests VRF randomness and
///                               returns a requestId. Emits TreatmentAssigned
///                               once the VRF callback fires.
///
///           2. settleRetire() — anyone (usually the user) can call once the
///                               VRF word has arrived. The contract either
///                               retires (burns) the credit (both arms, gated
///                               or not) or refunds the credit (treatment
///                               below grade).
///
///         This design ensures:
///           - The arm assignment is verifiable and cannot be cherry-picked
///             by the user (pre-commitment to retire BEFORE arm is known).
///           - All retirement and assignment events are on-chain and
///             sufficient for intent-to-treat analysis.
///           - No off-chain trust is required for randomization integrity.
///
/// @dev Pre-registration: docs/field-experiment/pre-registration.md. Analysis
///      pipeline expects the events emitted below, in the order they are
///      defined. Do not reorder events without also updating the pipeline.
contract RandomizedGate {
    // ------------------------------------------------------------------
    // Configuration (immutable after construction)
    // ------------------------------------------------------------------
    ICarbonCreditRating public immutable ratings;
    ICarbonCreditRating.Grade public immutable minGrade;
    address public immutable vrfCoordinator;
    bytes32 public immutable vrfKeyHash;
    uint64 public immutable vrfSubId;

    // Experiment window: retirements are only accepted between these unix ts.
    // Hard-coded at deploy time to lock the sample frame for pre-registration.
    uint64 public immutable experimentStart;
    uint64 public immutable experimentEnd;

    // ------------------------------------------------------------------
    // Treatment assignment
    // ------------------------------------------------------------------
    enum Arm {
        PENDING, // VRF not yet arrived
        CONTROL, // no gate
        TREATMENT // gate enforced
    }

    struct Retirement {
        address user;
        address creditToken;
        uint256 tokenId;
        uint256 amount;
        Arm arm;
        uint64 commitTs;
        uint64 settleTs;
        bool settled;
        bool retired; // true if burn happened; false if refunded
        ICarbonCreditRating.Grade gradeAtSettle;
    }

    // requestId => retirement
    mapping(uint256 => Retirement) public retirements;
    // user => number of retirements they have attempted (for auditing)
    mapping(address => uint64) public userRetirementCount;

    // ------------------------------------------------------------------
    // Aggregate counters (for quick on-chain audit; ground truth is events)
    // ------------------------------------------------------------------
    uint64 public totalRetirements;
    uint64 public treatmentAssigned;
    uint64 public controlAssigned;
    uint64 public treatmentSucceeded;
    uint64 public treatmentRefused;
    uint64 public controlSucceeded;

    // ------------------------------------------------------------------
    // Errors
    // ------------------------------------------------------------------
    error NotInExperimentWindow();
    error AlreadySettled();
    error NotCommitted();
    error ArmStillPending();
    error OnlyVRFCoordinator();
    error TransferFailed();

    // ------------------------------------------------------------------
    // Events (analysis-pipeline contract)
    // ------------------------------------------------------------------
    /// @notice Emitted when the VRF callback lands and the user is assigned
    ///         to an arm. This is the first analysis event per retirement.
    event TreatmentAssigned(
        uint256 indexed requestId,
        address indexed user,
        address indexed creditToken,
        uint256 tokenId,
        uint256 amount,
        Arm arm,
        uint64 commitTs
    );

    /// @notice Emitted on successful settlement (either retirement or refund).
    ///         Analysis pipeline joins TreatmentAssigned to RetirementCompleted
    ///         on requestId and computes quality-of-retirement outcomes.
    event RetirementCompleted(
        uint256 indexed requestId,
        address indexed user,
        address indexed creditToken,
        uint256 tokenId,
        uint256 amount,
        Arm arm,
        bool retired,
        ICarbonCreditRating.Grade gradeAtSettle,
        uint16 compositeBpsAtSettle,
        uint64 settleTs
    );

    /// @notice Emitted when a user's retirement is committed (before VRF).
    ///         Used to reconstruct the commitment order and detect attrition.
    event RetirementCommitted(
        uint256 indexed requestId,
        address indexed user,
        address indexed creditToken,
        uint256 tokenId,
        uint256 amount,
        uint64 commitTs
    );

    // ------------------------------------------------------------------
    // Constructor
    // ------------------------------------------------------------------
    constructor(
        ICarbonCreditRating _ratings,
        ICarbonCreditRating.Grade _minGrade,
        address _vrfCoordinator,
        bytes32 _keyHash,
        uint64 _subId,
        uint64 _start,
        uint64 _end
    ) {
        require(_end > _start, "bad window");
        ratings = _ratings;
        minGrade = _minGrade;
        vrfCoordinator = _vrfCoordinator;
        vrfKeyHash = _keyHash;
        vrfSubId = _subId;
        experimentStart = _start;
        experimentEnd = _end;
    }

    // ------------------------------------------------------------------
    // Step 1: Commit
    // ------------------------------------------------------------------
    /// @notice Commit a retirement. Pulls the credit into escrow, requests
    ///         VRF randomness, and returns the requestId. The user cannot
    ///         know their arm until VRF resolves.
    function commitRetire(address creditToken, uint256 tokenId, uint256 amount)
        external
        returns (uint256 requestId)
    {
        if (block.timestamp < experimentStart || block.timestamp >= experimentEnd) {
            revert NotInExperimentWindow();
        }

        // Pull credit into escrow BEFORE arm is known.
        bool ok = IERC20Minimal(creditToken).transferFrom(msg.sender, address(this), amount);
        if (!ok) revert TransferFailed();

        // Request a single random word. In tests we accept a mock coordinator
        // that fulfills synchronously via rawFulfillRandomWords.
        requestId = IVRFCoordinatorV2Plus(vrfCoordinator).requestRandomWords(
            vrfKeyHash,
            vrfSubId,
            3, // minConfirmations; irrelevant in tests
            200000, // callbackGasLimit
            1
        );

        retirements[requestId] = Retirement({
            user: msg.sender,
            creditToken: creditToken,
            tokenId: tokenId,
            amount: amount,
            arm: Arm.PENDING,
            commitTs: uint64(block.timestamp),
            settleTs: 0,
            settled: false,
            retired: false,
            gradeAtSettle: ICarbonCreditRating.Grade.B
        });

        userRetirementCount[msg.sender] += 1;
        totalRetirements += 1;

        emit RetirementCommitted(requestId, msg.sender, creditToken, tokenId, amount, uint64(block.timestamp));
    }

    // ------------------------------------------------------------------
    // VRF callback (must match Chainlink's interface name)
    // ------------------------------------------------------------------
    /// @notice Chainlink VRF v2 callback. Only the coordinator may call.
    ///         Uses the first returned word mod 2 as arm assignment.
    function rawFulfillRandomWords(uint256 requestId, uint256[] calldata randomWords) external {
        if (msg.sender != vrfCoordinator) revert OnlyVRFCoordinator();

        Retirement storage r = retirements[requestId];
        if (r.user == address(0)) revert NotCommitted();
        // If already assigned or settled, this is a duplicate callback; no-op.
        if (r.arm != Arm.PENDING || r.settled) return;

        // 50/50 split by least significant bit of the VRF word.
        Arm assigned = (randomWords[0] & 1 == 1) ? Arm.TREATMENT : Arm.CONTROL;
        r.arm = assigned;

        if (assigned == Arm.TREATMENT) {
            treatmentAssigned += 1;
        } else {
            controlAssigned += 1;
        }

        emit TreatmentAssigned(
            requestId,
            r.user,
            r.creditToken,
            r.tokenId,
            r.amount,
            assigned,
            r.commitTs
        );
    }

    // ------------------------------------------------------------------
    // Step 2: Settle
    // ------------------------------------------------------------------
    /// @notice Settle a committed retirement once VRF has resolved. In the
    ///         control arm the credit is always retired (burned by transfer
    ///         to the zero address). In the treatment arm, the rating is
    ///         checked and the credit is either retired (meets grade) or
    ///         refunded to the user (below grade).
    function settleRetire(uint256 requestId) external {
        Retirement storage r = retirements[requestId];
        if (r.user == address(0)) revert NotCommitted();
        if (r.settled) revert AlreadySettled();
        if (r.arm == Arm.PENDING) revert ArmStillPending();

        // Read rating at settlement time. We record grade/composite even if
        // the credit is ultimately refunded, so the analysis pipeline can
        // study selection-on-unrated and grade-boundary RD.
        ICarbonCreditRating.Grade gradeAtSettle = ICarbonCreditRating.Grade.B;
        uint16 compositeBps = 0;
        bool rated;
        try ratings.ratingOf(r.creditToken, r.tokenId) returns (ICarbonCreditRating.Rating memory got) {
            gradeAtSettle = got.finalGrade;
            compositeBps = got.compositeBps;
            rated = true;
        } catch {
            rated = false;
        }

        bool shouldRetire;
        if (r.arm == Arm.CONTROL) {
            shouldRetire = true; // control arm always retires
        } else {
            // Treatment: retire iff rated, fresh, and meets grade
            if (!rated) {
                shouldRetire = false;
            } else if (ratings.isStale(r.creditToken, r.tokenId)) {
                shouldRetire = false;
            } else {
                shouldRetire = uint8(gradeAtSettle) >= uint8(minGrade);
            }
        }

        r.settled = true;
        r.retired = shouldRetire;
        r.settleTs = uint64(block.timestamp);
        r.gradeAtSettle = gradeAtSettle;

        if (shouldRetire) {
            // Burn by transfer to address(0xdead). Some tokens reject
            // transfers to 0x0; we use a standard burn sink.
            bool ok = IERC20Minimal(r.creditToken).transfer(address(0xdEaD), r.amount);
            if (!ok) revert TransferFailed();

            if (r.arm == Arm.TREATMENT) treatmentSucceeded += 1;
            else controlSucceeded += 1;
        } else {
            // Refund to user (treatment below grade, or stale/unrated)
            bool ok = IERC20Minimal(r.creditToken).transfer(r.user, r.amount);
            if (!ok) revert TransferFailed();

            treatmentRefused += 1;
        }

        emit RetirementCompleted(
            requestId,
            r.user,
            r.creditToken,
            r.tokenId,
            r.amount,
            r.arm,
            shouldRetire,
            gradeAtSettle,
            compositeBps,
            uint64(block.timestamp)
        );
    }

    // ------------------------------------------------------------------
    // Views
    // ------------------------------------------------------------------
    /// @notice Convenience accessor used by the analysis pipeline. Returns
    ///         (arm, settled, retired, gradeAtSettle).
    function armOf(uint256 requestId)
        external
        view
        returns (Arm, bool, bool, ICarbonCreditRating.Grade)
    {
        Retirement memory r = retirements[requestId];
        return (r.arm, r.settled, r.retired, r.gradeAtSettle);
    }

    /// @notice Raw balance of the balance ratio of treatment to total. Used
    ///         for quick-look balance checks on-chain; full chi-square is
    ///         done off-chain.
    function treatmentShareBps() external view returns (uint16) {
        uint64 assigned = treatmentAssigned + controlAssigned;
        if (assigned == 0) return 0;
        return uint16((uint256(treatmentAssigned) * 10000) / assigned);
    }
}
