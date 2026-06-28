import os
import sys
import joblib

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

from sklearn.neural_network import MLPRegressor
from sklearn.multioutput import MultiOutputRegressor

def get_mlp_model(params=None):
    if params is None:
        params = {
            "hidden_layer_sizes": (256, 128, 64),
            "activation": 'relu',
            "solver": 'adam',
            "learning_rate_init": 0.001,
            "max_iter": 500,
            "early_stopping": True,
            "validation_fraction": 0.1,
            "random_state": 42
        }
    base_model = MLPRegressor(**params)
    multi_model = MultiOutputRegressor(base_model)
    return multi_model

def train_mlp(X_train, y_train, params=None):
    model = get_mlp_model(params)
    model.fit(X_train, y_train)
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(config.MODEL_DIR, 'mlp_model.pkl'))
    return model
