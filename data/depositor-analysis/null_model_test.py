#!/usr/bin/env python3
"""
Null Model Permutation Test for Adverse Selection in Toucan BCT Pool
====================================================================

Tests whether BCT's observed volume-weighted mean quality (31.71) is
significantly worse than what random sampling would produce.

Two null models:
  1. BCT-eligible universe: randomly reassign quality scores among the 161
     scored TCO2s while preserving deposit tonnage structure
  2. Broader VCM universe: bootstrap from the full 318-credit VCM atlas
     (reconstructed from segment-level data in systematic_scan_results.json)
"""

import json
import os
import numpy as np
from collections import Counter

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
N_ITERATIONS = 100_000
SEED = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
with open(os.path.join(BASE_DIR, "bct_deposits_enriched.json")) as f:
    deposits = json.load(f)

with open(os.path.join(BASE_DIR, "tco2_scores_final.json")) as f:
    tco2_scores = json.load(f)

with open(os.path.join(BASE_DIR, "..", "lemons-index", "systematic_scan_results.json")) as f:
    scan_results = json.load(f)

print(f"Loaded {len(deposits)} deposits, {len(tco2_scores)} scored TCO2s")
print(f"Loaded {len(scan_results['pools'])} pool segments from VCM atlas")

# ---------------------------------------------------------------------------
# Compute observed BCT volume-weighted mean quality
# ---------------------------------------------------------------------------
# Build deposit-level arrays
deposit_tonnes = []
deposit_scores = []
unmatched = 0

for dep in deposits:
    addr = dep["tco2_address"]
    tonnes = dep["amount_tonnes"]
    if addr in tco2_scores:
        deposit_tonnes.append(tonnes)
        deposit_scores.append(tco2_scores[addr]["composite"])
    else:
        unmatched += 1

deposit_tonnes = np.array(deposit_tonnes)
deposit_scores = np.array(deposit_scores)
n_deposits = len(deposit_tonnes)

observed_vwm = np.average(deposit_scores, weights=deposit_tonnes)
total_tonnes = deposit_tonnes.sum()

print(f"\n--- Observed BCT Pool ---")
print(f"Matched deposits: {n_deposits} (unmatched: {unmatched})")
print(f"Total tonnes: {total_tonnes:,.0f}")
print(f"Volume-weighted mean quality: {observed_vwm:.2f}")
print(f"Equal-weighted mean quality: {deposit_scores.mean():.2f}")

# ---------------------------------------------------------------------------
# Unique TCO2 universe stats
# ---------------------------------------------------------------------------
unique_scores = np.array([v["composite"] for v in tco2_scores.values()])
print(f"\nBCT-eligible universe: {len(unique_scores)} unique TCO2s")
print(f"  Mean composite: {unique_scores.mean():.2f}")
print(f"  Median composite: {np.median(unique_scores):.2f}")
print(f"  Std: {unique_scores.std():.2f}")
print(f"  Min: {unique_scores.min():.2f}, Max: {unique_scores.max():.2f}")

# ---------------------------------------------------------------------------
# NULL MODEL 1: BCT-eligible universe permutation
# ---------------------------------------------------------------------------
# Strategy: For each iteration, randomly shuffle the mapping of quality scores
# to TCO2 addresses. This preserves the deposit tonnage structure AND the set
# of available scores, but breaks any correlation between quality and deposit
# size / frequency.
#
# Implementation: We have n_deposits deposits each pointing at a TCO2. We
# shuffle which score each deposit gets, drawing from the 161 unique scores
# with replacement proportional to how often each TCO2 appears in deposits
# (but reassigned randomly).
#
# More precisely: create an array of scores aligned to deposits. In each
# iteration, permute the score-to-TCO2 mapping, then recompute VWM.

print(f"\n{'='*60}")
print(f"NULL MODEL 1: BCT-eligible universe (permutation)")
print(f"{'='*60}")
print(f"H0: Quality scores are randomly assigned to TCO2 addresses")
print(f"    (deposit sizes preserved, score-to-address mapping shuffled)")
print(f"Iterations: {N_ITERATIONS:,}")

# Build TCO2 -> total tonnes mapping
tco2_tonnes = Counter()
tco2_list = []
for dep in deposits:
    addr = dep["tco2_address"]
    if addr in tco2_scores:
        tco2_tonnes[addr] += dep["amount_tonnes"]

