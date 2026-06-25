import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from scipy.stats.mstats import winsorize

def engineer_features(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'Performance_Class' in numeric_cols: numeric_cols.remove('Performance_Class')

    df = df.dropna(subset=['Performance_Class']).copy()
    for col in numeric_cols:
        if df[col].isna().all(): df[col] = 0

    for col in numeric_cols:
        df[col] = df.groupby('Performance_Class')[col].transform(lambda x: x.fillna(x.median()) if not x.isna().all() else x.fillna(0))
        if df[col].isna().any():
             global_median = df[col].median()
             if pd.isna(global_median): global_median = 0
             df[col] = df[col].fillna(global_median)

    for col in numeric_cols: df[col] = winsorize(df[col], limits=[0.01, 0.01])

    expected = ['Network_Load', 'SNR', 'Collision_Rate', 'Queue_Length', 'Packet_Delivery_Ratio', 'Latency_ms', 'Transmission_Rate', 'Jitter_ms']
    for c in expected:
        if c not in df.columns: df[c] = 0

    df['Load_SNR_Interaction'] = df['Network_Load'] * df['SNR']
    df['Congestion_Index'] = df['Collision_Rate'] * df['Queue_Length']
    df['Efficiency_Ratio'] = df['Packet_Delivery_Ratio'] / (df['Latency_ms'] + 1)
    df['Contention_Pressure'] = df['Network_Load'] / (df['Transmission_Rate'] + 1e-5)
    df['Signal_Quality_Score'] = df['SNR'] / (df['Jitter_ms'] + 1)
    df['Risk_Score'] = df['Collision_Rate'] + (1 - df['Packet_Delivery_Ratio'] / 100)

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'Performance_Class' in numeric_cols: numeric_cols.remove('Performance_Class')

    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    os.makedirs("outputs/models", exist_ok=True)
    joblib.dump(scaler, 'outputs/models/scaler.pkl')

    X = df[numeric_cols].replace([np.inf, -np.inf], np.nan).fillna(0)
    y = df['Performance_Class']

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y)

    feat_imp = pd.DataFrame({'Feature': numeric_cols, 'Importance': rf.feature_importances_}).sort_values(by='Importance', ascending=False)
    os.makedirs("outputs/tables", exist_ok=True)
    feat_imp.head(15).to_csv('outputs/tables/feature_importance_prescreeen.csv', index=False)

    return df

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    df = pd.read_csv("data/processed/merged_raw.csv")
    df = engineer_features(df)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    df = df[numeric_cols]
    df.to_csv("data/processed/features_engineered.csv", index=False)
