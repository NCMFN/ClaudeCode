import os
import sys
import pandas as pd
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.rule_based import predict_uci_bank
from models.ml_models import get_models

def test_data_files_exist():
    assert os.path.exists('data/uci_bank.csv')
    assert os.path.exists('data/kaggle_lead_scoring.csv')
    assert os.path.exists('data/kaggle_b2b_clean.csv')

def test_rule_based_predictions():
    df = pd.DataFrame({
        'age': [35, 20],
        'job': ['management', 'student'],
        'balance': [2000, 10],
        'campaign': [1, 5],
        'previous': [1, 0],
        'duration': [300, 50]
    })
    preds = predict_uci_bank(df, threshold=4)
    assert len(preds) == 2
    assert preds[0] == 1
    assert preds[1] == 0

def test_ml_models_instantiation():
    models = get_models()
    assert 'Logistic Regression' in models
    assert 'Random Forest' in models
    assert 'XGBoost' in models
