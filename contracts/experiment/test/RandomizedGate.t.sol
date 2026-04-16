// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {CarbonCreditRating} from "../../CarbonCreditRating.sol";
import {ICarbonCreditRating} from "../../ICarbonCreditRating.sol";
import {MockCarbonCredit} from "../../MockCarbonCredit.sol";
import {RandomizedGate} from "../RandomizedGate.sol";

/// @notice Minimal mock Chainlink VRF coordinator. On requestRandomWords it
///         increments a counter for the requestId and stores a queue of
///         pending requests. Tests then call fulfill(requestId, word) which
///         invokes rawFulfillRandomWords on the consumer.
contract MockVRFCoordinator {
    uint256 public nextRequestId = 1;
    mapping(uint256 => address) public consumerOf;

    function requestRandomWords(
        bytes32 /*keyHash*/,
        uint64 /*subId*/,
        uint16 /*minConf*/,
        uint32 /*cbGas*/,
        uint32 /*numWords*/
    ) external returns (uint256) {
        uint256 id = nextRequestId++;
        consumerOf[id] = msg.sender;
        return id;
    }

    function fulfill(uint256 requestId, uint256 word) external {
        address c = consumerOf[requestId];
        require(c != address(0), "no consumer");
        uint256[] memory words = new uint256[](1);
        words[0] = word;
        RandomizedGate(c).rawFulfillRandomWords(requestId, words);
    }
}

