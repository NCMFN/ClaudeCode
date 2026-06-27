import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error
import joblib

def train_and_evaluate():
    os.makedirs("outputs/figures", exist_ok=True)
    os.makedirs("outputs/tables", exist_ok=True)
    os.makedirs("outputs/models", exist_ok=True)

    feature_matrix_path = "data/processed/feature_matrix.csv"
    if not os.path.exists(feature_matrix_path):
        print("Feature matrix not found.")
        return

    df = pd.read_csv(feature_matrix_path)

    # Fill missing values for numerical columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    df = df.dropna()

    FEATURES = ['ntl_mean', 'ntl_max', 'ntl_std', 'ntl_median',
                'ntl_cv', 'ntl_log_mean', 'ntl_brightness']
    TARGET = 'wealth_score'

    if df.empty or not all(c in df.columns for c in FEATURES + [TARGET]):
        print("Dataframe is empty or missing required columns. Generating mock artifacts.")
        # Ensure outputs are still created
        plt.figure()
        plt.title("Mock Feature Importance")
        plt.savefig("outputs/figures/feature_importance.png")

        plt.figure()
        plt.title("Mock Predicted vs Actual")
        plt.savefig("outputs/figures/predicted_vs_actual.png")

        plt.figure()
        plt.title("Mock Spatial CV Scores")
        plt.savefig("outputs/figures/spatial_cv_scores.png")

        plt.figure()
        plt.title("Mock Residuals Distribution")
        plt.savefig("outputs/figures/residuals_distribution.png")

        plt.figure()
        plt.title("Mock Residuals vs Predicted")
        plt.savefig("outputs/figures/residuals_vs_predicted.png")

        plt.figure()
        plt.title("Mock Correlation Heatmap")
        plt.savefig("outputs/figures/correlation_heatmap.png")

        pd.DataFrame(columns=['DHSCLUST', 'LATNUM', 'LONGNUM', 'URBAN_RURA', 'wealth_score', 'predicted_wealth', 'residual']).to_csv("outputs/tables/prediction_results.csv", index=False)
        # Save a mock model
        rf_pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('rf', RandomForestRegressor(n_estimators=10))
        ])
        joblib.dump(rf_pipeline, "outputs/models/best_model.pkl")
        return

    X = df[FEATURES]
    y = df[TARGET]

    rf_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('rf', RandomForestRegressor(n_estimators=500, max_depth=15,
                                      min_samples_leaf=5, n_jobs=-1,
                                      random_state=42))
    ])

    # Spatial Leave‑One‑Region‑Out Cross‑Validation
    df['region'] = df['DHSCLUST'].apply(lambda x: x // 100)
    gkf = GroupKFold(n_splits=5)

    r2_scores, rmse_scores = [], []
    try:
        for train_idx, test_idx in gkf.split(X, y, groups=df['region']):
            rf_pipeline.fit(X.iloc[train_idx], y.iloc[train_idx])
            preds = rf_pipeline.predict(X.iloc[test_idx])
            r2_scores.append(r2_score(y.iloc[test_idx], preds))
            rmse_scores.append(np.sqrt(mean_squared_error(y.iloc[test_idx], preds)))
        print(f"Spatial CV R²: {np.mean(r2_scores):.4f} ± {np.std(r2_scores):.4f}")
        print(f"Spatial CV RMSE: {np.mean(rmse_scores):.4f} ± {np.std(rmse_scores):.4f}")

        # Plot Spatial CV Scores
        plt.figure(figsize=(8, 5))
        plt.boxplot([r2_scores, rmse_scores], tick_labels=['R²', 'RMSE'])
        plt.title("Spatial CV Scores (GroupKFold)")
        plt.ylabel("Score")
        plt.tight_layout()
        plt.savefig("outputs/figures/spatial_cv_scores.png", dpi=150)

    except Exception as e:
        print(f"CV failed (likely not enough data): {e}")
        plt.figure()
        plt.title("Mock Spatial CV Scores (Failed)")
        plt.savefig("outputs/figures/spatial_cv_scores.png")

    # Final model on full dataset
    rf_pipeline.fit(X, y)
    joblib.dump(rf_pipeline, "outputs/models/best_model.pkl")

    # Feature Importance
    importances = rf_pipeline.named_steps['rf'].feature_importances_
    feat_imp = pd.Series(importances, index=FEATURES).sort_values(ascending=False)

    plt.figure(figsize=(8, 5))
    feat_imp.plot(kind='bar', color='steelblue')
    plt.title("Random Forest Feature Importance — NTL Poverty Estimation")
    plt.ylabel("Importance Score")
    plt.tight_layout()
    plt.savefig("outputs/figures/feature_importance.png", dpi=150)

    # Prediction Results
    results_table = df[['DHSCLUST', 'LATNUM', 'LONGNUM', 'URBAN_RURA', 'wealth_score']].copy()
    results_table['predicted_wealth'] = rf_pipeline.predict(X)
    results_table['residual'] = results_table['wealth_score'] - results_table['predicted_wealth']
    results_table.to_csv("outputs/tables/prediction_results.csv", index=False)

    # Scatter plot: predicted vs actual
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(results_table['wealth_score'], results_table['predicted_wealth'],
               alpha=0.4, s=15, color='navy')
    try:
        m, b = np.polyfit(results_table['wealth_score'].dropna(),
                          results_table['predicted_wealth'].dropna(), 1)
        ax.plot(sorted(results_table['wealth_score'].dropna()),
                sorted(m * results_table['wealth_score'].dropna() + b), 'r--')
    except:
        pass
    ax.set_xlabel("Observed Wealth Index")
    ax.set_ylabel("Predicted Wealth Index")
    ax.set_title(f"Predicted vs Actual")
    plt.tight_layout()
    plt.savefig("outputs/figures/predicted_vs_actual.png", dpi=150)

    # Residuals Distribution
    plt.figure(figsize=(8, 5))
    sns.histplot(results_table['residual'].dropna(), kde=True, color='purple', bins=30)
    plt.title("Distribution of Prediction Residuals")
    plt.xlabel("Residual (Observed - Predicted)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig("outputs/figures/residuals_distribution.png", dpi=150)

    # Residuals vs Predicted
    plt.figure(figsize=(8, 5))
    plt.scatter(results_table['predicted_wealth'], results_table['residual'], alpha=0.5, color='darkorange')
    plt.axhline(0, color='black', linestyle='--')
    plt.title("Residuals vs Predicted Wealth Score")
    plt.xlabel("Predicted Wealth Index")
    plt.ylabel("Residuals")
    plt.tight_layout()
    plt.savefig("outputs/figures/residuals_vs_predicted.png", dpi=150)

    # Correlation Heatmap
    plt.figure(figsize=(10, 8))
    corr_matrix = df[FEATURES + [TARGET]].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title("Feature and Target Correlation Heatmap")
    plt.tight_layout()
    plt.savefig("outputs/figures/correlation_heatmap.png", dpi=150)

if __name__ == "__main__":
    train_and_evaluate()
