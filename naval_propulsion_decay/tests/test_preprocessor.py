import pytest
import os
import sys
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.preprocessor import NavalPreprocessor

def test_preprocessor():
    np.random.seed(42)
    # Generate 5 rows of random data for fit
    X_train = pd.DataFrame(np.random.rand(5, 16) * 100, columns=config.FEATURE_NAMES)
    # 3 rows for transform
    X_val = pd.DataFrame(np.random.rand(3, 16) * 100, columns=config.FEATURE_NAMES)
    X_test = pd.DataFrame(np.random.rand(3, 16) * 100, columns=config.FEATURE_NAMES)

    preprocessor = NavalPreprocessor()
    X_train_std, X_val_std, X_test_std, X_train_minmax, X_val_minmax, X_test_minmax = preprocessor.fit_transform_scalers(X_train, X_val, X_test)

    # Assert StandardScaler output properties on train set
    np.testing.assert_allclose(X_train_std.mean(axis=0), 0, atol=1e-7)
    np.testing.assert_allclose(X_train_std.std(axis=0, ddof=0), 1, atol=1e-7)

    # Assert MinMaxScaler output properties on train set
    assert (X_train_minmax.values >= -0.01).all() and (X_train_minmax.values <= 1.01).all()

    X_train_pca, X_val_pca, X_test_pca = preprocessor.fit_transform_pca(X_train_std, X_val_std, X_test_std)
    assert X_train_pca.shape[1] < 16, "PCA did not reduce columns"
    assert X_train_pca.shape[0] == 5
    assert X_val_pca.shape[0] == 3
