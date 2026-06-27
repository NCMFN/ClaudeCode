import argparse
import logging
import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data_loader import AISDataLoader
from src.destination_clusterer import PortDestinationClusterer
from src.feature_engineer import KinematicFeatureEngineer
from src.models.baseline_linear import LinearBaselineModel
from src.models.baseline_rf import RFBaselineModel
from src.models.lightgbm_model import LightGBMEtaModel
from src.evaluator import ETAEvaluator
from src.explainer import LightGBMExplainer


from config import RANDOM_SEED, TEST_SPLIT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('train')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, required=True)
    parser.add_argument('--model', type=str, choices=['all', 'lr', 'rf', 'lgbm'], default='all')
    parser.add_argument('--optuna_trials', type=int, default=100)
    args = parser.parse_args()

    start_time = time.time()
    logger.info(f"Starting training pipeline. Data: {args.data}, Model: {args.model}")

    # Ensure dirs
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('outputs/models', exist_ok=True)

    # 1. Load and validate
    loader = AISDataLoader()
    df = loader.load(args.data)
    df, report = loader.validate(df)

    # Sample down if too large for timely execution
    if len(df) > 50000:
        logger.info("Sampling dataset down to 50k for performance.")
        df = df.sample(50000, random_state=RANDOM_SEED)

    # 2. DBSCAN clustering
    clusterer = PortDestinationClusterer()
    clusterer.fit(df)
    df = clusterer.assign_destination(df)

    # 3. Feature engineering
    engineer = KinematicFeatureEngineer()
    df = engineer.transform(df)

    # Save processed
    df.to_parquet('data/processed/ais_features.parquet')

    # Run EDA

    # Run EDA notebook
    logger.info("Running EDA notebook")
    import subprocess
    try:
        subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", "notebooks/01_EDA.ipynb"], check=True)
    except Exception as e:
        logger.error(f"Failed to run EDA notebook: {e}")


    # 4. Train/test split
    features = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c not in ['MMSI', 'BaseDateTime', 'VesselName', 'ETA_hours', 'arrived', 'arrival_timestamp', 'VesselType', 'COG', 'Heading', 'bearing_to_dest']]

    # Stratified split by VesselType if possible
    vt_counts = df['VesselType'].value_counts()
    valid_vt = vt_counts[vt_counts > 1].index
    mask = df['VesselType'].isin(valid_vt)
    df_split = df[mask]

    X = df_split[features]
    y = df_split['ETA_hours']

    X_train, X_test, y_train, y_test, _, df_test_meta = train_test_split(
        X, y, df_split, test_size=TEST_SPLIT, random_state=RANDOM_SEED
    )

    # Further split train for validation
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=RANDOM_SEED
    )

    models_dict = {}

    # 5. Baseline LR
    if args.model in ['all', 'lr']:
        lr = LinearBaselineModel()
        lr.fit(X_train.fillna(0), y_train)
        _, preds_test = lr.evaluate(X_test.fillna(0), y_test)
        lr.save('outputs/models/lr_baseline.pkl')
        pd.DataFrame({'pred': preds_test}).to_csv('outputs/results/lr_predictions.csv', index=False)
        models_dict['Linear Regression'] = preds_test

    # Baseline RF
    if args.model in ['all', 'rf']:
        rf = RFBaselineModel()
        rf.fit(X_train.fillna(0), y_train)
        _, preds_test = rf.evaluate(X_test.fillna(0), y_test)
        rf.save('outputs/models/rf_baseline.pkl')
        rf.save_feature_importance(features, 'outputs/results/rf_feature_importance.csv')
        models_dict['Random Forest'] = preds_test

    # 6 & 7. LightGBM + Optuna
    if args.model in ['all', 'lgbm']:
        lgbm = LightGBMEtaModel()
        best_params = lgbm.tune(X_train, y_train, n_trials=args.optuna_trials)
        lgbm.fit(X_tr, y_tr, X_val, y_val, params=best_params)
        preds_test = lgbm.predict(X_test)
        lgbm.save('outputs/models/lgbm_final.txt', 'outputs/models/lgbm_final.pkl')
        models_dict['LightGBM'] = preds_test

        # 9. SHAP Explainability
        explainer = LightGBMExplainer()
        explainer.explain_global(lgbm.model, X_test)

        # 13. MKZ Analysis

    # Run MKZ notebook
    logger.info("Running MKZ notebook")
    try:
        subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", "notebooks/06_Micro_Kinematic_Zone_Analysis.ipynb"], check=True)
    except Exception as e:
        logger.error(f"Failed to run MKZ notebook: {e}")


    # 8. Evaluate all
    if models_dict:
        evaluator = ETAEvaluator()
        evaluator.evaluate(df_test_meta, models_dict)

        # 10. Print final results table
        metrics = pd.read_csv('outputs/results/final_metrics_comparison.csv')
        logger.info("\nFinal Results (All Strata):")
        print(metrics[metrics['Strata'] == 'All'][['Model', 'RMSE_hrs', 'MAE_hrs', 'R2', 'Within_1hr_pct']].to_markdown(index=False))

    runtime = time.time() - start_time
    logger.info(f"Pipeline complete in {runtime:.1f} seconds")

if __name__ == "__main__":
    main()
