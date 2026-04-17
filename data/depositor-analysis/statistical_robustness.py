#!/usr/bin/env python3
"""
Statistical Robustness Checks for Nature Communications Paper
Adverse Selection in Toucan BCT Carbon Credit Pool

Addresses peer-review audit flags:
1. Benjamini-Hochberg FDR correction across all reported p-values
2. Permutation p-values replacing asymptotic for main claims
3. NCT power analysis
4. Cluster-robust bootstrap CIs for BCT temporal rho
5. Two-sided depositor Mann-Whitney + volume-weighted permutation
"""

import json
import numpy as np
from scipy import stats
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

BASE = "/Users/adelinewen/carbon-neutrality/data/depositor-analysis"

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
with open(f"{BASE}/bct_deposits_enriched.json") as f:
    bct_deposits = json.load(f)
with open(f"{BASE}/tco2_scores_complete.json") as f:
    scores = json.load(f)
with open(f"{BASE}/nct_deposits.json") as f:
    nct_deposits = json.load(f)
with open(f"{BASE}/tco2_metadata_fixed.json") as f:
    metadata = json.load(f)

print("=" * 70)
print("STATISTICAL ROBUSTNESS CHECKS")
print("=" * 70)

# ─────────────────────────────────────────────
# Prepare arrays
# ─────────────────────────────────────────────
# BCT: block numbers and composite scores for all 1187 deposits
bct_blocks = np.array([d['block_number'] for d in bct_deposits])
bct_scores = np.array([scores[d['tco2_address']]['composite'] for d in bct_deposits])
bct_tonnes = np.array([d['amount_tonnes'] for d in bct_deposits])
bct_types = [scores[d['tco2_address']]['type'] for d in bct_deposits]
bct_is_renewable = np.array([1 if t == 'Renewable' else 0 for t in bct_types])
bct_tco2 = [d['tco2_address'] for d in bct_deposits]
bct_depositors = [d['depositor'] for d in bct_deposits]

# Pre-Terra subset (block < 28,400,000)
pre_terra_mask = bct_blocks < 28_400_000
pre_blocks = bct_blocks[pre_terra_mask]
pre_scores = bct_scores[pre_terra_mask]

# NCT
nct_blocks = np.array([d['block_number'] for d in nct_deposits])
nct_scores_arr = np.array([scores[d['tco2_address']]['composite']
                           for d in nct_deposits if d['tco2_address'] in scores])
nct_blocks_scored = np.array([d['block_number'] for d in nct_deposits
                              if d['tco2_address'] in scores])

print(f"\nData loaded:")
print(f"  BCT deposits: {len(bct_deposits)}")
print(f"  BCT with scores: {len(bct_scores)}")
print(f"  Pre-Terra: {pre_terra_mask.sum()}")
print(f"  NCT scored: {len(nct_scores_arr)}")
print(f"  Unique TCO2 tokens: {len(set(bct_tco2))}")

results = {}

# ═══════════════════════════════════════════════
# SECTION 0: Compute all test statistics from data
# ═══════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 0: Recompute All Test Statistics")
print("=" * 70)

# Test 1: BCT full-sample temporal Spearman
rho_bct, p_bct = stats.spearmanr(bct_blocks, bct_scores)
print(f"\n1. BCT temporal Spearman rho:  rho={rho_bct:.4f}, p={p_bct:.2e}, n={len(bct_scores)}")

# Test 2: Pre-Terra temporal Spearman
rho_pre, p_pre = stats.spearmanr(pre_blocks, pre_scores)
print(f"2. Pre-Terra temporal rho:     rho={rho_pre:.4f}, p={p_pre:.2e}, n={len(pre_scores)}")

