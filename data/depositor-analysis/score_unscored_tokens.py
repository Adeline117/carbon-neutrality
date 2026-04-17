#!/usr/bin/env python3
"""
Fix MNAR (missing-not-at-random) selection bias in tco2_scores_final.json.

Current state: 161/345 BCT tokens scored, 184 unscored. Unscored tokens skew
to newer vintages, creating systematic selection bias.

This script:
  1. Normalizes vintage fields (YYYYMMDD -> YYYY) and writes
     tco2_metadata_fixed.json.
  2. Scores every previously-unscored BCT token using the same archetype
     + country/vintage/methodology rules encoded in
     data/llm-panel-claude-opus/claude_opus_score.py.
  3. Attempts to score the 4 NCT-only tokens (not present in BCT metadata)
     by pulling name/vintage from available sources; where impossible, flags
     them with source="imputed_default".
  4. Writes tco2_scores_complete.json with a `source` field distinguishing
     original 161 vs newly imputed scores.
  5. Writes scoring_coverage_report.json with volume-weighted means,
     Spearman correlations, and grade distributions before/after.

Run: python3 score_unscored_tokens.py
"""
from __future__ import annotations

import json
import math
import statistics
from collections import Counter
from pathlib import Path

HERE = Path("/Users/adelinewen/carbon-neutrality/data/depositor-analysis")
META_PATH           = HERE / "tco2_metadata.json"
SCORES_IN_PATH      = HERE / "tco2_scores_final.json"
CLASS_PATH          = HERE / "project_classification_final.json"
BCT_DEPOSITS_PATH   = HERE / "bct_deposits_complete.json"
NCT_DEPOSITS_PATH   = HERE / "nct_deposits.json"

META_FIXED_PATH     = HERE / "tco2_metadata_fixed.json"
SCORES_OUT_PATH     = HERE / "tco2_scores_complete.json"
REPORT_PATH         = HERE / "scoring_coverage_report.json"

# ─── Step 1: Normalize vintage field ─────────────────────────────────────────

def normalize_vintage(raw: str) -> str:
    s = str(raw or "").strip()
    if len(s) > 4 and s[:4].isdigit():
        return s[:4]
    return s


def load_and_fix_metadata() -> tuple[dict, int]:
    meta = json.loads(META_PATH.read_text())
    fixed_count = 0
    for addr, m in meta.items():
        raw = m.get("vintage", "")
        norm = normalize_vintage(raw)
        if norm != str(raw):
            fixed_count += 1
        m["vintage"] = norm
    META_FIXED_PATH.write_text(json.dumps(meta, indent=2))
    return meta, fixed_count


# ─── Step 2: Scoring rules (ported from claude_opus_score.py) ────────────────

KNOWN_ISSUES = {
    "934":  {"flag": "Mai Ndombe: baseline inflation", "adj_additionality": -15, "adj_mrv_grade": -10},
    "674":  {"flag": "Rimba Raya: CarbonPlan investigation", "adj_permanence": -10, "adj_additionality": -10},
    "985":  {"flag": "Cordillera Azul: West 2023 overcredit", "adj_additionality": -15, "adj_mrv_grade": -10},
    "868":  {"flag": "Brazil Nut Concessions: baseline questionable", "adj_additionality": -20, "adj_mrv_grade": -15},
    "902":  {"flag": "Kariba REDD+: BeZero D", "adj_additionality": -20, "adj_permanence": -15, "adj_mrv_grade": -15},
    "1094": {"flag": "Ecomapua: CMW integrity flag", "adj_additionality": -10, "adj_mrv_grade": -10},
    "1382": {"flag": "Envira Amazonia: baseline concerns", "adj_additionality": -10},
    "1650": {"flag": "Keo Seima: buffer concerns", "adj_additionality": -5},
    "1748": {"flag": "Southern Cardamom: human rights concerns", "adj_additionality": -10, "disqualifier": "human_rights"},
}


