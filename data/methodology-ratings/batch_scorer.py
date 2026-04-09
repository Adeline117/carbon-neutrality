#!/usr/bin/env python3
"""Batch scorer: generate per-project grades from methodology archetypes.

Given a CSV of projects with columns (project_id, name, methodology_category,
registry, vintage_year, country), assigns each project the archetype scores
for its methodology category and adjusts for vintage. Outputs a full scored
dataset with composite, grade, and P(grade).

This enables scaling from 45 hand-scored credits to 500+ methodology-derived
ratings — addressing the framework's largest competitive gap vs commercial
agencies (45 vs 500-4400 rated credits).

Usage:
  python3 batch_scorer.py                          # score the built-in sample
  python3 batch_scorer.py --input projects.csv     # score a custom project list
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUBRICS = ROOT / "data" / "scoring-rubrics"
ARCHETYPES = HERE / "archetypes.json"

# Import scorer functions from the main scorer
sys.path.insert(0, str(ROOT / "data" / "pilot-scoring"))
from score import (
    composite,
    composite_variance,
    grade_from_score,
    grade_posterior,
    load_default_stds,
    load_rubric_index,
    normal_cdf,
)


def load_archetypes() -> dict[str, dict]:
    data = json.loads(ARCHETYPES.read_text())
    return {a["id"]: a for a in data["archetypes"]}


def vintage_score(vintage_year: int, current_year: int = 2026) -> int:
    return max(0, min(100, 100 - (current_year - vintage_year) * 12))


def score_project(
    project: dict,
    archetypes: dict,
    weights: dict,
    default_stds: dict,
    grade_bands: list[dict],
) -> dict:
    """Score a single project using its methodology archetype."""
    cat = project.get("methodology_category", "")
    archetype = archetypes.get(cat)
    if archetype is None:
        # Try fuzzy match
        for aid, a in archetypes.items():
            if cat.lower() in aid.lower() or aid.lower() in cat.lower():
                archetype = a
                break
    if archetype is None:
        archetype = archetypes.get("redd_project")  # fallback

    scores = dict(archetype["scores"])
    # Override vintage from project data
    vy = project.get("vintage_year", 2024)
    scores["vintage_year"] = vintage_score(int(vy))

    # Per-archetype stds: merge archetype-specific overrides with global defaults
    arch_stds = archetype.get("std_overrides", {})
    stds = {d: float(arch_stds.get(d, default_stds[d])) for d in default_stds}

    # Compute
    comp = composite(scores, weights)
    comp_var = composite_variance(stds, weights)
    comp_sigma = math.sqrt(comp_var) if comp_var > 0 else 0.0
    grade = grade_from_score(comp, grade_bands)
    posterior = grade_posterior(comp, comp_sigma, grade_bands)
    p_grade = posterior.get(grade, 0.0)

    return {
        "project_id": project.get("project_id", ""),
        "name": project.get("name", ""),
        "methodology_category": cat,
        "archetype_id": archetype["id"],
        "registry": project.get("registry", ""),
        "vintage_year": vy,
        "country": project.get("country", ""),
        "composite": round(comp, 2),
        "composite_std": round(comp_sigma, 2),
        "grade": grade,
        "p_grade": round(p_grade, 3),
        "ccp_status": archetype.get("ccp_status", "unknown"),
    }


def generate_sample_projects() -> list[dict]:
    """Generate a representative sample of 200 projects spanning all archetypes."""
    import random

    random.seed(42)  # reproducible

    archetypes_data = json.loads(ARCHETYPES.read_text())["archetypes"]
    countries = {
        "daccs_geological": ["Iceland", "USA", "Norway", "UK"],
        "biochar": ["USA", "Finland", "Cambodia", "Brazil", "Kenya"],
        "enhanced_weathering": ["UK", "USA", "India", "Brazil"],
        "bio_oil_geological": ["USA", "Canada"],
        "arr_conservation": ["Brazil", "Indonesia", "India", "Peru", "Kenya", "Colombia"],
        "arr_commercial_plantation": ["Uruguay", "Chile", "Brazil", "Indonesia"],
        "ifm": ["USA", "Canada", "Australia", "Brazil"],
        "redd_jurisdictional": ["Brazil", "DRC", "Indonesia", "Peru", "Guyana"],
        "redd_project": ["Brazil", "Indonesia", "DRC", "Peru", "Cambodia", "Zimbabwe", "Kenya"],
        "cookstoves": ["Kenya", "Ghana", "India", "Bangladesh", "Cambodia", "Uganda"],
        "landfill_gas": ["USA", "Brazil", "Mexico", "Turkey"],
        "n2o_abatement": ["India", "China", "South Korea"],
        "ods_destruction": ["USA", "Thailand", "Mexico"],
        "rice_methane": ["Vietnam", "Thailand", "India", "Bangladesh"],
        "sustainable_agriculture": ["USA", "Brazil", "India", "Australia"],
        "grid_renewable_energy": ["China", "India", "Brazil", "Turkey", "Vietnam"],
        "hfc23_destruction": ["China", "India"],
    }

    # Distribution of projects per archetype (roughly proportional to real VCM)
    counts = {
        "daccs_geological": 5,
        "biochar": 12,
        "enhanced_weathering": 4,
        "bio_oil_geological": 3,
        "arr_conservation": 20,
        "arr_commercial_plantation": 8,
        "ifm": 15,
        "redd_jurisdictional": 8,
        "redd_project": 30,
        "cookstoves": 25,
        "landfill_gas": 12,
        "n2o_abatement": 6,
        "ods_destruction": 5,
        "rice_methane": 8,
        "sustainable_agriculture": 10,
        "grid_renewable_energy": 20,
        "hfc23_destruction": 8,
    }

    projects = []
    pid = 1
    for arch in archetypes_data:
        aid = arch["id"]
        n = counts.get(aid, 5)
        country_list = countries.get(aid, ["Unknown"])
        for i in range(n):
            vintage = random.choice(range(2018, 2026)) if aid not in (
                "hfc23_destruction", "grid_renewable_energy"
            ) else random.choice(range(2012, 2022))
            projects.append({
                "project_id": f"BATCH-{pid:04d}",
                "name": f"{arch['description']} #{i+1} ({random.choice(country_list)})",
                "methodology_category": aid,
                "registry": arch["methodologies"][0] if arch["methodologies"] else "Unknown",
                "vintage_year": vintage,
                "country": random.choice(country_list),
            })
            pid += 1

    return projects


def main() -> None:
    rubrics = load_rubric_index()
    weights = {d["id"]: d["weight"] for d in rubrics["dimensions"]}
    grade_bands = rubrics["grades"]
    default_stds = load_default_stds(rubrics)
    archetypes = load_archetypes()

    # Load projects from CSV or generate sample
    if "--input" in sys.argv:
        idx = sys.argv.index("--input")
        input_path = Path(sys.argv[idx + 1])
        projects = list(csv.DictReader(input_path.open()))
    else:
        projects = generate_sample_projects()

    # Score each project
    results = [
        score_project(p, archetypes, weights, default_stds, grade_bands)
        for p in projects
    ]

    # Write CSV
    out_csv = HERE / "batch_scores.csv"
    fieldnames = list(results[0].keys())
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results)

    # Grade distribution
    dist: dict[str, int] = {}
    for r in results:
        dist[r["grade"]] = dist.get(r["grade"], 0) + 1

    print(f"Batch scored {len(results)} projects -> {out_csv}")
    print(f"Grade distribution: {dist}")

    # Per-archetype summary
    arch_grades: dict[str, dict] = {}
    for r in results:
        aid = r["archetype_id"]
        if aid not in arch_grades:
            arch_grades[aid] = {"grades": [], "composites": []}
        arch_grades[aid]["grades"].append(r["grade"])
        arch_grades[aid]["composites"].append(r["composite"])

    print("\nPer-methodology-category summary:")
    print(f"{'Category':<30s} {'N':>4s} {'Mean comp':>10s} {'Typical grade':<15s}")
    for aid, data in sorted(arch_grades.items()):
        n = len(data["composites"])
        mean_c = sum(data["composites"]) / n
        mode_g = max(set(data["grades"]), key=data["grades"].count)
        print(f"{aid:<30s} {n:>4d} {mean_c:>10.1f} {mode_g:<15s}")

    # Write summary JSON
    summary = {
        "total_projects": len(results),
        "grade_distribution": dist,
        "methodology_categories": len(arch_grades),
        "note": "Methodology-level archetype scoring. Per-project scores use archetype defaults adjusted for vintage. This is NOT per-project expert assessment — it is a scalable approximation for coverage expansion.",
    }
    (HERE / "batch_summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
