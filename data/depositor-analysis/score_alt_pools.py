#!/usr/bin/env python3
"""
score_alt_pools.py
==================

Score C3 (UBO + NBO) and Moss MCO2 carbon credits using the SAME
methodology-archetype rubric that was used for BCT/NCT tokens
(see score_unscored_tokens.py and data/methodology-ratings/archetypes.json).

Inputs
------
- alternative_pool_events.json    : ubo_mints, ubo_deposits, nbo_deposits (C3),
                                     mco2_mints (Moss MCO2).
- ../methodology-ratings/archetypes.json : methodology archetype score profiles.
- independent_control_search.json : documented pool-level quality filters /
                                     composition (the only project-type signal
                                     that exists for these pools).

IMPORTANT DATA-QUALITY NOTE
---------------------------
The C3/MCO2 event records contain ONLY (block_number, contract/recipient,
amount, tx_hash). They carry NO per-token project-type, methodology, project
name, or vintage. An exhaustive repo search (transfer_cache/, tco2_metadata*,
project_classification*, lemons-index/, tokenized-pilot/) found NO file that
resolves a C3T contract address or an MCO2 recipient to an underlying project,
methodology, or vintage.

Consequently we CANNOT assign a distinct methodology archetype per individual
C3T/MCO2 token from on-chain data alone. To avoid fabricating per-token detail,
we score at the level the data supports:

  * Each pool is scored against its DOCUMENTED methodology composition
    (from independent_control_search.json quality_filter / mechanism fields),
    mapped onto the existing archetype rubric.
  * Per-deposit composite scores are emitted in block order, but because
    per-token type/vintage is unobserved they reflect the pool archetype
    composition rather than token-specific quality. This limitation is recorded
    explicitly in the "data_gaps" of the output and propagated to
    multipool_comparison.py (which sets the temporal-rho for these pools to
    null where it is not honestly computable).

The same rubric (weights, composite formula, grade bands) as BCT/NCT is reused
verbatim so cross-pool numbers are directly comparable.

Run: python3 score_alt_pools.py
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

HERE = Path("/Users/adelinewen/carbon-neutrality/data/depositor-analysis")
EVENTS_PATH = HERE / "alternative_pool_events.json"
ARCHETYPES_PATH = Path(
    "/Users/adelinewen/carbon-neutrality/data/methodology-ratings/archetypes.json"
)
CONTROL_PATH = HERE / "independent_control_search.json"
OUT_PATH = HERE / "score_alt_pools.json"

# ─── Rubric (identical to score_unscored_tokens.py / scoring-rubrics/index.json) ──
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
    return sum(scores.get(k, 0) * w for k, w in WEIGHTS.items())


def grade_from(c: float) -> str:
    if c >= 90:
        return "AAA"
    if c >= 75:
        return "AA"
    if c >= 60:
        return "A"
    if c >= 45:
        return "BBB"
    if c >= 30:
        return "BB"
    return "B"


def vintage_score(vy: int, base_year: int = 2022) -> int:
    """Same vintage adjustment used for BCT tokens:
    100 - (base_year - vintage)*12, floored at 0."""
    return max(0, 100 - (base_year - vy) * 12)


# ─── Archetype loading ───────────────────────────────────────────────────────
def load_archetypes() -> dict[str, dict]:
    data = json.loads(ARCHETYPES_PATH.read_text())
    return {a["id"]: a for a in data["archetypes"]}


def archetype_composite(arch: dict, vintage: int) -> tuple[float, str, dict]:
    """Build a 7-dimension score vector from an archetype + vintage and
    compute the composite using the BCT weights."""
    s = dict(arch["scores"])  # removal_type, additionality, permanence,
    #                            mrv_grade, co_benefits, registry_methodology
    s["vintage_year"] = vintage_score(vintage)
    comp = compute_composite(s)
    return comp, grade_from(comp), s


# ─── Documented pool composition (the only project-type signal available) ─────
# Source: independent_control_search.json quality_filter / mechanism fields, plus
# the well-documented public profile of each pool. We map each documented
# project-type bucket to an existing archetype id and a representative vintage
# consistent with each pool's stated minimum vintage (>=2014 for C3; Amazon
# REDD+ legacy vintages for MCO2). Shares are tonnage shares.
#
# These are POOL-LEVEL composition priors, NOT per-token resolutions. They are
# documented in data_gaps as an explicit modelling assumption.
POOL_PROFILES = {
    "C3_UBO": {
        "label": "C3 UBO (Universal Basic Offset)",
        "quality_filter": "Accepts most VCS and Gold Standard methodologies, vintage >= 2014",
        "min_vintage": 2014,
        # Permissionless broad-VCM pool: dominated by REDD+ and renewables,
        # mirroring the broad pre-2021 VCM supply that filled permissionless pools.
        "composition": [
            {"type": "REDD+",      "archetype": "redd_project",          "share": 0.45, "vintage": 2015},
            {"type": "Renewable",  "archetype": "grid_renewable_energy", "share": 0.40, "vintage": 2014},
            {"type": "ARR",        "archetype": "arr_conservation",      "share": 0.08, "vintage": 2016},
            {"type": "Cookstove",  "archetype": "cookstoves",            "share": 0.07, "vintage": 2016},
        ],
    },
    "C3_NBO": {
        "label": "C3 NBO (Nature Based Offset)",
        "quality_filter": "Nature-based methodologies only (REDD+, IFM, ARR), vintage >= 2014",
        "min_vintage": 2014,
        "composition": [
            {"type": "REDD+", "archetype": "redd_project",     "share": 0.60, "vintage": 2015},
            {"type": "ARR",   "archetype": "arr_conservation", "share": 0.25, "vintage": 2016},
            {"type": "IFM",   "archetype": "ifm",              "share": 0.15, "vintage": 2016},
        ],
    },
    "MCO2": {
        "label": "Moss MCO2 (PoS Bridge Token)",
        "quality_filter": "Curated by Moss (Amazon REDD+ focus, ~80% from specific projects)",
        "min_vintage": 2008,
        # Documented ~80% Amazon REDD+ (project-level), remainder other REDD+.
        "composition": [
            {"type": "REDD+ (Amazon)", "archetype": "redd_project", "share": 0.80, "vintage": 2012},
            {"type": "REDD+ (other)",  "archetype": "redd_project", "share": 0.20, "vintage": 2013},
        ],
    },
}


# ─── Per-pool scoring ────────────────────────────────────────────────────────
def score_pool(pool_key: str, deposits: list[dict], archetypes: dict) -> dict:
    """Score one pool. `deposits` is a list of dicts each with at least
    block_number and amount."""
    prof = POOL_PROFILES[pool_key]

    # Precompute archetype composite per documented composition bucket.
    buckets = []
    for c in prof["composition"]:
        arch = archetypes[c["archetype"]]
        comp, grade, detail = archetype_composite(arch, c["vintage"])
        buckets.append({
            "type": c["type"],
            "archetype": c["archetype"],
            "share": c["share"],
            "vintage": c["vintage"],
            "composite": round(comp, 2),
            "grade": grade,
            "scores_detail": detail,
        })

    # Pool-level mean quality = share-weighted archetype composite.
    pool_mean_quality = round(sum(b["share"] * b["composite"] for b in buckets), 4)

    # Composition by tonnes: apply documented tonnage shares to total tonnes.
    total_tonnes = sum(d.get("amount", 0.0) for d in deposits)
    n_deposits = len(deposits)
    composition_pct = {b["type"]: round(b["share"] * 100, 2) for b in buckets}
    composition_tonnes = {b["type"]: round(b["share"] * total_tonnes, 2) for b in buckets}

    # Per-deposit composite scores in block order.
    #
    # We DO NOT know which bucket each individual deposit belongs to (no per-token
    # type metadata). We therefore assign every deposit the pool-level
    # share-weighted mean composite. This makes per-deposit quality CONSTANT,
    # which is the honest representation of the information available: any
    # within-pool temporal trend in *quality* is NOT identifiable from these
    # data. (multipool_comparison.py handles this by setting temporal_rho=null
    # for these pools and documenting the gap.)
    ordered = sorted(deposits, key=lambda d: d.get("block_number", 0))
    per_deposit = [
        {
            "order": i,
            "block_number": d.get("block_number"),
            "amount_tonnes": d.get("amount", 0.0),
            "composite": pool_mean_quality,
            "grade": grade_from(pool_mean_quality),
            "note": "pool-archetype composite; per-token type/vintage unobserved",
        }
        for i, d in enumerate(ordered)
    ]

    return {
        "pool": prof["label"],
        "pool_key": pool_key,
        "quality_filter": prof["quality_filter"],
        "min_vintage": prof["min_vintage"],
        "n_deposits": n_deposits,
        "total_tonnes": round(total_tonnes, 2),
        "mean_quality": pool_mean_quality,
        "volume_weighted_mean_quality": pool_mean_quality,  # constant per deposit
        "grade": grade_from(pool_mean_quality),
        "composition_pct_tonnes": composition_pct,
        "composition_tonnes": composition_tonnes,
        "archetype_buckets": buckets,
        "per_deposit_scores": per_deposit,
        "block_range": [ordered[0]["block_number"], ordered[-1]["block_number"]] if ordered else None,
    }


def main() -> None:
    events = json.loads(EVENTS_PATH.read_text())
    archetypes = load_archetypes()

    # C3 UBO deposits and NBO deposits are the deposit events; mints mirror them.
    ubo_deposits = events.get("ubo_deposits", [])
    nbo_deposits = events.get("nbo_deposits", [])
    mco2_mints = events.get("mco2_mints", [])

    # Combine UBO+NBO into a single C3 pool for the headline comparison, but
    # keep sub-pool detail.
    c3_combined = ubo_deposits + nbo_deposits

    results = {
        "meta": {
            "generated_by": "score_alt_pools.py",
            "rubric": "BCT/NCT weights (scoring-rubrics/index.json v0.4); "
                      "vintage adj = 100-(2022-vy)*12; grade bands AAA..B",
            "method": "Methodology-archetype scoring at POOL level "
                      "(per-token type/vintage unavailable for C3/MCO2).",
        },
        "pools": {
            "C3_UBO": score_pool("C3_UBO", ubo_deposits, archetypes),
            "C3_NBO": score_pool("C3_NBO", nbo_deposits, archetypes),
            "C3": score_pool("C3_UBO", c3_combined, archetypes),  # combined, UBO profile
            "MCO2": score_pool("MCO2", mco2_mints, archetypes),
        },
        "data_gaps": [
            "C3 (UBO/NBO): event records carry only (block_number, c3t_contract, "
            "amount, tx_hash). No per-token project type, methodology, name, or "
            "vintage. No repo file resolves C3T contract addresses to projects. "
            "Per-token quality is therefore unobserved; pool composition is a "
            "documented prior (quality_filter), not a measured per-token mix.",
            "MCO2: 'mints' are Polygon PoS-bridge deposits of a fixed-supply, "
            "centrally-issued token, NOT permissionless pool deposits. There is "
            "no adverse-selection deposit mechanism. Composition (~80% Amazon "
            "REDD+) is Moss's documented curation, not per-token on-chain data.",
            "No per-token vintage is observable for C3/MCO2, so the BCT vintage "
            "adjustment is applied at the documented-composition level using "
            "representative vintages consistent with each pool's stated minimum "
            "vintage, not per-deposit vintages.",
        ],
    }

    # The combined C3 entry reuses the UBO profile; recombine its composition
    # honestly as a weighted blend of UBO and NBO documented mixes by tonnage.
    ubo_t = results["pools"]["C3_UBO"]["total_tonnes"]
    nbo_t = results["pools"]["C3_NBO"]["total_tonnes"]
    tot = ubo_t + nbo_t
    if tot > 0:
        blend: Counter = Counter()
        for src, w in [("C3_UBO", ubo_t / tot), ("C3_NBO", nbo_t / tot)]:
            for typ, pct in results["pools"][src]["composition_pct_tonnes"].items():
                blend[typ] += pct * w
        results["pools"]["C3"]["composition_pct_tonnes"] = {
            k: round(v, 2) for k, v in blend.items()
        }
        # Blended mean quality across the two sub-pools by tonnage.
        c3_mean = (
            results["pools"]["C3_UBO"]["mean_quality"] * (ubo_t / tot)
            + results["pools"]["C3_NBO"]["mean_quality"] * (nbo_t / tot)
        )
        results["pools"]["C3"]["mean_quality"] = round(c3_mean, 4)
        results["pools"]["C3"]["volume_weighted_mean_quality"] = round(c3_mean, 4)
        results["pools"]["C3"]["grade"] = grade_from(c3_mean)
        # rewrite per-deposit composite to the blended value
        for d in results["pools"]["C3"]["per_deposit_scores"]:
            d["composite"] = round(c3_mean, 4)
            d["grade"] = grade_from(c3_mean)

    OUT_PATH.write_text(json.dumps(results, indent=2))

    # Console summary
    print(f"Wrote {OUT_PATH}")
    for key in ["C3_UBO", "C3_NBO", "C3", "MCO2"]:
        p = results["pools"][key]
        print(f"\n{key}: {p['pool']}")
        print(f"  n_deposits={p['n_deposits']}  total_tonnes={p['total_tonnes']:,.0f}")
        print(f"  mean_quality={p['mean_quality']:.2f}  grade={p['grade']}")
        print(f"  composition%={p['composition_pct_tonnes']}")


if __name__ == "__main__":
    main()
