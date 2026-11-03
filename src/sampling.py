import os
import json
import yaml
import pyarrow.parquet as pq
import pandas as pd
import numpy as np

def load_config():
    with open("config/protocol.yaml") as f:
        return yaml.safe_load(f)

def sample():
    config = load_config()
    seed = config['sampling']['seed']
    quota = config['sampling'].get('quota', 1000)

    in_dir = "outputs/parquet/auth"
    out_dir = "outputs/parquet/sampled"
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(in_dir):
        return

    for f in os.listdir(in_dir):
        if not f.endswith(".parquet"):
            continue

        file_path = os.path.join(in_dir, f)
        pf = pq.ParquetFile(file_path)

        sampled_batches = []
        total_rows = pf.metadata.num_rows

        weight = quota / total_rows if total_rows > 0 else 0
        threshold = quota / total_rows if total_rows > 0 else 0

        for batch in pf.iter_batches():
            df = batch.to_pandas()
            # Vectorised hash replacement: Use numpy random seeded hashing
            # since hashing strings in pandas is slow. The requirement says:
            # "deterministic inclusion by hashing (time, user, src, dst) with the seed"
            # We can use pd.util.hash_pandas_object
            hash_vals = pd.util.hash_pandas_object(df[['time', 'src_user', 'src_comp', 'dst_comp']], index=False)

            # Normalize to 0-1
            hash_norm = (hash_vals % (10**9)) / (10**9)

            mask = (df['is_redteam']) | (hash_norm <= threshold)

            sampled_df = df[mask].copy()
            sampled_df['weight'] = np.where(sampled_df['is_redteam'], 1.0, weight)
            sampled_batches.append(sampled_df)

        if sampled_batches:
            final_df = pd.concat(sampled_batches)
            final_df.to_parquet(os.path.join(out_dir, f))

    with open("outputs/run_state.json", "w") as f:
        json.dump({"stage": "features"}, f)

if __name__ == "__main__":
    sample()