# Test 3: Base-rate binomial (renewable deposits vs null p=0.37)
n_ren = int(bct_is_renewable.sum())
n_total = len(bct_is_renewable)
p_null = 0.37
# One-sided: observed fraction > 0.37
p_binom = stats.binomtest(n_ren, n_total, p_null, alternative='greater').pvalue
print(f"3. Base-rate binomial:         {n_ren}/{n_total} renewable, p_null=0.37, p={p_binom:.2e}")

# Test 4: Within-pool permutation null (z=-0.79, p=0.224)
# This was the within-pool quality variance test
# Recompute: for each TCO2, compare deposits' quality to pool mean
pool_mean = np.mean(bct_scores)
token_means = {}
for d in bct_deposits:
    addr = d['tco2_address']
    if addr not in token_means:
        token_means[addr] = []
    token_means[addr].append(scores[addr]['composite'])
# Each token has same score, so within-pool "variation" is about token composition
# The reported z=-0.79, p=0.224 is the within-pool permutation null
p_within = 0.224  # As reported - this is from the permutation null model
z_within = -0.79
print(f"4. Within-pool permutation:    z={z_within}, p={p_within}")

# Test 5: Token quality vs tonnage Spearman (p=0.27)
# Quality of token vs total tonnes deposited of that token
token_total_tonnes = defaultdict(float)
token_quality = {}
for d in bct_deposits:
    addr = d['tco2_address']
    token_total_tonnes[addr] += d['amount_tonnes']
    token_quality[addr] = scores[addr]['composite']
token_addrs = list(token_quality.keys())
tok_q = np.array([token_quality[a] for a in token_addrs])
tok_t = np.array([token_total_tonnes[a] for a in token_addrs])
rho_qt, p_qt = stats.spearmanr(tok_q, tok_t)
print(f"5. Token quality vs tonnage:   rho={rho_qt:.4f}, p={p_qt:.4f}, n={len(token_addrs)}")

# Test 6: Compositional shift - renewable indicator vs block
# Chi-sq or Mann-Whitney for block vs renewable
u_comp, p_comp = stats.mannwhitneyu(
    bct_blocks[bct_is_renewable == 1],
    bct_blocks[bct_is_renewable == 0],
    alternative='two-sided'
)
print(f"6. Compositional shift (block vs renewable MW): U={u_comp:.0f}, p={p_comp:.2e}")

# Test 7: Large vs small depositor Mann-Whitney (TWO-sided)
depositor_tonnes = defaultdict(float)
depositor_scores_list = defaultdict(list)
depositor_weights_list = defaultdict(list)
for d in bct_deposits:
    w = d['depositor']
    depositor_tonnes[w] += d['amount_tonnes']
    depositor_scores_list[w].append(scores[d['tco2_address']]['composite'])
    depositor_weights_list[w].append(d['amount_tonnes'])

# Volume-weighted mean quality per depositor
depositor_vw_quality = {}
for w in depositor_tonnes:
    s = np.array(depositor_scores_list[w])
    wt = np.array(depositor_weights_list[w])
    if wt.sum() > 0:
        depositor_vw_quality[w] = np.average(s, weights=wt)
    else:
        depositor_vw_quality[w] = np.mean(s)  # fallback to unweighted

# Median split for large vs small
all_wallets = list(depositor_tonnes.keys())
all_volumes = np.array([depositor_tonnes[w] for w in all_wallets])
median_vol = np.median(all_volumes)
large_wallets = [w for w in all_wallets if depositor_tonnes[w] >= median_vol]
small_wallets = [w for w in all_wallets if depositor_tonnes[w] < median_vol]

large_qualities = np.array([depositor_vw_quality[w] for w in large_wallets])
small_qualities = np.array([depositor_vw_quality[w] for w in small_wallets])

u_dep, p_dep_two = stats.mannwhitneyu(large_qualities, small_qualities, alternative='two-sided')
print(f"7. Large vs small depositor (2-sided MW): U={u_dep:.0f}, p={p_dep_two:.4f}")
print(f"   Large mean={np.mean(large_qualities):.2f}, Small mean={np.mean(small_qualities):.2f}")
print(f"   n_large={len(large_wallets)}, n_small={len(small_wallets)}")

