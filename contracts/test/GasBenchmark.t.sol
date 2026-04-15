// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// Gas benchmark tests for the CarbonCreditRating quality-gating primitive.
// Run with: forge test --match-contract GasBenchmarkTest --gas-report
//
// These tests quantify the gas overhead of on-chain credit quality checks so
// that DeFi integrators can estimate the marginal cost of adding a meetsGrade()
// gate to swaps, transfers, or collateral checks.

import {Test} from "forge-std/Test.sol";
import {CarbonCreditRating} from "../CarbonCreditRating.sol";
import {ICarbonCreditRating} from "../ICarbonCreditRating.sol";

contract GasBenchmarkTest is Test {
    CarbonCreditRating internal rating;
    address internal rater;
    address constant CREDIT_TOKEN = address(0xC0FFEE);
    address constant CREDIT_TOKEN_2 = address(0xBEEF);

    // ----------------------------------------------------------------
    // Helpers
    // ----------------------------------------------------------------

    /// @dev v0.5 default stds from the rubric's empirical calibration.
    function _defaultStds() internal pure returns (ICarbonCreditRating.DimensionStds memory) {
        return ICarbonCreditRating.DimensionStds({
            removalType: 4,
            additionality: 9,
            permanence: 4,
            mrvGrade: 7,
            vintageYear: 10,
            coBenefits: 9,
            registryMethodology: 11
        });
    }

    /// @dev High-quality DAC credit (Climeworks-style).
    function _highQualityScores() internal pure returns (ICarbonCreditRating.DimensionScores memory) {
        return ICarbonCreditRating.DimensionScores({
            removalType: 98,
            additionality: 95,
            permanence: 98,
            mrvGrade: 92,
            vintageYear: 100,
            coBenefits: 15,
            registryMethodology: 80
        });
    }

    /// @dev Mid-quality reforestation credit.
    function _midQualityScores() internal pure returns (ICarbonCreditRating.DimensionScores memory) {
        return ICarbonCreditRating.DimensionScores({
            removalType: 55,
            additionality: 60,
            permanence: 50,
            mrvGrade: 58,
            vintageYear: 70,
            coBenefits: 45,
            registryMethodology: 55
        });
    }

    /// @dev All disqualifiers off.
    function _noFlags() internal pure returns (ICarbonCreditRating.Disqualifiers memory) {
        return ICarbonCreditRating.Disqualifiers({
            doubleCounting: false,
            failedVerification: false,
            sanctionedRegistry: false,
            noThirdParty: false,
            humanRights: false,
            communityHarm: false,
            biodiversityHarm: false
        });
    }

    /// @dev One disqualifier active (noThirdParty).
    function _oneFlag() internal pure returns (ICarbonCreditRating.Disqualifiers memory) {
        return ICarbonCreditRating.Disqualifiers({
            doubleCounting: false,
            failedVerification: false,
            sanctionedRegistry: false,
            noThirdParty: true,
            humanRights: false,
            communityHarm: false,
            biodiversityHarm: false
        });
    }

    /// @dev Three disqualifiers active.
    function _threeFlags() internal pure returns (ICarbonCreditRating.Disqualifiers memory) {
        return ICarbonCreditRating.Disqualifiers({
            doubleCounting: false,
            failedVerification: false,
            sanctionedRegistry: true,
            noThirdParty: true,
            humanRights: false,
            communityHarm: true,
            biodiversityHarm: false
        });
    }

    /// @dev All seven disqualifiers active.
    function _allFlags() internal pure returns (ICarbonCreditRating.Disqualifiers memory) {
        return ICarbonCreditRating.Disqualifiers({
            doubleCounting: true,
            failedVerification: true,
            sanctionedRegistry: true,
            noThirdParty: true,
            humanRights: true,
            communityHarm: true,
            biodiversityHarm: true
        });
    }

    /// @dev Write a rating for a given tokenId from the authorized rater.
    function _writeRating(uint256 tokenId) internal {
        vm.prank(rater);
        rating.setRating(
            CREDIT_TOKEN,
            tokenId,
            _highQualityScores(),
            _defaultStds(),
            _noFlags(),
            uint64(block.timestamp + 365 days),
            keccak256(abi.encodePacked("evidence-", tokenId))
        );
    }

    /// @dev Bulk-write N ratings to CREDIT_TOKEN_2 for scalability tests.
    function _seedRatings(uint256 count) internal {
        for (uint256 i = 1; i <= count; i++) {
            vm.prank(rater);
            rating.setRating(
                CREDIT_TOKEN_2,
                i,
                _midQualityScores(),
                _defaultStds(),
                _noFlags(),
                uint64(block.timestamp + 365 days),
                keccak256(abi.encodePacked("seed-", i))
            );
        }
    }

    // ----------------------------------------------------------------
    // Setup
    // ----------------------------------------------------------------

    function setUp() public {
        rater = address(0xAAAA);
        rating = new CarbonCreditRating(rater);
        vm.warp(1_700_000_000); // deterministic timestamp (Nov 2023)
    }

    // ================================================================
    // 1. setRating: cold storage (first write)
    // ================================================================

    function test_gas_setRating_coldStorage_firstWrite() public {
        vm.prank(rater);
        rating.setRating(
            CREDIT_TOKEN,
            1,
            _highQualityScores(),
            _defaultStds(),
            _noFlags(),
            uint64(block.timestamp + 365 days),
            keccak256("evidence-1")
        );

        // Verify the write landed correctly.
        ICarbonCreditRating.Rating memory r = rating.ratingOf(CREDIT_TOKEN, 1);
        assertGt(r.compositeBps, 0, "rating stored");
    }

    // ================================================================
    // 2. setRating: warm storage (update existing rating)
    // ================================================================

    function test_gas_setRating_warmStorage_update() public {
        // First write (cold) -- not measured in the gas report name.
        _writeRating(2);

        // Second write (warm) -- this is the one that matters for the gas report.
        vm.prank(rater);
        rating.setRating(
            CREDIT_TOKEN,
            2,
            _midQualityScores(),
            _defaultStds(),
            _oneFlag(),
            uint64(block.timestamp + 180 days),
            keccak256("evidence-2-updated")
        );

        ICarbonCreditRating.Rating memory r = rating.ratingOf(CREDIT_TOKEN, 2);
        assertEq(r.evidenceHash, keccak256("evidence-2-updated"), "update stored");
    }

    // ================================================================
    // 3. meetsGrade: fresh rating
    // ================================================================

    function test_gas_meetsGrade_freshRating() public {
        _writeRating(3);

        bool meets = rating.meetsGrade(CREDIT_TOKEN, 3, ICarbonCreditRating.Grade.A);
        assertTrue(meets, "high-quality credit meets A");
    }

    function test_gas_meetsGrade_freshRating_fail() public {
        _writeRating(4);

        // High-quality credit should not fail AAA... actually it should pass AAA.
        // Use a mid-quality credit to get a "does not meet" path.
        vm.prank(rater);
        rating.setRating(
            CREDIT_TOKEN,
            5,
            _midQualityScores(),
            _defaultStds(),
            _noFlags(),
            uint64(block.timestamp + 365 days),
            keccak256("evidence-5")
        );
        bool meets = rating.meetsGrade(CREDIT_TOKEN, 5, ICarbonCreditRating.Grade.AAA);
        assertFalse(meets, "mid-quality credit does not meet AAA");
    }

    // ================================================================
    // 4. ratingOf: full read
    // ================================================================

    function test_gas_ratingOf_fullRead() public {
        _writeRating(6);

        ICarbonCreditRating.Rating memory r = rating.ratingOf(CREDIT_TOKEN, 6);
        assertGt(r.compositeBps, 0, "rating returned");
        assertEq(r.attestedBy, rater, "attester matches");
    }

    // ================================================================
    // 5. isStale: fresh rating + stale rating
    // ================================================================

    function test_gas_isStale_freshRating() public {
        _writeRating(7);

        bool stale = rating.isStale(CREDIT_TOKEN, 7);
        assertFalse(stale, "fresh rating is not stale");
    }

    function test_gas_isStale_expiredRating() public {
        vm.prank(rater);
        rating.setRating(
            CREDIT_TOKEN,
            8,
            _highQualityScores(),
            _defaultStds(),
            _noFlags(),
            uint64(block.timestamp + 1 days),
            keccak256("evidence-8")
        );

        // Fast-forward past expiry.
        vm.warp(block.timestamp + 2 days);

        bool stale = rating.isStale(CREDIT_TOKEN, 8);
        assertTrue(stale, "expired rating is stale");
    }

    function test_gas_isStale_unrated() public view {
        bool stale = rating.isStale(CREDIT_TOKEN, 999);
        assertFalse(stale, "unrated is not stale");
    }

    // ================================================================
    // 6. computeComposite (pure)
    // ================================================================

    function test_gas_computeComposite_pure() public view {
        uint16 bps = rating.computeComposite(_highQualityScores());
        assertEq(bps, 9505, "Orca composite");
    }

    // ================================================================
    // 7. computeCompositeVariance (pure)
    // ================================================================

    function test_gas_computeCompositeVariance_pure() public view {
        uint32 variance = rating.computeCompositeVariance(_defaultStds());
        assertEq(variance, 83706, "default stds variance");
    }

    function test_gas_computeCompositeVariance_zeroStds() public view {
        ICarbonCreditRating.DimensionStds memory zero;
        uint32 variance = rating.computeCompositeVariance(zero);
        assertEq(variance, 0, "zero stds yield zero variance");
    }

    // ================================================================
    // 8. gradeFromComposite (pure)
    // ================================================================

    function test_gas_gradeFromComposite_AAA() public view {
        ICarbonCreditRating.Grade g = rating.gradeFromComposite(9500);
        assertEq(uint8(g), uint8(ICarbonCreditRating.Grade.AAA), "9500 -> AAA");
    }

    function test_gas_gradeFromComposite_B() public view {
        ICarbonCreditRating.Grade g = rating.gradeFromComposite(1500);
        assertEq(uint8(g), uint8(ICarbonCreditRating.Grade.B), "1500 -> B");
    }

    function test_gas_gradeFromComposite_AA() public view {
        ICarbonCreditRating.Grade g = rating.gradeFromComposite(8000);
        assertEq(uint8(g), uint8(ICarbonCreditRating.Grade.AA), "8000 -> AA");
    }

    // ================================================================
    // 9. applyDisqualifiers: 0, 1, 3, and 7 flags
    // ================================================================

    function test_gas_applyDisqualifiers_0flags() public view {
        ICarbonCreditRating.Grade g = rating.applyDisqualifiers(
            ICarbonCreditRating.Grade.AAA,
            _noFlags()
        );
        assertEq(uint8(g), uint8(ICarbonCreditRating.Grade.AAA), "no flags -> unchanged");
    }

    function test_gas_applyDisqualifiers_1flag() public view {
        ICarbonCreditRating.Grade g = rating.applyDisqualifiers(
            ICarbonCreditRating.Grade.AAA,
            _oneFlag()
        );
        assertEq(uint8(g), uint8(ICarbonCreditRating.Grade.BBB), "noThirdParty caps at BBB");
    }

    function test_gas_applyDisqualifiers_3flags() public view {
        ICarbonCreditRating.Grade g = rating.applyDisqualifiers(
            ICarbonCreditRating.Grade.AAA,
            _threeFlags()
        );
        assertEq(uint8(g), uint8(ICarbonCreditRating.Grade.BB), "sanctionedRegistry caps at BB");
    }

    function test_gas_applyDisqualifiers_7flags_allActive() public view {
        ICarbonCreditRating.Grade g = rating.applyDisqualifiers(
            ICarbonCreditRating.Grade.AAA,
            _allFlags()
        );
        assertEq(uint8(g), uint8(ICarbonCreditRating.Grade.B), "all flags cap at B");
    }

    // ================================================================
    // 10. Batch setRating: 16 credits (tokenized pilot deployment)
    // ================================================================

    function test_gas_batch_setRating_16credits() public {
        ICarbonCreditRating.DimensionScores memory scores = _highQualityScores();
        ICarbonCreditRating.DimensionStds memory stds = _defaultStds();
        ICarbonCreditRating.Disqualifiers memory flags = _noFlags();
        uint64 expiry = uint64(block.timestamp + 365 days);

        for (uint256 i = 0; i < 16; i++) {
            vm.prank(rater);
            rating.setRating(
                CREDIT_TOKEN,
                1000 + i,
                scores,
                stds,
                flags,
                expiry,
                keccak256(abi.encodePacked("batch-", i))
            );
        }

        // Verify first and last.
        ICarbonCreditRating.Rating memory first = rating.ratingOf(CREDIT_TOKEN, 1000);
        ICarbonCreditRating.Rating memory last = rating.ratingOf(CREDIT_TOKEN, 1015);
        assertGt(first.compositeBps, 0, "first batch credit stored");
        assertGt(last.compositeBps, 0, "last batch credit stored");
    }

    // ================================================================
    // 11. Scalability: meetsGrade after N ratings written
    // ================================================================
    //
    // These tests measure whether meetsGrade cost is O(1) regardless of how
    // many ratings exist in storage. Because the rating lookup is a single
    // keccak256(abi.encode(addr,id)) -> mapping read, gas should be constant.
    // The tests write N unrelated ratings first, then measure the meetsGrade
    // call on the (N+1)-th credit.

    function test_gas_meetsGrade_after100ratings() public {
        _seedRatings(100);

        // Write the target credit (101st).
        _writeRating(101);

        bool meets = rating.meetsGrade(CREDIT_TOKEN, 101, ICarbonCreditRating.Grade.AA);
        assertTrue(meets, "meets AA after 100 ratings");
    }

    function test_gas_meetsGrade_after500ratings() public {
        _seedRatings(500);

        _writeRating(501);

        bool meets = rating.meetsGrade(CREDIT_TOKEN, 501, ICarbonCreditRating.Grade.AA);
        assertTrue(meets, "meets AA after 500 ratings");
    }

    function test_gas_meetsGrade_after1000ratings() public {
        _seedRatings(1000);

        _writeRating(1001);

        bool meets = rating.meetsGrade(CREDIT_TOKEN, 1001, ICarbonCreditRating.Grade.AA);
        assertTrue(meets, "meets AA after 1000 ratings");
    }

    // ================================================================
    // 12. Composite cost comparison helpers
    // ================================================================
    //
    // These tests isolate the gas cost of a meetsGrade call after a single
    // rating and after the rating is stale, making it easy to compare against
    // typical DeFi operations in the gas report output.

    function test_gas_meetsGrade_singleRating_viewOnly() public {
        _writeRating(2000);

        // Isolate the view call.
        bool meets = rating.meetsGrade(CREDIT_TOKEN, 2000, ICarbonCreditRating.Grade.BBB);
        assertTrue(meets, "high-quality meets BBB");
    }

    function test_gas_meetsGrade_staleRating_earlyExit() public {
        vm.prank(rater);
        rating.setRating(
            CREDIT_TOKEN,
            2001,
            _highQualityScores(),
            _defaultStds(),
            _noFlags(),
            uint64(block.timestamp + 1 days),
            keccak256("evidence-2001")
        );

        vm.warp(block.timestamp + 2 days);

        bool meets = rating.meetsGrade(CREDIT_TOKEN, 2001, ICarbonCreditRating.Grade.B);
        assertFalse(meets, "stale rating early exit returns false");
    }

    function test_gas_meetsGrade_unrated_earlyExit() public view {
        bool meets = rating.meetsGrade(CREDIT_TOKEN, 9999, ICarbonCreditRating.Grade.B);
        assertFalse(meets, "unrated early exit returns false");
    }
}
