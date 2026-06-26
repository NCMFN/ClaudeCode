# NTL Poverty Estimation

## Overview
This repository implements a full end-to-end geospatial machine learning research pipeline to estimate regional poverty levels using NASA Black Marble VIIRS Nighttime Light (NTL) satellite data. The primary objective is to train a Random Forest Regression model mapping NTL pixel statistics to DHS Wealth Index scores and generate high-resolution poverty heatmaps.

## Pipeline Architecture
- Phase 1: Environment Setup & Data Ingestion (DHS surveys, NASA NTL HDF-EOS5 files).
- Phase 2: NTL Raster Preprocessing (HDF to GeoTIFF conversion, cloud/blooming artefact masking, annual median composite).
- Phase 3: Feature Engineering (DHS cluster buffering, zonal statistics extraction).
- Phase 4: Model Training & Evaluation (Baseline RF Regression, Spatial CV, Feature Importance).
- Phase 5: Poverty Heatmap Generation (Applying model to NTL grid, generating spatial heatmaps).
- Phase 6: Multimodal Data Fusion (Incorporating MODIS NDVI data).
- Phase 7: Results Export & Reporting.

## Usage
Run the pipeline entirely via the main orchestrator script:
```bash
python main.py
```
Outputs (feature matrices, poverty heatmaps, result CSVs, and figures) are generated under the `data/processed/` and `outputs/` directories. Log artifacts are stored in `results/logs/`.
