#!/usr/bin/env python3
"""
BCT vs NCT Difference-in-Differences: Quality Trajectory Comparison
====================================================================
Root fix for "NCT temporal trend underpowered" weakness.

Instead of testing "does NCT decline?" (underpowered, n=35 tokens),
we test "does BCT decline FASTER than NCT?" — a DiD design that pools
both pools' deposit-level data for much greater statistical power.

Model: quality_i = β₀ + β₁·BCT_i + β₂·time_i + β₃·(BCT×time)_i + ε_i

β₃ (interaction) is the key coefficient: BCT-specific quality decline
relative to NCT baseline. This is the actual causal question.

Robustness:
  1. OLS with cluster-robust SE (clustered by tco2_address)
  2. Permutation test on β₃ (10,000 permutations)
  3. Bayesian bootstrap for posterior distribution of β₃
  4. Event-study variant: pre/post Terra collapse phase interaction
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy import stats as sstats

HERE = Path(__file__).resolve().parent
DEP_DIR = HERE.parent / "depositor-analysis"


def load_panel():
    """Build panel dataset: each deposit event with pool, time, quality."""
    scores = json.loads((DEP_DIR / "tco2_scores_complete.json").read_text())
    bct_deps = json.loads((DEP_DIR / "bct_deposits_complete.json").read_text())
    nct_deps = json.loads((DEP_DIR / "nct_deposits.json").read_text())

    # Terra collapse block (Polygon): ~2022-05-09
    TERRA_BLOCK = 28_400_000

    panel = []
    for dep in bct_deps:
        addr = dep["tco2_address"].lower()
        if addr not in scores:
            continue
        panel.append({
            "pool": "BCT",
            "is_bct": 1,
            "block": dep["block_number"],
            "tonnes": dep["amount_tonnes"],
            "quality": scores[addr]["composite"],
            "grade": scores[addr]["grade"],
            "type": scores[addr]["type"],
            "tco2": addr,
            "post_terra": 1 if dep["block_number"] > TERRA_BLOCK else 0,
        })

    for dep in nct_deps:
        addr = dep["tco2_address"].lower()
        if addr not in scores:
            continue
        panel.append({
            "pool": "NCT",
            "is_bct": 0,
            "block": dep["block_number"],
            "tonnes": dep["amount_tonnes"],
            "quality": scores[addr]["composite"],
            "grade": scores[addr]["grade"],
            "type": scores[addr]["type"],
            "tco2": addr,
            "post_terra": 1 if dep["block_number"] > TERRA_BLOCK else 0,
        })

    return panel


def ols_with_cluster_robust_se(X, y, clusters):
    """OLS regression with cluster-robust (CR1) standard errors."""
    n, k = X.shape
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta
    r2 = 1 - np.sum(resid**2) / np.sum((y - y.mean())**2)

    # Cluster-robust variance (HC1-style with cluster adjustment)
    unique_clusters = np.unique(clusters)
    G = len(unique_clusters)

    # Meat of sandwich: sum of u_g * u_g' where u_g = X_g' * e_g
    XtX_inv = np.linalg.inv(X.T @ X)
    meat = np.zeros((k, k))
    for c in unique_clusters:
        idx = clusters == c
        Xc = X[idx]
        ec = resid[idx]
        score_c = Xc.T @ ec  # k x 1
        meat += np.outer(score_c, score_c)

    # Small-sample correction: G/(G-1) * (n-1)/(n-k)
    correction = (G / (G - 1)) * ((n - 1) / (n - k))
    V_cr = correction * XtX_inv @ meat @ XtX_inv
    se_cr = np.sqrt(np.diag(V_cr))

    # t-stats and p-values (using G-1 df for cluster-robust)
    t_stats = beta / se_cr
    p_values = 2 * sstats.t.sf(np.abs(t_stats), df=G - 1)

    return beta, se_cr, t_stats, p_values, r2


def permutation_test_interaction(panel, n_perm=10000):
    """Permutation test: shuffle pool labels, re-estimate β₃ each time."""
    blocks = np.array([p["block"] for p in panel], dtype=float)
    blocks_z = (blocks - blocks.mean()) / blocks.std()
    quality = np.array([p["quality"] for p in panel])
    is_bct = np.array([p["is_bct"] for p in panel])

    # Observed interaction coefficient (simple: regress quality on interaction)
    interaction = is_bct * blocks_z
    X = np.column_stack([np.ones(len(panel)), is_bct, blocks_z, interaction])
    beta_obs = np.linalg.lstsq(X, quality, rcond=None)[0]
    obs_beta3 = beta_obs[3]

    # Permute pool labels
    rng = np.random.default_rng(42)
    perm_beta3 = np.zeros(n_perm)
    for i in range(n_perm):
        perm_bct = rng.permutation(is_bct)
        perm_interaction = perm_bct * blocks_z
        X_perm = np.column_stack([np.ones(len(panel)), perm_bct, blocks_z, perm_interaction])
        beta_perm = np.linalg.lstsq(X_perm, quality, rcond=None)[0]
        perm_beta3[i] = beta_perm[3]

    p_two_sided = np.mean(np.abs(perm_beta3) >= np.abs(obs_beta3))
    p_one_sided = np.mean(perm_beta3 <= obs_beta3)  # BCT declines more

    return obs_beta3, perm_beta3, p_two_sided, p_one_sided


def bayesian_bootstrap(panel, n_boot=10000):
    """Bayesian bootstrap for posterior of β₃."""
    blocks = np.array([p["block"] for p in panel], dtype=float)
    blocks_z = (blocks - blocks.mean()) / blocks.std()
    quality = np.array([p["quality"] for p in panel])
    is_bct = np.array([p["is_bct"] for p in panel])
    interaction = is_bct * blocks_z
    X = np.column_stack([np.ones(len(panel)), is_bct, blocks_z, interaction])
    n = len(panel)

    rng = np.random.default_rng(123)
    boot_beta3 = np.zeros(n_boot)
    for i in range(n_boot):
        # Dirichlet weights (Bayesian bootstrap)
        w = rng.dirichlet(np.ones(n))
        W = np.diag(w * n)  # scale to sum=n for interpretability
        XtWX = X.T @ W @ X
        XtWy = X.T @ W @ quality
        try:
            beta = np.linalg.solve(XtWX, XtWy)
            boot_beta3[i] = beta[3]
        except np.linalg.LinAlgError:
            boot_beta3[i] = np.nan

    boot_beta3 = boot_beta3[~np.isnan(boot_beta3)]
    return boot_beta3


def main():
    print("=" * 70)
    print("BCT vs NCT DIFFERENCE-IN-DIFFERENCES")
    print("=" * 70)

    panel = load_panel()
    n_bct = sum(1 for p in panel if p["is_bct"])
    n_nct = sum(1 for p in panel if not p["is_bct"])
    print(f"\nPanel: {len(panel)} deposit events ({n_bct} BCT + {n_nct} NCT)")
    print(f"BCT unique tokens: {len(set(p['tco2'] for p in panel if p['is_bct']))}")
    print(f"NCT unique tokens: {len(set(p['tco2'] for p in panel if not p['is_bct']))}")

    # Normalize block numbers to [0, 1] for interpretability
    blocks = np.array([p["block"] for p in panel], dtype=float)
    blocks_z = (blocks - blocks.mean()) / blocks.std()
    quality = np.array([p["quality"] for p in panel])
    is_bct = np.array([p["is_bct"] for p in panel])
    tonnes = np.array([p["tonnes"] for p in panel])
    interaction = is_bct * blocks_z
    clusters = np.array([p["tco2"] for p in panel])

    # ── DiD regression ──────────────────────────────────────────────────
    print("\n── DiD Regression: quality ~ BCT + time + BCT×time ──")
    X = np.column_stack([np.ones(len(panel)), is_bct, blocks_z, interaction])
    labels = ["intercept", "β₁ (BCT)", "β₂ (time)", "β₃ (BCT×time)"]

    beta, se, t, p, r2 = ols_with_cluster_robust_se(X, quality, clusters)
    print(f"  R² = {r2:.4f}")
    print(f"  Clusters: {len(np.unique(clusters))}")
    for i, lbl in enumerate(labels):
        sig = "***" if p[i] < 0.001 else "**" if p[i] < 0.01 else "*" if p[i] < 0.05 else ""
        print(f"  {lbl:20s}: β={beta[i]:+8.3f}  SE={se[i]:.3f}  t={t[i]:+6.2f}  p={p[i]:.4f} {sig}")

    print(f"\n  KEY: β₃ = {beta[3]:+.3f} (p={p[3]:.4f})")
    if p[3] < 0.05:
        if beta[3] < 0:
            print("  → BCT quality declines significantly faster than NCT ✓")
        else:
            print("  → BCT quality increases faster than NCT (unexpected)")
    else:
        print("  → No significant differential trend (DiD interaction not significant)")

    # ── Tonnage-weighted DiD ────────────────────────────────────────────
    print("\n── Tonnage-Weighted DiD ──")
    W_tonnes = np.diag(tonnes / tonnes.mean())
    XtWX = X.T @ W_tonnes @ X
    XtWy = X.T @ W_tonnes @ quality
    beta_w = np.linalg.solve(XtWX, XtWy)

    # Bootstrap SE for weighted version
    rng = np.random.default_rng(999)
    boot_b3w = []
    unique_tokens = np.unique(clusters)
    for _ in range(2000):
        # Block bootstrap by token
        sampled_tokens = rng.choice(unique_tokens, size=len(unique_tokens), replace=True)
        idx = np.concatenate([np.where(clusters == t)[0] for t in sampled_tokens])
        Xb, yb, wb = X[idx], quality[idx], tonnes[idx]
        Wb = np.diag(wb / wb.mean())
        try:
            b = np.linalg.solve(Xb.T @ Wb @ Xb, Xb.T @ Wb @ yb)
            boot_b3w.append(b[3])
        except np.linalg.LinAlgError:
            pass
    boot_b3w = np.array(boot_b3w)
    se_w = np.std(boot_b3w)
    ci_w = np.percentile(boot_b3w, [2.5, 97.5])
    p_w = 2 * min(np.mean(boot_b3w >= 0), np.mean(boot_b3w <= 0))

    print(f"  β₃ (weighted) = {beta_w[3]:+.3f}  SE={se_w:.3f}  95% CI [{ci_w[0]:+.3f}, {ci_w[1]:+.3f}]  p≈{p_w:.4f}")

    # ── Event-study DiD (pre/post Terra) ────────────────────────────────
    print("\n── Event-Study DiD: Pre/Post Terra Collapse ──")
    post_terra = np.array([p["post_terra"] for p in panel])
    X_event = np.column_stack([np.ones(len(panel)), is_bct, post_terra, is_bct * post_terra])
    labels_event = ["intercept", "β₁ (BCT)", "β₂ (post-Terra)", "β₃ (BCT×post-Terra)"]

    beta_e, se_e, t_e, p_e, r2_e = ols_with_cluster_robust_se(X_event, quality, clusters)
    print(f"  R² = {r2_e:.4f}")
    for i, lbl in enumerate(labels_event):
        sig = "***" if p_e[i] < 0.001 else "**" if p_e[i] < 0.01 else "*" if p_e[i] < 0.05 else ""
        print(f"  {lbl:25s}: β={beta_e[i]:+8.3f}  SE={se_e[i]:.3f}  t={t_e[i]:+6.2f}  p={p_e[i]:.4f} {sig}")

    # ── Permutation test ────────────────────────────────────────────────
    print("\n── Permutation Test (10,000 shuffles) ──")
    obs_b3, perm_dist, p_2s, p_1s = permutation_test_interaction(panel)
    print(f"  Observed β₃ = {obs_b3:+.4f}")
    print(f"  Permutation p (two-sided) = {p_2s:.4f}")
    print(f"  Permutation p (one-sided, BCT worse) = {p_1s:.4f}")

    # ── Bayesian bootstrap posterior ────────────────────────────────────
    print("\n── Bayesian Bootstrap Posterior (10,000 draws) ──")
    posterior = bayesian_bootstrap(panel)
    prob_negative = np.mean(posterior < 0)
    ci_bayes = np.percentile(posterior, [2.5, 97.5])
    print(f"  Posterior mean β₃ = {np.mean(posterior):+.4f}")
    print(f"  95% credible interval: [{ci_bayes[0]:+.4f}, {ci_bayes[1]:+.4f}]")
    print(f"  P(β₃ < 0) = {prob_negative:.4f}")
    print(f"  → {prob_negative*100:.1f}% posterior probability that BCT declines faster than NCT")

    # ── Summary statistics by pool and period ───────────────────────────
    print("\n── Descriptive: Mean Quality by Pool × Period ──")
    for pool_name, pool_val in [("BCT", 1), ("NCT", 0)]:
        for period, period_val in [("Pre-Terra", 0), ("Post-Terra", 1)]:
            mask = (is_bct == pool_val) & (post_terra == period_val)
            n_obs = mask.sum()
            if n_obs > 0:
                q = quality[mask]
                t_sum = tonnes[mask].sum()
                wq = np.average(quality[mask], weights=tonnes[mask])
                print(f"  {pool_name:3s} {period:10s}: n={n_obs:5d}  mean_q={q.mean():.2f}  weighted_q={wq:.2f}  tonnes={t_sum:,.0f}")

    # ── Save results ────────────────────────────────────────────────────
    results = {
        "method": "Difference-in-Differences: BCT vs NCT quality trajectories",
        "date": "2026-05-05",
        "panel_size": len(panel),
        "n_bct_deposits": n_bct,
        "n_nct_deposits": n_nct,
        "n_bct_tokens": len(set(p["tco2"] for p in panel if p["is_bct"])),
        "n_nct_tokens": len(set(p["tco2"] for p in panel if not p["is_bct"])),

        "did_continuous_time": {
            "beta_intercept": round(float(beta[0]), 4),
            "beta_bct": round(float(beta[1]), 4),
            "beta_time": round(float(beta[2]), 4),
            "beta_interaction": round(float(beta[3]), 4),
            "se_interaction": round(float(se[3]), 4),
            "t_interaction": round(float(t[3]), 4),
            "p_interaction": round(float(p[3]), 6),
            "r_squared": round(float(r2), 4),
            "n_clusters": int(len(np.unique(clusters))),
        },

        "did_tonnage_weighted": {
            "beta_interaction": round(float(beta_w[3]), 4),
            "se_bootstrap": round(float(se_w), 4),
            "ci_95": [round(float(ci_w[0]), 4), round(float(ci_w[1]), 4)],
            "p_bootstrap": round(float(p_w), 4),
        },

        "did_event_study_terra": {
            "beta_intercept": round(float(beta_e[0]), 4),
            "beta_bct": round(float(beta_e[1]), 4),
            "beta_post_terra": round(float(beta_e[2]), 4),
            "beta_interaction": round(float(beta_e[3]), 4),
            "se_interaction": round(float(se_e[3]), 4),
            "t_interaction": round(float(t_e[3]), 4),
            "p_interaction": round(float(p_e[3]), 6),
            "r_squared": round(float(r2_e), 4),
        },

        "permutation_test": {
            "observed_beta3": round(float(obs_b3), 4),
            "p_two_sided": round(float(p_2s), 4),
            "p_one_sided_bct_worse": round(float(p_1s), 4),
            "n_permutations": 10000,
        },

        "bayesian_bootstrap": {
            "posterior_mean": round(float(np.mean(posterior)), 4),
            "posterior_sd": round(float(np.std(posterior)), 4),
            "ci_95_credible": [round(float(ci_bayes[0]), 4), round(float(ci_bayes[1]), 4)],
            "prob_bct_declines_faster": round(float(prob_negative), 4),
            "n_draws": len(posterior),
        },
    }

    out_path = HERE / "bct_nct_did_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n-> Saved to {out_path}")


if __name__ == "__main__":
    main()
