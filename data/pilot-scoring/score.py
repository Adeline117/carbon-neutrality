#!/usr/bin/env python3
"""
Pilot scoring script for the on-chain carbon credit quality rating framework.

Reads:
  ../scoring-rubrics/index.json      -- weights, grade bands, disqualifiers
  ./credits.json                     -- default dataset
  --credits PATH                     -- override with an alternate dataset (e.g. ../tokenized-pilot/credits.json)

Writes output files as siblings of the credits file:
  scores.csv                         -- per-credit composite, grades, per-dimension scores
  scores.md                          -- markdown summary table
  sensitivity.md                     -- (--sensitivity only) weight perturbation + leave-one-out

Usage:
  python3 score.py
  python3 score.py --sensitivity
  python3 score.py --credits ../tokenized-pilot/credits.json
  python3 score.py --credits ../tokenized-pilot/credits.json --sensitivity
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
RUBRICS = HERE.parent / "scoring-rubrics"


def load_dimension_adjustments() -> dict[str, list[dict]]:
    """Walk the per-dimension rubric files and collect any 'adjustments' blocks.
    Returns {dimension_id: [adjustment, ...]}.
    Adjustments are applied by apply_dimension_adjustments() before composite calc."""
    out: dict[str, list[dict]] = {}
    for f in sorted(RUBRICS.glob("[0-9][0-9]_*.json")):
        rubric = json.loads(f.read_text())
        if "adjustments" in rubric:
            out[rubric["id"]] = rubric["adjustments"]
    return out


def apply_dimension_adjustments(
    base_scores: dict[str, int],
    credit_adjustments: list[str],
    all_adjustments: dict[str, list[dict]],
) -> dict[str, int]:
    """Apply any v0.4.1+ dimension-level adjustments flagged by the credit.
    Returns a new score dict; does not mutate input. Scores are clamped to [0, 100]."""
    adjusted = dict(base_scores)
    for dim_id, adjs in all_adjustments.items():
        for adj in adjs:
            if adj["id"] in credit_adjustments:
                if adj.get("effect") == "delta":
                    adjusted[dim_id] = max(0, min(100, adjusted[dim_id] + adj["delta"]))
                elif adj.get("effect") == "score_cap":
                    adjusted[dim_id] = min(adjusted[dim_id], adj["cap"])
    return adjusted


def credits_path() -> Path:
    """Default to ./credits.json unless --credits PATH is given."""
    if "--credits" in sys.argv:
        i = sys.argv.index("--credits")
        if i + 1 >= len(sys.argv):
            raise SystemExit("--credits requires a path argument")
        return Path(sys.argv[i + 1]).resolve()
    return HERE / "credits.json"


def load_rubric_index() -> dict:
    with (RUBRICS / "index.json").open() as f:
        return json.load(f)


def load_credits(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def composite(scores: dict, weights: dict) -> float:
    return sum(scores[dim] * weights[dim] for dim in weights)


def grade_from_score(score: float, bands: list[dict]) -> str:
    # bands are declared high-to-low in index.json with integer mins.
    # Match the Solidity contract's logic exactly: return the first band
    # whose min is <= score. This handles non-integer composites correctly
    # (e.g., 59.53 falls into BBB, not into a gap between BBB.max=59 and A.min=60).
    for band in bands:
        if score >= band["min"]:
            return band["grade"]
    return "B"


GRADE_ORDER = ["B", "BB", "BBB", "A", "AA", "AAA"]


def cap_grade(grade: str, cap: str) -> str:
    """Return the lower of grade and cap per GRADE_ORDER."""
    if GRADE_ORDER.index(grade) <= GRADE_ORDER.index(cap):
        return grade
    return cap


def apply_disqualifiers(grade: str, flags: list[str], dq_spec: list[dict]) -> tuple[str, list[str]]:
    """Apply all disqualifier caps. Returns (final_grade, list of applied caps)."""
    applied = []
    final = grade
    for dq in dq_spec:
        if dq["id"] in flags:
            new = cap_grade(final, dq["grade_cap"])
            if new != final:
                applied.append(f"{dq['id']}->{dq['grade_cap']}")
                final = new
    return final, applied


def main() -> None:
    rubrics = load_rubric_index()
    creds_path = credits_path()
    credits = load_credits(creds_path)
    out_dir = creds_path.parent

    weights = {d["id"]: d["weight"] for d in rubrics["dimensions"]}
    dimensions = list(weights.keys())
    grade_bands = rubrics["grades"]
    dq_spec = rubrics["disqualifiers"]
    dim_adjustments = load_dimension_adjustments()

    rows = []
    for credit in credits["credits"]:
        base_scores = credit["scores"]
        # sanity: all dimensions present
        missing = [d for d in dimensions if d not in base_scores]
        if missing:
            raise SystemExit(f"Credit {credit['id']} missing dimensions: {missing}")

        # v0.4.1: apply dimension-level adjustments (e.g. commercial_plantation_arr)
        # before composite. Credit flags live in the "adjustments" list (parallel to
        # "disqualifiers"). Falls back to base_scores if no adjustments apply.
        credit_adjustments = credit.get("adjustments", [])
        scores = apply_dimension_adjustments(base_scores, credit_adjustments, dim_adjustments)

        comp = composite(scores, weights)
        nominal = grade_from_score(comp, grade_bands)
        final, applied = apply_disqualifiers(nominal, credit.get("disqualifiers", []), dq_spec)

        rows.append(
            {
                "id": credit["id"],
                "name": credit["name"],
                "type": credit.get("type", ""),
                "registry": credit.get("registry") or credit.get("underlying_registry", ""),
                "vintage": credit.get("vintage_year", ""),
                **{f"d_{d}": scores[d] for d in dimensions},
                "composite": round(comp, 2),
                "grade_nominal": nominal,
                "grade_final": final,
                "disqualifiers": ",".join(credit.get("disqualifiers", [])),
                "adjustments": ",".join(credit_adjustments),
                "caps_applied": ",".join(applied),
            }
        )

    # write CSV
    csv_path = out_dir / "scores.csv"
    fieldnames = list(rows[0].keys())
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # write markdown summary
    md = ["# Pilot Scoring Results", ""]
    md.append(f"Dataset: {len(rows)} credits   Weights: " + ", ".join(f"{k}={v}" for k, v in weights.items()))
    md.append("")
    md.append("| ID | Name | Type | Composite | Nominal | Final | Caps |")
    md.append("|----|------|------|-----------|---------|-------|------|")
    for r in sorted(rows, key=lambda x: -x["composite"]):
        name = r["name"][:40]
        typ = r["type"][:35]
        md.append(
            f"| {r['id']} | {name} | {typ} | {r['composite']} | {r['grade_nominal']} | {r['grade_final']} | {r['caps_applied'] or '-'} |"
        )
    md.append("")

    # grade distribution
    dist: dict[str, int] = {}
    for r in rows:
        dist[r["grade_final"]] = dist.get(r["grade_final"], 0) + 1
    md.append("## Final grade distribution")
    md.append("")
    md.append("| Grade | Count | Share |")
    md.append("|-------|-------|-------|")
    for g in ["AAA", "AA", "A", "BBB", "BB", "B"]:
        c = dist.get(g, 0)
        md.append(f"| {g} | {c} | {c/len(rows):.0%} |")
    md.append("")

    (out_dir / "scores.md").write_text("\n".join(md))

    # terminal preview
    print(f"Scored {len(rows)} credits from {creds_path} -> {csv_path}")
    print(f"Grade distribution (final): {dist}")

    if "--sensitivity" in sys.argv:
        write_sensitivity(credits, rubrics, rows, out_dir)


def write_sensitivity(credits: dict, rubrics: dict, baseline_rows: list[dict], out_dir: Path) -> None:
    """Weight-perturbation and leave-one-out sensitivity analyses.

    Writes sensitivity.md in `out_dir`. Uses the already-computed baseline grades
    to count grade flips as each weight is perturbed. Disqualifier caps are
    re-applied so flips reflect the full pipeline.
    """
    weights = {d["id"]: d["weight"] for d in rubrics["dimensions"]}
    dimensions = list(weights.keys())
    grade_bands = rubrics["grades"]
    dq_spec = rubrics["disqualifiers"]

    baseline_grades = {r["id"]: r["grade_final"] for r in baseline_rows}

    def score_all(w: dict) -> dict[str, str]:
        out = {}
        for credit in credits["credits"]:
            scores = credit["scores"]
            comp = sum(scores[d] * w[d] for d in dimensions)
            g = grade_from_score(comp, grade_bands)
            g, _ = apply_disqualifiers(g, credit.get("disqualifiers", []), dq_spec)
            out[credit["id"]] = g
        return out

    md = ["# Sensitivity Analysis", ""]
    md.append(f"Baseline grades from v0.4 weights: {weights}")
    md.append("")

    # --- weight perturbation: +/-5pp per weight, redistributing uniformly ---
    md.append("## 1. Weight perturbation (+/-5pp)")
    md.append("")
    md.append("For each dimension, add or subtract 5 percentage points of weight and redistribute the delta proportionally across the other dimensions. Report the number of credits whose final grade changes.")
    md.append("")
    md.append("| Dimension | Baseline | +5pp flips | -5pp flips |")
    md.append("|-----------|----------|-----------|-----------|")

    n = len(credits["credits"])
    for dim in dimensions:
        flips_plus = 0
        flips_minus = 0
        for delta in (+0.05, -0.05):
            new_w = dict(weights)
            target = new_w[dim] + delta
            if target < 0:
                continue
            new_w[dim] = target
            others = [d for d in dimensions if d != dim and weights[d] > 0]
            if not others:
                continue
            # Redistribute the delta proportionally among non-zero other weights
            other_sum = sum(weights[d] for d in others)
            for d in others:
                new_w[d] = weights[d] - delta * (weights[d] / other_sum)
            # renormalise against float error
            total = sum(new_w.values())
            if total > 0:
                new_w = {k: v / total for k, v in new_w.items()}
            new_grades = score_all(new_w)
            flips = sum(1 for cid, g in new_grades.items() if g != baseline_grades[cid])
            if delta > 0:
                flips_plus = flips
            else:
                flips_minus = flips
        md.append(f"| {dim} | {weights[dim]:.3f} | {flips_plus}/{n} | {flips_minus}/{n} |")
    md.append("")

    # --- leave-one-out: drop each dimension, redistribute proportionally ---
    md.append("## 2. Leave-one-out")
    md.append("")
    md.append("For each dimension with nonzero weight, set its weight to 0 and redistribute proportionally to the others. Report grade flips. (co_benefits is skipped since its v0.4 weight is already 0.)")
    md.append("")
    md.append("| Dropped dimension | Flips |")
    md.append("|-------------------|-------|")

    for dim in dimensions:
        if weights[dim] == 0:
            continue
        new_w = dict(weights)
        dropped = new_w[dim]
        new_w[dim] = 0.0
        remaining = sum(v for k, v in new_w.items() if v > 0)
        if remaining == 0:
            continue
        for k in new_w:
            if new_w[k] > 0:
                new_w[k] = new_w[k] + dropped * (new_w[k] / remaining)
        new_grades = score_all(new_w)
        flips = sum(1 for cid, g in new_grades.items() if g != baseline_grades[cid])
        md.append(f"| {dim} | {flips}/{n} |")
    md.append("")

    # --- boundary-proximity analysis: automatically find the most-fragile credits ---
    md.append("## 3. Key-credit stability under score perturbation")
    md.append("")
    md.append("Automatically identifies the credits closest to a grade boundary. Credits with buffer < 2.0 are grade-sensitive to small per-dimension rescoring.")
    md.append("")
    md.append("| Credit | Current grade | Current composite | Nearest boundary | Buffer |")
    md.append("|--------|---------------|-------------------|------------------|--------|")

    boundaries = sorted({b["min"] for b in grade_bands})

    def buffer_for(comp: float) -> tuple[float, int]:
        above = min((b for b in boundaries if b > comp), default=None)
        below = max((b for b in boundaries if b <= comp), default=0)
        buf_up = (above - comp) if above is not None else float("inf")
        buf_down = comp - below
        if buf_up < buf_down:
            return buf_up, above
        return buf_down, below

    scored = []
    for row in baseline_rows:
        # skip synthetic disqualifier stress tests from boundary analysis
        if "SYNTHETIC" in row.get("name", ""):
            continue
        buf, nearest = buffer_for(row["composite"])
        scored.append((buf, row, nearest))

    # sort by ascending buffer; show top 6 most fragile
    scored.sort(key=lambda x: x[0])
    for buf, row, nearest in scored[:6]:
        name = row["name"][:32]
        md.append(f"| {row['id']} {name} | {row['grade_final']} | {row['composite']} | {nearest} | {buf:.2f} |")
    md.append("")

    md.append("## 4. Interpretation notes")
    md.append("")
    md.append("- Weight-perturbation flips near zero or one credit per perturbation indicate stable weighting; multi-credit flips indicate fragility that should be flagged to expert reviewers.")
    md.append("- Leave-one-out is a stronger test: if dropping a dimension leaves grades largely unchanged, the dimension is redundant with the others.")
    md.append("- Buffer < 2.0 in the key-credit table indicates a credit whose grade is sensitive to per-dimension rescoring and should be flagged in the paper's sensitivity discussion.")
    md.append("")

    (out_dir / "sensitivity.md").write_text("\n".join(md))
    print(f"Wrote sensitivity analysis -> {out_dir / 'sensitivity.md'}")


if __name__ == "__main__":
    main()
