#!/usr/bin/env python3
"""
Extended Data 4: Deterministic weight-perturbation and leave-one-out analysis.

For each of the 7 dimensions:
  1. +5pp perturbation: increase weight by 0.05, redistribute proportionally
  2. -5pp perturbation: decrease weight by 0.05, redistribute proportionally
  3. Leave-one-out: set weight to 0, redistribute proportionally

Reports:
  - Number of grade changes per perturbation
  - Which credits flip (old grade -> new grade)
  - Max absolute composite score change
  - Per-credit composite delta

Writes: weight_perturbation_results.md

Pure Python -- no external dependencies beyond score.py in pilot-scoring/.

Usage:
    python3 weight_perturbation.py
"""

from __future__ import annotations

import json
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

GRADE_ORDER = ["B", "BB", "BBB", "A", "AA", "AAA"]
GRADE_NUM = {g: i for i, g in enumerate(GRADE_ORDER)}


def perturb_weights(
    base_weights: dict[str, float], target_dim: str, delta: float
) -> dict[str, float] | None:
    """Perturb target_dim by delta, redistribute proportionally among other non-zero dims.

    Returns None if the perturbation would make the target weight negative.
    """
    new_w = dict(base_weights)
    target_val = new_w[target_dim] + delta
    if target_val < 0:
        return None

    new_w[target_dim] = target_val
    others = [d for d in new_w if d != target_dim and base_weights[d] > 0]
    if not others:
        return None

    other_sum = sum(base_weights[d] for d in others)
    if other_sum == 0:
        return None

    for d in others:
        new_w[d] = base_weights[d] - delta * (base_weights[d] / other_sum)

    # Renormalize against float error
    total = sum(new_w.values())
    if total > 0:
        new_w = {k: v / total for k, v in new_w.items()}

    return new_w


def leave_one_out_weights(
    base_weights: dict[str, float], drop_dim: str
) -> dict[str, float] | None:
    """Set drop_dim to 0, redistribute its weight proportionally among remaining non-zero dims."""
    if base_weights[drop_dim] == 0:
        return None

    new_w = dict(base_weights)
    dropped = new_w[drop_dim]
    new_w[drop_dim] = 0.0

    remaining = [d for d in new_w if d != drop_dim and new_w[d] > 0]
    remaining_sum = sum(new_w[d] for d in remaining)
    if remaining_sum == 0:
        return None

    for d in remaining:
        new_w[d] = new_w[d] + dropped * (new_w[d] / remaining_sum)

    return new_w


def score_all_credits(
    credits: list[dict],
    weights: dict[str, float],
    grade_bands: list[dict],
    dq_spec: list[dict],
    dim_adjustments: dict,
) -> dict[str, tuple[float, str]]:
    """Score all credits with given weights. Returns {credit_id: (composite, final_grade)}."""
    dimensions = list(weights.keys())
    out = {}
    for credit in credits:
        base_scores = credit["scores"]
        adj_flags = credit.get("adjustments", [])
        scores = apply_dimension_adjustments(base_scores, adj_flags, dim_adjustments)
        comp = composite(scores, weights)
        grade = grade_from_score(comp, grade_bands)
        final, _ = apply_disqualifiers(grade, credit.get("disqualifiers", []), dq_spec)
        out[credit["id"]] = (comp, final)
    return out


def compare_results(
    baseline: dict[str, tuple[float, str]],
    perturbed: dict[str, tuple[float, str]],
    credit_names: dict[str, str],
) -> dict:
    """Compare baseline vs perturbed results. Returns summary dict."""
    flips = []
    deltas = []
    for cid in baseline:
        base_comp, base_grade = baseline[cid]
        pert_comp, pert_grade = perturbed[cid]
        delta = pert_comp - base_comp
        deltas.append((cid, delta))
        if base_grade != pert_grade:
            flips.append({
                "id": cid,
                "name": credit_names[cid],
                "base_grade": base_grade,
                "new_grade": pert_grade,
                "base_composite": round(base_comp, 2),
                "new_composite": round(pert_comp, 2),
                "delta": round(delta, 2),
                "direction": "up" if GRADE_NUM[pert_grade] > GRADE_NUM[base_grade] else "down",
            })

    abs_deltas = [abs(d) for _, d in deltas]
    max_delta = max(abs_deltas) if abs_deltas else 0.0
    mean_delta = sum(abs_deltas) / len(abs_deltas) if abs_deltas else 0.0

    return {
        "n_flips": len(flips),
        "flips": flips,
        "max_abs_delta": round(max_delta, 2),
        "mean_abs_delta": round(mean_delta, 2),
        "all_deltas": [(cid, round(d, 2)) for cid, d in deltas],
    }


