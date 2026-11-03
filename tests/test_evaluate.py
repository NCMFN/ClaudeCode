import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_bootstrap():
    import numpy as np
    from src.evaluate import block_bootstrap
    y_true = np.array([1, 0, 1, 0])
    y_pred = np.array([0.9, 0.1, 0.8, 0.2])
    groups = np.array([1, 1, 2, 2])
    ci = block_bootstrap(y_true, y_pred, groups, n_boot=10, seed=42)
    assert ci != (np.nan, np.nan)
