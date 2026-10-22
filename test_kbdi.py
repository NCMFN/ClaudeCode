import xarray as xr
url = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_erc_1979_CurrentYear_CONUS.nc"
try:
    ds = xr.open_dataset(url)
    print("ERC exists:", list(ds.data_vars))
except Exception as e:
    print(e)

url2 = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_bi_1979_CurrentYear_CONUS.nc"
try:
    ds2 = xr.open_dataset(url2)
    print("BI exists:", list(ds2.data_vars))
except Exception as e:
    print(e)

url3 = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_kbdi_1979_CurrentYear_CONUS.nc"
try:
    ds3 = xr.open_dataset(url3)
    print("KBDI exists:", list(ds3.data_vars))
except Exception as e:
    print(e)
