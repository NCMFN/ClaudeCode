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
    df = pd.read_csv('engineered_features.csv', index_col=0)

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

    # -------------------- Plot 1: Feature Importance --------------------
    print("\nGenerating Plot 1: Feature Importance...")
    importances = rf_model.feature_importances_
    indices = np.argsort(importances)[::-1]

    top_n = 10
    top_features = [feature_names[i] for i in indices[:top_n]]
    top_importances = importances[indices][:top_n]

    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_importances, y=top_features, palette='viridis', hue=top_features, legend=False)
    plt.title('Top 10 Microbial Taxa / Features driving Nitrogen Prediction')
    plt.xlabel('Relative Importance (Random Forest)')
    plt.ylabel('Feature')
    plt.tight_layout()
    plt.savefig('fig1_feature_importance.png', dpi=400)
    plt.close()

    # -------------------- Plot 2: Prediction vs Actual --------------------
    print("Generating Plot 2: Prediction vs Actual...")
    plt.figure(figsize=(8, 8))
    plt.scatter(y_test, y_pred_rf, alpha=0.6, label='Random Forest', c='blue')
    plt.scatter(y_test, y_pred_nn, alpha=0.6, label='Neural Network', c='orange')

    min_val = min(min(y_test), min(y_pred_rf), min(y_pred_nn))
    max_val = max(max(y_test), max(y_pred_rf), max(y_pred_nn))
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Perfect Prediction')

    plt.title('Soil Nitrogen Forecasting: Prediction vs Actual')
    plt.xlabel('Actual Total Nitrogen (umol/L)')
    plt.ylabel('Predicted Total Nitrogen (umol/L)')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig('fig2_pred_vs_actual.png', dpi=400)
    plt.close()

    # -------------------- Plot 3: Residuals Distribution --------------------
    print("Generating Plot 3: Residuals Distribution...")
    residuals_rf = y_test - y_pred_rf
    residuals_nn = y_test - y_pred_nn

    plt.figure(figsize=(10, 6))
    sns.kdeplot(residuals_rf, fill=True, label='Random Forest Residuals', color='blue')
    sns.kdeplot(residuals_nn, fill=True, label='Neural Network Residuals', color='orange')
    plt.axvline(0, color='red', linestyle='--', label='Zero Error')
    plt.title('Distribution of Prediction Errors (Residuals)')
    plt.xlabel('Error (Actual - Predicted)')
    plt.ylabel('Density')
    plt.legend()
    plt.tight_layout()
    plt.savefig('fig3_residuals.png', dpi=400)
    plt.close()

    # -------------------- Plot 4: Model Metrics Comparison --------------------
    print("Generating Plot 4: Model Metrics Comparison...")
    metrics_melted = results_df.melt(id_vars='Model', var_name='Metric', value_name='Score')

    plt.figure(figsize=(10, 6))
    sns.barplot(data=metrics_melted, x='Metric', y='Score', hue='Model', palette='coolwarm')
    plt.title('Comparison of Evaluation Metrics')
    plt.ylabel('Score')
    plt.tight_layout()
    plt.savefig('fig4_metrics.png', dpi=400)
    plt.close()

    # -------------------- Plot 5: Alpha Diversity vs Nitrogen --------------------
    print("Generating Plot 5: Alpha Diversity vs Target...")
    # This assumes 'shannon_entropy' was successfully captured during engineering
    if 'shannon_entropy' in df.columns:
        # Prepare target again since it's an exploration plot across all data
        df['total_nitrogen'] = pd.to_numeric(df['nitrate_umol_per_l'], errors='coerce').fillna(0) + \
                               pd.to_numeric(df['ammonium_umol_per_l'], errors='coerce').fillna(0)
        df_plot = df[df['total_nitrogen'] > 0]

        if len(df_plot) > 0:
            plt.figure(figsize=(10, 6))
            sns.regplot(data=df_plot, x='shannon_entropy', y='total_nitrogen', scatter_kws={'alpha':0.6}, line_kws={'color': 'red'})
            plt.title('Microbial Alpha Diversity (Shannon Entropy) vs Total Soil Nitrogen')
            plt.xlabel('Shannon Entropy')
            plt.ylabel('Total Nitrogen (umol/L)')
            plt.tight_layout()
            plt.savefig('fig5_diversity_vs_nitrogen.png', dpi=400)
            plt.close()
        else:
             print("No valid target data to plot diversity vs nitrogen.")
    else:
        print("Shannon Entropy column not found in dataset.")

    print("Evaluation complete. All 5 visualizations have been saved.")

if __name__ == "__main__":
    evaluate_models()
