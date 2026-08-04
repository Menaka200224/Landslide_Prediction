# Data sources

Every dataset used in this project must be logged here: origin, resolution, date obtained,
license/access terms. This matters both for reproducibility and for DMC/NBRO-facing
credibility — anyone should be able to trace exactly where every layer came from.

Fill in the "Obtained" and "License / access" columns as you acquire each dataset.
Nothing in `data/raw/` is committed to git — this file is the record of what should be there.

## Study area

| Item | Source | Resolution / format | Obtained | License / access |
|---|---|---|---|---|
| District & DS division boundaries | Sri Lanka Survey Department, or HDX/OCHA administrative boundaries (COD-AB) | Vector (polygon) | | |

## Terrain

| Item | Source | Resolution / format | Obtained | License / access |
|---|---|---|---|---|
| DEM | SRTM 30m (USGS EarthExplorer) or ASTER GDEM | 30m raster | | Public domain (SRTM) |
| Slope, aspect, curvature, SPI, TWI, STI | Derived from DEM (this project, `notebooks/02_terrain.ipynb`) | 30m raster | derived | derived |

## Climate

| Item | Source | Resolution / format | Obtained | License / access |
|---|---|---|---|---|
| Rainfall (satellite) | CHIRPS (Climate Hazards Group) | ~5km daily/monthly raster | | Free, open |
| Rainfall (station) | Department of Meteorology, Sri Lanka | Point, station records | | Request via DMC/institutional channel |
| NDVI / land cover | Sentinel-2 (via Copernicus/GEE) or ESA WorldCover | 10-20m raster | | Free, open |

## Geology & soil

| Item | Source | Resolution / format | Obtained | License / access |
|---|---|---|---|---|
| Geology / lithology | Geological Survey and Mines Bureau (GSMB) | Vector (polygon) | | Request required |
| Soil type & thickness | GSMB / FAO soil data | Vector or raster | | |

## Hydrology & infrastructure

| Item | Source | Resolution / format | Obtained | License / access |
|---|---|---|---|---|
| Rivers, streams, roads | OpenStreetMap (via Overpass or Geofabrik extracts) | Vector | | ODbL |

## Landslide inventory (labels)

| Item | Source | Resolution / format | Obtained | License / access |
|---|---|---|---|---|
| Landslide occurrence points | NBRO landslide database / Landslide Research and Risk Management Division | Vector (point, head-scarp centroid convention) | | Request required — contact NBRO directly, or via DMC |
| Non-landslide (negative) samples | Generated in this project (`notebooks/05_labels.ipynb`) via random sampling outside landslide buffer zones | Vector (point) | derived | derived |

## Operational reference (not a model input — design reference)

| Item | Source | Notes |
|---|---|---|
| Landslide Early Warning bulletins | NBRO Landslide Research and Risk Management Division | Rainfall-threshold warnings (Yellow >75mm/24hr, Amber >100mm, Red >150mm) issued at DS-division level. Used as (a) a design reference so this project's output format matches what DMC already consumes, and (b) potentially as a historical validation series if archived bulletins can be obtained — see `notebooks/09b_rainfall_trigger.ipynb`. |

## Notes on access

Several of the above (NBRO inventory, GSMB geology, Met Dept station rainfall) require direct
institutional requests rather than open download. Since this research is framed for DMC, the
most efficient path is usually to request these through DMC's existing relationship with NBRO
rather than approaching NBRO independently — worth raising early, since these requests can
take time to process.
