# Micro-Pricing Dynamics & Revenue Infrastructure

Implement a full supervised learning research pipeline to model micro-pricing dynamics across UK National Rail stations.

## Setup Instructions

1. Install dependencies:
   `pip install -r requirements.txt`

2. Download data:
   The Kaggle dataset can be downloaded using the Kaggle API:
   `export KAGGLE_USERNAME="your_username"`
   `export KAGGLE_KEY="your_key"`
   `kaggle datasets download -d helddata/uk-train-rides-maven-rail-challenge`
   Unzip the file and place `railway.csv` into `data/raw/`.

   Download `stations.csv`:
   `curl -L -O https://github.com/davwheat/uk-railway-stations/raw/main/stations.csv`
   Place into `data/raw/`.

   Download `orr_3184.csv` and `orr_3194a.csv` from the ORR Data Portal and place into `data/raw/`.

3. Run the complete pipeline:
   `./run_pipeline.sh`

This script will run feature engineering, model training, anomaly detection, equity analysis, and generate a final PDF policy impact report in the `outputs/report/` directory. All figures and tables will be saved in their respective directories under `outputs/`.
