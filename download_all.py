import requests
import pandas as pd
import os

os.makedirs('data', exist_ok=True)

# 1. NEON Ticks DP1.10092.001
print("Downloading NEON...")
url = "https://data.neonscience.org/api/v0/products/DP1.10092.001"
response = requests.get(url)
data = response.json()
if len(data['data']['siteCodes']) > 0:
    site_code = data['data']['siteCodes'][0]['siteCode']
    month = data['data']['siteCodes'][0]['availableMonths'][0]
    data_url = f"https://data.neonscience.org/api/v0/data/DP1.10092.001/{site_code}/{month}"
    data_resp = requests.get(data_url).json()
    files = data_resp.get('data', {}).get('files', [])
    for f in files:
        if f['name'].endswith('.csv'):
            csv_resp = requests.get(f['url'])
            with open("data/neon_ticks.csv", 'wb') as out:
                out.write(csv_resp.content)
            print(f"Downloaded neon_ticks.csv")
            break

# 2. NASA Power
print("Downloading NASA POWER...")
url = "https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=T2M&community=RE&longitude=-75.1652&latitude=39.9526&start=20230101&end=20230102&format=CSV"
response = requests.get(url)
if response.status_code == 200:
    with open('data/nasa_power.csv', 'wb') as f:
        f.write(response.content)
    print("Downloaded nasa_power.csv")

# 3. GBIF Species 2190124 (Scheloribates pallidulus)
print("Downloading GBIF...")
url = "https://api.gbif.org/v1/species/2190124"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame([data])
    df.to_csv('data/gbif_species_2190124.csv', index=False)
    print("Downloaded gbif_species_2190124.csv")

# The other URLs:
# https://ipt.gbif.us/resource?r=neon-tick-abundance-diversity-pathogen-data is 404 (we can fetch HTTP error instead of mock, based on protocol)
# NASA Earthdata LPDAAC (mod13a3v061, gedi02_bv002) and NSIDC (spl3smp) are landing pages, Earthdata requires login to download actual data files, so we cannot directly fetch them as .csv.
# We will just report their HTTP error codes or fetch their landing page metadata if possible.

print("Checking Earthdata/NSIDC/GBIF IPT links...")
links_to_check = {
    "neon_tick_abundance_diversity_pathogen": "https://ipt.gbif.us/resource?r=neon-tick-abundance-diversity-pathogen-data",
    "mod13a3v061": "https://lpdaac.usgs.gov/products/mod13a3v061/",
    "spl3smp": "https://nsidc.org/data/spl3smp",
    "gedi02_bv002": "https://lpdaac.usgs.gov/products/gedi02_bv002/"
}

for name, link in links_to_check.items():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(link, headers=headers, timeout=10)
        print(f"{name}: HTTP {response.status_code}")
        # According to the protocol: If a link is broken or restricted, report the specific HTTP error code instead of falling back to a simulated dataset.
        with open(f"data/{name}_status.txt", "w") as f:
            f.write(f"URL: {link}\nStatus Code: {response.status_code}\n")
    except Exception as e:
        print(f"{name}: Error {e}")
        with open(f"data/{name}_status.txt", "w") as f:
            f.write(f"URL: {link}\nError: {e}\n")

print("Done.")
