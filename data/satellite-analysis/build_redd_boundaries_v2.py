#!/usr/bin/env python3
"""
build_redd_boundaries_v2.py
===========================

Nature-grade rebuild of REDD+ project boundaries for the 12 BCT projects.

Strategy (in priority order):
  1. **West et al. 2023 Science shapefiles** (DataverseNL doi:10.34894/IQC9LM):
     Contains true KML-derived polygons for 5 of our 12 projects (934, 985,
     1566, 1650, 1748). Loaded from data/satellite-analysis/west2023_data/
     and re-projected to WGS84 for use downstream.
  2. **Approximate PDD centroid disc** (fallback for 7 projects):
     Rimba Raya (674), Kariba (902), Ecomapua (1094), Envira (1382),
     Brazil Nut (868), Kasigau (612), Agrocortex (1686). Uses equal-area
     disc at PDD-reported project area centred on PDD-reported centroid.

Outputs:
  data/satellite-analysis/redd_boundaries/VCS_{id}.geojson (overwritten)
  data/satellite-analysis/redd_boundaries/_manifest.json (overwritten)

Each geojson retains the original approximate disc under `geometry_approx`
as a fallback property so downstream sensitivity analysis can swap in the
disc. True polygons are written as MultiPolygon/Polygon in `geometry` with
`source` tagged accordingly.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import geopandas as gpd
from shapely.geometry import mapping, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
SAT_DIR = ROOT / "data" / "satellite-analysis"
BOUND_DIR = SAT_DIR / "redd_boundaries"
WEST_DIR = SAT_DIR / "west2023_data" / "shapefiles"
BOUND_DIR.mkdir(parents=True, exist_ok=True)


# Full BCT REDD+ project registry (same as build_redd_boundaries.py v1)
REDD_PROJECTS: dict[str, dict] = {
    "674":  {"name": "Rimba Raya Biodiversity Reserve",
             "country": "Indonesia", "lat": -3.30, "lon": 112.10,
             "area_ha": 100_000, "registration_year": 2013,
             "pdd_baseline_pct_per_yr": 1.35},
    "934":  {"name": "Mai Ndombe REDD+",
             "country": "DR Congo", "lat": -2.55, "lon": 17.90,
             "area_ha": 299_000, "registration_year": 2012,
             "pdd_baseline_pct_per_yr": 0.55},
    "902":  {"name": "Kariba REDD+",
             "country": "Zimbabwe", "lat": -16.75, "lon": 28.60,
             "area_ha": 785_000, "registration_year": 2011,
             "pdd_baseline_pct_per_yr": 1.00},
    "985":  {"name": "Cordillera Azul National Park REDD",
             "country": "Peru", "lat": -7.30, "lon": -76.00,
             "area_ha": 1_600_000, "registration_year": 2010,
             "pdd_baseline_pct_per_yr": 0.40},
    "1094": {"name": "Ecomapua Amazon REDD",
             "country": "Brazil", "lat": -1.25, "lon": -49.80,
             "area_ha": 90_000, "registration_year": 2012,
             "pdd_baseline_pct_per_yr": 0.75},
    "1382": {"name": "Envira Amazonia",
             "country": "Brazil", "lat": -8.56, "lon": -70.10,
             "area_ha": 39_000, "registration_year": 2013,
             "pdd_baseline_pct_per_yr": 1.22},
    "1650": {"name": "Keo Seima REDD+",
             "country": "Cambodia", "lat": 12.70, "lon": 106.85,
             "area_ha": 166_000, "registration_year": 2015,
             "pdd_baseline_pct_per_yr": 1.80},
    "1748": {"name": "Southern Cardamom REDD+",
             "country": "Cambodia", "lat": 11.55, "lon": 103.50,
             "area_ha": 497_000, "registration_year": 2015,
             "pdd_baseline_pct_per_yr": 1.92},
    "868":  {"name": "Brazil Nut Concessions (Madre de Dios)",
             "country": "Peru", "lat": -12.00, "lon": -69.40,
             "area_ha": 300_000, "registration_year": 2012,
             "pdd_baseline_pct_per_yr": 0.70},
    "612":  {"name": "Kasigau Corridor REDD Phase II",
             "country": "Kenya", "lat": -3.75, "lon": 38.60,
             "area_ha": 170_000, "registration_year": 2011,
             "pdd_baseline_pct_per_yr": 0.48},
    "1566": {"name": "Mataven REDD+",
             "country": "Colombia", "lat": 4.70, "lon": -69.50,
             "area_ha": 1_150_000, "registration_year": 2014,
             "pdd_baseline_pct_per_yr": 0.35},
    "1686": {"name": "Agrocortex REDD",
             "country": "Brazil", "lat": -9.40, "lon": -71.40,
             "area_ha": 186_000, "registration_year": 2015,
             "pdd_baseline_pct_per_yr": 0.90},
}


# Mapping: project_id -> (shapefile, id_column_value)
WEST2023_MAP = {
    "934":  ("DRC_polygons.shp",      "934"),
    "985":  ("Peru_polygons.shp",     "985"),
    "1566": ("Colombia_polygons.shp", "1566"),
    "1650": ("Cambodia_polygons.shp", "1650"),
    "1748": ("Cambodia_polygons.shp", "1748"),
}


def disc_polygon(lat: float, lon: float, area_ha: float,
                 n: int = 64) -> list[list[float]]:
    area_m2 = area_ha * 10_000.0
    radius_m = math.sqrt(area_m2 / math.pi)
    deg_lat = radius_m / 111_000.0
    deg_lon = radius_m / (111_000.0 * max(math.cos(math.radians(lat)), 1e-6))
    ring: list[list[float]] = []
    for i in range(n):
        theta = 2.0 * math.pi * i / n
        dy = deg_lat * math.sin(theta)
        dx = deg_lon * math.cos(theta)
        ring.append([round(lon + dx, 6), round(lat + dy, 6)])
    ring.append(ring[0])
    return ring


def load_west_polygon(pid: str) -> dict | None:
    if pid not in WEST2023_MAP:
        return None
    shp_name, id_val = WEST2023_MAP[pid]
    shp_path = WEST_DIR / shp_name
    if not shp_path.exists():
        return None
    try:
        gdf = gpd.read_file(shp_path)
    except Exception as e:
        print(f"  [warn] read_file failed for {shp_name}: {e}")
        return None
    # Reproject to WGS84
    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    # Robust filter: ID may be str or int; REDD is str or int
    def _is_redd1(v):
        try:
            return int(v) == 1
        except Exception:
            return str(v) == "1"
    def _id_match(v):
        try:
            return int(v) == int(id_val)
        except Exception:
            return str(v) == str(id_val)
    mask = gdf["ID"].apply(_id_match) & gdf["REDD"].apply(_is_redd1)
    sub = gdf[mask]
    if len(sub) == 0:
        print(f"  [info] shapefile has no REDD=1 row for ID={id_val} (West "
              f"2023 release omitted the geometry); falling back to disc.")
        return None
    # Union into single (multi)polygon; drop Z
    geoms = [g for g in sub.geometry if g is not None and not g.is_empty]
    if not geoms:
        return None
    # Drop Z dimension
    from shapely.ops import transform
    def drop_z(g):
        return transform(lambda x, y, z=None: (x, y), g)
    geoms = [drop_z(g) for g in geoms]
    union = unary_union(geoms)
    return mapping(union)


def main() -> int:
    manifest: dict[str, dict] = {}
    for pid, meta in REDD_PROJECTS.items():
        west_geom = load_west_polygon(pid)
        if west_geom is not None:
            source = "west2023_vu_shapefile"
            geometry = west_geom
            print(f"  VCS {pid} ({meta['name'][:40]}): USING West 2023 polygon")
        else:
            source = "approximate_pdd_centroid_disc"
            ring = disc_polygon(meta["lat"], meta["lon"], meta["area_ha"])
            geometry = {"type": "Polygon", "coordinates": [ring]}
            print(f"  VCS {pid} ({meta['name'][:40]}): fallback disc "
                  f"({meta['area_ha']:,} ha @ {meta['lat']},{meta['lon']})")

        # Always include fallback disc in props for downstream sensitivity
        disc_ring = disc_polygon(meta["lat"], meta["lon"], meta["area_ha"])
        gj = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {
                    "vcs_id": pid,
                    "name": meta["name"],
                    "country": meta["country"],
                    "area_ha": meta["area_ha"],
                    "registration_year": meta["registration_year"],
                    "pdd_baseline_pct_per_yr": meta["pdd_baseline_pct_per_yr"],
                    "centroid_lat": meta["lat"],
                    "centroid_lon": meta["lon"],
                    "source": source,
                    "west2023_available": west_geom is not None,
                    "fallback_disc": {
                        "type": "Polygon",
                        "coordinates": [disc_ring],
                    },
                },
                "geometry": geometry,
            }],
        }
        path = BOUND_DIR / f"VCS_{pid}.geojson"
        path.write_text(json.dumps(gj, indent=2))
        manifest[pid] = {
            "path": str(path.relative_to(ROOT)),
            "area_ha": meta["area_ha"],
            "registration_year": meta["registration_year"],
            "source": source,
            "west2023_available": west_geom is not None,
        }

    (BOUND_DIR / "_manifest.json").write_text(json.dumps(manifest, indent=2))
    n_real = sum(1 for v in manifest.values() if v["west2023_available"])
    n_disc = len(manifest) - n_real
    print(f"\nWrote {len(manifest)} boundaries to {BOUND_DIR}:")
    print(f"  - West 2023 real polygons: {n_real}")
    print(f"  - Approximate discs:       {n_disc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
