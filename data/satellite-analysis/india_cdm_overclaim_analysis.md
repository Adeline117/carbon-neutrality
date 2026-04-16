# Indian CDM Grid-EF Counterfactual: BCT Renewable Credits

**Pipeline:** `data/satellite-analysis/ember_grid_counterfactual.py`
**Ember EF source:** `reference_table`
**CDM CM-EF source:** CEA CO2 Baseline Database, India (v5–v19)

## Method

For each Indian renewable project deposited into BCT, we back-compute the implied generation using the CDM Combined Margin EF published by CEA at the project vintage:

    MWh_implied = claimed_tCO2 / EF_CDM_CM(vintage)

We then apply Ember's realized Indian grid EF at the same vintage to that MWh to obtain the counterfactual displacement:

    tCO2_ember = MWh_implied × EF_Ember(vintage)

The overclaim ratio is `claimed / ember_consistent`. A ratio of 1.20 means the project claimed 20% more physical grid displacement than Ember's realized grid-mix data supports.

## Emission-factor series used

| Year | CDM CM-EF (tCO2/MWh) | Ember realized (tCO2/MWh) | Gap (%) |
|------|----------------------|---------------------------|---------|
| 2008 | 0.920 | 0.766 | +20.1% |
| 2009 | 0.940 | 0.758 | +24.0% |
| 2010 | 0.940 | 0.736 | +27.7% |
| 2011 | 0.930 | 0.720 | +29.2% |
| 2012 | 0.920 | 0.720 | +27.8% |
| 2013 | 0.910 | 0.710 | +28.2% |
| 2014 | 0.910 | 0.706 | +28.9% |
| 2015 | 0.900 | 0.713 | +26.2% |
| 2016 | 0.880 | 0.699 | +25.9% |
| 2017 | 0.860 | 0.676 | +27.2% |
| 2018 | 0.850 | 0.670 | +26.9% |
| 2019 | 0.820 | 0.655 | +25.2% |
| 2020 | 0.790 | 0.631 | +25.2% |
| 2021 | 0.780 | 0.637 | +22.4% |
| 2022 | 0.760 | 0.633 | +20.1% |
| 2023 | 0.730 | 0.619 | +17.9% |

## Top projects by BCT volume (n=18)

| # | Project ID | Name (trimmed) | Tech | Tonnes in BCT | Vintages | EF_CDM | EF_Ember | Overclaim ratio |
|---|-----------|----------------|------|---------------|----------|-------|---------|-----------------|
| 1 | 173 | Vishnuprayag Hydro-electric Project (VHEP) by Ja | hydro | 1,189,259 | 2008,2013,2014… | 0.911 | 0.737 | **1.236** |
| 2 | 766 | Teesta- V Hydro Power project in Sikkim | hydro | 927,901 | 2008,2009,2010 | 0.935 | 0.747 | **1.252** |
| 3 | 51 | 29.70 MW Wind Power project in Karnataka India | wind | 270,000 | 2012,2013,2014… | 0.910 | 0.712 | **1.277** |
| 4 | 1291 | Hydro Power Project in backward district of Andh | hydro | 268,500 | 2013,2014 | 0.910 | 0.707 | **1.288** |
| 5 | 493 | 5 MW Brahm Ganga Hydro – Electric Project at Kul | hydro | 191,068 | 2008,2010,2011… | 0.909 | 0.721 | **1.261** |
| 6 | 1525 | Wind power project at Jaibhim by SIIL | wind | 103,558 | 2011,2012 | 0.924 | 0.720 | **1.283** |
| 7 | 1160 | 6.5 MW cogeneration project in Akbarpur, Punjab | biomass | 86,030 | 2012,2013,2014 | 0.913 | 0.711 | **1.283** |
| 8 | 132 | 9 MW Neria Hyrdroelectric project, Karnataka, In | other | 62,893 | 2011,2013,2014… | 0.910 | 0.711 | **1.280** |
| 9 | 566 | 10 MW Wind Power Project in Maharashtra by Deepa | wind | 60,597 | 2012,2013,2014… | 0.908 | 0.712 | **1.275** |
| 10 | 274 | Hanuman Ganga Hydro (4.95 MW) Plant at Uttarakha | hydro | 39,492 | 2010,2011,2012… | 0.923 | 0.720 | **1.281** |
| 11 | 655 | 24.8 MW Wind power project by Belgaum Wind Farms | wind | 36,251 | 2016 | 0.880 | 0.699 | **1.259** |
| 12 | 1742 | Hydroelectric Project in Kinnaur District in Him | hydro | 33,134 | 2016 | 0.880 | 0.699 | **1.259** |
| 13 | 631 | 13.25 MW Wind Power Generation by RMTL, in Kutch | wind | 31,011 | 2014,2015,2016 | 0.902 | 0.710 | **1.270** |
| 14 | 669 | Wind Energy project by Ramco group in india | wind | 26,055 | 2013 | 0.910 | 0.710 | **1.282** |
| 15 | 624 | 15 MW Biomass Residue Based Power Project at Gha | biomass | 15,347 | 2009 | 0.940 | 0.758 | **1.240** |
| 16 | 682 | Wind Power Project at Anthiyur, Tamil Nadu | wind | 10,226 | 2009 | 0.940 | 0.758 | **1.240** |
| 17 | 927 | 13.75 MW wind power project in Davangere, Karnat | wind | 9,863 | 2010 | 0.940 | 0.736 | **1.277** |
| 18 | 1190 | Wind power project in Gujarat | wind | 7,719 | 2017,2018 | 0.852 | 0.671 | **1.269** |

## Headline statistics

- Projects analyzed in top tier: **18**
- Mean overclaim ratio: **1.267**
- Projects with overclaim ratio ≥ 1.0: **18 / 18**
- Projects with overclaim ratio ≥ 1.2: **18 / 18**
- Projects with overclaim ratio ≥ 1.5: **0 / 18**

- Aggregate claimed displacement (top 18): **3,368,904 tCO2**
- Ember-consistent displacement: **2,683,969 tCO2**
- Aggregate overclaim: **25.5%** (= 684,935 tCO2 of phantom displacement)

## Caveats

- CDM CM-EF is a conservative ex-ante baseline; some projects used regional (Southern/Northern/Eastern/Western) EFs rather than the national CM. Regional values can differ ±5% from the national CM in either direction.
- Ember's realized EF reflects *operating* grid mix, not *build-margin* grid mix. CDM methodology argues the build-margin captures the counterfactual of what would have been built. We discuss this in the paper's Limitations.
- Implied MWh from claimed tCO2 may double-count projects that also claim non-electricity benefits (e.g. co-gen heat). Those are flagged tech=biomass.
- This MVP uses annual national EFs. Paper 4 will swap in hourly location-resolved EFs from the remote-sensing PI co-author.