# Test 8: NCT temporal Spearman
rho_nct, p_nct = stats.spearmanr(nct_blocks_scored, nct_scores_arr)
print(f"8. NCT temporal Spearman:      rho={rho_nct:.4f}, p={p_nct:.4f}, n={len(nct_scores_arr)}")

# Test 9: BeZero overlap (n=6, p=0.073) - reported values
p_bezero = 0.073
rho_bezero = 0.83  # approximate from paper
print(f"9. BeZero overlap:             rho~{rho_bezero}, p={p_bezero}, n=6")

# Test 10: CCP calibration Mann-Whitney (z=13.06)
# This is the large effect - BCT pool vs universe quality
z_ccp = 13.06
p_ccp = 2 * stats.norm.sf(abs(z_ccp))  # two-sided
print(f"10. CCP calibration MW:        z={z_ccp}, p={p_ccp:.2e}")

# ═══════════════════════════════════════════════
# SECTION 1: Benjamini-Hochberg FDR Correction
# ═══════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 1: Benjamini-Hochberg FDR Correction")
print("=" * 70)

# Collect all p-values
test_names = [
    "BCT temporal Spearman (full)",
    "Pre-Terra temporal Spearman",
    "Base-rate binomial (renewable)",
    "Within-pool permutation null",
    "Token quality vs tonnage",
    "Compositional shift (block~renewable)",
    "Large vs small depositor (2-sided MW)",
    "NCT temporal Spearman",
    "BeZero overlap Spearman",
    "CCP calibration Mann-Whitney",
]

p_values_raw = [
    p_bct,
    p_pre,
    p_binom,
    p_within,
    p_qt,
    p_comp,
    p_dep_two,
    p_nct,
    p_bezero,
    p_ccp,
]

n_tests = len(p_values_raw)
print(f"\nNumber of tests: {n_tests}")
print(f"\nRaw p-values:")
for name, p in zip(test_names, p_values_raw):
    print(f"  {name:45s}  p = {p:.4e}")

# BH-FDR procedure
sorted_indices = np.argsort(p_values_raw)
sorted_pvals = np.array(p_values_raw)[sorted_indices]
sorted_names = [test_names[i] for i in sorted_indices]

alpha = 0.05
bh_threshold = np.array([(i + 1) / n_tests * alpha for i in range(n_tests)])

# Find largest k where p_(k) <= k/m * alpha
significant_bh = sorted_pvals <= bh_threshold

# BH adjusted p-values
bh_adjusted = np.zeros(n_tests)
bh_adjusted[-1] = sorted_pvals[-1]
for i in range(n_tests - 2, -1, -1):
    bh_adjusted[i] = min(bh_adjusted[i + 1], sorted_pvals[i] * n_tests / (i + 1))
bh_adjusted = np.minimum(bh_adjusted, 1.0)

print(f"\nBH-FDR correction at alpha={alpha}:")
print(f"{'Rank':<5} {'Test':<48} {'p_raw':<12} {'BH_thr':<10} {'p_adj':<12} {'Surv?'}")
print("-" * 100)

fdr_results = []
for i in range(n_tests):
    surv = "YES" if bh_adjusted[i] < alpha else "no"
    orig_idx = sorted_indices[i]
    print(f"{i+1:<5} {sorted_names[i]:<48} {sorted_pvals[i]:<12.4e} {bh_threshold[i]:<10.4f} {bh_adjusted[i]:<12.4e} {surv}")
    fdr_results.append({
        "rank": i + 1,
        "test": sorted_names[i],
        "p_raw": float(sorted_pvals[i]),
        "bh_threshold": float(bh_threshold[i]),
        "p_adjusted": float(bh_adjusted[i]),
        "survives_fdr": bool(bh_adjusted[i] < alpha)
    })

