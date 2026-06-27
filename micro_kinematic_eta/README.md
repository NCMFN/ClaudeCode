# Micro-Kinematic ETA Forecasting

ETA forecasting via micro-kinematic LightGBM. This project models Vessel Estimated Time of Arrival using a computationally-efficient LightGBM supervised regression pipeline.

## Problem Statement
Port congestion and AIS data sparsity challenge traditional deep learning sequence models like LSTMs. They are computationally heavy for edge-deployment.

## Kinematic Hypothesis
Local kinematic behaviors (SOG, COG, bearing) become exponentially more predictive within a 50km "Micro-Kinematic Zone" (MKZ) of the destination.

## Dataset
- [Marine Cadastre AIS (US Waters)](https://marinecadastre.gov/ais/)
- [Kaggle: Ship Tracking AIS Data](https://www.kaggle.com/datasets/aysekoytak/ship-tracking-ais-data)

## Pipeline Diagram
```text
AIS CSV → Validate → DBSCAN Clustering → Feature Engineering
    → Train/Test Split → [LR | RF | LightGBM+Optuna]
    → Evaluate (RMSE/MAE/R²) → SHAP Explainability → Inference API
```

## Installation & Usage
```bash
pip install -r requirements.txt
python scripts/download_data.py
python scripts/train.py --data data/raw/ais_data.csv --model all --optuna_trials 10
python scripts/inference.py --lat 51.9 --lon 4.1 --sog 12.5 --cog 270 --heading 268 --vessel_type cargo --draft 8.5 --datetime "2024-03-15 14:30:00"
```

## Results
See `outputs/results/final_metrics_comparison.csv`

## Key Finding
Accuracy improves exponentially within the micro-kinematic zone (<50km) due to velocity stability and heading alignment.

## Environmental Impact
Optimizing ETA supports just-in-time arrival, reducing anchorage idle time and saving SOx/NOx emissions.
