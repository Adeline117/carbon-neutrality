#!/usr/bin/env python3
"""Fetch BCT pool deposit events and depositor TCO2 holdings from Polygon.

This script collects the on-chain data required for the depositor-level
adverse selection analysis. It queries the Toucan BCT pool contract for
all Deposited events, identifies unique depositors, and reconstructs each
depositor's TCO2 portfolio at the time of their deposits.

Requirements:
    pip install web3 requests

Usage:
    # Full data collection (requires Polygon RPC endpoint)
    python3 fetch_deposits.py

    # With custom RPC endpoint
    python3 fetch_deposits.py --rpc https://polygon-rpc.com

    # Limit to specific block range (useful for testing)
    python3 fetch_deposits.py --from-block 20000000 --to-block 40000000

    # Use PolygonScan API instead of RPC (slower but more reliable)
    python3 fetch_deposits.py --polygonscan-api YOUR_API_KEY

Output:
    bct_deposits.json         -- all BCT deposit events
    depositor_portfolios.json -- per-depositor TCO2 holdings at deposit time
    tco2_metadata.json        -- TCO2 token -> project/vintage mapping
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent

# ── Contract addresses on Polygon ──────────────────────────────────────────

BCT_POOL = "0x2F800Db0fdb5223b3C3f354886d907A671414A7F"
NCT_POOL = "0xD838290e877E0188a4A44700463419ED96c16107"
TCO2_FACTORY = "0x639dFeA994b139A3d6C3750D4C4E24daEc039BD7"
CARBON_OFFSET_BATCHES = "0x8a4D7458dDe3023A3b24225D62087701a88B09Dd"

# BCT deployed around block 20_000_000 (Oct 2021)
BCT_DEPLOY_BLOCK = 20_000_000
# End of 2022 (peak adverse selection period)
END_OF_2022_BLOCK = 37_000_000

# ── ABI fragments (minimal, only what we need) ────────────────────────────

# Pool deposit event: Deposited(address indexed sender, address indexed erc20, uint256 amount)
DEPOSITED_EVENT_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "name": "sender", "type": "address"},
        {"indexed": True, "name": "erc20", "type": "address"},
        {"indexed": False, "name": "amount", "type": "uint256"},
    ],
    "name": "Deposited",
    "type": "event",
}

# ERC-20 Transfer event: Transfer(address indexed from, address indexed to, uint256 value)
TRANSFER_EVENT_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "name": "from", "type": "address"},
        {"indexed": True, "name": "to", "type": "address"},
        {"indexed": False, "name": "value", "type": "uint256"},
    ],
    "name": "Transfer",
    "type": "event",
}

# Minimal ERC-20 ABI for name() and symbol() calls
ERC20_NAME_ABI = [
    {
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# Pool ABI fragment for getScoredTCO2s (lists all TCO2s in the pool)
POOL_ABI = [
    {
        "inputs": [],
        "name": "getScoredTCO2s",
        "outputs": [{"name": "", "type": "address[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]


def compute_event_signature(event_name: str, param_types: list[str]) -> str:
    """Compute the keccak256 topic0 for an event signature."""
    try:
        from web3 import Web3

        sig = f"{event_name}({','.join(param_types)})"
        return Web3.keccak(text=sig).hex()
    except ImportError:
        # Fallback: precomputed values
        sigs = {
            "Deposited(address,address,uint256)":
                "0x0f7d13863f0093bda08ef1823a3b8eee7a4821cc40e578a817a079b9eb0e571f",
            "Transfer(address,address,uint256)":
                "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
        }
        sig = f"{event_name}({','.join(param_types)})"
        return sigs.get(sig, "")


# ── Data fetching via web3.py ──────────────────────────────────────────────

def connect_rpc(rpc_url: str):
    """Connect to Polygon RPC."""
    from web3 import Web3

    if rpc_url.startswith("ws"):
        w3 = Web3(Web3.WebsocketProvider(rpc_url))
    else:
        w3 = Web3(Web3.HTTPProvider(rpc_url))

    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to RPC at {rpc_url}")

    chain_id = w3.eth.chain_id
    if chain_id != 137:
        print(f"WARNING: Connected to chain {chain_id}, expected 137 (Polygon)")

    print(f"Connected to Polygon RPC. Latest block: {w3.eth.block_number}")
    return w3


def fetch_bct_deposits(
    w3,
    from_block: int = BCT_DEPLOY_BLOCK,
    to_block: int = END_OF_2022_BLOCK,
    batch_size: int = 10_000,
) -> list[dict]:
    """Fetch all BCT Deposited events in the given block range.

    Returns a list of dicts:
        {sender, tco2_address, amount_wei, amount_tonnes, block_number, tx_hash, log_index}
    """
    from web3 import Web3

    pool_address = Web3.to_checksum_address(BCT_POOL)
    deposited_topic = compute_event_signature("Deposited", ["address", "address", "uint256"])

    deposits = []
    current = from_block

    print(f"Fetching BCT deposits from block {from_block} to {to_block}...")

    while current <= to_block:
        end = min(current + batch_size - 1, to_block)
        try:
            logs = w3.eth.get_logs({
                "address": pool_address,
                "topics": [deposited_topic],
                "fromBlock": current,
                "toBlock": end,
            })
        except Exception as e:
            # If batch too large, halve it
            if "too many" in str(e).lower() or "limit" in str(e).lower():
                batch_size = max(1000, batch_size // 2)
                print(f"  Reducing batch size to {batch_size}")
                continue
            raise

        for log in logs:
            sender = "0x" + log["topics"][1].hex()[-40:]
            tco2_address = "0x" + log["topics"][2].hex()[-40:]
            amount_wei = int(log["data"].hex(), 16) if isinstance(log["data"], bytes) else int(log["data"], 16)
            amount_tonnes = amount_wei / 1e18

            deposits.append({
                "sender": Web3.to_checksum_address(sender),
                "tco2_address": Web3.to_checksum_address(tco2_address),
                "amount_wei": str(amount_wei),
                "amount_tonnes": amount_tonnes,
                "block_number": log["blockNumber"],
                "tx_hash": log["transactionHash"].hex(),
                "log_index": log["logIndex"],
            })

        n = len(deposits)
        progress = (end - from_block) / (to_block - from_block) * 100
        if n > 0 and (end - from_block) % (batch_size * 10) < batch_size:
            print(f"  Block {end}: {n} deposits found ({progress:.0f}%)")

        current = end + 1
        time.sleep(0.1)  # Rate limiting

    print(f"Total BCT deposits found: {len(deposits)}")
    return deposits


def fetch_tco2_metadata(w3, tco2_addresses: list[str]) -> dict[str, dict]:
    """Fetch name and symbol for each TCO2 token to extract project ID and vintage.

    TCO2 token names follow the pattern:
        "Toucan Protocol: TCO2-VCS-<projectId>-<vintage>"
    e.g. "Toucan Protocol: TCO2-VCS-934-2016"
    """
    from web3 import Web3

    metadata = {}
    for i, addr in enumerate(tco2_addresses):
        try:
            contract = w3.eth.contract(
                address=Web3.to_checksum_address(addr),
                abi=ERC20_NAME_ABI,
            )
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()

            # Parse project info from name
            project_info = parse_tco2_name(name, symbol)
            metadata[addr] = {
                "name": name,
                "symbol": symbol,
                **project_info,
            }
        except Exception as e:
            metadata[addr] = {
                "name": "UNKNOWN",
                "symbol": "UNKNOWN",
                "error": str(e),
            }

        if (i + 1) % 50 == 0:
            print(f"  TCO2 metadata: {i+1}/{len(tco2_addresses)}")
        time.sleep(0.05)

    print(f"Fetched metadata for {len(metadata)} TCO2 tokens")
    return metadata


def parse_tco2_name(name: str, symbol: str) -> dict:
    """Parse TCO2 token name to extract registry, project ID, and vintage.

    Examples:
        "Toucan Protocol: TCO2-VCS-934-2016" -> {registry: VCS, project_id: 934, vintage: 2016}
        "TCO2-VCS-1477-2019" -> {registry: VCS, project_id: 1477, vintage: 2019}
    """
    import re

    # Try parsing from symbol first (more standardized)
    # Symbol pattern: TCO2-VCS-<id>-<vintage>
    for text in [symbol, name]:
        match = re.search(r"TCO2-(\w+)-(\d+)-(\d{4})", text)
        if match:
            return {
                "registry": match.group(1),
                "project_id": int(match.group(2)),
                "vintage_year": int(match.group(3)),
            }

    # Fallback: try to find any 4-digit year and project number
    years = re.findall(r"(20\d{2})", name)
    ids = re.findall(r"(\d{3,})", name)

    return {
        "registry": "VCS",
        "project_id": int(ids[0]) if ids else 0,
        "vintage_year": int(years[-1]) if years else 0,
    }


def reconstruct_depositor_portfolios(
    w3,
    deposits: list[dict],
    tco2_addresses: list[str],
    batch_size: int = 5_000,
) -> dict[str, dict]:
    """For each depositor, reconstruct their TCO2 holdings at deposit time.

    This is the most expensive step. For each depositor, we need to know what
    OTHER TCO2 tokens they held when they deposited into BCT.

    Strategy: For each unique depositor, query Transfer events across all known
    TCO2 tokens and reconstruct balances at the deposit block.
    """
    from web3 import Web3

    # Group deposits by sender
    depositor_deposits: dict[str, list[dict]] = {}
    for d in deposits:
        depositor_deposits.setdefault(d["sender"], []).append(d)

    transfer_topic = compute_event_signature("Transfer", ["address", "address", "uint256"])
    portfolios = {}

    print(f"Reconstructing portfolios for {len(depositor_deposits)} depositors...")

    for idx, (depositor, deps) in enumerate(depositor_deposits.items()):
        # Find the block range: from first deposit - buffer to last deposit
        blocks = [d["block_number"] for d in deps]
        earliest_block = min(blocks) - 100_000  # ~2 days before first deposit
        latest_block = max(blocks)

        # Deposited TCO2s (what they put into BCT)
        deposited_tco2s: dict[str, float] = {}
        for d in deps:
            addr = d["tco2_address"]
            deposited_tco2s[addr] = deposited_tco2s.get(addr, 0) + d["amount_tonnes"]

        # Query balances of all known TCO2 tokens at the latest deposit block
        # This tells us what they RETAINED
        retained_tco2s: dict[str, float] = {}

        for tco2_addr in tco2_addresses:
            try:
                contract = w3.eth.contract(
                    address=Web3.to_checksum_address(tco2_addr),
                    abi=ERC20_NAME_ABI,
                )
                # Query balance at the block of the last deposit
                balance = contract.functions.balanceOf(
                    Web3.to_checksum_address(depositor)
                ).call(block_identifier=latest_block)

                if balance > 0:
                    retained_tco2s[tco2_addr] = balance / 1e18
            except Exception:
                continue  # Skip tokens we can't query

            time.sleep(0.02)

        portfolios[depositor] = {
            "depositor": depositor,
            "n_deposits": len(deps),
            "deposit_blocks": blocks,
            "deposited_tco2s": deposited_tco2s,
            "retained_tco2s": retained_tco2s,
            "n_deposited_types": len(deposited_tco2s),
            "n_retained_types": len(retained_tco2s),
        }

        if (idx + 1) % 50 == 0:
            print(f"  Portfolios: {idx+1}/{len(depositor_deposits)}")

    print(f"Reconstructed {len(portfolios)} depositor portfolios")
    return portfolios


# ── Alternative: PolygonScan API approach ──────────────────────────────────

def fetch_deposits_polygonscan(api_key: str) -> list[dict]:
    """Fetch BCT deposits via PolygonScan API (fallback if RPC unavailable).

    PolygonScan's getLogs API supports filtering by topic and address.
    Rate limit: 5 calls/sec on free tier, 10k results per call.
    """
    import requests

    base_url = "https://api.polygonscan.com/api"
    deposited_topic = compute_event_signature("Deposited", ["address", "address", "uint256"])

    deposits = []
    page = 1
    offset = 1000  # results per page

    print("Fetching BCT deposits via PolygonScan API...")

    while True:
        params = {
            "module": "logs",
            "action": "getLogs",
            "address": BCT_POOL,
            "topic0": deposited_topic,
            "fromBlock": BCT_DEPLOY_BLOCK,
            "toBlock": END_OF_2022_BLOCK,
            "page": page,
            "offset": offset,
            "apikey": api_key,
        }

        resp = requests.get(base_url, params=params, timeout=30)
        data = resp.json()

        if data["status"] != "1" or not data["result"]:
            break

        for log in data["result"]:
            sender = "0x" + log["topics"][1][-40:]
            tco2_address = "0x" + log["topics"][2][-40:]
            amount_wei = int(log["data"], 16)

            deposits.append({
                "sender": sender,
                "tco2_address": tco2_address,
                "amount_wei": str(amount_wei),
                "amount_tonnes": amount_wei / 1e18,
                "block_number": int(log["blockNumber"], 16),
                "tx_hash": log["transactionHash"],
                "log_index": int(log["logIndex"], 16),
            })

        if len(data["result"]) < offset:
            break

        page += 1
        time.sleep(0.25)  # Rate limit

    print(f"Total BCT deposits via PolygonScan: {len(deposits)}")
    return deposits


# ── Alternative: Dune Analytics SQL approach ───────────────────────────────

DUNE_QUERY_BCT_DEPOSITS = """
-- Dune Analytics query: BCT pool deposit events on Polygon
-- Run at: https://dune.com/queries/new?category=decoded_projects&namespace=toucan_protocol
--
-- This query extracts all BCT deposit events and maps depositors to their
-- deposited TCO2 types, enabling the adverse selection analysis.