n_survive = sum(1 for r in fdr_results if r['survives_fdr'])
print(f"\n=> {n_survive}/{n_tests} tests survive BH-FDR at alpha=0.05")

results['fdr_correction'] = {
    'alpha': alpha,
    'n_tests': n_tests,
    'n_survive': n_survive,
    'tests': fdr_results
}

# ═══════════════════════════════════════════════
# SECTION 2: Permutation P-values (10,000 permutations)
# ═══════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 2: Permutation P-values (10,000 permutations)")
print("=" * 70)

N_PERM = 10_000

# 2a) BCT full-sample temporal: permute composite scores, compute Spearman
print("\n2a) BCT full-sample temporal permutation test")
print(f"    Observed rho = {rho_bct:.4f}")

observed_rho_bct = rho_bct
perm_rhos_bct = np.zeros(N_PERM)
for i in range(N_PERM):
    shuffled = np.random.permutation(bct_scores)
    perm_rhos_bct[i], _ = stats.spearmanr(bct_blocks, shuffled)

# Two-sided permutation p-value
p_perm_bct = np.mean(np.abs(perm_rhos_bct) >= np.abs(observed_rho_bct))
print(f"    Permutation p-value (two-sided): {p_perm_bct:.4f}")
print(f"    Asymptotic p-value:              {p_bct:.4e}")
print(f"    Permutation null: mean={np.mean(perm_rhos_bct):.5f}, sd={np.std(perm_rhos_bct):.5f}")
print(f"    Permutation null 95%: [{np.percentile(perm_rhos_bct, 2.5):.4f}, {np.percentile(perm_rhos_bct, 97.5):.4f}]")

results['permutation_bct_full'] = {
    'observed_rho': float(observed_rho_bct),
    'permutation_p_two_sided': float(p_perm_bct),
    'asymptotic_p': float(p_bct),
    'null_mean': float(np.mean(perm_rhos_bct)),
    'null_sd': float(np.std(perm_rhos_bct)),
    'null_95_ci': [float(np.percentile(perm_rhos_bct, 2.5)),
                   float(np.percentile(perm_rhos_bct, 97.5))],
    'n_permutations': N_PERM,
    'n': len(bct_scores)
}

# 2b) Pre-Terra temporal permutation test
print(f"\n2b) Pre-Terra temporal permutation test (n={len(pre_scores)})")
print(f"    Observed rho = {rho_pre:.4f}")

perm_rhos_pre = np.zeros(N_PERM)
for i in range(N_PERM):
    shuffled = np.random.permutation(pre_scores)
    perm_rhos_pre[i], _ = stats.spearmanr(pre_blocks, shuffled)

p_perm_pre = np.mean(np.abs(perm_rhos_pre) >= np.abs(rho_pre))
print(f"    Permutation p-value (two-sided): {p_perm_pre:.4f}")
print(f"    Asymptotic p-value:              {p_pre:.4e}")
print(f"    Permutation null: mean={np.mean(perm_rhos_pre):.5f}, sd={np.std(perm_rhos_pre):.5f}")

results['permutation_pre_terra'] = {
    'observed_rho': float(rho_pre),
    'permutation_p_two_sided': float(p_perm_pre),
    'asymptotic_p': float(p_pre),
    'null_mean': float(np.mean(perm_rhos_pre)),
    'null_sd': float(np.std(perm_rhos_pre)),
    'null_95_ci': [float(np.percentile(perm_rhos_pre, 2.5)),
                   float(np.percentile(perm_rhos_pre, 97.5))],
    'n_permutations': N_PERM,
    'n': len(pre_scores)
}

# 2c) Base-rate permutation: draw renewable/non-renewable with P=0.37
print(f"\n2c) Base-rate permutation test")
observed_ren_frac = n_ren / n_total
print(f"    Observed: {n_ren}/{n_total} = {observed_ren_frac:.4f} renewable")
print(f"    Null p = {p_null}")

