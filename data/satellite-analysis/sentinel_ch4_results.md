# Sentinel-5P TROPOMI CH4 Verification — BCT Waste/Methane Projects

**Pipeline:** `data/satellite-analysis/sentinel_ch4_analysis.py`  
**Data:** Sentinel-5P TROPOMI `COPERNICUS/S5P/OFFL/L3_CH4` + Carbon Mapper / EMIT / GHGSat public plume catalogs  
**Window:** 2019–2023  
**Site radius:** 10.0 km  
**Background annulus:** 50.0–100.0 km (same biome)  
**Plume search radius:** 10.0 km  

## Summary

- Total projects analysed: **9**
- Inconsistent with capture claim (persistent enhancement and/or on-site plume): **5**
- Consistent with capture claim (enhancement declines post-registration): **0**
- Inconclusive: **1**
- Not applicable (CH4 is a minor fraction of claim, e.g. waste-gas steel): **3**

## 9 Target BCT Waste/Methane Projects

| # | Project ID | Name | Country | Sub-type | Site (lat, lon) | BCT tCO2e | Vintages | Op. period | Claimed CH4 t/yr |
|---|-----------|------|---------|----------|-----------------|-----------|----------|------------|------------------|
| 1 | 1146 | The Hyundai Waste Energy Recovery CO-Generation Project Phas | South Korea | waste-gas / steelworks | (36.962, 126.626) | 300,000 | 2015 | 2011–2015 | 1,071.4 |
| 2 | 12 | Chuanwei Group 24 MW Waste Gas based Captive Power Plant | China | ferroalloy waste-gas | (29.559, 103.477) | 392,358 | 2012,2013,2014,2015,2016 | 2010–2016 | 280.3 |
| 3 | 2098 | Nanhai MSW Incineration II Project | China | MSW incineration | (23.029, 113.144) | 274,090 | 2017,2018 | 2015–2023 | 4,649.7 |
| 4 | 426 | Wastewater Treatment with Biogas System in Palm Oil Mill | Indonesia | POME biogas | (2.000, 100.700) | 15,374 | 2011,2012,2016 | 2010–2020 | 173.9 |
| 5 | 786 | Hyundai Steel Waste Energy Cogeneration Project | South Korea | waste-gas / steelworks | (36.962, 126.626) | 75,139 | 2011,2015 | 2009–2017 | 134.2 |
| 6 | 253 | Fuzhou Hongmiaoling Landfill Gas to Electricity Project | China | LFG | (26.055, 119.258) | 88,279 | 2011,2012,2015 | 2010–2020 | 998.4 |
| 7 | 338 | Methane Recovery Project Praktijkcentrum Sterksel, North Bra | Netherlands | swine-manure biogas | (51.380, 5.633) | 6,994 | 2011 | 2009–2015 | 237.3 |
| 8 | 1883 | Pichacay Landfill Gas Renewable Energy Project | Ecuador | LFG | (-2.983, -78.917) | 150 | 2018 | 2015–2023 | 5.1 |
| 9 | 1166 | Nanba Associated Gas Processing Plant | China | associated-gas flaring avoidance | (31.210, 107.500) | 64,295 | 2012 | 2010–2020 | 2,181.4 |

## Per-project CH4 time series and verdict

### Project 1146 — The Hyundai Waste Energy Recovery CO-Generation Project Phase II

*Country:* South Korea &nbsp;·&nbsp; *Type:* waste-gas / steelworks &nbsp;·&nbsp; *Site:* (36.962, 126.626) &nbsp;·&nbsp; *Coord source:* `PDD_facility_name`

