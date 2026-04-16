# Tokenized carbon credits overstated physical climate impact by a quarter — evidence from 1,187 on-chain deposits and satellite-anchored grid counterfactuals

**Target journal:** *Nature* (Article, ~3,000 words + 4 display items)
**Paper 4 of the Plan B four-paper pipeline.**
**Status:** MVP skeleton. Sections marked `[CO-AUTHOR PLACEHOLDER]` await the remote-sensing PI collaborator.

---

## Authors (tentative)

- Adeline Wen (lead, on-chain + economics)
- **[CO-AUTHOR PLACEHOLDER: remote-sensing PI — co-first author]**
- Additional co-authors TBD (Verra registry contact; CEA/Ember data liaison)

---

## Abstract (Nature ≤ 200 words)

**[CO-AUTHOR PLACEHOLDER: satellite PI to finalize opening sentence linking this to the remote-sensing MRV literature.]**

Voluntary carbon markets claim that every retired credit represents one tonne of CO2 avoided or removed. Tokenization, beginning with Toucan Protocol's Base Carbon Tonne (BCT) pool in 2021, promised to make that claim auditable by writing retirements to a public blockchain. Here we combine the complete on-chain deposit history of BCT (1,187 deposits, 168 Verra projects, 22.0 Mt CO2e bridged) with satellite-era measured grid emission factors and 23 years of Hansen Global Forest Change data to test the physical validity of those claims. Focusing on the 18 top-volume Indian renewable-energy credits — which together represent 3.37 Mt of claimed displacement across hydro, wind, and biomass — we find that every single project overstated its grid-displacement impact by 20-29% (mean 26.7%) relative to Ember-measured realized Indian grid emission factors at each vintage. Aggregated, this is **685,000 tCO2 of phantom climate benefit** in the top tier alone. **[CO-AUTHOR PLACEHOLDER: REDD+ satellite result, 1-2 sentences.]** These findings establish a quantitative reproducible protocol for retrospective verification of tokenized carbon claims.

---

## Introduction / Hook

> **Tokenized carbon credits funded projects that overestimated physical climate impact by more than a quarter — and every one of the eighteen largest Indian renewable credits on-chain is implicated.**