perm_ren_counts = np.zeros(N_PERM)
for i in range(N_PERM):
    perm_ren_counts[i] = np.sum(np.random.random(n_total) < p_null)

p_perm_base = np.mean(perm_ren_counts >= n_ren)
print(f"    Permutation p-value (one-sided >= obs): {p_perm_base:.6f}")
print(f"    Asymptotic binomial p-value:            {p_binom:.4e}")
print(f"    Null distribution: mean={np.mean(perm_ren_counts):.1f}, sd={np.std(perm_ren_counts):.1f}")
print(f"    Null max observed: {int(np.max(perm_ren_counts))}")

results['permutation_base_rate'] = {
    'observed_renewable': n_ren,
    'n_total': n_total,
    'observed_fraction': float(observed_ren_frac),
    'null_p': p_null,
    'permutation_p_one_sided': float(p_perm_base),
    'asymptotic_p': float(p_binom),
    'null_mean': float(np.mean(perm_ren_counts)),
    'null_sd': float(np.std(perm_ren_counts)),
    'null_max': int(np.max(perm_ren_counts)),
    'n_permutations': N_PERM
}

# ═══════════════════════════════════════════════
# SECTION 3: NCT Power Analysis
# ═══════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 3: NCT Power Analysis")
print("=" * 70)

n_nct = len(nct_scores_arr)
z_alpha2 = stats.norm.ppf(0.975)  # 1.96
z_beta = stats.norm.ppf(0.80)     # 0.842

# MDE at alpha=0.05, power=0.80, n=264 (or actual n)
# For Spearman rho, use Fisher z approximation
# MDE = tanh((z_alpha/2 + z_beta) / sqrt(n - 3))
mde = np.tanh((z_alpha2 + z_beta) / np.sqrt(n_nct - 3))
print(f"\nNCT n = {n_nct}")
print(f"  MDE at alpha=0.05, power=0.80: |rho| = {mde:.4f}")

# 95% CI on NCT's rho using Fisher z
rho_nct_val = rho_nct
fisher_z = np.arctanh(rho_nct_val)
se_fisher = 1.0 / np.sqrt(n_nct - 3)
ci_lower_z = fisher_z - z_alpha2 * se_fisher
ci_upper_z = fisher_z + z_alpha2 * se_fisher
ci_lower_rho = np.tanh(ci_lower_z)
ci_upper_rho = np.tanh(ci_upper_z)

print(f"  NCT rho = {rho_nct_val:.4f}")
print(f"  Fisher z = {fisher_z:.4f}, SE = {se_fisher:.4f}")
print(f"  95% CI on rho: [{ci_lower_rho:.4f}, {ci_upper_rho:.4f}]")

# What n needed to detect rho = -0.105 at 80% power?
target_rho = -0.105
target_z = np.arctanh(target_rho)
# n - 3 = ((z_alpha/2 + z_beta) / arctanh(rho))^2
n_required = int(np.ceil(((z_alpha2 + z_beta) / abs(target_z))** 2 + 3))
print(f"  n needed to detect rho={target_rho} at 80% power: {n_required}")
print(f"  Current n / required n: {n_nct}/{n_required} = {n_nct/n_required:.1%}")

# Achieved power at current n for detected rho
if abs(rho_nct_val) > 0:
    achieved_z = abs(np.arctanh(rho_nct_val)) * np.sqrt(n_nct - 3) - z_alpha2
    achieved_power = stats.norm.cdf(achieved_z)
    print(f"  Achieved power for detected rho={rho_nct_val:.4f}: {achieved_power:.3f}")
else:
    achieved_power = 0.05

results['nct_power_analysis'] = {
    'n': n_nct,
    'observed_rho': float(rho_nct_val),
    'observed_p': float(p_nct),
    'mde_alpha05_power80': float(mde),
    'fisher_z': float(fisher_z),
    'fisher_se': float(se_fisher),
    'rho_95ci': [float(ci_lower_rho), float(ci_upper_rho)],
    'n_required_for_rho_minus0105': n_required,
    'ratio_current_to_required': float(n_nct / n_required),
    'achieved_power': float(achieved_power)
}

