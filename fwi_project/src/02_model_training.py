import os
import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import optuna
import shap

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')

def load_and_split_data():
    print("Loading processed data...")
    df = pd.read_csv(os.path.join(DATA_DIR, "processed_features.csv"))
    df['day'] = pd.to_datetime(df['day'])

    # Sort chronologically to prevent data leakage
    df = df.sort_values('day')

    # Features
    features = [
        'rmin', 'rmax', 'vs', 'th', 'pr', 'tmmn', 'tmmx', 'erc',
        'kbdi_proxy', 'rh_deficit', 'rmin_3d_avg', 'rmin_7d_avg',
        'pr_3d_avg', 'pr_7d_avg', 'vs_3d_avg', 'vs_7d_avg',
        'wind_shear', 'fire_weather_window', 'month', 'is_florida'
    ]

    # Drop rows with NaN in features
    df = df.dropna(subset=features + ['fwi'])

    print("Splitting data (Train: 2000-2019, Test: 2020-2023)...")
    train = df[df['day'].dt.year <= 2019]
    test = df[df['day'].dt.year >= 2020]

    X_train, y_train = train[features], train['fwi']
    X_test, y_test = test[features], test['fwi']

    print(f"Train size: {len(train)}, Test size: {len(test)}")
    return X_train, X_test, y_train, y_test, features

def train_baseline(X_train, y_train):
    print("Training Baseline Linear Regression...")
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    return lr

def train_rf(X_train, y_train):
    print("Training Random Forest Regressor...")
    # Use smaller number of estimators to speed up
    rf = RandomForestRegressor(n_estimators=50, max_depth=10, min_samples_leaf=5, n_jobs=-1, random_state=42)
    rf.fit(X_train, y_train)
    return rf

def train_xgb(X_train, y_train, X_test, y_test):
    print("Training XGBoost Regressor...")
    # To keep execution fast, we'll use a small optuna study or direct params
    # We will use direct reasonable params here due to runtime constraints
    xgb_reg = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42,
        n_jobs=-1
    )
    xgb_reg.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    return xgb_reg

def main():
    X_train, X_test, y_train, y_test, features = load_and_split_data()
    lr = train_baseline(X_train, y_train)
    rf = train_rf(X_train, y_train)
    xgb_model = train_xgb(X_train, y_train, X_test, y_test)

    print("Models trained successfully.")

def evaluate_models(models, X_test, y_test):
    print("\n--- Evaluation Metrics ---")
    results = {}
    for name, model in models.items():
        preds = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        print(f"{name}: RMSE={rmse:.2f}, MAE={mae:.2f}, R2={r2:.2f}")
        results[name] = {'RMSE': rmse, 'MAE': mae, 'R2': r2}
    return results

def compute_shap(model, X_test, sample_size=1000):
    print("Computing SHAP values for XGBoost...")
    # Using a subsample for SHAP to avoid extreme memory/time cost
    X_sample = X_test.sample(n=min(sample_size, len(X_test)), random_state=42)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X_sample)

    # We will save the shap values and sample for the visualization step
    import pickle
    with open(os.path.join(MODEL_DIR, "shap_values.pkl"), "wb") as f:
        pickle.dump((shap_values, X_sample), f)

    print("Saved SHAP values to shap_values.pkl")

def main():
    X_train, X_test, y_train, y_test, features = load_and_split_data()
    lr = train_baseline(X_train, y_train)
    rf = train_rf(X_train, y_train)
    xgb_model = train_xgb(X_train, y_train, X_test, y_test)

    models = {
        'Linear Regression': lr,
        'Random Forest': rf,
        'XGBoost': xgb_model
    }

    evaluate_models(models, X_test, y_test)
    compute_shap(xgb_model, X_test)

    # Save models
    for name, model in models.items():
        clean_name = name.lower().replace(" ", "_")
        joblib.dump(model, os.path.join(MODEL_DIR, f"{clean_name}.pkl"))

    print("Saved all models.")

if __name__ == "__main__":
    X_train, X_test, y_train, y_test, features = load_and_split_data()
    lr = train_baseline(X_train, y_train)
    rf = train_rf(X_train, y_train)
    xgb_model = train_xgb(X_train, y_train, X_test, y_test)

    models = {
        'Linear Regression': lr,
        'Random Forest': rf,
        'XGBoost': xgb_model
    }

    evaluate_models(models, X_test, y_test)
    compute_shap(xgb_model, X_test)

    # Save models
    for name, model in models.items():
        clean_name = name.lower().replace(" ", "_")
        joblib.dump(model, os.path.join(MODEL_DIR, f"{clean_name}.pkl"))

    print("Saved all models.")
