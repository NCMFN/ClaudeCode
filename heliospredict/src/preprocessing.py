import pandas as pd
import numpy as np
import os
from sklearn.ensemble import IsolationForest
from pathlib import Path

def process_sensor_data(raw_dir):
    dfs = []
    for i in range(1, 7):
        file_path = os.path.join(raw_dir, f"{i}.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df['device_id'] = i
            df.columns = [c.lower().strip() for c in df.columns]
            time_col = next((c for c in df.columns if 'time' in c or 'date' in c), None)
            if time_col: df['time'] = pd.to_datetime(df[time_col], unit='ms' if df[time_col].max() > 1e11 else None)
            else: df['time'] = pd.date_range('2023-01-01', periods=len(df), freq='S')
            lux_col = next((c for c in df.columns if 'lux' in c or 'light' in c or 'als' in c), None)
            df['lux'] = df[lux_col] if lux_col else 500
            dfs.append(df[['device_id', 'time', 'lux']])
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def apply_isolation_forest(df, features):
    X = df[features].fillna(0)
    return IsolationForest(contamination=0.05, random_state=42).fit_predict(X) == -1

def temporal_alignment(df, external_dir):
    df_resampled = []
    for device_id, group in df.groupby('device_id'):
        group = group.set_index('time').sort_index()
        group = group[~group.index.duplicated(keep='first')]
        resampled = group.resample('5min').ffill()
        resampled['device_id'] = device_id
        df_resampled.append(resampled.reset_index())

    if df_resampled: df = pd.concat(df_resampled, ignore_index=True)

    uv_file = os.path.join(external_dir, "London_uv_hourly.csv")
    if os.path.exists(uv_file):
        uv_df = pd.read_csv(uv_file)
        uv_df['time'] = pd.to_datetime(uv_df['time'])
        if uv_df['uv_index'].isna().all(): uv_df['uv_index'] = (uv_df['shortwave_radiation'] / 100).clip(0, 11)
        uv_df = uv_df.set_index('time').resample('5min').ffill().reset_index()
        df['hour_min'] = df['time'].dt.strftime('%H:%M')
        uv_df['hour_min'] = uv_df['time'].dt.strftime('%H:%M')
        uv_profile = uv_df.groupby('hour_min')['uv_index'].mean().reset_index()
        df = pd.merge(df, uv_profile, on='hour_min', how='left')
        df.drop(columns=['hour_min'], inplace=True)
        df['uv_index'] = df['uv_index'].fillna(0)
    else: df['uv_index'] = 0.0
    return df

def main():
    raw_dir, external_dir, processed_dir = Path("data/raw"), Path("data/external"), Path("data/processed")
    df = process_sensor_data(raw_dir)
    if df.empty: return
    df['is_outlier'] = apply_isolation_forest(df, ['lux'])
    df['is_outdoor'] = df['lux'] > 1000
    df = temporal_alignment(df, external_dir)
    df['date'] = df['time'].dt.date
    df['session_id'] = df['device_id'].astype(str) + "_" + df['date'].astype(str)
    def min_max_scale(g, cols):
        for col in cols:
            mi, ma = g[col].min(), g[col].max()
            g[f"{col}_scaled"] = (g[col] - mi) / (ma - mi) if ma > mi else 0.0
        return g
    df = df.groupby('session_id', group_keys=False).apply(lambda g: min_max_scale(g, ['lux', 'uv_index']))
    df['hour'], df['day_of_year'] = df['time'].dt.hour, df['time'].dt.dayofyear
    df['hour_z'] = (df['hour'] - df['hour'].mean()) / df['hour'].std()
    df['day_of_year_z'] = (df['day_of_year'] - df['day_of_year'].mean()) / df['day_of_year'].std()
    df.to_parquet(processed_dir / "heliospredict_processed.parquet", index=False)

if __name__ == "__main__": main()
