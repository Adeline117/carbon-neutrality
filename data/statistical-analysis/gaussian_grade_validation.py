#!/usr/bin/env python3
"""Validate Gaussian approximation for grade posteriors.

For 10 credits near grade boundaries, compare:
  1. Monte Carlo P(grade) from 10k per-dimension samples
  2. Gaussian CDF P(grade) from composite mean + variance

Reports max absolute error to verify the distributional scoring claim.

Usage:
    python3 gaussian_grade_validation.py
"""

import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent

SEED = 42
N_SAMPLES = 10_000

# Framework weights
WEIGHTS = {
    "removal_type": 0.250,
    "additionality": 0.200,
    "mrv_grade": 0.200,
    "permanence": 0.175,
    "vintage_year": 0.100,
    "registry_methodology": 0.075,
}

# Calibrated per-dimension standard deviations (from IRR study)
SIGMAS = {
    "removal_type": 4.7,
    "additionality": 9.7,
    "mrv_grade": 8.0,
    "permanence": 4.5,
    "vintage_year": 11.6,
    "registry_methodology": 12.6,
}

# Grade boundaries
GRADE_BOUNDS = {
    "AAA": (90, 100),
    "AA": (75, 90),
    "A": (60, 75),
    "BBB": (45, 60),
    "BB": (30, 45),
    "B": (0, 30),
}

GRADES_ORDERED = ["B", "BB", "BBB", "A", "AA", "AAA"]


