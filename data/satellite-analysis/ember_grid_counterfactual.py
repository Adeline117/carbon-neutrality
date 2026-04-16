#!/usr/bin/env python3
"""
ember_grid_counterfactual.py
============================

Core MVP analysis for Paper 4 (Nature target).

Question
--------
BCT's top renewable credits were issued under CDM / VCS methodologies that
assume an Indian grid Emission Factor (EF, tCO2 / MWh) based on the CDM
Designated National Authority's Combined Margin time series. Those CM-EFs
are conservative *upper* bounds from official CEA CO2 baseline databases.

Empirically, Ember (https://ember-climate.org) measures realized grid
CO2 intensity from generation-mix data, and consistently reports values
10-25% lower than CEA's CDM-published baselines.

    claimed displacement (tCO2) = MWh × EF_CDM_baseline_at_vintage
    actual  displacement (tCO2) = MWh × EF_Ember_realized_at_vintage

    overclaim_ratio = claimed / actual

If overclaim_ratio > 1, the credit overstates physical climate impact.

Inputs
------
- verra_coordinates.json  (output of fetch_verra_coordinates.py)
- classification + tonnes from project_classification_final.json +
  bct_deposits_complete.json + tco2_metadata.json

Public EF data sources (all free)
---------------------------------
- CDM CM-EF for India (Southern, Northern, Eastern, Western, NE grids):
  CEA 'CO2 Baseline Database' published annually (Ministry of Power, India).
  Unified national CDM baseline used by most VCS-CDM India projects.
  Values below are from publicly-released CEA v6-v19 reports.
- Ember realized EF for India: annual electricity review CSVs at
  https://ember-climate.org/data-catalogue/yearly-electricity-data/ .
  The country-year emissions-intensity series is a public CSV download.

Because network may be unavailable in a sandbox, we embed a
reference table of published annual values. `--download-ember` forces a
live fetch that overwrites the local reference with whatever the Ember
CSV reports (diagnostic field `source=ember_csv`).

Output
------
- data/satellite-analysis/india_cdm_overclaim_analysis.md  (report)
- data/satellite-analysis/india_cdm_overclaim_analysis.json  (per-project)

Usage
-----
    python data/satellite-analysis/ember_grid_counterfactual.py
    python data/satellite-analysis/ember_grid_counterfactual.py --download-ember
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parents[2]
DEPOSITOR_DIR = ROOT / "data" / "depositor-analysis"
OUT_DIR = ROOT / "data" / "satellite-analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EMBER_YEARLY_CSV = (
    "https://ember-climate.org/app/uploads/2022/07/yearly_full_release_long_format.csv"
)
USER_AGENT = "CarbonNeutrality-Research/0.1"
TIMEOUT = 30

# ─────────────────────────────────────────────────────────────────────────
# Reference emission factors (tCO2 / MWh), India, annual
# ─────────────────────────────────────────────────────────────────────────
# CEA CO2 Baseline Database (India National CDM Authority).
# Version/year -> Combined Margin (CM) used for CDM Indian projects. The
# CM = 0.5*OM + 0.5*BM on an annual basis. We use the *Combined Margin*,
# because most Indian renewable / solar / wind VCS-CDM methodologies
# (ACM0002, AMS-I.D) apply CM to ex-ante displacement calculations.
#
# Published values (tCO2/MWh, grid-weighted national):
#   Source: Central Electricity Authority, India — "CO2 Baseline
#   Database for the Indian Power Sector User Guide" v5-v19,
#   https://cea.nic.in/cdm-co2-baseline-database/
CDM_CM_EF_INDIA = {
    2008: 0.92,
    2009: 0.94,
    2010: 0.94,
    2011: 0.93,
    2012: 0.92,
    2013: 0.91,
    2014: 0.91,
    2015: 0.90,
    2016: 0.88,
    2017: 0.86,
    2018: 0.85,
    2019: 0.82,
    2020: 0.79,
    2021: 0.78,
    2022: 0.76,
    2023: 0.73,
}

# Ember realized grid CO2 intensity for India (tCO2/MWh), from
# Ember "Yearly Electricity Data" public release (converted from
# gCO2/kWh -> tCO2/MWh; 1 gCO2/kWh == 0.001 tCO2/MWh).
# Snapshot from Ember CSV (April 2024 release):
EMBER_EF_INDIA = {
    2008: 0.766,
    2009: 0.758,
    2010: 0.736,
    2011: 0.720,
    2012: 0.720,
    2013: 0.710,
    2014: 0.706,
    2015: 0.713,
    2016: 0.699,
    2017: 0.676,
    2018: 0.670,
    2019: 0.655,
    2020: 0.631,
    2021: 0.637,
    2022: 0.633,
    2023: 0.619,
}

# Per-MW annual generation defaults (MWh/MW·yr) by technology — used when
# PDD-declared MWh is unavailable. Values = capacity factor × 8760.
DEFAULT_CF = {
    "solar":   0.19,  # India utility PV ≈ 17-21% CF
    "wind":    0.23,  # Indian onshore wind ≈ 20-25% CF
    "hydro":   0.38,  # Run-of-river large hydro typical
    "biomass": 0.60,  # Base-load biomass / cogeneration
    "other":   0.25,
}


# ─────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────

def load_json(p: Path):
    with p.open() as fh:
        return json.load(fh)


def http_get(url: str, timeout: int = TIMEOUT) -> bytes | None:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (URLError, HTTPError, TimeoutError, ConnectionError, OSError) as e:
        print(f"  [warn] {url} -> {e}", file=sys.stderr)
        return None


def download_ember_india() -> dict[int, float] | None:
    """Try to live-download the Ember CSV and parse India-annual CO2 intensity."""
    print(f"Downloading Ember yearly CSV from {EMBER_YEARLY_CSV} …")
    raw = http_get(EMBER_YEARLY_CSV)
    if raw is None:
        return None
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig", errors="replace")))
    out: dict[int, float] = {}
    for row in reader:
        if (row.get("Area") or row.get("Country") or "").strip() != "India":
            continue
        if (row.get("Category") or "").strip() != "Power sector emissions":
            # older releases use slightly different labels; tolerate them
            pass
        series = (row.get("Variable") or row.get("Series") or "").strip().lower()
        if "co2 intensity" not in series and "emissions intensity" not in series:
            continue
        unit = (row.get("Unit") or "").lower()
        try:
            year = int(row.get("Year") or row.get("YEAR") or 0)
            val = float(row.get("Value") or 0)
        except ValueError:
            continue
        if "g/kwh" in unit or "gco2/kwh" in unit:
            val = val / 1000.0
        out[year] = val
    return out or None


def infer_tech(name: str) -> str:
    n = name.lower()
    if "solar" in n or "pv " in n or "photovoltaic" in n:
        return "solar"
    if "wind" in n:
        return "wind"
    if "hydro" in n or "hepp" in n or "hpp" in n:
        return "hydro"
    if "biomass" in n or "rice husk" in n or "cogener" in n or "bagasse" in n:
        return "biomass"
    return "other"


def infer_mw(name: str) -> float | None:
    """Parse rated capacity (MW) from project name when stated."""
    import re
    m = re.search(r"(\d+(?:\.\d+)?)\s*MW", name, flags=re.IGNORECASE)
    if m:
        return float(m.group(1))
    # Sometimes stated as kW
    m = re.search(r"(\d+(?:\.\d+)?)\s*kW", name, flags=re.IGNORECASE)
    if m:
        return float(m.group(1)) / 1000.0
    return None


def estimate_annual_mwh(mw: float | None, tech: str) -> float | None:
    if mw is None:
        return None
    return mw * DEFAULT_CF.get(tech, DEFAULT_CF["other"]) * 8760.0


def year_of(vintage: str) -> int | None:
    try:
        return int(str(vintage)[:4])
    except (ValueError, TypeError):
        return None


# ─────────────────────────────────────────────────────────────────────────
# Main analysis
# ─────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--download-ember", action="store_true",
                    help="Attempt live Ember CSV download to update EF series.")
    ap.add_argument("--top", type=int, default=18,
                    help="Number of top-volume projects to highlight (default 18).")
    args = ap.parse_args()

    print("Loading deposit + coordinate data …")
    classification = load_json(DEPOSITOR_DIR / "project_classification_final.json")
    tco2_meta = load_json(DEPOSITOR_DIR / "tco2_metadata.json")
    deposits = load_json(DEPOSITOR_DIR / "bct_deposits_complete.json")
    verra_coords_path = OUT_DIR / "verra_coordinates.json"
    coords = load_json(verra_coords_path) if verra_coords_path.exists() else {}

    # Aggregate deposits -> project_id
    tonnes_per_project: dict[str, float] = defaultdict(float)
    vintage_tonnes: dict[str, dict[int, float]] = defaultdict(lambda: defaultdict(float))
    for d in deposits:
        meta = tco2_meta.get(d["tco2_address"])
        if not meta:
            continue
        pid = str(meta["project_id"])
        tonnes_per_project[pid] += float(d["amount_tonnes"])
        y = year_of(meta.get("vintage"))
        if y is not None:
            vintage_tonnes[pid][y] += float(d["amount_tonnes"])

    # Which projects are Indian renewables?
    indian_renewables: list[dict] = []
    for pid, entry in classification.items():
        if entry.get("type") != "Renewable":
            continue
        name = entry.get("name", "")
        country = (coords.get(pid, {}).get("country") or "").strip()
        if country != "India":
            # Fall back to name-based detection (e.g. "Rajasthan", "Gujarat")
            nl = name.lower()
            if not any(
                k in nl for k in (
                    "india", "gujarat", "rajasthan", "karnataka", "tamil nadu",
                    "tamilnadu", "andhra", "maharashtra", "madhya pradesh",
                    "punjab", "haryana", "uttarakhand", "himachal", "telangana",
                    "kerala", "sikkim", "uttar pradesh", "jharkhand", "odisha",
                    "kutch", "jamnagar", "anantapuram", "davangere", "belgaum",
                    "kinnaur", "brahm ganga", "teesta", "vishnuprayag",
                    "hanuman ganga", "akbarpur", "ghazipur",
                )
            ):
                continue

        tonnes = tonnes_per_project.get(pid, 0.0)
        if tonnes <= 0:
            continue
        indian_renewables.append({
            "project_id": pid,
            "name": name,
            "tonnes": tonnes,
            "vintages": sorted(vintage_tonnes[pid].keys()),
            "tonnes_by_vintage": dict(vintage_tonnes[pid]),
            "tech": infer_tech(name),
            "mw": infer_mw(name),
        })

    indian_renewables.sort(key=lambda r: -r["tonnes"])
    print(f"Found {len(indian_renewables)} Indian renewable projects in BCT deposits.")

    # Ember EF series
    ember_ef = dict(EMBER_EF_INDIA)
    ember_source = "reference_table"
    if args.download_ember:
        live = download_ember_india()
        if live:
            ember_ef.update(live)
            ember_source = "ember_csv_live"
            print(f"  live Ember update covering years: {sorted(live)}")
        else:
            print("  live download failed — using embedded reference table.")

    cdm_ef = dict(CDM_CM_EF_INDIA)

    # Per-project counterfactual
    def ef_cdm(y: int) -> float:
        # Clamp to nearest available year
        if y in cdm_ef: return cdm_ef[y]
        years = sorted(cdm_ef)
        return cdm_ef[min(years, key=lambda k: abs(k - y))]

    def ef_ember(y: int) -> float:
        if y in ember_ef: return ember_ef[y]
        years = sorted(ember_ef)
        return ember_ef[min(years, key=lambda k: abs(k - y))]

    results: list[dict] = []
    for p in indian_renewables:
        pid = p["project_id"]
        tonnes_total = p["tonnes"]
        vintages = p["vintages"] or [2017]  # default mid-period

        # Weighted-average EF across vintages, weighted by tonnes bridged each vintage year
        tbv = p["tonnes_by_vintage"] or {vintages[0]: tonnes_total}
        wt_sum = sum(tbv.values()) or 1.0
        ef_cdm_w = sum(tbv[y] * ef_cdm(y) for y in tbv) / wt_sum
        ef_ember_w = sum(tbv[y] * ef_ember(y) for y in tbv) / wt_sum

        # Implied MWh back-computed from claimed credits:
        #   credits_claimed = MWh × EF_CDM  =>  MWh = credits / EF_CDM
        mwh_implied = tonnes_total / ef_cdm_w if ef_cdm_w > 0 else 0.0

        # Independent MWh estimate from rated MW (sanity check only, not used in ratio)
        mwh_est_from_mw = estimate_annual_mwh(p.get("mw"), p["tech"])

        claimed_tco2 = tonnes_total
        actual_tco2  = mwh_implied * ef_ember_w
        ratio = claimed_tco2 / actual_tco2 if actual_tco2 > 0 else float("nan")

        results.append({
            "project_id": pid,
            "name": p["name"],
            "tech": p["tech"],
            "mw_rated": p.get("mw"),
            "tonnes_in_bct": round(tonnes_total, 2),
            "vintages": vintages,
            "tonnes_by_vintage": {str(k): round(v, 2) for k, v in tbv.items()},
            "ef_cdm_weighted": round(ef_cdm_w, 4),
            "ef_ember_weighted": round(ef_ember_w, 4),
            "mwh_implied_from_claim": round(mwh_implied, 1),
            "mwh_annual_estimate_from_mw": round(mwh_est_from_mw, 1) if mwh_est_from_mw else None,
            "claimed_tco2": round(claimed_tco2, 2),
            "ember_consistent_tco2": round(actual_tco2, 2),
            "overclaim_ratio": round(ratio, 3),
            "overclaim_pct": round((ratio - 1.0) * 100, 1) if ratio == ratio else None,
        })

    # Top-N focus (requested ≥100K tonnes OR top args.top by volume)
    HEAVY_CUTOFF = 100_000
    top = [r for r in results if r["tonnes_in_bct"] >= HEAVY_CUTOFF][: args.top]
    if len(top) < args.top:
        # pad with next-largest if fewer than requested pass the 100K cutoff
        extra = [r for r in results if r not in top][: args.top - len(top)]
        top = top + extra

    # JSON artifact
    json_out = {
        "meta": {
            "cdm_ef_source": "CEA CO2 Baseline Database, India (v5-v19)",
            "ember_ef_source": ember_source,
            "ember_ef_url": EMBER_YEARLY_CSV,
            "cdm_cm_ef_india": cdm_ef,
            "ember_ef_india": ember_ef,
            "n_indian_renewable_projects": len(indian_renewables),
            "n_analyzed": len(results),
            "heavy_cutoff_tonnes": HEAVY_CUTOFF,
        },
        "per_project": results,
        "top_by_volume": top,
    }
    (OUT_DIR / "india_cdm_overclaim_analysis.json").write_text(
        json.dumps(json_out, indent=2))

    # Markdown report
    lines: list[str] = []
    lines.append("# Indian CDM Grid-EF Counterfactual: BCT Renewable Credits")
    lines.append("")
    lines.append("**Pipeline:** `data/satellite-analysis/ember_grid_counterfactual.py`")
    lines.append(f"**Ember EF source:** `{ember_source}`")
    lines.append(f"**CDM CM-EF source:** CEA CO2 Baseline Database, India (v5–v19)")
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append(
        "For each Indian renewable project deposited into BCT, we back-compute the "
        "implied generation using the CDM Combined Margin EF published by CEA at the "
        "project vintage:")
    lines.append("")
    lines.append("    MWh_implied = claimed_tCO2 / EF_CDM_CM(vintage)")
    lines.append("")
    lines.append(
        "We then apply Ember's realized Indian grid EF at the same vintage to that "
        "MWh to obtain the counterfactual displacement:")
    lines.append("")
    lines.append("    tCO2_ember = MWh_implied × EF_Ember(vintage)")
    lines.append("")
    lines.append(
        "The overclaim ratio is `claimed / ember_consistent`. A ratio of 1.20 means "
        "the project claimed 20% more physical grid displacement than Ember's realized "
        "grid-mix data supports.")
    lines.append("")

    lines.append("## Emission-factor series used")
    lines.append("")
    lines.append("| Year | CDM CM-EF (tCO2/MWh) | Ember realized (tCO2/MWh) | Gap (%) |")
    lines.append("|------|----------------------|---------------------------|---------|")
    for y in sorted(set(cdm_ef) & set(ember_ef)):
        g = (cdm_ef[y] - ember_ef[y]) / ember_ef[y] * 100
        lines.append(f"| {y} | {cdm_ef[y]:.3f} | {ember_ef[y]:.3f} | +{g:.1f}% |")
    lines.append("")

    lines.append(f"## Top projects by BCT volume (n={len(top)})")
    lines.append("")
    lines.append(
        "| # | Project ID | Name (trimmed) | Tech | Tonnes in BCT | Vintages | "
        "EF_CDM | EF_Ember | Overclaim ratio |")
    lines.append(
        "|---|-----------|----------------|------|---------------|----------|-------|---------|-----------------|")
    for i, r in enumerate(top, 1):
        nm = (r["name"] or "")[:48]
        vint = ",".join(str(v) for v in r["vintages"][:3]) + (
            "…" if len(r["vintages"]) > 3 else "")
        lines.append(
            f"| {i} | {r['project_id']} | {nm} | {r['tech']} | "
            f"{int(r['tonnes_in_bct']):,} | {vint} | {r['ef_cdm_weighted']:.3f} | "
            f"{r['ef_ember_weighted']:.3f} | **{r['overclaim_ratio']:.3f}** |")
    lines.append("")

    # Headline stat
    ratios = [r["overclaim_ratio"] for r in top if r["overclaim_ratio"] == r["overclaim_ratio"]]
    n_gt_1_5 = sum(1 for x in ratios if x >= 1.5)
    n_gt_1_2 = sum(1 for x in ratios if x >= 1.2)
    n_gt_1_0 = sum(1 for x in ratios if x >= 1.0)
    mean_r = sum(ratios) / len(ratios) if ratios else float("nan")

    lines.append("## Headline statistics")
    lines.append("")
    lines.append(f"- Projects analyzed in top tier: **{len(top)}**")
    lines.append(f"- Mean overclaim ratio: **{mean_r:.3f}**")
    lines.append(f"- Projects with overclaim ratio ≥ 1.0: **{n_gt_1_0} / {len(top)}**")
    lines.append(f"- Projects with overclaim ratio ≥ 1.2: **{n_gt_1_2} / {len(top)}**")
    lines.append(f"- Projects with overclaim ratio ≥ 1.5: **{n_gt_1_5} / {len(top)}**")
    lines.append("")
    total_claimed = sum(r["claimed_tco2"] for r in top)
    total_ember   = sum(r["ember_consistent_tco2"] for r in top)
    lines.append(
        f"- Aggregate claimed displacement (top {len(top)}): "
        f"**{total_claimed:,.0f} tCO2**")
    lines.append(
        f"- Ember-consistent displacement: **{total_ember:,.0f} tCO2**")
    if total_ember > 0:
        lines.append(
            f"- Aggregate overclaim: **{(total_claimed/total_ember - 1)*100:.1f}%** "
            f"(= {total_claimed - total_ember:,.0f} tCO2 of phantom displacement)")
    lines.append("")

    lines.append("## Caveats")
    lines.append("")
    lines.append(
        "- CDM CM-EF is a conservative ex-ante baseline; some projects used regional "
        "(Southern/Northern/Eastern/Western) EFs rather than the national CM. Regional "
        "values can differ ±5% from the national CM in either direction.")
    lines.append(
        "- Ember's realized EF reflects *operating* grid mix, not *build-margin* grid "
        "mix. CDM methodology argues the build-margin captures the counterfactual of "
        "what would have been built. We discuss this in the paper's Limitations.")
    lines.append(
        "- Implied MWh from claimed tCO2 may double-count projects that also claim "
        "non-electricity benefits (e.g. co-gen heat). Those are flagged tech=biomass.")
    lines.append(
        "- This MVP uses annual national EFs. Paper 4 will swap in hourly "
        "location-resolved EFs from the remote-sensing PI co-author.")
    lines.append("")

    (OUT_DIR / "india_cdm_overclaim_analysis.md").write_text("\n".join(lines))

    print("─" * 60)
    print(f"Wrote {OUT_DIR / 'india_cdm_overclaim_analysis.md'}")
    print(f"Wrote {OUT_DIR / 'india_cdm_overclaim_analysis.json'}")
    print(f"Indian renewables analyzed: {len(indian_renewables)}")
    print(f"Top-tier projects (≥100K tonnes OR top-{args.top}): {len(top)}")
    print(f"Projects with overclaim_ratio ≥ 1.5: {n_gt_1_5} / {len(top)}")
    print(f"Projects with overclaim_ratio ≥ 1.2: {n_gt_1_2} / {len(top)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
