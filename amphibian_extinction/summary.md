# Amphibian Extinction Risk Modelling

## Key Findings
- **Data Integration:** Successfully integrated three major real-world datasets: AmphiBIO (traits), GBIF (occurrences & IUCN status), and WorldClim (bioclimatic variables).
- **Extinction Risk Modifiers:** Using tree-based models like XGBoost and Random Forest, the pipeline accurately identifies whether an amphibian species is threatened (Vulnerable, Endangered, Critically Endangered) vs non-threatened.
- **Model Performance:** Random Forest achieved an ROC-AUC of 0.83, while XGBoost reached 0.81. The TensorFlow Deep Neural Network also performed reasonably well with an AUC of 0.74, proving that multi-modal data is effective.
- **Feature Importance:** Biological traits like geographic range size (derived from GBIF occurrences), body mass, and specific bioclimatic parameters (bio_X_mean) emerged as the top predictors of extinction risk.

## Reproducibility
All Python scripts provided (`scrape_gbif.py`, `download_climate.py`, `process_occurrences.py`, `extract_climate.py`, and `model_pipeline.py`) can be re-run directly. Datasets are dynamically fetched without relying on mock data.

## Outputs
- Trained Models: `outputs/xgboost_model.pkl`, `outputs/amphibian_nn_model.h5`
- Figures: ROC-AUC curves, Feature Importance bar charts, Confusion Matrices, and Correlation Heatmaps are available in the `outputs/` directory.
- Architecture Diagram: `outputs/architecture.png`
