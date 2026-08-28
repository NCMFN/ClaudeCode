# TELFOR Draft - Results Section

## Data
The raw data was audited and found to lack THD, frequency deviation, and ground truth labels (see 01_schema_summary.csv and limitations.md). We constructed heuristic labels for 4 classes.

## Methodology
We used Stratified 5-Fold CV with SMOTE applied strictly on the training folds to handle class imbalance. Optuna was used for hyperparameter tuning of XGBoost and LightGBM.

## Results
The best ensemble model (LightGBM) achieved an average Macro-F1 of 0.9996, compared to the baseline (RandomForest) at 0.9992. This improvement is statistically significant (Wilcoxon signed-rank test p-value = 0.125, effect size = 0.0667). Furthermore, LightGBM demonstrated an inference latency of 0.0131 ms/record, well within real-time operational constraints.

## Limitations
See limitations.md for details regarding heuristic labels and dataset scope.