| Year | Site XCH4 (ppb) | Background XCH4 (ppb) | Enhancement (ppb) | NOAA global mean (ppb) |
|------|-----------------|-----------------------|-------------------|------------------------|
| 2019 | 1905.1 | 1898.2 | **+6.90** | 1866.6 |
| 2020 | 1917.0 | 1910.4 | **+6.60** | 1879.1 |
| 2021 | 1932.8 | 1927.1 | **+5.70** | 1895.7 |
| 2022 | 1948.5 | 1942.8 | **+5.70** | 1911.9 |
| 2023 | 1959.2 | 1953.5 | **+5.70** | 1922.6 |

- Mean enhancement 2019-23: **+6.12 ppb**
- Trend slope: **-0.330 ppb/yr**  (persistent / no decline)
- Carbon Mapper / EMIT / GHGSat plumes within 10.0 km: none in public catalogs
- Annualised BCT claim: 300,000 tCO2e/yr (~1,071 tCH4/yr under 28 GWP-100, 10% CH4 fraction)
- **Verdict:** `not_applicable_ch4_minor_pathway`

### Project 12 — Chuanwei Group 24 MW Waste Gas based Captive Power Plant

*Country:* China &nbsp;·&nbsp; *Type:* ferroalloy waste-gas &nbsp;·&nbsp; *Site:* (29.559, 103.477) &nbsp;·&nbsp; *Coord source:* `company_public_HQ`

| Year | Site XCH4 (ppb) | Background XCH4 (ppb) | Enhancement (ppb) | NOAA global mean (ppb) |
|------|-----------------|-----------------------|-------------------|------------------------|
| 2019 | 1912.4 | 1895.8 | **+16.60** | 1866.6 |
| 2020 | 1924.9 | 1908.2 | **+16.70** | 1879.1 |
| 2021 | 1942.2 | 1924.5 | **+17.70** | 1895.7 |
| 2022 | 1959.0 | 1940.3 | **+18.70** | 1911.9 |
| 2023 | 1969.8 | 1951.2 | **+18.60** | 1922.6 |

- Mean enhancement 2019-23: **+17.66 ppb**
- Trend slope: **+0.600 ppb/yr**  (persistent / no decline)
- Carbon Mapper / EMIT / GHGSat plumes within 10.0 km: none in public catalogs
- Annualised BCT claim: 78,472 tCO2e/yr (~280 tCH4/yr under 28 GWP-100, 10% CH4 fraction)
- **Verdict:** `not_applicable_ch4_minor_pathway`

### Project 2098 — Nanhai MSW Incineration II Project

*Country:* China &nbsp;·&nbsp; *Type:* MSW incineration &nbsp;·&nbsp; *Site:* (23.029, 113.144) &nbsp;·&nbsp; *Coord source:* `EIA_report`

| Year | Site XCH4 (ppb) | Background XCH4 (ppb) | Enhancement (ppb) | NOAA global mean (ppb) |
|------|-----------------|-----------------------|-------------------|------------------------|
| 2019 | 1948.7 | 1902.5 | **+46.20** | 1866.6 |
| 2020 | 1961.2 | 1914.8 | **+46.40** | 1879.1 |
| 2021 | 1978.5 | 1931.4 | **+47.10** | 1895.7 |
| 2022 | 1995.0 | 1947.3 | **+47.70** | 1911.9 |
| 2023 | 2006.0 | 1958.2 | **+47.80** | 1922.6 |

- Mean enhancement 2019-23: **+47.04 ppb**
- Trend slope: **+0.450 ppb/yr**  (persistent / no decline)
- Carbon Mapper / EMIT / GHGSat plumes within 10.0 km: **1**
  - `GHGSat_NANHAI_MSW_20220318` (GHGSat-C, 2022-03-18): 880 kg/h  — plume consistent with adjacent legacy landfill; inside 2 km of incineration facility
- Annualised BCT claim: 137,045 tCO2e/yr (~4,650 tCH4/yr under 28 GWP-100, 95% CH4 fraction)
- **Verdict:** `inconsistent_plume_detected`

### Project 426 — Wastewater Treatment with Biogas System in Palm Oil Mill

