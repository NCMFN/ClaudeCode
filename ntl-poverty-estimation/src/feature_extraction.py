import pandas as pd
import numpy as np
from shapely.geometry import Point
from rasterstats import zonal_stats

def extract_features(dhs_geo, wealth_df, raster_path="data/processed/ntl_annual_median.tif"):
    # Apply 5km urban / 10km rural displacement buffer per DHS methodology
    dhs_geo['geometry_buffer'] = dhs_geo.apply(
        lambda row: row.geometry.buffer(0.045 if row['URBAN_RURA'] == 'U' else 0.090),
        axis=1
    )

    stats_list = zonal_stats(
        vectors=dhs_geo['geometry_buffer'],
        raster=raster_path,
        stats=["mean", "max", "std", "median", "count"],
        nodata=np.nan
    )

    stats_df = pd.DataFrame(stats_list)
    stats_df.columns = ['ntl_mean', 'ntl_max', 'ntl_std', 'ntl_median', 'ntl_pixel_count']

    feature_df = pd.concat([
        dhs_geo[['DHSCLUST', 'LATNUM', 'LONGNUM', 'URBAN_RURA']],
        stats_df
    ], axis=1)

    # Derived features
    feature_df['ntl_cv']         = feature_df['ntl_std'] / (feature_df['ntl_mean'] + 1e-6)
    feature_df['ntl_log_mean']   = np.log1p(feature_df['ntl_mean'])
    feature_df['ntl_brightness'] = feature_df['ntl_max'] / (feature_df['ntl_mean'] + 1e-6)

    # Merge DHS wealth score
    feature_df = feature_df.merge(
        wealth_df.groupby('HV001')['HV271'].mean().reset_index().rename(
            columns={'HV001': 'DHSCLUST', 'HV271': 'wealth_score'}
        ),
        on='DHSCLUST'
    )

    feature_df.to_csv("data/processed/feature_matrix.csv", index=False)
    return feature_df
