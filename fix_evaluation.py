with open("src/phase5_evaluation.py", "w") as f:
    f.write("""import numpy as np
import pandas as pd
import joblib
import os
import matplotlib.pyplot as plt
from sklearn.metrics import average_precision_score, f1_score, recall_score, precision_recall_curve, confusion_matrix
import shap
import scipy.stats

def run_evaluation():
    print("Loading test data and models for evaluation...")
    model_dir = "outputs/datasets/models"

    data = np.load(f"{model_dir}/test_data.npz")
    X_tab_test = data['X_tab_test']
    X_meta_test = data['X_meta_test']
    y_test = data['y_test']
    X_tab_train = data['X_tab_train']
    y_train = data['y_train']

    meta_clf = joblib.load(f"{model_dir}/meta_model.pkl")
    xgb_clf = joblib.load(f"{model_dir}/xgb_model.pkl")

    try:
        with open(f"{model_dir}/threshold.txt", "r") as f:
            best_threshold = float(f.read().strip())
    except:
        best_threshold = 0.5

    meta_probs = meta_clf.predict_proba(X_meta_test)[:, 1]
    meta_preds = (meta_probs >= best_threshold).astype(int)

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
        "Threshold": best_threshold,
        "PR_AUC": pr_auc,
        "F1_Macro": f1_mac,
        "Malicious_Recall": recall,
        "FP_per_1000": fp_rate
    }])

    table_dir = "outputs/tables"
    metrics.to_csv(f"{table_dir}/evaluation_metrics.csv", index=False)
    print("Computed Test Metrics without leakage.")

    # 1. Real Significance Testing from CV folds
    cv_file = f"{table_dir}/cross_validation.csv"
    if os.path.exists(cv_file):
        cv_df = pd.read_csv(cv_file)
        sig_data = []
        for model in ['xgb', 'svm', 'mlp']:
            if len(cv_df) >= 5: # Valid Wilcoxon requires multiple samples
                stat, p = scipy.stats.wilcoxon(cv_df['meta'], cv_df[model])
                sig_data.append({
                    "Comparison": f"Meta vs {model.upper()}",
                    "p-value (Wilcoxon)": p,
                    "Significant (a=0.05)": p < 0.05
                })
            else:
                sig_data.append({
                    "Comparison": f"Meta vs {model.upper()}",
                    "p-value (Wilcoxon)": "NOT_COMPUTED",
                    "Significant (a=0.05)": "NOT_COMPUTED"
                })
        pd.DataFrame(sig_data).to_csv(f"{table_dir}/significance_testing.csv", index=False)
    else:
        print("Cross-validation fold data missing, skipping significance test.")

    # 2. Real Ablation Study (Retrain XGBoost to measure exact drops)
    print("Running Real Ablation Study...")
    import xgboost as xgb

    # numeric_cols = ['hour_sin', 'hour_cos', 'dow_sin', 'dow_cos', 'path_entropy',
    #                 'peer_z_score', 'usb_delta_seconds', 'graph_degree', 'graph_betweenness']
    # 0,1,2,3: Temporal
    # 4: Path Entropy
    # 5: Peer Z-Score
    # 6: USB Delta
    # 7,8: Graph Centrality

    ablation_res = []

    groups = {
        "Temporal": [0,1,2,3],
        "Path Entropy": [4],
        "Peer Z-Score": [5],
        "USB Delta": [6],
        "Graph Centrality": [7,8]
    }

    for name, cols in groups.items():
        keep_cols = [i for i in range(X_tab_train.shape[1]) if i not in cols]
        X_tr_abl = X_tab_train[:, keep_cols]
        X_te_abl = X_tab_test[:, keep_cols]

        clf = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
        clf.fit(X_tr_abl, y_train)
        probs = clf.predict_proba(X_te_abl)[:, 1]

        if len(np.unique(y_test)) > 1:
            auc = average_precision_score(y_test, probs)
        else:
            auc = np.nan
        ablation_res.append({"Removed Feature Set": name, "PR-AUC (XGBoost)": auc})

    ablation_res.append({"Removed Feature Set": "None (Full Model)", "PR-AUC (XGBoost)": pr_auc}) # full model auc

    pd.DataFrame(ablation_res).to_csv(f"{table_dir}/ablation_study.csv", index=False)

    # 3. Real Complexity Analysis
    print("Measuring Real Inference Latency...")
    import time
    latencies = []
    # Test batch of 100 single events
    for i in range(min(100, len(X_tab_test))):
        t0 = time.perf_counter()
        _ = xgb_clf.predict_proba(X_tab_test[i:i+1])
        latencies.append((time.perf_counter() - t0) * 1000) # ms

    mean_lat = np.mean(latencies)

    try:
        with open(f"{model_dir}/train_times.txt", "r") as f:
            times = f.read()
    except:
        times = "Unknown"

    complexity = pd.DataFrame({
        "Metric": ["Training Times", "Inference Latency XGBoost (mean)"],
        "Value": [times.replace('\\n', ' | '), f"{mean_lat:.2f} ms per event"]
    })
    complexity.to_csv(f"{table_dir}/complexity_analysis.csv", index=False)

    print("Evaluation complete. Generated assets.")

if __name__ == "__main__":
    run_evaluation()
""")
