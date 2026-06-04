# Early-Stage Anomaly Detection and Downtime Risk Scoring in Cloud-Integrated Industrial Sensors

This project implements an end-to-end Machine Learning pipeline to predict maintenance requirements and calculate proactive downtime risk scores for cloud-integrated industrial sensors.

## Features
- **Data Ingestion & EDA**: Handling missing values, parsing timestamps, and generating visual reports.
- **Feature Engineering**: Computing rolling window statistics across multimodal sensors (Vibration, Pressure, Energy, Humidity, Temperature). Includes correlation between vibration and energy spikes.
- **Micro-Anomaly Detection**: Using Isolation Forest and LSTM Autoencoders to flag anomalies before major failures occur.
- **Proactive Risk Scoring**: A weighted scoring formula that fuses anomaly rates, pressure variance, and energy spikes to output a 0-100 risk score, transmitting only critical metrics to simulate Cloud-Edge systems.
- **Predictive Maintenance**: Using Random Forest, XGBoost, and LSTM Sequence models evaluated with GroupKFold.
- **Visuals**: Auto-generates system architecture diagram using `networkx` and `matplotlib`.

## Deliverables
- `pipeline.py`: Main execution script that orchestrates the entire workflow.
- `pipeline_utils.py`, `anomaly_scoring.py`, `classification_sim.py`: Modular files.
- `eda_report.ipynb`: Exploratory data analysis notebook.
- `models/`: Pickled / Keras saved models.
- `outputs/`: CSV scores and the final classification report.
- `*.png`: All generated plots (ROC curves, confusion matrices, timelines, system architecture) are saved directly to the repository root directory.

## How to Run

1. **Install requirements:**
   ```bash
   pip install kagglehub xgboost tensorflow scikit-learn matplotlib seaborn jupyter nbformat nbconvert imbalanced-learn pytest networkx
   ```
2. **Download data:**
   Ensure the data is in the `data/` directory named `smart_manufacturing_data.csv`. You can use `download_data.py` to fetch it.
   ```bash
   python download_data.py
   ```
3. **Run the pipeline:**
   ```bash
   python pipeline.py
   ```
4. **View results:**
   Image outputs (ROC curves, timelines, matrices) will be located in the root folder. The `classification_report.txt` and raw `risk_scores.csv` will be located in the `outputs/` folder.
   Logs are recorded in `results/logs/pipeline.log`.

## Tests
Run the test suite using pytest. The tests are located in `tests/test_pipeline.py`.
```bash
pytest tests/test_pipeline.py -v
```
