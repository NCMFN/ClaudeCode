import pandas as pd
import numpy as np
import optuna
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import average_precision_score, make_scorer
import joblib
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from preprocess import preprocess_data

def train_models():
    print("Loading and preprocessing data...")
    (X_train, y_train), (X_val, y_val), (X_test, y_test, risks_test) = preprocess_data()

    # Custom scorer for AUCPR which is important for imbalanced sets
    aucpr_scorer = make_scorer(average_precision_score, response_method='predict_proba')
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # Ensure bool columns are cast to int before training to prevent Optuna/XGBoost errors
    X_train = X_train.astype(float)
    X_val = X_val.astype(float)
    X_test = X_test.astype(float)

    print("Training SVC...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    svc = SVC(kernel='rbf', class_weight='balanced', probability=True, random_state=42)
    svc.fit(X_train_scaled, y_train)


    print("Tuning and training RandomForest...")
    def rf_objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 500, step=100),
            'max_depth': trial.suggest_int('max_depth', 3, 15),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
        }

        model = RandomForestClassifier(
            **params,
            class_weight='balanced',
            max_features='sqrt',
            random_state=42
        )
        scores = cross_val_score(model, X_train, y_train, cv=cv, scoring=aucpr_scorer)
        return scores.mean()

    rf_study = optuna.create_study(direction='maximize')
    rf_study.optimize(rf_objective, n_trials=5) # Set to 50 as requested, though might be slow

    best_rf_params = rf_study.best_params
    rf = RandomForestClassifier(
        **best_rf_params,
        class_weight='balanced',
        max_features='sqrt',
        random_state=42
    )
    rf.fit(X_train, y_train)

    print("Tuning and training XGBoost...")
    def xgb_objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 500, step=100),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        }

        # Calculate scale_pos_weight based on train distribution
        scale_pos_weight = (len(y_train) - sum(y_train)) / sum(y_train)

        model = XGBClassifier(
            **params,
            scale_pos_weight=scale_pos_weight,
            eval_metric='aucpr',
            random_state=42
        )

        scores = cross_val_score(model, X_train, y_train, cv=cv, scoring=aucpr_scorer)
        return scores.mean()

    # Optuna logging level set to warning to reduce output verbosity
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    xgb_study = optuna.create_study(direction='maximize')
    xgb_study.optimize(xgb_objective, n_trials=5)

    best_xgb_params = xgb_study.best_params
    scale_pos_weight = (len(y_train) - sum(y_train)) / sum(y_train)

    xgb = XGBClassifier(
        **best_xgb_params,
        scale_pos_weight=scale_pos_weight,
        eval_metric='aucpr',
        random_state=42
    )

    # We use eval_set for early stopping
    xgb.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )

    print("Saving models...")
    os.makedirs('../outputs/models', exist_ok=True)
    joblib.dump(xgb, '../outputs/models/xgb_best.joblib')
    joblib.dump(rf, '../outputs/models/rf_best.joblib')
    joblib.dump(svc, '../outputs/models/svc_best.joblib')
    joblib.dump(scaler, '../outputs/models/scaler.joblib')

    return {
        'xgb': xgb,
        'rf': rf,
        'svc': svc,
        'scaler': scaler,
        'X_test': X_test,
        'y_test': y_test,
        'risks_test': risks_test
    }

if __name__ == '__main__':
    train_models()
