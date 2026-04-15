// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title GeneralizationTest
/// @notice Proves the ERC-CCQR interface is reusable across non-carbon domains.
///         Deploys BiodiversityCreditGate and RenewableEnergyCertGate with the
///         same CarbonCreditRating backend, sets dummy ratings, and verifies
///         that meetsGrade() gates work identically for all asset types.
///
///         This is the on-chain proof artifact for the WWW 2027 generalization
///         argument (Section 7.1).

import {CarbonCreditRating} from "../CarbonCreditRating.sol";
import {ICarbonCreditRating} from "../ICarbonCreditRating.sol";
import {BiodiversityCreditGate} from "../examples/BiodiversityCreditGate.sol";
import {RenewableEnergyCertGate} from "../examples/RenewableEnergyCertGate.sol";

contract GeneralizationTest {
    CarbonCreditRating rating;
    BiodiversityCreditGate bioGate;
    RenewableEnergyCertGate recGate;

    // Dummy token addresses representing non-carbon assets
    address constant BIO_TOKEN = address(0xB10D);   // biodiversity credit
    address constant REC_TOKEN = address(0x3EC0);   // renewable energy certificate

    function _defaultStds() internal pure returns (ICarbonCreditRating.DimensionStds memory) {
        return ICarbonCreditRating.DimensionStds({
            removalType: 4, additionality: 9, permanence: 4,
            mrvGrade: 7, vintageYear: 10, coBenefits: 9, registryMethodology: 11
        });
    }

    function setUp() public {
        rating = new CarbonCreditRating(address(this));
        // BiodiversityCreditGate: require grade AA (4) minimum
        bioGate = new BiodiversityCreditGate(
            ICarbonCreditRating(address(rating)),
            ICarbonCreditRating.Grade.AA
        );
        // RenewableEnergyCertGate: require grade A (3) minimum
        recGate = new RenewableEnergyCertGate(
            ICarbonCreditRating(address(rating)),
            ICarbonCreditRating.Grade.A
        );
    }

    /// @dev High-quality biodiversity credit (AAA) passes the AA gate.
    function testBiodiversityHighQualityPasses() public {
        setUp();

        ICarbonCreditRating.DimensionScores memory scores = ICarbonCreditRating.DimensionScores({
            removalType: 95, additionality: 92, permanence: 90,
            mrvGrade: 88, vintageYear: 95, coBenefits: 80, registryMethodology: 85
        });
        ICarbonCreditRating.Disqualifiers memory noFlags;
        uint64 expiresAt = uint64(block.timestamp + 365 days);

        rating.setRating(BIO_TOKEN, 0, scores, _defaultStds(), noFlags, expiresAt, keccak256("bio-high"));

        // Should pass: meetsGrade returns true
        require(rating.meetsGrade(BIO_TOKEN, 0, ICarbonCreditRating.Grade.AA), "bio AAA should meet AA");

        // Gate contract should return composite without reverting
        uint16 composite = bioGate.checkDeposit(BIO_TOKEN, 0);
        require(composite > 0, "composite should be positive");
    }

    /// @dev Low-quality biodiversity credit (BB) rejected by the AA gate.
    function testBiodiversityLowQualityRejected() public {
        setUp();

        ICarbonCreditRating.DimensionScores memory scores = ICarbonCreditRating.DimensionScores({
            removalType: 30, additionality: 35, permanence: 25,
            mrvGrade: 40, vintageYear: 20, coBenefits: 50, registryMethodology: 30
        });
        ICarbonCreditRating.Disqualifiers memory noFlags;
        uint64 expiresAt = uint64(block.timestamp + 365 days);

        rating.setRating(BIO_TOKEN, 1, scores, _defaultStds(), noFlags, expiresAt, keccak256("bio-low"));

        // Should fail: BB < AA
        require(!rating.meetsGrade(BIO_TOKEN, 1, ICarbonCreditRating.Grade.AA), "bio BB should not meet AA");

        // Gate contract should revert
        bool rejected = false;
        try bioGate.checkDeposit(BIO_TOKEN, 1) {
            rejected = false;
        } catch {
            rejected = true;
        }
        require(rejected, "low-quality biodiversity credit should be rejected by AA gate");
    }

    /// @dev High-quality REC (AA) passes the A gate.
    function testRECHighQualityPasses() public {
        setUp();

        ICarbonCreditRating.DimensionScores memory scores = ICarbonCreditRating.DimensionScores({
            removalType: 85, additionality: 80, permanence: 82,
            mrvGrade: 78, vintageYear: 90, coBenefits: 70, registryMethodology: 75
        });
        ICarbonCreditRating.Disqualifiers memory noFlags;
        uint64 expiresAt = uint64(block.timestamp + 365 days);

        rating.setRating(REC_TOKEN, 0, scores, _defaultStds(), noFlags, expiresAt, keccak256("rec-high"));

        // Should pass: AA >= A
        require(rating.meetsGrade(REC_TOKEN, 0, ICarbonCreditRating.Grade.A), "REC AA should meet A");

        uint16 composite = recGate.checkDeposit(REC_TOKEN, 0);
        require(composite > 0, "REC composite should be positive");
    }

    /// @dev Low-quality REC (BB) rejected by the A gate.
    function testRECLowQualityRejected() public {
        setUp();

        ICarbonCreditRating.DimensionScores memory scores = ICarbonCreditRating.DimensionScores({
            removalType: 25, additionality: 30, permanence: 20,
            mrvGrade: 35, vintageYear: 15, coBenefits: 40, registryMethodology: 25
        });
        ICarbonCreditRating.Disqualifiers memory noFlags;
        uint64 expiresAt = uint64(block.timestamp + 365 days);

        rating.setRating(REC_TOKEN, 1, scores, _defaultStds(), noFlags, expiresAt, keccak256("rec-low"));

        require(!rating.meetsGrade(REC_TOKEN, 1, ICarbonCreditRating.Grade.A), "REC BB should not meet A");

        bool rejected = false;
        try recGate.checkDeposit(REC_TOKEN, 1) {
            rejected = false;
        } catch {
            rejected = true;
        }
        require(rejected, "low-quality REC should be rejected by A gate");
    }

    /// @dev Unrated asset rejected by both gates.
    function testUnratedRejectedByBothGates() public {
        setUp();

        address UNKNOWN = address(0xDEAD);

        bool bioRejected = false;
        try bioGate.checkDeposit(UNKNOWN, 0) {
            bioRejected = false;
        } catch {
            bioRejected = true;
        }
        require(bioRejected, "unrated should be rejected by biodiversity gate");

        bool recRejected = false;
        try recGate.checkDeposit(UNKNOWN, 0) {
            recRejected = false;
        } catch {
            recRejected = true;
        }
        require(recRejected, "unrated should be rejected by REC gate");
    }

    /// @dev Same rating contract serves both biodiversity and REC gates
    ///      simultaneously -- proving multi-domain composability.
    function testMultiDomainFromSingleRatingContract() public {
        setUp();

        ICarbonCreditRating.Disqualifiers memory noFlags;
        uint64 expiresAt = uint64(block.timestamp + 365 days);

        // Rate a biodiversity credit as AAA
        ICarbonCreditRating.DimensionScores memory bioScores = ICarbonCreditRating.DimensionScores({
            removalType: 95, additionality: 92, permanence: 90,
            mrvGrade: 88, vintageYear: 95, coBenefits: 80, registryMethodology: 85
        });
        rating.setRating(BIO_TOKEN, 42, bioScores, _defaultStds(), noFlags, expiresAt, keccak256("bio-42"));

        // Rate a REC as A
        ICarbonCreditRating.DimensionScores memory recScores = ICarbonCreditRating.DimensionScores({
            removalType: 65, additionality: 62, permanence: 60,
            mrvGrade: 58, vintageYear: 70, coBenefits: 55, registryMethodology: 60
        });
        rating.setRating(REC_TOKEN, 42, recScores, _defaultStds(), noFlags, expiresAt, keccak256("rec-42"));

        // Both can be queried from the same rating contract
        uint16 bioComposite = bioGate.checkDeposit(BIO_TOKEN, 42);
        uint16 recComposite = recGate.checkDeposit(REC_TOKEN, 42);

        require(bioComposite > recComposite, "AAA bio should have higher composite than A REC");

        // Verify grades via ratingOf
        ICarbonCreditRating.Rating memory bioRating = rating.ratingOf(BIO_TOKEN, 42);
        ICarbonCreditRating.Rating memory recRating = rating.ratingOf(REC_TOKEN, 42);

        require(uint8(bioRating.finalGrade) > uint8(recRating.finalGrade),
            "biodiversity AAA grade should exceed REC A grade");
    }
}
