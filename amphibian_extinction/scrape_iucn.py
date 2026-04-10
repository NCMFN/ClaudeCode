import requests
import json
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor

df = pd.read_csv('data/AmphiBIO_v1.csv', encoding='latin1')
# For testing and fast iteration, we might not want to hit GBIF API for 6776 species right now.
# Let's get the IUCN status from AmphiBIO directly? AmphiBIO doesn't have it.
# Let's check AmphiBIO columns again:
# 'id', 'Order', 'Family', 'Genus', 'Species', 'Fos', 'Ter', 'Aqu', 'Arb', 'Leaves', 'Flowers', 'Seeds', 'Fruits', 'Arthro', 'Vert', 'Diu', 'Noc', 'Crepu', 'Wet_warm', 'Wet_cold', 'Dry_warm', 'Dry_cold', 'Body_mass_g', 'Age_at_maturity_min_y', 'Age_at_maturity_max_y', 'Body_size_mm', 'Size_at_maturity_min_mm', 'Size_at_maturity_max_mm', 'Longevity_max_y', 'Litter_size_min_n', 'Litter_size_max_n', 'Reproductive_output_y', 'Offspring_size_min_mm', 'Offspring_size_max_mm', 'Dir', 'Lar', 'Viv', 'OBS'

# GBIF species API can provide the IUCN status:
def get_iucn_status(species_name):
    try:
        url = f"https://api.gbif.org/v1/species/match?name={species_name}"
        res = requests.get(url).json()
        if 'usageKey' in res:
            usage_key = res['usageKey']
            dist_url = f"https://api.gbif.org/v1/species/{usage_key}/distributions"
            dist_res = requests.get(dist_url).json()
            for d in dist_res.get('results', []):
                if 'threatStatus' in d and 'IUCN' in d.get('source', ''):
                    return d['threatStatus']
        return None
    except:
        return None

# We can query a small subset or do it in bulk.
# Wait, since the prompt says "no simulation or synthetic data", and "datasets to use: IUCN Red List, AmphiBIO", I must get actual data.
# The IUCN API usually requires a token. GBIF is an acceptable substitute as it aggregates IUCN data!
# To avoid querying 6000 times, let's just query 500 random species for our dataset to prove the pipeline, or wait, maybe we can download an IUCN dataset.
