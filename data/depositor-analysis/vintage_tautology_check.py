#!/usr/bin/env python3
"""
Critical methodological check: the paper's partial correlation analysis claims the
temporal quality decline REVERSES (rho = -0.50 -> +0.60) once vintage is partialled out.
But vintage (as `vintage_year`) is itself a dimension of the composite score (weight 0.10).
Controlling for a component of the dependent variable is tautological.

This script:
  1) Confirms the scoring rubric WEIGHTS from claude_opus_score.py
  2) Recomputes each project's composite WITHOUT the vintage_year dimension,
     redistributing the 0.10 weight proportionally across the other 6 active dimensions
     (co_benefits has weight 0 in the rubric, so it stays at 0).
  3) Joins projects -> tCO2 tokens via tco2_metadata.json
  4) Filters BCT deposits to the renewable subset with recoverable vintage
  5) Computes:
        - block vs vintage-free composite   (Spearman + Kendall)
        - vintage vs vintage-free composite (Spearman + Kendall)
        - partial corr block vs vintage-free composite | vintage (both metrics)
  6) Compares to the "original" composite (with vintage) as a sanity check.
  7) Saves tco2_scores_novintage.json and vintage_tautology_check.json.
"""

import json
import math
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy.stats import spearmanr, kendalltau, rankdata

ROOT = Path("/Users/adelinewen/carbon-neutrality")
PANEL_PATH = ROOT / "data/llm-panel-claude-opus/panel_scores.jsonl"
META_PATH = ROOT / "data/depositor-analysis/tco2_metadata.json"
DEPOSITS_PATH = ROOT / "data/depositor-analysis/bct_deposits_enriched.json"
OUT_NOVINT = ROOT / "data/depositor-analysis/tco2_scores_novintage.json"
OUT_CHECK = ROOT / "data/depositor-analysis/vintage_tautology_check.json"

# ------- 1. rubric weights -------
WEIGHTS_ORIG = {
    "removal_type": 0.25,
    "additionality": 0.20,
    "permanence": 0.175,
    "mrv_grade": 0.20,
    "vintage_year": 0.10,
    "co_benefits": 0.00,
    "registry_methodology": 0.075,
}
# active dimensions excluding vintage_year AND co_benefits (which already has w=0)
ACTIVE_EXCL_VINTAGE = [
    "removal_type", "additionality", "permanence", "mrv_grade", "registry_methodology"
]
total_active = sum(WEIGHTS_ORIG[k] for k in ACTIVE_EXCL_VINTAGE)  # 0.9
# redistribute the 0.10 vintage weight proportionally: each w -> w / total_active
WEIGHTS_NOVINT = {k: WEIGHTS_ORIG[k] / total_active for k in ACTIVE_EXCL_VINTAGE}
WEIGHTS_NOVINT["co_benefits"] = 0.0  # explicit
WEIGHTS_NOVINT["vintage_year"] = 0.0

print("Weights (no-vintage, redistributed across 5 active dims + co_benefits=0):")
for k, v in WEIGHTS_NOVINT.items():
    print(f"  {k}: {v:.4f}")
assert abs(sum(WEIGHTS_NOVINT.values()) - 1.0) < 1e-9, "weights must sum to 1"

# Match prompt: removal=0.2778, additionality=0.2222, permanence=0.1944, mrv=0.2222, registry=0.0833
expected = {
    "removal_type": 0.2778,
    "additionality": 0.2222,
    "permanence": 0.1944,
    "mrv_grade": 0.2222,
    "registry_methodology": 0.0833,
}
for k, v in expected.items():
    assert abs(WEIGHTS_NOVINT[k] - v) < 0.001, f"{k} weight mismatch"
print("Redistributed weights match spec.\n")


# ------- 2. recompute composites without vintage -------
projects = {}
with open(PANEL_PATH) as f:
    for line in f:
        r = json.loads(line)
        projects[str(r["project_id"])] = r


def composite_no_vintage(scores):
    return sum(scores[k] * WEIGHTS_NOVINT[k] for k in WEIGHTS_NOVINT)


# also recompute original composite for sanity
def composite_orig(scores):
    return sum(scores[k] * WEIGHTS_ORIG[k] for k in WEIGHTS_ORIG)


# ------- 3. join to tCO2 tokens via metadata -------
with open(META_PATH) as f:
    tco2_meta = json.load(f)

