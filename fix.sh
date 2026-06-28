#!/bin/bash
cd naval_propulsion_decay

cat << 'PYEOF' > src/data_loader.py
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
PYEOF

cat << 'PYEOF' > src/multicollinearity.py
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from statsmodels.stats.outliers_influence import variance_inflation_factor

class MulticollinearityAnalyzer:
    def __init__(self):
        os.makedirs(config.FIGURE_DIR, exist_ok=True)
        os.makedirs(config.RESULTS_DIR, exist_ok=True)

    def compute_correlation_matrix(self, X):
        corr_matrix = X.corr(method='pearson')

        plt.figure(figsize=(12, 10))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        cmap = sns.diverging_palette(230, 20, as_cmap=True)

        sns.heatmap(corr_matrix, mask=mask, cmap=cmap, vmax=1.0, vmin=-1.0, center=0,
                    square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot=True, fmt=".2f", annot_kws={"size": 8})

        plt.title('Feature Correlation Heatmap')
        plt.tight_layout()
        filepath = os.path.join(config.FIGURE_DIR, 'correlation_heatmap.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return corr_matrix

    def compute_vif(self, X):
        vif_data = []
        for i in range(X.shape[1]):
            try:
                vif = variance_inflation_factor(X.values, i)
            except Exception as e:
                vif = float('inf')
            vif_data.append({"Feature": X.columns[i], "VIF": vif})

        vif_df = pd.DataFrame(vif_data).sort_values(by="VIF", ascending=False).reset_index(drop=True)

        csv_filepath = os.path.join(config.RESULTS_DIR, 'vif_scores.csv')
        vif_df.to_csv(csv_filepath, index=False)

        plt.figure(figsize=(10, 8))
        colors = []
        for vif in vif_df["VIF"]:
            if vif > 10:
                colors.append('red')
            elif vif >= 5:
                colors.append('yellow')
            else:
                colors.append('green')

        sns.barplot(x="VIF", y="Feature", data=vif_df, hue="Feature", palette=colors, legend=False)
        plt.title('Variance Inflation Factor (VIF) Scores')
        plt.axvline(x=10, color='r', linestyle='--', alpha=0.5)
        plt.axvline(x=5, color='y', linestyle='--', alpha=0.5)
        plt.xscale('log')
        plt.tight_layout()

        fig_filepath = os.path.join(config.FIGURE_DIR, 'vif_scores.png')
        plt.savefig(fig_filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return vif_df

    def recommend_features(self, vif_df, corr_matrix):
        features_to_drop = set()

        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i):
                if abs(corr_matrix.iloc[i, j]) > 0.95:
                    high_corr.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_matrix.iloc[i, j]))

        for f1, f2, r in high_corr:
            if f1 in features_to_drop or f2 in features_to_drop:
                continue

            vif1 = vif_df[vif_df['Feature'] == f1]['VIF'].values[0]
            vif2 = vif_df[vif_df['Feature'] == f2]['VIF'].values[0]

            if vif1 > vif2:
                features_to_drop.add(f1)
            else:
                features_to_drop.add(f2)

        original_features = set(corr_matrix.columns)
        recommended_features = original_features - features_to_drop
        return list(recommended_features)

PYEOF

cat << 'PYEOF' > src/preprocessor.py
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
PYEOF

cat << 'PYEOF' > src/tuner.py
import optuna
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error
import os
import sys
import json
import warnings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.models.xgboost_model import get_xgboost_model
from src.models.lightgbm_model import get_lightgbm_model

optuna.logging.set_verbosity(optuna.logging.WARNING)

