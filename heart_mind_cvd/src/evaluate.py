import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (roc_auc_score, average_precision_score, f1_score,
                             confusion_matrix, brier_score_loss, roc_curve)
import shap
from sklearn.linear_model import LogisticRegression

# Set up standard matplotlib styling
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
                     'xtick.labelsize': 10, 'ytick.labelsize': 10,
                     'figure.dpi': 300, 'savefig.dpi': 300})

def evaluate_models(data_path, output_dir):
    """
    Evaluate trained models, compute metrics, plot ROC, and run SHAP analysis.
    """
    print("Loading data splits and models...")
    splits = joblib.load(os.path.join(data_path, 'data_splits.joblib'))
    X_train, y_train, X_val, y_val, X_test, y_test = splits

    rf_model = joblib.load(os.path.join(output_dir, 'models', 'rf_best.joblib'))
    xgb_model = joblib.load(os.path.join(output_dir, 'models', 'xgb_best.joblib'))

    os.makedirs(os.path.join(output_dir, 'figures'), exist_ok=True)

    # Train Logistic Regression baseline
    lr_model = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
    lr_model.fit(X_train, y_train)

    models = {
        'Logistic Regression': lr_model,
        'RandomForest': rf_model,
        'XGBoost': xgb_model
    }

    metrics = []

    # Evaluate and gather metrics
    plt.figure(figsize=(8, 6))
    for name, model in models.items():
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        auc_roc = roc_auc_score(y_test, y_prob)
        auc_prc = average_precision_score(y_test, y_prob)
        f1 = f1_score(y_test, y_pred, average='macro')
        brier = brier_score_loss(y_test, y_prob)

        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

        metrics.append({
            'Model': name,
            'AUC-ROC': auc_roc,
            'AUC-PRC': auc_prc,
            'Sensitivity': sensitivity,
            'Specificity': specificity,
            'F1 (macro)': f1,
            'Brier Score': brier
        })

        # Plot ROC
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        plt.plot(fpr, tpr, label=f'{name} (AUC = {auc_roc:.3f})')

    # Finalize ROC plot
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve Comparison')
    plt.legend(loc='lower right')
    roc_path = os.path.join(output_dir, 'figures', 'roc_curve_comparison.png')
    plt.savefig(roc_path, bbox_inches='tight')
    plt.close()
    print(f"Saved ROC curve comparison to {roc_path}")

    # Print metrics
    metrics_df = pd.DataFrame(metrics)
    print("\n--- Model Evaluation Summary ---")
    print(metrics_df.to_string(index=False))

    # Demographic parity check (AUC by subgroups on Test set)
    # Re-link demographic info. Since we OHE'd race and ordinal encoded sex...
    # We might not have the original labels, but we can use the columns we have.
    print("\n--- Demographic Parity Check (XGBoost) ---")
    y_prob_xgb = xgb_model.predict_proba(X_test)[:, 1]

    # Assuming 'SEX_A' exists in X_test. If ordinal encoded, 0/1. Let's just output by the values.
    if 'SEX_A' in X_test.columns:
        for val in X_test['SEX_A'].unique():
            idx = X_test['SEX_A'] == val
            if sum(y_test[idx]) > 0:
                auc = roc_auc_score(y_test[idx], y_prob_xgb[idx])
                flag = "*** FLAG (< 0.7) ***" if auc < 0.7 else ""
                print(f"SEX_A = {val}: AUC-ROC = {auc:.3f} {flag}")
            else:
                print(f"SEX_A = {val}: Not enough positive cases to compute AUC.")

    # SHAP Analysis
    print("\nRunning SHAP Analysis on XGBoost...")
    explainer = shap.TreeExplainer(xgb_model)
    # Using test set for SHAP to avoid data leakage on train set distributions
    # Since background data is large, taking a sample
    shap_values = explainer(X_test)

    # Global feature importance (bar chart)
    plt.figure()
    shap.plots.bar(shap_values, max_display=15, show=False)
    plt.title('SHAP Feature Importance (Top 15)')
    bar_path = os.path.join(output_dir, 'figures', 'shap_feature_importance.png')
    plt.savefig(bar_path, bbox_inches='tight')
    plt.close()
    print(f"Saved SHAP bar chart to {bar_path}")

    # Beeswarm plot
    plt.figure()
    shap.plots.beeswarm(shap_values, max_display=15, show=False)
    plt.title('SHAP Beeswarm Plot')
    beeswarm_path = os.path.join(output_dir, 'figures', 'shap_beeswarm.png')
    plt.savefig(beeswarm_path, bbox_inches='tight')
    plt.close()
    print(f"Saved SHAP beeswarm plot to {beeswarm_path}")

    # Dependence plot for mental_health_burden_score
    if 'mental_health_burden_score' in X_test.columns:
        plt.figure(figsize=(8,6))
        # Ensure we just call scatter and save
        shap.plots.scatter(shap_values[:, 'mental_health_burden_score'], show=False)
        plt.title('SHAP Dependence Plot: Mental Health Burden Score')
        dep_path = os.path.join(output_dir, 'figures', 'shap_dependence.png')
        plt.savefig(dep_path, bbox_inches='tight')
        plt.close()
        print(f"Saved SHAP dependence plot to {dep_path}")

    return metrics_df

if __name__ == "__main__":
    evaluate_models('heart_mind_cvd/data/', 'heart_mind_cvd/outputs/')
