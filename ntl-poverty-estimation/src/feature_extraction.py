import pandas as pd
import geopandas as gpd
import numpy as np
from rasterstats import zonal_stats
from shapely.geometry import Point
import os
from typing import Optional

def extract_features(dhs_geo: gpd.GeoDataFrame, wealth_df: pd.DataFrame, raster_path: str, output_csv: str) -> Optional[pd.DataFrame]:
    """
    Buffers DHS clusters, extracts zonal statistics from NTL raster, and merges with wealth index.

    Args:
        dhs_geo (gpd.GeoDataFrame): GeoDataFrame containing DHS cluster coordinates.
        wealth_df (pd.DataFrame): DataFrame containing wealth index per cluster.
        raster_path (str): Path to the NTL annual median GeoTIFF.
        output_csv (str): Path to save the extracted feature matrix.

    Returns:
        Optional[pd.DataFrame]: The extracted feature DataFrame, or None if inputs are empty or missing.
    """
    if dhs_geo.empty or wealth_df.empty:
        print("DHS DataFrames are empty. Skipping feature extraction.")
        return None

    if not os.path.exists(raster_path):
        print(f"Raster file {raster_path} not found. Skipping feature extraction.")
        return None

    try:
        # Buffer coordinates: 5km (0.045 deg) for urban, 10km (0.090 deg) for rural
        dhs_geo_buffered = dhs_geo.copy()
        dhs_geo_buffered['geometry'] = dhs_geo_buffered.apply(
            lambda row: row.geometry.buffer(0.045 if row['URBAN_RURA'] == 'U' else 0.090),
            axis=1
        )

        stats_list = zonal_stats(
            vectors=dhs_geo_buffered['geometry'],
            raster=raster_path,
            stats=["mean", "max", "std", "median", "count"],
            nodata=np.nan
        )

        stats_df = pd.DataFrame(stats_list)
        stats_df.columns = ['ntl_mean', 'ntl_max', 'ntl_std', 'ntl_median', 'ntl_pixel_count']

        feature_df = pd.concat([
            dhs_geo[['DHSCLUST', 'LATNUM', 'LONGNUM', 'URBAN_RURA']].reset_index(drop=True),
            stats_df
        ], axis=1)

        # Derived features
        feature_df['ntl_cv'] = feature_df['ntl_std'] / (feature_df['ntl_mean'] + 1e-6)
        feature_df['ntl_log_mean'] = np.log1p(feature_df['ntl_mean'].clip(lower=0)) # Ensure non-negative
        feature_df['ntl_brightness'] = feature_df['ntl_max'] / (feature_df['ntl_mean'] + 1e-6)

        # Merge DHS wealth score
        wealth_agg = wealth_df.groupby('HV001')['wealth_score'].mean().reset_index().rename(
            columns={'HV001': 'DHSCLUST'}
        )
        feature_df = feature_df.merge(wealth_agg, on='DHSCLUST')

        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        feature_df.to_csv(output_csv, index=False)
        return feature_df

    except Exception as e:
        print(f"Error during feature extraction: {e}")
        return None
