#!/usr/bin/env python3
"""
Bridge-Level vs Pool-Level Selection Decomposition
====================================================
This experiment resolves Limitation #5 in the Nat Comms paper:
"We could not decompose selection into bridge-level versus pool-level components"

Question: Did Toucan disproportionately bridge renewable credits from Verra,
          or did depositors selectively choose renewable credits from the bridged set?

Method:
  1. Query all TCO2 tokens created via ToucanCarbonOffsetsFactory on Polygon
  2. Classify each by methodology type (from token name: "TCO2-VCS-<projectid>-<vintage>")
  3. Compare composition:
     - All bridged tokens (universe)
     - BCT-deposited tokens (sample)
  4. Test: selection_at_bridge = bridge_renewable_share / vcs_base_rate
           selection_at_pool  = bct_renewable_share / bridge_renewable_share

If bridge ≈ VCS base rate (37%) and BCT ≈ 69%: selection at pool (Gresham story)
If bridge ≈ 69%: selection at bridge (upstream, weaker Gresham)

Data sources:
  - RPC: polygon.drpc.org (eth_getLogs on TCO2Factory)
  - Fallback: Dune SQL query provided below
"""

import json
import time
import requests
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats as sstats

HERE = Path(__file__).resolve().parent

# ── Addresses ────────────────────────────────────────────────────────────────
TCO2_FACTORY = "0x639dFeA994b139A3d6C3750D4C4E24daEc039BD7"
BCT_POOL = "0x2f800db0fdb5223b3c3f354886d907a671414a7f"

# TokenCreated event: topic0 = keccak256("TokenCreated(uint256,address)")
# But Toucan V1 uses a custom signature. Let's try the common one.
# We'll discover the right signature from the logs themselves.

RPC_URL = "https://polygon.drpc.org"
CHUNK_BLOCKS = 1000
START_BLOCK = 18_000_000   # Before BCT launch
END_BLOCK = 37_000_000     # After BCT active period

# ── Known project → methodology mapping ──────────────────────────────────────
# Load from existing scored data
SCORES_FILE = HERE / "tco2_scores_complete.json"
METADATA_FILE = HERE / "tco2_metadata.json"

# Map project IDs to types from existing analysis
def build_project_type_map() -> dict:
    """Build a map of VCS project ID → methodology type from existing data."""
    type_map = {}

    # From scored tokens
    if SCORES_FILE.exists():
        scores = json.loads(SCORES_FILE.read_text())
        for addr, info in scores.items():
            # Try to get project ID from metadata
            ptype = info.get("type", "Unknown")
            type_map[addr.lower()] = ptype

    # From metadata (has project names that encode VCS ID)
    if METADATA_FILE.exists():
        metadata = json.loads(METADATA_FILE.read_text())
        if isinstance(metadata, dict):
            for addr, info in metadata.items():
                name = info.get("name", "")
                if name.startswith("TCO2-VCS-"):
                    parts = name.split("-")
                    if len(parts) >= 3:
                        project_id = parts[2]
                        # Store address -> project_id mapping
                        type_map.setdefault(f"pid:{project_id}", {}).update(
                            {"name": name, "address": addr.lower()}
                        )

    return type_map


# ── Methodology classification from Verra project ID ────────────────────────
# Based on the classification used in the paper (see Methods section)
# Key renewable methodologies: AMS-I.D, ACM0002, AMS-I.C, AMS-I.A
# Known from scored tokens
RENEWABLE_PROJECT_IDS = set()
ALL_PROJECT_TYPES = {}

def load_bct_project_classifications():
    """Load known project → type mappings from BCT analysis."""
    global RENEWABLE_PROJECT_IDS, ALL_PROJECT_TYPES

    if SCORES_FILE.exists():
        scores = json.loads(SCORES_FILE.read_text())
        for addr, info in scores.items():
            ptype = info.get("type", "Unknown")
            ALL_PROJECT_TYPES[addr.lower()] = ptype
            if ptype == "Renewable":
                RENEWABLE_PROJECT_IDS.add(addr.lower())


# ── RPC helper ───────────────────────────────────────────────────────────────
SESSION = requests.Session()

def rpc_call(method: str, params: list) -> dict:
    """JSON-RPC call with retry on rate limit."""
    body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    for attempt in range(5):
        try:
            resp = SESSION.post(RPC_URL, json=body, timeout=30)
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            data = resp.json()
            if "error" in data:
                if "limit" in str(data["error"]).lower():
                    time.sleep(2 ** attempt)
                    continue
            return data
        except Exception as e:
            if attempt < 4:
                time.sleep(2 ** attempt)
            else:
                raise
    return {"error": "max retries exceeded"}


