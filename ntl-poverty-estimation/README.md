# NTL Poverty Estimation

An end-to-end geospatial machine learning research pipeline to estimate regional poverty levels using NASA Black Marble VIIRS Nighttime Light (NTL) satellite data.

## Features
- A trained Random Forest Regression model mapping NTL pixel statistics to DHS Wealth Index scores
- A high-resolution poverty heatmap at 30 arc-second (~1km) resolution
- Feature importance analysis and spatial cross-validation reports
- A structured research results CSV and publication-ready figures

## Pipeline
The pipeline runs through several phases:
1. Data Ingestion (NASA Earthdata, DHS)
2. NTL Raster Preprocessing (HDF to GeoTIFF, cloud masking)
3. Feature Engineering (Zonal stats)
4. Model Training & Evaluation (Random Forest, Spatial CV)
5. Poverty Heatmap Generation
6. Multimodal Data Fusion (NDVI via GEE)
7. Results Export & Reporting

## Running
Ensure required API keys (NASA Earthdata, GEE) are configured or run the pipeline to view the gracefully-handled empty outputs.

```bash
python main.py
```
