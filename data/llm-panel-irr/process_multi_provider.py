#!/usr/bin/env python3
"""
Process multi-provider LLM panel scoring outputs and compute cross-provider
inter-rater reliability metrics.

Takes scoring outputs from multiple LLM providers (GPT-5, Gemini, Llama/DeepSeek,
plus the existing Anthropic panel) in JSON format, computes per-provider and
cross-provider IRR statistics, and compares to the Anthropic-only baseline.

Standard library only: csv, json, math, statistics.

Usage:
    python3 process_multi_provider.py
    python3 process_multi_provider.py --input path/to/multi_provider.json
    python3 process_multi_provider.py --input results.json --anthropic-kappa 0.600

Input JSON format:
    See sample_multi_provider.json for the expected schema. The file contains
    an array of provider objects, each with an array of credit scores.

Output:
    data/llm-panel-irr/multi_provider_results.md
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUBRICS = ROOT / "data" / "scoring-rubrics"

DIMS = [
    "removal_type",
    "additionality",
    "permanence",
    "mrv_grade",
    "vintage_year",
    "co_benefits",
    "registry_methodology",
]

GRADES = ["B", "BB", "BBB", "A", "AA", "AAA"]
GRADE_INDEX = {g: i for i, g in enumerate(GRADES)}

ANTHROPIC_BASELINE_KAPPA = 0.600
ANTHROPIC_BASELINE_ICC = 0.993


# -----------------------------------------------------------------------
# Statistical helpers (same implementations as irr.py, no import coupling)
# -----------------------------------------------------------------------

def load_rubric() -> dict:
    with (RUBRICS / "index.json").open() as f:
        return json.load(f)


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
            if GRADE_INDEX.get(final, 0) > GRADE_INDEX.get(cap, 0):
                final = cap
    return final


def composite_for(scores: dict, weights: dict) -> float:
    return sum(scores.get(d, 0) * weights.get(d, 0) for d in DIMS)


def pearson(x: list[float], y: list[float]) -> float:
    n = len(x)
    if n < 2:
        return float("nan")
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    dx = math.sqrt(sum((a - mx) ** 2 for a in x))
    dy = math.sqrt(sum((a - my) ** 2 for a in y))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


def cohens_kappa(a: list[int], b: list[int], k: int) -> float:
    """Cohen's kappa for categorical agreement."""
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(1 for i in range(n) if a[i] == b[i]) / n
    pa = [a.count(c) / n for c in range(k)]
    pb = [b.count(c) / n for c in range(k)]
    pe = sum(pa[c] * pb[c] for c in range(k))
    if pe == 1:
        return 1.0
    return (po - pe) / (1 - pe)


def fleiss_kappa(matrix: list[list[int]], k: int) -> float:
    """Fleiss' kappa.  matrix[i][c] = # raters assigning item i to category c."""
    n = len(matrix)
    if n == 0:
        return float("nan")
    m = sum(matrix[0])
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
    """ICC(2,k) -- two-way random, mean of k raters, consistency."""
    n = len(ratings)
    if n < 2:
        return float("nan")
    k = len(ratings[0])
    if k < 2:
        return float("nan")
    grand_mean = sum(sum(r) for r in ratings) / (n * k)

    subject_means = [sum(r) / k for r in ratings]
    rater_means = [sum(ratings[i][j] for i in range(n)) / n for j in range(k)]

    SSR = k * sum((sm - grand_mean) ** 2 for sm in subject_means)
    SSC = n * sum((rm - grand_mean) ** 2 for rm in rater_means)
    SST = sum((ratings[i][j] - grand_mean) ** 2 for i in range(n) for j in range(k))
    SSE = SST - SSR - SSC

    MSR = SSR / (n - 1)
    MSE = SSE / ((n - 1) * (k - 1)) if (n > 1 and k > 1) else float("nan")

    if MSR == 0:
        return float("nan")
    return (MSR - MSE) / MSR


