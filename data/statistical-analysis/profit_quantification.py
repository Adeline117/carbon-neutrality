#!/usr/bin/env python3
"""profit_quantification.py -- profit bounds for top-5 redeemers (scripted).

Supersedes the previously hand-recorded profit_quantification.json by
computing the same quantity reproducibly from the transfer cache and the
documented price assumptions (Methods): contemporaneous off-chain price
ranges per credit type (Ecosystem Marketplace / Carbon Pulse, 2021-2022)
minus BCT redemption cost (pool price + selective-redemption fee, $1-5/t).

Scenarios: low = (type price low - cost high), mid = midpoints,
high = (type price high - cost low); negatives floored at zero per type.
"""
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = HERE.parent / "depositor-analysis"
BCT = "0x2f800db0fdb5223b3c3f354886d907a671414a7f"

# $/tonne assumption ranges as documented in Methods / Supplementary
PRICE = {"Industrial gas": (3, 12), "REDD+": (4, 15), "IFM": (5, 18),
         "ARR": (6, 20), "Renewable": (0.30, 1.50)}
COST = (1, 5)


def token_types():
    s = json.loads((D / "tco2_scores_complete.json").read_text())
    for key in ("tokens", "by_token", "scores"):
        if key in s and isinstance(s[key], dict):
            s = s[key]
            break
    out = {}
    for k, v in s.items():
        t = str(v.get("type") or "")
        if "renewable" in t.lower():
            t = "Renewable"
        out[k.lower()] = t
    return out


def main():
    types = token_types()
    red = defaultdict(lambda: defaultdict(float))  # wallet -> type -> tonnes
    for f in (D / "transfer_cache").glob("*.json"):
        data = json.loads(f.read_text())
        t = types.get(f.stem.lower(), "")
        for e in data.get("events", []):
            if e["from"].lower() == BCT:
                red[e["to"].lower()][t] += int(e["value_wei"]) / 1e18
    top5 = sorted(red.items(), key=lambda kv: -sum(kv[1].values()))[:5]

    def profit(tonnes_by_type, scenario):
        total = 0.0
        for t, tn in tonnes_by_type.items():
            if t not in PRICE:
                continue
            lo, hi = PRICE[t]
            if scenario == "low":
                margin = lo - COST[1]
            elif scenario == "high":
                margin = hi - COST[0]
            else:
                margin = (lo + hi) / 2 - sum(COST) / 2
            total += max(0.0, margin) * tn
        return total

    wallets = []
    agg = {"low": 0.0, "mid": 0.0, "high": 0.0}
    for w, tt in top5:
        row = {"wallet": w[:10] + "...", "tonnes": round(sum(tt.values()), 1),
               "dominant_type": max(tt, key=tt.get)}
        for s in agg:
            v = profit(tt, s)
            row[f"profit_{s}_usd"] = round(v)
            agg[s] += v
        wallets.append(row)

    out = {
        "method": "top-5 redeemer tonnage by type (transfer_cache) x documented price "
                  "assumption ranges minus BCT redemption cost; scenario bounds",
        "assumptions": {"offchain_price_usd_per_t": PRICE, "bct_cost_usd_per_t": COST},
        "top_5_wallets": wallets,
        "aggregate": {f"profit_{s}_usd": round(v) for s, v in agg.items()},
        "note": "Upper bound: includes retirement-routed volume (the largest wallet is a "
                "retirement contract). Gas and slippage excluded.",
        "supersedes": "hand-recorded profit_quantification.json",
    }
    (HERE / "profit_quantification_results.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({k: out[k] for k in ("aggregate",)}, indent=1))
    for w in wallets:
        print(w)


if __name__ == "__main__":
    main()
