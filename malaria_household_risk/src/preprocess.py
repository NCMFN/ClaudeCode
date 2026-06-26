import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from imblearn.over_sampling import SMOTE
import joblib
import os

CATEGORICAL = ['wall_type', 'roof_type', 'floor_type']
ORDINAL = ['education_head', 'income_level']
BINARY = ['bed_net_available', 'bed_net_used_last_night', 'eave_open']
NUMERICAL = ['proximity_water_body_m', 'household_size', 'num_windows_screened']
TARGET = 'target'

def handle_missing(df):
    for col in CATEGORICAL + ORDINAL + BINARY:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 0)
    for col in NUMERICAL:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median() if pd.notnull(df[col].median()) else 0)
    return df

def fit_and_transform(df, output_dir='outputs/models'):
    df = df.copy()
    df = handle_missing(df)

    if 'proximity_water_body_m' in df.columns:
        df['proximity_water_body_m'] = np.log1p(df['proximity_water_body_m'].astype(float))

    os.makedirs(output_dir, exist_ok=True)

    education_categories = [['None', 'Primary', 'Secondary', 'Tertiary']]
    income_categories = [['Low', 'Middle', 'High']]

    ordinal_enc_edu = OrdinalEncoder(categories=education_categories, handle_unknown='use_encoded_value', unknown_value=-1)
    ordinal_enc_inc = OrdinalEncoder(categories=income_categories, handle_unknown='use_encoded_value', unknown_value=-1)

    df[['education_head']] = ordinal_enc_edu.fit_transform(df[['education_head']])
    df[['income_level']] = ordinal_enc_inc.fit_transform(df[['income_level']])

    ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    cat_encoded = ohe.fit_transform(df[CATEGORICAL])
    cat_cols = ohe.get_feature_names_out(CATEGORICAL)
    df_cat = pd.DataFrame(cat_encoded, columns=cat_cols, index=df.index)

    df = pd.concat([df.drop(CATEGORICAL, axis=1), df_cat], axis=1)

    joblib.dump(ordinal_enc_edu, os.path.join(output_dir, 'ordinal_enc_edu.pkl'))
    joblib.dump(ordinal_enc_inc, os.path.join(output_dir, 'ordinal_enc_inc.pkl'))
    joblib.dump(ohe, os.path.join(output_dir, 'ohe.pkl'))
    joblib.dump(cat_cols, os.path.join(output_dir, 'cat_cols.pkl'))

    return df

def transform_new(df, output_dir='outputs/models'):
    df = df.copy()
    df = handle_missing(df)

    if 'proximity_water_body_m' in df.columns:
        df['proximity_water_body_m'] = np.log1p(df['proximity_water_body_m'].astype(float))

    ordinal_enc_edu = joblib.load(os.path.join(output_dir, 'ordinal_enc_edu.pkl'))
    ordinal_enc_inc = joblib.load(os.path.join(output_dir, 'ordinal_enc_inc.pkl'))
    ohe = joblib.load(os.path.join(output_dir, 'ohe.pkl'))
    cat_cols = joblib.load(os.path.join(output_dir, 'cat_cols.pkl'))

    df[['education_head']] = ordinal_enc_edu.transform(df[['education_head']])
    df[['income_level']] = ordinal_enc_inc.transform(df[['income_level']])

    cat_encoded = ohe.transform(df[CATEGORICAL])
    df_cat = pd.DataFrame(cat_encoded, columns=cat_cols, index=df.index)

    df = pd.concat([df.drop(CATEGORICAL, axis=1), df_cat], axis=1)

    expected_cols = joblib.load(os.path.join(output_dir, 'feature_names.pkl'))
    for col in expected_cols:
        if col not in df.columns:
            df[col] = 0
    return df[expected_cols]

def get_train_test_data(filepath='data/raw/dataset.csv'):
    df = pd.read_csv(filepath)
    df = df.drop_duplicates()

    df_processed = fit_and_transform(df)

    X = df_processed.drop(TARGET, axis=1)
    y = df_processed[TARGET]

    # Save feature names for inference
    joblib.dump(list(X.columns), os.path.join('outputs/models', 'feature_names.pkl'))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    smote = SMOTE(random_state=42)
    X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)

    return X_train_sm, X_test, y_train_sm, y_test

def preprocess_input(input_dict):
    df = pd.DataFrame([input_dict])
    return transform_new(df)

if __name__ == '__main__':
    X_train, X_test, y_train, y_test = get_train_test_data()
    print(f"Train data shape after SMOTE: {X_train.shape}")
    print(f"Test data shape: {X_test.shape}")
