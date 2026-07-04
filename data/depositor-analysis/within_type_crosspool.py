#!/usr/bin/env python3
"""within_type_crosspool.py -- does the quality screen select WITHIN credit type?

The cross-pool design->quality gradient is definitional if screens act only on
credit type (our composite is type-driven, so type-screened pools must score
higher). The sharper question: holding credit type fixed, do screened pools
hold higher-quality credits than unscreened pools? We compare tonnage-weighted
mean composite of NCT (nature-screened) vs BCT (unscreened) deposits within
each nature-based type. Near-zero within-type differences mean the screen acts
on type composition only, making the gradient a measured (not merely conceded)
definitional quantity -- and confirming the validity of the within-token
matched-pair design (credits in both pools are quality-identical within type).
"""
import json
from collections import defaultdict
from pathlib import Path

D = Path(__file__).resolve().parent


def load_scores():
    s = json.loads((D / "tco2_scores_complete.json").read_text())
    for key in ("tokens", "by_token", "scores"):
        if key in s and isinstance(s[key], dict):
            s = s[key]
            break
    return s


def pool_stats(deps_file, scores):
    agg = defaultdict(lambda: [0.0, 0.0])
    toks = defaultdict(set)
    for d in json.loads((D / deps_file).read_text()):
        v = scores.get(d["tco2_address"].lower())
        if not v:
            continue
        t = str(v.get("type") or v.get("credit_type") or v.get("category")
                or v.get("methodology_type") or "")
        c = v.get("composite") or v.get("composite_score") or v.get("score")
        if c is None:
            continue
        agg[t][0] += d["amount_tonnes"]
        agg[t][1] += d["amount_tonnes"] * float(c)
        toks[t].add(d["tco2_address"].lower())
    return {t: {"wmean": round(v[1] / v[0], 2), "tonnes": round(v[0]),
                "n_tokens": len(toks[t])}
            for t, v in agg.items() if v[0] > 0}


def main():
    scores = load_scores()
    bct = pool_stats("bct_deposits_enriched.json", scores)
    nct = pool_stats("nct_deposits.json", scores)
    rows = {}
    for t in sorted(set(nct) & set(bct)):
        rows[t] = {"bct": bct[t], "nct": nct[t],
                   "delta_nct_minus_bct": round(nct[t]["wmean"] - bct[t]["wmean"], 2)}
    max_abs = max(abs(r["delta_nct_minus_bct"]) for r in rows.values())
    out = {
        "question": "does the nature screen select higher-quality credits WITHIN type?",
        "method": "tonnage-weighted mean composite of deposits, per type, BCT vs NCT",
        "by_type": rows,
        "max_abs_within_type_delta": max_abs,
        "conclusion": ("screen acts on type composition only; within-type quality is "
                       "near-identical across pools" if max_abs < 1.0 else
                       "screen selects within type"),
    }
    (D / "within_type_crosspool_results.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
