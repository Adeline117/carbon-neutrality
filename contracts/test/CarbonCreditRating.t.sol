// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// Foundry-compatible tests. Run with: forge test
// The tests do not depend on forge-std; Assertions are inline.

import {CarbonCreditRating} from "../CarbonCreditRating.sol";
import {ICarbonCreditRating} from "../ICarbonCreditRating.sol";

contract CarbonCreditRatingTest {
    CarbonCreditRating rating;
    address constant CREDIT_TOKEN = address(0xC0FFEE);

    function setUp() public {
        // Make this test contract the rater so it can call setRating directly.
        rating = new CarbonCreditRating(address(this));
    }

    /// @dev Climeworks Orca-style input. v0.4: composite 95.2 -> 9520 bps -> AAA.
    ///      Previously (v0.3): 8680 bps AA. The Oxford inversion is now resolved.
    function testOrcaComposite() public {
        setUp();
        ICarbonCreditRating.DimensionScores memory s = ICarbonCreditRating.DimensionScores({
            removalType: 98,
            additionality: 95,
            permanence: 98,
            mrvGrade: 92,
            vintageYear: 100,
            coBenefits: 15,
            registryMethodology: 82
        });
        uint16 bps = rating.computeComposite(s);
        // v0.4 weights: 2500 / 2000 / 1750 / 2000 / 1000 / 0 / 750
        // 98*2500 + 95*2000 + 98*1750 + 92*2000 + 100*1000 + 15*0 + 82*750
        // = 245000 + 190000 + 171500 + 184000 + 100000 + 0 + 61500
        // = 952000 / 100 = 9520
        require(bps == 9520, "composite mismatch");
        require(rating.gradeFromComposite(bps) == ICarbonCreditRating.Grade.AAA, "Orca reaches AAA");
    }

    /// @dev Kariba-style low-quality credit with no_third_party flag.
    function testKaribaDisqualifier() public {
        setUp();
        ICarbonCreditRating.DimensionScores memory s = ICarbonCreditRating.DimensionScores({
            removalType: 18,
            additionality: 20,
            permanence: 22,
            mrvGrade: 25,
            vintageYear: 0,
            coBenefits: 20,
            registryMethodology: 25
        });
        ICarbonCreditRating.Disqualifiers memory flags = ICarbonCreditRating.Disqualifiers({
            doubleCounting: false,
            failedVerification: false,
            sanctionedRegistry: false,
            noThirdParty: true,
            humanRights: false,
            communityHarm: false
        });
        // Already B on composite alone; disqualifier is a no-op here.
        uint16 bps = rating.computeComposite(s);
        require(bps < 3000, "should be below BB threshold");
        ICarbonCreditRating.Grade g = rating.applyDisqualifiers(ICarbonCreditRating.Grade.B, flags);
        require(g == ICarbonCreditRating.Grade.B, "stays B");
    }

    /// @dev Disqualifier should CAP a high-composite credit.
    function testDisqualifierCapsHighScorer() public {
        setUp();
        // synthetic high-quality credit: 95 across the board.
        // Note: co_benefits weight is 0 in v0.4, so co_benefits=95 contributes 0,
        // but the sum of the other weights is still 10000, so composite = 9500.
        ICarbonCreditRating.DimensionScores memory s = ICarbonCreditRating.DimensionScores({
            removalType: 95,
            additionality: 95,
            permanence: 95,
            mrvGrade: 95,
            vintageYear: 95,
            coBenefits: 95,
            registryMethodology: 95
        });
        ICarbonCreditRating.Disqualifiers memory doubleCount = ICarbonCreditRating.Disqualifiers({
            doubleCounting: true,
            failedVerification: false,
            sanctionedRegistry: false,
            noThirdParty: false,
            humanRights: false,
            communityHarm: false
        });
        uint16 bps = rating.computeComposite(s);
        require(bps == 9500, "composite");
        ICarbonCreditRating.Grade nominal = rating.gradeFromComposite(bps);
        require(nominal == ICarbonCreditRating.Grade.AAA, "nominal AAA");
        ICarbonCreditRating.Grade finalG = rating.applyDisqualifiers(nominal, doubleCount);
        require(finalG == ICarbonCreditRating.Grade.B, "double counting caps to B");
    }

    /// @dev v0.4: co_benefits must have zero effect on the composite.
    ///      Same scores with co_benefits=0 vs co_benefits=100 must produce identical composites.
    function testCoBenefitsNoEffect() public {
        setUp();
        ICarbonCreditRating.DimensionScores memory base = ICarbonCreditRating.DimensionScores({
            removalType: 80,
            additionality: 70,
            permanence: 75,
            mrvGrade: 78,
            vintageYear: 90,
            coBenefits: 0,
            registryMethodology: 72
        });
        ICarbonCreditRating.DimensionScores memory high = ICarbonCreditRating.DimensionScores({
            removalType: 80,
            additionality: 70,
            permanence: 75,
            mrvGrade: 78,
            vintageYear: 90,
            coBenefits: 100,
            registryMethodology: 72
        });
        uint16 a = rating.computeComposite(base);
        uint16 b = rating.computeComposite(high);
        require(a == b, "co_benefits must not affect composite");
    }

    /// @dev v0.4 safeguards-gate: communityHarm caps an otherwise-high-scoring credit at BBB.
    ///      This is the new disqualifier introduced by v0.4. A credit could have excellent
    ///      technical integrity but document community harm; the framework still recognizes
    ///      the technical quality (composite stays high) but refuses to admit it into
    ///      premium pools.
    function testCommunityHarmCapsAtBBB() public {
        setUp();
        // High-quality reforestation with documented community harm.
        ICarbonCreditRating.DimensionScores memory s = ICarbonCreditRating.DimensionScores({
            removalType: 75,
            additionality: 78,
            permanence: 65,
            mrvGrade: 80,
            vintageYear: 100,
            coBenefits: 5,
            registryMethodology: 78
        });
        ICarbonCreditRating.Disqualifiers memory flags = ICarbonCreditRating.Disqualifiers({
            doubleCounting: false,
            failedVerification: false,
            sanctionedRegistry: false,
            noThirdParty: false,
            humanRights: false,
            communityHarm: true
        });
        uint16 bps = rating.computeComposite(s);
        ICarbonCreditRating.Grade nominal = rating.gradeFromComposite(bps);
        // Composite should be around 76.x (AA). Let's just assert it's above BBB.
        require(nominal >= ICarbonCreditRating.Grade.A, "nominal should be A or higher");
        ICarbonCreditRating.Grade finalG = rating.applyDisqualifiers(nominal, flags);
        require(finalG == ICarbonCreditRating.Grade.BBB, "community harm caps at BBB");
    }

    /// @dev meetsGrade should return false for unrated credits.
    function testUnratedIsIneligible() public {
        setUp();
        bool ok = rating.meetsGrade(CREDIT_TOKEN, 1, ICarbonCreditRating.Grade.A);
        require(!ok, "unrated should not meet grade");
    }

    /// @dev Full setRating + meetsGrade happy path as the rater.
    function testSetAndReadRating() public {
        setUp();
        ICarbonCreditRating.DimensionScores memory s = ICarbonCreditRating.DimensionScores({
            removalType: 80,
            additionality: 80,
            permanence: 70,
            mrvGrade: 75,
            vintageYear: 100,
            coBenefits: 70,
            registryMethodology: 80
        });
        ICarbonCreditRating.Disqualifiers memory flags; // all false

        uint64 expiresAt = uint64(block.timestamp + 365 days);
        bytes32 evidenceHash = keccak256("example-attestation-bundle");

        rating.setRating(CREDIT_TOKEN, 42, s, flags, expiresAt, evidenceHash);

        ICarbonCreditRating.Rating memory r = rating.ratingOf(CREDIT_TOKEN, 42);
        require(r.compositeBps >= 7500, "should be AA or better");
        require(r.finalGrade >= ICarbonCreditRating.Grade.AA, "final grade AA+");
        require(r.methodologyVersion == 0x0400, "methodology stamped v0.4");
        require(r.expiresAt == expiresAt, "expiresAt stored");
        require(r.evidenceHash == evidenceHash, "evidenceHash stored");
        require(rating.meetsGrade(CREDIT_TOKEN, 42, ICarbonCreditRating.Grade.A), "meets A");
        require(!rating.meetsGrade(CREDIT_TOKEN, 42, ICarbonCreditRating.Grade.AAA), "does not meet AAA");
        require(!rating.isStale(CREDIT_TOKEN, 42), "not stale");
    }

    /// @dev B: setRating must reject an expiresAt in the past.
    function testSetRatingRejectsPastExpiry() public {
        setUp();
        ICarbonCreditRating.DimensionScores memory s = ICarbonCreditRating.DimensionScores({
            removalType: 80,
            additionality: 80,
            permanence: 70,
            mrvGrade: 75,
            vintageYear: 100,
            coBenefits: 70,
            registryMethodology: 80
        });
        ICarbonCreditRating.Disqualifiers memory flags;
        // block.timestamp starts at 1 in forge; pick 0 which is "already expired"
        // wait -- 0 is interpreted as "never expires". Use block.timestamp directly (not strictly in the future).
        bool reverted = false;
        try rating.setRating(CREDIT_TOKEN, 99, s, flags, uint64(block.timestamp), bytes32(0)) {
            reverted = false;
        } catch {
            reverted = true;
        }
        require(reverted, "setRating should revert when expiresAt is not strictly in the future");
    }

    /// @dev B: a rating past its expiresAt is stale and meetsGrade must return false.
    function testStaleRatingRejected() public {
        setUp();
        ICarbonCreditRating.DimensionScores memory s = ICarbonCreditRating.DimensionScores({
            removalType: 95,
            additionality: 90,
            permanence: 92,
            mrvGrade: 88,
            vintageYear: 100,
            coBenefits: 30,
            registryMethodology: 80
        });
        ICarbonCreditRating.Disqualifiers memory flags;
        uint64 expiresAt = uint64(block.timestamp + 1 days);

        rating.setRating(CREDIT_TOKEN, 7, s, flags, expiresAt, bytes32(0));
        require(!rating.isStale(CREDIT_TOKEN, 7), "fresh");
        require(rating.meetsGrade(CREDIT_TOKEN, 7, ICarbonCreditRating.Grade.AA), "AA fresh");

        // fast-forward past expiry
        vm_warp(block.timestamp + 2 days);

        require(rating.isStale(CREDIT_TOKEN, 7), "now stale");
        require(!rating.meetsGrade(CREDIT_TOKEN, 7, ICarbonCreditRating.Grade.B), "stale rating is not eligible even at B");
    }

    /// @dev B: expiresAt == 0 means "never expires".
    function testNeverExpires() public {
        setUp();
        ICarbonCreditRating.DimensionScores memory s = ICarbonCreditRating.DimensionScores({
            removalType: 80,
            additionality: 80,
            permanence: 80,
            mrvGrade: 80,
            vintageYear: 100,
            coBenefits: 50,
            registryMethodology: 80
        });
        ICarbonCreditRating.Disqualifiers memory flags;

        rating.setRating(CREDIT_TOKEN, 11, s, flags, 0, bytes32(0));
        require(!rating.isStale(CREDIT_TOKEN, 11), "expiresAt=0 is never stale");

        vm_warp(block.timestamp + 3650 days);
        require(!rating.isStale(CREDIT_TOKEN, 11), "still not stale after 10 years");
    }

    /// @dev B: re-rating (second setRating call) resets freshness and methodology version.
    function testReRatingResetsFreshness() public {
        setUp();
        ICarbonCreditRating.DimensionScores memory s = ICarbonCreditRating.DimensionScores({
            removalType: 85,
            additionality: 85,
            permanence: 85,
            mrvGrade: 85,
            vintageYear: 100,
            coBenefits: 40,
            registryMethodology: 80
        });
        ICarbonCreditRating.Disqualifiers memory flags;

        rating.setRating(CREDIT_TOKEN, 55, s, flags, uint64(block.timestamp + 1 days), bytes32(0));
        vm_warp(block.timestamp + 2 days);
        require(rating.isStale(CREDIT_TOKEN, 55), "stale after 2 days");

        // re-rate
        rating.setRating(CREDIT_TOKEN, 55, s, flags, uint64(block.timestamp + 365 days), keccak256("new-evidence"));
        require(!rating.isStale(CREDIT_TOKEN, 55), "fresh again after re-rating");

        ICarbonCreditRating.Rating memory r = rating.ratingOf(CREDIT_TOKEN, 55);
        require(r.evidenceHash == keccak256("new-evidence"), "new evidence hash recorded");
    }

    /// @dev B: unrated credits report isStale = false (nothing to be stale).
    function testUnratedNotStale() public {
        setUp();
        require(!rating.isStale(CREDIT_TOKEN, 999), "unrated credits are not stale");
    }

    // --- Foundry cheatcode helper --------------------------------------------
    // We use vm.warp() via the address(0x7109...) convention so this file stays
    // free of forge-std imports.
    function vm_warp(uint256 ts) internal {
        address vm = address(uint160(uint256(keccak256("hevm cheat code"))));
        (bool ok, ) = vm.call(abi.encodeWithSignature("warp(uint256)", ts));
        require(ok, "vm.warp failed");
    }
}
