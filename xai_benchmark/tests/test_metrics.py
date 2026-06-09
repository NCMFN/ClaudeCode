import numpy as np
import pytest
from metrics.metrics import (
    calculate_simplicity,
    calculate_relevance,
    calculate_q_score
)

def test_calculate_simplicity_lime():
    # 2 samples, 3 features. LIME logic checks > 1e-6.
    # Sample 1 uses 1 feature, Sample 2 uses 2 features.
    vals = np.array([
        [0.0, 0.5, 0.0],
        [0.1, -0.2, 0.0]
    ])

    simp = calculate_simplicity(vals, method='lime')
    # Sample 1 count: 1 -> simp: 1.0
    # Sample 2 count: 2 -> simp: 0.5
    # Mean -> 0.75
    assert np.isclose(simp, 0.75)

def test_calculate_simplicity_shap():
    # SHAP logic checks > threshold (mean abs val)
    vals = np.array([
        [1.0, 0.1, 0.1],
        [2.0, 2.0, 0.0]
    ])
    # Sample 1 threshold = 0.4. Count > 0.4 is 1 (the 1.0). Simp = 1.0
    # Sample 2 threshold = 1.33. Count > 1.33 is 2. Simp = 0.5
    simp = calculate_simplicity(vals, method='shap')
    assert np.isclose(simp, 0.75)

def test_calculate_relevance():
    vals = np.array([
        [0.9, 0.8, 0.1, 0.0],
        [0.1, 0.2, 0.9, 0.8]
    ])
    feature_names = ['mean radius', 'mean area', 'noise1', 'noise2']

    # K=2 top features
    # Sample 1 top features: mean radius, mean area. Both relevant. Relevance = 2/2 = 1.0
    # Sample 2 top features: noise1, noise2. Neither relevant. Relevance = 0.0
    mean_rel, kappa = calculate_relevance(vals, feature_names, dataset_name='Breast_Cancer', k=2)
    assert np.isclose(mean_rel, 0.5)
    # Kappa should be computable but depends on the random flip simulation. Just check it's returned.
    assert isinstance(kappa, float)

def test_calculate_q_score():
    q = calculate_q_score(0.8, 0.6, 1.0, 0.4)
    expected = 0.25 * (0.8 + 0.6 + 1.0 + 0.4)
    assert np.isclose(q, expected)