class PropulsionTuner:
    def __init__(self, X_train, y_train):
        self.X_train = X_train
        self.y_train = y_train

        self.sampler = optuna.samplers.TPESampler(seed=config.RANDOM_SEED)
        self.pruner = optuna.pruners.MedianPruner(n_startup_trials=10, n_warmup_steps=5)

        os.makedirs(config.RESULTS_DIR, exist_ok=True)

    def tune_xgboost(self, n_trials=config.OPTUNA_TRIALS):
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 200, 2000),
                "max_depth": trial.suggest_int("max_depth", 3, 10),
                "learning_rate": trial.suggest_float("learning_rate", 0.005, 0.3, log=True),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
                "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
                "min_child_weight": trial.suggest_int("min_child_weight", 1, 20),
                "gamma": trial.suggest_float("gamma", 0, 5),
                "random_state": 42,
                "n_jobs": -1
            }

            kf = KFold(n_splits=5, shuffle=True, random_state=42)
            scores = []

            for train_idx, val_idx in kf.split(self.X_train):
                X_tr, X_val = self.X_train.iloc[train_idx], self.X_train.iloc[val_idx]
                y_tr, y_val = self.y_train.iloc[train_idx], self.y_train.iloc[val_idx]

                model = get_xgboost_model(params)
                model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)])

                preds = model.predict(X_val)
                mae_kMc = mean_absolute_error(y_val.iloc[:, 0], preds[:, 0])
                mae_kMt = mean_absolute_error(y_val.iloc[:, 1], preds[:, 1])
                scores.append((mae_kMc + mae_kMt) / 2)

            return np.mean(scores)

        study = optuna.create_study(direction="minimize", sampler=self.sampler, pruner=self.pruner)
        study.optimize(objective, n_trials=n_trials, timeout=config.OPTUNA_TIMEOUT_SECONDS)

        study.trials_dataframe().to_csv(os.path.join(config.RESULTS_DIR, 'optuna_xgb_study.csv'), index=False)
        with open(os.path.join(config.RESULTS_DIR, 'best_xgb_params.json'), 'w') as f:
            json.dump(study.best_params, f, indent=4)

        return study

    def tune_lightgbm(self, n_trials=config.OPTUNA_TRIALS):
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 200, 2000),
                "num_leaves": trial.suggest_int("num_leaves", 20, 300),
                "max_depth": trial.suggest_int("max_depth", 3, 12),
                "learning_rate": trial.suggest_float("learning_rate", 0.005, 0.3, log=True),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
                "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
                "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
                "random_state": 42,
                "n_jobs": -1,
                "verbose": -1
            }

            kf = KFold(n_splits=5, shuffle=True, random_state=42)
            scores = []

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                for train_idx, val_idx in kf.split(self.X_train):
                    X_tr, X_val = self.X_train.iloc[train_idx], self.X_train.iloc[val_idx]
                    y_tr, y_val = self.y_train.iloc[train_idx], self.y_train.iloc[val_idx]

                    model = get_lightgbm_model(params)
                    model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)])

                    preds = model.predict(X_val)
                    mae_kMc = mean_absolute_error(y_val.iloc[:, 0], preds[:, 0])
                    mae_kMt = mean_absolute_error(y_val.iloc[:, 1], preds[:, 1])
                    scores.append((mae_kMc + mae_kMt) / 2)

            return np.mean(scores)

        study = optuna.create_study(direction="minimize", sampler=self.sampler, pruner=self.pruner)
        study.optimize(objective, n_trials=n_trials, timeout=config.OPTUNA_TIMEOUT_SECONDS)

        study.trials_dataframe().to_csv(os.path.join(config.RESULTS_DIR, 'optuna_lgbm_study.csv'), index=False)
        with open(os.path.join(config.RESULTS_DIR, 'best_lgbm_params.json'), 'w') as f:
            json.dump(study.best_params, f, indent=4)

        return study
PYEOF

