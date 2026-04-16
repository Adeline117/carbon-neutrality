#!/usr/bin/env python3
"""Wallet-level TCO2 portfolio reconstruction pipeline.

For every BCT deposit (wallet W at block B), reconstruct the wallet's full
TCO2 holdings at block B by replaying on-chain Transfer events. Then compute
a per-wallet Selection Index (SI) = mean deposited quality - mean retained
quality, with paired Wilcoxon tests, bootstrap CIs, and Cohen's d.

Inputs
------
  data/depositor-analysis/bct_deposits_complete.json
      1,187 BCT Deposited events (block_number, tx_hash, tco2_address,
      amount_tonnes; ~540 are missing the wallet address -- we refetch
      those via eth_getTransactionReceipt so tx.from is populated).

  data/depositor-analysis/tco2_metadata.json
      345 TCO2 tokens with project_id / vintage.

  data/depositor-analysis/tco2_scores_final.json
      Quality scores (composite 0-100, grade) for 161 scored TCO2s.

Outputs
-------
  data/depositor-analysis/bct_deposits_enriched.json
      Same as bct_deposits_complete.json but with `depositor` filled for
      every row.

  data/depositor-analysis/transfer_cache/<tco2>.json
      Cached Transfer events per TCO2 address (incremental, resumable).

  data/depositor-analysis/wallet_portfolios.json
      Per-wallet, per-deposit-timestamp portfolio snapshots:
        {wallet: {snapshots: [{block, deposited_tco2, deposited_tonnes,
                               deposited_quality, retained:
                               {tco2_addr: {balance_tonnes, quality}}}, ...]}}

  data/depositor-analysis/adverse_selection_per_wallet.md
      Per-wallet SI report with paired Wilcoxon + bootstrap CI + Cohen's d.

Design notes
------------
  * RPC: polygon.drpc.org free tier, 1000-block chunk limit. We issue
    concurrent single requests (20 workers) rather than JSON-RPC batches
    because drpc's free tier caps batch size at 3.
  * We ONLY fetch Transfer logs for the 161 scored TCO2s (those are the
    ones for which we can compute quality). Metadata exists for all 345
    but without a quality score we cannot use them in SI.
  * Transfer events are cached per TCO2 in data/depositor-analysis/
    transfer_cache/<tco2>.json with resume support -- each file stores
    (last_scanned_block, events[]). Re-running the pipeline picks up
    where it stopped.
  * After all transfers are cached, portfolio replay is a pure in-memory
    step: sort transfers by (block, log_index), compute running balances
    per (wallet, tco2), emit snapshot at every deposit block.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import requests

HERE = Path(__file__).resolve().parent
CACHE_DIR = HERE / "transfer_cache"
CACHE_DIR.mkdir(exist_ok=True)

# ── RPC config ─────────────────────────────────────────────────────────────

RPC_URL = "https://polygon.drpc.org"
CHUNK_BLOCKS = 1000           # drpc free-tier hard cap
MAX_WORKERS = 20              # concurrent requests
REQUEST_TIMEOUT = 30
RETRY_SLEEP = 1.0
MAX_RETRIES = 5

# ── Contract / event constants ─────────────────────────────────────────────

BCT_POOL = "0x2F800Db0fdb5223b3C3f354886d907A671414A7F".lower()
TRANSFER_TOPIC = (
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
)

# Block window for BCT adverse-selection period (Oct 2021 -- Dec 2022).
BCT_START_BLOCK = 20_000_000
BCT_END_BLOCK = 37_000_000


# ── Low-level RPC helper ───────────────────────────────────────────────────


def _rpc(method: str, params: list, session: requests.Session | None = None) -> Any:
    """Issue one JSON-RPC call with retries on 429/5xx."""
    sess = session or requests
    body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            r = sess.post(RPC_URL, json=body, timeout=REQUEST_TIMEOUT)
            if r.status_code == 429:
                time.sleep(RETRY_SLEEP * (2 ** attempt))
                continue
            if r.status_code >= 500:
                time.sleep(RETRY_SLEEP * (2 ** attempt))
                continue
            d = r.json()
            if "error" in d:
                msg = d["error"].get("message", "")
                if "rate" in msg.lower() or "limit" in msg.lower() or "batch" in msg.lower():
                    time.sleep(RETRY_SLEEP * (2 ** attempt))
                    continue
                raise RuntimeError(f"RPC error: {d['error']}")
            return d["result"]
        except (requests.Timeout, requests.ConnectionError) as e:
            last_err = e
            time.sleep(RETRY_SLEEP * (2 ** attempt))
    raise RuntimeError(f"RPC failed after {MAX_RETRIES} retries: {last_err}")


# ══════════════════════════════════════════════════════════════════════════
# Phase A -- Enrich deposits with wallet (tx.from)
# ══════════════════════════════════════════════════════════════════════════


def enrich_deposits_with_wallets(deposits_path: Path, out_path: Path) -> list[dict]:
    """Fill the missing `depositor` (= tx.from) field for every deposit row."""
    deposits = json.loads(deposits_path.read_text())
    missing = [d for d in deposits if "depositor" not in d]
    if not missing:
        print(f"[phase A] All {len(deposits)} deposits already enriched.")
        out_path.write_text(json.dumps(deposits, indent=2))
        return deposits

    print(f"[phase A] Enriching {len(missing)}/{len(deposits)} deposits with tx.from ...")

    # Dedup by tx_hash -- multiple Deposited events can share a tx
    tx_hashes = sorted({d["tx_hash"] for d in missing})
    print(f"[phase A] Unique tx_hashes to fetch: {len(tx_hashes)}")

    sess = requests.Session()
    from_by_tx: dict[str, str] = {}

    def fetch_tx(tx_hash: str) -> tuple[str, str | None]:
        try:
            rec = _rpc("eth_getTransactionReceipt", [tx_hash], session=sess)
            return (tx_hash, rec["from"].lower())
        except Exception as e:  # noqa: BLE001
            print(f"  WARN: tx {tx_hash[:12]}... fetch failed: {e}")
            return (tx_hash, None)

    done = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = [ex.submit(fetch_tx, th) for th in tx_hashes]
        for fut in as_completed(futs):
            tx, sender = fut.result()
            if sender is not None:
                from_by_tx[tx] = sender
            done += 1
            if done % 100 == 0:
                print(f"  {done}/{len(tx_hashes)} tx receipts fetched")

    # Merge into deposits
    for d in deposits:
        if "depositor" not in d:
            sender = from_by_tx.get(d["tx_hash"])
            if sender is not None:
                d["depositor"] = sender
        else:
            d["depositor"] = d["depositor"].lower()

    missing_after = [d for d in deposits if "depositor" not in d]
    if missing_after:
        print(f"[phase A] WARN: {len(missing_after)} deposits still missing depositor; dropping them.")
        deposits = [d for d in deposits if "depositor" in d]

    out_path.write_text(json.dumps(deposits, indent=2))
    wallets = sorted({d["depositor"] for d in deposits})
    print(f"[phase A] Saved {out_path.name}: {len(deposits)} deposits, {len(wallets)} unique wallets")
    return deposits


# ══════════════════════════════════════════════════════════════════════════
# Phase B -- Fetch all Transfer events per TCO2 (cached, resumable)
# ══════════════════════════════════════════════════════════════════════════


def _fetch_transfers_chunk(tco2: str, from_block: int, to_block: int,
                           session: requests.Session) -> list[dict]:
    """Fetch Transfer logs for one TCO2 in [from_block, to_block] (inclusive)."""
    logs = _rpc(
        "eth_getLogs",
        [{
            "address": tco2,
            "fromBlock": hex(from_block),
            "toBlock": hex(to_block),
            "topics": [TRANSFER_TOPIC],
        }],
        session=session,
    )
    out = []
    for l in logs:
        # Some RPCs skip topics for malformed logs; guard
        topics = l.get("topics", [])
        if len(topics) < 3:
            continue
        frm = "0x" + topics[1][-40:].lower()
        to = "0x" + topics[2][-40:].lower()
        data_hex = l.get("data", "0x")
        try:
            value_wei = int(data_hex, 16) if data_hex != "0x" else 0
        except ValueError:
            value_wei = 0
        out.append({
            "block": int(l["blockNumber"], 16),
            "log_index": int(l["logIndex"], 16),
            "tx_hash": l["transactionHash"],
            "from": frm,
            "to": to,
            "value_wei": str(value_wei),
        })
    return out


def _load_cache(tco2: str) -> dict:
    path = CACHE_DIR / f"{tco2}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {"tco2": tco2, "last_scanned_block": BCT_START_BLOCK - 1, "events": []}


def _save_cache(tco2: str, cache: dict) -> None:
    path = CACHE_DIR / f"{tco2}.json"
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cache))
    tmp.replace(path)


def fetch_transfers_for_tco2(
    tco2: str,
    end_block: int,
    report_every: int = 50,
    verbose: bool = False,
) -> dict:
    """Fetch Transfer events for one TCO2 over [BCT_START_BLOCK, end_block].

    Chunks are CHUNK_BLOCKS wide (drpc cap). Resumes from cache if present.
    """
    cache = _load_cache(tco2)
    start = max(cache["last_scanned_block"] + 1, BCT_START_BLOCK)
    if start > end_block:
        return cache

    # Build chunk list
    chunks: list[tuple[int, int]] = []
    b = start
    while b <= end_block:
        chunks.append((b, min(b + CHUNK_BLOCKS - 1, end_block)))
        b += CHUNK_BLOCKS

    sess = requests.Session()

    # Concurrent fetch, then sort into cache in order
    results: dict[int, list[dict]] = {}
    n_ok = 0
    t0 = time.time()

    def _worker(idx: int, frm: int, to: int) -> tuple[int, list[dict]]:
        return idx, _fetch_transfers_chunk(tco2, frm, to, sess)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(_worker, i, frm, to): (i, frm, to)
                for i, (frm, to) in enumerate(chunks)}
        for fut in as_completed(futs):
            try:
                idx, events = fut.result()
            except Exception as e:  # noqa: BLE001
                idx, frm, to = futs[fut]
                if verbose:
                    print(f"    chunk {idx} [{frm}-{to}] FAILED: {e}")
                # Retry sequentially
                try:
                    events = _fetch_transfers_chunk(tco2, frm, to, sess)
                except Exception as e2:  # noqa: BLE001
                    print(f"    chunk {idx} [{frm}-{to}] FAILED again: {e2}; skipping")
                    events = []
            results[idx] = events
            n_ok += 1
            if verbose and n_ok % report_every == 0:
                dt = time.time() - t0
                rate = n_ok / max(dt, 1e-9)
                print(f"    {n_ok}/{len(chunks)} chunks ({rate:.0f}/s)")

    # Append in block order
    new_events: list[dict] = []
    for i in range(len(chunks)):
        new_events.extend(results.get(i, []))
    cache["events"].extend(new_events)
    cache["events"].sort(key=lambda e: (e["block"], e["log_index"]))
    cache["last_scanned_block"] = end_block
    _save_cache(tco2, cache)
    return cache


def fetch_all_transfers(
    tco2_list: list[str],
    end_block: int,
    progress_every: int = 10,
    verbose_per_tco2: bool = False,
) -> None:
    """Phase B: fetch Transfer events for every TCO2 in `tco2_list`."""
    print(f"[phase B] Fetching transfers for {len(tco2_list)} TCO2s "
          f"(blocks {BCT_START_BLOCK}..{end_block}, {CHUNK_BLOCKS}-block chunks)")
    t0 = time.time()
    for i, tco2 in enumerate(tco2_list, 1):
        tco2 = tco2.lower()
        tstart = time.time()
        cache = fetch_transfers_for_tco2(tco2, end_block, verbose=verbose_per_tco2)
        dt = time.time() - tstart
        if i % progress_every == 0 or i == 1 or i == len(tco2_list):
            cum = time.time() - t0
            eta = cum / i * (len(tco2_list) - i)
            print(f"[phase B] {i}/{len(tco2_list)} {tco2} "
                  f"events={len(cache['events'])} ({dt:.1f}s)  "
                  f"cum={cum/60:.1f}m  ETA={eta/60:.1f}m")


# ══════════════════════════════════════════════════════════════════════════
# Phase C -- Replay transfers, reconstruct portfolios, compute SI
# ══════════════════════════════════════════════════════════════════════════


def load_all_transfers(tco2_list: list[str]) -> dict[str, list[dict]]:
    """Load cached transfer events for every TCO2."""
    out: dict[str, list[dict]] = {}
    for tco2 in tco2_list:
        tco2 = tco2.lower()
        cache = _load_cache(tco2)
        out[tco2] = cache.get("events", [])
    return out


def reconstruct_portfolios(
    deposits: list[dict],
    tco2_scores: dict[str, dict],
    transfers_by_tco2: dict[str, list[dict]],
) -> dict[str, dict]:
    """Build per-wallet portfolio snapshots at each deposit block.

    Algorithm:
      For each TCO2: walk its transfer events in (block, log_index) order,
      maintain running balance for every address seen. Whenever one of our
      tracked wallets hits a deposit block, record its current balance.

    Returns:
      {wallet: {
          "n_deposits": int,
          "snapshots": [
              {"block": int, "tx_hash": str,
               "deposited_tco2": str, "deposited_tonnes": float,
               "deposited_quality": float | None,
               "retained": {tco2_addr: {"balance_tonnes": float,
                                         "quality": float | None}}},
              ...
          ]
      }}
    """
    # Wallets we care about
    wallets = sorted({d["depositor"].lower() for d in deposits})
    wallet_set = set(wallets)

    # Deposit events grouped by wallet, sorted by block
    deposits_by_wallet: dict[str, list[dict]] = {}
    for d in deposits:
        w = d["depositor"].lower()
        deposits_by_wallet.setdefault(w, []).append({
            "block": d["block_number"],
            "tx_hash": d["tx_hash"],
            "tco2": d["tco2_address"].lower(),
            "amount": float(d["amount_tonnes"]),
        })
    for w in deposits_by_wallet:
        deposits_by_wallet[w].sort(key=lambda x: x["block"])

    # For each wallet we need a balance vector across all tracked TCO2s.
    # balances[wallet][tco2] = wei int.  Use dict-of-dict for sparsity.
    balances: dict[str, dict[str, int]] = {w: {} for w in wallet_set}

    # For each wallet x deposit-block pair we remember the balance vector at
    # (or immediately before) that block. We iterate per TCO2: each TCO2's
    # transfer stream is walked independently, and at the end of the walk we
    # know the wallet's final balance for that TCO2. But we also need the
    # balance AT a specific block B, not just the final balance.
    #
    # So per-wallet per-TCO2 we record the balance snapshot immediately
    # after the most recent transfer <= each deposit block.

    # Build per-TCO2 snapshot lookup: for each (wallet, tco2), we will emit
    # (block_of_snapshot, balance_wei) triples as we walk.
    # Instead of a dense matrix, we merge deposit blocks sorted per wallet
    # with the transfer stream.

    # Result accumulator: wallet_balances_at_block[w][b][tco2] = wei
    wallet_balances_at_block: dict[str, dict[int, dict[str, int]]] = {
        w: {d["block"]: {} for d in deposits_by_wallet.get(w, [])}
        for w in wallet_set
    }

    # For each TCO2, walk events; for each wallet touched, record balance
    # at every deposit block the wallet has (using sorted deposit blocks).
    for tco2, events in transfers_by_tco2.items():
        tco2 = tco2.lower()
        if not events:
            continue
        # per-wallet running balance for this TCO2
        wallet_bal: dict[str, int] = {}
        # per-wallet index into its sorted deposit blocks, for snapshotting
        wallet_deposit_blocks: dict[str, list[int]] = {
            w: [d["block"] for d in deposits_by_wallet.get(w, [])]
            for w in wallet_set
        }
        # Pointer: next deposit block index to snapshot per wallet
        wallet_ptr: dict[str, int] = {w: 0 for w in wallet_set}

        def snapshot_wallet_up_to(w: str, up_to_block: int) -> None:
            """Snapshot this wallet's balance for this TCO2 at every deposit
            block <= up_to_block that hasn't been snapshotted yet."""
            blocks = wallet_deposit_blocks.get(w, [])
            p = wallet_ptr[w]
            bal = wallet_bal.get(w, 0)
            while p < len(blocks) and blocks[p] < up_to_block:
                # This deposit-block is BEFORE the next transfer event =>
                # balance equals the current `bal`.
                db = blocks[p]
                if bal > 0:
                    wallet_balances_at_block[w][db][tco2] = bal
                p += 1
            wallet_ptr[w] = p

        for ev in events:
            block = ev["block"]
            frm = ev["from"]
            to = ev["to"]
            val = int(ev["value_wei"])

            # BEFORE applying this transfer, snapshot wallets whose deposit
            # blocks are strictly less than `block` (these deposits happened
            # before the transfer, so current balance is the correct one).
            if frm in wallet_set:
                snapshot_wallet_up_to(frm, block)
            if to in wallet_set:
                snapshot_wallet_up_to(to, block)

            # Apply the transfer.
            if frm in wallet_set:
                wallet_bal[frm] = wallet_bal.get(frm, 0) - val
            if to in wallet_set:
                wallet_bal[to] = wallet_bal.get(to, 0) + val

            # Also: if a deposit is on the SAME block as this transfer, the
            # order matters. Convention: deposit snapshots reflect the
            # balance AT the moment of the deposit, which in practice means
            # "after any prior transfers in the same tx". We conservatively
            # snapshot at the transfer's block including this transfer's
            # effect AFTER it's applied, so deposits at the same block see
            # the updated balance.
            if frm in wallet_set:
                snapshot_wallet_up_to(frm, block + 1)
            if to in wallet_set:
                snapshot_wallet_up_to(to, block + 1)

        # Flush remaining deposit blocks for every wallet that touched this
        # TCO2 (balance after all transfers).
        for w in wallet_set:
            blocks = wallet_deposit_blocks.get(w, [])
            p = wallet_ptr[w]
            bal = wallet_bal.get(w, 0)
            while p < len(blocks):
                db = blocks[p]
                if bal > 0:
                    wallet_balances_at_block[w][db][tco2] = bal
                p += 1

    # Now build per-wallet snapshots keyed by deposit event.
    portfolios: dict[str, dict] = {}
    for w in wallets:
        deps = deposits_by_wallet.get(w, [])
        snapshots = []
        for d in deps:
            block = d["block"]
            tco2_held = wallet_balances_at_block.get(w, {}).get(block, {})
            retained = {}
            for tco2_addr, wei in tco2_held.items():
                score = tco2_scores.get(tco2_addr, {}).get("composite")
                retained[tco2_addr] = {
                    "balance_tonnes": wei / 1e18,
                    "quality": score,
                }
            dep_quality = tco2_scores.get(d["tco2"], {}).get("composite")
            snapshots.append({
                "block": block,
                "tx_hash": d["tx_hash"],
                "deposited_tco2": d["tco2"],
                "deposited_tonnes": d["amount"],
                "deposited_quality": dep_quality,
                "retained": retained,
            })
        portfolios[w] = {
            "wallet": w,
            "n_deposits": len(deps),
            "snapshots": snapshots,
        }
    return portfolios


