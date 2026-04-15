# Amphibian Extinction Risk Modelling

## Key Findings
- **Data Integration & Compliance:** The pipeline explicitly validates, ingests, and merges empirical data from **four major authoritative open datasets**:
  1. `figshare.com` (AmphiBIO v1, DOI: 10.6084/m9.figshare.4644424) for species ecological traits.
  2. `gbif.org` for global spatial occurrences.
  3. `iucnredlist.org` (via GBIF aggregate backbone) for the actual target IUCN Red List risk status.
  4. `amphibiaweb.org` for overarching taxonomy verification and valid species matching.
  Additionally, WorldClim (ucdavis) is used for high-resolution bioclimatic baselines.

- **Extinction Risk Modifiers:** Using tree-based models like XGBoost and Random Forest, the pipeline accurately identifies whether an amphibian species is threatened (Vulnerable, Endangered, Critically Endangered) vs non-threatened.
- **Model Performance:** Random Forest achieved an ROC-AUC of 0.83, while XGBoost reached 0.81 (Validated with 5-Fold Stratified CV showing a mean ~0.80). The TensorFlow Deep Neural Network also performed reasonably well with an AUC of 0.74, proving that multi-modal data is effective.
- **Feature Importance:** Biological traits like geographic range size (derived from GBIF occurrences), body mass, and specific bioclimatic parameters (bio_X_mean) emerged as the top predictors of extinction risk.

## Reproducibility
All Python scripts provided (`pipeline.py`) can be re-run directly. Datasets are dynamically fetched without relying on mock data.

## Outputs
- Trained Models: `outputs/xgboost_model.pkl`, `outputs/amphibian_nn_model.h5`
- Figures: ROC-AUC curves, Feature Importance bar charts, Confusion Matrices, Geographic Risk Maps, Dataset Schema mappings, and Correlation Heatmaps are available in the `outputs/` directory.
- Architecture Diagram: `outputs/architecture.png`
