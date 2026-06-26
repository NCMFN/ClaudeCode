import os
import pandas as pd
import geopandas as gpd
import earthaccess
import warnings

warnings.filterwarnings("ignore")

def ingest_data():
    # NASA Earthdata Authentication
    try:
        earthaccess.login(strategy="netrc")
        results = earthaccess.search_data(
            short_name="VNP46A3",
            version="2",
            temporal=("2019-01", "2023-12"),
            bounding_box=(-180, -90, 180, 90)
        )
        if results:
            earthaccess.download(results, local_path="data/raw/ntl/")
    except Exception as e:
        print(f"Earthaccess login/download failed or unavailable: {e}")

    # Load DHS Survey Data
    dhs_hr_path = "data/raw/dhs/XXHR7DFL.DTA"
    if os.path.exists(dhs_hr_path):
        dhs_hr = pd.read_stata(dhs_hr_path, convert_categoricals=False)
        wealth_df = dhs_hr[['HHID', 'HV001', 'HV002', 'HV271']].copy()
    else:
        print("DHS HR data not found, returning empty DataFrame.")
        wealth_df = pd.DataFrame(columns=['HHID', 'HV001', 'HV002', 'HV271'])

    dhs_geo_path = "data/raw/dhs/XXGE7AFL.shp"
    if os.path.exists(dhs_geo_path):
        dhs_geo = gpd.read_file(dhs_geo_path)
        dhs_geo = dhs_geo[dhs_geo['LATNUM'] != 0]
    else:
        print("DHS GEO data not found, returning empty GeoDataFrame.")
        dhs_geo = gpd.GeoDataFrame(columns=['DHSCLUST', 'LATNUM', 'LONGNUM', 'URBAN_RURA', 'geometry'])

    # Save processed base data
    os.makedirs("data/processed", exist_ok=True)
    wealth_df.to_csv("data/processed/wealth_df.csv", index=False)
    if not dhs_geo.empty:
        dhs_geo.to_file("data/processed/dhs_geo.shp")
    else:
        # Save as empty csv to indicate it's empty since shp fails on empty sometimes
        dhs_geo.to_csv("data/processed/dhs_geo.csv", index=False)

if __name__ == "__main__":
    ingest_data()
