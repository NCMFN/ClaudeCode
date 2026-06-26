import os
import rasterio
from rasterio.transform import from_bounds
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import joblib

def generate_heatmap():
    os.makedirs("outputs/figures", exist_ok=True)
    os.makedirs("outputs/paper_assets", exist_ok=True)

    ntl_tif = "data/processed/ntl_annual_median.tif"
    model_path = "outputs/models/best_model.pkl"

    if not os.path.exists(ntl_tif) or not os.path.exists(model_path):
        print("Required inputs for mapping not found.")
        return

    best_model = joblib.load(model_path)

    with rasterio.open(ntl_tif) as src:
        ntl_grid = src.read(1)
        transform = src.transform
        crs = src.crs
        h, w = ntl_grid.shape

    ntl_flat = ntl_grid.flatten()
    valid_mask = ~np.isnan(ntl_flat)

    # Note: features match FEATURES list from model_pipeline.py
    pixel_features = pd.DataFrame({
        'ntl_mean':       ntl_flat,
        'ntl_max':        ntl_flat,
        'ntl_std':        np.zeros_like(ntl_flat),
        'ntl_median':     ntl_flat,
        'ntl_cv':         np.zeros_like(ntl_flat),
        'ntl_log_mean':   np.log1p(ntl_flat),
        'ntl_brightness': np.ones_like(ntl_flat)
    })

    poverty_scores = np.full(ntl_flat.shape, np.nan)

    if valid_mask.any():
        try:
            poverty_scores[valid_mask] = best_model.predict(pixel_features[valid_mask])
        except Exception as e:
            print(f"Prediction failed on grid: {e}")
            poverty_scores[valid_mask] = 0

    poverty_grid = poverty_scores.reshape(h, w)

    with rasterio.open("outputs/poverty_heatmap.tif", 'w',
                       driver='GTiff', height=h, width=w,
                       count=1, dtype='float32', crs=crs,
                       transform=transform) as dst:
        dst.write(poverty_grid.astype('float32'), 1)

    fig, ax = plt.subplots(figsize=(12, 9))

    if np.isnan(poverty_grid).all():
        poverty_grid = np.zeros_like(poverty_grid)

    vmin = np.nanpercentile(poverty_grid, 5) if not np.isnan(poverty_grid).all() else 0
    vmax = np.nanpercentile(poverty_grid, 95) if not np.isnan(poverty_grid).all() else 1

    img = ax.imshow(poverty_grid, cmap='RdYlGn', origin='upper',
                    vmin=vmin, vmax=vmax)
    plt.colorbar(img, ax=ax, label='Predicted Wealth Index Score')
    ax.set_title("Regional Poverty Heatmap — NTL‑Derived Wealth Estimation", fontsize=14)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig("outputs/figures/poverty_heatmap.png", dpi=200)

    # Generate Manifest
    manifest = pd.DataFrame([
        {"file": "outputs/poverty_heatmap.tif", "type": "dataset"},
        {"file": "outputs/tables/prediction_results.csv", "type": "table"},
        {"file": "outputs/figures/feature_importance.png", "type": "figure"},
        {"file": "outputs/figures/predicted_vs_actual.png", "type": "figure"},
        {"file": "outputs/figures/poverty_heatmap.png", "type": "figure"}
    ])
    manifest.to_csv("outputs/paper_assets/paper_assets_manifest.csv", index=False)

if __name__ == "__main__":
    generate_heatmap()
