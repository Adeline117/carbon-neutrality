#!/usr/bin/env python3
"""
Pilot scoring script for the on-chain carbon credit quality rating framework.

Reads:
  ../scoring-rubrics/index.json   -- weights, grade bands, disqualifiers
  ./credits.json                  -- per-credit dimension scores and disqualifier flags

Writes:
  ./scores.csv                    -- composite score, grade (nominal and post-disqualifier), per-dimension scores
  ./scores.md                     -- markdown summary table

Usage:
  python3 score.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
RUBRICS = HERE.parent / "scoring-rubrics"


def load_rubric_index() -> dict:
    with (RUBRICS / "index.json").open() as f:
        return json.load(f)


def load_credits() -> dict:
    with (HERE / "credits.json").open() as f:
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
    credits = load_credits()

    weights = {d["id"]: d["weight"] for d in rubrics["dimensions"]}
    dimensions = list(weights.keys())
    grade_bands = rubrics["grades"]
    dq_spec = rubrics["disqualifiers"]

    rows = []
    for credit in credits["credits"]:
        scores = credit["scores"]
        # sanity: all dimensions present
        missing = [d for d in dimensions if d not in scores]
        if missing:
            raise SystemExit(f"Credit {credit['id']} missing dimensions: {missing}")

        comp = composite(scores, weights)
        nominal = grade_from_score(comp, grade_bands)
        final, applied = apply_disqualifiers(nominal, credit.get("disqualifiers", []), dq_spec)

        rows.append(
            {
                "id": credit["id"],
                "name": credit["name"],
                "type": credit["type"],
                "registry": credit["registry"],
                "vintage": credit["vintage_year"],
                **{f"d_{d}": scores[d] for d in dimensions},
                "composite": round(comp, 2),
                "grade_nominal": nominal,
                "grade_final": final,
                "disqualifiers": ",".join(credit.get("disqualifiers", [])),
                "caps_applied": ",".join(applied),
            }
        )

    # write CSV
    csv_path = HERE / "scores.csv"
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

    (HERE / "scores.md").write_text("\n".join(md))

    # terminal preview
    print(f"Scored {len(rows)} credits -> {csv_path}")
    print(f"Grade distribution (final): {dist}")


if __name__ == "__main__":
    main()
