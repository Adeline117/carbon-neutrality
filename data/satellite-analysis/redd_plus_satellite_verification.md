# REDD+ Satellite Verification (Hansen GFC 2001-2023)

**Pipeline:** `data/satellite-analysis/hansen_deforestation.py`
**Tile source:** `https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11` (CC-BY, publicly downloadable)
**rasterio available:** `False`

## Summary

- REDD+ projects in BCT: **12**
- Projects with recorded PDD baseline: **12**
- Projects with computed Hansen loss rate: **0**

> `rasterio` is not installed in this environment; the pipeline records the exact Hansen GeoTIFF URLs for the remote-sensing co-author to process on Google Earth Engine with project polygons. Running `pip install rasterio` will enable local tile computation.

## Per-project Hansen tile URLs

| Project ID | Name | Country | Lat | Lon | Loss-year tile |
|------------|------|---------|-----|-----|----------------|
| 1052 | North Pikounda REDD+ | DR Congo | 0.18 | 15.7 | `Hansen_GFC-2023-v1.11_lossyear_10N_010E.tif` |
| 1094 | Ecomapua Amazon REDD Project | Brazil | -1.25 | -49.8 | `Hansen_GFC-2023-v1.11_lossyear_00N_050W.tif` |
| 1382 | The Envira Amazonia Project - A Trop | Brazil | -8.56 | -70.1 | `Hansen_GFC-2023-v1.11_lossyear_00N_080W.tif` |
| 1748 | Southern Cardamom REDD+ Project | Cambodia | 11.55 | 103.5 | `Hansen_GFC-2023-v1.11_lossyear_20N_100E.tif` |
| 674 | Rimba Raya Biodiversity Reserve Proj | Indonesia | -3.3 | 112.1 | `Hansen_GFC-2023-v1.11_lossyear_00N_110E.tif` |
| 981 | Pacajai REDD+ Project | Brazil | -2.7 | -51.0 | `Hansen_GFC-2023-v1.11_lossyear_00N_060W.tif` |
| 985 | Cordillera Azul National Park REDD P | Peru | -7.3 | -76.0 | `Hansen_GFC-2023-v1.11_lossyear_00N_080W.tif` |
| 1686 | Agrocortex REDD Project | Brazil | -9.4 | -71.4 | `Hansen_GFC-2023-v1.11_lossyear_00N_080W.tif` |
| 1566 | REDD+ Project Resguardo Indigena Uni | Colombia | 4.7 | -69.5 | `Hansen_GFC-2023-v1.11_lossyear_10N_070W.tif` |
| 934 | The Mai Ndombe REDD+ Project | DR Congo | -2.55 | 17.9 | `Hansen_GFC-2023-v1.11_lossyear_00N_010E.tif` |
| 1650 | Reduced Emissions from Deforestation | Cambodia | 12.7 | 106.85 | `Hansen_GFC-2023-v1.11_lossyear_20N_100E.tif` |
| 612 | The Kasigau Corridor REDD Project -  | Kenya | -3.75 | 38.6 | `Hansen_GFC-2023-v1.11_lossyear_00N_030E.tif` |

## Baseline vs observed

Computation deferred to co-author. The table above records the PDD baseline deforestation rates we've already parsed from public VCS methodology documents. The co-author's task is to pair each with the Hansen-measured loss rate inside the actual project polygon (not the 10-km centroid buffer we record here).

## REDD+ projects with PDD baselines parsed

| Project ID | Project | Baseline loss (%/yr) |
|------------|---------|----------------------|
| 1052 | North Pikounda REDD+ | 0.45 |
| 1094 | Ecomapua Amazon REDD Project | 0.75 |
| 1382 | Envira Amazonia | 1.22 |
| 1566 | Mataven REDD+ | 0.35 |
| 1650 | Keo Seima REDD+ | 1.8 |
| 1686 | Agrocortex REDD Project | 0.9 |
| 1748 | Southern Cardamom REDD+ | 1.92 |
| 612 | Kasigau Corridor REDD Phase II | 0.48 |
| 674 | Rimba Raya Biodiversity Reserve | 1.35 |
| 934 | Mai Ndombe REDD+ | 0.55 |
| 981 | Pacajai REDD+ Project | 0.8 |
| 985 | Cordillera Azul National Park REDD | 0.4 |

## What the co-author needs to add

1. Project polygon shapefiles (Verra VCS methodology uploads, or JNR-aligned jurisdictional maps).
2. Leakage-belt definitions per VCS methodology.
3. Google Earth Engine credentials to run the Hansen zonal stats over real polygons (we've recorded the tile URLs above so the pipeline is drop-in replaceable).
4. Pair with West et al. (2023) *Science* 'Action needed to make carbon offsets from forest conservation work for climate change mitigation' matched-sample method for counterfactual deforestation.
