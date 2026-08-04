"""Geospatial helpers shared across notebooks.

Design goal: every function here is written assuming limited RAM. Rasters are read
windowed where possible, clipped to the AOI as early as possible, and written back out
as Cloud-Optimized GeoTIFFs (COG) so the next notebook can reopen them cheaply.
"""
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask as rio_mask
from rasterio.warp import calculate_default_transform, reproject, Resampling


def load_aoi(path: str | Path, dissolve: bool = True) -> gpd.GeoDataFrame:
    """Load the study-area boundary and optionally dissolve to a single polygon.

    Parameters
    ----------
    path
        Path to a vector file (GeoPackage, shapefile, etc.) containing the AOI,
        e.g. the four target districts.
    dissolve
        If True, merge all features into one polygon — most raster clipping
        functions want a single geometry rather than a multi-row GeoDataFrame.
    """
    aoi = gpd.read_file(path)
    if dissolve:
        aoi = aoi.dissolve()
    return aoi


def clip_raster_to_aoi(
    src_path: str | Path,
    aoi: gpd.GeoDataFrame,
    dst_path: str | Path,
    dtype: str | None = None,
    nodata: float | None = None,
) -> Path:
    """Clip a raster to the AOI boundary and write it out as a COG.

    This should typically be the *first* operation run on any newly downloaded
    raster, before any further processing — it's the single biggest RAM saver
    in this pipeline, especially for country- or region-scale source rasters.

    Parameters
    ----------
    src_path
        Path to the source raster (e.g. a full SRTM tile or CHIRPS global grid).
    aoi
        AOI GeoDataFrame, ideally already in the same CRS as the raster (this
        function reprojects the AOI to match if not).
    dst_path
        Output path. Parent directories are created if missing.
    dtype
        Optional dtype to downcast to (e.g. "float32", "int16"). Skip this only
        if you specifically need the source precision.
    nodata
        Nodata value to set on the output, if different from the source.
    """
    dst_path = Path(dst_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(src_path) as src:
        aoi_proj = aoi.to_crs(src.crs) if aoi.crs != src.crs else aoi
        out_image, out_transform = rio_mask(src, aoi_proj.geometry, crop=True)
        out_meta = src.meta.copy()

        if dtype is not None:
            out_image = out_image.astype(dtype)

        out_meta.update(
            {
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
                "dtype": dtype or out_meta["dtype"],
                "nodata": nodata if nodata is not None else out_meta.get("nodata"),
                "compress": "deflate",
                "tiled": True,
                "blockxsize": 256,
                "blockysize": 256,
            }
        )

    with rasterio.open(dst_path, "w", **out_meta) as dst:
        dst.write(out_image)

    return dst_path


def reproject_raster(
    src_path: str | Path,
    dst_path: str | Path,
    dst_crs: str = "EPSG:32644",  # WGS84 / UTM zone 44N — matches Sri Lanka's extent
    resampling: Resampling = Resampling.bilinear,
) -> Path:
    """Reproject a raster to a target CRS.

    Sri Lanka spans UTM zone 44N — worth standardizing every layer to this CRS
    (rather than leaving some in geographic WGS84) so distances and areas computed
    downstream are metric, not degrees.
    """
    dst_path = Path(dst_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(src_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds
        )
        meta = src.meta.copy()
        meta.update(
            {"crs": dst_crs, "transform": transform, "width": width, "height": height}
        )

        with rasterio.open(dst_path, "w", **meta) as dst:
            for band in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, band),
                    destination=rasterio.band(dst, band),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=resampling,
                )
    return dst_path


def sample_raster_at_points(
    raster_path: str | Path, points: gpd.GeoDataFrame, band: int = 1
) -> np.ndarray:
    """Read only the pixel values under each point — never loads the full raster.

    This is the memory-safe equivalent of the "add grid values to points" QGIS
    step: rasterio.sample() streams values one point at a time from disk.
    """
    with rasterio.open(raster_path) as src:
        pts_proj = points.to_crs(src.crs) if points.crs != src.crs else points
        coords = [(geom.x, geom.y) for geom in pts_proj.geometry]
        values = np.array([v[band - 1] for v in src.sample(coords)])
    return values


def free_memory(*objects) -> None:
    """Explicitly drop references and collect garbage.

    Call this at the end of a notebook cell once large arrays/GeoDataFrames have
    been written to disk and are no longer needed in this session — don't rely
    on implicit garbage collection in a long-running kernel.
    """
    import gc

    for obj in objects:
        del obj
    gc.collect()