# ══════════════════════════════════════════════════════════════════════════
# Phase D -- Selection Index + statistics
# ══════════════════════════════════════════════════════════════════════════


def _mean(xs: list[float]) -> float | None:
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _weighted_mean(pairs: list[tuple[float, float]]) -> float | None:
    # pairs = [(value, weight), ...]
    pairs = [(v, w) for v, w in pairs if v is not None and w is not None and w > 0]
    if not pairs:
        return None
    W = sum(w for _, w in pairs)
    if W == 0:
        return None
    return sum(v * w for v, w in pairs) / W


def compute_selection_indices(portfolios: dict[str, dict]) -> dict:
    """Compute per-wallet Selection Index and aggregate statistics."""
    rows = []
    for w, pf in portfolios.items():
        # Aggregate all deposits by this wallet
        dep_pairs: list[tuple[float, float]] = []
        ret_pairs: list[tuple[float, float]] = []
        total_dep_tonnes = 0.0
        total_ret_tonnes = 0.0
        dep_tco2s: set[str] = set()
        ret_tco2s: set[str] = set()
        for snap in pf["snapshots"]:
            q = snap["deposited_quality"]
            t = snap["deposited_tonnes"]
            if q is not None:
                dep_pairs.append((q, t))
                total_dep_tonnes += t
                dep_tco2s.add(snap["deposited_tco2"])
            for tco2, info in snap["retained"].items():
                rq = info["quality"]
                rt = info["balance_tonnes"]
                if rq is not None and rt > 0:
                    ret_pairs.append((rq, rt))
                    total_ret_tonnes += rt
                    ret_tco2s.add(tco2)

        mean_dep = _mean([v for v, _ in dep_pairs])
        mean_ret = _mean([v for v, _ in ret_pairs])
        w_mean_dep = _weighted_mean(dep_pairs)
        w_mean_ret = _weighted_mean(ret_pairs)

        rows.append({
            "wallet": w,
            "n_deposits": pf["n_deposits"],
            "n_deposited_types": len(dep_tco2s),
            "n_retained_types": len(ret_tco2s),
            "total_deposited_tonnes": round(total_dep_tonnes, 4),
            "total_retained_tonnes": round(total_ret_tonnes, 4),
            "mean_deposited_quality": mean_dep,
            "mean_retained_quality": mean_ret,
            "weighted_deposited_quality": w_mean_dep,
            "weighted_retained_quality": w_mean_ret,
            "SI_unweighted": (mean_dep - mean_ret) if (mean_dep is not None and mean_ret is not None) else None,
            "SI_weighted": (w_mean_dep - w_mean_ret) if (w_mean_dep is not None and w_mean_ret is not None) else None,
        })

    # Summary statistics on wallets with paired observations.
    paired = [(r["mean_deposited_quality"], r["mean_retained_quality"])
              for r in rows
              if r["mean_deposited_quality"] is not None
              and r["mean_retained_quality"] is not None]
    d_vals = [a - b for a, b in paired]  # paired differences (SI)

    stats: dict[str, Any] = {
        "n_wallets_total": len(rows),
        "n_wallets_paired": len(paired),
        "n_wallets_SI_negative": sum(1 for x in d_vals if x < 0),
        "n_wallets_SI_zero": sum(1 for x in d_vals if x == 0),
        "n_wallets_SI_positive": sum(1 for x in d_vals if x > 0),
    }

    if d_vals:
        import numpy as np
        from scipy import stats as sstats

        arr = np.array(d_vals, dtype=float)
        stats["mean_SI"] = float(arr.mean())
        stats["median_SI"] = float(np.median(arr))
        stats["std_SI"] = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
        # Cohen's d for paired samples (dz): mean(d)/sd(d)
        stats["cohens_dz"] = float(arr.mean() / arr.std(ddof=1)) if (len(arr) > 1 and arr.std(ddof=1) > 0) else None

        # Paired Wilcoxon signed-rank (two-sided; H0: median(diff) == 0)
        try:
            nonzero = arr[arr != 0]
            if len(nonzero) >= 1:
                w_res = sstats.wilcoxon(nonzero, alternative="two-sided")
                stats["wilcoxon_statistic"] = float(w_res.statistic)
                stats["wilcoxon_pvalue_two_sided"] = float(w_res.pvalue)
                # One-sided: H1: mean_dep < mean_ret (SI < 0)
                w_less = sstats.wilcoxon(nonzero, alternative="less")
                stats["wilcoxon_pvalue_less"] = float(w_less.pvalue)
            else:
                stats["wilcoxon_statistic"] = None
                stats["wilcoxon_pvalue_two_sided"] = None
                stats["wilcoxon_pvalue_less"] = None
        except Exception as e:  # noqa: BLE001
            stats["wilcoxon_error"] = str(e)

        # Bootstrap 95% CI on mean SI
        rng = np.random.default_rng(42)
        boot_means = []
        n = len(arr)
        for _ in range(10_000):
            sample = rng.choice(arr, size=n, replace=True)
            boot_means.append(sample.mean())
        lo, hi = np.percentile(boot_means, [2.5, 97.5])
        stats["bootstrap_mean_SI_ci95"] = [float(lo), float(hi)]
        stats["bootstrap_n_iter"] = 10_000

    # Volume-weighted aggregate SI across ALL deposits / retained balances.
    dep_pairs_all: list[tuple[float, float]] = []
    ret_pairs_all: list[tuple[float, float]] = []
    for r in rows:
        for pf_wallet, pf in portfolios.items():
            if pf_wallet != r["wallet"]:
                continue
            for snap in pf["snapshots"]:
                if snap["deposited_quality"] is not None:
                    dep_pairs_all.append((snap["deposited_quality"], snap["deposited_tonnes"]))
                for info in snap["retained"].values():
                    if info["quality"] is not None and info["balance_tonnes"] > 0:
                        ret_pairs_all.append((info["quality"], info["balance_tonnes"]))
    w_dep = _weighted_mean(dep_pairs_all)
    w_ret = _weighted_mean(ret_pairs_all)
    if w_dep is not None and w_ret is not None:
        stats["volume_weighted_SI_aggregate"] = float(w_dep - w_ret)
        stats["volume_weighted_mean_deposited_quality"] = float(w_dep)
        stats["volume_weighted_mean_retained_quality"] = float(w_ret)

    return {"per_wallet": rows, "aggregate": stats}


