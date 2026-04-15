#!/usr/bin/env python3
"""Bootstrap confidence intervals and permutation tests for rank correlation.

Computes Spearman rho for every pair (ours vs each agency, inter-agency),
with 10,000-resample bootstrap 95% CI (percentile method) and 10,000-
permutation test p-values.  Analyses are run separately for:
  1. REDD+ only (n=6, the original CMW 2023 Table 20 dataset)
  2. Full dataset (REDD+ + cross-type, n up to 17 depending on available pairs)

Pure Python -- no scipy, numpy, or external dependencies.

Usage:
    python3 bootstrap_rank_correlation.py
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DATASET = ROOT / "data" / "rank-correlation" / "dataset.json"

SEED = 42
N_BOOTSTRAP = 10_000
N_PERMUTATION = 10_000
CI_LEVEL = 0.95

# ---------------------------------------------------------------------------
# Spearman rho -- same implementation as data/rank-correlation/compute.py
# ---------------------------------------------------------------------------

def _ranks(vals: list[float]) -> list[float]:
    """Average rank for ties (1-indexed)."""
    indexed = sorted(enumerate(vals), key=lambda p: p[1])
    out = [0.0] * len(vals)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            out[indexed[k][0]] = avg_rank
        i = j + 1
    return out


def spearman_rho(x: list[float], y: list[float]) -> float:
    """Spearman rank correlation with average-rank tie handling."""
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    rx = _ranks(x)
    ry = _ranks(y)
    n = len(x)
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = sum((r - mx) ** 2 for r in rx) ** 0.5
    dy = sum((r - my) ** 2 for r in ry) ** 0.5
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


# ---------------------------------------------------------------------------
# Bootstrap percentile CI
# ---------------------------------------------------------------------------

def bootstrap_ci(
    x: list[float],
    y: list[float],
    rng: random.Random,
    n_boot: int = N_BOOTSTRAP,
    alpha: float = 1 - CI_LEVEL,
) -> tuple[float, float, list[float]]:
    """Return (lower, upper) percentile CI and the full bootstrap distribution."""
    n = len(x)
    boot_rhos: list[float] = []
    for _ in range(n_boot):
        idx = [rng.randint(0, n - 1) for _ in range(n)]
        bx = [x[i] for i in idx]
        by = [y[i] for i in idx]
        r = spearman_rho(bx, by)
        if math.isnan(r):
            continue
        boot_rhos.append(r)
    if not boot_rhos:
        return (float("nan"), float("nan"), [])
    boot_rhos.sort()
    lo_idx = int(math.floor((alpha / 2) * len(boot_rhos)))
    hi_idx = int(math.ceil((1 - alpha / 2) * len(boot_rhos))) - 1
    lo_idx = max(0, min(lo_idx, len(boot_rhos) - 1))
    hi_idx = max(0, min(hi_idx, len(boot_rhos) - 1))
    return (boot_rhos[lo_idx], boot_rhos[hi_idx], boot_rhos)


# ---------------------------------------------------------------------------
# Permutation test
# ---------------------------------------------------------------------------

def permutation_p(
    x: list[float],
    y: list[float],
    observed_rho: float,
    rng: random.Random,
    n_perm: int = N_PERMUTATION,
) -> float:
    """Two-sided permutation p-value: fraction of permuted |rho| >= |observed|."""
    if math.isnan(observed_rho):
        return float("nan")
    count = 0
    abs_obs = abs(observed_rho)
    yy = list(y)
    for _ in range(n_perm):
        rng.shuffle(yy)
        r = spearman_rho(x, yy)
        if not math.isnan(r) and abs(r) >= abs_obs - 1e-12:
            count += 1
    return count / n_perm


# ---------------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------------

def load_dataset() -> dict:
    with DATASET.open() as f:
        return json.load(f)


def _get_our_grade(p: dict) -> str:
    """Extract the framework grade from a cross-type project."""
    v06 = p.get("our_v06", {})
    disqualifiers = v06.get("disqualifiers", [])
    if "human_rights" in disqualifiers:
        return "B"
    return v06.get("grade", "B")


def build_redd_series(data: dict) -> dict[str, list[float]]:
    """Build numeric series for the 6 REDD+ projects."""
    mapping = data["scale_mappings"]
    series: dict[str, list[float]] = {
        "ours": [], "bezero": [], "calyx_nzm": [], "sylvera_nzm": [],
    }
    for p in data["projects"]:
        our_grade = p["our_v04"].get("v0_4_1_grade") or p["our_v04"]["grade"]
        series["ours"].append(mapping["ours_v04"][our_grade])
        series["bezero"].append(mapping["bezero"][p["agency_ratings"]["bezero"]])
        series["calyx_nzm"].append(mapping["calyx_nzm"][p["agency_ratings"]["calyx_nzm"]])
        series["sylvera_nzm"].append(mapping["sylvera_nzm"][p["agency_ratings"]["sylvera_nzm"]])
    return series


def build_full_series(data: dict) -> dict[str, dict[str, list[float]]]:
    """Build pairwise series for REDD+ + cross-type (full dataset).

    Returns dict of {pair_label: {"x": [...], "y": [...]}} for each pair
    where both raters have a rating.
    """
    mapping = data["scale_mappings"]
    ours_map = mapping["ours_v04"]
    bezero_map = mapping["bezero"]
    calyx_extended = {
        "D": 0, "D+": 1, "C": 2, "C+": 3, "B": 4, "B+": 5,
        "A": 6, "A+": 7, "AA": 8, "AA+": 9, "AAA": 10,
        "E": 0,
    }
    sylvera_extended = {
        "D": 0, "C": 1, "B": 2, "BB": 3, "BBB": 4,
        "A": 5, "AA": 6, "AAA": 7,
        "Tier 3": 0, "Tier 2": 3, "Tier 1": 6,
    }

    # Collect all projects with their numeric scores per rater
    all_projects: list[dict[str, float | None]] = []

    # REDD+ projects
    for p in data["projects"]:
        our_grade = p["our_v04"].get("v0_4_1_grade") or p["our_v04"]["grade"]
        rec: dict[str, float | None] = {
            "ours": ours_map.get(our_grade),
            "bezero": bezero_map.get(p["agency_ratings"].get("bezero", "")),
            "calyx": mapping["calyx_nzm"].get(p["agency_ratings"].get("calyx_nzm", "")),
            "sylvera": mapping["sylvera_nzm"].get(p["agency_ratings"].get("sylvera_nzm", "")),
        }
        all_projects.append(rec)

    # Cross-type projects
    ct = data.get("cross_type_projects", {}).get("projects", [])
    for p in ct:
        our_grade = _get_our_grade(p)
        ar = p.get("agency_ratings", {})
        rec = {
            "ours": ours_map.get(our_grade),
            "bezero": bezero_map.get(ar.get("bezero", "")),
            "calyx": calyx_extended.get(ar.get("calyx", ar.get("calyx_nzm", "")), None),
            "sylvera": sylvera_extended.get(ar.get("sylvera", ar.get("sylvera_nzm", "")), None),
        }
        all_projects.append(rec)

    # Build pairwise series where both are non-None
    raters = ["ours", "bezero", "calyx", "sylvera"]
    pairs: dict[str, dict[str, list[float]]] = {}
    for i, a in enumerate(raters):
        for b in raters[i + 1:]:
            label = f"{a} vs {b}"
            xs, ys = [], []
            for rec in all_projects:
                va, vb = rec.get(a), rec.get(b)
                if va is not None and vb is not None:
                    xs.append(float(va))
                    ys.append(float(vb))
            if len(xs) >= 2:
                pairs[label] = {"x": xs, "y": ys}
    return pairs


# ---------------------------------------------------------------------------
# Analysis runner
# ---------------------------------------------------------------------------

def analyze_pairs(
    series_pairs: dict[str, dict[str, list[float]]],
    label: str,
    rng: random.Random,
) -> list[dict]:
    """Run bootstrap CI + permutation test for each pair."""
    results = []
    for pair_name, xy in sorted(series_pairs.items()):
        x, y = xy["x"], xy["y"]
        n = len(x)
        rho = spearman_rho(x, y)
        ci_lo, ci_hi, boot_dist = bootstrap_ci(x, y, rng)
        p_val = permutation_p(x, y, rho, rng)

        # Boot distribution stats
        if boot_dist:
            boot_mean = sum(boot_dist) / len(boot_dist)
            boot_se = (sum((v - boot_mean) ** 2 for v in boot_dist) / len(boot_dist)) ** 0.5
        else:
            boot_mean = float("nan")
            boot_se = float("nan")

        is_ours = "ours" in pair_name
        results.append({
            "dataset": label,
            "pair": pair_name,
            "n": n,
            "spearman_rho": _r(rho),
            "ci_95_lower": _r(ci_lo),
            "ci_95_upper": _r(ci_hi),
            "bootstrap_se": _r(boot_se),
            "permutation_p": _r(p_val),
            "significant_005": p_val < 0.05 if not math.isnan(p_val) else None,
            "is_ours_vs_agency": is_ours,
        })
    return results


def _r(v: float, decimals: int = 4) -> float:
    """Round, preserving NaN."""
    if math.isnan(v):
        return v
    return round(v, decimals)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def results_to_markdown(results: list[dict]) -> str:
    lines = [
        "# Bootstrap Rank Correlation Analysis",
        "",
        f"Seed: {SEED} | Bootstrap resamples: {N_BOOTSTRAP:,} | Permutations: {N_PERMUTATION:,}",
        "",
    ]
    current_dataset = None
    for r in results:
        if r["dataset"] != current_dataset:
            current_dataset = r["dataset"]
            lines.append(f"## {current_dataset}")
            lines.append("")
            lines.append("| Pair | n | Spearman rho | 95% CI | Boot SE | Perm p | Sig? |")
            lines.append("|------|---|------------:|--------|--------:|-------:|------|")
        sig = "yes" if r["significant_005"] else ("no" if r["significant_005"] is not None else "n/a")
        ci_str = f"[{_fmt(r['ci_95_lower'])}, {_fmt(r['ci_95_upper'])}]"
        lines.append(
            f"| {r['pair']} | {r['n']} | {_fmt(r['spearman_rho'])} | "
            f"{ci_str} | {_fmt(r['bootstrap_se'])} | {_fmt(r['permutation_p'])} | {sig} |"
        )
    lines.append("")

    # Summary interpretation
    lines.append("## Summary")
    lines.append("")
    for dataset_label in ("REDD+ only (n=6)", "Full dataset (REDD+ + cross-type)"):
        ds_results = [r for r in results if r["dataset"] == dataset_label]
        if not ds_results:
            continue
        ours_pairs = [r for r in ds_results if r["is_ours_vs_agency"]]
        agency_pairs = [r for r in ds_results if not r["is_ours_vs_agency"]]
        if ours_pairs:
            ours_mean = sum(r["spearman_rho"] for r in ours_pairs if not math.isnan(r["spearman_rho"])) / max(1, sum(1 for r in ours_pairs if not math.isnan(r["spearman_rho"])))
            lines.append(f"**{dataset_label}**: mean ours-vs-agency rho = {ours_mean:+.3f}")
        if agency_pairs:
            vals = [r["spearman_rho"] for r in agency_pairs if not math.isnan(r["spearman_rho"])]
            if vals:
                agency_mean = sum(vals) / len(vals)
                lines.append(f"  mean inter-agency rho = {agency_mean:+.3f}")
        lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- Bootstrap CI uses the percentile method (10,000 resamples).")
    lines.append("- Permutation p-value is two-sided: P(|rho_perm| >= |rho_obs|).")
    lines.append("- With n=6 (REDD+ only), wide CIs and non-significant p-values are expected.")
    lines.append("- The full dataset adds cross-type projects, increasing statistical power.")
    lines.append("")

    return "\n".join(lines)


def _fmt(v: float) -> str:
    if isinstance(v, float) and math.isnan(v):
        return "n/a"
    return f"{v:+.4f}" if isinstance(v, float) else str(v)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    rng = random.Random(SEED)
    data = load_dataset()

    all_results: list[dict] = []

    # --- REDD+ only (n=6) ---
    redd_series = build_redd_series(data)
    raters = list(redd_series.keys())
    redd_pairs: dict[str, dict[str, list[float]]] = {}
    for i, a in enumerate(raters):
        for b in raters[i + 1:]:
            redd_pairs[f"{a} vs {b}"] = {"x": redd_series[a], "y": redd_series[b]}
    redd_results = analyze_pairs(redd_pairs, "REDD+ only (n=6)", rng)
    all_results.extend(redd_results)

    # --- Full dataset (REDD+ + cross-type) ---
    full_pairs = build_full_series(data)
    full_results = analyze_pairs(full_pairs, "Full dataset (REDD+ + cross-type)", rng)
    all_results.extend(full_results)

    # --- Output ---
    out_json = HERE / "bootstrap_rank_correlation_results.json"
    out_json.write_text(json.dumps(all_results, indent=2, default=str))

    out_md = HERE / "bootstrap_rank_correlation_results.md"
    out_md.write_text(results_to_markdown(all_results))

    # Terminal summary
    print(f"Bootstrap rank correlation analysis complete.")
    print(f"  Seed: {SEED}")
    print(f"  Bootstrap resamples: {N_BOOTSTRAP:,}")
    print(f"  Permutations: {N_PERMUTATION:,}")
    print()
    for r in all_results:
        sig = "*" if r.get("significant_005") else ""
        print(
            f"  [{r['dataset']}] {r['pair']:<25s} n={r['n']:>2d}  "
            f"rho={_fmt(r['spearman_rho']):>8s}  "
            f"CI=[{_fmt(r['ci_95_lower'])}, {_fmt(r['ci_95_upper'])}]  "
            f"p={_fmt(r['permutation_p'])}{sig}"
        )
    print()
    print(f"Wrote: {out_json}")
    print(f"Wrote: {out_md}")


if __name__ == "__main__":
    main()