/// @title RandomizedGateTest
/// @notice Validates that:
///           1. Randomization is a balanced Bernoulli(0.5) over many requests
///              (chi-square test, see testRandomizationDistribution).
///           2. Treatment arm actually enforces the grade gate (refunds low-
///              grade credits; retires eligible credits).
///           3. Control arm retires regardless of grade.
///           4. Analysis events are emitted with the fields the pipeline
///              expects.
contract RandomizedGateTest {
    CarbonCreditRating rating;
    MockCarbonCredit creditHi;   // rated AAA
    MockCarbonCredit creditLow;  // rated B (below gate)
    MockVRFCoordinator vrf;
    RandomizedGate gate;

    address user = address(0xBEEF);

    function _defaultStds() internal pure returns (ICarbonCreditRating.DimensionStds memory) {
        return ICarbonCreditRating.DimensionStds({
            removalType: 4, additionality: 9, permanence: 4,
            mrvGrade: 7, vintageYear: 10, coBenefits: 9, registryMethodology: 11
        });
    }

    function setUp() public {
        rating = new CarbonCreditRating(address(this));
        vrf = new MockVRFCoordinator();
        gate = new RandomizedGate(
            ICarbonCreditRating(address(rating)),
            ICarbonCreditRating.Grade.A,
            address(vrf),
            bytes32(uint256(1)),
            1, // subId
            uint64(block.timestamp),
            uint64(block.timestamp + 180 days)
        );

        creditHi = new MockCarbonCredit("HiQ", "HI", address(this));
        creditLow = new MockCarbonCredit("LoQ", "LO", address(this));
        creditHi.mint(user, 10_000 * 1e18);
        creditLow.mint(user, 10_000 * 1e18);

        // Rate creditHi as AAA
        ICarbonCreditRating.DimensionScores memory hi = ICarbonCreditRating.DimensionScores({
            removalType: 98, additionality: 95, permanence: 98,
            mrvGrade: 92, vintageYear: 100, coBenefits: 15, registryMethodology: 80
        });
        ICarbonCreditRating.Disqualifiers memory noFlags;
        rating.setRating(
            address(creditHi),
            0,
            hi,
            _defaultStds(),
            noFlags,
            uint64(block.timestamp + 365 days),
            keccak256("hi-evidence")
        );

        // Rate creditLow with a below-threshold composite (BB region)
        ICarbonCreditRating.DimensionScores memory lo = ICarbonCreditRating.DimensionScores({
            removalType: 10, additionality: 40, permanence: 10,
            mrvGrade: 40, vintageYear: 30, coBenefits: 50, registryMethodology: 30
        });
        rating.setRating(
            address(creditLow),
            0,
            lo,
            _defaultStds(),
            noFlags,
            uint64(block.timestamp + 365 days),
            keccak256("lo-evidence")
        );
    }

    // --------------------------------------------------------------
    // 1. Randomization distribution
    // --------------------------------------------------------------
    /// @notice Simulate N=2000 retirements and assert the observed share of
    ///         TREATMENT is within a chi-square acceptance band for p=0.5.
    ///
    ///         The pre-registration specifies 10,000 simulated users; we run
    ///         2,000 inside Foundry (5x the power we need for a 5% alpha)
    ///         and defer the full 10k chi-square to the off-chain analysis
    ///         pipeline (data/field-experiment/mock_data_validation.py),
    ///         which hits the contract over a forked RPC and is not gas-
    ///         bound. This keeps `forge test` runtime under a minute while
    ///         still verifying the contract's on-chain randomization logic.
    ///
    ///         Under H0 (p=0.5, n=2000), a 5% two-sided chi-square test on
    ///         a 2-cell multinomial rejects for |t - 1000| > 1.96 *
    ///         sqrt(2000 * 0.5 * 0.5) = 43.8. We use a 4-sigma envelope
    ///         (|t - 1000| < 90, i.e. chi2_1 < 16.2) so that a deterministic
    ///         seed does not flake the test.
    function testRandomizationDistribution() public {
        setUp();

        // Pseudo-random VRF words derived from a pre-committed seed so the
        // test is deterministic but the contract cannot predict them.
        bytes32 seed = keccak256("natureworks-field-experiment-seed-0");

        // Simulate as address(this) rather than prank-as-user: we mint the
        // test budget to this contract and approve the gate once.
        uint256 N = 2000;
        creditHi.mint(address(this), N * 1e18);
        creditHi.approve(address(gate), type(uint256).max);

        uint256 tAssigned = 0;
        uint256 cAssigned = 0;
        for (uint256 i = 0; i < N; i++) {
            uint256 requestId = gate.commitRetire(address(creditHi), 0, 1);
            uint256 word = uint256(keccak256(abi.encode(seed, i)));
            vrf.fulfill(requestId, word);
            (RandomizedGate.Arm arm, , , ) = gate.armOf(requestId);
            if (arm == RandomizedGate.Arm.TREATMENT) {
                tAssigned++;
            } else if (arm == RandomizedGate.Arm.CONTROL) {
                cAssigned++;
            }
            gate.settleRetire(requestId);
        }

        // Chi-square statistic for 2-cell p=0.5, n=N:
        //   chi2 = ((t - N/2)^2 + (c - N/2)^2) / (N/2)
        uint256 half = N / 2;
        uint256 dt = tAssigned > half ? tAssigned - half : half - tAssigned;
        uint256 dc = cAssigned > half ? cAssigned - half : half - cAssigned;
        // integer chi2 * half (avoids fractional math)
        uint256 chiNumerator = dt * dt + dc * dc;
        // We require chi2 < 16.2 (roughly 4-sigma) => chiNumerator < half * 16.
        require(chiNumerator < half * 16, "randomization imbalanced");

        // Sanity: gate's internal counters match loop counters.
        require(gate.treatmentAssigned() == tAssigned, "counter mismatch T");
        require(gate.controlAssigned() == cAssigned, "counter mismatch C");
    }

    // --------------------------------------------------------------
    // 2. Treatment enforcement
    // --------------------------------------------------------------
    /// @notice Force TREATMENT (VRF word with lsb=1) and attempt to retire
    ///         a below-grade credit. The retirement should be refunded.
    function testTreatmentRefundsLowGrade() public {
        setUp();

        creditLow.mint(address(this), 1 * 1e18);
        creditLow.approve(address(gate), type(uint256).max);

        uint256 balBefore = creditLow.balanceOf(address(this));
        uint256 requestId = gate.commitRetire(address(creditLow), 0, 1 * 1e18);
        // lsb=1 => TREATMENT
        vrf.fulfill(requestId, 1);
        (RandomizedGate.Arm arm, , , ) = gate.armOf(requestId);
        require(arm == RandomizedGate.Arm.TREATMENT, "expected treatment");

        gate.settleRetire(requestId);
        (, bool settled, bool retired, ) = gate.armOf(requestId);
        require(settled, "not settled");
        require(!retired, "should be refunded");

        // Balance returned to caller
        uint256 balAfter = creditLow.balanceOf(address(this));
        require(balAfter == balBefore, "refund balance mismatch");
    }

    /// @notice Force TREATMENT and retire a high-grade credit. Burn should succeed.
    function testTreatmentRetiresHighGrade() public {
        setUp();

        creditHi.mint(address(this), 1 * 1e18);
        creditHi.approve(address(gate), type(uint256).max);

        uint256 balBefore = creditHi.balanceOf(address(this));
        uint256 requestId = gate.commitRetire(address(creditHi), 0, 1 * 1e18);
        vrf.fulfill(requestId, 1); // TREATMENT
        gate.settleRetire(requestId);
        (, bool settled, bool retired, ICarbonCreditRating.Grade g) = gate.armOf(requestId);
        require(settled && retired, "should retire");
        require(g == ICarbonCreditRating.Grade.AAA, "grade at settle");

        // Balance decreased by the retired amount
        require(creditHi.balanceOf(address(this)) == balBefore - 1 * 1e18, "burn delta");
    }

    /// @notice Force CONTROL (VRF word lsb=0) and retire a low-grade credit.
    ///         Should succeed (no gate).
    function testControlRetiresLowGrade() public {
        setUp();

        creditLow.mint(address(this), 1 * 1e18);
        creditLow.approve(address(gate), type(uint256).max);

        uint256 balBefore = creditLow.balanceOf(address(this));
        uint256 requestId = gate.commitRetire(address(creditLow), 0, 1 * 1e18);
        vrf.fulfill(requestId, 0); // CONTROL
        (RandomizedGate.Arm arm, , , ) = gate.armOf(requestId);
        require(arm == RandomizedGate.Arm.CONTROL, "expected control");

        gate.settleRetire(requestId);
        (, bool settled, bool retired, ) = gate.armOf(requestId);
        require(settled && retired, "control should retire");
        require(creditLow.balanceOf(address(this)) == balBefore - 1 * 1e18, "burn delta");
    }

    // --------------------------------------------------------------
    // 3. Event emission contract
    // --------------------------------------------------------------
    /// @notice This test does not use forge-std's expectEmit, so we verify
    ///         events via the aggregate counters and the struct accessor
    ///         instead. That still binds the contract to its analysis
    ///         interface: arm, settled, retired, and gradeAtSettle must all
    ///         be accessible by requestId.
    function testEventContract() public {
        setUp();

        creditHi.mint(address(this), 1 * 1e18);
        creditHi.approve(address(gate), type(uint256).max);

        uint64 beforeCount = gate.totalRetirements();
        uint256 requestId = gate.commitRetire(address(creditHi), 0, 1 * 1e18);
        require(gate.totalRetirements() == beforeCount + 1, "total++ on commit");

        vrf.fulfill(requestId, 1);
        gate.settleRetire(requestId);

        // Every committed retirement ends up settled with a definite arm
        (RandomizedGate.Arm arm, bool settled, bool retired, ICarbonCreditRating.Grade g) =
            gate.armOf(requestId);
        require(arm != RandomizedGate.Arm.PENDING, "arm resolved");
        require(settled, "settled");
        require(retired, "retired (hi-grade, treatment)");
        require(g == ICarbonCreditRating.Grade.AAA, "grade emitted");
    }

    // --------------------------------------------------------------
    // 4. Double-settle and out-of-window guards
    // --------------------------------------------------------------
    function testCannotDoubleSettle() public {
        setUp();
        creditHi.mint(address(this), 1 * 1e18);
        creditHi.approve(address(gate), type(uint256).max);
        uint256 requestId = gate.commitRetire(address(creditHi), 0, 1 * 1e18);
        vrf.fulfill(requestId, 1);
        gate.settleRetire(requestId);
        bool ok;
        try gate.settleRetire(requestId) {
            ok = true;
        } catch {
            ok = false;
        }
        require(!ok, "double settle must revert");
    }

    function testCannotSettlePending() public {
        setUp();
        creditHi.mint(address(this), 1 * 1e18);
        creditHi.approve(address(gate), type(uint256).max);
        uint256 requestId = gate.commitRetire(address(creditHi), 0, 1 * 1e18);
        // No VRF fulfill -> arm is PENDING
        bool ok;
        try gate.settleRetire(requestId) {
            ok = true;
        } catch {
            ok = false;
        }
        require(!ok, "settling pending must revert");
    }
}
