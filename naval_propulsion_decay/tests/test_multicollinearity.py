import pytest
import os
import sys
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.multicollinearity import MulticollinearityAnalyzer

def test_multicollinearity():
    np.random.seed(42)
    # create synthetic data with high correlation between first two cols
    x1 = np.random.rand(100)
    x2 = x1 + np.random.rand(100) * 0.01

    data = np.random.rand(100, 16)
    data[:, 0] = x1
    data[:, 1] = x2
    X_train = pd.DataFrame(data, columns=config.FEATURE_NAMES)
    X_train['Lp'] = x1
    X_train['v'] = x2

    analyzer = MulticollinearityAnalyzer()
    corr = analyzer.compute_correlation_matrix(X_train)

    assert corr.shape == (16, 16)
    assert corr.loc['Lp', 'v'] > 0.90

    vif_df = analyzer.compute_vif(X_train)
    assert len(vif_df) == 16
    assert (vif_df['VIF'] > 0).all()
