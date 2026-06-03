import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from typing import Tuple
import joblib
import os

def preprocess_data(df: pd.DataFrame, out_dir="results/models") -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series, list]:
    """
    Preprocesses the data:
    - Missing value imputation
    - Outlier removal using IQR
    - Scaling
    - Train/val/test splits
    Returns X_train, X_val, X_test, y_train, y_val, y_test, features_list
    """
    df = df.copy()
    os.makedirs(out_dir, exist_ok=True)

    # Target and features to ignore
    target = 'Detection_Accuracy'
    drop_cols = ['Node_ID', 'Timestamp']

    # 1. Missing Value Imputation
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    numeric_cols = [c for c in numeric_cols if c not in drop_cols and c != target]

    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    if df[target].isnull().sum() > 0:
        df[target] = df[target].fillna(df[target].median())

    # Categorical handling if merged
    if 'Anchor_Status' in df.columns:
        df['Anchor_Status'] = df['Anchor_Status'].fillna(-1)
    if 'Obstacle_Presence' in df.columns:
        df['Obstacle_Presence'] = df['Obstacle_Presence'].fillna(-1)

    # 2. Outlier Removal using IQR on key features
    # 'Residual_Energy', 'Noise_Level', 'Signal_Strength', 'Transmission_Power'
    key_features = ['Residual_Energy', 'Noise_Level', 'Signal_Strength', 'Transmission_Power']
    for col in key_features:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Remove outliers
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]

    # Split into X and y
    X = df.drop(columns=[target] + drop_cols)
    y = df[target]

    features = X.columns.tolist()

    # 3. Train (70), Val (15), Test (15) Splits
    X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    # 15 / 85 = 0.17647 for the validation split from train_val
    X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.17647, random_state=42)

    # 4. Normalize / Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    # Save scaler for later use in simulation
    joblib.dump(scaler, os.path.join(out_dir, 'scaler.pkl'))

    # Convert back to DataFrame for convenience
    X_train = pd.DataFrame(X_train_scaled, columns=features, index=X_train.index)
    X_val = pd.DataFrame(X_val_scaled, columns=features, index=X_val.index)
    X_test = pd.DataFrame(X_test_scaled, columns=features, index=X_test.index)

    return X_train, X_val, X_test, y_train, y_val, y_test, features

if __name__ == "__main__":
    from data_loader import download_data, load_all_datasets
    from feature_engineering import engineer_features
    p_path, w_path, l_path = download_data()
    df = load_all_datasets(p_path, w_path, l_path)
    df = engineer_features(df)

    X_train, X_val, X_test, y_train, y_val, y_test, features = preprocess_data(df)

    print(f"X_train shape: {X_train.shape}")
    print(f"X_val shape: {X_val.shape}")
    print(f"X_test shape: {X_test.shape}")
