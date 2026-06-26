import re

with open('/app/downloads.md', 'r') as f:
    content = f.read()

# We need to add all these files to the right sections.
new_datasets = """
- **Predictions**
  - Description: Predictions
  - Source: Generated
  - Download Link: [predictions.csv](ntl-poverty-estimation/outputs/datasets/predictions.csv)
- **Residuals**
  - Description: Residuals
  - Source: Generated
  - Download Link: [residuals.csv](ntl-poverty-estimation/outputs/datasets/residuals.csv)
- **Fold Results**
  - Description: Fold Results
  - Source: Generated
  - Download Link: [fold_results.csv](ntl-poverty-estimation/outputs/datasets/fold_results.csv)
- **Feature Importance**
  - Description: Feature Importance Dataset
  - Source: Generated
  - Download Link: [feature_importance.csv](ntl-poverty-estimation/outputs/datasets/feature_importance.csv)
- **SHAP Values**
  - Description: SHAP Values
  - Source: Generated
  - Download Link: [shap_values.csv](ntl-poverty-estimation/outputs/datasets/shap_values.csv)
- **Error Metrics**
  - Description: Error Metrics
  - Source: Generated
  - Download Link: [error_metrics.csv](ntl-poverty-estimation/outputs/datasets/error_metrics.csv)
- **Fairness Metrics**
  - Description: Fairness Metrics
  - Source: Generated
  - Download Link: [fairness_metrics.csv](ntl-poverty-estimation/outputs/datasets/fairness_metrics.csv)
- **Prediction Results**
  - Description: Prediction Results
  - Source: Generated
  - Download Link: [prediction_results.csv](ntl-poverty-estimation/outputs/datasets/prediction_results.csv)
- **Model Performance Table**
  - Description: Model Performance Table
  - Source: Generated
  - Download Link: [table_1_model_performance.csv](ntl-poverty-estimation/outputs/tables/table_1_model_performance.csv)
- **Feature Importance Table**
  - Description: Feature Importance Table
  - Source: Generated
  - Download Link: [table_2_feature_importance.csv](ntl-poverty-estimation/outputs/tables/table_2_feature_importance.csv)
- **Cross Validation Results Table**
  - Description: Cross Validation Results Table
  - Source: Generated
  - Download Link: [table_3_cross_validation_results.csv](ntl-poverty-estimation/outputs/tables/table_3_cross_validation_results.csv)
- **Error Analysis Table**
  - Description: Error Analysis Table
  - Source: Generated
  - Download Link: [table_4_error_analysis.csv](ntl-poverty-estimation/outputs/tables/table_4_error_analysis.csv)
- **Fairness Assessment Table**
  - Description: Fairness Assessment Table
  - Source: Generated
  - Download Link: [table_5_fairness_assessment.csv](ntl-poverty-estimation/outputs/tables/table_5_fairness_assessment.csv)
- **Paper Assets Manifest**
  - Description: Paper Assets Manifest
  - Source: Generated
  - Download Link: [paper_assets_manifest.csv](ntl-poverty-estimation/outputs/paper_assets/paper_assets_manifest.csv)
"""

