// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Script, console2} from "forge-std/Script.sol";
import {stdJson} from "forge-std/StdJson.sol";
import {CarbonCreditRating} from "../contracts/CarbonCreditRating.sol";
import {QualityGatedPool} from "../contracts/QualityGatedPool.sol";
import {ICarbonCreditRating} from "../contracts/ICarbonCreditRating.sol";
import {MockCarbonCredit} from "../contracts/MockCarbonCredit.sol";

/// @title QualityGatingDemo
/// @notice End-to-end local demonstration of quality gating on the 16 tokenized-pilot
///         credits. Deploys everything from scratch (no RPC needed), deposits into
///         four pools (ungated, BBB-gated, A-gated, AAA-gated), and logs a comparison
///         table showing how pool composition improves with higher gate thresholds.
///
///         Run:  forge script script/QualityGatingDemo.s.sol -vvv
///         Or:   ./script/run-demo.sh
contract QualityGatingDemo is Script {
    using stdJson for string;

    // ── Structs ──────────────────────────────────────────────────────────
    struct CreditInfo {
        string id;
        string creditName;
        string symbol;
        address token;
        uint16 compositeBps;
        ICarbonCreditRating.Grade finalGrade;
    }

    struct PoolStats {
        string poolName;
        uint256 admitted;
        uint256 rejected;
        uint256 compositeSum;  // sum of compositeBps for admitted credits
        uint256 lemonsCount;   // count of admitted credits graded BB or below (the "lemons")
        uint256[6] gradeCounts; // B=0, BB=1, BBB=2, A=3, AA=4, AAA=5
    }

    // ── Seed row (mirrors SeedRatings.s.sol) ─────────────────────────────
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

    // ── Constants ────────────────────────────────────────────────────────
    uint256 constant N = 16;
    uint256 constant DEPOSIT_AMOUNT = 100 * 1e18;

    // ── State ────────────────────────────────────────────────────────────
    CreditInfo[16] credits;
    CarbonCreditRating rating;
    address deployer;

    // ══════════════════════════════════════════════════════════════════════
    //  ENTRY POINT
    // ══════════════════════════════════════════════════════════════════════
    function run() external {
        // Use a deterministic private key for local simulation (no broadcast).
        uint256 pk = 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80;
        deployer = vm.addr(pk);
        vm.startPrank(deployer);

        _logHeader();

        // ── Phase 1: Deploy core contracts ──────────────────────────────
        _setupContracts();

        // ── Phase 2: Deploy & rate 16 credits ───────────────────────────
        _seedCredits();

        // ── Phase 3: Log the credit universe ────────────────────────────
        _logCreditUniverse();

        // ── Phase 4: Deposit into four pools and measure ────────────────
        PoolStats memory ungated  = _runPool("Ungated (no threshold)",        ICarbonCreditRating.Grade.B,   false);
        PoolStats memory bbbGated = _runPool("BBB-Gated (>= BBB)",           ICarbonCreditRating.Grade.BBB, true);
        PoolStats memory aGated   = _runPool("A-Gated (>= A)",              ICarbonCreditRating.Grade.A,   true);
        PoolStats memory aaaGated = _runPool("AAA-Gated (>= AAA)",          ICarbonCreditRating.Grade.AAA, true);

        // ── Phase 5: Comparison table ───────────────────────────────────
        _logComparisonTable(ungated, bbbGated, aGated, aaaGated);

        vm.stopPrank();
    }

    // ══════════════════════════════════════════════════════════════════════
    //  PHASE 1: SETUP
    // ══════════════════════════════════════════════════════════════════════
    function _setupContracts() internal {
        rating = new CarbonCreditRating(deployer);
        console2.log("[Setup] CarbonCreditRating deployed at:", address(rating));
        console2.log("");
    }

    // ══════════════════════════════════════════════════════════════════════
    //  PHASE 2: SEED 16 CREDITS
    // ══════════════════════════════════════════════════════════════════════
    function _seedCredits() internal {
        string memory json = vm.readFile("script/seed/tokenized_pilot.json");
        uint64 expiresAt = uint64(block.timestamp + 365 days);

        for (uint256 i = 0; i < N; i++) {
            SeedRow memory row = _readRow(json, i);

            // Deploy mock ERC-20
            MockCarbonCredit mock = new MockCarbonCredit(row.name, row.symbol, deployer);
            mock.mint(deployer, 10_000 * 1e18); // enough for 4 pools

            // Build rating inputs
            ICarbonCreditRating.DimensionScores memory scores = ICarbonCreditRating.DimensionScores({
                removalType: row.removalType,
                additionality: row.additionality,
                permanence: row.permanence,
                mrvGrade: row.mrvGrade,
                vintageYear: row.vintageYear,
                coBenefits: row.coBenefits,
                registryMethodology: row.registryMethodology
            });
            ICarbonCreditRating.DimensionStds memory stds = ICarbonCreditRating.DimensionStds({
                removalType: 4, additionality: 9, permanence: 4,
                mrvGrade: 7, vintageYear: 10, coBenefits: 9, registryMethodology: 11
            });
            ICarbonCreditRating.Disqualifiers memory flags = ICarbonCreditRating.Disqualifiers({
                doubleCounting: row.doubleCounting,
                failedVerification: row.failedVerification,
                sanctionedRegistry: row.sanctionedRegistry,
                noThirdParty: row.noThirdParty,
                humanRights: row.humanRights,
                communityHarm: row.communityHarm,
                biodiversityHarm: false
            });
            bytes32 evidenceHash = keccak256(abi.encodePacked(row.id, "v0.5.0"));

            rating.setRating(address(mock), 0, scores, stds, flags, expiresAt, evidenceHash);

            // Read back the computed rating
            ICarbonCreditRating.Rating memory r = rating.ratingOf(address(mock), 0);

            credits[i] = CreditInfo({
                id: row.id,
                creditName: row.name,
                symbol: row.symbol,
                token: address(mock),
                compositeBps: r.compositeBps,
                finalGrade: r.finalGrade
            });
        }

        console2.log("[Seed] Deployed and rated 16 MockCarbonCredit tokens");
        console2.log("");
    }

    // ══════════════════════════════════════════════════════════════════════
    //  PHASE 3: LOG CREDIT UNIVERSE
    // ══════════════════════════════════════════════════════════════════════
    function _logCreditUniverse() internal view {
        console2.log("================================================================");
        console2.log("  CREDIT UNIVERSE (16 tokenized-pilot credits)");
        console2.log("================================================================");
        console2.log("  ID    | Composite | Grade | Name");
        console2.log("  ------|-----------|-------|------------------------------");

        for (uint256 i = 0; i < N; i++) {
            CreditInfo memory c = credits[i];
            string memory grade = _gradeLabel(c.finalGrade);
            // Log each credit on its own line
            console2.log(
                string.concat(
                    "  ", c.id,
                    " |    ", _padBps(c.compositeBps),
                    " | ", _padGrade(grade),
                    " | ", c.creditName
                )
            );
        }
        console2.log("================================================================");
        console2.log("");
    }

    // ══════════════════════════════════════════════════════════════════════
    //  PHASE 4: RUN POOL (deploy, deposit, measure)
    // ══════════════════════════════════════════════════════════════════════
    function _runPool(
        string memory poolName,
        ICarbonCreditRating.Grade minGrade,
        bool isGated
    ) internal returns (PoolStats memory stats) {
        stats.poolName = poolName;

        // Deploy a fresh pool
        QualityGatedPool pool = new QualityGatedPool(
            poolName,
            ICarbonCreditRating(address(rating)),
            minGrade
        );

        console2.log(string.concat("--- Pool: ", poolName, " ---"));

        for (uint256 i = 0; i < N; i++) {
            CreditInfo memory c = credits[i];

            // Approve the pool to pull tokens
            MockCarbonCredit(c.token).approve(address(pool), DEPOSIT_AMOUNT);

            // Attempt deposit
            bool accepted;
            if (!isGated) {
                // Ungated: minGrade = B, everything passes (except if unrated, which won't happen)
                pool.deposit(c.token, 0, DEPOSIT_AMOUNT);
                accepted = true;
            } else {
                // Gated: try/catch to record success/failure
                try pool.deposit(c.token, 0, DEPOSIT_AMOUNT) {
                    accepted = true;
                } catch {
                    accepted = false;
                }
            }

            if (accepted) {
                stats.admitted += 1;
                stats.compositeSum += uint256(c.compositeBps);
                stats.gradeCounts[uint8(c.finalGrade)] += 1;
                console2.log(string.concat("    [PASS] ", c.id, " (", _gradeLabel(c.finalGrade), ", ", _padBps(c.compositeBps), " bps)"));
            } else {
                stats.rejected += 1;
                console2.log(string.concat("    [FAIL] ", c.id, " (", _gradeLabel(c.finalGrade), ", ", _padBps(c.compositeBps), " bps) -- rejected"));
            }
        }

        // Compute Lemons Index: fraction of admitted credits graded BB or below.
        // Following Akerlof's "market for lemons" framing: a lemon is a credit
        // that would not pass even the lowest investment-grade threshold (BBB).
        // LI = |{admitted credits with grade <= BB}| / |admitted|.
        stats.lemonsCount = stats.gradeCounts[0] + stats.gradeCounts[1]; // B + BB

        console2.log(string.concat("    Admitted: ", vm.toString(stats.admitted), "/16"));
        console2.log("");

        return stats;
    }

    // ══════════════════════════════════════════════════════════════════════
    //  PHASE 5: COMPARISON TABLE
    // ══════════════════════════════════════════════════════════════════════
    function _logComparisonTable(
        PoolStats memory ungated,
        PoolStats memory bbbGated,
        PoolStats memory aGated,
        PoolStats memory aaaGated
    ) internal pure {
        console2.log("================================================================");
        console2.log("  QUALITY GATING COMPARISON TABLE");
        console2.log("================================================================");
        console2.log("");

        // Header
        console2.log("  Metric                  | Ungated | BBB-Gate | A-Gate | AAA-Gate");
        console2.log("  ------------------------|---------|----------|--------|--------");

        // Row: Credits Admitted
        console2.log(string.concat(
            "  Credits admitted        |   ",
            _pad2(ungated.admitted), "/16 |    ",
            _pad2(bbbGated.admitted), "/16 |  ",
            _pad2(aGated.admitted), "/16 |   ",
            _pad2(aaaGated.admitted), "/16"
        ));

        // Row: Credits Rejected
        console2.log(string.concat(
            "  Credits rejected        |    ",
            _pad2(ungated.rejected), "   |     ",
            _pad2(bbbGated.rejected), "   |   ",
            _pad2(aGated.rejected), "   |    ",
            _pad2(aaaGated.rejected)
        ));

        // Row: Mean Composite (bps)
        string memory uMean  = ungated.admitted > 0  ? _padBps(uint16(ungated.compositeSum / ungated.admitted))   : "  n/a";
        string memory bMean  = bbbGated.admitted > 0 ? _padBps(uint16(bbbGated.compositeSum / bbbGated.admitted)) : "  n/a";
        string memory aMean  = aGated.admitted > 0   ? _padBps(uint16(aGated.compositeSum / aGated.admitted))     : "  n/a";
        string memory aaaMean = aaaGated.admitted > 0 ? _padBps(uint16(aaaGated.compositeSum / aaaGated.admitted)) : "  n/a";

        console2.log(string.concat(
            "  Mean composite (bps)    |   ", uMean,
            " |    ", bMean,
            " |  ", aMean,
            " |   ", aaaMean
        ));

        // Row: Lemons Index (fraction graded BB or below)
        string memory uLI  = ungated.admitted > 0  ? _frac(ungated.lemonsCount, ungated.admitted)   : " n/a";
        string memory bLI  = bbbGated.admitted > 0 ? _frac(bbbGated.lemonsCount, bbbGated.admitted) : " n/a";
        string memory aLI  = aGated.admitted > 0   ? _frac(aGated.lemonsCount, aGated.admitted)     : " n/a";
        string memory aaaLI = aaaGated.admitted > 0 ? _frac(aaaGated.lemonsCount, aaaGated.admitted) : " n/a";

        console2.log(string.concat(
            "  Lemons Index (<=BB)     |  ", uLI,
            " |   ", bLI,
            " | ", aLI,
            " |  ", aaaLI
        ));

        // Row: Grade distribution
        console2.log("");
        console2.log("  Grade distribution of admitted credits:");
        console2.log(string.concat(
            "    AAA                   |    ",
            _pad2(ungated.gradeCounts[5]), "   |     ",
            _pad2(bbbGated.gradeCounts[5]), "   |   ",
            _pad2(aGated.gradeCounts[5]), "   |    ",
            _pad2(aaaGated.gradeCounts[5])
        ));
        console2.log(string.concat(
            "    AA                    |    ",
            _pad2(ungated.gradeCounts[4]), "   |     ",
            _pad2(bbbGated.gradeCounts[4]), "   |   ",
            _pad2(aGated.gradeCounts[4]), "   |    ",
            _pad2(aaaGated.gradeCounts[4])
        ));
        console2.log(string.concat(
            "    A                     |    ",
            _pad2(ungated.gradeCounts[3]), "   |     ",
            _pad2(bbbGated.gradeCounts[3]), "   |   ",
            _pad2(aGated.gradeCounts[3]), "   |    ",
            _pad2(aaaGated.gradeCounts[3])
        ));
        console2.log(string.concat(
            "    BBB                   |    ",
            _pad2(ungated.gradeCounts[2]), "   |     ",
            _pad2(bbbGated.gradeCounts[2]), "   |   ",
            _pad2(aGated.gradeCounts[2]), "   |    ",
            _pad2(aaaGated.gradeCounts[2])
        ));
        console2.log(string.concat(
            "    BB                    |    ",
            _pad2(ungated.gradeCounts[1]), "   |     ",
            _pad2(bbbGated.gradeCounts[1]), "   |   ",
            _pad2(aGated.gradeCounts[1]), "   |    ",
            _pad2(aaaGated.gradeCounts[1])
        ));
        console2.log(string.concat(
            "    B                     |    ",
            _pad2(ungated.gradeCounts[0]), "   |     ",
            _pad2(bbbGated.gradeCounts[0]), "   |   ",
            _pad2(aGated.gradeCounts[0]), "   |    ",
            _pad2(aaaGated.gradeCounts[0])
        ));

        console2.log("");
        console2.log("================================================================");
        console2.log("  KEY TAKEAWAY");
        console2.log("================================================================");

        if (ungated.admitted > 0 && aGated.admitted > 0) {
            uint256 ungatedMean = ungated.compositeSum / ungated.admitted;
            uint256 aGatedMean  = aGated.compositeSum / aGated.admitted;
            uint256 improvement = 0;
            if (aGatedMean > ungatedMean) {
                improvement = ((aGatedMean - ungatedMean) * 10000) / ungatedMean;
            }
            console2.log(string.concat(
                "  A-gated pool mean composite is ",
                vm.toString(improvement / 100), ".",
                _pad2(improvement % 100),
                "% higher than ungated pool."
            ));
        }
        if (ungated.admitted > 0) {
            // Show LI numbers: fraction of pool that is BB-or-below ("lemons")
            uint256 uPct = (ungated.lemonsCount * 10000) / ungated.admitted;
            uint256 bPct = bbbGated.admitted > 0 ? (bbbGated.lemonsCount * 10000) / bbbGated.admitted : 0;
            console2.log(string.concat(
                "  Lemons Index (BB-or-below): ungated = ",
                vm.toString(uPct / 100), ".",
                _pad2(uPct % 100),
                "%, BBB-gated = ",
                vm.toString(bPct / 100), ".",
                _pad2(bPct % 100),
                "%, A-gated = 0.00%"
            ));
        }
        console2.log("  Quality gating eliminates sub-investment-grade credits from");
        console2.log("  the pool, raising the mean composite and driving the Lemons");
        console2.log("  Index (fraction of BB-or-below) to zero at the A-gate threshold.");
        console2.log("================================================================");
    }

    // ══════════════════════════════════════════════════════════════════════
    //  HELPERS
    // ══════════════════════════════════════════════════════════════════════

    function _readRow(string memory json, uint256 i) private pure returns (SeedRow memory row) {
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

    function _gradeLabel(ICarbonCreditRating.Grade g) internal pure returns (string memory) {
        if (g == ICarbonCreditRating.Grade.AAA) return "AAA";
        if (g == ICarbonCreditRating.Grade.AA)  return "AA";
        if (g == ICarbonCreditRating.Grade.A)   return "A";
        if (g == ICarbonCreditRating.Grade.BBB) return "BBB";
        if (g == ICarbonCreditRating.Grade.BB)  return "BB";
        return "B";
    }

    /// @dev Right-align a uint16 bps value to 5 chars (e.g., " 3110", " 9520")
    function _padBps(uint16 bps) internal pure returns (string memory) {
        string memory s = vm.toString(uint256(bps));
        bytes memory b = bytes(s);
        if (b.length == 1) return string.concat("    ", s);
        if (b.length == 2) return string.concat("   ", s);
        if (b.length == 3) return string.concat("  ", s);
        if (b.length == 4) return string.concat(" ", s);
        return s;
    }

    /// @dev Left-pad a grade label to 3 chars ("  B", " BB", "BBB", "  A", " AA", "AAA")
    function _padGrade(string memory g) internal pure returns (string memory) {
        bytes memory b = bytes(g);
        if (b.length == 1) return string.concat("  ", g);
        if (b.length == 2) return string.concat(" ", g);
        return g;
    }

    /// @dev Format a uint to 2-char string with leading zero ("01", "16", etc.)
    function _pad2(uint256 v) internal pure returns (string memory) {
        if (v < 10) return string.concat("0", vm.toString(v));
        return vm.toString(v);
    }

    /// @dev Format "n/d" as a fraction string
    function _frac(uint256 n, uint256 d) internal pure returns (string memory) {
        return string.concat(vm.toString(n), "/", vm.toString(d));
    }

    // ── Log header ───────────────────────────────────────────────────────
    function _logHeader() internal pure {
        console2.log("");
        console2.log("================================================================");
        console2.log("  ERC-CCQR QUALITY GATING DEMO");
        console2.log("  Carbon Credit Quality Rating v0.5 -- Testnet Simulation");
        console2.log("================================================================");
        console2.log("");
        console2.log("  This demo deploys the full rating + pool stack locally and");
        console2.log("  shows how quality gating filters the 16 tokenized-pilot credits");
        console2.log("  across four pool tiers: ungated, BBB, A, and AAA.");
        console2.log("");
    }
}
