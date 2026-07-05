#!/usr/bin/env python3
"""quality_gate_real.py -- quality-gate counterfactual on the REAL BCT deposit stream.

Supersedes counterfactual_simulation.py for the paper's gating claim: that
script evaluates grade floors on stylized pool compositions hardcoded in
data/lemons-index/pool_analyzer.py, not on BCT's actual deposits. This script
applies each grade floor to the real tonnage-weighted deposit stream
(bct_deposits_enriched.json x tco2_scores_complete.json, the same inputs as
the composition analysis) and reports, per floor:

- gated Lemons Index (1 - tonnage-weighted mean composite / 100) of admitted
  deposits, vs the real ungated baseline;
- admitted share of tonnage (the cost of the gate: how much volume a floor
  excludes).

Grade thresholds match the manuscript: BBB >= 45, BB >= 30, B < 30
(composite 0-100).
"""
import json
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "depositor-analysis"
OUT = Path(__file__).resolve().parent / "quality_gate_real_results.json"
FLOORS = {"B (no gate)": 0, "BB": 30, "BBB": 45, "A": 60, "AA": 75}


def load_scores():
    s = json.loads((D / "tco2_scores_complete.json").read_text())
    for key in ("tokens", "by_token", "scores"):
        if key in s and isinstance(s[key], dict):
            s = s[key]
            break
    out = {}
    for k, v in s.items():
        c = v.get("composite") or v.get("composite_score") or v.get("score")
        if c is not None:
            out[k.lower()] = float(c)
    return out


def main():
    scores = load_scores()
    deposits = json.loads((D / "bct_deposits_enriched.json").read_text())
    rows = [(scores[d["tco2_address"].lower()], d["amount_tonnes"])
            for d in deposits if d["tco2_address"].lower() in scores]
    total_t = sum(t for _, t in rows)
    baseline_li = 1 - sum(c * t for c, t in rows) / total_t / 100

    results = {}
    for name, floor in FLOORS.items():
        adm = [(c, t) for c, t in rows if c >= floor]
        t_adm = sum(t for _, t in adm)
        li = 1 - sum(c * t for c, t in adm) / t_adm / 100 if t_adm else None
        results[name] = {
            "floor_composite": floor,
            "gated_lemons_index": round(li, 3) if li is not None else None,
            "li_reduction_absolute": round(baseline_li - li, 3) if li is not None else None,
            "li_reduction_relative_pct": round(100 * (baseline_li - li) / baseline_li, 1) if li is not None else None,
            "admitted_tonnage_share_pct": round(100 * t_adm / total_t, 1),
        }

    out = {
        "method": "grade floors applied to the real tonnage-weighted BCT deposit stream "
                  "(bct_deposits_enriched x tco2_scores_complete); supersedes the stylized "
                  "counterfactual_simulation.py for the paper's gating claim",
        "deposits_scored": len(rows),
        "deposits_total": len(deposits),
        "baseline_lemons_index": round(baseline_li, 3),
        "floors": results,
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
