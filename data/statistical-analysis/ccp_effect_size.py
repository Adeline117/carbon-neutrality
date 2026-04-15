#!/usr/bin/env python3
"""Effect size analysis for CCP calibration: CCP-eligible vs non-CCP credits.

Computes:
  1. Cohen's d (pooled SD)
  2. Cliff's delta (nonparametric)
  3. Mann-Whitney U with z-score and p-value
  4. Glass's delta (non-CCP SD as denominator)
  5. 95% bootstrap CI for each effect size (10,000 resamples)
  6. Common Language Effect Size (CLES)

Data is reconstructed from the known CCP validation grade distributions:
  CCP-eligible (n=165): AAA=14, AA=28, A=34, BBB=71, BB=18, B=0
  Non-CCP       (n=153): AAA=0,  AA=12, A=0,  BBB=0,  BB=59, B=82

Ordinal scale: B=0, BB=1, BBB=2, A=3, AA=4, AAA=5.

Pure Python -- no scipy, numpy, or external dependencies.

Usage:
    python3 ccp_effect_size.py
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BATCH_SUMMARY = ROOT / "data" / "methodology-ratings" / "batch_summary.json"

SEED = 42
N_BOOTSTRAP = 10_000
CI_LEVEL = 0.95

# Ordinal scale
GRADE_NUM = {"B": 0, "BB": 1, "BBB": 2, "A": 3, "AA": 4, "AAA": 5}

# Known grade distributions from CCP validation
CCP_DIST = {"AAA": 14, "AA": 28, "A": 34, "BBB": 71, "BB": 18, "B": 0}
NON_CCP_DIST = {"AAA": 0, "AA": 12, "A": 0, "BBB": 0, "BB": 59, "B": 82}


# ---------------------------------------------------------------------------
# Reconstruct ordinal data from grade distributions
# ---------------------------------------------------------------------------

def expand_distribution(dist: dict[str, int]) -> list[int]:
    """Expand a grade distribution into a list of ordinal values."""
    values: list[int] = []
    for grade, count in dist.items():
        values.extend([GRADE_NUM[grade]] * count)
    return values


# ---------------------------------------------------------------------------
# Basic statistics (pure Python)
# ---------------------------------------------------------------------------

def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def variance(xs: list[float], ddof: int = 1) -> float:
    """Sample variance with Bessel correction (ddof=1)."""
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - ddof)


def std(xs: list[float], ddof: int = 1) -> float:
    return math.sqrt(variance(xs, ddof))


def normal_cdf(z: float) -> float:
    """Standard normal CDF via math.erf."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


# ---------------------------------------------------------------------------
# Effect size computations
# ---------------------------------------------------------------------------

def cohens_d(group1: list[float], group2: list[float]) -> float:
    """Cohen's d with pooled standard deviation."""
    n1, n2 = len(group1), len(group2)
    m1, m2 = mean(group1), mean(group2)
    s1_sq = variance(group1, ddof=1)
    s2_sq = variance(group2, ddof=1)
    pooled_var = ((n1 - 1) * s1_sq + (n2 - 1) * s2_sq) / (n1 + n2 - 2)
    pooled_sd = math.sqrt(pooled_var)
    if pooled_sd == 0:
        return float("nan")
    return (m1 - m2) / pooled_sd


def glass_delta(group1: list[float], group2: list[float]) -> float:
    """Glass's delta using group2 (non-CCP) SD as denominator."""
    sd2 = std(group2, ddof=1)
    if sd2 == 0:
        return float("nan")
    return (mean(group1) - mean(group2)) / sd2


def cliffs_delta(group1: list[float], group2: list[float]) -> float:
    """Cliff's delta: nonparametric effect size.

    delta = (# group1 > group2 - # group1 < group2) / (n1 * n2)
    Range: [-1, +1]. +1 means every value in group1 exceeds every value in group2.
    """
    n1, n2 = len(group1), len(group2)
    more = 0
    less = 0
    for a in group1:
        for b in group2:
            if a > b:
                more += 1
            elif a < b:
                less += 1
    return (more - less) / (n1 * n2)


def mann_whitney_u(
    group1: list[float], group2: list[float]
) -> tuple[float, float, float]:
    """Mann-Whitney U test. Returns (U, z, p_two_sided).

    Uses the normal approximation for the z-score (valid for n > 20).
    """
    n1, n2 = len(group1), len(group2)

    # Count how many group1 values exceed each group2 value (and ties)
    u1 = 0.0
    for a in group1:
        for b in group2:
            if a > b:
                u1 += 1.0
            elif a == b:
                u1 += 0.5

    u2 = n1 * n2 - u1
    u_stat = min(u1, u2)

    # Normal approximation
    mu_u = n1 * n2 / 2.0
    # Tie correction for sigma
    combined = group1 + group2
    n = n1 + n2

    # Count tie groups
    from collections import Counter
    counts = Counter(combined)
    tie_correction = sum(t ** 3 - t for t in counts.values()) / (n * (n - 1))
    sigma_u = math.sqrt(n1 * n2 / 12.0 * (n + 1 - tie_correction))

    if sigma_u == 0:
        return (u_stat, float("nan"), float("nan"))

    z = (u1 - mu_u) / sigma_u
    p = 2.0 * (1.0 - normal_cdf(abs(z)))

    return (u_stat, z, p)


