# West et al. 2023 Replication Data

## Source

Thales A. P. West, *Replication Data for: Action needed to make carbon
offsets from forest conservation work for climate change mitigation*
(West et al. 2023, *Science* **381**, 873-877).

- **DOI:** 10.34894/IQC9LM
- **DataverseNL landing:** https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/IQC9LM
- **Direct download:** https://dataverse.nl/api/access/datafile/374696 (50.9 MB, 7z archive)
- **Contact:** Dr. Thales A. P. West <t.a.pupowest@vu.nl>

## Files shipped with this repo (git-tracked)

### `shapefiles_slim/` (~0.7 MB, 4 files)

Per-BCT-project project polygons (REDD=1 rows only) for the 4 projects
that have shapefile coverage:

- `DRC_polygons.shp`      → VCS 934 (Mai Ndombe)
- `Peru_polygons.shp`     → VCS 985 (Cordillera Azul)
- `Colombia_polygons.shp` → VCS 1566 (Mataven)
- `Cambodia_polygons.shp` → VCS 1650 (Keo Seima)

VCS 1748 (Southern Cardamom) is absent from the public shapefile
release but is present in the CSV. Its project polygon for our purposes
falls back to the PDD centroid disc.

### `csv_slim/` (~12 MB, 5 files)

Per-BCT-project slices of the per-polygon-per-year covariate CSVs for
all 5 BCT REDD+ projects with West 2023 coverage (934, 985, 1566, 1650,
1748). Used by `matched_synthetic_control.py` Estimator A.

## Files NOT shipped (gitignored; recreate locally if needed)

- `shapefiles/` — full 142 MB shapefiles with all REDD+ and candidate-
  control polygons for 6 countries.
- `csv/` — full 91 MB country-level CSVs.

## How to regenerate the full archive

```sh
mkdir -p /tmp/west2023 && cd /tmp/west2023
curl -o data.7z https://dataverse.nl/api/access/datafile/374696

python3 -c "
import py7zr
with py7zr.SevenZipFile('data.7z') as z: z.extractall('.')
with py7zr.SevenZipFile('West et al. (2023) data/Shapefiles.7z') as z:
    z.extractall('West et al. (2023) data')
with py7zr.SevenZipFile('West et al. (2023) data/Main datasets.7z') as z:
    z.extractall('West et al. (2023) data')
"

# Then copy to the project:
cp -r "West et al. (2023) data/Shapefiles/"* \
     /path/to/repo/data/satellite-analysis/west2023_data/shapefiles/
cp "West et al. (2023) data/Main datasets/"*.csv \
     /path/to/repo/data/satellite-analysis/west2023_data/csv/
```

## How to regenerate the slim slices

```python
import geopandas as gpd
import pandas as pd
import os

BCT = {
    'DRC_polygons.shp':      ['934'],
    'Peru_polygons.shp':     ['985'],
    'Colombia_polygons.shp': ['1566'],
    'Cambodia_polygons.shp': ['1650'],
}
for fname, ids in BCT.items():
    gdf = gpd.read_file(f'shapefiles/{fname}')
    mask = gdf['ID'].astype(str).isin(ids) & gdf['REDD'].astype(str).eq('1')
    gdf[mask].to_file(f'shapefiles_slim/{fname}')

CSV = {
    '934':  'DRC_synth_control_data.csv',
    '985':  'Peru_synth_control_data.csv',
    '1566': 'Colombia_synth_control_data.csv',
    '1650': 'cambodia_synth_control_data.csv',
    '1748': 'cambodia_synth_control_data.csv',
}
for pid, fname in CSV.items():
    df = pd.read_csv(f'csv/{fname}')
    df[df['ID']==int(pid)].to_csv(
        f'csv_slim/{pid}_{fname.replace(".csv","")}.csv', index=False)
```