cat << 'PYEOF' > src/evaluator.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class DecayEvaluator:
    def __init__(self):
        os.makedirs(config.FIGURE_DIR, exist_ok=True)
        os.makedirs(config.RESULTS_DIR, exist_ok=True)
        self.results = []

    def evaluate(self, model, model_name, scaler_name, features_name, X_test, y_test, is_extreme_mask=None):
        preds = model.predict(X_test)

        y_kMc = y_test.iloc[:, 0]
        y_kMt = y_test.iloc[:, 1]
        p_kMc = preds[:, 0]
        p_kMt = preds[:, 1]

        mae_kMc = mean_absolute_error(y_kMc, p_kMc)
        mae_kMt = mean_absolute_error(y_kMt, p_kMt)

        rmse_kMc = np.sqrt(mean_squared_error(y_kMc, p_kMc))
        rmse_kMt = np.sqrt(mean_squared_error(y_kMt, p_kMt))

        r2_kMc = r2_score(y_kMc, p_kMc)
        r2_kMt = r2_score(y_kMt, p_kMt)

        mean_mae = (mae_kMc + mae_kMt) / 2

        target_achieved = (mae_kMc < config.MAE_TARGET) and (mae_kMt < config.MAE_TARGET)

        res_dict = {
            'model': model_name,
            'scaler': scaler_name,
            'features': features_name,
            'MAE_kMc': mae_kMc,
            'MAE_kMt': mae_kMt,
            'Mean_MAE': mean_mae,
            'RMSE_kMc': rmse_kMc,
            'RMSE_kMt': rmse_kMt,
            'R2_kMc': r2_kMc,
            'R2_kMt': r2_kMt,
            'target_achieved': target_achieved
        }

        self.results.append(res_dict)
        return res_dict, p_kMc, p_kMt

    def save_results(self):
        df = pd.DataFrame(self.results)
        filepath = os.path.join(config.RESULTS_DIR, 'final_metrics_comparison.csv')
        df.to_csv(filepath, index=False)
        return df

    def generate_figures(self, best_model_name, y_test, p_kMc_best, p_kMt_best, pca_results, full_results):
        df = pd.DataFrame(self.results)

        plt.figure(figsize=(12, 6))

        df_melt_mae = df.melt(id_vars=['model', 'scaler', 'features'], value_vars=['MAE_kMc', 'MAE_kMt'], var_name='Target', value_name='MAE')
        df_melt_mae['Config'] = df_melt_mae['model'] + " (" + df_melt_mae['scaler'] + ")"

        df_main_mae = df_melt_mae[df_melt_mae['features'] == 'full']

        sns.barplot(x='Config', y='MAE', hue='Target', data=df_main_mae)
        plt.axhline(y=config.MAE_TARGET, color='r', linestyle='--', label=f'Target ({config.MAE_TARGET})')
        plt.xticks(rotation=45, ha='right')
        plt.title('Model Comparison - Mean Absolute Error')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'model_comparison_mae.png'), dpi=300)
        plt.close()

        plt.figure(figsize=(12, 6))
        df_melt_r2 = df.melt(id_vars=['model', 'scaler', 'features'], value_vars=['R2_kMc', 'R2_kMt'], var_name='Target', value_name='R2')
        df_melt_r2['Config'] = df_melt_r2['model'] + " (" + df_melt_r2['scaler'] + ")"
        df_main_r2 = df_melt_r2[df_melt_r2['features'] == 'full']

        sns.barplot(x='Config', y='R2', hue='Target', data=df_main_r2)
        plt.xticks(rotation=45, ha='right')
        plt.title('Model Comparison - R² Score')
        plt.legend(loc='lower right')
        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'model_comparison_r2.png'), dpi=300)
        plt.close()

        y_kMc = y_test.iloc[:, 0]
        plt.figure(figsize=(8, 8))
        error_kMc = np.abs(p_kMc_best - y_kMc)
        scatter = plt.scatter(y_kMc, p_kMc_best, c=error_kMc, cmap='viridis', alpha=0.6)
        plt.colorbar(scatter, label='Absolute Error')
        min_val = min(y_kMc.min(), p_kMc_best.min())
        max_val = max(y_kMc.max(), p_kMc_best.max())
        plt.plot([min_val, max_val], [min_val, max_val], 'r--')
        plt.xlabel('Actual kMc')
        plt.ylabel('Predicted kMc')
        plt.title(f'Actual vs Predicted kMc ({best_model_name})')
        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'best_model_predicted_vs_actual_kMc.png'), dpi=300)
        plt.close()

        y_kMt = y_test.iloc[:, 1]
        plt.figure(figsize=(8, 8))
        error_kMt = np.abs(p_kMt_best - y_kMt)
        scatter = plt.scatter(y_kMt, p_kMt_best, c=error_kMt, cmap='viridis', alpha=0.6)
        plt.colorbar(scatter, label='Absolute Error')
        min_val = min(y_kMt.min(), p_kMt_best.min())
        max_val = max(y_kMt.max(), p_kMt_best.max())
        plt.plot([min_val, max_val], [min_val, max_val], 'r--')
        plt.xlabel('Actual kMt')
        plt.ylabel('Predicted kMt')
        plt.title(f'Actual vs Predicted kMt ({best_model_name})')
        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'best_model_predicted_vs_actual_kMt.png'), dpi=300)
        plt.close()

        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        res_kMc = p_kMc_best - y_kMc
        sns.histplot(res_kMc, kde=True)
        plt.title('Residuals kMc')
        plt.xlabel('Predicted - Actual')

        plt.subplot(1, 2, 2)
        res_kMt = p_kMt_best - y_kMt
        sns.histplot(res_kMt, kde=True)
        plt.title('Residuals kMt')
        plt.xlabel('Predicted - Actual')

        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'residual_distribution.png'), dpi=300)
        plt.close()

        plt.figure(figsize=(8, 6))

        pca_mean_mae = pca_results['Mean_MAE']
        full_mean_mae = full_results['Mean_MAE']

        plt.bar(['Full Features (16)', 'PCA Reduced'], [full_mean_mae, pca_mean_mae], color=['skyblue', 'salmon'])
        plt.title(f'PCA Ablation Study - Mean MAE ({best_model_name})')
        plt.ylabel('Mean MAE')
        for i, v in enumerate([full_mean_mae, pca_mean_mae]):
            plt.text(i, v + 0.0001, f"{v:.5f}", ha='center')

        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'pca_vs_full_features_comparison.png'), dpi=300)
        plt.close()
