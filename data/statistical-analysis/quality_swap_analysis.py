#!/usr/bin/env python3
"""Quality Swap Forensics: Do overlap wallets systematically extract quality?

For each wallet that both deposited into AND redeemed from BCT:
  - What was the mean quality of what they deposited?
  - What was the mean quality of what they redeemed?
  - quality_swap = redeemed_quality - deposited_quality

Also profiles top 20 redeemers: which types did each wallet extract?

Usage:
    python3 quality_swap_analysis.py
"""

import json
import os
import math
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CACHE_DIR = ROOT / "data" / "depositor-analysis" / "transfer_cache"
SCORES_FILE = ROOT / "data" / "depositor-analysis" / "tco2_scores_complete.json"

BCT_POOL = "0x2f800db0fdb5223b3c3f354886d907a671414a7f"


def main():
    # Load quality scores
    with open(SCORES_FILE) as f:
        scores = json.load(f)

    # Normalize addresses to lowercase
    scores_lower = {k.lower(): v for k, v in scores.items()}

    # Extract all deposits and redemptions from transfer cache
    # deposit: wallet → BCT pool (to = BCT)
    # redeem: BCT pool → wallet (from = BCT)

    wallet_deposits = defaultdict(list)   # wallet → [(token_addr, tonnes, block, quality, type)]
    wallet_redeems = defaultdict(list)    # wallet → [(token_addr, tonnes, block, quality, type)]

    cache_files = list(CACHE_DIR.glob("*.json"))
    print(f"Processing {len(cache_files)} transfer cache files...")

    for cf in cache_files:
        token_addr = cf.stem.lower()
        token_info = scores_lower.get(token_addr, {})
        quality = token_info.get("composite", None)
        credit_type = token_info.get("type", "Unknown")

        if quality is None:
            continue

        with open(cf) as f:
            data = json.load(f)

        events = data.get("events", []) if isinstance(data, dict) else data
        for evt in events:
            from_addr = evt.get("from", "").lower()
            to_addr = evt.get("to", "").lower()
            value_wei = evt.get("value_wei", evt.get("value", "0"))
            tonnes = float(value_wei) / 1e18
            block = evt.get("block", 0)

            if tonnes <= 0:
                continue

            if to_addr == BCT_POOL:
                # Deposit: from_addr is the depositor
                wallet_deposits[from_addr].append((token_addr, tonnes, block, quality, credit_type))
            elif from_addr == BCT_POOL:
                # Redemption: to_addr is the redeemer
                wallet_redeems[to_addr].append((token_addr, tonnes, block, quality, credit_type))

    all_depositors = set(wallet_deposits.keys())
    all_redeemers = set(wallet_redeems.keys())
    overlap_wallets = all_depositors & all_redeemers

    print(f"\nUnique depositors: {len(all_depositors)}")
    print(f"Unique redeemers: {len(all_redeemers)}")
    print(f"Overlap wallets: {len(overlap_wallets)}")
    print(f"Overlap %: {len(overlap_wallets)/len(all_redeemers)*100:.1f}% of redeemers")

    # === RESULT A: QUALITY SWAP ===
    swap_results = []
    for wallet in overlap_wallets:
        deps = wallet_deposits[wallet]
        reds = wallet_redeems[wallet]

        dep_tonnes = sum(t for _, t, _, _, _ in deps)
        red_tonnes = sum(t for _, t, _, _, _ in reds)

        if dep_tonnes == 0 or red_tonnes == 0:
            continue

        dep_quality = sum(t * q for _, t, _, q, _ in deps) / dep_tonnes
        red_quality = sum(t * q for _, t, _, q, _ in reds) / red_tonnes

        dep_types = defaultdict(float)
        red_types = defaultdict(float)
        for _, t, _, _, tp in deps:
            dep_types[tp] += t
        for _, t, _, _, tp in reds:
            red_types[tp] += t

        swap_results.append({
            "wallet": wallet[:10] + "...",
            "deposited_tonnes": round(dep_tonnes, 1),
            "redeemed_tonnes": round(red_tonnes, 1),
            "deposited_quality": round(dep_quality, 2),
            "redeemed_quality": round(red_quality, 2),
            "quality_swap": round(red_quality - dep_quality, 2),
            "deposited_types": {k: round(v, 1) for k, v in sorted(dep_types.items(), key=lambda x: -x[1])},
            "redeemed_types": {k: round(v, 1) for k, v in sorted(red_types.items(), key=lambda x: -x[1])},
        })

    swap_results.sort(key=lambda x: -abs(x["quality_swap"]))

    positive_swaps = [s for s in swap_results if s["quality_swap"] > 0]
    negative_swaps = [s for s in swap_results if s["quality_swap"] < 0]
    zero_swaps = [s for s in swap_results if s["quality_swap"] == 0]

    mean_swap = sum(s["quality_swap"] for s in swap_results) / len(swap_results) if swap_results else 0

    # Tonnage-weighted mean swap
    total_swap_tonnes = sum(min(s["deposited_tonnes"], s["redeemed_tonnes"]) for s in swap_results)
    weighted_swap = sum(
        s["quality_swap"] * min(s["deposited_tonnes"], s["redeemed_tonnes"])
        for s in swap_results
    ) / total_swap_tonnes if total_swap_tonnes > 0 else 0

    # === RESULT B: TOP REDEEMER PROFILING ===
    redeemer_profiles = []
    for wallet in sorted(all_redeemers, key=lambda w: -sum(t for _, t, _, _, _ in wallet_redeems[w]))[:20]:
        reds = wallet_redeems[wallet]
        total_tonnes = sum(t for _, t, _, _, _ in reds)
        mean_quality = sum(t * q for _, t, _, q, _ in reds) / total_tonnes if total_tonnes > 0 else 0

        types_redeemed = defaultdict(float)
        for _, t, _, _, tp in reds:
            types_redeemed[tp] += t

        blocks = [b for _, _, b, _, _ in reds]
        n_events = len(reds)
        block_span = max(blocks) - min(blocks) if len(blocks) > 1 else 0

        is_depositor = wallet in all_depositors
        dep_quality = 0
        if is_depositor:
            deps = wallet_deposits[wallet]
            dep_t = sum(t for _, t, _, _, _ in deps)
            dep_quality = sum(t * q for _, t, _, q, _ in deps) / dep_t if dep_t > 0 else 0

        redeemer_profiles.append({
            "wallet": wallet[:10] + "...",
            "wallet_full": wallet,
            "redeemed_tonnes": round(total_tonnes, 1),
            "mean_quality_redeemed": round(mean_quality, 2),
            "n_redemption_events": n_events,
            "block_span": block_span,
            "types_redeemed": {k: round(v, 1) for k, v in sorted(types_redeemed.items(), key=lambda x: -x[1])},
            "dominant_type": max(types_redeemed, key=types_redeemed.get),
            "is_also_depositor": is_depositor,
            "deposited_quality": round(dep_quality, 2) if is_depositor else None,
            "quality_swap": round(mean_quality - dep_quality, 2) if is_depositor else None,
        })

    # === COMPILE RESULTS ===
    results = {
        "quality_swap_analysis": {
            "n_overlap_wallets": len(overlap_wallets),
            "n_with_both_activity": len(swap_results),
            "overlap_pct_of_redeemers": round(len(overlap_wallets) / len(all_redeemers) * 100, 2),
            "positive_swaps": len(positive_swaps),
            "negative_swaps": len(negative_swaps),
            "zero_swaps": len(zero_swaps),
            "mean_quality_swap": round(mean_swap, 2),
            "tonnage_weighted_swap": round(weighted_swap, 2),
            "interpretation": "",
            "top_10_swaps": swap_results[:10],
        },
        "redeemer_profiles": {
            "n_unique_redeemers": len(all_redeemers),
            "top_20": redeemer_profiles,
        },
        "depositor_summary": {
            "n_unique_depositors": len(all_depositors),
            "total_deposited_tonnes": round(sum(sum(t for _, t, _, _, _ in deps) for deps in wallet_deposits.values()), 1),
            "total_redeemed_tonnes": round(sum(sum(t for _, t, _, _, _ in reds) for reds in wallet_redeems.values()), 1),
        }
    }

    # Verdict
    if mean_swap > 0 and len(positive_swaps) > len(negative_swaps):
        results["quality_swap_analysis"]["interpretation"] = (
            f"QUALITY EXTRACTION CONFIRMED. {len(positive_swaps)} of {len(swap_results)} overlap wallets "
            f"redeemed higher quality than they deposited (mean swap: +{mean_swap:.1f} points, "
            f"tonnage-weighted: +{weighted_swap:.1f}). These wallets systematically extracted quality from BCT."
        )
    elif mean_swap < 0:
        results["quality_swap_analysis"]["interpretation"] = (
            f"REVERSE PATTERN. Overlap wallets deposited higher quality than they redeemed "
            f"(mean swap: {mean_swap:.1f} points). This contradicts quality extraction hypothesis."
        )
    else:
        results["quality_swap_analysis"]["interpretation"] = (
            f"MIXED PATTERN. Mean swap: {mean_swap:.1f}, positive: {len(positive_swaps)}, "
            f"negative: {len(negative_swaps)}."
        )

    out = HERE / "quality_swap_results.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print(f"\n{'='*70}")
    print("QUALITY SWAP ANALYSIS")
    print(f"{'='*70}")
    print(f"Overlap wallets with activity: {len(swap_results)}")
    print(f"Positive swap (redeem > deposit quality): {len(positive_swaps)}")
    print(f"Negative swap: {len(negative_swaps)}")
    print(f"Zero swap: {len(zero_swaps)}")
    print(f"Mean quality swap: {mean_swap:+.2f}")
    print(f"Tonnage-weighted swap: {weighted_swap:+.2f}")
    print(f"\n{results['quality_swap_analysis']['interpretation']}")

    print(f"\n{'='*70}")
    print("TOP 20 REDEEMERS")
    print(f"{'='*70}")
    print(f"{'Wallet':<14} {'Tonnes':>12} {'MeanQ':>8} {'Events':>8} {'Dominant Type':<16} {'Also Dep?':>10} {'Swap':>8}")
    print("-" * 80)
    for p in redeemer_profiles:
        swap_str = f"{p['quality_swap']:+.1f}" if p['quality_swap'] is not None else "N/A"
        dep_str = "YES" if p['is_also_depositor'] else "no"
        print(f"{p['wallet']:<14} {p['redeemed_tonnes']:>12,.0f} {p['mean_quality_redeemed']:>8.1f} {p['n_redemption_events']:>8} {p['dominant_type']:<16} {dep_str:>10} {swap_str:>8}")

    print(f"\nWrote: {out}")


if __name__ == "__main__":
    main()