# -----------------------------------------------------------------------
# Data loading and processing
# -----------------------------------------------------------------------

def load_multi_provider(path: Path) -> dict:
    """Load the multi-provider JSON file.

    Expected schema:
    {
        "providers": [
            {
                "provider": "openai",
                "model": "gpt-5",
                "raters": [
                    {
                        "rater_id": "gpt5-run1",
                        "credits": [
                            {
                                "id": "C001",
                                "scores": {"removal_type": 95, ...},
                                "disqualifiers": []
                            }, ...
                        ]
                    }, ...
                ]
            }, ...
        ]
    }
    """
    with path.open() as f:
        return json.load(f)


def process_provider(provider_data: dict, weights: dict, bands: list[dict],
                     dq_spec: list[dict]) -> dict:
    """Process a single provider's data, returning per-credit grades and composites."""
    raters = provider_data["raters"]
    results = {}

    for rater in raters:
        rid = rater["rater_id"]
        results[rid] = {}
        for credit in rater["credits"]:
            cid = credit["id"]
            scores = credit["scores"]
            comp = composite_for(scores, weights)
            dq_flags = [f for f in credit.get("disqualifiers", [])
                        if f in {dq["id"] for dq in dq_spec}]
            nominal = grade_from_composite(comp, bands)
            final = apply_dq_cap(nominal, dq_flags, dq_spec)
            results[rid][cid] = {
                "scores": scores,
                "composite": round(comp, 2),
                "grade": final,
                "grade_idx": GRADE_INDEX[final],
                "disqualifiers": credit.get("disqualifiers", []),
            }

    return results


def per_provider_fleiss(provider_results: dict, credit_ids: list[str]) -> float:
    """Compute grade-level Fleiss' kappa for one provider's rater set."""
    raters = list(provider_results.keys())
    n_raters = len(raters)
    if n_raters < 2:
        return float("nan")

    matrix = []
    for cid in credit_ids:
        row = [0] * len(GRADES)
        for rid in raters:
            if cid in provider_results[rid]:
                g_idx = provider_results[rid][cid]["grade_idx"]
                row[g_idx] += 1
        matrix.append(row)

    return fleiss_kappa(matrix, len(GRADES))


def per_provider_icc(provider_results: dict, credit_ids: list[str]) -> float:
    """Compute ICC(2,k) on composites for one provider's rater set."""
    raters = list(provider_results.keys())
    ratings = []
    for cid in credit_ids:
        row = []
        for rid in raters:
            if cid in provider_results[rid]:
                row.append(provider_results[rid][cid]["composite"])
        if len(row) == len(raters):
            ratings.append(row)

    return icc_2k(ratings)


def per_dimension_disagreement(all_provider_results: dict[str, dict],
                               credit_ids: list[str]) -> dict[str, dict]:
    """Compute per-dimension mean absolute disagreement across all raters from
    all providers pooled together."""
    # Collect all rater results into a flat dict
    all_raters = {}
    for pname, presults in all_provider_results.items():
        for rid, credits in presults.items():
            all_raters[f"{pname}:{rid}"] = credits

    rater_ids = sorted(all_raters.keys())
    dim_stats = {}

    for d in DIMS:
        mad_pairs = []
        disagreement_by_credit = {}

        for cid in credit_ids:
            scores = []
            for rid in rater_ids:
                if cid in all_raters[rid]:
                    scores.append(all_raters[rid][cid]["scores"].get(d, 0))

            if len(scores) >= 2:
                # Mean absolute difference across all pairs
                pairs = [(scores[i], scores[j])
                         for i in range(len(scores))
                         for j in range(i + 1, len(scores))]
                pairwise_diffs = [abs(a - b) for a, b in pairs]
                mean_diff = sum(pairwise_diffs) / len(pairwise_diffs)
                mad_pairs.append(mean_diff)
                disagreement_by_credit[cid] = mean_diff

        overall_mad = sum(mad_pairs) / len(mad_pairs) if mad_pairs else float("nan")

        # Find the credit with maximum disagreement for this dimension
        worst_credit = max(disagreement_by_credit, key=disagreement_by_credit.get) \
            if disagreement_by_credit else "N/A"
        worst_value = disagreement_by_credit.get(worst_credit, float("nan"))

        dim_stats[d] = {
            "mean_abs_delta": overall_mad,
            "worst_credit": worst_credit,
            "worst_delta": worst_value,
        }

    return dim_stats


