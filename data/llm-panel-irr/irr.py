#!/usr/bin/env python3
"""Inter-rater reliability analysis for the v0.5 LLM panel study.

Reads the 3 raters' scored JSON from raw/<model>/scored.json, joins them
with the author's v0.4.1 scores from ../pilot-scoring/credits.json, and
computes:

  - Per-dimension pairwise absolute agreement (mean |score_a - score_b|)
  - Per-dimension Pearson correlation across the panel (rough IRR)
  - Grade-level Cohen's kappa for each rater pair
  - Fleiss' kappa across the full panel for grade level
  - ICC(2,k) on the continuous composite
  - Panel-median vs author exact-grade agreement rate
  - Fragility validation for C004, C011, C014
  - Disqualifier recall for C026-C029

Pure Python, no external dependencies.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUBRICS = ROOT / "data" / "scoring-rubrics"
AUTHOR_CREDITS = ROOT / "data" / "pilot-scoring" / "credits.json"
RAW = HERE / "raw"

GRADES = ["B", "BB", "BBB", "A", "AA", "AAA"]
GRADE_INDEX = {g: i for i, g in enumerate(GRADES)}

DIMS = [
    "removal_type",
    "additionality",
    "permanence",
    "mrv_grade",
    "vintage_year",
    "co_benefits",
    "registry_methodology",
]

RATERS = ["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5"]

# ---------- helpers ----------

def load_rubric() -> dict:
    return json.loads((RUBRICS / "index.json").read_text())


def grade_from_composite(composite: float, bands: list[dict]) -> str:
    for band in bands:
        if composite >= band["min"]:
            return band["grade"]
    return "B"


def apply_dq_cap(grade: str, flags: list[str], dq_spec: list[dict]) -> str:
    final = grade
    caps = {dq["id"]: dq["grade_cap"] for dq in dq_spec}
    for f in flags:
        if f in caps:
            cap = caps[f]
            if GRADE_INDEX[final] > GRADE_INDEX[cap]:
                final = cap
    return final


def composite_for(scores: dict, weights: dict) -> float:
    return sum(scores[d] * weights[d] for d in DIMS)


def pearson(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    mx = sum(x) / len(x)
    my = sum(y) / len(y)
    num = sum((x[i] - mx) * (y[i] - my) for i in range(len(x)))
    dx = math.sqrt(sum((a - mx) ** 2 for a in x))
    dy = math.sqrt(sum((a - my) ** 2 for a in y))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


def cohens_kappa(a: list[int], b: list[int], k: int) -> float:
    """Cohen's kappa for categorical agreement. Categories are 0..k-1."""
    n = len(a)
    if n == 0:
        return float("nan")
    # Observed agreement
    po = sum(1 for i in range(n) if a[i] == b[i]) / n
    # Expected by chance
    pa = [a.count(c) / n for c in range(k)]
    pb = [b.count(c) / n for c in range(k)]
    pe = sum(pa[c] * pb[c] for c in range(k))
    if pe == 1:
        return 1.0
    return (po - pe) / (1 - pe)


def fleiss_kappa(matrix: list[list[int]], k: int) -> float:
    """Fleiss' kappa. matrix[i][c] = number of raters who put item i in category c."""
    n = len(matrix)
    if n == 0:
        return float("nan")
    m = sum(matrix[0])  # raters per item
    if m < 2:
        return float("nan")

    p_j = [sum(matrix[i][c] for i in range(n)) / (n * m) for c in range(k)]
    P_i = [
        (sum(matrix[i][c] ** 2 for c in range(k)) - m) / (m * (m - 1))
        for i in range(n)
    ]
    P_bar = sum(P_i) / n
    P_e = sum(p ** 2 for p in p_j)
    if P_e == 1:
        return 1.0
    return (P_bar - P_e) / (1 - P_e)


