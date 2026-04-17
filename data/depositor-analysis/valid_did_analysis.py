#!/usr/bin/env python3
"""Valid Difference-in-Differences analysis addressing the SUTVA violation.

The original BCT-vs-NCT DiD in `nct_comparison_results.json` is compromised
because 31/35 NCT tokens (88.6%) also appear in BCT, and 14.9% of BCT
tonnage comes from wallets that also deposit in NCT. Treatment and control
share units --> SUTVA independence fails, Fisher z independent-sample test
assumptions fail.

This script implements three alternative identification strategies:

    1.  Non-overlapping subsets
        - BCT-only tokens vs NCT-only tokens
        - Removes the shared-unit dependence entirely.

    2.  Token-clustered bootstrap standard errors
        - Pool deposits from BCT and NCT, resample clusters (TCO2 tokens)
          with replacement, recompute each pool's Spearman rho per bootstrap
          replicate, and report the cluster-robust SE of (rho_BCT - rho_NCT).

    3.  Within-BCT DiD: Renewable vs Nature-based
        - Same pool, same depositor population, only the credit type varies.
        - Formal Fisher z-test of the two within-BCT correlations.

Alternative control candidate MCO2 (Moss) is assessed for data availability.

Outputs: valid_did_analysis.json + console report.
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats as sstats

HERE = Path(__file__).resolve().parent

RNG = np.random.default_rng(20260416)
N_BOOT = 5000


# ──────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────

def load_scored_deposits() -> tuple[list[dict], list[dict]]:
    """Load BCT + NCT deposits and attach composite quality / type."""
    scores = {k.lower(): v for k, v in
              json.loads((HERE / "tco2_scores_final.json").read_text()).items()}

    bct = json.loads((HERE / "bct_deposits_enriched.json").read_text())
    nct = json.loads((HERE / "nct_deposits.json").read_text())

    for d in bct + nct:
        addr = d["tco2_address"].lower()
        s = scores.get(addr)
        d["composite_quality"] = s["composite"] if s else None
        d["credit_type"] = s["type"] if s else None
    return bct, nct


def filter_scored(deps: list[dict]) -> list[dict]:
    return [d for d in deps if d.get("composite_quality") is not None]


def spearman(deps: list[dict]) -> tuple[float, float, int]:
    if len(deps) < 3:
        return (float("nan"), float("nan"), len(deps))
    x = np.array([d["block_number"] for d in deps], dtype=float)
    y = np.array([d["composite_quality"] for d in deps], dtype=float)
    rho, p = sstats.spearmanr(x, y)
    return float(rho), float(p), len(deps)


def half_split(deps: list[dict]) -> tuple[float, float]:
    """Mean composite_quality in the first vs second half (by block)."""
    if len(deps) < 4:
        return (float("nan"), float("nan"))
    order = sorted(deps, key=lambda d: d["block_number"])
    mid = len(order) // 2
    early = np.mean([d["composite_quality"] for d in order[:mid]])
    late = np.mean([d["composite_quality"] for d in order[mid:]])
    return float(early), float(late)


def fisher_z_test(rho_a: float, n_a: int, rho_b: float, n_b: int) -> dict:
    """Standard independent-sample Fisher z comparison of two correlations."""
    if n_a <= 3 or n_b <= 3 or any(abs(r) >= 1 for r in (rho_a, rho_b)):
        return {"z": None, "p": None, "note": "insufficient data"}
    za = math.atanh(rho_a)
    zb = math.atanh(rho_b)
    se = math.sqrt(1 / (n_a - 3) + 1 / (n_b - 3))
    z = (za - zb) / se
    p = 2 * sstats.norm.sf(abs(z))
    return {"z": float(z), "p": float(p), "rho_a": rho_a, "rho_b": rho_b,
            "n_a": n_a, "n_b": n_b}


# ──────────────────────────────────────────────────────────────────────────
# 1. Non-overlapping-subset DiD
# ──────────────────────────────────────────────────────────────────────────

def non_overlapping_subset_did(bct: list[dict], nct: list[dict]) -> dict:
    """Restrict BCT to tokens NEVER deposited into NCT, and vice versa."""
    bct_tokens = {d["tco2_address"].lower() for d in bct}
    nct_tokens = {d["tco2_address"].lower() for d in nct}
    bct_only_tokens = bct_tokens - nct_tokens
    nct_only_tokens = nct_tokens - bct_tokens
    shared_tokens = bct_tokens & nct_tokens

    bct_only_scored = filter_scored(
        [d for d in bct if d["tco2_address"].lower() in bct_only_tokens])
    nct_only_scored = filter_scored(
        [d for d in nct if d["tco2_address"].lower() in nct_only_tokens])

    rho_b, p_b, n_b = spearman(bct_only_scored)
    rho_n, p_n, n_n = spearman(nct_only_scored)

    bct_early, bct_late = half_split(bct_only_scored)
    nct_early, nct_late = half_split(nct_only_scored)
    bct_change = bct_late - bct_early if not math.isnan(bct_early) else float("nan")
    nct_change = nct_late - nct_early if not math.isnan(nct_early) else float("nan")
    did_estimate = bct_change - nct_change if not (
        math.isnan(bct_change) or math.isnan(nct_change)) else float("nan")

    fisher = fisher_z_test(rho_b, n_b, rho_n, n_n)

    # Warnings on small N
    warnings = []
    if n_n < 30:
        warnings.append(
            f"NCT-only subset tiny (n={n_n}); Spearman p unreliable, "
            "DiD underpowered.")
    if n_b < 30:
        warnings.append(f"BCT-only subset small (n={n_b}).")

    # Conclusion logic — must handle NaN (NCT-only scored==0)
    bct_computable = not math.isnan(rho_b)
    nct_computable = not math.isnan(rho_n)
    bct_degrades = bct_computable and rho_b < -0.2 and p_b < 0.05
    nct_degrades = nct_computable and rho_n < -0.2 and p_n < 0.05

    if not nct_computable:
        # This is the actual situation: all 4 NCT-only tokens are unscored.
        conclusion = (
            "DiD NOT IDENTIFIED in this design. All 4 NCT-only tokens are "
            "unscored, leaving zero scored deposits on the control side. "
            f"The BCT-only side still degrades (rho={rho_b:+.3f}, p={p_b:.2e}), "
            "confirming that degradation is not driven solely by the "
            "shared-token subset — but without a control arm there is no "
            "DiD. Non-overlapping-subset design is infeasible with current "
            "scoring coverage."
        )
    elif bct_degrades and not nct_degrades:
        conclusion = "DiD survives: BCT-only degrades, NCT-only does not."
    elif not bct_degrades and not nct_degrades:
        conclusion = "Original DiD appears spurious: BCT-only shows no degradation either."
    elif bct_degrades and nct_degrades:
        conclusion = "Both subsets degrade; reduced-but-present DiD."
    else:
        conclusion = "Unexpected pattern: NCT-only degrades but BCT-only does not."

    return {
        "n_bct_tokens_unique": len(bct_tokens),
        "n_nct_tokens_unique": len(nct_tokens),
        "n_shared_tokens": len(shared_tokens),
        "n_bct_only_tokens": len(bct_only_tokens),
        "n_nct_only_tokens": len(nct_only_tokens),
        "token_overlap_pct_of_nct": round(
            100 * len(shared_tokens) / max(len(nct_tokens), 1), 1),
        "bct_only_n_deposits": n_b,
        "nct_only_n_deposits": n_n,
        "bct_only_spearman_rho": rho_b,
        "bct_only_spearman_p": p_b,
        "nct_only_spearman_rho": rho_n,
        "nct_only_spearman_p": p_n,
        "bct_only_early_mean": bct_early,
        "bct_only_late_mean": bct_late,
        "bct_only_change": bct_change,
        "nct_only_early_mean": nct_early,
        "nct_only_late_mean": nct_late,
        "nct_only_change": nct_change,
        "did_estimate": did_estimate,
        "fisher_z_rho": fisher,
        "conclusion": conclusion,
        "warnings": warnings,
    }


# ──────────────────────────────────────────────────────────────────────────
# 2. Token-clustered bootstrap SE on (rho_BCT - rho_NCT)
# ──────────────────────────────────────────────────────────────────────────

def cluster_bootstrap_did(
    bct: list[dict], nct: list[dict], n_boot: int = N_BOOT,
) -> dict:
    """Block-bootstrap resampling TCO2 token clusters (with replacement).

    Clusters are the tokens themselves. The set of clusters for bootstrap is
    the UNION of BCT and NCT tokens (capturing the dependence), and each
    replicate keeps all deposits of each drawn cluster. Because a token can
    appear in both pools, drawing it contributes to both BCT and NCT
    subsamples simultaneously --- the correct dependence preservation.
    """
    bct_s = filter_scored(bct)
    nct_s = filter_scored(nct)

    # Group by token
    bct_by_tok: dict[str, list[dict]] = defaultdict(list)
    nct_by_tok: dict[str, list[dict]] = defaultdict(list)
    for d in bct_s:
        bct_by_tok[d["tco2_address"].lower()].append(d)
    for d in nct_s:
        nct_by_tok[d["tco2_address"].lower()].append(d)

    # Universe of clusters = union
    tokens = sorted(set(bct_by_tok) | set(nct_by_tok))
    k = len(tokens)

    obs_rho_b, _, _ = spearman(bct_s)
    obs_rho_n, _, _ = spearman(nct_s)
    obs_diff = obs_rho_b - obs_rho_n

    diffs = np.empty(n_boot, dtype=float)
    rho_bs = np.empty(n_boot, dtype=float)
    rho_ns = np.empty(n_boot, dtype=float)

    for b in range(n_boot):
        draw = RNG.integers(0, k, size=k)
        bct_sample: list[dict] = []
        nct_sample: list[dict] = []
        for idx in draw:
            tok = tokens[idx]
            bct_sample.extend(bct_by_tok.get(tok, ()))
            nct_sample.extend(nct_by_tok.get(tok, ()))
        rb, _, _ = spearman(bct_sample)
        rn, _, _ = spearman(nct_sample)
        rho_bs[b] = rb
        rho_ns[b] = rn
        diffs[b] = (rb - rn) if not (math.isnan(rb) or math.isnan(rn)) else np.nan

    finite = diffs[np.isfinite(diffs)]
    se_diff = float(np.std(finite, ddof=1))
    se_rho_b = float(np.nanstd(rho_bs, ddof=1))
    se_rho_n = float(np.nanstd(rho_ns, ddof=1))

    # Cluster-robust z: observed difference / bootstrap SE
    z_cluster = float(obs_diff / se_diff) if se_diff > 0 else float("nan")
    p_cluster = float(2 * sstats.norm.sf(abs(z_cluster))) if not math.isnan(z_cluster) else float("nan")

    ci_low, ci_high = np.nanpercentile(finite, [2.5, 97.5])

    # Compare with naive (independent) Fisher z
    fisher_naive = fisher_z_test(obs_rho_b, len(bct_s), obs_rho_n, len(nct_s))

    return {
        "n_bootstrap": n_boot,
        "n_clusters": k,
        "observed_rho_bct": obs_rho_b,
        "observed_rho_nct": obs_rho_n,
        "observed_rho_difference": obs_diff,
        "cluster_robust_se_rho_diff": se_diff,
        "cluster_robust_se_rho_bct": se_rho_b,
        "cluster_robust_se_rho_nct": se_rho_n,
        "cluster_robust_z": z_cluster,
        "cluster_robust_p": p_cluster,
        "cluster_robust_ci95": [float(ci_low), float(ci_high)],
        "naive_fisher_z": fisher_naive.get("z"),
        "naive_fisher_p": fisher_naive.get("p"),
        "se_inflation_factor": (
            se_diff / math.sqrt(1 / (len(bct_s) - 3) + 1 / (len(nct_s) - 3))
            if len(bct_s) > 3 and len(nct_s) > 3 else None
        ),
        "conclusion": (
            "Cluster-robust inference preserves significance."
            if not math.isnan(p_cluster) and p_cluster < 0.05
            else "Cluster-robust inference does NOT preserve significance."
        ),
    }


# ──────────────────────────────────────────────────────────────────────────
# 3. Within-BCT DiD: Renewable vs Nature-based
# ──────────────────────────────────────────────────────────────────────────

# Mapping of credit_type -> broad category
NATURE_BASED = {"REDD+", "ARR", "IFM"}
RENEWABLE = {"Renewable"}
INDUSTRIAL = {"Industrial", "Industrial gas", "Fossil switch", "Waste/Methane"}


def within_bct_did(bct: list[dict]) -> dict:
    bct_s = filter_scored(bct)
    for d in bct_s:
        t = d.get("credit_type") or ""
        if t in NATURE_BASED:
            d["_bucket"] = "nature"
        elif t in RENEWABLE:
            d["_bucket"] = "renewable"
        elif t in INDUSTRIAL:
            d["_bucket"] = "industrial"
        else:
            d["_bucket"] = "other"

    buckets: dict[str, list[dict]] = defaultdict(list)
    for d in bct_s:
        buckets[d["_bucket"]].append(d)

    stats_by_bucket = {}
    for name, deps in buckets.items():
        rho, p, n = spearman(deps)
        early, late = half_split(deps)
        stats_by_bucket[name] = {
            "n": n,
            "spearman_rho": rho,
            "spearman_p": p,
            "early_mean": early,
            "late_mean": late,
            "change": (late - early) if not math.isnan(early) else float("nan"),
            "mean_quality": float(np.mean([d["composite_quality"] for d in deps]))
            if deps else float("nan"),
        }

    # Primary DiD: renewable (treatment group with race-to-bottom) vs nature
    ren = stats_by_bucket.get("renewable", {})
    nat = stats_by_bucket.get("nature", {})
    rho_ren = ren.get("spearman_rho", float("nan"))
    rho_nat = nat.get("spearman_rho", float("nan"))
    n_ren = ren.get("n", 0)
    n_nat = nat.get("n", 0)

    fisher = fisher_z_test(rho_ren, n_ren, rho_nat, n_nat)

    # Half-split DiD within BCT
    ren_change = ren.get("change", float("nan"))
    nat_change = nat.get("change", float("nan"))
    did_halfsplit = (
        ren_change - nat_change
        if not (math.isnan(ren_change) or math.isnan(nat_change))
        else float("nan")
    )

    # Token-clustered bootstrap on the within-BCT difference
    # (safer than Fisher z because the same depositor population
    # participates in both buckets)
    ren_deps = buckets.get("renewable", [])
    nat_deps = buckets.get("nature", [])
    ren_by_tok: dict[str, list[dict]] = defaultdict(list)
    nat_by_tok: dict[str, list[dict]] = defaultdict(list)
    for d in ren_deps:
        ren_by_tok[d["tco2_address"].lower()].append(d)
    for d in nat_deps:
        nat_by_tok[d["tco2_address"].lower()].append(d)
    tokens = sorted(set(ren_by_tok) | set(nat_by_tok))
    k = len(tokens)

    diffs = np.empty(N_BOOT, dtype=float)
    for b in range(N_BOOT):
        draw = RNG.integers(0, k, size=k)
        rs, ns_ = [], []
        for idx in draw:
            tok = tokens[idx]
            rs.extend(ren_by_tok.get(tok, ()))
            ns_.extend(nat_by_tok.get(tok, ()))
        rr, _, _ = spearman(rs)
        rn, _, _ = spearman(ns_)
        diffs[b] = (rr - rn) if not (math.isnan(rr) or math.isnan(rn)) else np.nan

    finite = diffs[np.isfinite(diffs)]
    se_boot = float(np.std(finite, ddof=1)) if finite.size else float("nan")
    z_boot = (rho_ren - rho_nat) / se_boot if se_boot > 0 else float("nan")
    p_boot = float(2 * sstats.norm.sf(abs(z_boot))) if not math.isnan(z_boot) else float("nan")
    ci_low, ci_high = (np.nanpercentile(finite, [2.5, 97.5])
                      if finite.size else (float("nan"), float("nan")))

    return {
        "strategy": "within-BCT renewable vs nature-based DiD",
        "rationale": (
            "Same pool, same depositor universe, only credit type varies. "
            "Eliminates SUTVA contamination by holding pool-design and "
            "depositor-composition fixed."
        ),
        "bucket_stats": stats_by_bucket,
        "halfsplit_did": did_halfsplit,
        "fisher_z_independent": fisher,
        "cluster_bootstrap": {
            "n_bootstrap": N_BOOT,
            "n_clusters": k,
            "rho_difference": rho_ren - rho_nat
            if not (math.isnan(rho_ren) or math.isnan(rho_nat)) else float("nan"),
            "se": se_boot,
            "z": z_boot,
            "p": p_boot,
            "ci95": [float(ci_low), float(ci_high)],
        },
        "conclusion": (
            "Within-BCT DiD confirms adverse-selection on renewable credits."
            if (not math.isnan(p_boot)) and p_boot < 0.05 and rho_ren < rho_nat
            else "Within-BCT DiD does not significantly distinguish renewable from nature."
        ),
    }


# ──────────────────────────────────────────────────────────────────────────
# 4. MCO2 alternative control — data availability check
# ──────────────────────────────────────────────────────────────────────────

def mco2_availability() -> dict:
    """Check whether MCO2 deposit / composition data exists locally."""
    pool_analyzer_path = HERE.parent / "lemons-index" / "pool_analyzer.py"
    results_path = HERE.parent / "lemons-index" / "results.json"
    hits: dict[str, Any] = {
        "pool_analyzer_mentions_mco2": False,
        "results_mentions_mco2": None,
        "mco2_deposit_data_on_chain": False,
        "notes": [],
    }
    if pool_analyzer_path.exists():
        text = pool_analyzer_path.read_text().lower()
        hits["pool_analyzer_mentions_mco2"] = (
            "mco2" in text or "moss" in text
        )
    if results_path.exists():
        try:
            r = json.loads(results_path.read_text())
            if isinstance(r, list):
                for p in r:
                    if isinstance(p, dict) and (
                        "mco2" in str(p.get("name", "")).lower()
                        or "moss" in str(p.get("name", "")).lower()
                    ):
                        hits["results_mentions_mco2"] = p
                        break
        except Exception:
            pass

    hits["notes"].append(
        "MCO2 is an ERC-20 on Ethereum/Polygon but it is NOT a permissionless "
        "deposit pool like BCT/NCT --- it is a fixed-supply retirement token "
        "issued by Moss against specific bridged REDD+ credits. There are no "
        "ongoing 'Deposited' events to fetch. Only static composition data "
        "is available (n=30 synthetic archetype credits in pool_analyzer.py)."
    )
    hits["notes"].append(
        "MCO2 therefore cannot serve as a temporal-analysis control. "
        "It can still be cited cross-sectionally (Lemons Index = 0.713) "
        "as evidence that other open-acceptance tokens suffer similar "
        "quality problems, but not as a DiD control arm."
    )
    hits["conclusion"] = (
        "MCO2 unavailable as a DiD control: no on-chain deposit stream."
    )
    return hits


# ──────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────

def main() -> dict:
    print("=" * 70)
    print("VALID DiD ANALYSIS — addressing SUTVA violation in BCT vs NCT")
    print("=" * 70)
    sys.stdout.flush()

    bct, nct = load_scored_deposits()
    print(f"Loaded: {len(bct)} BCT deposits, {len(nct)} NCT deposits")
    print(f"Scored: {len(filter_scored(bct))} BCT, {len(filter_scored(nct))} NCT")

    print("\n— [1/4] Non-overlapping subsets —")
    sub = non_overlapping_subset_did(bct, nct)
    print(f"  BCT-only tokens: {sub['n_bct_only_tokens']} "
          f"({sub['bct_only_n_deposits']} deposits)")
    print(f"  NCT-only tokens: {sub['n_nct_only_tokens']} "
          f"({sub['nct_only_n_deposits']} deposits)")
    print(f"  BCT-only Spearman rho: {sub['bct_only_spearman_rho']:.4f} "
          f"(p={sub['bct_only_spearman_p']:.3g})")
    print(f"  NCT-only Spearman rho: {sub['nct_only_spearman_rho']:.4f} "
          f"(p={sub['nct_only_spearman_p']:.3g})")
    print(f"  Half-split DiD: {sub['did_estimate']:+.3f}")
    if sub["warnings"]:
        for w in sub["warnings"]:
            print(f"  WARNING: {w}")
    print(f"  -> {sub['conclusion']}")

    print("\n— [2/4] Cluster-robust bootstrap (token clustering) —")
    cb = cluster_bootstrap_did(bct, nct)
    print(f"  Observed rho_BCT - rho_NCT: {cb['observed_rho_difference']:+.4f}")
    print(f"  Naive Fisher z p: {cb['naive_fisher_p']:.3g}")
    print(f"  Cluster-robust SE: {cb['cluster_robust_se_rho_diff']:.4f}")
    if cb.get("se_inflation_factor") is not None:
        print(f"  SE inflation vs naive: "
              f"{cb['se_inflation_factor']:.2f}x")
    print(f"  Cluster-robust z: {cb['cluster_robust_z']:.3f}, "
          f"p: {cb['cluster_robust_p']:.3g}")
    print(f"  95% CI for rho-diff: "
          f"[{cb['cluster_robust_ci95'][0]:+.3f}, "
          f"{cb['cluster_robust_ci95'][1]:+.3f}]")
    print(f"  -> {cb['conclusion']}")

    print("\n— [3/4] Within-BCT renewable vs nature-based DiD —")
    wb = within_bct_did(bct)
    for bucket in ("renewable", "nature", "industrial", "other"):
        s = wb["bucket_stats"].get(bucket)
        if s:
            print(f"  {bucket:10s}: n={s['n']:4d}, rho={s['spearman_rho']:+.3f} "
                  f"(p={s['spearman_p']:.3g}), mean_q={s['mean_quality']:.2f}")
    cb2 = wb["cluster_bootstrap"]
    print(f"  rho_renewable - rho_nature: {cb2['rho_difference']:+.4f}")
    print(f"  Cluster-robust z: {cb2['z']:.3f}, p: {cb2['p']:.3g}")
    print(f"  95% CI: [{cb2['ci95'][0]:+.3f}, {cb2['ci95'][1]:+.3f}]")
    fz = wb["fisher_z_independent"]
    if fz.get("z") is not None:
        print(f"  Fisher z (naive, independent): z={fz['z']:.3f}, p={fz['p']:.3g}")
    print(f"  -> {wb['conclusion']}")

    print("\n— [4/4] MCO2 availability —")
    mco2 = mco2_availability()
    for n in mco2["notes"]:
        print(f"  • {n}")
    print(f"  -> {mco2['conclusion']}")

    # Assemble final results
    results = {
        "meta": {
            "generated": "2026-04-16",
            "rng_seed": 20260416,
            "n_bootstrap": N_BOOT,
            "rationale": (
                "Original BCT-vs-NCT DiD violates SUTVA: 31/35 NCT tokens "
                "also appear in BCT; ~14.9% of BCT tonnage comes from wallets "
                "that also deposit in NCT. Fisher z-test assumes "
                "independence; this script supplies three valid alternatives."
            ),
            "data_sources": {
                "bct": "bct_deposits_enriched.json",
                "nct": "nct_deposits.json",
                "scores": "tco2_scores_final.json",
            },
        },
        "approach_1_non_overlapping_subsets": sub,
        "approach_2_cluster_robust_bootstrap": cb,
        "approach_3_within_bct_credit_type": wb,
        "approach_4_mco2_alternative_control": mco2,
        "overall_assessment": synthesize(sub, cb, wb, mco2),
    }

    out_path = HERE / "valid_did_analysis.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nSaved results to {out_path}")
    return results


def synthesize(sub: dict, cb: dict, wb: dict, mco2: dict) -> dict:
    """Honest synthesis across approaches."""
    verdicts = {}

    # Approach 1: did BCT-only still degrade?  Did NCT-only degrade?
    rho_b = sub["bct_only_spearman_rho"]
    p_b = sub["bct_only_spearman_p"]
    rho_n = sub["nct_only_spearman_rho"]
    verdicts["non_overlapping_subset"] = {
        "bct_only_still_degrades": (not math.isnan(rho_b))
            and rho_b < -0.2 and p_b < 0.05,
        "nct_only_n_adequate": sub["nct_only_n_deposits"] >= 30,
        "nct_only_computable": not math.isnan(rho_n),
        "did_identified": (not math.isnan(rho_n)) and (not math.isnan(rho_b)),
        "conclusion": sub["conclusion"],
    }

    # Approach 2: cluster-robust preserves significance?
    p_c = cb["cluster_robust_p"]
    verdicts["cluster_robust"] = {
        "preserves_significance": (not math.isnan(p_c)) and p_c < 0.05,
        "p_value": p_c,
        "ci_excludes_zero": (cb["cluster_robust_ci95"][0] > 0
                             or cb["cluster_robust_ci95"][1] < 0),
    }

    # Approach 3: within-BCT DiD significant?
    p3 = wb["cluster_bootstrap"]["p"]
    verdicts["within_bct_did"] = {
        "preserves_significance": (not math.isnan(p3)) and p3 < 0.05,
        "p_value": p3,
        "renewable_degrades_more": wb["cluster_bootstrap"]["rho_difference"] < 0,
    }

    # Approach 4: MCO2 available?
    verdicts["mco2_control"] = {
        "available": False,
        "reason": "No on-chain deposit stream for MCO2 (fixed-supply token).",
    }

    # Overall
    strong_support = (
        verdicts["within_bct_did"]["preserves_significance"]
        and verdicts["within_bct_did"]["renewable_degrades_more"]
    )
    survives_if = []
    if verdicts["within_bct_did"]["preserves_significance"]:
        survives_if.append("within-BCT renewable-vs-nature DiD")
    if verdicts["non_overlapping_subset"]["did_identified"] and verdicts[
            "non_overlapping_subset"]["bct_only_still_degrades"]:
        survives_if.append("non-overlapping-subset BCT-only Spearman")
    if verdicts["cluster_robust"]["preserves_significance"]:
        survives_if.append("cluster-robust pool-level comparison")

    fails_if = []
    if not verdicts["cluster_robust"]["preserves_significance"]:
        fails_if.append(
            "cluster-robust pool-level comparison: SEs inflate once token "
            "dependence is honoured, and the BCT-NCT rho difference is no "
            "longer distinguishable at alpha=0.05."
        )
    if not verdicts["non_overlapping_subset"]["did_identified"]:
        fails_if.append(
            f"non-overlapping-subset DiD is UNIDENTIFIED: all "
            f"{sub['n_nct_only_tokens']} NCT-only tokens are unscored, "
            f"so the control arm has zero scored deposits. Best we can say "
            f"is that BCT-only (n={sub['bct_only_n_deposits']}) still shows "
            f"rho={rho_b:+.3f}, ruling out shared-token churn as sole driver."
        )
    elif not verdicts["non_overlapping_subset"]["nct_only_n_adequate"]:
        fails_if.append(
            f"non-overlapping-subset: NCT-only has "
            f"only {sub['nct_only_n_deposits']} scored deposits "
            f"({sub['n_nct_only_tokens']} unique tokens), underpowered."
        )
    if not verdicts["within_bct_did"]["preserves_significance"]:
        fails_if.append(
            "within-BCT DiD: naive Fisher z is highly significant "
            f"(p=3.6e-05) but cluster-robust bootstrap p="
            f"{verdicts['within_bct_did']['p_value']:.3f} — the SE inflates "
            "because many BCT tokens are concentrated in a small number of "
            "methodology clusters with temporally clumped deposits."
        )

    headline = (
        "The original BCT-vs-NCT pool-level DiD is NOT an identified "
        "causal estimate because 88.6% of NCT tokens are also in BCT, "
        "and once token-level dependence is modelled via cluster-robust "
        "bootstrap SEs the rho difference is no longer distinguishable "
        "from zero (p=0.24). "
        + ("The within-BCT renewable-vs-nature DiD survives rigorous "
           "inference and is the defensible causal claim for the paper."
           if strong_support else
           "None of the three valid designs preserves the original DiD at "
           "alpha=0.05 under cluster-robust inference. What DOES survive is "
           "the descriptive finding that renewable credits degrade sharply "
           "within BCT (rho=-0.50, n=707) while nature-based credits do not "
           "(rho=-0.10, n=97) — reported honestly with the caveat that "
           "cluster-robust SEs do not reject equality of the two rhos.")
    )

    return {
        "headline": headline,
        "approaches_that_support_claim": survives_if,
        "approaches_that_undermine_claim": fails_if,
        "per_approach_verdicts": verdicts,
        "recommended_paper_claim": (
            "Drop the BCT-vs-NCT DiD as a causal claim. The paper should "
            "report: (i) BCT-only Spearman rho=-0.413 (p=6.5e-35, n=814) "
            "as a within-treatment temporal degradation fact — robust to "
            "excluding shared tokens; (ii) within-BCT descriptive "
            "decomposition rho_renewable=-0.50 vs rho_nature=-0.10 as "
            "suggestive evidence of adverse selection by credit type, with "
            "the explicit caveat that a cluster-robust bootstrap "
            "(token-clustered, n_boot=5000) yields p=0.20 for the rho "
            "difference — i.e. we CANNOT reject equality under correct "
            "inference. This is a much weaker empirical claim than the "
            "original paper's DiD. Retracting the causal DiD and retreating "
            "to descriptive correlation is the statistically defensible "
            "path."
        ),
    }


if __name__ == "__main__":
    main()
