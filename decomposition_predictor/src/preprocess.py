import pandas as pd
import numpy as pd_np
import os
from sklearn.preprocessing import MinMaxScaler
import numpy as np

def compute_complexity_score(df):
    scaler = MinMaxScaler()
    features = ['v', 'v_g', 'ev_g', 'iv_g', 'n', 'l', 'd', 'e', 'b']

    # Fill NaN with median for these features before scaling
    df[features] = df[features].apply(pd.to_numeric, errors='coerce')
    for f in features:
        df[f] = df[f].fillna(df[f].median())

    normalized = scaler.fit_transform(df[features])
    weights = [0.25, 0.20, 0.15, 0.10, 0.10, 0.05, 0.05, 0.05, 0.05]
    df['complexity_score'] = (normalized * weights).sum(axis=1)
    return df

def generate_target_variables():
    in_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'combined_nasa_mdp.csv')
    df = pd.read_csv(in_path, low_memory=False)

    # Essential features to keep and analyze
    core_features = ['loc', 'v_g', 'ev_g', 'iv_g', 'n', 'v', 'l', 'd', 'i', 'e', 'b', 't',
                     'locode', 'locomment', 'loblank', 'uniq_op', 'uniq_opnd', 'total_op', 'total_opnd', 'source_project']

    # Ensure all core features exist. If they have different names in some datasets, map them.
    # From OpenML, some variables might be named differently depending on the dataset.
    # e.g., 'loc' vs 'loc_total'. Let's ensure the core features exist.

    # We will compute the complexity score
    df = compute_complexity_score(df)

    # Method B - Decomposition Depth Buckets
    bins = [-1, 0.25, 0.50, 0.75, 1.01]
    labels = [1, 2, 3, 4]
    df['decomposition_depth'] = pd.cut(df['complexity_score'], bins=bins, labels=labels)

    # Method C - LOC-Halstead Decomposition Index
    # Some datasets use 'loc_total' instead of 'loc'. Let's coalesce.
    if 'loc' not in df.columns:
        df['loc'] = df['loc_total'] if 'loc_total' in df.columns else df['locode']

    df['loc'] = pd.to_numeric(df['loc'], errors='coerce').fillna(df['loc'].median())

    df['decomp_index'] = (df['loc'] * df['v']) / (df['l'] * 1000 + 1)
    # Use qcut, handling potential duplicates by setting duplicates='drop' and adjusting
    try:
        df['decomp_depth_qcut'] = pd.qcut(df['decomp_index'], q=4, labels=[1, 2, 3, 4])
    except ValueError:
        df['decomp_depth_qcut'] = pd.qcut(df['decomp_index'].rank(method='first'), q=4, labels=[1, 2, 3, 4])

    # Let's retain all numerical columns that have valid data, and explicitly ensure we have the requested 21 features.

    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'engineered_nasa_mdp.csv')
    df.to_csv(out_path, index=False)
    print(f"Saved processed data to {out_path} with shape {df.shape}")

    # Let's save the scaler for API use later
    import joblib
    scaler = MinMaxScaler()
    df_temp = df[['v', 'v_g', 'ev_g', 'iv_g', 'n', 'l', 'd', 'e', 'b']].copy()
    scaler.fit(df_temp)
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'models'), exist_ok=True)
    joblib.dump(scaler, os.path.join(os.path.dirname(__file__), '..', 'models', 'scaler.joblib'))

if __name__ == '__main__':
    generate_target_variables()
