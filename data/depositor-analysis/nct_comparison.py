#!/usr/bin/env python3
"""NCT vs BCT temporal quality comparison.

Fetches NCT (Nature Carbon Tonne) pool Deposited events from Polygon,
scores each deposit using tco2_scores_final.json, then runs the same
temporal-degradation analysis as BCT (Spearman rho, quartile breakdown,
Mann-Whitney) and computes a cross-pool difference-in-differences (DiD).

The actual Toucan Pool event is:
    event Deposited(address erc20Addr, uint256 amount)
    topic0 = keccak256("Deposited(address,uint256)")
           = 0x2da466a7b24304f47e87fa2e1e5a81b9831ce54fec19055ce277ca2f39ba42c4
Both params are non-indexed (encoded in data). The depositor (sender)
is NOT in the event and must be recovered from the transaction receipt.

NCT has an AFOLU filter (only nature-based credits) + vintage >= 2012.
The hypothesis: BCT exhibits temporal quality degradation (rho = -0.44)
due to its permissionless mechanism, while NCT (with quality filters)
does NOT -- proving the degradation is caused by pool design, not
supply-side changes.

Outputs:
    nct_deposits.json              -- raw NCT deposit events
    nct_comparison_results.json    -- full comparison statistics
"""

from __future__ import annotations

import json
import math
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import requests

HERE = Path(__file__).resolve().parent

# ── RPC config ─────────────────────────────────────────────────────────────

RPC_URL = "https://polygon.drpc.org"
CHUNK_BLOCKS = 1000           # drpc free-tier hard cap
MAX_WORKERS = 20              # concurrent requests
REQUEST_TIMEOUT = 30
RETRY_SLEEP = 1.0
MAX_RETRIES = 5

# ── Contract / event constants ─────────────────────────────────────────────

NCT_POOL = "0xD838290e877E0188a4A44700463419ED96c16107"
BCT_POOL = "0x2F800Db0fdb5223b3C3f354886d907A671414A7F"

# Block window matching BCT analysis (Oct 2021 -- Dec 2022)
START_BLOCK = 20_000_000
END_BLOCK   = 37_000_000

# Actual Toucan Pool event: Deposited(address erc20Addr, uint256 amount)
# Both params are NON-indexed (in data), no indexed topics beyond topic0.
DEPOSITED_TOPIC0 = "0x2da466a7b24304f47e87fa2e1e5a81b9831ce54fec19055ce277ca2f39ba42c4"


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
# Step 1: Fetch Deposited events (for both NCT and BCT)
# ══════════════════════════════════════════════════════════════════════════

def fetch_deposits_chunk(
    pool_address: str,
    from_block: int,
    to_block: int,
    session: requests.Session,
) -> list[dict]:
    """Fetch Deposited(address,uint256) logs for a pool in [from_block, to_block].

    Event layout:
        topic0 = 0x2da466a7...
        data   = abi.encode(address erc20Addr, uint256 amount)
               = 32 bytes (address padded) + 32 bytes (uint256)
    """
    logs = _rpc(
        "eth_getLogs",
        [{
            "address": pool_address,
            "fromBlock": hex(from_block),
            "toBlock": hex(to_block),
            "topics": [DEPOSITED_TOPIC0],
        }],
        session=session,
    )
    deposits = []
    for log in logs:
        data = log.get("data", "0x")
        if len(data) < 130:
            continue  # Malformed, need at least 2 x 32 bytes + "0x"

        # Decode: first 32 bytes = address (right-aligned), next 32 bytes = uint256
        erc20 = "0x" + data[26:66]
        amount_hex = data[66:130]
        try:
            amount_wei = int(amount_hex, 16)
        except ValueError:
            amount_wei = 0

        deposits.append({
            "block_number": int(log["blockNumber"], 16),
            "tx_hash": log["transactionHash"],
            "tco2_address": erc20.lower(),
            "amount_wei": str(amount_wei),
            "amount_tonnes": amount_wei / 1e18,
            "log_index": int(log["logIndex"], 16),
        })
    return deposits