WITH bct_deposits AS (
    SELECT
        evt_block_number AS block_number,
        evt_block_time AS block_time,
        evt_tx_hash AS tx_hash,
        "sender" AS depositor,
        "erc20" AS tco2_address,
        "amount" / 1e18 AS amount_tonnes
    FROM toucan_protocol_polygon.Pool_evt_Deposited
    WHERE contract_address = 0x2F800Db0fdb5223b3C3f354886d907A671414A7F  -- BCT
      AND evt_block_time >= '2021-10-01'
      AND evt_block_time <= '2022-12-31'
),

-- Get TCO2 token metadata (project ID and vintage from token name)
tco2_info AS (
    SELECT DISTINCT
        d.tco2_address,
        t.name AS tco2_name,
        t.symbol AS tco2_symbol
    FROM bct_deposits d
    LEFT JOIN tokens.erc20 t ON t.contract_address = d.tco2_address
        AND t.blockchain = 'polygon'
),

-- Per-depositor summary
depositor_summary AS (
    SELECT
        depositor,
        COUNT(*) AS n_deposits,
        COUNT(DISTINCT tco2_address) AS n_tco2_types,
        SUM(amount_tonnes) AS total_tonnes,
        MIN(block_time) AS first_deposit,
        MAX(block_time) AS last_deposit
    FROM bct_deposits
    GROUP BY depositor
)

