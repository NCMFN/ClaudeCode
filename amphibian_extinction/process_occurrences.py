import requests
import pandas as pd
import os
import json
from concurrent.futures import ThreadPoolExecutor

df = pd.read_csv('data/iucn_status_final.csv')
df = df.dropna(subset=['IUCN_Status'])
species_list = df['Species'].unique()

print(f"Total species with IUCN status: {len(species_list)}")

def get_climate_for_species(species_name):
    # Get usageKey
    try:
        url = f"https://api.gbif.org/v1/species/match?name={species_name}"
        res = requests.get(url, timeout=5).json()
        if 'usageKey' not in res:
            return None

        usage_key = res['usageKey']
        occ_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={usage_key}&hasCoordinate=true&limit=20"
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

if not os.path.exists('data/species_coords.json'):
    print("Fetching species occurrence coordinates...")
    results = {}
    # Use 30 threads and a timeout so we don't wait forever
    # Also just sample the first 2000 species to save time
    subset = species_list[:2000]
    with ThreadPoolExecutor(max_workers=30) as executor:
        for i, res in enumerate(executor.map(get_climate_for_species, subset)):
            if res:
                results[res["Species"]] = res["coords"]
            if (i+1) % 200 == 0:
                print(f"Processed {i+1}/{len(subset)}")

    with open('data/species_coords.json', 'w') as f:
        json.dump(results, f)
    print("Saved species_coords.json")
else:
    print("Coordinates already fetched.")
