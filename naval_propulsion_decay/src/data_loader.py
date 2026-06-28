import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from sklearn.model_selection import train_test_split

class NavalPropulsionLoader:
    def __init__(self):
        pass

    def load(self, filepath):
        print(f"Loading data from {filepath}...")
        df = pd.read_csv(filepath, sep=r'\s+', header=None)

        columns = config.FEATURE_NAMES + config.TARGET_NAMES
        df.columns = columns

        for col in columns:
            df[col] = df[col].astype('float64')

        return df

    def validate(self, df):
        checks = {
            "shape_correct": df.shape == (11934, 18),
            "no_nan_values": not df.isna().any().any(),
            "kMc_range": df['kMc'].between(0.95, 1.0).all(),
            "kMt_range": df['kMt'].between(0.95, 1.0).all(),
            "v_range": df['v'].between(0, 30).all(),
            "T48_range": df['T48'].between(0, 1200).all(),
        }
        return checks

    def get_splits(self, df):
        X = df[config.FEATURE_NAMES]
        y = df[config.TARGET_NAMES]

        try:
            stratify_col = pd.qcut(df['kMc'], q=5, labels=False)
        except ValueError:
            stratify_col = pd.qcut(df['kMc'], q=5, labels=False, duplicates='drop')

        X_temp, X_test, y_temp, y_test, _, _ = train_test_split(
            X, y, stratify_col, test_size=config.TEST_SIZE, random_state=config.RANDOM_SEED
        )

        val_frac = config.VAL_SIZE / (1 - config.TEST_SIZE)

        try:
            stratify_col_temp = pd.qcut(y_temp['kMc'], q=5, labels=False, duplicates='drop')
        except ValueError:
            stratify_col_temp = None

        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_frac, random_state=config.RANDOM_SEED, stratify=stratify_col_temp
        )

        os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
        X_train.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "X_train.csv"), index=False)
        X_val.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "X_val.csv"), index=False)
        X_test.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "X_test.csv"), index=False)

        y_train.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "y_train.csv"), index=False)
        y_val.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "y_val.csv"), index=False)
        y_test.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "y_test.csv"), index=False)

        return X_train, X_val, X_test, y_train, y_val, y_test
