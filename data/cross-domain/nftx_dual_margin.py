#!/usr/bin/env python3
"""nftx_dual_margin.py -- quantitative BCT-isomorphic tests on NFTX vaults.

Inputs: nftx_raw/<SYM>.json (events, from fetch_nftx_events.py) and
nftx_raw/sales_<SYM>.json (per-tokenId sale panel, from fetch_nft_sales.py).

Three tests per vault, mirroring the BCT pipeline:
1. Value heterogeneity under uniform pricing: dispersion of sale prices
   within the collection (P90/P10 ratio) -- every vault token redeems for
   "one item" regardless of which item.
2. Value-selective redemption (the BCT redemption-asymmetry analogue):
   each minted/redeemed tokenId is assigned the price PERCENTILE of its
   nearest-in-block sale within a +/-200k-block rolling window of collection
   sales (percentiles control for market-level price drift, which would
   otherwise confound early-mint/late-redeem timing). Mann-Whitney U on
   redeemed vs minted percentiles; report coverage (share of event tokens
   with an observable sale) because unsold tokens are unobservable.
3. Dual-margin account separation (account-level, same discipline as BCT):
   minter/redeemer wallet overlap from vault ERC-20 mint/burn transfers.
   Addresses appearing in >5% of a side's events are flagged as likely
   routers/zaps and the overlap is reported both raw and router-excluded.

Output: nftx_dual_margin_results.json. scipy for Mann-Whitney.
"""
import json
from bisect import bisect_left, bisect_right
from collections import Counter
from pathlib import Path

from scipy.stats import mannwhitneyu, wilcoxon

HERE = Path(__file__).resolve().parent
RAW = HERE / "nftx_raw"
WINDOW = 200_000  # blocks, ~1 month
ROUTER_SHARE = 0.05


def percentile_of(sales_sorted, blocks, prices, token_sales, ev_block):
    """token value = percentile of its nearest-in-block sale within the window."""
    if not token_sales:
        return None
    sale_block, sale_price = min(token_sales, key=lambda s: abs(s[0] - ev_block))
    lo = bisect_left(blocks, sale_block - WINDOW)
    hi = bisect_right(blocks, sale_block + WINDOW)
    window_prices = prices[lo:hi]
    if len(window_prices) < 20:
        return None
    rank = sum(1 for p in window_prices if p <= sale_price)
    return rank / len(window_prices)


