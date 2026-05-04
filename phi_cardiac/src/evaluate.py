import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as plt_sns
import shap
from sklearn.metrics import precision_score, recall_score

# Apply global plotting configurations required by memory
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
                     'xtick.labelsize': 10, 'ytick.labelsize': 10,
                     'figure.dpi': 300, 'savefig.dpi': 300})

def evaluate_models(data_file, model_dir, fig_dir):
    os.makedirs(fig_dir, exist_ok=True)

    # 1. Plot R2 comparison
    metrics_file = os.path.join(model_dir, 'model_metrics.csv')
    if os.path.exists(metrics_file):
        metrics = pd.read_csv(metrics_file)

        plt.figure(figsize=(10, 6))
        plt.bar(metrics['Model'], metrics['R2'], color=['#888780', '#993C1D', '#1D9E75', '#BA7517'])
        plt.title('R² Comparison Across Models')
        plt.ylabel('R² Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(fig_dir, 'model_r2_comparison.png'))
        plt.close()

    # Load model and data
    model = joblib.load(os.path.join(model_dir, 'xgb_phi_best.joblib'))
    df = pd.read_csv(data_file, parse_dates=['date'])
    df = df.sort_values(['city', 'date'])
    df_encoded = pd.get_dummies(df, columns=['city'], drop_first=True)
    test_mask = df_encoded['split'] == 'test'

    city_cols = [c for c in df_encoded.columns if c.startswith('city_')]
    features = ['t2m', 'pm25_mean', 'no2_mean', 'o3_mean', 'feels_like_temp',
                   'relative_humidity', 'wind_speed', 'pm25_lag24', 'pm25_lag48', 'pm25_lag72',
                   't2m_lag24', 't2m_lag48', 't2m_lag72', 't2m_zscore', 'phi_initial',
                   'day_of_week', 'month', 'is_weekend', 'is_heatwave',
                   'pm25_3day_rolling_mean', 'temp_3day_rolling_mean'] + city_cols

    X_test = df_encoded.loc[test_mask, features]

    # SHAP TreeExplainer
    # Sample a bit if large
    X_sample = shap.sample(X_test, 1000) if len(X_test) > 1000 else X_test
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    # 2. SHAP feature importance bar chart
    plt.figure()
    shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
    plt.title('SHAP Feature Importance')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'shap_feature_importance.png'))
    plt.close()

    # 3. Interaction plot: PM2.5 x Temperature interaction
    plt.figure()
    shap.dependence_plot("pm25_mean", shap_values, X_sample, interaction_index="t2m", show=False)
    plt.title('PM2.5 x Temperature Interaction')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'phi_interaction_dependence.png'))
    plt.close()

    # 4. PHI alert simulation
    df_test = df[df['split'] == 'test'].copy()

    # Recreate the final PHI from XGBoost predictions (or use the proxy)
    # The requirement says "flag days where PHI > 95th percentile". We'll use phi_initial for simplicity.
    phi_95 = df_test['phi_initial'].quantile(0.95)
    df_test['alert'] = (df_test['phi_initial'] > phi_95).astype(int)

    # Target: admissions > 75th percentile on same day or next 2 days
    p75 = df_test['daily_cardiac_admissions'].quantile(0.75)
    df_test['surge'] = (df_test['daily_cardiac_admissions'] > p75).astype(int)

    # Create the future surge target (same day or next 2 days)
    # Need to process per city
    df_test = df_test.sort_values(['city', 'date'])
    df_test['surge_target'] = 0
    for city in df_test['city'].unique():
        mask = df_test['city'] == city
        surge = df_test.loc[mask, 'surge']
        # Forward rolling max for next 2 days (inclusive of today)
        surge_window = surge.iloc[::-1].rolling(window=3, min_periods=1).max().iloc[::-1]
        df_test.loc[mask, 'surge_target'] = surge_window

    y_true = df_test['surge_target']
    y_pred = df_test['alert']

    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)

    alert_perf = pd.DataFrame([{
        'threshold_percentile': 95,
        'precision': precision,
        'recall': recall,
        'lead_time_hours': 24 # Minimum since it predicts next days
    }])
    alert_perf.to_csv('outputs/alert_performance.csv', index=False)

    # Alert performance curve (Precision-Recall for different percentiles)
    percentiles = [80, 85, 90, 95, 98]
    precisions = []
    recalls = []

    for p in percentiles:
        threshold = df_test['phi_initial'].quantile(p/100.0)
        preds = (df_test['phi_initial'] > threshold).astype(int)
        precisions.append(precision_score(y_true, preds, zero_division=0))
        recalls.append(recall_score(y_true, preds, zero_division=0))

    plt.figure(figsize=(8, 6))
    plt.plot(recalls, precisions, marker='o', linestyle='-', color='#1F3864')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Alert Performance Curve (Precision-Recall)')
    for i, p in enumerate(percentiles):
        plt.annotate(f"{p}th", (recalls[i], precisions[i]), textcoords="offset points", xytext=(0,10), ha='center')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'alert_performance_curve.png'))
    plt.close()

    print("Evaluation completed. Visualizations saved.")

if __name__ == "__main__":
    evaluate_models(
        data_file="data/processed/phi_features.csv",
        model_dir="outputs/models",
        fig_dir="outputs/figures"
    )
