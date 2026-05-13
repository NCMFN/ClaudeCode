import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE

def handle_missing_values(df):
    if df.empty:
        return df

    # 1. Handle missing values
    df = df.sort_values(['Device_ID', 'Uptime_Cycles'])

    # Thermal_Log: forward-fill within Device_ID group
    if 'Thermal_Log' in df.columns:
        df['Thermal_Log'] = df.groupby('Device_ID')['Thermal_Log'].transform(lambda x: x.ffill().bfill())

    # Workload_Ratio: median imputation
    if 'Workload_Ratio' in df.columns:
        df['Workload_Ratio'] = df['Workload_Ratio'].fillna(df['Workload_Ratio'].median())

    # Uptime_Cycles: linear interpolation
    if 'Uptime_Cycles' in df.columns:
        df['Uptime_Cycles'] = df['Uptime_Cycles'].interpolate(method='linear')

    return df

def detect_outliers_iqr(df, column):
    if df.empty or column not in df.columns:
        return df

    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Cap outliers
    df[column] = np.where(df[column] > upper_bound, upper_bound, df[column])
    df[column] = np.where(df[column] < lower_bound, lower_bound, df[column])
    return df

def preprocess_data(df, is_train=True, smote_random_state=42, scaler=None, label_encoder=None):
    if df.empty:
        return df, scaler, label_encoder

    df = handle_missing_values(df)

    # 2. Encode categorical columns
    if label_encoder is None:
        label_encoder = LabelEncoder()
        df['Device_ID'] = label_encoder.fit_transform(df['Device_ID'].astype(str))
    else:
        # Handle unseen labels gracefully
        df['Device_ID'] = df['Device_ID'].map(lambda s: s if s in label_encoder.classes_ else 'unknown')
        if 'unknown' not in label_encoder.classes_:
            label_encoder.classes_ = np.append(label_encoder.classes_, 'unknown')
        df['Device_ID'] = label_encoder.transform(df['Device_ID'].astype(str))

    # 3. Detect and cap outliers
    df = detect_outliers_iqr(df, 'Thermal_Log')
    df = detect_outliers_iqr(df, 'Workload_Ratio')

    # Split features and target
    target_col = 'Failure_Label'
    if target_col not in df.columns:
        return df, scaler, label_encoder

    X = df.drop(columns=[target_col])
    y = df[target_col]

    if len(np.unique(y)) < 2:
        print("Warning: Target variable has less than 2 classes. Skipping SMOTE.")
    elif is_train:
        # 4. Address CLASS IMBALANCE using SMOTE (only on train)
        smote = SMOTE(random_state=smote_random_state, k_neighbors=min(5, len(X)-1) if len(X) > 1 else 1)
        try:
             X, y = smote.fit_resample(X, y)
        except Exception as e:
             print(f"SMOTE failed, proceeding without it: {e}")

    # 5. Scale numeric features
    numeric_cols = X.select_dtypes(include=[np.number]).columns
    if scaler is None:
        scaler = StandardScaler()
        X[numeric_cols] = scaler.fit_transform(X[numeric_cols])
    else:
        X[numeric_cols] = scaler.transform(X[numeric_cols])

    # Recombine
    processed_df = pd.concat([X.reset_index(drop=True), y.reset_index(drop=True)], axis=1)

    return processed_df, scaler, label_encoder

def run_preprocessing(input_dir='data/processed', output_dir='data/processed'):
    # Find main dataset
    target_file = None
    for filename in os.listdir(input_dir):
        if filename.endswith('.csv') and 'mock_data' in filename:
            target_file = filename
            break

    if target_file is None:
        # Fallback to first csv
        csvs = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
        if not csvs:
            print("No CSV files found for preprocessing.")
            return
        target_file = csvs[0]

    df = pd.read_csv(os.path.join(input_dir, target_file))

    if df.empty:
         print("Dataset is empty. Saving empty parquets.")
         df.to_parquet(os.path.join(output_dir, 'train_split.parquet'), index=False)
         df.to_parquet(os.path.join(output_dir, 'val_split.parquet'), index=False)
         df.to_parquet(os.path.join(output_dir, 'test_split.parquet'), index=False)
         return

    # Chronological Split
    df = df.sort_values('Uptime_Cycles')

    # 70% Train, 15% Val, 15% Test
    train_idx = int(len(df) * 0.7)
    val_idx = int(len(df) * 0.85)

    train_df = df.iloc[:train_idx]
    val_df = df.iloc[train_idx:val_idx]
    test_df = df.iloc[val_idx:]

    # Process
    train_processed, scaler, encoder = preprocess_data(train_df, is_train=True)
    val_processed, _, _ = preprocess_data(val_df, is_train=False, scaler=scaler, label_encoder=encoder)
    test_processed, _, _ = preprocess_data(test_df, is_train=False, scaler=scaler, label_encoder=encoder)

    # Save as parquet
    train_processed.to_parquet(os.path.join(output_dir, 'train_split.parquet'), index=False)
    val_processed.to_parquet(os.path.join(output_dir, 'val_split.parquet'), index=False)
    test_processed.to_parquet(os.path.join(output_dir, 'test_split.parquet'), index=False)

    print("Preprocessing complete. Saved splits to data/processed/")

if __name__ == "__main__":
    run_preprocessing()
