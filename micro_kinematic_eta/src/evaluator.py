import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging
import os
from config import OUTPUTS_FIGURES_DIR, OUTPUTS_RESULTS_DIR, MICRO_KINEMATIC_ZONE_THRESHOLD_KM

class ETAEvaluator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_results = []
        os.makedirs(OUTPUTS_FIGURES_DIR, exist_ok=True)
        os.makedirs(OUTPUTS_RESULTS_DIR, exist_ok=True)

    def _compute_metrics(self, y_true, y_pred, model_name, strata_name):
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        # MAPE where ETA > 1 to avoid div by zero
        mask_mape = y_true > 1
        if mask_mape.sum() > 0:
            mape = np.mean(np.abs((y_true[mask_mape] - y_pred[mask_mape]) / y_true[mask_mape])) * 100
        else:
            mape = np.nan

        errors = np.abs(y_true - y_pred)
        within_1hr = (errors <= 1.0).mean() * 100
        within_3hr = (errors <= 3.0).mean() * 100

        self.metrics_results.append({
            'Model': model_name,
            'Strata': strata_name,
            'RMSE_hrs': rmse,
            'MAE_hrs': mae,
            'R2': r2,
            'MAPE': mape,
            'Within_1hr_pct': within_1hr,
            'Within_3hr_pct': within_3hr
        })

    def evaluate(self, df_test, models_dict):
        # models_dict = {'Linear Regression': lr_preds, 'Random Forest': rf_preds, 'LightGBM': lgbm_preds}
        y_true = df_test['ETA_hours'].values

        # Create strata masks
        mkz_mask = df_test['dist_to_dest_km'] <= MICRO_KINEMATIC_ZONE_THRESHOLD_KM
        outside_mask = ~mkz_mask

        # We need raw VesselType for strata. It might be VesselType or VesselType_enc depending on feature engineer output.
        # Let's assume 'VesselType' is still in df_test.
        if 'VesselType' in df_test.columns:
            vessel_types = df_test['VesselType'].unique()
        else:
            vessel_types = []

        for model_name, preds in models_dict.items():
            self._compute_metrics(y_true, preds, model_name, 'All')

            if mkz_mask.sum() > 0:
                self._compute_metrics(y_true[mkz_mask], preds[mkz_mask], model_name, 'Inside MKZ')
            if outside_mask.sum() > 0:
                self._compute_metrics(y_true[outside_mask], preds[outside_mask], model_name, 'Outside MKZ')

            for vt in vessel_types:
                vt_mask = df_test['VesselType'] == vt
                if vt_mask.sum() > 10:  # Only if enough samples
                    self._compute_metrics(y_true[vt_mask], preds[vt_mask], model_name, f'VesselType: {vt}')

        # Save metrics
        metrics_df = pd.DataFrame(self.metrics_results)
        out_path = os.path.join(OUTPUTS_RESULTS_DIR, 'final_metrics_comparison.csv')
        metrics_df.to_csv(out_path, index=False)
        self.logger.info(f"Saved metrics to {out_path}")

        self._generate_figures(df_test, models_dict, metrics_df)

    def _generate_figures(self, df_test, models_dict, metrics_df):
        lgbm_preds = models_dict.get('LightGBM')
        if lgbm_preds is None:
            self.logger.warning("LightGBM predictions not provided, skipping some figures.")
            return

        y_true = df_test['ETA_hours'].values
        errors = lgbm_preds - y_true
        abs_errors = np.abs(errors)

        df_plot = df_test.copy()
        df_plot['lgbm_preds'] = lgbm_preds
        df_plot['lgbm_error'] = errors
        df_plot['lgbm_abs_error'] = abs_errors

        # 1. comparison_rmse_bar.png
        plt.figure(figsize=(12, 6))
        all_metrics = metrics_df[metrics_df['Strata'] == 'All'].copy()
        if not all_metrics.empty:
            melted = all_metrics.melt(id_vars=['Model'], value_vars=['RMSE_hrs', 'MAE_hrs', 'R2'])
            sns.barplot(data=melted, x='variable', y='value', hue='Model')
            plt.title('Global Model Comparison (All Test Records)')
            plt.savefig(os.path.join(OUTPUTS_FIGURES_DIR, 'comparison_rmse_bar.png'), dpi=300, bbox_inches='tight')
        plt.close()

        # 2. lgbm_predicted_vs_actual.png
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(y_true, lgbm_preds, c=df_plot['dist_to_dest_km'], cmap='viridis', alpha=0.5, s=10)
        plt.colorbar(scatter, label='Distance to Destination (km)')
        plt.plot([0, y_true.max()], [0, y_true.max()], 'r--', linewidth=2)
        plt.xlabel('Actual ETA (hours)')
        plt.ylabel('Predicted ETA (hours)')
        plt.title('LightGBM: Predicted vs Actual ETA')
        plt.savefig(os.path.join(OUTPUTS_FIGURES_DIR, 'lgbm_predicted_vs_actual.png'), dpi=300, bbox_inches='tight')
        plt.close()

        # 3. lgbm_error_by_distance.png
        bins = [0, 10, 25, 50, 100, np.inf]
        labels = ['0-10', '10-25', '25-50', '50-100', '100+']
        df_plot['dist_bin'] = pd.cut(df_plot['dist_to_dest_km'], bins=bins, labels=labels, right=False)

        plt.figure(figsize=(10, 6))
        sns.pointplot(data=df_plot, x='dist_bin', y='lgbm_abs_error')
        plt.axvline(x=2.5, color='red', linestyle='--', alpha=0.5, label='MKZ Boundary (50km)') # between 25-50 and 50-100
        plt.xlabel('Distance to Destination (km)')
        plt.ylabel('Mean Absolute Error (hours)')
        plt.title('Prediction Error vs Distance to Destination')
        plt.legend()
        plt.savefig(os.path.join(OUTPUTS_FIGURES_DIR, 'lgbm_error_by_distance.png'), dpi=300, bbox_inches='tight')
        plt.close()

        # 4. lgbm_residual_histogram.png
        plt.figure(figsize=(10, 6))
        sns.histplot(errors, bins=50)
        plt.axvline(0, color='r', linestyle='--')
        plt.xlabel('Prediction Error (Predicted - Actual) hours')
        plt.title('LightGBM Residual Distribution')
        plt.savefig(os.path.join(OUTPUTS_FIGURES_DIR, 'lgbm_residual_histogram.png'), dpi=300, bbox_inches='tight')
        plt.close()

        # 5. error_by_vessel_type.png
        if 'VesselType' in df_plot.columns:
            plt.figure(figsize=(12, 6))
            sns.boxplot(data=df_plot, x='VesselType', y='lgbm_abs_error')
            plt.xticks(rotation=45)
            plt.ylabel('Absolute Error (hours)')
            plt.title('Prediction Error by Vessel Type')
            plt.savefig(os.path.join(OUTPUTS_FIGURES_DIR, 'error_by_vessel_type.png'), dpi=300, bbox_inches='tight')
            plt.close()
