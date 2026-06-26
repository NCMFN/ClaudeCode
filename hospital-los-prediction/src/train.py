import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import shap
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV, train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, RegressorMixin
from xgboost import XGBRegressor

from features import build_preprocessor, get_feature_names

class XGBoostWithEarlyStopping(BaseEstimator, RegressorMixin):
    """
    Custom wrapper to handle internal train/val splitting for XGBoost's early stopping
    without leaking data across CV folds or using static eval_sets in Pipeline/SearchCV.
    """
    def __init__(self, n_estimators=100, max_depth=6, learning_rate=0.1,
                 subsample=1.0, colsample_bytree=1.0, reg_alpha=0, reg_lambda=1,
                 early_stopping_rounds=50, random_state=42, n_jobs=-1, validation_fraction=0.1):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.reg_alpha = reg_alpha
        self.reg_lambda = reg_lambda
        self.early_stopping_rounds = early_stopping_rounds
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.validation_fraction = validation_fraction
        self.model_ = None

    def fit(self, X, y):
        # Split incoming fold data internally to create a valid eval_set
        X_t, X_v, y_t, y_v = train_test_split(
            X, y, test_size=self.validation_fraction, random_state=self.random_state
        )

        self.model_ = XGBRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            subsample=self.subsample,
            colsample_bytree=self.colsample_bytree,
            reg_alpha=self.reg_alpha,
            reg_lambda=self.reg_lambda,
            objective='reg:squarederror',
            random_state=self.random_state,
            n_jobs=self.n_jobs,
            early_stopping_rounds=self.early_stopping_rounds
        )

        self.model_.fit(X_t, y_t, eval_set=[(X_v, y_v)], verbose=False)
        return self

    def predict(self, X):
        return self.model_.predict(X)

    @property
    def feature_importances_(self):
        return self.model_.feature_importances_

def load_data(path: str):
    """
    Load data from a given path and split it into feature and target sets.
    """
    df = pd.read_csv(path)
    X = df.drop(columns=['lengthofstay'])
    y = df['lengthofstay']
    return X, y

