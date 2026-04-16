// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// Foundry test suite for QRX (Quality-Revealing Exchange). Run with:
//   forge test --match-contract QRX
//
// Test plan
// ---------
//   1. Happy path:
//        a. deposit() at claimed grade, bond held
//        b. retire() without challenge returns full bond
//   2. Challenge path:
//        a. challenge() by anyone transitions status
//        b. resolve() slashes proportional to gap
//        c. retire() after resolve returns only bondRemaining
//   3. Slashing function correctness:
//        a. No slash when trueGrade ≥ claimedGrade
//        b. Linear scaling across grade gaps (1/5, 2/5, ... 5/5)
//   4. Incentive / payoff tests:
//        a. Truthful high-quality depositor payoff == bond returned in full
//        b. Overclaim depositor payoff == bond − slash < bond
//   5. Sybil resistance:
//        a. N wallets each posting bond b_i face total slash Σ slash(b_i)
//        b. Splitting one deposit into K pieces does not reduce expected slash
//   6. MEV / bond-lending:
//        a. Bond cannot be withdrawn while Challenged
//        b. Challenger cannot self-resolve
//   7. Access control:
//        a. Non-arbiter cannot resolve()
//        b. Non-depositor cannot retire()
//   8. Constructor validation:
//        a. Non-monotone bond rates revert
//        b. Zero addresses revert
//   9. Gas benchmarks (explicit gas-labelled tests, picked up by --gas-report)
//
// The suite uses forge-std/Test for prank/expectRevert/warp; the CarbonCreditRating
// test file (CarbonCreditRating.t.sol) is bare-bones to mirror on-chain behaviour
// but we rely on the richer Test helpers here to keep the challenge matrix
// concise.

import {Test, console} from "forge-std/Test.sol";

import {QRX} from "../QRX.sol";
import {IQRX} from "../IQRX.sol";
import {ICarbonCreditRating} from "../ICarbonCreditRating.sol";
import {MockCarbonCredit} from "../MockCarbonCredit.sol";

