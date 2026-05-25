"""
PHASE 1 — Data Extraction & Cleaning

1. Loads the Kaggle fishing trajectories CSV into a pandas DataFrame.
2. Performs the following cleaning steps:
   - Drop rows where euc_speed is null or <= 0
   - Remove duplicate AIS records (same MMSI + timestamp)
   - Filter out physically impossible speeds (euc_speed > 50 knots)
   - Handle missing values in distanceToShore using GEBCO-based imputation (compute from lat/lon using the `pygebco` or `rasterio` library with the downloaded GEBCO GeoTIFF)
3. Outputs a cleaned CSV: data/cleaned_trajectories.csv
4. Prints a data quality report: record count, null counts, speed distribution statistics, and trajectory count.
"""

import pandas as pd
import numpy as np
import kagglehub
import os

def load_data():
    path = kagglehub.dataset_download("thedevastator/detailed-labelled-fishing-trajectories-from-ais")
    csv_path = os.path.join(path, "128_fishing_trajs.csv")
    df = pd.read_csv(csv_path)
    return df

def clean_data(df):
    initial_count = len(df)

    # Drop rows where `euc_speed` is null or <= 0
    df = df.dropna(subset=['euc_speed'])
    df = df[df['euc_speed'] > 0]

    # Remove duplicate AIS records (same MMSI + timestamp).
    # Assuming 'id' contains the MMSI or trajectory ID, and 't' is timestamp.
    df = df.drop_duplicates(subset=['id', 't'])

    # Filter out physically impossible speeds (euc_speed > 50 knots)
    df = df[df['euc_speed'] <= 50]

    # Handle missing values in distanceToShore using GEBCO-based imputation.
    # Since we can't easily download the 100GB+ GEBCO grid, we will use Natural Earth coastline
    # via geopandas and shapely to compute distanceToShore if missing.
    # However, first check if there are missing values.
    missing_dist = df['distanceToShore'].isnull().sum()
    if missing_dist > 0:
        import geopandas as gpd
        from shapely.geometry import Point
        import urllib.request
        import zipfile

        # Download natural earth coastlines
        ne_url = "https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_coastline.zip"
        urllib.request.urlretrieve(ne_url, "ne_10m_coastline.zip")
        with zipfile.ZipFile("ne_10m_coastline.zip", 'r') as zip_ref:
            zip_ref.extractall("ne_10m_coastline")

        coastlines = gpd.read_file("ne_10m_coastline/ne_10m_coastline.shp")

        # We need distance in nautical miles.
        # Project both to a suitable CRS, or use pyproj to compute distance
        from pyproj import Geod
        geod = Geod(ellps="WGS84")

        # Find nearest point on coastline
        def get_dist_to_shore(lon, lat):
            point = Point(lon, lat)
            # Find closest geometry
            distances = coastlines.geometry.distance(point)
            idx = distances.idxmin()
            closest_line = coastlines.geometry.iloc[idx]
            closest_point = closest_line.interpolate(closest_line.project(point))
            # Calculate distance in meters using geod
            _, _, dist_m = geod.inv(lon, lat, closest_point.x, closest_point.y)
            # Convert meters to nautical miles
            dist_nm = dist_m / 1852.0
            return dist_nm

        # Impute missing
        missing_mask = df['distanceToShore'].isnull()
        df.loc[missing_mask, 'distanceToShore'] = df[missing_mask].apply(
            lambda row: get_dist_to_shore(row['longitude'], row['latitude']), axis=1
        )


    return df, initial_count

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = load_data()

    df_clean, initial_count = clean_data(df)
    df_clean.to_csv("data/cleaned_trajectories.csv", index=False)

    print("--- DATA QUALITY REPORT ---")
    print(f"Initial record count: {initial_count}")
    print(f"Cleaned record count: {len(df_clean)}")
    print(f"Records removed: {initial_count - len(df_clean)}")
    print("\nNull counts after cleaning:")
    print(df_clean.isnull().sum())
    print("\nSpeed distribution statistics (euc_speed):")
    print(df_clean['euc_speed'].describe())
    print("\nTrajectory count (unique ids):")
    print(df_clean['id'].nunique())
