import json
import os

def create_notebook(path, code):
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": code
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    with open(path, 'w') as f:
        json.dump(notebook, f, indent=2)

create_notebook("uk-rail-pricing/notebooks/01_eda.ipynb", ["# Run EDA\n", "import sys\n", "sys.path.append('../src')\n", "import eda\n", "eda.run_eda()"])
create_notebook("uk-rail-pricing/notebooks/02_feature_engineering.ipynb", ["# Run Feature Engineering\n", "import sys\n", "sys.path.append('../src')\n", "import feature_engineering\n", "import data_loader\n", "import pandas as pd\n", "df = data_loader.load_and_clean_data('../data/raw/railway.csv')\n", "stations_df = pd.read_csv('../data/geospatial/stations.csv')\n", "feature_engineering.generate_figs(df.copy())\n", "feature_engineering.engineer_features(df, stations_df)"])
create_notebook("uk-rail-pricing/notebooks/03_model_training.ipynb", ["# Run Model Training\n", "import sys\n", "sys.path.append('../src')\n", "import model\n", "model.train_and_evaluate()"])
create_notebook("uk-rail-pricing/notebooks/04_validation_error_analysis.ipynb", ["# Run Anomaly Detection and Equity Analysis\n", "import sys\n", "sys.path.append('../src')\n", "import anomaly_detection\n", "import equity_analysis\n", "anomaly_detection.run_anomaly_detection()\n", "equity_analysis.run_equity_analysis()"])
create_notebook("uk-rail-pricing/notebooks/05_policy_impact_report.ipynb", ["# Generate Policy Impact Report\n", "import sys\n", "sys.path.append('../src')\n", "import report_generator\n", "report_generator.build_report()"])
