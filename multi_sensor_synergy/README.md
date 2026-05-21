# Multi-Sensor Synergy for Early Detection of Nutrient System Failures
in Automated Hydroponic Farming

## Project Overview
This project builds a machine learning pipeline in Python that predicts hardware/sensor failure events in automated hydroponic farming systems using multi-sensor data fusion, a novel Moisture Index (MOI) feature, and a comparative classification strategy.

## Installation

```bash
pip install -r requirements.txt
```

## Running the Pipeline

Ensure that the raw CSV and Excel datasets are downloaded from Kaggle into `data/raw/`.

To run the full pipeline, execute the modules in sequence:

1. Data Loading & Merging
```bash
python src/data_loader.py
```

2. Feature Engineering
```bash
python src/feature_engineering.py
```

3. Model Training (Trains 5 classifiers and applies SMOTE)
```bash
python src/model_training.py
```

4. Model Evaluation & A/B Testing
```bash
python src/evaluation.py
```

## Outputs
- Model weights: `outputs/models/`
- Plots: `outputs/plots/`
- Results summary: `outputs/results_summary.csv`
- Logs: `results/logs/`
