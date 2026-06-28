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
