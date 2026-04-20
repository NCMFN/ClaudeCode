import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from imblearn.over_sampling import SMOTE
import os

def preprocess_and_split(df: pd.DataFrame, max_samples_per_class: int = 5000, random_state: int = 42):
    print("Starting preprocessing and splitting...")

    count_cols = ['NUM_LIQUIDITY_ADDS', 'NUM_LIQUIDITY_REMOVES', 'single_event_removal', 'zero_adds_after_remove']
    for col in df.columns:
        if df[col].isnull().any():
            if col in count_cols:
                df[col] = df[col].fillna(0)
            elif pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())

    df = df.dropna(subset=['INACTIVITY_STATUS'])

    X = df.drop(columns=['INACTIVITY_STATUS'])
    y = df['INACTIVITY_STATUS'].astype(int)

    df_majority = df[df.INACTIVITY_STATUS == 0]
    df_minority = df[df.INACTIVITY_STATUS == 1]

    n_majority = min(len(df_majority), max_samples_per_class)
    n_minority = min(len(df_minority), max_samples_per_class)

    df_majority_downsampled = df_majority.sample(n=n_majority, random_state=random_state)
    df_minority_sampled = df_minority.sample(n=n_minority, random_state=random_state)

    df_balanced = pd.concat([df_majority_downsampled, df_minority_sampled])

    X_bal = df_balanced.drop(columns=['INACTIVITY_STATUS'])
    y_bal = df_balanced['INACTIVITY_STATUS'].astype(int)

    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X_bal, y_bal, test_size=0.15, stratify=y_bal, random_state=random_state
    )

    val_size = 0.15 / 0.85
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=val_size, stratify=y_train_val, random_state=random_state
    )

    binary_cols = ['is_short_lived', 'high_remove_ratio', 'single_event_removal', 'zero_adds_after_remove']
    continuous_cols = [c for c in X_train.columns if c not in binary_cols]

    X_train = X_train.replace([np.inf, -np.inf], np.nan).fillna(X_train.median())
    X_val = X_val.replace([np.inf, -np.inf], np.nan).fillna(X_train.median())
    X_test = X_test.replace([np.inf, -np.inf], np.nan).fillna(X_train.median())

    scaler = MinMaxScaler()
    X_train[continuous_cols] = scaler.fit_transform(X_train[continuous_cols])
    X_val[continuous_cols] = scaler.transform(X_val[continuous_cols])
    X_test[continuous_cols] = scaler.transform(X_test[continuous_cols])

    smote = SMOTE(random_state=random_state)
    X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)

    return (X_train, y_train), (X_train_sm, y_train_sm), (X_val, y_val), (X_test, y_test), continuous_cols