def cles(group1: list[float], group2: list[float]) -> float:
    """Common Language Effect Size: P(random CCP > random non-CCP)."""
    n1, n2 = len(group1), len(group2)
    count = 0.0
    for a in group1:
        for b in group2:
            if a > b:
                count += 1.0
            elif a == b:
                count += 0.5
    return count / (n1 * n2)


# ---------------------------------------------------------------------------
# Bootstrap CI
# ---------------------------------------------------------------------------

def bootstrap_ci(
    group1: list[float],
    group2: list[float],
    stat_fn,
    rng: random.Random,
    n_boot: int = N_BOOTSTRAP,
    alpha: float = 1 - CI_LEVEL,
) -> tuple[float, float]:
    """Percentile bootstrap CI for a two-sample statistic."""
    boot_vals: list[float] = []
    n1, n2 = len(group1), len(group2)
    for _ in range(n_boot):
        b1 = [group1[rng.randint(0, n1 - 1)] for _ in range(n1)]
        b2 = [group2[rng.randint(0, n2 - 1)] for _ in range(n2)]
        val = stat_fn(b1, b2)
        if not math.isnan(val):
            boot_vals.append(val)
    if not boot_vals:
        return (float("nan"), float("nan"))
    boot_vals.sort()
    lo = int(math.floor((alpha / 2) * len(boot_vals)))
    hi = int(math.ceil((1 - alpha / 2) * len(boot_vals))) - 1
    lo = max(0, min(lo, len(boot_vals) - 1))
    hi = max(0, min(hi, len(boot_vals) - 1))
    return (boot_vals[lo], boot_vals[hi])


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def _r(v: float, decimals: int = 4) -> float:
    if math.isnan(v):
        return v
    return round(v, decimals)


def _fmt(v: float) -> str:
    if isinstance(v, float) and math.isnan(v):
        return "n/a"
    return f"{v:.4f}"