tco2_novint = {}
drops_no_project = 0
drops_no_score = 0
for addr, meta in tco2_meta.items():
    pid = str(meta.get("project_id"))
    if not pid:
        drops_no_project += 1
        continue
    rec = projects.get(pid)
    if rec is None:
        drops_no_score += 1
        continue
    scores = rec["scores"]
    c_nv = composite_no_vintage(scores)
    c_or = composite_orig(scores)
    # vintage parsing: first 4 digits
    v_raw = str(meta.get("vintage") or "")
    try:
        vy = int(v_raw[:4])
    except Exception:
        vy = None
    tco2_novint[addr] = {
        "project_id": pid,
        "type": rec["type"],
        "vintage": vy,
        "composite_orig": round(c_or, 3),
        "composite_novintage": round(c_nv, 3),
        "scores": scores,
    }

print(f"tCO2 tokens joined: {len(tco2_novint)}")
print(f"  dropped (no project_id): {drops_no_project}")
print(f"  dropped (no panel score): {drops_no_score}\n")

with open(OUT_NOVINT, "w") as f:
    json.dump(tco2_novint, f, indent=2)
print(f"Wrote {OUT_NOVINT}\n")


# ------- 4. BCT deposits: filter renewables with recoverable vintage -------
with open(DEPOSITS_PATH) as f:
    deposits = json.load(f)

print(f"Total BCT deposits: {len(deposits)}")

rows_all = []
rows_renew = []
for d in deposits:
    addr = d["tco2_address"]
    rec = tco2_novint.get(addr)
    if rec is None:
        continue
    if rec["vintage"] is None:
        continue
    row = {
        "block": d["block_number"],
        "vintage": rec["vintage"],
        "type": rec["type"],
        "composite_orig": rec["composite_orig"],
        "composite_novintage": rec["composite_novintage"],
        "tonnes": d["amount_tonnes"],
    }
    rows_all.append(row)
    if rec["type"] == "Renewable":
        rows_renew.append(row)

print(f"Deposits with joined score+vintage: {len(rows_all)}")
print(f"Renewable-only deposits: {len(rows_renew)}\n")


