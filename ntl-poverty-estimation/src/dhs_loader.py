import pandas as pd
import geopandas as gpd
import os
from typing import Tuple, Optional

def load_dhs_data(hr_path: str, geo_path: str) -> Tuple[pd.DataFrame, gpd.GeoDataFrame]:
    """
    Loads DHS Household Recode (HR) data and Geographic (GE) data.
    Gracefully returns empty dataframes if files are missing, ensuring no synthetic data generation.

    Args:
        hr_path (str): File path to DHS HR DTA file.
        geo_path (str): File path to DHS GE shapefile.

    Returns:
        Tuple[pd.DataFrame, gpd.GeoDataFrame]: Tuple containing wealth dataframe and GPS coordinates GeoDataFrame.
    """
    if not os.path.exists(hr_path):
        print(f"Warning: DHS HR file {hr_path} not found. Returning empty DataFrame.")
        wealth_df = pd.DataFrame(columns=['HHID', 'HV001', 'HV002', 'wealth_score'])
    else:
        try:
            dhs_hr = pd.read_stata(hr_path, convert_categoricals=False)
            wealth_df = dhs_hr[['HHID', 'HV001', 'HV002', 'HV271']].copy()
            wealth_df.rename(columns={'HV271': 'wealth_score'}, inplace=True)
        except Exception as e:
            print(f"Error loading {hr_path}: {e}")
            wealth_df = pd.DataFrame(columns=['HHID', 'HV001', 'HV002', 'wealth_score'])

    if not os.path.exists(geo_path):
        print(f"Warning: DHS GE file {geo_path} not found. Returning empty GeoDataFrame.")
        dhs_geo = gpd.GeoDataFrame(columns=['DHSCLUST', 'LATNUM', 'LONGNUM', 'URBAN_RURA', 'geometry'])
    else:
        try:
            dhs_geo = gpd.read_file(geo_path)
            if 'LATNUM' in dhs_geo.columns:
                dhs_geo = dhs_geo[dhs_geo['LATNUM'] != 0].copy()
        except Exception as e:
            print(f"Error loading {geo_path}: {e}")
            dhs_geo = gpd.GeoDataFrame(columns=['DHSCLUST', 'LATNUM', 'LONGNUM', 'URBAN_RURA', 'geometry'])

    return wealth_df, dhs_geo

if __name__ == "__main__":
    wealth_df, dhs_geo = load_dhs_data("data/raw/dhs/XXHR7DFL.DTA", "data/raw/dhs/XXGE7AFL.shp")
    print("Wealth data shape:", wealth_df.shape)
    print("Geo data shape:", dhs_geo.shape)