contract QRXTest is Test {
    // ---------------------------------------------------------------
    // Fixtures
    // ---------------------------------------------------------------

    QRX internal qrx;
    MockCarbonCredit internal credit;
    MockCarbonCredit internal bondUsd; // "USDC" stand-in

    address internal constant ARBITER = address(0xA1B);
    address internal constant TREASURY = address(0x7EA);
    address internal constant ALICE = address(0xA11CE);
    address internal constant BOB = address(0xB0B);
    address internal constant CHALLENGER = address(0xC1A1);

    // Bond rates per tonne, indexed by Grade (B=0..AAA=5). Chosen so that
    // per-tonne AAA bond is 10x B bond — large enough to be materially
    // costly to overclaim, small enough that tests don't overflow.
    //
    // In the paper we calibrate these to the empirical BCT retirement-delta
    // (see data/qrx/counterfactual_replay.py).
    //
    // Values are in bondToken smallest units per tonne.
    uint256 internal constant RATE_B   = 1e6;   // 1.00 USDC / tonne
    uint256 internal constant RATE_BB  = 2e6;   // 2.00
    uint256 internal constant RATE_BBB = 4e6;   // 4.00
    uint256 internal constant RATE_A   = 7e6;   // 7.00
    uint256 internal constant RATE_AA  = 10e6;  // 10.00
    uint256 internal constant RATE_AAA = 15e6;  // 15.00

    function setUp() public {
        credit = new MockCarbonCredit("BCT-clone", "BCT", address(this));
        bondUsd = new MockCarbonCredit("MockUSDC", "USDC", address(this));

        uint256[6] memory rates = [RATE_B, RATE_BB, RATE_BBB, RATE_A, RATE_AA, RATE_AAA];
        qrx = new QRX(
            address(bondUsd),
            ARBITER,
            TREASURY,
            5000, // 50% challenger bounty
            rates
        );

        // Fund Alice and Bob with credits + bond tokens.
        credit.mint(ALICE, 1_000_000);
        credit.mint(BOB, 1_000_000);
        bondUsd.mint(ALICE, 1_000_000_000e6);
        bondUsd.mint(BOB, 1_000_000_000e6);

        // Pre-approve the QRX contract from both parties.
        vm.prank(ALICE);
        credit.approve(address(qrx), type(uint256).max);
        vm.prank(ALICE);
        bondUsd.approve(address(qrx), type(uint256).max);

        vm.prank(BOB);
        credit.approve(address(qrx), type(uint256).max);
        vm.prank(BOB);
        bondUsd.approve(address(qrx), type(uint256).max);

        vm.warp(1_700_000_000);
    }

    // ---------------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------------

    function _deposit(address from, ICarbonCreditRating.Grade g, uint256 amount) internal returns (uint256) {
        uint256 bond = qrx.bondRequired(g, amount);
        vm.prank(from);
        return qrx.deposit(address(credit), amount, g, bond);
    }

    function _depositWithBond(
        address from,
        ICarbonCreditRating.Grade g,
        uint256 amount,
        uint256 bond
    ) internal returns (uint256) {
        vm.prank(from);
        return qrx.deposit(address(credit), amount, g, bond);
    }

    // ==============================================================
    // 1. Happy path
    // ==============================================================

    function test_happyPath_depositReturnsCreditAndBond() public {
        uint256 amount = 100;
        uint256 aliceCredit0 = credit.balanceOf(ALICE);
        uint256 aliceBond0 = bondUsd.balanceOf(ALICE);

        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.AA, amount);

        // Credit moved to QRX.
        assertEq(credit.balanceOf(address(qrx)), amount);
        assertEq(credit.balanceOf(ALICE), aliceCredit0 - amount);

        // Bond moved to QRX.
        uint256 expectedBond = RATE_AA * amount;
        assertEq(bondUsd.balanceOf(address(qrx)), expectedBond);
        assertEq(bondUsd.balanceOf(ALICE), aliceBond0 - expectedBond);

        // Deposit record.
        IQRX.Deposit memory d = qrx.depositOf(id);
        assertEq(d.depositor, ALICE);
        assertEq(uint256(d.amount), amount);
        assertEq(uint8(d.claimedGrade), uint8(ICarbonCreditRating.Grade.AA));
        assertEq(d.bond, expectedBond);
        assertEq(d.bondRemaining, expectedBond);
        assertEq(uint8(d.status), uint8(IQRX.Status.Active));
    }

    function test_happyPath_retireReturnsFullBond() public {
        uint256 amount = 100;
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.AA, amount);

        uint256 aliceCredit0 = credit.balanceOf(ALICE);
        uint256 aliceBond0 = bondUsd.balanceOf(ALICE);
        uint256 expectedBond = RATE_AA * amount;

        vm.prank(ALICE);
        qrx.retire(id);

        assertEq(credit.balanceOf(ALICE), aliceCredit0 + amount, "credit returned");
        assertEq(bondUsd.balanceOf(ALICE), aliceBond0 + expectedBond, "bond returned in full");

        IQRX.Deposit memory d = qrx.depositOf(id);
        assertEq(uint8(d.status), uint8(IQRX.Status.Retired));
        assertEq(d.bondRemaining, 0);
    }

    // ==============================================================
    // 2. Challenge path
    // ==============================================================

    function test_challenge_transitionsStatus() public {
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.AAA, 100);

        vm.prank(CHALLENGER);
        qrx.challenge(id, keccak256("evidence:mrv-report-v1"));

        IQRX.Deposit memory d = qrx.depositOf(id);
        assertEq(uint8(d.status), uint8(IQRX.Status.Challenged));
        assertEq(d.challenger, CHALLENGER);
    }

    function test_challenge_onlyActiveMayBeChallenged() public {
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.A, 10);
        vm.prank(CHALLENGER);
        qrx.challenge(id, bytes32("evidence"));

        // Second challenge on a Challenged deposit should revert.
        vm.prank(BOB);
        vm.expectRevert(
            abi.encodeWithSelector(QRX.WrongStatus.selector, IQRX.Status.Challenged, IQRX.Status.Active)
        );
        qrx.challenge(id, bytes32("evidence2"));
    }

    function test_resolve_slashesProportionalToGap() public {
        // Claim AAA (rank 5), reveal B (rank 0). Full slash.
        uint256 amount = 100;
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.AAA, amount);
        uint256 bond = RATE_AAA * amount;

        vm.prank(CHALLENGER);
        qrx.challenge(id, bytes32("e"));

        uint256 treasury0 = bondUsd.balanceOf(TREASURY);
        uint256 challenger0 = bondUsd.balanceOf(CHALLENGER);

        vm.prank(ARBITER);
        qrx.resolve(id, ICarbonCreditRating.Grade.B);

        IQRX.Deposit memory d = qrx.depositOf(id);
        assertEq(uint8(d.status), uint8(IQRX.Status.Resolved));
        assertEq(d.bondRemaining, 0, "full slash on 5-grade gap");

        // 50/50 split between challenger and treasury.
        uint256 expectedBounty = bond / 2;
        uint256 expectedTreasury = bond - expectedBounty;
        assertEq(bondUsd.balanceOf(CHALLENGER) - challenger0, expectedBounty);
        assertEq(bondUsd.balanceOf(TREASURY) - treasury0, expectedTreasury);
    }

    function test_resolve_partialSlashOneGrade() public {
        // Claim AA (4), reveal A (3). Gap = 1 → slash = bond/5.
        uint256 amount = 100;
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.AA, amount);
        uint256 bond = RATE_AA * amount;

        vm.prank(CHALLENGER);
        qrx.challenge(id, bytes32("e"));

        vm.prank(ARBITER);
        qrx.resolve(id, ICarbonCreditRating.Grade.A);

        IQRX.Deposit memory d = qrx.depositOf(id);
        uint256 expectedSlash = bond / 5;
        assertEq(d.bondRemaining, bond - expectedSlash);
    }

    function test_resolve_noSlashWhenTrueGradeEqualsClaim() public {
        uint256 amount = 100;
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.A, amount);
        uint256 bond = RATE_A * amount;

        vm.prank(CHALLENGER);
        qrx.challenge(id, bytes32("e"));
        vm.prank(ARBITER);
        qrx.resolve(id, ICarbonCreditRating.Grade.A);

        IQRX.Deposit memory d = qrx.depositOf(id);
        assertEq(d.bondRemaining, bond, "no slash when true == claimed");
    }

    function test_resolve_noSlashWhenTrueGradeExceedsClaim() public {
        // Under-claim: depositor claims A but true grade is AAA. No slash.
        uint256 amount = 100;
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.A, amount);
        uint256 bond = RATE_A * amount;

        vm.prank(CHALLENGER);
        qrx.challenge(id, bytes32("e"));
        vm.prank(ARBITER);
        qrx.resolve(id, ICarbonCreditRating.Grade.AAA);

        IQRX.Deposit memory d = qrx.depositOf(id);
        assertEq(d.bondRemaining, bond, "under-claim: no slash");
    }

    function test_retire_afterSlashReturnsRemainder() public {
        uint256 amount = 100;
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.AAA, amount);
        uint256 bond = RATE_AAA * amount;

        vm.prank(CHALLENGER);
        qrx.challenge(id, bytes32("e"));
        vm.prank(ARBITER);
        qrx.resolve(id, ICarbonCreditRating.Grade.BBB);
        // gap = 5 − 2 = 3, slash = bond * 3/5

        uint256 expectedSlash = (bond * 3) / 5;
        uint256 expectedRemaining = bond - expectedSlash;

        uint256 aliceBond0 = bondUsd.balanceOf(ALICE);
        vm.prank(ALICE);
        qrx.retire(id);

        assertEq(bondUsd.balanceOf(ALICE) - aliceBond0, expectedRemaining);
    }

    // ==============================================================
    // 3. Slashing function correctness (pure)
    // ==============================================================

    function test_slashAmount_zeroWhenTrueGradeAtLeastClaim() public view {
        uint256 b = 1000;
        assertEq(qrx.slashAmount(b, ICarbonCreditRating.Grade.A, ICarbonCreditRating.Grade.A), 0);
        assertEq(qrx.slashAmount(b, ICarbonCreditRating.Grade.A, ICarbonCreditRating.Grade.AA), 0);
        assertEq(qrx.slashAmount(b, ICarbonCreditRating.Grade.AAA, ICarbonCreditRating.Grade.AAA), 0);
    }

    function test_slashAmount_linearInGap() public view {
        uint256 b = 500;
        // gap 1: 500 / 5 = 100
        assertEq(qrx.slashAmount(b, ICarbonCreditRating.Grade.BB, ICarbonCreditRating.Grade.B), 100);
        // gap 2: 500 * 2 / 5 = 200
        assertEq(qrx.slashAmount(b, ICarbonCreditRating.Grade.BBB, ICarbonCreditRating.Grade.B), 200);
        // gap 3: 500 * 3 / 5 = 300
        assertEq(qrx.slashAmount(b, ICarbonCreditRating.Grade.A, ICarbonCreditRating.Grade.B), 300);
        // gap 4: 500 * 4 / 5 = 400
        assertEq(qrx.slashAmount(b, ICarbonCreditRating.Grade.AA, ICarbonCreditRating.Grade.B), 400);
        // gap 5: full slash
        assertEq(qrx.slashAmount(b, ICarbonCreditRating.Grade.AAA, ICarbonCreditRating.Grade.B), 500);
    }

    // ==============================================================
    // 4. Incentive / payoff tests
    // ==============================================================

    /// @dev Truthful high-quality depositor: no slash, bond fully returned.
    function test_payoff_truthfulVsOverclaim_highQuality() public {
        // Setup: two deposits, both for AA-true-quality credit.
        //  - Alice claims AA truthfully; bond = RATE_AA * amount
        //  - Bob claims AAA (overclaim); bond = RATE_AAA * amount
        // After challenge+resolve(trueGrade=AA):
        //  - Alice: bond returned in full
        //  - Bob: gap = 5 − 4 = 1 → slash bond/5
        uint256 amount = 100;

        uint256 idA = _deposit(ALICE, ICarbonCreditRating.Grade.AA, amount);
        uint256 idB = _deposit(BOB,   ICarbonCreditRating.Grade.AAA, amount);

        uint256 aliceBondIn = RATE_AA * amount;
        uint256 bobBondIn   = RATE_AAA * amount;

        vm.prank(CHALLENGER);
        qrx.challenge(idA, bytes32("e-a"));
        vm.prank(ARBITER);
        qrx.resolve(idA, ICarbonCreditRating.Grade.AA);

        vm.prank(CHALLENGER);
        qrx.challenge(idB, bytes32("e-b"));
        vm.prank(ARBITER);
        qrx.resolve(idB, ICarbonCreditRating.Grade.AA);

        IQRX.Deposit memory dA = qrx.depositOf(idA);
        IQRX.Deposit memory dB = qrx.depositOf(idB);

        assertEq(dA.bondRemaining, aliceBondIn, "truthful Alice recovers full bond");

        uint256 bobSlash = bobBondIn / 5;
        assertEq(dB.bondRemaining, bobBondIn - bobSlash, "Bob's overclaim is slashed by 1/5");

        // Critical invariant: Bob's net payoff (credit + bondRemaining − bondIn)
        // is strictly worse than Alice's across every amount.
        int256 aliceNet = int256(dA.bondRemaining) - int256(aliceBondIn); // 0
        int256 bobNet   = int256(dB.bondRemaining) - int256(bobBondIn);   // negative
        assertGt(aliceNet, bobNet, "truthful dominates overclaim in bond accounting");
    }

    /// @dev Low-quality depositor considering overclaim: slash > surplus ⇒ skip.
    ///      This is the separating-equilibrium intuition captured as an arithmetic
    ///      check. We model a buyer willing to pay (WTP_AAA − WTP_B) more for
    ///      AAA-labelled credits. If slash > surplus, overclaim is strictly dominated.
    function test_payoff_overclaimDominated_whenSlashExceedsSurplus() public pure {
        // Pretend-B credit being claimed as AAA.
        uint256 amount = 100;
        uint256 bond = RATE_AAA * amount;

        // Assume WTP surplus of 0.5e6 per tonne for AAA vs B (modest assumption;
        // real markets see Puro.earth pricing ~10x BCT).
        uint256 wtpSurplusPerTonne = 0.5e6;
        uint256 surplus = wtpSurplusPerTonne * amount;

        // If caught (gap = 5) with certainty, slash == bond == RATE_AAA*amount.
        uint256 fullSlash = bond;

        assertGt(fullSlash, surplus, "bond > surplus: overclaim strictly dominated under p(caught)=1");

        // Even at detection probability p, overclaim is only profitable if
        // p * slash < surplus ⇒ p < surplus / slash. The reference bond rates
        // yield this threshold p < 0.5e6 / 15e6 = 3.33%. The paper shows that
        // challenge-bounty incentives push realised p materially above this.
        // For the test, assert the threshold is tight enough to be credible.
        uint256 thresholdBps = (surplus * 10000) / fullSlash;
        assertLt(thresholdBps, 500, "overclaim profitable only if detection p < 5%");
    }

    // ==============================================================
    // 5. Sybil resistance
    // ==============================================================

    /// @dev A single 1000-tonne AAA deposit with bond B is attacked equivalently
    ///      to 10 × 100-tonne AAA deposits each with bond B/10: total slash
    ///      under full detection is identical. Splitting does not reduce loss.
    function test_sybilResistance_splittingDoesNotReduceSlash() public {
        uint256 amount = 1000;

        // Strategy 1: single deposit.
        uint256 idSingle = _deposit(ALICE, ICarbonCreditRating.Grade.AAA, amount);
        vm.prank(CHALLENGER);
        qrx.challenge(idSingle, bytes32("single"));
        vm.prank(ARBITER);
        qrx.resolve(idSingle, ICarbonCreditRating.Grade.B);
        uint256 singleSlash = RATE_AAA * amount - qrx.depositOf(idSingle).bondRemaining;

        // Strategy 2: 10 small deposits, each independently challenged.
        uint256 totalSlashSplit;
        for (uint256 i = 0; i < 10; i++) {
            uint256 id = _deposit(BOB, ICarbonCreditRating.Grade.AAA, amount / 10);
            vm.prank(CHALLENGER);
            qrx.challenge(id, bytes32("split"));
            vm.prank(ARBITER);
            qrx.resolve(id, ICarbonCreditRating.Grade.B);
            totalSlashSplit += RATE_AAA * (amount / 10) - qrx.depositOf(id).bondRemaining;
        }

        assertEq(singleSlash, totalSlashSplit, "splitting does not reduce slash");
    }

    /// @dev Sub-linear bond schedules would allow Sybil arbitrage (deposit N
    ///      small claims for less total bond than one big claim). The reference
    ///      schedule is linear — this test guards against accidental regressions
    ///      if the schedule is ever made step-wise or concave.
    function test_sybilResistance_bondLinearInAmount() public view {
        uint256 bondBig = qrx.bondRequired(ICarbonCreditRating.Grade.AAA, 1000);
        uint256 bondSmall = qrx.bondRequired(ICarbonCreditRating.Grade.AAA, 100);
        assertEq(bondBig, bondSmall * 10, "bond linear in amount prevents sybil arb");
    }

    // ==============================================================
    // 6. MEV / bond-lending
    // ==============================================================

    /// @dev The depositor cannot retire (and reclaim bond) while a challenge is
    ///      pending. This rules out a bond-lending attack where the depositor
    ///      borrows, overclaims, and returns the bond before detection lands.
    function test_mev_cannotRetireWhileChallenged() public {
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.AA, 100);

        vm.prank(CHALLENGER);
        qrx.challenge(id, bytes32("e"));

        vm.prank(ALICE);
        vm.expectRevert(
            abi.encodeWithSelector(QRX.WrongStatus.selector, IQRX.Status.Challenged, IQRX.Status.Active)
        );
        qrx.retire(id);
    }

    /// @dev A challenger cannot self-resolve even by impersonation; resolve
    ///      requires msg.sender == arbiter.
    function test_mev_challengerCannotSelfResolve() public {
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.AAA, 50);
        vm.prank(CHALLENGER);
        qrx.challenge(id, bytes32("e"));

        vm.prank(CHALLENGER);
        vm.expectRevert(QRX.NotArbiter.selector);
        qrx.resolve(id, ICarbonCreditRating.Grade.B);
    }

    /// @dev A non-depositor cannot siphon credit or bond via retire().
    function test_mev_nonDepositorCannotRetire() public {
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.A, 100);

        vm.prank(BOB);
        vm.expectRevert(QRX.NotDepositor.selector);
        qrx.retire(id);
    }

    // ==============================================================
    // 7. Access control & bond-amount checks
    // ==============================================================

    function test_deposit_revertsWhenBondBelowMinimum() public {
        uint256 amount = 100;
        uint256 min = qrx.bondRequired(ICarbonCreditRating.Grade.AAA, amount);

        vm.prank(ALICE);
        vm.expectRevert(abi.encodeWithSelector(QRX.BondBelowMinimum.selector, min - 1, min));
        qrx.deposit(address(credit), amount, ICarbonCreditRating.Grade.AAA, min - 1);
    }

    function test_deposit_acceptsExtraBond() public {
        // Depositor over-posts to signal extra confidence. Allowed.
        uint256 amount = 100;
        uint256 min = qrx.bondRequired(ICarbonCreditRating.Grade.AA, amount);
        uint256 extra = min * 2;

        uint256 id = _depositWithBond(ALICE, ICarbonCreditRating.Grade.AA, amount, extra);
        assertEq(qrx.depositOf(id).bond, extra);
    }

    function test_resolve_revertsOnActiveDeposit() public {
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.A, 10);

        vm.prank(ARBITER);
        vm.expectRevert(
            abi.encodeWithSelector(QRX.WrongStatus.selector, IQRX.Status.Active, IQRX.Status.Challenged)
        );
        qrx.resolve(id, ICarbonCreditRating.Grade.B);
    }

    // ==============================================================
    // 8. Constructor validation
    // ==============================================================

    function test_ctor_rejectsNonMonotoneRates() public {
        // AA rate < A rate: should revert.
        uint256[6] memory rates = [
            uint256(1e6), uint256(2e6), uint256(4e6), uint256(7e6), uint256(6e6), uint256(15e6)
        ];
        vm.expectRevert(abi.encodeWithSelector(QRX.BondRatesNotMonotone.selector, 4));
        new QRX(address(bondUsd), ARBITER, TREASURY, 5000, rates);
    }

    function test_ctor_rejectsDuplicateRates() public {
        // Two adjacent grades at the same rate is not strictly monotone → revert.
        uint256[6] memory rates = [
            uint256(1e6), uint256(2e6), uint256(2e6), uint256(7e6), uint256(10e6), uint256(15e6)
        ];
        vm.expectRevert(abi.encodeWithSelector(QRX.BondRatesNotMonotone.selector, 2));
        new QRX(address(bondUsd), ARBITER, TREASURY, 5000, rates);
    }

    function test_ctor_rejectsZeroAddresses() public {
        uint256[6] memory rates = [
            uint256(1e6), uint256(2e6), uint256(4e6), uint256(7e6), uint256(10e6), uint256(15e6)
        ];

        vm.expectRevert(QRX.BadConfig.selector);
        new QRX(address(0), ARBITER, TREASURY, 5000, rates);

        vm.expectRevert(QRX.BadConfig.selector);
        new QRX(address(bondUsd), address(0), TREASURY, 5000, rates);

        vm.expectRevert(QRX.BadConfig.selector);
        new QRX(address(bondUsd), ARBITER, address(0), 5000, rates);
    }

    function test_ctor_rejectsBountyOverTenThousandBps() public {
        uint256[6] memory rates = [
            uint256(1e6), uint256(2e6), uint256(4e6), uint256(7e6), uint256(10e6), uint256(15e6)
        ];
        vm.expectRevert(QRX.BadConfig.selector);
        new QRX(address(bondUsd), ARBITER, TREASURY, 10001, rates);
    }

    // ==============================================================
    // 9. Edge cases
    // ==============================================================

    function test_deposit_revertsOnZeroAmount() public {
        vm.prank(ALICE);
        vm.expectRevert(QRX.BadConfig.selector);
        qrx.deposit(address(credit), 0, ICarbonCreditRating.Grade.A, 0);
    }

    function test_depositOf_revertsOnUnknownId() public {
        vm.expectRevert(QRX.UnknownDeposit.selector);
        qrx.depositOf(999);
    }

    // ==============================================================
    // 10. Gas benchmarks
    // ==============================================================
    //
    // Named test_gas_* so they show up cleanly in --gas-report output for the
    // paper's Implementation / Gas section.

    function test_gas_deposit() public {
        vm.prank(ALICE);
        qrx.deposit(address(credit), 100, ICarbonCreditRating.Grade.AA, RATE_AA * 100);
    }

    function test_gas_challenge() public {
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.AA, 100);
        vm.prank(CHALLENGER);
        qrx.challenge(id, keccak256("evidence"));
    }

    function test_gas_resolve() public {
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.AAA, 100);
        vm.prank(CHALLENGER);
        qrx.challenge(id, keccak256("evidence"));
        vm.prank(ARBITER);
        qrx.resolve(id, ICarbonCreditRating.Grade.B);
    }

    function test_gas_retire_noChallenge() public {
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.A, 100);
        vm.prank(ALICE);
        qrx.retire(id);
    }

    function test_gas_retire_afterSlash() public {
        uint256 id = _deposit(ALICE, ICarbonCreditRating.Grade.AAA, 100);
        vm.prank(CHALLENGER);
        qrx.challenge(id, keccak256("e"));
        vm.prank(ARBITER);
        qrx.resolve(id, ICarbonCreditRating.Grade.BB);
        vm.prank(ALICE);
        qrx.retire(id);
    }
}
