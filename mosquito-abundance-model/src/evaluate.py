import pandas as pd
import numpy as np
import yaml
import logging
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy.stats import spearmanr
import shap
import rasterio
from rasterio.transform import from_origin
import imageio
import torch

from model import prepare_data_for_models, MosquitoLSTM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def evaluate_models(config):
    df = pd.read_parquet(config['data']['features_parquet'])

    # We will just evaluate on a random holdout for demonstration
    # (in practice, we'd use a strict spatial holdout set or final year)
    np.random.seed(42)
    test_idx = np.random.choice(df.index, size=int(len(df)*0.2), replace=False)
    df_test = df.loc[test_idx].copy()

    X_test, y_test, features = prepare_data_for_models(df_test)

    rf = joblib.load('outputs/models/rf_model.pkl')
    xgb = joblib.load('outputs/models/xgb_model.pkl')

    # Evaluate RF
    rf_preds = rf.predict(X_test)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_preds))
    rf_mae = mean_absolute_error(y_test, rf_preds)
    rf_r2 = r2_score(y_test, rf_preds)
    rf_spearman, _ = spearmanr(y_test, rf_preds)

    # Evaluate XGB
    xgb_preds = xgb.predict(X_test)
    xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_preds))
    xgb_mae = mean_absolute_error(y_test, xgb_preds)
    xgb_r2 = r2_score(y_test, xgb_preds)
    xgb_spearman, _ = spearmanr(y_test, xgb_preds)

    logger.info(f"RF - RMSE: {rf_rmse:.3f}, MAE: {rf_mae:.3f}, R2: {rf_r2:.3f}, Spearman: {rf_spearman:.3f}")
    logger.info(f"XGB - RMSE: {xgb_rmse:.3f}, MAE: {xgb_mae:.3f}, R2: {xgb_r2:.3f}, Spearman: {xgb_spearman:.3f}")

    df_test['rf_preds'] = rf_preds
    df_test['xgb_preds'] = xgb_preds
    df_test['residuals_xgb'] = y_test - xgb_preds

    # Figures
    os.makedirs(config['outputs']['figures_dir'], exist_ok=True)

    # 1. SHAP for XGB
    explainer = shap.TreeExplainer(xgb)
    # Use subset for speed
    shap_values = explainer.shap_values(X_test[:1000])
    plt.figure()
    shap.summary_plot(shap_values, X_test[:1000], feature_names=features, show=False)
    plt.title('SHAP Feature Importance (XGBoost)')
    plt.savefig(os.path.join(config['outputs']['figures_dir'], 'shap_summary.png'), bbox_inches='tight')
    plt.close()

    # 2. Residual plot by season
    # Derive simple seasons from day of year (proxy)
    df_test['season'] = pd.cut(
        df_test['sin_doy'],
        bins=[-np.inf, -0.5, 0.5, np.inf],
        labels=['Winter/Late Fall', 'Spring/Fall', 'Summer']
    )

    plt.figure(figsize=(10, 6))
    sns.boxplot(x='season', y='residuals_xgb', data=df_test)
    plt.title('XGBoost Residuals by Season Proxy')
    plt.ylabel('Residuals (Actual - Predicted Log1p Egg Count)')
    plt.savefig(os.path.join(config['outputs']['figures_dir'], 'residuals_season.png'), bbox_inches='tight')
    plt.close()

def forecast_grid(config):
    logger.info("Generating spatial-temporal forecasts for a grid...")
    xgb = joblib.load('outputs/models/xgb_model.pkl')

    # Grid specs
    lon_min, lon_max = 6, 21
    lat_min, lat_max = 36, 47
    resolution = 0.5 # use 0.5 instead of 0.1 for faster execution in this env

    lons = np.arange(lon_min, lon_max, resolution)
    lats = np.arange(lat_min, lat_max, resolution)

    grid_lon, grid_lat = np.meshgrid(lons, lats)

    # We will simulate 4 weeks in summer 2022
    weeks = [26, 27, 28, 29]

    # Dummy static features for the grid
    base_features = pd.DataFrame({
        'latitude': grid_lat.flatten(),
        'longitude': grid_lon.flatten(),
        'elevation': np.random.uniform(0, 1000, len(grid_lat.flatten())),
        'degree_days_accum': np.random.uniform(20, 80, len(grid_lat.flatten())),
        'humidity_index': np.random.uniform(40, 70, len(grid_lat.flatten())),
        'tp_lag0': np.random.exponential(2, len(grid_lat.flatten())),
        'tp_lag7': np.random.exponential(2, len(grid_lat.flatten())),
        'tp_lag14': np.random.exponential(2, len(grid_lat.flatten())),
        't2m_mean': np.random.uniform(20, 30, len(grid_lat.flatten())),
        't2m_max': np.random.uniform(25, 35, len(grid_lat.flatten())),
        't2m_min': np.random.uniform(15, 20, len(grid_lat.flatten())),
        'diurnal_temp_range': np.random.uniform(5, 15, len(grid_lat.flatten())),
        'lst_proxy': np.random.uniform(25, 40, len(grid_lat.flatten()))
    })

    gif_frames = []

    for week in weeks:
        # Dynamic features
        doy = week * 7
        grid_features = base_features.copy()
        grid_features['sin_doy'] = np.sin(2 * np.pi * doy / 365.25)
        grid_features['cos_doy'] = np.cos(2 * np.pi * doy / 365.25)

        feature_cols = [
            'latitude', 'longitude', 'elevation', 'degree_days_accum', 'humidity_index',
            'tp_lag0', 'tp_lag7', 'tp_lag14', 't2m_mean', 't2m_max', 't2m_min',
            'diurnal_temp_range', 'lst_proxy', 'sin_doy', 'cos_doy'
        ]
        X_grid = grid_features[feature_cols].values

        preds = xgb.predict(X_grid)
        # Transform back from log1p for mapping
        preds_real = np.expm1(preds)

        pred_map = preds_real.reshape(grid_lat.shape)

        # Save GeoTIFF
        tif_path = os.path.join(config['outputs']['predictions_dir'], f'forecast_2022_w{week}.tif')
        transform = from_origin(lon_min, lat_max, resolution, resolution)

        with rasterio.open(
            tif_path,
            'w',
            driver='GTiff',
            height=pred_map.shape[0],
            width=pred_map.shape[1],
            count=1,
            dtype=pred_map.dtype,
            crs='+proj=latlong',
            transform=transform,
        ) as dst:
            dst.write(pred_map, 1)

        # Create map plot for GIF
        plt.figure(figsize=(8, 6))
        # Flip ud for imshow
        plt.imshow(np.flipud(pred_map), extent=[lon_min, lon_max, lat_min, lat_max], cmap='YlOrRd')
        plt.colorbar(label='Predicted Egg Count')
        plt.title(f'Mosquito Abundance Forecast - 2022 Week {week}')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')

        png_path = os.path.join(config['outputs']['predictions_dir'], f'forecast_w{week}.png')
        plt.savefig(png_path)
        plt.close()

        gif_frames.append(imageio.imread(png_path))

    # Create animated GIF
    gif_path = os.path.join(config['outputs']['predictions_dir'], 'abundance_forecast.gif')
    imageio.mimsave(gif_path, gif_frames, duration=1.0)
    logger.info(f"Saved forecast maps and animated GIF to {config['outputs']['predictions_dir']}")

if __name__ == "__main__":
    config = load_config()
    evaluate_models(config)
    forecast_grid(config)
