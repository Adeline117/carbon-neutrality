// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {CarbonCreditRating} from "../CarbonCreditRating.sol";
import {QualityGatedPool} from "../QualityGatedPool.sol";
import {MockCarbonCredit} from "../MockCarbonCredit.sol";
import {ICarbonCreditRating} from "../ICarbonCreditRating.sol";

/// @title IntegrationTest
/// @notice End-to-end lifecycle test: deploy → rate → deposit accepted →
///         deposit rejected → re-rate → stale → reject stale.
///         Proves the entire pipeline works as a connected system, not just
///         unit-tested pieces.
contract IntegrationTest {
    CarbonCreditRating rating;
    QualityGatedPool premiumPool;  // AA+ gated
    QualityGatedPool standardPool; // A+ gated
    MockCarbonCredit orca;  // high quality
    MockCarbonCredit bct;   // low quality

    function _defaultStds() internal pure returns (ICarbonCreditRating.DimensionStds memory) {
        return ICarbonCreditRating.DimensionStds({
            removalType: 4, additionality: 9, permanence: 4,
            mrvGrade: 7, vintageYear: 10, coBenefits: 9, registryMethodology: 11
        });
    }

    function setUp() public {
        // Deploy core contracts
        rating = new CarbonCreditRating(address(this));
        premiumPool = new QualityGatedPool("Premium AA+", ICarbonCreditRating(address(rating)), ICarbonCreditRating.Grade.AA);
        standardPool = new QualityGatedPool("Standard A+", ICarbonCreditRating(address(rating)), ICarbonCreditRating.Grade.A);

        // Deploy mock credits
        orca = new MockCarbonCredit("Climeworks Orca", "MCC-ORCA", address(this));
        bct = new MockCarbonCredit("Toucan BCT", "MCC-BCT", address(this));

        // Mint tokens
        orca.mint(address(this), 1000 * 1e18);
        bct.mint(address(this), 1000 * 1e18);
    }

    /// @dev Full lifecycle: rate → deposit AA credit into premium pool → succeeds
    function testFullLifecycleAADeposit() public {
        setUp();

        // Rate Orca as AAA
        ICarbonCreditRating.DimensionScores memory orcaScores = ICarbonCreditRating.DimensionScores({
            removalType: 98, additionality: 95, permanence: 98,
            mrvGrade: 92, vintageYear: 100, coBenefits: 15, registryMethodology: 80
        });
        ICarbonCreditRating.Disqualifiers memory noFlags;
        uint64 expiresAt = uint64(block.timestamp + 365 days);

        rating.setRating(address(orca), 0, orcaScores, _defaultStds(), noFlags, expiresAt, keccak256("orca-evidence"));

        // Verify rating
        ICarbonCreditRating.Rating memory r = rating.ratingOf(address(orca), 0);
        require(r.finalGrade == ICarbonCreditRating.Grade.AAA, "Orca should be AAA");
        require(r.compositeVarianceBps2 == 83706, "variance mismatch");
        require(!rating.isStale(address(orca), 0), "should not be stale");

        // Deposit into premium pool
        orca.approve(address(premiumPool), 100 * 1e18);
        premiumPool.deposit(address(orca), 0, 100 * 1e18);
        require(premiumPool.balanceOf(address(this)) == 100 * 1e18, "should have pool shares");
    }

    /// @dev Rate BCT as BB → premium pool rejects, standard pool rejects
    function testLowQualityRejectedByBothPools() public {
        setUp();

        // Rate BCT as BB
        ICarbonCreditRating.DimensionScores memory bctScores = ICarbonCreditRating.DimensionScores({
            removalType: 30, additionality: 32, permanence: 15,
            mrvGrade: 48, vintageYear: 16, coBenefits: 35, registryMethodology: 45
        });
        ICarbonCreditRating.Disqualifiers memory noFlags;

        rating.setRating(address(bct), 0, bctScores, _defaultStds(), noFlags, uint64(block.timestamp + 365 days), keccak256("bct-evidence"));

        ICarbonCreditRating.Rating memory r = rating.ratingOf(address(bct), 0);
        require(r.finalGrade == ICarbonCreditRating.Grade.BB, "BCT should be BB");

        // Premium pool (AA+) should reject
        bct.approve(address(premiumPool), 100 * 1e18);
        bool rejected = false;
        try premiumPool.deposit(address(bct), 0, 100 * 1e18) {
            rejected = false;
        } catch {
            rejected = true;
        }
        require(rejected, "premium pool should reject BB credit");

        // Standard pool (A+) should also reject
        bct.approve(address(standardPool), 100 * 1e18);
        rejected = false;
        try standardPool.deposit(address(bct), 0, 100 * 1e18) {
            rejected = false;
        } catch {
            rejected = true;
        }
        require(rejected, "standard pool should reject BB credit");
    }

    /// @dev Unrated credit → pool rejects
    function testUnratedCreditRejected() public {
        setUp();

        orca.approve(address(premiumPool), 100 * 1e18);
        bool rejected = false;
        try premiumPool.deposit(address(orca), 0, 100 * 1e18) {
            rejected = false;
        } catch {
            rejected = true;
        }
        require(rejected, "unrated credit should be rejected");
    }

    /// @dev Rate → warp past expiry → pool rejects stale
    function testStaleRatingRejectedByPool() public {
        setUp();

        ICarbonCreditRating.DimensionScores memory scores = ICarbonCreditRating.DimensionScores({
            removalType: 98, additionality: 95, permanence: 98,
            mrvGrade: 92, vintageYear: 100, coBenefits: 15, registryMethodology: 80
        });
        ICarbonCreditRating.Disqualifiers memory noFlags;

        // Set rating with 1-day expiry
        rating.setRating(address(orca), 0, scores, _defaultStds(), noFlags, uint64(block.timestamp + 1 days), keccak256("short-lived"));

        // Warp past expiry
        vm_warp(block.timestamp + 2 days);

        // Pool should reject stale rating
        orca.approve(address(premiumPool), 100 * 1e18);
        bool rejected = false;
        try premiumPool.deposit(address(orca), 0, 100 * 1e18) {
            rejected = false;
        } catch {
            rejected = true;
        }
        require(rejected, "stale rating should be rejected by pool");
    }

    /// @dev Disqualifier caps grade → pool rejects even with high composite
    function testDisqualifierCausesPoolRejection() public {
        setUp();

        ICarbonCreditRating.DimensionScores memory scores = ICarbonCreditRating.DimensionScores({
            removalType: 95, additionality: 95, permanence: 95,
            mrvGrade: 95, vintageYear: 95, coBenefits: 95, registryMethodology: 95
        });
        // Double counting → caps at B
        ICarbonCreditRating.Disqualifiers memory flags;
        flags.doubleCounting = true;

        rating.setRating(address(orca), 0, scores, _defaultStds(), flags, uint64(block.timestamp + 365 days), bytes32(0));

        ICarbonCreditRating.Rating memory r = rating.ratingOf(address(orca), 0);
        require(r.nominalGrade == ICarbonCreditRating.Grade.AAA, "nominal should be AAA");
        require(r.finalGrade == ICarbonCreditRating.Grade.B, "final should be B (capped)");

        // Even standard pool (A+) rejects
        orca.approve(address(standardPool), 100 * 1e18);
        bool rejected = false;
        try standardPool.deposit(address(orca), 0, 100 * 1e18) {
            rejected = false;
        } catch {
            rejected = true;
        }
        require(rejected, "B-capped credit should be rejected by A+ pool");
    }

    // Foundry cheatcode helper
    function vm_warp(uint256 ts) internal {
        address vm = address(uint160(uint256(keccak256("hevm cheat code"))));
        (bool ok, ) = vm.call(abi.encodeWithSignature("warp(uint256)", ts));
        require(ok, "vm.warp failed");
    }
}
