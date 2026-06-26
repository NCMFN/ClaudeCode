import pandas as pd
import geopandas as gpd

def load_dhs_data(hr_path="data/raw/dhs/XXHR7DFL.DTA", geo_path="data/raw/dhs/XXGE7AFL.shp"):
    # Load DHS Household Recode (wealth index is variable HVIDX or HV271)
    dhs_hr = pd.read_stata(hr_path, convert_categoricals=False)
    wealth_df = dhs_hr[['HHID', 'HV001', 'HV002', 'HV271']].copy()  # HV271 = wealth factor score

    # Load DHS GPS cluster coordinates (GE file)
    dhs_geo = gpd.read_file(geo_path)
    dhs_geo = dhs_geo[dhs_geo['LATNUM'] != 0]  # Drop suppressed coordinates

    return wealth_df, dhs_geo
