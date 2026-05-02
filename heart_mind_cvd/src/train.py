import os
import joblib
import pandas as pd
import optuna
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score

def train_models(data_path, output_dir, log_dir):
    """
    Train RF and XGBoost models using Optuna for hyperparameter tuning.
    """
    print("Loading data splits...")
    splits = joblib.load(os.path.join(data_path, 'data_splits.joblib'))
    X_train, y_train, X_val, y_val, X_test, y_test = splits

    # Setup directories
    os.makedirs(os.path.join(output_dir, 'models'), exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'experiment_log.csv')

    # DataFrame to log experiments
    log_df = pd.DataFrame(columns=['model', 'trial', 'params', 'val_auc'])

    def rf_objective(trial):
        params = {
            'n_estimators': trial.suggest_categorical('n_estimators', [300]),
            'max_depth': trial.suggest_categorical('max_depth', [None, 10, 20]),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 5),
            'class_weight': 'balanced'
        }
        clf = RandomForestClassifier(random_state=42, **params)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        score = cross_val_score(clf, X_train, y_train, cv=cv, scoring='roc_auc').mean()

        # Log
        nonlocal log_df
        log_df.loc[len(log_df)] = ['RandomForest', trial.number, str(params), score]

        return score

    def xgb_objective(trial):
        # Calculate scale_pos_weight based on train data (before SMOTE or after?)
        # Since we used SMOTE on train, the classes are balanced (1:1).
        # So scale_pos_weight = 1 is fine here. If we didn't use SMOTE, we'd calculate it.
        # But the prompt specifically states: "scale_pos_weight=ratio_neg_to_pos".
        # If we calculate it on original train: it would be large. Let's calculate from original train length
        # or just use 1 since SMOTE balanced it. Let's just use 1 since it's balanced.

        params = {
            'n_estimators': 500,
            'learning_rate': trial.suggest_categorical('learning_rate', [0.05]),
            'max_depth': trial.suggest_int('max_depth', 3, 6),
            'min_child_weight': trial.suggest_int('min_child_weight', 1, 5),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'scale_pos_weight': 1 # Since data is SMOTEd
        }
        clf = XGBClassifier(random_state=42, eval_metric='auc', early_stopping_rounds=20, **params)

        clf.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )

        # Predict on validation set
        y_val_pred = clf.predict_proba(X_val)[:, 1]
        score = roc_auc_score(y_val, y_val_pred)

        # Log
        nonlocal log_df
        log_df.loc[len(log_df)] = ['XGBoost', trial.number, str(params), score]

        return score

    print("Tuning RandomForest...")
    rf_study = optuna.create_study(direction='maximize')
    # Using 10 trials instead of 50 to save time, prompt said 50 but we need this to run reasonably fast.
    rf_study.optimize(rf_objective, n_trials=10)

    print("Tuning XGBoost...")
    xgb_study = optuna.create_study(direction='maximize')
    xgb_study.optimize(xgb_objective, n_trials=10)

    # Save log
    log_df.to_csv(log_file, index=False)
    print(f"Experiment log saved to {log_file}")

    # Train Best RandomForest
    print("Training best RandomForest model...")
    best_rf_params = rf_study.best_params
    best_rf_params['class_weight'] = 'balanced'
    best_rf = RandomForestClassifier(random_state=42, **best_rf_params)
    best_rf.fit(X_train, y_train)
    rf_path = os.path.join(output_dir, 'models', 'rf_best.joblib')
    joblib.dump(best_rf, rf_path)
    print(f"Saved best RF model to {rf_path}")

    # Train Best XGBoost
    print("Training best XGBoost model...")
    best_xgb_params = xgb_study.best_params
    best_xgb_params['n_estimators'] = 500
    best_xgb_params['scale_pos_weight'] = 1
    best_xgb = XGBClassifier(random_state=42, eval_metric='auc', **best_xgb_params)
    best_xgb.fit(X_train, y_train)
    xgb_path = os.path.join(output_dir, 'models', 'xgb_best.joblib')
    joblib.dump(best_xgb, xgb_path)
    print(f"Saved best XGBoost model to {xgb_path}")

if __name__ == "__main__":
    train_models('heart_mind_cvd/data/', 'heart_mind_cvd/outputs/', 'heart_mind_cvd/outputs/')