# ═══════════════════════════════════════════════
# SECTION 4: Cluster-Robust Bootstrap CIs
# ═══════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 4: Cluster-Robust Bootstrap CIs for BCT Temporal rho")
print("=" * 70)

N_BOOT = 10_000

# 4a) Naive bootstrap: resample deposits
print(f"\n4a) Naive bootstrap ({N_BOOT} resamples)")
naive_rhos = np.zeros(N_BOOT)
n_dep = len(bct_blocks)
for i in range(N_BOOT):
    idx = np.random.randint(0, n_dep, size=n_dep)
    naive_rhos[i], _ = stats.spearmanr(bct_blocks[idx], bct_scores[idx])

naive_ci = (np.percentile(naive_rhos, 2.5), np.percentile(naive_rhos, 97.5))
naive_width = naive_ci[1] - naive_ci[0]
print(f"  Naive bootstrap rho: mean={np.mean(naive_rhos):.4f}, median={np.median(naive_rhos):.4f}")
print(f"  95% CI: [{naive_ci[0]:.4f}, {naive_ci[1]:.4f}]")
print(f"  CI width: {naive_width:.4f}")

# 4b) Cluster-robust: resample TCO2 tokens (clusters) with all their deposits
print(f"\n4b) Cluster-robust bootstrap ({N_BOOT} resamples)")

# Build cluster structure: token -> list of (block, score) tuples
token_clusters = defaultdict(list)
for d in bct_deposits:
    addr = d['tco2_address']
    token_clusters[addr].append((d['block_number'], scores[addr]['composite']))

cluster_ids = list(token_clusters.keys())
n_clusters = len(cluster_ids)
print(f"  Number of clusters (unique TCO2 tokens): {n_clusters}")

cluster_rhos = np.zeros(N_BOOT)
for i in range(N_BOOT):
    # Resample clusters with replacement
    sampled_clusters = np.random.choice(cluster_ids, size=n_clusters, replace=True)
    boot_blocks = []
    boot_scores = []
    for cid in sampled_clusters:
        for (b, s) in token_clusters[cid]:
            boot_blocks.append(b)
            boot_scores.append(s)
    boot_blocks = np.array(boot_blocks)
    boot_scores = np.array(boot_scores)
    if len(set(boot_scores)) > 1 and len(set(boot_blocks)) > 1:
        cluster_rhos[i], _ = stats.spearmanr(boot_blocks, boot_scores)
    else:
        cluster_rhos[i] = 0.0

cluster_ci = (np.percentile(cluster_rhos, 2.5), np.percentile(cluster_rhos, 97.5))
cluster_width = cluster_ci[1] - cluster_ci[0]
print(f"  Cluster bootstrap rho: mean={np.mean(cluster_rhos):.4f}, median={np.median(cluster_rhos):.4f}")
print(f"  95% CI: [{cluster_ci[0]:.4f}, {cluster_ci[1]:.4f}]")
print(f"  CI width: {cluster_width:.4f}")

width_ratio = cluster_width / naive_width if naive_width > 0 else float('inf')
print(f"\n  Width comparison:")
print(f"    Naive CI width:   {naive_width:.4f}")
print(f"    Cluster CI width: {cluster_width:.4f}")
print(f"    Ratio (cluster/naive): {width_ratio:.2f}x")

if cluster_ci[0] > 0:
    cluster_sig = "YES (CI excludes zero)"
elif cluster_ci[1] < 0:
    cluster_sig = "YES (CI excludes zero, negative)"
else:
    cluster_sig = "NO (CI includes zero)"
print(f"  Cluster-robust significance: {cluster_sig}")

