import sys
import os
import yaml
from data_loader import load_data
from features import engineer_features, select_features
from evaluate import evaluate_models

def main():
    if len(sys.argv) > 1:
        run_id = int(sys.argv[1])
    else:
        run_id = 1

    print(f"Starting Run {run_id}...")

    # 1. Load Data
    df = load_data()

    # 2. Engineer Features
    df_feat = engineer_features(df)

    # 3. Select Features
    X, y = select_features(df_feat)

    # 4. Evaluate Models (includes training, eval, and saving artifacts)
    evaluate_models(X, y, config_path='config.yaml', run_id=run_id)

    print(f"Run {run_id} completed successfully.")

if __name__ == "__main__":
    main()
