import urllib.request
import urllib.error

urls = [
    "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_rmin_1979_CurrentYear_CONUS.nc",
    "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_rmax_1979_CurrentYear_CONUS.nc",
    "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_vs_1979_CurrentYear_CONUS.nc",
    "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_th_1979_CurrentYear_CONUS.nc",
    "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_pr_1979_CurrentYear_CONUS.nc",
    "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_tmmn_1979_CurrentYear_CONUS.nc",
    "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_tmmx_1979_CurrentYear_CONUS.nc",
    "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_erc_1979_CurrentYear_CONUS.nc",
    "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_bi_1979_CurrentYear_CONUS.nc",
    "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_fm100_1979_CurrentYear_CONUS.nc",
    "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_fm1000_1979_CurrentYear_CONUS.nc",
]

for url in urls:
    try:
        response = urllib.request.urlopen(url + ".html")
        print(f"URL OK: {url}")
    except urllib.error.URLError as e:
        print(f"URL ERROR {url}: {e}")
