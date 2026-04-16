#!/usr/bin/env python3
"""Validate a panel-scores run.

Given a runs/<run_id>/panel_scores.jsonl, compute:

  - Inter-model Fleiss' κ per dimension (10-bucket binning) + grade-level κ
  - ICC(2,k) on the continuous composite
  - Pairwise Cohen's κ on grade
  - Correlation (Spearman + Pearson) with external ratings from
    data/rank-correlation/expanded_dataset.json where the project IDs overlap
  - Adversarial injection test using 4 synthetic stress-test credits
    (double_counting, sanctioned_registry, no_third_party, community_harm)

Outputs:
  - runs/<run_id>/validation_summary.json
  - runs/<run_id>/per_project_composites.csv
  - runs/<run_id>/external_correlation.json
  - stdout human report

Pure Python (math, statistics, json). No scipy/numpy.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from pathlib import Path
from collections import defaultdict
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = Path("/Users/adelinewen/carbon-neutrality")
RUBRICS = REPO / "data" / "scoring-rubrics"
RUNS_DIR = HERE / "runs"
EXTERNAL_DATASET = REPO / "data" / "rank-correlation" / "expanded_dataset.json"

DIMS = [
    "removal_type", "additionality", "permanence", "mrv_grade",
    "vintage_year", "co_benefits", "registry_methodology",
]
GRADES = ["B", "BB", "BBB", "A", "AA", "AAA"]
GRADE_INDEX = {g: i for i, g in enumerate(GRADES)}


# ---------- stats helpers (pure python) ----------

def pearson(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    mx = sum(x) / len(x); my = sum(y) / len(y)
    num = sum((x[i] - mx) * (y[i] - my) for i in range(len(x)))
    dx = math.sqrt(sum((a - mx) ** 2 for a in x))
    dy = math.sqrt(sum((a - my) ** 2 for a in y))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


def rank(values: list[float]) -> list[float]:
    # Average-rank with ties
    indexed = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and values[indexed[j + 1]] == values[indexed[i]]:
            j += 1
        avg = (i + j) / 2 + 1  # ranks are 1-indexed
        for k in range(i, j + 1):
            ranks[indexed[k]] = avg
        i = j + 1
    return ranks


def spearman(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    return pearson(rank(x), rank(y))


def cohens_kappa(a: list[int], b: list[int], k: int) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(1 for i in range(n) if a[i] == b[i]) / n
    pa = [a.count(c) / n for c in range(k)]
    pb = [b.count(c) / n for c in range(k)]
    pe = sum(pa[c] * pb[c] for c in range(k))
    if pe == 1:
        return 1.0
    return (po - pe) / (1 - pe)


def fleiss_kappa(matrix: list[list[int]], k: int) -> float:
    n = len(matrix)
    if n == 0:
        return float("nan")
    m = sum(matrix[0])
    if m < 2:
        return float("nan")
    p_j = [sum(matrix[i][c] for i in range(n)) / (n * m) for c in range(k)]
    P_i = [
        (sum(matrix[i][c] ** 2 for c in range(k)) - m) / (m * (m - 1))
        for i in range(n)
    ]
    P_bar = sum(P_i) / n
    P_e = sum(p ** 2 for p in p_j)
    if P_e == 1:
        return 1.0
    return (P_bar - P_e) / (1 - P_e)


def icc_2k(ratings: list[list[float]]) -> float:
    n = len(ratings)
    if n < 2:
        return float("nan")
    k = len(ratings[0])
    grand_mean = sum(sum(r) for r in ratings) / (n * k)
    subject_means = [sum(r) / k for r in ratings]
    rater_means = [sum(ratings[i][j] for i in range(n)) / n for j in range(k)]
    SSR = k * sum((sm - grand_mean) ** 2 for sm in subject_means)
    SSC = n * sum((rm - grand_mean) ** 2 for rm in rater_means)
    SST = sum((ratings[i][j] - grand_mean) ** 2 for i in range(n) for j in range(k))
    SSE = SST - SSR - SSC
    MSR = SSR / (n - 1)
    MSE = SSE / ((n - 1) * (k - 1)) if (n > 1 and k > 1) else float("nan")
    if MSR == 0:
        return float("nan")
    return (MSR - MSE) / MSR


# ---------- loaders ----------

def load_rubric() -> dict:
    return json.loads((RUBRICS / "index.json").read_text())


def load_rows(run_id: str) -> list[dict]:
    path = RUNS_DIR / run_id / "panel_scores.jsonl"
    if not path.exists():
        raise SystemExit(f"no rows at {path}")
    out = []
    for line in path.read_text().splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def composite_for(scores: dict[str, int], weights: dict[str, float]) -> float:
    return sum((scores.get(d) or 0) * weights[d] for d in DIMS)


def grade_from_composite(composite: float, bands: list[dict]) -> str:
    for band in bands:
        if composite >= band["min"]:
            return band["grade"]
    return "B"


def apply_dq_cap(grade: str, flags: list[str], dq_spec: list[dict]) -> str:
    caps = {dq["id"]: dq["grade_cap"] for dq in dq_spec}
    final = grade
    for f in flags:
        if f in caps:
            cap = caps[f]
            if GRADE_INDEX[final] > GRADE_INDEX[cap]:
                final = cap
    return final


# ---------- external correlation ----------

def load_external() -> dict[str, dict]:
    """project_id (string, e.g. '1094') -> agency_ratings dict."""
    if not EXTERNAL_DATASET.exists():
        return {}
    d = json.loads(EXTERNAL_DATASET.read_text())
    out = {}
    for p in d["projects"]:
        rid = p.get("registry_id", "")
        m = rid.replace("VCS", "").replace("GS", "").strip()
        m = m.split()[0] if m else ""
        if m.isdigit():
            out[m] = {
                "agency_ratings": p.get("agency_ratings", {}),
                "our_grade": p.get("our_grade"),
                "name": p.get("name"),
            }
    return out


BEZERO_SCALE = {"D": 0, "C": 1, "B": 2, "BB": 3, "BBB": 4, "A": 5, "AA": 6, "AAA": 7}
CALYX_SCALE = {
    "E": 0, "E+": 0.5, "D": 1, "D+": 1.5, "C": 2, "C+": 2.5,
    "B": 3, "B+": 3.5, "A": 4, "A+": 4.5, "AA": 5, "AA+": 5.5, "AAA": 6,
}
SYLVERA_SCALE = {"D": 0, "C": 1, "B": 2, "BB": 3, "BBB": 4, "A": 5, "AA": 6, "AAA": 7,
                 "Tier 3": 0, "Tier 2": 3, "Tier 1": 6}


# ---------- adversarial stress-test stub ----------

STRESS_TESTS = [
    {
        "project_ref": {"registry": "VCS", "project_id": "STRESS01"},
        "fields": {
            "type_archetype": "REDD+",
            "methodology": "VM0007",
            "country": "Kenya",
            "vintage": "2022",
            "description": (
                "Tropical REDD+ project with credits SOLD TO TWO BUYERS under separate "
                "contracts; evidence of double-counting across VCS and host-country "
                "NDC inventory. All other technical fields are AA-tier."
            ),
            "claims": ["Avoided deforestation", "DOUBLE-ASSIGNED to country NDC"],
            "monitoring_approach": "Remote sensing + field plots (otherwise adequate).",
        },
        "expected_disqualifier": "double_counting",
    },
    {
        "project_ref": {"registry": "CDM", "project_id": "STRESS02"},
        "fields": {
            "type_archetype": "Industrial gas",
            "methodology": "AM0001",
            "country": "Iran",
            "vintage": "2015",
            "description": (
                "Large-scale HFC-23 destruction at a sanctioned facility; the originating "
                "CDM registry has been under sanction since 2018. Technical MRV is strong."
            ),
            "claims": ["HFC-23 destruction"],
            "monitoring_approach": "Continuous emissions monitoring.",
        },
        "expected_disqualifier": "sanctioned_registry",
    },
    {
        "project_ref": {"registry": "VCS", "project_id": "STRESS03"},
        "fields": {
            "type_archetype": "ARR",
            "methodology": "VM0047",
            "country": "Indonesia",
            "vintage": "2024",
            "description": (
                "Well-designed reforestation project — BUT monitoring reports were produced "
                "by the project developer itself; no independent VVB has verified any issuance. "
                "All technical dimensions are A/AA."
            ),
            "claims": ["Net tree-cover increase", "Self-verified"],
            "monitoring_approach": "Self-reported; no third-party attestation.",
        },
        "expected_disqualifier": "no_third_party",
    },
    {
        "project_ref": {"registry": "VCS", "project_id": "STRESS04"},
        "fields": {
            "type_archetype": "REDD+",
            "methodology": "VM0015",
            "country": "Democratic Republic of the Congo",
            "vintage": "2022",
            "description": (
                "Large REDD+ concession with DOCUMENTED INDIGENOUS EVICTIONS and credible "
                "human-rights complaints filed with the registry grievance mechanism; "
                "technical scores are otherwise AA-tier."
            ),
            "claims": ["Avoided deforestation", "LAND-TENURE DISPUTE"],
            "monitoring_approach": "Remote sensing (technically adequate).",
        },
        "expected_disqualifier": "community_harm",
    },
]


def write_stress_evidence_packs(out_dir: Path) -> list[Path]:
    """Serialize the 4 stress tests as evidence packs so run_panel.py can score them."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for s in STRESS_TESTS:
        pack = {
            "evidence_pack_version": "0.1.0",
            "project_ref": s["project_ref"],
            "fields": s["fields"],
            "provenance": [{"source": "stress-test-synthetic", "fetched_at": "synthetic"}],
            "evidence_level": "synthetic-stress-test",
            "_expected_disqualifier": s["expected_disqualifier"],
        }
        pid = s["project_ref"]["project_id"]
        p = out_dir / f"{s['project_ref']['registry']}_{pid}.json"
        p.write_text(json.dumps(pack, indent=2))
        paths.append(p)
    return paths


