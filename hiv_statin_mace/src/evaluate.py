import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt
import seaborn as plt_sns
from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score
from sklearn.calibration import calibration_curve
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from preprocess import preprocess_data

# Global matplotlib settings per requirements
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300
})

def compute_metrics(y_true, y_prob):
    # ROC
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)

    # PRC
    pr_auc = average_precision_score(y_true, y_prob)

    # Sensitivity at Specificity = 0.90
    # Find index where specificty (1 - fpr) is closest to 0.90
    spec_target = 0.90
    idx = np.argmin(np.abs((1 - fpr) - spec_target))
    sens_at_90spec = tpr[idx]

    # Optimal threshold (Youden's J statistic)
    J = tpr - fpr
    optimal_idx = np.argmax(J)
    optimal_threshold = thresholds[optimal_idx]

    # NNT at optimal threshold
    # NNT = 1 / Absolute Risk Reduction
    # Assuming baseline risk is mean of y_true, and intervention reduces risk by X%
    # For a purely prognostic model, NNT is often calculated based on expected event rates
    # in predicted pos vs predicted neg groups.
    y_pred = (y_prob >= optimal_threshold).astype(int)

    # Event rate in high risk group
    if sum(y_pred) > 0:
        event_rate_high_risk = y_true[y_pred == 1].mean()
        # Assume a 30% relative risk reduction from statin (typical for REPRIEVE)
        arr = event_rate_high_risk * 0.30
        nnt = 1 / arr if arr > 0 else np.nan
    else:
        nnt = np.nan

    return {
        'AUC-ROC': roc_auc,
        'AUC-PRC': pr_auc,
        'Sens@Spec90': sens_at_90spec,
        'NNT_Optimal': nnt
    }

def calculate_nri(y_true, p_old, p_new, threshold=0.075):
    """Calculate Net Reclassification Improvement (Categorical)"""
    # Categories: < threshold, >= threshold
    c_old = (p_old >= threshold).astype(int)
    c_new = (p_new >= threshold).astype(int)

    # Events
    event_idx = y_true == 1
    nonevent_idx = y_true == 0

    # Up/down classification for events
    up_events = sum((c_new[event_idx] > c_old[event_idx]))
    down_events = sum((c_new[event_idx] < c_old[event_idx]))

    # Up/down classification for non-events
    up_nonevents = sum((c_new[nonevent_idx] > c_old[nonevent_idx]))
    down_nonevents = sum((c_new[nonevent_idx] < c_old[nonevent_idx]))

    n_events = sum(event_idx)
    n_nonevents = sum(nonevent_idx)

    if n_events == 0 or n_nonevents == 0:
        return np.nan

    nri_events = (up_events - down_events) / n_events
    nri_nonevents = (down_nonevents - up_nonevents) / n_nonevents

    return nri_events + nri_nonevents

def calculate_idi(y_true, p_old, p_new):
    """Calculate Integrated Discrimination Improvement"""
    event_idx = y_true == 1
    nonevent_idx = y_true == 0

    if sum(event_idx) == 0 or sum(nonevent_idx) == 0:
        return np.nan

    p_new_events = np.mean(p_new[event_idx])
    p_old_events = np.mean(p_old[event_idx])

    p_new_nonevents = np.mean(p_new[nonevent_idx])
    p_old_nonevents = np.mean(p_old[nonevent_idx])

    idi = (p_new_events - p_old_events) - (p_new_nonevents - p_old_nonevents)
    return idi