def _vy(vintage: str, default: int = 2015) -> int:
    s = str(vintage or "")
    try:
        return int(s[:4])
    except ValueError:
        return default


def score_renewable(name: str, pid: str, vintage: str) -> dict:
    n = (name or "").upper()
    vy = _vy(vintage)
    s = {
        "removal_type": 32,
        "additionality": 25,
        "permanence": 5,
        "mrv_grade": 55,
        "vintage_year": max(0, 100 - (2022 - vy) * 12),
        "co_benefits": 30,
        "registry_methodology": 40,
    }
    if any(k in n for k in ["CHINA", "CHINESE", "YUNNAN", "SICHUAN", "GUANGDONG", "HUNAN", "HEBEI", "GUIZHOU", "GANSU", "SHANDONG", "ZHEJIANG", "HUBEI", "JIANGXI"]):
        s["additionality"] = 15 if vy >= 2012 else 25
        s["registry_methodology"] = 30
    elif any(k in n for k in ["INDIA", "INDIAN", "KARNATAKA", "TAMIL", "MAHARASHTRA", "GUJARAT", "RAJASTHAN", "PUNJAB", "ANDHRA", "HIMACHAL", "UTTARAKHAND"]):
        s["additionality"] = 18 if vy >= 2012 else 25
        s["registry_methodology"] = 32
    elif "TURK" in n or "ANATOLIA" in n or "AKSU" in n or "DERELI" in n or "KUMKOY" in n or "ALKUMRU" in n or "SAMSUN" in n:
        s["additionality"] = 22
    elif "BRAZIL" in n or "BRAZILIAN" in n:
        s["additionality"] = 25
    elif "HYDRO" in n and ("LARGE" in n or "MW" in n):
        s["additionality"] = 15

    if "WIND" in n:
        s["mrv_grade"] = 60
    elif "HYDRO" in n:
        s["mrv_grade"] = 55
        if vy >= 2012 and not any(x in n for x in ["SMALL", "MICRO", "RUN-OF-RIVER"]):
            s["additionality"] -= 5
    elif "SOLAR" in n:
        s["mrv_grade"] = 60
        if vy >= 2013:
            s["additionality"] = max(10, s["additionality"] - 5)
    elif "BIOMASS" in n or "BAGASSE" in n:
        s["additionality"] = 30
        s["co_benefits"] = 45
    elif "GEOTHERMAL" in n:
        s["additionality"] = 45

    if vy >= 2013:
        s["additionality"] = max(10, s["additionality"] - 5)
    return s


def score_redd(name: str, pid: str, vintage: str) -> dict:
    n = (name or "").upper()
    vy = _vy(vintage)
    s = {
        "removal_type": 22,
        "additionality": 35,
        "permanence": 40,
        "mrv_grade": 45,
        "vintage_year": max(0, 100 - (2022 - vy) * 12),
        "co_benefits": 55,
        "registry_methodology": 30,
    }
    if "BRAZIL" in n or "AMAZON" in n:
        s["additionality"] = 40
    elif "ZIMBABWE" in n or "KARIBA" in n:
        s["additionality"] = 20
    elif "DRC" in n or "CONGO" in n or "MAI NDOMBE" in n:
        s["additionality"] = 25
    elif "CAMBODIA" in n or "LAOS" in n or "VIETNAM" in n:
        s["additionality"] = 30
    elif "PERU" in n or "COLOMBIA" in n:
        s["additionality"] = 35
    elif "INDONESIA" in n or "BORNEO" in n or "SUMATRA" in n or "KALIMANTAN" in n:
        s["additionality"] = 30

    if "APD" in n or "AVOIDED PLANNED" in n or "GROUPED" in n:
        s["removal_type"] = 25
        s["additionality"] += 10
        s["mrv_grade"] += 5
    return s


def score_waste_methane(name, pid, vintage):
    vy = _vy(vintage)
    return {
        "removal_type": 50, "additionality": 60, "permanence": 5,
        "mrv_grade": 65, "vintage_year": max(0, 100 - (2022 - vy) * 12),
        "co_benefits": 40, "registry_methodology": 45,
    }


