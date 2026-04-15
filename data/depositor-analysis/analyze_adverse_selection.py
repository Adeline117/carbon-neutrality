#!/usr/bin/env python3
"""Depositor-level adverse selection analysis for Toucan BCT pool.

Tests whether BCT depositors who held multiple carbon credit types
selectively deposited their lowest-quality credits while retaining
higher-quality ones --- the precise mechanism Akerlof (1970) predicts.

This analysis uses:
  1. BCT deposit events from fetch_deposits.py (or Dune export)
  2. Depositor TCO2 portfolios (from RPC or Dune)
  3. Our quality scoring framework (archetypes + batch_scorer)

Inputs:
  bct_deposits.json           -- deposit events (from fetch_deposits.py)
  depositor_portfolios.json   -- per-depositor TCO2 holdings
  tco2_metadata.json          -- TCO2 -> project mapping

Outputs:
  adverse_selection_results.json  -- full statistical results
  results.md                      -- human-readable findings

Usage:
  python3 analyze_adverse_selection.py
  python3 analyze_adverse_selection.py --simulated   # run with simulated data for pipeline validation
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

# Import the quality scoring framework
sys.path.insert(0, str(ROOT / "data" / "pilot-scoring"))
sys.path.insert(0, str(ROOT / "data" / "methodology-ratings"))

from score import composite, grade_from_score, load_rubric_index, load_default_stds
from batch_scorer import load_archetypes, score_project, vintage_score

# ── Load scoring infrastructure ────────────────────────────────────────────

RUBRICS = load_rubric_index()
WEIGHTS = {d["id"]: d["weight"] for d in RUBRICS["dimensions"]}
BANDS = RUBRICS["grades"]
DEFAULT_STDS = load_default_stds(RUBRICS)
ARCHETYPES = load_archetypes()

GRADE_NUM = {"B": 0, "BB": 1, "BBB": 2, "A": 3, "AA": 4, "AAA": 5}

# ── Known addresses ────────────────────────────────────────────────────────

KLIMADAO_ADDRESSES = {
    "0x7Dd4f0B986F032A44F913BF92c9e8b7c17D77aD7",  # KlimaDAO treasury
    "0x4D70a031Fc76DA6a9bC0C922101A05FA95c3A227",  # KlimaDAO staking
}

# ── Methodology category mapping from Verra project IDs ────────────────────

# Major Verra project categories deposited into BCT (from CarbonPlan analysis
# and on-chain observation). Maps VCS methodology IDs to our archetype categories.
VERRA_METHODOLOGY_MAP = {
    # REDD+ and forestry
    "VM0006": "redd_project",
    "VM0007": "redd_project",
    "VM0009": "redd_project",
    "VM0015": "redd_project",
    "VM0037": "redd_project",
    "AR-ACM0003": "arr_conservation",
    "AR-AM0014": "arr_conservation",
    "VM0010": "ifm",
    # Industrial gas
    "AM0001": "hfc23_destruction",
    "AMS-III.AB": "ods_destruction",
    # Renewable energy
    "AMS-I.D": "grid_renewable_energy",
    "ACM0002": "grid_renewable_energy",
    "AMS-I.F": "grid_renewable_energy",
    # Cookstoves
    "AMS-II.G": "cookstoves",
    "AMS-I.E": "cookstoves",
    # Waste management
    "ACM0001": "landfill_gas",
    "AMS-III.G": "landfill_gas",
    # Agriculture
    "AMS-III.AU": "rice_methane",
    # N2O
    "AM0028": "n2o_abatement",
}

# Simplified mapping by project name patterns (when methodology is unknown)
PROJECT_TYPE_PATTERNS = {
    "redd": "redd_project",
    "deforestation": "redd_project",
    "forest": "arr_conservation",
    "reforestation": "arr_conservation",
    "afforestation": "arr_conservation",
    "cookstove": "cookstoves",
    "stove": "cookstoves",
    "wind": "grid_renewable_energy",
    "solar": "grid_renewable_energy",
    "hydro": "grid_renewable_energy",
    "renewable": "grid_renewable_energy",
    "landfill": "landfill_gas",
    "methane": "landfill_gas",
    "hfc": "hfc23_destruction",
    "biochar": "biochar",
    "rice": "rice_methane",
    "n2o": "n2o_abatement",
    "nitrous": "n2o_abatement",
}


def classify_tco2(metadata: dict) -> dict:
    """Map a TCO2 token's metadata to a methodology category and quality score."""
    name = metadata.get("name", "").lower()
    symbol = metadata.get("symbol", "").lower()
    vintage = metadata.get("vintage_year", 0)
    project_id = metadata.get("project_id", 0)

    # Try methodology map first
    for meth_id, category in VERRA_METHODOLOGY_MAP.items():
        if meth_id.lower() in name or meth_id.lower() in symbol:
            return score_tco2(category, vintage, metadata.get("country", ""))

    # Try pattern matching on name
    for pattern, category in PROJECT_TYPE_PATTERNS.items():
        if pattern in name or pattern in symbol:
            return score_tco2(category, vintage, metadata.get("country", ""))

    # Default: use the most common category in BCT (REDD+)
    # This is conservative: REDD+ scores low, so defaulting to it
    # understates the retained-deposited gap (biases against our hypothesis)
    return score_tco2("redd_project", vintage if vintage > 0 else 2018, "")


