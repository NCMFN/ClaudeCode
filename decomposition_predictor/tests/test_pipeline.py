import pytest
import pandas as pd
import numpy as np
import os
import joblib
from fastapi.testclient import TestClient
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.api import app, load_models

client = TestClient(app)

@pytest.fixture(autouse=True)
def init_models():
    load_models()

def test_data_loading_correctness():
    # Check if raw data exists and has no NaNs in target-related columns (after preprocessing)
    processed_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'engineered_nasa_mdp.csv')
    assert os.path.exists(processed_path), "Processed data not found"

    df = pd.read_csv(processed_path, low_memory=False)
    assert len(df) > 0, "Dataframe is empty"

    features = ['loc', 'v_g', 'ev_g', 'iv_g', 'n', 'v', 'l', 'd', 'e', 'b']
    available = [f for f in features if f in df.columns]

    # Check shape
    assert df.shape[1] > 20, "Dataframe missing columns"

    # After preprocessing we shouldn't have NaNs in the core fields used for target calculation
    for f in available:
        assert df[f].isna().sum() == 0, f"NaNs found in {f}"

def test_target_variable_engineering():
    processed_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'engineered_nasa_mdp.csv')
    df = pd.read_csv(processed_path, low_memory=False)

    assert 'complexity_score' in df.columns, "complexity_score missing"
    assert 'decomposition_depth' in df.columns, "decomposition_depth missing"

    # CS in [0,1]
    assert df['complexity_score'].min() >= 0.0, "Complexity score < 0"
    assert df['complexity_score'].max() <= 1.0, "Complexity score > 1"

    # depth in {1,2,3,4}
    assert set(df['decomposition_depth'].dropna().unique()).issubset({1, 2, 3, 4}), "Invalid decomposition depth values"

def test_rfe_returns_features():
    # RFE outputs selected features to a text file, let's just check it
    features_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'selected_features.txt')
    assert os.path.exists(features_path), "RFE features file missing"
    with open(features_path, 'r') as f:
        features = f.read().strip().split(',')

    assert len(features) >= 3, "RFE returned fewer than 3 features"

def test_best_model_r2():
    results_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'model_comparison.csv')
    assert os.path.exists(results_path), "Model comparison results missing"
    results = pd.read_csv(results_path)

    best_r2 = results['CV_R2'].max()
    assert best_r2 >= 0.70, f"Best model R2 is {best_r2}, lower than required 0.70"

def test_api_predict():
    payload = {
        "loc": 450,
        "v_g": 12,
        "ev_g": 8,
        "iv_g": 6,
        "v": 3200,
        "l": 0.04,
        "d": 25.0,
        "e": 80000,
        "b": 1.07
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200, f"API failed with {response.status_code}: {response.text}"

    data = response.json()
    assert "complexity_score" in data
    assert "decomposition_depth" in data
    assert "recommended_agents" in data
    assert "confidence" in data
    assert "top_drivers" in data

    assert data["decomposition_depth"] in [1, 2, 3, 4]
