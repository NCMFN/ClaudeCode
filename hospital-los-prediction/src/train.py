import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import shap

from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.base import BaseEstimator, RegressorMixin
import xgboost as xgb

from etl import run_etl
from features import engineer_features, get_preprocessor, save_feature_correlations

np.random.seed(42)

class XGBWrapper(BaseEstimator, RegressorMixin):
    def __init__(self, n_estimators=500, learning_rate=0.05, max_depth=6,
                 subsample=0.8, colsample_bytree=0.8, reg_alpha=0.1, reg_lambda=1.0,
                 objective='reg:squarederror', early_stopping_rounds=50, random_state=42):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.reg_alpha = reg_alpha
        self.reg_lambda = reg_lambda
        self.objective = objective
        self.early_stopping_rounds = early_stopping_rounds
        self.random_state = random_state
        self.model = None
        self._is_fitted = False

    def fit(self, X, y):
        X_arr = np.array(X) if isinstance(X, pd.DataFrame) else X
        y_arr = np.array(y) if isinstance(y, pd.Series) else y

        X_train, X_val, y_train, y_val = train_test_split(
            X_arr, y_arr, test_size=0.2, random_state=self.random_state
        )

        self.model = xgb.XGBRegressor(
            n_estimators=self.n_estimators,
            learning_rate=self.learning_rate,
            max_depth=self.max_depth,
            subsample=self.subsample,
            colsample_bytree=self.colsample_bytree,
            reg_alpha=self.reg_alpha,
            reg_lambda=self.reg_lambda,
            objective=self.objective,
            early_stopping_rounds=self.early_stopping_rounds,
            random_state=self.random_state
        )

        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )

        self._is_fitted = True
        return self

    def predict(self, X):
        return self.model.predict(X)

    def __sklearn_is_fitted__(self):
        return self._is_fitted

def evaluate_metrics(y_true, y_pred, model_name):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)

    return {
        'Model': model_name,
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2,
        'MAPE': mape
    }

def plot_scatter(y_true, y_pred, title, filename):
    os.makedirs(os.path.dirname(f"outputs/figures/{filename}"), exist_ok=True)
    plt.figure(figsize=(8, 6))
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--')
    plt.xlabel('Actual LOS (days)')
    plt.ylabel('Predicted LOS (days)')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"outputs/figures/{filename}")
    plt.close()

def plot_residuals(y_true, y_pred, title, filename):
    os.makedirs(os.path.dirname(f"outputs/figures/{filename}"), exist_ok=True)
    residuals = y_true - y_pred
    plt.figure(figsize=(8, 6))
    sns.histplot(residuals, kde=True)
    plt.xlabel('Residuals (Actual - Predicted)')
    plt.ylabel('Frequency')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"outputs/figures/{filename}")
    plt.close()

def plot_shap(model, X_processed, feature_names, filename):
    os.makedirs(os.path.dirname(f"outputs/figures/{filename}"), exist_ok=True)
    explainer = shap.TreeExplainer(model)
    sample_idx = np.random.choice(X_processed.shape[0], min(1000, X_processed.shape[0]), replace=False)
    shap_values = explainer.shap_values(X_processed[sample_idx])

    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, pd.DataFrame(X_processed[sample_idx], columns=feature_names),
                      max_display=15, show=False)
    plt.tight_layout()
    plt.savefig(f"outputs/figures/{filename}")
    plt.close()

def plot_feature_importance(model, feature_names, filename):
    os.makedirs(os.path.dirname(f"outputs/figures/{filename}"), exist_ok=True)
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    plt.figure(figsize=(10, 8))
    plt.bar(range(len(importances)), importances[indices], align="center")
    plt.xticks(range(len(importances)), [feature_names[i] for i in indices], rotation=90)
    plt.title("Feature Importances")
    plt.tight_layout()
    plt.savefig(f"outputs/figures/{filename}")
    plt.close()

def plot_distribution(y, title, filename):
    os.makedirs(os.path.dirname(f"outputs/figures/{filename}"), exist_ok=True)
    plt.figure(figsize=(8, 6))
    sns.histplot(y, kde=True, bins=20)
    plt.title(title)
    plt.xlabel("Length of Stay (days)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(f"outputs/figures/{filename}")
    plt.close()

def plot_correlation_heatmap(df, filename):
    os.makedirs(os.path.dirname(f"outputs/figures/{filename}"), exist_ok=True)
    plt.figure(figsize=(10, 8))
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Feature Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(f"outputs/figures/{filename}")
    plt.close()

def plot_boxplot(df, x_col, y_col, title, filename):
    os.makedirs(os.path.dirname(f"outputs/figures/{filename}"), exist_ok=True)
    plt.figure(figsize=(8, 6))
    sns.boxplot(x=x_col, y=y_col, data=df)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"outputs/figures/{filename}")
    plt.close()

