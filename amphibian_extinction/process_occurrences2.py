import requests
import pandas as pd
import os
import json
from concurrent.futures import ThreadPoolExecutor
import time

df = pd.read_csv('data/iucn_status_final.csv')
df = df.dropna(subset=['IUCN_Status'])
species_list = df['Species'].unique()

def get_climate_for_species(species_name):
    try:
        url = f"https://api.gbif.org/v1/species/match?name={species_name}"
        res = requests.get(url, timeout=5).json()
        if 'usageKey' not in res:
            return None

        usage_key = res['usageKey']
        occ_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={usage_key}&hasCoordinate=true&limit=10"
        occ_res = requests.get(occ_url, timeout=5).json()

        coords = []
        for r in occ_res.get('results', []):
            if 'decimalLongitude' in r and 'decimalLatitude' in r:
                coords.append((r['decimalLongitude'], r['decimalLatitude']))

        if not coords:
            return None

        return {"Species": species_name, "coords": coords}
    except:
        return None

with open('data/species_coords.json') as f:
    results = json.load(f)

# we only have 173 coordinates, likely many gbif queries failed or timed out, or returned 0 occurrences for that name.
# let's try the rest of the 4800 species to see if we can get at least 1000 with coords.
# also some species are in AmphiBIO but might not have coords in GBIF easily.
subset = [s for s in species_list if s not in results]
print(f"Fetching coords for {len(subset)} species...")

with ThreadPoolExecutor(max_workers=30) as executor:
    for i, res in enumerate(executor.map(get_climate_for_species, subset)):
        if res:
            results[res["Species"]] = res["coords"]
        if (i+1) % 500 == 0:
            print(f"Processed {i+1}/{len(subset)}, Found: {len(results)}")

with open('data/species_coords.json', 'w') as f:
    json.dump(results, f)
print(f"Total coordinates fetched: {len(results)}")
