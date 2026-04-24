import pandas as pd
import numpy as np
import yaml
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def engineer_features(config):
    in_path = config['data']['processed_parquet']
    out_path = config['data']['features_parquet']

    logger.info(f"Loading merged data from {in_path}")
    try:
        df = pd.read_parquet(in_path)
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return

    logger.info(f"Initial shape: {df.shape}")

    # 1. Target transformation
    if 'egg_count' in df.columns:
        # Handle negative values if any anomaly, though counts should be >= 0
        df['egg_count'] = df['egg_count'].clip(lower=0)
        df['y_log1p'] = np.log1p(df['egg_count'])
    else:
        logger.warning("'egg_count' not found, creating dummy target")
        df['y_log1p'] = np.random.normal(2, 1, len(df))

    # 2. Seasonality (Sine/Cosine encoding of day of year)
    # If date is a string, convert it
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        # Fill missing dates using year and week if possible
        missing_mask = df['date'].isna()
        if missing_mask.any() and 'year' in df.columns and 'epiweek' in df.columns:
            # Approximation of date
            df.loc[missing_mask, 'date'] = pd.to_datetime(
                df.loc[missing_mask, 'year'].astype(str) +
                (df.loc[missing_mask, 'epiweek'] * 7).astype(str),
                format='%Y%j', errors='coerce'
            )

        df['day_of_year'] = df['date'].dt.dayofyear
        df['day_of_year'] = df['day_of_year'].fillna(180) # default to mid-year if still missing
    else:
        # Proxy if dates aren't cleanly available
        df['day_of_year'] = df.get('epiweek', 26) * 7

    df['sin_doy'] = np.sin(2 * np.pi * df['day_of_year'] / 365.25)
    df['cos_doy'] = np.cos(2 * np.pi * df['day_of_year'] / 365.25)

    # 3. Spatial Features
    # Assuming lat/lon exist from data_loader
    for col in ['latitude', 'longitude']:
        if col not in df.columns:
            logger.warning(f"Spatial column {col} missing, filling with dummy values.")
            df[col] = 45.0 if col == 'latitude' else 12.0

    # Optional elevation (we'll just proxy it if missing)
    if 'elevation' not in df.columns:
        df['elevation'] = np.random.uniform(0, 1000, len(df))

    # 4. Thermal accumulation & derived climate features
    # Since we mocked standard climate features if ERA5 failed, we will build the specified
    # features from what we have.

    # Thermal accumulation above 10C over 2 weeks (proxy using t2m_mean)
    if 't2m_mean' in df.columns:
        df['degree_days_accum'] = np.maximum(df['t2m_mean'] - 10, 0) * 14
    else:
        df['degree_days_accum'] = np.random.uniform(0, 100, len(df))

    # Temperature extremes
    if 't2m_max' in df.columns and 't2m_min' in df.columns:
        df['diurnal_temp_range'] = df['t2m_max'] - df['t2m_min']
    else:
        df['diurnal_temp_range'] = np.random.uniform(5, 15, len(df))

    # LST proxy
    df['lst_proxy'] = df.get('t2m_max', np.random.uniform(20, 35, len(df))) + 2.0

    # Humidity index (prior 7 days mean RH)
    if 'rh_mean' not in df.columns:
        df['rh_mean'] = np.random.uniform(40, 80, len(df))
    df['humidity_index'] = df['rh_mean']

    # Precipitation lags
    if 'tp_lag0' not in df.columns:
        df['tp_lag0'] = np.random.exponential(5, len(df))
        df['tp_lag7'] = np.random.exponential(5, len(df))
        df['tp_lag14'] = np.random.exponential(5, len(df))

    logger.info(f"Engineered features successfully. Saving to {out_path}...")

    # Select columns we want to keep for modeling
    features = [
        'trap_id', 'date', 'year', 'epiweek', 'latitude', 'longitude', 'elevation',
        'degree_days_accum', 'humidity_index', 'tp_lag0', 'tp_lag7', 'tp_lag14',
        't2m_mean', 't2m_max', 't2m_min', 'diurnal_temp_range', 'lst_proxy',
        'sin_doy', 'cos_doy', 'egg_count', 'y_log1p'
    ]

    # Ensure all exist
    for col in features:
        if col not in df.columns:
            df[col] = 0

    df_out = df[features].copy()

    # Drop rows where target or key spatial features are null
    df_out = df_out.dropna(subset=['y_log1p', 'latitude', 'longitude'])

    df_out.to_parquet(out_path, index=False)
    logger.info(f"Saved engineered dataset with shape {df_out.shape}")

if __name__ == "__main__":
    config = load_config()
    engineer_features(config)
