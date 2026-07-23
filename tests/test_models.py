import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.features import prepare_data
from src.models import train_logistic_regression, train_svm_linear, check_multicollinearity

def test_models():
    # Make dataset big enough for 5-fold CV (each class needs at least 5 samples)
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
    svm = train_svm_linear(X_train, y_train, preprocessor)

    preds_lr = lr.predict(X_test)
    assert len(preds_lr) == len(X_test)

    preds_svm = svm.predict(X_test)
    assert len(preds_svm) == len(X_test)

    vif = check_multicollinearity(X_train, preprocessor)
    assert not vif.empty
