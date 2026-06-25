import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from pathlib import Path

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
                     'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

DATA_DIR = Path("dementia_geospatial_risk/data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = Path("dementia_geospatial_risk/outputs")
FIG_DIR = OUTPUTS_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

def generate_eda():
    print("Loading data...")
    df = pd.read_csv(PROCESSED_DIR / "model_ready_data.csv", dtype={'FIPS': str})

    # Needs risk classes 0, 1, 2
    if 'target_risk_class' not in df.columns:
        print("Missing target_risk_class.")
        return

    df['risk_class'] = df['target_risk_class']

    # Figure 1: Choropleth map of raw SCD prevalence
    print("Generating Figure 1 (Choropleth)...")
    try:
        counties = gpd.read_file(RAW_DIR / "census" / "tl_2022_us_county.shp")
        counties = counties.merge(df[['FIPS', 'scd_prevalence']], left_on="GEOID", right_on="FIPS", how="inner")
        conus = counties[~counties['STATEFP'].isin(['02', '15', '60', '66', '69', '72', '78'])]

        fig, ax = plt.subplots(1, 1, figsize=(15, 10))
        conus.plot(column="scd_prevalence", cmap="viridis", legend=True, ax=ax)
        ax.set_title("Raw SCD Prevalence by US County")
        ax.axis('off')
        plt.savefig(FIG_DIR / "Figure_1.png", bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Skipping Figure 1 due to: {e}")

    # Figure 2: Correlation heatmap
    print("Generating Figure 2 (Correlation Heatmap)...")
    try:
        cols = ['scd_prevalence', 'pollution_cumulative_load', 'latitude_gradient',
                'ozone_annual_mean', 'median_age', 'pct_over65', 'population_density', 'solar_exposure_index']
        # Filter to columns that actually exist
        cols = [c for c in cols if c in df.columns and not df[c].isna().all()]
        if len(cols) > 1:
            corr = df[cols].corr()
            plt.figure(figsize=(10, 8))
            sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
            plt.title("Correlation Heatmap of Features vs Target")
            plt.savefig(FIG_DIR / "Figure_2.png", bbox_inches='tight')
            plt.close()
    except Exception as e:
        print(f"Skipping Figure 2 due to: {e}")

    # Figure 3: Distribution plots
    print("Generating Figure 3 (Distribution plots)...")
    try:
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))

        if 'pm25_mean' in df.columns:
            sns.boxplot(x='risk_class', y='pm25_mean', hue='risk_class', data=df, ax=axes[0], palette="Set2", legend=False)
            axes[0].set_title("PM2.5 Distribution by Risk Class")

        if 'latitude' in df.columns:
            # We don't have NCEI solar index mock anymore, so we plot latitude or ozone
            plot_col = 'ozone_annual_mean' if 'ozone_annual_mean' in df.columns else 'latitude'
            sns.violinplot(x='risk_class', y=plot_col, hue='risk_class', data=df, ax=axes[1], palette="Set3", legend=False)
            axes[1].set_title(f"{plot_col} by Risk Class")

        plt.tight_layout()
        plt.savefig(FIG_DIR / "Figure_3.png", bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Skipping Figure 3 due to: {e}")

    # Figure 4: Scatter plot
    print("Generating Figure 4 (Scatter Plot)...")
    try:
        if 'pm25_mean' in df.columns and 'latitude' in df.columns:
            df['pm25_quartile'] = pd.qcut(df['pm25_mean'], 4, labels=['Q1', 'Q2', 'Q3', 'Q4'], duplicates='drop')
            plt.figure(figsize=(10, 6))
            sns.scatterplot(x='latitude', y='scd_prevalence', hue='pm25_quartile', data=df, palette='viridis', alpha=0.7)
            plt.title("Latitude vs SCD Rate colored by PM2.5 Quartile")
            plt.savefig(FIG_DIR / "Figure_4.png", bbox_inches='tight')
            plt.close()
    except Exception as e:
        print(f"Skipping Figure 4 due to: {e}")

    # Figure 5: Class imbalance bar chart
    print("Generating Figure 5 (Class Imbalance)...")
    try:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        counts_pre = df['risk_class'].value_counts().sort_index()
        axes[0].bar(counts_pre.index.astype(str), counts_pre.values, color='skyblue')
        axes[0].set_title("Pre-SMOTE Class Distribution")
        axes[0].set_xlabel("Risk Class")
        axes[0].set_ylabel("Count")

        smote_val = counts_pre.max()
        axes[1].bar(['0', '1', '2'], [smote_val, smote_val, smote_val], color='lightgreen')
        axes[1].set_title("Post-SMOTE Class Distribution (Target)")
        axes[1].set_xlabel("Risk Class")

        plt.tight_layout()
        plt.savefig(FIG_DIR / "Figure_5.png", bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Skipping Figure 5 due to: {e}")

if __name__ == "__main__":
    generate_eda()
