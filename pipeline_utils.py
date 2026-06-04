import pandas as pd
import numpy as np

def load_and_preprocess_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.sort_values(by=['machine_id', 'timestamp'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    machines = df['machine_id'].copy()

    def fill_group(g):
        return g.ffill().bfill()

    df = df.groupby('machine_id', group_keys=False).apply(fill_group)

    if 'machine_id' not in df.columns:
        df['machine_id'] = machines.values

    return df

def extract_rolling_features(df: pd.DataFrame, window_min: int = 10) -> pd.DataFrame:
    df = df.copy()
    window = f'{window_min}min'

    features_list = []

    for m_id, group in df.groupby('machine_id'):
        group = group.copy()
        if 'timestamp' in group.columns:
            group.set_index('timestamp', inplace=True)

        res = pd.DataFrame(index=group.index)

        # We explicitly set machine_id in the result
        res['machine_id'] = m_id

        res['maintenance_required'] = group['maintenance_required']
        res['anomaly_flag'] = group['anomaly_flag']

        for col in ['vibration', 'pressure', 'energy_consumption', 'humidity', 'temperature']:
            res[col] = group[col]

        roll_vib = group['vibration'].rolling(window)
        res['vib_mean'] = roll_vib.mean()
        res['vib_std'] = roll_vib.std()
        res['vib_max'] = roll_vib.max()
        res['vib_kurtosis'] = roll_vib.kurt()
        res['vib_ptp'] = roll_vib.max() - roll_vib.min()

        roll_press = group['pressure'].rolling(window)
        res['press_var'] = roll_press.var()
        res['press_roc'] = group['pressure'].diff()
        press_mean = roll_press.mean()
        press_std = roll_press.std()
        res['press_zscore'] = (group['pressure'] - press_mean) / press_std

        roll_eng = group['energy_consumption'].rolling(window)
        eng_mean = roll_eng.mean()
        eng_std = roll_eng.std()

        is_spike = group['energy_consumption'] > (eng_mean + 2 * eng_std)
        res['eng_spike_count'] = is_spike.astype(int).rolling(window).sum()

        res['eng_avg_delta'] = group['energy_consumption'] - eng_mean

        res['vib_eng_corr'] = group['vibration'].rolling(window).corr(is_spike.astype(float))

        res['hour'] = group.index.hour
        res['dayofweek'] = group.index.dayofweek

        anomaly_times = group[group['anomaly_flag'] == 1].index
        if len(anomaly_times) > 0:
            temp = pd.DataFrame({'anomaly_time': anomaly_times}, index=anomaly_times)
            merged = pd.merge_asof(pd.DataFrame(index=group.index), temp, left_index=True, right_index=True, direction='backward')
            res['min_since_anomaly'] = (group.index - merged['anomaly_time']).dt.total_seconds() / 60.0
            res['min_since_anomaly'] = res['min_since_anomaly'].fillna(999999)
        else:
            res['min_since_anomaly'] = 999999

        features_list.append(res)

    df_features = pd.concat(features_list)

    machines2 = df_features['machine_id'].copy()

    def fill_na_features(group):
        return group.bfill().ffill()

    df_features = df_features.groupby('machine_id', group_keys=False).apply(fill_na_features)
    df_features.fillna(0, inplace=True)

    if 'machine_id' not in df_features.columns:
        df_features['machine_id'] = machines2.values

    df_features.reset_index(inplace=True)

    if 'index' in df_features.columns and 'timestamp' not in df_features.columns:
        df_features.rename(columns={'index': 'timestamp'}, inplace=True)

    return df_features