def score_fossil_switch(name, pid, vintage):
    vy = _vy(vintage)
    return {
        "removal_type": 35, "additionality": 18, "permanence": 5,
        "mrv_grade": 55, "vintage_year": max(0, 100 - (2022 - vy) * 12),
        "co_benefits": 20, "registry_methodology": 35,
    }


def score_ifm(name, pid, vintage):
    vy = _vy(vintage)
    return {
        "removal_type": 55, "additionality": 50, "permanence": 55,
        "mrv_grade": 55, "vintage_year": max(0, 100 - (2022 - vy) * 12),
        "co_benefits": 55, "registry_methodology": 45,
    }


def score_arr(name, pid, vintage):
    vy = _vy(vintage)
    return {
        "removal_type": 65, "additionality": 55, "permanence": 50,
        "mrv_grade": 55, "vintage_year": max(0, 100 - (2022 - vy) * 12),
        "co_benefits": 60, "registry_methodology": 45,
    }


def score_industrial_gas(name, pid, vintage):
    vy = _vy(vintage)
    n = (name or "").upper()
    s = {
        "removal_type": 55, "additionality": 40, "permanence": 10,
        "mrv_grade": 75, "vintage_year": max(0, 100 - (2022 - vy) * 12),
        "co_benefits": 15, "registry_methodology": 35,
    }
    if "HFC" in n:
        s["additionality"] = 25
    return s


def score_default(name, pid, vintage, base):
    vy = _vy(vintage)
    base = dict(base)
    base["vintage_year"] = max(0, 100 - (2022 - vy) * 12)
    return base


SCORERS = {
    "Renewable":          score_renewable,
    "REDD+":              score_redd,
    "Waste/Methane":      score_waste_methane,
    "Fossil switch":      score_fossil_switch,
    "IFM":                score_ifm,
    "ARR":                score_arr,
    "Industrial gas":     score_industrial_gas,
    "Industrial":         lambda n,p,v: score_default(n,p,v,{"removal_type":50,"additionality":45,"permanence":5,"mrv_grade":55,"vintage_year":0,"co_benefits":25,"registry_methodology":40}),
    "Cookstove":          lambda n,p,v: score_default(n,p,v,{"removal_type":35,"additionality":40,"permanence":5,"mrv_grade":35,"vintage_year":0,"co_benefits":50,"registry_methodology":40}),
    "Agriculture":        lambda n,p,v: score_default(n,p,v,{"removal_type":40,"additionality":45,"permanence":30,"mrv_grade":45,"vintage_year":0,"co_benefits":50,"registry_methodology":40}),
    "Energy efficiency":  lambda n,p,v: score_default(n,p,v,{"removal_type":40,"additionality":40,"permanence":5,"mrv_grade":50,"vintage_year":0,"co_benefits":35,"registry_methodology":40}),
}

WEIGHTS = {
    "removal_type": 0.25,
    "additionality": 0.20,
    "permanence": 0.175,
    "mrv_grade": 0.20,
    "vintage_year": 0.10,
    "co_benefits": 0.00,
    "registry_methodology": 0.075,
}


def compute_composite(scores: dict) -> float:
    return sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)


def grade_from(c: float, disqualifiers=None) -> str:
    if   c >= 90: g = "AAA"
    elif c >= 75: g = "AA"
    elif c >= 60: g = "A"
    elif c >= 45: g = "BBB"
    elif c >= 30: g = "BB"
    else:         g = "B"
    if disqualifiers:
        cap_order = ["AAA", "AA", "A", "BBB", "BB", "B"]
        for dq in disqualifiers:
            if dq == "human_rights":
                g = "B"
            elif dq in ("community_harm", "biodiversity_harm", "no_third_party"):
                if cap_order.index(g) < cap_order.index("BBB"):
                    g = "BBB"
    return g


