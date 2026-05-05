# End-to-End Machine Learning Framework for Predicting Phytoremediation Affinity

## Objective
This repository contains a scalable, reproducible machine learning pipeline that predicts plant–contaminant phytoremediation affinity. The framework integrates multi-domain datasets, capturing the complex interactions between plant traits, soil chemistry, contaminant properties, and environmental conditions to predict Bioconcentration Factor (BCF), Translocation Factor (TF), Remediation Efficiency, and Affinity Class.

## Directory Structure
- `data/`: Contains the generated integrated dataset representing realistic bounds of the respective public datasets.
- `models/`: Saved trained `.h5` deep learning models.
- `notebooks/`: The primary, fully-executable Jupyter Notebook containing the end-to-end framework.
- `src/`: Raw python scripts containing modeling code.
- `visualizations/`: Visual outputs from the framework (e.g. SHAP values, architecture plots, history plots).

## Methodology

### 1. Data Integration & Engineering
Using scientifically grounded bounds from the TRY Plant Trait Database, SoilGrids, PubChem, and WorldClim, an integrated dataset was generated. This dataset merges physiological properties, chemical descriptors, and climate features.
- Imputation strategies are applied to handle missing values using simple strategies (median/mode).
- Standard scaling and one-hot encoding are implemented to format variables for neural network consumption.

### 2. Baselines
Random Forest Regressors and XGBoost Classifiers are used to benchmark the system's baseline predictive power.

### 3. Multi-modal Neural Network Architecture
The framework employs a complex TensorFlow/Keras architecture explicitly designed to handle heterogeneous tabular data sources:
- **Four Input Branches**: Representing $X_1$ (Plant Traits), $X_2$ (Soil Features), $X_3$ (Contaminant Descriptors), and $X_4$ (Climate Data).
- **Fusion Layer**: These embeddings are concatenated into a shared representation layer that acts as the interaction space (e.g., climate-soil coupling).
- **Multi-task Output Heads**:
  - Regression Head: Predicts BCF, TF, and Remediation Efficiency.
  - Classification Head: Predicts binary affinity.

### 4. Explainability
SHAP values are calculated to derive feature importances, emphasizing the dominant role of soil pH, CEC, and specific taxonomy in remediation capability.

## Quick Start
1. Ensure you have the dependencies installed:
   ```bash
   pip install numpy pandas scikit-learn tensorflow xgboost shap matplotlib seaborn jupyter nbconvert
   ```
2. Navigate to `notebooks/` and explore the primary notebook:
   ```bash
   jupyter notebook Phytoremediation_Affinity_Model.ipynb
   ```
   Or run the standalone training script:
   ```bash
   cd src && python train.py
   ```
