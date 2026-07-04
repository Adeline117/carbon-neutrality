#!/usr/bin/env python3
"""early_warning_framework_free.py -- framework-free variant of the early warning.

The Lemons Index early warning depends on the author-derived composite score.
This variant asks whether the SAME real-time trigger fires using only public
ledger data plus Verra credit-type labels: the cumulative renewable share of
deposited tonnage (renewables being the category with documented near-zero
additionality in independent literature, not in our framework).

Signal: R(t) = renewable tonnage deposited up to t / total tonnage up to t.
Danger threshold: R >= 0.50 (majority of pool tonnage in the near-zero-
additionality category). We report the first crossing date and the value at
trigger, for comparison with the Lemons Index trigger (2021-10-06, LI 0.711).

Depends on: bct_deposits_enriched.json (per-deposit tonnage, block, tco2) and
project type labels resolved the same way early_warning.py resolves them.
numpy only.
"""
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data" / "depositor-analysis"
DANGER_R = 0.50

B0, D0 = 20364343, date(2021, 10, 11)
B1, D1 = 36999866, date(2022, 12, 28)


def block_to_date(b):
    frac = (b - B0) / (B1 - B0)
    return D0 + timedelta(days=frac * (D1 - D0).days)


def load_types():
    """token address -> is_renewable, using the same classification data the
    composition analysis uses (Verra methodology categories)."""
    candidates = ["project_types.json", "tco2_scores_complete.json",
                  "bct_composition_complete.json"]
    for name in candidates:
        p = D / name
        if not p.exists():
            continue
        data = json.loads(p.read_text())
        # try common shapes
        if isinstance(data, dict):
            for key in ("tokens", "by_token", "scores"):
                if key in data and isinstance(data[key], dict):
                    data = data[key]
                    break
        if isinstance(data, dict):
            out = {}
            for k, v in data.items():
                if not isinstance(v, dict):
                    continue
                t = (v.get("type") or v.get("credit_type") or v.get("category")
                     or v.get("methodology_type") or "")
                if t:
                    out[k.lower()] = "renewable" in str(t).lower()
            if out:
                print(f"  types from {name}: {len(out)} tokens")
                return out
    raise SystemExit("no usable type mapping found")


def main():
    types = load_types()
    deposits = json.loads((D / "bct_deposits_enriched.json").read_text())
    rows = []
    for dep in deposits:
        tco2 = dep["tco2_address"].lower() if "tco2_address" in dep else dep.get("tco2", "").lower()
        if tco2 not in types:
            continue
        rows.append((dep["block_number"], dep["amount_tonnes"], types[tco2]))
    rows.sort()
    print(f"  {len(rows)} of {len(deposits)} deposits type-resolved")

    cum_total = cum_renew = 0.0
    trigger = None
    series_samples = []
    for i, (blk, tonnes, is_ren) in enumerate(rows):
        cum_total += tonnes
        if is_ren:
            cum_renew += tonnes
        share = cum_renew / cum_total
        if i % 100 == 0:
            series_samples.append({"block": blk, "date": str(block_to_date(blk)),
                                   "cum_renewable_share": round(share, 4)})
        # require a minimal burn-in so a single first deposit doesn't trigger
        if trigger is None and cum_total >= 100_000 and share >= DANGER_R:
            trigger = {"date": str(block_to_date(blk)), "block": blk,
                       "share_at_trigger": round(share, 4),
                       "cum_tonnes_at_trigger": round(cum_total)}
    final_share = cum_renew / cum_total

    # threshold-crossing analysis after trigger (whipsaw honesty check)
    ct2 = cr2 = 0.0
    crossings = []
    state = None
    for blk, tonnes, is_ren in rows:
        ct2 += tonnes
        if is_ren:
            cr2 += tonnes
        if ct2 < 100_000:
            continue
        cur = (cr2 / ct2) >= DANGER_R
        if state is None:
            state = cur
        elif cur != state:
            crossings.append({"date": str(block_to_date(blk)),
                              "direction": "above->below" if state else "below->above",
                              "cum_mt": round(ct2 / 1e6, 2)})
            state = cur
    stable_from = crossings[-1]["date"] if crossings and crossings[-1]["direction"] == "below->above" else (trigger or {}).get("date")

    out = {
        "signal": "cumulative renewable share of deposited tonnage (ledger + Verra type labels only)",
        "danger_threshold": DANGER_R,
        "burn_in_tonnes": 100_000,
        "trigger": trigger,
        "final_share": round(final_share, 4),
        "coverage": {"deposits_resolved": len(rows), "deposits_total": len(deposits)},
        "threshold_crossings_after_trigger": crossings,
        "stable_above_threshold_from": stable_from,
        "comparison": "Lemons Index trigger: 2021-10-06 at LI 0.711 (early_warning_results.json)",
        "series_samples": series_samples[:15],
    }
    (D / "early_warning_framework_free_results.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({k: out[k] for k in ("trigger", "final_share", "coverage")}, indent=1))


if __name__ == "__main__":
    main()
