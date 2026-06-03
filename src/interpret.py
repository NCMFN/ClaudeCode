import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def run_interpretation(model, X_train, out_dir="results/figures"):
    os.makedirs(out_dir, exist_ok=True)

    print("Generating Feature Importance Bar Chart...")
    importances = model.feature_importances_
    features = X_train.columns

    # Sort feature importances in descending order
    indices = np.argsort(importances)[::-1]

    plt.figure(figsize=(10, 8))
    sns.barplot(x=importances[indices], y=[features[i] for i in indices], color='#1F3864')
    plt.title('XGBoost Feature Importances')
    plt.xlabel('Relative Importance')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'feature_importance.png'))
    plt.close()

    print("Computing SHAP values...")
    # Using a sample of X_train to speed up SHAP computation
    X_sample = shap.sample(X_train, 500)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    print("Generating SHAP summary plot...")
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_sample, show=False)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'shap_summary.png'))
    plt.close()

    top_3_indices = indices[:3]
    top_3_features = [features[i] for i in top_3_indices]
    print(f"\nTop 3 most predictive features: {top_3_features}")

    with open(os.path.join(out_dir, 'top_features.txt'), 'w') as f:
        f.write(", ".join(top_3_features))

if __name__ == "__main__":
    from data_loader import download_data, load_primary_dataset
    from feature_engineering import engineer_features
    from preprocessing import preprocess_data

    p_path, _, _ = download_data()
    df = load_primary_dataset(p_path)
    df = engineer_features(df)
    X_train, _, _, _, _, _, _ = preprocess_data(df)

    best_model = joblib.load('results/models/Best_XGBoost.pkl')
    run_interpretation(best_model, X_train)
