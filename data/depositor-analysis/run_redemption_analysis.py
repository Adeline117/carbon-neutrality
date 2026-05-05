#!/usr/bin/env python3
"""BCT Redemption Analysis: identify TCO2 outflows from BCT pool = redemptions.

Redemptions are identified by:
1. BCT burns: Transfer(user -> 0x0) on the BCT token = BCT pool token burned
2. TCO2 outflows: Transfer(BCT_pool -> user) on TCO2 tokens = credits leaving pool

We use the existing transfer_cache data (already fetched for all 349 scored TCO2s)
to identify TCO2 outflows from the BCT pool address. This avoids additional RPC calls.
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats as sstats

HERE = Path(__file__).resolve().parent
CACHE_DIR = HERE / "transfer_cache"

BCT_POOL = "0x2f800db0fdb5223b3c3f354886d907a671414a7f"
BCT_START_BLOCK = 20_000_000
BCT_END_BLOCK = 37_000_000


def load_redemptions_from_transfer_cache(tco2_scores: dict) -> list[dict]:
    """Extract TCO2 outflows from BCT pool using cached Transfer events.

    A Transfer event where `from` == BCT_POOL on a TCO2 contract means
    that TCO2 was redeemed out of the pool.
    """
    redemptions = []
    tco2_list = sorted(tco2_scores.keys())
    n_loaded = 0

    for tco2 in tco2_list:
        cache_path = CACHE_DIR / f"{tco2}.json"
        if not cache_path.exists():
            continue

        try:
            cache = json.loads(cache_path.read_text())
        except Exception:
            continue

        events = cache.get("events", [])
        for ev in events:
            if ev.get("from", "").lower() == BCT_POOL:
                # This is a TCO2 leaving the pool = redemption
                to = ev.get("to", "").lower()
                if to == "0x" + "0" * 40:
                    continue  # Skip burns to zero
                amount_wei = int(ev.get("value_wei", "0"))
                if amount_wei <= 0:
                    continue
                redemptions.append({
                    "tco2_address": tco2,
                    "redeemer": to,
                    "amount_tonnes": amount_wei / 1e18,
                    "block_number": ev["block"],
                    "tx_hash": ev.get("tx_hash", ""),
                })

        n_loaded += 1

    # Also identify deposits: TCO2 flowing INTO the pool
    deposits_from_cache = []
    for tco2 in tco2_list:
        cache_path = CACHE_DIR / f"{tco2}.json"
        if not cache_path.exists():
            continue
        try:
            cache = json.loads(cache_path.read_text())
        except Exception:
            continue
        events = cache.get("events", [])
        for ev in events:
            if ev.get("to", "").lower() == BCT_POOL:
                frm = ev.get("from", "").lower()
                if frm == "0x" + "0" * 40:
                    continue
                amount_wei = int(ev.get("value_wei", "0"))
                if amount_wei <= 0:
                    continue
                deposits_from_cache.append({
                    "tco2_address": tco2,
                    "depositor": frm,
                    "amount_tonnes": amount_wei / 1e18,
                    "block_number": ev["block"],
                    "tx_hash": ev.get("tx_hash", ""),
                })

    redemptions.sort(key=lambda r: r["block_number"])
    deposits_from_cache.sort(key=lambda d: d["block_number"])

    print(f"  Loaded transfer caches for {n_loaded} TCO2s")
    print(f"  TCO2 outflows from pool (redemptions): {len(redemptions)}")
    print(f"  TCO2 inflows to pool (deposits): {len(deposits_from_cache)}")

    return redemptions, deposits_from_cache


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
            redeemed_qualities.append({
                "quality": quality, "tonnes": tonnes,
                "type": credit_type, "block": r["block_number"],
            })

    for d in deposits:
        tco2 = d["tco2_address"].lower()
        score_info = tco2_scores.get(tco2, {})
        quality = score_info.get("composite")
        credit_type = score_info.get("type", "Unknown")
        tonnes = d["amount_tonnes"]
        deposited_types[credit_type] += tonnes
        if quality is not None:
            deposited_qualities.append({
                "quality": quality, "tonnes": tonnes,
                "type": credit_type, "block": d["block_number"],
            })

    # ── Basic counts ──────────────────────────────────────────────────
    results = {
        "n_redemptions_total": len(redemptions),
        "n_redemptions_scored": len(redeemed_qualities),
        "n_deposits_total": len(deposits),
        "n_deposits_scored": len(deposited_qualities),
        "total_redeemed_tonnes": sum(r["amount_tonnes"] for r in redemptions),
        "total_deposited_tonnes": sum(d["amount_tonnes"] for d in deposits),
    }

    redeemed_q_arr = np.array([r["quality"] for r in redeemed_qualities])
    deposited_q_arr = np.array([d["quality"] for d in deposited_qualities])

    # ── Statistical tests ──────────────────────────────────────────────
    if len(redeemed_q_arr) > 5 and len(deposited_q_arr) > 5:
        # Mann-Whitney U: are redeemed credits higher quality?
        mw_stat, mw_p = sstats.mannwhitneyu(
            redeemed_q_arr, deposited_q_arr, alternative="greater"
        )
        results["mann_whitney_unweighted"] = {
            "statistic": float(mw_stat),
            "p_value_greater": float(mw_p),
            "interpretation": "H1: redeemed credits have higher quality than deposited",
            "mean_redeemed_quality": float(np.mean(redeemed_q_arr)),
            "mean_deposited_quality": float(np.mean(deposited_q_arr)),
            "median_redeemed_quality": float(np.median(redeemed_q_arr)),
            "median_deposited_quality": float(np.median(deposited_q_arr)),
            "sd_redeemed": float(np.std(redeemed_q_arr, ddof=1)),
            "sd_deposited": float(np.std(deposited_q_arr, ddof=1)),
            "n_redeemed": len(redeemed_q_arr),
            "n_deposited": len(deposited_q_arr),
        }

        # Two-sided
        mw2_stat, mw2_p = sstats.mannwhitneyu(
            redeemed_q_arr, deposited_q_arr, alternative="two-sided"
        )
        results["mann_whitney_two_sided_p"] = float(mw2_p)

        # Tonnage-weighted means
        def weighted_avg(items):
            total_t = sum(i["tonnes"] for i in items)
            if total_t == 0:
                return 0
            return sum(i["quality"] * i["tonnes"] for i in items) / total_t

        wtd_r = weighted_avg(redeemed_qualities)
        wtd_d = weighted_avg(deposited_qualities)
        results["tonnage_weighted"] = {
            "mean_redeemed_quality_weighted": float(wtd_r),
            "mean_deposited_quality_weighted": float(wtd_d),
            "quality_difference_weighted": float(wtd_r - wtd_d),
        }

        # Effect size
        pooled_std = np.sqrt(
            (np.var(redeemed_q_arr, ddof=1) + np.var(deposited_q_arr, ddof=1)) / 2
        )
        if pooled_std > 0:
            results["cohens_d"] = float(
                (np.mean(redeemed_q_arr) - np.mean(deposited_q_arr)) / pooled_std
            )

        # KS test
        ks_stat, ks_p = sstats.ks_2samp(redeemed_q_arr, deposited_q_arr)
        results["ks_test"] = {"statistic": float(ks_stat), "p_value": float(ks_p)}

        # Permutation test (10K)
        rng = np.random.default_rng(42)
        combined = np.concatenate([redeemed_q_arr, deposited_q_arr])
        n_r = len(redeemed_q_arr)
        obs_diff = np.mean(redeemed_q_arr) - np.mean(deposited_q_arr)
        n_perm = 10_000
        perm_diffs = np.zeros(n_perm)
        for i in range(n_perm):
            rng.shuffle(combined)
            perm_diffs[i] = np.mean(combined[:n_r]) - np.mean(combined[n_r:])
        perm_p = float(np.mean(perm_diffs >= obs_diff))
        results["permutation_test"] = {
            "observed_diff": float(obs_diff),
            "n_permutations": n_perm,
            "p_value_greater": perm_p,
            "null_mean": float(np.mean(perm_diffs)),
            "null_sd": float(np.std(perm_diffs)),
        }
    else:
        results["note"] = (
            f"Insufficient scored events for tests: "
            f"{len(redeemed_q_arr)} redeemed, {len(deposited_q_arr)} deposited"
        )

    # ── Type composition ──────────────────────────────────────────────
    total_redeemed = sum(redeemed_types.values())
    total_deposited = sum(deposited_types.values())

    if total_redeemed > 0 and total_deposited > 0:
        redeemed_pct = {k: v / total_redeemed * 100 for k, v in sorted(redeemed_types.items())}
        deposited_pct = {k: v / total_deposited * 100 for k, v in sorted(deposited_types.items())}
        results["redeemed_composition_tonnes"] = {k: round(v, 2) for k, v in sorted(redeemed_types.items())}
        results["deposited_composition_tonnes"] = {k: round(v, 2) for k, v in sorted(deposited_types.items())}
        results["redeemed_composition_pct"] = {k: round(v, 2) for k, v in redeemed_pct.items()}
        results["deposited_composition_pct"] = {k: round(v, 2) for k, v in deposited_pct.items()}

        ren_r = redeemed_pct.get("Renewable", 0)
        ren_d = deposited_pct.get("Renewable", 0)
        results["renewable_share"] = {
            "redeemed_pct": round(ren_r, 2),
            "deposited_pct": round(ren_d, 2),
            "ratio": round(ren_r / ren_d, 3) if ren_d > 0 else None,
            "interpretation": (
                "Higher renewable share in redemptions = good credits arbitraged out (Gresham)"
                if ren_r > ren_d
                else "Renewable credits NOT preferentially redeemed"
            ),
        }

    # ── Net composition dynamics ──────────────────────────────────────
    def block_to_month_idx(block):
        # Block 20M ~ Oct 2021, 2sec blocks, ~1.3M blocks/month
        return int((block - 20_000_000) * 2 / (86400 * 30))

    dep_by_month = defaultdict(lambda: defaultdict(float))
    red_by_month = defaultdict(lambda: defaultdict(float))

    for d in deposited_qualities:
        dep_by_month[block_to_month_idx(d["block"])][d["type"]] += d["tonnes"]
    for r in redeemed_qualities:
        red_by_month[block_to_month_idx(r["block"])][r["type"]] += r["tonnes"]

    all_months = sorted(set(list(dep_by_month.keys()) + list(red_by_month.keys())))
    all_types_set = sorted(set(list(deposited_types.keys()) + list(redeemed_types.keys())))

    cum_dep = defaultdict(float)
    cum_red = defaultdict(float)
    timeseries = []

    for m in all_months:
        for t in all_types_set:
            cum_dep[t] += dep_by_month.get(m, {}).get(t, 0)
            cum_red[t] += red_by_month.get(m, {}).get(t, 0)
        net = {t: cum_dep[t] - cum_red[t] for t in all_types_set}
        total_net = sum(max(0, v) for v in net.values())
        net_pct = {}
        if total_net > 0:
            net_pct = {t: round(max(0, net[t]) / total_net * 100, 2) for t in all_types_set}
        timeseries.append({
            "month_idx": m,
            "net_composition_pct": net_pct,
            "net_renewable_pct": net_pct.get("Renewable", 0),
            "cum_deposited_renewable_tonnes": round(cum_dep.get("Renewable", 0), 2),
            "cum_redeemed_renewable_tonnes": round(cum_red.get("Renewable", 0), 2),
            "cum_net_renewable_tonnes": round(cum_dep.get("Renewable", 0) - cum_red.get("Renewable", 0), 2),
        })

    # Save first/last few for the JSON
    results["net_composition_timeseries_endpoints"] = {
        "first_3": timeseries[:3] if len(timeseries) >= 3 else timeseries,
        "last_3": timeseries[-3:] if len(timeseries) >= 3 else timeseries,
        "n_months": len(timeseries),
    }

    if len(timeseries) > 4:
        half = len(timeseries) // 2
        first_ren = np.mean([t["net_renewable_pct"] for t in timeseries[:half]])
        second_ren = np.mean([t["net_renewable_pct"] for t in timeseries[half:]])
        results["net_renewable_drift"] = {
            "first_half_mean_net_renewable_pct": round(float(first_ren), 2),
            "second_half_mean_net_renewable_pct": round(float(second_ren), 2),
            "drift_pp": round(float(second_ren - first_ren), 2),
        }
        months_arr = np.arange(len(timeseries))
        ren_arr = np.array([t["net_renewable_pct"] for t in timeseries])
        if np.std(ren_arr) > 0:
            rho, p = sstats.spearmanr(months_arr, ren_arr)
            results["net_renewable_drift"]["spearman_rho"] = round(float(rho), 4)
            results["net_renewable_drift"]["spearman_p"] = float(p)

    # ── Redemption rate analysis ──────────────────────────────────────
    # Per-type: what fraction of deposited tonnes were subsequently redeemed?
    if total_deposited > 0 and total_redeemed > 0:
        type_redemption_rates = {}
        for t in all_types_set:
            dep_t = sum(v for k, v in deposited_types.items() if k == t)
            red_t = sum(v for k, v in redeemed_types.items() if k == t)
            if dep_t > 0:
                type_redemption_rates[t] = {
                    "deposited_tonnes": round(dep_t, 2),
                    "redeemed_tonnes": round(red_t, 2),
                    "redemption_rate_pct": round(red_t / dep_t * 100, 2),
                }
        results["redemption_rate_by_type"] = type_redemption_rates

        # Chi-squared test: does redemption rate differ by type?
        if len(type_redemption_rates) >= 2:
            # Use binary: renewable vs non-renewable
            ren_dep = deposited_types.get("Renewable", 0)
            ren_red = redeemed_types.get("Renewable", 0)
            nonren_dep = sum(v for k, v in deposited_types.items() if k != "Renewable")
            nonren_red = sum(v for k, v in redeemed_types.items() if k != "Renewable")

            # Contingency table: [[ren_red, ren_retained], [nonren_red, nonren_retained]]
            ren_retained = ren_dep - ren_red
            nonren_retained = nonren_dep - nonren_red
            if ren_retained >= 0 and nonren_retained >= 0:
                table = np.array([
                    [max(0, ren_red), max(0, ren_retained)],
                    [max(0, nonren_red), max(0, nonren_retained)],
                ])
                if table.min() >= 0 and table.sum() > 0:
                    chi2, chi2_p, dof, expected = sstats.chi2_contingency(table)
                    results["chi2_renewable_redemption"] = {
                        "chi2": float(chi2),
                        "p_value": float(chi2_p),
                        "dof": int(dof),
                        "contingency_table": table.tolist(),
                        "interpretation": (
                            "Renewable credits redeemed at different rate than non-renewable"
                            if chi2_p < 0.05 else
                            "No significant difference in redemption rate by type"
                        ),
                    }

    return results


def main():
    print("=" * 70)
    print("BCT REDEMPTION ANALYSIS (from transfer cache)")
    print("=" * 70)
    sys.stdout.flush()

    # Load data
    deposits_orig = json.loads((HERE / "bct_deposits_enriched.json").read_text())
    tco2_scores = {
        k.lower(): v
        for k, v in json.loads((HERE / "tco2_scores_complete.json").read_text()).items()
    }

    print(f"Loaded {len(deposits_orig)} deposit events, {len(tco2_scores)} TCO2 scores")
    print(f"Transfer cache dir: {CACHE_DIR}")
    sys.stdout.flush()

    # Load redemptions from transfer cache
    print("\nExtracting redemptions from transfer cache...")
    redemptions, deposits_cache = load_redemptions_from_transfer_cache(tco2_scores)

    # Use the cache-derived deposits for consistency (same TCO2 universe)
    print(f"\nUsing {len(deposits_cache)} cache-derived deposits and {len(redemptions)} redemptions")

    # Also compare with the original deposits
    print(f"Original deposit events: {len(deposits_orig)}")
    print(f"Cache-derived deposit events: {len(deposits_cache)}")
    print(f"Total redeemed tonnes: {sum(r['amount_tonnes'] for r in redemptions):,.0f}")
    print(f"Total deposited tonnes (cache): {sum(d['amount_tonnes'] for d in deposits_cache):,.0f}")
    sys.stdout.flush()

    # Run analysis
    print("\nAnalyzing redemption quality distributions...")
    results = analyze_redemptions(redemptions, deposits_cache, tco2_scores)

    # Save
    out_path = HERE / "redemption_analysis.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"Saved to {out_path.name}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Redemptions: {results['n_redemptions_total']} events ({results['n_redemptions_scored']} scored)")
    print(f"Deposits: {results['n_deposits_total']} events ({results['n_deposits_scored']} scored)")
    print(f"Total redeemed tonnes: {results['total_redeemed_tonnes']:,.0f}")
    print(f"Total deposited tonnes: {results['total_deposited_tonnes']:,.0f}")

    if "mann_whitney_unweighted" in results:
        mw = results["mann_whitney_unweighted"]
        print(f"\nMann-Whitney (H1: redeemed quality > deposited quality):")
        print(f"  Mean redeemed quality:  {mw['mean_redeemed_quality']:.2f} +/- {mw['sd_redeemed']:.2f}")
        print(f"  Mean deposited quality: {mw['mean_deposited_quality']:.2f} +/- {mw['sd_deposited']:.2f}")
        print(f"  p (greater):            {mw['p_value_greater']:.4e}")
        print(f"  n_redeemed={mw['n_redeemed']}, n_deposited={mw['n_deposited']}")

    if "tonnage_weighted" in results:
        tw = results["tonnage_weighted"]
        print(f"\nTonnage-weighted quality:")
        print(f"  Redeemed:  {tw['mean_redeemed_quality_weighted']:.2f}")
        print(f"  Deposited: {tw['mean_deposited_quality_weighted']:.2f}")
        print(f"  Diff:      {tw['quality_difference_weighted']:+.2f}")

    if "cohens_d" in results:
        print(f"  Cohen's d: {results['cohens_d']:.3f}")

    if "permutation_test" in results:
        pt = results["permutation_test"]
        print(f"\nPermutation test (10K):")
        print(f"  Observed diff: {pt['observed_diff']:.3f}")
        print(f"  p (greater):   {pt['p_value_greater']:.4f}")

    if "renewable_share" in results:
        rs = results["renewable_share"]
        print(f"\nRenewable share:")
        print(f"  Redeemed:  {rs['redeemed_pct']:.1f}%")
        print(f"  Deposited: {rs['deposited_pct']:.1f}%")
        if rs.get("ratio"):
            print(f"  Ratio:     {rs['ratio']:.3f}x")

    if "redemption_rate_by_type" in results:
        print(f"\nRedemption rates by type:")
        for t, info in sorted(results["redemption_rate_by_type"].items(),
                               key=lambda x: -x[1].get("redemption_rate_pct", 0)):
            print(f"  {t}: {info['redemption_rate_pct']:.1f}% "
                  f"({info['redeemed_tonnes']:,.0f} / {info['deposited_tonnes']:,.0f} t)")

    if "chi2_renewable_redemption" in results:
        chi2 = results["chi2_renewable_redemption"]
        print(f"\nChi-squared (renewable vs non-renewable redemption rate):")
        print(f"  chi2={chi2['chi2']:.2f}, p={chi2['p_value']:.4e}")

    if "net_renewable_drift" in results:
        nrd = results["net_renewable_drift"]
        print(f"\nNet pool renewable drift:")
        print(f"  First half:  {nrd['first_half_mean_net_renewable_pct']:.1f}%")
        print(f"  Second half: {nrd['second_half_mean_net_renewable_pct']:.1f}%")
        print(f"  Drift:       {nrd['drift_pp']:+.1f}pp")
        if nrd.get("spearman_rho") is not None:
            print(f"  Spearman rho: {nrd['spearman_rho']:.3f} (p={nrd['spearman_p']:.4e})")


if __name__ == "__main__":
    main()
