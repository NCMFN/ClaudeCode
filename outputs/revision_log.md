# Revision Log - Pass #6 (Reviewer-Directed Overhaul)

## Summary of Changes
- **Methodological Shift:** Shifted focus from building an "accurate detector" to demonstrating a methodological framework for detecting temporal leakage and evaluating generalization.
- **Chronological Split Added:** Models are now rigorously evaluated using a strictly chronological split (train early, val middle, test late) to unmask temporal overfitting.
- **Ablation Studies:** Extensive ablation across feature groups (Temporal, Behavioral, Graph, All) mapping across evaluation splits.
- **Adversarial Diagnostics:** Added precise boundary-crossing fraction diagnostics and a targeted temporal-shift evasion attack.
- **Sampling Visualizations:** Generated artifact proofs documenting how subsampling masks standard group-k-fold testing.
- **Feature Operationalization:** Detailed mapping of proxy variables to realistic behaviors vs. artifacts.
- **CERT Limitation:** Cross-dataset validation against CERT r6.2 is explicitly marked as 'Not yet completed' due to known access constraints, avoiding any fabricated results.

## Reproducibility diff outcome
Zero-diff.


## Pass #6 Artifact Count Verification
Total figures now: 30
Total tables now: 30
Net-new figures: 12
Net-new tables: 11

Net-new figures list:
 - ablation_variant_conditions_bar.png
 - cm_meta_chrono.png
 - cm_mlp_chrono.png
 - cm_svm_chrono.png
 - cm_xgb_dist.png
 - cm_xgboost_chrono.png
 - day_of_week_by_class.png
 - hour_cos_distribution_by_class.png
 - pr_all_models_chrono.png
 - pr_xgb_dist.png
 - roc_all_models_chrono.png
 - temporal_distribution_stacked.png

Net-new tables list:
 - ablation_variant_conditions.csv
 - cert_cross_dataset_validation_skipped.csv
 - chrono_split_limitation.csv
 - cm_counts_xgb_dist.csv
 - cross_validation_chrono.csv
 - evaluation_metrics_chrono.csv
 - evaluation_metrics_dist.csv
 - feature_operationalization_map.csv
 - significance_and_effect_sizes.csv
 - temporal_class_overlap.csv
 - temporal_period_counts.csv

Verified: 12 net-new figures, 11 net-new tables since Pass #5 baseline of 20+20. Full itemized list above.
