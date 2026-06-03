import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.preprocessing import StandardScaler

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def run_simulation(df: pd.DataFrame, model, scaler: StandardScaler, out_dir="results/"):
    """
    Simulates the Adaptive Power Control (APC) system loop.
    1. Input sample WSN nodes.
    2. Run inference to predict Detection Accuracy.
    3. If predicted accuracy < 75%, increase Transmission Power by 10%.
    4. Re-run prediction and log improvement.
    """
    print("Running Adaptive Power Control (APC) simulation...")

    # We need the original, unscaled dataframe to do the +10% properly.
    # Take the full engineered df, sample 100 rows for simulation.
    sim_df = df.sample(n=100, random_state=42).copy()

    # Features required for prediction
    drop_cols = ['Node_ID', 'Timestamp', 'Detection_Accuracy']
    feature_cols = [c for c in sim_df.columns if c not in drop_cols]

    # Function to get predictions
    def get_preds(data):
        X = data[feature_cols].copy()

        # Fill missing numeric values as done in preprocessing
        for c in X.columns:
            if X[c].isnull().sum() > 0:
                X[c] = X[c].fillna(df[c].median() if c in df.columns else -1)

        X_scaled = scaler.transform(X)
        return model.predict(X_scaled)

    initial_preds = get_preds(sim_df)
    sim_df['Initial_Accuracy_Pred'] = initial_preds

    # Flag for APC
    sim_df['APC_Triggered'] = sim_df['Initial_Accuracy_Pred'] < 75.0

    # Adjust Transmission_Power for flagged nodes
    adjusted_df = sim_df.copy()
    mask = adjusted_df['APC_Triggered']
    adjusted_df.loc[mask, 'Transmission_Power'] = adjusted_df.loc[mask, 'Transmission_Power'] * 1.10

    adjusted_preds = get_preds(adjusted_df)
    sim_df['Adjusted_Accuracy_Pred'] = adjusted_preds

    # Output
    results = sim_df[['Node_ID', 'Initial_Accuracy_Pred', 'APC_Triggered', 'Adjusted_Accuracy_Pred']]
    results.to_csv(os.path.join(out_dir, 'apc_simulation_results.csv'), index=False)
    print("APC Simulation complete. Sample results:")
    print(results.head())

    return results

def run_trend_analysis(df: pd.DataFrame, model, scaler: StandardScaler, out_dir="results/figures"):
    """
    Accuracy Sustainability Trend Analysis
    - Group by Residual Energy buckets
    - Plot mean predicted accuracy vs energy bucket, broken by noise quintile
    """
    print("\nRunning Accuracy Sustainability Trend Analysis...")
    df = df.copy()

    feature_cols = [c for c in df.columns if c not in ['Node_ID', 'Timestamp', 'Detection_Accuracy']]

    X = df[feature_cols].copy()
    for c in X.columns:
        if X[c].isnull().sum() > 0:
            X[c] = X[c].fillna(df[c].median() if c in df.columns else -1)

    X_scaled = scaler.transform(X)
    df['Predicted_Accuracy'] = model.predict(X_scaled)

    # Energy buckets
    bins = [0, 15, 30, 60, 100]
    labels = ['[0-15%]', '[15-30%]', '[30-60%]', '[60-100%]']
    df['Energy_Bucket'] = pd.cut(df['Residual_Energy'], bins=bins, labels=labels, include_lowest=True)

    # Noise quintiles
    df['Noise_Quintile'] = pd.qcut(df['Noise_Level'], 5, labels=['Q1 (Low)', 'Q2', 'Q3', 'Q4', 'Q5 (High)'])

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Energy_Bucket', y='Predicted_Accuracy', hue='Noise_Quintile', marker='o', palette='coolwarm')
    plt.title('Predicted Accuracy vs Residual Energy by Noise Quintile')
    plt.xlabel('Residual Energy Bucket (%)')
    plt.ylabel('Mean Predicted Detection Accuracy (%)')
    plt.legend(title='Noise Quintile')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'accuracy_sustainability_trend.png'))
    plt.close()
    print("Trend analysis plot saved.")

if __name__ == "__main__":
    from data_loader import download_data, load_all_datasets
    from feature_engineering import engineer_features
    from preprocessing import preprocess_data

    p_path, w_path, l_path = download_data()
    df = load_all_datasets(p_path, w_path, l_path)
    df = engineer_features(df)

    scaler = joblib.load('results/models/scaler.pkl')
    best_model = joblib.load('results/models/Best_XGBoost.pkl')

    run_simulation(df, best_model, scaler)
    run_trend_analysis(df, best_model, scaler)
