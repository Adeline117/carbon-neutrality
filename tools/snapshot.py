#!/usr/bin/env python3
"""Snapshot the deployed CarbonCreditRating contract state into
docs/api/v0.4.1/ratings.json so the repo publishes a cacheable public read
API via GitHub Pages.

Reads:
  - RATING_ADDRESS env var (from .env or GitHub Action secret)
  - BASE_SEPOLIA_RPC_URL env var (defaults to the free public endpoint)
  - script/seed/tokenized_pilot.json for the credit ID ↔ symbol mapping
  - docs/v0.4.1-deployment-notes.md for the MCC-<id> → address mapping

Writes:
  - docs/api/v0.4.1/ratings.json     (array of all 14 rating tuples)
  - docs/api/v0.4.1/by-credit/<id>.json
  - docs/api/v0.4.1/index.json       (metadata)

Usage (locally):
  export RATING_ADDRESS=0x...
  python3 tools/snapshot.py

Usage (CI):
  See .github/workflows/snapshot.yml
"""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "script" / "seed" / "tokenized_pilot.json"
DEPLOYMENT_NOTES = ROOT / "docs" / "v0.4.1-deployment-notes.md"
API_DIR = ROOT / "docs" / "api" / "v0.4.1"
BY_CREDIT_DIR = API_DIR / "by-credit"

GRADES = ["B", "BB", "BBB", "A", "AA", "AAA"]
DIM_ORDER = [
    "removalType",
    "additionality",
    "permanence",
    "mrvGrade",
    "vintageYear",
    "coBenefits",
    "registryMethodology",
]
DQ_ORDER = [
    "doubleCounting",
    "failedVerification",
    "sanctionedRegistry",
    "noThirdParty",
    "humanRights",
    "communityHarm",
]


def cast_call(rpc_url: str, contract: str, sig: str, *args: str) -> str:
    """Run `cast call` and return stdout."""
    cmd = ["cast", "call", contract, sig, *args, "--rpc-url", rpc_url]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"cast call failed: {res.stderr}")
    return res.stdout.strip()


