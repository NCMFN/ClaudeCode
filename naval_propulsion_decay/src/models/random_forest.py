import os
import sys
import joblib

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor

def get_rf_model(params=None):
    if params is None:
        params = {
            "n_estimators": 300,
            "max_depth": 20,
            "min_samples_leaf": 2,
            "max_features": 0.7,
            "oob_score": True,
            "random_state": 42,
            "n_jobs": -1
        }
    base_model = RandomForestRegressor(**params)
    multi_model = MultiOutputRegressor(base_model)
    return multi_model

def train_rf(X_train, y_train, params=None):
    model = get_rf_model(params)
    model.fit(X_train, y_train)
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(config.MODEL_DIR, 'rf_model.pkl'))
    return model