def icc_2k(ratings: list[list[float]]) -> float:
    """ICC(2,k) — two-way random effects, mean of k raters, consistency.

    ratings[i] is the list of k rater scores for item i.
    Uses the formulation: ICC = (MSR - MSE) / MSR
    where MSR = between-subjects mean square and MSE = error mean square.
    """
    n = len(ratings)
    if n < 2:
        return float("nan")
    k = len(ratings[0])
    grand_mean = sum(sum(r) for r in ratings) / (n * k)

    subject_means = [sum(r) / k for r in ratings]
    rater_means = [sum(ratings[i][j] for i in range(n)) / n for j in range(k)]

    SSR = k * sum((sm - grand_mean) ** 2 for sm in subject_means)
    SSC = n * sum((rm - grand_mean) ** 2 for rm in rater_means)
    SST = sum((ratings[i][j] - grand_mean) ** 2 for i in range(n) for j in range(k))
    SSE = SST - SSR - SSC

    MSR = SSR / (n - 1)
    MSC = SSC / (k - 1) if k > 1 else float("nan")
    MSE = SSE / ((n - 1) * (k - 1)) if (n > 1 and k > 1) else float("nan")

    if MSR == 0:
        return float("nan")
    return (MSR - MSE) / MSR


# ---------- load data ----------

def load_rater_scores() -> dict[str, dict[str, dict]]:
    """Returns {rater: {credit_id: {dim_scores + disqualifiers}}}"""
    out: dict[str, dict[str, dict]] = {}
    for model in RATERS:
        path = RAW / model / "scored.json"
        if not path.exists():
            print(f"Warning: {model} scored.json missing")
            continue
        data = json.loads(path.read_text())
        out[model] = {c["id"]: c for c in data["credits"]}
    return out


def load_author_scores() -> dict[str, dict]:
    data = json.loads(AUTHOR_CREDITS.read_text())
    return {c["id"]: c for c in data["credits"]}


# ---------- main analysis ----------

