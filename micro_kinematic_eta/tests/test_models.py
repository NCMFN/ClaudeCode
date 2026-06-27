import pytest
import pandas as pd
import numpy as np
import os
from src.models.baseline_linear import LinearBaselineModel
from src.models.baseline_rf import RFBaselineModel

def test_models_predict_and_evaluate():
    X = pd.DataFrame(np.random.randn(10, 5), columns=['f1', 'f2', 'f3', 'f4', 'f5'])
    y = pd.Series(np.random.rand(10) * 10)

    # Linear
    lr = LinearBaselineModel()
    lr.fit(X, y)
    preds = lr.predict(X)
    assert len(preds) == 10
    assert not np.isnan(preds).any()

    metrics, _ = lr.evaluate(X, y)
    assert np.isfinite(metrics['rmse']) and metrics['rmse'] >= 0

    # RF
    rf = RFBaselineModel()
    rf.fit(X, y)
    preds = rf.predict(X)
    assert len(preds) == 10
    assert not np.isnan(preds).any()

    metrics, _ = rf.evaluate(X, y)
    assert np.isfinite(metrics['rmse']) and metrics['rmse'] >= 0

def test_optuna_lgbm():
    from src.models.lightgbm_model import LightGBMEtaModel
    import pandas as pd
    import numpy as np
    import os

    os.makedirs("outputs/results", exist_ok=True)
    X = pd.DataFrame(np.random.randn(500, 5), columns=["f1", "f2", "f3", "f4", "f5"])
    y = pd.Series(np.random.rand(500) * 10)

    model = LightGBMEtaModel()
    params = model.tune(X, y, n_trials=3)

    assert "num_leaves" in params
    assert os.path.exists("outputs/results/optuna_study.csv")

    # split for fit
    X_train, X_val = X.iloc[:400], X.iloc[400:]
    y_train, y_val = y.iloc[:400], y.iloc[400:]

    model.fit(X_train, y_train, X_val, y_val, params=params)
    preds = model.predict(X_val)

    assert len(preds) == 100
    assert not np.isnan(preds).any()
