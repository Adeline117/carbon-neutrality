#!/usr/bin/env python3
"""
A2 design-note gate: compute every candidate v0.4 scoring mechanism against the
v0.3 pilot dataset and print a comparison table.

Options:
  v0_3    = status quo (current v0.3 rubric)
  rev12   = Rev-1 reweight + Rev-2 removal bonus (the naive proposal)
  alt1    = Rev-1 reweight + multiplicative 1.05 premium on same condition
  alt2    = Geometric-mean technical core + linear remainder
  alt3    = Safeguards-gate: co_benefits weight -> 0, redistributed; gate at BBB if harm

Writes a markdown comparison table to stdout.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).parent
CREDITS = json.loads((HERE / "credits.json").read_text())["credits"]

# -------- shared helpers --------

GRADE_ORDER = ["B", "BB", "BBB", "A", "AA", "AAA"]
BANDS = [
    ("AAA", 90, 100),
    ("AA",  75,  89.999999),
    ("A",   60,  74.999999),
    ("BBB", 45,  59.999999),
    ("BB",  30,  44.999999),
    ("B",    0,  29.999999),
]


def grade(score: float) -> str:
    for name, lo, hi in BANDS:
        if lo <= score <= hi:
            return name
    return "B"


def apply_dq_caps(g: str, flags: list[str]) -> str:
    caps = {
        "double_counting":      "B",
        "failed_verification":  "B",
        "human_rights":         "B",
        "sanctioned_registry":  "BB",
        "no_third_party":       "BBB",
    }
    for f in flags:
        if f in caps:
            c = caps[f]
            if GRADE_ORDER.index(g) > GRADE_ORDER.index(c):
                g = c
    return g


# -------- scoring mechanisms --------

def score_v0_3(s: dict) -> float:
    w = {
        "removal_type":         0.20,
        "additionality":        0.20,
        "permanence":           0.15,
        "mrv_grade":            0.15,
        "vintage_year":         0.10,
        "co_benefits":          0.10,
        "registry_methodology": 0.10,
    }
    return sum(s[k] * v for k, v in w.items())


_REV1_WEIGHTS = {
    "removal_type":         0.225,
    "additionality":        0.20,
    "permanence":           0.15,
    "mrv_grade":            0.175,
    "vintage_year":         0.10,
    "co_benefits":          0.075,
    "registry_methodology": 0.075,
}


def _removal_bonus_condition(s: dict) -> bool:
    return s["removal_type"] >= 90 and s["permanence"] >= 90 and s["mrv_grade"] >= 85


def score_rev12(s: dict) -> float:
    base = sum(s[k] * v for k, v in _REV1_WEIGHTS.items())
    bonus = 5.0 if _removal_bonus_condition(s) else 0.0
    return min(100.0, base + bonus)


def score_alt1(s: dict) -> float:
    """Multiplicative 1.05 premium on the same condition."""
    base = sum(s[k] * v for k, v in _REV1_WEIGHTS.items())
    if _removal_bonus_condition(s):
        base = base * 1.05
    return min(100.0, base)


def score_alt2(s: dict) -> float:
    """
    Geometric-mean technical core + linear remainder.

    composite = 0.60 * geomean(removal_type, permanence, mrv_grade)
              + 0.40 * weighted_mean(additionality, vintage, co_benefits, registry)

    Weights of the 'remainder' four dimensions are their v0.2 weights renormalised
    to sum to 1 (add=0.40, vin=0.20, cob=0.20, reg=0.20), then scaled by 0.40.
    """
    r, p, m = s["removal_type"], s["permanence"], s["mrv_grade"]
    # geomean; guard against zero
    if min(r, p, m) == 0:
        tech = 0.0
    else:
        tech = (r * p * m) ** (1 / 3)

    # remainder: original weights 0.20/0.10/0.10/0.10 sum to 0.50 -> normalised to 0.40/0.20/0.20/0.20
    rem = (
        0.40 * s["additionality"]
        + 0.20 * s["vintage_year"]
        + 0.20 * s["co_benefits"]
        + 0.20 * s["registry_methodology"]
    )

    return 0.60 * tech + 0.40 * rem


_ALT3_WEIGHTS = {
    # Rev-1 weights with co_benefits=0, its 0.075 redistributed across the three
    # technical dimensions (each gets +0.025).
    "removal_type":         0.225 + 0.025,   # 0.25
    "additionality":        0.20,
    "permanence":           0.15  + 0.025,   # 0.175
    "mrv_grade":            0.175 + 0.025,   # 0.20
    "vintage_year":         0.10,
    "co_benefits":          0.0,
    "registry_methodology": 0.075,
}


def score_alt3(s: dict) -> float:
    """Safeguards-gate: co_benefits not scored; acts as a BBB cap only if harm flagged."""
    return sum(s[k] * v for k, v in _ALT3_WEIGHTS.items())


# -------- gate logic for Alt-3 --------

def apply_alt3_gate(g: str, credit: dict) -> str:
    """In Alt-3, co_benefits < some_threshold with documented harm caps at BBB.
    We do not have a 'harm_flag' field in the pilot, so we approximate:
    co_benefits < 10 is the rubric's 'None / documented negative externalities' band,
    so we treat it as a harm flag for this analysis."""
    cob = credit["scores"]["co_benefits"]
    if cob < 10:
        if GRADE_ORDER.index(g) > GRADE_ORDER.index("BBB"):
            return "BBB"
    return g


# -------- analysis --------

def analyse():
    mechanisms = [
        ("v0_3",  score_v0_3,  None),
        ("rev12", score_rev12, None),
        ("alt1",  score_alt1,  None),
        ("alt2",  score_alt2,  None),
        ("alt3",  score_alt3,  apply_alt3_gate),
    ]

    rows = []
    for c in CREDITS:
        s = c["scores"]
        row = {"id": c["id"], "name": c["name"][:40], "type": c["type"][:30]}
        for name, fn, extra_gate in mechanisms:
            raw = round(fn(s), 2)
            g = grade(raw)
            g = apply_dq_caps(g, c.get("disqualifiers", []))
            if extra_gate is not None:
                g = extra_gate(g, c)
            row[f"{name}_score"] = raw
            row[f"{name}_grade"] = g
        rows.append(row)

    return rows, mechanisms


def fmt_table(rows, mechanisms):
    headers = ["ID", "Name", "Type"]
    for name, _, _ in mechanisms:
        headers.append(f"{name}")
        headers.append(f"  ({name[:4]})")

    # compact summary: ID, name, 5 (score/grade) pairs
    lines = [
        "| ID | Name | v0.3 | rev12 | alt1 | alt2 | alt3 |",
        "|----|------|------|-------|------|------|------|",
    ]
    for r in rows:
        cells = [
            r["id"],
            r["name"],
            f'{r["v0_3_score"]:.1f} {r["v0_3_grade"]}',
            f'{r["rev12_score"]:.1f} {r["rev12_grade"]}',
            f'{r["alt1_score"]:.1f} {r["alt1_grade"]}',
            f'{r["alt2_score"]:.1f} {r["alt2_grade"]}',
            f'{r["alt3_score"]:.1f} {r["alt3_grade"]}',
        ]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def distribution(rows, key_prefix):
    dist = {}
    for r in rows:
        g = r[f"{key_prefix}_grade"]
        dist[g] = dist.get(g, 0) + 1
    return dist


def main():
    rows, mechs = analyse()
    print("# Option Comparison\n")
    print(fmt_table(rows, mechs))
    print()
    print("## Grade distributions\n")
    print("| Grade | v0.3 | rev12 | alt1 | alt2 | alt3 |")
    print("|-------|------|-------|------|------|------|")
    for g in ["AAA", "AA", "A", "BBB", "BB", "B"]:
        cells = [g]
        for name, _, _ in mechs:
            d = distribution(rows, name)
            cells.append(str(d.get(g, 0)))
        print("| " + " | ".join(cells) + " |")
    print()

    # key credits spotlight
    spotlight = ["C001", "C002", "C003", "C005", "C006", "C007", "C010", "C014"]
    print("## Spotlight: load-bearing credits\n")
    print("| ID | Name | v0.3 | rev12 | alt1 | alt2 | alt3 | Notes |")
    print("|----|------|------|-------|------|------|------|-------|")
    notes = {
        "C001": "Orca DACCS — must reach AAA",
        "C002": "Heirloom DAC — must reach AAA",
        "C003": "CarbonCure — mrv_grade=85 threshold edge",
        "C005": "Pacific Biochar — high-quality NBS",
        "C006": "Husk biochar — co-benefit-heavy NBS",
        "C007": "Brazilian reforestation — BCT headline; must stay >=77 for 2pt buffer",
        "C010": "Kenya cookstoves — co-benefit-heavy avoidance",
        "C014": "Plan Vivo agroforestry — co-benefit-heavy borderline A",
    }
    for rid in spotlight:
        r = next(x for x in rows if x["id"] == rid)
        cells = [
            r["id"],
            r["name"],
            f'{r["v0_3_score"]:.1f} {r["v0_3_grade"]}',
            f'{r["rev12_score"]:.1f} {r["rev12_grade"]}',
            f'{r["alt1_score"]:.1f} {r["alt1_grade"]}',
            f'{r["alt2_score"]:.1f} {r["alt2_grade"]}',
            f'{r["alt3_score"]:.1f} {r["alt3_grade"]}',
            notes[rid],
        ]
        print("| " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
