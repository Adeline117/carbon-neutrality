// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Script, console2} from "forge-std/Script.sol";
import {CarbonCreditRating} from "../contracts/CarbonCreditRating.sol";
import {QualityGatedPool} from "../contracts/QualityGatedPool.sol";
import {ICarbonCreditRating} from "../contracts/ICarbonCreditRating.sol";
import {MockCarbonCredit} from "../contracts/MockCarbonCredit.sol";

/// @notice v0.4.1 Base Sepolia deployment script.
///
/// Deploys:
///   1. CarbonCreditRating (rater = msg.sender)
///   2. QualityGatedPool("Premium AA+", minGrade = AA)
///   3. QualityGatedPool("Standard A+",  minGrade = A)
///
/// Usage (from repo root):
///   source .env
///   forge script script/Deploy.s.sol \
///       --rpc-url $BASE_SEPOLIA_RPC_URL \
///       --broadcast \
///       --verify \
///       --etherscan-api-key $BASESCAN_API_KEY \
///       -vvv
///
/// After this runs, pipe the printed addresses into script/SeedRatings.s.sol
/// by setting the RATING_ADDRESS env var, then run SeedRatings to populate
/// the contract with the 14 tokenized-pilot credits.
contract Deploy is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("DEPLOYER_PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        address deployer = vm.addr(deployerPrivateKey);

        // 1. Rating contract with deployer as the initial (and only) rater.
        CarbonCreditRating rating = new CarbonCreditRating(deployer);
        console2.log("CarbonCreditRating:", address(rating));

        // 2. AA-gated pool (premium tier)
        QualityGatedPool premiumPool = new QualityGatedPool(
            "Premium Carbon Pool (v0.4.1 AA+)",
            ICarbonCreditRating(address(rating)),
            ICarbonCreditRating.Grade.AA
        );
        console2.log("Premium AA+ Pool:", address(premiumPool));

        // 3. A-gated pool (standard tier)
        QualityGatedPool standardPool = new QualityGatedPool(
            "Standard Carbon Pool (v0.4.1 A+)",
            ICarbonCreditRating(address(rating)),
            ICarbonCreditRating.Grade.A
        );
        console2.log("Standard A+ Pool:", address(standardPool));

        vm.stopBroadcast();

        console2.log("");
        console2.log("=====================================================");
        console2.log("Deployment complete. Next steps:");
        console2.log("  1. Save the rating address above to RATING_ADDRESS in .env");
        console2.log("  2. Run: forge script script/SeedRatings.s.sol --rpc-url $BASE_SEPOLIA_RPC_URL --broadcast -vvv");
        console2.log("  3. Update README.md 'Try it on Base Sepolia' section with the addresses above");
        console2.log("  4. Run: python3 tools/snapshot.py to generate docs/api/v0.4.1/ratings.json");
        console2.log("=====================================================");
    }
}