def fetch_all_deposits(pool_address: str, pool_name: str) -> list[dict]:
    """Fetch all Deposited events in [START_BLOCK, END_BLOCK] using
    concurrent 1000-block chunks."""

    print(f"\n{'='*60}")
    print(f"FETCHING {pool_name} DEPOSITED EVENTS")
    print(f"{'='*60}")
    print(f"Pool: {pool_address}")
    print(f"Topic0: {DEPOSITED_TOPIC0}")
    print(f"Block range: {START_BLOCK:,} - {END_BLOCK:,}")
    print(f"Chunk size: {CHUNK_BLOCKS} blocks, {MAX_WORKERS} workers")
    sys.stdout.flush()

    # Build chunk list
    chunks = []
    b = START_BLOCK
    while b <= END_BLOCK:
        chunks.append((b, min(b + CHUNK_BLOCKS - 1, END_BLOCK)))
        b += CHUNK_BLOCKS

    print(f"Total chunks: {len(chunks):,}")
    sys.stdout.flush()

    sess = requests.Session()
    all_deposits = []
    completed = 0
    t0 = time.time()
    errors = 0

    def worker(idx: int, frm: int, to: int):
        return idx, fetch_deposits_chunk(pool_address, frm, to, sess)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(worker, i, frm, to): (i, frm, to)
                for i, (frm, to) in enumerate(chunks)}
        for fut in as_completed(futs):
            try:
                idx, deposits = fut.result()
                all_deposits.extend(deposits)
            except Exception as e:
                i, frm, to = futs[fut]
                errors += 1
                # Retry once
                try:
                    time.sleep(1)
                    deposits = fetch_deposits_chunk(pool_address, frm, to, sess)
                    all_deposits.extend(deposits)
                except Exception:
                    print(f"  WARN: chunk [{frm}-{to}] failed twice")
            completed += 1
            if completed % 2000 == 0 or completed == len(chunks):
                elapsed = time.time() - t0
                rate = completed / max(elapsed, 1e-9)
                eta = (len(chunks) - completed) / max(rate, 1e-9)
                print(f"  {completed}/{len(chunks)} chunks "
                      f"({elapsed/60:.1f}m elapsed, ETA {eta/60:.1f}m) "
                      f"deposits so far: {len(all_deposits)}")
                sys.stdout.flush()

    # Sort by block number
    all_deposits.sort(key=lambda d: (d["block_number"], d["log_index"]))

    elapsed = time.time() - t0
    print(f"\nFetch complete: {len(all_deposits)} {pool_name} deposits "
          f"in {elapsed/60:.1f} minutes")
    if errors:
        print(f"  ({errors} chunk errors encountered)")
    sys.stdout.flush()

    return all_deposits


def enrich_with_senders(deposits: list[dict]) -> list[dict]:
    """Fetch tx.from for each deposit via eth_getTransactionReceipt.

    The Deposited event does not include the sender address. We recover
    it from the transaction receipt's `from` field.
    """
    # De-duplicate by tx_hash (multiple deposits can share one tx)
    tx_hashes = sorted({d["tx_hash"] for d in deposits})
    print(f"\nEnriching {len(deposits)} deposits with sender from "
          f"{len(tx_hashes)} unique transactions...")
    sys.stdout.flush()

    sess = requests.Session()
    from_by_tx: dict[str, str] = {}

    def fetch_tx(tx_hash: str) -> tuple[str, str | None]:
        try:
            rec = _rpc("eth_getTransactionReceipt", [tx_hash], session=sess)
            return (tx_hash, rec["from"].lower())
        except Exception:
            return (tx_hash, None)

    done = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = [ex.submit(fetch_tx, th) for th in tx_hashes]
        for fut in as_completed(futs):
            tx, sender = fut.result()
            if sender is not None:
                from_by_tx[tx] = sender
            done += 1
            if done % 100 == 0 or done == len(tx_hashes):
                print(f"  {done}/{len(tx_hashes)} tx receipts fetched")
                sys.stdout.flush()

    for d in deposits:
        d["depositor"] = from_by_tx.get(d["tx_hash"], "unknown")

    n_resolved = sum(1 for d in deposits if d["depositor"] != "unknown")
    print(f"  Resolved: {n_resolved}/{len(deposits)}")
    return deposits