def main():
    if not os.path.exists("data/LengthOfStay.csv"):
        print("Downloading dataset...")
        import kagglehub
        import shutil
        path = kagglehub.dataset_download("aayushchou/hospital-length-of-stay-dataset-microsoft")
        os.makedirs("data", exist_ok=True)
        for f in os.listdir(path):
            if f.endswith(".csv"):
                shutil.copy(os.path.join(path, f), "data/")

    print("Running ETL...")
    df = run_etl("data/LengthOfStay.csv")

    print("Engineering features...")
    df = engineer_features(df)

    # 5. Exploratory Data Analysis Figures
    print("Generating EDA figures...")
    plot_distribution(df['lengthofstay'], "Length of Stay Distribution", "los_distribution.png")
    plot_correlation_heatmap(df, "correlation_heatmap.png")
    plot_boxplot(df, 'treatment_type', 'lengthofstay', "LOS by Treatment Type", "los_by_treatment_type.png")
    plot_boxplot(df, 'primary_diagnosis', 'lengthofstay', "LOS by Primary Diagnosis", "los_by_primary_diagnosis.png")

    X = df.drop(columns=['lengthofstay', 'Admission date'])
    y = df['lengthofstay']

    save_feature_correlations(X, y, "outputs/tables/feature_correlations.csv")

    y_binned = pd.qcut(y + np.random.normal(0, 1e-6, size=len(y)), q=4, labels=False)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y_binned, random_state=42)

    preprocessor = get_preprocessor()

    print("Training Baseline Model...")
    baseline_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', LinearRegression())
    ])
    baseline_pipeline.fit(X_train, y_train)
    y_pred_base = baseline_pipeline.predict(X_test)
    base_metrics = evaluate_metrics(y_test, y_pred_base, 'Linear Regression Baseline')

    # 6. Baseline Model Figures
    print("Generating Baseline figures...")
    plot_scatter(y_test, y_pred_base, 'Actual vs Predicted LOS (Linear Regression)', 'baseline_scatter.png')
    plot_residuals(y_test, y_pred_base, 'Residuals Distribution (Linear Regression)', 'baseline_residuals.png')

    print("Tuning XGBoost Model...")
    xgb_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', XGBWrapper(random_state=42))
    ])

    param_grid = {
        'model__n_estimators': [300, 500, 700],
        'model__max_depth': [4, 6, 8],
        'model__learning_rate': [0.01, 0.05, 0.1],
        'model__subsample': [0.7, 0.8, 0.9]
    }

    y_train_binned = pd.qcut(y_train + np.random.normal(0, 1e-6, size=len(y_train)), q=4, labels=False)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_splits = list(skf.split(X_train, y_train_binned))

    search = RandomizedSearchCV(
        xgb_pipeline, param_grid, n_iter=20,
        cv=cv_splits,
        scoring='neg_mean_absolute_error',
        n_jobs=-1, random_state=42, verbose=1
    )
    search.fit(X_train, y_train)

    best_pipeline = search.best_estimator_
    print(f"Best XGB Params: {search.best_params_}")

    y_pred_xgb = best_pipeline.predict(X_test)
    xgb_metrics = evaluate_metrics(y_test, y_pred_xgb, 'XGBoost (Tuned)')

    os.makedirs('outputs/tables', exist_ok=True)
    metrics_df = pd.DataFrame([base_metrics, xgb_metrics])
    metrics_df.to_csv("outputs/tables/performance_metrics.csv", index=False)
    print(metrics_df)

    print("Running explicit 5-fold CV for logging MAE...")
    cv_maes = []
    fold = 1
    for train_idx, val_idx in cv_splits:
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

        best_pipeline.fit(X_tr, y_tr)
        preds = best_pipeline.predict(X_val)
        mae = mean_absolute_error(y_val, preds)
        print(f"Fold {fold} MAE: {mae:.4f}")
        cv_maes.append({'Fold': fold, 'MAE': mae})
        fold += 1

    pd.DataFrame(cv_maes).to_csv("outputs/tables/cv_fold_results.csv", index=False)

    print("Generating XGBoost figures...")
    plot_scatter(y_test, y_pred_xgb, 'Actual vs Predicted LOS (XGBoost)', 'xgb_scatter.png')
    plot_residuals(y_test, y_pred_xgb, 'Residuals Distribution (XGBoost)', 'xgb_residuals.png')

    best_pipeline.fit(X_train, y_train)
    X_train_processed = best_pipeline.named_steps['preprocessor'].transform(X_train)

    preprocessor = best_pipeline.named_steps['preprocessor']
    woe_cols = preprocessor.transformers_[0][2]
    ohe = preprocessor.transformers_[1][1]
    ohe_cols = list(ohe.get_feature_names_out(preprocessor.transformers_[1][2]))
    num_cols = preprocessor.transformers_[2][2]

    feature_names = woe_cols + ohe_cols + num_cols

    xgb_model = best_pipeline.named_steps['model'].model

    plot_shap(xgb_model, X_train_processed, feature_names, 'xgb_shap_summary.png')
    plot_feature_importance(xgb_model, feature_names, 'xgb_feature_importance.png')

    print("Saving model artifacts...")
    os.makedirs('outputs', exist_ok=True)
    joblib.dump(best_pipeline, 'outputs/xgb_los_model.pkl')
    joblib.dump(best_pipeline.named_steps['preprocessor'], 'outputs/preprocessor.pkl')

    print("Pipeline Complete.")

if __name__ == "__main__":
    main()