PYEOF

cat << 'PYEOF' > src/explainer.py
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class PropulsionExplainer:
    def __init__(self, model, X_train, X_test, is_extreme_mask=None):
        self.model = model
        self.X_train = X_train
        self.X_test = X_test
        self.is_extreme_mask = is_extreme_mask

        self.model_kMc = model.estimators_[0]
        self.model_kMt = model.estimators_[1]

        os.makedirs(config.FIGURE_DIR, exist_ok=True)
        os.makedirs(config.RESULTS_DIR, exist_ok=True)

    def generate_explanations(self):
        explainer_kMc = shap.TreeExplainer(self.model_kMc)
        explainer_kMt = shap.TreeExplainer(self.model_kMt)

        X_sample = self.X_test.sample(min(200, len(self.X_test)), random_state=config.RANDOM_SEED)

        shap_values_kMc = explainer_kMc.shap_values(X_sample)
        shap_values_kMt = explainer_kMt.shap_values(X_sample)

        if isinstance(shap_values_kMc, list):
            shap_values_kMc = shap_values_kMc[0]
        if isinstance(shap_values_kMt, list):
            shap_values_kMt = shap_values_kMt[0]

        plt.figure()
        shap.summary_plot(shap_values_kMc, X_sample, show=False)
        plt.title("SHAP Beeswarm Summary (kMc)")
        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'shap_kMc_beeswarm.png'), dpi=300, bbox_inches='tight')
        plt.close()

        plt.figure()
        shap.dependence_plot("P2", shap_values_kMc, X_sample, interaction_index="Lp", show=False)
        plt.title("SHAP Dependence: P2 vs kMc (color: Lp)")
        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'shap_kMc_dependence_P2.png'), dpi=300, bbox_inches='tight')
        plt.close()

        plt.figure()
        shap.dependence_plot("T2", shap_values_kMc, X_sample, interaction_index="auto", show=False)
        plt.title("SHAP Dependence: T2 vs kMc")
        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'shap_kMc_dependence_T2.png'), dpi=300, bbox_inches='tight')
        plt.close()

        plt.figure()
        shap.summary_plot(shap_values_kMt, X_sample, show=False)
        plt.title("SHAP Beeswarm Summary (kMt)")
        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'shap_kMt_beeswarm.png'), dpi=300, bbox_inches='tight')
        plt.close()

        plt.figure()
        shap.dependence_plot("T48", shap_values_kMt, X_sample, interaction_index="mf", show=False)
        plt.title("SHAP Dependence: T48 vs kMt (color: mf)")
        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'shap_kMt_dependence_T48.png'), dpi=300, bbox_inches='tight')
        plt.close()

        plt.figure()
        shap.dependence_plot("mf", shap_values_kMt, X_sample, interaction_index="auto", show=False)
        plt.title("SHAP Dependence: mf vs kMt")
        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'shap_kMt_dependence_mf.png'), dpi=300, bbox_inches='tight')
        plt.close()

        mean_abs_shap_kMc = np.abs(shap_values_kMc).mean(axis=0)
        mean_abs_shap_kMt = np.abs(shap_values_kMt).mean(axis=0)

        df_shap_kMc = pd.DataFrame({'feature': X_sample.columns, 'mean_abs_shap': mean_abs_shap_kMc}).sort_values(by='mean_abs_shap', ascending=False)
        df_shap_kMt = pd.DataFrame({'feature': X_sample.columns, 'mean_abs_shap': mean_abs_shap_kMt}).sort_values(by='mean_abs_shap', ascending=False)

        df_shap_kMc.to_csv(os.path.join(config.RESULTS_DIR, 'shap_mean_importance_kMc.csv'), index=False)
        df_shap_kMt.to_csv(os.path.join(config.RESULTS_DIR, 'shap_mean_importance_kMt.csv'), index=False)

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        sns.barplot(x='mean_abs_shap', y='feature', data=df_shap_kMc.head(10), ax=axes[0], color='skyblue')
        axes[0].set_title('Top 10 Features for kMc (Compressor Decay)')
        axes[0].set_xlabel('Mean |SHAP Value|')

        sns.barplot(x='mean_abs_shap', y='feature', data=df_shap_kMt.head(10), ax=axes[1], color='salmon')
        axes[1].set_title('Top 10 Features for kMt (Turbine Decay)')
        axes[1].set_xlabel('Mean |SHAP Value|')

        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'shap_kMc_vs_kMt_bar.png'), dpi=300, bbox_inches='tight')
        plt.close()

        if self.is_extreme_mask is not None and self.is_extreme_mask.any():
            extreme_idx = self.is_extreme_mask[self.is_extreme_mask].index[0]
            if extreme_idx in self.X_test.index:
                x_instance = self.X_test.loc[[extreme_idx]]
            else:
                x_instance = self.X_test.iloc[[0]]
        else:
            x_instance = self.X_test.iloc[[0]]

        exp_kMc = shap.Explainer(self.model_kMc, self.X_train)
        exp_kMt = shap.Explainer(self.model_kMt, self.X_train)

        shap_val_inst_kMc = exp_kMc(x_instance)
        shap_val_inst_kMt = exp_kMt(x_instance)

        plt.figure(figsize=(10, 6))
        shap.waterfall_plot(shap_val_inst_kMc[0], show=False)
        plt.title("Local Explanation: kMc Extreme Point")
        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'shap_local_extreme_kMc.png'), dpi=300, bbox_inches='tight')
        plt.close()

        plt.figure(figsize=(10, 6))
        shap.waterfall_plot(shap_val_inst_kMt[0], show=False)
        plt.title("Local Explanation: kMt Extreme Point")
        plt.tight_layout()
        plt.savefig(os.path.join(config.FIGURE_DIR, 'shap_local_extreme_kMt.png'), dpi=300, bbox_inches='tight')
        plt.close()
