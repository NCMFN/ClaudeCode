import pandas as pd
import numpy as np
import os

def engineer_features(df: pd.DataFrame, output_path: str) -> pd.DataFrame:
    print("Starting feature engineering...")
    if 'INACTIVITY_STATUS' in df.columns:
        df['INACTIVITY_STATUS'] = df['INACTIVITY_STATUS'].map({'Active': 0, 'Inactive': 1})

    df['liquidity_removal_rate_72h'] = df['TOTAL_REMOVED_LIQUIDITY'] / (df['TOTAL_ADDED_LIQUIDITY'] + 1e-9)
    df['liquidity_to_pool_ratio'] = df['TOTAL_REMOVED_LIQUIDITY'] / (df['NUM_LIQUIDITY_REMOVES'] + 1)
    df['add_to_remove_ratio'] = df['ADD_TO_REMOVE_RATIO']
    df['net_liquidity'] = df['TOTAL_ADDED_LIQUIDITY'] - df['TOTAL_REMOVED_LIQUIDITY']
    df['remove_volume_per_event'] = df['TOTAL_REMOVED_LIQUIDITY'] / (df['NUM_LIQUIDITY_REMOVES'] + 1)
    df['add_volume_per_event'] = df['TOTAL_ADDED_LIQUIDITY'] / (df['NUM_LIQUIDITY_ADDS'] + 1)

    ts_cols = ['FIRST_POOL_ACTIVITY_TIMESTAMP', 'LAST_POOL_ACTIVITY_TIMESTAMP', 'LAST_SWAP_TIMESTAMP']
    for col in ts_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    df['pool_lifetime_hours'] = (df['LAST_POOL_ACTIVITY_TIMESTAMP'] - df['FIRST_POOL_ACTIVITY_TIMESTAMP']).dt.total_seconds() / 3600.0
    df['swap_to_close_gap_hours'] = (df['LAST_POOL_ACTIVITY_TIMESTAMP'] - df['LAST_SWAP_TIMESTAMP']).dt.total_seconds() / 3600.0
    df['pool_lifetime_hours'] = df['pool_lifetime_hours'].fillna(0)

    df['activity_velocity'] = (df['NUM_LIQUIDITY_ADDS'] + df['NUM_LIQUIDITY_REMOVES']) / (df['pool_lifetime_hours'] + 1)
    df['removal_event_frequency'] = df['NUM_LIQUIDITY_REMOVES'] / (df['pool_lifetime_hours'] + 1)
    df['is_short_lived'] = (df['pool_lifetime_hours'] < 1.0).astype(int)
    df['high_remove_ratio'] = (df['ADD_TO_REMOVE_RATIO'] > 1.0).astype(int)

    df['add_remove_imbalance'] = (df['NUM_LIQUIDITY_ADDS'] - df['NUM_LIQUIDITY_REMOVES']).abs()
    df['liquidity_concentration'] = df['TOTAL_REMOVED_LIQUIDITY'] / (df['TOTAL_ADDED_LIQUIDITY'] + df['TOTAL_REMOVED_LIQUIDITY'] + 1e-9)
    df['log_total_removed'] = np.log1p(df['TOTAL_REMOVED_LIQUIDITY'].fillna(0))
    df['log_total_added'] = np.log1p(df['TOTAL_ADDED_LIQUIDITY'].fillna(0))

    df['single_event_removal'] = (df['NUM_LIQUIDITY_REMOVES'] == 1).astype(int)
    df['zero_adds_after_remove'] = (df['NUM_LIQUIDITY_ADDS'] == 0).astype(int)

    cols_to_drop = ['LIQUIDITY_POOL_ADDRESS', 'MINT', 'LAST_SWAP_TX_ID',
                    'FIRST_POOL_ACTIVITY_TIMESTAMP', 'LAST_POOL_ACTIVITY_TIMESTAMP', 'LAST_SWAP_TIMESTAMP']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

    print(f"Features engineered. New shape: {df.shape}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Engineered features saved to {output_path}")

    return df
