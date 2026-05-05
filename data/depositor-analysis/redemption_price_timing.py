#!/usr/bin/env python3
"""
Redemption-Price Timing Analysis
=================================
Test: Do high-quality credits get redeemed out of BCT when price drops?

Hypothesis (Gresham exit mechanism):
- When BCT price < OTC fair value of non-renewable credits, rational holders redeem
- Redemption of high-quality credits should cluster in price-decline periods
- If true: the exit margin of Gresham is price-responsive, not just a static composition effect

Outputs: redemption_price_timing_results.json
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats as sstats
from collections import defaultdict

HERE = Path(__file__).resolve().parent
CACHE_DIR = HERE / "transfer_cache"
BCT_POOL = "0x2f800db0fdb5223b3c3f354886d907a671414a7f"

# Block-to-date conversion (from event_study_results.json)
SEC_PER_BLOCK = 2.3  # approximate for Polygon
GENESIS_BLOCK = 20_000_000  # approx Oct 2021
GENESIS_TIMESTAMP = 1633132800  # 2021-10-02 UTC


def block_to_date(block: int) -> str:
    """Approximate block number to date string."""
    from datetime import datetime, timezone
    ts = GENESIS_TIMESTAMP + (block - GENESIS_BLOCK) * SEC_PER_BLOCK
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def load_price_data() -> dict:
    """Load BCT daily price data. Try multiple sources."""
    # Check if we have price data from the price_quality analysis
    price_file = HERE / "bct_daily_prices.json"
    if price_file.exists():
        return json.loads(price_file.read_text())

    # Try the price_quality_results for any embedded price series
    pq_file = HERE / "price_quality_results.json"
    if pq_file.exists():
        pq = json.loads(pq_file.read_text())
        if "daily_prices" in pq:
            return pq["daily_prices"]

    # Fallback: construct from what we know
    # BCT price trajectory: ~$7 (Oct 2021) → ~$1 (May 2022) → ~$0.50 (late 2022)
    # We'll use block-based price bins as a proxy
    return None


def load_redemptions_with_quality() -> list[dict]:
    """Load all redemption events with quality scores from transfer cache."""
    # Load scores
    scores_file = HERE / "tco2_scores_complete.json"
    scores = json.loads(scores_file.read_text())

    # Build TCO2 → score/type map (scores is a dict keyed by address)
    tco2_info = {}
    for addr, entry in scores.items():
        tco2_info[addr.lower()] = {
            "composite": entry.get("composite", entry.get("score")),
            "type": entry.get("type", entry.get("methodology_category", "Unknown")),
        }

    # Extract redemptions from transfer cache
    redemptions = []
    for cache_file in sorted(CACHE_DIR.glob("*.json")):
        tco2 = cache_file.stem.lower()
        info = tco2_info.get(tco2, {})
        if not info.get("composite"):
            continue

        try:
            cache = json.loads(cache_file.read_text())
        except Exception:
            continue

        for ev in cache.get("events", []):
            if ev.get("from", "").lower() == BCT_POOL:
                to = ev.get("to", "").lower()
                if to == "0x" + "0" * 40:
                    continue
                amount_wei = int(ev.get("value_wei", "0"))
                if amount_wei <= 0:
                    continue
                redemptions.append({
                    "tco2": tco2,
                    "block": ev["block"],
                    "date": block_to_date(ev["block"]),
                    "tonnes": amount_wei / 1e18,
                    "quality": info["composite"],
                    "type": info["type"],
                    "redeemer": to,
                })

    redemptions.sort(key=lambda r: r["block"])
    return redemptions


def analyze_redemption_timing(redemptions: list[dict]) -> dict:
    """Analyze temporal patterns in redemption quality."""
    if not redemptions:
        return {"error": "No redemptions loaded"}

    results = {}

    # --- 1. Split redemptions into temporal phases ---
    blocks = [r["block"] for r in redemptions]
    min_block, max_block = min(blocks), max(blocks)
    terra_block = 28_400_000  # May 2022
    ftx_block = 35_200_000   # Nov 2022

    phases = {
        "pre_terra": [r for r in redemptions if r["block"] < terra_block],
        "post_terra_pre_ftx": [r for r in redemptions if terra_block <= r["block"] < ftx_block],
        "post_ftx": [r for r in redemptions if r["block"] >= ftx_block],
    }

    results["phase_summary"] = {}
    for phase_name, phase_data in phases.items():
        if not phase_data:
            results["phase_summary"][phase_name] = {"n": 0}
            continue

        qualities = [r["quality"] for r in phase_data]
        tonnes = [r["tonnes"] for r in phase_data]
        weighted_q = np.average(qualities, weights=tonnes) if sum(tonnes) > 0 else 0

        type_tonnes = defaultdict(float)
        for r in phase_data:
            type_tonnes[r["type"]] += r["tonnes"]

        results["phase_summary"][phase_name] = {
            "n_events": len(phase_data),
            "total_tonnes": round(sum(tonnes), 1),
            "mean_quality_unweighted": round(float(np.mean(qualities)), 2),
            "mean_quality_weighted": round(float(weighted_q), 2),
            "composition_pct": {k: round(v / sum(tonnes) * 100, 1) for k, v in type_tonnes.items()},
        }

    # --- 2. Temporal correlation: do higher-quality redemptions come earlier? ---
    if len(redemptions) > 20:
        r_blocks = np.array([r["block"] for r in redemptions])
        r_quality = np.array([r["quality"] for r in redemptions])
        rho, p = sstats.spearmanr(r_blocks, r_quality)
        results["temporal_quality_correlation"] = {
            "spearman_rho": round(float(rho), 4),
            "spearman_p": float(p),
            "n": len(redemptions),
            "interpretation": "Negative = higher quality redeemed earlier (Gresham exit timing)"
        }

    # --- 3. Burst analysis: do redemptions cluster in time? ---
    # Look for redemption bursts (many events in short block range)
    block_diffs = np.diff(sorted(blocks))
    if len(block_diffs) > 10:
        results["burst_analysis"] = {
            "median_inter_redemption_blocks": int(np.median(block_diffs)),
            "mean_inter_redemption_blocks": int(np.mean(block_diffs)),
            "p10_blocks": int(np.percentile(block_diffs, 10)),
            "p90_blocks": int(np.percentile(block_diffs, 90)),
            "cv": round(float(np.std(block_diffs) / np.mean(block_diffs)), 3),
            "interpretation": "CV > 1 suggests clustered/bursty redemptions"
        }

    # --- 4. Per-type timing: when does each type get redeemed? ---
    type_timing = {}
    for ctype in set(r["type"] for r in redemptions):
        type_events = [r for r in redemptions if r["type"] == ctype]
        if len(type_events) >= 5:
            type_blocks = [r["block"] for r in type_events]
            type_timing[ctype] = {
                "n_events": len(type_events),
                "total_tonnes": round(sum(r["tonnes"] for r in type_events), 1),
                "median_block": int(np.median(type_blocks)),
                "first_block": min(type_blocks),
                "last_block": max(type_blocks),
                "first_date": block_to_date(min(type_blocks)),
                "last_date": block_to_date(max(type_blocks)),
                "span_days": round((max(type_blocks) - min(type_blocks)) * SEC_PER_BLOCK / 86400, 1),
            }

    results["per_type_timing"] = type_timing

    # --- 5. Redeemer concentration ---
    redeemer_tonnes = defaultdict(float)
    redeemer_quality = defaultdict(list)
    for r in redemptions:
        redeemer_tonnes[r["redeemer"]] += r["tonnes"]
        redeemer_quality[r["redeemer"]].append(r["quality"])

    n_redeemers = len(redeemer_tonnes)
    total_redeemed = sum(redeemer_tonnes.values())
    sorted_redeemers = sorted(redeemer_tonnes.items(), key=lambda x: -x[1])

    top10_tonnes = sum(t for _, t in sorted_redeemers[:10])
    results["redeemer_concentration"] = {
        "n_unique_redeemers": n_redeemers,
        "top10_share_pct": round(top10_tonnes / total_redeemed * 100, 1) if total_redeemed > 0 else 0,
        "gini": round(float(gini_coefficient([t for _, t in sorted_redeemers])), 3),
    }

    # --- 6. Cross-margin test: are depositors also redeemers? ---
    # Load deposit data to compare
    deposits_file = HERE / "bct_deposits_enriched.json"
    if deposits_file.exists():
        deposits = json.loads(deposits_file.read_text())
        depositor_addresses = set()
        for d in deposits:
            addr = d.get("depositor", d.get("from", "")).lower()
            if addr:
                depositor_addresses.add(addr)

        redeemer_addresses = set(redeemer_tonnes.keys())
        overlap = depositor_addresses & redeemer_addresses
        results["depositor_redeemer_overlap"] = {
            "n_depositors": len(depositor_addresses),
            "n_redeemers": len(redeemer_addresses),
            "n_overlap": len(overlap),
            "overlap_pct_of_redeemers": round(len(overlap) / len(redeemer_addresses) * 100, 1) if redeemer_addresses else 0,
            "interpretation": "High overlap suggests round-trip arbitrage; low overlap suggests different actors on each side"
        }

        # Quality comparison: overlapping vs non-overlapping redeemers
        overlap_qualities = []
        nonoverlap_qualities = []
        for addr, quals in redeemer_quality.items():
            mean_q = np.mean(quals)
            if addr in overlap:
                overlap_qualities.append(mean_q)
            else:
                nonoverlap_qualities.append(mean_q)

        if len(overlap_qualities) > 3 and len(nonoverlap_qualities) > 3:
            mw, mw_p = sstats.mannwhitneyu(overlap_qualities, nonoverlap_qualities, alternative="two-sided")
            results["depositor_redeemer_overlap"]["quality_comparison"] = {
                "overlap_mean_quality": round(float(np.mean(overlap_qualities)), 2),
                "nonoverlap_mean_quality": round(float(np.mean(nonoverlap_qualities)), 2),
                "mann_whitney_p": float(mw_p),
            }

    return results


def gini_coefficient(values: list) -> float:
    """Compute Gini coefficient."""
    arr = np.sort(np.array(values, dtype=float))
    n = len(arr)
    if n == 0 or arr.sum() == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return float((2 * np.sum(index * arr) - (n + 1) * np.sum(arr)) / (n * np.sum(arr)))


def main():
    print("=" * 60)
    print("REDEMPTION-PRICE TIMING ANALYSIS")
    print("=" * 60)

    print("\n1. Loading redemption events with quality scores...")
    redemptions = load_redemptions_with_quality()
    print(f"   Loaded {len(redemptions)} scored redemption events")

    if not redemptions:
        print("   ERROR: No redemptions found. Check transfer_cache.")
        return

    print(f"   Block range: {redemptions[0]['block']} - {redemptions[-1]['block']}")
    print(f"   Date range: {redemptions[0]['date']} - {redemptions[-1]['date']}")
    print(f"   Types: {set(r['type'] for r in redemptions)}")

    print("\n2. Analyzing temporal patterns...")
    results = analyze_redemption_timing(redemptions)

    # Print summary
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    if "temporal_quality_correlation" in results:
        tc = results["temporal_quality_correlation"]
        print(f"\n  Temporal quality correlation: ρ = {tc['spearman_rho']}, p = {tc['spearman_p']:.4g}")

    if "phase_summary" in results:
        print("\n  Phase breakdown:")
        for phase, data in results["phase_summary"].items():
            if data.get("n_events", 0) > 0:
                print(f"    {phase}: n={data['n_events']}, "
                      f"quality_weighted={data['mean_quality_weighted']}, "
                      f"tonnes={data['total_tonnes']:.0f}")

    if "redeemer_concentration" in results:
        rc = results["redeemer_concentration"]
        print(f"\n  Redeemer concentration: {rc['n_unique_redeemers']} unique, "
              f"top10={rc['top10_share_pct']}%, Gini={rc['gini']}")

    if "depositor_redeemer_overlap" in results:
        dro = results["depositor_redeemer_overlap"]
        print(f"\n  Depositor-redeemer overlap: {dro['n_overlap']}/{dro['n_redeemers']} "
              f"({dro['overlap_pct_of_redeemers']}%)")

    if "burst_analysis" in results:
        ba = results["burst_analysis"]
        print(f"\n  Redemption burstiness: CV={ba['cv']} "
              f"(median gap={ba['median_inter_redemption_blocks']} blocks)")

    # Save
    out_path = HERE / "redemption_price_timing_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n→ Saved to {out_path}")


if __name__ == "__main__":
    main()
