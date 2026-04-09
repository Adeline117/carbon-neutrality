// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title IEASMinimal
/// @notice Minimal interface for reading attestations from the Ethereum
///         Attestation Service. Only the fields our adapter needs are included.
///         Full EAS interface: https://docs.attest.org/
/// @dev    EAS is deployed on Ethereum mainnet, Base, Optimism, Arbitrum,
///         Scroll, Linea, and Polygon. The adapter is chain-agnostic; point
///         it at the EAS address for your target chain.
interface IEASMinimal {
    struct Attestation {
        bytes32 uid;
        bytes32 schema;
        uint64 time;
        uint64 expirationTime;
        uint64 revocationTime;
        bytes32 refUID;
        address recipient;
        address attester;
        bool revocable;
        bytes data;
    }

    /// @notice Fetch a single attestation by its unique identifier.
    function getAttestation(bytes32 uid) external view returns (Attestation memory);
}