# ══════════════════════════════════════════════════════════════════════════
# Step 2: Score deposits
# ══════════════════════════════════════════════════════════════════════════

def score_deposits(
    deposits: list[dict],
    tco2_scores: dict[str, dict],
    tco2_metadata: dict[str, dict],
) -> list[dict]:
    """Add quality score to each deposit using tco2_scores_final.json."""

    scored = 0
    unscored_tco2s = set()

    for dep in deposits:
        addr = dep["tco2_address"].lower()
        if addr in tco2_scores:
            dep["composite_quality"] = tco2_scores[addr]["composite"]
            dep["grade"] = tco2_scores[addr].get("grade")
            dep["credit_type"] = tco2_scores[addr].get("type")
            scored += 1
        elif addr in tco2_metadata:
            dep["composite_quality"] = None
            dep["grade"] = None
            dep["credit_type"] = "AFOLU (unscored)"
            unscored_tco2s.add(addr)
        else:
            dep["composite_quality"] = None
            dep["grade"] = None
            dep["credit_type"] = "unknown"
            unscored_tco2s.add(addr)

    print(f"\nScoring results:")
    print(f"  Scored deposits: {scored}/{len(deposits)}")
    print(f"  Unscored unique TCO2s: {len(unscored_tco2s)}")
    if unscored_tco2s:
        print(f"  Unscored TCO2 addresses (first 5): {sorted(unscored_tco2s)[:5]}")
    sys.stdout.flush()

    return deposits


# ══════════════════════════════════════════════════════════════════════════
# Step 3: Temporal analysis (matching BCT methodology)
# ══════════════════════════════════════════════════════════════════════════

def temporal_analysis(deposits: list[dict], pool_name: str) -> dict:
    """Run Spearman rho, quartile breakdown, Mann-Whitney on deposit quality
    over time (block number). Matches the BCT temporal analysis exactly."""
    import numpy as np
    from scipy import stats as sstats

    # Filter to scored deposits only
    scored = [d for d in deposits if d.get("composite_quality") is not None]
    if not scored:
        return {
            "pool": pool_name,
            "error": f"No scored deposits for {pool_name}",
            "n_deposits_total": len(deposits),
            "n_deposits_scored": 0,
        }

    blocks = np.array([d["block_number"] for d in scored], dtype=float)
    quality = np.array([d["composite_quality"] for d in scored], dtype=float)
    tonnes = np.array([d["amount_tonnes"] for d in scored], dtype=float)

    result = {
        "pool": pool_name,
        "n_deposits_total": len(deposits),
        "n_deposits_scored": len(scored),
        "pct_scored": round(100 * len(scored) / len(deposits), 1) if deposits else 0,
        "block_range": [int(blocks.min()), int(blocks.max())],
        "mean_quality": float(quality.mean()),
        "median_quality": float(np.median(quality)),
        "std_quality": float(quality.std(ddof=1)) if len(quality) > 1 else 0.0,
        "total_tonnes": float(tonnes.sum()),
    }

    # Volume-weighted mean quality
    if tonnes.sum() > 0:
        result["volume_weighted_mean_quality"] = float(
            np.average(quality, weights=tonnes)
        )

    # ── Spearman rho: block_number vs composite_quality ──
    if len(scored) >= 3:
        rho, p_spearman = sstats.spearmanr(blocks, quality)
        result["spearman_rho"] = float(rho)
        result["spearman_p"] = float(p_spearman)
    else:
        result["spearman_rho"] = None
        result["spearman_p"] = None

    # ── Quartile breakdown ──
    n = len(scored)
    quartile_size = n // 4
    if quartile_size > 0:
        order = np.argsort(blocks)
        sorted_quality = quality[order]
        sorted_blocks = blocks[order]
        sorted_tonnes = tonnes[order]

        quartiles = {}
        for qi in range(4):
            start_idx = qi * quartile_size
            end_idx = (qi + 1) * quartile_size if qi < 3 else n
            q_quality = sorted_quality[start_idx:end_idx]
            q_tonnes = sorted_tonnes[start_idx:end_idx]
            q_blocks = sorted_blocks[start_idx:end_idx]

            quartiles[f"Q{qi+1}"] = {
                "n": int(len(q_quality)),
                "mean_quality": float(q_quality.mean()),
                "median_quality": float(np.median(q_quality)),
                "std_quality": float(q_quality.std(ddof=1)) if len(q_quality) > 1 else 0.0,
                "total_tonnes": float(q_tonnes.sum()),
                "block_range": [int(q_blocks.min()), int(q_blocks.max())],
            }
            if q_tonnes.sum() > 0:
                quartiles[f"Q{qi+1}"]["vol_weighted_quality"] = float(
                    np.average(q_quality, weights=q_tonnes)
                )

        result["quartiles"] = quartiles

        q1_mean = quartiles["Q1"]["mean_quality"]
        q4_mean = quartiles["Q4"]["mean_quality"]
        result["Q1_Q4_diff"] = float(q1_mean - q4_mean)

    # ── Mann-Whitney: first half vs second half ──
    if n >= 4:
        mid = n // 2
        order = np.argsort(blocks)
        first_half = quality[order[:mid]]
        second_half = quality[order[mid:]]

        result["first_half_mean"] = float(first_half.mean())
        result["second_half_mean"] = float(second_half.mean())
        result["half_diff"] = float(first_half.mean() - second_half.mean())

        try:
            u_stat, p_mw = sstats.mannwhitneyu(
                first_half, second_half, alternative="two-sided"
            )
            result["mannwhitney_U"] = float(u_stat)
            result["mannwhitney_p"] = float(p_mw)
        except Exception as e:
            result["mannwhitney_error"] = str(e)

    # ── Kendall tau ──
    if len(scored) >= 3:
        try:
            tau, p_tau = sstats.kendalltau(blocks, quality)
            result["kendall_tau"] = float(tau)
            result["kendall_p"] = float(p_tau)
        except Exception:
            pass

    # ── OLS slope: quality per 1M blocks ──
    if len(scored) >= 3:
        coeffs = np.polyfit(blocks, quality, 1)
        slope_per_block = coeffs[0]
        result["ols_slope_per_1M_blocks"] = float(slope_per_block * 1_000_000)

    return result


