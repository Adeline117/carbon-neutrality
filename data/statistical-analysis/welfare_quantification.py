#!/usr/bin/env python3
"""Welfare Cost Quantification: Dollar value of BCT's adverse selection.

Computes the foregone genuine emission reductions from BCT absorbing
low-quality credits instead of market-average or quality-gated credits.

Additionality rates by type from literature:
  - Calel et al. (2024): <16% of credits represent real reductions
  - West et al. (2023): REDD+ over-crediting ~3x
  - Cames et al. (2016): CDM renewable energy 73% non-additional
  - Schneider et al. (2019): Large hydro 95%+ non-additional

Social Cost of Carbon: US EPA 2024 ($51-190/tCO2, central $51)

Usage:
    python3 welfare_quantification.py
"""

import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

SEED = 42
N_MONTE_CARLO = 10_000

# BCT composition by type (tonnes deposited, from manifest)
BCT_COMPOSITION = {
    "Renewable":     10_233_697,
    "Fossil switch":  1_735_878,
    "ARR":              845_104,
    "Waste/Methane":    812_725,
    "Industrial gas":   672_255,
    "REDD+":            521_889,
    "IFM":              285_367,
    "Industrial":       100_814,
}

TOTAL_BCT = sum(BCT_COMPOSITION.values())

# Additionality rates: P(real emission reduction | credit type)
# Each type has (low, central, high) estimates from literature
ADDITIONALITY_RATES = {
    "Renewable":     (0.02, 0.05, 0.15),   # Cames 2016: 73% non-additional; Schneider 2019
    "Fossil switch": (0.10, 0.25, 0.40),   # Mixed evidence; some fuel switching is genuine
    "ARR":           (0.30, 0.50, 0.70),    # Nature-based removal, moderate additionality
    "Waste/Methane": (0.20, 0.40, 0.60),    # Landfill gas, methane capture — moderate
    "Industrial gas":(0.60, 0.80, 0.95),    # HFC/N2O destruction — generally additional
    "REDD+":         (0.10, 0.25, 0.40),    # West 2023: ~3x over-crediting; Calel 2024
    "IFM":           (0.25, 0.45, 0.65),    # Improved forest management — moderate
    "Industrial":    (0.15, 0.30, 0.50),    # Various industrial processes
}

# Counterfactual: market-average quality mix (VCS registry proportions)
# From base_rate_analysis: VCS is ~37% renewable
MARKET_AVG_COMPOSITION = {
    "Renewable":     0.37,
    "Fossil switch": 0.08,
    "ARR":           0.06,
    "Waste/Methane": 0.07,
    "Industrial gas": 0.04,
    "REDD+":         0.17,
    "IFM":           0.05,
    "Industrial":    0.03,
    # Cookstoves, other: fill to 1.0
}
# Normalize
remaining = 1.0 - sum(MARKET_AVG_COMPOSITION.values())
MARKET_AVG_COMPOSITION["Other_high_quality"] = remaining  # Assume 40% additionality
ADDITIONALITY_RATES["Other_high_quality"] = (0.25, 0.40, 0.55)

# Social Cost of Carbon (US EPA 2024, $/tCO2)
SCC_RANGE = {
    "low": 51,       # EPA 2024 central at 3% discount
    "central": 120,   # EPA 2024 central at 2% discount
    "high": 190,      # EPA 2024 95th percentile at 2% discount
}


def compute_real_tonnes(composition_tonnes, additionality_rates, scenario="central"):
    """Compute real emission reductions given composition and additionality rates."""
    idx = {"low": 0, "central": 1, "high": 2}[scenario]
    total_real = 0
    for credit_type, tonnes in composition_tonnes.items():
        rate = additionality_rates.get(credit_type, (0.20, 0.35, 0.50))[idx]
        total_real += tonnes * rate
    return total_real


def monte_carlo_welfare(rng, n_iter=N_MONTE_CARLO):
    """Monte Carlo over additionality rates and SCC to produce welfare distribution."""
    welfare_gaps = []

    for _ in range(n_iter):
        # Sample additionality rates (triangular distribution)
        sampled_rates = {}
        for t, (lo, mid, hi) in ADDITIONALITY_RATES.items():
            sampled_rates[t] = rng.triangular(lo, hi, mid)

        # BCT actual real tonnes
        bct_real = sum(
            BCT_COMPOSITION.get(t, 0) * sampled_rates.get(t, 0.3)
            for t in BCT_COMPOSITION
        )

        # Counterfactual: same total tonnes, market-average mix
        cf_composition = {
            t: TOTAL_BCT * share
            for t, share in MARKET_AVG_COMPOSITION.items()
        }
        cf_real = sum(
            cf_composition.get(t, 0) * sampled_rates.get(t, 0.3)
            for t in cf_composition
        )

        # Foregone real reductions
        foregone = cf_real - bct_real

        # Sample SCC (uniform between low and high)
        scc = rng.uniform(SCC_RANGE["low"], SCC_RANGE["high"])

        welfare_gap = foregone * scc
        welfare_gaps.append({
            "bct_real_tonnes": bct_real,
            "cf_real_tonnes": cf_real,
            "foregone_tonnes": foregone,
            "scc": scc,
            "welfare_gap_usd": welfare_gap,
        })

    return welfare_gaps


