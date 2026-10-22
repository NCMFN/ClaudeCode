import xarray as xr
import pandas as pd
import os

DATA_DIR = os.path.join('fwi_project', 'data')
nc_path = os.path.join(DATA_DIR, "gridmet_se_us.nc")
ds = xr.open_dataset(nc_path)

print("Calculating FWI and proxy features...")
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

# Aggressive subsampling for the workspace constraints
print("Aggressively subsampling data to fit within 2GB RAM limits...")
ds = ds.isel(day=slice(None, None, 10), lat=slice(None, None, 3), lon=slice(None, None, 3))

print("Converting to dataframe...")
df = ds.to_dataframe().reset_index()
print(f"Total rows before dropna: {len(df)}")
df = df.dropna(subset=['fwi', 'rmin'])
print(f"Total rows after dropna: {len(df)}")

df['month'] = df['day'].dt.month
df['is_florida'] = ((df['lat'] < 31) & (df['lon'] > -88)).astype(int)

out_csv = os.path.join(DATA_DIR, "processed_features.csv")
print(f"Saving to {out_csv}...")
df.to_csv(out_csv, index=False)
print("Done.")
