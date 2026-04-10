import json
import rasterio
import pandas as pd
import numpy as np

# Load the dict
with open('data/species_coords.json') as f:
    coords_dict = json.load(f)

print(f"Loaded coordinates for {len(coords_dict)} species.")

# Open all 19 rasters
rasters = {}
for i in range(1, 20):
    try:
        # Use rasterio to open the datasets
        rasters[f"bio_{i}"] = rasterio.open(f"data/wc2.1_10m_bio/wc2.1_10m_bio_{i}.tif")
    except Exception as e:
        print(f"Failed to open bio_{i}: {e}")

climate_data = []

for species, coords in coords_dict.items():
    if not coords: continue

    # Extract values for each coordinate
    species_climate = {}
    for var, src in rasters.items():
        vals = []
        for lon, lat in coords:
            try:
                # Sample the raster at this point
                # rasterio sample expects an iterable of (lon, lat) tuples
                val = list(src.sample([(lon, lat)]))[0][0]
                if val != src.nodata:
                    vals.append(val)
            except:
                pass

        if vals:
            species_climate[f"{var}_mean"] = np.mean(vals)
        else:
            species_climate[f"{var}_mean"] = np.nan

    # Also calculate range extent (just max_dist roughly, or bounding box area)
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    if len(lons) > 1:
        range_size = (max(lons) - min(lons)) * (max(lats) - min(lats))
    else:
        range_size = 0

    species_climate["Species"] = species
    species_climate["range_size_deg2"] = range_size

    climate_data.append(species_climate)

df_climate = pd.DataFrame(climate_data)
df_climate.to_csv('data/species_climate.csv', index=False)
print("Saved species_climate.csv")

for src in rasters.values():
    src.close()