def evaluate_model(y_true, y_pred, model_name="Model"):
    """
    Evaluate regression model performance.
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)

    print(f"\n--- {model_name} Results ---")
    print(f"MAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2:   {r2:.4f}")
    print(f"MAPE: {mape:.4f}")

    return {'mae': mae, 'rmse': rmse, 'r2': r2, 'mape': mape}

def plot_actual_vs_predicted(y_true, y_pred, output_path="outputs/actual_vs_predicted.png"):
    """
    Generate and save a scatter plot of Actual vs Predicted LOS values.
    """
    plt.figure(figsize=(10, 6))
    plt.scatter(y_true, y_pred, alpha=0.1, color='blue')
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
    plt.xlabel("Actual LOS (Days)")
    plt.ylabel("Predicted LOS (Days)")
    plt.title("Actual vs Predicted Length of Stay")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_residuals(y_true, y_pred, output_path="outputs/residuals.png"):
    """
    Generate and save a histogram of regression residuals.
    """
    residuals = y_true - y_pred
    plt.figure(figsize=(10, 6))
    sns.histplot(residuals, kde=True, bins=50, color='purple')
    plt.xlabel("Residuals (Actual - Predicted)")
    plt.title("Residual Distribution")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_feature_importance(model, feature_names, output_path="outputs/feature_importance.png"):
    """
    Generate and save a bar chart of native XGBoost feature importances.
    """
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    plt.figure(figsize=(12, 8))
    plt.title("XGBoost Feature Importance")
    plt.bar(range(len(importances)), importances[indices], align="center")
    plt.xticks(range(len(importances)), [feature_names[i] for i in indices], rotation=90)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def generate_shap_plot(model, X_transformed, feature_names, output_path="outputs/shap_summary.png"):
    """
    Generate and save a SHAP summary plot for interpretability.
    """
    X_df = pd.DataFrame(X_transformed, columns=feature_names)
    X_sample = X_df.sample(n=min(5000, len(X_df)), random_state=42)

    explainer = shap.TreeExplainer(model.model_)
    shap_values = explainer.shap_values(X_sample)

    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_sample, show=False, max_display=15)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def proper_training_flow():
    """
    Execute full training lifecycle, including CV tuning, evaluation, and artifact generation.
    """
    X, y = load_data("data/processed_data.csv")

    # Stratification bins for CV splits
    y_bins = pd.qcut(y, q=4, labels=False, duplicates='drop')
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # 1. Evaluate Baseline Model using CV
    print("\nTraining Baseline Linear Regression...")
    lr_pipeline = Pipeline([
        ('preprocessor', build_preprocessor()),
        ('model', LinearRegression())
    ])

    lr_preds = np.zeros_like(y, dtype=float)
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y_bins)):
        lr_pipeline.fit(X.iloc[train_idx], y.iloc[train_idx])
        preds = lr_pipeline.predict(X.iloc[val_idx])
        lr_preds[val_idx] = preds
        print(f"LR Fold {fold+1} MAE: {mean_absolute_error(y.iloc[val_idx], preds):.4f}")
    evaluate_model(y, lr_preds, "Baseline Linear Regression")

    # 2. XGBoost Setup and Hyperparameter Tuning
    print("\nPreparing for XGBoost Hyperparameter Tuning...")

    xgb_wrapper = XGBoostWithEarlyStopping(
        random_state=42, n_jobs=-1, early_stopping_rounds=50
    )

    xgb_pipeline = Pipeline([
        ('preprocessor', build_preprocessor()),
        ('model', xgb_wrapper)
    ])

    param_grid = {
        'model__n_estimators': [300, 500, 700],
        'model__max_depth': [4, 6, 8],
        'model__learning_rate': [0.01, 0.05, 0.1],
        'model__subsample': [0.7, 0.8, 0.9],
        'model__colsample_bytree': [0.8], # Fixed from prompt
        'model__reg_alpha': [0.1],        # Fixed from prompt
        'model__reg_lambda': [1.0]        # Fixed from prompt
    }

    # Perform RandomizedSearchCV on the raw data. The Pipeline guarantees
    # the preprocessor (TargetEncoder) only ever sees the training folds.
    # We use a 20% holdout for the search to run in reasonable time while avoiding leakage
    X_tune, _, y_tune, _ = train_test_split(
        X, y, train_size=0.8, random_state=42, stratify=y_bins
    )

    search = RandomizedSearchCV(
        xgb_pipeline,
        param_distributions=param_grid,
        n_iter=20,
        cv=3,
        scoring='neg_mean_absolute_error',
        random_state=42,
        n_jobs=1,
        verbose=1
    )

    print("\nRunning RandomizedSearchCV with 20 iterations...")
    search.fit(X_tune, y_tune)

    best_params = search.best_params_
    print(f"\nBest Hyperparameters Found: {best_params}")

    # Strip the 'model__' prefix for clean initialization
    best_xgb_params = {k.replace('model__', ''): v for k, v in best_params.items()}

    # 3. XGBoost Cross-Validation Evaluation with Best Params
    print("\nEvaluating Tuned XGBoost Regressor using CV folds...")
    xgb_preds = np.zeros_like(y, dtype=float)

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y_bins)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        # Pipeline per fold to guarantee perfect isolation
        fold_pipeline = Pipeline([
            ('preprocessor', build_preprocessor()),
            ('model', XGBoostWithEarlyStopping(
                **best_xgb_params,
                random_state=42,
                n_jobs=-1,
                early_stopping_rounds=50
            ))
        ])

        fold_pipeline.fit(X_train, y_train)

        preds = fold_pipeline.predict(X_val)
        xgb_preds[val_idx] = preds
        fold_mae = mean_absolute_error(y_val, preds)
        print(f"XGB Fold {fold+1} MAE: {fold_mae:.4f}")

    evaluate_model(y, xgb_preds, "Tuned XGBoost Regressor (CV)")

    # 4. Final Model Training & Export
    print("\nTraining Final XGBoost Model on Full Data...")

    final_pipeline = Pipeline([
        ('preprocessor', build_preprocessor()),
        ('model', XGBoostWithEarlyStopping(
            **best_xgb_params,
            random_state=42,
            n_jobs=-1,
            early_stopping_rounds=50
        ))
    ])

    # Training the final model on 100% of the raw data.
    final_pipeline.fit(X, y)

    # Visualizations
    plot_actual_vs_predicted(y, xgb_preds, "outputs/actual_vs_predicted.png")
    plot_residuals(y, xgb_preds, "outputs/residuals.png")

    # Extract feature names
    dummy_pipeline = Pipeline([('preprocessor', build_preprocessor())])
    dummy_pipeline.fit(X, y)
    feature_names = get_feature_names(dummy_pipeline)

    final_model = final_pipeline.named_steps['model']
    plot_feature_importance(final_model, feature_names, "outputs/feature_importance.png")

    X_trans_full = dummy_pipeline.transform(X)
    generate_shap_plot(final_model, X_trans_full, feature_names, "outputs/shap_summary.png")

    joblib.dump(final_pipeline, "outputs/xgb_los_model.pkl")
    print("Model saved to outputs/xgb_los_model.pkl")
    print("All plots saved to outputs/")

if __name__ == "__main__":
    proper_training_flow()
