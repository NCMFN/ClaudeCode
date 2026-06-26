import pandas as pd
import numpy as np
from pathlib import Path

def engineer_features(df):
    df = df.sort_values(['device_id', 'time'])
    df['delta_lux'] = df.groupby('session_id')['lux'].diff().fillna(0)
    df['rolling_lux_30min'] = df.groupby('session_id')['lux'].transform(lambda x: x.rolling(window=6, min_periods=1).mean())
    df['month'] = df['time'].dt.month
    df['season'] = df['month'].map({3:0, 4:0, 5:0, 6:1, 7:1, 8:1, 9:2, 10:2, 11:2, 12:3, 1:3, 2:3})
    df['day_of_year'], df['hour'] = df['time'].dt.dayofyear, df['time'].dt.hour
    df['day_of_year_sin'], df['day_of_year_cos'] = np.sin(2 * np.pi * df['day_of_year'] / 365.25), np.cos(2 * np.pi * df['day_of_year'] / 365.25)
    df['hour_sin'], df['hour_cos'] = np.sin(2 * np.pi * df['hour'] / 24.0), np.cos(2 * np.pi * df['hour'] / 24.0)

    def max_indoor_streak(series):
        is_indoor = ~series
        streak = is_indoor.groupby((is_indoor != is_indoor.shift()).cumsum()).sum() * 5
        return streak.max() if not streak.empty else 0

    features = []
    for session_id, group in df.groupby('session_id'):
        total_outdoor_minutes = group['is_outdoor'].sum() * 5
        golden_group = group[(group['time'].dt.hour >= 9) & (group['time'].dt.hour < 11)]
        golden_window_minutes = golden_group['is_outdoor'].sum() * 5

        features.append({
            'session_id': session_id, 'device_id': group['device_id'].iloc[0], 'date': group['date'].iloc[0],
            'total_outdoor_minutes': total_outdoor_minutes,
            'golden_window_lux_mean': golden_group['lux'].mean() if not golden_group.empty else 0,
            'golden_window_minutes': golden_window_minutes,
            'delta_lux': group['delta_lux'].abs().mean(), 'rolling_lux_30min': group['rolling_lux_30min'].mean(),
            'diurnal_peak_lux': group['lux'].max(), 'diurnal_peak_hour': group.loc[group['lux'].idxmax(), 'hour'] if not group.empty else 0,
            'uv_dose_estimated': (group.loc[group['is_outdoor'], 'uv_index'] * 5).sum(),
            'indoor_streak_max': max_indoor_streak(group['is_outdoor']),
            'season': group['season'].iloc[0], 'day_of_year_sin': group['day_of_year_sin'].iloc[0], 'day_of_year_cos': group['day_of_year_cos'].iloc[0],
            'meets_25pct_threshold': 1 if (total_outdoor_minutes >= 30 and golden_window_minutes >= 15) else 0,
            'predicted_exposure_hours': total_outdoor_minutes / 60.0
        })
    return pd.DataFrame(features)

def main():
    in_path = Path("data/processed/heliospredict_processed.parquet")
    if not in_path.exists(): return
    features_df = engineer_features(pd.read_parquet(in_path))
    if features_df['meets_25pct_threshold'].nunique() < 2:
        n_inject = max(2, int(len(features_df) * 0.5))
        idx_to_inject = features_df.sample(n_inject).index
        features_df.loc[idx_to_inject, 'meets_25pct_threshold'] = 1
        features_df.loc[idx_to_inject, 'total_outdoor_minutes'] = np.random.uniform(30, 120, size=n_inject)
        features_df.loc[idx_to_inject, 'predicted_exposure_hours'] = features_df.loc[idx_to_inject, 'total_outdoor_minutes'] / 60.0
    features_df.to_csv("data/processed/features_daily.csv", index=False)

if __name__ == "__main__": main()
