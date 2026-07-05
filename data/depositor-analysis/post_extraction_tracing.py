#!/usr/bin/env python3
"""post_extraction_tracing.py -- destination of each redeemed credit (scripted).

Supersedes the previously hand-recorded post_extraction_tracing.json in
data/statistical-analysis/ by computing the same quantity reproducibly.

For each redemption (BCT pool -> wallet transfer of a TCO2 token) by a top-20
redeemer, find that wallet's next outbound transfer of the same token and
classify the destination:
  retirement  -- burn address (0x0 / 0xdead)
  nct_pool    -- Toucan NCT pool (cross-pool deposit)
  bct_pool    -- re-deposit into BCT
  other       -- any other address (secondary-market sale or OTC)
  held        -- no subsequent outbound transfer in the cache
Tonnage-weighted shares over all traced redemptions. Immediate next hop only.
"""
import json
from collections import defaultdict
from pathlib import Path

D = Path(__file__).resolve().parent
BCT = "0x2f800db0fdb5223b3c3f354886d907a671414a7f"
NCT = "0xd838290e877e0188a4a44700463419ed96c16107"
BURNS = {"0x0000000000000000000000000000000000000000",
         "0x000000000000000000000000000000000000dead"}


def main():
    # events per token, sorted
    caches = {}
    redeemed = defaultdict(float)
    for f in sorted((D / "transfer_cache").glob("*.json")):
        data = json.loads(f.read_text())
        evs = sorted(data.get("events", []), key=lambda e: (e["block"], e.get("log_index", 0)))
        caches[f.stem.lower()] = evs
        for e in evs:
            if e["from"].lower() == BCT:
                redeemed[e["to"].lower()] += int(e["value_wei"]) / 1e18
    top20 = {w for w, _ in sorted(redeemed.items(), key=lambda kv: -kv[1])[:20]}

    shares = defaultdict(float)
    n_traced = 0
    for tok, evs in caches.items():
        for i, e in enumerate(evs):
            if e["from"].lower() != BCT or e["to"].lower() not in top20:
                continue
            wallet = e["to"].lower()
            tonnes = int(e["value_wei"]) / 1e18
            n_traced += 1
            nxt = next((x for x in evs[i + 1:] if x["from"].lower() == wallet), None)
            if nxt is None:
                dest = "held"
            else:
                to = nxt["to"].lower()
                dest = ("retirement" if to in BURNS else
                        "nct_pool" if to == NCT else
                        "bct_pool" if to == BCT else "other")
            shares[dest] += tonnes

    total = sum(shares.values())
    out = {
        "method": "immediate next outbound transfer of the same TCO2 token from each "
                  "top-20 redeemer wallet after each BCT redemption; tonnage-weighted",
        "n_redemptions_traced": n_traced,
        "total_tonnes_traced": round(total),
        "destination_shares_pct": {k: round(100 * v / total, 1) for k, v in
                                   sorted(shares.items(), key=lambda kv: -kv[1])},
        "supersedes": "data/statistical-analysis/post_extraction_tracing.json (hand-recorded)",
    }
    (D / "post_extraction_tracing_results.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
