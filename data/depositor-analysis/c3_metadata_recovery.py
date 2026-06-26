#!/usr/bin/env python3
"""
c3_metadata_recovery.py — recover C3 per-token metadata on-chain and compute its
temporal-quality slope (the signal the first multipool pass reported as
"not recoverable").

Finding: C3's tokenized credits (C3T) encode the Verra project id and vintage in
their ERC-20 symbol, exactly like Toucan's TCO2 (e.g. "C3T-VCS-1140-2015").
We read symbol() via `cast call` against a public Polygon node, parse
project+vintage, type each project by overlap with our existing classification,
score by type-mean composite, and compute the Spearman slope of quality vs
deposit block order.

Coverage (honest): 22/26 C3T tokens resolve a symbol; 12/18 projects type via
classification overlap; 52/92 deposits scored. Result: rho = -0.277 (p = 0.047),
same direction and low band as BCT — a second, independent operator.

Requires: foundry `cast` on PATH + a public Polygon RPC. Outputs
c3_token_metadata.json and c3_temporal_recovered.json. Re-run to refresh.
"""
from __future__ import annotations
import json, re, subprocess
import numpy as np
from scipy import stats
from pathlib import Path
from collections import defaultdict

D = Path(__file__).resolve().parent
RPC = "https://polygon-bor-rpc.publicnode.com"


def recover_symbols(contracts):
    meta = {}
    for a in contracts:
        try:
            sym = subprocess.run(["cast", "call", a, "symbol()(string)", "--rpc-url", RPC],
                                 capture_output=True, text=True, timeout=20).stdout.strip().strip('"')
            m = re.search(r"VCS-(\d+)-(\d{4})", sym)
            meta[a] = ({"symbol": sym, "project_id": m.group(1), "vintage": int(m.group(2))}
                       if m else {"symbol": sym, "project_id": None, "vintage": None})
        except Exception as e:
            meta[a] = {"symbol": None, "error": str(e)[:40]}
    return meta


def main():
    ev = json.load(open(D / "alternative_pool_events.json"))
    cls = json.load(open(D / "project_classification_final.json"))
    deps = [(r["c3t_contract"].lower(), r["block_number"])
            for k in ("ubo_deposits", "nbo_deposits") for r in ev.get(k, [])]
    contracts = sorted({a for a, _ in deps})

    meta = recover_symbols(contracts)
    json.dump({"contracts": meta, "n": len(contracts)},
              open(D / "c3_token_metadata.json", "w"), indent=1)

    # type-mean composite from BCT scored tokens
    scores = json.load(open(D / "tco2_scores_complete.json"))
    sc = {}
    it = scores.items() if isinstance(scores, dict) else ((r.get("tco2_address"), r) for r in scores)
    for k, v in it:
        c = v.get("composite") or v.get("composite_score")
        if c is not None:
            sc[str(k).lower()] = float(c)
    md = json.load(open(D / "tco2_metadata_fixed.json"))
    tc = defaultdict(list)
    rec = md.items() if isinstance(md, dict) else ((None, r) for r in md)
    for addr, r in rec:
        t = (cls.get(str(r.get("project_id"))) or {}).get("type")
        a = str(addr).lower() if addr else None
        if t and a in sc:
            tc[t].append(sc[a])
    type_mean = {t: float(np.mean(v)) for t, v in tc.items()}

    tok = {a.lower(): type_mean[(cls.get(str(m["project_id"])) or {}).get("type")]
           for a, m in meta.items()
           if m.get("project_id") and (cls.get(str(m["project_id"])) or {}).get("type") in type_mean}
    stream = sorted((b, tok[a]) for a, b in deps if a in tok)
    blocks = np.array([b for b, _ in stream]); comps = np.array([c for _, c in stream])
    rho, p = stats.spearmanr(blocks, comps)
    q = np.array_split(comps[np.argsort(blocks)], 4)
    out = {"n_scored_deposits": len(stream), "temporal_rho": round(float(rho), 4),
           "temporal_p": float(p), "q1_q4_decline": round(float(np.mean(q[0]) - np.mean(q[-1])), 2),
           "mean_composite": round(float(np.mean(comps)), 2),
           "coverage": f"{sum(1 for v in meta.values() if v.get('vintage'))}/{len(contracts)} tokens, "
                       f"{len(stream)}/92 deposits scored"}
    json.dump(out, open(D / "c3_temporal_recovered.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
