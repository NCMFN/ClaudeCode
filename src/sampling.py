import pandas as pd
import numpy as np
import logging
import hashlib
import os
from typing import Tuple, Iterator

logger = logging.getLogger(__name__)

def deterministic_hash_prob(time: int, src_user: str, src_comp: str, dst_comp: str, seed: int = 42) -> float:
    key = f"{time}_{src_user}_{src_comp}_{dst_comp}_{seed}".encode('utf-8')
    h = int(hashlib.md5(key).hexdigest(), 16)
    return (h % 1000000) / 1000000.0

def time_stratified_sample_stream(
    partition_iterator: Iterator[pd.DataFrame],
    benign_quota_per_day: int,
    redteam_cap_per_user_per_day: int
) -> Tuple[pd.DataFrame, float, dict]:

    logger.info("Starting time-stratified streaming sampling...")

    total_events = 0
    total_malicious = 0

    mal_tracker = {}
    benign_counts = {}

    output_dir = 'data/lanl/sampled'
    os.makedirs(output_dir, exist_ok=True)

    for f in os.listdir(output_dir):
        if f.endswith('.parquet'):
            os.remove(os.path.join(output_dir, f))

    target_p = 0.005

    for df in partition_iterator:
        if df.empty: continue
        total_events += len(df)
        total_malicious += df['is_malicious'].sum()

        # Vectorized hash computation
        df['hash_val'] = [
            deterministic_hash_prob(t, u, c1, c2)
            for t, u, c1, c2 in zip(df['time'], df['src_user'], df['src_comp'], df['dst_comp'])
        ]

        # Fast groupby processing
        for day, day_df in df.groupby('day'):
            is_mal = day_df['is_malicious'] == 1
            benign_counts[day] = benign_counts.get(day, 0) + (~is_mal).sum()

            # 1. Fast malicious filtering using dict tracking (vectorized where possible)
            mal_df = day_df[is_mal].copy()
            if not mal_df.empty:
                keep_mal = []
                for u in mal_df['src_user']:
                    k = (day, u)
                    mal_tracker[k] = mal_tracker.get(k, 0) + 1
                    keep_mal.append(mal_tracker[k] <= redteam_cap_per_user_per_day)
                mal_df = mal_df[keep_mal]

            # 2. Fast benign filtering
            ben_df = day_df[(~is_mal) & (day_df['hash_val'] < target_p)].copy()

            # Combine and stream out
            out_df = pd.concat([mal_df, ben_df])
            if not out_df.empty:
                out_path = os.path.join(output_dir, f'day_{day:02d}.parquet')
                if os.path.exists(out_path):
                    # Append mode
                    existing = pd.read_parquet(out_path)
                    pd.concat([existing, out_df]).to_parquet(out_path, index=False)
                else:
                    out_df.to_parquet(out_path, index=False)

    true_prevalence = total_malicious / total_events if total_events > 0 else 0
    logger.info(f"Original prevalence: {true_prevalence:.8f}")

    # Pass 2: Truncate loosely sampled disk files
    final_dfs = []
    for day, true_count in benign_counts.items():
        path = os.path.join(output_dir, f'day_{day:02d}.parquet')
        if not os.path.exists(path):
            continue

        day_df = pd.read_parquet(path)
        is_mal = day_df['is_malicious'] == 1

        mal_df = day_df[is_mal].copy()
        mal_df['sampling_weight'] = 1.0

        ben_df = day_df[~is_mal].copy()

        if len(ben_df) > benign_quota_per_day:
            ben_df = ben_df.sort_values('hash_val').head(benign_quota_per_day).copy()

        if len(ben_df) > 0:
            p = len(ben_df) / true_count if true_count > 0 else 1.0
            ben_df['sampling_weight'] = 1.0 / p if p > 0 else 1.0

        final_dfs.append(mal_df.drop(columns=['hash_val']))
        final_dfs.append(ben_df.drop(columns=['hash_val']))

    if final_dfs:
        final_sampled_df = pd.concat(final_dfs).sort_values('time').reset_index(drop=True)
    else:
        final_sampled_df = pd.DataFrame()

    return final_sampled_df, true_prevalence, benign_counts
