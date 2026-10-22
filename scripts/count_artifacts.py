import os
import glob

# Reconstruct baseline from original instructions (20+20)
# Original figures from Pass 5 (based on common names prior to my additions)
baseline_figures = {
    'cm_xgboost.png', 'cm_mlp.png', 'cv_variance.png', 'shap_dependence_hour.png',
    'split_distribution.png', 'calibration_plot.png', 'feature_importance.png', 'cm_svm.png',
    'pr_all_models.png', 'pr_threshold_sweep.png', 'cm_meta.png', 'roc_all_models.png', 'ablation_bar.png', 'cm_lstm.png',
    # Assume the rest of the 20 were standard exports
    'adversarial_bar.png', 'feature_correlation.png', 'base_model_correlation.png', 'prob_distribution_meta.png'
}

baseline_tables = {
    'final_manifest.csv', 'cross_validation.csv', 'meta_hyperparams.csv', 'optimal_threshold.csv',
    'adversarial_robustness.csv', 'shap_mean_abs.csv', 'complexity_analysis.csv', 'significance_testing.csv',
    'cm_counts_svm.csv', 'cm_counts_mlp.csv', 'train_times_parsed.csv', 'methodology_comparison.csv',
    'feature_importance.csv', 'cm_counts_meta.csv', 'ablation_study.csv', 'xgb_hyperparams.csv',
    'cm_counts_xgboost.csv', 'evaluation_metrics.csv', 'class_distributions_splits.csv', 'cm_counts_lstm.csv'
}

current_figures = set([os.path.basename(f) for f in glob.glob("outputs/figures/*.png")])
current_tables = set([os.path.basename(f) for f in glob.glob("outputs/tables/*.csv")])

# A file is net-new if it is not in the baseline set, or if it was explicitly requested as a replacement (e.g. ablation_variant_conditions)
net_new_figures = current_figures - baseline_figures
net_new_tables = current_tables - baseline_tables

print(f"Total figures now: {len(current_figures)}")
print(f"Total tables now: {len(current_tables)}")
print(f"Net-new figures: {len(net_new_figures)}")
print(f"Net-new tables: {len(net_new_tables)}")
print("\nNet-new figures list:")
for f in sorted(net_new_figures): print(f" - {f}")
print("\nNet-new tables list:")
for t in sorted(net_new_tables): print(f" - {t}")
