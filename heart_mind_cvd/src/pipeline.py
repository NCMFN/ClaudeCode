import argparse
import os

# Import pipeline steps
from preprocess import preprocess_data
from features import engineer_features
from train import train_models
from evaluate import evaluate_models

def main():
    parser = argparse.ArgumentParser(description="Run the Heart & Mind ML Pipeline.")
    parser.add_argument('--data_path', type=str, required=True, help="Directory containing raw data (adult22.csv)")
    parser.add_argument('--output_dir', type=str, required=True, help="Directory for models and figures")
    args = parser.parse_args()

    # Standardize paths
    raw_data_dir = args.data_path
    processed_data_dir = os.path.dirname(os.path.normpath(args.data_path))
    output_dir = args.output_dir
    log_dir = os.path.join(output_dir, 'logs') if 'logs' not in output_dir else output_dir
    if not os.path.exists(log_dir):
        log_dir = output_dir

    print("\n" + "="*50)
    print("STEP 1: Preprocessing Data")
    print("="*50)
    preprocess_data(raw_data_dir, processed_data_dir)

    print("\n" + "="*50)
    print("STEP 2: Feature Engineering & Splitting")
    print("="*50)
    engineer_features(processed_data_dir, processed_data_dir)

    print("\n" + "="*50)
    print("STEP 3: Training Models")
    print("="*50)
    train_models(processed_data_dir, output_dir, log_dir)

    print("\n" + "="*50)
    print("STEP 4: Evaluating Models & SHAP Analysis")
    print("="*50)
    metrics_df = evaluate_models(processed_data_dir, output_dir)

    print("\n" + "="*50)
    print("PIPELINE COMPLETE")
    print("Final Model Metrics Summary:")
    print(metrics_df.to_string(index=False))
    print("="*50)

if __name__ == "__main__":
    main()
