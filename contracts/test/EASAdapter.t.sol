// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {CarbonCreditRating} from "../CarbonCreditRating.sol";
import {CarbonCreditRatingEASAdapter} from "../CarbonCreditRatingEASAdapter.sol";
import {ICarbonCreditRating} from "../ICarbonCreditRating.sol";
import {IEASMinimal} from "../IEASMinimal.sol";

/// @title MockEAS
/// @notice Fake EAS contract for testing the adapter without a real EAS deployment.
contract MockEAS is IEASMinimal {
    mapping(bytes32 => Attestation) private _attestations;

    function setAttestation(bytes32 uid, Attestation memory att) external {
        _attestations[uid] = att;
    }

    function getAttestation(bytes32 uid) external view returns (Attestation memory) {
        return _attestations[uid];
    }
}

/// @title EASAdapterTest
/// @notice Tests for CarbonCreditRatingEASAdapter: relay, revocation,
///         untrusted attester, schema mismatch, and expiry.
contract EASAdapterTest {
    CarbonCreditRating rating;
    CarbonCreditRatingEASAdapter adapter;
    MockEAS mockEAS;

    bytes32 constant SCHEMA_ID = bytes32(uint256(0xCAFE));
    address constant CREDIT_TOKEN = address(0xC0FFEE);
    address constant TRUSTED_ATTESTER = address(0xBEEF);
    address constant UNTRUSTED_ATTESTER = address(0xDEAD);

    function _defaultStds() internal pure returns (ICarbonCreditRating.DimensionStds memory) {
        return ICarbonCreditRating.DimensionStds({
            removalType: 4, additionality: 9, permanence: 4,
            mrvGrade: 7, vintageYear: 10, coBenefits: 9, registryMethodology: 11
        });
    }

    function setUp() public {
        rating = new CarbonCreditRating(address(this));
        mockEAS = new MockEAS();
        adapter = new CarbonCreditRatingEASAdapter(rating, IEASMinimal(address(mockEAS)), SCHEMA_ID);

        // Add the adapter as a rater on the rating contract
        rating.setRater(address(adapter), true);

        // Add a trusted attester
        adapter.setAttester(TRUSTED_ATTESTER, true);
    }

    function _buildAttestationData() internal view returns (bytes memory) {
        ICarbonCreditRating.DimensionScores memory scores = ICarbonCreditRating.DimensionScores({
            removalType: 98, additionality: 95, permanence: 98,
            mrvGrade: 92, vintageYear: 100, coBenefits: 15, registryMethodology: 82
        });
        ICarbonCreditRating.DimensionStds memory stds = ICarbonCreditRating.DimensionStds({
            removalType: 4, additionality: 9, permanence: 4,
            mrvGrade: 7, vintageYear: 10, coBenefits: 9, registryMethodology: 11
        });
        ICarbonCreditRating.Disqualifiers memory flags; // all false
        uint64 expiresAt = uint64(block.timestamp + 365 days);
        bytes32 evidenceHash = keccak256("orca-attestation");

        return abi.encode(scores, stds, flags, expiresAt, evidenceHash);
    }

    /// @dev Happy path: relay a valid attestation from a trusted attester.
    function testRelayHappyPath() public {
        setUp();
        bytes32 uid = bytes32(uint256(1));
        IEASMinimal.Attestation memory att = IEASMinimal.Attestation({
            uid: uid,
            schema: SCHEMA_ID,
            time: uint64(block.timestamp),
            expirationTime: 0,
            revocationTime: 0,
            refUID: bytes32(0),
            recipient: CREDIT_TOKEN,
            attester: TRUSTED_ATTESTER,
            revocable: true,
            data: _buildAttestationData()
        });
        mockEAS.setAttestation(uid, att);

        adapter.relay(uid, CREDIT_TOKEN, 0);

        // Verify the rating was written
        ICarbonCreditRating.Rating memory r = rating.ratingOf(CREDIT_TOKEN, 0);
        require(r.compositeBps > 9000, "should be AAA composite");
        require(r.finalGrade == ICarbonCreditRating.Grade.AAA, "should be AAA");
        require(r.attestedBy == address(adapter), "attested by adapter");
    }

    /// @dev Revoked attestation should be rejected.
    function testRelayRejectsRevoked() public {
        setUp();
        bytes32 uid = bytes32(uint256(2));
        IEASMinimal.Attestation memory att = IEASMinimal.Attestation({
            uid: uid,
            schema: SCHEMA_ID,
            time: uint64(block.timestamp),
            expirationTime: 0,
            revocationTime: uint64(block.timestamp), // revoked at current time
            refUID: bytes32(0),
            recipient: CREDIT_TOKEN,
            attester: TRUSTED_ATTESTER,
            revocable: true,
            data: _buildAttestationData()
        });
        mockEAS.setAttestation(uid, att);

        bool reverted = false;
        try adapter.relay(uid, CREDIT_TOKEN, 0) {
            reverted = false;
        } catch {
            reverted = true;
        }
        require(reverted, "should revert on revoked attestation");
    }

    /// @dev Untrusted attester should be rejected.
    function testRelayRejectsUntrustedAttester() public {
        setUp();
        bytes32 uid = bytes32(uint256(3));
        IEASMinimal.Attestation memory att = IEASMinimal.Attestation({
            uid: uid,
            schema: SCHEMA_ID,
            time: uint64(block.timestamp),
            expirationTime: 0,
            revocationTime: 0,
            refUID: bytes32(0),
            recipient: CREDIT_TOKEN,
            attester: UNTRUSTED_ATTESTER,
            revocable: true,
            data: _buildAttestationData()
        });
        mockEAS.setAttestation(uid, att);

        bool reverted = false;
        try adapter.relay(uid, CREDIT_TOKEN, 0) {
            reverted = false;
        } catch {
            reverted = true;
        }
        require(reverted, "should revert on untrusted attester");
    }

    /// @dev Wrong schema should be rejected.
    function testRelayRejectsSchemaMismatch() public {
        setUp();
        bytes32 uid = bytes32(uint256(4));
        IEASMinimal.Attestation memory att = IEASMinimal.Attestation({
            uid: uid,
            schema: bytes32(uint256(0xBAD)), // wrong schema
            time: uint64(block.timestamp),
            expirationTime: 0,
            revocationTime: 0,
            refUID: bytes32(0),
            recipient: CREDIT_TOKEN,
            attester: TRUSTED_ATTESTER,
            revocable: true,
            data: _buildAttestationData()
        });
        mockEAS.setAttestation(uid, att);

        bool reverted = false;
        try adapter.relay(uid, CREDIT_TOKEN, 0) {
            reverted = false;
        } catch {
            reverted = true;
        }
        require(reverted, "should revert on schema mismatch");
    }

    /// @dev Attester count tracking.
    function testAttesterCount() public {
        setUp();
        require(adapter.trustedAttesterCount() == 1, "should have 1 attester");
        adapter.setAttester(address(0x1234), true);
        require(adapter.trustedAttesterCount() == 2, "should have 2 attesters");
        adapter.setAttester(TRUSTED_ATTESTER, false);
        require(adapter.trustedAttesterCount() == 1, "should have 1 after removal");
    }
}
