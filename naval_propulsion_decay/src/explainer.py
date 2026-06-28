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
