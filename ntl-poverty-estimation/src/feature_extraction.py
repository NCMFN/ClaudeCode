import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from rasterstats import zonal_stats
import numpy as np
import warnings

warnings.filterwarnings("ignore")

def extract_features():
    wealth_df_path = "data/processed/wealth_df.csv"
    dhs_geo_shp = "data/processed/dhs_geo.shp"
    dhs_geo_csv = "data/processed/dhs_geo.csv"
    ntl_tif = "data/processed/ntl_annual_median.tif"

    if os.path.exists(wealth_df_path):
        wealth_df = pd.read_csv(wealth_df_path)
    else:
        print("wealth_df.csv not found, proceeding with empty dataframe.")
        wealth_df = pd.DataFrame(columns=['HHID', 'HV001', 'HV002', 'HV271'])

    if os.path.exists(dhs_geo_shp):
        dhs_geo = gpd.read_file(dhs_geo_shp)
    elif os.path.exists(dhs_geo_csv):
        dhs_geo = pd.read_csv(dhs_geo_csv)
        if dhs_geo.empty:
            dhs_geo = gpd.GeoDataFrame(columns=['DHSCLUST', 'LATNUM', 'LONGNUM', 'URBAN_RURA', 'geometry'])
        else:
            dhs_geo = gpd.GeoDataFrame(dhs_geo, geometry=gpd.points_from_xy(dhs_geo.LONGNUM, dhs_geo.LATNUM))
    else:
        print("DHS GEO data not found, returning empty GeoDataFrame.")
        dhs_geo = gpd.GeoDataFrame(columns=['DHSCLUST', 'LATNUM', 'LONGNUM', 'URBAN_RURA', 'geometry'])

    if dhs_geo.empty or wealth_df.empty or not os.path.exists(ntl_tif):
        print("Required inputs are missing or empty. Creating empty feature matrix.")
        feature_df = pd.DataFrame(columns=['DHSCLUST', 'LATNUM', 'LONGNUM', 'URBAN_RURA',
                                           'ntl_mean', 'ntl_max', 'ntl_std', 'ntl_median', 'ntl_pixel_count',
                                           'ntl_cv', 'ntl_log_mean', 'ntl_brightness', 'wealth_score'])
        feature_df.to_csv("data/processed/feature_matrix.csv", index=False)
        return

    # Buffer DHS Cluster Coordinates
    dhs_geo['geometry_buffer'] = dhs_geo.apply(
        lambda row: row.geometry.buffer(0.045 if row['URBAN_RURA'] == 'U' else 0.090),
        axis=1
    )

    # Extract Zonal Statistics
    try:
        stats_list = zonal_stats(
            vectors=dhs_geo['geometry_buffer'],
            raster=ntl_tif,
            stats=["mean", "max", "std", "median", "count"],
            nodata=np.nan
        )
    except Exception as e:
        print(f"Zonal stats failed: {e}")
        stats_list = [{'mean': np.nan, 'max': np.nan, 'std': np.nan, 'median': np.nan, 'count': np.nan} for _ in range(len(dhs_geo))]

    stats_df = pd.DataFrame(stats_list)
    stats_df.columns = ['ntl_mean', 'ntl_max', 'ntl_std', 'ntl_median', 'ntl_pixel_count']

    # Derived Feature Matrix
    feature_df = pd.concat([
        dhs_geo[['DHSCLUST', 'LATNUM', 'LONGNUM', 'URBAN_RURA']].reset_index(drop=True),
        stats_df.reset_index(drop=True)
    ], axis=1)

    # Derived features
    feature_df['ntl_cv'] = feature_df['ntl_std'] / (feature_df['ntl_mean'] + 1e-6)
    feature_df['ntl_log_mean'] = np.log1p(feature_df['ntl_mean'])
    feature_df['ntl_brightness'] = feature_df['ntl_max'] / (feature_df['ntl_mean'] + 1e-6)

    # Merge DHS wealth score
    if not wealth_df.empty:
        wealth_agg = wealth_df.groupby('HV001')['HV271'].mean().reset_index().rename(
            columns={'HV001': 'DHSCLUST', 'HV271': 'wealth_score'}
        )
        feature_df = feature_df.merge(wealth_agg, on='DHSCLUST', how='left')
    else:
        feature_df['wealth_score'] = np.nan

    feature_df.to_csv("data/processed/feature_matrix.csv", index=False)

if __name__ == "__main__":
    extract_features()
