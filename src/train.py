import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import os
import json

def train_and_evaluate(X_train, y_train, X_val, y_val, out_dir="results/models"):
    os.makedirs(out_dir, exist_ok=True)

    models = {
        'XGBoost': XGBRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            random_state=42,
            n_jobs=-1
        ),
        'RandomForest': RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        ),
        'SVR': SVR(
            kernel='rbf',
            C=10,
            epsilon=0.1
        )
    }

    results = []

    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)

        preds = model.predict(X_val)

        rmse = np.sqrt(mean_squared_error(y_val, preds))
        mae = mean_absolute_error(y_val, preds)
        r2 = r2_score(y_val, preds)

        results.append({
            'Model': name,
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2
        })

        joblib.dump(model, os.path.join(out_dir, f"{name}.pkl"))

    results_df = pd.DataFrame(results)
    print("\nModel Evaluation Summary:")
    print(results_df.to_string(index=False))

    # Save results to JSON
    with open(os.path.join(out_dir, 'validation_results.json'), 'w') as f:
        json.dump(results, f, indent=4)

    return models, results_df

if __name__ == "__main__":
    from data_loader import download_data, load_all_datasets
    from feature_engineering import engineer_features
    from preprocessing import preprocess_data

    p_path, _, _ = download_data()
    df = load_all_datasets(p_path, None, None)
    df = engineer_features(df)
    X_train, X_val, X_test, y_train, y_val, y_test, _ = preprocess_data(df)

    train_and_evaluate(X_train, y_train, X_val, y_val)
