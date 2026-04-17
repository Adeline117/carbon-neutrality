#!/usr/bin/env python3
"""Wallet-Clustered Binomial Test for BCT Adverse Selection.

Part 2 of the Nature Comms evidence:
The paper's binomial test (p<10^-187) treats each deposit as independent,
but 509 wallets make 1,187 deposits (Gini=0.94, effective N=26.4).
This script properly accounts for wallet-level clustering.

Tests:
1. Wallet-level permutation test (10K iterations)
2. Wallet-level binomial test (n=509 wallets)
3. Effective-N binomial (n=1/HHI ~ 26.4)
4. Bootstrap CI on selection coefficient (wallet-resampling, 10K iterations)
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats as sstats

HERE = Path(__file__).resolve().parent

VCS_RENEWABLE_BASE_RATE = 0.37  # 37% of VCS universe is renewable


def compute_wallet_renewable_shares(
    deposits: list[dict],
    tco2_scores: dict[str, dict],
) -> dict:
    """Compute per-wallet renewable fraction (by count and by tonnage)."""

    wallet_stats = defaultdict(lambda: {
        "n_total": 0, "n_renewable": 0, "n_scored": 0,
        "tonnes_total": 0.0, "tonnes_renewable": 0.0, "tonnes_scored": 0.0,
        "deposits": [],
    })

    for d in deposits:
        wallet = d["depositor"].lower()
        tco2 = d["tco2_address"].lower()
        tonnes = d["amount_tonnes"]

        score_info = tco2_scores.get(tco2, {})
        credit_type = score_info.get("type")

        ws = wallet_stats[wallet]
        ws["n_total"] += 1
        ws["tonnes_total"] += tonnes

        if credit_type is not None:
            ws["n_scored"] += 1
            ws["tonnes_scored"] += tonnes
            is_renewable = credit_type == "Renewable"
            if is_renewable:
                ws["n_renewable"] += 1
                ws["tonnes_renewable"] += tonnes
            ws["deposits"].append({
                "tco2": tco2,
                "tonnes": tonnes,
                "type": credit_type,
                "is_renewable": is_renewable,
            })

    # Compute fractions
    wallet_shares = {}
    for wallet, ws in wallet_stats.items():
        if ws["n_scored"] > 0:
            wallet_shares[wallet] = {
                "n_total": ws["n_total"],
                "n_scored": ws["n_scored"],
                "n_renewable": ws["n_renewable"],
                "tonnes_total": ws["tonnes_total"],
                "tonnes_scored": ws["tonnes_scored"],
                "tonnes_renewable": ws["tonnes_renewable"],
                "frac_renewable_count": ws["n_renewable"] / ws["n_scored"],
                "frac_renewable_tonnes": ws["tonnes_renewable"] / ws["tonnes_scored"] if ws["tonnes_scored"] > 0 else 0,
                "deposits": ws["deposits"],
            }

    return wallet_shares


def wallet_clustered_permutation_test(
    wallet_shares: dict,
    base_rate: float = VCS_RENEWABLE_BASE_RATE,
    n_permutations: int = 10_000,
    seed: int = 42,
) -> dict:
    """Wallet-clustered permutation test.

    H0: the wallet-level renewable share equals the VCS base rate.

    For each permutation:
    - For each wallet, randomly assign renewable/non-renewable labels to each
      of its deposits with P(renewable) = base_rate, independently per wallet
    - Compute the wallet-mean renewable share
    - p-value = fraction of permutations where stat >= observed
    """
    rng = np.random.default_rng(seed)

    # Observed: mean wallet-level renewable share (by count)
    count_fracs = np.array([ws["frac_renewable_count"] for ws in wallet_shares.values()])
    tonnage_fracs = np.array([ws["frac_renewable_tonnes"] for ws in wallet_shares.values()])

    observed_mean_count = float(np.mean(count_fracs))
    observed_mean_tonnage = float(np.mean(tonnage_fracs))

    # Also compute tonnage-weighted mean across wallets
    total_scored_tonnes = sum(ws["tonnes_scored"] for ws in wallet_shares.values())
    observed_weighted_mean = sum(
        ws["frac_renewable_tonnes"] * ws["tonnes_scored"]
        for ws in wallet_shares.values()
    ) / total_scored_tonnes if total_scored_tonnes > 0 else 0

    # Wallet deposit counts (for simulation)
    wallet_n_scored = [ws["n_scored"] for ws in wallet_shares.values()]
    wallet_tonnes_per_deposit = []
    for ws in wallet_shares.values():
        tonnes_list = [d["tonnes"] for d in ws["deposits"]]
        wallet_tonnes_per_deposit.append(tonnes_list)

    n_wallets = len(wallet_n_scored)

    # Permutation: count-based
    perm_means_count = np.zeros(n_permutations)
    perm_means_tonnage = np.zeros(n_permutations)
    perm_means_weighted = np.zeros(n_permutations)

    for i in range(n_permutations):
        wallet_fracs_count = np.zeros(n_wallets)
        wallet_fracs_tonnage = np.zeros(n_wallets)
        wallet_tonnage_weighted_num = 0.0

        for j in range(n_wallets):
            n_deps = wallet_n_scored[j]
            tonnes_list = wallet_tonnes_per_deposit[j]
            total_t = sum(tonnes_list)

            # Random assignment: each deposit is renewable with P=base_rate
            is_renewable = rng.random(n_deps) < base_rate
            wallet_fracs_count[j] = np.mean(is_renewable)

            if total_t > 0:
                renewable_tonnes = sum(
                    t for t, r in zip(tonnes_list, is_renewable) if r
                )
                wallet_fracs_tonnage[j] = renewable_tonnes / total_t
                wallet_tonnage_weighted_num += (renewable_tonnes / total_t) * total_t
            else:
                wallet_fracs_tonnage[j] = np.mean(is_renewable)

        perm_means_count[i] = np.mean(wallet_fracs_count)
        perm_means_tonnage[i] = np.mean(wallet_fracs_tonnage)
        perm_means_weighted[i] = wallet_tonnage_weighted_num / total_scored_tonnes if total_scored_tonnes > 0 else 0

    # p-values (one-sided: observed >= permuted)
    p_count = float(np.mean(perm_means_count >= observed_mean_count))
    p_tonnage = float(np.mean(perm_means_tonnage >= observed_mean_tonnage))
    p_weighted = float(np.mean(perm_means_weighted >= observed_weighted_mean))

    return {
        "n_wallets": n_wallets,
        "n_permutations": n_permutations,
        "base_rate": base_rate,
        "observed_mean_wallet_renewable_share_count": observed_mean_count,
        "observed_mean_wallet_renewable_share_tonnage": observed_mean_tonnage,
        "observed_weighted_mean_renewable_share": float(observed_weighted_mean),
        "permutation_null_mean_count": float(np.mean(perm_means_count)),
        "permutation_null_sd_count": float(np.std(perm_means_count)),
        "permutation_null_95ci_count": [
            float(np.percentile(perm_means_count, 2.5)),
            float(np.percentile(perm_means_count, 97.5)),
        ],
        "p_value_count": p_count,
        "permutation_null_mean_tonnage": float(np.mean(perm_means_tonnage)),
        "permutation_null_sd_tonnage": float(np.std(perm_means_tonnage)),
        "permutation_null_95ci_tonnage": [
            float(np.percentile(perm_means_tonnage, 2.5)),
            float(np.percentile(perm_means_tonnage, 97.5)),
        ],
        "p_value_tonnage": p_tonnage,
        "permutation_null_mean_weighted": float(np.mean(perm_means_weighted)),
        "permutation_null_sd_weighted": float(np.std(perm_means_weighted)),
        "p_value_weighted": p_weighted,
        "interpretation": (
            f"Observed wallet-mean renewable share = {observed_mean_count:.3f} "
            f"vs null mean = {np.mean(perm_means_count):.3f} (base rate {base_rate}). "
            f"Permutation p = {p_count:.4f}"
        ),
    }


def wallet_level_binomial_test(
    wallet_shares: dict,
    base_rate: float = VCS_RENEWABLE_BASE_RATE,
) -> dict:
    """Wallet-level binomial test: what fraction of wallets have >50% renewable?"""
    n_wallets = len(wallet_shares)
    n_majority_renewable_count = sum(
        1 for ws in wallet_shares.values() if ws["frac_renewable_count"] > 0.5
    )
    n_majority_renewable_tonnage = sum(
        1 for ws in wallet_shares.values() if ws["frac_renewable_tonnes"] > 0.5
    )

    # Under H0: P(wallet has >50% renewable) when each deposit is renewable
    # with P=base_rate. For a wallet with n deposits, P(>50% renewable) =
    # 1 - binom.cdf(n//2, n, base_rate).
    # The expected number of majority-renewable wallets:
    expected_majority = 0
    for ws in wallet_shares.values():
        n = ws["n_scored"]
        threshold = n // 2  # more than 50%
        p_majority = 1 - sstats.binom.cdf(threshold, n, base_rate)
        expected_majority += p_majority

    # Average probability of a wallet being majority-renewable
    avg_p_majority = expected_majority / n_wallets if n_wallets > 0 else 0

    # Binomial test on wallet-level
    binom_result_count = sstats.binomtest(
        n_majority_renewable_count, n_wallets, avg_p_majority, alternative="greater"
    )
    binom_result_tonnage = sstats.binomtest(
        n_majority_renewable_tonnage, n_wallets, avg_p_majority, alternative="greater"
    )

    return {
        "n_wallets": n_wallets,
        "n_majority_renewable_by_count": n_majority_renewable_count,
        "n_majority_renewable_by_tonnage": n_majority_renewable_tonnage,
        "frac_majority_renewable_count": n_majority_renewable_count / n_wallets if n_wallets else 0,
        "frac_majority_renewable_tonnage": n_majority_renewable_tonnage / n_wallets if n_wallets else 0,
        "expected_majority_renewable_under_H0": expected_majority,
        "avg_p_majority_under_H0": avg_p_majority,
        "binomial_p_count": float(binom_result_count.pvalue),
        "binomial_p_tonnage": float(binom_result_tonnage.pvalue),
        "binomial_ci95_count": [float(x) for x in binom_result_count.proportion_ci(confidence_level=0.95)],
    }


def effective_n_binomial(
    deposits: list[dict],
    tco2_scores: dict[str, dict],
    base_rate: float = VCS_RENEWABLE_BASE_RATE,
) -> dict:
    """Effective-N binomial using HHI to account for deposit concentration."""
    # Compute wallet-level deposit concentrations
    wallet_deposits = defaultdict(int)
    for d in deposits:
        wallet_deposits[d["depositor"].lower()] += 1

    n_deposits = len(deposits)
    n_wallets = len(wallet_deposits)

    # HHI (deposit concentration)
    shares = [count / n_deposits for count in wallet_deposits.values()]
    hhi = sum(s ** 2 for s in shares)
    effective_n = 1 / hhi

    # Gini coefficient
    sorted_counts = sorted(wallet_deposits.values())
    n = len(sorted_counts)
    cumsum = np.cumsum(sorted_counts)
    gini = 1 - 2 * sum(cumsum) / (n * sum(sorted_counts)) + 1 / n

    # Count renewable deposits
    n_renewable = 0
    n_scored = 0
    for d in deposits:
        tco2 = d["tco2_address"].lower()
        score_info = tco2_scores.get(tco2, {})
        if score_info.get("type") is not None:
            n_scored += 1
            if score_info["type"] == "Renewable":
                n_renewable += 1

    renewable_rate = n_renewable / n_scored if n_scored > 0 else 0

    # Naive binomial (treats all deposits as independent)
    naive_binom = sstats.binomtest(n_renewable, n_scored, base_rate, alternative="greater")

    # Effective-N binomial: rescale to effective_n observations
    # k_effective = renewable_rate * effective_n
    k_effective = round(renewable_rate * effective_n)
    n_effective_int = round(effective_n)
    effective_binom = sstats.binomtest(
        k_effective, n_effective_int, base_rate, alternative="greater"
    )

    # Also compute with a more conservative effective N based on
    # the design effect (DEFF = 1 + (CV^2 of cluster sizes) * rho_ICC)
    # Approximate rho_ICC ~ 0.5 (within-wallet correlation for renewable)
    counts_arr = np.array(list(wallet_deposits.values()), dtype=float)
    mean_cluster = np.mean(counts_arr)
    var_cluster = np.var(counts_arr, ddof=1)
    cv2_cluster = var_cluster / (mean_cluster ** 2) if mean_cluster > 0 else 0

    rho_icc = 0.5  # conservative ICC estimate
    deff = 1 + cv2_cluster * rho_icc * (mean_cluster - 1)
    effective_n_deff = n_scored / deff

    k_deff = round(renewable_rate * effective_n_deff)
    n_deff_int = round(effective_n_deff)
    deff_binom = sstats.binomtest(
        min(k_deff, n_deff_int), n_deff_int, base_rate, alternative="greater"
    )

    return {
        "n_deposits": n_deposits,
        "n_wallets": n_wallets,
        "n_scored": n_scored,
        "n_renewable": n_renewable,
        "renewable_rate": renewable_rate,
        "base_rate": base_rate,
        "hhi": hhi,
        "effective_n_hhi": effective_n,
        "gini": float(gini),
        "mean_deposits_per_wallet": float(mean_cluster),
        "cv2_cluster_sizes": float(cv2_cluster),
        "naive_binomial_p": float(naive_binom.pvalue),
        "naive_binomial_ci95": [float(x) for x in naive_binom.proportion_ci()],
        "effective_n_binomial": {
            "n_effective": n_effective_int,
            "k_effective": k_effective,
            "p_value": float(effective_binom.pvalue),
            "ci95": [float(x) for x in effective_binom.proportion_ci()],
        },
        "deff_adjusted_binomial": {
            "rho_icc_assumed": rho_icc,
            "deff": float(deff),
            "n_effective_deff": float(effective_n_deff),
            "n_effective_deff_int": n_deff_int,
            "k_effective_deff": min(k_deff, n_deff_int),
            "p_value": float(deff_binom.pvalue),
        },
        "summary": (
            f"Naive binomial (n={n_scored}): p={naive_binom.pvalue:.2e}. "
            f"HHI-adjusted (n_eff={effective_n:.1f}): p={effective_binom.pvalue:.4f}. "
            f"DEFF-adjusted (n_eff={effective_n_deff:.1f}): p={deff_binom.pvalue:.4f}. "
            f"Gini={gini:.3f}, HHI={hhi:.4f}"
        ),
    }


def bootstrap_selection_coefficient(
    wallet_shares: dict,
    base_rate: float = VCS_RENEWABLE_BASE_RATE,
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> dict:
    """Bootstrap CI on the selection coefficient, resampling at wallet level."""
    rng = np.random.default_rng(seed)

    wallets = list(wallet_shares.values())
    n_wallets = len(wallets)

    # Selection coefficient = observed renewable rate - base rate
    # Computed at wallet level, then averaged

    # Observed
    obs_fracs = np.array([w["frac_renewable_count"] for w in wallets])
    obs_fracs_tonnage = np.array([w["frac_renewable_tonnes"] for w in wallets])
    obs_mean = float(np.mean(obs_fracs))
    obs_mean_tonnage = float(np.mean(obs_fracs_tonnage))
    obs_selection_coeff = obs_mean - base_rate
    obs_selection_coeff_tonnage = obs_mean_tonnage - base_rate

    # Bootstrap: resample wallets with replacement
    boot_means_count = np.zeros(n_bootstrap)
    boot_means_tonnage = np.zeros(n_bootstrap)

    for i in range(n_bootstrap):
        idx = rng.integers(0, n_wallets, size=n_wallets)
        boot_means_count[i] = np.mean(obs_fracs[idx])
        boot_means_tonnage[i] = np.mean(obs_fracs_tonnage[idx])

    boot_coeff_count = boot_means_count - base_rate
    boot_coeff_tonnage = boot_means_tonnage - base_rate

    ci_count = [float(np.percentile(boot_coeff_count, 2.5)),
                float(np.percentile(boot_coeff_count, 97.5))]
    ci_tonnage = [float(np.percentile(boot_coeff_tonnage, 2.5)),
                  float(np.percentile(boot_coeff_tonnage, 97.5))]

    # BCa bootstrap CI (bias-corrected and accelerated)
    # Bias correction
    z0_count = float(sstats.norm.ppf(np.mean(boot_means_count < obs_mean)))
    z0_tonnage = float(sstats.norm.ppf(np.mean(boot_means_tonnage < obs_mean_tonnage)))

    # Acceleration (jackknife)
    jackknife_means_count = np.zeros(n_wallets)
    jackknife_means_tonnage = np.zeros(n_wallets)
    for j in range(n_wallets):
        mask = np.ones(n_wallets, dtype=bool)
        mask[j] = False
        jackknife_means_count[j] = np.mean(obs_fracs[mask])
        jackknife_means_tonnage[j] = np.mean(obs_fracs_tonnage[mask])

    jk_mean_count = np.mean(jackknife_means_count)
    jk_diff_count = jk_mean_count - jackknife_means_count
    a_count = float(np.sum(jk_diff_count ** 3) / (6 * (np.sum(jk_diff_count ** 2)) ** 1.5)) if np.sum(jk_diff_count ** 2) > 0 else 0

    jk_mean_tonnage = np.mean(jackknife_means_tonnage)
    jk_diff_tonnage = jk_mean_tonnage - jackknife_means_tonnage
    a_tonnage = float(np.sum(jk_diff_tonnage ** 3) / (6 * (np.sum(jk_diff_tonnage ** 2)) ** 1.5)) if np.sum(jk_diff_tonnage ** 2) > 0 else 0

    # BCa percentiles
    alpha_lo, alpha_hi = 0.025, 0.975
    z_lo, z_hi = sstats.norm.ppf(alpha_lo), sstats.norm.ppf(alpha_hi)

    def bca_quantile(z0, a, z):
        return float(sstats.norm.cdf(z0 + (z0 + z) / (1 - a * (z0 + z))))

    bca_lo_count = bca_quantile(z0_count, a_count, z_lo)
    bca_hi_count = bca_quantile(z0_count, a_count, z_hi)
    bca_ci_count = [
        float(np.percentile(boot_coeff_count, bca_lo_count * 100)),
        float(np.percentile(boot_coeff_count, bca_hi_count * 100)),
    ]

    return {
        "n_wallets": n_wallets,
        "n_bootstrap": n_bootstrap,
        "base_rate": base_rate,
        "observed_mean_renewable_share_count": obs_mean,
        "observed_mean_renewable_share_tonnage": obs_mean_tonnage,
        "selection_coefficient_count": obs_selection_coeff,
        "selection_coefficient_tonnage": obs_selection_coeff_tonnage,
        "bootstrap_ci95_count": ci_count,
        "bootstrap_ci95_tonnage": ci_tonnage,
        "bca_ci95_count": bca_ci_count,
        "bootstrap_se_count": float(np.std(boot_coeff_count)),
        "bootstrap_se_tonnage": float(np.std(boot_coeff_tonnage)),
        "bootstrap_bias_count": float(np.mean(boot_coeff_count) - obs_selection_coeff),
        "z_score_count": float(obs_selection_coeff / np.std(boot_coeff_count)) if np.std(boot_coeff_count) > 0 else None,
        "interpretation": (
            f"Selection coefficient (count) = {obs_selection_coeff:.3f} "
            f"[{ci_count[0]:.3f}, {ci_count[1]:.3f}] 95% CI. "
            f"Selection coefficient (tonnage) = {obs_selection_coeff_tonnage:.3f} "
            f"[{ci_tonnage[0]:.3f}, {ci_tonnage[1]:.3f}] 95% CI."
        ),
    }


def main():
    print("=" * 70)
    print("WALLET-CLUSTERED BINOMIAL TEST")
    print("=" * 70)

    # Load data
    deposits = json.loads((HERE / "bct_deposits_enriched.json").read_text())
    tco2_scores = {
        k.lower(): v
        for k, v in json.loads((HERE / "tco2_scores_complete.json").read_text()).items()
    }

    print(f"Loaded {len(deposits)} deposits, {len(tco2_scores)} TCO2 scores")

    # Step 1: Compute wallet-level renewable shares
    print("\n--- Step 1: Wallet-level renewable shares ---")
    wallet_shares = compute_wallet_renewable_shares(deposits, tco2_scores)
    print(f"  Wallets with scored deposits: {len(wallet_shares)}")

    # Distribution summary
    fracs = [ws["frac_renewable_count"] for ws in wallet_shares.values()]
    fracs_arr = np.array(fracs)
    print(f"  Mean wallet renewable share (count): {np.mean(fracs_arr):.3f}")
    print(f"  Median: {np.median(fracs_arr):.3f}")
    print(f"  SD: {np.std(fracs_arr, ddof=1):.3f}")
    print(f"  Wallets 100% renewable: {sum(1 for f in fracs if f == 1.0)}")
    print(f"  Wallets 0% renewable: {sum(1 for f in fracs if f == 0.0)}")
    print(f"  Wallets >50% renewable: {sum(1 for f in fracs if f > 0.5)}")

    # Step 2: Wallet-clustered permutation test
    print("\n--- Step 2: Wallet-clustered permutation test (10K iterations) ---")
    perm_results = wallet_clustered_permutation_test(wallet_shares)
    print(f"  Observed mean wallet renewable share: {perm_results['observed_mean_wallet_renewable_share_count']:.3f}")
    print(f"  Null mean (base rate {VCS_RENEWABLE_BASE_RATE}): {perm_results['permutation_null_mean_count']:.3f}")
    print(f"  Null 95% CI: [{perm_results['permutation_null_95ci_count'][0]:.3f}, {perm_results['permutation_null_95ci_count'][1]:.3f}]")
    print(f"  p-value (count): {perm_results['p_value_count']:.4f}")
    print(f"  p-value (tonnage): {perm_results['p_value_tonnage']:.4f}")
    print(f"  p-value (weighted): {perm_results['p_value_weighted']:.4f}")

    # Step 3: Wallet-level binomial test
    print("\n--- Step 3: Wallet-level binomial test ---")
    binom_results = wallet_level_binomial_test(wallet_shares)
    print(f"  Wallets majority-renewable (count): {binom_results['n_majority_renewable_by_count']}/{binom_results['n_wallets']}")
    print(f"  Expected under H0: {binom_results['expected_majority_renewable_under_H0']:.1f}")
    print(f"  Binomial p (count): {binom_results['binomial_p_count']:.4e}")
    print(f"  Binomial p (tonnage): {binom_results['binomial_p_tonnage']:.4e}")

    # Step 4: Effective-N binomial
    print("\n--- Step 4: Effective-N binomial ---")
    eff_n_results = effective_n_binomial(deposits, tco2_scores)
    print(f"  HHI: {eff_n_results['hhi']:.4f}")
    print(f"  Effective N (1/HHI): {eff_n_results['effective_n_hhi']:.1f}")
    print(f"  Gini: {eff_n_results['gini']:.3f}")
    print(f"  Naive binomial p: {eff_n_results['naive_binomial_p']:.2e}")
    print(f"  HHI-adjusted p: {eff_n_results['effective_n_binomial']['p_value']:.4f}")
    print(f"  DEFF-adjusted p: {eff_n_results['deff_adjusted_binomial']['p_value']:.4f}")
    print(f"  DEFF: {eff_n_results['deff_adjusted_binomial']['deff']:.2f}")

    # Step 5: Bootstrap CI on selection coefficient
    print("\n--- Step 5: Bootstrap CI on selection coefficient (10K iterations) ---")
    boot_results = bootstrap_selection_coefficient(wallet_shares)
    print(f"  Selection coeff (count): {boot_results['selection_coefficient_count']:.3f}")
    print(f"  95% CI (count): [{boot_results['bootstrap_ci95_count'][0]:.3f}, {boot_results['bootstrap_ci95_count'][1]:.3f}]")
    print(f"  BCa 95% CI (count): [{boot_results['bca_ci95_count'][0]:.3f}, {boot_results['bca_ci95_count'][1]:.3f}]")
    print(f"  Selection coeff (tonnage): {boot_results['selection_coefficient_tonnage']:.3f}")
    print(f"  95% CI (tonnage): [{boot_results['bootstrap_ci95_tonnage'][0]:.3f}, {boot_results['bootstrap_ci95_tonnage'][1]:.3f}]")
    print(f"  Bootstrap SE (count): {boot_results['bootstrap_se_count']:.4f}")
    if boot_results.get("z_score_count"):
        print(f"  z-score (count): {boot_results['z_score_count']:.2f}")

    # Assemble combined results
    results = {
        "wallet_renewable_shares_summary": {
            "n_wallets": len(wallet_shares),
            "mean_renewable_share_count": float(np.mean(fracs_arr)),
            "median_renewable_share_count": float(np.median(fracs_arr)),
            "sd_renewable_share_count": float(np.std(fracs_arr, ddof=1)),
            "n_100pct_renewable": int(sum(1 for f in fracs if f == 1.0)),
            "n_0pct_renewable": int(sum(1 for f in fracs if f == 0.0)),
            "n_gt50pct_renewable": int(sum(1 for f in fracs if f > 0.5)),
        },
        "permutation_test": perm_results,
        "wallet_binomial_test": binom_results,
        "effective_n_analysis": eff_n_results,
        "bootstrap_selection_coefficient": boot_results,
        "conclusion": "",
    }

    # Write conclusion
    if perm_results["p_value_count"] < 0.05:
        conclusion = (
            f"SIGNIFICANT: Even after clustering at the wallet level (n={len(wallet_shares)} wallets, "
            f"Gini={eff_n_results['gini']:.3f}, effective N={eff_n_results['effective_n_hhi']:.1f}), "
            f"the renewable over-representation in BCT deposits remains statistically significant. "
            f"Wallet-clustered permutation p={perm_results['p_value_count']:.4f}. "
            f"Selection coefficient = {boot_results['selection_coefficient_count']:.3f} "
            f"[{boot_results['bootstrap_ci95_count'][0]:.3f}, {boot_results['bootstrap_ci95_count'][1]:.3f}]. "
            f"The naive binomial p={eff_n_results['naive_binomial_p']:.2e} is inflated by clustering, "
            f"but the corrected tests still reject H0."
        )
    else:
        conclusion = (
            f"After clustering at the wallet level (n={len(wallet_shares)} wallets, "
            f"Gini={eff_n_results['gini']:.3f}, effective N={eff_n_results['effective_n_hhi']:.1f}), "
            f"the renewable over-representation does NOT remain significant at alpha=0.05. "
            f"Wallet-clustered permutation p={perm_results['p_value_count']:.4f}. "
            f"The naive binomial p={eff_n_results['naive_binomial_p']:.2e} was severely inflated by clustering."
        )

    results["conclusion"] = conclusion
    print(f"\n{'=' * 70}")
    print("CONCLUSION")
    print("=" * 70)
    print(conclusion)

    # Save
    out_path = HERE / "wallet_clustered_test.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nSaved to {out_path.name}")


if __name__ == "__main__":
    main()
