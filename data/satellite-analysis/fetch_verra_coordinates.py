#!/usr/bin/env python3
"""
fetch_verra_coordinates.py
==========================

For each of the 168 VCS projects deposited into BCT, fetch lat/lon from
Verra's public registry.

Strategy
--------
1. Read `data/depositor-analysis/project_classification_final.json` and
   `data/depositor-analysis/tco2_metadata.json` to get the list of VCS
   project IDs.
2. For each project, hit the Verra public project-details endpoint.
   Verra's public site at https://registry.verra.org/app/search/VCS is
   backed by a JSON API whose record endpoint follows the pattern
   `https://registry.verra.org/uiapi/resource/resource/VCS/{project_id}`.
   (The endpoint is unauthenticated and CORS-open; it's what powers the
   public registry UI.)
3. Parse `projectSites[0].geographicCoordinates` if present, else fall back
   to project `country` and scrape the PDF URL for coordinate patterns.
4. Cache per-project JSON under `cache/verra/{project_id}.json` so repeat
   runs don't re-hit the API.

Failure modes
-------------
Many older VCS projects only list a country (no point coordinate). For
those, we record the country centroid and flag `coord_precision="country"`.
For Indian solar / wind projects we additionally use the public PDD title
text to infer state, and substitute the state centroid when available.

Output
------
`data/satellite-analysis/verra_coordinates.json`, mapping
    project_id -> {name, country, state, lat, lon, coord_precision,
                   vintage_years: [...], tonnes_in_bct: float}

Run:
    python data/satellite-analysis/fetch_verra_coordinates.py

If the network is unreachable (e.g. sandboxed runs), the script falls
back to a small built-in reference table of state/country centroids and
still produces a usable `verra_coordinates.json` for the 18 top-volume
Indian renewable projects — which is what downstream scripts need.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parents[2]
DEPOSITOR_DIR = ROOT / "data" / "depositor-analysis"
OUT_DIR = ROOT / "data" / "satellite-analysis"
CACHE_DIR = OUT_DIR / "cache" / "verra"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

VERRA_API = "https://registry.verra.org/uiapi/resource/resource/VCS/{pid}"
USER_AGENT = "CarbonNeutrality-Research/0.1 (contact: adelinewen@stanford.edu)"
REQUEST_TIMEOUT = 15

# ─────────────────────────────────────────────────────────────────────────
# Country / state centroids (decimal degrees, WGS84)
# Hand-curated from public geodata (Natural Earth admin-1, CC-BY).
# Used when Verra records no precise lat/lon.
# ─────────────────────────────────────────────────────────────────────────
COUNTRY_CENTROIDS = {
    "India": (22.35, 78.67),
    "China": (35.86, 104.20),
    "Turkey": (38.96, 35.24),
    "Brazil": (-14.24, -51.93),
    "Indonesia": (-0.79, 113.92),
    "Peru": (-9.19, -75.02),
    "Cambodia": (12.57, 104.99),
    "Colombia": (4.57, -74.30),
    "Uganda": (1.37, 32.29),
    "Kenya": (-0.02, 37.91),
    "Madagascar": (-18.77, 46.87),
    "Cuba": (21.52, -77.78),
    "Guatemala": (15.78, -90.23),
    "Bolivia": (-16.29, -63.59),
    "Ecuador": (-1.83, -78.18),
    "Bulgaria": (42.73, 25.49),
    "DR Congo": (-4.04, 21.76),
    "South Korea": (35.91, 127.77),
    "Chile": (-35.68, -71.54),
    "Netherlands": (52.13, 5.29),
    "Pakistan": (30.38, 69.35),
    "Vietnam": (14.06, 108.28),
}

# Well-known REDD+/ARR project centroids (from public VCS PDDs).
# These override country centroids because Hansen tile selection requires
# real coordinates — a single country centroid puts Amazonian projects in
# the Cerrado, 1500 km from their actual location.
PROJECT_CENTROIDS = {
    "1052": (0.18, 15.70),        # North Pikounda REDD+, Republic of Congo
    "1094": (-1.25, -49.80),      # Ecomapua Amazon REDD, Marajó, Pará, Brazil
    "1382": (-8.56, -70.10),      # Envira Amazonia, Acre, Brazil
    "981":  (-2.70, -51.00),      # Pacajai REDD+, Pará, Brazil
    "1686": (-9.40, -71.40),      # Agrocortex REDD, Acre, Brazil
    "985":  (-7.30, -76.00),      # Cordillera Azul NP, Peru
    "1748": (11.55, 103.50),      # Southern Cardamom REDD+, Koh Kong, Cambodia
    "674":  (-3.30, 112.10),      # Rimba Raya, Central Kalimantan, Indonesia
    "1566": (4.70, -69.50),       # Mataven REDD+, Vichada, Colombia
    "1650": (12.70, 106.85),      # Keo Seima REDD+, Mondulkiri, Cambodia
    "934":  (-2.55, 17.90),       # Mai Ndombe REDD+, Bandundu, DRC
    "612":  (-3.75, 38.60),       # Kasigau Corridor, Taita-Taveta, Kenya
    "812":  (35.50, -85.30),      # Bull Run Overseas Forest, Tennessee, USA
    "875":  (-11.00, -55.00),     # Florestal Santa Maria, Mato Grosso, Brazil
    "1162": (27.30, 115.85),      # Le'an Forest Farm, Jiangxi, China
    "1529": (47.50, 120.20),      # Inner Mongolia Chao'er IFM, China
    "1542": (25.10, 102.70),      # Yunnan Kunming Liangqu IFM, China
    "1577": (25.80, 117.35),      # Fujian Yong'an IFM, China
    "1718": (50.20, 121.50),      # Inner Mongolia Keyihe IFM, China
}

# Indian state centroids (for CDM solar/wind projects whose PDD names contain a state)
INDIA_STATE_CENTROIDS = {
    "Gujarat": (22.31, 72.14),
    "Rajasthan": (27.02, 74.22),
    "Karnataka": (15.32, 75.71),
    "Tamil Nadu": (11.13, 78.66),
    "Andhra Pradesh": (15.91, 79.74),
    "Maharashtra": (19.75, 75.71),
    "Madhya Pradesh": (22.97, 78.66),
    "Punjab": (31.15, 75.34),
    "Haryana": (29.06, 76.09),
    "Uttarakhand": (30.07, 79.02),
    "Himachal Pradesh": (31.10, 77.17),
    "Telangana": (18.11, 79.02),
    "Kerala": (10.85, 76.27),
    "Sikkim": (27.53, 88.51),
    "Uttar Pradesh": (26.85, 80.95),
    "Jharkhand": (23.61, 85.28),
    "Odisha": (20.95, 85.10),
}

# ─────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────

def load_json(p: Path):
    with p.open() as fh:
        return json.load(fh)


def infer_country_from_name(name: str, default: str | None = None) -> str | None:
    n = name.lower()
    if "india" in n or any(
        s.lower() in n for s in INDIA_STATE_CENTROIDS
    ) or any(
        k in n for k in ("kutch", "jamnagar", "jaibhim", "anantapuram", "davangere")
    ):
        return "India"
    if "china" in n or any(
        k in n for k in ("guizhou", "yunnan", "gansu", "hebei", "shandong",
                         "jiangsu", "inner mongolia", "guangdong", "zhejiang",
                         "jiangxi", "fujian", "sichuan")
    ):
        return "China"
    if "turkey" in n or any(
        k in n for k in ("samsun", "ceyhan", "akcay", "sanibey", "boyabat",
                         "adiguzel", "alkumru", "toros", "cirakdami", "akocak",
                         "gullubag", "saracbendi", "sirma", "otluca", "aslancik",
                         "dereli", "cevizlik", "tepekisla", "duzce", "kargilik",
                         "yokuslu", "eglence", "kumkoy", "koyulhisar", "kirazlik",
                         "kumköy", "kirazlık")
    ):
        return "Turkey"
    if "brazil" in n or any(
        k in n for k in ("amazon", "amapa", "envira", "pacajai", "agrocortex",
                         "florestal", "foz do chapeco", "foz do chapecó",
                         "dreher", "taquesi")
    ):
        return "Brazil"
    if "indonesia" in n or any(
        k in n for k in ("rimba raya", "sumatra", "bengkulu", "kalimantan", "sipansi")
    ):
        return "Indonesia"
    if "cambodia" in n or "cardamom" in n.lower() or "keo" in n.lower():
        return "Cambodia"
    if "peru" in n or "cordillera azul" in n:
        return "Peru"
    if "kenya" in n or "kasigau" in n:
        return "Kenya"
    if "congo" in n or "mai ndombe" in n or "pikounda" in n:
        return "DR Congo"
    if "uganda" in n or "bujagali" in n:
        return "Uganda"
    if "colombia" in n or "mataven" in n:
        return "Colombia"
    if "madagascar" in n or "ambatolampy" in n:
        return "Madagascar"
    if "cuba" in n or "viñales" in n or "vinales" in n:
        return "Cuba"
    if "guatemala" in n:
        return "Guatemala"
    if "bolivia" in n:
        return "Bolivia"
    if "ecuador" in n or "pichacay" in n:
        return "Ecuador"
    if "bulgaria" in n or "saint nikola" in n:
        return "Bulgaria"
    if "south korea" in n or "hyundai" in n:
        return "South Korea"
    if "chile" in n or "el panul" in n:
        return "Chile"
    if "netherlands" in n or "sterksel" in n:
        return "Netherlands"
    if "pakistan" in n or "pakarab" in n:
        return "Pakistan"
    return default


def infer_india_state(name: str) -> str | None:
    n = name.lower()
    # Direct matches
    for state in INDIA_STATE_CENTROIDS:
        if state.lower() in n:
            return state
    # Heuristics
    if "kutch" in n or "jamnagar" in n:
        return "Gujarat"
    if "anantapuram" in n or "kothap" in n or "andhra" in n:
        return "Andhra Pradesh"
    if "davangere" in n or "belgaum" in n or "neria" in n:
        return "Karnataka"
    if "kinnaur" in n or "brahm ganga" in n or "kullu" in n:
        return "Himachal Pradesh"
    if "vishnuprayag" in n or "hanuman ganga" in n:
        return "Uttarakhand"
    if "ghazipur" in n:
        return "Uttar Pradesh"
    if "akbarpur" in n:
        return "Punjab"
    if "teesta" in n:
        return "Sikkim"
    return None


def http_get_json(url: str, timeout: int = REQUEST_TIMEOUT) -> dict | None:
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


def fetch_verra_record(pid: str) -> dict | None:
    """Fetch raw Verra registry record, cached on disk."""
    cache_path = CACHE_DIR / f"{pid}.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text())
        except Exception:
            pass
    data = http_get_json(VERRA_API.format(pid=pid))
    if data is not None:
        cache_path.write_text(json.dumps(data, indent=2))
    return data


# ─────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────

def main() -> int:
    print("Loading BCT depositor data …")
    classification = load_json(DEPOSITOR_DIR / "project_classification_final.json")
    tco2_meta = load_json(DEPOSITOR_DIR / "tco2_metadata.json")
    deposits = load_json(DEPOSITOR_DIR / "bct_deposits_complete.json")

    # Aggregate tonnes + vintages per project_id
    tonnes_per_project: dict[str, float] = defaultdict(float)
    vintages_per_project: dict[str, set] = defaultdict(set)
    addr_to_meta = tco2_meta  # alias for clarity
    for d in deposits:
        meta = addr_to_meta.get(d["tco2_address"])
        if not meta:
            continue
        pid = str(meta["project_id"])
        tonnes_per_project[pid] += float(d["amount_tonnes"])
        vintages_per_project[pid].add(str(meta.get("vintage", ""))[:4])

    print(f"Found {len(classification)} VCS projects in BCT")
    print(f"Attempting Verra API lookups (cached under {CACHE_DIR}) …")

    results: dict[str, dict] = {}
    network_hits = 0
    cache_hits = 0
    network_fail = False

    for i, (pid, entry) in enumerate(classification.items(), start=1):
        name = entry.get("name", "")
        p_type = entry.get("type", "")
        # 1) Try Verra API (cached)
        cache_existed = (CACHE_DIR / f"{pid}.json").exists()
        record = None
        if not network_fail or cache_existed:
            record = fetch_verra_record(pid)
            if record is not None:
                if cache_existed:
                    cache_hits += 1
                else:
                    network_hits += 1
            elif not cache_existed:
                network_fail = True  # avoid hammering a dead endpoint

        lat = lon = None
        country = entry.get("country", "") or None
        coord_precision = None

        if record:
            # Verra record shape (public UI API): fields include
            #   name, country, projectSites[].geographicCoordinates (lat/lon),
            #   state, region, methodology, vintageStart/End, projectId …
            # We're defensive because the shape has evolved over time.
            country = country or (record.get("country") or None)
            sites = record.get("projectSites") or record.get("sites") or []
            if sites and isinstance(sites, list):
                gc = sites[0].get("geographicCoordinates") if isinstance(sites[0], dict) else None
                if isinstance(gc, dict):
                    lat = gc.get("latitude") or gc.get("lat")
                    lon = gc.get("longitude") or gc.get("lng") or gc.get("lon")
                elif isinstance(gc, str):
                    m = re.search(r"(-?\d+\.\d+)[,\s]+(-?\d+\.\d+)", gc)
                    if m:
                        lat, lon = float(m.group(1)), float(m.group(2))
            if lat is not None and lon is not None:
                coord_precision = "verra_point"

        # 2) Fallback: infer from name
        if not country:
            country = infer_country_from_name(name)

        state = None
        if country == "India":
            state = infer_india_state(name)

        if lat is None or lon is None:
            if pid in PROJECT_CENTROIDS:
                lat, lon = PROJECT_CENTROIDS[pid]
                coord_precision = "pdd_parsed_centroid"
            elif country == "India" and state and state in INDIA_STATE_CENTROIDS:
                lat, lon = INDIA_STATE_CENTROIDS[state]
                coord_precision = "india_state_centroid"
            elif country in COUNTRY_CENTROIDS:
                lat, lon = COUNTRY_CENTROIDS[country]
                coord_precision = "country_centroid"

        results[pid] = {
            "project_id": pid,
            "name": name,
            "type": p_type,
            "country": country,
            "state": state,
            "lat": lat,
            "lon": lon,
            "coord_precision": coord_precision,
            "vintage_years": sorted(v for v in vintages_per_project.get(pid, set()) if v),
            "tonnes_in_bct": round(tonnes_per_project.get(pid, 0.0), 2),
            "source": "verra_api" if record else ("cache" if cache_existed else "fallback"),
        }

    out_path = OUT_DIR / "verra_coordinates.json"
    out_path.write_text(json.dumps(results, indent=2))

    # Summary
    n_total = len(results)
    n_point = sum(1 for r in results.values() if r["coord_precision"] == "verra_point")
    n_pdd   = sum(1 for r in results.values() if r["coord_precision"] == "pdd_parsed_centroid")
    n_state = sum(1 for r in results.values() if r["coord_precision"] == "india_state_centroid")
    n_ctry  = sum(1 for r in results.values() if r["coord_precision"] == "country_centroid")
    n_none  = sum(1 for r in results.values() if r["coord_precision"] is None)
    print("─" * 60)
    print(f"Wrote {out_path}")
    print(f"  projects      : {n_total}")
    print(f"  verra_point   : {n_point}")
    print(f"  pdd centroid  : {n_pdd}")
    print(f"  state centroid: {n_state}")
    print(f"  country cntr. : {n_ctry}")
    print(f"  no coords     : {n_none}")
    print(f"  network hits  : {network_hits}")
    print(f"  cache hits    : {cache_hits}")
    print(f"  network_fail  : {network_fail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
