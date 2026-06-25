import pandas as pd
import numpy as np
import os
import joblib
import shap
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def run_explainability():
    results_df = pd.read_csv("outputs/tables/model_training_summary.csv")
    best_model_name = results_df.sort_values(by='F1_Weighted', ascending=False).iloc[0]['Model']
    best_model = joblib.load(f"outputs/models/{best_model_name}_best.pkl")
    X_test = pd.read_csv("data/synthetic/X_test.csv")
    y_test = pd.read_csv("data/synthetic/y_test.csv")['Performance_Class']

    X_shap = X_test.sample(min(300, len(X_test)), random_state=42)

    if best_model_name in ['RandomForest', 'GradientBoosting', 'XGBoost', 'LightGBM']:
        explainer = shap.TreeExplainer(best_model)
        shap_values = explainer.shap_values(X_shap)
    else:
        background = shap.kmeans(X_test, 100)
        explainer = shap.KernelExplainer(best_model.predict_proba, background)
        shap_values = explainer.shap_values(X_shap)

    os.makedirs("outputs/figures", exist_ok=True)

    if isinstance(shap_values, list):
        plt.figure()
        shap.summary_plot(shap_values, X_shap, plot_type='bar', show=False)
        plt.tight_layout()
        plt.savefig('outputs/figures/fig_20_shap_summary.png')
        plt.close()
        shap_values_class0 = shap_values[0]
    elif len(np.shape(shap_values)) == 3:
        sv_list = [shap_values[:,:,i] for i in range(shap_values.shape[2])]
        plt.figure()
        shap.summary_plot(sv_list, X_shap, plot_type='bar', show=False)
        plt.tight_layout()
        plt.savefig('outputs/figures/fig_20_shap_summary.png')
        plt.close()
        shap_values_class0 = sv_list[0]
    else:
        plt.figure()
        shap.summary_plot(shap_values, X_shap, plot_type='bar', show=False)
        plt.tight_layout()
        plt.savefig('outputs/figures/fig_20_shap_summary.png')
        plt.close()
        shap_values_class0 = shap_values

    if isinstance(shap_values, list): exp_obj = shap.Explanation(values=shap_values[0], data=X_shap, feature_names=X_shap.columns)
    elif len(np.shape(shap_values)) == 3: exp_obj = shap.Explanation(values=shap_values[:,:,0], data=X_shap, feature_names=X_shap.columns)
    else: exp_obj = shap.Explanation(values=shap_values, data=X_shap, feature_names=X_shap.columns)

    plt.figure()
    shap.plots.beeswarm(exp_obj, show=False)
    plt.tight_layout()
    plt.savefig('outputs/figures/fig_21_shap_beeswarm.png')
    plt.close()

    y_shap = y_test.loc[X_shap.index]
    for cls in [0, 1, 2]:
        cls_idx_series = y_shap[y_shap == cls]
        if len(cls_idx_series) > 0:
            idx = cls_idx_series.index[0]
            loc_idx = X_shap.index.get_loc(idx)
            val = shap_values[cls][loc_idx] if isinstance(shap_values, list) else (shap_values[:,:,cls][loc_idx] if len(np.shape(shap_values)) == 3 else shap_values[loc_idx])
            expected = explainer.expected_value[cls] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value
            fp = shap.force_plot(expected, val, X_shap.iloc[loc_idx], show=False)
            shap.save_html(f"outputs/figures/shap_force_class{cls}.html", fp)

    mean_abs_shap = np.mean(np.abs(shap_values_class0), axis=0)
    top_3_features = X_shap.columns[np.argsort(mean_abs_shap)[-3:][::-1]]
    for feat in top_3_features:
        plt.figure()
        shap.dependence_plot(feat, shap_values_class0, X_shap, show=False)
        plt.tight_layout()
        plt.savefig(f'outputs/figures/fig_22_shap_dep_{feat}.png')
        plt.close()

    rf_prescreen = pd.read_csv("outputs/tables/feature_importance_prescreeen.csv").set_index('Feature')['Importance']
    best_gain = pd.Series(best_model.feature_importances_, index=X_shap.columns) if hasattr(best_model, 'feature_importances_') else pd.Series(0, index=X_shap.columns)
    shap_imp = pd.Series(mean_abs_shap, index=X_shap.columns)

    if rf_prescreen.sum() > 0: rf_prescreen /= rf_prescreen.sum()
    if best_gain.sum() > 0: best_gain /= best_gain.sum()
    if shap_imp.sum() > 0: shap_imp /= shap_imp.sum()

    comp_df = pd.DataFrame({'RF_Prescreen': rf_prescreen, f'{best_model_name}_Gain': best_gain, 'SHAP_Mean_Abs': shap_imp}).fillna(0).sort_values(by='SHAP_Mean_Abs', ascending=False).head(10)
    comp_df.plot(kind='bar', figsize=(10, 6), colormap='Set2')
    plt.title('Figure 23: Feature Importance Comparison')
    plt.ylabel('Normalized Importance')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('outputs/figures/fig_23_importance_comparison.png')
    plt.close()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_explainability()