def normal_cdf(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def gaussian_p_grade(mu, sigma, grade):
    lo, hi = GRADE_BOUNDS[grade]
    if sigma <= 0:
        return 1.0 if lo <= mu < hi else 0.0
    p_below_hi = normal_cdf((hi - mu) / sigma) if hi < 100 else 1.0
    p_below_lo = normal_cdf((lo - mu) / sigma) if lo > 0 else 0.0
    return max(0.0, p_below_hi - p_below_lo)


def compute_composite(scores):
    return sum(WEIGHTS[d] * scores[d] for d in WEIGHTS)


def compute_composite_variance():
    return sum(WEIGHTS[d]**2 * SIGMAS[d]**2 for d in WEIGHTS)


def to_grade(composite):
    for g in reversed(GRADES_ORDERED):
        if composite >= GRADE_BOUNDS[g][0]:
            return g
    return "B"


# 10 boundary credits: designed to sit near grade thresholds
BOUNDARY_CREDITS = [
    {
        "name": "Near-AAA (composite ~89)",
        "scores": {"removal_type": 95, "additionality": 88, "permanence": 92, "mrv_grade": 85, "vintage_year": 80, "registry_methodology": 78}
    },
    {
        "name": "Near-AA/AAA boundary (composite ~90)",
        "scores": {"removal_type": 96, "additionality": 90, "permanence": 93, "mrv_grade": 86, "vintage_year": 82, "registry_methodology": 80}
    },
    {
        "name": "Near-AA (composite ~76)",
        "scores": {"removal_type": 82, "additionality": 75, "permanence": 78, "mrv_grade": 72, "vintage_year": 65, "registry_methodology": 70}
    },
    {
        "name": "Near-A/AA boundary (composite ~75)",
        "scores": {"removal_type": 80, "additionality": 74, "permanence": 76, "mrv_grade": 71, "vintage_year": 64, "registry_methodology": 68}
    },
    {
        "name": "Near-A (composite ~61)",
        "scores": {"removal_type": 68, "additionality": 62, "permanence": 58, "mrv_grade": 58, "vintage_year": 50, "registry_methodology": 55}
    },
    {
        "name": "Near-BBB/A boundary (composite ~60)",
        "scores": {"removal_type": 66, "additionality": 60, "permanence": 56, "mrv_grade": 57, "vintage_year": 50, "registry_methodology": 55}
    },
    {
        "name": "Near-BBB (composite ~46)",
        "scores": {"removal_type": 50, "additionality": 48, "permanence": 42, "mrv_grade": 45, "vintage_year": 40, "registry_methodology": 42}
    },
    {
        "name": "Near-BB/BBB boundary (composite ~45)",
        "scores": {"removal_type": 48, "additionality": 46, "permanence": 40, "mrv_grade": 44, "vintage_year": 40, "registry_methodology": 42}
    },
    {
        "name": "Near-BB (composite ~31)",
        "scores": {"removal_type": 30, "additionality": 32, "permanence": 28, "mrv_grade": 35, "vintage_year": 30, "registry_methodology": 28}
    },
    {
        "name": "Near-B/BB boundary (composite ~30)",
        "scores": {"removal_type": 28, "additionality": 30, "permanence": 26, "mrv_grade": 33, "vintage_year": 30, "registry_methodology": 28}
    },
]


def main():
    rng = random.Random(SEED)
    composite_sigma = math.sqrt(compute_composite_variance())

    results = []
    max_abs_error = 0.0

    for credit in BOUNDARY_CREDITS:
        scores = credit["scores"]
        mu = compute_composite(scores)
        point_grade = to_grade(mu)

        # Monte Carlo: sample per-dimension scores, compute composite, tally grades
        mc_counts = {g: 0 for g in GRADES_ORDERED}
        for _ in range(N_SAMPLES):
            sampled = {}
            for dim in WEIGHTS:
                s = rng.gauss(scores[dim], SIGMAS[dim])
                s = max(0, min(100, s))  # Clamp to [0, 100]
                sampled[dim] = s
            comp = compute_composite(sampled)
            mc_counts[to_grade(comp)] += 1

        mc_probs = {g: mc_counts[g] / N_SAMPLES for g in GRADES_ORDERED}

        # Gaussian CDF approximation
        gauss_probs = {g: gaussian_p_grade(mu, composite_sigma, g) for g in GRADES_ORDERED}

        # Compute errors
        errors = {g: abs(mc_probs[g] - gauss_probs[g]) for g in GRADES_ORDERED}
        max_error_this = max(errors.values())
        max_abs_error = max(max_abs_error, max_error_this)

        results.append({
            "credit": credit["name"],
            "composite_mu": round(mu, 1),
            "point_grade": point_grade,
            "mc_probs": {g: round(p, 4) for g, p in mc_probs.items()},
            "gaussian_probs": {g: round(p, 4) for g, p in gauss_probs.items()},
            "max_abs_error": round(max_error_this, 4),
            "max_error_grade": max(errors, key=errors.get),
        })

    output = {
        "test": "Gaussian approximation validation for grade posteriors",
        "method": f"Monte Carlo ({N_SAMPLES:,} samples per credit) vs Gaussian CDF on 10 boundary credits",
        "composite_sigma": round(composite_sigma, 2),
        "n_credits": len(results),
        "max_absolute_error_across_all": round(max_abs_error, 4),
        "mean_max_error": round(sum(r["max_abs_error"] for r in results) / len(results), 4),
        "credits": results,
        "verdict": "",
        "seed": SEED,
        "n_samples": N_SAMPLES
    }

    if max_abs_error < 0.05:
        output["verdict"] = f"EXCELLENT. Max absolute error = {max_abs_error:.4f} (< 5%). Gaussian CDF is an accurate approximation for grade posteriors, even at grade boundaries."
    elif max_abs_error < 0.10:
        output["verdict"] = f"GOOD. Max absolute error = {max_abs_error:.4f} (< 10%). Gaussian CDF is a reasonable approximation; slight deviations at boundaries."
    else:
        output["verdict"] = f"MODERATE. Max absolute error = {max_abs_error:.4f} (>= 10%). Gaussian CDF shows notable deviations at grade boundaries. Consider reporting Monte Carlo posteriors for boundary credits."

    out_path = HERE / "gaussian_grade_validation.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Composite sigma: {composite_sigma:.2f}")
    print(f"\n{'Credit':<40} {'mu':>6} {'Grade':>6} {'MaxErr':>8} {'ErrGrade':>10}")
    print("-" * 75)
    for r in results:
        print(f"{r['credit']:<40} {r['composite_mu']:>6.1f} {r['point_grade']:>6} {r['max_abs_error']:>8.4f} {r['max_error_grade']:>10}")

    print(f"\nMax absolute error across all: {max_abs_error:.4f}")
    print(f"Mean max error: {output['mean_max_error']:.4f}")
    print(f"Verdict: {output['verdict']}")
    print(f"\nWrote: {out_path}")


if __name__ == "__main__":
    main()
