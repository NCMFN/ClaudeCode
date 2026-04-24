import xarray as xr
import sys

url = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_rmin_1979_CurrentYear_CONUS.nc"
try:
    ds = xr.open_dataset(url)
    print("Dataset opened!")
    se_ds = ds.sel(lat=slice(37, 24), lon=slice(-95, -74), day=slice('2020-01-01', '2020-01-05'))
    print("Subset created:")
    print(se_ds)
    se_ds.load()
    print("Data loaded successfully.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