# ------- 5. Correlation + partial correlation helpers -------
def partial_corr_from_pearson_on_ranks(x, y, z, method="spearman"):
    """Partial correlation of x,y controlling for z, computed as the Pearson
    correlation of the residuals after ranking (Spearman) or directly (Kendall
    is handled separately).  For Spearman we use rank-transform then Pearson
    partial (the standard Spearman partial corr formula).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    z = np.asarray(z, dtype=float)
    if method == "spearman":
        x = rankdata(x)
        y = rankdata(y)
        z = rankdata(z)
    # Pearson partial correlation formula
    def pear(a, b):
        a = a - a.mean()
        b = b - b.mean()
        denom = math.sqrt((a * a).sum() * (b * b).sum())
        if denom == 0:
            return float("nan")
        return float((a * b).sum() / denom)
    rxy = pear(x, y)
    rxz = pear(x, z)
    ryz = pear(y, z)
    denom = math.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
    if denom == 0:
        return float("nan"), rxy, rxz, ryz
    return (rxy - rxz * ryz) / denom, rxy, rxz, ryz


def partial_kendall(x, y, z):
    """Partial Kendall tau using the standard tau-based partial formula
    tau(xy|z) = (tau_xy - tau_xz * tau_yz) / sqrt((1-tau_xz^2)(1-tau_yz^2))
    (Kendall 1942). Not identical to Pearson-on-ranks; reported for robustness.
    """
    tau_xy, _ = kendalltau(x, y)
    tau_xz, _ = kendalltau(x, z)
    tau_yz, _ = kendalltau(y, z)
    denom = math.sqrt(max(0.0, (1 - tau_xz ** 2) * (1 - tau_yz ** 2)))
    if denom == 0:
        return float("nan"), tau_xy, tau_xz, tau_yz
    return (tau_xy - tau_xz * tau_yz) / denom, tau_xy, tau_xz, tau_yz


def analyze(label, rows):
    if len(rows) < 3:
        return {"label": label, "n": len(rows), "error": "too few rows"}
    block = np.array([r["block"] for r in rows], dtype=float)
    vintage = np.array([r["vintage"] for r in rows], dtype=float)
    comp_nv = np.array([r["composite_novintage"] for r in rows], dtype=float)
    comp_or = np.array([r["composite_orig"] for r in rows], dtype=float)

    out = {"label": label, "n": len(rows)}

    # pairwise Spearman
    out["spearman"] = {}
    rho, p = spearmanr(block, comp_nv);   out["spearman"]["block_vs_novintage"]   = {"rho": float(rho), "p": float(p)}
    rho, p = spearmanr(vintage, comp_nv); out["spearman"]["vintage_vs_novintage"] = {"rho": float(rho), "p": float(p)}
    rho, p = spearmanr(block, vintage);   out["spearman"]["block_vs_vintage"]     = {"rho": float(rho), "p": float(p)}
    rho, p = spearmanr(block, comp_or);   out["spearman"]["block_vs_orig"]        = {"rho": float(rho), "p": float(p)}
    rho, p = spearmanr(vintage, comp_or); out["spearman"]["vintage_vs_orig"]      = {"rho": float(rho), "p": float(p)}

    # Spearman partial correlations (rank then Pearson partial formula)
    pc_nv, rxy, rxz, ryz = partial_corr_from_pearson_on_ranks(block, comp_nv, vintage, "spearman")
    out["spearman"]["partial_block_vs_novintage__control_vintage"] = {
        "rho": pc_nv, "marginal_block_vs_nv": rxy,
        "block_vs_vintage": rxz, "novintage_vs_vintage": ryz,
    }
    pc_or, rxy2, rxz2, ryz2 = partial_corr_from_pearson_on_ranks(block, comp_or, vintage, "spearman")
    out["spearman"]["partial_block_vs_orig__control_vintage"] = {
        "rho": pc_or, "marginal_block_vs_orig": rxy2,
        "block_vs_vintage": rxz2, "orig_vs_vintage": ryz2,
    }

    # Kendall
    out["kendall"] = {}
    tau, p = kendalltau(block, comp_nv);   out["kendall"]["block_vs_novintage"]   = {"tau": float(tau), "p": float(p)}
    tau, p = kendalltau(vintage, comp_nv); out["kendall"]["vintage_vs_novintage"] = {"tau": float(tau), "p": float(p)}
    tau, p = kendalltau(block, vintage);   out["kendall"]["block_vs_vintage"]     = {"tau": float(tau), "p": float(p)}
    tau, p = kendalltau(block, comp_or);   out["kendall"]["block_vs_orig"]        = {"tau": float(tau), "p": float(p)}
    tau, p = kendalltau(vintage, comp_or); out["kendall"]["vintage_vs_orig"]      = {"tau": float(tau), "p": float(p)}
    pk_nv, t_xy, t_xz, t_yz = partial_kendall(block, comp_nv, vintage)
    out["kendall"]["partial_block_vs_novintage__control_vintage"] = {
        "tau": pk_nv, "marginal_block_vs_nv": t_xy,
        "block_vs_vintage": t_xz, "novintage_vs_vintage": t_yz,
    }
    pk_or, t_xy2, t_xz2, t_yz2 = partial_kendall(block, comp_or, vintage)
    out["kendall"]["partial_block_vs_orig__control_vintage"] = {
        "tau": pk_or, "marginal_block_vs_orig": t_xy2,
        "block_vs_vintage": t_xz2, "orig_vs_vintage": t_yz2,
    }
    return out


result_renew = analyze("renewable_only", rows_renew)
result_all = analyze("all_types", rows_all)

# Also de-duplicate to project-level rows (one row per tCO2 token, ignoring volume)
# to rule out weighting artifacts.
# Rebuild properly including address for token-level uniqueness
# (rows_renew above doesn't carry tco2 address, so re-iterate deposits)
rows_all2, rows_renew2 = [], []
for d in deposits:
    addr = d["tco2_address"]
    rec = tco2_novint.get(addr)
    if rec is None or rec["vintage"] is None:
        continue
    row = {
        "addr": addr, "block": d["block_number"], "vintage": rec["vintage"],
        "type": rec["type"], "composite_orig": rec["composite_orig"],
        "composite_novintage": rec["composite_novintage"], "tonnes": d["amount_tonnes"],
    }
    rows_all2.append(row)
    if rec["type"] == "Renewable":
        rows_renew2.append(row)

# Token-level aggregation: one row per (addr), using earliest block as deposit proxy
agg_renew = {}
for r in rows_renew2:
    a = r["addr"]
    if a not in agg_renew or r["block"] < agg_renew[a]["block"]:
        agg_renew[a] = r
rows_renew_tokenlvl = list(agg_renew.values())
result_renew_tokenlvl = analyze("renewable_token_level_earliest_block", rows_renew_tokenlvl)

summary = {
    "weights_orig": WEIGHTS_ORIG,
    "weights_novintage_redistributed": WEIGHTS_NOVINT,
    "n_projects_scored": len(projects),
    "n_tco2_tokens_scored": len(tco2_novint),
    "n_deposits_with_vintage": len(rows_all),
    "n_renewable_deposits": len(rows_renew),
    "n_renewable_tokens_unique": len(rows_renew_tokenlvl),
    "results": {
        "renewable_deposits": result_renew,
        "all_deposits": result_all,
        "renewable_token_level": result_renew_tokenlvl,
    },
}

with open(OUT_CHECK, "w") as f:
    json.dump(summary, f, indent=2, default=float)

print(f"Wrote {OUT_CHECK}\n")

# ------- 6. Human-readable summary -------
def show(r):
    print(f"--- {r['label']}  (n={r['n']}) ---")
    s = r["spearman"]; k = r["kendall"]
    print("Spearman:")
    print(f"  block vs composite_orig       : rho = {s['block_vs_orig']['rho']:+.3f}  (p={s['block_vs_orig']['p']:.3g})")
    print(f"  block vs composite_novintage  : rho = {s['block_vs_novintage']['rho']:+.3f}  (p={s['block_vs_novintage']['p']:.3g})")
    print(f"  block vs vintage              : rho = {s['block_vs_vintage']['rho']:+.3f}  (p={s['block_vs_vintage']['p']:.3g})")
    print(f"  vintage vs composite_orig     : rho = {s['vintage_vs_orig']['rho']:+.3f}")
    print(f"  vintage vs composite_novintage: rho = {s['vintage_vs_novintage']['rho']:+.3f}  <-- should be near 0 if vintage was the ONLY channel")
    print(f"  PARTIAL block vs composite_orig | vintage     : rho = {s['partial_block_vs_orig__control_vintage']['rho']:+.3f}")
    print(f"  PARTIAL block vs composite_novintage | vintage: rho = {s['partial_block_vs_novintage__control_vintage']['rho']:+.3f}")
    print("Kendall:")
    print(f"  block vs composite_orig       : tau = {k['block_vs_orig']['tau']:+.3f}")
    print(f"  block vs composite_novintage  : tau = {k['block_vs_novintage']['tau']:+.3f}")
    print(f"  PARTIAL block vs composite_orig | vintage     : tau = {k['partial_block_vs_orig__control_vintage']['tau']:+.3f}")
    print(f"  PARTIAL block vs composite_novintage | vintage: tau = {k['partial_block_vs_novintage__control_vintage']['tau']:+.3f}")
    print()


print("=" * 78)
print("VINTAGE TAUTOLOGY CHECK -- SUMMARY")
print("=" * 78)
show(result_renew)
show(result_all)
show(result_renew_tokenlvl)

# Verdict
pr_nv = result_renew["spearman"]["partial_block_vs_novintage__control_vintage"]["rho"]
pr_or = result_renew["spearman"]["partial_block_vs_orig__control_vintage"]["rho"]
mg_nv = result_renew["spearman"]["block_vs_novintage"]["rho"]
mg_or = result_renew["spearman"]["block_vs_orig"]["rho"]

print("=" * 78)
print("VERDICT (renewable subset):")
print(f"  Marginal block vs composite_orig        rho = {mg_or:+.3f}")
print(f"  Marginal block vs composite_novintage   rho = {mg_nv:+.3f}")
print(f"  Partial  block | vintage, orig          rho = {pr_or:+.3f}")
print(f"  Partial  block | vintage, novintage     rho = {pr_nv:+.3f}")
if pr_nv > 0 and mg_nv < 0:
    verdict = (
        "REVERSAL SURVIVES removal of vintage dimension. "
        "The vintage-drift channel is a real mechanism beyond the rubric's vintage component."
    )
elif pr_nv <= 0 and mg_nv <= 0:
    verdict = (
        "REVERSAL DISAPPEARS once vintage is not double-counted. "
        "Original 'vintage drift as specific channel' claim was (at least partly) a tautological artifact."
    )
else:
    verdict = (
        "Mixed/attenuated result: the reversal weakens substantially when vintage is removed "
        "from the composite. Claim that 'vintage drift is THE specific channel' is not fully defensible."
    )
print(verdict)
print("=" * 78)