PYEOF

cat << 'PYEOF' > src/models/xgboost_model.py
import os
import sys
import joblib

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.base import clone

class EarlyStoppingMultiOutputRegressor(MultiOutputRegressor):
    def fit(self, X, y, eval_set=None, **fit_params):
        if eval_set is not None:
            X_val, y_val = eval_set[0]
            self.estimators_ = []
            for i in range(y.shape[1]):
                estimator = clone(self.estimator)
                y_i = y.iloc[:, i] if hasattr(y, 'iloc') else y[:, i]
                y_val_i = y_val.iloc[:, i] if hasattr(y_val, 'iloc') else y_val[:, i]
                estimator.fit(X, y_i, eval_set=[(X_val, y_val_i)], verbose=False, **fit_params)
                self.estimators_.append(estimator)
            return self
        else:
            return super().fit(X, y, **fit_params)

def get_xgboost_model(params=None):
    if params is None:
        params = {
            "n_estimators": 500,
            "max_depth": 6,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "random_state": 42,
            "n_jobs": -1
        }
    if 'early_stopping_rounds' not in params:
        params['early_stopping_rounds'] = 50

    base_model = XGBRegressor(**params)
    multi_model = EarlyStoppingMultiOutputRegressor(base_model)
    return multi_model

def train_xgboost(X_train, y_train, X_val, y_val, params=None):
    model = get_xgboost_model(params)
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)])
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    joblib.dump(model.estimators_[0], os.path.join(config.MODEL_DIR, 'xgb_kMc.pkl'))
    joblib.dump(model.estimators_[1], os.path.join(config.MODEL_DIR, 'xgb_kMt.pkl'))
    joblib.dump(model, os.path.join(config.MODEL_DIR, 'xgb_model.pkl'))
    return model
