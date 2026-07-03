import numpy as np
import pandas as pd
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import average_precision_score, f1_score, recall_score, precision_recall_curve, confusion_matrix
import shap

def run_evaluation():
    print("Loading test data and models for evaluation...")
    model_dir = "outputs/datasets/models"

    data = np.load(f"{model_dir}/test_data.npz")
    X_tab_test = data['X_tab_test']
    X_meta_test = data['X_meta_test']
    y_test = data['y_test']

    meta_clf = joblib.load(f"{model_dir}/meta_model.pkl")
    xgb_clf = joblib.load(f"{model_dir}/xgb_model.pkl")

    meta_probs = meta_clf.predict_proba(X_meta_test)[:, 1]
    meta_preds = meta_clf.predict(X_meta_test)

    # 1. Metrics
    if len(np.unique(y_test)) > 1:
        pr_auc = average_precision_score(y_test, meta_probs)
        f1_mac = f1_score(y_test, meta_preds, average='macro')
        recall = recall_score(y_test, meta_preds)

        cm = confusion_matrix(y_test, meta_preds)
        fp = cm[0, 1] if cm.shape == (2,2) else 0
        fp_rate = (fp / len(y_test)) * 1000
    else:
        pr_auc, f1_mac, recall, fp_rate = 0, 0, 0, 0

    metrics = pd.DataFrame([{
        "Model": "Meta-Classifier",
        "PR_AUC": pr_auc,
        "F1_Macro": f1_mac,
        "Malicious_Recall": recall,
        "FP_per_1000": fp_rate
    }])

    table_dir = "outputs/tables"
    metrics.to_csv(f"{table_dir}/evaluation_metrics.csv", index=False)

    # 2. PR Curve Plot
    fig_dir = "outputs/figures"
    if len(np.unique(y_test)) > 1:
        precision, recall_vals, _ = precision_recall_curve(y_test, meta_probs)
        plt.figure(figsize=(8, 6))
        plt.plot(recall_vals, precision, marker='.', label='Meta-Classifier')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curve')
        plt.legend()
        plt.savefig(f"{fig_dir}/pr_curve.png", dpi=300, bbox_inches='tight')
        plt.close()

    # 3. SHAP
    print("Computing SHAP values...")
    explainer = shap.TreeExplainer(xgb_clf)
    # Using a sample to speed up SHAP
    shap_sample = X_tab_test[:100]
    shap_values = explainer.shap_values(shap_sample)

    feature_names = ['hour_sin', 'hour_cos', 'dow_sin', 'dow_cos', 'path_entropy',
                     'peer_z_score', 'usb_delta_seconds', 'graph_degree', 'graph_betweenness']

    plt.figure()
    shap.summary_plot(shap_values, shap_sample, feature_names=feature_names, show=False)
    plt.savefig(f"{fig_dir}/shap_summary.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Compare Table (Methodology)
    method_df = pd.DataFrame({
        "Feature": ["Dataset Scale", "Adversarial Robustness", "Ensemble Method", "Explainability"],
        "Current Study 2024": ["7,400", "None", "Random Forest", "Feature Importance"],
        "Proposed Research": ["1.6B+ (Subsampled)", "Low-and-Slow Simulation", "XGB+SVM+LSTM Meta", "SHAP + LIME Stability"]
    })
    method_df.to_csv(f"{table_dir}/methodology_comparison.csv", index=False)

    # Generate paper_assets_manifest.csv
    asset_dir = "outputs/paper_assets"
    os.makedirs(asset_dir, exist_ok=True)

    manifest_data = []
    for root, dirs, files in os.walk("outputs"):
        if "paper_assets" in root: continue
        for file in files:
            path = os.path.join(root, file)
            manifest_data.append({"Asset": file, "Path": path})

    manifest_df = pd.DataFrame(manifest_data)
    manifest_df.to_csv(f"{asset_dir}/paper_assets_manifest.csv", index=False)

    print("Evaluation complete. Generated assets manifest.")

if __name__ == "__main__":
    run_evaluation()
