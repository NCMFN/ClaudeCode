import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import GroupKFold
import matplotlib.pyplot as plt
import os
import joblib
from typing import Tuple, List, Optional

def train_and_evaluate(features_csv: str, output_model_path: str, output_fig_path: str) -> Optional[Pipeline]:
    """
    Trains a Random Forest Regression model, evaluates it using Spatial GroupKFold CV,
    and plots feature importance.

    Args:
        features_csv (str): Path to the input feature matrix CSV.
        output_model_path (str): Path to save the trained model pipeline.
        output_fig_path (str): Path to save the feature importance figure.

    Returns:
        Optional[Pipeline]: The trained model pipeline, or None if error/missing data.
    """
    if not os.path.exists(features_csv):
        print(f"Feature matrix {features_csv} not found. Skipping model training.")
        return None

    try:
        df = pd.read_csv(features_csv).dropna()
        if df.empty:
            print("Feature matrix is empty after dropping NaNs. Skipping model training.")
            return None

        FEATURES = ['ntl_mean', 'ntl_max', 'ntl_std', 'ntl_median',
                    'ntl_cv', 'ntl_log_mean', 'ntl_brightness']
        TARGET = 'wealth_score'

        # Ensure features exist
        missing_features = [f for f in FEATURES if f not in df.columns]
        if missing_features:
            print(f"Missing features in DataFrame: {missing_features}. Skipping training.")
            return None

        X = df[FEATURES]
        y = df[TARGET]

        rf_pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('rf', RandomForestRegressor(n_estimators=500, max_depth=15,
                                          min_samples_leaf=5, n_jobs=-1,
                                          random_state=42))
        ])

        # Spatial Leave-One-Region-Out Cross-Validation
        df['region'] = df['DHSCLUST'].apply(lambda x: x // 100)

        # Need at least n_splits groups
        n_splits = min(5, df['region'].nunique())

        if n_splits > 1:
            gkf = GroupKFold(n_splits=n_splits)
            r2_scores, rmse_scores = [], []

            for train_idx, test_idx in gkf.split(X, y, groups=df['region']):
                rf_pipeline.fit(X.iloc[train_idx], y.iloc[train_idx])
                preds = rf_pipeline.predict(X.iloc[test_idx])
                r2_scores.append(r2_score(y.iloc[test_idx], preds))
                rmse_scores.append(np.sqrt(mean_squared_error(y.iloc[test_idx], preds)))

            print(f"Spatial CV R²: {np.mean(r2_scores):.4f} ± {np.std(r2_scores):.4f}")
            print(f"Spatial CV RMSE: {np.mean(rmse_scores):.4f} ± {np.std(rmse_scores):.4f}")
        else:
            print("Not enough regions for Spatial GroupKFold CV. Skipping CV.")

        # Final model on full dataset
        rf_pipeline.fit(X, y)

        # Save Model
        os.makedirs(os.path.dirname(output_model_path), exist_ok=True)
        joblib.dump(rf_pipeline, output_model_path)

        # Ensure directories exist
        os.makedirs(os.path.dirname(output_fig_path), exist_ok=True)
        tables_dir = os.path.join(os.path.dirname(os.path.dirname(output_fig_path)), 'tables')
        os.makedirs(tables_dir, exist_ok=True)
        datasets_dir = os.path.join(os.path.dirname(os.path.dirname(output_fig_path)), 'datasets')
        os.makedirs(datasets_dir, exist_ok=True)

        # Feature Importance
        importances = rf_pipeline.named_steps['rf'].feature_importances_
        feat_imp = pd.Series(importances, index=FEATURES).sort_values(ascending=False)

        # Table: Feature Importance
        feat_imp_df = feat_imp.reset_index()
        feat_imp_df.columns = ['Feature', 'Importance']
        feat_imp_df.to_csv(os.path.join(tables_dir, 'table_2_feature_importance.csv'), index=False)
        feat_imp_df.to_csv(os.path.join(datasets_dir, 'feature_importance.csv'), index=False)

        plt.figure(figsize=(8, 5))
        feat_imp.plot(kind='bar', color='steelblue')
        plt.title("Random Forest Feature Importance — NTL Poverty Estimation")
        plt.ylabel("Importance Score")
        plt.tight_layout()
        plt.savefig(output_fig_path, dpi=300, bbox_inches="tight")
        plt.close()

        # Save predictions vs actuals for Phase 7
        results_table = df[['DHSCLUST', 'LATNUM', 'LONGNUM', 'URBAN_RURA', 'wealth_score']].copy()
        results_table['predicted_wealth'] = rf_pipeline.predict(X)
        results_table['residual'] = results_table['wealth_score'] - results_table['predicted_wealth']

        # Dataset: Predictions and Residuals
        results_table.to_csv(os.path.join(datasets_dir, 'predictions.csv'), index=False)
        results_table[['DHSCLUST', 'residual']].to_csv(os.path.join(datasets_dir, 'residuals.csv'), index=False)

        fig, ax = plt.subplots(figsize=(7, 6))
        ax.scatter(results_table['wealth_score'], results_table['predicted_wealth'],
                   alpha=0.4, s=15, color='navy')
        m, b = np.polyfit(results_table['wealth_score'], results_table['predicted_wealth'], 1)
        ax.plot(sorted(results_table['wealth_score']),
                sorted(m * results_table['wealth_score'] + b), 'r--')
        ax.set_xlabel("Observed Wealth Index")
        ax.set_ylabel("Predicted Wealth Index")
        r2_val = r2_score(results_table['wealth_score'], results_table['predicted_wealth'])
        ax.set_title(f"Predicted vs Actual — R² = {r2_val:.3f}")
        plt.tight_layout()
        plt.savefig(os.path.join(os.path.dirname(output_fig_path), 'predicted_vs_actual.png'), dpi=300, bbox_inches="tight")
        plt.close()

        # Table: Model Performance
        rmse_val = np.sqrt(mean_squared_error(results_table['wealth_score'], results_table['predicted_wealth']))
        perf_df = pd.DataFrame({'Metric': ['R-Squared', 'RMSE'], 'Value': [r2_val, rmse_val]})
        perf_df.to_csv(os.path.join(tables_dir, 'table_1_model_performance.csv'), index=False)

        if n_splits > 1:
            fold_results_df = pd.DataFrame({
                'Fold': range(1, len(r2_scores) + 1),
                'R2_Score': r2_scores,
                'RMSE': rmse_scores
            })
            fold_results_df.to_csv(os.path.join(datasets_dir, 'fold_results.csv'), index=False)
            fold_results_df.to_csv(os.path.join(tables_dir, 'table_3_cross_validation_results.csv'), index=False)

        return rf_pipeline

    except Exception as e:
        print(f"Error during model training: {e}")
        return None
