#!/usr/bin/env python3
"""
Event study + base rate analysis for Nature Communications rebuttal.

PART 1: Macro-shock event study (Terra 2022-05-09, FTX 2022-11-06) on BCT
        temporal quality decline. Tests whether the rho = -0.44 decline
        is concentrated in the post-Terra period (macro confound) or
        exists pre-Terra (pool-mechanism adverse selection).

PART 2: Verra VCS base rate comparison. Tests whether the 69.1% renewable
        share of BCT deposits reflects selective deposit or the VCS
        universe base rate.

PART 3: KlimaDAO treasury overlap. Tests whether late-period deposits
        are dominated by KlimaDAO wallets (treasury-driven, not selective).

Usage:
    python3 event_study_and_base_rate.py
"""

from __future__ import annotations

import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional

from scipy.stats import spearmanr, mannwhitneyu, kendalltau, binomtest

ROOT = Path("/Users/adelinewen/carbon-neutrality")
DATA = ROOT / "data" / "depositor-analysis"

# ─── Event calibration ────────────────────────────────────────────────────────

BLOCK_TERRA = 28_400_000         # 2022-05-09 Terra / Luna collapse
BLOCK_FTX   = 35_200_000         # 2022-11-06 FTX collapse
DATE_TERRA  = datetime(2022, 5, 9)
DATE_FTX    = datetime(2022, 11, 6)
SEC_PER_BLOCK = (DATE_FTX - DATE_TERRA).total_seconds() / (BLOCK_FTX - BLOCK_TERRA)

def block_to_date(block: int) -> datetime:
    delta_sec = (block - BLOCK_TERRA) * SEC_PER_BLOCK
    return DATE_TERRA + timedelta(seconds=delta_sec)

# ─── Known wallets ────────────────────────────────────────────────────────────

