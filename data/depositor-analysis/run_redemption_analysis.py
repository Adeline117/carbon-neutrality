#!/usr/bin/env python3
"""BCT Redemption Analysis: fetch Redeemed events and compare quality distributions.

Part 1 of the Nature Comms adverse selection evidence:
If high-quality credits deposited into BCT were quickly redeemed (arbitraged out),
this is direct evidence of Gresham dynamics.
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
import requests
from scipy import stats as sstats

HERE = Path(__file__).resolve().parent

# ── RPC config ──────────────────────────────────────────────────────────────

RPC_URL = "https://polygon.drpc.org"
CHUNK_BLOCKS = 1000
MAX_WORKERS = 20
REQUEST_TIMEOUT = 30
RETRY_SLEEP = 1.0
MAX_RETRIES = 5

BCT_POOL = "0x2F800Db0fdb5223b3C3f354886d907A671414A7F".lower()
BCT_START_BLOCK = 20_000_000
BCT_END_BLOCK = 37_000_000

# Precomputed keccak256("Redeemed(address,address,uint256)")
REDEEMED_TOPIC = "0x27d4634c833b7622a0acddbf7f746183625f105945e95c723ad1d5a9f2a0b6fc"


def _rpc(method: str, params: list, session: requests.Session | None = None) -> Any:
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


def _fetch_chunk(from_block: int, to_block: int, session: requests.Session) -> list[dict]:
    """Fetch Redeemed logs for one chunk."""
    logs = _rpc("eth_getLogs", [{
        "address": BCT_POOL,
        "fromBlock": hex(from_block),
        "toBlock": hex(to_block),
        "topics": [REDEEMED_TOPIC],
    }], session=session)

    results = []
    for log in logs:
        topics = log.get("topics", [])
        if len(topics) < 3:
            continue
        sender = "0x" + topics[1][-40:].lower()
        tco2_address = "0x" + topics[2][-40:].lower()
        data_hex = log.get("data", "0x")
        try:
            amount_wei = int(data_hex, 16) if data_hex != "0x" else 0
        except ValueError:
            amount_wei = 0

        block_num = int(log["blockNumber"], 16) if isinstance(log["blockNumber"], str) else log["blockNumber"]

        results.append({
            "sender": sender,
            "tco2_address": tco2_address,
            "amount_wei": str(amount_wei),
            "amount_tonnes": amount_wei / 1e18,
            "block_number": block_num,
            "tx_hash": log["transactionHash"],
        })
    return results


def fetch_redeemed_events(from_block: int, to_block: int) -> list[dict]:
    """Fetch all BCT Redeemed events using concurrent chunk fetching."""
    print(f"Fetching BCT Redeemed events from block {from_block} to {to_block}...")
    print(f"  Topic: {REDEEMED_TOPIC}")

    # Build chunk list
    chunks = []
    b = from_block
    while b <= to_block:
        chunks.append((b, min(b + CHUNK_BLOCKS - 1, to_block)))
        b += CHUNK_BLOCKS

    print(f"  Total chunks: {len(chunks)}")

    sess = requests.Session()
    all_results: dict[int, list[dict]] = {}
    done = 0
    t0 = time.time()

    def worker(idx: int, frm: int, to: int) -> tuple[int, list[dict]]:
        return idx, _fetch_chunk(frm, to, sess)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(worker, i, frm, to): (i, frm, to)
                for i, (frm, to) in enumerate(chunks)}
        for fut in as_completed(futs):
            try:
                idx, events = fut.result()
            except Exception as e:
                idx, frm, to = futs[fut]
                print(f"  Chunk {idx} [{frm}-{to}] FAILED: {e}")
                # Retry once
                try:
                    time.sleep(1)
                    events = _fetch_chunk(frm, to, sess)
                except Exception as e2:
                    print(f"  Chunk {idx} FAILED again: {e2}; skipping")
                    events = []
            all_results[idx] = events
            done += 1
            if done % 1000 == 0:
                dt = time.time() - t0
                rate = done / max(dt, 1e-9)
                total_events = sum(len(v) for v in all_results.values())
                print(f"  {done}/{len(chunks)} chunks ({rate:.0f}/s), {total_events} events so far")

    # Merge in order
    redemptions = []
    for i in range(len(chunks)):
        redemptions.extend(all_results.get(i, []))

    # Sort by block
    redemptions.sort(key=lambda r: r["block_number"])

    print(f"  Total BCT redemptions found: {len(redemptions)}")
    print(f"  Total time: {time.time() - t0:.1f}s")
    return redemptions


def analyze_redemptions(
    redemptions: list[dict],
    deposits: list[dict],
    tco2_scores: dict[str, dict],
) -> dict:
    """Compare quality distributions of redeemed vs deposited credits."""

    redeemed_qualities = []
    redeemed_types = defaultdict(float)
    deposited_qualities = []
    deposited_types = defaultdict(float)

    for r in redemptions:
        tco2 = r["tco2_address"].lower()
        score_info = tco2_scores.get(tco2, {})
        quality = score_info.get("composite")
        credit_type = score_info.get("type", "Unknown")
        tonnes = r["amount_tonnes"]
        redeemed_types[credit_type] += tonnes
        if quality is not None:
            redeemed_qualities.append({"quality": quality, "tonnes": tonnes, "type": credit_type, "block": r["block_number"]})

    for d in deposits:
        tco2 = d["tco2_address"].lower()
        score_info = tco2_scores.get(tco2, {})
        quality = score_info.get("composite")
        credit_type = score_info.get("type", "Unknown")
        tonnes = d["amount_tonnes"]
        deposited_types[credit_type] += tonnes
        if quality is not None:
            deposited_qualities.append({"quality": quality, "tonnes": tonnes, "type": credit_type, "block": d["block_number"]})

    # ── Statistical tests ──────────────────────────────────────────────
    redeemed_q_arr = np.array([r["quality"] for r in redeemed_qualities])
    deposited_q_arr = np.array([d["quality"] for d in deposited_qualities])

    results = {
        "n_redemptions_total": len(redemptions),
        "n_redemptions_scored": len(redeemed_qualities),
        "n_deposits_total": len(deposits),
        "n_deposits_scored": len(deposited_qualities),
        "total_redeemed_tonnes": sum(r["amount_tonnes"] for r in redemptions),
        "total_deposited_tonnes": sum(d["amount_tonnes"] for d in deposits),
    }

    if len(redeemed_q_arr) > 0 and len(deposited_q_arr) > 0:
        # Mann-Whitney U: are redeemed credits higher quality than deposited?
        mw_stat, mw_p = sstats.mannwhitneyu(redeemed_q_arr, deposited_q_arr, alternative="greater")
        results["mann_whitney_unweighted"] = {
            "statistic": float(mw_stat),
            "p_value_greater": float(mw_p),
            "interpretation": "H1: redeemed credits have higher quality than deposited",
            "mean_redeemed_quality": float(np.mean(redeemed_q_arr)),
            "mean_deposited_quality": float(np.mean(deposited_q_arr)),
            "median_redeemed_quality": float(np.median(redeemed_q_arr)),
            "median_deposited_quality": float(np.median(deposited_q_arr)),
            "n_redeemed": len(redeemed_q_arr),
            "n_deposited": len(deposited_q_arr),
        }

        # Also test two-sided
        mw_stat2, mw_p2 = sstats.mannwhitneyu(redeemed_q_arr, deposited_q_arr, alternative="two-sided")
        results["mann_whitney_two_sided"] = {
            "statistic": float(mw_stat2),
            "p_value": float(mw_p2),
        }

        # Tonnage-weighted comparison
        def weighted_avg(items):
            total_t = sum(i["tonnes"] for i in items)
            if total_t == 0:
                return 0
            return sum(i["quality"] * i["tonnes"] for i in items) / total_t

        results["tonnage_weighted"] = {
            "mean_redeemed_quality_weighted": weighted_avg(redeemed_qualities),
            "mean_deposited_quality_weighted": weighted_avg(deposited_qualities),
            "quality_difference": weighted_avg(redeemed_qualities) - weighted_avg(deposited_qualities),
        }

        # Effect size
        pooled_std = np.sqrt((np.var(redeemed_q_arr, ddof=1) + np.var(deposited_q_arr, ddof=1)) / 2)
        if pooled_std > 0:
            results["cohens_d"] = float((np.mean(redeemed_q_arr) - np.mean(deposited_q_arr)) / pooled_std)

        # KS test
        ks_stat, ks_p = sstats.ks_2samp(redeemed_q_arr, deposited_q_arr)
        results["ks_test"] = {"statistic": float(ks_stat), "p_value": float(ks_p)}

    elif len(redeemed_q_arr) == 0:
        results["note_redeemed"] = "No scored redemptions found -- likely the Redeemed topic did not match any events."

    # Type composition
    total_redeemed = sum(redeemed_types.values())
    total_deposited = sum(deposited_types.values())

    if total_redeemed > 0 and total_deposited > 0:
        redeemed_pct = {k: v / total_redeemed * 100 for k, v in redeemed_types.items()}
        deposited_pct = {k: v / total_deposited * 100 for k, v in deposited_types.items()}
        results["redeemed_composition_tonnes"] = dict(redeemed_types)
        results["deposited_composition_tonnes"] = dict(deposited_types)
        results["redeemed_composition_pct"] = redeemed_pct
        results["deposited_composition_pct"] = deposited_pct

        ren_r = redeemed_pct.get("Renewable", 0)
        ren_d = deposited_pct.get("Renewable", 0)
        results["renewable_share"] = {
            "redeemed_pct": ren_r,
            "deposited_pct": ren_d,
            "ratio": ren_r / ren_d if ren_d > 0 else None,
            "interpretation": (
                "Higher renewable share in redemptions = good credits arbitraged out (Gresham)"
                if ren_r > ren_d
                else "Renewable credits NOT preferentially redeemed"
            ),
        }

    # Net composition dynamics (monthly bins)
    def block_to_month_idx(block):
        return int((block - 20_000_000) * 2 / (86400 * 30))

    dep_by_month = defaultdict(lambda: defaultdict(float))
    red_by_month = defaultdict(lambda: defaultdict(float))
    for d in deposited_qualities:
        dep_by_month[block_to_month_idx(d["block"])][d["type"]] += d["tonnes"]
    for r in redeemed_qualities:
        red_by_month[block_to_month_idx(r["block"])][r["type"]] += r["tonnes"]

    all_months = sorted(set(list(dep_by_month.keys()) + list(red_by_month.keys())))
    all_types_set = set(list(deposited_types.keys()) + list(redeemed_types.keys()))

    cum_dep = defaultdict(float)
    cum_red = defaultdict(float)
    timeseries = []

    for m in all_months:
        for t in all_types_set:
            cum_dep[t] += dep_by_month.get(m, {}).get(t, 0)
            cum_red[t] += red_by_month.get(m, {}).get(t, 0)
        net = {t: cum_dep[t] - cum_red[t] for t in all_types_set}
        total_net = sum(max(0, v) for v in net.values())
        net_pct = {t: max(0, net[t]) / total_net * 100 for t in all_types_set} if total_net > 0 else {}
        timeseries.append({
            "month_idx": m,
            "net_composition_pct": net_pct,
            "net_renewable_pct": net_pct.get("Renewable", 0),
        })

    results["net_composition_timeseries_sample"] = timeseries[:3] + timeseries[-3:] if len(timeseries) > 6 else timeseries

    if len(timeseries) > 2:
        half = len(timeseries) // 2
        first_ren = np.mean([t["net_renewable_pct"] for t in timeseries[:half]])
        second_ren = np.mean([t["net_renewable_pct"] for t in timeseries[half:]])
        results["net_renewable_drift"] = {
            "first_half_mean_renewable_pct": float(first_ren),
            "second_half_mean_renewable_pct": float(second_ren),
            "drift_pp": float(second_ren - first_ren),
            "spearman_rho": None,
            "spearman_p": None,
        }
        # Spearman correlation of month vs net renewable %
        months_arr = np.arange(len(timeseries))
        ren_arr = np.array([t["net_renewable_pct"] for t in timeseries])
        if len(ren_arr) > 3 and np.std(ren_arr) > 0:
            rho, p = sstats.spearmanr(months_arr, ren_arr)
            results["net_renewable_drift"]["spearman_rho"] = float(rho)
            results["net_renewable_drift"]["spearman_p"] = float(p)

    return results


def main():
    print("=" * 70)
    print("BCT REDEMPTION ANALYSIS")
    print("=" * 70)
    sys.stdout.flush()

    deposits = json.loads((HERE / "bct_deposits_enriched.json").read_text())
    tco2_scores = {k.lower(): v for k, v in json.loads((HERE / "tco2_scores_complete.json").read_text()).items()}
    print(f"Loaded {len(deposits)} deposits, {len(tco2_scores)} TCO2 scores")
    sys.stdout.flush()

    cache_path = HERE / "bct_redemptions_raw.json"
    if cache_path.exists():
        print(f"Loading cached redemptions from {cache_path.name}...")
        redemptions = json.loads(cache_path.read_text())
        print(f"  Cached: {len(redemptions)} redemptions")
    else:
        redemptions = fetch_redeemed_events(BCT_START_BLOCK, BCT_END_BLOCK)
        cache_path.write_text(json.dumps(redemptions, indent=2))
        print(f"  Cached to {cache_path.name}")
    sys.stdout.flush()

    print("\nAnalyzing redemption quality distributions...")
    results = analyze_redemptions(redemptions, deposits, tco2_scores)

    out_path = HERE / "redemption_analysis.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"Saved to {out_path.name}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Redemptions: {results['n_redemptions_total']} ({results['n_redemptions_scored']} scored)")
    print(f"Total redeemed tonnes: {results['total_redeemed_tonnes']:,.0f}")

    if "mann_whitney_unweighted" in results:
        mw = results["mann_whitney_unweighted"]
        print(f"\nMann-Whitney (redeemed > deposited quality):")
        print(f"  Mean redeemed:  {mw['mean_redeemed_quality']:.2f}")
        print(f"  Mean deposited: {mw['mean_deposited_quality']:.2f}")
        print(f"  p (greater):    {mw['p_value_greater']:.4e}")

    if "renewable_share" in results:
        rs = results["renewable_share"]
        print(f"\nRenewable share:")
        print(f"  Redeemed:  {rs['redeemed_pct']:.1f}%")
        print(f"  Deposited: {rs['deposited_pct']:.1f}%")

    if "net_renewable_drift" in results:
        nrd = results["net_renewable_drift"]
        print(f"\nNet renewable drift:")
        print(f"  First half:  {nrd['first_half_mean_renewable_pct']:.1f}%")
        print(f"  Second half: {nrd['second_half_mean_renewable_pct']:.1f}%")
        print(f"  Drift:       {nrd['drift_pp']:+.1f}pp")
        if nrd.get("spearman_rho") is not None:
            print(f"  Spearman rho: {nrd['spearman_rho']:.3f} (p={nrd['spearman_p']:.4e})")

    if "note_redeemed" in results:
        print(f"\nWARNING: {results['note_redeemed']}")


if __name__ == "__main__":
    main()
