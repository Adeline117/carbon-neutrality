#!/usr/bin/env python3
"""
multipool_comparison.py
=======================

Assemble a 4-pool adverse-selection / temporal-quality comparison to address
the "n=1 / single pool" objection: BCT, NCT, C3 (UBO+NBO), Moss MCO2.

For BCT and NCT: REUSE the already-computed temporal statistics from
nct_comparison_results.json (do NOT recompute).

For C3 and MCO2: use the pool scores produced by score_alt_pools.py and compute
whatever adverse-selection signal is honestly identifiable. Because the C3/MCO2
event records carry NO per-token project type or vintage (see score_alt_pools.py
data_gaps), per-deposit quality is unobserved -> a within-pool temporal Spearman
of quality vs deposit order is NOT identifiable and is reported as null, with the
limitation recorded in data_gaps. Composition, n, and tonnes ARE reported.

Where a temporal signal IS computable from the raw events alone (deposit-SIZE
trend over block order, as a weak proxy for "small low-quality dumps late"), it
is reported in an auxiliary field but NOT presented as the quality-rho.

Output: multipool_comparison.json
Run: python3 multipool_comparison.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path("/Users/adelinewen/carbon-neutrality/data/depositor-analysis")
NCT_RESULTS = HERE / "nct_comparison_results.json"
ALT_SCORES = HERE / "score_alt_pools.json"
EVENTS_PATH = HERE / "alternative_pool_events.json"
OUT_PATH = HERE / "multipool_comparison.json"


def top_type(comp: dict) -> str | None:
    if not comp:
        return None
    return max(comp.items(), key=lambda kv: kv[1])[0]


def deposit_size_trend(deposits: list[dict]) -> dict:
    """Auxiliary, honest signal computable WITHOUT quality metadata:
    Spearman rho of deposit AMOUNT vs block order. This is NOT the quality-rho;
    it is a weak structural proxy reported separately."""
    if len(deposits) < 3:
        return {"spearman_rho_size_vs_order": None, "spearman_p": None, "n": len(deposits)}
    ordered = sorted(deposits, key=lambda d: d.get("block_number", 0))
    blocks = np.array([d.get("block_number", 0) for d in ordered], dtype=float)
    amounts = np.array([d.get("amount", 0.0) for d in ordered], dtype=float)
    rho, p = stats.spearmanr(blocks, amounts)
    return {
        "spearman_rho_size_vs_order": None if np.isnan(rho) else round(float(rho), 4),
        "spearman_p": None if np.isnan(p) else float(p),
        "n": len(ordered),
    }


def build_bct(nct: dict) -> dict:
    t = nct["bct_temporal"]
    comp = pct_composition_from_bct()
    return {
        "pool": "BCT (Toucan permissionless)",
        "mechanism": "permissionless deposit pool",
        "n_deposits": t["n_deposits_total"],
        "n_deposits_scored": t["n_deposits_scored"],
        "total_tonnes": round(t["total_tonnes"], 2),
        "mean_quality": round(t["mean_quality"], 2),
        "volume_weighted_mean_quality": round(t["volume_weighted_mean_quality"], 2),
        "temporal_rho": round(t["spearman_rho"], 4),
        "temporal_p": t["spearman_p"],
        "q1_q4_decline": round(t["Q1_Q4_diff"], 4),
        "q1_mean": round(t["quartiles"]["Q1"]["mean_quality"], 2),
        "q4_mean": round(t["quartiles"]["Q4"]["mean_quality"], 2),
        "composition": comp,
        "top_type": top_type(comp),
        "redemption_selectivity": None,
        "price_quality": None,
        "source": "nct_comparison_results.json",
        "temporal_identified": True,
    }


def build_nct(nct: dict) -> dict:
    t = nct["nct_temporal"]
    return {
        "pool": "NCT (Toucan AFOLU-filtered)",
        "mechanism": "filtered deposit pool (AFOLU only, vintage >= 2012)",
        "n_deposits": t["n_deposits_total"],
        "n_deposits_scored": t["n_deposits_scored"],
        "total_tonnes": round(t["total_tonnes"], 2),
        "mean_quality": round(t["mean_quality"], 2),
        "volume_weighted_mean_quality": round(t["volume_weighted_mean_quality"], 2),
        "temporal_rho": round(t["spearman_rho"], 4),
        "temporal_p": t["spearman_p"],
        "q1_q4_decline": round(t["Q1_Q4_diff"], 4),
        "q1_mean": round(t["quartiles"]["Q1"]["mean_quality"], 2),
        "q4_mean": round(t["quartiles"]["Q4"]["mean_quality"], 2),
        "composition": {"AFOLU (nature-based)": 100.0},
        "top_type": "AFOLU (nature-based)",
        "redemption_selectivity": None,
        "price_quality": None,
        "source": "nct_comparison_results.json",
        "temporal_identified": True,
    }


def pct_composition_from_bct() -> dict:
    """BCT composition by tonnes from the existing complete composition file,
    if available; else from redemption_analysis deposited composition."""
    for fname in ("bct_composition_complete.json", "bct_composition_final.json"):
        p = HERE / fname
        if p.exists():
            try:
                d = json.loads(p.read_text())
                # find a pct-by-type dict
                for key in ("composition_pct", "deposited_composition_pct",
                            "composition_by_type_pct", "pct"):
                    if key in d and isinstance(d[key], dict):
                        return {k: round(v, 2) for k, v in d[key].items()}
                # else if it's already a flat type->pct dict
                if all(isinstance(v, (int, float)) for v in d.values()):
                    return {k: round(v, 2) for k, v in d.items()}
            except Exception:
                pass
    # fallback to redemption_analysis deposited composition pct
    rp = HERE / "redemption_analysis.json"
    if rp.exists():
        d = json.loads(rp.read_text())
        if "deposited_composition_pct" in d:
            return {k: round(v, 2) for k, v in d["deposited_composition_pct"].items()}
    return {}


def build_alt(pool_key: str, alt: dict, deposits: list[dict], mechanism: str,
              temporal_identified: bool) -> dict:
    p = alt["pools"][pool_key]
    comp = p["composition_pct_tonnes"]
    aux = deposit_size_trend(deposits)
    return {
        "pool": p["pool"],
        "mechanism": mechanism,
        "n_deposits": p["n_deposits"],
        "n_deposits_scored": p["n_deposits"],
        "total_tonnes": p["total_tonnes"],
        "mean_quality": p["mean_quality"],
        "volume_weighted_mean_quality": p["volume_weighted_mean_quality"],
        # Quality-vs-order Spearman is NOT identifiable (per-token quality
        # unobserved). Reported null, not fabricated.
        "temporal_rho": None,
        "temporal_p": None,
        "q1_q4_decline": None,
        "q1_mean": None,
        "q4_mean": None,
        "composition": comp,
        "top_type": top_type(comp),
        "redemption_selectivity": None,
        "price_quality": None,
        "source": "computed (score_alt_pools.py)",
        "temporal_identified": temporal_identified,
        "aux_deposit_size_trend": aux,
    }


def main() -> None:
    nct = json.loads(NCT_RESULTS.read_text())
    alt = json.loads(ALT_SCORES.read_text())
    events = json.loads(EVENTS_PATH.read_text())

    c3_deposits = events.get("ubo_deposits", []) + events.get("nbo_deposits", [])
    mco2_mints = events.get("mco2_mints", [])

    pools = {
        "BCT": build_bct(nct),
        "NCT": build_nct(nct),
        "C3": build_alt("C3", alt, c3_deposits,
                        "permissionless deposit pool (UBO) + filtered (NBO)",
                        temporal_identified=False),
        "MCO2": build_alt("MCO2", alt, mco2_mints,
                          "centrally-issued bridge token (NOT a deposit pool)",
                          temporal_identified=False),
    }

    # Headline: direction-consistency across pools where temporal quality IS
    # identified (BCT permissionless vs NCT filtered).
    bct_rho = pools["BCT"]["temporal_rho"]
    nct_rho = pools["NCT"]["temporal_rho"]
    headline = (
        f"Temporal quality degradation is identified only where per-token "
        f"quality is observable: BCT (permissionless) shows a strong, "
        f"significant decline (rho={bct_rho:+.3f}, p={pools['BCT']['temporal_p']:.1e}), "
        f"while NCT (AFOLU-filtered, same operator/chain/period) does NOT "
        f"(rho={nct_rho:+.3f}, p={pools['NCT']['temporal_p']:.3f}). "
        f"The contrast holds the depositor population, chain, and time window "
        f"fixed and varies only the pool's quality filter, so the n=1 objection "
        f"is answered by a within-operator permissionless-vs-filtered comparison "
        f"rather than by a single pool. C3 (UBO/NBO) and MCO2 are included for "
        f"composition/volume context but cannot supply an independent temporal-rho: "
        f"C3 lacks per-token quality metadata and MCO2 has no adverse-selection "
        f"deposit mechanism at all (centrally-issued fixed-supply token). Among "
        f"pools where quality is observed, the direction is CONSISTENT: the "
        f"permissionless pool degrades, the filtered pool does not."
    )

    data_gaps = [
        "C3 (UBO+NBO): no per-token project type, methodology, name, or vintage "
        "in the event records or anywhere in the repo. Per-deposit quality is "
        "unobserved, so a temporal Spearman of quality vs deposit order is NOT "
        "identifiable. temporal_rho/temporal_p/q1_q4_decline set to null. "
        "Composition (REDD+/Renewable/ARR/...) is a documented quality-filter "
        "prior, not a measured per-token mix.",
        "C3 statistical power is ~8% of BCT (92 vs 1,187 deposits) even if "
        "metadata existed; insufficient for an independent temporal DiD "
        "(per independent_control_search.json).",
        "MCO2: NOT a permissionless deposit pool. 'mints' are Polygon PoS-bridge "
        "deposits of a fixed-supply, centrally-issued token (Moss Amazon REDD+). "
        "There is no race-to-the-bottom deposit mechanism, so adverse selection "
        "is structurally absent and a temporal quality-rho is not meaningful. "
        "temporal_rho set to null.",
        "No redemption events for C3 or MCO2 exist in the repo (BCT's "
        "redemption_analysis.json has no counterpart). Selective-redemption rates "
        "by type are NOT computable for C3/MCO2; redemption_selectivity = null.",
        "No price series for C3 (UBO/NBO) or MCO2 in the repo (cf. BCT "
        "bct_prices_daily.json). price_quality = null for both.",
        "BCT and NCT temporal statistics are reused verbatim from "
        "nct_comparison_results.json and were NOT recomputed here.",
    ]

    out = {
        "meta": {
            "generated_by": "multipool_comparison.py",
            "purpose": "4-pool generalization to address the n=1 / single-pool objection",
            "pools_compared": ["BCT", "NCT", "C3", "MCO2"],
            "rubric": "identical BCT/NCT scoring rubric (scoring-rubrics v0.4)",
        },
        "pools": pools,
        "direction_consistency": {
            "pools_with_identified_temporal_quality": ["BCT", "NCT"],
            "bct_rho": bct_rho,
            "nct_rho": nct_rho,
            "degradation_direction_consistent": (bct_rho is not None and bct_rho < 0),
            "permissionless_degrades_filtered_does_not": (
                bct_rho is not None and nct_rho is not None
                and bct_rho < -0.3 and abs(nct_rho) < 0.15
            ),
            "note": "C3 and MCO2 cannot contribute a temporal-rho (see data_gaps); "
                    "they contribute composition/volume context only.",
        },
        "headline": headline,
        "data_gaps": data_gaps,
    }

    OUT_PATH.write_text(json.dumps(out, indent=2))

    # Console table
    print(f"Wrote {OUT_PATH}\n")
    hdr = f"{'Pool':<6} {'n':>6} {'tonnes':>14} {'rho (p)':>22} {'Q1->Q4':>9} {'top type':<22}"
    print(hdr)
    print("-" * len(hdr))
    for key in ["BCT", "NCT", "C3", "MCO2"]:
        p = pools[key]
        if p["temporal_rho"] is not None:
            rho_s = f"{p['temporal_rho']:+.3f} (p={p['temporal_p']:.1e})"
            q_s = f"{p['q1_q4_decline']:+.2f}"
        else:
            rho_s = "null (not identifiable)"
            q_s = "null"
        print(f"{key:<6} {p['n_deposits']:>6} {p['total_tonnes']:>14,.0f} "
              f"{rho_s:>22} {q_s:>9} {str(p['top_type']):<22}")
    print()
    print("Direction consistent (permissionless degrades, filtered does not):",
          out["direction_consistency"]["permissionless_degrades_filtered_does_not"])


if __name__ == "__main__":
    main()
