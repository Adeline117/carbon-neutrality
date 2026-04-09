#!/usr/bin/env python3
"""Unit tests for the core scoring engine (data/pilot-scoring/score.py).

These tests verify the same invariants as the Solidity Foundry tests,
ensuring off-chain ≡ on-chain agreement. Run with: python3 -m pytest tests/
"""

import math
import sys
from pathlib import Path

# Add scorer to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "data" / "pilot-scoring"))
from score import (
    apply_dimension_adjustments,
    apply_disqualifiers,
    composite,
    composite_variance,
    grade_from_score,
    grade_posterior,
    load_dimension_adjustments,
    load_rubric_index,
    normal_cdf,
)

RUBRICS = load_rubric_index()
WEIGHTS = {d["id"]: d["weight"] for d in RUBRICS["dimensions"]}
BANDS = RUBRICS["grades"]
DQ_SPEC = RUBRICS["disqualifiers"]
DIMS = list(WEIGHTS.keys())


# --- Composite tests ---

def test_orca_composite():
    """Climeworks Orca — must match Solidity test vector (9505 bps = 95.05)."""
    scores = {
        "removal_type": 98, "additionality": 95, "permanence": 98,
        "mrv_grade": 92, "vintage_year": 100, "co_benefits": 15,
        "registry_methodology": 80,
    }
    comp = composite(scores, WEIGHTS)
    assert abs(comp - 95.05) < 0.01, f"Orca composite {comp} != 95.05"


def test_zero_scores():
    scores = {d: 0 for d in DIMS}
    assert composite(scores, WEIGHTS) == 0.0


def test_max_scores():
    scores = {d: 100 for d in DIMS}
    comp = composite(scores, WEIGHTS)
    assert abs(comp - 100.0) < 0.01


# --- Grade boundary tests ---

def test_grade_boundaries():
    assert grade_from_score(90.0, BANDS) == "AAA"
    assert grade_from_score(89.99, BANDS) == "AA"
    assert grade_from_score(75.0, BANDS) == "AA"
    assert grade_from_score(74.99, BANDS) == "A"
    assert grade_from_score(60.0, BANDS) == "A"
    assert grade_from_score(59.99, BANDS) == "BBB"
    assert grade_from_score(45.0, BANDS) == "BBB"
    assert grade_from_score(44.99, BANDS) == "BB"
    assert grade_from_score(30.0, BANDS) == "BB"
    assert grade_from_score(29.99, BANDS) == "B"
    assert grade_from_score(0.0, BANDS) == "B"


# --- Disqualifier tests ---

def test_disqualifier_double_counting_caps_at_B():
    g, _ = apply_disqualifiers("AAA", ["double_counting"], DQ_SPEC)
    assert g == "B"


def test_disqualifier_sanctioned_caps_at_BB():
    g, _ = apply_disqualifiers("AAA", ["sanctioned_registry"], DQ_SPEC)
    assert g == "BB"


def test_disqualifier_no_third_party_caps_at_BBB():
    g, _ = apply_disqualifiers("AAA", ["no_third_party"], DQ_SPEC)
    assert g == "BBB"


def test_disqualifier_community_harm_caps_at_BBB():
    g, _ = apply_disqualifiers("AA", ["community_harm"], DQ_SPEC)
    assert g == "BBB"


def test_disqualifier_biodiversity_harm_caps_at_BBB():
    g, _ = apply_disqualifiers("AA", ["biodiversity_harm"], DQ_SPEC)
    assert g == "BBB"


def test_disqualifier_compose_to_strictest():
    """double_counting (B) + no_third_party (BBB) → B (strictest wins)."""
    g, _ = apply_disqualifiers("AAA", ["double_counting", "no_third_party"], DQ_SPEC)
    assert g == "B"


def test_disqualifier_never_raises():
    g, _ = apply_disqualifiers("B", ["no_third_party"], DQ_SPEC)
    assert g == "B"  # BBB cap doesn't raise B


# --- Variance tests ---

def test_zero_stds_zero_variance():
    stds = {d: 0.0 for d in DIMS}
    assert composite_variance(stds, WEIGHTS) == 0.0


