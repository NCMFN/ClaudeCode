import pandas as pd
import numpy as np
import lightgbm as lgb
import optuna
import joblib
import logging
import json
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold
from config import RANDOM_SEED, LGBM_EARLY_STOPPING_ROUNDS

class LightGBMEtaModel:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.q_low_model = None
        self.q_high_model = None

    def tune(self, X, y, n_trials=100):
        self.logger.info(f"Starting Optuna hyperparameter search with {n_trials} trials")
        optuna.logging.set_verbosity(optuna.logging.WARNING)

        def objective(trial):
            params = {
                "objective": "regression",
                "metric": "rmse",
                "boosting_type": "gbdt",
                "num_leaves": trial.suggest_int("num_leaves", 20, 300),
                "max_depth": trial.suggest_int("max_depth", 3, 12),
                "learning_rate": trial.suggest_float("learning_rate", 0.005, 0.3, log=True),
                "n_estimators": trial.suggest_int("n_estimators", 200, 2000),
                "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
                "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
                "random_state": RANDOM_SEED,
                "n_jobs": -1,
                "verbose": -1
            }

            cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
            rmses = []

            for train_idx, val_idx in cv.split(X):
                X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

                model = lgb.LGBMRegressor(**params)
                model.fit(
                    X_tr, y_tr,
                    eval_set=[(X_val, y_val)],
                    eval_metric="rmse",
                    callbacks=[lgb.early_stopping(LGBM_EARLY_STOPPING_ROUNDS, verbose=False)]
                )

                preds = model.predict(X_val)
                rmse = np.sqrt(mean_squared_error(y_val, preds))
                rmses.append(rmse)

            return np.mean(rmses)

        study = optuna.create_study(
            direction="minimize",
            sampler=optuna.samplers.TPESampler(seed=RANDOM_SEED),
            pruner=optuna.pruners.MedianPruner()
        )
        study.optimize(objective, n_trials=n_trials)

        self.logger.info(f"Best RMSE: {study.best_value:.4f}")
        self.logger.info(f"Best params: {study.best_params}")

        # Save study results
        study.trials_dataframe().to_csv('outputs/results/optuna_study.csv', index=False)
        with open('outputs/results/best_lgbm_params.json', 'w') as f:
            json.dump(study.best_params, f)

        return study.best_params

    def fit(self, X_train, y_train, X_val, y_val, params=None):
        if params is None:
            params = {
                "objective": "regression",
                "random_state": RANDOM_SEED,
                "n_estimators": 500,
                "n_jobs": -1,
                "verbose": -1
            }
        else:
            params['objective'] = "regression"
            params['random_state'] = RANDOM_SEED
            params['n_jobs'] = -1
            params['verbose'] = -1

        self.logger.info("Training final LightGBM model...")
        self.model = lgb.LGBMRegressor(**params)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            eval_metric="rmse",
            callbacks=[lgb.early_stopping(LGBM_EARLY_STOPPING_ROUNDS, verbose=False)]
        )
        self.logger.info("Training complete.")

        # Train quantile models for confidence intervals
        self.logger.info("Training quantile regression models for confidence intervals...")
        q_params_low = params.copy()
        q_params_low.update({"objective": "quantile", "alpha": 0.1})
        self.q_low_model = lgb.LGBMRegressor(**q_params_low)
        self.q_low_model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(LGBM_EARLY_STOPPING_ROUNDS, verbose=False)]
        )

        q_params_high = params.copy()
        q_params_high.update({"objective": "quantile", "alpha": 0.9})
        self.q_high_model = lgb.LGBMRegressor(**q_params_high)
        self.q_high_model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(LGBM_EARLY_STOPPING_ROUNDS, verbose=False)]
        )
        self.logger.info("Quantile models training complete.")

    def predict(self, X):
        return self.model.predict(X)

    def predict_intervals(self, X):
        lower = self.q_low_model.predict(X)
        upper = self.q_high_model.predict(X)
        return lower, upper

    def save(self, txt_path, pkl_path):
        self.model.booster_.save_model(txt_path)
        joblib.dump(self.model, pkl_path)
        joblib.dump(self.q_low_model, pkl_path.replace('.pkl', '_q01.pkl'))
        joblib.dump(self.q_high_model, pkl_path.replace('.pkl', '_q09.pkl'))
        self.logger.info(f"Saved LightGBM models to {txt_path} and {pkl_path}")
