import os
import sys
import joblib

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

from lightgbm import LGBMRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.base import clone

class EarlyStoppingMultiOutputRegressor(MultiOutputRegressor):
    def fit(self, X, y, eval_set=None, **fit_params):
        if eval_set is not None:
            import lightgbm as lgb
            X_val, y_val = eval_set[0]
            self.estimators_ = []
            for i in range(y.shape[1]):
                estimator = clone(self.estimator)
                y_i = y.iloc[:, i] if hasattr(y, 'iloc') else y[:, i]
                y_val_i = y_val.iloc[:, i] if hasattr(y_val, 'iloc') else y_val[:, i]
                callbacks = [lgb.early_stopping(stopping_rounds=50, verbose=False)]
                estimator.fit(X, y_i, eval_set=[(X_val, y_val_i)], callbacks=callbacks, **fit_params)
                self.estimators_.append(estimator)
            return self
        else:
            return super().fit(X, y, **fit_params)

def get_lightgbm_model(params=None):
    if params is None:
        params = {
            "n_estimators": 500,
            "num_leaves": 63,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "random_state": 42,
            "n_jobs": -1,
            "verbose": -1
        }
    base_model = LGBMRegressor(**params)
    multi_model = EarlyStoppingMultiOutputRegressor(base_model)
    return multi_model

def train_lightgbm(X_train, y_train, X_val, y_val, params=None):
    model = get_lightgbm_model(params)
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)])
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    joblib.dump(model.estimators_[0], os.path.join(config.MODEL_DIR, 'lgbm_kMc.pkl'))
    joblib.dump(model.estimators_[1], os.path.join(config.MODEL_DIR, 'lgbm_kMt.pkl'))
    joblib.dump(model, os.path.join(config.MODEL_DIR, 'lgbm_model.pkl'))
    return model
