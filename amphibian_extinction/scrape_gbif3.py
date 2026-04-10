import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import os

df = pd.read_csv('data/AmphiBIO_v1.csv', encoding='latin1')
species_list = df['Species'].dropna().unique()

def get_iucn_status_fast(species_name):
    try:
        url = f"https://api.gbif.org/v1/species/match?name={species_name}"
        res = requests.get(url, timeout=5).json()
        if 'usageKey' in res:
            usage_key = res['usageKey']
            dist_url = f"https://api.gbif.org/v1/species/{usage_key}/distributions"
            dist_res = requests.get(dist_url, timeout=5).json()
            for d in dist_res.get('results', []):
                if 'threatStatus' in d:
                    return {"Species": species_name, "IUCN_Status": d['threatStatus']}
        return {"Species": species_name, "IUCN_Status": None}
    except Exception as e:
        return {"Species": species_name, "IUCN_Status": None}

subset = species_list[4000:]
results = []
with ThreadPoolExecutor(max_workers=30) as executor:
    for i, res in enumerate(executor.map(get_iucn_status_fast, subset)):
        results.append(res)
        if (i+1) % 500 == 0:
            print(f"Processed {i+1}/{len(subset)}")

status_df = pd.DataFrame(results)
status_df.to_csv('data/iucn_status_part3.csv', index=False)