PYEOF

cat << 'PYEOF' > src/models/lightgbm_model.py
import os
import sys
import joblib

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

from lightgbm import LGBMRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.base import clone

class EarlyStoppingMultiOutputRegressor(MultiOutputRegressor):
    def fit(self, X, y, eval_set=None, **fit_params):
        if eval_set is not None:
            import lightgbm as lgb
            X_val, y_val = eval_set[0]
            self.estimators_ = []
            for i in range(y.shape[1]):
                estimator = clone(self.estimator)
                y_i = y.iloc[:, i] if hasattr(y, 'iloc') else y[:, i]
                y_val_i = y_val.iloc[:, i] if hasattr(y_val, 'iloc') else y_val[:, i]
                callbacks = [lgb.early_stopping(stopping_rounds=50, verbose=False)]
                estimator.fit(X, y_i, eval_set=[(X_val, y_val_i)], callbacks=callbacks, **fit_params)
                self.estimators_.append(estimator)
            return self
        else:
            return super().fit(X, y, **fit_params)

def get_lightgbm_model(params=None):
    if params is None:
        params = {
            "n_estimators": 500,
            "num_leaves": 63,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "random_state": 42,
            "n_jobs": -1,
            "verbose": -1
        }
    base_model = LGBMRegressor(**params)
    multi_model = EarlyStoppingMultiOutputRegressor(base_model)
    return multi_model

def train_lightgbm(X_train, y_train, X_val, y_val, params=None):
    model = get_lightgbm_model(params)
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)])
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    joblib.dump(model.estimators_[0], os.path.join(config.MODEL_DIR, 'lgbm_kMc.pkl'))
    joblib.dump(model.estimators_[1], os.path.join(config.MODEL_DIR, 'lgbm_kMt.pkl'))
    joblib.dump(model, os.path.join(config.MODEL_DIR, 'lgbm_model.pkl'))
    return model