def cross_provider_pairwise(all_results: dict[str, dict],
                            credit_ids: list[str]) -> list[dict]:
    """Compute pairwise Cohen's kappa between every provider pair,
    using each provider's median grade as a single 'rater'."""
    providers = sorted(all_results.keys())
    pairs = []

    for i in range(len(providers)):
        for j in range(i + 1, len(providers)):
            p1 = providers[i]
            p2 = providers[j]

            grades_p1 = []
            grades_p2 = []

            for cid in credit_ids:
                # Median grade for provider 1
                g1_list = [all_results[p1][rid][cid]["grade_idx"]
                           for rid in all_results[p1]
                           if cid in all_results[p1][rid]]
                g2_list = [all_results[p2][rid][cid]["grade_idx"]
                           for rid in all_results[p2]
                           if cid in all_results[p2][rid]]

                if g1_list and g2_list:
                    g1_list.sort()
                    g2_list.sort()
                    grades_p1.append(g1_list[len(g1_list) // 2])
                    grades_p2.append(g2_list[len(g2_list) // 2])

            if grades_p1:
                kappa = cohens_kappa(grades_p1, grades_p2, len(GRADES))
                exact = sum(1 for a, b in zip(grades_p1, grades_p2) if a == b)
                within1 = sum(1 for a, b in zip(grades_p1, grades_p2) if abs(a - b) <= 1)
                n = len(grades_p1)
                pairs.append({
                    "provider_1": p1,
                    "provider_2": p2,
                    "kappa": kappa,
                    "exact_agreement": exact / n if n > 0 else 0,
                    "within_1_band": within1 / n if n > 0 else 0,
                    "n": n,
                })

    return pairs


def overall_multi_provider_fleiss(all_results: dict[str, dict],
                                  credit_ids: list[str]) -> float:
    """Compute Fleiss' kappa with ALL individual raters from ALL providers pooled."""
    # Flatten all raters
    all_raters = []
    for pname in sorted(all_results.keys()):
        for rid in sorted(all_results[pname].keys()):
            all_raters.append((pname, rid))

    if len(all_raters) < 2:
        return float("nan")

    matrix = []
    for cid in credit_ids:
        row = [0] * len(GRADES)
        for pname, rid in all_raters:
            if cid in all_results[pname][rid]:
                g_idx = all_results[pname][rid][cid]["grade_idx"]
                row[g_idx] += 1
        if sum(row) == len(all_raters):  # all raters scored this credit
            matrix.append(row)

    return fleiss_kappa(matrix, len(GRADES))


def overall_multi_provider_icc(all_results: dict[str, dict],
                               credit_ids: list[str]) -> float:
    """ICC(2,k) with ALL raters pooled on composite scores."""
    all_raters = []
    for pname in sorted(all_results.keys()):
        for rid in sorted(all_results[pname].keys()):
            all_raters.append((pname, rid))

    if len(all_raters) < 2:
        return float("nan")

    ratings = []
    for cid in credit_ids:
        row = []
        for pname, rid in all_raters:
            if cid in all_results[pname][rid]:
                row.append(all_results[pname][rid][cid]["composite"])
        if len(row) == len(all_raters):
            ratings.append(row)

    return icc_2k(ratings)


def flag_dimension_disagreements(dim_stats: dict[str, dict],
                                 threshold: float = 10.0) -> list[str]:
    """Return dimensions where mean absolute disagreement exceeds threshold."""
    flagged = []
    for d in DIMS:
        if dim_stats[d]["mean_abs_delta"] > threshold:
            flagged.append(d)
    return flagged


# -----------------------------------------------------------------------
# Report generation
# -----------------------------------------------------------------------

def generate_report(data: dict, all_results: dict[str, dict],
                    credit_ids: list[str], provider_stats: dict,
                    cross_pairs: list[dict], overall_fk: float,
                    overall_icc: float, dim_stats: dict,
                    flagged_dims: list[str],
                    anthropic_kappa: float) -> str:
    """Generate multi_provider_results.md."""
    lines = []
    lines.append("# Multi-Provider LLM Panel IRR Results")
    lines.append("")

    n_providers = len(data["providers"])
    total_raters = sum(len(p["raters"]) for p in data["providers"])
    lines.append(f"*{n_providers} providers, {total_raters} total raters, "
                 f"{len(credit_ids)} credits.*")
    lines.append("")

    # Section 1: Per-provider statistics
    lines.append("## 1. Per-Provider IRR Statistics")
    lines.append("")
    lines.append("| Provider | Model | N raters | Fleiss' kappa | ICC(2,k) |")
    lines.append("|----------|-------|--------:|-------------:|--------:|")
    for p in data["providers"]:
        pname = p["provider"]
        model = p["model"]
        n_raters = len(p["raters"])
        fk = provider_stats[pname]["fleiss"]
        icc = provider_stats[pname]["icc"]
        fk_str = f"{fk:+.3f}" if not math.isnan(fk) else "N/A (1 rater)"
        icc_str = f"{icc:+.3f}" if not math.isnan(icc) else "N/A (1 rater)"
        lines.append(f"| {pname} | {model} | {n_raters} | {fk_str} | {icc_str} |")
    lines.append("")

    # Section 2: Cross-provider pairwise agreement
    lines.append("## 2. Cross-Provider Pairwise Agreement (Median Grade)")
    lines.append("")
    lines.append("| Provider 1 | Provider 2 | Cohen's kappa | Exact agreement | Within +/-1 band |")
    lines.append("|------------|------------|-------------:|----------------:|----------------:|")
    for pair in cross_pairs:
        lines.append(
            f"| {pair['provider_1']} | {pair['provider_2']} | "
            f"{pair['kappa']:+.3f} | {pair['exact_agreement']:.0%} | "
            f"{pair['within_1_band']:.0%} |")
    lines.append("")

    if cross_pairs:
        mean_kappa = sum(p["kappa"] for p in cross_pairs) / len(cross_pairs)
        mean_exact = sum(p["exact_agreement"] for p in cross_pairs) / len(cross_pairs)
        lines.append(f"**Mean cross-provider kappa:** {mean_kappa:+.3f}")
        lines.append(f"**Mean cross-provider exact agreement:** {mean_exact:.0%}")
        lines.append("")

    # Section 3: Overall pooled statistics
    lines.append("## 3. Overall Multi-Provider Statistics (All Raters Pooled)")
    lines.append("")
    lines.append("| Metric | Anthropic-only (baseline) | Multi-provider (all pooled) | Delta |")
    lines.append("|--------|-------------------------:|---------------------------:|------:|")
    lines.append(
        f"| Grade-level Fleiss' kappa | {anthropic_kappa:+.3f} | "
        f"{overall_fk:+.3f} | {overall_fk - anthropic_kappa:+.3f} |")
    lines.append(
        f"| Composite ICC(2,k) | {ANTHROPIC_BASELINE_ICC:+.3f} | "
        f"{overall_icc:+.3f} | {overall_icc - ANTHROPIC_BASELINE_ICC:+.3f} |")
    lines.append("")

    if overall_fk < anthropic_kappa:
        lines.append("**Finding:** Multi-provider kappa is LOWER than Anthropic-only "
                      "baseline, suggesting provider-shared biases in the Anthropic "
                      "panel that inflate within-family agreement.")
    elif overall_fk > anthropic_kappa:
        lines.append("**Finding:** Multi-provider kappa is HIGHER than Anthropic-only "
                      "baseline, suggesting the rubric produces consistent results "
                      "even across model families.")
    else:
        lines.append("**Finding:** Multi-provider kappa matches Anthropic-only baseline.")
    lines.append("")

    # Section 4: Per-dimension disagreement
    lines.append("## 4. Per-Dimension Cross-Provider Disagreement")
    lines.append("")
    lines.append("| Dimension | Mean |Delta| | Worst credit | Worst |Delta| | Flagged? |")
    lines.append("|-----------|---------------:|-------------|----------------:|----------|")
    for d in DIMS:
        s = dim_stats[d]
        flag = "YES" if d in flagged_dims else ""
        lines.append(
            f"| {d} | {s['mean_abs_delta']:.1f} | {s['worst_credit']} | "
            f"{s['worst_delta']:.1f} | {flag} |")
    lines.append("")

    if flagged_dims:
        lines.append(f"**Dimensions with mean |Delta| > 10 (flagged):** "
                      f"{', '.join(flagged_dims)}")
        lines.append("")
        lines.append("These dimensions show the most inter-provider disagreement "
                      "and are the primary targets for rubric refinement in v0.6.")
    else:
        lines.append("**No dimensions exceeded the |Delta| > 10 disagreement threshold.**")
    lines.append("")

    # Section 5: Provider bias detection
    lines.append("## 5. Provider Bias Detection")
    lines.append("")
    lines.append("Mean composite score by provider (systematic bias check):")
    lines.append("")
    lines.append("| Provider | Mean composite | Std composite | vs Grand mean |")
    lines.append("|----------|---------------:|--------------:|-------------:|")

    all_comps = []
    for pname in sorted(all_results.keys()):
        p_comps = []
        for rid in all_results[pname]:
            for cid in credit_ids:
                if cid in all_results[pname][rid]:
                    p_comps.append(all_results[pname][rid][cid]["composite"])
        all_comps.extend(p_comps)
        if p_comps:
            mean_c = sum(p_comps) / len(p_comps)
            std_c = statistics.stdev(p_comps) if len(p_comps) > 1 else 0
        else:
            mean_c = std_c = float("nan")
        # Store for delta computation
        all_results[pname]["_mean_composite"] = mean_c
        all_results[pname]["_std_composite"] = std_c

    grand_mean = sum(all_comps) / len(all_comps) if all_comps else float("nan")

    for pname in sorted(all_results.keys()):
        mc = all_results[pname].get("_mean_composite", float("nan"))
        sc = all_results[pname].get("_std_composite", float("nan"))
        if not math.isnan(mc) and not math.isnan(grand_mean):
            delta = mc - grand_mean
        else:
            delta = float("nan")
        lines.append(
            f"| {pname} | {mc:.1f} | {sc:.1f} | {delta:+.1f} |")
    lines.append("")

    # Section 6: Interpretation
    lines.append("## 6. Interpretation and Paper Integration Notes")
    lines.append("")
    lines.append("### For the Nature Communications revision:")
    lines.append("")
    lines.append("1. **Section 2 (Results), 'Quality ratings are reproducible'**: "
                 "Update the Fleiss' kappa paragraph to report multi-provider kappa "
                 f"({overall_fk:+.3f}) alongside the Anthropic-only baseline "
                 f"({anthropic_kappa:+.3f}).")
    lines.append("")
    lines.append("2. **Table 1 (Per-dimension reliability)**: Add a column for "
                 "multi-provider mean |Delta| per dimension.")
    lines.append("")
    lines.append("3. **Discussion**: If multi-provider kappa < Anthropic kappa, "
                 "this validates Limitation 1 (Anthropic-only panel). If multi-provider "
                 "kappa >= Anthropic kappa, Limitation 1 is partially resolved.")
    lines.append("")

    return "\n".join(lines)


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main() -> None:
    input_path = HERE / "sample_multi_provider.json"
    anthropic_kappa = ANTHROPIC_BASELINE_KAPPA

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--input" and i + 1 < len(args):
            input_path = Path(args[i + 1]).resolve()
            i += 2
        elif args[i] == "--anthropic-kappa" and i + 1 < len(args):
            anthropic_kappa = float(args[i + 1])
            i += 2
        else:
            print(f"Unknown argument: {args[i]}")
            i += 1

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        print("Run with --input <path> or create sample_multi_provider.json")
        sys.exit(1)

    print(f"Loading multi-provider data from {input_path}")
    data = load_multi_provider(input_path)

    # Load framework config
    rubric = load_rubric()
    weights = {d["id"]: d["weight"] for d in rubric["dimensions"]}
    bands = rubric["grades"]
    dq_spec = rubric["disqualifiers"]

    # Process each provider
    all_results = {}
    provider_stats = {}

    for p in data["providers"]:
        pname = p["provider"]
        print(f"\nProcessing provider: {pname} ({p['model']}, {len(p['raters'])} raters)")
        results = process_provider(p, weights, bands, dq_spec)
        all_results[pname] = results

        # Gather credit IDs from first rater of this provider
        first_rater = list(results.keys())[0]
        credit_ids = sorted(results[first_rater].keys())

        fk = per_provider_fleiss(results, credit_ids)
        icc = per_provider_icc(results, credit_ids)
        provider_stats[pname] = {"fleiss": fk, "icc": icc}
        print(f"  Fleiss' kappa: {fk:+.3f}" if not math.isnan(fk) else "  Fleiss' kappa: N/A")
        print(f"  ICC(2,k): {icc:+.3f}" if not math.isnan(icc) else "  ICC(2,k): N/A")

    # Determine global credit ID list from first provider
    first_provider = data["providers"][0]["provider"]
    first_rater = list(all_results[first_provider].keys())[0]
    credit_ids = sorted(all_results[first_provider][first_rater].keys())
    print(f"\n{len(credit_ids)} credits in common across providers")

    # Cross-provider pairwise agreement
    print("\nCross-provider pairwise agreement:")
    cross_pairs = cross_provider_pairwise(all_results, credit_ids)
    for pair in cross_pairs:
        print(f"  {pair['provider_1']} vs {pair['provider_2']}: "
              f"kappa={pair['kappa']:+.3f}, exact={pair['exact_agreement']:.0%}")

    # Overall pooled Fleiss' kappa
    overall_fk = overall_multi_provider_fleiss(all_results, credit_ids)
    overall_icc = overall_multi_provider_icc(all_results, credit_ids)
    print(f"\nOverall pooled Fleiss' kappa: {overall_fk:+.3f}")
    print(f"Overall pooled ICC(2,k): {overall_icc:+.3f}")
    print(f"Anthropic-only baseline kappa: {anthropic_kappa:+.3f}")
    print(f"Delta: {overall_fk - anthropic_kappa:+.3f}")

    # Per-dimension disagreement
    dim_stats = per_dimension_disagreement(all_results, credit_ids)
    flagged_dims = flag_dimension_disagreements(dim_stats)
    if flagged_dims:
        print(f"\nFlagged dimensions (|Delta| > 10): {', '.join(flagged_dims)}")

    # Generate report
    report = generate_report(
        data, all_results, credit_ids, provider_stats,
        cross_pairs, overall_fk, overall_icc, dim_stats,
        flagged_dims, anthropic_kappa)

    out_path = HERE / "multi_provider_results.md"
    out_path.write_text(report)
    print(f"\nWrote report to {out_path}")


if __name__ == "__main__":
    main()