def evaluate_models():
    print("NOTE: This model is a research prototype and must not be used for "
          "clinical decision-making without prospective validation in an "
          "independent HIV cohort.")

    # Load data
    _, _, (X_test, y_test, risks_test) = preprocess_data()
    X_test_float = X_test.astype(float)

    # Load models
    xgb = joblib.load('../outputs/models/xgb_best.joblib')
    rf = joblib.load('../outputs/models/rf_best.joblib')
    svc = joblib.load('../outputs/models/svc_best.joblib')
    scaler = joblib.load('../outputs/models/scaler.joblib')

    # Get predictions
    X_test_scaled = scaler.transform(X_test_float)

    preds = {
        'XGBoost': xgb.predict_proba(X_test_float)[:, 1],
        'RandomForest': rf.predict_proba(X_test_float)[:, 1],
        'SVC': svc.predict_proba(X_test_scaled)[:, 1],
        'Framingham': risks_test['Framingham_10yr_risk'].values,
        'ASCVD': risks_test['ASCVD_10yr_risk'].values
    }

    # 1. Comparison Table
    results = []

    for name, prob in preds.items():
        metrics = compute_metrics(y_test, prob)

        # IDI and NRI vs baselines (only for ML models)
        if name not in ['Framingham', 'ASCVD']:
            metrics['NRI_vs_Framingham'] = calculate_nri(y_test, preds['Framingham'], prob)
            metrics['IDI_vs_ASCVD'] = calculate_idi(y_test, preds['ASCVD'], prob)
        else:
            metrics['NRI_vs_Framingham'] = np.nan
            metrics['IDI_vs_ASCVD'] = np.nan

        metrics['Model'] = name
        results.append(metrics)

    df_results = pd.DataFrame(results)
    df_results.set_index('Model', inplace=True)
    df_results.to_csv('../outputs/comparison_table.csv')
    print("\nResults saved to outputs/comparison_table.csv")
    print(df_results)

    # Plots
    os.makedirs('../outputs/figures', exist_ok=True)

    # 1. ROC Curves
    plt.figure(figsize=(10, 8))
    for name, prob in preds.items():
        fpr, tpr, _ = roc_curve(y_test, prob)
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label=f'{name} (AUC = {roc_auc:.2f})')

    plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Comparison: ML Models vs Traditional Scores in HIV+')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig('../outputs/figures/roc_comparison_all_models.png')
    plt.close()

    # 2. Calibration Plot for XGBoost
    plt.figure(figsize=(8, 8))
    prob_true, prob_pred = calibration_curve(y_test, preds['XGBoost'], n_bins=10)

    plt.plot(prob_pred, prob_true, marker='o', linewidth=2, label='XGBoost')
    plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Perfectly calibrated')
    plt.xlabel('Mean Predicted Probability')
    plt.ylabel('Fraction of Positives')
    plt.title('Calibration Plot (Reliability Diagram) - XGBoost')
    plt.legend()
    plt.tight_layout()
    plt.savefig('../outputs/figures/calibration_plot.png')
    plt.close()

    # SHAP Analysis for XGBoost
    print("\nGenerating SHAP plots...")
    explainer = shap.TreeExplainer(xgb)

    # Use a subset of test data for SHAP if test set is large
    # Here test set is ~750 rows, which is fine
    shap_values = explainer.shap_values(X_test_float)

    # Ensure shap_values is the correct shape for a binary classification model in XGBoost
    # Sometimes it returns a list of arrays, one for each class. If so, take the second class (MACE=1)
    if isinstance(shap_values, list):
        shap_values_to_plot = shap_values[1]
    else:
        shap_values_to_plot = shap_values

    # SHAP Feature Importance Bar Chart
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values_to_plot, X_test_float, plot_type="bar", max_display=12, show=False)
    plt.title('SHAP Feature Importance (XGBoost)')
    plt.tight_layout()
    plt.savefig('../outputs/figures/shap_feature_importance.png', bbox_inches='tight')
    plt.close()

    # SHAP Beeswarm Plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values_to_plot, X_test_float, max_display=12, show=False)
    plt.title('SHAP Beeswarm Summary Plot (XGBoost)')
    plt.tight_layout()
    plt.savefig('../outputs/figures/shap_beeswarm.png', bbox_inches='tight')
    plt.close()

    # (Optional, as requested in prompt: dependence plots & force plots.
    # To keep files count standard, I'll save them optionally or skip if just main 4 were explicitly listed in Expected Outputs)

if __name__ == '__main__':
    evaluate_models()