# ══════════════════════════════════════════════════════════════════════════
# Step 4: Cross-pool Difference-in-Differences
# ══════════════════════════════════════════════════════════════════════════

def compute_did(bct_temporal: dict, nct_temporal: dict) -> dict:
    """Compute difference-in-differences: the causal effect of BCT's
    permissionless mechanism on temporal quality degradation.

    DiD = (BCT_late - BCT_early) - (NCT_late - NCT_early)

    If DiD is significantly negative, it means BCT's degradation is
    worse than NCT's, attributable to the pool mechanism (not supply).
    """
    did = {
        "method": "Difference-in-Differences (DiD)",
        "treatment": "BCT (permissionless pool)",
        "control": "NCT (AFOLU-filtered pool, vintage >= 2012)",
    }

    # Using first-half vs second-half means
    bct_early = bct_temporal.get("first_half_mean")
    bct_late = bct_temporal.get("second_half_mean")
    nct_early = nct_temporal.get("first_half_mean")
    nct_late = nct_temporal.get("second_half_mean")

    if all(v is not None for v in [bct_early, bct_late, nct_early, nct_late]):
        bct_change = bct_late - bct_early
        nct_change = nct_late - nct_early
        did_estimate = bct_change - nct_change

        did["bct_early_mean"] = float(bct_early)
        did["bct_late_mean"] = float(bct_late)
        did["bct_change"] = float(bct_change)
        did["nct_early_mean"] = float(nct_early)
        did["nct_late_mean"] = float(nct_late)
        did["nct_change"] = float(nct_change)
        did["did_estimate"] = float(did_estimate)
        did["interpretation"] = (
            f"BCT quality changed by {bct_change:+.2f} points "
            f"(early {bct_early:.2f} -> late {bct_late:.2f}). "
            f"NCT quality changed by {nct_change:+.2f} points "
            f"(early {nct_early:.2f} -> late {nct_late:.2f}). "
            f"DiD = {did_estimate:+.2f}. "
        )
        if did_estimate < -1:
            did["interpretation"] += (
                "BCT's decline EXCEEDS NCT's, confirming that the "
                "permissionless pool mechanism drives quality degradation "
                "beyond supply-side changes."
            )
        elif abs(did_estimate) < 1:
            did["interpretation"] += (
                "Both pools show similar trends, suggesting supply-side "
                "factors may dominate."
            )
        else:
            did["interpretation"] += (
                "NCT shows greater decline than BCT, which is unexpected."
            )

    # Using Q1 vs Q4 means
    bct_q1 = bct_temporal.get("quartiles", {}).get("Q1", {}).get("mean_quality")
    bct_q4 = bct_temporal.get("quartiles", {}).get("Q4", {}).get("mean_quality")
    nct_q1 = nct_temporal.get("quartiles", {}).get("Q1", {}).get("mean_quality")
    nct_q4 = nct_temporal.get("quartiles", {}).get("Q4", {}).get("mean_quality")

    if all(v is not None for v in [bct_q1, bct_q4, nct_q1, nct_q4]):
        bct_q_change = bct_q4 - bct_q1
        nct_q_change = nct_q4 - nct_q1
        did_q = bct_q_change - nct_q_change

        did["quartile_did"] = {
            "bct_Q1_mean": float(bct_q1),
            "bct_Q4_mean": float(bct_q4),
            "bct_Q1_Q4_change": float(bct_q_change),
            "nct_Q1_mean": float(nct_q1),
            "nct_Q4_mean": float(nct_q4),
            "nct_Q1_Q4_change": float(nct_q_change),
            "did_estimate": float(did_q),
        }

    # Spearman rho comparison with Fisher z-test
    bct_rho = bct_temporal.get("spearman_rho")
    nct_rho = nct_temporal.get("spearman_rho")
    if bct_rho is not None and nct_rho is not None:
        did["spearman_comparison"] = {
            "bct_rho": float(bct_rho),
            "nct_rho": float(nct_rho),
            "rho_difference": float(bct_rho - nct_rho),
            "bct_p": float(bct_temporal.get("spearman_p", float("nan"))),
            "nct_p": float(nct_temporal.get("spearman_p", float("nan"))),
        }

        import numpy as np
        try:
            z_bct = np.arctanh(bct_rho)
            z_nct = np.arctanh(nct_rho)
            n_bct = bct_temporal.get("n_deposits_scored", 0)
            n_nct = nct_temporal.get("n_deposits_scored", 0)
            if n_bct > 3 and n_nct > 3:
                se = math.sqrt(1.0/(n_bct - 3) + 1.0/(n_nct - 3))
                z_diff = (z_bct - z_nct) / se
                from scipy.stats import norm
                p_diff = 2 * norm.sf(abs(z_diff))
                did["spearman_comparison"]["fisher_z_diff"] = float(z_diff)
                did["spearman_comparison"]["fisher_p"] = float(p_diff)
                did["spearman_comparison"]["fisher_interpretation"] = (
                    f"Fisher z-test for rho difference: z={z_diff:.3f}, p={p_diff:.4f}. "
                    + ("Significant difference (p < 0.05)." if p_diff < 0.05
                       else "Not significant (p >= 0.05).")
                )
        except Exception:
            pass

    return did


