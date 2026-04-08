// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ICarbonCreditRating} from "./ICarbonCreditRating.sol";

/// @notice Minimal ERC-20-like interface. We avoid importing OpenZeppelin to keep
///         the prototype self-contained.
interface IERC20Minimal {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

/// @title QualityGatedPool
/// @notice Example quality-tier pool: only accepts deposits of credits whose
///         rating is at or above `minGrade`. Mints pool shares 1:1 for accepted
///         deposits. Mirrors Toucan's BCT pattern but with grade enforcement.
///
/// @dev    This is an illustrative prototype. A production pool would need:
///         - Rating freshness check (stale rating rejected)
///         - Fee handling and treasury
///         - Re-rating on redemption (grade may have changed)
///         - ERC-1155 / ERC-721 support for per-credit identity
///         - Reentrancy guards
contract QualityGatedPool {
    ICarbonCreditRating public immutable ratings;
    ICarbonCreditRating.Grade public immutable minGrade;
    string public name;

    // pool share accounting (ERC-20-ish but intentionally minimal)
    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;

    // accepted credit tokens and balances held by the pool
    mapping(address => uint256) public creditReserves;

    error BelowMinGrade(ICarbonCreditRating.Grade finalGrade, ICarbonCreditRating.Grade required);
    error Unrated();
    error InsufficientShares();

    event Deposit(address indexed user, address indexed creditToken, uint256 tokenId, uint256 amount, uint256 sharesMinted);
    event Withdraw(address indexed user, address indexed creditToken, uint256 amount, uint256 sharesBurned);
    event Transfer(address indexed from, address indexed to, uint256 amount);

    constructor(
        string memory _name,
        ICarbonCreditRating _ratings,
        ICarbonCreditRating.Grade _minGrade
    ) {
        name = _name;
        ratings = _ratings;
        minGrade = _minGrade;
    }

    /// @notice Deposit `amount` of an ERC-20-represented carbon credit.
    ///         The credit's (token, tokenId) must have a final rating >= minGrade.
    ///         For ERC-20 credits where there is no tokenId (pool of a single batch),
    ///         pass tokenId = 0.
    function deposit(address creditToken, uint256 tokenId, uint256 amount) external {
        // grade check -- reverts with a descriptive error if unrated or below threshold
        ICarbonCreditRating.Rating memory r;
        try ratings.ratingOf(creditToken, tokenId) returns (ICarbonCreditRating.Rating memory got) {
            r = got;
        } catch {
            revert Unrated();
        }
        if (uint8(r.finalGrade) < uint8(minGrade)) {
            revert BelowMinGrade(r.finalGrade, minGrade);
        }

        // pull credit
        bool ok = IERC20Minimal(creditToken).transferFrom(msg.sender, address(this), amount);
        require(ok, "transferFrom failed");

        // mint shares 1:1 (no fee, no peg maintenance in this prototype)
        balanceOf[msg.sender] += amount;
        totalSupply += amount;
        creditReserves[creditToken] += amount;

        emit Deposit(msg.sender, creditToken, tokenId, amount, amount);
        emit Transfer(address(0), msg.sender, amount);
    }

    /// @notice Burn pool shares and receive the same amount of a single underlying credit.
    ///         Caller specifies which credit they want (any credit the pool currently holds).
    ///         In a real pool this would be proportional / auction-based.
    function withdraw(address creditToken, uint256 amount) external {
        if (balanceOf[msg.sender] < amount) revert InsufficientShares();
        require(creditReserves[creditToken] >= amount, "insufficient reserves");

        balanceOf[msg.sender] -= amount;
        totalSupply -= amount;
        creditReserves[creditToken] -= amount;

        bool ok = IERC20Minimal(creditToken).transfer(msg.sender, amount);
        require(ok, "transfer failed");

        emit Transfer(msg.sender, address(0), amount);
        emit Withdraw(msg.sender, creditToken, amount, amount);
    }

    /// @notice Plain ERC-20-style transfer of pool shares.
    function transfer(address to, uint256 amount) external returns (bool) {
        if (balanceOf[msg.sender] < amount) revert InsufficientShares();
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }
}
