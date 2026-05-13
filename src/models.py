import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from xgboost import XGBRegressor, XGBClassifier
from sklearn.metrics import mean_squared_error, accuracy_score
import optuna
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score

def load_data(input_dir='data/processed'):
    try:
        train_df = pd.read_parquet(os.path.join(input_dir, 'train_features.parquet'))
        val_df = pd.read_parquet(os.path.join(input_dir, 'val_features.parquet'))
        test_df = pd.read_parquet(os.path.join(input_dir, 'test_features.parquet'))
        return train_df, val_df, test_df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def prepare_data(df, task='regression'):
    if df.empty:
        return pd.DataFrame(), pd.Series()

    X = df.drop(columns=['RUL', 'Failure_Label', 'Device_ID'], errors='ignore')

    if task == 'regression':
        if 'RUL' in df.columns:
            y = df['RUL']
        else:
            y = pd.Series([0]*len(df))
    else:
        if 'Failure_Label' in df.columns:
            y = df['Failure_Label']
        else:
            y = pd.Series([0]*len(df))

    return X, y

def train_regression(X_train, y_train, X_val, y_val, trials=10):
    if X_train.empty:
        return None, None

    print("Training Regression Models...")

    # Random Forest (Baseline)
    rf_reg = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_reg.fit(X_train, y_train)

    # XGBoost Optuna Search
    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-5, 10, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-5, 10, log=True),
            'random_state': 42,
            'n_jobs': -1
        }
        model = XGBRegressor(**params)
        model.fit(X_train, y_train)
        preds = model.predict(X_val)
        return np.sqrt(mean_squared_error(y_val, preds))

    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=trials, n_jobs=1)

    best_xgb_reg = XGBRegressor(**study.best_params, random_state=42, n_jobs=-1)
    best_xgb_reg.fit(X_train, y_train)

    return rf_reg, best_xgb_reg

def train_classification(X_train, y_train, X_val, y_val):
    if X_train.empty:
         return None, None

    print("Training Classification Models...")

    # Check if target is multi-class or binary
    n_classes = len(np.unique(y_train))
    if n_classes < 2:
         print("Warning: Only 1 class found in target. Skipping classification training.")
         return None, None

    # Random Forest (Baseline)
    rf_clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    rf_clf.fit(X_train, y_train)

    # XGBoost
    if n_classes == 2:
        # Calculate scale_pos_weight for binary
        try:
             counts = y_train.value_counts()
             scale_pos_weight = counts[0] / counts[1]
             xgb_clf = XGBClassifier(n_estimators=200, scale_pos_weight=scale_pos_weight, random_state=42, use_label_encoder=False, eval_metric='logloss')
        except:
             xgb_clf = XGBClassifier(n_estimators=200, random_state=42, use_label_encoder=False, eval_metric='logloss')
    else:
        xgb_clf = XGBClassifier(n_estimators=200, random_state=42, objective='multi:softprob', eval_metric='mlogloss', use_label_encoder=False)

    xgb_clf.fit(X_train, y_train)

    return rf_clf, xgb_clf

def run_training(trials=50, output_dir='outputs/models/'):
    os.makedirs(output_dir, exist_ok=True)

    train_df, val_df, test_df = load_data()

    # Task A: Regression
    X_train_reg, y_train_reg = prepare_data(train_df, 'regression')
    X_val_reg, y_val_reg = prepare_data(val_df, 'regression')

    rf_reg, xgb_reg = train_regression(X_train_reg, y_train_reg, X_val_reg, y_val_reg, trials=trials)

    if rf_reg:
        joblib.dump(rf_reg, os.path.join(output_dir, 'rf_regressor.joblib'))
    if xgb_reg:
        joblib.dump(xgb_reg, os.path.join(output_dir, 'xgb_regressor.joblib'))

    # Task B: Classification
    X_train_clf, y_train_clf = prepare_data(train_df, 'classification')
    X_val_clf, y_val_clf = prepare_data(val_df, 'classification')

    rf_clf, xgb_clf = train_classification(X_train_clf, y_train_clf, X_val_clf, y_val_clf)

    if rf_clf:
         joblib.dump(rf_clf, os.path.join(output_dir, 'rf_classifier.joblib'))
    if xgb_clf:
         joblib.dump(xgb_clf, os.path.join(output_dir, 'xgb_classifier.joblib'))

    print("Model training complete.")

if __name__ == "__main__":
    run_training(trials=2) # use small number for quick testing if run directly
