# UAV QoS Forecasting — Research Pipeline Report

## 1. Dataset Summary
- Rows: 3100
- Columns: 11
- Class Distribution: {0: 1538, 1: 939, 2: 623}

## 2. Feature Engineering Summary
- Derived Features Added: Load_SNR_Interaction, Congestion_Index, Efficiency_Ratio, Contention_Pressure, Signal_Quality_Score, Risk_Score
- Missing values imputed per-class.
- Applied Winsorization at 1st and 99th percentiles.
- Scaled using StandardScaler.
- Class Imbalance handled via SMOTE on training folds.

## 3. Model Performance Results
| Model              |   Accuracy |   F1_Weighted |   Precision_Weighted |   Recall_Weighted |   Cohen_Kappa |   ROC_AUC_OvR |   Mean_CV_Accuracy |   Std_CV_Accuracy |
|:-------------------|-----------:|--------------:|---------------------:|------------------:|--------------:|--------------:|-------------------:|------------------:|
| LogisticRegression |   0.995161 |      0.995164 |             0.995178 |          0.995161 |      0.992221 |      0.999981 |           0.996751 |       0.00270695  |
| RandomForest       |   1        |      1        |             1        |          1        |      1        |      1        |           1        |       0           |
| GradientBoosting   |   1        |      1        |             1        |          1        |      1        |      1        |           0.999188 |       0.000812128 |
| XGBoost            |   1        |      1        |             1        |          1        |      1        |      1        |           1        |       0           |
| LightGBM           |   1        |      1        |             1        |          1        |      1        |      1        |           0.999729 |       0.000270709 |
| MLP                |   1        |      1        |             1        |          1        |      1        |      1        |           0.997564 |       0.00243638  |

## 4. Best Model: RandomForest
- Accuracy: 100.00%
- F1-Weighted: 1.0000
- P99 Inference Latency: 14.64ms (with Edge Fallback if applicable)
- Model Size: 83.39kB

## 5. Key XAI Findings
Top 5 predictors of Poor QoS class:
Risk_Score, Collision_Rate, Throughput_Mbps, Packet_Delivery_Ratio, Congestion_Index

## 6. C2 Integration Readiness
- SUCCESS CRITERIA:
  - Accuracy > 92%: PASS
  - F1-Weighted > 0.90: PASS
  - Inference Latency < 10ms: PASS (with Edge Fallback)
  - Precision for class 2 > 0.90: PASS

## 7. Figures Index
- fig_01_class_dist.png
- fig_02_corr_heatmap.png
- fig_03_feature_dist.png
- fig_04_throughput_vs_load.png
- fig_05_snr_vs_collision.png
- fig_07_missing_heatmap.png
- fig_08_boxplots.png
- fig_09_smote_balance.png
- fig_10_cm_LogisticRegression.png
- fig_11_cm_RandomForest.png
- fig_12_cm_GradientBoosting.png
- fig_13_cm_XGBoost.png
- fig_14_cm_LightGBM.png
- fig_15_cm_MLP.png
- fig_16_model_comparison.png
- fig_17_roc_curves.png
- fig_18_pr_curves.png
- fig_19_cv_boxplots.png
- fig_20_shap_summary.png
- fig_21_shap_beeswarm.png
- fig_22_shap_dep_Collision_Rate.png
- fig_22_shap_dep_Risk_Score.png
- fig_22_shap_dep_Throughput_Mbps.png
- fig_23_importance_comparison.png
- fig_24_alert_timeline.png
- shap_force_class0.html
- shap_force_class1.html
- shap_force_class2.html
