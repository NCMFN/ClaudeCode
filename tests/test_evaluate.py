import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.features import prepare_data
from src.models import train_logistic_regression
from src.evaluate import evaluate_model, get_logistic_regression_odds_ratios

def test_evaluate():
    df = pd.DataFrame({
        'resistance_ohm_per_mi': np.random.uniform(2.5, 12, 100),
        'capacitance_uf_per_mi': np.random.uniform(0.25, 0.45, 100),
        'voltage_vdc': np.random.uniform(12, 700, 100),
        'length_nmi': np.random.uniform(500, 2200, 100),
        'retardation_ms': np.random.uniform(100, 1800, 100),
        'fault_class': np.random.choice(['A', 'B', 'C'], 100)
    })

    X_train, X_test, y_train, y_test, preprocessor, le, num_features = prepare_data(df, test_size=0.2, random_state=42)
    lr = train_logistic_regression(X_train, y_train, preprocessor)

    res = evaluate_model(lr, X_test, y_test, le)
    assert 'accuracy' in res
    assert 'f1_macro' in res

    or_df = get_logistic_regression_odds_ratios(lr, le)
    assert not or_df.empty
    assert len(or_df.columns) == len(num_features)
