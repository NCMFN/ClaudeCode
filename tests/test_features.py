import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.features import feature_engineering, get_preprocessor, prepare_data

def test_feature_engineering():
    df = pd.DataFrame({
        'resistance_ohm_per_mi': [10.0, 5.0],
        'capacitance_uf_per_mi': [0.3, 0.4]
    })

    df_eng = feature_engineering(df)

    assert 'RC_interaction' in df_eng.columns
    assert df_eng['RC_interaction'][0] == 3.0
    assert df_eng['RC_interaction'][1] == 2.0

def test_prepare_data():
    df = pd.DataFrame({
        'resistance_ohm_per_mi': [10.0, 5.0, 8.0, 4.0, 11.0, 12.0],
        'capacitance_uf_per_mi': [0.3, 0.4, 0.25, 0.45, 0.35, 0.3],
        'voltage_vdc': [12.0, 12.0, 700.0, 15.0, 12.0, 500.0],
        'length_nmi': [1500, 1000, 2000, 500, 1800, 2200],
        'retardation_ms': [300, 150, 800, 100, 500, 1500],
        'fault_class': ['A', 'B', 'C', 'A', 'B', 'C']
    })

    X_train, X_test, y_train, y_test, preprocessor, le, num_features = prepare_data(df, test_size=0.5, random_state=42)

    assert len(X_train) == 3
    assert len(X_test) == 3
    assert len(y_train) == 3
    assert len(y_test) == 3

    assert 'RC_interaction' in num_features
