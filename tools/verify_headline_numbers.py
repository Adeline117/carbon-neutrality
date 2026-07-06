#!/usr/bin/env python3
"""verify_headline_numbers.py -- assert every headline number in the manuscript
against the canonical results manifest and cached analysis outputs.
Exit 0 = all consistent.

Run from the repo root:  python3 tools/verify_headline_numbers.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAIL = []


def check(name, actual, expected, tol=0.0):
    ok = (abs(float(actual) - float(expected)) <= tol) if isinstance(expected, (int, float)) \
        else (actual == expected)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {actual}  (manuscript: {expected})")
    if not ok:
        FAIL.append(name)


def main():
    print("Headline-number verification\n")
    manifest = json.loads((ROOT / "results" / "manifest.json").read_text())

    def mval(section, key):
        return manifest[section][key]["value"]

    # Manuscript headline numbers <- canonical manifest (each entry carries its
    # own source-file provenance, checked by tools/living-paper/fill_manifest.py)
    check("renewable share (69.1%)", mval("composition", "renewable_pct_tonnes"), 69.1, 0.05)
    check("within-token gap (+73.9 pp)", mval("within_token", "boot_gap_mean_pp"), 73.9, 0.05)

    comp = json.loads((ROOT / "data/depositor-analysis/bct_composition_complete.json").read_text())
    check("renewable share, raw composition file", comp["by_type"]["Renewable"]["pct"], 69.1, 0.05)
    check("total deposits (1,187)", comp["total_deposits"], 1187)
    check("total tonnage (~22.0 Mt)", round(comp["total_tonnes"] / 1e6, 1), 22.0, 0.05)

    gr = json.loads((ROOT / "data/statistical-analysis/quality_gate_real_results.json").read_text())
    check("gating baseline, real deposit stream (0.689)", gr["baseline_lemons_index"], 0.689, 0.0005)
    check("BBB gate endpoint (0.506)", gr["floors"]["BBB"]["gated_lemons_index"], 0.506, 0.0005)
    check("BBB gate admitted tonnage (7.2%)", gr["floors"]["BBB"]["admitted_tonnage_share_pct"], 7.2, 0.05)

    ew = json.loads((ROOT / "data/depositor-analysis/early_warning_results.json").read_text())
    check("early-warning LI at trigger (0.71)", round(ew["li_at_trigger"], 2), 0.71, 0.005)
    check("early-warning lead (~7 months)", round(ew["lead_time_months"]), 7)
    check("launch-window mean price ($5.66)", ew["peak_price_usd"], 5.66, 0.005)

    pr = json.loads((ROOT / "data/depositor-analysis/bct_prices_daily.json").read_text())
    check("price series committed (1,493 daily points)", len(pr), 1493)
    pq = json.loads((ROOT / "data/depositor-analysis/price_quality_results.json").read_text())
    check("price-score correlation (+0.77)", round(pq["price_vs_cum_pqd"]["pearson_r"], 2), 0.77, 0.005)
    check("first-diff renewable-share beta (-1.8 on 0-1 share)", round(pq["ols_first_differenced"]["coefficients"]["d_ren"], 1), -1.8, 0.05)

    ff = json.loads((ROOT / "data/depositor-analysis/early_warning_framework_free_results.json").read_text())
    check("framework-free trigger same day as LI", ff["trigger"]["date"], ew["li_trigger_date"])
    check("framework-free stable above threshold from first week", ff["stable_above_threshold_from"], "2021-10-10")
    check("framework-free final share (69.11%)", round(100 * ff["final_share"], 2), 69.11, 0.01)

    wt2 = json.loads((ROOT / "data/depositor-analysis/within_type_crosspool_results.json").read_text())
    check("within-type cross-pool max delta (<=0.32)", wt2["max_abs_within_type_delta"], 0.32, 0.005)

    ent = json.loads((ROOT / "data/depositor-analysis/entity_funding_analysis.json").read_text())
    v = ent["verdict"]
    check("entity audit: EOAs analysed (33)", v["eoas_analyzed"], 33)
    check("entity audit: cross-side common funders (1)", len(v["non_exchange_common_funders"]), 1)
    check("entity audit: direct cross-side transfers (7)", v["direct_cross_side_transfers"], 7)

    nx = json.loads((ROOT / "data/cross-domain/nftx_dual_margin_results.json").read_text())
    es = nx["summary"]["entry_side_selection"]
    check("NFTX entry-margin selection unanimous (6/6)", es["unanimous"] and len(es["vaults_minted_below_collection_median"]), 6)
    check("NFTX per-vault Wilcoxon significant (6/6)", len(es["per_vault_wilcoxon_sig"]), 6)
    check("NFTX exit-margin extraction absent", nx["summary"]["exit_side_extraction"]["present"], False)

    print(f"\n{'ALL CONSISTENT (exit 0)' if not FAIL else 'INCONSISTENT: ' + ', '.join(FAIL)}")
    sys.exit(1 if FAIL else 0)


def _flatten(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _flatten(v, f"{prefix}{k}.")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _flatten(v, f"{prefix}{i}.")
    else:
        yield prefix.rstrip("."), obj


if __name__ == "__main__":
    main()