def write_markdown_report(
    si_result: dict,
    out_path: Path,
    pool: str = "Toucan BCT (Polygon)",
) -> None:
    agg = si_result["aggregate"]
    rows = sorted(
        si_result["per_wallet"],
        key=lambda r: (r["SI_unweighted"] if r["SI_unweighted"] is not None else 1e9),
    )

    lines: list[str] = []
    lines.append(f"# Wallet-level adverse selection -- {pool}\n")
    lines.append(f"Generated by `reconstruct_portfolios.py` from real on-chain data.\n")
    lines.append("## Aggregate statistics\n")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Wallets total | {agg.get('n_wallets_total')} |")
    lines.append(f"| Wallets with paired (deposited, retained) observations | {agg.get('n_wallets_paired')} |")
    lines.append(f"| Wallets with SI < 0 (deposited worse than retained) | {agg.get('n_wallets_SI_negative')} |")
    lines.append(f"| Wallets with SI = 0 | {agg.get('n_wallets_SI_zero')} |")
    lines.append(f"| Wallets with SI > 0 | {agg.get('n_wallets_SI_positive')} |")
    if agg.get("n_wallets_paired"):
        pct_neg = 100 * agg["n_wallets_SI_negative"] / agg["n_wallets_paired"]
        lines.append(f"| Share of wallets with SI < 0 | {pct_neg:.1f}% |")
    if "mean_SI" in agg:
        lines.append(f"| Mean SI across wallets | {agg['mean_SI']:.3f} |")
        lines.append(f"| Median SI across wallets | {agg['median_SI']:.3f} |")
        lines.append(f"| SD of SI | {agg['std_SI']:.3f} |")
    if agg.get("cohens_dz") is not None:
        lines.append(f"| Cohen's d_z (paired effect size) | {agg['cohens_dz']:.3f} |")
    if "bootstrap_mean_SI_ci95" in agg:
        lo, hi = agg["bootstrap_mean_SI_ci95"]
        lines.append(f"| Bootstrap 95% CI on mean SI (10k iter) | [{lo:.3f}, {hi:.3f}] |")
    if agg.get("wilcoxon_pvalue_two_sided") is not None:
        lines.append(f"| Wilcoxon signed-rank p (two-sided) | {agg['wilcoxon_pvalue_two_sided']:.3e} |")
    if agg.get("wilcoxon_pvalue_less") is not None:
        lines.append(f"| Wilcoxon p (H1: SI < 0) | {agg['wilcoxon_pvalue_less']:.3e} |")
    if "volume_weighted_SI_aggregate" in agg:
        lines.append(f"| Volume-weighted aggregate SI (tonnes-weighted) | {agg['volume_weighted_SI_aggregate']:.3f} |")
        lines.append(f"| Volume-weighted mean deposited quality | {agg['volume_weighted_mean_deposited_quality']:.2f} |")
        lines.append(f"| Volume-weighted mean retained quality | {agg['volume_weighted_mean_retained_quality']:.2f} |")
    lines.append("")
    lines.append("## Per-wallet table (sorted by SI ascending)\n")
    lines.append("| Wallet | N deposits | N deposited types | N retained types | Deposited tonnes | Retained tonnes | Mean dep Q | Mean ret Q | SI (unweighted) | SI (weighted) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    def _fmt(x: float | None, nd: int = 2) -> str:
        if x is None: return "n/a"
        return f"{x:.{nd}f}"
    for r in rows:
        lines.append("| " + " | ".join([
            r["wallet"],
            str(r["n_deposits"]),
            str(r["n_deposited_types"]),
            str(r["n_retained_types"]),
            _fmt(r["total_deposited_tonnes"], 1),
            _fmt(r["total_retained_tonnes"], 1),
            _fmt(r["mean_deposited_quality"]),
            _fmt(r["mean_retained_quality"]),
            _fmt(r["SI_unweighted"]),
            _fmt(r["SI_weighted"]),
        ]) + " |")
    lines.append("")
    lines.append("## Method\n")
    lines.append(
        "For each BCT deposit event (wallet W, block B, TCO2 X, amount A), we "
        "replay all on-chain `Transfer(address,address,uint256)` events on the "
        f"161 scored TCO2 tokens across blocks {BCT_START_BLOCK}..{BCT_END_BLOCK} "
        "(Oct 2021 -- Dec 2022) in `{CHUNK_BLOCKS}`-block chunks on "
        "polygon.drpc.org, reconstruct W's balance vector at block B, and "
        "compare the quality score (composite 0-100) of the credit X that W "
        "chose to deposit against the tonnes-weighted mean quality of the "
        "credits W simultaneously retained. Per wallet we collapse multiple "
        "deposits into a single Selection Index (SI) via simple mean (and "
        "tonnes-weighted mean). We then test H0: median(SI) = 0 with a "
        "paired Wilcoxon signed-rank test across wallets, and report a "
        "10,000-iteration bootstrap 95% CI on the mean SI plus Cohen's d_z "
        "as the paired-effect-size statistic."
    )
    out_path.write_text("\n".join(lines))


# ══════════════════════════════════════════════════════════════════════════
# Orchestration
# ══════════════════════════════════════════════════════════════════════════


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["A", "B", "C", "all"], default="all",
                    help="A=enrich deposits with tx.from, B=fetch transfers, "
                         "C=reconstruct + compute SI.")
    ap.add_argument("--end-block", type=int, default=BCT_END_BLOCK,
                    help="Last block to scan for Transfer events.")
    ap.add_argument("--only-scored", action="store_true", default=True,
                    help="Only fetch transfers for TCO2s with quality scores.")
    ap.add_argument("--limit-tco2", type=int, default=0,
                    help="Only process the first N TCO2s (for testing).")
    ap.add_argument("--verbose-per-tco2", action="store_true",
                    help="Print progress inside each TCO2's chunk loop.")
    args = ap.parse_args()

    deposits_path = HERE / "bct_deposits_complete.json"
    enriched_path = HERE / "bct_deposits_enriched.json"
    scores_path = HERE / "tco2_scores_final.json"
    portfolios_path = HERE / "wallet_portfolios.json"
    md_path = HERE / "adverse_selection_per_wallet.md"

    # Load / enrich deposits
    if args.phase in ("A", "all"):
        deposits = enrich_deposits_with_wallets(deposits_path, enriched_path)
    else:
        if not enriched_path.exists():
            print("ERROR: enriched deposits not found; run phase A first.")
            sys.exit(1)
        deposits = json.loads(enriched_path.read_text())

    # Load scores
    tco2_scores: dict[str, dict] = {
        k.lower(): v for k, v in json.loads(scores_path.read_text()).items()
    }

    if args.only_scored:
        tco2_list = sorted(tco2_scores.keys())
    else:
        meta = json.loads((HERE / "tco2_metadata.json").read_text())
        tco2_list = sorted(k.lower() for k in meta.keys())
    if args.limit_tco2 > 0:
        tco2_list = tco2_list[:args.limit_tco2]

    print(f"[main] TCO2s to process: {len(tco2_list)}")

    if args.phase in ("B", "all"):
        fetch_all_transfers(tco2_list, end_block=args.end_block,
                            verbose_per_tco2=args.verbose_per_tco2)

    if args.phase in ("C", "all"):
        transfers = load_all_transfers(tco2_list)
        n_events = sum(len(v) for v in transfers.values())
        print(f"[phase C] Loaded {n_events:,} Transfer events across {len(transfers)} TCO2s.")
        portfolios = reconstruct_portfolios(deposits, tco2_scores, transfers)
        portfolios_path.write_text(json.dumps(portfolios, indent=2, default=str))
        print(f"[phase C] Saved {portfolios_path.name} "
              f"({portfolios_path.stat().st_size/1024:.1f} KB, "
              f"{len(portfolios)} wallets).")

        si = compute_selection_indices(portfolios)
        (HERE / "wallet_selection_index.json").write_text(
            json.dumps(si, indent=2, default=str)
        )
        write_markdown_report(si, md_path)
        print(f"[phase C] Saved {md_path.name}")

        agg = si["aggregate"]
        print("\n" + "=" * 60)
        print("WALLET-LEVEL SELECTION INDEX SUMMARY")
        print("=" * 60)
        print(f"  Wallets paired: {agg.get('n_wallets_paired')}")
        print(f"  Wallets SI<0:   {agg.get('n_wallets_SI_negative')}")
        if "mean_SI" in agg:
            print(f"  Mean SI:        {agg['mean_SI']:.3f}")
            print(f"  Median SI:      {agg['median_SI']:.3f}")
        if agg.get("cohens_dz") is not None:
            print(f"  Cohen's d_z:    {agg['cohens_dz']:.3f}")
        if "bootstrap_mean_SI_ci95" in agg:
            lo, hi = agg["bootstrap_mean_SI_ci95"]
            print(f"  95% CI on mean: [{lo:.3f}, {hi:.3f}]")
        if agg.get("wilcoxon_pvalue_two_sided") is not None:
            print(f"  Wilcoxon p:     {agg['wilcoxon_pvalue_two_sided']:.3e}")
        if "volume_weighted_SI_aggregate" in agg:
            print(f"  Vol-wtd SI:     {agg['volume_weighted_SI_aggregate']:.3f}")


if __name__ == "__main__":
    main()
