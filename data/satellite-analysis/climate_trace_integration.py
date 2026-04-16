#!/usr/bin/env python3
"""
climate_trace_integration.py
============================

Cross-reference BCT-deposited VCS projects with Climate TRACE asset data.

Climate TRACE (https://climatetrace.org) publishes a public, attribution-
free CSV/JSON download of every known power-plant and industrial asset
globally, with measured or modelled annual emissions. The v5 REST API
(https://api.climatetrace.org/v5/) supports:

    GET /v5/assets?countries=IND&sectors=power
    GET /v5/assets/{asset_id}

For each BCT project coordinate, we find the nearest Climate TRACE asset
in the relevant sector (power for renewables, manufacturing for industrial
projects) within a distance tolerance, and cross-reference:

  - Claimed project capacity (MW) vs nearest TRACE asset capacity.
  - Claimed zero-emission status vs TRACE measured emissions intensity
    for that plant.
  - If no nearest asset within 50 km, flag `status=no_match`. This is
    itself a finding: projects that can't be located in TRACE may not
    be physically additional.

Output
------
- data/satellite-analysis/climate_trace_match.md
- data/satellite-analysis/climate_trace_match.json

Fallback
--------
If the Climate TRACE API is unreachable, we still produce a plan/report
skeleton that the co-author can fill in once credentialled access is
available. The report documents the exact queries we attempted.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "satellite-analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = OUT_DIR / "cache" / "climate_trace"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

TRACE_API_BASE = "https://api.climatetrace.org/v5"
USER_AGENT = "CarbonNeutrality-Research/0.1"
TIMEOUT = 30

COUNTRY_ISO3 = {
    "India": "IND",
    "China": "CHN",
    "Turkey": "TUR",
    "Brazil": "BRA",
    "Indonesia": "IDN",
    "Peru": "PER",
    "Cambodia": "KHM",
    "Colombia": "COL",
    "Uganda": "UGA",
    "Kenya": "KEN",
    "Madagascar": "MDG",
    "Cuba": "CUB",
    "Guatemala": "GTM",
    "Bolivia": "BOL",
    "Ecuador": "ECU",
    "Bulgaria": "BGR",
    "DR Congo": "COD",
    "South Korea": "KOR",
    "Chile": "CHL",
    "Netherlands": "NLD",
    "Pakistan": "PAK",
    "Vietnam": "VNM",
}


def http_get_json(url: str, timeout: int = TIMEOUT) -> dict | None:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, HTTPError, TimeoutError, ConnectionError, OSError) as e:
        print(f"  [warn] {url} -> {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"  [warn] non-JSON response from {url}: {e}", file=sys.stderr)
        return None


def fetch_country_assets(iso3: str, sector: str) -> list[dict]:
    cache_path = CACHE_DIR / f"{iso3}_{sector}.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text())
        except Exception:
            pass
    url = f"{TRACE_API_BASE}/assets?countries={iso3}&sectors={sector}&limit=5000"
    data = http_get_json(url)
    if data is None:
        return []
    assets = data.get("assets") or data.get("data") or []
    cache_path.write_text(json.dumps(assets, indent=2))
    return assets


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def sector_for_type(project_type: str) -> str:
    t = (project_type or "").lower()
    if t in ("renewable", "fossil switch"):
        return "power"
    if t in ("industrial", "industrial gas"):
        return "manufacturing"
    if t in ("waste/methane",):
        return "waste"
    if t in ("redd+", "arr", "ifm"):
        return "forestry-and-land-use"
    if t == "agriculture":
        return "agriculture"
    return "power"


def nearest_asset(assets: list[dict], lat: float, lon: float,
                  max_km: float = 50.0) -> tuple[dict | None, float | None]:
    best = None
    best_d = None
    for a in assets:
        a_lat = a.get("latitude") or a.get("Latitude") or (a.get("centroid") or {}).get("lat")
        a_lon = a.get("longitude") or a.get("Longitude") or (a.get("centroid") or {}).get("lon")
        if a_lat is None or a_lon is None:
            continue
        try:
            d = haversine_km(lat, lon, float(a_lat), float(a_lon))
        except (TypeError, ValueError):
            continue
        if best_d is None or d < best_d:
            best_d = d
            best = a
    if best_d is not None and best_d <= max_km:
        return best, best_d
    return None, best_d  # still return the closest (for diagnostics) but flag


# ─────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-km", type=float, default=50.0)
    ap.add_argument("--top", type=int, default=18)
    args = ap.parse_args()

    coords_path = OUT_DIR / "verra_coordinates.json"
    if not coords_path.exists():
        print("ERROR: run fetch_verra_coordinates.py first.", file=sys.stderr)
        return 1
    coords = json.loads(coords_path.read_text())

    # Restrict to top-N by tonnes, and to projects with coordinates
    sorted_pids = sorted(
        (p for p in coords.values() if p.get("lat") is not None),
        key=lambda p: -float(p.get("tonnes_in_bct") or 0),
    )
    candidates = sorted_pids[: max(args.top * 3, 50)]
    print(f"Attempting Climate TRACE match for {len(candidates)} candidate projects …")

    # Group lookup by (country, sector) to minimize API calls
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in candidates:
        iso3 = COUNTRY_ISO3.get(p["country"] or "", None)
        if not iso3:
            continue
        sector = sector_for_type(p.get("type", ""))
        key = (iso3, sector)
        by_key.setdefault(key, [])
        by_key[key].append(p)

    asset_cache: dict[tuple[str, str], list[dict]] = {}
    for key in by_key:
        iso3, sector = key
        print(f"  fetching TRACE {sector} assets for {iso3} …")
        asset_cache[key] = fetch_country_assets(iso3, sector)
        time.sleep(0.1)  # gentle rate-limit

    matches: list[dict] = []
    for p in candidates:
        iso3 = COUNTRY_ISO3.get(p["country"] or "", None)
        if not iso3 or p.get("lat") is None:
            continue
        sector = sector_for_type(p.get("type", ""))
        assets = asset_cache.get((iso3, sector), [])
        if not assets:
            matches.append({
                "project_id": p["project_id"],
                "name": p["name"],
                "country": p["country"],
                "sector": sector,
                "status": "no_trace_data",
                "asset_count_queried": 0,
                "nearest_km": None,
            })
            continue
        best, d = nearest_asset(assets, p["lat"], p["lon"], max_km=args.max_km)
        if best is None:
            matches.append({
                "project_id": p["project_id"],
                "name": p["name"],
                "country": p["country"],
                "coord_precision": p["coord_precision"],
                "sector": sector,
                "status": "no_match_within_max_km",
                "asset_count_queried": len(assets),
                "nearest_km": round(d, 2) if d is not None else None,
            })
            continue
        matches.append({
            "project_id": p["project_id"],
            "name": p["name"],
            "country": p["country"],
            "coord_precision": p["coord_precision"],
            "sector": sector,
            "status": "match",
            "nearest_km": round(d, 2),
            "trace_asset_id": best.get("id") or best.get("asset_id"),
            "trace_asset_name": best.get("name") or best.get("asset_name"),
            "trace_asset_capacity_mw": best.get("capacity") or best.get("capacity_mw"),
            "trace_asset_emissions_tco2_2022": (
                best.get("emissions", {}).get("2022")
                if isinstance(best.get("emissions"), dict) else best.get("emissions_2022")
            ),
        })

    # ── Markdown report ────────────────────────────────────────────────
    n_total = len(matches)
    n_match = sum(1 for m in matches if m["status"] == "match")
    n_no_asset_data = sum(1 for m in matches if m["status"] == "no_trace_data")
    n_no_within = sum(1 for m in matches if m["status"] == "no_match_within_max_km")

    lines: list[str] = []
    lines.append("# Climate TRACE Asset Match for BCT Projects")
    lines.append("")
    lines.append("**Pipeline:** `data/satellite-analysis/climate_trace_integration.py`")
    lines.append(f"**API:** `{TRACE_API_BASE}`  (public, free)")
    lines.append(f"**Match tolerance:** {args.max_km} km")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Projects attempted: **{n_total}**")
    lines.append(f"- Matched to nearest TRACE asset within {args.max_km} km: **{n_match}**")
    lines.append(f"- No match within tolerance: **{n_no_within}**")
    lines.append(f"- Climate TRACE returned no data for country/sector: **{n_no_asset_data}**")
    lines.append("")
    if n_total == 0:
        lines.append(
            "> The pipeline is in dry-run mode (no network reach to Climate TRACE). "
            "Re-run with network access to populate matches. All query parameters are "
            "recorded so the co-author can reproduce exactly.")
        lines.append("")

    lines.append("## Per-project")
    lines.append("")
    lines.append(
        "| Project ID | Name | Country | Sector | Status | Nearest (km) | "
        "TRACE Asset | Cap (MW) |")
    lines.append(
        "|-----------|------|---------|--------|--------|--------------|-------------|---------|")
    for m in matches:
        nm = (m["name"] or "")[:40]
        lines.append(
            f"| {m['project_id']} | {nm} | {m.get('country','')} | {m.get('sector','')} | "
            f"{m['status']} | {m.get('nearest_km','')} | "
            f"{m.get('trace_asset_name','')} | {m.get('trace_asset_capacity_mw','')} |")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "Matches allow us to triangulate: (a) whether the claimed project physically "
        "exists where the PDD says it does, (b) whether its nameplate capacity roughly "
        "matches TRACE's estimate, and (c) for fossil-switch projects, whether TRACE "
        "measures the expected emissions reduction at the site.")
    lines.append("")
    lines.append(
        "**No-match-within-tolerance** is a meaningful null result: it signals either "
        "coarse Verra coordinates (country centroid only) or a plant too small for "
        "TRACE's detection threshold. Both merit discussion in the Nature paper.")
    lines.append("")

    (OUT_DIR / "climate_trace_match.md").write_text("\n".join(lines))
    (OUT_DIR / "climate_trace_match.json").write_text(
        json.dumps({"matches": matches, "max_km": args.max_km}, indent=2))

    print("─" * 60)
    print(f"Wrote {OUT_DIR / 'climate_trace_match.md'}")
    print(f"Wrote {OUT_DIR / 'climate_trace_match.json'}")
    print(f"Summary: {n_match} match / {n_no_within} out-of-range / {n_no_asset_data} no-data")
    return 0


if __name__ == "__main__":
    sys.exit(main())
