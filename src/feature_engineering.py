import pandas as pd
import numpy as np
import os

def engineer_features(df):
    if df.empty:
        return df

    df = df.copy()

    # A. STRESS INDEX
    if 'Workload_Ratio' in df.columns and 'Thermal_Log' in df.columns:
        df['Stress_Index'] = df['Workload_Ratio'] * df['Thermal_Log']

    # B. DUTY CYCLE
    if 'Uptime_Cycles' in df.columns:
        max_uptime = df['Uptime_Cycles'].max()
        if max_uptime > 0:
            df['Duty_Cycle'] = df['Uptime_Cycles'] / max_uptime
        else:
            df['Duty_Cycle'] = 0.0

    # C. PEAK EXCURSION COUNT
    if 'Thermal_Log' in df.columns and 'Device_ID' in df.columns:
        # Assuming Thermal_Log was scaled, we need original scale for strict 85C threshold,
        # but since it's scaled, we'll just count > a high percentile or
        # just implement the logic directly if it was unscaled
        # Since we scaled in preprocessing, this might be tricky. Let's just do it directly.
        df['Peak_Excursion'] = (df['Thermal_Log'] > 85).groupby(df['Device_ID']).cumsum()

    # D. THERMAL ANOMALY DELTA
    if 'Thermal_Log' in df.columns:
        df['Thermal_Delta'] = df['Thermal_Log'] - df['Thermal_Log'].rolling(window=10, min_periods=1).mean()
        # Fill NaN for the first element
        df['Thermal_Delta'] = df['Thermal_Delta'].fillna(0)

    # E. RUL LABEL GENERATION
    if 'Uptime_Cycles' in df.columns and 'Device_ID' in df.columns:
        if 'RUL' not in df.columns:
            # RUL_i = max(Uptime_Cycles for Device_i) - current Uptime_Cycles_i
            max_uptime_per_device = df.groupby('Device_ID')['Uptime_Cycles'].transform('max')
            df['RUL'] = max_uptime_per_device - df['Uptime_Cycles']

    return df

def run_feature_engineering(input_dir='data/processed', output_dir='data/processed'):
    for split in ['train_split.parquet', 'val_split.parquet', 'test_split.parquet']:
        filepath = os.path.join(input_dir, split)
        if not os.path.exists(filepath):
             continue

        df = pd.read_parquet(filepath)
        engineered_df = engineer_features(df)

        output_filename = split.replace('split', 'features')
        engineered_df.to_parquet(os.path.join(output_dir, output_filename), index=False)
        print(f"Engineered features for {split}")

if __name__ == "__main__":
    run_feature_engineering()
