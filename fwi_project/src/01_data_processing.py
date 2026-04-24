import xarray as xr
import pandas as pd
import numpy as np
import os
import requests
import zipfile
import geopandas as gpd

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

GRIDMET_VARS = {
    'rmin': 'daily_minimum_relative_humidity',
    'rmax': 'daily_maximum_relative_humidity',
    'vs': 'daily_mean_wind_speed',
    'th': 'daily_mean_wind_direction',
    'pr': 'precipitation_amount',
    'tmmn': 'daily_minimum_temperature',
    'tmmx': 'daily_maximum_temperature',
    'erc': 'daily_mean_energy_release_component-g',
    'bi': 'daily_mean_burning_index_g'
}

def extract_gridmet_data(start_year, end_year):
    print(f"Starting gridMET data extraction for {start_year}-{end_year}...")
    base_url = "http://thredds.northwestknowledge.net:8080/thredds/dodsC"
    lat_slice = slice(37, 24)
    lon_slice = slice(-95, -74)
    time_slice = slice(f'{start_year}-01-01', f'{end_year}-12-31')

    datasets = []
    for var, var_name in GRIDMET_VARS.items():
        url = f"{base_url}/agg_met_{var}_1979_CurrentYear_CONUS.nc"
        print(f"Loading {var} from {url}")
        try:
            ds = xr.open_dataset(url)
            ds_subset = ds[var_name].sel(lat=lat_slice, lon=lon_slice, day=time_slice)
            ds_subset = ds_subset.isel(lat=slice(None, None, 5), lon=slice(None, None, 5))
            ds_subset.load()
            ds_subset = ds_subset.rename(var)
            datasets.append(ds_subset)
        except Exception as e:
            print(f"Error loading {var}: {e}")

    if datasets:
        merged_ds = xr.merge(datasets)
        return merged_ds
    return None

def fetch_mtbs_data():
    print("Fetching MTBS perimeter data...")
    mtbs_url = "https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/MTBS_Fire/data/composite_data/burned_area_extent_shapefile/mtbs_perimeter_data.zip"
    mtbs_dir = os.path.join(DATA_DIR, 'mtbs')
    os.makedirs(mtbs_dir, exist_ok=True)
    zip_path = os.path.join(mtbs_dir, 'mtbs_perimeter_data.zip')

    if not os.path.exists(zip_path):
        try:
            response = requests.get(mtbs_url, stream=True)
            response.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(mtbs_dir)
        except Exception as e:
            print(f"Error fetching MTBS: {e}")

    shp_path = os.path.join(mtbs_dir, 'mtbs_perims_DD.shp')
    if os.path.exists(shp_path):
        try:
            gdf = gpd.read_file(shp_path)
            gdf['ig_date'] = pd.to_datetime(gdf['ig_date'])
            gdf_se = gdf[(gdf['ig_date'].dt.year >= 2000) & (gdf['ig_date'].dt.year <= 2023)]

            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                centroids = gdf_se.geometry.centroid
                mask = (centroids.y >= 24) & (centroids.y <= 37) & (centroids.x >= -95) & (centroids.x <= -74)
                gdf_se = gdf_se[mask]

            out_path = os.path.join(DATA_DIR, "mtbs_se_us.gpkg")
            gdf_se.to_file(out_path, driver="GPKG")
            return gdf_se
        except Exception as e:
            print(f"Error processing MTBS: {e}")
    return None

def engineer_features():
    print("Engineering features...")
    nc_path = os.path.join(DATA_DIR, "gridmet_se_us.nc")
    ds = xr.open_dataset(nc_path)

    ds['fwi'] = ds['bi'] / 2.5
    ds['kbdi_proxy'] = ds['tmmx'].rolling(day=30, min_periods=1).sum() - (ds['pr'].rolling(day=30, min_periods=1).sum() * 10)
    ds['kbdi_proxy'] = xr.where(ds['kbdi_proxy'] > 0, ds['kbdi_proxy'], 0)
    ds['rh_deficit'] = ds['rmax'] - ds['rmin']

    for var in ['rmin', 'pr', 'vs']:
        ds[f'{var}_3d_avg'] = ds[var].rolling(day=3, min_periods=1).mean()
        ds[f'{var}_7d_avg'] = ds[var].rolling(day=7, min_periods=1).mean()

    ds['wind_shear'] = ds['vs'] * 1.5
    ds['fire_weather_window'] = (ds['rmin'] < 25) & (ds['wind_shear'] > 5) & (ds['kbdi_proxy'] > 500)
    ds['fire_weather_window'] = ds['fire_weather_window'].astype(int)

    # Subsample to fit in memory
    ds = ds.isel(day=slice(None, None, 10), lat=slice(None, None, 3), lon=slice(None, None, 3))

    df = ds.to_dataframe().reset_index()
    df = df.dropna(subset=['fwi', 'rmin'])

    df['month'] = df['day'].dt.month
    df['is_florida'] = ((df['lat'] < 31) & (df['lon'] > -88)).astype(int)

    out_csv = os.path.join(DATA_DIR, "processed_features.csv")
    df.to_csv(out_csv, index=False)
    print(f"Saved {len(df)} rows to {out_csv}")
    return df

if __name__ == "__main__":
    if not os.path.exists(os.path.join(DATA_DIR, "gridmet_se_us.nc")):
        ds = extract_gridmet_data(2000, 2023)
        ds.to_netcdf(os.path.join(DATA_DIR, "gridmet_se_us.nc"))
    if not os.path.exists(os.path.join(DATA_DIR, "mtbs_se_us.gpkg")):
        fetch_mtbs_data()
    engineer_features()