def main() -> None:
    rubrics = load_rubric_index()
    grade_bands = rubrics["grades"]
    dq_spec = rubrics["disqualifiers"]
    dim_adjustments = load_dimension_adjustments()

    with CREDITS_PATH.open() as f:
        credits_data = json.load(f)
    credits = credits_data["credits"]

    weights = {d["id"]: d["weight"] for d in rubrics["dimensions"]}
    dimensions = list(weights.keys())
    credit_names = {c["id"]: c["name"] for c in credits}
    n = len(credits)

    # Compute baseline
    baseline = score_all_credits(credits, weights, grade_bands, dq_spec, dim_adjustments)

    # ========== +/-5pp perturbation ==========
    perturbation_results = {}
    for dim in dimensions:
        perturbation_results[dim] = {}
        for direction, delta in [("plus_5pp", +0.05), ("minus_5pp", -0.05)]:
            new_w = perturb_weights(weights, dim, delta)
            if new_w is None:
                perturbation_results[dim][direction] = {
                    "n_flips": 0,
                    "flips": [],
                    "max_abs_delta": 0.0,
                    "mean_abs_delta": 0.0,
                    "skipped": True,
                    "reason": "weight would go negative",
                }
                continue
            perturbed = score_all_credits(credits, new_w, grade_bands, dq_spec, dim_adjustments)
            result = compare_results(baseline, perturbed, credit_names)
            result["new_weights"] = {k: round(v, 4) for k, v in new_w.items()}
            perturbation_results[dim][direction] = result

    # ========== Leave-one-out ==========
    loo_results = {}
    for dim in dimensions:
        new_w = leave_one_out_weights(weights, dim)
        if new_w is None:
            loo_results[dim] = {
                "n_flips": 0,
                "flips": [],
                "max_abs_delta": 0.0,
                "mean_abs_delta": 0.0,
                "skipped": True,
                "reason": "weight already zero",
            }
            continue
        perturbed = score_all_credits(credits, new_w, grade_bands, dq_spec, dim_adjustments)
        result = compare_results(baseline, perturbed, credit_names)
        result["new_weights"] = {k: round(v, 4) for k, v in new_w.items()}
        loo_results[dim] = result

    # ========== Write markdown ==========
    md = generate_markdown(
        weights, dimensions, n, perturbation_results, loo_results, baseline, credit_names
    )
    out_path = HERE / "weight_perturbation_results.md"
    out_path.write_text(md)
    print(f"Wrote: {out_path}")

    # Also write JSON for programmatic consumption
    out_json = HERE / "weight_perturbation_results.json"
    out_json.write_text(json.dumps({
        "perturbation": perturbation_results,
        "leave_one_out": loo_results,
    }, indent=2))
    print(f"Wrote: {out_json}")


