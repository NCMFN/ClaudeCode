import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import os

df = pd.read_csv('data/AmphiBIO_v1.csv', encoding='latin1')
species_list = df['Species'].dropna().unique()

# GBIF species API doesn't always have IUCN in distributions. Another way is to query the IUCN red list API using a public dataset API if possible.
# Actually, the GBIF species backbone has `threatStatus` in the species profile?
def get_iucn_status_fast(species_name):
    try:
        url = f"https://api.gbif.org/v1/species/match?name={species_name}"
        res = requests.get(url, timeout=5).json()
        if 'usageKey' in res:
            usage_key = res['usageKey']
            # Sometimes threatStatus is directly in the species profile
            prof_url = f"https://api.gbif.org/v1/species/{usage_key}/speciesProfiles"
            prof_res = requests.get(prof_url, timeout=5).json()
            # or distributions
            dist_url = f"https://api.gbif.org/v1/species/{usage_key}/distributions"
            dist_res = requests.get(dist_url, timeout=5).json()

            for d in dist_res.get('results', []):
                if 'threatStatus' in d:
                    return {"Species": species_name, "IUCN_Status": d['threatStatus']}
        return {"Species": species_name, "IUCN_Status": None}
    except Exception as e:
        return {"Species": species_name, "IUCN_Status": None}

print("Fetching more statuses from GBIF to ensure we have a good dataset...")
results = []
# We'll run the next 3000 species to see if we get enough non-NaN.
subset = species_list[1000:4000]
with ThreadPoolExecutor(max_workers=30) as executor:
    for i, res in enumerate(executor.map(get_iucn_status_fast, subset)):
        results.append(res)
        if (i+1) % 500 == 0:
            print(f"Processed {i+1}/{len(subset)}")

status_df = pd.DataFrame(results)
status_df.to_csv('data/iucn_status_part2.csv', index=False)
print("Saved iucn_status_part2.csv")