def percentile(data, p):
    data_sorted = sorted(data)
    idx = int(p * len(data_sorted))
    idx = max(0, min(idx, len(data_sorted) - 1))
    return data_sorted[idx]


def main():
    rng = random.Random(SEED)

    # Point estimates
    scenarios = {}
    for scenario in ["low", "central", "high"]:
        bct_real = compute_real_tonnes(BCT_COMPOSITION, ADDITIONALITY_RATES, scenario)
        cf_composition = {t: TOTAL_BCT * share for t, share in MARKET_AVG_COMPOSITION.items()}
        cf_real = compute_real_tonnes(cf_composition, ADDITIONALITY_RATES, scenario)
        foregone = cf_real - bct_real

        scenarios[scenario] = {
            "bct_real_tonnes": round(bct_real),
            "cf_real_tonnes": round(cf_real),
            "foregone_tonnes": round(foregone),
            "bct_additionality_pct": round(bct_real / TOTAL_BCT * 100, 1),
            "cf_additionality_pct": round(cf_real / TOTAL_BCT * 100, 1),
        }

        for scc_label, scc_val in SCC_RANGE.items():
            scenarios[scenario][f"welfare_gap_{scc_label}_scc_usd"] = round(foregone * scc_val)

    # Monte Carlo
    mc_results = monte_carlo_welfare(rng)
    welfare_gaps = [r["welfare_gap_usd"] for r in mc_results]
    foregone_tonnes_list = [r["foregone_tonnes"] for r in mc_results]

    results = {
        "test": "Welfare cost of BCT's design-determined adverse selection",
        "method": "Compare real emission reductions under BCT's actual composition vs. counterfactual market-average composition. Additionality rates from Calel et al. 2024, West et al. 2023, Cames et al. 2016. SCC from US EPA 2024.",
        "total_bct_tonnes": TOTAL_BCT,
        "point_estimates": scenarios,
        "monte_carlo": {
            "n_iterations": N_MONTE_CARLO,
            "foregone_tonnes": {
                "mean": round(sum(foregone_tonnes_list) / len(foregone_tonnes_list)),
                "median": round(percentile(foregone_tonnes_list, 0.5)),
                "p5": round(percentile(foregone_tonnes_list, 0.05)),
                "p95": round(percentile(foregone_tonnes_list, 0.95)),
            },
            "welfare_gap_usd": {
                "mean": round(sum(welfare_gaps) / len(welfare_gaps)),
                "median": round(percentile(welfare_gaps, 0.5)),
                "p5": round(percentile(welfare_gaps, 0.05)),
                "p95": round(percentile(welfare_gaps, 0.95)),
                "p25": round(percentile(welfare_gaps, 0.25)),
                "p75": round(percentile(welfare_gaps, 0.75)),
            }
        },
        "verdict": "",
        "seed": SEED,
    }

    # Format verdict
    median_gap = results["monte_carlo"]["welfare_gap_usd"]["median"]
    p5 = results["monte_carlo"]["welfare_gap_usd"]["p5"]
    p95 = results["monte_carlo"]["welfare_gap_usd"]["p95"]
    results["verdict"] = (
        f"BCT's design-determined adverse selection resulted in an estimated "
        f"${median_gap / 1e6:.0f}M in foregone genuine emission reductions "
        f"(90% CI: ${p5 / 1e6:.0f}M -- ${p95 / 1e6:.0f}M), "
        f"relative to a counterfactual pool with market-average quality composition."
    )

    out = HERE / "welfare_quantification_results.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Total BCT tonnes: {TOTAL_BCT:,}")
    print(f"\n{'Scenario':<12} {'BCT real':>12} {'CF real':>12} {'Foregone':>12} {'BCT add%':>10} {'CF add%':>10}")
    print("-" * 70)
    for s in ["low", "central", "high"]:
        d = scenarios[s]
        print(f"{s:<12} {d['bct_real_tonnes']:>12,} {d['cf_real_tonnes']:>12,} {d['foregone_tonnes']:>12,} {d['bct_additionality_pct']:>9.1f}% {d['cf_additionality_pct']:>9.1f}%")

    print(f"\nWelfare gap (point estimates):")
    for s in ["low", "central", "high"]:
        d = scenarios[s]
        for scc in ["low", "central", "high"]:
            gap = d[f"welfare_gap_{scc}_scc_usd"]
            print(f"  {s} additionality × ${SCC_RANGE[scc]}/t SCC: ${gap / 1e6:,.0f}M")

    print(f"\nMonte Carlo ({N_MONTE_CARLO:,} iterations):")
    mc = results["monte_carlo"]
    print(f"  Foregone tonnes: {mc['foregone_tonnes']['mean']:,} (mean), [{mc['foregone_tonnes']['p5']:,} - {mc['foregone_tonnes']['p95']:,}] (90% CI)")
    print(f"  Welfare gap: ${mc['welfare_gap_usd']['mean'] / 1e6:,.0f}M (mean)")
    print(f"  Welfare gap: ${mc['welfare_gap_usd']['median'] / 1e6:,.0f}M (median)")
    print(f"  90% CI: ${mc['welfare_gap_usd']['p5'] / 1e6:,.0f}M -- ${mc['welfare_gap_usd']['p95'] / 1e6:,.0f}M")

    print(f"\n{results['verdict']}")
    print(f"\nWrote: {out}")


if __name__ == "__main__":
    main()
