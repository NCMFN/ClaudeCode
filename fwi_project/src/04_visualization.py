import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import joblib
import shap
import pickle

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')

def plot_fwi_heatmap():
    print("Generating FWI Geospatial Heatmap...")
    df = pd.read_csv(os.path.join(DATA_DIR, "processed_features.csv"))
    df['day'] = pd.to_datetime(df['day'])

    # Pick a high-risk day, e.g., one with the highest average FWI
    daily_fwi = df.groupby('day')['fwi'].mean()
    high_risk_day = daily_fwi.idxmax()
    print(f"Selected High-Risk Day: {high_risk_day.date()}")

    day_data = df[df['day'] == high_risk_day]

    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE, linewidth=1)
    ax.add_feature(cfeature.STATES, linewidth=0.5)
    ax.set_extent([-95, -74, 24, 37])

    scatter = ax.scatter(
        day_data['lon'], day_data['lat'],
        c=day_data['fwi'], cmap='YlOrRd',
        s=50, alpha=0.8, transform=ccrs.PlateCarree()
    )

    plt.colorbar(scatter, ax=ax, label='Predicted FWI', orientation='horizontal', pad=0.05)
    plt.title(f"Predicted FWI for SE US on {high_risk_day.date()}")

    out_path = os.path.join(OUTPUT_DIR, "fwi_heatmap.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved heatmap to {out_path}")

def plot_shap_summary():
    print("Generating SHAP summary plot...")
    shap_path = os.path.join(MODEL_DIR, "shap_values.pkl")
    if not os.path.exists(shap_path):
        print("SHAP values not found.")
        return

    with open(shap_path, "rb") as f:
        shap_values, X_sample = pickle.load(f)

    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_sample, show=False)
    out_path = os.path.join(OUTPUT_DIR, "shap_summary.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
    out_path = os.path.join(OUTPUT_DIR, "shap_feature_importance.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved SHAP plots.")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plot_fwi_heatmap()
    plot_shap_summary()

def plot_fwi_timeseries():
    print("Generating FWI Time Series for validation events...")
    preds_path = os.path.join(DATA_DIR, "validation_events.csv")
    if not os.path.exists(preds_path):
        print("Validation events predictions not found.")
        return

    preds = pd.read_csv(preds_path)
    preds['day'] = pd.to_datetime(preds['day'])
    preds['ig_date'] = pd.to_datetime(preds['ig_date'])

    events = preds['event_name'].unique()
    fig, axes = plt.subplots(len(events), 1, figsize=(10, 4*len(events)), sharex=False)
    if len(events) == 1:
        axes = [axes]

    for ax, event in zip(axes, events):
        event_data = preds[preds['event_name'] == event].sort_values('day')
        ig_date = event_data['ig_date'].iloc[0]

        ax.plot(event_data['day'], event_data['pred_fwi'], marker='o', label='Predicted FWI', color='red')
        ax.axvline(ig_date, color='black', linestyle='--', label='Ignition Date')
        ax.set_title(f"FWI Forecast for {event}")
        ax.set_ylabel("FWI")
        ax.legend()
        ax.grid(True)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fwi_time_series.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved FWI time series to {out_path}")

def export_predictions_csv():
    print("Exporting 2020-2023 predictions to CSV...")
    df = pd.read_csv(os.path.join(DATA_DIR, "processed_features.csv"))
    df['day'] = pd.to_datetime(df['day'])
    df_test = df[df['day'].dt.year >= 2020].copy()

    model = joblib.load(os.path.join(MODEL_DIR, "xgboost.pkl"))
    features = [
        'rmin', 'rmax', 'vs', 'th', 'pr', 'tmmn', 'tmmx', 'erc',
        'kbdi_proxy', 'rh_deficit', 'rmin_3d_avg', 'rmin_7d_avg',
        'pr_3d_avg', 'pr_7d_avg', 'vs_3d_avg', 'vs_7d_avg',
        'wind_shear', 'fire_weather_window', 'month', 'is_florida'
    ]

    # Check for NaN in features
    df_test = df_test.dropna(subset=features)
    df_test['pred_fwi'] = model.predict(df_test[features])

    out_cols = ['day', 'lat', 'lon', 'fwi', 'pred_fwi']
    out_csv = os.path.join(OUTPUT_DIR, "predicted_fwi_2020_2023.csv")
    df_test[out_cols].to_csv(out_csv, index=False)
    print(f"Saved predictions CSV to {out_csv}")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plot_fwi_heatmap()
    plot_shap_summary()
    plot_fwi_timeseries()
    export_predictions_csv()