# ══════════════════════════════════════════════════════════════════════════
# Printing
# ══════════════════════════════════════════════════════════════════════════

def print_temporal_summary(result: dict, label: str) -> None:
    """Pretty-print temporal analysis results."""
    if "error" in result:
        print(f"\n  {label}: {result['error']}")
        return

    print(f"\n{'_'*60}")
    print(f"  {label} TEMPORAL ANALYSIS")
    print(f"{'_'*60}")
    print(f"  Total deposits:        {result.get('n_deposits_total', '?')}")
    print(f"  Scored deposits:       {result.get('n_deposits_scored', '?')} "
          f"({result.get('pct_scored', '?')}%)")
    print(f"  Mean quality:          {result.get('mean_quality', '?'):.2f}")
    print(f"  Median quality:        {result.get('median_quality', '?'):.2f}")
    if result.get("volume_weighted_mean_quality") is not None:
        print(f"  Vol-weighted quality:  {result['volume_weighted_mean_quality']:.2f}")
    print(f"  Total tonnes:          {result.get('total_tonnes', 0):,.0f}")

    rho = result.get("spearman_rho")
    if rho is not None:
        print(f"\n  Spearman rho:          {rho:.4f} (p={result.get('spearman_p', '?'):.2e})")
    tau = result.get("kendall_tau")
    if tau is not None:
        print(f"  Kendall tau:           {tau:.4f} (p={result.get('kendall_p', '?'):.2e})")
    slope = result.get("ols_slope_per_1M_blocks")
    if slope is not None:
        print(f"  OLS slope/1M blocks:   {slope:.2f}")

    if "quartiles" in result:
        print(f"\n  Quartile breakdown:")
        for q in ["Q1", "Q2", "Q3", "Q4"]:
            qi = result["quartiles"].get(q, {})
            print(f"    {q}: mean={qi.get('mean_quality', '?'):.2f}, "
                  f"n={qi.get('n', '?')}, "
                  f"tonnes={qi.get('total_tonnes', 0):,.0f}")
        print(f"  Q1-Q4 diff:            {result.get('Q1_Q4_diff', '?'):+.2f}")

    if result.get("first_half_mean") is not None:
        print(f"\n  First half mean:       {result['first_half_mean']:.2f}")
        print(f"  Second half mean:      {result['second_half_mean']:.2f}")
        print(f"  Half diff:             {result.get('half_diff', 0):+.2f}")
    if result.get("mannwhitney_p") is not None:
        print(f"  Mann-Whitney U p:      {result['mannwhitney_p']:.2e}")
    sys.stdout.flush()