def main() -> None:
    rubric = load_rubric()
    weights = {d["id"]: d["weight"] for d in rubric["dimensions"]}
    bands = rubric["grades"]
    dq_spec = rubric["disqualifiers"]

    rater_scores = load_rater_scores()
    author_scores = load_author_scores()

    credit_ids = sorted(author_scores.keys())
    all_raters = ["author"] + RATERS

    # Build per-dimension score matrices (credit × rater)
    dim_matrices: dict[str, list[list[float]]] = {d: [] for d in DIMS}
    composites: list[list[float]] = []
    grades: list[list[str]] = []
    disqualifiers: dict[str, list[set]] = {r: [] for r in all_raters}

    for cid in credit_ids:
        auth = author_scores[cid]
        row_dims = {}
        row_comp = []
        row_grade = []
        for rater in all_raters:
            if rater == "author":
                scores = auth["scores"]
                dqs = set(auth.get("disqualifiers", []))
            else:
                c = rater_scores.get(rater, {}).get(cid)
                if c is None:
                    scores = {d: 0 for d in DIMS}
                    dqs = set()
                else:
                    scores = c["scores"]
                    dqs = set(c.get("disqualifiers", []))

            for d in DIMS:
                row_dims.setdefault(d, []).append(scores[d])
            comp = composite_for(scores, weights)
            # clamp author-only flags like pre_paris_override that don't exist in rubric
            flag_list = [f for f in dqs if f in {dq["id"] for dq in dq_spec}]
            nominal = grade_from_composite(comp, bands)
            final = apply_dq_cap(nominal, flag_list, dq_spec)
            row_comp.append(round(comp, 2))
            row_grade.append(final)
            disqualifiers[rater].append(dqs)

        for d in DIMS:
            dim_matrices[d].append(row_dims[d])
        composites.append(row_comp)
        grades.append(row_grade)

    # --- Per-dimension pairwise absolute mean disagreement ---
    print("=" * 70)
    print(" Per-dimension mean absolute disagreement (across all panel pairs)")
    print("=" * 70)
    per_dim_mad = {}
    for d in DIMS:
        mads = []
        for i in range(1, len(all_raters)):  # skip author in this pass to isolate panel
            for j in range(i + 1, len(all_raters)):
                mad = sum(
                    abs(dim_matrices[d][k][i] - dim_matrices[d][k][j]) for k in range(len(credit_ids))
                ) / len(credit_ids)
                mads.append(mad)
        mean_mad = sum(mads) / len(mads) if mads else float("nan")
        per_dim_mad[d] = mean_mad
        print(f"  {d:22s}  mean |Δ|={mean_mad:5.2f}")

    # --- Per-dimension Pearson correlation across panel (mean of pairs) ---
    print()
    print("=" * 70)
    print(" Per-dimension Pearson correlation (mean of LLM pairs)")
    print("=" * 70)
    per_dim_pearson = {}
    for d in DIMS:
        rhos = []
        llm_indices = [all_raters.index(r) for r in RATERS]
        for i_idx in range(len(llm_indices)):
            for j_idx in range(i_idx + 1, len(llm_indices)):
                i, j = llm_indices[i_idx], llm_indices[j_idx]
                x = [dim_matrices[d][k][i] for k in range(len(credit_ids))]
                y = [dim_matrices[d][k][j] for k in range(len(credit_ids))]
                rho = pearson(x, y)
                if not math.isnan(rho):
                    rhos.append(rho)
        mean_rho = sum(rhos) / len(rhos) if rhos else float("nan")
        per_dim_pearson[d] = mean_rho
        print(f"  {d:22s}  mean Pearson ρ={mean_rho:+.3f}")

    # --- Grade-level agreement (full panel of 4 = author + 3 LLMs) ---
    print()
    print("=" * 70)
    print(" Grade-level pairwise agreement")
    print("=" * 70)
    # Cohen's kappa for each pair
    grade_ints = [[GRADE_INDEX[g] for g in row] for row in grades]
    for i, ri in enumerate(all_raters):
        for j, rj in enumerate(all_raters[i + 1:], start=i + 1):
            a = [grade_ints[k][i] for k in range(len(credit_ids))]
            b = [grade_ints[k][j] for k in range(len(credit_ids))]
            exact = sum(1 for k in range(len(a)) if a[k] == b[k]) / len(a)
            within1 = sum(1 for k in range(len(a)) if abs(a[k] - b[k]) <= 1) / len(a)
            k = cohens_kappa(a, b, len(GRADES))
            print(f"  {ri:20s} vs {rj:20s}  κ={k:+.3f}  exact={exact:.0%}  ±1 band={within1:.0%}")

    # --- Fleiss' kappa on the LLM panel only (3 raters) ---
    print()
    print("=" * 70)
    print(" Fleiss' κ on LLM-only panel (3 raters × 29 credits)")
    print("=" * 70)
    matrix = []
    for k_idx, cid in enumerate(credit_ids):
        row = [0] * len(GRADES)
        for i in range(len(RATERS)):
            llm_idx = all_raters.index(RATERS[i])
            row[grade_ints[k_idx][llm_idx]] += 1
        matrix.append(row)
    fk = fleiss_kappa(matrix, len(GRADES))
    print(f"  Grade-level Fleiss' κ = {fk:+.3f}")

    # Per-dimension Fleiss' kappa, binning scores into 5-point buckets
    print()
    print("=" * 70)
    print(" Per-dimension Fleiss' κ (scores binned to 10 buckets of 10 pts)")
    print("=" * 70)
    N_BUCKETS = 10
    per_dim_fleiss = {}
    for d in DIMS:
        mat = []
        for k_idx in range(len(credit_ids)):
            row = [0] * N_BUCKETS
            for i in range(len(RATERS)):
                llm_idx = all_raters.index(RATERS[i])
                s = dim_matrices[d][k_idx][llm_idx]
                b = min(N_BUCKETS - 1, s // 10)
                row[b] += 1
            mat.append(row)
        k_val = fleiss_kappa(mat, N_BUCKETS)
        per_dim_fleiss[d] = k_val
        print(f"  {d:22s}  κ = {k_val:+.3f}")

    # --- ICC on continuous composite ---
    print()
    print("=" * 70)
    print(" ICC(2,k) on continuous composite (3-rater LLM panel)")
    print("=" * 70)
    llm_composites = []
    for k_idx in range(len(credit_ids)):
        row = []
        for r in RATERS:
            llm_idx = all_raters.index(r)
            row.append(composites[k_idx][llm_idx])
        llm_composites.append(row)
    icc = icc_2k(llm_composites)
    print(f"  ICC(2,k) = {icc:+.3f}")

    # --- Author vs panel median exact agreement ---
    print()
    print("=" * 70)
    print(" Author v0.4.1 grade vs LLM panel median grade")
    print("=" * 70)
    exact = 0
    within1 = 0
    for k_idx, cid in enumerate(credit_ids):
        llm_grades = [grade_ints[k_idx][all_raters.index(r)] for r in RATERS]
        llm_grades.sort()
        median = llm_grades[len(llm_grades) // 2]
        author = grade_ints[k_idx][0]
        if author == median:
            exact += 1
        if abs(author - median) <= 1:
            within1 += 1
    print(f"  Exact agreement:  {exact}/{len(credit_ids)} = {exact/len(credit_ids):.0%}")
    print(f"  Within ±1 band:   {within1}/{len(credit_ids)} = {within1/len(credit_ids):.0%}")

    # --- Fragility validation for C004, C011, C014 ---
    print()
    print("=" * 70)
    print(" Fragility flag validation (boundary-adjacent credits)")
    print("=" * 70)
    fragility_targets = {"C004": "AAA", "C011": "BBB", "C014": "A"}
    for cid, expected in fragility_targets.items():
        if cid not in [c for c in credit_ids]:
            continue
        k_idx = credit_ids.index(cid)
        llm_grades_for = [grades[k_idx][all_raters.index(r)] for r in RATERS]
        matches = sum(1 for g in llm_grades_for if g == expected)
        print(f"  {cid} (author: {expected}): LLM panel = {llm_grades_for}, matching {expected} = {matches}/3")

    # --- Disqualifier recall for C026-C029 ---
    print()
    print("=" * 70)
    print(" Disqualifier recall (synthetic stress tests)")
    print("=" * 70)
    stress_targets = {
        "C026": "double_counting",
        "C027": "sanctioned_registry",
        "C028": "no_third_party",
        "C029": "community_harm",
    }
    for cid, expected in stress_targets.items():
        if cid not in credit_ids:
            continue
        hit = 0
        for r in RATERS:
            flags = rater_scores[r][cid].get("disqualifiers", [])
            if expected in flags:
                hit += 1
        print(f"  {cid} expected '{expected}': recalled by {hit}/3 raters")

    # --- Write structured outputs ---
    summary = {
        "n_credits": len(credit_ids),
        "raters": RATERS,
        "per_dimension_mad": per_dim_mad,
        "per_dimension_pearson_mean": per_dim_pearson,
        "per_dimension_fleiss": per_dim_fleiss,
        "grade_fleiss_kappa_llm_panel": fk,
        "composite_icc_2k_llm_panel": icc,
        "author_vs_panel_median_exact": exact / len(credit_ids),
        "author_vs_panel_median_within1": within1 / len(credit_ids),
    }
    (HERE / "irr_summary.json").write_text(json.dumps(summary, indent=2))

    # Per-credit CSV
    with (HERE / "panel_scores.csv").open("w", newline="") as f:
        w = csv.writer(f)
        header = ["credit_id"]
        for r in all_raters:
            header.append(f"{r}_grade")
            header.append(f"{r}_composite")
        w.writerow(header)
        for k_idx, cid in enumerate(credit_ids):
            row = [cid]
            for i, r in enumerate(all_raters):
                row.append(grades[k_idx][i])
                row.append(composites[k_idx][i])
            w.writerow(row)

    print()
    print("Wrote:")
    print(f"  {HERE / 'irr_summary.json'}")
    print(f"  {HERE / 'panel_scores.csv'}")


if __name__ == "__main__":
    main()