new_images = """
- **Feature Importance Plot**
  - Description: Feature Importance Plot
  - Source/Attribution: Generated
  - Download Link: [feature_importance.png](ntl-poverty-estimation/outputs/figures/feature_importance.png)
- **Predicted vs Actual Plot**
  - Description: Predicted vs Actual Plot
  - Source/Attribution: Generated
  - Download Link: [predicted_vs_actual.png](ntl-poverty-estimation/outputs/figures/predicted_vs_actual.png)
- **Poverty Heatmap**
  - Description: Poverty Heatmap Plot
  - Source/Attribution: Generated
  - Download Link: [poverty_heatmap.png](ntl-poverty-estimation/outputs/figures/poverty_heatmap.png)
- **Model Comparison Plot**
  - Description: Model Comparison Plot
  - Source/Attribution: Generated
  - Download Link: [model_comparison.png](ntl-poverty-estimation/outputs/figures/model_comparison.png)
- **Confusion Matrix**
  - Description: Confusion Matrix Plot
  - Source/Attribution: Generated
  - Download Link: [confusion_matrix.png](ntl-poverty-estimation/outputs/figures/confusion_matrix.png)
- **Correlation Heatmap**
  - Description: Correlation Heatmap Plot
  - Source/Attribution: Generated
  - Download Link: [correlation_heatmap.png](ntl-poverty-estimation/outputs/figures/correlation_heatmap.png)
- **Residual Analysis**
  - Description: Residual Analysis Plot
  - Source/Attribution: Generated
  - Download Link: [residual_analysis.png](ntl-poverty-estimation/outputs/figures/residual_analysis.png)
- **ROC Curve**
  - Description: ROC Curve
  - Source/Attribution: Generated
  - Download Link: [roc_curve.png](ntl-poverty-estimation/outputs/figures/roc_curve.png)
- **Precision Recall Curve**
  - Description: Precision Recall Curve
  - Source/Attribution: Generated
  - Download Link: [precision_recall_curve.png](ntl-poverty-estimation/outputs/figures/precision_recall_curve.png)
- **SHAP Summary Plot**
  - Description: SHAP Summary Plot
  - Source/Attribution: Generated
  - Download Link: [shap_summary.png](ntl-poverty-estimation/outputs/figures/shap_summary.png)
- **Partial Dependence**
  - Description: Partial Dependence Plot
  - Source/Attribution: Generated
  - Download Link: [partial_dependence.png](ntl-poverty-estimation/outputs/figures/partial_dependence.png)
- **Geospatial Map**
  - Description: Geospatial Map Plot
  - Source/Attribution: Generated
  - Download Link: [geospatial_map.png](ntl-poverty-estimation/outputs/figures/geospatial_map.png)
- **Clustering Visualization**
  - Description: Clustering Visualization
  - Source/Attribution: Generated
  - Download Link: [clustering_visualization.png](ntl-poverty-estimation/outputs/figures/clustering_visualization.png)
- **Time Series Forecast**
  - Description: Time Series Forecast Plot
  - Source/Attribution: Generated
  - Download Link: [time_series_forecast.png](ntl-poverty-estimation/outputs/figures/time_series_forecast.png)
- **Cross Validation Results**
  - Description: Cross Validation Results Plot
  - Source/Attribution: Generated
  - Download Link: [cross_validation_results.png](ntl-poverty-estimation/outputs/figures/cross_validation_results.png)
- **Hyperparameter Tuning**
  - Description: Hyperparameter Tuning Plot
  - Source/Attribution: Generated
  - Download Link: [hyperparameter_tuning.png](ntl-poverty-estimation/outputs/figures/hyperparameter_tuning.png)
- **Heatmap Plot**
  - Description: Heatmap Plot
  - Source/Attribution: Generated
  - Download Link: [heatmap.png](ntl-poverty-estimation/outputs/figures/heatmap.png)
"""

new_research_files = """
- **Poverty Heatmap TIF**
  - Description: Poverty Heatmap GeoTIFF
  - Source: Generated
  - Download Link: [poverty_heatmap.tif](ntl-poverty-estimation/outputs/poverty_heatmap.tif)
- **Research Report**
  - Description: Research Report PDF
  - Source: Generated
  - Download Link: [research_report.pdf](ntl-poverty-estimation/outputs/reports/research_report.pdf)
- **Final Paper TEX**
  - Description: Final Paper LaTeX File
  - Source: Generated
  - Download Link: [final_paper.tex](ntl-poverty-estimation/outputs/final_paper.tex)
"""

content = content.replace('## Datasets', '## Datasets' + new_datasets)
content = content.replace('## Images', '## Images' + new_images)
content = content.replace('## Research Files', '## Research Files' + new_research_files)

with open('/app/downloads.md', 'w') as f:
    f.write(content)
