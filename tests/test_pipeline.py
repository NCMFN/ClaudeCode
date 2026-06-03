import pytest
import pandas as pd
import numpy as np

def test_feature_engineering():
    from src.feature_engineering import engineer_features

    # Mock data
    df = pd.DataFrame({
        'Node_ID': [1, 2],
        'Timestamp': ['2024-01-01 00:00:00', '2024-01-01 00:01:00'],
        'Residual_Energy': [50.0, 30.0],
        'Noise_Level': [20.0, 40.0],
        'X_Coordinate': [10.0, 20.0],
        'Y_Coordinate': [10.0, 20.0]
    })

    df_engineered = engineer_features(df)

    assert 'ENR' in df_engineered.columns
    assert 'SDF' in df_engineered.columns
    assert 'Temporal_Noise_Smoothing' in df_engineered.columns

    # ENR should be around 50/20 = 2.5 and 30/40 = 0.75
    np.testing.assert_almost_equal(df_engineered['ENR'].iloc[0], 2.5, decimal=1)

def test_preprocessing():
    from src.preprocessing import preprocess_data

    df = pd.DataFrame({
        'Node_ID': range(100),
        'Timestamp': [f'2024-01-01 00:{i:02d}:00' for i in range(60)] + [f'2024-01-01 01:{i:02d}:00' for i in range(40)],
        'Residual_Energy': np.random.uniform(0, 100, 100),
        'Noise_Level': np.random.uniform(20, 50, 100),
        'Signal_Strength': np.random.uniform(-90, -30, 100),
        'Transmission_Power': np.random.uniform(0, 20, 100),
        'Detection_Accuracy': np.random.uniform(0, 100, 100),
        'X_Coordinate': np.random.uniform(0, 100, 100),
        'Y_Coordinate': np.random.uniform(0, 100, 100),
    })

    # Add engineered columns manually for testing
    from src.feature_engineering import engineer_features
    df = engineer_features(df)

    X_train, X_val, X_test, y_train, y_val, y_test, features = preprocess_data(df)

    # Check splits
    assert len(X_train) + len(X_val) + len(X_test) == len(df)
    assert 'Detection_Accuracy' not in X_train.columns
    assert 'Node_ID' not in X_train.columns