def score_tco2(category: str, vintage_year: int, country: str) -> dict:
    """Score a TCO2 token using the methodology archetype system."""
    project = {
        "methodology_category": category,
        "vintage_year": vintage_year,
        "country": country,
    }
    result = score_project(project, ARCHETYPES, WEIGHTS, DEFAULT_STDS, BANDS)
    return {
        "methodology_category": category,
        "vintage_year": vintage_year,
        "composite": result["composite"],
        "grade": result["grade"],
    }


# ── Core analysis ──────────────────────────────────────────────────────────

def compute_depositor_deltas(
    deposits: list[dict],
    portfolios: dict[str, dict],
    tco2_metadata: dict[str, dict],
    exclude_addresses: set[str] | None = None,
) -> list[dict]:
    """Compute the quality differential (retained - deposited) for each depositor.

    Returns a list of per-depositor records:
        {depositor, mean_deposited_quality, mean_retained_quality, delta,
         n_deposited_types, n_retained_types, total_deposited_tonnes}
    """
    if exclude_addresses is None:
        exclude_addresses = set()

    results = []

    for depositor, portfolio in portfolios.items():
        if depositor in exclude_addresses:
            continue

        deposited = portfolio.get("deposited_tco2s", {})
        retained = portfolio.get("retained_tco2s", {})

        # Skip depositors with only one type total
        all_types = set(deposited.keys()) | set(retained.keys())
        if len(all_types) < 2:
            continue

        # Skip if no retained credits (deposited everything)
        retained_only = {k: v for k, v in retained.items() if k not in deposited}
        if not retained_only:
            continue

        # Score deposited TCO2s
        deposited_scores = []
        deposited_volumes = []
        for tco2_addr, volume in deposited.items():
            meta = tco2_metadata.get(tco2_addr, {})
            score = classify_tco2(meta)
            deposited_scores.append(score["composite"])
            deposited_volumes.append(volume)

        # Score retained TCO2s
        retained_scores = []
        retained_volumes = []
        for tco2_addr, volume in retained_only.items():
            meta = tco2_metadata.get(tco2_addr, {})
            score = classify_tco2(meta)
            retained_scores.append(score["composite"])
            retained_volumes.append(volume)

        if not deposited_scores or not retained_scores:
            continue

        # Volume-weighted means
        total_dep_vol = sum(deposited_volumes)
        total_ret_vol = sum(retained_volumes)

        if total_dep_vol == 0 or total_ret_vol == 0:
            continue

        mean_dep = sum(s * v for s, v in zip(deposited_scores, deposited_volumes)) / total_dep_vol
        mean_ret = sum(s * v for s, v in zip(retained_scores, retained_volumes)) / total_ret_vol

        # Also compute unweighted means
        mean_dep_uw = sum(deposited_scores) / len(deposited_scores)
        mean_ret_uw = sum(retained_scores) / len(retained_scores)

        results.append({
            "depositor": depositor,
            "mean_deposited_quality": round(mean_dep, 2),
            "mean_retained_quality": round(mean_ret, 2),
            "delta": round(mean_ret - mean_dep, 2),
            "delta_unweighted": round(mean_ret_uw - mean_dep_uw, 2),
            "n_deposited_types": len(deposited),
            "n_retained_types": len(retained_only),
            "total_deposited_tonnes": round(total_dep_vol, 2),
            "total_retained_tonnes": round(total_ret_vol, 2),
        })

    return results


