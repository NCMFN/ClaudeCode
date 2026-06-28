import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
import joblib
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class NavalPreprocessor:
    def __init__(self):
        os.makedirs(config.MODEL_DIR, exist_ok=True)
        os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
        self.standard_scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
        self.pca = PCA(n_components=0.99)

    def fit_transform_scalers(self, X_train, X_val, X_test):
        X_train_std = pd.DataFrame(self.standard_scaler.fit_transform(X_train), columns=X_train.columns)
        X_val_std = pd.DataFrame(self.standard_scaler.transform(X_val), columns=X_val.columns)
        X_test_std = pd.DataFrame(self.standard_scaler.transform(X_test), columns=X_test.columns)

        joblib.dump(self.standard_scaler, os.path.join(config.MODEL_DIR, 'standard_scaler.pkl'))

        X_train_minmax = pd.DataFrame(self.minmax_scaler.fit_transform(X_train), columns=X_train.columns)
        X_val_minmax = pd.DataFrame(self.minmax_scaler.transform(X_val), columns=X_val.columns)
        X_test_minmax = pd.DataFrame(self.minmax_scaler.transform(X_test), columns=X_test.columns)

        joblib.dump(self.minmax_scaler, os.path.join(config.MODEL_DIR, 'minmax_scaler.pkl'))

        X_train_std.to_csv(os.path.join(config.PROCESSED_DATA_DIR, 'X_train_std.csv'), index=False)
        X_val_std.to_csv(os.path.join(config.PROCESSED_DATA_DIR, 'X_val_std.csv'), index=False)
        X_test_std.to_csv(os.path.join(config.PROCESSED_DATA_DIR, 'X_test_std.csv'), index=False)

        X_train_minmax.to_csv(os.path.join(config.PROCESSED_DATA_DIR, 'X_train_minmax.csv'), index=False)
        X_val_minmax.to_csv(os.path.join(config.PROCESSED_DATA_DIR, 'X_val_minmax.csv'), index=False)
        X_test_minmax.to_csv(os.path.join(config.PROCESSED_DATA_DIR, 'X_test_minmax.csv'), index=False)

        return X_train_std, X_val_std, X_test_std, X_train_minmax, X_val_minmax, X_test_minmax

    def fit_transform_pca(self, X_train_std, X_val_std, X_test_std):
        X_train_pca = self.pca.fit_transform(X_train_std)
        X_val_pca = self.pca.transform(X_val_std)
        X_test_pca = self.pca.transform(X_test_std)

        n_comp = self.pca.n_components_
        joblib.dump(self.pca, os.path.join(config.MODEL_DIR, 'pca_transformer.pkl'))

        pca_cols = [f"PC{i+1}" for i in range(n_comp)]
        X_train_pca_df = pd.DataFrame(X_train_pca, columns=pca_cols)
        X_val_pca_df = pd.DataFrame(X_val_pca, columns=pca_cols)
        X_test_pca_df = pd.DataFrame(X_test_pca, columns=pca_cols)

        X_train_pca_df.to_csv(os.path.join(config.PROCESSED_DATA_DIR, 'X_train_pca.csv'), index=False)
        X_val_pca_df.to_csv(os.path.join(config.PROCESSED_DATA_DIR, 'X_val_pca.csv'), index=False)
        X_test_pca_df.to_csv(os.path.join(config.PROCESSED_DATA_DIR, 'X_test_pca.csv'), index=False)

        return X_train_pca_df, X_val_pca_df, X_test_pca_df

    def flag_outliers(self, X):
        Q1 = X.quantile(0.25)
        Q3 = X.quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR

        outliers_mask = ((X < lower_bound) | (X > upper_bound)).any(axis=1)
        return outliers_mask