# ══════════════════════════════════════════════════════════════════════════
# Main pipeline
# ══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("NCT vs BCT TEMPORAL QUALITY COMPARISON")
    print("=" * 60)
    sys.stdout.flush()

    # Load scoring data
    scores_path = HERE / "tco2_scores_final.json"
    meta_path = HERE / "tco2_metadata.json"
    tco2_scores = {k.lower(): v for k, v in json.loads(scores_path.read_text()).items()}
    tco2_metadata = {k.lower(): v for k, v in json.loads(meta_path.read_text()).items()}

    # ── Fetch or load NCT deposits ────────────────────────────────────
    nct_path = HERE / "nct_deposits.json"
    if nct_path.exists():
        print(f"\nFound cached NCT deposits at {nct_path}")
        nct_deposits = json.loads(nct_path.read_text())
        print(f"Loaded {len(nct_deposits)} NCT deposits from cache")
        sys.stdout.flush()
    else:
        # Fetch from chain
        nct_deposits = fetch_all_deposits(NCT_POOL, "NCT")
        # Enrich with sender addresses
        nct_deposits = enrich_with_senders(nct_deposits)
        # Save
        nct_path.write_text(json.dumps(nct_deposits, indent=2))
        print(f"Saved {len(nct_deposits)} NCT deposits to {nct_path}")
        sys.stdout.flush()

    # ── Load BCT deposits from existing enriched file ─────────────────
    bct_enriched_path = HERE / "bct_deposits_enriched.json"
    print(f"\nLoading BCT deposits from {bct_enriched_path.name}...")
    bct_deposits = json.loads(bct_enriched_path.read_text())
    print(f"Loaded {len(bct_deposits)} BCT deposits")
    sys.stdout.flush()

    # ── Score both pools ──────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("SCORING DEPOSITS")
    print(f"{'='*60}")
    print("\n--- NCT ---")
    nct_deposits = score_deposits(nct_deposits, tco2_scores, tco2_metadata)
    print("\n--- BCT ---")
    bct_deposits = score_deposits(bct_deposits, tco2_scores, tco2_metadata)

    # ── Run temporal analysis for both ────────────────────────────────
    nct_temporal = temporal_analysis(nct_deposits, "NCT")
    bct_temporal = temporal_analysis(bct_deposits, "BCT")

    # ── Print summaries ───────────────────────────────────────────────
    print_temporal_summary(bct_temporal, "BCT")
    print_temporal_summary(nct_temporal, "NCT")

    # ── Compute DiD ───────────────────────────────────────────────────
    did = compute_did(bct_temporal, nct_temporal)

    print(f"\n{'='*60}")
    print("DIFFERENCE-IN-DIFFERENCES (DiD)")
    print(f"{'='*60}")

    if "did_estimate" in did:
        print(f"\n  BCT change (early->late): {did['bct_change']:+.2f}")
        print(f"  NCT change (early->late): {did['nct_change']:+.2f}")
        print(f"  DiD estimate:             {did['did_estimate']:+.2f}")
        print(f"\n  {did['interpretation']}")

    if "quartile_did" in did:
        qd = did["quartile_did"]
        print(f"\n  Quartile-based DiD:")
        print(f"    BCT Q1->Q4: {qd['bct_Q1_Q4_change']:+.2f}")
        print(f"    NCT Q1->Q4: {qd['nct_Q1_Q4_change']:+.2f}")
        print(f"    DiD:        {qd['did_estimate']:+.2f}")

    if "spearman_comparison" in did:
        sc = did["spearman_comparison"]
        print(f"\n  Spearman rho comparison:")
        print(f"    BCT rho: {sc['bct_rho']:.4f} (p={sc['bct_p']:.2e})")
        print(f"    NCT rho: {sc['nct_rho']:.4f} (p={sc['nct_p']:.2e})")
        print(f"    Rho diff: {sc['rho_difference']:+.4f}")
        if "fisher_p" in sc:
            print(f"    Fisher z-test p: {sc['fisher_p']:.4f}")
            print(f"    {sc['fisher_interpretation']}")

    sys.stdout.flush()

    # ── Compile and save results ──────────────────────────────────────
    results = {
        "bct_temporal": bct_temporal,
        "nct_temporal": nct_temporal,
        "did": did,
        "summary": {
            "bct_deposits": len(bct_deposits),
            "nct_deposits": len(nct_deposits),
            "bct_scored": bct_temporal.get("n_deposits_scored", 0),
            "nct_scored": nct_temporal.get("n_deposits_scored", 0),
            "bct_spearman_rho": bct_temporal.get("spearman_rho"),
            "nct_spearman_rho": nct_temporal.get("spearman_rho"),
            "bct_mean_quality": bct_temporal.get("mean_quality"),
            "nct_mean_quality": nct_temporal.get("mean_quality"),
            "conclusion": "",
        },
    }

    # Generate conclusion
    bct_rho = bct_temporal.get("spearman_rho")
    nct_rho = nct_temporal.get("spearman_rho")
    if bct_rho is not None and nct_rho is not None:
        bct_sig = bct_temporal.get("spearman_p", 1) < 0.05
        nct_sig = nct_temporal.get("spearman_p", 1) < 0.05

        if bct_rho < -0.2 and bct_sig and (nct_rho > -0.2 or not nct_sig):
            results["summary"]["conclusion"] = (
                f"BCT shows significant temporal quality degradation "
                f"(rho={bct_rho:.3f}, p<0.05) while NCT does NOT "
                f"(rho={nct_rho:.3f}). "
                f"This confirms that BCT's permissionless deposit mechanism "
                f"drives adverse selection -- the quality decline is NOT "
                f"a supply-side phenomenon. "
                f"NCT's AFOLU filter + vintage requirement successfully "
                f"prevents the race-to-the-bottom dynamic."
            )
        elif bct_rho < -0.2 and nct_rho < -0.2:
            results["summary"]["conclusion"] = (
                f"Both BCT (rho={bct_rho:.3f}) and NCT (rho={nct_rho:.3f}) "
                f"show temporal degradation. However, the DiD analysis "
                f"isolates the EXCESS degradation attributable to BCT's "
                f"permissionless mechanism beyond supply-side trends."
            )
        else:
            results["summary"]["conclusion"] = (
                f"BCT rho={bct_rho:.3f}, NCT rho={nct_rho:.3f}. "
                f"Further analysis needed to disentangle pool-mechanism "
                f"from supply-side effects."
            )

    results_path = HERE / "nct_comparison_results.json"
    results_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nSaved comparison results to {results_path}")

    # ── Final summary ─────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("FINAL CONCLUSION")
    print(f"{'='*60}")
    print(f"\n  {results['summary']['conclusion']}")
    print()
    sys.stdout.flush()

    return results


if __name__ == "__main__":
    main()
