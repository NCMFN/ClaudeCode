import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline_utils import extract_rolling_features
from anomaly_scoring import detect_micro_anomalies, compute_risk_score
from classification_sim import simulate_cloud_edge, calculate_lead_time

def test_feature_shape(sample_df):
    df_feat = extract_rolling_features(sample_df, window_min=10)
    assert df_feat.shape[1] > 15
    assert 'vib_mean' in df_feat.columns
    assert 'press_var' in df_feat.columns

def test_no_data_leakage(sample_df):
    from sklearn.model_selection import GroupKFold

    df_feat = extract_rolling_features(sample_df, window_min=10)
    df_anom = detect_micro_anomalies(df_feat, ['vibration', 'pressure', 'energy_consumption'])
    df_risk = compute_risk_score(df_anom)

    features = ['vib_mean', 'press_var', 'eng_spike_count', 'risk_score']
    X = df_risk[features].values
    y = df_risk['maintenance_required'].values
    groups = df_risk['machine_id'].values

    gkf = GroupKFold(n_splits=3)
    train_idx, val_idx = next(gkf.split(X, y, groups))

    train_machines = set(df_risk.iloc[train_idx]['machine_id'])
    val_machines = set(df_risk.iloc[val_idx]['machine_id'])

    assert len(train_machines & val_machines) == 0

def test_risk_score_range(sample_df):
    df_feat = extract_rolling_features(sample_df, window_min=10)
    df_anom = detect_micro_anomalies(df_feat, ['vibration', 'pressure', 'energy_consumption'])
    df_risk = compute_risk_score(df_anom)
    assert df_risk['risk_score'].between(0, 100).all()

def test_high_risk_threshold(sample_df):
    df_feat = extract_rolling_features(sample_df, window_min=10)
    df_anom = detect_micro_anomalies(df_feat, ['vibration', 'pressure', 'energy_consumption'])
    df_risk = compute_risk_score(df_anom)

    high_risk = df_risk[df_risk['risk_score'] > 75]
    assert 'high_risk_flag' in df_risk.columns
    if len(high_risk) > 0:
        assert (high_risk['high_risk_flag'] == 1).all()

def test_bandwidth_reduction(sample_df):
    df_feat = extract_rolling_features(sample_df, window_min=10)
    df_anom = detect_micro_anomalies(df_feat, ['vibration', 'pressure', 'energy_consumption'])
    df_risk = compute_risk_score(df_anom)

    tot, tx, red = simulate_cloud_edge(df_risk)

    assert tot == len(df_risk)
    assert 0 <= red <= 100
    assert red > 50.0

def test_classifier_output_binary(sample_df):
    from sklearn.ensemble import RandomForestClassifier
    import numpy as np

    df_feat = extract_rolling_features(sample_df, window_min=10)
    df_anom = detect_micro_anomalies(df_feat, ['vibration', 'pressure', 'energy_consumption'])
    df_risk = compute_risk_score(df_anom)

    features = ['vib_mean', 'press_var', 'eng_spike_count', 'risk_score']
    X = df_risk[features].fillna(0).values
    y = df_risk['maintenance_required'].values

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)

    preds = model.predict(X)
    assert set(preds).issubset({0, 1})

def test_recall_minimum(sample_df):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import recall_score
    import numpy as np

    df_feat = extract_rolling_features(sample_df, window_min=10)
    df_anom = detect_micro_anomalies(df_feat, ['vibration', 'pressure', 'energy_consumption'])
    df_risk = compute_risk_score(df_anom)

    features = ['vib_mean', 'press_var', 'eng_spike_count', 'risk_score']
    X = df_risk[features].fillna(0).values
    y = df_risk['maintenance_required'].values

    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=None, min_samples_split=2)
    model.fit(X, y)

    preds = model.predict(X)

    if sum(y) > 0:
        assert recall_score(y, preds) > 0.90