# Arrays aligned by unique TCO2 address
tco2_addrs = list(tco2_tonnes.keys())
tco2_total_tonnes = np.array([tco2_tonnes[a] for a in tco2_addrs])
tco2_score_arr = np.array([tco2_scores[a]["composite"] for a in tco2_addrs])

n_unique_deposited = len(tco2_addrs)
print(f"Unique TCO2s actually deposited (with scores): {n_unique_deposited}")

# The observed VWM can also be computed from aggregated TCO2-level data
observed_vwm_check = np.average(tco2_score_arr, weights=tco2_total_tonnes)
print(f"Observed VWM (TCO2-level check): {observed_vwm_check:.4f}")

rng = np.random.default_rng(SEED)

# Permutation test: shuffle scores across TCO2 addresses, keeping tonnage fixed
null1_vwm = np.empty(N_ITERATIONS)
for i in range(N_ITERATIONS):
    shuffled_scores = rng.permutation(tco2_score_arr)
    null1_vwm[i] = np.average(shuffled_scores, weights=tco2_total_tonnes)

null1_mean = null1_vwm.mean()
null1_std = null1_vwm.std()
null1_z = (observed_vwm - null1_mean) / null1_std
null1_p_lower = np.mean(null1_vwm <= observed_vwm)  # fraction as bad or worse
null1_percentile = np.mean(null1_vwm <= observed_vwm) * 100

print(f"\nNull distribution: mean = {null1_mean:.2f}, std = {null1_std:.2f}")
print(f"Null 5th percentile: {np.percentile(null1_vwm, 5):.2f}")
print(f"Null 95th percentile: {np.percentile(null1_vwm, 95):.2f}")
print(f"Null min: {null1_vwm.min():.2f}, max: {null1_vwm.max():.2f}")
print(f"\nObserved VWM: {observed_vwm:.2f}")
print(f"z-score: {null1_z:.3f}")
print(f"Empirical p-value (one-sided, lower): {null1_p_lower:.6f}")
print(f"Percentile of observed in null: {null1_percentile:.2f}%")

if null1_p_lower == 0:
    print(f"  -> p < {1/N_ITERATIONS:.1e} (observed below all {N_ITERATIONS:,} null draws)")
elif null1_p_lower < 0.001:
    print(f"  -> Highly significant (p < 0.001)")
elif null1_p_lower < 0.05:
    print(f"  -> Significant (p < 0.05)")
else:
    print(f"  -> Not significant at 0.05 level")

# ---------------------------------------------------------------------------
# NULL MODEL 2: Broader VCM universe bootstrap
# ---------------------------------------------------------------------------
# Reconstruct individual credit scores from the segment-level data in
# systematic_scan_results.json. We use the "Full 318-credit market" pool
# which has the complete grade distribution.

print(f"\n{'='*60}")
print(f"NULL MODEL 2: Broader VCM universe (bootstrap)")
print(f"{'='*60}")

# Get the full market pool
full_market = None
for pool in scan_results["pools"]:
    if pool["name"] == "Full 318-credit market":
        full_market = pool
        break

print(f"Full VCM market: n={full_market['n']}, mean={full_market['mean_composite']}, "
      f"std={full_market['std_composite']}")

# Reconstruct individual scores from all methodology-based pools (non-overlapping)
# Use the primary methodology pools which partition the market
primary_pools = [
    "REDD+ pool",          # 59
    "Cookstove pool",      # 36
    "Biochar pool",        # 20
    "DACCS pool",          # 14
    "Renewable energy pool",  # 40
    "Industrial avoidance pool (N2O/CH4/ODS/LFG)",  # 44
    "Nature-based removal pool (ARR/IFM)",  # 57
    "Enhanced weathering pool",  # 12
    "Bio-oil geological pool",  # 8
    "Rice methane pool",   # 12
    "Sustainable agriculture pool",  # 16
]

# For each pool, synthesize individual scores using mean and std (normal approx)
# constrained to [min, max] range
vcm_scores = []
for pool in scan_results["pools"]:
    if pool["name"] in primary_pools:
        n = pool["n"]
        mu = pool["mean_composite"]
        sigma = pool["std_composite"]
        lo = pool["min_composite"]
        hi = pool["max_composite"]

        # Generate representative scores: use linspace within the pool's range
        # weighted by approximate normal distribution
        if sigma > 0 and n > 1:
            # Generate n evenly-spaced quantiles
            quantiles = np.linspace(0.5/n, 1 - 0.5/n, n)
            from scipy.stats import norm
            raw = norm.ppf(quantiles, loc=mu, scale=sigma)
            # Clip to observed range
            raw = np.clip(raw, lo, hi)
            vcm_scores.extend(raw.tolist())
        else:
            vcm_scores.extend([mu] * n)

