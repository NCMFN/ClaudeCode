import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_classif
from statsmodels.stats.outliers_influence import variance_inflation_factor
from preprocess import get_train_test_data

def compute_correlation_matrix(X):
    return X.corr()

def compute_vif(X):
    # Add constant or just compute on raw for simplicity in this task
    # Standardizing helps VIF stability
    X_std = (X - X.mean()) / X.std()
    X_std = X_std.fillna(0) # Handle constant features if any

    vif_data = pd.DataFrame()
    vif_data["Feature"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X_std.values, i) for i in range(len(X.columns))]
    return vif_data.sort_values('VIF', ascending=False)

def compute_mutual_information(X, y):
    mi_scores = mutual_info_classif(X, y, random_state=42)
    mi_scores = pd.Series(mi_scores, name="MI Scores", index=X.columns)
    mi_scores = mi_scores.sort_values(ascending=False)
    return mi_scores

if __name__ == '__main__':
    X_train, _, y_train, _ = get_train_test_data()

    print("--- Correlation Matrix ---")
    corr = compute_correlation_matrix(X_train)
    print(corr.head())

    print("\n--- Variance Inflation Factor (VIF) ---")
    vif = compute_vif(X_train)
    print(vif.head(10))

    print("\n--- Mutual Information Scores ---")
    mi_scores = compute_mutual_information(X_train, y_train)
    print(mi_scores.head(10))
