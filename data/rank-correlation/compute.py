#!/usr/bin/env python3
"""
Compute pairwise rank correlation (Spearman) between our v0.4 framework and
three commercial carbon credit rating agencies (BeZero, Calyx Global NZM,
Sylvera NZM) using the 6-project dataset from Carbon Market Watch 2023
Table 20.

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
        our_grade = p["our_v04"]["grade"]
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

    (HERE / "results.md").write_text("\n".join(md_lines))
    print(f"\nWrote: {HERE/'results.md'}\nWrote: {HERE/'results.csv'}")


if __name__ == "__main__":
    main()
