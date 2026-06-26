import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
from sklearn.pipeline import Pipeline
from typing import Optional

def generate_poverty_heatmap(model: Pipeline, raster_path: str, output_tif: str, output_fig: str) -> None:
    """
    Applies the trained model to the NTL grid to generate a poverty heatmap.

    Args:
        model (Pipeline): Trained Random Forest model pipeline.
        raster_path (str): Path to the NTL annual median GeoTIFF.
        output_tif (str): Path to save the predicted heatmap GeoTIFF.
        output_fig (str): Path to save the heatmap visualization PNG.
    """
    if model is None:
        print("Model is None. Skipping heatmap generation.")
        return

    if not os.path.exists(raster_path):
        print(f"Raster {raster_path} not found. Skipping heatmap generation.")
        return

    try:
        with rasterio.open(raster_path) as src:
            ntl_grid = src.read(1)
            transform = src.transform
            crs = src.crs
            h, w = ntl_grid.shape

        ntl_flat = ntl_grid.flatten()
        valid_mask = ~np.isnan(ntl_flat)

        if not np.any(valid_mask):
            print("No valid pixels in NTL grid.")
            return

        pixel_features = pd.DataFrame({
            'ntl_mean':       ntl_flat,
            'ntl_max':        ntl_flat,
            'ntl_std':        np.zeros_like(ntl_flat),
            'ntl_median':     ntl_flat,
            'ntl_cv':         np.zeros_like(ntl_flat),
            'ntl_log_mean':   np.log1p(np.clip(ntl_flat, 0, None)),
            'ntl_brightness': np.ones_like(ntl_flat)
        })

        poverty_scores = np.full(ntl_flat.shape, np.nan)
        poverty_scores[valid_mask] = model.predict(pixel_features[valid_mask])
        poverty_grid = poverty_scores.reshape(h, w)

        os.makedirs(os.path.dirname(output_tif), exist_ok=True)
        with rasterio.open(output_tif, 'w',
                           driver='GTiff', height=h, width=w,
                           count=1, dtype='float32', crs=crs,
                           transform=transform) as dst:
            dst.write(poverty_grid.astype('float32'), 1)
        print(f"Poverty heatmap saved to {output_tif}")

        fig, ax = plt.subplots(figsize=(12, 9))
        img = ax.imshow(poverty_grid, cmap='RdYlGn', origin='upper',
                        vmin=np.nanpercentile(poverty_grid, 5),
                        vmax=np.nanpercentile(poverty_grid, 95))
        plt.colorbar(img, ax=ax, label='Predicted Wealth Index Score')
        ax.set_title("Regional Poverty Heatmap — NTL-Derived Wealth Estimation", fontsize=14)
        ax.axis('off')
        plt.tight_layout()
        os.makedirs('outputs/figures', exist_ok=True)
        plt.savefig('outputs/figures/poverty_heatmap.png', dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Poverty heatmap visualization saved to outputs/figures/poverty_heatmap.png")

    except Exception as e:
        print(f"Error generating poverty heatmap: {e}")
