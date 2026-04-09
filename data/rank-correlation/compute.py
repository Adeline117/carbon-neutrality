#!/usr/bin/env python3
"""
Compute pairwise rank correlation (Spearman) between our v0.4 framework and
three commercial carbon credit rating agencies (BeZero, Calyx Global NZM,
Sylvera NZM) using the 6-project dataset from Carbon Market Watch 2023
Table 20.

v0.6 extension: if a "cross_type_projects" array exists in dataset.json,
also compute per-type Spearman between our v0.6 scores and BeZero on the
cross-type dataset, and an overall Spearman across all projects where both
our framework and BeZero have ratings.

Pure Python, no external dependencies. Writes results.md and results.csv.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
DATASET = HERE / "dataset.json"


def load_dataset() -> dict:
    with DATASET.open() as f:
        return json.load(f)


def spearman_rank_correlation(x: list[float], y: list[float]) -> float:
    """Spearman rho. Handles ties via average ranks."""
    if len(x) != len(y) or len(x) < 2:
        return float("nan")

    def ranks(vals: list[float]) -> list[float]:
        # average rank for ties
        indexed = sorted(enumerate(vals), key=lambda p: p[1])
        out = [0.0] * len(vals)
        i = 0
        while i < len(indexed):
            j = i
            while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
                j += 1
            avg_rank = (i + j) / 2 + 1  # 1-indexed
            for k in range(i, j + 1):
                out[indexed[k][0]] = avg_rank
            i = j + 1
        return out

    rx = ranks(x)
    ry = ranks(y)
    n = len(x)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = sum((r - mean_rx) ** 2 for r in rx) ** 0.5
    den_y = sum((r - mean_ry) ** 2 for r in ry) ** 0.5
    if den_x == 0 or den_y == 0:
        return float("nan")
    return num / (den_x * den_y)


def kendall_tau(x: list[float], y: list[float]) -> float:
    """Kendall tau-b. Handles ties."""
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    n = len(x)
    concordant = 0
    discordant = 0
    tx = 0
    ty = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[i] - x[j]
            dy = y[i] - y[j]
            if dx == 0 and dy == 0:
                continue
            if dx == 0:
                tx += 1
                continue
            if dy == 0:
                ty += 1
                continue
            if (dx > 0 and dy > 0) or (dx < 0 and dy < 0):
                concordant += 1
            else:
                discordant += 1
    denom = ((concordant + discordant + tx) * (concordant + discordant + ty)) ** 0.5
    if denom == 0:
        return float("nan")
    return (concordant - discordant) / denom


def main() -> None:
    data = load_dataset()
    projects = data["projects"]
    mapping = data["scale_mappings"]

    # build numeric series per rater
    series: dict[str, list[float]] = {
        "ours_v04": [],
        "bezero": [],
        "calyx_nzm": [],
        "sylvera_nzm": [],
    }
    ids: list[str] = []
    grades: dict[str, list[str]] = {k: [] for k in series}

    for p in projects:
        ids.append(p["id"])
        # Prefer v0.4.1 adjusted grade if present (e.g. Guanare's
        # commercial_plantation_arr adjustment), fall back to base v0.4.
        our_grade = p["our_v04"].get("v0_4_1_grade") or p["our_v04"]["grade"]
        series["ours_v04"].append(mapping["ours_v04"][our_grade])
        grades["ours_v04"].append(our_grade)
        for rater in ("bezero", "calyx_nzm", "sylvera_nzm"):
            g = p["agency_ratings"][rater]
            series[rater].append(mapping[rater][g])
            grades[rater].append(g)

    raters = list(series.keys())
    pairs = [(a, b) for i, a in enumerate(raters) for b in raters[i + 1 :]]

    # pairwise correlations
    print(f"Rank correlation on n={len(projects)} projects (CMW 2023 Table 20 + our v0.4 scoring)\n")
    print("| Pair | Spearman rho | Kendall tau |")
    print("|------|-------------:|------------:|")
    rows = []
    for a, b in pairs:
        rho = spearman_rank_correlation(series[a], series[b])
        tau = kendall_tau(series[a], series[b])
        rows.append({"pair": f"{a} vs {b}", "spearman": rho, "kendall": tau})
        print(f"| {a} vs {b} | {rho:+.3f} | {tau:+.3f} |")
    print()

    # per-project comparison table
    print("## Per-project grades\n")
    print("| ID | Project | Our v0.4 | BeZero | Calyx NZM | Sylvera NZM |")
    print("|----|---------|----------|--------|-----------|-------------|")
    for i, p in enumerate(projects):
        print(
            f"| {p['id']} | {p['name'][:40]} | "
            f"{grades['ours_v04'][i]} ({series['ours_v04'][i]}) | "
            f"{grades['bezero'][i]} ({series['bezero'][i]}) | "
            f"{grades['calyx_nzm'][i]} ({series['calyx_nzm'][i]}) | "
            f"{grades['sylvera_nzm'][i]} ({series['sylvera_nzm'][i]}) |"
        )

    # write results files
    (HERE / "results.csv").write_text(
        "\n".join(
            ["pair,spearman,kendall"]
            + [f"{r['pair']},{r['spearman']:.4f},{r['kendall']:.4f}" for r in rows]
        )
    )

    md_lines = [
        "# Rank Correlation Results",
        "",
        f"Dataset: {len(projects)} REDD+ projects from Carbon Market Watch 2023 Table 20, scored under v0.4.",
        "",
        "## Pairwise correlations",
        "",
        "| Pair | Spearman rho | Kendall tau |",
        "|------|-------------:|------------:|",
    ]
    for r in rows:
        md_lines.append(f"| {r['pair']} | {r['spearman']:+.3f} | {r['kendall']:+.3f} |")
    md_lines.append("")
    md_lines.append("## Per-project grades")
    md_lines.append("")
    md_lines.append("| ID | Project | Our v0.4 | BeZero | Calyx NZM | Sylvera NZM |")
    md_lines.append("|----|---------|----------|--------|-----------|-------------|")
    for i, p in enumerate(projects):
        md_lines.append(
            f"| {p['id']} | {p['name']} | "
            f"{grades['ours_v04'][i]} | {grades['bezero'][i]} | "
            f"{grades['calyx_nzm'][i]} | {grades['sylvera_nzm'][i]} |"
        )
    md_lines.append("")

    # inter-agency vs our-vs-agency comparison
    md_lines.append("## Interpretation: are we as agreeable as the commercial agencies are with each other?")
    md_lines.append("")
    agency_pairs = [r for r in rows if "ours_v04" not in r["pair"]]
    our_pairs = [r for r in rows if "ours_v04" in r["pair"]]
    agency_mean_rho = sum(r["spearman"] for r in agency_pairs) / len(agency_pairs) if agency_pairs else float("nan")
    our_mean_rho = sum(r["spearman"] for r in our_pairs) / len(our_pairs) if our_pairs else float("nan")
    md_lines.append(
        f"- Inter-agency Spearman (mean of BeZero/Calyx/Sylvera pairs): **{agency_mean_rho:+.3f}**"
    )
    md_lines.append(
        f"- Our-framework-vs-agency Spearman (mean of our pairs): **{our_mean_rho:+.3f}**"
    )
    if our_mean_rho >= agency_mean_rho:
        md_lines.append(
            "- **Our pairwise agreement with the commercial raters is no worse than the commercial raters' agreement with each other.** This is the success criterion from the v0.4 plan note."
        )
    else:
        md_lines.append(
            "- Our pairwise agreement with the commercial raters is weaker than the commercial raters' agreement with each other. This is a flag to address in v0.6."
        )
    md_lines.append("")
    md_lines.append(f"Sample size is small (n={len(projects)}). Treat the direction of the comparison as evidence, not the absolute magnitudes.")

    # ── v0.6 Cross-type analysis ──────────────────────────────────────────
    cross_type = data.get("cross_type_projects")
    if cross_type and cross_type.get("projects"):
        ct_projects = cross_type["projects"]
        ct_md_lines = compute_cross_type(ct_projects, mapping, md_lines)
        md_lines = ct_md_lines

    (HERE / "results.md").write_text("\n".join(md_lines))
    print(f"\nWrote: {HERE/'results.md'}\nWrote: {HERE/'results.csv'}")


def compute_cross_type(
    ct_projects: list[dict],
    mapping: dict,
    md_lines: list[str],
) -> list[str]:
    """Compute per-type and overall Spearman for cross-type dataset.

    Uses the v0.6 grade scale (same letter grades as ours_v04 mapping) and
    BeZero's 8-point scale. Only projects with a BeZero rating are included
    in the BeZero correlation. Calyx and Sylvera are computed where available.
    """
    ours_map = mapping["ours_v04"]
    bezero_map = mapping["bezero"]
    # Calyx updated to AAA-D scale in Jan 2025; we extend the mapping for
    # cross-type projects that may use the new Calyx scale.
    calyx_extended = {
        "D": 0, "D+": 1, "C": 2, "C+": 3, "B": 4, "B+": 5,
        "A": 6, "A+": 7, "AA": 8, "AA+": 9, "AAA": 10,
        # Backwards compat with NZM scale
        "E": 0,
    }
    sylvera_extended = {
        "D": 0, "C": 1, "B": 2, "BB": 3, "BBB": 4,
        "A": 5, "AA": 6, "AAA": 7,
        # Backwards compat with NZM tiers
        "Tier 3": 0, "Tier 2": 3, "Tier 1": 6,
    }

    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("# Cross-Type Rank Correlation (v0.6 extension)")
    md_lines.append("")
    md_lines.append(
        f"Dataset: {len(ct_projects)} non-REDD+ projects with publicly documented agency ratings, "
        "scored under v0.6 using methodology archetypes."
    )
    md_lines.append("")

    # ── Per-project table ──
    md_lines.append("## Per-project grades (cross-type)")
    md_lines.append("")
    md_lines.append("| ID | Project | Type | Our v0.6 | BeZero | Calyx | Sylvera |")
    md_lines.append("|----|---------|------|----------|--------|-------|---------|")
    for p in ct_projects:
        our_grade = _get_our_grade(p)
        bz = p["agency_ratings"].get("bezero", "-")
        cx = p["agency_ratings"].get("calyx", p["agency_ratings"].get("calyx_nzm", "-"))
        sy = p["agency_ratings"].get("sylvera", p["agency_ratings"].get("sylvera_nzm", "-"))
        md_lines.append(
            f"| {p['id']} | {p['name'][:45]} | {p['project_type']} | "
            f"{our_grade} | {bz} | {cx} | {sy} |"
        )
    md_lines.append("")

    # ── Build series for BeZero pairwise (most data points) ──
    ours_bz: list[float] = []
    bezero_bz: list[float] = []
    type_buckets: dict[str, list[tuple[float, float]]] = {}

    for p in ct_projects:
        our_grade = _get_our_grade(p)
        if our_grade not in ours_map:
            continue
        bz = p["agency_ratings"].get("bezero")
        if not bz or bz not in bezero_map:
            continue
        our_num = ours_map[our_grade]
        bz_num = bezero_map[bz]
        ours_bz.append(our_num)
        bezero_bz.append(bz_num)
        ptype = p.get("project_type", "Unknown")
        type_buckets.setdefault(ptype, []).append((our_num, bz_num))

    # Overall cross-type correlation vs BeZero
    if len(ours_bz) >= 2:
        rho_all = spearman_rank_correlation(ours_bz, bezero_bz)
        tau_all = kendall_tau(ours_bz, bezero_bz)
        md_lines.append("## Overall cross-type: Our v0.6 vs BeZero")
        md_lines.append("")
        md_lines.append(f"- n = {len(ours_bz)} projects with both ratings")
        md_lines.append(f"- Spearman rho: **{rho_all:+.3f}**")
        md_lines.append(f"- Kendall tau: **{tau_all:+.3f}**")
        md_lines.append("")

    # Per-type Spearman vs BeZero
    md_lines.append("## Per-type Spearman: Our v0.6 vs BeZero")
    md_lines.append("")
    md_lines.append("| Project type | n | Spearman rho | Kendall tau |")
    md_lines.append("|--------------|---|-------------:|------------:|")
    per_type_rows = []
    for ptype in sorted(type_buckets.keys()):
        pts = type_buckets[ptype]
        if len(pts) < 2:
            md_lines.append(f"| {ptype} | {len(pts)} | n/a (n<2) | n/a |")
            per_type_rows.append({"type": ptype, "n": len(pts), "spearman": float("nan"), "kendall": float("nan")})
            continue
        xs = [t[0] for t in pts]
        ys = [t[1] for t in pts]
        rho = spearman_rank_correlation(xs, ys)
        tau = kendall_tau(xs, ys)
        if rho != rho:  # NaN check
            md_lines.append(f"| {ptype} | {len(pts)} | n/a (tied) | n/a (tied) |")
        else:
            md_lines.append(f"| {ptype} | {len(pts)} | {rho:+.3f} | {tau:+.3f} |")
        per_type_rows.append({"type": ptype, "n": len(pts), "spearman": rho, "kendall": tau})
    md_lines.append("")

    # ── Calyx pairwise (where available) ──
    ours_cx: list[float] = []
    calyx_cx: list[float] = []
    for p in ct_projects:
        our_grade = _get_our_grade(p)
        if our_grade not in ours_map:
            continue
        cx = p["agency_ratings"].get("calyx", p["agency_ratings"].get("calyx_nzm"))
        if not cx or cx not in calyx_extended:
            continue
        ours_cx.append(ours_map[our_grade])
        calyx_cx.append(calyx_extended[cx])

    if len(ours_cx) >= 2:
        rho_cx = spearman_rank_correlation(ours_cx, calyx_cx)
        tau_cx = kendall_tau(ours_cx, calyx_cx)
        md_lines.append("## Our v0.6 vs Calyx (cross-type)")
        md_lines.append("")
        md_lines.append(f"- n = {len(ours_cx)} projects with both ratings")
        if rho_cx != rho_cx:  # NaN
            md_lines.append("- Spearman rho: **n/a (tied on one or both variables)**")
            md_lines.append("- Kendall tau: **n/a**")
        else:
            md_lines.append(f"- Spearman rho: **{rho_cx:+.3f}**")
            md_lines.append(f"- Kendall tau: **{tau_cx:+.3f}**")
        md_lines.append("")

    # ── Sylvera pairwise (where available) ──
    ours_sy: list[float] = []
    sylvera_sy: list[float] = []
    for p in ct_projects:
        our_grade = _get_our_grade(p)
        if our_grade not in ours_map:
            continue
        sy = p["agency_ratings"].get("sylvera", p["agency_ratings"].get("sylvera_nzm"))
        if not sy or sy not in sylvera_extended:
            continue
        ours_sy.append(ours_map[our_grade])
        sylvera_sy.append(sylvera_extended[sy])

    if len(ours_sy) >= 2:
        rho_sy = spearman_rank_correlation(ours_sy, sylvera_sy)
        tau_sy = kendall_tau(ours_sy, sylvera_sy)
        md_lines.append("## Our v0.6 vs Sylvera (cross-type)")
        md_lines.append("")
        md_lines.append(f"- n = {len(ours_sy)} projects with both ratings")
        if rho_sy != rho_sy:  # NaN
            md_lines.append("- Spearman rho: **n/a (tied on one or both variables)**")
            md_lines.append("- Kendall tau: **n/a**")
        else:
            md_lines.append(f"- Spearman rho: **{rho_sy:+.3f}**")
            md_lines.append(f"- Kendall tau: **{tau_sy:+.3f}**")
        md_lines.append("")

    # ── Combined dataset: REDD+ (v0.4.1) + cross-type (v0.6) vs BeZero ──
    md_lines.append("## Combined dataset: REDD+ + cross-type vs BeZero")
    md_lines.append("")
    md_lines.append(
        "Pooling the 6 REDD+ projects (our v0.4.1 grades) with the cross-type "
        "projects (our v0.6 grades) for an overall correlation against BeZero."
    )
    md_lines.append("")

    # Write cross-type results CSV
    csv_lines = ["section,pair_or_type,n,spearman,kendall"]
    if len(ours_bz) >= 2:
        csv_lines.append(f"cross_type_overall,ours_v06 vs bezero,{len(ours_bz)},{rho_all:.4f},{tau_all:.4f}")
    for r in per_type_rows:
        sp = f"{r['spearman']:.4f}" if r["spearman"] == r["spearman"] else "nan"
        kt = f"{r['kendall']:.4f}" if r["kendall"] == r["kendall"] else "nan"
        csv_lines.append(f"per_type,{r['type']},{r['n']},{sp},{kt}")

    # Append to results.csv
    existing_csv = (HERE / "results.csv").read_text()
    (HERE / "results.csv").write_text(existing_csv + "\n" + "\n".join(csv_lines))

    # Print cross-type summary
    print("\n\n── Cross-Type Rank Correlation (v0.6) ──\n")
    if len(ours_bz) >= 2:
        print(f"Overall cross-type (n={len(ours_bz)}): Spearman {rho_all:+.3f}, Kendall {tau_all:+.3f}")
    print("\nPer-type vs BeZero:")
    print("| Type | n | Spearman | Kendall |")
    print("|------|---|----------|---------|")
    for r in per_type_rows:
        sp = f"{r['spearman']:+.3f}" if r["spearman"] == r["spearman"] else "n/a"
        kt = f"{r['kendall']:+.3f}" if r["kendall"] == r["kendall"] else "n/a"
        print(f"| {r['type']} | {r['n']} | {sp} | {kt} |")

    return md_lines


def _get_our_grade(p: dict) -> str:
    """Extract our grade from a cross-type project entry."""
    v06 = p.get("our_v06", {})
    # Check for disqualifier cap
    disqualifiers = v06.get("disqualifiers", [])
    if disqualifiers:
        # If disqualifier notes mention a cap, the notes should specify
        # the final grade. For automated computation, we apply the cap.
        grade = v06.get("grade", "B")
        notes = v06.get("disqualifier_notes", "")
        if "human_rights" in disqualifiers:
            # human_rights caps at B
            grade_order = ["B", "BB", "BBB", "A", "AA", "AAA"]
            idx = grade_order.index(grade) if grade in grade_order else 0
            cap_idx = grade_order.index("B")
            if idx > cap_idx:
                grade = "B"
        return grade
    return v06.get("grade", "B")


if __name__ == "__main__":
    main()