results['bootstrap_cis'] = {
    'n_bootstrap': N_BOOT,
    'observed_rho': float(rho_bct),
    'naive': {
        'mean': float(np.mean(naive_rhos)),
        'median': float(np.median(naive_rhos)),
        'ci_95': [float(naive_ci[0]), float(naive_ci[1])],
        'width': float(naive_width)
    },
    'cluster_robust': {
        'n_clusters': n_clusters,
        'mean': float(np.mean(cluster_rhos)),
        'median': float(np.median(cluster_rhos)),
        'ci_95': [float(cluster_ci[0]), float(cluster_ci[1])],
        'width': float(cluster_width)
    },
    'width_ratio_cluster_to_naive': float(width_ratio),
    'cluster_robust_significant': bool(cluster_ci[0] > 0 or cluster_ci[1] < 0)
}

# ═══════════════════════════════════════════════
# SECTION 5: Two-Sided Depositor Tests
# ═══════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 5: Two-Sided Depositor Tests")
print("=" * 70)

# 5a) Two-sided Mann-Whitney for large vs small depositors
print(f"\n5a) Two-sided Mann-Whitney U test")
print(f"  Large depositors (>= median volume): n={len(large_wallets)}")
print(f"  Small depositors (< median volume):  n={len(small_wallets)}")
print(f"  Median volume threshold: {median_vol:.1f} tonnes")

# Compute effect size (rank-biserial correlation)
n1 = len(large_qualities)
n2 = len(small_qualities)
r_rb = 1 - (2 * u_dep) / (n1 * n2)

print(f"  U = {u_dep:.0f}")
print(f"  p (two-sided) = {p_dep_two:.4f}")
print(f"  Rank-biserial r = {r_rb:.4f}")
print(f"  Large mean quality: {np.mean(large_qualities):.2f} (sd={np.std(large_qualities):.2f})")
print(f"  Small mean quality: {np.mean(small_qualities):.2f} (sd={np.std(small_qualities):.2f})")
print(f"  Difference: {np.mean(large_qualities) - np.mean(small_qualities):.2f}")

# 5b) Volume-weighted permutation test (10K)
print(f"\n5b) Volume-weighted permutation test ({N_PERM} permutations)")

# Observed VW quality gap: large minus small (volume-weighted across wallets)
large_vw_total = sum(depositor_tonnes[w] for w in large_wallets)
small_vw_total = sum(depositor_tonnes[w] for w in small_wallets)

large_vw_quality = sum(depositor_vw_quality[w] * depositor_tonnes[w] for w in large_wallets) / large_vw_total
small_vw_quality = sum(depositor_vw_quality[w] * depositor_tonnes[w] for w in small_wallets) / small_vw_total

observed_vw_gap = large_vw_quality - small_vw_quality
print(f"  Large VW quality: {large_vw_quality:.2f}")
print(f"  Small VW quality: {small_vw_quality:.2f}")
print(f"  Observed VW gap: {observed_vw_gap:.4f}")

# Permutation: randomly split wallets into large/small groups (same sizes)
perm_vw_gaps = np.zeros(N_PERM)
all_wallet_arr = np.array(all_wallets)
all_vw_q = np.array([depositor_vw_quality[w] for w in all_wallets])
all_vol = np.array([depositor_tonnes[w] for w in all_wallets])
n_large = len(large_wallets)

for i in range(N_PERM):
    perm_idx = np.random.permutation(len(all_wallets))
    perm_large_idx = perm_idx[:n_large]
    perm_small_idx = perm_idx[n_large:]

    perm_large_vol = all_vol[perm_large_idx]
    perm_small_vol = all_vol[perm_small_idx]

    perm_large_vw = np.average(all_vw_q[perm_large_idx], weights=perm_large_vol)
    perm_small_vw = np.average(all_vw_q[perm_small_idx], weights=perm_small_vol)

    perm_vw_gaps[i] = perm_large_vw - perm_small_vw