vcm_scores = np.array(vcm_scores)
print(f"Reconstructed VCM universe: {len(vcm_scores)} credits")
print(f"  Mean: {vcm_scores.mean():.2f}, Std: {vcm_scores.std():.2f}")
print(f"  Min: {vcm_scores.min():.2f}, Max: {vcm_scores.max():.2f}")

total_primary = sum(p["n"] for p in scan_results["pools"] if p["name"] in primary_pools)
print(f"  (Sum of primary pool sizes: {total_primary})")

# Strategy: For each iteration, draw n_unique_deposited scores (with replacement)
# from the VCM universe, assign them to the existing tonnage structure
# (keeping tonnage weights fixed), compute VWM.
print(f"\nH0: BCT depositors randomly sample {n_unique_deposited} TCO2s from the")
print(f"    broader {len(vcm_scores)}-credit VCM universe")
print(f"Iterations: {N_ITERATIONS:,}")

null2_vwm = np.empty(N_ITERATIONS)
for i in range(N_ITERATIONS):
    sampled = rng.choice(vcm_scores, size=n_unique_deposited, replace=True)
    null2_vwm[i] = np.average(sampled, weights=tco2_total_tonnes)

null2_mean = null2_vwm.mean()
null2_std = null2_vwm.std()
null2_z = (observed_vwm - null2_mean) / null2_std
null2_p_lower = np.mean(null2_vwm <= observed_vwm)
null2_percentile = null2_p_lower * 100

print(f"\nNull distribution: mean = {null2_mean:.2f}, std = {null2_std:.2f}")
print(f"Null 5th percentile: {np.percentile(null2_vwm, 5):.2f}")
print(f"Null 95th percentile: {np.percentile(null2_vwm, 95):.2f}")
print(f"Null min: {null2_vwm.min():.2f}, max: {null2_vwm.max():.2f}")
print(f"\nObserved VWM: {observed_vwm:.2f}")
print(f"z-score: {null2_z:.3f}")
print(f"Empirical p-value (one-sided, lower): {null2_p_lower:.6f}")
print(f"Percentile of observed in null: {null2_percentile:.2f}%")

if null2_p_lower == 0:
    print(f"  -> p < {1/N_ITERATIONS:.1e} (observed below all {N_ITERATIONS:,} null draws)")
elif null2_p_lower < 0.001:
    print(f"  -> Highly significant (p < 0.001)")
elif null2_p_lower < 0.05:
    print(f"  -> Significant (p < 0.05)")
else:
    print(f"  -> Not significant at 0.05 level")

# ---------------------------------------------------------------------------
# NULL MODEL 3 (bonus): Pure tonnage-weighted bootstrap within BCT universe
# ---------------------------------------------------------------------------
# For each iteration, resample 877 deposits (with replacement) from the
# actual deposit pool, computing VWM each time. This tests how concentrated
# the tonnage is on low-quality tokens.

print(f"\n{'='*60}")
print(f"NULL MODEL 3: Deposit-level bootstrap (BCT internal)")
print(f"{'='*60}")
print(f"H0: Each deposit is an iid draw from the empirical BCT deposit distribution")
print(f"Iterations: {N_ITERATIONS:,}")

null3_vwm = np.empty(N_ITERATIONS)
for i in range(N_ITERATIONS):
    idx = rng.integers(0, n_deposits, size=n_deposits)
    boot_tonnes = deposit_tonnes[idx]
    boot_scores = deposit_scores[idx]
    null3_vwm[i] = np.average(boot_scores, weights=boot_tonnes)

null3_mean = null3_vwm.mean()
null3_std = null3_vwm.std()
null3_ci_lower = np.percentile(null3_vwm, 2.5)
null3_ci_upper = np.percentile(null3_vwm, 97.5)