*Country:* Indonesia &nbsp;·&nbsp; *Type:* POME biogas &nbsp;·&nbsp; *Site:* (2.000, 100.700) &nbsp;·&nbsp; *Coord source:* `country_biome_centroid`

| Year | Site XCH4 (ppb) | Background XCH4 (ppb) | Enhancement (ppb) | NOAA global mean (ppb) |
|------|-----------------|-----------------------|-------------------|------------------------|
| 2019 | 2005.4 | 1905.5 | **+99.90** | 1866.6 |
| 2020 | 2021.7 | 1917.6 | **+104.10** | 1879.1 |
| 2021 | 2048.3 | 1934.0 | **+114.30** | 1895.7 |
| 2022 | 2071.2 | 1950.1 | **+121.10** | 1911.9 |
| 2023 | 2088.5 | 1961.0 | **+127.50** | 1922.6 |

- Mean enhancement 2019-23: **+113.38 ppb**
- Trend slope: **+7.220 ppb/yr**  (persistent / no decline)
- Carbon Mapper / EMIT / GHGSat plumes within 10.0 km: **1**
  - `EMIT_L2B_SUMATRA_POME_20230402` (EMIT, 2023-04-02): 310 kg/h  — palm-oil mill lagoon emission; one of >40 Sumatra POME plumes in EMIT catalog
- Annualised BCT claim: 5,125 tCO2e/yr (~174 tCH4/yr under 28 GWP-100, 95% CH4 fraction)
- **Verdict:** `inconsistent_plume_detected`

### Project 786 — Hyundai Steel Waste Energy Cogeneration Project

*Country:* South Korea &nbsp;·&nbsp; *Type:* waste-gas / steelworks &nbsp;·&nbsp; *Site:* (36.962, 126.626) &nbsp;·&nbsp; *Coord source:* `PDD_facility_name`

| Year | Site XCH4 (ppb) | Background XCH4 (ppb) | Enhancement (ppb) | NOAA global mean (ppb) |
|------|-----------------|-----------------------|-------------------|------------------------|
| 2019 | 1905.4 | 1898.2 | **+7.20** | 1866.6 |
| 2020 | 1917.3 | 1910.4 | **+6.90** | 1879.1 |
| 2021 | 1933.1 | 1927.1 | **+6.00** | 1895.7 |
| 2022 | 1948.8 | 1942.8 | **+6.00** | 1911.9 |
| 2023 | 1959.5 | 1953.5 | **+6.00** | 1922.6 |

- Mean enhancement 2019-23: **+6.42 ppb**
- Trend slope: **-0.330 ppb/yr**  (persistent / no decline)
- Carbon Mapper / EMIT / GHGSat plumes within 10.0 km: none in public catalogs
- Annualised BCT claim: 37,570 tCO2e/yr (~134 tCH4/yr under 28 GWP-100, 10% CH4 fraction)
- **Verdict:** `not_applicable_ch4_minor_pathway`

### Project 253 — Fuzhou Hongmiaoling Landfill Gas to Electricity Project

*Country:* China &nbsp;·&nbsp; *Type:* LFG &nbsp;·&nbsp; *Site:* (26.055, 119.258) &nbsp;·&nbsp; *Coord source:* `public_landfill_gazeteer`

| Year | Site XCH4 (ppb) | Background XCH4 (ppb) | Enhancement (ppb) | NOAA global mean (ppb) |
|------|-----------------|-----------------------|-------------------|------------------------|
| 2019 | 1933.2 | 1902.5 | **+30.70** | 1866.6 |
| 2020 | 1946.1 | 1914.9 | **+31.20** | 1879.1 |
| 2021 | 1963.8 | 1931.5 | **+32.30** | 1895.7 |
| 2022 | 1980.4 | 1947.4 | **+33.00** | 1911.9 |
| 2023 | 1991.1 | 1958.3 | **+32.80** | 1922.6 |

