import os
import sys
import yaml
import json
import logging
from datetime import datetime
import pandas as pd
import numpy as np
import pyarrow.parquet as pq

from ingest import download_file, load_redteam_events, ingest_auth_data, AUTH_URL, REDTEAM_URL, get_file_sha256
from sampling import time_stratified_sample_stream
from features import update_global_states_and_compute, finalize_categorical_features, get_feature_columns, reset_feature_state
from protocols import p1_random_split, p2_user_split, p3_chronological_split, p4_rolling_origin
from models import get_models
from evaluate import run_evaluation_protocol, evaluate_paired_deltas
from figures import generate_figure_a, generate_figure_b
from figure_lint import lint_figures

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def update_status(status_text: str):
    with open("STATUS.md", "w") as f:
        f.write(f"# Status\n\n{status_text}\n")

def run_pipeline():
    os.makedirs('outputs/tables', exist_ok=True)
    os.makedirs('outputs/figures', exist_ok=True)
    os.makedirs('data/lanl', exist_ok=True)

    with open('config/protocol.yaml', 'r') as f:
        config = yaml.safe_load(f)

    redteam_path = 'data/lanl/redteam.txt.gz'
    auth_path = 'data/lanl/auth.txt.gz'

    logger.info("Downloading redteam events...")
    if not download_file(REDTEAM_URL, redteam_path):
        update_status("PROPOSED METHODOLOGY: no validation performed. Failed to download redteam data.")
        logger.error("Failed to download redteam. Exit.")
        sys.exit(1)

    logger.info("Downloading auth events...")
    auth_downloaded = download_file(AUTH_URL, auth_path)

    if not auth_downloaded or (os.path.exists(auth_path) and os.path.getsize(auth_path) < 100 * 1024 * 1024):
         logger.warning("Auth data incomplete or download failed. Falling back to PROPOSED METHODOLOGY.")
         update_status("PROPOSED METHODOLOGY: no validation performed. 12 GB file download timed out or blocked in sandbox. To resume, download locally and re-run `python src/run_pipeline.py`.")

         prov = {
             'status': 'PROPOSED',
             'config': config,
             'timestamp': datetime.now().isoformat(),
             'redteam_hash': get_file_sha256(redteam_path),
             'auth_hash': '',
         }
         with open('outputs/provenance.json', 'w') as f:
             json.dump(prov, f, indent=2)

         generate_figure_b('outputs/figures')
         lint_figures('outputs/figures')
         return

    logger.info("Full data available. Running pipeline...")

    redteam_set = load_redteam_events(redteam_path)
    total_rows, malicious_rows, unmatched_reasons = ingest_auth_data(auth_path, redteam_set, 'data/lanl/parquet')

    import glob
    parts = sorted(glob.glob('data/lanl/parquet/**/*.parquet', recursive=True))

    # Calculate global start day dynamically (or assume 0 from normalisation)
    # The exact cutoff is determined by start_time + p3_train_days
    # For now, we assume day 0 start, so cutoff time is just train_days * 86400
    # A true robust way is to scan the first chunk for the first time.
    # We will just use the config parameter strictly.
    train_cutoff_time = config['protocols']['p3_train_days'] * 86400

    def partition_iterator():
        reset_feature_state()
        for p in parts:
            pf = pq.ParquetFile(p)
            for batch in pf.iter_batches(batch_size=100_000):
                df_batch = batch.to_pandas()
                df_batch_featured = update_global_states_and_compute(df_batch, train_cutoff_time=train_cutoff_time)
                yield df_batch_featured

    df_sampled, true_prev, benign_counts = time_stratified_sample_stream(
        partition_iterator(),
        config['sampling']['benign_quota_per_day'],
        config['sampling']['redteam_cap_per_user_per_day']
    )

    df_features = finalize_categorical_features(df_sampled)

    N_d_safe = {int(k): int(v) for k, v in benign_counts.items()}

    prov = {
        'status': 'COMPLETED',
        'config': config,
        'timestamp': datetime.now().isoformat(),
        'redteam_hash': get_file_sha256(redteam_path),
        'auth_hash': get_file_sha256(auth_path),
        'total_rows_ingested': total_rows,
        'malicious_rows_ingested': malicious_rows,
        'sampled_rows': len(df_features),
        'true_prevalence': true_prev,
        'unmatched_reasons_count': len(unmatched_reasons),
        'daily_benign_counts': N_d_safe
    }
    with open('outputs/provenance.json', 'w') as f:
        json.dump(prov, f, indent=2)

    legacy_rows = []
    accumulated_benign = 0
    def legacy_partition_iterator():
        for p in parts:
            pf = pq.ParquetFile(p)
            for batch in pf.iter_batches(batch_size=100_000):
                yield batch.to_pandas()

    for df in legacy_partition_iterator():
        if accumulated_benign < 500000:
            benign_chunk = df[df['is_malicious'] == 0]
            needed = 500000 - accumulated_benign
            legacy_rows.append(benign_chunk.head(needed))
            accumulated_benign += len(benign_chunk.head(needed))

        malicious_chunk = df[df['is_malicious'] == 1]
        legacy_rows.append(malicious_chunk)

    legacy_sampling_replay = pd.concat(legacy_rows, ignore_index=True)
    legacy_sampling_replay['hour'] = (legacy_sampling_replay['time'] % 86400) // 3600
    legacy_sampling_replay['day_of_week'] = legacy_sampling_replay['day'] % 7
    legacy_sampling_replay['hour_sin'] = np.sin(2 * np.pi * legacy_sampling_replay['hour'] / 24)
    legacy_sampling_replay['hour_cos'] = np.cos(2 * np.pi * legacy_sampling_replay['hour'] / 24)

    time_features = ['hour_sin', 'hour_cos', 'day_of_week']
    m_obj = get_models(seed=config['seed'])['LogisticRegression']

    legacy_pr_auc = np.nan
    try:
        from sklearn.model_selection import train_test_split
        df_train_leg, df_test_leg = train_test_split(legacy_sampling_replay, test_size=0.2, stratify=legacy_sampling_replay['is_malicious'], random_state=42)
        X_train_time, y_train_leg = df_train_leg[time_features], df_train_leg['is_malicious']
        X_test_time, y_test_leg = df_test_leg[time_features], df_test_leg['is_malicious']

        m_obj.fit(X_train_time, y_train_leg)
        y_score_leg = m_obj.predict_proba(X_test_time)[:, 1]
        from sklearn.metrics import average_precision_score
        legacy_pr_auc = float(average_precision_score(y_test_leg, y_score_leg))
        logger.info(f"Legacy sampling time-only PR-AUC: {legacy_pr_auc:.4f} (Expect near 1.0 due to leakage)")
    except Exception as e:
        logger.error(f"Failed to compute legacy time-only baseline: {e}")

    feature_cols = get_feature_columns()
    models = get_models(seed=config['seed'])

    results = []
    trained_models = {m: {} for m in models}

    protocols = {
        'P1': lambda: p1_random_split(df_features, seed=config['seed']),
        'P2': lambda: p2_user_split(df_features, seed=config['seed']),
        'P3': lambda: p3_chronological_split(df_features,
                                     train_days=config['protocols']['p3_train_days'],
                                     val_days=config['protocols']['p3_val_days'],
                                     test_days=config['protocols']['p3_test_days'],
                                     purge_gap_days=config['protocols']['purge_gap_days']),
        'P4': lambda: p4_rolling_origin(df_features,
                                     n_splits=config['protocols']['p4_n_splits'],
                                     purge_gap_days=config['protocols']['purge_gap_days'])
    }

    for p_name, generator_func in protocols.items():
        for m_name, model in models.items():
             res, t_mdls = run_evaluation_protocol(df_features, feature_cols, m_name, model, generator_func(), p_name, true_prev, df_groups=df_features['day'])
             results.extend(res)
             trained_models[m_name][p_name] = t_mdls

    res_df = pd.DataFrame(results)
    res_df.to_csv('outputs/tables/evaluation_results.csv', index=False)

    p3_gen = p3_chronological_split(df_features,
                                     train_days=config['protocols']['p3_train_days'],
                                     val_days=config['protocols']['p3_val_days'],
                                     test_days=config['protocols']['p3_test_days'],
                                     purge_gap_days=config['protocols']['purge_gap_days'])

    evaluate_paired_deltas(df_features, feature_cols, df_features['day'], p3_gen, trained_models)

    generate_figure_b('outputs/figures')
    generate_figure_a(legacy_sampling_replay, df_features, 'outputs/figures', legacy_pr_auc)

    lint_figures('outputs/figures')

    # Strictly handle partial run logic: only upgrade STATUS if PARTIAL_RUN is not 1
    if os.environ.get('PARTIAL_RUN') != '1':
        update_status("COMPLETED: genuine measurements")
    else:
        logger.info("Pipeline completed in PARTIAL_RUN mode. Status remains PROPOSED METHODOLOGY.")

    logger.info("Pipeline run_pipeline.py execution finished.")

if __name__ == "__main__":
    run_pipeline()
