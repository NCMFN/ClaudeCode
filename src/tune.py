import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import os
import json

def tune_xgboost(X_train, y_train, X_test, y_test, out_dir="results/models"):
    """
    Tunes the XGBoost regressor (which was the best from validation)
    using RandomizedSearchCV and evaluates on the Test set.
    """
    os.makedirs(out_dir, exist_ok=True)

    print("Starting hyperparameter tuning for XGBoost...")
    param_distributions = {
        'n_estimators': [100, 200, 300, 400],
        'max_depth': [4, 6, 8, 10],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'subsample': [0.6, 0.8, 1.0],
        'colsample_bytree': [0.6, 0.8, 1.0]
    }

    xgb = XGBRegressor(random_state=42, n_jobs=-1)

    search = RandomizedSearchCV(
        estimator=xgb,
        param_distributions=param_distributions,
        n_iter=10,  # Keeping iterations reasonable for execution time
        scoring='neg_root_mean_squared_error',
        cv=3,
        verbose=1,
        random_state=42,
        n_jobs=-1
    )

    search.fit(X_train, y_train)

    best_model = search.best_estimator_
    print(f"Best parameters found: {search.best_params_}")

    # Evaluate on test set
    preds = best_model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    print(f"\nFinal Test Set Evaluation (Best XGBoost):")
    print(f"RMSE: {rmse:.6f}")
    print(f"MAE: {mae:.6f}")
    print(f"R2: {r2:.6f}")

    joblib.dump(best_model, os.path.join(out_dir, 'Best_XGBoost.pkl'))

    results = {
        'best_params': search.best_params_,
        'test_metrics': {
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2
        }
    }

    with open(os.path.join(out_dir, 'tuning_results.json'), 'w') as f:
        json.dump(results, f, indent=4)

    return best_model

if __name__ == "__main__":
    from data_loader import download_data, load_all_datasets
    from feature_engineering import engineer_features
    from preprocessing import preprocess_data

    p_path, _, _ = download_data()
    df = load_all_datasets(p_path, None, None)
    df = engineer_features(df)
    # Note: we pass X_train and evaluate on X_test for the final report
    X_train, X_val, X_test, y_train, y_val, y_test, _ = preprocess_data(df)

    tune_xgboost(X_train, y_train, X_test, y_test)
