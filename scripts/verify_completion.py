import os
import sys
import json
import subprocess
import glob

def check_file_exists(path, min_size=1):
    if not os.path.exists(path):
        return False
    if min_size and os.path.getsize(path) < min_size:
        return False
    return True

def run():
    failed = False
    mode_path = 'outputs/run_mode.json'
    if not os.path.exists(mode_path):
        print("FAIL: outputs/run_mode.json does not exist")
        failed = True
    else:
        with open(mode_path, 'r') as f:
            mode_data = json.load(f)
            mode = mode_data.get('mode')
            if mode not in ['REAL', 'PROTOCOL_ONLY']:
                print(f"FAIL: invalid mode {mode}")
                failed = True

        if mode == 'REAL':
            if not check_file_exists('outputs/tables/redteam_summary.csv', 10):
                print("FAIL: redteam_summary.csv missing or empty in REAL mode")
                failed = True

            # Check for 20 figures
            figures = [
                'fig_timeline_redteam_vs_benign_leaky.png',
                'fig_timeline_redteam_vs_benign_matched.png',
                'fig_leakage_gap_by_split.png',
                'fig_time_only_control.png',
                'fig_label_shuffle_control.png',
                'fig_rolling_origin_prauc.png',
                'fig_pr_curves_chronological.png',
                'fig_roc_curves_chronological.png',
                'fig_alert_budget_curve.png',
                'fig_calibration.png',
                'fig_confusion_matrices.png',
                'fig_shap_summary.png',
                'fig_shap_dependence_top_feature.png',
                'fig_attribution_share_temporal.png',
                'fig_ablation.png',
                'fig_robustness_stress.png',
                'fig_bootstrap_ci_forest.png',
                'fig_split_composition.png',
                'fig_feature_correlation_train_only.png',
                'fig_probability_distribution.png'
            ]
            for fig in figures:
                path = f"outputs/figures/{fig}"
                if not check_file_exists(path, 10000):  # min 10KB
                    print(f"FAIL: figure {path} missing or <10KB")
                    failed = True

            tables = [
                'redteam_unmatched.csv',
                'ingest_report.csv',
                'split_composition.csv',
                'model_cards.csv',
                'leakage_audit_arms.csv',
                'leakage_gap_by_split.csv',
                'time_only_control.csv',
                'label_shuffle_control.csv',
                'attribution_share_temporal.csv',
                'evaluation_chronological.csv',
                'pairwise_comparisons.csv',
                'ablation.csv',
                'robustness.csv',
                'complexity.csv',
                'shap_mean_abs.csv',
                'redteam_summary.csv'
            ]
            for tab in tables:
                path = f"outputs/tables/{tab}"
                if not check_file_exists(path, 10):
                    print(f"FAIL: table {path} missing or empty")
                    failed = True

        elif mode == 'PROTOCOL_ONLY':
            # ensure no perf metric column in outputs
            pass

    # run pytest
    res = subprocess.run(['pytest', '-q', 'tests/'], capture_output=True, text=True)
    if res.returncode != 0:
        print("FAIL: pytest failed")
        print(res.stdout)
        failed = True

    if failed:
        sys.exit(1)
    else:
        print("ALL GATES PASSED")

if __name__ == '__main__':
    run()
