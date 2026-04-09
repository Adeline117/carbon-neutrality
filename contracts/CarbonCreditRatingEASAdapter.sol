// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ICarbonCreditRating} from "./ICarbonCreditRating.sol";
import {CarbonCreditRating} from "./CarbonCreditRating.sol";
import {IEASMinimal} from "./IEASMinimal.sol";

/// @title CarbonCreditRatingEASAdapter
/// @notice v0.6 decentralized rater adapter. Relays EAS attestations from
///         trusted attesters (registries) into the CarbonCreditRating contract.
///
///         Design pattern: Option A2 from docs/decentralized-rater-design.md.
///         The adapter maintains an allowlist of trusted attester addresses
///         (corresponding to major carbon registries: Verra, Gold Standard,
///         Puro, Isometric, ICVCM, Rainbow, etc.). Anyone can call `relay()`
///         with an EAS attestation UID; the adapter verifies the attestation
///         is from a trusted attester, not revoked, and matches the expected
///         schema, then decodes the dimension scores and writes them to the
///         rating contract.
///
///         Implementation reference: Hypercerts evaluator registry pattern
///         (hypercerts.org) and GainForest Ecocerts schema
///         (github.com/hypercerts-org/ecocerts).
///
/// @dev    PRELIMINARY PROTOTYPE. Production deployment should:
///         - Use a timelocked multisig for allowlist governance
///         - Add rate limiting (max 1 rating per credit per attester per window)
///         - Emit richer events for indexing
///         - Support batch relay for gas efficiency
contract CarbonCreditRatingEASAdapter {
    // ------------------------------------------------------------------
    // Immutables
    // ------------------------------------------------------------------
    CarbonCreditRating public immutable ratingContract;
    IEASMinimal public immutable eas;
    bytes32 public immutable schemaId;

    // ------------------------------------------------------------------
    // State
    // ------------------------------------------------------------------
    address public owner;
    mapping(address => bool) public isTrustedAttester;
    uint256 public trustedAttesterCount;

    // ------------------------------------------------------------------
    // Errors
    // ------------------------------------------------------------------
    error NotOwner();
    error AttestationRevoked(bytes32 uid);
    error UntrustedAttester(address attester);
    error SchemaMismatch(bytes32 got, bytes32 want);
    error AttestationExpired(bytes32 uid);

    // ------------------------------------------------------------------
    // Events
    // ------------------------------------------------------------------
    event AttesterSet(address indexed attester, bool trusted);
    event RatingRelayed(
        bytes32 indexed attestationUid,
        address indexed creditToken,
        uint256 indexed tokenId,
        address attester
    );
    event OwnerTransferred(address indexed from, address indexed to);

    // ------------------------------------------------------------------
    // Modifiers
    // ------------------------------------------------------------------
    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    // ------------------------------------------------------------------
    // Constructor
    // ------------------------------------------------------------------
    /// @param _ratingContract The CarbonCreditRating contract to write to.
    ///        The adapter must be added as a rater via `setRater(adapter, true)`.
    /// @param _eas The EAS contract on this chain.
    /// @param _schemaId The EAS schema UID for carbon credit quality ratings.
    constructor(
        CarbonCreditRating _ratingContract,
        IEASMinimal _eas,
        bytes32 _schemaId
    ) {
        ratingContract = _ratingContract;
        eas = _eas;
        schemaId = _schemaId;
        owner = msg.sender;
        emit OwnerTransferred(address(0), msg.sender);
    }

    // ------------------------------------------------------------------
    // Admin
    // ------------------------------------------------------------------
    function setAttester(address attester, bool trusted) external onlyOwner {
        if (isTrustedAttester[attester] != trusted) {
            isTrustedAttester[attester] = trusted;
            if (trusted) {
                trustedAttesterCount++;
            } else {
                trustedAttesterCount--;
            }
            emit AttesterSet(attester, trusted);
        }
    }

    function transferOwnership(address newOwner) external onlyOwner {
        emit OwnerTransferred(owner, newOwner);
        owner = newOwner;
    }

    // ------------------------------------------------------------------
    // Relay
    // ------------------------------------------------------------------
    /// @notice Pull an EAS attestation and write its decoded rating to the
    ///         CarbonCreditRating contract. Anyone can call this; the adapter
    ///         verifies the attestation's provenance.
    /// @param attestationUid The EAS attestation UID to relay.
    /// @param creditToken The ERC-20 token address of the credit being rated.
    /// @param tokenId The token ID (0 for ERC-20 credits).
    function relay(
        bytes32 attestationUid,
        address creditToken,
        uint256 tokenId
    ) external {
        IEASMinimal.Attestation memory att = eas.getAttestation(attestationUid);

        // Verify schema
        if (att.schema != schemaId) revert SchemaMismatch(att.schema, schemaId);

        // Verify not revoked
        if (att.revocationTime != 0) revert AttestationRevoked(attestationUid);

        // Verify not expired (EAS-level expiry, separate from our expiresAt)
        if (att.expirationTime != 0 && block.timestamp >= att.expirationTime) {
            revert AttestationExpired(attestationUid);
        }

        // Verify trusted attester
        if (!isTrustedAttester[att.attester]) revert UntrustedAttester(att.attester);

        // Decode the attestation data.
        // Schema: (DimensionScores, DimensionStds, Disqualifiers, uint64 expiresAt, bytes32 evidenceHash)
        (
            ICarbonCreditRating.DimensionScores memory scores,
            ICarbonCreditRating.DimensionStds memory stds,
            ICarbonCreditRating.Disqualifiers memory flags,
            uint64 expiresAt,
            bytes32 evidenceHash
        ) = abi.decode(
            att.data,
            (
                ICarbonCreditRating.DimensionScores,
                ICarbonCreditRating.DimensionStds,
                ICarbonCreditRating.Disqualifiers,
                uint64,
                bytes32
            )
        );

        // Relay to the rating contract. The adapter must be an authorized rater.
        ratingContract.setRating(creditToken, tokenId, scores, stds, flags, expiresAt, evidenceHash);

        emit RatingRelayed(attestationUid, creditToken, tokenId, att.attester);
    }
}
