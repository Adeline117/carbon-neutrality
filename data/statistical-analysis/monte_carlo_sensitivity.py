#!/usr/bin/env python3
"""Monte Carlo sensitivity analysis via Dirichlet weight perturbation.

Goes beyond the existing +/-5pp perturbation by sampling 10,000 weight
vectors from a Dirichlet distribution centered on the current weights.

For each sampled weight vector, all 29 pilot credits are re-scored.
The analysis reports per-credit grade stability, fragile credits,
global robustness, and pairwise weight-grade sensitivity.

Concentration parameters tested: 20 (wide), 50 (default), 100 (tight).

Co-benefits weight is forced to 0 in all samples (safeguards-gate):
weights are sampled for the 6 non-zero dimensions and renormalized.

Pure Python -- no scipy, numpy, or external dependencies.

Usage:
    python3 monte_carlo_sensitivity.py
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUBRICS_PATH = ROOT / "data" / "scoring-rubrics" / "index.json"
CREDITS_PATH = ROOT / "data" / "pilot-scoring" / "credits.json"

# Add pilot-scoring to path for score.py functions
sys.path.insert(0, str(ROOT / "data" / "pilot-scoring"))
from score import (
    apply_dimension_adjustments,
    apply_disqualifiers,
    composite,
    grade_from_score,
    load_dimension_adjustments,
    load_rubric_index,
)

SEED = 42
N_ITERATIONS = 10_000
CONCENTRATIONS = [20, 50, 100]

# Current weights (from index.json)
CURRENT_WEIGHTS = {
    "removal_type": 0.250,
    "additionality": 0.200,
    "permanence": 0.175,
    "mrv_grade": 0.200,
    "vintage_year": 0.100,
    "co_benefits": 0.000,
    "registry_methodology": 0.075,
}

# Non-zero dimensions (co_benefits excluded by safeguards-gate)
ACTIVE_DIMS = [d for d, w in CURRENT_WEIGHTS.items() if w > 0]
ACTIVE_WEIGHTS = [CURRENT_WEIGHTS[d] for d in ACTIVE_DIMS]

GRADE_ORDER = ["B", "BB", "BBB", "A", "AA", "AAA"]
GRADE_NUM = {g: i for i, g in enumerate(GRADE_ORDER)}


# ---------------------------------------------------------------------------
# Dirichlet sampling (pure Python)
# ---------------------------------------------------------------------------

def sample_gamma(alpha: float, rng: random.Random) -> float:
    """Sample from Gamma(alpha, 1) using Marsaglia and Tsang's method.

    For alpha >= 1: direct method.
    For alpha < 1: use the boost alpha' = alpha + 1, then scale.
    """
    if alpha < 1.0:
        # Boost: Gamma(alpha) = Gamma(alpha+1) * U^(1/alpha)
        g = sample_gamma(alpha + 1.0, rng)
        u = rng.random()
        return g * (u ** (1.0 / alpha))

    # Marsaglia and Tsang (2000)
    d = alpha - 1.0 / 3.0
    c = 1.0 / math.sqrt(9.0 * d)
    while True:
        while True:
            x = rng.gauss(0, 1)
            v = 1.0 + c * x
            if v > 0:
                break
        v = v * v * v
        u = rng.random()
        if u < 1.0 - 0.0331 * (x * x) * (x * x):
            return d * v
        if math.log(u) < 0.5 * x * x + d * (1.0 - v + math.log(v)):
            return d * v


def sample_dirichlet(alphas: list[float], rng: random.Random) -> list[float]:
    """Sample from Dirichlet(alphas) using Gamma sampling."""
    gammas = [sample_gamma(a, rng) for a in alphas]
    total = sum(gammas)
    if total == 0:
        # Fallback: uniform
        n = len(alphas)
        return [1.0 / n] * n
    return [g / total for g in gammas]


def sample_weight_vector(concentration: float, rng: random.Random) -> dict[str, float]:
    """Sample a weight vector from Dirichlet centered on current weights.

    co_benefits is forced to 0. Active dimensions are sampled from
    Dirichlet(alpha_i = w_i * concentration) and renormalized to sum to 1.
    """
    alphas = [w * concentration for w in ACTIVE_WEIGHTS]
    sampled = sample_dirichlet(alphas, rng)
    # Build full weight dict with co_benefits = 0
    weights = {}
    for dim, val in zip(ACTIVE_DIMS, sampled):
        weights[dim] = val
    weights["co_benefits"] = 0.0
    return weights


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_credit(
    credit: dict,
    weights: dict[str, float],
    grade_bands: list[dict],
    dq_spec: list[dict],
    dim_adjustments: dict,
) -> tuple[float, str]:
    """Score a single credit with given weights. Returns (composite, final_grade)."""
    base_scores = credit["scores"]
    adj_flags = credit.get("adjustments", [])
    scores = apply_dimension_adjustments(base_scores, adj_flags, dim_adjustments)
    comp = composite(scores, weights)
    grade = grade_from_score(comp, grade_bands)
    final, _ = apply_disqualifiers(grade, credit.get("disqualifiers", []), dq_spec)
    return comp, final


def compute_baseline(
    credits: list[dict],
    grade_bands: list[dict],
    dq_spec: list[dict],
    dim_adjustments: dict,
) -> dict[str, tuple[float, str]]:
    """Score all credits with baseline weights."""
    out = {}
    for c in credits:
        comp, grade = score_credit(c, CURRENT_WEIGHTS, grade_bands, dq_spec, dim_adjustments)
        out[c["id"]] = (comp, grade)
    return out


# ---------------------------------------------------------------------------
# Monte Carlo simulation
# ---------------------------------------------------------------------------

def run_simulation(
    credits: list[dict],
    grade_bands: list[dict],
    dq_spec: list[dict],
    dim_adjustments: dict,
    concentration: float,
    baseline: dict[str, tuple[float, str]],
    rng: random.Random,
) -> dict:
    """Run N_ITERATIONS of weight perturbation and collect statistics."""
    n_credits = len(credits)
    credit_ids = [c["id"] for c in credits]

    # Per-credit tracking
    grade_counts: dict[str, dict[str, int]] = {
        cid: {g: 0 for g in GRADE_ORDER} for cid in credit_ids
    }
    composites_all: dict[str, list[float]] = {cid: [] for cid in credit_ids}

    # For pairwise weight sensitivity: track (weight_value, composite) for
    # boundary-adjacent credits
    boundary_credits = []
    for cid in credit_ids:
        base_comp, base_grade = baseline[cid]
        # Check if within 5 points of a boundary
        grade_idx = GRADE_ORDER.index(base_grade)
        boundaries = [0, 30, 45, 60, 75, 90]
        for b in boundaries:
            if abs(base_comp - b) < 5:
                boundary_credits.append(cid)
                break

    weight_composite_pairs: dict[str, dict[str, list[tuple[float, float]]]] = {
        cid: {dim: [] for dim in ACTIVE_DIMS} for cid in boundary_credits
    }

    for iteration in range(N_ITERATIONS):
        w = sample_weight_vector(concentration, rng)
        for credit in credits:
            cid = credit["id"]
            comp, grade = score_credit(credit, w, grade_bands, dq_spec, dim_adjustments)
            grade_counts[cid][grade] += 1
            composites_all[cid].append(comp)

            if cid in weight_composite_pairs:
                for dim in ACTIVE_DIMS:
                    weight_composite_pairs[cid][dim].append((w[dim], comp))

    # Compute per-credit statistics
    credit_results = []
    for credit in credits:
        cid = credit["id"]
        base_comp, base_grade = baseline[cid]

        # Grade stability: fraction of iterations with same grade as baseline
        same_count = grade_counts[cid].get(base_grade, 0)
        stability = same_count / N_ITERATIONS

        # P(upgrade) and P(downgrade)
        base_idx = GRADE_ORDER.index(base_grade)
        p_upgrade = sum(
            grade_counts[cid][g]
            for g in GRADE_ORDER[base_idx + 1:]
        ) / N_ITERATIONS
        p_downgrade = sum(
            grade_counts[cid][g]
            for g in GRADE_ORDER[:base_idx]
        ) / N_ITERATIONS

        # Composite statistics
        comps = composites_all[cid]
        comp_mean = sum(comps) / len(comps)
        comp_std = math.sqrt(sum((c - comp_mean) ** 2 for c in comps) / len(comps))
        comp_min = min(comps)
        comp_max = max(comps)

        # Grade distribution
        grade_dist = {
            g: round(grade_counts[cid][g] / N_ITERATIONS, 4)
            for g in GRADE_ORDER
            if grade_counts[cid][g] > 0
        }

        credit_results.append({
            "id": cid,
            "name": credit["name"],
            "baseline_composite": round(base_comp, 2),
            "baseline_grade": base_grade,
            "grade_stability": round(stability, 4),
            "p_upgrade": round(p_upgrade, 4),
            "p_downgrade": round(p_downgrade, 4),
            "composite_mean": round(comp_mean, 2),
            "composite_std": round(comp_std, 2),
            "composite_min": round(comp_min, 2),
            "composite_max": round(comp_max, 2),
            "grade_distribution": grade_dist,
            "is_fragile": stability < 0.90,
        })

    # Pairwise weight sensitivity for boundary credits
    sensitivity_results = []
    for cid in boundary_credits:
        for dim in ACTIVE_DIMS:
            pairs = weight_composite_pairs[cid][dim]
            if len(pairs) < 10:
                continue
            # Pearson correlation between weight and composite
            ws = [p[0] for p in pairs]
            cs = [p[1] for p in pairs]
            r = _pearson(ws, cs)
            sensitivity_results.append({
                "credit_id": cid,
                "dimension": dim,
                "correlation": round(r, 4),
            })

    # Global robustness
    stabilities = [cr["grade_stability"] for cr in credit_results]
    global_robustness = sum(stabilities) / len(stabilities)

    fragile = [cr for cr in credit_results if cr["is_fragile"]]

    return {
        "concentration": concentration,
        "n_iterations": N_ITERATIONS,
        "global_robustness": round(global_robustness, 4),
        "n_fragile": len(fragile),
        "fragile_credits": [
            {"id": c["id"], "name": c["name"], "stability": c["grade_stability"],
             "baseline_grade": c["baseline_grade"]}
            for c in fragile
        ],
        "credit_results": credit_results,
        "weight_sensitivity": sensitivity_results,
    }


def _pearson(x: list[float], y: list[float]) -> float:
    """Pearson correlation coefficient."""
    n = len(x)
    if n < 2:
        return float("nan")
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    dx = math.sqrt(sum((xi - mx) ** 2 for xi in x))
    dy = math.sqrt(sum((yi - my) ** 2 for yi in y))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def results_to_markdown(all_runs: list[dict]) -> str:
    lines = [
        "# Monte Carlo Sensitivity Analysis",
        "",
        f"Seed: {SEED} | Iterations per concentration: {N_ITERATIONS:,}",
        "",
        "Weight vectors sampled from Dirichlet(alpha_i = w_i * concentration).",
        "co_benefits weight forced to 0 (safeguards-gate).",
        "",
        "## Global Robustness by Concentration",
        "",
        "| Concentration | Global robustness | Fragile credits (stability < 90%) |",
        "|:-------------:|:-----------------:|:---------------------------------:|",
    ]
    for run in all_runs:
        lines.append(
            f"| {run['concentration']} | {run['global_robustness']:.2%} | "
            f"{run['n_fragile']} / {len(run['credit_results'])} |"
        )

    # Default concentration detail
    default_run = next(r for r in all_runs if r["concentration"] == 50)

    lines.extend([
        "",
        "## Per-Credit Results (concentration=50)",
        "",
        "| ID | Name | Base grade | Stability | P(up) | P(down) | Comp mean +/- std |",
        "|----|------|-----------|-----------|-------|---------|-------------------|",
    ])
    for cr in sorted(default_run["credit_results"], key=lambda x: x["grade_stability"]):
        name = cr["name"][:35]
        flag = " **FRAGILE**" if cr["is_fragile"] else ""
        lines.append(
            f"| {cr['id']} | {name} | {cr['baseline_grade']} | "
            f"{cr['grade_stability']:.1%}{flag} | {cr['p_upgrade']:.1%} | "
            f"{cr['p_downgrade']:.1%} | {cr['composite_mean']:.1f} +/- {cr['composite_std']:.1f} |"
        )

    # Fragile credits detail
    fragile = default_run["fragile_credits"]
    if fragile:
        lines.extend([
            "",
            "## Fragile Credits (stability < 90%, concentration=50)",
            "",
        ])
        for fc in sorted(fragile, key=lambda x: x["stability"]):
            cr = next(c for c in default_run["credit_results"] if c["id"] == fc["id"])
            lines.append(f"### {fc['id']}: {fc['name']}")
            lines.append(f"- Baseline: {fc['baseline_grade']} (composite {cr['baseline_composite']})")
            lines.append(f"- Stability: {fc['stability']:.1%}")
            lines.append(f"- Grade distribution: {cr['grade_distribution']}")
            lines.append("")

    # Weight sensitivity
    sens = default_run.get("weight_sensitivity", [])
    if sens:
        lines.extend([
            "",
            "## Weight Sensitivity (boundary-adjacent credits, concentration=50)",
            "",
            "Pearson correlation between each weight value and composite score across MC iterations.",
            "",
            "| Credit | Dimension | Correlation |",
            "|--------|-----------|:-----------:|",
        ])
        for s in sorted(sens, key=lambda x: -abs(x["correlation"])):
            lines.append(f"| {s['credit_id']} | {s['dimension']} | {s['correlation']:+.3f} |")

    # Comparison across concentrations
    lines.extend([
        "",
        "## Concentration Comparison",
        "",
        "| Credit | Baseline | c=20 stability | c=50 stability | c=100 stability |",
        "|--------|----------|:--------------:|:--------------:|:---------------:|",
    ])
    # Build lookup
    stab_by_conc: dict[int, dict[str, float]] = {}
    for run in all_runs:
        lookup = {cr["id"]: cr["grade_stability"] for cr in run["credit_results"]}
        stab_by_conc[run["concentration"]] = lookup

    for cr in default_run["credit_results"]:
        cid = cr["id"]
        s20 = stab_by_conc.get(20, {}).get(cid, float("nan"))
        s50 = stab_by_conc.get(50, {}).get(cid, float("nan"))
        s100 = stab_by_conc.get(100, {}).get(cid, float("nan"))
        name = cr["name"][:30]
        lines.append(
            f"| {cid} {name} | {cr['baseline_grade']} | "
            f"{s20:.1%} | {s50:.1%} | {s100:.1%} |"
        )

    lines.extend([
        "",
        "## Notes",
        "",
        "- Concentration=20 is a wide prior (more weight variation); 100 is tight.",
        "- A 'fragile' credit has grade stability < 90%, meaning its grade changes in >10% of random weight samples.",
        "- Global robustness is the mean grade stability across all credits.",
        "- The safeguards-gate (co_benefits=0) is maintained in all samples.",
        "",
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    rubrics = load_rubric_index()
    grade_bands = rubrics["grades"]
    dq_spec = rubrics["disqualifiers"]
    dim_adjustments = load_dimension_adjustments()

    with CREDITS_PATH.open() as f:
        credits_data = json.load(f)
    credits = credits_data["credits"]

    print(f"Monte Carlo Sensitivity Analysis")
    print(f"  Credits: {len(credits)}")
    print(f"  Iterations per concentration: {N_ITERATIONS:,}")
    print(f"  Concentrations: {CONCENTRATIONS}")
    print(f"  Seed: {SEED}")
    print(f"  Active dimensions: {ACTIVE_DIMS}")
    print(f"  Current weights: {dict(zip(ACTIVE_DIMS, ACTIVE_WEIGHTS))}")
    print()

    # Compute baseline
    baseline = compute_baseline(credits, grade_bands, dq_spec, dim_adjustments)
    print("Baseline grades:")
    for cid, (comp, grade) in sorted(baseline.items()):
        print(f"  {cid}: {grade} ({comp:.2f})")
    print()

    # Run for each concentration
    all_runs = []
    for conc in CONCENTRATIONS:
        rng = random.Random(SEED)
        print(f"Running concentration={conc}...", end=" ", flush=True)
        result = run_simulation(
            credits, grade_bands, dq_spec, dim_adjustments,
            concentration=conc, baseline=baseline, rng=rng,
        )
        all_runs.append(result)
        print(
            f"done. Robustness={result['global_robustness']:.2%}, "
            f"fragile={result['n_fragile']}/{len(credits)}"
        )

    # Write outputs
    out_json = HERE / "monte_carlo_sensitivity_results.json"
    out_json.write_text(json.dumps(all_runs, indent=2))

    out_md = HERE / "monte_carlo_sensitivity_results.md"
    out_md.write_text(results_to_markdown(all_runs))

    print(f"\nWrote: {out_json}")
    print(f"Wrote: {out_md}")


if __name__ == "__main__":
    main()