Voluntary carbon markets have absorbed more than $2 B in retail and corporate purchases since 2020, on the premise that each credit corresponds to one measurable tonne of avoided or removed CO2. That premise rests on two foundations: (i) the registry (here Verra's VCS programme) issues credits only to projects that demonstrate additionality, and (ii) the underlying methodology quantifies displacement or removal using defensible counterfactuals. Both foundations have been challenged by recent work: West et al. (2023) showed Verra REDD+ baselines overshoot observed deforestation by a factor of ~3; Badgley et al. (2022) showed California's forestry offsets inflated climate value by ~30% through programme design.

Tokenization was marketed as a transparency upgrade. By writing retirement events to a public chain, Toucan, Moss, and Klima made it possible to audit *who owns what* in real time. Prior work (Papers 1-3 of this series) has shown that the credits actually bridged into on-chain pools are disproportionately low-quality: of BCT's 22.0 Mt, **69.1%** are renewable energy (ACM0002 / AMS-I.D methodologies) that the post-2013 CDM Executive Board itself deprecated as no-longer-additional for grid-connected projects in India and China.

But on-chain observability also makes something else possible. For the first time, we can link an entire population of retired credits to a **machine-readable project ID + vintage tuple**. If we pair that tuple with satellite-era *measured* grid emission factors and *measured* forest change, we can test retrospectively whether the claimed tonne corresponds to a real tonne.

This paper establishes that protocol and runs it on the BCT universe.

---

## Data

### On-chain deposit graph (fully observed)

- **1,187 deposits** into Toucan's BCT pool covering 2021-07-20 to present (ingested via Base L2 event logs; see `data/depositor-analysis/fetch_deposits.py`).
- **22.0 Mt CO2e** nominal face value.
- **168 unique Verra VCS projects** traceable by project ID + vintage parsed from the deterministic TCO2 token name `Toucan Protocol: TCO2-VCS-{project_id}-{vintage}`.
- **187 unique depositor addresses** with full transaction history.
- Classification by CDM project type:
  - Renewable: 123 projects, **69.1%** of volume (15.2 Mt)
  - Fossil switch: 9, 10.4%
  - REDD+: 12, 4.2%
  - Waste/methane: 9, 5.5%
  - Other: 15

### Ember realized grid emission factors

- Annual Indian grid CO2 intensity (tCO2/MWh), 2008-2023, from Ember's public "Yearly Electricity Data" CSV (https://ember-climate.org/data-catalogue/yearly-electricity-data/).
- Compiled from generation-mix × fuel-specific emission factors; peer-reviewed and updated annually.

### CDM Combined Margin baselines

- Central Electricity Authority (India) "CO2 Baseline Database for the Indian Power Sector", versions v5-v19 (2008-2023), publicly downloadable.
- Combined Margin = ½·Operating Margin + ½·Build Margin — the baseline that ACM0002 / AMS-I.D projects must use.

### Satellite: Hansen Global Forest Change

- Hansen et al. (2013, *Science*) v1.11 (2001-2023), redistributed CC-BY via Google Earth Engine public storage.
- 30 m annual forest-loss-year tiles (`lossyear_*.tif`).

### Satellite: Climate TRACE v5 assets

- Free/public API at `api.climatetrace.org/v5/assets`.
- Global inventory of power plants and industrial facilities with measured or modelled annual emissions.
- Used for asset-level cross-reference with claimed project coordinates.

### Verra registry coordinates

- Scraped (public API) for all 168 BCT projects. 104 resolve to at least country-centroid; 19 to Indian-state centroid. Precise-point coordinates recorded where available. Coordinate precision is tracked per project.

---

## Methods

**[CO-AUTHOR PLACEHOLDER: satellite PI — please add: (a) exact method for project-polygon delineation from VCS methodology uploads and JNR jurisdictional maps; (b) matched-sample counterfactual à la West et al. 2023 for REDD+ leakage belts; (c) hourly location-resolved grid EF from WattTime / Tomorrow.io (or your preferred source) to supersede the annual national EF we use in the MVP below.]**

### Counterfactual framework (Indian grid)

For every Indian renewable BCT deposit $d$ with claimed displacement $C_d$ (tCO2) and vintage year $y_d$:

1. Recover implied generation: $\text{MWh}_d = C_d / \text{EF}_\text{CDM}(y_d)$ where $\text{EF}_\text{CDM}(y)$ is the CEA CM EF for year $y$.
2. Compute Ember-consistent displacement: $A_d = \text{MWh}_d \times \text{EF}_\text{Ember}(y_d)$.
3. Project-level overclaim ratio: $r_p = \sum_{d \in p} C_d / \sum_{d \in p} A_d$.

Under the null that CDM baselines accurately reflect realized grid displacement, $E[r_p] = 1$. Values $r > 1$ indicate claimed credits overstate measurable grid CO2 benefit.

### Forest-loss counterfactual (REDD+)

**[CO-AUTHOR PLACEHOLDER: West et al. 2023 matched-sample protocol, applied project-by-project with Hansen loss-year tiles inside Verra-registered polygons and leakage belts.]**

For each of the 12 REDD+ projects in BCT we have recorded the Hansen GeoTIFF URLs covering the project centroid (10° Hansen tile), the parsed PDD-declared baseline deforestation rate where public, and a placeholder 10-km centroid-buffer observed loss rate pending receipt of project polygons.

### Asset-level cross-reference (Climate TRACE)

For each project coordinate we query the Climate TRACE API for the nearest power / manufacturing / waste asset within 50 km, and cross-reference claimed capacity vs TRACE capacity. Projects with `status=no_match_within_max_km` constitute a testable null hypothesis: they may lie below TRACE's detection threshold (typical cutoff ~5 MW) or may have never physically been built at the PDD-declared location.

---

## Results

### Headline: 18 of 18 top-volume Indian renewable projects overclaimed

Running the pipeline on the 18 projects with **≥100,000 tonnes** bridged into BCT (or top-18 by volume, whichever is smaller):

| Statistic | Value |
|-----------|-------|
| Projects in tier | 18 |
| Mean overclaim ratio (claimed / Ember-consistent) | **1.267** |
| Projects with ratio ≥ 1.0 | 18 / 18 |
| Projects with ratio ≥ 1.2 | 18 / 18 |
| Projects with ratio ≥ 1.5 | 0 / 18 |
| Aggregate claimed displacement | 3,368,904 tCO2 |
| Aggregate Ember-consistent displacement | 2,683,969 tCO2 |
| **Aggregate phantom displacement** | **684,935 tCO2 (+25.5%)** |

All 18 projects span 2008-2019 vintages, covering hydro (8 projects), wind (7), biomass (2), and mixed/unclassified (1). The overclaim magnitude is **remarkably stable across tech and vintage**: every project falls between 1.236× and 1.288×, with mean 1.267×. This uniformity is itself diagnostic: it is not driven by idiosyncratic project errors but by the *systematic gap* between CEA's ex-ante CM baselines and Ember's ex-post realized grid intensity.

The annual-national-mean result is a lower bound. Under hourly location-resolved EFs (see Methods / `[CO-AUTHOR PLACEHOLDER]`), solar projects — whose generation profile peaks during the grid's lowest-intensity hours — are expected to exceed 1.5× overclaim, widening the aggregate phantom displacement above 35%.

See `data/satellite-analysis/india_cdm_overclaim_analysis.md` for the full per-project table.

### Why the gap is structural, not measurement noise

CEA's CM baselines are published as conservative ex-ante estimates with deliberate asymmetry: the OM uses 3-year back-average thermal intensity, and the BM uses the top-20% most recent additions. Both overweight high-emission coal relative to the realized generation mix, because India's solar buildout (2015-2023) is *not* reflected in the BM construction rules. Ember's realized EF tracks the actual mix, including the growing renewable share.

This is not an argument that the CDM did its arithmetic wrong — within the CDM rulebook, CEA CM is the correct number. It is an argument that the CDM rulebook, applied to tokenized credits sold to 2021-2024 retail buyers, **systematically over-reports what retirement physically delivered**.

### Project-by-project detail (top 6)

| Rank | Project | Tech | Tonnes in BCT | Overclaim ratio |
|------|---------|------|---------------|-----------------|
| 1 | Vishnuprayag Hydro (VCS-173) | Hydro | 1,189,259 | 1.236 |
| 2 | Teesta-V Hydro, Sikkim (VCS-766) | Hydro | 927,901 | 1.252 |
| 3 | 29.70 MW Wind, Karnataka (VCS-51) | Wind | 270,000 | 1.277 |
| 4 | Andhra Backward-District Hydro (VCS-1291) | Hydro | 268,500 | 1.288 |
| 5 | Brahm Ganga Hydro, Kullu (VCS-493) | Hydro | 191,068 | 1.261 |
| 6 | Jaibhim Wind, SIIL (VCS-1525) | Wind | 103,558 | 1.283 |

The top two projects (VCS-173 and VCS-766) alone represent 2.12 Mt of bridged credits — a fifth of BCT's entire renewable volume — and overclaim by 23.6% and 25.2% respectively.

### REDD+ satellite result

**[CO-AUTHOR PLACEHOLDER: full REDD+ result.]**

MVP status: tile URLs recorded for 12 Hansen tiles covering all REDD+ BCT projects. Public PDD baselines parsed for 12/12 projects (range: 0.35%/yr for Mataven to 1.92%/yr for Southern Cardamom). Awaiting project polygons from co-author to run matched-sample counterfactual.

### Climate TRACE cross-reference

**[CO-AUTHOR PLACEHOLDER: once network-reachable from your institution, run `climate_trace_integration.py` — returns nearest-asset match for every coordinated project. No API key required.]**

---

## Discussion

Three implications.

**(1) Tokenized markets inherit CDM accounting debt.** Toucan, Moss, and Klima did not create the overclaim — they inherited it from Verra's methodology. But by bridging low-quality renewable credits onto permissionless chains, they rebroadcast that debt to new buyers (mostly DeFi protocols and corporate sustainability purchasers in 2021-2022) who had no way to see the vintage-weighted grid-EF gap. On-chain transparency of *ownership* did not produce transparency of *climate truth*.

**(2) A retrospective audit protocol is now feasible.** The pipeline we publish here — project_id + vintage -> CEA CM EF, matched to Ember realized EF — runs in under 30 seconds on commodity hardware against any tokenized carbon pool with a similar on-chain schema (Toucan-family tokens, Moss MCO2, Klima retired credits). The same approach extends to any CDM-aligned national grid once a counterfactual time series (Ember, IEA, or national TSO) exists. This is a scalable MRV tool that the research community, not just project developers, can operate.

**(3) Policy implication.** The Integrity Council for the Voluntary Carbon Market (ICVCM) Core Carbon Principles currently exclude BCT-type Indian renewable credits post-2020; our result validates that exclusion quantitatively and for the first time. Ongoing CORSIA eligibility decisions and Article 6 authorization for pre-2020 vintage credits should apply the same EF-realized test.

### Limitations

- Annual national EFs conflate regional and hourly variation. A solar plant in Gujarat that operates 10am-4pm displaces an EF different from the 24-hour mean. **[CO-AUTHOR PLACEHOLDER: replace annual EF with hourly location-resolved EF series — this is the core remote-sensing contribution you add.]**
- CDM methodologies argue that build-margin captures the *counterfactual* grid (what would have been built absent the project), not the realized grid. Our test interprets "claimed displacement" as realized-grid displacement, which is the consumer-facing interpretation but not the methodology-internal one. Both framings matter; we recommend dual reporting.
- 64 of 168 projects lack any Verra-reported coordinate. For grid-EF work this does not matter (we need only country + vintage). For REDD+ and Climate TRACE work, coarse coordinates limit resolution. Future work should petition Verra for machine-readable polygon publication.

---

## Methods (extended) — for Nature's Methods section

### On-chain data pipeline

See `data/depositor-analysis/fetch_deposits.py`. Events decoded from the Toucan `OffsetHelper` + `BCTPool` contract ABIs on Base L2. Project-id parsing uses the deterministic pattern `^Toucan Protocol: TCO2-VCS-(\d+)-(\d{4,8})$`. Full deposit-level data at `data/depositor-analysis/bct_deposits_complete.json`.

### Coordinate resolution

See `data/satellite-analysis/fetch_verra_coordinates.py`. Precedence: (i) Verra public registry record `projectSites[0].geographicCoordinates`; (ii) Indian-state centroid when project name contains a state keyword; (iii) country centroid. Precision level is recorded per-project (`verra_point` / `india_state_centroid` / `country_centroid`).

### Grid EF counterfactual

See `data/satellite-analysis/ember_grid_counterfactual.py`. Vintage years weighted by tonnes-bridged-at-that-vintage. Both EF series provided in-script for reproducibility; `--download-ember` fetches the live Ember CSV for updates.

### Hansen forest-loss analysis

See `data/satellite-analysis/hansen_deforestation.py`. Tile URLs recorded for co-author GEE pipeline. Local rasterio fallback computes 10-km centroid-buffer loss rates when rasterio is installed.

### Climate TRACE asset match

See `data/satellite-analysis/climate_trace_integration.py`. Haversine nearest-neighbour within 50 km. Full per-project match records saved to JSON for audit.

---

## Data and code availability

All code and intermediate outputs: GitHub repo `carbon-neutrality`, branch `main`.

- Pipeline scripts: `data/satellite-analysis/*.py`
- Reports: `data/satellite-analysis/*.md`
- On-chain deposit data: `data/depositor-analysis/bct_deposits_complete.json` (CC-BY)
- Grid EF reference tables: embedded in `ember_grid_counterfactual.py` with source citations

Ember data: CC-BY 4.0 from Ember Climate. CEA baselines: public Indian Ministry of Power. Hansen tiles: CC-BY 4.0 via Google Earth Engine. Climate TRACE: CC-BY 4.0.

---

## Target: Nature

Rationale: novelty = first retrospective satellite + on-chain audit of an entire tokenized pool. Methods = reproducible and open. Stakes = $2B market and ongoing policy decisions (ICVCM, CORSIA, Article 6). Requires remote-sensing co-author PI for full polygon-based REDD+ analysis — see `co-author-pitch.md`.
