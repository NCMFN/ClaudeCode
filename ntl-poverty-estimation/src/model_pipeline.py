import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error

def train_and_evaluate(df_path="data/processed/feature_matrix.csv"):
    df = pd.read_csv(df_path).dropna()

    FEATURES = ['ntl_mean', 'ntl_max', 'ntl_std', 'ntl_median',
                'ntl_cv', 'ntl_log_mean', 'ntl_brightness']
    TARGET = 'wealth_score'

    X = df[FEATURES]
    y = df[TARGET]

    rf_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('rf', RandomForestRegressor(n_estimators=500, max_depth=15,
                                      min_samples_leaf=5, n_jobs=-1,
                                      random_state=42))
    ])

    # Spatial Leave-One-Region-Out Cross-Validation
    df['region'] = df['DHSCLUST'].apply(lambda x: x // 100)  # Proxy: adjust for actual admin unit
    gkf = GroupKFold(n_splits=5)

    r2_scores, rmse_scores = [], []
    for train_idx, test_idx in gkf.split(X, y, groups=df['region']):
        rf_pipeline.fit(X.iloc[train_idx], y.iloc[train_idx])
        preds = rf_pipeline.predict(X.iloc[test_idx])
        r2_scores.append(r2_score(y.iloc[test_idx], preds))
        rmse_scores.append(np.sqrt(mean_squared_error(y.iloc[test_idx], preds)))

    print(f"Spatial CV R²: {np.mean(r2_scores):.4f} ± {np.std(r2_scores):.4f}")
    print(f"Spatial CV RMSE: {np.mean(rmse_scores):.4f} ± {np.std(rmse_scores):.4f}")

    # Final model on full dataset
    rf_pipeline.fit(X, y)

    # Hyperparameter Tuning (Optional)
    param_grid = {
        'rf__n_estimators': [200, 500, 1000],
        'rf__max_depth': [10, 15, 20, None],
        'rf__min_samples_leaf': [3, 5, 10],
        'rf__max_features': ['sqrt', 'log2', 0.5]
    }

    search = RandomizedSearchCV(rf_pipeline, param_grid, n_iter=30, cv=3,
                                 scoring='r2', n_jobs=-1, random_state=42)
    search.fit(X, y)
    best_model = search.best_estimator_

    # Feature Importance
    importances = best_model.named_steps['rf'].feature_importances_
    feat_imp = pd.Series(importances, index=FEATURES).sort_values(ascending=False)

    plt.figure(figsize=(8, 5))
    feat_imp.plot(kind='bar', color='steelblue')
    plt.title("Random Forest Feature Importance — NTL Poverty Estimation")
    plt.ylabel("Importance Score")
    plt.tight_layout()
    plt.savefig("outputs/figures/feature_importance.png", dpi=150)

    return best_model, df, X
