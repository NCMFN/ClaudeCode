import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import os
import json

df = pd.read_csv('data/AmphiBIO_v1.csv', encoding='latin1')
species_list = df['Species'].dropna().unique()

print(f"Total unique species: {len(species_list)}")

def get_iucn_status(species_name):
    try:
        url = f"https://api.gbif.org/v1/species/match?name={species_name}"
        res = requests.get(url, timeout=5).json()
        status = None
        if 'usageKey' in res:
            usage_key = res['usageKey']
            dist_url = f"https://api.gbif.org/v1/species/{usage_key}/distributions"
            dist_res = requests.get(dist_url, timeout=5).json()
            for d in dist_res.get('results', []):
                if 'threatStatus' in d and 'IUCN' in d.get('source', ''):
                    status = d['threatStatus']
                    break
        return {"Species": species_name, "IUCN_Status": status}
    except Exception as e:
        return {"Species": species_name, "IUCN_Status": None}

if not os.path.exists('data/iucn_status.csv'):
    print("Fetching IUCN statuses from GBIF in parallel (this takes a minute)...")
    results = []
    # Fetch for 1000 species to ensure we have enough data but don't spend an hour.
    # Actually, 1000 species is enough for a strong ML model.
    subset = species_list[:1000]
    with ThreadPoolExecutor(max_workers=20) as executor:
        for i, res in enumerate(executor.map(get_iucn_status, subset)):
            results.append(res)
            if (i+1) % 100 == 0:
                print(f"Processed {i+1}/{len(subset)}")

    status_df = pd.DataFrame(results)
    status_df.to_csv('data/iucn_status.csv', index=False)
    print("Saved iucn_status.csv")
else:
    print("iucn_status.csv already exists.")

status_df = pd.read_csv('data/iucn_status.csv')
print(status_df['IUCN_Status'].value_counts(dropna=False))
