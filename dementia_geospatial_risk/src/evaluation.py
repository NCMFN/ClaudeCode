import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import shap
import joblib

# Use memory instructions for Matplotlib standard settings:
# "For uniform matplotlib figure styling (especially in Colab environments), use standard rcParams: {'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300} to ensure crisp text and high-resolution outputs."
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
                     'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

DATA_DIR = Path("dementia_geospatial_risk/data")
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = Path("dementia_geospatial_risk/outputs")
MODELS_DIR = OUTPUTS_DIR / "models"
FIG_DIR = OUTPUTS_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

def plot_confusion_matrices():
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    models = ['XGBoost', 'Random Forest', 'SVM']

    for i, model in enumerate(models):
        cm_path = MODELS_DIR / f"{model}_cm.npy"
        if not cm_path.exists():
            continue
        cm = np.load(cm_path)

        # Row-normalize as per memory: "When plotting normalized confusion matrices for ML evaluation, ensure they are row-normalized (true labels) using cm.sum(axis=1, keepdims=True) so that values sum to 1.0 per row"
        cm_norm = cm.astype('float') / cm.sum(axis=1, keepdims=True)

        sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues', ax=axes[i], vmin=0, vmax=1)
        axes[i].set_title(f'{model} Normalized CM')
        axes[i].set_xlabel('Predicted Label')
        axes[i].set_ylabel('True Label')

    plt.tight_layout()
    plt.savefig(FIG_DIR / "Figure_6_confusion_matrices.png")
    plt.close()

def shap_analysis():
    df = pd.read_csv(PROCESSED_DIR / "model_ready_data.csv", dtype={'FIPS': str})

    drop_cols = ['FIPS', 'GEOID', 'NAME', 'STATEFP', 'latitude', 'longitude', 'pm25_mean', '_STATE', 'scd_prevalence', 'state_fips']
    X = df.drop(columns=[c for c in drop_cols if c in df.columns] + ['target_risk_class'])

    model_path = MODELS_DIR / "best_XGBoost_model.pkl"
    if not model_path.exists():
        print("XGBoost model not found.")
        return

    pipeline = joblib.load(model_path)
    # The pipeline has ['smote', 'clf']. SHAP requires the model directly, not pipeline
    best_xgb = pipeline.named_steps['clf']

    # We explain on the raw features (X) to understand global behavior
    # Note: SHAP explainers for multi-class XGBoost will output list of shap values
    explainer = shap.TreeExplainer(best_xgb)
    shap_values = explainer.shap_values(X)

    # Depending on xgboost version, shap_values might be a single 3D array or list of 2D arrays
    # If list, let's take the mean absolute over all classes or just the highest risk class (index 2)
    if isinstance(shap_values, list):
        shap_values_class2 = shap_values[2] # High risk class
    elif shap_values.ndim == 3:
        shap_values_class2 = shap_values[:, :, 2]
    else:
        shap_values_class2 = shap_values

    # Figure 7 - SHAP Summary Plot
    plt.figure()
    shap.summary_plot(shap_values_class2, X, show=False)
    plt.savefig(FIG_DIR / "Figure_7.png", bbox_inches='tight')
    plt.close()

    # Figure 8 - SHAP Bar Plot
    plt.figure()
    shap.summary_plot(shap_values_class2, X, plot_type='bar', show=False)
    plt.savefig(FIG_DIR / "Figure_8.png", bbox_inches='tight')
    plt.close()

    # Figure 9 - SHAP Dependence Plot
    plt.figure()
    if 'pollution_cumulative_load' in X.columns and 'solar_exposure_index' in X.columns:
        shap.dependence_plot('pollution_cumulative_load', shap_values_class2, X, interaction_index='solar_exposure_index', show=False)
        plt.savefig(FIG_DIR / "Figure_9.png", bbox_inches='tight')
    plt.close()

    # Figure 10 - Force plot for one High and one Low risk
    # We will pick indices where y=0 and y=2
    y = df['target_risk_class']
    idx_high = y[y==2].index[0] if len(y[y==2]) > 0 else 0
    idx_low = y[y==0].index[0] if len(y[y==0]) > 0 else 1

    # We cannot save javascript force plots easily to static PNG via shap directly without matplotlib fallback or HTML.
    # But shap.force_plot supports matplotlib=True

    shap.force_plot(explainer.expected_value[2] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value,
                    shap_values_class2[idx_high], X.iloc[idx_high], matplotlib=True, show=False)
    plt.savefig(FIG_DIR / "Figure_10_HighRisk.png", bbox_inches='tight')
    plt.close()

    shap.force_plot(explainer.expected_value[0] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value,
                    shap_values_class2[idx_low], X.iloc[idx_low], matplotlib=True, show=False)
    plt.savefig(FIG_DIR / "Figure_10_LowRisk.png", bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    plot_confusion_matrices()
    shap_analysis()
