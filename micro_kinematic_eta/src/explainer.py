import shap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import logging
from config import OUTPUTS_FIGURES_DIR, OUTPUTS_RESULTS_DIR

class LightGBMExplainer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        os.makedirs(OUTPUTS_FIGURES_DIR, exist_ok=True)
        os.makedirs(OUTPUTS_RESULTS_DIR, exist_ok=True)

    def explain_global(self, model, X_test):
        self.logger.info("Generating global SHAP explanations...")

        # Sample for speed if too large
        if len(X_test) > 5000:
            X_sample = X_test.sample(5000, random_state=42)
        else:
            X_sample = X_test

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)

        # 1. shap_summary_beeswarm.png
        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values, X_sample, show=False)
        plt.savefig(os.path.join(OUTPUTS_FIGURES_DIR, 'shap_summary_beeswarm.png'), dpi=300, bbox_inches='tight')
        plt.close()

        # 2. shap_bar_global.png
        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
        plt.savefig(os.path.join(OUTPUTS_FIGURES_DIR, 'shap_bar_global.png'), dpi=300, bbox_inches='tight')
        plt.close()

        # 3. shap_dependence_dist.png
        if 'dist_to_dest_km' in X_sample.columns:
            plt.figure(figsize=(10, 6))
            shap.dependence_plot('dist_to_dest_km', shap_values, X_sample, show=False)
            plt.savefig(os.path.join(OUTPUTS_FIGURES_DIR, 'shap_dependence_dist.png'), dpi=300, bbox_inches='tight')
            plt.close()

        # 4. shap_dependence_sog.png
        if 'SOG_kmh' in X_sample.columns:
            plt.figure(figsize=(10, 6))
            shap.dependence_plot('SOG_kmh', shap_values, X_sample, show=False)
            plt.savefig(os.path.join(OUTPUTS_FIGURES_DIR, 'shap_dependence_sog.png'), dpi=300, bbox_inches='tight')
            plt.close()

        # Save global importance values
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        shap_df = pd.DataFrame({
            'feature': X_sample.columns,
            'mean_abs_shap': mean_abs_shap
        }).sort_values('mean_abs_shap', ascending=False)

        out_path = os.path.join(OUTPUTS_RESULTS_DIR, 'shap_global_importance.csv')
        shap_df.to_csv(out_path, index=False)
        self.logger.info(f"Saved SHAP importance to {out_path}")

    def explain_local(self, model, X_row, feature_names=None):
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_row)

        # Return structured data for JSON API, not waterfall plot file
        # We need the top 3 features and their shap values
        sv = shap_values[0]
        if feature_names is None:
            if isinstance(X_row, pd.DataFrame):
                feature_names = X_row.columns
            else:
                feature_names = [f"f{i}" for i in range(len(sv))]

        # Sort by absolute SHAP value
        indices = np.argsort(np.abs(sv))[::-1]

        top_3 = []
        for i in indices[:3]:
            top_3.append({
                "feature": feature_names[i],
                "shap_value": float(sv[i])
            })

        return top_3
