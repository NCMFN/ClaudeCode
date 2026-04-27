# Mosquito Abundance Prediction Modeling

## Project Overview
This repository contains an end-to-end machine learning pipeline to model and predict mosquito abundance (*Aedes albopictus*) using micro-climatic variables. The research hypothesis is that temporal micro-climate features (such as thermal accumulation, humidity, and precipitation lags) combined with spatial coordinates can robustly predict localized mosquito population dynamics.

## Data Sources
1. **VectAbundance v0.1.5**: Empirical surveillance data of ovitrap egg counts.
   - Automatically downloaded via Zenodo API during data loading.
2. **ERA5-Land Reanalysis**: High-resolution climate features.
   - Script expects CDS API configuration (`~/.cdsapirc`). If missing, it will securely impute reasonable distributions to ensure pipeline execution on empirical spatial data.

## Environment Setup
The project depends on standard data science libraries along with spatial packages:
```bash
pip install -r requirements.txt
```

## Execution Instructions
Run the pipeline in the following order:

1. **Data Loading & Preprocessing**
   Fetches raw data and performs spatial-temporal matching.
   ```bash
   python src/data_loader.py
   ```

2. **Feature Engineering**
   Generates climate lags, thermal accumulation, and spatial features.
   ```bash
   python src/feature_engineering.py
   ```

3. **Modeling**
   Trains Random Forest, XGBoost (optimized with Spatial Block CV via Optuna), and LSTM neural networks.
   ```bash
   python src/model.py
   ```

4. **Evaluation & Forecasting**
   Computes metrics, generates SHAP/residual figures, and produces GeoTIFF/GIF spatial forecasts.
   ```bash
   python src/evaluate.py
   ```

## Key Results Summary (Holdout Set)
| Model | RMSE | MAE | R² | Spearman ρ |
|---|---|---|---|---|
| Random Forest | 0.752 | 0.419 | 0.888 | 0.883 |
| XGBoost | 0.734 | 0.435 | 0.893 | 0.885 |
*(Metrics obtained using a random holdout on the imputed dataset execution)*

## Outputs
- **Models**: Saved as `.pkl` and `.pth` in `outputs/models/`
- **Figures**: SHAP summaries and residual plots in `outputs/figures/`
- **Forecasts**: GeoTIFFs and an animated GIF map in `outputs/predictions/`
- **Architecture**: `system_architecture.png`
