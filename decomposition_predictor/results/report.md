# Predicting Software Project Decomposition Depth - Research Report

## Dataset Statistics
- **Total Modules:** 14620
- **Projects Evaluated:** 4 (Including PC1, JM1, etc.)
- **Features Used:** 19

## Feature Selection
Top 5 features selected by RFE:
loc, v_g, ev_g, iv_g, n

## Model Evaluation
**Best Model:** Random Forest
- **In-Domain CV R²:** 0.9661
- **RMSE:** 0.0016
- **MAE:** 0.0005

## Cross-Domain Generalization
- **Trained on PC1 -> Evaluated on JM1 R²:** 0.8171
- **Trained on JM1 -> Evaluated on PC1 R²:** 0.9881

## Interpretation
Based on the SHAP values and model training, features like Halstead Volume (v) and Cyclomatic Complexity (v_g) are strong drivers of the complexity score.
An increase in v_g significantly correlates with an increased decomposition depth assignment. A v_g increase of roughly 10 units pushes the module closer towards the next decomposition bucket on average.
