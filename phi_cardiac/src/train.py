import pandas as pd
import numpy as np
import os
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBRegressor
import optuna

def root_mean_squared_error(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))

def train_models(input_file, model_dir):
    os.makedirs(model_dir, exist_ok=True)
    df = pd.read_csv(input_file, parse_dates=['date'])
    df = df.sort_values(['city', 'date'])

    # We will dummy encode 'city'
    df = pd.get_dummies(df, columns=['city'], drop_first=True)

    train_mask = df['split'] == 'train'
    val_mask = df['split'] == 'val'
    test_mask = df['split'] == 'test'

    city_cols = [c for c in df.columns if c.startswith('city_')]

    target_col = 'target_log1p'

    # Model 1: Baseline: OLS linear regression (temperature only)
    features_m1 = ['t2m'] + city_cols
    X_train_m1 = df.loc[train_mask, features_m1]
    y_train = df.loc[train_mask, target_col]
    X_test_m1 = df.loc[test_mask, features_m1]
    y_test = df.loc[test_mask, target_col]
    y_test_orig = np.expm1(y_test)

    m1 = LinearRegression()
    m1.fit(X_train_m1, y_train)
    m1_pred = m1.predict(X_test_m1)
    m1_pred_orig = np.expm1(m1_pred)

    # Model 2: OLS with PM2.5 + temperature separately
    features_m2 = ['t2m', 'pm25_mean'] + city_cols
    X_train_m2 = df.loc[train_mask, features_m2]
    X_test_m2 = df.loc[test_mask, features_m2]

    m2 = LinearRegression()
    m2.fit(X_train_m2, y_train)
    m2_pred = m2.predict(X_test_m2)
    m2_pred_orig = np.expm1(m2_pred)

    # Model 3: XGBRegressor using all features including PHI interaction term
    features_m3 = ['t2m', 'pm25_mean', 'no2_mean', 'o3_mean', 'feels_like_temp',
                   'relative_humidity', 'wind_speed', 'pm25_lag24', 'pm25_lag48', 'pm25_lag72',
                   't2m_lag24', 't2m_lag48', 't2m_lag72', 't2m_zscore', 'phi_initial',
                   'day_of_week', 'month', 'is_weekend', 'is_heatwave',
                   'pm25_3day_rolling_mean', 'temp_3day_rolling_mean'] + city_cols

    X_train_m3 = df.loc[train_mask, features_m3]
    X_val_m3 = df.loc[val_mask, features_m3]
    y_val = df.loc[val_mask, target_col]
    X_test_m3 = df.loc[test_mask, features_m3]

    def objective(trial):
        params = {
            'n_estimators': trial.suggest_categorical('n_estimators', [200, 1000]),
            'max_depth': trial.suggest_categorical('max_depth', [3, 8]),
            'learning_rate': trial.suggest_categorical('learning_rate', [0.01, 0.3]),
            'subsample': trial.suggest_categorical('subsample', [0.6, 1.0]),
            'random_state': 42,
            'n_jobs': -1
        }

        # We simulate TimeSeriesSplit
        tscv = TimeSeriesSplit(n_splits=5)
        scores = []
        # Since pandas index might be messy, reset it
        X_tmp = X_train_m3.reset_index(drop=True)
        y_tmp = y_train.reset_index(drop=True)

        for train_index, val_index in tscv.split(X_tmp):
            X_tr, X_va = X_tmp.iloc[train_index], X_tmp.iloc[val_index]
            y_tr, y_va = y_tmp.iloc[train_index], y_tmp.iloc[val_index]

            model = XGBRegressor(**params)
            model.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], verbose=False)
            preds = model.predict(X_va)
            scores.append(mean_squared_error(y_va, preds))

        return np.mean(scores)

    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=10) # Using 10 trials instead of 50 for speed in sandbox

    best_params = study.best_params
    best_params['random_state'] = 42

    m3 = XGBRegressor(**best_params)
    m3.fit(X_train_m3, y_train, eval_set=[(X_val_m3, y_val)], verbose=False)
    m3_pred = m3.predict(X_test_m3)
    m3_pred_orig = np.expm1(m3_pred)

    joblib.dump(m3, os.path.join(model_dir, 'xgb_phi_best.joblib'))

    # Model 4: XGBRegressor using lagged features only (48-72h lags)
    features_m4 = ['pm25_lag48', 'pm25_lag72', 't2m_lag48', 't2m_lag72'] + city_cols
    X_train_m4 = df.loc[train_mask, features_m4]
    X_test_m4 = df.loc[test_mask, features_m4]

    m4 = XGBRegressor(**best_params)
    m4.fit(X_train_m4, y_train, verbose=False)
    m4_pred = m4.predict(X_test_m4)
    m4_pred_orig = np.expm1(m4_pred)

    # Evaluation dictionary
    results = []

    models = {
        'Baseline (T only)': m1_pred_orig,
        'OLS (PM2.5 + T)': m2_pred_orig,
        'XGBoost (All + PHI)': m3_pred_orig,
        'XGBoost (Lags only)': m4_pred_orig
    }

    for name, pred_orig in models.items():
        r2 = r2_score(y_test_orig, pred_orig)
        rmse = root_mean_squared_error(y_test_orig, pred_orig)
        mae = mean_absolute_error(y_test_orig, pred_orig)

        results.append({
            'Model': name,
            'R2': r2,
            'RMSE': rmse,
            'MAE': mae
        })
        print(f"{name} - R2: {r2:.4f}, RMSE: {rmse:.4f}, MAE: {mae:.4f}")

    pd.DataFrame(results).to_csv(os.path.join(model_dir, 'model_metrics.csv'), index=False)

if __name__ == "__main__":
    train_models(
        input_file="data/processed/phi_features.csv",
        model_dir="outputs/models"
    )
