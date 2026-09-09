#!/bin/bash
set -e
echo "Starting E2E pipeline..."

echo "1. Feature Engineering..."
python3 src/feature_engineering.py

echo "2. EDA..."
python3 notebooks/01_eda.py

echo "3. Model Training..."
python3 src/model.py

echo "4. Anomaly Detection..."
python3 src/anomaly_detection.py

echo "5. Equity Analysis..."
python3 src/equity_analysis.py

echo "6. Report Generation..."
python3 notebooks/05_policy_impact_report.py

echo "Pipeline complete!"
