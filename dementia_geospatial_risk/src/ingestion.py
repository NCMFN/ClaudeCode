import os
import requests
import zipfile
import pandas as pd
from pathlib import Path
import time

DATA_DIR = Path("dementia_geospatial_risk/data")
RAW_DIR = DATA_DIR / "raw"

def download_file(url, save_path):
    if save_path.exists():
        print(f"File {save_path} already exists. Skipping download.")
        return True
    print(f"Downloading {url} to {save_path}...")
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 404:
            print(f"File not found: {url}")
            # Ensure we create an empty file or just return False based on memory rules
            # "report the specific HTTP error code instead of falling back to a simulated dataset"
            print(f"HTTP Error 404 for {url}")
            return False

        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded. Size: {os.path.getsize(save_path) / (1024*1024):.2f} MB")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def get_brfss_data():
    brfss_dir = RAW_DIR / "brfss"
    brfss_dir.mkdir(parents=True, exist_ok=True)

    # Download 2015-2022
    for year in range(2015, 2023):
        if year == 2022:
            url = "https://www.cdc.gov/brfss/annual_data/2022/files/LLCP2022XPT.zip"
        else:
            url = f"https://www.cdc.gov/brfss/annual_data/{year}/files/LLCP{year}XPT.zip"

        save_path = brfss_dir / f"LLCP{year}XPT.zip"
        download_file(url, save_path)

        if save_path.exists():
            try:
                with zipfile.ZipFile(save_path, 'r') as zip_ref:
                    zip_ref.extractall(brfss_dir)
            except Exception as e:
                print(f"Failed to extract {save_path}: {e}")

def get_epa_data():
    epa_dir = RAW_DIR / "epa"
    epa_dir.mkdir(parents=True, exist_ok=True)

    for year in range(2012, 2023):
        pm25_url = f"https://aqs.epa.gov/aqsweb/airdata/annual_conc_by_monitor_{year}.zip"
        download_file(pm25_url, epa_dir / f"pm25_{year}.zip")
        if (epa_dir / f"pm25_{year}.zip").exists():
            with zipfile.ZipFile(epa_dir / f"pm25_{year}.zip", 'r') as zip_ref:
                zip_ref.extractall(epa_dir)

def get_noaa_data():
    noaa_dir = RAW_DIR / "noaa"
    noaa_dir.mkdir(parents=True, exist_ok=True)
    # Actually just download the one provided in the instructions if it works, or fallback to empty.
    # Instruction says: https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc%3AC00072
    url = "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc%3AC00072"
    download_file(url, noaa_dir / "ncei_metadata.xml")

def get_census_data():
    census_dir = RAW_DIR / "census"
    census_dir.mkdir(parents=True, exist_ok=True)
    url_shp = "https://www2.census.gov/geo/tiger/TIGER2022/COUNTY/tl_2022_us_county.zip"
    download_file(url_shp, census_dir / "tl_2022_us_county.zip")
    if (census_dir / "tl_2022_us_county.zip").exists():
        with zipfile.ZipFile(census_dir / "tl_2022_us_county.zip", 'r') as zip_ref:
            zip_ref.extractall(census_dir)

if __name__ == "__main__":
    get_brfss_data()
    get_epa_data()
    get_noaa_data()
    get_census_data()
