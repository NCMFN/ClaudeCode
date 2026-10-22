import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install("xarray")
install("netCDF4")
install("requests")
install("pandas")
