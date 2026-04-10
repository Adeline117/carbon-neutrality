#!/usr/bin/env python3
"""Unit tests for the batch methodology-level scorer."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "data" / "methodology-ratings"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "data" / "pilot-scoring"))

from batch_scorer import load_archetypes, score_project, vintage_score
from score import load_rubric_index, load_default_stds


RUBRICS = load_rubric_index()
WEIGHTS = {d["id"]: d["weight"] for d in RUBRICS["dimensions"]}
BANDS = RUBRICS["grades"]
DEFAULT_STDS = load_default_stds(RUBRICS)
ARCHETYPES = load_archetypes()


def test_vintage_current_year():
    assert vintage_score(2026, 2026) == 100

def test_vintage_decay():
    assert vintage_score(2024, 2026) == 76
    assert vintage_score(2020, 2026) == 28

def test_vintage_floor():
    assert vintage_score(2010, 2026) == 0
    assert vintage_score(2000, 2026) == 0

def test_daccs_archetype_reaches_aaa():
    project = {"methodology_category": "daccs_geological", "vintage_year": 2025}
    result = score_project(project, ARCHETYPES, WEIGHTS, DEFAULT_STDS, BANDS)
    assert result["grade"] == "AAA", f"DACCS 2025 should be AAA, got {result['grade']}"

def test_redd_project_is_low():
    project = {"methodology_category": "redd_project", "vintage_year": 2020}
    result = score_project(project, ARCHETYPES, WEIGHTS, DEFAULT_STDS, BANDS)
    assert result["grade"] in ("B", "BB"), f"REDD+ 2020 should be B/BB, got {result['grade']}"

def test_per_archetype_std_varies():
    daccs = {"methodology_category": "daccs_geological", "vintage_year": 2025}
    redd = {"methodology_category": "redd_project", "vintage_year": 2025}
    r1 = score_project(daccs, ARCHETYPES, WEIGHTS, DEFAULT_STDS, BANDS)
    r2 = score_project(redd, ARCHETYPES, WEIGHTS, DEFAULT_STDS, BANDS)
    assert r1["composite_std"] < r2["composite_std"], \
        f"DACCS σ={r1['composite_std']} should be < REDD+ σ={r2['composite_std']}"

def test_hfc23_is_B():
    project = {"methodology_category": "hfc23_destruction", "vintage_year": 2015}
    result = score_project(project, ARCHETYPES, WEIGHTS, DEFAULT_STDS, BANDS)
    assert result["grade"] == "B", f"HFC-23 2015 should be B, got {result['grade']}"

def test_unknown_category_fallback():
    project = {"methodology_category": "nonexistent_xyz", "vintage_year": 2024}
    result = score_project(project, ARCHETYPES, WEIGHTS, DEFAULT_STDS, BANDS)
    assert result["archetype_id"] == "redd_project", "unknown should fall back to redd_project"


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