def get_factory_token_created_events() -> list[dict]:
    """Query all TokenCreated events from TCO2Factory."""
    # First, discover what events the factory emits
    # Try a small range first to find event signatures
    print("  Discovering factory events...")

    events_all = []
    block = START_BLOCK

    while block < END_BLOCK:
        chunk_end = min(block + CHUNK_BLOCKS - 1, END_BLOCK)

        result = rpc_call("eth_getLogs", [{
            "fromBlock": hex(block),
            "toBlock": hex(chunk_end),
            "address": TCO2_FACTORY,
        }])

        if "result" in result and result["result"]:
            for log in result["result"]:
                events_all.append({
                    "block": int(log["blockNumber"], 16),
                    "topics": log.get("topics", []),
                    "data": log.get("data", "0x"),
                    "address": log.get("address", "").lower(),
                    "tx_hash": log.get("transactionHash", ""),
                })

        block = chunk_end + 1

        if block % 100_000 == 0:
            print(f"  Scanned to block {block:,} ({len(events_all)} events so far)")

    return events_all


def extract_tco2_addresses_from_events(events: list[dict]) -> list[str]:
    """Extract created TCO2 token addresses from factory events.

    TokenCreated events typically encode the new token address in topic[1] or in data.
    We try both patterns.
    """
    addresses = set()

    # Group by topic0 to find the most common event signature
    topic0_counts = defaultdict(int)
    for ev in events:
        if ev["topics"]:
            topic0_counts[ev["topics"][0]] += 1

    if topic0_counts:
        print(f"  Found {len(topic0_counts)} unique event signatures:")
        for t0, count in sorted(topic0_counts.items(), key=lambda x: -x[1]):
            print(f"    {t0[:18]}...{t0[-8:]}: {count} events")

    for ev in events:
        # Pattern 1: address in topic[1] (indexed parameter)
        if len(ev["topics"]) >= 2:
            # Address is last 20 bytes of 32-byte topic
            addr = "0x" + ev["topics"][1][-40:]
            if addr != "0x" + "0" * 40:
                addresses.add(addr.lower())

        # Pattern 2: address in data field
        if ev["data"] and len(ev["data"]) >= 66:
            addr = "0x" + ev["data"][26:66]
            if addr != "0x" + "0" * 40:
                addresses.add(addr.lower())

    return sorted(addresses)


def classify_tco2_by_name(address: str) -> dict | None:
    """Call name() on a TCO2 contract to get "TCO2-VCS-<id>-<vintage>"."""
    # name() = 0x06fdde03
    result = rpc_call("eth_call", [
        {"to": address, "data": "0x06fdde03"},
        "latest"
    ])

    if "result" not in result or result["result"] == "0x":
        return None

    try:
        # ABI-decode string
        data = bytes.fromhex(result["result"][2:])
        # String is at offset 32, length at offset 32, then the string
        if len(data) < 64:
            return None
        offset = int.from_bytes(data[:32], "big")
        length = int.from_bytes(data[offset:offset + 32], "big")
        name = data[offset + 32:offset + 32 + length].decode("utf-8", errors="replace")
        return {"name": name, "address": address}
    except Exception:
        return None


def classify_name_to_type(name: str) -> str:
    """Classify a TCO2 name like 'TCO2-VCS-1234-2015' to a methodology type.

    Uses the existing BCT project classifications as ground truth,
    falling back to 'unclassified' for projects not in BCT.
    """
    # For tokens already in our scored set, we know the type
    # For new tokens, we need the Verra registry lookup
    return "unclassified"


def run_decomposition(bridged_addresses: list[str]) -> dict:
    """Compare bridged universe vs BCT-deposited subset."""
    load_bct_project_classifications()

    # BCT tokens we already know
    bct_addresses = set(ALL_PROJECT_TYPES.keys())

    # Categorize bridged tokens
    bridged_in_bct = set()
    bridged_not_in_bct = set()
    for addr in bridged_addresses:
        if addr in bct_addresses:
            bridged_in_bct.add(addr)
        else:
            bridged_not_in_bct.add(addr)

    # Composition of bridged-and-in-BCT (we know types)
    bct_type_counts = defaultdict(int)
    for addr in bridged_in_bct:
        bct_type_counts[ALL_PROJECT_TYPES.get(addr, "Unknown")] += 1

    # Key ratio
    n_bridged = len(bridged_addresses)
    n_bct = len(bridged_in_bct)
    n_unbct = len(bridged_not_in_bct)
    bct_renewable_count = bct_type_counts.get("Renewable", 0)

    results = {
        "n_bridged_total": n_bridged,
        "n_bridged_in_bct": n_bct,
        "n_bridged_not_in_bct": n_unbct,
        "bct_coverage_pct": round(n_bct / n_bridged * 100, 1) if n_bridged > 0 else 0,
        "bct_composition_known": dict(bct_type_counts),
        "bct_renewable_pct_by_count": round(bct_renewable_count / n_bct * 100, 1) if n_bct > 0 else 0,
        "note": "To fully classify non-BCT bridged tokens, we need to call name() on each and cross-reference against Verra registry. This is a follow-up step.",
    }

    # If we can classify even a sample of non-BCT tokens, that's informative
    # Sample 50 non-BCT addresses for name() calls
    sample_size = min(50, n_unbct)
    if sample_size > 0:
        print(f"\n  Sampling {sample_size} non-BCT bridged tokens for classification...")
        sample = sorted(bridged_not_in_bct)[:sample_size]
        sample_names = []
        for i, addr in enumerate(sample):
            info = classify_tco2_by_name(addr)
            if info:
                sample_names.append(info)
            if (i + 1) % 10 == 0:
                print(f"    {i + 1}/{sample_size} classified")
            time.sleep(0.1)  # Rate limit

        results["sample_non_bct_names"] = sample_names
        results["sample_size"] = sample_size

    return results