def results_to_markdown(results: dict) -> str:
    lines = [
        "# CCP Calibration Effect Size Analysis",
        "",
        f"Seed: {SEED} | Bootstrap resamples: {N_BOOTSTRAP:,}",
        "",
        "## Data Summary",
        "",
        f"- CCP-eligible credits: n = {results['n_ccp']}",
        f"- Non-CCP credits: n = {results['n_non_ccp']}",
        f"- CCP mean grade (ordinal): {results['ccp_mean']:.3f}",
        f"- Non-CCP mean grade (ordinal): {results['non_ccp_mean']:.3f}",
        f"- CCP SD: {results['ccp_sd']:.3f}",
        f"- Non-CCP SD: {results['non_ccp_sd']:.3f}",
        "",
        "### Grade distributions",
        "",
        "| Grade | Ordinal | CCP | Non-CCP |",
        "|-------|---------|-----|---------|",
    ]
    for g in ["AAA", "AA", "A", "BBB", "BB", "B"]:
        lines.append(f"| {g} | {GRADE_NUM[g]} | {CCP_DIST[g]} | {NON_CCP_DIST[g]} |")

    lines.extend([
        "",
        "## Effect Sizes",
        "",
        "| Metric | Value | 95% CI | Interpretation |",
        "|--------|------:|--------|----------------|",
    ])

    for es in results["effect_sizes"]:
        ci_str = f"[{_fmt(es['ci_lower'])}, {_fmt(es['ci_upper'])}]"
        lines.append(f"| {es['name']} | {_fmt(es['value'])} | {ci_str} | {es['interpretation']} |")

    lines.extend([
        "",
        "## Mann-Whitney U Test",
        "",
        f"- U statistic: {_fmt(results['mann_whitney']['u'])}",
        f"- z-score: {_fmt(results['mann_whitney']['z'])}",
        f"- p-value (two-sided): {results['mann_whitney']['p']:.2e}",
        f"- Significant at alpha=0.05: {'yes' if results['mann_whitney']['p'] < 0.05 else 'no'}",
        f"- Significant at alpha=0.001: {'yes' if results['mann_whitney']['p'] < 0.001 else 'no'}",
        "",
        "## CLES (Common Language Effect Size)",
        "",
        f"- P(random CCP credit outranks random non-CCP credit) = **{results['cles']:.1%}**",
        f"- 95% CI: [{_fmt(results['cles_ci_lower'])}, {_fmt(results['cles_ci_upper'])}]",
        "",
        "## Interpretation",
        "",
        "- Cohen's d > 0.8 is conventionally 'large'; values > 2.0 indicate very large separation.",
        "- Cliff's delta near +1.0 means CCP credits almost always outrank non-CCP credits.",
        "- CLES close to 1.0 means a randomly chosen CCP credit will almost certainly outscore a randomly chosen non-CCP credit.",
        "- The CCP quality gate effectively separates the credit quality distribution into two nearly non-overlapping populations.",
        "",
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    rng = random.Random(SEED)

    # Load batch summary for context (totals validation)
    try:
        with BATCH_SUMMARY.open() as f:
            batch = json.load(f)
        print(f"Batch summary: {batch['total_projects']} projects, distribution: {batch['grade_distribution']}")
    except FileNotFoundError:
        print(f"Warning: {BATCH_SUMMARY} not found; using hardcoded distributions.")

    # Reconstruct ordinal data
    ccp_data = [float(v) for v in expand_distribution(CCP_DIST)]
    non_ccp_data = [float(v) for v in expand_distribution(NON_CCP_DIST)]

    print(f"\nCCP-eligible: n={len(ccp_data)}, mean={mean(ccp_data):.3f}, sd={std(ccp_data):.3f}")
    print(f"Non-CCP:      n={len(non_ccp_data)}, mean={mean(non_ccp_data):.3f}, sd={std(non_ccp_data):.3f}")

    # Compute effect sizes
    d = cohens_d(ccp_data, non_ccp_data)
    delta_cliff = cliffs_delta(ccp_data, non_ccp_data)
    delta_glass = glass_delta(ccp_data, non_ccp_data)
    u_stat, z_stat, p_val = mann_whitney_u(ccp_data, non_ccp_data)
    cles_val = cles(ccp_data, non_ccp_data)

    print(f"\nCohen's d:     {d:.4f}")
    print(f"Cliff's delta: {delta_cliff:.4f}")
    print(f"Glass's delta: {delta_glass:.4f}")
    print(f"Mann-Whitney U={u_stat:.1f}, z={z_stat:.4f}, p={p_val:.2e}")
    print(f"CLES:          {cles_val:.4f}")

    # Bootstrap CIs
    print(f"\nComputing bootstrap CIs ({N_BOOTSTRAP:,} resamples)...")
    ci_d = bootstrap_ci(ccp_data, non_ccp_data, cohens_d, rng)
    ci_cliff = bootstrap_ci(ccp_data, non_ccp_data, cliffs_delta, rng)
    ci_glass = bootstrap_ci(ccp_data, non_ccp_data, glass_delta, rng)
    ci_cles = bootstrap_ci(ccp_data, non_ccp_data, cles, rng)

    def interpret_d(val: float) -> str:
        absv = abs(val)
        if absv >= 2.0:
            return "Very large"
        if absv >= 0.8:
            return "Large"
        if absv >= 0.5:
            return "Medium"
        if absv >= 0.2:
            return "Small"
        return "Negligible"

    def interpret_cliff(val: float) -> str:
        absv = abs(val)
        if absv >= 0.474:
            return "Large"
        if absv >= 0.33:
            return "Medium"
        if absv >= 0.147:
            return "Small"
        return "Negligible"

    effect_sizes = [
        {
            "name": "Cohen's d (pooled SD)",
            "value": _r(d),
            "ci_lower": _r(ci_d[0]),
            "ci_upper": _r(ci_d[1]),
            "interpretation": interpret_d(d),
        },
        {
            "name": "Glass's delta (non-CCP SD)",
            "value": _r(delta_glass),
            "ci_lower": _r(ci_glass[0]),
            "ci_upper": _r(ci_glass[1]),
            "interpretation": interpret_d(delta_glass),
        },
        {
            "name": "Cliff's delta (nonparametric)",
            "value": _r(delta_cliff),
            "ci_lower": _r(ci_cliff[0]),
            "ci_upper": _r(ci_cliff[1]),
            "interpretation": interpret_cliff(delta_cliff),
        },
        {
            "name": "CLES",
            "value": _r(cles_val),
            "ci_lower": _r(ci_cles[0]),
            "ci_upper": _r(ci_cles[1]),
            "interpretation": f"{cles_val:.1%} probability CCP > non-CCP",
        },
    ]

    results = {
        "n_ccp": len(ccp_data),
        "n_non_ccp": len(non_ccp_data),
        "ccp_mean": _r(mean(ccp_data)),
        "non_ccp_mean": _r(mean(non_ccp_data)),
        "ccp_sd": _r(std(ccp_data)),
        "non_ccp_sd": _r(std(non_ccp_data)),
        "effect_sizes": effect_sizes,
        "mann_whitney": {
            "u": _r(u_stat),
            "z": _r(z_stat),
            "p": p_val,
        },
        "cles": _r(cles_val),
        "cles_ci_lower": _r(ci_cles[0]),
        "cles_ci_upper": _r(ci_cles[1]),
        "seed": SEED,
        "n_bootstrap": N_BOOTSTRAP,
    }

    # Write outputs
    out_json = HERE / "ccp_effect_size_results.json"
    out_json.write_text(json.dumps(results, indent=2, default=str))

    out_md = HERE / "ccp_effect_size_results.md"
    out_md.write_text(results_to_markdown(results))

    print(f"\nWrote: {out_json}")
    print(f"Wrote: {out_md}")


if __name__ == "__main__":
    main()