def score_project(ptype: str, name: str, pid: str, vintage: str) -> tuple[dict, list[str], str | None]:
    scorer = SCORERS.get(ptype)
    if scorer is None:
        # Fallback archetype
        scores = score_default(name, pid, vintage, {"removal_type":35,"additionality":35,"permanence":20,"mrv_grade":45,"vintage_year":0,"co_benefits":30,"registry_methodology":35})
        ptype_used = "Default"
    else:
        scores = scorer(name, pid, vintage)
        ptype_used = ptype

    disqualifiers: list[str] = []
    flag: str | None = None
    if pid in KNOWN_ISSUES:
        issue = KNOWN_ISSUES[pid]
        for k, v in issue.items():
            if k.startswith("adj_"):
                dim = k[4:]
                if dim in scores:
                    scores[dim] = max(0, scores[dim] + v)
            elif k == "disqualifier":
                disqualifiers.append(v)
            elif k == "flag":
                flag = v
    return scores, disqualifiers, flag


# ─── Step 3: Build complete score table ──────────────────────────────────────

def build_complete_scores(meta: dict, existing_scores: dict, cls: dict) -> dict:
    complete: dict[str, dict] = {}

    # Preserve original 161 scores verbatim (mark source)
    for addr, entry in existing_scores.items():
        out = dict(entry)
        out["source"] = "original"
        complete[addr] = out

    # Impute for every address in meta that lacks a score
    for addr, m in meta.items():
        if addr in complete:
            continue
        pid = m.get("project_id")
        c = cls.get(pid, {})
        ptype = c.get("type") or "Default"
        # Prefer rich classification name; fall back to the token "name"
        rich_name = c.get("name") or m.get("name", "")
        vintage = m.get("vintage", "2015")

        scores, dqs, flag = score_project(ptype, rich_name, pid, vintage)
        composite = compute_composite(scores)
        grade = grade_from(composite, dqs)

        complete[addr] = {
            "composite": round(composite, 2),
            "grade": grade,
            "type": ptype,
            "vintage": _vy(vintage),
            "source": "imputed",
            "scores_detail": scores,
            "disqualifiers": dqs,
            "flag": flag,
            "imputed_from": {
                "project_id": pid,
                "classification_type": ptype,
                "name_used": rich_name,
            },
        }
    return complete


# ─── Step 4: Handle NCT-only tokens (4 addresses outside BCT metadata) ───────

def handle_nct_only(nct_addrs: set[str], complete: dict) -> list[str]:
    """Ensure every NCT token has an entry. For addresses lacking metadata we
    emit an imputed_default placeholder score so coverage is 35/35."""
    added: list[str] = []
    for addr in nct_addrs:
        if addr in complete:
            continue
        scores = {"removal_type":35,"additionality":35,"permanence":20,"mrv_grade":45,"vintage_year":0,"co_benefits":30,"registry_methodology":35}
        composite = compute_composite(scores)
        grade = grade_from(composite)
        complete[addr] = {
            "composite": round(composite, 2),
            "grade": grade,
            "type": "Unknown (AFOLU)",
            "vintage": None,
            "source": "imputed_default",
            "scores_detail": scores,
            "disqualifiers": [],
            "flag": "NCT-only token, no BCT metadata available; default archetype assigned",
            "imputed_from": {"project_id": None, "classification_type": None, "name_used": None},
        }
        added.append(addr)
    return added


# ─── Step 5: Verification / reporting ────────────────────────────────────────

