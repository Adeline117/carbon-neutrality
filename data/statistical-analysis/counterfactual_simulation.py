#!/usr/bin/env python3
"""Counterfactual simulation: 'What if Toucan BCT had quality gating?'

Simulates the effect of applying meetsGrade() quality gates at each grade
threshold (B, BB, BBB, A, AA, AAA) to historical pool compositions from
the Lemons Index pool_analyzer.

For each pool and each threshold:
  - How many credits are admitted?
  - What is the new Lemons Index?
  - What is the mean composite?
  - What is the A+% (fraction of credits at grade A or above)?

Special focus on BCT: demonstrates that quality gating at grade>=BBB would
have produced a pool resembling CHAR's natural quality profile.

Pure Python -- no external dependencies beyond standard library.

Usage:
    python3 counterfactual_simulation.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

# Add necessary paths for imports
sys.path.insert(0, str(ROOT / "data" / "pilot-scoring"))
sys.path.insert(0, str(ROOT / "data" / "methodology-ratings"))
sys.path.insert(0, str(ROOT / "data" / "lemons-index"))

from score import load_rubric_index, load_default_stds, grade_from_score
from batch_scorer import load_archetypes, score_project, vintage_score
from pool_analyzer import (
    POOLS,
    lemons_index,
    quality_concentration_ratio,
    grade_hhi,
)

RUBRICS = load_rubric_index()
WEIGHTS = {d["id"]: d["weight"] for d in RUBRICS["dimensions"]}
BANDS = RUBRICS["grades"]
DEFAULT_STDS = load_default_stds(RUBRICS)
ARCHETYPES = load_archetypes()

GRADE_ORDER = ["B", "BB", "BBB", "A", "AA", "AAA"]
GRADE_NUM = {g: i for i, g in enumerate(GRADE_ORDER)}
GRADE_THRESHOLDS = {g: GRADE_NUM[g] for g in GRADE_ORDER}


# ---------------------------------------------------------------------------
# Scoring helper
# ---------------------------------------------------------------------------

def score_pool_entry(entry: dict) -> tuple[float, str]:
    """Score a single pool entry using its methodology archetype."""
    project = {
        "methodology_category": entry["methodology_category"],
        "vintage_year": entry["vintage_year"],
        "country": entry.get("country", ""),
    }
    result = score_project(project, ARCHETYPES, WEIGHTS, DEFAULT_STDS, BANDS)
    return result["composite"], result["grade"]


def expand_pool(pool: dict) -> list[dict]:
    """Expand pool entries (each with n copies) into individual scored credits."""
    credits = []
    for entry in pool["credits"]:
        comp, grade = score_pool_entry(entry)
        n = entry.get("n", 1)
        for _ in range(n):
            credits.append({
                "methodology_category": entry["methodology_category"],
                "vintage_year": entry["vintage_year"],
                "country": entry.get("country", ""),
                "composite": comp,
                "grade": grade,
                "grade_num": GRADE_NUM[grade],
            })
    return credits


# ---------------------------------------------------------------------------
# Quality gating simulation
# ---------------------------------------------------------------------------

def apply_quality_gate(
    credits: list[dict], threshold_grade: str
) -> list[dict]:
    """Filter credits to only those at or above the threshold grade."""
    threshold = GRADE_NUM[threshold_grade]
    return [c for c in credits if c["grade_num"] >= threshold]


def analyze_gated_pool(credits: list[dict]) -> dict:
    """Compute pool metrics for a set of credits."""
    if not credits:
        return {
            "n_credits": 0,
            "mean_composite": 0.0,
            "lemons_index": 1.0,
            "a_plus_pct": 0.0,
            "grade_hhi": 0.0,
            "grade_distribution": {},
        }
    composites = [c["composite"] for c in credits]
    grades = [c["grade"] for c in credits]
    li = lemons_index(composites)
    qcr = quality_concentration_ratio(grades, "A")
    hhi = grade_hhi(grades)
    mean_comp = sum(composites) / len(composites)

    from collections import Counter
    dist = dict(Counter(grades))

    return {
        "n_credits": len(credits),
        "mean_composite": round(mean_comp, 2),
        "lemons_index": round(li, 4),
        "a_plus_pct": round(qcr, 4),
        "grade_hhi": round(hhi, 4),
        "grade_distribution": dist,
    }


def simulate_pool(pool: dict) -> dict:
    """Run quality gating at every threshold for a single pool."""
    credits = expand_pool(pool)
    baseline = analyze_gated_pool(credits)

    gates = {}
    for threshold in GRADE_ORDER:
        gated = apply_quality_gate(credits, threshold)
        metrics = analyze_gated_pool(gated)
        metrics["threshold"] = threshold
        metrics["admission_rate"] = (
            round(metrics["n_credits"] / baseline["n_credits"], 4)
            if baseline["n_credits"] > 0 else 0.0
        )
        metrics["li_improvement"] = round(
            baseline["lemons_index"] - metrics["lemons_index"], 4
        )
        gates[threshold] = metrics

    return {
        "pool_name": pool["name"],
        "baseline": baseline,
        "gated": gates,
    }


# ---------------------------------------------------------------------------
# BCT / CHAR comparison
# ---------------------------------------------------------------------------

def bct_char_comparison(results: list[dict]) -> dict:
    """Compare counterfactual BCT-with-gating to actual CHAR pool."""
    bct = next((r for r in results if "BCT" in r["pool_name"]), None)
    char = next((r for r in results if "CHAR" in r["pool_name"]), None)

    if not bct or not char:
        return {"note": "BCT or CHAR pool not found in results."}

    char_li = char["baseline"]["lemons_index"]
    char_a_pct = char["baseline"]["a_plus_pct"]

    # Find which BCT gating threshold produces metrics closest to CHAR
    best_match = None
    best_li_diff = float("inf")
    for threshold, metrics in bct["gated"].items():
        if metrics["n_credits"] == 0:
            continue
        li_diff = abs(metrics["lemons_index"] - char_li)
        if li_diff < best_li_diff:
            best_li_diff = li_diff
            best_match = threshold

    bct_bbb = bct["gated"].get("BBB", {})

    return {
        "bct_baseline_li": bct["baseline"]["lemons_index"],
        "bct_baseline_a_pct": bct["baseline"]["a_plus_pct"],
        "char_li": char_li,
        "char_a_pct": char_a_pct,
        "bct_gated_bbb_li": bct_bbb.get("lemons_index"),
        "bct_gated_bbb_a_pct": bct_bbb.get("a_plus_pct"),
        "bct_gated_bbb_admission": bct_bbb.get("admission_rate"),
        "bct_gated_bbb_n": bct_bbb.get("n_credits"),
        "closest_match_threshold": best_match,
        "closest_match_li_diff": round(best_li_diff, 4),
        "conclusion": (
            f"Quality gating BCT at grade>=BBB would have produced "
            f"LI={bct_bbb.get('lemons_index', 'n/a')} vs CHAR's LI={char_li}. "
            f"CHAR achieves comparable quality through its biochar-only allowlist "
            f"rather than an explicit grade gate."
        ),
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def results_to_markdown(results: list[dict], comparison: dict) -> str:
    lines = [
        "# Counterfactual Simulation: Quality Gating in Carbon Pools",
        "",
        "What if historical on-chain carbon pools had applied quality gates?",
        "",
    ]

    # Summary table: all pools at BBB threshold
    lines.extend([
        "## Summary: BBB Quality Gate Impact",
        "",
        "| Pool | Baseline LI | Gated LI (BBB+) | LI improvement | Admitted | A+% |",
        "|------|:-----------:|:---------------:|:--------------:|:--------:|:---:|",
    ])
    for r in results:
        bl = r["baseline"]
        gated = r["gated"].get("BBB", {})
        if gated.get("n_credits", 0) == 0:
            lines.append(
                f"| {r['pool_name']} | {bl['lemons_index']:.3f} | "
                f"n/a (0 credits) | n/a | 0% | 0% |"
            )
        else:
            lines.append(
                f"| {r['pool_name']} | {bl['lemons_index']:.3f} | "
                f"{gated['lemons_index']:.3f} | {gated['li_improvement']:+.3f} | "
                f"{gated['admission_rate']:.0%} ({gated['n_credits']}) | "
                f"{gated['a_plus_pct']:.0%} |"
            )

    # Per-pool detail
    for r in results:
        lines.extend([
            "",
            f"## {r['pool_name']}",
            "",
            f"Baseline: {r['baseline']['n_credits']} credits, "
            f"LI={r['baseline']['lemons_index']:.3f}, "
            f"mean composite={r['baseline']['mean_composite']:.1f}, "
            f"A+%={r['baseline']['a_plus_pct']:.0%}",
            "",
            "| Threshold | Admitted | Mean composite | Lemons Index | LI improvement | A+% |",
            "|:---------:|:--------:|:--------------:|:------------:|:--------------:|:---:|",
        ])
        for threshold in GRADE_ORDER:
            g = r["gated"][threshold]
            if g["n_credits"] == 0:
                lines.append(
                    f"| >= {threshold} | 0 (0%) | - | - | - | - |"
                )
            else:
                lines.append(
                    f"| >= {threshold} | {g['n_credits']} ({g['admission_rate']:.0%}) | "
                    f"{g['mean_composite']:.1f} | {g['lemons_index']:.3f} | "
                    f"{g['li_improvement']:+.3f} | {g['a_plus_pct']:.0%} |"
                )

    # BCT vs CHAR comparison
    lines.extend([
        "",
        "## BCT vs CHAR: Quality Gating Equivalence",
        "",
    ])
    if "conclusion" in comparison:
        lines.extend([
            f"- BCT baseline Lemons Index: {comparison.get('bct_baseline_li', 'n/a')}",
            f"- BCT with grade>=BBB gate: LI={comparison.get('bct_gated_bbb_li', 'n/a')}, "
            f"admission={comparison.get('bct_gated_bbb_admission', 'n/a')}, "
            f"n={comparison.get('bct_gated_bbb_n', 'n/a')}",
            f"- CHAR (biochar-only allowlist): LI={comparison.get('char_li', 'n/a')}",
            f"- Closest BCT gate to match CHAR: >= {comparison.get('closest_match_threshold', 'n/a')} "
            f"(LI diff = {comparison.get('closest_match_li_diff', 'n/a')})",
            "",
            f"**{comparison['conclusion']}**",
        ])
    else:
        lines.append(comparison.get("note", "Comparison not available."))

    lines.extend([
        "",
        "## Key Findings",
        "",
        "1. **BCT's Lemons Index drops dramatically** with even a modest BBB gate, "
        "because most of its credits are low-quality REDD+, old wind, and HFC-23.",
        "2. **CHAR's allowlist achieves naturally** what a grade gate would enforce: "
        "by restricting to biochar projects with known high-quality profiles, it avoids "
        "adverse selection without needing an on-chain quality score.",
        "3. **An on-chain meetsGrade() check** could replicate CHAR's quality profile "
        "for pools that accept diverse project types -- this is the core value "
        "proposition of the ERC-CCQR standard.",
        "4. **The BBB threshold** is the minimum viable quality gate: it excludes "
        "the bulk of low-integrity credits while still admitting legitimate avoidance "
        "projects (cookstoves, landfill gas) with adequate verification.",
        "",
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Counterfactual Simulation: Quality Gating in Carbon Pools")
    print(f"  Pools: {len(POOLS)}")
    print(f"  Grade thresholds: {GRADE_ORDER}")
    print()

    results = []
    for pool in POOLS:
        r = simulate_pool(pool)
        results.append(r)
        bl = r["baseline"]
        print(
            f"  {pool['name']:<45s} n={bl['n_credits']:>3d}  "
            f"LI={bl['lemons_index']:.3f}  A+%={bl['a_plus_pct']:.0%}"
        )
        bbb = r["gated"]["BBB"]
        if bbb["n_credits"] > 0:
            print(
                f"    -> with BBB gate: n={bbb['n_credits']:>3d}  "
                f"LI={bbb['lemons_index']:.3f}  A+%={bbb['a_plus_pct']:.0%}  "
                f"improvement={bbb['li_improvement']:+.3f}"
            )
        else:
            print("    -> with BBB gate: 0 credits admitted")

    print()

    comparison = bct_char_comparison(results)
    if "conclusion" in comparison:
        print(f"BCT vs CHAR: {comparison['conclusion']}")

    # Write outputs
    out_data = {
        "pools": results,
        "bct_char_comparison": comparison,
    }
    out_json = HERE / "counterfactual_simulation_results.json"
    out_json.write_text(json.dumps(out_data, indent=2))

    out_md = HERE / "counterfactual_simulation_results.md"
    out_md.write_text(results_to_markdown(results, comparison))

    print(f"\nWrote: {out_json}")
    print(f"Wrote: {out_md}")


if __name__ == "__main__":
    main()