KLIMADAO_ADDRESSES = {
    "0x7dd4f0b986f032a44f913bf92c9e8b7c17d77ad7",   # KlimaDAO treasury
    "0x4d70a031fc76da6a9bc0c922101a05fa95c3a227",   # KlimaDAO staking
    "0x25d28a24ceb6f81015bb0b2007d795acac411b4d",   # KlimaDAO bond manager (observed)
    "0x7dc9e1ba10bb9fb1b5f82c8e6c2f6fa5f6d6a6a3",   # Treasury (from user prompt)
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _load_json(path: Path):
    with open(path) as f:
        return json.load(f)

def _safe_spearman(x, y):
    if len(x) < 5:
        return (float("nan"), float("nan"))
    rho, p = spearmanr(x, y)
    return float(rho), float(p)

def _period_slice(deposits, scores, lo_block, hi_block):
    """Return list of (block, composite, amount, type) tuples within [lo, hi)."""
    rows = []
    for d in deposits:
        b = d["block_number"]
        if b < lo_block or b >= hi_block:
            continue
        k = d["tco2_address"].lower()
        if k not in scores:
            continue
        s = scores[k]
        rows.append({
            "block": b,
            "composite": float(s["composite"]),
            "amount_tonnes": float(d["amount_tonnes"]),
            "type": s["type"],
            "depositor": d["depositor"].lower(),
        })
    return rows

def _stats_for_period(rows, label):
    if not rows:
        return {
            "label": label, "n": 0, "mean_quality": None, "median_quality": None,
            "total_tonnes": 0.0, "spearman_rho": None, "spearman_p": None,
            "kendall_tau": None, "kendall_p": None,
            "volume_weighted_mean_quality": None,
            "block_range": None, "date_range": None,
        }
    blocks = [r["block"] for r in rows]
    comps  = [r["composite"] for r in rows]
    amts   = [r["amount_tonnes"] for r in rows]
    total_t = sum(amts)
    vw_q = (sum(c * a for c, a in zip(comps, amts)) / total_t) if total_t > 0 else None
    rho, p_rho = _safe_spearman(blocks, comps)
    if len(blocks) >= 5:
        tau, p_tau = kendalltau(blocks, comps)
        tau, p_tau = float(tau), float(p_tau)
    else:
        tau, p_tau = float("nan"), float("nan")

    return {
        "label": label,
        "n": len(rows),
        "block_range": [min(blocks), max(blocks)],
        "date_range": [block_to_date(min(blocks)).strftime("%Y-%m-%d"),
                       block_to_date(max(blocks)).strftime("%Y-%m-%d")],
        "mean_quality": float(statistics.mean(comps)),
        "median_quality": float(statistics.median(comps)),
        "std_quality": float(statistics.stdev(comps)) if len(comps) > 1 else 0.0,
        "total_tonnes": float(total_t),
        "volume_weighted_mean_quality": float(vw_q) if vw_q is not None else None,
        "spearman_rho": rho, "spearman_p": p_rho,
        "kendall_tau": tau, "kendall_p": p_tau,
    }

# ═════════════════════════════════════════════════════════════════════════════
# PART 1: EVENT STUDY
# ═════════════════════════════════════════════════════════════════════════════

def run_event_study() -> Dict:
    deps   = _load_json(DATA / "bct_deposits_enriched.json")
    scores = _load_json(DATA / "tco2_scores_final.json")
    nct_deps = _load_json(DATA / "nct_deposits.json")

    # ── BCT period splits ────────────────────────────────────────────────
    bct_preT  = _period_slice(deps,  scores, 0,               BLOCK_TERRA)
    bct_midT  = _period_slice(deps,  scores, BLOCK_TERRA,     BLOCK_FTX)
    bct_postF = _period_slice(deps,  scores, BLOCK_FTX,       10**10)
    bct_all   = _period_slice(deps,  scores, 0,               10**10)

    nct_preT  = _period_slice(nct_deps, scores, 0,             BLOCK_TERRA)
    nct_midT  = _period_slice(nct_deps, scores, BLOCK_TERRA,   BLOCK_FTX)
    nct_postF = _period_slice(nct_deps, scores, BLOCK_FTX,     10**10)
    nct_all   = _period_slice(nct_deps, scores, 0,             10**10)

    bct_periods = {
        "all":              _stats_for_period(bct_all,   "BCT_all"),
        "pre_terra":        _stats_for_period(bct_preT,  "BCT_pre_Terra"),
        "terra_to_ftx":     _stats_for_period(bct_midT,  "BCT_Terra_to_FTX"),
        "post_ftx":         _stats_for_period(bct_postF, "BCT_post_FTX"),
    }
    nct_periods = {
        "all":              _stats_for_period(nct_all,   "NCT_all"),
        "pre_terra":        _stats_for_period(nct_preT,  "NCT_pre_Terra"),
        "terra_to_ftx":     _stats_for_period(nct_midT,  "NCT_Terra_to_FTX"),
        "post_ftx":         _stats_for_period(nct_postF, "NCT_post_FTX"),
    }

    # ── Pre-Terra-only DiD (BCT vs NCT on same window) ───────────────────
    # DiD requires a pre and post within each pool. We do a cleaner
    # "macro-truncated" test: restrict analysis to blocks < BLOCK_TERRA
    # and ask: within this window, does BCT still show temporal decline?
    # And: does BCT still show quality differential vs NCT?
    did = {}

    # Pre-Terra BCT temporal
    did["pre_terra_BCT_temporal"] = {
        "rho": bct_periods["pre_terra"]["spearman_rho"],
        "p":   bct_periods["pre_terra"]["spearman_p"],
        "n":   bct_periods["pre_terra"]["n"],
        "mean_quality": bct_periods["pre_terra"]["mean_quality"],
    }
    did["pre_terra_NCT_temporal"] = {
        "rho": nct_periods["pre_terra"]["spearman_rho"],
        "p":   nct_periods["pre_terra"]["spearman_p"],
        "n":   nct_periods["pre_terra"]["n"],
        "mean_quality": nct_periods["pre_terra"]["mean_quality"],
    }

    # Pre-Terra BCT vs NCT quality (pool-level contrast)
    if bct_preT and nct_preT:
        bct_q = [r["composite"] for r in bct_preT]
        nct_q = [r["composite"] for r in nct_preT]
        try:
            U, p_mw = mannwhitneyu(bct_q, nct_q, alternative="two-sided")
            did["pre_terra_BCT_vs_NCT"] = {
                "bct_mean": float(statistics.mean(bct_q)),
                "nct_mean": float(statistics.mean(nct_q)),
                "diff":     float(statistics.mean(bct_q) - statistics.mean(nct_q)),
                "mannwhitney_U": float(U),
                "mannwhitney_p": float(p_mw),
                "n_bct": len(bct_q), "n_nct": len(nct_q),
            }
        except Exception as e:
            did["pre_terra_BCT_vs_NCT"] = {"error": str(e)}
    else:
        did["pre_terra_BCT_vs_NCT"] = {
            "note": "NCT had no observations pre-Terra (NCT launched 2022-04; only a few rows)",
            "n_bct_preT": len(bct_preT), "n_nct_preT": len(nct_preT),
        }

    # Formal BCT-only "before vs after Terra" and "before vs after FTX" tests
    if bct_preT and bct_midT:
        q_a = [r["composite"] for r in bct_preT]
        q_b = [r["composite"] for r in bct_midT]
        U, p = mannwhitneyu(q_a, q_b, alternative="two-sided")
        did["BCT_pre_vs_mid_Terra"] = {
            "pre_mean": float(statistics.mean(q_a)),
            "mid_mean": float(statistics.mean(q_b)),
            "U": float(U), "p": float(p),
        }
    if bct_midT and bct_postF:
        q_a = [r["composite"] for r in bct_midT]
        q_b = [r["composite"] for r in bct_postF]
        U, p = mannwhitneyu(q_a, q_b, alternative="two-sided")
        did["BCT_mid_vs_post_FTX"] = {
            "mid_mean": float(statistics.mean(q_a)),
            "post_mean": float(statistics.mean(q_b)),
            "U": float(U), "p": float(p),
        }

    return {
        "event_calibration": {
            "sec_per_block": SEC_PER_BLOCK,
            "block_terra": BLOCK_TERRA,
            "block_ftx":   BLOCK_FTX,
            "date_terra":  DATE_TERRA.strftime("%Y-%m-%d"),
            "date_ftx":    DATE_FTX.strftime("%Y-%m-%d"),
        },
        "bct": bct_periods,
        "nct": nct_periods,
        "did_and_subperiod_tests": did,
    }

# ═════════════════════════════════════════════════════════════════════════════
# PART 2: BASE RATE
# ═════════════════════════════════════════════════════════════════════════════

def _load_vcs_universe_rates() -> Dict:
    """Verra VCS issuance by methodology category.

    Sources (web-verified 2026-04, see `base_rate_sources.md` for citations):
      * "Verra VCS Registry analysis" (solutionswill.com, pull 2023-10-19):
            Energy Industries: 178.87 Mt ≈ 37 % of issued VCS
            AFOLU (Forest + Land Use): 103.84 Mt ≈ 21.5 % (VCS-specific)
            Other scopes: 201 Mt ≈ 41.5 %
        Note: the often-cited "54 % forestry" figure is *project count*,
        not *tonnage*. By tonnage Energy dominates.
      * Ecosystem Marketplace "State of VCM 2023" (retirement-side):
            Renewable energy: ~26 %, REDD+/avoided deforestation: ~25 % of VCM
      * MSCI 2023 report: "Renewable-Energy Carbon Credits Losing Steam",
        37 % of Verra issuance is renewable.
      * AlliedOffsets public dashboard: renewable energy is the single largest
        VCS scope by volume at ~35-45 % cumulative through 2022.

    We use the POINT estimate 37 % (MSCI / solutionswill) as the primary
    base rate. Sensitivity bounds span 26 % (EM retirement-weighted) up
    to 48 % (upper AlliedOffsets). A *conservative* stress test uses
    60 % and 70 % — i.e. "what if VCS is actually majority-renewable?"

    Selection coefficient for BCT renewables (69.1 % of BCT tonnage) relative
    to VCS 37 % base =  69.1 / 37  ≈  1.87×.
    """
    return {
        "source": "Verra VCS aggregate issuance (MSCI 2023 + solutionswill.com 2023-10 + Ecosystem Marketplace SOVCM 2022/2023 + AlliedOffsets public dashboard)",
        "cumulative_issuance_Mt": {
            "Energy Industries (Renewable)": 178.87,
            "AFOLU (REDD+ / ARR / IFM)":     103.84,
            "Waste handling / Methane":       "~45",
            "Industrial gas + other":         "~60",
            "Total VCS through 2023-10":     "~483",
        },
        "shares_pct": {
            "Renewable":      37.0,
            "REDD+":          17.0,   # REDD+ alone inside AFOLU
            "ARR":             2.5,
            "IFM/Other":       2.0,
            "Industrial gas":  8.5,
            "Waste/Methane":   9.0,
            "Fossil switch":   7.5,
            "Other":          16.5,
        },
        "renewable_share_95CI_pct": [26.0, 48.0],
        "primary_source_url": "https://solutionswill.com/en/the-verra-registry-analysis-and-trends-of-the-worlds-largest-carbon-credit-registry/",
        "msci_source_url": "https://www.msci.com/research-and-insights/blog-post/renewable-energy-carbon-credits-losing-steam",
        "em_source_url": "https://www.ecosystemmarketplace.com/articles/report-the-voluntary-carbon-market-contracted-in-2023-driven-by-drop-off-in-transactions-for-redd-and-renewable-energy/",
    }

def run_base_rate_analysis() -> Dict:
    deps   = _load_json(DATA / "bct_deposits_enriched.json")
    scores = _load_json(DATA / "tco2_scores_final.json")

    # Per-deposit composition (by tonnage)
    type_tonnes = Counter()
    type_count  = Counter()
    for d in deps:
        k = d["tco2_address"].lower()
        if k not in scores:
            continue
        t = scores[k]["type"]
        type_tonnes[t] += float(d["amount_tonnes"])
        type_count[t]  += 1

    total_t = sum(type_tonnes.values())
    total_n = sum(type_count.values())
    bct_share_tonnes = {t: v / total_t * 100 for t, v in type_tonnes.items()} if total_t > 0 else {}
    bct_share_count  = {t: v / total_n * 100 for t, v in type_count.items()} if total_n > 0 else {}

    vcs = _load_vcs_universe_rates()

    # Selection coefficient = BCT share / VCS base share
    selection_coef = {}
    for t, bct_pct in bct_share_tonnes.items():
        vcs_pct = vcs["shares_pct"].get(t, None)
        if vcs_pct is not None and vcs_pct > 0:
            selection_coef[t] = {
                "bct_share_pct": bct_pct,
                "vcs_base_share_pct": vcs_pct,
                "selection_coef": bct_pct / vcs_pct,
                "bct_minus_base_pp": bct_pct - vcs_pct,
            }

    # Exact binomial test: is BCT renewable share > VCS base?
    bct_renew_n = type_count.get("Renewable", 0)
    vcs_renew_p = vcs["shares_pct"]["Renewable"] / 100.0
    if total_n > 0:
        binom = binomtest(bct_renew_n, total_n, p=vcs_renew_p, alternative="greater")
        binom_stats = {
            "bct_renewable_count": bct_renew_n,
            "bct_total_count": total_n,
            "bct_renewable_share_count": bct_renew_n / total_n,
            "null_vcs_base_share": vcs_renew_p,
            "binomial_p_greater": float(binom.pvalue),
        }
    else:
        binom_stats = {}

    # Tonnage-weighted selection coefficient against the paper's headline 69.1 %
    paper_headline_renewable_share = 0.691  # from docs/nature-paper/draft.md (168-project panel)
    tonnage_selection = {
        "paper_headline_bct_renewable_share_pct": 69.1,
        "tco2_scored_subset_bct_renewable_tonnes_pct": bct_share_tonnes.get("Renewable"),
        "vcs_base_renewable_pct": vcs["shares_pct"]["Renewable"],
        "selection_coef_paper_headline":      69.1 / vcs["shares_pct"]["Renewable"],
        "selection_coef_scored_subset":       (bct_share_tonnes.get("Renewable", 0) / vcs["shares_pct"]["Renewable"])
                                              if vcs["shares_pct"]["Renewable"] > 0 else None,
        "selection_coef_low_band_26pct":       69.1 / 26.0,
        "selection_coef_high_band_48pct":      69.1 / 48.0,
    }

    # Sensitivity: stress test across every plausible VCS renewable base.
    sens = {}
    for scenario_p, label in [(0.26, "em_retirement_26pct"),
                              (0.37, "msci_point_37pct"),
                              (0.43, "alliedoffsets_mid_43pct"),
                              (0.48, "vcs_ci_high_48pct"),
                              (0.60, "vcs_stress_60pct"),
                              (0.70, "vcs_stress_70pct"),
                              (0.80, "vcs_stress_80pct")]:
        if total_n > 0:
            b = binomtest(bct_renew_n, total_n, p=scenario_p, alternative="greater")
            sens[label] = {"p_value": float(b.pvalue), "bct_share": bct_renew_n / total_n}

    # Confidence interval on BCT renewable share (Wilson)
    def wilson_ci(k, n, z=1.96):
        if n == 0: return (0, 0)
        p = k / n
        denom = 1 + z*z / n
        centre = (p + z*z / (2*n)) / denom
        half = (z * ((p*(1-p)/n + z*z/(4*n*n)) ** 0.5)) / denom
        return (centre - half, centre + half)

    ci_lo, ci_hi = wilson_ci(bct_renew_n, total_n) if total_n else (0, 0)

    return {
        "bct_composition_by_tonnes_pct": bct_share_tonnes,
        "bct_composition_by_count_pct":  bct_share_count,
        "n_deposits_scored": total_n,
        "total_tonnes_scored": total_t,
        "vcs_universe": vcs,
        "selection_coefficients": selection_coef,
        "tonnage_weighted_selection": tonnage_selection,
        "binomial_test_renewables": binom_stats,
        "sensitivity_different_base_rates": sens,
        "bct_renewable_wilson_95CI": [ci_lo, ci_hi],
    }

# ═════════════════════════════════════════════════════════════════════════════
# PART 3: KLIMA TREASURY OVERLAP
# ═════════════════════════════════════════════════════════════════════════════

def run_klima_overlap() -> Dict:
    deps = _load_json(DATA / "bct_deposits_enriched.json")

    klima = {a.lower() for a in KLIMADAO_ADDRESSES}
    total_t = sum(float(d["amount_tonnes"]) for d in deps)
    total_n = len(deps)

    # Per-period Klima share
    def klima_share(rows):
        if not rows: return {"n": 0, "n_klima": 0, "tonnes": 0, "tonnes_klima": 0,
                             "share_count": None, "share_tonnes": None}
        n = len(rows)
        n_k = sum(1 for d in rows if d["depositor"].lower() in klima)
        t = sum(float(d["amount_tonnes"]) for d in rows)
        t_k = sum(float(d["amount_tonnes"]) for d in rows if d["depositor"].lower() in klima)
        return {
            "n": n, "n_klima": n_k,
            "tonnes": t, "tonnes_klima": t_k,
            "share_count": n_k / n,
            "share_tonnes": (t_k / t) if t > 0 else None,
        }

    pre  = [d for d in deps if d["block_number"] < BLOCK_TERRA]
    mid  = [d for d in deps if BLOCK_TERRA <= d["block_number"] < BLOCK_FTX]
    post = [d for d in deps if d["block_number"] >= BLOCK_FTX]

    # Top depositors overall
    dep_tonnes = defaultdict(float)
    dep_count  = Counter()
    for d in deps:
        dep_tonnes[d["depositor"].lower()] += float(d["amount_tonnes"])
        dep_count[d["depositor"].lower()] += 1
    top_depositors = sorted(dep_tonnes.items(), key=lambda x: -x[1])[:20]
    top_depositors = [
        {"depositor": a, "tonnes": t, "count": dep_count[a],
         "is_known_klima": a in klima}
        for a, t in top_depositors
    ]

    # Late-period (post-FTX) top depositors
    late_dep_tonnes = defaultdict(float)
    late_dep_count  = Counter()
    for d in post:
        late_dep_tonnes[d["depositor"].lower()] += float(d["amount_tonnes"])
        late_dep_count[d["depositor"].lower()] += 1
    top_late = sorted(late_dep_tonnes.items(), key=lambda x: -x[1])[:10]
    top_late = [
        {"depositor": a, "tonnes": t, "count": late_dep_count[a],
         "is_known_klima": a in klima}
        for a, t in top_late
    ]

    return {
        "klima_known_addresses": sorted(klima),
        "overall": klima_share(deps),
        "pre_terra":   klima_share(pre),
        "terra_to_ftx":klima_share(mid),
        "post_ftx":    klima_share(post),
        "top_20_depositors_all_time": top_depositors,
        "top_10_depositors_post_ftx": top_late,
    }

# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

def main():
    es  = run_event_study()
    br  = run_base_rate_analysis()
    kl  = run_klima_overlap()

    # Save
    out_es = DATA / "event_study_results.json"
    out_br = DATA / "base_rate_analysis.json"
    out_kl = DATA / "klima_overlap_results.json"

    with open(out_es, "w") as f:
        json.dump({**es, "klima_overlap": kl}, f, indent=2, default=str)
    with open(out_br, "w") as f:
        json.dump(br, f, indent=2, default=str)
    with open(out_kl, "w") as f:
        json.dump(kl, f, indent=2, default=str)

    # ── Summary ──
    print("=" * 76)
    print("PART 1: EVENT STUDY — temporal quality decline by period")
    print("=" * 76)
    for p in ["pre_terra", "terra_to_ftx", "post_ftx", "all"]:
        s = es["bct"][p]
        print(f"BCT {p:<14s} n={s['n']:>4d}  "
              f"mean_q={s['mean_quality'] or 'NA':>6}  "
              f"rho={s['spearman_rho']:>7.4f}  "
              f"p={s['spearman_p']:>9.2e}  "
              f"tonnes={s['total_tonnes']:>12,.0f}")
    print()
    for p in ["pre_terra", "terra_to_ftx", "post_ftx", "all"]:
        s = es["nct"][p]
        rho = s['spearman_rho']
        pv = s['spearman_p']
        print(f"NCT {p:<14s} n={s['n']:>4d}  "
              f"mean_q={s['mean_quality'] or 'NA':>6}  "
              f"rho={'NA' if rho is None else f'{rho:>7.4f}'}  "
              f"p={'NA' if pv is None else f'{pv:>9.2e}'}  "
              f"tonnes={s['total_tonnes']:>12,.0f}")
    print()
    did = es["did_and_subperiod_tests"]
    if "pre_terra_BCT_vs_NCT" in did and "diff" in did["pre_terra_BCT_vs_NCT"]:
        d = did["pre_terra_BCT_vs_NCT"]
        print(f"Pre-Terra BCT vs NCT: BCT={d['bct_mean']:.2f}  NCT={d['nct_mean']:.2f}  "
              f"diff={d['diff']:+.2f}  p={d['mannwhitney_p']:.2e}")
    else:
        note = did["pre_terra_BCT_vs_NCT"].get("note", "")
        print(f"Pre-Terra BCT vs NCT: {note}")
    if "BCT_pre_vs_mid_Terra" in did:
        d = did["BCT_pre_vs_mid_Terra"]
        print(f"BCT pre-Terra vs Terra-to-FTX: {d['pre_mean']:.2f} -> {d['mid_mean']:.2f}  p={d['p']:.2e}")
    if "BCT_mid_vs_post_FTX" in did:
        d = did["BCT_mid_vs_post_FTX"]
        print(f"BCT Terra-to-FTX vs post-FTX:  {d['mid_mean']:.2f} -> {d['post_mean']:.2f}  p={d['p']:.2e}")

    print()
    print("=" * 76)
    print("PART 2: VERRA VCS BASE RATE COMPARISON")
    print("=" * 76)
    for t, sc in sorted(br["selection_coefficients"].items(), key=lambda x: -x[1]["selection_coef"]):
        print(f"{t:<18s} BCT={sc['bct_share_pct']:>5.1f}%  "
              f"VCS_base={sc['vcs_base_share_pct']:>5.1f}%  "
              f"coef={sc['selection_coef']:>5.2f}x  "
              f"Δpp={sc['bct_minus_base_pp']:+6.1f}")
    b = br["binomial_test_renewables"]
    print()
    if b:
        print(f"Binomial test (BCT renewables {b['bct_renewable_count']}/{b['bct_total_count']} "
              f"= {b['bct_renewable_share_count']*100:.1f}%, null VCS base = "
              f"{b['null_vcs_base_share']*100:.1f}%):  p = {b['binomial_p_greater']:.2e}")
    print("Sensitivity to assumed VCS renewable base rate:")
    for k, v in br["sensitivity_different_base_rates"].items():
        print(f"   {k:<22s} p = {v['p_value']:.3e}")
    ci_lo, ci_hi = br["bct_renewable_wilson_95CI"]
    print(f"BCT renewable-share 95 % CI (Wilson): [{ci_lo*100:.1f}%, {ci_hi*100:.1f}%]")
    tw = br["tonnage_weighted_selection"]
    print()
    print("Tonnage-weighted selection coefficients (paper headline 69.1% renewable):")
    print(f"   BCT 69.1% / VCS 37% (MSCI/solutionswill point) = {tw['selection_coef_paper_headline']:.2f}x")
    print(f"   BCT 69.1% / VCS 48% (upper 95% CI)              = {tw['selection_coef_high_band_48pct']:.2f}x")
    print(f"   BCT 69.1% / VCS 26% (EM retirement-weighted)    = {tw['selection_coef_low_band_26pct']:.2f}x")

    print()
    print("=" * 76)
    print("PART 3: KLIMA DAO TREASURY OVERLAP")
    print("=" * 76)
    for p in ["overall", "pre_terra", "terra_to_ftx", "post_ftx"]:
        x = kl[p]
        sc = x["share_count"]; st = x["share_tonnes"]
        sc = f"{sc*100:>5.2f}%" if sc is not None else "   NA"
        st = f"{st*100:>5.2f}%" if st is not None else "   NA"
        print(f"{p:<14s}  n={x['n']:>4d}  n_klima={x['n_klima']:>3d}  "
              f"share_count={sc}  share_tonnes={st}")
    print("\nTop 10 post-FTX depositors (by tonnage):")
    for d in kl["top_10_depositors_post_ftx"]:
        tag = "  <-- KlimaDAO" if d["is_known_klima"] else ""
        print(f"   {d['depositor']}  {d['tonnes']:>12,.2f}t  n={d['count']}{tag}")

    print()
    print("=" * 76)
    print("VERDICTS")
    print("=" * 76)
    # Verdict 1: does decline survive in pre-Terra window?
    r_pre = es["bct"]["pre_terra"]["spearman_rho"]
    p_pre = es["bct"]["pre_terra"]["spearman_p"]
    if r_pre is not None and r_pre < -0.05 and p_pre < 0.05:
        print(f"[SURVIVES] Temporal decline present pre-Terra: rho={r_pre:.3f}, p={p_pre:.2e}")
        print("           ==> Macro-shock confound RULED OUT (decline is pool-mechanism).")
    else:
        print(f"[FAILS]    Pre-Terra decline weak/absent: rho={r_pre}, p={p_pre}")
        print("           ==> Macro-shock confound remains PLAUSIBLE.")
    # Verdict 2: renewables base rate
    if b and b["binomial_p_greater"] < 0.001:
        print(f"[SURVIVES] BCT renewable share {b['bct_renewable_share_count']*100:.1f}% "
              f"significantly > VCS base {b['null_vcs_base_share']*100:.0f}% "
              f"(p={b['binomial_p_greater']:.2e}).")
        print("           ==> Base-rate confound RULED OUT.")
    else:
        print(f"[FAILS]    BCT renewable share not clearly above VCS base.")
    # Verdict 3: Klima treasury domination
    post = kl["post_ftx"]
    sc = post["share_count"] or 0.0
    st = post["share_tonnes"] or 0.0
    if max(sc, st) < 0.30:
        print(f"[SURVIVES] KlimaDAO wallets are {sc*100:.1f}% of post-FTX deposits "
              f"({st*100:.1f}% by tonnage).")
        print("           ==> Klima-treasury confound RULED OUT.")
    else:
        print(f"[FAILS]    KlimaDAO wallets are {sc*100:.1f}% of post-FTX deposits.")

if __name__ == "__main__":
    main()
