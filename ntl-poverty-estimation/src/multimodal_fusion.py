import ee
import os
import pandas as pd
import geopandas as gpd
from rasterstats import zonal_stats
from typing import Optional

def fetch_ndvi_data(study_region: ee.Geometry, output_prefix: str) -> bool:
    """
    Fetches MODIS NDVI data using Earth Engine. Fails gracefully if EE is unauthenticated.

    Args:
        study_region (ee.Geometry): Target region geometry.
        output_prefix (str): Prefix for EE export task description.

    Returns:
        bool: True if task started successfully, False otherwise.
    """
    try:
        ee.Initialize()
    except Exception as e:
        print(f"Earth Engine authentication failed: {e}. Skipping NDVI fusion.")
        return False

    try:
        ndvi = ee.ImageCollection("MODIS/061/MOD13A3") \
                 .filterDate("2021-01-01", "2022-12-31") \
                 .select("NDVI") \
                 .mean() \
                 .multiply(0.0001)

        task = ee.batch.Export.image.toDrive(
            image=ndvi,
            description=f"{output_prefix}_MODIS_NDVI_annual",
            scale=1000,
            region=study_region,
            fileFormat="GeoTIFF"
        )
        task.start()
        print(f"Started Earth Engine export task for NDVI to Drive: {output_prefix}_MODIS_NDVI_annual")
        return True
    except Exception as e:
        print(f"Error starting Earth Engine task: {e}")
        return False

def append_ndvi_stats(feature_df: pd.DataFrame, dhs_geo: gpd.GeoDataFrame, ndvi_raster_path: str) -> pd.DataFrame:
    """
    Appends NDVI zonal statistics to the feature matrix.
    Returns original feature_df if raster is missing.

    Args:
        feature_df (pd.DataFrame): Existing feature matrix.
        dhs_geo (gpd.GeoDataFrame): Buffered DHS geometries.
        ndvi_raster_path (str): Path to local NDVI GeoTIFF.

    Returns:
        pd.DataFrame: Updated feature matrix.
    """
    if not os.path.exists(ndvi_raster_path):
        print(f"NDVI raster {ndvi_raster_path} not found. Returning original features without NDVI.")
        return feature_df

    try:
        ndvi_stats = zonal_stats(dhs_geo['geometry'], ndvi_raster_path, stats=["mean", "std"])
        feature_df['ndvi_mean'] = [s['mean'] for s in ndvi_stats]
        feature_df['ndvi_std']  = [s['std']  for s in ndvi_stats]
        return feature_df
    except Exception as e:
        print(f"Error extracting NDVI stats: {e}")
        return feature_df