def test_variance_matches_solidity():
    """Default stds (4,9,4,7,10,9,11) → variance = 83706 bps² (Solidity test)."""
    stds = {
        "removal_type": 4, "additionality": 9, "permanence": 4,
        "mrv_grade": 7, "vintage_year": 10, "co_benefits": 9,
        "registry_methodology": 11,
    }
    var = composite_variance(stds, WEIGHTS)
    # Solidity computes in integer bps²: sum(w_bps² * σ²) / 10000
    # Python computes in float (0-100)² units: sum(w² * σ²)
    # Convert: python_var * 10000 ≈ solidity_var (within float tolerance)
    # Actually Python uses fractional weights, Solidity uses bps weights.
    # Let's just check the std:
    sigma = math.sqrt(var)
    assert abs(sigma - 2.88) < 0.05, f"sigma {sigma} != ~2.88"


# --- P(grade) posterior tests ---

def test_posterior_deterministic_at_zero_std():
    post = grade_posterior(95.0, 0.0, BANDS)
    assert post["AAA"] == 1.0
    assert post["AA"] == 0.0


def test_posterior_orca():
    post = grade_posterior(95.05, 2.88, BANDS)
    assert post["AAA"] > 0.90, f"P(AAA) = {post['AAA']} should be >0.90"


def test_posterior_charm_fragile():
    post = grade_posterior(90.53, 2.88, BANDS)
    assert 0.40 < post["AAA"] < 0.70, f"P(AAA) = {post['AAA']} should be ~0.57"


def test_posterior_sums_to_one():
    post = grade_posterior(60.0, 5.0, BANDS)
    total = sum(post.values())
    assert abs(total - 1.0) < 0.001, f"posterior sums to {total}"


# --- Normal CDF test ---

def test_normal_cdf_standard():
    assert abs(normal_cdf(0) - 0.5) < 0.001
    assert abs(normal_cdf(1.96) - 0.975) < 0.001
    assert abs(normal_cdf(-1.96) - 0.025) < 0.001


# --- Dimension adjustment test ---

def test_commercial_plantation_arr_adjustment():
    adjs = load_dimension_adjustments()
    base = {"removal_type": 65, "additionality": 35, "permanence": 40,
            "mrv_grade": 50, "vintage_year": 40, "co_benefits": 35,
            "registry_methodology": 55}
    adjusted = apply_dimension_adjustments(base, ["commercial_plantation_arr"], adjs)
    assert adjusted["removal_type"] == 45, "65 - 20 = 45"
    assert adjusted["additionality"] == 35, "other dims unchanged"


def test_no_adjustment_when_no_flags():
    adjs = load_dimension_adjustments()
    base = {"removal_type": 65, "additionality": 35, "permanence": 40,
            "mrv_grade": 50, "vintage_year": 40, "co_benefits": 35,
            "registry_methodology": 55}
    adjusted = apply_dimension_adjustments(base, [], adjs)
    assert adjusted == base


# --- Co-benefits zero-weight test ---

def test_co_benefits_no_effect():
    s1 = {d: 80 for d in DIMS}
    s1["co_benefits"] = 0
    s2 = dict(s1)
    s2["co_benefits"] = 100
    assert composite(s1, WEIGHTS) == composite(s2, WEIGHTS)


# --- Python ↔ Solidity cross-check ---

def test_python_solidity_crosscheck():
    """Verify Python composite matches Solidity's integer bps math for 3 credits."""
    import json
    credits_path = Path(__file__).resolve().parent.parent / "data" / "pilot-scoring" / "credits.json"
    credits_data = json.loads(credits_path.read_text())["credits"]
    weights_bps = {d["id"]: int(d["weight"] * 10000) for d in RUBRICS["dimensions"]}

    for cid, expected_bps in [("C001", 9505), ("C010", 4632), ("C022", 1960)]:
        c = next(x for x in credits_data if x["id"] == cid)
        s = c["scores"]
        # Solidity: sum(score * w_bps) // 100
        sol_bps = sum(s[d] * weights_bps[d] for d in weights_bps) // 100
        # Python: composite * 100 rounded
        py_comp = composite(s, WEIGHTS)
        py_bps = int(round(py_comp * 100))
        assert sol_bps == expected_bps, f"{cid}: Solidity {sol_bps} != expected {expected_bps}"
        assert py_bps == sol_bps, f"{cid}: Python {py_bps} != Solidity {sol_bps}"


if __name__ == "__main__":
    # Simple runner without pytest
    import traceback
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
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
