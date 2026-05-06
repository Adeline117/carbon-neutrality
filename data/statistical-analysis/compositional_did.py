#!/usr/bin/env python3
"""
Compositional DiD: BCT vs NCT renewable share trajectory.
Framework-free version of the quality DiD - uses credit type classification
(renewable vs non-renewable) instead of composite quality scores.

This demonstrates that the core BCT-NCT divergence holds WITHOUT
the scoring framework, using only on-chain data + Verra type classification.
"""

import json
import numpy as np
from scipy import stats as sstats
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEP_DIR = HERE.parent / "depositor-analysis"

TERRA_BLOCK = 28_400_000


def main():
    scores = json.loads((DEP_DIR / "tco2_scores_complete.json").read_text())
    bct_deps = json.loads((DEP_DIR / "bct_deposits_complete.json").read_text())
    nct_deps = json.loads((DEP_DIR / "nct_deposits.json").read_text())

    panel = []
    for dep in bct_deps:
        addr = dep["tco2_address"].lower()
        if addr not in scores:
            continue
        is_renewable = 1 if scores[addr]["type"] == "Renewable" else 0
        panel.append({
            "pool": "BCT", "is_bct": 1,
            "block": dep["block_number"],
            "tonnes": dep["amount_tonnes"],
            "is_renewable": is_renewable,
            "quality": scores[addr]["composite"],
            "tco2": addr,
            "post_terra": 1 if dep["block_number"] > TERRA_BLOCK else 0,
        })
    for dep in nct_deps:
        addr = dep["tco2_address"].lower()
        if addr not in scores:
            continue
        is_renewable = 1 if scores[addr]["type"] == "Renewable" else 0
        panel.append({
            "pool": "NCT", "is_bct": 0,
            "block": dep["block_number"],
            "tonnes": dep["amount_tonnes"],
            "is_renewable": is_renewable,
            "quality": scores[addr]["composite"],
            "tco2": addr,
            "post_terra": 1 if dep["block_number"] > TERRA_BLOCK else 0,
        })

    n_bct = sum(1 for p in panel if p["is_bct"])
    n_nct = sum(1 for p in panel if not p["is_bct"])
    print(f"Panel: {len(panel)} deposits ({n_bct} BCT + {n_nct} NCT)")

    # Arrays
    is_bct = np.array([p["is_bct"] for p in panel])
    post_terra = np.array([p["post_terra"] for p in panel])
    is_renewable = np.array([p["is_renewable"] for p in panel])
    quality = np.array([p["quality"] for p in panel])
    clusters = np.array([p["tco2"] for p in panel])

    # === Compositional DiD: renewable share ===
    X = np.column_stack([np.ones(len(panel)), is_bct, post_terra, is_bct * post_terra])

    # OLS with cluster-robust SE
    n, k = X.shape
    beta = np.linalg.lstsq(X, is_renewable, rcond=None)[0]
    resid = is_renewable - X @ beta
    unique_clusters = np.unique(clusters)
    G = len(unique_clusters)
    XtX_inv = np.linalg.inv(X.T @ X)
    meat = np.zeros((k, k))
    for c in unique_clusters:
        idx = clusters == c
        Xc = X[idx]
        ec = resid[idx]
        score_c = Xc.T @ ec
        meat += np.outer(score_c, score_c)
    correction = (G / (G - 1)) * ((n - 1) / (n - k))
    V_cr = correction * XtX_inv @ meat @ XtX_inv
    se_cr = np.sqrt(np.diag(V_cr))
    t_stats = beta / se_cr
    p_values = 2 * sstats.t.sf(np.abs(t_stats), df=G - 1)

    print("\n=== Compositional DiD: P(renewable) ===")
    labels = ["intercept", "BCT", "post-Terra", "BCT x post-Terra"]
    for i, lbl in enumerate(labels):
        sig = "***" if p_values[i] < 0.001 else "**" if p_values[i] < 0.01 else "*" if p_values[i] < 0.05 else ""
        print(f"  {lbl:20s}: β={beta[i]:+.4f}  SE={se_cr[i]:.4f}  t={t_stats[i]:+.2f}  p={p_values[i]:.4f} {sig}")

    # Descriptive: renewable share by pool x period
    print("\n=== Descriptive: Renewable share ===")
    for pool_name, pool_val in [("BCT", 1), ("NCT", 0)]:
        for period, period_val in [("Pre-Terra", 0), ("Post-Terra", 1)]:
            mask = (is_bct == pool_val) & (post_terra == period_val)
            if mask.sum() > 0:
                ren_share = is_renewable[mask].mean()
                n_obs = mask.sum()
                print(f"  {pool_name:3s} {period:10s}: n={n_obs:5d}  renewable_share={ren_share:.3f}")

    # === Quality DiD for comparison ===
    beta_q = np.linalg.lstsq(X, quality, rcond=None)[0]
    resid_q = quality - X @ beta_q
    meat_q = np.zeros((k, k))
    for c in unique_clusters:
        idx = clusters == c
        Xc = X[idx]
        ec = resid_q[idx]
        score_c = Xc.T @ ec
        meat_q += np.outer(score_c, score_c)
    V_cr_q = correction * XtX_inv @ meat_q @ XtX_inv
    se_cr_q = np.sqrt(np.diag(V_cr_q))
    t_q = beta_q / se_cr_q
    p_q = 2 * sstats.t.sf(np.abs(t_q), df=G - 1)

    print("\n=== Quality DiD (for comparison) ===")
    for i, lbl in enumerate(labels):
        sig = "***" if p_q[i] < 0.001 else "**" if p_q[i] < 0.01 else "*" if p_q[i] < 0.05 else ""
        print(f"  {lbl:20s}: β={beta_q[i]:+.4f}  SE={se_cr_q[i]:.4f}  t={t_q[i]:+.2f}  p={p_q[i]:.4f} {sig}")

    # Permutation test on compositional interaction
    rng = np.random.default_rng(42)
    obs_beta3 = beta[3]
    n_perm = 10000
    perm_beta3 = np.zeros(n_perm)
    for i in range(n_perm):
        perm_bct = rng.permutation(is_bct)
        X_perm = np.column_stack([np.ones(len(panel)), perm_bct, post_terra, perm_bct * post_terra])
        b = np.linalg.lstsq(X_perm, is_renewable, rcond=None)[0]
        perm_beta3[i] = b[3]
    p_perm = np.mean(np.abs(perm_beta3) >= np.abs(obs_beta3))

    print(f"\n=== Permutation test (compositional) ===")
    print(f"  Observed β₃ = {obs_beta3:+.4f}")
    print(f"  Permutation p (two-sided) = {p_perm:.4f}")

    # Save results
    results = {
        "method": "Compositional DiD: P(renewable) as framework-free outcome",
        "panel_size": len(panel),
        "n_bct": n_bct,
        "n_nct": n_nct,
        "n_clusters": G,
        "compositional_did": {
            "beta_intercept": round(float(beta[0]), 4),
            "beta_bct": round(float(beta[1]), 4),
            "beta_post_terra": round(float(beta[2]), 4),
            "beta_interaction": round(float(beta[3]), 4),
            "se_interaction": round(float(se_cr[3]), 4),
            "t_interaction": round(float(t_stats[3]), 2),
            "p_interaction": round(float(p_values[3]), 6),
        },
        "quality_did_comparison": {
            "beta_interaction": round(float(beta_q[3]), 4),
            "se_interaction": round(float(se_cr_q[3]), 4),
            "p_interaction": round(float(p_q[3]), 6),
        },
        "permutation_p": round(float(p_perm), 4),
        "descriptive": {
            "bct_pre_terra_renewable": round(float(is_renewable[(is_bct == 1) & (post_terra == 0)].mean()), 3),
            "bct_post_terra_renewable": round(float(is_renewable[(is_bct == 1) & (post_terra == 1)].mean()), 3),
            "nct_pre_terra_renewable": round(float(is_renewable[(is_bct == 0) & (post_terra == 0)].mean()), 3),
            "nct_post_terra_renewable": round(float(is_renewable[(is_bct == 0) & (post_terra == 1)].mean()), 3),
        },
    }

    out = HERE / "compositional_did_results.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n-> Saved to {out}")


if __name__ == "__main__":
    main()
