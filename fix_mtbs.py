import os
import geopandas as pd
import pandas as pd2
import geopandas as gpd

DATA_DIR = os.path.join('fwi_project', 'data')
mtbs_dir = os.path.join(DATA_DIR, 'mtbs')
shp_path = os.path.join(mtbs_dir, 'mtbs_perims_DD.shp')

if os.path.exists(shp_path):
    try:
        print("Loading MTBS shapefile...")
        gdf = gpd.read_file(shp_path)
        # Filter for SE US and 2000-2023
        gdf['ig_date'] = pd2.to_datetime(gdf['ig_date'])
        gdf_se = gdf[
            (gdf['ig_date'].dt.year >= 2000) &
            (gdf['ig_date'].dt.year <= 2023)
        ]

        # The bounding box filter (using centroid for simplicity)
        # Handle UserWarning about geometry centroid using Geographic CRS
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            centroids = gdf_se.geometry.centroid
            mask = (centroids.y >= 24) & (centroids.y <= 37) & (centroids.x >= -95) & (centroids.x <= -74)
            gdf_se = gdf_se[mask]

        out_path = os.path.join(DATA_DIR, "mtbs_se_us.gpkg")
        gdf_se.to_file(out_path, driver="GPKG")
        print(f"Saved MTBS SE US data ({len(gdf_se)} fires) to {out_path}")
    except Exception as e:
        print(f"Error processing MTBS shapefile: {e}")
