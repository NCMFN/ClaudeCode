# Research Mode Context

Activated when working on supervised ML research tasks.

## Session Objectives
- Produce reproducible, publication-quality ML pipelines
- Target IEEE conference/journal formatting for outputs
- Prioritise explainability (SHAP) and rigour over speed

## Active Constraints
- Experiment budget: MAX 10 runs
- Minimum improvement threshold to continue: 2%
- All outputs saved to `/outputs/` with fixed filenames
- `random_state=42` enforced globally

## Preferred Models (in order of trial)
1. Logistic / Linear Regression (baseline)
2. Random Forest
3. XGBoost
4. LightGBM
5. SVM (only if n_samples < 15,000)
6. MLP (only if explicit non-linearity confirmed)

## Primary Metrics
- Classification: F1-macro (primary), ROC-AUC, MCC
- Regression: RMSE (primary), R², MAE, MAPE

## Research Institution
University of Uyo, Department of Computer Science, Nigeria
Co-authors: Abang E. Emem and collaborators
Submission targets: IEEE conferences and journals