def analyse_vault(sym):
    ev = json.loads((RAW / f"{sym}.json").read_text())
    sales = json.loads((RAW / f"sales_{sym}.json").read_text())["sales"]
    sales = [s for s in sales if s["price_eth"] > 0 and s.get("block")]
    sales.sort(key=lambda s: int(s["block"]))
    blocks = [int(s["block"]) for s in sales]
    prices = [s["price_eth"] for s in sales]
    by_token = {}
    for s in sales:
        by_token.setdefault(str(s["tokenId"]), []).append((int(s["block"]), s["price_eth"]))

    # 1. heterogeneity
    ps = sorted(prices)
    n = len(ps)
    p10, p50, p90 = ps[n // 10], ps[n // 2], ps[(9 * n) // 10]
    heterogeneity = {"n_sales": n, "p10_eth": round(p10, 4), "median_eth": round(p50, 4),
                     "p90_eth": round(p90, 4), "p90_p10_ratio": round(p90 / p10, 2) if p10 else None}

    # 2. value-selective redemption
    def event_percentiles(events):
        vals, covered, total = [], 0, 0
        for e in events:
            for tid in e["nft_ids"]:
                total += 1
                v = percentile_of(sales, blocks, prices, by_token.get(str(tid), []), e["block"])
                if v is not None:
                    covered += 1
                    vals.append(v)
        return vals, covered, total

    red_vals, red_cov, red_tot = event_percentiles(ev["redeemed_events"])
    min_vals, min_cov, min_tot = event_percentiles(ev["minted_events"])

    # robustness: strict matching (sale within WINDOW blocks of the event)
    def strict_minted_stats():
        vals = []
        for e in ev["minted_events"]:
            for tid in e["nft_ids"]:
                cand = [t for t in by_token.get(str(tid), []) if abs(t[0] - e["block"]) <= WINDOW]
                if not cand:
                    continue
                sb, sp = min(cand, key=lambda t: abs(t[0] - e["block"]))
                lo = bisect_left(blocks, sb - WINDOW)
                hi = bisect_right(blocks, sb + WINDOW)
                w = prices[lo:hi]
                if len(w) >= 20:
                    vals.append(sum(1 for pr in w if pr <= sp) / len(w))
        if len(vals) < 20:
            return None
        vals.sort()
        _, wp = wilcoxon([v - 0.5 for v in vals], alternative="less")
        return {"n": len(vals), "median_pctile": round(vals[len(vals) // 2], 3),
                "wilcoxon_p": float(f"{wp:.3g}")}
    strict = strict_minted_stats()
    if red_vals and min_vals:
        u, p = mannwhitneyu(red_vals, min_vals, alternative="greater")
        med_r = sorted(red_vals)[len(red_vals) // 2]
        med_m = sorted(min_vals)[len(min_vals) // 2]
        w_stat, w_p = wilcoxon([v - 0.5 for v in min_vals], alternative="less")
        mv = sorted(min_vals)
        dep_iqr = mv[(3 * len(mv)) // 4] - mv[len(mv) // 4]
        selectivity = {"redeemed_n": len(red_vals), "minted_n": len(min_vals),
                       "minted_below_collection_median_p": float(f"{w_p:.3g}"),
                       "deposited_pctile_iqr": round(dep_iqr, 3),
                       "strict_matching_robustness": strict,
                       "redeemed_median_pctile": round(med_r, 3),
                       "minted_median_pctile": round(med_m, 3),
                       "gap_pp": round(100 * (med_r - med_m), 1),
                       "mannwhitney_p_greater": float(f"{p:.3g}"),
                       "coverage_redeemed": round(red_cov / red_tot, 3) if red_tot else None,
                       "coverage_minted": round(min_cov / min_tot, 3) if min_tot else None}
    else:
        selectivity = None

    # 3. dual-margin wallets
    minters = Counter(t["wallet"] for t in ev["erc20_mints"])
    redeemers = Counter(t["wallet"] for t in ev["erc20_burns"])

    def routers(cnt, total):
        return {w for w, c in cnt.items() if c / total > ROUTER_SHARE}

    r_m = routers(minters, sum(minters.values()))
    r_r = routers(redeemers, sum(redeemers.values()))
    m_set, r_set = set(minters), set(redeemers)
    m2, rd2 = m_set - r_m - r_r, r_set - r_m - r_r
    overlap_raw = len(m_set & r_set)
    overlap_ex = len(m2 & rd2)
    dual_margin = {
        "minter_wallets": len(m_set), "redeemer_wallets": len(r_set),
        "overlap_raw": overlap_raw,
        "overlap_raw_pct_of_redeemers": round(100 * overlap_raw / len(r_set), 1),
        "likely_routers_flagged": sorted(r_m | r_r),
        "minter_wallets_ex_routers": len(m2), "redeemer_wallets_ex_routers": len(rd2),
        "overlap_ex_routers": overlap_ex,
        "overlap_ex_pct_of_redeemers": round(100 * overlap_ex / len(rd2), 1) if rd2 else None,
        "redeemer_to_minter_ratio": round(len(rd2) / len(m2), 2) if m2 else None,
    }
    FEES = {"MILADY": (1.0, 1.0, 2.0), "PHUNK": (5.0, 2.0, 3.0), "WIZARD": (5.0, 2.0, 3.0),
            "MEEB": (5.0, 2.0, 3.0), "MANA": (15.0, 2.0, 8.0), "BGAN": (5.0, 2.0, 3.0)}
    fee = FEES.get(sym)
    fees = ({"mint_pct": fee[0], "random_redeem_pct": fee[1], "target_redeem_pct": fee[2],
             "exit_selection_priced": fee[2] > fee[1],
             "source": "on-chain view calls (mintFee/randomRedeemFee/targetRedeemFee), 2026-07-03"}
            if fee else None)
    return {"heterogeneity": heterogeneity, "value_selectivity": selectivity,
            "dual_margin": dual_margin, "fees": fees}


def main():
    vaults = [p.stem for p in RAW.glob("*.json")
              if not p.stem.startswith("sales_") and (RAW / f"sales_{p.stem}.json").exists()]
    out = {"window_blocks": WINDOW, "router_share_threshold": ROUTER_SHARE, "vaults": {}}
    for sym in sorted(vaults):
        print(f"analysing {sym}")
        out["vaults"][sym] = analyse_vault(sym)
    sel = [(s, v["value_selectivity"]) for s, v in out["vaults"].items() if v["value_selectivity"]]
    pos = [s for s, x in sel if x["gap_pp"] > 0]
    sig = [s for s, x in sel if x["gap_pp"] > 0 and x["mannwhitney_p_greater"] < 0.05]
    entry_below = [s2 for s2, x in sel if x["minted_median_pctile"] < 0.5]
    entry_sig = [s2 for s2, x in sel if x["minted_below_collection_median_p"] < 0.05]
    out["summary"] = {
        "vaults_analysed": len(out["vaults"]),
        "vaults_with_value_panel": len(sel),
        "entry_side_selection": {
            "vaults_minted_below_collection_median": entry_below,
            "unanimous": len(entry_below) == len(sel),
            "cross_vault_sign_test_p_one_sided": round(0.5 ** len(sel), 4) if len(entry_below) == len(sel) else None,
            "per_vault_wilcoxon_sig": entry_sig,
        },
        "exit_side_extraction": {
            "positive_direction": pos,
            "significant_at_5pct": sig,
            "present": bool(sig),
        },
        "verdict": ("entry-margin lemons selection replicates in all vaults; "
                    "exit-margin extraction absent (consistent with NFTX pricing targeted "
                    "redemption above random redemption in all six vaults)"
                    if len(entry_below) == len(sel) and not sig else "mixed"),
    }
    (HERE / "nftx_dual_margin_results.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out["summary"], indent=1))


if __name__ == "__main__":
    main()
