#!/usr/bin/env python3
"""Unit tests for the statistical functions used in rank correlation (compute.py)
and inter-rater reliability (irr.py). These functions produce the headline
numbers cited in the paper — Spearman rho, Kendall tau, Fleiss' kappa, ICC,
Cohen's kappa. A bug in any of them invalidates the paper's claims.

Run with: python3 tests/test_statistics.py
"""

import math
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "data" / "rank-correlation"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "data" / "llm-panel-irr"))

from compute import spearman_rank_correlation, kendall_tau
from irr import fleiss_kappa, cohens_kappa, icc_2k, pearson


# --- Spearman rank correlation ---

def test_spearman_perfect_positive():
    assert abs(spearman_rank_correlation([1, 2, 3, 4], [1, 2, 3, 4]) - 1.0) < 0.001

def test_spearman_perfect_negative():
    assert abs(spearman_rank_correlation([1, 2, 3, 4], [4, 3, 2, 1]) - (-1.0)) < 0.001

def test_spearman_uncorrelated():
    # [1,2,3,4] vs [2,4,1,3] — rho should be 0
    rho = spearman_rank_correlation([1, 2, 3, 4], [2, 4, 1, 3])
    assert abs(rho) < 0.5, f"expected near-zero, got {rho}"

def test_spearman_with_ties():
    rho = spearman_rank_correlation([1, 1, 2, 3], [1, 2, 2, 3])
    assert not math.isnan(rho), "should handle ties without NaN"

def test_spearman_too_short():
    assert math.isnan(spearman_rank_correlation([1], [1]))

def test_spearman_length_mismatch():
    assert math.isnan(spearman_rank_correlation([1, 2], [1]))


# --- Kendall tau ---

def test_kendall_perfect_positive():
    assert abs(kendall_tau([1, 2, 3, 4], [1, 2, 3, 4]) - 1.0) < 0.001

def test_kendall_perfect_negative():
    assert abs(kendall_tau([1, 2, 3, 4], [4, 3, 2, 1]) - (-1.0)) < 0.001

def test_kendall_known_value():
    # [1,2,3] vs [1,3,2]: one discordant pair out of 3 → tau = (2-1)/3 = 0.333
    tau = kendall_tau([1, 2, 3], [1, 3, 2])
    assert abs(tau - 0.333) < 0.05, f"expected ~0.333, got {tau}"


# --- Fleiss' kappa ---

def test_fleiss_perfect_agreement():
    # 3 raters, 4 items, 2 categories — all agree
    matrix = [[3, 0], [0, 3], [3, 0], [0, 3]]
    k = fleiss_kappa(matrix, 2)
    assert abs(k - 1.0) < 0.001, f"perfect agreement should be 1.0, got {k}"

def test_fleiss_maximum_disagreement():
    # 2 raters, 4 items, 2 categories — each item has 1 vote per category
    # This is MAXIMUM disagreement (kappa = -1.0), not chance
    matrix = [[1, 1], [1, 1], [1, 1], [1, 1]]
    k = fleiss_kappa(matrix, 2)
    assert abs(k - (-1.0)) < 0.001, f"max disagreement should be -1.0, got {k}"

def test_fleiss_known_example():
    # Fleiss 1971 Table 2 example (simplified)
    # 10 items, 6 raters, 5 categories
    matrix = [
        [0, 0, 0, 0, 6],
        [0, 3, 3, 0, 0],
        [0, 0, 4, 0, 2],
        [0, 3, 0, 3, 0],
        [2, 2, 0, 2, 0],
        [1, 0, 0, 5, 0],
        [0, 0, 3, 3, 0],
        [1, 0, 0, 5, 0],
        [0, 2, 2, 2, 0],
        [2, 0, 4, 0, 0],
    ]
    k = fleiss_kappa(matrix, 5)
    # Hand-computed for THIS specific matrix: P_bar=0.487, P_e=0.238, kappa=0.327
    assert abs(k - 0.327) < 0.01, f"expected ~0.327, got {k}"


# --- Cohen's kappa ---

def test_cohens_perfect():
    a = [0, 1, 2, 0, 1, 2]
    b = [0, 1, 2, 0, 1, 2]
    k = cohens_kappa(a, b, 3)
    assert abs(k - 1.0) < 0.001

def test_cohens_chance():
    # Completely random: 50/50 on 2 categories
    a = [0, 1, 0, 1, 0, 1, 0, 1]
    b = [1, 0, 1, 0, 1, 0, 1, 0]
    k = cohens_kappa(a, b, 2)
    assert k < 0.0, f"opposite agreement should be negative, got {k}"


# --- ICC(2,k) ---

def test_icc_perfect():
    # All raters agree perfectly
    ratings = [[10, 10, 10], [20, 20, 20], [30, 30, 30]]
    icc = icc_2k(ratings)
    assert abs(icc - 1.0) < 0.01, f"perfect agreement ICC should be 1.0, got {icc}"

def test_icc_high():
    # Close agreement
    ratings = [[10, 11, 10], [20, 19, 21], [30, 30, 29]]
    icc = icc_2k(ratings)
    assert icc > 0.95, f"high agreement ICC should be >0.95, got {icc}"


# --- Pearson ---

def test_pearson_perfect():
    r = pearson([1, 2, 3, 4], [2, 4, 6, 8])
    assert abs(r - 1.0) < 0.001

def test_pearson_negative():
    r = pearson([1, 2, 3, 4], [8, 6, 4, 2])
    assert abs(r - (-1.0)) < 0.001

def test_pearson_zero():
    r = pearson([1, 2, 3, 4], [1, -1, 1, -1])
    assert abs(r) < 0.5, f"expected near-zero, got {r}"


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
