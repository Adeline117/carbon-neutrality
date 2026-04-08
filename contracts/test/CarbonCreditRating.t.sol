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

    /// @dev Climeworks Orca-style input. Matches pilot C001: composite 86.8 -> 8680 bps -> AA.
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
        // 98*2000 + 95*2000 + 98*1500 + 92*1500 + 100*1000 + 15*1000 + 82*1000
        // = 196000 + 190000 + 147000 + 138000 + 100000 + 15000 + 82000
        // = 868000 / 100 = 8680
        require(bps == 8680, "composite mismatch");
        require(rating.gradeFromComposite(bps) == ICarbonCreditRating.Grade.AA, "grade mismatch");
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
            humanRights: false
        });
        // Already B on composite alone (~19 bps region); disqualifier is a no-op here.
        uint16 bps = rating.computeComposite(s);
        require(bps < 3000, "should be below BB threshold");
        ICarbonCreditRating.Grade g = rating.applyDisqualifiers(ICarbonCreditRating.Grade.B, flags);
        require(g == ICarbonCreditRating.Grade.B, "stays B");
    }

    /// @dev Disqualifier should CAP a high-composite credit.
    function testDisqualifierCapsHighScorer() public {
        setUp();
        // synthetic high-quality credit: 95 across the board -> 9500 bps -> AAA
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
            humanRights: false
        });
        uint16 bps = rating.computeComposite(s);
        require(bps == 9500, "composite");
        ICarbonCreditRating.Grade nominal = rating.gradeFromComposite(bps);
        require(nominal == ICarbonCreditRating.Grade.AAA, "nominal AAA");
        ICarbonCreditRating.Grade finalG = rating.applyDisqualifiers(nominal, doubleCount);
        require(finalG == ICarbonCreditRating.Grade.B, "double counting caps to B");
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

        rating.setRating(CREDIT_TOKEN, 42, s, flags);

        ICarbonCreditRating.Rating memory r = rating.ratingOf(CREDIT_TOKEN, 42);
        require(r.compositeBps >= 7500, "should be AA or better");
        require(r.finalGrade >= ICarbonCreditRating.Grade.AA, "final grade AA+");
        require(rating.meetsGrade(CREDIT_TOKEN, 42, ICarbonCreditRating.Grade.A), "meets A");
        require(!rating.meetsGrade(CREDIT_TOKEN, 42, ICarbonCreditRating.Grade.AAA), "does not meet AAA");
    }

}
