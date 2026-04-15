#!/usr/bin/env python3
"""
Process Best-Worst Scaling (BWS) expert panel responses and integrate into
the carbon credit quality framework.

Takes a CSV of expert BWS responses (from the v2-BWS questionnaire,
docs/expert-questionnaire-v2-bws.md Section 2.1), computes BWS scores,
derives new weights, recomputes all 29 pilot credit composites, and
reports grade changes, flips, and rank correlation with BeZero.

Standard library only: csv, json, math, statistics, random.

Usage:
    python3 process_bws.py                              # uses sample_responses.csv
    python3 process_bws.py --input path/to/responses.csv
    python3 process_bws.py --input responses.csv --bootstrap 10000

Input CSV format:
    See sample_responses.csv for the expected column layout. Each row is
    one respondent. Columns are:
        respondent_id, name, affiliation, role, years_vcm,
        set01_most, set01_least, set02_most, set02_least, ..., set15_most, set15_least

    The set columns use dimension codes:
        removal_type, additionality, permanence, mrv_grade, vintage_year, registry_methodology

Output:
    data/expert-panel/bws_results.md
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUBRICS = ROOT / "data" / "scoring-rubrics"
PILOT_CREDITS = ROOT / "data" / "pilot-scoring" / "credits.json"

# -----------------------------------------------------------------------
# BWS design: BIBD(6, 15, 10, 4, 6) — all C(6,4) subsets
# Each set is a tuple of 4 dimension codes present in that set.
# -----------------------------------------------------------------------
DIMENSIONS = [
    "removal_type",
    "additionality",
    "permanence",
    "mrv_grade",
    "vintage_year",
    "registry_methodology",
]

# The 15 choice sets from the questionnaire (Appendix B), using 1-indexed
# dimension numbers mapped to codes.  Sets match the questionnaire order.
CHOICE_SETS = [
    ("removal_type", "additionality", "permanence", "mrv_grade"),            # Set 1
    ("removal_type", "additionality", "permanence", "vintage_year"),         # Set 2
    ("removal_type", "additionality", "permanence", "registry_methodology"), # Set 3
    ("removal_type", "additionality", "mrv_grade", "vintage_year"),          # Set 4
    ("removal_type", "additionality", "mrv_grade", "registry_methodology"),  # Set 5
    ("removal_type", "additionality", "vintage_year", "registry_methodology"),  # Set 6
    ("removal_type", "permanence", "mrv_grade", "vintage_year"),             # Set 7
    ("removal_type", "permanence", "mrv_grade", "registry_methodology"),     # Set 8
    ("removal_type", "permanence", "vintage_year", "registry_methodology"),  # Set 9
    ("removal_type", "mrv_grade", "vintage_year", "registry_methodology"),   # Set 10
    ("additionality", "permanence", "mrv_grade", "vintage_year"),            # Set 11
    ("additionality", "permanence", "mrv_grade", "registry_methodology"),    # Set 12
    ("additionality", "permanence", "vintage_year", "registry_methodology"), # Set 13
    ("additionality", "mrv_grade", "vintage_year", "registry_methodology"),  # Set 14
    ("permanence", "mrv_grade", "vintage_year", "registry_methodology"),     # Set 15
]

CURRENT_WEIGHTS = {
    "removal_type": 0.250,
    "additionality": 0.200,
    "permanence": 0.175,
    "mrv_grade": 0.200,
    "vintage_year": 0.100,
    "registry_methodology": 0.075,
}

GRADE_ORDER = ["B", "BB", "BBB", "A", "AA", "AAA"]
GRADE_INDEX = {g: i for i, g in enumerate(GRADE_ORDER)}


# -----------------------------------------------------------------------
# Scoring helpers (replicated from score.py to avoid import coupling)
# -----------------------------------------------------------------------

def load_rubric_index() -> dict:
    with (RUBRICS / "index.json").open() as f:
        return json.load(f)


def load_credits() -> list[dict]:
    with PILOT_CREDITS.open() as f:
        data = json.load(f)
    return data["credits"]


def grade_from_score(score: float, bands: list[dict]) -> str:
    for band in bands:
        if score >= band["min"]:
            return band["grade"]
    return "B"


def cap_grade(grade: str, cap: str) -> str:
    if GRADE_INDEX[grade] <= GRADE_INDEX[cap]:
        return grade
    return cap


def apply_disqualifiers(grade: str, flags: list[str], dq_spec: list[dict]) -> str:
    final = grade
    for dq in dq_spec:
        if dq["id"] in flags:
            new = cap_grade(final, dq["grade_cap"])
            if new != final:
                final = new
    return final


def composite(scores: dict, weights: dict) -> float:
    return sum(scores.get(d, 0) * weights.get(d, 0) for d in weights)


def score_all_credits(credits: list[dict], weights: dict, bands: list[dict],
                      dq_spec: list[dict]) -> list[dict]:
    """Score all credits with a given weight vector.  Returns list of
    {id, name, composite, grade} dicts."""
    results = []
    for c in credits:
        comp = composite(c["scores"], weights)
        nominal = grade_from_score(comp, bands)
        dq_flags = [f for f in c.get("disqualifiers", [])
                    if f in {dq["id"] for dq in dq_spec}]
        final = apply_disqualifiers(nominal, dq_flags, dq_spec)
        results.append({
            "id": c["id"],
            "name": c["name"],
            "composite": round(comp, 2),
            "grade": final,
        })
    return results


# -----------------------------------------------------------------------
# BWS computation
# -----------------------------------------------------------------------

def parse_responses(csv_path: Path) -> list[dict]:
    """Parse expert BWS response CSV. Returns list of respondent dicts."""
    respondents = []
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            resp = {
                "id": row.get("respondent_id", ""),
                "name": row.get("name", ""),
                "affiliation": row.get("affiliation", ""),
                "role": row.get("role", ""),
                "years_vcm": row.get("years_vcm", ""),
                "choices": [],
            }
            for s in range(1, 16):
                most_col = f"set{s:02d}_most"
                least_col = f"set{s:02d}_least"
                most = row.get(most_col, "").strip()
                least = row.get(least_col, "").strip()
                resp["choices"].append({"set": s, "most": most, "least": least})
            respondents.append(resp)
    return respondents


def validate_responses(respondents: list[dict]) -> list[str]:
    """Validate responses. Returns list of warning strings."""
    warnings = []
    for resp in respondents:
        rid = resp["id"]
        for choice in resp["choices"]:
            s = choice["set"]
            most = choice["most"]
            least = choice["least"]
            valid_dims = set(CHOICE_SETS[s - 1])

            if most and most not in valid_dims:
                warnings.append(
                    f"Respondent {rid}, set {s}: MOST '{most}' not in set {valid_dims}")
            if least and least not in valid_dims:
                warnings.append(
                    f"Respondent {rid}, set {s}: LEAST '{least}' not in set {valid_dims}")
            if most and least and most == least:
                warnings.append(
                    f"Respondent {rid}, set {s}: MOST == LEAST ('{most}')")
            if not most or not least:
                warnings.append(
                    f"Respondent {rid}, set {s}: missing MOST or LEAST")
    return warnings


def compute_bws_scores(respondents: list[dict]) -> dict:
    """Compute BWS scores per respondent and aggregated.

    Returns {
        "individual": {resp_id: {dim: score}},
        "aggregate": {dim: mean_score},
        "aggregate_std": {dim: std_score},
        "n": int,
    }
    """
    individual = {}

    for resp in respondents:
        rid = resp["id"]
        counts = {d: {"best": 0, "worst": 0} for d in DIMENSIONS}

        for choice in resp["choices"]:
            most = choice["most"]
            least = choice["least"]
            if most in counts:
                counts[most]["best"] += 1
            if least in counts:
                counts[least]["worst"] += 1

        scores = {d: counts[d]["best"] - counts[d]["worst"] for d in DIMENSIONS}
        individual[rid] = scores

    # Aggregate
    n = len(respondents)
    aggregate = {}
    aggregate_std = {}
    for d in DIMENSIONS:
        vals = [individual[rid][d] for rid in individual]
        aggregate[d] = sum(vals) / n if n > 0 else 0
        aggregate_std[d] = statistics.stdev(vals) if n > 1 else 0

    return {
        "individual": individual,
        "aggregate": aggregate,
        "aggregate_std": aggregate_std,
        "n": n,
    }


def bws_to_weights(aggregate_scores: dict[str, float]) -> dict[str, float]:
    """Convert aggregate BWS scores to normalized weights.

    Uses the shift-and-normalize method from Appendix A.3 of the
    questionnaire:
        shifted(i) = BWS_agg(i) - min_j(BWS_agg(j))
        weight(i) = shifted(i) / sum_j(shifted(j))

    If all scores are equal, returns uniform weights.
    """
    min_score = min(aggregate_scores.values())
    shifted = {d: aggregate_scores[d] - min_score for d in DIMENSIONS}

    total = sum(shifted.values())
    if total == 0:
        # All dimensions tied — return uniform
        return {d: 1.0 / len(DIMENSIONS) for d in DIMENSIONS}

    return {d: shifted[d] / total for d in DIMENSIONS}


def bootstrap_ci(respondents: list[dict], n_boot: int = 10000,
                 alpha: float = 0.05) -> dict[str, tuple[float, float]]:
    """Bootstrap 95% CI for each dimension's BWS weight.

    Resamples respondents with replacement, re-derives weights each time,
    and reports the (alpha/2, 1-alpha/2) percentiles.
    """
    boot_weights = {d: [] for d in DIMENSIONS}

    for _ in range(n_boot):
        sample = random.choices(respondents, k=len(respondents))
        bws = compute_bws_scores(sample)
        w = bws_to_weights(bws["aggregate"])
        for d in DIMENSIONS:
            boot_weights[d].append(w[d])

    ci = {}
    for d in DIMENSIONS:
        boot_weights[d].sort()
        lo_idx = int(n_boot * alpha / 2)
        hi_idx = int(n_boot * (1 - alpha / 2)) - 1
        ci[d] = (boot_weights[d][lo_idx], boot_weights[d][hi_idx])

    return ci


def chi_squared_test(bws_weights: dict[str, float],
                     current_weights: dict[str, float],
                     n: int) -> tuple[float, float]:
    """Chi-squared goodness-of-fit test (Appendix A.7 of questionnaire).

    H0: BWS weight vector == current weight vector.
    Returns (chi2, p_approx).  p_approx uses the normal approx to chi2(5).
    """
    chi2 = n * sum(
        (bws_weights[d] - current_weights[d]) ** 2 / current_weights[d]
        for d in DIMENSIONS
        if current_weights[d] > 0
    )
    # Degrees of freedom = 6 - 1 = 5
    df = len(DIMENSIONS) - 1
    # Approximate p-value using Wilson-Hilferty normal approximation
    z = ((chi2 / df) ** (1.0 / 3.0) - (1 - 2.0 / (9.0 * df))) / math.sqrt(
        2.0 / (9.0 * df))
    p = 1 - 0.5 * (1 + math.erf(z / math.sqrt(2)))
    return chi2, max(0, p)


def spearman_rank(x: list[float], y: list[float]) -> float:
    """Compute Spearman rank correlation between two lists."""
    n = len(x)
    if n < 2:
        return float("nan")

    def ranks(vals):
        sorted_vals = sorted(enumerate(vals), key=lambda p: p[1])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and sorted_vals[j + 1][1] == sorted_vals[j][1]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[sorted_vals[k][0]] = avg_rank
            i = j + 1
        return r

    rx = ranks(x)
    ry = ranks(y)
    d_sq = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return 1.0 - 6.0 * d_sq / (n * (n * n - 1))


# -----------------------------------------------------------------------
# Reporting
# -----------------------------------------------------------------------

def generate_report(respondents: list[dict], bws_result: dict,
                    bws_weights: dict[str, float],
                    bootstrap_cis: dict[str, tuple[float, float]],
                    chi2: float, p_value: float,
                    baseline_results: list[dict],
                    new_results: list[dict],
                    n_boot: int) -> str:
    """Generate the bws_results.md report."""
    lines = []
    lines.append("# Expert BWS Weight Calibration Results")
    lines.append("")
    lines.append(f"*N = {bws_result['n']} respondents, {n_boot} bootstrap resamples.*")
    lines.append("")

    # Section 1: Raw BWS scores
    lines.append("## 1. Aggregate BWS Scores")
    lines.append("")
    lines.append("| Dimension | BWS Score (mean) | BWS Score (std) | Standardized |")
    lines.append("|-----------|----------------:|----------------:|-------------:|")
    for d in DIMENSIONS:
        agg = bws_result["aggregate"][d]
        std = bws_result["aggregate_std"][d]
        standardized = agg / 10.0  # max possible per dimension is 10
        lines.append(f"| {d} | {agg:+.2f} | {std:.2f} | {standardized:+.3f} |")
    lines.append("")

    # Section 2: Weight comparison
    lines.append("## 2. Weight Comparison")
    lines.append("")
    lines.append("| Dimension | Current weight | BWS weight | 95% CI | Delta |")
    lines.append("|-----------|---------------:|-----------:|-------:|------:|")
    for d in DIMENSIONS:
        cur = CURRENT_WEIGHTS[d]
        bws = bws_weights[d]
        ci_lo, ci_hi = bootstrap_cis[d]
        delta = bws - cur
        lines.append(
            f"| {d} | {cur:.3f} | {bws:.3f} | [{ci_lo:.3f}, {ci_hi:.3f}] | {delta:+.3f} |")
    lines.append("")

    # Ordering comparison
    current_order = sorted(DIMENSIONS, key=lambda d: -CURRENT_WEIGHTS[d])
    bws_order = sorted(DIMENSIONS, key=lambda d: -bws_weights[d])
    lines.append(f"**Current weight ordering:** {' > '.join(current_order)}")
    lines.append("")
    lines.append(f"**BWS-derived ordering:** {' > '.join(bws_order)}")
    lines.append("")

    # Spearman on orderings
    cur_ranks = [CURRENT_WEIGHTS[d] for d in DIMENSIONS]
    bws_ranks = [bws_weights[d] for d in DIMENSIONS]
    rho = spearman_rank(cur_ranks, bws_ranks)
    lines.append(f"**Weight-ordering Spearman rho:** {rho:+.3f}")
    lines.append("")

    # Chi-squared test
    lines.append("## 3. Chi-Squared Goodness-of-Fit Test")
    lines.append("")
    lines.append(f"- chi2 = {chi2:.3f} (df = {len(DIMENSIONS) - 1})")
    lines.append(f"- p = {p_value:.4f}")
    if p_value > 0.05:
        lines.append("- **Result: FAIL TO REJECT H0** -- BWS weights are not "
                      "significantly different from current weights (p > 0.05).")
        lines.append("- **Decision rule (A.8 case 1):** Retain current weights.")
    elif rho > 0.8:
        lines.append("- **Result: REJECT H0** -- BWS weights differ significantly "
                      "from current weights.")
        lines.append("- **Decision rule (A.8 case 2):** Rank ordering matches; "
                      "adopt BWS-derived weights.")
    else:
        lines.append("- **Result: REJECT H0 and ordering differs.**")
        lines.append("- **Decision rule (A.8 case 3):** Investigate dimension-by-"
                      "dimension; adopt BWS weights only where the 95% CI excludes "
                      "the current weight.")
    lines.append("")

    # Section 4: Grade impact
    lines.append("## 4. Grade Impact Analysis")
    lines.append("")

    baseline_grades = {r["id"]: r for r in baseline_results}
    flips = []
    for r in new_results:
        old = baseline_grades[r["id"]]
        if r["grade"] != old["grade"]:
            flips.append({
                "id": r["id"],
                "name": r["name"],
                "old_grade": old["grade"],
                "new_grade": r["grade"],
                "old_composite": old["composite"],
                "new_composite": r["composite"],
            })

    lines.append(f"**Grade changes:** {len(flips)} of {len(new_results)} credits")
    lines.append("")

    if flips:
        lines.append("| Credit | Old grade | New grade | Old composite | New composite |")
        lines.append("|--------|----------|----------|-------------:|-------------:|")
        for flip in flips:
            lines.append(
                f"| {flip['id']} {flip['name'][:30]} | {flip['old_grade']} | "
                f"{flip['new_grade']} | {flip['old_composite']} | {flip['new_composite']} |")
        lines.append("")
    else:
        lines.append("No grade changes under BWS-derived weights.")
        lines.append("")

    # Rank correlation with BeZero
    lines.append("## 5. Rank Correlation")
    lines.append("")
    baseline_comps = [r["composite"] for r in sorted(baseline_results, key=lambda r: r["id"])]
    new_comps = [r["composite"] for r in sorted(new_results, key=lambda r: r["id"])]
    internal_rho = spearman_rank(baseline_comps, new_comps)
    lines.append(f"**Internal Spearman (current vs BWS weights):** {internal_rho:+.3f}")
    lines.append("")
    lines.append("*Note: Rank correlation with BeZero cannot be computed until the "
                 "n=27 overlap dataset is re-scored with the new weights. Run "
                 "`score.py` with the updated index.json to generate the comparison.*")
    lines.append("")

    # Section 6: Per-respondent consistency
    lines.append("## 6. Per-Respondent BWS Score Ranges")
    lines.append("")
    lines.append("| Respondent | Most-important dim | Least-important dim | Score range |")
    lines.append("|------------|-------------------|--------------------|-----------:|")
    for resp in respondents:
        rid = resp["id"]
        scores = bws_result["individual"][rid]
        best_dim = max(scores, key=scores.get)
        worst_dim = min(scores, key=scores.get)
        score_range = scores[best_dim] - scores[worst_dim]
        lines.append(f"| {rid} | {best_dim} ({scores[best_dim]:+d}) | "
                     f"{worst_dim} ({scores[worst_dim]:+d}) | {score_range} |")
    lines.append("")

    # Section 7: Decision summary
    lines.append("## 7. Decision Summary for v0.6")
    lines.append("")
    lines.append("| Check | Status |")
    lines.append("|-------|--------|")
    lines.append(f"| N >= 20 (stable count analysis) | {'PASS' if bws_result['n'] >= 20 else 'BELOW TARGET'} (N={bws_result['n']}) |")
    lines.append(f"| N >= 30 (MNL estimation) | {'PASS' if bws_result['n'] >= 30 else 'COUNT ONLY'} (N={bws_result['n']}) |")
    lines.append(f"| Chi-squared p > 0.05 | {'YES' if p_value > 0.05 else 'NO'} (p={p_value:.4f}) |")
    lines.append(f"| Rank ordering matches | {'YES' if rho > 0.8 else 'NO'} (rho={rho:+.3f}) |")
    lines.append(f"| Grade flips | {len(flips)} |")
    lines.append(f"| Max weight delta | {max(abs(bws_weights[d] - CURRENT_WEIGHTS[d]) for d in DIMENSIONS):.3f} |")
    lines.append("")

    return "\n".join(lines)


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main() -> None:
    # Parse arguments
    input_path = HERE / "sample_responses.csv"
    n_boot = 10000

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--input" and i + 1 < len(args):
            input_path = Path(args[i + 1]).resolve()
            i += 2
        elif args[i] == "--bootstrap" and i + 1 < len(args):
            n_boot = int(args[i + 1])
            i += 2
        else:
            print(f"Unknown argument: {args[i]}")
            i += 1

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        print("Run with --input <path> or create sample_responses.csv")
        sys.exit(1)

    print(f"Loading responses from {input_path}")
    respondents = parse_responses(input_path)
    print(f"Loaded {len(respondents)} respondents")

    # Validate
    warnings = validate_responses(respondents)
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")

    # Compute BWS scores
    bws_result = compute_bws_scores(respondents)
    print("\nAggregate BWS scores:")
    for d in DIMENSIONS:
        print(f"  {d:22s}  {bws_result['aggregate'][d]:+.2f}")

    # Derive weights
    bws_weights = bws_to_weights(bws_result["aggregate"])
    print("\nBWS-derived weights:")
    for d in DIMENSIONS:
        delta = bws_weights[d] - CURRENT_WEIGHTS[d]
        print(f"  {d:22s}  {bws_weights[d]:.3f}  (current: {CURRENT_WEIGHTS[d]:.3f}, delta: {delta:+.3f})")

    # Bootstrap CIs
    print(f"\nBootstrapping {n_boot} resamples for 95% CIs...")
    random.seed(42)
    bootstrap_cis = bootstrap_ci(respondents, n_boot)
    for d in DIMENSIONS:
        lo, hi = bootstrap_cis[d]
        print(f"  {d:22s}  [{lo:.3f}, {hi:.3f}]")

    # Chi-squared test
    chi2, p_value = chi_squared_test(bws_weights, CURRENT_WEIGHTS, bws_result["n"])
    print(f"\nChi-squared test: chi2={chi2:.3f}, p={p_value:.4f}")

    # Load framework data
    rubric = load_rubric_index()
    bands = rubric["grades"]
    dq_spec = rubric["disqualifiers"]
    credits = load_credits()

    # Score with current weights (baseline)
    baseline_results = score_all_credits(credits, CURRENT_WEIGHTS, bands, dq_spec)

    # Score with BWS-derived weights (ensuring co_benefits stays at 0)
    new_weights = dict(bws_weights)
    # The BWS questionnaire only covers the 6 active dimensions.
    # co_benefits must stay at 0.0 (safeguards-gate).
    # Normalize the 6 BWS dimensions to sum to 1.0.
    total = sum(new_weights.values())
    if total > 0:
        new_weights = {d: v / total for d, v in new_weights.items()}

    # Build full 7-dimension weight dict for composite calculation
    full_weights = dict(new_weights)
    full_weights["co_benefits"] = 0.0

    new_results = score_all_credits(credits, full_weights, bands, dq_spec)

    # Also need current full weights for baseline
    full_current = dict(CURRENT_WEIGHTS)
    full_current["co_benefits"] = 0.0
    baseline_results = score_all_credits(credits, full_current, bands, dq_spec)

    # Generate report
    report = generate_report(
        respondents, bws_result, bws_weights, bootstrap_cis,
        chi2, p_value, baseline_results, new_results, n_boot)

    out_path = HERE / "bws_results.md"
    out_path.write_text(report)
    print(f"\nWrote report to {out_path}")

    # Print summary
    flips = sum(1 for b, n in zip(baseline_results, new_results)
                if b["grade"] != n["grade"])
    print(f"\nSummary: {flips} grade changes out of {len(baseline_results)} credits")


if __name__ == "__main__":
    main()