def generate_markdown(
    weights: dict[str, float],
    dimensions: list[str],
    n: int,
    perturbation_results: dict,
    loo_results: dict,
    baseline: dict[str, tuple[float, str]],
    credit_names: dict[str, str],
) -> str:
    lines = [
        "# Weight Perturbation Analysis (Extended Data 4)",
        "",
        "Deterministic +/-5pp perturbation and leave-one-out analysis for the",
        "7-dimension scoring framework.",
        "",
        f"Baseline weights: {', '.join(f'{k}={v}' for k, v in weights.items())}",
        f"Credits scored: {n}",
        "",
    ]

    # ---------- Summary table: +/-5pp ----------
    lines.extend([
        "## 1. Weight Perturbation Summary (+/-5pp)",
        "",
        "For each dimension, weight is increased/decreased by 5 percentage points",
        "with the delta redistributed proportionally among other non-zero dimensions.",
        "",
        "| Dimension | Baseline wt | +5pp flips | +5pp max |delta| | -5pp flips | -5pp max |delta| |",
        "|-----------|:-----------:|:----------:|:---------------:|:----------:|:---------------:|",
    ])
    for dim in dimensions:
        bw = weights[dim]
        plus = perturbation_results[dim].get("plus_5pp", {})
        minus = perturbation_results[dim].get("minus_5pp", {})
        p_flips = plus.get("n_flips", 0)
        p_max = plus.get("max_abs_delta", 0.0)
        m_flips = minus.get("n_flips", 0)
        m_max = minus.get("max_abs_delta", 0.0)
        lines.append(
            f"| {dim} | {bw:.3f} | {p_flips}/{n} | {p_max:.2f} | {m_flips}/{n} | {m_max:.2f} |"
        )
    lines.append("")

    # ---------- Detail: which credits flip for each perturbation ----------
    lines.extend([
        "## 2. Per-Perturbation Grade Flips (+/-5pp)",
        "",
        "Credits whose final grade changes under each perturbation.",
        "",
    ])

    any_flips = False
    for dim in dimensions:
        for direction, label in [("plus_5pp", "+5pp"), ("minus_5pp", "-5pp")]:
            result = perturbation_results[dim].get(direction, {})
            flips = result.get("flips", [])
            if not flips:
                continue
            any_flips = True
            lines.append(f"### {dim} {label} ({len(flips)} flip{'s' if len(flips) != 1 else ''})")
            lines.append("")
            new_w = result.get("new_weights", {})
            if new_w:
                lines.append(f"Perturbed weights: {', '.join(f'{k}={v:.4f}' for k, v in new_w.items() if v > 0)}")
                lines.append("")
            lines.append("| Credit | Old grade | New grade | Old composite | New composite | Delta |")
            lines.append("|--------|:---------:|:---------:|--------------:|--------------:|------:|")
            for f in sorted(flips, key=lambda x: x["id"]):
                name = f["name"][:40]
                lines.append(
                    f"| {f['id']} {name} | {f['base_grade']} | {f['new_grade']} | "
                    f"{f['base_composite']:.2f} | {f['new_composite']:.2f} | {f['delta']:+.2f} |"
                )
            lines.append("")

    if not any_flips:
        lines.append("*No grade flips under any +/-5pp perturbation.*")
        lines.append("")

    # ---------- Leave-one-out summary ----------
    lines.extend([
        "## 3. Leave-One-Out Summary",
        "",
        "For each non-zero dimension, set its weight to 0 and redistribute proportionally.",
        "co_benefits is skipped (weight already 0).",
        "",
        "| Dropped dimension | Flips | Max |delta| | Mean |delta| |",
        "|-------------------|:-----:|:-----------:|:------------:|",
    ])
    for dim in dimensions:
        result = loo_results.get(dim, {})
        if result.get("skipped"):
            lines.append(f"| {dim} | (skipped, wt=0) | — | — |")
            continue
        lines.append(
            f"| {dim} | {result['n_flips']}/{n} | {result['max_abs_delta']:.2f} | {result['mean_abs_delta']:.2f} |"
        )
    lines.append("")

    # ---------- Detail: which credits flip in leave-one-out ----------
    lines.extend([
        "## 4. Per-Dimension Leave-One-Out Flips",
        "",
    ])

    any_loo_flips = False
    for dim in dimensions:
        result = loo_results.get(dim, {})
        if result.get("skipped"):
            continue
        flips = result.get("flips", [])
        if not flips:
            continue
        any_loo_flips = True
        lines.append(f"### Drop {dim} ({len(flips)} flip{'s' if len(flips) != 1 else ''})")
        lines.append("")
        new_w = result.get("new_weights", {})
        if new_w:
            lines.append(f"Redistributed weights: {', '.join(f'{k}={v:.4f}' for k, v in new_w.items() if v > 0)}")
            lines.append("")
        lines.append("| Credit | Old grade | New grade | Old composite | New composite | Delta |")
        lines.append("|--------|:---------:|:---------:|--------------:|--------------:|------:|")
        for f in sorted(flips, key=lambda x: x["id"]):
            name = f["name"][:40]
            lines.append(
                f"| {f['id']} {name} | {f['base_grade']} | {f['new_grade']} | "
                f"{f['base_composite']:.2f} | {f['new_composite']:.2f} | {f['delta']:+.2f} |"
            )
        lines.append("")

    if not any_loo_flips:
        lines.append("*No grade flips under any leave-one-out perturbation.*")
        lines.append("")

    # ---------- Aggregate stability metrics ----------
    total_plus_flips = sum(
        perturbation_results[d].get("plus_5pp", {}).get("n_flips", 0)
        for d in dimensions
    )
    total_minus_flips = sum(
        perturbation_results[d].get("minus_5pp", {}).get("n_flips", 0)
        for d in dimensions
    )
    total_loo_flips = sum(
        loo_results.get(d, {}).get("n_flips", 0)
        for d in dimensions
    )
    n_perturbations = sum(
        1 for d in dimensions
        for direction in ["plus_5pp", "minus_5pp"]
        if not perturbation_results[d].get(direction, {}).get("skipped", False)
    )
    n_loo = sum(1 for d in dimensions if not loo_results.get(d, {}).get("skipped", False))

    max_flips_per_pert = max(
        perturbation_results[d].get(direction, {}).get("n_flips", 0)
        for d in dimensions
        for direction in ["plus_5pp", "minus_5pp"]
    )
    max_flips_loo = max(
        loo_results.get(d, {}).get("n_flips", 0)
        for d in dimensions
        if not loo_results.get(d, {}).get("skipped", False)
    )

    lines.extend([
        "## 5. Aggregate Stability Metrics",
        "",
        f"- Total +/-5pp perturbations tested: {n_perturbations}",
        f"- Total +5pp grade flips: {total_plus_flips}",
        f"- Total -5pp grade flips: {total_minus_flips}",
        f"- Max grade flips in any single +/-5pp perturbation: {max_flips_per_pert}",
        f"- Total leave-one-out tests: {n_loo}",
        f"- Total leave-one-out grade flips: {total_loo_flips}",
        f"- Max grade flips in any single leave-one-out: {max_flips_loo}",
        "",
    ])

    # ---------- Which credits are most perturbation-sensitive ----------
    flip_count_per_credit: dict[str, int] = {}
    for dim in dimensions:
        for direction in ["plus_5pp", "minus_5pp"]:
            for f in perturbation_results[dim].get(direction, {}).get("flips", []):
                cid = f["id"]
                flip_count_per_credit[cid] = flip_count_per_credit.get(cid, 0) + 1
        for f in loo_results.get(dim, {}).get("flips", []):
            cid = f["id"]
            flip_count_per_credit[cid] = flip_count_per_credit.get(cid, 0) + 1

    if flip_count_per_credit:
        lines.extend([
            "## 6. Most Perturbation-Sensitive Credits",
            "",
            "Credits ranked by how many perturbation scenarios (out of "
            f"{n_perturbations} +/-5pp + {n_loo} LOO = {n_perturbations + n_loo} total) "
            "cause a grade flip.",
            "",
            "| Credit | Baseline grade | Composite | Total flips | Buffer to boundary |",
            "|--------|:-------------:|---------:|:-----------:|:------------------:|",
        ])
        boundaries = sorted({b["min"] for b in json.loads(Path(RUBRICS_PATH).read_text())["grades"]})
        for cid, count in sorted(flip_count_per_credit.items(), key=lambda x: -x[1]):
            base_comp, base_grade = baseline[cid]
            # Compute buffer
            above = min((b for b in boundaries if b > base_comp), default=None)
            below = max((b for b in boundaries if b <= base_comp), default=0)
            buf_up = (above - base_comp) if above is not None else float("inf")
            buf_down = base_comp - below
            buffer = min(buf_up, buf_down)
            name = credit_names[cid][:35]
            lines.append(
                f"| {cid} {name} | {base_grade} | {base_comp:.2f} | "
                f"{count}/{n_perturbations + n_loo} | {buffer:.2f} |"
            )
        lines.append("")

    # ---------- Notes ----------
    lines.extend([
        "## Notes",
        "",
        "- Perturbation redistributes the delta proportionally among other non-zero-weight",
        "  dimensions, preserving sum-to-1. Disqualifier caps are re-applied after rescoring.",
        "- Leave-one-out is the extreme case: the entire dimension weight is redistributed.",
        "- A credit with many flips across perturbation scenarios is boundary-adjacent and",
        "  should be flagged in the paper's sensitivity discussion.",
        "- Synthetic stress-test credits (C026-C029) are included; their grades are typically",
        "  locked by disqualifier caps and rarely flip.",
        "",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    main()
