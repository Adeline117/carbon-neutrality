// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Script, console2} from "forge-std/Script.sol";
import {stdJson} from "forge-std/StdJson.sol";
import {CarbonCreditRating} from "../contracts/CarbonCreditRating.sol";
import {ICarbonCreditRating} from "../contracts/ICarbonCreditRating.sol";
import {MockCarbonCredit} from "../contracts/MockCarbonCredit.sol";

/// @notice v0.4.1 seed script. Deploys 14 MockCarbonCredit tokens corresponding
///         to the data/tokenized-pilot/ rows and calls setRating() on each.
///
/// Reads script/seed/tokenized_pilot.json for the 14 credits and their
/// author-assigned v0.4 dimension scores. Requires RATING_ADDRESS in the
/// environment (output of Deploy.s.sol).
///
/// PRELIMINARY AUTHOR ATTESTATIONS — NOT ENDORSED BY ANY REGISTRY, RATING
/// AGENCY, OR REAL-WORLD CARBON MARKET PARTICIPANT. The ratings written by
/// this script are author judgment for a Base Sepolia testnet demonstration.
contract SeedRatings is Script {
    using stdJson for string;

    struct SeedRow {
        string id;
        string name;
        string symbol;
        uint8 removalType;
        uint8 additionality;
        uint8 permanence;
        uint8 mrvGrade;
        uint8 vintageYear;
        uint8 coBenefits;
        uint8 registryMethodology;
        bool doubleCounting;
        bool failedVerification;
        bool sanctionedRegistry;
        bool noThirdParty;
        bool humanRights;
        bool communityHarm;
    }

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("DEPLOYER_PRIVATE_KEY");
        address ratingAddress = vm.envAddress("RATING_ADDRESS");
        address deployer = vm.addr(deployerPrivateKey);

        CarbonCreditRating rating = CarbonCreditRating(ratingAddress);

        // The JSON is a top-level array, so we parse each index individually.
        string memory json = vm.readFile("script/seed/tokenized_pilot.json");
        uint256 n = 14; // known at generation time; script/seed/tokenized_pilot.json is hand-audited

        vm.startBroadcast(deployerPrivateKey);

        // One-year freshness window; deployer can refresh by re-running the script.
        uint64 expiresAt = uint64(block.timestamp + 365 days);

        for (uint256 i = 0; i < n; i++) {
            SeedRow memory row = _readRow(json, i);

            // 1. Deploy a mock ERC-20 representing this credit
            MockCarbonCredit mock = new MockCarbonCredit(row.name, row.symbol, deployer);
            mock.mint(deployer, 1_000 * 1e18);

            // 2. Write the rating under (mockAddress, tokenId = 0)
            ICarbonCreditRating.DimensionScores memory scores = ICarbonCreditRating.DimensionScores({
                removalType: row.removalType,
                additionality: row.additionality,
                permanence: row.permanence,
                mrvGrade: row.mrvGrade,
                vintageYear: row.vintageYear,
                coBenefits: row.coBenefits,
                registryMethodology: row.registryMethodology
            });
            ICarbonCreditRating.Disqualifiers memory flags = ICarbonCreditRating.Disqualifiers({
                doubleCounting: row.doubleCounting,
                failedVerification: row.failedVerification,
                sanctionedRegistry: row.sanctionedRegistry,
                noThirdParty: row.noThirdParty,
                humanRights: row.humanRights,
                communityHarm: row.communityHarm
            });
            // evidenceHash = keccak of the credit id + methodology version; real provenance
            // would point to an IPFS bundle of the PDD + verification reports.
            bytes32 evidenceHash = keccak256(abi.encodePacked(row.id, "v0.4.1"));

            rating.setRating(address(mock), 0, scores, flags, expiresAt, evidenceHash);

            console2.log(row.id, address(mock));
        }

        vm.stopBroadcast();

        console2.log("");
        console2.log("=====================================================");
        console2.log("Seeded 14 tokenized-pilot credits as MockCarbonCredit ERC-20s.");
        console2.log("Addresses are logged above; copy them into docs/v0.4.1-deployment-notes.md");
        console2.log("Then run: python3 tools/snapshot.py to generate the public read API");
        console2.log("=====================================================");
    }

    function _readRow(string memory json, uint256 i) private view returns (SeedRow memory row) {
        string memory k = string.concat("$[", vm.toString(i), "]");
        row.id     = json.readString(string.concat(k, ".id"));
        row.name   = json.readString(string.concat(k, ".name"));
        row.symbol = json.readString(string.concat(k, ".symbol"));
        row.removalType          = uint8(json.readUint(string.concat(k, ".scores.removal_type")));
        row.additionality        = uint8(json.readUint(string.concat(k, ".scores.additionality")));
        row.permanence           = uint8(json.readUint(string.concat(k, ".scores.permanence")));
        row.mrvGrade             = uint8(json.readUint(string.concat(k, ".scores.mrv_grade")));
        row.vintageYear          = uint8(json.readUint(string.concat(k, ".scores.vintage_year")));
        row.coBenefits           = uint8(json.readUint(string.concat(k, ".scores.co_benefits")));
        row.registryMethodology  = uint8(json.readUint(string.concat(k, ".scores.registry_methodology")));
        bool[] memory flags = json.readBoolArray(string.concat(k, ".flags"));
        row.doubleCounting      = flags[0];
        row.failedVerification  = flags[1];
        row.sanctionedRegistry  = flags[2];
        row.noThirdParty        = flags[3];
        row.humanRights         = flags[4];
        row.communityHarm       = flags[5];
    }

}