# ---------- main ----------

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    p.add_argument("--stress-run-id", default=None, help="Optional: run id for the stress-test panel run")
    args = p.parse_args()

    rubric = load_rubric()
    weights = {d["id"]: d["weight"] for d in rubric["dimensions"]}
    bands = rubric["grades"]
    dq_spec = rubric["disqualifiers"]

    rows = load_rows(args.run_id)
    # Group by project, rater
    by_proj: dict[str, dict[str, dict]] = defaultdict(dict)
    raters: set[str] = set()
    for r in rows:
        pid = f"{r['project_ref']['registry']}_{r['project_ref']['project_id']}"
        model = r["rater_model"]
        raters.add(model)
        by_proj[pid][model] = r
    raters_list = sorted(raters)
    n_raters = len(raters_list)

    # Keep only projects that every rater scored
    complete_pids = [pid for pid, m in by_proj.items() if set(m.keys()) >= set(raters_list)]
    complete_pids.sort()
    print(f"Run {args.run_id}: {len(by_proj)} projects seen, {len(complete_pids)} complete across {n_raters} raters")

    if not complete_pids:
        raise SystemExit("no fully-rated projects; did the run finish?")

    # --- Per-dimension matrices ---
    dim_matrix: dict[str, list[list[float]]] = {d: [] for d in DIMS}
    composites: list[list[float]] = []
    grades: list[list[str]] = []
    dqflags: list[list[list[str]]] = []  # [pid][rater] = list of flags
    mode_matrix: list[list[str]] = []

    for pid in complete_pids:
        per_dim = {d: [] for d in DIMS}
        per_comp = []
        per_grade = []
        per_dq = []
        per_mode = []
        for r in raters_list:
            row = by_proj[pid][r]
            scores = row.get("scores") or {}
            for d in DIMS:
                v = scores.get(d)
                if v is None:
                    v = 0
                per_dim[d].append(float(v))
            comp = composite_for(scores, weights)
            dq = row.get("disqualifiers") or []
            nominal = grade_from_composite(comp, bands)
            final = apply_dq_cap(nominal, dq, dq_spec)
            per_comp.append(comp)
            per_grade.append(final)
            per_dq.append(dq)
            per_mode.append(row.get("mode", "unknown"))
        for d in DIMS:
            dim_matrix[d].append(per_dim[d])
        composites.append(per_comp)
        grades.append(per_grade)
        dqflags.append(per_dq)
        mode_matrix.append(per_mode)

    # --- Per-dimension Fleiss' κ with 10-bucket binning ---
    N_BUCKETS = 10
    per_dim_fleiss = {}
    for d in DIMS:
        mat = []
        for vec in dim_matrix[d]:
            row = [0] * N_BUCKETS
            for v in vec:
                b = min(N_BUCKETS - 1, int(v) // 10)
                row[b] += 1
            mat.append(row)
        per_dim_fleiss[d] = fleiss_kappa(mat, N_BUCKETS)

    # --- Grade-level Fleiss' κ ---
    grade_matrix = []
    for row in grades:
        bucket = [0] * len(GRADES)
        for g in row:
            bucket[GRADE_INDEX[g]] += 1
        grade_matrix.append(bucket)
    grade_fleiss = fleiss_kappa(grade_matrix, len(GRADES))

    # --- ICC(2,k) on composite ---
    composite_icc = icc_2k(composites)

    # --- Pairwise Cohen's κ + exact agreement on grade ---
    pairwise = []
    grade_ints = [[GRADE_INDEX[g] for g in row] for row in grades]
    for i in range(len(raters_list)):
        for j in range(i + 1, len(raters_list)):
            a = [grade_ints[k][i] for k in range(len(complete_pids))]
            b = [grade_ints[k][j] for k in range(len(complete_pids))]
            k_val = cohens_kappa(a, b, len(GRADES))
            exact = sum(1 for x in range(len(a)) if a[x] == b[x]) / len(a)
            within1 = sum(1 for x in range(len(a)) if abs(a[x] - b[x]) <= 1) / len(a)
            pairwise.append({
                "a": raters_list[i], "b": raters_list[j],
                "cohens_kappa": k_val, "exact": exact, "within_1": within1,
            })

    # --- External correlation ---
    external = load_external()
    ext_pairs: dict[str, list[tuple[float, float]]] = defaultdict(list)
    # Panel-median composite per project vs agency scale
    for k_idx, pid in enumerate(complete_pids):
        raw = pid.split("_", 1)[1]
        ext = external.get(raw)
        if not ext:
            continue
        # Panel median composite
        pc = sorted(composites[k_idx])[len(composites[k_idx]) // 2]
        for agency, scale in (("bezero", BEZERO_SCALE), ("calyx", CALYX_SCALE), ("sylvera", SYLVERA_SCALE)):
            tag = ext["agency_ratings"].get(agency)
            if tag in scale:
                ext_pairs[agency].append((pc, scale[tag]))

    ext_corr = {}
    for agency, pairs in ext_pairs.items():
        if len(pairs) >= 3:
            xs = [p[0] for p in pairs]
            ys = [p[1] for p in pairs]
            ext_corr[agency] = {
                "n": len(pairs),
                "pearson": pearson(xs, ys),
                "spearman": spearman(xs, ys),
            }
        else:
            ext_corr[agency] = {"n": len(pairs), "pearson": None, "spearman": None,
                                "note": "insufficient overlap"}

    # --- Adversarial injection check (if stress-run provided) ---
    stress_summary = None
    if args.stress_run_id:
        try:
            stress_rows = load_rows(args.stress_run_id)
        except SystemExit:
            stress_rows = []
        stress_by = defaultdict(dict)
        for r in stress_rows:
            pid = r["project_ref"]["project_id"]
            stress_by[pid][r["rater_model"]] = r
        expected = {s["project_ref"]["project_id"]: s["expected_disqualifier"] for s in STRESS_TESTS}
        stress_results = []
        total = 0; hit = 0
        for pid, exp in expected.items():
            row = {"project_id": pid, "expected": exp, "recall_by_model": {}}
            for rater, rec in stress_by.get(pid, {}).items():
                flags = rec.get("disqualifiers", []) or []
                ok = exp in flags
                row["recall_by_model"][rater] = {"flags": flags, "hit": ok}
                total += 1
                if ok:
                    hit += 1
            stress_results.append(row)
        stress_summary = {
            "overall_recall": (hit / total) if total else None,
            "total_attempts": total,
            "hits": hit,
            "per_credit": stress_results,
        }

    # --- Write outputs ---
    run_dir = RUNS_DIR / args.run_id
    per_proj_path = run_dir / "per_project_composites.csv"
    with per_proj_path.open("w", newline="") as f:
        w = csv.writer(f)
        header = ["project"] + [f"{r}_composite" for r in raters_list] + [f"{r}_grade" for r in raters_list] + [f"{r}_mode" for r in raters_list]
        w.writerow(header)
        for k_idx, pid in enumerate(complete_pids):
            row = [pid] + [round(composites[k_idx][i], 2) for i in range(n_raters)] + list(grades[k_idx]) + list(mode_matrix[k_idx])
            w.writerow(row)

    n_live = sum(1 for row in mode_matrix for m in row if m == "live")
    n_synth = sum(1 for row in mode_matrix for m in row if m == "synthetic-archetype-fallback")
    dry_run = n_live == 0

    summary = {
        "run_id": args.run_id,
        "raters": raters_list,
        "n_projects_complete": len(complete_pids),
        "n_live_rows": n_live,
        "n_synthetic_rows": n_synth,
        "DRY_RUN_WARNING": (
            "ALL ROWS ARE SYNTHETIC ARCHETYPE FALLBACK. Metrics below do NOT "
            "measure LLM inter-rater agreement — they measure the deterministic "
            "stub's self-consistency. Set ANTHROPIC_API_KEY and re-run to get "
            "real Claude panel scores." if dry_run else None
        ),
        "grade_fleiss_kappa": grade_fleiss,
        "composite_icc_2k": composite_icc,
        "per_dimension_fleiss": per_dim_fleiss,
        "pairwise_grade_agreement": pairwise,
        "external_correlation": ext_corr,
        "stress_test_recall": stress_summary,
    }
    (run_dir / "validation_summary.json").write_text(json.dumps(summary, indent=2, default=str))

    # Human report
    print()
    print("=" * 60)
    print(f" Validation summary: {args.run_id}")
    print("=" * 60)
    if dry_run:
        print("  *** DRY-RUN: zero live rows. Metrics reflect synthetic stub ***")
        print("  *** self-consistency only, NOT LLM inter-rater agreement.    ***")
    print(f"  raters:                 {raters_list}")
    print(f"  projects complete:      {len(complete_pids)}")
    print(f"  live/synthetic rows:    {summary['n_live_rows']}/{summary['n_synthetic_rows']}")
    print(f"  grade Fleiss κ:         {grade_fleiss:+.3f}")
    print(f"  composite ICC(2,k):     {composite_icc:+.3f}")
    print(f"  per-dim Fleiss κ:")
    for d, k in per_dim_fleiss.items():
        print(f"    {d:22s} {k:+.3f}")
    print(f"  pairwise Cohen's κ:")
    for p in pairwise:
        print(f"    {p['a']:30s} vs {p['b']:30s} κ={p['cohens_kappa']:+.3f} exact={p['exact']:.0%} ±1={p['within_1']:.0%}")
    print(f"  external correlation:")
    for agency, c in ext_corr.items():
        if c.get("pearson") is not None:
            print(f"    {agency:10s} n={c['n']} pearson={c['pearson']:+.3f} spearman={c['spearman']:+.3f}")
        else:
            print(f"    {agency:10s} n={c['n']} (insufficient overlap)")
    if stress_summary:
        print(f"  stress-test recall:     {stress_summary['hits']}/{stress_summary['total_attempts']}")
    print()
    print(f"  wrote: {run_dir / 'validation_summary.json'}")
    print(f"  wrote: {per_proj_path}")


if __name__ == "__main__":
    main()
