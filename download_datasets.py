import requests
import os
import pandas as pd
from urllib.parse import urlparse

def download_data():
    links = [
        "https://www.neonscience.org/data-collection/ticks",
        "https://ipt.gbif.us/resource?r=neon-tick-abundance-diversity-pathogen-data",
        "https://data.neonscience.org/data-products/DP1.10092.001",
        "https://power.larc.nasa.gov/",
        "https://lpdaac.usgs.gov/products/mod13a3v061/",
        "https://nsidc.org/data/spl3smp",
        "https://lpdaac.usgs.gov/products/gedi02_bv002/",
        "https://www.gbif.org/species/2190124"
    ]

    for i, link in enumerate(links):
        print(f"Testing link {link}...")
        try:
            # We are not directly downloading from these URLs since they are HTML pages (landing pages).
            # The prompt asks to "provide the above datasets so that i can download it in .csv formats".
            # Let's inspect the content of the URLs.
            response = requests.get(link, timeout=10)
            print(f"Status Code: {response.status_code}, Content-Type: {response.headers.get('Content-Type')}")
        except Exception as e:
            print(f"Error fetching {link}: {e}")

if __name__ == "__main__":
    download_data()
