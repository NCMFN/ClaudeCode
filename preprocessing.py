import pandas as pd
import numpy as np
import logging
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import IsolationForest
import features
from config import COL_MAPPING as CM

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def preprocess_data(df_in, exclude_anomalies=False, output_dir='outputs'):
    os.makedirs(output_dir, exist_ok=True)
    df = df_in.copy()

    # 1. Feature Engineering
    logging.info("Engineering features...")
    df = features.engineer_features(df)

    if CM['target'] not in df.columns:
        raise ValueError(f"Target column '{CM['target']}' not found in dataset.")

    if CM['id'] in df.columns:
        df = df.drop(columns=[CM['id']])

    y = df[CM['target']]
    X = df.drop(columns=[CM['target']])

    # 6. Stratified Split First to avoid data leakage
    logging.info("Splitting dataset (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    train_idx = X_train.index
    test_idx = X_test.index

    numeric_cols = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = X_train.select_dtypes(include=['object', 'category']).columns.tolist()

    # 2. Missing Values Imputation
    logging.info("Imputing missing values...")
    if numeric_cols:
        num_imputer = SimpleImputer(strategy='median')
        X_train_num = pd.DataFrame(num_imputer.fit_transform(X_train[numeric_cols]), columns=numeric_cols, index=train_idx)
        X_test_num = pd.DataFrame(num_imputer.transform(X_test[numeric_cols]), columns=numeric_cols, index=test_idx)
        X_train[numeric_cols] = X_train_num
        X_test[numeric_cols] = X_test_num

    if categorical_cols:
        cat_imputer = SimpleImputer(strategy='most_frequent')
        X_train_cat = pd.DataFrame(cat_imputer.fit_transform(X_train[categorical_cols]), columns=categorical_cols, index=train_idx)
        X_test_cat = pd.DataFrame(cat_imputer.transform(X_test[categorical_cols]), columns=categorical_cols, index=test_idx)
        X_train[categorical_cols] = X_train_cat
        X_test[categorical_cols] = X_test_cat

    # 3. Encoding
    logging.info("Encoding categorical variables...")
    if CM['employment_type'] in categorical_cols:
        le = LabelEncoder()
        le.fit(X_train[CM['employment_type']])
        test_classes = set(X_test[CM['employment_type']])
        for c in test_classes:
            if c not in le.classes_:
                le.classes_ = np.append(le.classes_, c)

        X_train[CM['employment_type']] = le.transform(X_train[CM['employment_type']])
        X_test[CM['employment_type']] = le.transform(X_test[CM['employment_type']])

        categorical_cols.remove(CM['employment_type'])
        numeric_cols.append(CM['employment_type'])

    if CM['interest_rate_tier'] in categorical_cols:
        le_tier = LabelEncoder()
        le_tier.fit(X_train[CM['interest_rate_tier']])
        test_classes = set(X_test[CM['interest_rate_tier']])
        for c in test_classes:
            if c not in le_tier.classes_:
                le_tier.classes_ = np.append(le_tier.classes_, c)

        X_train[CM['interest_rate_tier']] = le_tier.transform(X_train[CM['interest_rate_tier']])
        X_test[CM['interest_rate_tier']] = le_tier.transform(X_test[CM['interest_rate_tier']])

        categorical_cols.remove(CM['interest_rate_tier'])
        numeric_cols.append(CM['interest_rate_tier'])

    if categorical_cols:
        ohe = OneHotEncoder(sparse_output=False, drop='first', handle_unknown='ignore')
        encoded_cats_train = ohe.fit_transform(X_train[categorical_cols])
        encoded_cats_test = ohe.transform(X_test[categorical_cols])
        encoded_cols = ohe.get_feature_names_out(categorical_cols)

        encoded_train_df = pd.DataFrame(encoded_cats_train, columns=encoded_cols, index=train_idx)
        encoded_test_df = pd.DataFrame(encoded_cats_test, columns=encoded_cols, index=test_idx)

        X_train = pd.concat([X_train.drop(columns=categorical_cols), encoded_train_df], axis=1)
        X_test = pd.concat([X_test.drop(columns=categorical_cols), encoded_test_df], axis=1)

    # 4. Scaling
    logging.info("Scaling features...")
    cols_to_scale = [col for col in [CM['income'], CM['loan_amount']] if col in X_train.columns]
    if cols_to_scale:
        scaler = RobustScaler()
        X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train[cols_to_scale]), columns=cols_to_scale, index=train_idx)
        X_test_scaled = pd.DataFrame(scaler.transform(X_test[cols_to_scale]), columns=cols_to_scale, index=test_idx)
        X_train[cols_to_scale] = X_train_scaled
        X_test[cols_to_scale] = X_test_scaled

        for col in cols_to_scale:
            min_val = min(X_train[col].min(), X_test[col].min())
            offset = -min_val + 1e-5 if min_val <= 0 else 0

            X_train[f'{col}_log'] = np.log1p(X_train[col] + offset)
            X_test[f'{col}_log'] = np.log1p(X_test[col] + offset)

            X_train = X_train.drop(columns=[col])
            X_test = X_test.drop(columns=[col])

    # 5. Outlier Detection on Training Set
    logging.info("Detecting outliers...")
    iso = IsolationForest(contamination=0.05, random_state=42)
    preds = iso.fit_predict(X_train)
    anomalies_mask = preds == -1

    anomalies_df = X_train[anomalies_mask].copy()
    anomalies_path = os.path.join(output_dir, 'anomalies.csv')
    anomalies_df.to_csv(anomalies_path, index=False)
    logging.info(f"Found {anomalies_mask.sum()} anomalous rows. Saved to {anomalies_path}")

    if exclude_anomalies:
        logging.info("Dropping anomalies from dataset...")
        X_train = X_train[~anomalies_mask]
        y_train = y_train[~anomalies_mask]

    return X_train, X_test, y_train, y_test
