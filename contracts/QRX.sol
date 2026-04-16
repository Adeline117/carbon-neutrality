// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IQRX} from "./IQRX.sol";
import {ICarbonCreditRating} from "./ICarbonCreditRating.sol";

/// @notice Minimal ERC-20-like interface; matches QualityGatedPool to avoid
///         pulling in OpenZeppelin. Production deployment should swap in
///         SafeERC20.
interface IERC20Minimal {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

/// @title QRX — Quality-Revealing Exchange
/// @notice Reference implementation of the bonded deposit mechanism that
///         breaks the Akerlof pooling equilibrium in tokenized carbon credit
///         pools. See docs/qrx-paper/draft.md for the full motivation and
///         IQRX.sol for the interface-level docs.
///
/// @dev    Bond schedule. The reference bond requirement is
///
///             b ≥ bondRatePerTonne[claimedGrade] × amount
///
///         where bondRatePerTonne is set at construction time. The schedule
///         must be strictly increasing in grade: posting a AAA bond is more
///         expensive per tonne than posting a B bond. This is what makes the
///         claim credible.
///
///         Slash function. At resolution, if trueGrade < claimedGrade, we
///         slash
///
///             slashed = bond × (rank(claimedGrade) − rank(trueGrade)) / 5
///
///         The denominator is 5 because the grade enum has 6 levels (B..AAA)
///         and thus 5 possible gaps. This linear schedule is the simplest
///         incentive-compatible design; nonlinear (convex) schedules that
///         penalise larger gaps harder are a natural extension.
///
///         Slash distribution. Slashed bonds are split between the challenger
///         (as a bounty for providing evidence) and a treasury (used to
///         compensate downstream buyers / fund MRV infrastructure). The
///         default split is 50/50.
///
///         Threat model. See docs/qrx-paper/draft.md §Threat Model for a full
///         accounting; the test file exercises sybil, MEV, and griefing
///         scenarios.
contract QRX is IQRX {
    // ------------------------------------------------------------------
    // Immutable config
    // ------------------------------------------------------------------

    /// @notice ERC-20 used for bonds (e.g. USDC). Using a single numeraire
    ///         keeps bond size comparable across credit types.
    address public immutable bondToken;

    /// @notice Arbiter authorised to resolve challenges. In the reference
    ///         deployment this is the multisig operating the MRV oracle;
    ///         production deployments would use an Optimistic-Oracle–style
    ///         dispute system (UMA, Kleros) instead.
    address public immutable arbiter;

    /// @notice Recipient of the non-bounty portion of slashed bonds.
    address public immutable treasury;

    /// @notice Basis points (out of 10000) of slashed bond sent to challenger.
    ///         Default 5000 (50%). Higher → stronger challenger incentive but
    ///         larger griefing surface.
    uint16 public immutable challengerBountyBps;

    /// @notice Bond rate per tonne of claimed-grade credit, in bondToken
    ///         smallest units. Indexed by Grade enum value (B=0 .. AAA=5).
    ///         MUST be non-decreasing — the constructor enforces this.
    uint256[6] public bondRatePerTonne;

    // ------------------------------------------------------------------
    // Storage
    // ------------------------------------------------------------------

    /// @dev sequence of deposits; depositId ∈ [0, _count).
    uint256 private _count;
    mapping(uint256 => Deposit) private _deposits;

    // ------------------------------------------------------------------
    // Errors
    // ------------------------------------------------------------------

    error NotArbiter();
    error NotDepositor();
    error BondBelowMinimum(uint256 provided, uint256 required);
    error BondRatesNotMonotone(uint256 atIndex);
    error TransferFailed();
    error WrongStatus(Status have, Status expected);
    error UnknownDeposit();
    error InvalidTrueGrade();
    error BadConfig();
    error GradeOutOfRange(uint8 g);

    // ------------------------------------------------------------------
    // Constructor
    // ------------------------------------------------------------------

    /// @param _bondToken              ERC-20 used for the bond.
    /// @param _arbiter                Authorised to resolve challenges.
    /// @param _treasury               Receives the non-bounty slash portion.
    /// @param _challengerBountyBps    Basis-points share to challenger (≤10000).
    /// @param _bondRatePerTonne       Non-decreasing bond-per-tonne schedule
    ///                                indexed by Grade (B=0 .. AAA=5).
    constructor(
        address _bondToken,
        address _arbiter,
        address _treasury,
        uint16 _challengerBountyBps,
        uint256[6] memory _bondRatePerTonne
    ) {
        if (_bondToken == address(0)) revert BadConfig();
        if (_arbiter == address(0)) revert BadConfig();
        if (_treasury == address(0)) revert BadConfig();
        if (_challengerBountyBps > 10000) revert BadConfig();

        // Enforce strict monotonicity so that higher-grade claims always cost
        // strictly more per tonne than lower-grade claims — otherwise the
        // separating equilibrium collapses.
        for (uint256 i = 1; i < 6; i++) {
            if (_bondRatePerTonne[i] <= _bondRatePerTonne[i - 1]) {
                revert BondRatesNotMonotone(i);
            }
        }

        bondToken = _bondToken;
        arbiter = _arbiter;
        treasury = _treasury;
        challengerBountyBps = _challengerBountyBps;
        bondRatePerTonne = _bondRatePerTonne;
    }

    // ------------------------------------------------------------------
    // Views
    // ------------------------------------------------------------------

    /// @inheritdoc IQRX
    function bondRequired(
        ICarbonCreditRating.Grade claimedGrade,
        uint256 amount
    ) public view returns (uint256) {
        uint8 g = uint8(claimedGrade);
        if (g > 5) revert GradeOutOfRange(g);
        return bondRatePerTonne[g] * amount;
    }

    /// @inheritdoc IQRX
    function slashAmount(
        uint256 bond,
        ICarbonCreditRating.Grade claimedGrade,
        ICarbonCreditRating.Grade trueGrade
    ) public pure returns (uint256) {
        uint8 cg = uint8(claimedGrade);
        uint8 tg = uint8(trueGrade);
        if (cg > 5 || tg > 5) revert GradeOutOfRange(cg > 5 ? cg : tg);
        if (tg >= cg) return 0;
        uint256 gap = uint256(cg - tg);
        // slashed = bond * gap / 5 (5 = max possible gap between B and AAA)
        return (bond * gap) / 5;
    }

    /// @inheritdoc IQRX
    function depositOf(uint256 depositId) external view returns (Deposit memory) {
        Deposit memory d = _deposits[depositId];
        if (d.status == Status.None) revert UnknownDeposit();
        return d;
    }

    /// @inheritdoc IQRX
    function depositCount() external view returns (uint256) {
        return _count;
    }

    // ------------------------------------------------------------------
    // Mutating entry points
    // ------------------------------------------------------------------

    /// @inheritdoc IQRX
    function deposit(
        address creditToken,
        uint256 amount,
        ICarbonCreditRating.Grade claimedGrade,
        uint256 bondAmount
    ) external returns (uint256 depositId) {
        uint8 g = uint8(claimedGrade);
        if (g > 5) revert GradeOutOfRange(g);
        if (amount == 0) revert BadConfig();

        uint256 minBond = bondRatePerTonne[g] * amount;
        if (bondAmount < minBond) revert BondBelowMinimum(bondAmount, minBond);

        // Pull credit and bond. Credit stays with QRX for the lifetime of
        // the deposit so that retire() can release it back.
        if (!IERC20Minimal(creditToken).transferFrom(msg.sender, address(this), amount)) {
            revert TransferFailed();
        }
        if (!IERC20Minimal(bondToken).transferFrom(msg.sender, address(this), bondAmount)) {
            revert TransferFailed();
        }

        depositId = _count++;
        _deposits[depositId] = Deposit({
            depositor: msg.sender,
            creditToken: creditToken,
            amount: amount,
            claimedGrade: claimedGrade,
            trueGrade: ICarbonCreditRating.Grade.B, // placeholder until resolve()
            bond: bondAmount,
            bondRemaining: bondAmount,
            status: Status.Active,
            challenger: address(0),
            evidenceHash: bytes32(0),
            depositedAt: uint64(block.timestamp),
            challengedAt: 0,
            resolvedAt: 0
        });

        emit Deposited(depositId, msg.sender, creditToken, amount, claimedGrade, bondAmount);
    }

    /// @inheritdoc IQRX
    function challenge(uint256 depositId, bytes32 evidenceHash) external {
        Deposit storage d = _deposits[depositId];
        if (d.status != Status.Active) revert WrongStatus(d.status, Status.Active);

        d.status = Status.Challenged;
        d.challenger = msg.sender;
        d.evidenceHash = evidenceHash;
        d.challengedAt = uint64(block.timestamp);

        emit Challenged(depositId, msg.sender, evidenceHash);
    }

    /// @inheritdoc IQRX
    function resolve(uint256 depositId, ICarbonCreditRating.Grade trueGrade) external {
        if (msg.sender != arbiter) revert NotArbiter();

        Deposit storage d = _deposits[depositId];
        if (d.status != Status.Challenged) revert WrongStatus(d.status, Status.Challenged);
        if (uint8(trueGrade) > 5) revert InvalidTrueGrade();

        uint256 slashed = slashAmount(d.bond, d.claimedGrade, trueGrade);
        if (slashed > d.bondRemaining) slashed = d.bondRemaining; // defensive

        d.trueGrade = trueGrade;
        d.bondRemaining -= slashed;
        d.status = Status.Resolved;
        d.resolvedAt = uint64(block.timestamp);

        emit Resolved(depositId, d.claimedGrade, trueGrade, slashed, d.bondRemaining);

        if (slashed > 0) {
            _distributeSlash(depositId, d.challenger, slashed);
        }
    }

    /// @inheritdoc IQRX
    function retire(uint256 depositId) external {
        Deposit storage d = _deposits[depositId];
        if (d.status != Status.Active && d.status != Status.Resolved) {
            revert WrongStatus(d.status, Status.Active);
        }
        if (msg.sender != d.depositor) revert NotDepositor();

        uint256 bondToReturn = d.bondRemaining;

        // Effects before interactions.
        d.bondRemaining = 0;
        d.status = Status.Retired;

        // Return the carbon credit amount back to the depositor (this models
        // on-chain retirement: the depositor regains custody to then retire
        // via the credit token's own retire path).
        if (!IERC20Minimal(d.creditToken).transfer(d.depositor, d.amount)) {
            revert TransferFailed();
        }

        if (bondToReturn > 0) {
            if (!IERC20Minimal(bondToken).transfer(d.depositor, bondToReturn)) {
                revert TransferFailed();
            }
        }

        emit Retired(depositId, d.depositor, bondToReturn);
    }

    // ------------------------------------------------------------------
    // Internals
    // ------------------------------------------------------------------

    function _distributeSlash(uint256 depositId, address challenger, uint256 slashed) private {
        uint256 bounty = (slashed * challengerBountyBps) / 10000;
        uint256 treasuryShare = slashed - bounty;

        if (bounty > 0 && challenger != address(0)) {
            if (!IERC20Minimal(bondToken).transfer(challenger, bounty)) revert TransferFailed();
        } else {
            // No challenger (shouldn't happen in the normal flow because
            // resolve() only runs on Challenged deposits, but be defensive).
            treasuryShare += bounty;
            bounty = 0;
        }

        if (treasuryShare > 0) {
            if (!IERC20Minimal(bondToken).transfer(treasury, treasuryShare)) revert TransferFailed();
        }

        emit SlashDistributed(depositId, challenger, bounty, treasury, treasuryShare);
    }
}
