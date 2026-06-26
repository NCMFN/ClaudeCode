import rasterio
from rasterio.transform import from_bounds
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sklearn.metrics import r2_score

def generate_heatmap(best_model, ntl_raster_path="data/processed/ntl_annual_median.tif", output_tif="outputs/poverty_heatmap.tif"):
    with rasterio.open(ntl_raster_path) as src:
        ntl_grid = src.read(1)
        transform = src.transform
        crs = src.crs
        h, w = ntl_grid.shape

    # Build pixel-level feature matrix (flatten 2D grid)
    ntl_flat = ntl_grid.flatten()
    valid_mask = ~np.isnan(ntl_flat)

    pixel_features = pd.DataFrame({
        'ntl_mean':       ntl_flat,
        'ntl_max':        ntl_flat,       # For single-date; replace with proper stats if stacked
        'ntl_std':        np.zeros_like(ntl_flat),
        'ntl_median':     ntl_flat,
        'ntl_cv':         np.zeros_like(ntl_flat),
        'ntl_log_mean':   np.log1p(ntl_flat),
        'ntl_brightness': np.ones_like(ntl_flat)
    })

    poverty_scores = np.full(ntl_flat.shape, np.nan)
    if np.any(valid_mask):
        poverty_scores[valid_mask] = best_model.predict(pixel_features[valid_mask])

    poverty_grid = poverty_scores.reshape(h, w)

    # Save heatmap GeoTIFF
    with rasterio.open(output_tif, 'w',
                       driver='GTiff', height=h, width=w,
                       count=1, dtype='float32', crs=crs,
                       transform=transform) as dst:
        dst.write(poverty_grid.astype('float32'), 1)

    print(f"Poverty heatmap saved to {output_tif}")

    return poverty_grid

def visualize_heatmap(poverty_grid, output_img="outputs/figures/poverty_heatmap.png"):
    fig, ax = plt.subplots(figsize=(12, 9))
    if not np.all(np.isnan(poverty_grid)):
        img = ax.imshow(poverty_grid, cmap='RdYlGn', origin='upper',
                        vmin=np.nanpercentile(poverty_grid, 5),
                        vmax=np.nanpercentile(poverty_grid, 95))
        plt.colorbar(img, ax=ax, label='Predicted Wealth Index Score')
    ax.set_title("Regional Poverty Heatmap — NTL-Derived Wealth Estimation", fontsize=14)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(output_img, dpi=200)

def export_results(best_model, df, X):
    # Save results table
    results_table = df[['DHSCLUST', 'LATNUM', 'LONGNUM', 'URBAN_RURA', 'wealth_score']].copy()
    results_table['predicted_wealth'] = best_model.predict(X)
    results_table['residual'] = results_table['wealth_score'] - results_table['predicted_wealth']
    results_table.to_csv("outputs/prediction_results.csv", index=False)

    # Scatter plot: predicted vs actual
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(results_table['wealth_score'], results_table['predicted_wealth'],
               alpha=0.4, s=15, color='navy')

    # Avoid polyfit on empty or all-nan
    valid = results_table.dropna(subset=['wealth_score', 'predicted_wealth'])
    if len(valid) > 1:
        m, b = np.polyfit(valid['wealth_score'], valid['predicted_wealth'], 1)
        ax.plot(sorted(valid['wealth_score']),
                sorted(m * valid['wealth_score'] + b), 'r--')
        score = r2_score(valid['wealth_score'], valid['predicted_wealth'])
        ax.set_title(f"Predicted vs Actual — R² = {score:.3f}")
    else:
        ax.set_title("Predicted vs Actual")

    ax.set_xlabel("Observed Wealth Index")
    ax.set_ylabel("Predicted Wealth Index")
    plt.tight_layout()
    plt.savefig("outputs/figures/predicted_vs_actual.png", dpi=150)

    print("All outputs saved. Research pipeline complete.")
