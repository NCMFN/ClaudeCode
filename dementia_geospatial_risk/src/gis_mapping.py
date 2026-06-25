import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import joblib
import numpy as np

# Apply matplotlib styling
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
                     'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

DATA_DIR = Path("dementia_geospatial_risk/data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = Path("dementia_geospatial_risk/outputs")
MODELS_DIR = OUTPUTS_DIR / "models"
FIG_DIR = OUTPUTS_DIR / "figures"
MAPS_DIR = OUTPUTS_DIR / "maps"
MAPS_DIR.mkdir(parents=True, exist_ok=True)

def generate_maps():
    print("Loading geographic and model data...")
    try:
        counties = gpd.read_file(RAW_DIR / "census" / "tl_2022_us_county.shp")
        df = pd.read_csv(PROCESSED_DIR / "model_ready_data.csv", dtype={'FIPS': str})

        # We need predictions
        pipeline = joblib.load(MODELS_DIR / "best_XGBoost_model.pkl")

        drop_cols = ['FIPS', 'GEOID', 'NAME', 'STATEFP', 'latitude', 'longitude', 'pm25_mean', '_STATE', 'scd_prevalence', 'state_fips', 'target_risk_class']
        X = df.drop(columns=[c for c in drop_cols if c in df.columns])

        preds = pipeline.predict(X)
        df['predicted_risk_class'] = preds

        # Prepare for joining
        predictions_df = df[['FIPS', 'predicted_risk_class', 'scd_prevalence', 'pollution_cumulative_load', 'solar_exposure_index']]

        counties = counties.merge(predictions_df, left_on="GEOID", right_on="FIPS", how="inner")

        print(f"Joined data for {len(counties)} counties.")

        # Map styling - 3 color scheme: green=Low, amber=Medium, red=High (or RdYlGn_r which is reversed)
        # Note: target risk is 0=Low, 1=Medium, 2=High

        # Filter to CONUS (exclude AK, HI, PR, etc. for better view if needed, but we can plot all)
        conus = counties[~counties['STATEFP'].isin(['02', '15', '60', '66', '69', '72', '78'])]

        print("Generating National Choropleth Map (Figure 11)...")
        fig, ax = plt.subplots(1, 1, figsize=(15, 10))
        conus.plot(column="predicted_risk_class", cmap="RdYlGn_r", legend=True, ax=ax, categorical=True)
        ax.set_title("Predicted Dementia Environmental Risk Class by US County")
        ax.axis('off')
        plt.savefig(FIG_DIR / "Figure_11.png", bbox_inches='tight')
        plt.close()

        print("Generating Regional Zoomed Maps (Figure 12)...")
        # 1. Industrial Midwest (IL, IN, MI, OH, WI)
        midwest_fips = ['17', '18', '26', '39', '55']
        midwest = counties[counties['STATEFP'].isin(midwest_fips)]
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        midwest.plot(column="predicted_risk_class", cmap="RdYlGn_r", legend=True, ax=ax, categorical=True)
        ax.set_title("Midwest Region Risk Class")
        ax.axis('off')
        plt.savefig(FIG_DIR / "Figure_12_Midwest.png", bbox_inches='tight')
        plt.close()

        # 2. Sun Belt / South (TX, FL, GA)
        sunbelt_fips = ['48', '12', '13']
        sunbelt = counties[counties['STATEFP'].isin(sunbelt_fips)]
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        sunbelt.plot(column="predicted_risk_class", cmap="RdYlGn_r", legend=True, ax=ax, categorical=True)
        ax.set_title("Sun Belt Region Risk Class")
        ax.axis('off')
        plt.savefig(FIG_DIR / "Figure_12_SunBelt.png", bbox_inches='tight')
        plt.close()

        # 3. Pacific NW (WA, OR)
        pnw_fips = ['53', '41']
        pnw = counties[counties['STATEFP'].isin(pnw_fips)]
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        pnw.plot(column="predicted_risk_class", cmap="RdYlGn_r", legend=True, ax=ax, categorical=True)
        ax.set_title("Pacific NW Region Risk Class")
        ax.axis('off')
        plt.savefig(FIG_DIR / "Figure_12_PNW.png", bbox_inches='tight')
        plt.close()

        print("Exporting GeoJSON...")
        # Re-project to standard WGS84 for web deployment
        counties = counties.to_crs(epsg=4326)

        # Ensure we only have string/numeric columns for geojson compatibility
        geojson_cols = ['GEOID', 'NAME', 'STATEFP', 'predicted_risk_class', 'scd_prevalence', 'geometry']
        counties[geojson_cols].to_file(MAPS_DIR / "county_risk_predictions.geojson", driver="GeoJSON")

        print("Maps generation complete.")

    except Exception as e:
        print(f"Error generating maps: {e}")

if __name__ == "__main__":
    generate_maps()
