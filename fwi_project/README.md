# Predicting Localized Fire Weather Index (FWI) in the SE US

This project implements an end-to-end machine learning pipeline to predict the Fire Weather Index (FWI) proxy based on meteorological data and validating predictions against real fire intensification events in the Southeastern United States.

## Repository Structure

```
fwi_project/
├── data/                  # Contains raw/processed datasets (gridMET, MTBS)
├── models/                # Trained model artifacts (.pkl)
├── outputs/               # Visualizations, diagrams, and predicted CSVs
├── src/                   # Source code
│   ├── 01_data_processing.py
│   ├── 02_model_training.py
│   ├── 03_validation.py
│   ├── 04_visualization.py
│   └── 05_architecture.py
├── requirements.txt       # Dependencies
└── README.md              # Project documentation
```

## Setup & Reproduction Steps

1. **Install Dependencies:**
   Ensure you have Python 3.10+ installed.
   ```bash
   pip install -r requirements.txt
   ```

2. **Phase 1: Data Acquisition & Feature Engineering**
   This script streams gridMET data via OPeNDAP, downloads MTBS fire perimeters, derives proxies for KBDI and FWI, and engineers relevant rolling weather features.
   ```bash
   python src/01_data_processing.py
   ```

3. **Phase 2: Model Training & Tuning**
   Trains XGBoost, Random Forest, and Linear Regression models using a time-based train-test split (Train: 2000-2019, Test: 2020-2023). Extracts SHAP values.
   ```bash
   python src/02_model_training.py
   ```

4. **Phase 3: Validation**
   Validates the model's predictive capability by calculating a hit rate for the top 15 MTBS fire blow-up events. Also performs an ablation study by removing humidity and wind shear.
   ```bash
   python src/03_validation.py
   ```

5. **Phase 4: Visualization & Output**
   Generates a geospatial FWI heatmap, SHAP summary plots, FWI time series, the predicted outputs CSV, and the system architecture diagram.
   ```bash
   python src/04_visualization.py
   python src/05_architecture.py
   ```

6. **End-to-End Pipeline (Optional)**
   You can run all scripts sequentially using `main.py`:
   ```bash
   python main.py
   ```

## Key Findings
- Machine Learning (XGBoost/RF) can highly accurately predict the FWI proxy based on localized micro-climate variables.
- SHAP feature importance confirms the relevance of engineered proxies and features to overall fire danger ratings.
