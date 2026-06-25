# Predictive Satiety Modeling: Classifying Food Items via Glycemic Load vs. Satiety Index Metrics

## Project Overview
This repository contains a complete, reproducible machine learning pipeline that classifies foods into satiety tiers (Low / Medium / High) using nutritional and processing features. It investigates whether physical bulk (Water, Fiber) outweighs Glycemic Load as a predictor of short-term satiety.

## Dataset Sources
- Satiety Index for Foods (Brad K. Lee): https://www.kaggle.com/datasets/bradkmlee/satiety
- USDA FoodData Central: https://fdc.nal.usda.gov/download-datasets/
- International GI Tables 2021 (University of Sydney): https://glycemicindex.com/foodSearch.php
- Food Nutrition Dataset: https://www.kaggle.com/datasets/utsavdey1410/food-nutrition-dataset

*Note: Datasets are downloaded directly in the pipeline, or placed in `data/raw/` manually.*

## Installation
```bash
pip install -r requirements.txt
```

## How to Run the Pipeline
To run the full end-to-end pipeline, simply execute:
```bash
python src/run_pipeline.py
```

## Expected Output Files
### Figures (`outputs/figures/`)
- `fig1_si_distribution.png`: Histogram of Satiety Index by food category
- `fig2_gi_vs_si_scatter.png`: Scatter plot of GI vs Satiety Index (The Potato Paradox)
- `fig3_correlation_heatmap.png`: Pearson correlation heatmap of features
- `fig4_si_by_category.png`: Box plots of Satiety Index by category
- `fig5_confusion_matrices.png`: Confusion matrices for DT, LR, and RF models
- `fig6_roc_curves.png`: ROC curves for all models
- `fig7_cv_scores.png`: Cross-validation accuracy distribution
- `fig8_decision_tree.png`: Visualised Decision Tree
- `fig9_lr_odds_ratios.png`: Logistic Regression odds ratios for top 10 features
- `fig10_shap_summary.png`: SHAP beeswarm summary plot
- `fig11_shap_bar.png`: SHAP bar plot of mean absolute values
- `fig12_shap_dependence.png`: SHAP dependence plot

### Tables (`outputs/tables/`)
- `table1_correlations.csv`: Pearson correlations of features
- `table2_model_comparison.csv`: Full evaluation metrics for DT, LR, and RF
- `table3_lr_coefficients.csv`: Logistic Regression coefficients and odds ratios
- `table4_shap_values.csv`: SHAP values for feature importance
- `table5_hypothesis_test.csv`: Statistical test comparing Physical Bulk vs GL
- `table6_results_summary.csv`: Summary of model performances and top features
- `unmatched_foods.csv`: Foods that were not matched correctly across datasets

### Other Outputs
- `outputs/policy_brief.txt`: Summary of findings and policy implications