def statistical_tests(deltas: list[float]) -> dict:
    """Run statistical tests on the depositor-level delta distribution.

    Returns test statistics, p-values, effect sizes, and confidence intervals.
    """
    n = len(deltas)
    if n < 3:
        return {"error": f"Insufficient data: n={n}"}

    mean_delta = sum(deltas) / n
    var_delta = sum((d - mean_delta) ** 2 for d in deltas) / (n - 1)
    sd_delta = math.sqrt(var_delta) if var_delta > 0 else 0.001

    # ── Paired t-test (H0: mean delta = 0) ─────────────────────────────
    t_stat = mean_delta / (sd_delta / math.sqrt(n))

    # Two-sided p-value approximation using normal distribution for large n
    # For small n, this is approximate; scipy.stats.t would be exact
    z = abs(t_stat)
    # Approximation of 2-sided p from z
    p_t = 2 * (1 - _phi(z))

    # ── Wilcoxon signed-rank test (nonparametric) ──────────────────────
    # Manual implementation (avoids scipy dependency)
    pos_ranks, neg_ranks = [], []
    abs_deltas = [(abs(d), d) for d in deltas if d != 0]
    abs_deltas.sort(key=lambda x: x[0])

    for rank, (_, orig) in enumerate(abs_deltas, 1):
        if orig > 0:
            pos_ranks.append(rank)
        else:
            neg_ranks.append(rank)

    W_plus = sum(pos_ranks)
    W_minus = sum(neg_ranks)
    W = min(W_plus, W_minus)
    n_nonzero = len(abs_deltas)

    # Normal approximation for Wilcoxon test
    if n_nonzero >= 10:
        mu_W = n_nonzero * (n_nonzero + 1) / 4
        sigma_W = math.sqrt(n_nonzero * (n_nonzero + 1) * (2 * n_nonzero + 1) / 24)
        z_W = (W - mu_W) / sigma_W if sigma_W > 0 else 0
        p_wilcoxon = 2 * _phi(-abs(z_W))
    else:
        z_W = float("nan")
        p_wilcoxon = float("nan")

    # ── Bootstrap CI for mean delta ────────────────────────────────────
    random.seed(42)
    bootstrap_means = []
    for _ in range(10_000):
        sample = [random.choice(deltas) for _ in range(n)]
        bootstrap_means.append(sum(sample) / n)

    bootstrap_means.sort()
    ci_lower = bootstrap_means[int(0.025 * 10_000)]
    ci_upper = bootstrap_means[int(0.975 * 10_000)]

    # ── Effect size: Cohen's d ─────────────────────────────────────────
    cohens_d = mean_delta / sd_delta if sd_delta > 0 else float("inf")

    # ── Selection rate: proportion with delta > 0 ──────────────────────
    n_positive = sum(1 for d in deltas if d > 0)
    selection_rate = n_positive / n

    # ── Permutation test ───────────────────────────────────────────────
    # Under H0, the sign of each delta is random
    random.seed(42)
    perm_means = []
    for _ in range(10_000):
        perm_deltas = [d * random.choice([-1, 1]) for d in deltas]
        perm_means.append(sum(perm_deltas) / n)

    p_permutation = sum(1 for pm in perm_means if pm >= mean_delta) / 10_000

    return {
        "n_depositors": n,
        "mean_delta": round(mean_delta, 3),
        "sd_delta": round(sd_delta, 3),
        "median_delta": round(sorted(deltas)[n // 2], 3),

        # Paired t-test
        "t_statistic": round(t_stat, 3),
        "p_value_t_test": round(p_t, 6),

        # Wilcoxon signed-rank
        "W_plus": W_plus,
        "W_minus": W_minus,
        "z_wilcoxon": round(z_W, 3) if not math.isnan(z_W) else None,
        "p_value_wilcoxon": round(p_wilcoxon, 6) if not math.isnan(p_wilcoxon) else None,

        # Bootstrap CI
        "bootstrap_ci_95": [round(ci_lower, 3), round(ci_upper, 3)],

        # Effect size
        "cohens_d": round(cohens_d, 3),
        "cohens_d_interpretation": (
            "large" if abs(cohens_d) >= 0.8 else
            "medium" if abs(cohens_d) >= 0.5 else
            "small" if abs(cohens_d) >= 0.2 else
            "negligible"
        ),

        # Selection rate
        "selection_rate": round(selection_rate, 3),
        "n_positive_delta": n_positive,
        "n_negative_delta": n - n_positive,

        # Permutation test
        "p_value_permutation": round(p_permutation, 4),
    }


def _phi(z: float) -> float:
    """Standard normal CDF approximation (Abramowitz and Stegun 7.1.26)."""
    a1, a2, a3 = 0.254829592, -0.284496736, 1.421413741
    a4, a5 = -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1 if z >= 0 else -1
    z = abs(z)
    t = 1.0 / (1.0 + p * z)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z * z / 2)
    return 0.5 * (1.0 + sign * y)


# ── Simulated data for pipeline validation ─────────────────────────────────

def generate_simulated_data() -> tuple[list[dict], dict[str, dict], dict[str, dict]]:
    """Generate realistic simulated BCT deposit data for pipeline validation.

    The simulation encodes the adverse selection hypothesis: depositors with
    mixed portfolios tend to deposit their lower-quality credits.

    Based on real BCT composition data:
    - ~43 credits, dominated by old REDD+, HFC-23, renewables
    - Peak deposit period: Oct 2021 - Dec 2022
    - ~500-1500 unique depositors
    - KlimaDAO was by far the largest holder (~8M BCT)
    """
    random.seed(42)

    # Define TCO2 token types that existed in BCT
    # (simulated addresses with realistic category/vintage combos)
    tco2_types = [
        # Low quality credits (what we expect to see deposited)
        {"addr": "0xTCO2_REDD_BR_2016_001", "category": "redd_project", "vintage": 2016, "country": "Brazil"},
        {"addr": "0xTCO2_REDD_BR_2018_002", "category": "redd_project", "vintage": 2018, "country": "Brazil"},
        {"addr": "0xTCO2_REDD_ID_2015_003", "category": "redd_project", "vintage": 2015, "country": "Indonesia"},
        {"addr": "0xTCO2_REDD_DRC_2017_004", "category": "redd_project", "vintage": 2017, "country": "DRC"},
        {"addr": "0xTCO2_HFC23_CN_2013_005", "category": "hfc23_destruction", "vintage": 2013, "country": "China"},
        {"addr": "0xTCO2_WIND_CN_2014_006", "category": "grid_renewable_energy", "vintage": 2014, "country": "China"},
        {"addr": "0xTCO2_WIND_IN_2016_007", "category": "grid_renewable_energy", "vintage": 2016, "country": "India"},
        {"addr": "0xTCO2_COOK_KE_2017_008", "category": "cookstoves", "vintage": 2017, "country": "Kenya"},
        {"addr": "0xTCO2_LFG_BR_2016_009", "category": "landfill_gas", "vintage": 2016, "country": "Brazil"},
        {"addr": "0xTCO2_REDD_PE_2019_010", "category": "redd_project", "vintage": 2019, "country": "Peru"},

        # Medium quality credits
        {"addr": "0xTCO2_ARR_BR_2020_011", "category": "arr_conservation", "vintage": 2020, "country": "Brazil"},
        {"addr": "0xTCO2_COOK_GH_2021_012", "category": "cookstoves", "vintage": 2021, "country": "Ghana"},
        {"addr": "0xTCO2_IFM_US_2020_013", "category": "ifm", "vintage": 2020, "country": "USA"},
        {"addr": "0xTCO2_ARR_CO_2021_014", "category": "arr_conservation", "vintage": 2021, "country": "Colombia"},
        {"addr": "0xTCO2_REDD_BR_2021_015", "category": "redd_project", "vintage": 2021, "country": "Brazil"},

        # Higher quality credits (more likely retained)
        {"addr": "0xTCO2_BIOCHAR_FI_2024_016", "category": "biochar", "vintage": 2024, "country": "Finland"},
        {"addr": "0xTCO2_BIOCHAR_US_2023_017", "category": "biochar", "vintage": 2023, "country": "USA"},
        {"addr": "0xTCO2_ARR_PE_2022_018", "category": "arr_conservation", "vintage": 2022, "country": "Peru"},
        {"addr": "0xTCO2_EW_UK_2024_019", "category": "enhanced_weathering", "vintage": 2024, "country": "UK"},
        {"addr": "0xTCO2_N2O_KR_2022_020", "category": "n2o_abatement", "vintage": 2022, "country": "South Korea"},
    ]

    # Score each TCO2 type
    tco2_scores = {}
    for t in tco2_types:
        result = score_tco2(t["category"], t["vintage"], t["country"])
        tco2_scores[t["addr"]] = {**t, **result}

    # Sort by quality for selection simulation
    sorted_types = sorted(tco2_types, key=lambda t: tco2_scores[t["addr"]]["composite"])

    # Generate depositors with adverse selection behavior
    n_depositors = 200
    deposits = []
    portfolios = {}
    tco2_metadata = {t["addr"]: {
        "name": f"TCO2-VCS-{i+100}-{t['vintage']}",
        "symbol": f"TCO2-VCS-{i+100}-{t['vintage']}",
        "vintage_year": t["vintage"],
        "project_id": i + 100,
        "country": t["country"],
        "methodology_category": t["category"],
    } for i, t in enumerate(tco2_types)}

    for d_idx in range(n_depositors):
        depositor = f"0xDEPOSITOR_{d_idx:04d}"

        # Each depositor holds 2-6 TCO2 types
        n_held = random.randint(2, min(6, len(tco2_types)))
        held_types = random.sample(tco2_types, n_held)

        # Adverse selection: depositors preferentially deposit their
        # lowest-quality credits. Probability of depositing inversely
        # proportional to quality score.
        held_scores = [(t, tco2_scores[t["addr"]]["composite"]) for t in held_types]
        held_scores.sort(key=lambda x: x[1])  # lowest quality first

        # The depositor deposits 1 to n_held-1 types (must retain at least 1)
        n_deposit = random.randint(1, max(1, n_held - 1))

        # With 70% probability, deposit the lowest-quality credits (adverse selection)
        # With 30% probability, deposit randomly (noise/null behavior)
        if random.random() < 0.70:
            # Adverse selection: deposit the lowest-quality ones
            deposit_types = [t for t, _ in held_scores[:n_deposit]]
            retain_types = [t for t, _ in held_scores[n_deposit:]]
        else:
            # Random selection (null behavior)
            random.shuffle(held_types)
            deposit_types = held_types[:n_deposit]
            retain_types = held_types[n_deposit:]

        # Create deposit events and portfolio
        deposited_tco2s = {}
        for t in deposit_types:
            volume = random.uniform(10, 10_000)
            deposits.append({
                "sender": depositor,
                "tco2_address": t["addr"],
                "amount_tonnes": volume,
                "block_number": 25_000_000 + d_idx * 1000,
            })
            deposited_tco2s[t["addr"]] = volume

        retained_tco2s = {}
        for t in retain_types:
            retained_tco2s[t["addr"]] = random.uniform(10, 10_000)

        portfolios[depositor] = {
            "depositor": depositor,
            "n_deposits": len(deposit_types),
            "deposit_blocks": [25_000_000 + d_idx * 1000],
            "deposited_tco2s": deposited_tco2s,
            "retained_tco2s": retained_tco2s,
            "n_deposited_types": len(deposited_tco2s),
            "n_retained_types": len(retained_tco2s),
        }

    return deposits, portfolios, tco2_metadata


# ── Results formatting ─────────────────────────────────────────────────────

def format_results_md(
    stats: dict,
    stats_no_klima: dict | None,
    depositor_records: list[dict],
    is_simulated: bool = False,
) -> str:
    """Format analysis results as markdown."""
    lines = [
        "# Depositor-Level Adverse Selection Analysis: Results",
        "",
        "*Testing whether BCT depositors strategically deposited low-quality credits*"
        " *while retaining high-quality ones.*",
        "",
    ]

    if is_simulated:
        lines.extend([
            "> **NOTE:** These results use **simulated data** for pipeline validation.",
            "> The simulation encodes a 70% adverse selection rate to verify that the",
            "> statistical pipeline correctly detects the signal. Real on-chain data is",
            "> needed for publication-ready results.",
            "",
        ])

    lines.extend([
        "## Summary Statistics",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Depositors analyzed | {stats['n_depositors']} |",
        f"| Mean quality differential ($\\Delta$) | {stats['mean_delta']:.3f} |",
        f"| Median $\\Delta$ | {stats['median_delta']:.3f} |",
        f"| SD of $\\Delta$ | {stats['sd_delta']:.3f} |",
        f"| Selection rate ($\\Delta > 0$) | {stats['selection_rate']:.1%} |",
        f"| Depositors with $\\Delta > 0$ | {stats['n_positive_delta']} / {stats['n_depositors']} |",
        "",
        "## Interpretation of $\\Delta$",
        "",
        "$\\Delta = \\bar{{Q}}_{{\\text{{retained}}}} - \\bar{{Q}}_{{\\text{{deposited}}}}$",
        "",
        "- $\\Delta > 0$: depositor retained higher-quality credits than they deposited (**adverse selection**)",
        "- $\\Delta = 0$: no quality differential (random deposit behavior)",
        "- $\\Delta < 0$: depositor deposited higher-quality credits than they retained (reverse selection)",
        "",
        "## Statistical Tests",
        "",
        "### Paired t-test ($H_0$: $\\mu_\\Delta = 0$)",
        "",
        f"- $t$ = {stats['t_statistic']:.3f}",
        f"- $p$ = {stats['p_value_t_test']:.6f}",
        f"- {'**Significant at $\\alpha = 0.05$**' if stats['p_value_t_test'] < 0.05 else 'Not significant'}",
        "",
        "### Wilcoxon signed-rank test (nonparametric)",
        "",
    ])

    if stats.get("z_wilcoxon") is not None:
        lines.extend([
            f"- $W^+$ = {stats['W_plus']}, $W^-$ = {stats['W_minus']}",
            f"- $z$ = {stats['z_wilcoxon']:.3f}",
            f"- $p$ = {stats['p_value_wilcoxon']:.6f}",
            f"- {'**Significant**' if stats['p_value_wilcoxon'] < 0.05 else 'Not significant'}",
            "",
        ])
    else:
        lines.extend(["- Insufficient non-zero observations for Wilcoxon test", ""])

    lines.extend([
        "### Bootstrap 95% CI for mean $\\Delta$",
        "",
        f"- CI: [{stats['bootstrap_ci_95'][0]:.3f}, {stats['bootstrap_ci_95'][1]:.3f}]",
        f"- {'CI excludes zero: **evidence of adverse selection**' if stats['bootstrap_ci_95'][0] > 0 else 'CI includes zero: inconclusive'}",
        "",
        "### Permutation test (one-sided)",
        "",
        f"- $p$ = {stats['p_value_permutation']:.4f}",
        "",
        "### Effect size",
        "",
        f"- Cohen's $d$ = {stats['cohens_d']:.3f} ({stats['cohens_d_interpretation']})",
        "",
    ])

    if stats_no_klima:
        lines.extend([
            "## Robustness: Excluding KlimaDAO",
            "",
            f"| Metric | All depositors | Excluding KlimaDAO |",
            f"|--------|---------------|-------------------|",
            f"| $n$ | {stats['n_depositors']} | {stats_no_klima['n_depositors']} |",
            f"| Mean $\\Delta$ | {stats['mean_delta']:.3f} | {stats_no_klima['mean_delta']:.3f} |",
            f"| Selection rate | {stats['selection_rate']:.1%} | {stats_no_klima['selection_rate']:.1%} |",
            f"| Cohen's $d$ | {stats['cohens_d']:.3f} | {stats_no_klima['cohens_d']:.3f} |",
            f"| $p$ (permutation) | {stats['p_value_permutation']:.4f} | {stats_no_klima['p_value_permutation']:.4f} |",
            "",
        ])

    # Distribution of deltas
    lines.extend([
        "## Distribution of Per-Depositor Quality Differentials",
        "",
        "| $\\Delta$ range | Count | Proportion |",
        "|----------------|-------|------------|",
    ])

    deltas = [r["delta"] for r in depositor_records]
    bins = [(-100, -20), (-20, -10), (-10, 0), (0, 10), (10, 20), (20, 100)]
    labels = ["< -20", "-20 to -10", "-10 to 0", "0 to +10", "+10 to +20", "> +20"]
    for (lo, hi), label in zip(bins, labels):
        count = sum(1 for d in deltas if lo <= d < hi)
        prop = count / len(deltas) if deltas else 0
        lines.append(f"| {label} | {count} | {prop:.1%} |")

    lines.extend([
        "",
        "## Methodology",
        "",
        "See `methodology.md` for full description of the depositor-level analysis",
        "pipeline, including data collection, quality scoring, statistical tests,",
        "and robustness checks.",
        "",
    ])

    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulated", action="store_true",
                        help="Run with simulated data for pipeline validation")
    args = parser.parse_args()

    print("=" * 70)
    print(" DEPOSITOR-LEVEL ADVERSE SELECTION ANALYSIS")
    print(" Toucan BCT Pool on Polygon")
    print("=" * 70)

    if args.simulated:
        print("\n[SIMULATED MODE] Using generated data for pipeline validation\n")
        deposits, portfolios, tco2_metadata = generate_simulated_data()
    else:
        # Load real data
        deposits_path = HERE / "bct_deposits.json"
        portfolios_path = HERE / "depositor_portfolios.json"
        metadata_path = HERE / "tco2_metadata.json"

        for p in [deposits_path, portfolios_path, metadata_path]:
            if not p.exists():
                print(f"ERROR: {p} not found.")
                print("Run fetch_deposits.py first, or use --simulated for pipeline validation.")
                sys.exit(1)

        deposits = json.loads(deposits_path.read_text())
        portfolios = json.loads(portfolios_path.read_text())
        tco2_metadata = json.loads(metadata_path.read_text())

    # ── Compute per-depositor deltas ───────────────────────────────────
    print("Computing per-depositor quality differentials...")
    depositor_records = compute_depositor_deltas(
        deposits, portfolios, tco2_metadata
    )
    print(f"Analyzable depositors (held >= 2 TCO2 types): {len(depositor_records)}")

    if not depositor_records:
        print("ERROR: No depositors with sufficient data for analysis.")
        sys.exit(1)

    # ── Statistical tests: all depositors ──────────────────────────────
    deltas = [r["delta"] for r in depositor_records]
    print(f"\nRunning statistical tests on {len(deltas)} depositors...")
    stats = statistical_tests(deltas)

    # ── Robustness: exclude KlimaDAO ───────────────────────────────────
    depositor_records_no_klima = compute_depositor_deltas(
        deposits, portfolios, tco2_metadata,
        exclude_addresses=KLIMADAO_ADDRESSES,
    )
    if depositor_records_no_klima:
        deltas_no_klima = [r["delta"] for r in depositor_records_no_klima]
        stats_no_klima = statistical_tests(deltas_no_klima)
    else:
        stats_no_klima = None

    # ── Print summary ──────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(" RESULTS")
    print("=" * 70)
    print(f"\n  Depositors analyzed:      {stats['n_depositors']}")
    print(f"  Mean Delta (ret - dep):   {stats['mean_delta']:.3f}")
    print(f"  Median Delta:             {stats['median_delta']:.3f}")
    print(f"  Selection rate:           {stats['selection_rate']:.1%}")
    print(f"  Cohen's d:                {stats['cohens_d']:.3f} ({stats['cohens_d_interpretation']})")
    print(f"  Paired t-test p:          {stats['p_value_t_test']:.6f}")
    if stats.get("p_value_wilcoxon") is not None:
        print(f"  Wilcoxon p:               {stats['p_value_wilcoxon']:.6f}")
    print(f"  Permutation p:            {stats['p_value_permutation']:.4f}")
    print(f"  Bootstrap 95% CI:         [{stats['bootstrap_ci_95'][0]:.3f}, {stats['bootstrap_ci_95'][1]:.3f}]")

    if stats["bootstrap_ci_95"][0] > 0:
        print("\n  >>> EVIDENCE OF ADVERSE SELECTION: CI excludes zero <<<")
    elif stats["mean_delta"] > 0:
        print("\n  >>> SUGGESTIVE of adverse selection but CI includes zero <<<")
    else:
        print("\n  >>> NO EVIDENCE of adverse selection <<<")

    # ── Save results ───────────────────────────────────────────────────
    full_results = {
        "analysis": "depositor_level_adverse_selection",
        "pool": "Toucan BCT (Polygon)",
        "is_simulated": args.simulated,
        "statistics": stats,
        "statistics_excluding_klimadao": stats_no_klima,
        "per_depositor": depositor_records[:50],  # first 50 for inspection
        "n_total_depositor_records": len(depositor_records),
    }

    results_json = HERE / "adverse_selection_results.json"
    results_json.write_text(json.dumps(full_results, indent=2, default=str))
    print(f"\nSaved: {results_json}")

    results_md = HERE / "results.md"
    md = format_results_md(stats, stats_no_klima, depositor_records, is_simulated=args.simulated)
    results_md.write_text(md)
    print(f"Saved: {results_md}")


if __name__ == "__main__":
    main()