print(f"\nBootstrap distribution: mean = {null3_mean:.2f}, std = {null3_std:.2f}")
print(f"95% CI: [{null3_ci_lower:.2f}, {null3_ci_upper:.2f}]")
print(f"Observed VWM: {observed_vwm:.2f}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print(f"\n{'='*60}")
print(f"SUMMARY: Adverse Selection Test Results")
print(f"{'='*60}")
print(f"")
print(f"BCT observed vol-wtd mean quality:  {observed_vwm:.2f} / 100")
print(f"BCT Pool Quality Deficit (PQD):     {1 - observed_vwm/100:.3f}")
print(f"")
print(f"Null Model 1 (within BCT-eligible universe):")
print(f"  Null mean: {null1_mean:.2f}  |  z = {null1_z:.2f}  |  p = {null1_p_lower:.6f}")
print(f"  Interpretation: BCT is at the {null1_percentile:.1f}th percentile of random")
print(f"  score-to-address assignment within its own eligible token set.")
if null1_p_lower < 0.05:
    print(f"  --> REJECT H0: Tonnage is disproportionately concentrated on low-quality tokens")
else:
    print(f"  --> FAIL TO REJECT H0 at alpha=0.05")
print(f"")
print(f"Null Model 2 (broader VCM universe, {len(vcm_scores)} credits):")
print(f"  Null mean: {null2_mean:.2f}  |  z = {null2_z:.2f}  |  p = {null2_p_lower:.6f}")
print(f"  Interpretation: BCT is at the {null2_percentile:.1f}th percentile of random")
print(f"  sampling from the broader VCM market.")
if null2_p_lower < 0.05:
    print(f"  --> REJECT H0: BCT pool is significantly worse than random VCM sampling")
else:
    print(f"  --> FAIL TO REJECT H0 at alpha=0.05")
print(f"")
print(f"Null Model 3 (bootstrap 95% CI for BCT VWM):")
print(f"  95% CI: [{null3_ci_lower:.2f}, {null3_ci_upper:.2f}]")
print(f"  The true BCT VWM is tightly estimated around {observed_vwm:.2f}")

# ---------------------------------------------------------------------------
# Save results
# ---------------------------------------------------------------------------
results = {
    "description": "Null model permutation test for adverse selection in BCT pool",
    "observed": {
        "volume_weighted_mean": round(observed_vwm, 4),
        "equal_weighted_mean": round(float(deposit_scores.mean()), 4),
        "total_tonnes": round(float(total_tonnes), 0),
        "n_deposits": n_deposits,
        "n_unique_tco2": n_unique_deposited,
        "pqd": round(1 - observed_vwm / 100, 4),
    },
    "null_model_1_bct_eligible": {
        "description": "Permutation test: shuffle scores across TCO2 addresses within BCT-eligible universe",
        "universe_size": len(unique_scores),
        "universe_mean": round(float(unique_scores.mean()), 4),
        "n_iterations": N_ITERATIONS,
        "null_mean": round(float(null1_mean), 4),
        "null_std": round(float(null1_std), 4),
        "null_p5": round(float(np.percentile(null1_vwm, 5)), 4),
        "null_p95": round(float(np.percentile(null1_vwm, 95)), 4),
        "z_score": round(float(null1_z), 4),
        "p_value_lower": round(float(null1_p_lower), 6),
        "percentile": round(float(null1_percentile), 2),
        "significant_at_005": bool(null1_p_lower < 0.05),
    },
    "null_model_2_vcm_universe": {
        "description": "Bootstrap from broader VCM universe (318 credits reconstructed from segment data)",
        "universe_size": len(vcm_scores),
        "universe_mean": round(float(vcm_scores.mean()), 4),
        "n_iterations": N_ITERATIONS,
        "null_mean": round(float(null2_mean), 4),
        "null_std": round(float(null2_std), 4),
        "null_p5": round(float(np.percentile(null2_vwm, 5)), 4),
        "null_p95": round(float(np.percentile(null2_vwm, 95)), 4),
        "z_score": round(float(null2_z), 4),
        "p_value_lower": round(float(null2_p_lower), 6),
        "percentile": round(float(null2_percentile), 2),
        "significant_at_005": bool(null2_p_lower < 0.05),
    },
    "null_model_3_bootstrap_ci": {
        "description": "Deposit-level bootstrap for 95% CI of BCT VWM",
        "n_iterations": N_ITERATIONS,
        "bootstrap_mean": round(float(null3_mean), 4),
        "bootstrap_std": round(float(null3_std), 4),
        "ci_95_lower": round(float(null3_ci_lower), 4),
        "ci_95_upper": round(float(null3_ci_upper), 4),
    },
}

output_path = os.path.join(BASE_DIR, "null_model_results.json")
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
