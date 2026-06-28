import optuna
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error
import os
import sys
import json
import warnings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.models.xgboost_model import get_xgboost_model
from src.models.lightgbm_model import get_lightgbm_model

optuna.logging.set_verbosity(optuna.logging.WARNING)

class PropulsionTuner:
    def __init__(self, X_train, y_train):
        self.X_train = X_train
        self.y_train = y_train

        self.sampler = optuna.samplers.TPESampler(seed=config.RANDOM_SEED)
        self.pruner = optuna.pruners.MedianPruner(n_startup_trials=10, n_warmup_steps=5)

        os.makedirs(config.RESULTS_DIR, exist_ok=True)

    def tune_xgboost(self, n_trials=config.OPTUNA_TRIALS):
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 200, 2000),
                "max_depth": trial.suggest_int("max_depth", 3, 10),
                "learning_rate": trial.suggest_float("learning_rate", 0.005, 0.3, log=True),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
                "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
                "min_child_weight": trial.suggest_int("min_child_weight", 1, 20),
                "gamma": trial.suggest_float("gamma", 0, 5),
                "random_state": 42,
                "n_jobs": -1
            }

            kf = KFold(n_splits=5, shuffle=True, random_state=42)
            scores = []

            for train_idx, val_idx in kf.split(self.X_train):
                X_tr, X_val = self.X_train.iloc[train_idx], self.X_train.iloc[val_idx]
                y_tr, y_val = self.y_train.iloc[train_idx], self.y_train.iloc[val_idx]

                model = get_xgboost_model(params)
                model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)])

                preds = model.predict(X_val)
                mae_kMc = mean_absolute_error(y_val.iloc[:, 0], preds[:, 0])
                mae_kMt = mean_absolute_error(y_val.iloc[:, 1], preds[:, 1])
                scores.append((mae_kMc + mae_kMt) / 2)

            return np.mean(scores)

        study = optuna.create_study(direction="minimize", sampler=self.sampler, pruner=self.pruner)
        study.optimize(objective, n_trials=n_trials, timeout=config.OPTUNA_TIMEOUT_SECONDS)

        study.trials_dataframe().to_csv(os.path.join(config.RESULTS_DIR, 'optuna_xgb_study.csv'), index=False)
        with open(os.path.join(config.RESULTS_DIR, 'best_xgb_params.json'), 'w') as f:
            json.dump(study.best_params, f, indent=4)

        return study

    def tune_lightgbm(self, n_trials=config.OPTUNA_TRIALS):
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 200, 2000),
                "num_leaves": trial.suggest_int("num_leaves", 20, 300),
                "max_depth": trial.suggest_int("max_depth", 3, 12),
                "learning_rate": trial.suggest_float("learning_rate", 0.005, 0.3, log=True),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
                "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
                "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
                "random_state": 42,
                "n_jobs": -1,
                "verbose": -1
            }

            kf = KFold(n_splits=5, shuffle=True, random_state=42)
            scores = []

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                for train_idx, val_idx in kf.split(self.X_train):
                    X_tr, X_val = self.X_train.iloc[train_idx], self.X_train.iloc[val_idx]
                    y_tr, y_val = self.y_train.iloc[train_idx], self.y_train.iloc[val_idx]

                    model = get_lightgbm_model(params)
                    model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)])

                    preds = model.predict(X_val)
                    mae_kMc = mean_absolute_error(y_val.iloc[:, 0], preds[:, 0])
                    mae_kMt = mean_absolute_error(y_val.iloc[:, 1], preds[:, 1])
                    scores.append((mae_kMc + mae_kMt) / 2)

            return np.mean(scores)

        study = optuna.create_study(direction="minimize", sampler=self.sampler, pruner=self.pruner)
        study.optimize(objective, n_trials=n_trials, timeout=config.OPTUNA_TIMEOUT_SECONDS)

        study.trials_dataframe().to_csv(os.path.join(config.RESULTS_DIR, 'optuna_lgbm_study.csv'), index=False)
        with open(os.path.join(config.RESULTS_DIR, 'best_lgbm_params.json'), 'w') as f:
            json.dump(study.best_params, f, indent=4)

        return study