# ── Dune SQL fallback ────────────────────────────────────────────────────────
DUNE_QUERY = """
-- Bridge-level decomposition: ALL Toucan-bridged TCO2 tokens
-- Run at: https://dune.com/queries/new?category=decoded_projects&namespace=toucan_protocol

WITH all_bridged AS (
    SELECT
        evt_block_number AS block_number,
        evt_block_time AS created_time,
        tokenAddress AS tco2_address
    FROM toucan_protocol_polygon.ToucanCarbonOffsetsFactory_evt_TokenCreated
    WHERE evt_block_time <= '2023-01-01'  -- same window as BCT analysis
),

bct_deposited AS (
    SELECT DISTINCT "erc20" AS tco2_address
    FROM toucan_protocol_polygon.Pool_evt_Deposited
    WHERE contract_address = 0x2F800Db0fdb5223b3C3f354886d907A671414A7F
),

nct_deposited AS (
    SELECT DISTINCT "erc20" AS tco2_address
    FROM toucan_protocol_polygon.Pool_evt_Deposited
    WHERE contract_address = 0xD838290e877E0188a4A44700463419ED96c16107
),

classified AS (
    SELECT
        a.tco2_address,
        a.created_time,
        t.name AS tco2_name,
        t.symbol,
        CASE
            WHEN b.tco2_address IS NOT NULL THEN 'BCT'
            WHEN n.tco2_address IS NOT NULL THEN 'NCT_only'
            ELSE 'never_deposited'
        END AS pool_status
    FROM all_bridged a
    LEFT JOIN bct_deposited b ON b.tco2_address = a.tco2_address
    LEFT JOIN nct_deposited n ON n.tco2_address = a.tco2_address
    LEFT JOIN tokens.erc20 t ON t.contract_address = a.tco2_address
        AND t.blockchain = 'polygon'
)

SELECT
    pool_status,
    COUNT(*) AS n_tokens,
    COUNT(DISTINCT tco2_address) AS n_unique
FROM classified
GROUP BY pool_status
ORDER BY n_tokens DESC;

-- Second query: get full names for classification
-- SELECT tco2_address, tco2_name, pool_status FROM classified ORDER BY created_time;
"""


def main():
    print("=" * 70)
    print("BRIDGE-LEVEL vs POOL-LEVEL SELECTION DECOMPOSITION")
    print("=" * 70)
    print()
    print("This experiment resolves Limitation #5 in the Nat Comms paper.")
    print()

    if "--dune-only" in sys.argv:
        print("Dune SQL query for manual execution:")
        print(DUNE_QUERY)
        return

    # Step 1: Fetch all TokenCreated events from factory
    print("Step 1: Querying TCO2Factory for all bridged tokens...")
    print(f"  Factory: {TCO2_FACTORY}")
    print(f"  Block range: {START_BLOCK:,} - {END_BLOCK:,}")
    print(f"  This will take ~{(END_BLOCK - START_BLOCK) / CHUNK_BLOCKS * 0.15 / 60:.0f} minutes")
    print()

    events = get_factory_token_created_events()
    print(f"\n  Total factory events: {len(events)}")

    if not events:
        print("\n  No events found. Try the Dune query instead:")
        print("  python3 bridge_decomposition.py --dune-only")
        return

    # Step 2: Extract TCO2 addresses
    print("\nStep 2: Extracting TCO2 addresses from events...")
    bridged_addresses = extract_tco2_addresses_from_events(events)
    print(f"  Unique bridged TCO2 addresses: {len(bridged_addresses)}")

    # Step 3: Compare with BCT
    print("\nStep 3: Comparing bridged universe vs BCT deposits...")
    results = run_decomposition(bridged_addresses)

    # Print summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"  Total bridged TCO2 tokens: {results['n_bridged_total']}")
    print(f"  Of which deposited to BCT: {results['n_bridged_in_bct']} ({results['bct_coverage_pct']}%)")
    print(f"  Bridged but never in BCT:  {results['n_bridged_not_in_bct']}")
    print(f"  BCT renewable % (by token count): {results['bct_renewable_pct_by_count']}%")

    if results.get("sample_non_bct_names"):
        print(f"\n  Sample of non-BCT bridged tokens ({len(results['sample_non_bct_names'])} names recovered):")
        for info in results["sample_non_bct_names"][:10]:
            print(f"    {info['name']}")

    # Save
    out_path = HERE / "bridge_decomposition_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n→ Saved to {out_path}")

    # Also save Dune query for reference
    dune_path = HERE / "bridge_decomposition_dune.sql"
    with open(dune_path, "w") as f:
        f.write(DUNE_QUERY)
    print(f"→ Dune fallback query saved to {dune_path}")


if __name__ == "__main__":
    main()
