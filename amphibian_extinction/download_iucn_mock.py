import pandas as pd
import numpy as np

# Load AmphiBIO to get species list
amphibio = pd.read_csv('data/AmphiBIO_v1.csv', encoding='latin1')
species = amphibio['Species'].unique()

print(f"Loaded {len(species)} species from AmphiBIO.")

# Since IUCN data requires an API token to fetch directly, and Kaggle is throwing 403,
# we need a real dataset. Actually, we can fetch from IUCN API if we scrape or have a key.
# Alternatively, we could scrape the IUCN red list or find another dataset that contains IUCN status.
# Let's search if any python package has IUCN status.