def spearman_rho(xs: list[float], ys: list[float]) -> tuple[float, int]:
    """Spearman's rho via rank correlation. Returns (rho, n)."""
    n = len(xs)
    if n < 2:
        return (float("nan"), n)

    def rank(arr):
        idx = sorted(range(len(arr)), key=lambda i: arr[i])
        ranks = [0.0] * len(arr)
        i = 0
        while i < len(arr):
            j = i
            while j + 1 < len(arr) and arr[idx[j + 1]] == arr[idx[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[idx[k]] = avg
            i = j + 1
        return ranks

    rx = rank(xs)
    ry = rank(ys)
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = math.sqrt(sum((v - mx) ** 2 for v in rx))
    dy = math.sqrt(sum((v - my) ** 2 for v in ry))
    if dx == 0 or dy == 0:
        return (float("nan"), n)
    return (num / (dx * dy), n)


def vol_weighted_stats(deposits, score_table, only_source=None):
    total_t = 0.0
    weighted = 0.0
    grade_tonnes = Counter()
    xs_block, ys_q = [], []
    for d in deposits:
        addr = d["tco2_address"].lower()
        if addr not in score_table:
            continue
        s = score_table[addr]
        if only_source and s.get("source") != only_source:
            continue
        comp = s["composite"]
        t = d["amount_tonnes"]
        weighted += comp * t
        total_t += t
        grade_tonnes[s["grade"]] += t
        xs_block.append(d["block_number"])
        ys_q.append(comp)
    wmean = (weighted / total_t) if total_t > 0 else float("nan")
    rho, n = spearman_rho(xs_block, ys_q) if xs_block else (float("nan"), 0)
    return {
        "n_scored_deposits": n,
        "total_tonnes": total_t,
        "volume_weighted_mean": wmean,
        "spearman_rho_block_vs_quality": rho,
        "grade_tonnes": dict(grade_tonnes),
    }


def grade_distribution(score_table, source_filter=None):
    dist = Counter()
    for v in score_table.values():
        if source_filter and v.get("source") != source_filter:
            continue
        dist[v["grade"]] += 1
    return dict(dist)


def main():
    print("─── Step 1: normalize vintages ───")
    meta, vintage_fixed = load_and_fix_metadata()
    print(f"Normalized {vintage_fixed} vintage fields out of {len(meta)} entries")
    print(f"Wrote {META_FIXED_PATH}")

    existing = json.loads(SCORES_IN_PATH.read_text())
    cls      = json.loads(CLASS_PATH.read_text())
    print(f"Loaded existing scores: {len(existing)}")
    print(f"Loaded project classifications: {len(cls)}")

    print("\n─── Step 2: score previously-unscored BCT tokens ───")
    complete = build_complete_scores(meta, existing, cls)
    n_original = sum(1 for v in complete.values() if v.get("source") == "original")
    n_imputed  = sum(1 for v in complete.values() if v.get("source") == "imputed")
    print(f"Tokens scored: {len(complete)} (original={n_original}, imputed={n_imputed})")

    print("\n─── Step 3: fold in NCT-only tokens ───")
    nct_deposits = json.loads(NCT_DEPOSITS_PATH.read_text())
    nct_addrs = {d["tco2_address"].lower() for d in nct_deposits}
    added = handle_nct_only(nct_addrs, complete)
    print(f"NCT-only tokens given default score: {len(added)}")
    print(f"Total tokens in complete table: {len(complete)}")

    SCORES_OUT_PATH.write_text(json.dumps(complete, indent=2))
    print(f"Wrote {SCORES_OUT_PATH}")

    print("\n─── Step 4: coverage/bias report ───")
    bct_deposits = json.loads(BCT_DEPOSITS_PATH.read_text())

    # Coverage
    bct_addrs = {d["tco2_address"].lower() for d in bct_deposits}
    bct_covered_all = sum(1 for a in bct_addrs if a in complete)
    nct_covered_all = sum(1 for a in nct_addrs if a in complete)

    # Vintage medians (scored vs imputed)
    scored_v = [v["vintage"] for v in complete.values() if v.get("source") == "original" and isinstance(v.get("vintage"), int)]
    imputed_v = [v["vintage"] for v in complete.values() if v.get("source") == "imputed" and isinstance(v.get("vintage"), int)]

    # BCT volume-weighted stats: original-only vs all
    bct_all    = vol_weighted_stats(bct_deposits, complete)
    bct_orig   = vol_weighted_stats(bct_deposits, complete, only_source="original")
    nct_all    = vol_weighted_stats(nct_deposits, complete)
    nct_orig   = vol_weighted_stats(nct_deposits, complete, only_source="original")

    report = {
        "generated": "2026-04-16",
        "step1_vintage_normalization": {
            "entries_total": len(meta),
            "entries_normalized": vintage_fixed,
            "output_file": str(META_FIXED_PATH),
        },
        "token_coverage": {
            "bct_unique_addresses":       len(bct_addrs),
            "bct_scored_total":           bct_covered_all,
            "nct_unique_addresses":       len(nct_addrs),
            "nct_scored_total":           nct_covered_all,
            "original_scored_count":      n_original,
            "imputed_score_count":        n_imputed,
            "nct_only_default_count":     len(added),
            "output_file":                str(SCORES_OUT_PATH),
        },
        "vintage_distribution": {
            "original_scored_n":        len(scored_v),
            "original_scored_median":   statistics.median(scored_v) if scored_v else None,
            "original_scored_mean":     round(statistics.mean(scored_v), 2) if scored_v else None,
            "imputed_n":                len(imputed_v),
            "imputed_median":           statistics.median(imputed_v) if imputed_v else None,
            "imputed_mean":             round(statistics.mean(imputed_v), 2) if imputed_v else None,
        },
        "bct_volume_weighted": {
            "all_tokens_345":     bct_all,
            "original_only_161":  bct_orig,
            "vol_weighted_delta": round((bct_all["volume_weighted_mean"] or 0) - (bct_orig["volume_weighted_mean"] or 0), 4),
            "spearman_delta":     round((bct_all["spearman_rho_block_vs_quality"] or 0) - (bct_orig["spearman_rho_block_vs_quality"] or 0), 4),
        },
        "nct_volume_weighted": {
            "all_tokens_35":    nct_all,
            "original_only":    nct_orig,
        },
        "grade_distribution_counts": {
            "all":      grade_distribution(complete),
            "original": grade_distribution(complete, "original"),
            "imputed":  grade_distribution(complete, "imputed"),
        },
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2))
    print(f"Wrote {REPORT_PATH}")

    # Print concise summary
    print("\n================ KEY RESULTS ================")
    print(f"BCT coverage:  {bct_covered_all}/{len(bct_addrs)}   (was 161/345)")
    print(f"NCT coverage:  {nct_covered_all}/{len(nct_addrs)}")
    print(f"")
    print(f"BCT vol-weighted mean (ALL tokens):       {bct_all['volume_weighted_mean']:.3f} over {bct_all['n_scored_deposits']} deposits, {bct_all['total_tonnes']:,.0f} t")
    print(f"BCT vol-weighted mean (ORIGINAL 161 only): {bct_orig['volume_weighted_mean']:.3f} over {bct_orig['n_scored_deposits']} deposits, {bct_orig['total_tonnes']:,.0f} t")
    print(f"Delta (ALL - ORIGINAL):                   {bct_all['volume_weighted_mean'] - bct_orig['volume_weighted_mean']:+.3f}")
    print(f"")
    print(f"BCT Spearman rho block vs quality:")
    print(f"  ALL tokens:      rho = {bct_all['spearman_rho_block_vs_quality']:+.4f}  (n = {bct_all['n_scored_deposits']})")
    print(f"  ORIGINAL 161:    rho = {bct_orig['spearman_rho_block_vs_quality']:+.4f}  (n = {bct_orig['n_scored_deposits']})")
    print(f"  Delta:           {bct_all['spearman_rho_block_vs_quality'] - bct_orig['spearman_rho_block_vs_quality']:+.4f}")
    print(f"")
    print("Grade distribution (tokens):")
    for g in ["AAA","AA","A","BBB","BB","B"]:
        a = report["grade_distribution_counts"]["all"].get(g, 0)
        o = report["grade_distribution_counts"]["original"].get(g, 0)
        i = report["grade_distribution_counts"]["imputed"].get(g, 0)
        print(f"  {g:>4}: all={a:>3}  original={o:>3}  imputed={i:>3}")


if __name__ == "__main__":
    main()
