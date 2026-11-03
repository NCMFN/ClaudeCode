import os
import json
import pandas as pd
import numpy as np

def extract_features():
    in_dir = "outputs/parquet/sampled"
    out_dir = "outputs/parquet/features"
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(in_dir):
        return

    user_counts = pd.Series(dtype=int)

    files = sorted([f for f in os.listdir(in_dir) if f.endswith(".parquet")])

    for f in files:
        df = pd.read_parquet(os.path.join(in_dir, f))

        df['hour'] = (df['time'] % 86400) // 3600
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24.0)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24.0)

        df = df.sort_values('time')

        # Vectorised causal cumcount
        df['user_login_count'] = df.groupby('src_user').cumcount() + 1

        # Add previous partitions state
        prev_counts = df['src_user'].map(user_counts).fillna(0)
        df['user_login_count'] += prev_counts

        # Update state for next partition
        partition_counts = df.groupby('src_user').size()
        user_counts = user_counts.add(partition_counts, fill_value=0)

        df.to_parquet(os.path.join(out_dir, f))

    with open("outputs/run_state.json", "w") as f:
        json.dump({"stage": "evaluate"}, f)

if __name__ == "__main__":
    extract_features()