def parse_rating_tuple(hex_out: str) -> dict:
    """Decode the Rating struct returned by ratingOf(address,uint256).

    Rating layout (abi order):
      DimensionScores scores        -- 7 × uint8
      Disqualifiers flags            -- 6 × bool
      uint16 compositeBps
      Grade nominalGrade            -- uint8
      Grade finalGrade              -- uint8
      uint64 lastUpdatedAt
      uint64 expiresAt
      uint16 methodologyVersion
      bytes32 evidenceHash
      address attestedBy
    """
    # `cast call` returns an ABI-encoded tuple. Use `cast abi-decode` to parse.
    sig = (
        "rating((uint8,uint8,uint8,uint8,uint8,uint8,uint8),"
        "(bool,bool,bool,bool,bool,bool),uint16,uint8,uint8,uint64,uint64,uint16,bytes32,address)"
    )
    res = subprocess.run(
        ["cast", "abi-decode", sig, hex_out],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        raise RuntimeError(f"abi-decode failed: {res.stderr}")
    lines = [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]

    # Groups: 1 tuple line for scores, 1 for flags, then individual scalars
    # Simpler: read one value per line after removing parens/commas
    scalars = []
    for line in lines:
        cleaned = line.strip("(),")
        if cleaned:
            scalars.append(cleaned)

    if len(scalars) < 7 + 6 + 8:
        raise RuntimeError(f"unexpected abi-decode output: {lines!r}")

    i = 0
    scores = {DIM_ORDER[k]: int(scalars[i + k]) for k in range(7)}
    i += 7
    flags = {DQ_ORDER[k]: scalars[i + k] == "true" for k in range(6)}
    i += 6
    composite_bps = int(scalars[i]); i += 1
    nominal_grade = GRADES[int(scalars[i])]; i += 1
    final_grade = GRADES[int(scalars[i])]; i += 1
    last_updated = int(scalars[i]); i += 1
    expires_at = int(scalars[i]); i += 1
    methodology_version = int(scalars[i]); i += 1
    evidence_hash = scalars[i]; i += 1
    attested_by = scalars[i]; i += 1

    return {
        "scores": scores,
        "disqualifiers": [k for k, v in flags.items() if v],
        "compositeBps": composite_bps,
        "composite": composite_bps / 100,
        "nominalGrade": nominal_grade,
        "finalGrade": final_grade,
        "lastUpdatedAt": last_updated,
        "expiresAt": expires_at,
        "methodologyVersion": f"0x{methodology_version:04x}",
        "evidenceHash": evidence_hash,
        "attestedBy": attested_by,
    }


def load_credit_addresses() -> dict[str, str]:
    """Parse docs/v0.4.1-deployment-notes.md for the MCC-<id> -> address table.

    The expected line format is:
        | MCC-T001 | Toucan BCT ... | 0x... |
    """
    if not DEPLOYMENT_NOTES.exists():
        return {}
    out: dict[str, str] = {}
    for line in DEPLOYMENT_NOTES.read_text().splitlines():
        if "| MCC-" in line and "0x" in line:
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if len(parts) >= 3 and parts[0].startswith("MCC-"):
                credit_id = parts[0].removeprefix("MCC-")
                addr = parts[-1]
                if addr.startswith("0x") and len(addr) == 42:
                    out[credit_id] = addr
    return out


def main() -> None:
    rating_address = os.environ.get("RATING_ADDRESS", "").strip()
    rpc_url = os.environ.get("BASE_SEPOLIA_RPC_URL", "https://sepolia.base.org")

    if not rating_address or not rating_address.startswith("0x"):
        print(
            "RATING_ADDRESS not set. Deploy the contract first with "
            "`forge script script/Deploy.s.sol --broadcast`.",
            file=sys.stderr,
        )
        sys.exit(1)

    credit_addresses = load_credit_addresses()
    if not credit_addresses:
        print(
            "No credit addresses found in docs/v0.4.1-deployment-notes.md. "
            "Fill in the MCC-<id> -> 0x... table after running SeedRatings.s.sol.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load seed metadata (id -> name, symbol)
    seed_rows = json.loads(SEED.read_text())
    seed_by_id = {row["id"]: row for row in seed_rows}

    ratings_out = []
    BY_CREDIT_DIR.mkdir(parents=True, exist_ok=True)

    for credit_id, addr in sorted(credit_addresses.items()):
        meta = seed_by_id.get(credit_id, {})
        try:
            hex_out = cast_call(
                rpc_url,
                rating_address,
                "ratingOf(address,uint256)",
                addr,
                "0",
            )
            parsed = parse_rating_tuple(hex_out)
        except Exception as e:
            print(f"Failed to read {credit_id} @ {addr}: {e}", file=sys.stderr)
            continue

        entry = {
            "id": credit_id,
            "name": meta.get("name", ""),
            "symbol": meta.get("symbol", f"MCC-{credit_id}"),
            "creditTokenAddress": addr,
            "tokenId": 0,
            **parsed,
            "disclaimer": (
                "PRELIMINARY AUTHOR ATTESTATION on Base Sepolia testnet. "
                "Not endorsed by any registry, rating agency, or real-world "
                "carbon market participant."
            ),
        }
        ratings_out.append(entry)
        (BY_CREDIT_DIR / f"{credit_id}.json").write_text(json.dumps(entry, indent=2))

    (API_DIR / "ratings.json").write_text(json.dumps(ratings_out, indent=2))

    index = {
        "framework_version": "0.4.1",
        "schema_version": "0.2.1",
        "chain": "base-sepolia",
        "chain_id": 84532,
        "rating_contract": rating_address,
        "rpc_url_public": "https://sepolia.base.org",
        "snapshot_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "credit_count": len(ratings_out),
        "disclaimer": (
            "PRELIMINARY AUTHOR ATTESTATIONS ONLY. NOT ENDORSED BY VERRA, GOLD "
            "STANDARD, PURO, ISOMETRIC, ICVCM, BEZERO, SYLVERA, CALYX GLOBAL, "
            "OR MSCI. Base Sepolia testnet only. Any value derived from these "
            "ratings is play money."
        ),
        "source_of_truth": "https://github.com/Adeline117/carbon-neutrality",
    }
    (API_DIR / "index.json").write_text(json.dumps(index, indent=2))

    print(f"Snapshotted {len(ratings_out)} credits → {API_DIR / 'ratings.json'}")


if __name__ == "__main__":
    main()