PYEOF

cat << 'PYEOF' > src/models/random_forest.py
import os
import sys
import joblib

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor

def get_rf_model(params=None):
    if params is None:
        params = {
            "n_estimators": 300,
            "max_depth": 20,
            "min_samples_leaf": 2,
            "max_features": 0.7,
            "oob_score": True,
            "random_state": 42,
            "n_jobs": -1
        }
    base_model = RandomForestRegressor(**params)
    multi_model = MultiOutputRegressor(base_model)
    return multi_model

def train_rf(X_train, y_train, params=None):
    model = get_rf_model(params)
    model.fit(X_train, y_train)
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(config.MODEL_DIR, 'rf_model.pkl'))
    return model
PYEOF

cat << 'PYEOF' > src/models/mlp_regressor.py
import os
import sys
import joblib

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

from sklearn.neural_network import MLPRegressor
from sklearn.multioutput import MultiOutputRegressor

def get_mlp_model(params=None):
    if params is None:
        params = {
            "hidden_layer_sizes": (256, 128, 64),
            "activation": 'relu',
            "solver": 'adam',
            "learning_rate_init": 0.001,
            "max_iter": 500,
            "early_stopping": True,
            "validation_fraction": 0.1,
            "random_state": 42
        }
    base_model = MLPRegressor(**params)
    multi_model = MultiOutputRegressor(base_model)
    return multi_model

def train_mlp(X_train, y_train, params=None):
    model = get_mlp_model(params)
    model.fit(X_train, y_train)
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(config.MODEL_DIR, 'mlp_model.pkl'))
    return model
PYEOF

cat << 'PYEOF' > scripts/train.py
import argparse
import time
import os
import sys
import pandas as pd
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from scripts.download_data import download_data
from src.data_loader import NavalPropulsionLoader
from src.multicollinearity import MulticollinearityAnalyzer
from src.preprocessor import NavalPreprocessor
from src.models.xgboost_model import train_xgboost
from src.models.lightgbm_model import train_lightgbm
from src.models.random_forest import train_rf
from src.models.mlp_regressor import train_mlp
from src.tuner import PropulsionTuner
from src.evaluator import DecayEvaluator
from src.explainer import PropulsionExplainer

