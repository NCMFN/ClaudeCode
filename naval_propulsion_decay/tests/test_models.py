import pytest
import os
import sys
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.models.xgboost_model import train_xgboost
from src.models.lightgbm_model import train_lightgbm
from src.models.random_forest import train_rf
from src.models.mlp_regressor import train_mlp
from src.evaluator import DecayEvaluator

def test_models():
    np.random.seed(42)
    X_train = pd.DataFrame(np.random.rand(200, 16), columns=config.FEATURE_NAMES)
    y_train = pd.DataFrame(np.random.rand(200, 2) * 0.1 + 0.9, columns=config.TARGET_NAMES) # ranges 0.9-1.0
    X_val = pd.DataFrame(np.random.rand(20, 16), columns=config.FEATURE_NAMES)
    y_val = pd.DataFrame(np.random.rand(20, 2) * 0.1 + 0.9, columns=config.TARGET_NAMES)

    xgb_model = train_xgboost(X_train, y_train, X_val, y_val, params={'n_estimators': 10, 'max_depth': 3})

    xgb_preds = xgb_model.predict(X_val)
    assert xgb_preds.shape == (20, 2)

    lgbm_model = train_lightgbm(X_train, y_train, X_val, y_val, params={'n_estimators': 10, 'num_leaves': 10, 'verbose': -1})
    lgbm_preds = lgbm_model.predict(X_val)
    assert (lgbm_preds >= 0).all()

    rf_model = train_rf(X_train, y_train, params={'n_estimators': 10, 'max_depth': 3})
    rf_preds = rf_model.predict(X_val)
    assert (rf_preds >= 0).all()

    mlp_model = train_mlp(X_train, y_train, params={'hidden_layer_sizes': (10,), 'max_iter': 10})
    mlp_preds = mlp_model.predict(X_val)

    evaluator = DecayEvaluator()
    res, _, _ = evaluator.evaluate(xgb_model, 'xgb', 'minmax', 'full', X_val, y_val)

    assert res['MAE_kMc'] >= 0
    assert res['MAE_kMt'] >= 0
    assert 'target_achieved' in res
    assert isinstance(res['target_achieved'], bool)