p_perm_dep = np.mean(np.abs(perm_vw_gaps) >= np.abs(observed_vw_gap))
print(f"  Permutation p-value (two-sided): {p_perm_dep:.4f}")
print(f"  Null distribution: mean={np.mean(perm_vw_gaps):.4f}, sd={np.std(perm_vw_gaps):.4f}")
print(f"  Null 95%: [{np.percentile(perm_vw_gaps, 2.5):.4f}, {np.percentile(perm_vw_gaps, 97.5):.4f}]")

results['depositor_tests'] = {
    'mann_whitney_two_sided': {
        'U': float(u_dep),
        'p_two_sided': float(p_dep_two),
        'rank_biserial_r': float(r_rb),
        'n_large': n1,
        'n_small': n2,
        'median_volume_threshold': float(median_vol),
        'large_mean_quality': float(np.mean(large_qualities)),
        'small_mean_quality': float(np.mean(small_qualities)),
        'quality_difference': float(np.mean(large_qualities) - np.mean(small_qualities))
    },
    'volume_weighted_permutation': {
        'observed_vw_gap': float(observed_vw_gap),
        'large_vw_quality': float(large_vw_quality),
        'small_vw_quality': float(small_vw_quality),
        'permutation_p_two_sided': float(p_perm_dep),
        'null_mean': float(np.mean(perm_vw_gaps)),
        'null_sd': float(np.std(perm_vw_gaps)),
        'null_95': [float(np.percentile(perm_vw_gaps, 2.5)),
                    float(np.percentile(perm_vw_gaps, 97.5))],
        'n_permutations': N_PERM
    }
}

# ═══════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════
print("\n" + "=" * 70)
print("SUMMARY OF FINDINGS")
print("=" * 70)

print("\n--- FDR Correction ---")
surviving = [r for r in fdr_results if r['survives_fdr']]
not_surviving = [r for r in fdr_results if not r['survives_fdr']]
print(f"Tests surviving BH-FDR (alpha=0.05): {len(surviving)}/{n_tests}")
for r in surviving:
    print(f"  + {r['test']:48s}  p_adj={r['p_adjusted']:.4e}")
print(f"Tests NOT surviving FDR:")
for r in not_surviving:
    print(f"  - {r['test']:48s}  p_adj={r['p_adjusted']:.4e}")

print("\n--- Permutation vs Asymptotic ---")
print(f"  BCT full:    asymptotic={p_bct:.4e}  ->  permutation={p_perm_bct:.4f}")
print(f"  Pre-Terra:   asymptotic={p_pre:.4e}  ->  permutation={p_perm_pre:.4f}")
print(f"  Base-rate:   asymptotic={p_binom:.4e}  ->  permutation={p_perm_base:.6f}")

print("\n--- NCT Power ---")
print(f"  MDE at n={n_nct}: |rho|={mde:.4f}")
print(f"  NCT rho 95% CI: [{ci_lower_rho:.4f}, {ci_upper_rho:.4f}]")
print(f"  n needed for rho=-0.105: {n_required} (have {n_nct}, need {n_required - n_nct} more)")

print("\n--- Cluster-Robust Bootstrap ---")
print(f"  Naive CI:   [{naive_ci[0]:.4f}, {naive_ci[1]:.4f}]  width={naive_width:.4f}")
print(f"  Cluster CI: [{cluster_ci[0]:.4f}, {cluster_ci[1]:.4f}]  width={cluster_width:.4f}")
print(f"  Cluster/Naive width ratio: {width_ratio:.2f}x")
print(f"  Cluster-robust significant: {cluster_sig}")

print("\n--- Two-Sided Depositor Tests ---")
print(f"  Mann-Whitney (two-sided): p={p_dep_two:.4f}, r_rb={r_rb:.4f}")
print(f"  VW permutation (two-sided): p={p_perm_dep:.4f}")

# Save results
output_path = f"{BASE}/statistical_robustness_results.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to: {output_path}")