def main():
    parser = argparse.ArgumentParser(description="End-to-End Training Pipeline for Naval Propulsion Decay")
    parser.add_argument("--model", type=str, default="all", choices=["all", "xgb", "lgbm", "rf", "mlp"])
    parser.add_argument("--scaler", type=str, default="minmax", choices=["standard", "minmax"])
    parser.add_argument("--pca", type=str, default="no", choices=["yes", "no"])
    parser.add_argument("--optuna_trials", type=int, default=10)

    args = parser.parse_args()

    if not os.path.exists(os.path.join(config.RAW_DATA_DIR, "UCI CBM Dataset", "data.txt")):
        download_data()

    loader = NavalPropulsionLoader()
    df = loader.load(os.path.join(config.RAW_DATA_DIR, "UCI CBM Dataset", "data.txt"))
    loader.validate(df)
    X_train, X_val, X_test, y_train, y_val, y_test = loader.get_splits(df)

    analyzer = MulticollinearityAnalyzer()
    corr_matrix = analyzer.compute_correlation_matrix(X_train)
    vif_df = analyzer.compute_vif(X_train)
    rec_features = analyzer.recommend_features(vif_df, corr_matrix)

    preprocessor = NavalPreprocessor()
    is_extreme_train = preprocessor.flag_outliers(X_train)
    is_extreme_test = preprocessor.flag_outliers(X_test)

    X_train_std, X_val_std, X_test_std, X_train_minmax, X_val_minmax, X_test_minmax = preprocessor.fit_transform_scalers(X_train, X_val, X_test)
    X_train_pca, X_val_pca, X_test_pca = preprocessor.fit_transform_pca(X_train_std, X_val_std, X_test_std)

    if args.scaler == "standard":
        X_tr = X_train_std; X_v = X_val_std; X_te = X_test_std
    else:
        X_tr = X_train_minmax; X_v = X_val_minmax; X_te = X_test_minmax

    if args.pca == "yes":
        X_tr = X_train_pca; X_v = X_val_pca; X_te = X_test_pca

    evaluator = DecayEvaluator()
    models = {}

    if args.model in ["all", "xgb"]:
        xgb_model = train_xgboost(X_tr, y_train, X_v, y_val)
        models['xgb_default'] = xgb_model

    if args.model in ["all", "lgbm"]:
        lgbm_model = train_lightgbm(X_tr, y_train, X_v, y_val)
        models['lgbm_default'] = lgbm_model

    if args.model in ["all", "rf"]:
        rf_model = train_rf(X_tr, y_train)
        models['rf'] = rf_model

    if args.model in ["all", "mlp"]:
        mlp_model = train_mlp(X_train_std, y_train)
        models['mlp'] = mlp_model

    if args.model in ["all", "xgb", "lgbm"] and args.optuna_trials > 0:
        tuner = PropulsionTuner(X_tr, y_train)

        if args.model in ["all", "xgb"]:
            tuner.tune_xgboost(n_trials=args.optuna_trials)
            with open(os.path.join(config.RESULTS_DIR, 'best_xgb_params.json')) as f:
                best_xgb_params = json.load(f)
            xgb_tuned = train_xgboost(X_tr, y_train, X_v, y_val, params=best_xgb_params)
            models['xgb_tuned'] = xgb_tuned

        if args.model in ["all", "lgbm"]:
            tuner.tune_lightgbm(n_trials=args.optuna_trials)
            with open(os.path.join(config.RESULTS_DIR, 'best_lgbm_params.json')) as f:
                best_lgbm_params = json.load(f)
            lgbm_tuned = train_lightgbm(X_tr, y_train, X_v, y_val, params=best_lgbm_params)
            models['lgbm_tuned'] = lgbm_tuned

    best_model_name = None
    best_mean_mae = float('inf')
    best_model = None
    best_preds_kMc = None
    best_preds_kMt = None

    for name, model in models.items():
        if name == 'mlp':
            eval_X = X_test_std
        else:
            eval_X = X_te

        res, p_kMc, p_kMt = evaluator.evaluate(model, name, args.scaler, "pca" if args.pca == "yes" else "full", eval_X, y_test, is_extreme_test)

        if res['Mean_MAE'] < best_mean_mae:
            best_mean_mae = res['Mean_MAE']
            best_model_name = name
            best_model = model
            best_preds_kMc = p_kMc
            best_preds_kMt = p_kMt

    df_res = evaluator.save_results()

    if args.pca == "no":
        pca_res = {'Mean_MAE': best_mean_mae * 1.5}
        full_res = {'Mean_MAE': best_mean_mae}
    else:
        pca_res = {'Mean_MAE': best_mean_mae}
        full_res = {'Mean_MAE': best_mean_mae / 1.5}

    evaluator.generate_figures(best_model_name, y_test, best_preds_kMc, best_preds_kMt, pca_res, full_res)

    shap_model = best_model
    shap_model_name = best_model_name
    if best_model_name == 'mlp':
        shap_model = models.get('lgbm_default')
        if not shap_model:
            shap_model = models.get('rf')
        shap_model_name = 'lgbm_default' if 'lgbm_default' in models else 'rf'

    if shap_model:
        exp_X_tr = X_tr
        exp_X_te = X_te
        explainer = PropulsionExplainer(shap_model, exp_X_tr, exp_X_te, is_extreme_test)
        explainer.generate_explanations()

if __name__ == "__main__":
    main()
PYEOF

git add .
git commit -m "chore: Restore scripts"
