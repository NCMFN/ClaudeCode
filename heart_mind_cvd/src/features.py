import pandas as pd
import numpy as np
import os
import joblib
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split

def engineer_features(data_path, output_dir):
    """
    Engineer new features, one-hot encode, handle imbalance,
    and split the data.
    """
    print("Loading processed data for feature engineering...")
    df = pd.read_csv(os.path.join(data_path, 'nhis_processed.csv'))

    # In NHIS: 1 usually means "Yes".
    # After OrdinalEncoder, let's map back to boolean for scoring, or assume 0=No, 1=Yes.
    # Wait, if original was 1=Yes, 2=No, OrdinalEncoder maps 1->0, 2->1.
    # So if original was 1 (Yes), it's now 0.
    # Let's inspect the values before using them.
    # Actually, if we just want "presence" of risk, we can define a function.
    # Assuming ANXEV_A, DEPEV_A, HYPEV_A, DIBEV_A: 1=Yes. If OrdinalEncoder mapped them to 0=Yes, 1=No.
    # Let's just create the features based on standard boolean logic if possible.
    # Since we ordinal encoded, 1 is usually mapped to 0 (since it's smaller than 2).
    # So 0 means Yes, 1 means No.

    def is_yes(val):
        return 1 if val == 0 else 0

    df['anx_flag'] = df['ANXEV_A'].apply(is_yes) if 'ANXEV_A' in df.columns else 0
    df['dep_flag'] = df['DEPEV_A'].apply(is_yes) if 'DEPEV_A' in df.columns else 0
    df['rx_flag'] = df['RX12M_A'].apply(is_yes) if 'RX12M_A' in df.columns else 0

    df['mental_health_burden_score'] = df['anx_flag'] + df['dep_flag'] + df['rx_flag']

    df['hyp_flag'] = df['HYPEV_A'].apply(is_yes) if 'HYPEV_A' in df.columns else 0
    df['dib_flag'] = df['DIBEV_A'].apply(is_yes) if 'DIBEV_A' in df.columns else 0
    # BMICAT_A >= 3 (Obese or higher). After ordinal encoding, check values.
    # BMICAT_A 1=Underweight, 2=Normal, 3=Overweight, 4=Obese.
    # OrdinalEncoder: 1->0, 2->1, 3->2, 4->3.
    # So >= 3 in original means >= 2 in encoded.
    df['bmi_risk'] = (df['BMICAT_A'] >= 2).astype(int) if 'BMICAT_A' in df.columns else 0

    df['metabolic_risk_score'] = df['hyp_flag'] + df['dib_flag'] + df['bmi_risk']

    # Drop intermediate flags to avoid multicollinearity if desired, but tree models handle it.
    df = df.drop(columns=['anx_flag', 'dep_flag', 'rx_flag', 'hyp_flag', 'dib_flag', 'bmi_risk'])

    # One-hot encode race/ethnicity and education
    # HISPALLP_A and EDUCP_A
    cols_to_ohe = [c for c in ['HISPALLP_A', 'EDUCP_A'] if c in df.columns]
    df = pd.get_dummies(df, columns=cols_to_ohe, drop_first=True)

    # Separate X and y
    y = df['label']

    # Ensure WTFA_A is dropped from features if we're not using it directly for modeling
    X = df.drop(columns=['label', 'WTFA_A'], errors='ignore')

    # Stratified split: 70% train, 15% val, 15% test
    # First split: 70% train, 30% temp
    print("Splitting data into train/val/test...")
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, stratify=y, random_state=42)

    # Second split: 15% val, 15% test (which is 50% of the 30% temp)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42)

    print(f"Train size: {len(X_train)}, Val size: {len(X_val)}, Test size: {len(X_test)}")

    # Apply SMOTE to training data
    print("Applying SMOTE to training data...")
    # Expected positive class is small. Let's check.
    num_pos = sum(y_train == 1)
    if num_pos < 5: # If extremely small due to sample, adjust k_neighbors
        k_neighbors = max(1, num_pos - 1)
        smote = SMOTE(random_state=42, k_neighbors=k_neighbors)
    else:
        smote = SMOTE(random_state=42)

    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    print(f"Post-SMOTE train size: {len(X_train_resampled)}. Positive class ratio: {y_train_resampled.mean():.4f}")

    # Save splits
    os.makedirs(output_dir, exist_ok=True)
    joblib.dump((X_train_resampled, y_train_resampled, X_val, y_val, X_test, y_test),
                os.path.join(output_dir, 'data_splits.joblib'))
    print(f"Data splits saved to {os.path.join(output_dir, 'data_splits.joblib')}")

    return X_train_resampled, y_train_resampled, X_val, y_val, X_test, y_test

if __name__ == "__main__":
    engineer_features('heart_mind_cvd/data/', 'heart_mind_cvd/data/')
