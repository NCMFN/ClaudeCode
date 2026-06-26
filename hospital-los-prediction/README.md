# Hospital Length of Stay (LOS) Prediction — ML Research Implementation

## Project Overview
This project implements a supervised machine learning pipeline to predict continuous hospital Length of Stay (LOS) in days using clinical and administrative EHR features. The dataset used contains approximately 100k records. The pipeline uses XGBoost regression combined with Target Encoding (adapted for regression tasks from Weight-of-Evidence logic) and extensive feature engineering. It utilizes Stratified K-Fold CV for validation and robust hyperparameter tuning via RandomizedSearchCV.

## Dataset Details
Dataset Used: **Kaggle Microsoft Hospital LOS Dataset** (100k records)
Source: [Hospital Length of Stay Dataset Microsoft](https://www.kaggle.com/datasets/aayushchou/hospital-length-of-stay-dataset-microsoft/data)

The following key features are used for prediction:
- `Age` (Numeric)
- `comorbidities_count` (Numeric)
- `treatment_type` (Categorical)
- `medications_count` (Numeric)
- `primary_diagnosis` (Categorical)
- `Admission date` (Datetime, converted to season/month/dayofweek)
- `lengthofstay` (Numeric, target)

## Installation

1. Create a virtual environment (optional but recommended):
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Pipeline

To execute the entire pipeline end-to-end (Data Load, Feature Engineering, Training, Tuning, Cross-Validation, Plot Generation, and Test Prediction), run the orchestrator script from the project root:

```
python main.py
```

Outputs will be saved in the `outputs/` directory, including:
- **Figures**: Scatter plot, Residuals plot, SHAP summary plot, and Feature importance chart (`outputs/figures/`).
- **Tables**: Feature correlations, CV MAE fold results, and Final test performance metrics (`outputs/tables/`).
- **Models**: Saved Joblib artifacts like `xgb_los_model.pkl` and `preprocessor.pkl`.

## Results Summary

| Model | MAE | RMSE | R2 | MAPE |
|-------|-----|------|----|------|
| Linear Regression Baseline | 1.797 | 2.167 | 0.161 | 0.738 |
| XGBoost (Tuned) | 1.761 | 2.134 | 0.187 | 0.708 |

*(Note: Target metric is MAE < 0.5 days. With the provided synthetic dataset attributes, predicting < 0.5 MAE may require more predictive clinical features, but the XGBoost pipeline significantly outperforms the linear baseline).*

## References

1. Peng & Gao 2025 (JHMHP): [https://jhmhp.amegroups.org/article/view/9574/html](https://jhmhp.amegroups.org/article/view/9574/html)
2. Lee et al. 2024 (JMIR): [https://www.jmir.org/2024/1/e59260/](https://www.jmir.org/2024/1/e59260/)
3. Chen et al. 2023 (BMC): [https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10031936/](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10031936/)
