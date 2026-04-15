import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf

def evaluate_models():
    print("Loading test data and models...")
    X_test_scaled = np.load('X_test_scaled.npy')
    y_test = np.load('y_test.npy')

    with open('rf_model.pkl', 'rb') as f:
        rf_model = pickle.load(f)

    nn_model = tf.keras.models.load_model('nn_model.keras')

    with open('feature_names.pkl', 'rb') as f:
        feature_names = pickle.load(f)

    # Predictions
    print("Generating predictions...")
    y_pred_rf = rf_model.predict(X_test_scaled)
    y_pred_nn = nn_model.predict(X_test_scaled).flatten()

    # Calculate metrics
    print("\n--- Model Evaluation ---")

    metrics = {
        'Model': ['Random Forest', 'Deep Learning (FNN)'],
        'RMSE': [np.sqrt(mean_squared_error(y_test, y_pred_rf)), np.sqrt(mean_squared_error(y_test, y_pred_nn))],
        'MAE': [mean_absolute_error(y_test, y_pred_rf), mean_absolute_error(y_test, y_pred_nn)],
        'R2': [r2_score(y_test, y_pred_rf), r2_score(y_test, y_pred_nn)]
    }

    results_df = pd.DataFrame(metrics)
    print(results_df.to_string(index=False))

    # Feature Importance (Random Forest)
    print("\nExtracting feature importance...")
    importances = rf_model.feature_importances_
    indices = np.argsort(importances)[::-1]

    top_n = 10
    top_features = [feature_names[i] for i in indices[:top_n]]
    top_importances = importances[indices][:top_n]

    # Plotting Feature Importance
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_importances, y=top_features, palette='viridis', hue=top_features, legend=False)
    plt.title('Top 10 Microbial Taxa / Features driving Nitrogen Prediction')
    plt.xlabel('Relative Importance (Random Forest)')
    plt.ylabel('Feature')
    plt.tight_layout()
    plt.savefig('feature_importance.png', dpi=400)
    plt.close()

    # Plotting Prediction vs Actual
    plt.figure(figsize=(8, 8))
    plt.scatter(y_test, y_pred_rf, alpha=0.6, label='Random Forest', c='blue')
    plt.scatter(y_test, y_pred_nn, alpha=0.6, label='Neural Network', c='orange')

    # 1:1 line
    min_val = min(min(y_test), min(y_pred_rf), min(y_pred_nn))
    max_val = max(max(y_test), max(y_pred_rf), max(y_pred_nn))
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Perfect Prediction')

    plt.title('Soil Nitrogen Forecasting: Prediction vs Actual')
    plt.xlabel('Actual Total Nitrogen (umol/L)')
    plt.ylabel('Predicted Total Nitrogen (umol/L)')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig('pred_vs_actual.png', dpi=400)
    plt.close()

    print("Evaluation complete. Visualizations saved as 'feature_importance.png' and 'pred_vs_actual.png'")

if __name__ == "__main__":
    evaluate_models()
