#!/usr/bin/env python3
"""Adversarial credit tests: verify the framework resists known gaming vectors.

Each test constructs a credit designed to exploit a specific rubric weakness.
If the grade is wrong, the rubric has a vulnerability.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "data" / "pilot-scoring"))
from score import (
    apply_dimension_adjustments,
    apply_disqualifiers,
    composite,
    grade_from_score,
    load_dimension_adjustments,
    load_rubric_index,
)

RUBRICS = load_rubric_index()
WEIGHTS = {d["id"]: d["weight"] for d in RUBRICS["dimensions"]}
BANDS = RUBRICS["grades"]
DQ_SPEC = RUBRICS["disqualifiers"]
DIM_ADJS = load_dimension_adjustments()


def _score_and_grade(scores, disqualifiers=None, adjustments=None):
    adj_scores = apply_dimension_adjustments(scores, adjustments or [], DIM_ADJS)
    comp = composite(adj_scores, WEIGHTS)
    grade = grade_from_score(comp, BANDS)
    final, _ = apply_disqualifiers(grade, disqualifiers or [], DQ_SPEC)
    return comp, final


def test_narrative_washing_blocked():
    """Cookstove with co_benefits=95 but weak integrity. Under safeguards-gate
    (co_benefits weight=0), narrative should NOT inflate the grade."""
    scores = {
        "removal_type": 35, "additionality": 30, "permanence": 5,
        "mrv_grade": 35, "vintage_year": 100, "co_benefits": 95,
        "registry_methodology": 75,
    }
    comp, grade = _score_and_grade(scores)
    assert grade in ("BB", "B"), f"narrative washing should land BB/B, got {grade} ({comp:.1f})"


def test_double_counting_caps_perfect_credit():
    """Perfect technical scores but double-counted → must cap at B."""
    scores = {
        "removal_type": 98, "additionality": 95, "permanence": 98,
        "mrv_grade": 95, "vintage_year": 100, "co_benefits": 90,
        "registry_methodology": 80,
    }
    comp, grade = _score_and_grade(scores, disqualifiers=["double_counting"])
    assert grade == "B", f"double counting should cap at B, got {grade}"
    assert comp > 90, f"composite should still be AAA-level ({comp:.1f})"


def test_registry_shopping_blocked():
    """Weak project (grid solar) can't inflate via Verra prestige because
    ACM0002 is ICVCM-rejected → registry score 25, not 80."""
    scores = {
        "removal_type": 30, "additionality": 20, "permanence": 5,
        "mrv_grade": 55, "vintage_year": 100, "co_benefits": 35,
        "registry_methodology": 25,  # ICVCM-rejected, even though on Verra
    }
    comp, grade = _score_and_grade(scores)
    assert grade in ("BB", "B"), f"registry shopping should fail, got {grade} ({comp:.1f})"


def test_vintage_arbitrage_blocked():
    """2012 credit re-tokenized in 2024 — vintage formula uses 2012, not 2024."""
    scores = {
        "removal_type": 22, "additionality": 18, "permanence": 5,
        "mrv_grade": 40, "vintage_year": 0,  # 2012 vintage = score 0 in 2026
        "co_benefits": 10, "registry_methodology": 25,
    }
    comp, grade = _score_and_grade(scores)
    assert grade == "B", f"vintage arbitrage should land B, got {grade} ({comp:.1f})"


def test_biodiversity_destroyer_capped():
    """High-carbon monoculture plantation — biodiversityHarm + commercial_plantation_arr
    should prevent it from reaching A."""
    scores = {
        "removal_type": 65, "additionality": 45, "permanence": 45,
        "mrv_grade": 60, "vintage_year": 100, "co_benefits": 8,
        "registry_methodology": 45,
    }
    comp, grade = _score_and_grade(
        scores,
        disqualifiers=["biodiversity_harm"],
        adjustments=["commercial_plantation_arr"],
    )
    assert grade == "BBB", f"biodiversity destroyer should cap at BBB, got {grade} ({comp:.1f})"


def test_co_benefits_truly_zero_weight():
    """Verify co_benefits=0 vs co_benefits=100 produces identical composite."""
    base = {d: 50 for d in WEIGHTS}
    base["co_benefits"] = 0
    comp0 = composite(base, WEIGHTS)
    base["co_benefits"] = 100
    comp100 = composite(base, WEIGHTS)
    assert comp0 == comp100, f"co_benefits must have zero effect: {comp0} vs {comp100}"


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
            print(f"  PASS {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"  FAIL {t.__name__}: {e}")
            traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed out of {passed + failed}")
    sys.exit(1 if failed else 0)
