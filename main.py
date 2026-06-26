import argparse
import logging
import time

import eda
import preprocessing
import imbalance
import model
import evaluate
import explain

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def parse_args():
    parser = argparse.ArgumentParser(description="P2P Micro-Lending Default Risk Classification Pipeline")
    parser.add_argument('--data_path', type=str, default=None, help="Path to Loan_default.csv")
    parser.add_argument('--imbalance_strategy', type=str, choices=['smote', 'weight', 'undersample'],
                        default='smote', help="Strategy to handle class imbalance")
    parser.add_argument('--tune_hyperparams', type=lambda x: (str(x).lower() == 'true'),
                        default=False, help="Whether to tune LightGBM hyperparameters (True/False)")
    parser.add_argument('--exclude_anomalies', type=lambda x: (str(x).lower() == 'true'),
                        default=False, help="Whether to drop anomalies detected by Isolation Forest (True/False)")
    return parser.parse_args()

def main():
    args = parse_args()
    start_time = time.time()

    logging.info("=== Starting Loan Default Prediction Pipeline ===")

    # 1. Data Loading & EDA
    logging.info("\n--- Phase 1: Data Loading & EDA ---")
    df = eda.load_data(args.data_path)
    eda.perform_eda(df)

    mean_loan_amount = df['LoanAmount'].mean()

    # 2. Preprocessing & Feature Engineering
    logging.info("\n--- Phase 2 & 3: Feature Engineering & Preprocessing ---")
    X_train, X_test, y_train, y_test = preprocessing.preprocess_data(
        df, exclude_anomalies=args.exclude_anomalies
    )

    # 3. Class Imbalance
    logging.info("\n--- Phase 4: Class Imbalance Handling ---")
    X_train_res, y_train_res, lgb_kwargs = imbalance.handle_imbalance(
        X_train, y_train, strategy=args.imbalance_strategy
    )

    # 4. Model Training
    logging.info("\n--- Phase 5: Model Training ---")
    best_model = model.train_model(
        X_train_res, y_train_res,
        tune_hyperparams=args.tune_hyperparams,
        lgb_kwargs=lgb_kwargs
    )

    # 5. Evaluation
    logging.info("\n--- Phase 6: Evaluation ---")
    evaluate.evaluate_model(best_model, X_test, y_test, mean_loan_amount)

    # 6. Explainability
    logging.info("\n--- Phase 7: SHAP Explainability ---")
    explain.explain_model(best_model, X_test)

    elapsed = time.time() - start_time
    logging.info(f"\n=== Pipeline Completed in {elapsed:.2f} seconds ===")

if __name__ == "__main__":
    main()
