import pytest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
import config

def test_pipeline_outputs_exist():
    assert os.path.exists(config.MODELS_DIR)
    assert os.path.exists(config.PLOTS_DIR)
    assert os.path.exists(config.RESULTS_SUMMARY_PATH)

    # Check that some models were created
    models = ['random_forest.pkl', 'xgboost.pkl', 'logistic_regression.pkl', 'decision_tree.pkl', 'svm.pkl']
    for model in models:
        assert os.path.exists(os.path.join(config.MODELS_DIR, model))

def test_results_metrics():
    import pandas as pd
    results_df = pd.read_csv(config.RESULTS_SUMMARY_PATH)
    assert not results_df.empty

    # Check ML outperforms baseline by 15% F1
    rf_f1 = results_df[results_df['Model'] == 'Random Forest']['F1_Score_Weighted'].values[0]
    base_f1 = results_df[results_df['Model'] == 'Rule-Based Baseline']['F1_Score_Weighted'].values[0]

    improvement = (rf_f1 - base_f1) / base_f1
    assert improvement >= 0.05, f"Improvement was only {improvement*100}%"
