import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import shap

def evaluate_models():
    print("Loading test data and models...")
    X_test_scaled = np.load('X_test_scaled.npy')
    y_test = np.load('y_test.npy')

    with open('rf_model.pkl', 'rb') as f:
        rf_model = pickle.load(f)
    with open('gb_model.pkl', 'rb') as f:
        gb_model = pickle.load(f)
    with open('ridge_model.pkl', 'rb') as f:
        ridge_model = pickle.load(f)

    with open('feature_names.pkl', 'rb') as f:
        feature_names = pickle.load(f)

    print("Generating predictions...")
    y_pred_rf = rf_model.predict(X_test_scaled)
    y_pred_gb = gb_model.predict(X_test_scaled)
    y_pred_ridge = ridge_model.predict(X_test_scaled)

    print("\n--- Model Evaluation ---")
    metrics = {
        'Model': ['Random Forest', 'Gradient Boosting', 'Ridge Regression'],
        'RMSE': [
            np.sqrt(mean_squared_error(y_test, y_pred_rf)),
            np.sqrt(mean_squared_error(y_test, y_pred_gb)),
            np.sqrt(mean_squared_error(y_test, y_pred_ridge))
        ],
        'MAE': [
            mean_absolute_error(y_test, y_pred_rf),
            mean_absolute_error(y_test, y_pred_gb),
            mean_absolute_error(y_test, y_pred_ridge)
        ],
        'R2': [
            r2_score(y_test, y_pred_rf),
            r2_score(y_test, y_pred_gb),
            r2_score(y_test, y_pred_ridge)
        ]
    }
    results_df = pd.DataFrame(metrics)
    print(results_df.to_string(index=False))

    # -------------------- Plot 1: SHAP Feature Importance --------------------
    print("Calculating SHAP values...")
    explainer = shap.TreeExplainer(rf_model)
    shap_values = explainer.shap_values(X_test_scaled)

    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X_test_scaled, feature_names=feature_names, show=False)
    plt.title('SHAP Values: Taxa Importance on Soil Nitrogen')
    plt.tight_layout()
    plt.savefig('fig1_feature_importance.png', dpi=400)
    plt.close()

    # -------------------- Plot 2: Prediction vs Actual --------------------
    plt.figure(figsize=(8, 8))
    plt.scatter(y_test, y_pred_rf, alpha=0.6, label='Random Forest', c='blue')
    plt.scatter(y_test, y_pred_gb, alpha=0.6, label='Gradient Boosting', c='green')

    min_val = min(y_test.min(), y_pred_rf.min(), y_pred_gb.min())
    max_val = max(y_test.max(), y_pred_rf.max(), y_pred_gb.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Perfect Prediction')

    plt.title('Soil Nitrogen Forecasting: Prediction vs Actual')
    plt.legend()
    plt.tight_layout()
    plt.savefig('fig2_pred_vs_actual.png', dpi=400)
    plt.close()

    print("Evaluation complete. Visualizations have been saved.")

if __name__ == "__main__":
    evaluate_models()
