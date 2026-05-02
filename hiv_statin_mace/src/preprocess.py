import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import sys
import os

# Add the src directory to path to import scores
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scores import calculate_ascvd_risk, calculate_framingham_risk

def preprocess_data(filepath='../data/processed/synthetic_data.csv'):
    df = pd.read_csv(filepath)

    # Calculate baseline risks before filtering
    df['ASCVD_10yr_risk'] = df.apply(calculate_ascvd_risk, axis=1)
    df['Framingham_10yr_risk'] = df.apply(calculate_framingham_risk, axis=1)

    # Filter to "low-to-moderate" baseline risk: ASCVD_10yr_risk < 10%
    df = df[df['ASCVD_10yr_risk'] < 0.10].copy()

    # Missing value handling: IL-6 and hsCRP
    # Flag and use median imputation with missing indicator column
    for col in ['il6_level', 'hscrp_level']:
        if df[col].isnull().sum() > 0:
            df[f'{col}_missing'] = df[col].isnull().astype(int)
            df[col] = df[col].fillna(df[col].median())

    # Log-transform
    for col in ['il6_level', 'hscrp_level', 'cd4_count_nadir']:
        # adding a small constant to prevent log(0) if any values are exactly 0
        df[col] = np.log1p(df[col])

    # Handle categorical variables for modeling
    categorical_cols = ['smoking_status', 'race']
    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    # Define features and target
    target = 'MACE'

    # Drop columns not used for training
    cols_to_drop = [target, 'is_synthetic', 'ASCVD_10yr_risk', 'Framingham_10yr_risk']

    X = df.drop(columns=[col for col in cols_to_drop if col in df.columns])
    y = df[target]

    # Also save the risks for the test set later
    risks = df[['ASCVD_10yr_risk', 'Framingham_10yr_risk']]

    # Split: 70% train, 15% val, 15% test
    # First split: 70% train, 30% temp (val + test)
    X_train, X_temp, y_train, y_temp, risks_train, risks_temp = train_test_split(
        X, y, risks, test_size=0.3, random_state=42, stratify=y
    )

    # Second split: split temp in half for 15% val, 15% test
    X_val, X_test, y_val, y_test, risks_val, risks_test = train_test_split(
        X_temp, y_temp, risks_temp, test_size=0.5, random_state=42, stratify=y_temp
    )

    # SMOTE oversample minority class on training data only
    smote = SMOTE(random_state=42)
    X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

    return (X_train_smote, y_train_smote), (X_val, y_val), (X_test, y_test, risks_test)

if __name__ == '__main__':
    train, val, test = preprocess_data()
    print(f"Train size (after SMOTE): {train[0].shape}")
    print(f"Val size: {val[0].shape}")
    print(f"Test size: {test[0].shape}")