SELECT * FROM bct_deposits
ORDER BY block_number ASC;

-- Second query: depositor portfolios (run separately)
-- This gets all TCO2 Transfer events to/from known BCT depositors
-- to reconstruct what they held vs. what they deposited.
/*
WITH depositors AS (
    SELECT DISTINCT "sender" AS depositor
    FROM toucan_protocol_polygon.Pool_evt_Deposited
    WHERE contract_address = 0x2F800Db0fdb5223b3C3f354886d907A671414A7F
),

tco2_transfers AS (
    SELECT
        evt_block_number,
        evt_block_time,
        contract_address AS tco2_address,
        "from" AS sender,
        "to" AS receiver,
        value / 1e18 AS amount_tonnes
    FROM erc20_polygon.evt_Transfer
    WHERE ("from" IN (SELECT depositor FROM depositors)
           OR "to" IN (SELECT depositor FROM depositors))
      AND contract_address IN (
          -- Filter to only TCO2 tokens (from factory)
          SELECT contract_address
          FROM toucan_protocol_polygon.ToucanCarbonOffsetsFactory_evt_TokenCreated
      )
)

SELECT * FROM tco2_transfers
ORDER BY evt_block_number ASC;
*/
"""


# ── Main pipeline ──────────────────────────────────────────────────────────

def save_json(data: Any, path: Path) -> None:
    path.write_text(json.dumps(data, indent=2, default=str))
    print(f"Saved: {path} ({path.stat().st_size / 1024:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(description="Fetch BCT deposit data from Polygon")
    parser.add_argument("--rpc", default="https://polygon-rpc.com",
                        help="Polygon RPC endpoint URL")
    parser.add_argument("--from-block", type=int, default=BCT_DEPLOY_BLOCK)
    parser.add_argument("--to-block", type=int, default=END_OF_2022_BLOCK)
    parser.add_argument("--polygonscan-api", type=str, default=None,
                        help="PolygonScan API key (alternative to RPC)")
    parser.add_argument("--skip-portfolios", action="store_true",
                        help="Skip portfolio reconstruction (expensive)")
    parser.add_argument("--dune-query-only", action="store_true",
                        help="Just print the Dune SQL query and exit")
    args = parser.parse_args()

    if args.dune_query_only:
        print(DUNE_QUERY_BCT_DEPOSITS)
        return

    # ── Step 1: Fetch deposits ─────────────────────────────────────────
    if args.polygonscan_api:
        deposits = fetch_deposits_polygonscan(args.polygonscan_api)
    else:
        try:
            w3 = connect_rpc(args.rpc)
            deposits = fetch_bct_deposits(w3, args.from_block, args.to_block)
        except ImportError:
            print("ERROR: web3 not installed. Install with: pip install web3")
            print("Alternatively, use --polygonscan-api or --dune-query-only")
            sys.exit(1)
        except ConnectionError as e:
            print(f"ERROR: {e}")
            print("Try a different RPC endpoint or use --polygonscan-api")
            sys.exit(1)

    save_json(deposits, HERE / "bct_deposits.json")

    # ── Step 2: Extract unique TCO2 addresses ──────────────────────────
    tco2_addresses = sorted(set(d["tco2_address"] for d in deposits))
    print(f"\nUnique TCO2 tokens deposited: {len(tco2_addresses)}")

    # ── Step 3: Fetch TCO2 metadata ────────────────────────────────────
    if not args.polygonscan_api:
        metadata = fetch_tco2_metadata(w3, tco2_addresses)
    else:
        # With PolygonScan, we'd need separate API calls for contract reads
        metadata = {addr: {"name": "PENDING", "symbol": "PENDING"} for addr in tco2_addresses}

    save_json(metadata, HERE / "tco2_metadata.json")

    # ── Step 4: Reconstruct depositor portfolios ───────────────────────
    if not args.skip_portfolios:
        if args.polygonscan_api:
            print("Portfolio reconstruction requires RPC access. Skipping.")
        else:
            portfolios = reconstruct_depositor_portfolios(
                w3, deposits, tco2_addresses
            )
            save_json(portfolios, HERE / "depositor_portfolios.json")
    else:
        print("Skipping portfolio reconstruction (--skip-portfolios)")

    # ── Step 5: Summary statistics ─────────────────────────────────────
    depositors = set(d["sender"] for d in deposits)
    total_tonnes = sum(d["amount_tonnes"] for d in deposits)

    summary = {
        "total_deposits": len(deposits),
        "unique_depositors": len(depositors),
        "unique_tco2_tokens": len(tco2_addresses),
        "total_tonnes_deposited": round(total_tonnes, 2),
        "block_range": [args.from_block, args.to_block],
        "note": "BCT pool deposits on Polygon, Oct 2021 - Dec 2022",
    }
    save_json(summary, HERE / "fetch_summary.json")

    print("\n" + "=" * 60)
    print("DATA COLLECTION SUMMARY")
    print("=" * 60)
    print(f"Total deposit events:   {len(deposits)}")
    print(f"Unique depositors:      {len(depositors)}")
    print(f"Unique TCO2 tokens:     {len(tco2_addresses)}")
    print(f"Total tonnes deposited: {total_tonnes:,.0f}")
    print(f"\nNext step: python3 analyze_adverse_selection.py")


if __name__ == "__main__":
    main()