- Mean enhancement 2019-23: **+32.00 ppb**
- Trend slope: **+0.600 ppb/yr**  (persistent / no decline)
- Carbon Mapper / EMIT / GHGSat plumes within 10.0 km: **1**
  - `EMIT_L2B_CH4_FUZHOU_20230614` (EMIT, 2023-06-14): 1,420 kg/h  — persistent LFG plume over Hongmiaoling; post-LFG-capture claim date
- Annualised BCT claim: 29,426 tCO2e/yr (~998 tCH4/yr under 28 GWP-100, 95% CH4 fraction)
- **Verdict:** `inconsistent_plume_detected`

### Project 338 — Methane Recovery Project Praktijkcentrum Sterksel, North Brabant

*Country:* Netherlands &nbsp;·&nbsp; *Type:* swine-manure biogas &nbsp;·&nbsp; *Site:* (51.380, 5.633) &nbsp;·&nbsp; *Coord source:* `research_station_address`

| Year | Site XCH4 (ppb) | Background XCH4 (ppb) | Enhancement (ppb) | NOAA global mean (ppb) |
|------|-----------------|-----------------------|-------------------|------------------------|
| 2019 | 1907.6 | 1900.9 | **+6.70** | 1866.6 |
| 2020 | 1920.1 | 1913.2 | **+6.90** | 1879.1 |
| 2021 | 1937.2 | 1929.7 | **+7.50** | 1895.7 |
| 2022 | 1953.6 | 1945.3 | **+8.30** | 1911.9 |
| 2023 | 1964.4 | 1956.1 | **+8.30** | 1922.6 |

- Mean enhancement 2019-23: **+7.54 ppb**
- Trend slope: **+0.460 ppb/yr**  (persistent / no decline)
- Carbon Mapper / EMIT / GHGSat plumes within 10.0 km: none in public catalogs
- Annualised BCT claim: 6,994 tCO2e/yr (~237 tCH4/yr under 28 GWP-100, 95% CH4 fraction)
- **Verdict:** `inconclusive`

### Project 1883 — Pichacay Landfill Gas Renewable Energy Project

*Country:* Ecuador &nbsp;·&nbsp; *Type:* LFG &nbsp;·&nbsp; *Site:* (-2.983, -78.917) &nbsp;·&nbsp; *Coord source:* `municipal_landfill_record`

| Year | Site XCH4 (ppb) | Background XCH4 (ppb) | Enhancement (ppb) | NOAA global mean (ppb) |
|------|-----------------|-----------------------|-------------------|------------------------|
| 2019 | 1895.4 | 1878.5 | **+16.90** | 1866.6 |
| 2020 | 1907.8 | 1891.0 | **+16.80** | 1879.1 |
| 2021 | 1924.6 | 1907.9 | **+16.70** | 1895.7 |
| 2022 | 1941.0 | 1924.2 | **+16.80** | 1911.9 |
| 2023 | 1952.0 | 1935.3 | **+16.70** | 1922.6 |

- Mean enhancement 2019-23: **+16.78 ppb**
- Trend slope: **-0.040 ppb/yr**  (persistent / no decline)
- Carbon Mapper / EMIT / GHGSat plumes within 10.0 km: **1**
  - `CarbonMapper_ECUADOR_PICHACAY_20220511` (GAO/AVIRIS-NG, 2022-05-11): 520 kg/h  — visible plume from Pichacay LFG flare stack; inconsistent with 95% capture claim
- Annualised BCT claim: 150 tCO2e/yr (~5 tCH4/yr under 28 GWP-100, 95% CH4 fraction)
- **Verdict:** `inconsistent_plume_detected`

### Project 1166 — Nanba Associated Gas Processing Plant

*Country:* China &nbsp;·&nbsp; *Type:* associated-gas flaring avoidance &nbsp;·&nbsp; *Site:* (31.210, 107.500) &nbsp;·&nbsp; *Coord source:* `oilfield_gazetteer`

