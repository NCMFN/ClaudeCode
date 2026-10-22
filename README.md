# Adaptive Wireless Sensor Network Regression Modeling

This project implements a continuous regression model that predicts **Signal Detection Accuracy (%)** in a Wireless Sensor Network (WSN) using node health metrics, environmental noise, and hardware parameters.

## Structure
- `run_pipeline.py`: The end-to-end Python pipeline spanning data processing, EDA, modeling, interpretation, and Adaptive Power Control (APC) simulation.
- `outputs/figures/`: 52 PNG figures analyzing the dataset, model performance, feature importance (SHAP), and APC scenarios.
- `outputs/models/`: Pickled trained machine learning models.
- `outputs/datasets/`: Processed datasets and CSVs of predictions.
- `outputs/paper_assets/`: Markdown summary reports and figure manifests for easy referencing in write-ups.

## Datasets
1. Primary WSN Dataset (`WSN_Dataset.csv`)
2. Node Health + RSSI + Energy (`WSN-DS.csv`)
3. WSN Node Localization (`WSN_Localization_Dataset.csv`)

## Execution
The pipeline is executed end-to-end by running:
```bash
python run_pipeline.py
```
