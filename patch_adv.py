import re

with open("src/phase4_adversarial.py", "r") as f:
    content = f.read()

# Add config import
content = content.replace("import xgboost as xgb", "import xgboost as xgb\nfrom config import HOUR_COS_PERTURBATION, EVASION_PERTURBATION_MULTIPLIER")

replacement = """
    # 4. New hour_cos Targeted Attack
    X_tab_hour = X_tab_test.copy()

    # Feature 1 is hour_cos
    # Perturb hour_cos by HOUR_COS_PERTURBATION
    X_tab_hour[malicious_idx, 1] += HOUR_COS_PERTURBATION

    # Clip to valid cosine range
    X_tab_hour[malicious_idx, 1] = np.clip(X_tab_hour[malicious_idx, 1], -1.0, 1.0)

    hour_probs = xgb_base.predict_proba(X_tab_hour)[:, 1]
    hour_pr_auc = average_precision_score(y_test, hour_probs)
    print(f"Targeted hour_cos Attack PR-AUC: {hour_pr_auc:.4f}")


    # Evasion stats (assuming threshold 0.5 for boundary)
    base_preds = (baseline_probs[malicious_idx] > 0.5).astype(int)
    base_mal_count = base_preds.sum()

    evasion_preds = (evasion_probs[malicious_idx] > 0.5).astype(int)
    evasion_crossed = base_mal_count - evasion_preds.sum()

    hour_preds = (hour_probs[malicious_idx] > 0.5).astype(int)
    hour_crossed = base_mal_count - hour_preds.sum()


    diagnostics = pd.DataFrame({
        "Attack Type": ["Evasion (Behavioral/Graph)", "Label Poisoning (5% Train)", "Targeted Feature (hour_cos)"],
        "Features Perturbed": ["peer_z_score, graph_degree", "Labels", "hour_cos"],
        "Magnitude": [f"{EVASION_PERTURBATION_MULTIPLIER}x multiplier", "5% train labels flipped", f"+{HOUR_COS_PERTURBATION} absolute"],
        "Boundary-Crossing Fraction": [f"{evasion_crossed/len(malicious_idx):.2f}" if len(malicious_idx) > 0 else "N/A", "N/A", f"{hour_crossed/len(malicious_idx):.2f}" if len(malicious_idx) > 0 else "N/A"],
        "Resulting PR-AUC": [evasion_pr_auc, poisoning_pr_auc, hour_pr_auc]
    })

    out_dir = "outputs/tables"
    os.makedirs(out_dir, exist_ok=True)
    results = pd.DataFrame({
        "Metric": ["Baseline PR-AUC", "Evasion PR-AUC", "Poisoning PR-AUC", "Dist-Shift PR-AUC", "Targeted hour_cos PR-AUC"],
        "Value": [baseline_pr_auc, evasion_pr_auc, poisoning_pr_auc, dist_pr_auc, hour_pr_auc]
    })

    results.to_csv(f"{out_dir}/adversarial_robustness.csv", index=False)
    diagnostics.to_csv(f"{out_dir}/adversarial_robustness_diagnostics.csv", index=False)
"""

content = re.sub(r'results = pd\.DataFrame\(.*?\)\n\n    out_dir = "outputs/tables"\n    os\.makedirs\(out_dir, exist_ok=True\)\n    results\.to_csv\(f"\{out_dir\}/adversarial_robustness\.csv", index=False\)', replacement, content, flags=re.DOTALL)


with open("src/phase4_adversarial.py", "w") as f:
    f.write(content)