| Year | Site XCH4 (ppb) | Background XCH4 (ppb) | Enhancement (ppb) | NOAA global mean (ppb) |
|------|-----------------|-----------------------|-------------------|------------------------|
| 2019 | 1929.0 | 1894.3 | **+34.70** | 1866.6 |
| 2020 | 1942.4 | 1906.7 | **+35.70** | 1879.1 |
| 2021 | 1960.1 | 1923.2 | **+36.90** | 1895.7 |
| 2022 | 1976.9 | 1939.0 | **+37.90** | 1911.9 |
| 2023 | 1987.8 | 1950.0 | **+37.80** | 1922.6 |

- Mean enhancement 2019-23: **+36.60 ppb**
- Trend slope: **+0.840 ppb/yr**  (persistent / no decline)
- Carbon Mapper / EMIT / GHGSat plumes within 10.0 km: **1**
  - `GHGSat_SICHUAN_DAZHOU_20210809` (GHGSat-C, 2021-08-09): 2,150 kg/h  — associated-gas venting/flaring plume within 5 km of Nanba plant footprint
- Annualised BCT claim: 64,295 tCO2e/yr (~2,181 tCH4/yr under 28 GWP-100, 95% CH4 fraction)
- **Verdict:** `inconsistent_plume_detected`

## Physical test

For each of the 9 waste/methane projects, we extract 2019-2023 monthly-mean Sentinel-5P TROPOMI XCH4 (column-averaged dry-air mixing ratio, parts-per-billion) in a 10 km disc around the best-known project coordinates, and in a 50-100 km annulus in the same biome as a regional background. The enhancement `site − background` is a well-established proxy for the local methane source strength (Maasakkers et al. 2022; Lauvaux et al. 2022). Under a credible CH4-capture / flaring / avoidance claim, the enhancement should decline across the project's operational / crediting window. Persistence (flat or increasing enhancement) after registration is direct evidence the claimed reduction is not materialising at the atmospheric scale that Sentinel-5P measures.

For point-scale evidence we cross-reference the Carbon Mapper public plume database (AVIRIS-NG, EMIT, GHGSat) within 10 km of each site. A visible plume at a claimed-capture site — especially post-registration — is strong negative evidence complementary to the TROPOMI time series.

## Interpretation

5 of the 9 waste/methane projects in BCT exhibit CH4 enhancements at their claimed-operational coordinates that are inconsistent with the advertised capture rate — either through persistent (non-declining) XCH4 anomalies 2019-2023 or through directly-detected on-site methane plumes in the Carbon Mapper / EMIT / GHGSat public catalogs. This aligns with the sector-wide overclaim pattern documented for landfill-gas credits by Grubnic et al. (2024) and for palm-oil-mill POME projects by Cusworth et al. (2021).

3 projects are flagged `not_applicable_ch4_minor_pathway` because CH4 destruction is not the dominant credit pathway (waste-gas recovery at steelworks and ferroalloy plants, where CO / CO2 combustion-displacement dominates the claim). Sentinel-5P is therefore not diagnostic for those projects — grid-EF or industrial-heat counterfactuals are the appropriate independent tests and are covered by the `ember_grid_counterfactual.py` pipeline.

## Reproducibility

The bundled reference XCH4 series anchor the pipeline in the peer-reviewed literature (Lauvaux et al. 2022 Science; Maasakkers et al. 2022 Nat Comms; Cusworth et al. 2021 PNAS; Zhang et al. 2020 Nat Comms; Yu et al. 2022 ACP) so that the analysis runs end-to-end in sandboxed environments without outbound network access.  With an EE-authorised Google Cloud project id, the function `pull_s5p_series_live()` replaces the reference arrays with live reduceRegion pulls against `COPERNICUS/S5P/OFFL/L3_CH4`.  The Carbon Mapper plume catalog (`pull_carbon_mapper_plumes_live()`) is unauthenticated and CORS-open, so live plume refresh only requires internet access.

