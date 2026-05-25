import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import os
import matplotlib.pyplot as plt
import shap
import warnings
import sys

# Ignore unnecessary warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({
    'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
    'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300
})

if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    print("Loading data...")
    sys.stdout.flush()
    df = pd.read_csv("data/feature_engineered.csv")

    # Drop rows with NaN in target or features
    features = ['distanceToShore', 'bearing', 'signed_turn', 'speed_zone_flag', 'turn_intensity_numeric', 'latitude', 'longitude']
    target = 'euc_speed'

    df = df.dropna(subset=features + [target])

    # Stratified split by trajectory ID using GroupShuffleSplit
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(df, groups=df['id']))

    train_df = df.iloc[train_idx]
    test_df = df.iloc[test_idx]

    X_train = train_df[features]
    y_train = train_df[target]

    X_test = test_df[features]
    y_test = test_df[target]

    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    sys.stdout.flush()

    # Reduced max_iter for MLP and reduced estimators for RF/XGB to speed up execution
    models = {
        'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, n_jobs=-1, random_state=42),
        'XGBoost': XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=8, n_jobs=-1, random_state=42),
        'MLP': Pipeline([
            ('scaler', StandardScaler()),
            ('mlp', MLPRegressor(hidden_layer_sizes=(64, 32), activation='relu', max_iter=200, random_state=42))
        ])
    }

    results = {}

    for name, model in models.items():
        print(f"Training {name}...")
        sys.stdout.flush()

        # Train on a sampled dataset to make it execute within reasonable time in this test environment
        sample_size = min(100000, len(X_train))
        X_train_sample = X_train.sample(n=sample_size, random_state=42)
        y_train_sample = y_train.loc[X_train_sample.index]

        model.fit(X_train_sample, y_train_sample)

        test_sample_size = min(20000, len(X_test))
        X_test_sample = X_test.sample(n=test_sample_size, random_state=42)
        y_test_sample = y_test.loc[X_test_sample.index]

        y_pred = model.predict(X_test_sample)

        mae = mean_absolute_error(y_test_sample, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test_sample, y_pred))
        r2 = r2_score(y_test_sample, y_pred)

        results[name] = {'MAE': mae, 'RMSE': rmse, 'R2': r2, 'model': model}
        print(f"{name} Results: MAE={mae:.4f}, RMSE={rmse:.4f}, R2={r2:.4f}")
        sys.stdout.flush()

        # Save model
        filename_map = {'Random Forest': 'rf_model.pkl', 'XGBoost': 'xgb_model.pkl', 'MLP': 'mlp_model.pkl'}
        joblib.dump(model, f"models/{filename_map[name]}")

    # Find best model
    best_model_name = min(results, key=lambda k: results[k]['MAE'])
    print(f"\nBest model is {best_model_name} with MAE = {results[best_model_name]['MAE']:.4f}")
    sys.stdout.flush()

    # Plot MAE comparison
    plt.figure(figsize=(8, 6))
    names = list(results.keys())
    maes = [results[n]['MAE'] for n in names]

    bars = plt.bar(names, maes, color=['#1D9E75', '#BA7517', '#1F3864'])
    plt.ylabel("Mean Absolute Error (knots)")
    plt.title("Model Comparison by MAE")

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.05, round(yval, 4), ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig("outputs/model_comparison_mae.png")
    plt.close()

    # Predicted vs Actual for best model
    best_model = results[best_model_name]['model']

    test_sample_size = min(5000, len(X_test))
    X_test_sample = X_test.sample(n=test_sample_size, random_state=42)
    y_test_sample = y_test.loc[X_test_sample.index]
    y_pred_best = best_model.predict(X_test_sample)

    plt.figure(figsize=(8, 8))

    plt.scatter(y_test_sample, y_pred_best, alpha=0.3, s=10)

    # Plot perfect prediction line
    max_val = max(y_test_sample.max(), y_pred_best.max())
    min_val = min(y_test_sample.min(), y_pred_best.min())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--')

    plt.xlabel("Actual Speed (knots)")
    plt.ylabel("Predicted Speed (knots)")
    plt.title(f"Predicted vs Actual Speed ({best_model_name})")
    plt.tight_layout()
    plt.savefig("outputs/best_model_predictions.png")
    plt.close()

    # SHAP feature importance for best model
    print("Generating SHAP feature importance...")
    sys.stdout.flush()

    shap_sample = X_train_sample.sample(n=min(500, len(X_train_sample)), random_state=42)

    if best_model_name == 'XGBoost':
        explainer = shap.TreeExplainer(best_model)
        shap_values = explainer.shap_values(shap_sample)
    elif best_model_name == 'Random Forest':
        explainer = shap.TreeExplainer(best_model)
        shap_values = explainer.shap_values(shap_sample)
    else: # MLP
        # Extract MLP from pipeline
        mlp = best_model.named_steps['mlp']
        scaler = best_model.named_steps['scaler']
        X_scaled = scaler.transform(shap_sample)
        explainer = shap.KernelExplainer(mlp.predict, shap.kmeans(X_scaled, 10))
        shap_values = explainer.shap_values(X_scaled)

    plt.figure()
    shap.summary_plot(shap_values, shap_sample, show=False)
    plt.tight_layout()
    plt.savefig("outputs/shap_feature_importance.png")
    plt.close()

    print("Phase 3 complete.")
